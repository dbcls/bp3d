#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;

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
#$FORM{lng} = "ja" if(!exists($FORM{lng}));

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $file = sprintf("%04d%02d%02d%02d%02d%02d_%d",$year+1900,$mon+1,$mday,$hour,$min,$sec,$$);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
open(LOG,">> log.txt");
print LOG "\n[$logtime]:$0\n";
foreach my $key (sort keys(%FORM)){
	print LOG "\$FORM{$key}=[",$FORM{$key},"]\n";
}
#foreach my $key (sort keys(%COOKIE)){
#	print LOG "COOKIE{$key}=[",$COOKIE{$key},"]\n";
#}
#foreach my $key (sort keys(%ENV)){
#	print LOG "ENV{$key}=[",$ENV{$key},"]\n";
#}





#print qq|Content-type: text/html; charset=UTF-8\n\n|;


#return;

my $parentURL = $FORM{parent} if(exists($FORM{parent}));
my $lsdb_OpenID;
my $lsdb_Auth;
my $lsdb_Config;
my $lsdb_Identity;
if(defined $parentURL){
	($lsdb_OpenID,$lsdb_Auth,$lsdb_Config) = &openidAuth($parentURL);
}elsif(exists($COOKIE{openid_url}) && exists($COOKIE{openid_session})){
	($lsdb_OpenID,$lsdb_Auth,$lsdb_Config,$lsdb_Identity) = &AG::login::openidAuthSession($COOKIE{openid_url},$COOKIE{openid_session});
}
$lsdb_Auth = int($lsdb_Auth) if(defined $lsdb_Auth);

$FORM{type} = "sample" unless(exists($FORM{type}));

my $RTN = {
	success => JSON::XS::false,
	msg => undef
};

my $base_dir;
my $del_sql;
if($FORM{type} eq "sample"){
	unless(defined $lsdb_Auth){
		$RTN->{'msg'} = qq|There is no administrative privileges.|;
		my $json = &cgi_lib::common::printContentJSON($RTN,\%FORM);
		say LOG __LINE__.$json;
		close(LOG);
		exit;
	}
	$base_dir = "samples";
	$del_sql = qq|delete from sample where sp_id=?|;
}elsif($FORM{type} eq "user"){
	unless(defined $lsdb_OpenID){
		$RTN->{'msg'} = qq|Please login with OpenID.|;
		my $json = &cgi_lib::common::printContentJSON($RTN,\%FORM);
		say LOG __LINE__.$json;
		close(LOG);
		exit;
	}
	$base_dir = "users";
	$del_sql = qq|delete from save where sv_id=? and sv_openid=?|;
}elsif(exists($FORM{type})){
	$RTN->{'msg'} = qq|Unknown Type!!|;
	my $json = &cgi_lib::common::printContentJSON($RTN,\%FORM);
	say LOG __LINE__.$json;
	close(LOG);
	exit;
}

unless(exists($FORM{id})){
	$RTN->{'msg'} = qq|There is not Category information|;
	my $json = &cgi_lib::common::printContentJSON($RTN,\%FORM);
	say LOG __LINE__.$json;
	close(LOG);
	exit;
}

unless($FORM{id} =~ /^AGSMP/){
	$RTN->{'msg'} = qq|There is not Category information|;
	my $json = &cgi_lib::common::printContentJSON($RTN,\%FORM);
	say LOG __LINE__.$json;
	close(LOG);
	exit;
}

#my $RTN = {
#	"success" => "false",
#};

my $file_id = $FORM{id};
$file_id =~ s/^AGSMP//g;

$dbh->{AutoCommit} = 0;
$dbh->{RaiseError} = 1;

eval{

#	opendir(DIR,"samples");
#	my @FILES = grep {/^$file_id/} readdir(DIR);
#	close(DIR);
#	foreach my $file (@FILES){
#		unlink qq|samples/$file| if(-e qq|samples/$file|);
#	}
#	$RTN->{success} = "true";


	my $param_num = 0;
	my $sth;
	my $rows = -1;
	$sth = $dbh->prepare($del_sql);
	$sth->bind_param(++$param_num, $file_id);
	$sth->bind_param(++$param_num, $lsdb_OpenID) if($FORM{type} eq "user");
	$sth->execute();
	$rows = $sth->rows;
	$sth->finish;
	undef $sth;

	$RTN->{success} = JSON::XS::true if($rows>=0);
	if($rows>=0){
		$dbh->commit();
	}else{
		$dbh->rollback();
	}

};
if($@){
	my $msg = $@;
	$dbh->rollback();
#	$msg =~ s/\s*$//g;
#	$msg =~ s/^\s*//g;
#	$RTN = {
#		"success" => "false",
#		"msg"     => $msg
#	};
}
#	my $json = to_json($RTN);

my $json = &cgi_lib::common::printContentJSON($RTN,\%FORM);

#my $json = encode_json($RTN);
#$json =~ s/"(true|false)"/$1/mg;
#print $json;
print LOG __LINE__,":",$json,"\n";

close(LOG);
exit;
