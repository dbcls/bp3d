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

$FORM{'cmd'} = qq|read| unless(defined $FORM{'cmd'});

unless(
	defined $FORM{'cmd'} &&
	defined $FORM{'md_id'} &&
	defined $FORM{'mv_id'} &&
	defined $FORM{'mr_id'} &&
	defined $FORM{'ci_id'} &&
	defined $FORM{'cb_id'} &&
	defined $FORM{'bul_id'}
){
	&gzip_json($DATAS);
	exit;
}

if($FORM{'cmd'} eq 'read'){
	eval{
		my @bind_values;

		my $sql=<<SQL;
select
 arti.art_id,
 arti.art_name,
 arti.art_ext,
 artg.artg_name,
 artg.artg_id,
 EXTRACT(EPOCH FROM arti.art_entry) as arti_entry,
 cm.cdi_id,
 cm.cdi_name,
 cm.cdi_name_e,
 cm.cm_id,
 cm.cm_use,
 cm.cmp_id,
 cm.cm_comment,
 cm.art_hist_serial
-- ,rep.rep_id,
-- EXTRACT(EPOCH FROM rep.rep_entry) as rep_entry,
-- EXTRACT(EPOCH FROM cm_modified) as cm_max_entry_cdi,
-- cd.seg_id,
-- seg_name,
-- seg_color,
-- seg_thum_bgcolor,
-- seg_thum_fgcolor
from
 art_file_info as arti

left join (
 select
  artg_name,
  artg_id,
  artg_delcause,
  atrg_use
 from
  art_group
) as artg on
   arti.artg_id=artg.artg_id

left join (
 select
  art_id,
  art_hist_serial,
  cm.cdi_id,
  cdi.cdi_name,
  cdi.cdi_name_e,
  cm_id,
  cm_use,
  cmp_id,
  cm_comment,
  cm_entry
 from
  (select * from concept_art_map where (ci_id,cb_id,md_id,mv_id,mr_id,art_id,art_hist_serial) in (
    select
     ci_id,cb_id,md_id,mv_id,max(mr_id) as mr_id,art_id,max(art_hist_serial) as art_hist_serial
    from
     concept_art_map
    where
     ci_id=$FORM{'ci_id'} AND
     cb_id=$FORM{'cb_id'} AND
     md_id=$FORM{'md_id'} AND
     mv_id=$FORM{'mv_id'} AND
     mr_id<=$FORM{'mr_id'}
    GROUP BY
     ci_id,cb_id,md_id,mv_id,art_id
   )
  ) as cm

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
   ci_id=$FORM{'ci_id'}
 ) as cdi on
  cm.cdi_id=cdi.cdi_id

 where
  cm_delcause is null
) as cm on
 cm.art_id=arti.art_id

where
 art_delcause is null and
 artg_delcause is null and
 atrg_use and
SQL
		if(exists $FORM{'cm_use'} && defined $FORM{'cm_use'} && length $FORM{'cm_use'}){
			$sql .= qq|cm.cm_use and |;
		}

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
		elsif(exists $FORM{'cm_use_keys'} && defined $FORM{'cm_use_keys'} && length $FORM{'cm_use_keys'}){
			my $cm_use_keys = &cgi_lib::common::decodeJSON($FORM{'cm_use_keys'});
			if(defined $cm_use_keys && ref $cm_use_keys eq 'ARRAY' && scalar @$cm_use_keys){
				push @bind_values,(map {$_->{'art_id'},$_->{'cdi_name'}} @$cm_use_keys);
				$sql .= qq|(arti.art_id,cm.cdi_name) in (|. join(",",map {'(?,?)'} @$cm_use_keys) . ')';
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
  (ci_id,cb_id,md_id,mv_id,mr_id,cdi_id) in (
   select
    ci_id,cb_id,md_id,mv_id,max(mr_id) as mr_id,cdi_id
   from
    concept_art_map
   where
    ci_id=$FORM{'ci_id'} AND
    cb_id=$FORM{'cb_id'} AND
    md_id=$FORM{'md_id'} AND
    mv_id=$FORM{'mv_id'} AND
    mr_id<=$FORM{'mr_id'}
   GROUP BY
    ci_id,cb_id,md_id,mv_id,cdi_id
 )
 and cdi_id=?
|;
				if(exists $FORM{'cm_use'} && defined $FORM{'cm_use'} && lc($FORM{'cm_use'}) eq 'true'){
					$sql_cm .= ' and cm_use';
				}

&cgi_lib::common::message($sql_cm, $LOG) if(defined $LOG);
				my $sth_cm = $dbh->prepare($sql_cm) or die $dbh->errstr;

				my $cdi_id;
				my $but_cids;
				my %cdi_ids_hash;
#				my $sql_bul = qq|select distinct cdi_id,but_cids from view_buildup_tree where but_delcause is null and ci_id=$FORM{'ci_id'} AND cb_id=$FORM{'cb_id'} AND bul_id=$FORM{'bul_id'} AND cdi_name in (|. join(",",map {'?'} @$cdi_names) . ')';
#				my $sql_bul = qq|select distinct cdi_id,but_cids from view_buildup_tree where but_delcause is null and ci_id=$FORM{'ci_id'} AND cb_id=$FORM{'cb_id'} AND cdi_name in (|. join(",",map {'?'} @$cdi_names) . ')';
				my $sql_bul = sprintf(qq|
SELECT
 cdi_id,
 but_cids
FROM
 buildup_tree_info AS bti
WHERE
 but_delcause IS NULL AND
 md_id=$FORM{'md_id'} AND
 mv_id=$FORM{'mv_id'} AND
 mr_id=$FORM{'mr_id'} AND
 ci_id=$FORM{'ci_id'} AND
 cb_id=$FORM{'cb_id'} AND
 cdi_id IN (
  SELECT
   cdi_id
  FROM
   concept_data_info
  WHERE
   ci_id=$FORM{'ci_id'} AND
   cdi_name in (%s)
 )
|,join(',',map {'?'} @$cdi_names));

&cgi_lib::common::message($sql_bul, $LOG) if(defined $LOG);
				my $sth = $dbh->prepare($sql_bul) or die $dbh->errstr;
				$sth->execute(map {$_->{'cdi_name'}} @$cdi_names) or die $dbh->errstr;
				if($sth->rows()){
					my $column_number = 0;
					$sth->bind_col(++$column_number, \$cdi_id,   undef);
					$sth->bind_col(++$column_number, \$but_cids, undef);
					while($sth->fetch){
						$cdi_ids_hash{$cdi_id} = 0 if(defined $cdi_id);
						if(defined $but_cids){
							my $ids = &cgi_lib::common::decodeJSON($but_cids);
							if(defined $ids && ref $ids eq 'ARRAY'){
								$cdi_ids_hash{$_} = 0 for(@$ids);
							}
						}
					}
				}
				$sth->finish;
				undef $sth;
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%cdi_ids_hash,1), $LOG) if(defined $LOG);

#
				my @temp_cdi_ids = keys(%cdi_ids_hash);
				if(scalar @temp_cdi_ids){
					$sql_bul = qq|select but_cids from buildup_tree_info where but_delcause is null and md_id=$FORM{'md_id'} AND mv_id=$FORM{'mv_id'} AND mr_id=$FORM{'mr_id'} AND ci_id=$FORM{'ci_id'} AND cb_id=$FORM{'cb_id'} AND cdi_id=? AND but_cids is not null|;
&cgi_lib::common::message($sql_bul, $LOG) if(defined $LOG);
					my $sth = $dbh->prepare($sql_bul) or die $dbh->errstr;
					foreach my $cid (@temp_cdi_ids){
						$sth->execute($cid) or die $dbh->errstr;
						if($sth->rows()){
							my $column_number = 0;
							my $but_cids;
							$sth->bind_col(++$column_number, \$but_cids, undef);
							while($sth->fetch){
								next unless(defined $but_cids);
								my $ids = &cgi_lib::common::decodeJSON($but_cids);
								next unless(defined $ids && ref $ids eq 'ARRAY');
								$cdi_ids_hash{$_} = 0 for(@$ids);
							}
						}
						$sth->finish;
					}
					undef $sth;
				}
				undef $sql_bul;
				undef @temp_cdi_ids;


#&cgi_lib::common::message("\@temp_cdi_ids=[".join(",",keys(%cdi_ids_hash))."]", $LOG) if(defined $LOG);

				foreach my $id (keys(%cdi_ids_hash)){
					$sth_cm->execute($id) or die $dbh->errstr;
#&cgi_lib::common::message("\$id=[$id]", $LOG) if(defined $LOG);
#&cgi_lib::common::message("\$sth_cm->rows()=[".$sth_cm->rows()."]", $LOG) if(defined $LOG);
					$cdi_ids_hash{$id} = $sth_cm->rows();
					$sth_cm->finish;
				}
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%cdi_ids_hash,1), $LOG) if(defined $LOG);



				my @cdi_ids = grep {$cdi_ids_hash{$_}>0} keys(%cdi_ids_hash);
