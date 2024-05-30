#!/opt/services/ag/local/perl/bin/perl

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
use Hash::Merge;
use Time::HiRes;
use Time::Piece;

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

use BITS::ConceptArtMapPart;
my $is_subclass_cdi_name = $BITS::ConceptArtMapPart::is_subclass_cdi_name;

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
#	&cgi_lib::common::message(sprintf("\n%04d:%04d/%02d/%02d %02d:%02d:%02d.%d",__LINE__,$year+1900,$mon+1,$mday,$hour,$min,$sec,$microsec), $LOG);
#	&cgi_lib::common::message(\%ENV, $LOG);
#	&cgi_lib::common::message(\%FORM, $LOG);

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
#$crl_id = 4;	 #part_ofに固定

if(defined $LOG){
#	&cgi_lib::common::message('$md_id='.$md_id, $LOG);
#	&cgi_lib::common::message('$mv_id='.$mv_id, $LOG);
#	&cgi_lib::common::message('$ci_id='.$ci_id, $LOG);
#	&cgi_lib::common::message('$cb_id='.$cb_id, $LOG);
#	&cgi_lib::common::message('$crl_id='.$crl_id, $LOG);
}
$FORM{'ci_id'}=$ci_id;
$FORM{'cb_id'}=$cb_id;
$FORM{'md_id'}=$md_id;
$FORM{'mv_id'}=$mv_id;
$FORM{'crl_id'}=$crl_id;


umask(0);
my $art_abs_path = &catdir($FindBin::Bin,'art_file');
&File::Path::make_path($art_abs_path,{chmod=>0777}) unless(-e $art_abs_path);

#if($FORM{'cmd'} eq 'read' && exists $FORM{'art_id'} && defined $FORM{'art_id'}){
if($FORM{'cmd'} eq 'read'){
	$DATAS = &cmd_read(%FORM);
}
elsif($FORM{'cmd'} eq 'update'){

#	$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8(qq|JSON形式が違います|);
#	&gzip_json($DATAS);
#	exit;

#	&cgi_lib::common::message($FORM{'cmd'}, $LOG) if(defined $LOG);


	my $datas = &cgi_lib::common::decodeJSON($FORM{'datas'});
	if(defined $datas && ref $datas eq 'ARRAY'){
		$dbh->{'AutoCommit'} = 0;
		$dbh->{'RaiseError'} = 1;
		eval{

#			&gzip_json($DATAS);
#			exit;

			my $sth_arti_upd = $dbh->prepare('UPDATE art_file_info SET art_comment=?,art_category=?,art_judge=?,art_class=?,art_modified=now() WHERE art_id=?') or die $dbh->errstr;
			foreach my $data (@$datas){
				next unless(defined $data && ref $data eq 'HASH' && exists $data->{'art_id'} && defined $data->{'art_id'} && length $data->{'art_id'});
				$sth_arti_upd->execute($data->{'arta_comment'},$data->{'arta_category'},$data->{'arta_judge'},$data->{'arta_class'},$data->{'art_id'}) or die $dbh->errstr;
				$sth_arti_upd->finish;
			}
			undef $sth_arti_upd;


			$DATAS->{'success'} = JSON::XS::true;
		};
		if($@){
#			&cgi_lib::common::message($@, $LOG) if(defined $LOG);
			$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8($@);

			$dbh->rollback;
		}
		$dbh->{'AutoCommit'} = 1;
		$dbh->{'RaiseError'} = 0;

	}else{
		$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8(qq|JSON形式が違います|);
	}
}
elsif($FORM{'cmd'} eq 'update_ver2'){
	unless(#0 &&
		exists $FORM{'datas'} && defined $FORM{'datas'}
	){
		$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8(qq|JSON形式が違います|);
		&gzip_json($DATAS);
		exit;
	}
#	&cgi_lib::common::message($FORM{'cmd'}, $LOG) if(defined $LOG);

	#$epocsec = &Time::HiRes::tv_interval($t0);
	#($sec,$min) = localtime($epocsec);
#	&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

	my $datas = &cgi_lib::common::decodeJSON($FORM{'datas'});
	if(defined $datas && ref $datas eq 'ARRAY'){

#print $LOG __LINE__.":",&Data::Dumper::Dumper($datas),"\n";

		$dbh->{'AutoCommit'} = 0;
		$dbh->{'RaiseError'} = 1;
		eval{
			my $sql =<<SQL;
select
 arti.prefix_id,
 arti.art_serial,
 arti.art_name,
 arti.art_ext,
 arti.art_timestamp
from
 art_file_info as arti
where
 arti.art_id=?
SQL
			my $sth_art_sel = $dbh->prepare($sql) or die $dbh->errstr;

			$sql =<<SQL;
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
  art_mirroring,
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
  ?,
  ?
)
;
SQL
			my $sth_art_mirror_ins = $dbh->prepare($sql) or die $dbh->errstr;

#			my $sth_art_mirror_del = $dbh->prepare('DELETE FROM art_file WHERE art_id=?') or die $dbh->errstr;

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
			my $sth_arti_mirror_ins = $dbh->prepare($sql_insert_art_file_info) or die $dbh->errstr;
			my $sth_arti_mirror_upd = $dbh->prepare('UPDATE art_file_info SET art_delcause=NULL,art_modified=now() WHERE art_id=?') or die $dbh->errstr;

			my $sql_update_art_file_info =<<SQL;
UPDATE ONLY
 art_file_info
SET
 art_md5 = art_file.art_md5,
 art_data_size = art_file.art_data_size,
 art_xmin = art_file.art_xmin,
 art_xmax = art_file.art_xmax,
 art_ymin = art_file.art_ymin,
 art_ymax = art_file.art_ymax,
 art_zmin = art_file.art_zmin,
 art_zmax = art_file.art_zmax,
 art_volume = art_file.art_volume,
 art_mirroring = art_file.art_mirroring
FROM
 art_file
WHERE
 art_file_info.art_id = art_file.art_id AND art_file.art_delcause IS NULL;
SQL

			my $sth_arta_sel = $dbh->prepare(qq|select art_comment,art_category,art_judge,art_class from art_file_info where art_id=?|) or die $dbh->errstr;
			my $sth_arta_upd = $dbh->prepare(qq|update art_file_info set art_comment=?,art_category=?,art_judge=?,art_class=?,art_entry=now() where art_id=?|) or die $dbh->errstr;


#			my $sth_map_sel = $dbh->prepare(qq|select cdi_id,cm_comment,cmp_id from concept_art_map where art_id=? and ci_id=?|) or die $dbh->errstr;
#			my $sth_map_upd = $dbh->prepare(qq|update concept_art_map set cdi_id=?,cm_comment=?,cmp_id=?,cm_entry=now(),cm_delcause=null where art_id=? and ci_id=?|) or die $dbh->errstr;
#			my $sth_map_ins = $dbh->prepare(qq|insert into concept_art_map (cdi_id,cm_comment,cmp_id,art_id,ci_id) values (?,?,?,?,?)|) or die $dbh->errstr;
#			my $sth_map_del = $dbh->prepare(qq|delete from concept_art_map where art_id=? and ci_id=?|) or die $dbh->errstr;
			my $sth_map_sel = $dbh->prepare(qq|select cdi_id,cm_comment,cmp_id,cm_use from concept_art_map where art_id=? and md_id=$md_id and mv_id=$mv_id|) or die $dbh->errstr;
#			my $sth_map_upd = $dbh->prepare(qq|update concept_art_map set cdi_id=?,cm_comment=?,cmp_id=?,cm_entry=now(),cm_delcause=null where art_id=? and md_id=$md_id and mv_id=$mv_id|) or die $dbh->errstr;
			my $sth_map_upd = $dbh->prepare(qq|update concept_art_map set cdi_id=?,cm_comment=?,cmp_id=?,cm_use=true,cm_entry=now(),cm_delcause=null where art_id=? and md_id=$md_id and mv_id=$mv_id|) or die $dbh->errstr;
#			my $sth_map_ins = $dbh->prepare(qq|insert into concept_art_map (cdi_id,cm_comment,cmp_id,art_id,ci_id,cb_id,md_id,mv_id) values (?,?,?,?,$ci_id,$cb_id,$md_id,$mv_id)|) or die $dbh->errstr;
			my $sth_map_ins = $dbh->prepare(qq|insert into concept_art_map (cdi_id,cm_comment,cmp_id,art_id,ci_id,md_id,mv_id) values (?,?,?,?,$ci_id,$md_id,$mv_id)|) or die $dbh->errstr;
			my $sth_map_del = $dbh->prepare(qq|delete from concept_art_map where art_id=? and md_id=$md_id and mv_id=$mv_id|) or die $dbh->errstr;


#			my $sth_cdi_sel = $dbh->prepare(qq|select cdi_id from concept_data_info where ci_id=$ci_id AND cdi_name=?|) or die $dbh->errstr;
			my $sth_cdi_sel = $dbh->prepare(qq|select cdi.cdi_id,COALESCE(cd.cd_name,cdi.cdi_name_e) from concept_data_info as cdi left join(select * from concept_data where ci_id=$ci_id AND cb_id=$cb_id) as cd on cdi.cdi_id=cd.cdi_id where cdi.ci_id=$ci_id AND cdi.cdi_name=?|) or die $dbh->errstr;

#			my $sth_artff_sel = $dbh->prepare(qq|select * from art_folder_file where artf_id=? and art_id=?|) or die $dbh->errstr;
			my $sth_artff_sel = $dbh->prepare(qq|select * from art_folder_file where COALESCE(artf_id,0)=? and art_id=?|) or die $dbh->errstr;

#			my $sth_artff_sel = $dbh->prepare(qq|select artf_id from art_folder_file where artf_id is not null and art_id=?|) or die $dbh->errstr;
			my $sth_artff_sel_all = $dbh->prepare(qq|select artf_id from art_folder_file where art_id=?|) or die $dbh->errstr;
			my $sth_artff_ins = $dbh->prepare(qq|insert into art_folder_file (artf_id,art_id) values (?,?)|) or die $dbh->errstr;
			my $sth_artff_sel_folder = $dbh->prepare(qq|select artf_id from art_folder_file where COALESCE(artf_id,0)=COALESCE(?,0) and art_id=?|) or die $dbh->errstr;

			#$epocsec = &Time::HiRes::tv_interval($t0);
			#($sec,$min) = localtime($epocsec);
#			&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

#			my $old_cm_modified = &BITS::ConceptArtMapModified::exec(
#				dbh => $dbh,
#				md_id => $md_id,
#				mv_id => $mv_id,
#				ci_id => $ci_id,
#				cb_id => $cb_id,
#				use_only_map_terms=>&BITS::Config::USE_ONLY_MAP_TERMS(),
#				LOG => $LOG
#			);

			my $sth_cmp_abbr_sel = $dbh->prepare(qq|select cmp_abbr from concept_art_map_part where cmp_id=?|) or die $dbh->errstr;
			my $sth_cmp_id_sel = $dbh->prepare(qq|select cmp_id from concept_art_map_part where cmp_abbr=?|) or die $dbh->errstr;
			my $column_number;

			my @MAKE_ART_IMAGES;

			foreach my $data (@$datas){
				my $art_id = (exists $data->{'art_id'} && defined $data->{'art_id'}) ? $data->{'art_id'} : undef;
				next unless(defined $art_id);

				my %merge_data = %{ &Hash::Merge::merge( $data, \%FORM ) };
#				&cgi_lib::common::message(\%merge_data, $LOG) if(defined $LOG);
				&BITS::ConceptArtMapPart::create_subclass(%merge_data);

				if($data->{'cmp_id'} && $data->{'cdi_name'} !~ /$is_subclass_cdi_name/){
					my $cmp_abbr;
					$sth_cmp_abbr_sel->execute($data->{'cmp_id'}) or die $dbh->errstr;
					if($sth_cmp_abbr_sel->rows()>0){
						$column_number = 0;
						$sth_cmp_abbr_sel->bind_col(++$column_number, \$cmp_abbr, undef);
						$sth_cmp_abbr_sel->fetch;
					}
					$sth_cmp_abbr_sel->finish;
					if(defined $cmp_abbr && length $cmp_abbr){
						$data->{'cdi_name'} = sprintf('%s-%s',$data->{'cdi_name'},$cmp_abbr);
						$data->{'cmp_id'} = 0;
					}
				}

				my $cdi_id;
				my $cdi_name_e;
				if(exists $data->{'cdi_name'} && defined $data->{'cdi_name'}){
					$sth_cdi_sel->execute($data->{'cdi_name'}) or die $dbh->errstr;
					my $column_number = 0;
					$sth_cdi_sel->bind_col(++$column_number, \$cdi_id, undef);
					$sth_cdi_sel->bind_col(++$column_number, \$cdi_name_e, undef);
					$sth_cdi_sel->fetch;
					$sth_cdi_sel->finish;
				}

				$sth_arta_sel->execute($art_id) or die $dbh->errstr;
				my $rows = $sth_arta_sel->rows();
				my($arta_comment,$arta_category,$arta_judge,$arta_class);
				if($rows>0){
					my $column_number = 0;
					$sth_arta_sel->bind_col(++$column_number, \$arta_comment, undef);
					$sth_arta_sel->bind_col(++$column_number, \$arta_category, undef);
					$sth_arta_sel->bind_col(++$column_number, \$arta_judge, undef);
					$sth_arta_sel->bind_col(++$column_number, \$arta_class, undef);
					$sth_arta_sel->fetch;
				}
				$sth_arta_sel->finish;
				print $LOG __LINE__.qq|:\$rows=[$rows]\n|;
#				next unless($rows>0);
				unless(
					defined $arta_comment && exists $data->{'arta_comment'} && defined $data->{'arta_comment'} && $data->{'arta_comment'} eq $arta_comment &&
					defined $arta_category && exists $data->{'arta_category'} && defined $data->{'arta_category'} && $data->{'arta_category'} eq $arta_category &&
					defined $arta_judge && exists $data->{'arta_judge'} && defined $data->{'arta_judge'} && $data->{'arta_judge'} eq $arta_judge &&
					defined $arta_class && exists $data->{'arta_class'} && defined $data->{'arta_class'} && $data->{'arta_class'} eq $arta_class
				){
					$arta_comment = $data->{'arta_comment'}   unless(defined $arta_comment && exists $data->{'arta_comment'} && defined $data->{'arta_comment'} && $data->{'arta_comment'} eq $arta_comment);
					$arta_category = $data->{'arta_category'} unless(defined $arta_category && exists $data->{'arta_category'} && defined $data->{'arta_category'} && $data->{'arta_category'} eq $arta_category);
					$arta_judge = $data->{'arta_judge'}       unless(defined $arta_judge && exists $data->{'arta_judge'} && defined $data->{'arta_judge'} && $data->{'arta_judge'} eq $arta_judge);
					$arta_class = $data->{'arta_class'}       unless(defined $arta_class && exists $data->{'arta_class'} && defined $data->{'arta_class'} && $data->{'arta_class'} eq $arta_class);
					if($rows>0){
						$sth_arta_upd->execute($arta_comment,$arta_category,$arta_judge,$arta_class,$art_id) or die $dbh->errstr;
						my $rows = $sth_arta_upd->rows();
						$sth_arta_upd->finish;
						print $LOG __LINE__.qq|:\$rows=[$rows]\n|;
					}else{
						die 'INSERT ??';
#						$sth_arta_ins->execute($arta_comment,$arta_category,$arta_judge,$arta_class,$art_id) or die $dbh->errstr;
#						my $rows = $sth_arta_ins->rows();
#						$sth_arta_ins->finish;
#						print $LOG __LINE__.qq|:\$rows=[$rows]\n|;
					}
				}

				$sth_map_sel->execute($art_id) or die $dbh->errstr;
				$rows = $sth_map_sel->rows();
				print $LOG __LINE__.qq|:\$rows=[$rows]\n|;
				my($map_cdi_id,$cm_comment,$cmp_id,$cm_use);
				if($rows>0){
					my $column_number = 0;
					$sth_map_sel->bind_col(++$column_number, \$map_cdi_id, undef);
					$sth_map_sel->bind_col(++$column_number, \$cm_comment, undef);
					$sth_map_sel->bind_col(++$column_number, \$cmp_id, undef);
					$sth_map_sel->bind_col(++$column_number, \$cm_use, undef);
					$sth_map_sel->fetch;
				}
				$sth_map_sel->finish;

				if(defined $cmp_id){
					$cmp_id -= 0;
				}else{
					$cmp_id = 0;
				}
				if(exists $data->{'cmp_id'} && defined $data->{'cmp_id'}){
					$data->{'cmp_id'} -= 0;
				}else{
					$data->{'cmp_id'} = 0;
				}

				if(defined $cm_use){
					$cm_use -= 0;
				}else{
					$cm_use = 0;
				}

				unless(
					defined $map_cdi_id &&
					defined $cdi_id &&
					$map_cdi_id eq $cdi_id &&
					defined $cm_comment && exists $data->{'cm_comment'} && defined $data->{'cm_comment'} && $cm_comment eq $data->{'cm_comment'} &&
					$cmp_id == $data->{'cmp_id'} &&
					$cm_use == 1
				){
					if($rows>0){
						if(defined $cdi_id){
							$sth_map_upd->execute($cdi_id,$data->{'cm_comment'},$data->{'cmp_id'},$art_id,) or die $dbh->errstr;
							$sth_map_upd->finish;
						}else{
							$sth_map_del->execute($art_id) or die $dbh->errstr;
							$sth_map_del->finish;
						}
					}elsif(defined $cdi_id){
						$sth_map_ins->execute($cdi_id,$data->{'cm_comment'},$data->{'cmp_id'},$art_id) or die $dbh->errstr;
						$sth_map_ins->finish;
					}

					if(defined $cdi_id){

						if($data->{'cdi_name'} =~ /$is_subclass_cdi_name/){
							$data->{'cdi_name'} = $1;
							my $cmp_abbr = $2;
							$sth_cmp_id_sel->execute($cmp_abbr) or die $dbh->errstr;
							my $cmp_rows = $sth_cmp_id_sel->rows();
							my $hash_cmp;
							$hash_cmp = $sth_cmp_id_sel->fetchrow_hashref if($cmp_rows>0);
							$sth_cmp_id_sel->finish;
							$cmp_id = $hash_cmp->{'cmp_id'} if(defined $hash_cmp && ref $hash_cmp eq 'HASH' && exists $hash_cmp->{'cmp_id'} && defined $hash_cmp->{'cmp_id'});
						}

						push(@{$DATAS->{'datas'}},{
							art_id        => $art_id,
							cdi_id        => $cdi_id - 0,
							cdi_name      => $data->{'cdi_name'},
							cdi_name_e    => $cdi_name_e,
							cmp_id        => $cmp_id - 0,
							cm_use        => JSON::XS::true,
							never_current => JSON::XS::false
						});
					}
				}

				if(exists $data->{'mirror'} && defined $data->{'mirror'} && $data->{'mirror'}){
					my $mirror_art_id = (exists $data->{'mirror_art_id'} && defined $data->{'mirror_art_id'} && length $data->{'mirror_art_id'} ? $data->{'mirror_art_id'} : undef);
					my $art_mirroring;
					if(defined $mirror_art_id && length $mirror_art_id){
						if($mirror_art_id =~ /^([A-Z]+[0-9]+)$/){
							$art_mirroring = 'false';
						}elsif($mirror_art_id =~ /^([A-Z]+[0-9]+)M$/){
							$art_mirroring = 'true';
						}
					}else{
						if($art_id =~ /^([A-Z]+[0-9]+)$/){
							$mirror_art_id = $1.'M';
							$art_mirroring = 'true';
						}elsif($art_id =~ /^([A-Z]+[0-9]+)M$/){
							$mirror_art_id = $1;
							$art_mirroring = 'false';
						}
					}
					if(defined $mirror_art_id && $mirror_art_id eq $art_id){
						undef $mirror_art_id;
					}
					if(defined $mirror_art_id){
						$sth_art_sel->execute($mirror_art_id) or die $dbh->errstr;
						my $mirror_rows = $sth_art_sel->rows();
						$sth_art_sel->finish;
						unless($mirror_rows>0){
							$sth_art_sel->execute($art_id) or die $dbh->errstr;
							my $rows = $sth_art_sel->rows();
							my($prefix_id,$art_serial,$art_name,$art_ext,$art_timestamp);
							if($rows>0){
								my $column_number = 0;
								$sth_art_sel->bind_col(++$column_number, \$prefix_id, undef);
								$sth_art_sel->bind_col(++$column_number, \$art_serial, undef);
								$sth_art_sel->bind_col(++$column_number, \$art_name, undef);
								$sth_art_sel->bind_col(++$column_number, \$art_ext, undef);
								$sth_art_sel->bind_col(++$column_number, \$art_timestamp, undef);
								$sth_art_sel->fetch;
							}
							$sth_art_sel->finish;
							if(defined $art_ext){
								my $org_file_path = &catfile($art_abs_path,qq|$art_id$art_ext|);
								my $mir_file_prefix = &catfile($art_abs_path,$mirror_art_id);
								my $mir_file_path = qq|$mir_file_prefix$art_ext|;
								my $mir_prop = &BITS::VTK::reflection($org_file_path,$mir_file_prefix);
								die __LINE__.qq|:ERROR: reflection()[$mir_file_path]| unless(defined $mir_prop && ref $mir_prop eq 'HASH' && ref $mir_prop->{'bounds'} eq 'ARRAY');

								my $art_xmin = $mir_prop->{'bounds'}->[0] - 0;
								my $art_xmax = $mir_prop->{'bounds'}->[1] - 0;
								my $art_ymin = $mir_prop->{'bounds'}->[2] - 0;
								my $art_ymax = $mir_prop->{'bounds'}->[3] - 0;
								my $art_zmin = $mir_prop->{'bounds'}->[4] - 0;
								my $art_zmax = $mir_prop->{'bounds'}->[5] - 0;
								my $art_volume = defined $mir_prop->{'volume'} && $mir_prop->{'volume'} > 0 ?  &Truncated($mir_prop->{'volume'} / 1000) : 0;
								my $art_cube_volume = &Truncated(($art_xmax-$art_xmin)*($art_ymax-$art_ymin)*($art_zmax-$art_zmin)/1000);

								if(-e $mir_file_path && -s $mir_file_path){
									my $art_data = &readObjFile($mir_file_path);
									my $art_data_size = length($art_data);
									if($art_data_size>0){
										my $art_md5 = &Digest::MD5::md5_hex($art_data);
										my $art_raw_data = &readFile($mir_file_path);
										my $art_raw_data_size = length($art_raw_data);

#										$sth_art_mirror_del->execute($mirror_art_id) or die $dbh->errstr;
#										$sth_art_mirror_del->finish();

										my $param_num = 0;
										$sth_art_mirror_ins->bind_param(++$param_num, $prefix_id);
										$sth_art_mirror_ins->bind_param(++$param_num, $mirror_art_id);
										$sth_art_mirror_ins->bind_param(++$param_num, $art_serial);
										$sth_art_mirror_ins->bind_param(++$param_num, $art_name);
										$sth_art_mirror_ins->bind_param(++$param_num, $art_ext);
										$sth_art_mirror_ins->bind_param(++$param_num, $art_timestamp);
										$sth_art_mirror_ins->bind_param(++$param_num, $art_md5);
										$sth_art_mirror_ins->bind_param(++$param_num, $art_data, { pg_type => DBD::Pg::PG_BYTEA });
										$sth_art_mirror_ins->bind_param(++$param_num, $art_data_size);
										$sth_art_mirror_ins->bind_param(++$param_num, $art_xmin);
										$sth_art_mirror_ins->bind_param(++$param_num, $art_xmax);
										$sth_art_mirror_ins->bind_param(++$param_num, $art_ymin);
										$sth_art_mirror_ins->bind_param(++$param_num, $art_ymax);
										$sth_art_mirror_ins->bind_param(++$param_num, $art_zmin);
										$sth_art_mirror_ins->bind_param(++$param_num, $art_zmax);
										$sth_art_mirror_ins->bind_param(++$param_num, $art_volume);
										$sth_art_mirror_ins->bind_param(++$param_num, $art_mirroring);
										$sth_art_mirror_ins->bind_param(++$param_num, $art_raw_data, { pg_type => DBD::Pg::PG_BYTEA });
										$sth_art_mirror_ins->bind_param(++$param_num, $art_raw_data_size);
										$sth_art_mirror_ins->execute() or die $dbh->errstr;
										$mirror_rows = $sth_art_mirror_ins->rows();
										$sth_art_mirror_ins->finish();

#										&cgi_lib::common::message($mirror_rows, $LOG) if(defined $LOG);
#										&cgi_lib::common::message($mirror_art_id, $LOG) if(defined $LOG);

#										$dbh->do($sql_insert_art_file_info) or die $dbh->errstr;
#										$dbh->do($sql_update_art_file_info) or die $dbh->errstr;

										$sth_arti_mirror_ins->execute($mirror_art_id) or die $dbh->errstr;
										$sth_arti_mirror_ins->finish();

										&BITS::Voxel::insVoxelData($dbh,$mirror_art_id,$art_data);

#										&make_art_image($mirror_art_id);
										push(@MAKE_ART_IMAGES, $mirror_art_id);
									}
								}

							}
						}else{
							$sth_arti_mirror_upd->execute($mirror_art_id) or die $dbh->errstr;
							$sth_arti_mirror_upd->finish;
						}
						if($mirror_rows>0){

							$sth_arta_sel->execute($mirror_art_id) or die $dbh->errstr;
							my $rows = $sth_arta_sel->rows();
							my($arta_comment,$arta_category,$arta_judge,$arta_class);
							if($rows>0){
								my $column_number = 0;
								$sth_arta_sel->bind_col(++$column_number, \$arta_comment, undef);
								$sth_arta_sel->bind_col(++$column_number, \$arta_category, undef);
								$sth_arta_sel->bind_col(++$column_number, \$arta_judge, undef);
								$sth_arta_sel->bind_col(++$column_number, \$arta_class, undef);
								$sth_arta_sel->fetch;
							}
							$sth_arta_sel->finish;
							$arta_comment = '' unless(defined $arta_comment);
							$arta_category = '' unless(defined $arta_category);
							$arta_judge = '' unless(defined $arta_judge);
							$arta_class = '' unless(defined $arta_class);

							$data->{'arta_comment'} = '' unless(exists $data->{'arta_comment'} && defined $data->{'arta_comment'});
							$data->{'arta_category'} = '' unless(exists $data->{'arta_category'} && defined $data->{'arta_category'});
							$data->{'arta_judge'} = '' unless(exists $data->{'arta_judge'} && defined $data->{'arta_judge'});
							$data->{'arta_class'} = '' unless(exists $data->{'arta_class'} && defined $data->{'arta_class'});

							unless(
								$data->{'arta_comment'} eq $arta_comment &&
								$data->{'arta_category'} eq $arta_category &&
								$data->{'arta_judge'} eq $arta_judge &&
								$data->{'arta_class'} eq $arta_class
							){
								$arta_comment = $data->{'arta_comment'} unless($data->{'arta_comment'} eq $arta_comment);
								$arta_category = $data->{'arta_category'} unless($data->{'arta_category'} eq $arta_category);
								$arta_judge = $data->{'arta_judge'} unless($data->{'arta_judge'} eq $arta_judge);
								$arta_class = $data->{'arta_class'} unless($data->{'arta_class'} eq $arta_class);
								if($rows>0){
									$sth_arta_upd->execute($arta_comment,$arta_category,$arta_judge,$arta_class,$mirror_art_id) or die $dbh->errstr;
									$sth_arta_upd->finish;
								}else{
									die 'INSERT ??';
#									$sth_arta_ins->execute($arta_comment,$arta_category,$arta_judge,$arta_class,$mirror_art_id) or die $dbh->errstr;
#									$sth_arta_ins->finish;
								}
							}

#							if(exists $data->{'mirror_same_concept'} && defined $data->{'mirror_same_concept'} || exists $data->{'mirror_cdi_name'} && defined $data->{'mirror_cdi_name'}){
							if(
								(exists $data->{'mirror_type'} && defined $data->{'mirror_type'} && $data->{'mirror_type'} ne ''     && exists $data->{'mirror_cdi_name'} && defined $data->{'mirror_cdi_name'} && length $data->{'mirror_cdi_name'}) ||
								(exists $data->{'mirror_type'} && defined $data->{'mirror_type'} && $data->{'mirror_type'} eq 'same' && defined $cdi_id && length $cdi_id)
							){

								my $mirror_cdi_id;
								my $mirror_cdi_name_e;
								my $mirror_cm_comment = $data->{'cm_comment'};
								my $mirror_cmp_id = $data->{'cmp_id'};
#								if(defined $data->{'mirror_same_concept'} && $data->{'mirror_same_concept'} && defined $cdi_id && length $cdi_id){
								if($data->{'mirror_type'} eq 'same'){
									$mirror_cdi_id = $cdi_id;
									$mirror_cdi_name_e = $cdi_name_e;
								}
#								elsif(defined $data->{'mirror_cdi_name'} && length $data->{'mirror_cdi_name'}){
								else{

									&BITS::ConceptArtMapPart::create_subclass(%merge_data, cdi_name => $data->{'mirror_cdi_name'}, cmp_id => $data->{'mirror_cmp_id'});

									if($data->{'mirror_cmp_id'} && $data->{'mirror_cdi_name'} !~ /$is_subclass_cdi_name/){
										my $cmp_abbr;
										$sth_cmp_abbr_sel->execute($data->{'mirror_cmp_id'}) or die $dbh->errstr;
										if($sth_cmp_abbr_sel->rows()>0){
											$column_number = 0;
											$sth_cmp_abbr_sel->bind_col(++$column_number, \$cmp_abbr, undef);
											$sth_cmp_abbr_sel->fetch;
										}
										$sth_cmp_abbr_sel->finish;
										if(defined $cmp_abbr && length $cmp_abbr){
											$data->{'mirror_cdi_name'} = sprintf('%s-%s',$data->{'mirror_cdi_name'},$cmp_abbr);
											$data->{'mirror_cmp_id'} = 0;
										}
									}
									$mirror_cmp_id = $data->{'mirror_cmp_id'};

									$sth_cdi_sel->execute($data->{'mirror_cdi_name'}) or die $dbh->errstr;
									my $column_number = 0;
									$sth_cdi_sel->bind_col(++$column_number, \$mirror_cdi_id, undef);
									$sth_cdi_sel->bind_col(++$column_number, \$mirror_cdi_name_e, undef);
									$sth_cdi_sel->fetch;
									$sth_cdi_sel->finish;

								}

								$sth_map_sel->execute($mirror_art_id) or die $dbh->errstr;
								my $rows = $sth_map_sel->rows();
								my($map_cdi_id,$cm_comment,$cmp_id,$cm_use);
								if($rows>0){
									my $column_number = 0;
									$sth_map_sel->bind_col(++$column_number, \$map_cdi_id, undef);
									$sth_map_sel->bind_col(++$column_number, \$cm_comment, undef);
									$sth_map_sel->bind_col(++$column_number, \$cmp_id, undef);
									$sth_map_sel->bind_col(++$column_number, \$cm_use, undef);
									$sth_map_sel->fetch;
								}
								$sth_map_sel->finish;

								if(defined $cmp_id){
									$cmp_id -= 0;
								}else{
									$cmp_id = 0;
								}
								if(defined $cm_use){
									$cm_use -= 0;
								}else{
									$cm_use = 0;
								}

								$map_cdi_id = '' unless(defined $map_cdi_id);
								unless(
									$map_cdi_id eq $mirror_cdi_id &&
									$cm_comment eq $mirror_cm_comment &&
									$cmp_id     == $mirror_cmp_id &&
									$cm_use     == 1
								){
									if($rows>0){
										if(defined $mirror_cdi_id){
											$sth_map_upd->execute($mirror_cdi_id,$mirror_cm_comment,$mirror_cmp_id,$mirror_art_id) or die $dbh->errstr;
											$sth_map_upd->finish;
										}else{
											$sth_map_del->execute($mirror_art_id,$ci_id) or die $dbh->errstr;
											$sth_map_del->finish;
										}
									}elsif(defined $mirror_cdi_id){
										$sth_map_ins->execute($mirror_cdi_id,$mirror_cm_comment,$mirror_cmp_id,$mirror_art_id) or die $dbh->errstr;
										$sth_map_ins->finish;
									}

									if(defined $mirror_cdi_id){

										if($data->{'mirror_cdi_name'} =~ /$is_subclass_cdi_name/){
											$data->{'mirror_cdi_name'} = $1;
											my $cmp_abbr = $2;
											$sth_cmp_id_sel->execute($cmp_abbr) or die $dbh->errstr;
											my $cmp_rows = $sth_cmp_id_sel->rows();
											my $hash_cmp;
											$hash_cmp = $sth_cmp_id_sel->fetchrow_hashref if($cmp_rows>0);
											$sth_cmp_id_sel->finish;
											$cmp_id = $hash_cmp->{'cmp_id'} if(defined $hash_cmp && ref $hash_cmp eq 'HASH' && exists $hash_cmp->{'cmp_id'} && defined $hash_cmp->{'cmp_id'});
										}

										push(@{$DATAS->{'datas'}},{
											art_id        => $art_id,
											cdi_id        => $mirror_cdi_id - 0,
											cdi_name      => $data->{'mirror_cdi_name'},
											cdi_name_e    => $mirror_cdi_name_e,
											cmp_id        => $cmp_id - 0,
											cm_use        => JSON::XS::true,
											never_current => JSON::XS::false
										});
									}

								}
							}
=pod
							$sth_artff_sel->execute($data->{'artf_id'},$mirror_art_id) or die $dbh->errstr;
							my $rows_artff_sel = $sth_artff_sel->rows();
							$sth_artff_sel->finish;
							unless($rows_artff_sel>0){
								$sth_artff_ins->execute($data->{'artf_id'} ? $data->{'artf_id'} : undef,$mirror_art_id) or die $dbh->errstr;
								$sth_artff_ins->finish;
							}
=cut

							my $column_number = 0;
							my $mirror_artf_id;
							my $rows_artff_sel_folder;
							$sth_artff_sel_all->execute($art_id) or die $dbh->errstr;
							$sth_artff_sel_all->bind_col(++$column_number, \$mirror_artf_id, undef);
							while($sth_artff_sel_all->fetch){
								$sth_artff_sel_folder->execute($mirror_artf_id,$mirror_art_id) or die $dbh->errstr;
								$rows_artff_sel_folder = $sth_artff_sel_folder->rows();
								$sth_artff_sel_folder->finish;
								next if($rows_artff_sel_folder>0);

								$sth_artff_ins->execute($mirror_artf_id,$mirror_art_id) or die $dbh->errstr;
								$sth_artff_ins->finish;
							}
							$sth_artff_sel_all->finish;



						}
					}
				}
			}
			undef $sth_arta_sel;

			#$epocsec = &Time::HiRes::tv_interval($t0);
			#($sec,$min) = localtime($epocsec);
#			&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

#			my $new_cm_modified = &BITS::ConceptArtMapModified::exec(
#				dbh => $dbh,
#				md_id => $md_id,
#				mv_id => $mv_id,
#				ci_id => $ci_id,
#				cb_id => $cb_id,
#				use_only_map_terms=>&BITS::Config::USE_ONLY_MAP_TERMS(),
#				LOG => $LOG
#			);
#			my $diff_cm_modified = &BITS::ConceptArtMapModified::diff($new_cm_modified,$old_cm_modified);
#			if(defined $diff_cm_modified){
#				&cgi_lib::common::message($diff_cm_modified, $LOG) if(defined $LOG);
#			}


#			$dbh->rollback;
			$dbh->commit();
			$dbh->do("NOTIFY art_file");
			$dbh->do("NOTIFY concept_art_map");

			$DATAS->{'success'} = JSON::XS::true;
			$DATAS->{'total'} = scalar @{$DATAS->{'datas'}};

			&make_art_image(\@MAKE_ART_IMAGES) if(scalar @MAKE_ART_IMAGES);
			&recreate_subclass(%FORM, LOG => $LOG);
		};
		if($@){
#			&cgi_lib::common::message($@, $LOG);
			$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8($@);
			$dbh->rollback;
		}
		$dbh->{'AutoCommit'} = 1;
		$dbh->{'RaiseError'} = 0;

	}else{
		$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8(qq|JSON形式が違います|);
	}
}

