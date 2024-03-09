#!/bp3d/local/perl/bin/perl

$| = 1;
select(STDERR);
$| = 1;
select(STDOUT);

use strict;

use constant {
	APACHECTL => '/bp3d/local/apache/bin/apachectl',

	PSQL => '/bp3d/local/pgsql/bin/psql',
	PG_DUMP => '/bp3d/local/pgsql/bin/pg_dump',
	DROPDB => '/bp3d/local/pgsql/bin/dropdb',
	CREATEDB => '/bp3d/local/pgsql/bin/createdb',
	SENNA_SQL => '/bp3d/local/pgsql/share/pgsenna2.sql',
	DBLINK_SQL => '/bp3d/local/pgsql/share/contrib/dblink.sql',

	GZIP => '/usr/bin/gzip',
	ZCAT => '/bin/zcat',
	WC   => '/usr/bin/wc',

	USE_GZIP => 0,

	SERVICE_HOME => '/bp3d/ag-in-service',
	SERVICE_CONF => '/bp3d/ag-in-service/apache_conf/setenv.conf',
	SERVICE_DB_NAME => 'bp3d',
	SERVICE_DB_HOST => '127.0.0.1',
	SERVICE_DB_PORT => '8543',
	SERVICE_DB_USER => 'postgres',
	SERVICE_DB_PWD => '',

	TEST_HOME => '/bp3d/ag-test',
	TEST_DB_NAME => 'bp3d',
	TEST_DB_HOST => '127.0.0.1',
	TEST_DB_PORT => '8543',
	TEST_DB_USER => 'postgres',
	TEST_DB_PWD => '',
};

#die qq|$0 database_name ag-test-port-number ag-in-service-port-number\n| unless scalar @ARGV == 3;

use File::Basename;
use File::Spec;
use File::Path;
#use File::Copy;
#use List::Util;
#use Image::Info;
#use Cwd;

use FindBin;
my $htdocs_path;
BEGIN{
	use FindBin;
	$htdocs_path = qq|$FindBin::Bin/../htdocs_131012|;
	$htdocs_path = qq|$FindBin::Bin/../htdocs| unless(-e $htdocs_path);
#	print __LINE__,":BEGIN2!!\n";
}
use lib $FindBin::Bin,$htdocs_path;

require "webgl_common.pl";

use make_httpd_conf;

my $dbh = &get_dbh();

#my $md_id=1;
#my $prev_mv_id=3;
#my $next_mv_id=4;

#my $database_name = shift @ARGV;
#my $ag_test_port_number = shift @ARGV;
#my $ag_in_service_port_number = shift @ARGV;


eval{
	&make_httpd_conf::make_renderer_conf($dbh);

	&set_service_dbport(TEST_DB_PORT);
	&restart_apache();
	my $dump_file = &dump_testdb();
	die "Dump Failure!!\n" unless(defined $dump_file && -e $dump_file && -s $dump_file);

	&dropdb_servicedb();
	&createdb_servicedb();
	&loadsql_servicedb(SENNA_SQL);
	&loadsql_servicedb(DBLINK_SQL);
	&restore_servicedb($dump_file);

	&set_service_dbport(SERVICE_DB_PORT);
	&restart_apache();

	&system_command(sprintf("%s %s",GZIP,$dump_file));
};
if($@){
	die __LINE__,":$@\n";
}

exit;

sub set_service_dbport {
	my $db_port = shift;
	die "" unless(defined $db_port);

	my $dir = &File::Basename::dirname(SERVICE_CONF);
	unless(-e $dir){
		my $old = umask(0);
		&File::Path::mkpath($dir,0,0777);
		umask($old);
	}
	my $OUT;
	open($OUT,"> ".SERVICE_CONF) or die $!;
	flock($OUT,2);
	print $OUT qq|SetEnv AG_DB_PORT $db_port\n|;
	close($OUT);
}

sub system_command {
	my $cmd = shift;
	die "Unknown command\n" unless(defined $cmd);
	printf("%03d:\$cmd=[%s]\n", __LINE__,$cmd);
	if(system($cmd)){
		if($? == -1){
			die "failed to execute: $!\n";
		}elsif($? & 127){
			die sprintf("child died with signal %d, %s coredump\n",($? & 127),($? & 128) ? 'with' : 'without');
		}else{
			die sprintf("child exited with value %d\n", $? >> 8);
		}
	}
	printf("%d:status code %d.\n",__LINE__,$?);

	return $?;
}

