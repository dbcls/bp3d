#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use Data::Dumper;
use DBD::Pg;
use File::Path;
use Number::Format qw(:subs);
use File::Spec::Functions qw(abs2rel rel2abs catdir catfile splitdir tmpdir);

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
require "webgl_common.pl";
use cgi_lib::common;

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);
$FORM{$_} = &cgi_lib::common::decodeUTF8($FORM{$_}) for(keys(%FORM));
$COOKIE{$_} = &cgi_lib::common::decodeUTF8($COOKIE{$_}) for(keys(%COOKIE));
my($logfile,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

my $t0 = [&Time::HiRes::gettimeofday()];
my($epocsec,$microsec) = &Time::HiRes::gettimeofday();
my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);

my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
$logfile .= '.'.sprintf("%04d%02d%02d%02d",$year+1900,$mon+1,$mday,$hour);

open(my $LOG,">> $logfile");
flock($LOG,2);
print $LOG "\n[$logtime]:$0\n";
&cgi_lib::common::message(\%FORM,$LOG);
#foreach my $key (sort keys(%FORM)){
#	print $LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}
#foreach my $key (sort keys(%COOKIE)){
#	print $LOG "\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
#}
#foreach my $key (sort keys(%ENV)){
#	print $LOG __LINE__,":\$ENV{$key}=[",$ENV{$key},"]\n";
#}

&setDefParams(\%FORM,\%COOKIE);
&cgi_lib::common::message(\%FORM,$LOG);
#foreach my $key (sort keys(%FORM)){
#	print $LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}

#$FORM{'cmd'}=qq|tree-path|;
#$FORM{'params'}=qq|{"model":"bp3d","version":"4.0","ag_data":"obj/bp3d/4.0","tree":"isa","md_id":1,"mv_id":3,"mr_id":2,"ci_id":1,"cb_id":4,"bul_id":3,"cdi_name":"FMA18886"}|;


my $DATAS = {
	"datas" => [],
	"total" => 0,
	"success" => JSON::XS::false
};

if(defined $FORM{'cmd'}){
	if($FORM{'cmd'} eq 'tree-path' && defined $FORM{'params'}){
		&getTreePath($dbh,\%FORM,$DATAS);

	}elsif($FORM{'cmd'} eq 'history-mapping' && defined $FORM{'art_id'}){
		&getHistoryMapping($dbh,\%FORM,$DATAS);

	}elsif($FORM{'cmd'} eq 'upload-history-mapping-all-list'){
		&getUploadHistoryMappingAllList($dbh,\%FORM,$DATAS);
		exit;

	}elsif($FORM{'cmd'} eq 'fma-history-mapping-all-list'){
		&getFMAHistoryMappingAllList($dbh,\%FORM,$DATAS);
		exit;

	}elsif($FORM{'cmd'} eq 'upload-all-list'){
		&outputUploadAllList($dbh,\%FORM);
		exit;

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
			&utf8::decode($DATAS->{'msg'}) unless(&utf8::is_utf8($DATAS->{'msg'}));
		}

	}elsif($FORM{'cmd'} eq 'export-tree-all-cancel'){
		eval{
			&exportTreeAll_Cancel($dbh,\%FORM);
			$DATAS->{'success'} = JSON::XS::true;
			$DATAS->{'sessionID'} = $FORM{'sessionID'};
		};
		if($@){
			$DATAS->{'msg'} = $@;
			&utf8::decode($DATAS->{'msg'}) unless(&utf8::is_utf8($DATAS->{'msg'}));
		}

	}elsif($FORM{'cmd'} eq 'export-tree-all-download'){
#		&exportTreeAll($dbh,\%FORM);
#		exit;
		&exportTreeAll_Download($dbh,\%FORM);
		exit;

	}elsif($FORM{'cmd'} eq 'export-concept'){
		&exportConcept($dbh,\%FORM);
		exit;

	}elsif($FORM{'cmd'} eq 'export-concept-art-map'){
		&exportConceptArtMap($dbh,\%FORM);
		exit;

	}
}
#print qq|Content-type: text/html; charset=UTF-8\n\n|;
#print &JSON::XS::encode_json($DATAS);
print $LOG __LINE__,":",&JSON::XS::encode_json($DATAS),"\n";
&gzip_json($DATAS);

close($LOG);

exit;

sub getTreePath {
	my $dbh = shift;
	my $FORM = shift;
	my $DATAS = shift;
	my $params = &cgi_lib::common::decodeJSON($FORM->{'params'});
	if(defined $params && ref $params eq 'HASH' && exists $params->{'cdi_name'} && defined $params->{'cdi_name'}){

		&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

		my $sql =<<SQL;
select cdi_id,but_cids from buildup_tree_info where but_delcause is null and but_pids is null
SQL
		my @W;
		my @bind_values;
		foreach my $col (qw/md_id mv_id mr_id ci_id cb_id bul_id/){
			next unless(exists $params->{$col} && defined $params->{$col});
			push(@W,qq|$col=?|);
			push(@bind_values,$params->{$col});
		}
		$sql .= " AND ".join(" AND ",@W) if(scalar @W);
		undef @W;
print $LOG __LINE__,":\$sql=[$sql]\n";
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		if(scalar @bind_values){
			$sth->execute(@bind_values) or die $dbh->errstr;
		}else{
			$sth->execute() or die $dbh->errstr;
		}
		my $cdi_id;
		my $but_cids;
		my %H;
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_id,   undef);
		$sth->bind_col(++$column_number, \$but_cids,   undef);
		while($sth->fetch){
			next unless(defined $cdi_id && defined $but_cids);
			my $cids = &cgi_lib::common::decodeJSON($but_cids);
			next unless(defined $cids);

			$H{$cdi_id} = undef;
			$H{$_} = undef for(@$cids);
		}
		$sth->finish;
		undef $sth;

#		my $ids = join(",",keys(%H));
#print $LOG __LINE__,":\$ids=[$ids]\n";
		&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);



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
#		push(@W,qq|md_id=$params->{'md_id'}|) if(defined $params->{'md_id'});
#		push(@W,qq|mv_id=$params->{'mv_id'}|) if(defined $params->{'mv_id'});
#		push(@W,qq|mr_id=$params->{'mr_id'}|) if(defined $params->{'mr_id'});
#		push(@W,qq|ci_id=$params->{'ci_id'}|) if(defined $params->{'ci_id'});
#		push(@W,qq|cb_id=$params->{'cb_id'}|) if(defined $params->{'cb_id'});
#		push(@W,qq|bul_id=$params->{'bul_id'}|) if(defined $params->{'bul_id'});
		foreach my $col (qw/md_id mv_id mr_id ci_id cb_id bul_id/){
			next unless(exists $params->{$col} && defined $params->{$col});
			push(@W,qq|$col=$params->{$col}|);
		}
		$sql .= join(" AND ",@W);
