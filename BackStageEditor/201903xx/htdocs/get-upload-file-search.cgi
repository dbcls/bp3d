#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use JSON::XS;
use File::Basename;
use Cwd qw(abs_path);
use File::Spec;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
#use CGI::Carp::DebugScreen ( debug => 1 );
use Data::Dumper;
use DBD::Pg;
use POSIX;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;

use BITS::Config;
use BITS::VTK;
use BITS::Voxel;

use obj2deci;
require "webgl_common.pl";

my $query = CGI->new;
my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);

my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);

my $log_file = qq|$FindBin::Bin/logs/$cgi_name.txt|;
$log_file .= qq|.$FORM{'cmd'}| if(exists $FORM{'cmd'});

open(LOG,"> $log_file");
select(LOG);
$| = 1;
select(STDOUT);

foreach my $key (sort keys(%FORM)){
	print LOG __LINE__,qq|:\$FORM{$key}=[$FORM{$key}]\n|;
}

$FORM{'cmd'} = 'read' unless(defined $FORM{'cmd'});
#$FORM{'start'} = 0 unless(defined $FORM{'start'});
#$FORM{'limit'} = 25 unless(defined $FORM{'limit'});

#$FORM{'name'} = qq|120406_liver_divided01_obj|;

#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $DATAS = {
	'datas' => [],
	'total' => 0,
	'success' => JSON::XS::false
};

=pod
eval{
	die "error!!";
	$DATAS->{'success'} = JSON::XS::true;
};
if($@){
	$DATAS->{'msg'} = $@;
}
my $json = &JSON::XS::encode_json($DATAS);
print $json;
close(LOG);
exit;
=cut


=pod
http://192.168.1.237/WebGL/130710/api-upload-file-list.cgi?cmd=search&md_id=1&mv_id=3&mr_id=2&ci_id=1&cb_id=4&bul_id=3&limit=10&art_id=FJ3660
=cut

=pod
$FORM{'art_point'} = qq|{"x":41.81039175449132,"y":-147.36891142464657,"z":805.2097610111996}|;
$FORM{'model'} = qq|bp3d|;
$FORM{'version'} = qq|4.0|;
$FORM{'ag_data'} = qq|obj/bp3d/4.0|;
$FORM{'tree'} = qq|isa|;
$FORM{'md_id'} = qq|1|;
$FORM{'mv_id'} = qq|3|;
$FORM{'mr_id'} = qq|2|;
$FORM{'ci_id'} = qq|1|;
$FORM{'cb_id'} = qq|4|;
$FORM{'bul_id'} = qq|3|;
$FORM{'art_id'} = qq|FJ3484|;
$FORM{'conditions'} = qq|{"parts_map":true,"version":[{"md_id":1,"mv_id":3,"mr_id":2}]}|;
$FORM{'start'} = qq|0|;
$FORM{'limit'} = qq|10|;
=cut