elsif($FORM{'cmd'} eq 'update_concept_art_map'){
	unless(
		exists $FORM{'datas'} && defined $FORM{'datas'}
	){
		$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8(qq|JSON形式が違います|);
		&gzip_json($DATAS);
		exit;
	}
	my $datas = &cgi_lib::common::decodeJSON($FORM{'datas'});
	if(defined $datas && ref $datas eq 'ARRAY'){
		$dbh->{'AutoCommit'} = 0;
		$dbh->{'RaiseError'} = 1;
		eval{
#			my $sth_map_sel = $dbh->prepare(qq|select cdi_id from concept_art_map where art_id=? and ci_id=$ci_id|) or die $dbh->errstr;
#			my $sth_map_ins = $dbh->prepare(qq|insert into concept_art_map (cdi_id,cmp_id,art_id,ci_id) values (?,?,?,$ci_id)|) or die $dbh->errstr;
#			my $sth_map_upd = $dbh->prepare(qq|update concept_art_map set cdi_id=?,cmp_id=?,cm_delcause=null,cm_entry=now() where art_id=? and ci_id=$ci_id|) or die $dbh->errstr;
#			my $sth_map_del = $dbh->prepare(qq|delete from concept_art_map where art_id=? and ci_id=$ci_id|) or die $dbh->errstr;

			my $sth_map_sel = $dbh->prepare(qq|select cdi_id from concept_art_map where art_id=? and md_id=$md_id and mv_id=$mv_id|) or die $dbh->errstr;
#			my $sth_map_ins = $dbh->prepare(qq|insert into concept_art_map (cdi_id,cmp_id,art_id,ci_id,cb_id,md_id,mv_id) values (?,?,?,$ci_id,$cb_id,$md_id,$mv_id)|) or die $dbh->errstr;
			my $sth_map_ins = $dbh->prepare(qq|insert into concept_art_map (cdi_id,cmp_id,art_id,ci_id,md_id,mv_id) values (?,?,?,$ci_id,$md_id,$mv_id)|) or die $dbh->errstr;
#			my $sth_map_upd = $dbh->prepare(qq|update concept_art_map set cdi_id=?,cmp_id=?,cm_delcause=null,cm_entry=now() where art_id=? and md_id=$md_id and mv_id=$mv_id|) or die $dbh->errstr;
			my $sth_map_upd = $dbh->prepare(qq|update concept_art_map set cdi_id=?,cmp_id=?,cm_use=?,cm_delcause=null,cm_entry=now() where art_id=? and md_id=$md_id and mv_id=$mv_id|) or die $dbh->errstr;
			my $sth_map_del = $dbh->prepare(qq|delete from concept_art_map where art_id=? and md_id=$md_id and mv_id=$mv_id|) or die $dbh->errstr;

			my $sth_cdi_sel = $dbh->prepare(qq|select cdi.cdi_id,COALESCE(cd.cd_name,cdi.cdi_name_e) from concept_data_info as cdi left join(select * from concept_data where ci_id=$ci_id AND cb_id=$cb_id) as cd on cdi.cdi_id=cd.cdi_id where cdi.ci_id=$ci_id AND cdi.cdi_name=?|) or die $dbh->errstr;

			my $sth_cdi_sel_mirror = $dbh->prepare(qq|select cdi.cdi_id,cdi.cdi_name,COALESCE(cd.cd_name,cdi.cdi_name_e) from concept_data_info as cdi left join(select * from concept_data where ci_id=$ci_id AND cb_id=$cb_id) as cd on cdi.cdi_id=cd.cdi_id where cdi.ci_id=$ci_id AND lower(COALESCE(cd.cd_name,cdi.cdi_name_e))=?|) or die $dbh->errstr;

			my $sth_map_cdi_sel = $dbh->prepare(qq|select art_id from concept_art_map where cdi_id=? and md_id=$md_id and mv_id=$mv_id|) or die $dbh->errstr;
			my $sth_map_exists_sel = $dbh->prepare(qq|select art_id from concept_art_map where cdi_id=? and cmp_id=? and cm_use=? and art_id=? and md_id=$md_id and mv_id=$mv_id|) or die $dbh->errstr;


			my $sql_art_sel =<<SQL;
select
 art.prefix_id,
 art.art_serial,
 art.art_name,
 art.art_ext,
 art.art_timestamp
from
 art_file as art
where
 art.art_id=?
SQL
			my $sth_art_sel = $dbh->prepare($sql_art_sel) or die $dbh->errstr;

			my $sql_art_mirror_ins =<<SQL;
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
  art_mirroring,
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
  ?,
  ?
)
;
SQL
			my $sth_art_mirror_ins = $dbh->prepare($sql_art_mirror_ins) or die $dbh->errstr;

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
			my $sth_arti_mirror_ins = $dbh->prepare($sql_insert_art_file_info) or die $dbh->errstr;
			my $sth_arti_mirror_upd = $dbh->prepare('UPDATE art_file_info SET art_delcause=NULL,art_modified=now() WHERE art_id=?') or die $dbh->errstr;

			my $sth_artff_sel = $dbh->prepare(qq|select artf_id from art_folder_file where artf_id is not null and art_id=?|) or die $dbh->errstr;
			my $sth_artff_sel_all = $dbh->prepare(qq|select artf_id from art_folder_file where art_id=?|) or die $dbh->errstr;
			my $sth_artff_ins = $dbh->prepare(qq|insert into art_folder_file (artf_id,art_id) values (?,?)|) or die $dbh->errstr;
			my $sth_artff_sel_folder = $dbh->prepare(qq|select artf_id from art_folder_file where COALESCE(artf_id,0)=COALESCE(?,0) and art_id=?|) or die $dbh->errstr;

			my $sth_cmp_abbr_sel = $dbh->prepare(qq|select cmp_abbr from concept_art_map_part where cmp_id=?|) or die $dbh->errstr;
			my $sth_cmp_id_sel = $dbh->prepare(qq|select cmp_id from concept_art_map_part where cmp_abbr=?|) or die $dbh->errstr;

#			my $old_cm_modified = &BITS::ConceptArtMapModified::exec(
#				dbh => $dbh,
#				md_id => $md_id,
#				mv_id => $mv_id,
#				ci_id => $ci_id,
#				cb_id => $cb_id,
#				use_only_map_terms=>&BITS::Config::USE_ONLY_MAP_TERMS(),
#				LOG => $LOG
#			);

			my $column_number;

			if(exists $FORM{'cmd_mode'} && defined $FORM{'cmd_mode'} && $FORM{'cmd_mode'} eq 'replace'){#指定されたOBJで対応を入れ替える為、既存の使用しないデータは削除する
#				&cgi_lib::common::message('', $LOG) if(defined $LOG);
				my $cdi_name;
				foreach my $data (@$datas){
					$cdi_name = (exists $data->{'cdi_name'} && defined $data->{'cdi_name'} && length $data->{'cdi_name'}) ? $data->{'cdi_name'} : undef;
					next unless(defined $cdi_name);
				}
				my $cdi_id;
				if(defined $cdi_name && length $cdi_name){
					$sth_cdi_sel->execute($cdi_name) or die $dbh->errstr;
					$column_number = 0;
					$sth_cdi_sel->bind_col(++$column_number, \$cdi_id, undef);
					$sth_cdi_sel->fetch;
					$sth_cdi_sel->finish;
				}
				if(defined $cdi_id){
					my %ART_IDS;
					my $art_id;
					$sth_map_cdi_sel->execute($cdi_id) or die $dbh->errstr;
					$column_number = 0;
					$sth_map_cdi_sel->bind_col(++$column_number, \$art_id, undef);
					while($sth_map_cdi_sel->fetch){
						$ART_IDS{$art_id} = undef;
					}
					$sth_map_cdi_sel->finish;

					foreach my $data (@$datas){
						my $art_id = (exists $data->{'art_id'} && defined $data->{'art_id'}) ? $data->{'art_id'} : undef;
						next unless(defined $art_id);
						delete $ART_IDS{$art_id} if(exists $ART_IDS{$art_id});
					}
#					&cgi_lib::common::message([keys(%ART_IDS)], $LOG) if(defined $LOG);
					if(scalar keys(%ART_IDS)){
						foreach my $art_id (keys(%ART_IDS)){
							$sth_map_del->execute($art_id) or die $dbh->errstr;
							$sth_map_del->finish;
						}
					}
					undef %ART_IDS;
				}
			}

			my @MAKE_ART_IMAGES;

			foreach my $data (@$datas){
#				&cgi_lib::common::message($data, $LOG) if(defined $LOG);
				my $art_id = (exists $data->{'art_id'} && defined $data->{'art_id'}) ? $data->{'art_id'} : undef;
				next unless(defined $art_id);

				my %merge_data = %{ &Hash::Merge::merge( $data, \%FORM ) };
#				&cgi_lib::common::message(\%merge_data, $LOG) if(defined $LOG);
				&BITS::ConceptArtMapPart::create_subclass(%merge_data, dbh => $dbh, LOG => $LOG);

				if($data->{'cmp_id'} && $data->{'cdi_name'} !~ /$is_subclass_cdi_name/){
					my $cmp_abbr;
					$sth_cmp_abbr_sel->execute($data->{'cmp_id'}) or die $dbh->errstr;
					if($sth_cmp_abbr_sel->rows()>0){
						$column_number = 0;
						$sth_cmp_abbr_sel->bind_col(++$column_number, \$cmp_abbr, undef);
						$sth_cmp_abbr_sel->fetch;
					}
					$sth_cmp_abbr_sel->finish;
					if(defined $cmp_abbr && length $cmp_abbr){
						$data->{'cdi_name'} = sprintf('%s-%s',$data->{'cdi_name'},$cmp_abbr);
						$data->{'cmp_id'} = 0;
					}
				}

				my $cdi_name = (exists $data->{'cdi_name'} && defined $data->{'cdi_name'} && length $data->{'cdi_name'}) ? $data->{'cdi_name'} : undef;
				my $cmp_id = (exists $data->{'cmp_id'} && defined $data->{'cmp_id'}) ? $data->{'cmp_id'}-0 : 0;

#				&cgi_lib::common::message($cdi_name, $LOG) if(defined $LOG);
#				&cgi_lib::common::message($cmp_id, $LOG) if(defined $LOG);

				my $cdi_id;
				my $cdi_name_e;
#				if(defined $cdi_name && length $cdi_name && exists $data->{'cm_use'} && defined $data->{'cm_use'} && $data->{'cm_use'}){
				if(defined $cdi_name && length $cdi_name){
					$sth_cdi_sel->execute($cdi_name) or die $dbh->errstr;
					$column_number = 0;
					$sth_cdi_sel->bind_col(++$column_number, \$cdi_id, undef);
					$sth_cdi_sel->bind_col(++$column_number, \$cdi_name_e, undef);
					$sth_cdi_sel->fetch;
					$sth_cdi_sel->finish;
				}
				my $cm_use = 0;
				if(exists $data->{'never_current'} && defined $data->{'never_current'} && $data->{'never_current'}){
					$cm_use = 0;
				}else{
					$cm_use = 1;# if(exists $data->{'cm_use'} && defined $data->{'cm_use'} && $data->{'cm_use'});
				}

#				&cgi_lib::common::message($cdi_id, $LOG) if(defined $LOG);
#				&cgi_lib::common::message($cdi_name_e, $LOG) if(defined $LOG);
#				&cgi_lib::common::message($cm_use, $LOG) if(defined $LOG);

				$sth_map_sel->execute($art_id) or die $dbh->errstr;
				my $sel_rows = $sth_map_sel->rows();
				$sth_map_sel->finish;

#				&cgi_lib::common::message($sel_rows, $LOG) if(defined $LOG);

				if(defined $cdi_id){
					if($sel_rows>0){
#						$sth_map_exists_sel->execute($cdi_id,$cmp_id,$art_id) or die $dbh->errstr;
						$sth_map_exists_sel->execute($cdi_id,$cmp_id,$cm_use,$art_id) or die $dbh->errstr;
						$sel_rows = $sth_map_exists_sel->rows();
						$sth_map_exists_sel->finish;
						unless($sel_rows>0){
#							$sth_map_upd->execute($cdi_id,$cmp_id,$art_id) or die $dbh->errstr;
							$sth_map_upd->execute($cdi_id,$cmp_id,$cm_use,$art_id) or die $dbh->errstr;
							$sth_map_upd->finish;
						}
					}else{
						$sth_map_ins->execute($cdi_id,$cmp_id,$art_id) or die $dbh->errstr;
						$sth_map_ins->finish;
					}

					if($cdi_name =~ /$is_subclass_cdi_name/){
						$cdi_name = $1;
						my $cmp_abbr = $2;
						$sth_cmp_id_sel->execute($cmp_abbr) or die $dbh->errstr;
						if($sth_cmp_id_sel->rows()>0){
							$column_number = 0;
							$sth_cmp_id_sel->bind_col(++$column_number, \$cmp_id, undef);
							$sth_cmp_id_sel->fetch;
						}
						$sth_cmp_id_sel->finish;
					}

					push(@{$DATAS->{'datas'}},{
						art_id        => $art_id,
						cdi_id        => $cdi_id - 0,
						cdi_name      => $cdi_name,
						cdi_name_e    => $cdi_name_e,
						cmp_id        => $cmp_id - 0,
						cm_use        => $cm_use ? JSON::XS::true : JSON::XS::false,
						never_current => $cm_use ? JSON::XS::false : JSON::XS::true,
					});

					if(defined $cdi_name_e && length $cdi_name_e && exists $data->{'mirror'} && defined $data->{'mirror'} && $data->{'mirror'}){
						my $mirror_cdi_id;
						my $mirror_cdi_name = (exists $data->{'mirror_cdi_name'} && defined $data->{'mirror_cdi_name'} && length $data->{'mirror_cdi_name'} ? $data->{'mirror_cdi_name'} : undef);
						my $mirror_cdi_name_e;
						my $mirror_cmp_id = (exists $data->{'mirror_cmp_id'} && defined $data->{'mirror_cmp_id'} && length $data->{'mirror_cmp_id'} ? $data->{'mirror_cmp_id'} : 0 );
						my $mirror_art_id = (exists $data->{'mirror_art_id'} && defined $data->{'mirror_art_id'} && length $data->{'mirror_art_id'} ? $data->{'mirror_art_id'} : undef);
						my $art_mirroring;

						if(defined $mirror_cdi_name && length $mirror_cdi_name){

							&BITS::ConceptArtMapPart::create_subclass(%merge_data, cdi_name=>$mirror_cdi_name, dbh => $dbh, LOG => $LOG);

							if($data->{'mirror_cmp_id'} && $data->{'mirror_cdi_name'} !~ /$is_subclass_cdi_name/){
								my $cmp_abbr;
								$sth_cmp_abbr_sel->execute($data->{'mirror_cmp_id'}) or die $dbh->errstr;
								if($sth_cmp_abbr_sel->rows()>0){
									$column_number = 0;
									$sth_cmp_abbr_sel->bind_col(++$column_number, \$cmp_abbr, undef);
									$sth_cmp_abbr_sel->fetch;
								}
								$sth_cmp_abbr_sel->finish;
								if(defined $cmp_abbr && length $cmp_abbr){
									$data->{'mirror_cdi_name'} = sprintf('%s-%s',$data->{'mirror_cdi_name'},$cmp_abbr);
									$data->{'mirror_cmp_id'} = 0;
								}
							}
							$mirror_cdi_name = (exists $data->{'mirror_cdi_name'} && defined $data->{'mirror_cdi_name'} && length $data->{'mirror_cdi_name'} ? $data->{'mirror_cdi_name'} : undef);
							$mirror_cmp_id = (exists $data->{'mirror_cmp_id'} && defined $data->{'mirror_cmp_id'} && length $data->{'mirror_cmp_id'} ? $data->{'mirror_cmp_id'} : 0 );

							$sth_cdi_sel->execute($mirror_cdi_name) or die $dbh->errstr;
							$column_number = 0;
							$sth_cdi_sel->bind_col(++$column_number, \$mirror_cdi_id, undef);
							$sth_cdi_sel->bind_col(++$column_number, \$mirror_cdi_name_e, undef);
							$sth_cdi_sel->fetch;
							$sth_cdi_sel->finish;
						}else{
							$mirror_cdi_name_e = lc $cdi_name_e;
							if($mirror_cdi_name_e =~ /\bleft\b/){
								$mirror_cdi_name_e =~ s/\bleft\b/right/g;
							}elsif($mirror_cdi_name_e =~ /\bright\b/){
								$mirror_cdi_name_e =~ s/\bright\b/left/g;
							}
							unless($mirror_cdi_name_e eq lc($cdi_name_e)){
#								&cgi_lib::common::message('$mirror_cdi_name_e='.$mirror_cdi_name_e, $LOG) if(defined $LOG);
								$sth_cdi_sel_mirror->execute($mirror_cdi_name_e) or die $dbh->errstr;
								$column_number = 0;
								$sth_cdi_sel_mirror->bind_col(++$column_number, \$mirror_cdi_id, undef);
								$sth_cdi_sel_mirror->bind_col(++$column_number, \$mirror_cdi_name, undef);
								$sth_cdi_sel_mirror->bind_col(++$column_number, \$mirror_cdi_name_e, undef);
								$sth_cdi_sel_mirror->fetch;
								$sth_cdi_sel_mirror->finish;
							}
						}
#						unless(defined $mirror_cdi_id){	#対応するミラー概念が無い場合は、同じ概念を対応付けする
#							$mirror_cdi_id = $cdi_id;
#							$mirror_cdi_name = $cdi_name;
#							$mirror_cdi_name_e = $cdi_name_e;
#						}
						if(1 || defined $mirror_cdi_id){
#							&cgi_lib::common::message('$mirror_cdi_id='.$mirror_cdi_id, $LOG) if(defined $LOG);
							if(defined $mirror_art_id && length $mirror_art_id){
								if($mirror_art_id =~ /^([A-Z]+[0-9]+)$/){
									$art_mirroring = 0;
								}elsif($mirror_art_id =~ /^([A-Z]+[0-9]+)M$/){
									$art_mirroring = 1;
								}
							}else{
								if($art_id =~ /^([A-Z]+[0-9]+)$/){
									$mirror_art_id = $1.'M';
									$art_mirroring = 1;
								}elsif($art_id =~ /^([A-Z]+[0-9]+)M$/){
									$mirror_art_id = $1;
									$art_mirroring = 0;
								}
							}
							if(defined $mirror_art_id){
#								&cgi_lib::common::message('$mirror_art_id='.$mirror_art_id, $LOG) if(defined $LOG);
								$sth_art_sel->execute($mirror_art_id) or die $dbh->errstr;
								my $mirror_rows = $sth_art_sel->rows();
								$sth_art_sel->finish;
#								&cgi_lib::common::message('$mirror_rows='.$mirror_rows, $LOG) if(defined $LOG);
								unless($mirror_rows>0){
									$sth_art_sel->execute($art_id) or die $dbh->errstr;
									my $rows = $sth_art_sel->rows();
									my($prefix_id,$art_serial,$art_name,$art_ext,$art_timestamp);
#									&cgi_lib::common::message('$rows='.$rows, $LOG) if(defined $LOG);
									if($rows>0){
										my $column_number = 0;
										$sth_art_sel->bind_col(++$column_number, \$prefix_id, undef);
										$sth_art_sel->bind_col(++$column_number, \$art_serial, undef);
										$sth_art_sel->bind_col(++$column_number, \$art_name, undef);
										$sth_art_sel->bind_col(++$column_number, \$art_ext, undef);
										$sth_art_sel->bind_col(++$column_number, \$art_timestamp, undef);
										$sth_art_sel->fetch;
									}
									$sth_art_sel->finish;
									if(defined $art_ext){
#										&cgi_lib::common::message('$art_ext='.$art_ext, $LOG) if(defined $LOG);

										my $org_file_path = &catfile($art_abs_path,qq|$art_id$art_ext|);
										my $mir_file_prefix = &catfile($art_abs_path,$mirror_art_id);
										my $mir_file_path = qq|$mir_file_prefix$art_ext|;
										my $mir_prop = &BITS::VTK::reflection($org_file_path,$mir_file_prefix);
										die __LINE__.qq|:ERROR: reflection()[$mir_file_path]| unless(defined $mir_prop && ref $mir_prop eq 'HASH' && ref $mir_prop->{'bounds'} eq 'ARRAY');

										my $art_xmin = $mir_prop->{'bounds'}->[0] - 0;
										my $art_xmax = $mir_prop->{'bounds'}->[1] - 0;
										my $art_ymin = $mir_prop->{'bounds'}->[2] - 0;
										my $art_ymax = $mir_prop->{'bounds'}->[3] - 0;
										my $art_zmin = $mir_prop->{'bounds'}->[4] - 0;
										my $art_zmax = $mir_prop->{'bounds'}->[5] - 0;
										my $art_volume = defined $mir_prop->{'volume'} && $mir_prop->{'volume'} > 0 ?  &Truncated($mir_prop->{'volume'} / 1000) : 0;

										if(-e $mir_file_path && -s $mir_file_path){
											my $art_data = &readObjFile($mir_file_path);
											my $art_data_size = length($art_data);
											if($art_data_size>0){
												my $art_md5 = &Digest::MD5::md5_hex($art_data);
												my $art_raw_data = &readFile($mir_file_path);
												my $art_raw_data_size = length($art_raw_data);

												my $param_num = 0;
												$sth_art_mirror_ins->bind_param(++$param_num, $prefix_id);
												$sth_art_mirror_ins->bind_param(++$param_num, $mirror_art_id);
												$sth_art_mirror_ins->bind_param(++$param_num, $art_serial);
												$sth_art_mirror_ins->bind_param(++$param_num, $art_name);
												$sth_art_mirror_ins->bind_param(++$param_num, $art_ext);
												$sth_art_mirror_ins->bind_param(++$param_num, $art_timestamp);
												$sth_art_mirror_ins->bind_param(++$param_num, $art_md5);
												$sth_art_mirror_ins->bind_param(++$param_num, $art_data, { pg_type => DBD::Pg::PG_BYTEA });
												$sth_art_mirror_ins->bind_param(++$param_num, $art_data_size);
												$sth_art_mirror_ins->bind_param(++$param_num, $art_xmin);
												$sth_art_mirror_ins->bind_param(++$param_num, $art_xmax);
												$sth_art_mirror_ins->bind_param(++$param_num, $art_ymin);
												$sth_art_mirror_ins->bind_param(++$param_num, $art_ymax);
												$sth_art_mirror_ins->bind_param(++$param_num, $art_zmin);
												$sth_art_mirror_ins->bind_param(++$param_num, $art_zmax);
												$sth_art_mirror_ins->bind_param(++$param_num, $art_volume);
												$sth_art_mirror_ins->bind_param(++$param_num, $art_mirroring);
												$sth_art_mirror_ins->bind_param(++$param_num, $art_raw_data, { pg_type => DBD::Pg::PG_BYTEA });
												$sth_art_mirror_ins->bind_param(++$param_num, $art_raw_data_size);
												$sth_art_mirror_ins->execute() or die $dbh->errstr;
												$mirror_rows = $sth_art_mirror_ins->rows();
												$sth_art_mirror_ins->finish();

												$sth_arti_mirror_ins->execute($mirror_art_id) or die $dbh->errstr;
												$sth_arti_mirror_ins->finish();

												&BITS::Voxel::insVoxelData($dbh,$mirror_art_id,$art_data);

#												&make_art_image($mirror_art_id);
												push(@MAKE_ART_IMAGES, $mirror_art_id);
											}
										}

									}
								}else{
									$sth_arti_mirror_upd->execute($mirror_art_id) or die $dbh->errstr;
									$sth_arti_mirror_upd->finish;
								}

								my $column_number = 0;
								my $mirror_artf_id;
								my $rows_artff_sel_folder;
								$sth_artff_sel_all->execute($art_id) or die $dbh->errstr;
								$sth_artff_sel_all->bind_col(++$column_number, \$mirror_artf_id, undef);
								while($sth_artff_sel_all->fetch){
									$sth_artff_sel_folder->execute($mirror_artf_id,$mirror_art_id) or die $dbh->errstr;
									$rows_artff_sel_folder = $sth_artff_sel_folder->rows();
									$sth_artff_sel_folder->finish;
									next if($rows_artff_sel_folder>0);

									$sth_artff_ins->execute($mirror_artf_id,$mirror_art_id) or die $dbh->errstr;
									$sth_artff_ins->finish;
								}
								$sth_artff_sel_all->finish;

=pod
								$sth_artff_sel->execute($mirror_art_id) or die $dbh->errstr;
								my $rows_artff_sel = $sth_artff_sel->rows();
								$sth_artff_sel->bind_col(++$column_number, \$mirror_artf_id, undef);
								$sth_artff_sel->fetch;
								$sth_artff_sel->finish;
								unless($rows_artff_sel>0){
									unless(defined $mirror_artf_id){
										$column_number = 0;
										$sth_artff_sel->execute($art_id) or die $dbh->errstr;
										$sth_artff_sel->bind_col(++$column_number, \$mirror_artf_id, undef);
										$sth_artff_sel->fetch;
										$sth_artff_sel->finish;
									}
									$rows_artff_sel = 0;
									unless(defined $mirror_artf_id){
										$sth_artff_sel_all->execute($mirror_art_id) or die $dbh->errstr;
										$rows_artff_sel = $sth_artff_sel_all->rows();
										$sth_artff_sel_all->finish;
									}
									unless($rows_artff_sel>0){
										$sth_artff_ins->execute($mirror_artf_id,$mirror_art_id) or die $dbh->errstr;
										$sth_artff_ins->finish;
									}
								}
=cut
							}
						}

						if(defined $mirror_cdi_id && defined $mirror_art_id){
#							&cgi_lib::common::message('$mirror_cdi_id='.$mirror_cdi_id, $LOG) if(defined $LOG);
#							&cgi_lib::common::message('$mirror_art_id='.$mirror_art_id, $LOG) if(defined $LOG);

							$sth_map_sel->execute($mirror_art_id) or die $dbh->errstr;
							my $sel_rows = $sth_map_sel->rows();
							$sth_map_sel->finish;
#							&cgi_lib::common::message('$sel_rows='.$sel_rows, $LOG) if(defined $LOG);

							if($sel_rows>0){
#								$sth_map_exists_sel->execute($mirror_cdi_id,$mirror_cmp_id,$mirror_art_id) or die $dbh->errstr;
								$sth_map_exists_sel->execute($mirror_cdi_id,$mirror_cmp_id,$cm_use,$mirror_art_id) or die $dbh->errstr;
								$sel_rows = $sth_map_exists_sel->rows();
								$sth_map_exists_sel->finish;
#								&cgi_lib::common::message('$sel_rows='.$sel_rows, $LOG) if(defined $LOG);
								unless($sel_rows>0){
									$sth_map_upd->execute($mirror_cdi_id,$mirror_cmp_id,$cm_use,$mirror_art_id) or die $dbh->errstr;
									$sth_map_upd->finish;
								}
							}else{
								$sth_map_ins->execute($mirror_cdi_id,$mirror_cmp_id,$mirror_art_id) or die $dbh->errstr;
								$sth_map_ins->finish;
							}

#							push(@{$DATAS->{'datas'}},{
#								art_id     => $mirror_art_id,
#								cdi_id     => $mirror_cdi_id - 0,
#								cdi_name   => $mirror_cdi_name,
#								cdi_name_e => $mirror_cdi_name_e,
#								cmp_id     => $mirror_cmp_id - 0,
#							});

						}

						if(defined $mirror_art_id){

							if($mirror_cdi_name =~ /$is_subclass_cdi_name/){
								$mirror_cdi_name = $1;
								my $cmp_abbr = $2;
								$sth_cmp_id_sel->execute($cmp_abbr) or die $dbh->errstr;
								if($sth_cmp_id_sel->rows()>0){
									$column_number = 0;
									$sth_cmp_id_sel->bind_col(++$column_number, \$mirror_cmp_id, undef);
									$sth_cmp_id_sel->fetch;
								}
								$sth_cmp_id_sel->finish;
							}

							push(@{$DATAS->{'datas'}},{
								art_id     => $mirror_art_id,
								cdi_id     => defined $mirror_cdi_id ? $mirror_cdi_id - 0 : undef,
								cdi_name   => defined $mirror_cdi_name ? $mirror_cdi_name : undef,
								cdi_name_e => defined $mirror_cdi_name_e ? $mirror_cdi_name_e : undef,
								cmp_id     => defined $mirror_cmp_id ? $mirror_cmp_id - 0 : undef,
							});
						}

					}

				}elsif($sel_rows>0){
					$sth_map_del->execute($art_id) or die $dbh->errstr;
					$sth_map_del->finish;

					push(@{$DATAS->{'datas'}},{
						art_id     => $art_id,
						cdi_id     => undef,
						cdi_name   => undef,
						cdi_name_e => undef,
						cmp_id     => undef
					});
				}
			}

			$DATAS->{'total'} = scalar @{$DATAS->{'datas'}};

#			$dbh->rollback;
			$dbh->commit();
			$dbh->do("NOTIFY concept_art_map");
			$DATAS->{'success'} = JSON::XS::true;

#			&cgi_lib::common::message($DATAS, $LOG) if(defined $LOG);

			&make_art_image(\@MAKE_ART_IMAGES) if(scalar @MAKE_ART_IMAGES);
			&recreate_subclass(%FORM, LOG => $LOG);

		};
		if($@){
#			&cgi_lib::common::message($@, $LOG) if(defined $LOG);
			$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8($@);

			$dbh->rollback;
		}
		$dbh->{'AutoCommit'} = 1;
		$dbh->{'RaiseError'} = 0;

	}else{
		$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8(qq|JSON形式が違います|);
	}
}
elsif($FORM{'cmd'} eq 'create'){
	unless(
		exists $FORM{'datas'} && defined $FORM{'datas'}
	){
		$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8(qq|JSON形式が違います|);
		&gzip_json($DATAS);
		exit;
	}
	my $datas = &cgi_lib::common::decodeJSON($FORM{'datas'});
	&cgi_lib::common::message($datas, $LOG) if(defined $LOG);
	if(defined $datas && ref $datas eq 'ARRAY'){
		$dbh->{'AutoCommit'} = 0;
		$dbh->{'RaiseError'} = 1;
		eval{
			my $sth_map_sel = $dbh->prepare(qq|select cdi_id from concept_art_map where art_id=? and md_id=$md_id and mv_id=$mv_id|) or die $dbh->errstr;
			my $sth_map_upd = $dbh->prepare(qq|update concept_art_map set cdi_id=?,cm_comment=?,cmp_id=?,cm_use=true,cm_entry=now(),cm_delcause=null where art_id=? and md_id=$md_id and mv_id=$mv_id|) or die $dbh->errstr;
			my $sth_map_ins = $dbh->prepare(qq|insert into concept_art_map (cdi_id,cm_comment,cmp_id,art_id,ci_id,md_id,mv_id) values (?,?,?,?,$ci_id,$md_id,$mv_id)|) or die $dbh->errstr;
			my $sth_cdi_sel = $dbh->prepare(qq|select cdi_id from concept_data_info where cdi_name=?|) or die $dbh->errstr;

			my $cm_comment;
			my $NOTIFY_concept_art_map = 0;
			foreach my $data (@$datas){
				my $art_id = (exists $data->{'art_id'} && defined $data->{'art_id'}) ? $data->{'art_id'} : undef;
				my $cdi_id = (exists $data->{'cdi_id'} && defined $data->{'cdi_id'}) ? $data->{'cdi_id'} : undef;
				my $cmp_id = (exists $data->{'cmp_id'} && defined $data->{'cmp_id'}) ? $data->{'cmp_id'} : 0;
				my $cdi_name = (exists $data->{'cdi_name'} && defined $data->{'cdi_name'}) ? $data->{'cdi_name'} : undef;
				next unless(defined $art_id);
				unless(defined $cdi_id){
					if(defined $cdi_name){
						$sth_cdi_sel->execute($cdi_name) or die $dbh->errstr;
						if($sth_cdi_sel->rows()>0){
							my $column_number = 0;
							$sth_cdi_sel->bind_col(++$column_number, \$cdi_id, undef);
							$sth_cdi_sel->fetch;
						}
						$sth_cdi_sel->finish;
					}
				}
				next unless(defined $cdi_id);

				$sth_map_sel->execute($art_id) or die $dbh->errstr;
				my $rows = $sth_map_sel->rows();
				$sth_map_sel->finish;
				if($rows>0){
					$sth_map_upd->execute($cdi_id,$cm_comment,$cmp_id,$art_id) or die $dbh->errstr;
					$sth_map_upd->finish;
				}
				else{
					$sth_map_ins->execute($cdi_id,$cm_comment,$cmp_id,$art_id) or die $dbh->errstr;
					$sth_map_ins->finish;
				}
				$NOTIFY_concept_art_map++;
			}

			$dbh->commit();
			$dbh->do("NOTIFY concept_art_map") if($NOTIFY_concept_art_map>0);
			$DATAS->{'success'} = JSON::XS::true;
		};
		if($@){
#			&cgi_lib::common::message($@, $LOG) if(defined $LOG);
			$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8($@);

			$dbh->rollback;
		}
		$dbh->{'AutoCommit'} = 1;
		$dbh->{'RaiseError'} = 0;
	}else{
		$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8(qq|JSON形式が違います|);
	}
}
elsif($FORM{'cmd'} eq 'destroy'){

	unless(
		exists $FORM{'datas'} && defined $FORM{'datas'}
	){
		$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8(qq|JSON形式が違います|);
		&gzip_json($DATAS);
		exit;
	}


	my $datas = &cgi_lib::common::decodeJSON($FORM{'datas'});
	if(defined $datas && ref $datas eq 'ARRAY'){
		$dbh->{'AutoCommit'} = 0;
		$dbh->{'RaiseError'} = 1;
		eval{
			my $sth_artf_del = $dbh->prepare(qq|delete from art_folder_file where COALESCE(artf_id,0)=? and art_id=?|) or die $dbh->errstr;
			my $sth_artf_sel = $dbh->prepare(qq|select artf_id from art_folder_file where artff_delcause is null and art_id=?|) or die $dbh->errstr;

#			my $sth_arti_delete = $dbh->prepare(qq|delete from art_file_info where art_id=?|) or die $dbh->errstr;
			my $sth_arti_delete  = $dbh->prepare(qq{update art_file_info set art_delcause='DELETE ['||now()||']' where art_id=?}) or die $dbh->errstr;

			my $sth_cm_delete   = $dbh->prepare(qq|delete from concept_art_map where md_id=$md_id and mv_id=$mv_id and art_id=?|) or die $dbh->errstr;

#			my $sth_art_delete  = $dbh->prepare(qq|delete from art_file where art_id=?|) or die $dbh->errstr;
#			my $sth_art_delete  = $dbh->prepare(qq{update art_file set art_delcause='DELETE ['||now()||']' where art_id=?}) or die $dbh->errstr;

			my $NOTIFY_art_file = 0;
			my $NOTIFY_art_folder_file = 0;
			my $NOTIFY_concept_art_map = 0;

#			my $old_cm_modified = &BITS::ConceptArtMapModified::exec(
#				dbh => $dbh,
#				md_id => $md_id,
#				mv_id => $mv_id,
#				use_only_map_terms=>&BITS::Config::USE_ONLY_MAP_TERMS(),
#				LOG => $LOG
#			);

			foreach my $data (@$datas){
				my $art_id = (exists $data->{'art_id'} && defined $data->{'art_id'}) ? $data->{'art_id'} : undef;
				next unless(defined $art_id);

				$sth_artf_del->execute($data->{'artf_id'},$art_id) or die $dbh->errstr;
				my $rows_artf_del = $sth_artf_del->rows();
				$sth_artf_del->finish;
				$NOTIFY_art_folder_file += $rows_artf_del if($rows_artf_del>0);

				$sth_artf_sel->execute($art_id) or die $dbh->errstr;
				my $rows_artf_sel = $sth_artf_sel->rows();
				$sth_artf_sel->finish;
				next if($rows_artf_sel>0);

				$sth_cm_delete->execute($art_id) or die $dbh->errstr;
				my $rows_cm_del = $sth_cm_delete->rows();
				$sth_cm_delete->finish;
				$NOTIFY_concept_art_map += $rows_cm_del if($rows_cm_del>0);

				$sth_arti_delete->execute($art_id) or die $dbh->errstr;
				my $rows_arti_del = $sth_arti_delete->rows();
				$sth_arti_delete->finish;
				$NOTIFY_art_file += $rows_arti_del if($rows_arti_del>0);

#				$sth_art_delete->execute($art_id) or die $dbh->errstr;
#				my $rows_art_del = $sth_art_delete->rows();
#				$sth_art_delete->finish;
#				$NOTIFY_art_file += $rows_art_del if($rows_art_del>0);
			}

#			my $new_cm_modified = &BITS::ConceptArtMapModified::exec(
#				dbh => $dbh,
#				md_id => $md_id,
#				mv_id => $mv_id,
#				use_only_map_terms=>&BITS::Config::USE_ONLY_MAP_TERMS(),
#				LOG => $LOG
#			);
#			my $diff_cm_modified = &BITS::ConceptArtMapModified::diff($new_cm_modified,$old_cm_modified);
#			if(defined $diff_cm_modified){
#				&cgi_lib::common::message($diff_cm_modified, $LOG) if(defined $LOG);
#			}

			$dbh->commit();
			$dbh->do("NOTIFY art_file") if($NOTIFY_art_file);
			$dbh->do("NOTIFY concept_art_map") if($NOTIFY_concept_art_map);
			$dbh->do("NOTIFY art_folder_file") if($NOTIFY_art_folder_file);
			$DATAS->{'success'} = JSON::XS::true;
		};
		if($@){
#			&cgi_lib::common::message($@, $LOG) if(defined $LOG);
			$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8($@);

			$dbh->rollback;
		}
		$dbh->{'AutoCommit'} = 1;
		$dbh->{'RaiseError'} = 0;
	}else{
		$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8(qq|JSON形式が違います|);
	}
}


