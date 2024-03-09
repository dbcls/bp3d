#!/bp3d/local/perl/bin/perl

$| = 1;
select(STDERR);
$| = 1;
select(STDOUT);

use strict;
use warnings;
use feature ':5.10';

use File::Basename;
use File::Spec::Functions;
use JSON::XS;
use Cwd qw(abs_path);
use Hash::Merge qw( merge );
Hash::Merge::set_behavior('LEFT_PRECEDENT');
use File::Path;
use File::Copy;
use List::Util;
use Math::Round;
use POSIX qw( floor );
use DBD::Pg;
use Data::Dumper;

use FindBin;
my $htdocs_path;
my $common_path;
BEGIN{
	use FindBin;
#	$htdocs_path = qq|$FindBin::Bin/../htdocs_130910|;
	$htdocs_path = qq|$FindBin::Bin/../htdocs| unless(defined $htdocs_path && -e $htdocs_path);

	$common_path = qq|/bp3d/ag-common/lib|;
}
use lib $FindBin::Bin,$htdocs_path,qq|$htdocs_path/../cgi_lib|,$common_path;

use Getopt::Long qw(:config posix_default no_ignore_case gnu_compat);
my $config = {
	host => '127.0.0.1',
	port => '8543'
};
&Getopt::Long::GetOptions($config,qw/
	host|h=s
	port|p=s
/) or exit 1;

$ENV{'AG_DB_HOST'} = $config->{'host'};
$ENV{'AG_DB_PORT'} = $config->{'port'};


use BITS::ArtFile;
use BITS::ImageC;
require "webgl_common.pl";
use cgi_lib::common;

use renderer;

use constant {
	DEF_SERVER_NUMBRT => 98,
	MAX_PROG => 14,

	TMPFS => '/dev/shm',

	USE_BP3D_COLOR => 1,
	DEBUG_USE_BP3D_COLOR => 0,
};

my $dbh = &get_dbh();

#my $lib_path;
my $xvfb_lock;
my $display_size;
my $txt_file_lock;

my $inter_files;
my $tmp_base_path;
my $tmp_img_prefix;

sub sigexit {
	print __LINE__,":INT!![$txt_file_lock]\n";
	print __LINE__,":$@\n";
	eval{close(OUT);};
	if(defined $inter_files){
		foreach my $file (@$inter_files){
			unlink $file if(-e $file);
		}
	}
	&File::Path::remove_tree($tmp_base_path) if(defined $tmp_base_path && -e $tmp_base_path && -d $tmp_base_path);
	&File::Path::remove_tree($txt_file_lock) if(defined $txt_file_lock && -e $txt_file_lock && -d $txt_file_lock);
#	rmdir($txt_file_lock) if(defined $txt_file_lock);
	exit;
}

sub getDisplay {
	#未使用のdisplayを探す
	my $display;
	for($display=0;;$display++){
		last unless(-e qq|/tmp/.X$display-lock|);
	}
	return $display;
}

sub setDisplay {
	#未使用のdisplayを探す
	my $display = &getDisplay();
	$ENV{'DISPLAY'} = qq|:$display|;

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
	if(exists $ENV{'DISPLAY'} && defined $ENV{'DISPLAY'}){
		my $d = $ENV{'DISPLAY'};
		$d =~ s/:(\d+)$/$1/;
		my $lock_file = qq|/tmp/.X$d-lock|;
		if(-e $lock_file){
			my $pid = `cat $lock_file`;
			$pid =~ s/\s*$//g;
			$pid =~ s/^\s*//g;
			kill 2,$pid;
		}
	}
#	&python_end();
}

my $LOCK;
BEGIN{
	print __LINE__,":BEGIN!!1\n";
=pod
	my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,qr/\.[^\.]+$/);
	my $lock_file = qq|$FindBin::Bin/logs/$cgi_name.lock|;
	unless(-e $lock_file){
		open($LOCK,"> $lock_file") or die $!;
		unless(flock($LOCK, 6)){
			close($LOCK);
			undef $LOCK;
			exit;
		}
	}
=cut

=pod
	unless(exists $ENV{'DISPLAY'} && defined $ENV{'DISPLAY'}){
		my $server_number = DEF_SERVER_NUMBRT;
		$server_number = &getDisplay() if($server_number<0);
		exit unless(defined $server_number);

		if($server_number>0){
			exec qq|xvfb-run -n $server_number -s "-screen 0 640x640x24" $0|;
			exit;
		}else{
			$ENV{'DISPLAY'} = qq|:0|;
		}
	}
=cut
	print __LINE__,":BEGIN!!\n";

