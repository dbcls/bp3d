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

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;

use BITS::Config;
require "webgl_common.pl";

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
$log_file .= '.'.sprintf("%04d%02d%02d%02d",$year+1900,$mon+1,$mday,$hour);

open(LOG,">> $log_file");
select(LOG);
$| = 1;
select(STDOUT);

my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
print LOG "\n[$logtime]:$0\n";

foreach my $key (sort keys(%FORM)){
	print LOG __LINE__,qq|:\$FORM{$key}=[$FORM{$key}]\n|;
}
foreach my $key (sort keys(%ENV)){
	print LOG __LINE__,qq|:\$ENV{$key}=[$ENV{$key}]\n|;
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

unless(defined $ENV{REQUEST_METHOD}){
#DEBUG
	$FORM{'art_point'} = qq|{"x":45.72223031506283,"y":-104.2487002747223,"z":1517.728255572939}|;
	$FORM{'model'} = qq|bp3d|;
	$FORM{'version'} = qq|4.1|;
	$FORM{'ag_data'} = qq|obj/bp3d/4.1|;
	$FORM{'tree'} = qq|isa|;
	$FORM{'md_id'} = 1;
	$FORM{'mv_id'} = 4;
	$FORM{'mr_id'} = 1;
	$FORM{'ci_id'} = 1;
	$FORM{'cb_id'} = 4;
	$FORM{'bul_id'} = 3;
	$FORM{'art_id'} = qq|FJ1746|;
#	$FORM{'conditions'} = qq|{"parts_map":true,"version":{"md_id":1,"mv_id":4,"mr_id":1},"tree":{"ci_id":1,"cb_id":4,"bul_id":3}}|;
	$FORM{'start'} = 0;
	$FORM{'limit'} = 10;
#DEBUG
}

if($FORM{'cmd'} eq 'read'){
	eval{
		my $md_id;
		my $mv_id;
		my $mr_id;
		my $ci_id;
		my $cb_id;
		my $bul_id;
		$bul_id=$FORM{'bul_id'};

		my $target_art_point_x;
		my $target_art_point_y;
		my $target_art_point_z;
		my $voxel_range = $FORM{'voxel_range'} || 10;
#		my $voxel_range = 50;
		my $parts_map;

		my $conditions;
		eval{$conditions = &JSON::XS::decode_json($FORM{'conditions'}) if(defined $FORM{'conditions'});};
		if(defined $conditions && $conditions->{'parts_map'} eq JSON::XS::true){
			$parts_map = 1;
			$md_id=$FORM{'md_id'};
			$mv_id=$FORM{'mv_id'};
			$mr_id=$FORM{'mr_id'};
			$ci_id=$FORM{'ci_id'};
			$cb_id=$FORM{'cb_id'};
		}

		my $where_rep = '';
		{
			my @w;
			push(@w,qq|md_id=$FORM{'md_id'}|) if(defined $FORM{'md_id'});
			push(@w,qq|mv_id=$FORM{'mv_id'}|) if(defined $FORM{'mv_id'});
			push(@w,qq|mr_id<=$FORM{'mr_id'}|) if(defined $FORM{'mr_id'});
			push(@w,qq|ci_id=$FORM{'ci_id'}|) if(defined $FORM{'ci_id'});
			push(@w,qq|cb_id=$FORM{'cb_id'}|) if(defined $FORM{'cb_id'});
			push(@w,qq|bul_id=$FORM{'bul_id'}|) if(defined $FORM{'bul_id'});
			$where_rep = qq| and | . join(" AND ",@w);
			undef @w;
		}
		my $where_map = '';
		{
			my @w;
			push(@w,qq|md_id=$FORM{'md_id'}|) if(defined $FORM{'md_id'});
			push(@w,qq|mv_id=$FORM{'mv_id'}|) if(defined $FORM{'mv_id'});
			push(@w,qq|mr_id<=$FORM{'mr_id'}|) if(defined $FORM{'mr_id'});
			push(@w,qq|ci_id=$FORM{'ci_id'}|) if(defined $FORM{'ci_id'});
			push(@w,qq|cb_id=$FORM{'cb_id'}|) if(defined $FORM{'cb_id'});
			$where_map = qq| AND | . join(" AND ",@w);
			undef @w;
		}

		my $art_point;
		eval{$art_point = &JSON::XS::decode_json($FORM{'art_point'}) if(defined $FORM{'art_point'});};

		if(defined $art_point){
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
					$where_all = qq| AND map.cdi_id is not null|;
				}
				my $sql_fmt =<<SQL;
select
 cdi.cdi_name,
 cdi.cdi_name_e,
 cdi.cdi_name_j,
 cdi.cdi_name_k,
 cdi.cdi_name_l,
 rep.rep_id,
 repa.rep_id,

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
 arti.art_mirroring,

 arti.artg_id,
 arti.artg_name,

 arta.art_comment,
 arta.art_category,
 arta.art_judge,
 arta.art_class,

 hart.art_hist_serial,
 hart.art_thumb,

 map.cm_use,
 map.cmp_id,

 md.md_abbr,
 mv.mv_name_e,
 bul.bul_abbr,

 art.art_serial,

 min(distance_voxel) as distance_voxel
from (
 select
  arti.*,
  artg_name
 from
  art_file_info as arti
 left join (
  select artg_id,artg_name from art_group where atrg_use and artg_delcause is null
 ) as artg on
    artg.artg_id=arti.artg_id
 where
  artg_name is not null
) as arti

left join (
 select * from art_file
) as art on
   art.art_id=arti.art_id

left join (
 select * from art_annotation
) as arta on
   arta.art_id=arti.art_id


--イメージへのパスを生成する為
LEFT JOIN (
   SELECT
     art_id,
     max(hist_serial) as art_hist_serial,
    'art_images/'||idp.prefix_char||'/'||substring(to_char(art_serial,'FM9999990000') from 1 for 2)||'/'||substring(to_char(art_serial,'FM9999990000') from 3 for 2)||'/'||art_id||'-'||max(hist_serial) as art_thumb
   FROM
     history_art_file as hart
   LEFT JOIN (
      select prefix_char::text,prefix_id from id_prefix
   ) idp on
       idp.prefix_id=hart.prefix_id
   GROUP BY
     art_id,
     art_serial,
     idp.prefix_char
) as hart ON 
   hart.art_id=arti.art_id

left join (
 select * from concept_art_map
 where
  cm_delcause is null $where_map
) as map on
   map.art_id=arti.art_id

left join (
  select
   art_id,
   art_hist_serial,
   min(abs(sqrt(power(((art_xmin+art_xmax)/2) - $target_art_point_x,2)+power(((art_ymin+art_ymax)/2) - $target_art_point_y,2)+power(((art_zmin+art_zmax)/2) - $target_art_point_z,2)))) as distance_voxel
  from
   voxel_data
  where
   voxel_id in (%s)
  group by
   art_id
   ,art_hist_serial

 ) as vd on
    arti.art_id=vd.art_id AND 
    hart.art_hist_serial=vd.art_hist_serial

left join (
   select * from representation where rep_delcause is null $where_rep
 ) as rep on
    map.md_id=rep.md_id AND 
    map.mv_id=rep.mv_id AND
    map.mr_id=rep.mr_id AND
    map.ci_id=rep.ci_id AND
    map.cb_id=rep.cb_id AND
    map.cdi_id=rep.cdi_id

left join (
   select * from representation_art
 ) as repa on
    repa.rep_id=rep.rep_id AND 
    repa.art_id=arti.art_id AND 
    repa.art_hist_serial=hart.art_hist_serial

left join (
   select * from concept_data_info where cdi_delcause is null
 ) as cdi on
    map.ci_id=cdi.ci_id AND
    map.cdi_id=cdi.cdi_id

left join (
   select * from model
 ) as md on
    md.md_id=rep.md_id

left join (
   select * from model_version
 ) as mv on
    mv.md_id=rep.md_id and
    mv.mv_id=rep.mv_id

left join (
   select * from buildup_logic
 ) as bul on
    bul.bul_id=rep.bul_id

where
 (arti.art_id,hart.art_hist_serial) in (
   select distinct art_id,art_hist_serial from voxel_data where voxel_id in (%s)
 )
 $where_all
group by
 cdi.cdi_name,
 cdi.cdi_name_e,
 cdi.cdi_name_j,
 cdi.cdi_name_k,
 cdi.cdi_name_l,
 rep.rep_id,
 repa.rep_id,
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
 arti.art_mirroring,

 arti.artg_id,
 arti.artg_name,

 arta.art_comment,
 arta.art_category,
 arta.art_judge,
 arta.art_class,

 hart.art_hist_serial,
 hart.art_thumb,

 map.cm_use,
 map.cmp_id,

 md.md_abbr,
 mv.mv_name_e,
 bul.bul_abbr,

 art.art_serial

order by
 min(distance_voxel),
 art.art_serial desc
SQL
				my $target_voxel_ids_str = join(",",keys(%$target_voxel_ids));
				my $sql = sprintf($sql_fmt,$target_voxel_ids_str,$target_voxel_ids_str);

print LOG __LINE__,":\$sql=[\n",$sql,"\n]\n";

				my $sth = $dbh->prepare($sql) or die $dbh->errstr;
				$sth->execute() or die $dbh->errstr;
				my $total = $sth->rows();
				$sth->finish;
				undef $sth;

				$sql .= qq| limit 50|;

				my $sth_data = $dbh->prepare(qq|select art_data from history_art_file where art_id=? AND hist_serial=?|) or die $dbh->errstr;
				my $sth_repa = $dbh->prepare(qq|select rep_id from representation_art where rep_id=? AND art_id=?|) or die $dbh->errstr;

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

				my $cm_use;
				my $cmp_id;

				my $md_abbr;
				my $mv_name_e;
				my $bul_abbr;

				my $art_serial;

				my $distance_voxel;
				my $sth = $dbh->prepare($sql) or die $dbh->errstr;
				my $col_idx=0;
				$sth->execute() or die $dbh->errstr;
				$sth->bind_col(++$col_idx, \$cdi_name, undef);
				$sth->bind_col(++$col_idx, \$cdi_name_e, undef);
				$sth->bind_col(++$col_idx, \$cdi_name_j, undef);
				$sth->bind_col(++$col_idx, \$cdi_name_k, undef);
				$sth->bind_col(++$col_idx, \$cdi_name_l, undef);

				$sth->bind_col(++$col_idx, \$rep_id, undef);
				$sth->bind_col(++$col_idx, \$use_rep_id, undef);

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
				$sth->bind_col(++$col_idx, \$art_mirroring, undef);

				$sth->bind_col(++$col_idx, \$artg_id, undef);
				$sth->bind_col(++$col_idx, \$artg_name, undef);

				$sth->bind_col(++$col_idx, \$art_comment, undef);
				$sth->bind_col(++$col_idx, \$art_category, undef);
				$sth->bind_col(++$col_idx, \$art_judge, undef);
				$sth->bind_col(++$col_idx, \$art_class, undef);

				$sth->bind_col(++$col_idx, \$art_hist_serial, undef);
				$sth->bind_col(++$col_idx, \$art_thumb, undef);

				$sth->bind_col(++$col_idx, \$cm_use, undef);
				$sth->bind_col(++$col_idx, \$cmp_id, undef);

				$sth->bind_col(++$col_idx, \$md_abbr, undef);
				$sth->bind_col(++$col_idx, \$mv_name_e, undef);
				$sth->bind_col(++$col_idx, \$bul_abbr, undef);

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
					my $file_path = File::Spec->catfile($group_path,qq|$art_id-$art_hist_serial$art_ext|);

					unless(-e $file_path && -s $file_path == $art_data_size && (stat($file_path))[9]==$art_timestamp){
						my $art_data;
						$sth_data->execute($art_id,$art_hist_serial) or die $dbh->errstr;
						$sth_data->bind_col(1, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
						$sth_data->fetch;
						$sth_data->finish;
#						undef $sth_data;

						if(defined $art_data && open(OBJ,"> $file_path")){
							flock(OBJ,2);
							binmode(OBJ);
							print OBJ $art_data;
							close(OBJ);
							utime $art_timestamp,$art_timestamp,$file_path;
						}
						undef $art_data;
					}
					my $path = &File::Basename::basename($file_path);


					my $art_xcenter = (defined $art_xmin && defined $art_xmax) ? ($art_xmin+$art_xmax)/2 : undef;
					my $art_ycenter = (defined $art_ymin && defined $art_ymax) ? ($art_ymin+$art_ymax)/2 : undef;
					my $art_zcenter = (defined $art_zmin && defined $art_zmax) ? ($art_zmin+$art_zmax)/2 : undef;

					if(defined $rep_id){
						$sth_repa->execute($rep_id,$art_id) or die $dbh->errstr;
						undef $rep_id unless($sth_repa->rows());
						$sth_repa->finish;
					}

					push(@{$DATAS->{'datas'}},{

						#Old I/O
						name  => $file_name,
						group => $artg_name,
						grouppath => $grouppath,
						path  => $path,
						mtime => $art_timestamp + 0,

						xmin   => $art_xmin + 0,
						xmax   => $art_xmax + 0,
						ymin   => $art_ymin + 0,
						ymax   => $art_ymax + 0,
						zmin   => $art_zmin + 0,
						zmax   => $art_zmax + 0,
						volume => $art_volume + 0,

						xcenter => $art_xcenter,
						ycenter => $art_ycenter,
						zcenter => $art_zcenter,

						#New I/O
						art_id          => $art_id,
						art_hist_serial => $art_hist_serial + 0,
						art_thumb       => $art_thumb,
						art_name        => $art_name,
						art_timestamp   => $art_timestamp + 0,

						art_xmin       => $art_xmin + 0,
						art_xmax       => $art_xmax + 0,
						art_ymin       => $art_ymin + 0,
						art_ymax       => $art_ymax + 0,
						art_zmin       => $art_zmin + 0,
						art_zmax       => $art_zmax + 0,

						art_xcenter    => $art_xcenter,
						art_ycenter    => $art_ycenter,
						art_zcenter    => $art_zcenter,

						art_volume     => $art_volume + 0,
						art_comment    => $art_comment,
						art_mirroring  => $art_mirroring ? JSON::XS::true : JSON::XS::false,
						art_category   => $art_category,
						art_judge      => $art_judge,
						art_class      => $art_class,

						artg_id        => $artg_id + 0,
						artg_name      => $artg_name,

						cdi_name       => $cdi_name,
						cdi_name_e     => $cdi_name_e,

						rep_id         => $rep_id,
#						rep_id         => $use_rep_id,
						use_rep_id     => $use_rep_id,

						md_id          => $md_id + 0,
						md_abbr        => $md_abbr,
						mv_id          => $mv_id + 0,
						mv_name_e      => $mv_name_e,

						mr_id          => $mr_id + 0,
						bul_id         => $bul_id + 0,
						bul_abbr       => $bul_abbr,

						cm_use         => $cm_use ? JSON::XS::true : JSON::XS::false,
						cmp_id         => $cmp_id + 0,

						filename       => $file_name,

						distance_voxel => $distance_voxel,

					});
				}
				$sth->finish;
				undef $sth;

			}
		}
		$DATAS->{'total'} = scalar @{$DATAS->{'datas'}};
		$DATAS->{'success'} = JSON::XS::true;
	};
	if($@){
		$DATAS->{'msg'} = $@;
		my $msg = $DATAS->{'msg'};
		&utf8::encode($msg) if(&utf8::is_utf8($msg));
		print LOG __LINE__,":",$msg,"\n";
	}
}
#my $json = &JSON::XS::encode_json($DATAS);
#print $json;
&gzip_json($DATAS);
#print LOG $json,"\n";
print LOG __LINE__,":",Dumper($DATAS),"\n";

close(LOG);

exit;
