package BITS::ReCalc;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use Time::HiRes;
use Cwd;
use Clone;

use constant {
	DEBUG => 0
};

use Data::Dumper;
$Data::Dumper::Indent = 1;
$Data::Dumper::Sortkeys = 1;

sub _getParentTreeNode {
	my %arg = @_;
	my $dbh   = $arg{'dbh'};
	my $sth = $arg{'sth'};
	my $hash = $arg{'hash'};
	my $enabled_cdi_ids = $arg{'enabled_cdi_ids'};
	my $cdi_id = $arg{'cdi_id'};
	my $bul_id = $arg{'bul_id'};

#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":[$cdi_id][$bul_id][$hash]\n" if(DEBUG);
#exit;

	return unless(exists $enabled_cdi_ids->{$cdi_id}->{$bul_id});

	my $cdi_pids;
	my $cdi_pid;
	my $column_number = 0;
	$sth->execute($cdi_id,$bul_id) or die $dbh->errstr;
#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":\t",$sth->rows(),"\n" if(DEBUG);
	$column_number = 0;
	$sth->bind_col(++$column_number, \$cdi_pid,   undef);
	while($sth->fetch){
		next unless(defined $cdi_pid);
		next unless(exists $enabled_cdi_ids->{$cdi_pid}->{$bul_id});
		next if(exists $hash->{$cdi_pid} && exists $hash->{$cdi_pid}->{$bul_id});
		next if($cdi_id == $cdi_pid);
#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":\t[$cdi_id][$cdi_pid]\n"if(DEBUG);
		$hash->{$cdi_pid}->{$bul_id} = undef;
		$cdi_pids->{$cdi_pid} = undef;
	}
	$sth->finish;

	if(defined $cdi_pids){
#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":\t[$cdi_id][$cdi_pids]\n"if(DEBUG);
		foreach my $cdi_pid (keys(%$cdi_pids)){
			&_getParentTreeNode(dbh=>$dbh,sth=>$sth,hash=>$hash,enabled_cdi_ids=>$enabled_cdi_ids,cdi_id=>$cdi_pid,bul_id=>$bul_id);
		}
	}
}

sub _get_cdi_ids {
	my %arg = @_;
	my $dbh   = $arg{'dbh'};
	my $ci_id = $arg{'ci_id'};
	my $cb_id = $arg{'cb_id'};

	my $cdi_names;
	if(defined $arg{'cdi_names'}){
		if(ref $arg{'cdi_names'} eq 'ARRAY'){
			$cdi_names = $arg{'cdi_names'};
		}else{
			eval{$cdi_names = &JSON::XS::decode_json($arg{'cdi_names'});};
		}
	}
	return undef unless(defined $cdi_names);

	my $all_but_cids;
	my $cdi_id;
	my $bul_id;
	my $but_cids;
	my $enabled_cdi_ids;
	my $cdi_ids;

	my $sql =<<SQL;
select
 cdi_id,
 bul_id,
 but_cids
from
 buildup_tree
where
 ci_id=$ci_id AND
 cb_id=$cb_id AND
 cdi_pid is null AND
 but_delcause is null
SQL
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$cdi_id,   undef);
	$sth->bind_col(++$column_number, \$bul_id,   undef);
	$sth->bind_col(++$column_number, \$but_cids,   undef);
	while($sth->fetch){
		$all_but_cids->{$bul_id}->{$cdi_id} = undef;
		if(defined $but_cids){
			my $cdi_cids;
			eval{$cdi_cids = &JSON::XS::decode_json($but_cids);};
			if(defined $cdi_cids && ref $cdi_cids eq 'ARRAY'){
				foreach my $cdi_cid (@$cdi_cids){
					$all_but_cids->{$bul_id}->{$cdi_cid} = undef;
				}
			}
		}
	}
	$sth->finish;
	undef $sth;

#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($all_but_cids),"\n" if(DEBUG);
#exit;

	if(DEBUG){
		my($epocsec, $microsec) = &Time::HiRes::gettimeofday();
		my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);
		print STDERR sprintf("%04d:%04d/%02d/%02d %02d:%02d:%02d.%d\n",__LINE__,$year+1900,$mon+1,$mday,$hour,$min,$sec,$microsec);
	}

	#使用可能なノードを取得
	if(defined $all_but_cids){
		foreach my $bul_id (keys(%$all_but_cids)){
			my $sql_fmt =<<SQL;
select
 cdi_id
from
 buildup_tree
where
 ci_id=$ci_id AND
 cb_id=$cb_id AND
 bul_id=$bul_id AND
 but_delcause is null AND
 cdi_id in (%s)
SQL
			my $sth = $dbh->prepare(sprintf($sql_fmt,join(",",keys(%{$all_but_cids->{$bul_id}})))) or die $dbh->errstr;
			$sth->execute() or die $dbh->errstr;
			my $cdi_id;
			my $column_number = 0;
			$sth->bind_col(++$column_number, \$cdi_id,   undef);
			while($sth->fetch){
				$enabled_cdi_ids->{$cdi_id}->{$bul_id} = undef;
			}
			$sth->finish;
			undef $sth;
		}
	}

#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($enabled_cdi_ids),"\n" if(DEBUG);
#exit;

	if(DEBUG){
		my($epocsec, $microsec) = &Time::HiRes::gettimeofday();
		my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);
		print STDERR sprintf("%04d:%04d/%02d/%02d %02d:%02d:%02d.%d\n",__LINE__,$year+1900,$mon+1,$mday,$hour,$min,$sec,$microsec);
	}

=pod
	my $sql =<<SQL;
select
 cdi.cdi_id,
 but.cdi_pid,
 but.bul_id,
 but.but_cids
from
 concept_data_info as cdi
left join (
 select cdi_id,cdi_pid,bul_id,but_cids from buildup_tree where ci_id=$ci_id AND cb_id=$cb_id AND but_delcause is null
) as but on
 but.cdi_id=cdi.cdi_id
where
 cdi.ci_id=$ci_id AND
 cdi.cdi_delcause is null AND
 cdi.cdi_name=?
