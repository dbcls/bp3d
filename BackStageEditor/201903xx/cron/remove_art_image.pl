#!/bp3d/local/perl/bin/perl

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
use DBD::Pg;
use Data::Dumper;

use FindBin;
my $htdocs_path;
my $common_path;
BEGIN{
	use FindBin;
#	$htdocs_path = qq|$FindBin::Bin/../htdocs_130910|;
	$htdocs_path = qq|$FindBin::Bin/../htdocs| unless(-e $htdocs_path);

	$common_path = qq|/bp3d/ag-common/lib|;
}
use lib $FindBin::Bin,$htdocs_path,$common_path;

require "webgl_common.pl";

use renderer;

use constant {
	DEF_SERVER_NUMBRT => 98,
	MAX_PROG => 6,

	USE_BP3D_COLOR => 1,
	DEBUG_USE_BP3D_COLOR => 0
};

my @REMOVE_FMAID = qw/FMA61284 FMA23881 FMA85544 FMA71324/;

my $dbh = &get_dbh();

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

my $sth_but_cids = $dbh->prepare(qq|select cdi_name,bul_id,ci_id,but_cids from view_buildup_tree where but_delcause is null and cdi_name=?|) or die $dbh->errstr;
my %REMOVE_FMAID;
foreach my $remove_cdi_name (@REMOVE_FMAID){
	$sth_but_cids->execute($remove_cdi_name) or die $dbh->errstr;
	while(my $row = $sth_but_cids->fetchrow_hashref){
		next unless(defined $row->{'cdi_name'} && defined $row->{'bul_id'});
		$REMOVE_FMAID{$row->{'cdi_name'}}->{$row->{'bul_id'}} = undef;

		next unless(defined $row->{'ci_id'} && defined $row->{'but_cids'});
		my $ci_id = $row->{'ci_id'};
		my $but_cids = &JSON::XS::decode_json($row->{'but_cids'});
		my $sql_cdi = sprintf(qq|select cdi_name from concept_data_info where ci_id=$ci_id and cdi_id in (%s)|,join(",",@$but_cids));

		my $sth_cdi = $dbh->prepare($sql_cdi) or die $dbh->errstr;
		$sth_cdi->execute() or die $dbh->errstr;
		while(my $row_cdi = $sth_cdi->fetchrow_hashref){
			$REMOVE_FMAID{$row_cdi->{'cdi_name'}}->{$row->{'bul_id'}} = undef if(defined $row_cdi->{'cdi_name'});
		}
		$sth_cdi->finish;
		undef $sth_cdi;

	}
	$sth_but_cids->finish;

}
#my $sth_cdi_parent = $dbh->prepare(qq|select cdi_pname from view_buildup_tree where but_delcause is null and ci_id=$ci_id and cb_id=$cb_id and cdi_name=? and bul_id=?|) or die $dbh->errstr;
#foreach my $cdi_name (@REMOVE_FMAID){
#	&getParentTreeNode($sth_cdi_parent,\%REMOVE_FMAID,$cdi_name,$t_type);
#}
#print Dumper(\%REMOVE_FMAID);

undef $sth_but_cids;
#undef $sth_cdi_parent;
#exit;



#my $lib_path;
my $xvfb_lock;
my $display_size;
my $txt_file_lock;


my $inter_files;
sub sigexit {
	print __LINE__,":INT!![$txt_file_lock]\n";
	print __LINE__,":$@\n";
	eval{close(OUT);};
	if(defined $inter_files){
		foreach my $file (@$inter_files){
			unlink $file if(-e $file);
		}
	}
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
	my @extlist = qw|.pl|;
	my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);
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
	close($LOCK) if(defined $LOCK);
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
	my $m = umask(0);
	&File::Path::make_path($lock_dirpath,{verbose => 0, mode => 0777});
	umask($m);
}

my $lock_filefmt = qq|$cgi_name.lock-%d|;
my $lock_no=0;
my $LOCK;
for(;$lock_no<MAX_PROG;$lock_no++){
	my $lock_filepath = File::Spec->catdir($lock_dirpath,sprintf($lock_filefmt,$lock_no));
	print __LINE__,":\$lock_filepath=[$lock_filepath]\n";
	if(-e $lock_filepath){
		open($LOCK,"+< $lock_filepath") or die qq|[$lock_filepath]:$!|;
	}else{
		open($LOCK,"> $lock_filepath") or die qq|[$lock_filepath]:$!|;
	}
	last if(flock($LOCK, 6));
}
exit unless($lock_no<MAX_PROG);


