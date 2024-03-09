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

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
open(LOG,">> log.txt");
print LOG "\n[$logtime]:$0\n";



my $buf = "";
my $read_data = "";
my $remain = $ENV{'CONTENT_LENGTH'} // 0;

print qq|Content-type: text/html; charset=UTF-8\n\n|;

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
print LOG __LINE__,":\$read_data=[",$read_data,"]\n";

# データを解釈する
my $pos1 = 0; # ヘッダ部の先頭
my $pos2 = 0; # ボディ部の先頭
my $pos3 = 0; # ボディ部の終端
my $delimiter = "";
my $MAX_FORM = 50;
my $max_count = 0;
my $filename;
eval{

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
	if($name ne ""){
		unless(exists($FORM{$name})){
			if($size>0){
				$FORM{$name} = substr($read_data, $pos2, $size);
			}else{
				$FORM{$name} = undef;
			}
		}else{
			if(ref $FORM{$name} ne "ARRAY"){
				my $org_val = $FORM{$name};
				my @TEMP = ();
				$FORM{$name} = \@TEMP;
				push(@{$FORM{$name}},$org_val);
			}
			my $val;
			if($size>0){
				$val = substr($read_data, $pos2, $size);
			}else{
				$val = undef;
			}
			push(@{$FORM{$name}},$val);
		}
	}

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

};
if($@){
	&exitProcess($@);
}


my %COOKIE = ();
&getCookie(\%COOKIE);

#$FORM{lng} = $COOKIE{"ag_annotation.locale"} if(!exists($FORM{lng}) && exists($COOKIE{"ag_annotation.locale"})); #とりあえず
#$FORM{lng} = "ja" if(!exists($FORM{lng}));

foreach my $key (sort keys(%FORM)){
	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
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
unless(exists($FORM{f_id})){
	&exitProcess("Unknown Method!!");
}

#unless(exists($FORM{f_id})){
#	print qq|{success:false}|;
#	print LOG __LINE__,qq|:{success:false}\n|;
#	close(LOG);
#	exit;
#}

#my $parentURL = $FORM{parent} if(exists($FORM{parent}));
#my ($lsdb_OpenID,$lsdb_Auth);
#if(defined $parentURL){
#	($lsdb_OpenID,$lsdb_Auth) = &openidAuth($parentURL);
#}

#DEBUG
#$lsdb_OpenID = qq|http://openid.dbcls.jp/user/tyamamot| unless(defined $lsdb_OpenID);

my $parentURL = $FORM{parent} if(exists($FORM{parent}));
my ($lsdb_OpenID,$lsdb_Auth);
my $lsdb_Config;
my $lsdb_Identity;
if(defined $parentURL){
	($lsdb_OpenID,$lsdb_Auth,$lsdb_Config) = &openidAuth($parentURL);
}elsif(exists($COOKIE{openid_url}) && exists($COOKIE{openid_session})){
	($lsdb_OpenID,$lsdb_Auth,$lsdb_Config,$lsdb_Identity) = &AG::login::openidAuthSession($COOKIE{openid_url},$COOKIE{openid_session});
}

$FORM{lng} = $COOKIE{"ag_annotation.locale"} if(!exists($FORM{lng}) && exists($COOKIE{"ag_annotation.locale"})); #とりあえず
$FORM{lng} = "en" if(!exists($FORM{lng}));

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);

