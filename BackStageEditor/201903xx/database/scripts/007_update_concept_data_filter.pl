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

require "common.pl";
require "common_db.pl";

my $dbh = &get_dbh();

#my $root_cdi_id = undef;
#eval{$root_cdi_id = ROOT_CDI_ID;};
my $root_cdi_id;

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
	$sth->execute();
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

#$dbh->{'AutoCommit'} = 0;
#$dbh->{'RaiseError'} = 1;
eval{


	my $table = qq|concept_data_filter|;

	$dbh->do(qq|delete from $table where ci_id=$ci_id and cb_id=$cb_id|) or die;

	my $sql_cdi_name = qq|select cdi_id from concept_data_info where cdi_delcause is null and ci_id=$ci_id and cdi_name=?|;
	my $sth_cdi_name = $dbh->prepare($sql_cdi_name) or die;

	my $sql_ins = qq|insert into $table (ci_id,cb_id,cdi_id,cdf_id,cdf_entry,cdf_openid) values (?,?,?,?,'now()','system')|;
	my $sth_ins = $dbh->prepare($sql_ins) or die;

	my $sql_fma_isa = qq|select cdi_id from concept_tree where ci_id=$ci_id and cb_id=$cb_id and bul_id=? and cdi_pid=? group by cdi_id|;
	my $sth_fma_isa = $dbh->prepare($sql_fma_isa) or die;

	my $sql_filter = qq|select cdi_id from $table where ci_id=$ci_id and cb_id=$cb_id and cdi_id=? and cdf_id=?|;
	my $sth_filter = $dbh->prepare($sql_filter) or croak $dbh->errstr;

	my $sql_cb = qq|select cdi_id from concept_data where ci_id=$ci_id and cb_id=$cb_id and cdi_id=?|;
	my $sth_cb = $dbh->prepare($sql_cb) or die;

	sub get_cdi_id {
		my $cdf_id = shift;
		my $cdi_pid = shift;
		my $bul_id = shift;
		my $hash = shift;

		$bul_id = 3 unless(defined $bul_id);
		$hash = {} unless(defined $hash);

		my %FID = ();
		my $sth_fma;

		if($cdf_id =~ /^FMA/){
			my $cdi_id;
			$sth_cdi_name->execute($cdf_id) or croak $dbh->errstr;
			$sth_cdi_name->bind_col(1, \$cdi_id, undef);
			$sth_cdi_name->fetch;
			$sth_cdi_name->finish;
			return unless(defined $cdi_id);
			$cdf_id = $cdi_id;
		}
		if($cdi_pid =~ /^FMA/){
			my $cdi_id;
			$sth_cdi_name->execute($cdi_pid) or croak $dbh->errstr;
			$sth_cdi_name->bind_col(1, \$cdi_id, undef);
			$sth_cdi_name->fetch;
			$sth_cdi_name->finish;
			return unless(defined $cdi_id);
			$cdi_pid = $cdi_id;
		}

		$sth_cb->execute($cdf_id) or croak $dbh->errstr;
		my $cdf_id_rows = $sth_cb->rows();
		$sth_cdi_name->finish;

		$sth_cb->execute($cdi_pid) or croak $dbh->errstr;
		my $cdi_pid_rows = $sth_cb->rows();
		$sth_cdi_name->finish;

		return unless($cdf_id_rows && $cdi_pid_rows);

		$hash->{$cdi_pid} = undef;

		$sth_filter->execute($cdi_pid,$cdf_id) or croak $dbh->errstr;
		my $rows = $sth_filter->rows();
		$sth_filter->finish;
		return if($rows>0);

		$sth_ins->execute($ci_id,$cb_id,$cdi_pid,$cdf_id) or croak $dbh->errstr;
		$sth_ins->finish;

		$sth_fma = $sth_fma_isa;

		my $cdi_id;
		$sth_fma->execute($bul_id,$cdi_pid) or croak $dbh->errstr;
		$sth_fma->bind_col(1, \$cdi_id, undef);
		while($sth_fma->fetch){
			$FID{$cdi_id} = undef if(defined $cdi_id);
		}
		$sth_fma->finish;
		foreach my $cdi_id (keys(%FID)){
			next if(exists($hash->{$cdi_id}));
			&get_cdi_id($cdf_id,$cdi_id,$bul_id,$hash);
		}
	}

	&get_cdi_id('FMA5018','FMA5018');
	&get_cdi_id('FMA5018','FMA23881');
	&get_cdi_id('FMA5018','FMA85544');
	&get_cdi_id('FMA5018','FMA71324');

	&get_cdi_id('FMA5022','FMA5022');
	&get_cdi_id('FMA5022','FMA10474');
	&get_cdi_id('FMA5022','FMA32558');
	&get_cdi_id('FMA5022','FMA85453');

	&get_cdi_id('FMA3710','FMA3710');
	&get_cdi_id('FMA3710','FMA50722');
	&get_cdi_id('FMA3710','FMA7161',4);
	&get_cdi_id('FMA3710','FMA228642',4);
	&get_cdi_id('FMA3710','FMA228684',4);
	&get_cdi_id('FMA3710','FMA269098',4);

	&get_cdi_id('FMA3710','FMA63812');#追加(2013/04/25)
	&get_cdi_id('FMA3710','FMA63814');#追加(2013/04/25)
	&get_cdi_id('FMA3710','FMA49894',4);#追加(2013/04/25)


#	$dbh->commit;
};
if($@){
	print $@,"\n";
#	$dbh->rollback;
}

#$dbh->{'AutoCommit'} = 1;
#$dbh->{'RaiseError'} = 0;
exit;

#print STDERR __LINE__.':ANALYZE;'."\n";
#$dbh->do(qq|ANALYZE;|) or die $!;
