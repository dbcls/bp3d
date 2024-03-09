#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use Data::Dumper;
use List::Util;
use File::Spec;
use DBD::Pg;
use File::Spec::Functions qw(abs2rel rel2abs catdir catfile splitdir);
use Time::HiRes;
my $t0 = [&Time::HiRes::gettimeofday()];

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
require "webgl_common.pl";
use cgi_lib::common;
use BITS::ConceptArtMapModified;

use BITS::ConceptArtMapPart;
my $is_subclass_cdi_name = $BITS::ConceptArtMapPart::is_subclass_cdi_name;

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);
my($logfile,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

=pod
$FORM{ag_data}=qq|obj/bp3d/4.0|;
$FORM{f_id}=qq|root|;
$FORM{model}=qq|bp3d|;
$FORM{node}=qq|root|;
$FORM{tree}=qq|isa|;
$FORM{version}=qq|4.0|;
=cut

my $LOG;
my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
#$logfile .= sprintf(".%04d%02d%02d%02d",$year+1900,$mon+1,$mday,$hour);
$logfile .=  sprintf(".%02d%02d%02d.%05d",$hour,$min,$sec,$$);
open($LOG,">> $logfile");
select($LOG);
$| = 1;
select(STDOUT);

flock($LOG,2);
print $LOG "\n[$logtime]:$0\n";
&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG) if(defined $LOG);

my $DATAS = {
	'datas'   => [],
	'total'   => 0,
	'success' => JSON::XS::false
};
#$FORM{'ci_id'}=1;
$FORM{'cmd'} = qq|read| unless(defined $FORM{'cmd'});



my $ci_id=$FORM{'ci_id'};
my $cb_id=$FORM{'cb_id'};
my $md_id=$FORM{'md_id'};
my $mv_id=$FORM{'mv_id'};
my $crl_id=$FORM{'crl_id'};

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
$FORM{'ci_id'}=$ci_id;
$FORM{'cb_id'}=$cb_id;
$FORM{'md_id'}=$md_id;
$FORM{'mv_id'}=$mv_id;
$FORM{'crl_id'}=$crl_id;



unless(
	defined $FORM{'cmd'} &&
	defined $FORM{'ci_id'}
){
	&gzip_json($DATAS);
	exit;
}