sub restart_apache {
	return &system_command(APACHECTL.qq| -k restart|);
}

sub dump_testdb {
	chdir(TEST_HOME) or die $!;

	my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
	my $dump_date = sprintf("%04d%02d%02d",$year+1900,$mon+1,$mday);
	my $dump_gz1file = sprintf("%s.dump.%s.gz",File::Spec->catfile(TEST_HOME,TEST_DB_NAME),$dump_date);
	my $dump_gz2file = sprintf("%s.%s.dump.gz",File::Spec->catfile(TEST_HOME,TEST_DB_NAME),$dump_date);
	my $dump_file = sprintf("%s.%s.dump",File::Spec->catfile(TEST_HOME,TEST_DB_NAME),$dump_date);
	unlink $dump_gz1file if(-e $dump_gz1file);
	unlink $dump_gz2file if(-e $dump_gz2file);
	unlink $dump_file if(-e $dump_file);

#	my $cmd_dump = sprintf(qq/%s --host=%s --port=%s --username=%s --schema-only %s/,PG_DUMP,TEST_DB_HOST,TEST_DB_PORT,TEST_DB_USER,TEST_DB_NAME);
	my $cmd_dump = sprintf(qq/%s --host=%s --port=%s --username=%s %s/,PG_DUMP,TEST_DB_HOST,TEST_DB_PORT,TEST_DB_USER,TEST_DB_NAME);
	my $cmd;
	if(USE_GZIP){
		$cmd = sprintf(qq/%s | %s > %s/,$cmd_dump,GZIP,$dump_file);
	}else{
		$cmd = sprintf(qq/%s > %s/,$cmd_dump,$dump_file);
	}
	&system_command($cmd);

	my $wc = 0;
	if(-e $dump_file && -s $dump_file){
		my $c;
		if(USE_GZIP){
			$c = sprintf(qq/%s %s | %s -l/,ZCAT,$dump_file,WC);
		}else{
			$c = sprintf(qq/%s -l %s/,WC,$dump_file);
		}
		$wc = qx/$c/;
		$wc =~ s/\s*$//g;
	}
	if($wc>0){
		return $dump_file;
	}else{
		unlink $dump_file if(-e $dump_file);
		return undef;
	}
}

sub dropdb_servicedb {
	chdir(SERVICE_HOME) or die $!;
	my $cmd = sprintf(qq/%s -h %s -p %s -U %s %s/,DROPDB,SERVICE_DB_HOST,SERVICE_DB_PORT,SERVICE_DB_USER,SERVICE_DB_NAME);
	return &system_command($cmd);
}
sub createdb_servicedb {
	chdir(SERVICE_HOME) or die $!;
	my $cmd = sprintf(qq/%s -h %s -p %s -U %s %s/,CREATEDB,SERVICE_DB_HOST,SERVICE_DB_PORT,SERVICE_DB_USER,SERVICE_DB_NAME);
	return &system_command($cmd);
}
sub loadsql_servicedb {
	my $sql_file = shift;
	die "Unknown SQL file\n" unless(defined $sql_file && -e $sql_file && -s $sql_file);
	chdir(SERVICE_HOME) or die $!;
	my $cmd = sprintf(qq/%s -h %s -p %s -U %s %s -f %s/,PSQL,SERVICE_DB_HOST,SERVICE_DB_PORT,SERVICE_DB_USER,SERVICE_DB_NAME,$sql_file);
	return &system_command($cmd);
}
sub restore_servicedb {
	my $dump_file = shift;
	die "Unknown Dump file\n" unless(defined $dump_file && -e $dump_file && -s $dump_file);
	chdir(SERVICE_HOME) or die $!;
	if(USE_GZIP){
		my $cmd = sprintf(qq/%s %s | %s -h %s -p %s -U %s %s/,ZCAT,$dump_file,PSQL,SERVICE_DB_HOST,SERVICE_DB_PORT,SERVICE_DB_USER,SERVICE_DB_NAME);
		return &system_command($cmd);
	}else{
		return &loadsql_servicedb($dump_file);
	}
}
