#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use JSON::XS;
use Data::Dumper;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
require "webgl_common.pl";

#my $disEnv = &getDispEnv();
#my $dispTreeChildPartsNum = $disEnv->{dispTreeChildPartsNum};
my $dispTreeChildPartsNum = 'false';# unless(defined $dispTreeChildPartsNum);

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);
#my($logfile,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

my @extlist = qw|.cgi .pl|;
my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);
my $logfile = qq|$FindBin::Bin/logs/$FORM{'f_id'}.$cgi_name.txt|;

=pod
$FORM{ag_data}=qq|obj/bp3d/4.0|;
$FORM{f_id}=qq|root|;
$FORM{model}=qq|bp3d|;
$FORM{node}=qq|root|;
$FORM{tree}=qq|isa|;
$FORM{version}=qq|4.0|;
=cut

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);

open(LOG,"> $logfile");
flock(LOG,2);
print LOG "\n[$logtime]:$0\n";
foreach my $key (sort keys(%FORM)){
	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
}
#foreach my $key (sort keys(%COOKIE)){
#	print LOG "\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
#}
#foreach my $key (sort keys(%ENV)){
#	print LOG __LINE__,":\$ENV{$key}=[",$ENV{$key},"]\n";
#}

$FORM{node} = $FORM{f_id} if(!defined $FORM{node} && defined $FORM{f_id});
#if(!defined $FORM{but_id} && defined $FORM{tree});
#$FORM{tree}=qq|isa|;

&setDefParams(\%FORM,\%COOKIE);
foreach my $key (sort keys(%FORM)){
	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
}

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
foreach my $key (sort keys(%FORM)){
	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
}

my @TREE = ();

unless(defined $FORM{'version'}){
	print qq|Content-type: text/html; charset=UTF-8\n\n|;
	exit;
}

my $lsdb_OpenID;
my $lsdb_Auth;
my $parentURL = $FORM{'parent'} if(exists($FORM{'parent'}));
my $parent_text;
if(defined $parentURL){
	($lsdb_OpenID,$lsdb_Auth) = &openidAuth($parentURL);
}

$SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit";
sub sigexit {
	my($date) = `date`;
	$date =~ s/\s*$//g;
	print STDERR "[$date] KILL THIS CGI!![$ENV{SCRIPT_NAME}]\n";
	exit(1);
}

my $singleClickExpand = JSON::XS::false;
my @LIST1 = ();

#$FORM{'node'} = 'root';

###
###

#    select ci_id,cb_id,bul_id,cdi_pid,count(cdi_id) as num from buildup_tree group by ci_id,cb_id,bul_id,cdi_pid

my $sql;
$sql=<<SQL;
select
  tree.bul_id,
  f.cdi_name,
  f.cdi_name_j,
  f.cdi_name_e,
  COALESCE(t.num,0),
  COALESCE(t2.num,0),
  f.cdi_taid,
  tree.ci_id,
  tree.cb_id,
  tree.but_cnum,
  COALESCE(bu.but_cnum,0)>0 as bu_cnum,
  rep.rep_id,
  rep.xmin,
  rep.xmax,
  rep.ymin,
  rep.ymax,
  rep.zmin,
  rep.zmax,
  rep.volume,
  rep.primitive,
  rep.density_objs,
  rep.density_ends,
  EXTRACT(EPOCH FROM rep.entry),
  rep.md_abbr,
  rep.mv_name_e
from
  view_buildup_tree as tree

left join (
  select
    but1.ci_id,
    but1.cb_id,
    but1.bul_id,
    but1.cdi_pid,
    count(but2.cdi_id) as num
  from
    buildup_tree as but1
  left join (
      select * from buildup_tree where ci_id=$FORM{ci_id} and cb_id=$FORM{cb_id} and bul_id=$FORM{bul_id}
   ) as but2 on (
     but1.ci_id=but2.ci_id and
     but1.cb_id=but2.cb_id and
     but1.bul_id=but2.bul_id and
     but1.cdi_id=but2.cdi_pid
   )
  where
   but1.ci_id=$FORM{ci_id} and but1.cb_id=$FORM{cb_id} and but1.bul_id=$FORM{bul_id}
  group by
    but1.ci_id,
    but1.cb_id,
    but1.bul_id,
    but1.cdi_pid
 ) as t on (
  tree.ci_id = t.ci_id and 
  tree.cb_id = t.cb_id and 
  tree.cdi_id = t.cdi_pid and 
  tree.bul_id = t.bul_id
 )

left join (
  select
    but1.ci_id,
    but1.cb_id,
    but1.bul_id,
    but1.cdi_pid,
    count(but1.cdi_id) as num
  from
    buildup_tree as but1
  where
   but1.ci_id=$FORM{ci_id} and but1.cb_id=$FORM{cb_id} and but1.bul_id=$FORM{bul_id}
  group by
    but1.ci_id,
    but1.cb_id,
    but1.bul_id,
    but1.cdi_pid
 ) as t2 on (
  tree.ci_id = t2.ci_id and 
  tree.cb_id = t2.cb_id and 
  tree.cdi_id = t2.cdi_pid and 
  tree.bul_id = t2.bul_id
 )



