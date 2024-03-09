#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use Data::Dumper;
use DBD::Pg;
use File::Path;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI::Cookie;
use File::Spec::Functions qw(catdir catfile);

use Cwd;
use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/IM|,&Cwd::abs_path(qq|$FindBin::Bin/../../ag-common/lib|);
use cgi_lib::common;

require "common.pl";
require "common_db.pl";

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);
#my($logfile,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);
=pod
my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
my $filetime = sprintf("%04d/%02d/%02d",$year+1900,$mon+1,$mday);
my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0, qr/\..*$/);
my $log_dir = &catdir($FindBin::Bin,'logs',$filetime);
if(exists $ENV{'HTTP_X_FORWARDED_FOR'}){
	my @H = split(/,\s*/,$ENV{'HTTP_X_FORWARDED_FOR'});
	$log_dir = &catdir($log_dir,$H[0]);
}elsif(exists $ENV{'REMOTE_ADDR'}){
	$log_dir = &catdir($log_dir,$ENV{'REMOTE_ADDR'});
}
$log_dir = &catdir($log_dir,$COOKIE{'ag_annotation.session'}) if(exists $COOKIE{'ag_annotation.session'});
unless(-e $log_dir){
	my $old_umask = umask(0);
	&File::Path::mkpath($log_dir,0,0777);
	umask($old_umask);
}
open(LOG,">> $log_dir/$cgi_name.txt");
flock(LOG,2);
select(LOG);
$| = 1;
select(STDOUT);
print $LOG "\n[$logtime]:$0\n";
foreach my $key (sort keys(%FORM)){
	print $LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
}
foreach my $key (sort keys(%COOKIE)){
	print $LOG "\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
}
foreach my $key (sort keys(%ENV)){
	print $LOG __LINE__,":\$ENV{$key}=[",$ENV{$key},"]\n";
}
=cut
my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0, qr/\..*$/);
my $LOG = &cgi_lib::common::getLogFH(\%FORM,\%COOKIE);

#&setDefParams(\%FORM,\%COOKIE);

#foreach my $key (sort keys(%FORM)){
#	print $LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
&cgi_lib::common::dumper(\%FORM,$LOG) if(defined $LOG);

#$FORM{'cmd'}=qq|tree-path|;
#$FORM{'params'}=qq|{"model":"bp3d","version":"4.0","ag_data":"obj/bp3d/4.0","tree":"isa","md_id":1,"mv_id":3,"mr_id":2,"ci_id":1,"cb_id":4,"bul_id":3,"cdi_name":"FMA18886"}|;


my $DATAS = {
	"datas" => [],
	"total" => 0,
	"success" => JSON::XS::false
};

if(defined $FORM{'cmd'}){
	if($FORM{'cmd'} eq 'upload-all-list'){
		&outputUploadAllList($dbh,\%FORM);
		exit;
	}elsif($FORM{'cmd'} eq 'concept-objfiles-list'){
		&exportFMA2UploadAllList($dbh,\%FORM);
		exit;

=pod
	}elsif($FORM{'cmd'} eq 'tree-path' && defined $FORM{'params'}){
		&getTreePath($dbh,\%FORM,$DATAS);

	}elsif($FORM{'cmd'} eq 'history-mapping' && defined $FORM{'art_id'}){
		&getHistoryMapping($dbh,\%FORM,$DATAS);

	}elsif($FORM{'cmd'} eq 'export-upload-all-list'){
		&exportUploadAllList($dbh,\%FORM);
		exit;

	}elsif($FORM{'cmd'} eq 'fma-all-list'){
		&outputFMAAllList($dbh,\%FORM);
		exit;

	}elsif($FORM{'cmd'} eq 'export-fma-all-list'){
		&exportFMAAllList($dbh,\%FORM);
		exit;


	}elsif($FORM{'cmd'} eq 'export-tree-all'){
#		&exportTreeAll($dbh,\%FORM);
#		exit;
		$DATAS->{'sessionID'} = &exportTreeAll_Batch($dbh,\%FORM);
		$DATAS->{'success'} = JSON::XS::true if(defined $DATAS->{'sessionID'});

	}elsif($FORM{'cmd'} eq 'export-tree-all-progress'){
#		&exportTreeAll($dbh,\%FORM);
#		exit;
		eval{
			$DATAS->{'progress'} = &exportTreeAll_Progress($dbh,\%FORM);
			if(defined $DATAS->{'progress'}){
				$DATAS->{'success'} = JSON::XS::true;
				$DATAS->{'sessionID'} = $FORM{'sessionID'};
			}else{
				$DATAS->{'msg'} = qq|???|;
			}
		};
		if($@){
			$DATAS->{'msg'} = $@;
		}

	}elsif($FORM{'cmd'} eq 'export-tree-all-download'){
#		&exportTreeAll($dbh,\%FORM);
#		exit;
		&exportTreeAll_Download($dbh,\%FORM);
		exit;
=cut
	}
}
#print qq|Content-type: text/html; charset=UTF-8\n\n|;
#print &JSON::XS::encode_json($DATAS);
&cgi_lib::common::printContentJSON($DATAS,\%FORM);
#print $LOG __LINE__,":",&JSON::XS::encode_json($DATAS),"\n";

#close($LOG);

exit;

sub getTreePath {
	my $dbh = shift;
	my $FORM = shift;
	my $DATAS = shift;
	my $params;
	eval{$params = &JSON::XS::decode_json($FORM->{'params'});};
	if(defined $params && ref $params eq 'HASH' && defined $params->{cdi_name}){

		my $sql =<<SQL;
select cdi_id,but_cids from view_buildup_tree where but_delcause is null and cdi_pid is null
SQL
		my @W=();
		push(@W,qq|md_id=$params->{'md_id'}|) if(defined $params->{'md_id'});
		push(@W,qq|mv_id=$params->{'mv_id'}|) if(defined $params->{'mv_id'});
		push(@W,qq|mr_id=$params->{'mr_id'}|) if(defined $params->{'mr_id'});
		push(@W,qq|ci_id=$params->{'ci_id'}|) if(defined $params->{'ci_id'});
		push(@W,qq|cb_id=$params->{'cb_id'}|) if(defined $params->{'cb_id'});
		push(@W,qq|bul_id=$params->{bul_id}|) if(defined $params->{bul_id});
		$sql .= " AND ".join(" AND ",@W) if(scalar @W > 0);
#print $LOG __LINE__,":\$sql=[$sql]\n";
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		my $cdi_id;
		my $but_cids;
		my %H;
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_id,   undef);
		$sth->bind_col(++$column_number, \$but_cids,   undef);
		while($sth->fetch){
			next unless(defined $cdi_id && defined $but_cids);
			my $cids;
			eval{$cids = &JSON::XS::decode_json($but_cids);};
			next unless(defined $cids);

			$H{$cdi_id} = undef;
			foreach (@$cids){
				$H{$_} = undef;
			}
		}
		$sth->finish;
		undef $sth;

#		my $ids = join(",",keys(%H));
#print $LOG __LINE__,":\$ids=[$ids]\n";



		$sql =<<SQL;
select
 cdi_id,
 cdi_pid,
 cdi_name,
 cdi_pname
from
 view_buildup_tree
where
SQL

		@W=(qq|cdi_name=?|);
		push(@W,qq|md_id=$params->{'md_id'}|) if(defined $params->{'md_id'});
		push(@W,qq|mv_id=$params->{'mv_id'}|) if(defined $params->{'mv_id'});
		push(@W,qq|mr_id=$params->{'mr_id'}|) if(defined $params->{'mr_id'});
		push(@W,qq|ci_id=$params->{'ci_id'}|) if(defined $params->{'ci_id'});
		push(@W,qq|cb_id=$params->{'cb_id'}|) if(defined $params->{'cb_id'});
		push(@W,qq|bul_id=$params->{bul_id}|) if(defined $params->{bul_id});
		$sql .= join(" AND ",@W);
#print $LOG __LINE__,":\$sql=[$sql]\n";
		$sth = $dbh->prepare($sql) or die $dbh->errstr;

		sub getParentTreeNode {
			my $dbh = shift;
			my $sth = shift;
			my $H = shift;
			my $hash = shift;
			my $nodelist = shift;
			my $p_cdi_name = shift;

			push(@$nodelist,$p_cdi_name) unless(exists $hash->{$p_cdi_name});

#print $LOG __LINE__,":\$p_cdi_name=[$p_cdi_name]\n";
			return if(exists $hash->{$p_cdi_name});
#print $LOG __LINE__,":\$p_cdi_name=[$p_cdi_name]\n";

			my $cdi_id;
			my $cdi_pid;
			my $cdi_name;
			my $cdi_pname;
			my $column_number = 0;
			$sth->execute($p_cdi_name) or die $dbh->errstr;
			$column_number = 0;
			$sth->bind_col(++$column_number, \$cdi_id,   undef);
			$sth->bind_col(++$column_number, \$cdi_pid,   undef);
			$sth->bind_col(++$column_number, \$cdi_name,   undef);
			$sth->bind_col(++$column_number, \$cdi_pname,   undef);
			while($sth->fetch){
				next if(defined $cdi_id && !exists $H->{$cdi_id});
				next if(defined $cdi_pid && !exists $H->{$cdi_pid});
				$hash->{$cdi_name}->{$cdi_pname} = undef if(defined $cdi_pname && $cdi_id != $cdi_pid);
			}
			$sth->finish;

			foreach my $cdi_pname (keys(%{$hash->{$p_cdi_name}})){
				&getParentTreeNode($dbh,$sth,$H,$hash,$nodelist,$cdi_pname);
			}
		}

		my $hash = {};
		my $nodelist = [];
		&getParentTreeNode($dbh,$sth,\%H,$hash,$nodelist,$params->{cdi_name});
		my @path;
		my $cdi_pname = $params->{cdi_name};
		while(defined $cdi_pname && exists $hash->{$cdi_pname}){
			unshift(@path,$cdi_pname);
			$cdi_pname = (keys(%{$hash->{$cdi_pname}}))[0];
		}
		unshift(@path,'root');

		$DATAS->{'treepath'} = '/'.join('/',@path);
		$DATAS->{'nodelist'} = $nodelist;
		$DATAS->{'success'}  = JSON::XS::true;

#print $LOG __LINE__,":",Dumper($hash),"\n";
#print $LOG __LINE__,":",Dumper(\@path),"\n";
	}
}

