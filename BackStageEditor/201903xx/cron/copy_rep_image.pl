#!/bp3d/local/perl/bin/perl

$| = 1;
select(STDERR);
$| = 1;
select(STDOUT);

use strict;

die qq|$0 md_id prev_mv_id next_mv_id\n| unless scalar @ARGV == 3;

use File::Basename;
use File::Spec;
use File::Path;
use File::Copy;
use List::Util;
use Image::Info;

use FindBin;
my $htdocs_path;
BEGIN{
	use FindBin;
	$htdocs_path = qq|$FindBin::Bin/../htdocs_130910|;
	$htdocs_path = qq|$FindBin::Bin/../htdocs| unless(-e $htdocs_path);
#	print __LINE__,":BEGIN2!!\n";
}
use lib $FindBin::Bin,$htdocs_path;

require "webgl_common.pl";

my $dbh = &get_dbh();

#my $md_id=1;
#my $prev_mv_id=3;
#my $next_mv_id=4;

my $md_id = shift @ARGV;
my $prev_mv_id = shift @ARGV;
my $next_mv_id = shift @ARGV;

eval{
	my $find = qx|which find|;
	$find =~ s/\s*$//g;
	if(defined $find && -X $find){
		print __LINE__,qq|:$find\n|;
		my $sql=<<SQL;
select
 mr_version
from
 model_revision
where
 mr_delcause is null and
 mr_use and
 (md_id,mv_id,mr_id) in (
   select md_id,mv_id,max(mr_id) from model_revision where md_id=? and mv_id=? group by md_id,mv_id
 )
SQL
		my $sth_mr_sel = $dbh->prepare($sql) or die $dbh->errstr;

		$sth_mr_sel->execute($md_id,$prev_mv_id) or die $dbh->errstr;
		my $prev_mr_version;
		my $column_number = 0;
		$sth_mr_sel->bind_col(++$column_number, \$prev_mr_version, undef);
		$sth_mr_sel->fetch;
		$sth_mr_sel->finish;
		my $prev_img_prefix = &getRepImagePrefix($prev_mr_version) if(defined $prev_mr_version);

		$sth_mr_sel->execute($md_id,$next_mv_id) or die $dbh->errstr;
		my $next_mr_version;
		my $column_number = 0;
		$sth_mr_sel->bind_col(++$column_number, \$next_mr_version, undef);
		$sth_mr_sel->fetch;
		$sth_mr_sel->finish;
		my $next_img_prefix = &getRepImagePrefix($next_mr_version) if(defined $next_mr_version);

		if(defined $prev_img_prefix && -d $prev_img_prefix && defined $next_img_prefix){
			my $old = umask(0);
			my $cmd = qq|$find $prev_img_prefix/ -type f -or -type l|;
			print __LINE__,":$cmd\n";
			open(CMD,qq/$cmd |/) or die $!;
			while(<CMD>){
				chomp;
				my $old_path = $_;
				my $rel_path = File::Spec->abs2rel($old_path,$prev_img_prefix);
				my $new_path = File::Spec->catfile($next_img_prefix,$rel_path);
				next if(-e $new_path);

				my $new_dir = &File::Basename::dirname($new_path);
				&File::Path::mkpath($new_dir,0,0777) unless(-e $new_dir);
				if(-l $old_path){
					my $link_path = readlink($old_path);
					symlink $link_path,$new_path or die $! if(defined $link_path && !-e $new_path);
				}else{
					symlink $old_path,$new_path or die $! if(!-e $new_path);
				}
#				my($a,$u) = (stat($new_path))[8,9];
#				my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($u);
#				print sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec),"\n";
#				last;
			}
			close(CMD);
			umask($old);
		}
		exit;
	}
	my $rsync = qx|which rsync|;
	$rsync =~ s/\s*$//g;
	if(defined $rsync && -X $rsync){
		print __LINE__,qq|:$rsync\n|;
		my $sql=<<SQL;
select
 mr_version
from
 model_revision
where
 mr_delcause is null and
 mr_use and
 (md_id,mv_id,mr_id) in (
   select md_id,mv_id,max(mr_id) from model_revision where md_id=? and mv_id=? group by md_id,mv_id
 )
SQL
		my $sth_mr_sel = $dbh->prepare($sql) or die $dbh->errstr;

		$sth_mr_sel->execute($md_id,$prev_mv_id) or die $dbh->errstr;
		my $prev_mr_version;
		my $column_number = 0;
		$sth_mr_sel->bind_col(++$column_number, \$prev_mr_version, undef);
		$sth_mr_sel->fetch;
		$sth_mr_sel->finish;
		my $prev_img_prefix = &getRepImagePrefix($prev_mr_version) if(defined $prev_mr_version);

		$sth_mr_sel->execute($md_id,$next_mv_id) or die $dbh->errstr;
		my $next_mr_version;
		my $column_number = 0;
		$sth_mr_sel->bind_col(++$column_number, \$next_mr_version, undef);
		$sth_mr_sel->fetch;
		$sth_mr_sel->finish;
		my $next_img_prefix = &getRepImagePrefix($next_mr_version) if(defined $next_mr_version);

		if(defined $prev_img_prefix && -d $prev_img_prefix && defined $next_img_prefix){
			my $cmd = qq|$rsync -av $prev_img_prefix/ $next_img_prefix|;
			print $cmd,"\n";
#			system($cmd);
		}
		exit;
	}else{
		my $sql=<<SQL;
select
 rep.ci_id,
 rep.cb_id,
 rep.cdi_id,
 rep.bul_id,
 mr_version,
 cdi_name
from
 representation as rep

left join (
 select * from concept_data_info where cdi_delcause is null
) as cdi on cdi.ci_id=rep.ci_id and cdi.cdi_id=rep.cdi_id

left join (
 select * from model_revision where mr_delcause is null and mr_use
) as mr on mr.md_id=rep.md_id and mr.mv_id=rep.mv_id and mr.mr_id=rep.mr_id

where
 rep_delcause is null and
 (rep.ci_id,rep.cb_id,rep.cdi_id,rep.bul_id,rep.md_id,rep.mv_id,rep.mr_id) in (
   select ci_id,cb_id,cdi_id,bul_id,md_id,mv_id,max(mr_id) from representation where md_id=? and mv_id=? group by ci_id,cb_id,cdi_id,bul_id,md_id,mv_id
 )
order by
 rep.ci_id,
 rep.cb_id,
 rep.bul_id,
 cdi_name
SQL
		my $sth_rep_sel = $dbh->prepare($sql) or die $dbh->errstr;


		my $sql=<<SQL;
select
 mr_version,
 EXTRACT(EPOCH FROM rep_entry)
from
 representation as rep

left join (
 select * from concept_data_info where cdi_delcause is null
) as cdi on cdi.ci_id=rep.ci_id and cdi.cdi_id=rep.cdi_id

left join (
 select * from model_revision where mr_delcause is null and mr_use
) as mr on mr.md_id=rep.md_id and mr.mv_id=rep.mv_id and mr.mr_id=rep.mr_id

where
 rep_delcause is null and
 rep.ci_id=? and
 rep.cb_id=? and
 rep.cdi_id=? and
 rep.bul_id=? and
 rep.md_id=? and
 rep.mv_id=?
SQL
		my $sth_next_rep_sel = $dbh->prepare($sql) or die $dbh->errstr;


		$sth_rep_sel->execute($md_id,$prev_mv_id) or die $dbh->errstr;
		print __LINE__,":",$sth_rep_sel->rows(),"\n";
		my($ci_id,$cb_id,$cdi_id,$bul_id,$prev_mr_version,$cdi_name);
		my $column_number = 0;
		$sth_rep_sel->bind_col(++$column_number, \$ci_id, undef);
		$sth_rep_sel->bind_col(++$column_number, \$cb_id, undef);
		$sth_rep_sel->bind_col(++$column_number, \$cdi_id, undef);
		$sth_rep_sel->bind_col(++$column_number, \$bul_id, undef);
		$sth_rep_sel->bind_col(++$column_number, \$prev_mr_version, undef);
		$sth_rep_sel->bind_col(++$column_number, \$cdi_name, undef);
		while($sth_rep_sel->fetch){

			my $mv_version;
			my $new_rep_entry;
			$sth_next_rep_sel->execute($ci_id,$cb_id,$cdi_id,$bul_id,$md_id,$next_mv_id) or die $dbh->errstr;
			my $column_number = 0;
			$sth_next_rep_sel->bind_col(++$column_number, \$mv_version, undef);
			$sth_next_rep_sel->bind_col(++$column_number, \$new_rep_entry, undef);
			$sth_next_rep_sel->fetch;
			$sth_next_rep_sel->finish;

			next unless(defined $mv_version && defined $new_rep_entry);

			my $prev_img_prefix = &getRepImagePrefix($prev_mr_version,$bul_id,$cdi_name);
			my @prev_images = &getImageFileList($prev_img_prefix);
			my $is_copy;
			foreach my $path (@prev_images){
				next unless(-e $path && -s $path);
				$is_copy = 1;
				last;
			}
			if(defined $is_copy){
				my($next_img_prefix,$next_img_path) = &getRepImagePrefix($mv_version,$bul_id,$cdi_name);
				umask(0);
				&File::Path::mkpath($next_img_path,0,0777) unless(-e $next_img_path);
				print __LINE__,":\$next_img_path=[$next_img_path]\n";

				unshift(@prev_images,qq|$prev_img_prefix.gif|);
				unshift(@prev_images,qq|$prev_img_prefix.txt|);
				foreach my $path (@prev_images){
					next unless(-e $path && -s $path);
					my($img_name,$img_dir,$img_ext) = &File::Basename::fileparse($path);
					my $img_path = File::Spec->catfile($next_img_path,$img_name);
					unlink $img_path if(-e $img_path);
					if(-l $path){
						my $link_path = readlink($path);
						symlink $link_path,$img_path if(defined $link_path);
					}
					if(-f $path && !-e $img_path){
						&File::Copy::copy($path,$next_img_path) or die $!;
					}
					if(-e $img_path && -s $img_path){
						my($a,$u) = (stat($path))[8,9];
						utime $a,$u,$img_path;
					}else{
						die __LINE__,":file copy error!! [$img_path]\n";
					}
				}
		#		exit;
			}
		}
		$sth_rep_sel->finish;
	}
};
if($@){
	die __LINE__,":$@\n";
}