#	&setDisplay();

	$SIG{'HUP'} = $SIG{'INT'} = $SIG{'QUIT'} = $SIG{'ILL'} = $SIG{'TRAP'} = $SIG{'ABRT'} = $SIG{'BUS'} = $SIG{'FPE'} = $SIG{'KILL'} = $SIG{'USR1'} = $SIG{'SEGV'} = $SIG{'USR2'} = $SIG{'TERM'} = "sigexit";
}
END{
	&File::Path::remove_tree($tmp_base_path) if(defined $tmp_base_path && -e $tmp_base_path && -d $tmp_base_path);
	&File::Path::remove_tree($txt_file_lock) if(defined $txt_file_lock && -e $txt_file_lock && -d $txt_file_lock);
	close($LOCK) if(defined $LOCK);
	print __LINE__,":END!!\n";
#	&unsetDisplay();
}

#use lib $lib_path;
#use BITS::Config;
#use BITS::DB;


#use Inline Python;

my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,qr/\.[^\.]+$/);

#my $lock_dirpath = &catdir($FindBin::Bin,'logs');
my $lock_dirpath = &catdir(TMPFS,$cgi_name);
unless(-e $lock_dirpath){
	my $m = umask(0);
	&File::Path::make_path($lock_dirpath,{verbose => 0, mode => 0777});
	umask($m);
}

my $lock_filefmt = qq|$cgi_name.lock-%d|;
my $lock_no=0;
#my $LOCK;
for(;$lock_no<MAX_PROG;$lock_no++){
	my $lock_filepath = &catdir($lock_dirpath,sprintf($lock_filefmt,$lock_no));
	print __LINE__,":\$lock_filepath=[$lock_filepath]\n";
	if(-e $lock_filepath){
		open($LOCK,"+< $lock_filepath") or die qq|[$lock_filepath]:$!|;
	}else{
		open($LOCK,"> $lock_filepath") or die qq|[$lock_filepath]:$!|;
	}
	last if(flock($LOCK, 6));
}
exit unless($lock_no<MAX_PROG);


my $art_file_prefix = &catdir($FindBin::Bin,qq|art_file|);
unless(-e $art_file_prefix){
	my $m = umask(0);
	&File::Path::make_path($art_file_prefix,{verbose => 0, mode => 0777});
	umask($m);
}
#my $art_file_fmt = qq|$art_file_prefix/%s-%d%s|;
my $art_file_fmt = qq|$art_file_prefix/%s%s|;

my $ART_INFOS;
if(defined $ARGV[0] && -e $ARGV[0]){
	local $/ = undef;
	open(IN,"< $ARGV[0]") or die $!;
	flock(IN,1);
	$ART_INFOS = &JSON::XS::decode_json(<IN>);
	close(IN);
}


my $bp3d_objs = &renderer::new_bp3d_objs();
sub load_art_file {
#	my $dbh = &get_dbh();

#	my @FILES;

	my $art_id;
	my $art_ext;
	my $art_data;
	my $art_data_size;
	my $art_timestamp;
	my $hist_serial;
	my $sql;

	if(defined $ART_INFOS && ref $ART_INFOS eq 'ARRAY' && scalar @$ART_INFOS > 0){
		my @ART_IDS = map { $_->{'art_id'} } @$ART_INFOS;
		my $sql_fmt=<<SQL;
select
 art_id,
 art_ext,
-- art_data,
 art_data_size,
 EXTRACT(EPOCH FROM art_timestamp),
 hist_serial
from
 history_art_file
where
 art_id in ('%s')
order by
 hist_timestamp desc
SQL
		$sql = sprintf($sql_fmt,join("','",@ART_IDS));

	}else{
		$sql=<<SQL;
select
 art_id,
 art_ext,
-- art_data,
 art_data_size,
 EXTRACT(EPOCH FROM art_timestamp),
 hist_serial
from
 history_art_file
order by
 hist_timestamp desc
SQL
	}
#	&cgi_lib::common::message($sql);
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
#	say __LINE__,":\$sth->rows()=[",$sth->rows(),"]";
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$art_id, undef);
	$sth->bind_col(++$column_number, \$art_ext, undef);
#	$sth->bind_col(++$column_number, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
	$sth->bind_col(++$column_number, \$art_data_size, undef);
	$sth->bind_col(++$column_number, \$art_timestamp, undef);
	$sth->bind_col(++$column_number, \$hist_serial, undef);
	while($sth->fetch){
		next unless(defined $art_id && defined $art_data_size && defined $art_timestamp && defined $hist_serial);
#		my $objfile = sprintf($art_file_fmt,$art_id,$hist_serial,$art_ext);
		my $objfile = sprintf($art_file_fmt,$art_id,$art_ext);
		my $size = -s $objfile;
		my $mtime = 0;
		$mtime = (stat($objfile))[9] if(-e $objfile);
		unless(-e $objfile && $size == $art_data_size && $mtime>=$art_timestamp){
			&BITS::ArtFile::load_art_file_fromDB(dbh=>$dbh,art_id=>$art_id,hist_serial=>$hist_serial,art_file_fmt=>$art_file_fmt);
		}
		$bp3d_objs->objReader($objfile,1.0) if(-e $objfile);
	}
	$sth->finish;
	undef $sth;
}
#warn __LINE__,"\n";
&load_art_file();

