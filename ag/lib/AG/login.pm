package AG::login;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use File::Spec::Functions qw(catdir catfile);

use FindBin;
use Cwd;
#use lib $FindBin::Bin,&catdir($FindBin::Bin,'API'),&Cwd::abs_path(&catdir($FindBin::Bin,'..','..','ag-common','lib'));
use AG::ComDB::Auth;
use AG::DB;
use cgi_lib::common;

my $ag_com_auth;
my $ag_db;
my $LOG;

#Crypt::SSLeayが無い場合、エラーになる

#下記の順にインストールすると良いらしい。(http://www.atmarkit.co.jp/fsecurity/rensai/openid03/openid01.html)
#1.Math::BigInt
#2.Math::BigInt::GMP
#3.Crypt::DH
#4.Net::OpenID::Consumer

sub openid_login {
	use CGI;
	my $cgi = CGI->new;
	$cgi->charset('utf-8');

	my @param = $cgi->param();
	my %PARAMS = (
		'__PACKAGE__' => __PACKAGE__,
		'__FILE__' => __FILE__
	);
	foreach my $key (@param){
		$PARAMS{$key} = $cgi->param($key);
	}
	undef @param;
	my @cookie = $cgi->cookie();
	my %COOKIE;
	foreach my $key (@cookie){
		$COOKIE{$key} = $cgi->cookie($key);
	}
	undef @cookie;
	$LOG = &cgi_lib::common::getLogFH(\%PARAMS,\%COOKIE);

	if($cgi->param('openid_url')) {
		use Net::OpenID::Consumer;
		use LWP::UserAgent;
		my $csr = Net::OpenID::Consumer->new(
			ua => LWP::UserAgent->new,
			args => $cgi,
			consumer_secret => sub { $_[0] },
		);

		my $claimed_url = $cgi->param('openid_url');
		my $session = $cgi->param('session');
		my $identity = $csr->claimed_identity($claimed_url);
		unless(defined $identity){
			my $user = {};
			$user->{error} = "true";
			&output($session,$user);
		}else{
			$identity->set_extension_args(
				"http://openid.net/extensions/sreg/1.1",
				{
					required => 'email',
					optional => 'fullname,nickname'
				}
			);

			require "common.pl";
			my @param = ();
			for my $p ($cgi->param){
				next if($p eq "openid_url");
				next if($p =~ "tp_ap");
				push(@param,qq|$p=|.&url_encode($cgi->param($p)));
			}

			my $return_to = &getGlobalPath();
			my $trust_root;
			if(defined $return_to){
				use File::Basename;
				my($name,$dir,$ext) = fileparse($ENV{SCRIPT_NAME});
#				$return_to .= $name;
				$trust_root = $return_to;
				$return_to .= '?verify=1'.(scalar @param > 0 ? '&'.join("&",@param):'');
			}else{
				$trust_root = $cgi->url;
				$return_to = URI->new($cgi->url.'?verify=1' . (scalar @param > 0 ? '&'.join("&",@param):''))->as_string;
			}
			my $check_url = $identity->check_url(
				return_to  => $return_to,
				trust_root => $trust_root
			);
			print $LOG __LINE__,":\$check_url=[$check_url]\n";
			print $cgi->redirect(-uri => $check_url);
			exit;
		}
	}elsif($cgi->param('verify')){
		print $LOG __LINE__,"\n";
		use Net::OpenID::Consumer;
		use LWP::UserAgent;
#		use Mozilla::CA;
		my $ua = LWP::UserAgent->new() or die;
#		my $ua = LWP::UserAgent->new(agent=>qq|Mozilla/5.0 (Windows NT 6.0; rv:25.0) Gecko/20100101 Firefox/25.0|) or die;
#		$ua->ssl_opts( verify_hostnames => 0 );
#		$ua->ssl_opts (SSL_ca_file => Mozilla::CA::SSL_ca_file());
		my $csr = Net::OpenID::Consumer->new(
			ua => $ua,
			args => $cgi,
			consumer_secret => sub { $_[0] },
			debug => 1
		);

		my $setup_url = $csr->user_setup_url();
		my $identity = $csr->verified_identity();
		if(defined $setup_url){
			print $LOG __LINE__,":$setup_url\n";
			print $cgi->redirect(-uri => $setup_url);
		}else{
			my $user;
			if($csr->user_cancel){
				print $LOG __LINE__,"\n";
				$user = &get_identity($identity);
				$user->{user_cancel} = "true";
				&output($cgi->param('session'),$user);

			}elsif(defined $identity){
				print $LOG __LINE__,"\n";
				$user = &get_identity($identity);
				&output($cgi->param('session'),$user);
			}else{
				print $LOG __LINE__,"\n";
				$user = &get_identity($identity);
				$user->{errcode} = $csr->errcode;
				$user->{errtext} = $csr->errtext;
				&output($cgi->param('session'),$user);
			}
			print $LOG __LINE__,"\n";

			require "common.pl";
			my @param = ();
			for my $p ($cgi->param){
				next if($p eq "verify");
				next if($p eq "session");
				next if($p =~ /^oic\./);
				next if($p =~ /^openid\./);

				push(@param,qq|$p=|.&url_encode($cgi->param($p)));
			}

			my $host = &getGlobalPath();
			print $LOG __LINE__,":\$host=[$host]\n";
			my $url;
			if(defined $host){
				$url = $host;
#				$url =~ s/\/$// if($url =~ /[^\/][\/]$/ && $ENV{SCRIPT_NAME} =~ /^\//);
#				$url .= $ENV{SCRIPT_NAME}.(scalar @param > 0 ? '?'.join("&",@param):'');
				$url .= (scalar @param > 0 ? '?'.join("&",@param):'');
			}else{
				$host = (split(/,\s*/,(exists($ENV{HTTP_X_FORWARDED_HOST})?$ENV{HTTP_X_FORWARDED_HOST}:$ENV{HTTP_HOST})))[0];
				$url = qq|http://$host$ENV{SCRIPT_NAME}|.(scalar @param > 0 ? '?'.join("&",@param):'');
				print $LOG __LINE__,":\$url=[$url]\n";
			}
			print $LOG __LINE__,":\$url=[$url]\n";

#			my $cookie_path="/";
			my $cookie_path=undef;
			if(exists $ENV{REQUEST_URI} && defined $ENV{REQUEST_URI}){
				$cookie_path=$ENV{REQUEST_URI};
				$cookie_path=~s/[^\/]*$//g;
			}elsif(exists $ENV{SCRIPT_URL} && defined $ENV{SCRIPT_URL}){
				$cookie_path=$ENV{SCRIPT_URL};
				$cookie_path=~s/[^\/]*$//g;
			}
			foreach my $key (sort keys(%ENV)){
				print $LOG __LINE__,":\$ENV{$key}=[",$ENV{$key},"]\n";
			}
			print $LOG __LINE__,":\$cookie_path=[$cookie_path]\n";
			my $secure = exists $ENV{HTTPS} ? 1 : 0;
			my $httponly = 1;
=pod
			my $cookie = $cgi->cookie(
				-name     => 'openid_session',
				-value    => $user->{user_cancel} ? '' : $cgi->param('session'),
				-path     => $cookie_path,
				-expires  => $user->{user_cancel} ? '-1d' : '+1d',
				-httponly => $httponly,
				-secure   => $secure
			);
#print "Set-Cookie: ".CGI::Cookie->new(-name=>'openid_session',-value=>'',-expires=>'-1d',-path=>$cookie_path,-secure=>$secure,-httponly=>$httponly)."\n";
			print $LOG __LINE__,":$cookie\n";
=cut

			print &setCookie('openid_session',$user->{user_cancel} ? '' : $cgi->param('session'))," HttpOnly\n";

			print $LOG __LINE__,":$url\n";
			print $cgi->redirect(
				-uri => $url
			);
		}
		exit;
	}else{
		my $path = &catdir($FindBin::Bin,'login');
		if(-e $path && -d $path && -w $path){
			my @files = glob &catdir($path,'*.txt');
			my $curtime = time;
			foreach my $file (@files){
				my $mtime = (stat($file))[9];
				unlink $file if(($curtime-$mtime)>60*60*24);
			}
		}
	}
	close($LOG) if(defined $LOG);
	undef $LOG;
}
sub get_identity {
	my $identity = shift;
	return {} unless(defined $identity);
	my $user = +{ map { $_ => scalar $identity->$_ } qw( url display rss atom foaf declared_rss declared_atom declared_foaf foafmaker ) };
	$user->{signed_extension_fields} = $identity->signed_extension_fields('http://openid.net/extensions/sreg/1.1');
	return $user;
}