SQL
=cut
	$sql =<<SQL;
select cdi_id,cdi_pid,bul_id,but_cids from view_buildup_tree where ci_id=$ci_id AND cb_id=$cb_id AND but_delcause is null AND cdi_name=?
SQL
#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":",$sql,"\n" if(DEBUG);

	my $cdi_pids;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;

	my $sql_fmt =<<SQL;
select cdi_id,cdi_pid from buildup_tree where ci_id=$ci_id AND cb_id=$cb_id AND but_delcause is null AND cdi_pid IS NOT NULL AND bul_id=%d AND cdi_id in (%s) GROUP BY cdi_id,cdi_pid
SQL

print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":",&Data::Dumper::Dumper($cdi_names),"\n" if(DEBUG);
	foreach my $cdi_name (@$cdi_names){
#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":",$cdi_name,"\n" if(DEBUG);
		$sth->execute($cdi_name) or die $dbh->errstr;
		my $cdi_id;
		my $cdi_pid;
		my $bul_id;
		my $but_cids;
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_id,   undef);
		$sth->bind_col(++$column_number, \$cdi_pid,   undef);
		$sth->bind_col(++$column_number, \$bul_id,   undef);
		$sth->bind_col(++$column_number, \$but_cids,   undef);
		while($sth->fetch){

			next unless(defined $cdi_id && defined $bul_id);
			next unless(exists $enabled_cdi_ids->{$cdi_id}->{$bul_id});

			$cdi_ids->{$cdi_id}->{$bul_id} = undef;
			$cdi_pids->{$cdi_id}->{$bul_id} = $cdi_pid if(defined $cdi_pid);
#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":\$but_cids=[$but_cids]\n" if(DEBUG);
			if(defined $but_cids){
				my $cdi_cids;
				eval{$cdi_cids = &JSON::XS::decode_json($but_cids);};
				if(defined $cdi_cids && ref $cdi_cids eq 'ARRAY'){
					foreach my $cdi_cid (@$cdi_cids){
						next unless(exists $enabled_cdi_ids->{$cdi_cid}->{$bul_id});
						$cdi_ids->{$cdi_cid}->{$bul_id} = undef;
					}
#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":",sprintf($sql_fmt,$bul_id,join(',',@$cdi_cids)),"\n" if(DEBUG);
					my $sth_p = $dbh->prepare(sprintf($sql_fmt,$bul_id,join(',',@$cdi_cids))) or die $dbh->errstr;
					$sth_p->execute() or die $dbh->errstr;
					my $temp_cdi_id;
					my $temp_cdi_pid;
					my $column_number = 0;
					$sth_p->bind_col(++$column_number, \$temp_cdi_id,   undef);
					$sth_p->bind_col(++$column_number, \$temp_cdi_pid,   undef);
					while($sth_p->fetch){
						next unless(defined $temp_cdi_id && defined $temp_cdi_pid);
						$cdi_ids->{$temp_cdi_pid}->{$bul_id} = undef;
						$cdi_pids->{$temp_cdi_id}->{$bul_id} = $temp_cdi_pid;
					}
					$sth_p->finish;
					undef $sth_p;


				}
			}

		}
		$sth->finish;
	}
	undef $sth;

#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($cdi_ids),"\n" if(DEBUG);
#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($cdi_pids),"\n" if(DEBUG);
#exit;

	if(DEBUG){
		my($epocsec, $microsec) = &Time::HiRes::gettimeofday();
		my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);
		print STDERR sprintf("%04d:%04d/%02d/%02d %02d:%02d:%02d.%d\n",__LINE__,$year+1900,$mon+1,$mday,$hour,$min,$sec,$microsec);
	}

#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($cdi_ids),"\n" if(DEBUG);
#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":",(scalar keys(%$cdi_ids)),"\n" if(DEBUG);

	if(defined $cdi_ids){
		my $sql = qq|select cdi_pid,bul_id from buildup_tree where ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=? AND bul_id=?|;
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		foreach my $cdi_id (keys(%$cdi_ids)){
			foreach my $bul_id (keys(%{$cdi_ids->{$cdi_id}})){

#				my $cdi_pid = $cdi_pids->{$cdi_id}->{$bul_id};
#				next if(defined $cdi_pid && exists $cdi_ids->{$cdi_pid} && defined $cdi_ids->{$cdi_pid} && exists $cdi_ids->{$cdi_pid}->{$bul_id});

				&_getParentTreeNode(dbh=>$dbh,sth=>$sth,hash=>$cdi_ids,enabled_cdi_ids=>$enabled_cdi_ids,cdi_id=>$cdi_id,bul_id=>$bul_id);
			}
		}
		undef $sth;
	}

#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($cdi_ids),"\n" if(DEBUG);
#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":",(scalar keys(%$cdi_ids)),"\n" if(DEBUG);
#exit;

	if(DEBUG){
		my($epocsec, $microsec) = &Time::HiRes::gettimeofday();
		my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);
		print STDERR sprintf("%04d:%04d/%02d/%02d %02d:%02d:%02d.%d\n",__LINE__,$year+1900,$mon+1,$mday,$hour,$min,$sec,$microsec);
	}

	return ($cdi_ids,$enabled_cdi_ids);
}

