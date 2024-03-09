#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use DBI;
use DBD::Pg;
#use Digest::MD5 qw(md5 md5_hex md5_base64);

use File::Spec::Functions qw(catdir catfile);
use Cwd;
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'API'),&Cwd::abs_path(&catdir($FindBin::Bin,'..','lib')),&Cwd::abs_path(&catdir($FindBin::Bin,'..','..','ag-common','lib'));
use cgi_lib::common;
use AG::login;

require "common.pl";
require "common_db.pl";
my $dbh = &get_dbh();

my %FORM = ();
&decodeForm(\%FORM);
delete $FORM{_formdata} if(exists($FORM{_formdata}));

my %COOKIE = ();
&getCookie(\%COOKIE);

#$FORM{lng} = $COOKIE{"ag_annotation.locale"} if(!exists($FORM{lng}) && exists($COOKIE{"ag_annotation.locale"})); #とりあえず
$FORM{lng} = "ja" if(!exists($FORM{lng}));

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
open(LOG,">> log.txt");
print LOG "\n[$logtime]:$0\n";
foreach my $key (sort keys(%FORM)){
	print LOG "\$FORM{$key}=[",$FORM{$key},"]\n";
}
#foreach my $key (sort keys(%COOKIE)){
#	print LOG "COOKIE{$key}=[",$COOKIE{$key},"]\n";
#}






#print qq|Content-type: text/html; charset=UTF-8\n\n|;


my $RTN = {success => JSON::XS::false};

#if(!exists($FORM{f_id}) || !exists($FORM{c_id}) || !exists($FORM{parent})){
if(!exists($FORM{c_id})){
	my $json = &cgi_lib::common::printContentJSON($RTN,\%FORM);

#	print qq|{success:false}|;
	say LOG __LINE__.$json;
	close(LOG);
	exit;
}

my $lsdb_OpenID;
my $lsdb_Auth;
my $parentURL = $FORM{parent} if(exists($FORM{parent}));
my $lsdb_Config;
my $lsdb_Identity;
if(defined $parentURL){
	($lsdb_OpenID,$lsdb_Auth,$lsdb_Config) = &openidAuth($parentURL);
}elsif(exists($COOKIE{openid_url}) && exists($COOKIE{openid_session})){
	($lsdb_OpenID,$lsdb_Auth,$lsdb_Config,$lsdb_Identity) = &AG::login::openidAuthSession($COOKIE{openid_url},$COOKIE{openid_session});
}


#if(!$lsdb_OpenID && !exists($FORM{c_passwd})){
#	print qq|{success:false}|;
#	print LOG __LINE__,qq|:{success:false}\n|;
#	close(LOG);
#	exit;
#}

my $rows = &authFeedback($dbh,\%FORM,$lsdb_Auth,$lsdb_OpenID);
$RTN->{'success'} = JSON::XS::true if($rows==1);
my $json = &cgi_lib::common::printContentJSON($RTN,\%FORM);
say LOG __LINE__.$json;

close(LOG);
exit;