left join (
    select ci_id,cdi_id,cdi_name,cdi_name_j,cdi_name_e,cdi_taid,cdi_delcause from concept_data_info
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
      bu.ci_id,
      bu.cb_id,
      bu.bul_id,
      but.cdi_pid,
      count(but.cdi_id) as but_cnum 
    from
      (select * from representation where md_id=$FORM{md_id} and mv_id=$FORM{mv_id} and ci_id=$FORM{ci_id} and cb_id=$FORM{cb_id} and bul_id=$FORM{bul_id}) as bu,
      buildup_tree as but 
    where
      bu.ci_id=but.ci_id and 
      bu.cb_id=but.cb_id and 
      bu.bul_id=but.bul_id and 
      bu.cdi_id=but.cdi_id
    group by bu.ci_id,bu.cb_id,bu.bul_id,but.cdi_pid
  ) as bu on (tree.ci_id = bu.ci_id and tree.cb_id = bu.cb_id and tree.cdi_id = bu.cdi_pid and tree.bul_id = bu.bul_id)

left join (
    select
      bu.rep_id,
      bu.ci_id,
      bu.cb_id,
      bu.bul_id,
      bu.cdi_id,
      bu.rep_xmin as xmin,
      bu.rep_xmax as xmax,
      bu.rep_ymin as ymin,
      bu.rep_ymax as ymax,
      bu.rep_zmin as zmin,
      bu.rep_zmax as zmax,
      bu.rep_volume as volume,
      bu.rep_primitive as primitive,
      bu.rep_density_objs as density_objs,
      bu.rep_density_ends as density_ends,
      bu.rep_entry as entry,
      md.md_abbr,
      mv.mv_name_e
    from
      (select * from representation
       where
         (md_id,mv_id,mr_id,ci_id,cb_id,bul_id,cdi_id) in
         (select
            md_id,mv_id,max(mr_id),ci_id,cb_id,bul_id,cdi_id
          from
            representation
          where
            md_id=$FORM{md_id} and mv_id=$FORM{mv_id} and ci_id=$FORM{ci_id} and cb_id=$FORM{cb_id} and bul_id=$FORM{bul_id}
          group by
            md_id,mv_id,ci_id,cb_id,bul_id,cdi_id
         )
      ) as bu
    left join (
        select * from model
      ) as md on md.md_id=bu.md_id
    left join (
        select * from model_version
      ) as mv on mv.md_id=bu.md_id and mv.mv_id=bu.mv_id
    group by
      bu.rep_id,bu.ci_id,bu.cb_id,bu.bul_id,bu.cdi_id,
      bu.rep_xmin,
      bu.rep_xmax,
      bu.rep_ymin,
      bu.rep_ymax,
      bu.rep_zmin,
      bu.rep_zmax,
      bu.rep_volume,
      bu.rep_primitive,
      bu.rep_density_objs,
      bu.rep_density_ends,
      bu.rep_entry,
      md.md_abbr,
      mv.mv_name_e
  ) as rep on (
    tree.ci_id = rep.ci_id and
    tree.cb_id = rep.cb_id and
    tree.cdi_id = rep.cdi_id and
    tree.bul_id = rep.bul_id
  )

--left join (
--    select
--      repa.rep_id,
--      min(art_xmin) as xmin,
--      max(art_xmax) as xmax,
--      min(art_ymin) as ymin,
--      max(art_ymax) as ymax,
--      min(art_zmin) as zmin,
--      max(art_zmax) as zmax
--    from
--      representation_art as repa
--    left join (
--        select
--          art_id,
--          art_serial,
--          art_xmin,
--          art_xmax,
--          art_ymin,
--          art_ymax,
--          art_zmin,
--          art_zmax
--        from
--          history_art_file
--      ) as art on (art.art_id=repa.art_id and art.art_serial=repa.art_hist_serial)
--    group by
--      rep_id
--  ) as repa on (repa.rep_id = rep.rep_id)

where
 tree.ci_id=$FORM{ci_id} and tree.cb_id=$FORM{cb_id} and tree.bul_id=$FORM{'bul_id'} and
SQL

my @LIST1 = ();
unless(exists($FORM{'node'})){
#	my $json = &JSON::XS::encode_json(\@TREE);
#	print $json;
	&gzip_json(\@TREE);
#	print LOG __LINE__,":",$json,"\n";
	close(LOG);
	exit;
}elsif($FORM{'node'} eq "root"){
	$sql .= qq|tree.cdi_pid is null and tree.but_delcause is null and f.cdi_delcause is null|;
}elsif(exists($FORM{'f_id'})){
	$sql .= qq|tree.cdi_pname=? and tree.but_delcause is null and f.cdi_delcause is null|;
}
#$sql .= qq| order by tree.t_order|;
#$sql .= qq| order by tree.t_cnum desc|;
$sql .= qq| order by bu_cnum desc,f.cdi_name_e|;

