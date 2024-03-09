#!/usr/bin/perl

$| = 1;
select(STDERR);
$| = 1;
select(STDOUT);

use File::Basename;
use File::Spec;
use JSON::XS;
use Cwd qw(abs_path);
use Hash::Merge qw( merge );
Hash::Merge::set_behavior('LEFT_PRECEDENT');
use File::Path;
use File::Copy;
use List::Util;
use Math::Round;
use POSIX qw( floor );
use File::Spec;
use Digest::MD5;

my $USE_CPU_NUM = 4;

my $lib_path;
my $xvfb_lock;
my $display_size;

my $inter_files;

sub sigexit {
	warn __LINE__,":INT!!\n";
	eval{close(OUT);};
	if(defined $inter_files){
		foreach my $file (@$inter_files){
			unlink $file if(-e $file);
		}
	}
	exit;
}

my $DISPLAY;
my $curtime;
sub setDisplay {
	#未使用のdisplayを探す
	my $display;
	for($display=0;;$display++){
		$xvfb_lock = qq|/tmp/.X$display-lock|;
		last unless(-e $xvfb_lock);
	}
	$DISPLAY = $display;
	$ENV{'DISPLAY'} = qq|:$display|;
warn __LINE__,":[$$][$curtime]:\$DISPLAY=[$DISPLAY]\n";

	$display_size = qq|640x640|;
	foreach my $val (@ARGV){
		next unless($val =~ /^[0-9]{3,}x[0-9]{3,}$/);
		$display_size = $val;
		last;
	}

	my $cmd = '/usr/bin/Xvfb '. $ENV{'DISPLAY'} . ' -screen 0 '. $display_size .'x24 > /dev/null 2>&1 &';
	system($cmd);
}

sub unsetDisplay {
	if(defined $DISPLAY && defined $xvfb_lock){
warn __LINE__,":[$$][$curtime]:\$DISPLAY=[$DISPLAY]\n";
		my $lock_file = qq|/tmp/.X$DISPLAY-lock|;
		if($xvfb_lock eq $lock_file && -e $lock_file){
			my $pid = `cat $lock_file`;
			$pid =~ s/\s*$//g;
			$pid =~ s/^\s*//g;
			kill 2,$pid;
		}
	}
#	&python_end();
}

my $sys_lock_file;
my $lock_file;

BEGIN{
	$curtime = time();
	my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($curtime);
	my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);


	warn __LINE__,":[$$][$curtime][$logtime]:BEGIN:1!!\n";
#	$lib_path = dirname(abs_path($0)).qq|/../local/usr/lib/perl|;

=pod
	close(STDERR);
	close(STDOUT);

	my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
	my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
	my @extlist = qw|.cgi|;
	my($cgi_name,$cgi_dir,$cgi_ext) = fileparse($0,@extlist);
	open(STDOUT,">> logs/$cgi_name.stdout.txt");
	flock(STDOUT,2);
	print "\n[$logtime]:$0\n";

	open(STDERR,">> logs/$cgi_name.stderr.txt");
	flock(STDERR,2);
	print STDERR "\n[$logtime]:$0\n";
=cut

	warn __LINE__,":[$$][$curtime]:\$sys_lock_file=[$sys_lock_file]\n";
	if(scalar @ARGV > 0 && -d $ARGV[0]){
		my @extlist = qw|.pl|;
		my($cgi_name,$cgi_dir,$cgi_ext) = fileparse(abs_path($0),@extlist);
		$sys_lock_file = File::Spec->catfile($cgi_dir,'tmp_image',&Digest::MD5::md5_hex($ARGV[0]).qq|.lock|);
		warn __LINE__,":[$$][$curtime]:\$sys_lock_file=[$sys_lock_file]\n" if(defined $sys_lock_file);
		mkdir($sys_lock_file) or undef $sys_lock_file;
		warn __LINE__,":[$$][$curtime]:\$sys_lock_file=[$sys_lock_file]\n" if(defined $sys_lock_file);
#		sleep(5) if(defined $sys_lock_file);
	}else{
		&setDisplay();
	}
	$SIG{'HUP'} = $SIG{'INT'} = $SIG{'QUIT'} = $SIG{'ILL'} = $SIG{'TRAP'} = $SIG{'ABRT'} = $SIG{'BUS'} = $SIG{'FPE'} = $SIG{'KILL'} = $SIG{'TERM'} = "sigexit";

	warn __LINE__,":[$$][$curtime][$logtime]:BEGIN:2!!\n";
}

