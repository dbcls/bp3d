package BITS::ConceptArtMapModified;

use strict;
use warnings;
use feature ':5.10';
use File::Path;
use JSON::XS;
use Time::HiRes;
use Hash::Diff;
use cgi_lib::common;

use constant {
	DEBUG => 1,
};

#１．最終更新日時をクリア
#２．マッピングの履歴テーブルから、最終更新日時をFMAIDごとに取得
#３．FMAIDにマッピングされているOBJがある場合、その最終更新日時で更新する

#my $dbh = &get_dbh();
#my $rows = $dbh->do(qq|UPDATE concept_art_map_modified SET cm_modified=NULL|) or die $dbh->errstr;
#print qq|[$rows]\n|;

=pod
CREATE OR REPLACE VIEW concept_tree_info
AS
SELECT
 ci_id,
 cb_id,
 cdi_id,
 but_cnum     as cti_cnum,
 but_cids     as cti_cids,
 but_depth    as cti_depth,
 but_pnum     as cti_pnum,
 but_pids     as cti_pids,
 but_delcause as cti_delcause,
 but_entry    as cti_entry,
 but_openid   as cti_openid
FROM
 buildup_tree_info
;
=cut

sub exec {
	my %arg = @_;
	my $dbh    = $arg{'dbh'};
#	my $ci_id  = $arg{'ci_id'};
#	my $cb_id  = $arg{'cb_id'};
#	my $md_id  = $arg{'md_id'};
#	my $mv_id  = $arg{'mv_id'};
#	my $cdi_id = $arg{'cdi_ids'};
	my $use_only_map_terms = $arg{'use_only_map_terms'};
	my $LOG = $arg{'LOG'};
	my $t0 = [&Time::HiRes::gettimeofday()];
#	&cgi_lib::common::dumper(\%arg, $LOG) if(defined $LOG);

	return unless(exists $arg{'md_id'} && defined $arg{'md_id'} && exists $arg{'mv_id'} && defined $arg{'mv_id'});

	unless(exists $arg{'ci_id'} && defined $arg{'ci_id'} && exists $arg{'cb_id'} && defined $arg{'cb_id'}){
		my $sth_mv = $dbh->prepare('SELECT ci_id,cb_id FROM model_version WHERE md_id=? and mv_id=?') or die $dbh->errstr;
		$sth_mv->execute($arg{'md_id'},$arg{'mv_id'}) or die $dbh->errstr;
		my $column_number = 0;
		my $ci_id;
		my $cb_id;
		$sth_mv->bind_col(++$column_number, \$ci_id, undef);
		$sth_mv->bind_col(++$column_number, \$cb_id, undef);
		$sth_mv->fetch;
		$sth_mv->finish;
		undef $sth_mv;
		$arg{'ci_id'} = $ci_id if(defined $ci_id);
		$arg{'cb_id'} = $cb_id if(defined $cb_id);
	}
	return unless(exists $arg{'ci_id'} && defined $arg{'ci_id'} && exists $arg{'cb_id'} && defined $arg{'cb_id'});

	if(exists $arg{'art_ids'} && defined $arg{'art_ids'}){
		my $art_ids;
		unless(ref $arg{'art_ids'} eq 'ARRAY'){
			$art_ids=&cgi_lib::common::decodeJSON($arg{'art_ids'});
		}else{
			$art_ids = $arg{'art_ids'};
		}
		if(defined $art_ids){
			my $cdi_ids = {};
			my $sql_cm = sprintf(qq|
select
 cdi_id
from
 history_concept_art_map
where
 md_id=? AND
 mv_id=? AND
 art_id in (%s)
GROUP BY
 cdi_id
|,join(',',map {'?'} @$art_ids));
			my $sth_cm = $dbh->prepare($sql_cm) or die $dbh->errstr;
			$sth_cm->execute($arg{'md_id'},$arg{'mv_id'},@$art_ids) or die $dbh->errstr;
			my $total = $sth_cm->rows();
			my $column_number = 0;
			my $cdi_id;
			$sth_cm->bind_col(++$column_number, \$cdi_id, undef);
			while($sth_cm->fetch){
				$cdi_ids->{$cdi_id} = undef;
			}
			$sth_cm->finish;
			undef $sth_cm;
			$arg{'cdi_ids'} = [];
			push(@{$arg{'cdi_ids'}},sort {$a<=>$b} keys(%$cdi_ids));
			undef $cdi_ids;
		}
	}

#	&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);
#	&cgi_lib::common::dumper(\%arg, $LOG) if(defined $LOG);


	if(exists $arg{'cdi_names'} && defined $arg{'cdi_names'}){
		my $cdi_names;
		unless(ref $arg{'cdi_names'} eq 'ARRAY'){
			$cdi_names=&cgi_lib::common::decodeJSON($arg{'cdi_names'});
		}else{
			$cdi_names = $arg{'cdi_names'};
		}
		if(defined $cdi_names && ref $cdi_names eq 'ARRAY' && scalar @$cdi_names){
			my $sth_cdi = $dbh->prepare(sprintf(qq|SELECT cdi_id FROM concept_data_info WHERE ci_id=? and cdi_name in (%s)|,join(',',map {'?'} @$cdi_names))) or die $dbh->errstr;
			$sth_cdi->execute($arg{'ci_id'},@$cdi_names) or die $dbh->errstr;
			my $cdi_ids = {};
			my $column_number = 0;
			my $cdi_id;
			$sth_cdi->bind_col(++$column_number, \$cdi_id, undef);
			while($sth_cdi->fetch){
				$cdi_ids->{$cdi_id} = undef;
			}
			$sth_cdi->finish;
			undef $sth_cdi;
			$arg{'cdi_ids'} = [];
			push(@{$arg{'cdi_ids'}},sort {$a<=>$b} keys(%$cdi_ids));
			undef $cdi_ids;
		}
	}

	unless(exists $arg{'cdi_ids'} && defined $arg{'cdi_ids'}){
		my $cdi_ids = {};
		my $sql_cm = qq|
select
 cdi_id
from
 history_concept_art_map
where
 md_id=? AND
 mv_id=?
GROUP BY
 cdi_id
|;
		my $sth_cm = $dbh->prepare($sql_cm) or die $dbh->errstr;
		$sth_cm->execute($arg{'md_id'},$arg{'mv_id'}) or die $dbh->errstr;
		my $total = $sth_cm->rows();
#		&cgi_lib::common::message($total, $LOG) if(defined $LOG);
		my $column_number = 0;
		my $cdi_id;
		$sth_cm->bind_col(++$column_number, \$cdi_id, undef);
		while($sth_cm->fetch){
			$cdi_ids->{$cdi_id} = undef;
		}
		$sth_cm->finish;
		undef $sth_cm;
		$arg{'cdi_ids'} = [];
		push(@{$arg{'cdi_ids'}},sort {$a<=>$b} keys(%$cdi_ids));
		undef $cdi_ids;
	}

	return unless(exists $arg{'cdi_ids'} && defined $arg{'cdi_ids'});

	my %ALL_CM_MODIFIED;

	my @BUL_IDS;
	my $sth_bul = $dbh->prepare(qq|SELECT bul_id FROM buildup_logic WHERE bul_use and bul_delcause is null|) or die $dbh->errstr;
	$sth_bul->execute() or die $dbh->errstr;
	my $column_number = 0;
	my $bul_id;
	$sth_bul->bind_col(++$column_number, \$bul_id, undef);
	while($sth_bul->fetch){
		push(@BUL_IDS, $bul_id);
	}
	$sth_bul->finish;
	undef $sth_bul;

	foreach my $bul_id (@BUL_IDS){
		&cgi_lib::common::message("\$bul_id=[$bul_id]", $LOG) if(defined $LOG);
		my $cdi_ids;
		unless(ref $arg{'cdi_ids'} eq 'ARRAY'){
			$cdi_ids = &cgi_lib::common::decodeJSON($arg{'cdi_ids'});
		}else{
			$cdi_ids = $arg{'cdi_ids'};
		}
		if(defined $cdi_ids && ref $cdi_ids eq 'ARRAY' && scalar @$cdi_ids){
			my $sth_but = $dbh->prepare(sprintf(qq|SELECT cdi_id,but_cids FROM buildup_tree_info WHERE md_id=? and mv_id=? and mr_id=? and bul_id=? and cdi_id in (%s)|,join(',',@$cdi_ids))) or die $dbh->errstr;
			$sth_but->execute($arg{'md_id'},$arg{'mv_id'},$arg{'mr_id'},$bul_id) or die $dbh->errstr;
	#			&cgi_lib::common::message($sth_but->rows(), $LOG) if(defined $LOG);

			my $hash_cdi_ids = {};
			my $column_number = 0;
			my $cdi_id;
			my $cti_cids;
			$sth_but->bind_col(++$column_number, \$cdi_id, undef);
			$sth_but->bind_col(++$column_number, \$cti_cids, undef);
			while($sth_but->fetch){
				$hash_cdi_ids->{$cdi_id} = undef;
				next if(defined $use_only_map_terms);
				if(defined $cti_cids){
					my $cids = &cgi_lib::common::decodeJSON($cti_cids);
					if(defined $cids){
						$hash_cdi_ids->{$_} = undef for(@$cids);
					}
				}
			}
			$sth_but->finish;
			undef $sth_but;
			$cdi_ids = [];
			push(@$cdi_ids,sort {$a<=>$b} keys(%$hash_cdi_ids));
		}

		next unless(defined $cdi_ids && ref $cdi_ids eq 'ARRAY' && scalar @$cdi_ids);

		my $sql_cm = sprintf(qq|
SELECT
 cdi_id,
 MAX(GREATEST(cm_entry,hist_timestamp)),
 EXTRACT(EPOCH FROM MAX(GREATEST(cm_entry,hist_timestamp)))
FROM
 history_concept_art_map
where
 md_id=? AND
 mv_id=? AND
 cdi_id in (%s)
GROUP BY
 cdi_id
ORDER BY
 MAX(GREATEST(cm_entry,hist_timestamp)) ASC,
 cdi_id
|,join(',',@$cdi_ids));
		my $sth_cm = $dbh->prepare($sql_cm) or die $dbh->errstr;

		$sth_cm->execute($arg{'md_id'},$arg{'mv_id'}) or die $dbh->errstr;
		my $total = $sth_cm->rows();
#	&cgi_lib::common::message($total, $LOG) if(defined $LOG);

		my %MAX_CM_MODIFIED;
		my $column_number = 0;
		my $cdi_id;
		my $cm_entry;
		my $cm_entry_epoch;
		$sth_cm->bind_col(++$column_number, \$cdi_id, undef);
		$sth_cm->bind_col(++$column_number, \$cm_entry, undef);
		$sth_cm->bind_col(++$column_number, \$cm_entry_epoch, undef);
		while($sth_cm->fetch){
			$MAX_CM_MODIFIED{$cdi_id} = {
				cm_entry => $cm_entry,
				cm_entry_epoch => $cm_entry_epoch - 0,
				cm_delcause => 'DELETE'
			};
		}
		$sth_cm->finish;
		undef $sth_cm;

#	&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);
		&cgi_lib::common::message(scalar keys(%MAX_CM_MODIFIED), $LOG) if(defined $LOG);
		&cgi_lib::common::message(\%MAX_CM_MODIFIED, $LOG) if(defined $LOG);

		my %CM_MODIFIED;
		my $sth_cti = $dbh->prepare(sprintf(qq|SELECT cdi_id,but_pids FROM buildup_tree_info WHERE md_id=? and mv_id=? and mr_id=? and bul_id=? and cdi_id in (%s)|,join(',',keys(%MAX_CM_MODIFIED)))) or die $dbh->errstr;
		$sth_cti->execute($arg{'md_id'},$arg{'mv_id'},$arg{'mr_id'},$bul_id) or die $dbh->errstr;
		$column_number = 0;
		my $cti_pids;
		$sth_cti->bind_col(++$column_number, \$cdi_id, undef);
		$sth_cti->bind_col(++$column_number, \$cti_pids, undef);
		while($sth_cti->fetch){
			next unless(defined $cdi_id && exists $MAX_CM_MODIFIED{$cdi_id} && defined $MAX_CM_MODIFIED{$cdi_id});
			unless(
				exists  $CM_MODIFIED{$cdi_id} &&
				defined $CM_MODIFIED{$cdi_id} &&
				$CM_MODIFIED{$cdi_id}->{'cm_entry_epoch'} > $MAX_CM_MODIFIED{$cdi_id}->{'cm_entry_epoch'}
			){
				$CM_MODIFIED{$cdi_id}->{'cm_entry'}       = $MAX_CM_MODIFIED{$cdi_id}->{'cm_entry'};
				$CM_MODIFIED{$cdi_id}->{'cm_entry_epoch'} = $MAX_CM_MODIFIED{$cdi_id}->{'cm_entry_epoch'};
				$CM_MODIFIED{$cdi_id}->{'cm_delcause'}    = $MAX_CM_MODIFIED{$cdi_id}->{'cm_delcause'};
			}
			next if(defined $use_only_map_terms);
			next unless(defined $cti_pids);
			my $pids = &cgi_lib::common::decodeJSON($cti_pids);
			next unless(defined $pids && ref $pids eq 'ARRAY');
			foreach my $pid (@$pids){
				unless(
					exists $CM_MODIFIED{$pid} &&
					defined $CM_MODIFIED{$pid} &&
					$CM_MODIFIED{$pid}->{'cm_entry_epoch'} > $MAX_CM_MODIFIED{$cdi_id}->{'cm_entry_epoch'}
				){
					$CM_MODIFIED{$pid}->{'cm_entry'}       = $MAX_CM_MODIFIED{$cdi_id}->{'cm_entry'};
					$CM_MODIFIED{$pid}->{'cm_entry_epoch'} = $MAX_CM_MODIFIED{$cdi_id}->{'cm_entry_epoch'};
					$CM_MODIFIED{$pid}->{'cm_delcause'}    = $MAX_CM_MODIFIED{$cdi_id}->{'cm_delcause'};
				}
			}
		}
		$sth_cti->finish;
		undef $sth_cti;

#	&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);
		&cgi_lib::common::message(scalar keys(%CM_MODIFIED), $LOG) if(defined $LOG);
		&cgi_lib::common::message(\%CM_MODIFIED, $LOG) if(defined $LOG);

		$sth_cti = $dbh->prepare(sprintf(qq|
SELECT
 cdi_id,
 but_pids
FROM
 buildup_tree_info
WHERE
 bul_id=? and
 (md_id,mv_id,mr_id,ci_id,cb_id,cdi_id) IN (
  SELECT
   md_id,
   mv_id,
   mr_id,
   ci_id,
   cb_id,
   cdi_id
  FROM
   concept_art_map
  WHERE
   cm_use AND
   cm_delcause is null AND
   (md_id,mv_id,mr_id,cdi_id) IN (SELECT md_id,mv_id,MAX(mr_id),cdi_id FROM concept_art_map WHERE md_id=? AND mv_id=? AND mr_id<=? AND cdi_id in (%s) GROUP BY md_id,mv_id,cdi_id)
  GROUP BY
   md_id,
   mv_id,
   mr_id,
   ci_id,
   cb_id,
   cdi_id
 )
|,join(',',keys(%MAX_CM_MODIFIED)))) or die $dbh->errstr;
		$sth_cti->execute($bul_id,$arg{'md_id'},$arg{'mv_id'},$arg{'mr_id'}) or die $dbh->errstr;

#	&cgi_lib::common::message($sth_cti->rows(), $LOG) if(defined $LOG);

		$column_number = 0;
		$sth_cti->bind_col(++$column_number, \$cdi_id, undef);
		$sth_cti->bind_col(++$column_number, \$cti_pids, undef);
		while($sth_cti->fetch){
			unless(defined $cdi_id && exists $CM_MODIFIED{$cdi_id} && defined $CM_MODIFIED{$cdi_id}){
				warn __LINE__."\n";
				next;
			}
			$CM_MODIFIED{$cdi_id}->{'cm_delcause'} = undef;
			next if(defined $use_only_map_terms);
			next unless(defined $cti_pids);
			my $pids = &cgi_lib::common::decodeJSON($cti_pids);
			next unless(defined $pids && ref $pids eq 'ARRAY');

			&cgi_lib::common::message("[$cdi_id]$cti_pids", $LOG) if(defined $LOG);

			foreach my $pid (@$pids){
				unless(exists $CM_MODIFIED{$pid} && defined $CM_MODIFIED{$pid}){
					warn __LINE__."\n";
				}else{
					$CM_MODIFIED{$pid}->{'cm_delcause'} = undef;
				}
			}
		}
		$sth_cti->finish;
		undef $sth_cti;

		if(scalar keys(%CM_MODIFIED)){
			my $sth_ct_sel = $dbh->prepare(qq|SELECT cdi_id FROM buildup_tree WHERE ci_id=? AND cb_id=? AND bul_id=? GROUP BY cdi_id|) or die $dbh->errstr;

			my $sth_cmm_sel = $dbh->prepare(qq|SELECT cdi_id FROM concept_art_map_modified WHERE md_id=? AND mv_id=? AND bul_id=?|) or die $dbh->errstr;
			my $sth_cmm_upd = $dbh->prepare(qq|UPDATE concept_art_map_modified SET cm_modified=?,ci_id=?,cb_id=? WHERE md_id=? AND mv_id=? AND mr_id=? AND bul_id=? AND cdi_id=?|) or die $dbh->errstr;
			my $sth_cmm_ins = $dbh->prepare(qq|INSERT INTO concept_art_map_modified (cm_modified,ci_id,cb_id,md_id,mv_id,mr_id,bul_id,cdi_id) VALUES (?,?,?,?,?,?,?,?)|) or die $dbh->errstr;


			my %CMM_CDI_IDS;
			my %EXISTS_CDI_IDS;

			$CMM_CDI_IDS{$bul_id} = {};
			$EXISTS_CDI_IDS{$bul_id} = {};

			my $cdi_id;

			$sth_ct_sel->execute($arg{'ci_id'},$arg{'cb_id'},$bul_id) or die $dbh->errstr;
			$column_number = 0;
			$sth_ct_sel->bind_col(++$column_number, \$cdi_id, undef);
			while($sth_ct_sel->fetch){
				$EXISTS_CDI_IDS{$bul_id}->{$cdi_id} = undef;
			}
			$sth_ct_sel->finish;

			$sth_cmm_sel->execute($arg{'md_id'},$arg{'mv_id'},$bul_id) or die $dbh->errstr;
			$column_number = 0;
			$sth_cmm_sel->bind_col(++$column_number, \$cdi_id, undef);
			while($sth_cmm_sel->fetch){
				$CMM_CDI_IDS{$bul_id}->{$cdi_id} = undef;
			}
			$sth_cmm_sel->finish;


			undef $sth_cmm_sel;
			undef $sth_ct_sel;

			my $all_total = scalar keys(%CM_MODIFIED);
			my $total = 0;

			foreach my $cdi_id (keys(%CM_MODIFIED)){
				$total++;
				if(exists $arg{'callback'} && defined $arg{'callback'}){
					my $callback_value = ($all_total-$total)/$all_total;
					$arg{'callback'}->(int($callback_value*100)/100,$callback_value);
				}
				next if(exists $CM_MODIFIED{$cdi_id}->{'cm_delcause'} && defined $CM_MODIFIED{$cdi_id}->{'cm_delcause'});
				next unless(exists $EXISTS_CDI_IDS{$bul_id}->{$cdi_id});

				if(exists $CMM_CDI_IDS{$bul_id}->{$cdi_id}){
					$sth_cmm_upd->execute($CM_MODIFIED{$cdi_id}->{'cm_entry'},$arg{'ci_id'},$arg{'cb_id'},$arg{'md_id'},$arg{'mv_id'},$arg{'mr_id'},$bul_id,$cdi_id) or die $dbh->errstr;
					$sth_cmm_upd->finish;
				}else{
					$sth_cmm_ins->execute($CM_MODIFIED{$cdi_id}->{'cm_entry'},$arg{'ci_id'},$arg{'cb_id'},$arg{'md_id'},$arg{'mv_id'},$arg{'mr_id'},$bul_id,$cdi_id) or die $dbh->errstr;
					$sth_cmm_ins->finish;
				}

				$ALL_CM_MODIFIED{$cdi_id} = undef;
			}

			undef $sth_cmm_ins;
			undef $sth_cmm_upd;
		}
	}
#	return \%CM_MODIFIED;
#	return;
	return \%ALL_CM_MODIFIED;
}

