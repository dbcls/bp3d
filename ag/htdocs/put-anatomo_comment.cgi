#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI::Cookie;
use LWP::UserAgent;
use File::Basename;

use File::Spec::Functions qw(catdir catfile);
use Cwd;
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'API'),&Cwd::abs_path(&catdir($FindBin::Bin,'..','lib')),&Cwd::abs_path(&catdir($FindBin::Bin,'..','..','ag-common','lib'));
use cgi_lib::common;
use AG::login;

require "common.pl";
require "common_db.pl";

my %FORM = ();
my %COOKIE = ();

my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);

my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0, qr/\..*$/);
my $LOG = &cgi_lib::common::getLogFH(\%FORM,\%COOKIE);
#open $LOG,">./tmp_image/$cgi_name.txt";

=pod
my $query = CGI->new;
my %cookies = fetch CGI::Cookie;


my @param = $query->param();
foreach my $key (sort @param){
	print $LOG __LINE__,":$key=[",$query->param($key),"]\n";
	$FORM{$key} = $query->param($key);
}
foreach my $key (sort keys(%cookies)){
	print $LOG __LINE__,":$key=[",$cookies{$key}->value,"]\n";
	$COOKIE{$key} = $cookies{$key}->value;
}
=cut
#close(OUT);



#my $prmstr = "";
#my @CMDs = ();
#my $B_CMD = "";
#if($ENV{'REQUEST_METHOD'} eq 'POST'){
#	read(STDIN, $B_CMD, $ENV{'CONTENT_LENGTH'});
#	@CMDs = split(/&/, $B_CMD);
#}else{
#	$B_CMD = $ENV{'QUERY_STRING'};
#	@CMDs = split(/&/, $ENV{'QUERY_STRING'});
#}
#
#my $fma_id = "";
#foreach my $aCMD (@CMDs){
#	my ($c_key, $c_val) = split("=", $aCMD);
#	$fma_id = $c_val if ($c_key eq "fma_id");
#}

my $fma_id =$query->param('fma_id');
my $title = $query->param('title');
my $comment = $query->param('comment');
my $name = $query->param('author');
my $passwd = $query->param('passwd');
my $parent = $query->param('parent');
my $email = $query->param('email');
my $version = $FORM{version};
my $type = $query->param('type');

undef $fma_id if(defined $fma_id && $fma_id eq "");
undef $version if(defined $version && $version eq "");
undef $type if(defined $type && $type eq "");

my $prmstr = $query->param('tp_ap');
sub decodeForm_local($$) {
	my $formdata = shift;
	my $FORM;
	if(defined $formdata){
		use Encode;
		use Encode::Guess;
		my @pairs = split(/&/,$formdata);
		foreach my $pair (@pairs){
			my($name, $value) = split(/=/, $pair);
			next if($value eq '');
			$value = &url_decode($value);
			unless(utf8::is_utf8($value)){
				# UTF8フラグ がない場合、decode して、UTF8フラグつきにする
				my $guessed_obj = Encode::Guess::guess_encoding($value, qw/euc-jp shift-jis/);
				$value = $guessed_obj->decode($value) if(ref $guessed_obj);
			}
#		$value = Encode::encode('utf8', $value) if(utf8::is_utf8($value));
#			utf8::decode($value) unless(utf8::is_utf8($value));
			utf8::encode($value) if(utf8::is_utf8($value));
			$FORM = {} unless(defined $FORM);
			$FORM->{$name} .= "\0" if(exists($FORM->{$name}));
			$FORM->{$name} .= $value;
		}
	}
	return $FORM;
}
my $form = &decodeForm_local($prmstr);
if(exists $form->{iw} && exists $form->{ih}){
	if($form->{iw}<$form->{ih}){
		$form->{ih} = $form->{iw};
	}else{
		$form->{iw} = $form->{ih};
	}
}
my @PARAM = ();
foreach my $key (keys(%$form)){
	push(@PARAM,qq|$key=|.&url_encode($form->{$key}));
}
$prmstr = join("&",@PARAM);


my $path_str = &getGlobalPath();
unless(defined $path_str){
	my $host = (split(/,\s*/,(exists($ENV{HTTP_X_FORWARDED_HOST})?$ENV{HTTP_X_FORWARDED_HOST}:$ENV{HTTP_HOST})))[0];
	my @TEMP = split("/",$ENV{REQUEST_URI});
	$TEMP[$#TEMP] = "";
	$path_str = join("/",@TEMP);
	$path_str = qq|http://$host$path_str|;
}

my $PATH = &getIntermediateServerPath();

#open OUT,">./tmp_image/tmptmptmp.html";
print $LOG __LINE__,":\$path_str=[$path_str]\n";

$path_str .= $PATH->{image};
print $LOG __LINE__,":\$path_str=[$path_str]\n";

$path_str = qq|$path_str?$prmstr|;
print $LOG __LINE__,":\$path_str=[$path_str]\n";


my $ct_id = 2;
my $ua = LWP::UserAgent->new;
#my $req = HTTP::Request->new(GET => 'http://221.186.138.157/Anatomography_dev/image.cgi?'.$B_CMD);
#my $req = HTTP::Request->new(GET => 'image.cgi?tp_ap='.$prmstr);
my $req = HTTP::Request->new(GET => $path_str);


print $LOG __LINE__,":\$path_str=[$path_str]\n";

$req->authorization_basic("gogo", "togo");
my $res = $ua->request($req);
my $image;
if ($res->is_success) {
#	open OUT,">./tmp_image/tmptmptmp.png";
#	binmode(OUT);
#	print $LOG $res->content;
#	close OUT;
	$image = $res->content;
} else {
	print $LOG $res->error_as_HTML();
}
close $LOG;

$| = 1;

#print qq|Content-type: text/html; charset=UTF-8\n\n|;

use Image::Info qw(image_info dim);
use Image::Magick;
use DBI;
use DBD::Pg;
use JSON::XS;
use Digest::MD5 qw(md5 md5_hex md5_base64);


$FORM{lng} = $COOKIE{"ag_annotation.locale"} if(!exists($FORM{lng}) && exists($COOKIE{"ag_annotation.locale"})); #とりあえず
$FORM{lng} = "en" if(!exists($FORM{lng}));

my $dbh = &get_dbh();
$version = &convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);

