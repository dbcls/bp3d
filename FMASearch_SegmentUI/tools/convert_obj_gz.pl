#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use File::Basename;
use File::Spec::Functions qw(abs2rel catdir catfile splitdir);
use File::Path;
use File::Copy;

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

my $total = scalar @ARGV;
my $count = $total;
foreach my $file (@ARGV){
	my($name,$dir,$ext) = &File::Basename::fileparse($file,qw/.obj/);
	my ($atime,$utime) = (stat($file))[8,9];
	my $old_gzip_file = &catfile($dir,qq|$name.obj.gz|);
	my $gzip_file = &catfile($dir,qq|$name.ogz|);

	&File::Copy::move($old_gzip_file,$gzip_file) if(-e $old_gzip_file);

	my $gz_atime = 0;
	my $gz_utime = 0;
	($gz_atime,$gz_utime) = (stat($gzip_file))[8,9] if(-e $gzip_file && -f $gzip_file);

	printf("[%04d] : %s\r",$count,$name);
	unless($utime == $gz_utime){
		system(qq|/bin/gzip -c -9 $file > $gzip_file|);
		utime $atime,$utime,$gzip_file if(-e $gzip_file);
	}
	$count--;
}
say '';