sub getHistoryMapping {
	my $dbh = shift;
	my $FORM = shift;
	my $DATAS = shift;

	my $sql =<<SQL;
select
 hmap.art_id,
 hmap.ci_id,
 hmap.cb_id,

 hmap.md_id,
 md.md_name_e,

 hmap.mv_id,
 hmap.mr_id,
 mv.mv_name_e,

 hmap.cdi_id,
 cdi.cdi_name,
 cdi.cdi_name_j,
 cdi.cdi_name_e,
 cdi.cdi_name_k,
 cdi.cdi_name_l,

 cm_id,
 cm_use,
 cm_comment,
 cm_delcause,
 cm_openid,

 hist_event,
 he.he_name,

 hist_serial,
 EXTRACT(EPOCH FROM hist_timestamp)

from
 history_concept_art_map as hmap

LEFT JOIN (
  select * from model where md_use and md_delcause is null
) AS md ON
   md.md_id=hmap.md_id

LEFT JOIN (
  select * from model_version where mv_use and mv_delcause is null
) AS mv ON
   mv.md_id=hmap.md_id AND
   mv.mv_id=hmap.mv_id

LEFT JOIN (
  select * from concept_data_info where cdi_delcause is null
) AS cdi ON
   cdi.ci_id=hmap.ci_id AND
   cdi.cdi_id=hmap.cdi_id

LEFT JOIN (
  select * from history_event where he_delcause is null
) AS he ON
   he.he_id=hmap.hist_event

where
 hmap.art_id=?
SQL

	if(exists $FORM->{'sort'} && defined $FORM->{'sort'}){
		my $SORT;
		eval{$SORT=&JSON::XS::decode_json($FORM->{'sort'});};
		if(defined $SORT && ref $SORT eq 'ARRAY'){
			my @S;
			foreach my $s (@$SORT){
				push(@S,qq|$s->{property} $s->{direction}|);
			}
			$sql .= qq|ORDER BY | . join(',',@S) if(scalar @S > 0);
		}
	}

	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute($FORM->{'art_id'}) or die $dbh->errstr;
	$DATAS->{'total'} = $sth->rows();

		my $art_id;
		my $ci_id;
		my $cb_id;

		my $md_id;
		my $md_name_e;

		my $mv_id;
		my $mr_id;
		my $mv_name_e;

		my $cdi_id;
		my $cdi_name;
		my $cdi_name_j;
		my $cdi_name_e;
		my $cdi_name_k;
		my $cdi_name_l;

		my $cm_id;
		my $cm_use;
		my $cm_comment;
		my $cm_delcause;
		my $cm_openid;

		my $hist_event;
		my $he_name;

		my $hist_serial;
		my $hist_timestamp;

		my $column_number = 0;
		$sth->bind_col(++$column_number, \$art_id,   undef);
		$sth->bind_col(++$column_number, \$ci_id,   undef);
		$sth->bind_col(++$column_number, \$cb_id,   undef);

		$sth->bind_col(++$column_number, \$md_id,   undef);
		$sth->bind_col(++$column_number, \$md_name_e,   undef);

		$sth->bind_col(++$column_number, \$mv_id,   undef);
		$sth->bind_col(++$column_number, \$mr_id,   undef);
		$sth->bind_col(++$column_number, \$mv_name_e,   undef);

		$sth->bind_col(++$column_number, \$cdi_id,   undef);
		$sth->bind_col(++$column_number, \$cdi_name,   undef);
		$sth->bind_col(++$column_number, \$cdi_name_j,   undef);
		$sth->bind_col(++$column_number, \$cdi_name_e,   undef);
		$sth->bind_col(++$column_number, \$cdi_name_k,   undef);
		$sth->bind_col(++$column_number, \$cdi_name_l,   undef);

		$sth->bind_col(++$column_number, \$cm_id,   undef);
		$sth->bind_col(++$column_number, \$cm_use,   undef);
		$sth->bind_col(++$column_number, \$cm_comment,   undef);
		$sth->bind_col(++$column_number, \$cm_delcause,   undef);
		$sth->bind_col(++$column_number, \$cm_openid,   undef);

		$sth->bind_col(++$column_number, \$hist_event,   undef);
		$sth->bind_col(++$column_number, \$he_name,   undef);

		$sth->bind_col(++$column_number, \$hist_serial,   undef);
		$sth->bind_col(++$column_number, \$hist_timestamp,   undef);

		while($sth->fetch){
			push(@{$DATAS->{'datas'}},{

				art_id => $art_id,
				ci_id => $ci_id,
				cb_id => $cb_id,

				md_id => $md_id,
				md_name_e => $md_name_e,

				mv_id => $mv_id,
				mr_id => $mr_id,
				mv_name_e => $mv_name_e,

				cdi_id => $cdi_id,
				cdi_name => $cdi_name,
				cdi_name_j => $cdi_name_j,
				cdi_name_e => $cdi_name_e,
				cdi_name_k => $cdi_name_k,
				cdi_name_l => $cdi_name_l,

				cm_id => $cm_id,
				cm_use => $cm_use,
				cm_comment => $cm_comment,
				cm_openid => $cm_openid,

				hist_event => $hist_event,
				he_name => $he_name,

				hist_serial => $hist_serial,
				hist_timestamp => $hist_timestamp,


			});
		}
		$sth->finish;
		undef $sth;

	$DATAS->{'success'}  = JSON::XS::true;

}

