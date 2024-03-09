#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
#use Image::Info qw(image_info dim);
#use Image::Magick;
use Storable;
#use SetEnv;
use File::Basename;
use File::Path;
use File::Spec;
use File::Spec::Functions qw(catdir catfile);
use Digest::MD5 qw(md5 md5_hex md5_base64);
use Clone;

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI::Cookie;
use Cwd;
use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/IM|,&Cwd::abs_path(qq|$FindBin::Bin/../../ag-common/lib|);
use cgi_lib::common;

require "common.pl";
require "common_db.pl";
require "common_zrangeobject.pl";
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
$FORM{$_} = &cgi_lib::common::decodeUTF8($FORM{$_}) for(keys(%FORM));

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
=pod
my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
my $filetime = sprintf("%04d/%02d/%02d",$year+1900,$mon+1,$mday);
my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);
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
print $LOG "\n[$logtime]:$0\n";
foreach my $key (sort keys(%FORM)){
	print $LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
}
=cut
my $CACHE;
my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0, qr/\..*$/);
my $LOG = &cgi_lib::common::getLogFH(\%FORM,\%COOKIE);
&cgi_lib::common::message(\%FORM, $LOG) if(defined $LOG);

foreach my $key (sort keys(%FORM)){
	if($key =~ /filter/){
		my $key2 = &url_decode($key);
#		print $LOG __LINE__,":\$FORM{$key2}=[",$FORM{$key},"]\n";
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
#		print $LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
	}
}


#foreach my $key (sort keys(%COOKIE)){
#	print $LOG "\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
#}
#foreach my $key (sort keys(%ENV)){
#	print $LOG "\$ENV{$key}=[",$ENV{$key},"]\n";
#}

#foreach my $key (sort keys(%FORM)){
#	print $LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}
&setDefParams(\%FORM,\%COOKIE);
&cgi_lib::common::message(\%FORM, $LOG) if(defined $LOG);

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
&cgi_lib::common::message(\%FORM, $LOG) if(defined $LOG);

my $md_id=$FORM{'md_id'};
my $mv_id=$FORM{'mv_id'};
my $mr_id=$FORM{'mr_id'};
my $bul_id=$FORM{'bul_id'};
my $ci_id=$FORM{'ci_id'};
my $cb_id=$FORM{'cb_id'};


$SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit";
sub sigexit{
	my($date) = `date`;
	$date =~ s/\s*$//g;
	print STDERR "[$date] KILL THIS CGI!![$ENV{SCRIPT_NAME}]\n";
	exit(1);
}

#####
#####
#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $IMAGES = {
	"records" => [],
	"total" => 0,
	"success" => JSON::XS::false
};

#unless(defined $FORM{'t_type'} && defined $bp3d_table){
unless(defined $FORM{'t_type'} && defined $FORM{'version'}){
	$IMAGES->{'success'} = JSON::XS::true;
#	my $json = &JSON::XS::encode_json($IMAGES);
#	if(exists($FORM{'callback'})){
#		print $FORM{'callback'},"(",$json,")";
#	}else{
#		print $json;
#	}
#	print $LOG __LINE__.':'.$json."\n";
	&cgi_lib::common::printContentJSON($IMAGES,\%FORM);
	close($LOG) if(defined $LOG);
	exit;
}
&cgi_lib::common::message('', $LOG) if(defined $LOG);

#77:$FORM{'segments'}=[[{"disp":"Head","value":"head","zmin":1431.1,"zmax":null},{"disp":"Upper body","value":"body","zmin":914.2,"zmax":1431.1},{"disp":"Leg","value":"leg","zmin":null,"zmax":914.2},{"disp":"Head+Upper body","value":"head-body","zmin":"[1431.1,914.2]","zmax":"[null,1431.1]"},{"disp":"Upper body+Leg","value":"body-leg","zmin":"[914.2 , null]","zmax":"[1431.1,914.2]"},{"disp":"All","value":"all","zmin":"[1431.1,914.2,null]","zmax":"[null,1431.1,914.2]"},{"disp":"None","value":"none","zmin":null,"zmax":null}]]
#78:$FORM{'cuboid_volumes'}=[[{"disp":"10未満","value":"x-10","min":null,"max":10},{"disp":"10以上100未満","value":"10-100","min":10,"max":100},{"disp":"100以上1000未満","value":"100-1000","min":100,"max":1000},{"disp":"1000以上","value":"1000-x","min":1000,"max":null}]]

