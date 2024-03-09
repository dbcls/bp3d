#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI::Cookie;

use File::Spec::Functions qw(catdir catfile);
use Cwd;
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'API'),&Cwd::abs_path(&catdir($FindBin::Bin,'..','lib')),&Cwd::abs_path(&catdir($FindBin::Bin,'..','..','ag-common','lib'));
use cgi_lib::common;
use AG::login;

require "common.pl";
require "common_db.pl";

my %FORM = ();
#&decodeForm(\%FORM);
#delete $FORM{_formdata} if(exists($FORM{_formdata}));

my %COOKIE = ();
#&getCookie(\%COOKIE);

my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
open(LOG,">> log.txt");
select(LOG);$|=1;select(STDOUT);
print LOG "\n[$logtime]:$0\n";
foreach my $key (sort keys(%FORM)){
	print LOG "\$FORM{$key}=[",$FORM{$key},"]\n";
}
foreach my $key (sort keys(%COOKIE)){
	print LOG "\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
}

my $RESULT = {
	'success' => JSON::XS::true
};
my $callback = $FORM{callback};

&AG::login::openidLogoutSession($COOKIE{'openid_url'},$COOKIE{'openid_session'}) if(exists($COOKIE{'openid_url'}) && exists($COOKIE{'openid_session'}));

#my $cookie_path="/";
#if(exists $ENV{REQUEST_URI} && defined $ENV{REQUEST_URI}){
#	$cookie_path=$ENV{REQUEST_URI};
#	$cookie_path=~s/[^\/]*$//g;
#}elsif(exists $ENV{SCRIPT_URL} && defined $ENV{SCRIPT_URL}){
#	$cookie_path=$ENV{SCRIPT_URL};
#	$cookie_path=~s/[^\/]*$//g;
#}
#my $secure = exists $ENV{HTTPS} ? 1 : 0;
#my $httponly = 1;
#print "Set-Cookie: ".CGI::Cookie->new(-name=>'openid_session',-value=>'',-expires=>'-1d',-path=>$cookie_path,-secure=>$secure,-httponly=>$httponly)."\n";
print &clearCookie('openid_session')," HttpOnly\n";

&result();

exit;

sub result {
#	my $json = to_json($RESULT);
#	$json =~ s/"(true|false)"/$1/mg;

	my $json = &cgi_lib::common::printContentJSON($RESULT,\%FORM);

#	my $json = &JSON::XS::encode_json($RESULT);
#	$json = $callback."(".$json.")\n" if(defined $callback);
#	print qq|Content-type: text/javascript; charset=UTF-8\n\n|;
#	print $json;

	print LOG "$json\n";
	close(LOG);

	exit;
}
