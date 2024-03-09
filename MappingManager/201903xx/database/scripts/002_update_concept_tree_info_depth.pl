#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use Time::HiRes;
use JSON::XS;

my $t0 = [&Time::HiRes::gettimeofday()];

use FindBin;
#use lib qq|$FindBin::Bin/../..|,qq|$FindBin::Bin/../../../lib|,qq|$FindBin::Bin/../../../../ag-common/lib|;
#use cgi_lib::common;
use lib qq|$FindBin::Bin/../../cgi_lib|;

#my $c = 1912;
#my @A = qw/21 71735 1912 71735 1912 71735 1912 71735 1912 71735 1912 71735 1912 71735 1912 69999 18971 59354 4484 15487/;
#my @B = grep {$_."" == $c} @A;
#&cgi_lib::common::message(scalar @B);
#exit;

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

#require "common_db.pl";
require "webgl_common.pl";
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

my $sth_but_sel;
my $sth_but_upd;

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
	my $cti_cnum;
	my $cti_pnum;

	print STDERR __LINE__.':ANALYZE;'."\n";
	$dbh->do(qq|ANALYZE concept_tree_info;|) or die $!;

	foreach my $crl_id (qw/0 3 4/){
#	if(1){
#		my $crl_id = 4;

		$sql=qq|UPDATE concept_tree_info SET cti_depth=? WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=? AND crl_id=$crl_id|;
		$sth_bti_upd_depth = $dbh->prepare($sql) or die $dbh->errstr;

		my %ID2DEPTH;
		my %PID2CID;
		my %CID2PID;
		my %CNUM;
		my %ALL_CNUM;
		my %ALL_PNUM;

		$sql=qq|select cdi_id,cti_cnum,cti_pnum from concept_tree_info where ci_id=$ci_id AND cb_id=$cb_id AND crl_id=$crl_id|;
		$sth_but_parent = $dbh->prepare($sql) or die $dbh->errstr;
		$sth_but_parent->execute() or die $dbh->errstr;
		$rows = $sth_but_parent->rows();
		print sprintf(qq|%3d:[%d]:[%6d]\n|,__LINE__,$crl_id,$rows);
		$col_num=0;
		$sth_but_parent->bind_col(++$col_num, \$cdi_id, undef);
		$sth_but_parent->bind_col(++$col_num, \$cti_cnum, undef);
		$sth_but_parent->bind_col(++$col_num, \$cti_pnum, undef);
		while($sth_but_parent->fetch){
			$ALL_CNUM{$cdi_id} = $cti_cnum - 0;
			$ALL_PNUM{$cdi_id} = $cti_pnum - 0;
		}
		$sth_but_parent->finish;
		undef $sth_but_parent;

		if($crl_id eq '0'){
			$sql=qq|select cdi_id,cdi_pid from concept_tree where ci_id=$ci_id AND cb_id=$cb_id AND cdi_id IS NOT NULL AND cdi_pid IS NOT NULL AND cdi_id<>cdi_pid|;
#			$sql=qq|select cdi_id,cdi_pid from concept_tree where ci_id=$ci_id AND cb_id=$cb_id AND bul_id=3 AND cdi_id IS NOT NULL AND cdi_pid IS NOT NULL AND cdi_id<>cdi_pid|;
		}else{
			$sql=qq|select cdi_id,cdi_pid from concept_tree where ci_id=$ci_id AND cb_id=$cb_id AND crl_id=$crl_id AND cdi_id IS NOT NULL AND cdi_pid IS NOT NULL AND cdi_id<>cdi_pid|;
		}
		$sth_but_parent = $dbh->prepare($sql) or die $dbh->errstr;
		$sth_but_parent->execute() or die $dbh->errstr;
		$rows = $sth_but_parent->rows();
		print sprintf(qq|%3d:[%d]:[%6d]\n|,__LINE__,$crl_id,$rows);
		$col_num=0;
		$sth_but_parent->bind_col(++$col_num, \$cdi_id, undef);
		$sth_but_parent->bind_col(++$col_num, \$cdi_pid, undef);
		while($sth_but_parent->fetch){
			next unless(exists $ALL_CNUM{$cdi_id} && exists $ALL_CNUM{$cdi_pid});

			$PID2CID{$cdi_pid}->{$cdi_id} = undef;
			$CID2PID{$cdi_id}->{$cdi_pid} = undef;

			$CNUM{$cdi_pid} = 0 unless(exists $CNUM{$cdi_pid});
			$CNUM{$cdi_id} = 0 unless(exists $CNUM{$cdi_id});
			$CNUM{$cdi_pid}++;
		}
		$sth_but_parent->finish;
		undef $sth_but_parent;


		$rows = scalar keys(%PID2CID);
		print sprintf(qq|%3d:[%d]:[%6d]\n|,__LINE__,$crl_id,$rows);

=pod
		foreach my $cdi_id (keys(%PID2CID)){
			unless(exists $ALL_PNUM{$cdi_id}){
				&cgi_lib::common::message($cdi_id);
				delete $PID2CID{$cdi_id};
#				die __LINE__;
			}
			unless(exists $ALL_CNUM{$cdi_id}){
				&cgi_lib::common::message($cdi_id);
				delete $PID2CID{$cdi_id};
#				die __LINE__;
			}
			unless(exists $CNUM{$cdi_id}){
				&cgi_lib::common::message($cdi_id);
				die __LINE__;
			}
		}
=cut

		foreach my $cdi_id (sort {$ALL_PNUM{$a}<=>$ALL_PNUM{$b}} sort {$ALL_CNUM{$b}<=>$ALL_CNUM{$a}} sort {$CNUM{$a}<=>$CNUM{$b}} keys(%PID2CID)){
#		if(1){
#			my $cdi_id = 21;
#			my $cdi_id = 61804;
			--$rows;
			next unless(defined $cdi_id);

			print sprintf(qq|%3d:[%d]:[%6d]:[%6d]\n|,__LINE__,$crl_id,$rows,$cdi_id);

			&get_depth(\%PID2CID,\%ALL_PNUM,\%ALL_CNUM,\%CNUM,\%ID2DEPTH,$cdi_id);

			print sprintf(qq|\n%3d:[%d]:[%6d]:[%6d]:[%6d]\n|,__LINE__,$crl_id,$rows,$cdi_id,$ID2DEPTH{$cdi_id});
		}
#		print "\n";

		$rows = scalar keys(%ID2DEPTH);
		print sprintf(qq|%3d:[%d]:[%6d]\n|,__LINE__,$crl_id,$rows);
		foreach my $cdi_id (keys(%ID2DEPTH)){
			print sprintf(qq|\r%3d:[%d]:[%6d]:[%5d]:[%6d]|,__LINE__,$crl_id,$cdi_id,$ID2DEPTH{$cdi_id},--$rows);
			$sth_bti_upd_depth->execute($ID2DEPTH{$cdi_id},$cdi_id) or die $dbh->errstr;
			$sth_bti_upd_depth->finish;
		}

		print "\n\n";
		undef $sth_bti_upd_depth;

	}
};
if($@){
	print __LINE__,":",$@,"\n";
}