my $sth_ins_openid_session;
my $sth_sel_openid_auth;
my $sth_upd_openid_auth;
my $sth_ins_openid_auth;
sub output {
	my $session = shift;
	my $info = shift;

	print $LOG __LINE__,":\$session=[$session]\n";
	print $LOG __LINE__,":\$info=[$info]\n";
	if(defined $info){
		foreach my $key (%$info){
			print $LOG __LINE__,":\$info->{$key}=[$info->{$key}]\n";
		}
	}

	return unless(defined $session && defined $info && exists($info->{url}));

	$ag_com_auth = new AG::ComDB::Auth unless(defined $ag_com_auth);
	$ag_com_auth->openidLoginSession($info,$session);
}

my $sth_sel_openid_session;
sub openidAuthSession {
	my $openid_url = shift;
	my $openid_session = shift;

	$ag_com_auth = new AG::ComDB::Auth unless(defined $ag_com_auth);
	return $ag_com_auth->openidAuthSession($openid_url,$openid_session);
}

my $sth_del_openid_session;
sub openidLogoutSession {
	my $openid_url = shift;
	my $openid_session = shift;

	$ag_com_auth = new AG::ComDB::Auth unless(defined $ag_com_auth);
	$ag_com_auth->openidLogoutSession($openid_url,$openid_session);
	return;
}

