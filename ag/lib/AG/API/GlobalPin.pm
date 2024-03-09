package AG::API::GlobalPin;

use strict;
#use AgJSONParser;
use File::Basename;
use File::Spec;
use JSON::XS;

use AG::ComDB;
use AG::ComDB::Auth;
use AG::ComDB::GlobalPin;

use constant {
	DEBUG => AG::ComDB::GlobalPin::DEBUG,

	CMD_ADDING   => 'post',
	CMD_UPDATE   => 'update',
	CMD_DELETE   => 'remove',
	CMD_SEARCH   => 'search',
	CMD_GET      => 'get',
	CMD_GET_ATTR => 'getattr',
	CMD_GET_LIST => 'getlist',
	CMD_LINK     => 'link',
	CMD_UNLINK   => 'unlink',
	CMD_AUTH     => 'auth',

	TYPE_PIN   => 'pin',
	TYPE_GROUP => 'group',
};

sub parse {
	my %arg = @_;
	my $cmd     = $arg{'cmd'};
	my $type    = $arg{'type'};
	my $json    = $arg{'json'};
	my $start   = $arg{'start'};
	my $limit   = $arg{'limit'};
	my $sort    = $arg{'sort'},
	my $dir     = $arg{'dir'},
	my $cookie  = $arg{'cookie'};
	my $forcing = $arg{'forcing'};
	my $RTN = {
		success => JSON::XS::false,
		message => undef
	};
	eval{
		my $comdb = new AG::ComDB;
		my $auth = new AG::ComDB::Auth(dbh=>$comdb->get_dbh());
		my $glbpin = new AG::ComDB::GlobalPin(dbh=>$comdb->get_dbh());
		my($authOpenID,$authAuth,$authConfig,$authIdentity) = $auth->openidAuthSession($cookie->{'openid_url'},$cookie->{'openid_session'}) if(defined $cookie->{'openid_url'} && defined $cookie->{'openid_session'});

		&_log(":\$arg{'json'}=[$arg{'json'}]",__LINE__);

		my $jsonObj;
		eval{$jsonObj = &JSON::XS::decode_json($arg{'json'}) if(defined $arg{'json'});};
		&Carp::croak($@.'('.__LINE__.')') if($@);

		&_log("",__LINE__);

		my $success = JSON::XS::false;
		my $message = undef;
		my $rows = undef;
		my $datas;
		my $method;
		if($arg{'cmd'} eq CMD_LINK){
			$method = 'linkPinGroup'.($forcing?'Forcing':'');
		}elsif($arg{'cmd'} eq CMD_UNLINK){
			$method = 'unlinkPinGroup'.($forcing?'Forcing':'');
		}elsif($arg{'cmd'} eq CMD_AUTH){
			$method = 'auth';
		}else{
			$datas = [];
			if($arg{'type'} eq TYPE_PIN){
				if($arg{'cmd'} eq CMD_ADDING){
					$method = 'addPin';
				}elsif($arg{'cmd'} eq CMD_UPDATE){
					$method = 'updatePin';
				}elsif($arg{'cmd'} eq CMD_DELETE){
					$method = 'removePin';
				}elsif($arg{'cmd'} eq CMD_SEARCH){
					$method = 'searchPin';
				}elsif($arg{'cmd'} eq CMD_GET){
					$method = 'getPin';
				}elsif($arg{'cmd'} eq CMD_GET_LIST){
					$method = 'getPinList';
				}
				$RTN->{'Pin'} = $datas;
			}elsif($arg{'type'} eq TYPE_GROUP){
				if($arg{'cmd'} eq CMD_ADDING){
					$method = 'addPinGroup';
				}elsif($arg{'cmd'} eq CMD_UPDATE){
					$method = 'updatePinGroup';
				}elsif($arg{'cmd'} eq CMD_DELETE){
					$method = 'removePinGroup';
				}elsif($arg{'cmd'} eq CMD_SEARCH){
					$method = 'searchPinGroup'.($forcing?'Forcing':'');
				}elsif($arg{'cmd'} eq CMD_GET){
					$method = 'getPinGroup'.($forcing?'Forcing':'');
				}elsif($arg{'cmd'} eq CMD_GET_ATTR){
					$method = 'getPinGroupAttr';
				}elsif($arg{'cmd'} eq CMD_GET_LIST){
					$method = 'getPinGroupList';
				}
				$RTN->{'PinGroup'} = $datas;
			}
		}
		&_log(":\$method=[$method]",__LINE__);
		($success,$message,$rows) = &_execFunc(json=>$jsonObj,openid=>$authOpenID,glbpin=>$glbpin,datas=>$datas,start=>$start,limit=>$limit,'sort'=>$sort,dir=>$dir,cookie=>$cookie,method=>$method) if(defined $method);
		$RTN->{'success'} = $success;
		$RTN->{'message'} = $message;
		&_log(":\$success=[$success]",__LINE__);

		if($arg{'cmd'} eq CMD_AUTH){
			$datas = [];
			if($arg{'type'} eq TYPE_PIN){
				$method = 'getPin';
				$RTN->{'Pin'} = $datas;
			}elsif($arg{'type'} eq TYPE_GROUP){
				$method = 'getPinGroup';
				$RTN->{'PinGroup'} = $datas;
			}
			my($success,$message) = &_execFunc(json=>$jsonObj,openid=>$authOpenID,glbpin=>$glbpin,datas=>$datas,start=>$start,limit=>$limit,'sort'=>$sort,dir=>$dir,cookie=>$cookie,method=>$method) if(defined $method);
		}
		$RTN->{'total'} = $rows + 0 if(defined $rows);
	};
	if($@){
		$RTN->{'success'} = JSON::XS::false;
		$RTN->{'message'} = $@;
#		print __LINE__.":\$arg{'json'}=[$arg{'json'}]<br>\n" if(defined $arg{'json'});
	}
	if(defined $RTN->{'message'}){
		&utf8::decode($RTN->{'message'}) unless(&utf8::is_utf8($RTN->{'message'}));
	}
	return $RTN;
}

