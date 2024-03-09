package BITS::ConceptArtMapModified;

use strict;
use warnings;
use feature ':5.10';
use File::Path;
use JSON::XS;
use Time::HiRes;
use Hash::Diff;
use cgi_lib::common;
use BITS::Config;

use constant {
	DEBUG => 1,
};

#１．最終更新日時をクリア
#２．マッピングの履歴テーブルから、最終更新日時をFMAIDごとに取得
#３．FMAIDにマッピングされているOBJがある場合、その最終更新日時で更新する

#my $dbh = &get_dbh();
#my $rows = $dbh->do(qq|update concept_art_map_modified set cm_modified=NULL|) or die $dbh->errstr;
#print qq|[$rows]\n|;

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
		my $sth_mv = $dbh->prepare('select ci_id,cb_id from model_version where md_id=? and mv_id=?') or die $dbh->errstr;
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

	$arg{'crl_id'} = 0 unless(exists $arg{'crl_id'} && defined $arg{'crl_id'});

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
			my $sth_cdi = $dbh->prepare(sprintf(qq|select cdi_id from concept_data_info where ci_id=? and cdi_name in (%s)|,join(',',map {'?'} @$cdi_names))) or die $dbh->errstr;
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

	if(exists $arg{'cdi_ids'} && defined $arg{'cdi_ids'}){
		my $sth_but;
		my $cdi_ids;
		unless(ref $arg{'cdi_ids'} eq 'ARRAY'){
			$cdi_ids=&cgi_lib::common::decodeJSON($arg{'cdi_ids'});
		}else{
			$cdi_ids = $arg{'cdi_ids'};
		}
		if(defined $cdi_ids && ref $cdi_ids eq 'ARRAY' && scalar @$cdi_ids){
			$sth_but = $dbh->prepare(sprintf(qq|select cdi_id,cti_cids from concept_tree_info where ci_id=? and cb_id=? and crl_id=? and cdi_id in (%s)|,join(',',@$cdi_ids))) or die $dbh->errstr;
			$sth_but->execute($arg{'ci_id'},$arg{'cb_id'},$arg{'crl_id'}) or die $dbh->errstr;
#			&cgi_lib::common::message($sth_but->rows(), $LOG) if(defined $LOG);
		}
		if(defined $sth_but){
			my $cdi_ids = {};
			my $column_number = 0;
			my $cdi_id;
			my $cti_cids;
			$sth_but->bind_col(++$column_number, \$cdi_id, undef);
			$sth_but->bind_col(++$column_number, \$cti_cids, undef);
			while($sth_but->fetch){
				$cdi_ids->{$cdi_id} = undef;
				next if(defined $use_only_map_terms);
				if(defined $cti_cids){
					my $cids = &cgi_lib::common::decodeJSON($cti_cids);
					if(defined $cids){
						$cdi_ids->{$_} = undef for(@$cids);
					}
				}
			}
			$sth_but->finish;
			undef $sth_but;
			$arg{'cdi_ids'} = [];
			push(@{$arg{'cdi_ids'}},sort {$a<=>$b} keys(%$cdi_ids));
			undef $cdi_ids;
		}
	}

#	&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);
#	&cgi_lib::common::dumper(\%arg, $LOG) if(defined $LOG);
	return unless(exists $arg{'cdi_ids'} && defined $arg{'cdi_ids'} && ref $arg{'cdi_ids'} eq 'ARRAY' && scalar @{$arg{'cdi_ids'}});

	my $cdi_ids_str = join(',',@{$arg{'cdi_ids'}});
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
|,$cdi_ids_str);
	my $sth_cm = $dbh->prepare($sql_cm) or die $dbh->errstr;

#	&cgi_lib::common::message(qq|\$sql_cm=[$sql_cm]|,$LOG) if(defined $LOG);

#	&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

	$sth_cm->execute($arg{'md_id'},$arg{'mv_id'}) or die $dbh->errstr;
	my $total = $sth_cm->rows();
	&cgi_lib::common::message($total, $LOG) if(defined $LOG);

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
#	&cgi_lib::common::message(scalar keys(%MAX_CM_MODIFIED), $LOG) if(defined $LOG);

	my %CM_MODIFIED;
	my $sth_cti = $dbh->prepare(sprintf(qq|select cdi_id,cti_pids from concept_tree_info where ci_id=? and cb_id=? and crl_id=? and cdi_id in (%s)|,join(',',keys(%MAX_CM_MODIFIED)))) or die $dbh->errstr;
	$sth_cti->execute($arg{'ci_id'},$arg{'cb_id'},$arg{'crl_id'}) or die $dbh->errstr;
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
	&cgi_lib::common::message(scalar keys(%MAX_CM_MODIFIED), $LOG) if(defined $LOG);