#$epocsec = &Time::HiRes::tv_interval($t0);
#($sec,$min) = localtime($epocsec);
#&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

#my $json = &cgi_lib::common::encodeJSON($DATAS);
#print $json;
&gzip_json($DATAS);
#print $LOG $json,"\n";
#print $LOG __LINE__.":",&Data::Dumper::Dumper($DATAS),"\n";

#$epocsec = &Time::HiRes::tv_interval($t0);
#($sec,$min) = localtime($epocsec);
#&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

#&cgi_lib::common::message(&cgi_lib::common::encodeJSON($DATAS,1), $LOG) if(defined $LOG);

if($FORM{'cmd'} eq 'read'){
	my $prog_basename = qq|batch-load-obj|;
	my $prog = &catfile($FindBin::Bin,'..','batch',qq|$prog_basename.pl|);
	if(-e $prog && -x $prog){
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
close($LOG);

exit;


sub cmd_read {
	my %FORM = @_;
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

	$dbh->{'AutoCommit'} = 0;
	$dbh->{'RaiseError'} = 1;
	eval{
		my $CX_ART_IDS;					#CX検索用
		my $CX_ART_IDS_PARENT;	#CX検索用
		my $CX_ALL_ART_IDS;			#CX検索用

		if(exists $FORM{'query'} && defined $FORM{'query'} && length $FORM{'query'}){
			my %ART_IDS;
			if(exists $FORM{'exists_art_ids'} && defined $FORM{'exists_art_ids'} && length $FORM{'exists_art_ids'}){
				my $exists_art_ids = &cgi_lib::common::decodeJSON($FORM{'exists_art_ids'});
				if(defined $exists_art_ids && ref $exists_art_ids eq 'ARRAY'){
					$ART_IDS{$_} = undef for(@$exists_art_ids);
				}
			}

			if(exists $FORM{'prefix_char'} && defined $FORM{'prefix_char'} && length $FORM{'prefix_char'} && $FORM{'prefix_char'} eq 'CX'){	#CX検索用
				my $prefix_id;
				my $sql = 'SELECT prefix_id FROM id_prefix WHERE prefix_delcause IS NULL AND prefix_char=?';
				my $sth = $dbh->prepare($sql) or die $dbh->errstr;
				$sth->execute($FORM{'prefix_char'}) or die $dbh->errstr;
				if($sth->rows()>0){
					my $column_number = 0;
					$sth->bind_col(++$column_number, \$prefix_id, undef);
					$sth->fetch;
				}
				$sth->finish;
				undef $sql;
				undef $sth;
				if(defined $prefix_id){
					$sql = 'SELECT art_id,art_name || art_ext,arto_id FROM art_file_info WHERE art_delcause IS NULL AND prefix_id=?';
					$sth = $dbh->prepare($sql) or die $dbh->errstr;
					$sth->execute($prefix_id) or die $dbh->errstr;
					if($sth->rows()>0){
						my $column_number = 0;
						my $art_id;
						my $art_filename;
						my $arto_id;
						$sth->bind_col(++$column_number, \$art_id, undef);
						$sth->bind_col(++$column_number, \$art_filename, undef);
						$sth->bind_col(++$column_number, \$arto_id, undef);
						while($sth->fetch){
							$CX_ART_IDS->{$art_id} = {
								filename => $art_filename
							};
							$CX_ART_IDS_PARENT->{$art_id}->{$art_id} = undef;
							$CX_ALL_ART_IDS->{$art_id} = undef;
							if(defined $arto_id && length $arto_id){
								my @arto_ids;
								if($arto_id =~ /[^A-Za-z0-9]/){
									@arto_ids = split(/[^A-Za-z0-9]+/,$arto_id);
								}else{
									push(@arto_ids,$arto_id);
								}
								$CX_ART_IDS->{$art_id}->{'children'}->{$_} = undef for(@arto_ids);
								$CX_ART_IDS_PARENT->{$_}->{$art_id} = undef for(@arto_ids);
								$CX_ALL_ART_IDS->{$_} = undef for(@arto_ids);
							}
						}
					}
					$sth->finish;
					undef $sql;
					undef $sth;
				}
			}

			my $query = &cgi_lib::common::decodeUTF8($FORM{'query'});
			my $space = &cgi_lib::common::decodeUTF8('　');
			$query =~ s/\.obj//g;
			$query =~ s/$space/ /g;
			$query =~ s/\s*$//g;
			$query =~ s/^\s*//g;
			$query =~ s/\s{2,}/ /g;
#			&cgi_lib::common::message($query,$LOG) if(defined $LOG);
			my @KEYWORDS = split(/\s/,$query);
			my @WHERE = map {'art_name ~* ?'} @KEYWORDS;
			my @WHERE2 = map {'art_id ~* ?'} @KEYWORDS;
			my $sql = sprintf('SELECT art_id FROM art_file_info WHERE (%s) OR (%s)  GROUP BY art_id',join(' AND ',@WHERE),join(' AND ',@WHERE2));
			my $sth = $dbh->prepare($sql) or die $dbh->errstr;
#			&cgi_lib::common::message($sql,$LOG) if(defined $LOG);
#			&cgi_lib::common::message(\@KEYWORDS,$LOG) if(defined $LOG);
			$sth->execute(@KEYWORDS,@KEYWORDS) or die $dbh->errstr;
#			&cgi_lib::common::message($sth->rows(),$LOG) if(defined $LOG);
			my $art_id;
			my $column_number = 0;
			$sth->bind_col(++$column_number, \$art_id, undef);
			while($sth->fetch){
				if(defined $CX_ALL_ART_IDS && ref $CX_ALL_ART_IDS eq 'HASH'){
					if(exists $CX_ALL_ART_IDS->{$art_id}){
						$ART_IDS{$art_id} = undef;
						if(exists $CX_ART_IDS_PARENT->{$art_id}){
#							$ART_IDS{$_} = undef for(keys(%{$CX_ART_IDS_PARENT->{$art_id}}));
						}
					}
				}else{
					$ART_IDS{$art_id} = undef;
				}
			}
			$sth->finish;
			undef $sth;

#			&cgi_lib::common::message([keys(%ART_IDS)],$LOG) if(defined $LOG);
			$FORM{'exists_art_ids'} = &cgi_lib::common::encodeJSON([sort keys(%ART_IDS)]) if(scalar keys(%ART_IDS));
		}

		unless(
			(
				(exists $FORM{'artf_id'} && defined $FORM{'artf_id'} && $FORM{'artf_id'} =~ /^[0-9]+$/) ||
				(exists $FORM{'cdi_name'} && defined $FORM{'cdi_name'} && length $FORM{'cdi_name'}) ||
				(exists $FORM{'cdi_pname'} && defined $FORM{'cdi_pname'} && length $FORM{'cdi_pname'}) ||
				(exists $FORM{'cdi_cname'} && defined $FORM{'cdi_cname'} && length $FORM{'cdi_cname'}) ||
				(exists $FORM{'exists_art_ids'} && defined $FORM{'exists_art_ids'} && length $FORM{'exists_art_ids'})
			)
		){
			$DATAS->{'success'} = JSON::XS::true;
			return $DATAS;
		}

		my $selected_art_ids;
		if(exists $FORM{'selected_art_ids'} && defined $FORM{'selected_art_ids'}){
			$selected_art_ids = &cgi_lib::common::decodeJSON($FORM{'selected_art_ids'});
			$selected_art_ids = undef unless(defined $selected_art_ids && ref $selected_art_ids eq 'HASH');
		};

		my $artf_id=$FORM{'artf_id'};
		my $recursive = exists $FORM{'recursive'} && defined $FORM{'recursive'} && $FORM{'recursive'} eq 'true' ? 1 : 0;
		my $cdi_name=$FORM{'cdi_name'};
		my $cdi_pname=$FORM{'cdi_pname'};
		my $cdi_cname=$FORM{'cdi_cname'};

		my $mirror_cdi_name=$FORM{'mirror_cdi_name'};
		my $mirror_cdi_pname=$FORM{'mirror_cdi_pname'};
		my $mirror_cdi_cname=$FORM{'mirror_cdi_cname'};

		my $exists_art_ids = exists $FORM{'exists_art_ids'} && defined $FORM{'exists_art_ids'} && length $FORM{'exists_art_ids'} ? &cgi_lib::common::decodeJSON($FORM{'exists_art_ids'}) : undef;

		my %USE_ART_ID;
		my %USE_CDI_ID;
		my $USE_ART_DATE;
		my($ELEMENT, $COMP_DENSITY_USE_TERMS, $COMP_DENSITY_END_TERMS, $COMP_DENSITY, $CDI_MAP, $CDI_MAP_ART_DATE, $CDI_ID2CID, $CDI_MAP_SUM_VOLUME_DEL_ID, $CDI_DESC_OBJ_OLD_DEL_ID);
		my %CID2GROUPID;
		my %GROUP_INFO;
		my %USE_VIRTUAL_MAP;
		my ($VIRTUAL_ELEMENT, $VIRTUAL_COMP_DENSITY_USE_TERMS, $VIRTUAL_COMP_DENSITY_END_TERMS, $VIRTUAL_COMP_DENSITY, $VIRTUAL_CDI_MAP, $VIRTUAL_CDI_MAP_ART_DATE, $VIRTUAL_CDI_ID2CID, $VIRTUAL_CDI_MAP_SUM_VOLUME_DEL_ID, $VIRTUAL_CDI_DESC_OBJ_OLD_DEL_ID);
		my $concept_art_map_name = 'concept_art_map';
		my $art_file_info_name = 'art_file_info';

		my $where_artf_id;
		my $where_art_id;
		my $sth;
		my $column_number = 0;
		if(defined $artf_id){
			my @artf_ids;
			if($recursive){
				my %HASH = ($artf_id=>undef);
				do{
					@artf_ids = keys(%HASH);
					my $artf_id;
					my $sth = $dbh->prepare(sprintf('select COALESCE(artf_id,0) from art_folder where artf_delcause is null and COALESCE(artf_pid,0) in (%s)',join(',',map {'?'} @artf_ids))) or die $dbh->errstr;
					$sth->execute(@artf_ids) or die $dbh->errstr;
					$sth->bind_col(1, \$artf_id, undef);
					while($sth->fetch){
						next unless(defined $artf_id && length $artf_id);
						$HASH{$artf_id} = undef;
					}
					$sth->finish;
					undef $sth;
				}while(scalar @artf_ids < scalar keys(%HASH));
				@artf_ids = keys(%HASH);
#				$where_artf_id = 'COALESCE(aff.artf_id,0) in ('.join(',',@artf_ids).')';
			}else{
				push(@artf_ids,$artf_id);
#				$where_artf_id = 'COALESCE(aff.artf_id,0)='.$artf_id;
			}
			$where_artf_id = 'COALESCE(aff.artf_id,0) in ('.join(',',@artf_ids).')';

			$sth = $dbh->prepare("SELECT cdi_id FROM concept_art_map WHERE cm_delcause IS NULL AND md_id=$md_id AND mv_id=$mv_id AND art_id IN (SELECT art_id FROM art_folder_file WHERE COALESCE(artf_id,0) in (". join(',',@artf_ids) .")) GROUP BY cdi_id") or die $dbh->errstr;
			$sth->execute() or die $dbh->errstr;
			$column_number = 0;
			my $cdi_id;
			$sth->bind_col(++$column_number, \$cdi_id, undef);
			while($sth->fetch){
				$USE_CDI_ID{$cdi_id} = undef;
			}
			$sth->finish;
			undef $sth;

		}
		elsif((defined $cdi_name && length $cdi_name) || (defined $cdi_pname && length $cdi_pname) || (defined $cdi_cname && length $cdi_cname)){
			if(defined $exists_art_ids && ref $exists_art_ids eq 'ARRAY'){
				$USE_ART_ID{$_} = undef for(@$exists_art_ids);
				$where_art_id = "arti.art_id in ('".join("','",keys(%USE_ART_ID))."')";	#3.2.1-inferenceに存在しないFMAIDが指定されることがあるため

				$sth = $dbh->prepare(sprintf("SELECT cdi_id FROM concept_art_map WHERE cm_delcause IS NULL AND md_id=$md_id AND mv_id=$mv_id AND art_id IN (%s) GROUP BY cdi_id",join(',',map {'?'} @$exists_art_ids))) or die $dbh->errstr;
				$sth->execute(@$exists_art_ids) or die $dbh->errstr;
				$column_number = 0;
				my $cdi_id;
				$sth->bind_col(++$column_number, \$cdi_id, undef);
				while($sth->fetch){
					$USE_CDI_ID{$cdi_id} = undef;
				}
				$sth->finish;
				undef $sth;

			}

			$column_number = 0;
			if(defined $cdi_name && length $cdi_name){

				my $cdi_id;
				my $cdi_name_e;

				my $mirror_cdi_id;
				my $mirror_cdi_name_e;

				&BITS::ConceptArtMapPart::create_subclass(%FORM, dbh => $dbh, LOG => $LOG);
				&BITS::ConceptArtMapPart::create_subclass(%FORM, cdi_name=>$mirror_cdi_name, dbh => $dbh, LOG => $LOG) if(defined $mirror_cdi_name && length $mirror_cdi_name);

#				$sth = $dbh->prepare("SELECT cdi.cdi_id,cd_name FROM concept_data_info as cdi,concept_data as cd WHERE cdi.ci_id=cd.ci_id AND cdi.cdi_id=cd.cdi_id AND cdi.ci_id=$ci_id AND cd.cb_id=$cb_id AND cdi_name=?") or die $dbh->errstr;
				$sth = $dbh->prepare("SELECT cdi.cdi_id,cd_name FROM concept_data_info as cdi LEFT JOIN (SELECT * FROM concept_data WHERE ci_id=$ci_id AND cb_id=$cb_id) cd ON cd.cdi_id=cdi.cdi_id WHERE cdi.ci_id=$ci_id AND cdi_name=?") or die $dbh->errstr;
				$sth->execute($cdi_name) or die $dbh->errstr;
				if($sth->rows()>0){
					$column_number = 0;
					$sth->bind_col(++$column_number, \$cdi_id, undef);
					$sth->bind_col(++$column_number, \$cdi_name_e, undef);
					$sth->fetch;
				}
				$sth->finish;
				if(defined $mirror_cdi_name && length $mirror_cdi_name){
					$sth->execute($mirror_cdi_name) or die $dbh->errstr;
					if($sth->rows()>0){
						$column_number = 0;
						$sth->bind_col(++$column_number, \$mirror_cdi_id, undef);
						$sth->bind_col(++$column_number, \$mirror_cdi_name_e, undef);
						$sth->fetch;
					}
					$sth->finish;
				}
				undef $sth;

#				&cgi_lib::common::message($cdi_name, $LOG) if(defined $LOG);
#				&cgi_lib::common::message($cdi_name_e, $LOG) if(defined $LOG);
#				&cgi_lib::common::message($cdi_id, $LOG) if(defined $LOG);

				if(defined $cdi_id){
					$USE_CDI_ID{$cdi_id} = undef;
					$GROUP_INFO{$cdi_id} = {
						cdi_name => $cdi_name,
						cdi_name_e => $cdi_name_e
					};
					if(exists $FORM{'art_id'} && defined $FORM{'art_id'} && length $FORM{'art_id'}){
						$USE_VIRTUAL_MAP{$cdi_id}->{$FORM{'art_id'}} = undef;
					}
					if(defined $mirror_cdi_id){
						$USE_CDI_ID{$mirror_cdi_id} = undef;
						$GROUP_INFO{$mirror_cdi_id} = {
							cdi_name => $mirror_cdi_name,
							cdi_name_e => $mirror_cdi_name_e
						};
						if(exists $FORM{'mirror_art_id'} && defined $FORM{'mirror_art_id'} && length $FORM{'mirror_art_id'}){
							$USE_VIRTUAL_MAP{$mirror_cdi_id}->{$FORM{'mirror_art_id'}} = undef;
						}
					}

					#親の場合
					unless(exists $FORM{'hideParentTerm'} && defined $FORM{'hideParentTerm'} && $FORM{'hideParentTerm'} eq '1'){
						if($crl_id eq '0'){
							$sth = $dbh->prepare("SELECT cdi_pid FROM concept_tree WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=? AND cdi_pid IN (SELECT cdi_id FROM concept_art_map WHERE cm_use AND cm_delcause IS NULL AND md_id=$md_id AND mv_id=$mv_id)") or die $dbh->errstr;
						}else{
							$sth = $dbh->prepare("SELECT cdi_pid FROM concept_tree WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=? AND cdi_pid IN (SELECT cdi_id FROM concept_art_map WHERE cm_use AND cm_delcause IS NULL AND md_id=$md_id AND mv_id=$mv_id) AND crl_id=$crl_id") or die $dbh->errstr;
						}
						my $cdi_pid;
						$sth->execute($cdi_id) or die $dbh->errstr;
						$column_number = 0;
						$sth->bind_col(++$column_number, \$cdi_pid, undef);
						while($sth->fetch){
							next unless(defined $cdi_pid);
							$USE_CDI_ID{$cdi_pid} = undef;
						}
						$sth->finish;
						if(defined $mirror_cdi_id){
							$sth->execute($mirror_cdi_id) or die $dbh->errstr;
							$column_number = 0;
							$sth->bind_col(++$column_number, \$cdi_pid, undef);
							while($sth->fetch){
								next unless(defined $cdi_pid);
								$USE_CDI_ID{$cdi_pid} = undef;
							}
							$sth->finish;
						}
						undef $sth;
					}

					#先祖の場合
					unless(exists $FORM{'hideAncestorTerm'} && defined $FORM{'hideAncestorTerm'} && $FORM{'hideAncestorTerm'} eq '1'){
						$sth = $dbh->prepare("SELECT cti_pids FROM concept_tree_info WHERE ci_id=$ci_id AND cb_id=$cb_id AND crl_id=$crl_id AND cti_pids IS NOT NULL AND cdi_id=?") or die $dbh->errstr;
						my $cti_pids;
						$sth->execute($cdi_id) or die $dbh->errstr;
						$column_number = 0;
						$sth->bind_col(++$column_number, \$cti_pids, undef);
						while($sth->fetch){
							next unless(defined $cti_pids);
							$cti_pids = &cgi_lib::common::decodeJSON($cti_pids);
							next unless(defined $cti_pids && ref $cti_pids eq 'ARRAY');
							$USE_CDI_ID{$_} = undef for(@$cti_pids);
						}
						$sth->finish;
						if(defined $mirror_cdi_id){
							$sth->execute($mirror_cdi_id) or die $dbh->errstr;
							$column_number = 0;
							$sth->bind_col(++$column_number, \$cti_pids, undef);
							while($sth->fetch){
								next unless(defined $cti_pids);
								$cti_pids = &cgi_lib::common::decodeJSON($cti_pids);
								next unless(defined $cti_pids && ref $cti_pids eq 'ARRAY');
								$USE_CDI_ID{$_} = undef for(@$cti_pids);
							}
							$sth->finish;
						}
						undef $sth;
					}

					#子供の場合
					unless(exists $FORM{'hideChildrenTerm'} && defined $FORM{'hideChildrenTerm'} && $FORM{'hideChildrenTerm'} eq '1'){
						if($crl_id eq '0'){
							$sth = $dbh->prepare("SELECT cdi_id FROM concept_tree WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_pid=? AND cdi_id IN (SELECT cdi_id FROM concept_art_map WHERE cm_use AND cm_delcause IS NULL AND md_id=$md_id AND mv_id=$mv_id)") or die $dbh->errstr;
						}else{
							$sth = $dbh->prepare("SELECT cdi_id FROM concept_tree WHERE ci_id=$ci_id AND cb_id=$cb_id AND crl_id=$crl_id AND cdi_pid=? AND cdi_id IN (SELECT cdi_id FROM concept_art_map WHERE cm_use AND cm_delcause IS NULL AND md_id=$md_id AND mv_id=$mv_id)") or die $dbh->errstr;
						}
						my $cdi_cid;
						$sth->execute($cdi_id) or die $dbh->errstr;
						$column_number = 0;
						$sth->bind_col(++$column_number, \$cdi_cid, undef);
						while($sth->fetch){
							next unless(defined $cdi_cid);
							$USE_CDI_ID{$cdi_cid} = undef;
						}
						$sth->finish;
						if(defined $mirror_cdi_id){
							$sth->execute($mirror_cdi_id) or die $dbh->errstr;
							$column_number = 0;
							$sth->bind_col(++$column_number, \$cdi_cid, undef);
							while($sth->fetch){
								next unless(defined $cdi_cid);
								$USE_CDI_ID{$cdi_cid} = undef;
							}
							$sth->finish;
						}
						undef $sth;
					}

					#子孫の場合
					unless(exists $FORM{'hideDescendantsTerm'} && defined $FORM{'hideDescendantsTerm'} && $FORM{'hideDescendantsTerm'} eq '1'){
						unless(exists $FORM{'hidePairTerm'} && defined $FORM{'hidePairTerm'} && $FORM{'hidePairTerm'} eq '1'){
							my $cdi_pair_name_e;
							$sth = $dbh->prepare("SELECT cd_name FROM concept_data_info as cdi,concept_data as cd WHERE cdi.ci_id=cd.ci_id AND cdi.cdi_id=cd.cdi_id AND cdi.ci_id=$ci_id AND cd.cb_id=$cb_id AND cdi_name=?") or die $dbh->errstr;
							$sth->execute($cdi_name) or die $dbh->errstr;
							$column_number = 0;
							$sth->bind_col(++$column_number, \$cdi_pair_name_e, undef);
							$sth->fetch;
							$sth->finish;
							undef $sth;
							if(defined $cdi_pair_name_e && ($cdi_pair_name_e =~ /\bleft\b/i || $cdi_pair_name_e =~ /\bright\b/i)){
								if($cdi_pair_name_e =~ /\bleft\b/i){
									$cdi_pair_name_e =~ s/\bleft\b/right/i
								}elsif($cdi_pair_name_e =~ /\bright\b/i){
									$cdi_pair_name_e =~ s/\bright\b/left/i
								}
	#							&cgi_lib::common::message($cdi_pair_name_e, $LOG) if(defined $LOG);
								$cdi_id = undef;
								$cdi_name = undef;
								$cdi_name_e = undef;

								$sth = $dbh->prepare("SELECT cdi.cdi_id,cdi_name,cd_name FROM concept_data_info as cdi,concept_data as cd WHERE cdi.ci_id=cd.ci_id AND cdi.cdi_id=cd.cdi_id AND cdi.ci_id=$ci_id AND cd.cb_id=$cb_id AND lower(cd_name)=lower(?)") or die $dbh->errstr;
								$sth->execute($cdi_pair_name_e) or die $dbh->errstr;
								if($sth->rows()>0){
									$column_number = 0;
									$sth->bind_col(++$column_number, \$cdi_id, undef);
									$sth->bind_col(++$column_number, \$cdi_name, undef);
									$sth->bind_col(++$column_number, \$cdi_name_e, undef);
									$sth->fetch;
								}
								$sth->finish;
								undef $sth;
	#							&cgi_lib::common::message($cdi_id, $LOG) if(defined $cdi_id && defined $LOG);
	#							&cgi_lib::common::message($cdi_name, $LOG) if(defined $cdi_name && defined $LOG);
	#							&cgi_lib::common::message($cdi_name_e, $LOG) if(defined $cdi_name_e && defined $LOG);
								if(defined $cdi_id){
									$USE_CDI_ID{$cdi_id} = undef;
									$GROUP_INFO{$cdi_id} = {
										cdi_name => $cdi_name,
										cdi_name_e => $cdi_name_e
									};
								}

							}

							my $sql = sprintf("SELECT cdi_id,cti_cids FROM concept_tree_info WHERE ci_id=$ci_id AND cb_id=$cb_id AND crl_id=$crl_id AND cdi_id IN (%s)",join(',',keys(%USE_CDI_ID)));
		#					&cgi_lib::common::message($sql, $LOG) if(defined $sql && defined $LOG);
							$sth = $dbh->prepare($sql) or die $dbh->errstr;
							$sth->execute() or die $dbh->errstr;
							$column_number = 0;
							my $cti_cids;
							$sth->bind_col(++$column_number, \$cdi_id, undef);
							$sth->bind_col(++$column_number, \$cti_cids, undef);
							while($sth->fetch){
								$CID2GROUPID{$cdi_id} = $cdi_id;
								if(defined $cti_cids){
									$cti_cids = &cgi_lib::common::decodeJSON($cti_cids);
									next unless(defined $cti_cids && ref $cti_cids eq 'ARRAY');
									$USE_CDI_ID{$_} = undef for(@$cti_cids);
									$CID2GROUPID{$_} = $cdi_id for(@$cti_cids);
								}
							}
							$sth->finish;
							undef $sth;
						}
						else{
							$sth = $dbh->prepare("SELECT cti_cids FROM concept_tree_info WHERE ci_id=$ci_id AND cb_id=$cb_id AND crl_id=$crl_id AND cti_cids IS NOT NULL AND cdi_id=?") or die $dbh->errstr;
							my $cti_cids;
							$sth->execute($cdi_id) or die $dbh->errstr;
							$column_number = 0;
							$sth->bind_col(++$column_number, \$cti_cids, undef);
							while($sth->fetch){
								next unless(defined $cti_cids);
								$cti_cids = &cgi_lib::common::decodeJSON($cti_cids);
								next unless(defined $cti_cids && ref $cti_cids eq 'ARRAY');
								$USE_CDI_ID{$_} = undef for(@$cti_cids);
							}
							$sth->finish;
							if(defined $mirror_cdi_id){
								$sth->execute($mirror_cdi_id) or die $dbh->errstr;
								$column_number = 0;
								$sth->bind_col(++$column_number, \$cti_cids, undef);
								while($sth->fetch){
									next unless(defined $cti_cids);
									$cti_cids = &cgi_lib::common::decodeJSON($cti_cids);
									next unless(defined $cti_cids && ref $cti_cids eq 'ARRAY');
									$USE_CDI_ID{$_} = undef for(@$cti_cids);
								}
								$sth->finish;
							}
							undef $sth;
						}
					}

				}
#				&cgi_lib::common::message(\%USE_CDI_ID, $LOG) if(defined $LOG);
#				&cgi_lib::common::message(\%CID2GROUPID, $LOG) if(defined $LOG);
#				&cgi_lib::common::message(\%GROUP_INFO, $LOG) if(defined $LOG);

			}
			elsif(defined $cdi_pname && length $cdi_pname){
				#未使用のため
				$DATAS->{'success'} = JSON::XS::true;
				&gzip_json($DATAS);
				exit;

				$sth = $dbh->prepare("SELECT cdi_pid,crt_ids FROM concept_data_info AS cdi LEFT JOIN (SELECT cdi_id,cdi_pid,COALESCE(crt_ids,'0') as crt_ids FROM concept_tree WHERE ci_id=$ci_id AND cb_id=$cb_id) AS ct ON ct.cdi_id=cdi.cdi_id WHERE ci_id=$ci_id AND cdi_name=?") or die $dbh->errstr;
				$sth->execute($cdi_pname) or die $dbh->errstr;
				$column_number = 0;
				my $cdi_pid;
				my $crt_ids;
				$sth->bind_col(++$column_number, \$cdi_pid, undef);
				$sth->bind_col(++$column_number, \$crt_ids, undef);
				while($sth->fetch){
					next unless(defined $cdi_pid);
					$USE_CDI_ID{$cdi_pid} = [split(/;/,$crt_ids)];
				}
				$sth->finish;
				undef $sth;
			}
			elsif(defined $cdi_cname && length $cdi_cname){

				&BITS::ConceptArtMapPart::create_subclass(%FORM, cdi_name=>$cdi_cname, dbh => $dbh, LOG => $LOG);
				&BITS::ConceptArtMapPart::create_subclass(%FORM, cdi_name=>$mirror_cdi_cname, dbh => $dbh, LOG => $LOG) if(defined $mirror_cdi_cname && length $mirror_cdi_cname);

				my $cdi_cid;
				my $mirror_cdi_cid;
				$sth = $dbh->prepare("SELECT cdi_id FROM concept_data_info WHERE ci_id=$ci_id AND cdi_name=?") or die $dbh->errstr;
				$sth->execute($cdi_cname) or die $dbh->errstr;
				$column_number = 0;
				$sth->bind_col(++$column_number, \$cdi_cid, undef);
				$sth->fetch;
				$sth->finish;
				if(defined $mirror_cdi_cname && length $mirror_cdi_cname){
					$sth->execute($mirror_cdi_cname) or die $dbh->errstr;
					$column_number = 0;
					$sth->bind_col(++$column_number, \$mirror_cdi_cid, undef);
					$sth->fetch;
					$sth->finish;
				}
				undef $sth;
#				&cgi_lib::common::message($cdi_cname, $LOG) if(defined $LOG);
#				&cgi_lib::common::message($cdi_cid, $LOG) if(defined $LOG);

				if(defined $cdi_cid){
					if(exists $FORM{'art_id'} && defined $FORM{'art_id'} && length $FORM{'art_id'}){
						$USE_VIRTUAL_MAP{$cdi_cid}->{$FORM{'art_id'}} = undef;
					}
					if(defined $mirror_cdi_cid){
						if(exists $FORM{'mirror_art_id'} && defined $FORM{'mirror_art_id'} && length $FORM{'mirror_art_id'}){
							$USE_VIRTUAL_MAP{$mirror_cdi_cid}->{$FORM{'mirror_art_id'}} = undef;
						}
					}

					#先祖の場合
					unless(exists $FORM{'hideAncestorTerm'} && defined $FORM{'hideAncestorTerm'} && $FORM{'hideAncestorTerm'} eq '1'){
						my $cti_pids;
						$sth = $dbh->prepare("SELECT cti_pids FROM concept_tree_info WHERE ci_id=$ci_id AND cb_id=$cb_id AND crl_id=$crl_id AND cti_pids IS NOT NULL AND cdi_id=?") or die $dbh->errstr;
						$sth->execute($cdi_cid) or die $dbh->errstr;
						$column_number = 0;
						$sth->bind_col(++$column_number, \$cti_pids, undef);
						while($sth->fetch){
							next unless(defined $cti_pids);
							$cti_pids = &cgi_lib::common::decodeJSON($cti_pids);
							next unless(defined $cti_pids && ref $cti_pids eq 'ARRAY');
							$USE_CDI_ID{$_} = undef for(@$cti_pids);
						}
						$sth->finish;
						if(defined $mirror_cdi_cid){
							$sth->execute($mirror_cdi_cid) or die $dbh->errstr;
							$column_number = 0;
							$sth->bind_col(++$column_number, \$cti_pids, undef);
							while($sth->fetch){
								next unless(defined $cti_pids);
								$cti_pids = &cgi_lib::common::decodeJSON($cti_pids);
								next unless(defined $cti_pids && ref $cti_pids eq 'ARRAY');
								$USE_CDI_ID{$_} = undef for(@$cti_pids);
							}
							$sth->finish;
						}
						undef $sth;
					}
					#親の場合
					else{
						my $cdi_pid;
						if($crl_id eq '0'){
							$sth = $dbh->prepare("SELECT cdi_pid FROM concept_tree WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=? AND cdi_pid IN (SELECT cdi_id FROM concept_art_map WHERE cm_use AND cm_delcause IS NULL AND md_id=$md_id AND mv_id=$mv_id)") or die $dbh->errstr;
						}else{
							$sth = $dbh->prepare("SELECT cdi_pid FROM concept_tree WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=? AND cdi_pid IN (SELECT cdi_id FROM concept_art_map WHERE cm_use AND cm_delcause IS NULL AND md_id=$md_id AND mv_id=$mv_id) AND crl_id=$crl_id") or die $dbh->errstr;
						}
						$sth->execute($cdi_cid) or die $dbh->errstr;
						$column_number = 0;
						$sth->bind_col(++$column_number, \$cdi_pid, undef);
						while($sth->fetch){
							next unless(defined $cdi_pid);
							$USE_CDI_ID{$cdi_pid} = undef;
						}
						$sth->finish;
						if(defined $mirror_cdi_cid){
							$sth->execute($mirror_cdi_cid) or die $dbh->errstr;
							$column_number = 0;
							$sth->bind_col(++$column_number, \$cdi_pid, undef);
							while($sth->fetch){
								next unless(defined $cdi_pid);
								$USE_CDI_ID{$cdi_pid} = undef;
							}
							$sth->finish;
						}
						undef $sth;
					}
				}
			}
		}
		elsif(defined $exists_art_ids && ref $exists_art_ids eq 'ARRAY'){
			$USE_ART_ID{$_} = undef for(@$exists_art_ids);

			$sth = $dbh->prepare(sprintf("SELECT cdi_id FROM concept_art_map WHERE cm_delcause IS NULL AND md_id=$md_id AND mv_id=$mv_id AND art_id IN (%s) GROUP BY cdi_id",join(',',map {'?'} @$exists_art_ids))) or die $dbh->errstr;
			$sth->execute(@$exists_art_ids) or die $dbh->errstr;
			$column_number = 0;
			my $cdi_id;
			$sth->bind_col(++$column_number, \$cdi_id, undef);
			while($sth->fetch){
				$USE_CDI_ID{$cdi_id} = undef;
			}
			$sth->finish;
			undef $sth;

			$where_art_id = "arti.art_id in ('".join("','",keys(%USE_ART_ID))."')";
		}

		if(scalar keys(%USE_CDI_ID)){
#&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

			if(scalar keys(%USE_VIRTUAL_MAP)){
				$dbh->{'PrintWarn'} = 0;
				$dbh->do("CREATE TEMP TABLE virtual_concept_art_map AS SELECT * FROM concept_art_map WHERE md_id=$md_id AND mv_id=$mv_id") or die $dbh->errstr;
				$dbh->do("ALTER TABLE virtual_concept_art_map ADD PRIMARY KEY (art_id, md_id, mv_id)") or die $dbh->errstr;
				$dbh->do("CREATE INDEX idx_virtual_concept_art_map_1 ON virtual_concept_art_map (ci_id, cdi_id)") or die $dbh->errstr;
				$dbh->do("CREATE INDEX idx_virtual_concept_art_map_2 ON virtual_concept_art_map (md_id, mv_id, cdi_id)") or die $dbh->errstr;
				$dbh->do("CREATE INDEX idx_virtual_concept_art_map_4 ON virtual_concept_art_map (md_id, mv_id)") or die $dbh->errstr;
				$dbh->do("ANALYZE virtual_concept_art_map") or die $dbh->errstr;

				$dbh->do("CREATE TEMP TABLE virtual_art_file_info AS SELECT * FROM art_file_info WHERE art_delcause IS NULL") or die $dbh->errstr;
				$dbh->do("ALTER TABLE virtual_art_file_info ADD PRIMARY KEY (art_id)") or die $dbh->errstr;
#					$dbh->do("ALTER TABLE virtual_art_file_info ADD CONSTRAINT virtual_art_file_info_prefix_id_art_serial_art_mirroring_key UNIQUE (prefix_id, art_serial, art_mirroring)") or die $dbh->errstr;
				$dbh->do("CREATE INDEX idx_virtual_art_file_info_prefix_id_art_serial_art_mirroring ON virtual_art_file_info (prefix_id, art_serial, art_mirroring)") or die $dbh->errstr;
				$dbh->do("ANALYZE virtual_art_file_info") or die $dbh->errstr;

				$dbh->{'PrintWarn'} = 1;
				$concept_art_map_name = 'virtual_concept_art_map';
				$art_file_info_name = 'virtual_art_file_info';

				my $sth_cm_art_del = $dbh->prepare("DELETE FROM $concept_art_map_name WHERE md_id=$md_id AND mv_id=$mv_id AND art_id=?") or die $dbh->errstr;
				my $sth_cm_art_ins = $dbh->prepare("INSERT INTO $concept_art_map_name (art_id,ci_id,cdi_id,md_id,mv_id,cm_use,cm_entry,cm_openid,cmp_id) VALUES (?,$ci_id,?,$md_id,$mv_id,true,now(),'system'::text,0)") or die $dbh->errstr;

				my $sth_arti_sel = $dbh->prepare("SELECT * FROM $art_file_info_name WHERE art_id=?") or die $dbh->errstr;

				foreach my $cdi_id (keys %USE_VIRTUAL_MAP){
					foreach my $art_id (keys %{$USE_VIRTUAL_MAP{$cdi_id}}){
						$sth_cm_art_del->execute($art_id) or die $dbh->errstr;
						$sth_cm_art_del->finish;

						$sth_cm_art_ins->execute($art_id,$cdi_id) or die $dbh->errstr;
						$sth_cm_art_ins->finish;

						$sth_arti_sel->execute($art_id) or die $dbh->errstr;
						my $rows = $sth_arti_sel->rows();
						$sth_arti_sel->finish;
						next if($rows>0);

						my $mirror_art_id;
						my $art_mirroring;
						if($art_id =~ /^([A-Z]+[0-9]+)$/){
							$mirror_art_id = $1.'M';
							$art_mirroring = 1;
						}elsif($art_id =~ /^([A-Z]+[0-9]+)M$/){
							$mirror_art_id = $1;
							$art_mirroring = 0;
						}
						next unless(defined $mirror_art_id && defined $art_mirroring);
						my $hash_ref;
						$sth_arti_sel->execute($mirror_art_id) or die $dbh->errstr;
						$rows = $sth_arti_sel->rows();
						$hash_ref = $sth_arti_sel->fetchrow_hashref if($rows>0);
						$sth_arti_sel->finish;
						next unless(defined $hash_ref && ref $hash_ref eq 'HASH');
						$hash_ref->{'art_id'} = $art_id;
						$hash_ref->{'art_mirroring'} = $art_mirroring;
						$hash_ref->{'art_xmin'} *= -1;
						$hash_ref->{'art_xmax'} *= -1;

						my $sql = sprintf("INSERT INTO $art_file_info_name (%s) VALUES (%s)",join(',',sort keys(%$hash_ref)),join(',',map {'?'} keys(%$hash_ref)));
						my @values = map {$hash_ref->{$_}} sort keys(%$hash_ref);

#							&cgi_lib::common::message('$sql='.$sql, $LOG) if(defined $LOG);
#							&cgi_lib::common::message(\@values, $LOG) if(defined $LOG);

						my $sth_arti_ins = $dbh->prepare($sql) or die $dbh->errstr;
						$sth_arti_ins->execute(@values) or die $dbh->errstr;
						$sth_arti_ins->finish;
						undef $sth_arti_ins;

					}
				}

				undef $sth_cm_art_del;
				undef $sth_cm_art_ins;
			}

&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

#				my $sql = sprintf("SELECT art_id,cdi_id FROM concept_art_map WHERE cm_use AND cm_delcause IS NULL AND md_id=$md_id AND mv_id=$mv_id AND cdi_id IN (%s) GROUP BY art_id,cdi_id",join(',',keys(%USE_CDI_ID)));
#				my $sql = sprintf("SELECT art_id,cdi_id FROM concept_art_map WHERE cm_delcause IS NULL AND md_id=$md_id AND mv_id=$mv_id AND cdi_id IN (%s) GROUP BY art_id,cdi_id",join(',',keys(%USE_CDI_ID)));
			my $sql = sprintf("SELECT art_id,cdi_id FROM $concept_art_map_name WHERE cm_delcause IS NULL AND md_id=$md_id AND mv_id=$mv_id AND cdi_id IN (%s) GROUP BY art_id,cdi_id",join(',',keys(%USE_CDI_ID)));
			%USE_CDI_ID = ();
#			&cgi_lib::common::message($sql,$LOG) if(defined $LOG);
			$sth = $dbh->prepare($sql) or die $dbh->errstr;
			$sth->execute() or die $dbh->errstr;
			$column_number = 0;
			my $art_id;
			my $cdi_id;
			$sth->bind_col(++$column_number, \$art_id, undef);
			$sth->bind_col(++$column_number, \$cdi_id, undef);
			while($sth->fetch){
				$USE_ART_ID{$art_id} = undef;
				$USE_CDI_ID{$cdi_id} = undef;
			}
			$sth->finish;
			undef $sth;

#&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

			if(scalar keys(%USE_ART_ID) && scalar keys(%USE_CDI_ID)){
				$where_art_id = "arti.art_id in ('".join("','",keys(%USE_ART_ID))."')";

#					&cgi_lib::common::message([sort keys(%USE_CDI_ID)], $LOG) if(defined $LOG);
				$sth = $dbh->prepare(sprintf("SELECT cdi_id,cti_depth FROM concept_tree_info WHERE ci_id=$ci_id AND cb_id=$cb_id AND crl_id=$crl_id AND cdi_id IN (%s)",join(',',keys(%USE_CDI_ID)))) or die $dbh->errstr;
				$sth->execute() or die $dbh->errstr;
				my $concept_tree_info_rows = $sth->rows();
#				&cgi_lib::common::message($sth->rows(), $LOG) if(defined $LOG);
				if($concept_tree_info_rows>0){
					$column_number = 0;
					my $cti_id;
					my $cti_depth;
					$sth->bind_col(++$column_number, \$cti_id, undef);
					$sth->bind_col(++$column_number, \$cti_depth, undef);
					while($sth->fetch){
						next unless(defined $cti_id && exists $USE_CDI_ID{$cti_id});
						$USE_CDI_ID{$cti_id} = $cti_depth - 0;
					}
				}
				$sth->finish;
				undef $sth;

#&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

				my $use_cdi_ids = [grep {defined $USE_CDI_ID{$_}} keys %USE_CDI_ID];
#				&cgi_lib::common::message($use_cdi_ids, $LOG) if(defined $LOG);
				if(scalar @$use_cdi_ids){

					($ELEMENT, $COMP_DENSITY_USE_TERMS, $COMP_DENSITY_END_TERMS, $COMP_DENSITY, $CDI_MAP, $CDI_MAP_ART_DATE, $CDI_ID2CID, $CDI_MAP_SUM_VOLUME_DEL_ID, $CDI_DESC_OBJ_OLD_DEL_ID) = &BITS::ConceptArtMapModified::calcElementAndDensity(
						dbh     => $dbh,
						md_id   => $md_id,
						mv_id   => $mv_id,
						ci_id   => $ci_id,
						cb_id   => $cb_id,
						crl_id  => $crl_id,
						cdi_ids => $use_cdi_ids,#[keys %USE_CDI_ID],
						concept_art_map_name => $concept_art_map_name,
						art_file_info_name => $art_file_info_name,
#						LOG => $LOG
					);

					if(defined $LOG){
#						&cgi_lib::common::message($ELEMENT, $LOG);
#						&cgi_lib::common::message($COMP_DENSITY_USE_TERMS, $LOG);
#						&cgi_lib::common::message($COMP_DENSITY_END_TERMS, $LOG);
#						&cgi_lib::common::message($COMP_DENSITY, $LOG);
#						&cgi_lib::common::message($CDI_MAP, $LOG);
#						&cgi_lib::common::message($CDI_MAP_ART_DATE, $LOG);
#						&cgi_lib::common::message($CDI_ID2CID, $LOG);
#						&cgi_lib::common::message($CDI_MAP_SUM_VOLUME_DEL_ID, $LOG);
#						&cgi_lib::common::message($CDI_DESC_OBJ_OLD_DEL_ID, $LOG);
					}

#&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

					if(scalar keys(%USE_VIRTUAL_MAP)){
						($VIRTUAL_ELEMENT, $VIRTUAL_COMP_DENSITY_USE_TERMS, $VIRTUAL_COMP_DENSITY_END_TERMS, $VIRTUAL_COMP_DENSITY, $VIRTUAL_CDI_MAP, $VIRTUAL_CDI_MAP_ART_DATE, $VIRTUAL_CDI_ID2CID, $VIRTUAL_CDI_MAP_SUM_VOLUME_DEL_ID, $VIRTUAL_CDI_DESC_OBJ_OLD_DEL_ID) = &BITS::ConceptArtMapModified::calcElementAndDensity(
							dbh     => $dbh,
							md_id   => $md_id,
							mv_id   => $mv_id,
							ci_id   => $ci_id,
							cb_id   => $cb_id,
							crl_id  => $crl_id,
							cdi_ids => $use_cdi_ids,#[keys %USE_CDI_ID],
#							LOG => $LOG
						);

						if(defined $LOG){
#							&cgi_lib::common::message($VIRTUAL_ELEMENT, $LOG);
#							&cgi_lib::common::message($VIRTUAL_COMP_DENSITY_USE_TERMS, $LOG);
#							&cgi_lib::common::message($VIRTUAL_COMP_DENSITY_END_TERMS, $LOG);
#							&cgi_lib::common::message($VIRTUAL_COMP_DENSITY, $LOG);
#							&cgi_lib::common::message($VIRTUAL_CDI_MAP, $LOG);
#							&cgi_lib::common::message($VIRTUAL_CDI_MAP_ART_DATE, $LOG);
#							&cgi_lib::common::message($VIRTUAL_CDI_ID2CID, $LOG);
#							&cgi_lib::common::message($VIRTUAL_CDI_MAP_SUM_VOLUME_DEL_ID, $LOG);
#							&cgi_lib::common::message($VIRTUAL_CDI_DESC_OBJ_OLD_DEL_ID, $LOG);
						}

					}
				}

#&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

			}

#			&cgi_lib::common::message(\%USE_ART_ID, $LOG) if(defined $LOG);
#			&cgi_lib::common::message(\%USE_CDI_ID, $LOG) if(defined $LOG);
		}
		my $select_sql;
		if(defined $where_artf_id){
			$dbh->{'PrintWarn'} = 0;
			$dbh->do('CREATE TEMP TABLE selected_art_ids (art_id text PRIMARY KEY,selected boolean default true)') or die $dbh->errstr;
			$dbh->{'PrintWarn'} = 1;

			if(exists $FORM{'select_all'} && defined $FORM{'select_all'}){
				$dbh->do('INSERT INTO selected_art_ids (art_id) SELECT art_id from art_folder_file as aff WHERE '.$where_artf_id.' GROUP BY art_id') or die $dbh->errstr;
			}elsif(defined $selected_art_ids && ref $selected_art_ids eq 'HASH'){
				my @art_ids = keys(%$selected_art_ids);
				my $sth = $dbh->prepare(sprintf('INSERT INTO selected_art_ids (art_id) VALUES %s',join(',',map {'(?)'} @art_ids))) or die $dbh->errstr;
				$sth->execute(@art_ids) or die $dbh->errstr;
				$sth->finish;
				undef $sth;
			}

			$select_sql=<<SQL;
select
 aff.art_id,
 COALESCE(aff.artf_id,0) as artf_id,
 COALESCE(artf.artf_name,'') as artf_name,

 arti.art_name,
 arti.art_ext,
-- arti.art_nsn,
 arti.art_mirroring,

 EXTRACT(EPOCH FROM arti.art_timestamp) as art_timestamp,
 EXTRACT(EPOCH FROM art.art_modified) as art_upload_modified,
 arti.art_md5,
 arti.art_data_size,
 arti.art_xmin,
 arti.art_xmax,
 arti.art_ymin,
 arti.art_ymax,
 arti.art_zmin,
 arti.art_zmax,
 to_number(to_char((arti.art_xmax+arti.art_xmin)/2,'FM99990D0000'),'99990D0000S') as art_xcenter,
 to_number(to_char((arti.art_ymax+arti.art_ymin)/2,'FM99990D0000'),'99990D0000S') as art_ycenter,
 to_number(to_char((arti.art_zmax+arti.art_zmin)/2,'FM99990D0000'),'99990D0000S') as art_zcenter,
 arti.art_volume,
-- arti.art_cube_volume,

 arti.arto_id,

 arti.art_comment as arta_comment,
 arti.art_category as arta_category,
 arti.art_judge as arta_judge,
 arti.art_class as arta_class,

 cm.cdi_id,
 cdi.cdi_name,
 COALESCE(cd.cd_name,cdi.cdi_name_e),
 COALESCE(cd.cd_exists,false),

 cm.cm_comment,
 cm.cmp_id,
 cm.cm_use,
 EXTRACT(EPOCH FROM cm.cm_entry) as cm_entry,

-- null as seg_name,
-- null as seg_color,
 seg_name,
 seg_color,

 COALESCE(sel.selected,false) as selected,
 arti.prefix_id,
 arti.art_serial,

 CASE WHEN cm.cm_entry>=fm_timestamp THEN true
      ELSE false
 END as cm_edited

from
 art_folder_file as aff

left join (
  select *
  from
   art_folder
  where
   artf_delcause is null
 ) as artf on
   aff.artf_id=artf.artf_id

left join (
  select *
  from
   art_file_info
 ) as arti on
   aff.art_id=arti.art_id

left join (
  select
   art_id,
   art_modified
  from
   art_file
 ) as art on
   aff.art_id=art.art_id

left join (
  select
   ci_id,
   cdi_id,
   art_id,
   cm_comment,
   cmp_id,
   cm_use,
   cm_entry
  from
   concept_art_map
  where
--   cm_use and
   cm_delcause is null and
   md_id=$md_id and
   mv_id=$mv_id
 ) as cm on
   aff.art_id=cm.art_id

left join (
  select
   ci_id,
   cdi_id,
   cdi_name,
   cdi_name_e
  from
   concept_data_info
  where
   cdi_delcause is null and
   ci_id=$ci_id
 ) as cdi on
   cdi.cdi_id=cm.cdi_id

LEFT JOIN (
  SELECT cdi_id, cd_name, seg_id, true as cd_exists FROM concept_data WHERE ci_id=$ci_id AND cb_id=$cb_id
 ) cd ON cd.cdi_id = cm.cdi_id
LEFT JOIN (
  SELECT seg_id, seg_name, seg_color, seg_thum_bgcolor FROM concept_segment
 ) cs ON cd.seg_id = cs.seg_id

CROSS JOIN (
  SELECT MAX(fm_timestamp) as fm_timestamp FROM freeze_mapping WHERE fm_point
 ) fm

left join (
 select * from selected_art_ids
) as sel on
   sel.art_id=aff.art_id

where
 aff.artff_delcause is null
 and $where_artf_id
SQL
		}
		elsif(defined $where_art_id){
			$select_sql=<<SQL;
select
 arti.art_id,
 NULL as artf_id,
 NULL as artf_name,

 arti.art_name,
 arti.art_ext,
 arti.art_mirroring,

 EXTRACT(EPOCH FROM arti.art_timestamp) as art_timestamp,
 EXTRACT(EPOCH FROM art.art_modified) as art_upload_modified,
 arti.art_md5,
 arti.art_data_size,
 arti.art_xmin,
 arti.art_xmax,
 arti.art_ymin,
 arti.art_ymax,
 arti.art_zmin,
 arti.art_zmax,
 to_number(to_char((arti.art_xmax+arti.art_xmin)/2,'FM99990D0000'),'99990D0000S') as art_xcenter,
 to_number(to_char((arti.art_ymax+arti.art_ymin)/2,'FM99990D0000'),'99990D0000S') as art_ycenter,
 to_number(to_char((arti.art_zmax+arti.art_zmin)/2,'FM99990D0000'),'99990D0000S') as art_zcenter,
 arti.art_volume,

 arti.arto_id,

 arti.art_comment as arta_comment,
 arti.art_category as arta_category,
 arti.art_judge as arta_judge,
 arti.art_class as arta_class,

 cm.cdi_id,
 cdi.cdi_name,
 COALESCE(cd.cd_name,cdi.cdi_name_e),
 COALESCE(cd.cd_exists,false),

 cm.cm_comment,
 cm.cmp_id,
 cm.cm_use,
 EXTRACT(EPOCH FROM cm.cm_entry) as cm_entry,

 seg_name,
 seg_color,

 false as selected,
 arti.prefix_id,
 arti.art_serial,

 CASE WHEN cm.cm_entry>=fm_timestamp THEN true
      ELSE false
 END as cm_edited

from
-- art_file_info as arti
 $art_file_info_name as arti

left join (
  select
   art_id,
   art_modified
  from
   art_file
 ) as art on
   arti.art_id=art.art_id

left join (
  select
   ci_id,
   cdi_id,
   art_id,
   cm_comment,
   cmp_id,
   cm_use,
   cm_entry
  from
--   concept_art_map
   $concept_art_map_name
  where
--   cm_use and
   cm_delcause is null and
   md_id=$md_id and
   mv_id=$mv_id
 ) as cm on
   arti.art_id=cm.art_id

left join (
  select
   ci_id,
   cdi_id,
   cdi_name,
   cdi_name_e
  from
   concept_data_info
  where
   cdi_delcause is null and
   ci_id=$ci_id
 ) as cdi on
   cdi.cdi_id=cm.cdi_id

LEFT JOIN (
  SELECT cdi_id, cd_name, seg_id, true as cd_exists FROM concept_data WHERE ci_id=$ci_id AND cb_id=$cb_id
 ) cd ON cd.cdi_id = cm.cdi_id
LEFT JOIN (
  SELECT seg_id, seg_name, seg_color, seg_thum_bgcolor FROM concept_segment
 ) cs ON cd.seg_id = cs.seg_id

CROSS JOIN (
  SELECT MAX(fm_timestamp) as fm_timestamp FROM freeze_mapping WHERE fm_point
 ) fm

where
 $where_art_id
SQL
		}
		if(defined $select_sql){
			if(exists $FORM{'sort'} && defined $FORM{'sort'}){
				my $SORT = &cgi_lib::common::decodeJSON($FORM{'sort'});
				my @order_by;
#				@order_by = grep {exists $_->{'property'} && defined $_->{'property'} && length $_->{'property'}} @$SORT if(defined $SORT && ref $SORT eq 'ARRAY');
				@order_by = grep {$_->{'property'} ne 'current_use'} grep {exists $_->{'property'} && defined $_->{'property'} && length $_->{'property'}} @$SORT if(defined $SORT && ref $SORT eq 'ARRAY');
				if(scalar @order_by){
					my ( $idx ) = grep { lc($order_by[$_]->{'property'}) eq 'art_id' } 0 .. $#order_by;
					if(defined $idx && $idx>=0){
						my @remove = splice(@order_by,$idx,0,({
							'property'=>'prefix_id',
							'direction'=>$order_by[$idx]->{'direction'}
						},{
							'property'=>'art_serial',
							'direction'=>$order_by[$idx]->{'direction'}
						}));
					}else{
						push(@order_by,{
							'property'=>'prefix_id',
							'direction'=>$order_by[0]->{'direction'}
						},{
							'property'=>'art_serial',
							'direction'=>$order_by[0]->{'direction'}
						},{
							'property'=>'art_id',
							'direction'=>$order_by[0]->{'direction'}
						});
					}
					( $idx ) = grep { lc($order_by[$_]->{'property'}) eq 'art_filename' } 0 .. $#order_by;
					if(defined $idx && $idx>=0){
						my @remove = splice(@order_by,$idx,1,({
							'property'=>'art_name',
							'direction'=>$order_by[$idx]->{'direction'}
						},{
							'property'=>'art_ext',
							'direction'=>$order_by[$idx]->{'direction'}
						}));
					}
					$select_sql .= ' ORDER BY '. join(',', map {$_->{'property'} .' '. (defined $_->{'direction'} ? uc($_->{'direction'}) : 'ASC')} @order_by);
				}
			}
			if(exists $FORM{'limit'} && defined $FORM{'limit'} && $FORM{'limit'} =~ /^[0-9]+$/){
				$select_sql .= ' LIMIT '. $FORM{'limit'};
			}
			if(exists $FORM{'start'} && defined $FORM{'start'} && $FORM{'start'} =~ /^[0-9]+$/){
				$select_sql .= ' OFFSET '. $FORM{'start'};
			}



			print $LOG __LINE__.qq|:\$select_sql=[$select_sql]\n|;
#			my $sth = $dbh->prepare($sql) or die $dbh->errstr;
			my $sth;


			my $column_number;


#			my $sth_data = $dbh->prepare(qq|select art_data from history_art_file where art_id=? AND hist_serial=?|) or die $dbh->errstr;
#			my $sth_data = $dbh->prepare(qq|select art_data from art_file where art_id=? order by art_serial desc NULLS FIRST limit 1|) or die $dbh->errstr;

#			($epocsec,$microsec) = &Time::HiRes::gettimeofday();
#			my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);
#			print $LOG sprintf("%04d:%04d/%02d/%02d %02d:%02d:%02d.%d\n",__LINE__.$year+1900,$mon+1,$mday,$hour,$min,$sec,$microsec);
			#$epocsec = &Time::HiRes::tv_interval($t0);
			#($sec,$min) = localtime($epocsec);
#			&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

			if(defined $where_artf_id){
				my $sth_count = $dbh->prepare('select art_id from art_folder_file as aff where artff_delcause is null and ' . $where_artf_id . ' group by art_id') or die $dbh->errstr;
				$sth_count->execute() or die $dbh->errstr;
				$DATAS->{'total'} = $sth_count->rows();
				my $art_id;
				$column_number = 0;
				$sth_count->bind_col(++$column_number, \$art_id, undef);
				while($sth_count->fetch){
					$USE_ART_ID{$art_id} = undef if(defined $art_id);
				}
				$sth_count->finish;
				undef $sth_count;
			}
			elsif(defined $where_art_id){
				$DATAS->{'total'} = scalar keys(%USE_ART_ID);
			}

#			($epocsec,$microsec) = &Time::HiRes::gettimeofday();
#			my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);
#			print $LOG sprintf("%04d:%04d/%02d/%02d %02d:%02d:%02d.%d\n",__LINE__.$year+1900,$mon+1,$mday,$hour,$min,$sec,$microsec);
			#$epocsec = &Time::HiRes::tv_interval($t0);
			#($sec,$min) = localtime($epocsec);
#			&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

			if($DATAS->{'total'}>0){
#				if(exists $FORM{'sort'} && defined $FORM{'sort'}){
#					my $SORT;
#					eval{$SORT = &cgi_lib::common::decodeJSON($FORM{'sort'});};
#					if(defined $SORT){
#						my @S = ();
#						foreach my $s (@$SORT){
#							next if($s->{'property'} eq 'selected');
#							push(@S,qq|$s->{property} $s->{direction}|);
#						}
#						$sql .= qq| ORDER BY |.join(",",@S);
#
#						$sth->finish() if(defined $sth);
#						undef $sth;
#					}
#				}

				my %SORT_KEYS;
				my $SORT;
				if(exists $FORM{'sort'} && defined $FORM{'sort'}){
					$SORT = &cgi_lib::common::decodeJSON($FORM{'sort'});
					%SORT_KEYS = map { $_->{'property'} => defined $_->{'direction'} ? uc($_->{'direction'}) : 'ASC' } @$SORT if(defined $SORT && ref $SORT eq 'ARRAY');
				}

				my %FILTER_KEYS;
				my $FILTER;
				if(exists $FORM{'filter'} && defined $FORM{'filter'}){
					$FILTER = &cgi_lib::common::decodeJSON($FORM{'filter'});
					%FILTER_KEYS = map { $_->{'property'} => $_->{'value'} } @$FILTER if(defined $FILTER && ref $FILTER eq 'ARRAY');
				}

				unless(defined $sth){
					print $LOG __LINE__.qq|:\$select_sql=[$select_sql]\n|;

#					($epocsec,$microsec) = &Time::HiRes::gettimeofday();
#					my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);
#					print $LOG sprintf("%04d:%04d/%02d/%02d %02d:%02d:%02d.%d\n",__LINE__.$year+1900,$mon+1,$mday,$hour,$min,$sec,$microsec);
					#$epocsec = &Time::HiRes::tv_interval($t0);
					#($sec,$min) = localtime($epocsec);
#					&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

					$sth = $dbh->prepare($select_sql) or die $dbh->errstr;

#					($epocsec,$microsec) = &Time::HiRes::gettimeofday();
#					my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);
#					print $LOG sprintf("%04d:%04d/%02d/%02d %02d:%02d:%02d.%d\n",__LINE__.$year+1900,$mon+1,$mday,$hour,$min,$sec,$microsec);
					#$epocsec = &Time::HiRes::tv_interval($t0);
					#($sec,$min) = localtime($epocsec);
#					&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

					$sth->execute() or die $dbh->errstr;

#					($epocsec,$microsec) = &Time::HiRes::gettimeofday();
#					my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);
#					print $LOG sprintf("%04d:%04d/%02d/%02d %02d:%02d:%02d.%d\n",__LINE__.$year+1900,$mon+1,$mday,$hour,$min,$sec,$microsec);
					#$epocsec = &Time::HiRes::tv_interval($t0);
					#($sec,$min) = localtime($epocsec);
#					&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);
				}

#				my $sth_art_file_info = $dbh->prepare(qq|select art_name,art_ext,art_group.artg_id,artg_name from art_file_info left join (select * from art_group) as art_group on (art_group.artg_id=art_file_info.artg_id) where art_file_info.art_id=?|) or die $dbh->errstr;
#				my $sth_art_file_info = $dbh->prepare(qq|select art_id,art_name,art_ext from art_file_info where art_file_info.art_id=?|) or die $dbh->errstr;
				my $sth_art_file_info = $dbh->prepare(qq|select art_id,art_name,art_ext from $art_file_info_name where art_id=?|) or die $dbh->errstr;

				my $sth_art_folder = $dbh->prepare(qq|select COALESCE(paf.artf_id,0),COALESCE(paf.artf_name,'') from art_folder as af left join (select artf_id,artf_name from art_folder where artf_delcause is null) paf on paf.artf_id=af.artf_pid where af.artf_delcause is null and af.artf_id=?|) or die $dbh->errstr;

				my $sth_cm_exists = $dbh->prepare(qq|select * from concept_art_map where art_id=? and cdi_id=? and ci_id=$ci_id and md_id=$md_id and mv_id=$mv_id|) or die $dbh->errstr;
				my $sth_cm_art_exists = $dbh->prepare(qq|select * from concept_art_map as cm,concept_data_info as cdi where cm.ci_id=cdi.ci_id and cm.cdi_id=cdi.cdi_id and art_id=? and md_id=$md_id and mv_id=$mv_id|) or die $dbh->errstr;

				my $sth_cmp_id_sel = $dbh->prepare(qq|select cmp_id from concept_art_map_part where cmp_abbr=?|) or die $dbh->errstr;

				my $sth_cdi_sel = $dbh->prepare(qq|select cdi_name from concept_data_info where ci_id=$ci_id AND cdi_id=?|) or die $dbh->errstr;
				my %CDI2NAME;

				my %ART2CDI;
				my %ART2REP;

				my %CRT;
				my $sth_concept_relation_type = $dbh->prepare(qq|select * from concept_relation_type|) or die $dbh->errstr;
				$sth_concept_relation_type->execute() or die $dbh->errstr;
				while(my $hash_ref = $sth_concept_relation_type->fetchrow_hashref){
					$CRT{$hash_ref->{'crt_id'}} = {
						crt_name  => $hash_ref->{'crt_name'},
						crt_abbr  => $hash_ref->{'crt_abbr'},
						crt_order => $hash_ref->{'crt_order'} - 0
					};
				}
				$sth_concept_relation_type->finish;
				undef $sth_concept_relation_type;


				$column_number = 0;

				my $art_id;
				my $artf_id;
				my $artf_name;

				my $art_name;
				my $art_ext;
				my $art_nsn;
				my $art_mirroring;

				my $art_timestamp;
				my $art_upload_modified;
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

				my $arta_comment;
				my $arta_category;
				my $arta_judge;
				my $arta_class;

				my $arto_id;
				my $arto_comment;
				my $arto_name;
				my $arto_ext;

				my $arti_entry;
				my $art_modified;

				my $cdi_id;
				my $cdi_name;
				my $cdi_name_e;
				my $cd_exists;

				my $cm_comment;
				my $cmp_id;
				my $cm_entry;
				my $cm_use;

				my $seg_name;
				my $seg_color;

				my $selected;
				my $prefix_id;
				my $art_serial;

				my $cm_edited;

				my %FOLDER_SEARCH_ART_ID;

				$sth->bind_col(++$column_number, \$art_id, undef);
				$sth->bind_col(++$column_number, \$artf_id, undef);
				$sth->bind_col(++$column_number, \$artf_name, undef);

				$sth->bind_col(++$column_number, \$art_name, undef);
				$sth->bind_col(++$column_number, \$art_ext, undef);
#				$sth->bind_col(++$column_number, \$art_nsn, undef);
				$sth->bind_col(++$column_number, \$art_mirroring, undef);

				$sth->bind_col(++$column_number, \$art_timestamp, undef);
				$sth->bind_col(++$column_number, \$art_upload_modified, undef);
				$sth->bind_col(++$column_number, \$art_md5, undef);
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
#				$sth->bind_col(++$column_number, \$art_cube_volume, undef);

				$sth->bind_col(++$column_number, \$arto_id, undef);

				$sth->bind_col(++$column_number, \$arta_comment, undef);
				$sth->bind_col(++$column_number, \$arta_category, undef);
				$sth->bind_col(++$column_number, \$arta_judge, undef);
				$sth->bind_col(++$column_number, \$arta_class, undef);

				$sth->bind_col(++$column_number, \$cdi_id, undef);
				$sth->bind_col(++$column_number, \$cdi_name, undef);
				$sth->bind_col(++$column_number, \$cdi_name_e, undef);
				$sth->bind_col(++$column_number, \$cd_exists, undef);

				$sth->bind_col(++$column_number, \$cm_comment, undef);
				$sth->bind_col(++$column_number, \$cmp_id, undef);
				$sth->bind_col(++$column_number, \$cm_use, undef);
				$sth->bind_col(++$column_number, \$cm_entry, undef);

				$sth->bind_col(++$column_number, \$seg_name, undef);
				$sth->bind_col(++$column_number, \$seg_color, undef);

				$sth->bind_col(++$column_number, \$selected, undef);
				$sth->bind_col(++$column_number, \$prefix_id, undef);
				$sth->bind_col(++$column_number, \$art_serial, undef);

				$sth->bind_col(++$column_number, \$cm_edited, undef);

				while($sth->fetch){
					next unless(exists $USE_ART_ID{$art_id});
					delete $USE_ART_ID{$art_id};

					#CX検索用
					if(defined $CX_ALL_ART_IDS && ref $CX_ALL_ART_IDS eq 'HASH'){
						next unless(exists $CX_ALL_ART_IDS->{$art_id});
					}


					my $art_rel_path = &abs2rel($art_abs_path,$FindBin::Bin);
					my $file_name = $art_name;
					$file_name .= $art_ext unless($art_name =~ /$art_ext$/);

					my $file_path = &catfile($art_abs_path,qq|$art_id$art_ext|);

#					my $path = &File::Basename::basename($file_path);
=pod
					if(defined $art_data_size && defined $art_timestamp){
						my($s,$t) = (0,0);
						($s,$t) = (stat($file_path))[7,9] if(-e $file_path);
						unless($s==$art_data_size && $t==$art_timestamp){
							print $LOG __LINE__.":\$file_path=[$file_path]\n";
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
								undef $OBJ;
								utime $art_timestamp,$art_timestamp,$file_path;
							}
							undef $art_data;
						}
					}
=cut

					my $arto_comment;
					my $arto_name;
					my $arto_ext;


					my @max_timestamp;
					push(@max_timestamp, $arti_entry) if(defined $arti_entry);
					push(@max_timestamp, $art_timestamp) if(defined $art_timestamp);
					my $art_modified = &List::Util::max(@max_timestamp);
#=cut


#					my $selected = exists $FORM{'select_all'} && defined $FORM{'select_all'} ? JSON::XS::true : JSON::XS::false;
#					unless(exists $FORM{'select_all'} && defined $FORM{'select_all'}){
#						if(defined $selected_art_ids && exists $selected_art_ids->{$art_id} && defined $selected_art_ids->{$art_id}){
#							$selected = JSON::XS::true;
#						}
#					}
					$selected = $selected ? JSON::XS::true : JSON::XS::false;

					my $arto_filename;
					if(defined $arto_id && $arto_id =~ /[^A-Za-z0-9]/){
						my @temp_arto_ids = split(/[^A-Za-z0-9]+/,$arto_id);
						my @arto_ids;
						my @arto_filenames;

						foreach my $temp_art_id (@temp_arto_ids){
							$sth_art_file_info->execute($temp_art_id) or die $dbh->errstr;
							my $temp_art_id;
							my $temp_art_name;
							my $temp_art_ext;
							$sth_art_file_info->bind_col(1, \$temp_art_id, undef);
							$sth_art_file_info->bind_col(2, \$temp_art_name, undef);
							$sth_art_file_info->bind_col(3, \$temp_art_ext, undef);
							while($sth_art_file_info->fetch){
								push(@arto_ids,$temp_art_id);
								push(@arto_filenames,qq|$temp_art_name$temp_art_ext|);
							}
							$sth_art_file_info->finish;
						}

						my $joinChar = '+';
						$arto_id = join($joinChar,@arto_ids);
						$arto_filename = join($joinChar,@arto_filenames);
					}

					my @artf_names;
					if(defined $artf_id && $artf_id!=0){
						push(@artf_names, $artf_name);
						my $temp_artf_pid = $artf_id;
						do{
							my $temp_artf_pname;
							$sth_art_folder->execute($temp_artf_pid) or die $dbh->errstr;
							$sth_art_folder->bind_col(1, \$temp_artf_pid, undef);
							$sth_art_folder->bind_col(2, \$temp_artf_pname, undef);
							$sth_art_folder->fetch;
							$sth_art_folder->finish;
							unshift(@artf_names,$temp_artf_pname) if(defined $temp_artf_pname);
						}while(defined $temp_artf_pid && $temp_artf_pid ne '0');
					}

					my $img_prefix;
					my $img_path;
					my $img_info;
					my $thumbnail_path;
					my $thumbnail_timestamp;
					my $img_size = [undef,undef,undef,[16,16]];
#					if(defined $FORM{'mv_id'}){
#						($img_prefix,$img_path) = &getObjImagePrefix($art_id,$md_id,$mv_id);
#						$img_info = &getImageFileList($img_prefix, $img_size);
#						$thumbnail_path = sprintf($img_info->{'gif_fmt'},$img_prefix,$img_info->{'sizeStrXS'});
#					}
					unless(defined $thumbnail_path && -e $thumbnail_path && -f $thumbnail_path && -s $thumbnail_path){
						($img_prefix,$img_path) = &getObjImagePrefix($art_id);
						$img_info = &getImageFileList($img_prefix, $img_size);
						$thumbnail_path = sprintf($img_info->{'gif_fmt'},$img_prefix,$img_info->{'sizeStrXS'});
#						&cgi_lib::common::message($thumbnail_path, $LOG) if(defined $LOG);
					}
					if(-e $thumbnail_path && -f $thumbnail_path && -s $thumbnail_path){
#						$thumbnail_path = sprintf(qq|<img align=center width=16 height=16 src="%s?%s">|,&abs2rel($thumbnail_path,$FindBin::Bin),(stat($thumbnail_path))[9]);
						$thumbnail_timestamp = (stat($thumbnail_path))[9];
						$thumbnail_path = &abs2rel($thumbnail_path,$FindBin::Bin);
					}else{
						$thumbnail_path = undef;
					}
=pod
					if(exists $USE_CDI_ID{$cdi_id} && defined $USE_CDI_ID{$cdi_id} && ref $USE_CDI_ID{$cdi_id} eq 'ARRAY'){
						foreach my $crt_id (@{$USE_CDI_ID{$cdi_id}}){
							if(exists $CRT{$crt_id}){
								$crt_id = $CRT{$crt_id}->{'crt_name'};
							}else{
							}
						}
					}
=cut
					my $never_current = (defined $cm_use && $cm_use ? JSON::XS::false : JSON::XS::true);
					$cm_use = (defined $cm_use && $cm_use ? JSON::XS::true : JSON::XS::false);

					my $is_virtual = JSON::XS::false;
					my $virtual_current_use;
					my $virtual_current_use_reason;
					my $rows_cm_exists;
					my $hash_cm_exists;

					my $current_use;
					my $current_use_reason;
					if(defined $cdi_id && defined $art_id && defined $CDI_MAP_ART_DATE && ref $CDI_MAP_ART_DATE eq 'HASH' && exists $CDI_MAP_ART_DATE->{$cdi_id} && defined $CDI_MAP_ART_DATE->{$cdi_id} && ref $CDI_MAP_ART_DATE->{$cdi_id} eq 'HASH' && exists $CDI_MAP_ART_DATE->{$cdi_id}->{$art_id}){
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

#					&cgi_lib::common::message($current_use, $LOG) if(defined $LOG);
					if(defined $cdi_id && $current_use == JSON::XS::true && defined $CDI_MAP_SUM_VOLUME_DEL_ID && exists $CDI_MAP_SUM_VOLUME_DEL_ID->{$cdi_id}){
						$current_use = JSON::XS::false;	#子供のOBJが親のボリュームの90%より多い場合
						$current_use_reason = 'Descendants of OBJ is more than 90% of the parent of the volume';
					}

					if(defined $VIRTUAL_CDI_MAP_ART_DATE && ref $VIRTUAL_CDI_MAP_ART_DATE eq 'HASH'){
						$sth_cm_exists->execute($art_id,$cdi_id) or die $dbh->errstr;
						$rows_cm_exists = $sth_cm_exists->rows();
						$hash_cm_exists = $sth_cm_exists->fetchrow_hashref if($rows_cm_exists>0);
						$sth_cm_exists->finish;

						if(defined $cdi_id && defined $art_id && exists $VIRTUAL_CDI_MAP_ART_DATE->{$cdi_id} && defined $VIRTUAL_CDI_MAP_ART_DATE->{$cdi_id} && ref $VIRTUAL_CDI_MAP_ART_DATE->{$cdi_id} eq 'HASH' && exists $VIRTUAL_CDI_MAP_ART_DATE->{$cdi_id}->{$art_id}){
							$is_virtual = JSON::XS::true;
							$virtual_current_use = JSON::XS::true;	#子供のOBJより古くない場合
							$virtual_current_use_reason = undef;
						}else{
							if($rows_cm_exists>0){
								$virtual_current_use = JSON::XS::false;
								if(
									defined $cdi_id &&
									defined $art_id &&
									defined $VIRTUAL_CDI_DESC_OBJ_OLD_DEL_ID &&
									ref     $VIRTUAL_CDI_DESC_OBJ_OLD_DEL_ID eq 'HASH' &&
									exists  $VIRTUAL_CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id} &&
									defined $VIRTUAL_CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id} &&
									ref     $VIRTUAL_CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id} eq 'HASH' &&
									exists  $VIRTUAL_CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id}->{$art_id} &&
									defined $VIRTUAL_CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id}->{$art_id} &&
									ref     $VIRTUAL_CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id}->{$art_id} eq 'HASH' &&
									exists  $VIRTUAL_CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id}->{$art_id}->{'max_cdi_id'} &&
									defined $VIRTUAL_CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id}->{$art_id}->{'max_cdi_id'}
								){
									my $max_cdi_id = $VIRTUAL_CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id}->{$art_id}->{'max_cdi_id'};
									my $max_art_timestamp = localtime($VIRTUAL_CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id}->{$art_id}->{'max_art_timestamp'});

									if($VIRTUAL_CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id}->{$art_id}->{'max_cdi_id'} eq $VIRTUAL_CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id}->{$art_id}->{'del_cdi_id'}){
										$virtual_current_use_reason = sprintf('Older than other OBJ [%s]', $max_art_timestamp->strftime('%Y/%m/%d %H:%M:%S'));
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
										$virtual_current_use_reason = sprintf('It is older than descendant OBJ [%s][%s]', $max_cdi_name, $max_art_timestamp->strftime('%Y/%m/%d %H:%M:%S'));
									}

								}
								elsif(defined $cdi_id){
									$virtual_current_use_reason = 'Older than the other OBJ or descendants of OBJ';
								}
							}
						}
					}

					if(defined $VIRTUAL_CDI_MAP_SUM_VOLUME_DEL_ID && ref $VIRTUAL_CDI_MAP_SUM_VOLUME_DEL_ID eq 'HASH'){
						if(defined $cdi_id && defined $virtual_current_use && $virtual_current_use == JSON::XS::true && exists $VIRTUAL_CDI_MAP_SUM_VOLUME_DEL_ID->{$cdi_id}){
							$is_virtual = JSON::XS::true;
							$virtual_current_use = JSON::XS::false;	#子供のOBJが親のボリュームの90%より多い場合
							$virtual_current_use_reason = 'Descendants of OBJ is more than 90% of the parent of the volume';
						}
					}
