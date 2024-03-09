#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';
use FindBin;

use lib qq|$FindBin::Bin/../..|,qq|$FindBin::Bin/../../../lib|,qq|$FindBin::Bin/../../../../ag-common/lib|;

use Getopt::Long qw(:config posix_default no_ignore_case gnu_compat);
my $config = {
	host => '127.0.0.1',
	port => '8543'
};
&Getopt::Long::GetOptions($config,qw/
	host|h=s
	port|p=s
/) or exit 1;

$ENV{'AG_DB_HOST'} = $config->{'host'};
$ENV{'AG_DB_PORT'} = $config->{'port'};

require "common.pl";
require "common_db.pl";

my $dbh = &get_dbh();

#my $root_cdi_id = undef;
#eval{$root_cdi_id = ROOT_CDI_ID;};
my $root_cdi_id;

my $ci_id;

if(scalar @ARGV < 2){
	say STDERR qq|$0 concept_info_id FMA2TA_file_path FMA2LANG_Latin_file_path| ;
	say STDERR qq|#optins :| ;
	say STDERR qq|# --host,-h : database host [default:$config->{'host'}]| ;
	say STDERR qq|# --port,-p : database port [default:$config->{'port'}]| ;
	say STDERR qq|#concept_info_id:| ;
	my $sql=<<SQL;
select
 ci_id,
 ci_name
from
 concept_info
where
 ci_delcause is null and ci_use
order by ci_id;
SQL
	my $ci_name;
	my $sth = $dbh->prepare($sql);
	$sth->execute();
	$sth->bind_col(1, \$ci_id, undef);
	$sth->bind_col(2, \$ci_name, undef);
	while($sth->fetch){
		say STDERR sprintf("              %-2s: %-5s",$ci_id,$ci_name);
	}
	$sth->finish;
	undef $sth;
	exit 1;
}
$ci_id = shift @ARGV;
my $FMA2TA_file_path = shift @ARGV;
my $FMA2LANG_Latin_file_path = shift @ARGV;

my %FMA2TA;
open(my $IN, $FMA2TA_file_path) or die qq|$! [$FMA2TA_file_path]|;
flock($IN, 1);
while(<$IN>){
	chomp;
	my($id,$ta) = split(/\t/);
	if($id =~ /^(FMA):([0-9]+)$/){
		$id = qq|$1$2|;
	}else{
		undef $id;
	}
	if(length $ta){
		my @TA = map {
			if(/^([A-Z]+)([0-9\.]+)$/){
				my $t1 = $1;
				my $t2 = $2;
				$t2 =~ s/^[^0-9]+//g;
				$t2 =~ s/[^0-9]+$//g;
				qq|$t1$t2|;
			}else{
				$_;
			}
		} sort grep {/^[A-Z]+[0-9\.]+$/} split(/\|/, $ta);
		$ta = join('|', @TA);
		undef $ta unless(length $ta);
	}
	next unless(defined $id && defined $ta);
	say qq|$id\t$ta| if(exists $FMA2TA{$id});
	$FMA2TA{$id} = $ta;
}
close($IN);

my %FMA2LANG;
open($IN, $FMA2LANG_Latin_file_path) or die qq|$! [$FMA2LANG_Latin_file_path]|;
flock($IN, 1);
while(<$IN>){
	chomp;
	my($id,$lang) = split(/\t/);
	if($id =~ /^(FMA):([0-9]+)$/){
		$id = qq|$1$2|;
	}else{
		undef $id;
	}
	undef $lang unless(defined $lang && length $lang);
	next unless(defined $id && defined $lang);
	say qq|$id\t$lang| if(exists $FMA2LANG{$id});
	$FMA2LANG{$id} = $lang;
}
close($IN);

#exit;

my $table = qq|concept_data_info|;

$dbh->do(qq|ALTER TABLE $table DISABLE TRIGGER trig_after_concept_data_info;|) or die $!;
$dbh->do(qq|ALTER TABLE $table DISABLE TRIGGER trig_before_concept_data_info;|) or die $!;

$dbh->{AutoCommit} = 0;
$dbh->{RaiseError} = 1;
eval{
	my $sql = qq|update $table set cdi_taid=NULL where ci_id=? and cdi_taid is not null|;
	say STDERR $sql;
#	$dbh->do($sql) or die $!;
	my $sth = $dbh->prepare($sql) or die $!;
	$sth->execute($ci_id) or die $dbh->errstr;
	say STDERR $sth->rows();
	$sth->finish;

	my $sql_upd = qq|update $table set cdi_taid=? where ci_id=? and cdi_name=?|;
	my $sth_upd = $dbh->prepare($sql_upd) or die $!;

	my $sql_upd_lang = qq|update $table set cdi_name_l=? where ci_id=? and cdi_name=?|;
	my $sth_upd_lang = $dbh->prepare($sql_upd_lang) or die $!;

	foreach my $id (keys(%FMA2TA)){
		print STDERR sprintf(qq|%-10s : %-64s\r|, $id, $FMA2TA{$id});
		$sth_upd->execute($FMA2TA{$id},$ci_id,$id) or die $dbh->errstr;
		$sth_upd->finish;
	}
	say STDERR '';

	foreach my $id (keys(%FMA2LANG)){
		print STDERR sprintf(qq|%-10s : %-64s\r|, $id, $FMA2LANG{$id});
		$sth_upd_lang->execute($FMA2LANG{$id},$ci_id,$id) or die $dbh->errstr;
		$sth_upd_lang->finish;
	}
	say STDERR '';


	$dbh->commit;
};
if($@){
	print $@,"\n";
	$dbh->rollback;
	$dbh->{AutoCommit} = 1;
	$dbh->{RaiseError} = 0;
}

$dbh->do(qq|ALTER TABLE $table ENABLE TRIGGER trig_after_concept_data_info;|) or die;
$dbh->do(qq|ALTER TABLE $table ENABLE TRIGGER trig_before_concept_data_info;|) or die;