&cgi_lib::common::message("\@cdi_ids=[".join(",",@cdi_ids)."]", $LOG) if(defined $LOG);
				if(scalar @cdi_ids){
					push @bind_values, @cdi_ids;
					$sql .= qq|cm.cdi_id in (|. join(",",map {'?'} @cdi_ids) . ')';
				}else{
					$DATAS->{'success'} = JSON::XS::true;
&cgi_lib::common::message(&cgi_lib::common::encodeJSON($DATAS,1), $LOG) if(defined $LOG);
					&gzip_json($DATAS);
					close($LOG);
					exit;
				}
			}
		}

&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);
&cgi_lib::common::message($sql, $LOG) if(defined $LOG);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\@bind_values), $LOG) if(defined $LOG);

		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute(@bind_values) or die $dbh->errstr;
		$DATAS->{'total'} = $sth->rows();
&cgi_lib::common::message($DATAS->{'total'}, $LOG) if(defined $LOG);
&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);


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
 art_volume,
 art_cube_volume
from
 art_file
where
 art_id=?
SQL
		my $sth_art = $dbh->prepare($sql_art) or die $dbh->errstr;

		my $sql_arto =<<SQL;
select 
 EXTRACT(EPOCH FROM arto_entry) as arto_entry,
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
where
arto.art_id=?
SQL
		my $sth_arto = $dbh->prepare($sql_arto) or die $dbh->errstr;

		my $sql_arta =<<SQL;
