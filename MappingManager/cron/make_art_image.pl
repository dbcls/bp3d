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
use Parallel::ForkManager;
use Sys::CPU;

use FindBin;
my $htdocs_path;
my $common_path;
BEGIN{
	use FindBin;
#	$htdocs_path = qq|$FindBin::Bin/../htdocs_130910|;
	$htdocs_path = qq|$FindBin::Bin/../htdocs| unless(defined $htdocs_path && -e $htdocs_path);

	$common_path = qq|/bp3d/ag-common/lib|;

	die "$! [$FindBin::Bin]" unless(chdir($FindBin::Bin));
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
	obj|o=s@
	force|f
/) or exit 1;

$ENV{'AG_DB_HOST'} = $config->{'host'};
$ENV{'AG_DB_PORT'} = $config->{'port'};


use BITS::ArtFile;
use BITS::ImageC;
require "webgl_common.pl";
use cgi_lib::common;

&cgi_lib::common::message(\%ENV);

use renderer;
use obj2deci;

use constant {
	DEF_SERVER_NUMBRT => 98,
	MAX_PROG => 14,

	TMPFS => '/dev/shm',

	USE_BP3D_COLOR => 1,
	DEBUG_USE_BP3D_COLOR => 0,


#	USE_IMAGE_SIZES => [[640,640],[120,120],[40,40],[16,16]],
	USE_IMAGE_SIZES => [undef,[120,120],undef,[16,16]],

#	USE_MAX_AZIMUTH => 72,
#	USE_MAX_AZIMUTH => 36,
#	USE_MAX_AZIMUTH => 24,
	USE_MAX_AZIMUTH => 12,
#	USE_MAX_AZIMUTH => 8,

#	USE_ANIMATED_GIF_DELAY => 0,
	USE_ANIMATED_GIF_DELAY => 30,

};



my $dbh = &get_dbh();

#my $lib_path;
my $xvfb_lock;
my $display_size;
my $txt_file_lock;

my $inter_files;
my $tmp_base_path;
my $tmp_img_prefix;

my $OUT;
sub sigexit {
	say __LINE__.":INT!!" . (defined $txt_file_lock ? "[$txt_file_lock]" : '');
	say __LINE__.":$@";
	eval{close($OUT) if(defined $OUT);};
	if(defined $inter_files && ref $inter_files eq 'ARRAY'){
		foreach my $file (@$inter_files){
			unlink $file if(-e $file);
		}
	}
	&File::Path::remove_tree($tmp_base_path) if(defined $tmp_base_path && -e $tmp_base_path && -d $tmp_base_path);
	&File::Path::remove_tree($txt_file_lock) if(defined $txt_file_lock && -e $txt_file_lock && -d $txt_file_lock);
#	rmdir($txt_file_lock) if(defined $txt_file_lock);
	exit;
}

my $LOCK;
my $is_child;
my $old_umask;
BEGIN{
	$old_umask = umask(0);
	print __LINE__,":BEGIN!!1\n";
	$SIG{'HUP'} = $SIG{'INT'} = $SIG{'QUIT'} = $SIG{'ILL'} = $SIG{'TRAP'} = $SIG{'ABRT'} = $SIG{'BUS'} = $SIG{'FPE'} = $SIG{'KILL'} = $SIG{'USR1'} = $SIG{'SEGV'} = $SIG{'USR2'} = $SIG{'TERM'} = "sigexit";
}
END{
	unless(defined $is_child){
		umask($old_umask);
		close($LOCK) if(defined $LOCK);
		&File::Path::remove_tree($tmp_base_path) if(defined $tmp_base_path && -e $tmp_base_path && -d $tmp_base_path);
		print __LINE__.":IS PARENT END!!\n";
	}elsif($is_child==$$){
		&File::Path::remove_tree($txt_file_lock) if(defined $txt_file_lock && -e $txt_file_lock && -d $txt_file_lock);
		print __LINE__.":IS CHILD END!![$$]\n";
	}else{
#		print __LINE__.":IS CHILD CHILD END!![$$]\n";
	}
	print __LINE__,":END!!\n";
}

#use lib $lib_path;
#use BITS::Config;
#use BITS::DB;


#use Inline Python;

my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,qr/\.[^\.]+$/);

#my $lock_dirpath = &catdir($FindBin::Bin,'logs');
my $lock_dirpath = &catdir(TMPFS,$cgi_name);
unless(-e $lock_dirpath){
#	my $m = umask(0);
	&File::Path::make_path($lock_dirpath,{verbose => 0, mode => 0777});
#	umask($m);
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
#	my $m = umask(0);
	&File::Path::make_path($art_file_prefix,{verbose => 0, mode => 0777});
#	umask($m);
}
#my $art_file_fmt = qq|$art_file_prefix/%s-%d%s|;
my $art_file_fmt = &catdir($art_file_prefix,'%s%s');