my $art_file_prefix = File::Spec->catdir($FindBin::Bin,qq|art_file|);
unless(-e $art_file_prefix){
	my $m = umask(0);
	&File::Path::make_path($art_file_prefix,{verbose => 0, mode => 0777});
	umask($m);
}
my $art_file_fmt = qq|$art_file_prefix/%s-%d%s|;

my $ART_INFOS;
if(defined $ARGV[0] && -e $ARGV[0]){
	open(IN,"< $ARGV[0]") or die $!;
	flock(IN,1);
	my @DATAS = <IN>;
	close(IN);
	$ART_INFOS = &JSON::XS::decode_json(join('',@DATAS));
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
		my @ART_IDS;
		foreach my $art_info (@$ART_INFOS){
			push(@ART_IDS,$art_info->{'art_id'});
		}
		my $sql_fmt=<<SQL;
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
 art_data,
 art_data_size,
 EXTRACT(EPOCH FROM art_timestamp),
 hist_serial
from
 history_art_file
order by
 hist_timestamp desc
SQL
	}

	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	warn __LINE__,":\$sth->rows()=[",$sth->rows(),"]\n";
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$art_id, undef);
	$sth->bind_col(++$column_number, \$art_ext, undef);
	$sth->bind_col(++$column_number, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
	$sth->bind_col(++$column_number, \$art_data_size, undef);
	$sth->bind_col(++$column_number, \$art_timestamp, undef);
	$sth->bind_col(++$column_number, \$hist_serial, undef);
	while($sth->fetch){
		next unless(defined $art_id && defined $art_data  && defined $art_data_size && defined $art_timestamp && defined $hist_serial);
		my $objfile = sprintf($art_file_fmt,$art_id,$hist_serial,$art_ext);
		my $size = -s $objfile;
		my $mtime = 0;
		$mtime = (stat($objfile))[9] if(-e $objfile);
		unless(-e $objfile && $size == $art_data_size && $mtime>=$art_timestamp){
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
			utime($art_timestamp,$art_timestamp,$objfile);
#			push(@FILES,$objfile);
		}
		my $IN;
		open($IN,$objfile) or die "$!:$objfile\n";
		flock($IN,1);
		close($IN);
		$bp3d_objs->objReader($objfile,1.0);
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

my @extlist = qw|.pl|;
my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);


#my $version = qq|3.0|;
#my $tree = qq|bp3d|;
my $copyrightL = qq|$FindBin::Bin/img/copyrightM.png|;
my $copyrightS = qq|$FindBin::Bin/img/copyrightS.png|;


my $sql;
if(defined $ART_INFOS && ref $ART_INFOS eq 'ARRAY' && scalar @$ART_INFOS > 0){
	my @ART_IDS;
	foreach my $art_info (@$ART_INFOS){
		push(@ART_IDS,$art_info->{'art_id'});
	}
	my $sql_fmt=qq|select distinct art_id,art_ext,hist_serial,art_serial,EXTRACT(EPOCH FROM art_timestamp) from history_art_file where art_id in ('%s') order by art_serial desc,hist_serial desc|;
	$sql = sprintf($sql_fmt,join("','",@ART_IDS));
}else{
	$sql = qq|select distinct art_id,art_ext,hist_serial,art_serial,EXTRACT(EPOCH FROM art_timestamp) from history_art_file order by art_serial desc,hist_serial desc|;
}
my $sth_history_art_file = $dbh->prepare($sql) or die $dbh->errstr;

my $obj2image = &renderer::new_obj2image($bp3d_objs,1);
my $FOCUS_COLOR;
my $COLOR;
if(USE_BP3D_COLOR){
	push(@$FOCUS_COLOR,(1.0,0.3176470588235294,0.0));
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
	my $objfile = sprintf($art_file_fmt,$art_id,$art_hist_serial,$art_ext);
	next unless(-e $objfile && -s $objfile);
	push(@$obj_files1,{
		path => $objfile,
		art_id => $art_id,
		art_hist_serial => $art_hist_serial,
		timestamp => $art_timestamp
	});
}
$sth_history_art_file->finish;
undef $sth_history_art_file;



sub make_image {
	my $obj_file = shift;
	my $mr_version = shift;

	my $obj_path;
	my $obj_timestamp;
	if(ref $obj_file eq 'HASH'){
		$obj_path = $obj_file->{'path'};
		$obj_timestamp = $obj_file->{'timestamp'};
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
	print __LINE__,":\$txt_file=[",$txt_file,"][",(-e $txt_file ? 1 : 0),"][",(-s $txt_file),"]\n";

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
	my $chk;
	foreach my $chk_file (@chk_files){
#		print qq|unlink $chk_file|."\n";
		unlink $chk_file;
	}

	unless(defined $chk){
		&File::Path::remove_tree($txt_file_lock) if(defined $txt_file_lock && -e $txt_file_lock && -d $txt_file_lock);
		$txt_file_lock = undef;
		return;
	}
	return;

	if(open(OUT,"> $txt_file")){
		if(flock(OUT, 6)){

			foreach my $chk_file (@chk_files){
				next unless(-e $chk_file);
				unlink $chk_file if(-e $chk_file && $chk_file ne $txt_file);
			}

			my $largerbbox = [];
			my $b1 = $obj2image->bound([$obj_file]);
			foreach my $v (@$b1){
				$v+=0;
			}

			print __LINE__,":\$obj_path=$obj_path\n";
			print __LINE__,":\$b1=[",join(",",@$b1),"]\n";

			for(my $i=0;$i<scalar @$b1;$i++){
				$largerbbox->[$i] = $b1->[$i] unless(defined $largerbbox->[$i]);
			}
			print __LINE__,":\$largerbbox=[",join(",",@$largerbbox),"]\n";

			my $fmax = &List::Util::max(abs($largerbbox->[0]-$largerbbox->[1]),abs($largerbbox->[2]-$largerbbox->[3]),abs($largerbbox->[4]-$largerbbox->[5]));
			my $fzoom = &getYRangeZoom($fmax);
			my $fzoom1 = ($fzoom>0) ? $fzoom-0.1 : $fzoom;
			my $largerbboxYRange = &getZoomYRange($fzoom1);

			print __LINE__,":\$largerbboxYRange=[",$fmax,"][",$fzoom,"][",$fzoom1,"][",$largerbboxYRange,"]\n";

			my $b1max = &List::Util::max(abs($b1->[0]-$b1->[1]),abs($b1->[2]-$b1->[3]),abs($b1->[4]-$b1->[5]));
			my $b1zoom = &getYRangeZoom($b1max);

			my $b1zoom1 = ($b1zoom>0) ? $b1zoom-0.1 : $b1zoom;
			my $b1YRange = &getZoomYRange($b1zoom1);
			print __LINE__,":\$b1YRange=[",$b1max,"][",$b1zoom,"][",$b1zoom1,"][",$b1YRange,"]\n";

			undef $inter_files if(defined $inter_files);


			push(@$inter_files,$txt_file);

			my $bb;




			push(@$inter_files,@$imgsL);

			my $dest_prefix = sprintf($gif_prefix_fmt,$img_prefix,$sizeStrL);
			$bb = $obj2image->obj2animgif($sizeL,[$obj_file],undef,$dest_prefix,$b1YRange,undef,undef) unless(-e $imgsL->[0]);

			my @PNG_FILES = ();

			for(my $i=0;$i<360;$i+=5){
				my $target_png_file = sprintf(qq|$dest_prefix\-%d-target.png|,$i);
				my $png_file = sprintf(qq|$dest_prefix\-%d.png|,$i);
				system(qq|convert $target_png_file -quality 95 png8:$png_file|) if(-e $target_png_file && -s $target_png_file);
				if(-e $png_file && -s $png_file){
					push(@PNG_FILES,$png_file);
				}else{
					die __LINE__,":Unknown file [$png_file]\n";
				}
			}

			my $gif_file = qq|$dest_prefix.gif|;
			system(qq|convert -dispose Background -delay 0 -loop 0 |.join(" ",@PNG_FILES).qq| $gif_file|) unless(-e $gif_file && -s $gif_file);
			utime $obj_timestamp,$obj_timestamp,$gif_file if(defined $obj_timestamp && -e $gif_file && -s $gif_file);

#exit;
			my $angle = 0;
			my $png_file;
			for(my $i=1;$i<=4;$i++){
				unless(-e $imgsL->[$i]){
					my $png_file = qq|$dest_prefix\-$angle.png|;
					die __LINE__,":Unknown file [$png_file]\n" unless(-e $png_file);
					&File::Copy::copy($png_file,$imgsL->[$i]) if(-e $png_file);
					utime $obj_timestamp,$obj_timestamp,$imgsL->[$i] if(defined $obj_timestamp && -e $imgsL->[$i] && -s $imgsL->[$i]);
				}
				$angle += 90;
			}

			for($angle=0;$angle<360;$angle+=5){
				my $target_png_file = sprintf(qq|$dest_prefix\-%d-target.png|,$angle);
				my $png_file = qq|$dest_prefix\-$angle.png|;
				unlink $target_png_file if(-e $target_png_file);
				unlink $png_file if(-e $png_file);
			}
#exit;

			push(@$inter_files,@$imgsM);


			my $dest_prefix = sprintf($gif_prefix_fmt,$img_prefix,$sizeStrM);
			unless(-e $imgsM->[0]){
				system(qq|convert -geometry $sizeStrM -sharpen 0.7 $imgsL->[0] $imgsM->[0]|) if(-e $imgsL->[0]);
				utime $obj_timestamp,$obj_timestamp,$imgsM->[0] if(defined $obj_timestamp && -e $imgsM->[0] && -s $imgsM->[0]);
			}
			unlink qq|$img_prefix.gif| if(-e qq|$img_prefix.gif|);
			symlink qq|$obj_name\_$sizeStrM.gif|,qq|$img_prefix.gif| if(-e $imgsM->[0]);
			push(@$inter_files,qq|$img_prefix.gif|);

			$angle = 0;
			for(my $i=1;$i<=4;$i++){
				unless(-e $imgsM->[$i]){
					if(-e $imgsL->[$i]){
						system(qq|convert -geometry $sizeStrM -sharpen 0.7 $imgsL->[$i] -quality 95 png8:$imgsM->[$i]|);
						utime $obj_timestamp,$obj_timestamp,$imgsM->[$i] if(defined $obj_timestamp && -e $imgsM->[$i] && -s $imgsM->[$i]);
					}else{
						$png_file = qq|$dest_prefix\-$angle.png|;
						die __LINE__,":Unknown file [$png_file]\n" unless(-e $png_file);
						&File::Copy::copy($png_file,$imgsM->[$i]) if(-e $png_file);
						utime $obj_timestamp,$obj_timestamp,$imgsM->[$i] if(defined $obj_timestamp && -e $imgsM->[$i] && -s $imgsM->[$i]);
					}
				}
				$angle += 90;
			}
			for($angle=0;$angle<360;$angle+=5){
				$png_file = qq|$dest_prefix\-$angle.png|;
				unlink $png_file if(-e $png_file);
			}





			push(@$inter_files,@$imgsS);

			my $dest_prefix = sprintf($gif_prefix_fmt,$img_prefix,$sizeStrS);

			unless(-e $imgsS->[0]){
				system(qq|convert -geometry $sizeStrS -sharpen 0.7 $imgsL->[0] $imgsS->[0]|) if(-e $imgsL->[0]);
				utime $obj_timestamp,$obj_timestamp,$imgsS->[0] if(defined $obj_timestamp && -e $imgsS->[0] && -s $imgsS->[0]);
			}

			$angle = 0;
			for(my $i=1;$i<=4;$i++){
				unless(-e $imgsS->[$i]){
					if(-e $imgsL->[$i]){
						system(qq|convert -geometry $sizeStrS -sharpen 0.7 $imgsL->[$i] -quality 95 png8:$imgsS->[$i]|);
						utime $obj_timestamp,$obj_timestamp,$imgsS->[$i] if(defined $obj_timestamp && -e $imgsS->[$i] && -s $imgsS->[$i]);
					}else{
						$png_file = qq|$dest_prefix\-$angle.png|;
						die __LINE__,":Unknown file [$png_file]\n" unless(-e $png_file);
						&File::Copy::copy($png_file,$imgsS->[$i]) if(-e $png_file);
						utime $obj_timestamp,$obj_timestamp,$imgsS->[$i] if(defined $obj_timestamp && -e $imgsS->[$i] && -s $imgsS->[$i]);
					}
				}
				$angle += 90;
			}
			for($angle=0;$angle<360;$angle+=5){
				$png_file = qq|$dest_prefix\-$angle.png|;
				unlink $png_file if(-e $png_file);
			}




			push(@$inter_files,@$imgsXS);


			my $dest_prefix = sprintf($gif_prefix_fmt,$img_prefix,$sizeStrXS);

			unless(-e $imgsXS->[0]){
				system(qq|convert -geometry $sizeStrXS -sharpen 0.7 $imgsL->[0] $imgsXS->[0]|) if(-e $imgsL->[0]);
				utime $obj_timestamp,$obj_timestamp,$imgsXS->[0] if(defined $obj_timestamp && -e $imgsXS->[0] && -s $imgsXS->[0]);
			}

			$angle = 0;
			for(my $i=1;$i<=4;$i++){
				unless(-e $imgsXS->[$i]){
					if(-e $imgsL->[$i]){
						system(qq|convert -geometry $sizeStrXS -sharpen 0.7 $imgsL->[$i] -quality 95 png8:$imgsXS->[$i]|);
						utime $obj_timestamp,$obj_timestamp,$imgsXS->[$i] if(defined $obj_timestamp && -e $imgsXS->[$i] && -s $imgsXS->[$i]);
					}else{
						$png_file = qq|$dest_prefix\-$angle.png|;
						die __LINE__,":Unknown file [$png_file]\n" unless(-e $png_file);
						&File::Copy::move($png_file,$imgsXS->[$i]) if(-e $png_file);
						utime $obj_timestamp,$obj_timestamp,$imgsXS->[$i] if(defined $obj_timestamp && -e $imgsXS->[$i] && -s $imgsXS->[$i]);
					}
				}
				$angle += 90;
			}
			for($angle=0;$angle<360;$angle+=5){
				$png_file = qq|$dest_prefix\-$angle.png|;
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
		}
		close(OUT);
		utime $obj_timestamp,$obj_timestamp,$txt_file if(defined $obj_timestamp && -e $txt_file && -s $txt_file);

	}
	undef $inter_files if(defined $inter_files);
	&File::Path::remove_tree($txt_file_lock) if(defined $txt_file_lock && -e $txt_file_lock && -d $txt_file_lock);
	$txt_file_lock = undef;
}

if(defined $obj_files1){

	my $sql = qq|
select
 cdi_name,
 mr_version,
 EXTRACT(EPOCH FROM GREATEST(cm.cm_entry,cm.art_timestamp))

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
where
 cm_use and cm_delcause is null and
 mr_use and mr_delcause is null and
 mv_use and mv_frozen and mv_delcause is null and mv_publish and
 art_id=? and art_hist_serial=?
|;
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;

	my $DEF_COLOR;
	my $DEF_COLOR_ART;
	my $DEF_TIMESTAMP_ART;

	foreach my $o (@$obj_files1){
		my $art_id = $o->{'art_id'};
#		next if($art_id ne 'FJ6459');
		my $art_hist_serial = $o->{'art_hist_serial'};
		if(USE_BP3D_COLOR){
			$sth->execute($art_id,$art_hist_serial) or die $dbh->errstr;
			if($sth->rows()>0){
				my $cdi_name;
				my $mr_version;
				my $timestamp;
				my $column_number = 0;
				$sth->bind_col(++$column_number, \$cdi_name, undef);
				$sth->bind_col(++$column_number, \$mr_version, undef);
				$sth->bind_col(++$column_number, \$timestamp, undef);
				while($sth->fetch){
#					next if($mr_version ne '4.3.1403311232');
					next unless(exists $REMOVE_FMAID{$cdi_name});
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
					$DEF_TIMESTAMP_ART->{$art_id}->{$art_hist_serial}->{$mr_version} = $timestamp;
				}
			}
			$sth->finish;
		}
		$o->{'color'} = undef;
#		$o->{'timestamp'} = undef;
#		&make_image($o);
		if(USE_BP3D_COLOR){
			if(defined $DEF_COLOR_ART && exists $DEF_COLOR_ART->{$art_id} && exists $DEF_COLOR_ART->{$art_id}->{$art_hist_serial} && ref $DEF_COLOR_ART->{$art_id}->{$art_hist_serial} eq 'HASH'){
#				&make_image($o);
				foreach my $mr_version (sort {$b <=> $a} keys(%{$DEF_COLOR_ART->{$art_id}->{$art_hist_serial}})){
					$o->{'color'} = $DEF_COLOR_ART->{$art_id}->{$art_hist_serial}->{$mr_version};
					$o->{'timestamp'} = $DEF_TIMESTAMP_ART->{$art_id}->{$art_hist_serial}->{$mr_version};
					&make_image($o,$mr_version);
				}
			}
		}else{
#			&make_image($o);
		}
	}
	undef $sth;
	undef $obj_files1;
}
undef $obj2image;


exit;