select
 EXTRACT(EPOCH FROM art_entry) as art_entry,
 art_comment,
 art_category,
 art_judge,
 art_class
from
 art_annotation
where
 art_id=?
SQL
		my $sth_arta = $dbh->prepare($sql_arta) or die $dbh->errstr;

		my $sql_hart =<<SQL;
select
 max(hist_serial) as art_hist_serial
from
 history_art_file
where
 hist_event in (select he_id from history_event where he_name in ('INSERT','UPDATE')) and
 art_id=?
SQL
		my $sth_hart = $dbh->prepare($sql_hart) or die $dbh->errstr;

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

		my $column_number;
		my $sth_md = $dbh->prepare(qq|select md_abbr from model where md_id=$FORM{'md_id'}|) or die $dbh->errstr;
		$sth_md->execute() or die $dbh->errstr;
		my $md_abbr;
		$column_number = 0;
		$sth_md->bind_col(++$column_number, \$md_abbr, undef);
		$sth_md->fetch;
		$sth_md->finish;
		undef $sth_md;

		my $sth_mv = $dbh->prepare(qq|select mv_name_e from model_version where md_id=$FORM{'md_id'} AND mv_id=$FORM{'mv_id'}|) or die $dbh->errstr;
		$sth_mv->execute() or die $dbh->errstr;
		my $mv_name_e;
		$column_number = 0;
		$sth_mv->bind_col(++$column_number, \$mv_name_e, undef);
		$sth_mv->fetch;
		$sth_mv->finish;
		undef $sth_mv;

		my $sth_bul = $dbh->prepare(qq|select bul_abbr from buildup_logic where bul_id=$FORM{'bul_id'}|) or die $dbh->errstr;
		$sth_bul->execute() or die $dbh->errstr;
		my $bul_abbr;
		$column_number = 0;
		$sth_bul->bind_col(++$column_number, \$bul_abbr, undef);
		$sth_bul->fetch;
		$sth_bul->finish;
		undef $sth_bul;

		my $sth_data = $dbh->prepare(qq|select art_data from history_art_file where art_id=? AND hist_serial=?|) or die $dbh->errstr;


		my $sth_rep = $dbh->prepare(qq|
select
 rep_id,
 EXTRACT(EPOCH FROM rep.rep_entry)
from
 (select rep_id,cdi_id,rep_entry,rep_delcause from representation where (ci_id,cb_id,md_id,mv_id,mr_id,bul_id,cdi_id) in (
   select
    ci_id,cb_id,md_id,mv_id,max(mr_id) as mr_id,bul_id,cdi_id
   from
    representation
   where
    ci_id=$FORM{'ci_id'} AND
    cb_id=$FORM{'cb_id'} AND
    bul_id=$FORM{'bul_id'} AND
    md_id=$FORM{'md_id'} AND
    mv_id=$FORM{'mv_id'} AND
    mr_id<=$FORM{'mr_id'} AND
    cdi_id=?
   GROUP BY
    ci_id,cb_id,md_id,mv_id,bul_id,cdi_id
  ) AND rep_delcause is null
 ) as rep
|) or die $dbh->errstr;

		my $sth_cmm = $dbh->prepare(qq|
select
 cdi_id,
 EXTRACT(EPOCH FROM cm_modified)
from
 (select * from concept_art_map_modified where (md_id,mv_id,mr_id,ci_id,cb_id,bul_id,cdi_id) in
  (
   select md_id,mv_id,max(mr_id),ci_id,cb_id,bul_id,cdi_id from concept_art_map_modified
   where md_id=$FORM{'md_id'} and mv_id=$FORM{'mv_id'} and mr_id<=$FORM{'mr_id'} and ci_id=$FORM{'ci_id'} and cb_id=$FORM{'cb_id'} and bul_id=$FORM{'bul_id'} and cdi_id=?
   group by md_id,mv_id,ci_id,cb_id,bul_id,cdi_id
  )
 ) as cmm
|) or die $dbh->errstr;

		my $sth_seg = $dbh->prepare(qq|
 select
  cd.seg_id,
  seg_name,
  seg_color,
  seg_thum_bgcolor,
  seg_thum_fgcolor
 from
  concept_data as cd

 left join (
  select
   seg_id,
   seg_name,
   seg_color,
   seg_thum_bgcolor,
   seg_thum_fgcolor
  from
   concept_segment
  where
   seg_delcause is null
 ) as cs on
   cs.seg_id=cd.seg_id

 where
  ci_id=$FORM{'ci_id'} AND
  cb_id=$FORM{'cb_id'} AND
  cd_delcause is null AND
  cdi_id=?
|) or die $dbh->errstr;

		my $sth_all_cm_count = $dbh->prepare('select mv_name_e,mv_order from concept_art_map as cm left join (select * from model_version) as mv on (cm.md_id=mv.md_id and cm.mv_id=mv.mv_id) where cm_use and cm_delcause is null and art_id=? group by mv_name_e,mv_order order by mv_order') or die $dbh->errstr;

		my $art_id;
		my $art_name;
		my $art_ext;
		my $artg_name;
		my $arti_entry;
		my $artg_id;
		my $cdi_id;
		my $cdi_name;
		my $cdi_name_e;
		my $cm_id;
		my $cm_use;
		my $cmp_id;
		my $cm_comment;
		my $art_hist_serial;
