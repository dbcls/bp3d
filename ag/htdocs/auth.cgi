#!/bp3d/local/perl/bin/perl
#ユーザがログインしているかの判定のみ
$| = 1;

use strict;
use warnings;
use feature ':5.10';

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI::Cookie;
use JSON::XS;

use File::Spec::Functions qw(catdir catfile);
use Cwd;
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'API'),&Cwd::abs_path(&catdir($FindBin::Bin,'..','lib')),&Cwd::abs_path(&catdir($FindBin::Bin,'..','..','ag-common','lib'));
use cgi_lib::common;
use AG::login;

my $RTN = {
	success => JSON::XS::false
};


my %FORM = ();
my %COOKIE = ();

eval{
	require "common.pl";
	require "common_db.pl";

	my $query = CGI->new;
	&getParams($query,\%FORM,\%COOKIE);

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

	$RTN->{'success'} = JSON::XS::true if(defined $lsdb_OpenID);
};
#if($@){
#	$RTN->{'msg'} = $@;
#	&utf8::decode($RTN->{'msg'}) unless(utf8::is_utf8($RTN->{'msg'}));
#}

#print qq|Content-type: text/html; charset=UTF-8\n\n|;
#print &JSON::XS::encode_json($RTN);

&cgi_lib::common::printContentJSON($RTN,\%FORM);