#my $cache_file = qq|$FindBin::Bin/cache_fma/$FORM{'version'}/$cgi_name/|;
#my $cache_path = &catdir($FindBin::Bin,qq|cache_fma|,$FORM{'version'},$cgi_name);
my $form = &Clone::clone(\%FORM);
delete $form->{$_} for(qw|lng position|);

my $cache_path = &getCachePath($form,$cgi_name);
unless(-e $cache_path){
	umask(0);
	&File::Path::mkpath($cache_path,0,0777) or die;
}

$form = &Clone::clone(\%FORM);
delete $form->{$_} for(qw|lng position sorttype t_type version md_id mv_id mr_id ci_id cb_id bul_id degenerate_same_shape_icons|);
if(exists $form->{'segments'} && defined $form->{'segments'} && length $form->{'segments'} && exists $form->{'cuboid_volumes'} && defined $form->{'cuboid_volumes'} && length $form->{'cuboid_volumes'}){
	delete $form->{$_} for(qw|cvmin cvmax zmin zmax|);
}

my @TEMP = map {qq|$_=|.(exists $form->{$_} && defined $form->{$_} ? $form->{$_} : '')} sort keys(%$form);
&cgi_lib::common::message(\@TEMP, $LOG) if(defined $LOG);
#print $LOG __LINE__.':'.join("&",@TEMP)."\n";
#print $LOG __LINE__.':'.&Digest::MD5::md5_hex(join("&",@TEMP))."\n";
my $cache_file = &catfile($cache_path,&Digest::MD5::md5_hex(join("&",@TEMP)));
unlink $cache_file if(-e $cache_file);#DEBUG
#print $LOG __LINE__.':'.$cache_file."\n";
#unlink $cache_file if(-e $cache_file);
if(-e $cache_file && -s $cache_file){
	if(open(IN,"< $cache_file")){
		flock(IN,1);
		my $json = <IN>;
		close(IN);
		if(defined $json && length($json)>0){
#			if(exists($FORM{'callback'})){
#				print $FORM{'callback'},"(",$json,")";
#			}else{
#				print $json;
#			}
			&cgi_lib::common::printContentJSON($json,\%FORM);
			print $LOG __LINE__.':'.$json."\n";
			close($LOG);
			exit;
		}
	}
}else{
	open($CACHE,"> $cache_file") or die;
	flock($CACHE,2);
}

=pod
my $sql_rep_sub = qq|
select
 *
from
 representation as rep,
 concept_data as cd,
 concept_data_info as cdi,
 concept_segment as cs

where
 cd.ci_id   = rep.ci_id and
 cd.cb_id   = rep.cb_id and
 cd.cdi_id  = rep.cdi_id and
 cdi.ci_id  = rep.ci_id and
 cdi.cdi_id = rep.cdi_id and
 cs.seg_id  = cd.seg_id and
 rep_delcause is null AND (md_id,mv_id,mr_id,bul_id,rep.cdi_id) in (select md_id,mv_id,max(mr_id),bul_id,cdi_id from representation where md_id=$md_id and mv_id=$mv_id and mr_id<=$mr_id and bul_id=$bul_id group by md_id,mv_id,bul_id,cdi_id)