print LOG __LINE__,":sql=[$sql]\n";

my $sth = $dbh->prepare($sql) or die $dbh->errstr;

my $expanded = JSON::XS::false;

if($FORM{'node'} eq "root"){
	$sth->execute() or die $dbh->errstr;
	$expanded = JSON::XS::true;
}elsif(exists($FORM{'f_id'})){
	$sth->execute($FORM{'f_id'}) or die $dbh->errstr;
}else{
	$sth->execute() or die $dbh->errstr;
}
print LOG __LINE__,":rows=[",$sth->rows(),"]\n";


my($bul_id,$cdi_name,$name_j,$name_e,$leaf_num,$cnum,$b_state,$t_broute,$t_isbp3d,$t_logical,$f_taid,$ci_id,$cb_id,$t_cnum,$bu_cnum);
my($rep_id,$art_xmin,$art_xmax,$art_ymin,$art_ymax,$art_zmin,$art_zmax,$rep_volume,$rep_primitive,$rep_density_objs,$rep_density_ends,$rep_entry,$md_abbr,$mv_name_e);

my $column_number = 0;
$sth->bind_col(++$column_number, \$bul_id,   undef);
$sth->bind_col(++$column_number, \$cdi_name,    undef);
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
$sth->bind_col(++$column_number, \$art_xmin,  undef);
$sth->bind_col(++$column_number, \$art_xmax,  undef);
$sth->bind_col(++$column_number, \$art_ymin,  undef);
$sth->bind_col(++$column_number, \$art_ymax,  undef);
$sth->bind_col(++$column_number, \$art_zmin,  undef);
$sth->bind_col(++$column_number, \$art_zmax,  undef);
$sth->bind_col(++$column_number, \$rep_volume,  undef);
$sth->bind_col(++$column_number, \$rep_primitive,  undef);
$sth->bind_col(++$column_number, \$rep_density_objs,  undef);
$sth->bind_col(++$column_number, \$rep_density_ends,  undef);
$sth->bind_col(++$column_number, \$rep_entry,  undef);
$sth->bind_col(++$column_number, \$md_abbr,  undef);
$sth->bind_col(++$column_number, \$mv_name_e,  undef);

while($sth->fetch){

#		next if($cnum == 0);

#print LOG __LINE__,":\$num=[$num]\n";

	my $text;
	if($FORM{'lng'} eq 'ja'){
		$text = (defined $name_j ? $name_j : $name_e);
	}else{
		$text = $name_e;
	}
#	utf8::decode($text) if(defined $text);
#	my $cnum = $num;

	my $iconCls = undef;

#	$iconCls = qq|timgfolder_gray| if($bu_cnum<=0);
#	$iconCls = qq|timgfolder_gray| unless(defined $rep_id);
	$iconCls = qq|timgfolder_route_parts| unless(defined $rep_id);

#	my $leaf = ($leaf_num>0 ? JSON::XS::false : JSON::XS::true);
	my $leaf = ($t_cnum>0 ? JSON::XS::false : JSON::XS::true);
	$iconCls = qq|timgfolder_end_parts| if($cnum<=0);

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

	my $HASH = {
		text    => $text,
		leaf    => $leaf,
		iconCls => $iconCls,
#		f_id    => $cdi_name,
		checked => defined $rep_id ? JSON::XS::false : undef,

#		b_id     => $rep_id,
#		b_name_e => $name_e,
#		b_name_j => $name_j,
		expanded => $expanded,
		filesize => 0,
		model    => $md_abbr,
		mtime    => defined $rep_entry ? $rep_entry+0 : undef,
#		name     => $name_e,
#		path     => undef,
		version  => $mv_name_e,
		volume   => defined $rep_volume ? $rep_volume+0 : undef,
		xmax     => defined $art_xmin ? $art_xmin+0 : undef,
		xmin     => defined $art_xmax ? $art_xmax+0 : undef,
		ymax     => defined $art_ymin ? $art_ymin+0 : undef,
		ymin     => defined $art_ymax ? $art_ymax+0 : undef,
		zmax     => defined $art_zmin ? $art_zmin+0 : undef,
		zmin     => defined $art_zmax ? $art_zmax+0 : undef,

		ci_id    => $ci_id,
		cb_id    => $cb_id,

		rep_id     => $rep_id,
		cdi_name   => $cdi_name,
		cdi_name_e => $name_e,
		cdi_name_j => $name_j,

		leaf_num => defined $leaf_num ? $leaf_num+0 : undef,
		cnum     => defined $cnum ? $cnum+0 : undef,

	};
#	$HASH->{'expanded'} = JSON::XS::true if($FORM{'node'} eq "root");
	push(@TREE,$HASH);
	undef $text;
}
$sth->finish;
undef $sth;



#my $json = to_json(\@TREE);
#my $json = &JSON::XS::encode_json(\@TREE);
#print $json;
&gzip_json(\@TREE);
#print LOG __LINE__,":",$json,"\n";

print LOG __LINE__,":",Dumper(\@TREE),"\n";

close(LOG);
exit;

=debug




=cut
