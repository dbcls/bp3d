#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use CGI;
use LWP::UserAgent;
use Net::OpenID::Consumer;
use JSON::XS;
use Digest::MD5 qw(md5 md5_hex md5_base64);

use File::Spec::Functions qw(catdir catfile);
use Cwd;
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'API'),&Cwd::abs_path(&catdir($FindBin::Bin,'..','lib')),&Cwd::abs_path(&catdir($FindBin::Bin,'..','..','ag-common','lib'));
use cgi_lib::common;

require "common.pl";
my %FORM = ();
&decodeForm(\%FORM);
delete $FORM{_formdata} if(exists($FORM{_formdata}));

my %COOKIE = ();
&getCookie(\%COOKIE);

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
	"success" => "false"
};

my $cgi = CGI->new;
$cgi->charset('utf-8');
my $CLAIMED_URL = $cgi->param('openid_url');
my $callback = $cgi->param('callback');
my $csr = Net::OpenID::Consumer->new(
	ua              => LWP::UserAgent->new,
	args            => $cgi,
	consumer_secret => 'bits.cc',
	required_root   => 'http://www.gbits.co.jp/project/OpenID/',
	#debug => 1,
);


if(defined $CLAIMED_URL){
	my $claimed_identity = $csr->claimed_identity($CLAIMED_URL) || &result();
	if(defined $claimed_identity){
		$RESULT->{"success"} = "true";
		$RESULT->{"session"} = md5_hex($logtime.$$."bits.cc");
	}
}

&result();

exit;

sub result {
#	my $json = to_json($RESULT);

	my $json = &cgi_lib::common::printContentJSON($RESULT,\%FORM);

#	my $json = encode_json($RESULT);
#	$json =~ s/"(true|false)"/$1/mg;
#	$json = $callback."(".$json.")\n" if(defined $callback);
#	print qq|Content-type: text/javascript; charset=UTF-8\n\n|;
#	print $json;

	print LOG "$json\n";
	close(LOG);

	exit;
}
