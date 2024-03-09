#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use constant {
#	TIMEOUT => 60*5
	TIMEOUT => 60
};

use JSON::XS;
use Storable;
use File::Basename;
use File::Path;
use File::Spec;
use File::Spec::Functions qw(catdir catfile);

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI::Cookie;
use Cwd;
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'IM'),&Cwd::abs_path(&catdir($FindBin::Bin,'..','..','ag-common','lib'));
use cgi_lib::common;

require "common.pl";
require "common_db.pl";

my $disEnv = &getDispEnv();
my $addPointElementHidden = $disEnv->{addPointElementHidden};
my $dispTreeChildPartsNum = $disEnv->{dispTreeChildPartsNum};
$addPointElementHidden = 'false' unless(defined $addPointElementHidden);
$dispTreeChildPartsNum = 'true' unless(defined $dispTreeChildPartsNum);

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);

my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0, qr/\..*$/);
my $LOG = &cgi_lib::common::getLogFH(\%FORM,\%COOKIE);

&setDefParams(\%FORM,\%COOKIE);

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);

my @TREE = ();

unless(
	exists  $FORM{'version'} &&
	defined $FORM{'version'} &&
	exists  $FORM{'md_id'} &&
	defined $FORM{'md_id'} &&
	exists  $FORM{'mv_id'} &&
	defined $FORM{'mv_id'} &&
	exists  $FORM{'mr_id'} &&
	defined $FORM{'mr_id'} &&
	exists  $FORM{'ci_id'} &&
	defined $FORM{'ci_id'} &&
	exists  $FORM{'cb_id'} &&
	defined $FORM{'cb_id'} &&
	exists  $FORM{'bul_id'} &&
	defined $FORM{'bul_id'} &&
	exists  $FORM{'node'} &&
	defined $FORM{'node'} &&
	($FORM{'node'} eq 'root' || (exists $FORM{'f_pid'} && defined $FORM{'f_pid'}) || (exists $FORM{'pid'} && defined $FORM{'pid'}))
){
	print $LOG __LINE__,":\n";
	&cgi_lib::common::printContentJSON(\@TREE,\%FORM);
	exit;
}
print $LOG __LINE__,":\n";

sub time_out_json {
	my $RTN = {};
	$RTN->{'success'} = JSON::XS::false;
	$RTN->{'msg'}     = 'Request Timeout';
	&cgi_lib::common::printContentJSON($RTN);
	my $tim = alarm 0;
	&cgi_lib::common::message($tim, $LOG) if(defined $LOG);
	exit;
}
local $SIG{'ALRM'} = \&time_out_json;
alarm TIMEOUT;



#my $wt_version = qq|ci_id=$FORM{'ci_id'} and cb_id=$FORM{'cb_id'}|;
#warn  $wt_version = qq|ci_id=$FORM{'ci_id'} and cb_id=$FORM{'cb_id'}|;

#$FORM{version} = "Talairach" if($FORM{'bul_id'} eq "101");


my $lsdb_OpenID;
my $lsdb_Auth;
my $parentURL = $FORM{'parent'} if(exists($FORM{'parent'}));
my $parent_text;
if(defined $parentURL){
	($lsdb_OpenID,$lsdb_Auth) = &openidAuth($parentURL);
}

my $cache_path = &getCachePath(\%FORM,$cgi_name);
&cgi_lib::common::message($cache_path, $LOG) if(defined $LOG);
#print $LOG __LINE__,":\$cache_path=[$cache_path]\n";
unless(-e $cache_path){
	my $old = umask(0);
	&File::Path::make_path($cache_path,{mode=>0777});
	umask($old)
}
if(!exists $FORM{'f_pid'} && exists $FORM{'pid'}){
	my $sth = $dbh->prepare(qq|select cdi_name from concept_data_info where ci_id=$FORM{'ci_id'} and cdi_id=$FORM{'pid'}|) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	my $cdi_name;
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$cdi_name,   undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;
	if(defined $cdi_name && length $cdi_name){
		$FORM{'f_pid'} = $cdi_name;
		delete $FORM{'pid'};
	}
}
my $cache_file;
if(exists $FORM{'f_pid'} && defined $FORM{'f_pid'}){
	$cache_file = &catfile($cache_path,&getBaseDirFromID($FORM{'f_pid'}),qq|$FORM{'f_pid'}.txt|);
}elsif($FORM{'node'} eq 'root' || $FORM{'node'} eq 'trash'){
	$cache_file = &catfile($cache_path,$FORM{'node'},qq|$FORM{'node'}.txt|);
}else{
	&cgi_lib::common::printContentJSON(\@TREE,\%FORM);
	exit;
}