my $parentURL = $FORM{parent} if(exists($FORM{parent}));
my ($lsdb_OpenID,$lsdb_Auth);
my $lsdb_Config;
my $lsdb_Identity;
if(defined $parentURL){
	($lsdb_OpenID,$lsdb_Auth,$lsdb_Config) = &openidAuth($parentURL);
	$passwd = md5_hex($$."bits.cc") if(defined $lsdb_OpenID);
}elsif(exists($COOKIE{openid_url}) && exists($COOKIE{openid_session})){
	($lsdb_OpenID,$lsdb_Auth,$lsdb_Config,$lsdb_Identity) = &AG::login::openidAuthSession($COOKIE{openid_url},$COOKIE{openid_session});
	$passwd = $COOKIE{openid_session} if(defined $lsdb_OpenID);
}

my $RTN = {
	"success" => JSON::XS::false,
	"msg"     => undef
};

$dbh->{AutoCommit} = 0;
$dbh->{RaiseError} = 1;
my $rows;
eval{
	my $sth;
	my $param_num;

	if($comment){
		$comment =~ s/\x0D\x0A|\x0D|\x0A/\n/mg;
		$comment = &_hesc($comment);
		$comment = &_trim($comment);
	}else{
		die qq|Undefined Comment|;
	}

	if($name){
		$name = &_hesc($name);
		$name = &_trim($name);
	}

	if($title){
		$title = &_hesc($title);
		$title = &_trim($title);
	}

	if($email){
		$email = &_hesc($email);
		$email = &_trim($email);
	}

	if($passwd){
		$passwd = &_trim($passwd);
		$passwd = md5_hex($passwd."bits.cc");
	}else{
		undef $passwd;
	}

	my $c_addr = (exists($ENV{HTTP_X_FORWARDED_FOR}) ? $ENV{HTTP_X_FORWARDED_FOR} : $ENV{REMOTE_ADDR});

	$param_num = 0;
#	$sth = $dbh->prepare(q{ insert into comment (f_id,c_pid,c_openid,c_name,c_email,c_user_agent,c_referer,c_addr,c_locale,c_title,c_comment,c_image,c_entry) values (?,?,?,?,?,?,?,?,?,?,?,?,'now()') });
#	$sth = $dbh->prepare(q{ insert into comment (c_openid,c_name,c_user_agent,c_referer,c_addr,c_locale,c_title,c_comment,c_image,c_url,ct_id,c_entry) values (?,?,?,?,?,?,?,?,?,?,?,'now()') });
	$sth = $dbh->prepare(q{ insert into comment (f_id,c_openid,c_name,c_email,c_user_agent,c_referer,c_addr,c_locale,c_title,c_comment,c_passwd,c_image,c_url,ct_id,tgi_version,t_type,c_entry) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'now()') });
#	$sth->bind_param(++$param_num, $FORM{f_id});
#	$sth->bind_param(++$param_num, $FORM{c_pid});
	$sth->bind_param(++$param_num, $fma_id);
	$sth->bind_param(++$param_num, $lsdb_OpenID);
	$sth->bind_param(++$param_num, $name);
	$sth->bind_param(++$param_num, $email);
	$sth->bind_param(++$param_num, $ENV{HTTP_USER_AGENT});
	$sth->bind_param(++$param_num, $ENV{HTTP_REFERER});
	$sth->bind_param(++$param_num, $c_addr);
	$sth->bind_param(++$param_num, $FORM{lng});
	$sth->bind_param(++$param_num, $title);
	$sth->bind_param(++$param_num, $comment);
	$sth->bind_param(++$param_num, $passwd);
	$sth->bind_param(++$param_num, $image, { pg_type => DBD::Pg::PG_BYTEA });
	$sth->bind_param(++$param_num, "cgi?tp_ap=".$prmstr);
	$sth->bind_param(++$param_num, $ct_id);
	$sth->bind_param(++$param_num, $version);
	$sth->bind_param(++$param_num, $type);
	$sth->execute();
	$rows = $sth->rows;

	$sth->finish;
	undef $sth;
	if($rows>=0){
		$dbh->commit();
		$RTN->{success} = JSON::XS::true;
	}else{
		$dbh->rollback();
	}
#	print qq|{success:$success}|;
};
if($@){
#	$RTN->{msg} = $@;
#	my $msg = $@;
#	warn __LINE__,":$msg\n";
	$dbh->rollback();
#	$msg = &_hesc($msg);

#	my $RTN = {
#		"success" => JSON::XS::false,
#		"msg"     => $msg
#	};

#	my $json = encode_json($RTN);
#	print $json;


#	warn __LINE__,qq|:$json\n|;
}

&cgi_lib::common::printContentJSON($RTN,\%FORM);

$dbh->{AutoCommit} = 1;
$dbh->{RaiseError} = 0;


exit;

sub url_encode($) {
  my $str = shift;
  $str =~ s/([^\w ])/'%'.unpack('H2', $1)/eg;
  $str =~ tr/ /+/;
  return $str;
}

sub url_decode($) {
  my $str = shift;
  $str =~ tr/+/ /;
  $str =~ s/%([0-9A-Fa-f][0-9A-Fa-f])/pack('H2', $1)/eg;
  return $str;
}