#	$sth_cti = $dbh->prepare(sprintf(qq|select cdi_id,cti_pids from concept_tree_info where crl_id=? and (ci_id,cb_id,cdi_id) in (select ci_id,cb_id,cdi_id from concept_art_map where cm_use and cm_delcause is null and md_id=? and mv_id=? and cdi_id in (%s) group by ci_id,cb_id,cdi_id)|,join(',',keys(%MAX_CM_MODIFIED)))) or die $dbh->errstr;
#	$sth_cti = $dbh->prepare(sprintf(qq|select cdi_id,cti_pids from concept_tree_info where crl_id=? and (ci_id,cb_id) in (select ci_id,cb_id from model_version where md_id=? and mv_id=?) and (ci_id,cdi_id) in (select ci_id,cdi_id from concept_art_map where cm_use and cm_delcause is null and md_id=? and mv_id=? and cdi_id in (%s) group by ci_id,cb_id,cdi_id)|,join(',',keys(%MAX_CM_MODIFIED)))) or die $dbh->errstr;

	$sth_cti = $dbh->prepare(sprintf(qq|select cdi_id,cti_pids from concept_tree_info where crl_id=%d and ci_id=%d and cb_id=%d and (cdi_id) in (select cdi_id from concept_art_map where cm_use and cm_delcause is null and md_id=%d and mv_id=%d and cdi_id in (%s) group by cdi_id)|,$arg{'crl_id'},$arg{'ci_id'},$arg{'cb_id'},$arg{'md_id'},$arg{'mv_id'},join(',',keys(%MAX_CM_MODIFIED)))) or die $dbh->errstr;

	$sth_cti->execute() or die $dbh->errstr;

	&cgi_lib::common::message($sth_cti->rows(), $LOG) if(defined $LOG);
#die __LINE__;
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

	return \%CM_MODIFIED;
}