if($FORM{'cmd'} eq 'read'){

	unless(
		(exists $FORM{'art_id'}    && defined $FORM{'art_id'}    && length $FORM{'art_id'})   ||
		(exists $FORM{'art_ids'}   && defined $FORM{'art_ids'}   && length $FORM{'art_ids'})  ||
		(exists $FORM{'cdi_names'} && defined $FORM{'cdi_names'} && length $FORM{'cdi_names'})
	){
		&gzip_json($DATAS);
		exit;
	}
	eval{
		my @bind_values;

		my $sql=<<SQL;
select
 arti.art_id,
 arti.art_name,
 arti.art_ext,
 EXTRACT(EPOCH FROM arti.art_entry) as arti_entry,
 cm.cdi_id,
 cm.cdi_name,
 cm.cdi_name_e,
-- cm.cm_id,
 cm.cmp_id,
 cm.cm_use,
 cm.cm_comment
from
 art_file_info as arti

left join (
 select
  art_id,
  cm.cdi_id,
  cdi.cdi_name,
  cdi.cdi_name_e,
--  cm_id,
  cmp_id,
  cm_use,
  cm_comment,
  cm_entry
 from
  concept_art_map as cm

 left join (
  select
   ci_id,
   cdi_id,
   cdi_name,
   cdi_name_e
  from
   concept_data_info
  where
   cdi_delcause is null
 ) as cdi on
  cm.ci_id=cdi.ci_id and
  cm.cdi_id=cdi.cdi_id

 where
  cm_delcause is null and
  cm.ci_id=$FORM{'ci_id'}
) as cm on
 cm.art_id=arti.art_id

where
 art_delcause is null and
SQL

		if(exists $FORM{'art_id'} && defined $FORM{'art_id'} && length $FORM{'art_id'}){
			push @bind_values,split(/[^A-Za-z0-9]+/,$FORM{'art_id'});
			if(scalar @bind_values){
				$sql .= qq|arti.art_id in (| . join(",",map {'?'} @bind_values) . qq|)|;
			}
		}
		elsif(exists $FORM{'art_ids'} && defined $FORM{'art_ids'} && length $FORM{'art_ids'}){
			my $art_ids = &cgi_lib::common::decodeJSON($FORM{'art_ids'});
			if(defined $art_ids && ref $art_ids eq 'ARRAY' && scalar @$art_ids){
				push @bind_values,(map {$_->{'art_id'}} @$art_ids);
				$sql .= qq|arti.art_id in (|. join(",",map {'?'} @$art_ids) . ')';
			}
		}
		elsif(exists $FORM{'cdi_names'} && defined $FORM{'cdi_names'} && length $FORM{'cdi_names'}){
			my $cdi_names = &cgi_lib::common::decodeJSON($FORM{'cdi_names'});
			if(defined $cdi_names && ref $cdi_names eq 'ARRAY' && scalar @$cdi_names){
				my $sql_cm = qq|
 select
  cdi_id
 from
  concept_art_map
 where
  cm_delcause is null and
  ci_id=$FORM{'ci_id'}
  and cdi_id=?
|;

				my $sth_cm = $dbh->prepare($sql_cm) or die $dbh->errstr;

				my $cdi_id;
				my %cdi_ids_hash;

				my $sql_bul = qq|select distinct cdi_id from concept_data_info where cdi_delcause is null and ci_id=$FORM{'ci_id'} AND cdi_name in (|. join(",",map {'?'} @$cdi_names) . ')';
				print $LOG __LINE__,":\$sql_bul=[$sql_bul]\n" if(defined $LOG);
				my $sth = $dbh->prepare($sql_bul) or die $dbh->errstr;
				$sth->execute(map {$_->{'cdi_name'}} @$cdi_names) or die $dbh->errstr;
				if($sth->rows()){
					my $column_number = 0;
					$sth->bind_col(++$column_number, \$cdi_id,   undef);
					while($sth->fetch){
						$cdi_ids_hash{$cdi_id} = 0 if(defined $cdi_id);
					}
				}
				$sth->finish;
				undef $sth;

&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%cdi_ids_hash), $LOG) if(defined $LOG);

				foreach my $id (keys(%cdi_ids_hash)){
					$sth_cm->execute($id) or die $dbh->errstr;
					$cdi_ids_hash{$id} = $sth_cm->rows();
					$sth_cm->finish;
				}

				my @cdi_ids = grep {$cdi_ids_hash{$_}>0} keys(%cdi_ids_hash);
&cgi_lib::common::message("\@cdi_ids=[".join(",",@cdi_ids)."]", $LOG) if(defined $LOG);
				if(scalar @cdi_ids){
					push @bind_values, @cdi_ids;
					$sql .= qq|cm.cdi_id in (|. join(",",map {'?'} @cdi_ids) . ')';
				}else{
					$DATAS->{'success'} = JSON::XS::true;
&cgi_lib::common::message(&cgi_lib::common::encodeJSON($DATAS), $LOG) if(defined $LOG);
					&gzip_json($DATAS);
					close($LOG);
					exit;
				}
			}
		}

&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

		print $LOG __LINE__,":\$sql=[$sql]\n";
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\@bind_values), $LOG) if(defined $LOG);

		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute(@bind_values) or die $dbh->errstr;
		$DATAS->{'total'} = $sth->rows();
		print $LOG __LINE__,":\$DATAS->{'total'}=[",$DATAS->{'total'},"]\n";

&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

		my $column_number;
		my $art_id;
		my $art_name;
		my $art_ext;
		my $arti_entry;
		my $cdi_id;
		my $cdi_name;
		my $cdi_name_e;
		my $cm_id;
		my $cmp_id;
		my $cm_use;
		my $cm_comment;

		my ($ELEMENT, $COMP_DENSITY_USE_TERMS, $COMP_DENSITY_END_TERMS, $COMP_DENSITY, $CDI_MAP, $CDI_MAP_ART_DATE, $CDI_ID2CID, $CDI_MAP_SUM_VOLUME_DEL_ID);

		if($DATAS->{'total'}){
			my %USE_CDI_ID;
			$column_number = 0;
			$sth->bind_col(++$column_number, \$art_id,     undef);
			$sth->bind_col(++$column_number, \$art_name,   undef);
			$sth->bind_col(++$column_number, \$art_ext,    undef);
			$sth->bind_col(++$column_number, \$arti_entry, undef);
			$sth->bind_col(++$column_number, \$cdi_id,     undef);
			while($sth->fetch){
				$USE_CDI_ID{$cdi_id} = undef if(defined $cdi_id);
			}
			$sth->finish;

			$sth->execute(@bind_values) or die $dbh->errstr;

			my $cdi_ids = [keys %USE_CDI_ID];
			if(scalar @$cdi_ids){
				($ELEMENT, $COMP_DENSITY_USE_TERMS, $COMP_DENSITY_END_TERMS, $COMP_DENSITY, $CDI_MAP, $CDI_MAP_ART_DATE, $CDI_ID2CID, $CDI_MAP_SUM_VOLUME_DEL_ID) = &BITS::ConceptArtMapModified::calcElementAndDensity(
					dbh     => $dbh,
					md_id   => $md_id,
					mv_id   => $mv_id,
					ci_id   => $ci_id,
					cb_id   => $cb_id,
					crl_id  => $crl_id,
					cdi_ids => $cdi_ids,
					LOG => $LOG
				);
			}
&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);
		}

		my $sql_art =<<SQL;
