#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use JSON::XS;
use File::Basename;
use Cwd qw(abs_path);
use File::Spec;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use Data::Dumper;
use DBD::Pg;
use POSIX;
use Time::HiRes;
use Time::Piece;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;

use BITS::Config;
use BITS::ConceptArtMapModified;

require "webgl_common.pl";
use cgi_lib::common;

my $query = CGI->new;
my $dbh = &get_dbh();

my $t0 = [&Time::HiRes::gettimeofday()];

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
$log_file .= '.'.sprintf("%04d%02d%02d%02d",$year+1900,$mon+1,$mday,$hour);

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
#$FORM{'limit'} = 25 unless(defined $FORM{'limit'});

#$FORM{'name'} = qq|120406_liver_divided01_obj|;

#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $DATAS = {
	'datas'   => [],
	'total'   => 0,
	'msg'     => undef,
	'success' => JSON::XS::false
};

my $ci_id=$FORM{'ci_id'};
my $cb_id=$FORM{'cb_id'};
my $md_id=$FORM{'md_id'};
my $mv_id=$FORM{'mv_id'};

$md_id=1 unless(defined $md_id && $md_id =~ /^[1-9][0-9]*$/);
unless(defined $mv_id && $mv_id =~ /^[1-9][0-9]*$/){
	$mv_id = undef;
	$ci_id = undef;
	$cb_id = undef;
	my $sth_mv;
	if(defined $FORM{'mv_id'} && $FORM{'mv_id'} =~ /^\-[1-9][0-9]*$/){
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
	&cgi_lib::common::message('$ci_id='.$ci_id, $LOG);
	&cgi_lib::common::message('$cb_id='.$cb_id, $LOG);
}
$FORM{'ci_id'}=$ci_id;
$FORM{'cb_id'}=$cb_id;
$FORM{'md_id'}=$md_id;
$FORM{'mv_id'}=$mv_id;

if($FORM{'cmd'} eq 'read'){
	eval{
		my $target_art_point_x;
		my $target_art_point_y;
		my $target_art_point_z;
		my $voxel_range = $FORM{'voxel_range'} || 10;
#		my $voxel_range = 50;
		my $parts_map;

		my $conditions;
		$conditions = &cgi_lib::common::decodeJSON($FORM{'conditions'}) if(exists $FORM{'conditions'} && defined $FORM{'conditions'});
		if(defined $conditions && ref $conditions eq 'HASH' && $conditions->{'parts_map'} eq JSON::XS::true){
			$parts_map = 1;
			$ci_id = $FORM{'ci_id'} if(exists $FORM{'ci_id'} && defined $FORM{'ci_id'});
		}

		my $where_map = '';
		{
			my @w;
			push(@w,qq|ci_id=$FORM{'ci_id'}|) if(exists $FORM{'ci_id'} && defined $FORM{'ci_id'});
			$where_map = qq| AND | . join(" AND ",@w);
			undef @w;
		}

		my $art_point;
		$art_point = &cgi_lib::common::decodeJSON($FORM{'art_point'}) if(exists $FORM{'art_point'} && defined $FORM{'art_point'});

		if(defined $art_point && ref $art_point eq 'HASH'){
			$target_art_point_x = $art_point->{'x'};
			$target_art_point_y = $art_point->{'y'};
			$target_art_point_z = $art_point->{'z'};
		}
		if(defined $target_art_point_x && defined $target_art_point_y && defined $target_art_point_z){
			my $sql = qq|select distinct voxel_id from voxel_data where voxel_id in (select voxel_id from voxel_index where voxel_x>=? AND voxel_x<=? AND voxel_y>=? AND voxel_y<=? AND voxel_z>=? AND voxel_z<=?)|;
			my $sth = $dbh->prepare($sql) or die $dbh->errstr;
			my $p = $voxel_range/2;
			my @bind_values = ();
			push(@bind_values,floor($target_art_point_x-$p));
			push(@bind_values,ceil($target_art_point_x+$p));
			push(@bind_values,floor($target_art_point_y-$p));
			push(@bind_values,ceil($target_art_point_y+$p));
			push(@bind_values,floor($target_art_point_z-$p));
			push(@bind_values,ceil($target_art_point_z+$p));

			$sth->execute(@bind_values) or die $dbh->errstr;
			my $target_voxel_ids;
			my $voxel_id;
			my $column_number = 0;
			$sth->bind_col(++$column_number, \$voxel_id, undef);
			while($sth->fetch){
				$target_voxel_ids->{$voxel_id} = undef if(defined $voxel_id);
			}
			$sth->finish;
			undef $sth;

			if(defined $target_voxel_ids){
				my $where_all = '';
				if(defined $parts_map){
					$where_all = qq| AND cm.cdi_id is not null|;
				}
				my $sql_fmt =<<SQL;
select
 cdi.cdi_id,
 cdi.cdi_name,
 cdi.cdi_name_e,
 cdi.cdi_name_j,
 cdi.cdi_name_k,
 cdi.cdi_name_l,

 arti.art_data_size,
 arti.art_xmin,
 arti.art_xmax,
 arti.art_ymin,
 arti.art_ymax,
 arti.art_zmin,
 arti.art_zmax,
 arti.art_volume,

 EXTRACT(EPOCH FROM arti.art_timestamp) as art_timestamp,

 arti.art_id,
 arti.art_name,
 arti.art_ext,

 arti.art_comment,
 arti.art_category,
 arti.art_judge,
 arti.art_class,

 cm.cmp_id,
 EXTRACT(EPOCH FROM cm.cm_entry) as cm_entry,

 seg_color,

 art.art_serial,

 min(distance_voxel) as distance_voxel
from
 art_file_info as arti

left join (
 select art_id,art_serial from art_file
) as art on
   art.art_id=arti.art_id

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
  SELECT cdi_id, seg_id FROM concept_data WHERE ci_id=$ci_id AND cb_id=$cb_id
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
 cdi.cdi_name_e,
 cdi.cdi_name_j,
 cdi.cdi_name_k,
 cdi.cdi_name_l,
 arti.art_data_size,
 arti.art_xmin,
 arti.art_xmax,
 arti.art_ymin,
 arti.art_ymax,
 arti.art_zmin,
 arti.art_zmax,
 arti.art_volume,
 arti.art_timestamp,

 arti.art_id,
 arti.art_name,
 arti.art_ext,

 arti.art_comment,
 arti.art_category,
 arti.art_judge,
 arti.art_class,

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

				$sql .= qq| limit 50|;

#				my $sth_data = $dbh->prepare(qq|select art_data from art_file where art_id=? order by art_serial desc NULLS FIRST limit 1|) or die $dbh->errstr;
				my $sth_aff = $dbh->prepare(qq|select COALESCE(aff.artf_id,0) as artf_id, COALESCE(af.artf_name,'/') as artf_name from art_folder_file as aff left join (select * from art_folder) as af on aff.artf_id=af.artf_id where artff_delcause is null and artf_delcause is null and art_id=? order by aff.artff_timestamp desc NULLS FIRST limit 1|) or die $dbh->errstr;


				my $cdi_id;
				my $cdi_name;
				my $cdi_name_e;
				my $cdi_name_j;
				my $cdi_name_k;
				my $cdi_name_l;

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

				my $use_cdi_ids;

				my $sth = $dbh->prepare($sql) or die $dbh->errstr;
				my $col_idx=0;
				$sth->execute() or die $dbh->errstr;

				$sth->bind_col(++$col_idx, \$cdi_id, undef);
				$sth->bind_col(++$col_idx, \$cdi_name, undef);
				$sth->bind_col(++$col_idx, \$cdi_name_e, undef);
				$sth->bind_col(++$col_idx, \$cdi_name_j, undef);
				$sth->bind_col(++$col_idx, \$cdi_name_k, undef);
				$sth->bind_col(++$col_idx, \$cdi_name_l, undef);

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

#					my $group_path = File::Spec->catdir($FindBin::Bin,'art_file',$artg_name);
					my $group_path = File::Spec->catdir($FindBin::Bin,'art_file');
					my $grouppath = File::Spec->abs2rel($group_path,$FindBin::Bin);
					unless(-e $group_path){
						umask(0);
						&File::Path::mkpath($group_path,{mode=>0777});
					}
					my $file_name = $art_name;
					$file_name .= $art_ext unless($art_name =~ /$art_ext$/);
					my $file_path = File::Spec->catfile($group_path,qq|$art_id$art_ext|);
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
					$sth_aff->execute($art_id) or die $dbh->errstr;
					$sth_aff->bind_col(1, \$artf_id, undef);
					$sth_aff->bind_col(2, \$artf_name, undef);
					$sth_aff->fetch;
					$sth_aff->finish;

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

					push(@{$DATAS->{'datas'}},{

						art_id          => $art_id,
						art_name        => $art_name,
						art_ext         => $art_ext,
						art_timestamp   => $art_timestamp - 0,
						art_data_size   => $art_data_size - 0,

						art_xmin       => $art_xmin - 0,
						art_xmax       => $art_xmax - 0,
						art_ymin       => $art_ymin - 0,
						art_ymax       => $art_ymax - 0,
						art_zmin       => $art_zmin - 0,
						art_zmax       => $art_zmax - 0,

						art_xcenter    => $art_xcenter,
						art_ycenter    => $art_ycenter,
						art_zcenter    => $art_zcenter,

						art_volume     => $art_volume - 0,
						art_comment    => $art_comment,
						art_category   => $art_category,
						art_judge      => $art_judge,
						art_class      => $art_class,

						cdi_id         => defined $cdi_id ? $cdi_id - 0 : undef,
						cdi_name       => $cdi_name,
						cdi_name_e     => $cdi_name_e,

						cmp_id         => defined $cmp_id ? $cmp_id - 0 : undef,
						cm_entry       => defined $cm_entry ? $cm_entry - 0 : undef,
						seg_color      => $seg_color,

						art_filename   => qq|$art_name$art_ext|,
						art_path       => &abs2rel($file_path,$FindBin::Bin),

						artf_id => $artf_id,
						artf_name => $artf_name,

						art_tmb_path   => $thumbnail_path,

						distance_voxel => $distance_voxel - 0,

						current_use   => JSON::XS::false,
						current_use_reason => undef

					});

					$use_cdi_ids->{$cdi_id} = undef if(defined $cdi_id);
				}
				$sth->finish;
				undef $sth;

#=pod
#&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);
				if(defined $use_cdi_ids && ref $use_cdi_ids eq 'HASH' && scalar keys(%$use_cdi_ids)){
					my($ELEMENT, $COMP_DENSITY_USE_TERMS, $COMP_DENSITY_END_TERMS, $COMP_DENSITY, $CDI_MAP, $CDI_MAP_ART_DATE, $CDI_ID2CID, $CDI_MAP_SUM_VOLUME_DEL_ID,$CDI_DESC_OBJ_OLD_DEL_ID) = &BITS::ConceptArtMapModified::calcElementAndDensity(
						dbh     => $dbh,
						md_id   => $md_id,
						mv_id   => $mv_id,
						ci_id   => $ci_id,
						cb_id   => $cb_id,
						crl_id  => undef,
						cdi_ids => [keys %$use_cdi_ids],
						concept_art_map_name => undef,
						art_file_info_name => undef,
						LOG => $LOG
					);

#&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

#					if(defined $LOG){
#						&cgi_lib::common::message($ELEMENT, $LOG);
#						&cgi_lib::common::message($COMP_DENSITY_USE_TERMS, $LOG);
#						&cgi_lib::common::message($COMP_DENSITY_END_TERMS, $LOG);
#						&cgi_lib::common::message($COMP_DENSITY, $LOG);
#						&cgi_lib::common::message($CDI_MAP, $LOG);
#						&cgi_lib::common::message($CDI_MAP_ART_DATE, $LOG);
#						&cgi_lib::common::message($CDI_ID2CID, $LOG);
#						&cgi_lib::common::message($CDI_MAP_SUM_VOLUME_DEL_ID, $LOG);
#					}

					if(defined $CDI_MAP_ART_DATE && ref $CDI_MAP_ART_DATE eq 'HASH'){
						my $sth_cdi_sel = $dbh->prepare(qq|select cdi_name from concept_data_info where ci_id=$ci_id AND cdi_id=?|) or die $dbh->errstr;
						my %CDI2NAME;
						foreach my $data (@{$DATAS->{'datas'}}){
							next unless(exists $data->{'cdi_id'} && defined $data->{'cdi_id'} && exists $data->{'art_id'} && defined $data->{'art_id'});
							$cdi_id = $data->{'cdi_id'};
							$art_id = $data->{'art_id'};

							my $current_use;
							my $current_use_reason;
							if(exists $CDI_MAP_ART_DATE->{$cdi_id} && defined $CDI_MAP_ART_DATE->{$cdi_id} && ref $CDI_MAP_ART_DATE->{$cdi_id} eq 'HASH' && exists $CDI_MAP_ART_DATE->{$cdi_id}->{$art_id}){
								$current_use = JSON::XS::true;	#子供のOBJより古くない場合
								$current_use_reason = undef;
							}
							elsif(
								defined $cdi_id &&
								defined $art_id &&
								defined $CDI_DESC_OBJ_OLD_DEL_ID &&
								ref     $CDI_DESC_OBJ_OLD_DEL_ID eq 'HASH' &&
								exists  $CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id} &&
								defined $CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id} &&
								ref     $CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id} eq 'HASH' &&
								exists  $CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id}->{$art_id} &&
								defined $CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id}->{$art_id} &&
								ref     $CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id}->{$art_id} eq 'HASH' &&
								exists  $CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id}->{$art_id}->{'max_cdi_id'} &&
								defined $CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id}->{$art_id}->{'max_cdi_id'}
							){
								$current_use = JSON::XS::false;

								my $max_cdi_id = $CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id}->{$art_id}->{'max_cdi_id'};
								my $max_art_timestamp = localtime($CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id}->{$art_id}->{'max_art_timestamp'});

								if($CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id}->{$art_id}->{'max_cdi_id'} eq $CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id}->{$art_id}->{'del_cdi_id'}){
									$current_use_reason = sprintf('Older than other OBJ [%s]', $max_art_timestamp->strftime('%Y/%m/%d %H:%M:%S'));
								}
								else{
									my $max_cdi_name;
									unless(exists $CDI2NAME{$max_cdi_id} && defined $CDI2NAME{$max_cdi_id}){
										$sth_cdi_sel->execute($max_cdi_id) or die $dbh->errstr;
										$column_number = 0;
										$sth_cdi_sel->bind_col(++$column_number, \$max_cdi_name, undef);
										$sth_cdi_sel->fetch;
										$sth_cdi_sel->finish;
										$CDI2NAME{$max_cdi_id} = $max_cdi_name;
									}
									else{
										$max_cdi_name = $CDI2NAME{$max_cdi_id};
									}
									$current_use_reason = sprintf('It is older than descendant OBJ [%s][%s]', $max_cdi_name, $max_art_timestamp->strftime('%Y/%m/%d %H:%M:%S'));
								}
							}
							else{
								$current_use = JSON::XS::false;
								if(defined $cdi_id){
									$current_use_reason = 'Older than the other OBJ or descendants of OBJ';
								}
								else{
									$current_use_reason = undef;
								}
							}

							$data->{'current_use'} = $current_use;
							$data->{'current_use_reason'} = $current_use_reason;
						}
					}
				}
#&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);
#=cut
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
#my $json = &JSON::XS::encode_json($DATAS);
#print $json;
&gzip_json($DATAS);
#print $LOG $json,"\n";
print $LOG __LINE__,":",Dumper($DATAS),"\n";

close($LOG);

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