$dbh->{AutoCommit} = 0;
$dbh->{RaiseError} = 1;
eval{
	my $rows;
	my $total_rows = 0;
	my $sth;
	my $param_num;

	my $bp3d_table = &getBP3DTablename($FORM{version});
	if(defined $bp3d_table){
		my $sth_upd = $dbh->prepare(qq| update $bp3d_table set b_modified='now()',b_m_openid=?,b_comid=?,b_color=? where b_id=? |);
		$param_num = 0;
		$sth_upd->bind_param(++$param_num, $lsdb_OpenID);
		$sth_upd->bind_param(++$param_num, $FORM{common_id});
		$sth_upd->bind_param(++$param_num, $FORM{def_color});
		$sth_upd->bind_param(++$param_num, $FORM{f_id});
		$sth_upd->execute();
		$rows = $sth_upd->rows;
		$sth_upd->finish;
		undef $sth_upd;
		undef $bp3d_table;
	}

	my @lsdb_id_arr;
	my @lsdb_term_e_arr;
	my @lsdb_term_l_arr;
	my @lsdb_term_j_arr;
	my @lsdb_term_k_arr;

	my $lsdb_id;
	my $lsdb_term_e;
	my $lsdb_term_l;
	my $lsdb_term_j;
	my $lsdb_term_k;

	if(exists($FORM{lsdb_id})){
#		$FORM{lsdb_id} = &_trim($FORM{lsdb_id});
		if(ref $FORM{lsdb_id} eq "ARRAY"){
			push(@lsdb_id_arr,@{$FORM{lsdb_id}});
		}else{
			push(@lsdb_id_arr,$FORM{lsdb_id});
		}
	}
	if(exists($FORM{lsdb_term_e})){
#		$FORM{lsdb_term_e} =~ s/\x0D\x0A|\x0D|\x0A/;/g;
#		$FORM{lsdb_term_e} = &_trim($FORM{lsdb_term_e});
		if(ref $FORM{lsdb_term_e} eq "ARRAY"){
			push(@lsdb_term_e_arr,@{$FORM{lsdb_term_e}});
		}else{
			push(@lsdb_term_e_arr,$FORM{lsdb_term_e});
		}
	}
	if(exists($FORM{lsdb_term_l})){
#		$FORM{lsdb_term_l} =~ s/\x0D\x0A|\x0D|\x0A/;/g;
#		$FORM{lsdb_term_l} = &_trim($FORM{lsdb_term_l});
		if(ref $FORM{lsdb_term_l} eq "ARRAY"){
			push(@lsdb_term_l_arr,@{$FORM{lsdb_term_l}});
		}else{
			push(@lsdb_term_l_arr,$FORM{lsdb_term_l});
		}
	}
	if(exists($FORM{lsdb_term_j})){
#		$FORM{lsdb_term_j} =~ s/\x0D\x0A|\x0D|\x0A/;/g;
#		$FORM{lsdb_term_j} = &_trim($FORM{lsdb_term_j});
		if(ref $FORM{lsdb_term_j} eq "ARRAY"){
			push(@lsdb_term_j_arr,@{$FORM{lsdb_term_j}});
		}else{
			push(@lsdb_term_j_arr,$FORM{lsdb_term_j});
		}
	}
	if(exists($FORM{lsdb_term_k})){
#		$FORM{lsdb_term_k} =~ s/\x0D\x0A|\x0D|\x0A/;/g;
#		$FORM{lsdb_term_k} = &_trim($FORM{lsdb_term_k});
		if(ref $FORM{lsdb_term_k} eq "ARRAY"){
			push(@lsdb_term_k_arr,@{$FORM{lsdb_term_k}});
		}else{
			push(@lsdb_term_k_arr,$FORM{lsdb_term_k});
		}
	}

#foreach my $key (sort keys(%FORM)){
#	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}

	my $sth_sel = $dbh->prepare(q{ select f_id from lsdb_term where f_id=? and lsdb_id=? });
	my $sth_ins = $dbh->prepare(q{ insert into lsdb_term (lsdb_entry,lsdb_modified,lsdb_e_openid,lsdb_m_openid,lsdb_term_e,lsdb_term_l,lsdb_term_j,lsdb_term_k,f_id,lsdb_id) values ('now()','now()',?,?,?,?,?,?,?,?) });
	my $sth_upd = $dbh->prepare(q{ update lsdb_term set lsdb_modified='now()',lsdb_m_openid=?,lsdb_term_e=?,lsdb_term_l=?,lsdb_term_j=?,lsdb_term_k=?,lsdb_delcause=null where f_id=? and lsdb_id=? });
	my $sth_del = $dbh->prepare(q{ update lsdb_term set lsdb_modified='now()',lsdb_delcause='DELETE',lsdb_m_openid=? where f_id=? and lsdb_id=? });

	for(my $i=0;$i<scalar @lsdb_id_arr;$i++){
		$lsdb_id = $lsdb_id_arr[$i];
		$lsdb_term_e = $lsdb_term_e_arr[$i];
		$lsdb_term_l = $lsdb_term_l_arr[$i];
		$lsdb_term_j = $lsdb_term_j_arr[$i];
		$lsdb_term_k = $lsdb_term_k_arr[$i];

		$lsdb_term_e = undef if(length($lsdb_term_e)==0);
		$lsdb_term_l = undef if(length($lsdb_term_l)==0);
		$lsdb_term_j = undef if(length($lsdb_term_j)==0);
		$lsdb_term_k = undef if(length($lsdb_term_k)==0);

		$sth_sel->execute($FORM{f_id},$lsdb_id);
		$rows = $sth_sel->rows();
		$sth_sel->finish;


		$param_num = 0;
		if($rows == 0 && (defined($lsdb_term_e) ||defined($lsdb_term_l) ||defined($lsdb_term_j) ||defined($lsdb_term_k))){
			$sth_ins->bind_param(++$param_num, $lsdb_OpenID);
			$sth_ins->bind_param(++$param_num, $lsdb_OpenID);
			$sth_ins->bind_param(++$param_num, $lsdb_term_e);
			$sth_ins->bind_param(++$param_num, $lsdb_term_l);
			$sth_ins->bind_param(++$param_num, $lsdb_term_j);
			$sth_ins->bind_param(++$param_num, $lsdb_term_k);
			$sth_ins->bind_param(++$param_num, $FORM{f_id});
			$sth_ins->bind_param(++$param_num, $lsdb_id);
			$sth_ins->execute();
			$rows = $sth_ins->rows;
			$sth_ins->finish;
		}elsif(defined($lsdb_term_e) ||defined($lsdb_term_l) ||defined($lsdb_term_j) ||defined($lsdb_term_k)){
			$sth_upd->bind_param(++$param_num, $lsdb_OpenID);
			$sth_upd->bind_param(++$param_num, $lsdb_term_e);
			$sth_upd->bind_param(++$param_num, $lsdb_term_l);
			$sth_upd->bind_param(++$param_num, $lsdb_term_j);
			$sth_upd->bind_param(++$param_num, $lsdb_term_k);
			$sth_upd->bind_param(++$param_num, $FORM{f_id});
			$sth_upd->bind_param(++$param_num, $lsdb_id);
			$sth_upd->execute();
			$rows = $sth_upd->rows;
			$sth_upd->finish;
		}else{
			$sth_del->bind_param(++$param_num, $lsdb_OpenID);
			$sth_del->bind_param(++$param_num, $FORM{f_id});
			$sth_del->bind_param(++$param_num, $lsdb_id);
			$sth_del->execute();
			$rows = $sth_del->rows;
			$sth_del->finish;
		}
		print LOG __LINE__,":rows=[$rows]\n";
		if($rows>=0){
			$total_rows += $rows;
		}else{
			$total_rows = -1;
		}
		last if($total_rows<0);
	}

	print LOG __LINE__,":total_rows=[$total_rows]\n";
	my $success = ($total_rows>=0?"true":"false");

	if($rows>=0){
		$dbh->commit();
	}else{
		$dbh->rollback();
	}
	print qq|{success:$success}|;
	print LOG __LINE__,qq|:{success:$success}\n|;
};
if($@){
	my $msg = $@;
	$dbh->rollback();

	$msg =~ s/\s*$//g;
	$msg =~ s/^\s*//g;
	my $RTN = {
		"success" => "false",
		"msg"     => $msg
	};
#	my $json = to_json($RTN);
	my $json = encode_json($RTN);
	$json =~ s/"(true|false)"/$1/mg;
	print $json;
	print LOG __LINE__,":",$json,"\n";
}
$dbh->{AutoCommit} = 1;
$dbh->{RaiseError} = 0;


close(LOG);
exit;

sub exitProcess {
	my $msg = shift;
	my $RTN = {
		"success" => "false",
		"msg"     => $msg
	};
#	my $json = to_json($RTN);
	my $json = encode_json($RTN);
	$json =~ s/"(true|false)"/$1/mg;
	print $json;
	print LOG __LINE__,":",$json,"\n";
	close(LOG);
	exit;
}