#		my $rep_id;
#		my $rep_entry;
#		my $cm_max_entry_cdi;
#		my $seg_id;
#		my $seg_name;
#		my $seg_color;
#		my $seg_thum_bgcolor;
#		my $seg_thum_fgcolor;

		$column_number = 0;
		$sth->bind_col(++$column_number, \$art_id,     undef);
		$sth->bind_col(++$column_number, \$art_name,   undef);
		$sth->bind_col(++$column_number, \$art_ext,    undef);
		$sth->bind_col(++$column_number, \$artg_name,  undef);
		$sth->bind_col(++$column_number, \$artg_id,    undef);
		$sth->bind_col(++$column_number, \$arti_entry, undef);


		$sth->bind_col(++$column_number, \$cdi_id,     undef);
		$sth->bind_col(++$column_number, \$cdi_name,   undef);
		$sth->bind_col(++$column_number, \$cdi_name_e, undef);
		$sth->bind_col(++$column_number, \$cm_id,      undef);
		$sth->bind_col(++$column_number, \$cm_use,     undef);
		$sth->bind_col(++$column_number, \$cmp_id,     undef);
		$sth->bind_col(++$column_number, \$cm_comment, undef);
		$sth->bind_col(++$column_number, \$art_hist_serial,  undef);

#		$sth->bind_col(++$column_number, \$rep_id,     undef);
#		$sth->bind_col(++$column_number, \$rep_entry,        undef);
#		$sth->bind_col(++$column_number, \$cm_max_entry_cdi, undef);

#		$sth->bind_col(++$column_number, \$seg_id, undef);
#		$sth->bind_col(++$column_number, \$seg_name, undef);
#		$sth->bind_col(++$column_number, \$seg_color, undef);
#		$sth->bind_col(++$column_number, \$seg_thum_bgcolor, undef);
#		$sth->bind_col(++$column_number, \$seg_thum_fgcolor, undef);

