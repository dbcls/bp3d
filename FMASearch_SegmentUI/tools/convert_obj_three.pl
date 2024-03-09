#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use File::Basename;
use File::Spec::Functions qw(abs2rel catdir catfile splitdir);
use File::Path;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
use BITS::Config;

$ENV{'AG_DB_NAME'} = 'bp3d'      unless(exists $ENV{'AG_DB_NAME'} && defined $ENV{'AG_DB_NAME'});
$ENV{'AG_DB_HOST'} = '127.0.0.1' unless(exists $ENV{'AG_DB_HOST'} && defined $ENV{'AG_DB_HOST'});
$ENV{'AG_DB_PORT'} = '8543'      unless(exists $ENV{'AG_DB_PORT'} && defined $ENV{'AG_DB_PORT'});

require "webgl_common.pl";
use cgi_lib::common;

my $dbh = &get_dbh();


unless(scalar @ARGV){
	say STDERR "$0 xxxxxxxx.obj [xxxxxxxx.obj ...]";
	exit 1;
}
umask(0);
my $convert_obj_three = &catfile($FindBin::Bin,'..','htdocs','static','js','three','utils','converters','obj','convert_obj_three.py');
my $total = scalar @ARGV;
my $count = $total;
foreach my $file (@ARGV){
	my($name,$dir,$ext) = &File::Basename::fileparse($file,qw/.obj/);
	my $js_file = &catfile($dir,qq|$name.js|);
	my $bin_file = &catfile($dir,qq|$name.bin|);
	my $json_file = &catfile($dir,qq|$name.json|);
	unless(-e $js_file && -s $js_file && -e $bin_file && -s $bin_file && -e $json_file && -s $json_file){
		my ($atime,$utime) = (stat($file))[8,9];
		printf('[%04d] : ',$count);
		unless(-e $js_file && -s $js_file && -e $bin_file && -s $bin_file){
			system(qq|python $convert_obj_three -i $file -o $js_file -t binary|);
			utime $atime,$utime,$js_file if(-e $js_file);
			utime $atime,$utime,$bin_file if(-e $bin_file);
		}
		unless(-e $json_file && -s $json_file){
			system(qq|python $convert_obj_three -i $file -o $json_file|);
			utime $atime,$utime,$json_file if(-e $json_file);
		}
	}
	$count--;
}
