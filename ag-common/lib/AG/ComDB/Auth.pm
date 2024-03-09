package AG::ComDB::Auth;

use base qw/AG::ComDB/;

use strict;
use Digest::MD5 qw(md5_hex);
use JSON::XS;
use Carp;

#sub new {
#	my $class = shift;
#	my %args = @_;
#	my $self = new AG::ComDB(%args);
#	return bless $self, $class;
#}

sub openidLoginSession {
	my $self = shift;
	my $openid_info = shift;
	my $openid_session = shift;
	my $dbh = $self->get_dbh();
	$dbh->{AutoCommit} = 0;
	$dbh->{RaiseError} = 1;
	eval{
		my $json = &JSON::XS::encode_json($openid_info);

		my $sth_ins_openid_session = $dbh->prepare(qq|insert into openid_session (os_openid,os_id,os_info,os_entry) values (?,?,?,'now()')|) or &Carp::croak(DBI->errstr());
		$sth_ins_openid_session->execute($openid_info->{url},$openid_session,$json) or &Carp::croak(DBI->errstr());
		$sth_ins_openid_session->finish;
		undef $sth_ins_openid_session;

		my $sth_sel_openid_auth = $dbh->prepare(qq|select oa_auth from openid_auth where oa_openid=?|) or &Carp::croak(DBI->errstr());
		$sth_sel_openid_auth->execute($openid_info->{url}) or &Carp::croak(DBI->errstr());
		my $rows = $sth_sel_openid_auth->rows;
		$sth_sel_openid_auth->finish;
		undef $sth_sel_openid_auth;
		if($rows>0){
			my $sth_upd_openid_auth = $dbh->prepare(qq|update openid_auth set oa_info=?,oa_modified='now()' where oa_openid=?|) or &Carp::croak(DBI->errstr());
			$sth_upd_openid_auth->execute($json,$openid_info->{url}) or &Carp::croak(DBI->errstr());
			$sth_upd_openid_auth->finish;
			undef $sth_upd_openid_auth;
		}else{
			my $sth_ins_openid_auth = $dbh->prepare(qq|insert into openid_auth (oa_openid,oa_info,oa_entry,oa_modified) values (?,?,'now()','now()')|) or &Carp::croak(DBI->errstr());
			$sth_ins_openid_auth->execute($openid_info->{url},$json) or &Carp::croak(DBI->errstr());
			$sth_ins_openid_auth->finish;
			undef $sth_ins_openid_auth;
		}
		$dbh->commit();
	};
	if($@){
		warn __LINE__,":",$@,"\n";
		$dbh->rollback;
	}
	$dbh->{AutoCommit} = 1;
	$dbh->{RaiseError} = 0;
}

sub openidAuthSession {
	my $self = shift;
	my $openid_url = shift;
	my $openid_session = shift;
	my($lsdb_OpenID,$lsdb_Auth,$lsdb_Config,$lsdb_Identity);

	my $dbh = $self->get_dbh();
	my $sth_sel_openid_session = $dbh->prepare(qq|select os_info from openid_session where os_openid=? and os_id=?|) or &Carp::croak(DBI->errstr());
	$sth_sel_openid_session->execute($openid_url,$openid_session) or &Carp::croak(DBI->errstr());
	if($sth_sel_openid_session->rows>0){
		my $os_info;
		my $column_number = 0;
		$sth_sel_openid_session->bind_col(++$column_number, \$os_info, undef);
		$sth_sel_openid_session->fetch;

		$lsdb_OpenID = $openid_url;
		$lsdb_Identity = &JSON::XS::decode_json($os_info) if(defined $os_info);
		my $sth_sel_openid_auth = $dbh->prepare(qq|select oa_auth from openid_auth where oa_openid=?|) or &Carp::croak(DBI->errstr());
		$sth_sel_openid_auth->execute($openid_url) or &Carp::croak(DBI->errstr());
		$column_number = 0;
		$sth_sel_openid_auth->bind_col(++$column_number, \$lsdb_Auth, undef);
		$sth_sel_openid_auth->fetch;
		$sth_sel_openid_auth->finish;
		undef $sth_sel_openid_auth;
	}
	$sth_sel_openid_session->finish;
	undef $sth_sel_openid_session;
	return ($lsdb_OpenID,$lsdb_Auth,$lsdb_Config,$lsdb_Identity);
}

my $sth_del_openid_session;
sub openidLogoutSession {
	my $self = shift;
	my $openid_url = shift;
	my $openid_session = shift;
	my $dbh = $self->get_dbh();
	$dbh->{AutoCommit} = 0;
	$dbh->{RaiseError} = 1;
	eval{
		my $sth_del_openid_session = $dbh->prepare(qq|delete from openid_session where os_openid=? and os_id=?|) or &Carp::croak(DBI->errstr());
		$sth_del_openid_session->execute($openid_url,$openid_session) or &Carp::croak(DBI->errstr());
		$sth_del_openid_session->finish;
		undef $sth_del_openid_session;
		$dbh->commit();
	};
	if($@){
		$dbh->rollback;
	}
	$dbh->{AutoCommit} = 1;
	$dbh->{RaiseError} = 0;
}

1;
