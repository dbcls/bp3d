#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use FindBin;
use lib qq|$FindBin::Bin/../..|,qq|$FindBin::Bin/../../../lib|,qq|$FindBin::Bin/../../../../ag-common/lib|;

use Getopt::Long qw(:config posix_default no_ignore_case gnu_compat);
my $config = {
	db => 'bp3d',
	host => '127.0.0.1',
	port => '8543'
};
&Getopt::Long::GetOptions($config,qw/
	db|d=s
	host|h=s
	port|p=s
/) or exit 1;

$ENV{'AG_DB_NAME'} = $config->{'db'};
$ENV{'AG_DB_HOST'} = $config->{'host'};
$ENV{'AG_DB_PORT'} = $config->{'port'};

require "common_db.pl";
my $dbh = &get_dbh();

my $ci_id;
my $cb_id;
if(scalar @ARGV < 2){
	warn qq|$0 concept_info_id concept_build_id\n| ;
	warn qq|#optins :\n| ;
	warn qq|# --db,-d   : database name [default:$config->{'db'}]\n|;
	warn qq|# --host,-h : database host [default:$config->{'host'}]\n| ;
	warn qq|# --port,-p : database port [default:$config->{'port'}]\n| ;
	warn qq|#concept_info_id:concept_build_id:\n| ;
	my $sql=<<SQL;
select info.ci_id,cb_id,ci_name,cb_name,cb_release from concept_build
left join (select ci_id,ci_name from concept_info where ci_delcause is null) as info on (concept_build.ci_id=info.ci_id)
where cb_delcause is null
order by info.ci_id,cb_id;
SQL
	my $ci_name;
	my $cb_name;
	my $cb_release;
	my $sth = $dbh->prepare($sql);
	$sth->execute() or die $dbh->errstr;
	$sth->bind_col(1, \$ci_id, undef);
	$sth->bind_col(2, \$cb_id, undef);
	$sth->bind_col(3, \$ci_name, undef);
	$sth->bind_col(4, \$cb_name, undef);
	$sth->bind_col(5, \$cb_release, undef);
	while($sth->fetch){
		warn sprintf("             %-2d :            %3d : %-5s : %-25s : %10s\n",$ci_id,$cb_id,$ci_name,"$cb_name",$cb_release);
	}
	$sth->finish;
	undef $sth;
	exit 1;
}
$ci_id = $ARGV[0];
$cb_id = $ARGV[1];

my $sth_sel_info = $dbh->prepare(qq|select cdi_id from concept_data_info where ci_id=$ci_id and cdi_name=?|);

sub get_cdi {
	my $cdi_name = shift;
	my $cdi_id;
	$sth_sel_info->execute($cdi_name) or die $dbh->errstr;
	$sth_sel_info->bind_col(1, \$cdi_id, undef);
	$sth_sel_info->fetch;
	$sth_sel_info->finish;
	return $cdi_id;
}

my %USE_ID = ();

#$dbh->{'AutoCommit'} = 0;
#$dbh->{'RaiseError'} = 1;
eval{

	my $sth_upd = $dbh->prepare(qq|update concept_data set phy_id=null where ci_id=$ci_id and cb_id=$cb_id and phy_id is not null|);
	$sth_upd->execute();
	print "UPDATE:[",$sth_upd->rows,"]\n";
	$sth_upd->finish;
	undef $sth_upd;

	my $sth_select = $dbh->prepare(qq|select * from concept_data where ci_id=$ci_id and cb_id=$cb_id and phy_id is null|);
	$sth_select->execute();
	print "TARGET:[",$sth_select->rows,"]\n";
	undef $sth_select;

	%USE_ID = ();
	print "UPDATE:FMA67112:[2]\n";
	my $rtn = &update(&get_cdi('FMA67112'),2);
	print "\n[$rtn]\n";

	$sth_select = $dbh->prepare(qq|select * from concept_data where ci_id=$ci_id and cb_id=$cb_id and phy_id is null|);
	$sth_select->execute();
	print "TARGET:[",$sth_select->rows,"]\n";
	undef $sth_select;

	%USE_ID = ();
	print "UPDATE:FMA67165:[1]\n";
	$rtn = &update(&get_cdi('FMA67165'),1);
	print "\n[$rtn]\n";

#	$dbh->commit();
};
if($@){
	print $@,"\n";
#	$dbh->rollback;
}
#$dbh->{'AutoCommit'} = 1;
#$dbh->{'RaiseError'} = 0;

#$dbh->do(qq|ANALYZE;|) or die $dbh->errstr;

exit;

sub update {
	my $cdi_id = shift;
	my $phy_id = shift;

	$USE_ID{$cdi_id} = "";
	print sprintf("\r[%5d]:UPDATE:[%6d]:[%d][%6d]\r",__LINE__,$cdi_id,$phy_id,scalar keys(%USE_ID));

	my $cdi_id2;

	my $sth_upd = $dbh->prepare(qq|update concept_data set phy_id=? where cdi_id=? and ci_id=$ci_id and cb_id=$cb_id and phy_id is null|);
	$sth_upd->execute($phy_id,$cdi_id);
	my $rows = $sth_upd->rows();
	$sth_upd->finish;
	undef $sth_upd;
	unless($rows>0){
		print "\n";
		warn __LINE__,":[$cdi_id][$phy_id][$rows]\n";
		return undef;
	}

	my @IDS;
	my $sql=<<SQL;
select concept_tree.cdi_id from concept_tree
left join (select ci_id,cb_id,cdi_id,phy_id from concept_data) as d on d.ci_id=concept_tree.ci_id and d.cb_id=concept_tree.cb_id and d.cdi_id=concept_tree.cdi_id
where 
 concept_tree.cdi_pid=? and
 concept_tree.ci_id=$ci_id and
 concept_tree.cb_id=$cb_id and
 concept_tree.bul_id=3 and
 d.phy_id is null
SQL
	my $sth_select = $dbh->prepare($sql);
	$sth_select->execute($cdi_id);
	$sth_select->bind_col(1, \$cdi_id2, undef);
	while($sth_select->fetch){
		push(@IDS,$cdi_id2) if(defined $cdi_id2);
	}
	$sth_select->finish;
	undef $sth_select;

	foreach my $cdi_id2 (@IDS){
		my $rtn = &update($cdi_id2,$phy_id);
		if(defined $rtn){
			$rows += $rtn;
		}else{
			print "\n";
			warn __LINE__,":[$cdi_id2][$phy_id][$rtn]\n";
			return undef;
		}
	}
	return $rows;
}