my $ART_INFOS;
if(defined $ARGV[0] && -e $ARGV[0]){
	local $/ = undef;
	open(IN,"< $ARGV[0]") or die $!;
	flock(IN,1);
	$ART_INFOS = &cgi_lib::common::decodeJSON(<IN>);
	close(IN);
}

if(exists $config->{'obj'} && defined $config->{'obj'} && ref $config->{'obj'} eq 'ARRAY'){
	foreach my $obj (@{$config->{'obj'}}){
		my @art_ids = split(/[^A-Za-z0-9]+/,$obj);
		foreach my $art_id (@art_ids){
			push(@$ART_INFOS,{art_id=>$art_id});
		}
	}
}

#&cgi_lib::common::message(&cgi_lib::common::encodeJSON($config,1));
#&cgi_lib::common::message(&cgi_lib::common::encodeJSON($ART_INFOS,1));
#exit;

my $bp3d_objs = &renderer::new_bp3d_objs();
sub load_art_file {
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
 art_data_size,
 EXTRACT(EPOCH FROM art_timestamp)
from
 art_file_info
where
 art_id in ('%s')
order by
 prefix_id desc,
 art_serial desc
SQL
		$sql = sprintf($sql_fmt,join("','",@ART_IDS));

	}else{
		$sql=<<SQL;
select
 art_id,
 art_ext,
 art_data_size,
 EXTRACT(EPOCH FROM art_timestamp)
from
 art_file_info
order by
 prefix_id desc,
 art_serial desc
SQL
	}

	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	&cgi_lib::common::message("\$sth->rows()=[".$sth->rows()."]");
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$art_id, undef);
	$sth->bind_col(++$column_number, \$art_ext, undef);
	$sth->bind_col(++$column_number, \$art_data_size, undef);
	$sth->bind_col(++$column_number, \$art_timestamp, undef);
	while($sth->fetch){
		next unless(defined $art_id && defined $art_data_size && defined $art_timestamp);
		my $objfile = sprintf($art_file_fmt,$art_id,$art_ext);
		my $size = -s $objfile;
		my $mtime = 0;
		$mtime = (stat($objfile))[9] if(-e $objfile);
		unless(-e $objfile && $size == $art_data_size && $mtime>=$art_timestamp){
			&BITS::ArtFile::load_art_file_fromDB(dbh=>$dbh,art_id=>$art_id,art_file_fmt=>$art_file_fmt);
		}
		$bp3d_objs->objReader($objfile,1.0) if(-e $objfile);
	}
	$sth->finish;
	undef $sth;
}
#warn __LINE__,"\n";
&load_art_file();
#warn __LINE__,"\n";

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
	my $sql_fmt=qq|select art_id,art_ext,EXTRACT(EPOCH FROM art_timestamp) from art_file where art_id in ('%s') order by art_serial desc,prefix_id desc|;
	$sql = sprintf($sql_fmt,join("','",@ART_IDS));
}else{
	$sql = qq|select art_id,art_ext,EXTRACT(EPOCH FROM art_timestamp) from art_file order by art_serial desc,prefix_id desc|;
}
#&cgi_lib::common::message($sql);
#exit;
my $sth_art_file_sel = $dbh->prepare($sql) or die $dbh->errstr;

#my $g_img_sizes = [[640,640],[120,120],[40,40],[16,16]];
my $g_img_sizes = &USE_IMAGE_SIZES();
my $g_animated_gif_delay = &USE_ANIMATED_GIF_DELAY();
my $g_max_azimuth = &USE_MAX_AZIMUTH();
my $g_file_info = &getImageFileList(undef,$g_img_sizes);
my $g_img_size;
my $g_img_sizeStr;
if(exists $g_file_info->{'sizeL'} && defined $g_file_info->{'sizeL'} && ref $g_file_info->{'sizeL'} eq 'ARRAY'){
	$g_img_size = $g_file_info->{'sizeL'};
	$g_img_sizeStr = $g_file_info->{'sizeStrL'};
}elsif(exists $g_file_info->{'sizeM'} && defined $g_file_info->{'sizeM'} && ref $g_file_info->{'sizeM'} eq 'ARRAY'){
	$g_img_size = $g_file_info->{'sizeM'};
	$g_img_sizeStr = $g_file_info->{'sizeStrM'};
}elsif(exists $g_file_info->{'sizeS'} && defined $g_file_info->{'sizeS'} && ref $g_file_info->{'sizeS'} eq 'ARRAY'){
	$g_img_size = $g_file_info->{'sizeS'};
	$g_img_sizeStr = $g_file_info->{'sizeStrS'};
}elsif(exists $g_file_info->{'sizeXS'} && defined $g_file_info->{'sizeXS'} && ref $g_file_info->{'sizeXS'} eq 'ARRAY'){
	$g_img_size = $g_file_info->{'sizeXS'};
	$g_img_sizeStr = $g_file_info->{'sizeStrXS'};
}

