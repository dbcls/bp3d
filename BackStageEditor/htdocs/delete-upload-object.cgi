#!/bp3d/local/perl/bin/perl

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use Cwd qw(abs_path);
use File::Basename;
use File::Spec;
use File::Copy;
use File::Path;
use JSON::XS;
use Encode;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
use BITS::FreeFormObj;

my $query = CGI->new;
my @params = $query->param();
my %PARAMS = ();
foreach my $param (@params){
	$PARAMS{$param} = defined $query->param($param) ? $query->param($param) : undef;
	$PARAMS{$param} = undef if(defined $PARAMS{$param} && length($PARAMS{$param})==0);
}

my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = fileparse($0,@extlist);

open(LOG,"> $FindBin::Bin/$cgi_name.txt");
foreach my $key (sort keys(%PARAMS)){
	print LOG __LINE__,qq|:\$PARAMS{$key}=[$PARAMS{$key}]\n|;
}

print qq|Content-type: text/html; charset=UTF-8\n\n|;
my $RTN = {
	success => JSON::XS::false
};

if(defined $PARAMS{names}){
	my $NAMES = &JSON::XS::decode_json($PARAMS{names});
	foreach my $name (@$NAMES){
		print LOG __LINE__,qq|:\$name=[$name]\n|;
		&BITS::FreeFormObj::DeleteObj($name);
	}
}

$RTN->{success} = JSON::XS::true;
print encode_json($RTN);
