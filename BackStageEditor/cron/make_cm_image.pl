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
	force|f
	target|t=s@
	version|v=s@
/) or exit 1;

$ENV{'AG_DB_HOST'} = $config->{'host'};
$ENV{'AG_DB_PORT'} = $config->{'port'};

my $JSONXS_DEBUG = JSON::XS->new->utf8->indent(1)->canonical(1);

say $JSONXS_DEBUG->encode($config);
#exit;

#use BITS::ReCalc;
use BITS::ArtFile;
use BITS::ImageC;
use BITS::ConceptArtMapModified;

require "webgl_common.pl";
use cgi_lib::common;

use renderer;

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
	IMAGEMAGICK_COLOR_REDUCTION_OPTION => '-quality 95 +dither -colors 256 -depth 8'
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
my $txt_file_lock;
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
	exit unless(defined $display);
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

BEGIN{
	$old_umask = umask(0);
=pod
	unless(exists $ENV{'DISPLAY'} && defined $ENV{'DISPLAY'}){
		my $server_number = DEF_SERVER_NUMBRT;
		$server_number = &getDisplay() if($server_number<0);
		exit unless(defined $server_number);

		if($server_number>0){
			exec qq|xvfb-run -n $server_number -s "-screen 0 640x640x24" $0| if(defined $server_number);
			exit;
		}else{
			$ENV{'DISPLAY'} = qq|:0|;
		}
	}
=cut
	print __LINE__.":BEGIN!!\n";
#	&setDisplay();
	$SIG{'HUP'} = $SIG{'INT'} = $SIG{'QUIT'} = $SIG{'ILL'} = $SIG{'TRAP'} = $SIG{'ABRT'} = $SIG{'BUS'} = $SIG{'FPE'} = $SIG{'KILL'} = $SIG{'USR1'} = $SIG{'SEGV'} = $SIG{'USR2'} = $SIG{'TERM'} = "sigexit";
}
END{
	umask($old_umask);
	unless(defined $is_child){
#		&File::Path::remove_tree($lock_filepath) if(defined $lock_filepath && -e $lock_filepath && -d $lock_filepath);
#		&File::Path::remove_tree($txt_file_lock) if(defined $txt_file_lock && -e $txt_file_lock && -d $txt_file_lock);
		print __LINE__.":IS PARENT END!![".(defined $lock_filepath ? $lock_filepath : "")."][".(defined $txt_file_lock ? $txt_file_lock : "")."]\n";
	}elsif($is_child==$$){
		&File::Path::remove_tree($txt_file_lock) if(defined $txt_file_lock && -e $txt_file_lock && -d $txt_file_lock);
		print __LINE__.":IS CHILD END!![".(defined $lock_filepath ? $lock_filepath : "")."][".(defined $txt_file_lock ? $txt_file_lock : "")."][$$]\n";
	}else{
#		print __LINE__.":IS CHILD CHILD END!![$$]\n";
	}
#	print __LINE__.":END!!\n";
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
	&File::Path::make_path($lock_dirpath,{verbose => 0, mode => 0777});
}

