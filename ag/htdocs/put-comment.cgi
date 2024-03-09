#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use Image::Info qw(image_info dim);
use Image::Magick;
use DBI;
use DBD::Pg;
use JSON::XS;
use Digest::MD5 qw(md5 md5_hex md5_base64);

use File::Spec::Functions qw(catdir catfile);
use Cwd;
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'API'),&Cwd::abs_path(&catdir($FindBin::Bin,'..','lib')),&Cwd::abs_path(&catdir($FindBin::Bin,'..','..','ag-common','lib'));
use cgi_lib::common;
use AG::login;

require "common.pl";
require "common_db.pl";
my $dbh = &get_dbh();

my %FORM = ();

my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0, qr/\..*$/);

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
open(LOG,">> logs/$cgi_name.txt");
select(LOG);$|=1;
select(STDOUT);$|=1;
print LOG "\n[$logtime]:$0\n";

#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $RTN = {
	success => JSON::XS::false,
	msg     => undef
};

my $buf = "";
my $read_data = "";
my $remain = $ENV{'CONTENT_LENGTH'} // 0;

if($remain<=0){
	&exitProcess(qq|ERROR:Size 0!!|);
}
if(($remain/1024)>10000){
	&exitProcess(qq|ERROR:Size Over!!|);
}

binmode(STDIN);
while ($remain) {
	$remain -= sysread(STDIN, $buf, $remain);
	$read_data .= $buf;
}

# データを解釈する
my $pos1 = 0; # ヘッダ部の先頭
my $pos2 = 0; # ボディ部の先頭
my $pos3 = 0; # ボディ部の終端
my $delimiter = "";
my $MAX_FORM = 50;
my $max_count = 0;
my $filename;
while (1) {
	undef $filename;
	# ヘッダ処理
	$pos2 = index($read_data, "\r\n\r\n", $pos1) + 4;
	my @headers = split("\r\n", substr($read_data, $pos1, $pos2 - $pos1));
	my $name = "";
	foreach (@headers) {
		if ($delimiter eq "") {
			$delimiter = $_;
		} elsif (/^Content-Disposition: ([^;]*); name="([^;]*)"; filename="([^;]*)"/i) {
			$name = $2;
			if ($3) {
				$filename = $3;
				if ($filename =~ /([^\\\/]+)$/) {
					$filename = $1;
				}
			}
		} elsif (/^Content-Disposition: ([^;]*); name="([^;]*)"/i) {
			$name = $2;
		}
	}

	# ボディ処理
	$pos3 = index($read_data, "\r\n$delimiter", $pos2);
	my $size = $pos3 - $pos2;
	$FORM{$name} = substr($read_data, $pos2, $size) if($name ne "" && $size>0);

	# 終了処理
	$pos1 = $pos3 + length("\r\n$delimiter");
	if (substr($read_data, $pos1, 4) eq "--\r\n") {
		# すべてのファイルの終端
		last;
	} else {
		# 次のファイルを読み出す
		$pos1 += 2;
		last if ($max_count++ > $MAX_FORM);
		next;
	}
}



my %COOKIE = ();
&getCookie(\%COOKIE);

#$FORM{lng} = $COOKIE{"ag_annotation.locale"} if(!exists($FORM{lng}) && exists($COOKIE{"ag_annotation.locale"})); #とりあえず
#$FORM{lng} = "ja" if(!exists($FORM{lng}));

foreach my $key (sort keys(%FORM)){
	if($key eq "c_image"){
		print LOG __LINE__,":\$FORM{$key}=[IMAGE]\n";
	}else{
		print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
	}
}
foreach my $key (sort keys(%COOKIE)){
	print LOG __LINE__,":\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
}
foreach my $key (sort keys(%ENV)){
	print LOG __LINE__,":\$ENV{$key}=[",$ENV{$key},"]\n";
}

if(!&isPostMethod()){
	&exitProcess("Unknown Method!!");
}


#unless(exists($FORM{f_id})){
#	print qq|{success:false}|;
#	print LOG __LINE__,qq|:{success:false}\n|;
#	close(LOG);
#	exit;
#}