#					&cgi_lib::common::message($current_use, $LOG) if(defined $LOG);

					if(defined $cdi_id && defined $art_id && $is_virtual == JSON::XS::false && exists $USE_VIRTUAL_MAP{$cdi_id} && defined $USE_VIRTUAL_MAP{$cdi_id} && ref $USE_VIRTUAL_MAP{$cdi_id} eq 'HASH' && exists $USE_VIRTUAL_MAP{$cdi_id}->{$art_id}){
						unless(defined $rows_cm_exists){
							$sth_cm_exists->execute($art_id,$cdi_id) or die $dbh->errstr;
							$rows_cm_exists = $sth_cm_exists->rows();
							$hash_cm_exists = $sth_cm_exists->fetchrow_hashref if($rows_cm_exists>0);
							$sth_cm_exists->finish;
						}
						$is_virtual = JSON::XS::true unless($rows_cm_exists>0);
					}

#					&cgi_lib::common::message($art_id, $LOG) if(defined $LOG);
#					&cgi_lib::common::message($is_virtual, $LOG) if(defined $LOG);

					my $virtual_cm_use;
					my $virtual_never_current;
					my $virtual_cdi_name;
					if(defined $hash_cm_exists && ref $hash_cm_exists eq 'HASH'){
						$virtual_cm_use = $hash_cm_exists->{'cm_use'} ? JSON::XS::true : JSON::XS::false;
						$virtual_never_current = $hash_cm_exists->{'cm_use'} ? JSON::XS::false : JSON::XS::true;
					}
					if($is_virtual == JSON::XS::true){
						$sth_cm_art_exists->execute($art_id) or die $dbh->errstr;
						my $rows_cm_art_exists = $sth_cm_art_exists->rows();
						my $hash_cm_art_exists;
						$hash_cm_art_exists = $sth_cm_art_exists->fetchrow_hashref if($rows_cm_art_exists>0);
						$sth_cm_art_exists->finish;
						if(defined $hash_cm_art_exists && ref $hash_cm_art_exists eq 'HASH' && exists $hash_cm_art_exists->{'cdi_name'} && defined $hash_cm_art_exists->{'cdi_name'} && $hash_cm_art_exists->{'cdi_name'} ne $cdi_name){
							$virtual_cdi_name = $hash_cm_art_exists->{'cdi_name'};
						}
						$virtual_cm_use = undef if(defined $virtual_cm_use && $virtual_cm_use == $cm_use);
						$virtual_never_current = undef if(defined $virtual_never_current && $virtual_never_current == $never_current);
						$virtual_current_use = undef if(defined $virtual_current_use && $virtual_current_use == $current_use);
						$virtual_current_use_reason = undef if(defined $virtual_current_use_reason && defined $current_use_reason && $virtual_current_use_reason eq $current_use_reason);
						unless(defined $virtual_cdi_name || defined $virtual_cm_use || defined $virtual_never_current || defined $virtual_current_use || defined $virtual_current_use_reason){
							unless(defined $rows_cm_exists){
								$sth_cm_exists->execute($art_id,$cdi_id) or die $dbh->errstr;
								$rows_cm_exists = $sth_cm_exists->rows();
								$hash_cm_exists = $sth_cm_exists->fetchrow_hashref if($rows_cm_exists>0);
								$sth_cm_exists->finish;
							}
							$is_virtual = JSON::XS::false if($rows_cm_exists>0);
						}
					}else{
						$virtual_cm_use = undef if(defined $virtual_cm_use && $virtual_cm_use == $cm_use);
						$virtual_never_current = undef if(defined $virtual_never_current && $virtual_never_current == $never_current);
						$virtual_current_use = undef if(defined $virtual_current_use && $virtual_current_use == $current_use);
						$virtual_current_use_reason = undef if(defined $virtual_current_use_reason && defined $current_use_reason && $virtual_current_use_reason eq $current_use_reason);
						$virtual_cdi_name = undef if(defined $virtual_cdi_name && defined $cdi_name && $virtual_cdi_name eq $cdi_name);

						$is_virtual = JSON::XS::true if(defined $virtual_cdi_name || defined $virtual_cm_use || defined $virtual_never_current || defined $virtual_current_use || defined $virtual_current_use_reason);
					}

					unless(defined $rows_cm_exists){
						$sth_cm_exists->execute($art_id,$cdi_id) or die $dbh->errstr;
						$rows_cm_exists = $sth_cm_exists->rows();
						$hash_cm_exists = $sth_cm_exists->fetchrow_hashref if($rows_cm_exists>0);
						$sth_cm_exists->finish;
					}
					my $is_exists = $rows_cm_exists>0 ? JSON::XS::true : JSON::XS::false;

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

					$FOLDER_SEARCH_ART_ID{$art_id} = undef unless(defined $artf_id);

					push(@{$DATAS->{'datas'}},{

						selected => $selected,

						art_id          => $art_id,
						art_name        => $art_name,
						art_timestamp   => defined $art_timestamp ? $art_timestamp + 0 : undef,
						art_modified    => defined $art_modified ? $art_modified + 0 : undef,
						art_upload_modified    => defined $art_upload_modified ? $art_upload_modified + 0 : undef,
						art_data_size   => defined $art_data_size ? $art_data_size + 0 : undef,

						art_xmin       => defined $art_xmin ? $art_xmin + 0 : undef,
						art_xmax       => defined $art_xmax ? $art_xmax + 0 : undef,
						art_ymin       => defined $art_ymin ? $art_ymin + 0 : undef,
						art_ymax       => defined $art_ymax ? $art_ymax + 0 : undef,
						art_zmin       => defined $art_zmin ? $art_zmin + 0 : undef,
						art_zmax       => defined $art_zmax ? $art_zmax + 0 : undef,

						art_xcenter    => defined $art_xcenter ? $art_xcenter + 0 : undef,
						art_ycenter    => defined $art_ycenter ? $art_ycenter + 0 : undef,
						art_zcenter    => defined $art_zcenter ? $art_zcenter + 0 : undef,

						art_volume     => defined $art_volume ? $art_volume + 0 : undef,

						art_mirroring  => $art_mirroring ? JSON::XS::true : JSON::XS::false,

						arta_comment    => $arta_comment,
						arta_category   => $arta_category,
						arta_judge      => $arta_judge,
						arta_class      => $arta_class,

						arto_id        => $arto_id,
						arto_comment   => $arto_comment,
						arto_filename  => defined $arto_filename ? $arto_filename : (defined $arto_name && defined $arto_ext ? qq|$arto_name$arto_ext| : undef),

						cdi_id         => defined $cdi_id ? $cdi_id - 0 : undef,
						cdi_name       => $cdi_name,
						cdi_name_e     => $cdi_name_e,
						cd_exists      => defined $cd_exists && $cd_exists ? JSON::XS::true : JSON::XS::false,


						cmp_id         => (defined $cmp_id ? $cmp_id-0 : 0),
						cm_use         => $cm_use,
						cm_entry       => defined $cm_entry ? $cm_entry - 0 : undef,

						cm_edited      => defined $cm_edited && $cm_edited ? JSON::XS::true : JSON::XS::false,

						seg_name       => $seg_name,
						seg_color      => $seg_color,

						art_filename   => qq|$art_name$art_ext|,
						art_path       => &abs2rel($file_path,$FindBin::Bin),

						artf_id       => defined $artf_id ? $artf_id - 0 : undef,
						artf_name     => $artf_name,
						artf_names    => \@artf_names,

						art_tmb_relpath   => $thumbnail_path,
						art_tmb_timestamp => defined $thumbnail_path && defined $thumbnail_timestamp ? $thumbnail_timestamp - 0 : undef,
						art_tmb_path   => defined $thumbnail_path && defined $thumbnail_timestamp ? sprintf(qq|<img align=center width=16 height=16 src="%s?%s">|,$thumbnail_path,$thumbnail_timestamp) : undef,

#						relation_type => (exists $USE_CDI_ID{$cdi_id} && defined $USE_CDI_ID{$cdi_id} && ref $USE_CDI_ID{$cdi_id} eq 'ARRAY') ? $USE_CDI_ID{$cdi_id} : undef,
#						depth => (exists $USE_CDI_ID{$cdi_id} && defined $USE_CDI_ID{$cdi_id} && ref $USE_CDI_ID{$cdi_id} eq '') ? $USE_CDI_ID{$cdi_id} : undef,
						depth => (defined $cdi_id && exists $USE_CDI_ID{$cdi_id} && defined $USE_CDI_ID{$cdi_id}) ? $USE_CDI_ID{$cdi_id} : undef,

						current_use        => $current_use,
						current_use_reason => $current_use_reason,

						never_current  => $never_current,

						group_id => defined $cdi_id && exists $CID2GROUPID{$cdi_id} ? $CID2GROUPID{$cdi_id} - 0 : undef,
						group_name => defined $cdi_id && exists $CID2GROUPID{$cdi_id} ? $GROUP_INFO{$CID2GROUPID{$cdi_id}}->{'cdi_name'} : undef,
						group_name_e => defined $cdi_id && exists $CID2GROUPID{$cdi_id} ? $GROUP_INFO{$CID2GROUPID{$cdi_id}}->{'cdi_name_e'} : undef,

#						prefix_id     => $prefix_id - 0,
#						art_serial    => $art_serial - 0

						is_exists => $is_exists,
						is_virtual => $is_virtual,
						virtual_current_use => $virtual_current_use,
						virtual_current_use_reason => $virtual_current_use_reason,
						virtual_cm_use => $virtual_cm_use,
						virtual_never_current => $virtual_never_current,
						virtual_cdi_name => $virtual_cdi_name,
					});

					#CX検索用
					if(defined $CX_ART_IDS_PARENT && ref $CX_ART_IDS_PARENT eq 'HASH' && exists $CX_ART_IDS_PARENT->{$art_id}){
						my $HASH = $DATAS->{'datas'}->[-1];
						my @cx_group_ids = keys(%{$CX_ART_IDS_PARENT->{$art_id}});
						$HASH->{'cx_group_id'} = shift @cx_group_ids;
#						&cgi_lib::common::message($HASH, $LOG) if(defined $LOG);
						if(scalar @cx_group_ids){
							foreach my $cx_group_id (@cx_group_ids){
								my $C = &Clone::clone($HASH);
								$C->{'cx_group_id'} = $cx_group_id;
								push(@{$DATAS->{'datas'}},$C);
#								&cgi_lib::common::message($C, $LOG) if(defined $LOG);
							}
						}
					}else{
#						&cgi_lib::common::message($DATAS->{'datas'}->[-1], $LOG) if(defined $LOG);
					}


					#$epocsec = &Time::HiRes::tv_interval($t0);
					#($sec,$min) = localtime($epocsec);
