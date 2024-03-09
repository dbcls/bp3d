#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use DBD::Pg;
use POSIX;
use Data::Dumper;
use Cwd qw(abs_path);
use File::Basename;
use File::Spec::Functions;

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

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
use BITS::VTK;

require "webgl_common.pl";

=pod
my($x,$y,$z) = (0.6,-0.2,-0.3);
print qq|[$x:$y:$z]=[|,sprintf(qq|[%d:%d:%d]|,int($x),int($y),int($z)),"\n";
print qq|[$x:$y:$z]=[|,sprintf(qq|[%d:%d:%d]|,ceil($x),ceil($y),ceil($z)),"\n";
print qq|[$x:$y:$z]=[|,sprintf(qq|[%d:%d:%d]|,floor($x),floor($y),floor($z)),"\n";
exit;
=cut

my $dbh = &get_dbh();

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

my @TABLES = qw/art_file concept_art_map history_art_file history_concept_art_map representation_art voxel_data/;

if(defined $trigger_hash && ref $trigger_hash eq 'HASH'){
#	foreach $table_name (keys(%{$trigger_hash})){
	foreach $table_name (@TABLES){
		next unless(exists $trigger_hash->{$table_name} && defined $trigger_hash->{$table_name} && ref $trigger_hash->{$table_name} eq 'HASH');
		foreach $trigger_name (keys(%{$trigger_hash->{$table_name}})){
			$sql = qq|ALTER TABLE $table_name DISABLE TRIGGER $trigger_name;|;
			say $sql;
			$dbh->do($sql) or die $!;
		}
	}
}
#$dbh->{'AutoCommit'} = 0;
#$dbh->{'RaiseError'} = 1;
eval{

	my $art_ids;
	my $art_id;
	my $art_hist_serial;
	my $sth;
	my $total;
	my $count;
	my $rows;
=pod
	$sql=qq|
select art_id,min(art_hist_serial) AS min_art_hist_serial from voxel_data group by art_id
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
=cut

	my @UPDATE_TABLES = qw/representation_art history_concept_art_map concept_art_map/;
	foreach my $update_table (@UPDATE_TABLES){
		$sql=qq|UPDATE $update_table SET art_hist_serial=0 WHERE art_hist_serial<>0|;
		say $sql;
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$rows = $sth->rows();
		$sth->finish;
		undef $sth;
		say sprintf("[%6d]",$rows);
	}

	$sql=qq|DELETE FROM voxel_data WHERE art_hist_serial<>0|;
	say $sql;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$rows = $sth->rows();
	$sth->finish;
	undef $sth;
	say sprintf("[%6d]",$rows);

	my $max_hist_serial;
	my $min_hist_serial = 0;
	$sql=qq|
select max(hist_serial) from history_art_file
|;
	my $sth_art_sel = $dbh->prepare($sql) or die $dbh->errstr;
	$column_number = 0;
	$sth_art_sel->execute() or die $dbh->errstr;
	$sth_art_sel->bind_col(++$column_number, \$max_hist_serial, undef);
	$sth_art_sel->fetch;
	$sth_art_sel->finish;
	undef $sth_art_sel;

	if(defined $max_hist_serial && $max_hist_serial > $min_hist_serial){
		while($max_hist_serial > $min_hist_serial){
			$sql=qq|DELETE FROM history_art_file WHERE hist_serial=$max_hist_serial|;
			say $sql;
			$sth = $dbh->prepare($sql) or die $dbh->errstr;
			$sth->execute() or die $dbh->errstr;
			$rows = $sth->rows();
			$sth->finish;
			undef $sth;
			say sprintf("[%6d]",$rows);
			$max_hist_serial--;
		}
	}
	else{
		$sql=qq|DELETE FROM history_art_file WHERE hist_serial<>0|;
		say $sql;
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$rows = $sth->rows();
		$sth->finish;
		undef $sth;
		say sprintf("[%6d]",$rows);
	}

#	$dbh->commit();
};
if($@){
	print __LINE__,":",$@,"\n";
#	$dbh->rollback;
}
#$dbh->{'AutoCommit'} = 1;
#$dbh->{'RaiseError'} = 0;


if(defined $trigger_hash && ref $trigger_hash eq 'HASH'){
#	foreach $table_name (keys(%{$trigger_hash})){
	foreach $table_name (@TABLES){
		next unless(exists $trigger_hash->{$table_name} && defined $trigger_hash->{$table_name} && ref $trigger_hash->{$table_name} eq 'HASH');
		foreach $trigger_name (keys(%{$trigger_hash->{$table_name}})){
			$sql = qq|ALTER TABLE $table_name ENABLE TRIGGER $trigger_name;|;
			say $sql;
			$dbh->do($sql) or die $!;
		}
	}
}

