#!/bp3d/local/perl/bin/perl

use strict;
use feature ':5.10';
use Time::HiRes;
use File::Basename;
use File::Spec;
use JSON::XS;

use constant {
	INTERVAL_SECOND => 60*60*24
};

sub main {

	my($name, $dir, $ext) = &File::Basename::fileparse($0, qr/\..*$/);
	my $log_dir = File::Spec->catfile($dir,'..','..','..','tmp_image','*','*','*');
	my $cmd = qq|find $log_dir -mtime +1 -type f -exec gzip {} \\;|;
	say $cmd;
	exit 0;

	my($wtime,$msec) = &Time::HiRes::gettimeofday();
	my $itime = $wtime - INTERVAL_SECOND;
	while(1){
		my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($itime);
		$year = sprintf("%04d",$year+1900);
		$mon  = sprintf("%02d",$mon+1);
		$mday = sprintf("%02d",$mday);

		my $log_dir = File::Spec->catfile($dir,'..','..','..','tmp_image',$year,$mon,$mday);
		say $log_dir;
		last unless(-e $log_dir);
		chdir $log_dir;
		say $log_dir;
		my @text_files = glob "*.txt";
		last unless(scalar  @text_files);
		foreach my $text_file (@text_files){
			say $text_file;
		}
		$itime -= INTERVAL_SECOND;
	}
}

&main();
