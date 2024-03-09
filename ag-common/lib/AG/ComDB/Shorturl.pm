package AG::ComDB::Shorturl;

use base qw/AG::ComDB/;

use strict;
use Digest::MD5 qw(md5_hex);
use JSON::XS;
use Carp;

=pod
CREATE TABLE shorten_param (
  sp_shorten  text    NOT NULL,
  sp_original text    NOT NULL,
  su_entry    timestamp without time zone NOT NULL,
  PRIMARY KEY (sp_shorten)
);
CREATE INDEX shorten_param_sp_original_idx ON shorten_param USING btree (sp_original);
=cut

sub new {
	my $class = shift;
	my %args = @_;
	my $self = new AG::ComDB(%args);
	my $dbh = $self->get_dbh();
	$self->{__sth_sp_original} = $dbh->prepare(qq|select sp_original from shorten_param where sp_shorten=?|) or &Carp::croak(DBI->errstr());
	$self->{__sth_sp_shorten} = $dbh->prepare(qq|select sp_shorten from shorten_param where md5(sp_original)=md5(?) and sp_original=?|) or &Carp::croak(DBI->errstr());
	return bless $self, $class;
}

sub isShortUrl {
	my $self = shift;
	my $url = shift;
	return undef unless(defined $url);
	return ($url =~ /[&?]shorten=/) ? 1 : 0;
}

sub shorten_url {
	my $self = shift;
	my $url= shift;
	my @chars = (
		'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
		'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
		'0','1','2','3','4','5','6','7','8','9'
	);
	my @output;
	my $hex = &Digest::MD5::md5_hex($url);
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

sub get_long_url {
	my $self = shift;
	my $short_url = shift;
	return undef unless(defined $short_url);

	$self->{__sth_sp_original}->execute($short_url) or &Carp::croak(DBI->errstr());
	my $column_number = 0;
	my $sp_original;
	$self->{__sth_sp_original}->bind_col(++$column_number, \$sp_original, undef);
	$self->{__sth_sp_original}->fetch;
	$self->{__sth_sp_original}->finish;

	return $sp_original;
}

sub convert_url {
	my $self = shift;
	my $url = shift;
	my %args = @_;
	return undef unless(defined $url);
	$args{'encode'} = 1 unless(defined $args{'encode'});
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
		my $dbh = $self->get_dbh();
		if($param =~ /^shorten=/){
			$param =~ s/^shorten=//;
			my $sp_original = $self->get_long_url($param);
			if(defined $sp_original){
				delete $results->{data}->{url};
				$results->{data}->{expand}->{long_url} = $base_url.'?'.$sp_original;
			}
		}else{
			$dbh->{AutoCommit} = 0;
			$dbh->{RaiseError} = 1;
			eval{
				$self->{__sth_sp_shorten}->execute($param,$param) or &Carp::croak(DBI->errstr());
				my $column_number = 0;
				my $sp_shorten;
				$self->{__sth_sp_shorten}->bind_col(++$column_number, \$sp_shorten, undef);
				$self->{__sth_sp_shorten}->fetch;
				$self->{__sth_sp_shorten}->finish;
				unless(defined $sp_shorten){
					$sp_shorten = $self->shorten_url($param);
					#shortURLへ変換後、同じものがあるか確認
					my $sp_original = $self->get_long_url($sp_shorten);
					my $count=0;
					while(defined $sp_original){#$sp_shortenが重複する事が考えられる為、shorten_urlが登録済みか確認
						$sp_shorten = $self->shorten_url($param.(++$count));
						$sp_original = $self->get_long_url($sp_shorten);
					}
					unless(defined $sp_original){
						my $param_num = 0;
						my $sth = $dbh->prepare(qq|insert into shorten_param (sp_shorten,sp_original,su_entry) values (?,?,'now()')|) or &Carp::croak(DBI->errstr());
						$sth->bind_param(++$param_num,$sp_shorten);
						$sth->bind_param(++$param_num,$param);
						$sth->execute() or &Carp::croak(DBI->errstr());
						$sth->finish;
						undef $sth;
						$dbh->commit();
					}
				}
				$results->{data}->{url} = $base_url.'?shorten='.$sp_shorten if(defined $sp_shorten);
			};
			if($@){
				my $msg = $@;
				$dbh->rollback();
				&utf8::decode($msg) unless(&utf8::is_utf8($msg));
				$msg =~ s/\s*$//g;
				$msg =~ s/^\s*//g;
				$results->{'success'} = JSON::XS::false;
				$results->{'msg'} = $msg;
			}
			$dbh->{AutoCommit} = 1;
			$dbh->{RaiseError} = 0;

		}
	}
	return $args{'encode'} ? &JSON::XS::encode_json($results) : $results;
}

1;