sub calcElementAndDensity {
	my %arg = @_;
	my $dbh    = $arg{'dbh'};
	my $ci_id  = $arg{'ci_id'};
	my $cb_id  = $arg{'cb_id'};
	my $md_id  = $arg{'md_id'};
	my $mv_id  = $arg{'mv_id'};
	my $crl_id  = $arg{'crl_id'};
	my $cdi_ids = $arg{'cdi_ids'};
	my $cdi_cids = $arg{'cdi_cids'};
	my $cdi_pids = $arg{'cdi_pids'};
	my $concept_art_map_name = $arg{'concept_art_map_name'};
	my $art_file_info_name = $arg{'art_file_info_name'};
	my $LOG = $arg{'LOG'};
	my $t0 = [&Time::HiRes::gettimeofday()];
#	&cgi_lib::common::dumper(\%arg, $LOG) if(defined $LOG);
#	$CDI_ID2CID = {} unless(defined $CDI_ID2CID && ref $CDI_ID2CID eq 'HASH');
	my $CDI_ID2CID = {};
	my $CDI_ID2PID = {};
	if(defined $cdi_cids && ref $cdi_cids eq 'HASH'){
		foreach my $cdi_pid (keys(%{$cdi_cids})){
			if(exists $cdi_cids->{$cdi_pid} && defined $cdi_cids->{$cdi_pid} && ref $cdi_cids->{$cdi_pid} eq 'ARRAY'){
				push(@{$CDI_ID2CID->{$cdi_pid}}, @{$cdi_cids->{$cdi_pid}});
			}
			else{
				$CDI_ID2CID->{$cdi_pid} = undef;
			}
		}
	}
	if(defined $cdi_pids && ref $cdi_pids eq 'HASH'){
		foreach my $cdi_cid (keys(%{$cdi_pids})){
			$CDI_ID2PID->{$cdi_cid}->{$_} = undef for(keys(%{$cdi_pids->{$cdi_cid}}));
		}
	}
	else{
		foreach my $cdi_pid (keys(%{$CDI_ID2CID})){
			next unless(exists $CDI_ID2CID->{$cdi_pid} && defined $CDI_ID2CID->{$cdi_pid} && ref $CDI_ID2CID->{$cdi_pid} eq 'ARRAY');
			$CDI_ID2PID->{$_}->{$cdi_pid} = undef for(@{$CDI_ID2CID->{$cdi_pid}});
		}
	}
&cgi_lib::common::message($CDI_ID2CID, $LOG) if(defined $LOG);

	$concept_art_map_name = 'concept_art_map' unless(defined $concept_art_map_name && length $concept_art_map_name);
	$art_file_info_name = 'art_file_info' unless(defined $art_file_info_name && length $art_file_info_name);

	return unless(exists $arg{'md_id'} && defined $arg{'md_id'} && exists $arg{'mv_id'} && defined $arg{'mv_id'});
	unless(exists $arg{'ci_id'} && defined $arg{'ci_id'} && exists $arg{'cb_id'} && defined $arg{'cb_id'}){
		my $sth_mv = $dbh->prepare('select ci_id,cb_id from model_version where md_id=? and mv_id=?') or die $dbh->errstr;
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
#	$crl_id = 4;	#part_ofに固定　https://www.evernote.com/shard/s10/client/snv?noteGuid=9ef677a4-077c-9c51-9655-cf872b417247&noteKey=8dab1dff6b6233a57a9398efe56711e3&sn=https%3A%2F%2Fwww.evernote.com%2Fshard%2Fs10%2Fsh%2F9ef677a4-077c-9c51-9655-cf872b417247%2F8dab1dff6b6233a57a9398efe56711e3&title=Current%2B%25E4%25BD%259C%25E6%2588%2590%252F%25E4%25B8%258A%25E4%25BD%258D%25E6%25A6%2582%25E5%25BF%25B5%25E8%25A1%25A8%25E7%25A4%25BA%25E7%2594%25A8%25E3%2580%2580%25E6%25A6%2582%25E5%25BF%25B5%25E3%2583%2584%25E3%2583%25AA%25E3%2583%25BC%25E4%25BD%259C%25E6%2588%2590%25E4%25BE%259D%25E9%25A0%25BC%25E3%2580%25802021Feb08

#&cgi_lib::common::message('$md_id=['.$arg{md_id}.']', $LOG);
#&cgi_lib::common::message('$mv_id=['.$arg{mv_id}.']', $LOG);
#&cgi_lib::common::message('$ci_id=['.$arg{ci_id}.']', $LOG);
#&cgi_lib::common::message('$cb_id=['.$arg{cb_id}.']', $LOG);

	my $cdi_id;
	my $column_number;
	my $sql;
	my $sth;

	if(defined $cdi_ids && ref $cdi_ids eq 'ARRAY'){
#&cgi_lib::common::message('$cdi_ids=['.(scalar @$cdi_ids).']', $LOG);
		$sql =<<SQL;
select
cdi_id,
cti_cids
from
concept_tree_info
where
cti_delcause is null and
ci_id=$ci_id and
cb_id=$cb_id and
crl_id=$crl_id
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

		foreach my $cdi_id (keys(%{$CDI_ID2CID})){
			next unless(exists $CDI_ID2CID->{$cdi_id} && defined $CDI_ID2CID->{$cdi_id} && ref $CDI_ID2CID->{$cdi_id} eq 'ARRAY');
			foreach my $cdi_cid (@{$CDI_ID2CID->{$cdi_id}}){
				$IDS{$cdi_cid} = undef;
			}
		}

		if(scalar keys(%IDS)){
			$cdi_ids = [map {$_-0} keys(%IDS)];
		}else{
			$cdi_ids = undef;
		}
	}
&cgi_lib::common::message($cdi_ids, $LOG) if(defined $LOG);
#exit;
&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

	#elementとdensityを取得
#	my $CDI_ID2CID = {};
#	my %CDI_ID2PID;
	$sql =<<SQL;
select
 cdi_id,
 cti_cids
 ,cti_pids
from
 concept_tree_info
where
 cti_delcause is null and
 ci_id=$ci_id and
 cb_id=$cb_id and
 crl_id=$crl_id
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
		if(exists $CDI_ID2CID->{$cdi_id}){
			if(defined $cti_cids && length $cti_cids){
				$CDI_ID2CID->{$cdi_id} = [] unless(defined $CDI_ID2CID->{$cdi_id});
				push(@{$CDI_ID2CID->{$cdi_id}}, @{&cgi_lib::common::decodeJSON($cti_cids)});
				my %hash;
				$CDI_ID2CID->{$cdi_id} = [map {$_-0} sort {$a<=>$b} grep{!$hash{$_}++} @{$CDI_ID2CID->{$cdi_id}}];
			}
		}else{
			if(defined $cti_cids && length $cti_cids){
				$CDI_ID2CID->{$cdi_id} = &cgi_lib::common::decodeJSON($cti_cids);
			}else{
				$CDI_ID2CID->{$cdi_id} = undef;
			}
		}

		if(exists $CDI_ID2PID->{$cdi_id}){
			if(defined $cti_pids && length $cti_pids){
				$CDI_ID2PID->{$cdi_id} = {} unless(defined $CDI_ID2PID->{$cdi_id});
				$CDI_ID2PID->{$cdi_id}->{$_} = undef for(@{&cgi_lib::common::decodeJSON($cti_pids)});
			}
		}else{
			if(defined $cti_pids && length $cti_pids){
				$CDI_ID2PID->{$cdi_id}->{$_} = undef for(@{&cgi_lib::common::decodeJSON($cti_pids)});
			}else{
				$CDI_ID2PID->{$cdi_id} = undef;
			}
		}
	}
	$sth->finish;
	undef $sth;
&cgi_lib::common::message($CDI_ID2CID, $LOG) if(defined $LOG);
&cgi_lib::common::message($CDI_ID2PID, $LOG) if(defined $LOG);

	my %CDI_ID2PID_HASH;
	foreach my $cdi_id (keys(%{$CDI_ID2PID})){
		$CDI_ID2PID_HASH{$cdi_id} = {};
		next unless(defined $CDI_ID2PID->{$cdi_id});
		if(ref $CDI_ID2PID->{$cdi_id} eq 'ARRAY'){
			$CDI_ID2PID_HASH{$cdi_id}->{$_} = undef for(@{$CDI_ID2PID->{$cdi_id}});
		}
		elsif(ref $CDI_ID2PID->{$cdi_id} eq 'HASH'){
			$CDI_ID2PID_HASH{$cdi_id}->{$_} = undef for(keys(%{$CDI_ID2PID->{$cdi_id}}));
		}
	}
&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

#&cgi_lib::common::message('%CDI_ID2CID=['.(scalar keys(%CDI_ID2CID)).']', $LOG);
#&cgi_lib::common::message('exists  2203:%CDI_ID2CID=['.(exists $CDI_ID2CID->{'2203'} ? 1 : 0).']', $LOG);
#&cgi_lib::common::message('defined 2203:%CDI_ID2CID=['.(defined $CDI_ID2CID->{'2203'} ? 1 : 0).']', $LOG) if(exists $CDI_ID2CID->{'2203'});
#&cgi_lib::common::message('exists  46048:%CDI_ID2CID=['.(exists $CDI_ID2CID->{'46048'} ? 1 : 0).']', $LOG);
#&cgi_lib::common::message('defined 46048:%CDI_ID2CID=['.(defined $CDI_ID2CID->{'46048'} ? 1 : 0).']', $LOG) if(exists $CDI_ID2CID->{'46048'});


	my %CDI_MAP;
	my %CDI_MAP_MAX_DATE;
	my %CDI_MAP_ART_DATE;
	my %CDI_MAP_SUM_VOLUME;

#	my $max_art_timestamp_column = 'EXTRACT(EPOCH FROM max(art_timestamp))';
#	$max_art_timestamp_column = 'EXTRACT(EPOCH FROM max(art_timestamp)::date)' if(&BITS::Config::USE_OBJ_TIMESTAMP_COMPARISON_UNIT() eq &BITS::Config::USE_OBJ_TIMESTAMP_COMPARISON_UNIT_DATE());
	my $max_art_timestamp_column = 'EXTRACT(EPOCH FROM art_timestamp)';
	$max_art_timestamp_column = 'EXTRACT(EPOCH FROM art_timestamp::date)' if(&BITS::Config::USE_OBJ_TIMESTAMP_COMPARISON_UNIT() eq &BITS::Config::USE_OBJ_TIMESTAMP_COMPARISON_UNIT_DATE());

	$sql =<<SQL;
select
 cdi_id,
 $max_art_timestamp_column,
-- sum(art_volume)
 art_volume
from
-- concept_art_map as cm
 $concept_art_map_name as cm
left join (
  select
   art_id,
   art_timestamp,
   art_volume
  from
--   art_file_info
   $art_file_info_name
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
#	$sql .= ' group by cdi_id';
	$sql .= ' order by cdi_id ASC, art_timestamp DESC';

	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
#	&cgi_lib::common::message('$sth->rows()=['.$sth->rows().']', $LOG)  if(defined $LOG);
	$column_number = 0;
	my $art_timestamp;
	my $art_volume;
	$sth->bind_col(++$column_number, \$cdi_id, undef);
	$sth->bind_col(++$column_number, \$art_timestamp, undef);
	$sth->bind_col(++$column_number, \$art_volume, undef);
	while($sth->fetch){
		next if(exists $CDI_MAP{$cdi_id});
		$CDI_MAP{$cdi_id} = undef;
		$CDI_MAP_MAX_DATE{$cdi_id} = $art_timestamp - 0;
		$CDI_MAP_SUM_VOLUME{$cdi_id} = $art_volume - 0;
	}
	$sth->finish;
	undef $sth;
&cgi_lib::common::message(\%CDI_MAP_MAX_DATE, $LOG) if(defined $LOG);
&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

	#子供のOBJより古いOBJを使用している親は削除
	my %CDI_DESC_OBJ_OLD_DEL_ID;
	if(scalar keys(%CDI_MAP_MAX_DATE)){
		my $art_timestamp_column = 'EXTRACT(EPOCH FROM art_timestamp)';
		$art_timestamp_column = 'EXTRACT(EPOCH FROM art_timestamp::date)' if(&BITS::Config::USE_OBJ_TIMESTAMP_COMPARISON_UNIT() eq &BITS::Config::USE_OBJ_TIMESTAMP_COMPARISON_UNIT_DATE());
		$sql =<<SQL;
select
 cdi_id,
 cm.art_id,
 $art_timestamp_column
from
-- concept_art_map as cm
 $concept_art_map_name as cm
left join (
  select
   art_id,
   art_timestamp
  from
--   art_file_info
   $art_file_info_name
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
&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

		if(1){
			$sql =<<SQL;
select
cdi_id,
cti_pids
from
concept_tree_info
where
cti_delcause is null and
ci_id=$ci_id and
cb_id=$cb_id 
and crl_id=$crl_id
SQL
			$sql .= sprintf(' and cdi_id in (%s)',join(',',keys(%CDI_MAP_MAX_DATE)));
			$sth = $dbh->prepare($sql) or die $dbh->errstr;
			$sth->execute() or die $dbh->errstr;
			$column_number = 0;
			my $cti_pids;
			$sth->bind_col(++$column_number, \$cdi_id, undef);
			$sth->bind_col(++$column_number, \$cti_pids, undef);
			my $CTI_PIDS = {};
			while($sth->fetch){
				next unless(defined $cti_pids && length $cti_pids);
				$CTI_PIDS->{$cdi_id} = &cgi_lib::common::decodeJSON($cti_pids);
			}
			$sth->finish;
			undef $sth;

			foreach my $cdi_id (keys(%CDI_MAP_MAX_DATE)){
				my $cti_pids;
				if(exists $CTI_PIDS->{$cdi_id} && defined $CTI_PIDS->{$cdi_id}){
					$cti_pids = $CTI_PIDS->{$cdi_id};
				}
				elsif($crl_id==4 && exists $CDI_ID2PID->{$cdi_id} && defined $CDI_ID2PID->{$cdi_id} && ref $CDI_ID2PID->{$cdi_id} eq 'HASH'){
					push(@{$cti_pids}, keys(%{$CDI_ID2PID->{$cdi_id}}));
				}
				next unless(defined $cti_pids && ref $cti_pids eq 'ARRAY');

				foreach my $cti_pid (@$cti_pids){
					if(exists $CDI_MAP_ART_DATE{$cdi_id} && exists $CDI_MAP_MAX_DATE{$cdi_id}){
						foreach my $art_id (keys(%{$CDI_MAP_ART_DATE{$cdi_id}})){
							next if($CDI_MAP_ART_DATE{$cdi_id}->{$art_id}>=$CDI_MAP_MAX_DATE{$cdi_id});
&cgi_lib::common::message(sprintf("delete \$CDI_MAP_ART_DATE{%s}->{%s}=%s < %s : %s",$cdi_id,$art_id,$CDI_MAP_ART_DATE{$cdi_id}->{$art_id},$CDI_MAP_MAX_DATE{$cdi_id},$cdi_id), $LOG) if(defined $LOG);
							$CDI_DESC_OBJ_OLD_DEL_ID{$cdi_id}->{$art_id} = {
								del_art_id => $art_id,
								del_art_timestamp => $CDI_MAP_ART_DATE{$cdi_id}->{$art_id},
								del_cdi_id => $cdi_id,
								max_cdi_id => $cdi_id,
								max_art_timestamp => $CDI_MAP_MAX_DATE{$cdi_id}
							};
							delete $CDI_MAP_ART_DATE{$cdi_id}->{$art_id};
						}
					}
					if(exists $CDI_MAP_ART_DATE{$cti_pid} && exists $CDI_MAP_MAX_DATE{$cdi_id}){
						foreach my $art_id (keys(%{$CDI_MAP_ART_DATE{$cti_pid}})){
							next if($CDI_MAP_ART_DATE{$cti_pid}->{$art_id}>=$CDI_MAP_MAX_DATE{$cdi_id});
&cgi_lib::common::message(sprintf("delete \$CDI_MAP_ART_DATE{%s}->{%s}=%s < %s : %s",$cti_pid,$art_id,$CDI_MAP_ART_DATE{$cti_pid}->{$art_id},$CDI_MAP_MAX_DATE{$cdi_id},$cdi_id), $LOG) if(defined $LOG);
							$CDI_DESC_OBJ_OLD_DEL_ID{$cti_pid}->{$art_id} = {
								del_art_id => $art_id,
								del_art_timestamp => $CDI_MAP_ART_DATE{$cti_pid}->{$art_id},
								del_cdi_id => $cti_pid,
								max_cdi_id => $cdi_id,
								max_art_timestamp => $CDI_MAP_MAX_DATE{$cdi_id}
							};
							delete $CDI_MAP_ART_DATE{$cti_pid}->{$art_id};
						}
					}
				}
			}



			foreach my $cdi_id (sort {$a <=> $b} keys(%CDI_MAP_ART_DATE)){
				next if(scalar keys(%{$CDI_MAP_ART_DATE{$cdi_id}}));
#&cgi_lib::common::message('DELETE:['.$cdi_id.']', $LOG);
				delete $CDI_MAP{$cdi_id};
				delete $CDI_MAP_MAX_DATE{$cdi_id};
				delete $CDI_MAP_ART_DATE{$cdi_id};
				delete $CDI_MAP_SUM_VOLUME{$cdi_id};
			}
		}
	}
#exit;
&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

	#子供の要素が親の要素の体積の90%より多い場合、親のOBJを除去
	my %CDI_MAP_SUM_VOLUME_DEL_ID;
	if(scalar keys(%CDI_MAP_SUM_VOLUME)){
=pod
		my %CDI_ID2NAME;
		my %CDI_NAME2ID;
		if(1){
			my $sth_cdi = $dbh->prepare(qq|select cdi_id,cdi_name from concept_data_info where cdi_delcause is null and ci_id=$ci_id|) or die $dbh->errstr;
			$sth_cdi->execute() or die $dbh->errstr;
			$column_number = 0;
			my $cdi_id;
			my $cdi_name;
			$sth_cdi->bind_col(++$column_number, \$cdi_id, undef);
			$sth_cdi->bind_col(++$column_number, \$cdi_name, undef);
			while($sth_cdi->fetch){
				$CDI_ID2NAME{$cdi_id} = $cdi_name;
				$CDI_NAME2ID{$cdi_name} = $cdi_id;
			}
			$sth_cdi->finish;
			undef $sth_cdi;
		}
=cut

#&cgi_lib::common::message('%CDI_MAP_SUM_VOLUME=['.(scalar keys(%CDI_MAP_SUM_VOLUME)).']', $LOG);
#&cgi_lib::common::message('$crl_id=['.$crl_id.']', $LOG);
#say $LOG '';

		my %CDI_MAP_SUM_VOLUME_P;
		my %CDI_MAP_SUM_VOLUME_C;
		foreach my $cdi_id (sort {$a<=>$b} keys(%CDI_MAP_SUM_VOLUME)){
			$CDI_MAP_SUM_VOLUME_P{$cdi_id} = $CDI_MAP_SUM_VOLUME{$cdi_id};
			$CDI_MAP_SUM_VOLUME_C{$cdi_id} = 0;
			next unless(exists $CDI_ID2CID->{$cdi_id} && defined $CDI_ID2CID->{$cdi_id} && ref $CDI_ID2CID->{$cdi_id} eq 'ARRAY');
			foreach my $cdi_cid (@{$CDI_ID2CID->{$cdi_id}}){
				next unless(exists $CDI_MAP_SUM_VOLUME{$cdi_cid} && defined $CDI_MAP_SUM_VOLUME{$cdi_cid});
				$CDI_MAP_SUM_VOLUME_P{$cdi_id} += $CDI_MAP_SUM_VOLUME{$cdi_cid};
				$CDI_MAP_SUM_VOLUME_C{$cdi_id} += $CDI_MAP_SUM_VOLUME{$cdi_cid};
			}
		}


		foreach my $cdi_id (keys(%CDI_MAP_SUM_VOLUME)){
			next unless(exists $CDI_MAP_SUM_VOLUME_C{$cdi_id} && defined $CDI_MAP_SUM_VOLUME_C{$cdi_id} && $CDI_MAP_SUM_VOLUME_C{$cdi_id} > 0);
			next unless(exists $CDI_MAP_SUM_VOLUME_P{$cdi_id} && defined $CDI_MAP_SUM_VOLUME_P{$cdi_id} && $CDI_MAP_SUM_VOLUME_P{$cdi_id} > 0);
			next unless($CDI_MAP_SUM_VOLUME_C{$cdi_id}/$CDI_MAP_SUM_VOLUME_P{$cdi_id}>0.9);
#			&cgi_lib::common::message('$cdi_id=['.$cdi_id.']['.$CDI_ID2NAME{$cdi_id}.']', $LOG);
#			&cgi_lib::common::message('$CDI_MAP_SUM_VOLUME_C{'.$cdi_id.'}=['.$CDI_MAP_SUM_VOLUME_C{$cdi_id}.']', $LOG);
#			&cgi_lib::common::message('$CDI_MAP_SUM_VOLUME_P{'.$cdi_id.'}=['.$CDI_MAP_SUM_VOLUME_P{$cdi_id}.']', $LOG);
#			&cgi_lib::common::message('C/P=['.$CDI_MAP_SUM_VOLUME_C{$cdi_id}/$CDI_MAP_SUM_VOLUME_P{$cdi_id}.']', $LOG);
#			say $LOG '';
			$CDI_MAP_SUM_VOLUME_DEL_ID{$cdi_id} = $CDI_MAP_SUM_VOLUME_C{$cdi_id}/$CDI_MAP_SUM_VOLUME_P{$cdi_id};
		}
#		&cgi_lib::common::message(join(',',sort {$a<=>$b} keys(%CDI_MAP_SUM_VOLUME_DEL_ID)), $LOG) if(defined $LOG);
	}

#&cgi_lib::common::message('%CDI_MAP=['.(scalar keys(%CDI_MAP)).']', $LOG);
#&cgi_lib::common::message('exists  46048:%CDI_MAP=['.(exists $CDI_MAP{'46048'} ? 1 : 0).']', $LOG);
#&cgi_lib::common::message('defined 46048:%CDI_MAP=['.(defined $CDI_MAP{'46048'} ? 1 : 0).']', $LOG) if(exists $CDI_MAP{'46048'});

	#マップされていて子孫が無い場合は、element
	foreach my $cdi_id (keys(%CDI_MAP)){
		unless(exists $CDI_ID2CID->{$cdi_id}){
#			die 'Unknown ID '.$cdi_id ;
			&cgi_lib::common::message('Unknown ID '.$cdi_id, $LOG) if(defined $LOG);
			next;
		}
		unless(defined $CDI_ID2CID->{$cdi_id}){
			$CDI_MAP{$cdi_id} = 1;
			next;
		}
	}
&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

#&cgi_lib::common::message('%CDI_MAP=['.(scalar grep {defined $CDI_MAP{$_}} keys(%CDI_MAP)).']', $LOG);
#&cgi_lib::common::message('exists  46048:%CDI_MAP=['.(exists $CDI_MAP{'46048'} ? 1 : 0).']', $LOG);
#&cgi_lib::common::message('defined 46048:%CDI_MAP=['.(defined $CDI_MAP{'46048'} ? 1 : 0).']', $LOG) if(exists $CDI_MAP{'46048'});

	#マップされていて子孫がマップされていない場合も、element
	foreach my $cdi_id (grep {!defined $CDI_MAP{$_}} keys(%CDI_MAP)){
		next unless(defined $CDI_ID2CID->{$cdi_id});
		$CDI_MAP{$cdi_id} = 1 unless(scalar grep {exists $CDI_MAP{$_}} @{$CDI_ID2CID->{$cdi_id}});
	}
&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

#exit;

#&cgi_lib::common::message('%CDI_MAP=['.(scalar grep {defined $CDI_MAP{$_}} keys(%CDI_MAP)).']', $LOG);
#&cgi_lib::common::message('exists  46048:%CDI_MAP=['.(exists $CDI_MAP{'46048'} ? 1 : 0).']', $LOG);
#&cgi_lib::common::message('defined 46048:%CDI_MAP=['.(defined $CDI_MAP{'46048'} ? 1 : 0).']', $LOG) if(exists $CDI_MAP{'46048'});
#&cgi_lib::common::message('defined 46048:%CDI_ID2CID=['.(defined $CDI_ID2CID->{'46048'} ? (join(',',@{$CDI_ID2CID->{'46048'}})) : 0).']', $LOG) if(exists $CDI_ID2CID->{'46048'});


	my %ELEMENT = map {$_=>undef} grep {defined $CDI_MAP{$_}} keys(%CDI_MAP);
	my %COMP_DENSITY_USE_TERMS;
	my %COMP_DENSITY_END_TERMS;
	my %COMP_DENSITY;
	foreach my $cdi_id (keys(%{$CDI_ID2CID})){
		$COMP_DENSITY_USE_TERMS{$cdi_id} = 0;
		$COMP_DENSITY_END_TERMS{$cdi_id} = 0;
		$COMP_DENSITY{$cdi_id} = 0;
	}
&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);


#&cgi_lib::common::message('exists  2203:%COMP_DENSITY=['.(exists $COMP_DENSITY{'2203'} ? 1 : 0).']', $LOG);
#&cgi_lib::common::message('defined 2203:%COMP_DENSITY=['.(defined $COMP_DENSITY{'2203'} ? 1 : 0).']', $LOG) if(exists $COMP_DENSITY{'2203'});

	#elementの子孫を削除
	foreach my $cdi_id (keys(%ELEMENT)){
		next unless(exists $CDI_ID2CID->{$cdi_id} && defined $CDI_ID2CID->{$cdi_id});
#		delete $CDI_ID2CID->{$_} for(@{$CDI_ID2CID->{$cdi_id}});
		foreach my $cdi_cid (@{$CDI_ID2CID->{$cdi_id}}){
			next if(exists $CDI_ID2PID_HASH{$cdi_id} && defined $CDI_ID2PID_HASH{$cdi_id} && ref $CDI_ID2PID_HASH{$cdi_id} eq 'HASH' && exists $CDI_ID2PID_HASH{$cdi_id}->{$cdi_cid});
			delete $CDI_ID2CID->{$cdi_cid};
		}
		$CDI_ID2CID->{$cdi_id} = undef;
	}
&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

#&cgi_lib::common::message('exists  2203:%CDI_ID2CID=['.(exists $CDI_ID2CID->{'2203'} ? 1 : 0).']', $LOG);
#&cgi_lib::common::message('defined 2203:%CDI_ID2CID=['.(defined $CDI_ID2CID->{'2203'} ? (scalar @{$CDI_ID2CID->{'2203'}}) : 0).']', $LOG) if(exists $CDI_ID2CID->{'2203'});
#&cgi_lib::common::message('defined 2203:%CDI_ID2CID=['.(defined $CDI_ID2CID->{'2203'} ? (join(',',@{$CDI_ID2CID->{'2203'}})) : 0).']', $LOG) if(exists $CDI_ID2CID->{'2203'});

&cgi_lib::common::message($CDI_ID2CID, $LOG) if(defined $LOG);

	foreach my $cdi_id (keys(%{$CDI_ID2CID})){
		if(defined $CDI_ID2CID->{$cdi_id}){
			foreach my $cdi_cid (@{$CDI_ID2CID->{$cdi_id}}){
#				say $cdi_cid if($cdi_id==2203);
				$COMP_DENSITY_USE_TERMS{$cdi_id}++ if(exists $CDI_MAP{$cdi_cid} && defined $CDI_MAP{$cdi_cid});
				$COMP_DENSITY_END_TERMS{$cdi_id}++ if(exists $CDI_ID2CID->{$cdi_cid} && !defined $CDI_ID2CID->{$cdi_cid});
			}
		}
		if(exists $ELEMENT{$cdi_id}){
			if(exists $CDI_MAP{$cdi_id}){
				$COMP_DENSITY_USE_TERMS{$cdi_id}++;
				$COMP_DENSITY_END_TERMS{$cdi_id}++;
			}
		}
	}
&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

=pod
	#互いに子供の場合も、とりあえずelementにする？
	foreach my $cdi_id (grep {!defined $CDI_MAP{$_}} keys(%CDI_MAP)){
		next unless(defined $CDI_ID2CID->{$cdi_id});
		foreach my $cdi_cid (grep {exists $CDI_MAP{$_} && !defined $CDI_MAP{$_}} @{$CDI_ID2CID->{$cdi_id}}){
#&cgi_lib::common::message('['.$cdi_id.']['.$cdi_cid.']', $LOG);
			$CDI_MAP{$cdi_id} = $CDI_MAP{$cdi_cid} = 1;
			$ELEMENT{$cdi_id} = 1;
			$ELEMENT{$cdi_cid} = 1;

			$COMP_DENSITY_USE_TERMS{$cdi_id}=1;
			$COMP_DENSITY_END_TERMS{$cdi_id}=1;
			$COMP_DENSITY_USE_TERMS{$cdi_cid}=1;
			$COMP_DENSITY_END_TERMS{$cdi_cid}=1;
		}
	}
=cut

	foreach my $cdi_id (keys(%COMP_DENSITY_USE_TERMS)){
		next if($COMP_DENSITY_USE_TERMS{$cdi_id} == 0 || $COMP_DENSITY_END_TERMS{$cdi_id} == 0);
		$COMP_DENSITY{$cdi_id} = &Truncated($COMP_DENSITY_USE_TERMS{$cdi_id} / $COMP_DENSITY_END_TERMS{$cdi_id});
	}
&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

#	undef %CDI_ID2CID;
#	undef %CDI_MAP;

#&cgi_lib::common::message('%CDI_MAP=['.(scalar keys(%CDI_MAP)).']['.(scalar grep {defined $CDI_MAP{$_}} keys(%CDI_MAP)).']', $LOG);
#&cgi_lib::common::message('%ELEMENT=['.(scalar keys(%ELEMENT)).']', $LOG);
#&cgi_lib::common::message('%COMP_DENSITY_USE_TERMS=['.(scalar keys(%COMP_DENSITY_USE_TERMS)).']', $LOG);
#&cgi_lib::common::message('%COMP_DENSITY_END_TERMS=['.(scalar keys(%COMP_DENSITY_END_TERMS)).']', $LOG);
#&cgi_lib::common::message('%COMP_DENSITY=['.(scalar keys(%COMP_DENSITY)).']', $LOG);
#&cgi_lib::common::message('%COMP_DENSITY=['.(scalar grep {!exists $ELEMENT{$_} && defined $COMP_DENSITY{$_} && $COMP_DENSITY{$_}>0} keys(%COMP_DENSITY)).']', $LOG);
#&cgi_lib::common::message('%COMP_DENSITY=['.(scalar grep {!exists $ELEMENT{$_} && defined $COMP_DENSITY{$_} && $COMP_DENSITY{$_}==1} keys(%COMP_DENSITY)).']', $LOG);

	return (\%ELEMENT, \%COMP_DENSITY_USE_TERMS, \%COMP_DENSITY_END_TERMS, \%COMP_DENSITY, \%CDI_MAP, \%CDI_MAP_ART_DATE, $CDI_ID2CID, \%CDI_MAP_SUM_VOLUME_DEL_ID, \%CDI_DESC_OBJ_OLD_DEL_ID);
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