sub makeSessionID {
	my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
	my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
	use Digest::MD5 qw(md5_hex);
	return &Digest::MD5::md5_hex($logtime.$$.'bits.cc');
}

sub getSessionID {
	my $us_id;
	use CGI;
	my $cgi = CGI->new;
	my $session = $cgi->cookie('ag_annotation.session');
	my $openid_url = $cgi->cookie('openid_url');
	my $openid_session = $cgi->cookie('openid_session');
	if(defined $openid_url && defined $openid_session){
		my($lsdb_OpenID,$lsdb_Auth,$lsdb_Config,$lsdb_Identity) = &openidAuthSession($openid_url,$openid_session);
		$us_id = $lsdb_OpenID;
	}
	if(!defined $us_id && defined $session){
		$us_id = $session;
	}
	return $us_id;
}


my $sth_sel_session;
my $sth_sel_session_state;
my $sth_sel_session_keymap;
my $sth_del_session;
my $sth_upd_session;
my $sth_ins_session;
my $sth_remove_session;
my $sth_clear_session;
my $sth_ins_session_history;
my $sth_remove_session_history;

sub _check_ag_db {
	unless(defined $ag_db && $ag_db->get_dbh()->ping()){
		undef $ag_db;
		undef $sth_sel_session if(defined $sth_sel_session);
		undef $sth_sel_session_state if(defined $sth_sel_session_state);
		undef $sth_sel_session_keymap if(defined $sth_sel_session_keymap);

		undef $sth_del_session if(defined $sth_del_session);
		undef $sth_upd_session if(defined $sth_upd_session);
		undef $sth_ins_session if(defined $sth_ins_session);
		undef $sth_remove_session if(defined $sth_remove_session);
		undef $sth_clear_session if(defined $sth_clear_session);
		undef $sth_ins_session_history if(defined $sth_ins_session_history);
		undef $sth_remove_session_history if(defined $sth_remove_session_history);
	}
	$ag_db = new AG::DB unless(defined $ag_db);
}

sub _getSession {
	my $us_id = shift;

	&_check_ag_db();
	my $dbh = $ag_db->get_dbh();
	undef $sth_sel_session if(defined $sth_sel_session);
	unless(defined $sth_sel_session){
		$sth_sel_session = $dbh->prepare(qq|select us_info from user_session where us_id=?|) or die $dbh->errstr;
	}
	$sth_sel_session->execute($us_id) or die $dbh->errstr;
	my $column_number = 0;
	my $us_info;
	$sth_sel_session->bind_col(++$column_number, \$us_info, undef);
	$sth_sel_session->fetch;
	$sth_sel_session->finish;
	$us_info = decode_json($us_info) if(defined $us_info);
	return $us_info;
}
sub getSession {
	my $us_id = shift;
	my $session_id = &getSessionID();
	my $us_info;
	$us_info = &_getSession($session_id) if(defined $session_id);
	$us_info = &_getSession($us_id) if(!defined $us_info && defined $us_id);
	return $us_info;
}

