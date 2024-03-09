package AG::API::JSONParser;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use LWP::UserAgent;
use Time::HiRes;
use Encode;
use Encode::Guess;
use File::Spec::Functions qw(catdir catfile abs2rel);
use File::Path;
use FindBin;

use SetEnv;

use cgi_lib::common;

use AG::DB;
use AG::DB::Version;

use constant {
	RETRY => 10,
	TIMEOUT => 5,
	LONG_TIMEOUT => 15,
	SLEEP_TIME_5XX => 3,
	SLEEP_TIME_XXX => 3,
};

sub new () {
	my $pkg = shift;
	my $jsonstr = shift;
	my $jsonObj;
	my $UserAgent;
	my $env = SetEnv->new;
	my $error;

#	my $log_dir = &get_log_dir_name($env->{basePath},'AgJSONParser');
#	my $log_file = &catfile($log_dir,&get_log_file_name());

	my $LOG = &cgi_lib::common::getLogFH(undef,undef,&get_log_file_basename(),&get_log_dir_basename('AgJSONParser'));

#	open OUT,"> $log_file";
#	select(OUT);
#	$| = 1;
#	select(STDOUT);
#print $LOG "\n";
#print $LOG __LINE__.':'.&getTime()."\n";

	# I.Muto 2013-10-25 from here
	# if shorten parameter exists, convert to long form before parsing json string
	my $shortenPrm;
	$shortenPrm = $1 if($jsonstr =~ /shorten=([^\&]+)/);
	print $LOG __LINE__,":\$shortenPrm=[$shortenPrm]\n" if(defined $shortenPrm);
	if(defined $shortenPrm){
		my $shorturl = new AG::ComDB::Shorturl;
		$jsonstr = $shorturl->get_long_url($shortenPrm);
		undef $shorturl;
	}
	print $LOG __LINE__,":\$jsonstr=[$jsonstr]\n" if(defined $jsonstr);
	# I.Muto 2013-10-25 to here

#	&cgi_lib::common::message($jsonstr);
	my $callback;
	if(defined $jsonstr && $jsonstr =~ /^(.*?)&*callback=*([^&]*)&*(.*)$/){
		$callback = $2;
		undef $callback unless($callback);
		$jsonstr = $1.$3;
#		&cgi_lib::common::message($1);
#		&cgi_lib::common::message($3);
	}
#	&cgi_lib::common::message($jsonstr);
	print $LOG __LINE__,":\$jsonstr=[$jsonstr]\n" if(defined $jsonstr);

	if(defined $jsonstr && $jsonstr =~ /^.*?([\{\[].+$)/){
		$jsonstr = $1;
		if($jsonstr =~ /^\[/){
			$jsonstr =~ s/^(\[.*\]).*$/$1/;
		}elsif($jsonstr =~ /^\{/){
			$jsonstr =~ s/^(\{.*\}).*$/$1/;
		}
	}
	print $LOG __LINE__,":\$jsonstr=[$jsonstr]\n" if(defined $jsonstr);

#exit;
	my $org_jsonstr = $jsonstr;
	if(defined $jsonstr){
		eval{
			my $str = &cgi_lib::common::url_decode($jsonstr);
			unless(&Encode::is_utf8($str)){
				# UTF8フラグ がない場合、decode して、UTF8フラグつきにする
				my $guessed_obj = &Encode::Guess::guess_encoding($str, qw/euc-jp shift-jis/);
				$str = $guessed_obj->decode($str) if(ref $guessed_obj);
			}
			$str = &cgi_lib::common::encodeUTF8($str);
print $LOG __LINE__.':'.$str."\n";
			$jsonObj = &cgi_lib::common::decodeJSON($str);
print $LOG __LINE__.':'.&Data::Dumper::Dumper($jsonObj);
		};
		if($@){
			print $LOG __LINE__.':'.$@."\n";
			push(@$error,__LINE__.":".$@);
		}
		unless(defined $jsonObj){
			eval{
				use AG::API::URLParser;
				my $urlParser = new AG::API::URLParser();
				$urlParser->parseURL($jsonstr);
				$jsonObj = $urlParser->{'jsonObj'};
			};
			if($@){
				print $LOG __LINE__.':'.$@."\n";
				push(@$error,__LINE__.":".$@);
			}
		}
		unless(defined $jsonObj){
print $LOG __LINE__,":\n";
			return undef;
		}
		$jsonstr = &cgi_lib::common::encodeJSON($jsonObj);
print $LOG __LINE__.':'.$jsonstr."\n" if(defined $jsonstr);

		if(defined $jsonstr){
			#正常に変換できるかチェック
			eval{
				my $temp_json = &JSON::XS::decode_json($jsonstr);
				undef $temp_json;
			};
			if($@){
				push(@$error,__LINE__.":".$@);
#				my $err_dir = &get_log_dir_name($env->{basePath},'AgJSONParser_error');
#				my $err_file = &catfile($err_dir,&get_log_file_name());
				my $ERR = &cgi_lib::common::getLogFH(undef,undef,&get_log_file_basename(),&get_log_dir_basename('AgJSONParser_error'));
#				if(open(my $ERR,">> $err_file")){
				if(defined $ERR){
#					print $ERR __LINE__.':'.&getTime()."\n";
					print $ERR __LINE__,":\$error=[\n",join("\n",@{$error}),"]\n" if(defined $error);
					print $ERR __LINE__,":\$org_jsonstr=[",$org_jsonstr,"]\n";
					print $ERR __LINE__,":\$jsonstr=[",$jsonstr,"]\n";
#					foreach my $key (sort keys(%ENV)){
#						print $ERR __LINE__,":\$ENV{$key}=[",$ENV{$key},"]\n";
#					}
					print $ERR "\n\n";
					close($ERR);
				}
				return undef;
			}
			#PartColorの文字が不正だとレンダラーでエラーになる為、削除
			if(defined $jsonObj && ref $jsonObj eq 'HASH' && exists $jsonObj->{'Part'} && defined $jsonObj->{'Part'} && ref $jsonObj->{'Part'} eq 'ARRAY'){
				foreach my $part (@{$jsonObj->{'Part'}}){
					next unless(defined $part->{'PartColor'});
					$part->{'PartColor'} =~ s/^#//g;;
					$part->{'PartColor'} = uc($part->{'PartColor'});
					next if($part->{'PartColor'} =~ /^[0-9A-F]{6}$/);
					delete $part->{'PartColor'};
				}
				$jsonstr = &cgi_lib::common::encodeJSON($jsonObj);
			}
		}

		$UserAgent = LWP::UserAgent->new(agent => 'AnatomogramGUI/0.6');
		$UserAgent->timeout(TIMEOUT);
	}

	my $db = new AG::DB();
	my %COOKIE = ();
	{
#		use common;
#		use common_db;
#		my $dbh = &common_db::get_dbh();

#		use AG::DB;
		my $dbh = $db->get_dbh();

		#レンダラーで使用するバージョンを取得
		my $Version = defined $jsonObj->{'Common'}->{'Version'} ? $jsonObj->{'Common'}->{'Version'} : undef;
		undef $Version if(defined $Version && lc($Version) eq 'latest');
#		$Version = &common::getLatestVersion($dbh,$jsonObj->{'Common'}->{Model}) unless(defined $Version);
		$Version = $db->latestRendererVersion($jsonObj->{'Common'}->{Model}) unless(defined $Version);
		my %FORM = ('version'=>$Version);
		&cgi_lib::common::getCookie(\%COOKIE);
		$FORM{lng} = $COOKIE{"ag_annotation.locale"} if(!exists($FORM{lng}) && exists($COOKIE{"ag_annotation.locale"}));
		$FORM{lng} = "en" unless(exists($FORM{lng}));

		foreach my $key (sort keys(%FORM)){
			next unless(defined $FORM{$key});
			print $LOG __LINE__,":\$FORM{$key}=[$FORM{$key}]\n";
		}
		foreach my $key (sort keys(%COOKIE)){
			next unless(defined $COOKIE{$key});
			print $LOG __LINE__,":\$COOKIE{$key}=[$COOKIE{$key}]\n";
		}
		foreach my $key (sort keys(%ENV)){
			next unless(defined $ENV{$key});
			print $LOG __LINE__,":\$ENV{$key}=[$ENV{$key}]\n";
		}
#		print $LOG __LINE__,":\$dbh=[$dbh]\n";
#		if(defined $dbh){
#			print $LOG __LINE__,":\$dbh->{pg_enable_utf8}=[$dbh->{pg_enable_utf8}]\n";
#		}else{
#			print $LOG __LINE__,":\$dbh=[undef]\n";
#		}

#		&common::convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
		$db->convDataVersion2RendererVersion(\%FORM,\%COOKIE);
		foreach my $key (sort keys(%FORM)){
			next unless(defined $FORM{$key});
			print $LOG __LINE__,":\$FORM{$key}=[$FORM{$key}]\n";
		}

		unless(defined $jsonObj->{'Common'}->{'Version'} && $jsonObj->{'Common'}->{'Version'} eq $FORM{'version'}){
			$jsonObj->{'Common'}->{'Version'} = $FORM{'version'};
			$jsonstr = &cgi_lib::common::encodeJSON($jsonObj);
		}
		unless(defined $jsonObj->{'Common'}->{'TreeName'} && $jsonObj->{'Common'}->{'TreeName'} =~ /^(isa|partof:?)$/){
#			&cgi_lib::common::message($jsonObj->{'Common'}->{'Version'});
#			&cgi_lib::common::message(int($jsonObj->{'Common'}->{'Version'}));
			my $v = $jsonObj->{'Common'}->{'Version'};
			$v =~ s/^([0-9]+).*$/$1/;
#			&cgi_lib::common::message(int($v));
#			$jsonObj->{'Common'}->{'TreeName'} = int($jsonObj->{'Common'}->{'Version'})<4 ? 'bp3d' : 'isa';
			$jsonObj->{'Common'}->{'TreeName'} = int($v)<4 ? 'bp3d' : 'isa';
			$jsonstr = &cgi_lib::common::encodeJSON($jsonObj);
		}

print $LOG __LINE__.':'.$jsonstr."\n" if(defined $jsonstr);

#		undef $dbh;
		undef $Version;
		undef %FORM;
#		undef %COOKIE;
	}

	unless(exists $jsonObj->{'Common'}->{'Model'} && defined $jsonObj->{'Common'}->{'Model'} && length $jsonObj->{'Common'}->{'Model'}){
		$jsonObj->{'Common'}->{'Model'} = 'bp3d';
	}
	unless(exists $jsonObj->{'Common'}->{'CoordinateSystemName'} && defined $jsonObj->{'Common'}->{'CoordinateSystemName'} && length $jsonObj->{'Common'}->{'CoordinateSystemName'}){
		$jsonObj->{'Common'}->{'CoordinateSystemName'} = 'bp3d';
	}
	unless(exists $jsonObj->{'Common'}->{'TreeName'} && defined $jsonObj->{'Common'}->{'TreeName'} && length $jsonObj->{'Common'}->{'TreeName'}){
		$jsonObj->{'Common'}->{'TreeName'} = 'isa';
	}
	$jsonstr = &cgi_lib::common::encodeJSON($jsonObj);


	if(defined $callback){
		$jsonObj->{callback} = $callback;
	}

	bless {
		env => $env,
		db => $db,
		UserAgent => $UserAgent,
		HTTPHeaders => undef,
		HTTPResponse => undef,
		org_jsonstr => $org_jsonstr,
		error => $error,
		json => $jsonstr,
		jsonObj => $jsonObj,
		mvpFile => $env->{basePath}."ModelVersionPort.txt",
		cookie => \%COOKIE,
		__LOG__ => $LOG
	}, $pkg;
}

sub getModel () {
	my $self = shift;
	my $model = "bp3d";
	$model = $self->{'jsonObj'}->{'Common'}->{"Model"} if(exists $self->{'jsonObj'}->{'Common'} && exists $self->{'jsonObj'}->{'Common'}->{"Model"});
	if(defined $self->{mvpFile} && -e $self->{mvpFile}){
		my %mv2p = {};
		open my $IN,$self->{mvpFile};
		while (<$IN>) {
			next if(/^#/);
			chomp;
			my ($modelwk, $versionwk, $portwk) = split("\t", $_);
			$mv2p{$modelwk}{$versionwk} = $portwk;
		}
		close $IN;
		$model = "bp3d" unless(exists $mv2p{$model});
	}
	return $model;
}

sub getVersion () {
	my $self = shift;
	my $model = $self->getModel();
	my $version = "latest";
	$version = $self->{'jsonObj'}->{'Common'}->{"Version"} if(exists $self->{'jsonObj'}->{'Common'} && exists $self->{'jsonObj'}->{'Common'}->{"Version"});
	if(defined $self->{mvpFile} && -e $self->{mvpFile}){
		my %mv2p = {};
		open my $IN,$self->{mvpFile};
		while (<$IN>) {
			next if (/^#/);
			chomp;
			my ($modelwk, $versionwk, $portwk) = split("\t", $_);
			$mv2p{$modelwk}{$versionwk} = $portwk;
		}
		close $IN;
		$version = undef if ($version eq "latest");
		unless (exists $mv2p{$model}{$version}) {
			my $port = $mv2p{$model}{"latest"};
			foreach my $ver (keys %{$mv2p{$model}}) {
				if ($mv2p{$model}{$ver} eq $port && $ver ne "latest") {
					$version = $ver;
					last;
				}
			}
		}
	}
	return $version;
}

sub getPort () {
	my $self = shift;
	my $model = "bp3d";
	my $version = "latest";
	my $port = undef;
	if(defined $self->{mvpFile} && -e $self->{mvpFile}){
		my %mv2p = {};
		open my $IN,$self->{mvpFile};
		while (<$IN>) {
			next if (/^#/);
			chomp;
			my ($modelwk, $versionwk, $portwk) = split("\t", $_);
			$mv2p{$modelwk}{$versionwk} = $portwk;
		}
		close $IN;
		if (exists $self->{'jsonObj'}->{'Common'}) {
			$version = $self->{'jsonObj'}->{'Common'}->{"Version"} if(exists $self->{'jsonObj'}->{'Common'}->{"Version"});
			$model = $self->{'jsonObj'}->{'Common'}->{"Model"}     if(exists $self->{'jsonObj'}->{'Common'}->{"Model"});
		}
		$port = $mv2p{$model}{$version};
		unless ($port) {
			if ($mv2p{$model}{"latest"}) {
				$port = $mv2p{$model}{"latest"};
			} else {
				$port = $mv2p{"bp3d"}{"latest"};
			}
		}
	}
	return $port;
}

sub getContent {
	my $self = shift;
	return $self->{'HTTPResponse'} ? $self->{'HTTPResponse'}->content : undef;
}
sub getContentCode {
	my $self = shift;
	return $self->{'HTTPResponse'} ? $self->{'HTTPResponse'}->code : undef;
}
sub getContentStatus {
	my $self = shift;
	return $self->{'HTTPResponse'} ? $self->{'HTTPResponse'}->status_line : undef;
}
sub getContentLength {
	my $self = shift;
	return $self->{'HTTPHeaders'} ? $self->{'HTTPHeaders'}->header('Content-Length') : undef;
}
sub getContentType {
	my $self = shift;
	return $self->{'HTTPHeaders'} ? $self->{'HTTPHeaders'}->header('Content-Type') : undef;
}
sub getBalancerInformation {
	my $self = shift;
	return $self->{'HTTPHeaders'} ? $self->{'HTTPHeaders'}->header('X-Balancer-Information') : undef;
}
sub _setBalancerInformation {
	my $self = shift;
	my $value = shift;
	if($self->{'HTTPHeaders'}){
		if(defined $value){
			$self->{'HTTPHeaders'}->header('X-Balancer-Information' => $value);
		}else{
			$self->{'HTTPHeaders'}->remove_header('X-Balancer-Information');
		}
	}
}

sub _initHeader {
	my $self = shift;
	$self->{'HTTPHeaders'} = undef;
	$self->{'HTTPResponse'} = undef;
}
sub _setHeader {
	my $self = shift;
	my $res = shift;
	$self->{'HTTPHeaders'} = $res->headers;
	$self->{'HTTPResponse'} = $res;
}

sub _setBeforeParam {
	my $self = shift;
	my $method = shift;

	return unless($method eq 'image' || $method eq 'print');
 
 	my $LOG = $self->{__LOG__};
	print $LOG __LINE__,":\n";
	my $jsonObj = $self->{'jsonObj'};
	return unless(defined $jsonObj && ((defined $jsonObj->{'Part'} && scalar @{$jsonObj->{'Part'}}) || (defined $jsonObj->{'Pin'} && scalar @{$jsonObj->{'Pin'}})));
	print $LOG __LINE__,":\n";
	if(exists $jsonObj->{'Common'} && defined $jsonObj->{'Common'}){
		print $LOG __LINE__,":\$jsonObj->{'Common'}->{'PinDescriptionDrawFlag'}=[$jsonObj->{'Common'}->{'PinDescriptionDrawFlag'}]\n" if(exists $jsonObj->{'Common'}->{'PinDescriptionDrawFlag'} && defined $jsonObj->{'Common'}->{'PinDescriptionDrawFlag'});
		print $LOG __LINE__,":\$jsonObj->{'Common'}->{'PinIndicationLineDrawFlag'}=[$jsonObj->{'Common'}->{'PinIndicationLineDrawFlag'}]\n" if(exists $jsonObj->{'Common'}->{'PinIndicationLineDrawFlag'} && defined $jsonObj->{'Common'}->{'PinIndicationLineDrawFlag'});
	}

#	use common;
#	use common_db;
#	my $dbh = &common_db::get_dbh();
#	my $dbh = $self->{'db'}->get_dbh();
	my $flag = 0;

	if(exists $jsonObj->{'Pin'} && defined $jsonObj->{'Pin'} && ref $jsonObj->{'Pin'} eq 'ARRAY' && scalar @{$jsonObj->{'Pin'}}){
		my $pins = $self->{'jsonObj'}->{'Pin'};
		if(scalar map {exists $_->{'PinGroupID'}} @$pins){
			$flag = 1;
			my $cookie = $self->{cookie};
			use Hash::Merge;
			use AG::ComDB;
			use AG::ComDB::Auth;
			use AG::ComDB::GlobalPin;
			my $comdb = new AG::ComDB;
			my $auth = new AG::ComDB::Auth(dbh=>$comdb->get_dbh());
			my $glbpin = new AG::ComDB::GlobalPin(dbh=>$comdb->get_dbh());
			my($authOpenID,$authAuth,$authConfig,$authIdentity) = $auth->openidAuthSession($cookie->{'openid_url'},$cookie->{'openid_session'}) if(defined $cookie && ref $cookie eq 'HASH' && defined $cookie->{'openid_url'} && defined $cookie->{'openid_session'});

			my %P = map {$_->{'PinID'}=>undef} @$pins;
			my @PS;
			foreach my $p (@$pins){
				unless(exists $p->{'PinGroupID'}){
					push(@PS,$p);
				}else{
					foreach my $key (keys(%$p)){
						unless(defined $p->{$key} && length $p->{$key}){
							delete $p->{$key};
						}elsif(
							$p->{$key} eq 'NaN' ||
							$p->{$key} eq 'undefined'
						){
							delete $p->{$key};
						}
					}
					delete $p->{'PinID'};
					my $json = &Hash::Merge::merge($p,{});
					my($rows,$data) = $glbpin->getPinList(json=>$json,openid=>$authOpenID,'sort'=>'gp_entry',dir=>'ASC');
					if(defined $data){
						foreach my $d (@$data){
							next if(exists $P{$d->{'PinID'}});
							delete $d->{'PinShape'};
							delete $d->{'PinSize'};
							delete $d->{'PinNumberDrawFlag'};
							delete $d->{'PinDescriptionDrawFlag'};
							my $np = &Hash::Merge::merge($p, $d);
							push(@PS,$np);
						}
					}
				}
			}
			$self->{'jsonObj'}->{'Pin'} = \@PS;
		}
	}


	my $drawX = 10;
	my $drawY = 10;
	my $fontSize = $self->{'env'}->{'fontSize'};
	if($method eq 'image'){
		$drawX += 80;
		$drawY += 5;
	}
	if($method eq 'print'){
		$fontSize *= 2 ;
		$drawY *= 2;
	}
	if(exists $jsonObj->{'Common'} && defined $jsonObj->{'Common'} && (
		(
			exists $jsonObj->{'Common'}->{'PinDescriptionDrawFlag'} &&
			defined $jsonObj->{'Common'}->{'PinDescriptionDrawFlag'} &&
			$jsonObj->{'Common'}->{'PinDescriptionDrawFlag'} == JSON::XS::true &&
			$jsonObj->{'Common'}->{'PinIndicationLineDrawFlag'} != 0)
#		|| ($jsonObj->{'Common'}->{'PointDescriptionDrawFlag'} == JSON::XS::true && $jsonObj->{'Common'}->{'PointIndicationLineDrawFlag'} != 0)
	)){
		#Legend
		if(defined $self->{'jsonObj'}->{'Legend'} && $self->{'jsonObj'}->{'Legend'}->{'DrawLegendFlag'} == JSON::XS::true){
			my $legend = $self->{'jsonObj'}->{'Legend'};
			if($legend->{LegendPosition} eq "UL"){
				my $str = '';
				$str .= defined $legend->{'LegendTitle'} ? $legend->{'LegendTitle'} : '';
				$str .= "\n" if(length($str)>0);
				$str .= defined $legend->{'Legend'} ? $legend->{'Legend'} : '';
				$str .= "\n" if(length($str)>0);
				$str .= defined $legend->{'LegendAuthor'} ? $legend->{'LegendAuthor'} : '';
				my @bounds = GD::Image->stringFT(0, $self->{'env'}->{'fontPath'}, $fontSize, 0, $drawX, $drawY, $str);
				$drawY = $bounds[1] + $fontSize + 1;
			}
		}
		#Pin
		if(defined $jsonObj->{'Pin'} && $jsonObj->{'Common'}->{'PinDescriptionDrawFlag'} == JSON::XS::true){
			my $pins = $self->{'jsonObj'}->{'Pin'};
			if(defined $pins && ref $pins eq 'ARRAY'){
#				for(my $i=0;$i<scalar @$pins;$i++){
#					my $pin = $pins->[$i];
				foreach my $pin (@$pins){
					my $PinID = exists $pin->{'PinID'} && defined $pin->{'PinID'} ? $pin->{'PinID'} : '';
					my $PinPartName = exists $pin->{'PinPartName'} && defined $pin->{'PinPartName'} ? $pin->{'PinPartName'} : '';
					my $PinDescription = exists $pin->{'PinDescription'} && defined $pin->{'PinDescription'} ? $pin->{'PinDescription'} : '';
					my @bounds = GD::Image->stringFT(0, $self->{'env'}->{'fontPath'}, $fontSize, 0, $drawX, $drawY, qq|$PinID : $PinPartName : $PinDescription|);
					$drawY = $bounds[1] + $fontSize + 1;
					if($jsonObj->{'Common'}->{'PinIndicationLineDrawFlag'} != 0){
						$pin->{'PinIndicationLineDrawFlag'} = $jsonObj->{'Common'}->{'PinIndicationLineDrawFlag'};
						$pin->{'PinIndicationLineScreenY'} = int(($bounds[3] + $bounds[5]) / 2);
						$pin->{'PinIndicationLineScreenX'} = int($bounds[4] + 1);
						$flag = 1;
						print $LOG __LINE__,":\$pin->{'PinIndicationLineScreen'}=[$pin->{'PinIndicationLineScreenX'}][$pin->{'PinIndicationLineScreenY'}]\n";
					}
				}
			}
		}
	}
=pod
	my %PIN;
	if(defined $jsonObj->{'Part'}){
		my $sql = qq|select f_id,p_name_e,p_label,p_coord,p_x3d,p_y3d,p_z3d,p_avx3d,p_avy3d,p_avz3d,p_uvx3d,p_uvy3d,p_uvz3d,EXTRACT(EPOCH FROM p_entry) from bp3d_point where f_pid=? or |;
		if($jsonObj->{'Common'}->{'TreeName'} eq 'isa'){
			$sql .= qq|p_is_a LIKE ?|;
		}elsif($jsonObj->{'Common'}->{'TreeName'} eq 'partof'){
			$sql .= qq|p_part_of LIKE ?|;
		}else{
			$sql .= qq|p_conventional LIKE ?|;
		}
		my $sth = $dbh->prepare($sql);
		my $count = scalar @{$jsonObj->{'Part'}};
		for(my $i=0;$i<$count;$i++){
			my $part = $jsonObj->{'Part'}->[$i];
			next if(!defined $part->{PartDrawChildPoint} || $part->{PartDrawChildPoint} == JSON::XS::false);
			$sth->execute($part->{PartID},$part->{PartID}.",%");
			if($sth->rows>0){
				my $column_number = 0;
				my $f_id;
				my $p_name_e;
				my $p_label;
				my $p_coord;
				my $p_x3d;
				my $p_y3d;
				my $p_z3d;
				my $p_avx3d;
				my $p_avy3d;
				my $p_avz3d;
				my $p_uvx3d;
				my $p_uvy3d;
				my $p_uvz3d;
				my $p_entry;
				$sth->bind_col(++$column_number, \$f_id, undef);
				$sth->bind_col(++$column_number, \$p_name_e, undef);
				$sth->bind_col(++$column_number, \$p_label, undef);
				$sth->bind_col(++$column_number, \$p_coord, undef);
				$sth->bind_col(++$column_number, \$p_x3d, undef);
				$sth->bind_col(++$column_number, \$p_y3d, undef);
				$sth->bind_col(++$column_number, \$p_z3d, undef);
				$sth->bind_col(++$column_number, \$p_avx3d, undef);
				$sth->bind_col(++$column_number, \$p_avy3d, undef);
				$sth->bind_col(++$column_number, \$p_avz3d, undef);
				$sth->bind_col(++$column_number, \$p_uvx3d, undef);
				$sth->bind_col(++$column_number, \$p_uvy3d, undef);
				$sth->bind_col(++$column_number, \$p_uvz3d, undef);
				$sth->bind_col(++$column_number, \$p_entry, undef);
				while($sth->fetch){
					my %PinItem = ();
					$PinItem{'PinID'} = $f_id;
					$PinItem{PinX} = $p_x3d;
					$PinItem{PinY} = $p_y3d;
					$PinItem{PinZ} = $p_z3d;
					$PinItem{PinArrowVectorX} = $p_avx3d;
					$PinItem{PinArrowVectorY} = $p_avy3d;
					$PinItem{PinArrowVectorZ} = $p_avz3d;
					$PinItem{PinUpVectorX} = $p_uvx3d;
					$PinItem{PinUpVectorY} = $p_uvy3d;
					$PinItem{PinUpVectorZ} = $p_uvz3d;

					$PinItem{'PinColor'} = qq|0000FF|;
					$PinItem{'PinDescriptionColor'} = qq|0000FF|;
					$PinItem{'PinDescriptionDrawFlag'} = $jsonObj->{'Common'}->{'PointDescriptionDrawFlag'} if(defined $jsonObj->{'Common'}->{'PointDescriptionDrawFlag'});
					$PinItem{'PinPartID'} = $f_id;
					$PinItem{'PinPartName'} = $p_name_e;
					$PinItem{'PinDescription'} = $p_label;
#							$PinItem{PinShape} = "PIN";
					$PinItem{PinShape} = "SC";
#							$PinItem{PinSize} = 15.0;

					if($PinItem{'PinDescriptionDrawFlag'}==JSON::XS::true){
						$PinItem{'PinIndicationLineDrawFlag'} = $jsonObj->{'Common'}->{'PointIndicationLineDrawFlag'} if(defined $jsonObj->{'Common'}->{'PointIndicationLineDrawFlag'});
#						$PinItem{'PinIndicationLineScreenX'} = 100;
#						$PinItem{'PinIndicationLineScreenY'} = 100;
					}
					$PinItem{PinSelectableFlag} = JSON::XS::true;

					$PinItem{PinEntryDate} = $p_entry;

					$PIN{$f_id} = \%PinItem;

				}
			}
			$sth->finish;
		}
		undef $sth;
	}
	if(defined $jsonObj->{'Point'}){
		my $sql = qq|select f_id,p_name_e,p_label,p_coord,p_x3d,p_y3d,p_z3d,p_avx3d,p_avy3d,p_avz3d,p_uvx3d,p_uvy3d,p_uvz3d,EXTRACT(EPOCH FROM p_entry) from bp3d_point where f_id=?|;
		my $sth = $dbh->prepare($sql);
		my $count = scalar @{$jsonObj->{'Point'}};
		for(my $i=0;$i<$count;$i++){
			my $point = $jsonObj->{'Point'}->[$i];
			if($point->{PointRemove} == JSON::XS::true){
				delete $PIN{$point->{PointID}} if(exists($PIN{$point->{PointID}}));
				next;
			}
			$sth->execute($point->{PointID});
			if($sth->rows>0){
				my $column_number = 0;
				my $f_id;
				my $p_name_e;
				my $p_label;
				my $p_coord;
				my $p_x3d;
				my $p_y3d;
				my $p_z3d;
				my $p_avx3d;
				my $p_avy3d;
				my $p_avz3d;
				my $p_uvx3d;
				my $p_uvy3d;
				my $p_uvz3d;
				my $p_entry;
				$sth->bind_col(++$column_number, \$f_id, undef);
				$sth->bind_col(++$column_number, \$p_name_e, undef);
				$sth->bind_col(++$column_number, \$p_label, undef);
				$sth->bind_col(++$column_number, \$p_coord, undef);
				$sth->bind_col(++$column_number, \$p_x3d, undef);
				$sth->bind_col(++$column_number, \$p_y3d, undef);
				$sth->bind_col(++$column_number, \$p_z3d, undef);
				$sth->bind_col(++$column_number, \$p_avx3d, undef);
				$sth->bind_col(++$column_number, \$p_avy3d, undef);
				$sth->bind_col(++$column_number, \$p_avz3d, undef);
				$sth->bind_col(++$column_number, \$p_uvx3d, undef);
				$sth->bind_col(++$column_number, \$p_uvy3d, undef);
				$sth->bind_col(++$column_number, \$p_uvz3d, undef);
				$sth->bind_col(++$column_number, \$p_entry, undef);
				$sth->fetch;

				my %PinItem = ();
				$PinItem{'PinID'} = $f_id;
				$PinItem{PinX} = $p_x3d;
				$PinItem{PinY} = $p_y3d;
				$PinItem{PinZ} = $p_z3d;
				$PinItem{PinArrowVectorX} = $p_avx3d;
				$PinItem{PinArrowVectorY} = $p_avy3d;
				$PinItem{PinArrowVectorZ} = $p_avz3d;
				$PinItem{PinUpVectorX} = $p_uvx3d;
				$PinItem{PinUpVectorY} = $p_uvy3d;
				$PinItem{PinUpVectorZ} = $p_uvz3d;

				$PinItem{'PinColor'} = $point->{PointColor};
				$PinItem{'PinDescriptionColor'} = $point->{PointColor};
				$PinItem{'PinDescriptionDrawFlag'} = $jsonObj->{'Common'}->{'PointDescriptionDrawFlag'} if(defined $jsonObj->{'Common'}->{'PointDescriptionDrawFlag'});
				$PinItem{'PinPartID'} = $f_id;
				$PinItem{'PinPartName'} = $p_name_e;
				$PinItem{'PinDescription'} = $p_label;
#							$PinItem{PinShape} = "PIN";
				$PinItem{PinShape} = "SC";
#							$PinItem{PinSize} = 15.0;

				if($PinItem{'PinDescriptionDrawFlag'}==JSON::XS::true){
					$PinItem{'PinIndicationLineDrawFlag'} = $jsonObj->{'Common'}->{'PointIndicationLineDrawFlag'} if(defined $jsonObj->{'Common'}->{'PointIndicationLineDrawFlag'});
				}
				$PinItem{PinSelectableFlag} = JSON::XS::true;

				$PinItem{PinEntryDate} = $p_entry;

				$PIN{$f_id} = \%PinItem;
			}
			$sth->finish;
		}
		undef $sth;
	}
	if(scalar keys(%PIN) > 0){
		$flag = 1;
		foreach my $f_id (sort {$PIN{$a}->{PinEntryDate} <=> $PIN{$b}->{PinEntryDate}} keys(%PIN)){
			delete $PIN{$f_id}->{PinEntryDate};
			if(defined $jsonObj->{'Common'} && ($jsonObj->{'Common'}->{'PointDescriptionDrawFlag'} == JSON::XS::true && $jsonObj->{'Common'}->{'PointIndicationLineDrawFlag'} != 0)){
				my @bounds = GD::Image->stringFT(0, $self->{'env'}->{'fontPath'}, $fontSize, 0, $drawX, $drawY, $PIN{$f_id}->{'PinID'}." : ".$PIN{$f_id}->{'PinPartName'}." : ".$PIN{$f_id}->{'PinDescription'});
				$drawY = $bounds[1] + $fontSize + 1;
				if($jsonObj->{'Common'}->{'PinIndicationLineDrawFlag'} != 0){
					$PIN{$f_id}->{'PinIndicationLineScreenY'} = int(($bounds[3] + $bounds[5]) / 2);
					$PIN{$f_id}->{'PinIndicationLineScreenX'} = int($bounds[4] + 1);
				}
			}
			push(@{$jsonObj->{'Pin'}},$PIN{$f_id});
		}
	}
=cut
	$self->{json} = &cgi_lib::common::encodeJSON($jsonObj) if($flag);
print $LOG __LINE__.':'.$self->{json}."\n" if($flag);
}

sub _getMethodContent {
	my $self = shift;
	my $method = shift;
	my $json = shift;
	return undef unless(defined $self->{UserAgent});
	$method = 'image' unless(defined $method);
	$json = $self->{json} unless(defined $json);
	my $url = $self->{'env'}->{URL}->{$method}.$self->getModel()."/".$self->getVersion()."/$method";
 	my $LOG = $self->{__LOG__};
print $LOG __LINE__,":\$url=[$url]\n";

	if($method eq 'animation' || $method eq 'point'){
		$self->{UserAgent}->timeout(LONG_TIMEOUT);
	}else{
		$self->{UserAgent}->timeout(TIMEOUT);
	}

	my $retry = RETRY;
	my $req;
	my $res;
	while($retry>0){
		print $LOG "\n" if($retry < RETRY);
		print $LOG __LINE__.':'.&getTime()."\n";
		$req = HTTP::Request->new('POST', $url);
		$req->authorization_basic('gogo', 'togo');
		$req->content($json);
#		$req->header('X-Balancer-Request' => 1);
		$res = $self->{UserAgent}->request($req);
		print $LOG __LINE__.':'.&getTime()."\n";
		print $LOG __LINE__,":\$retry=[$retry]\n";
		print $LOG __LINE__,":\$method=[$method]\n";
		print $LOG __LINE__.':'.$res->status_line."\n";
		if($res->is_success){
			print $LOG __LINE__.':'.$res->headers->as_string."\n";
			print $LOG __LINE__.':'.$res->content."\n";
			last;
		}else{
			if(exists($ENV{REQUEST_METHOD})){
				print $LOG __LINE__.':'.$retry."\n";
				print $LOG __LINE__.':'.$url."\n";
				print $LOG __LINE__.':'.$res->status_line."\n";
				print $LOG __LINE__.':'.$res->headers->as_string."\n";
				print $LOG __LINE__.':'.$res->content."\n";
				print $LOG __LINE__.':'.$json,"\n\n";

#				my $err_dir = &get_log_dir_name($self->{'env'}->{basePath},'AgJSONParser_error');
#				my $err_file = &catfile($err_dir,&get_log_file_name($res->code));

				my $ERR = &cgi_lib::common::getLogFH(undef,undef,&get_log_file_basename($res->code),&get_log_dir_basename('AgJSONParser_error'));
#				if(open(my $ERR,">> $err_file")){
				if(defined $ERR){
#					print $ERR __LINE__.':'.&getTime()."\n";
#					foreach my $key (sort keys(%ENV)){
#						print $ERR __LINE__,":\$ENV{$key}=[",$ENV{$key},"]\n";
#					}
					print $ERR __LINE__,":\$error=[\n",join("\n",@{$self->{error}}),"]\n" if(defined $self->{error});
					print $ERR __LINE__,":\$method=[",$method,"]\n";
					print $ERR __LINE__,":\$retry=[",$retry,"]\n";
					print $ERR __LINE__,":\$url=[",$url,"]\n";
					print $ERR __LINE__,":\$res->status_line=[",$res->status_line,"]\n";
					print $ERR __LINE__.":\$res->headers->as_string=[".$res->headers->as_string."]\n";
					print $ERR __LINE__,":\$res->content=[",$res->content,"]\n";
					print $ERR __LINE__,":\$self->{org_jsonstr}=[",$self->{org_jsonstr},"]\n";
					print $ERR __LINE__,":\$json=[",$json,"]\n";
					print $ERR "\n";
					close($ERR);
				}
			}else{
				&cgi_lib::common::message($retry);
				&cgi_lib::common::message($url);
				&cgi_lib::common::message($res->status_line);
				&cgi_lib::common::message($res->content);
				&cgi_lib::common::message($json);
				say STDERR qq|\n|;
			}
			sleep($res->code eq "503" || $res->code eq "500" ? SLEEP_TIME_5XX : SLEEP_TIME_XXX);
			$retry--;
		}
	}
	return ($res ,$res->is_success ? $res->content : undef);
}

sub getMethodContent {
	my $self = shift;
	my $method = shift;
	return undef unless(defined $self->{UserAgent});
	$method = 'image' unless(defined $method);
	$self->_setBeforeParam($method);
	$self->_initHeader();
	my($res,$content) = $self->_getMethodContent($method);
	$self->_setHeader($res);
	return $content;
}

sub getMethodPicture {
	my $self = shift;
	my $method = shift;
	$method = 'image' unless(defined $method);
 	my $LOG = $self->{__LOG__};
print $LOG __LINE__.':'.&getTime()."\n";
	$self->_initHeader();
	my $imgurl;
	my $img;
	my $content = $self->getMethodContent($method);
	my $balancerInformation = $self->getBalancerInformation();
print $LOG __LINE__,":\$balancerInformation=[$balancerInformation]\n" if(defined $balancerInformation);
	my $contentObj;
	eval{ $contentObj = &cgi_lib::common::decodeJSON($content) if(defined $content); };
#	$imgurl = $1 if(defined $content && $content =~ /URL\":\"(.+)?\"/);
	$imgurl = $contentObj->{Image}->{URL} if(defined $contentObj && defined $contentObj->{Image});
	undef $contentObj;
print $LOG __LINE__,":\$imgurl=[$imgurl]\n" if(defined $imgurl);
print $LOG __LINE__.':'.&getTime()."\n";
	if(defined $imgurl){

#動作確認用
#		$imgurl =~ s/192\.168\.1\.207\/spool/221\.186\.138\.155\/project\/anatomo_spool207/g;
#print $LOG __LINE__,":\$imgurl=[$imgurl]\n";

		my $retry = RETRY;
		while($retry>0){
			print $LOG "\n" if($retry < RETRY);
			print $LOG __LINE__,":\$retry=[$retry]\n";
			print $LOG __LINE__.':'.&getTime()."\n";
			$self->_initHeader();
			my $req = HTTP::Request->new('GET' => $imgurl);
			$req->authorization_basic('gogo', 'togo');
			my $res = $self->{UserAgent}->request($req);
			$self->_setHeader($res);
			$self->_setBalancerInformation($balancerInformation);
			$img = $res->content;
			print $LOG __LINE__.':'.&getTime()."\n";
			print $LOG __LINE__,":\$method=[$method]\n";
			print $LOG __LINE__.':'.$res->status_line."\n";
			if($res->is_success){
				$img = $self->drawImageInfo($method,$img);
				last;
			}else{
				if(exists($ENV{REQUEST_METHOD})){
					print $LOG __LINE__.':'.$retry."\n";
					print $LOG __LINE__.':'.$imgurl."\n";
					print $LOG __LINE__.':'.$res->status_line."\n";
					print $LOG __LINE__.':'.$res->content,"\n\n";
				}else{
					&cgi_lib::common::message($retry);
					&cgi_lib::common::message($imgurl);
					&cgi_lib::common::message($res->status_line);
					&cgi_lib::common::message($res->content);
					say STDERR qq|\n|;
				}
				sleep($res->code eq "503" || $res->code eq "500" ? SLEEP_TIME_5XX : SLEEP_TIME_XXX);
				$retry--;
			}
		}
	}
print $LOG __LINE__.':'.&getTime()."\n";
	return $img;
}

#sub url_decode($) {
#	my $str = shift;
#	$str =~ tr/+/ /;
#	$str =~ s/%([0-9A-Fa-f][0-9A-Fa-f])/pack('H2', $1)/eg;
#	return $str;
#}

sub drawImageInfo($$$) {
	my $self = shift;
	my $method = shift;
	my $png = shift;

	return $png unless($method eq 'image' || $method eq 'print');

 	my $LOG = $self->{__LOG__};

	if(defined $png &&
		( defined $self->{'jsonObj'}->{'Legend'} ||
		  defined $self->{'jsonObj'}->{'Pin'} || 
		 (defined $self->{'jsonObj'}->{'Common'} && defined $self->{'jsonObj'}->{'Common'}->{'CopyrightType'}) ||
		 (defined $self->{'jsonObj'}->{'Window'} && defined $self->{'jsonObj'}->{'Window'}->{'BackgroundColor'} && defined $self->{'jsonObj'}->{'Window'}->{'BackgroundOpacity'} && $self->{'jsonObj'}->{'Window'}->{'BackgroundOpacity'} == 0)
		)){
		my $drawX = 10;
		my $drawY = 10;
		my $fontSize = $self->{'env'}->{'fontSize'};
		if($method eq 'image'){
			$drawX += 80;
			$drawY += 5;
		}
		if($method eq 'print'){
			$fontSize *= 2 ;
			$drawY *= 2;
		}

		use GD;

		GD::Image->trueColor(1);
#		my $image = GD::Image->new($png);
		my $image;

		#Legend
		if(defined $self->{'jsonObj'}->{'Legend'} && $self->{'jsonObj'}->{'Legend'}->{'DrawLegendFlag'} == JSON::XS::true){
			my $legend = $self->{'jsonObj'}->{'Legend'};
			if($legend->{LegendPosition} eq "UL"){
				my $color;
				$image = GD::Image->new($png) unless(defined $image);
				if(length($legend->{'LegendColor'})==6){
					$color = $image->colorAllocate(hex(substr($legend->{'LegendColor'},0,2)), hex(substr($legend->{'LegendColor'},2,2)), hex(substr($legend->{'LegendColor'},4,2)));
				}else{
					$color = $image->colorAllocate(255,255,255);
				}
				my $str = '';
				$str .= defined $legend->{'LegendTitle'} ? $legend->{'LegendTitle'} : '';
				$str .= "\n" if(length($str)>0);
				$str .= defined $legend->{'Legend'} ? $legend->{'Legend'} : '';
				$str .= "\n" if(length($str)>0);
				$str .= defined $legend->{'LegendAuthor'} ? $legend->{'LegendAuthor'} : '';
				my @bounds = $image->stringFT($color, $self->{'env'}->{'fontPath'}, $fontSize, 0, $drawX, $drawY, $str);
				$drawY = $bounds[1] + $fontSize + 1;
			}
		}

		#Pin or Point
		if(defined $self->{'jsonObj'}->{'Pin'} || defined $self->{'jsonObj'}->{'Point'}){
			if(defined $self->{'jsonObj'}->{'Point'}){
			}
			my($res,$content) = $self->_getMethodContent('map');
			my $mapObj;
			if(defined $content){
				eval{
					my $jsonObj = &cgi_lib::common::decodeJSON($content);
					if(defined $jsonObj && defined $jsonObj->{Map}){
						for(my $i=0;$i<scalar @{$jsonObj->{Map}};$i++){
							next unless(defined $jsonObj->{Map}->[$i]->{'PinID'});
							$mapObj->{$jsonObj->{Map}->[$i]->{'PinID'}} = $jsonObj->{Map}->[$i];
						}
					}
				};
				print $LOG __LINE__.':'.$@."\n" if($@);
			}
			if(defined $self->{'jsonObj'}->{'Pin'}){
				my $pins = $self->{'jsonObj'}->{'Pin'};
				for(my $i=0;$i<scalar @$pins;$i++){
					my $pin = $pins->[$i];
					next unless(defined $pin && ref $pin eq 'HASH');
					my $color;
					if(defined $mapObj && exists $mapObj->{$pin->{'PinID'}} && defined $mapObj->{$pin->{'PinID'}} && ref $mapObj->{$pin->{'PinID'}} eq 'HASH' && $pin->{'PinID'} ne $pin->{'PinPartID'}){
						$image = GD::Image->new($png) unless(defined $image);
						if(length($pin->{'PinColor'})==6){
							$color = $image->colorAllocate(hex(substr($pin->{'PinColor'},0,2)), hex(substr($pin->{'PinColor'},2,2)), hex(substr($pin->{'PinColor'},4,2)));
						}else{
							$color = $image->colorAllocate(255,255,255);
						}
						my $x = $mapObj->{$pin->{'PinID'}}->{'PinScreenX'};
						my $y = $mapObj->{$pin->{'PinID'}}->{'PinScreenY'};
						if($method eq 'print'){
							$x *= 2;
							$y *= 2;
						}
						$image->filledArc($x, $y, 10, 10, 0, 360, $color) if(exists $pin->{PinShape} && defined $pin->{PinShape} && $pin->{PinShape} eq "SC");
						unless(
							exists $self->{'jsonObj'}->{'Common'} &&
							defined $self->{'jsonObj'}->{'Common'} &&
							exists $self->{'jsonObj'}->{'Common'}->{'PinNumberDrawFlag'} &&
							defined $self->{'jsonObj'}->{'Common'}->{'PinNumberDrawFlag'} &&
							$self->{'jsonObj'}->{'Common'}->{'PinNumberDrawFlag'} == JSON::XS::false
						){
							$image->string(gdGiantFont, $x + 5, $y + 5, $pin->{'PinID'}, $color);
						}
					}
					unless(exists $pin->{'PinDescriptionDrawFlag'} && defined $pin->{'PinDescriptionDrawFlag'}){
						$pin->{'PinDescriptionDrawFlag'} = $self->{'jsonObj'}->{'Common'}->{'PinDescriptionDrawFlag'};
					}else{
						$pin->{'PinDescriptionDrawFlag'} = JSON::XS::true if(lc($pin->{'PinDescriptionDrawFlag'}) eq 'true');
						$pin->{'PinDescriptionDrawFlag'} = JSON::XS::false if(lc($pin->{'PinDescriptionDrawFlag'}) eq 'false');
					}
					next if($pin->{'PinDescriptionDrawFlag'} != JSON::XS::true);
					$image = GD::Image->new($png) unless(defined $image);
					if(length($pin->{'PinDescriptionColor'})==6){
						$color = $image->colorAllocate(hex(substr($pin->{'PinDescriptionColor'},0,2)), hex(substr($pin->{'PinDescriptionColor'},2,2)), hex(substr($pin->{'PinDescriptionColor'},4,2)));
					}else{
						$color = $image->colorAllocate(255,255,255);
					}
					my @bounds = $image->stringFT($color, $self->{'env'}->{'fontPath'}, $fontSize, 0, $drawX, $drawY, $pin->{'PinID'}." : ".$pin->{'PinPartName'}." : ".($pin->{'PinDescription'} // ''));
					$drawY = $bounds[1] + $fontSize + 1;
				}
			}
		}

		#Copyright
		if(defined $self->{'jsonObj'}->{'Common'} && defined $self->{'jsonObj'}->{'Common'}->{'CopyrightType'}){
			my $copyImg;
			if($self->{'jsonObj'}->{'Common'}->{'CopyrightType'} eq "large"){
				$copyImg = GD::Image->newFromPng("img/copyrightL.png", 1);
			}elsif($self->{'jsonObj'}->{'Common'}->{'CopyrightType'} eq "medium" || $self->{'jsonObj'}->{'Common'}->{'CopyrightType'} eq "midium"){
				$copyImg = GD::Image->newFromPng("img/copyright.png", 1);
			} elsif ($self->{'jsonObj'}->{'Common'}->{'CopyrightType'} eq "small") {
				$copyImg = GD::Image->newFromPng("img/copyrightS.png", 1);
			}
			if(defined $copyImg){
				$image = GD::Image->new($png) unless(defined $image);
				my($dstW, $dstH) = $image->getBounds();
				my($srcW, $srcH) = $copyImg->getBounds();
				$image->copy($copyImg, $dstW - $srcW, $dstH - $srcH, 0, 0, $srcW, $srcH);
				undef $copyImg;
			}
		}

		if(defined $self->{'jsonObj'}->{'Window'} && defined $self->{'jsonObj'}->{'Window'}->{'BackgroundColor'} && defined $self->{'jsonObj'}->{'Window'}->{'BackgroundOpacity'} && $self->{'jsonObj'}->{'Window'}->{'BackgroundOpacity'} == 0){
			$image = GD::Image->new($png) unless(defined $image);
			my $BGC = $self->{'jsonObj'}->{'Window'}->{'BackgroundColor'};
			my $transcolor = $image->colorClosest(hex(substr($BGC,0,2)), hex(substr($BGC,2,2)), hex(substr($BGC,4,2)));
			$image->transparent($transcolor);
		}

		$png = $image->png if(defined $image);
		undef $image;

		#PNG8に変換
	#	use Image::Magick;
	#	my $im = Image::Magick->new();
	#	$im->BlobToImage($png);
	#	$im->Quantize(colors=>256,dither=>'False');
	#	$png = $im->ImageToBlob();
	#	undef $im;

#		$ContentType = qq|image/png|;
	}
	return $png;

}

sub getTime() {
	my $now = Time::HiRes::time;
	my($wtime,$msec) = split(/\./,$now);
	$msec = 0 unless(defined $msec);
	my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($wtime);
	return sprintf("AgJSONParser:%04d/%02d/%02d %02d:%02d:%02d.%d",$year+1900,$mon+1,$mday,$hour,$min,$sec,$msec);
}

sub now() {
	my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime();
	return sprintf("%04d%02d%02d%02d%02d%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
}

sub now2() {
	my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime();
	return sprintf("%04d/%02d/%02d",$year+1900,$mon+1,$mday);
}

sub get_log_dir_name {
	my $basePath = shift;
	my $type = shift;
	my @PATH = ($basePath,&get_log_dir_basename($type),&now2());
	if(exists $ENV{HTTP_X_FORWARDED_FOR} && defined $ENV{HTTP_X_FORWARDED_FOR}){
		push(@PATH,$ENV{HTTP_X_FORWARDED_FOR});
	}elsif(exists $ENV{REMOTE_ADDR} && defined $ENV{REMOTE_ADDR}){
		push(@PATH,$ENV{REMOTE_ADDR});
	}else{
		push(@PATH,'localhost');
	}
	my $log_dir = &catdir(@PATH);
	unless(-e $log_dir){
		my $old_umask = umask(0);
		&File::Path::mkpath($log_dir,0,0777);
		umask($old_umask);
	}
	return $log_dir;
}

sub get_log_dir_basename {
	my $type = shift;
	my @PATH = ('tmp_image','logs',$type);
	return &catdir(@PATH);
}

sub get_log_file_name() {
	my $status_code = shift;
	my($seconds, $microseconds) = &Time::HiRes::gettimeofday();
	my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($seconds);
	return sprintf(qq|%02d_%02d_%02d_%06d_%05d_%s.txt|,$hour,$min,$sec,$microseconds,$$,&get_log_file_basename($status_code));
}

sub get_log_file_basename() {
	my $status_code = shift;
	$status_code = 0 unless(defined $status_code);
	return sprintf(qq|%03d|,$status_code);
}

1;
