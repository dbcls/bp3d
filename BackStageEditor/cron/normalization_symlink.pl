#!/bp3d/local/perl/bin/perl

use strict;

use FindBin;
use Cwd qw(abs_path);

use constant {
	FIND_PATH => '/bp3d/bp3d_images/'
};

BEGIN {
	chdir($FindBin::Bin);
}

open(CMD,"find /bp3d/bp3d_images/ -type l 2> /dev/null |") or die $!,"\n";
while(<CMD>){
	chomp;
#	my $abs_path = &Cwd::abs_path($_);
	my $abs_path = $_;
	if(-e $abs_path && -l $abs_path){
		my $link_path = readlink($abs_path);
		if($link_path =~ /\/opt\/services\/ag\/system_130930\/cron/){
			$link_path =~ s/\/system_130930\/cron//g;
			print qq|[$abs_path]->[$link_path]\n|;
#			unlink $abs_path;
#			symlink $link_path, $abs_path or die "$!:$link_path:$abs_path";
		}
	}elsif(-e $abs_path && -f $abs_path){
		print qq|[$abs_path]->???\n|;
		my $link_path = readlink($abs_path) or die "$!:$abs_path";
		print qq|[$abs_path]->[$link_path]\n|;
		exit;
	}elsif(-e $abs_path){
		print qq|[$abs_path]->???\n|;
	}else{
#		print qq|[$abs_path]->???\n|;
		unlink $abs_path;
	}
}
close(CMD);
