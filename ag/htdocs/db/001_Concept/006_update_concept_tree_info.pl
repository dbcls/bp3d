#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use Time::HiRes;
use JSON::XS;

=pod
ALTER TABLE buildup_logic DROP CONSTRAINT buildup_logic_crl_id_check CASCADE;
ALTER TABLE buildup_logic DROP CONSTRAINT buildup_logic_bul_rep_key_check CASCADE;
INSERT INTO buildup_logic (crl_id,bul_order,bul_name_e,bul_rep_key,bul_entry,bul_use,bul_abbr,bul_openid) VALUES (0,0,'FMA','F','2013-03-18 10:22:26.286383',false,'fma','system');

ALTER TABLE concept_tree_info ADD COLUMN crl_id integer not null default 0;
ALTER TABLE concept_tree_info ADD CONSTRAINT concept_tree_info_crl_id_fkey FOREIGN KEY (crl_id) REFERENCES buildup_logic (crl_id) ON DELETE CASCADE;

ALTER TABLE concept_tree_info DROP CONSTRAINT concept_tree_info_pkey;
ALTER TABLE concept_tree_info ADD PRIMARY KEY (ci_id, cb_id, crl_id, cdi_id);

=cut

my $t0 = [&Time::HiRes::gettimeofday()];

use FindBin;
use lib qq|$FindBin::Bin/../..|,qq|$FindBin::Bin/../../../lib|,qq|$FindBin::Bin/../../../../ag-common/lib|;

use Getopt::Long qw(:config posix_default no_ignore_case gnu_compat);
my $config = {
	host => '127.0.0.1',
	port => '8543',
	only_FMA20394 => 0
};
&Getopt::Long::GetOptions($config,qw/
	host|h=s
	port|p=s
	only_FMA20394
/) or exit 1;

$ENV{'AG_DB_HOST'} = $config->{'host'};
$ENV{'AG_DB_PORT'} = $config->{'port'};

require "common_db.pl";
my $dbh = &get_dbh();

my $ci_id;
my $cb_id;
if(scalar @ARGV < 2){
	select(STDERR);
	$| = 1;
	say qq|$0 concept_info_id concept_build_id| ;
	say qq|#optins :|;
	say qq|# --host,-h : database host [default:$config->{'host'}]|;
	say qq|# --port,-p : database port [default:$config->{'port'}]|;
	say qq|#concept_info_id:concept_build_id:|;
	my $sql=<<SQL;
select info.ci_id,cb_id,ci_name,cb_name,cb_release from concept_build
left join (select ci_id,ci_name from concept_info where ci_delcause is null) as info on (concept_build.ci_id=info.ci_id)
where cb_delcause is null
order by cb_release,info.ci_id,cb_id;
SQL
	my $ci_name;
	my $cb_name;
	my $cb_release;
	my $sth = $dbh->prepare($sql);
	$sth->execute();
	$sth->bind_col(1, \$ci_id, undef);
	$sth->bind_col(2, \$cb_id, undef);
	$sth->bind_col(3, \$ci_name, undef);
	$sth->bind_col(4, \$cb_name, undef);
	$sth->bind_col(5, \$cb_release, undef);
	while($sth->fetch){
		say sprintf("             %-2d :            %3d : %-5s : %-25s : %10s",$ci_id,$cb_id,$ci_name,"$cb_name",$cb_release);
	}
	$sth->finish;
	undef $sth;
	exit 1;
}
$ci_id = $ARGV[0];
$cb_id = $ARGV[1];

#my $dbh = &get_dbh();

my %CIDS;
my %PIDS;

my $sth_but_sel = shift;
my $sth_but_upd = shift;