#print STDERR __LINE__.':ANALYZE;'."\n";
#$dbh->do(qq|ANALYZE;|) or die $!;

exit;

sub get_depth {
	my $pid2cid = shift;
	my $all_pnum = shift;
	my $all_cnum = shift;
	my $cnum = shift;
	my $id2depth = shift;
	my $cdi_id = shift;
	my $depth = shift;

	$depth = 0 unless(defined $depth);
	if(exists $id2depth->{$cdi_id}){
		return;
	}
	$id2depth->{$cdi_id} = $depth;
	print sprintf(qq|\r%3d:[%6d]:[%6d]:[%6d]|,__LINE__,$cdi_id,scalar keys(%$id2depth),$depth);
#	die __LINE__;

	if(exists $pid2cid->{$cdi_id}){
		foreach my $cdi_cid (sort {$all_pnum->{$a}<=>$all_pnum->{$b}} sort {$all_cnum->{$b}<=>$all_cnum->{$a}} sort {$cnum->{$a}<=>$cnum->{$b}} keys(%{$pid2cid->{$cdi_id}})){
			print sprintf(qq|\r%3d:[%6d]:[%6d]:[%6d]|,__LINE__,$cdi_id,scalar keys(%$id2depth),$depth);
			&get_depth($pid2cid,$all_pnum,$all_cnum,$cnum,$id2depth,$cdi_cid,$depth+1);
		}
	}
	return;
}
