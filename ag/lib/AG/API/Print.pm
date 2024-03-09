package AG::API::Print;

use strict;
use warnings;
use feature ':5.10';

#use AG::API::JSONParser;
use base qw/AG::API::JSONParser/;
use File::Basename;
#use common;
#use common_db;
use AG::ComDB::Shorturl;
use AG::API::Log;

sub parse {
	my $parser = shift;
#	my $json = shift;
	my $func = shift;
	my $json = $parser->{json};

	my $ag_log = new AG::API::Log($json);

	my $img;
	my $ContentType = qq|image/gif|;
	my $Status;
	my $Code = '503';
	my $content;
#	my @extlist = qw|.cgi|;
	my($name,$dir,$ext) = &File::Basename::fileparse($0,qr/\..*$/);

#	open OUT,">./tmp_image/$name.txt";
	my $OUT = &cgi_lib::common::getLogFH(undef,undef,&AG::API::JSONParser::get_log_file_basename(),&AG::API::JSONParser::get_log_dir_basename($name));

#	my $parser = new AgJSONParser($json);

	if(defined $parser){
		print $OUT __LINE__,":[$json]\n";
		print $OUT __LINE__,":[$parser->{json}]\n";
	#	print $OUT __LINE__,":[",$parser->getMethodContent($name),"]\n";

		$img = $parser->getMethodPicture($name);
		$Status = $parser->getContentStatus();
		$Code = $parser->getContentCode();
		$ContentType = $parser->getContentType();
		$content = $parser->getContent() unless($Code eq '200');

	}else{
		if($json =~ /^shorten=(.+)$/){
			my $shorten = $1;
=pod
			my $dbh = &common_db::get_dbh();
			my $sth = $dbh->prepare(qq|select sp_original from shorten_param where sp_shorten=?|);
			$sth->execute($shorten);
			my $column_number = 0;
			my $sp_original;
			$sth->bind_col(++$column_number, \$sp_original, undef);
			$sth->fetch;
			$sth->finish;
			undef $sth;
=cut
			my $shorturl = new AG::ComDB::Shorturl;
			my $sp_original = $shorturl->get_long_url($shorten);
			if(defined $sp_original){
				my $index_key = "tp_ap=";
				$sp_original = &cgi_lib::common::url_decode(substr($sp_original,index($sp_original,$index_key)+length($index_key))) if(index($sp_original,$index_key)>=0);
				my $parser = new AG::API::JSONParser($sp_original);
				if(defined $parser){
					$img = $parser->getMethodPicture($name);
					$Status = $parser->getContentStatus();
					$Code = $parser->getContentCode();
					$ContentType = $parser->getContentType();
					$content = $parser->getContent() unless($Code eq '200');
				}

			}
			undef $sp_original;
			undef $shorturl;
		}
	}

#	if(defined $parser){
#		$img = $parser->getMethodPicture($name);
#		$Status = $parser->getContentStatus();
#		$ContentType = $parser->getContentType();
#	}

	print "Status:$Status\n" if(defined $Status);
	if($Code eq '200'){
		print "Content-Type:$ContentType\n\n";
		binmode(STDOUT);
		print $img;
	}else{
		&cgi_lib::common::printContent($content,$ContentType);
	}

	close($OUT);
	$ag_log->print(defined $parser ? $parser->{'jsonObj'} : undef,undef,defined $parser ? $parser->getBalancerInformation() : undef);
}

1;
