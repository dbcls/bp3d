#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use File::Basename;
use File::Spec::Functions qw(catdir catfile);
use JSON::XS;

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI::Cookie;

use Time::HiRes;
my $t0 = [&Time::HiRes::gettimeofday()];

use Data::Dumper;
$Data::Dumper::Indent = 1;
$Data::Dumper::Sortkeys = 1;

use Cwd;
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'API'),&Cwd::abs_path(&catdir($FindBin::Bin,'..','..','ag-common','lib'));
use cgi_lib::common;

use constant VIEW_PREFIX => qq|reference_|;

require "common.pl";
require "common_db.pl";

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);
&checkXSS(\%FORM);

my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0, qr/\..*$/);
my $log_filename = $cgi_name;
$log_filename .= qq|.$FORM{'type'}| if(exists $FORM{'type'} && defined $FORM{'type'} && length $FORM{'type'});
my $LOG = &cgi_lib::common::getLogFH(\%FORM,\%COOKIE,$log_filename);
if(defined $LOG){
	my $old = select($LOG);
	$| = 1;
	select($old);
}

&setDefParams(\%FORM,\%COOKIE);
&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);

#my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
#my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
#my @extlist = qw|.cgi|;
#my($cgi_name,$cgi_dir,$cgi_ext) = fileparse($0,@extlist);
#open(LOG,">> $FindBin::Bin/logs/$COOKIE{'ag_annotation.session'}.$cgi_name.$FORM{'type'}.txt");
#open(LOG,"> $FindBin::Bin/logs/$COOKIE{'ag_annotation.session'}.$cgi_name.$FORM{'type'}.txt");
#flock(LOG,2);
#print $LOG "\n[$logtime]:$0\n";
#foreach my $key (sort keys(%FORM)){
#	print $LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}
#foreach my $key (sort keys(%COOKIE)){
#	print $LOG __LINE__,":\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
#}
#foreach my $key (sort keys(%ENV)){
#	print $LOG __LINE__,":\$ENV{$key}=[",$ENV{$key},"]\n";
#}

$FORM{'table'} = qq|representation_art| unless(exists $FORM{'table'} && defined $FORM{'table'});

#print qq|Content-type: text/html; charset=UTF-8\n\n|;

exit unless(exists $COOKIE{'ag_annotation.session'});
exit unless(defined $FORM{'type'} && defined $FORM{'table'});

if(exists $FORM{'rep_ids'} && defined $FORM{'rep_ids'}){
	my $rep_ids = &cgi_lib::common::decodeJSON($FORM{'rep_ids'});
	if(defined $rep_ids && ref $rep_ids eq 'ARRAY'){
		$FORM{'rep_id'} = [];
		push(@{$FORM{'rep_id'}},@$rep_ids);
	}
	delete $FORM{'rep_ids'};
	if(exists $FORM{'art_ids'} && defined $FORM{'art_ids'}){
		my $art_ids = &cgi_lib::common::decodeJSON($FORM{'art_ids'});
		delete $FORM{'art_ids'};
		$FORM{'art_ids'} = [];
		push(@{$FORM{'art_ids'}},@$art_ids);
	}
}

my %SQL;
#my $view_name = VIEW_PREFIX.qq|representation_art|;
my $view_name = VIEW_PREFIX.$FORM{'table'};
$SQL{$view_name}=<<SQL;
--CREATE TEMPORARY VIEW $view_name AS
CREATE VIEW $view_name AS
SELECT distinct
  false::boolean            as download,
  mr_version||'/'||idp.prefix_char||'/'||substring(art.art_serial_char from 1 for 2)||'/'||substring(art.art_serial_char from 3 for 2)||'/'||art.art_id||'_16x16.gif' as thumb,
  art.art_id                as model_component,
  rep.rep_id                as representation_id,
  repa2.cdi_name            as represented_concept,
  repa2.cdi_name_e          as english_name,
  md.md_name_e              as model,
  mv.mv_name_e              as compatibility_version,
  repa.art_hist_serial      as serial,

  artg.artg_name||'/'||arti.art_name||arti.art_ext as filename,
  arti.art_timestamp        as timestamp,

  art.art_xmin              as xmin,
  art.art_xmax              as xmax,
  art.art_ymin              as ymin,
  art.art_ymax              as ymax,
  art.art_zmin              as zmin,
  art.art_zmax              as zmax,
  art.art_volume            as volume,
  art.art_cube_volume       as cube_volume,
  art.art_entry             as entry,
  COALESCE(cd.seg_color,bd.seg_color) as color

FROM representation rep

LEFT JOIN (
    SELECT *
    FROM representation_art
  ) repa ON repa.rep_id  = rep.rep_id
LEFT JOIN (
    SELECT concept_data_info.ci_id, concept_data_info.cdi_id, concept_data_info.cdi_name
    FROM concept_data_info
  ) cdi ON cdi.ci_id  = rep.ci_id AND
           cdi.cdi_id = rep.cdi_id
LEFT JOIN (
    SELECT concept_info.ci_id, concept_info.ci_name
    FROM concept_info
  ) ci ON ci.ci_id  = rep.ci_id
LEFT JOIN (
    SELECT concept_build.ci_id, concept_build.cb_id, concept_build.cb_name
    FROM concept_build
  ) cb ON cb.ci_id = rep.ci_id AND
          cb.cb_id = rep.cb_id

LEFT JOIN (
--    SELECT *,to_char(art_serial,'FM9999990000') as art_serial_char FROM history_art_file
    SELECT *,to_char( to_number(substring(art_id from '[0-9]+'),'FM9999999999'),'FM9999990000') as art_serial_char FROM history_art_file
  ) art ON art.art_id=repa.art_id AND art.hist_serial=repa.art_hist_serial

LEFT JOIN (
    select prefix_char::text,prefix_id from id_prefix
  ) idp on idp.prefix_id=art.prefix_id

LEFT JOIN (
    SELECT model.md_id, model.md_name_e, model.md_name_j
    FROM model
  ) md ON md.md_id  = rep.md_id