sub check {
	my %arg = @_;
	my $dbh     = $arg{'dbh'};
	my $ci_id   = $arg{'ci_id'};
	my $cb_id   = $arg{'cb_id'};
#	my $bul_id  = $arg{'bul_id'};
	my $md_id   = $arg{'md_id'};
	my $mv_id   = $arg{'mv_id'};
	my $mr_id   = $arg{'mr_id'};

	if(DEBUG){
		my($epocsec, $microsec) = &Time::HiRes::gettimeofday();
		my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);
		print STDERR sprintf("%04d:%04d/%02d/%02d %02d:%02d:%02d.%d\n",__LINE__,$year+1900,$mon+1,$mday,$hour,$min,$sec,$microsec);
	}

	my $cdi_names;
	unless(defined $arg{'cdi_names'}){
		my $sth = $dbh->prepare(qq|select cdi_name from view_buildup_tree where ci_id=$ci_id AND cb_id=$cb_id AND but_delcause is null AND cdi_pid IS NULL|) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		my $cdi_name;
		$sth->bind_col(1, \$cdi_name,   undef);
		while($sth->fetch){
			push(@$cdi_names,$cdi_name) if(defined $cdi_name);
		}
		$sth->finish;
		undef $sth;
#		$arg{'cdi_names'} = $cdi_names if(defined $cdi_names);
	}else{
		$cdi_names = $arg{'cdi_names'};
	}
	if(DEBUG){
		if(defined $cdi_names){
			if(ref $cdi_names eq 'ARRAY'){
				print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":".join(",",sort @$cdi_names)."\n";
			}else{
				print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":".$cdi_names."\n";
			}
		}
	}

	my $cdi_ids_hash;
	my $enabled_cdi_ids;
#	unless(defined $arg{'cdi_ids'}){
		delete $arg{'cdi_ids'} if(exists $arg{'cdi_ids'});
		($cdi_ids_hash,$enabled_cdi_ids) = &_get_cdi_ids(dbh=>$dbh,ci_id=>$ci_id,cb_id=>$cb_id,cdi_names=>$cdi_names);
		push(@{$arg{'cdi_ids'}},keys(%$cdi_ids_hash)) if(defined $cdi_ids_hash);
#	}

	if(DEBUG){
		my($epocsec, $microsec) = &Time::HiRes::gettimeofday();
		my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);
		print STDERR sprintf("%04d:%04d/%02d/%02d %02d:%02d:%02d.%d\n",__LINE__,$year+1900,$mon+1,$mday,$hour,$min,$sec,$microsec);
	}

	return undef unless(defined $arg{'cdi_ids'});

	my $cdi_ids_str = join(",",sort {$a<=>$b} @{$arg{'cdi_ids'}});
	my $cdi_ids;

	my $sql = qq|
select *,EXTRACT(EPOCH FROM cm_entry) as cm_entry_epoch from view_concept_art_map where (ci_id,cb_id,md_id,mv_id,mr_id,cdi_id) in 
(
 select
  ci_id,cb_id,md_id,mv_id,max(mr_id) as mr_id,cdi_id
 from
  concept_art_map
 where
  ci_id=$ci_id AND
  cb_id=$cb_id AND
  md_id=$md_id AND
  mv_id=$mv_id AND
  mr_id<=$mr_id
 group by
  ci_id,cb_id,md_id,mv_id,cdi_id
)
|;
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":",$sth->rows(),"\n" if(DEBUG);
	my %CM;
#	my %CM_HASH;
	my %CM_ART;
	while(my $row = $sth->fetchrow_hashref){
		next unless(defined $row && exists $row->{'cdi_id'} && defined $row->{'cdi_id'});

#		next if(exists $CM_HASH{$row->{'cdi_id'}} && defined $CM_HASH{$row->{'cdi_id'}} && exists $CM_HASH{$row->{'cdi_id'}}->{$row->{'cm_id'}});
#		$CM_HASH{$row->{'cdi_id'}}->{$row->{'cm_id'}} = undef;

		push(@{$CM{$row->{'cdi_id'}}},$row) if(exists $row->{'cdi_id'} && defined $row->{'cdi_id'});
		push(@{$CM_ART{$row->{'art_id'}}->{$row->{'art_hist_serial'}}},$row) if(exists $row->{'art_id'} && defined $row->{'art_id'} && exists $row->{'art_hist_serial'} && defined $row->{'art_hist_serial'});
	}
	$sth->finish;
	undef $sth;
if(DEBUG){
#	print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":\n";
#	print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":",scalar keys(%CM),"\n";
#	print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper(\%CM),"\n";
}


	$sql = qq|
select cdi_id,EXTRACT(EPOCH FROM max(hist_timestamp)) as hist_timestamp_epoch,max(hist_timestamp) as hist_timestamp from history_concept_art_map where (ci_id,cb_id,md_id,mv_id,mr_id,cdi_id) in 
(
 select
  ci_id,cb_id,md_id,mv_id,max(mr_id) as mr_id,cdi_id
 from
  history_concept_art_map
 where
  ci_id=$ci_id AND
  cb_id=$cb_id AND
  md_id=$md_id AND
  mv_id=$mv_id AND
  mr_id<=$mr_id
 group by
  ci_id,cb_id,md_id,mv_id,cdi_id
)
group by
 cdi_id
|;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":",$sth->rows(),"\n" if(DEBUG);
	my %HCM;
	while(my $row = $sth->fetchrow_hashref){
		next unless(defined $row && exists $row->{'cdi_id'} && defined $row->{'cdi_id'} && exists $row->{'hist_timestamp_epoch'} && defined $row->{'hist_timestamp_epoch'});
		$HCM{$row->{'cdi_id'}} = $row;
	}
	$sth->finish;
	undef $sth;
if(DEBUG){
#	print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":\n";
	print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":",scalar keys(%HCM),"\n";
#	print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper(\%CM),"\n";
}



#強制的に最終更新日時より古いものを更新する
#	my $sth = $dbh->prepare(qq|select EXTRACT(EPOCH FROM MAX(cm_modified)) as cm_modified_epoch from concept_art_map_modified where ci_id=$ci_id AND cb_id=$cb_id AND md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id|) or die $dbh->errstr;
#	$sth->execute() or die $dbh->errstr;
#	my $row = $sth->fetchrow_hashref;
#	$sth->finish;
#	undef $sth;
#	my $max_cm_modified_epoch = $row->{'cm_modified_epoch'};
#	undef $row;
	my $max_cm_modified_epoch = 0;


#				my $sql = sprintf(qq|select * from buildup_tree where ci_id=$ci_id AND cb_id=$cb_id AND but_delcause is null AND cdi_id in (%s)|,$cdi_ids_str);
	$sql = qq|select * from buildup_tree where ci_id=$ci_id AND cb_id=$cb_id AND but_delcause is null|;
