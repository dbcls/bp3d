package AG::DB;

use strict;
use DBI;
use Carp;

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
use constant DB_LINK => 'dbname='.($ENV{AG_DB_NAME} || DB_NAME).' host='.($ENV{AG_DB_HOST} || DB_HOST).' port='.($ENV{AG_DB_PORT} || DB_PORT).' user='.DB_USER.' password='.DB_PASSWD;

#use Digest::MD5 qw(md5_hex);
#use JSON::XS;
#use Carp;

#require "common.pl";
#require "CommonDB.pl";

sub new {
	# 暗黙のうちに引き渡されるクラス名を受け取る
	my $class = shift;
	my %args = (
		'connect' => DB_CONNECT,
		'dbh'     => undef,
		'dbname'  => $ENV{AG_DB_NAME} || DB_NAME,
		'host'    => $ENV{AG_DB_HOST} || DB_HOST,
		'port'    => $ENV{AG_DB_PORT} || DB_PORT,
		'user'    => DB_USER,
		'passwd'  => DB_PASSWD,
		@_
	);

	my $data_source = qq|dbname=$args{'dbname'};host=$args{'host'};port=$args{'port'}|;
	my $dbh = $args{'dbh'};
	if($args{'connect'} && !defined $dbh){
		$args{'connect'} = 0;
		if(defined $ENV{MOD_PERL}){
			my $r = Apache::DBI->connect_on_init(DBSOURCE_PREFIX.$data_source,$args{'user'},$args{'passwd'}) or &Carp::croak(DBI->errstr());
			warn __PACKAGE__.":".__LINE__.":\$r=[$r]\n";
			if($r){
				$dbh = DBI->connect(DBSOURCE_PREFIX.$data_source,$args{'user'},$args{'passwd'}) or &Carp::croak(DBI->errstr());
				warn __PACKAGE__.":".__LINE__.":\$dbh=[$dbh]\n";
			}
		}else{
			$dbh = DBI->connect(DBSOURCE_PREFIX.$data_source,$args{'user'},$args{'passwd'}) or &Carp::croak(DBI->errstr());
#			warn __PACKAGE__.":".__LINE__.":\$dbh=[$dbh]\n";
		}
		$dbh->{'pg_enable_utf8'} = ENABLE_UTF8 if(defined $dbh);
		$args{'connect'} = 1;
	}else{
		$args{'connect'} = 0;
	}

	# 無名ハッシュのリファレンスを作成
	my $self = {
		_connect => $args{'connect'},
		_user => $args{'user'},
		_passwd => $args{'passwd'},
		_data_source => $data_source,
		_dblink => qq|dbname=$args{'dbname'} host=$args{'host'} port=$args{'port'} user=$args{'user'} password=$args{'passwd'}|,
		_dbh => $dbh,
		_sth => {}
	};
	# bless したオブジェクトリファレンスを返す
	return bless $self, $class;
}

sub DESTROY {
	my $self = shift;
	$self->disconnectDB();
}

sub connectDB {
	my $self = shift;
	$self->disconnectDB();

	my $dbh = DBI->connect(DBSOURCE_PREFIX.$self->get_data_source(),$self->get_user(),$self->get_passwd()) or &Carp::croak(DBI->errstr());
	return undef unless(defined $dbh);
	$dbh->{'pg_enable_utf8'} = ENABLE_UTF8;
	$self->{'_dbh'} = $dbh;
	return $dbh;
}

sub disconnectDB {
	my $self = shift;
	if($self->{'_connect'}){
		foreach my $key (keys(%{$self->{_sth}})){
			delete $self->{_sth}->{$key} if(defined $self->{_sth}->{$key});
		}
		if(defined $self->{'_dbh'}){
			$self->{'_dbh'}->disconnect();
			delete $self->{'_dbh'};
		}
	}
}

sub get_dbh {
	my $self = shift;
	return $self->{'_dbh'};
}

sub get_dblink {
	my $self = shift;
	return $self->{'_dblink'};
}
#=pod
sub get_data_source {
	my $self = shift;
	return $self->{'_data_source'};
}

sub get_user {
	my $self = shift;
	return $self->{'_user'};
}

sub get_passwd {
	my $self = shift;
	return $self->{'_passwd'};
}
#=cut

sub get_ludia_operator {
	my $self = shift;
	return LUDIA_OPERATOR;
}

sub ExecuteSQL {
	my $self = shift;
	my $sql = shift;
	my @DATA = ();
	my $dbh = $self->get_dbh();
	my $sth = $dbh->prepare($sql);
	$sth->execute();
	while(my @row = $sth->fetchrow_array()){
		push(@DATA,join("\t",@row));
		undef @row;
	}
	$sth->finish();
	undef $sth;
	return(@DATA);
}

