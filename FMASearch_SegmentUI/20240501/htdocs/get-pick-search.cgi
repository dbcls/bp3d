#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use JSON::XS;
use File::Basename;
use Cwd qw(abs_path);
use File::Spec::Functions qw(catdir catfile);
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use Data::Dumper;
use DBD::Pg;
use POSIX;
use Time::HiRes;

use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'..','cgi_lib'),q|/bp3d/ag-common/lib|;
use BITS::Config;
use BITS::VTK;

require "webgl_common.pl";
use cgi_lib::common;

my $t0 = [&Time::HiRes::gettimeofday()];

my $query = CGI->new;
my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);
my($log_file,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

#my @extlist = qw|.cgi|;
#my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);

#my $log_file = qq|$FindBin::Bin/logs/$cgi_name.txt|;
$log_file .= qq|.$FORM{'cmd'}| if(exists $FORM{'cmd'});

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
#$log_file .= '.'.sprintf("%04d%02d%02d%02d.%05d",$year+1900,$mon+1,$mday,$hour);
$log_file .=  sprintf(".%02d%02d%02d.%05d",$hour,$min,$sec,$$);

open(my $LOG,">> $log_file");
select($LOG);
$| = 1;
select(STDOUT);

my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
print $LOG "\n[$logtime]:$0\n";

foreach my $key (sort keys(%FORM)){
	print $LOG __LINE__,qq|:\$FORM{$key}=[$FORM{$key}]\n|;
}
foreach my $key (sort keys(%ENV)){
	print $LOG __LINE__,qq|:\$ENV{$key}=[$ENV{$key}]\n|;
}

$FORM{'cmd'} = 'read' unless(defined $FORM{'cmd'});
#$FORM{'start'} = 0 unless(defined $FORM{'start'});
$FORM{'limit'} = 50 unless(defined $FORM{'limit'});

#$FORM{'name'} = qq|120406_liver_divided01_obj|;

#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $DATAS = {
	'datas'   => [],
	'total'   => 0,
	'msg'     => undef,
	'success' => JSON::XS::false
};

my $ci_id=$FORM{&BITS::Config::LOCATION_HASH_CIID_KEY()};
my $cb_id=$FORM{&BITS::Config::LOCATION_HASH_CBID_KEY()};
my $md_id=$FORM{&BITS::Config::LOCATION_HASH_MDID_KEY()};
my $mv_id=$FORM{&BITS::Config::LOCATION_HASH_MVID_KEY()};
my $mr_id=$FORM{&BITS::Config::LOCATION_HASH_MRID_KEY()};

$md_id=1 unless(defined $md_id && $md_id =~ /^[1-9][0-9]*$/);
unless(defined $mv_id && $mv_id =~ /^[1-9][0-9]*$/){
	$mv_id = undef;
	$ci_id = undef;
	$cb_id = undef;
	my $sth_mv;
	if(defined $FORM{&BITS::Config::LOCATION_HASH_MVID_KEY()} && $FORM{&BITS::Config::LOCATION_HASH_MVID_KEY()} =~ /^\-[1-9][0-9]*$/){
		$sth_mv = $dbh->prepare("select mv_id from model_version where mv_delcause is null and mv_use and md_id=? order by mv_id desc limit 2") or die $dbh->errstr;
		$sth_mv->execute($md_id) or die $dbh->errstr;
		if($sth_mv->rows()>1){
			$sth_mv->bind_col(1, \$mv_id, undef);
			while($sth_mv->fetch){}
		}
		$sth_mv->finish;
		undef $sth_mv;
	}else{
		$sth_mv = $dbh->prepare("select max(mv_id) from model_version where mv_delcause is null and mv_use and md_id=?") or die $dbh->errstr;
		$sth_mv->execute($md_id) or die $dbh->errstr;
		$sth_mv->bind_col(1, \$mv_id, undef);
		$sth_mv->fetch;
		$sth_mv->finish;
		undef $sth_mv;
	}
	if(defined $mv_id){
		$sth_mv = $dbh->prepare("select ci_id,cb_id from model_version where md_id=? and mv_id=?") or die $dbh->errstr;
		$sth_mv->execute($md_id,$mv_id) or die $dbh->errstr;
		$sth_mv->bind_col(1, \$ci_id, undef);
		$sth_mv->bind_col(2, \$cb_id, undef);
		$sth_mv->fetch;
		$sth_mv->finish;
		undef $sth_mv;
	}
}

