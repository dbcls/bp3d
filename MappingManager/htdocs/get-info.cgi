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
use File::Spec::Functions qw(abs2rel rel2abs catdir catfile splitdir);

use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'..','cgi_lib');

use BITS::ConceptArtMapModified;

require "webgl_common.pl";
use cgi_lib::common;

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);
my($logfile,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
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

#&setDefParams(\%FORM,\%COOKIE);
#&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM,1),$LOG);
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

my $ci_id=$FORM{'ci_id'};
my $cb_id=$FORM{'cb_id'};
my $md_id=$FORM{'md_id'};
my $mv_id=$FORM{'mv_id'};

$md_id=1 unless(defined $md_id && $md_id =~ /^[1-9][0-9]*$/);
unless(defined $mv_id && $mv_id =~ /^[1-9][0-9]*$/){
	$mv_id = undef;
	$ci_id = undef;
	$cb_id = undef;
	my $sth_mv;
	if(defined $FORM{'mv_id'} && $FORM{'mv_id'} =~ /^\-[1-9][0-9]*$/){
		$sth_mv = $dbh->prepare("select mv_id from model_version where mv_delcause is null and mv_use and md_id=? order by mv_id desc limit 2") or die $dbh->errstr;
		$sth_mv->execute($md_id) or die $dbh->errstr;
		if($sth_mv->rows()>1){
			$sth_mv->bind_col(1, \$mv_id, undef);
			while($sth_mv->fetch){}
		}
		$sth_mv->finish;
		undef $sth_mv;
	}else{
		$sth_mv = $dbh->prepare("select max(mv_id) from model_version where mv_delcause is null and mv_use and md_id=?") or die $dbh->errstr;
		$sth_mv->execute($md_id) or die $dbh->errstr;
		$sth_mv->bind_col(1, \$mv_id, undef);
		$sth_mv->fetch;
		$sth_mv->finish;
		undef $sth_mv;
	}
	if(defined $mv_id){
		$sth_mv = $dbh->prepare("select ci_id,cb_id from model_version where md_id=? and mv_id=?") or die $dbh->errstr;
		$sth_mv->execute($md_id,$mv_id) or die $dbh->errstr;
		$sth_mv->bind_col(1, \$ci_id, undef);
		$sth_mv->bind_col(2, \$cb_id, undef);
		$sth_mv->fetch;
		$sth_mv->finish;
		undef $sth_mv;
	}
}

unless(defined $ci_id && defined $cb_id && defined $md_id && defined $mv_id){
	$DATAS->{'success'} = JSON::XS::true;
	&cgi_lib::common::printContentJSON($DATAS,\%FORM);
	close($LOG) if(defined $LOG);
	exit;
}
if(defined $LOG){
	&cgi_lib::common::message('$md_id='.$md_id, $LOG);
	&cgi_lib::common::message('$mv_id='.$mv_id, $LOG);
	&cgi_lib::common::message('$ci_id='.$ci_id, $LOG);
	&cgi_lib::common::message('$cb_id='.$cb_id, $LOG);
}
$FORM{'ci_id'}=$ci_id;
$FORM{'cb_id'}=$cb_id;
$FORM{'md_id'}=$md_id;
$FORM{'mv_id'}=$mv_id;

if(defined $FORM{'cmd'}){
	if($FORM{'cmd'} eq 'tree-path' && exists $FORM{'params'} && defined $FORM{'params'}){

	}elsif($FORM{'cmd'} eq 'history-mapping' && ((exists $FORM{'cdi_name'} && defined $FORM{'cdi_name'}) || (exists $FORM{'art_id'} && defined $FORM{'art_id'}))){
		&getHistoryMapping($dbh,\%FORM,$DATAS);

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

	}elsif($FORM{'cmd'} eq 'export-concept-art-map'){
		&exportConceptArtMap($dbh,\%FORM);
		exit;

	}
}
#print qq|Content-type: text/html; charset=UTF-8\n\n|;
#print &JSON::XS::encode_json($DATAS);
&cgi_lib::common::message($DATAS, $LOG) if(defined $LOG);
&gzip_json($DATAS);

close($LOG);

exit;

sub getTreePath {
}

sub getHistoryMapping {
	my $dbh = shift;
	my $FORM = shift;
	my $DATAS = shift;

	my $sql =<<SQL;
select
 hcm.art_id,

 afi.art_name,
 afi.art_ext,

 EXTRACT(EPOCH FROM afi.art_timestamp) as art_timestamp,
 EXTRACT(EPOCH FROM art.art_modified) as art_upload_modified,
 afi.art_data_size,
 afi.art_xmin,
 afi.art_xmax,
 afi.art_ymin,
 afi.art_ymax,
 afi.art_zmin,
 afi.art_zmax,
 to_number(to_char((afi.art_xmax+afi.art_xmin)/2,'FM99990D0000'),'99990D0000S') as art_xcenter,
 to_number(to_char((afi.art_ymax+afi.art_ymin)/2,'FM99990D0000'),'99990D0000S') as art_ycenter,
 to_number(to_char((afi.art_zmax+afi.art_zmin)/2,'FM99990D0000'),'99990D0000S') as art_zcenter,
 afi.art_volume,

 hcm.cdi_id,

 cdi.cdi_name,
 COALESCE(cd.cd_name,cdi.cdi_name_e),

 hcm.cm_comment,
 hcm.cm_delcause,
 hcm.cmp_id,
 EXTRACT(EPOCH FROM hcm.cm_entry),

 hcm.hist_event,
 he.he_name,

 hist_serial,
 EXTRACT(EPOCH FROM hist_timestamp)

from
 history_concept_art_map as hcm

LEFT JOIN (
  select * from concept_data_info
) AS cdi ON
   cdi.ci_id=hcm.ci_id AND
   cdi.cdi_id=hcm.cdi_id

LEFT JOIN (
  select * from concept_data
) AS cd ON
   cd.ci_id=hcm.ci_id AND
   cd.cb_id=hcm.cb_id AND
   cd.cdi_id=hcm.cdi_id

LEFT JOIN (
  select * from history_event
) AS he ON
   he.he_id=hcm.hist_event

LEFT JOIN (
  select * from art_file_info
) AS afi ON
   afi.art_id=hcm.art_id

left join (
  select
   art_id,
   art_modified
  from
   art_file
 ) as art on
   afi.art_id=art.art_id

where
SQL

	if(exists $FORM->{'cdi_name'} && defined $FORM->{'cdi_name'}){
		$sql .= qq|cdi.cdi_name=?|;
	}
	elsif(exists $FORM->{'art_id'} && defined $FORM->{'art_id'}){
		$sql .= qq|hcm.art_id=?|;
	}


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
	if(exists $FORM->{'cdi_name'} && defined $FORM->{'cdi_name'}){
		$sth->execute($FORM->{'cdi_name'}) or die $dbh->errstr;
	}
	elsif(exists $FORM->{'art_id'} && defined $FORM->{'art_id'}){
		$sth->execute($FORM->{'art_id'}) or die $dbh->errstr;
	}
	$DATAS->{'total'} = $sth->rows();

		my $art_id;
		my $art_name;
		my $art_ext;

		my $art_timestamp;
		my $art_upload_modified;
		my $art_data_size;
		my $art_xmin;
		my $art_xmax;
		my $art_ymin;
		my $art_ymax;
		my $art_zmin;
		my $art_zmax;
		my $art_xcenter;
		my $art_ycenter;
		my $art_zcenter;
		my $art_volume;

		my $ci_id;

		my $cdi_id;
		my $cdi_name;
		my $cdi_name_j;
		my $cdi_name_e;
		my $cdi_name_k;
		my $cdi_name_l;

#		my $cm_id;
		my $cm_comment;
		my $cm_delcause;
		my $cm_openid;
		my $cmp_id;
		my $cm_entry;

		my $hist_event;
		my $he_name;

		my $hist_serial;
		my $hist_timestamp;

		my $column_number = 0;
		$sth->bind_col(++$column_number, \$art_id,   undef);

		$sth->bind_col(++$column_number, \$art_name,   undef);
		$sth->bind_col(++$column_number, \$art_ext,   undef);

		$sth->bind_col(++$column_number, \$art_timestamp, undef);
		$sth->bind_col(++$column_number, \$art_upload_modified, undef);
		$sth->bind_col(++$column_number, \$art_data_size, undef);
		$sth->bind_col(++$column_number, \$art_xmin, undef);
		$sth->bind_col(++$column_number, \$art_xmax, undef);
		$sth->bind_col(++$column_number, \$art_ymin, undef);
		$sth->bind_col(++$column_number, \$art_ymax, undef);
		$sth->bind_col(++$column_number, \$art_zmin, undef);
		$sth->bind_col(++$column_number, \$art_zmax, undef);
		$sth->bind_col(++$column_number, \$art_xcenter, undef);
		$sth->bind_col(++$column_number, \$art_ycenter, undef);
		$sth->bind_col(++$column_number, \$art_zcenter, undef);
		$sth->bind_col(++$column_number, \$art_volume, undef);

#		$sth->bind_col(++$column_number, \$ci_id,   undef);

		$sth->bind_col(++$column_number, \$cdi_id,   undef);
		$sth->bind_col(++$column_number, \$cdi_name,   undef);
#		$sth->bind_col(++$column_number, \$cdi_name_j,   undef);
		$sth->bind_col(++$column_number, \$cdi_name_e,   undef);
#		$sth->bind_col(++$column_number, \$cdi_name_k,   undef);
#		$sth->bind_col(++$column_number, \$cdi_name_l,   undef);

#		$sth->bind_col(++$column_number, \$cm_id,   undef);
		$sth->bind_col(++$column_number, \$cm_comment,   undef);
		$sth->bind_col(++$column_number, \$cm_delcause,   undef);
#		$sth->bind_col(++$column_number, \$cm_openid,   undef);
		$sth->bind_col(++$column_number, \$cmp_id,   undef);
		$sth->bind_col(++$column_number, \$cm_entry,   undef);

		$sth->bind_col(++$column_number, \$hist_event,   undef);
		$sth->bind_col(++$column_number, \$he_name,   undef);

		$sth->bind_col(++$column_number, \$hist_serial,   undef);
		$sth->bind_col(++$column_number, \$hist_timestamp,   undef);


		umask(0);
		my $art_abs_path = &catdir($FindBin::Bin,'art_file');
		&File::Path::mkpath($art_abs_path,{mode=>0777}) unless(-e $art_abs_path);

		while($sth->fetch){

			my $file_name = $art_name;
			$file_name .= $art_ext unless($art_name =~ /$art_ext$/);
			my $file_path = &catfile($art_abs_path,qq|$art_id$art_ext|);

			my $img_prefix;
			my $img_path;
			my $img_info;
			my $thumbnail_path;
			my $img_size = [undef,undef,undef,[16,16]];
			unless(defined $thumbnail_path && -e $thumbnail_path && -f $thumbnail_path && -s $thumbnail_path){
				($img_prefix,$img_path) = &getObjImagePrefix($art_id);
				$img_info = &getImageFileList($img_prefix, $img_size);
				$thumbnail_path = sprintf($img_info->{'gif_fmt'},$img_prefix,$img_info->{'sizeStrXS'});
			}
			if(-e $thumbnail_path && -f $thumbnail_path && -s $thumbnail_path){
				$thumbnail_path = sprintf(qq|<img align=center width=16 height=16 src="%s?%s">|,&abs2rel($thumbnail_path,$FindBin::Bin),(stat($thumbnail_path))[9]);
			}else{
				$thumbnail_path = undef;
			}


			push(@{$DATAS->{'datas'}},{

				art_id => $art_id,
				art_name       => $art_name,
				art_filename   => qq|$art_name$art_ext|,
				art_path       => &abs2rel($file_path,$FindBin::Bin),
				art_tmb_path   => $thumbnail_path,

				art_timestamp   => defined $art_timestamp ? $art_timestamp + 0 : undef,
				art_upload_modified   => defined $art_upload_modified ? $art_upload_modified + 0 : undef,
				art_data_size   => defined $art_data_size ? $art_data_size + 0 : undef,

				art_xmin       => defined $art_xmin ? $art_xmin + 0 : undef,
				art_xmax       => defined $art_xmax ? $art_xmax + 0 : undef,
				art_ymin       => defined $art_ymin ? $art_ymin + 0 : undef,
				art_ymax       => defined $art_ymax ? $art_ymax + 0 : undef,
				art_zmin       => defined $art_zmin ? $art_zmin + 0 : undef,
				art_zmax       => defined $art_zmax ? $art_zmax + 0 : undef,

				art_xcenter    => defined $art_xcenter ? $art_xcenter + 0 : undef,
				art_ycenter    => defined $art_ycenter ? $art_ycenter + 0 : undef,
				art_zcenter    => defined $art_zcenter ? $art_zcenter + 0 : undef,

				art_volume     => defined $art_volume ? $art_volume + 0 : undef,

#				ci_id => $ci_id,

				cdi_id => $cdi_id,
				cdi_name => $cdi_name,
#				cdi_name_j => $cdi_name_j,
				cdi_name_e => $cdi_name_e,
#				cdi_name_k => $cdi_name_k,
#				cdi_name_l => $cdi_name_l,

#				cm_id => $cm_id,
				cm_comment => $cm_comment,
#				cm_openid => $cm_openid,
				cmp_id => $cmp_id,
				cm_entry => $cm_entry * 1000,

				hist_event => $hist_event,
				he_name => $he_name,

				hist_serial => $hist_serial,
#				hist_timestamp => $hist_timestamp - 0,
				hist_timestamp => $hist_timestamp * 1000,


			});
		}
		$sth->finish;
		undef $sth;

	$DATAS->{'success'}  = JSON::XS::true;

}

sub outputUploadAllList {
	my $dbh = shift;
	my $FORM = shift;

	my $ci_id = $FORM->{'ci_id'};
	my $title = $FORM->{'title'};

	my $md_id=$FORM{'md_id'};
	my $mv_id=$FORM{'mv_id'};
	$md_id=1 unless(defined $md_id && $md_id =~ /^[0-9]+$/);
	unless(defined $mv_id && $mv_id =~ /^[0-9]+$/){
		my $sth_mv = $dbh->prepare("select max(mv_id) from model_version where mv_delcause is null and mv_use and md_id=?") or die $dbh->errstr;
		$sth_mv->execute($md_id) or die $dbh->errstr;
		$sth_mv->bind_col(1, \$mv_id, undef);
		$sth_mv->fetch;
		$sth_mv->finish;
		undef $sth_mv;
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
	width: 76px;
	max-width: 76px;
	white-space: nowrap;
}
.cdi_name_e>span {
	font-family:Courier,Courier New,monospace;
}
tbody .cdi_syn_e {
	padding-left: 20px;
}
td.cdi_syn_e div {
	display: list-item;
}
.art_data_size {
	width: 70px;
	max-width: 70px;
}
tbody .artf_name {
	padding-left: 20px;
}
td.artf_name div {
	display: list-item;
}

</style>
</head>
HTML

	my $sql=<<SQL;
select
 arti.art_id,
 arti.art_name,
 arti.art_ext,
 cdi_name,
 cdi_name_e,
 cdi_syn_e,
 art_data_size,
 length(cmp.cmp_abbr),
 cmp.cmp_abbr
from
 art_file_info as arti

left join (
   select
    art_id,
    prefix_id,
    art_serial
   from
     art_file
 ) as art on
    art.art_id=arti.art_id

left join (
   select
    *
   from
     concept_art_map
   where
    cm_delcause is null and
    md_id=$md_id and
    mv_id=$mv_id
 ) as map on
    map.art_id=arti.art_id

left join (
   select * from concept_art_map_part where cmp_delcause is null
 ) as cmp on
    cmp.cmp_id=map.cmp_id
 
left join (
   select * from concept_data_info
 ) as cdi on
    cdi.ci_id=map.ci_id and
    cdi.cdi_id=map.cdi_id

where
 art_delcause is null

order by
 art.prefix_id,
 art.art_serial,
 arti.art_id
SQL

	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	my $art_id;
	my $art_name;
	my $art_ext;
	my $cdi_name;
	my $cdi_name_e;
	my $cdi_syn_e;
	my $art_data_size;
	my $cmp_id;
	my $cmp_abbr;


	my $column_number = 0;
	$sth->bind_col(++$column_number, \$art_id,   undef);
	$sth->bind_col(++$column_number, \$art_name,   undef);
	$sth->bind_col(++$column_number, \$art_ext,   undef);
	$sth->bind_col(++$column_number, \$cdi_name,   undef);
	$sth->bind_col(++$column_number, \$cdi_name_e,   undef);
	$sth->bind_col(++$column_number, \$cdi_syn_e,   undef);
	$sth->bind_col(++$column_number, \$art_data_size,   undef);
	$sth->bind_col(++$column_number, \$cmp_id,   undef);
	$sth->bind_col(++$column_number, \$cmp_abbr,   undef);

	my $sth_art_folder_file = $dbh->prepare(qq|select aff.artf_id,af.artf_name from art_folder_file as aff left join (select * from art_folder) as af on af.artf_id=aff.artf_id where aff.art_id=?|) or die $dbh->errstr;
	my $sth_art_folder = $dbh->prepare(qq|select paf.artf_id,paf.artf_name from art_folder as af left join (select artf_id,artf_name from art_folder where artf_delcause is null) paf on paf.artf_id=af.artf_pid where af.artf_delcause is null and af.artf_id=?|) or die $dbh->errstr;

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
<td class="cdi_name">FMA ID</td>
<td class="cdi_name_e">FMA Name</td>
<td class="cdi_syn_e">FMA Synonym</td>
<td class="art_name">objファイル名</td>
<td class="art_data_size">File Size</td>
<td class="artf_name">Folder</td>
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

		$rows++;

		&print_upload_all_list_tail() if($rows%50==1 && $rows>1);
		&print_upload_all_list_head() if($rows%50==1);

		if(defined $cdi_syn_e){
#			$cdi_syn_e =~ s/(;)/$1<br>/g;
			$cdi_syn_e = '<div>'.join('</div><div>',split(/;/,$cdi_syn_e)).'</div>';
		}else{
			$cdi_syn_e = '';
		}
		if(defined $art_data_size){
			$art_data_size = &format_number($art_data_size);
#			$art_data_size = &format_bytes($art_data_size, unit => 'K');
		}

		$cdi_name = '' unless(defined $cdi_name);
		$cdi_name_e = '' unless(defined $cdi_name_e);

		$cmp_id = 0 unless(defined $cmp_id);
		$cmp_id -= 0;
		if($cmp_id){
			$cdi_name = sprintf('%s-%s', $cdi_name, $cmp_abbr);
			$cdi_name_e = sprintf('[<span>%s</span>] %s', $cmp_abbr, $cdi_name_e);
		}

		my @all_artf_names = ();
		$sth_art_folder_file->execute($art_id) or die $dbh->errstr;
		my $artf_id;
		my $artf_name;
		my $column_number = 0;
		$sth_art_folder_file->bind_col(++$column_number, \$artf_id,   undef);
		$sth_art_folder_file->bind_col(++$column_number, \$artf_name,   undef);
		while($sth_art_folder_file->fetch){
			my @artf_names = ();
			if(defined $artf_name){
				unshift @artf_names, $artf_name;
				my $temp_artf_pid = $artf_id;
				do{
					my $temp_artf_pname;
					$sth_art_folder->execute($temp_artf_pid) or die $dbh->errstr;
					$sth_art_folder->bind_col(1, \$temp_artf_pid, undef);
					$sth_art_folder->bind_col(2, \$temp_artf_pname, undef);
					$sth_art_folder->fetch;
					$sth_art_folder->finish;
					unshift(@artf_names,$temp_artf_pname) if(defined $temp_artf_pname);
				}while(defined $temp_artf_pid);
			}
			push(@all_artf_names, '/'.join('/',@artf_names));
		}
		$sth_art_folder_file->finish;

		$artf_name = '<div>'.join('</div><div>',sort {length $a <=> length $b} sort @all_artf_names).'</div>';

		my $html =<<HTML;
<tr>
<td class="row_number">$rows</td>
<td class="art_id">$art_id</td>
<td class="cdi_name">$cdi_name</td>
<td class="cdi_name_e">$cdi_name_e</td>
<td class="cdi_syn_e">$cdi_syn_e</td>
<td class="art_name">$art_name$art_ext</td>
<td class="art_data_size" align="right">$art_data_size</td>
<td class="artf_name">$artf_name</td>
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

	my $ci_id = $FORM->{'ci_id'};

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
	if($ENV{'HTTP_USER_AGENT'}=~/Windows/){
		$LF = "\r\n";
		$CODE = "shiftjis";
	}elsif($ENV{'HTTP_USER_AGENT'}=~/Macintosh/){
		$LF = "\r";
		$CODE = "shiftjis";
	}

	my $sql=<<SQL;
select
 arti.art_id,
 arti.art_name,
 arti.art_ext,
 cdi_name,
 cdi_name_e,
 cdi_syn_e,
 to_char(arti.art_timestamp,'YYYY/MM/DD HH24:MI:SS'),
 arti.art_comment,
 arti.art_category,
 arti.art_judge,
 arti.art_class,

 arti.art_xmin,
 arti.art_xmax,
 arti.art_ymin,
 arti.art_ymax,
 arti.art_zmin,
 arti.art_zmax,
 arti.art_volume,
 arti.art_data_size,

 length(cmp.cmp_abbr),
 cmp.cmp_abbr

from
 art_file_info as arti


left join (
   select
    *
   from
     concept_art_map
   where
    cm_delcause is null and
    ci_id=$ci_id
 ) as map on
    map.art_id=arti.art_id

left join (
   select * from concept_art_map_part where cmp_delcause is null
 ) as cmp on
    cmp.cmp_id=map.cmp_id

left join (
   select * from concept_data_info
 ) as cdi on
    cdi.ci_id=map.ci_id and
    cdi.cdi_id=map.cdi_id

order by
 arti.prefix_id,
 arti.art_serial,
 arti.art_id
SQL

	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	my $art_id;
	my $art_name;
	my $art_ext;
	my $cdi_name;
	my $cdi_name_e;
	my $cdi_syn_e;

	my $art_timestamp;
	my $art_comment;
	my $art_category;
	my $art_judge;
	my $art_class;

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
	$sth->bind_col(++$column_number, \$cdi_name,   undef);
	$sth->bind_col(++$column_number, \$cdi_name_e,   undef);
	$sth->bind_col(++$column_number, \$cdi_syn_e,   undef);

	$sth->bind_col(++$column_number, \$art_timestamp,   undef);
	$sth->bind_col(++$column_number, \$art_comment,   undef);
	$sth->bind_col(++$column_number, \$art_category,   undef);
	$sth->bind_col(++$column_number, \$art_judge,   undef);
	$sth->bind_col(++$column_number, \$art_class,   undef);

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

#	my $header = qq|#FJID	BPID	Use_Map	isMirroring	FMA_ID	FMA_Name	FMA_Synonym	OBJ_Filename	OBJ_Group	OBJ_Timestamp	Comment	Category	Judge	Class	Xmin	Xmax	Ymin	Ymax	Zmin	Zmax	Volume	Size|;
	my $header = qq|#FJID	FMA_ID	FMA_Name	FMA_Synonym	OBJ_Filename	OBJ_Timestamp	Comment	Category	Judge	Class	Xmin	Xmax	Ymin	Ymax	Zmin	Zmax	Volume	Size|;
	&utf8::decode($header) unless(&utf8::is_utf8($header));

	($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime();
	my $timestamp = sprintf("%04d/%02d/%02d %02d:%02d:%02d", $year+1900,$month+1,$mday,$hour,$min,$sec);

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

			$worksheet->write( $y, $x++, $cdi_name,   $uni_format );
			$worksheet->write( $y, $x++, $cdi_name_e, $uni_format );
			$worksheet->write( $y, $x++, $cdi_syn_e,  $uni_format );
			$worksheet->write( $y, $x++, qq|$art_name$art_ext|, $uni_format );

			$worksheet->write( $y, $x++, $art_timestamp, $uni_format );
			$worksheet->write( $y, $x++, $art_comment,   $uni_format );
			$worksheet->write( $y, $x++, $art_category,  $uni_format );
			$worksheet->write( $y, $x++, $art_judge,     $uni_format );
			$worksheet->write( $y, $x++, $art_class,     $uni_format );

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
			push(@t,$cdi_name);
			push(@t,$cdi_name_e);
			push(@t,$cdi_syn_e);
			push(@t,qq|$art_name$art_ext|);

			push(@t,$art_timestamp);
			push(@t,$art_comment);
			push(@t,$art_category);
			push(@t,$art_judge);
			push(@t,$art_class);

			push(@t,$art_xmin);
			push(@t,$art_xmax);
			push(@t,$art_ymin);
			push(@t,$art_ymax);
			push(@t,$art_zmin);
			push(@t,$art_zmax);
			push(@t,$art_volume);
			push(@t,$art_data_size);

			my $o = join("\t",map {defined $_ ? $_ : ''} @t);
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

	my $md_id=$FORM{'md_id'};
	my $mv_id=$FORM{'mv_id'};
	$md_id=1 unless(defined $md_id && $md_id =~ /^[0-9]+$/);
	unless(defined $mv_id && $mv_id =~ /^[0-9]+$/){
		my $sth_mv = $dbh->prepare("select max(mv_id) from model_version where mv_delcause is null and mv_use and md_id=?") or die $dbh->errstr;
		$sth_mv->execute($md_id) or die $dbh->errstr;
		$sth_mv->bind_col(1, \$mv_id, undef);
		$sth_mv->fetch;
		$sth_mv->finish;
		undef $sth_mv;
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
table, .table {
	display: table;
	table-layout: fixed;
	border-collapse: collapse;
	width: 100%;
	margin-bottom: 2px;
	border-width: 1px;
}
.thead {
	display: table-header-group;
}
.tbody {
	display: table-row-group;
}
.tfoot {
	display: table-footer-group;
}
.tr {
	display: table-row;
}
.td,.th {
	display: table-cell;
	border: 1px solid black;
}

.tbody>.tr>.td {
	visibility: visible;
}

tr>td, .tr>.td {
	vertical-align: top;
}
tr.head>td, .tr.head>.td {
	text-align: center;
	font-weight: bold;
	background-color: #cccccc;
	-moz-user-select:-moz-none;
	-khtml-user-select:none;
	-webkit-user-select:none;
}
td, .td {
	padding: 2px;
}
tr:nth-child(odd), .tr:nth-child(odd) {
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
	width: 72px;
	max-width: 72px;
}
.cdi_name_e {
	max-width: 700px;
}
.cdi_syn_e {
	max-width: 654px;
}
tbody .cdi_syn_e, .tbody .cdi_syn_e {
	padding-left: 20px;
}
td.cdi_syn_e div, .td.cdi_syn_e div {
	display: list-item;
}
.cdi_def_e {
	display: none;
}
.art_num {
	width: 70px;
	max-width: 70px;
	text-align: center;
}
.art_ids {
/*
	width: 70px;
	max-width: 300px;
*/
	padding-left: 20px;
}
table.art_ids, .table.art_ids {
	table-layout: auto;
	border-collapse: collapse;
	width: auto;
	margin-bottom: 0;
}
table.art_ids tr:nth-child(odd), .table.art_ids .tr:nth-child(odd) {
	background-color: transparent;
}
table.art_ids td, .table.art_ids .td {
	padding: 0;
	padding-left: 2px;
}
table.art_ids td div, .table.art_ids .td div {
	display: list-item;
}

</style>
</head>
HTML

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
 to_char(cdi.cdi_entry,'YYYY/MM/DD HH24:MI:SS'),
 cm.art_num
from
  concept_data_info as cdi
left join (
  select
   ci_id,
   cdi_id,
   count(art_id) as art_num
  from
   concept_art_map
  where
   cm_delcause is null
  group by
   ci_id,cdi_id
) as cm on
 cdi.ci_id=cm.ci_id and
 cdi.cdi_id=cm.cdi_id
where
 cdi.cdi_delcause is null and
 cdi.ci_id=$ci_id
order by
 cdi_name
-- to_number(substring(cdi_name from 4),'999999')
--limit 100
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
	my $cdi_entry;
	my $art_num;

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
	$sth->bind_col(++$column_number, \$cdi_entry,   undef);
	$sth->bind_col(++$column_number, \$art_num,   undef);

	my $sth_art_num = $dbh->prepare(qq|
select
 cm.art_id,
 art_name,
 art_ext
from
 concept_art_map as cm
left join (
 select art_id,art_name,art_ext from art_file_info
) as arti on cm.art_id=arti.art_id
left join (
 select art_id,prefix_id,art_serial from art_file
) as art on cm.art_id=art.art_id
where
 cm_delcause is null and
 md_id=$md_id and
 mv_id=$mv_id and
 cdi_id=?
order by
 art.prefix_id,
 art.art_serial,
 cm.art_id
|) or die $dbh->errstr;

	print <<HTML;
<body>
HTML

	sub print_table_head {
		print <<HTML;
<table class="" border=1>
	<thead class="">
		<tr class=" head">
			<td class=" row_number">#</td>
			<td class=" cdi_name">ID</td>
			<td class=" cdi_name_e">Name</td>
			<td class=" cdi_syn_e">Synonym</td>
			<td class=" cdi_def_e">Definition</td>
			<td class=" art_num">#FJID</td>
			<td class=" art_ids">FJID</td>
		</tr>
	</thead>
	<tbody class="">
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

#	&print_table_head();

	while($sth->fetch){

		next unless(defined $cdi_name);

		$rows++;

		&print_table_tail() if($rows%50==1 && $rows>1);
		&print_table_head() if($rows%50==1);

		my $art_ids = '';
		if(defined $art_num && $art_num>0){
			$sth_art_num->execute($cdi_id) or die $dbh->errstr;
			$column_number = 0;
			my $art_id;
			my $art_name;
			my $art_ext;
			$sth_art_num->bind_col(++$column_number, \$art_id,   undef);
			$sth_art_num->bind_col(++$column_number, \$art_name,   undef);
			$sth_art_num->bind_col(++$column_number, \$art_ext,   undef);
			my @ART_IDS;
			while($sth_art_num->fetch){
				push(@ART_IDS,qq|<tr class=""><td class=""><div>$art_id</div></td><td class="">:</td><td class="">$art_name$art_ext</td></tr>|);
			}
			$sth_art_num->finish;
			$art_ids = '<table class=" art_ids"><tbody class="">'.join('',@ART_IDS).'</tbody></table>';
		}

		if(defined $cdi_syn_e){
#			$cdi_syn_e =~ s/(;)/$1<br>/g;
			$cdi_syn_e = '<div>'.join('</div><div>',split(/;/,$cdi_syn_e)).'</div>';
		}else{
			$cdi_syn_e = '';
		}
		$cdi_def_e = '' unless(defined $cdi_def_e);
		$art_num = '' unless(defined $art_num);
		$art_ids = '' unless(defined $art_ids);
		$cdi_name_e = '' unless(defined $cdi_name_e);

		my $html =<<HTML;
		<tr class="">
			<td class=" row_number">$rows</td>
			<td class=" cdi_name">$cdi_name</td>
			<td class=" cdi_name_e">$cdi_name_e</td>
			<td class=" cdi_syn_e">$cdi_syn_e</td>
			<td class=" cdi_def_e">$cdi_def_e</td>
			<td class=" art_num">$art_num</td>
			<td class=" art_ids">$art_ids</td>
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
	undef $sth_art_num;
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
	if($ENV{'HTTP_USER_AGENT'}=~/Windows/){
		$LF = "\r\n";
		$CODE = "shiftjis";
	}elsif($ENV{'HTTP_USER_AGENT'}=~/Macintosh/){
		$LF = "\r";
		$CODE = "shiftjis";
	}

	my $column_number = 0;
	my $cdi_id;

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
 to_char(cdi.cdi_entry,'YYYY/MM/DD HH24:MI:SS'),
 cm.art_num
from
  concept_data_info as cdi
left join (
  select ci_id,cdi_id,count(art_id) as art_num from concept_art_map where cm_delcause is null group by ci_id,cdi_id
) as cm on cdi.ci_id=cm.ci_id and cdi.cdi_id=cm.cdi_id
where
 cdi.cdi_delcause is null and cdi.ci_id=$ci_id
order by
 cdi_name
-- to_number(substring(cdi_name from 4),'999999')
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
	my $cdi_entry;
	my $art_num;

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
	$sth->bind_col(++$column_number, \$cdi_entry,   undef);
	$sth->bind_col(++$column_number, \$art_num,   undef);

	my $sth_art_num = $dbh->prepare('select cm.art_id,art_name,art_ext from concept_art_map as cm left join (select art_id,art_name,art_ext,art_serial,prefix_id from art_file_info where art_delcause is null) as arti on cm.art_id=arti.art_id where cm_delcause is null and ci_id=? and cdi_id=? order by arti.prefix_id,art_serial,cm.art_id') or die $dbh->errstr;

	my $header = qq|#ID	Name	Name(L)	Name(J)	Name(K)	Synonym	Synonym(J)	Definition	Definition(J)	TAID	#FJID	FJID|;
	&utf8::decode($header) unless(&utf8::is_utf8($header));

	($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime();
	my $timestamp = sprintf("%04d/%02d/%02d %02d:%02d:%02d", $year+1900,$month+1,$mday,$hour,$min,$sec);

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

			next unless(defined $cdi_name);

			my $art_ids = '';
			if(defined $art_num && $art_num>0){
				$sth_art_num->execute($ci_id,$cdi_id) or die $dbh->errstr;
				$column_number = 0;
				my $art_id;
				my $art_name;
				my $art_ext;
				$sth_art_num->bind_col(++$column_number, \$art_id,   undef);
				$sth_art_num->bind_col(++$column_number, \$art_name,   undef);
				$sth_art_num->bind_col(++$column_number, \$art_ext,   undef);
				my @ART_IDS;
				while($sth_art_num->fetch){
					push(@ART_IDS,qq|$art_id:$art_name$art_ext|);
				}
				$sth_art_num->finish;
				$art_ids = join(';',@ART_IDS);
			}

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

			$worksheet->write( $y, $x++, $art_num, $uni_format );
			$worksheet->write( $y, $x++, $art_ids, $uni_format );

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

			my $art_ids = '';
			if(defined $art_num && $art_num>0){
				$sth_art_num->execute($ci_id,$cdi_id) or die $dbh->errstr;
				$column_number = 0;
				my $art_id;
				my $art_name;
				my $art_ext;
				$sth_art_num->bind_col(++$column_number, \$art_id,   undef);
				$sth_art_num->bind_col(++$column_number, \$art_name,   undef);
				$sth_art_num->bind_col(++$column_number, \$art_ext,   undef);
				my @ART_IDS;
				while($sth_art_num->fetch){
					push(@ART_IDS,qq|$art_id:$art_name$art_ext|);
				}
				$sth_art_num->finish;
				$art_ids = join(';',@ART_IDS);
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

			push(@t,$art_num);
			push(@t,$art_ids);

			my $o = join("\t",map {defined $_ ? $_ : ''} @t);
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

sub exportConceptArtMap {
	my $dbh = shift;
	my $FORM = shift;

	my $out_path = &catdir($FindBin::Bin,'download',".$$");
	&File::Path::rmtree($out_path) if(-e $out_path);
	&File::Path::mkpath($out_path);

use BITS::ExportConceptArtMap;
	my $zip = &BITS::ExportConceptArtMap::exec($dbh,$FORM,$out_path);

	my ($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime();
	my @weekly = ('Sun', 'Mon', 'Tue', 'Wed', 'Thr', 'Fri', 'Sut');

	my $file = exists $FORM->{'filename'} && defined $FORM->{'filename'} && length $FORM->{'filename'} ? &_trim(&cgi_lib::common::decodeUTF8($FORM->{'filename'})) : undef;
	$file = sprintf("%04d%02d%02d%02d%02d%02d", $year+1900,$month+1,$mday,$hour,$min,$sec) unless(defined $file && length $file);
	my $zip_file = qq|$file.zip|;

=pod
use Encode;

use Archive::Zip;
use IO::File;
use File::Copy;
use File::Path;

	my $md_id = $FORM->{'md_id'};
	my $mv_id = $FORM->{'mv_id'};
	my $ci_id = $FORM->{'ci_id'};
	my $cb_id = $FORM->{'cb_id'};
	my $format = 'txt';

	my($ELEMENT, $COMP_DENSITY_USE_TERMS, $COMP_DENSITY_END_TERMS, $COMP_DENSITY, $CDI_MAP, $CDI_MAP_ART_DATE, $CDI_ID2CID, $CDI_MAP_SUM_VOLUME_DEL_ID) = &BITS::ConceptArtMapModified::calcElementAndDensity(
		dbh     => $dbh,
		md_id   => $md_id,
		mv_id   => $mv_id,
		ci_id   => $ci_id,
		cb_id   => $cb_id
	);


	my $art_file_base_path = &catdir($FindBin::Bin,'art_file');
#	my $art_file_raw_base_path = &catdir($FindBin::Bin,'download','art_file');
	&File::Path::mkpath($art_file_base_path) unless(-e $art_file_base_path);
#	&File::Path::mkpath($art_file_raw_base_path) unless(-e $art_file_raw_base_path);

	my $out_path = &catdir($FindBin::Bin,'download',".$$");
	&File::Path::rmtree($out_path) if(-e $out_path);
	&File::Path::mkpath($out_path);

	my ($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime();
	my @weekly = ('Sun', 'Mon', 'Tue', 'Wed', 'Thr', 'Fri', 'Sut');

	my $file = exists $FORM{'filename'} && defined $FORM{'filename'} && length $FORM{'filename'} ? &_trim(&cgi_lib::common::decodeUTF8($FORM{'filename'})) : '';
	$file = sprintf("%04d%02d%02d%02d%02d%02d", $year+1900,$month+1,$mday,$hour,$min,$sec) unless(defined $file && length $file);

	my $file_basename = qq|$file.$format|;

	my $file_name = &catdir($out_path,'concept_art_map.txt');
	my $zip_file = qq|$file.zip|;
	my $file_path = &catdir($out_path,$zip_file);

	my $LF = "\n";
	my $CODE = "utf8";

	my $column_number = 0;

	my $sql=<<SQL;
select
 cm.art_id,
 cm.cdi_id,
 cdi.cdi_name,
 cmp.cmp_abbr,
 length(cmp.cmp_abbr),
-- to_char(cm.cm_entry,'YYYY-MM-DD HH24:MI:SS'),
 cm.cm_entry,

 arti.art_name,
 arti.art_ext,
-- to_char(arti.art_timestamp,'YYYY-MM-DD HH24:MI:SS'),
 arti.art_timestamp,
 EXTRACT(EPOCH FROM arti.art_timestamp),

-- arti.art_nsn,
 arti.art_mirroring,
 arti.art_comment,
 arti.art_delcause,
-- to_char(arti.art_entry,'YYYY-MM-DD HH24:MI:SS'),
 arti.art_entry,
 arti.art_modified,
 prefix.prefix_char,
 arti.art_serial,
 arti.art_md5,
 arti.art_data_size,
 arti.art_xmin,
 arti.art_xmax,
 arti.art_ymin,
 arti.art_ymax,
 arti.art_zmin,
 arti.art_zmax,
 arti.art_volume,
-- arti.art_cube_volume,
 arti.art_category,
 arti.art_judge,
 arti.art_class,
 arti.arto_id,
 arti.arto_comment

from
 concept_art_map as cm

left join (
  select
   ci_id,
   cdi_id,
   cdi_name
  from
   concept_data_info
) as cdi on cdi.ci_id=cm.ci_id and cdi.cdi_id=cm.cdi_id

left join (
  select
   *
  from
   art_file_info
) as arti on arti.art_id=cm.art_id

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
 select * from id_prefix
) as prefix on prefix.prefix_id=arti.prefix_id

where
 cm.cm_delcause is null and
 arti.art_id is not null and
 cdi.cdi_name is not null and
 cm.md_id=$md_id and
 cm.mv_id=$mv_id
-- and cm.ci_id=$ci_id
-- and cm.cb_id=$cb_id
order by
 arti.prefix_id,
 arti.art_serial,
 arti.art_id
SQL

	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;

	my $art_id;
	my $cdi_id;
	my $cdi_name;
	my $cmp_abbr;
	my $cmp_length;
	my $cm_entry;
	my $art_name;
	my $art_ext;
	my $art_timestamp;
	my $art_timestamp_epoch;

#	my $art_nsn;
	my $art_mirroring;
	my $art_comment;
	my $art_delcause;
	my $art_entry;
	my $art_modified;

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
#	my $art_cube_volume;
	my $art_category;
	my $art_judge;
	my $art_class;
	my $arto_id;
	my $arto_comment;

	$column_number = 0;
	$sth->bind_col(++$column_number, \$art_id,   undef);
	$sth->bind_col(++$column_number, \$cdi_id,   undef);
	$sth->bind_col(++$column_number, \$cdi_name,   undef);
	$sth->bind_col(++$column_number, \$cmp_abbr,   undef);
	$sth->bind_col(++$column_number, \$cmp_length,   undef);
	$sth->bind_col(++$column_number, \$cm_entry,   undef);
	$sth->bind_col(++$column_number, \$art_name,   undef);
	$sth->bind_col(++$column_number, \$art_ext,   undef);
	$sth->bind_col(++$column_number, \$art_timestamp,   undef);
	$sth->bind_col(++$column_number, \$art_timestamp_epoch,   undef);

#	$sth->bind_col(++$column_number, \$art_nsn,   undef);
	$sth->bind_col(++$column_number, \$art_mirroring,   undef);
	$sth->bind_col(++$column_number, \$art_comment,   undef);
	$sth->bind_col(++$column_number, \$art_delcause,   undef);
	$sth->bind_col(++$column_number, \$art_entry,   undef);
	$sth->bind_col(++$column_number, \$art_modified,   undef);

	$sth->bind_col(++$column_number, \$prefix_char,   undef);
	$sth->bind_col(++$column_number, \$art_serial,   undef);
	$sth->bind_col(++$column_number, \$art_md5,   undef);
	$sth->bind_col(++$column_number, \$art_data_size,   undef);
	$sth->bind_col(++$column_number, \$art_xmin,   undef);
	$sth->bind_col(++$column_number, \$art_xmax,   undef);
	$sth->bind_col(++$column_number, \$art_ymin,   undef);
	$sth->bind_col(++$column_number, \$art_ymax,   undef);
	$sth->bind_col(++$column_number, \$art_zmin,   undef);
	$sth->bind_col(++$column_number, \$art_zmax,   undef);
	$sth->bind_col(++$column_number, \$art_volume,   undef);
#	$sth->bind_col(++$column_number, \$art_cube_volume,   undef);
	$sth->bind_col(++$column_number, \$art_category,   undef);
	$sth->bind_col(++$column_number, \$art_judge,   undef);
	$sth->bind_col(++$column_number, \$art_class,   undef);
	$sth->bind_col(++$column_number, \$arto_id,   undef);
	$sth->bind_col(++$column_number, \$arto_comment,   undef);

	my $sth_data = $dbh->prepare(qq|select art_data from art_file where art_id=? order by art_serial desc NULLS FIRST limit 1|) or die $dbh->errstr;
	my $sth_data_raw = $dbh->prepare(qq|select art_raw_data,art_raw_data_size from art_file where art_id=? order by art_serial desc NULLS FIRST limit 1|) or die $dbh->errstr;

	my $sth_group_folder = $dbh->prepare(qq|
select
 COALESCE(artf.artf_id,0) as artf_id,
 artf.artf_pid,
 COALESCE(artf.artf_name,'') as artf_name
from
 art_folder_file as artff
left join (
  select artf_id,artf_pid,artf_name from art_folder
) as artf on artf.artf_id=artff.artf_id
where
 artff.art_id=?
|) or die $dbh->errstr;

	my $sth_folder = $dbh->prepare(qq|select COALESCE(artf.artf_id,0) as artf_id,artf.artf_pid,COALESCE(artf.artf_name,'') as artf_name from art_folder as artf where COALESCE(artf.artf_id,0)=?|) or die $dbh->errstr;

#	my $header = qq|#FJID	FMA_ID	PART	MAP_DATE	FILENAME	FILE_DATE|;
	my @header_arr = qw|
FJID
FMA_ID
MAP_Timestamp
OBJ_Filename
OBJ_Timestamp

Comment
Category
Judge
Class
Xmin
Xmax
Ymin
Ymax
Zmin
Zmax
Volume
Size

art_entry
art_modified
prefix_char
art_serial
art_md5
arto_id

art_folder
|;

	my $header = '#'.join("\t",map {$_ =~ /^[a-z]/ ? uc($_) : $_} @header_arr);

#	&utf8::decode($header) unless(&utf8::is_utf8($header));
	$header = &cgi_lib::common::decodeUTF8($header);

	($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime();
	my $timestamp = sprintf("%04d/%02d/%02d %02d:%02d:%02d", $year+1900,$month+1,$mday,$hour,$min,$sec);

	open(my $OUT,"> $file_name") or die "$! [$file_name]";

	&utf8::encode($timestamp) if(&utf8::is_utf8($timestamp));
	my $s = qq|#Export Date:$timestamp|;
	&utf8::decode($s) unless(&utf8::is_utf8($s));
	print $OUT &Encode::encode($CODE,$s),$LF;

	print $OUT &Encode::encode($CODE,$header),$LF;

	my $zip = Archive::Zip->new();

	my %OUTPUT_ART_ID;
	my %ORG_ART_ID;
	while($sth->fetch){

		next unless(defined $art_id && defined $cdi_name);

		my $current_use;
		if(defined $cdi_id && defined $art_id && defined $CDI_MAP_ART_DATE && ref $CDI_MAP_ART_DATE eq 'HASH' && exists $CDI_MAP_ART_DATE->{$cdi_id} && defined $CDI_MAP_ART_DATE->{$cdi_id} && ref $CDI_MAP_ART_DATE->{$cdi_id} eq 'HASH' && exists $CDI_MAP_ART_DATE->{$cdi_id}->{$art_id}){
			$current_use = JSON::XS::true;	#子供のOBJより古くない場合
		}else{
			$current_use = JSON::XS::false;
		}
		if(defined $cdi_id && $current_use == JSON::XS::true && defined $CDI_MAP_SUM_VOLUME_DEL_ID && exists $CDI_MAP_SUM_VOLUME_DEL_ID->{$cdi_id}){
			$current_use = JSON::XS::false;	#子供のOBJが親のボリュームの90%より多い場合
		}
		next if($current_use == JSON::XS::false);

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
		next unless(-e $out_art_file_path && -f $out_art_file_path && -s $out_art_file_path);

		utime $art_timestamp_epoch,$art_timestamp_epoch,$out_art_file_path;


		my $art_filename_raw = qq|${art_id}_raw${art_ext}|;
		my $out_art_file_path_raw = &catfile($out_path,$art_filename_raw);
		unless(-e $out_art_file_path_raw && -f $out_art_file_path_raw && -s $out_art_file_path_raw){
			my $art_raw_data;
			my $art_raw_data_size;
			$sth_data_raw->execute($art_id) or die $dbh->errstr;
			$sth_data_raw->bind_col(1, \$art_raw_data, { pg_type => DBD::Pg::PG_BYTEA });
			$sth_data_raw->bind_col(2, \$art_raw_data_size, undef);
			$sth_data_raw->fetch;
			$sth_data_raw->finish;
			unless($art_data_size==$art_raw_data_size){
				if(defined $art_raw_data && open(my $OBJ,"> $out_art_file_path_raw")){
					flock($OBJ,2);
					binmode($OBJ,':utf8');
					print $OBJ $art_raw_data;
					close($OBJ);
					undef $OBJ;
				}
				undef $art_raw_data;
				undef $art_raw_data_size;
				next unless(-e $out_art_file_path_raw && -f $out_art_file_path_raw && -s $out_art_file_path_raw);
				utime $art_timestamp_epoch,$art_timestamp_epoch,$out_art_file_path_raw;
			}
			undef $art_raw_data;
			undef $art_raw_data_size;
		}


		$cmp_length = 0 unless(defined $cmp_length);
		$cmp_length -= 0;

		my @ART_FOLDER;
		$sth_group_folder->execute($art_id) or die $dbh->errstr;
		my $artf_id;
		my $artf_pid;
		my $artf_name;
		$column_number = 0;
		$sth_group_folder->bind_col(++$column_number, \$artf_id,   undef);
		$sth_group_folder->bind_col(++$column_number, \$artf_pid,   undef);
		$sth_group_folder->bind_col(++$column_number, \$artf_name,   undef);
		$sth_group_folder->fetch;
		$sth_group_folder->finish;
		unshift(@ART_FOLDER,$artf_name);
		while(defined $artf_pid){
			$sth_folder->execute($artf_pid) or die $dbh->errstr;
			$column_number = 0;
			$sth_folder->bind_col(++$column_number, \$artf_id,   undef);
			$sth_folder->bind_col(++$column_number, \$artf_pid,   undef);
			$sth_folder->bind_col(++$column_number, \$artf_name,   undef);
			$sth_folder->fetch;
			$sth_folder->finish;
			unshift(@ART_FOLDER,$artf_name);
		}

		if(defined $art_name && length $art_name){
			my($name,$dir,$ext) = &File::Basename::fileparse($art_name,qw|.obj|);
			$art_name = $name;
		}
		if(defined $arto_id && length $arto_id){
			my $HASH = {
				arto_id => $arto_id,
				arto_comment => $arto_comment,
			};
			$arto_id = &cgi_lib::common::encodeJSON($HASH);
		}

		my @t;
		push(@t,$art_id);
		push(@t,$cmp_length ? "$cdi_name-$cmp_abbr" : $cdi_name);
		push(@t,$cm_entry);
		push(@t,qq|$art_name$art_ext|);
		push(@t,$art_timestamp);

		push(@t,$art_comment);
		push(@t,$art_category);
		push(@t,$art_judge);
		push(@t,$art_class);
		push(@t,$art_xmin);
		push(@t,$art_xmax);
		push(@t,$art_ymin);
		push(@t,$art_ymax);
		push(@t,$art_zmin);
		push(@t,$art_zmax);
		push(@t,$art_volume);
		push(@t,$art_data_size);

#		push(@t,$art_nsn);
		push(@t,$art_entry);
		push(@t,$art_modified);
		push(@t,$prefix_char);
		push(@t,$art_serial);
		push(@t,$art_md5);
#		push(@t,$art_cube_volume);
		push(@t,$arto_id);
#		push(@t,$arto_comment);

		push(@t,'/'.join('/',@ART_FOLDER));

		my $o = join("\t",map {defined $_ ? $_ : ''} @t);
		&utf8::decode($o) unless(&utf8::is_utf8($o));
		print $OUT &Encode::encode($CODE,$o),$LF;

		$zip->addFile(&cgi_lib::common::encodeUTF8($out_art_file_path),&cgi_lib::common::encodeUTF8($art_filename));
		$zip->addFile(&cgi_lib::common::encodeUTF8($out_art_file_path_raw),&cgi_lib::common::encodeUTF8($art_filename_raw)) if(-e $out_art_file_path_raw && -f $out_art_file_path_raw && -s $out_art_file_path_raw);

		$OUTPUT_ART_ID{$art_id} = undef;

		if($art_mirroring){
			if($art_id =~ /^([A-Z]+[0-9]+)M$/){
				my $org_art_id = $1;
				$ORG_ART_ID{$org_art_id} = undef;
			}else{
				die "Unknown Mrror ID [$art_id]";
			}
		}
	}
	$sth->finish;
	undef $sth;
	undef %OUTPUT_ART_ID;
	undef %ORG_ART_ID;

	close($OUT);


	$zip->addFile(&cgi_lib::common::encodeUTF8($file_name),&cgi_lib::common::encodeUTF8(&File::Basename::basename($file_name)));

	my($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,$atime,$mtime,$ctime,$blksize,$blocks) = stat($file_name);
=cut

	my $mtime = time;
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
