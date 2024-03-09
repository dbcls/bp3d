#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';


use JSON::XS;
use File::Basename;
use Cwd qw(abs_path);
use File::Spec::Functions qw(abs2rel rel2abs catdir catfile splitdir);
use CGI;
use CGI::Carp qw(fatalsToBrowser);
#use CGI::Carp::DebugScreen ( debug => 1 );
use Data::Dumper;
use DBD::Pg;
use POSIX;
use List::Util;
use List::MoreUtils;
use Hash::Merge;
use Time::HiRes;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;

use BITS::Config;
use BITS::VTK;
use BITS::Voxel;
use BITS::ConceptArtMapModified;

use obj2deci;
require "webgl_common.pl";
use cgi_lib::common;
use AG::login;


my $query = CGI->new;
my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
#my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);
$FORM{$_} = &cgi_lib::common::decodeUTF8($FORM{$_}) for(sort keys(%FORM));
$COOKIE{$_} = &cgi_lib::common::decodeUTF8($COOKIE{$_}) for(sort keys(%COOKIE));
if(exists($COOKIE{'ag_annotation.session'})){
	my $session_info = {};
	$session_info->{'PARAMS'}->{$_} = $FORM{$_} for(sort keys(%FORM));
	$session_info->{'COOKIE'}->{$_} = $COOKIE{$_} for(sort keys(%COOKIE));
	&AG::login::setSessionHistory($session_info);
}

my($log_file,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

#my @extlist = qw|.cgi|;
#my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);

my $t0 = [&Time::HiRes::gettimeofday()];
my($epocsec,$microsec) = &Time::HiRes::gettimeofday();
my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);

#my $log_file = qq|$FindBin::Bin/logs/$cgi_name.txt|;
$log_file .= qq|.$FORM{'cmd'}| if(exists $FORM{'cmd'});

$log_file .= qq|.artg_ids| if(exists $FORM{'artg_ids'});
$log_file .= qq|.art_datas| if(exists $FORM{'art_datas'});
#$log_file .=  sprintf(".%04d%02d%02d%02d",$year+1900,$mon+1,$mday,$hour);
$log_file .=  sprintf(".%02d%02d%02d.%05d",$hour,$min,$sec,$$);

my $LOG;
open($LOG,">> $log_file");
select($LOG);
$| = 1;
select(STDOUT);