#				my $sql = qq|select cdi_id,bul_id from buildup_tree where ci_id=$ci_id AND cb_id=$cb_id AND but_delcause is null|;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":",$sth->rows(),"\n" if(DEBUG);
	my %BUT;
	while(my $row = $sth->fetchrow_hashref){
		my $row_clone = &Clone::clone($row);;
		$row_clone->{'but_cids'} = (exists $row_clone->{'but_cids'} && defined $row_clone->{'but_cids'}) ? &JSON::XS::decode_json($row_clone->{'but_cids'}) : undef;
		$BUT{$row_clone->{'cdi_id'}}->{$row_clone->{'bul_id'}} = $row_clone;
	}
	$sth->finish;
	undef $sth;
#exit;

	my $sth_repa = $dbh->prepare(qq|select * from representation_art where rep_id=?|) or die $dbh->errstr;

	$sql = qq|select *,EXTRACT(EPOCH FROM rep_entry) as rep_entry_epoch from view_representation where
(ci_id,cb_id,md_id,mv_id,mr_id,cdi_id,bul_id) in 
  (select
    ci_id,cb_id,md_id,mv_id,max(mr_id) as mr_id,cdi_id,bul_id
   from
    representation
   where
    ci_id=$ci_id AND
    cb_id=$cb_id AND
    md_id=$md_id AND
    mv_id=$mv_id AND
    mr_id<=$mr_id
   group by
    ci_id,cb_id,md_id,mv_id,cdi_id,bul_id
)
|;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":",$sth->rows(),"\n" if(DEBUG);
#	my $min_rep_entry_epoch;
	my %REP;
	while(my $row = $sth->fetchrow_hashref){
#					print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($row),"\n" if(DEBUG);
		$REP{$row->{'cdi_id'}}->{$row->{'bul_id'}} = $row;
#		$min_rep_entry_epoch = $row->{'rep_entry_epoch'} if(defined $min_rep_entry_epoch && $min_rep_entry_epoch > $row->{'rep_entry_epoch'} || !defined $min_rep_entry_epoch);

		$sth_repa->execute($row->{'rep_id'}) or die $dbh->errstr;
		while(my $rowa = $sth_repa->fetchrow_hashref){
			$REP{$row->{'cdi_id'}}->{$row->{'bul_id'}}->{'rep_a'}->{$rowa->{'art_id'}} = $rowa->{'art_hist_serial'} if(defined $rowa);
		}
		$sth_repa->finish;
	}
	$sth->finish;
	undef $sth;
#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper(\%REP),"\n";

#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":\n";
#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($cdi_ids),"\n";

#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":\$max_cm_entry_epoch=[$max_cm_entry_epoch]\n" if(DEBUG);
#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":\$min_rep_entry_epoch=[$min_rep_entry_epoch]\n" if(DEBUG);


#	foreach my $cdi_id (sort {$a<=>$b} keys(%CM)){
	foreach my $cdi_id (sort {$a<=>$b} @{$arg{'cdi_ids'}}){
		next unless(exists $BUT{$cdi_id} && defined $BUT{$cdi_id});
		next unless(exists $CM{$cdi_id} && defined $CM{$cdi_id});
#					print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($cdi_id),"\n" if(DEBUG);
print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":\$CM{$cdi_id}->[0]->{'cdi_name'}=[",$CM{$cdi_id}->[0]->{'cdi_name'},"]\n" if(DEBUG);
		foreach my $bul_id (sort {$a<=>$b} keys %{$BUT{$cdi_id}}){
print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":[$cdi_id][$bul_id]\n" if(DEBUG);
			foreach my $cm (@{$CM{$cdi_id}}){
				my $val;
				if(exists $REP{$cdi_id} && defined $REP{$cdi_id} && exists $REP{$cdi_id}->{$bul_id} && defined $REP{$cdi_id}->{$bul_id}){
					next unless($REP{$cdi_id}->{$bul_id}->{'rep_primitive'});
					next if(!$cm->{'cm_use'} && defined $REP{$cdi_id}->{$bul_id}->{'rep_delcause'});
#					next if($cm->{'cm_entry_epoch'} <= $REP{$cdi_id}->{$bul_id}->{'rep_entry_epoch'} && $max_cm_modified_epoch <= $REP{$cdi_id}->{$bul_id}->{'rep_entry_epoch'});
#					unless(
#						(!$cm->{'cm_use'} && !defined $REP{$cdi_id}->{$bul_id}->{'rep_delcause'}) ||
#						( $cm->{'cm_use'} &&  defined $REP{$cdi_id}->{$bul_id}->{'rep_delcause'})
#					){
#						next if($cm->{'cm_entry_epoch'} <= $REP{$cdi_id}->{$bul_id}->{'rep_entry_epoch'} && $max_cm_modified_epoch <= $REP{$cdi_id}->{$bul_id}->{'rep_entry_epoch'});
#					}
					next if($cm->{'cm_entry_epoch'} <= $REP{$cdi_id}->{$bul_id}->{'rep_entry_epoch'} && $HCM{$cdi_id}->{'hist_timestamp_epoch'} <= $REP{$cdi_id}->{$bul_id}->{'rep_entry_epoch'});
					$val = ($cm->{'cm_use'} ? 'update' : 'delete') . ':'.__LINE__;
					$val .= ':['.$cm->{'cm_use'}.']:['.$cm->{'cm_entry'}.']:['.$HCM{$cdi_id}->{'hist_timestamp'}.']:['.$REP{$cdi_id}->{$bul_id}->{'rep_entry'}.']:'.$REP{$cdi_id}->{$bul_id}->{'cdi_name'};
#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($cm);
#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($REP{$cdi_id}->{$bul_id});
				}else{
					next unless($cm->{'cm_use'});
					$val = 'insert:'.__LINE__.':'.$cm->{'cdi_name'};
#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($cm)."\n";# if(DEBUG);
				}
print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":\t[$val]\n" if(DEBUG);
				$cdi_ids->{$cdi_id}->{$bul_id} = $val;
				last if(defined $cdi_ids && exists $cdi_ids->{$cdi_id} && defined $cdi_ids->{$cdi_id} && exists $cdi_ids->{$cdi_id}->{$bul_id} && defined $cdi_ids->{$cdi_id}->{$bul_id} && $cdi_ids->{$cdi_id}->{$bul_id} !~ /^delete/);
			}
		}
	}