sub calcElementAndDensity {
	my %arg = @_;
	my $dbh    = $arg{'dbh'};
	my $ci_id  = $arg{'ci_id'};
	my $cb_id  = $arg{'cb_id'};
	my $md_id  = $arg{'md_id'};
	my $mv_id  = $arg{'mv_id'};
	my $mr_id  = $arg{'mr_id'};
	my $crl_id  = $arg{'crl_id'};
	my $bul_id  = $arg{'crl_id'};
	my $cdi_ids  = $arg{'cdi_ids'};
	my $LOG = $arg{'LOG'};
	my $t0 = [&Time::HiRes::gettimeofday()];
#	&cgi_lib::common::dumper(\%arg, $LOG) if(defined $LOG);

	return unless(exists $arg{'md_id'} && defined $arg{'md_id'} && exists $arg{'mv_id'} && defined $arg{'mv_id'});
	unless(exists $arg{'ci_id'} && defined $arg{'ci_id'} && exists $arg{'cb_id'} && defined $arg{'cb_id'}){
		my $sth_mv = $dbh->prepare('SELECT ci_id,cb_id FROM model_version WHERE md_id=? and mv_id=?') or die $dbh->errstr;
		$sth_mv->execute($arg{'md_id'},$arg{'mv_id'}) or die $dbh->errstr;
		my $column_number = 0;
		$sth_mv->bind_col(++$column_number, \$ci_id, undef);
		$sth_mv->bind_col(++$column_number, \$cb_id, undef);
		$sth_mv->fetch;
		$sth_mv->finish;
		undef $sth_mv;
		$arg{'ci_id'} = $ci_id if(defined $ci_id);
		$arg{'cb_id'} = $cb_id if(defined $cb_id);
	}
	return unless(exists $arg{'ci_id'} && defined $arg{'ci_id'} && exists $arg{'cb_id'} && defined $arg{'cb_id'});

	$crl_id = 0 unless(defined $crl_id);

	my $cdi_id;
	my $column_number;
	my $sql;
	my $sth;

	if(defined $cdi_ids && ref $cdi_ids eq 'ARRAY'){
#&cgi_lib::common::message('$cdi_ids=['.(scalar @$cdi_ids).']', $LOG);
		$sql =<<SQL;
select
 cdi_id,
 but_cids
from
 buildup_tree_info
where
 but_delcause is null and
 md_id=$md_id and
 mv_id=$mv_id and
 mr_id=$mr_id and
 bul_id=$bul_id
SQL
		$sql .= sprintf(' and cdi_id in (%s)',join(',',@$cdi_ids));
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$column_number = 0;
		my $cti_cids;
		$sth->bind_col(++$column_number, \$cdi_id, undef);
		$sth->bind_col(++$column_number, \$cti_cids, undef);
		my %IDS;
		while($sth->fetch){
			$IDS{$cdi_id} = undef if(defined $cdi_id);
			if(defined $cti_cids && length $cti_cids){
				$cti_cids = &cgi_lib::common::decodeJSON($cti_cids);
				if(defined $cti_cids && ref $cti_cids eq 'ARRAY'){
					$IDS{$_} = undef for(@$cti_cids);
				}
			}
		}
		$sth->finish;
		undef $sth;
		if(scalar keys(%IDS)){
			$cdi_ids = [keys(%IDS)];
		}else{
			$cdi_ids = undef;
		}
	}
#&cgi_lib::common::message($cdi_ids, $LOG) if(defined $LOG);
#exit;
#&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

	#elementとdensityを取得
	my %CDI_ID2CID;
	my %CDI_ID2PID;
	$sql =<<SQL;
select
 cdi_id,
 but_cids
 ,but_pids
from
 buildup_tree_info
where
 but_delcause is null and
 md_id=$md_id and
 mv_id=$mv_id and
 mr_id=$mr_id and
 bul_id=$bul_id
SQL
	if(defined $cdi_ids && ref $cdi_ids eq 'ARRAY'){
#&cgi_lib::common::message('$cdi_ids=['.(scalar @$cdi_ids).']', $LOG);
		$sql .= sprintf(' and cdi_id in (%s)',join(',',@$cdi_ids));
#&cgi_lib::common::message('$sql=['.$sql.']', $LOG);
	}
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
#&cgi_lib::common::message('$sth->rows()=['.$sth->rows().']', $LOG);
	$column_number = 0;
	my $cti_cids;
	my $cti_pids;
	$sth->bind_col(++$column_number, \$cdi_id, undef);
	$sth->bind_col(++$column_number, \$cti_cids, undef);
	$sth->bind_col(++$column_number, \$cti_pids, undef);
	while($sth->fetch){
		if(exists $CDI_ID2CID{$cdi_id}){
			if(defined $cti_cids && length $cti_cids){
				$CDI_ID2CID{$cdi_id} = [] unless(defined $CDI_ID2CID{$cdi_id});
				push(@{$CDI_ID2CID{$cdi_id}}, @{&cgi_lib::common::decodeJSON($cti_cids)});
			}
		}else{
			if(defined $cti_cids && length $cti_cids){
				$CDI_ID2CID{$cdi_id} = &cgi_lib::common::decodeJSON($cti_cids);
			}else{
				$CDI_ID2CID{$cdi_id} = undef;
			}
		}

		if(exists $CDI_ID2PID{$cdi_id}){
			if(defined $cti_pids && length $cti_pids){
				$CDI_ID2PID{$cdi_id} = [] unless(defined $CDI_ID2PID{$cdi_id});
				push(@{$CDI_ID2PID{$cdi_id}}, @{&cgi_lib::common::decodeJSON($cti_pids)});
			}
		}else{
			if(defined $cti_pids && length $cti_pids){
				$CDI_ID2PID{$cdi_id} = &cgi_lib::common::decodeJSON($cti_pids);
			}else{
				$CDI_ID2PID{$cdi_id} = undef;
			}
		}
	}
	$sth->finish;
	undef $sth;

	my %CDI_ID2PID_HASH;
	foreach my $cdi_id (keys(%CDI_ID2PID)){
		$CDI_ID2PID_HASH{$cdi_id} = {};
		next unless(defined $CDI_ID2PID{$cdi_id} && ref $CDI_ID2PID{$cdi_id} eq 'ARRAY');
		$CDI_ID2PID_HASH{$cdi_id}->{$_} = undef for(@{$CDI_ID2PID{$cdi_id}});
	}

#&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

	my %COMP_DENSITY_ALL_END_TERMS;
	my %COMP_DENSITY_ALL_END_TERM_IDS;
	my %ALL_END_TERMS;
	$sql =<<SQL;
select
 cdi_id
from
 buildup_tree_info
where
 but_cids is null and
 but_delcause is null and
 md_id=$md_id and
 mv_id=$mv_id and
 mr_id=$mr_id and
 bul_id=$bul_id
SQL
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
#&cgi_lib::common::message('$sth->rows()=['.$sth->rows().']', $LOG);
	$column_number = 0;
	$sth->bind_col(++$column_number, \$cdi_id, undef);
	while($sth->fetch){
		$ALL_END_TERMS{$cdi_id} = undef;
	}
	$sth->finish;
	undef $sth;

#&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

	foreach my $cdi_id (keys(%CDI_ID2CID)){
		$COMP_DENSITY_ALL_END_TERMS{$cdi_id} = 0;
		$COMP_DENSITY_ALL_END_TERM_IDS{$cdi_id} = {};
		if(defined $CDI_ID2CID{$cdi_id} && ref $CDI_ID2CID{$cdi_id} eq 'ARRAY'){
			my %HASH = map {$_=>undef} @{$CDI_ID2CID{$cdi_id}};
			foreach my $cdi_cid (keys(%HASH)){
				next unless(exists $ALL_END_TERMS{$cdi_cid});
				$COMP_DENSITY_ALL_END_TERMS{$cdi_id}++;
				$COMP_DENSITY_ALL_END_TERM_IDS{$cdi_id}->{$cdi_cid} = undef;
			}
		}elsif(exists $ALL_END_TERMS{$cdi_id}){
			$COMP_DENSITY_ALL_END_TERMS{$cdi_id} = 1;
			$COMP_DENSITY_ALL_END_TERM_IDS{$cdi_id}->{$cdi_id} = undef;
		}
	}

	undef %ALL_END_TERMS;

#&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);


	my %CDI_MAP;
	my %CDI_MAP_MAX_DATE;
	my %CDI_MAP_ART_DATE;
#	my %CDI_MAP_SUM_VOLUME;
	$sql =<<SQL;
select
 cdi_id,
 EXTRACT(EPOCH FROM max(art_timestamp)::date)
from
 concept_art_map as cm
left join (
  select
   art_id,
   art_timestamp
  from
   art_file_info
) as afi on afi.art_id=cm.art_id
where
 cm_use and
 cm_delcause is null and
 md_id=$md_id and
 mv_id=$mv_id
SQL
	if(defined $cdi_ids && ref $cdi_ids eq 'ARRAY'){
#&cgi_lib::common::message('$cdi_ids=['.(scalar @$cdi_ids).']', $LOG);
		$sql .= sprintf(' and cdi_id in (%s)',join(',',@$cdi_ids));
#&cgi_lib::common::message('$sql=['.$sql.']', $LOG);
	}
	$sql .= ' group by cdi_id';

	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
#	&cgi_lib::common::message('$sth->rows()=['.$sth->rows().']', $LOG)  if(defined $LOG);
	$column_number = 0;
	my $art_timestamp;
#	my $art_volume;
	$sth->bind_col(++$column_number, \$cdi_id, undef);
	$sth->bind_col(++$column_number, \$art_timestamp, undef);
#	$sth->bind_col(++$column_number, \$art_volume, undef);
	while($sth->fetch){
		$CDI_MAP{$cdi_id} = undef;
		$CDI_MAP_MAX_DATE{$cdi_id} = $art_timestamp - 0;
#		$CDI_MAP_SUM_VOLUME{$cdi_id} = $art_volume - 0;
	}
	$sth->finish;
	undef $sth;
#&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

	#子供のOBJより古いOBJを使用している親は削除
	if(0 && scalar keys(%CDI_MAP_MAX_DATE)){
		$sql =<<SQL;
select
 cdi_id,
 cm.art_id,
 EXTRACT(EPOCH FROM art_timestamp::date)
from
 concept_art_map as cm
left join (
  select
   art_id,
   art_timestamp
  from
   art_file_info
) as afi on afi.art_id=cm.art_id
where
 cm_use and
 cm_delcause is null and
 md_id=$md_id and
 mv_id=$mv_id
SQL
		$sql .= sprintf(' and cdi_id in (%s)',join(',',keys(%CDI_MAP_MAX_DATE)));

		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$column_number = 0;
		my $art_id;
		my $art_timestamp;
		$sth->bind_col(++$column_number, \$cdi_id, undef);
		$sth->bind_col(++$column_number, \$art_id, undef);
		$sth->bind_col(++$column_number, \$art_timestamp, undef);
		while($sth->fetch){
			$CDI_MAP_ART_DATE{$cdi_id}->{$art_id} = $art_timestamp - 0;
		}
		$sth->finish;
		undef $sth;
#&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

		if(1){
			$sql =<<SQL;
select
 cdi_id,
 but_pids
from
 buildup_tree_info
where
 but_delcause is null and
 md_id=$md_id and
 mv_id=$mv_id and
 mr_id=$mr_id and
 bul_id=$bul_id
SQL
			$sql .= sprintf(' and cdi_id in (%s)',join(',',keys(%CDI_MAP_MAX_DATE)));
			$sth = $dbh->prepare($sql) or die $dbh->errstr;
			$sth->execute() or die $dbh->errstr;
			$column_number = 0;
			my $cti_pids;
			$sth->bind_col(++$column_number, \$cdi_id, undef);
			$sth->bind_col(++$column_number, \$cti_pids, undef);
			my %IDS;
			while($sth->fetch){
				if(defined $cti_pids && length $cti_pids){
					$cti_pids = &cgi_lib::common::decodeJSON($cti_pids);
					if(defined $cti_pids && ref $cti_pids eq 'ARRAY'){
						foreach my $cti_pid (@$cti_pids){
							if(exists $CDI_MAP_ART_DATE{$cdi_id} && exists $CDI_MAP_MAX_DATE{$cdi_id}){
								foreach my $art_id (keys(%{$CDI_MAP_ART_DATE{$cdi_id}})){
									next if($CDI_MAP_ART_DATE{$cdi_id}->{$art_id}>=$CDI_MAP_MAX_DATE{$cdi_id});
									delete $CDI_MAP_ART_DATE{$cdi_id}->{$art_id};
								}
							}
							if(exists $CDI_MAP_ART_DATE{$cti_pid} && exists $CDI_MAP_MAX_DATE{$cdi_id}){
								foreach my $art_id (keys(%{$CDI_MAP_ART_DATE{$cti_pid}})){
									next if($CDI_MAP_ART_DATE{$cti_pid}->{$art_id}>=$CDI_MAP_MAX_DATE{$cdi_id});
									delete $CDI_MAP_ART_DATE{$cti_pid}->{$art_id};
								}
							}
						}
					}
				}
			}
			$sth->finish;
			undef $sth;

			foreach my $cdi_id (sort {$a <=> $b} keys(%CDI_MAP_ART_DATE)){
				next if(scalar keys(%{$CDI_MAP_ART_DATE{$cdi_id}}));
&cgi_lib::common::message('DELETE:['.$cdi_id.']', $LOG);
die __LINE__;
				delete $CDI_MAP{$cdi_id};
				delete $CDI_MAP_MAX_DATE{$cdi_id};
				delete $CDI_MAP_ART_DATE{$cdi_id};
#				delete $CDI_MAP_SUM_VOLUME{$cdi_id};
			}
		}
	}
#exit;
#&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

	#子供の要素が親の要素の体積の90%より多い場合、親のOBJを除去
=pod
	my %CDI_MAP_SUM_VOLUME_DEL_ID;
	if(scalar keys(%CDI_MAP_SUM_VOLUME)){
		my %CDI_MAP_SUM_VOLUME_P;
		my %CDI_MAP_SUM_VOLUME_C;
		foreach my $cdi_id (sort {$a<=>$b} keys(%CDI_MAP_SUM_VOLUME)){
			$CDI_MAP_SUM_VOLUME_P{$cdi_id} = $CDI_MAP_SUM_VOLUME{$cdi_id};
			$CDI_MAP_SUM_VOLUME_C{$cdi_id} = 0;
			next unless(exists $CDI_ID2CID{$cdi_id} && defined $CDI_ID2CID{$cdi_id} && ref $CDI_ID2CID{$cdi_id} eq 'ARRAY');
			foreach my $cdi_cid (@{$CDI_ID2CID{$cdi_id}}){
				next unless(exists $CDI_MAP_SUM_VOLUME{$cdi_cid} && defined $CDI_MAP_SUM_VOLUME{$cdi_cid});
				$CDI_MAP_SUM_VOLUME_P{$cdi_id} += $CDI_MAP_SUM_VOLUME{$cdi_cid};
				$CDI_MAP_SUM_VOLUME_C{$cdi_id} += $CDI_MAP_SUM_VOLUME{$cdi_cid};
			}
		}

		foreach my $cdi_id (keys(%CDI_MAP_SUM_VOLUME)){
			next unless(exists $CDI_MAP_SUM_VOLUME_C{$cdi_id} && defined $CDI_MAP_SUM_VOLUME_C{$cdi_id} && $CDI_MAP_SUM_VOLUME_C{$cdi_id} > 0);
			next unless(exists $CDI_MAP_SUM_VOLUME_P{$cdi_id} && defined $CDI_MAP_SUM_VOLUME_P{$cdi_id} && $CDI_MAP_SUM_VOLUME_P{$cdi_id} > 0);
			next unless($CDI_MAP_SUM_VOLUME_C{$cdi_id}/$CDI_MAP_SUM_VOLUME_P{$cdi_id}>0.9);
			$CDI_MAP_SUM_VOLUME_DEL_ID{$cdi_id} = $CDI_MAP_SUM_VOLUME_C{$cdi_id}/$CDI_MAP_SUM_VOLUME_P{$cdi_id};
		}
	}
=cut

	#マップされていて子孫が無い場合は、element
	foreach my $cdi_id (keys(%CDI_MAP)){
		unless(exists $CDI_ID2CID{$cdi_id}){
#			die 'Unknown ID '.$cdi_id ;
			&cgi_lib::common::message('Unknown ID '.$cdi_id, $LOG) if(defined $LOG);
			next;
		}
		unless(defined $CDI_ID2CID{$cdi_id}){
			$CDI_MAP{$cdi_id} = 1;
			next;
		}
	}
#&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

	#マップされていて子孫がマップされていない場合も、element
	foreach my $cdi_id (grep {!defined $CDI_MAP{$_}} keys(%CDI_MAP)){
		next unless(defined $CDI_ID2CID{$cdi_id});
		$CDI_MAP{$cdi_id} = 1 unless(scalar grep {exists $CDI_MAP{$_}} @{$CDI_ID2CID{$cdi_id}});
	}
#&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

	my %ELEMENT = map {$_=>undef} grep {defined $CDI_MAP{$_}} keys(%CDI_MAP);
	my %COMP_DENSITY_USE_TERMS;
	my %COMP_DENSITY_END_TERMS;

	my %COMP_DENSITY_USE_TERM_IDS;
	my %COMP_DENSITY_END_TERM_IDS;

	my %COMP_DENSITY;
	foreach my $cdi_id (keys(%CDI_ID2CID)){
		$COMP_DENSITY_USE_TERMS{$cdi_id} = 0;
		$COMP_DENSITY_END_TERMS{$cdi_id} = 0;
		$COMP_DENSITY_USE_TERM_IDS{$cdi_id} = {};
		$COMP_DENSITY_END_TERM_IDS{$cdi_id} = {};
		$COMP_DENSITY{$cdi_id} = 0;
	}
#&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

	#elementの子孫を削除
	foreach my $cdi_id (keys(%ELEMENT)){
		next unless(exists $CDI_ID2CID{$cdi_id} && defined $CDI_ID2CID{$cdi_id});
#		delete $CDI_ID2CID{$_} for(@{$CDI_ID2CID{$cdi_id}});
		foreach my $cdi_cid (@{$CDI_ID2CID{$cdi_id}}){
			next if(exists $CDI_ID2PID_HASH{$cdi_id} && defined $CDI_ID2PID_HASH{$cdi_id} && ref $CDI_ID2PID_HASH{$cdi_id} eq 'HASH' && exists $CDI_ID2PID_HASH{$cdi_id}->{$cdi_cid});
			delete $CDI_ID2CID{$cdi_cid};
		}
		$CDI_ID2CID{$cdi_id} = undef;
	}
#&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);
#&cgi_lib::common::message([sort keys(%CDI_ID2CID)], $LOG) if(defined $LOG);

	foreach my $cdi_id (keys(%CDI_ID2CID)){
		if(defined $CDI_ID2CID{$cdi_id}){
			foreach my $cdi_cid (@{$CDI_ID2CID{$cdi_id}}){
				if(exists $CDI_MAP{$cdi_cid} && defined $CDI_MAP{$cdi_cid}){
					$COMP_DENSITY_USE_TERMS{$cdi_id}++;
					$COMP_DENSITY_USE_TERM_IDS{$cdi_id}->{$cdi_cid} = undef;
				}
				if(exists $CDI_ID2CID{$cdi_cid} && !defined $CDI_ID2CID{$cdi_cid}){
					$COMP_DENSITY_END_TERMS{$cdi_id}++;
					$COMP_DENSITY_END_TERM_IDS{$cdi_id}->{$cdi_cid} = undef;
				}
			}
		}
		if(exists $ELEMENT{$cdi_id}){
			if(exists $CDI_MAP{$cdi_id}){
				$COMP_DENSITY_USE_TERMS{$cdi_id}++;
				$COMP_DENSITY_END_TERMS{$cdi_id}++;

				$COMP_DENSITY_USE_TERM_IDS{$cdi_id}->{$cdi_id} = undef;
				$COMP_DENSITY_END_TERM_IDS{$cdi_id}->{$cdi_id} = undef;
			}
		}
	}
#&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);
#&cgi_lib::common::message(\%COMP_DENSITY_USE_TERM_IDS, $LOG) if(defined $LOG);
#&cgi_lib::common::message(\%COMP_DENSITY_END_TERM_IDS, $LOG) if(defined $LOG);
#&cgi_lib::common::message(\%COMP_DENSITY_ALL_END_TERMS, $LOG) if(defined $LOG);
#&cgi_lib::common::message(\%COMP_DENSITY_ALL_END_TERM_IDS, $LOG) if(defined $LOG);

	foreach my $cdi_id (keys(%COMP_DENSITY_USE_TERMS)){
		next if($COMP_DENSITY_USE_TERMS{$cdi_id} == 0 || $COMP_DENSITY_END_TERMS{$cdi_id} == 0);
		$COMP_DENSITY{$cdi_id} = &Truncated($COMP_DENSITY_USE_TERMS{$cdi_id} / $COMP_DENSITY_END_TERMS{$cdi_id});
	}
#&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

#	return (\%ELEMENT, \%COMP_DENSITY_USE_TERMS, \%COMP_DENSITY_END_TERMS, \%COMP_DENSITY, \%CDI_MAP, \%CDI_MAP_ART_DATE, \%CDI_ID2CID);
	return (\%ELEMENT, \%COMP_DENSITY_USE_TERMS, \%COMP_DENSITY_END_TERMS, \%COMP_DENSITY_USE_TERM_IDS, \%COMP_DENSITY_END_TERM_IDS, \%COMP_DENSITY_ALL_END_TERMS, \%COMP_DENSITY_ALL_END_TERM_IDS);
}

sub Truncated {
	my $v = shift;
	return undef unless(defined $v);
	my $rate = 100000;
	return int($v * $rate + 0.5) / $rate;
}

sub diff {
	my $new_cm_modified = shift;
	my $old_cm_modified = shift;
	my $diff_cm_modified = &Hash::Diff::diff($new_cm_modified,$old_cm_modified);
	undef $diff_cm_modified if(defined $diff_cm_modified && ref $diff_cm_modified eq 'HASH' && scalar keys(%$diff_cm_modified) == 0);
	return $diff_cm_modified;
}

1;
