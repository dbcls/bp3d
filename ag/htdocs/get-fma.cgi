#!/opt/services/ag/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use File::Path;
use File::Spec;
use File::Spec::Functions qw(catdir catfile);
use File::Basename;
use Data::Dumper;

#use Image::Info qw(image_info dim);
#use Image::Magick;
#use Storable;
#use SetEnv;

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI::Cookie;
use Cwd;
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'API'),&Cwd::abs_path(&catdir($FindBin::Bin,'..','lib')),&Cwd::abs_path(&catdir($FindBin::Bin,'..','..','ag-common','lib'));
use cgi_lib::common;

require "common.pl";
require "common_db.pl";
my $dbh = &get_dbh();

my $disEnv = &getDispEnv();
my $addPointElementHidden = $disEnv->{addPointElementHidden};
my $removeGridColOrganSystem = $disEnv->{removeGridColOrganSystem};
$addPointElementHidden = 'false' unless(defined $addPointElementHidden);
$removeGridColOrganSystem = 'true' unless(defined $removeGridColOrganSystem);

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);

#my $env = SetEnv->new;
#my @BP3DVERSION = ();
#foreach my $version (@{$env->{versions}}){
#	push(@BP3DVERSION,"$version");
#}

#DEBUG 常に削除
#delete $FORM{parent} if(exists($FORM{parent}));
#my $lsdb_OpenID;
#my $lsdb_Auth;
#my $parentURL = $FORM{parent} if(exists($FORM{parent}));
#my $parent_text;
#if(defined $parentURL){
#	($lsdb_OpenID,$lsdb_Auth) = &openidAuth($parentURL);
#}

my @FILTER = ();

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0, qr/\..*$/);
my $LOG = &cgi_lib::common::getLogFH(\%FORM,\%COOKIE);

#open(LOG,"> $FindBin::Bin/logs/$COOKIE{'ag_annotation.session'}.$cgi_name.txt");
#print LOG "\n[$logtime]:$0\n";
#foreach my $key (sort keys(%FORM)){
#	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}
foreach my $key (sort keys(%FORM)){
	if($key =~ /filter/){
		my $key2 = &url_decode($key);
#		print LOG __LINE__,":\$FORM{$key2}=[",$FORM{$key},"]\n";
		if($key2 =~ /^filter\[([0-9]+)\]\[data\]\[type\]$/){
			my $idx = $1;
			$FILTER[$idx]->{data}->{type} = $FORM{$key};
		}elsif($key2 =~ /^filter\[([0-9]+)\]\[data\]\[comparison\]$/){
			my $idx = $1;
			$FILTER[$idx]->{data}->{comparison} = $FORM{$key};
		}elsif($key2 =~ /^filter\[([0-9]+)\]\[data\]\[value\]$/){
			my $idx = $1;
			$FILTER[$idx]->{data}->{value} = $FORM{$key};
		}elsif($key2 =~ /^filter\[([0-9]+)\]\[field\]$/){
			my $idx = $1;
			$FILTER[$idx]->{field} = $FORM{$key};
		}
	}else{
#		print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
	}
}


#foreach my $key (sort keys(%COOKIE)){
#	print LOG "\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
#}
#foreach my $key (sort keys(%ENV)){
#	print LOG "\$ENV{$key}=[",$ENV{$key},"]\n";
#}

#$FORM{lng} = $COOKIE{"ag_annotation.locale"} if(!exists($FORM{lng}) && exists($COOKIE{"ag_annotation.locale"})); #とりあえず
#$FORM{lng} = "en" if(!exists($FORM{lng}));
#$FORM{position} = "front" if(!exists($FORM{position}));
#$FORM{version} = $BP3DVERSION[0] if(!exists($FORM{version}));

&setDefParams(\%FORM,\%COOKIE);
#foreach my $key (sort keys(%FORM)){
#	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
#foreach my $key (sort keys(%FORM)){
#	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}

#my $bp3d_table = &getBP3DTablename($FORM{version});


$SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit";
sub sigexit {
	my($date) = `date`;
	$date =~ s/\s*$//g;
	print STDERR "[$date] KILL THIS CGI!![$ENV{SCRIPT_NAME}]\n";
	exit(1);
}
=pod
if(exists($FORM{version}) && (!exists($FORM{tg_id}) || !exists($FORM{tgi_id}))){
	my $tg_id;
	my $tgi_id;
	my $sth_tree_group_item = $dbh->prepare(qq|select tg_id,tgi_id from tree_group_item where tgi_version=?|);
	$sth_tree_group_item->execute($FORM{version});
	my $column_number = 0;
	$sth_tree_group_item->bind_col(++$column_number, \$tg_id, undef);
	$sth_tree_group_item->bind_col(++$column_number, \$tgi_id, undef);
	$sth_tree_group_item->fetch;
	if(defined $tg_id && defined $tgi_id){
		$FORM{tg_id} = $tg_id;
		$FORM{tgi_id} = $tgi_id;
	}
	$sth_tree_group_item->finish;
	undef $sth_tree_group_item;
}
my $wt_version = qq|tg_id=$FORM{tg_id} and tgi_id=$FORM{tgi_id}| if(exists($FORM{tg_id}) && exists($FORM{tgi_id}));
=cut

#####
#####
print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $IMAGES = {
	"records" => [],
	"total" => 0
};

my @bind_values = ();
my @LIST1 = ();
#unless(exists($FORM{node}) && exists($FORM{query}) && defined $bp3d_table && defined $wt_version){
unless(exists($FORM{node}) && exists($FORM{query})){
	$IMAGES->{success} = JSON::XS::true if(exists($FORM{callback}));
#	my $json = to_json($IMAGES);
	my $json = &JSON::XS::encode_json($IMAGES);
	if(exists($FORM{callback})){
		print $FORM{callback},"(",$json,")";
	}else{
		print $json;
	}
#	print LOG __LINE__,":",$json,"\n";
	exit;
}

if(exists($FORM{node}) && !exists($FORM{query})){
	push(@{$IMAGES->{records}},&getFMA($dbh,\%FORM,$FORM{node}));
	$IMAGES->{success} = JSON::XS::true if(exists($FORM{callback}));
	my $json = &JSON::XS::encode_json($IMAGES);
	if(exists($FORM{callback})){
		print $FORM{callback},"(",$json,")";
	}else{
		print $json;
	}
#	print LOG __LINE__,":",$json,"\n";
#	close(LOG);
	exit;
}
=pod
if($FORM{node} eq 'label' && exists($FORM{f_pid}) && exists($FORM{query})){
	my $f_id;
	my $sql = qq|select f_id from bp3d_point where $wt_version and f_pid=? and p_label=? and p_delcause is null|;
	my $sth = $dbh->prepare($sql);
	$sth->execute($FORM{f_pid},$FORM{query});
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$f_id, undef);
	while($sth->fetch){
		push(@{$IMAGES->{records}},&getFMA($dbh,\%FORM,$f_id));
	}
	$sth->finish;
	undef $sth;

	$IMAGES->{success} = JSON::XS::true if(exists($FORM{callback}));
	my $json = &JSON::XS::encode_json($IMAGES);
	if(exists($FORM{callback})){
		print $FORM{callback},"(",$json,")";
	}else{
		print $json;
	}
	print LOG __LINE__,":",$json,"\n";
	close(LOG);
	exit;
}
=cut

undef $query;

my $operator = &get_ludia_operator();
$query = $FORM{query};
my $space = qq|　|;
&utf8::decode($query) unless(&utf8::is_utf8($query));
&utf8::decode($space) unless(&utf8::is_utf8($space));
$query =~ s/$space/ /g;
&utf8::encode($query);