#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":\n" if(DEBUG);
print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($cdi_ids)."\n" if(DEBUG);
#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper(\%CM),"\n" if(DEBUG);
#exit;

=pod
#末端のノードでマップされていない場合
	foreach my $cdi_id (sort {$a<=>$b} @{$arg{'cdi_ids'}}){
		next unless(exists $BUT{$cdi_id} && defined $BUT{$cdi_id});

		my $but_cids_hash;
		foreach my $bul_id (sort {$a<=>$b} keys %{$BUT{$cdi_id}}){
			my $but_cids = defined $BUT{$cdi_id}->{$bul_id}->{'but_cids'} ? &JSON::XS::decode_json($BUT{$cdi_id}->{$bul_id}->{'but_cids'}) : undef;
			next unless(defined $but_cids);
			foreach my $but_cid (@$but_cids){
				next unless(exists $CM{$but_cid} && defined $CM{$but_cid});
				$but_cids_hash->{$but_cid} = undef unless(exists $but_cids_hash->{$but_cid});
			}
		}
		foreach my $bul_id (sort {$a<=>$b} keys %{$BUT{$cdi_id}}){
			next if(defined $BUT{$cdi_id}->{$bul_id}->{'but_cids'});

			foreach my $but_cid (keys %$but_cids_hash){
				foreach my $cm (@{$CM{$but_cid}}){
					my $val;
					if(exists $REP{$cdi_id} && defined $REP{$cdi_id} && exists $REP{$cdi_id}->{$bul_id} && defined $REP{$cdi_id}->{$bul_id}){
						next unless($REP{$cdi_id}->{$bul_id}->{'rep_primitive'});
						next if(!$cm->{'cm_use'} && defined $REP{$cdi_id}->{$bul_id}->{'rep_delcause'});
						next if($cm->{'cm_entry_epoch'} <= $REP{$cdi_id}->{$bul_id}->{'rep_entry_epoch'});
						$val = ($cm->{'cm_use'} ? 'update' : 'delete') . ':'.__LINE__;
						$val .= ':['.$cm->{'cm_use'}.']:['.$cm->{'cm_entry'}.']:['.$REP{$cdi_id}->{$bul_id}->{'rep_entry'}.']:'.$REP{$cdi_id}->{$bul_id}->{'cdi_name'};
					}else{
						$val = 'insert:'.__LINE__;
					}
					$cdi_ids->{$cdi_id}->{$bul_id} = $val;
					last if(defined $cdi_ids && exists $cdi_ids->{$cdi_id} && defined $cdi_ids->{$cdi_id} && exists $cdi_ids->{$cdi_id}->{$bul_id} && defined $cdi_ids->{$cdi_id}->{$bul_id} && $cdi_ids->{$cdi_id}->{$bul_id} !~ /^delete/);
				}
			}
		}
	}
print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($cdi_ids),"\n" if(DEBUG);
=cut

	my %CDIS_BUL;
	foreach my $cdi_id (@{$arg{'cdi_ids'}}){
#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":\$cdi_id=[",$cdi_id,"]\n";
		next unless(exists $BUT{$cdi_id} && defined $BUT{$cdi_id});
		next unless(exists $REP{$cdi_id} && defined $REP{$cdi_id});
		foreach my $bul_id (sort {$a<=>$b} keys(%{$REP{$cdi_id}})){
			push(@{$CDIS_BUL{$bul_id}},$cdi_id);
		}
	}

