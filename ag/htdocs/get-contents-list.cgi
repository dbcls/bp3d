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
use lib $FindBin::Bin,&catdir($FindBin::Bin,'API'),&Cwd::abs_path(&catdir($FindBin::Bin,'..','lib')),&Cwd::abs_path(&catdir($FindBin::Bin,'..','..','ag-common','lib'));
use cgi_lib::common;
use AG::login;

require "common.pl";
require "common_db.pl";

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);


#DEBUG 常に削除
#delete $FORM{parent} if(exists($FORM{parent}));
my $lsdb_OpenID;
my $lsdb_Auth;
my $parentURL = $FORM{parent} if(exists($FORM{parent}));
my $parent_text;
my $lsdb_Config;
my $lsdb_Identity;
if(defined $parentURL){
	($lsdb_OpenID,$lsdb_Auth) = &openidAuth($parentURL);
}elsif(exists($COOKIE{openid_url}) && exists($COOKIE{openid_session})){
	($lsdb_OpenID,$lsdb_Auth,$lsdb_Config,$lsdb_Identity) = &AG::login::openidAuthSession($COOKIE{openid_url},$COOKIE{openid_session});
}



#37:$FORM{filter[0][data][type]}=[string]
#37:$FORM{filter[0][data][value]}=[bra]
#37:$FORM{filter[0][field]}=[name_e]

my @FILTER = ();

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = fileparse($0,@extlist);
#open(LOG,"> $FindBin::Bin/logs/$COOKIE{'ag_annotation.session'}.$cgi_name.txt");
#print LOG "\n[$logtime]:$0\n";
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
#	print LOG __LINE__,":\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
#}
#foreach my $key (sort keys(%ENV)){
#	print LOG "ENV{$key}=[",$ENV{$key},"]\n";
#}

#print LOG __LINE__,":\@FILTER=[",encode_json(\@FILTER),"]\n";

&setDefParams(\%FORM,\%COOKIE);
#foreach my $key (sort keys(%FORM)){
#	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}
&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
#foreach my $key (sort keys(%FORM)){
#	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}

#my $bp3d_table = &getBP3DTablename($FORM{version});

#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $IMAGES = {
	"records" => [],
	"total" => 0,
	"rep_num" => undef
};

#unless(&existsTable($bp3d_table)){
##	my $json = to_json($IMAGES);
#	my $json = encode_json($IMAGES);
#	$json =~ s/"(true|false)"/$1/mg;
#	print $json;
#	print LOG __LINE__,":",$json,"\n";
#	close(LOG);
#	exit;
#}

umask(0);

my $cache_file;
if(scalar @FILTER == 0){
#	my $cache_path = File::Spec->catdir($FindBin::Bin,qq|cache_fma|,$FORM{'version'},$cgi_name,$FORM{'lng'},$FORM{'t_type'});
	my $cache_path = &getCachePath(\%FORM,$cgi_name);
	&File::Path::mkpath($cache_path,0,0777) unless(-e $cache_path);

	$cache_file = File::Spec->catfile($cache_path,qq|list|);
#	$cache_file = qq|$cache_path/list|;
	if(exists($FORM{'dir'}) && exists($FORM{'sort'})){
		$cache_file .= qq|_$FORM{'sort'}|;
		$cache_file .= qq|_$FORM{"dir"}|;
	}

	$cache_file .= qq|_|;
	$cache_file .= qq|$FORM{"limit"}| if(exists($FORM{limit}));
	$cache_file .= qq|_|;
	$cache_file .= qq|$FORM{"start"}| if(exists($FORM{start}));

	$cache_file .= qq|.txt|;
	unlink $cache_file if(-e $cache_file);#DEBUG
	if(-e $cache_file && -s $cache_file){
		local $/ = undef;
		open(IN,"< $cache_file");
		flock(IN,1);
		my $json = <IN>;
		close(IN);
#		my $json = join('',@CACHE);
#		print $json;
#		print LOG $json,"\n";
#		close(LOG);
		&cgi_lib::common::printContent($json);
		exit;
	}else{
		open(CACHE,"> $cache_file");
		flock(CACHE,2);
	}
}


