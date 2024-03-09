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
use File::Path;
use JSON::XS;
use Cwd qw(abs_path);
use Hash::Merge qw( merge );
Hash::Merge::set_behavior('LEFT_PRECEDENT');
use File::Path;
use File::Copy;
use List::Util;
use Math::Round;
use POSIX qw( floor :sys_wait_h);
use DBD::Pg;
use Image::Info;
use Time::HiRes qw/gettimeofday tv_interval/;
use Encode;
use Sys::CPU;
use Time::Piece;
use Hash::Diff;

use Data::Dumper;
$Data::Dumper::Indent = 1;
$Data::Dumper::Sortkeys = 1;

use FindBin;
my $htdocs_path;
BEGIN{
	use FindBin;
#	$htdocs_path = qq|$FindBin::Bin/../htdocs_130910|;
	$htdocs_path = qq|$FindBin::Bin/../htdocs| unless(defined $htdocs_path && -e $htdocs_path);
	print __LINE__.":BEGIN2!!\n";
	die "$! [$FindBin::Bin]" unless(chdir($FindBin::Bin));
}
use lib $FindBin::Bin,$htdocs_path,qq|$htdocs_path/../cgi_lib|;

use Getopt::Long qw(:config posix_default no_ignore_case gnu_compat);
my $config = {
	host => '127.0.0.1',
	port => '8543'
};
&Getopt::Long::GetOptions($config,qw/
	host|h=s
	port|p=s
	target|t=s@
	version|v=s@
/) or exit 1;

$ENV{'AG_DB_HOST'} = $config->{'host'};
$ENV{'AG_DB_PORT'} = $config->{'port'};

#my $JSONXS_DEBUG = JSON::XS->new->utf8->indent(1)->canonical(1);
#say $JSONXS_DEBUG->encode($config);
#exit;

use BITS::Config;
#use BITS::ReCalc;
use BITS::ArtFile;
use BITS::ImageC;
use BITS::ConceptArtMapModified;

require "webgl_common.pl";
use cgi_lib::common;

use renderer;
use obj2deci;

#repの画像の場合、データ量が大きい為、Xserverの負荷を分散する為に、各プロセスに１つ
#use constant DEF_SERVER_NUMBRT => 97;
use constant {
	DEF_SERVER_NUMBRT => -1,
	MAX_PROG => 2,
	MAX_CHILD => 4,

	CACHE_FMA_PATH => '/bp3d/cache_fma',
	CHECK_USE_DATE => 0,	#日付のみで確認
	CHECK_USE_DATE_TIME => 1,	#日時で確認
	CHECK_EXISTS_FILE => 0,	#ファイルの有無で確認

	USE_BP3D_COLOR => 1,
	DEBUG_USE_BP3D_COLOR => 0,

	TMPFS => '/dev/shm',
	IMAGEMAGICK_PATH => '/bp3d/local/ImageMagick/6.7.1-0/bin/',
	IMAGEMAGICK_COLOR_REDUCTION_OPTION => '-quality 95 +dither -colors 256 -depth 8',

	BASE_CDI_NAME => [qw/FMA7163 FMA5018 FMA242789/],

#	USE_IMAGE_SIZES => [[640,640],[120,120],[40,40],[16,16]],
	USE_IMAGE_SIZES => [undef,[120,120],undef,[16,16]],

#	USE_MAX_AZIMUTH => 72,
#	USE_MAX_AZIMUTH => 36,
#	USE_MAX_AZIMUTH => 24,
	USE_MAX_AZIMUTH => 12,
#	USE_MAX_AZIMUTH => 8,

#	USE_ANIMATED_GIF_DELAY => 0,
	USE_ANIMATED_GIF_DELAY => 30,

#	USE_ONLY_MAP_TERMS => 1,	#サムネイル作成時にTermにマップされているOBJのみを使用する（従来のサムネイルを作成する場合は、undefを指定する）
##	USE_ONLY_MAP_TERMS => undef,	#サムネイル作成時にTermにマップされているOBJのみを使用する（従来のサムネイルを作成する場合は、undefを指定する）

#	USE_BACKGROUND => 1,	#サムネイル作成時に背景を使用する
	USE_BACKGROUND => 0,	#サムネイル作成時に背景を使用する

	USE_LARGER_BOX => 0,	#サムネイル作成時にLARGER_BOXを使用する


	USE_CALC_VOLUME => 0,	#ボリュームを計算する
};

my $dbh = &get_dbh();

my $MAX_PROG = MAX_PROG;
my $MAX_CHILD = &Sys::CPU::cpu_count();
if($MAX_CHILD>MAX_CHILD){
	$MAX_CHILD = int($MAX_CHILD / MAX_PROG);
}else{
	$MAX_PROG = 1;
}

#my $lib_path;
my $xvfb_lock;
my $display_size;


my $inter_files;
my $is_child;
my $lock_filepath;
my $lock_path;
my $old_umask;

my $tmp_base_path;
my $tmp_img_prefix;

sub sigexit {
	print "\n",__LINE__.":INT!!\n";
#	eval{close(OUT);};
	eval{&unlink_inter_files();};
	exit 1;
}
sub unlink_inter_files {
	if(defined $inter_files){
		foreach my $file (@$inter_files){
			if(-e $file){
				if(-d $file){
					&File::Path::remove_tree($file);
				}else{
					unlink $file;
				}
			}
		}
	}
	&File::Path::remove_tree($tmp_base_path) if(defined $tmp_base_path && -e $tmp_base_path);
}

BEGIN{
	$old_umask = umask(0);
	print __LINE__.":BEGIN!!\n";
	$SIG{'HUP'} = $SIG{'INT'} = $SIG{'QUIT'} = $SIG{'ILL'} = $SIG{'TRAP'} = $SIG{'ABRT'} = $SIG{'BUS'} = $SIG{'FPE'} = $SIG{'KILL'} = $SIG{'USR1'} = $SIG{'SEGV'} = $SIG{'USR2'} = $SIG{'TERM'} = "sigexit";
}
END{
	unless(defined $is_child){
		umask($old_umask);
		print __LINE__.":IS PARENT END!![".(defined $lock_filepath ? $lock_filepath : "")."][".(defined $lock_path ? $lock_path : "")."]\n";
	}elsif($is_child==$$){
		&File::Path::remove_tree($lock_path) if(defined $lock_path && -e $lock_path && -d $lock_path);
		print __LINE__.":IS CHILD END!![".(defined $lock_filepath ? $lock_filepath : "")."][".(defined $lock_path ? $lock_path : "")."][$$]\n";
	}else{
#		print __LINE__.":IS CHILD CHILD END!![$$]\n";
	}
}

my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,qr/\.[^\.]+$/);

#my $lock_dirpath = &catdir($FindBin::Bin,'logs');
my $lock_dirpath = &catdir(TMPFS,$cgi_name);
unless(-e $lock_dirpath){
	&File::Path::make_path($lock_dirpath,{verbose => 0, mode => 0777});
}

my $tmp_filefmt = qq|$cgi_name-%d|;
my $lock_filefmt = qq|$cgi_name.lock-%d|;
my $lock_no=0;
my $LOCK;
for(;$lock_no<$MAX_PROG;$lock_no++){
	$lock_filepath = &catdir($lock_dirpath,sprintf($lock_filefmt,$lock_no));
	print __LINE__.":\$lock_filepath=[$lock_filepath]\n";
	my $f;
	if(-e $lock_filepath){
		$f = qq|+<|;
	}else{
		$f = qq|>|;
	}
	open($LOCK,"$f $lock_filepath") or die qq|[$lock_filepath]:$!|;
	last if(flock($LOCK, 6));

}
exit unless($lock_no<$MAX_PROG);



my $art_file_prefix = &catdir($FindBin::Bin,'art_file');
unless(-e $art_file_prefix){
	&File::Path::make_path($art_file_prefix,{verbose => 0, mode => 0777});
}
my $art_file_fmt = &catdir($art_file_prefix,'%s%s');

sub load_art_file {
	my %args = (
		reduction => 1.0,
		@_
	);
	my $md_id = $args{'md_id'};
	my $mv_id = $args{'mv_id'};
	my $reduction = $args{'reduction'};
#	my $dbh = &get_dbh();

	my $obj_files1 = $args{'obj_files1'};
	my $obj_files2 = $args{'obj_files2'};


#	my @FILES;
	my $bp3d_objs = &renderer::new_bp3d_objs();

	if(defined $obj_files1 && ref $obj_files1 eq 'ARRAY'){
		my @FILES = ();
		push(@FILES,@$obj_files1);
		push(@FILES,@$obj_files2) if(defined $obj_files2 && ref $obj_files2 eq 'ARRAY');
		foreach my $objfile (@FILES){
			if(ref $objfile eq 'HASH'){
				unless(-e $objfile->{'path'}){
#					&BITS::ArtFile::load_art_file_fromDB(dbh=>$dbh,art_id=>$objfile->{'art_id'},hist_serial=>$objfile->{'hist_serial'},art_file_fmt=>$art_file_fmt);
					&BITS::ArtFile::load_art_file_fromDB(dbh=>$dbh,art_id=>$objfile->{'art_id'},art_file_fmt=>$art_file_fmt);
				}
				$bp3d_objs->objReader($objfile->{'path'},$reduction) if(-e $objfile->{'path'});
			}else{
				$bp3d_objs->objReader($objfile,$reduction) if(-e $objfile);
			}
		}
		return $bp3d_objs;
	}




	my $art_id;
	my $art_ext;
	my $art_data;
	my $art_data_size;
	my $art_timestamp;
	my $hist_serial;

	my $sql=<<SQL;;
select
 art_id,
 art_ext,
 art_data_size,
 EXTRACT(EPOCH FROM art_timestamp)
from
 art_file
where
 art_id in (
   select
    art_id
   from
    concept_art_map
   where
    cm_use and
    cm_delcause is null and
    md_id=$md_id and mv_id=$mv_id
   group by
    art_id
 )
SQL
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	print __LINE__.":\$sth->rows()=[",$sth->rows(),"]\n";
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$art_id, undef);
	$sth->bind_col(++$column_number, \$art_ext, undef);
	$sth->bind_col(++$column_number, \$art_data_size, undef);
	$sth->bind_col(++$column_number, \$art_timestamp, undef);