print $LOG __LINE__,":\$sql=[$sql]\n";
		$sth = $dbh->prepare($sql) or die $dbh->errstr;

		&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

		sub getParentTreeNode {
			my $dbh = shift;
			my $sth = shift;
			my $H = shift;
			my $hash = shift;
			my $nodelist = shift;
			my $p_cdi_name = shift;

			push(@$nodelist,$p_cdi_name) unless(exists $hash->{$p_cdi_name});

print $LOG __LINE__,":\$p_cdi_name=[$p_cdi_name]\n";
			return if(exists $hash->{$p_cdi_name});
print $LOG __LINE__,":\$p_cdi_name=[$p_cdi_name]\n";

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
		&getParentTreeNode($dbh,$sth,\%H,$hash,$nodelist,$params->{'cdi_name'});
		my @path;
		my $cdi_pname = $params->{'cdi_name'};
		while(defined $cdi_pname && exists $hash->{$cdi_pname}){
			unshift(@path,$cdi_pname);
			$cdi_pname = (keys(%{$hash->{$cdi_pname}}))[0];
		}
		unshift(@path,'root');

		&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

		$DATAS->{'treepath'} = '/'.join('/',@path);
		$DATAS->{'nodelist'} = $nodelist;
		$DATAS->{'success'}  = JSON::XS::true;

if(defined $LOG){
	&cgi_lib::common::message($hash, $LOG);
	&cgi_lib::common::message(\@path, $LOG);
}

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
 cmp_id,

 hist_event,
 he.he_name,

 hist_serial,
 EXTRACT(EPOCH FROM hist_timestamp)

from
 history_concept_art_map as hmap

LEFT JOIN (
--  select * from model where md_use and md_delcause is null
  select * from model
) AS md ON
   md.md_id=hmap.md_id

LEFT JOIN (
--  select * from model_version where mv_use and mv_delcause is null
  select * from model_version
) AS mv ON
   mv.md_id=hmap.md_id AND
   mv.mv_id=hmap.mv_id

LEFT JOIN (
--  select * from concept_data_info where cdi_delcause is null
  select * from concept_data_info
) AS cdi ON
   cdi.ci_id=hmap.ci_id AND
   cdi.cdi_id=hmap.cdi_id

LEFT JOIN (
--  select * from history_event where he_delcause is null
  select * from history_event
) AS he ON
   he.he_id=hmap.hist_event

where
 hmap.art_id=?
SQL

	if(exists $FORM->{'sort'} && defined $FORM->{'sort'}){
		my $SORT = &cgi_lib::common::decodeJSON($FORM->{'sort'});
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
		my $cmp_id;

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
		$sth->bind_col(++$column_number, \$cmp_id,   undef);

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
				cmp_id => $cmp_id,

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

sub outputUploadAllList {
	my $dbh = shift;
	my $FORM = shift;

	my $bul_id = $FORM->{'bul_id'};
	my $cb_id = $FORM->{'cb_id'};
	my $ci_id = $FORM->{'ci_id'};
	my $md_id = $FORM->{'md_id'};
	my $mr_id = $FORM->{'mr_id'};
	my $mv_id = $FORM->{'mv_id'};
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
.cdi_name_e>span {
	font-family:Courier,Courier New,monospace;
}

</style>
</head>
HTML

	my $sql=<<SQL;
select
 arti.art_id,
 arti.art_name,
 arti.art_ext,
 arti.artg_id,
 artg_name,
 cdi_name,
 cdi_name_e,
 cdi_syn_e,
-- rep.rep_id,
 repa.rep_id,
 art_data_size,
 cmp.cmp_id,
 cmp.cmp_abbr
from
 (
   select
     art_id,
     art_name,
     art_ext,
     art_timestamp,
     art_nsn,
     art_mirroring,
     harti.artg_id,
     art_comment,
     art_delcause,
     art_entry,
     art_openid,
--     hist_event,
--     hist_serial,
--     hist_timestamp,
     artg_name
   from
--     history_art_file_info as harti
     art_file_info as harti

   left join (
      select * from art_group
    ) as artg on
       artg.artg_id=harti.artg_id

   where
    atrg_use AND
    artg_delcause is null
--    AND (art_id,harti.artg_id,hist_serial) in (
--      select
--        art_id,artg_id,max(hist_serial)
--      from
--        history_art_file_info
--      where
--        artg_id not in (1,2)
--      group by
--        art_id,artg_id
--    ) AND
--    hist_event in (
--      select he_id from history_event where he_name in ('INSERT','UPDATE')
--    )
 ) as arti

--グループ情報
--left join (
--   select * from art_group
-- ) as artg on
--    artg.artg_id=arti.artg_id

left join (
   select art_id,art_serial,art_data_size,prefix_id from art_file
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
     (select * from concept_art_map where (ci_id,cb_id,md_id,mv_id,mr_id,art_id) in (select ci_id,cb_id,md_id,mv_id,max(mr_id),art_id from concept_art_map where ci_id=$ci_id and cb_id=$cb_id and md_id=$md_id and mv_id=$mv_id group by ci_id,cb_id,md_id,mv_id,art_id)) as cm
   where
    cm_delcause is null
 ) as map on
    map.art_id=arti.art_id

left join (
   select * from concept_art_map_part where cmp_use and cmp_delcause is null
 ) as cmp on
    cmp.cmp_id=map.cmp_id
 
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
    *
   from
    representation_art
 ) as repa on
    repa.rep_id          = rep.rep_id and
    repa.art_id          = arti.art_id and
    repa.art_hist_serial = hart2.art_hist_serial

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
 art.prefix_id,
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
	my $art_data_size;
	my $cmp_id;
	my $cmp_abbr;


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
	$sth->bind_col(++$column_number, \$art_data_size,   undef);
	$sth->bind_col(++$column_number, \$cmp_id,   undef);
	$sth->bind_col(++$column_number, \$cmp_abbr,   undef);

	print <<HTML;
<body>
HTML



	sub print_upload_all_list_head {
		print <<HTML;
<table border=1>
<thead>
<tr class="head">
<td class="row_number">#</td>
<td class="art_id">FJID</td>
<td class="rep_id">BPID</td>
<td class="cdi_name">FMA ID</td>
<td class="cdi_name_e">FMA Name</td>
<td class="cdi_syn_e">FMA Synonym</td>
<td class="art_name">objファイル名</td>
<td class="artg_name">objグループ名</td>
<td class="art_data_size">File Size</td>
</tr>
</thead>
<tbody>
HTML
	}

	sub print_upload_all_list_tail {
		print <<HTML;
</tbody>
</table>
HTML
	}

	my $rows = 0;

	while($sth->fetch){
		next unless(defined $art_id);

		$cdi_syn_e =~ s/(;)/$1<br>/g if(defined $cdi_syn_e);

		$rows++;

		&print_upload_all_list_tail() if($rows%50==1 && $rows>1);
		&print_upload_all_list_head() if($rows%50==1);

		$art_data_size = &format_number($art_data_size);

		$cmp_id = 0 unless(defined $cmp_id);
		$cmp_id -= 0;
		if($cmp_id){
			$cdi_name = sprintf('%s-%s', $cdi_name, $cmp_abbr);
			$cdi_name_e = sprintf('[<span>%s</span>] %s', $cmp_abbr, $cdi_name_e);
		}
		my $html =<<HTML;
<tr>
<td class="row_number">$rows</td>
<td class="art_id">$art_id</td>
<td class="rep_id">$rep_id</td>
<td class="cdi_name">$cdi_name</td>
<td class="cdi_name_e">$cdi_name_e</td>
<td class="cdi_syn_e">$cdi_syn_e</td>
<td class="art_name">$art_name$art_ext</td>
<td class="artg_name">$artg_name</td>
<td class="art_data_size" align="right">$art_data_size</td>
</tr>
HTML
		&utf8::encode($html) if(&utf8::is_utf8($html));
		print $html;
	}

	&print_upload_all_list_tail();

	print <<HTML;
</body>
</html>
HTML

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

	my $bul_id = $FORM->{'bul_id'};
	my $ci_id = $FORM->{'ci_id'};
	my $cb_id = $FORM->{'cb_id'};
	my $md_id = $FORM->{'md_id'};
	my $mv_id = $FORM->{'mv_id'};
	my $mr_id = $FORM->{'mr_id'};

	my $title = $FORM->{'title'} || 'All Upload Parts List';
	$title = &cgi_lib::common::decodeUTF8($title);

#	my $format = $FORM->{'format'} || 'xls';
	my $format = $FORM->{'format'} || 'txt';

	my $out_path = &catdir($FindBin::Bin,'download');
	my ($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime();
	my @weekly = ('Sun', 'Mon', 'Tue', 'Wed', 'Thr', 'Fri', 'Sut');

	my $file = exists $FORM{'filename'} && defined $FORM{'filename'} && length $FORM{'filename'} ? &_trim(&cgi_lib::common::decodeUTF8($FORM{'filename'})) : '';
	$file = sprintf("%04d%02d%02d%02d%02d%02d", $year+1900,$month+1,$mday,$hour,$min,$sec) unless(defined $file && length $file);

	my $file_basename = qq|$file.$format|;
	my $file_base_ext = qq|$file.$format|;
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
 map.cm_use,
 arti.art_mirroring,

 art.art_xmin,
 art.art_xmax,
 art.art_ymin,
 art.art_ymax,
 art.art_zmin,
 art.art_zmax,
 art.art_volume,
 art.art_data_size,

 cmp.cmp_id,
 cmp.cmp_abbr

from
 (
   select
     art_id,
     art_name,
     art_ext,
     art_mirroring,
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
    arti.art_delcause is null
--    AND arti.artg_id not in (1,2)
 ) as arti


left join (
--   select art_id,art_serial from art_file
   select
    art_id,
    art_serial,
    art_xmin,
    art_xmax,
    art_ymin,
    art_ymax,
    art_zmin,
    art_zmax,
    art_volume,
    art_data_size
   from art_file
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
     (select * from concept_art_map where (ci_id,cb_id,md_id,mv_id,mr_id,art_id) in (select ci_id,cb_id,md_id,mv_id,max(mr_id),art_id from concept_art_map where ci_id=$ci_id and cb_id=$cb_id and md_id=$md_id and mv_id=$mv_id group by ci_id,cb_id,md_id,mv_id,art_id)) as cm
   where
    cm_delcause is null
 ) as map on
    map.art_id=arti.art_id

left join (
   select * from concept_art_map_part where cmp_use and cmp_delcause is null
 ) as cmp on
    cmp.cmp_id=map.cmp_id

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
 md.md_name_e ASC NULLS LAST,
 mv.mv_name_e ASC NULLS LAST,
 bul.bul_name_e ASC NULLS LAST,
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
	my $art_mirroring;

	my $art_xmin;
	my $art_xmax;
	my $art_ymin;
	my $art_ymax;
	my $art_zmin;
	my $art_zmax;
	my $art_volume;
	my $art_data_size;

	my $cmp_id;
	my $cmp_abbr;

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
	$sth->bind_col(++$column_number, \$art_mirroring,   undef);

	$sth->bind_col(++$column_number, \$art_xmin,   undef);
	$sth->bind_col(++$column_number, \$art_xmax,   undef);
	$sth->bind_col(++$column_number, \$art_ymin,   undef);
	$sth->bind_col(++$column_number, \$art_ymax,   undef);
	$sth->bind_col(++$column_number, \$art_zmin,   undef);
	$sth->bind_col(++$column_number, \$art_zmax,   undef);
	$sth->bind_col(++$column_number, \$art_volume,   undef);
	$sth->bind_col(++$column_number, \$art_data_size,   undef);

	$sth->bind_col(++$column_number, \$cmp_id,   undef);
	$sth->bind_col(++$column_number, \$cmp_abbr,   undef);

#	my $header = qq|#FJID	BPID	FMA_ID	FMA_Name	FMA_Synonym	OBJ_Filename	OBJ_Group	OBJ_Timestamp	Comment	Category	Judge	Class	Model	Version	Tree|;
#	my $header = qq|#FJID	BPID	Use_Map	FMA_ID	FMA_Name	FMA_Synonym	OBJ_Filename	OBJ_Group	OBJ_Timestamp	Comment	Category	Judge	Class|;
#	my $header = qq|#FJID	BPID	Use_Map	FMA_ID	FMA_Name	FMA_Synonym	OBJ_Filename	OBJ_Group	OBJ_Timestamp	Comment	Category	Judge	Class	Xmin	Xmax	Ymin	Ymax	Zmin	Zmax	Volume|;
	my $header = qq|#FJID	BPID	Use_Map	isMirroring	FMA_ID	FMA_Name	FMA_Synonym	OBJ_Filename	OBJ_Group	OBJ_Timestamp	Comment	Category	Judge	Class	Xmin	Xmax	Ymin	Ymax	Zmin	Zmax	Volume	Size|;
	&utf8::decode($header) unless(&utf8::is_utf8($header));

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
		my $worksheet_name = $title;
		&utf8::decode($worksheet_name) unless(&utf8::is_utf8($worksheet_name));
		my $worksheet = $workbook->add_worksheet($worksheet_name);

		my $pg=1;
		my $y = 0;

		my $x = 0;


		while($sth->fetch){
			next unless(defined $art_id);

			if($y==0){
				&utf8::encode($timestamp) if(&utf8::is_utf8($timestamp));
				my $s = qq|#Export Date:$timestamp|;
				&utf8::decode($s) unless(&utf8::is_utf8($s));
				$worksheet->write($y++, 0, $s,     $uni_format );

				&utf8::encode($md_name_e) if(&utf8::is_utf8($md_name_e));
				$s = qq|#Model:$md_name_e|;
				&utf8::decode($s) unless(&utf8::is_utf8($s));
				$worksheet->write($y++, 0, $s,     $uni_format );

				&utf8::encode($mv_name_e) if(&utf8::is_utf8($mv_name_e));
				$s = qq|#Version:$mv_name_e|;
				&utf8::decode($s) unless(&utf8::is_utf8($s));
				$worksheet->write($y++, 0, $s,     $uni_format );

				&utf8::encode($bul_name_e) if(&utf8::is_utf8($bul_name_e));
				$s = qq|#Tree:$bul_name_e|;
				&utf8::decode($s) unless(&utf8::is_utf8($s));
				$worksheet->write($y++, 0, $s,     $uni_format );

				$x = 0;
				foreach my $h (split(/\t/,$header)){
					$worksheet->write( $y, $x++, $h, $uni_format );
				}
				$y++;
			}

			$x = 0;

			$cmp_id = 0 unless(defined $cmp_id);
			$cmp_id -= 0;
			if($cmp_id){
				$cdi_name = sprintf('%s-%s', $cdi_name, $cmp_abbr);
				$cdi_name_e = sprintf('[%s] %s', $cmp_abbr, $cdi_name_e);
			}

			$worksheet->write( $y, $x++, $art_id,     $uni_format );
			$worksheet->write( $y, $x++, $rep_id,     $uni_format );
			$worksheet->write( $y, $x++, $cm_use,   $uni_format );
			$worksheet->write( $y, $x++, $art_mirroring,   $uni_format );

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

			$worksheet->write( $y, $x++, $art_xmin,     $uni_format );
			$worksheet->write( $y, $x++, $art_xmax,     $uni_format );
			$worksheet->write( $y, $x++, $art_ymin,     $uni_format );
			$worksheet->write( $y, $x++, $art_ymax,     $uni_format );
			$worksheet->write( $y, $x++, $art_zmin,     $uni_format );
			$worksheet->write( $y, $x++, $art_zmax,     $uni_format );
			$worksheet->write( $y, $x++, $art_volume,     $uni_format );
			$worksheet->write( $y, $x++, $art_data_size,     $uni_format );

			$y++;
			next if(($format eq 'xls' && $y<65536) || ($format eq 'xlsx' && $y<1048576));

			$pg++;
			my $worksheet_name = qq|$title ($pg)|;
			&utf8::decode($worksheet_name) unless(&utf8::is_utf8($worksheet_name));
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
				&utf8::encode($timestamp) if(&utf8::is_utf8($timestamp));
				my $s = qq|#Export Date:$timestamp|;
				&utf8::decode($s) unless(&utf8::is_utf8($s));
				print OUT &Encode::encode($CODE,$s),$LF;
				$y++;

				&utf8::encode($md_name_e) if(&utf8::is_utf8($md_name_e));
				$s = qq|#Model:$md_name_e|;
				&utf8::decode($s) unless(&utf8::is_utf8($s));
				print OUT &Encode::encode($CODE,$s),$LF;
				$y++;

				&utf8::encode($mv_name_e) if(&utf8::is_utf8($mv_name_e));
				$s = qq|#Version:$mv_name_e|;
				&utf8::decode($s) unless(&utf8::is_utf8($s));
				print OUT &Encode::encode($CODE,$s),$LF;
				$y++;

				&utf8::encode($bul_name_e) if(&utf8::is_utf8($bul_name_e));
				$s = qq|#Tree:$bul_name_e|;
				&utf8::decode($s) unless(&utf8::is_utf8($s));
				print OUT &Encode::encode($CODE,$s),$LF;
				$y++;

				print OUT &Encode::encode($CODE,$header),$LF;
				$y++;
			}

			$cmp_id = 0 unless(defined $cmp_id);
			$cmp_id -= 0;
			if($cmp_id){
				$cdi_name = sprintf('%s-%s', $cdi_name, $cmp_abbr);
				$cdi_name_e = sprintf('[%s] %s', $cmp_abbr, $cdi_name_e);
			}

			my @t;
			push(@t,$art_id);
			push(@t,$rep_id);
			push(@t,$cm_use);
			push(@t,$art_mirroring);
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

			push(@t,$art_xmin);
			push(@t,$art_xmax);
			push(@t,$art_ymin);
			push(@t,$art_ymax);
			push(@t,$art_zmin);
			push(@t,$art_zmax);
			push(@t,$art_volume);
			push(@t,$art_data_size);

			my $o = join("\t",@t);
			utf8::decode($o) unless(utf8::is_utf8($o));
			print OUT &Encode::encode($CODE,$o),$LF;

			$y++;
		}

		close(OUT);
	}

	$sth->finish;
	undef $sth;

	my($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,$atime,$mtime,$ctime,$blksize,$blocks) = stat($file_name);

	&utf8::encode($zip_file) if(&utf8::is_utf8($zip_file));
	&utf8::encode($file_name) if(&utf8::is_utf8($file_name));

	&utf8::decode($file_base_ext) unless(&utf8::is_utf8($file_base_ext));
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

	my $sth_but_cids = $dbh->prepare(qq|select cdi_id,but_cids from view_buildup_tree where ci_id=$ci_id AND cb_id=$cb_id and bul_id=4 and cdi_name='FMA20394'|);
	$sth_but_cids->execute() or die DBI->errstr();
	my $column_number = 0;
	my $cdi_id;
	my $but_cids;
	my %but_cids_hash;
	$sth_but_cids->bind_col(++$column_number, \$cdi_id, undef);
	$sth_but_cids->bind_col(++$column_number, \$but_cids, undef);
	$sth_but_cids->fetch;
	$sth_but_cids->finish;
	if(defined $cdi_id){
		$but_cids_hash{$cdi_id} = undef;
		if(defined $but_cids){
			$but_cids = &cgi_lib::common::decodeJSON($but_cids);
			if(defined $but_cids && ref $but_cids eq 'ARRAY'){
				%but_cids_hash = map {$_ => undef} @$but_cids;
			}
		}
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
    select * from concept_data_info where ci_id=$ci_id
  ) as cdi

left join (
  select ci_id,cb_id,cdi_id,count(bul_id) as c,max(bul_id) as m from (
    select ci_id,cb_id,cdi_id,bul_id from buildup_tree where ci_id=$ci_id AND cb_id=$cb_id group by ci_id,cb_id,cdi_id,bul_id
  ) as a
  group by a.ci_id,a.cb_id,a.cdi_id

) as but2 on
   cdi.ci_id=but2.ci_id AND
   cdi.cdi_id=but2.cdi_id

where
 cdi_delcause is null
 and but2.c > 0
order by
 to_number(substring(cdi_name from 4),'999999')
SQL

	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;

#	my $cdi_id;
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

	$column_number = 0;
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
	my %buildup_logic_count;

	while($sth->fetch){

		next unless(defined $cdi_name);

		$cdi_syn_e =~ s/(;)/$1<br>/g if(defined $cdi_syn_e);
#print $LOG __LINE__.':'.join("\t",$cdi_id,$cdi_name,$cdi_name_j,$cdi_name_e,$cdi_syn_j,$cdi_syn_e,$cdi_def_j,$cdi_def_e,$cdi_taid,$bul_id_cnt,$bul_id_max)."\n";

		my $buildup_logic;
		if($bul_id_cnt==2){
			if(exists $but_cids_hash{$cdi_id}){
				$buildup_logic = 'both';
			}else{
				$buildup_logic = 'is_a';
#				$buildup_logic = 'is_a*';
			}
		}elsif($bul_id_max==3){
			$buildup_logic = 'is_a';
		}elsif($bul_id_max==4){
			$buildup_logic = 'part_of';
		}else{
			$buildup_logic = 'none';
		}
		$buildup_logic_count{$buildup_logic} = 0 unless(exists $buildup_logic_count{$buildup_logic});
		$buildup_logic_count{$buildup_logic}++;

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
		&utf8::encode($html) if(&utf8::is_utf8($html));
		print $html;
	}

	&print_table_tail();

	foreach my $key (sort keys(%buildup_logic_count)){
		print qq|$key=[$buildup_logic_count{$key}]<br>|;
	}
=pod
both=[40038]
is_a=[44412]
=cut

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

	my $ci_id = $FORM->{'ci_id'};
	my $cb_id = $FORM->{'cb_id'};
	my $title = $FORM->{'title'} || 'All FMA List';
	$title = &cgi_lib::common::decodeUTF8($title);
#	my $format = $FORM->{'format'} || 'xls';
	my $format = $FORM->{'format'} || 'txt';

	my $out_path = &catdir($FindBin::Bin,'download');
	my ($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime();
	my @weekly = ('Sun', 'Mon', 'Tue', 'Wed', 'Thr', 'Fri', 'Sut');

	my $file = exists $FORM{'filename'} && defined $FORM{'filename'} && length $FORM{'filename'} ? &_trim(&cgi_lib::common::decodeUTF8($FORM{'filename'})) : '';
	$file = sprintf("%04d%02d%02d%02d%02d%02d", $year+1900,$month+1,$mday,$hour,$min,$sec) unless(defined $file && length $file);

	my $file_basename = qq|$file.$format|;
	my $file_base_ext = qq|$file.$format|;
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

	my $sth_but_cids = $dbh->prepare(qq|select cdi_id,but_cids from view_buildup_tree where ci_id=$ci_id AND cb_id=$cb_id and bul_id=4 and cdi_name='FMA20394'|);
	$sth_but_cids->execute() or die DBI->errstr();
	my $column_number = 0;
	my $cdi_id;
	my $but_cids;
	my %but_cids_hash;
	$sth_but_cids->bind_col(++$column_number, \$cdi_id, undef);
	$sth_but_cids->bind_col(++$column_number, \$but_cids, undef);
	$sth_but_cids->fetch;
	$sth_but_cids->finish;
	if(defined $cdi_id){
		$but_cids_hash{$cdi_id} = undef;
		if(defined $but_cids){
			$but_cids = &cgi_lib::common::decodeJSON($but_cids);
			if(defined $but_cids && ref $but_cids eq 'ARRAY'){
				%but_cids_hash = map {$_ => undef} @$but_cids;
			}
		}
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
    select * from concept_data_info where ci_id=$ci_id
  ) as cdi

left join (
  select ci_id,cb_id,cdi_id,count(bul_id) as c,max(bul_id) as m from (
    select ci_id,cb_id,cdi_id,bul_id from buildup_tree where ci_id=$ci_id AND cb_id=$cb_id group by ci_id,cb_id,cdi_id,bul_id
  ) as a
  group by a.ci_id,a.cb_id,a.cdi_id

) as but2 on
   cdi.ci_id=but2.ci_id AND
   cdi.cdi_id=but2.cdi_id

where
 cdi_delcause is null
 and but2.c > 0
order by
 to_number(substring(cdi_name from 4),'999999')
SQL

	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;

#	my $cdi_id;
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

	$column_number = 0;
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

	my $header = qq|#ID	Name	Name(L)	Name(J)	Name(K)	Synonym	Synonym(J)	Definition	Definition(J)	TAID	Tree|;
	&utf8::decode($header) unless(&utf8::is_utf8($header));

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
#		&cgi_lib::common::message($title,$LOG);
		my $worksheet_name = &cgi_lib::common::decodeUTF8('ALL FMA List');
#		my $worksheet_name = &cgi_lib::common::encodeUTF8($title);
#		&cgi_lib::common::message($worksheet_name,$LOG);
		my $worksheet = $workbook->add_worksheet($worksheet_name);

		my $pg=1;
		my $y = 0;

		my $x = 0;

		while($sth->fetch){

			next unless(defined $cdi_name);

			if($y==0){
				&utf8::encode($timestamp) if(&utf8::is_utf8($timestamp));
				my $s = qq|#Export Date:$timestamp|;
				&utf8::decode($s) unless(&utf8::is_utf8($s));
				$worksheet->write($y++, 0, $s,     $uni_format );

				$x = 0;
				foreach my $h (split(/\t/,$header)){
					$worksheet->write( $y, $x++, $h, $uni_format );
				}
				$y++;
			}



			my $buildup_logic;
			if($bul_id_cnt==2){
				if(exists $but_cids_hash{$cdi_id}){
					$buildup_logic = 'both';
				}else{
					$buildup_logic = 'is_a';
				}
			}elsif($bul_id_max==3){
				$buildup_logic = 'is_a';
			}elsif($bul_id_max==4){
				$buildup_logic = 'part_of';
			}else{
				$buildup_logic = 'none';
			}
			&utf8::decode($buildup_logic) unless(&utf8::is_utf8($buildup_logic));

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
			next if(($format eq 'xls' && $y<65536) || ($format eq 'xlsx' && $y<1048576));

			$pg++;
			my $worksheet_name = qq|$title ($pg)|;
			&utf8::decode($worksheet_name) unless(&utf8::is_utf8($worksheet_name));
			$worksheet = $workbook->add_worksheet($worksheet_name);
			$y = 0;
		}
		$workbook->close();

	}else{
		open(OUT,"> $file_name");

		&utf8::encode($timestamp) if(&utf8::is_utf8($timestamp));
		my $s = qq|#Export Date:$timestamp|;
		&utf8::decode($s) unless(&utf8::is_utf8($s));
		print OUT &Encode::encode($CODE,$s),$LF;

		print OUT &Encode::encode($CODE,$header),$LF;

		while($sth->fetch){

			next unless(defined $cdi_name);

			my $buildup_logic;
			if($bul_id_cnt==2){
				if(exists $but_cids_hash{$cdi_id}){
					$buildup_logic = 'both';
				}else{
					$buildup_logic = 'is_a';
				}
			}elsif($bul_id_max==3){
				$buildup_logic = 'is_a';
			}elsif($bul_id_max==4){
				$buildup_logic = 'part_of';
			}else{
				$buildup_logic = 'none';
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

			my $o = join("\t",@t);
			utf8::decode($o) unless(utf8::is_utf8($o));
			print OUT &Encode::encode($CODE,$o),$LF;
		}

		close(OUT);
	}


	$sth->finish;
	undef $sth;

	my($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,$atime,$mtime,$ctime,$blksize,$blocks) = stat($file_name);

	&utf8::encode($zip_file) if(&utf8::is_utf8($zip_file));
	&utf8::encode($file_name) if(&utf8::is_utf8($file_name));

	&utf8::decode($file_base_ext) unless(&utf8::is_utf8($file_base_ext));
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
	my $prog = &catfile($FindBin::Bin,'..','batch',qq|$prog_basename.pl|);
	if(-e $prog && -x $prog){
		$time_md5 = &Digest::MD5::md5_hex(&Time::HiRes::time());
		$FORM->{'sessionID'} = $time_md5;
		$FORM->{'prefix'} = &catdir($out_path,$time_md5);

		my $params_file = &catfile($out_path,qq|$time_md5.json|);
#		open(OUT,"> $params_file") or die $!;
#		flock(OUT,2);
#		print OUT &JSON::XS::encode_json($FORM);
#		close(OUT);
#		chmod 0666,$params_file;

		&cgi_lib::common::writeFileJSON($params_file,$FORM);
		chmod 0666,$params_file;

		my $test_file = &catfile($out_path,qq|$time_md5.txt|);
		&cgi_lib::common::writeFileJSON($test_file,$FORM,1);
		chmod 0666,$test_file;

		my $pid = fork;
		if(defined $pid){
			if($pid == 0){
				my $logs_file = &catfile($FindBin::Bin,'logs',$prog_basename.sprintf(".%05d",$$));
				my $f1 = "$logs_file.log";
				my $f2 = "$logs_file.err";
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
		$progress = &cgi_lib::common::decodeJSON(join('',@DATAS));
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

sub exportTreeAll_Cancel {
	my $dbh = shift;
	my $FORM = shift;

	my $out_path = &catdir($FindBin::Bin,'download');
	my $time_md5 = $FORM->{'sessionID'};
	my $prefix = &catdir($out_path,$time_md5);
	my $params_file = &catfile($out_path,qq|$time_md5.json|);

	&File::Path::rmtree($prefix) or die $! if(-e $prefix);
	unlink $params_file or die $! if(-e $params_file);
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
		$progress = &cgi_lib::common::decodeJSON(join('',@DATAS));
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

sub exportConcept {
	my $dbh = shift;
	my $FORM = shift;

use Encode;

use Archive::Zip;
use IO::File;
use File::Copy;
use File::Path;

	my $ci_id = $FORM->{'ci_id'};
	my $cb_id = $FORM->{'cb_id'};
	my $all_data = exists $FORM->{'all_data'} && defined $FORM->{'all_data'} && $FORM->{'all_data'} eq '1' ? 1 : undef;

	$ci_id = undef unless(defined $ci_id && $ci_id =~ /^[0-9]+$/);
	$cb_id = undef unless(defined $cb_id && $cb_id =~ /^[0-9]+$/);

	my $column_number = 0;

	my %CDI;
	my %BUL;
	my %RELATION_TYPE;

	my %USE_CDI;
	my %TYPEDEF;

	my $sth_cb_sel = $dbh->prepare(qq|
select
 ci_name as concept,
 cb_name as build,
 cb_release as release,
 EXTRACT(EPOCH FROM cb_release) as release_epoch,
 cb_entry as entry,
 EXTRACT(EPOCH FROM cb_entry) as entry_epoch
from
 concept_build as cb

left join (
 select * from concept_info
) as ci on ci.ci_id=cb.ci_id
where
 cb.ci_id=? and cb.cb_id=?
|) or die $dbh->errstr;
	$sth_cb_sel->execute($ci_id,$cb_id) or die $dbh->errstr;
	my $CONCEPT_BUILD = $sth_cb_sel->fetchrow_hashref;
	if(defined $CONCEPT_BUILD && ref $CONCEPT_BUILD eq 'HASH'){
		$CONCEPT_BUILD->{'entry_epoch'} -= 0,
		$CONCEPT_BUILD->{'release_epoch'} -= 0,
	}else{
		$CONCEPT_BUILD = {};
	}
	$sth_cb_sel->finish;

	my $sth_cdi_sel = $dbh->prepare(qq|select *,EXTRACT(EPOCH FROM cdi_entry) as cdi_entry_epoch from concept_data_info where ci_id=?|) or die $dbh->errstr;
	$sth_cdi_sel->execute($ci_id) or die $dbh->errstr;
	while(my $hash_ref = $sth_cdi_sel->fetchrow_hashref){
		my $cdi_id = $hash_ref->{'cdi_id'};
		$hash_ref->{'entry'} = $hash_ref->{'cdi_entry'};
		$hash_ref->{'entry_epoch'} = $hash_ref->{'cdi_entry_epoch'} - 0;
		$hash_ref->{'id'} = $hash_ref->{'cdi_name'};
		$hash_ref->{'name'} = $hash_ref->{'cdi_name_e'};
		$hash_ref->{'synonym'} = defined $hash_ref->{'cdi_syn_e'} ? [split(/;/,$hash_ref->{'cdi_syn_e'})] : undef;
		$hash_ref->{'def'} = $hash_ref->{'cdi_def_e'};
		$hash_ref->{'taid'} = $hash_ref->{'cdi_taid'};

		delete $hash_ref->{'ci_id'};
		delete $hash_ref->{'cdi_id'};
		delete $hash_ref->{'cdi_openid'};
		delete $hash_ref->{'cdi_name'};
		delete $hash_ref->{'cdi_name_e'};
		delete $hash_ref->{'cdi_name_j'};
		delete $hash_ref->{'cdi_name_k'};
		delete $hash_ref->{'cdi_name_l'};
		delete $hash_ref->{'cdi_taid'};
		delete $hash_ref->{'cdi_syn_e'};
		delete $hash_ref->{'cdi_syn_j'};
		delete $hash_ref->{'cdi_def_e'};
		delete $hash_ref->{'cdi_def_j'};
		delete $hash_ref->{'cdi_comment'};
		delete $hash_ref->{'cdi_delcause'};
		delete $hash_ref->{'cdi_entry'};
		delete $hash_ref->{'cdi_entry_epoch'};

		if(defined $all_data){
			$USE_CDI{$hash_ref->{'id'}} = $CDI{$cdi_id} = $hash_ref;
		}else{
			$CDI{$cdi_id} = $hash_ref;
		}
	}
	$sth_cdi_sel->finish;


	my $sth_cd_sel = $dbh->prepare(qq|select *,EXTRACT(EPOCH FROM cd_entry) as cd_entry_epoch from concept_data where ci_id=? and cb_id=?|) or die $dbh->errstr;
	$sth_cd_sel->execute($ci_id,$cb_id) or die $dbh->errstr;
	while(my $hash_ref = $sth_cd_sel->fetchrow_hashref){
		my $cdi_id = $hash_ref->{'cdi_id'};
		$CDI{$cdi_id}->{'entry'} = $hash_ref->{'cd_entry'};
		$CDI{$cdi_id}->{'entry_epoch'} = $hash_ref->{'cd_entry_epoch'} - 0;
		$CDI{$cdi_id}->{'name'} = $hash_ref->{'cd_name'};
		$CDI{$cdi_id}->{'synonym'} = defined $hash_ref->{'cd_syn'} ? [split(/;/,$hash_ref->{'cd_syn'})] : undef;
		$CDI{$cdi_id}->{'def'} = $hash_ref->{'cd_def'};
	}
	$sth_cd_sel->finish;


	my $sth_bul_sel = $dbh->prepare(qq|select * from buildup_logic|) or die $dbh->errstr;
	$sth_bul_sel->execute() or die $dbh->errstr;
	while(my $hash_ref = $sth_bul_sel->fetchrow_hashref){
		$BUL{$hash_ref->{'bul_id'}} = $hash_ref;
	}
	$sth_bul_sel->finish;

	my $sth_rel_sel = $dbh->prepare(qq|select * from fma_partof_type|) or die $dbh->errstr;
	$sth_rel_sel->execute() or die $dbh->errstr;
	while(my $hash_ref = $sth_rel_sel->fetchrow_hashref){
		$RELATION_TYPE{$hash_ref->{'f_potid'}} = $hash_ref;
	}
	$sth_rel_sel->finish;

	my $sth_ct_sel = $dbh->prepare(qq|select * from concept_tree where ci_id=? and cb_id=?|) or die $dbh->errstr;
	$sth_ct_sel->execute($ci_id,$cb_id) or die $dbh->errstr;
	while(my $hash_ref = $sth_ct_sel->fetchrow_hashref){
		next unless(exists $CDI{$hash_ref->{'cdi_id'}} && defined $CDI{$hash_ref->{'cdi_id'}});
		next unless(exists $BUL{$hash_ref->{'bul_id'}} && defined $BUL{$hash_ref->{'bul_id'}});

		$USE_CDI{$CDI{$hash_ref->{'cdi_id'}}->{'id'}} = $CDI{$hash_ref->{'cdi_id'}} unless(exists $USE_CDI{$CDI{$hash_ref->{'cdi_id'}}->{'id'}});

		if(defined $hash_ref->{'cdi_pid'} && exists $CDI{$hash_ref->{'cdi_pid'}} && defined $CDI{$hash_ref->{'cdi_pid'}}){
			$USE_CDI{$CDI{$hash_ref->{'cdi_pid'}}->{'id'}} = $CDI{$hash_ref->{'cdi_pid'}} unless(exists $USE_CDI{$CDI{$hash_ref->{'cdi_pid'}}->{'id'}});

			if(defined $hash_ref->{'f_potids'}){
#				my $cdi = $CDI{$hash_ref->{'cdi_id'}}->{$BUL{$hash_ref->{'bul_id'}}->{'bul_name_e'}}->{'parent'}->{$CDI{$hash_ref->{'cdi_pid'}}->{'id'}} = [];

				$CDI{$hash_ref->{'cdi_id'}}->{$BUL{$hash_ref->{'bul_id'}}->{'bul_name_e'}}->{'parent'} = {} unless(exists $CDI{$hash_ref->{'cdi_id'}}->{$BUL{$hash_ref->{'bul_id'}}->{'bul_name_e'}}->{'parent'});
				my $parent = $CDI{$hash_ref->{'cdi_id'}}->{$BUL{$hash_ref->{'bul_id'}}->{'bul_name_e'}}->{'parent'};

				my @f_potids = split(/;/,$hash_ref->{'f_potids'});
				foreach my $f_potid (@f_potids){
					next unless(exists $RELATION_TYPE{$f_potid} && defined $RELATION_TYPE{$f_potid});
#					push(@$cdi,$RELATION_TYPE{$f_potid}->{'f_potname'});

					my $f_potname = $RELATION_TYPE{$f_potid}->{'f_potname'};
					$parent->{$f_potname} = [] unless(exists $parent->{$f_potname});
					push(@{$parent->{$f_potname}}, $CDI{$hash_ref->{'cdi_pid'}}->{'id'});

					$TYPEDEF{$f_potname} = 0 unless(exists $TYPEDEF{$f_potname});
					$TYPEDEF{$f_potname}++;
				}
			}else{
				$CDI{$hash_ref->{'cdi_id'}}->{$BUL{$hash_ref->{'bul_id'}}->{'bul_name_e'}} = {} unless(exists $CDI{$hash_ref->{'cdi_id'}}->{$BUL{$hash_ref->{'bul_id'}}->{'bul_name_e'}});
				$CDI{$hash_ref->{'cdi_id'}}->{$BUL{$hash_ref->{'bul_id'}}->{'bul_name_e'}}->{'parent'} = [] unless(exists $CDI{$hash_ref->{'cdi_id'}}->{$BUL{$hash_ref->{'bul_id'}}->{'bul_name_e'}}->{'parent'});
				my $parent = $CDI{$hash_ref->{'cdi_id'}}->{$BUL{$hash_ref->{'bul_id'}}->{'bul_name_e'}}->{'parent'};
				push(@$parent, $CDI{$hash_ref->{'cdi_pid'}}->{'id'});
			}
		}
	}
	$sth_ct_sel->finish;

#select cdi_id,bul_id,but_cids,but_depth from buildup_tree where but_cids is not null and ci_id=1 and cb_id=9 group by cdi_id,bul_id,but_cids,but_depth;

#&cgi_lib::common::message('',$LOG);
#	my $sth_but_sel = $dbh->prepare(qq|select cdi_id,bul_id,but_cids,but_depth from buildup_tree where but_cids is not null and ci_id=? and cb_id=? group by cdi_id,bul_id,but_cids,but_depth|) or die $dbh->errstr;
	my $sth_but_sel = $dbh->prepare(qq|select cdi_id,bul_id,but_cids from buildup_tree where but_cids is not null and ci_id=? and cb_id=? group by cdi_id,bul_id,but_cids|) or die $dbh->errstr;
	$sth_but_sel->execute($ci_id,$cb_id) or die $dbh->errstr;
	while(my $hash_ref = $sth_but_sel->fetchrow_hashref){
		next unless(exists $CDI{$hash_ref->{'cdi_id'}} && defined $CDI{$hash_ref->{'cdi_id'}});
		next unless(exists $BUL{$hash_ref->{'bul_id'}} && defined $BUL{$hash_ref->{'bul_id'}});
		my $but_cids = &cgi_lib::common::decodeJSON($hash_ref->{'but_cids'});
		next unless(defined $but_cids && ref $but_cids eq 'ARRAY');
		my @CCDI;
		foreach my $cdi_id (@$but_cids){
			next unless(exists $CDI{$cdi_id} && defined $CDI{$cdi_id});
			push(@CCDI, $CDI{$cdi_id}->{'id'});
		}
		if(scalar @CCDI){
			if(exists $CDI{$hash_ref->{'cdi_id'}}->{$BUL{$hash_ref->{'bul_id'}}->{'bul_name_e'}}->{'all_children'}){
				&cgi_lib::common::message(scalar @{$CDI{$hash_ref->{'cdi_id'}}->{$BUL{$hash_ref->{'bul_id'}}->{'bul_name_e'}}->{'all_children'}},$LOG);
				&cgi_lib::common::message(&cgi_lib::common::encodeJSON($CDI{$hash_ref->{'cdi_id'}}->{$BUL{$hash_ref->{'bul_id'}}->{'bul_name_e'}}->{'all_children'},1),$LOG);
				&cgi_lib::common::message(scalar @CCDI,$LOG);
				&cgi_lib::common::message(&cgi_lib::common::encodeJSON([sort @CCDI],1),$LOG);

				&cgi_lib::common::message(&cgi_lib::common::encodeJSON($CDI{$hash_ref->{'cdi_id'}}->{$BUL{$hash_ref->{'bul_id'}}->{'bul_name_e'}}->{'all_children'},0),$LOG);
				&cgi_lib::common::message(&cgi_lib::common::encodeJSON([sort @CCDI],0),$LOG);
				die __LINE__ ;
			}else{
				$CDI{$hash_ref->{'cdi_id'}}->{$BUL{$hash_ref->{'bul_id'}}->{'bul_name_e'}}->{'all_children'} = [];
			}
			push(@{$CDI{$hash_ref->{'cdi_id'}}->{$BUL{$hash_ref->{'bul_id'}}->{'bul_name_e'}}->{'all_children'}}, sort @CCDI);
		}
#		$CDI{$hash_ref->{'cdi_id'}}->{$BUL{$hash_ref->{'bul_id'}}->{'bul_name_e'}}->{'depth'} = $hash_ref->{'but_depth'};

	}
	$sth_but_sel->finish;

#	foreach my $cdi_id (keys(%CDI)){
#		next if(exists $USE_CDI{$cdi_id});
#		delete $USE_CDI{$cdi_id};
#	}

	my $out_path = &catdir($FindBin::Bin,'download',".$$");
	&File::Path::rmtree($out_path) if(-e $out_path);
	&File::Path::mkpath($out_path);
	my $json_file_name = &catdir($out_path,&cgi_lib::common::decodeUTF8('concept_data_info.json'));
#	&cgi_lib::common::writeFileJSON($json_file_name,\%CDI,1);
#	&cgi_lib::common::writeFileJSON($json_file_name,\%USE_CDI,1);
#	$CONCEPT_BUILD->{'term'} = \%USE_CDI;
	$CONCEPT_BUILD->{'terms'} = [];
	push(@{$CONCEPT_BUILD->{'terms'}}, $USE_CDI{$_}) for(sort keys(%USE_CDI));
	$CONCEPT_BUILD->{'#terms'} = scalar @{$CONCEPT_BUILD->{'terms'}};

#	$CONCEPT_BUILD->{'typedef'} = [sort keys(%TYPEDEF)];
	$CONCEPT_BUILD->{'typedef'} = \%TYPEDEF;
	$CONCEPT_BUILD->{'#typedef'} = scalar keys(%TYPEDEF);
	&cgi_lib::common::writeFileJSON($json_file_name,$CONCEPT_BUILD,1);
#die __LINE__;
	my $zip = Archive::Zip->new();
	$zip->addFile(&cgi_lib::common::encodeUTF8($json_file_name),&cgi_lib::common::encodeUTF8(&File::Basename::basename($json_file_name)));

	my $file = exists $FORM{'filename'} && defined $FORM{'filename'} && length $FORM{'filename'} ? &_trim(&cgi_lib::common::decodeUTF8($FORM{'filename'})) : undef;
	unless(defined $file && length $file){
		my ($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime();
		$file = sprintf("%04d%02d%02d%02d%02d%02d", $year+1900,$month+1,$mday,$hour,$min,$sec);
	}
	my $zip_file = qq|$file.zip|;
	my $file_path = &catdir($out_path,$zip_file);

	my($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,$atime,$mtime,$ctime,$blksize,$blocks) = stat($json_file_name);
	$zip_file = &cgi_lib::common::encodeUTF8($zip_file);

	my $stdout = IO::File->new->fdopen(fileno(STDOUT), "w") || croak($!);
	$stdout->printflush("Pragma: no-cache\n");
	$stdout->printflush("Content-Type: application/zip\n");
	$stdout->printflush("Content-Disposition: filename=$zip_file\n");
	$stdout->printflush("Last-Modified: ".&HTTP::Date::time2str($mtime)."\n");
#	$stdout->printflush("Accept-Ranges: bytes\n");
#	$stdout->printflush("Content-Length: $size\n");
	$stdout->printflush("\n");
	$zip->writeToFileHandle($stdout, 0);
	$stdout->close;

	&File::Path::rmtree($out_path) if(-e $out_path);
}

sub exportConceptArtMap {
	my $dbh = shift;
	my $FORM = shift;

use Encode;

use Archive::Zip;
use IO::File;
use File::Copy;
use File::Path;

	my $ci_id = $FORM->{'ci_id'};
	my $cb_id = $FORM->{'cb_id'};
	my $md_id = $FORM->{'md_id'};
	my $mv_id = $FORM->{'mv_id'};
	my $mr_id = $FORM->{'mr_id'};

	$ci_id = undef unless(defined $ci_id && $ci_id =~ /^[0-9]+$/);
	$cb_id = undef unless(defined $cb_id && $cb_id =~ /^[0-9]+$/);
	$md_id = undef unless(defined $md_id && $md_id =~ /^[0-9]+$/);
	$mv_id = undef unless(defined $mv_id && $mv_id =~ /^[0-9]+$/);
	$mr_id = undef unless(defined $mr_id && $mr_id =~ /^[0-9]+$/);

	my $mv_filter = '';
	my $mv_ids = exists $FORM->{'mv_ids'} && defined $FORM->{'mv_ids'} ? &cgi_lib::common::decodeJSON($FORM->{'mv_ids'}) : undef;
	unless(defined $mv_ids && ref $mv_ids eq 'ARRAY' && scalar @$mv_ids){
		if(defined $md_id && defined $mv_id){
			push(@$mv_ids,{md_id=>$md_id,mv_id=>$mv_id});
		}
	}
	if(defined $mv_ids && ref $mv_ids eq 'ARRAY' && scalar @$mv_ids){
		$mv_ids = [grep {defined $_ && ref $_ eq 'HASH' && exists $_->{'md_id'} && defined $_->{'md_id'} && $_->{'md_id'} =~ /^[0-9]+$/ && exists $_->{'mv_id'} && defined $_->{'mv_id'} && $_->{'mv_id'} =~ /^[0-9]+$/} @$mv_ids];
		my @mvs = map {$_->{'mv_id'}} @$mv_ids;
		if(scalar @mvs){
			$mv_filter = ' and mv_id in ('.join(',',@mvs).')';
		}
	}
	unless($mv_filter eq ''){
		if(defined $md_id && defined $mv_id){
			$mv_filter = ' and mv_id in ('.$mv_id.')';
		}
	}

	die __LINE__ unless(defined $mv_ids && ref $mv_ids eq 'ARRAY');

	my $column_number = 0;

	my %ART_IDS;
	my %CDI_NAMES;
	my %CDI_IDS;
=pod
	my $sth_map_sel_cdi = $dbh->prepare(qq/
select
 cdi_name || cmp_abbr,
 cdi_name_e,
 MAX(cm_entry),
 EXTRACT(EPOCH FROM max(cm_entry)),
 cm.cmp_id,
 cm.cdi_id
from
 (select * from concept_art_map where (ci_id,cb_id,md_id,mv_id,mr_id,cdi_id,cmp_id) in (select ci_id,cb_id,md_id,mv_id,max(mr_id),cdi_id,cmp_id from concept_art_map where md_id=? and mv_id=? group by ci_id,cb_id,md_id,mv_id,cdi_id,cmp_id)) as cm

left join (
  select
   ci_id,
   cdi_id,
   cdi_name,
   cdi_name_e
  from
   concept_data_info
  where
   cdi_delcause is null
) as cdi on cdi.ci_id=cm.ci_id and cdi.cdi_id=cm.cdi_id

left join (
  select
   cmp_id,
   cmp_title,
   cmp_abbr
  from
   concept_art_map_part
  where
   cmp_delcause is null
) as cmp on cmp.cmp_id=cm.cmp_id

where
 cm_use and
 cm_delcause is null
group by
 cdi_name,
 cdi_name_e,
 cmp_abbr,
 cm.cmp_id,
 cm.cdi_id
/) or die $dbh->errstr;
=cut
	my $sth_map_sel_cdi = $dbh->prepare(qq/
select
 cdi_name || cmp_abbr,
 cdi_name_e,
 MAX(cm_entry),
 EXTRACT(EPOCH FROM max(cm_entry)),
 MAX(art_timestamp),
 cm.cmp_id,
 cm.cdi_id
from
 (select * from concept_art_map where (ci_id,cb_id,md_id,mv_id,mr_id,cdi_id,cmp_id) in (select ci_id,cb_id,md_id,mv_id,max(mr_id),cdi_id,cmp_id from concept_art_map where md_id=? and mv_id=? group by ci_id,cb_id,md_id,mv_id,cdi_id,cmp_id)) as cm

left join (
  select
   ci_id,
   cdi_id,
   cdi_name,
   cdi_name_e
  from
   concept_data_info
  where
   cdi_delcause is null
) as cdi on cdi.ci_id=cm.ci_id and cdi.cdi_id=cm.cdi_id

left join (
  select
   cmp_id,
   cmp_title,
   cmp_abbr
  from
   concept_art_map_part
  where
   cmp_delcause is null
) as cmp on cmp.cmp_id=cm.cmp_id

left join (
  select
   art_id,
   art_timestamp)::date
  from
   history_art_file_info
) as afi on afi.art_id=cm.art_id

where
 cm_use and
 cm_delcause is null
group by
 cdi_name,
 cdi_name_e,
 cmp_abbr,
 cm.cmp_id,
 cm.cdi_id
/) or die $dbh->errstr;
=pod
	my $sth_map_sel_art = $dbh->prepare(qq/
select 
  art_id,
  art_hist_serial,
  cdi_name || cmp_abbr,
  cm_entry,
  EXTRACT(EPOCH FROM cm_entry) as cm_entry_epoch,
  cm.cmp_id,
  cm.cdi_id
from
 (select * from concept_art_map where (ci_id,cb_id,md_id,mv_id,mr_id,cdi_id,cmp_id) in (select ci_id,cb_id,md_id,mv_id,max(mr_id),cdi_id,cmp_id from concept_art_map where md_id=? and mv_id=? group by ci_id,cb_id,md_id,mv_id,cdi_id,cmp_id)) as cm

left join (
  select
   ci_id,
   cdi_id,
   cdi_name,
   cdi_name_e
  from
   concept_data_info
  where
   cdi_delcause is null
) as cdi on cdi.ci_id=cm.ci_id and cdi.cdi_id=cm.cdi_id

left join (
  select
   cmp_id,
   cmp_title,
   cmp_abbr
  from
   concept_art_map_part
  where
   cmp_delcause is null
) as cmp on cmp.cmp_id=cm.cmp_id


where
 cm_use and
 cm_delcause is null
;
/) or die $dbh->errstr;
=cut
	my $sth_map_sel_art = $dbh->prepare(qq/
select 
  cm.art_id,
  MAX(art_hist_serial),
  cdi_name || cmp_abbr as cdi_name,
  cm_entry,
  EXTRACT(EPOCH FROM cm_entry) as cm_entry_epoch,
  art_timestamp,
  cm.cmp_id,
  cm.cdi_id
from
 (select * from concept_art_map where (ci_id,cb_id,md_id,mv_id,mr_id,cdi_id,cmp_id) in (select ci_id,cb_id,md_id,mv_id,max(mr_id),cdi_id,cmp_id from concept_art_map where md_id=? and mv_id=? group by ci_id,cb_id,md_id,mv_id,cdi_id,cmp_id)) as cm

left join (
  select
   ci_id,
   cdi_id,
   cdi_name,
   cdi_name_e
  from
   concept_data_info
  where
   cdi_delcause is null
) as cdi on cdi.ci_id=cm.ci_id and cdi.cdi_id=cm.cdi_id

left join (
  select
   cmp_id,
   cmp_title,
   cmp_abbr
  from
   concept_art_map_part
  where
   cmp_delcause is null
) as cmp on cmp.cmp_id=cm.cmp_id

left join (
  select
   art_id,
   MAX(art_timestamp::date) as art_timestamp
  from
   history_art_file_info
  group by
   art_id
) as afi on afi.art_id=cm.art_id

where
 cm_use and
 cm_delcause is null
group by
  cm.art_id,
  cdi_name || cmp_abbr,
  cm_entry,
  EXTRACT(EPOCH FROM cm_entry),
  art_timestamp,
  cm.cmp_id,
  cm.cdi_id
;
/) or die $dbh->errstr;

	foreach my $mv_ids (reverse @$mv_ids){
		$column_number = 0;
		$sth_map_sel_cdi->execute($mv_ids->{'md_id'},$mv_ids->{'mv_id'}) or die $dbh->errstr;
		my $cdi_name;
		my $cdi_name_e;
		my $cm_entry;
		my $cm_entry_epoch;
		my $art_timestamp;
		my $cmp_id;
		my $cdi_id;
		$sth_map_sel_cdi->bind_col(++$column_number, \$cdi_name, undef);
		$sth_map_sel_cdi->bind_col(++$column_number, \$cdi_name_e, undef);
		$sth_map_sel_cdi->bind_col(++$column_number, \$cm_entry, undef);
		$sth_map_sel_cdi->bind_col(++$column_number, \$cm_entry_epoch, undef);
		$sth_map_sel_cdi->bind_col(++$column_number, \$art_timestamp, undef);
		$sth_map_sel_cdi->bind_col(++$column_number, \$cmp_id, undef);
		$sth_map_sel_cdi->bind_col(++$column_number, \$cdi_id, undef);
		while($sth_map_sel_cdi->fetch){
			$CDI_NAMES{$cdi_name} = {
				cm_entry       => $cm_entry,
				cm_entry_epoch => $cm_entry_epoch - 0,
				art_timestamp  => $art_timestamp,
				art_id         => {}
			};
			$CDI_IDS{qq|$cdi_id\t$cmp_id|} = {};
		}
		$sth_map_sel_cdi->finish;


		$sth_map_sel_art->execute($mv_ids->{'md_id'},$mv_ids->{'mv_id'}) or die $dbh->errstr;
		my($art_id,$art_hist_serial);
		$column_number = 0;
		$sth_map_sel_art->bind_col(++$column_number, \$art_id, undef);
		$sth_map_sel_art->bind_col(++$column_number, \$art_hist_serial, undef);
		$sth_map_sel_art->bind_col(++$column_number, \$cdi_name, undef);
		$sth_map_sel_art->bind_col(++$column_number, \$cm_entry, undef);
		$sth_map_sel_art->bind_col(++$column_number, \$cm_entry_epoch, undef);
		$sth_map_sel_art->bind_col(++$column_number, \$art_timestamp, undef);
		$sth_map_sel_art->bind_col(++$column_number, \$cmp_id, undef);
		$sth_map_sel_art->bind_col(++$column_number, \$cdi_id, undef);
		while($sth_map_sel_art->fetch){

			next unless($CDI_NAMES{$cdi_name}->{'art_timestamp'} eq $art_timestamp);

			$CDI_NAMES{$cdi_name}->{'art_id'}->{$art_id} = {
				art_hist_serial => $art_hist_serial,
				cm_entry        => $cm_entry,
				cm_entry_epoch  => $cm_entry_epoch - 0
			};
			$CDI_IDS{qq|$cdi_id\t$cmp_id|}->{$art_id} = $cm_entry;
		}
		$sth_map_sel_art->finish;
	}

	my @SQLS;
	if(scalar keys(%CDI_IDS)){
		foreach my $c_id (keys(%CDI_IDS)){
			my($cdi_id,$cmp_id) = split(/\t/,$c_id);
			foreach my $art_id (keys(%{$CDI_IDS{$c_id}})){
#				push(@SQLS,sprintf("INSERT INTO concept_art_map (art_id,ci_id,cb_id,cdi_id,md_id,mv_id) VALUES (%s,1,9,%d,1,1);",$art_id,$cdi_id));
				push(@SQLS,join("\t",$art_id,1,9,$cdi_id,1,1,$cmp_id,$CDI_IDS{$c_id}->{$art_id}));
			}
		}
	}



	my $sth_art_sel = $dbh->prepare(qq{
select
-- arti.art_id,
 arti.art_name,
 arti.art_ext,
 arti.art_timestamp,
 EXTRACT(EPOCH FROM arti.art_timestamp),

 arti.art_nsn,
 arti.art_mirroring,
 arta.art_comment,
 arti.art_delcause,
 arti.art_entry,
 EXTRACT(EPOCH FROM arti.art_entry),
 prefix.prefix_char,
 art.art_serial,
 art.art_md5,
 art.art_data_size,
 art.art_xmin,
 art.art_xmax,
 art.art_ymin,
 art.art_ymax,
 art.art_zmin,
 art.art_zmax,
 art.art_volume,
 art.art_cube_volume,
 arta.art_category,
 arta.art_judge,
 arta.art_class,
 arto.arto_id,
 arto.arto_comment,
 artf.artf_id,
-- COALESCE(artf.artf_pid,0),
 artf.artf_pid,
-- COALESCE(artf.artf_name,'/')
 artf.artf_name
from
 art_file_info as arti

left join (
  select
   art_id,
   prefix_id,
   art_serial,
   art_md5,
   art_data_size,
   art_xmin,
   art_xmax,
   art_ymin,
   art_ymax,
   art_zmin,
   art_zmax,
   art_volume,
   art_cube_volume
  from
   art_file
  where
   art_delcause is null
) as art on art.art_id=arti.art_id

left join (
  select
   *
  from
   art_annotation
) as arta on arta.art_id=arti.art_id

left join (
  select
   *
  from
   art_org_info
) as arto on arto.art_id=arti.art_id

left join (
 select * from id_prefix where prefix_delcause is null
) as prefix on prefix.prefix_id=art.prefix_id

left join (
  select artg_id,artf_id from art_group
) as artg on artg.artg_id=arti.artg_id

left join (
  select artf_id,artf_pid,artf_name from art_folder
) as artf on artf.artf_id=artg.artf_id

where
 arti.art_id=?
order by
 art.prefix_id,
 art.art_serial,
 arti.art_id
}) or die $dbh->errstr;

	my $sth_data = $dbh->prepare(qq|select art_data from art_file where art_id=? order by art_serial desc NULLS FIRST limit 1|) or die $dbh->errstr;
#	my $sth_folder = $dbh->prepare(qq|select COALESCE(artf.artf_id,0) as artf_id,artf.artf_pid,COALESCE(artf.artf_name,'') as artf_name from art_folder as artf where COALESCE(artf.artf_id,0)=?|) or die $dbh->errstr;
	my $sth_folder = $dbh->prepare(qq|select artf.artf_id,artf.artf_pid,artf.artf_name from art_folder as artf where artf.artf_id=?|) or die $dbh->errstr;

	my $art_file_base_path = &catdir($FindBin::Bin,'art_file');
	my $out_path = &catdir($FindBin::Bin,'download',".$$");
	&File::Path::rmtree($out_path) if(-e $out_path);
	&File::Path::mkpath($out_path);
	my $zip = Archive::Zip->new();

	foreach my $cdi_name (keys(%CDI_NAMES)){
		foreach my $art_id (keys(%{$CDI_NAMES{$cdi_name}->{'art_id'}})){
			die __LINE__ if(exists $ART_IDS{$art_id} && defined $ART_IDS{$art_id});
			$ART_IDS{$art_id} = $CDI_NAMES{$cdi_name}->{'art_id'}->{$art_id};

			$sth_art_sel->execute($art_id) or die $dbh->errstr;

#			my $art_id;
			my $art_name;
			my $art_ext;
			my $art_timestamp;
			my $art_timestamp_epoch;

			my $art_nsn;
			my $art_mirroring;
			my $art_comment;
			my $art_delcause;
			my $art_entry;
			my $art_entry_epoch;
			my $prefix_char;
			my $art_serial;
			my $art_md5;
			my $art_data_size;
			my $art_xmin;
			my $art_xmax;
			my $art_ymin;
			my $art_ymax;
			my $art_zmin;
			my $art_zmax;
			my $art_volume;
			my $art_cube_volume;
			my $art_category;
			my $art_judge;
			my $art_class;
			my $arto_id;
			my $arto_comment;

			my $artf_id;
			my $artf_pid;
			my $artf_name;

			$column_number = 0;
#			$sth_art_sel->bind_col(++$column_number, \$art_id,   undef);
			$sth_art_sel->bind_col(++$column_number, \$art_name,   undef);
			$sth_art_sel->bind_col(++$column_number, \$art_ext,   undef);
			$sth_art_sel->bind_col(++$column_number, \$art_timestamp,   undef);
			$sth_art_sel->bind_col(++$column_number, \$art_timestamp_epoch,   undef);

			$sth_art_sel->bind_col(++$column_number, \$art_nsn,   undef);
			$sth_art_sel->bind_col(++$column_number, \$art_mirroring,   undef);
			$sth_art_sel->bind_col(++$column_number, \$art_comment,   undef);
			$sth_art_sel->bind_col(++$column_number, \$art_delcause,   undef);
			$sth_art_sel->bind_col(++$column_number, \$art_entry,   undef);
			$sth_art_sel->bind_col(++$column_number, \$art_entry_epoch,   undef);
			$sth_art_sel->bind_col(++$column_number, \$prefix_char,   undef);
			$sth_art_sel->bind_col(++$column_number, \$art_serial,   undef);
			$sth_art_sel->bind_col(++$column_number, \$art_md5,   undef);
			$sth_art_sel->bind_col(++$column_number, \$art_data_size,   undef);
			$sth_art_sel->bind_col(++$column_number, \$art_xmin,   undef);
			$sth_art_sel->bind_col(++$column_number, \$art_xmax,   undef);
			$sth_art_sel->bind_col(++$column_number, \$art_ymin,   undef);
			$sth_art_sel->bind_col(++$column_number, \$art_ymax,   undef);
			$sth_art_sel->bind_col(++$column_number, \$art_zmin,   undef);
			$sth_art_sel->bind_col(++$column_number, \$art_zmax,   undef);
			$sth_art_sel->bind_col(++$column_number, \$art_volume,   undef);
			$sth_art_sel->bind_col(++$column_number, \$art_cube_volume,   undef);
			$sth_art_sel->bind_col(++$column_number, \$art_category,   undef);
			$sth_art_sel->bind_col(++$column_number, \$art_judge,   undef);
			$sth_art_sel->bind_col(++$column_number, \$art_class,   undef);
			$sth_art_sel->bind_col(++$column_number, \$arto_id,   undef);
			$sth_art_sel->bind_col(++$column_number, \$arto_comment,   undef);

			$sth_art_sel->bind_col(++$column_number, \$artf_id,   undef);
			$sth_art_sel->bind_col(++$column_number, \$artf_pid,   undef);
			$sth_art_sel->bind_col(++$column_number, \$artf_name,   undef);

			$sth_art_sel->fetch;

			$ART_IDS{$art_id}->{'art_name'} = $art_name;
			$ART_IDS{$art_id}->{'art_ext'} = $art_ext;
			$ART_IDS{$art_id}->{'art_timestamp'} = $art_timestamp;
			$ART_IDS{$art_id}->{'art_timestamp_epoch'} = $art_timestamp_epoch - 0;

			$ART_IDS{$art_id}->{'art_nsn'} = $art_nsn;
			$ART_IDS{$art_id}->{'art_mirroring'} = $art_mirroring;
			$ART_IDS{$art_id}->{'art_comment'} = $art_comment;
			$ART_IDS{$art_id}->{'art_delcause'} = $art_delcause;
			$ART_IDS{$art_id}->{'art_entry'} = $art_entry;
			$ART_IDS{$art_id}->{'art_entry_epoch'} = $art_entry_epoch - 0;
			$ART_IDS{$art_id}->{'prefix_char'} = $prefix_char;
			$ART_IDS{$art_id}->{'art_serial'} = $art_serial - 0;
			$ART_IDS{$art_id}->{'art_md5'} = $art_md5;
			$ART_IDS{$art_id}->{'art_data_size'} = $art_data_size - 0;

			$ART_IDS{$art_id}->{'art_xmin'} = $art_xmin - 0;
			$ART_IDS{$art_id}->{'art_xmax'} = $art_xmax - 0;
			$ART_IDS{$art_id}->{'art_ymin'} = $art_ymin - 0;
			$ART_IDS{$art_id}->{'art_ymax'} = $art_ymax - 0;
			$ART_IDS{$art_id}->{'art_zmin'} = $art_zmin - 0;
			$ART_IDS{$art_id}->{'art_zmax'} = $art_zmax - 0;
			$ART_IDS{$art_id}->{'art_volume'} = $art_volume - 0;
			$ART_IDS{$art_id}->{'art_cube_volume'} = $art_cube_volume - 0;

			$ART_IDS{$art_id}->{'art_category'} = $art_category;
			$ART_IDS{$art_id}->{'art_judge'} = $art_judge;
			$ART_IDS{$art_id}->{'art_class'} = $art_class;
			$ART_IDS{$art_id}->{'arto_id'} = defined $arto_id ? [split(/;/,$arto_id)] : undef;
			$ART_IDS{$art_id}->{'arto_comment'} = $arto_comment;

			my @ART_FOLDER;
			unshift(@ART_FOLDER,defined $artf_name ? $artf_name : '');
			while(defined $artf_pid){
				$sth_folder->execute($artf_pid) or die $dbh->errstr;
				$column_number = 0;
				$sth_folder->bind_col(++$column_number, \$artf_id,   undef);
				$sth_folder->bind_col(++$column_number, \$artf_pid,   undef);
				$sth_folder->bind_col(++$column_number, \$artf_name,   undef);
				$sth_folder->fetch;
				$sth_folder->finish;
				unshift(@ART_FOLDER,defined $artf_name ? $artf_name : '');
			}
			$ART_IDS{$art_id}->{'artf_name'} = '/'.join('/',@ART_FOLDER);

			$sth_art_sel->finish;

			my $art_filename = qq|$art_id$art_ext|;
			my $art_file_path = &catfile($art_file_base_path,$art_filename);
			my $out_art_file_path = &catfile($out_path,$art_filename);

			my($size,$timestamp) = (0,0);
			($size,$timestamp) = (stat($art_file_path))[7,9] if(-e $art_file_path && -f $art_file_path && -s $art_file_path);

			unless($art_data_size==$size && $art_timestamp_epoch==$timestamp){
				my $art_data;
				$sth_data->execute($art_id) or die $dbh->errstr;
				$sth_data->bind_col(1, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
				$sth_data->fetch;
				$sth_data->finish;
				if(defined $art_data && open(my $OBJ,"> $art_file_path")){
					flock($OBJ,2);
					binmode($OBJ,':utf8');
					print $OBJ $art_data;
					close($OBJ);
					undef $OBJ;
				}
				undef $art_data;
				utime $art_timestamp_epoch,$art_timestamp_epoch,$art_file_path;
			}
			&File::Copy::copy($art_file_path,$out_art_file_path);
			next unless(-e $out_art_file_path && -s $out_art_file_path);

			utime $art_timestamp_epoch,$art_timestamp_epoch,$out_art_file_path;
			$zip->addFile(&cgi_lib::common::encodeUTF8($out_art_file_path),&cgi_lib::common::encodeUTF8($art_filename));

		}
	}

	my $json_file_name = &catdir($out_path,&cgi_lib::common::decodeUTF8('concept_art_map.json'));
	&cgi_lib::common::writeFileJSON($json_file_name,\%CDI_NAMES,1);
	$zip->addFile(&cgi_lib::common::encodeUTF8($json_file_name),&cgi_lib::common::encodeUTF8(&File::Basename::basename($json_file_name)));

	if(scalar @SQLS){
		my $sql_file_name = &catdir($out_path,&cgi_lib::common::decodeUTF8('concept_art_map.txt'));
		my $OUT;
		open($OUT,qq|> $sql_file_name|) or die __FILE__.':'.__LINE__.':'.$!.qq|[$sql_file_name]|;
		flock($OUT,2);
		print $OUT join("\n",@SQLS)."\n";
		close($OUT);
		$zip->addFile(&cgi_lib::common::encodeUTF8($sql_file_name),&cgi_lib::common::encodeUTF8(&File::Basename::basename($sql_file_name)));
	}

	my $file = exists $FORM{'filename'} && defined $FORM{'filename'} && length $FORM{'filename'} ? &_trim(&cgi_lib::common::decodeUTF8($FORM{'filename'})) : undef;
	unless(defined $file && length $file){
		my ($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime();
		$file = sprintf("%04d%02d%02d%02d%02d%02d", $year+1900,$month+1,$mday,$hour,$min,$sec);
	}
	my $zip_file = qq|$file.zip|;
	my $file_path = &catdir($out_path,$zip_file);

	my($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,$atime,$mtime,$ctime,$blksize,$blocks) = stat($json_file_name);
	$zip_file = &cgi_lib::common::encodeUTF8($zip_file);

	my $stdout = IO::File->new->fdopen(fileno(STDOUT), "w") || croak($!);
	$stdout->printflush("Pragma: no-cache\n");
	$stdout->printflush("Content-Type: application/zip\n");
	$stdout->printflush("Content-Disposition: filename=$zip_file\n");
	$stdout->printflush("Last-Modified: ".&HTTP::Date::time2str($mtime)."\n");
#	$stdout->printflush("Accept-Ranges: bytes\n");
#	$stdout->printflush("Content-Length: $size\n");
	$stdout->printflush("\n");
	$zip->writeToFileHandle($stdout, 0);
	$stdout->close;

	&File::Path::rmtree($out_path) if(-e $out_path);
}

sub getUploadHistoryMappingAllList {
	my $dbh = shift;
	my $FORM = shift;

	my $ci_id = $FORM->{'ci_id'};
	my $md_id = $FORM->{'md_id'};
	my $title = $FORM->{'title'};

	my $mv_filter = '';
	my $mv_ids = exists $FORM->{'mv_ids'} && defined $FORM->{'mv_ids'} ? &cgi_lib::common::decodeJSON($FORM->{'mv_ids'}) : [];
	if(defined $mv_ids && ref $mv_ids eq 'ARRAY' && scalar @$mv_ids){
		my @mvs = map {$_->{'mv_id'}} grep {defined $_ && ref $_ eq 'HASH' && exists $_->{'mv_id'} && defined $_->{'mv_id'} && $_->{'mv_id'} =~ /^[0-9]+$/} @$mv_ids;
		if(scalar @mvs){
			$mv_filter = ' and mv_id in ('.join(',',@mvs).')';
		}
	}

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
tr>td {
	vertical-align: top;
}
tr.head>td {
	text-align: center;
	vertical-align: middle;
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
	display: none;
	width: 44px;
	text-align: right;
	background-color: #cccccc;
	-moz-user-select:-moz-none;
	-khtml-user-select:none;
	-webkit-user-select:none;
}
.art_id {
	width: 70px;
	max-width: 70px;
}
.cdi_name {
	width: 70px;
	max-width: 70px;
}
.number {
	text-align: right;
	width: 70px;
	max-width: 70px;
}
.art_data_size {
}
.art_xmin {
	display: none;
}
.art_xmax {
	display: none;
}
.art_ymin {
	display: none;
}
.art_ymax {
	display: none;
}
.art_zmin {
	display: none;
}
.art_zmax {
	display: none;
}
.art_volume {
	display: none;
}
</style>
</head>
HTML

	my $sql_art=<<SQL;
select
 arti.art_id,
 arti.art_name,
 arti.art_ext,
 art_data_size,
 art_xmin,
 art_xmax,
 art_ymin,
 art_ymax,
 art_zmin,
 art_zmax,
 art_volume
from
 (
   select md_id,art_id from concept_art_map where (ci_id,cb_id,md_id,mv_id,mr_id,art_id) in (
     select ci_id,cb_id,md_id,mv_id,max(mr_id),art_id from concept_art_map
     where
      ci_id=$ci_id and md_id=$md_id $mv_filter and
      mv_id in (
        select mr.mv_id from model_version as mv
        left join (
           select * from model_revision
         ) as mr on
            mr.md_id=mv.md_id and
            mr.mv_id=mv.mv_id
        where
         mv.md_id=$md_id and
         mv_delcause is null and
         mv_use and
--         mv_publish and
         mr_delcause is null and
         mr_use
        group by mr.mv_id
      )
     group by
      ci_id,cb_id,md_id,mv_id,art_id
   )
   and cm_delcause is null and cm_use
   group by md_id,art_id
 ) as cm

left join (
   select
    art_id,
    art_serial,
    prefix_id,
    art_data_size,
    art_xmin,
    art_xmax,
    art_ymin,
    art_ymax,
    art_zmin,
    art_zmax,
    art_volume
   from
    art_file
 ) as art on
    art.art_id=cm.art_id

left join (
   select
    art_id,
    art_name,
    art_ext,
    art_timestamp
   from
    art_file_info
 ) as arti on
    arti.art_id=cm.art_id

left join (
   select * from id_prefix
 ) as id_prefix on
    id_prefix.prefix_id=art.prefix_id

order by
 id_prefix.prefix_char,
 art.art_serial,
 art.art_id
;
SQL

	my $sql_cm=<<SQL;
select
 cdi_name,
 cdi_name_e,
 cdi_syn_e,
 cmp.cmp_id,
 cmp.cmp_abbr
from
 (
   select * from concept_art_map where (ci_id,cb_id,md_id,mv_id,mr_id,art_id) in (
     select ci_id,cb_id,md_id,mv_id,max(mr_id),art_id from concept_art_map where ci_id=$ci_id and md_id=$md_id group by ci_id,cb_id,md_id,mv_id,art_id
   )
   and cm_delcause is null and cm_use $mv_filter
 ) as cm

left join (
   select * from concept_data_info
 ) as cdi on
    cdi.ci_id=cm.ci_id and
    cdi.cdi_id=cm.cdi_id

left join (
   select * from concept_art_map_part
 ) as cmp on
    cmp.cmp_id=cm.cmp_id

where
  cm.mv_id=? and
  cm.art_id=?
SQL

	my $sql_header=<<SQL;
select
 mv.mv_id,
 mv_name_e,
 to_char(mr_entry,'YYYY/MM/DD'),
 to_char(hist_timestamp,'YYYY/MM/DD')
from
 (select * from model_version where (md_id,mv_id) in (
   select
    md_id,min(mv_id)
   from
    model_version
   where
    mv_delcause is null and
    mv_use and
--    mv_publish and
    md_id=$md_id $mv_filter
   group by
    md_id,mv_objects_set
 )) as mv

left join (
   select md_id,mv_id,max(mr_entry) as mr_entry from model_revision where mr_delcause is null and mr_use group by md_id,mv_id
 ) as mr on
    mr.md_id=mv.md_id and
    mr.mv_id=mv.mv_id

left join (
   select md_id,mv_id,max(hist_timestamp) as hist_timestamp from history_concept_art_map group by md_id,mv_id
 ) as hcm on
    hcm.md_id=mv.md_id and
    hcm.mv_id=mv.mv_id

order by
 mr_entry,
 hist_timestamp
;
SQL

	my $sth_art = $dbh->prepare($sql_art) or die $dbh->errstr;
	$sth_art->execute() or die $dbh->errstr;
	my $art_id;
	my $art_name;
	my $art_ext;
	my $art_data_size;
	my $art_xmin;
	my $art_xmax;
	my $art_ymin;
	my $art_ymax;
	my $art_zmin;
	my $art_zmax;
	my $art_volume;

	my $column_number = 0;
	$sth_art->bind_col(++$column_number, \$art_id,   undef);
	$sth_art->bind_col(++$column_number, \$art_name,   undef);
	$sth_art->bind_col(++$column_number, \$art_ext,   undef);
	$sth_art->bind_col(++$column_number, \$art_data_size,   undef);
	$sth_art->bind_col(++$column_number, \$art_xmin,   undef);
	$sth_art->bind_col(++$column_number, \$art_xmax,   undef);
	$sth_art->bind_col(++$column_number, \$art_ymin,   undef);
	$sth_art->bind_col(++$column_number, \$art_ymax,   undef);
	$sth_art->bind_col(++$column_number, \$art_zmin,   undef);
	$sth_art->bind_col(++$column_number, \$art_zmax,   undef);
	$sth_art->bind_col(++$column_number, \$art_volume,   undef);


	my $sth_cm = $dbh->prepare($sql_cm) or die $dbh->errstr;

	print <<HTML;
<body>
HTML


	my @HEADER;
	my $sth_header = $dbh->prepare($sql_header) or die $dbh->errstr;
	$sth_header->execute() or die $dbh->errstr;
	my $h_mv_id;
	my $h_mv_name_e;
	my $h_mr_entry;
	my $h_hist_timestamp;
	$column_number = 0;
	$sth_header->bind_col(++$column_number, \$h_mv_id,   undef);
	$sth_header->bind_col(++$column_number, \$h_mv_name_e,   undef);
	$sth_header->bind_col(++$column_number, \$h_mr_entry,   undef);
	$sth_header->bind_col(++$column_number, \$h_hist_timestamp,   undef);
	while($sth_header->fetch){
		push(@HEADER,{
			mv_id => $h_mv_id,
			mv_name_e => $h_mv_name_e,
			mr_entry => $h_mr_entry,
			hist_timestamp => $h_hist_timestamp,
		});
	}
	$sth_header->finish;
	undef $sth_header;

	sub print_upload_history_mapping_all_list_head {
		my $HEADER = shift;

		print <<HTML;
<table border=1>
<thead>
<tr class="head">
<td class="row_number">#</td>
<td class="art_id">FJID</td>
<td class="art_name">objファイル名</td>
<td class="art_data_size number">File Size</td>
<td class="art_xmin number">XMin</td>
<td class="art_xmax number">XMax</td>
<td class="art_ymin number">YMin</td>
<td class="art_ymax number">YMax</td>
<td class="art_zmin number">ZMin</td>
<td class="art_zmax number">ZMax</td>
<td class="art_volume number">Volume</td>
HTML

		foreach my $header (@$HEADER){
			print <<HTML;
<td class="cdi_name">$header->{mv_name_e}<br>FMA ID</td>
HTML
		}

		print <<HTML;
</tr>
</thead>
<tbody>
HTML
	}

	sub print_upload_history_mapping_all_list_tail {
		print <<HTML;
</tbody>
</table>
HTML
	}

	my $rows = 0;

	while($sth_art->fetch){
		next unless(defined $art_id);


		$rows++;

		&print_upload_history_mapping_all_list_tail() if($rows%50==1 && $rows>1);
		&print_upload_history_mapping_all_list_head(\@HEADER) if($rows%50==1);

		$art_data_size = &format_number($art_data_size);
		$art_xmin = &format_number($art_xmin);
		$art_xmax = &format_number($art_xmax);
		$art_ymin = &format_number($art_ymin);
		$art_ymax = &format_number($art_ymax);
		$art_zmin = &format_number($art_zmin);
		$art_zmax = &format_number($art_zmax);
		$art_volume = &format_number($art_volume);

		my $html =<<HTML;
<tr>
<td class="row_number">$rows</td>
<td class="art_id">$art_id</td>
<td class="art_name">$art_name$art_ext</td>
<td class="art_data_size number">$art_data_size</td>
<td class="art_xmin number">$art_xmin</td>
<td class="art_xmax number">$art_xmax</td>
<td class="art_ymin number">$art_ymin</td>
<td class="art_ymax number">$art_ymax</td>
<td class="art_zmin number">$art_zmin</td>
<td class="art_zmax number">$art_zmax</td>
<td class="art_volume number">$art_volume</td>
HTML

		foreach my $header (@HEADER){
			$sth_cm->execute($header->{'mv_id'},$art_id) or die $dbh->errstr;

			my $cdi_name;
			my $cdi_name_e;
			my $cdi_syn_e;
			my $cmp_id;
			my $cmp_abbr;
			my $column_number = 0;
			$sth_cm->bind_col(++$column_number, \$cdi_name,   undef);
			$sth_cm->bind_col(++$column_number, \$cdi_name_e,   undef);
			$sth_cm->bind_col(++$column_number, \$cdi_syn_e,   undef);
			$sth_cm->bind_col(++$column_number, \$cmp_id,   undef);
			$sth_cm->bind_col(++$column_number, \$cmp_abbr,   undef);
			$sth_cm->fetch;
			$sth_cm->finish;
			$cdi_name = '' unless(defined $cdi_name && length $cdi_name);

			$cmp_id = 0 unless(defined $cmp_id);
			$cmp_id -= 0;
			if($cmp_id){
				$cdi_name = sprintf('%s-%s', $cdi_name, $cmp_abbr);
				$cdi_name_e = sprintf('[<span>%s</span>] %s', $cmp_abbr, $cdi_name_e);
			}

			$html .=<<HTML;
<td class="cdi_name">$cdi_name</td>
HTML
		}

		$html .=<<HTML;
</tr>
HTML

		&utf8::encode($html) if(&utf8::is_utf8($html));
		print $html;
	}

	&print_upload_history_mapping_all_list_tail();

	print <<HTML;
</body>
</html>
HTML

	$sth_art->finish;
	undef $sth_art;
}

sub getFMAHistoryMappingAllList {
	my $dbh = shift;
	my $FORM = shift;

	my $ci_id = $FORM->{'ci_id'};
	my $md_id = $FORM->{'md_id'};
	my $title = $FORM->{'title'};

	my $mv_filter = '';
	my $mv_ids = exists $FORM->{'mv_ids'} && defined $FORM->{'mv_ids'} ? &cgi_lib::common::decodeJSON($FORM->{'mv_ids'}) : [];
	if(defined $mv_ids && ref $mv_ids eq 'ARRAY' && scalar @$mv_ids){
		my @mvs = map {$_->{'mv_id'}} grep {defined $_ && ref $_ eq 'HASH' && exists $_->{'mv_id'} && defined $_->{'mv_id'} && $_->{'mv_id'} =~ /^[0-9]+$/} @$mv_ids;
		if(scalar @mvs){
			$mv_filter = ' and mv_id in ('.join(',',@mvs).')';
		}
	}

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
tr>td {
	vertical-align: top;
}
tr.head>td {
	text-align: center;
	vertical-align: middle;
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
	display: none;
	width: 44px;
	text-align: right;
	background-color: #cccccc;
	-moz-user-select:-moz-none;
	-khtml-user-select:none;
	-webkit-user-select:none;
}
.art_id {
	width: 140px;
	max-width: 140px;
}
.cdi_name {
	width: 70px;
	max-width: 70px;
}
.number {
	text-align: right;
	width: 70px;
	max-width: 70px;
}
.art_data_size {
}
.art_xmin {
	display: none;
}
.art_xmax {
	display: none;
}
.art_ymin {
	display: none;
}
.art_ymax {
	display: none;
}
.art_zmin {
	display: none;
}
.art_zmax {
	display: none;
}
.art_volume {
	display: none;
}
.cdi_name_e>span {
	font-family:Courier,Courier New,monospace;
}
</style>
</head>
HTML
=pod
	my $sql_art=<<SQL;
select
 arti.art_id,
 arti.art_name,
 arti.art_ext,
 art_data_size,
 art_xmin,
 art_xmax,
 art_ymin,
 art_ymax,
 art_zmin,
 art_zmax,
 art_volume
from
 (
   select mv_id,art_id,cdi_id from concept_art_map where (ci_id,cb_id,md_id,mv_id,mr_id,art_id) in (
     select ci_id,cb_id,md_id,mv_id,max(mr_id),art_id from concept_art_map
     where
      ci_id=$ci_id and md_id=$md_id $mv_filter and
      mv_id in (
        select mr.mv_id from model_version as mv
        left join (
           select * from model_revision
         ) as mr on
            mr.md_id=mv.md_id and
            mr.mv_id=mv.mv_id
        where
         mv.md_id=$md_id and
         mv_delcause is null and
         mv_use and
--         mv_publish and
         mr_delcause is null and
         mr_use
        group by mr.mv_id
      )
     group by
      ci_id,cb_id,md_id,mv_id,art_id
   )
   and cm_delcause is null and cm_use
   group by mv_id,art_id,cdi_id
 ) as cm

left join (
   select
    art_id,
    art_serial,
    prefix_id,
    art_data_size,
    art_xmin,
    art_xmax,
    art_ymin,
    art_ymax,
    art_zmin,
    art_zmax,
    art_volume
   from
    art_file
 ) as art on
    art.art_id=cm.art_id

left join (
   select
    art_id,
    art_name,
    art_ext,
    art_timestamp
   from
    art_file_info
 ) as arti on
    arti.art_id=cm.art_id

left join (
   select * from id_prefix
 ) as id_prefix on
    id_prefix.prefix_id=art.prefix_id

where
 cm.mv_id=? and
 cm.cdi_id=?
order by
 id_prefix.prefix_char,
 art.art_serial,
 art.art_id
;
SQL
=cut
	my $sql_art=<<SQL;
select
 arti.art_id,
 arti.art_name,
 arti.art_ext,
 art_data_size,
 art_xmin,
 art_xmax,
 art_ymin,
 art_ymax,
 art_zmin,
 art_zmax,
 art_volume
from
 (
   select
     mv_id,cm.art_id,cdi_id
   from
     concept_art_map as cm

   left join (
      select art_id,art_timestamp::date from history_art_file_info
   ) as afi on afi.art_id=cm.art_id

   where (ci_id,cb_id,md_id,mv_id,mr_id,art_timestamp) in (
     select ci_id,cb_id,md_id,mv_id,max(mr_id),max(art_timestamp) from concept_art_map as cm
     left join (
       select art_id,art_timestamp::date from history_art_file_info
     ) as afi on afi.art_id=cm.art_id
     where
      ci_id=$ci_id and md_id=$md_id $mv_filter and
      mv_id in (
        select mr.mv_id from model_version as mv
        left join (
           select * from model_revision
         ) as mr on
            mr.md_id=mv.md_id and
            mr.mv_id=mv.mv_id
        where
         mv.md_id=$md_id and
         mv_delcause is null and
         mv_use and
--         mv_publish and
         mr_delcause is null and
         mr_use
        group by mr.mv_id
      )
     group by
      ci_id,cb_id,md_id,mv_id,art_timestamp
   )
   and cm_delcause is null and cm_use
   group by mv_id,cm.art_id,cdi_id
 ) as cm

left join (
   select
    art_id,
    art_serial,
    prefix_id,
    art_data_size,
    art_xmin,
    art_xmax,
    art_ymin,
    art_ymax,
    art_zmin,
    art_zmax,
    art_volume
   from
    art_file
 ) as art on
    art.art_id=cm.art_id

left join (
   select
    art_id,
    art_name,
    art_ext,
    art_timestamp
   from
    art_file_info
 ) as arti on
    arti.art_id=cm.art_id

left join (
   select * from id_prefix
 ) as id_prefix on
    id_prefix.prefix_id=art.prefix_id

where
 cm.mv_id=? and
 cm.cdi_id=?
order by
 id_prefix.prefix_char,
 art.art_serial,
 art.art_id
;
SQL
=pod
	my $sql_cm=<<SQL;
select
 cm.cdi_id,
 cdi_name,
 cdi_name_e,
 cdi_syn_e,
 cmp.cmp_id,
 cmp.cmp_abbr
from
 (
   select ci_id,cdi_id,cmp_id from concept_art_map where (ci_id,cb_id,md_id,mv_id,mr_id,art_id) in (
     select ci_id,cb_id,md_id,mv_id,max(mr_id),art_id from concept_art_map where ci_id=$ci_id and md_id=$md_id $mv_filter

     and mv_id in (
        select mr.mv_id from model_version as mv
        left join (
           select * from model_revision
         ) as mr on
            mr.md_id=mv.md_id and
            mr.mv_id=mv.mv_id
        where
         mv.md_id=$md_id and
         mv_delcause is null and
         mv_use and
--         mv_publish and
         mr_delcause is null and
         mr_use
        group by mr.mv_id
      )

     group by ci_id,cb_id,md_id,mv_id,art_id
   )
   and cm_delcause is null and cm_use
   group by
     ci_id,cdi_id,cmp_id
 ) as cm

left join (
   select * from concept_data_info
 ) as cdi on
    cdi.ci_id=cm.ci_id and
    cdi.cdi_id=cm.cdi_id

left join (
   select * from concept_art_map_part
 ) as cmp on
    cmp.cmp_id=cm.cmp_id

order by cdi_name
;
SQL
=cut
	my $sql_cm=<<SQL;
select
 cm.cdi_id,
 cdi_name,
 cdi_name_e,
 cdi_syn_e,
 cmp.cmp_id,
 cmp.cmp_abbr
from
 (
   select
    ci_id,
    cdi_id,
    cmp_id
   from
    concept_art_map as cm

   left join (
      select art_id,art_timestamp::date from history_art_file_info
   ) as afi on afi.art_id=cm.art_id

   where (ci_id,cb_id,md_id,mv_id,mr_id,art_timestamp) in (
     select ci_id,cb_id,md_id,mv_id,max(mr_id),max(art_timestamp) from concept_art_map as cm
     left join (
       select art_id,art_timestamp::date from history_art_file_info
     ) as afi on afi.art_id=cm.art_id
     where
      ci_id=$ci_id and md_id=$md_id $mv_filter and
      mv_id in (
        select mr.mv_id from model_version as mv
        left join (
           select * from model_revision
         ) as mr on
            mr.md_id=mv.md_id and
            mr.mv_id=mv.mv_id
        where
         mv.md_id=$md_id and
         mv_delcause is null and
         mv_use and
--         mv_publish and
         mr_delcause is null and
         mr_use
        group by mr.mv_id
      )
     group by
      ci_id,cb_id,md_id,mv_id,art_timestamp

   )
   and cm_delcause is null and cm_use
   group by
     ci_id,cdi_id,cmp_id
 ) as cm

left join (
   select * from concept_data_info
 ) as cdi on
    cdi.ci_id=cm.ci_id and
    cdi.cdi_id=cm.cdi_id

left join (
   select * from concept_art_map_part
 ) as cmp on
    cmp.cmp_id=cm.cmp_id

order by cdi_name
;
SQL

	my $sql_header=<<SQL;
select
 mv.mv_id,
 mv_name_e,
 to_char(mr_entry,'YYYY/MM/DD'),
 to_char(hist_timestamp,'YYYY/MM/DD')
from
 (select * from model_version where (md_id,mv_id) in (
   select
    md_id,min(mv_id)
   from
    model_version
   where
    mv_delcause is null and
    mv_use and
--    mv_publish and
    md_id=$md_id $mv_filter
   group by
    md_id,mv_objects_set
 )) as mv

left join (
   select md_id,mv_id,max(mr_entry) as mr_entry from model_revision where mr_delcause is null and mr_use group by md_id,mv_id
 ) as mr on
    mr.md_id=mv.md_id and
    mr.mv_id=mv.mv_id

left join (
   select md_id,mv_id,max(hist_timestamp) as hist_timestamp from history_concept_art_map group by md_id,mv_id
 ) as hcm on
    hcm.md_id=mv.md_id and
    hcm.mv_id=mv.mv_id

left join (
   select md_id,mv_id,count(*) as num from concept_art_map where (ci_id,cb_id,md_id,mv_id,mr_id,art_id) in (
     select ci_id,cb_id,md_id,mv_id,max(mr_id),art_id from concept_art_map where ci_id=$ci_id and md_id=$md_id

     and mv_id in (
        select mr.mv_id from model_version as mv
        left join (
           select * from model_revision
         ) as mr on
            mr.md_id=mv.md_id and
            mr.mv_id=mv.mv_id
        where
         mv.md_id=$md_id and
         mv_delcause is null and
         mv_use and
--         mv_publish and
         mr_delcause is null and
         mr_use
        group by mr.mv_id
      )

     group by ci_id,cb_id,md_id,mv_id,art_id
   )
   and cm_delcause is null and cm_use
   group by
     md_id,mv_id
 ) as cm on
    cm.md_id=mv.md_id and
    cm.mv_id=mv.mv_id

where
 COALESCE(cm.num,0)>0
order by
 mr_entry,
 hist_timestamp
;
SQL

	my $sth_art = $dbh->prepare($sql_art) or die $dbh->errstr;


	my $sth_cm = $dbh->prepare($sql_cm) or die $dbh->errstr;
	$sth_cm->execute() or die $dbh->errstr;
	my $cdi_id;
	my $cdi_name;
	my $cdi_name_e;
	my $cdi_syn_e;
	my $cmp_id;
	my $cmp_abbr;
	my $column_number = 0;
	$sth_cm->bind_col(++$column_number, \$cdi_id,   undef);
	$sth_cm->bind_col(++$column_number, \$cdi_name,   undef);
	$sth_cm->bind_col(++$column_number, \$cdi_name_e,   undef);
	$sth_cm->bind_col(++$column_number, \$cdi_syn_e,   undef);
	$sth_cm->bind_col(++$column_number, \$cmp_id,   undef);
	$sth_cm->bind_col(++$column_number, \$cmp_abbr,   undef);

	print <<HTML;
<body>
HTML


	my @HEADER;
	my $sth_header = $dbh->prepare($sql_header) or die $dbh->errstr;
	$sth_header->execute() or die $dbh->errstr;
	my $h_mv_id;
	my $h_mv_name_e;
	my $h_mr_entry;
	my $h_hist_timestamp;
	$column_number = 0;
	$sth_header->bind_col(++$column_number, \$h_mv_id,   undef);
	$sth_header->bind_col(++$column_number, \$h_mv_name_e,   undef);
	$sth_header->bind_col(++$column_number, \$h_mr_entry,   undef);
	$sth_header->bind_col(++$column_number, \$h_hist_timestamp,   undef);
	while($sth_header->fetch){
		push(@HEADER,{
			mv_id => $h_mv_id,
			mv_name_e => $h_mv_name_e,
			mr_entry => $h_mr_entry,
			hist_timestamp => $h_hist_timestamp,
		});
	}
	$sth_header->finish;
	undef $sth_header;

	sub print_fma_history_mapping_all_list_head {
		my $HEADER = shift;

		print <<HTML;
<table border=1>
<thead>
<tr class="head">
<td class="row_number">#</td>
<td class="cdi_name">FMAID</td>
<td class="cdi_name_e">Name</td>
HTML

		foreach my $header (@$HEADER){
			print <<HTML;
<td class="art_id">$header->{mv_name_e}<br>FJID</td>
HTML
		}

		print <<HTML;
</tr>
</thead>
<tbody>
HTML
	}

	sub print_fma_history_mapping_all_list_tail {
		print <<HTML;
</tbody>
</table>
HTML
	}

	my $rows = 0;

	while($sth_cm->fetch){
		next unless(defined $cdi_id);


		$rows++;

		&print_fma_history_mapping_all_list_tail() if($rows%50==1 && $rows>1);
		&print_fma_history_mapping_all_list_head(\@HEADER) if($rows%50==1);

		$cdi_name = '' unless(defined $cdi_name && length $cdi_name);

		$cmp_id = 0 unless(defined $cmp_id);
		$cmp_id -= 0;
		if($cmp_id){
			$cdi_name = sprintf('%s-%s', $cdi_name, $cmp_abbr);
			$cdi_name_e = sprintf('[<span>%s</span>] %s', $cmp_abbr, $cdi_name_e);
		}

		my $html =<<HTML;
<tr>
<td class="row_number">$rows</td>
<td class="cdi_name">$cdi_name</td>
<td class="cdi_name_e">$cdi_name_e</td>
HTML

		foreach my $header (@HEADER){

			$sth_art->execute($header->{'mv_id'},$cdi_id) or die $dbh->errstr;
			my $art_id;
			my $art_name;
			my $art_ext;
			my $art_data_size;
			my $art_xmin;
			my $art_xmax;
			my $art_ymin;
			my $art_ymax;
			my $art_zmin;
			my $art_zmax;
			my $art_volume;
			my @ART_IDS;

			my $column_number = 0;
			$sth_art->bind_col(++$column_number, \$art_id,   undef);
			$sth_art->bind_col(++$column_number, \$art_name,   undef);
			$sth_art->bind_col(++$column_number, \$art_ext,   undef);
			$sth_art->bind_col(++$column_number, \$art_data_size,   undef);
			$sth_art->bind_col(++$column_number, \$art_xmin,   undef);
			$sth_art->bind_col(++$column_number, \$art_xmax,   undef);
			$sth_art->bind_col(++$column_number, \$art_ymin,   undef);
			$sth_art->bind_col(++$column_number, \$art_ymax,   undef);
			$sth_art->bind_col(++$column_number, \$art_zmin,   undef);
			$sth_art->bind_col(++$column_number, \$art_zmax,   undef);
			$sth_art->bind_col(++$column_number, \$art_volume,   undef);
			while($sth_art->fetch){
				$art_data_size = &format_number($art_data_size);
				$art_xmin = &format_number($art_xmin);
				$art_xmax = &format_number($art_xmax);
				$art_ymin = &format_number($art_ymin);
				$art_ymax = &format_number($art_ymax);
				$art_zmin = &format_number($art_zmin);
				$art_zmax = &format_number($art_zmax);
				$art_volume = &format_number($art_volume);
				push(@ART_IDS,$art_id);
			}
			$sth_art->finish;
			$art_id = join(', ',@ART_IDS);

			$html .=<<HTML;
<td class="art_id">$art_id</td>
HTML
		}

		$html .=<<HTML;
</tr>
HTML

		&utf8::encode($html) if(&utf8::is_utf8($html));
		print $html;
	}

	&print_fma_history_mapping_all_list_tail();

	print <<HTML;
</body>
</html>
HTML

	$sth_art->finish;
	undef $sth_art;
}