if(defined $cache_file){
	&cgi_lib::common::message($cache_file, $LOG) if(defined $LOG);
	my $d = &File::Basename::dirname($cache_file);
	unless(-e $d){
		my $old = umask(0);
		&File::Path::make_path($d,{mode=>0777});
		umask($old)
	}
}
unlink $cache_file if(-e $cache_file); #DEBUG
if(-e $cache_file && -s $cache_file){
	unlink $cache_file if(-e $cache_file && (stat($cache_file))[9] <= (stat($0))[9]);
	if(-e $cache_file && -s $cache_file){
		my $sql;
		if(exists($FORM{'f_pid'})){
			$sql = qq|
  select
   EXTRACT(EPOCH FROM rep_entry) as rep_entry
  from
    (select * from view_representation
     where
       (md_id,mv_id,mr_id,ci_id,cb_id,bul_id,cdi_id) in
       (select
          md_id,mv_id,max(mr_id),ci_id,cb_id,bul_id,cdi_id
        from
          representation
        where
          md_id=$FORM{md_id} and
          mv_id=$FORM{mv_id} and
          mr_id<=$FORM{mr_id} and
          ci_id=$FORM{ci_id} and
          cb_id=$FORM{cb_id} and
          bul_id=$FORM{bul_id}
        group by
          md_id,mv_id,ci_id,cb_id,bul_id,cdi_id
       )
    ) as rep
  where
   rep_delcause is null and
   cdi_name=?
|;
		}else{
			$sql = qq|
select
  rep.rep_entry
from
  view_buildup_tree as tree
left join (
  select
   EXTRACT(EPOCH FROM rep_entry) as rep_entry,
   cdi_id
  from
    (select * from representation
     where
       (md_id,mv_id,mr_id,ci_id,cb_id,bul_id,cdi_id) in
       (select
          md_id,mv_id,max(mr_id),ci_id,cb_id,bul_id,cdi_id
        from
          representation
        where
          md_id=$FORM{md_id} and
          mv_id=$FORM{mv_id} and
          mr_id<=$FORM{mr_id} and
          ci_id=$FORM{ci_id} and
          cb_id=$FORM{cb_id} and
          bul_id=$FORM{bul_id}
        group by
          md_id,mv_id,ci_id,cb_id,bul_id,cdi_id
       )
    ) as rep
  where
   rep_delcause is null
) as rep on (rep.cdi_id=tree.cdi_id)
where
  but_delcause is null and
  md_id=$FORM{md_id} and
  mv_id=$FORM{mv_id} and
  mr_id=$FORM{mr_id} and
  ci_id=$FORM{ci_id} and
  cb_id=$FORM{cb_id} and
  bul_id=$FORM{bul_id} and
|;
		}
		if(exists($FORM{'f_pid'})){
#			$sql .= qq|cdi_pname=?|;
		}elsif($FORM{'node'} eq "trash"){
			$sql .= qq|but_delcause is not null|;
		}elsif($FORM{'node'} eq "root"){
			$sql .= qq|cdi_pid is null|;
		}

		print $LOG __LINE__,":sql=[$sql]\n";
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		if(exists($FORM{'f_pid'})){
			$sth->execute($FORM{'f_pid'}) or die $dbh->errstr;
		}else{
			$sth->execute() or die $dbh->errstr;
		}
		my $rep_entry;
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$rep_entry,   undef);
		while($sth->fetch){
			$rep_entry = 0 unless(defined $rep_entry);
			unlink $cache_file if(-e $cache_file && (stat($cache_file))[9] <= $rep_entry);
			last unless(-e $cache_file && -s $cache_file);
		}
		$sth->finish;
		undef $sth;
	}
	if(-e $cache_file && -s $cache_file){
		open(my $CACHE, $cache_file) or die qq|$! [$cache_file]|;
		flock($CACHE, 1);
		local $/ = undef;
		my $json = <$CACHE>;
		close($CACHE);
		&cgi_lib::common::printContentJSON($json,\%FORM);
		exit;
	}
}