#http://192.168.1.237/bp3d-38321/get-info.cgi?model=bp3d&version=4.1&ag_data=obj%2Fbp3d%2F4.1&tree=isa&md_id=1&mv_id=4&mr_id=1&ci_id=1&cb_id=4&bul_id=3&cmd=upload-all-list&title=ALL%20Upload%20Parts%20List
#http://192.168.1.237/bp3d-38321/get-info.cgi?model=bp3d&version=4.1&tree=isa&cmd=upload-all-list&title=ALL%20Upload%20Parts%20List
sub outputUploadAllList {
	my $dbh = shift;
	my $FORM = shift;

	my $bul_id = $FORM->{bul_id};
	my $cb_id = $FORM->{'cb_id'};
	my $ci_id = $FORM->{'ci_id'};
	my $md_id = $FORM->{'md_id'};
	my $mr_id = $FORM->{'mr_id'};
	my $mv_id = $FORM->{'mv_id'};
	my $title = $FORM->{'title'};
	my $load = $FORM->{load};

	if(defined $LOG){
		&cgi_lib::common::message("\$md_id=[$md_id]",$LOG) if(defined $md_id);
		&cgi_lib::common::message("\$mv_id=[$mv_id]",$LOG) if(defined $mv_id);
		&cgi_lib::common::message("\$mr_id=[$mr_id]",$LOG) if(defined $mr_id);
		&cgi_lib::common::message("\$ci_id=[$ci_id]",$LOG) if(defined $ci_id);
		&cgi_lib::common::message("\$cb_id=[$cb_id]",$LOG) if(defined $cb_id);
		&cgi_lib::common::message("\$bul_id=[$bul_id]",$LOG) if(defined $bul_id);
	}

	if(exists $FORM->{'model'} && defined $FORM->{'model'} && !defined $md_id){
		my $sth = $dbh->prepare(qq|select md_id from model where md_abbr=?|) or die $dbh->errstr;
		$sth->execute($FORM->{'model'}) or die $dbh->errstr;
		if($sth->rows()>0){
			my $column_number = 0;
			$sth->bind_col(++$column_number, \$md_id,   undef);
			$sth->fetch;
		}
		$sth->finish;
		undef $sth;
	}
	if(exists $FORM->{'version'} && defined $FORM->{'version'} && defined $md_id && (!defined $mv_id || !defined $mr_id)){
		my $sth = $dbh->prepare(qq|select mv_id,mr_id from model_revision where mv_id=? and mr_version=?|) or die $dbh->errstr;
		$sth->execute($md_id,$FORM->{'version'}) or die $dbh->errstr;
		if($sth->rows()>0){
			my $column_number = 0;
			$sth->bind_col(++$column_number, \$mv_id,   undef);
			$sth->bind_col(++$column_number, \$mr_id,   undef);
			$sth->fetch;
		}
		$sth->finish;
		undef $sth;
	}
	if(exists $FORM->{'tree'} && defined $FORM->{'tree'} && !defined $bul_id){
		my $sth = $dbh->prepare(qq|select bul_id from buildup_logic where bul_abbr=?|) or die $dbh->errstr;
		$sth->execute($FORM->{'tree'}) or die $dbh->errstr;
		if($sth->rows()>0){
			my $column_number = 0;
			$sth->bind_col(++$column_number, \$bul_id,   undef);
			$sth->fetch;
		}
		$sth->finish;
		undef $sth;
	}
	if(defined $md_id && defined $mv_id && defined $mr_id && !defined $ci_id){
		my $sth = $dbh->prepare(qq|select max(ci_id) from representation where md_id=? and mv_id=? and mr_id=?|) or die $dbh->errstr;
		$sth->execute($md_id,$mv_id,$mr_id) or die $dbh->errstr;
		if($sth->rows()>0){
			my $column_number = 0;
			$sth->bind_col(++$column_number, \$ci_id,   undef);
			$sth->fetch;
		}
		$sth->finish;
		undef $sth;
	}

	if(defined $md_id && defined $mv_id && defined $mr_id && defined $ci_id && !defined $cb_id){
		my $sth = $dbh->prepare(qq|select max(cb_id) from representation where md_id=? and mv_id=? and mr_id=? and ci_id=?|) or die $dbh->errstr;
		$sth->execute($md_id,$mv_id,$mr_id,$ci_id) or die $dbh->errstr;
		if($sth->rows()>0){
			my $column_number = 0;
			$sth->bind_col(++$column_number, \$cb_id,   undef);
			$sth->fetch;
		}
		$sth->finish;
		undef $sth;
	}

	if(defined $LOG){
		&cgi_lib::common::message("\$md_id=[$md_id]",$LOG);
		&cgi_lib::common::message("\$mv_id=[$mv_id]",$LOG);
		&cgi_lib::common::message("\$mr_id=[$mr_id]",$LOG);
		&cgi_lib::common::message("\$ci_id=[$ci_id]",$LOG);
		&cgi_lib::common::message("\$cb_id=[$cb_id]",$LOG);
		&cgi_lib::common::message("\$bul_id=[$bul_id]",$LOG);
	}

#		print qq|Content-type: text/html; charset=UTF-8\n\n|;

	unless(defined $load){
		my $cgi = qq|./$cgi_name$cgi_ext|;
		$FORM->{'load'} = 1;
		if(exists $FORM->{'version_name'}){
			$FORM->{'version'} = $FORM->{'version_name'} if(defined $FORM->{'version_name'} && length $FORM->{'version_name'});
			delete $FORM->{'version_name'};
		}
#		my $params = &JSON::XS::encode_json($FORM);
		my $params = &cgi_lib::common::encodeJSON($FORM);
#		print qq|Content-type: text/html; charset=UTF-8\n\n|;
		my $CONTENTS = <<HTML;
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta http-equiv="Content-Style-Type" content="text/css" />
<meta http-equiv="Content-Script-Type" content="text/javascript" />
<meta http-equiv="X-UA-Compatible" content="chrome=1">

<link rel="stylesheet" href="js/extjs-4.1.1/resources/css/ext-all.css" type="text/css" media="all">

<title>$title</title>
<style>
* {
	font-size:12px;
	font-family: tahoma, arial, verdana, sans-serif;
}
body {
	margin: 0;
	padding: 0;
}
table {
	table-layout: fixed;
	border-collapse: collapse;
	width: 100%;
	margin-bottom: 2px;
}
tr>td {
	vertical-align: top;
}
tr.head>td {
	text-align: center;
	font-weight: bold;
	background-color: #cccccc;
}
td {
	padding: 2px;
}
tr:nth-child(odd) {
	background-color: #f0f0f0;
}
.row_number {
	width: 44px;
	text-align: right;
	background-color: #cccccc;
	-moz-user-select:-moz-none;
	-khtml-user-select:none;
	-webkit-user-select:none;
	display: none;
}
.art_id {
	width: 70px;
	max-width: 70px;
}
.rep_id {
	width: 70px;
	max-width: 70px;
}
.cdi_name {
	width: 70px;
	max-width: 70px;
}

</style>
</head>
<body>
<script type="text/javascript" src="js/jquery.js"></script>
<script type="text/javascript" src="js/extjs-4.1.1/ext-all.js"></script>
<script type="text/javascript"><!--
Ext.BLANK_IMAGE_URL = "js/extjs-4.1.1/resources/themes/images/default/tree/s.gif";
Ext.Loader.setConfig({enabled: true});
Ext.require([
	'*'
]);
Ext.onReady(function() {
	Ext.getBody().load({
		ajaxOptions: {
			timeout: 300000
		},
		url:'$cgi',
		params:$params,
		loadMask: 'Making table. It may take a while ...',
		success:function(self,response,options){
			if(window.console && window.console.log){
				console.log("success()");
				console.log(this);
				console.log(response);
				console.log(options);
			}
		},
		failure:function(self,response,options){
			if(window.console && window.console.log){
				console.log("failure()");
				console.log(this);
				console.log(response);
				console.log(options);
			}
		}
	});
});
</script>
</body>
</html>
HTML
		$CONTENTS = &cgi_lib::common::html_compress($CONTENTS);
		&cgi_lib::common::message($CONTENTS,$LOG) if(defined $LOG);
		&cgi_lib::common::printContent($CONTENTS);
		return;
	}

#		print qq|Content-type: text/html; charset=UTF-8\n\n|;

	my $sql=<<SQL;
select
 arti.art_id,
 arti.art_name,
 arti.art_ext,
 COALESCE(artg.artg_id,arti.artg_id),
 COALESCE(artg.artg_name,arti.artg_name),
 cdi_name,
 cdi_name_e,
 cdi_syn_e,
-- rep.rep_id,
 repa.rep_id
from
 (
   select
     art_id,
     art_name,
     art_ext,
     art_timestamp,
     artg_name,
     arti.artg_id
   from
     art_file_info as arti

   left join (
      select * from art_group
    ) as artg on
       artg.artg_id=arti.artg_id

   where
    atrg_use AND
    artg_delcause is null AND
    arti.art_delcause is null



--    AND arti.artg_id not in (1,2)
 ) as arti

left join (
   select art_id,art_serial from art_file
 ) as art on
    art.art_id=arti.art_id

--history_art_fileから最新のhist_serialを取得
left join (
   select art_id,max(hist_serial) as art_hist_serial from history_art_file group by art_id
 ) as hart2 on
    hart2.art_id=arti.art_id

left join (
   select
    *
   from
    concept_art_map
   where
    (md_id,mv_id,mr_id,art_id) in (
     select
      md_id,mv_id,max(mr_id) as mr_id,art_id
     from
      concept_art_map
     where
      md_id=$md_id and mv_id=$mv_id and mr_id<=$mr_id
     group by
      md_id,mv_id,art_id
   ) and
--    cm_use and -- バージョンに関係なく対応付けしたFMAIDを表示させる場合は、cm_useは参照しない
    cm_delcause is null
 ) as map on
    map.art_id=arti.art_id

left join (
   select * from concept_data_info
 ) as cdi on
    cdi.ci_id=map.ci_id and
    cdi.cdi_id=map.cdi_id


left join (
   select
    *
   from
    representation
   where
    (md_id,mv_id,mr_id,bul_id,cdi_id) in (
     select
      md_id,mv_id,max(mr_id) as mr_id,bul_id,cdi_id
     from
      representation
     where
      md_id=$md_id and mv_id=$mv_id and mr_id<=$mr_id and bul_id=$bul_id
     group by
      md_id,mv_id,bul_id,cdi_id
   )
 ) as rep on
    rep.md_id=map.md_id and
    rep.mv_id=map.mv_id and
    rep.mr_id=map.mr_id and
    rep.cdi_id=map.cdi_id

--実際に使用されているかを確認
left join (
  select
   *
  from
   representation_art
) as repa on
  repa.rep_id = rep.rep_id and
  repa.art_id = arti.art_id

left join (
   select * from history_art_file_info
 ) as harti on
    repa.art_id          = harti.art_id and
    repa.art_hist_serial = harti.hist_serial

--グループ情報
left join (
   select * from art_group
 ) as artg on
    artg.artg_id=harti.artg_id

left join (
   select * from model
 ) as md on
    md.md_id=rep.md_id

left join (
   select * from model_version
 ) as mv on
    mv.md_id=rep.md_id and
    mv.mv_id=rep.mv_id

left join (
   select * from buildup_logic
 ) as bul on
    bul.bul_id=rep.bul_id

order by
   regexp_matches(arti.art_id,'^[A-Za-z]+'),
   array_to_string(regexp_matches(arti.art_id,'[0-9]+'),'')::integer,
   arti.art_id
SQL

	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	my $art_id;
	my $art_name;
	my $art_ext;
	my $artg_id;
	my $artg_name;
	my $cdi_name;
	my $cdi_name_e;
	my $cdi_syn_e;
	my $rep_id;
	my $cm_id;

	my $column_number = 0;
	$sth->bind_col(++$column_number, \$art_id,   undef);
	$sth->bind_col(++$column_number, \$art_name,   undef);
	$sth->bind_col(++$column_number, \$art_ext,   undef);
	$sth->bind_col(++$column_number, \$artg_id,   undef);
	$sth->bind_col(++$column_number, \$artg_name,   undef);
	$sth->bind_col(++$column_number, \$cdi_name,   undef);
	$sth->bind_col(++$column_number, \$cdi_name_e,   undef);
	$sth->bind_col(++$column_number, \$cdi_syn_e,   undef);
	$sth->bind_col(++$column_number, \$rep_id,   undef);


#	print <<HTML;
#<body>
#HTML



	sub print_upload_all_list_head {
		return <<HTML;
<table border=1>
<thead>
<tr class="head">
<td class="row_number">#</td>
<td class="art_id">FJID</td>
<td class="rep_id">BPID</td>
<td class="cdi_name">FMA ID</td>
<td class="cdi_name_e">FMA Name</td>
<td class="cdi_syn_e">FMA Synonym</td>
<td class="art_name">obj file</td>
<td class="artg_name">obj group</td>
</tr>
</thead>
<tbody>
HTML
	}

	sub print_upload_all_list_tail {
		return <<HTML;
</tbody>
</table>
HTML
	}

	my $rows = 0;
	my $CONTENTS = '';
	while($sth->fetch){
		next unless(defined $art_id);

		$cdi_syn_e =~ s/(;)/$1<br>/g if(defined $cdi_syn_e);

		$rows++;

		$CONTENTS .= &print_upload_all_list_tail() if($rows%50==1 && $rows>1);
		$CONTENTS .= &print_upload_all_list_head() if($rows%50==1);

		$art_id = '' unless(defined $art_id);
		$rep_id = '' unless(defined $rep_id);
		$cdi_name = '' unless(defined $cdi_name);
		$cdi_name_e = '' unless(defined $cdi_name_e);
		$cdi_syn_e = '' unless(defined $cdi_syn_e);
		$art_name = '' unless(defined $art_name);
		$art_ext = '' unless(defined $art_ext);
		$artg_name = '' unless(defined $artg_name);

		$art_id = &cgi_lib::common::encodeUTF8($art_id);
		$rep_id = &cgi_lib::common::encodeUTF8($rep_id);
		$cdi_name = &cgi_lib::common::encodeUTF8($cdi_name);
		$cdi_name_e = &cgi_lib::common::encodeUTF8($cdi_name_e);
		$cdi_syn_e = &cgi_lib::common::encodeUTF8($cdi_syn_e);
		$art_name = &cgi_lib::common::encodeUTF8($art_name);
		$art_ext = &cgi_lib::common::encodeUTF8($art_ext);
		$artg_name = &cgi_lib::common::encodeUTF8($artg_name);

		$CONTENTS .= <<HTML;
<tr>
<td class="row_number">$rows</td>
<td class="art_id">$art_id</td>
<td class="rep_id">$rep_id</td>
<td class="cdi_name">$cdi_name</td>
<td class="cdi_name_e">$cdi_name_e</td>
<td class="cdi_syn_e">$cdi_syn_e</td>
<td class="art_name">$art_name$art_ext</td>
<td class="artg_name">$artg_name</td>
</tr>
HTML
#		&utf8::encode($html) if(&utf8::is_utf8($html));
#		print $html;
	}

	$CONTENTS .= &print_upload_all_list_tail();
#	$CONTENTS = &cgi_lib::common::html_compress(&cgi_lib::common::decodeUTF8($CONTENTS));
	$CONTENTS = &cgi_lib::common::html_compress($CONTENTS);
	&cgi_lib::common::message($CONTENTS,$LOG) if(defined $LOG);
#	&cgi_lib::common::printContent(&cgi_lib::common::encodeUTF8($CONTENTS));
	&cgi_lib::common::printContent($CONTENTS);

#	print <<HTML;
#</body>
#</html>
#HTML

	$sth->finish;
	undef $sth;
}