my $sql;
$sql  = qq|select a.f_id,a.cdi_id,a.score,a.name_j,a.name_k,a.name_e,a.name_l,a.taid,a.entry,a.xmin,a.xmax,a.ymin,a.ymax,a.zmin,a.zmax,a.volume,(CASE WHEN a.zmin is null THEN 0 ELSE 1 END) as ord,a.seg_color from (|;
{

	$sql .=<<SQL;

select
 cdi.ci_id,
 cdi.cdi_name as f_id,
 cdi.cdi_id as cdi_id,
 
 cdi.cdi_name_j as name_j,
 cdi.cdi_name_k as name_k,
 cdi.cdi_name_e as name_e,
 cdi.cdi_name_l as name_l,
 cdi.cdi_taid   as taid,

 bu.rep_entry as entry,

 bu.rep_xmin as xmin,
 bu.rep_xmax as xmax,
 bu.rep_ymin as ymin,
 bu.rep_ymax as ymax,
 bu.rep_zmin as zmin,
 bu.rep_zmax as zmax,
 bu.rep_volume as volume,

 COALESCE(cd.seg_color,bd.seg_color) as seg_color,

 0 as score
-- pgs2getscore(cdi.ctid, 'idx_concept_data_info_ludia') as score
-- pgs2getscore(cdi.ctid, 'idx_concept_data_info_ludia2') as score
-- pgs2getscore(cdi.ctid, 'idx_concept_data_info_ludia3') as score


from
 concept_data_info as cdi

left join (
  select
   ci_id,
   cdi_id,
   max(mr_id) as mr_id
  from
   representation
  where
   ci_id=$FORM{ci_id} and 
   cb_id=$FORM{cb_id} and 
   md_id=$FORM{md_id} and 
   mv_id=$FORM{mv_id} and 
   bul_id=$FORM{bul_id} and 
   rep_delcause is null
  group by
   ci_id,cdi_id
) as bu2 on
  bu2.ci_id=cdi.ci_id and 
  bu2.cdi_id=cdi.cdi_id

left join (
  select
   ci_id,
   rep_id,
   cdi_id,
   mr_id,
   rep_entry,
   rep_xmin,
   rep_xmax,
   rep_ymin,
   rep_ymax,
   rep_zmin,
   rep_zmax,
   rep_volume
 from
  representation
 where
  ci_id=$FORM{ci_id} and 
  cb_id=$FORM{cb_id} and 
  md_id=$FORM{md_id} and 
  mv_id=$FORM{mv_id} and 
  bul_id=$FORM{bul_id} and 
  rep_delcause is null
) as bu on 
  bu.ci_id=cdi.ci_id and 
  bu.cdi_id=cdi.cdi_id and 
  bu.mr_id=bu2.mr_id

left join (
 select
  cd.ci_id,
  cd.cdi_id,
  cs.seg_name,
  cs.seg_color,
  cs.seg_thum_bgcolor,
  cs.seg_thum_bocolor
 from
  concept_data as cd

 left join (
  select
  seg_id,
  seg_name,
  seg_color,
  seg_thum_bgcolor,
  seg_thum_bocolor
 from
  concept_segment
 ) as cs on
  cs.seg_id = cd.seg_id

 where
  ci_id=$FORM{ci_id} and 
  cb_id=$FORM{cb_id} and 
  cd_delcause is null
) as cd on 
  cd.ci_id=cdi.ci_id and 
  cd.cdi_id=cdi.cdi_id

left join (
 select
  cd.ci_id,
  cd.cdi_id,
  cs.seg_name,
  cs.seg_color,
  cs.seg_thum_bgcolor,
  cs.seg_thum_bocolor
 from
  buildup_data as cd

 left join (
  select
  seg_id,
  seg_name,
  seg_color,
  seg_thum_bgcolor,
  seg_thum_bocolor
 from
  concept_segment
 ) as cs on
  cs.seg_id = cd.seg_id

 where
  md_id=$FORM{md_id} and 
  mv_id=$FORM{mv_id} and 
  mr_id=$FORM{mr_id} and 
  cd_delcause is null
) as bd on 
  bd.ci_id=cdi.ci_id and 
  bd.cdi_id=cdi.cdi_id


where
 cdi.ci_id=$FORM{ci_id} and
 COALESCE(cd.cdi_id,bd.cdi_id) is not null and
 (ARRAY[cdi.cdi_name,cdi.cdi_name_j,cdi.cdi_name_e,cdi.cdi_name_k,cdi.cdi_name_l,cdi.cdi_syn_j,cdi.cdi_syn_e,cdi.cdi_taid] $operator ?)
-- (ARRAY[cdi.cdi_name,cdi.cdi_name_j,cdi.cdi_name_e,cdi.cdi_name_k,cdi.cdi_name_l,cdi.cdi_taid] $operator ?)
SQL
	push(@bind_values,qq|*D+ $query|);
}
$sql .= qq|) as a|;

#print LOG __LINE__,":\$sql=[$sql]\n";