END{
	my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
	my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
	warn __LINE__,":[$$][$curtime][$logtime]:END:1!!\n";
	&unsetDisplay();

#	my @extlist = qw|.cgi|;
#	my($cgi_name,$cgi_dir,$cgi_ext) = fileparse(abs_path($0),@extlist);
#	$lock_file = File::Spec->catfile($cgi_dir,qq|$cgi_name.lock|);

	warn __LINE__,":[$$][$curtime]:\$sys_lock_file=[$sys_lock_file]\n";
	if(defined $sys_lock_file && -d $sys_lock_file){
		rmdir($sys_lock_file) or warn __LINE__,":[$$][$curtime]:$!\n";
	}
	warn __LINE__,":[$$][$curtime][$logtime]:END:2!!\n";
}

if(scalar @ARGV > 0 && -d $ARGV[0]){
	warn __LINE__,":[$$][$curtime]:\$sys_lock_file=[$sys_lock_file]\n";
	unless(defined $sys_lock_file && -d $sys_lock_file){
		warn __LINE__,":[$$][$curtime]:EXIT!!\n";
		exit ;
	}
}else{
	if(defined $xvfb_lock){
		warn __LINE__,":[$$][$curtime]:\$xvfb_lock=[$xvfb_lock]\n";
		unless(defined $xvfb_lock && -e $xvfb_lock){
			warn __LINE__,":[$$][$curtime]:EXIT!!\n";
			exit;
		}
	}
}


#exit;

#use lib $lib_path;
#use BITS::Config;
#use BITS::DB;


use Inline Python;

use strict;

my $DEF_HEIGHT = 1800;
sub getZoomYRange {
	my $zoom = shift;
	return &List::Util::max(1,&Math::Round::round( exp(1) ** ((log($DEF_HEIGHT)/log(2)-$zoom) * log(2)) ));
}
sub getYRangeZoom {
	my $yrange = shift;
	return &Math::Round::round((log($DEF_HEIGHT)/log(2) - log($yrange)/log(2)) * 10) / 10;
}

sub _wait {
	my $break = shift;
	my $rtn = 0;
	my $pid = -1;
	do{
		$pid = wait;
#		warn __LINE__,":EXIT!!:[$pid][$break]\n";
		$rtn = $? if($pid!=-1 && $?);
		$pid=-1 if(defined $break);
	}while($pid!=-1);
#	warn __LINE__,":RETURN!!:[$pid][$break][$rtn]\n";
	return $rtn;
}

my($cgi_name,$cgi_dir,$cgi_ext) = fileparse(abs_path($0),".pl");
#warn __LINE__,":\$cgi_name=[$cgi_name]\n";
#warn __LINE__,":\$cgi_dir=[$cgi_dir]\n";
#warn __LINE__,":\$cgi_ext=[$cgi_ext]\n";

my @SRC;
my $dest;
#my $color = [1,0,0];
#my $color = [0.94,0.82,0.62];
my $color;
my $angle;

my $json_file;