my %ANN = ();
my %ANN_P = ();
my %ANN_PATH = ();

my $store_file = &catfile($cache_path,qq|tree_$FORM{'bul_id'}\_storable.store|);
my $store2_file = &catfile($cache_path,qq|tree2_$FORM{'bul_id'}\_storable.store|);
my $store_lock = &catfile($cache_path,qq|tree_storable.lock|);

$SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit";
sub sigexit {
	my($date) = `date`;
	$date =~ s/\s*$//g;
	print STDERR "[$date] KILL THIS CGI!![$ENV{SCRIPT_NAME}]\n";
	rmdir $store_lock if(-e $store_lock);
	exit(1);
}

if(!-e $store_file && !mkdir($store_lock)){
	exit if(!exists($ENV{'REQUEST_METHOD'}));
	my $wait = 30;
	while($wait){
		if(-e $store_lock){
			$wait--;
			sleep(1);
			next;
		}
		last;
	}
}
if(-e $store_file && -s $store_file){
	my $href = retrieve($store_file);
	%ANN = %$href;

	$href = retrieve($store2_file);
	%ANN_P = %$href;
}else{
	my $sql = qq|select cdi_id,cdi_pid,cdi_name,cdi_pname from view_buildup_tree where md_id=$FORM{md_id} and mv_id=$FORM{mv_id} and mr_id=$FORM{mr_id} and ci_id=$FORM{ci_id} and cb_id=$FORM{cb_id} and bul_id=$FORM{'bul_id'} and but_delcause is null|;
	my @LIST1 = &ExecuteSQL($sql);
	while(scalar @LIST1 > 0){
		my($a_id,$a_pid,$f_id,$cd_pid) = split(/\t/,shift @LIST1);
		next if(!defined $cd_pid || $cd_pid eq "");
		push(@{$ANN_P{$a_pid}},$a_id);
		$ANN{$a_id} = $a_pid;
		push(@{$ANN_P{$cd_pid}},$f_id);
		$ANN{$f_id} = $cd_pid;
	}
	undef @LIST1;

	store \%ANN, $store_file;
	store \%ANN_P, $store2_file;
	rmdir($store_lock);
}

my $singleClickExpand = JSON::XS::false;
my @LIST1 = ();

#$FORM{'node'} = 'root';

###
###



my $sql=<<SQL;
select
  tree.bul_id,
  f.cdi_name,
  f.cdi_name_j,
  COALESCE(cd.cd_name,f.cdi_name_e),
  COALESCE(t.num,0),
  COALESCE(t2.num,0),
  f.cdi_taid,
  tree.ci_id,
  tree.cb_id,
  bti.but_cnum,
  COALESCE(bu.but_cnum,0)>0 as bu_cnum,
  rep.rep_id,
  rep.primitive,
  rep.density_objs,
  rep.density_ends
from
  buildup_tree as tree

left join (
  select
    md_id,
    mv_id,
    mr_id,
    ci_id,
    cb_id,
    bul_id,
    cdi_id,
    but_cnum
  from
    buildup_tree_info
  where
   md_id=$FORM{md_id} and
   mv_id=$FORM{mv_id} and
   mr_id=$FORM{mr_id} and
   ci_id=$FORM{ci_id} and
   cb_id=$FORM{cb_id}
) as bti on (
  tree.md_id = bti.md_id and 
  tree.mv_id = bti.mv_id and 
  tree.mr_id = bti.mr_id and 
  tree.ci_id = bti.ci_id and 
  tree.cb_id = bti.cb_id and 
  tree.bul_id = bti.bul_id and
  tree.cdi_id = bti.cdi_id
)