LEFT JOIN (
    SELECT model_version.md_id, model_version.mv_id, model_version.mv_version, model_version.mv_name_e, model_version.mv_name_j
    FROM model_version
  ) mv ON mv.md_id = rep.md_id AND
          mv.mv_id = rep.mv_id
LEFT JOIN (
    SELECT md_id, mv_id, mr_id, mr_version
    FROM model_revision
  ) mr ON mr.md_id = rep.md_id AND
          mr.mv_id = rep.mv_id AND
          mr.mr_id = rep.mr_id

LEFT JOIN (
    SELECT
     cm.art_id,
     cm.art_hist_serial,
     cm.ci_id,
     cm.cb_id,
     cm.md_id,
     cm.mv_id,
     cm.mr_id,
     cm.cdi_id,
     cdi.cdi_name,
     cdi.cdi_name_e
    FROM
--     (select * from concept_art_map where (ci_id,cb_id,md_id,mv_id,mr_id,cdi_id) in (select ci_id,cb_id,md_id,mv_id,max(mr_id),cdi_id from concept_art_map group by ci_id,cb_id,md_id,mv_id,cdi_id)) as cm
     (select * from concept_art_map where (art_id,ci_id,cb_id,md_id,mv_id,mr_id,cdi_id) in (select art_id,ci_id,cb_id,md_id,mv_id,max(mr_id),cdi_id from concept_art_map group by art_id,ci_id,cb_id,md_id,mv_id,cdi_id)) as cm
    LEFT JOIN (
        SELECT
         ci_id,
         cdi_id,
         cdi_name,
         cdi_name_e
        FROM
         concept_data_info
      ) cdi on
         cdi.ci_id=cm.ci_id AND
         cdi.cdi_id=cm.cdi_id
    WHERE
     cm_use AND
     cm_delcause is null
    GROUP BY
     cm.art_id,
     cm.art_hist_serial,
     cm.ci_id,
     cm.cb_id,
     cm.md_id,
     cm.mv_id,
     cm.mr_id,
     cm.cdi_id,
     cdi.cdi_name,
     cdi.cdi_name_e
  ) repa2 ON
     repa2.ci_id = rep.ci_id AND
     repa2.cb_id = rep.cb_id AND
     repa2.md_id = rep.md_id AND
     repa2.mv_id = rep.mv_id AND
     repa2.art_id = repa.art_id AND
     repa2.art_hist_serial = repa.art_hist_serial

LEFT JOIN (
    SELECT * FROM art_file_info where art_delcause is null
  ) arti ON arti.art_id  = art.art_id

LEFT JOIN (
    SELECT * FROM art_group where atrg_use AND artg_delcause is null
  ) artg ON artg.artg_id  = arti.artg_id


LEFT JOIN (
 SELECT ci_id, cb_id, cdi_id, seg_color, seg_thum_bgcolor
 FROM concept_data as cd
 LEFT JOIN (
  SELECT seg_id, seg_color, seg_thum_bgcolor
  FROM concept_segment
 ) cs ON cd.seg_id = cs.seg_id

) cd ON cd.ci_id = repa2.ci_id AND
        cd.cb_id = repa2.cb_id AND
        cd.cdi_id = repa2.cdi_id

LEFT JOIN (
 SELECT md_id, mv_id, mr_id, cdi_id, seg_color, seg_thum_bgcolor
 FROM buildup_data as bd
 LEFT JOIN (
  SELECT seg_id, seg_color, seg_thum_bgcolor
  FROM concept_segment
 ) cs ON bd.seg_id = cs.seg_id

) bd ON bd.md_id = repa2.md_id AND
        bd.mv_id = repa2.mv_id AND
        bd.mr_id = repa2.mr_id AND
        bd.cdi_id = repa2.cdi_id


WHERE
 rep.rep_delcause IS NULL AND
 repa2.cdi_name_e IS NOT NULL
order by
 repa.art_hist_serial
SQL

#my $view_name = VIEW_PREFIX.qq|representation|;
#$SQL{$view_name}=<<SQL;
#SQL

#my $view_name = VIEW_PREFIX.qq|art_file|;
#$SQL{$view_name}=<<SQL;
#SQL

#my $view_name = VIEW_PREFIX.$FORM{'table'};

#DEBUG
=pod
if(&existsView($view_name)){
	$dbh->do(qq|drop view $view_name|) or die $dbh->errstr;
}
=cut

unless(&existsView($view_name)){
	$dbh->do($SQL{$view_name}) or die $dbh->errstr if(exists $SQL{$view_name});
}
#my $columns = &getDbTableColumns($view_name);
my $columns = &cgi_lib::common::decodeJSON(qq|[
	{"column_name":"download","data_type":"boolean","ordinal_position":1},
	{"column_name":"thumb","data_type":"text","ordinal_position":2},
	{"column_name":"model_component","data_type":"text","ordinal_position":3},
	{"column_name":"represented_concept","data_type":"text","ordinal_position":5},
	{"column_name":"english_name","data_type":"text","ordinal_position":6},
	{"column_name":"model","data_type":"text","ordinal_position":7},
	{"column_name":"compatibility_version","data_type":"text","ordinal_position":8},
	{"column_name":"serial","data_type":"integer","ordinal_position":9},
	{"column_name":"filename","data_type":"text","ordinal_position":10},
	{"column_name":"timestamp","data_type":"timestamp without time zone","ordinal_position":11},
	{"column_name":"xmin","data_type":"numeric","ordinal_position":12},
	{"column_name":"xmax","data_type":"numeric","ordinal_position":13},
	{"column_name":"ymin","data_type":"numeric","ordinal_position":14},
	{"column_name":"ymax","data_type":"numeric","ordinal_position":15},
	{"column_name":"zmin","data_type":"numeric","ordinal_position":16},
	{"column_name":"zmax","data_type":"numeric","ordinal_position":17},
	{"column_name":"volume","data_type":"numeric","ordinal_position":18},
	{"column_name":"cube_volume","data_type":"numeric","ordinal_position":19},
	{"column_name":"entry","data_type":"timestamp without time zone","ordinal_position":20},
	{"column_name":"color","data_type":"text","ordinal_position":21}
]|);
exit unless(defined $columns);