foreach my $val (@ARGV){
	next if($val =~ /^[0-9]{3,}x[0-9]{3,}$/);
	if(-e $val){

warn __LINE__,":[$$][$curtime]:\$val=[$val]\n";

		if(-d $val){

			&unsetDisplay();
#			if(exists $ENV{'DISPLAY'} && defined $ENV{'DISPLAY'}){
#				$ENV{'DISPLAY'} = undef;
#				delete $ENV{'DISPLAY'};
#			}

#			$lock_file = File::Spec->catfile($cgi_dir,qq|$cgi_name.lock|);
warn __LINE__,":[$$][$curtime]:\$sys_lock_file=[$sys_lock_file]\n";
#			mkdir($lock_file) or die "$!:$lock_file";
			unless(-d $val){
				die __LINE__,":[$$][$curtime]:$sys_lock_file";
			}else{
				warn __LINE__,":[$$][$curtime]:",`ls -ld $sys_lock_file`;
			}
#exit;

			my $rtn = 0;
			while(1){
				my @FILES;
				if(open(CMD,qq{find $val -type f -name "*.json" | sort -u |})){
					while(<CMD>){
						chomp;
						push(@FILES,$_);
					}
					close(CMD);
				}
				my $files = scalar @FILES;
				warn __LINE__,":[$$][$curtime]:\$files=[$files]\n";

				last if($files == 0);

				my $pid;
				my $cnt;
				my $cpu_num=0;
				for($cnt=0;$cnt<$files;$cnt++){
					warn __LINE__,":[$$][$curtime]:\$cnt=[",($cnt+1),"/$files]\n";
					my $f = qq|$FILES[$cnt]|;
					warn __LINE__,":[$$][$curtime]:\$f=[$f]\n";
					$pid = fork;
					if(defined $pid && $pid == 0){
						undef $sys_lock_file if(defined $sys_lock_file);
						undef $DISPLAY if(defined $DISPLAY);
						undef $xvfb_lock if(defined $xvfb_lock);
						warn __LINE__,":[$$][$curtime]:START!!\n";
						warn __LINE__,":[$$][$curtime]:\$cnt=[",($cnt+1),"/$files]\n";
						my $cmd = qq|$0 "$f"|;
						warn __LINE__,":[$$][$curtime]:\$cmd=[$cmd]\n";
						system($cmd);
						warn __LINE__,":[$$][$curtime]:EXIT!!:[$?]\n";
						exit $?;
					}elsif(!defined $pid){
						die qq|no exec!!\n|;
					}else{
						$cpu_num++;
						warn __LINE__,":[$$][$curtime]:\$cpu_num=[$cpu_num]\n";
						if($USE_CPU_NUM<=$cpu_num){
							my $rtn = &_wait(1);
							warn __LINE__,":[$$][$curtime]:\$rtn=[$rtn]\n";
							last $rtn if($rtn);
							$cpu_num--;
						}else{
							sleep(1);
						}
					}
				}
				$rtn = &_wait();
				warn __LINE__,":[$$][$curtime]:\$rtn=[$rtn]\n";
				last if($rtn);

				undef @FILES;
			}
#			rmdir $lock_file if(defined $lock_file && -e $lock_file);
			exit $rtn;


		}elsif(-f $val){
			my($name,$dir,$ext) = fileparse($val,".obj");
			if(defined $ext && length($ext)>0){
				push(@SRC,$val);
			}else{
				my($name,$dir,$ext) = fileparse($val,".json");
				next unless(defined $ext && length($ext)>0);

				$json_file = $val;
				$lock_file = File::Spec->catfile($dir,qq|$name.lock|);
				mkdir($lock_file) or exit;

				my $IN;
				if(open($IN,"< $json_file")){
					my $str = "";
					while(<$IN>){
						chomp;
						$str .= $_;
					}
					close($IN);
					if(length($str)>0){
						my $json;
						eval{$json = decode_json($str);};
						if(defined $json){
							if(defined $json->{'src'}){
								if(ref $json->{'src'} eq 'ARRAY'){
									push(@SRC,@{$json->{'src'}});
								}elsif(-e $json->{'src'}){
									push(@SRC,$json->{'src'});
								}
							}
							if(defined $json->{'dest'}){
								$dest = $json->{'dest'};
							}
							if(defined $json->{'size'}){
								$display_size = $json->{'size'};
							}
							if(defined $json->{'width'} || defined $json->{'height'}){
								if(defined $json->{'width'} && defined $json->{'height'}){
									$display_size = $json->{'width'}.'x'.$json->{'height'};
								}elsif(defined $json->{'width'}){
									$display_size = $json->{'width'}.'x'.$json->{'width'};
								}elsif(defined $json->{'height'}){
									$display_size = $json->{'height'}.'x'.$json->{'height'};
								}
							}
							if(defined $json->{'color'} && ref $json->{'color'} eq 'ARRAY'){
								$color = $json->{'color'};
							}
							if(defined $json->{'angle'}){
								$angle = $json->{'angle'};
							}
						}
					}
				}else{
					rmdir($lock_file) if(defined $lock_file && -e $lock_file);
				}
			}
		}
	}else{
		unless(defined $dest){
			my($name,$dir,$ext) = fileparse($val);
#			warn __LINE__,":[$$][$curtime]:[$name][$dir]!!\n";
			next unless(defined $name && length($name)>0 && defined $dir && length($dir)>0);
			$dest = $val;
		}else{
			warn __LINE__,":[$$][$curtime]:$val!!\n";
		}
	}
}
unless(scalar @SRC>0){
	rmdir($lock_file) if(defined $lock_file && -e $lock_file);
	die "$0 [image size (640x640)] [src obj file [..]] [dest image prefix]\n";
}
#$dest = qq|temp/.$$| unless(defined $dest);
unless(defined $dest){
	$dest=File::Spec->catfile($cgi_dir, 'temp', ".$$");
}else{
	$dest = abs_path($dest);
}
warn __LINE__,":[$$][$curtime]:\$dest=[$dest]\n";