my $sql;
$sql  = qq|select * from (|;

$sql .= qq|select|;
$sql .= qq| rep_id as b_id|;
$sql .= qq|,cdi_name as f_id|;
$sql .= qq|,cdi_name as b_comid|;
$sql .= qq|,cdi_name_j as name_j|;
$sql .= qq|,COALESCE(cd_name,cdi_name_e) as name_e|;
$sql .= qq|,cdi_name_k as name_k|;
$sql .= qq|,cdi_name_l as name_l|;
$sql .= qq|,cdi_syn_j as syn_j|;
$sql .= qq|,COALESCE(cd_syn,cdi_syn_e) as syn_e|;
$sql .= qq|,null as organsys_j|;
$sql .= qq|,null as organsys_e|;
$sql .= qq|,null as phase|;
$sql .= qq|,cdi_taid as taid|;

$sql .= qq|,rep_xmin as xmin|;
$sql .= qq|,rep_xmax as xmax|;
$sql .= qq|,rep_ymin as ymin|;
$sql .= qq|,rep_ymax as ymax|;
$sql .= qq|,rep_zmin as zmin|;
$sql .= qq|,rep_zmax as zmax|;
$sql .= qq|,rep_volume as volume|;
$sql .= qq|,rep_cube_volume as cube_volume|;
$sql .= qq|,(rep_density_objs::real/rep_density_ends::real) as density|;

$sql .= qq|,rep_primitive as primitive|;
$sql .= qq|,null as state|;
$sql .= qq|,rep_delcause|;
$sql .= qq|,EXTRACT(EPOCH FROM rep_entry) as entry|;
$sql .= qq|,EXTRACT(EPOCH FROM rep_entry) as lastmod|;
$sql .= qq|,rep_openid as e_openid|;
$sql .= qq|,rep_openid as m_openid|;
$sql .= qq|,seg_color|;
$sql .= qq| from view_representation as rep|;
#$sql .= qq| left join (select f_id,f_name_j,f_name_e,f_name_k,f_name_l,f_syn_j,f_syn_e from fma) as f on rep.f_id=f.f_id|;

$sql .= qq| left join (select ci_id,cb_id,cdi_id,seg_id,cd_name,cd_syn from concept_data) as cd on cd.ci_id = rep.ci_id AND cd.cb_id = rep.cb_id AND cd.cdi_id = rep.cdi_id|;
$sql .= qq| left join (select seg_id,seg_name,seg_color,seg_thum_bgcolor,seg_thum_bocolor from concept_segment) as cs on cs.seg_id = cd.seg_id|;


=pod
{type:'string',  dataIndex:'common_id'},
{type:'string',  dataIndex:'b_id'},
{type:'string',  dataIndex:'name_j'},
{type:'string',  dataIndex:'name_e'},
{type:'string',  dataIndex:'name_k'},
{type:'string',  dataIndex:'name_l'},
{type:'numeric', dataIndex:'phase'},
{type:'date',    dataIndex:'entry'},
{type:'numeric', dataIndex:'xmin'},
{type:'numeric', dataIndex:'xmax'},
{type:'numeric', dataIndex:'ymin'},
{type:'numeric', dataIndex:'ymax'},
{type:'numeric', dataIndex:'zmin'},
{type:'numeric', dataIndex:'zmax'},
{type:'numeric', dataIndex:'volume'},
{type:'string',  dataIndex:'organsys'},
{type:'string',  dataIndex:'state'}
=cut

my @bind_values = ();
my $where =<<SQL;
(rep.ci_id,rep.cb_id,rep.md_id,rep.mv_id,rep.mr_id,rep.bul_id,rep.cdi_id) in (
select
 ci_id,
 cb_id,
 md_id,
 mv_id,
 max(mr_id) as mr_id,
 bul_id,
 cdi_id
from
 representation
where
 ci_id=$FORM{ci_id} and
 cb_id=$FORM{cb_id} and
 md_id=$FORM{md_id} and
 mv_id=$FORM{mv_id} and
 mr_id<=$FORM{mr_id} and
 bul_id=? and
 rep_delcause is null
group by
 ci_id,
 cb_id,
 md_id,
 mv_id,
 bul_id,
 cdi_id
)
SQL
push(@bind_values,$FORM{bul_id});
my @WHERE = ($where);
#print LOG __LINE__,":\@FILTER=[",(scalar @FILTER),"]\n";
if(scalar @FILTER > 0){
	my $operator = &get_ludia_operator();
	my $space = qq|　|;
	utf8::decode($space) unless(utf8::is_utf8($space));

	foreach my $filter (@FILTER){
#		print LOG __LINE__,":\$filter=[$filter]\n";
		next unless(defined $filter);
#		print LOG __LINE__,":\$filter->{data}->{type}=[$filter->{data}->{type}]\n";
		if($filter->{data}->{type} eq "string"){
			my $query = $filter->{data}->{value};
			utf8::decode($query) unless(utf8::is_utf8($query));
			$query =~ s/$space/ /g;
			utf8::encode($query);
			if($filter->{field} =~ /^name_/){
				push(@WHERE,qq|COALESCE(b_$filter->{field},f_$filter->{field}) $operator ?|); push(@bind_values,qq|*D+ $query|);
			}elsif($filter->{field} eq "b_id"){
				push(@WHERE,qq|$filter->{field} ~ ?|); push(@bind_values,qq|$query|);
			}elsif($filter->{field} eq "common_id"){
				push(@WHERE,qq|b_comid ~ ?|); push(@bind_values,qq|$query|);
			}else{
				push(@WHERE,qq|b_$filter->{field} ~ ?|); push(@bind_values,qq|$query|);
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
				push(@WHERE,qq|to_date(to_char(b_$filter->{field},'YYYY/MM/DD'),'YYYY/MM/DD') $comparison to_date(?,'YYYY/MM/DD')|); push(@bind_values,qq|$query|);
			}else{
				push(@WHERE,qq|b_$filter->{field} $comparison ?|); push(@bind_values,qq|$query|);
			}
		}
	}
#	print LOG __LINE__,":\@bind_values=[",join("\n",@bind_values),"]\n";
}
$sql .= qq| where |.join(" and ",@WHERE) if(scalar @WHERE > 0);
$sql .= qq|) as a where zmin is not null and zmax is not null|;