if($FORM{'type'} eq 'schema'){

	my @COLS;
	if(exists $FORM{'rep_id'} && defined $FORM{'rep_id'}){
		foreach my $col (@$columns){
			next if($col->{'column_name'} eq 'rep_id' || $col->{'column_name'} eq 'representation_id');
			push(@COLS,$col);
		}
	}else{
		push(@COLS,@$columns);
	}
#	print &JSON::XS::encode_json(\@COLS);
	&cgi_lib::common::printContentJSON(\@COLS,\%FORM);
	&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\@COLS,1),$LOG) if(defined $LOG);
}
elsif($FORM{'type'} eq 'data'){
	&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);
	my @cols;
	my $delcause;
	my %name2type;
	foreach my $col (@$columns){
		next if($col->{'data_type'} eq 'bytea');
#		next if($col->{'column_name'} =~ /openid/);
#		if($col->{'column_name'} =~ /_delcause$/){
#			$delcause = $col->{'column_name'};
#			next;
#		}

		if($col->{'data_type'} =~ /^timestamp/){
			push(@cols,'EXTRACT(EPOCH FROM '.$col->{'column_name'}.') as '.$col->{'column_name'});
		}else{
			push(@cols,$col->{'column_name'});
		}
		$name2type{$col->{'column_name'}} = $col->{'data_type'};
	}
#	my $sql = qq|select |.join(",",@cols).qq| from $view_name|;
	my $sql =<<SQL;
SELECT
 thumb,
 model_component,
 representation_id,
 represented_concept,
 english_name,
 model,
 compatibility_version,
 serial,
 filename,
 EXTRACT(EPOCH FROM timestamp) AS timestamp,
 obj_xmin AS xmin,
 obj_xmax AS xmax,
 obj_ymin AS ymin,
 obj_ymax AS ymax,
 obj_zmin AS zmin,
 obj_zmax AS zmax,
 volume,
 cube_volume,
 EXTRACT(EPOCH FROM entry) AS entry,
 color
FROM
 view_representation_art
SQL

	my @bind_values;
	my @where;

	push(@where,qq|$delcause is null|) if(defined $delcause);
