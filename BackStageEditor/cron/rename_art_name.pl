#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

#use JSON::XS;
use DBD::Pg;
#use POSIX;
#use Data::Dumper;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
require "webgl_common.pl";
use cgi_lib::common;
my $dbh = &get_dbh();

$dbh->{'AutoCommit'} = 0;
$dbh->{'RaiseError'} = 1;
eval{
	foreach my $table (qw|art_file art_file_info history_art_file history_art_file_info|){
		unless(&_existsTable($dbh,$table)){
			say STDERR qq|Unknown table [$table]|;
			next;
		}
		unless(&_existsTableColumn($dbh,$table,'art_name')){
			say STDERR qq|Unknown column [$table][art_name]|;
			next;
		}

		my $sth = $dbh->prepare(qq|select art_id,art_name from $table where art_name like '%/%' or art_name like '%.obj'|) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		if($sth->rows()>0){
			say STDERR sprintf(qq|%5d [$table]|,$sth->rows());

			my $trig_before = qq|trig_before_$table|;
			my $trig_after  = qq|trig_after_$table|;

			if(&_existsTrigger($dbh,$trig_before)){
				$dbh->do(qq|ALTER TABLE ONLY $table DISABLE TRIGGER $trig_before;|) or die $dbh->errstr;
			}
			if(&_existsTrigger($dbh,$trig_after)){
				$dbh->do(qq|ALTER TABLE ONLY $table DISABLE TRIGGER $trig_after;|) or die $dbh->errstr;
			}

			my $sth_upd = $dbh->prepare("update $table set art_name=? where art_id=?") or die $dbh->errstr;
			my $column_number = 0;
			my $art_id;
			my $art_name;
			$sth->bind_col(++$column_number, \$art_id, undef);
			$sth->bind_col(++$column_number, \$art_name, undef);
			while($sth->fetch){
				next unless(defined $art_id && defined $art_name);
				my($name,$dir,$ext) = &File::Basename::fileparse($art_name,qw|.obj|);
				$sth_upd->execute($name,$art_id) or die $dbh->errstr;
				$sth_upd->finish;
			}
			undef $sth_upd;

			if(&_existsTrigger($dbh,$trig_before)){
				$dbh->do(qq|ALTER TABLE ONLY $table ENABLE TRIGGER $trig_before;|) or die $dbh->errstr;
			}
			if(&_existsTrigger($dbh,$trig_after)){
				$dbh->do(qq|ALTER TABLE ONLY $table ENABLE TRIGGER $trig_after;|) or die $dbh->errstr;
			}
		}else{
			say STDERR qq|none [$table]|;
		}
		$sth->finish;
		undef $sth;
	}

	$dbh->commit;
};
if($@){
	say STDERR $@;
	$dbh->rollback;
}
$dbh->{'AutoCommit'} = 1;
$dbh->{'RaiseError'} = 0;

exit;

sub _existsTable {
	my $dbh = shift;
	my $table_name = shift;
	return 0 unless(defined $table_name);
	my $sth = $dbh->prepare(qq|select tablename from pg_tables where tablename=?|);
	$sth->execute($table_name);
	my $rows = $sth->rows();
	$sth->finish;
	undef $sth;
	say STDERR sprintf("%03d:[%s][%d]",__LINE__,$table_name,$rows);
	return $rows;
}

sub _existsTableColumn {
	my $dbh = shift;
	my $table_name = shift;
	my $column_name = shift;
	return 0 unless(defined $table_name && defined $column_name);
	my $sth = $dbh->prepare(qq|select column_name from information_schema.columns where table_name=? and column_name=?|);
	$sth->execute($table_name,$column_name);
	my $rows = $sth->rows();
	$sth->finish;
	undef $sth;
	say STDERR sprintf("%03d:[%s][%s][%d]",__LINE__,$table_name,$column_name,$rows);
	return $rows;
}

sub _existsTrigger {
	my $dbh = shift;
	my $tgname = shift;
	return 0 unless(defined $tgname);
	my $sth = $dbh->prepare(qq|select tgname from pg_trigger where tgname=?|);
	$sth->execute($tgname);
	my $rows = $sth->rows();
	$sth->finish;
	undef $sth;
	say STDERR sprintf("%03d:[%s][%d]",__LINE__,$tgname,$rows);
	return $rows;
}
=pod
select column_name from information_schema.columns where table_name='art_file' and column_name='art_name';

=cut
