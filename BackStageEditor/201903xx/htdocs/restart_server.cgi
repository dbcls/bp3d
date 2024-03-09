#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use JSON::XS;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
require "webgl_common.pl";

#print qq|Content-type: text/html; charset=UTF-8\n\n|;
my $RTN = {
	success => JSON::XS::true
};
#print &JSON::XS::encode_json($RTN);
&gzip_json($RTN);

my $path = &getApachectlPath();
my $pid = fork;
if(defined $pid){
	if($pid == 0){
		close(STDOUT);
		close(STDERR);
		close(STDIN);
		exec(qq|$path -k restart|);
		exit(1);
	}
}else{
	die("Can't execute program");
}