unless(defined $ci_id && defined $cb_id && defined $md_id && defined $mv_id){
	$DATAS->{'success'} = JSON::XS::true;
	&cgi_lib::common::printContentJSON($DATAS,\%FORM);
	close($LOG) if(defined $LOG);
	exit;
}
if(defined $LOG){
	&cgi_lib::common::message('$md_id='.$md_id, $LOG);
	&cgi_lib::common::message('$mv_id='.$mv_id, $LOG);
	&cgi_lib::common::message('$mr_id='.$mr_id, $LOG);
	&cgi_lib::common::message('$ci_id='.$ci_id, $LOG);
	&cgi_lib::common::message('$cb_id='.$cb_id, $LOG);
}
$FORM{&BITS::Config::LOCATION_HASH_CIID_KEY()}=$ci_id;
$FORM{&BITS::Config::LOCATION_HASH_CBID_KEY()}=$cb_id;
$FORM{&BITS::Config::LOCATION_HASH_MDID_KEY()}=$md_id;
$FORM{&BITS::Config::LOCATION_HASH_MVID_KEY()}=$mv_id;

if($FORM{'cmd'} eq 'read'){
	eval{
		my $target_art_point_x;
		my $target_art_point_y;
		my $target_art_point_z;
		my $voxel_range = $FORM{&BITS::Config::VOXEL_RANGE_FIELD_ID()} || 10;
#		my $voxel_range = 50;
		my $parts_map;

		my $conditions;
		$conditions = &cgi_lib::common::decodeJSON($FORM{&BITS::Config::CONDITIONS_FIELD_ID()}) if(exists $FORM{&BITS::Config::CONDITIONS_FIELD_ID()} && defined $FORM{&BITS::Config::CONDITIONS_FIELD_ID()});
&cgi_lib::common::message($conditions, $LOG) if(defined $LOG);
		if(defined $conditions && ref $conditions eq 'HASH' && $conditions->{'parts_map'} eq JSON::XS::true){
			$parts_map = 1;
			$ci_id = $FORM{&BITS::Config::LOCATION_HASH_CIID_KEY()} if(exists $FORM{&BITS::Config::LOCATION_HASH_CIID_KEY()} && defined $FORM{&BITS::Config::LOCATION_HASH_CIID_KEY()});
		}

		my $where_map = '';
		{
			my @w;
			push(@w,'ci_id='.$FORM{&BITS::Config::LOCATION_HASH_CIID_KEY()}) if(exists $FORM{&BITS::Config::LOCATION_HASH_CIID_KEY()} && defined $FORM{&BITS::Config::LOCATION_HASH_CIID_KEY()});
			$where_map = qq| AND | . join(" AND ",@w);
			undef @w;
		}

		my $art_point;
		$art_point = &cgi_lib::common::decodeJSON($FORM{&BITS::Config::OBJ_POINT_FIELD_ID()}) if(exists $FORM{&BITS::Config::OBJ_POINT_FIELD_ID()} && defined $FORM{&BITS::Config::OBJ_POINT_FIELD_ID()});

		if(defined $art_point && ref $art_point eq 'HASH'){
			$target_art_point_x = $art_point->{'x'};
			$target_art_point_y = $art_point->{'y'};
			$target_art_point_z = $art_point->{'z'};
		}
		if(defined $target_art_point_x && defined $target_art_point_y && defined $target_art_point_z){
#			my $sql = qq|select distinct voxel_id from voxel_data where voxel_id in (select voxel_id from voxel_index where voxel_x>=? AND voxel_x<=? AND voxel_y>=? AND voxel_y<=? AND voxel_z>=? AND voxel_z<=?)|;
#			my $sql = qq|select voxel_id,voxel_x,voxel_y,voxel_z from voxel_index where voxel_x>=? AND voxel_x<=? AND voxel_y>=? AND voxel_y<=? AND voxel_z>=? AND voxel_z<=?|;
			my $sql = qq|select voxel_id from voxel_index where voxel_x>=? AND voxel_x<=? AND voxel_y>=? AND voxel_y<=? AND voxel_z>=? AND voxel_z<=?|;
			my $sth = $dbh->prepare($sql) or die $dbh->errstr;
			my $p = $voxel_range/2;
			my @bind_values = ();
			push(@bind_values,floor($target_art_point_x-$p));
			push(@bind_values,ceil($target_art_point_x+$p));
			push(@bind_values,floor($target_art_point_y-$p));
			push(@bind_values,ceil($target_art_point_y+$p));
			push(@bind_values,floor($target_art_point_z-$p));
			push(@bind_values,ceil($target_art_point_z+$p));

&cgi_lib::common::message($sql, $LOG) if(defined $LOG);
&cgi_lib::common::message($p, $LOG) if(defined $LOG);
&cgi_lib::common::message(\@bind_values, $LOG) if(defined $LOG);

			$sth->execute(@bind_values) or die $dbh->errstr;
			my $target_voxel_ids;
			my $target_voxel_points;
			my $voxel_id;
#			my $voxel_x;
#			my $voxel_y;
#			my $voxel_z;
			my $column_number = 0;
			$sth->bind_col(++$column_number, \$voxel_id, undef);
#			$sth->bind_col(++$column_number, \$voxel_x, undef);
#			$sth->bind_col(++$column_number, \$voxel_y, undef);
#			$sth->bind_col(++$column_number, \$voxel_z, undef);
			while($sth->fetch){
				$target_voxel_ids->{$voxel_id} = undef if(defined $voxel_id);
#				push(@$target_voxel_points, [$voxel_x-0,$voxel_y-0,$voxel_z-0]);
			}
			$sth->finish;
			undef $sth;
#&cgi_lib::common::message($target_voxel_ids, $LOG) if(defined $LOG);
&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

			my $min_distance_hash;
			if(defined $target_voxel_ids){
=pod
				$sql = sprintf(qq|select distinct art_id from voxel_data where voxel_id in (%s)|,join(',',keys(%$target_voxel_ids)));
				$sth = $dbh->prepare($sql) or die $dbh->errstr;
				$sth->execute() or die $dbh->errstr;
				my $art_ids_hash;
				my $art_id;
				$column_number = 0;
				$sth->bind_col(++$column_number, \$art_id, undef);
				while($sth->fetch){
					$art_ids_hash->{$art_id} = undef;
				}
				$sth->finish;
				undef $sth;

				if(defined $art_ids_hash){
					foreach my $art_id (keys(%$art_ids_hash)){
						my $file = &catfile($FindBin::Bin,'art_file',$art_id.'.obj');
						my $inside_points = &BITS::VTK::pointsOutsideObject($file,$target_voxel_points);
						if(scalar @$inside_points){
							my $min_distance = &BITS::VTK::pointDistanceObject($file,[$target_art_point_x-0,$target_art_point_y-0,$target_art_point_z-0]);
#							$min_distance_hash->{$art_id} = $min_distance if($voxel_range/2>=$min_distance);
							unless(exists $min_distance_hash->{$art_id}){
								$min_distance_hash->{$art_id} = $min_distance;
							}
							elsif($min_distance_hash->{$art_id}>$min_distance){
								$min_distance_hash->{$art_id} = $min_distance;
							}
						}
					}
				}
=cut
				$sql = sprintf(qq|select art_id,art_xmin,art_xmax,art_ymin,art_ymax,art_zmin,art_zmax from voxel_data where voxel_id in (%s) group by art_id,art_xmin,art_xmax,art_ymin,art_ymax,art_zmin,art_zmax|,join(',',keys(%$target_voxel_ids)));
				$sth = $dbh->prepare($sql) or die $dbh->errstr;
				$sth->execute() or die $dbh->errstr;
				my $art_ids_hash;
				my $art_id;
				my $art_xmin;
				my $art_xmax;
				my $art_ymin;
				my $art_ymax;
				my $art_zmin;
				my $art_zmax;
				my $x1 = $target_art_point_x-0;
				my $y1 = $target_art_point_y-0;
				my $z1 = $target_art_point_z-0;
				$column_number = 0;
				$sth->bind_col(++$column_number, \$art_id, undef);
				$sth->bind_col(++$column_number, \$art_xmin, undef);
				$sth->bind_col(++$column_number, \$art_xmax, undef);
				$sth->bind_col(++$column_number, \$art_ymin, undef);
				$sth->bind_col(++$column_number, \$art_ymax, undef);
				$sth->bind_col(++$column_number, \$art_zmin, undef);
				$sth->bind_col(++$column_number, \$art_zmax, undef);
				while($sth->fetch){
					$art_ids_hash->{$art_id} = undef;

					my $x2 = ($art_xmax+$art_xmin)/2;
					my $y2 = ($art_ymax+$art_ymin)/2;
					my $z2 = ($art_zmax+$art_zmin)/2;
					my $distance = sqrt(($x2 - $x1) * ($x2 - $x1) + ($y2 - $y1) * ($y2 - $y1) + ($z2 - $z1) * ($z2 - $z1));
					unless(exists $min_distance_hash->{$art_id}){
						$min_distance_hash->{$art_id} = $distance;
					}
					elsif($min_distance_hash->{$art_id}>$distance){
						$min_distance_hash->{$art_id} = $distance;
					}

				}
				$sth->finish;
				undef $sth;


			}
&cgi_lib::common::message($min_distance_hash, $LOG) if(defined $LOG);
&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

			if(defined $target_voxel_ids){
				my $where_all = '';
#				if(defined $parts_map){
					$where_all = qq| AND cm.cdi_id is not null AND cm.ci_id=$ci_id AND cm.cb_id=$cb_id AND cm.md_id=$md_id AND cm.mv_id=$mv_id AND cm.mr_id=$mr_id|;
					if(defined $min_distance_hash){
#						my @ART_IDS = sort {$min_distance_hash->{$a} <=> $min_distance_hash->{$b}} keys(%$min_distance_hash);
						my @ART_IDS = sort {$min_distance_hash->{$a} <=> $min_distance_hash->{$b}} grep {$min_distance_hash->{$_} <= $voxel_range ? 1 : 0} keys(%$min_distance_hash);



#						if(exists $FORM{'limit'} && defined $FORM{'limit'} && scalar @ART_IDS > $FORM{'limit'}){
#							$#ART_IDS = $FORM{'limit'}-1;
#						}
						$where_all .= sprintf(qq| AND cm.art_id IN (%s)|,join(',',map {qq|'$_'|} @ART_IDS)) ;
					}
					else{
						$where_all .= qq| AND distance_voxel<=$voxel_range|;


					}
#				}
#&cgi_lib::common::message($parts_map, $LOG) if(defined $LOG);
&cgi_lib::common::message($where_all, $LOG) if(defined $LOG);
				my $sql_fmt =<<SQL;
select
 cdi.cdi_id,
 cdi.cdi_name,
 COALESCE(cd.cd_name,cdi.cdi_name_e),
 cdi.cdi_name_j,
 cdi.cdi_name_k,
 cdi.cdi_name_l,

 COALESCE(cd.cd_syn,cdi.cdi_syn_e),
 COALESCE(cd.cd_def,cdi.cdi_def_e),

-- arti.art_data_size,
-- arti.art_xmin,
-- arti.art_xmax,
-- arti.art_ymin,
-- arti.art_ymax,
-- arti.art_zmin,
-- arti.art_zmax,
-- arti.art_volume,

 art.art_data_size,
 art.art_xmin,
 art.art_xmax,
 art.art_ymin,
 art.art_ymax,
 art.art_zmin,
 art.art_zmax,
 art.art_volume,

 EXTRACT(EPOCH FROM arti.art_timestamp) as art_timestamp,

 arti.art_id,
 arti.art_name,
 arti.art_ext,

-- arti.art_comment,
-- arti.art_category,
-- arti.art_judge,
-- arti.art_class,

 arta.art_comment,
 arta.art_category,
 arta.art_judge,
 arta.art_class,

 cm.cmp_id,
 EXTRACT(EPOCH FROM cm.cm_entry) as cm_entry,

 seg_color,

 art.art_serial,

 min(distance_voxel) as distance_voxel
from
 art_file_info as arti

left join (
-- select art_id,art_serial from art_file
 select
  art_id,
  art_serial,
  art_data_size,
  art_xmin,
  art_xmax,
  art_ymin,
  art_ymax,
  art_zmin,
  art_zmax,
  art_volume
 from
  art_file
) as art on
   art.art_id=arti.art_id

left join (
 select * from art_annotation
) as arta on
   art.art_id=arta.art_id

--イメージへのパスを生成する為
left join (
 select * from concept_art_map
 where
  cm_delcause is null $where_map
) as cm on
   cm.art_id=arti.art_id

left join (
  select
   art_id,
   min(abs(sqrt(power(((art_xmin+art_xmax)/2) - $target_art_point_x,2)+power(((art_ymin+art_ymax)/2) - $target_art_point_y,2)+power(((art_zmin+art_zmax)/2) - $target_art_point_z,2)))) as distance_voxel
  from
   voxel_data
  where
   voxel_id in (%s)
  group by
   art_id

 ) as vd on
    arti.art_id=vd.art_id

left join (
   select * from concept_data_info where cdi_delcause is null
 ) as cdi on
    cm.ci_id=cdi.ci_id AND
    cm.cdi_id=cdi.cdi_id

LEFT JOIN (
  SELECT * FROM concept_data WHERE ci_id=$ci_id AND cb_id=$cb_id
 ) cd ON cd.cdi_id = cm.cdi_id
LEFT JOIN (
  SELECT seg_id, seg_color, seg_thum_bgcolor FROM concept_segment
 ) cs ON cd.seg_id = cs.seg_id

where
 (arti.art_id) in (
   select distinct art_id from voxel_data where voxel_id in (%s)
 )
 $where_all
group by
 cdi.cdi_id,
 cdi.cdi_name,
 COALESCE(cd.cd_name,cdi.cdi_name_e),
 cdi.cdi_name_j,
 cdi.cdi_name_k,
 cdi.cdi_name_l,

 COALESCE(cd.cd_syn,cdi.cdi_syn_e),
 COALESCE(cd.cd_def,cdi.cdi_def_e),

-- arti.art_data_size,
-- arti.art_xmin,
-- arti.art_xmax,
-- arti.art_ymin,
-- arti.art_ymax,
-- arti.art_zmin,
-- arti.art_zmax,
-- arti.art_volume,

 art.art_data_size,
 art.art_xmin,
 art.art_xmax,
 art.art_ymin,
 art.art_ymax,
 art.art_zmin,
 art.art_zmax,
 art.art_volume,

 arti.art_timestamp,

 arti.art_id,
 arti.art_name,
 arti.art_ext,

-- arti.art_comment,
-- arti.art_category,
-- arti.art_judge,
-- arti.art_class,

 arta.art_comment,
 arta.art_category,
 arta.art_judge,
 arta.art_class,

 cm.cmp_id,
 cm_entry,
 seg_color,

 art.art_serial

order by
 min(distance_voxel),
 art.art_serial desc
SQL
				my $target_voxel_ids_str = join(",",keys(%$target_voxel_ids));
				my $sql = sprintf($sql_fmt,$target_voxel_ids_str,$target_voxel_ids_str);

print $LOG __LINE__,":\$sql=[\n",$sql,"\n]\n";

				my $sth = $dbh->prepare($sql) or die $dbh->errstr;
				$sth->execute() or die $dbh->errstr;
				my $total = $sth->rows();
				$sth->finish;
				undef $sth;

#				$sql .= qq| limit $FORM{'limit'}|;
				$sql .= qq| limit 50|;

#				my $sth_data = $dbh->prepare(qq|select art_data from art_file where art_id=? order by art_serial desc NULLS FIRST limit 1|) or die $dbh->errstr;
#				my $sth_aff = $dbh->prepare(qq|select COALESCE(aff.artf_id,0) as artf_id, COALESCE(af.artf_name,'/') as artf_name from art_folder_file as aff left join (select * from art_folder) as af on aff.artf_id=af.artf_id where artff_delcause is null and artf_delcause is null and art_id=? order by aff.artff_timestamp desc NULLS FIRST limit 1|) or die $dbh->errstr;


				my $cdi_id;
				my $cdi_name;
				my $cdi_name_e;
				my $cdi_name_j;
				my $cdi_name_k;
				my $cdi_name_l;

				my $cdi_syn_e;
				my $cdi_def_e;

				my $rep_id;
				my $use_rep_id;

				my $art_data_size;
				my $art_xmin;
				my $art_xmax;
				my $art_ymin;
				my $art_ymax;
				my $art_zmin;
				my $art_zmax;
				my $art_volume;
				my $art_timestamp;

				my $art_id;
				my $art_name;
				my $art_ext;
				my $art_mirroring;

				my $artg_id;
				my $artg_name;

				my $art_comment;
				my $art_category;
				my $art_judge;
				my $art_class;

				my $art_hist_serial;
				my $art_thumb;

				my $cmp_id;
				my $cm_entry;
				my $seg_color;

				my $md_abbr;
				my $mv_name_e;
				my $bul_abbr;

				my $art_serial;

				my $distance_voxel;

				my @DATAS;

				my $sth = $dbh->prepare($sql) or die $dbh->errstr;
				my $col_idx=0;
				$sth->execute() or die $dbh->errstr;

				$sth->bind_col(++$col_idx, \$cdi_id, undef);
				$sth->bind_col(++$col_idx, \$cdi_name, undef);
				$sth->bind_col(++$col_idx, \$cdi_name_e, undef);
				$sth->bind_col(++$col_idx, \$cdi_name_j, undef);
				$sth->bind_col(++$col_idx, \$cdi_name_k, undef);
				$sth->bind_col(++$col_idx, \$cdi_name_l, undef);

				$sth->bind_col(++$col_idx, \$cdi_syn_e, undef);
				$sth->bind_col(++$col_idx, \$cdi_def_e, undef);

				$sth->bind_col(++$col_idx, \$art_data_size, undef);
				$sth->bind_col(++$col_idx, \$art_xmin, undef);
				$sth->bind_col(++$col_idx, \$art_xmax, undef);
				$sth->bind_col(++$col_idx, \$art_ymin, undef);
				$sth->bind_col(++$col_idx, \$art_ymax, undef);
				$sth->bind_col(++$col_idx, \$art_zmin, undef);
				$sth->bind_col(++$col_idx, \$art_zmax, undef);
				$sth->bind_col(++$col_idx, \$art_volume, undef);
				$sth->bind_col(++$col_idx, \$art_timestamp, undef);

				$sth->bind_col(++$col_idx, \$art_id, undef);
				$sth->bind_col(++$col_idx, \$art_name, undef);
				$sth->bind_col(++$col_idx, \$art_ext, undef);

				$sth->bind_col(++$col_idx, \$art_comment, undef);
				$sth->bind_col(++$col_idx, \$art_category, undef);
				$sth->bind_col(++$col_idx, \$art_judge, undef);
				$sth->bind_col(++$col_idx, \$art_class, undef);

				$sth->bind_col(++$col_idx, \$cmp_id, undef);
				$sth->bind_col(++$col_idx, \$cm_entry, undef);
				$sth->bind_col(++$col_idx, \$seg_color, undef);

				$sth->bind_col(++$col_idx, \$art_serial, undef);

				$sth->bind_col(++$col_idx, \$distance_voxel, undef);
				while($sth->fetch){

					my $file_name;
					my $grouppath;
					my $path;

#					my $group_path = &catdir($FindBin::Bin,'art_file',$artg_name);
					my $group_path = &catdir($FindBin::Bin,'art_file');
					my $grouppath = &abs2rel($group_path,$FindBin::Bin);
					unless(-e $group_path){
						umask(0);
						&File::Path::mkpath($group_path,{mode=>0777});
					}
					my $file_name = $art_name;
					$file_name .= $art_ext unless($art_name =~ /$art_ext$/);
					my $file_path = &catfile($group_path,qq|$art_id$art_ext|);
=pod
					unless(-e $file_path && -s $file_path == $art_data_size && (stat($file_path))[9]==$art_timestamp){
						my $art_data;
						$sth_data->execute($art_id) or die $dbh->errstr;
						$sth_data->bind_col(1, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
						$sth_data->fetch;
						$sth_data->finish;
#						undef $sth_data;

						if(defined $art_data && open(my $OBJ,"> $file_path")){
							flock($OBJ,2);
							binmode($OBJ,':utf8');
							print $OBJ $art_data;
							close($OBJ);
							utime $art_timestamp,$art_timestamp,$file_path;
						}
						undef $art_data;
					}
=cut
					my $path = &File::Basename::basename($file_path);


					my $art_xcenter = (defined $art_xmin && defined $art_xmax) ? ($art_xmin+$art_xmax)/2 : undef;
					my $art_ycenter = (defined $art_ymin && defined $art_ymax) ? ($art_ymin+$art_ymax)/2 : undef;
					my $art_zcenter = (defined $art_zmin && defined $art_zmax) ? ($art_zmin+$art_zmax)/2 : undef;

					my $artf_id;
					my $artf_name;
#					$sth_aff->execute($art_id) or die $dbh->errstr;
#					$sth_aff->bind_col(1, \$artf_id, undef);
#					$sth_aff->bind_col(2, \$artf_name, undef);
#					$sth_aff->fetch;
#					$sth_aff->finish;

					my $img_prefix;
					my $img_path;
					my $img_info;
					my $thumbnail_path;
					#($img_prefix,$img_path) = &getObjImagePrefix($art_id,$md_id,$mv_id);
					#$img_info = &getImageFileList($img_prefix);
					#$thumbnail_path = sprintf($img_info->{'gif_fmt'},$img_prefix,$img_info->{'sizeStrXS'});
					unless(defined $thumbnail_path && -e $thumbnail_path && -f $thumbnail_path && -s $thumbnail_path){
						($img_prefix,$img_path) = &getObjImagePrefix($art_id);
						$img_info = &getImageFileList($img_prefix);
						$thumbnail_path = sprintf($img_info->{'gif_fmt'},$img_prefix,$img_info->{'sizeStrXS'});
					}
					if(-e $thumbnail_path && -f $thumbnail_path && -s $thumbnail_path){
						$thumbnail_path = sprintf(qq|<img align=center width=16 height=16 src="%s?%s">|,&abs2rel($thumbnail_path,$FindBin::Bin),(stat($thumbnail_path))[9]);
					}else{
						$thumbnail_path = undef;
					}

					my $hash = {};

					$hash->{&BITS::Config::CONCEPT_INFO_DATA_FIELD_ID()} = $ci_id - 0;
					$hash->{&BITS::Config::CONCEPT_BUILD_DATA_FIELD_ID()} = $cb_id - 0;
					$hash->{&BITS::Config::MODEL_DATA_FIELD_ID()} = $md_id - 0;
					$hash->{&BITS::Config::MODEL_VERSION_DATA_FIELD_ID()} = $mv_id - 0;
					$hash->{&BITS::Config::MODEL_REVISION_DATA_FIELD_ID()} = $mr_id - 0;

					$hash->{&BITS::Config::OBJ_ID_DATA_FIELD_ID()} = $art_id;
					$hash->{&BITS::Config::OBJ_NAME_FIELD_ID()} = $art_name;
					$hash->{&BITS::Config::OBJ_EXT_FIELD_ID()} = $art_name;
					$hash->{&BITS::Config::OBJ_TIMESTAMP_DATA_FIELD_ID()} = $art_timestamp - 0;
					$hash->{&BITS::Config::OBJ_DATA_SIZE_FIELD_ID()} = $art_data_size - 0;

					$hash->{&BITS::Config::OBJ_X_MIN_FIELD_ID()} = $art_xmin - 0;
					$hash->{&BITS::Config::OBJ_X_MAX_FIELD_ID()} = $art_xmax - 0;
					$hash->{&BITS::Config::OBJ_Y_MIN_FIELD_ID()} = $art_ymin - 0;
					$hash->{&BITS::Config::OBJ_Y_MAX_FIELD_ID()} = $art_ymax - 0;
					$hash->{&BITS::Config::OBJ_Z_MIN_FIELD_ID()} = $art_zmin - 0;
					$hash->{&BITS::Config::OBJ_Z_MAX_FIELD_ID()} = $art_zmax - 0;

					$hash->{&BITS::Config::OBJ_X_CENTER_FIELD_ID()} = $art_xcenter - 0;
					$hash->{&BITS::Config::OBJ_Y_CENTER_FIELD_ID()} = $art_ycenter - 0;
					$hash->{&BITS::Config::OBJ_Z_CENTER_FIELD_ID()} = $art_zcenter - 0;

					$hash->{&BITS::Config::OBJ_VOLUME_FIELD_ID()} = $art_volume - 0;

					$hash->{&BITS::Config::OBJ_COMMENT_FIELD_ID()} = $art_comment;
					$hash->{&BITS::Config::OBJ_CATEGORY_FIELD_ID()} = $art_category;
					$hash->{&BITS::Config::OBJ_JUDGE_FIELD_ID()} = $art_judge;
					$hash->{&BITS::Config::OBJ_CLASS_FIELD_ID()} = $art_class;


					$hash->{&BITS::Config::CONCEPT_DATA_INFO_ID_FIELD_ID()} = defined $cdi_id ? $cdi_id - 0 : undef;
					$hash->{&BITS::Config::CONCEPT_DATA_INFO_NAME_FIELD_ID()} = $cdi_name;
					$hash->{&BITS::Config::CONCEPT_DATA_INFO_NAME_E_FIELD_ID()} = $cdi_name_e;

					$hash->{&BITS::Config::SYNONYM_DATA_FIELD_ID()} = $cdi_syn_e;
					$hash->{&BITS::Config::DEFINITION_DATA_FIELD_ID()} = $cdi_def_e;

					$hash->{&BITS::Config::CONCEPT_OBJ_MAP_PART_ID_FIELD_ID()} = defined $cmp_id ? $cmp_id - 0 : undef;
					$hash->{&BITS::Config::CONCEPT_OBJ_MAP_ENTRY_FIELD_ID()} = defined $cm_entry ? $cm_entry - 0 : undef;

					$hash->{&BITS::Config::CONCEPT_DATA_COLOR_DATA_FIELD_ID()} = $seg_color;
					$hash->{&BITS::Config::SEGMENT_COLOR_FIELD_ID()} = $seg_color;

					$hash->{&BITS::Config::OBJ_FILENAME_FIELD_ID()} = qq|$art_name$art_ext|;
					$hash->{&BITS::Config::OBJ_URL_DATA_FIELD_ID()} = &abs2rel($file_path,$FindBin::Bin);

					$hash->{&BITS::Config::OBJ_THUMBNAIL_PATH_FIELD_ID()} = $thumbnail_path;

					$hash->{&BITS::Config::DISTANCE_FIELD_ID()} = $distance_voxel - 0;

					$hash->{&BITS::Config::TARGET_RECORD_FIELD_ID()} = (exists $FORM{&BITS::Config::OBJ_ID_DATA_FIELD_ID()} && defined $FORM{&BITS::Config::OBJ_ID_DATA_FIELD_ID()} && $FORM{&BITS::Config::OBJ_ID_DATA_FIELD_ID()} eq $art_id) ? JSON::XS::true : JSON::XS::false;


#					$hash->{&BITS::Config::DISTANCE_FIELD_ID()} = $min_distance_hash->{$art_id} if(defined $min_distance_hash && ref $min_distance_hash eq 'HASH' && exists $min_distance_hash->{$art_id} && defined $min_distance_hash->{$art_id});

					$hash->{&BITS::Config::EXISTS_PALETTE_FIELD_ID()} = JSON::XS::false;


#					push(@{$DATAS->{'datas'}},$hash);
					push(@DATAS, $hash);
				}
				$sth->finish;
				undef $sth;

				@DATAS = sort {$a->{&BITS::Config::DISTANCE_FIELD_ID()} <=> $b->{&BITS::Config::DISTANCE_FIELD_ID()}} @DATAS;
				if(exists $FORM{'limit'} && defined $FORM{'limit'} && scalar @DATAS > $FORM{'limit'}){
					$#DATAS = $FORM{'limit'}-1;
				}
				push(@{$DATAS->{'datas'}},@DATAS);


			}
		}
		$DATAS->{'total'} = scalar @{$DATAS->{'datas'}};
		$DATAS->{'success'} = JSON::XS::true;
	};
	if($@){
		$DATAS->{'msg'} = $@;
		my $msg = $DATAS->{'msg'};
		&utf8::encode($msg) if(&utf8::is_utf8($msg));
		print $LOG __LINE__,":",$msg,"\n";
	}
}
&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);
#my $json = &JSON::XS::encode_json($DATAS);
#print $json;
&gzip_json($DATAS);
#print $LOG $json,"\n";
print $LOG __LINE__,":",Dumper($DATAS),"\n";
&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