|;
if(1){
	my @W;
	push(@W, 'rep_primitive') if($FORM{'primitive'} eq 'true');

	if((exists $FORM{'density_max'} && defined $FORM{'density_max'} && $FORM{'density_max'} =~ /^[0-9\.]+$/) || (exists $FORM{'density_min'} && defined $FORM{'density_min'} && $FORM{'density_min'} =~ /^[0-9\.]+$/)){
		my $sql_rep_density = qq|rep_primitive=false and CASE WHEN rep_density_objs>0 AND rep_density_ends>0 THEN (rep_density_objs::real/rep_density_ends::real) ELSE 0 END|;
		if(exists $FORM{'density_max'} && defined $FORM{'density_max'} && $FORM{'density_max'} =~ /^[0-9\.]+$/ && exists $FORM{'density_min'} && defined $FORM{'density_min'} && $FORM{'density_min'} =~ /^[0-9\.]+$/){
			push(@W,qq|($sql_rep_density<$FORM{'density_max'} AND $sql_rep_density>=$FORM{'density_min'})|);
		}
		elsif(exists $FORM{'density_max'} && defined $FORM{'density_max'} && $FORM{'density_max'} =~ /^[0-9\.]+$/){
			push(@W,qq|$sql_rep_density<$FORM{'density_max'}|);
		}
		elsif(exists $FORM{'density_min'} && defined $FORM{'density_min'} && $FORM{'density_min'} =~ /^[0-9\.]+$/){
			push(@W,qq|$sql_rep_density>=$FORM{'density_min'}|);
		}
	}
	$sql_rep_sub .= ' and (('.join(') or (',@W).'))' if(scalar @W > 0);

	if(exists $FORM{'filter'} && defined $FORM{'filter'} && length $FORM{'filter'}){
		my $filter = $FORM{'filter'};
		$sql_rep_sub .= qq| and cdf_name='$filter'|;
	}
	$sql_rep_sub .= qq| and cdi_taid is not null| if(exists $FORM{'only_ta'} && defined $FORM{'only_ta'} && $FORM{'only_ta'} eq 'true');
}
=cut
my $sql_rep_sub = &get_sql_rep_sub(%FORM);
&cgi_lib::common::message($sql_rep_sub, $LOG) if(defined $LOG);

my $BUL_ID_TOTAL;