sub _execFunc {
	my %arg = @_;
	my $json    = $arg{'json'};
	my $start   = $arg{'start'};
	my $limit   = $arg{'limit'};
	my $sort    = $arg{'sort'},
	my $dir     = $arg{'dir'},
	my $cookie  = $arg{'cookie'};
	my $openid  = $arg{'openid'};
#	my $forcing = $arg{'forcing'};
	my $glbpin  = $arg{'glbpin'};
	my $datas   = $arg{'datas'};
	my $method  = $arg{'method'};
	my $success = JSON::XS::false;
	my $message = undef;
	my $rows;
	my $data;
	$json = {} unless(defined $json);
	if(defined $json){
		if(defined $datas){
			($rows,$data) = $glbpin->$method(json=>$json,openid=>$openid,start=>$start,limit=>$limit,'sort'=>$sort,dir=>$dir,cookie=>$cookie);
			&_log(":\$rows=[$rows]",__LINE__);
			&_log("\$data=[$data]",__LINE__);
			if(defined $data){
				if(ref $data eq 'HASH'){
					$success = JSON::XS::true;
					push(@$datas,$data);
				}elsif(ref $data eq 'ARRAY'){
					$success = JSON::XS::true;
					push(@$datas,@$data);
				}
			}
		}else{
			$success = JSON::XS::true if($rows = $glbpin->$method(json=>$json,openid=>$openid,start=>$start,limit=>$limit,'sort'=>$sort,dir=>$dir,cookie=>$cookie));
		}
		$message = $glbpin->error() if($success == JSON::XS::false);
	}
	return ($success,$message,$rows);
}

sub _log {
	my $msg = shift;
	my $line = shift;
	print __PACKAGE__.":$line:$msg<br>\n" if(DEBUG);
#	warn __PACKAGE__.":$line:$msg\n" if(DEBUG);
}
1;
