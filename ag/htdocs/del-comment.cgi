#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use DBI;
use DBD::Pg;
use Image::Info qw(image_info dim);
use File::Path;

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

$FORM{lng} = $COOKIE{"ag_annotation.locale"} if(!exists($FORM{lng}) && exists($COOKIE{"ag_annotation.locale"})); #とりあえず
$FORM{lng} = "en" if(!exists($FORM{lng}));

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
open(LOG,">> log.txt");
print LOG "\n[$logtime]:$0\n";
foreach my $key (sort keys(%FORM)){
	print LOG "FORM{$key}=[",$FORM{$key},"]\n";
}
foreach my $key (sort keys(%COOKIE)){
	print LOG "COOKIE{$key}=[",$COOKIE{$key},"]\n";
}




my $RTN = {
	success => JSON::XS::false
};


#print qq|Content-type: text/html; charset=UTF-8\n\n|;


#if(!exists($FORM{f_id}) || !exists($FORM{c_id}) || !exists($FORM{parent})){
#if(!exists($FORM{c_id}) || !exists($FORM{parent})){
if(!exists($FORM{c_id})){
	my $json = &cgi_lib::common::printContentJSON($RTN,\%FORM);
	say LOG __LINE__.qq|:$json|;
	close(LOG);
	exit;
}

my $parentURL = $FORM{parent} if(exists($FORM{parent}));
my ($lsdb_OpenID,$lsdb_Auth);
my $lsdb_Config;
my $lsdb_Identity;
if(defined $parentURL){
	($lsdb_OpenID,$lsdb_Auth,$lsdb_Config) = &openidAuth($parentURL);
}elsif(exists($COOKIE{openid_url}) && exists($COOKIE{openid_session})){
	($lsdb_OpenID,$lsdb_Auth,$lsdb_Config,$lsdb_Identity) = &AG::login::openidAuthSession($COOKIE{openid_url},$COOKIE{openid_session});
}


my $rows = &authFeedback($dbh,\%FORM,$lsdb_Auth,$lsdb_OpenID);

if($rows == 0){
	my $json = &cgi_lib::common::printContentJSON($RTN,\%FORM);
	say LOG __LINE__.qq|:$json|;
	close(LOG);
	exit;
}

my %IMG_FILE = {};


#my $rows;
my $sql;
$sql = qq|update comment set c_delcause=?,c_modified='now()' where c_id=?|;
print LOG qq|sql=[$sql]\n|;

my $c_delcause = "$logtime\n";
$c_delcause .= "DELETE\n";
if(defined $lsdb_OpenID){
	$c_delcause .= "$lsdb_OpenID\n";
}else{
	$c_delcause .= "PASSWORD\n";
}
$c_delcause .= "$ENV{HTTP_USER_AGENT}\n";
$c_delcause .= "$ENV{HTTP_REFERER}\n";
$c_delcause .= (exists($ENV{HTTP_X_FORWARDED_FOR}) ? $ENV{HTTP_X_FORWARDED_FOR} : $ENV{REMOTE_ADDR});

$dbh->{AutoCommit} = 0;
$dbh->{RaiseError} = 1;
$rows = 0;
eval{
	my $sth = $dbh->prepare($sql) or return undef;
	$sth->execute($c_delcause,$FORM{c_id});
	my $rows = $sth->rows;
	$sth->finish;

	undef $sth;
	if($rows>=0){
		$dbh->commit();
	}else{
		$dbh->rollback();
	}
};
if($@){
	my $msg = $@;
	$dbh->rollback();
}
$dbh->{AutoCommit} = 1;
$dbh->{RaiseError} = 0;

$RTN->{'success'} = JSON::XS::true if($rows>=0);
my $json = &cgi_lib::common::printContentJSON($RTN,\%FORM);
say LOG __LINE__.qq|:$json|;


if($rows>0){
	if(exists($FORM{c_image})){
		unlink $FORM{c_image} if(-e $FORM{c_image});
		print LOG qq|file=[$FORM{c_image}]\n|;
	}
	if(exists($FORM{c_image_thumb})){
		unlink $FORM{c_image_thumb} if(-e $FORM{c_image_thumb});
		print LOG qq|file=[$FORM{c_image_thumb}]\n|;
	}
}


close(LOG);
exit;