sub tName2Type {
	my $t_key = shift;
	my $t_type;
	if($t_key eq 'bp3d'){
		$t_type = 1;
	}elsif($t_key eq 'isa'){
		$t_type = 3;
	}elsif($t_key eq 'partof'){
		$t_type = 4;
	}
	return $t_type;
}

my $DEF_HEIGHT = 1800;
sub getZoomYRange {
	my $zoom = shift;
	return &List::Util::max(1,&Math::Round::round( exp(1) ** ((log($DEF_HEIGHT)/log(2)-$zoom) * log(2)) ));
}
sub getYRangeZoom {
	my $yrange = shift;
	return &Math::Round::round((log($DEF_HEIGHT)/log(2) - log($yrange)/log(2)) * 10) / 10;
}

#my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,qr/\.[^\.]+$/);


#my $version = qq|3.0|;
#my $tree = qq|bp3d|;
my $copyrightL = qq|$FindBin::Bin/img/copyrightM.png|;
my $copyrightS = qq|$FindBin::Bin/img/copyrightS.png|;


my $sql;
if(defined $ART_INFOS && ref $ART_INFOS eq 'ARRAY' && scalar @$ART_INFOS > 0){
	my @ART_IDS = map { $_->{'art_id'} } @$ART_INFOS;
	my $sql_fmt=qq|select distinct art_id,art_ext,hist_serial,art_serial,EXTRACT(EPOCH FROM art_timestamp) from history_art_file where art_id in ('%s') order by art_serial desc,hist_serial desc|;
	$sql = sprintf($sql_fmt,join("','",@ART_IDS));
}else{
	$sql = qq|select distinct art_id,art_ext,hist_serial,art_serial,EXTRACT(EPOCH FROM art_timestamp) from history_art_file order by art_serial desc,hist_serial desc|;
}
#&cgi_lib::common::message($sql);
my $sth_history_art_file = $dbh->prepare($sql) or die $dbh->errstr;

my $obj2image = &renderer::new_obj2image($bp3d_objs,1);
my $FOCUS_COLOR;
my $COLOR;
my $DEF_TIMESTAMP;
if(USE_BP3D_COLOR){
#	push(@$FOCUS_COLOR,(1.0,0.3176470588235294,0.0));
	($COLOR,$FOCUS_COLOR,$DEF_TIMESTAMP) = &BITS::ArtFile::get_def_colors(dbh=>$dbh);
}
if(defined $FOCUS_COLOR){
	$obj2image->setFocusColor($FOCUS_COLOR);
}else{
	$obj2image->resetFocusColor();
}
if(defined $COLOR){
	$obj2image->setColor($COLOR);
}else{
	$obj2image->resetColor();
}

my $obj_files1;
my $art_id;
my $art_ext;
my $art_hist_serial;
my $art_timestamp;
$sth_history_art_file->execute() or die $dbh->errstr;
my $column_number = 0;
$sth_history_art_file->bind_col(++$column_number, \$art_id, undef);
$sth_history_art_file->bind_col(++$column_number, \$art_ext, undef);
$sth_history_art_file->bind_col(++$column_number, \$art_hist_serial, undef);
$sth_history_art_file->bind_col(++$column_number, \$art_timestamp, undef);
while($sth_history_art_file->fetch){
	next unless(defined $art_id && defined $art_ext && defined $art_hist_serial);
#	my $objfile = sprintf($art_file_fmt,$art_id,$art_hist_serial,$art_ext);
	my $objfile = sprintf($art_file_fmt,$art_id,$art_ext);
	unless(-e $objfile && -s $objfile){
#		&cgi_lib::common::message($objfile);
		next;
	}
	push(@$obj_files1,{
		path => $objfile,
		art_id => $art_id,
		art_hist_serial => $art_hist_serial,
		timestamp => $art_timestamp
	});
}
$sth_history_art_file->finish;
undef $sth_history_art_file;

#&cgi_lib::common::message(&cgi_lib::common::encodeJSON($obj_files1,1));
#exit 1;