if(exists($FORM{'dir'}) && exists($FORM{'sort'})){
	my $key = $FORM{'sort'};
#	$key = "b_id" if($key eq "f_id");
	$key = "b_comid" if($key eq "common_id");
	if($key eq "organsys"){
#		$key = "f_$key";
		if($FORM{lng} eq "ja"){
			$key .= "_j";
		}else{
			$key .= "_e";
		}
	}else{
#		$key = "f_$key" unless($key =~ /^f_/);
	}
	$sql .= qq| order by $key $FORM{'dir'}|;
}else{
#	$sql .= qq| order by f_name_k|;
	$sql .= qq| order by name_k|;
}
$sql .= qq| NULLS LAST|;

my $sth = $dbh->prepare($sql);
if(scalar @bind_values > 0){
	$sth->execute(@bind_values);
}else{
	$sth->execute();
}
$IMAGES->{total} = $sth->rows;
$sth->finish;

$IMAGES->{'rep_num'}->{$FORM{bul_id}} = $IMAGES->{total};

my $bul_sql=<<SQL;
select
 bul_id
from
 representation
where
 ci_id=? and
 cb_id=? and
 md_id=? and
 mv_id=? and
 bul_id<>?
group by
 bul_id
SQL
my $bul_sth = $dbh->prepare($bul_sql);
$bul_sth->execute($FORM{'ci_id'},$FORM{'cb_id'},$FORM{'md_id'},$FORM{'mv_id'},$FORM{'bul_id'});
my $bul_id;
my $column_number = 0;
$bul_sth->bind_col(++$column_number, \$bul_id, undef);
while($bul_sth->fetch){
	next unless(defined $bul_id);
	$bind_values[0] = $bul_id;
	$sth->execute(@bind_values);
	$IMAGES->{'rep_num'}->{$bul_id} = $sth->rows;
	$sth->finish;
}
$bul_sth->finish;
undef $bul_sth;
undef $sth;

$bind_values[0] = $FORM{bul_id};

$sql .= qq| limit $FORM{limit}| if(exists($FORM{limit}));
$sql .= qq| offset $FORM{start}| if(exists($FORM{start}));

#print LOG __LINE__,":sql=[$sql]\n";

$sth = $dbh->prepare($sql) or die $sth->errstr;

if(scalar @bind_values > 0){
	$sth->execute(@bind_values) or die $sth->errstr;
}else{
	$sth->execute() or die $sth->errstr;
}

#$IMAGES->{total} = $sth->rows;

my($a_id,$a_pid,$a_order,$a_fmaid,$a_name_j,$a_name_e,$a_name_k,$a_name_l,$a_syn_j,$a_syn_e,$a_detail_j,$a_detail_e,$a_organsys_j,$a_organsys_e,$a_phase,$a_taid,$b_xmin,$b_xmax,$b_ymin,$b_ymax,$f_zmin,$f_zmax,$f_volume,$a_delcause,$a_entry,$a_modified,$e_openid,$m_openid,$num,$b_state,$b_id,$b_comid,$b_cube_volume,$b_density,$b_primitive,$seg_color);

