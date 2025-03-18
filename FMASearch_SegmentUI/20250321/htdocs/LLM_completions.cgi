#!/opt/services/ag/local/perl/bin/perl

$| = 1;

use strict;
use JSON::XS;
#use Storable;
#use File::Spec;
#use Data::Dumper;
#use Clone;
#use Time::HiRes;
use LWP::UserAgent;

my %FORM = ();
my %COOKIE = ();
if(exists($ENV{'REQUEST_METHOD'})){

use CGI;
use CGI::Carp qw(fatalsToBrowser);
#use CGI::Cookie;

	my $q = CGI->new;
	my @param = $q->param();
	map { $FORM{$_} = $q->param($_) } @param;
#	print "@param"; 
}

my $data = {"version" => "20250301l500","parts" => [{"id" => "FMA59799-L","rgb" => "F5B041","opacity" => 1},{"id" => "FMA59799-R","rgb" => "F5B041","opacity" => 1},{"id" => "FMA27383-L","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27383-R","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27367-L","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27367-R","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27365-R","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27368-U","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27376-U","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27382-L","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27382-R","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27452-U","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27448-U","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27384-L","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27384-R","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27366-R","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27380-L","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27380-R","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27375-U","rgb" => "E5D0FA","opacity" => 1}],"camera" => [-0.13700103759765625,-1906.1342520713806,1319.7449951171875],"focus" => [-0.13700103759765625,-106.13425207138062,1319.7449951171875],"up" => [0,0,1],"zoom" => 10};

$data = {
	choices => [{
		message => {
			content => [{ 
				"id" => "call_12345xyz",
				"type" => "function",
				"function" => {
					"name" => "addPart",
					"arguments" =>  {"FMAID" => "FMA62046"}
				}
			}]
		}
	}]
};

#die __LINE__;

my $json = &JSON::XS::encode_json($data);
$json = $FORM{'callback'}.qq|($json)| if(exists $FORM{'callback'} && defined $FORM{'callback'} && length $FORM{'callback'});

if(exists $ENV{'REQUEST_METHOD'}){
	my $content_type = qq|application/json|;
	$content_type = qq|application/javascript| if(exists $FORM{'callback'} && defined $FORM{'callback'} && length $FORM{'callback'});
	#print qq|Status: 404 Mitsukaran!!\n|;
	print qq|Content-type: $content_type; charset=UTF-8\n|;
	print qq|\n|;
}
print $json;