$dbh->{'AutoCommit'} = 0;
$dbh->{'RaiseError'} = 1;
eval{
	my $sql;
	my $sth_but_parent;
	my $sth_bti_upd;
	my $sth_but_child;
	my $sth_bti_upd_depth;
	my $sth_bti_child;
	my $rows;
	my $col_num;
	my $cdi_id;
	my $cdi_pid;
	my $cti_depth;

	$rows = $dbh->do(qq|DELETE FROM concept_tree_info WHERE ci_id=$ci_id AND cb_id=$cb_id|) or die $dbh->errstr;
	print sprintf(qq|%3d:[%6d]\n|,__LINE__,$rows);

	$sql=<<SQL;
INSERT INTO concept_tree_info (ci_id,cb_id,cdi_id,crl_id)
SELECT
 ci_id,cb_id,cdi_id,0
FROM (
 select ci_id,cb_id,cdi_id from concept_tree where ci_id=$ci_id AND cb_id=$cb_id
 union
 select ci_id,cb_id,cdi_pid as cdi_id from concept_tree where ci_id=$ci_id AND cb_id=$cb_id
) as a
GROUP BY
 ci_id,cb_id,cdi_id
SQL
	$rows = $dbh->do($sql) or die $dbh->errstr;
	print sprintf(qq|%3d:[%6d]\n|,__LINE__,$rows);

	foreach my $crl_id (qw/3 4/){
		$sql=<<SQL;
INSERT INTO concept_tree_info (ci_id,cb_id,cdi_id,crl_id)
SELECT
 ci_id,cb_id,cdi_id,bul_id
FROM (
 select ci_id,cb_id,cdi_id,bul_id from concept_tree where ci_id=$ci_id AND cb_id=$cb_id AND bul_id=$crl_id
 union
 select ci_id,cb_id,cdi_pid as cdi_id,bul_id from concept_tree where ci_id=$ci_id AND cb_id=$cb_id AND bul_id=$crl_id
) as a
GROUP BY
 ci_id,cb_id,cdi_id,bul_id
SQL
		$rows = $dbh->do($sql) or die $dbh->errstr;
		print sprintf(qq|%3d:[%6d]\n|,__LINE__,$rows);
	}

	print STDERR __LINE__.':ANALYZE;'."\n";
	$dbh->do(qq|ANALYZE concept_tree_info;|) or die $!;

	foreach my $crl_id (qw/0 3 4/){
		$sql=qq|UPDATE concept_tree_info SET cti_cnum=?,cti_cids=? WHERE ci_id=$ci_id AND cb_id=$cb_id AND crl_id=$crl_id AND cdi_id=?|;
		$sth_bti_upd = $dbh->prepare($sql) or die $dbh->errstr;

		$sql=qq|UPDATE concept_tree_info SET cti_depth=? WHERE ci_id=$ci_id AND cb_id=$cb_id AND crl_id=$crl_id AND cdi_id=?|;
		$sth_bti_upd_depth = $dbh->prepare($sql) or die $dbh->errstr;

		my %ID2DEPTH;
		my %PID2CID;
		my %CID2PID;
		if($crl_id eq '0'){
			$sql=qq|select cdi_id,cdi_pid from concept_tree where ci_id=$ci_id AND cb_id=$cb_id AND cdi_id IS NOT NULL AND cdi_pid IS NOT NULL AND cdi_id<>cdi_pid|;
		}else{
			$sql=qq|select cdi_id,cdi_pid from concept_tree where ci_id=$ci_id AND cb_id=$cb_id AND bul_id=$crl_id AND cdi_id IS NOT NULL AND cdi_pid IS NOT NULL AND cdi_id<>cdi_pid|;
		}
		$sth_but_parent = $dbh->prepare($sql) or die $dbh->errstr;
		$sth_but_parent->execute() or die $dbh->errstr;
		$rows = $sth_but_parent->rows();
		print sprintf(qq|%3d:[%d]:[%6d]\n|,__LINE__,$crl_id,$rows);
		$col_num=0;
		$sth_but_parent->bind_col(++$col_num, \$cdi_id, undef);
		$sth_but_parent->bind_col(++$col_num, \$cdi_pid, undef);
		while($sth_but_parent->fetch){
			$PID2CID{$cdi_pid}->{$cdi_id} = undef;
			$CID2PID{$cdi_id}->{$cdi_pid} = undef;
		}
		$sth_but_parent->finish;
		undef $sth_but_parent;

		$rows = scalar keys(%PID2CID);
		print sprintf(qq|%3d:[%d]:[%6d]\n|,__LINE__,$crl_id,$rows);

		foreach my $cdi_id (sort {$a<=>$b} keys(%PID2CID)){
			--$rows;
			next unless(defined $cdi_id);
			print sprintf(qq|\r%3d:[%d]:[%6d]:[%6d]|,__LINE__,$crl_id,$rows,$cdi_id);

			my $use_cdi_cid = &upd_children(\%PID2CID,\%ID2DEPTH,$cdi_id);
			delete $use_cdi_cid->{$cdi_id};

			my $cti_cids_arr = [map {$_+0} sort {$a<=>$b} keys(%$use_cdi_cid)];
			my $cti_cnum = scalar @$cti_cids_arr;
			my $cti_cids = $cti_cnum ? &JSON::XS::encode_json($cti_cids_arr) : undef;

			$sth_bti_upd->execute($cti_cnum,$cti_cids,$cdi_id) or die $dbh->errstr;
			$sth_bti_upd->finish;

			print sprintf(qq|\r%3d:[%d]:[%6d]:[%6d]:[%6d]                       |,__LINE__,$crl_id,$rows,$cdi_id,$cti_cnum);
			print "\n";
		}
		$dbh->commit();
		print "\n";
		undef $sth_bti_upd;

		$rows = scalar keys(%ID2DEPTH);
		print sprintf(qq|%3d:[%d]:[%6d]\n|,__LINE__,$crl_id,$rows);
		foreach my $cdi_id (keys(%ID2DEPTH)){
			print sprintf(qq|\r%3d:[%d]:[%6d]|,__LINE__,$crl_id,--$rows);
			$sth_bti_upd_depth->execute($ID2DEPTH{$cdi_id},$cdi_id) or die $dbh->errstr;
			$sth_bti_upd_depth->finish;
		}
		$dbh->commit();
		print "\n";
		undef $sth_bti_upd_depth;


		$sql=qq|UPDATE concept_tree_info SET cti_pnum=?,cti_pids=? WHERE ci_id=$ci_id AND cb_id=$cb_id AND crl_id=$crl_id AND cdi_id=?|;
		$sth_bti_upd = $dbh->prepare($sql) or die $dbh->errstr;

		$rows = scalar keys(%CID2PID);
		print sprintf(qq|%3d:[%d]:[%6d]\n|,__LINE__,$crl_id,$rows);

		foreach my $cdi_id (sort {$a<=>$b} keys(%CID2PID)){
			--$rows;
			next unless(defined $cdi_id);

			print sprintf(qq|\r%3d:[%d]:[%6d]:[%6d]|,__LINE__,$crl_id,$rows,$cdi_id);

			my $use_cdi_pid = &get_parent(\%CID2PID,$cdi_id);
			delete $use_cdi_pid->{$cdi_id};

			my $cti_pids_arr = [map {$_+0} sort {$a<=>$b} keys(%$use_cdi_pid)];
			my $cti_pnum = scalar @$cti_pids_arr;
			my $cti_pids = $cti_pnum ? &JSON::XS::encode_json($cti_pids_arr) : undef;

			$sth_bti_upd->execute($cti_pnum,$cti_pids,$cdi_id) or die $dbh->errstr;
			$sth_bti_upd->finish;

			print sprintf(qq|\r%3d:[%d]:[%6d]:[%6d]:[%6d]|,__LINE__,$crl_id,$rows,$cdi_id,$cti_pnum);
			print "\n";
		}
		print "\n";
		undef $sth_bti_upd;


		$dbh->commit();
	}
#	$dbh->rollback;
};
if($@){
	print __LINE__,":",$@,"\n";
	$dbh->rollback;
}
$dbh->{'AutoCommit'} = 1;
$dbh->{'RaiseError'} = 0;

