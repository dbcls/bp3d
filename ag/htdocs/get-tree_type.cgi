#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use File::Basename;

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI::Cookie;

use File::Spec::Functions qw(catdir catfile);
use Cwd;
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'API'),&Cwd::abs_path(&catdir($FindBin::Bin,'..','..','ag-common','lib'));
use cgi_lib::common;

require "common.pl";
require "common_db.pl";
my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = fileparse($0,@extlist);
#open(LOG,"> $FindBin::Bin/logs/$COOKIE{'ag_annotation.session'}.$cgi_name.txt");
#print LOG "\n[$logtime]:$0\n";
#foreach my $key (sort keys(%FORM)){
#	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}
#foreach my $key (sort keys(%COOKIE)){
#	print LOG "\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
#}
#foreach my $key (sort keys(%ENV)){
#	print LOG "ENV{$key}=[",$ENV{$key},"]\n";
#}

#$FORM{lng} = $COOKIE{"ag_annotation.locale"} if(!exists($FORM{lng}) && exists($COOKIE{"ag_annotation.locale"})); #とりあえず
#$FORM{lng} = "en" if(!exists($FORM{lng}));
#$FORM{tg_id} = $COOKIE{"ag_annotation.images.tg_id"} if(!exists($FORM{tg_id}) && exists($COOKIE{"ag_annotation.images.tg_id"}));

&setDefParams(\%FORM,\%COOKIE);
#foreach my $key (sort keys(%FORM)){
#	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
#foreach my $key (sort keys(%FORM)){
#	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}

=pod
my $wt_version;
$wt_version = qq|tg_id=$FORM{tg_id} and tgi_id=$FORM{tgi_id}| if(exists($FORM{tg_id}) && exists($FORM{tgi_id}));

#$FORM{version} = "Talairach" if($FORM{t_type} eq "101");



my $lsdb_OpenID;
my $lsdb_Auth;
my $parentURL = $FORM{parent} if(exists($FORM{parent}));
my $parent_text;
if(defined $parentURL){
	($lsdb_OpenID,$lsdb_Auth) = &openidAuth($parentURL);
}
=cut


my @TREE = ();
my $TYPES = {
	records => [],
	total => 0
};

#print qq|Content-type: text/html; charset=UTF-8\n\n|;


my $sql_bul_name .= $FORM{lng} eq "ja" ? qq|COALESCE(bul_name_j,bul_name_e)| : qq|bul_name_e|;
my $sql_bul = qq|select bul_id,bul_order,bul_delcause,$sql_bul_name as bul_name from buildup_logic|;
=pod
=cut

my $sql;
=pod
$sql =<<SQL;
select distinct
 butc.bul_id,
-- ci.ci_name ||' '||cb.cb_name||' '||bul.bul_name,
 bul.bul_name,
 butc.ci_id,
 butc.cb_id,
 butc.butc_num,
 ci.ci_name,
 cb.cb_name,
 bul.bul_abbr,
 ci.ci_order,
 cb.cb_order,
 bul.bul_order
from
 buildup_tree_cnum as butc
left join (select ci_id,ci_name,ci_order,ci_delcause from concept_info) as ci on (ci.ci_id=butc.ci_id)
left join (select ci_id,cb_id,cb_name,cb_order,cb_delcause from concept_build) as cb on (cb.ci_id=butc.ci_id and cb.cb_id=butc.cb_id)
left join (select bul_id,bul_order,bul_delcause,bul_name_e as bul_name,bul_abbr from buildup_logic) as bul on (bul.bul_id=butc.bul_id)
left join (select ci_id,cb_id,bul_id,count(cdi_id) as num from buildup_tree where but_delcause is null group by ci_id,cb_id,bul_id) as but on (but.ci_id=butc.ci_id and but.cb_id=butc.cb_id and but.bul_id=butc.bul_id)
left join (select ci_id,cb_id,bul_id,count(cdi_id) as num from representation where rep_delcause is null group by ci_id,cb_id,bul_id) as bu on (bu.ci_id=butc.ci_id and bu.cb_id=butc.cb_id and bu.bul_id=butc.bul_id)
where
 ci.ci_delcause is null and
 cb.cb_delcause is null and
 bul.bul_delcause is null and
 butc.butc_delcause is null and
 butc.butc_num>0 and
 bu.num>0 and
 butc.ci_id=? AND
 butc.cb_id=?
order by
 ci.ci_order,
 cb.cb_order,
 bul.bul_order
SQL
=cut