#	print $sql;

	if(exists $FORM{'hash'} && defined $FORM{'hash'}){
		my %hash;
		my @info = split("&",$FORM{'hash'});
		foreach my $i (@info){
			$hash{$1} = &url_decode($2) if($i =~ /^(.+)=(.+)$/);
		}
		foreach my $i (keys(%hash)){
			if($i eq 'art_id'){
				my @a = split(",",$hash{$i});
				my @s = split("","?"x(scalar @a));
				push(@where,qq|art_id in (|.join(",",@s).qq|)|);
				push(@bind_values,@a);
			}else{
				next;
			}
		}
	}elsif(exists $FORM{'rep_id'} && defined $FORM{'rep_id'}){
		if(ref $FORM{'rep_id'} eq 'ARRAY'){
			push(@where, sprintf(qq|representation_id in (%s)|, join(',', map {'?'} @{$FORM{'rep_id'}})));
			push(@bind_values, @{$FORM{'rep_id'}});
#			print $LOG __LINE__.':'."\n";
		}else{
#			push(@where,qq|representation_id=?|);
			push(@where,qq|rep_id=?|);
			push(@bind_values, $FORM{'rep_id'});
#			print $LOG __LINE__.':'.(ref $FORM{'rep_id'})."\n";
		}
	}
	print $LOG __LINE__.':@where='.&Data::Dumper::Dumper(\@where);

	if(scalar @where > 0){
		$sql .= qq| where | ;
		$sql .= join(" AND ",@where);
	}

	#mix
	if(exists $FORM{'rep_id'} && defined $FORM{'rep_id'}){
=pod
		my $md_id;
		my $mv_id;
		my $mr_id;
		my $bul_id;
		my @rep_id_values;
#		my $sql_rep = qq|select md_id,mv_id,mr_id,bul_id from representation where rep_id=?|;
		my $sql_rep = qq|select md_id,mv_id,mr_id,bul_id from representation where rep_id|;
		if(ref $FORM{'rep_id'} eq 'ARRAY'){
			$sql_rep .= sprintf(qq| in (%s)|, join(',', map {'?'} @{$FORM{'rep_id'}}));
			push(@rep_id_values, @{$FORM{'rep_id'}});
		}else{
			$sql_rep .= qq|=?|;
			push(@rep_id_values, $FORM{'rep_id'});
		}
		my $sth_rep = $dbh->prepare($sql_rep) or die $dbh->errstr;
#		$sth_rep->execute($FORM{'rep_id'}) or die $dbh->errstr;
		$sth_rep->execute(@rep_id_values) or die $dbh->errstr;
		my $column_number = 0;
		$sth_rep->bind_col(++$column_number, \$md_id, undef);
		$sth_rep->bind_col(++$column_number, \$mv_id, undef);
		$sth_rep->bind_col(++$column_number, \$mr_id, undef);
		$sth_rep->bind_col(++$column_number, \$bul_id, undef);
		$sth_rep->fetch;
		$sth_rep->finish;
		undef $sth_rep;


		my $cdi_id;
		my $but_cids;

		my $sql_but_cids = qq|select cdi_id,but_cids from buildup_tree_info WHERE (md_id,mv_id,mr_id,ci_id,cb_id,bul_id,cdi_id) in (select md_id,mv_id,mr_id,ci_id,cb_id,bul_id,cdi_id from representation where rep_id|;

		if(ref $FORM{'rep_id'} eq 'ARRAY'){
			$sql_but_cids .= sprintf(qq| in (%s)|, join(',', map {'?'} @{$FORM{'rep_id'}}));
		}else{
			$sql_but_cids .= qq|=?|;
		}
		$sql_but_cids .= qq|)|;
#print $LOG __LINE__,qq|:\$sql_but_cids=[|.$sql_but_cids.qq|]\n| if(defined $LOG);
		my $sth_but_cids = $dbh->prepare($sql_but_cids) or die $dbh->errstr;

		$sth_but_cids->execute(@rep_id_values) or die $dbh->errstr;
		$column_number = 0;
		$sth_but_cids->bind_col(++$column_number, \$cdi_id, undef);
		$sth_but_cids->bind_col(++$column_number, \$but_cids, undef);
		$sth_but_cids->fetch;
		$sth_but_cids->finish;
		undef $sth_but_cids;
		$but_cids = &cgi_lib::common::decodeJSON($but_cids) if(defined $but_cids);
		$but_cids = [] unless(defined $but_cids && ref $but_cids eq 'ARRAY');
		push(@$but_cids,$cdi_id);

		my $rep_ids;
		if(defined $rep_ids && ref $rep_ids eq 'ARRAY' && scalar @$rep_ids > 0){
			$sql .= qq| UNION select |.join(",",@cols).qq| from $view_name where representation_id in ('|.join("','",@$rep_ids).qq|')|;
		}
=cut

=pod
		$sql=<<SQL;
SELECT
  false::boolean            as download,
  mr_version||'/'||idp.prefix_char||'/'||substring(art.art_serial_char from 1 for 2)||'/'||substring(art.art_serial_char from 3 for 2)||'/'||art.art_id||'_16x16.gif' as thumb,
  cm.art_id                 as model_component,
  rep.rep_id                as representation_id,
  cdi.cdi_name              as represented_concept,
  cdi.cdi_name_e            as english_name,
  md.md_name_e              as model,
  mv.mv_name_e              as compatibility_version,
  0 as serial,
  art.art_name||art.art_ext             as filename,
  EXTRACT(EPOCH FROM art.art_timestamp) as timestamp,

  art.art_xmin                        as xmin,
  art.art_xmax                        as xmax,
  art.art_ymin                        as ymin,
  art.art_ymax                        as ymax,
  art.art_zmin                        as zmin,
  art.art_zmax                        as zmax,
  art.art_volume                      as volume,
  art.art_cube_volume                 as cube_volume,
  EXTRACT(EPOCH FROM art.art_entry)   as entry,
  COALESCE(cd.seg_color,bd.seg_color) as color


FROM
 representation AS rep

LEFT JOIN concept_art_map AS cm ON cm.md_id=rep.md_id AND cm.mv_id=rep.mv_id AND cm.mr_id=rep.mr_id AND cm.cdi_id=rep.cdi_id
LEFT JOIN (
 SELECT
  art_id,
  prefix_id,
  art_name,
  art_ext,
  art_timestamp,
  art_xmin,
  art_ymin,
  art_zmin,
  art_xmax,
  art_ymax,
  art_zmax,
  art_volume,
  art_cube_volume,
  art_entry,
  to_char( to_number(substring(art_id from '[0-9]+'),'FM9999999999'),'FM9999990000') as art_serial_char
 FROM
  art_file
) art ON art.art_id=cm.art_id

LEFT JOIN id_prefix AS idp on idp.prefix_id=art.prefix_id

LEFT JOIN concept_data_info AS cdi on cdi.ci_id=rep.ci_id AND cdi.cdi_id=rep.cdi_id

LEFT JOIN (
    SELECT model.md_id, model.md_name_e, model.md_name_j
    FROM model
  ) md ON md.md_id  = rep.md_id
LEFT JOIN (
    SELECT model_version.md_id, model_version.mv_id, model_version.mv_version, model_version.mv_name_e, model_version.mv_name_j
    FROM model_version
  ) mv ON mv.md_id = rep.md_id AND
          mv.mv_id = rep.mv_id
LEFT JOIN (
    SELECT md_id, mv_id, mr_id, mr_version
    FROM model_revision
  ) mr ON mr.md_id = rep.md_id AND
          mr.mv_id = rep.mv_id AND
          mr.mr_id = rep.mr_id

LEFT JOIN (
 SELECT ci_id, cb_id, cdi_id, seg_color, seg_thum_bgcolor
 FROM concept_data as cd
 LEFT JOIN (
  SELECT seg_id, seg_color, seg_thum_bgcolor
  FROM concept_segment
 ) cs ON cd.seg_id = cs.seg_id

) cd ON cd.ci_id = rep.ci_id AND
        cd.cb_id = rep.cb_id AND
        cd.cdi_id = rep.cdi_id

LEFT JOIN (
 SELECT md_id, mv_id, mr_id, cdi_id, seg_color, seg_thum_bgcolor
 FROM buildup_data as bd
 LEFT JOIN (
  SELECT seg_id, seg_color, seg_thum_bgcolor
  FROM concept_segment
 ) cs ON bd.seg_id = cs.seg_id

) bd ON bd.md_id = rep.md_id AND
        bd.mv_id = rep.mv_id AND
        bd.mr_id = rep.mr_id AND
        bd.cdi_id = rep.cdi_id

WHERE
 rep_primitive AND
 rep_delcause IS NULL AND
(
 rep.ci_id,
 rep.cb_id,
 rep.md_id,
 rep.mv_id,
 rep.mr_id,
 rep.bul_id,
 rep.cdi_id
) IN (
 SELECT
  ci_id,
  cb_id,
  md_id,
  mv_id,
  mr_id,
  bul_id,
  regexp_split_to_table(regexp_replace(regexp_replace(COALESCE(but_cids,''),'[^0-9]+\$','')||','||cdi_id ,'^[^0-9]+',''),'[^0-9]+')::integer
 FROM
  buildup_tree_info
 WHERE
--  but_cids IS NOT NULL AND
  (
   ci_id,
   cb_id,
   cdi_id,
   md_id,
   mv_id,
   mr_id,
   bul_id
  ) IN (
   SELECT
    ci_id,
    cb_id,
    cdi_id,
    md_id,
    mv_id,
    mr_id,
    bul_id
   FROM
    representation
   WHERE
    rep_id IN (%s)
  )
)
SQL

		if(ref $FORM{'rep_id'} eq 'ARRAY'){
			$sql = sprintf($sql, join(',', map {'?'} @{$FORM{'rep_id'}}));
			push(@bind_values, @{$FORM{'rep_id'}});
		}else{
			$sql = sprintf($sql, '?');
			push(@bind_values, $FORM{'rep_id'});
		}
=cut

=pod
		$sql = qq|
select DISTINCT
  download,
  thumb,
  model_component,
  represented_concept,
  english_name,
  model,
  compatibility_version,
  serial,

  filename,
  timestamp,

  xmin,
  xmax,
  ymin,
  ymax,
  zmin,
  zmax,
  volume,
  cube_volume,
  entry,
  color
from ($sql) as a |;
=cut

	}