if(scalar @FILTER > 0){

	my @WHERE = ();
	my $operator = &get_ludia_operator();
	my $space = qq|　|;
	&utf8::decode($space) unless(&utf8::is_utf8($space));

	foreach my $filter (@FILTER){
#		print LOG __LINE__,":\$filter=[$filter]\n";
		next unless(defined $filter);
#		print LOG __LINE__,":\$filter->{data}->{type}=[$filter->{data}->{type}]\n";
		if($filter->{data}->{type} eq "string"){
			my $query = $filter->{data}->{value};
			&utf8::decode($query) unless(&utf8::is_utf8($query));
			$query =~ s/$space/ /g;
			&utf8::encode($query);
			if($filter->{field} =~ /^name_/){
				push(@WHERE,qq|a.$filter->{field} $operator ?|); push(@bind_values,qq|*D+ $query|);
			}else{
				push(@WHERE,qq|a.$filter->{field} ~ ?|); push(@bind_values,qq|$query|);
			}
		}elsif($filter->{data}->{type} eq "boolean"){
			push(@WHERE,qq|(CASE WHEN a.zmin is null THEN 0 ELSE 1 END)=?|);
			my $query = $filter->{data}->{value};
			if($query eq 'true'){
			 push(@bind_values,1);
			}else{
			 push(@bind_values,0);
			}
		}else{
#			print LOG __LINE__,":\$filter->{data}->{comparison}=[$filter->{data}->{comparison}]\n";
			my $comparison = '=';
			if($filter->{data}->{comparison} eq 'gt'){
				$comparison = '>';
			}elsif($filter->{data}->{comparison} eq 'lt'){
				$comparison = '<';
			}
			my $query = $filter->{data}->{value};
			if($filter->{data}->{type} eq "date"){
				$query = $3.'/'.$1.'/'.$2 if($query =~ /^([0-9]{2})\/([0-9]{2})\/([0-9]{4})$/);
				push(@WHERE,qq|to_date(to_char(a.$filter->{field},'YYYY/MM/DD'),'YYYY/MM/DD') $comparison to_date(?,'YYYY/MM/DD')|); push(@bind_values,qq|$query|);
			}else{
				push(@WHERE,qq|a.$filter->{field} $comparison ?|); push(@bind_values,qq|$query|);
			}
		}
	}
	$sql .= qq| where |.join(" and ",@WHERE) if(scalar @WHERE > 0);

}

$sql .= qq| group by a.f_id,a.cdi_id,a.score,a.name_j,a.name_k,a.name_e,a.name_l,a.taid,a.entry,a.xmin,a.xmax,a.ymin,a.ymax,a.zmin,a.zmax,a.volume,a.seg_color|;

#print LOG __LINE__,":sql=[$sql]\n";

my $sth = $dbh->prepare($sql) or die DBI->errstr();
$sth->execute(@bind_values) or die DBI->errstr();
$IMAGES->{total} = $sth->rows();

my %CDI_IDS=();
my $column_number = 0;
my $cdi_name;
my $cdi_id;
$sth->bind_col(++$column_number, \$cdi_name, undef);
$sth->bind_col(++$column_number, \$cdi_id, undef);
while($sth->fetch){
	$CDI_IDS{$cdi_id} = $cdi_name;
}
$sth->finish;
undef $sth;