my $tmp_filefmt = qq|$cgi_name-%d|;
my $lock_filefmt = qq|$cgi_name.lock-%d|;
my $lock_no=0;
my $LOCK;
for(;$lock_no<$MAX_PROG;$lock_no++){
	$lock_filepath = &catdir($lock_dirpath,sprintf($lock_filefmt,$lock_no));
	print __LINE__.":\$lock_filepath=[$lock_filepath]\n";
#	last if(!-e $lock_filepath && &File::Path::make_path($lock_filepath,{verbose => 0, mode => 0777}));

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
#my $art_file_fmt = qq|$art_file_prefix/%s-%d%s|;
my $art_file_fmt = qq|$art_file_prefix/%s%s|;

sub load_art_file {
	my %args = (
		reduction => 1.0,
		@_
	);
	my $md_id = $args{'md_id'};
	my $mv_id = $args{'mv_id'};
	my $mr_id = $args{'mr_id'};
	my $reduction = $args{'reduction'};
#	my $dbh = &get_dbh();

	my $obj_files1 = $args{'obj_files1'};
	my $obj_files2 = $args{'obj_files2'};


#	my @FILES;
	my $bp3d_objs = &renderer::new_bp3d_objs();

	if(defined $obj_files1 && ref $obj_files1 eq 'ARRAY' && defined $obj_files2 && ref $obj_files2 eq 'ARRAY'){
		my @FILES = ();
		push(@FILES,@$obj_files1);
		push(@FILES,@$obj_files2);
		foreach my $objfile (@FILES){
			if(ref $objfile eq 'HASH'){
				&BITS::ArtFile::load_art_file_fromDB(dbh=>$dbh,art_id=>$objfile->{'art_id'},hist_serial=>$objfile->{'hist_serial'},art_file_fmt=>$art_file_fmt) unless(-e $objfile->{'path'});
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
	my $art_entry;
	my $hist_serial;

	my $sql=<<SQL;;
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
 (art_id,hist_serial) in (
   select
    art_id,
    art_hist_serial
   from
    concept_art_map
   where
    cm_id in (
      select
       cm_id
      from
       concept_art_map
      where
       cm_use and
       cm_delcause is null and
       (md_id,mv_id,mr_id,cdi_id) in (
           select
            md_id,mv_id,max(mr_id) as mr_id,cdi_id
           from
            concept_art_map
           where
            md_id=$md_id and mv_id=$mv_id and mr_id<=$mr_id
           group by
            md_id,mv_id,cdi_id
        )
    )
   group by
    art_id,art_hist_serial
 )
order by
 hist_timestamp desc
SQL
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	print __LINE__.":\$sth->rows()=[",$sth->rows(),"]\n";
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$art_id, undef);
	$sth->bind_col(++$column_number, \$art_ext, undef);
#	$sth->bind_col(++$column_number, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
	$sth->bind_col(++$column_number, \$art_data_size, undef);
	$sth->bind_col(++$column_number, \$art_entry, undef);
	$sth->bind_col(++$column_number, \$hist_serial, undef);
	while($sth->fetch){
#		next unless(defined $art_id && defined $art_data_size && defined $art_entry && defined $hist_serial);
#		my $objfile = sprintf($art_file_fmt,$art_id,$hist_serial,$art_ext);
		next unless(defined $art_id && defined $art_data_size && defined $art_entry);
		my $objfile = sprintf($art_file_fmt,$art_id,$art_ext);
		my $size = -s $objfile;
		my $mtime = 0;
		$mtime = (stat($objfile))[9] if(-e $objfile);
		unless(-e $objfile && $size == $art_data_size && $mtime>=$art_entry){
			&BITS::ArtFile::load_art_file_fromDB(dbh=>$dbh,art_id=>$art_id,hist_serial=>$hist_serial,art_file_fmt=>$art_file_fmt);
		}
		$bp3d_objs->objReader($objfile,$reduction) if(-e $objfile);
	}
	$sth->finish;
	undef $sth;

	return $bp3d_objs;
}

sub tName2Type {
	my $t_key = shift;

	my $bul_id;
#	if($t_key eq 'bp3d'){
#		$bul_id = 1;
#	}elsif($t_key eq 'isa'){
#		$bul_id = 3;
#	}elsif($t_key eq 'partof'){
#		$bul_id = 4;
#	}

	my $sql = qq|select bul_id from buildup_logic where bul_abbr=lower(?)|;
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute($t_key) or die $dbh->errstr;
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$bul_id, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;

	return $bul_id;
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

#my @TREE = ('bp3d','isa','partof');
#my @TREE = ('isa','partof');
#my @TREE = qw/isa/;
#my @TREE = qw/partof/;
#my @TREE = qw/partof isa/;
#my @TREE = qw/isa/;
my @TREE = ();
if(scalar @TREE == 0){
	my $sql = qq|select bul_abbr from buildup_logic where bul_use|;
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	my $column_number = 0;
	my $bul_abbr;
	$sth->bind_col(++$column_number, \$bul_abbr, undef);
	while($sth->fetch){
		push(@TREE,$bul_abbr) if(defined $bul_abbr);
	}
	$sth->finish;
	undef $sth;
}

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

#my $base_cdi_name = {
my $BASE_CDI_NAME = {
	'bp3d'   => 'FMA20394',
#	'isa'    => 'FMA62955',
	'isa'    => [qw/FMA7163 FMA5018 FMA242789/],
#	'partof' => 'FMA20394',
	'partof' => [qw/FMA7163 FMA5018 FMA242789/],
};

#my $version = qq|3.0|;
#my $tree = qq|bp3d|;
my $copyrightL = qq|$FindBin::Bin/../htdocs/img/copyrightM.png|;
my $copyrightS = qq|$FindBin::Bin/../htdocs/img/copyrightS.png|;

my %STANDARD_BBOX = ();

#my $md_id;
#my $sql = qq|select md_id from model where md_use and md_abbr=?|;
#my $sth = $dbh->prepare($sql) or die $dbh->errstr;
#$sth->execute($model) or die $dbh->errstr;
#my $column_number = 0;
#$sth->bind_col(++$column_number, \$md_id, undef);
#$sth->fetch;
#$sth->finish;
#undef $sth;

my @MD_IDS;

my @USE_CDI_NAMES;
if(exists $config->{'target'} && defined $config->{'target'} && ref $config->{'target'} eq 'ARRAY' && scalar @{$config->{'target'}}){
	foreach my $cdi_name (@{$config->{'target'}}){
		push(@USE_CDI_NAMES, $_) for(split(/[^A-Za-z0-9]/,$cdi_name));
	}
}

if(exists $config->{'version'} && defined $config->{'version'} && ref $config->{'version'} eq 'ARRAY' && scalar @{$config->{'version'}}){
	my $sql = sprintf('select md_id from model_revision where mr_use and mr_version in (%s) group by md_id order by md_id', join(',',map {'?'} @{$config->{'version'}}));
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

	my $md_abbr;
	my $sql = qq|select md_abbr from model where md_id=$md_id|;
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$sth->bind_col(1, \$md_abbr, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;


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
#		my $sql = qq|select mr_version from model_revision where mr_use and md_id=? order by mr_order|;
		my $sql = qq|
select mr.mr_version from model_revision as mr
left join (select * from model_version) as mv on mv.md_id=mr.md_id and mv.mv_id=mr.mv_id
where
 mr.mr_use and
-- mv.mv_publish and
 mv.mv_use and
-- mv.mv_frozen and
 mr.md_id=?
order by
 mv.mv_order,
 mr.mr_order
|;
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute($md_id) or die $dbh->errstr;
		my $column_number = 0;
		my $mr_version;
		$sth->bind_col(++$column_number, \$mr_version, undef);
		while($sth->fetch){
			push(@VERSION,$mr_version) if(defined $mr_version);
		}
		$sth->finish;
		undef $sth;
	}


	foreach my $version (@VERSION){

		print __LINE__.":\$version=[".$version."]\n";

		%STANDARD_BBOX = ();

		my $mv_id;
		my $mr_id;
		my $sql = qq|select mv_id,mr_id from model_revision where md_id=? and mr_version=?|;
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute($md_id,$version) or die $dbh->errstr;
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$mv_id, undef);
		$sth->bind_col(++$column_number, \$mr_id, undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;
		unless(defined $mv_id && defined $mr_id){
			die __LINE__.";Unknown Version!!\n";
		}

		my $ci_id;
		my $cb_id;
		my $mv_publish;
		$sql = qq|select ci_id,cb_id,mv_publish from model_version where md_id=? and mv_id=?|;
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute($md_id,$mv_id) or die $dbh->errstr;
		$column_number = 0;
		$sth->bind_col(++$column_number, \$ci_id, undef);
		$sth->bind_col(++$column_number, \$cb_id, undef);
		$sth->bind_col(++$column_number, \$mv_publish, undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;
		unless(defined $mv_id && defined $mr_id){
			die __LINE__.";Unknown Version!!\n";
		}

		my $change_cdi_ids;
		unless($mv_publish){
#			$change_cdi_ids = &BITS::ReCalc::check(
#				dbh   => $dbh,
#				ci_id => $ci_id,
#				cb_id => $cb_id,
#				md_id => $md_id,
#				mv_id => $mv_id,
#				mr_id => $mr_id,
#			);

			$change_cdi_ids = &BITS::ConceptArtMapModified::exec(
				dbh => $dbh,
				md_id => $md_id,
				mv_id => $mv_id,
				mr_id => $mr_id
			);

		}
#			die __LINE__.":\n";

		my($DEF_COLOR_ART,$DEF_COLOR) = &BITS::ArtFile::get_all_colors(dbh=>$dbh,md_id=>$md_id,mv_id=>$mv_id,mr_id=>$mr_id,ci_id=>$ci_id,cb_id=>$cb_id);

		foreach my $cdi_name (@STANDARD_CDI_NAME){
			my($art_xmin,$art_xmax,$art_ymin,$art_ymax,$art_zmin,$art_zmax) = &BITS::ArtFile::get_art_file_bbox(dbh=>$dbh,md_id=>$md_id,mv_id=>$mv_id,mr_id=>$mr_id,ci_id=>$ci_id,cb_id=>$cb_id,bul_id=>0,cdi_name=>$cdi_name);
			next unless(defined $art_xmin && defined $art_xmax && defined $art_ymin && defined $art_ymax && defined $art_zmin && defined $art_zmax);
			push(@{$STANDARD_BBOX{$cdi_name}},$art_xmin+0,$art_xmax+0,$art_ymin+0,$art_ymax+0,$art_zmin+0,$art_zmax+0);
			print __LINE__.":[$cdi_name]=[",&JSON::XS::encode_json($STANDARD_BBOX{$cdi_name}),"]\n";
		}



		my %Z_BBOX = ();

		$sql =<<SQL;
select
 z,
 min(xmin) as xmin,
 max(xmax) as xmax,
 min(ymin) as ymin,
 max(ymax) as ymax,
 min(zmin) as zmin,
 max(zmax) as zmax
from (
(
 select
  round(art_zmin) as z,
  min(art_xmin) as xmin,
  max(art_xmax) as xmax,
  min(art_ymin) as ymin,
  max(art_ymax) as ymax,
  min(art_zmin) as zmin,
  max(art_zmax) as zmax
 from
  history_art_file
 where
  (art_id,hist_serial) in (
    select
     art_id,art_hist_serial
    from
     concept_art_map
    where
     cm_use and
     cm_delcause is null and
     (md_id,mv_id,mr_id,cdi_id) in (select md_id,mv_id,max(mr_id) as mr_id,cdi_id from concept_art_map where md_id=$md_id and mv_id=$mv_id and mr_id<=$mr_id group by md_id,mv_id,cdi_id)
  )
 group by z
)
union
(
 select
  round(art_zmax) as z,
  min(art_xmin) as xmin,
  max(art_xmax) as xmax,
  min(art_ymin) as ymin,
  max(art_ymax) as ymax,
  min(art_zmin) as zmin,
  max(art_zmax) as zmax
 from
  history_art_file
 where
  (art_id,hist_serial) in (
    select
     art_id,art_hist_serial
    from
     concept_art_map
    where
     cm_use and
     cm_delcause is null and
     (md_id,mv_id,mr_id,cdi_id) in (select md_id,mv_id,max(mr_id) as mr_id,cdi_id from concept_art_map where md_id=$md_id and mv_id=$mv_id and mr_id<=$mr_id group by md_id,mv_id,cdi_id)
  )
 group by z
)
) a
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

		foreach my $tree (@TREE){

			print __LINE__.":\$tree=$tree\n";

			my $bul_id = &tName2Type($tree);

			my $sth_cdi = $dbh->prepare(qq|select cdi_name from concept_data_info as cdi where cdi_delcause is null and cdi.ci_id=$ci_id and cdi.cdi_id=?|) or die $dbh->errstr;


			my $base_cdi_name;
			my $sth_tbp = $dbh->prepare(qq|select cdi_id from thumbnail_background_part where md_id=$md_id and mv_id=$mv_id and ci_id=$ci_id and tbp_use and tbp_delcause is null|) or die $dbh->errstr;
			$sth_tbp->execute() or die $dbh->errstr;
			$column_number = 0;
			my $cdi_id;
			$sth_tbp->bind_col(++$column_number, \$cdi_id, undef);
			while($sth_tbp->fetch){
				$sth_cdi->execute($cdi_id) or die $dbh->errstr;
				$column_number = 0;
				my $cdi_name;
				$sth_cdi->bind_col(++$column_number, \$cdi_name, undef);
				$sth_cdi->fetch;
				$sth_cdi->finish;
				next unless(defined $cdi_name);
				$base_cdi_name = {} unless(defined $base_cdi_name);
				$base_cdi_name->{$tree} = [] unless(defined $base_cdi_name->{$tree});
				push(@{$base_cdi_name->{$tree}},$cdi_name);
			}
			$sth_tbp->finish;
			undef $sth_tbp;

			$base_cdi_name = {} unless(defined $base_cdi_name);
			$base_cdi_name->{$tree} = &Clone::clone($BASE_CDI_NAME->{$tree}) unless(defined $base_cdi_name->{$tree});


			my $base_art_files;
			if(ref $base_cdi_name->{$tree} eq 'ARRAY'){
				foreach my $cdi_name (@{$base_cdi_name->{$tree}}){
					my $art_files = &BITS::ArtFile::get_art_file(dbh=>$dbh,md_id=>$md_id,mv_id=>$mv_id,mr_id=>$mr_id,ci_id=>$ci_id,cb_id=>$cb_id,bul_id=>0,cdi_name=>$cdi_name);
					push(@$base_art_files,@$art_files) if(defined $art_files && ref $art_files eq 'ARRAY');
					undef $art_files;
				}
			}else{
				my $art_files = &BITS::ArtFile::get_art_file(dbh=>$dbh,md_id=>$md_id,mv_id=>$mv_id,mr_id=>$mr_id,ci_id=>$ci_id,cb_id=>$cb_id,bul_id=>0,cdi_name=>$base_cdi_name->{$tree});
				push(@$base_art_files,@$art_files) if(defined $art_files && ref $art_files eq 'ARRAY');
				undef $art_files;

			}

			unless(defined $base_art_files && ref $base_art_files eq 'ARRAY'){
#				my $sth = $dbh->prepare(qq|select cdi_name,bul_id from view_buildup_tree where cdi_pid is null and but_delcause is null and ci_id=? and cb_id=? and bul_id=?|) or die $dbh->errstr;
				my $sth = $dbh->prepare(qq|select cdi_name,bul_id from view_buildup_tree where cdi_pid is null and ci_id=? and cb_id=? and bul_id=?|) or die $dbh->errstr;
				$sth->execute($ci_id,$cb_id,$bul_id) or die $dbh->errstr;
				my $column_number = 0;
				my $cdi_name;
				my $temp_cdi_name;
				$sth->bind_col(++$column_number, \$cdi_name, undef);
				while($sth->fetch){
					$temp_cdi_name->{$cdi_name} = undef
				}
				$sth->finish;
				undef $sth;
				if(defined $temp_cdi_name && ref $temp_cdi_name eq 'HASH'){
					foreach my $cdi_name (keys %$temp_cdi_name){
						my $art_files = &BITS::ArtFile::get_art_file(dbh=>$dbh,md_id=>$md_id,mv_id=>$mv_id,mr_id=>$mr_id,ci_id=>$ci_id,cb_id=>$cb_id,bul_id=>0,cdi_name=>$cdi_name);
						push(@$base_art_files,@$art_files) if(defined $art_files && ref $art_files eq 'ARRAY');
						undef $art_files;

					}
				}
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

			($rep_xmin,$rep_xmax,$rep_ymin,$rep_ymax,$rep_zmin,$rep_zmax) = &BITS::ArtFile::get_art_file_bbox(dbh=>$dbh,md_id=>$md_id,mv_id=>$mv_id,mr_id=>$mr_id,ci_id=>$ci_id,cb_id=>$cb_id,bul_id=>$bul_id);
			next unless(defined $rep_xmin && defined $rep_xmax && defined $rep_ymin && defined $rep_ymax && defined $rep_zmin && defined $rep_zmax);
			my $all_bound = [$rep_xmin+0,$rep_xmax+0,$rep_ymin+0,$rep_ymax+0,$rep_zmin+0,$rep_zmax+0];

			my @CDI_NAMES = ();

			if(defined $change_cdi_ids){

#				print STDERR __LINE__,':'.&Data::Dumper::Dumper($change_cdi_ids);
#				die __LINE__.":DEBUG\n";

				my $sql_cmm = qq|
select EXTRACT(EPOCH FROM cm_modified) as cm_modified from concept_art_map_modified where (ci_id,cb_id,md_id,mv_id,mr_id,bul_id,cdi_id) in (
 select
  ci_id,cb_id,md_id,mv_id,max(mr_id) as mr_id,bul_id,cdi_id
 from
  concept_art_map_modified
 where
  ci_id=$ci_id and
  cb_id=$cb_id and
  md_id=$md_id and
  mv_id=$mv_id and
  mr_id<=$mr_id and
  bul_id=$bul_id
 group by
  ci_id,cb_id,md_id,mv_id,bul_id,cdi_id
) and cdi_id=?|;
				my $sth_cmm = $dbh->prepare($sql_cmm) or die $dbh->errstr;

				my $sth_cd = $dbh->prepare(qq|select EXTRACT(EPOCH FROM GREATEST(cd_entry,seg_entry)) as cd_entry,seg_thum_fgcolor from view_concept_data where cd_delcause is null and ci_id=$ci_id and cb_id=$cb_id and cdi_id=?|) or die $dbh->errstr;

				foreach my $cdi_id (keys(%$change_cdi_ids)){
#					next unless(exists $change_cdi_ids->{$cdi_id}->{$bul_id});
					next unless(exists $change_cdi_ids->{$cdi_id});

					$sth_cdi->execute($cdi_id) or die $dbh->errstr;
					my $cdi_name;
					$sth_cdi->bind_col(1, \$cdi_name, undef);
					$sth_cdi->fetch;
					$sth_cdi->finish;
					next unless(defined $cdi_name);

#					my $rep_delcause = (defined $change_cdi_ids->{$cdi_id}->{$bul_id} && $change_cdi_ids->{$cdi_id}->{$bul_id} =~ /^delete/) ? 'DELETE' : undef;
					my $rep_delcause = (exists $change_cdi_ids->{$cdi_id} && defined $change_cdi_ids->{$cdi_id}->{'cm_delcause'}) ? 'DELETE' : undef;
					my $cm_modified;
					unless(defined $rep_delcause){
						$sth_cmm->execute($cdi_id) or die $dbh->errstr;
						$sth_cmm->bind_col(1, \$cm_modified, undef);
						$sth_cmm->fetch;
						$sth_cmm->finish;
					}

#					unless(defined $cm_modified){
#						print STDERR __LINE__.qq|:\$rep_delcause=[$rep_delcause]\n|;
#						print STDERR __LINE__.qq|:\$cdi_name=[$cdi_name],\$cdi_id=[$cdi_id],\$cm_modified=[$cm_modified]\n|;
#						print STDERR __LINE__.qq|:\$sql_cmm=[$sql_cmm]\n|;
#						die __LINE__."\n";
#					}

					my $cd_entry;
					my $seg_thum_fgcolor;
					$sth_cd->execute($cdi_id) or die $dbh->errstr;
					$sth_cd->bind_col(1, \$cd_entry, undef);
					$sth_cd->bind_col(2, \$seg_thum_fgcolor, undef);
					$sth_cd->fetch;
					$sth_cd->finish;

					if(defined $cm_modified && defined $cd_entry){
						$cm_modified = $cd_entry if($cm_modified < $cd_entry);
					}elsif(!defined $cm_modified && defined $cd_entry){
						$cm_modified = $cd_entry;
					}

					my $rep_entry = defined $cm_modified ? $cm_modified : time;
					my $lt = localtime($rep_entry);

					push(@CDI_NAMES,{
						cdi_name     => $cdi_name,
						rep_delcause => $rep_delcause,
						md_abbr      => $md_abbr,
						mr_version   => $version,
						rep_entry    => $rep_entry,
						rep_entry_str => $lt->strftime('%Y-%m-%d %H:%M:%S'),
						rep_ci_id    => $ci_id,
						rep_cb_id    => $cb_id,
						rep_color    => $seg_thum_fgcolor,
						bul_id       => $bul_id,
					});
				}
				undef $sth_cmm;

#				print STDERR __LINE__,':'.&Data::Dumper::Dumper(\@CDI_NAMES);
#				next;
#				die __LINE__.":DEBUG\n";
#				print STDERR __LINE__.':'.&Data::Dumper::Dumper(\@CDI_NAMES);
			}

			undef $sth_cdi;

#				die __LINE__.":\n";

#					die __LINE__.':'.&Data::Dumper::Dumper($t_b_id) if($target_cdi_name eq 'FMA72706');

			#DEBUG

			print STDERR __LINE__.':$change_cdi_ids='.(defined $change_cdi_ids ? 1 : 0)."\n";
			print STDERR __LINE__.':@CDI_NAMES='.(scalar @CDI_NAMES)."\n";

			if(defined $change_cdi_ids || scalar @CDI_NAMES == 0){
				my %EXISTS_CDI = ();
				%EXISTS_CDI = map {$_=>undef} @CDI_NAMES if(defined $change_cdi_ids && scalar @CDI_NAMES);

				my $rep_primitive;
				my $forcing;
#プリミティブを再生成する為
#				if($bul_id==3){
#					$rep_primitive = 1;
#					$forcing = 1;
#				}

				my $all_map_cdi_names = &BITS::ArtFile::get_all_map_cdi_names(dbh=>$dbh,md_id=>$md_id,mv_id=>$mv_id,mr_id=>$mr_id,ci_id=>$ci_id,cb_id=>$cb_id,bul_id=>$bul_id,rep_primitive=>$rep_primitive,forcing=>$forcing);
#				print STDERR __LINE__.':'.&Data::Dumper::Dumper($all_map_cdi_names);
#				print STDERR __LINE__.':$all_map_cdi_names='.(defined $all_map_cdi_names ? (&cgi_lib::common::encodeJSON($all_map_cdi_names,1)) : 0)."\n";

#				print STDERR __LINE__.':'.Dumper($all_map_cdi_names)."\n";
#				die __LINE__.":\n";

				my $all_unmap_cdi_names = &BITS::ArtFile::get_all_unmap_cdi_names(dbh=>$dbh,md_id=>$md_id,mv_id=>$mv_id,mr_id=>$mr_id,ci_id=>$ci_id,cb_id=>$cb_id,bul_id=>$bul_id,all_map_cdi_names=>$all_map_cdi_names) if($lock_no==0 && defined $all_map_cdi_names);
				if(defined $all_unmap_cdi_names){
#					print STDERR __LINE__.':'.&Data::Dumper::Dumper($all_unmap_cdi_names);
					foreach my $cdi_name (keys(%$all_unmap_cdi_names)){
						next if(exists $EXISTS_CDI{$cdi_name});
						push(@CDI_NAMES,{
							cdi_name     => $cdi_name,
							rep_delcause => 'DELETE',
							md_abbr      => $md_abbr,
							mr_version   => $version,
							rep_entry    => time,
							rep_ci_id    => $ci_id,
							rep_cb_id    => $cb_id,
							bul_id       => $bul_id,
						});
#						$EXISTS_CDI{$cdi_name} = undef;
					}
				}
				if(defined $all_map_cdi_names){
#					print STDERR __LINE__.':'.&Data::Dumper::Dumper($all_map_cdi_names);

					my $sql_cmm = qq|
select
 cdi.cdi_name,
 EXTRACT(EPOCH FROM max(cm_modified)) as cm_modified
from
 concept_art_map_modified as cmm
left join (
 select * from concept_data_info
) as cdi on cdi.ci_id=cmm.ci_id and cdi.cdi_id=cmm.cdi_id
where
 (cmm.ci_id,cmm.cb_id,cmm.md_id,cmm.mv_id,cmm.mr_id,cmm.bul_id,cmm.cdi_id) in (
 select
  ci_id,cb_id,md_id,mv_id,max(mr_id) as mr_id,bul_id,cdi_id
 from
  concept_art_map_modified
 where
  ci_id=$ci_id and
  cb_id=$cb_id and
  md_id=$md_id and
  mv_id=$mv_id and
  mr_id<=$mr_id
  and bul_id=$bul_id
 group by
  ci_id,cb_id,md_id,mv_id,bul_id,cdi_id
)
group by cdi.cdi_name
|;
#					print STDERR __LINE__.":\$sql_cmm=[$sql_cmm]\n";
					my $sth_cmm = $dbh->prepare($sql_cmm) or die $dbh->errstr;
					$sth_cmm->execute() or die $dbh->errstr;
					my %CMM_TIME = ();
					my $cdi_name;
					my $cm_modified;
					my $column_number = 0;
					$sth_cmm->bind_col(++$column_number, \$cdi_name, undef);
					$sth_cmm->bind_col(++$column_number, \$cm_modified, undef);
					while($sth_cmm->fetch){
						next unless(defined $cdi_name);
						$CMM_TIME{$cdi_name} = $cm_modified;
					}
					$sth_cmm->finish;
					undef $sth_cmm;


					foreach my $cdi_name (keys(%$all_map_cdi_names)){
#						print STDERR __LINE__.":\$cdi_name=[$cdi_name]\n";
						next if(exists $EXISTS_CDI{$cdi_name});
#						print STDERR __LINE__.":\$cdi_name=[$cdi_name]\n";

						my $cm_modified = exists $CMM_TIME{$cdi_name} && defined $CMM_TIME{$cdi_name} ? $CMM_TIME{$cdi_name} : undef;

#						my $rep_entry = (ref  $all_map_cdi_names->{$cdi_name}->{$bul_id} eq 'HASH' ? $all_map_cdi_names->{$cdi_name}->{$bul_id}->{'entry'} : $all_map_cdi_names->{$cdi_name}->{$bul_id});
						my $rep_entry = (ref  $all_map_cdi_names->{$cdi_name} eq 'HASH' ? $all_map_cdi_names->{$cdi_name}->{'entry'} : $all_map_cdi_names->{$cdi_name});

#						$rep_entry = $cm_modified if(defined $cm_modified && $rep_entry < $cm_modified);
						$rep_entry = $cm_modified if(defined $cm_modified);

						push(@CDI_NAMES,{
							cdi_name     => $cdi_name,
							rep_delcause => undef,
							md_abbr      => $md_abbr,
							mr_version   => $version,
							rep_entry    => $rep_entry,
							rep_ci_id    => $ci_id,
							rep_cb_id    => $cb_id,
#							rep_color    => (ref  $all_map_cdi_names->{$cdi_name}->{$bul_id} eq 'HASH' ? $all_map_cdi_names->{$cdi_name}->{$bul_id}->{'seg_thum_fgcolor'} : undef),
							rep_color    => (ref  $all_map_cdi_names->{$cdi_name} eq 'HASH' ? $all_map_cdi_names->{$cdi_name}->{'seg_thum_fgcolor'} : undef),
							bul_id       => $bul_id,
						});

						$EXISTS_CDI{$cdi_name} = undef;
					}
				}
			}

#			print STDERR __LINE__.':'.&Data::Dumper::Dumper(\@CDI_NAMES);
#			next;

			my %CACHE_JSON;

			foreach my $t_b_id (@CDI_NAMES){
				my $target_cdi_name = $t_b_id->{'cdi_name'};
				my $md_abbr = $t_b_id->{'md_abbr'};
#				my $mr_version = $t_b_id->{'mr_version'};
				my $mr_version = $version;
				my $rep_ci_id = $t_b_id->{'rep_ci_id'};
				my $rep_cb_id = $t_b_id->{'rep_cb_id'};
				my $rep_entry = $t_b_id->{'rep_entry'};
				my $rep_delcause = $t_b_id->{'rep_delcause'};
				my $rep_color = $t_b_id->{'rep_color'};

				if(scalar @USE_CDI_NAMES){
					next unless(scalar grep {$_ eq $target_cdi_name} @USE_CDI_NAMES);
				}
				print __LINE__.":\$rep_color=[".$rep_color."]\n" if(defined $rep_color);


				$rep_entry = $tbp_max_enter if(defined $tbp_max_enter && $tbp_max_enter>$rep_entry);

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

				my($img_prefix,$img_path) = &getCmImagePrefix($mr_version,$bul_id,$target_cdi_name);
#				my($img_prefix,$img_path) = &getCmImagePrefix($mr_version,undef,$target_cdi_name);

#				my $cache_json_base_path = sprintf(qq|/bp3d/cache_fma/%s/common|,$mr_version);
				my $cache_json_base_path = &catdir(CACHE_FMA_PATH,$mr_version,'common','*',$rep_ci_id,$rep_cb_id,$md_id,$mv_id,$mr_id,$bul_id);
				unless(exists $CACHE_JSON{$cache_json_base_path}){
					$CACHE_JSON{$cache_json_base_path} = $CACHE_JSON{$cache_json_base_path} || {};
					if(open(my $CMD,qq{find $cache_json_base_path -name "*.json" 2> /dev/null |})){
						while(<$CMD>){
							chomp;
							next unless(-e $_);
							my $basename = &File::Basename::basename($_,".json");
							$CACHE_JSON{$cache_json_base_path}->{$basename} = $CACHE_JSON{$cache_json_base_path}->{$basename} || {};
							$CACHE_JSON{$cache_json_base_path}->{$basename}->{$_} = undef;
						}
						close($CMD);
					}
				}

				&File::Path::make_path($img_path,{verbose => 0, mode => 0777}) unless(-e $img_path);

#				my $img_prefix = &catdir($img_path,$target_cdi_name);
				my $txt_file = qq|$img_prefix.txt|;
#				print __LINE__.":\$txt_file=[",$txt_file,"][",(-e $txt_file ? 1 : 0),"][",(-s $txt_file),"]\n";

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
				push(@chk_files,@$imgsL);
				push(@chk_files,@$imgsM);
				push(@chk_files,@$imgsS);
				push(@chk_files,@$imgsXS);

				if(defined $t_b_id->{'rep_delcause'} || scalar @USE_CDI_NAMES || $config->{'force'}){
					unlink qq|$img_prefix.gif|;# if(-e qq|$img_prefix.gif|);	#リンク元が存在しない場合を考慮する
					foreach my $chk_file (@chk_files){
#						next unless(-e $chk_file);	#リンク元が存在しない場合を考慮する
#						say __LINE__.":unlink:[$chk_file]";
						unlink $chk_file;
					}
#die "DEBUG";
#					die __LINE__.':'.&Data::Dumper::Dumper($t_b_id) if($target_cdi_name eq 'FMA72706');

					if(exists $CACHE_JSON{$cache_json_base_path} && exists $CACHE_JSON{$cache_json_base_path}->{$target_cdi_name}){
						foreach (sort keys(%{$CACHE_JSON{$cache_json_base_path}->{$target_cdi_name}})){
							next unless(-e $_);
							unlink $_;
							print __LINE__.":unlink:[$_]\n";
						}
					}

					next if(defined $t_b_id->{'rep_delcause'});
				}
				say __LINE__.":\$txt_file=[",$txt_file,"][",(-e $txt_file ? (-s $txt_file) : 0),"]" if(defined $txt_file);

#				shift @chk_files;

#				my $chk = (-l $txt_file) ? 1 : undef;
				my $chk;
				my $max_mtime = 0;
				unless(defined $chk){
					foreach my $chk_file (@chk_files){
						my $chk_mtime = -e $chk_file ? (stat($chk_file))[9] : 0;
						$max_mtime = $chk_mtime if($max_mtime<$chk_mtime);
						if(-e $chk_file && -s $chk_file && $chk_mtime>=floor($rep_entry)){
							utime $rep_entry,$rep_entry,$chk_file if($chk_mtime>floor($rep_entry));
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

				if(exists $CACHE_JSON{$cache_json_base_path} && exists $CACHE_JSON{$cache_json_base_path}->{$target_cdi_name}){
					foreach (sort keys(%{$CACHE_JSON{$cache_json_base_path}->{$target_cdi_name}})){
						next unless(-e $_ && (stat($_))[9]<$max_mtime);
						unlink $_;
						print __LINE__.":unlink:[$_]\n";
					}
				}

				next unless(defined $chk);



				my $art_files = &BITS::ArtFile::get_art_file(dbh=>$dbh,md_id=>$md_id,mv_id=>$mv_id,mr_id=>$mr_id,ci_id=>$ci_id,cb_id=>$cb_id,bul_id=>$bul_id,cdi_name=>$target_cdi_name);
				unless(defined $art_files && ref $art_files eq 'ARRAY' && scalar @$art_files){
					undef $art_files;
					@chk_files = ();
					next;
				}
				undef $art_files;

#				unshift(@chk_files,$txt_file);


				$txt_file_lock = qq|$txt_file.lock|;
#				print __LINE__.":txt_file_lock:[$txt_file_lock]\n";
#				if(mkdir($txt_file_lock)){
#					print __LINE__.":mkdir:[OK]\n";
#				}else{
#					print __LINE__.":mkdir:[NG]\n";
#				}
#				if(&File::Path::make_path($txt_file_lock,{verbose => 0, mode => 0777})){
				if(mkdir($txt_file_lock,0777)){
#					print __LINE__.":make_path:[OK]\n";
				}else{
					undef $txt_file_lock;
					next;
				}
#					exit(1);
#				print __LINE__.":remove_tree:[",&File::Path::remove_tree($txt_file_lock),"]\n" if(-e $txt_file_lock && -d $txt_file_lock);


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

							print __LINE__.":[$md_id,$mv_id,$mr_id,$target_cdi_name]\n";


							unlink qq|$img_prefix.gif| if(-e qq|$img_prefix.gif|);
							foreach my $chk_file (@chk_files){
								next if($chk_file eq $txt_file);
								unlink $chk_file;
							}

							my $obj_files1;
							my $obj_files2 = [];

							my %use_objs;

#							my $sql_cm = qq|select cdi_name from view_concept_art_map WHERE md_id=? AND mv_id=? AND mr_id=? AND art_id=? AND art_hist_serial=? AND cm_use AND cm_delcause IS NULL|;
#							my $sth_cm = $dbh->prepare($sql_cm) or die $dbh->errstr;
							my $use_bp3d_color;

							my $art_files = &BITS::ArtFile::get_art_file(dbh=>$dbh,md_id=>$md_id,mv_id=>$mv_id,mr_id=>$mr_id,ci_id=>$ci_id,cb_id=>$cb_id,bul_id=>$bul_id,cdi_name=>$target_cdi_name);
							if(defined $art_files && ref $art_files eq 'ARRAY'){
#&cgi_lib::common::message($art_files);
								foreach my $art_file (@$art_files){
									my $art_id = $art_file->{'art_id'};
									my $art_ext = $art_file->{'art_ext'};
									my $art_hist_serial = $art_file->{'hist_serial'};

#									next unless(defined $art_id && defined $art_ext && defined $art_hist_serial);
#									my $objfile = sprintf($art_file_fmt,$art_id,$art_hist_serial,$art_ext);
									next unless(defined $art_id && defined $art_ext);
									my $objfile = sprintf($art_file_fmt,$art_id,$art_ext);
#									print STDERR __LINE__.":\$objfile=[$objfile]\n";
									&BITS::ArtFile::load_art_file_fromDB(dbh=>$dbh,art_id=>$art_id,hist_serial=>$art_hist_serial,art_file_fmt=>$art_file_fmt) unless(-e $objfile);
									next unless(-e $objfile);

									my $color;
									if(USE_BP3D_COLOR){
#										if(exists $DEF_COLOR_ART->{$art_id} && exists $DEF_COLOR_ART->{$art_id}->{$art_hist_serial} && ref $DEF_COLOR_ART->{$art_id}->{$art_hist_serial} eq 'ARRAY'){
										if(exists $DEF_COLOR_ART->{$art_id} && defined $DEF_COLOR_ART->{$art_id} && ref $DEF_COLOR_ART->{$art_id} eq 'ARRAY'){
#											push(@$color,@{$DEF_COLOR_ART->{$art_id}->{$art_hist_serial}});
											push(@$color,@{$DEF_COLOR_ART->{$art_id}});
											$use_bp3d_color = 1;
#											die __LINE__.':'.&Data::Dumper::Dumper($color)."\n";
										}else{
#											print STDERR __LINE__.":Unknown color [$art_id][$art_hist_serial]\n";
											print STDERR __LINE__.":Unknown color [$art_id]\n";
										}
									}


									push(@$obj_files1,{
										path => $objfile,
										color => $color,
										art_id=> $art_id,
#										hist_serial=>$art_hist_serial,
										art_ext=>$art_ext
									});
									$use_objs{$objfile} = undef;
								}
							}else{
								close($TXT);
								unlink $txt_file if(-z $txt_file);
								die __LINE__.":undefined \$art_files=[$art_files]!!\n";
							}


#							%use_objs = map {$_->{'path'}=>undef} @$obj_files1;
							if(defined $obj_files1 && ref $obj_files1 eq 'ARRAY'){
								print __LINE__.":obj_files1=[",(scalar @$obj_files1),"]\n";
							}else{
								close($TXT);
								unlink $txt_file if(-z $txt_file);
								die __LINE__.":undefined \$obj_files1=[$obj_files1]!!\n";
#								print __LINE__.":undefined \$obj_files1!!\n";
#								exit(0);
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

							if(defined $base_art_files && ref $base_art_files eq 'ARRAY'){
								my $color;
								push(@$color,@$DEF_COLOR) if(defined $DEF_COLOR && ref $DEF_COLOR eq 'ARRAY');

								foreach my $art_file (@$base_art_files){
									my $art_id = $art_file->{'art_id'};
									my $art_ext = $art_file->{'art_ext'};
									my $art_hist_serial = $art_file->{'hist_serial'};

#									next unless(defined $art_id && defined $art_ext && defined $art_hist_serial);
#									my $objfile = sprintf($art_file_fmt,$art_id,$art_hist_serial,$art_ext);

									next unless(defined $art_id && defined $art_ext);
									my $objfile = sprintf($art_file_fmt,$art_id,$art_ext);

									next if(exists $use_objs{$objfile});

									&BITS::ArtFile::load_art_file_fromDB(dbh=>$dbh,art_id=>$art_id,hist_serial=>$art_hist_serial,art_file_fmt=>$art_file_fmt) unless(-e $objfile);
									next unless(-e $objfile);

									push(@$obj_files2,{
										path => $objfile,
										color => $color,
										art_id=> $art_id,
#										hist_serial=>$art_hist_serial,
										art_ext=>$art_ext
									});
									$use_objs{$objfile} = undef;
								}
							}else{
								die __LINE__.":undefined \$base_art_files=[$base_art_files]!!\n";
							}

							print __LINE__.":obj_files2=[",(scalar @$obj_files2),"]\n" if(defined $obj_files2);

							my $bp3d_objs = &load_art_file(md_id=>$md_id,mv_id=>$mv_id,mr_id=>$mr_id,obj_files1=>$obj_files1,obj_files2=>$obj_files2);
							my $obj2image = &renderer::new_obj2image($bp3d_objs,1);
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
							my $b1 = $obj2image->bound($obj_files1);
							$_+=0 for(@$b1);

			#				next unless($b1->[4] >= $STANDARD_BBOX{$STANDARD_CDI_NAME[0]}->[4]);#頭の部分
			#				next unless($b1->[4] >= $STANDARD_BBOX{$STANDARD_CDI_NAME[1]}->[4]);#頸の部分
			#				next unless($b1->[5] <= $STANDARD_BBOX{$STANDARD_CDI_NAME[4]}->[5]);#短趾屈筋の部分
			#				next unless($b1->[5] <= $STANDARD_BBOX{$STANDARD_CDI_NAME[4]}->[5]);#足の部分

#							print __LINE__.":\$target_cdi_name=$target_cdi_name\n";
#							print __LINE__.":\$b1=[",join(",",@$b1),"]\n";

							&cgi_lib::common::message("\$target_cdi_name=$target_cdi_name");
							&cgi_lib::common::message('$b1='.&cgi_lib::common::encodeJSON($b1,1));
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

							my $largerbboxYRange = &getZoomYRange($fzoom1);

							print __LINE__.":\$largerbboxYRange=[",$fmax,"][",$fzoom,"][",$fzoom1,"][",$largerbboxYRange,"]\n";

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
							push(@$inter_files,@$imgsL);
							push(@$inter_files,@$imgsM);
							push(@$inter_files,@$imgsS);
							push(@$inter_files,@$imgsXS);
							push(@$inter_files,qq|$img_prefix.gif|);

#def obj2animgif(size,obj_files1,obj_files2,img_files,yRange,largerbbox,largerbboxYRange):

							my $dest_prefix = sprintf($gif_prefix_fmt,$img_prefix,$sizeStrL);
							my $dest_prefixM = sprintf($gif_prefix_fmt,$img_prefix,$sizeStrM);
							my $dest_prefixS = sprintf($gif_prefix_fmt,$img_prefix,$sizeStrS);
							my $dest_prefixXS = sprintf($gif_prefix_fmt,$img_prefix,$sizeStrXS);

							my $tmp_dest_prefix = sprintf($gif_prefix_fmt,$tmp_img_prefix,$sizeStrL);

							my @PNG_FILES = ();
							my @TARGET_PNG_FILES = ();

							my $target_png_fmt = qq|$tmp_dest_prefix\-%d-target.png|;
							my $larger_png_fmt = qq|$tmp_dest_prefix\-%d-larger.png|;
							my $angle_png_fmt  = qq|$tmp_dest_prefix\-%d.png|;
							my $larger_size = int($sizeL->[0]*0.4) . 'x' . int($sizeL->[1]*0.4);

							my %CC_PID;
#								$SIG{'CHLD'} = "sigchild";
#								sub sigchild {
#									print __LINE__.":IS CHILD CHILD END!![".join(' '.@_)."]\n";
#								}


							my $t0 = [&Time::HiRes::gettimeofday()];

							for(my $i=0;$i<360;$i+=5){
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
							for(my $i=0;$i<360;$i+=5){
								my $target_png_file = sprintf($target_png_fmt,$i);
								my $png_file = sprintf($angle_png_fmt,$i);
								push(@PNG_FILES,$png_file) if(-e $png_file && -s $png_file);
								push(@TARGET_PNG_FILES,$target_png_file) if(-e $target_png_file && -s $target_png_file);
							}

							my $elapsed = &Time::HiRes::tv_interval($t0,[&Time::HiRes::gettimeofday()]);
							print __LINE__.':'.$elapsed."\n";

							if(scalar @PNG_FILES < 72 || scalar @TARGET_PNG_FILES < 72){

								my $t0 = [&Time::HiRes::gettimeofday()];

								print __LINE__.":CALL obj2animgif()\n";
								print __LINE__.":\t\$sizeL=[".&JSON::XS::encode_json($sizeL)."]\n";
								print __LINE__.":\t\$obj_files1=[".&JSON::XS::encode_json($obj_files1)."]\n";
								print __LINE__.":\t\$obj_files2=[".&JSON::XS::encode_json($obj_files2)."]\n";
								print __LINE__.":\t\$dest_prefix=[$dest_prefix]\n";
								print __LINE__.":\t\$tmp_dest_prefix=[$tmp_dest_prefix]\n";
								print __LINE__.":\t\$b1YRange=[$b1YRange]\n";
								print __LINE__.":\t\$largerbbox=[".&JSON::XS::encode_json($largerbbox)."]\n";
								print __LINE__.":\t\$largerbboxYRange=[$largerbboxYRange]\n";

								$bb = $obj2image->obj2animgif($sizeL,$obj_files1,$obj_files2,$tmp_dest_prefix,$b1YRange,$largerbbox,$largerbboxYRange);
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

								for(my $i=0;$i<360;$i+=5){
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

								for(my $i=0;$i<360;$i+=5){
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
								&BITS::ImageC::animatedGIF(in_files=>\@PNG_FILES,out_file=>$gif_file) unless(-e $gif_file && -s $gif_file);
								utime $rep_entry,$rep_entry,$gif_file if(-e $gif_file && -s $gif_file);
								warn __LINE__.":[$?]:[$!]" if($?);
								exit $? if(defined $cc_pid);
							}

							$cc_pid = fork;
							warn __LINE__.":Cannot fork: $!" unless defined $cc_pid;
							if($cc_pid){
								$CC_PID{$cc_pid} = undef;
							}else{
								my $gif_file = qq|$dest_prefixM.gif|;
								&BITS::ImageC::animatedGIF(in_files=>\@PNG_FILES,out_file=>$gif_file,geometry=>$sizeStrM) unless(-e $gif_file && -s $gif_file);
								utime $rep_entry,$rep_entry,$gif_file if(-e $gif_file && -s $gif_file);
								warn __LINE__.":[$?]:[$!]" if($?);
								exit $? if(defined $cc_pid);
							}

							$cc_pid = fork;
							warn __LINE__.":Cannot fork: $!" unless defined $cc_pid;
							if($cc_pid){
								$CC_PID{$cc_pid} = undef;
							}else{
								my $gif_file = qq|$dest_prefixS.gif|;
								&BITS::ImageC::animatedGIF(in_files=>\@TARGET_PNG_FILES,out_file=>$gif_file,geometry=>$sizeStrS) unless(-e $gif_file && -s $gif_file);
								utime $rep_entry,$rep_entry,$gif_file if(-e $gif_file && -s $gif_file);
								warn __LINE__.":[$?]:[$!]" if($?);
								exit $? if(defined $cc_pid);
							}

							$cc_pid = fork;
							warn __LINE__.":Cannot fork: $!" unless defined $cc_pid;
							if($cc_pid){
								$CC_PID{$cc_pid} = undef;
							}else{
								my $gif_file = qq|$dest_prefixXS.gif|;
								&BITS::ImageC::animatedGIF(in_files=>\@TARGET_PNG_FILES,out_file=>$gif_file,geometry=>$sizeStrXS) unless(-e $gif_file && -s $gif_file);
								utime $rep_entry,$rep_entry,$gif_file if(-e $gif_file && -s $gif_file);
								warn __LINE__.":[$?]:[$!]" if($?);
								exit $? if(defined $cc_pid);
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
									unless(-e $imgsL->[$i]){
										$png_file = sprintf($angle_png_fmt,$angle);
										die __LINE__.":Unknown file [$png_file]\n" unless(-e $png_file);
										&File::Copy::copy($png_file,$imgsL->[$i]) if(-e $png_file);
									}
									utime $rep_entry,$rep_entry,$imgsL->[$i] if(-e $imgsL->[$i] && -s $imgsL->[$i]);

									unless(-e $imgsM->[$i]){
										if(-e $imgsL->[$i]){
											&BITS::ImageC::resize(in_file=>$imgsL->[$i],geometry=>$sizeStrM,out_file=>$imgsM->[$i]);
										}
									}
									utime $rep_entry,$rep_entry,$imgsM->[$i] if(-e $imgsM->[$i] && -s $imgsM->[$i]);

									my $target_png_file = sprintf($target_png_fmt,$angle);
									if(-e $target_png_file && -s $target_png_file){
										&BITS::ImageC::resize(in_file=>$target_png_file,geometry=>$sizeStrS,out_file=>$imgsS->[$i]) unless(-e $imgsS->[$i] && -s $imgsS->[$i]);
										utime $rep_entry,$rep_entry,$imgsS->[$i] if(-e $imgsS->[$i] && -s $imgsS->[$i]);

										&BITS::ImageC::resize(in_file=>$target_png_file,geometry=>$sizeStrXS,out_file=>$imgsXS->[$i]) unless(-e $imgsXS->[$i] && -s $imgsXS->[$i]);
										utime $rep_entry,$rep_entry,$imgsXS->[$i] if(-e $imgsXS->[$i] && -s $imgsXS->[$i]);
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

							for($angle=0;$angle<360;$angle+=5){
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
									zmax => $b1->[5]+0
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

						&File::Path::remove_tree($tmp_base_path) if(defined $tmp_base_path && -e $tmp_base_path);
						undef $tmp_base_path if(defined $tmp_base_path);
						undef $tmp_img_prefix if(defined $tmp_img_prefix);

#					}else{
#						undef $txt_file_lock if(defined $txt_file_lock);
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