my $cuboid_volumes;
my $segments;
if(exists $FORM{'cuboid_volumes'} && defined $FORM{'cuboid_volumes'} && exists $FORM{'segments'} && defined $FORM{'segments'}){
	eval{
		$cuboid_volumes = &cgi_lib::common::decodeJSON($FORM{'cuboid_volumes'});
		$segments = &cgi_lib::common::decodeJSON($FORM{'segments'});
		if(defined $cuboid_volumes && ref $cuboid_volumes eq 'ARRAY' && defined $segments && ref $segments eq 'ARRAY'){
&cgi_lib::common::message($cuboid_volumes, $LOG) if(defined $LOG);
&cgi_lib::common::message($segments, $LOG) if(defined $LOG);

			my %REP;

#=pod
#SQLで修正する場合、バグがある為、後で修正
			my $sql_rep = qq|
select
 COALESCE(cszr_abbr,'ANY') as cszr_abbr,
 COALESCE(csv_abbr,'any') as csv_abbr,
 total
from (
  select cszr_id,csv_id,count(*) as total from ($sql_rep_sub) as rep group by cszr_id,csv_id
 UNION
  select cszr_id,-1 as csv_id,count(*) as total from ($sql_rep_sub) as rep group by cszr_id
 UNION
  select -1 as cszr_id,csv_id,count(*) as total from ($sql_rep_sub) as rep group by csv_id
 UNION
  select -1 as cszr_id,-1 as csv_id,count(*) as total from ($sql_rep_sub) as rep
) as rep
left join (
 select * from concept_segment_zrange
) as cszr on rep.cszr_id=cszr.cszr_id
left join (
 select * from concept_segment_volume
) as csv on rep.csv_id=csv.csv_id
order by
 rep.cszr_id,
 rep.csv_id
|;
&cgi_lib::common::message($sql_rep, $LOG) if(defined $LOG);
			my $sth_rep = $dbh->prepare($sql_rep) or die $dbh->errstr;
			$sth_rep->execute() or die $dbh->errstr;
			while(my $hash_ref = $sth_rep->fetchrow_hashref){
				$REP{$hash_ref->{'csv_abbr'}}->{$hash_ref->{'cszr_abbr'}} = $hash_ref->{'total'}-0;
			}
			$sth_rep->finish;
			undef $sth_rep;
&cgi_lib::common::message(\%REP, $LOG) if(defined $LOG);
#=cut
			my $form = {};
			$form->{$_} = $FORM{$_} for(keys(%FORM));
			foreach my $cub (@$cuboid_volumes){
				$form->{'cvmin'} = $cub->{'min'};
				$form->{'cvmax'} = $cub->{'max'};
				foreach my $seg (@$segments){
					$form->{'zmin'} = $seg->{'zmin'};
					$form->{'zmax'} = $seg->{'zmax'};
=pod
#旧ロジック
					my $ret = &getZRangeObjects($dbh,$form,$LOG);
					next unless(defined $ret);
					push(@{$seg->{'totals'}},{
						'total' => $ret->{'total'},
						'cuboid_value' => $cub->{'value'},
						'segment_value' => $seg->{'value'}
					});
=cut

#=pod
#SQLで修正する場合、バグがある為、後で修正
					my $cuboid_value = $cub->{'value'};
					my $segment_value = $seg->{'value'};
					$segment_value = 'O' if($segment_value eq 'HUL');
					if(exists $REP{$cuboid_value} && defined $REP{$cuboid_value} && exists $REP{$cuboid_value}->{$segment_value} && defined $REP{$cuboid_value}->{$segment_value}){
						push(@{$seg->{'totals'}},{
							'total' => $REP{$cuboid_value}->{$segment_value},
							'cuboid_value' => $cub->{'value'},
							'segment_value' => $seg->{'value'}
						});
					}else{
						push(@{$seg->{'totals'}},{
							'total' => 0,
							'cuboid_value' => $cub->{'value'},
							'segment_value' => $seg->{'value'}
						});
					}
#=cut
				}
			}
		}
	};
	if($@){
		print $LOG __LINE__.':'.$@."\n";
	}
}elsif(exists $FORM{'segments'} && defined $FORM{'segments'}){
	eval{
		$segments = &cgi_lib::common::decodeJSON($FORM{'segments'});
		if(defined $segments && ref $segments eq 'ARRAY'){
=pod
			my $form = {};
			$form->{$_} = $FORM{$_} for(keys(%FORM));
			foreach my $seg (@$segments){
				$form->{'zmin'} = $seg->{'zmin'};
				$form->{'zmax'} = $seg->{'zmax'};
				my $ret = &getZRangeObjects($dbh,$form,$LOG);
				$seg->{'total'} = $ret->{'total'} if(defined $ret);
			}
=cut

			my %REP;
			my $sql_rep = qq|
select
 COALESCE(cszr_abbr,'ANY') as cszr_abbr,
 total
from (
  select cszr_id,count(*) as total from ($sql_rep_sub) as rep group by cszr_id
 UNION
  select -1 as cszr_id,count(*) as total from ($sql_rep_sub) as rep
) as rep
left join (
 select * from concept_segment_zrange
) as cszr on rep.cszr_id=cszr.cszr_id
order by
 rep.cszr_id
|;
&cgi_lib::common::message($sql_rep, $LOG) if(defined $LOG);
			my $sth_rep = $dbh->prepare($sql_rep) or die $dbh->errstr;
			$sth_rep->execute() or die $dbh->errstr;
			while(my $hash_ref = $sth_rep->fetchrow_hashref){
				$REP{$hash_ref->{'csv_abbr'}}->{$hash_ref->{'cszr_abbr'}} = $hash_ref->{'total'}-0;
			}
			$sth_rep->finish;
			undef $sth_rep;
&cgi_lib::common::message(\%REP, $LOG) if(defined $LOG);

			foreach my $seg (@$segments){
				my $segment_value = $seg->{'value'};
				$segment_value = 'O' if($segment_value eq 'HUL');
				if(exists $REP{$segment_value} && defined $REP{$segment_value}){
					$seg->{'total'} = $REP{$segment_value};
				}else{
					$seg->{'total'} = 0;
				}
			}
		}
	};
	if($@){
		print $LOG __LINE__.':'.$@."\n";
	}
}