$g_max_azimuth -= 0 if(defined $g_max_azimuth);
if(defined $g_img_size && ref $g_img_size eq 'ARRAY'){
	$_ -= 0 for(@$g_img_size);
}
my $obj2image = &renderer::new_obj2image($bp3d_objs,1,$g_img_size,$g_max_azimuth);
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
undef $obj2image;
undef $bp3d_objs;

my $obj_files1;
my $art_id;
my $art_ext;
my $art_timestamp;
$sth_art_file_sel->execute() or die $dbh->errstr;
my $column_number = 0;
$sth_art_file_sel->bind_col(++$column_number, \$art_id, undef);
$sth_art_file_sel->bind_col(++$column_number, \$art_ext, undef);
$sth_art_file_sel->bind_col(++$column_number, \$art_timestamp, undef);
while($sth_art_file_sel->fetch){
	next unless(defined $art_id && defined $art_ext && defined $art_timestamp);
	my $objfile = sprintf($art_file_fmt,$art_id,$art_ext);
	next unless(-e $objfile && -s $objfile);
	push(@$obj_files1,{
		path => $objfile,
		art_id => $art_id,
		timestamp => $art_timestamp - 0
	});
}
$sth_art_file_sel->finish;
undef $sth_art_file_sel;

#&cgi_lib::common::message(&cgi_lib::common::encodeJSON($obj_files1,1));
#exit 1;