&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

		while($sth->fetch){

			my $rep_id;
			my $rep_entry;
			my $cm_max_entry_cdi;
			my $seg_id;
			my $seg_name;
			my $seg_color;
			my $seg_thum_bgcolor;
			my $seg_thum_fgcolor;
			if(defined $cdi_id){
				$sth_rep->execute($cdi_id) or die $dbh->errstr;
				$column_number = 0;
				$sth_rep->bind_col(++$column_number, \$rep_id,     undef);
				$sth_rep->bind_col(++$column_number, \$rep_entry,        undef);
				$sth_rep->fetch;
				$sth_rep->finish;

				$sth_cmm->execute($cdi_id) or die $dbh->errstr;
				$column_number = 0;
				$sth_cmm->bind_col(++$column_number, \$cm_max_entry_cdi,     undef);
				$sth_cmm->fetch;
				$sth_cmm->finish;

				$sth_seg->execute($cdi_id) or die $dbh->errstr;
				$column_number = 0;
				$sth_seg->bind_col(++$column_number, \$seg_id, undef);
				$sth_seg->bind_col(++$column_number, \$seg_name, undef);
				$sth_seg->bind_col(++$column_number, \$seg_color, undef);
				$sth_seg->bind_col(++$column_number, \$seg_thum_bgcolor, undef);
				$sth_seg->bind_col(++$column_number, \$seg_thum_fgcolor, undef);
				$sth_seg->fetch;
				$sth_seg->finish;
			}

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
			$sth_art->bind_col(++$column_number, \$art_cube_volume, undef);
			$sth_art->fetch;
			$sth_art->finish;

			my $arto_entry;
			my $arto_id;
			my $arto_comment;
			my $arto_name;
			my $arto_ext;
			my $artog_id;
			my $artog_name;
			$sth_arto->execute($art_id) or die $dbh->errstr;
			$column_number = 0;
			$sth_arto->bind_col(++$column_number, \$arto_entry, undef);
			$sth_arto->bind_col(++$column_number, \$arto_id, undef);
			$sth_arto->bind_col(++$column_number, \$arto_comment, undef);
			$sth_arto->bind_col(++$column_number, \$arto_name, undef);
			$sth_arto->bind_col(++$column_number, \$arto_ext, undef);
			$sth_arto->bind_col(++$column_number, \$artog_id, undef);
			$sth_arto->bind_col(++$column_number, \$artog_name, undef);
			$sth_arto->fetch;
			$sth_arto->finish;

			my $arta_entry;
			my $art_comment;
			my $art_mirroring;
			my $art_category;
			my $art_judge;
			my $art_class;
			$sth_arta->execute($art_id) or die $dbh->errstr;
			$column_number = 0;
			$sth_arta->bind_col(++$column_number, \$arta_entry, undef);
			$sth_arta->bind_col(++$column_number, \$art_comment, undef);
			$sth_arta->bind_col(++$column_number, \$art_category, undef);
			$sth_arta->bind_col(++$column_number, \$art_judge, undef);
			$sth_arta->bind_col(++$column_number, \$art_class, undef);
			$sth_arta->fetch;
			$sth_arta->finish;

			unless(defined $art_hist_serial){
				$sth_hart->execute($art_id) or die $dbh->errstr;
				$column_number = 0;
				$sth_hart->bind_col(++$column_number, \$art_hist_serial, undef);
				$sth_hart->fetch;
				$sth_hart->finish;
			}
			$art_hist_serial = 0 unless(defined $art_hist_serial);

#			my $art_modified = &List::Util::max($arti_entry,$art_timestamp,$arta_entry,$arto_entry);
			my @max_timestamp;
			push(@max_timestamp, $arti_entry) if(defined $arti_entry);
			push(@max_timestamp, $art_timestamp) if(defined $art_timestamp);
			push(@max_timestamp, $arta_entry) if(defined $arta_entry);
			push(@max_timestamp, $arto_entry) if(defined $arto_entry);
			my $art_modified = &List::Util::max(@max_timestamp);

			my $file_name = $art_name;
			$file_name .= $art_ext unless($art_name =~ /$art_ext$/);

			my $group_abs_path = &catdir($FindBin::Bin,'art_file');
			my $group_rel_path = &abs2rel($group_abs_path,$FindBin::Bin);

			my $file_path = &catfile($group_abs_path,qq|$art_id-$art_hist_serial$art_ext|);
			my $path = &File::Basename::basename($file_path);

#			&cgi_lib::common::message($file_path, $LOG) if(defined $LOG);
#			&cgi_lib::common::message(&abs2rel($file_path,$FindBin::Bin), $LOG) if(defined $LOG);
#			my $path = &File::Basename::basename(&abs2rel($file_path,$FindBin::Bin));

			if(defined $art_data_size && defined $art_timestamp){
				my($s,$t) = (stat($file_path))[7,9] if(-e $file_path);
				unless($s==$art_data_size && $t==$art_timestamp){
					my $art_data;
					$sth_data->execute($art_id,$art_hist_serial) or die $dbh->errstr;
					$sth_data->bind_col(1, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
					$sth_data->fetch;
					$sth_data->finish;

					if(defined $art_data && open(my $OBJ,"> $file_path")){
						flock($OBJ,2);
						binmode($OBJ);
						print $OBJ $art_data;
						close($OBJ);
						utime $art_timestamp,$art_timestamp,$file_path;
					}
					undef $art_data;
				}
			}

			$sth_all_cm_count->execute($art_id) or die $dbh->errstr;
			my $all_cm_count = $sth_all_cm_count->rows();
			my $all_cm_count_mv_name_e = [];
			if($all_cm_count>0){
				my $mv_name_e;
				$column_number = 0;
				$sth_all_cm_count->bind_col(++$column_number, \$mv_name_e, undef);
				while($sth_all_cm_count->fetch){
					push(@$all_cm_count_mv_name_e,$mv_name_e) if(defined $mv_name_e && length $mv_name_e);
				}
			}
			$sth_all_cm_count->finish;

			my $HASH = {
				art_id   => $art_id,
				art_name => $art_name,
				art_ext => $art_ext,
				artg_name => $artg_name,
				artg_id => $artg_id,
				cdi_id => $cdi_id,
				cdi_name => $cdi_name,
				cdi_name_e => $cdi_name_e,
				cm_id => $cm_id,
				cm_use => $cm_use ? JSON::XS::true : JSON::XS::false,
				cmp_id => defined $cmp_id ? $cmp_id-0 : 0,
				cm_comment => $cm_comment,
				rep_id => $cm_use ? $rep_id : undef,
				art_filename => qq|$art_name$art_ext|,
				filename => qq|$art_name$art_ext|,

				all_cm_count => $all_cm_count,
				all_cm_map_versions => $all_cm_count_mv_name_e,

				use_rep_id => (defined $rep_entry && !defined $cm_max_entry_cdi) ? undef : ((!defined $rep_entry && defined $cm_max_entry_cdi) ? undef : ((defined $rep_entry && defined $cm_max_entry_cdi && $rep_entry < $cm_max_entry_cdi) ? undef : $rep_id)),

				filename => $file_name,
				name => $file_name,
				group => $artg_name,
				grouppath => $group_rel_path,
				path => $path,

				mtime => $art_modified,

				art_timestamp   => $art_timestamp + 0,
				art_modified    => $art_modified,
				art_data_size   => $art_data_size + 0,

				xmin   => $art_xmin + 0,
				xmax   => $art_xmax + 0,
				ymin   => $art_ymin + 0,
				ymax   => $art_ymax + 0,
				zmin   => $art_zmin + 0,
				zmax   => $art_zmax + 0,
				volume => $art_volume + 0,

				xcenter => $art_xcenter + 0,
				ycenter => $art_ycenter + 0,
				zcenter => $art_zcenter + 0,

				art_comment    => $art_comment,
				art_mirroring  => $art_mirroring ? JSON::XS::true : JSON::XS::false,,
				art_category   => $art_category,
				art_judge      => $art_judge,
				art_class      => $art_class,

				arto_id      => $arto_id,
				arto_comment => $arto_comment,
				arto_name    => $arto_name,
				arto_ext     => $arto_ext,
				artog_id     => $artog_id,
				artog_name   => $artog_name,

				md_abbr        => $md_abbr,
				mv_name_e      => $mv_name_e,
				bul_abbr       => $bul_abbr,

				md_id => $FORM{'md_id'}+0,
				mv_id => $FORM{'mv_id'}+0,
				mr_id => $FORM{'mr_id'}+0,
				ci_id => $FORM{'ci_id'}+0,
				cb_id => $FORM{'cb_id'}+0,
				bul_id => $FORM{'bul_id'}+0,

				seg_id => $seg_id,
				seg_name => $seg_name,
				seg_color => $seg_color,
				seg_thum_bgcolor => $seg_thum_bgcolor,
				seg_thum_fgcolor => $seg_thum_fgcolor,
				color => $seg_color

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