eval{
	my $sql=<<SQL;
select
 bul_id
from
 representation
where
 rep_delcause is null and
 (ci_id,cb_id,md_id,mv_id,mr_id,cdi_id) in
  (select
    ci_id,
    cb_id,
    md_id,
    mv_id,
    max(mr_id) as mr_id,
    cdi_id
   from
    representation
   where
    ci_id= $ci_id and
    cb_id= $cb_id and
    md_id= $md_id and
    mv_id= $mv_id and
    mr_id<=$mr_id
   group by
    ci_id,
    cb_id,
    md_id,
    mv_id,
    cdi_id
  )
group by
 bul_id
SQL
#print $LOG __LINE__.':'.$sql."\n";
	my $bul_id;
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$sth->bind_col(1, \$bul_id, undef);
	while($sth->fetch){
		$BUL_ID_TOTAL->{$bul_id} = undef if(defined $bul_id && $FORM{'bul_id'} ne $bul_id);
	}
	$sth->finish;
	undef $sth;

	foreach my $bul_id (keys(%$BUL_ID_TOTAL)){
		my $form = {};
		$form->{$_} = $FORM{$_} for(keys(%FORM));
		$form->{'bul_id'} = $bul_id;
#		$BUL_ID_TOTAL->{$bul_id} = &getZRangeObjects($dbh,$form,$LOG);
		$BUL_ID_TOTAL->{$bul_id} = {
			records => [],
			total => 0,
			success => JSON::XS::true
		};
		my $sql = &get_sql_cdi_name(&get_sql_rep_sub(%$form),%$form);

		my $cdi_name;
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$BUL_ID_TOTAL->{$bul_id}->{'total'} = $sth->rows();
		$sth->bind_col(1, \$cdi_name, undef);
		while($sth->fetch){
			push(@{$BUL_ID_TOTAL->{$bul_id}->{'records'}},$cdi_name);
		}
		$sth->finish;
		undef $sth;
		$BUL_ID_TOTAL->{$bul_id}->{'success'} = JSON::XS::true;
	}
};
if($@){
	print $LOG __LINE__.':'.$@."\n";
}

eval{
#	$IMAGES = &getZRangeObjects($dbh,\%FORM,$LOG);
	my $sql = &get_sql_cdi_name($sql_rep_sub,%FORM);

	$IMAGES->{'records'} = [];
	$IMAGES->{'total'} = 0;

	my $cdi_name;
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$IMAGES->{'total'} = $sth->rows();
	$sth->bind_col(1, \$cdi_name, undef);
	while($sth->fetch){
		push(@{$IMAGES->{'records'}},$cdi_name);
	}
	$sth->finish;
	undef $sth;

	$IMAGES->{'success'} = JSON::XS::true;
};
if($@){
	print $LOG __LINE__.':'.$@."\n";
}

$IMAGES->{'segments'} = $segments if(defined $segments);

$IMAGES->{'other'} = $BUL_ID_TOTAL if(defined $BUL_ID_TOTAL);

my $json = &cgi_lib::common::printContentJSON($IMAGES,\%FORM);
print $CACHE $json;
close($CACHE);

&cgi_lib::common::message($IMAGES,$LOG) if(defined $LOG);
close($LOG);
exit;