select 
 EXTRACT(EPOCH FROM art_timestamp) as art_timestamp,
 art_md5,
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
 art_volume
-- ,art_cube_volume
from
 art_file_info
where
 art_id=?
SQL
		my $sth_art = $dbh->prepare($sql_art) or die $dbh->errstr;

		my $sql_arto =<<SQL;
select 
 arto_id,
 arto_comment,
 art_name as arto_name,
 art_ext as arto_ext
from
 art_file_info as arto
where
 arto.art_id=?
SQL
		my $sth_arto = $dbh->prepare($sql_arto) or die $dbh->errstr;

		my $sql_arta =<<SQL;
select
 art_comment,
 art_category,
 art_judge,
 art_class
from
 art_file_info
where
 art_id=?
SQL
		my $sth_arta = $dbh->prepare($sql_arta) or die $dbh->errstr;

		my $param_datas;
		my $order = 0;
		if(exists $FORM{'art_ids'} && defined $FORM{'art_ids'} && length $FORM{'art_ids'}){
			my $datas = &JSON::XS::decode_json($FORM{'art_ids'});
			foreach my $data (@$datas){
				$param_datas->{$data->{'art_id'}} = $data;
				$param_datas->{$data->{'art_id'}}->{'_order'} = ++$order;
			}
		}
		elsif(exists $FORM{'cm_use_keys'} && defined $FORM{'cm_use_keys'} && length $FORM{'cm_use_keys'}){
			my $datas = &JSON::XS::decode_json($FORM{'cm_use_keys'});
			foreach my $data (@$datas){
				$param_datas = {} unless(defined $param_datas);
				$param_datas->{$data->{'art_id'}} = {} unless(defined $param_datas->{$data->{'art_id'}});
				$param_datas->{$data->{'art_id'}}->{$data->{'cdi_name'}} = $data;
				$param_datas->{$data->{'art_id'}}->{$data->{'cdi_name'}}->{'_order'} = ++$order;
			}
		}
		elsif(exists $FORM{'cdi_names'} && defined $FORM{'cdi_names'} && length $FORM{'cdi_names'}){
			my $datas = &JSON::XS::decode_json($FORM{'cdi_names'});
			foreach my $data (@$datas){
				$param_datas->{$data->{'cdi_name'}} = $data;
				$param_datas->{$data->{'cdi_name'}}->{'_order'} = ++$order;
			}
		}


#		my $sth_data = $dbh->prepare(qq|select art_data from history_art_file where art_id=? AND hist_serial=?|) or die $dbh->errstr;
#		my $sth_data = $dbh->prepare(qq|select art_data from art_file where art_id=? order by art_serial desc NULLS FIRST limit 1|) or die $dbh->errstr;
		my $sth_aff = $dbh->prepare(qq|select COALESCE(aff.artf_id,0) as artf_id, COALESCE(af.artf_name,'/') as artf_name from art_folder_file as aff left join (select * from art_folder) as af on aff.artf_id=af.artf_id where artff_delcause is null and artf_delcause is null and art_id=? order by aff.artff_timestamp desc NULLS FIRST limit 1|) or die $dbh->errstr;

		my $sth_cmp_id_sel = $dbh->prepare(qq|select cmp_id from concept_art_map_part where cmp_abbr=?|) or die $dbh->errstr;