close($LOG);
=pod
if($FORM{'cmd'} eq 'read'){
	my $prog_basename = qq|batch-load-obj|;
	my $prog = &catfile($FindBin::Bin,'..','batch',qq|$prog_basename.pl|);
	if(-e $prog && -x $prog){
		my($epocsec,$microsec) = &Time::HiRes::gettimeofday();
		my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);
		my $mfmt = sprintf("%04d%02d%02d%02d%02d%02d.%05d.%05d",$year+1900,$mon+1,$mday,$hour,$min,$sec,$microsec,$$);
		my $params_file = &catdir($FindBin::Bin,'temp',"$prog_basename-$mfmt.json");
		&cgi_lib::common::writeFileJSON($params_file,$DATAS);

		my $pid = fork;
		if(defined $pid){
			if($pid == 0){
				my $logdir = &getLogDir();
				my $f1 = &catfile($logdir,qq|$prog_basename.$mfmt.log|);
				my $f2 = &catfile($logdir,qq|$prog_basename.$mfmt.err|);
				close(STDOUT);
				close(STDERR);
				open STDOUT, "> $f1" || die "[$f1] $!\n";
				open STDERR, "> $f2" || die "[$f2] $!\n";
				close(STDIN);
				exec(qq|nice -n 19 $prog $params_file|);
				exit(1);
			}else{
#				$RTN->{'success'} = JSON::XS::true;
			}
		}else{
			die("Can't execute program");
		}
	}
}
=cut