sub _getSessionState {
	my $us_id = shift;

	&_check_ag_db();
	my $dbh = $ag_db->get_dbh();
	$sth_sel_session_state = $dbh->prepare(qq|select us_state from user_session where us_id=?|) unless(defined $sth_sel_session_state);
	$sth_sel_session_state->execute($us_id);
	my $column_number = 0;
	my $us_state;
	$sth_sel_session_state->bind_col(++$column_number, \$us_state, undef);
	$sth_sel_session_state->fetch;
	$sth_sel_session_state->finish;
	return $us_state;
}
sub getSessionState {
	my $us_id = shift;
	my $session_id = &getSessionID();
	my $us_state;
	$us_state = &_getSessionState($session_id) if(defined $session_id);
	$us_state = &_getSessionState($us_id) if(!defined $us_state && defined $us_id);
	return $us_state;
}

sub _getSessionKeymap {
	my $us_id = shift;

	&_check_ag_db();
	my $dbh = $ag_db->get_dbh();
	$sth_sel_session_keymap = $dbh->prepare(qq|select us_keymap from user_session where us_id=?|) unless(defined $sth_sel_session_keymap);
	$sth_sel_session_keymap->execute($us_id);
	my $column_number = 0;
	my $us_keymap;
	$sth_sel_session_keymap->bind_col(++$column_number, \$us_keymap, undef);
	$sth_sel_session_keymap->fetch;
	$sth_sel_session_keymap->finish;
	return $us_keymap;
}
sub getSessionKeymap {
	my $us_id = shift;
	my $session_id = &getSessionID();
	my $us_keymap;
	$us_keymap = &_getSessionKeymap($session_id) if(defined $session_id);
	$us_keymap = &_getSessionKeymap($us_id) if(!defined $us_keymap && defined $us_id);
	return $us_keymap;
}

sub setSession {
	my $param_info = shift;
	my $param_state = shift;
	my $param_keymap = shift;
	my $us_id = shift;

	my $us_info;
	my $us_state;
	my $us_keymap;
	if(defined $param_info){
		if(ref $param_info){
			$us_info = &cgi_lib::common::encodeJSON($param_info);
		}else{
			$us_info = $param_info;
		}
	}
	if(defined $param_state){
		if(ref $param_state){
			$us_state = &cgi_lib::common::encodeJSON($param_state);
		}else{
			$us_state = $param_state;
		}
	}
	if(defined $param_keymap){
		if(ref $param_keymap){
			$us_keymap = &cgi_lib::common::encodeJSON($param_keymap);
		}else{
			$us_keymap = $param_keymap;
		}
	}
	my $rtn = 0;
	$us_id = &getSessionID() unless(defined $us_id);
	return $rtn unless(defined $us_id);

	&_check_ag_db();
	my $dbh = $ag_db->get_dbh();
	$dbh->{'AutoCommit'} = 0;
	$dbh->{'RaiseError'} = 1;
	eval{
		unless(defined $us_info){
			$sth_del_session = $dbh->prepare(qq|delete from user_session where us_id=?|) unless(defined $sth_del_session);
			$sth_del_session->execute($us_id);
			$rtn = $sth_del_session->rows;
			$sth_del_session->finish;
		}else{
			my $us_addr = exists($ENV{HTTP_X_FORWARDED_FOR})?$ENV{HTTP_X_FORWARDED_FOR}:$ENV{REMOTE_ADDR};
			$sth_sel_session = $dbh->prepare(qq|select us_info from user_session where us_id=?|) unless(defined $sth_sel_session);
			$sth_sel_session->execute($us_id);
			if($sth_sel_session->rows>0){
				$sth_upd_session = $dbh->prepare(qq|update user_session set us_info=?,us_state=?,us_keymap=?,us_ua=?,us_addr=?,us_modified='now()' where us_id=?|) unless(defined $sth_upd_session);
				$sth_upd_session->execute($us_info,$us_state,$us_keymap,$ENV{HTTP_USER_AGENT},$us_addr,$us_id);
				$rtn = $sth_upd_session->rows;
				$sth_upd_session->finish;
			}else{
				$sth_ins_session = $dbh->prepare(qq|insert into user_session (us_id,us_info,us_state,us_keymap,us_ua,us_addr,us_entry,us_modified) values (?,?,?,?,?,?,'now()','now()')|) unless(defined $sth_ins_session);
				$sth_ins_session->execute($us_id,$us_info,$us_state,$us_keymap,$ENV{HTTP_USER_AGENT},$us_addr);
				$rtn = $sth_ins_session->rows;
				$sth_ins_session->finish;
			}
			$sth_sel_session->finish;
		}

		#一ヶ月以上更新されない情報を削除
		$sth_remove_session = $dbh->prepare(qq|delete from user_session where us_modified<(now() - interval '1 mon')|) unless(defined $sth_remove_session);
		$sth_remove_session->execute();
		$sth_remove_session->finish;

		$dbh->commit();
	};
	if($@){
		$dbh->rollback;
		$rtn = 0;
	}
	$dbh->{'AutoCommit'} = 1;
	$dbh->{'RaiseError'} = 0;
	undef $ag_db;
	return $rtn;
}