sub existsTable {
	my $self = shift;
	my $tablename = shift;
	return 0 unless(defined $tablename);
	my $dbh = $self->get_dbh();
	my $sth = $dbh->prepare(qq|select tablename from pg_tables where tablename=?|);
	$sth->execute($tablename);
	my $rows = $sth->rows();
	undef $sth;
	return $rows;
}

sub getIndexnamesFromTablename {
	my $self = shift;
	my $tablename = shift;
	return undef unless(defined $tablename);
	my @RTN = ();
	my $dbh = $self->get_dbh();
	my $sth = $dbh->prepare(qq|select indexname from pg_indexes where tablename=?|);
	$sth->execute($tablename);
	my $rows = $sth->rows();
	my $indexname;
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$indexname, undef);
	while($sth->fetch){
		push(@RTN,$indexname) if(defined $indexname);
	}
	$sth->finish;
	undef $sth;
	return wantarray ? @RTN : \@RTN;
}

sub getDbTableColumns {
	my $tablename = shift;
	return undef unless(defined $tablename);
	my @RTN = ();
	my $dbh = &get_dbh();
#	my $sth = $dbh->prepare(qq|select * from information_schema.columns where table_name=?|);
	my $sth = $dbh->prepare(qq|select column_name,data_type,ordinal_position from information_schema.columns where table_name=?|);
	$sth->execute($tablename);
	while(my $href = $sth->fetchrow_hashref){
		push(@RTN,$href);
	}
	$sth->finish;
	undef $sth;
	return scalar @RTN > 0 ? (wantarray ? @RTN : \@RTN) : undef;
}

sub getTree_Path2Root {
	my $self = shift;
	my $form = shift;
	my $f_id = shift;
	my $TREE_ROUTE = shift;
	my $route = shift;

	my $dbh = $self->get_dbh();
	$self->{_sth}->{_sth_tree_path2root} = $dbh->prepare(qq|select f_pid,t_delcause from tree where f_id=? and t_type=? and tg_id=? and tgi_id=?|) unless(defined $self->{_sth}->{_sth_tree_path2root});

	my $exists_flag;
	my $t_delcause_flag;

	unless(defined $route){
		$route = $f_id;
	}else{
		my @TEMP_ROUTE = split(/\t/,$route);
		foreach my $temp_fid (@TEMP_ROUTE){
			next if(!($temp_fid eq $f_id));
			$exists_flag = 1;
			last;
		}
		$route .= qq|\t$f_id|;
	}

	my @F_PID = ();
	unless(defined $exists_flag){
		$self->{_sth}->{_sth_tree_path2root}->execute($f_id,$form->{t_type},$form->{tg_id},$form->{tgi_id});
		if($self->{_sth}->{_sth_tree_path2root}->rows>0){
			my $f_pid;
			my $t_delcause;
			my $column_number = 0;
			$self->{_sth}->{_sth_tree_path2root}->bind_col(++$column_number, \$f_pid, undef);
			$self->{_sth}->{_sth_tree_path2root}->bind_col(++$column_number, \$t_delcause, undef);
			while($self->{_sth}->{_sth_tree_path2root}->fetch){
				if(defined $t_delcause){
					$t_delcause_flag = 1;
				}else{
					push(@F_PID,$f_pid);
				}
			}
		}
		$self->{_sth}->{_sth_tree_path2root}->finish;
	}
	if(scalar @F_PID > 0){
		foreach my $f_pid (@F_PID){
			&getTree_Path2Root($form,$f_pid,$TREE_ROUTE,$route);
			last if(scalar @$TREE_ROUTE > 100);
		}
	}elsif(!defined $exists_flag && !defined $t_delcause_flag){
		push(@$TREE_ROUTE,$route);
	}
}

sub get_phy_id {
	my $self = shift;
	my $f_id = shift;
	my $phy_id;
	my $dbh = $self->get_dbh();
	$f_id =~ s/\D+$//g if($f_id =~ /^FMA\d+/);
	$self->{_sth}->{_sth_fma_phy} = $dbh->prepare(qq|select phy_id from fma where f_id=?|) unless(defined $self->{_sth}->{_sth_fma_phy});
	$self->{_sth}->{_sth_fma_phy}->execute($f_id);
	my $column_number = 0;
	$self->{_sth}->{_sth_fma_phy}->bind_col(++$column_number, \$phy_id, undef);
	$self->{_sth}->{_sth_fma_phy}->fetch;
	$self->{_sth}->{_sth_fma_phy}->finish;
	return $phy_id;
}

1;
