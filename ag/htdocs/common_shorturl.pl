use strict;

=pod
#
#bit.lyは2048byteの制限がある為、使用しない
#
use LWP::UserAgent;
use HTTP::Request::Common;

#http://code.google.com/p/bitly-api/wiki/ApiDocumentation
#bit.ly[Username][tyamamot]
#bit.ly[API Key][R_9a06d0344391c889c290d47364949a55]
#http://api.bit.ly/v3/shorten?login=bitlyapidemo&apiKey=R_0da49e0a9118ff35f52f629d2d71bf07&longUrl=http%3A%2F%2Fbetaworks.com%2F&format=json
#http://api.bit.ly/v3/expand?shortUrl=http%3A%2F%2Fbit.ly%2F31IqMl&login=bitlyapidemo&apiKey=R_0da49e0a9118ff35f52f629d2d71bf07&format=json

sub isShortUrl {
	my $url = shift;
	return undef unless(defined $url);
	return ($url =~ /^http:\/\/bit\.ly\//)?1:0;
}
sub convert_url {
	my $url = shift;
	return undef unless(defined $url);

	my $login = qq|tyamamot|;
	my $apiKey = qq|R_9a06d0344391c889c290d47364949a55|;
	my $format = qq|json|;

	my $baseurl = qq|http://api.bit.ly/v3|;
	my $expand  = qq|$baseurl/expand|;
	my $shorten = qq|$baseurl/shorten|;

	if($url =~ /^http:\/\//){
		my %post = (
			'login'=>$login,
			'apiKey'=>$apiKey,
			'format'=>$format
		);
		my $post_url;
		if(&isShortUrl($url)){
			$post_url = $expand;
			$post{shortUrl} = $url;
		}else{
			$post_url = $shorten;
			$post{longUrl} = $url;
		}
		my $ua = LWP::UserAgent->new;
		my $res = $ua->request(POST($post_url, [%post]));
		return $res->content;
	}else{
		return qq|{}|;
	}
}
=cut


=pod
CREATE TABLE shorten_param (
  sp_shorten  text    NOT NULL,
  sp_original text    NOT NULL,
  su_entry    timestamp without time zone NOT NULL,
  PRIMARY KEY (sp_shorten)
);
CREATE INDEX shorten_param_sp_original_idx ON shorten_param USING btree (sp_original);
=cut

use Digest::MD5 qw(md5_hex);
use JSON::XS;
use Carp;

require "common.pl";
require "common_db.pl";

sub isShortUrl {
	my $url = shift;
	return undef unless(defined $url);
	return ($url =~ /[&?]shorten=/) ? 1 : 0;
}

sub shorten_url {
	my $url= shift;
	my @chars = (
		'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
		'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
		'0','1','2','3','4','5','6','7','8','9'
	);
	my @output;
	my $hex = md5_hex($url);
	my $len = length($hex);
	for(my $i=0;$i<$len/8;$i++){
		my $int = hex("0x".substr($hex,$i*8,8));
		my $out;
		for(my $j=0;$j<6;$j++){
			my $val = 0x0000003D & $int;
			$out .= $chars[$val];
			$int = $int >> 5;
		}
		push @output, $out;
	}
	return join("",@output);
}
sub convert_url {
	my $url = shift;
	return undef unless(defined $url);
	my $results = {
		status_code => 200,
		data => {
			url => $url
		}
	};
	my $idx = index($url,'?');
	if($idx>=0){
		my $base_url = substr($url,0,$idx);
		if(defined $base_url && $base_url =~ /\/ag_annotation\.cgi$/){
			$base_url =~ s/\/ag_annotation\.cgi$/\//g;
		}
		my $param = substr($url,$idx+1);
		my $dbh = &get_dbh();
		if($param =~ /^shorten=/){
			$param =~ s/^shorten=//;
			my $sth = $dbh->prepare(qq|select sp_original from shorten_param where sp_shorten=?|) or croak $dbh->errstr;
			$sth->execute($param) or croak $dbh->errstr;
			my $column_number = 0;
			my $sp_original;
			$sth->bind_col(++$column_number, \$sp_original, undef);
			$sth->fetch;
			$sth->finish;
			undef $sth;
			if(defined $sp_original){
				delete $results->{data}->{url};
				$results->{data}->{expand}->{long_url} = $base_url.'?'.$sp_original;
			}
		}else{
			my $sth = $dbh->prepare(qq|select sp_shorten from shorten_param where sp_original=?|) or croak $dbh->errstr;
			$sth->execute($param) or croak $dbh->errstr;
			my $column_number = 0;
			my $sp_shorten;
			$sth->bind_col(++$column_number, \$sp_shorten, undef);
			$sth->fetch;
			$sth->finish;
			undef $sth;
			unless(defined $sp_shorten){
				$sp_shorten = &shorten_url($param);
				#shortURLへ変換後、同じものがあるか確認
				my $sth = $dbh->prepare(qq|select sp_original from shorten_param where sp_shorten=?|) or croak $dbh->errstr;
				$sth->execute($sp_shorten) or croak $dbh->errstr;
				my $rows = $sth->rows();
				$sth->finish;
				undef $sth;
				if($rows<1){
					$dbh->{AutoCommit} = 0;
					$dbh->{RaiseError} = 1;
					eval{
						my $param_num = 0;
						my $sth = $dbh->prepare(qq|insert into shorten_param (sp_shorten,sp_original,su_entry) values (?,?,'now()')|) or croak $dbh->errstr;
						$sth->bind_param(++$param_num,$sp_shorten);
						$sth->bind_param(++$param_num,$param);
						$sth->execute() or croak $dbh->errstr;
						$sth->finish;
						undef $sth;
						$dbh->commit();
					};
					if($@){
						my $msg = $@;
						$dbh->rollback();
						$msg =~ s/\s*$//g;
						$msg =~ s/^\s*//g;
						$results->{'success'} = JSON::XS::false;
						$results->{'msg'} = $msg;
					}
					$dbh->{AutoCommit} = 1;
					$dbh->{RaiseError} = 0;
				}
			}
			$results->{data}->{url} = $base_url.'?shorten='.$sp_shorten;
		}
	}
	return &JSON::XS::encode_json($results);
}

1;
