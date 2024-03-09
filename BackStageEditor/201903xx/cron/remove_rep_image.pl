#!/bp3d/local/perl/bin/perl

$| = 1;
select(STDERR);
$| = 1;
select(STDOUT);

use File::Basename;
use File::Spec;
use File::Path;
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
use Image::Info;
use Time::HiRes qw/gettimeofday tv_interval/;

use FindBin;
my $htdocs_path;
BEGIN{
	use FindBin;
#	$htdocs_path = qq|$FindBin::Bin/../htdocs_130910|;
	$htdocs_path = qq|$FindBin::Bin/../htdocs| unless(-e $htdocs_path);
	print __LINE__,":BEGIN2!!\n";
}
use lib $FindBin::Bin,$htdocs_path;

require "webgl_common.pl";

use renderer;

#repの画像の場合、データ量が大きい為、Xserverの負荷を分散する為に、各プロセスに１つ
#use constant DEF_SERVER_NUMBRT => 97;
use constant {
	DEF_SERVER_NUMBRT => -1,
	MAX_PROG => 14,

	CACHE_FMA_PATH => '/bp3d/cache_fma',
	CHECK_USE_DATE => 0,	#日付のみで確認
	CHECK_USE_DATE_TIME => 1,	#日時で確認
	CHECK_EXISTS_FILE => 0,	#ファイルの有無で確認

	USE_BP3D_COLOR => 1,
	DEBUG_USE_BP3D_COLOR => 0,
};

my @REMOVE_FMAID = qw/FMA61284 FMA23881 FMA85544 FMA71324/;
#my @REMOVE_FMAID = qw/FMA23876 FMA23881 FMA85544 FMA71324/;


my $dbh = &get_dbh();

#my $lib_path;
my $xvfb_lock;
my $display_size;


my $inter_files;
my $is_child;
my $lock_filepath;
my $txt_file_lock;
my $old_umask;
sub sigexit {
	print "\n",__LINE__,":INT!!\n";
	eval{close(OUT);};
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
	print __LINE__,":BEGIN!!\n";
#	&setDisplay();
	$SIG{'HUP'} = $SIG{'INT'} = $SIG{'QUIT'} = $SIG{'ILL'} = $SIG{'TRAP'} = $SIG{'ABRT'} = $SIG{'BUS'} = $SIG{'FPE'} = $SIG{'KILL'} = $SIG{'USR1'} = $SIG{'SEGV'} = $SIG{'USR2'} = $SIG{'TERM'} = "sigexit";
}
END{
	umask($old_umask);
	unless(defined $is_child){
#		&File::Path::remove_tree($lock_filepath) if(defined $lock_filepath && -e $lock_filepath && -d $lock_filepath);
#		&File::Path::remove_tree($txt_file_lock) if(defined $txt_file_lock && -e $txt_file_lock && -d $txt_file_lock);
		print __LINE__,":IS PARENT END!![$lock_filepath][$txt_file_lock]\n";
	}else{
		&File::Path::remove_tree($txt_file_lock) if(defined $txt_file_lock && -e $txt_file_lock && -d $txt_file_lock);
		print __LINE__,":IS CHILD END!![$lock_filepath][$txt_file_lock]\n";
	}
	print __LINE__,":END!!\n";
#	&unsetDisplay();
}

#use lib $lib_path;
#use BITS::Config;
#use BITS::DB;


#use Inline Python;

use strict;


my @extlist = qw|.pl|;
my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);

my $lock_dirpath = File::Spec->catdir($FindBin::Bin,'logs');
unless(-e $lock_dirpath){
	&File::Path::make_path($lock_dirpath,{verbose => 0, mode => 0777});
}