$column_number = 0;
$sth->bind_col(++$column_number, \$b_id, undef);
$sth->bind_col(++$column_number, \$a_fmaid, undef);
$sth->bind_col(++$column_number, \$b_comid, undef);
$sth->bind_col(++$column_number, \$a_name_j, undef);
$sth->bind_col(++$column_number, \$a_name_e, undef);
$sth->bind_col(++$column_number, \$a_name_k, undef);
$sth->bind_col(++$column_number, \$a_name_l, undef);
$sth->bind_col(++$column_number, \$a_syn_j, undef);
$sth->bind_col(++$column_number, \$a_syn_e, undef);
$sth->bind_col(++$column_number, \$a_organsys_j, undef);
$sth->bind_col(++$column_number, \$a_organsys_e, undef);
$sth->bind_col(++$column_number, \$a_phase, undef);
$sth->bind_col(++$column_number, \$a_taid, undef);
$sth->bind_col(++$column_number, \$b_xmin, undef);
$sth->bind_col(++$column_number, \$b_xmax, undef);
$sth->bind_col(++$column_number, \$b_ymin, undef);
$sth->bind_col(++$column_number, \$b_ymax, undef);
$sth->bind_col(++$column_number, \$f_zmin, undef);
$sth->bind_col(++$column_number, \$f_zmax, undef);
$sth->bind_col(++$column_number, \$f_volume, undef);
$sth->bind_col(++$column_number, \$b_cube_volume, undef);
$sth->bind_col(++$column_number, \$b_density, undef);
$sth->bind_col(++$column_number, \$b_primitive, undef);
$sth->bind_col(++$column_number, \$b_state, undef);
$sth->bind_col(++$column_number, \$a_delcause, undef);
$sth->bind_col(++$column_number, \$a_entry, undef);
$sth->bind_col(++$column_number, \$a_modified, undef);
$sth->bind_col(++$column_number, \$e_openid, undef);
$sth->bind_col(++$column_number, \$m_openid, undef);
$sth->bind_col(++$column_number, \$seg_color, undef);

while($sth->fetch){
	my $name;
	my $organsys;
	if($FORM{lng} eq "ja"){
		$name = $a_name_j;
		$organsys = $a_organsys_j;
	}else{
		$name = $a_name_e;
		$organsys = $a_organsys_e;
	}

	my $icon_path = &getImagePath($a_fmaid,'rotate',$FORM{'version'},'16x16',$FORM{'t_type'});

	my $HASH = {
		f_id       => $a_fmaid,
		b_id       => $b_id,
		common_id  => $b_comid,
		name_j     => $a_name_j,
		name_e     => $a_name_e,
		name_k     => $a_name_k,
		name_l     => $a_name_l,
		syn_j      => $a_syn_j,
		syn_e      => $a_syn_e,
		organsys_j => $a_organsys_j,
		organsys_e => $a_organsys_e,
		organsys   => $organsys,
		phase      => $a_phase,
		taid       => $a_taid,
		xmin       => $b_xmin+0,
		xmax       => $b_xmax+0,
		ymin       => $b_ymin+0,
		ymax       => $b_ymax+0,
		zmin       => $f_zmin+0,
		zmax       => $f_zmax+0,
		volume     => $f_volume+0,
		cube_volume=> $b_cube_volume+0,
		density    => $b_density+0,
		primitive  => ($b_primitive ? JSON::XS::true : JSON::XS::false),
		state      => $b_state,
		entry      => $a_entry+0,
		lastmod    => $a_modified+0,

		icon       => defined $icon_path && -e $icon_path ? qq|$icon_path?|.(stat($icon_path))[9] : undef,
		seg_color  => $seg_color,
	};
	if($lsdb_Auth){
		$HASH->{delcause} = $a_delcause;
		$HASH->{m_openid} = $m_openid;
	}
#	foreach my $key (keys(%$HASH)){
#		utf8::decode($HASH->{$key}) if(defined $HASH->{$key});
#	}

	push(@{$IMAGES->{records}},$HASH);
	undef $name;
}
$sth->finish;
undef $sth;

#my $json = to_json($IMAGES);
my $json = &cgi_lib::common::printContentJSON($IMAGES);
#$json =~ s/"(true|false)"/$1/mg;

#print $json;
#print LOG __LINE__,":",$json,"\n";

if(defined $cache_file){
	print CACHE $json;
	close(CACHE);
}

#close(LOG);
exit;