#	$sth->bind_col(++$column_number, \$hist_serial, undef);
	while($sth->fetch){
#		next unless(defined $art_id && defined $art_data_size && defined $art_entry && defined $hist_serial);
		next unless(defined $art_id && defined $art_data_size && defined $art_timestamp);
		my $objfile = sprintf($art_file_fmt,$art_id,$hist_serial,$art_ext);
		my $size = -s $objfile;
		my $mtime = 0;
		$mtime = (stat($objfile))[9] if(-e $objfile);
		unless(-e $objfile && $size == $art_data_size && $mtime>=$art_timestamp){
#			&BITS::ArtFile::load_art_file_fromDB(dbh=>$dbh,art_id=>$art_id,hist_serial=>$hist_serial,art_file_fmt=>$art_file_fmt);
			&BITS::ArtFile::load_art_file_fromDB(dbh=>$dbh,art_id=>$art_id,art_file_fmt=>$art_file_fmt);
		}
		$bp3d_objs->objReader($objfile,$reduction) if(-e $objfile);
	}
	$sth->finish;
	undef $sth;

	return $bp3d_objs;
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


my $model = qq|bp3d|;

#my @VERSION = ("3.0","2.0");
#my @VERSION = ("4.0.1303281200");
#my @VERSION = ("4.0.1305021540");
my @VERSION = ();

my @STANDARD_CDI_NAME = (
#	"FMA71287",	# Head
	"FMA7154",	# Head
	"FMA7155",	# 頸(ver.3.0のみ)
	"FMA13076",	# 第５腰椎
	"FMA24485",	# 膝蓋骨
#	"FMA37450",	# 短趾屈筋
#	"FMA9664",	# 足(ver.3.0のみ),FMA24225
	"FMA24491",	# 足(ver.3.0のみ),FMA24225
);

#my $version = qq|3.0|;
my $copyrightL = qq|$FindBin::Bin/../htdocs/img/copyrightM.png|;
my $copyrightS = qq|$FindBin::Bin/../htdocs/img/copyrightS.png|;

my %STANDARD_BBOX = ();


my @MD_IDS;

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

=pod
my $sth_cmm_sel = $dbh->prepare(qq|select EXTRACT(EPOCH FROM cm_modified) from concept_art_map_modified where md_id=? AND mv_id=? AND cdi_id=?|) or die $dbh->errstr;
my $sth_cmm_upd = $dbh->prepare(qq|update concept_art_map_modified set cm_modified=?,cm_delcause=? where md_id=? AND mv_id=? AND cdi_id=?|) or die $dbh->errstr;
my $sth_cmm_ins = $dbh->prepare(qq|insert into concept_art_map_modified (cm_modified,cm_delcause,ci_id,cb_id,md_id,mv_id,cdi_id) VALUES (?,?,?,?,?,?,?)|) or die $dbh->errstr;
my $sth_cmm_upd_xyz = $dbh->prepare(qq|update concept_art_map_modified set cm_xmin=?,cm_xmax=?,cm_ymin=?,cm_ymax=?,cm_zmin=?,cm_zmax=?,cm_volume=?,cm_density_use_terms=?,cm_density_end_terms=?,cm_density=?,cm_primitive=?,cszr_id=?,csv_id=? where md_id=? AND mv_id=? AND cdi_id=?|) or die $dbh->errstr;

my %SEGMENT_ZRANGE;
if(1){
	my $sth_cszr_sel = $dbh->prepare(qq|select cszr_id,cszr_min,cszr_max from concept_segment_zrange where cszr_delcause is null|) or die $dbh->errstr;
	$sth_cszr_sel->execute() or die $dbh->errstr;
	my $column_number = 0;
	my $cszr_id;
	my $cszr_min;
	my $cszr_max;
	$sth_cszr_sel->bind_col(++$column_number, \$cszr_id, undef);
	$sth_cszr_sel->bind_col(++$column_number, \$cszr_min, undef);
	$sth_cszr_sel->bind_col(++$column_number, \$cszr_max, undef);
	while($sth_cszr_sel->fetch){
		$SEGMENT_ZRANGE{$cszr_id} = {
			'min' => $cszr_min,
			'max' => $cszr_max,
		};
	}
	$sth_cszr_sel->finish;
	undef $sth_cszr_sel;
}
my %SEGMENT_VALUME;
if(1){
	my $sth_csv_sel = $dbh->prepare(qq|select csv_id,csv_min,csv_max from concept_segment_volume where csv_delcause is null|) or die $dbh->errstr;
	$sth_csv_sel->execute() or die $dbh->errstr;
	my $column_number = 0;
	my $csv_id;
	my $csv_min;
	my $csv_max;
	$sth_csv_sel->bind_col(++$column_number, \$csv_id, undef);
	$sth_csv_sel->bind_col(++$column_number, \$csv_min, undef);
	$sth_csv_sel->bind_col(++$column_number, \$csv_max, undef);
	while($sth_csv_sel->fetch){
		$SEGMENT_VALUME{$csv_id}= {
			'min' => $csv_min,
			'max' => $csv_max,
		};
	}
	$sth_csv_sel->finish;
	undef $sth_csv_sel;
}
=cut

my @USE_CDI_NAMES;
if(exists $config->{'target'} && defined $config->{'target'} && ref $config->{'target'} eq 'ARRAY' && scalar @{$config->{'target'}}){
	foreach my $cdi_name (@{$config->{'target'}}){
		push(@USE_CDI_NAMES, $_) for(split(/[^A-Za-z0-9]/,$cdi_name));
	}
}

if(exists $config->{'version'} && defined $config->{'version'} && ref $config->{'version'} eq 'ARRAY' && scalar @{$config->{'version'}}){
	my $sql = sprintf('select md_id from model_version where mv_use and mv_version in (%s) group by md_id order by md_id', join(',',map {'?'} @{$config->{'version'}}));
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute(@{$config->{'version'}}) or die $dbh->errstr;
	print __LINE__.":\$sth->rows()=[",$sth->rows(),"]\n";
	my $column_number = 0;
	my $md_id;
	$sth->bind_col(++$column_number, \$md_id, undef);
	while($sth->fetch){
		next unless(defined $md_id);
		push(@MD_IDS,$md_id);
	}
	$sth->finish;
	undef $sth;
	unless(scalar @MD_IDS){
		say STDERR 'Unknown version['.join(',', @{$config->{'version'}}).']';
		exit 1;
	}
}