left join (
  select
    but1.md_id,
    but1.mv_id,
    but1.mr_id,
    but1.ci_id,
    but1.cb_id,
    but1.bul_id,
    but1.cdi_pid,
    count(but2.cdi_id) as num
  from
    buildup_tree as but1
  left join (
      select * from buildup_tree where md_id=$FORM{md_id} and mv_id=$FORM{mv_id} and mr_id=$FORM{mr_id} and ci_id=$FORM{ci_id} and cb_id=$FORM{cb_id}
   ) as but2 on (
     but1.md_id=but2.md_id and
     but1.mv_id=but2.mv_id and
     but1.mr_id=but2.mr_id and
     but1.ci_id=but2.ci_id and
     but1.cb_id=but2.cb_id and
     but1.bul_id=but2.bul_id and
     but1.cdi_id=but2.cdi_pid
   )
  where
   but1.md_id=$FORM{md_id} and
   but1.mv_id=$FORM{mv_id} and
   but1.mr_id=$FORM{mr_id} and
   but1.ci_id=$FORM{ci_id} and
   but1.cb_id=$FORM{cb_id}
  group by
    but1.md_id,
    but1.mv_id,
    but1.mr_id,
    but1.ci_id,
    but1.cb_id,
    but1.bul_id,
    but1.cdi_pid
 ) as t on (
  tree.md_id = t.md_id and 
  tree.mv_id = t.mv_id and 
  tree.mr_id = t.mr_id and 
  tree.ci_id = t.ci_id and 
  tree.cb_id = t.cb_id and 
  tree.cdi_id = t.cdi_pid and 
  tree.bul_id = t.bul_id
 )

left join (
  select
    but1.md_id,
    but1.mv_id,
    but1.mr_id,
    but1.ci_id,
    but1.cb_id,
    but1.bul_id,
    but1.cdi_pid,
    count(but1.cdi_id) as num
  from
    buildup_tree as but1
  where
   but1.md_id=$FORM{md_id} and
   but1.mv_id=$FORM{mv_id} and
   but1.mr_id=$FORM{mr_id} and
   but1.ci_id=$FORM{ci_id} and
   but1.cb_id=$FORM{cb_id}
  group by
    but1.md_id,
    but1.mv_id,
    but1.mr_id,
    but1.ci_id,
    but1.cb_id,
    but1.bul_id,
    but1.cdi_pid
 ) as t2 on (
  tree.md_id = t2.md_id and 
  tree.mv_id = t2.mv_id and 
  tree.mr_id = t2.mr_id and 
  tree.ci_id = t2.ci_id and 
  tree.cb_id = t2.cb_id and 
  tree.cdi_id = t2.cdi_pid and 
  tree.bul_id = t2.bul_id
 )



left join (
    select
      ci_id,
      cdi_id,
      cdi_name,
      cdi_name_j,
      cdi_name_e,
      cdi_taid,
      cdi_delcause
    from
      concept_data_info
  ) as f on (tree.ci_id = f.ci_id and tree.cdi_id = f.cdi_id)

left join (
    select
      ci_id,
      cdi_id,
      cdi_name,
      cdi_name_j,
      cdi_name_e,
      cdi_taid,
      cdi_delcause
    from
      concept_data_info
  ) as f2 on (tree.ci_id = f2.ci_id and tree.cdi_pid = f2.cdi_id)

left join (
    select
      ci_id,
      cb_id,
      cdi_id,
      cd_name,
      cd_delcause
    from
      concept_data
  ) as cd on (tree.ci_id = cd.ci_id and tree.cb_id = cd.cb_id and tree.cdi_id = cd.cdi_id)

left join (
    select
      bu.ci_id,
      bu.cb_id,
      bu.bul_id,
      but.cdi_pid,
      count(but.cdi_id) as but_cnum 
    from
      (select * from representation where md_id=$FORM{md_id} and mv_id=$FORM{mv_id} and ci_id=$FORM{ci_id} and cb_id=$FORM{cb_id}) as bu,
      buildup_tree as but 
    where
      bu.bul_id=but.bul_id and 
      bu.cdi_id=but.cdi_id
    group by bu.ci_id,bu.cb_id,bu.bul_id,but.cdi_pid
  ) as bu on (
     tree.cdi_id = bu.cdi_pid and
     tree.bul_id = bu.bul_id
  )