#print $LOG __LINE__,qq|:\$sql=[$sql]\n| if(defined $LOG);
&cgi_lib::common::message($sql,$LOG) if(defined $LOG);

	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	if(scalar @bind_values > 0){
		$sth->execute(@bind_values) or die $dbh->errstr;
		&cgi_lib::common::message(\@bind_values,$LOG) if(defined $LOG);
	}else{
		$sth->execute() or die $dbh->errstr;
	}
	my $rows = $sth->rows();
	$sth->finish;
	undef $sth;

#38:$FORM{sort}=[[{"property":"filename","direction":"ASC"}]]
	if(exists $FORM{'sort'} && defined $FORM{'sort'}){
		my $sort_arr = &cgi_lib::common::decodeJSON($FORM{'sort'});
		if(defined $sort_arr && ref $sort_arr eq 'ARRAY'){
#			my @S = map {qq|$_->{'property'} $_->{'direction'}|} @$sort_arr;
#			foreach my $s (@$sort_arr){
#				push(@S,qq|$s->{'property'} $s->{'direction'}|);
#			}
#			$sql .= qq| order by |.join(",",@S);
			$sql .= qq| order by |.join(",",map {qq|$_->{'property'} $_->{'direction'}|} @$sort_arr);
		}
	}

	$sql .= qq| limit $FORM{'limit'}| if(exists $FORM{'limit'} && defined $FORM{'limit'} && $FORM{'limit'} =~ /^[0-9]+$/);
	$sql .= qq| offset $FORM{'start'}| if(exists $FORM{'start'} && defined $FORM{'start'} && $FORM{'start'} =~ /^[0-9]+$/);

#print $LOG __LINE__,qq|:\$sql=[$sql]\n|;
#print $LOG __LINE__,qq|:\@bind_values=[|,join(",",@bind_values),qq|]\n|;
	&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

	my $datas = {
		total => $rows,
		datas=>[]
	};
