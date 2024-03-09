package AG::ComDB;

use base qw/AG::DB/;

use strict;
#use DBI;

use constant {
	DB_USER       => qq|postgres|,
	DB_PASSWD     => qq||,
	DB_NAME       => qq|bp3d_common|,
	DB_HOST       => qq|127.0.0.1|,
	DB_PORT       => qq|8543|
};

sub new {
	my $class = shift;
	my %args = (
		'dbh'     => undef,
		'dbname'  => $ENV{AG_COMDB_NAME} || DB_NAME,
		'host'    => $ENV{AG_COMDB_HOST} || DB_HOST,
		'port'    => $ENV{AG_COMDB_PORT} || DB_PORT,
		'user'    => DB_USER,
		'passwd'  => DB_PASSWD,
		@_
	);
	my $self = new AG::DB(%args);
	return bless $self, $class;
}


1;