#print STDERR __LINE__.':ANALYZE;'."\n";
#$dbh->do(qq|ANALYZE;|) or die $!;

exit;

sub upd_children {
	my $pid2cid = shift;
	my $id2depth = shift;
	my $cdi_id = shift;
	my $use_cdi_id = shift;
	my $depth = shift;
	$use_cdi_id = {} unless(defined $use_cdi_id);
	$depth = 0 unless(defined $depth);
	return if(exists $use_cdi_id->{$cdi_id});
	$use_cdi_id->{$cdi_id} = undef;

	if(exists $pid2cid->{$cdi_id}){
		foreach my $cdi_cid (keys(%{$pid2cid->{$cdi_id}})){
			print sprintf(qq|\r%3d:[%6d]:[%6d]:[%6d]|,__LINE__,$cdi_id,scalar keys(%$use_cdi_id),$depth);
			&upd_children($pid2cid,$id2depth,$cdi_cid,$use_cdi_id,$depth+1);
		}
	}
	print sprintf(qq|\r%3d:[%6d]:[%6d]:[%6d]|,__LINE__,$cdi_id,scalar keys(%$use_cdi_id),$depth);

	if(exists $id2depth->{$cdi_id}){
		$id2depth->{$cdi_id} = $depth if($id2depth->{$cdi_id} < $depth);
	}else{
		$id2depth->{$cdi_id} = $depth;
	}


	return $use_cdi_id;
}


sub get_parent {
	my $cid2pid = shift;
	my $cdi_id = shift;
	my $use_cdi_id = shift;
	$use_cdi_id = {} unless(defined $use_cdi_id);
	return if(exists $use_cdi_id->{$cdi_id});
	$use_cdi_id->{$cdi_id} = undef;

	if(exists $cid2pid->{$cdi_id}){
		foreach my $cdi_pid (sort {$a<=>$b} keys(%{$cid2pid->{$cdi_id}})){
			print sprintf(qq|\r%3d:[%6d]:[%6d]|,__LINE__,$cdi_id,scalar keys(%$use_cdi_id));
			&get_parent($cid2pid,$cdi_pid,$use_cdi_id);
		}
	}
	print sprintf(qq|\r%3d:[%6d]:[%6d]|,__LINE__,$cdi_id,scalar keys(%$use_cdi_id));
	return $use_cdi_id;
}