#		my $sth_art_folder = $dbh->prepare(qq|select COALESCE(paf.artf_id,0),COALESCE(paf.artf_name,'/') from art_folder as af left join (select artf_id,artf_name from art_folder where artf_delcause is null) paf on paf.artf_id=af.artf_pid where af.artf_delcause is null and af.artf_id=?|) or die $dbh->errstr;


		$column_number = 0;
		$sth->bind_col(++$column_number, \$art_id,     undef);
		$sth->bind_col(++$column_number, \$art_name,   undef);
		$sth->bind_col(++$column_number, \$art_ext,    undef);
		$sth->bind_col(++$column_number, \$arti_entry, undef);


		$sth->bind_col(++$column_number, \$cdi_id,     undef);
		$sth->bind_col(++$column_number, \$cdi_name,   undef);
		$sth->bind_col(++$column_number, \$cdi_name_e, undef);
#		$sth->bind_col(++$column_number, \$cm_id,      undef);
		$sth->bind_col(++$column_number, \$cmp_id,     undef);
		$sth->bind_col(++$column_number, \$cm_use,     undef);
		$sth->bind_col(++$column_number, \$cm_comment, undef);

&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

		while($sth->fetch){

			my $cm_max_entry_cdi;
			my $seg_id;
			my $seg_name;
			my $seg_color;
			my $seg_thum_bgcolor;
			my $seg_thum_fgcolor;

			my $art_timestamp;
			my $art_md5;
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
			$sth_art->execute($art_id) or die $dbh->errstr;
			$column_number = 0;
			$sth_art->bind_col(++$column_number, \$art_timestamp, undef);
			$sth_art->bind_col(++$column_number, \$art_md5, undef);
			$sth_art->bind_col(++$column_number, \$art_data_size, undef);
			$sth_art->bind_col(++$column_number, \$art_xmin, undef);
			$sth_art->bind_col(++$column_number, \$art_xmax, undef);
			$sth_art->bind_col(++$column_number, \$art_ymin, undef);
			$sth_art->bind_col(++$column_number, \$art_ymax, undef);
			$sth_art->bind_col(++$column_number, \$art_zmin, undef);
			$sth_art->bind_col(++$column_number, \$art_zmax, undef);
			$sth_art->bind_col(++$column_number, \$art_xcenter, undef);
			$sth_art->bind_col(++$column_number, \$art_ycenter, undef);
			$sth_art->bind_col(++$column_number, \$art_zcenter, undef);
			$sth_art->bind_col(++$column_number, \$art_volume, undef);
#			$sth_art->bind_col(++$column_number, \$art_cube_volume, undef);
			$sth_art->fetch;
			$sth_art->finish;

			my $arto_id;
			my $arto_comment;
			my $arto_name;
			my $arto_ext;
			my $artog_id;
			my $artog_name;
			$sth_arto->execute($art_id) or die $dbh->errstr;
			$column_number = 0;
			$sth_arto->bind_col(++$column_number, \$arto_id, undef);
			$sth_arto->bind_col(++$column_number, \$arto_comment, undef);
			$sth_arto->bind_col(++$column_number, \$arto_name, undef);
			$sth_arto->bind_col(++$column_number, \$arto_ext, undef);
			$sth_arto->fetch;
			$sth_arto->finish;

			my $art_comment;
			my $art_mirroring;
			my $art_category;
			my $art_judge;
			my $art_class;
			$sth_arta->execute($art_id) or die $dbh->errstr;
			$column_number = 0;
			$sth_arta->bind_col(++$column_number, \$art_comment, undef);
			$sth_arta->bind_col(++$column_number, \$art_category, undef);
			$sth_arta->bind_col(++$column_number, \$art_judge, undef);
			$sth_arta->bind_col(++$column_number, \$art_class, undef);
			$sth_arta->fetch;
			$sth_arta->finish;

			my @max_timestamp;
			push(@max_timestamp, $arti_entry) if(defined $arti_entry);
			push(@max_timestamp, $art_timestamp) if(defined $art_timestamp);
			my $art_modified = &List::Util::max(@max_timestamp);

			my $file_name = $art_name;
			$file_name .= $art_ext unless($art_name =~ /$art_ext$/);

			my $obj_abs_path = &catdir($FindBin::Bin,'art_file');
			my $obj_rel_path = &abs2rel($obj_abs_path,$FindBin::Bin);

			my $file_path = &catfile($obj_abs_path,qq|$art_id$art_ext|);
			my $path = &File::Basename::basename($file_path);

#			&cgi_lib::common::message($file_path, $LOG) if(defined $LOG);
#			&cgi_lib::common::message(&abs2rel($file_path,$FindBin::Bin), $LOG) if(defined $LOG);
#			my $path = &File::Basename::basename(&abs2rel($file_path,$FindBin::Bin));
=pod
			if(defined $art_data_size && defined $art_timestamp){
				my($s,$t) = (stat($file_path))[7,9] if(-e $file_path);
				unless($s==$art_data_size && $t==$art_timestamp){
					my $art_data;
					$sth_data->execute($art_id) or die $dbh->errstr;
					$sth_data->bind_col(1, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
					$sth_data->fetch;
					$sth_data->finish;

					if(defined $art_data && open(my $OBJ,"> $file_path")){
						flock($OBJ,2);
						binmode($OBJ,':utf8');
						print $OBJ $art_data;
						close($OBJ);
						utime $art_timestamp,$art_timestamp,$file_path;
					}
					undef $art_data;
				}
			}
=cut
			my $artf_id;
			my $artf_name;
			$sth_aff->execute($art_id) or die $dbh->errstr;
			$sth_aff->bind_col(1, \$artf_id, undef);
			$sth_aff->bind_col(2, \$artf_name, undef);
			$sth_aff->fetch;
			$sth_aff->finish;

			my $thumbnail_path;
			unless(defined $thumbnail_path && -e $thumbnail_path && -f $thumbnail_path && -s $thumbnail_path){
				my $img_size = [undef,undef,undef,[16,16]];
				my($img_prefix,$img_path) = &getObjImagePrefix($art_id);
				my $img_info = &getImageFileList($img_prefix, $img_size);
				$thumbnail_path = sprintf($img_info->{'gif_fmt'},$img_prefix,$img_info->{'sizeStrXS'});
			}
			if(-e $thumbnail_path && -f $thumbnail_path && -s $thumbnail_path){
				$thumbnail_path = sprintf(qq|<img align=center width=16 height=16 src="%s?%s">|,&abs2rel($thumbnail_path,$FindBin::Bin),(stat($thumbnail_path))[9]);
			}else{
				$thumbnail_path = undef;
			}

			if(defined $cdi_name && $cdi_name =~ /$is_subclass_cdi_name/){
				$cdi_name = $1;
				my $cmp_abbr = $2;
				$sth_cmp_id_sel->execute($cmp_abbr) or die $dbh->errstr;
				my $cmp_rows = $sth_cmp_id_sel->rows();
				my $hash_cmp;
				$hash_cmp = $sth_cmp_id_sel->fetchrow_hashref if($cmp_rows>0);
				$sth_cmp_id_sel->finish;
				$cmp_id = $hash_cmp->{'cmp_id'} if(defined $hash_cmp && ref $hash_cmp eq 'HASH' && exists $hash_cmp->{'cmp_id'} && defined $hash_cmp->{'cmp_id'});
			}

			my $current_use;
			my $current_use_reason;
			if(defined $cdi_id && defined $art_id && defined $CDI_MAP_ART_DATE && ref $CDI_MAP_ART_DATE eq 'HASH' && exists $CDI_MAP_ART_DATE->{$cdi_id} && defined $CDI_MAP_ART_DATE->{$cdi_id} && ref $CDI_MAP_ART_DATE->{$cdi_id} eq 'HASH' && exists $CDI_MAP_ART_DATE->{$cdi_id}->{$art_id}){
				$current_use = JSON::XS::true;	#子供のOBJより古くない場合
				$current_use_reason = undef;
			}else{
				$current_use = JSON::XS::false;
				$current_use_reason = 'Older than the other OBJ or descendants of OBJ';
			}

			my $HASH = {
				art_id   => $art_id,
				art_name => $art_name,
				art_ext => $art_ext,

				cdi_id => $cdi_id,
				cdi_name => $cdi_name,
				cdi_name_e => $cdi_name_e,
#				cm_id => $cm_id,
				cmp_id => defined $cmp_id ? $cmp_id-0 : 0,
				cm_comment => $cm_comment,

				art_filename => qq|$art_name$art_ext|,

				cm_use         => defined $cdi_id ? (defined $cm_use && $cm_use ? JSON::XS::true : JSON::XS::false) : JSON::XS::true,
				never_current  => defined $cdi_id ? (defined $cm_use && $cm_use ? JSON::XS::false : JSON::XS::true) : JSON::XS::false,

				current_use => $current_use,
				current_use_reason => $current_use_reason,

#				art_path => $path,
				art_path       => &abs2rel($file_path,$FindBin::Bin),
				art_tmb_path   => $thumbnail_path,

				art_modified => $art_modified,

				art_timestamp   => $art_timestamp - 0,
				art_modified    => $art_modified,
				art_data_size   => $art_data_size - 0,

				art_xmin   => $art_xmin - 0,
				art_xmax   => $art_xmax - 0,
				art_ymin   => $art_ymin - 0,
				art_ymax   => $art_ymax - 0,
				art_zmin   => $art_zmin - 0,
				art_zmax   => $art_zmax - 0,
				art_volume => $art_volume - 0,

				art_xcenter => $art_xcenter - 0,
				art_ycenter => $art_ycenter - 0,
				art_zcenter => $art_zcenter - 0,

				arta_comment    => $art_comment,
				arta_mirroring  => $art_mirroring ? JSON::XS::true : JSON::XS::false,,
				arta_category   => $art_category,
				arta_judge      => $art_judge,
				arta_class      => $art_class,

				arto_id      => $arto_id,
				arto_comment => $arto_comment,
				arto_name    => $arto_name,
				arto_ext     => $arto_ext,

				ci_id => $FORM{'ci_id'}-0,

				artf_id => $artf_id,
				artf_name => $artf_name,

#				selected => JSON::XS::true
			};

			if(defined $param_datas){
				if(exists $FORM{'art_ids'} && defined $FORM{'art_ids'} && length $FORM{'art_ids'}){
					if(exists $param_datas->{$art_id}){
						foreach my $key (keys(%{$param_datas->{$art_id}})){
							$HASH->{$key} = $param_datas->{$art_id}->{$key} unless(defined $HASH->{$key});
						}
					}
				}
				elsif(exists $FORM{'cm_use_keys'} && defined $FORM{'cm_use_keys'} && length $FORM{'cm_use_keys'}){
					if(exists $param_datas->{$art_id} && exists $param_datas->{$art_id}->{$cdi_name}){
						foreach my $key (keys(%{$param_datas->{$art_id}->{$cdi_name}})){
							$HASH->{$key} = $param_datas->{$art_id}->{$cdi_name}->{$key} unless(defined $HASH->{$key});
						}
					}
				}
				elsif(exists $FORM{'cdi_names'} && defined $FORM{'cdi_names'} && length $FORM{'cdi_names'}){
					if(exists $param_datas->{$cdi_name}){
						foreach my $key (keys(%{$param_datas->{$cdi_name}})){
							$HASH->{$key} = $param_datas->{$cdi_name}->{$key} unless(defined $HASH->{$key});
						}
					}
				}
			}


			push(@{$DATAS->{'datas'}},$HASH);
		}
		$sth->finish;
		undef $sth;

		if(defined $param_datas){
			@{$DATAS->{'datas'}} = map {delete $_->{'_order'};$_} sort {exists $a->{'_order'} && exists $b->{'_order'} ? $a->{'_order'} <=> $b->{'_order'} : 0} @{$DATAS->{'datas'}};
		}

		$DATAS->{'success'} = JSON::XS::true;
	};
	if($@){
		$DATAS->{'msg'} = $@;
		print $LOG __LINE__,":",$@,"\n";
	}
}
#print $LOG __LINE__,":\$DATAS=[".&JSON::XS::encode_json($DATAS)."]\n";
&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);
&gzip_json($DATAS);
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
