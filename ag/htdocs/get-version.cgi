#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;

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
#foreach my $key (sort keys(%ENV)){
#	print LOG __LINE__,":\$ENV{$key}=[",$ENV{$key},"]\n";
#}
#foreach my $key (sort keys(%FORM)){
#	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}

&setDefParams(\%FORM,\%COOKIE);
#foreach my $key (sort keys(%FORM)){
#	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
#foreach my $key (sort keys(%FORM)){
#	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}


my @TREE = ();
my $VERSIONS = {
	records => [],
	total => 0
};

#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $sql_mv_name .= $FORM{lng} eq "ja" ? qq|COALESCE(mv_name_j,mv_name_e)| : qq|mv_name_e|;
my $sql_mv = qq|select md_id,mv_id,mv_order,$sql_mv_name as mv_name,mv_delcause,mv_publish,mv_use,mv_comment,mv_objects_set from model_version|;
=pod
my $sql =<<SQL;
select distinct
 bu.md_id,
 bu.mv_id,
 max(bu.mr_id) as mr_id,
 mr_version,
 mv_name,
 mv_order,
 mr_order
from
 representation as bu
left join ($sql_mv) as mv on (bu.md_id=mv.md_id and bu.mv_id=mv.mv_id)
left join (select md_id,mv_id,mr_id,mr_version,mr_order from model_revision) as mr on (bu.md_id=mr.md_id and bu.mv_id=mr.mv_id and bu.mr_id=mr.mr_id)
where
 bu.rep_delcause is null and
 mv.mv_delcause is null and
-- bu.mv_id<=2 and
 bu.ci_id=?
group by
 bu.md_id,
 bu.mv_id,
 mr_version,
 mv_name,
 mv_order,
 mr_order
order by
 mv_order,
 mr_order
SQL
=cut
my $sql =<<SQL;
select distinct
 bu.md_id,
 bu.mv_id,
 bu.mr_id,
 bu.ci_id,
 bu.cb_id,
 mr_version,
 mv_name,
 mv_comment,
 mv_objects_set,
 ci_name,
 cb_name,
 mv_order,
 mr_order
from
 representation as bu
left join ($sql_mv) as mv on (bu.md_id=mv.md_id and bu.mv_id=mv.mv_id)
left join (select md_id,mv_id,mr_id,mr_version,mr_order from model_revision) as mr on (bu.md_id=mr.md_id and bu.mv_id=mr.mv_id and bu.mr_id=mr.mr_id)
left join (select ci_id,ci_name from concept_info where ci_use and ci_delcause is null) as ci on (bu.ci_id=ci.ci_id)
left join (select ci_id,cb_id,cb_name from concept_build where cb_use and cb_delcause is null) as cb on (bu.ci_id=cb.ci_id and bu.cb_id=cb.cb_id)
where
 bu.rep_delcause is null and
 mv.mv_delcause is null and
 mv.mv_publish and
 mv.mv_use and
-- bu.mv_id<=2 and
 bu.ci_id=? and
 (bu.md_id,bu.mv_id,bu.mr_id) in (select md_id,mv_id,max(mr_id) as mr_id from representation group by md_id,mv_id)
order by
 mv_order,
 mr_order
SQL

my $sth = $dbh->prepare($sql) or die $dbh->errstr;
#$FORM{ci_id} = 1;
$VERSIONS->{total} = $sth->execute($FORM{ci_id}) or die $dbh->errstr;

my $sql_relation = qq|select f_potname from concept_build_relation as c left join (select * from fma_partof_type) as f on (c.f_potid=f.f_potid) where cbr_use and c.f_potid>1 and ci_id=? and cb_id=? order by f.f_order|;
my $sth_relation = $dbh->prepare($sql_relation) or die $dbh->errstr;


my($md_id,$mv_id,$tgi_version,$md_name,$ci_id,$cb_id);
my $mr_id;
my $mv_comment;
my $mv_objects_set;
my $ci_name;
my $cb_name;

my $column_number = 0;
$sth->bind_col(++$column_number, \$md_id, undef);
$sth->bind_col(++$column_number, \$mv_id, undef);
$sth->bind_col(++$column_number, \$mr_id, undef);
$sth->bind_col(++$column_number, \$ci_id, undef);
$sth->bind_col(++$column_number, \$cb_id, undef);
$sth->bind_col(++$column_number, \$tgi_version, undef);
$sth->bind_col(++$column_number, \$md_name, undef);
$sth->bind_col(++$column_number, \$mv_comment, undef);
$sth->bind_col(++$column_number, \$mv_objects_set, undef);
$sth->bind_col(++$column_number, \$ci_name, undef);
$sth->bind_col(++$column_number, \$cb_name, undef);

while($sth->fetch){

	$sth_relation->execute($ci_id,$cb_id) or die;
	$column_number = 0;
	my $f_potname;
	my $part_of_relation = [];
	$sth_relation->bind_col(++$column_number, \$f_potname, undef);
	while($sth_relation->fetch){
		push(@$part_of_relation,$f_potname) if(defined $f_potname && length $f_potname);
	}
	$sth_relation->finish;

	my $HASH = {
		md_id => $md_id,
		mv_id => $mv_id,
		mr_id => $mr_id,
		ci_id => $ci_id,
		cb_id => $cb_id,

		tg_id  => $md_id,
		tgi_id => $mv_id,
		tgi_renderer_version => $tgi_version,
		tgi_version => $md_name,
		tgi_name => $md_name,
		tgi_comment => $mv_comment,
		tgi_objects_set => $mv_objects_set,
		tgi_tree_version => "$ci_name$cb_name",
		tgi_part_of_relation => join(', ',@$part_of_relation)
	};
	push(@{$VERSIONS->{'records'}},$HASH);
}
$sth->finish;
undef $sth;

#my $json = to_json($VERSIONS);
&cgi_lib::common::printContentJSON($VERSIONS);
#$json =~ s/"(true|false)"/$1/mg;

#print $json;
#print LOG __LINE__,":",$json,"\n";

#close(LOG);
exit;

=debug




=cut
