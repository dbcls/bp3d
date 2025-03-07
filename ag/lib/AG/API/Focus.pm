package AG::API::Focus;

use strict;
use warnings;
use feature ':5.10';

#use AG::API::JSONParser;
use base qw/AG::API::JSONParser/;
use File::Basename;
use JSON::XS;
use File::Spec;
use File::Spec::Functions qw(catdir catfile);
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
#	my $parser;
#	my @extlist = qw|.cgi|;
	my($name,$dir,$ext) = &File::Basename::fileparse($0,qr/\..*$/);

#	my $log_file = &catfile($dir,'tmp_image',qq|$name.txt|);
#	open my $OUT,"> $log_file";
	my $OUT = &cgi_lib::common::getLogFH(undef,undef,&AG::API::JSONParser::get_log_file_basename(),&AG::API::JSONParser::get_log_dir_basename($name));

	if(defined $json){
#		$parser = new AgJSONParser($json);
		if(defined $parser){
			print $OUT __LINE__,":[$parser->{json}]\n";
			$parser->{jsonObj}->{Camera}->{CameraMode} = "front";
			$parser->{jsonObj}->{Camera}->{Zoom} = 0;
			$parser->{json} = encode_json($parser->{jsonObj});
			print $OUT __LINE__,":[$parser->{json}]\n";

			$content = $parser->getMethodContent($name);
			$content = $parser->getContent() unless(defined $content);
			$Status = $parser->getContentStatus();
			$Code = $parser->getContentCode();
			$ContentType = $parser->getContentType();
		}
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
		&cgi_lib::common::_printContentJSON($content,defined $parser ? $parser->{'jsonObj'} : undef);
	}else{
		&cgi_lib::common::printContent($content,$ContentType);
	}

	print $OUT __LINE__,":[$content]\n" if(defined $content);
	close $OUT;
	$ag_log->print(defined $parser ? $parser->{'jsonObj'} : undef,$content,defined $parser ? $parser->getBalancerInformation() : undef);
}

1;
