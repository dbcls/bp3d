#!/bp3d/local/perl/bin/perl

use strict;

use Net::Ping::External 'ping';
use JSON::XS;
use LWP::UserAgent;
use Data::Dumper;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/IM|;

$ENV{'AG_DB_PORT'} = qq|8543|;#BackStageEditorで変更するため、テスト用のDBを参照するようにする

require "common.pl";
require "common_db.pl";

my $dbh = &get_dbh();

my $UserAgent = LWP::UserAgent->new(agent => 'Mozilla/5.0 (Windows NT 6.0; rv:11.0) Gecko/20100101 Firefox/11.0');
$UserAgent->timeout(5);

#my $json = qq|{"Camera":{"CameraUpVectorZ":1,"Zoom":0,"CameraMode":"camera","CameraX":-0.668,"TargetX":-0.668,"TargetZ":817.0304,"CameraUpVectorX":0,"CameraY":-997.8001,"CameraZ":817.0304,"CameraUpVectorY":0,"TargetY":-109.7441},"Part":[{"PartColor":"F0D2A0","PartID":"FMA23881","PartScalarFlag":true,"PartOpacity":1,"ScalarColorFlag":true,"PartScalar":10000}],"Common":{"DateTime":"20120206213327","PinIndicationLineDrawFlag":0,"PointIndicationLineDrawFlag":0,"ScalarColorFlag":true,"ColorbarFlag":true,"Model":"bp3d","Version":"3.0","CoordinateSystemName":"bp3d","PointDescriptionDrawFlag":true},"Window":{"BackgroundColor":"FFFFFF","ImageHeight":1080,"ImageWidth":1091}}|;
my $json = qq|{"Camera":{"CameraUpVectorZ":1,"Zoom":0,"CameraMode":"camera","CameraX":-0.668,"TargetX":-0.668,"TargetZ":817.0304,"CameraUpVectorX":0,"CameraY":-997.8001,"CameraZ":817.0304,"CameraUpVectorY":0,"TargetY":-109.7441},"Common":{"DateTime":"20120206213327","PinIndicationLineDrawFlag":0,"PointIndicationLineDrawFlag":0,"ScalarColorFlag":true,"ColorbarFlag":true,"Model":"bp3d","Version":"3.0","CoordinateSystemName":"isa","PointDescriptionDrawFlag":true},"Window":{"BackgroundColor":"FFFFFF","ImageHeight":400,"ImageWidth":400}}|;

my $PARAMS = {};
my $query = CGI->new;
my @params = $query->param();
foreach my $param (@params){
	next if(exists $PARAMS->{$param} && defined $PARAMS->{$param});
	$PARAMS->{$param} = defined $query->param($param) ? $query->param($param) : undef;
	$PARAMS->{$param} = undef if(defined $PARAMS->{$param} && length($PARAMS->{$param})==0);
}
my @url_params = $query->url_param();
foreach my $url_param (sort @url_params){
	next if(exists $PARAMS->{$url_param} && defined $PARAMS->{$url_param});
	$PARAMS->{$url_param} = defined $query->url_param($url_param) ? $query->url_param($url_param) : undef;
	$PARAMS->{$url_param} = undef if(defined $PARAMS->{$url_param} && length($PARAMS->{$url_param})==0);
}

print "Content-Type: text/html;charset=UTF-8\n\n";

my @RTN = ();
#my @HOSTS = ();
#my @PORTS = ();
#my @HOSTS = qw(172.18.5.51 172.18.5.53 172.18.5.54);
#my @HOSTS = qw(172.18.5.51 172.18.5.53);
#my @HOSTS = qw(172.18.5.51 172.18.5.54);
#my @HOSTS = qw(172.18.5.53 172.18.5.54);
#my @HOSTS = qw(172.18.5.54);
#my @PORTS = qw(8105 8107 8109 8111 8113);

#push(@HOSTS,qq|172.18.5.53|) if(exists $PARAMS->{'keywords'} && lc($PARAMS->{'keywords'}) eq 'all');



my @HOSTS = ();
my $sql = qq|select rh_ip from renderer_hosts where rh_use and rh_delcause is null order by rh_ip|;
my $sth = $dbh->prepare($sql);
$sth->execute();
my $column_number = 0;
my $rh_ip;
$sth->bind_col(++$column_number, \$rh_ip, undef);
while($sth->fetch){
	next unless(defined $rh_ip);
	push(@HOSTS,$rh_ip);
}
$sth->finish;
undef $sth;


my @PORTS = ();
my $sql = qq|select mv_port from model_version where mv_publish and mv_use and mv_frozen and mv_delcause is null order by mv_port|;
my $sth = $dbh->prepare($sql);
$sth->execute();
my $column_number = 0;
my $mv_port;
$sth->bind_col(++$column_number, \$mv_port, undef);
while($sth->fetch){
	next unless(defined $mv_port);
	push(@PORTS,$mv_port);
}
$sth->finish;
undef $sth;



my @STATUS;
my $status;
my $code;
foreach my $host (@HOSTS){
	my $alive = ping(host => $host, timeout => 3);
	if($alive){
#		print "$host is alive!\n";
		foreach my $port (@PORTS){
			my $url = qq|http://$host:$port/renderer/image|;
			my $req = HTTP::Request->new('POST',$url);
			$req->content($json);
			my $res = $UserAgent->request($req);
			push(@RTN,{
				host => $host,
				port => $port,
				url => $url,
				status => $res->status_line,
				code => $res->code
			});
			if($res->is_success){
				$status = $res->status_line unless(defined $status);
				$code = $res->code unless(defined $code);
			}else{
				$status = $res->status_line;
				$code = $res->code;
			}
		}
	}else{
		$status = qq|503 Service Unavailable|;
		$code = qq|503|;
		push(@RTN,{
			host => $host,
			status => $status,
			code => $code
		});
	}
}
#print "Status: ",$status,"\n\n$status\n";

#print $status,"\n";
print qq|status_code_$code\n|;
if($code ne '200'){
	print qq|<pre>|;
	print Dumper(\@RTN);
	print qq|</pre>|;

#	my $json = &JSON::XS::encode_json(\@RTN);
#	utf8::decode($json) unless(utf8::is_utf8($json));
#	$json =~ s/(\},)([^\s])/$1\n$2/g;
#	utf8::encode($json) if(utf8::is_utf8($json));
#	print $json;
}

=pod
my $sendmail = '/usr/sbin/sendmail'; # sendmailコマンドパス
my $from = 'tyamamot@bits.cc'; # 送信元メールアドレス
my $to = 'tyamamot@bits.cc'; # あて先メールアドレス
#$cc = 'hage@example.com'; # Ccのあて先メールアドレス
my $subject = 'test'; # メールの件名
my $msg = <<"_TEXT_"; # メールの本文(ヒアドキュメントで変数に代入)
message line 1
message line 2
_TEXT_
# sendmail コマンド起動
open(SDML,"| $sendmail -t -i") || die 'sendmail error';
# メールヘッダ出力
print SDML "From: $from\n";
print SDML "To: $to\n";
#print SDML "Cc: $cc\n";
print SDML "Subject: $subject\n";
print SDML "Content-Transfer-Encoding: 7bit\n";
print SDML "Content-Type: text/plain;\n\n";
# メール本文出力
print SDML "$msg";
# sendmail コマンド閉じる
close(SDML); 
mail -s "Tripwire(R) Integrity Check Report in `hostname`" tyamamot@bits.cc
=cut