my $parentURL = $FORM{parent} if(exists($FORM{parent}));
my ($lsdb_OpenID,$lsdb_Auth);
my $lsdb_Config;
my $lsdb_Identity;
if(defined $parentURL){
	($lsdb_OpenID,$lsdb_Auth,$lsdb_Config) = &openidAuth($parentURL);
	$FORM{c_passwd} = md5_hex($$."bits.cc") if(defined $lsdb_OpenID && !exists($FORM{c_passwd}));
}elsif(exists($COOKIE{openid_url}) && exists($COOKIE{openid_session})){
	($lsdb_OpenID,$lsdb_Auth,$lsdb_Config,$lsdb_Identity) = &AG::login::openidAuthSession($COOKIE{openid_url},$COOKIE{openid_session});
	$FORM{c_passwd} = $COOKIE{openid_session} if(defined $lsdb_OpenID && !exists($FORM{c_passwd}));
}

my $image;
if(exists($FORM{c_image})){
	$image = $FORM{c_image};
	if(defined $image){
		my $image_info = image_info(\$image);
		if(defined $image_info){
			unless(exists($image_info->{width}) && exists($image_info->{height}) && exists($image_info->{file_media_type}) && exists($image_info->{file_ext})){
				&exitProcess("Unknown MIME Type!!");
			}
		}else{
			&exitProcess("Unknown File!!");
		}
	}
}
print LOG __LINE__,":image=[",(defined $image ? "true":"false"),"]\n";


$FORM{lng} = $COOKIE{"ag_annotation.locale"} if(!exists($FORM{lng}) && exists($COOKIE{"ag_annotation.locale"})); #とりあえず
$FORM{lng} = "en" if(!exists($FORM{lng}));

$FORM{version} = $FORM{tgi_version};
$FORM{tgi_version} = &convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);