sub exportUploadAllList {
	my $dbh = shift;
	my $FORM = shift;

use Encode;
use Spreadsheet::WriteExcel;
use Excel::Writer::XLSX;

use Archive::Zip;
use IO::File;

	my $bul_id = $FORM->{bul_id};
	my $ci_id = $FORM->{'ci_id'};
	my $cb_id = $FORM->{'cb_id'};
	my $md_id = $FORM->{'md_id'};
	my $mv_id = $FORM->{'mv_id'};
	my $mr_id = $FORM->{'mr_id'};

	my $title = $FORM->{'title'} || 'All Upload Parts List';
#	my $format = $FORM->{'format'} || 'xls';
	my $format = $FORM->{'format'} || 'txt';

	my $out_path = qq|$FindBin::Bin/download|;
	my ($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime();
	my @weekly = ('Sun', 'Mon', 'Tue', 'Wed', 'Thr', 'Fri', 'Sut');
	my $file = sprintf("%04d%02d%02d%02d%02d%02d", $year+1900,$month+1,$mday,$hour,$min,$sec);
	my $file_basename = qq|$file.$format|;
	my $file_base_ext = qq|$title.$format|;
	my $file_name = &catdir($out_path,$file_basename);
	my $zip_file = qq|$file.zip|;
	my $file_path = &catdir($out_path,$zip_file);

	my $LF = "\n";
	my $CODE = "utf8";
	if($ENV{HTTP_USER_AGENT}=~/Windows/){
		$LF = "\r\n";
		$CODE = "shiftjis";
	}elsif($ENV{HTTP_USER_AGENT}=~/Macintosh/){
		$LF = "\r";
		$CODE = "shiftjis";
	}

	my $sql=<<SQL;
select
 arti.art_id,
 arti.art_name,
 arti.art_ext,
 artg_name,
 cdi_name,
 cdi_name_e,
 cdi_syn_e,
 repa.rep_id,
-- EXTRACT(EPOCH FROM arti.art_timestamp),
 to_char(arti.art_timestamp,'YYYY/MM/DD HH24:MI:SS'),
 arta.art_comment,
 arta.art_category,
 arta.art_judge,
 arta.art_class,

 md.md_name_e,
 mv.mv_name_e,
 bul.bul_name_e,
 map.cm_use

from
 (
   select
     art_id,
     art_name,
     art_ext,
     art_timestamp,
     artg_name
   from
     art_file_info as arti

   left join (
      select * from art_group
    ) as artg on
       artg.artg_id=arti.artg_id

   where
    atrg_use AND
    artg_delcause is null AND
    arti.art_delcause is null AND
    arti.artg_id not in (1,2)
 ) as arti


left join (
   select art_id,art_serial from art_file
 ) as art on
    art.art_id=arti.art_id

left join (
   select art_id,art_comment,art_category,art_judge,art_class from art_annotation
 ) as arta on
    arta.art_id=arti.art_id

left join (
   select
    *
   from
    concept_art_map
   where
    cm_delcause is null
    and ci_id=$ci_id and cb_id=$cb_id and md_id=$md_id and mv_id=$mv_id
 ) as map on
    map.art_id=arti.art_id

left join (
   select * from concept_data_info
 ) as cdi on
    cdi.ci_id=map.ci_id and
    cdi.cdi_id=map.cdi_id


left join (
   select
    *
   from
    representation
   where
    (ci_id,cb_id,md_id,mv_id,mr_id,bul_id,cdi_id) in (
     select
      ci_id,cb_id,md_id,mv_id,max(mr_id) as mr_id,bul_id,cdi_id
     from
      representation
     where
      ci_id=$ci_id and cb_id=$cb_id and md_id=$md_id and mv_id=$mv_id and bul_id=$bul_id
     group by
      ci_id,cb_id,md_id,mv_id,bul_id,cdi_id
   )
 ) as rep on
    rep.ci_id=map.ci_id and
    rep.cb_id=map.cb_id and
    rep.md_id=map.md_id and
    rep.mv_id=map.mv_id and
    rep.cdi_id=map.cdi_id

--実際に使用されているかを確認
left join (
   select
    rep_id,art_id
   from
    representation_art
   group by
    rep_id,art_id
 ) as repa on
    repa.rep_id = rep.rep_id and
    repa.art_id = arti.art_id

left join (
   select * from model
 ) as md on
    md.md_id=rep.md_id

left join (
   select * from model_version
 ) as mv on
    mv.md_id=rep.md_id and
    mv.mv_id=rep.mv_id

left join (
   select * from buildup_logic
 ) as bul on
    bul.bul_id=rep.bul_id

order by
 artg_name,
 art.art_serial,
 art.art_id
SQL

	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	my $art_id;
	my $art_name;
	my $art_ext;
	my $artg_id;
	my $artg_name;
	my $cdi_name;
	my $cdi_name_e;
	my $cdi_syn_e;
	my $rep_id;

	my $art_timestamp_epoch;
	my $art_timestamp;
	my $art_comment;
	my $art_category;
	my $art_judge;
	my $art_class;
	my $md_name_e;
	my $mv_name_e;
	my $bul_name_e;

	my $cm_use;

	my $column_number = 0;
	$sth->bind_col(++$column_number, \$art_id,   undef);
	$sth->bind_col(++$column_number, \$art_name,   undef);
	$sth->bind_col(++$column_number, \$art_ext,   undef);
#	$sth->bind_col(++$column_number, \$artg_id,   undef);
	$sth->bind_col(++$column_number, \$artg_name,   undef);
	$sth->bind_col(++$column_number, \$cdi_name,   undef);
	$sth->bind_col(++$column_number, \$cdi_name_e,   undef);
	$sth->bind_col(++$column_number, \$cdi_syn_e,   undef);
	$sth->bind_col(++$column_number, \$rep_id,   undef);

#	$sth->bind_col(++$column_number, \$art_timestamp_epoch,   undef);
	$sth->bind_col(++$column_number, \$art_timestamp,   undef);
	$sth->bind_col(++$column_number, \$art_comment,   undef);
	$sth->bind_col(++$column_number, \$art_category,   undef);
	$sth->bind_col(++$column_number, \$art_judge,   undef);
	$sth->bind_col(++$column_number, \$art_class,   undef);
	$sth->bind_col(++$column_number, \$md_name_e,   undef);
	$sth->bind_col(++$column_number, \$mv_name_e,   undef);
	$sth->bind_col(++$column_number, \$bul_name_e,   undef);

	$sth->bind_col(++$column_number, \$cm_use,   undef);


#	my $header = qq|#FJID	BPID	FMA_ID	FMA_Name	FMA_Synonym	OBJ_Filename	OBJ_Group	OBJ_Timestamp	Comment	Category	Judge	Class	Model	Version	Tree|;
#	my $header = qq|#FJID	BPID	Use_Map	FMA_ID	FMA_Name	FMA_Synonym	OBJ_Filename	OBJ_Group	OBJ_Timestamp	Comment	Category	Judge	Class|;
#	&utf8::decode($header) unless(&utf8::is_utf8($header));
	my $header = &cgi_lib::common::decodeUTF8(qq|#FJID	BPID	Use_Map	FMA_ID	FMA_Name	FMA_Synonym	OBJ_Filename	OBJ_Group	OBJ_Timestamp	Comment	Category	Judge	Class|);

	($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime();
	my $timestamp = sprintf("%04d/%02d/%02d/ %02d:%02d:%02d", $year+1900,$month+1,$mday,$hour,$min,$sec);

	if($format eq 'xls' || $format eq 'xlsx'){
		my $workbook;
		if($format eq 'xls'){
			$workbook = Spreadsheet::WriteExcel->new($file_name);
		}elsif($format eq 'xlsx'){
			$workbook = Excel::Writer::XLSX->new($file_name);
		}
		my $uni_format = $workbook->add_format(
#			font => 'Arial Unicode MS',
			size => 10
		);
		my $worksheet_name = &cgi_lib::common::decodeUTF8($title);
#		&utf8::decode($worksheet_name) unless(&utf8::is_utf8($worksheet_name));
		my $worksheet = $workbook->add_worksheet($worksheet_name);

		my $pg=1;
		my $y = 0;

		my $x = 0;


		while($sth->fetch){
			next unless(defined $art_id);

			if($y==0){
#				&utf8::encode($timestamp) if(&utf8::is_utf8($timestamp));
				my $s = &cgi_lib::common::decodeUTF8('#Export Date:'.&cgi_lib::common::encodeUTF8($timestamp));
#				&utf8::decode($s) unless(&utf8::is_utf8($s));
				$worksheet->write($y++, 0, $s,     $uni_format );

#				&utf8::encode($md_name_e) if(&utf8::is_utf8($md_name_e));
				$s = &cgi_lib::common::decodeUTF8('#Model:'.&cgi_lib::common::encodeUTF8($md_name_e));
#				&utf8::decode($s) unless(&utf8::is_utf8($s));
				$worksheet->write($y++, 0, $s,     $uni_format );

#				&utf8::encode($mv_name_e) if(&utf8::is_utf8($mv_name_e));
				$s = &cgi_lib::common::decodeUTF8('#Version:'.&cgi_lib::common::encodeUTF8($mv_name_e));
#				&utf8::decode($s) unless(&utf8::is_utf8($s));
				$worksheet->write($y++, 0, $s,     $uni_format );

#				&utf8::encode($bul_name_e) if(&utf8::is_utf8($bul_name_e));
				$s = &cgi_lib::common::decodeUTF8('#Tree:'.&cgi_lib::common::encodeUTF8($bul_name_e));
#				&utf8::decode($s) unless(&utf8::is_utf8($s));
				$worksheet->write($y++, 0, $s,     $uni_format );

				$x = 0;
				foreach my $h (split(/\t/,$header)){
					$worksheet->write( $y, $x++, $h, $uni_format );
				}
				$y++;
			}

			$x = 0;

			$worksheet->write( $y, $x++, $art_id,     $uni_format );
			$worksheet->write( $y, $x++, $rep_id,     $uni_format );
			$worksheet->write( $y, $x++, $cm_use,   $uni_format );

			$worksheet->write( $y, $x++, $cdi_name,   $uni_format );
			$worksheet->write( $y, $x++, $cdi_name_e, $uni_format );
			$worksheet->write( $y, $x++, $cdi_syn_e,  $uni_format );
			$worksheet->write( $y, $x++, qq|$art_name$art_ext|, $uni_format );
			$worksheet->write( $y, $x++, $artg_name,  $uni_format );

			$worksheet->write( $y, $x++, $art_timestamp, $uni_format );
			$worksheet->write( $y, $x++, $art_comment,   $uni_format );
			$worksheet->write( $y, $x++, $art_category,  $uni_format );
			$worksheet->write( $y, $x++, $art_judge,     $uni_format );
			$worksheet->write( $y, $x++, $art_class,     $uni_format );
#			$worksheet->write( $y, $x++, $md_name_e,     $uni_format );
#			$worksheet->write( $y, $x++, $mv_name_e,     $uni_format );
#			$worksheet->write( $y, $x++, $bul_name_e,    $uni_format );

			$y++;
			next if($y<65536);

			$pg++;
			my $worksheet_name = &cgi_lib::common::decodeUTF8(qq|$title ($pg)|);
#			&utf8::decode($worksheet_name) unless(&utf8::is_utf8($worksheet_name));
			$worksheet = $workbook->add_worksheet($worksheet_name);
			$y = 0;

		}
		$workbook->close();

	}else{
		open(OUT,"> $file_name");

		my $y = 0;

		while($sth->fetch){
			next unless(defined $art_id);

			if($y==0){
#				&utf8::encode($timestamp) if(&utf8::is_utf8($timestamp));
				my $s = &cgi_lib::common::decodeUTF8('#Export Date:'.&cgi_lib::common::encodeUTF8($timestamp));
#				&utf8::decode($s) unless(&utf8::is_utf8($s));
				print OUT &Encode::encode($CODE,$s),$LF;
				$y++;

#				&utf8::encode($md_name_e) if(&utf8::is_utf8($md_name_e));
				$s = &cgi_lib::common::decodeUTF8('#Model:'.&cgi_lib::common::encodeUTF8($md_name_e));
#				&utf8::decode($s) unless(&utf8::is_utf8($s));
				print OUT &Encode::encode($CODE,$s),$LF;
				$y++;

#				&utf8::encode($mv_name_e) if(&utf8::is_utf8($mv_name_e));
				$s = &cgi_lib::common::decodeUTF8('#Version:'.&cgi_lib::common::encodeUTF8($mv_name_e));
#				&utf8::decode($s) unless(&utf8::is_utf8($s));
				print OUT &Encode::encode($CODE,$s),$LF;
				$y++;

#				&utf8::encode($bul_name_e) if(&utf8::is_utf8($bul_name_e));
				$s = &cgi_lib::common::decodeUTF8('#Tree:'.&cgi_lib::common::encodeUTF8($bul_name_e));
#				&utf8::decode($s) unless(&utf8::is_utf8($s));
				print OUT &Encode::encode($CODE,$s),$LF;
				$y++;

				print OUT &Encode::encode($CODE,$header),$LF;
				$y++;
			}

			my @t;
			push(@t,$art_id);
			push(@t,$rep_id);
			push(@t,$cm_use);
			push(@t,$cdi_name);
			push(@t,$cdi_name_e);
			push(@t,$cdi_syn_e);
			push(@t,qq|$art_name$art_ext|);
			push(@t,$artg_name);

			push(@t,$art_timestamp);
			push(@t,$art_comment);
			push(@t,$art_category);
			push(@t,$art_judge);
			push(@t,$art_class);
#			push(@t,$md_name_e);
#			push(@t,$mv_name_e);
#			push(@t,$bul_name_e);

			my $o = &cgi_lib::common::decodeUTF8(join("\t",@t));
#			utf8::decode($o) unless(utf8::is_utf8($o));
			print OUT &Encode::encode($CODE,$o),$LF;

			$y++;
		}

		close(OUT);
	}

	$sth->finish;
	undef $sth;

	my($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,$atime,$mtime,$ctime,$blksize,$blocks) = stat($file_name);

#	&utf8::encode($zip_file) if(&utf8::is_utf8($zip_file));
#	&utf8::encode($file_name) if(&utf8::is_utf8($file_name));
	$zip_file = &cgi_lib::common::encodeUTF8($zip_file);
	$file_name = &cgi_lib::common::encodeUTF8($file_name);

#	&utf8::decode($file_base_ext) unless(&utf8::is_utf8($file_base_ext));
	$file_base_ext = &cgi_lib::common::decodeUTF8($file_base_ext);
	my $encoded_filename = &Encode::encode_utf8($file_base_ext);
	$encoded_filename = &Encode::encode($CODE, $file_base_ext);

	my $zip = Archive::Zip->new();
	my $zip_mem = $zip->addFile($file_name,$encoded_filename);

	my $stdout = IO::File->new->fdopen(fileno(STDOUT), "w") || croak($!);
	$stdout->printflush("Content-Type: application/zip\n");
	$stdout->printflush("Content-Disposition: filename=$zip_file\n");
	$stdout->printflush("Last-Modified: ".&HTTP::Date::time2str($mtime)."\n");
#	$stdout->printflush("Accept-Ranges: bytes\n");
#	$stdout->printflush("Content-Length: $size\n");
	$stdout->printflush("Pragma: no-cache\n\n");
	$zip->writeToFileHandle($stdout, 0);
	$stdout->close;


	unlink $file_name if(-e $file_name);
	unlink $file_path if(-e $file_path);
}

sub outputFMAAllList {
	my $dbh = shift;
	my $FORM = shift;

	my $md_id = $FORM->{'md_id'};
	my $mv_id = $FORM->{'mv_id'};
	my $mr_id = $FORM->{'mr_id'};
	my $ci_id = $FORM->{'ci_id'};
	my $cb_id = $FORM->{'cb_id'};
	my $title = $FORM->{'title'};

	print qq|Content-type: text/html; charset=UTF-8\n\n|;
	print <<HTML;
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta http-equiv="Content-Style-Type" content="text/css" />
<meta http-equiv="Content-Script-Type" content="text/javascript" />
<meta http-equiv="X-UA-Compatible" content="chrome=1">
<title>$title</title>
<style>
* {
	font-size:12px;
	font-family: tahoma, arial, verdana, sans-serif;
}
body {
	margin: 0;
	padding: 0;
}
table {
	table-layout: fixed;
	border-collapse: collapse;
	width: 100%;
	margin-bottom: 2px;
}

tbody>tr>td {
	visibility: visible;
}

tr>td {
	vertical-align: top;
}
tr.head>td {
	text-align: center;
	font-weight: bold;
	background-color: #cccccc;
	-moz-user-select:-moz-none;
	-khtml-user-select:none;
	-webkit-user-select:none;
}
td {
	padding: 2px;
}
tr:nth-child(odd) {
	background-color: #f0f0f0;
}
.row_number {
	width: 44px;
	text-align: right;
	background-color: #cccccc;
	-moz-user-select:-moz-none;
	-khtml-user-select:none;
	-webkit-user-select:none;
	display: none;
}
.cdi_name {
	width: 70px;
	max-width: 70px;
}
.cdi_name_e {
	max-width: 700px;
}
.cdi_syn_e {
	max-width: 654px;
}
.cdi_def_e {
	display: none;
}
.buildup_logic {
	width: 35px;
	max-width: 35px;
	text-align: center;
}
</style>
</head>
HTML

	my $sql=<<SQL;
--select
-- cdi_id,
-- cdi_name,
-- cdi_name_j,
-- cdi_name_e,
-- cdi_name_k,
-- cdi_name_l,
-- cdi_syn_j,
-- cdi_syn_e,
-- cdi_def_j,
-- cdi_def_e,
-- cdi_taid
--from
-- concept_data_info
--where
-- ci_id=$ci_id AND
-- cdi_delcause is null
--order by
-- to_number(substring(cdi_name from 4),'999999')

select
 cdi.cdi_id,
 cdi.cdi_name,
 cdi.cdi_name_j,
 cdi.cdi_name_e,
 cdi.cdi_name_k,
 cdi.cdi_name_l,
 cdi.cdi_syn_j,
 cdi.cdi_syn_e,
 cdi.cdi_def_j,
 cdi.cdi_def_e,
 cdi.cdi_taid,
 but2.c,
 but2.m
from
 (
   select distinct md_id,mv_id,mr_id,ci_id,cb_id,cdi_id from buildup_tree where md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND ci_id=$ci_id AND cb_id=$cb_id
 ) as but

left join (
 select * from concept_data_info
) as cdi on
   but.ci_id=cdi.ci_id AND
   but.cdi_id=cdi.cdi_id

left join (
  select md_id,mv_id,mr_id,ci_id,cb_id,cdi_id,count(bul_id) as c,max(bul_id) as m from (
    select md_id,mv_id,mr_id,ci_id,cb_id,cdi_id,bul_id from buildup_tree where ci_id=$ci_id AND cb_id=$cb_id group by md_id,mv_id,mr_id,ci_id,cb_id,cdi_id,bul_id
  ) as a
  group by a.md_id,a.mv_id,a.mr_id,a.ci_id,a.cb_id,a.cdi_id

) as but2 on
   but.md_id=but2.md_id AND
   but.mv_id=but2.mv_id AND
   but.mr_id=but2.mr_id AND
   but.ci_id=but2.ci_id AND
   but.cb_id=but2.cb_id AND
   but.cdi_id=but2.cdi_id

where
 cdi_delcause is null
order by
 to_number(substring(cdi_name from 4),'999999')

SQL

	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;

	my $cdi_id;
	my $cdi_name;
	my $cdi_name_j;
	my $cdi_name_e;
	my $cdi_name_k;
	my $cdi_name_l;
	my $cdi_syn_j;
	my $cdi_syn_e;
	my $cdi_def_j;
	my $cdi_def_e;
	my $cdi_taid;
	my $bul_id_cnt;
	my $bul_id_max;

	my $column_number = 0;
	$sth->bind_col(++$column_number, \$cdi_id,   undef);
	$sth->bind_col(++$column_number, \$cdi_name,   undef);
	$sth->bind_col(++$column_number, \$cdi_name_j,   undef);
	$sth->bind_col(++$column_number, \$cdi_name_e,   undef);
	$sth->bind_col(++$column_number, \$cdi_name_k,   undef);
	$sth->bind_col(++$column_number, \$cdi_name_l,   undef);
	$sth->bind_col(++$column_number, \$cdi_syn_j,   undef);
	$sth->bind_col(++$column_number, \$cdi_syn_e,   undef);
	$sth->bind_col(++$column_number, \$cdi_def_j,   undef);
	$sth->bind_col(++$column_number, \$cdi_def_e,   undef);
	$sth->bind_col(++$column_number, \$cdi_taid,   undef);
	$sth->bind_col(++$column_number, \$bul_id_cnt,   undef);
	$sth->bind_col(++$column_number, \$bul_id_max,   undef);

	print <<HTML;
<body>
HTML

	sub print_table_head {
		print <<HTML;
<table border=1>
<thead>
<tr class="head">
<td class="row_number">#</td>
<td class="cdi_name">ID</td>
<td class="cdi_name_e">Name</td>
<td class="cdi_syn_e">Synonym</td>
<td class="cdi_def_e">Definition</td>
<td class="buildup_logic">Tree</td>
</tr>
</thead>
<tbody>
HTML
	}

	sub print_table_tail {
		print <<HTML;
</tbody>
</table>
HTML
	}

	my $rows = 0;

	while($sth->fetch){

		next unless(defined $cdi_name);

		$cdi_syn_e =~ s/(;)/$1<br>/g if(defined $cdi_syn_e);

		my $buildup_logic;
		if($bul_id_cnt==2){
			$buildup_logic = 'both';
		}elsif($bul_id_max==3){
			$buildup_logic = 'is_a';
		}elsif($bul_id_max==4){
			$buildup_logic = 'part_of';
		}

		$rows++;

		&print_table_tail() if($rows%50==1 && $rows>1);
		&print_table_head() if($rows%50==1);

		my $html =<<HTML;
<tr>
<td class="row_number">$rows</td>
<td class="cdi_name">$cdi_name</td>
<td class="cdi_name_e">$cdi_name_e</td>
<td class="cdi_syn_e">$cdi_syn_e</td>
<td class="cdi_def_e">$cdi_def_e</td>
<td class="buildup_logic">$buildup_logic</td>
</tr>
HTML
#		&utf8::encode($html) if(&utf8::is_utf8($html));
		print &cgi_lib::common::encodeUTF8($html);
	}

	&print_table_tail();

	print <<HTML;
</body>
</html>
HTML

	$sth->finish;
	undef $sth;
}


sub exportFMAAllList {
	my $dbh = shift;
	my $FORM = shift;

use Encode;
use Spreadsheet::WriteExcel;
use Excel::Writer::XLSX;

use Archive::Zip;
use IO::File;

	my $md_id = $FORM->{'md_id'};
	my $mv_id = $FORM->{'mv_id'};
	my $mr_id = $FORM->{'mr_id'};
	my $ci_id = $FORM->{'ci_id'};
	my $cb_id = $FORM->{'cb_id'};
	my $title = $FORM->{'title'} || 'All FMA List';
#	my $format = $FORM->{'format'} || 'xls';
	my $format = $FORM->{'format'} || 'txt';

	my $out_path = qq|$FindBin::Bin/download|;
	my ($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime();
	my @weekly = ('Sun', 'Mon', 'Tue', 'Wed', 'Thr', 'Fri', 'Sut');
	my $file = sprintf("%04d%02d%02d%02d%02d%02d", $year+1900,$month+1,$mday,$hour,$min,$sec);
	my $file_basename = qq|$file.$format|;
	my $file_base_ext = qq|$title.$format|;
	my $file_name = &catdir($out_path,$file_basename);
	my $zip_file = qq|$file.zip|;
	my $file_path = &catdir($out_path,$zip_file);

	my $LF = "\n";
	my $CODE = "utf8";
	if($ENV{HTTP_USER_AGENT}=~/Windows/){
		$LF = "\r\n";
		$CODE = "shiftjis";
	}elsif($ENV{HTTP_USER_AGENT}=~/Macintosh/){
		$LF = "\r";
		$CODE = "shiftjis";
	}

	my $sql=<<SQL;
select
 cdi.cdi_id,
 cdi.cdi_name,
 cdi.cdi_name_j,
 cdi.cdi_name_e,
 cdi.cdi_name_k,
 cdi.cdi_name_l,
 cdi.cdi_syn_j,
 cdi.cdi_syn_e,
 cdi.cdi_def_j,
 cdi.cdi_def_e,
 cdi.cdi_taid,
 but2.c,
 but2.m
from
 (
   select distinct ci_id,cb_id,cdi_id from buildup_tree where md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND ci_id=$ci_id AND cb_id=$cb_id
 ) as but

left join (
 select * from concept_data_info
) as cdi on
   but.ci_id=cdi.ci_id AND
   but.cdi_id=cdi.cdi_id

left join (
  select md_id,mv_id,mr_id,ci_id,cb_id,cdi_id,count(bul_id) as c,max(bul_id) as m from (
    select md_id,mv_id,mr_id,ci_id,cb_id,cdi_id,bul_id from buildup_tree where md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND ci_id=$ci_id AND cb_id=$cb_id group by md_id,mv_id,mr_id,ci_id,cb_id,cdi_id,bul_id
  ) as a
  group by a.md_id,a.mv_id,a.mr_id,a.ci_id,a.cb_id,a.cdi_id

) as but2 on
   but.md_id=but2.md_id AND
   but.mv_id=but2.mv_id AND
   but.mr_id=but2.mr_id AND
   but.ci_id=but2.ci_id AND
   but.cb_id=but2.cb_id AND
   but.cdi_id=but2.cdi_id

where
 cdi_delcause is null
order by
 to_number(substring(cdi_name from 4),'999999')

SQL

	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;

	my $cdi_id;
	my $cdi_name;
	my $cdi_name_j;
	my $cdi_name_e;
	my $cdi_name_k;
	my $cdi_name_l;
	my $cdi_syn_j;
	my $cdi_syn_e;
	my $cdi_def_j;
	my $cdi_def_e;
	my $cdi_taid;
	my $bul_id_cnt;
	my $bul_id_max;

	my $column_number = 0;
	$sth->bind_col(++$column_number, \$cdi_id,   undef);
	$sth->bind_col(++$column_number, \$cdi_name,   undef);
	$sth->bind_col(++$column_number, \$cdi_name_j,   undef);
	$sth->bind_col(++$column_number, \$cdi_name_e,   undef);
	$sth->bind_col(++$column_number, \$cdi_name_k,   undef);
	$sth->bind_col(++$column_number, \$cdi_name_l,   undef);
	$sth->bind_col(++$column_number, \$cdi_syn_j,   undef);
	$sth->bind_col(++$column_number, \$cdi_syn_e,   undef);
	$sth->bind_col(++$column_number, \$cdi_def_j,   undef);
	$sth->bind_col(++$column_number, \$cdi_def_e,   undef);
	$sth->bind_col(++$column_number, \$cdi_taid,   undef);
	$sth->bind_col(++$column_number, \$bul_id_cnt,   undef);
	$sth->bind_col(++$column_number, \$bul_id_max,   undef);

#	my $header = qq|#ID	Name	Name(L)	Name(J)	Name(K)	Synonym	Synonym(J)	Definition	Definition(J)	TAID	Tree|;
	my $header = &cgi_lib::common::decodeUTF8(qq|#ID	Name	Name(L)	Name(J)	Name(K)	Synonym	Synonym(J)	Definition	Definition(J)	TAID	Tree|);

	($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime();
	my $timestamp = sprintf("%04d/%02d/%02d/ %02d:%02d:%02d", $year+1900,$month+1,$mday,$hour,$min,$sec);

	if($format eq 'xls' || $format eq 'xlsx'){
		my $workbook;
		if($format eq 'xls'){
			$workbook = Spreadsheet::WriteExcel->new($file_name);
		}elsif($format eq 'xlsx'){
			$workbook = Excel::Writer::XLSX->new($file_name);
		}
		my $uni_format = $workbook->add_format(
#			font => 'Arial Unicode MS',
			size => 10
		);
		my $worksheet_name = &cgi_lib::common::decodeUTF8($title);
#		&utf8::decode($worksheet_name) unless(&utf8::is_utf8($worksheet_name));
		my $worksheet = $workbook->add_worksheet($worksheet_name);

		my $pg=1;
		my $y = 0;

		my $x = 0;

		while($sth->fetch){

			next unless(defined $cdi_name);

			if($y==0){
#				&utf8::encode($timestamp) if(&utf8::is_utf8($timestamp));
				my $s = &cgi_lib::common::decodeUTF8(qq|#Export Date:|.&cgi_lib::common::encodeUTF8($timestamp));
#				&utf8::decode($s) unless(&utf8::is_utf8($s));
				$worksheet->write($y++, 0, $s,     $uni_format );

				$x = 0;
				foreach my $h (split(/\t/,$header)){
					$worksheet->write( $y, $x++, $h, $uni_format );
				}
				$y++;
			}



			my $buildup_logic;
			if($bul_id_cnt==2){
				$buildup_logic = 'both';
			}elsif($bul_id_max==3){
				$buildup_logic = 'is_a';
			}elsif($bul_id_max==4){
				$buildup_logic = 'part_of';
			}
#			&utf8::decode($buildup_logic) unless(&utf8::is_utf8($buildup_logic));
			$buildup_logic = &cgi_lib::common::decodeUTF8($buildup_logic);

			$x = 0;

			$worksheet->write( $y, $x++, $cdi_name, $uni_format );
			$worksheet->write( $y, $x++, $cdi_name_e, $uni_format );
			$worksheet->write( $y, $x++, $cdi_name_l, $uni_format );
			$worksheet->write( $y, $x++, $cdi_name_j, $uni_format );
			$worksheet->write( $y, $x++, $cdi_name_k, $uni_format );

			$worksheet->write( $y, $x++, $cdi_syn_e, $uni_format );
			$worksheet->write( $y, $x++, $cdi_syn_j, $uni_format );

			$worksheet->write( $y, $x++, $cdi_def_e, $uni_format );
			$worksheet->write( $y, $x++, $cdi_def_j, $uni_format );

			$worksheet->write( $y, $x++, $cdi_taid, $uni_format );
			$worksheet->write( $y, $x++, $buildup_logic, $uni_format );

			$y++;
			next if($y<65536);

			$pg++;
			my $worksheet_name = &cgi_lib::common::decodeUTF8(qq|$title ($pg)|);
#			&utf8::decode($worksheet_name) unless(&utf8::is_utf8($worksheet_name));
			$worksheet = $workbook->add_worksheet($worksheet_name);
			$y = 0;
		}
		$workbook->close();

	}else{
		open(OUT,"> $file_name");

#		&utf8::encode($timestamp) if(&utf8::is_utf8($timestamp));
#		my $s = qq|#Export Date:$timestamp|;
#		&utf8::decode($s) unless(&utf8::is_utf8($s));
		my $s = &cgi_lib::common::decodeUTF8('#Export Date:'.&cgi_lib::common::encodeUTF8($timestamp));
		print OUT &Encode::encode($CODE,$s),$LF;

		print OUT &Encode::encode($CODE,$header),$LF;

		while($sth->fetch){

			next unless(defined $cdi_name);

			my $buildup_logic;
			if($bul_id_cnt==2){
				$buildup_logic = 'both';
			}elsif($bul_id_max==3){
				$buildup_logic = 'is_a';
			}elsif($bul_id_max==4){
				$buildup_logic = 'part_of';
			}

			my @t;
			push(@t,$cdi_name);

			push(@t,$cdi_name_e);
			push(@t,$cdi_name_l);
			push(@t,$cdi_name_j);
			push(@t,$cdi_name_k);

			push(@t,$cdi_syn_e);
			push(@t,$cdi_syn_j);

			push(@t,$cdi_def_e);
			push(@t,$cdi_def_j);

			push(@t,$cdi_taid);
			push(@t,$buildup_logic);

			my $o = &cgi_lib::common::decodeUTF8(join("\t",@t));
#			utf8::decode($o) unless(utf8::is_utf8($o));
			print OUT &Encode::encode($CODE,$o),$LF;
		}

		close(OUT);
	}


	$sth->finish;
	undef $sth;

	my($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,$atime,$mtime,$ctime,$blksize,$blocks) = stat($file_name);

#	&utf8::encode($zip_file) if(&utf8::is_utf8($zip_file));
#	&utf8::encode($file_name) if(&utf8::is_utf8($file_name));
	$zip_file = &cgi_lib::common::encodeUTF8($zip_file);
	$file_name = &cgi_lib::common::encodeUTF8($file_name);

#	&utf8::decode($file_base_ext) unless(&utf8::is_utf8($file_base_ext));
	$file_base_ext = &cgi_lib::common::decodeUTF8($file_base_ext);
	my $encoded_filename = &Encode::encode_utf8($file_base_ext);
	$encoded_filename = &Encode::encode($CODE, $file_base_ext);

	my $zip = Archive::Zip->new();
	my $zip_mem = $zip->addFile($file_name,$encoded_filename);

	my $stdout = IO::File->new->fdopen(fileno(STDOUT), "w") || croak($!);
	$stdout->printflush("Content-Type: application/zip\n");
	$stdout->printflush("Content-Disposition: filename=$zip_file\n");
	$stdout->printflush("Last-Modified: ".&HTTP::Date::time2str($mtime)."\n");
#	$stdout->printflush("Accept-Ranges: bytes\n");
#	$stdout->printflush("Content-Length: $size\n");
	$stdout->printflush("Pragma: no-cache\n\n");
	$zip->writeToFileHandle($stdout, 0);
	$stdout->close;


	unlink $file_name if(-e $file_name);
	unlink $file_path if(-e $file_path);

}

=pod
sub exportTreeAll_Batch {
	my $dbh = shift;
	my $FORM = shift;

use Digest::MD5;
use Time::HiRes;

	my $ci_id = $FORM->{'ci_id'};
	my $cb_id = $FORM->{'cb_id'};

	my $md_id = $FORM->{'md_id'};
	my $mv_id = $FORM->{'mv_id'};
	my $mr_id = $FORM->{'mr_id'};

	my $title = $FORM->{'title'} || 'All FMA List';
	my $format = $FORM->{'format'} || 'tree';

	my $out_path = &catdir($FindBin::Bin,'download');
	unless(-e $out_path){
		&File::Path::mkpath($out_path,0,0777);
		chmod 0777,$out_path;
	}
	my $time_md5;

	my $prog_basename = qq|batch-export-tree-all|;
	my $prog = &catfile($FindBin::Bin,qq|$prog_basename.pl|);
	if(-e $prog && -x $prog){
		$time_md5 = &Digest::MD5::md5_hex(&Time::HiRes::time());
		$FORM->{'sessionID'} = $time_md5;
		$FORM->{'prefix'} = &catdir($out_path,$time_md5);

		my $params_file = &catfile($out_path,qq|$time_md5.json|);
		open(OUT,"> $params_file") or die $!;
		flock(OUT,2);
		print OUT &JSON::XS::encode_json($FORM);
		close(OUT);
		chmod 0666,$params_file;


		my $pid = fork;
		if(defined $pid){
			if($pid == 0){
				my $f1 = "$FindBin::Bin/logs/$prog_basename.log";
				my $f2 = "$FindBin::Bin/logs/$prog_basename.err";
				close(STDOUT);
				close(STDERR);
				open STDOUT, ">> $f1" || die "[$f1] $!\n";
				open STDERR, ">> $f2" || die "[$f2] $!\n";
				close(STDIN);
				exec(qq|nice -n 19 $prog $params_file|);
				exit(1);
			}
		}else{
			die("Can't execute program");
		}

	}
	return $time_md5;
}

sub exportTreeAll_Progress {
	my $dbh = shift;
	my $FORM = shift;

	my $out_path = &catdir($FindBin::Bin,'download');
	my $time_md5 = $FORM->{'sessionID'};
	my $params_file = &catfile($out_path,qq|$time_md5.json|);

	my $progress;
	while(1){
		open(IN,"< $params_file") or die qq|$! [$params_file]|;
		flock(IN,1);
		my @DATAS = <IN>;
		close(IN);
		eval{$progress = &JSON::XS::decode_json(join('',@DATAS));};
		undef @DATAS;
		last if(defined $progress);
	}
	delete $progress->{'prefix'};
	delete $progress->{'sessionID'};
	delete $progress->{'cmd'};
	delete $progress->{'tree'};
	delete $progress->{'t_type'};
	delete $progress->{'lng'};
	delete $progress->{'ag_data'};
	delete $progress->{'version'};
	delete $progress->{'t_depth'};
	delete $progress->{'zip_file_path'};

	return $progress;
}

sub exportTreeAll_Download {
	my $dbh = shift;
	my $FORM = shift;

	my $out_path = &catdir($FindBin::Bin,'download');
	my $time_md5 = $FORM->{'sessionID'};
	my $params_file = &catfile($out_path,qq|$time_md5.json|);

	my $progress;
	while(1){
		open(IN,"< $params_file") or die qq|$! [$params_file]|;
		flock(IN,1);
		my @DATAS = <IN>;
		close(IN);
		eval{$progress = &JSON::XS::decode_json(join('',@DATAS));};
		undef @DATAS;
		last if(defined $progress);
	}

	unless(lc($progress->{'msg'}) eq 'end'){
		print qq|Content-type: text/html; charset=UTF-8\n\n|;
	}else{
		my $zip_file_path = $progress->{'zip_file_path'};
		my $mtime = &HTTP::Date::time2str((stat($zip_file_path))[9]);
		my $zip_file = $progress->{'zip_file'};
		print<<ZIP;
Content-Type: application/zip
Content-Disposition: filename=$zip_file
Last-Modified: $mtime
Pragma: no-cache

ZIP
		open(IN,"< $zip_file_path") or die $!;
		flock(IN,1);
		binmode(IN);
		while(<IN>){
			print $_;
		}
		close(IN);
		unlink $zip_file_path;
		unlink $params_file;
	}
	return;
}

sub exportTreeAll {
	my $dbh = shift;
	my $FORM = shift;

use Encode;
use Archive::Zip;
use IO::File;

use make_bp3d_tree;

	my $ci_id = $FORM->{'ci_id'};
	my $cb_id = $FORM->{'cb_id'};

	my $md_id = $FORM->{'md_id'};
	my $mv_id = $FORM->{'mv_id'};
	my $mr_id = $FORM->{'mr_id'};

	my $title = $FORM->{'title'} || 'All FMA List';
	my $format = $FORM->{'format'} || 'tree';

	my $out_path = &catdir($FindBin::Bin,'download');
	my $prefix = &catdir($out_path,time);

	my $art_file_dir = &catdir($FindBin::Bin,'art_file');

	my ($tree_files,$use_art_ids,$mr_version) = &make_bp3d_tree::make_bp3d_tree(
		dbh    => $dbh,
		prefix => $prefix,
		ci_id  => $ci_id,
		cb_id  => $cb_id,
		md_id  => $md_id,
		mv_id  => $mv_id,
		mr_id  => $mr_id,
	);

	if(defined $tree_files && defined $use_art_ids && defined $mr_version){

		my ($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime();
		my @weekly = ('Sun', 'Mon', 'Tue', 'Wed', 'Thr', 'Fri', 'Sut');
#		my $file = sprintf("%04d%02d%02d%02d%02d%02d", $year+1900,$month+1,$mday,$hour,$min,$sec);
		my $file = defined $mr_version ? $mr_version : sprintf("%04d%02d%02d%02d%02d%02d", $year+1900,$month+1,$mday,$hour,$min,$sec);
#		my $file_basename = qq|$file.$format|;
#		my $file_base_ext = qq|$title.$format|;
#		my $file_name = &catdir($out_path,$file_basename);
		my $zip_file = qq|$file.zip|;
		my $zip_file_path = &catdir($out_path,$zip_file);

		my $LF = "\n";
		my $CODE = "utf8";
		if($ENV{HTTP_USER_AGENT}=~/Windows/){
			$LF = "\r\n";
			$CODE = "shiftjis";
		}elsif($ENV{HTTP_USER_AGENT}=~/Macintosh/){
			$LF = "\r";
			$CODE = "shiftjis";
		}

		&utf8::encode($zip_file) if(&utf8::is_utf8($zip_file));
		my $zip = Archive::Zip->new();
		my $mtime = 0;
		foreach my $file_path (@$tree_files){
			my $file_basename = &File::Basename::basename($file_path);

			my $temp_mtime = (stat($file_path))[9];
			$mtime = $temp_mtime if($mtime<$temp_mtime);

			&utf8::encode($file_path) if(&utf8::is_utf8($file_path));
			&utf8::decode($file_basename) unless(&utf8::is_utf8($file_basename));
			my $encoded_filename = &Encode::encode($CODE, $file_basename);

			$zip->addFile($file_path,$encoded_filename);
		}

		my $sth_art = $dbh->prepare(qq|select art_data from art_file where art_id=?|) or die $dbh->errstr;

		my $art_ids = "'".join("','",keys(%$use_art_ids))."'";
		my $sql =<<SQL;
select
 art_id,
 art_ext,
 EXTRACT(EPOCH FROM art_timestamp)
from
 art_file_info as arti
left join (
  select * from art_group
) as artg on
   artg.artg_id=arti.artg_id
where
 artg.atrg_use and
 artg.artg_delcause is null and
 arti.art_delcause is null and
 arti.art_id in ($art_ids)
group by
 art_id,
 art_name,
 art_ext,
 art_timestamp
SQL
		my $art_id;
		my $art_ext;
		my $art_timestamp;
		my $art_data;
		my $col_num=0;
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$sth->bind_col(++$col_num, \$art_id, undef);
		$sth->bind_col(++$col_num, \$art_ext, undef);
		$sth->bind_col(++$col_num, \$art_timestamp, undef);
		while($sth->fetch){
			my $file_path = &catfile($art_file_dir,qq|$art_id$art_ext|);
			unless(-e $file_path && (stat($file_path))[9]<=$art_timestamp){
				$sth_art->execute($art_id) or die $dbh->errstr;
				$sth_art->bind_col(1, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
				$sth_art->fetch;
				$sth_art->finish;
				next unless(defined $art_data);
				open(OUT,"> $file_path") or die $!;
				flock(OUT,2);
				binmode(OUT);
				print OUT $art_data;
				close(OUT);
				utime $art_timestamp,$art_timestamp,$file_path;
			}
			$mtime = $art_timestamp if($mtime<$art_timestamp);

			my $file_basename = &File::Basename::basename($file_path);
			&utf8::encode($file_path) if(&utf8::is_utf8($file_path));
			&utf8::decode($file_basename) unless(&utf8::is_utf8($file_basename));
			my $encoded_filename = &Encode::encode($CODE, $file_basename);
			$zip->addFile($file_path,$encoded_filename);
		}
		$sth->finish;
		undef $sth;
		undef $sth_art;

		my $stdout = IO::File->new->fdopen(fileno(STDOUT), "w") || croak($!);
		$stdout->printflush("Content-Type: application/zip\n");
		$stdout->printflush("Content-Disposition: filename=$zip_file\n");
		$stdout->printflush("Last-Modified: ".&HTTP::Date::time2str($mtime)."\n");
	#	$stdout->printflush("Accept-Ranges: bytes\n");
	#	$stdout->printflush("Content-Length: $size\n");
		$stdout->printflush("Pragma: no-cache\n\n");
		$zip->writeToFileHandle($stdout, 0);
		$stdout->close;
	}

	&File::Path::rmtree($prefix) if(-e $prefix);
}
=cut

sub exportFMA2UploadAllList {
	my $dbh = shift;
	my $FORM = shift;

use Encode;
use Spreadsheet::WriteExcel;
use Excel::Writer::XLSX;

use Archive::Zip;
use IO::File;

	my $ci_id = $FORM->{'ci_id'};
	my $cb_id = $FORM->{'cb_id'};
	my $md_id = $FORM->{'md_id'};
	my $mv_id = $FORM->{'mv_id'};
	my $mr_id = $FORM->{'mr_id'};
	my $title = $FORM->{'title'} || 'FMA2Obj';
	my $format = $FORM->{'format'} || 'txt';

	my $out_path = &catdir($FindBin::Bin,'download');
	my ($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime();
	my @weekly = ('Sun', 'Mon', 'Tue', 'Wed', 'Thr', 'Fri', 'Sut');
	my $file = sprintf("%04d%02d%02d%02d%02d%02d", $year+1900,$month+1,$mday,$hour,$min,$sec);
	my $file_basename = qq|$file.$format|;
	my $file_base_ext = qq|$title.$format|;
	my $file_name = &catdir($out_path,$file_basename);
	my $zip_file = qq|$file.zip|;
	my $file_path = &catdir($out_path,$zip_file);

	my $LF = "\n";
	my $CODE = "utf8";
	if($ENV{HTTP_USER_AGENT}=~/Windows/){
		$LF = "\r\n";
		$CODE = "shiftjis";
	}elsif($ENV{HTTP_USER_AGENT}=~/Macintosh/){
		$LF = "\r";
		$CODE = "shiftjis";
	}

	my $sql_mv=<<SQL;
SELECT
 mv_name_e,
 mv_objects_set,
 ci_name || cb_name
FROM
 model_version AS mv
LEFT JOIN (
 SELECT
  ci_id,
  ci_name
 FROM
  concept_info
) AS ci ON
 ci.ci_id=mv.ci_id
LEFT JOIN (
 SELECT
  ci_id,
  cb_id,
  cb_name
 FROM
  concept_build
) AS cb ON
 cb.ci_id=mv.ci_id AND
 cb.cb_id=mv.cb_id
WHERE
 md_id=$md_id AND
 mv_id=$mv_id
SQL

	my $sql_rep=<<SQL;
SELECT
 rep.rep_id,
 rep.cdi_name,
 bul.bul_name_e
FROM
 (
   SELECT * FROM view_representation WHERE (md_id,mv_id,mr_id,cdi_id,bul_id) IN (SELECT md_id,mv_id,max(mr_id) AS mr_id,cdi_id,bul_id FROM representation WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id<=$mr_id GROUP BY md_id,mv_id,cdi_id,bul_id)
 ) as rep

LEFT JOIN (
 SELECT * FROM buildup_logic
) AS bul ON
   rep.bul_id=bul.bul_id

WHERE
 rep_delcause IS NULL

ORDER BY
 bul.bul_order,
 rep.cdi_name
SQL

	my $sql_rep_art=<<SQL;
SELECT
 art_id
FROM
 representation_art
WHERE
 rep_id=?
ORDER BY
 art_id
SQL

	my $column_number = 0;
	my $data_version;
	my $objects_set;
	my $tree_version;
	my $sth_mv = $dbh->prepare($sql_mv) or die $dbh->errstr;
	$sth_mv->execute() or die $dbh->errstr;
	$sth_mv->bind_col(++$column_number, \$data_version,   undef);
	$sth_mv->bind_col(++$column_number, \$objects_set,   undef);
	$sth_mv->bind_col(++$column_number, \$tree_version,   undef);
	$sth_mv->fetch;
	$sth_mv->finish;
	undef $sth_mv;

	my $sth_rep_art = $dbh->prepare($sql_rep_art) or die $dbh->errstr;

	my $sth_rep = $dbh->prepare($sql_rep) or die $dbh->errstr;
	$sth_rep->execute() or die $dbh->errstr;
	my $rep_id;
	my $cdi_name;
	my $bul_name_e;
	my $art_id;
	$column_number = 0;
	$sth_rep->bind_col(++$column_number, \$rep_id,   undef);
	$sth_rep->bind_col(++$column_number, \$cdi_name,   undef);
	$sth_rep->bind_col(++$column_number, \$bul_name_e,   undef);

	my @REP;
	while($sth_rep->fetch){
		my $rep = {
			cdi_name => $cdi_name,
			bul_name_e => $bul_name_e,
			art_ids => []
		};
		$sth_rep_art->execute($rep_id) or die $dbh->errstr;
		$column_number = 0;
		$sth_rep_art->bind_col(++$column_number, \$art_id,   undef);
		while($sth_rep_art->fetch){
			push(@{$rep->{'art_ids'}},$art_id);
		}
		$sth_rep_art->finish;
		push(@REP, $rep);
	}
	$sth_rep->finish;
	undef $sth_rep;
	undef $sth_rep_art;


	open(my $OUT,"> $file_name") or die "$! [$file_name]";

	my $fmt =<<HEADER;
# Data Version	%s
# Objects set	%s
# Tree version	%s
# FMA ID	is_a/part_of	model component
HEADER
	print $OUT sprintf($fmt,$data_version,$objects_set,$tree_version);

	foreach my $rep (@REP){
		my @t;
		push(@t, $rep->{'cdi_name'});
		push(@t, $rep->{'bul_name_e'});
#		push(@t, @{$rep->{'art_ids'}});
		push(@t, join('+',@{$rep->{'art_ids'}}));

		my $o = &cgi_lib::common::decodeUTF8(join("\t",@t));
		print $OUT &Encode::encode($CODE,$o).$LF;
	}
	close($OUT);

	my($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,$atime,$mtime,$ctime,$blksize,$blocks) = stat($file_name);

	my $zip = Archive::Zip->new();
	local $Archive::Zip::UNICODE = 1;
	my $zip_mem = $zip->addFile($file_name,&cgi_lib::common::decodeUTF8($file_base_ext));

	my $stdout = IO::File->new->fdopen(fileno(STDOUT), "w") || croak($!);
	$stdout->printflush("Content-Type: application/zip\n");
	$stdout->printflush("Content-Disposition: filename=$zip_file\n");
	$stdout->printflush("Last-Modified: ".&HTTP::Date::time2str($mtime)."\n");
#	$stdout->printflush("Accept-Ranges: bytes\n");
#	$stdout->printflush("Content-Length: $size\n");
	$stdout->printflush("Pragma: no-cache\n\n");
	$zip->writeToFileHandle($stdout, 0);
	$stdout->close;


	unlink $file_name if(-e $file_name);


}