sub make_image {
	my $obj_file = shift;
	my $mr_version = shift;

	&cgi_lib::common::message(&cgi_lib::common::encodeJSON($obj_file,1));
	&cgi_lib::common::message($mr_version) if(defined $mr_version);

	my $obj_path;
	my $obj_timestamp;
	my $obj_delcause;
	if(ref $obj_file eq 'HASH'){
		$obj_path = $obj_file->{'path'};
		$obj_timestamp = $obj_file->{'timestamp'};
		$obj_delcause = $obj_file->{'delcause'};
	}else{
		$obj_path = $obj_file;
	}

	my($obj_name,$obj_dir,$obj_ext) = &File::Basename::fileparse($obj_path,".obj");

#	print __LINE__,":\$mr_version=[",$mr_version,"]\n";
	my($img_prefix,$img_path) = &getObjImagePrefix($obj_name,$mr_version);

	umask(0);
	&File::Path::make_path($img_path,{verbose => 0, mode => 0777}) unless(-e $img_path);

	my $txt_file = qq|$img_prefix.txt|;
	my $gif_file = qq|$img_prefix.gif|;
	$txt_file_lock = qq|$txt_file.lock|;
	&cgi_lib::common::message("\$txt_file=[$txt_file][".(-e $txt_file ? (-s $txt_file) : 0)."]") if(defined $txt_file);

#	unless(&File::Path::make_path($txt_file_lock,{verbose => 0, mode => 0777})){
	unless(mkdir($txt_file_lock,0777)){
		$txt_file_lock = undef;
		return;
	}


	my $file_info = &getImageFileList($img_prefix);

	my $sizeL = $file_info->{'sizeL'};
	my $sizeM = $file_info->{'sizeM'};
	my $sizeS = $file_info->{'sizeS'};
	my $sizeXS = $file_info->{'sizeXS'};

	my $sizeStrL = $file_info->{'sizeStrL'};
	my $sizeStrM = $file_info->{'sizeStrM'};
	my $sizeStrS = $file_info->{'sizeStrS'};
	my $sizeStrXS = $file_info->{'sizeStrXS'};

	my $gif_prefix_fmt = $file_info->{'gif_prefix_fmt'};
	my $gif_fmt = $file_info->{'gif_fmt'};

	my $png_prefix_fmt = $file_info->{'png_prefix_fmt'};
	my $png_fmt = $file_info->{'png_fmt'};

	my $imgsL = $file_info->{'imgsL'};
	my $imgsM = $file_info->{'imgsM'};
	my $imgsS = $file_info->{'imgsS'};
	my $imgsXS = $file_info->{'imgsXS'};

	my @chk_files;
	push(@chk_files,$txt_file);
	push(@chk_files,$gif_file);
	push(@chk_files,@$imgsL);
	push(@chk_files,@$imgsM);
	push(@chk_files,@$imgsS);
	push(@chk_files,@$imgsXS);

	if(defined $obj_delcause){
		foreach my $chk_file (@chk_files){
			unlink $chk_file;
		}
		&File::Path::remove_tree($txt_file_lock) if(defined $txt_file_lock && -e $txt_file_lock && -d $txt_file_lock);
		$txt_file_lock = undef;
		return;
	}

	my $chk;
	foreach my $chk_file (@chk_files){
		if(defined $obj_timestamp){
			my $chk_mtime = -e $chk_file ? (stat($chk_file))[9] : 0;
			if(-e $chk_file && -s $chk_file && $chk_mtime>=floor($obj_timestamp)){
				utime $obj_timestamp,$obj_timestamp,$chk_file if($chk_mtime>floor($obj_timestamp));
				next;
			}
		}else{
			next if(-e $chk_file && -s $chk_file);
		}
		$chk = 1;
		last;
	}
	unless(defined $chk){
		&File::Path::remove_tree($txt_file_lock) if(defined $txt_file_lock && -e $txt_file_lock && -d $txt_file_lock);
		$txt_file_lock = undef;
		return;
	}

	if(open(OUT,"> $txt_file")){
		if(flock(OUT, 6)){

			foreach my $chk_file (@chk_files){
				next unless(-e $chk_file);
				unlink $chk_file if(-e $chk_file && $chk_file ne $txt_file);
			}

			my $largerbbox = [];
			my $b1 = $obj2image->bound([$obj_file]);
			$_+=0 for(@$b1);

			&cgi_lib::common::message("\$obj_path=$obj_path");
			&cgi_lib::common::message('$b1='.&cgi_lib::common::encodeJSON($b1,1));
			my $error_cnt = 0;
			for(@$b1){
				$error_cnt++ if($_==1 || $_==-1);
			}
			if($error_cnt == scalar @$b1){
				close(OUT);
				foreach my $chk_file (@chk_files){
					next unless(-e $chk_file);
					unlink $chk_file if(-e $chk_file);
				}
				return 1;
			}

			for(my $i=0;$i<scalar @$b1;$i++){
				$largerbbox->[$i] = $b1->[$i] unless(defined $largerbbox->[$i]);
			}
			&cgi_lib::common::message('$largerbbox='.&cgi_lib::common::encodeJSON($largerbbox,1));

#			my $fmax = &List::Util::max(abs($largerbbox->[0]-$largerbbox->[1]),abs($largerbbox->[2]-$largerbbox->[3]),abs($largerbbox->[4]-$largerbbox->[5]));
			my @largerranges = (abs($largerbbox->[0]-$largerbbox->[1]),abs($largerbbox->[2]-$largerbbox->[3]),abs($largerbbox->[4]-$largerbbox->[5]));
#			push(@largerranges, ($largerranges[0]*$largerranges[0]+$largerranges[1]*$largerranges[1])**0.5);
#			push(@largerranges, ($largerranges[0]*$largerranges[0]+$largerranges[2]*$largerranges[2])**0.5);
#			push(@largerranges, ($largerranges[1]*$largerranges[1]+$largerranges[2]*$largerranges[2])**0.5);
			my $fmax = &List::Util::max(@largerranges);
			my $fzoom = &getYRangeZoom($fmax);
			my $fzoom1 = ($fzoom>0) ? $fzoom-0.1 : $fzoom;
			my $largerbboxYRange = &getZoomYRange($fzoom1);
#			my $largerbboxYRange = &getZoomYRange($fzoom);

			&cgi_lib::common::message("\$largerbboxYRange=[$fmax][$fzoom][$fzoom1][$largerbboxYRange]");

#			my $b1max = &List::Util::max(abs($b1->[0]-$b1->[1]),abs($b1->[2]-$b1->[3]),abs($b1->[4]-$b1->[5]));
			my @b1ranges = (abs($b1->[0]-$b1->[1]),abs($b1->[2]-$b1->[3]),abs($b1->[4]-$b1->[5]));
#			push(@b1ranges, ($b1ranges[0]*$b1ranges[0]+$b1ranges[1]+$b1ranges[1])**0.5);
#			push(@b1ranges, ($b1ranges[0]*$b1ranges[0]+$b1ranges[2]+$b1ranges[2])**0.5);
#			push(@b1ranges, ($b1ranges[1]*$b1ranges[1]+$b1ranges[2]+$b1ranges[2])**0.5);
			my $b1max = &List::Util::max(@b1ranges);

			my $b1zoom = &getYRangeZoom($b1max);

			my $b1zoom1 = ($b1zoom>0) ? $b1zoom-0.1 : $b1zoom;
			my $b1YRange = &getZoomYRange($b1zoom1);
#			my $b1YRange = &getZoomYRange($b1zoom);
			&cgi_lib::common::message("\$b1YRange=[$b1max][$b1zoom][$b1zoom1],$b1YRange]");

			undef $inter_files if(defined $inter_files);
			undef $tmp_base_path if(defined $tmp_base_path);
			undef $tmp_img_prefix if(defined $tmp_img_prefix);


			push(@$inter_files,$txt_file);

			my $bb;




			push(@$inter_files,@$imgsL);

			my $dest_prefix = sprintf($gif_prefix_fmt,$img_prefix,$sizeStrL);

			$tmp_base_path = &BITS::ImageC::get_tmppath(sprintf($lock_filefmt,$lock_no));
			&cgi_lib::common::message("\$tmp_base_path=[$tmp_base_path]");
			&File::Path::make_path($tmp_base_path,{verbose => 0, mode => 0777}) unless(-e $tmp_base_path);
			$tmp_img_prefix = &catdir($tmp_base_path,$obj_name);
			&cgi_lib::common::message("\$tmp_img_prefix=[$tmp_img_prefix]");
			my $tmp_dest_prefix = sprintf($gif_prefix_fmt,$tmp_img_prefix,$sizeStrL);


			$bb = $obj2image->obj2animgif($sizeL,[$obj_file],undef,$tmp_dest_prefix,$b1YRange,undef,undef) unless(-e $imgsL->[0]);

			my @PNG_FILES = ();

			my $target_png_fmt = qq|$tmp_dest_prefix\-%d-target.png|;
			my $angle_png_fmt  = qq|$tmp_dest_prefix\-%d.png|;

			for(my $i=0;$i<360;$i+=5){
				my $target_png_file = sprintf($target_png_fmt,$i);
				my $png_file = sprintf($angle_png_fmt,$i);
				my($bits,$type,$colorcount) = &BITS::ImageC::color_reduction(in_file=>$target_png_file,out_file=>$png_file);
				while(-e $png_file && -s $png_file && (!defined $colorcount || $colorcount > 256)){
					($bits,$type,$colorcount) = &BITS::ImageC::color_reduction(in_file=>$png_file);
				}
				unlink $target_png_file if(-e $target_png_file);

				if(-e $png_file && -s $png_file){
					push(@PNG_FILES,$png_file);
				}else{
					die __LINE__,":Unknown file [$png_file]\n";
				}
			}

			my $gif_file = qq|$dest_prefix.gif|;
			&BITS::ImageC::animatedGIF(in_files=>\@PNG_FILES,out_file=>$gif_file) unless(-e $gif_file && -s $gif_file);
			utime $obj_timestamp,$obj_timestamp,$gif_file if(defined $obj_timestamp && -e $gif_file && -s $gif_file);

#exit;
			my $angle = 0;
			my $png_file;
			for(my $i=1;$i<=4;$i++){
				unless(-e $imgsL->[$i]){
					$png_file = sprintf($angle_png_fmt,$angle);
					die __LINE__,":Unknown file [$png_file]\n" unless(-e $png_file);
					&File::Copy::copy($png_file,$imgsL->[$i]) if(-e $png_file);
					utime $obj_timestamp,$obj_timestamp,$imgsL->[$i] if(defined $obj_timestamp && -e $imgsL->[$i] && -s $imgsL->[$i]);
				}
				$angle += 90;
			}

#exit;

			push(@$inter_files,@$imgsM);


			$dest_prefix = sprintf($gif_prefix_fmt,$img_prefix,$sizeStrM);
			unless(-e $imgsM->[0]){
				&BITS::ImageC::resize(in_file=>$imgsL->[0],geometry=>$sizeStrM,out_file=>$imgsM->[0]) if(-e $imgsL->[0]);
				utime $obj_timestamp,$obj_timestamp,$imgsM->[0] if(defined $obj_timestamp && -e $imgsM->[0] && -s $imgsM->[0]);
			}
			unlink qq|$img_prefix.gif| if(-e qq|$img_prefix.gif|);
			symlink qq|$obj_name\_$sizeStrM.gif|,qq|$img_prefix.gif| if(-e $imgsM->[0]);
			push(@$inter_files,qq|$img_prefix.gif|);

			$angle = 0;
			for(my $i=1;$i<=4;$i++){
				unless(-e $imgsM->[$i]){
					if(-e $imgsL->[$i]){
						&BITS::ImageC::resize(in_file=>$imgsL->[$i],geometry=>$sizeStrM,out_file=>$imgsM->[$i]);
						utime $obj_timestamp,$obj_timestamp,$imgsM->[$i] if(defined $obj_timestamp && -e $imgsM->[$i] && -s $imgsM->[$i]);
					}else{
						$png_file = sprintf($angle_png_fmt,$angle);
						die __LINE__,":Unknown file [$png_file]\n" unless(-e $png_file);
						&BITS::ImageC::resize(in_file=>$png_file,geometry=>$sizeStrM,out_file=>$imgsM->[$i]);
						utime $obj_timestamp,$obj_timestamp,$imgsM->[$i] if(defined $obj_timestamp && -e $imgsM->[$i] && -s $imgsM->[$i]);
					}
				}
				$angle += 90;
			}


			push(@$inter_files,@$imgsS);

			$dest_prefix = sprintf($gif_prefix_fmt,$img_prefix,$sizeStrS);

			unless(-e $imgsS->[0]){
				&BITS::ImageC::resize(in_file=>$imgsL->[0],geometry=>$sizeStrS,out_file=>$imgsS->[0]) if(-e $imgsL->[0]);
				utime $obj_timestamp,$obj_timestamp,$imgsS->[0] if(defined $obj_timestamp && -e $imgsS->[0] && -s $imgsS->[0]);
			}

			$angle = 0;
			for(my $i=1;$i<=4;$i++){
				unless(-e $imgsS->[$i]){
					if(-e $imgsL->[$i]){
						&BITS::ImageC::resize(in_file=>$imgsL->[$i],geometry=>$sizeStrS,out_file=>$imgsS->[$i]);
						utime $obj_timestamp,$obj_timestamp,$imgsS->[$i] if(defined $obj_timestamp && -e $imgsS->[$i] && -s $imgsS->[$i]);
					}else{
						$png_file = sprintf($angle_png_fmt,$angle);
						die __LINE__,":Unknown file [$png_file]\n" unless(-e $png_file);
						&BITS::ImageC::resize(in_file=>$png_file,geometry=>$sizeStrS,out_file=>$imgsS->[$i]);
						utime $obj_timestamp,$obj_timestamp,$imgsS->[$i] if(defined $obj_timestamp && -e $imgsS->[$i] && -s $imgsS->[$i]);
					}
				}
				$angle += 90;
			}

			push(@$inter_files,@$imgsXS);


			$dest_prefix = sprintf($gif_prefix_fmt,$img_prefix,$sizeStrXS);

			unless(-e $imgsXS->[0]){
				&BITS::ImageC::resize(in_file=>$imgsL->[0],geometry=>$sizeStrXS,out_file=>$imgsXS->[0]) if(-e $imgsL->[0]);
				utime $obj_timestamp,$obj_timestamp,$imgsXS->[0] if(defined $obj_timestamp && -e $imgsXS->[0] && -s $imgsXS->[0]);
			}

			$angle = 0;
			for(my $i=1;$i<=4;$i++){
				unless(-e $imgsXS->[$i]){
					if(-e $imgsL->[$i]){
						&BITS::ImageC::resize(in_file=>$imgsL->[$i],geometry=>$sizeStrXS,out_file=>$imgsXS->[$i]);
						utime $obj_timestamp,$obj_timestamp,$imgsXS->[$i] if(defined $obj_timestamp && -e $imgsXS->[$i] && -s $imgsXS->[$i]);
					}else{
						$png_file = sprintf($angle_png_fmt,$angle);
						die __LINE__,":Unknown file [$png_file]\n" unless(-e $png_file);
						&BITS::ImageC::resize(in_file=>$png_file,geometry=>$sizeStrXS,out_file=>$imgsXS->[$i]);
						utime $obj_timestamp,$obj_timestamp,$imgsXS->[$i] if(defined $obj_timestamp && -e $imgsXS->[$i] && -s $imgsXS->[$i]);
					}
				}
				$angle += 90;
			}
			for($angle=0;$angle<360;$angle+=5){
				$png_file = sprintf($angle_png_fmt,$angle);
				unlink $png_file if(-e $png_file);
			}

			if(defined $b1){
				my $b = {
					xmin => $b1->[0]+0,
					xmax => $b1->[1]+0,
					ymin => $b1->[2]+0,
					ymax => $b1->[3]+0,
					zmin => $b1->[4]+0,
					zmax => $b1->[5]+0
				};
				print OUT &JSON::XS::encode_json($b);
			}

			undef $largerbbox if(defined $largerbbox);

			&File::Path::remove_tree($tmp_base_path) if(defined $tmp_base_path && -e $tmp_base_path);
			undef $tmp_base_path if(defined $tmp_base_path);
			undef $tmp_img_prefix if(defined $tmp_img_prefix);

		}
		close(OUT);
		utime $obj_timestamp,$obj_timestamp,$txt_file if(defined $obj_timestamp && -e $txt_file && -s $txt_file);

	}
	undef $inter_files if(defined $inter_files);
	&File::Path::remove_tree($txt_file_lock) if(defined $txt_file_lock && -e $txt_file_lock && -d $txt_file_lock);
	$txt_file_lock = undef;
}