sub make_image {
	my $obj_file = shift;
	my $md_id = shift;
	my $mv_id = shift;

	&cgi_lib::common::message(&cgi_lib::common::encodeJSON($obj_file,1));
	&cgi_lib::common::message($md_id) if(defined $md_id);
	&cgi_lib::common::message($mv_id) if(defined $mv_id);

	my $obj_path;
	my $obj_timestamp;
	my $obj_delcause;
	if(ref $obj_file eq 'HASH'){
		$obj_path = $obj_file->{'path'};
		$obj_timestamp = $obj_file->{'timestamp'} - 0;
		$obj_delcause = $obj_file->{'delcause'};
	}else{
		$obj_path = $obj_file;
	}

	my($obj_name,$obj_dir,$obj_ext) = &File::Basename::fileparse($obj_path,".obj");

#	print __LINE__,":\$mr_version=[",$mr_version,"]\n";
	my($img_prefix,$img_path) = &getObjImagePrefix($obj_name,$md_id,$mv_id);
#	my $img_path_base = &File::Basename::dirname($img_path);
#	umask(0);
	&File::Path::make_path($img_path,{verbose => 0, mode => 0777}) unless(-e $img_path);
#	&File::Path::make_path($img_path_base,{verbose => 0, mode => 0777}) unless(-e $img_path_base);

	my $txt_file = qq|$img_prefix.txt|;
	my $gif_file = qq|$img_prefix.gif|;
	$txt_file_lock = qq|$img_path.lock|;
	&cgi_lib::common::message("\$txt_file=[$txt_file][".(-e $txt_file ? (-s $txt_file) : 0)."]") if(defined $txt_file);

#	unless(&File::Path::make_path($txt_file_lock,{verbose => 0, mode => 0777})){
	unless(mkdir($txt_file_lock,0777)){
		$txt_file_lock = undef;
		return;
	}


	my $file_info = &getImageFileList($img_prefix,$g_img_sizes);

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
	push(@chk_files,@$imgsL) if(defined $imgsL && ref $imgsL eq 'ARRAY');
	push(@chk_files,@$imgsM) if(defined $imgsM && ref $imgsM eq 'ARRAY');
	push(@chk_files,@$imgsS) if(defined $imgsS && ref $imgsS eq 'ARRAY');
	push(@chk_files,@$imgsXS) if(defined $imgsXS && ref $imgsXS eq 'ARRAY');

	my $imgsMAX;
	if(defined $imgsL && ref $imgsL eq 'ARRAY'){
		$imgsMAX = $imgsL;
	}elsif(defined $imgsM && ref $imgsM eq 'ARRAY'){
		$imgsMAX = $imgsM;
	}elsif(defined $imgsS && ref $imgsS eq 'ARRAY'){
		$imgsMAX = $imgsS;
	}elsif(defined $imgsXS && ref $imgsXS eq 'ARRAY'){
		$imgsMAX = $imgsXS;
	}

	if(defined $obj_delcause){
		foreach my $chk_file (@chk_files){
			unlink $chk_file if(-e $chk_file);
		}
		&File::Path::remove_tree($txt_file_lock) if(defined $txt_file_lock && -e $txt_file_lock && -d $txt_file_lock);
		$txt_file_lock = undef;
		return;
	}

	my $chk;
	foreach my $chk_file (@chk_files){
		if(exists $config->{'force'}){
			unlink $chk_file if(-e $chk_file && -s $chk_file);
		}
		if(defined $obj_timestamp){
			my $chk_mtime = -e $chk_file ? (stat($chk_file))[9] : 0;
			if(-e $chk_file && -s $chk_file && $chk_mtime>=&floor($obj_timestamp)){
				utime $obj_timestamp,$obj_timestamp,$chk_file if($chk_mtime>&floor($obj_timestamp));
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

#	my $OUT;
	if(open($OUT,"> $txt_file")){
		&cgi_lib::common::message('');
		if(flock($OUT, 6)){
			&cgi_lib::common::message('');

			foreach my $chk_file (@chk_files){
				next unless(-e $chk_file);
				unlink $chk_file if(-e $chk_file && $chk_file ne $txt_file);
			}

			my $bp3d_objs = &renderer::new_bp3d_objs();
			$bp3d_objs->objReader($obj_path,1.0) if(-e $obj_path);
			my $obj2image = &renderer::new_obj2image($bp3d_objs,1,$g_img_size,$g_max_azimuth);
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

			my $largerbbox = [];
#			my $b1 = $obj2image->bound([$obj_file]);
			my $b1;
			my $b1_volume;
			my $prop;
#			$prop = &obj2deci::getProperties([$obj_file]);
			if(defined $prop && ref $prop eq 'HASH' && exists $prop->{'bounds'} && defined $prop->{'bounds'} && ref $prop->{'bounds'} eq 'ARRAY' && scalar @{$prop->{'bounds'}} >= 6 && exists $prop->{'volume'} && defined $prop->{'volume'}){
				$b1 = $prop->{'bounds'};
				$b1_volume = $prop->{'volume'} - 0;
			}else{
				$b1 = $obj2image->bound([$obj_file]);
			}
			if(defined $b1 && ref $b1 eq 'ARRAY'){
				$_ -= 0 for(@$b1);
			}else{
				die __LINE__.":undefined \$bound!!\n";
			}

#			&cgi_lib::common::message("\$obj_path=$obj_path");
#			&cgi_lib::common::message('$b1='.&cgi_lib::common::encodeJSON($b1,1));
			my $error_cnt = 0;
			for(@$b1){
				$error_cnt++ if($_==1 || $_==-1);
			}
			if($error_cnt == scalar @$b1){
				close($OUT);
				foreach my $chk_file (@chk_files){
					next unless(-e $chk_file);
					unlink $chk_file if(-e $chk_file);
				}
				return 1;
			}

			for(my $i=0;$i<scalar @$b1;$i++){
				$largerbbox->[$i] = $b1->[$i] - 0 unless(defined $largerbbox->[$i]);
			}
#			&cgi_lib::common::message('$largerbbox='.&cgi_lib::common::encodeJSON($largerbbox,1));

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




			push(@$inter_files,@$imgsL) if(defined $imgsL && ref $imgsL eq 'ARRAY');

			my $dest_prefix;
			if(defined $sizeStrL){
				$dest_prefix = sprintf($gif_prefix_fmt,$img_prefix,$sizeStrL);
			}elsif(defined $sizeStrM){
				$dest_prefix = sprintf($gif_prefix_fmt,$img_prefix,$sizeStrM);
			}elsif(defined $sizeStrS){
				$dest_prefix = sprintf($gif_prefix_fmt,$img_prefix,$sizeStrS);
			}elsif(defined $sizeStrXS){
				$dest_prefix = sprintf($gif_prefix_fmt,$img_prefix,$sizeStrXS);
			}

			$tmp_base_path = &BITS::ImageC::get_tmppath(sprintf($lock_filefmt,$lock_no));
			&cgi_lib::common::message("\$tmp_base_path=[$tmp_base_path]");
			&File::Path::make_path($tmp_base_path,{verbose => 0, mode => 0777}) unless(-e $tmp_base_path);
			$tmp_img_prefix = &catdir($tmp_base_path,$obj_name);
			&cgi_lib::common::message("\$tmp_img_prefix=[$tmp_img_prefix]");
			my $tmp_dest_prefix;
			if(defined $sizeStrL){
				$tmp_dest_prefix = sprintf($gif_prefix_fmt,$tmp_img_prefix,$sizeStrL);
			}elsif(defined $sizeStrM){
				$tmp_dest_prefix = sprintf($gif_prefix_fmt,$tmp_img_prefix,$sizeStrM);
			}elsif(defined $sizeStrS){
				$tmp_dest_prefix = sprintf($gif_prefix_fmt,$tmp_img_prefix,$sizeStrS);
			}elsif(defined $sizeStrXS){
				$tmp_dest_prefix = sprintf($gif_prefix_fmt,$tmp_img_prefix,$sizeStrXS);
			}

			&cgi_lib::common::message('');

			if(defined $sizeL){
				$bb = $obj2image->obj2animgif($sizeL,[$obj_file],undef,$tmp_dest_prefix,$b1YRange,undef,undef) unless(-e $imgsL->[0]);
			}elsif(defined $sizeM){
				$bb = $obj2image->obj2animgif($sizeM,[$obj_file],undef,$tmp_dest_prefix,$b1YRange,undef,undef) unless(-e $imgsM->[0]);
			}elsif(defined $sizeS){
				$bb = $obj2image->obj2animgif($sizeS,[$obj_file],undef,$tmp_dest_prefix,$b1YRange,undef,undef) unless(-e $imgsS->[0]);
			}elsif(defined $sizeXS){
				$bb = $obj2image->obj2animgif($sizeXS,[$obj_file],undef,$tmp_dest_prefix,$b1YRange,undef,undef) unless(-e $imgsXS->[0]);
			}

			&cgi_lib::common::message('');

			my @PNG_FILES = ();

			my $target_png_fmt = qq|$tmp_dest_prefix\-%d-target.png|;
			my $angle_png_fmt  = qq|$tmp_dest_prefix\-%d.png|;

			my $inc = 360/$g_max_azimuth;
			for(my $i=0;$i<360;$i+=$inc){
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

			&cgi_lib::common::message('');

			my $gif_file = qq|$dest_prefix.gif|;
			&BITS::ImageC::animatedGIF(in_files=>\@PNG_FILES,out_file=>$gif_file,delay=>$g_animated_gif_delay) unless(-e $gif_file && -s $gif_file);
			utime $obj_timestamp,$obj_timestamp,$gif_file if(defined $obj_timestamp && -e $gif_file && -s $gif_file);

			&cgi_lib::common::message('');

#exit;
			my $angle = 0;
			my $png_file;
			if(defined $imgsL && ref $imgsL eq 'ARRAY'){
				my $l = scalar @$imgsL - 1;
				for(my $i=1;$i<=$l;$i++){
					unless(-e $imgsL->[$i]){
						$png_file = sprintf($angle_png_fmt,$angle);
						die __LINE__,":Unknown file [$png_file]\n" unless(-e $png_file);
						&File::Copy::copy($png_file,$imgsL->[$i]) if(-e $png_file);
						utime $obj_timestamp,$obj_timestamp,$imgsL->[$i] if(defined $obj_timestamp && -e $imgsL->[$i] && -s $imgsL->[$i]);
					}
					$angle += 90;
				}
			}

#exit;
			if(defined $imgsM && ref $imgsM eq 'ARRAY'){
				push(@$inter_files,@$imgsM);

				unless(-e $imgsM->[0]){
					if(-e $imgsMAX->[0]){
						if($sizeStrM eq $g_img_sizeStr){
							&File::Copy::copy($imgsMAX->[0],$imgsM->[0]);
						}else{
							&BITS::ImageC::resize(in_file=>$imgsMAX->[0],geometry=>$sizeStrM,out_file=>$imgsM->[0]);
						}
						utime $obj_timestamp,$obj_timestamp,$imgsM->[0] if(defined $obj_timestamp && -e $imgsM->[0] && -s $imgsM->[0]);
					}
				}
				unlink qq|$img_prefix.gif| if(-e qq|$img_prefix.gif|);
				symlink qq|$obj_name\_$sizeStrM.gif|,qq|$img_prefix.gif| if(-e $imgsM->[0]);
				push(@$inter_files,qq|$img_prefix.gif|);

				$angle = 0;
				my $l = scalar @$imgsM - 1;
				for(my $i=1;$i<=$l;$i++){
					unless(-e $imgsM->[$i]){
						if(-e $imgsMAX->[$i]){
							if($sizeStrM eq $g_img_sizeStr){
								&File::Copy::copy($imgsMAX->[$i],$imgsM->[$i]);
							}else{
								&BITS::ImageC::resize(in_file=>$imgsMAX->[$i],geometry=>$sizeStrM,out_file=>$imgsM->[$i]);
							}
							utime $obj_timestamp,$obj_timestamp,$imgsM->[$i] if(defined $obj_timestamp && -e $imgsM->[$i] && -s $imgsM->[$i]);
						}else{
							$png_file = sprintf($angle_png_fmt,$angle);
							die __LINE__,":Unknown file [$png_file]\n" unless(-e $png_file);
							if($sizeStrM eq $g_img_sizeStr){
								&File::Copy::copy($png_file,$imgsM->[$i]);
							}else{
								&BITS::ImageC::resize(in_file=>$png_file,geometry=>$sizeStrM,out_file=>$imgsM->[$i]);
							}
							utime $obj_timestamp,$obj_timestamp,$imgsM->[$i] if(defined $obj_timestamp && -e $imgsM->[$i] && -s $imgsM->[$i]);
						}
					}
					$angle += 90;
				}
			}


			if(defined $imgsS && ref $imgsS eq 'ARRAY'){
				push(@$inter_files,@$imgsS);

				unless(-e $imgsS->[0]){
					if(-e $imgsMAX->[0]){
						if($sizeStrS eq $g_img_sizeStr){
							&File::Copy::copy($imgsMAX->[0],$imgsS->[0]);
						}else{
							&BITS::ImageC::resize(in_file=>$imgsMAX->[0],geometry=>$sizeStrS,out_file=>$imgsS->[0]);
						}
						utime $obj_timestamp,$obj_timestamp,$imgsS->[0] if(defined $obj_timestamp && -e $imgsS->[0] && -s $imgsS->[0]);
					}
				}

				$angle = 0;
				my $l = scalar @$imgsS - 1;
				for(my $i=1;$i<=$l;$i++){
					unless(-e $imgsS->[$i]){
						if(-e $imgsMAX->[$i]){
							if($sizeStrS eq $g_img_sizeStr){
								&File::Copy::copy($imgsMAX->[$i],$imgsS->[$i]);
							}else{
								&BITS::ImageC::resize(in_file=>$imgsMAX->[$i],geometry=>$sizeStrS,out_file=>$imgsS->[$i]);
							}
							utime $obj_timestamp,$obj_timestamp,$imgsS->[$i] if(defined $obj_timestamp && -e $imgsS->[$i] && -s $imgsS->[$i]);
						}else{
							$png_file = sprintf($angle_png_fmt,$angle);
							die __LINE__,":Unknown file [$png_file]\n" unless(-e $png_file);
							if($sizeStrS eq $g_img_sizeStr){
								&File::Copy::copy($png_file,$imgsS->[$i]);
							}else{
								&BITS::ImageC::resize(in_file=>$png_file,geometry=>$sizeStrS,out_file=>$imgsS->[$i]);
							}
							utime $obj_timestamp,$obj_timestamp,$imgsS->[$i] if(defined $obj_timestamp && -e $imgsS->[$i] && -s $imgsS->[$i]);
						}
					}
					$angle += 90;
				}
			}

			if(defined $imgsXS && ref $imgsXS eq 'ARRAY'){
				push(@$inter_files,@$imgsXS);

				unless(-e $imgsXS->[0]){
					if(-e $imgsMAX->[0]){
						if($sizeStrXS eq $g_img_sizeStr){
							&File::Copy::copy($imgsMAX->[0],$imgsXS->[0]);
						}else{
							&BITS::ImageC::resize(in_file=>$imgsMAX->[0],geometry=>$sizeStrXS,out_file=>$imgsXS->[0]);
						}
						utime $obj_timestamp,$obj_timestamp,$imgsXS->[0] if(defined $obj_timestamp && -e $imgsXS->[0] && -s $imgsXS->[0]);
					}
				}

				$angle = 0;
				my $l = scalar @$imgsXS - 1;
				for(my $i=1;$i<=$l;$i++){
					unless(-e $imgsXS->[$i]){
						if(-e $imgsMAX->[$i]){
							if($sizeStrXS eq $g_img_sizeStr){
								&File::Copy::copy($imgsMAX->[$i],$imgsXS->[$i]);
							}else{
								&BITS::ImageC::resize(in_file=>$imgsMAX->[$i],geometry=>$sizeStrXS,out_file=>$imgsXS->[$i]);
							}
							utime $obj_timestamp,$obj_timestamp,$imgsXS->[$i] if(defined $obj_timestamp && -e $imgsXS->[$i] && -s $imgsXS->[$i]);
						}else{
							$png_file = sprintf($angle_png_fmt,$angle);
							die __LINE__,":Unknown file [$png_file]\n" unless(-e $png_file);
							if($sizeStrXS eq $g_img_sizeStr){
								&File::Copy::copy($png_file,$imgsXS->[$i]);
							}else{
								&BITS::ImageC::resize(in_file=>$png_file,geometry=>$sizeStrXS,out_file=>$imgsXS->[$i]);
							}
							utime $obj_timestamp,$obj_timestamp,$imgsXS->[$i] if(defined $obj_timestamp && -e $imgsXS->[$i] && -s $imgsXS->[$i]);
						}
					}
					$angle += 90;
				}
			}
			for($angle=0;$angle<360;$angle+=$inc){
				$png_file = sprintf($angle_png_fmt,$angle);
				unlink $png_file if(-e $png_file);
			}

			if(defined $b1){
				my $b = {
					xmin => $b1->[0] - 0,
					xmax => $b1->[1] - 0,
					ymin => $b1->[2] - 0,
					ymax => $b1->[3] - 0,
					zmin => $b1->[4] - 0,
					zmax => $b1->[5] - 0,
					volume => defined $b1_volume ? $b1_volume - 0 : undef
				};
				print $OUT &JSON::XS::encode_json($b);
			}

			undef $largerbbox if(defined $largerbbox);

			&File::Path::remove_tree($tmp_base_path) if(defined $tmp_base_path && -e $tmp_base_path);
			undef $tmp_base_path if(defined $tmp_base_path);
			undef $tmp_img_prefix if(defined $tmp_img_prefix);


			undef $obj2image;
			undef $bp3d_objs;

		}
		close($OUT);
		utime $obj_timestamp,$obj_timestamp,$txt_file if(defined $obj_timestamp && -e $txt_file && -s $txt_file);

	}
	undef $OUT if(defined $OUT);
	undef $inter_files if(defined $inter_files);
	&File::Path::remove_tree($txt_file_lock) if(defined $txt_file_lock && -e $txt_file_lock && -d $txt_file_lock);
	$txt_file_lock = undef;

#	exit 1;
}

#&cgi_lib::common::message(&cgi_lib::common::encodeJSON($obj_files1,1));

if(defined $obj_files1){

	my $sql = qq|
select
 cdi.cdi_name,
 cm.md_id,
 cm.mv_id,
 EXTRACT(EPOCH FROM GREATEST(cm.cm_entry,cs.seg_entry)),
 COALESCE(cs_color.seg_thum_fgcolor,cs_null.seg_thum_fgcolor) as seg_thum_fgcolor,
 cs.seg_id
from
 concept_art_map as cm

left join (
 select * from model_version
) as mv on
  mv.md_id=cm.md_id and
  mv.mv_id=cm.mv_id

left join (
 select * from concept_data_info
) as cdi on
  cdi.ci_id=cm.ci_id and
  cdi.cdi_id=cm.cdi_id

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
 mv_use and mv_delcause is null and
 art_id=?
order by
 mv_entry desc
|;
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;

	my $DEF_COLOR_ART;
	my $DEF_TIMESTAMP_ART;

	foreach my $o (@$obj_files1){
		my $art_id = $o->{'art_id'};
=pod
		if(USE_BP3D_COLOR){
			$sth->execute($art_id) or die $dbh->errstr;
			if($sth->rows()>0){
				my $cdi_name;
				my $md_id;
				my $mv_id;
				my $timestamp;
				my $color;
				my $seg_id;
				my $column_number = 0;
				$sth->bind_col(++$column_number, \$cdi_name, undef);
				$sth->bind_col(++$column_number, \$md_id, undef);
				$sth->bind_col(++$column_number, \$mv_id, undef);
				$sth->bind_col(++$column_number, \$timestamp, undef);
				$sth->bind_col(++$column_number, \$color, undef);
				$sth->bind_col(++$column_number, \$seg_id, undef);
				while($sth->fetch){
					if(defined $color && defined $seg_id && $seg_id>0){
						$color =~ s/^#//g;
						push(@{$DEF_COLOR_ART->{$art_id}->{$md_id}->{$mv_id}},hex(uc(substr($color,0,2)))/255);
						push(@{$DEF_COLOR_ART->{$art_id}->{$md_id}->{$mv_id}},hex(uc(substr($color,2,2)))/255);
						push(@{$DEF_COLOR_ART->{$art_id}->{$md_id}->{$mv_id}},hex(uc(substr($color,4,2)))/255);
					}else{
						$DEF_COLOR_ART->{$art_id}->{$md_id}->{$mv_id} = undef;
					}
					$DEF_TIMESTAMP_ART->{$art_id}->{$md_id}->{$mv_id} = $timestamp;
				}
			}
			$sth->finish;
		}
=cut

=pod
		$o->{'color'} = undef;
		if(defined $o->{'timestamp'} && defined $DEF_TIMESTAMP && $o->{'timestamp'} < $DEF_TIMESTAMP){
			$o->{'timestamp'} = $DEF_TIMESTAMP;
		}elsif(!defined $o->{'timestamp'} && defined $DEF_TIMESTAMP){
			$o->{'timestamp'} = $DEF_TIMESTAMP;
		}

		&make_image($o);
		if(USE_BP3D_COLOR){
			if(defined $DEF_COLOR_ART && exists $DEF_COLOR_ART->{$art_id} && defined $DEF_COLOR_ART->{$art_id} && ref $DEF_COLOR_ART->{$art_id} eq 'HASH'){
				foreach my $md_id (sort {$b <=> $a} keys(%{$DEF_COLOR_ART->{$art_id}})){
					foreach my $mv_id (sort {$b <=> $a} keys(%{$DEF_COLOR_ART->{$art_id}->{$md_id}})){
						if(defined $DEF_COLOR_ART->{$art_id}->{$md_id}->{$md_id}){
							$o->{'color'} = $DEF_COLOR_ART->{$art_id}->{$md_id}->{$md_id};
						}else{
							$o->{'delcause'} = 1;
						}
						$o->{'timestamp'} = $DEF_TIMESTAMP_ART->{$art_id}->{$md_id}->{$mv_id};
						&make_image($o,$md_id,$mv_id);
					}
				}
			}
		}
=cut
	}
	undef $sth;

#	my $number_of_cpus = &Sys::CPU::cpu_count();
#	my $pm = new Parallel::ForkManager($number_of_cpus-1);
#	my $number_of_cpus = &Sys::CPU::cpu_count();
#	my $pm = new Parallel::ForkManager(1);

	foreach my $o (sort {$b->{'art_id'} cmp $a->{'art_id'}} @$obj_files1){
		undef $is_child if(defined $is_child);
#		$pm->start and next;

=pod
		my $pid = fork;
		die __LINE__.":Cannot fork: $!" unless defined $pid;
		if($pid){
			my $t0 = [&Time::HiRes::gettimeofday()];
			waitpid($pid,0);
			my $elapsed = &Time::HiRes::tv_interval($t0,[&Time::HiRes::gettimeofday()]);
			print __LINE__.':'.$elapsed."\n";
			print __LINE__.":親プロセス(子プロセスID: $pid)[",$?,"]\n";
			if($?){
				die __LINE__.":[",$?,"]\n";
			}else{
				undef $is_child if(defined $is_child);
			}
		}else{
			$is_child = $$;
=cut

			my $art_id = $o->{'art_id'};
			$o->{'color'} = undef;
			if(defined $o->{'timestamp'} && defined $DEF_TIMESTAMP && $o->{'timestamp'} < $DEF_TIMESTAMP){
				$o->{'timestamp'} = $DEF_TIMESTAMP - 0;
			}elsif(!defined $o->{'timestamp'} && defined $DEF_TIMESTAMP){
				$o->{'timestamp'} = $DEF_TIMESTAMP - 0;
			}
			&make_image($o);
			next;
			if(USE_BP3D_COLOR){
				if(defined $DEF_COLOR_ART && exists $DEF_COLOR_ART->{$art_id} && defined $DEF_COLOR_ART->{$art_id} && ref $DEF_COLOR_ART->{$art_id} eq 'HASH'){
					foreach my $md_id (sort {$b <=> $a} keys(%{$DEF_COLOR_ART->{$art_id}})){
						foreach my $mv_id (sort {$b <=> $a} keys(%{$DEF_COLOR_ART->{$art_id}->{$md_id}})){
							if(defined $DEF_COLOR_ART->{$art_id}->{$md_id}->{$md_id}){
								$o->{'color'} = $DEF_COLOR_ART->{$art_id}->{$md_id}->{$md_id};
							}else{
								$o->{'delcause'} = 1;
							}
							$o->{'timestamp'} = $DEF_TIMESTAMP_ART->{$art_id}->{$md_id}->{$mv_id} - 0;
							&make_image($o,$md_id,$mv_id);
						}
					}
				}
			}
#		$pm->finish;
#			exit 0;
#		}
	}

#	$pm->wait_all_children;

	undef $obj_files1;
}
undef $obj2image;


exit;
