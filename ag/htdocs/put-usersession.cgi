#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use File::Basename;
use File::Path;
use File::Spec;

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
my %COOKIE = ();
if(exists($ENV{'REQUEST_METHOD'})){
	my $query = CGI->new;
	&getParams($query,\%FORM,\%COOKIE);
}else{
	&decodeForm(\%FORM);
	delete $FORM{_formdata} if(exists($FORM{_formdata}));
	&getCookie(\%COOKIE);
}

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = fileparse($0,@extlist);
#open(LOG,"> $FindBin::Bin/logs/$FORM{'ag_annotation.session'}.$cgi_name.txt");
#flock(LOG,2);
#print LOG "\n[$logtime]:$0\n";
#foreach my $key (sort keys(%FORM)){
#	print LOG "\$FORM{$key}=[",$FORM{$key},"]\n";
#}
#foreach my $key (sort keys(%COOKIE)){
#	print LOG "COOKIE{$key}=[",$COOKIE{$key},"]\n";
#}
#foreach my $key (sort keys(%ENV)){
#	print LOG "ENV{$key}=[",$ENV{$key},"]\n";
#}



my $RESULT = {
	"success" => JSON::XS::true,
};

unless(ref $FORM{info}){
	my @arr = split("&",$FORM{info});
	$FORM{info} = \@arr;
}
#print LOG __LINE__,":[",&setSession($FORM{info},$FORM{state},$FORM{keymap}),"]\n";
&AG::login::setSession($FORM{info},$FORM{state},$FORM{keymap});

&cgi_lib::common::printContentJSON($RESULT,\%FORM);

#print qq|Content-type: text/html; charset=UTF-8\n\n|;

#my $callback = $FORM{callback};

#my $json = &JSON::XS::encode_json($RESULT);

#$json = $callback."(".$json.")\n" if(defined $callback);
#print $json;
#print LOG __LINE__,":",$json,"\n";
#close(LOG);

exit;