sub get_sql_rep_sub {
	my %FORM = @_;

	my $md_id=$FORM{'md_id'};
	my $mv_id=$FORM{'mv_id'};
	my $mr_id=$FORM{'mr_id'};
	my $bul_id=$FORM{'bul_id'};
	my $ci_id=$FORM{'ci_id'};
	my $cb_id=$FORM{'cb_id'};

	my $sql_rep_sub;
=pod
	$sql_rep_sub = qq|
select
 *
from
 representation as rep,
 concept_data as cd,
 concept_data_info as cdi,
 concept_segment as cs

where
 cd.ci_id   = rep.ci_id and
 cd.cb_id   = rep.cb_id and
 cd.cdi_id  = rep.cdi_id and
 cdi.ci_id  = rep.ci_id and
 cdi.cdi_id = rep.cdi_id and
 cs.seg_id  = cd.seg_id and
 rep_delcause is null AND (md_id,mv_id,mr_id,bul_id,rep.cdi_id) in (select md_id,mv_id,max(mr_id),bul_id,cdi_id from representation where md_id=$md_id and mv_id=$mv_id and mr_id<=$mr_id and bul_id=$bul_id group by md_id,mv_id,bul_id,cdi_id)
|;
=cut
	$sql_rep_sub = qq|
select
 *
from
 representation as rep

left join (
 select * from concept_data as cd
 left join concept_segment as cs on
  cs.seg_id  = cd.seg_id
) as cd on
 cd.ci_id   = rep.ci_id and
 cd.cb_id   = rep.cb_id and
 cd.cdi_id  = rep.cdi_id

left join (
 select * from buildup_data as bd
 left join concept_segment as cs on
  cs.seg_id  = bd.seg_id
) as bd on
 bd.md_id   = rep.md_id and
 bd.mv_id   = rep.mv_id and
 bd.mr_id   = rep.mr_id and
 bd.ci_id   = rep.ci_id and
 bd.cb_id   = rep.cb_id and
 bd.cdi_id  = rep.cdi_id

left join concept_data_info as cdi on
 cdi.ci_id  = rep.ci_id and
 cdi.cdi_id = rep.cdi_id


where
 rep_delcause is null AND (rep.md_id,rep.mv_id,rep.mr_id,rep.bul_id,rep.cdi_id) in (select md_id,mv_id,max(mr_id),bul_id,cdi_id from representation where md_id=$md_id and mv_id=$mv_id and mr_id<=$mr_id and bul_id=$bul_id group by md_id,mv_id,bul_id,cdi_id)
|;

	my @W;
	push(@W, 'rep_primitive') if($FORM{'primitive'} eq 'true');

	if((exists $FORM{'density_max'} && defined $FORM{'density_max'} && $FORM{'density_max'} =~ /^[0-9\.]+$/) || (exists $FORM{'density_min'} && defined $FORM{'density_min'} && $FORM{'density_min'} =~ /^[0-9\.]+$/)){
		my $sql_rep_density = qq|rep_primitive=false and CASE WHEN rep_density_objs>0 AND rep_density_ends>0 THEN (rep_density_objs::real/rep_density_ends::real) ELSE 0 END|;
		if(exists $FORM{'density_max'} && defined $FORM{'density_max'} && $FORM{'density_max'} =~ /^[0-9\.]+$/ && exists $FORM{'density_min'} && defined $FORM{'density_min'} && $FORM{'density_min'} =~ /^[0-9\.]+$/){
			push(@W,qq|($sql_rep_density<$FORM{'density_max'} AND $sql_rep_density>=$FORM{'density_min'})|);
		}
		elsif(exists $FORM{'density_max'} && defined $FORM{'density_max'} && $FORM{'density_max'} =~ /^[0-9\.]+$/){
			push(@W,qq|$sql_rep_density<$FORM{'density_max'}|);
		}
		elsif(exists $FORM{'density_min'} && defined $FORM{'density_min'} && $FORM{'density_min'} =~ /^[0-9\.]+$/){
			push(@W,qq|$sql_rep_density>=$FORM{'density_min'}|);
		}
	}
	$sql_rep_sub .= ' and (('.join(') or (',@W).'))' if(scalar @W > 0);

	if(exists $FORM{'filter'} && defined $FORM{'filter'} && length $FORM{'filter'}){
		my $filter = $FORM{'filter'};
		$sql_rep_sub .= qq| and COALESCE(cd.cdf_name,bd.cdf_name)='$filter'|;
	}
	$sql_rep_sub .= qq| and cdi_taid is not null| if(exists $FORM{'only_ta'} && defined $FORM{'only_ta'} && $FORM{'only_ta'} eq 'true');

	return $sql_rep_sub;
}