left join (
    select
      bu.ci_id,
      bu.cb_id,
      bu.bul_id,
      bu.cdi_id,
      bu.rep_id,
      bu.rep_primitive as primitive,
      bu.rep_density_objs as density_objs,
      bu.rep_density_ends as density_ends
    from
      (select * from representation
       where
         (md_id,mv_id,mr_id,ci_id,cb_id,bul_id,cdi_id) in
         (select
            md_id,mv_id,max(mr_id),ci_id,cb_id,bul_id,cdi_id
          from
            representation
          where
            md_id=$FORM{md_id} and
            mv_id=$FORM{mv_id} and
            mr_id<=$FORM{mr_id} and
            ci_id=$FORM{ci_id} and
            cb_id=$FORM{cb_id} and
            bul_id=$FORM{bul_id} and
            rep_delcause is null
          group by
            md_id,mv_id,ci_id,cb_id,bul_id,cdi_id
         )
      ) as bu
    group by
      bu.ci_id,
      bu.cb_id,
      bu.bul_id,
      bu.cdi_id,
      bu.rep_id,
      bu.rep_primitive,
      bu.rep_density_objs,
      bu.rep_density_ends,
      bu.rep_entry
  ) as rep on (
    tree.cdi_id = rep.cdi_id and
    tree.bul_id = rep.bul_id
  )

where
 tree.md_id=$FORM{md_id} and
 tree.mv_id=$FORM{mv_id} and
 tree.mr_id=$FORM{mr_id} and
 tree.ci_id=$FORM{ci_id} and
 tree.cb_id=$FORM{cb_id} and 
SQL

@LIST1 = ();
unless(exists($FORM{'node'})){
#	my $json = &JSON::XS::encode_json(\@TREE);
#	print $json;
	my $json = &cgi_lib::common::printContentJSON(\@TREE,\%FORM);
	print $LOG __LINE__,":",$json,"\n";
	close($LOG);
	exit;
}elsif($FORM{'node'} eq "trash"){
	$sql .= qq|(tree.but_delcause is not null or f.cdi_delcause is not null) and tree.bul_id=$FORM{'bul_id'}|;
}elsif($FORM{'node'} eq "root"){
	$sql .= qq|tree.cdi_pid is null and tree.bul_id=$FORM{'bul_id'} and tree.but_delcause is null and f.cdi_delcause is null|;
}elsif(exists($FORM{'f_pid'})){
	$sql .= qq|f2.cdi_name=? and tree.bul_id=$FORM{'bul_id'} and tree.but_delcause is null and f.cdi_delcause is null|;
}else{
	$sql .= qq|tree.cdi_pid=? and tree.bul_id=$FORM{'bul_id'} and tree.but_delcause is null and f.cdi_delcause is null|;
}
#$sql .= qq| order by tree.t_order|;
#$sql .= qq| order by tree.t_cnum desc|;
$sql .= qq| order by bu_cnum desc,f.cdi_name_e|;

print $LOG __LINE__,":sql=[$sql]\n";

my $sth = $dbh->prepare($sql) or die $dbh->errstr;

if(exists($FORM{'f_pid'})){
	$sth->execute($FORM{'f_pid'}) or die $dbh->errstr;
}elsif(exists($FORM{'pid'})){
	$sth->execute($FORM{'pid'}) or die $dbh->errstr;
}else{
	$sth->execute() or die $dbh->errstr;
}
#print $LOG __LINE__,":rows=[",$sth->rows(),"]\n";


my($bul_id,$cd_id,$name_j,$name_e,$leaf_num,$cnum,$b_state,$t_broute,$t_isbp3d,$t_logical,$f_taid,$ci_id,$cb_id,$t_cnum,$bu_cnum);
my($rep_id,$rep_primitive,$rep_density_objs,$rep_density_ends);

my $column_number = 0;
$sth->bind_col(++$column_number, \$bul_id,   undef);
$sth->bind_col(++$column_number, \$cd_id,    undef);
$sth->bind_col(++$column_number, \$name_j,   undef);
$sth->bind_col(++$column_number, \$name_e,   undef);
$sth->bind_col(++$column_number, \$leaf_num, undef);
$sth->bind_col(++$column_number, \$cnum,     undef);
$sth->bind_col(++$column_number, \$f_taid,   undef);
$sth->bind_col(++$column_number, \$ci_id,    undef);
$sth->bind_col(++$column_number, \$cb_id,    undef);
$sth->bind_col(++$column_number, \$t_cnum,   undef);
$sth->bind_col(++$column_number, \$bu_cnum,  undef);