#					&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

				}
				$sth->finish;
				undef $sth;

				#CX検索用
				if(defined $CX_ART_IDS_PARENT && ref $CX_ART_IDS_PARENT eq 'HASH'){
					$DATAS->{'total'} = scalar @{$DATAS->{'datas'}};
				}

				if(!defined $where_artf_id && defined $where_art_id){
#					$DATAS->{'datas'} = [sort {(defined $a->{'relation_type'} ? 1 : 0) <=> (defined $b->{'relation_type'} ? 1 : 0)} @{$DATAS->{'datas'}}];
					$DATAS->{'datas'} = [sort {
						(exists $b->{'cdi_id'} && defined $b->{'cdi_id'} && exists $USE_CDI_ID{$b->{'cdi_id'}} && defined $USE_CDI_ID{$b->{'cdi_id'}} ? $USE_CDI_ID{$b->{'cdi_id'}} : 0) <=> (exists $a->{'cdi_id'} && defined $a->{'cdi_id'} && exists $USE_CDI_ID{$a->{'cdi_id'}} && defined $USE_CDI_ID{$a->{'cdi_id'}} ? $USE_CDI_ID{$a->{'cdi_id'}} : 0)
					} @{$DATAS->{'datas'}}];

					my $cdi_name=$FORM{'cdi_name'};
					my $cdi_pname=$FORM{'cdi_pname'};
					my @T;
					my @N;
					if(defined $cdi_name && length $cdi_name){
						@T = sort {
							(exists $b->{'cdi_id'} && defined $b->{'cdi_id'} && exists $USE_CDI_ID{$b->{'cdi_id'}} && defined $USE_CDI_ID{$b->{'cdi_id'}} ? $USE_CDI_ID{$b->{'cdi_id'}} : 0) <=> (exists $a->{'cdi_id'} && defined $a->{'cdi_id'} && exists $USE_CDI_ID{$a->{'cdi_id'}} && defined $USE_CDI_ID{$a->{'cdi_id'}} ? $USE_CDI_ID{$a->{'cdi_id'}} : 0)
						} grep {($_->{'cdi_name'} // '') eq $cdi_name} @{$DATAS->{'datas'}};
						@N = sort {
							(exists $b->{'cdi_id'} && defined $b->{'cdi_id'} && exists $USE_CDI_ID{$b->{'cdi_id'}} && defined $USE_CDI_ID{$b->{'cdi_id'}} ? $USE_CDI_ID{$b->{'cdi_id'}} : 0) <=> (exists $a->{'cdi_id'} && defined $a->{'cdi_id'} && exists $USE_CDI_ID{$a->{'cdi_id'}} && defined $USE_CDI_ID{$a->{'cdi_id'}} ? $USE_CDI_ID{$a->{'cdi_id'}} : 0)
						} grep {($_->{'cdi_name'} // '') ne $cdi_name} @{$DATAS->{'datas'}};
						$DATAS->{'datas'} = [];
						push(@{$DATAS->{'datas'}},@T);
						push(@{$DATAS->{'datas'}},@N);
					}
					elsif(defined $cdi_pname && length $cdi_pname){
						@T = sort {
							(exists $b->{'cdi_id'} && defined $b->{'cdi_id'} && exists $USE_CDI_ID{$b->{'cdi_id'}} && defined $USE_CDI_ID{$b->{'cdi_id'}} ? $USE_CDI_ID{$b->{'cdi_id'}} : 0) <=> (exists $a->{'cdi_id'} && defined $a->{'cdi_id'} && exists $USE_CDI_ID{$a->{'cdi_id'}} && defined $USE_CDI_ID{$a->{'cdi_id'}} ? $USE_CDI_ID{$a->{'cdi_id'}} : 0)
						} grep {($_->{'cdi_name'} // '') eq $cdi_pname} @{$DATAS->{'datas'}};
						@N = sort {
							(exists $b->{'cdi_id'} && defined $b->{'cdi_id'} && exists $USE_CDI_ID{$b->{'cdi_id'}} && defined $USE_CDI_ID{$b->{'cdi_id'}} ? $USE_CDI_ID{$b->{'cdi_id'}} : 0) <=> (exists $a->{'cdi_id'} && defined $a->{'cdi_id'} && exists $USE_CDI_ID{$a->{'cdi_id'}} && defined $USE_CDI_ID{$a->{'cdi_id'}} ? $USE_CDI_ID{$a->{'cdi_id'}} : 0)
						} grep {($_->{'cdi_name'} // '') ne $cdi_pname} @{$DATAS->{'datas'}};
						$DATAS->{'datas'} = [];
						push(@{$DATAS->{'datas'}},@T);
						push(@{$DATAS->{'datas'}},@N);
					}

					$DATAS->{'art_timestamp'} = $USE_ART_DATE if(defined $USE_ART_DATE);
				}

#				($epocsec,$microsec) = &Time::HiRes::gettimeofday();
#				my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);
#				print $LOG sprintf("%04d:%04d/%02d/%02d %02d:%02d:%02d.%d\n",__LINE__.$year+1900,$mon+1,$mday,$hour,$min,$sec,$microsec);
				#$epocsec = &Time::HiRes::tv_interval($t0);
				#($sec,$min) = localtime($epocsec);
#				&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);


#				my %FOLDER_SEARCH_ART_ID;
				if(scalar keys(%FOLDER_SEARCH_ART_ID)){
#					{$art_id} = undef unless(defined $artf_id);

					my $sql_art_folder_file = sprintf(qq|select aff.art_id,COALESCE(paf.artf_id,0),COALESCE(paf.artf_name,'') from art_folder_file as aff left join (select artf_id,artf_name from art_folder where artf_delcause is null) paf on paf.artf_id=aff.artf_id where aff.artff_delcause is null and aff.art_id in (%s)|,join(',',map {'?'} keys(%FOLDER_SEARCH_ART_ID)));
					my $sth_art_folder_file = $dbh->prepare($sql_art_folder_file) or die $dbh->errstr;


					$sth_art_folder_file->execute(keys(%FOLDER_SEARCH_ART_ID)) or die $dbh->errstr;
					my $art_id;
					my $artf_id;
					my $artf_name;
					$sth_art_folder_file->bind_col(1, \$art_id, undef);
					$sth_art_folder_file->bind_col(2, \$artf_id, undef);
					$sth_art_folder_file->bind_col(3, \$artf_name, undef);
					while($sth_art_folder_file->fetch){

						my @artf_names = ($artf_name);
						if($artf_id!=0){
							my $temp_artf_pid = $artf_id;
							do{
								my $temp_artf_pname;
								$sth_art_folder->execute($temp_artf_pid) or die $dbh->errstr;
								$sth_art_folder->bind_col(1, \$temp_artf_pid, undef);
								$sth_art_folder->bind_col(2, \$temp_artf_pname, undef);
								$sth_art_folder->fetch;
								$sth_art_folder->finish;
								unshift(@artf_names,$temp_artf_pname) if(defined $temp_artf_pname);
							}while(defined $temp_artf_pid && $temp_artf_pid ne '0');
						}

						push(@{$FOLDER_SEARCH_ART_ID{$art_id}},{
							artf_id       => $artf_id - 0,
							artf_name     => $artf_name,
							artf_names    => []
						});
						push(@{$FOLDER_SEARCH_ART_ID{$art_id}->[-1]->{'artf_names'}}, @artf_names);

					}
					$sth_art_folder_file->finish;
					undef $sth_art_folder_file;


					foreach my $data (@{$DATAS->{'datas'}}){
						$art_id = $data->{'art_id'};
						next unless(exists $FOLDER_SEARCH_ART_ID{$art_id} && defined $FOLDER_SEARCH_ART_ID{$art_id} && ref $FOLDER_SEARCH_ART_ID{$art_id} eq 'ARRAY');
						$data->{'artf_id'} = join(';', map {$_->{'artf_id'}} @{$FOLDER_SEARCH_ART_ID{$art_id}});
						$data->{'artf_name'} = join(';', map {$_->{'artf_name'}} @{$FOLDER_SEARCH_ART_ID{$art_id}});
						if(scalar @{$FOLDER_SEARCH_ART_ID{$art_id}} == 1){
							push(@{$data->{'artf_names'}}, @{$FOLDER_SEARCH_ART_ID{$art_id}->[0]->{'artf_names'}});
						}
						else{
							push(@{$data->{'artf_names'}}, map {$_->{'artf_names'}} @{$FOLDER_SEARCH_ART_ID{$art_id}});
						}
					}

				}
			}

			$sth->finish() if(defined $sth);
			undef $sth;
		}

		$DATAS->{'success'} = JSON::XS::true;
	};
	if($@){
		$DATAS->{'success'} = JSON::XS::false;
		$DATAS->{'total'} = 0;
		$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8($@);
	}
	$dbh->rollback;
	$dbh->{'AutoCommit'} = 1;
	$dbh->{'RaiseError'} = 0;
	return $DATAS;
}

sub make_art_image {
	my $art_ids = shift;
	return unless(defined $art_ids && ref $art_ids eq 'ARRAY' && scalar @$art_ids);
	my $prog_basename = qq|make_art_image|;
	my $prog = &catfile($FindBin::Bin,'..','cron',qq|$prog_basename.pl|);
	if(-e $prog && -x $prog){
		my @OPTIONS = map {"--obj $_"} @$art_ids;
		push(@OPTIONS, sprintf('--host=%s',$ENV{'AG_DB_HOST'})) if(exists $ENV{'AG_DB_HOST'} && defined $ENV{'AG_DB_HOST'});
		push(@OPTIONS, sprintf('--port=%s',$ENV{'AG_DB_PORT'})) if(exists $ENV{'AG_DB_PORT'} && defined $ENV{'AG_DB_PORT'});
		my $options = join(' ',@OPTIONS);
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
				my $cmd = qq|nice -n 19 $prog $options|;
				say STDOUT $cmd;
				exec($cmd);
				exit(1);
			}else{
			}
		}else{
			die("Can't execute program");
		}
	}
}

sub recreate_subclass {
	my %FORM = @_;
	my $LOG = $FORM{'LOG'};
#	&cgi_lib::common::dumper(\%FORM, $LOG) if(defined $LOG);
	return unless(exists $FORM{'ci_id'} && defined $FORM{'ci_id'} && $FORM{'ci_id'} =~ /^[0-9]+$/ && exists $FORM{'cb_id'} && defined $FORM{'cb_id'} && $FORM{'cb_id'} =~ /^[0-9]+$/);
	my $prog_basename = qq|batch-recreate-subclass|;
	my $prog = &catfile($FindBin::Bin,'..','batch',qq|$prog_basename.pl|);
	if(-e $prog && -x $prog){
		my @OPTIONS;
		push(@OPTIONS, sprintf('--host=%s',$ENV{'AG_DB_HOST'})) if(exists $ENV{'AG_DB_HOST'} && defined $ENV{'AG_DB_HOST'});
		push(@OPTIONS, sprintf('--port=%s',$ENV{'AG_DB_PORT'})) if(exists $ENV{'AG_DB_PORT'} && defined $ENV{'AG_DB_PORT'});
		push(@OPTIONS, sprintf('--ci_id=%d',$FORM{'ci_id'}));
		push(@OPTIONS, sprintf('--cb_id=%d',$FORM{'cb_id'}));
		my $options = join(' ',@OPTIONS);

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
