package AG::API::PointSearch;

use strict;
use warnings;
use feature ':5.10';

#use AG::API::JSONParser;
use base qw/AG::API::JSONParser/;
use File::Basename;
use JSON::XS;
use POSIX;
#use common;
#use common_db;
use AG::API::Log;
use cgi_lib::common;

use FindBin;
use File::Spec::Functions qw(catdir catfile);

sub parse {
	my $parser = shift;
#	my $json = shift;
	my $func = shift;
	my $json = $parser->{json};

	my $ag_log = new AG::API::Log($json);

	my $content;
	my $ContentType = qq|application/json|;
	my $Status;
	my $Code = '503';
#	my $parser;
#	my @extlist = qw|.cgi|;
	my($name,$dir,$ext) = &File::Basename::fileparse($0,qr/\..*$/);

#	open OUT,">./tmp_image/$name.txt";
	my $OUT = &cgi_lib::common::getLogFH(undef,undef,&AG::API::JSONParser::get_log_file_basename(),&AG::API::JSONParser::get_log_dir_basename($name));

	if(defined $json){
#		$parser = new AgJSONParser($json);
		if(defined $parser){
			print $OUT __LINE__,":[$json]\n";
			print $OUT __LINE__,":[$parser->{'json'}]\n";
		#	$content = $parser->getMethodContent($name);
			$content = $parser->getMethodContent('point');

			my $obj = defined $content ? &cgi_lib::common::decodeJSON($content) : undef;
			my $item = defined $obj && ref $obj eq 'HASH' && exists $obj->{Pin} && defined $obj->{Pin} && ref $obj->{Pin} eq 'ARRAY' ? shift(@{$obj->{Pin}}) : undef;

#			if(defined $content){
			if(defined $item){

				&cgi_lib::common::message('$content='.$content,$OUT);
				eval{
	#				my $dbh = &common_db::get_dbh();
					my $dbh = $parser->{db}->get_dbh();

					my $obj = &cgi_lib::common::decodeJSON($content);
					my $item = shift(@{$obj->{Pin}});

					my $MARKERS;

					my $md_id;
					my $mv_id;
					my $mr_id;
					my $ci_id;
					my $cb_id;
					my $bul_id;
					my $mv_name_e;

		#			my $voxel_range;
					my $voxel_radius;

					my $jsonObj = &cgi_lib::common::decodeJSON($parser->{'json'});
		#			$voxel_range = $jsonObj->{Pick}->{VoxelRange} || 10;
					$voxel_radius = $jsonObj->{Pick}->{VoxelRadius} || 5;

					unless(defined $md_id){
		#				my $sth = $dbh->prepare(qq|select md_id from model where md_use and md_delcause is null and md_abbr=? order by md_order desc limit 1|) or die $dbh->errstr;
						my $sth = $dbh->prepare(qq|select md_id from model where md_delcause is null and md_abbr=? order by md_order desc limit 1|) or die $dbh->errstr;
						$sth->execute($jsonObj->{Common}->{Model}) or die $dbh->errstr;
						$sth->bind_col(1, \$md_id, undef);
						$sth->fetch;
						$sth->finish;
						undef $sth;
					}
					unless(defined $mv_id && defined $mr_id){
		#				my $sth = $dbh->prepare(qq|select mv_id,mr_id from model_revision where mr_use and mr_delcause is null and md_id=? and mr_version=? order by mr_order desc limit 1|) or die $dbh->errstr;
						my $sth = $dbh->prepare(qq|select mv_id,mr_id from model_revision where mr_delcause is null and md_id=? and mr_version=? order by mr_order desc limit 1|) or die $dbh->errstr;
						$sth->execute($md_id,$jsonObj->{Common}->{Version}) or die $dbh->errstr;
						$sth->bind_col(1, \$mv_id, undef);
						$sth->bind_col(2, \$mr_id, undef);
						$sth->fetch;
						$sth->finish;
						undef $sth;

						$sth = $dbh->prepare(qq|select mv_name_e from model_version where mv_delcause is null and md_id=? and mv_id=?|) or die $dbh->errstr;
						$sth->execute($md_id,$mv_id) or die $dbh->errstr;
						$sth->bind_col(1, \$mv_name_e, undef);
						$sth->fetch;
						$sth->finish;
						undef $sth;
					}
					unless(defined $ci_id && defined $cb_id){
						my $sth = $dbh->prepare(qq|select max(ci_id) from view_concept_art_map where cm_use and cm_delcause is null and md_id=? and mv_id=? and mr_id=?|) or die $dbh->errstr;
						$sth->execute($md_id,$mv_id,$mr_id) or die $dbh->errstr;
						$sth->bind_col(1, \$ci_id, undef);
						$sth->fetch;
						$sth->finish;
						undef $sth;

						$sth = $dbh->prepare(qq|select max(cb_id) from view_concept_art_map where cm_use and cm_delcause is null and md_id=? and mv_id=? and mr_id=? and ci_id=?|) or die $dbh->errstr;
						$sth->execute($md_id,$mv_id,$mr_id,$ci_id) or die $dbh->errstr;
						$sth->bind_col(1, \$cb_id, undef);
						$sth->fetch;
						$sth->finish;
						undef $sth;
					}

					unless(defined $bul_id){
		#				my $sth = $dbh->prepare(qq|select bul_id from buildup_logic where bul_use and bul_delcause is null and bul_abbr=? order by bul_order desc limit 1|) or die $dbh->errstr;
						my $sth = $dbh->prepare(qq|select bul_id from buildup_logic where bul_delcause is null and bul_abbr=? order by bul_order desc limit 1|) or die $dbh->errstr;
						$sth->execute($jsonObj->{Common}->{TreeName}) or die $dbh->errstr;
						$sth->bind_col(1, \$bul_id, undef);
						$sth->fetch;
						$sth->finish;
						undef $sth;
					}


					my $DEF_COLOR = {};
					my $color_path = &catfile($FindBin::Bin,'..','data',$jsonObj->{Common}->{Version},'bp3d.color');
					$color_path = &catfile($FindBin::Bin,'..','data','bp3d.color') unless(-e $color_path);
					if(-e $color_path){
						open(IN,"< $color_path");
						while(<IN>){
							s/\s*$//g;
							s/^\s*//g;
							next if(/^#/);
							my($id,$color) = split(/\t/);
							next if($id eq "" || $color eq "");
							next if(exists($DEF_COLOR->{$id}));
							$DEF_COLOR->{$id} = $color;
						}
						close(IN);
					}


					my $target_voxel_ids;
					my $target_art_point_x = $item->{'PinX'};
					my $target_art_point_y = $item->{'PinY'};
					my $target_art_point_z = $item->{'PinZ'};
					my $sql = qq|select distinct voxel_id from voxel_data where voxel_id in (select voxel_id from voxel_index where voxel_x>=? AND voxel_x<=? AND voxel_y>=? AND voxel_y<=? AND voxel_z>=? AND voxel_z<=?)|;
					my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		#			my $p = $voxel_range/2;
					my $p = $voxel_radius;

					my @bind_values = ();
					push(@bind_values,floor($target_art_point_x-$p));
					push(@bind_values,ceil($target_art_point_x+$p));
					push(@bind_values,floor($target_art_point_y-$p));
					push(@bind_values,ceil($target_art_point_y+$p));
					push(@bind_values,floor($target_art_point_z-$p));
					push(@bind_values,ceil($target_art_point_z+$p));

		#print $OUT __LINE__,qq|:\$sql=[$sql]\n|;
		#print $OUT __LINE__,qq|:|,join(",",@bind_values),qq|\n|;

					$sth->execute(@bind_values) or die $dbh->errstr;
					my $voxel_id;
					my $column_number = 0;
					$sth->bind_col(++$column_number, \$voxel_id, undef);
					while($sth->fetch){
						$target_voxel_ids->{$voxel_id} = undef if(defined $voxel_id);
					}
					$sth->finish;
					undef $sth;

					if(defined $target_voxel_ids){
						my $sql_fmt =<<SQL;
select
 map.cdi_name,
 cdi.cdi_name_e,
 cdi.cdi_name_j,
 cdi.cdi_name_k,
 cdi.cdi_name_l,
 rep.rep_id,
 rep.rep_xmin,
 rep.rep_xmax,
 rep.rep_ymin,
 rep.rep_ymax,
 rep.rep_zmin,
 rep.rep_zmax,
 rep.rep_volume,
 EXTRACT(EPOCH FROM rep.rep_entry) as rep_entry,
 cs.seg_color,
 min(distance_voxel) as distance_voxel
from
 view_concept_art_map as map

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
    map.art_id=vd.art_id AND 
    map.art_hist_serial=vd.art_hist_serial

left join (
   select * from representation where rep_delcause is null and bul_id=$bul_id
 ) as rep on
    map.md_id=rep.md_id AND 
    map.mv_id=rep.mv_id AND
    map.mr_id=rep.mr_id AND
    map.ci_id=rep.ci_id AND
    map.cb_id=rep.cb_id AND
    map.cdi_id=rep.cdi_id

left join (
   select * from concept_data_info where cdi_delcause is null
 ) as cdi on
    map.ci_id=cdi.ci_id AND
    map.cdi_id=cdi.cdi_id

left join (select ci_id,cb_id,cdi_id,seg_id from concept_data) as cd on cd.ci_id = map.ci_id AND cd.cb_id = map.cb_id AND cd.cdi_id = map.cdi_id
left join (select seg_id,seg_name,seg_color,seg_thum_bgcolor,seg_thum_bocolor from concept_segment) as cs on cs.seg_id = cd.seg_id

where
 rep.rep_id is not null AND
 map.cm_use AND
 map.cm_delcause is null AND
 map.md_id=$md_id AND
 map.mv_id=$mv_id AND
 map.mr_id<=$mr_id AND
 map.ci_id=$ci_id AND
 map.cb_id=$cb_id AND
 (map.art_id,map.art_hist_serial) in (
   select distinct art_id,art_hist_serial from voxel_data where voxel_id in (%s)
 )
group by
 map.cdi_name,
 cdi.cdi_name_e,
 cdi.cdi_name_j,
 cdi.cdi_name_k,
 cdi.cdi_name_l,
 rep.rep_id,
 rep.rep_xmin,
 rep.rep_xmax,
 rep.rep_ymin,
 rep.rep_ymax,
 rep.rep_zmin,
 rep.rep_zmax,
 rep.rep_volume,
 rep.rep_entry,
 cs.seg_color
order by
 min(distance_voxel)
SQL
						my $target_voxel_ids_str = join(",",keys(%$target_voxel_ids));
						my $sql = sprintf($sql_fmt,$target_voxel_ids_str,$target_voxel_ids_str);

						my $sth = $dbh->prepare($sql) or die $dbh->errstr;
						$sth->execute() or die $dbh->errstr;
						my $total = $sth->rows();
						$sth->finish;
						undef $sth;

						$sql .= qq| limit 50|;


						my $cdi_name;
						my $cdi_name_e;
						my $cdi_name_j;
						my $cdi_name_k;
						my $cdi_name_l;
						my $rep_id;

						my $rep_xmin;
						my $rep_xmax;
						my $rep_ymin;
						my $rep_ymax;
						my $rep_zmin;
						my $rep_zmax;
						my $rep_volume;
						my $rep_entry;
						my $seg_color;

						my $distance_voxel;
						$sth = $dbh->prepare($sql) or die $dbh->errstr;
						my $col_idx=0;
						$sth->execute() or die $dbh->errstr;
						$sth->bind_col(++$col_idx, \$cdi_name, undef);
						$sth->bind_col(++$col_idx, \$cdi_name_e, undef);
						$sth->bind_col(++$col_idx, \$cdi_name_j, undef);
						$sth->bind_col(++$col_idx, \$cdi_name_k, undef);
						$sth->bind_col(++$col_idx, \$cdi_name_l, undef);

						$sth->bind_col(++$col_idx, \$rep_id, undef);

						$sth->bind_col(++$col_idx, \$rep_xmin, undef);
						$sth->bind_col(++$col_idx, \$rep_xmax, undef);
						$sth->bind_col(++$col_idx, \$rep_ymin, undef);
						$sth->bind_col(++$col_idx, \$rep_ymax, undef);
						$sth->bind_col(++$col_idx, \$rep_zmin, undef);
						$sth->bind_col(++$col_idx, \$rep_zmax, undef);
						$sth->bind_col(++$col_idx, \$rep_volume, undef);
						$sth->bind_col(++$col_idx, \$rep_entry, undef);
						$sth->bind_col(++$col_idx, \$seg_color, undef);

						$sth->bind_col(++$col_idx, \$distance_voxel, undef);
						while($sth->fetch){

							next unless(!defined $MARKERS->{$cdi_name} || $MARKERS->{$cdi_name}->{distance} > $distance_voxel);

							$MARKERS->{$cdi_name} = {
								tg_id     => $md_id,
								tgi_id    => $mv_id,
								version   => $mv_name_e,
								common_id => $cdi_name,
								f_id      => $cdi_name,
								name_e    => $cdi_name_e,
								name_j    => $cdi_name_j,
								name_k    => $cdi_name_k,
								name_l    => $cdi_name_l,
								b_id      => $rep_id,
								xmin      => $rep_xmin,
								xmax      => $rep_xmax,
								ymin      => $rep_ymin,
								ymax      => $rep_ymax,
								zmin      => $rep_zmin,
								zmax      => $rep_zmax,
								volume    => $rep_volume,
								entry     => $rep_entry,
								seg_color => $seg_color,
								distance  => $distance_voxel,
								def_color => (exists $DEF_COLOR->{$cdi_name} && defined $DEF_COLOR->{$cdi_name}) ? $DEF_COLOR->{$cdi_name} : undef

							};
						}
						$sth->finish;
						undef $sth;

						if(defined $MARKERS){

							my $PinPartID = $item->{PinPartID};
							$PinPartID = $1 if($PinPartID =~ /^clipPlaneRect_(.+)$/);

							my $cdi_name;
							my $cdi_name_e;
							my $sth = $dbh->prepare(qq|select cdi_name,cdi_name_e from view_concept_art_map where cm_use and cm_delcause is null and md_id=? and mv_id=? and mr_id<=? and ci_id=? and cb_id=? and art_id=? order by mr_id desc,art_hist_serial desc limit 1|) or die $dbh->errstr;
							$sth->execute($md_id,$mv_id,$mr_id,$ci_id,$cb_id,$PinPartID) or die $dbh->errstr;
							$sth->bind_col(1, \$cdi_name, undef);
							$sth->bind_col(2, \$cdi_name_e, undef);
							$sth->fetch;
							$sth->finish;
							undef $sth;

							my $RTN = {
								id        => defined $cdi_name ? $cdi_name : $item->{PinPartID},
								name      => defined $cdi_name_e ? $cdi_name_e : $item->{PinPartName},
								worldPosX => $item->{PinX},
								worldPosY => $item->{PinY},
								worldPosZ => $item->{PinZ},
								arrVecX   => $item->{PinArrowVectorX},
								arrVecY   => $item->{PinArrowVectorY},
								arrVecZ   => $item->{PinArrowVectorZ},
								upVecX    => $item->{PinUpVectorX},
								upVecY    => $item->{PinUpVectorY},
								upVecZ    => $item->{PinUpVectorZ},
								coordId   => $item->{PinCoordinateSystemName},
								total     => $total,
								ids       => []
							};
							@{$RTN->{ids}} = map {
		#						{
		#							'id'     => $_,
		#							distance => $MARKERS->{$_}->{distance},
		#							rep_id   => $MARKERS->{$_}->{rep_id},
		#							f_id   => $MARKERS->{$_}->{cdi_name},
		#							name_e     => $MARKERS->{$_}->{name_e}
		#						}
								$MARKERS->{$_}
							} sort {
								$MARKERS->{$a}->{distance} <=> $MARKERS->{$b}->{distance}
							} keys(%$MARKERS);
							$content = &cgi_lib::common::encodeJSON($RTN);
						}
					}

					unless(defined $MARKERS){
						my $PinPartID = $item->{PinPartID};
						$PinPartID = $1 if($PinPartID =~ /^clipPlaneRect_(.+)$/);

						my $cdi_name;
						my $cdi_name_e;
						my $sth = $dbh->prepare(qq|select cdi_name,cdi_name_e from view_concept_art_map where cm_use and cm_delcause is null and md_id=? and mv_id=? and mr_id<=? and ci_id=? and cb_id=? and art_id=? order by mr_id desc,art_hist_serial desc limit 1|) or die $dbh->errstr;
						$sth->execute($md_id,$mv_id,$mr_id,$ci_id,$cb_id,$PinPartID) or die $dbh->errstr;
						$sth->bind_col(1, \$cdi_name, undef);
						$sth->bind_col(2, \$cdi_name_e, undef);
						$sth->fetch;
						$sth->finish;
						undef $sth;

						my $MARKER = {
							id        => defined $cdi_name ? $cdi_name : $item->{PinPartID},
							name      => defined $cdi_name_e ? $cdi_name_e : $item->{PinPartName},
							worldPosX => $item->{PinX},
							worldPosY => $item->{PinY},
							worldPosZ => $item->{PinZ},
							arrVecX   => $item->{PinArrowVectorX},
							arrVecY   => $item->{PinArrowVectorY},
							arrVecZ   => $item->{PinArrowVectorZ},
							upVecX    => $item->{PinUpVectorX},
							upVecY    => $item->{PinUpVectorY},
							upVecZ    => $item->{PinUpVectorZ},
							coordId   => $item->{PinCoordinateSystemName},
							total     => 0
						};
						$content = &cgi_lib::common::encodeJSON($MARKER);
					}
				};
				if($@){
					print $OUT __LINE__,":[$@]\n";
					$content = $@;
				}
			}else{
				$content = $parser->getContent();
#				&cgi_lib::common::message('$content='.$content,$OUT);
			}
			$Status = $parser->getContentStatus();
			$Code = $parser->getContentCode();
			$ContentType = $parser->getContentType();
		}
	}

	if(defined $Status){
#		&cgi_lib::common::message('$Status='.$Status,$OUT);
#		&cgi_lib::common::message('$Code='.$Code,$OUT);
#		&cgi_lib::common::message('$ContentType='.$ContentType,$OUT);

		print qq|Status: $Status\n|;
#		exit if($Code ne '200');
#		print qq|\n|;
	}

	#print "Content-Type:$ContentType\n\n";
	#binmode(STDOUT);
	#print $content;

#	if(exists($parser->{jsonObj}->{callback})){
#		print $parser->{jsonObj}->{callback},"(",$content,")";
#	}else{
#		print $content;
#	}
	if($Code eq '200'){
		if(defined $parser && exists $parser->{jsonObj}->{callback}){
			say qq|Content-Type:application/javascript|;
		}else{
			say qq|Content-Type:$ContentType|;
		}
		&cgi_lib::common::_printContentJSON($content,defined $parser ? $parser->{'jsonObj'} : undef);
	}else{
		&cgi_lib::common::printContent($content,$ContentType);
	}

	print $OUT __LINE__,":[$content]\n" if(defined $content);
	close $OUT;
	$ag_log->print(defined $parser ? $parser->{'jsonObj'} : undef,$content,defined $parser ? $parser->getBalancerInformation() : undef);
}

1;
