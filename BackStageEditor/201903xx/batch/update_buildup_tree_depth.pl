#!/bp3d/local/perl/bin/perl

use strict;

use Encode::Guess;
use Data::Dumper;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;

require "webgl_common.pl";

my $dbh = &get_dbh();

my %CIDS;

$dbh->{AutoCommit} = 0;
$dbh->{RaiseError} = 1;
eval{

	$dbh->do(qq|update buildup_tree set but_depth=0;|) or die $dbh->errstr;

	my $sql=<<SQL;
select ci_id,cb_id,bul_id,cdi_id from buildup_tree where cdi_pid is null AND but_delcause is NULL
SQL
	my $sth_but_root = $dbh->prepare($sql) or die $dbh->errstr;

	my $sql=<<SQL;
select cdi_id from buildup_tree where ci_id=? AND cb_id=? AND bul_id=? AND cdi_pid=? AND but_depth<? AND but_delcause is NULL
SQL
	my $sth_but_sel = $dbh->prepare($sql) or die $dbh->errstr;

	my $sql=<<SQL;
update buildup_tree set but_depth=? WHERE ci_id=? AND cb_id=? AND bul_id=? AND cdi_id=? AND cdi_pid is null
SQL
	my $sth_but_upd = $dbh->prepare($sql) or die $dbh->errstr;

	my %ROOT;
	$sth_but_root->execute() or die $dbh->errstr;
	my $ci_id;
	my $cb_id;
	my $bul_id;
	my $cdi_id;
	my $col_num=0;
	$sth_but_root->bind_col(++$col_num, \$ci_id, undef);
	$sth_but_root->bind_col(++$col_num, \$cb_id, undef);
	$sth_but_root->bind_col(++$col_num, \$bul_id, undef);
	$sth_but_root->bind_col(++$col_num, \$cdi_id, undef);
	while($sth_but_root->fetch){
		next unless(defined $ci_id && defined $cb_id && defined $bul_id && defined $cdi_id);
		$ROOT{qq|$ci_id\t$cb_id\t$bul_id\t$cdi_id|} = undef;
	}
	$sth_but_root->finish;
	undef $sth_but_root;

	my $but_depth=1;
	foreach my $key (sort keys(%ROOT)){
		my($ci_id,$cb_id,$bul_id,$cdi_id) = split(/\t/,$key);
		$sth_but_upd->execute($but_depth,$ci_id,$cb_id,$bul_id,$cdi_id) or die $dbh->errstr;
		$sth_but_upd->finish;

	}

	undef $sth_but_upd;
	my $sql=<<SQL;
update buildup_tree set but_depth=? WHERE ci_id=? AND cb_id=? AND bul_id=? AND cdi_id=? AND cdi_pid=?
SQL
	my $sth_but_upd = $dbh->prepare($sql) or die $dbh->errstr;


	foreach my $key (sort keys(%ROOT)){
		my($ci_id,$cb_id,$bul_id,$cdi_id) = split(/\t/,$key);
		&upd($sth_but_sel,$sth_but_upd,$ci_id,$cb_id,$bul_id,$cdi_id,$but_depth+1);
	}

	undef $sth_but_upd;
	my $sql=<<SQL;
update buildup_tree set but_cnum=?,but_cids=? WHERE ci_id=? AND cb_id=? AND bul_id=? AND cdi_id=?
SQL
	my $sth_but_upd = $dbh->prepare($sql) or die $dbh->errstr;

	foreach my $key (sort keys(%CIDS)){
		my($ci_id,$cb_id,$bul_id,$cdi_id) = split(/\t/,$key);
		my $but_cnum = scalar keys(%{$CIDS{$key}});
		my @but_cids_arr = sort keys(%{$CIDS{$key}});
		my $but_cids = JSON::XS::encode_json(\@but_cids_arr);
		$sth_but_upd->execute($but_cnum,$but_cids,$ci_id,$cb_id,$bul_id,$cdi_id) or die $dbh->errstr;
		$sth_but_upd->finish;
	}

	$dbh->commit();
#	$dbh->rollback;
};
if($@){
	print __LINE__,":",$@,"\n";
	$dbh->rollback;
}
$dbh->{AutoCommit} = 1;
$dbh->{RaiseError} = 0;

exit;

sub upd {
	my $sth_but_sel = shift;
	my $sth_but_upd = shift;
	my $ci_id = shift;
	my $cb_id = shift;
	my $bul_id = shift;
	my $cdi_pid = shift;
	my $but_depth = shift;

	my %IDS;
	$sth_but_sel->execute($ci_id,$cb_id,$bul_id,$cdi_pid,$but_depth) or die $dbh->errstr;

#	print __LINE__,qq|:[$but_depth]:[,$sth_but_sel->rows(),qq|]\n|;

	my $rows = $sth_but_sel->rows();
	if($rows>0){
		print sprintf(qq|%02d:[%02d]:[%02d]:[%d]:[%d]:[%d]:[%d]\n|,__LINE__,$but_depth,$rows,$ci_id,$cb_id,$bul_id,$cdi_pid);
		my $cdi_id;
		my $col_num=0;
		$sth_but_sel->bind_col(++$col_num, \$cdi_id, undef);
		while($sth_but_sel->fetch){
			next unless(defined $ci_id && defined $cb_id && defined $bul_id && defined $cdi_id);
			next if($cdi_pid == $cdi_id);
			$IDS{$cdi_id} = undef;

			$CIDS{qq|$ci_id\t$cb_id\t$bul_id\t$cdi_pid|}->{$cdi_id} = undef;
		}
	}
	$sth_but_sel->finish;

	if($rows>0){
		foreach my $cdi_id (sort keys(%IDS)){
			$sth_but_upd->execute($but_depth,$ci_id,$cb_id,$bul_id,$cdi_id,$cdi_pid) or die $dbh->errstr;
			$sth_but_upd->finish;
		}
		foreach my $cdi_id (sort keys(%IDS)){
			&upd($sth_but_sel,$sth_but_upd,$ci_id,$cb_id,$bul_id,$cdi_id,$but_depth+1);

			my $c_key = qq|$ci_id\t$cb_id\t$bul_id\t$cdi_id|;
			next unless(exists $CIDS{$c_key});
			my $p_key = qq|$ci_id\t$cb_id\t$bul_id\t$cdi_pid|;
			foreach my $cdi_cid (keys(%{$CIDS{$c_key}})){
				$CIDS{$p_key}->{$cdi_cid} = undef;
			}
		}
	}
}
