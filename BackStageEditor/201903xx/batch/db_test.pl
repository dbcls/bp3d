#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use Sys::CPU;
use Parallel::Fork::BossWorkerAsync;
use POSIX qw(floor ceil);
use DBI;
use DBD::Pg;

use Getopt::Long qw(:config posix_default no_ignore_case gnu_compat);
my $config = {
	db   => exists $ENV{'AG_DB_NAME'} && defined $ENV{'AG_DB_NAME'} ? $ENV{'AG_DB_NAME'} : 'bp3d',
	host => exists $ENV{'AG_DB_HOST'} && defined $ENV{'AG_DB_HOST'} ? $ENV{'AG_DB_HOST'} : '127.0.0.1',
	port => exists $ENV{'AG_DB_PORT'} && defined $ENV{'AG_DB_PORT'} ? $ENV{'AG_DB_PORT'} : '8543'
};
&Getopt::Long::GetOptions($config,qw/
	db|d=s
	host|h=s
	port|p=s
/) or exit 1;

$ENV{'AG_DB_HOST'} = $config->{'host'};
$ENV{'AG_DB_PORT'} = $config->{'port'};
$ENV{'AG_DB_NAME'} = $config->{'db'};

use constant {
	DB_CONNECT    => 1,
	DB_USER       => qq|postgres|,
	DB_PASSWD     => qq||,
	DB_NAME       => qq|bp3d|,
	DB_HOST       => qq|127.0.0.1|,
	DB_PORT       => qq|8543|,

#	LUDIA_OPERATOR=> '@@',
	LUDIA_OPERATOR=> '%%', #Ludiaが1.5.0以上で、PostgreSQLが8.3以上の場合、こちらを使用すること

	DBSOURCE_PREFIX => qq|dbi:Pg:|,
	ENABLE_UTF8   => 1
};

my $dbh;
sub init_sub {
	my %args = (
		'connect' => DB_CONNECT,
		'dbh'     => undef,
		'dbname'  => $ENV{'AG_DB_NAME'} || DB_NAME,
		'host'    => $ENV{'AG_DB_HOST'} || DB_HOST,
		'port'    => $ENV{'AG_DB_PORT'} || DB_PORT,
		'user'    => DB_USER,
		'passwd'  => DB_PASSWD
	);
	my $data_source = qq|dbname=$args{'dbname'};host=$args{'host'};port=$args{'port'}|;
	$dbh = DBI->connect(DBSOURCE_PREFIX.$data_source,$args{'user'},$args{'passwd'}) or die $!;
	$dbh->{'pg_enable_utf8'} = ENABLE_UTF8;
}

sub exit_sub {
	$dbh->disconnect();
	undef $dbh;
}

sub work_sub {
	my ($job)=@_;
}

sub result_sub {
	my ($result)=@_;
}

sub main {
	&init_sub();
	my $sql=<<SQL;
SELECT
     a.event_object_table  AS table_name
    ,a.trigger_name AS trigger_name
--    ,a.action_statement AS action_statement
--    ,REPLACE(a.action_statement, 'EXECUTE FUNCTION ','') AS func_name
    ,b.tgenabled AS trigger_enable
--    ,COALESCE( a.action_condition, '' ) AS action_condition
FROM
    information_schema.triggers AS a
    LEFT OUTER JOIN pg_trigger AS b ON
        a.trigger_name=b.tgname
WHERE
    a.trigger_schema = current_schema()
    AND b.tgenabled='O'
GROUP BY
     a.event_object_table
    ,a.trigger_name
    ,a.action_statement
    ,b.tgenabled
    ,a.action_condition
ORDER BY
    a.trigger_name
;
SQL

	my $sth_trigger_sel = $dbh->prepare($sql) or die $dbh->errstr;
	my $table_name;
	my $trigger_name;
	my $column_number = 0;
	my $trigger_hash;
	$sth_trigger_sel->execute() or die $dbh->errstr;
	$sth_trigger_sel->bind_col(++$column_number, \$table_name, undef);
	$sth_trigger_sel->bind_col(++$column_number, \$trigger_name, undef);
	while($sth_trigger_sel->fetch){
		$trigger_hash->{$table_name}->{$trigger_name} = undef;
	}
	$sth_trigger_sel->finish;
	undef $sth_trigger_sel;

	my @TABLES = qw/art_file concept_art_map history_art_file history_concept_art_map representation_art voxel_data/;

	if(defined $trigger_hash && ref $trigger_hash eq 'HASH'){
		foreach $table_name (@TABLES){
			next unless(exists $trigger_hash->{$table_name} && defined $trigger_hash->{$table_name} && ref $trigger_hash->{$table_name} eq 'HASH');
			foreach $trigger_name (keys(%{$trigger_hash->{$table_name}})){
				$sql = qq|ALTER TABLE $table_name DISABLE TRIGGER $trigger_name;|;
				say $sql;
				$dbh->do($sql) or die $!;
			}
		}
	}

	my $art_ids;
	my $art_id;
	my $art_hist_serial;
	my $sth;
	my $total;
	my $count;
	my $rows;
	$sql=qq|
select art_id,min(hist_serial) AS min_hist_serial from history_art_file group by art_id
|;
	my $sth_art_sel = $dbh->prepare($sql) or die $dbh->errstr;
	$column_number = 0;
	$sth_art_sel->execute() or die $dbh->errstr;
	$sth_art_sel->bind_col(++$column_number, \$art_id, undef);
	$sth_art_sel->bind_col(++$column_number, \$art_hist_serial, undef);
	while($sth_art_sel->fetch){
		$art_ids->{$art_id} = $art_hist_serial;
	}
	$sth_art_sel->finish;
	undef $sth_art_sel;
	$total = scalar keys(%{$art_ids});

	&exit_sub();


	my $number_of_cpus = &Sys::CPU::cpu_count();
	say $number_of_cpus;

	$count = &ceil($total / $number_of_cpus);










	my $bw = Parallel::Fork::BossWorkerAsync->new(
		work_handler    => \&work_sub,
		result_handler  => \&result_sub,
		init_handler    => \&init_sub,
		exit_handler    => \&exit_sub,
		global_timeout  => 0,
		worker_count    => $number_of_cpus,
		msg_delimiter   => "\0\0\0",
		read_size       => 1024 * 1024,
	);


	# Jobs are hashrefs
	$bw->add_work( {a => 3, b => 4} );
	while ($bw->pending()) {
		my $ref = $bw->get_result();
		if ($ref->{ERROR}) {
			print STDERR $ref->{ERROR};
		} else {
			print "$ref->{product}\n";
			print "$ref->{string}\n";
		}
	}
	$bw->shut_down();

	undef $bw;
}

&main();