if(defined $LOG){
	&cgi_lib::common::message(sprintf("\n%04d:%04d/%02d/%02d %02d:%02d:%02d.%d",__LINE__,$year+1900,$mon+1,$mday,$hour,$min,$sec,$microsec), $LOG);
	&cgi_lib::common::message(\%ENV, $LOG);
	&cgi_lib::common::message(\%FORM, $LOG);

	#$epocsec = &Time::HiRes::tv_interval($t0);
	&cgi_lib::common::dumper($epocsec, $LOG);

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

unless(defined $ci_id && defined $cb_id && defined $md_id && defined $mv_id){
	$DATAS->{'success'} = JSON::XS::true;
	&cgi_lib::common::printContentJSON($DATAS,\%FORM);
	close($LOG) if(defined $LOG);
	exit;
}

$crl_id = 0 unless(defined $crl_id);
#$crl_id = 3 unless(defined $crl_id);

if(defined $LOG){
	&cgi_lib::common::message('$md_id='.$md_id, $LOG);
	&cgi_lib::common::message('$mv_id='.$mv_id, $LOG);
	&cgi_lib::common::message('$ci_id='.$ci_id, $LOG);
	&cgi_lib::common::message('$cb_id='.$cb_id, $LOG);
	&cgi_lib::common::message('$crl_id='.$crl_id, $LOG);
}
$FORM{'ci_id'}=$ci_id;
$FORM{'cb_id'}=$cb_id;
$FORM{'md_id'}=$md_id;
$FORM{'mv_id'}=$mv_id;
$FORM{'crl_id'}=$crl_id;


umask(0);
my $art_abs_path = &catdir($FindBin::Bin,'art_file');
&File::Path::mkpath($art_abs_path,{mode=>0777}) unless(-e $art_abs_path);

if($FORM{'cmd'} eq 'read'){
	eval{
		my $datas = &cgi_lib::common::decodeJSON($FORM{'datas'});
		&cgi_lib::common::message($datas, $LOG);
		if(defined $datas && ref $datas eq 'ARRAY' && scalar @$datas >= 2){
			my $sql =<<SQL;
SELECT
 arti.art_id,
 cm.cdi_id,

 arti.art_name,
 arti.art_ext,
 (arti.art_name || arti.art_ext) AS art_filename,
 arti.art_mirroring,

 EXTRACT(EPOCH FROM arti.art_timestamp)::integer AS art_timestamp,
 EXTRACT(EPOCH FROM arti.art_modified)::integer AS art_modified,
 EXTRACT(EPOCH FROM art.art_modified)::integer AS art_upload_modified,
 arti.art_md5,
 arti.art_data_size,
 arti.art_xmin,
 arti.art_xmax,
 arti.art_ymin,
 arti.art_ymax,
 arti.art_zmin,
 arti.art_zmax,
 to_number(to_char((arti.art_xmax+arti.art_xmin)/2,'FM99990D0000'),'99990D0000S') AS art_xcenter,
 to_number(to_char((arti.art_ymax+arti.art_ymin)/2,'FM99990D0000'),'99990D0000S') AS art_ycenter,
 to_number(to_char((arti.art_zmax+arti.art_zmin)/2,'FM99990D0000'),'99990D0000S') AS art_zcenter,
 arti.art_volume,

 arti.arto_id,

 arti.art_comment,
 arti.art_category,
 arti.art_judge,
 arti.art_class,

 cdi.cdi_name,
 COALESCE(cd.cd_name,cdi.cdi_name_e) AS cdi_name_e,
 COALESCE(cd.cd_exists,false) AS cd_exists,

 cm.cm_comment,
 cm.cmp_id,
 cm.cm_use,
 EXTRACT(EPOCH FROM cm.cm_entry)::integer AS cm_entry,

 seg_color,

 arti.prefix_id,
 arti.art_serial,

 cdi.cp_id,
 cdi.cl_id,

 CASE WHEN cm.cm_entry>=fm_timestamp THEN true
      ELSE false
 END AS cm_edited

FROM
 art_file_info AS arti

LEFT JOIN (
  SELECT
   art_id,
   art_modified
  FROM
   art_file
 ) AS art on
   arti.art_id=art.art_id

LEFT JOIN (
  SELECT
   ci_id,
   cdi_id,
   art_id,
   cm_comment,
   cmp_id,
   cm_use,
   cm_entry
  FROM
   concept_art_map
  WHERE
--   cm_use and
   cm_delcause is null and
   md_id=$md_id and
   mv_id=$mv_id
 ) AS cm on
   arti.art_id=cm.art_id

left join (
  SELECT
   ci_id,
   cdi_id,
   cdi_name,
   cdi_name_e,
   cp_id,
   cl_id
  FROM
   concept_data_info
  WHERE
   cdi_delcause is null and
   ci_id=$ci_id
 ) AS cdi on
   cdi.cdi_id=cm.cdi_id

LEFT JOIN (
  SELECT cdi_id, cd_name, seg_id, true AS cd_exists FROM concept_data WHERE ci_id=$ci_id AND cb_id=$cb_id
 ) cd ON cd.cdi_id = cm.cdi_id
LEFT JOIN (
  SELECT seg_id, seg_color, seg_thum_bgcolor FROM concept_segment
 ) cs ON cd.seg_id = cs.seg_id

CROSS JOIN (
  SELECT MAX(fm_timestamp) AS fm_timestamp FROM freeze_mapping WHERE fm_point
 ) fm

WHERE
 arti.art_delcause IS NULL AND
 arto_id=?
SQL
			my $sth = $dbh->prepare($sql) or die $dbh->errstr;
			my @ART_IDS = sort &List::MoreUtils::uniq(map {$_->{'art_id'}} @$datas);
			my $arto_id = join(';',@ART_IDS);
			$sth->execute($arto_id) or die $dbh->errstr;
			my $column_number = 0;
			my $art_id;
			my $cdi_id;
			my %USE_CDI_ID;
			$sth->bind_col(++$column_number, \$art_id, undef);
			$sth->bind_col(++$column_number, \$cdi_id, undef);
			while($sth->fetch){
				$USE_CDI_ID{$cdi_id} = undef if(defined $cdi_id);
			}
			$sth->finish;

			my ($ELEMENT, $COMP_DENSITY_USE_TERMS, $COMP_DENSITY_END_TERMS, $COMP_DENSITY, $CDI_MAP, $CDI_MAP_ART_DATE, $CDI_ID2CID, $CDI_MAP_SUM_VOLUME_DEL_ID);
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


			$sth->execute($arto_id) or die $dbh->errstr;
			while(my $hash_ref = $sth->fetchrow_hashref){
				foreach my $key (qw/art_xmin art_xmax art_ymin art_ymax art_zmin art_zmax art_volume art_xcenter art_ycenter art_zcenter/){
					$hash_ref->{$key} -= 0;
				}
				$hash_ref->{'art_mirroring'} = $hash_ref->{'art_mirroring'} ? JSON::XS::true : JSON::XS::false;
				$hash_ref->{'cd_exists'} = $hash_ref->{'cd_exists'} ? JSON::XS::true : JSON::XS::false;
				$hash_ref->{'cm_use'} = $hash_ref->{'cm_use'} ? JSON::XS::true : JSON::XS::false;
				$hash_ref->{'cm_edited'} = $hash_ref->{'cm_edited'} ? JSON::XS::true : JSON::XS::false;

				my $art_rel_path = &abs2rel($art_abs_path,$FindBin::Bin);
				my $file_name = $hash_ref->{'art_filename'};
				my $file_path = &catfile($art_abs_path,$hash_ref->{'art_id'}.$hash_ref->{'art_ext'});

				my $img_prefix;
				my $img_path;
				my $img_info;
				my $thumbnail_path;
				my $thumbnail_timestamp;
				my $img_size = [undef,undef,undef,[16,16]];
				unless(defined $thumbnail_path && -e $thumbnail_path && -f $thumbnail_path && -s $thumbnail_path){
					($img_prefix,$img_path) = &getObjImagePrefix($hash_ref->{'art_id'});
					$img_info = &getImageFileList($img_prefix, $img_size);
					$thumbnail_path = sprintf($img_info->{'gif_fmt'},$img_prefix,$img_info->{'sizeStrXS'});
					&cgi_lib::common::message($thumbnail_path, $LOG) if(defined $LOG);
				}
				if(-e $thumbnail_path && -f $thumbnail_path && -s $thumbnail_path){
					$thumbnail_timestamp = (stat($thumbnail_path))[9];
					$thumbnail_path = &abs2rel($thumbnail_path,$FindBin::Bin);
				}else{
					$thumbnail_path = undef;
				}

				$hash_ref->{'art_path'}          = &abs2rel($file_path,$FindBin::Bin);
				$hash_ref->{'art_tmb_relpath'}   = $thumbnail_path;
				$hash_ref->{'art_tmb_timestamp'} = $thumbnail_timestamp;
				$hash_ref->{'art_tmb_path'}      = defined $thumbnail_path && defined $thumbnail_timestamp ? sprintf(qq|<img align=center width=16 height=16 src="%s?%s">|,$thumbnail_path,$thumbnail_timestamp) : undef;


				my $art_id = $hash_ref->{'art_id'};
				my $cdi_id = $hash_ref->{'cdi_id'};
				my $current_use;
				my $current_use_reason;
				if(defined $cdi_id && defined $art_id && defined $CDI_MAP_ART_DATE && ref $CDI_MAP_ART_DATE eq 'HASH' && exists $CDI_MAP_ART_DATE->{$cdi_id} && defined $CDI_MAP_ART_DATE->{$cdi_id} && ref $CDI_MAP_ART_DATE->{$cdi_id} eq 'HASH' && exists $CDI_MAP_ART_DATE->{$cdi_id}->{$art_id}){
					$current_use = JSON::XS::true;	#子供のOBJより古くない場合
					$current_use_reason = undef;
				}else{
					$current_use = JSON::XS::false;
					$current_use_reason = 'Older than the other OBJ or descendants of OBJ';
				}
				$hash_ref->{'current_use'}        = $current_use;
				$hash_ref->{'current_use_reason'} = $current_use_reason;

				push(@{$DATAS->{'datas'}},$hash_ref);
			}
			$sth->finish;
			undef $sth;

			$DATAS->{'total'} = scalar @{$DATAS->{'datas'}};
			$DATAS->{'success'} = JSON::XS::true;
		}
	};
	if($@){
		$DATAS->{'success'} = JSON::XS::false;
		$DATAS->{'total'} = 0;
		$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8($@);
	}
}
elsif($FORM{'cmd'} eq 'create'){
	$dbh->{'AutoCommit'} = 0;
	$dbh->{'RaiseError'} = 1;
	eval{
		my $datas = &cgi_lib::common::decodeJSON($FORM{'datas'});
		&cgi_lib::common::message($datas, $LOG);
		if(defined $datas && ref $datas eq 'ARRAY' && scalar @$datas >= 2){
			my $sql;
			my $sth;
			my $column_number;
			my @ART_IDS = sort &List::MoreUtils::uniq(map {$_->{'art_id'}} @$datas);
			my $arto_id = join(';',@ART_IDS);

			my $artf_id = $FORM{'artf_id'} - 0;
			$artf_id = undef unless($artf_id);

			my $art_name;# = $art_id;
			if(exists $FORM{'file_name'} && defined $FORM{'file_name'} && length $FORM{'file_name'}){
				&cgi_lib::common::message('',$LOG) if(defined $LOG);
				my $file_name = &cgi_lib::common::decodeUTF8($FORM{'file_name'});
				$file_name =~ s/\s*$//g;
				$file_name =~ s/^\s*//g;
				$file_name =~ s/\.obj$//ig;
				if(length $file_name){
					$file_name =~ s/\W/_/g;
					$art_name = $file_name;
				}
			}else{
				&cgi_lib::common::message('',$LOG) if(defined $LOG);
			}

			my $prefix_char = 'CX';
			$sth = $dbh->prepare('SELECT prefix_id FROM id_prefix WHERE prefix_char=?') or die $dbh->errstr;
			$sth->execute($prefix_char) or die $dbh->errstr;
			my $prefix_id;
			$column_number = 0;
			$sth->bind_col(++$column_number, \$prefix_id, undef);
			$sth->fetch;
			$sth->finish;
			undef $sth;

			$sql =<<SQL;
SELECT
 art_id,
 art_delcause
FROM
 art_file_info
WHERE
 prefix_id=? AND
 arto_id=?
SQL

			$sth = $dbh->prepare($sql) or die $dbh->errstr;
			$sth->execute($prefix_id,$arto_id) or die $dbh->errstr;
			my $rows = $sth->rows();
			my $art_id;
			my $art_delcause;
			if($rows){
				my $temp_art_name;
				$column_number = 0;
				$sth->bind_col(++$column_number, \$art_id, undef);
				$sth->bind_col(++$column_number, \$art_delcause, undef);
				$sth->fetch;
			}
			$sth->finish;
			undef $sth;

			&cgi_lib::common::message('$rows='.$rows,$LOG) if(defined $LOG && defined $rows);
			&cgi_lib::common::message('$art_id='.$art_id,$LOG) if(defined $LOG && defined $art_id);
			&cgi_lib::common::message('$art_delcause='.$art_id,$LOG) if(defined $LOG && defined $art_delcause);

			if(defined $art_id && defined $art_delcause){
				$art_name = $art_id unless(defined $art_name);
				$sth = $dbh->prepare('update art_file_info set art_name=?,art_delcause=NULL,art_modified=now() where art_id=?') or die $dbh->errstr;
				$sth->execute($art_name,$art_id) or die $dbh->errstr;
				$sth->finish();
				undef $sth;

				$sth = $dbh->prepare('SELECT * FROM art_folder_file WHERE COALESCE(artf_id,0)=COALESCE(?,0) AND art_id=?') or die $dbh->errstr;
				$sth->execute($artf_id,$art_id) or die $dbh->errstr;
				$rows = $sth->rows();
				$sth->finish();
				undef $sth;
				unless($rows){
					$sth = $dbh->prepare(qq|insert into art_folder_file (artf_id,art_id) values (?,?)|) or die $dbh->errstr;
				}
				else{
					$sth = $dbh->prepare(qq|UPDATE art_folder_file SET artff_delcause=NULL,artff_timestamp=now() WHERE COALESCE(artf_id,0)=COALESCE(?,0) AND art_id=?|) or die $dbh->errstr;
				}
				$sth->execute($artf_id,$art_id) or die $dbh->errstr;
				$sth->finish();
				undef $sth;

				$dbh->commit;
				$DATAS->{'success'} = JSON::XS::true;
				&make_art_image([$art_id]);
			}
			else{
				unless($rows){
					$sql =<<SQL;
SELECT
 (art_id || art_ext) AS art_filename,
 EXTRACT(EPOCH FROM art_timestamp)::integer AS art_timestamp,
 art_raw_data
FROM
 art_file
WHERE
 art_id IN (%s)
SQL
					$sth = $dbh->prepare(sprintf($sql,join(',',map {'?'} @ART_IDS))) or die $dbh->errstr;
					$sth->execute(@ART_IDS) or die $dbh->errstr;
					my $art_filename;
					my $art_timestamp_epoch;
					my $art_raw_data;
					my @ART_FILES;
					my @MAX_ART_TIMESTAMP_EPOCH;
					$column_number = 0;
					$sth->bind_col(++$column_number, \$art_filename, undef);
					$sth->bind_col(++$column_number, \$art_timestamp_epoch, undef);
					$sth->bind_col(++$column_number, \$art_raw_data, { pg_type => DBD::Pg::PG_BYTEA });
					while($sth->fetch){
						my $art_path = &catfile($art_abs_path,$art_filename);
						unless(-e $art_path && -f $art_path && -s $art_path){
							open(my $OUT, "> $art_path") or die qq|$! [$art_path]|;
							binmode($OUT);
							print $OUT $art_raw_data;
							close($OUT);
							utime $art_timestamp_epoch, $art_timestamp_epoch, $art_path;
						}
						push(@ART_FILES, $art_path);
						push(@MAX_ART_TIMESTAMP_EPOCH, $art_timestamp_epoch);
					}
					$sth->finish;
					undef $sth;
					my $max_art_timestamp_epoch = &List::Util::max(@MAX_ART_TIMESTAMP_EPOCH);

					$sth = $dbh->prepare('SELECT COALESCE(MAX(art_serial),0)+1 FROM art_file WHERE prefix_id=?') or die $dbh->errstr;
					$sth->execute($prefix_id) or die $dbh->errstr;
					my $art_serial;
					$column_number = 0;
					$sth->bind_col(++$column_number, \$art_serial, undef);
					$sth->fetch;
					$sth->finish;
					undef $sth;

					$art_id = qq|$prefix_char$art_serial|;
					$art_name = $art_id unless(defined $art_name);
					my $art_ext = '.obj';
					my $cx_temp_abs_path = &catdir($art_abs_path,".$$");
					my $cx_temp_prefix = &catfile($cx_temp_abs_path,$art_id);
					my $cx_temp_file = $cx_temp_prefix.$art_ext;
					&File::Path::mkpath($cx_temp_abs_path,{mode=>0777}) unless(-e $cx_temp_abs_path && -d $cx_temp_abs_path);
					my $cx_file = &catfile($art_abs_path,$art_id.$art_ext);
					my $cx_data;
					my $prop = &BITS::VTK::obj2normals(\@ART_FILES,$cx_temp_prefix);
					if(defined $prop && ref $prop eq 'HASH' && -e $cx_temp_file && -f $cx_temp_file && -s $cx_temp_file){
						$cx_data = &readObjFile($cx_temp_file);
						open(my $OUT,"> $cx_file") or die "$! [$cx_file]\n";
						say $OUT '# '.join('+',@ART_IDS);
						say $OUT '# '."$prop->{'bounds'}->[0],$prop->{'bounds'}->[1],$prop->{'bounds'}->[2],$prop->{'bounds'}->[3],$prop->{'bounds'}->[4],$prop->{'bounds'}->[5],$prop->{'volume'}";
						say $OUT '';
						print $OUT $cx_data;
						close($OUT);
						utime $max_art_timestamp_epoch,$max_art_timestamp_epoch,$cx_file;
					}
					&File::Path::remove_tree($cx_temp_abs_path) if(-e $cx_temp_abs_path && -d $cx_temp_abs_path);

					if(defined $cx_file && -e $cx_file && -f $cx_file && -s $cx_file && defined $cx_data && length $cx_data){
						$sql =<<SQL;
SELECT
 MAX(art_timestamp)
FROM
 art_file
WHERE
 art_id IN (%s)
SQL
						$sth = $dbh->prepare(sprintf($sql,join(',',map {'?'} @ART_IDS))) or die $dbh->errstr;
						$sth->execute(@ART_IDS) or die $dbh->errstr;
						my $art_timestamp;
						$column_number = 0;
						$sth->bind_col(++$column_number, \$art_timestamp, undef);
						$sth->fetch;
						$sth->finish;
						undef $sth;

						my $sql_art_ins =<<SQL;
insert into art_file (
  prefix_id,
  art_id,
  art_serial,
  art_name,
  art_ext,
  art_timestamp,
  art_md5,
  art_data,
  art_data_size,
  art_xmin,
  art_xmax,
  art_ymin,
  art_ymax,
  art_zmin,
  art_zmax,
  art_volume,
  art_raw_data,
  art_raw_data_size
) values (
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?
)
SQL
						my $sth_art_ins = $dbh->prepare($sql_art_ins) or die $dbh->errstr;

						my $sql_insert_art_file_info =<<SQL;
INSERT INTO
 art_file_info
 (
 art_id,
 art_name,
 art_ext,
 art_timestamp,
 art_mirroring,
 art_entry,
 art_openid,
 prefix_id,
 art_serial,
 art_md5,
 art_data_size,
 art_xmin,
 art_xmax,
 art_ymin,
 art_ymax,
 art_zmin,
 art_zmax,
 art_volume
 )
SELECT
 art_id,
 art_name,
 art_ext,
 art_timestamp,
 art_mirroring,
 art_entry,
 art_openid,
 prefix_id,
 art_serial,
 art_md5,
 art_data_size,
 art_xmin,
 art_xmax,
 art_ymin,
 art_ymax,
 art_zmin,
 art_zmax,
 art_volume
FROM
 art_file
WHERE
 art_id=?
SQL
						my $sth_arti_ins = $dbh->prepare($sql_insert_art_file_info) or die $dbh->errstr;

						my $sth_art_upd = $dbh->prepare('update art_file set art_name=?,art_timestamp=?,art_modified=now() where art_id=?') or die $dbh->errstr;
						my $sth_arti_upd = $dbh->prepare('update art_file_info set art_name=?,art_timestamp=?,art_modified=now() where art_id=?') or die $dbh->errstr;

						my $sth_arto_upd = $dbh->prepare(qq|update art_file_info set arto_id=?,arto_comment=?,art_modified=now() where art_id=?|) or die $dbh->errstr;
						my $sth_artff_ins = $dbh->prepare(qq|insert into art_folder_file (artf_id,art_id) values (?,?)|) or die $dbh->errstr;

						my $art_data_size = length $cx_data;
						my $art_md5 = &Digest::MD5::md5_hex($cx_data);
						my $param_num = 0;
						$sth_art_ins->bind_param(++$param_num, $prefix_id);
						$sth_art_ins->bind_param(++$param_num, $art_id);
						$sth_art_ins->bind_param(++$param_num, $art_serial);
						$sth_art_ins->bind_param(++$param_num, $art_name);
						$sth_art_ins->bind_param(++$param_num, $art_ext);
						$sth_art_ins->bind_param(++$param_num, $art_timestamp);
						$sth_art_ins->bind_param(++$param_num, $art_md5);
						$sth_art_ins->bind_param(++$param_num, $cx_data, { pg_type => DBD::Pg::PG_BYTEA });
						$sth_art_ins->bind_param(++$param_num, $art_data_size);
						$sth_art_ins->bind_param(++$param_num, $prop->{'bounds'}->[0]);
						$sth_art_ins->bind_param(++$param_num, $prop->{'bounds'}->[1]);
						$sth_art_ins->bind_param(++$param_num, $prop->{'bounds'}->[2]);
						$sth_art_ins->bind_param(++$param_num, $prop->{'bounds'}->[3]);
						$sth_art_ins->bind_param(++$param_num, $prop->{'bounds'}->[4]);
						$sth_art_ins->bind_param(++$param_num, $prop->{'bounds'}->[5]);
						$sth_art_ins->bind_param(++$param_num, defined $prop->{'volume'} && $prop->{'volume'} > 0 ?  &BITS::ConceptArtMapModified::Truncated($prop->{'volume'} / 1000) : 0);
						$sth_art_ins->bind_param(++$param_num, $cx_data, { pg_type => DBD::Pg::PG_BYTEA });
						$sth_art_ins->bind_param(++$param_num, $art_data_size);
						$sth_art_ins->execute() or die $dbh->errstr;
						$sth_art_ins->finish();

						$sth_arti_ins->execute($art_id) or die $dbh->errstr;
						$sth_arti_ins->finish();

						$sth_arto_upd->execute($arto_id,undef,$art_id) or die $dbh->errstr;
						$sth_arto_upd->finish;

						$sth_artff_ins->execute($artf_id,$art_id) or die $dbh->errstr;
						$sth_artff_ins->finish();

						&BITS::Voxel::insVoxelData($dbh,$art_id,$cx_data);

						$dbh->commit;
						$DATAS->{'success'} = JSON::XS::true;

						&make_art_image([$art_id]);
					}
					else{
						$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8('ファイルの変換に失敗しました。');
					}
				}
				else{
					$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8('CXファイルは既に存在しています。');
				}
			}
		}
		else{
			$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8('OBJファイルを２つ以上指定してください。');
		}
	};
	if($@){
		$DATAS->{'success'} = JSON::XS::false;
		$DATAS->{'total'} = 0;
		$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8($@);
		$dbh->rollback;
	}
	$dbh->{'AutoCommit'} = 1;
	$dbh->{'RaiseError'} = 0;
}


&gzip_json($DATAS);

exit;

sub make_art_image {
	my $art_ids = shift;
	return unless(defined $art_ids && ref $art_ids eq 'ARRAY' && scalar @$art_ids);
	my $prog_basename = qq|make_art_image|;
	my $prog = &catfile($FindBin::Bin,'..','cron',qq|$prog_basename.pl|);
	if(-e $prog && -x $prog){
		my $options = join(' ',map {"--obj $_"} @$art_ids);
		$options .= " --host $ENV{'AG_DB_HOST'}" if(exists $ENV{'AG_DB_HOST'} && defined $ENV{'AG_DB_HOST'} && length $ENV{'AG_DB_HOST'});
		$options .= " --port $ENV{'AG_DB_PORT'}" if(exists $ENV{'AG_DB_PORT'} && defined $ENV{'AG_DB_PORT'} && length $ENV{'AG_DB_PORT'});
		&cgi_lib::common::message($options, $LOG) if(defined $LOG);
		&cgi_lib::common::message(qq|nice -n 19 $prog $options|, $LOG) if(defined $LOG);

		my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
		my $mfmt = sprintf("%04d%02d%02d%02d%02d%02d.%d",$year+1900,$mon+1,$mday,$hour,$min,$sec,$$);
		my $pid = fork;
		if(defined $pid){
			if($pid == 0){
				my $logdir = &getLogDir();
				my $f1 = &catfile($logdir,qq|$prog_basename.log.$mfmt|);
				my $f2 = &catfile($logdir,qq|$prog_basename.err.$mfmt|);
				close(STDOUT);
				close(STDERR);
				open STDOUT, "> $f1" || die "[$f1] $!\n";
				open STDERR, "> $f2" || die "[$f2] $!\n";
				close(STDIN);
				exec(qq|nice -n 19 $prog $options|);
				exit(1);
			}else{
			}
		}else{
			die("Can't execute program");
		}
	}
}