my $cdi_ids = join(qq|,|,sort keys(%CDI_IDS));
my $sql_count;
if(length($cdi_ids)>0){
	$sql_count=<<SQL;
select rep.bul_id,count(c.rep_id) from (
  select distinct
   bul_id
  from
   representation
  where
   ci_id=$FORM{ci_id} and 
   cb_id=$FORM{cb_id} and 
   md_id=$FORM{md_id} and 
   mv_id=$FORM{mv_id} and 
   rep_delcause is null
) as rep
left join (
  select rep.bul_id,rep_id from representation as rep
  right join (
    select
     ci_id,
     cb_id,
     cdi_id,
     md_id,
     mv_id,
     bul_id,
     max(mr_id) as mr_id
    from
     representation
    where
     ci_id=$FORM{ci_id} and 
     cb_id=$FORM{cb_id} and 
     md_id=$FORM{md_id} and 
     mv_id=$FORM{mv_id} and 
     cdi_id in ($cdi_ids) and
     rep_delcause is null
    group by
     ci_id,
     cb_id,
     cdi_id,
     md_id,
     mv_id,
     bul_id
  ) as r on
   r.ci_id=rep.ci_id and
   r.cb_id=rep.cb_id and
   r.cdi_id=rep.cdi_id and
   r.md_id=rep.md_id and
   r.mv_id=rep.mv_id and
   r.bul_id=rep.bul_id and
   r.mr_id=rep.mr_id
  where
   rep_id is not null
  group by
   rep.bul_id,rep_id
) as c on
 c.bul_id=rep.bul_id
group by
 rep.bul_id
SQL
}else{
	$sql_count=<<SQL;
select rep.bul_id,0 from (
  select distinct
   bul_id
  from
   representation
  where
   ci_id=$FORM{ci_id} and 
   cb_id=$FORM{cb_id} and 
   md_id=$FORM{md_id} and 
   mv_id=$FORM{mv_id} and 
   rep_delcause is null
) as rep
SQL
}
#print LOG __LINE__,":\$sql_count=[$sql_count]\n";
my $sth_count = $dbh->prepare($sql_count) or die;
$sth_count->execute() or die;
my %REP_NUM;
my $bul_id;
my $rep_num;
$column_number = 0;
$sth_count->bind_col(++$column_number, \$bul_id, undef);
$sth_count->bind_col(++$column_number, \$rep_num, undef);
while($sth_count->fetch){
	$REP_NUM{$bul_id} = $rep_num + 0;
}
$sth_count->finish;
undef $sth_count;

$IMAGES->{rep_num} = \%REP_NUM;


#print LOG __LINE__,":\$IMAGES->{total}=[$IMAGES->{total}]\n";

#=debug

if(defined $FORM{sort} && $FORM{sort} eq "b_id"){
	$sql .= qq| order by ord|;
	$sql .= qq| $FORM{dir}| if(defined $FORM{dir});
	$sql .= qq|,a.name_e|;
}else{
#	$sql .= qq| order by ord desc,a.score desc,|;
	$sql .= qq| order by ord desc,|;
	if(defined($FORM{sort})){
		if($FORM{sort} eq "f_id"){
			$sql .= qq|$FORM{sort}|;
		}else{
			$sql .= qq|a.$FORM{sort}|;
		}
		$sql .= qq| $FORM{dir}| if(defined $FORM{dir});
		$sql .= qq| NULLS LAST|;
	}else{
		$sql .= qq|a.name_e|;
	}
}
#=cut

if(exists($FORM{limit})){
	$sql .= qq| limit $FORM{limit}|;
}else{
#	$sql .= qq| limit 400|;
	$sql .= qq| limit 3000|;
}
$sql .= qq| offset $FORM{start}| if(defined $FORM{start});

say $LOG __LINE__.":sql=[$sql]" if(defined $LOG);
say $LOG __LINE__.":bind_values=[".join(",",@bind_values)."]" if(defined $LOG);

$sth = $dbh->prepare($sql);

if(scalar @bind_values > 0){
	$sth->execute(@bind_values);
}else{
	$sth->execute();
}
#print LOG __LINE__,":rows=[",$sth->rows(),"]\n";

my $f_id;
undef $cdi_id;
my $score;

$column_number = 0;
$sth->bind_col(++$column_number, \$f_id, undef);
$sth->bind_col(++$column_number, \$cdi_id, undef);
$sth->bind_col(++$column_number, \$score, undef);

my %DISP_FMA = ();

while($sth->fetch){
	if($FORM{node} eq "search"){
		next if(exists($DISP_FMA{$f_id}));
		$DISP_FMA{$f_id} = undef;
	}
#print LOG __LINE__,":\$f_id=[$f_id]\n";
	my $rtn = &getFMA($dbh,\%FORM,$f_id);
	$rtn->{score} = $score;
	push(@{$IMAGES->{records}},$rtn);
}
$sth->finish;

#print LOG __LINE__,qq|:\$DISP_FMA=['|,join(qq|','|,sort keys(%DISP_FMA)),qq|']\n|;

undef $sth;

$IMAGES->{total} += 0;
$IMAGES->{success} = JSON::XS::true if(exists($FORM{callback}));
#my $json = to_json($IMAGES);
my $json = &JSON::XS::encode_json($IMAGES);

#print LOG __LINE__,":",Dumper($IMAGES),"\n";

if(exists($FORM{callback})){
	print $FORM{callback},"(",$json,")";
}else{
	print $json;
}
#print LOG __LINE__,":",$json,"\n";


#close(LOG);
exit;
