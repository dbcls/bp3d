use strict;

use JSON::XS;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/IM|,qq|$FindBin::Bin/../../ag-common/lib|;
use AG::ComDB::Auth;

my $ag_com_auth;

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
			print LOG __LINE__,":\$check_url=[$check_url]\n";
			print $cgi->redirect(-uri => $check_url);
			exit;
		}
	}elsif($cgi->param('verify')){
		print LOG __LINE__,"\n";
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
			print LOG __LINE__,":$setup_url\n";
			print $cgi->redirect(-uri => $setup_url);
		}else{
			my $user;
			if($csr->user_cancel){
				print LOG __LINE__,"\n";
				$user = &get_identity($identity);
				$user->{user_cancel} = "true";
				&output($cgi->param('session'),$user);

			}elsif(defined $identity){
				print LOG __LINE__,"\n";
				$user = &get_identity($identity);
				&output($cgi->param('session'),$user);
			}else{
				print LOG __LINE__,"\n";
				$user = &get_identity($identity);
				$user->{errcode} = $csr->errcode;
				$user->{errtext} = $csr->errtext;
				&output($cgi->param('session'),$user);
			}
			print LOG __LINE__,"\n";

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
			print LOG __LINE__,":\$host=[$host]\n";
			my $url;
			if(defined $host){
				$url = $host;
#				$url =~ s/\/$// if($url =~ /[^\/][\/]$/ && $ENV{SCRIPT_NAME} =~ /^\//);
#				$url .= $ENV{SCRIPT_NAME}.(scalar @param > 0 ? '?'.join("&",@param):'');
				$url .= (scalar @param > 0 ? '?'.join("&",@param):'');
			}else{
				$host = (split(/,\s*/,(exists($ENV{HTTP_X_FORWARDED_HOST})?$ENV{HTTP_X_FORWARDED_HOST}:$ENV{HTTP_HOST})))[0];
				$url = qq|http://$host$ENV{SCRIPT_NAME}|.(scalar @param > 0 ? '?'.join("&",@param):'');
				print LOG __LINE__,":\$url=[$url]\n";
			}
			print LOG __LINE__,":\$url=[$url]\n";

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
				print LOG __LINE__,":\$ENV{$key}=[",$ENV{$key},"]\n";
			}
			print LOG __LINE__,":\$cookie_path=[$cookie_path]\n";
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
			print LOG __LINE__,":$cookie\n";
=cut

			print &setCookie('openid_session',$user->{user_cancel} ? '' : $cgi->param('session'))," HttpOnly\n";

			print LOG __LINE__,":$url\n";
			print $cgi->redirect(
				-uri => $url
			);
		}
		exit;
	}else{
		my $path = qq|login|;
		if(opendir(DIR,$path)){
			my @files = grep /\.txt/, readdir(DIR);
			closedir(DIR);
			my $curtime = time;
			foreach my $file (@files){
				my $filename = qq|$path/$file|;
				next unless(-e $filename);
				my $mtime = (stat($filename))[9];
				unlink $filename if(($curtime-$mtime)>60*60*24);
			}
		}
	}
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

	print LOG __LINE__,":\$session=[$session]\n";
	print LOG __LINE__,":\$info=[$info]\n";
	if(defined $info){
		foreach my $key (%$info){
			print LOG __LINE__,":\$info->{$key}=[$info->{$key}]\n";
		}
	}

	return unless(defined $session && defined $info && exists($info->{url}));

	$ag_com_auth = new AG::ComDB::Auth unless(defined $ag_com_auth);
	$ag_com_auth->openidLoginSession($info,$session);
	return;

=pod
	my $json = &JSON::XS::encode_json($info);

	print LOG $json,"\n";

	my $dbh = &get_dbh();
	$dbh->{AutoCommit} = 0;
	$dbh->{RaiseError} = 1;
	eval{
		$sth_ins_openid_session = $dbh->prepare(qq|insert into openid_session (os_openid,os_id,os_info,os_entry) values (?,?,?,'now()')|) unless(defined $sth_ins_openid_session);
		$sth_ins_openid_session->execute($info->{url},$session,$json);
		$sth_ins_openid_session->finish;

		$sth_sel_openid_auth = $dbh->prepare(qq|select oa_auth from openid_auth where oa_openid=?|) unless(defined $sth_sel_openid_auth);
		$sth_sel_openid_auth->execute($info->{url});
		my $rows = $sth_sel_openid_auth->rows;
		if($rows>0){
			$sth_upd_openid_auth = $dbh->prepare(qq|update openid_auth set oa_info=?,oa_modified='now()' where oa_openid=?|) unless(defined $sth_upd_openid_auth);
			$sth_upd_openid_auth->execute($json,$info->{url});
			$sth_upd_openid_auth->finish;
		}else{
			$sth_ins_openid_auth = $dbh->prepare(qq|insert into openid_auth (oa_openid,oa_info,oa_entry,oa_modified) values (?,?,'now()','now()')|) unless(defined $sth_ins_openid_auth);
			$sth_ins_openid_auth->execute($info->{url},$json);
			$sth_ins_openid_auth->finish;
		}
		$dbh->commit();
	};
	if($@){
		warn __LINE__,":",$@,"\n";
		$dbh->rollback;
	}
	$dbh->{AutoCommit} = 1;
	$dbh->{RaiseError} = 0;
=cut
}