sub get_sql_cdi_name {
	my $sql_rep_sub = shift;
	my %FORM = @_;

	my $sql = qq|select cdi_name from ($sql_rep_sub) as a|;

	my $cszr_id;
	if(exists $FORM{'zmin'} && defined $FORM{'zmin'} && $FORM{'zmin'} =~ /^[0-9\.]+$/ && exists $FORM{'zmax'} && defined $FORM{'zmax'} && $FORM{'zmax'} =~ /^[0-9\.]+$/){
		$cszr_id = 2;
	}
	elsif(exists $FORM{'zmin'} && defined $FORM{'zmin'} && exists $FORM{'zmax'} && defined $FORM{'zmax'}){
		$cszr_id = 0;
	}
	elsif(exists $FORM{'zmin'} && defined $FORM{'zmin'} && $FORM{'zmin'} =~ /^[0-9\.]+$/){
		$cszr_id = 1;
	}
	elsif(exists $FORM{'zmax'} && defined $FORM{'zmax'} && $FORM{'zmax'} =~ /^[0-9\.]+$/){
		$cszr_id = 3;
	}

	my $csv_id;
	if(exists $FORM{'cvmin'} && defined $FORM{'cvmin'} && $FORM{'cvmin'} =~ /^[0-9\.]+$/ && exists $FORM{'cvmax'} && defined $FORM{'cvmax'} && $FORM{'cvmax'} =~ /^[0-9\.]+$/){
		if($FORM{'cvmin'} == 0.1 && $FORM{'cvmax'} == 0.35){
			$csv_id = 2;
		}
		elsif($FORM{'cvmin'} == 0.35 && $FORM{'cvmax'} == 1){
			$csv_id = 3;
		}
		elsif($FORM{'cvmin'} == 1 && $FORM{'cvmax'} == 10){
			$csv_id = 4;
		}
	}
	elsif(exists $FORM{'cvmin'} && defined $FORM{'cvmin'} && $FORM{'cvmin'} =~ /^[0-9\.]+$/){
		$csv_id = 5;
	}
	elsif(exists $FORM{'cvmax'} && defined $FORM{'cvmax'} && $FORM{'cvmax'} =~ /^[0-9\.]+$/){
		$csv_id = 1;
	}

	my @W;
	push(@W,qq|cszr_id=$cszr_id|) if(defined $cszr_id);
	push(@W,qq|csv_id=$csv_id|) if(defined $csv_id);

	if(exists $FORM{'zposition'} && defined $FORM{'zposition'} && $FORM{'zposition'} =~ /^[0-9\.]+$/ && exists $FORM{'zrange'} && defined $FORM{'zrange'} && $FORM{'zrange'} =~ /^[0-9\.]+$/){
		my $zmin = $FORM{'zposition'} - $FORM{'zrange'} / 2;
		my $zmax = $FORM{'zposition'} + $FORM{'zrange'} / 2;
		my @WHERE;
		push(@WHERE,qq|(rep_zmin>=$zmin and rep_zmin<=$zmax)|);
		push(@WHERE,qq|(rep_zmax>=$zmin and rep_zmax<=$zmax)|);
		push(@WHERE,qq|(rep_zmin>=$zmin and rep_zmax<=$zmax)|);
		push(@WHERE,qq|(rep_zmin<=$zmin and rep_zmax>=$zmax)|);
		push(@W,'('.join(' or ',@WHERE).')');
	}

	$sql .= ' where '.join(' and ',@W) if(scalar @W);

&cgi_lib::common::message($sql,$LOG) if(defined $LOG);

	return $sql;
}