#	foreach my $cdi_id (sort {$a<=>$b} @{$arg{'cdi_ids'}}){
#		next unless(exists $BUT{$cdi_id} && defined $BUT{$cdi_id});
#		next unless(exists $REP{$cdi_id} && defined $REP{$cdi_id});
#		foreach my $bul_id (sort {$a<=>$b} keys(%{$REP{$cdi_id}})){

	foreach my $bul_id (sort {$a<=>$b} keys(%CDIS_BUL)){
		foreach my $cdi_id (sort {$BUT{$b}->{$bul_id}->{'but_depth'}<=>$BUT{$a}->{$bul_id}->{'but_depth'}} @{$CDIS_BUL{$bul_id}}){
print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\$REP{$cdi_id}->{$bul_id}->{'cdi_name'}=[".$REP{$cdi_id}->{$bul_id}->{'cdi_name'}."]\n" if(DEBUG);
			if(defined $cdi_ids && exists $cdi_ids->{$cdi_id} && defined $cdi_ids->{$cdi_id} && exists $cdi_ids->{$cdi_id}->{$bul_id}){
				next;
			}
print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\n" if(DEBUG);
			unless(exists $BUT{$cdi_id}->{$bul_id} && defined $BUT{$cdi_id}->{$bul_id}){
				$cdi_ids->{$cdi_id}->{$bul_id} = 'delete:'.__LINE__.':'.$REP{$cdi_id}->{$bul_id}->{'cdi_name'};
				next;
			}
			if($REP{$cdi_id}->{$bul_id}->{'rep_primitive'}){
print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\n" if(DEBUG);
				unless(exists $CM{$cdi_id} && defined $CM{$cdi_id}){
					next if($max_cm_modified_epoch==0 && defined $REP{$cdi_id}->{$bul_id}->{'rep_delcause'});
					$cdi_ids->{$cdi_id}->{$bul_id} = 'delete:'.__LINE__.':'.$REP{$cdi_id}->{$bul_id}->{'cdi_name'};
					next;
				}
				if(exists $CM{$cdi_id} && defined $CM{$cdi_id}){
					foreach my $cm (@{$CM{$cdi_id}}){
						$cdi_ids->{$cdi_id}->{$bul_id} = ($cm->{'cm_use'} ? 'update:'.__LINE__ : 'delete:'.__LINE__) if($cm->{'cm_entry_epoch'} > $REP{$cdi_id}->{$bul_id}->{'rep_entry_epoch'} || $HCM{$cdi_id}->{'hist_timestamp_epoch'} > $REP{$cdi_id}->{$bul_id}->{'rep_entry_epoch'});
						last if(defined $cdi_ids && exists $cdi_ids->{$cdi_id} && defined $cdi_ids->{$cdi_id} && exists $cdi_ids->{$cdi_id}->{$bul_id} && defined $cdi_ids->{$cdi_id}->{$bul_id} && $cdi_ids->{$cdi_id}->{$bul_id} !~ /^delete/);
					}
				}
				next if(defined $cdi_ids && exists $cdi_ids->{$cdi_id} && defined $cdi_ids->{$cdi_id} && exists $cdi_ids->{$cdi_id}->{$bul_id});
				unless(defined $REP{$cdi_id}->{$bul_id}->{'rep_delcause'}){
					if(exists $REP{$cdi_id}->{$bul_id}->{'rep_a'} && defined $REP{$cdi_id}->{$bul_id}->{'rep_a'} && $REP{$cdi_id}->{$bul_id}->{'rep_child_objs'} != scalar keys(%{$REP{$cdi_id}->{$bul_id}->{'rep_a'}})){
						$cdi_ids->{$cdi_id}->{$bul_id} = 'update:'.__LINE__.':['.$REP{$cdi_id}->{$bul_id}->{'rep_child_objs'}.']->['.(scalar keys(%{$REP{$cdi_id}->{$bul_id}->{'rep_a'}})).']';
					}else{
						foreach my $art_id (keys(%{$REP{$cdi_id}->{$bul_id}->{'rep_a'}})){
							my $art_hist_serial = $REP{$cdi_id}->{$bul_id}->{'rep_a'}->{$art_id};
							if(exists $CM_ART{$art_id} && defined $CM_ART{$art_id} && exists $CM_ART{$art_id}->{$art_hist_serial} && defined $CM_ART{$art_id}->{$art_hist_serial}){
								foreach my $cm (@{$CM_ART{$art_id}->{$art_hist_serial}}){
									next unless(exists $cm->{'cm_use'} && defined $cm->{'cm_use'} && $cm->{'cm_use'});
									next if($cm->{'cdi_id'} == $cdi_id);
									$cdi_ids->{$cdi_id}->{$bul_id} = 'update:'.__LINE__.':'.$REP{$cdi_id}->{$bul_id}->{'cdi_name'};
									last;
								}
							}else{
								$cdi_ids->{$cdi_id}->{$bul_id} = 'update:'.__LINE__.':'.$REP{$cdi_id}->{$bul_id}->{'cdi_name'};
							}
						}
					}
				}
				elsif(exists $CM{$cdi_id} && defined $CM{$cdi_id}){
					foreach my $cm (@{$CM{$cdi_id}}){
						next unless($cm->{'cm_use'});
						$cdi_ids->{$cdi_id}->{$bul_id} = 'update:'.__LINE__.':'.$REP{$cdi_id}->{$bul_id}->{'cdi_name'};
						last;
					}
				}


			}else{
print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\n" if(DEBUG);
				next if(defined $REP{$cdi_id}->{$bul_id}->{'rep_delcause'});
print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\n" if(DEBUG);

#				my $but_cids = defined $BUT{$cdi_id}->{$bul_id}->{'but_cids'} ? &JSON::XS::decode_json($BUT{$cdi_id}->{$bul_id}->{'but_cids'}) : undef;
				my $but_cids = $BUT{$cdi_id}->{$bul_id}->{'but_cids'};
				push(@$but_cids,$cdi_id);

				my %but_cids_uniq = map {$_ => undef} @$but_cids;
				$but_cids = [keys %but_cids_uniq];

				if(defined $but_cids){
					my $rep_child_objs = 0;
					my $rep_density_objs = 0;
					my $max_cm_entry_epoch;
					foreach my $but_cid (@$but_cids){
						next unless(exists $CM{$but_cid} && defined $CM{$but_cid});
						$rep_density_objs++;
						foreach my $cm (@{$CM{$but_cid}}){
							if($cm->{'cm_use'}){
								$rep_child_objs++;
#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($cm),"\n" if(DEBUG);
							}
							next if(defined $cdi_ids && exists $cdi_ids->{$cdi_id} && defined $cdi_ids->{$cdi_id} && exists $cdi_ids->{$cdi_id}->{$bul_id} && defined $cdi_ids->{$cdi_id}->{$bul_id} && $cdi_ids->{$cdi_id}->{$bul_id} !~ /^delete/);
#							$cdi_ids->{$but_cid}->{$bul_id} = ($cm->{'cm_use'} ? 'update' : 'delete').':'.__LINE__.':'.$REP{$cdi_id}->{$bul_id}->{'cdi_name'} if($cm->{'cm_entry_epoch'}> $REP{$cdi_id}->{$bul_id}->{'rep_entry_epoch'});
#							$cdi_ids->{$but_cid}->{$bul_id} = 'update' .':'.__LINE__.':'.$REP{$cdi_id}->{$bul_id}->{'cdi_name'} if($cm->{'cm_entry_epoch'}> $REP{$cdi_id}->{$bul_id}->{'rep_entry_epoch'});
							if(defined $max_cm_entry_epoch && $max_cm_entry_epoch < $cm->{'cm_entry_epoch'} || !defined $max_cm_entry_epoch){
								$max_cm_entry_epoch = $cm->{'cm_entry_epoch'};
print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":[".$cm->{'cdi_name'}."]=[".$cm->{'cm_entry_epoch'}."][".$cm->{'cm_entry'}."]\n" if(DEBUG);
							}
						}
						if(exists $HCM{$but_cid} && (defined $max_cm_entry_epoch && $max_cm_entry_epoch < $HCM{$but_cid}->{'hist_timestamp_epoch'} || !defined $max_cm_entry_epoch)){
							$max_cm_entry_epoch = $HCM{$but_cid}->{'hist_timestamp_epoch'};
print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":[".$but_cid."]=[".$HCM{$but_cid}->{'hist_timestamp_epoch'}."][".$HCM{$but_cid}->{'hist_timestamp'}."]\n" if(DEBUG);
						}
					}
					if(defined $max_cm_entry_epoch){
						if($max_cm_entry_epoch > $REP{$cdi_id}->{$bul_id}->{'rep_entry_epoch'} || $max_cm_modified_epoch > $REP{$cdi_id}->{$bul_id}->{'rep_entry_epoch'}){
							$cdi_ids->{$cdi_id}->{$bul_id} = 'update' .':'.__LINE__.':'.$REP{$cdi_id}->{$bul_id}->{'cdi_name'};
print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":[".$cdi_ids->{$cdi_id}->{$bul_id}."][".$max_cm_entry_epoch."][".$REP{$cdi_id}->{$bul_id}->{'rep_entry_epoch'}."][".$REP{$cdi_id}->{$bul_id}->{'rep_entry'}."]\n" if(DEBUG);

#							my $but_cids_only = defined $BUT{$cdi_id}->{$bul_id}->{'but_cids'} ? &JSON::XS::decode_json($BUT{$cdi_id}->{$bul_id}->{'but_cids'}) : undef;
							my $but_cids_only = $BUT{$cdi_id}->{$bul_id}->{'but_cids'};
							if(defined $but_cids_only && ref $but_cids_only eq 'ARRAY'){
print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($but_cids_only),"\n" if(DEBUG);
								#子ノードが更新対象かを確認
								my $recalc_but_cids = 1;
								foreach my $but_cid (@$but_cids_only){
									$recalc_but_cids = 0 if(defined $cdi_ids && exists $cdi_ids->{$but_cid} && defined $cdi_ids->{$but_cid} && exists $cdi_ids->{$but_cid}->{$bul_id} && defined $cdi_ids->{$but_cid}->{$bul_id});
									last unless($recalc_but_cids);
								}
print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\$recalc_but_cids=[$recalc_but_cids]\n" if(DEBUG);
								#子ノードが更新対象になっていない場合
								if($recalc_but_cids){
									foreach my $but_cid (@$but_cids_only){
										next if(defined $cdi_ids && exists $cdi_ids->{$but_cid} && defined $cdi_ids->{$but_cid} && exists $cdi_ids->{$but_cid}->{$bul_id});
										next unless(exists $CM{$but_cid} && defined $CM{$but_cid});
										foreach my $cm (@{$CM{$but_cid}}){
											$cdi_ids->{$but_cid}->{$bul_id} = ($cm->{'cm_use'} ? 'update' : 'delete').':'.__LINE__.':'.$REP{$cdi_id}->{$bul_id}->{'cdi_name'}.':'.$cm->{'cdi_name'};
print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":[".$cdi_ids->{$but_cid}->{$bul_id}."]\n" if(DEBUG);
											last if(defined $cdi_ids && exists $cdi_ids->{$but_cid} && defined $cdi_ids->{$but_cid} && exists $cdi_ids->{$but_cid}->{$bul_id} && defined $cdi_ids->{$but_cid}->{$bul_id} && $cdi_ids->{$but_cid}->{$bul_id} !~ /^delete/);
										}
									}
								}
							}
							else{
print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($REP{$cdi_id}->{$bul_id}),"\n" if(DEBUG);
							}
						}
					}else{
						$cdi_ids->{$cdi_id}->{$bul_id} = 'delete' .':'.__LINE__.':'.$REP{$cdi_id}->{$bul_id}->{'cdi_name'};
					}
					unless(defined $cdi_ids && exists $cdi_ids->{$cdi_id} && defined $cdi_ids->{$cdi_id} && exists $cdi_ids->{$cdi_id}->{$bul_id}){
#						$cdi_ids->{$cdi_id}->{$bul_id} = 'update:'.__LINE__ if($REP{$cdi_id}->{$bul_id}->{'rep_child_objs'} != $rep_child_objs || $REP{$cdi_id}->{$bul_id}->{'rep_density_objs'} != $rep_density_objs);
						$cdi_ids->{$cdi_id}->{$bul_id} = 'update:'.__LINE__.qq|:$REP{$cdi_id}->{$bul_id}->{'cdi_name'}:[$REP{$cdi_id}->{$bul_id}->{'rep_child_objs'}]->[$rep_child_objs]| if($REP{$cdi_id}->{$bul_id}->{'rep_child_objs'} != $rep_child_objs);
					}
				}
				unless(defined $cdi_ids && exists $cdi_ids->{$cdi_id} && defined $cdi_ids->{$cdi_id} && exists $cdi_ids->{$cdi_id}->{$bul_id}){
					if(exists $REP{$cdi_id}->{$bul_id}->{'rep_a'} && defined $REP{$cdi_id}->{$bul_id}->{'rep_a'} && $REP{$cdi_id}->{$bul_id}->{'rep_child_objs'} != scalar keys(%{$REP{$cdi_id}->{$bul_id}->{'rep_a'}})){
						$cdi_ids->{$cdi_id}->{$bul_id} = 'update:'.__LINE__.':'.$REP{$cdi_id}->{$bul_id}->{'cdi_name'};
					}elsif(defined $but_cids){
						my %HASH = map {$_=>undef} @$but_cids;
						$HASH{$cdi_id} = undef;
						foreach my $art_id (keys(%{$REP{$cdi_id}->{$bul_id}->{'rep_a'}})){
							my $art_hist_serial = $REP{$cdi_id}->{$bul_id}->{'rep_a'}->{$art_id};
							if(exists $CM_ART{$art_id} && defined $CM_ART{$art_id} && exists $CM_ART{$art_id}->{$art_hist_serial} && defined $CM_ART{$art_id}->{$art_hist_serial}){
								foreach my $cm (@{$CM_ART{$art_id}->{$art_hist_serial}}){
									next unless(exists $cm->{'cm_use'} && defined $cm->{'cm_use'} && $cm->{'cm_use'});
									next if(exists $HASH{$cm->{'cdi_id'}} && exists $CM{$cm->{'cdi_id'}});
									$cdi_ids->{$cdi_id}->{$bul_id} = 'update:'.__LINE__.':'.$REP{$cdi_id}->{$bul_id}->{'cdi_name'};
									last;
								}
							}else{
								$cdi_ids->{$cdi_id}->{$bul_id} = 'update:'.__LINE__.':'.$REP{$cdi_id}->{$bul_id}->{'cdi_name'};
							}
						}
					}
				}
			}
		}
	}