my $sth_sel_openid_session;
sub openidAuthSession {
	my $openid_url = shift;
	my $openid_session = shift;

	$ag_com_auth = new AG::ComDB::Auth unless(defined $ag_com_auth);
	return $ag_com_auth->openidAuthSession($openid_url,$openid_session);

=pod
	my($lsdb_OpenID,$lsdb_Auth,$lsdb_Config,$lsdb_Identity);
	my $dbh = &get_dbh();
	$sth_sel_openid_session = $dbh->prepare(qq|select os_info from openid_session where os_openid=? and os_id=?|) unless(defined $sth_sel_openid_session);
	$sth_sel_openid_session->execute($openid_url,$openid_session);
	if($sth_sel_openid_session->rows>0){
		my $os_info;
		my $column_number = 0;
		$sth_sel_openid_session->bind_col(++$column_number, \$os_info, undef);
		$sth_sel_openid_session->fetch;
		if(0){#ローカルに管理者権限を管理するように変更
			my $ua = LWP::UserAgent->new;
			$ua->timeout(60);
			my $req = new HTTP::Request GET => qq|http://lifesciencedb.jp/lsdb_ag_auth.cgi?openid_url=$openid_url|;
			$req->authorization_basic('gogo', 'togo');
			my $res = $ua->request($req);
			if($res->is_success){
				my $parent_text = $res->content;
				unless(utf8::is_utf8($parent_text)){
					# UTF8フラグ がない場合、decode して、UTF8フラグつきにする
					my $guessed_obj = Encode::Guess::guess_encoding($parent_text, qw/euc-jp shift-jis/);
					$parent_text = $guessed_obj->decode($parent_text) if(ref $guessed_obj);
				}
				($lsdb_OpenID,$lsdb_Auth,$lsdb_Config) = split(/\t/,$parent_text);
				$lsdb_Config =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg if(defined $lsdb_Config);

#				use JSON;
#				$lsdb_Identity = from_json($os_info) if(defined $os_info);
				$lsdb_Identity = decode_json($os_info) if(defined $os_info);
			}
		}else{
			$lsdb_OpenID = $openid_url;
#			use JSON;
#			$lsdb_Identity = from_json($os_info) if(defined $os_info);
			$lsdb_Identity = decode_json($os_info) if(defined $os_info);
			$sth_sel_openid_auth = $dbh->prepare(qq|select oa_auth from openid_auth where oa_openid=?|) unless(defined $sth_sel_openid_auth);
			$sth_sel_openid_auth->execute($openid_url);
			$column_number = 0;
			$sth_sel_openid_auth->bind_col(++$column_number, \$lsdb_Auth, undef);
			$sth_sel_openid_auth->fetch;
			$sth_sel_openid_auth->finish;
		}
	}
	$sth_sel_openid_session->finish;
	return ($lsdb_OpenID,$lsdb_Auth,$lsdb_Config,$lsdb_Identity);
=cut
}

my $sth_del_openid_session;
sub openidLogoutSession {
	my $openid_url = shift;
	my $openid_session = shift;

	$ag_com_auth = new AG::ComDB::Auth unless(defined $ag_com_auth);
	$ag_com_auth->openidLogoutSession($openid_url,$openid_session);
	return;

=pod
	my $dbh = &get_dbh();
	$dbh->{AutoCommit} = 0;
	$dbh->{RaiseError} = 1;
	eval{
		$sth_del_openid_session = $dbh->prepare(qq|delete from openid_session where os_openid=? and os_id=?|) unless(defined $sth_del_openid_session);
		$sth_del_openid_session->execute($openid_url,$openid_session);
		$sth_del_openid_session->finish;
		$dbh->commit();
	};
	if($@){
		$dbh->rollback;
	}
	$dbh->{AutoCommit} = 1;
	$dbh->{RaiseError} = 0;
=cut
}

sub makeSessionID {
	my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
	my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
	use Digest::MD5 qw(md5_hex);
	return &Digest::MD5::md5_hex($logtime.$$."bits.cc");
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
sub _getSession {
	my $us_id = shift;
	my $dbh = &get_dbh();
	$sth_sel_session = $dbh->prepare(qq|select us_info from user_session where us_id=?|) unless(defined $sth_sel_session);
	$sth_sel_session->execute($us_id);
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

my $sth_sel_session_state;
sub _getSessionState {
	my $us_id = shift;
	my $dbh = &get_dbh();
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

my $sth_sel_session_keymap;
sub _getSessionKeymap {
	my $us_id = shift;
	my $dbh = &get_dbh();
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

my $sth_del_session;
my $sth_upd_session;
my $sth_ins_session;
my $sth_remove_session;
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
			$us_info = encode_json($param_info);
		}else{
			$us_info = $param_info;
		}
		$us_info =~ s/"(true|false)"/$1/g;
	}
	if(defined $param_state){
		if(ref $param_state){
			$us_state = encode_json($param_state);
		}else{
			$us_state = $param_state;
		}
		$us_state =~ s/"(true|false)"/$1/g;
	}
	if(defined $param_keymap){
		if(ref $param_keymap){
			$us_keymap = encode_json($param_keymap);
		}else{
			$us_keymap = $param_keymap;
		}
		$us_keymap =~ s/"(true|false)"/$1/g;
	}
	my $rtn = 0;
	$us_id = &getSessionID() unless(defined $us_id);
	return $rtn unless(defined $us_id);

	my $dbh = &get_dbh();
	$dbh->{AutoCommit} = 0;
	$dbh->{RaiseError} = 1;
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
	$dbh->{AutoCommit} = 1;
	$dbh->{RaiseError} = 0;
	return $rtn;
}

my $sth_clear_session;
sub clearSession {
	my $us_id = shift;

	my $rtn = 0;
	$us_id = &getSessionID() unless(defined $us_id);
	return $rtn unless(defined $us_id);

	my $dbh = &get_dbh();
	$dbh->{AutoCommit} = 0;
	$dbh->{RaiseError} = 1;
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
	$dbh->{AutoCommit} = 1;
	$dbh->{RaiseError} = 0;
	return $rtn;
}


1;