my $lock_filefmt = qq|$cgi_name.lock-%d|;
my $lock_no=0;
my $LOCK;
for(;$lock_no<MAX_PROG;$lock_no++){
	$lock_filepath = File::Spec->catdir($lock_dirpath,sprintf($lock_filefmt,$lock_no));
	print __LINE__,":\$lock_filepath=[$lock_filepath]\n";
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
exit unless($lock_no<MAX_PROG);



my $art_file_prefix = File::Spec->catdir($FindBin::Bin,'art_file');
unless(-e $art_file_prefix){
	&File::Path::make_path($art_file_prefix,{verbose => 0, mode => 0777});
}
my $art_file_fmt = qq|$art_file_prefix/%s-%d%s|;

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

#	my @FILES;
	my $bp3d_objs = &renderer::new_bp3d_objs();

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
 art_data,
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
    representation_art
   where
    rep_id in (
      select
       rep_id
      from
       representation
      where
       (md_id,mv_id,mr_id,cdi_id) in (
           select
            md_id,mv_id,max(mr_id) as mr_id,cdi_id
           from
            representation
           where
            md_id=$md_id and mv_id=$mv_id and mr_id<=$mr_id and rep_delcause is null
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
	print __LINE__,":\$sth->rows()=[",$sth->rows(),"]\n";
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$art_id, undef);
	$sth->bind_col(++$column_number, \$art_ext, undef);
	$sth->bind_col(++$column_number, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
	$sth->bind_col(++$column_number, \$art_data_size, undef);
	$sth->bind_col(++$column_number, \$art_entry, undef);
	$sth->bind_col(++$column_number, \$hist_serial, undef);
	while($sth->fetch){
		next unless(defined $art_id && defined $art_data && defined $art_data_size && defined $art_entry && defined $hist_serial);
		my $objfile = sprintf($art_file_fmt,$art_id,$hist_serial,$art_ext);
		my $size = -s $objfile;
		my $mtime = 0;
		$mtime = (stat($objfile))[9] if(-e $objfile);
		unless(-e $objfile && $size == $art_data_size && $mtime>=$art_entry){
			print __LINE__,":Write [$objfile]\n";
			my $OUT;
			if(-e $objfile){
				open($OUT,"+< $objfile") or die "$!:$objfile\n";
			}else{
				open($OUT,"> $objfile") or die "$!:$objfile\n";
			}
			flock($OUT,2);
			unless(tell($OUT)==$art_data_size){
				seek($OUT,0,0);
				binmode($OUT);
				print $OUT $art_data;
				truncate($OUT,tell($OUT));
			}
			close($OUT);
			utime($art_entry,$art_entry,$objfile);
#			push(@FILES,$objfile);
		}
#		my $IN;
#		open($IN,$objfile) or die "$!:$objfile\n";
#		flock($IN,1);
#		close($IN);
		$bp3d_objs->objReader($objfile,$reduction);
	}
	$sth->finish;
	undef $sth;

	return $bp3d_objs;
}

sub tName2Type {
	my $t_key = shift;

	my $t_type;
#	if($t_key eq 'bp3d'){
#		$t_type = 1;
#	}elsif($t_key eq 'isa'){
#		$t_type = 3;
#	}elsif($t_key eq 'partof'){
#		$t_type = 4;
#	}

	my $sql = qq|select bul_id from buildup_logic where bul_abbr=lower(?)|;
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute($t_key) or die $dbh->errstr;
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$t_type, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;

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


my $model = qq|bp3d|;

#my @VERSION = ("3.0","2.0");
#my @VERSION = ("4.0.1303281200");
#my @VERSION = ("4.0.1305021540");
my @VERSION = ();

#my @TREE = ('bp3d','isa','partof');
#my @TREE = ('isa','partof');
#my @TREE = qw/isa/;
#my @TREE = qw/partof/;
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

my @STANDARD_B_ID = (
#	"FMA71287",	# Head
	"FMA7154",	# Head
	"FMA7155",	# 頸(ver.3.0のみ)
	"FMA13076",	# 第５腰椎
	"FMA24485",	# 膝蓋骨
#	"FMA37450",	# 短趾屈筋
#	"FMA9664",	# 足(ver.3.0のみ),FMA24225
	"FMA24491",	# 足(ver.3.0のみ),FMA24225
);

my $base_b_id = {
	'bp3d'   => 'FMA20394',
	'isa'    => 'FMA62955',
	'partof' => 'FMA20394',
};

#my $version = qq|3.0|;
#my $tree = qq|bp3d|;
my $copyrightL = qq|$FindBin::Bin/img/copyrightM.png|;
my $copyrightS = qq|$FindBin::Bin/img/copyrightS.png|;

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
{
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
	my @VERSION = ();
	if(scalar @VERSION == 0){
#		my $sql = qq|select mr_version from model_revision where mr_use and md_id=? order by mr_order|;
		my $sql = qq|
select mr.mr_version from model_revision as mr
left join (select * from model_version) as mv on mv.md_id=mr.md_id and mv.mv_id=mr.mv_id
where mr.mr_use and mv.mv_publish and mv.mv_use and mv.mv_frozen and mr.md_id=? order by mr.mr_order
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
			die __LINE__,";Unknown Version!!\n";
		}

		my $ci_id;
		my $cb_id;
		my $sql = qq|select ci_id,cb_id from model_version where md_id=? and mv_id=?|;
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute($md_id,$mv_id) or die $dbh->errstr;
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$ci_id, undef);
		$sth->bind_col(++$column_number, \$cb_id, undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;
		unless(defined $mv_id && defined $mr_id){
			die __LINE__,";Unknown Version!!\n";
		}

		my $DEF_COLOR;
		my $DEF_COLOR_ART;
		my $DEF_COLOR_CDI;
		if(USE_BP3D_COLOR){
			my $bp3d_color_file = qq|/bp3d/ag-test/htdocs/data/$version/bp3d.color|;
			$bp3d_color_file = qq|/bp3d/ag-test/htdocs/data/bp3d.color| unless(-e $bp3d_color_file);
			if(-e $bp3d_color_file){
				open(IN,"< $bp3d_color_file");
				while(<IN>){
					s/\s*$//g;
					s/^\s*//g;
					next if(/^#/);
					my($cdi_name,$color) = split(/\t/);
					next if($cdi_name eq "" || $color eq "");
					next if(exists($DEF_COLOR->{$cdi_name}));
					$color =~ s/^#//g;
					push(@{$DEF_COLOR->{$cdi_name}},hex(uc(substr($color,0,2)))/255);
					push(@{$DEF_COLOR->{$cdi_name}},hex(uc(substr($color,2,2)))/255);
					push(@{$DEF_COLOR->{$cdi_name}},hex(uc(substr($color,4,2)))/255);
				}
				close(IN);
			}

			my $sql_cm = qq|select art_id,art_hist_serial,cdi_name,cdi_id from view_concept_art_map WHERE md_id=? AND mv_id=? AND mr_id=? AND cm_use AND cm_delcause IS NULL|;
			my $sth_cm = $dbh->prepare($sql_cm) or die $dbh->errstr;
			$sth_cm->execute($md_id,$mv_id,$mr_id) or die $dbh->errstr;
			my $art_id;
			my $art_hist_serial;
			my $cdi_name;
			my $cdi_id;
			my $column_number = 0;
			$sth_cm->bind_col(++$column_number, \$art_id, undef);
			$sth_cm->bind_col(++$column_number, \$art_hist_serial, undef);
			$sth_cm->bind_col(++$column_number, \$cdi_name, undef);
			$sth_cm->bind_col(++$column_number, \$cdi_id, undef);
			while($sth_cm->fetch){
				next unless(exists $DEF_COLOR->{$cdi_name});
				push(@{$DEF_COLOR_ART->{$art_id}->{$art_hist_serial}},@{$DEF_COLOR->{$cdi_name}}) unless(exists $DEF_COLOR_ART->{$art_id} && exists $DEF_COLOR_ART->{$art_id}->{$art_hist_serial});

				push(@{$DEF_COLOR_CDI->{$cdi_id}},@{$DEF_COLOR->{$cdi_name}}) unless(exists $DEF_COLOR_CDI->{$cdi_id});
			}
			$sth_cm->finish;
			undef $sth_cm;
		}




		my $sql =<<SQL;
select
 min(art_xmin),
 max(art_xmax),
 min(art_ymin),
 max(art_ymax),
 min(art_zmin),
 max(art_zmax)
from
 history_art_file
where
 (art_id,hist_serial) in (
     select
      art_id,art_hist_serial
     from
      representation_art
     where
      rep_id in (
          select
           rep_id
          from
--           view_representation
           representation
          where
           (md_id,mv_id,mr_id,cdi_id) in (
               select
                md_id,mv_id,max(mr_id) as mr_id,cdi_id
               from
                view_representation
               where
                md_id=? and mv_id=? and mr_id<=? and cdi_name=? and rep_delcause is null
               group by
                md_id,mv_id,cdi_id
            )
      )
 )

SQL
		my $sth_history_art_file_bbox = $dbh->prepare($sql) or die $dbh->errstr;


		my $sql_history_art_file =<<SQL;
select
 art_id,
 art_ext,
 hist_serial
from
 history_art_file
where
 (art_id,hist_serial) in (
     select
      art_id,art_hist_serial
     from
      representation_art
     where
      rep_id in (
          select
           rep_id
          from
           representation
          where
           (md_id,mv_id,mr_id,bul_id,cdi_id) in (
               select
                md_id,mv_id,max(mr_id) as mr_id,bul_id,cdi_id
               from
                view_representation
               where
                md_id=? and mv_id=? and mr_id<=? and bul_id=? and cdi_name=? and rep_delcause is null
               group by
                md_id,mv_id,bul_id,cdi_id
            )
      )
 )

SQL
		my $sth_history_art_file = $dbh->prepare($sql_history_art_file) or die $dbh->errstr;


#		my $bp3d_objs = &load_art_file(md_id=>$md_id,mv_id=>$mv_id,mr_id=>$mr_id);
#		my $obj2image = &renderer::new_obj2image($bp3d_objs,1);

		foreach my $b_id (@STANDARD_B_ID){

			my $art_xmin;
			my $art_xmax;
			my $art_ymin;
			my $art_ymax;
			my $art_zmin;
			my $art_zmax;

			$sth_history_art_file_bbox->execute($md_id,$mv_id,$mr_id,$b_id) or die $dbh->errstr;
			my $column_number = 0;
			$sth_history_art_file_bbox->bind_col(++$column_number, \$art_xmin, undef);
			$sth_history_art_file_bbox->bind_col(++$column_number, \$art_xmax, undef);
			$sth_history_art_file_bbox->bind_col(++$column_number, \$art_ymin, undef);
			$sth_history_art_file_bbox->bind_col(++$column_number, \$art_ymax, undef);
			$sth_history_art_file_bbox->bind_col(++$column_number, \$art_zmin, undef);
			$sth_history_art_file_bbox->bind_col(++$column_number, \$art_zmax, undef);
			$sth_history_art_file_bbox->fetch;
			$sth_history_art_file_bbox->finish;
			next unless(defined $art_xmin && defined $art_xmax && defined $art_ymin && defined $art_ymax && defined $art_zmin && defined $art_zmax);
			push(@{$STANDARD_BBOX{$b_id}},$art_xmin+0,$art_xmax+0,$art_ymin+0,$art_ymax+0,$art_zmin+0,$art_zmax+0);
			print __LINE__,":[$b_id]=[",&JSON::XS::encode_json($STANDARD_BBOX{$b_id}),"]\n";
		}



		my %Z_BBOX = ();

		my $sql =<<SQL;
select * from (
(select
  round(rep_zmin) as z,min(rep_xmin) as xmin,max(rep_xmax) as xmax,min(rep_ymin) as ymin,max(rep_ymax) as ymax,md_id,mv_id
 from
  representation
 where
  (md_id,mv_id,mr_id,cdi_id) in (select md_id,mv_id,max(mr_id) as mr_id,cdi_id from representation where md_id=$md_id and mv_id=$mv_id and mr_id<=$mr_id group by md_id,mv_id,cdi_id)
 group by z,md_id,mv_id
)
union
(select
  round(rep_zmax) as z,min(rep_xmin) as xmin,max(rep_xmax) as xmax,min(rep_ymin) as ymin,max(rep_ymax) as ymax,md_id,mv_id
 from
  view_representation
 where
  (md_id,mv_id,mr_id,cdi_id) in (select md_id,mv_id,max(mr_id) as mr_id,cdi_id from representation where md_id=$md_id and mv_id=$mv_id and mr_id<=$mr_id group by md_id,mv_id,cdi_id)
 group by z,md_id,mv_id)
) a
SQL

		my $rep_z;
		my $rep_xmin;
		my $rep_xmax;
		my $rep_ymin;
		my $rep_ymax;
		my $rep_zmin;
		my $rep_zmax;
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		warn __LINE__,":\$sth->rows()=[",$sth->rows(),"]\n";
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$rep_z, undef);
		$sth->bind_col(++$column_number, \$rep_xmin, undef);
		$sth->bind_col(++$column_number, \$rep_xmax, undef);
		$sth->bind_col(++$column_number, \$rep_ymin, undef);
		$sth->bind_col(++$column_number, \$rep_ymax, undef);
		$sth->bind_col(++$column_number, \$rep_zmin, undef);
		$sth->bind_col(++$column_number, \$rep_zmax, undef);
		while($sth->fetch){
			next unless(defined $rep_z &&
									defined $rep_xmin && defined $rep_xmax && 
									defined $rep_ymin && defined $rep_ymax && 
									defined $rep_zmin && defined $rep_zmax);

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

		foreach my $tree (@TREE){

			print __LINE__,":\$tree=$tree\n";

			my $t_type = &tName2Type($tree);

			my $sth_but_cids = $dbh->prepare(qq|select but_cids from view_buildup_tree where ci_id=$ci_id and cb_id=$cb_id and bul_id=$t_type and cdi_name=?|) or die $dbh->errstr;
			my %REMOVE_FMAID;
			foreach my $cdi_name (@REMOVE_FMAID){
				$REMOVE_FMAID{$cdi_name}->{$t_type} = undef;

				my $but_cids;
				my $cdi_pname;
				$sth_but_cids->execute($cdi_name) or die $dbh->errstr;
				while(my $row = $sth_but_cids->fetchrow_hashref){
					next unless(defined $row->{'but_cids'});

					my $but_cids = &JSON::XS::decode_json($row->{'but_cids'});
					my $sql_cdi = sprintf(qq|select cdi_name from concept_data_info where ci_id=$ci_id and cdi_id in (%s)|,join(",",@$but_cids));
#					warn __LINE__.":[$sql_cdi]\n";
					my $sth_cdi = $dbh->prepare($sql_cdi) or die $dbh->errstr;
					$sth_cdi->execute() or die $dbh->errstr;
					while(my $row_cdi = $sth_cdi->fetchrow_hashref){
						$REMOVE_FMAID{$row_cdi->{'cdi_name'}}->{$t_type} = undef if(defined $row_cdi->{'cdi_name'});
					}
					$sth_cdi->finish;
					undef $sth_cdi;

				}
				$sth_but_cids->finish;

			}
			my $sth_cdi_parent = $dbh->prepare(qq|select cdi_pname from view_buildup_tree where ci_id=$ci_id and cb_id=$cb_id and cdi_name=? and bul_id=?|) or die $dbh->errstr;
			foreach my $cdi_name (@REMOVE_FMAID){
				&getParentTreeNode($sth_cdi_parent,\%REMOVE_FMAID,$cdi_name,$t_type);
			}
#			print Dumper(\%REMOVE_FMAID);

			undef $sth_but_cids;
			undef $sth_cdi_parent;
#			exit;



			my $rep_xmin;
			my $rep_xmax;
			my $rep_ymin;
			my $rep_ymax;
			my $rep_zmin;
			my $rep_zmax;
			my $sql =<<SQL;
select
 min(rep_xmin),max(rep_xmax),min(rep_ymin),max(rep_ymax),min(rep_zmin),max(rep_zmax)
from
 representation
where
 (md_id,mv_id,mr_id,bul_id) in (select md_id,mv_id,max(mr_id) as mr_id,bul_id from representation where md_id=$md_id and mv_id=$mv_id and mr_id<=$mr_id and bul_id=$t_type group by md_id,mv_id,bul_id)
SQL
			my $sth = $dbh->prepare($sql) or die $dbh->errstr;
			$sth->execute() or die $dbh->errstr;
			warn __LINE__,":\$sth->rows()=[",$sth->rows(),"]\n";
			my $column_number = 0;
			$sth->bind_col(++$column_number, \$rep_xmin, undef);
			$sth->bind_col(++$column_number, \$rep_xmax, undef);
			$sth->bind_col(++$column_number, \$rep_ymin, undef);
			$sth->bind_col(++$column_number, \$rep_ymax, undef);
			$sth->bind_col(++$column_number, \$rep_zmin, undef);
			$sth->bind_col(++$column_number, \$rep_zmax, undef);
			$sth->fetch;
			$sth->finish;
			undef $sth;

			next unless(defined $rep_xmin && defined $rep_xmax && defined $rep_ymin && defined $rep_ymax && defined $rep_zmin && defined $rep_zmax);
			my $all_bound = [$rep_xmin+0,$rep_xmax+0,$rep_ymin+0,$rep_ymax+0,$rep_zmin+0,$rep_zmax+0];

			my @B_IDS = ();
			my @B_IDS = map {{
				cdi_name=>$_,
				rep_delcause => undef,
				md_abbr      => 'bp3d',
				mr_version   => $version,
				rep_entry    => time,
				rep_ci_id    => $ci_id,
				rep_cb_id    => $cb_id,
			}} keys(%REMOVE_FMAID);



			#DEBUG
=pod
			push(@B_IDS,{
				cdi_name     => 'FMA45970',
				rep_delcause => undef,
				md_abbr      => 'bp3d',
				mr_version   => '4.0.1305021540',
				rep_entry    => time,
				rep_ci_id    => 1,
				rep_cb_id    => 4,
			});
=cut
=pod
			push(@B_IDS,{
				cdi_name     => 'FMA72718',
				rep_delcause => undef,
				md_abbr      => 'bp3d',
				mr_version   => '4.3.1403311232',
				rep_entry    => time,
				rep_ci_id    => 1,
				rep_cb_id    => 5,
			});
=cut
=pod
			#神経
			push(@B_IDS,{
				cdi_name     => 'FMA11195',
				rep_delcause => undef,
				md_abbr      => 'bp3d',
				mr_version   => '4.3.1403311232',
				rep_entry    => time,
				rep_ci_id    => 1,
				rep_cb_id    => 5,
			});
			push(@B_IDS,{
				cdi_name     => 'FMA63819',
				rep_delcause => undef,
				md_abbr      => 'bp3d',
				mr_version   => '4.3.1403311232',
				rep_entry    => time,
				rep_ci_id    => 1,
				rep_cb_id    => 5,
			});

			#静脈
			push(@B_IDS,{
				cdi_name     => 'FMA86188',
				rep_delcause => undef,
				md_abbr      => 'bp3d',
				mr_version   => '4.3.1403311232',
				rep_entry    => time,
				rep_ci_id    => 1,
				rep_cb_id    => 5,
			});
			push(@B_IDS,{
				cdi_name     => 'FMA63814',
				rep_delcause => undef,
				md_abbr      => 'bp3d',
				mr_version   => '4.3.1403311232',
				rep_entry    => time,
				rep_ci_id    => 1,
				rep_cb_id    => 5,
			});

			#動脈
			push(@B_IDS,{
				cdi_name     => 'FMA86187',
				rep_delcause => undef,
				md_abbr      => 'bp3d',
				mr_version   => '4.3.1403311232',
				rep_entry    => time,
				rep_ci_id    => 1,
				rep_cb_id    => 5,
			});
			push(@B_IDS,{
				cdi_name     => 'FMA63812',
				rep_delcause => undef,
				md_abbr      => 'bp3d',
				mr_version   => '4.3.1403311232',
				rep_entry    => time,
				rep_ci_id    => 1,
				rep_cb_id    => 5,
			});

			#骨
			push(@B_IDS,{
				cdi_name     => 'FMA5018',
				rep_delcause => undef,
				md_abbr      => 'bp3d',
				mr_version   => '4.3.1403311232',
				rep_entry    => time,
				rep_ci_id    => 1,
				rep_cb_id    => 5,
			});
=cut
			if(scalar @B_IDS == 0){
				my $sql =<<SQL;
select
 cdi.cdi_name,
 rep.rep_delcause,
 md_abbr,
 mr_version,
 EXTRACT(EPOCH FROM rep.rep_entry),
 rep.ci_id,
 cb_id,

 cdi.cdi_taid,
 CASE WHEN cdi.cdi_taid IS NOT NULL THEN 1 ELSE 0 END as is_taid,
 rep.rep_entry,
 rep.rep_primitive,
 (rep.rep_density_objs::real/rep.rep_density_ends::real) as rep_density
from
 representation as rep
left join (select md_id,md_abbr from model) as md on (md.md_id = rep.md_id)
left join (select md_id,mv_id,mr_id,mr_version from model_revision) as mr on (mr.md_id = rep.md_id and mr.mv_id = rep.mv_id and mr.mr_id = rep.mr_id)
left join (select bul_id,bul_name_e from buildup_logic) as bul on (bul.bul_id = rep.bul_id)
left join (select ci_id,cdi_id,cdi_name,cdi_taid from concept_data_info) as cdi on (cdi.ci_id = rep.ci_id and cdi.cdi_id = rep.cdi_id)
where
 (rep.md_id,rep.mv_id,rep.mr_id,rep.bul_id,rep.cdi_id) in (select md_id,mv_id,max(mr_id) as mr_id,bul_id,cdi_id from representation where md_id=$md_id and mv_id=$mv_id and mr_id<=$mr_id and bul_id=$t_type group by md_id,mv_id,bul_id,cdi_id)
order by
 is_taid desc,
 rep_density desc NULLS LAST,
 rep.rep_primitive desc NULLS LAST,
 rep.rep_entry desc,
 cdi.cdi_name
SQL
				my $sth = $dbh->prepare($sql) or die $dbh->errstr;
				$sth->execute() or die $dbh->errstr;
				warn __LINE__,":\$sth->rows()=[",$sth->rows(),"]\n";
				my $column_number = 0;
				my $cdi_name;
				my $rep_delcause;
				my $md_abbr;
				my $mr_version;
				my $rep_entry;
				my $rep_ci_id;
				my $rep_cb_id;
				$sth->bind_col(++$column_number, \$cdi_name, undef);
				$sth->bind_col(++$column_number, \$rep_delcause, undef);
				$sth->bind_col(++$column_number, \$md_abbr, undef);
				$sth->bind_col(++$column_number, \$mr_version, undef);
				$sth->bind_col(++$column_number, \$rep_entry, undef);
				$sth->bind_col(++$column_number, \$rep_ci_id, undef);
				$sth->bind_col(++$column_number, \$rep_cb_id, undef);
				while($sth->fetch){
					next unless(defined $cdi_name);
					push(@B_IDS,{
						cdi_name     => $cdi_name,
						rep_delcause => $rep_delcause,
						md_abbr      => $md_abbr,
						mr_version   => $mr_version,
						rep_entry    => $rep_entry,
						rep_ci_id    => $rep_ci_id,
						rep_cb_id    => $rep_cb_id,
					});
				}
				$sth->finish;
				undef $sth;
			}

			my %CACHE_JSON;

			foreach my $t_b_id (@B_IDS){
				my $target_cdi_name = $t_b_id->{'cdi_name'};
				my $md_abbr = $t_b_id->{'md_abbr'};
#				my $mr_version = $t_b_id->{'mr_version'};
				my $mr_version = $version;
				my $rep_ci_id = $t_b_id->{'rep_ci_id'};
				my $rep_cb_id = $t_b_id->{'rep_cb_id'};
				my $rep_entry = $t_b_id->{'rep_entry'};
				my $rep_delcause = $t_b_id->{'rep_delcause'};

				my $FOCUS_COLOR;
				my $COLOR;
=pod
				if(USE_BP3D_COLOR){
					if(defined $DEF_COLOR && exists $DEF_COLOR->{$target_cdi_name} && defined $DEF_COLOR->{$target_cdi_name} && ref $DEF_COLOR->{$target_cdi_name} eq 'ARRAY'){
#						push(@$FOCUS_COLOR,@{$DEF_COLOR->{$target_cdi_name}});
#						push(@$COLOR,(1.0,1.0,1.0));
					}elsif(DEBUG_USE_BP3D_COLOR){
						#DEBUG
						next;
					}
#					push(@$FOCUS_COLOR,(1.0,0.3176470588235294,0.0));
#					push(@$COLOR,(1.0,1.0,1.0));
				}
=cut
				if(USE_BP3D_COLOR){
					push(@$FOCUS_COLOR,(1.0,0.3176470588235294,0.0));
				}

				my($img_prefix,$img_path) = &getRepImagePrefix($mr_version,$t_type,$target_cdi_name);

#				my $cache_json_base_path = sprintf(qq|/bp3d/cache_fma/%s/common|,$mr_version);
				my $cache_json_base_path = File::Spec->catdir(CACHE_FMA_PATH,$mr_version,'common','*',$rep_ci_id,$rep_cb_id,$md_id,$mv_id,$mr_id,$t_type);
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

#				my $img_prefix = File::Spec->catdir($img_path,$target_cdi_name);
				my $txt_file = qq|$img_prefix.txt|;
				print __LINE__,":\$txt_file=[",$txt_file,"][",(-e $txt_file ? 1 : 0),"][",(-s $txt_file),"]\n";

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

=pod
				my @SIZES = ([640,640],[120,120],[40,40],[16,16]);
				my $sizeL = shift @SIZES;
				my $sizeM = shift @SIZES;
				my $sizeS = shift @SIZES;
				my $sizeXS = shift @SIZES;

				my $sizeStrL = join("x",@$sizeL);
				my $sizeStrM = join("x",@$sizeM);
				my $sizeStrS = join("x",@$sizeS);
				my $sizeStrXS = join("x",@$sizeXS);

				my @DIR = qw|front left back right|;

				my $gif_prefix_fmt = qq|%s_%s|;
				my $gif_fmt = qq|$gif_prefix_fmt.gif|;

				my $png_prefix_fmt = qq|%s_%s_%s|;
				my $png_fmt = qq|$png_prefix_fmt.png|;

				my $imgsL;
				my $imgsM;
				my $imgsS;
				my $imgsXS;

				push(@$imgsL,sprintf($gif_fmt,$img_prefix,$sizeStrL));
				foreach my $dir (@DIR){
					push(@$imgsL,sprintf($png_fmt,$img_prefix,$dir,$sizeStrL));
				}

				push(@$imgsM,sprintf($gif_fmt,$img_prefix,$sizeStrM));
				foreach my $dir (@DIR){
					push(@$imgsM,sprintf($png_fmt,$img_prefix,$dir,$sizeStrM));
				}

				push(@$imgsS,sprintf($gif_fmt,$img_prefix,$sizeStrS));
				foreach my $dir (@DIR){
					push(@$imgsS,sprintf($png_fmt,$img_prefix,$dir,$sizeStrS));
				}

				push(@$imgsXS,sprintf($gif_fmt,$img_prefix,$sizeStrXS));
				foreach my $dir (@DIR){
					push(@$imgsXS,sprintf($png_fmt,$img_prefix,$dir,$sizeStrXS));
				}
=cut

				my @chk_files;
				push(@chk_files,$txt_file);
				push(@chk_files,@$imgsL);
				push(@chk_files,@$imgsM);
				push(@chk_files,@$imgsS);
				push(@chk_files,@$imgsXS);

#				if(defined $t_b_id->{'rep_delcause'}){
					unlink qq|$img_prefix.gif|;# if(-e qq|$img_prefix.gif|);	#リンク元が存在しない場合を考慮する
					foreach my $chk_file (@chk_files){
#						next unless(-e $chk_file);	#リンク元が存在しない場合を考慮する
#						print __LINE__,":unlink:[$chk_file]\n";
						unlink $chk_file;
					}


					next;
#				}

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

						my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($rep_entry);
						my $rep_mtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
						my $rep_date = sprintf("%04d/%02d/%02d",$year+1900,$mon+1,$mday);

#						if($version eq '4.1.1309051818' && $file_mtime ne $rep_mtime){
#							utime $rep_entry,$rep_entry,$chk_file;
#							$file_mtime = $rep_mtime;
#							$file_date = $rep_date;
#						}

						if(CHECK_USE_DATE_TIME && $file_mtime eq $rep_mtime){
							print __LINE__,":更新日時比較:[文字で確認][$file_mtime]==[$rep_mtime]\n";
							next;
						}
						if(CHECK_USE_DATE && $file_date eq $rep_date){
							print __LINE__,":更新日比較:[文字で確認][$file_date]==[$rep_date]\n";
							next;
						}

	#					next if($file_date ge $rep_date);#実際には、この比較は無効

						$chk = 1;


						print __LINE__,":更新日時比較:[$chk_file][$file_mtime]<[$rep_mtime]\n";

						last;
					}
				}

				if(exists $CACHE_JSON{$cache_json_base_path} && exists $CACHE_JSON{$cache_json_base_path}->{$target_cdi_name}){
					foreach (sort keys(%{$CACHE_JSON{$cache_json_base_path}->{$target_cdi_name}})){
						next unless(-e $_ && (stat($_))[9]<$max_mtime);
						unlink $_;
						print __LINE__,":unlink:[$_]\n";
					}
				}

				next unless(defined $chk);

#				unshift(@chk_files,$txt_file);


				$txt_file_lock = qq|$txt_file.lock|;
#				print __LINE__,":txt_file_lock:[$txt_file_lock]\n";
#				if(mkdir($txt_file_lock)){
#					print __LINE__,":mkdir:[OK]\n";
#				}else{
#					print __LINE__,":mkdir:[NG]\n";
#				}
#				if(&File::Path::make_path($txt_file_lock,{verbose => 0, mode => 0777})){
				if(mkdir($txt_file_lock,0777)){
#					print __LINE__,":make_path:[OK]\n";
				}else{
					undef $txt_file_lock;
					next;
				}
#					exit(1);
#				print __LINE__,":remove_tree:[",&File::Path::remove_tree($txt_file_lock),"]\n" if(-e $txt_file_lock && -d $txt_file_lock);


				my $pid = fork;
#				my $pid = 0;
				die __LINE__,":Cannot fork: $!" unless defined $pid;
				if($pid){

					wait;
					print __LINE__,":親プロセス(子プロセスID: $pid)[",$?,"]\n";
					if($?){
						die __LINE__,":[",$?,"]\n";
					}else{
#						exit 0;

						undef $is_child if(defined $is_child);

						&disconnectDB();
						&connectDB();
						$dbh = &get_dbh();
					}
				}else{
#					$SIG{'HUP'} = $SIG{'INT'} = $SIG{'QUIT'} = $SIG{'ILL'} = $SIG{'TRAP'} = $SIG{'ABRT'} = $SIG{'BUS'} = $SIG{'FPE'} = $SIG{'KILL'} = $SIG{'USR1'} = $SIG{'SEGV'} = $SIG{'USR2'} = $SIG{'TERM'} = "sigexit";

					$is_child = 1;
					undef $inter_files if(defined $inter_files);

					if(-l $txt_file){
						foreach my $chk_file (@chk_files){
							next unless(-e $chk_file);
							next unless(-l $chk_file);
							print __LINE__,":unlink:[$chk_file]\n";
							unlink $chk_file;
						}
						unlink qq|$img_prefix.gif| if(-e qq|$img_prefix.gif|);
					}
					my $TXT;
					if(open($TXT,"> $txt_file")){
#					if(!-e $lock_dirpath && &File::Path::make_path($lock_dirpath,{verbose => 0, mode => 0777}) && open($TXT,"> $txt_file")){
#						if(flock($TXT, 6)){
						if(1){

							&connectDB();
							$dbh = &get_dbh();

							my $sth_history_art_file = $dbh->prepare($sql_history_art_file) or die $dbh->errstr;

							print __LINE__,":[$md_id,$mv_id,$mr_id,$target_cdi_name]\n";

#							my $bp3d_objs = &load_art_file(md_id=>$md_id,mv_id=>$mv_id,mr_id=>$mr_id);
#							my $obj2image = &renderer::new_obj2image($bp3d_objs,1);
#							if(defined $FOCUS_COLOR){
#								$obj2image->setFocusColor($FOCUS_COLOR);
#								$obj2image->setColor($COLOR);
#							}else{
#								$obj2image->resetFocusColor();
#								$obj2image->resetColor();
#							}

							unlink qq|$img_prefix.gif| if(-e qq|$img_prefix.gif|);
							foreach my $chk_file (@chk_files){
								next unless(-e $chk_file);
								next if($chk_file eq $txt_file);
								unlink $chk_file;
							}

							my $obj_files1;
							my $obj_files2 = [];

							my %use_objs;

#							my $sql_cm = qq|select cdi_name from view_concept_art_map WHERE md_id=? AND mv_id=? AND mr_id=? AND art_id=? AND art_hist_serial=? AND cm_use AND cm_delcause IS NULL|;
#							my $sth_cm = $dbh->prepare($sql_cm) or die $dbh->errstr;
							my $use_bp3d_color;

							my $art_id;
							my $art_ext;
							my $art_hist_serial;
							$sth_history_art_file->execute($md_id,$mv_id,$mr_id,$t_type,$target_cdi_name) or die $dbh->errstr;
							my $column_number = 0;
							$sth_history_art_file->bind_col(++$column_number, \$art_id, undef);
							$sth_history_art_file->bind_col(++$column_number, \$art_ext, undef);
							$sth_history_art_file->bind_col(++$column_number, \$art_hist_serial, undef);
							while($sth_history_art_file->fetch){
								next unless(defined $art_id && defined $art_ext && defined $art_hist_serial);
								my $objfile = sprintf($art_file_fmt,$art_id,$art_hist_serial,$art_ext);
								next unless(-e $objfile);

								my $color;
#								if(USE_BP3D_COLOR){
#									$sth_cm->execute($md_id,$mv_id,$mr_id,$art_id,$art_hist_serial) or die $dbh->errstr;
#									my $cm_cdi_name;
#									$sth_cm->bind_col(1, \$cm_cdi_name, undef);
#									$sth_cm->fetch;
#									$sth_cm->finish;
#									if(defined $cm_cdi_name){
#										if(defined $DEF_COLOR && exists $DEF_COLOR->{$cm_cdi_name} && defined $DEF_COLOR->{$cm_cdi_name} && ref $DEF_COLOR->{$cm_cdi_name} eq 'ARRAY'){
#											push(@$color,@{$DEF_COLOR->{$cm_cdi_name}});
#											$use_bp3d_color = 1;
#										}else{
#											print STDERR __LINE__.":Unknown color [$art_id][$art_hist_serial]\n";
#										}
#									}else{
#										print STDERR __LINE__.":Unknown cdi_name [$art_id][$art_hist_serial][$target_cdi_name]\n";
#									}
#								}
								if(USE_BP3D_COLOR){
									if(exists $DEF_COLOR_ART->{$art_id} && exists $DEF_COLOR_ART->{$art_id}->{$art_hist_serial} && ref $DEF_COLOR_ART->{$art_id}->{$art_hist_serial} eq 'ARRAY'){
										push(@$color,@{$DEF_COLOR_ART->{$art_id}->{$art_hist_serial}});
										$use_bp3d_color = 1;
									}else{
										print STDERR __LINE__.":Unknown color [$art_id][$art_hist_serial]\n";
									}
								}


								push(@$obj_files1,{
									path => $objfile,
									color => $color
								});
				#				print __LINE__,":\$objfile=[$objfile]\n";
							}
							$sth_history_art_file->finish;

							%use_objs = map {$_->{'path'}=>undef} @$obj_files1;
							print __LINE__,":obj_files1=[",(scalar @$obj_files1),"]\n" if(defined $obj_files1 && ref $obj_files1 eq 'ARRAY');

							my $cdi_id;
							my $but_cids;
							my $sql_but_cids = qq|select cdi_id,but_cids from view_buildup_tree WHERE ci_id=? AND cb_id=? AND bul_id=? AND cdi_name=?|;
							my $sth_but_cids = $dbh->prepare($sql_but_cids) or die $dbh->errstr;
#							print __LINE__,":\$rep_ci_id=[$rep_ci_id]\n";
#							print __LINE__,":\$rep_cb_id=[$rep_cb_id]\n";
#							print __LINE__,":\$t_type=[$t_type]\n";
#							print __LINE__,":\$target_cdi_name=[$target_cdi_name]\n";
							$sth_but_cids->execute($rep_ci_id,$rep_cb_id,$t_type,$target_cdi_name) or die $dbh->errstr;
							print __LINE__,":\$rows=[",$sth_but_cids->rows(),"]\n";
							my $column_number = 0;
							$sth_but_cids->bind_col(++$column_number, \$cdi_id, undef);
							$sth_but_cids->bind_col(++$column_number, \$but_cids, undef);
							$sth_but_cids->fetch;
							$sth_but_cids->finish;
							undef $sth_but_cids;
#							print __LINE__,":\$but_cids=[$but_cids]\n";
							if(defined $cdi_id || defined $but_cids){
								my $but_cids_arr;
								if(defined $but_cids){
									eval{$but_cids_arr = &JSON::XS::decode_json($but_cids);};
								}
								push(@$but_cids_arr,$cdi_id) if(defined $cdi_id);
								print __LINE__,":\$but_cids_arr=[",(scalar @$but_cids_arr),"]\n" if(defined $but_cids_arr);
								if(defined $but_cids_arr && ref $but_cids_arr eq 'ARRAY'){
									my $fmt =<<SQL;
select
 art_id,
 art_ext,
 hist_serial
from
 history_art_file
where
 (art_id,hist_serial) in (
   select
    art_id,art_hist_serial
   from
    representation_art
   where
    rep_id in (
        select
         rep_id
        from
         representation
        where
         (md_id,mv_id,mr_id,bul_id,cdi_id) in (
           select
            md_id,mv_id,max(mr_id) as mr_id,bul_id,cdi_id
           from
            representation
           where
            bul_id<>? AND
            (md_id,mv_id,cdi_id) IN (
              select
               md_id,mv_id,cdi_id
              from
               representation
              where
               rep_id in (
                   select
                    rep_id
                   from
                    representation
                   where
                    (md_id,mv_id,mr_id,cdi_id) in (
                        select
                         md_id,mv_id,max(mr_id) as mr_id,cdi_id
                        from
                         representation
                        where
                         md_id=? and mv_id=? and mr_id<=? and bul_id=? and cdi_id in (%s) and rep_delcause is null
                        group by
                         md_id,mv_id,cdi_id
                     )
               )
              group by
               md_id,mv_id,cdi_id
            )
           group by
            md_id,mv_id,bul_id,cdi_id
         )
    )
 )
SQL
									my $sql = sprintf($fmt,join(",",@$but_cids_arr));
									my $sth = $dbh->prepare($sql) or die $dbh->errstr;
									$sth->execute($t_type,$md_id,$mv_id,$mr_id,$t_type) or die $dbh->errstr;
									print __LINE__,":\$rows=[",$sth->rows(),"]\n";
									my $column_number = 0;
									$sth->bind_col(++$column_number, \$art_id, undef);
									$sth->bind_col(++$column_number, \$art_ext, undef);
									$sth->bind_col(++$column_number, \$art_hist_serial, undef);
									while($sth->fetch){
										next unless(defined $art_id && defined $art_ext && defined $art_hist_serial);
										my $objfile = sprintf($art_file_fmt,$art_id,$art_hist_serial,$art_ext);
										next unless(-e $objfile);
#										print __LINE__,":\$objfile=[$objfile]\n";

										my $color;
#										if(USE_BP3D_COLOR){
#											$sth_cm->execute($md_id,$mv_id,$mr_id,$art_id,$art_hist_serial) or die $dbh->errstr;
#											my $cm_cdi_name;
#											$sth_cm->bind_col(1, \$cm_cdi_name, undef);
#											$sth_cm->fetch;
#											$sth_cm->finish;
#											if(defined $cm_cdi_name){
#												if(defined $DEF_COLOR && exists $DEF_COLOR->{$cm_cdi_name} && defined $DEF_COLOR->{$cm_cdi_name} && ref $DEF_COLOR->{$cm_cdi_name} eq 'ARRAY'){
#													push(@$color,@{$DEF_COLOR->{$cm_cdi_name}});
#												}else{
#													print STDERR __LINE__.":Unknown color [$art_id][$art_hist_serial]\n";
#												}
#											}else{
#												print STDERR __LINE__.":Unknown cdi_name [$art_id][$art_hist_serial][$target_cdi_name]\n";
#											}
#										}

										if(USE_BP3D_COLOR){
											if(exists $DEF_COLOR_ART->{$art_id} && exists $DEF_COLOR_ART->{$art_id}->{$art_hist_serial} && ref $DEF_COLOR_ART->{$art_id}->{$art_hist_serial} eq 'ARRAY'){
												push(@$color,@{$DEF_COLOR_ART->{$art_id}->{$art_hist_serial}});
												$use_bp3d_color = 1;
											}else{
												foreach my $but_cid (@$but_cids_arr){
													next unless(exists $DEF_COLOR_CDI->{$but_cid});
													push(@$color,@{$DEF_COLOR_CDI->{$but_cid}});
													$use_bp3d_color = 1;
													last
												}
												print STDERR __LINE__.":Unknown color [$art_id][$art_hist_serial]\n" unless(defined $color);
											}
										}

										unless(exists $use_objs{$objfile}){
											push(@$obj_files1,{
												path => $objfile,
												color => $color
											});
										}
									}
									$sth->finish;
									undef $sth;

									%use_objs = map {$_->{'path'}=>undef} @$obj_files1;
								}
							}

							if(USE_BP3D_COLOR && DEBUG_USE_BP3D_COLOR){
								unless(defined $use_bp3d_color){
									close($TXT);
									unlink $txt_file if(-z $txt_file);
									exit(0);
								}
							}

							print __LINE__,":obj_files1=[",(scalar @$obj_files1),"]\n" if(defined $obj_files1 && ref $obj_files1 eq 'ARRAY');
#							exit;



							$sth_history_art_file->execute($md_id,$mv_id,$mr_id,$t_type,$base_b_id->{$tree}) or die $dbh->errstr;
							print __LINE__,":\$rows=[",$sth_history_art_file->rows(),"]\n";
							my $column_number = 0;
							$sth_history_art_file->bind_col(++$column_number, \$art_id, undef);
							$sth_history_art_file->bind_col(++$column_number, \$art_ext, undef);
							$sth_history_art_file->bind_col(++$column_number, \$art_hist_serial, undef);
							while($sth_history_art_file->fetch){
								next unless(defined $art_id && defined $art_ext && defined $art_hist_serial);
								my $objfile = sprintf($art_file_fmt,$art_id,$art_hist_serial,$art_ext);
								next unless(-e $objfile);
								next if(exists $use_objs{$objfile});
								push(@$obj_files2,$objfile);
							}
							$sth_history_art_file->finish;

							print __LINE__,":obj_files2=[",(scalar @$obj_files2),"]\n" if(defined $obj_files2);


							my $bp3d_objs = &load_art_file(md_id=>$md_id,mv_id=>$mv_id,mr_id=>$mr_id);
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

							if(defined $obj_files1){

								my $largerbbox = [];
								my $b1 = $obj2image->bound($obj_files1);
								foreach my $v (@$b1){
									$v+=0;
								}

				#				next unless($b1->[4] >= $STANDARD_BBOX{$STANDARD_B_ID[0]}->[4]);#頭の部分
				#				next unless($b1->[4] >= $STANDARD_BBOX{$STANDARD_B_ID[1]}->[4]);#頸の部分
				#				next unless($b1->[5] <= $STANDARD_BBOX{$STANDARD_B_ID[4]}->[5]);#短趾屈筋の部分
				#				next unless($b1->[5] <= $STANDARD_BBOX{$STANDARD_B_ID[4]}->[5]);#足の部分


								print __LINE__,":\$target_cdi_name=$target_cdi_name\n";
								print __LINE__,":\$b1=[",join(",",@$b1),"]\n";

								foreach my $b_id (keys(%STANDARD_BBOX)){

									for(my $i=0;$i<scalar @$b1;$i++){
										if($i<4){
											next;
											#min
											if($STANDARD_BBOX{$b_id}->[$i] < $b1->[$i] && (!defined $largerbbox->[$i] || $STANDARD_BBOX{$b_id}->[$i] > $largerbbox->[$i])){
												$largerbbox->[$i] = $STANDARD_BBOX{$b_id}->[$i];
				#								$largerbbox->[$i+1] = $STANDARD_BBOX{$b_id}->[$i+1];
											}
											$i++;
											#max
											if($STANDARD_BBOX{$b_id}->[$i] > $b1->[$i] && (!defined $largerbbox->[$i] || $STANDARD_BBOX{$b_id}->[$i] < $largerbbox->[$i])){
				#								$largerbbox->[$i-1] = $STANDARD_BBOX{$b_id}->[$i-1];
												$largerbbox->[$i] = $STANDARD_BBOX{$b_id}->[$i];
											}
										}elsif(
											$b_id eq $STANDARD_B_ID[0] ||
											$b_id eq $STANDARD_B_ID[1] ||
											$b_id eq $STANDARD_B_ID[2]
										){
											#min
											if($STANDARD_BBOX{$b_id}->[$i] <= $b1->[$i] && (!defined $largerbbox->[$i] || $STANDARD_BBOX{$b_id}->[$i] > $largerbbox->[$i])){
												$largerbbox->[$i] = $STANDARD_BBOX{$b_id}->[$i];
											}
											$i++;
											#max
											if($STANDARD_BBOX{$b_id}->[$i] > $b1->[$i] && (!defined $largerbbox->[$i] || $STANDARD_BBOX{$b_id}->[$i] < $largerbbox->[$i])){
												$largerbbox->[$i] = $STANDARD_BBOX{$b_id}->[$i];
											}
										}else{
											#min
											if($STANDARD_BBOX{$b_id}->[$i] < $b1->[$i] && (!defined $largerbbox->[$i] || $STANDARD_BBOX{$b_id}->[$i] > $largerbbox->[$i])){
												$largerbbox->[$i] = $STANDARD_BBOX{$b_id}->[$i];
											}
											$i++;
											#max
											if($STANDARD_BBOX{$b_id}->[$i] >= $b1->[$i] && (!defined $largerbbox->[$i] || $STANDARD_BBOX{$b_id}->[$i] < $largerbbox->[$i])){
												$largerbbox->[$i] = $STANDARD_BBOX{$b_id}->[$i];
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
										$z_bbox->{'xmin'} = $Z_BBOX{$zr}->{'xmin'} if($Z_BBOX{$zr}->{'xmin'} < $z_bbox->{'xmin'});
										$z_bbox->{'xmax'} = $Z_BBOX{$zr}->{'xmax'} if($Z_BBOX{$zr}->{'xmax'} > $z_bbox->{'xmax'});
										$z_bbox->{'ymin'} = $Z_BBOX{$zr}->{'ymin'} if($Z_BBOX{$zr}->{'ymin'} < $z_bbox->{'ymin'});
										$z_bbox->{'ymax'} = $Z_BBOX{$zr}->{'ymax'} if($Z_BBOX{$zr}->{'ymax'} > $z_bbox->{'ymax'});
										$z_bbox->{'zmin'} = $Z_BBOX{$zr}->{'zmin'} if($Z_BBOX{$zr}->{'zmin'} < $z_bbox->{'zmin'});
										$z_bbox->{'zmax'} = $Z_BBOX{$zr}->{'zmax'} if($Z_BBOX{$zr}->{'zmax'} > $z_bbox->{'zmax'});
									}else{
										$z_bbox = {
											xmin => $Z_BBOX{$zr}->{'xmin'},
											xmax => $Z_BBOX{$zr}->{'xmax'},
											ymin => $Z_BBOX{$zr}->{'ymin'},
											ymax => $Z_BBOX{$zr}->{'ymax'},
											zmin => $Z_BBOX{$zr}->{'zmin'},
											zmax => $Z_BBOX{$zr}->{'zmax'}
										};
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
								print __LINE__,":\$largerbbox=[",join(",",@$largerbbox),"]\n";

				#			fmax = max(abs(fontBounds[0]-fontBounds[1]),abs(fontBounds[2]-fontBounds[3]),abs(fontBounds[4]-fontBounds[5]))
				#				my $fmax = abs($largerbbox->[4]-$largerbbox->[5]);
								my $fmax = &List::Util::max(abs($largerbbox->[0]-$largerbbox->[1]),abs($largerbbox->[2]-$largerbbox->[3]),abs($largerbbox->[4]-$largerbbox->[5]));
				#				my $bmax = &List::Util::max(abs($all_bound->[0]-$all_bound->[1]),abs($all_bound->[2]-$all_bound->[3]),abs($all_bound->[4]-$all_bound->[5]));
								print __LINE__,":\$fmax=[",$fmax,"]\n";

								my $fzoom = &getYRangeZoom($fmax);
				#				my $bzoom = &getYRangeZoom($bmax);

				#				my $fzoom1 = floor($fzoom/0.2) * 0.2;
								my $fzoom1 = ($fzoom>0) ? $fzoom-0.1 : $fzoom;
				#				my $bzoom1 = floor($bzoom/0.2) * 0.2;

								my $largerbboxYRange = &getZoomYRange($fzoom1);

								print __LINE__,":\$largerbboxYRange=[",$fmax,"][",$fzoom,"][",$fzoom1,"][",$largerbboxYRange,"]\n";
				#				print __LINE__,":\$bmax=[",$bmax,"][",$bzoom,"][",$bzoom1,"][",&getZoomYRange($bzoom1),"]\n";

								my $b1max = &List::Util::max(abs($b1->[0]-$b1->[1]),abs($b1->[2]-$b1->[3]),abs($b1->[4]-$b1->[5]));
								my $b1zoom = &getYRangeZoom($b1max);
				#				my $b1zoom1 = floor($b1zoom/0.2) * 0.2;
				#				$b1zoom1 -= 0.1 if($b1zoom1>0);
								my $b1zoom1 = ($b1zoom>0) ? $b1zoom-0.1 : $b1zoom;
								my $b1YRange = &getZoomYRange($b1zoom1);
								print __LINE__,":\$b1YRange=[",$b1max,"][",$b1zoom,"][",$b1zoom1,"][",$b1YRange,"]\n";

				#		scale = fmax*self.def_scale/bmax

				#				last;
				#				next;




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

								my @PNG_FILES = ();
								my @TARGET_PNG_FILES = ();

								for(my $i=0;$i<360;$i+=5){
									my $target_png_file = sprintf(qq|$dest_prefix\-%d-target.png|,$i);
									push(@TARGET_PNG_FILES,$target_png_file) if(-e $target_png_file && -s $target_png_file);

									my $png_file = sprintf(qq|$dest_prefix\-%d.png|,$i);
									if(-e $png_file && -s $png_file){
										push(@PNG_FILES,$png_file);
										next;
									}
									my $larger_png_file = sprintf(qq|$dest_prefix\-%d-larger.png|,$i);
									my $larger_size = int($sizeL->[0]*0.4) . 'x' . int($sizeL->[1]*0.4);
									if(-e $larger_png_file && -s $larger_png_file){
										my $hash = &Image::Info::image_info($larger_png_file);
										my $img_size = $hash->{width}.'x'.$hash->{height};
										system(qq|mogrify -transparent white -geometry $larger_size -sharpen 0.7 $larger_png_file|) if($larger_size ne $img_size);
									}
									system(qq|composite -gravity southeast $larger_png_file $target_png_file -quality 95 png8:$png_file|) if(-e $target_png_file && -s $target_png_file && -e $larger_png_file && -s $larger_png_file);
									push(@PNG_FILES,$png_file) if(-e $png_file && -s $png_file);
								}

								if(scalar @PNG_FILES < 72){

									my $t0 = [&Time::HiRes::gettimeofday()];

									$bb = $obj2image->obj2animgif($sizeL,$obj_files1,$obj_files2,$dest_prefix,$b1YRange,$largerbbox,$largerbboxYRange);

									my($epocsec,$microsec) = &Time::HiRes::tv_interval($t0,[&Time::HiRes::gettimeofday()]);
									my($sec,$min) = localtime($epocsec);
									print __LINE__,":",sprintf("%02d:%02d.%d",$min,$sec,$microsec),"\n";

									@PNG_FILES = ();
									@TARGET_PNG_FILES = ();

									for(my $i=0;$i<360;$i+=5){
										my $target_png_file = sprintf(qq|$dest_prefix\-%d-target.png|,$i);
										push(@TARGET_PNG_FILES,$target_png_file) if(-e $target_png_file && -s $target_png_file);

										my $png_file = sprintf(qq|$dest_prefix\-%d.png|,$i);
										if(-e $png_file && -s $png_file){
											push(@PNG_FILES,$png_file);
											next;
										}
										my $larger_png_file = sprintf(qq|$dest_prefix\-%d-larger.png|,$i);
										my $larger_size = int($sizeL->[0]*0.4) . 'x' . int($sizeL->[1]*0.4);
										if(-e $larger_png_file && -s $larger_png_file){
											my $hash = &Image::Info::image_info($larger_png_file);
											my $img_size = $hash->{width}.'x'.$hash->{height};
											system(qq|mogrify -transparent white -geometry $larger_size -sharpen 0.7 $larger_png_file|) if($larger_size ne $img_size);
										}
										system(qq|composite -gravity southeast $larger_png_file $target_png_file -quality 95 png8:$png_file|) if(-e $target_png_file && -s $target_png_file && -e $larger_png_file && -s $larger_png_file);
										if(-e $png_file && -s $png_file){
											push(@PNG_FILES,$png_file);
										}else{
											die __LINE__,":Unknown file [$png_file]\n";
										}
									}
								}

								my $gif_file = qq|$dest_prefix.gif|;
								system(qq|convert -dispose Background -delay 0 -loop 0 |.join(" ",@PNG_FILES).qq| $gif_file|) unless(-e $gif_file && -s $gif_file);
								utime $rep_entry,$rep_entry,$gif_file if(-e $gif_file && -s $gif_file);

								my $gif_file = qq|$dest_prefixM.gif|;
								system(qq|convert -geometry $sizeStrM -sharpen 0.7 -dispose Background -delay 0 -loop 0 |.join(" ",@PNG_FILES).qq| $gif_file|) unless(-e $gif_file && -s $gif_file);
								utime $rep_entry,$rep_entry,$gif_file if(-e $gif_file && -s $gif_file);

								my $gif_file = qq|$dest_prefixS.gif|;
								system(qq|convert -geometry $sizeStrS -sharpen 0.7 -dispose Background -delay 0 -loop 0 |.join(" ",@TARGET_PNG_FILES).qq| $gif_file|) unless(-e $gif_file && -s $gif_file);
								utime $rep_entry,$rep_entry,$gif_file if(-e $gif_file && -s $gif_file);

								my $gif_file = qq|$dest_prefixXS.gif|;
								system(qq|convert -geometry $sizeStrXS -sharpen 0.7 -dispose Background -delay 0 -loop 0 |.join(" ",@TARGET_PNG_FILES).qq| $gif_file|) unless(-e $gif_file && -s $gif_file);
								utime $rep_entry,$rep_entry,$gif_file if(-e $gif_file && -s $gif_file);

								unlink qq|$img_prefix.gif| if(-e qq|$img_prefix.gif|);
								symlink qq|$target_cdi_name\_$sizeStrM.gif|,qq|$img_prefix.gif| if(-e $imgsM->[0]);
								utime $rep_entry,$rep_entry,qq|$img_prefix.gif| if(-e qq|$img_prefix.gif| && -s qq|$img_prefix.gif|);

								my $angle = 0;
								my $png_file;
								$angle = 0;
								for(my $i=1;$i<=4;$i++){
									unless(-e $imgsL->[$i]){
										$png_file = sprintf(qq|$dest_prefix\-%d.png|,$angle);
										die __LINE__,":Unknown file [$png_file]\n" unless(-e $png_file);
										&File::Copy::copy($png_file,$imgsL->[$i]) if(-e $png_file);
									}
									utime $rep_entry,$rep_entry,$imgsL->[$i] if(-e $imgsL->[$i] && -s $imgsL->[$i]);

									unless(-e $imgsM->[$i]){
										if(-e $imgsL->[$i]){
											system(qq|convert -geometry $sizeStrM -sharpen 0.7 $imgsL->[$i] -quality 95 png8:$imgsM->[$i]|);
										}
									}
									utime $rep_entry,$rep_entry,$imgsM->[$i] if(-e $imgsM->[$i] && -s $imgsM->[$i]);

									my $target_png_file = sprintf(qq|$dest_prefix\-%d-target.png|,$angle);
									if(-e $target_png_file && -s $target_png_file){
										system(qq|convert -geometry $sizeStrS -sharpen 0.7 $target_png_file -quality 95 png8:$imgsS->[$i]|) unless(-e $imgsS->[$i] && -s $imgsS->[$i]);
										utime $rep_entry,$rep_entry,$imgsS->[$i] if(-e $imgsS->[$i] && -s $imgsS->[$i]);

										system(qq|convert -geometry $sizeStrXS -sharpen 0.7 $target_png_file -quality 95 png8:$imgsXS->[$i]|) unless(-e $imgsXS->[$i] && -s $imgsXS->[$i]);
										utime $rep_entry,$rep_entry,$imgsXS->[$i] if(-e $imgsXS->[$i] && -s $imgsXS->[$i]);
									}
									$angle += 90;
								}
	#exit;

								for($angle=0;$angle<360;$angle+=5){
									$png_file = sprintf(qq|$dest_prefix\-%d-target.png|,$angle);
									unlink $png_file if(-e $png_file);
									$png_file = sprintf(qq|$dest_prefix\-%d-larger.png|,$angle);
									unlink $png_file if(-e $png_file);
								}

	#exit;
								for($angle=0;$angle<360;$angle+=5){
									$png_file = sprintf(qq|$dest_prefix\-%d.png|,$angle);
									unlink $png_file if(-e $png_file);
								}
	#exit;



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
							}
							undef $obj_files1;
							undef $obj_files2;

							undef $obj2image;
							undef $bp3d_objs;
						}
						close($TXT);
						utime $rep_entry,$rep_entry,$txt_file if(-e $txt_file && -s $txt_file);
						undef $inter_files if(defined $inter_files);
#					}else{
#						undef $txt_file_lock if(defined $txt_file_lock);
					}
					eval{&unlink_inter_files();};
					exit 0;
				}

			}
		}
#		undef $obj2image;
#		undef $bp3d_objs;
#		last;
	}
}
exit;

sub getParentTreeNode {
	my $sth = shift;
	my $hash = shift;
	my $cdi_id = shift;
	my $bul_id = shift;

#	warn __LINE__.":[$cdi_id][$bul_id]\n";

	my $cdi_pids;
	my $cdi_pid;
	$sth->execute($cdi_id,$bul_id) or die $dbh->errstr;
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$cdi_pid,   undef);
	while($sth->fetch){
		next unless(defined $cdi_pid);
		next if(exists $hash->{$cdi_pid} && exists $hash->{$cdi_pid}->{$bul_id});
		next if($cdi_id eq $cdi_pid);
#		warn __LINE__.":\t[$cdi_pid]\n";
		$hash->{$cdi_pid}->{$bul_id} = undef;
		$cdi_pids->{$cdi_pid} = undef;
	}
	$sth->finish;

	foreach my $cdi_pid (keys(%$cdi_pids)){
		&getParentTreeNode($sth,$hash,$cdi_pid,$bul_id);
	}
}