$sth->bind_col(++$column_number, \$rep_id,  undef);
$sth->bind_col(++$column_number, \$rep_primitive,  undef);
$sth->bind_col(++$column_number, \$rep_density_objs,  undef);
$sth->bind_col(++$column_number, \$rep_density_ends,  undef);

while($sth->fetch){

	next if($cnum == 0);
	next unless($rep_density_objs);

#print $LOG __LINE__,":\$num=[$num]\n";

	my $text;
	if($FORM{'lng'} eq 'ja'){
		$text = (defined $name_j ? $name_j : $name_e);
	}else{
		$text = $name_e;
	}
#	utf8::decode($text) if(defined $text);
#	my $cnum = $num;

	my $iconCls = "timgfolder";
	$iconCls = ($bu_cnum>0 ? "timgfolder"  : "timgfolder_gray");

	$iconCls = qq|timgfolder_route_parts| unless(defined $rep_id);
	$iconCls = qq|timgfolder_end_parts| if($cnum<=0);

print $LOG __LINE__,":\$cd_id=[$cd_id]\n" if(defined $cd_id);
print $LOG __LINE__,":\$rep_primitive=[$rep_primitive]\n" if(defined $rep_primitive);
print $LOG __LINE__,":\$rep_density_objs=[$rep_density_objs]\n" if(defined $rep_density_objs);
print $LOG __LINE__,":\$rep_density_ends=[$rep_density_ends]\n" if(defined $rep_density_ends);

	if(defined $rep_primitive){
		if($rep_primitive==1){
			$iconCls = qq|timgfolder_primitive|;
		}else{
			my $rep_density = int(($rep_density_objs/$rep_density_ends)*100);
			if($rep_density<=5){
				$iconCls = qq|timgfolder_005|;
			}elsif($rep_density<=15){
				$iconCls = qq|timgfolder_015|;
			}elsif($rep_density<=25){
				$iconCls = qq|timgfolder_025|;
			}elsif($rep_density<=35){
				$iconCls = qq|timgfolder_035|;
			}elsif($rep_density<=45){
				$iconCls = qq|timgfolder_045|;
			}elsif($rep_density<=50){
				$iconCls = qq|timgfolder_050|;
			}elsif($rep_density<=55){
				$iconCls = qq|timgfolder_055|;
			}elsif($rep_density<=65){
				$iconCls = qq|timgfolder_065|;
			}elsif($rep_density<=75){
				$iconCls = qq|timgfolder_075|;
			}elsif($rep_density<=85){
				$iconCls = qq|timgfolder_085|;
			}elsif($rep_density<=95){
				$iconCls = qq|timgfolder_095|;
			}elsif($rep_density<=99){
				$iconCls = qq|timgfolder_099|;
			}else{
				$iconCls = qq|timgfolder_100|;
			}
		}
	}

	my $leaf = ($leaf_num>0 ? JSON::XS::false : JSON::XS::true);
	my $HASH = {
#		text    => qq|$text [ $cnum / $t_cnum ]|,
		text    => $dispTreeChildPartsNum eq 'true' ? qq|$text ($t_cnum)| : qq|$text|,
#		text    => qq|$text|,
		leaf    => $leaf,
		iconCls => $iconCls,
		singleClickExpand => $singleClickExpand,
		f_id    => $cd_id,
		attr => {
			f_id  => $cd_id,
			ci_id => $ci_id,
			cb_id => $cb_id,
			cb_id => $cb_id,
			leaf_num => $leaf_num,
			cnum => $cnum,
		}
	};
	$HASH->{'expanded'} = JSON::XS::true if($FORM{'node'} eq "root");
	push(@TREE,$HASH);
	undef $text;
}
$sth->finish;
undef $sth;




#my $json = &JSON::XS::encode_json(\@TREE);
#print $json;
my $json = &cgi_lib::common::printContentJSON(\@TREE,\%FORM);
open(my $CACHE, qq|> $cache_file|) or die qq|$! [$cache_file]|;
flock($CACHE, 2);
print $CACHE $json;
close($CACHE);

my $tim = alarm 0;
&cgi_lib::common::message($tim, $LOG) if(defined $LOG);

#close($LOG);
exit;

=debug




=cut