if(defined $obj_files1 && ref $obj_files1 eq 'ARRAY'){

#	&cgi_lib::common::message([sort { $a->{'art_id'} cmp $b->{'art_id'} } @$obj_files1]);
#	exit;

	my $sql = qq|
select
 cdi_name,
 mr_version,
 EXTRACT(EPOCH FROM GREATEST(cm.cm_entry,cm.art_timestamp,cd.cd_entry,cs.seg_entry)),
 COALESCE(cs_color.seg_thum_fgcolor,cs_null.seg_thum_fgcolor) as seg_thum_fgcolor,
 cs.seg_id
from
 view_concept_art_map as cm
left join (
 select * from model_revision
) as mr on
  mr.md_id=cm.md_id and
  mr.mv_id=cm.mv_id and
  mr.mr_id=cm.mr_id
left join (
 select * from model_version
) as mv on
  mv.md_id=cm.md_id and
  mv.mv_id=cm.mv_id

left join (
 select * from concept_data
) as cd on
  cd.ci_id=cm.ci_id and
  cd.cb_id=cm.cb_id and
  cd.cdi_id=cm.cdi_id

left join (
 select seg_id,seg_entry from concept_segment
) as cs on
  cs.seg_id=cd.seg_id

left join (select seg_id,seg_thum_fgcolor from concept_segment where seg_delcause is null) as cs_color on cs_color.seg_id = cd.seg_id
left join (select seg_id,seg_thum_fgcolor from concept_segment) as cs_null on cs_null.seg_id = 0

where
 cm_use and cm_delcause is null and
 mr_use and mr_delcause is null and
-- mv_use and mv_frozen and mv_delcause is null and mv_publish and
 mv_use and mv_delcause is null and
 art_id=? and art_hist_serial=?
order by
 mr_version desc
|;
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;

	my $DEF_COLOR;
	my $DEF_COLOR_ART;
	my $DEF_TIMESTAMP_ART;

	foreach my $o (@$obj_files1){
		next unless(defined $o && ref $o eq 'HASH');
		my $art_id = $o->{'art_id'};
#		next if($art_id ne 'FJ6459');
#		next if($art_id ne 'FJ6479');
#		next if($art_id ne 'MM1171');
		my $art_hist_serial = $o->{'art_hist_serial'};
		if(USE_BP3D_COLOR){
			$sth->execute($art_id,$art_hist_serial) or die $dbh->errstr;
			if($sth->rows()>0){
				my $cdi_name;
				my $mr_version;
				my $timestamp;
				my $color;
				my $seg_id;
				my $column_number = 0;
				$sth->bind_col(++$column_number, \$cdi_name, undef);
				$sth->bind_col(++$column_number, \$mr_version, undef);
				$sth->bind_col(++$column_number, \$timestamp, undef);
				$sth->bind_col(++$column_number, \$color, undef);
				$sth->bind_col(++$column_number, \$seg_id, undef);
				while($sth->fetch){
#					next if($mr_version ne '4.3.1403311232');
=pod
					unless(exists($DEF_COLOR->{$mr_version})){
						my $bp3d_color_file = qq|/bp3d/ag-test/htdocs/data/$mr_version/bp3d.color|;
						$bp3d_color_file = qq|/bp3d/ag-test/htdocs/data/bp3d.color| unless(-e $bp3d_color_file);
						if(-e $bp3d_color_file){
							open(IN,"< $bp3d_color_file");
							while(<IN>){
								s/\s*$//g;
								s/^\s*//g;
								next if(/^#/);
								my($cdi_name,$color) = split(/\t/);
								next if($cdi_name eq "" || $color eq "");
								next if(exists($DEF_COLOR->{$mr_version}->{$cdi_name}));
								$color =~ s/^#//g;
								push(@{$DEF_COLOR->{$mr_version}->{$cdi_name}},hex(uc(substr($color,0,2)))/255);
								push(@{$DEF_COLOR->{$mr_version}->{$cdi_name}},hex(uc(substr($color,2,2)))/255);
								push(@{$DEF_COLOR->{$mr_version}->{$cdi_name}},hex(uc(substr($color,4,2)))/255);
							}
							close(IN);
						}
					}
					if(defined $DEF_COLOR && exists $DEF_COLOR->{$mr_version} && exists $DEF_COLOR->{$mr_version}->{$cdi_name}){
						push(@{$DEF_COLOR_ART->{$art_id}->{$art_hist_serial}->{$mr_version}},@{$DEF_COLOR->{$mr_version}->{$cdi_name}}) unless(exists $DEF_COLOR_ART->{$art_id} && exists $DEF_COLOR_ART->{$art_id}->{$art_hist_serial} && exists $DEF_COLOR_ART->{$art_id}->{$art_hist_serial}->{$mr_version} && defined $DEF_COLOR_ART->{$art_id}->{$art_hist_serial}->{$mr_version});
					}else{
						$DEF_COLOR_ART->{$art_id}->{$art_hist_serial}->{$mr_version} = undef;
					}
=cut
					if(defined $color && defined $seg_id && $seg_id>0){
						$color =~ s/^#//g;
						push(@{$DEF_COLOR_ART->{$art_id}->{$art_hist_serial}->{$mr_version}},hex(uc(substr($color,0,2)))/255);
						push(@{$DEF_COLOR_ART->{$art_id}->{$art_hist_serial}->{$mr_version}},hex(uc(substr($color,2,2)))/255);
						push(@{$DEF_COLOR_ART->{$art_id}->{$art_hist_serial}->{$mr_version}},hex(uc(substr($color,4,2)))/255);
					}else{
						$DEF_COLOR_ART->{$art_id}->{$art_hist_serial}->{$mr_version} = undef;
					}
					$DEF_TIMESTAMP_ART->{$art_id}->{$art_hist_serial}->{$mr_version} = $timestamp;
				}
			}
			$sth->finish;
		}
		$o->{'color'} = undef;
#		$o->{'timestamp'} = undef;
		if(defined $o->{'timestamp'} && defined $DEF_TIMESTAMP && $o->{'timestamp'} < $DEF_TIMESTAMP){
			$o->{'timestamp'} = $DEF_TIMESTAMP;
		}elsif(!defined $o->{'timestamp'} && defined $DEF_TIMESTAMP){
			$o->{'timestamp'} = $DEF_TIMESTAMP;
		}

#		&make_image($o);
		if(USE_BP3D_COLOR){
			if(defined $DEF_COLOR_ART && exists $DEF_COLOR_ART->{$art_id} && exists $DEF_COLOR_ART->{$art_id}->{$art_hist_serial} && ref $DEF_COLOR_ART->{$art_id}->{$art_hist_serial} eq 'HASH'){
				&make_image($o);
				foreach my $mr_version (sort {$b cmp $a} keys(%{$DEF_COLOR_ART->{$art_id}->{$art_hist_serial}})){
					if(defined $DEF_COLOR_ART->{$art_id}->{$art_hist_serial}->{$mr_version}){
						$o->{'color'} = $DEF_COLOR_ART->{$art_id}->{$art_hist_serial}->{$mr_version};
					}else{
						$o->{'delcause'} = 1;
					}
					$o->{'timestamp'} = $DEF_TIMESTAMP_ART->{$art_id}->{$art_hist_serial}->{$mr_version};
					&make_image($o,$mr_version);
				}
#			}else{
##				exit unless(&make_image($o));
#				exit if(&make_image($o));
			}
		}else{
			&make_image($o);
		}
	}
	undef $sth;
	undef $obj_files1;
}
undef $obj2image;


exit;
