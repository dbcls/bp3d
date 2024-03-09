#!/bp3d/local/perl/bin/perl

use strict;
use JSON::XS;
use File::Basename;
use Cwd qw(abs_path);
use File::Spec;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
require "webgl_common.pl";

use BITS::Config;

my $query = CGI->new;
my @params = $query->param();
my %PARAMS = ();
foreach my $param (@params){
	$PARAMS{$param} = defined $query->param($param) ? $query->param($param) : undef;
	$PARAMS{$param} = undef if(defined $PARAMS{$param} && length($PARAMS{$param})==0);
}
$PARAMS{start} = 0 unless(defined $PARAMS{start});
$PARAMS{limit} = 25 unless(defined $PARAMS{limit});




#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $DATAS = {
	"datas" => [],
	"total" => 0
};

#		my $to = File::Spec->catfile($dir,$name,qq|all.json|);


my $data_dir = $BITS::Config::UPLOAD_PATH;
opendir(DIR,$data_dir) || die "[$data_dir] $!\n";
my @DIRS = map {qq|$data_dir/$_|} sort grep {$_ =~ /^[^\.]/ && -f qq|$data_dir/$_/all.json|} readdir(DIR);
closedir(DIR);

foreach my $dir (@DIRS){
	my ($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,$atime,$mtime,$ctime,$blksize,$blocks) = stat($dir);

	opendir(DIR,$dir) || die "[$dir] $!\n";
	my @FILES = map {qq|$dir/$_|} grep {$_ =~ /^[^\.]/ && $_ =~ /\.obj$/ && $_ !~ /\.org\.obj$/ && -f qq|$dir/$_|} readdir(DIR);
	closedir(DIR);

	my $dir_name = &File::Basename::basename($dir);

	push(@{$DATAS->{'datas'}},{
		name  => $dir_name,
		path  => qq|js/uploads/$dir_name|,
		ino   => $ino,
		num   => scalar @FILES,
		mtime => $mtime
	});
}
$DATAS->{'total'} = scalar @{$DATAS->{datas}};

#my $json = &JSON::XS::encode_json($DATAS);
#print $json;
&gzip_json($DATAS);