print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($cdi_ids),"\n" if(DEBUG);

	if(DEBUG){
		my($epocsec, $microsec) = &Time::HiRes::gettimeofday();
		my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);
		print STDERR sprintf("%04d:%04d/%02d/%02d %02d:%02d:%02d.%d\n",__LINE__,$year+1900,$mon+1,$mday,$hour,$min,$sec,$microsec);
	}


	if(defined $cdi_ids){
		my $sql = qq|select cdi_pid,bul_id from buildup_tree where ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=? AND bul_id=?|;
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		foreach my $cdi_id (keys(%$cdi_ids)){
			foreach my $bul_id (keys(%{$cdi_ids->{$cdi_id}})){
#				&_getParentTreeNode($sth,$cdi_ids,$enabled_cdi_ids,$cdi_id,$bul_id);
				&_getParentTreeNode(dbh=>$dbh,sth=>$sth,hash=>$cdi_ids,enabled_cdi_ids=>$enabled_cdi_ids,cdi_id=>$cdi_id,bul_id=>$bul_id);
			}
		}
		undef $sth;
	}

	if(DEBUG){
		my($epocsec, $microsec) = &Time::HiRes::gettimeofday();
		my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);
		print STDERR sprintf("%04d:%04d/%02d/%02d %02d:%02d:%02d.%d\n",__LINE__,$year+1900,$mon+1,$mday,$hour,$min,$sec,$microsec);
	}

	return $cdi_ids;
}

