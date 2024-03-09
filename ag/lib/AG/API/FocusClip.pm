package AG::API::FocusClip;

use strict;
use warnings;
use feature ':5.10';

#use AG::API::JSONParser;
use base qw/AG::API::JSONParser/;
use File::Basename;
use AG::API::Log;
use cgi_lib::common;

sub parse {
	my $parser = shift;
#	my $json = shift;
	my $func = shift;
	my $json = $parser->{json};

	my $ag_log = new AG::API::Log($json);

	my $content;
	my $ContentType = qq|application/json|;
	my $Status;
	my $Code = '503';
#	my @extlist = qw|.cgi|;
	my($name,$dir,$ext) = &File::Basename::fileparse($0,qr/\..*$/);

#	open OUT,">./tmp_image/$name.txt";
	my $OUT = &cgi_lib::common::getLogFH(undef,undef,&AG::API::JSONParser::get_log_file_basename(),&AG::API::JSONParser::get_log_dir_basename($name));

#	my $parser = new AgJSONParser($json);
	if(defined $parser){
		print $OUT __LINE__,":[$parser->{json}]\n";
		$content = $parser->getMethodContent($name);
		$content = $parser->getContent() unless(defined $content);
		$Status = $parser->getContentStatus();
		$Code = $parser->getContentCode();
		$ContentType = $parser->getContentType();
	}

	print "Status:$Status\n" if(defined $Status);
#	print "Content-Type:$ContentType\n\n";
	#binmode(STDOUT);
	#print $content;

#	if(exists($parser->{jsonObj}->{callback})){
#		print $parser->{jsonObj}->{callback},"(",$content,")";
#	}else{
#		print $content;
#	}

	if($Code eq '200'){
		if(defined $parser && exists $parser->{jsonObj}->{callback}){
			say qq|Content-Type:application/javascript|;
		}else{
			say qq|Content-Type:$ContentType|;
		}
		&cgi_lib::common::_printContentJSON($content,$parser->{jsonObj});
	}else{
		&cgi_lib::common::printContent($content,$ContentType);
	}

	print $OUT __LINE__,":[$content]\n";
	close $OUT;
	$ag_log->print(defined $parser ? $parser->{'jsonObj'} : undef,$content,defined $parser ? $parser->getBalancerInformation() : undef);
}

1;