&cgi_lib::common::message($sql,$LOG) if(defined $LOG);
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	if(scalar @bind_values > 0){
		$sth->execute(@bind_values) or die $dbh->errstr;
		&cgi_lib::common::message(\@bind_values,$LOG) if(defined $LOG);
	}else{
		$sth->execute() or die $dbh->errstr;
	}
	&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);
	while(my $href = $sth->fetchrow_hashref){
		foreach my $column_name (keys(%$href)){
#			say STDERR $name2type{$column_name};
			$href->{$column_name} += 0 unless($name2type{$column_name} eq 'text' || $name2type{$column_name} =~ /^character/);

			if($column_name eq 'thumb'){
#				my $path = qq|art_images/|.$href->{$column_name};
				my $path = catfile('art_images',$href->{$column_name});
&cgi_lib::common::message($path,$LOG) if(defined $LOG);
				unless(-e $path && -f $path && -s $path){
					my @p = split('/',$href->{$column_name});
					shift @p;
#					$path = qq|art_images/|.join('/',@p);
					$path = catfile('art_images',@p);
&cgi_lib::common::message($path,$LOG) if(defined $LOG);
				}
				if(-e $path && -f $path && -s $path){
					my $mtime = (stat($path))[9];
					$href->{$column_name} = qq|<img align=center width=16 height=16 src="$path?$mtime">|;
				}else{
					$href->{$column_name} = undef;
				}
			}

		}
		push(@{$datas->{'datas'}},$href);
	}
	$sth->finish;
	undef $sth;
	&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);
	if(defined $datas){
#		print &JSON::XS::encode_json($datas);
		&cgi_lib::common::printContentJSON($datas,\%FORM);
		&cgi_lib::common::message(&cgi_lib::common::encodeJSON($datas,1),$LOG) if(defined $LOG);
#		print $LOG __LINE__,qq|:\$datas=[|.&JSON::XS::encode_json($datas).qq|]\n| if(defined $LOG);
	}
	&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

}elsif($FORM{'type'} eq 'html'){
	my $title = exists $FORM{'rep_id'} && defined $FORM{'rep_id'} ? (ref $FORM{'rep_id'} eq 'ARRAY' ? join(",",@{$FORM{'rep_id'}}) : $FORM{'rep_id'}) : $FORM{'table'};
	my $rep_id = exists $FORM{'rep_id'} && defined $FORM{'rep_id'} ? (ref $FORM{'rep_id'} eq 'ARRAY' ? &JSON::XS::encode_json($FORM{'rep_id'}) : $FORM{'rep_id'}) : '""';
	my $rep_id_json = exists $FORM{'rep_id'} && defined $FORM{'rep_id'} ? (ref $FORM{'rep_id'} eq 'ARRAY' ? &JSON::XS::encode_json($FORM{'rep_id'}) : qq|"$FORM{'rep_id'}"|) : '""';
	my $EXT_PATH = qq|js/ext-4.2.1.883|;
	my @CSS = (
		"$EXT_PATH/resources/css/ext-all.css",
		"$EXT_PATH/ux/css/CheckColumn.css",
	);
	my @JS = (
		"js/jquery.js",
		"$EXT_PATH/ext-all.js",
		"$EXT_PATH/ux/CheckColumn.js",
	);
	push(@JS,"$EXT_PATH/locale/ext-lang-ja.js") if($FORM{lng} eq "ja");
	my $CONTENTS = <<HTML;
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja">
<head>
<meta http-equiv="X-UA-Compatible" content="IE=EmulateIE7" />
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta http-equiv="Content-Style-Type" content="text/css" />
<meta http-equiv="Content-Script-Type" content="text/javascript" />
<!-- CSS -->
HTML
	foreach my $css (@CSS){
		next unless(-e $css);
		my $mtime = (stat($css))[9];
		$CONTENTS .= qq|<link rel="stylesheet" href="$css?$mtime" type="text/css" media="all">\n|;
	}
	$CONTENTS .= <<HTML;
<!-- Javascript -->
HTML
	foreach my $js (@JS){
		next unless(-e $js);
		my $mtime = (stat($js))[9];
		$CONTENTS .= qq|<script type="text/javascript" src="$js?$mtime"></script>\n|;
	}
	$CONTENTS .= <<HTML;
<title>$title</title>
<style type="text/css">
.download_btn {
	background-image: url(css/ico_dl_d.png) !important;
}
a.external{
	color: #0044cc;
	background: url(css/external.png) no-repeat right center; !important;
	padding-right: 12px;
}
.download-image-btn{
	line-height:32px;
	font-size:32px;
}
a#download-image-btn{
	background: url(css/ico_dl_d.png) no-repeat center center; !important;
	padding-left:96px;
	text-decoration:none;
}
</style>
<script type="text/javascript"><!--
Ext.BLANK_IMAGE_URL = "$EXT_PATH/resources/themes/images/default/tree/s.gif";
Ext.Loader.setConfig({enabled: true});
Ext.require([
	'*'
]);
Ext.onReady(function() {
	Ext.state.Manager.setProvider(new Ext.state.CookieProvider()); //ソート順とかをCookieに登録する為に必要らしい

	Ext.QuickTips.init();
	bp3d.init();
});
var bp3d = {
	init:function(){
		var self = this;
		Ext.Ajax.request({
			url: '$cgi_name$cgi_ext',
			params: {
				type: 'schema',
				table: '$FORM{'table'}',
//				rep_id: Ext.encode($rep_id),
				rep_id: Ext.isArray($rep_id_json) ? null : $rep_id_json,
				rep_ids: Ext.isArray($rep_id_json) ? Ext.encode($rep_id_json) : null,
				hash: window.location.hash.substr(1)
			},
			success: function(response){
				var json;
				try{json = Ext.decode(response.responseText);}catch(e){}
				if(Ext.isEmpty(json)) return;

				var fields = [];
				var columns = [{xtype: 'rownumberer',minWidth:34}];
				Ext.Array.each(json,function(field,i,a){
					var type;
					var column_text = field.column_name.replace("_"," ");
					if(field.column_name=='thumb'){
						fields.push({
							name: field.column_name,
							type:'string'
						});
						columns.push({
							dataIndex: field.column_name,
							stateId: field.column_name,
//							text: column_text,
							menuDisabled:true,
							hideable: false,
							resizable: false,
							draggable: false,
							width: 28,
							renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
								if(record.data.color){
									metaData.style = 'background:'+record.data.color+';';
								}
								return value;
							}
						});
					}else if(field.data_type=='text'){
						fields.push({
							name: field.column_name,
							type:'string'
						});
						if(field.column_name=='model'){
							columns.push({
								dataIndex: field.column_name,
								stateId: field.column_name,
								text: column_text,
								draggable: false,
								width: 80,
								minWidth: 70
							});
						}else if(field.column_name=='color'){
							return true;
						}else{
							columns.push({
								dataIndex: field.column_name,
								stateId: field.column_name,
								text: column_text,
								hidden: (field.column_name=='filename' ? true : false),
								draggable: false,
								flex: field.column_name=='filename' || field.column_name=='english_name' ? 4 : 1,
								minWidth: 75
							});
						}
					}else if(field.data_type=='integer'){
						fields.push({
							name: field.column_name,
							type:'int'
						});
						columns.push({
							dataIndex: field.column_name,
							stateId: field.column_name,
							text: column_text,
							hidden: (field.column_name=='serial' ? true : false),
							draggable: false,
							xtype: 'numbercolumn',
							format:'0,000',
							align: 'right',
							width: 50
						});
					}else if(field.data_type=='numeric'){
						fields.push({
							name: field.column_name,
							type:'float'
						});
						columns.push({
							dataIndex: field.column_name,
							stateId: field.column_name,
							text: column_text,
							hidden: (field.column_name=='volume' ? false : true),
							draggable: false,
							xtype: 'numbercolumn',
							format:'0,000.0000',
							align: 'right',
							width: 70
						});
					}else if(field.data_type=='boolean'){
						fields.push({
							name: field.column_name,
							type:'boolean'
						});
						columns.push({
							dataIndex: field.column_name,
							stateId: field.column_name,
//							text: column_text,
							xtype: 'checkcolumn',
							menuDisabled:true,
							hideable: false,
							resizable: false,
							draggable: false,
							align: 'center',
							width: 30,
							listeners: {
								checkchange: function(column, recordIndex, checked, record){
									var gridpanels = Ext.ComponentQuery.query('gridpanel');
									if(Ext.isEmpty(gridpanels)) return;
									var selModel = gridpanels[0].getSelectionModel();
									if(Ext.isEmpty(selModel)) return;
									var records = selModel.getSelection();
									if(records.length>0) selModel.deselectAll(true);

									record.commit();

									if(records.length>0) selModel.select(records);
								}
							}
						});
					}else if(field.column_name.match(/^timestamp/) && field.data_type.match(/^timestamp/)){
						fields.push({
							name: field.column_name,
							type:'date',
							dateFormat:'timestamp'
						});
						columns.push({
							dataIndex: field.column_name,
							stateId: field.column_name,
							text: column_text,
							draggable: false,
							xtype: 'datecolumn',
							format:'Y/m/d',
							width: 70
						});
					}else if(field.data_type.match(/^timestamp/)){
						fields.push({
							name: field.column_name,
							type:'date',
							dateFormat:'timestamp'
						});
						columns.push({
							dataIndex: field.column_name,
							stateId: field.column_name,
							text: column_text,
							xtype: 'datecolumn',
							hidden: true,
							draggable: false,
							format:'Y/m/d H:i:s',
							width: 120
						});
					}
				});

				var proxy_ajax = {
					type: 'ajax',
					url: '$cgi_name$cgi_ext',
					timeout: 300000,
					extraParams: {
						type: 'data',
						table: '$FORM{'table'}',
//						rep_id: Ext.Object.toQueryString({rep_id:$rep_id}),
						rep_id: Ext.isArray($rep_id_json) ? null : $rep_id_json,
						rep_ids: Ext.isArray($rep_id_json) ? Ext.encode($rep_id_json) : null,
						hash: window.location.hash.substr(1)
					},
					reader: {
						type: 'json',
						root: 'datas'
					},
					actionMethods : {
						create : "POST",
						read   : "POST",
						update : "POST",
						destroy: "POST"
					},
						directionParam: undefined,
						filterParam: undefined,
						groupDirectionParam: undefined,
						groupParam: undefined,
						limitParam: undefined,
						pageParam: undefined,
						sortParam: undefined,
						startParam: undefined
				};

				var store = new Ext.data.JsonStore({
					autoLoad: false,
					remoteSort: false,
					autoLoad: true,
					filterOnLoad: false,
					proxy: proxy_ajax,
					fields: fields,
					pageSize: 5000,
					listeners: {
						update: function(store,record,operation){
							if(operation != Ext.data.Model.COMMIT) return;
							Ext.defer(function(){
								var dom = Ext.get('download-image-btn').findParent('div.download-image-btn');
								if(dom){
									var r = store.findRecord('download',true,0,false,false,true);
									if(r){
										Ext.get(dom).unmask();
									}else{
										Ext.get(dom).mask();
									}
								}
								bp3d.update_display_count();
							},0);

						}
					}
				});
				bp3d.__store = store;

				bp3d.__viewport = Ext.create('Ext.container.Viewport', {
					layout: 'border',
					items: [{
						id: 'grid-obj-list',
						region: 'center',
						xtype: 'grid',
						store: store,
						columns: columns,
						stateful: true,
						columnLines: true,
						plugins: {
							ptype: 'bufferedrenderer',
							trailingBufferZone: 20,
							leadingBufferZone: 50
						},
						viewConfig: {
							loadMask: false
						},
						dockedItems: [{
							xtype: 'toolbar',
							dock: 'top',
							hidden: false,
							items:[{
								text: 'check all',
								listeners: {
									click: {
										fn: function(b){
											var gridpanel = b.up('gridpanel');
											if(Ext.isEmpty(gridpanel)) return;
											var store = gridpanel.getStore();
											if(Ext.isEmpty(store)) return;

											var checked = true;
											store.suspendEvents(false);
											Ext.each(store.getRange(),function(r,i,a){
												if(r.data.download == checked) return true;
												r.beginEdit();
												r.set('download',checked);
												r.commit(false);
												r.endEdit(false,['download']);
											});
											store.resumeEvents();
											gridpanel.getView().refresh();

											var dom = Ext.get('download-image-btn').findParent('div.download-image-btn');
											if(dom) Ext.get(dom).unmask();
											bp3d.update_display_count();

										},
										buffer: 100
									}
								}
							},'-',{
								disabled: false,
								text: 'uncheck all',
								id: 'selected-onoff-btn',
								listeners: {
									click: {
										fn: function(b){
											var gridpanel = b.up('gridpanel');
											if(Ext.isEmpty(gridpanel)) return;
											var store = gridpanel.getStore();
											if(Ext.isEmpty(store)) return;

											var checked = false;
											store.suspendEvents(false);
											Ext.each(store.getRange(),function(r,i,a){
												if(r.data.download == checked) return true;
												r.beginEdit();
												r.set('download',checked);
												r.commit(false);
												r.endEdit(false,['download']);
											});
											store.resumeEvents();
											gridpanel.getView().refresh();

											var dom = Ext.get('download-image-btn').findParent('div.download-image-btn');
											if(dom) Ext.get(dom).mask();
											bp3d.update_display_count();

										},
										buffer: 100
									}
								}
							},'-','->',{
								id: 'tbtext-count',
								xtype: 'tbtext',
								text: '- / - Objects'
							}]
						},{
							hidden: true,
							xtype: 'pagingtoolbar',
							store: store,
							dock: 'bottom',
							displayInfo: true,
							displayMsg: self.lng.displayMsg,

							getPagingItems: function() {
								var me = this;
								return [{
									itemId: 'first',
									tooltip: me.firstText,
									overflowText: me.firstText,
									iconCls: Ext.baseCSSPrefix + 'tbar-page-first',
									disabled: true,
									handler: me.moveFirst,
									scope: me
								},{
									itemId: 'prev',
									tooltip: me.prevText,
									overflowText: me.prevText,
									iconCls: Ext.baseCSSPrefix + 'tbar-page-prev',
									disabled: true,
									handler: me.movePrevious,
									scope: me
								},
								'-',
								me.beforePageText,
								{
									xtype: 'numberfield',
									itemId: 'inputItem',
									name: 'inputItem',
									cls: Ext.baseCSSPrefix + 'tbar-page-number',
									allowDecimals: false,
									minValue: 1,
									hideTrigger: true,
									enableKeyEvents: true,
									keyNavEnabled: false,
									selectOnFocus: true,
									submitValue: false,
									// mark it as not a field so the form will not catch it when getting fields
									isFormField: false,
									width: me.inputItemWidth,
									margins: '-1 2 3 2',
									listeners: {
										scope: me,
										keydown: me.onPagingKeyDown,
										blur: me.onPagingBlur
									}
								},{
									xtype: 'tbtext',
									itemId: 'afterTextItem',
									text: Ext.String.format(me.afterPageText, 1)
								},
								'-',
								{
									itemId: 'next',
									tooltip: me.nextText,
									overflowText: me.nextText,
									iconCls: Ext.baseCSSPrefix + 'tbar-page-next',
									disabled: true,
									handler: me.moveNext,
									scope: me
								},{
									itemId: 'last',
									tooltip: me.lastText,
									overflowText: me.lastText,
									iconCls: Ext.baseCSSPrefix + 'tbar-page-last',
									disabled: true,
									handler: me.moveLast,
									scope: me
								},
								{
									hidden: true,
									itemId: 'refresh',
									tooltip: me.refreshText,
									overflowText: me.refreshText,
									iconCls: Ext.baseCSSPrefix + 'tbar-loading',
									handler: me.doRefresh,
									scope: me
								}];
							},

							items:[{
								hidden: true,
								text: self.lng.all_downloads,
								iconCls: 'download_btn',
								listeners: {
									click: {
										fn: function(b){
											self.download({all_downloads:1});
										},
										buffer: 100
									}
								}
							},{
								hidden: true,
								disabled: true,
								text: self.lng.download,
								id: 'download-btn',
								iconCls: 'download_btn',
								listeners: {
									click: {
										fn: function(b){
											var gridpanels = Ext.ComponentQuery.query('gridpanel');
											if(Ext.isEmpty(gridpanels)) return;
											var store = gridpanels[0].getStore();
											if(Ext.isEmpty(store)) return;
											var ids = [];
											Ext.each(store.getRange(),function(r,i,a){
												if(!r.data.download) return true;
												ids.push(r.data.model_component);
											});
											self.download({ids:ids});
										},
										buffer: 100
									}
								}
							},{
								hidden: true,
								xtype: 'tbitem',
								html: '<a class="external" target="_blank" href="http://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html">'+self.lng.license+'</a>'
							},'-']
						}]
					},{
						region: 'south',
						height: 36,
						border: false,
						bodyStyle: 'border-width:1px 0 0 0;background:transparent;padding:2px;text-align:right;',
						html: '<table align="right"><tr><td><div style="border-left:1px solid #99bce8;height:28px;margin:0 4px;"></div></td><td class="download-image-btn"><div class="download-image-btn"><a id="download-image-btn" class="download-image-btn" href="#" onclick="return bp3d.click_download();">&nbsp;</a></div></td><td><div style="border-left:1px solid #99bce8;height:28px;margin:0 4px;"></div></td><td><a class="external" target="_blank" href="http://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html">'+self.lng.license+'</a></td></tr></table>',
						listeners: {
							afterrender: {
								fn :function(){
									var dom = Ext.get('download-image-btn').findParent('div.download-image-btn');
									if(dom) Ext.get(dom).mask();
								},
								buffer: 250
							}
						}
					}],
					listeners: {
						afterrender: function( viewport, eOpts ){
							var store = viewport.down('gridpanel').getStore();
							if(store.isLoading()){
								viewport.setLoading(true);
							}
							store.on({
								beforeload: function(store,operation,eOpts){
									viewport.setLoading(true);
								},
								load: function(store,records, successful, eOpts){
									viewport.setLoading(false);
									bp3d.update_display_count();
								}
							});
						}
					}
				});
			},
			failure: function(response, opts) {
//				console.log('server-side failure with status code ' + response.status);
			}
		});
	},
	update_display_count: function(){
		var self = this;
		Ext.defer(function(){
			var gridpanel = Ext.getCmp('grid-obj-list');
			var store = gridpanel.getStore();
			var tbtext = Ext.getCmp('tbtext-count');
			var c = store.getCount();
			var fc = 0;
			store.each(function(record){
				if(record.get('download')) fc++;
			});
			tbtext.setText(Ext.util.Format.format('{0} / {1} Objects', fc, c));
		},100);
	},
	click_download: function(){
		var self = this;
//		var store = bp3d._download_store;
		var store = Ext.getCmp('grid-obj-list').getStore();
		if(Ext.isEmpty(store)) return;
		try{
			var c = store.getCount();
			store.filter('download',true);
			var fc = store.getCount();
			if(fc>0){
				if(c==fc){
					self.download({all_downloads:1});
				}else{
					var ids = [];
					Ext.each(store.getRange(),function(r,i,a){
						ids.push(r.data.model_component);
					});
					self.download({ids:ids});
				}
			}
		}catch(e){
//			console.log(e);
		}
		store.clearFilter();
		return false;
	},
	download: function(params){
		params = params || {};
		var form_name = 'form_download';
		if(!document.forms[form_name]){
			var form = \$('<form>').attr({
				action: "download.cgi",
				method: "POST",
				name:   form_name,
				id:     form_name,
				style:  "display:none;"
			}).appendTo(\$(document.body));
HTML
	if(exists $FORM{'rep_id'} && defined $FORM{'rep_id'} && ref $FORM{'rep_id'} eq 'ARRAY'){
		$CONTENTS .= <<HTML;
		var input = \$('<input type="hidden" name="filename">').appendTo(form);
		input.val(Ext.util.Format.date(new Date(),'YmdHis'));
HTML
		foreach my $id (@{$FORM{'rep_id'}}){
			$CONTENTS .= <<HTML;
			var input = \$('<input type="hidden" name="rep_id" value="$id">').appendTo(form);
HTML
		}
	}else{
		$CONTENTS .= <<HTML;
			var input = \$('<input type="hidden" name="rep_id" value="$rep_id">').appendTo(form);
HTML
	}
	$CONTENTS .= <<HTML;
			var input = \$('<input type="hidden" name="type" value="art_file">').appendTo(form);
			var input = \$('<input type="hidden" name="all_downloads">').appendTo(form);
			var input = \$('<input type="hidden" name="ids">').appendTo(form);
		}
		document.forms[form_name].all_downloads.value = '';
		document.forms[form_name].ids.value = '';
		if(params.all_downloads){
			document.forms[form_name].all_downloads.value = 1;
		}else if(params.ids){
			document.forms[form_name].ids.value = Ext.encode(params.ids);
		}else{
			return;
		}
		document.forms[form_name].submit();
	},
	lng : {
		displayMsg: '{0} - {1} / {2}',
HTML
	if($FORM{lng} eq "ja"){
		$CONTENTS .= <<HTML;
		all_downloads : '一括ダウンロード',
		download : 'ダウンロード',
		license : 'ライセンス事項'
HTML
	}else{
		$CONTENTS .= <<HTML;
		all_downloads : 'All downloads',
		download : 'Download',
		license : 'License terms'
HTML
	}
	$CONTENTS .= <<HTML;
	}
};
// --></script>
</head>
<body>
</body>
</html>
HTML
	&cgi_lib::common::printContent($CONTENTS);
}
close($LOG) if(defined $LOG);

__END__
#/bp3d/20170331/ag1/htdocs_170331/db/001_Concept/013_make_view_representation_art.pl