$sql =<<SQL;
SELECT
 rep.bul_id,
 bul.bul_name,
 mv.ci_id,
 mv.cb_id,
 rep.butc_num,
 ci.ci_name,
 cb.cb_name,
 bul.bul_abbr,
 ci.ci_order,
 cb.cb_order,
 bul.bul_order

FROM (
 SELECT md_id,mv_id,MAX(mr_id),bul_id,COUNT(cdi_id) AS butc_num FROM representation WHERE rep_delcause IS NULL GROUP BY md_id,mv_id,bul_id ORDER BY md_id,mv_id,bul_id
) AS rep

LEFT JOIN (
 SELECT
  bul_id,
  bul_order,
  bul_delcause,
  bul_name_e as bul_name,
  bul_abbr
 FROM
  buildup_logic
) AS bul ON bul.bul_id=rep.bul_id

LEFT JOIN (
 SELECT
  md_id,
  mv_id,
  ci_id,
  cb_id
 FROM
  model_version
) AS mv ON
 mv.md_id=rep.md_id AND
 mv.mv_id=rep.mv_id

LEFT JOIN (
 select
  ci_id,
  ci_name,
  ci_order,
  ci_delcause
 from
  concept_info
) as ci on ci.ci_id=mv.ci_id
LEFT JOIN (
 select
  ci_id,
  cb_id,
  cb_name,
  cb_order,
  cb_delcause
 from
  concept_build
) as cb on (cb.ci_id=mv.ci_id and cb.cb_id=mv.cb_id)

where
 rep.butc_num>0 and
 mv.ci_id=? AND
 mv.cb_id=?
order by
 ci.ci_order,
 cb.cb_order,
 bul.bul_order
SQL



=pod
$sql = qq|select|;
$sql .= qq| t_type|;
$sql .= qq|,t_name|;
$sql .= qq| from|;
$sql .= qq| (select tree.t_type|;
if(!exists($FORM{lng}) || $FORM{lng} eq "ja"){
	$sql .= qq| ,COALESCE(tree_type.t_name_j,tree_type.t_name_e)|;
}else{
	$sql .= qq| ,tree_type.t_name_e|;
}
$sql .= qq| as t_name,tree_type.t_order from tree|;
#$sql .= qq| left join (select t_type,t_name_j,t_name_e,t_order from tree_type) as tree_type on tree.t_type=tree_type.t_type|;
$sql .= qq| left join (select t_type,t_name_j,t_name_e,t_order from tree_type where t_delcause is null) as tree_type on tree.t_type=tree_type.t_type|;
$sql .= qq| and $wt_version| if(defined $wt_version);
$sql .= qq| ) as tree|;
$sql .= qq| where t_name is not null group by t_type,t_name,t_order order by t_order|;
=cut


#print LOG __LINE__,":sql=[$sql]\n";

my $sth = $dbh->prepare($sql) or die $dbh->errstr;

$sth->execute($FORM{ci_id},$FORM{cb_id}) or die $dbh->errstr;
$TYPES->{total} = $sth->rows();

my($bul_id,$bul_name,$ci_id,$ci_name,$cb_id,$cb_name,$butc_num,$bul_abbr);

my $column_number = 0;
$sth->bind_col(++$column_number, \$bul_id, undef);
$sth->bind_col(++$column_number, \$bul_name, undef);
$sth->bind_col(++$column_number, \$ci_id, undef);
$sth->bind_col(++$column_number, \$cb_id, undef);
$sth->bind_col(++$column_number, \$butc_num, undef);
$sth->bind_col(++$column_number, \$ci_name, undef);
$sth->bind_col(++$column_number, \$cb_name, undef);
$sth->bind_col(++$column_number, \$bul_abbr, undef);

while($sth->fetch){
	next unless(defined $bul_id && defined $bul_name);
#	utf8::decode($bul_name) if(defined $bul_name && !utf8::is_utf8($bul_name));
	my $HASH = {
		bul_id   => $bul_id,
		bul_name => $bul_name,
		bul_abbr => $bul_abbr,
		ci_id    => $ci_id,
		ci_name  => $ci_name,
		cb_id    => $cb_id,
		cb_name  => $cb_name,
		butc_num => $butc_num,
		t_type   => $bul_id,
		t_name   => qq|$ci_name $cb_name $bul_name|
	};
	push(@{$TYPES->{records}},$HASH);
}
$sth->finish;
undef $sth;

&cgi_lib::common::printContentJSON($TYPES);

#my $json = to_json($TYPES);
#my $json = &JSON::XS::encode_json($TYPES);
#$json =~ s/"(true|false)"/$1/mg;

#print $json;
#print LOG __LINE__,":",$json,"\n";

#close(LOG);
exit;

=debug




=cut