sub clearSession {
	my $us_id = shift;

	my $rtn = 0;
	$us_id = &getSessionID() unless(defined $us_id);
	return $rtn unless(defined $us_id);

	&_check_ag_db();
	my $dbh = $ag_db->get_dbh();
	$dbh->{'AutoCommit'} = 0;
	$dbh->{'RaiseError'} = 1;
	eval{
		my $us_addr = exists($ENV{HTTP_X_FORWARDED_FOR})?$ENV{HTTP_X_FORWARDED_FOR}:$ENV{REMOTE_ADDR};
		$sth_sel_session = $dbh->prepare(qq|select us_info from user_session where us_id=?|) unless(defined $sth_sel_session);
		$sth_sel_session->execute($us_id);
		if($sth_sel_session->rows>0){
			$sth_clear_session = $dbh->prepare(qq|update user_session set us_info=null,us_ua=?,us_addr=?,us_modified='now()' where us_id=?|) unless(defined $sth_clear_session);
			$sth_clear_session->execute($ENV{HTTP_USER_AGENT},$us_addr,$us_id);
			$rtn = $sth_clear_session->rows;
			$sth_clear_session->finish;
		}
		$sth_sel_session->finish;

		$dbh->commit();
	};
	if($@){
		$dbh->rollback;
		$rtn = 0;
	}
	$dbh->{'AutoCommit'} = 1;
	$dbh->{'RaiseError'} = 0;
	undef $ag_db;
	return $rtn;
}

sub setSessionHistory {
	my $param_info = shift;
	my $us_id = shift;

	my $rtn = 0;
	$us_id = &getSessionID() unless(defined $us_id);
	return __LINE__ unless(defined $us_id);

	my $ush_info;
	if(defined $param_info){
		if(ref $param_info){
			$ush_info = &cgi_lib::common::encodeJSON($param_info);
		}else{
			$ush_info = $param_info;
		}
	}

	&_check_ag_db();
	unless($ag_db->existsTable('user_session_history')){
		undef $ag_db;
		return __LINE__;
	}

	my $dbh = $ag_db->get_dbh();
	$dbh->{'AutoCommit'} = 0;
	$dbh->{'RaiseError'} = 1;
	eval{
		use Time::Piece;
		my $t = localtime((stat($0))[9]);
		my $ush_cgi = &cgi_lib::common::encodeJSON({
			name => $0,
			mtime => $t->strftime('%Y-%m-%d %H:%M:%S')
		});

		$sth_ins_session_history = $dbh->prepare(qq|insert into user_session_history (us_id,ush_cgi,ush_info) values (?,?,?)|) unless(defined $sth_ins_session_history);
		$sth_ins_session_history->execute($us_id,$ush_cgi,$ush_info);
		$sth_ins_session_history->finish;


		#一ヶ月以上更新されない情報を削除
		$sth_remove_session_history = $dbh->prepare(qq|delete from user_session_history where ush_entry<(now() - interval '1 mon')|) unless(defined $sth_remove_session_history);
		$sth_remove_session_history->execute();
		$sth_remove_session_history->finish;

		$dbh->commit();
	};
	if($@){
		$dbh->rollback;
		$rtn = $@;
	}
	$dbh->{'AutoCommit'} = 1;
	$dbh->{'RaiseError'} = 0;
	undef $ag_db;
	return $rtn;
}

1;