if(scalar @MD_IDS == 0){
	my $sql = qq|select md_id from model where md_use order by md_order|;
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	my $column_number = 0;
	my $md_id;
	$sth->bind_col(++$column_number, \$md_id, undef);
	while($sth->fetch){
		push(@MD_IDS,$md_id) if(defined $md_id);
	}
	$sth->finish;
	undef $sth;
}
foreach my $md_id (@MD_IDS){
	next unless(defined $md_id);

#	my @VERSION = qw/5.0.1404151010/;
#	my @VERSION = qw/4.3.1403311232/;
#	my @VERSION = qw/4.1.1309051818/;
#	my @VERSION = qw/4.0.1305021540/;
#	my @VERSION = qw/3.0.1304161700/;
#	my @VERSION = qw/2.0.1304161700/;
#	my @VERSION = qw/4.1.1309051818 4.0.1305021540 3.0.1304161700 2.0.1304161700/;
#	my @VERSION = qw/5.1.1508071408/;
#	my @VERSION = qw/5.0.1601201030/;
	my @VERSION = ();

	if(exists $config->{'version'} && defined $config->{'version'} && ref $config->{'version'} eq 'ARRAY' && scalar @{$config->{'version'}}){
		push(@VERSION,@{$config->{'version'}});
	}

	if(scalar @VERSION == 0){
		my $sql = qq|
select mv_version from model_version as mr
where
 mv_use and
 mr.md_id=?
order by
 mv_order
|;
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute($md_id) or die $dbh->errstr;
		my $column_number = 0;
		my $mv_version;
		$sth->bind_col(++$column_number, \$mv_version, undef);
		while($sth->fetch){
			push(@VERSION,$mv_version) if(defined $mv_version);
		}
		$sth->finish;
		undef $sth;
	}


	foreach my $version (@VERSION){

		print __LINE__.":\$version=[".$version."]\n";

		%STANDARD_BBOX = ();

		my $mv_id;
		my $ci_id;
		my $cb_id;
		my $sql = qq|select mv_id,ci_id,cb_id from model_version where md_id=? and mv_version=?|;
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute($md_id,$version) or die $dbh->errstr;
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$mv_id, undef);
		$sth->bind_col(++$column_number, \$ci_id, undef);
		$sth->bind_col(++$column_number, \$cb_id, undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;
		unless(defined $mv_id){
			die __LINE__.";Unknown Version!!\n";
		}

		my $prev_mv_id;
		my $prev_ci_id;
		my $prev_cb_id;
		$sql = qq|select mv_id,ci_id,cb_id from model_version where mv_use and md_id=$md_id and mv_id<$mv_id order by mv_id desc limit 1|;
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth->bind_col(++$column_number, \$prev_mv_id, undef);
		$sth->bind_col(++$column_number, \$prev_ci_id, undef);
		$sth->bind_col(++$column_number, \$prev_cb_id, undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;


		my %CDI_ID2NAME;
		my %CDI_NAME2ID;
		my $sth_cdi = $dbh->prepare(qq|select cdi_id,cdi_name from concept_data_info where cdi_delcause is null and ci_id=$ci_id|) or die $dbh->errstr;
		$sth_cdi->execute() or die $dbh->errstr;
		$column_number = 0;
		my $cdi_id;
		my $cdi_name;
		$sth_cdi->bind_col(++$column_number, \$cdi_id, undef);
		$sth_cdi->bind_col(++$column_number, \$cdi_name, undef);
		while($sth_cdi->fetch){
			$CDI_ID2NAME{$cdi_id} = $cdi_name;
			$CDI_NAME2ID{$cdi_name} = $cdi_id;
		}
		$sth_cdi->finish;
		undef $sth_cdi;

#		my $change_cdi_ids = &BITS::ReCalc::check(
#			dbh   => $dbh,
#			ci_id => $ci_id,
#			cb_id => $cb_id,
#			md_id => $md_id,
#			mv_id => $mv_id,
#		);

		my $current_set_old = &BITS::ConceptArtMapModified::exec(
			dbh => $dbh,
			md_id => $md_id,
			mv_id => $prev_mv_id,
			ci_id => $prev_ci_id,
			cb_id => $prev_cb_id,
			use_only_map_terms=>&BITS::Config::USE_ONLY_MAP_TERMS(),
			cdi_names => (scalar @USE_CDI_NAMES ? \@USE_CDI_NAMES : undef),
#			LOG => $LOG
		);
		my $current_set = &BITS::ConceptArtMapModified::exec(
			dbh => $dbh,
			md_id => $md_id,
			mv_id => $mv_id,
			ci_id => $ci_id,
			cb_id => $cb_id,
			use_only_map_terms=>&BITS::Config::USE_ONLY_MAP_TERMS(),
			cdi_names => (scalar @USE_CDI_NAMES ? \@USE_CDI_NAMES : undef),
#			LOG => $LOG
		);
#&cgi_lib::common::message(&cgi_lib::common::encodeJSON(&Hash::Diff::diff($current_set,$current_set_old),1), $LOG);
#my $current_set_diff = &Hash::Diff::diff($current_set,$current_set_old);
#		my $change_cdi_ids = &Hash::Diff::diff($current_set,$current_set_old);
#		undef $change_cdi_ids if(defined $change_cdi_ids && ref $change_cdi_ids eq 'HASH' && scalar keys(%$change_cdi_ids) == 0);


		if(defined $current_set_old && ref $current_set_old eq 'HASH' && scalar keys(%$current_set_old)){
			my $count = scalar keys(%$current_set_old);
			foreach my $cdi_id (keys(%$current_set_old)){
				printf("\rsymlink:[%4d]",--$count,'');
				my $target_cdi_name = $CDI_ID2NAME{$cdi_id};
				my($img_prefix,$img_path) = &getCmImagePrefix($md_id,$mv_id,undef,$target_cdi_name);
				my $img_base_path = &File::Basename::dirname($img_path);
				&File::Path::make_path($img_base_path,{verbose => 0, mode => 0777}) unless(-e $img_base_path && -d $img_base_path);
				unless(-e $img_path){
					if(defined $prev_mv_id && defined $prev_ci_id && defined $prev_cb_id && $prev_ci_id == $ci_id && $prev_cb_id == $cb_id){
						my($prev_img_prefix,$prev_img_path) = &getCmImagePrefix($md_id,$prev_mv_id,undef,$target_cdi_name);
						if(-e $prev_img_path){
							my $src = &abs2rel($prev_img_path,$img_base_path);
							symlink($src,$img_path);# or die "$!:$src:$img_path";
						}
					}
				}
			}
			say '';
		}


#say __LINE__.':'.scalar keys(%$current_set_old);
say __LINE__.':$current_set='.scalar keys(%$current_set);

#=pod
		my($ELEMENT, $COMP_DENSITY_USE_TERMS, $COMP_DENSITY_END_TERMS, $COMP_DENSITY, $CDI_MAP, $CDI_MAP_ART_DATE, $CDI_ID2CID);
		if(&BITS::Config::USE_ONLY_MAP_TERMS()){
			($ELEMENT, $COMP_DENSITY_USE_TERMS, $COMP_DENSITY_END_TERMS, $COMP_DENSITY, $CDI_MAP, $CDI_MAP_ART_DATE, $CDI_ID2CID) = &BITS::ConceptArtMapModified::calcElementAndDensity(
				dbh     => $dbh,
				md_id   => $md_id,
				mv_id   => $mv_id,
				ci_id   => $ci_id,
				cb_id   => $cb_id,
				cdi_ids => [keys %$current_set],
	#			LOG => $LOG
			);
			say __LINE__.':$CDI_MAP_ART_DATE='.scalar keys(%$CDI_MAP_ART_DATE) if(defined $CDI_MAP_ART_DATE);
			say __LINE__.':$ELEMENT='.scalar keys(%$ELEMENT) if(defined $ELEMENT);
			say __LINE__.':$COMP_DENSITY='.scalar keys(%$COMP_DENSITY) if(defined $COMP_DENSITY);
			say __LINE__.':$COMP_DENSITY='.scalar grep {$COMP_DENSITY->{$_}>0} keys(%$COMP_DENSITY) if(defined $COMP_DENSITY);
			say __LINE__.':$COMP_DENSITY_USE_TERMS='.scalar grep {$COMP_DENSITY_USE_TERMS->{$_}>0} keys(%$COMP_DENSITY_USE_TERMS) if(defined $COMP_DENSITY_USE_TERMS);

			foreach my $cdi_id (keys %$current_set){
				$current_set->{$cdi_id}->{'cm_delcause'} = 'DELETE' unless(exists $CDI_MAP_ART_DATE->{$cdi_id});
			}
		}

		my $change_cdi_ids;
		$change_cdi_ids = &BITS::ConceptArtMapModified::diff($current_set,$current_set_old);# if(defined $current_set && defined $current_set_old);
say __LINE__.':change_cdi_ids='.scalar keys(%$change_cdi_ids) if(defined $change_cdi_ids);

#exit;
#=cut

#			die __LINE__.":\n";

		my($DEF_COLOR_ART,$DEF_COLOR) = &BITS::ArtFile::get_all_colors(dbh=>$dbh,md_id=>$md_id,mv_id=>$mv_id,ci_id=>$ci_id,cb_id=>$cb_id);

		foreach my $cdi_name (@STANDARD_CDI_NAME){
			my($art_xmin,$art_xmax,$art_ymin,$art_ymax,$art_zmin,$art_zmax) = &BITS::ArtFile::get_art_file_bbox(dbh=>$dbh,md_id=>$md_id,mv_id=>$mv_id,ci_id=>$ci_id,cb_id=>$cb_id,cdi_id=>$CDI_NAME2ID{$cdi_name});
			next unless(defined $art_xmin && defined $art_xmax && defined $art_ymin && defined $art_ymax && defined $art_zmin && defined $art_zmax);
			push(@{$STANDARD_BBOX{$cdi_name}},$art_xmin+0,$art_xmax+0,$art_ymin+0,$art_ymax+0,$art_zmin+0,$art_zmax+0);
			&cgi_lib::common::message("[$cdi_name]=[".&cgi_lib::common::encodeJSON($STANDARD_BBOX{$cdi_name},1)."]");
		}



		my %Z_BBOX = ();

		$sql =<<SQL;
select
  round(art_zmax) as z,
  min(art_xmin) as xmin,
  max(art_xmax) as xmax,
  min(art_ymin) as ymin,
  max(art_ymax) as ymax,
  min(art_zmin) as zmin,
  max(art_zmax) as zmax
from
  art_file
where
  art_id in (
    select
     art_id
    from
     concept_art_map
    where
     cm_use and
     cm_delcause is null and
     md_id=$md_id and
     mv_id=$mv_id
  )
group by z
SQL

		my $rep_z;
		my $rep_xmin;
		my $rep_xmax;
		my $rep_ymin;
		my $rep_ymax;
		my $rep_zmin;
		my $rep_zmax;
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		say __LINE__.":\$sth->rows()=[".$sth->rows()."]";
		$column_number = 0;
		$sth->bind_col(++$column_number, \$rep_z, undef);
		$sth->bind_col(++$column_number, \$rep_xmin, undef);
		$sth->bind_col(++$column_number, \$rep_xmax, undef);
		$sth->bind_col(++$column_number, \$rep_ymin, undef);
		$sth->bind_col(++$column_number, \$rep_ymax, undef);
		$sth->bind_col(++$column_number, \$rep_zmin, undef);
		$sth->bind_col(++$column_number, \$rep_zmax, undef);
		while($sth->fetch){
			next unless(
				defined $rep_z &&
				defined $rep_xmin && defined $rep_xmax && 
				defined $rep_ymin && defined $rep_ymax && 
				defined $rep_zmin && defined $rep_zmax
			);

			$Z_BBOX{$rep_z} = {
				xmin => $rep_xmin+0,
				xmax => $rep_xmax+0,
				ymin => $rep_ymin+0,
				ymax => $rep_ymax+0,
				zmin => $rep_zmin+0,
				zmax => $rep_zmax+0
			};
		}
		$sth->finish;
		undef $sth;

		my $tbp_max_enter;
		my $sth_tbp_enter = $dbh->prepare(qq|select EXTRACT(EPOCH FROM max(tbp_enter)) from thumbnail_background_part where md_id=$md_id and mv_id=$mv_id and ci_id=$ci_id|) or die $dbh->errstr;
		$sth_tbp_enter->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth_tbp_enter->bind_col(++$column_number, \$tbp_max_enter, undef);
		$sth_tbp_enter->fetch;
		$sth_tbp_enter->finish;
		undef $sth_tbp_enter;
		$tbp_max_enter = 0 unless(defined $tbp_max_enter);
		print __LINE__.":\$tbp_max_enter=$tbp_max_enter\n";

		if(1){
			my $base_cdi_name;
			my $sth_tbp = $dbh->prepare(qq|select cdi_id from thumbnail_background_part where md_id=$md_id and mv_id=$mv_id and ci_id=$ci_id and tbp_use and tbp_delcause is null|) or die $dbh->errstr;
			$sth_tbp->execute() or die $dbh->errstr;
			$column_number = 0;
			my $cdi_id;
			$sth_tbp->bind_col(++$column_number, \$cdi_id, undef);
			while($sth_tbp->fetch){
				my $cdi_name = $CDI_ID2NAME{$cdi_id};
				next unless(defined $cdi_name);
				$base_cdi_name = [] unless(defined $base_cdi_name);
				push(@{$base_cdi_name},$cdi_name);
			}
			$sth_tbp->finish;
			undef $sth_tbp;

			$base_cdi_name = &BASE_CDI_NAME() unless(defined $base_cdi_name);

			my $base_art_files;
			if(ref $base_cdi_name eq 'ARRAY'){
				foreach my $cdi_name (@{$base_cdi_name}){
					my $art_files = &BITS::ArtFile::get_art_file(dbh=>$dbh,md_id=>$md_id,mv_id=>$mv_id,ci_id=>$ci_id,cb_id=>$cb_id,cdi_id=>$CDI_NAME2ID{$cdi_name});
					push(@$base_art_files,@$art_files) if(defined $art_files && ref $art_files eq 'ARRAY');
					undef $art_files;

				}
			}else{
				my $art_files = &BITS::ArtFile::get_art_file(dbh=>$dbh,md_id=>$md_id,mv_id=>$mv_id,ci_id=>$ci_id,cb_id=>$cb_id,cdi_id=>$CDI_NAME2ID{$base_cdi_name});
				push(@$base_art_files,@$art_files) if(defined $art_files && ref $art_files eq 'ARRAY');
				undef $art_files;

			}

			unless(defined $base_art_files && ref $base_art_files eq 'ARRAY'){
#				die __LINE__.":undefined \$base_art_files!!\n";
				print STDERR __LINE__.":undefined \$base_art_files!!\n";
				next;
			}



			my $rep_xmin;
			my $rep_xmax;
			my $rep_ymin;
			my $rep_ymax;
			my $rep_zmin;
			my $rep_zmax;

			($rep_xmin,$rep_xmax,$rep_ymin,$rep_ymax,$rep_zmin,$rep_zmax) = &BITS::ArtFile::get_art_file_bbox(dbh=>$dbh,md_id=>$md_id,mv_id=>$mv_id,ci_id=>$ci_id,cb_id=>$cb_id);
			next unless(defined $rep_xmin && defined $rep_xmax && defined $rep_ymin && defined $rep_ymax && defined $rep_zmin && defined $rep_zmax);
			my $all_bound = [$rep_xmin+0,$rep_xmax+0,$rep_ymin+0,$rep_ymax+0,$rep_zmin+0,$rep_zmax+0];

			my @CDI_NAMES = ();

			if(defined $change_cdi_ids){
#					&cgi_lib::common::message('');

#				print STDERR __LINE__.":".&Data::Dumper::Dumper($change_cdi_ids);
#				die __LINE__.":DEBUG\n";

				my $sth_cd = $dbh->prepare(qq|select EXTRACT(EPOCH FROM GREATEST(cd_entry,seg_entry)) as cd_entry,seg_thum_fgcolor from concept_data as cd left join(select seg_id,seg_entry,seg_thum_fgcolor from concept_segment) as seg on seg.seg_id=cd.seg_id where cd_delcause is null and ci_id=$ci_id and cb_id=$cb_id and cdi_id=?|) or die $dbh->errstr;

				foreach my $cdi_id (keys(%$change_cdi_ids)){
					next unless(exists $CDI_ID2NAME{$cdi_id} && defined $CDI_ID2NAME{$cdi_id} && length $CDI_ID2NAME{$cdi_id});
					my $cdi_name = $CDI_ID2NAME{$cdi_id};
					my $rep_delcause = (exists $change_cdi_ids->{$cdi_id} && defined $change_cdi_ids->{$cdi_id}->{'cm_delcause'}) ? 'DELETE' : undef;
					my $cm_modified;
					$cm_modified = $change_cdi_ids->{$cdi_id}->{'cm_entry_epoch'} unless(defined $rep_delcause);

#					if($cdi_name eq 'FMA72686' && defined $cm_modified){
#						my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($cm_modified);
#						my $file_mtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
#						say __LINE__.qq|:$cdi_name:[$file_mtime]|;
#					}

					my $cd_entry;
					my $seg_thum_fgcolor;
					$sth_cd->execute($cdi_id) or die $dbh->errstr;
					$sth_cd->bind_col(1, \$cd_entry, undef);
					$sth_cd->bind_col(2, \$seg_thum_fgcolor, undef);
					$sth_cd->fetch;
					$sth_cd->finish;

#					if($cdi_name eq 'FMA72686' && defined $cd_entry){
#						my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($cd_entry);
#						my $file_mtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
#						say __LINE__.qq|:$cdi_name:[$file_mtime]|;
#					}

					if(defined $cm_modified && defined $cd_entry){
						$cm_modified = $cd_entry if($cm_modified < $cd_entry);
					}elsif(!defined $cm_modified && defined $cd_entry){
						$cm_modified = $cd_entry;
					}

					my $rep_entry = defined $cm_modified ? $cm_modified : time;

#					if($cdi_name eq 'FMA72686'){
#						my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($rep_entry);
#						my $file_mtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
#						say __LINE__.qq|:$cdi_name:[$file_mtime]|;
#					}

					push(@CDI_NAMES,{
						cdi_name     => $cdi_name,
						rep_delcause => $rep_delcause,
						rep_entry    => $rep_entry,
						rep_color    => $seg_thum_fgcolor,
					});
				}

#				print STDERR __LINE__.":".&Data::Dumper::Dumper(\@CDI_NAMES);
#				next;
#				die __LINE__.":DEBUG\n";
#				print STDERR __LINE__.':'.&Data::Dumper::Dumper(\@CDI_NAMES);

				undef $sth_cd;
			}

#			say STDERR __LINE__;
#say __LINE__.':'.scalar @CDI_NAMES."\n";
#exit;

#			if(defined $change_cdi_ids || scalar @CDI_NAMES == 0){
			if(scalar @CDI_NAMES == 0){
				my %EXISTS_CDI = ();
				%EXISTS_CDI = map {$_->{'cdi_name'}=>undef} @CDI_NAMES if(defined $change_cdi_ids && scalar @CDI_NAMES);

				my $all_map_cdi_names = &BITS::ArtFile::get_all_map_cdi_names(dbh=>$dbh,md_id=>$md_id,mv_id=>$mv_id,ci_id=>$ci_id,cb_id=>$cb_id,use_only_map_terms=>&BITS::Config::USE_ONLY_MAP_TERMS());

				my $all_unmap_cdi_names = &BITS::ArtFile::get_all_unmap_cdi_names(dbh=>$dbh,md_id=>$md_id,mv_id=>$mv_id,ci_id=>$ci_id,cb_id=>$cb_id,all_map_cdi_names=>$all_map_cdi_names) if($lock_no==0 && defined $all_map_cdi_names);
				if(defined $all_unmap_cdi_names){
					foreach my $cdi_name (keys(%$all_unmap_cdi_names)){
						next if(exists $EXISTS_CDI{$cdi_name});
						push(@CDI_NAMES,{
							cdi_name     => $cdi_name,
							rep_delcause => 'DELETE',
							rep_entry    => time,
						});
#						$EXISTS_CDI{$cdi_name} = undef;
					}
#say __LINE__.':'.scalar keys($all_unmap_cdi_names);
				}
				if(defined $all_map_cdi_names){
#					print STDERR __LINE__.':'.&Data::Dumper::Dumper($all_map_cdi_names);

#say __LINE__.':'.scalar keys($all_map_cdi_names);
#exit;
#say __LINE__.':'.scalar @CDI_NAMES;
#exit;

					my %CMM_TIME = ();

					foreach my $cdi_id (keys(%$current_set)){
						next unless(exists $current_set->{$cdi_id});
						if(defined $change_cdi_ids->{$cdi_id}->{'cm_delcause'}){
							$CMM_TIME{$CDI_ID2NAME{$cdi_id}} = undef;
						}else{
							$CMM_TIME{$CDI_ID2NAME{$cdi_id}} = $change_cdi_ids->{$cdi_id}->{'cm_entry_epoch'};
						}
					}

					foreach my $cdi_name (keys(%$all_map_cdi_names)){
						next if(exists $EXISTS_CDI{$cdi_name});

						my $cm_modified = exists $CMM_TIME{$cdi_name} && defined $CMM_TIME{$cdi_name} ? $CMM_TIME{$cdi_name} : undef;

						my $rep_entry = (ref  $all_map_cdi_names->{$cdi_name} eq 'HASH' ? $all_map_cdi_names->{$cdi_name}->{'entry'} : $all_map_cdi_names->{$cdi_name});

#						if($cdi_name eq 'FMA72686'){
#							my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($rep_entry);
#							my $file_mtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
#							say __LINE__.qq|:$cdi_name:[$file_mtime]|;
#						}

						$rep_entry = $cm_modified if(defined $cm_modified);

#						if($cdi_name eq 'FMA72686'){
#							my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($rep_entry);
#							my $file_mtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
#							say __LINE__.qq|:$cdi_name:[$file_mtime]|;
#						}

						push(@CDI_NAMES,{
							cdi_name     => $cdi_name,
							rep_delcause => undef,
							rep_entry    => $rep_entry,
							rep_color    => (ref  $all_map_cdi_names->{$cdi_name} eq 'HASH' ? $all_map_cdi_names->{$cdi_name}->{'seg_thum_fgcolor'} : undef),
						});

						$EXISTS_CDI{$cdi_name} = undef;
					}
				}
			}
#say __LINE__.':'.scalar @CDI_NAMES;
#exit;

			foreach my $t_b_id (sort {$a->{'cdi_name'} cmp $b->{'cdi_name'}} @CDI_NAMES){
				my $target_cdi_name = $t_b_id->{'cdi_name'};
				my $rep_ci_id = $ci_id;
				my $rep_cb_id = $cb_id;
				my $rep_entry = $t_b_id->{'rep_entry'};
				my $rep_delcause = $t_b_id->{'rep_delcause'};
				my $rep_color = $t_b_id->{'rep_color'};
				print __LINE__.":\$rep_color=[".$rep_color."]\n" if(defined $rep_color);

				my($img_prefix,$img_path) = &getCmImagePrefix($md_id,$mv_id,undef,$target_cdi_name);
				my $img_base_path = &File::Basename::dirname($img_path);
				&File::Path::make_path($img_base_path,{verbose => 0, mode => 0777}) unless(-e $img_base_path && -d $img_base_path);
				$lock_path = qq|$img_path.lock|;
				if(mkdir($lock_path,0777)){
#					print __LINE__.":make_path:[OK]\n";
				}else{
					undef $lock_path;
					next;
				}

				if(defined $t_b_id->{'rep_delcause'}){
					if(defined $img_path && -e $img_path){
						if(-l $img_path){
							unlink $img_path;
						}elsif(-d $img_path){
							&File::Path::remove_tree($img_path);
						}
					}
					if(defined $lock_path){
						&File::Path::remove_tree($lock_path) if(-e $lock_path && -d $lock_path);
						undef $lock_path;
					}
					next;
				}

#				if($target_cdi_name eq 'FMA72686'){
#					my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($rep_entry);
#					my $file_mtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
#					say __LINE__.qq|:$cdi_name:[$file_mtime]|;
#				}

				if(defined $tbp_max_enter && $tbp_max_enter>$rep_entry){
					print __LINE__.":\$tbp_max_enter=$tbp_max_enter\n";
					print __LINE__.":\$rep_entry=$rep_entry\n";
					$rep_entry = $tbp_max_enter;
					print __LINE__.":\$rep_entry=$rep_entry\n";
				}
				my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($rep_entry);
				my $rep_entry_str = sprintf("%04d-%02d-%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);


#				if($target_cdi_name eq 'FMA72686'){
#					my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($rep_entry);
#					my $file_mtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
#					say __LINE__.qq|:$cdi_name:[$file_mtime]|;
#				}

				my $FOCUS_COLOR;
				my $COLOR;
#				if(USE_BP3D_COLOR){
#					push(@$FOCUS_COLOR,(1.0,0.3176470588235294,0.0));
#				}
				if(USE_BP3D_COLOR && defined $rep_color){
					my $tmp_color = $rep_color;
					$tmp_color =~ s/^#//g;
					push(@$FOCUS_COLOR,hex(uc(substr($tmp_color,0,2)))/255);
					push(@$FOCUS_COLOR,hex(uc(substr($tmp_color,2,2)))/255);
					push(@$FOCUS_COLOR,hex(uc(substr($tmp_color,4,2)))/255);
				}


#				die $img_path."\n";
				if(scalar @USE_CDI_NAMES){
					if(defined $img_path && -e $img_path){
						if(-l $img_path){
							unlink $img_path;
						}elsif(-d $img_path){
							&File::Path::remove_tree($img_path);
						}
					}
				}

				unless(-e $img_path){
					if(defined $prev_mv_id && defined $prev_ci_id && defined $prev_cb_id && $prev_ci_id == $ci_id && $prev_cb_id == $cb_id){
						my($prev_img_prefix,$prev_img_path) = &getCmImagePrefix($md_id,$prev_mv_id,undef,$target_cdi_name);
						if(-e $prev_img_path){
							my $src = &abs2rel($prev_img_path,$img_base_path);
							symlink($src,$img_path) or die "$!:$src:$img_path";
#&cgi_lib::common::message($src);
#&cgi_lib::common::message($img_path);
#exit 1;
						}
					}
				}
				&File::Path::make_path($img_path,{verbose => 0, mode => 0777}) unless(-e $img_path);

#				my $img_prefix = &catdir($img_path,$target_cdi_name);
				my $txt_file = qq|$img_prefix.txt|;
#				print __LINE__.":\$txt_file=[",$txt_file,"][",(-e $txt_file ? 1 : 0),"][",(-s $txt_file),"]\n";

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

				my @chk_files;
				push(@chk_files,$txt_file);
				push(@chk_files,@$imgsL)  if(defined $imgsL);
				push(@chk_files,@$imgsM)  if(defined $imgsM);
				push(@chk_files,@$imgsS)  if(defined $imgsS);
				push(@chk_files,@$imgsXS) if(defined $imgsXS);

				say __LINE__.":\$txt_file=[",$txt_file,"][",(-e $txt_file ? (-s $txt_file) : 0),"]" if(defined $txt_file);


#				shift @chk_files;

#				my $chk = (-l $txt_file) ? 1 : undef;
				my $chk;
				my $max_mtime = 0;
				my $rep_entry_floor = &floor($rep_entry);
				unless(defined $chk){
					foreach my $chk_file (@chk_files){
						my $chk_mtime = -e $chk_file ? (stat($chk_file))[9] : 0;
						$max_mtime = $chk_mtime if($max_mtime<$chk_mtime);
						if(-e $chk_file && -s $chk_file && $chk_mtime>=$rep_entry_floor){
							if($chk_mtime>$rep_entry_floor){
								my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($chk_mtime);
								my $chk_mtime_str = sprintf("%04d-%02d-%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);

								say __LINE__.':$chk_file=['.$chk_file.']';
								say __LINE__.':$chk_mtime=['.$chk_mtime.']['.$chk_mtime_str.']';
								say __LINE__.':$rep_entry=['.$rep_entry.']['.$rep_entry_str.']';
								say __LINE__.':$rep_entry_floor=['.$rep_entry_floor."]";
								$rep_entry -= 0;
#								die __LINE__."\n";
								utime $rep_entry,$rep_entry,$chk_file;
							}
							$max_mtime = $rep_entry if($max_mtime<$rep_entry);
							next;
						}
						next if(CHECK_EXISTS_FILE && -e $chk_file && -s $chk_file);

						my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($chk_mtime);
						my $file_mtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
						my $file_date = sprintf("%04d/%02d/%02d",$year+1900,$mon+1,$mday);

						($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($rep_entry);
						my $rep_mtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
						my $rep_date = sprintf("%04d/%02d/%02d",$year+1900,$mon+1,$mday);

#						if($version eq '4.1.1309051818' && $file_mtime ne $rep_mtime){
#							utime $rep_entry,$rep_entry,$chk_file;
#							$file_mtime = $rep_mtime;
#							$file_date = $rep_date;
#						}

						if(CHECK_USE_DATE_TIME && $file_mtime eq $rep_mtime){
							print __LINE__.":更新日時比較:[文字で確認][$file_mtime]==[$rep_mtime]\n";
							next;
						}
						if(CHECK_USE_DATE && $file_date eq $rep_date){
							print __LINE__.":更新日比較:[文字で確認][$file_date]==[$rep_date]\n";
							next;
						}

	#					next if($file_date ge $rep_date);#実際には、この比較は無効

						$chk = 1;


						print __LINE__.":更新日時比較:[$chk_file][$file_mtime]<[$rep_mtime]\n";

						last;
					}
				}
#				die __LINE__."\n" if(defined $chk && -e $txt_file);

				unless(defined $chk){
					utime $rep_entry,$rep_entry,$img_path if(-e $img_path && -d $img_path);
					if(defined $lock_path){
						&File::Path::remove_tree($lock_path) if(-e $lock_path && -d $lock_path);
						undef $lock_path;
					}
					next;
				}

				#シンボリックリンクの場合は、削除する
				if(defined $img_path && -e $img_path){
					unlink $img_path if(-l $img_path);
				}
				&File::Path::make_path($img_path,{verbose => 0, mode => 0777}) unless(-e $img_path);


				my $pid = fork;
#				my $pid = 0;
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
#						exit 0;

						undef $is_child if(defined $is_child);

						&disconnectDB();
						&connectDB();
						$dbh = &get_dbh();
					}
				}else{
#					$SIG{'HUP'} = $SIG{'INT'} = $SIG{'QUIT'} = $SIG{'ILL'} = $SIG{'TRAP'} = $SIG{'ABRT'} = $SIG{'BUS'} = $SIG{'FPE'} = $SIG{'KILL'} = $SIG{'USR1'} = $SIG{'SEGV'} = $SIG{'USR2'} = $SIG{'TERM'} = "sigexit";

					$is_child = $$;
					undef $inter_files if(defined $inter_files);

					undef $tmp_base_path if(defined $tmp_base_path);
					undef $tmp_img_prefix if(defined $tmp_img_prefix);

					if(-l $txt_file){
						unlink qq|$img_prefix.gif|;
						foreach my $chk_file (@chk_files){
							print __LINE__.":unlink:[$chk_file]\n";
							unlink $chk_file;
						}
					}

					my $TXT;
					if(open($TXT,"> $txt_file")){
#					if(!-e $lock_dirpath && &File::Path::make_path($lock_dirpath,{verbose => 0, mode => 0777}) && open($TXT,"> $txt_file")){
#						if(flock($TXT, 6)){
						if(1){

							&connectDB();
							$dbh = &get_dbh();

							print __LINE__.":[$md_id,$mv_id,$target_cdi_name]\n";


							unlink qq|$img_prefix.gif| if(-e qq|$img_prefix.gif|);
							foreach my $chk_file (@chk_files){
								next if($chk_file eq $txt_file);
								unlink $chk_file;
							}

							my $obj_files1;
							my $obj_files2;

							my %use_objs;

							my $use_bp3d_color;

							my $art_files = &BITS::ArtFile::get_art_file(
								dbh=>$dbh,
								md_id=>$md_id,
								mv_id=>$mv_id,
								ci_id=>$ci_id,
								cb_id=>$cb_id,
								cdi_id=>$CDI_NAME2ID{$target_cdi_name},
								use_only_map_terms=>&BITS::Config::USE_ONLY_MAP_TERMS()
							);
							if(defined $art_files && ref $art_files eq 'ARRAY'){
								my $cdi_id = $CDI_NAME2ID{$target_cdi_name};

								foreach my $art_file (@$art_files){
									my $art_id = $art_file->{'art_id'};
									my $art_ext = $art_file->{'art_ext'};
									next unless(defined $art_id && defined $art_ext);

									if(&BITS::Config::USE_ONLY_MAP_TERMS()){
										next unless(exists $CDI_MAP_ART_DATE->{$CDI_NAME2ID{$target_cdi_name}}->{$art_id});
									}

									my $objfile = sprintf($art_file_fmt,$art_id,$art_ext);
#									print STDERR __LINE__.":\$objfile=[$objfile]\n";
									&BITS::ArtFile::load_art_file_fromDB(dbh=>$dbh,art_id=>$art_id,art_file_fmt=>$art_file_fmt) unless(-e $objfile);
									next unless(-e $objfile);

									my $color;
									if(USE_BP3D_COLOR){
										if(exists $DEF_COLOR_ART->{$art_id} && ref $DEF_COLOR_ART->{$art_id} eq 'ARRAY'){
											push(@$color,@{$DEF_COLOR_ART->{$art_id}});
											$use_bp3d_color = 1;
#											die __LINE__.':'.&Data::Dumper::Dumper($color)."\n";
										}else{
											print STDERR __LINE__.":Unknown color [$art_id]\n";
										}
									}

									push(@$obj_files1,{
										path    => $objfile,
										color   => $color,
										art_id  => $art_id,
										art_ext => $art_ext
									});
									$use_objs{$objfile} = undef;
								}
							}else{
								die __LINE__.":undefined \$art_files=[$art_files]!!\n";
							}


#							%use_objs = map {$_->{'path'}=>undef} @$obj_files1;
							if(defined $obj_files1 && ref $obj_files1 eq 'ARRAY'){
								print __LINE__.":obj_files1=[",(scalar @$obj_files1),"]\n";
							}else{
								close($TXT);
								unlink $txt_file if(-z $txt_file);
#								die __LINE__.":undefined \$obj_files1=[$obj_files1]!!\n";
								print __LINE__.":undefined \$obj_files1!!\n";
								exit(0);
							}

							if(USE_BP3D_COLOR && DEBUG_USE_BP3D_COLOR){
								unless(defined $use_bp3d_color){
									close($TXT);
									unlink $txt_file if(-z $txt_file);
									exit(0);
								}
							}

							print __LINE__.":obj_files1=[",(scalar @$obj_files1),"]\n" if(defined $obj_files1 && ref $obj_files1 eq 'ARRAY');
#							exit 1;

							if(USE_BACKGROUND){
								if(defined $base_art_files && ref $base_art_files eq 'ARRAY'){
									my $color;
									push(@$color,@$DEF_COLOR) if(defined $DEF_COLOR && ref $DEF_COLOR eq 'ARRAY');

									$obj_files2 = [];
									foreach my $art_file (@$base_art_files){
										my $art_id = $art_file->{'art_id'};
										my $art_ext = $art_file->{'art_ext'};

										next unless(defined $art_id && defined $art_ext);

										my $objfile = sprintf($art_file_fmt,$art_id,$art_ext);
										next if(exists $use_objs{$objfile});

										&BITS::ArtFile::load_art_file_fromDB(dbh=>$dbh,art_id=>$art_id,art_file_fmt=>$art_file_fmt) unless(-e $objfile);
										next unless(-e $objfile);

										push(@$obj_files2,{
											path    => $objfile,
											color   => $color,
											art_id  => $art_id,
											art_ext => $art_ext
										});
										$use_objs{$objfile} = undef;
									}
								}else{
									die __LINE__.":undefined \$base_art_files=[$base_art_files]!!\n";
								}
							}

							print __LINE__.":obj_files2=[",(scalar @$obj_files2),"]\n" if(defined $obj_files2);

							my $bp3d_objs = &load_art_file(md_id=>$md_id,mv_id=>$mv_id,obj_files1=>$obj_files1,obj_files2=>$obj_files2);

							if(defined $g_img_size && ref $g_img_size eq 'ARRAY'){
								$_ -= 0 for(@$g_img_size);
							}
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

							my $largerbbox;
							my $largerbboxYRange;


							&cgi_lib::common::message("\$target_cdi_name=$target_cdi_name");

							my $b1;
#							my $b1 = $obj2image->bound($obj_files1);
#							$_+=0 for(@$b1);

							my $b1_volume;
							if(&USE_CALC_VOLUME()){
								my $prop = &obj2deci::getProperties($obj_files1);
#								&obj2deci::objDeleteAll();	#高速化の為、コメントアウト
								&cgi_lib::common::message('$prop='.&cgi_lib::common::encodeJSON($prop,1)) if(defined $prop);
								if(defined $prop && ref $prop eq 'HASH' && exists $prop->{'bounds'} && defined $prop->{'bounds'} && ref $prop->{'bounds'} eq 'ARRAY' && scalar @{$prop->{'bounds'}} >= 6 && exists $prop->{'volume'} && defined $prop->{'volume'}){
									$b1 = $prop->{'bounds'};
									$b1_volume = $prop->{'volume'} - 0;
								}
							}
							unless(defined $b1 && ref $b1 eq 'ARRAY'){
								$b1 = $obj2image->bound($obj_files1);
								&cgi_lib::common::message('$b1='.&cgi_lib::common::encodeJSON($b1,1)) if(defined $b1);
							}
							if(defined $b1 && ref $b1 eq 'ARRAY'){
								$_+=0 for(@$b1);
							}else{
								die __LINE__.":undefined \$bound!!\n";
							}

#							print __LINE__.":\$target_cdi_name=$target_cdi_name\n";
#							print __LINE__.":\$b1=[",join(",",@$b1),"]\n";
#							if(defined $prop){
#								&cgi_lib::common::message('$prop='.&cgi_lib::common::encodeJSON($prop,1));
#							}else{
#								&cgi_lib::common::message('$b1='.&cgi_lib::common::encodeJSON($b1,1));
#							}
							my $error_cnt = 0;
							for(@$b1){
								$error_cnt++ if($_==1 || $_==-1);
							}
							if($error_cnt == scalar @$b1){
								close($TXT);
								unlink qq|$img_prefix.gif| if(-e qq|$img_prefix.gif|);
								foreach my $chk_file (@chk_files){
									unlink $chk_file;
								}
								exit 1;
							}


							if(USE_LARGER_BOX){
								$largerbbox = [];
								foreach my $cdi_name (keys(%STANDARD_BBOX)){

									for(my $i=0;$i<scalar @$b1;$i++){
										if($i<4){
											next;
											#min
											if($STANDARD_BBOX{$cdi_name}->[$i] < $b1->[$i] && (!defined $largerbbox->[$i] || $STANDARD_BBOX{$cdi_name}->[$i] > $largerbbox->[$i])){
												$largerbbox->[$i] = $STANDARD_BBOX{$cdi_name}->[$i];
				#								$largerbbox->[$i+1] = $STANDARD_BBOX{$cdi_name}->[$i+1];
											}
											$i++;
											#max
											if($STANDARD_BBOX{$cdi_name}->[$i] > $b1->[$i] && (!defined $largerbbox->[$i] || $STANDARD_BBOX{$cdi_name}->[$i] < $largerbbox->[$i])){
				#								$largerbbox->[$i-1] = $STANDARD_BBOX{$cdi_name}->[$i-1];
												$largerbbox->[$i] = $STANDARD_BBOX{$cdi_name}->[$i];
											}
										}elsif(
											$cdi_name eq $STANDARD_CDI_NAME[0] ||
											$cdi_name eq $STANDARD_CDI_NAME[1] ||
											$cdi_name eq $STANDARD_CDI_NAME[2]
										){
											#min
											if($STANDARD_BBOX{$cdi_name}->[$i] <= $b1->[$i] && (!defined $largerbbox->[$i] || $STANDARD_BBOX{$cdi_name}->[$i] > $largerbbox->[$i])){
												$largerbbox->[$i] = $STANDARD_BBOX{$cdi_name}->[$i];
											}
											$i++;
											#max
											if($STANDARD_BBOX{$cdi_name}->[$i] > $b1->[$i] && (!defined $largerbbox->[$i] || $STANDARD_BBOX{$cdi_name}->[$i] < $largerbbox->[$i])){
												$largerbbox->[$i] = $STANDARD_BBOX{$cdi_name}->[$i];
											}
										}else{
											#min
											if($STANDARD_BBOX{$cdi_name}->[$i] < $b1->[$i] && (!defined $largerbbox->[$i] || $STANDARD_BBOX{$cdi_name}->[$i] > $largerbbox->[$i])){
												$largerbbox->[$i] = $STANDARD_BBOX{$cdi_name}->[$i];
											}
											$i++;
											#max
											if($STANDARD_BBOX{$cdi_name}->[$i] >= $b1->[$i] && (!defined $largerbbox->[$i] || $STANDARD_BBOX{$cdi_name}->[$i] < $largerbbox->[$i])){
												$largerbbox->[$i] = $STANDARD_BBOX{$cdi_name}->[$i];
											}
										}
									}
								}

								$largerbbox->[4] = $all_bound->[4] unless(defined $largerbbox->[4]);
								$largerbbox->[5] = $all_bound->[5] unless(defined $largerbbox->[5]);

								my $zs = &Math::Round::round($largerbbox->[4]);
								my $ze = &Math::Round::round($largerbbox->[5]);
								my $z_bbox;
								for(my $zr = $zs;$zr<=$ze;$zr++){
									if(defined $z_bbox){

										if(exists $Z_BBOX{$zr} && defined $Z_BBOX{$zr}){
											$z_bbox->{'xmin'} = $Z_BBOX{$zr}->{'xmin'}+0 if(!exists $z_bbox->{'xmin'} || !defined $z_bbox->{'xmin'} || $Z_BBOX{$zr}->{'xmin'}+0 < $z_bbox->{'xmin'}+0);
											$z_bbox->{'xmax'} = $Z_BBOX{$zr}->{'xmax'}+0 if(!exists $z_bbox->{'xmax'} || !defined $z_bbox->{'xmax'} || $Z_BBOX{$zr}->{'xmax'}+0 > $z_bbox->{'xmax'}+0);
											$z_bbox->{'ymin'} = $Z_BBOX{$zr}->{'ymin'}+0 if(!exists $z_bbox->{'ymin'} || !defined $z_bbox->{'ymin'} || $Z_BBOX{$zr}->{'ymin'}+0 < $z_bbox->{'ymin'}+0);
											$z_bbox->{'ymax'} = $Z_BBOX{$zr}->{'ymax'}+0 if(!exists $z_bbox->{'ymax'} || !defined $z_bbox->{'ymax'} || $Z_BBOX{$zr}->{'ymax'}+0 > $z_bbox->{'ymax'}+0);
											$z_bbox->{'zmin'} = $Z_BBOX{$zr}->{'zmin'}+0 if(!exists $z_bbox->{'zmin'} || !defined $z_bbox->{'zmin'} || $Z_BBOX{$zr}->{'zmin'}+0 < $z_bbox->{'zmin'}+0);
											$z_bbox->{'zmax'} = $Z_BBOX{$zr}->{'zmax'}+0 if(!exists $z_bbox->{'zmax'} || !defined $z_bbox->{'zmax'} || $Z_BBOX{$zr}->{'zmax'}+0 > $z_bbox->{'zmax'}+0);
										}
									}else{

										if(exists $Z_BBOX{$zr} && defined $Z_BBOX{$zr}){
											$z_bbox = {
												xmin => $Z_BBOX{$zr}->{'xmin'}+0,
												xmax => $Z_BBOX{$zr}->{'xmax'}+0,
												ymin => $Z_BBOX{$zr}->{'ymin'}+0,
												ymax => $Z_BBOX{$zr}->{'ymax'}+0,
												zmin => $Z_BBOX{$zr}->{'zmin'}+0,
												zmax => $Z_BBOX{$zr}->{'zmax'}+0
											};
										}

	#									print STDERR __LINE__.':'.&Data::Dumper::Dumper($z_bbox);
	#									die __LINE__.":DEBUG\n";
									}
								}
								if(defined $z_bbox){
									$largerbbox->[0] = $z_bbox->{'xmin'} unless(defined $largerbbox->[0]);
									$largerbbox->[1] = $z_bbox->{'xmax'} unless(defined $largerbbox->[1]);
									$largerbbox->[2] = $z_bbox->{'ymin'} unless(defined $largerbbox->[2]);
									$largerbbox->[3] = $z_bbox->{'ymax'} unless(defined $largerbbox->[3]);
									$largerbbox->[4] = $z_bbox->{'zmin'} unless(defined $largerbbox->[4]);
									$largerbbox->[5] = $z_bbox->{'zmax'} unless(defined $largerbbox->[5]);
								}



								for(my $i=0;$i<scalar @$all_bound;$i++){
									$largerbbox->[$i] = $all_bound->[$i] unless(defined $largerbbox->[$i]);
								}
								print __LINE__.":\$largerbbox=[",join(",",@$largerbbox),"]\n";

								my @largerranges = (abs($largerbbox->[0]-$largerbbox->[1]),abs($largerbbox->[2]-$largerbbox->[3]),abs($largerbbox->[4]-$largerbbox->[5]));
								my $fmax = &List::Util::max(@largerranges);

								print __LINE__.":\$fmax=[",$fmax,"]\n";

								my $fzoom = &getYRangeZoom($fmax);

								my $fzoom1 = ($fzoom>0) ? $fzoom-0.1 : $fzoom;

								$largerbboxYRange = &getZoomYRange($fzoom1);

								print __LINE__.":\$largerbboxYRange=[",$fmax,"][",$fzoom,"][",$fzoom1,"][",$largerbboxYRange,"]\n" if(defined $largerbboxYRange);
							}

							my @b1ranges = (abs($b1->[0]-$b1->[1]),abs($b1->[2]-$b1->[3]),abs($b1->[4]-$b1->[5]));
							my $b1max = &List::Util::max(@b1ranges);
							my $b1zoom = &getYRangeZoom($b1max);
							my $b1zoom1 = ($b1zoom>0) ? $b1zoom-0.1 : $b1zoom;
							my $b1YRange = &getZoomYRange($b1zoom1);
							print __LINE__.":\$b1YRange=[",$b1max,"][",$b1zoom,"][",$b1zoom1,"][",$b1YRange,"]\n";

							$tmp_base_path = &BITS::ImageC::get_tmppath(sprintf($tmp_filefmt,$lock_no));
							print __LINE__.":\$tmp_base_path=[$tmp_base_path]\n";
							&File::Path::make_path($tmp_base_path,{verbose => 0, mode => 0777}) unless(-e $tmp_base_path);
							$tmp_img_prefix = &catdir($tmp_base_path,$target_cdi_name);
							print __LINE__.":\$tmp_img_prefix=[$tmp_img_prefix]\n";

							my $bb;
							my $imgsLC;

							push(@$inter_files,$txt_file);
							push(@$inter_files,@$imgsL)  if(defined $imgsL);
							push(@$inter_files,@$imgsM)  if(defined $imgsM);
							push(@$inter_files,@$imgsS)  if(defined $imgsS);
							push(@$inter_files,@$imgsXS) if(defined $imgsXS);
							push(@$inter_files,qq|$img_prefix.gif|);

							my $dest_prefix;
							my $dest_prefixM;
							my $dest_prefixS;
							my $dest_prefixXS;
							if(defined $sizeStrL){
								$dest_prefix = sprintf($gif_prefix_fmt,$img_prefix,$sizeStrL);
							}
							if(defined $sizeStrM){
								$dest_prefixM = sprintf($gif_prefix_fmt,$img_prefix,$sizeStrM);
								$dest_prefix  = $dest_prefixM unless(defined $dest_prefix);
							}
							if(defined $sizeStrS){
								$dest_prefixS = sprintf($gif_prefix_fmt,$img_prefix,$sizeStrS);
								$dest_prefix  = $dest_prefixS unless(defined $dest_prefix);
							}
							if(defined $sizeStrXS){
								$dest_prefixXS = sprintf($gif_prefix_fmt,$img_prefix,$sizeStrXS);
								$dest_prefix   = $dest_prefixXS unless(defined $dest_prefix);
							}

							my $tmp_dest_prefix = sprintf($gif_prefix_fmt,$tmp_img_prefix,$g_img_sizeStr);

							my @PNG_FILES = ();
							my @TARGET_PNG_FILES = ();

							my $target_png_fmt = qq|$tmp_dest_prefix\-%d-target.png|;
							my $larger_png_fmt = qq|$tmp_dest_prefix\-%d-larger.png|;
							my $angle_png_fmt  = qq|$tmp_dest_prefix\-%d.png|;
							my $larger_size = int($g_img_size->[0]*0.4) . 'x' . int($g_img_size->[1]*0.4);

							my %CC_PID;

							my $t0 = [&Time::HiRes::gettimeofday()];

							my $inc = 360/$g_max_azimuth;
							for(my $i=0;$i<360;$i+=$inc){
								my $png_file = sprintf($angle_png_fmt,$i);
								next if(-e $png_file && -s $png_file);

								my $target_png_file = sprintf($target_png_fmt,$i);
								my $larger_png_file = sprintf($larger_png_fmt,$i);
								next unless(-e $target_png_file && -s $target_png_file && -e $larger_png_file && -s $larger_png_file);
								my $cc_pid = fork;
								warn __LINE__.":Cannot fork: $!" unless defined $cc_pid;
								if($cc_pid){
									$CC_PID{$cc_pid} = undef;
								}else{
									&BITS::ImageC::composite_bulk(target_file=>$target_png_file,larger_file=>$larger_png_file,out_file=>$png_file,larger_geometry=>$larger_size,larger_transparent=>'white');
									warn __LINE__.":[$?]:[$!]" if($?);
									exit $? if(defined $cc_pid);
								}
								while(scalar keys(%CC_PID) > $MAX_CHILD){
									foreach my $cc_pid (keys(%CC_PID)){
										if(my $rtn_pid = waitpid($cc_pid,0)){
											delete $CC_PID{$cc_pid} if($rtn_pid>0);
										}
									}
								}
							}
							while(scalar keys(%CC_PID) > 0){
								foreach my $cc_pid (keys(%CC_PID)){
									if(my $rtn_pid = waitpid($cc_pid,0)){
										delete $CC_PID{$cc_pid} if($rtn_pid>0);
									}
								}
							}
							for(my $i=0;$i<360;$i+=$inc){
								my $target_png_file = sprintf($target_png_fmt,$i);
								my $png_file = sprintf($angle_png_fmt,$i);
								push(@PNG_FILES,$png_file) if(-e $png_file && -s $png_file);
								push(@TARGET_PNG_FILES,$target_png_file) if(-e $target_png_file && -s $target_png_file);
							}

							my $elapsed = &Time::HiRes::tv_interval($t0,[&Time::HiRes::gettimeofday()]);
							print __LINE__.':'.$elapsed."\n";

							if(scalar @PNG_FILES < $g_max_azimuth || scalar @TARGET_PNG_FILES < $g_max_azimuth){

								my $t0 = [&Time::HiRes::gettimeofday()];

								print __LINE__.":CALL obj2animgif()\n";
								print __LINE__.":\t\$g_img_size=[".&JSON::XS::encode_json($g_img_size)."]\n";
								print __LINE__.":\t\$obj_files1=[".(defined $obj_files1 && ref $obj_files1 eq 'ARRAY' ? scalar @$obj_files1 : &JSON::XS::encode_json($obj_files1))."]\n";
								print __LINE__.":\t\$obj_files2=[".(defined $obj_files2 && ref $obj_files2 eq 'ARRAY' ? scalar @$obj_files2 : &JSON::XS::encode_json($obj_files2))."]\n" if(defined $obj_files2);
								print __LINE__.":\t\$dest_prefix=[$dest_prefix]\n";
								print __LINE__.":\t\$tmp_dest_prefix=[$tmp_dest_prefix]\n";
								print __LINE__.":\t\$b1YRange=[$b1YRange]\n";
								print __LINE__.":\t\$largerbbox=[".&JSON::XS::encode_json($largerbbox)."]\n" if(defined $largerbbox);
								print __LINE__.":\t\$largerbboxYRange=[$largerbboxYRange]\n" if(defined $largerbboxYRange);

								$bb = $obj2image->obj2animgif($g_img_size,$obj_files1,$obj_files2,$tmp_dest_prefix,$b1YRange,$largerbbox,$largerbboxYRange);
								undef $bb;
								undef $obj2image;
								undef $bp3d_objs;
								undef $obj_files1;
								undef $obj_files2;

								my $elapsed = &Time::HiRes::tv_interval($t0,[&Time::HiRes::gettimeofday()]);
								print __LINE__.':'.$elapsed."\n";
#die __LINE__.":[",$?,"]\n";

								@PNG_FILES = ();
								@TARGET_PNG_FILES = ();

								$t0 = [&Time::HiRes::gettimeofday()];

								for(my $i=0;$i<360;$i+=$inc){
									my $png_file = sprintf($angle_png_fmt,$i);
									next if(-e $png_file && -s $png_file);
									my $target_png_file = sprintf($target_png_fmt,$i);
									next unless(-e $target_png_file && -s $target_png_file);

									if(defined $largerbbox){
										my $larger_png_file;
										$larger_png_file = sprintf($larger_png_fmt,$i);
										next unless(-e $larger_png_file && -s $larger_png_file);

										my $cc_pid = fork;
										warn __LINE__.":Cannot fork: $!" unless defined $cc_pid;
										if($cc_pid){
											$CC_PID{$cc_pid} = undef;
										}else{
											&BITS::ImageC::composite_bulk(target_file=>$target_png_file,larger_file=>$larger_png_file,out_file=>$png_file,larger_geometry=>$larger_size,larger_transparent=>'white');
											warn __LINE__.":[$?]:[$!]" if($?);
											exit $? if(defined $cc_pid);
										}

										while(scalar keys(%CC_PID) > $MAX_CHILD){
											foreach my $cc_pid (keys(%CC_PID)){
												if(my $rtn_pid = waitpid($cc_pid,0)){
													delete $CC_PID{$cc_pid} if($rtn_pid>0);
												}
											}
										}
									}else{
										&File::Copy::copy($target_png_file,$png_file);
									}
								}
								while(scalar keys(%CC_PID) > 0){
									foreach my $cc_pid (keys(%CC_PID)){
										if(my $rtn_pid = waitpid($cc_pid,0)){
											delete $CC_PID{$cc_pid} if($rtn_pid>0);
										}
									}
								}

								for(my $i=0;$i<360;$i+=$inc){
									my $target_png_file = sprintf($target_png_fmt,$i);
									my $png_file = sprintf($angle_png_fmt,$i);
									if(-e $png_file && -s $png_file){
										push(@PNG_FILES,$png_file);
									}else{
										die __LINE__.":Unknown file [$png_file]\n";
									}
									if(-e $target_png_file && -s $target_png_file){
										push(@TARGET_PNG_FILES,$target_png_file);
									}else{
										die __LINE__.":Unknown file [$target_png_file]\n";
									}
								}

								$elapsed = &Time::HiRes::tv_interval($t0,[&Time::HiRes::gettimeofday()]);
								print __LINE__.':'.$elapsed."\n";
#die __LINE__.":[",$?,"]\n";
							}
							else{
								undef $obj2image;
								undef $bp3d_objs;
								undef $obj_files1;
								undef $obj_files2;
							}
#die __LINE__.":[",$?,"]\n";

							$t0 = [&Time::HiRes::gettimeofday()];

							my $cc_pid = fork;
							warn __LINE__.":Cannot fork: $!" unless defined $cc_pid;
							if($cc_pid){
								$CC_PID{$cc_pid} = undef;
							}else{
								my $gif_file = qq|$dest_prefix.gif|;
								&BITS::ImageC::animatedGIF(in_files=>\@PNG_FILES,out_file=>$gif_file,delay=>$g_animated_gif_delay) unless(-e $gif_file && -s $gif_file);
								utime $rep_entry,$rep_entry,$gif_file if(-e $gif_file && -s $gif_file);
								warn __LINE__.":[$?]:[$!]" if($?);
								exit $? if(defined $cc_pid);
							}

							if(defined $sizeStrM && $g_img_sizeStr ne $sizeStrM){
								$cc_pid = fork;
								warn __LINE__.":Cannot fork: $!" unless defined $cc_pid;
								if($cc_pid){
									$CC_PID{$cc_pid} = undef;
								}else{
									my $gif_file = qq|$dest_prefixM.gif|;
									&BITS::ImageC::animatedGIF(in_files=>\@PNG_FILES,out_file=>$gif_file,geometry=>$sizeStrM,delay=>$g_animated_gif_delay) unless(-e $gif_file && -s $gif_file);
									utime $rep_entry,$rep_entry,$gif_file if(-e $gif_file && -s $gif_file);
									warn __LINE__.":[$?]:[$!]" if($?);
									exit $? if(defined $cc_pid);
								}
							}

							if(defined $sizeStrS && $g_img_sizeStr ne $sizeStrS){
								$cc_pid = fork;
								warn __LINE__.":Cannot fork: $!" unless defined $cc_pid;
								if($cc_pid){
									$CC_PID{$cc_pid} = undef;
								}else{
									my $gif_file = qq|$dest_prefixS.gif|;
									&BITS::ImageC::animatedGIF(in_files=>\@TARGET_PNG_FILES,out_file=>$gif_file,geometry=>$sizeStrS,delay=>$g_animated_gif_delay) unless(-e $gif_file && -s $gif_file);
									utime $rep_entry,$rep_entry,$gif_file if(-e $gif_file && -s $gif_file);
									warn __LINE__.":[$?]:[$!]" if($?);
									exit $? if(defined $cc_pid);
								}
							}

							if(defined $sizeStrXS && $g_img_sizeStr ne $sizeStrXS){
								$cc_pid = fork;
								warn __LINE__.":Cannot fork: $!" unless defined $cc_pid;
								if($cc_pid){
									$CC_PID{$cc_pid} = undef;
								}else{
									my $gif_file = qq|$dest_prefixXS.gif|;
									&BITS::ImageC::animatedGIF(in_files=>\@TARGET_PNG_FILES,out_file=>$gif_file,geometry=>$sizeStrXS,delay=>$g_animated_gif_delay) unless(-e $gif_file && -s $gif_file);
									utime $rep_entry,$rep_entry,$gif_file if(-e $gif_file && -s $gif_file);
									warn __LINE__.":[$?]:[$!]" if($?);
									exit $? if(defined $cc_pid);
								}
							}

							while(scalar keys(%CC_PID) > 0){
								foreach my $cc_pid (keys(%CC_PID)){
									if(my $rtn_pid = waitpid($cc_pid,0)){
										delete $CC_PID{$cc_pid} if($rtn_pid>0);
									}
								}
							}

							unlink qq|$img_prefix.gif| if(-e qq|$img_prefix.gif|);
							symlink qq|$target_cdi_name\_$sizeStrM.gif|,qq|$img_prefix.gif| if(-e $imgsM->[0]);
							utime $rep_entry,$rep_entry,qq|$img_prefix.gif| if(-e qq|$img_prefix.gif| && -s qq|$img_prefix.gif|);

							my $angle = 0;
							my $png_file;
							$angle = 0;
							for(my $i=1;$i<=4;$i++){
								my $cc_pid = fork;
								warn __LINE__.":Cannot fork: $!" unless defined $cc_pid;
								if($cc_pid){
									$CC_PID{$cc_pid} = undef;
								}else{
									unless(-e $imgsMAX->[$i]){
										$png_file = sprintf($angle_png_fmt,$angle);
										die __LINE__.":Unknown file [$png_file]\n" unless(-e $png_file);
										&File::Copy::copy($png_file,$imgsMAX->[$i]) if(-e $png_file);
									}
									utime $rep_entry,$rep_entry,$imgsMAX->[$i] if(-e $imgsMAX->[$i] && -s $imgsMAX->[$i]);

									if(defined $sizeStrM && $g_img_sizeStr ne $sizeStrM && defined e $imgsM){
										unless(-e $imgsM->[$i]){
											if(-e $imgsMAX->[$i]){
												&BITS::ImageC::resize(in_file=>$imgsMAX->[$i],geometry=>$sizeStrM,out_file=>$imgsM->[$i]);
											}
										}
										utime $rep_entry,$rep_entry,$imgsM->[$i] if(-e $imgsM->[$i] && -s $imgsM->[$i]);
									}

									my $target_png_file = sprintf($target_png_fmt,$angle);
									if(-e $target_png_file && -s $target_png_file){
										if(defined $sizeStrS && $g_img_sizeStr ne $sizeStrS && defined $imgsS){
											&BITS::ImageC::resize(in_file=>$target_png_file,geometry=>$sizeStrS,out_file=>$imgsS->[$i]) unless(-e $imgsS->[$i] && -s $imgsS->[$i]);
											utime $rep_entry,$rep_entry,$imgsS->[$i] if(-e $imgsS->[$i] && -s $imgsS->[$i]);
										}
										if(defined $sizeStrXS && $g_img_sizeStr ne $sizeStrXS && defined $imgsXS){
											&BITS::ImageC::resize(in_file=>$target_png_file,geometry=>$sizeStrXS,out_file=>$imgsXS->[$i]) unless(-e $imgsXS->[$i] && -s $imgsXS->[$i]);
											utime $rep_entry,$rep_entry,$imgsXS->[$i] if(-e $imgsXS->[$i] && -s $imgsXS->[$i]);
										}
									}
									warn __LINE__.":[$?]:[$!]" if($?);
									exit $? if(defined $cc_pid);
								}
								$angle += 90;
							}
							while(scalar keys(%CC_PID) > 0){
								foreach my $cc_pid (keys(%CC_PID)){
									if(my $rtn_pid = waitpid($cc_pid,0)){
										delete $CC_PID{$cc_pid} if($rtn_pid>0);
									}
								}
							}
#exit;
							$elapsed = &Time::HiRes::tv_interval($t0,[&Time::HiRes::gettimeofday()]);
							print __LINE__.':'.$elapsed."\n";

							for($angle=0;$angle<360;$angle+=$inc){
								$png_file = sprintf($target_png_fmt,$angle);
								unlink $png_file if(-e $png_file);
								$png_file = sprintf($larger_png_fmt,$angle);
								unlink $png_file if(-e $png_file);
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
									zmax => $b1->[5]+0,
									volume => $b1_volume
								};
								print $TXT &JSON::XS::encode_json($b);
							}
							undef $largerbbox if(defined $largerbbox);

							undef $obj_files1;
							undef $obj_files2;

							undef $obj2image;
							undef $bp3d_objs;
						}
						close($TXT);
						utime $rep_entry,$rep_entry,$txt_file if(-e $txt_file && -s $txt_file);
						undef $inter_files if(defined $inter_files);

						utime $rep_entry,$rep_entry,$img_path if(-e $img_path && -d $img_path);

						&File::Path::remove_tree($tmp_base_path) if(defined $tmp_base_path && -e $tmp_base_path);
						undef $tmp_base_path if(defined $tmp_base_path);
						undef $tmp_img_prefix if(defined $tmp_img_prefix);

#					}else{
#						undef $lock_path if(defined $lock_path);
					}
					eval{&unlink_inter_files();};

#					die __LINE__.":[",$?,"]\n";

					exit 0;
				}

			}
		}
	}
}
exit;