sub get_max_map_info {
	my %arg = @_;
	my $dbh     = $arg{'dbh'};
	my $ci_id   = $arg{'ci_id'};
	my $cb_id   = $arg{'cb_id'};
	my $bul_id  = $arg{'bul_id'};
	my $md_id   = $arg{'md_id'};
	my $mv_id   = $arg{'mv_id'};
	my $mr_id   = $arg{'mr_id'};
	my $cdi_id   = $arg{'cdi_id'};
	my $but_cids = $arg{'but_cids'};

	my $cm_max_num_cdi;
	my $cm_max_entry_cdi;
#	return wantarray ? ($cm_max_num_cdi,$cm_max_entry_cdi) : [$cm_max_num_cdi,$cm_max_entry_cdi];

	my $sth_cmm = $dbh->prepare(qq|select EXTRACT(EPOCH FROM cm_modified) from concept_art_map_modified where ci_id=? AND cb_id=? AND md_id=? AND mv_id=? AND mr_id=? AND bul_id=? AND cdi_id=?|) or die $dbh->errstr;
	$sth_cmm->execute($ci_id,$cb_id,$md_id,$mv_id,$mr_id,$bul_id,$cdi_id) or die $dbh->errstr;
	$sth_cmm->bind_col(1, \$cm_max_entry_cdi, undef);
	$sth_cmm->fetch;
	$sth_cmm->finish;
	undef $sth_cmm;
	return wantarray ? ($cm_max_num_cdi,$cm_max_entry_cdi) : [$cm_max_num_cdi,$cm_max_entry_cdi];


	unless(defined $but_cids){
		my $sth = $dbh->prepare(qq|select but_cids from buildup_tree where but_delcause is null AND ci_id=$ci_id AND cb_id=$cb_id AND bul_id=$bul_id AND cdi_id=$cdi_id|) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$sth->bind_col(1, \$but_cids, undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;
	}
	my $but_cids_arr = &JSON::XS::decode_json($but_cids) if(defined $but_cids);
	push(@$but_cids_arr,$cdi_id);

	my $sql_cm_max_num_cdi = sprintf(qq|
select cm_use,count(*),EXTRACT(EPOCH FROM max(cm_entry)) from concept_art_map where cm_use and cm_delcause is null and (ci_id,cb_id,md_id,mv_id,mr_id,cdi_id) in (
  select ci_id,cb_id,md_id,mv_id,max(mr_id) as mr_id,cdi_id from concept_art_map where ci_id=$ci_id AND cb_id=$cb_id AND md_id=$md_id AND mv_id=$mv_id AND mr_id<=$mr_id AND cdi_id in (%s) group by ci_id,cb_id,md_id,mv_id,cdi_id
) group by cm_use
|,join(',',@$but_cids_arr));

	undef $but_cids_arr;

	my $sth_cm_max_num_cdi = $dbh->prepare($sql_cm_max_num_cdi) or die $dbh->errstr;
	$sth_cm_max_num_cdi->execute() or die $dbh->errstr;
	my $column_number = 0;
	my $cm_use;
	my $cm_count;
	my $cm_entry;
	$sth_cm_max_num_cdi->bind_col(++$column_number, \$cm_use, undef);
	$sth_cm_max_num_cdi->bind_col(++$column_number, \$cm_count, undef);
	$sth_cm_max_num_cdi->bind_col(++$column_number, \$cm_entry, undef);
	while($sth_cm_max_num_cdi->fetch){
		if($cm_use){
			$cm_max_num_cdi = 0 unless(defined $cm_max_num_cdi);
			$cm_max_num_cdi += $cm_count;
		}
		$cm_max_entry_cdi = $cm_entry if(defined $cm_max_entry_cdi && $cm_max_entry_cdi < $cm_entry || !defined $cm_max_entry_cdi)
	}
	$sth_cm_max_num_cdi->finish;
	undef $sth_cm_max_num_cdi;
	undef $sql_cm_max_num_cdi;

	return wantarray ? ($cm_max_num_cdi,$cm_max_entry_cdi) : [$cm_max_num_cdi,$cm_max_entry_cdi];
}

1;