#if($FORM{'cmd'} eq 'read' && exists $FORM{'art_id'} && defined $FORM{'art_id'}){
if($FORM{'cmd'} eq 'read'){
	my $where_search;
	my $column_search;
	my $checked_collision;
	my $target_path;
	my $target_art_id;
	my $target_art_hist_serial;
	my $target_md5;
	my $target_volume;
	my $target_artg_name;
	my $target_artg_path;
	my $target_voxel_ids;
	my $target_voxel_ids_str = '0';

	my $target_art_point;
	my $target_art_point_x=0;
	my $target_art_point_y=0;
	my $target_art_point_z=0;

	if(exists $FORM{'art_id'} && defined $FORM{'art_id'}){

		my $art_id=$FORM{'art_id'};
		delete $FORM{'art_id'};
		my $sql=<<SQL;
select
 art.art_id,
 art_hist_serial,
 art_ext,
 art_md5,
 art_xmin,
 art_xmax,
 art_ymin,
 art_ymax,
 art_zmin,
 art_zmax,
 to_number(to_char((art_xmax+art_xmin)/2,'FM99990D0000'),'99990D0000S') as art_xcenter,
 to_number(to_char((art_ymax+art_ymin)/2,'FM99990D0000'),'99990D0000S') as art_ycenter,
 to_number(to_char((art_zmax+art_zmin)/2,'FM99990D0000'),'99990D0000S') as art_zcenter,
 art_volume,
 art_cube_volume,
 GREATEST(abs(art_xmax-art_xmin)/2,abs(art_ymax-art_ymin)/2,abs(art_zmax-art_zmin)/2) as art_radius,
 sqrt(power(art_xmax-art_xmin,2)+power(art_ymax-art_ymin,2)+power(art_zmax-art_zmin,2)) as art_distance,
 artg_name
from
-- history_art_file as art
 art_file as art

left join (
   select art_id,max(hist_serial) as art_hist_serial from history_art_file group by art_id
 ) as hart on
    hart.art_id=art.art_id

left join (
   select * from art_group
 ) as artg on
    artg.artg_id=art.artg_id

where
 art.art_id=?
-- AND (art.art_id,art.hist_serial) in (
--   select art_id,max(hist_serial) as hist_serial from history_art_file group by art_id
-- )
SQL
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute($art_id) or die $dbh->errstr;

		my $art_id;
		my $art_hist_serial;
		my $art_ext;
		my $art_md5;
		my $art_xmin;
		my $art_xmax;
		my $art_ymin;
		my $art_ymax;
		my $art_zmin;
		my $art_zmax;
		my $art_xcenter;
		my $art_ycenter;
		my $art_zcenter;
		my $art_volume;
		my $art_cube_volume;
		my $art_radius;
		my $art_distance;
		my $artg_name;
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$art_id, undef);
		$sth->bind_col(++$column_number, \$art_hist_serial, undef);
		$sth->bind_col(++$column_number, \$art_ext, undef);
		$sth->bind_col(++$column_number, \$art_md5, undef);
		$sth->bind_col(++$column_number, \$art_xmin, undef);
		$sth->bind_col(++$column_number, \$art_xmax, undef);
		$sth->bind_col(++$column_number, \$art_ymin, undef);
		$sth->bind_col(++$column_number, \$art_ymax, undef);
		$sth->bind_col(++$column_number, \$art_zmin, undef);
		$sth->bind_col(++$column_number, \$art_zmax, undef);
		$sth->bind_col(++$column_number, \$art_xcenter, undef);
		$sth->bind_col(++$column_number, \$art_ycenter, undef);
		$sth->bind_col(++$column_number, \$art_zcenter, undef);
		$sth->bind_col(++$column_number, \$art_volume, undef);
		$sth->bind_col(++$column_number, \$art_cube_volume, undef);
		$sth->bind_col(++$column_number, \$art_radius, undef);
		$sth->bind_col(++$column_number, \$art_distance, undef);
		$sth->bind_col(++$column_number, \$artg_name, undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;

		if(defined $art_xcenter && defined $art_ycenter && defined $art_zcenter && defined $art_volume && defined $art_cube_volume){

#			my $group_path = File::Spec->catdir($FindBin::Bin,'art_file',$artg_name);
			my $group_path = File::Spec->catdir($FindBin::Bin,'art_file');
			my $file_path = File::Spec->catfile($group_path,qq|$art_id-$art_hist_serial$art_ext|);
			$target_path = $file_path unless(defined $target_path);

			$target_artg_name = $artg_name unless(defined $target_artg_name);
			$target_artg_path = File::Spec->abs2rel(&File::Basename::dirname($file_path),$FindBin::Bin) unless(defined $target_artg_path);
			$target_art_id = $art_id unless(defined $target_art_id);
			$target_art_hist_serial = $art_hist_serial unless(defined $target_art_hist_serial);
			$target_md5 = $art_md5 unless(defined $target_md5);
			$target_volume = $art_volume unless(defined $target_volume);

			my $checked_volume;
			my $value_volume;
			my $checked_distance;
			my $value_distance;

			my $conditions;
			eval{$conditions = &JSON::XS::decode_json($FORM{'conditions'}) if(defined $FORM{'conditions'});};
			if(defined $conditions){
				$checked_volume = $conditions->{'checked_volume'} if($conditions->{'checked_volume'} eq JSON::XS::true);
				$checked_distance = $conditions->{'checked_distance'} if($conditions->{'checked_distance'} eq JSON::XS::true);
				$checked_collision = $conditions->{'checked_collision'} if($conditions->{'checked_collision'} eq JSON::XS::true);
				$value_volume = $conditions->{'value_volume'} if(defined $checked_volume && defined $conditions->{'value_volume'});
				$value_distance = $conditions->{'value_distance'} if(defined $checked_distance && defined $conditions->{'value_distance'});
			}

			my @W;
			if(defined $value_volume || defined $value_distance || defined $checked_collision){
				if(defined $value_volume){
					push(@W,qq|abs(art_volume - $art_volume) < $value_volume|);#同じような体積のもの
					push(@W,qq|abs(art_cube_volume - $art_cube_volume) < $value_volume|);#同じような体積のもの
#					push(@W,qq|abs(sqrt(power(art_xmax-art_xmin,2)+power(art_ymax-art_ymin,2)+power(art_zmax-art_zmin,2)) - $art_distance)<1|);#直径での判定
				}
				if(defined $value_distance){
					push(@W,qq|abs(sqrt(power(art_xcenter - $art_xcenter,2)+power(art_ycenter - $art_ycenter,2)+power(art_zcenter - $art_zcenter,2))) < $value_distance|);
				}
				if(defined $checked_collision){

					unless(defined $target_voxel_ids){
						my @bind_values = ();
						my $sql = qq|select voxel_id from voxel_data where art_id=? AND art_hist_serial=?|;
						push(@bind_values,$art_id,$art_hist_serial);

#						$sql .= qq| union select voxel_id from voxel_index where voxel_x<=ceil(?) AND voxel_x>=floor(?) AND voxel_y<=ceil(?) AND voxel_y>=floor(?) AND voxel_z<=ceil(?) AND voxel_z>=floor(?)|;
#						push(@bind_values,$art_xmax,$art_xmin,$art_ymax,$art_ymin,$art_zmax,$art_zmin);

						if(scalar @bind_values > 0){
							my $sth = $dbh->prepare($sql) or die $dbh->errstr;
							$sth->execute(@bind_values) or die $dbh->errstr;
							my $voxel_id;
							my $column_number = 0;
							$sth->bind_col(++$column_number, \$voxel_id, undef);
							while($sth->fetch){
								push(@$target_voxel_ids,$voxel_id) if(defined $voxel_id);
							}
							$sth->finish;
							undef $sth;
						}
					}

					if(defined $target_voxel_ids){
						$target_voxel_ids_str = join(",",@$target_voxel_ids);
						my $w = qq|(art_id,art_hist_serial) in (select distinct art_id,0 from voxel_data where voxel_id in ($target_voxel_ids_str) union select art_id,0 from art_file where art_xmax<=ceil($art_xmax) AND art_xmin>=floor($art_xmin) AND art_ymax<=ceil($art_ymax) AND art_ymin>=floor($art_ymin) AND art_zmax<=ceil($art_zmax) AND art_zmin>=floor($art_zmin))|;
						push(@W,$w);
					}else{

						my $w = qq|(art_id,art_hist_serial) in (select art_id,0 from art_file where art_xmax<=ceil($art_xmax) AND art_xmin>=floor($art_xmin) AND art_ymax<=ceil($art_ymax) AND art_ymin>=floor($art_ymin) AND art_zmax<=ceil($art_zmax) AND art_zmin>=floor($art_zmin))|;
						push(@W,$w);

					}

				}
			}
			$where_search = qq|where | . join(' AND ',@W) if(scalar @W > 0);
print LOG __LINE__,qq|:\$where_search=[$where_search]\n|;



#			$column_search  = qq|,(abs(art_volume - $art_volume)+abs(art_cube_volume - $art_cube_volume)) as diff_volume|;
			$column_search  = qq|,abs(art_volume - $art_volume) as diff_volume|;
			$column_search .= qq|,abs(art_cube_volume - $art_cube_volume) as diff_cube_volume|;
			$column_search .= qq|,abs(sqrt(power(art_xcenter - $art_xcenter,2)+power(art_ycenter - $art_ycenter,2)+power(art_zcenter - $art_zcenter,2))) as distance_xyz|;

			my $SORT;
			eval{$SORT = &JSON::XS::decode_json($FORM{'sort'});} if(exists $FORM{'sort'} && defined $FORM{'sort'});
			$SORT = [] unless(defined $SORT);

			unshift(@$SORT,{
				direction => 'ASC',
				property => qq|distance_xyz|
			});


			if(defined $value_volume){
				unshift(@$SORT,{
					direction => 'ASC',
#					property => qq|abs(art_volume - $art_volume)+abs(art_cube_volume - $art_cube_volume)|
					property => qq|abs(art_volume - $art_volume)|
				});
			}

			$FORM{'sort'} = &JSON::XS::encode_json($SORT);

#		$FORM{'cmd'} = 'read';
		}
	}

	my $selected_art_ids;
	if(exists $FORM{'selected_art_ids'} && defined $FORM{'selected_art_ids'}){
		eval{$selected_art_ids = &JSON::XS::decode_json($FORM{'selected_art_ids'});};
	};

#if($FORM{'cmd'} eq 'read'){
	my $md_id=$FORM{'md_id'};
	my $mv_id=$FORM{'mv_id'};
	my $mr_id=$FORM{'mr_id'};
	my $ci_id=$FORM{'ci_id'};
	my $cb_id=$FORM{'cb_id'};
	my $bul_id=$FORM{'bul_id'};

	my $where_artg_id;

	if(exists $FORM{'artg_ids'} && defined $FORM{'artg_ids'}){
		my $artg_ids;
		eval{$artg_ids = &JSON::XS::decode_json($FORM{'artg_ids'});};
		if(defined $artg_ids && ref $artg_ids eq 'ARRAY' && scalar @$artg_ids > 0){
			my $artg_id = join(",",@$artg_ids);
#			$where_artg_id = qq|where art.artg_id in ($artg_id)|;
			$where_artg_id = qq|where artg_id in ($artg_id)|;
		}
	}

	$where_artg_id = '' if(defined $where_search && !defined $where_artg_id);

	if(defined $where_artg_id){
		my $sql=<<SQL;
select *  $column_search from (
select
 arti.art_id,
 hart2.art_hist_serial,
 'art_images/'||idp.prefix_char||'/'||substring(hart.art_serial_char from 1 for 2)||'/'||substring(hart.art_serial_char from 3 for 2)||'/'||art.art_id||'-'||hart2.art_hist_serial as art_thumb,
 arti.art_name,
 arti.art_ext,
 EXTRACT(EPOCH FROM arti.art_timestamp) as art_timestamp,
 art_md5,
-- art_data,
 art_data_size,
 art_xmin,
 art_xmax,
 art_ymin,
 art_ymax,
 art_zmin,
 art_zmax,
 to_number(to_char((art_xmax+art_xmin)/2,'FM99990D0000'),'99990D0000S') as art_xcenter,
 to_number(to_char((art_ymax+art_ymin)/2,'FM99990D0000'),'99990D0000S') as art_ycenter,
 to_number(to_char((art_zmax+art_zmin)/2,'FM99990D0000'),'99990D0000S') as art_zcenter,
 art_volume,
 art_cube_volume,
 arta.art_comment,
 arti.art_mirroring,
 arta.art_category,
 arta.art_judge,
 arta.art_class,
 arti.artg_id,
 artg_name,

 arto.arto_id,
 arto.arto_comment,
 arto.arto_name,
 arto.arto_ext,
 arto.artog_id,
 arto.artog_name,

 cdi_name,
 cdi_name_e,
 rep.rep_id,
 repa.rep_id,
 rep.md_id,
 md.md_abbr,
 rep.mv_id,
 mv.mv_name_e,
 rep.mr_id,
 rep.bul_id,
 bul.bul_abbr,
 map.cm_use,
 distance_voxel
from
 (select * from history_art_file_info where (art_id,artg_id,hist_serial) in (select art_id,artg_id,max(hist_serial) from history_art_file_info $where_artg_id group by art_id,artg_id)) as arti

--art_org_infoの関連情報
left join (
   select 
     arto.art_id,
     arto_id,
     arto_comment,
     arti.art_name as arto_name,
     arti.art_ext as arto_ext,
     artg.artg_id as artog_id,
     artg.artg_name as artog_name
   from
     art_org_info as arto
   left join (
     select * from art_file_info
   ) as arti on arti.art_id=arto.arto_id
   left join (
     select * from art_group
   ) as artg on artg.artg_id=arti.artg_id
 ) as arto on
    arto.art_id=arti.art_id

--art_fileの関連情報
left join (
   select * from art_file
 ) as art on
    art.art_id=arti.art_id

--history_art_fileから最新のhist_serialを取得
left join (
   select art_id,max(hist_serial) as art_hist_serial from history_art_file group by art_id
 ) as hart2 on
    hart2.art_id=art.art_id


--art_fileのアノテーション情報
left join (
   select * from art_annotation
 ) as arta on
    arta.art_id=art.art_id

--イメージへのパスを生成する為
LEFT JOIN (
    SELECT art_id,hist_serial,to_char(art_serial,'FM9999990000') as art_serial_char FROM history_art_file
  ) as hart ON 
     hart.art_id=hart2.art_id AND
     hart.hist_serial=hart2.art_hist_serial
LEFT JOIN (
    select prefix_char::text,prefix_id from id_prefix
  ) idp on idp.prefix_id=art.prefix_id

--グループ情報
left join (
   select * from art_group
 ) as artg on
    artg.artg_id=arti.artg_id

left join (
   select
    *
   from
    concept_art_map
   where
--    cm_use and -- バージョンに関係なく対応付けしたFMAIDを表示させる場合は、cm_useは参照しない
    cm_delcause is null
    and ci_id=$ci_id and cb_id=$cb_id and md_id=$md_id and mv_id=$mv_id
 ) as hmap on
    hmap.art_id=art.art_id

left join (
   select * from concept_data_info
 ) as cdi on
    cdi.ci_id=hmap.ci_id and
    cdi.cdi_id=hmap.cdi_id

-- 最新の状態を参照する為、concept_art_mapを参照する
left join (
   select
    *
   from
    concept_art_map
   where
--    cm_use and
    cm_delcause is null
    and ci_id=$ci_id and cb_id=$cb_id and md_id=$md_id and mv_id=$mv_id
 ) as map on
    map.art_id=art.art_id

left join (
   select
    *
   from
    representation
   where
    (ci_id,cb_id,md_id,mv_id,mr_id,bul_id,cdi_id) in (
     select
      ci_id,cb_id,md_id,mv_id,max(mr_id) as mr_id,bul_id,cdi_id
     from
      representation
     where
      ci_id=$ci_id and cb_id=$cb_id and md_id=$md_id and mv_id=$mv_id and bul_id=$bul_id
     group by
      ci_id,cb_id,md_id,mv_id,bul_id,cdi_id
   )
 ) as rep on
    rep.ci_id=map.ci_id and
    rep.cb_id=map.cb_id and
    rep.md_id=map.md_id and
    rep.mv_id=map.mv_id and
    rep.cdi_id=map.cdi_id

--実際に使用されているかを確認
left join (
   select
    *
   from
    representation_art
 ) as repa on
    repa.rep_id          = rep.rep_id and
    repa.art_id          = art.art_id and
    repa.art_hist_serial = hart2.art_hist_serial

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

left join (
  select
   art_id,
   art_hist_serial,
   min(abs(sqrt(power(((art_xmin+art_xmax)/2) - $target_art_point_x,2)+power(((art_ymin+art_ymax)/2) - $target_art_point_y,2)+power(((art_zmin+art_zmax)/2) - $target_art_point_z,2)))) as distance_voxel
  from
   voxel_data
  where
   voxel_id in ($target_voxel_ids_str)
  group by
   art_id
   ,art_hist_serial

 ) as vd on
    art.art_id=vd.art_id
    AND hart2.art_hist_serial=vd.art_hist_serial

--$where_artg_id

) as a
$where_search
SQL

		print LOG __LINE__,qq|:\$sql=[$sql]\n|;

		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$DATAS->{'total'} = $sth->rows();
		$sth->finish;
		undef $sth;

		if($DATAS->{'total'}>0){

			if(exists $FORM{'sort'} && defined $FORM{'sort'}){
				my $SORT;
				eval{$SORT = &JSON::XS::decode_json($FORM{'sort'});};
				if(defined $SORT){
					my @S = ();
					foreach my $s (@$SORT){
						next if($s->{'property'} eq 'selected');
						push(@S,qq|$s->{property} $s->{direction}|);
					}
					$sql .= qq| ORDER BY |.join(",",@S);
				}
			}

			if(exists $FORM{'limit'} && defined $FORM{'limit'} && $FORM{'limit'} =~ /^[0-9]+$/){
				$sql .= qq| LIMIT $FORM{'limit'}|;
			}
			if(exists $FORM{'start'} && defined $FORM{'start'} && $FORM{'start'} =~ /^[0-9]+$/){
				$sql .= qq| OFFSET $FORM{'start'}|;
			}

			print LOG __LINE__,qq|:\$sql=[$sql]\n|;

			$sth = $dbh->prepare($sql) or die $dbh->errstr;
			$sth->execute() or die $dbh->errstr;


			my $column_number = 0;
			my $art_id;
			my $art_hist_serial;
			my $art_thumb;
			my $art_name;
			my $art_ext;
			my $art_timestamp;
			my $art_md5;

			my $art_data;
			my $art_data_size;

			my $art_xmin;
			my $art_xmax;
			my $art_ymin;
			my $art_ymax;
			my $art_zmin;
			my $art_zmax;

			my $art_xcenter;
			my $art_ycenter;
			my $art_zcenter;

			my $art_volume;
			my $art_cube_volume;
			my $art_comment;
			my $art_mirroring;
			my $art_category;
			my $art_judge;
			my $art_class;
			my $artg_id;
			my $artg_name;

			my $arto_id;
			my $arto_comment;
			my $arto_name;
			my $arto_ext;
			my $artog_id;
			my $artog_name;

			my $cdi_name;
			my $cdi_name_e;
			my $rep_id;
			my $use_rep_id;

			my $md_id;
			my $md_abbr;
			my $mv_id;
			my $mv_name_e;
			my $mr_id;
			my $bul_id;
			my $bul_abbr;

			my $cm_use;

			my $distance_voxel;

			my $diff_volume;
			my $diff_cube_volume;
			my $distance_xyz;

			$sth->bind_col(++$column_number, \$art_id, undef);
			$sth->bind_col(++$column_number, \$art_hist_serial, undef);
			$sth->bind_col(++$column_number, \$art_thumb, undef);
			$sth->bind_col(++$column_number, \$art_name, undef);
			$sth->bind_col(++$column_number, \$art_ext, undef);
			$sth->bind_col(++$column_number, \$art_timestamp, undef);
			$sth->bind_col(++$column_number, \$art_md5, undef);

#			$sth->bind_col(++$column_number, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
			$sth->bind_col(++$column_number, \$art_data_size, undef);

			$sth->bind_col(++$column_number, \$art_xmin, undef);
			$sth->bind_col(++$column_number, \$art_xmax, undef);
			$sth->bind_col(++$column_number, \$art_ymin, undef);
			$sth->bind_col(++$column_number, \$art_ymax, undef);
			$sth->bind_col(++$column_number, \$art_zmin, undef);
			$sth->bind_col(++$column_number, \$art_zmax, undef);

			$sth->bind_col(++$column_number, \$art_xcenter, undef);
			$sth->bind_col(++$column_number, \$art_ycenter, undef);
			$sth->bind_col(++$column_number, \$art_zcenter, undef);

			$sth->bind_col(++$column_number, \$art_volume, undef);
			$sth->bind_col(++$column_number, \$art_cube_volume, undef);
			$sth->bind_col(++$column_number, \$art_comment, undef);
			$sth->bind_col(++$column_number, \$art_mirroring, undef);
			$sth->bind_col(++$column_number, \$art_category, undef);
			$sth->bind_col(++$column_number, \$art_judge, undef);
			$sth->bind_col(++$column_number, \$art_class, undef);

			$sth->bind_col(++$column_number, \$artg_id, undef);
			$sth->bind_col(++$column_number, \$artg_name, undef);

			$sth->bind_col(++$column_number, \$arto_id, undef);
			$sth->bind_col(++$column_number, \$arto_comment, undef);
			$sth->bind_col(++$column_number, \$arto_name, undef);
			$sth->bind_col(++$column_number, \$arto_ext, undef);
			$sth->bind_col(++$column_number, \$artog_id, undef);
			$sth->bind_col(++$column_number, \$artog_name, undef);

			$sth->bind_col(++$column_number, \$cdi_name, undef);
			$sth->bind_col(++$column_number, \$cdi_name_e, undef);
			$sth->bind_col(++$column_number, \$rep_id, undef);
			$sth->bind_col(++$column_number, \$use_rep_id, undef);

			$sth->bind_col(++$column_number, \$md_id, undef);
			$sth->bind_col(++$column_number, \$md_abbr, undef);
			$sth->bind_col(++$column_number, \$mv_id, undef);
			$sth->bind_col(++$column_number, \$mv_name_e, undef);

			$sth->bind_col(++$column_number, \$mr_id, undef);
			$sth->bind_col(++$column_number, \$bul_id, undef);
			$sth->bind_col(++$column_number, \$bul_abbr, undef);

			$sth->bind_col(++$column_number, \$cm_use, undef);

			$sth->bind_col(++$column_number, \$distance_voxel, undef);

			if(defined $column_search){
				$sth->bind_col(++$column_number, \$diff_volume, undef);
				$sth->bind_col(++$column_number, \$diff_cube_volume, undef);
				$sth->bind_col(++$column_number, \$distance_xyz, undef);
			}


			while($sth->fetch){
	#					my $path = File::Spec->catdir($BITS::Config::UPLOAD_PATH,$artg_name);
#				my $group_path = File::Spec->catdir($FindBin::Bin,'art_file',$artg_name);
				my $group_path = File::Spec->catdir($FindBin::Bin,'art_file');
				my $grouppath = File::Spec->abs2rel($group_path,$FindBin::Bin);

	#print LOG __LINE__,":\$path=[$path]\n";
	#print LOG __LINE__,":\$path=[$path]\n";
				unless(-e $group_path){
					umask(0);
					&File::Path::mkpath($group_path,{mode=>0777});
				}
				my $file_name = $art_name;
				$file_name .= $art_ext unless($art_name =~ /$art_ext$/);

	#					$path = File::Spec->catfile($path,$file_name);
#				$path = File::Spec->catfile($path,qq|$art_id$art_ext|);
				my $file_path = File::Spec->catfile($group_path,qq|$art_id-$art_hist_serial$art_ext|);

	#print LOG __LINE__,":\$path=[$path]\n";
				unless(-e $file_path && -s $file_path == $art_data_size && (stat($file_path))[9]==$art_timestamp){
					my $art_data;
					my $sth_data = $dbh->prepare(qq|select art_data from history_art_file where art_id=? AND hist_serial=?|) or die $dbh->errstr;
					$sth_data->execute($art_id,$art_hist_serial) or die $dbh->errstr;
					$sth_data->bind_col(1, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
					$sth_data->fetch;
					$sth_data->finish;
					undef $sth_data;

					if(defined $art_data && open(OBJ,"> $file_path")){
						flock(OBJ,2);
						binmode(OBJ);
						print OBJ $art_data;
						close(OBJ);
						utime $art_timestamp,$art_timestamp,$file_path;
					}
					undef $art_data;
				}

#				my $path = File::Spec->abs2rel($file_path,$group_path);
				my $path = &File::Basename::basename($file_path);
#				$path = $file_name;
#				$path = qq|$art_id$art_ext|;
#print LOG __LINE__,":\$path=[$path]\n";


				my $collision_rate;
				my $collision_rate_obj;
				if(defined $checked_collision && defined $column_search && defined $target_path && $target_path ne $file_path){
					#重なり

					if(0 && $target_md5 eq $art_md5){
						$collision_rate = 1;
					}else{
						if(defined $target_voxel_ids){
							my $sth_voxel = $dbh->prepare(qq|select count(voxel_id) from voxel_data where art_id=? AND art_hist_serial=? AND voxel_id in (|.join(",",@$target_voxel_ids).qq|)|) or die $dbh->errstr;
							$sth_voxel->execute($art_id,$art_hist_serial) or die $dbh->errstr;
							my $voxel_count;
							my $column_number = 0;
							$sth_voxel->bind_col(++$column_number, \$voxel_count, undef);
							$sth_voxel->fetch;
							$sth_voxel->finish;
							undef $sth_voxel;
							$collision_rate = $voxel_count / (scalar @$target_voxel_ids) if(defined $voxel_count);
						}

					}
					if(defined $collision_rate){
						$collision_rate_obj = &JSON::XS::encode_json({
							Legend => {
								DrawLegendFlag => JSON::XS::true,
								LegendTitle => qq|Description:|,
								Legend => [{
									text => qq| $target_art_id: red|,
									style => qq|color:red;|
								},{
									text => qq| $art_id: green|,
									style => qq|color:green;|
								}]
							},
							ExtensionPartGroup => [
							{
								PartGroupName  => $target_artg_name,
								PartGroupPath  => $target_artg_path,
								PartGroupItems => [{
									PartName  => $target_art_id,
									PartColor => "FF0000",
									PartPath  => &File::Basename::basename($target_path),
									PartMTime => (stat($target_path))[9] * 1000,
									PartOpacity => 1.0
								}]
							},
							{
								PartGroupName  => $artg_name,
								PartGroupPath  => $grouppath,
								PartGroupItems => [{
									PartName  => $file_name,
									PartColor => "00FF00",
									PartPath  => $path,
									PartMTime => $art_timestamp * 1000,
									PartOpacity => 0.3
								}]
							}
							]
						});
					}

				}else{
					$collision_rate = undef;
				}


				if(defined $rep_id && defined $use_rep_id){
					unless($rep_id eq $use_rep_id){
						$rep_id = undef;
						$use_rep_id = undef;
					}
				}elsif(defined $rep_id){
					$rep_id = undef;
					$use_rep_id = undef;
				}

				my $selected = JSON::XS::false;
				if(defined $selected_art_ids && exists $selected_art_ids->{$artg_id} && defined $selected_art_ids->{$artg_id} && exists  $selected_art_ids->{$artg_id}->{$art_id}){
					$selected = JSON::XS::true;
				}

				push(@{$DATAS->{'datas'}},{

					#Old I/O
					name  => $file_name,
					group => $artg_name,
					grouppath => $grouppath,
					path  => $path,
					mtime => $art_timestamp,

					xmin   => $art_xmin,
					xmax   => $art_xmax,
					ymin   => $art_ymin,
					ymax   => $art_ymax,
					zmin   => $art_zmin,
					zmax   => $art_zmax,
					volume => $art_volume,

					xcenter => $art_xcenter,
					ycenter => $art_ycenter,
					zcenter => $art_zcenter,

					selected => $selected,

					#New I/O
					art_id          => $art_id,
					art_hist_serial => $art_hist_serial,
					art_thumb       => $art_thumb,
					art_name        => $art_name,
					art_timestamp   => $art_timestamp,

					art_xmin       => $art_xmin,
					art_xmax       => $art_xmax,
					art_ymin       => $art_ymin,
					art_ymax       => $art_ymax,
					art_zmin       => $art_zmin,
					art_zmax       => $art_zmax,

					art_xcenter    => $art_xcenter,
					art_ycenter    => $art_ycenter,
					art_zcenter    => $art_zcenter,

					art_volume     => $art_volume,
					art_comment    => $art_comment,
					art_mirroring  => $art_mirroring,
					art_category   => $art_category,
					art_judge      => $art_judge,
					art_class      => $art_class,

					artg_id        => $artg_id,
					artg_name      => $artg_name,

					arto_id        => $arto_id,
					arto_comment   => $arto_comment,
#					arto_name      => $arto_name,
#					arto_ext       => $arto_ext,
					artog_id       => $artog_id,
					artog_name     => $artog_name,
					arto_filename  => defined $arto_name && defined $arto_ext ? qq|$arto_name$arto_ext| : undef,

					cdi_name       => $cdi_name,
					cdi_name_e     => $cdi_name_e,
					rep_id         => $rep_id,
					use_rep_id     => $use_rep_id,

					md_id          => $md_id,
					md_abbr        => $md_abbr,
					mv_id          => $mv_id,
					mv_name_e      => $mv_name_e,

					mr_id          => $mr_id,
					bul_id         => $bul_id,
					bul_abbr       => $bul_abbr,

					cm_use         => $cm_use ? JSON::XS::true : JSON::XS::false,

					filename       => $file_name,

					diff_volume        => $diff_volume,
					diff_cube_volume   => $diff_cube_volume,
					distance_xyz       => $distance_xyz,
					distance_voxel     => $distance_voxel,
					collision_rate     => $collision_rate,
					collision_rate_obj => $collision_rate_obj

				});
			}
			$sth->finish;
			undef $sth;
		}
	}

	$DATAS->{'success'} = JSON::XS::true;


}elsif($FORM{'cmd'} eq 'update'){
}

#my $json = &JSON::XS::encode_json($DATAS);
#print $json;
&gzip_json($DATAS);
#print LOG $json,"\n";
print LOG __LINE__,":",Dumper($DATAS),"\n";

close(LOG);

exit;

sub Truncated {
	my $v = shift;
	return undef unless(defined $v);
	my $rate = 100000;
	return int($v * $rate + 0.5) / $rate;
}

sub readFile {
	my $path = shift;
#	return undef unless(defined $path && -f $path);
	return undef unless(defined $path);
#	print __LINE__,":\$path=[$path]\n";
	my $rtn;
	my $IN;
	if(open($IN,$path)){
		my $old  = $/;
		undef $/;
		$rtn = <$IN>;
		$/ = $old;
		close($IN);
	}
	return $rtn;
}
