#!/opt/services/ag/local/perl/bin/perl

$| = 1;

use strict;
use JSON::XS;
#use Storable;
#use File::Spec;
use Data::Dumper;
#use Clone;
#use Time::HiRes;
use LWP::UserAgent;
use Hash::Merge;

use File::Spec::Functions qw(catdir catfile);
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'..','cgi_lib'),q|/opt/services/ag/ag-common/lib|;
use BITS::Config;
require "webgl_common.pl";
use cgi_lib::common;

my $LOG;
my %FORM = ();
my %COOKIE = ();
if(exists($ENV{'REQUEST_METHOD'})){

use CGI;
use CGI::Carp qw(fatalsToBrowser);
#use CGI::Cookie;

	my $q = CGI->new;
	#my @param = $q->param();
	#map { $FORM{$_} = $q->param($_) } @param;
#	print "@param"; 

	&getParams($q,\%FORM,\%COOKIE);
	my($logfile,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

	$FORM{$_} = &cgi_lib::common::decodeUTF8($FORM{$_}) for(keys(%FORM));

	my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
	my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
#$logfile .= '.'.sprintf("%04d%02d%02d%02d",$year+1900,$mon+1,$mday,$hour);
	$logfile .=  sprintf(".%02d%02d%02d.%05d",$hour,$min,$sec,$$);

#open(my $TRACE,">> $logfile.trace");
#select($TRACE);
#$| = 1;
#select(STDOUT);
#$dbh->trace('3|SQL', $TRACE);
#$dbh->trace('3|SQL', "$logfile.trace");

	if(1){
		open($LOG,">> $logfile");
		select($LOG);
		$| = 1;
		select(STDOUT);

		flock($LOG,2);
		print $LOG "\n[$logtime]:$0\n";
		&cgi_lib::common::message(\%FORM, $LOG);
	}

}

sub main {
	my $data = {"version" => "20250301l500","parts" => [{"id" => "FMA59799-L","rgb" => "F5B041","opacity" => 1},{"id" => "FMA59799-R","rgb" => "F5B041","opacity" => 1},{"id" => "FMA27383-L","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27383-R","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27367-L","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27367-R","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27365-R","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27368-U","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27376-U","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27382-L","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27382-R","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27452-U","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27448-U","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27384-L","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27384-R","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27366-R","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27380-L","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27380-R","rgb" => "E5D0FA","opacity" => 1},{"id" => "FMA27375-U","rgb" => "E5D0FA","opacity" => 1}],"camera" => [-0.13700103759765625,-1906.1342520713806,1319.7449951171875],"focus" => [-0.13700103759765625,-106.13425207138062,1319.7449951171875],"up" => [0,0,1],"zoom" => 10};

	my $llm_configuration = {
		API_KEY       => 'your-openai-api-key',
		API_URL       => 'https://api.openai.com/v1/chat/completions',
		Model         => 'gpt-4o',
		System_role   => 'developer',
		System_prompt => '',
		Max_tokens    => 300,
		Temperature   => 0.7,
		Tools         => {}
	};
	my $form_configuration = &JSON::XS::decode_json($FORM{'configuration'} // '{}');

	$llm_configuration = &Hash::Merge::merge($form_configuration, $llm_configuration);
	if(exists $ENV{'AG_DEBUG'} && defined $ENV{'AG_DEBUG'} && $ENV{'AG_DEBUG'} eq '1'){
		$llm_configuration->{'API_URL'} = 'https://bp3d-dev.dbcls.jp/FMASearch_SegmentUI/development/LLM_completions.cgi';
	}
	my $content = {
		model => $llm_configuration->{'Model'},
		messages => [{ 
			role => $llm_configuration->{'System_role'},
			content => $llm_configuration->{'System_prompt'}
		},{ 
			role => 'user',
			content => $FORM{'prompt'}
		}], 
		max_tokens => $llm_configuration->{'Max_tokens'},
		temperature => $llm_configuration->{'Temperature'}
	};
	my $ua = LWP::UserAgent->new;
	my $req = HTTP::Request->new(POST => $llm_configuration->{'API_URL'});
	$req->header('Authorization' => qq|Bearer $llm_configuration->{'API_KEY'}|);
	$req->content_type('application/json');
	$req->content(&JSON::XS::encode_json($content));
	&cgi_lib::common::message($req->as_string, $LOG) if(defined $LOG);
	my $res = $ua->request($req);
	#print Data::Dumper::Dumper($res);
	#print $res->code."\n";
	#print $res->message."\n";
	#print $res->as_string;
	&cgi_lib::common::message($res->as_string, $LOG) if(defined $LOG);
	if($res->is_success){
#		my $data = &JSON::XS::decode_json($res->decoded_content);
#		my $json = &JSON::XS::encode_json($data->{'choices'}->[0]->{'message'}->{'content'});

		my $json = $res->decoded_content;
		&cgi_lib::common::message($json, $LOG) if(defined $LOG);

		#my $json = &JSON::XS::encode_json($data);
		$json = $FORM{'callback'}.qq|($json)| if(exists $FORM{'callback'} && defined $FORM{'callback'} && length $FORM{'callback'});

		if(exists $ENV{'REQUEST_METHOD'}){
			my $content_type = qq|application/json|;
			$content_type = qq|application/javascript| if(exists $FORM{'callback'} && defined $FORM{'callback'} && length $FORM{'callback'});
			print qq|Content-type: $content_type; charset=UTF-8\n|;
			print qq|\n|;
		}
		print $json;
	}
	elsif($res->is_error){
		if(exists $ENV{'REQUEST_METHOD'}){
			print qq|Status: |.$res->status_line.qq|\n|;
			print qq|\n|;
		}
		&cgi_lib::common::message($res->decoded_content, $LOG) if(defined $LOG);
		print $res->decoded_content;
	}
}

&main();

close($LOG) if(defined $LOG);