warn __LINE__,":[$$][$curtime]:\$angle=[$angle]\n" if(defined $angle);

eval{
	my $g_file = qq|$dest.gif|;
	my $f_file = qq|$dest\_front.png|;
	my $l_file = qq|$dest\_left.png|;
	my $b_file = qq|$dest\_back.png|;
	my $r_file = qq|$dest\_right.png|;

	my @src_mtimes;
	my @dest_mtimes;
	foreach my $src (@SRC){
		push(@src_mtimes,(stat($src))[9]) if(-e $src);
	}
	my $src_mtime = &List::Util::max(@src_mtimes);

	push(@dest_mtimes,(-e $g_file)?(stat($g_file))[9] : 0);
	push(@dest_mtimes,(-e $f_file)?(stat($f_file))[9] : 0);
	push(@dest_mtimes,(-e $l_file)?(stat($l_file))[9] : 0);
	push(@dest_mtimes,(-e $b_file)?(stat($b_file))[9] : 0);
	push(@dest_mtimes,(-e $r_file)?(stat($r_file))[9] : 0);
	my $dest_mtime = &List::Util::min(@dest_mtimes);

	if($src_mtime>$dest_mtime){
		my($name,$dir,$ext) = fileparse($dest);
		unless(-e $dir){
			my $m = umask();
			umask(0);
			&File::Path::mkpath($dir,0,0777);
			umask($m);
		}

	#	my $temp_dest = qq|tmp_image/$$|;
		my $temp_dest=File::Spec->catfile($cgi_dir, 'tmp_image', $$).$curtime;
		warn __LINE__,":[$$][$curtime]:\$temp_dest=[$temp_dest]\n";
		my($name,$dir,$ext) = fileparse($temp_dest);
		unless(-e $dir){
			my $m = umask();
			umask(0);
			&File::Path::mkpath($dir,0,0777);
			umask($m);
		}

		my $b = &bound(\@SRC);
		foreach my $v (@$b){$v+=0};
		my $fmax = &List::Util::max(abs($b->[0]-$b->[1]),abs($b->[2]-$b->[3]),abs($b->[4]-$b->[5]));
		my $fzoom = &getYRangeZoom($fmax);
		$fzoom = ($fzoom>0) ? $fzoom-0.1 : $fzoom;
		my $yRange = &getZoomYRange($fzoom);
		my $size = [640,640];
	#	$size = [$1+0,$2+0] if(defined $display_size && $display_size =~ /^([0-9]{3,})x([0-9]{3,})$/);
		my $bb;
		if(defined $angle){
			$bb = &obj2png($size,$color,\@SRC,undef,$temp_dest,$angle,$yRange,undef,undef);
		}else{
			$bb = &obj2animgif($size,$color,\@SRC,undef,$temp_dest,$yRange,undef,undef);
		}
		if(defined $bb && ref $bb eq 'ARRAY'){
			my $convert = qq|convert -geometry $display_size -sharpen 0.7| if($display_size ne '640x640');
			if(-e qq|$temp_dest.gif|){
				my $s_file = qq|$temp_dest.gif|;
				system(qq|$convert $s_file $s_file|) if($display_size ne '640x640');
				unlink $g_file if(-e $g_file);
				rename($s_file,$g_file) or &File::Copy::copy($s_file,$g_file) or warn __LINE__,":[$$][$curtime]:$!";
			}
			foreach my $f (@$bb){
				next unless(-e $f);
				if($f eq qq|$temp_dest-0.png|){
					my $s_file = qq|$temp_dest-0.png|;
					system(qq|$convert $s_file png8:$s_file|) if(defined $convert);
					unlink $f_file if(-e $f_file);
					rename($s_file,$f_file) or &File::Copy::copy($s_file,$f_file) or warn __LINE__,":[$$][$curtime]:$!";
				}elsif($f eq qq|$temp_dest-90.png|){
					my $s_file = qq|$temp_dest-90.png|;
					system(qq|$convert $s_file png8:$s_file|) if(defined $convert);
					unlink $l_file if(-e $l_file);
					rename($s_file,$l_file) or &File::Copy::copy($s_file,$l_file) or warn __LINE__,":[$$][$curtime]:$!";
				}elsif($f eq qq|$temp_dest-180.png|){
					my $s_file = qq|$temp_dest-180.png|;
					system(qq|$convert $s_file png8:$s_file|) if(defined $convert);
					unlink $b_file if(-e $b_file);
					rename($s_file,$b_file) or &File::Copy::copy($s_file,$b_file) or warn __LINE__,":[$$][$curtime]:$!";
				}elsif($f eq qq|$temp_dest-270.png|){
					my $s_file = qq|$temp_dest-270.png|;
					system(qq|$convert $s_file png8:$s_file|) if(defined $convert);
					unlink $r_file if(-e $r_file);
					rename($s_file,$r_file) or &File::Copy::copy($s_file,$r_file) or warn __LINE__,":[$$][$curtime]:$!";
				}
				next unless(-e $f);
				unlink $f;
			}
		}
	}
};
if($@){
	warn __LINE__,":ERROR!!:[$$][$curtime]:[$@]:$!";
}
unlink($json_file) if(defined $json_file && -e $json_file);
rmdir($lock_file) if(defined $lock_file && -e $lock_file);

exit;

__DATA__
__Python__
#import vtk
#import os
import sys
#import time
#import tempfile
#import subprocess
#import shlex
#import inspect
#import shutil
#import copy
from obj2image import obj2image

op = obj2image()
#op = None

def obj2animgif(size,color,obj_files1,obj_files2,dest_prefix,yRange,largerbbox,largerbboxYRange):
	if size:
		op.setSize(size)
	if color:
		op.setColor(color)
	return op.animgif(obj_files1,obj_files2,dest_prefix,yRange,largerbbox,largerbboxYRange)

def obj2png(size,color,obj_files1,obj_files2,dest_prefix,angle,yRange,largerbbox,largerbboxYRange):
	if size:
		op.setSize(size)
	if color:
		op.setColor(color)
	return op.png(obj_files1,obj_files2,dest_prefix,angle,yRange,largerbbox,largerbboxYRange)

def bound(obj_files):
	return op.bound(obj_files)

def python_end():
	op.__del__()