$dbh->{AutoCommit} = 0;
$dbh->{RaiseError} = 1;
my $rows;
eval{
	my $sth;
	my $param_num;
	my $column_number;
	my $c_entry;

	if(exists($FORM{c_comment})){
		$FORM{c_comment} =~ s/\x0D\x0A|\x0D|\x0A/\n/g;
		my %ANCHOR = ();
		my $an_cnt = 0;
		while($FORM{c_comment} =~ /(<a(\s+.+?)<\/a>)/i){
			my $val = $1;
			my $key = sprintf("__ANCHOR_%05d__",++$an_cnt);
			$ANCHOR{$key} = $val;
			$FORM{c_comment} =~ s/<a\s+.+?<\/a>/$key/i;
		}
		$FORM{c_comment} = &_hesc($FORM{c_comment});
		$FORM{c_comment} = &_trim($FORM{c_comment});
		foreach my $key (keys(%ANCHOR)){
			$FORM{c_comment} =~ s/$key/$ANCHOR{$key}/;
		}
	}

	if(exists($FORM{c_name})){
		$FORM{c_name} = &_hesc($FORM{c_name});
		$FORM{c_name} = &_trim($FORM{c_name});
	}

	if(exists($FORM{c_email})){
		$FORM{c_email} = &_hesc($FORM{c_email});
		$FORM{c_email} = &_trim($FORM{c_email});
	}

	if(exists($FORM{c_title})){
		$FORM{c_title} = &_hesc($FORM{c_title});
		$FORM{c_title} = &_trim($FORM{c_title});
	}

	if(exists($FORM{c_passwd})){
		$FORM{c_passwd} = &_trim($FORM{c_passwd});
		$FORM{c_passwd} = md5_hex($FORM{c_passwd}."bits.cc");
	}

	my $c_addr = (exists($ENV{HTTP_X_FORWARDED_FOR}) ? $ENV{HTTP_X_FORWARDED_FOR} : $ENV{REMOTE_ADDR});

	$FORM{ct_id} = 1 if(!exists($FORM{ct_id}));
	$FORM{cs_id} = 1 if(!exists($FORM{cs_id}));

	my $next_c_id;
	$sth = $dbh->prepare(q{ select nextval('comment_c_id_seq') });
	$sth->execute();
	$column_number = 0;
	$sth->bind_col(++$column_number, \$next_c_id, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;

#	if(exists($FORM{c_id}) && $FORM{ct_id} == 2 && !defined $image){
	if(exists($FORM{c_id})){
		if(!defined $image){
			$sth = $dbh->prepare(q{ select c_entry,c_image from comment where c_id=? });
		}else{
			$sth = $dbh->prepare(q{ select c_entry from comment where c_id=? });
		}
		$sth->execute($FORM{c_id});
		$column_number = 0;
		$sth->bind_col(++$column_number, \$c_entry);
		$sth->bind_col(++$column_number, \$image, { pg_type => DBD::Pg::PG_BYTEA }) if(!defined $image);
		$sth->fetch;
		undef $sth;
	}else{
		$c_entry = sprintf("%04d-%02d-%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
	}

	$param_num = 0;
	$sth = $dbh->prepare(q{ insert into comment (f_id,c_id,c_pid,c_openid,c_name,c_email,c_user_agent,c_referer,c_addr,c_locale,c_title,c_comment,c_passwd,c_image,ct_id,cs_id,tgi_version,t_type,c_entry) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) });
	$sth->bind_param(++$param_num, $FORM{f_id});
	$sth->bind_param(++$param_num, $next_c_id);
	$sth->bind_param(++$param_num, $FORM{c_pid});
	$sth->bind_param(++$param_num, $lsdb_OpenID);
	$sth->bind_param(++$param_num, $FORM{c_name});
	$sth->bind_param(++$param_num, $FORM{c_email});
	$sth->bind_param(++$param_num, $ENV{HTTP_USER_AGENT});
	$sth->bind_param(++$param_num, $ENV{HTTP_REFERER});
	$sth->bind_param(++$param_num, $c_addr);
	$sth->bind_param(++$param_num, $FORM{lng});
	$sth->bind_param(++$param_num, $FORM{c_title});
	$sth->bind_param(++$param_num, $FORM{c_comment});
	$sth->bind_param(++$param_num, $FORM{c_passwd});
	$sth->bind_param(++$param_num, $image, { pg_type => DBD::Pg::PG_BYTEA });
	$sth->bind_param(++$param_num, $FORM{ct_id});
	$sth->bind_param(++$param_num, $FORM{cs_id});
	$sth->bind_param(++$param_num, $FORM{tgi_version});
	$sth->bind_param(++$param_num, $FORM{t_type});
	$sth->bind_param(++$param_num, $c_entry);
	$sth->execute();
	$rows = $sth->rows;

	print LOG __LINE__,":rows=[$rows]\n";
	my $success = ($rows>=0? JSON::XS::true : JSON::XS::false);
	$sth->finish;
	undef $sth;

	if(exists($FORM{c_id})){
		my $c_delcause = "$logtime\n";
		$c_delcause .= "DELETE\n";
		if(defined $lsdb_OpenID){
			$c_delcause .= "$lsdb_OpenID\n";
		}else{
			$c_delcause .= "PASSWORD\n";
		}
		$c_delcause .= "$ENV{HTTP_USER_AGENT}\n";
		$c_delcause .= "$ENV{HTTP_REFERER}\n";
		$c_delcause .= $c_addr;

		my $sql = qq|update comment set c_delcause=?,c_modified='now()' where c_id=?|;
		$sth = $dbh->prepare($sql);
		$sth->execute($c_delcause,$FORM{c_id});
		$sth->finish;
		undef $sth;

		$sql = qq|update comment set c_pid=? where c_pid=?|;
		$sth = $dbh->prepare($sql);
		$sth->execute($next_c_id,$FORM{c_id});
		$sth->finish;
		undef $sth;
	}

	if($rows>=0){
		$dbh->commit();
	}else{
		$dbh->rollback();
	}
	$RTN->{success} = $success;
#	print LOG __LINE__,qq|:{success:$success}\n|;
};
if($@){
#	my $msg = $@;
	$dbh->rollback();

#	$msg =~ s/\s*$//g;
#	$msg =~ s/^\s*//g;
#	my $RTN = {
#		"success" => "false",
#		"msg"     => $msg
#	};
#	my $json = to_json($RTN);
#	my $json = encode_json($RTN);
#	$json =~ s/"(true|false)"/$1/mg;
#	print $json;
#	print LOG __LINE__,":",$json,"\n";
}
$dbh->{AutoCommit} = 1;
$dbh->{RaiseError} = 0;

my $json = &cgi_lib::common::printContentJSON($RTN,\%FORM);
print LOG __LINE__,":",$json,"\n";

close(LOG);
exit;

sub exitProcess {
	my $msg = shift;
	my $RTN = {
		success => JSON::XS::false,
		msg     => $msg
	};
	my $json = &cgi_lib::common::printContentJSON($RTN,\%FORM);
#	my $json = to_json($RTN);
#	my $json = encode_json($RTN);
#	$json =~ s/"(true|false)"/$1/mg;
#	print $json;
	print LOG __LINE__,":",$json,"\n";
	close(LOG);
	exit;
}
