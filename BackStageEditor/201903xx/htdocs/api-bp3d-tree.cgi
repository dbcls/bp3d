#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use Data::Dumper;
use File::Spec::Functions qw(abs2rel rel2abs catdir catfile splitdir);
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'..','cgi_lib');
require "webgl_common.pl";
use cgi_lib::common;

$SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit";
sub sigexit {
	my($date) = `date`;
	$date =~ s/\s*$//g;
	print STDERR "[$date] KILL THIS CGI!![$ENV{SCRIPT_NAME}]\n";
	exit(1);
}

#my $disEnv = &getDispEnv();
#my $dispTreeChildPartsNum = $disEnv->{dispTreeChildPartsNum};
my $dispTreeChildPartsNum = 'false';# unless(defined $dispTreeChildPartsNum);

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);
my($logfile,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

#my @extlist = qw|.cgi .pl|;
#my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);
#my $logfile = qq|$FindBin::Bin/logs/$FORM{'cdi_name'}.$cgi_name.txt|;
$logfile .= '.'.$FORM{'cdi_name'} if(exists $FORM{'cdi_name'} && defined $FORM{'cdi_name'});

=pod
$FORM{ag_data}=qq|obj/bp3d/4.0|;
$FORM{'cdi_name'}=qq|root|;
$FORM{model}=qq|bp3d|;
$FORM{'node'}=qq|root|;
$FORM{tree}=qq|isa|;
$FORM{version}=qq|4.0|;
=cut

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
#$logfile .= '.'.sprintf("%04d%02d%02d%02d",$year+1900,$mon+1,$mday,$hour);
$logfile .=  sprintf(".%02d%02d%02d.%05d",$hour,$min,$sec,$$);

open(my $LOG,"> $logfile");
flock($LOG,2);
print $LOG "\n[$logtime]:$0\n";
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);

$FORM{'node'} = $FORM{'cdi_name'} if(!defined $FORM{'node'} && defined $FORM{'cdi_name'});
#if(!defined $FORM{but_id} && defined $FORM{tree});
#$FORM{tree}=qq|isa|;

$FORM{'use_checkbox'} = 'true' unless(defined $FORM{'use_checkbox'});


my @TREE = ();

unless(
	exists $FORM{'ci_id'} && defined $FORM{'ci_id'} &&
	exists $FORM{'cb_id'} && defined $FORM{'cb_id'} &&
	exists $FORM{'bul_id'} && defined $FORM{'bul_id'} &&
	exists $FORM{'md_id'} && defined $FORM{'md_id'} &&
	exists $FORM{'mv_id'} && defined $FORM{'mv_id'} &&
	exists $FORM{'mr_id'} && defined $FORM{'mr_id'}
){
	&gzip_json(\@TREE);
	close($LOG);
	exit;
}

&setDefParams(\%FORM,\%COOKIE);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);

#my $lsdb_OpenID;
#my $lsdb_Auth;
#my $parentURL = $FORM{'parent'} if(exists($FORM{'parent'}));
#my $parent_text;
#if(defined $parentURL){
#	($lsdb_OpenID,$lsdb_Auth) = &openidAuth($parentURL);
#}



$FORM{'cmd'} = 'read' unless(defined $FORM{'cmd'});

my $sql;

if($FORM{'cmd'} eq 'read'){
	$sql=<<SQL;
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
  tree.but_cnum,
  COALESCE(bu.but_cnum,0)>0 as bu_cnum,
  rep.rep_id,
  rep.md_id,
  rep.mv_id,
  rep.mr_id,
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
  rep.child_objs,
  EXTRACT(EPOCH FROM rep.entry),
  rep.md_abbr,
  rep.mv_name_e,
  rep.mv_publish,
  rep.mv_use,
  rep.mv_frozen,
  tree.cdi_id,
  tree.but_cids,
  EXTRACT(EPOCH FROM cm_modified) as cm_max_entry_cdi,
  cs.seg_id,
  seg_name,
  seg_color,
  seg_thum_bgcolor,
  seg_thum_fgcolor,
  EXTRACT(EPOCH FROM cd_entry) as cd_entry,
  EXTRACT(EPOCH FROM seg_entry) as seg_entry
from (
 select * from view_buildup_tree
 where
  md_id=$FORM{'md_id'} and
  mv_id=$FORM{'mv_id'} and
  mr_id=$FORM{'mr_id'} and
  bul_id=$FORM{'bul_id'}
) as tree

left join (
  select
    but1.md_id,
    but1.mv_id,
    but1.mr_id,
    but1.bul_id,
    but1.cdi_pid,
    count(but2.cdi_id) as num
  from
    buildup_tree as but1
  left join (
      select * from buildup_tree
      where
       md_id=$FORM{'md_id'} and
       mv_id=$FORM{'mv_id'} and
       mr_id=$FORM{'mr_id'} and
       bul_id=$FORM{'bul_id'}
   ) as but2 on (
     but1.md_id=but2.md_id and
     but1.mv_id=but2.mv_id and
     but1.mr_id=but2.mr_id and
     but1.bul_id=but2.bul_id and
     but1.cdi_id=but2.cdi_pid
   )
  where
   but1.md_id=$FORM{'md_id'} and
   but1.mv_id=$FORM{'mv_id'} and
   but1.mr_id=$FORM{'mr_id'} and
   but1.bul_id=$FORM{'bul_id'}
  group by
    but1.md_id,
    but1.mv_id,
    but1.mr_id,
    but1.bul_id,
    but1.cdi_pid
 ) as t on (
  tree.md_id = t.md_id and
  tree.mv_id = t.mv_id and
  tree.mr_id = t.mr_id and
  tree.cdi_id = t.cdi_pid and
  tree.bul_id = t.bul_id
 )

left join (
  select
    but1.md_id,
    but1.mv_id,
    but1.mr_id,
    but1.bul_id,
    but1.cdi_pid,
    count(but1.cdi_id) as num
  from
    buildup_tree as but1
  where
   but1.md_id=$FORM{'md_id'} and
   but1.mv_id=$FORM{'mv_id'} and
   but1.mr_id=$FORM{'mr_id'} and
   but1.bul_id=$FORM{'bul_id'}
  group by
    but1.md_id,
    but1.mv_id,
    but1.mr_id,
    but1.bul_id,
    but1.cdi_pid
 ) as t2 on (
  tree.md_id = t2.md_id and
  tree.mv_id = t2.mv_id and
  tree.mr_id = t2.mr_id and
  tree.cdi_id = t2.cdi_pid and
  tree.bul_id = t2.bul_id
 )



left join (
    select ci_id,cdi_id,cdi_name,cdi_name_j,cdi_name_e,cdi_taid,cdi_delcause from concept_data_info where ci_id=$FORM{'ci_id'}
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
      bu.md_id,
      bu.mv_id,
      bu.mr_id,
      bu.bul_id,
      but.cdi_pid,
      count(but.cdi_id) as but_cnum 
    from
      (select * from representation
       where
         (md_id,mv_id,mr_id,bul_id,cdi_id) in
         (select
            md_id,mv_id,max(mr_id),bul_id,cdi_id
          from
            representation
          where
            md_id=$FORM{'md_id'} and
            mv_id=$FORM{'mv_id'} and 
            bul_id=$FORM{'bul_id'}
          group by
            md_id,mv_id,bul_id,cdi_id
         )
      ) as bu,
      buildup_tree as but 
    where
      bu.md_id=but.md_id and 
      bu.mv_id=but.mv_id and 
      bu.mr_id=but.mr_id and 
      bu.bul_id=but.bul_id and 
      bu.cdi_id=but.cdi_id
    group by
      bu.md_id,
      bu.mv_id,
      bu.mr_id,
      bu.bul_id,
      but.cdi_pid
  ) as bu on (
    tree.md_id = bu.md_id and
    tree.mv_id = bu.mv_id and
    tree.mr_id = bu.mr_id and
    tree.cdi_id = bu.cdi_pid and
    tree.bul_id = bu.bul_id
  )

left join (
    select
      rep.rep_id,
      rep.bul_id,
      rep.md_id,
      rep.mv_id,
      rep.mr_id,
      rep.cdi_id,
      rep.rep_xmin as xmin,
      rep.rep_xmax as xmax,
      rep.rep_ymin as ymin,
      rep.rep_ymax as ymax,
      rep.rep_zmin as zmin,
      rep.rep_zmax as zmax,
      rep.rep_volume as volume,
      rep.rep_primitive as primitive,
      rep.rep_density_objs as density_objs,
      rep.rep_density_ends as density_ends,
      rep.rep_child_objs as child_objs,
      rep.rep_entry as entry,
      md.md_abbr,
      mv.mv_name_e,
      mv.mv_publish,
      mv.mv_use,
      mv.mv_frozen
    from
      (select * from representation
       where
         (md_id,mv_id,mr_id,bul_id,cdi_id) in
         (select
            md_id,mv_id,max(mr_id),bul_id,cdi_id
          from
            representation
          where
            md_id=$FORM{'md_id'} and
            mv_id=$FORM{'mv_id'} and
            bul_id=$FORM{'bul_id'}
          group by
            md_id,mv_id,bul_id,cdi_id
         )
      ) as rep
    left join (
        select * from model
      ) as md on md.md_id=rep.md_id
    left join (
        select * from model_version
      ) as mv on mv.md_id=rep.md_id and mv.mv_id=rep.mv_id
    where
      rep.rep_delcause is null
    group by
      rep.rep_id,
      rep.bul_id,
      rep.md_id,
      rep.mv_id,
      rep.mr_id,
      rep.cdi_id,
      rep.rep_xmin,
      rep.rep_xmax,
      rep.rep_ymin,
      rep.rep_ymax,
      rep.rep_zmin,
      rep.rep_zmax,
      rep.rep_volume,
      rep.rep_primitive,
      rep.rep_density_objs,
      rep.rep_density_ends,
      rep.rep_child_objs,
      rep.rep_entry,
      md.md_abbr,
      mv.mv_name_e,
      mv.mv_publish,
      mv.mv_use,
      mv.mv_frozen
  ) as rep on (
    tree.md_id = rep.md_id and
    tree.mv_id = rep.mv_id and
    tree.mr_id = rep.mr_id and
    tree.cdi_id = rep.cdi_id and
    tree.bul_id = rep.bul_id
  )

left join (
  select
   *
  from
    (select * from concept_art_map_modified
     where
       (md_id,mv_id,mr_id,bul_id,cdi_id) in
       (select
          md_id,mv_id,max(mr_id),bul_id,cdi_id
        from
          concept_art_map_modified
        where
          md_id=$FORM{'md_id'} and
          mv_id=$FORM{'mv_id'} and
          bul_id=$FORM{'bul_id'}
        group by
          md_id,mv_id,bul_id,cdi_id
       )
    ) as cmm
) as cmm on
    cmm.cdi_id=tree.cdi_id

left join (
 select
  *
 from
  concept_data
 where
  ci_id=$FORM{'ci_id'} AND
  cb_id=$FORM{'cb_id'} AND
  cd_delcause is null
) as cd on
   tree.cdi_id=cd.cdi_id

left join (
 select
  seg_id,
  seg_name,
  seg_color,
  seg_thum_bgcolor,
  seg_thum_fgcolor,
  seg_entry
 from
  concept_segment
 where
  seg_delcause is null
) as cs on
   cs.seg_id=cd.seg_id

where
SQL
	&cgi_lib::common::message($sql, $LOG);

	unless(exists($FORM{'node'})){
#		my $json = &JSON::XS::encode_json(\@TREE);
#		print $json;
		&gzip_json(\@TREE);
#		print $LOG __LINE__,":",$json,"\n";
		close($LOG);
		exit;
	}elsif($FORM{'node'} eq 'root'){
		$sql .= qq|tree.cdi_pid is null and tree.but_delcause is null and f.cdi_delcause is null|;
		if($FORM{'bul_id'} == 4){
#			$sql .= qq| and tree.cdi_name='FMA20394'|;
		}
	}elsif(exists($FORM{'cdi_name'})){
		$sql .= qq|tree.cdi_pname=? and tree.but_delcause is null and f.cdi_delcause is null|;
	}
#$sql .= qq| order by tree.t_order|;
#$sql .= qq| order by tree.t_cnum desc|;
	$sql .= qq| order by bu_cnum desc,f.cdi_name_e|;

	print $LOG __LINE__,":sql=[$sql]\n";

	my $sth = $dbh->prepare($sql) or die $dbh->errstr;

	my $sth_rep_delcause = $dbh->prepare(qq|
select
 rep_id,
 EXTRACT(EPOCH FROM max(rep_entry)),
 rep_delcause
from (select * from representation
       where
         (md_id,mv_id,mr_id,bul_id,cdi_id) in
         (select
            md_id,mv_id,max(mr_id),bul_id,cdi_id
          from
            representation
          where
            md_id=$FORM{'md_id'} and
            mv_id=$FORM{'mv_id'} and
            bul_id=$FORM{'bul_id'}
          group by
            md_id,mv_id,bul_id,cdi_id
         )
      ) as rep
where
 cdi_id=? and bul_id=?
group by
 rep_id,rep_delcause
|) or die $dbh->errstr;

	my $expanded = JSON::XS::false;

	if($FORM{'node'} eq 'root'){
		$sth->execute() or die $dbh->errstr;
#		$expanded = JSON::XS::true;
	}elsif(exists($FORM{'cdi_name'})){
		$sth->execute($FORM{'cdi_name'}) or die $dbh->errstr;
	}else{
		$sth->execute() or die $dbh->errstr;
	}
	print $LOG __LINE__,":rows=[",$sth->rows(),"]\n";

	my($bul_id,$cdi_name,$name_j,$name_e,$leaf_num,$cnum,$b_state,$t_broute,$t_isbp3d,$t_logical,$f_taid,$ci_id,$cb_id,$t_cnum,$bu_cnum);
	my($rep_id,$art_xmin,$art_xmax,$art_ymin,$art_ymax,$art_zmin,$art_zmax,$rep_volume,$rep_primitive,$rep_density_objs,$rep_density_ends,$rep_child_objs,$rep_entry,$md_abbr,$mv_name_e,$cdi_id,$but_cids);
	my($md_id,$mv_id,$mr_id);
	my($mv_publish,$mv_use,$mv_frozen);
	my $cm_max_entry_cdi;
	my $seg_id;
	my $seg_name;
	my $seg_color;
	my $seg_thum_bgcolor;
	my $seg_thum_fgcolor;
	my $cd_entry;
	my $seg_entry;

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
	$sth->bind_col(++$column_number, \$md_id,  undef);
	$sth->bind_col(++$column_number, \$mv_id,  undef);
	$sth->bind_col(++$column_number, \$mr_id,  undef);
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
	$sth->bind_col(++$column_number, \$rep_child_objs,  undef);
	$sth->bind_col(++$column_number, \$rep_entry,  undef);
	$sth->bind_col(++$column_number, \$md_abbr,  undef);
	$sth->bind_col(++$column_number, \$mv_name_e,  undef);
	$sth->bind_col(++$column_number, \$mv_publish,  undef);
	$sth->bind_col(++$column_number, \$mv_use,  undef);
	$sth->bind_col(++$column_number, \$mv_frozen,  undef);
	$sth->bind_col(++$column_number, \$cdi_id,  undef);
	$sth->bind_col(++$column_number, \$but_cids,  undef);
	$sth->bind_col(++$column_number, \$cm_max_entry_cdi,  undef);
	$sth->bind_col(++$column_number, \$seg_id,  undef);
	$sth->bind_col(++$column_number, \$seg_name,  undef);
	$sth->bind_col(++$column_number, \$seg_color,  undef);
	$sth->bind_col(++$column_number, \$seg_thum_bgcolor,  undef);
	$sth->bind_col(++$column_number, \$seg_thum_fgcolor,  undef);
	$sth->bind_col(++$column_number, \$cd_entry,  undef);
	$sth->bind_col(++$column_number, \$seg_entry,  undef);

	while($sth->fetch){
#		my $cm_max_num_cdi;
#		my $cm_max_entry_cdi;
		my $isUpdate = 0;
		my $rep_delcause;
		unless($mv_publish){
#			if(defined $cdi_id){
#				undef $cm_max_num_cdi;
#				undef $cm_max_entry_cdi;
#				($cm_max_num_cdi,$cm_max_entry_cdi) = &BITS::ReCalc::get_max_map_info(
#					dbh => $dbh,
#					ci_id => $FORM{'ci_id'},
#					cb_id => $FORM{'cb_id'},
#					md_id => $FORM{'md_id'},
#					mv_id => $FORM{'mv_id'},
#					mr_id => $FORM{'mr_id'},
#					bul_id => $FORM{'bul_id'},
#					cdi_id => $cdi_id,
#					but_cids => $but_cids
#				);
#			}
			if(defined $rep_id){
##				$isUpdate = (((defined $cm_max_num_cdi && $rep_child_objs == $cm_max_num_cdi) || (defined $cm_max_entry_cdi && $cm_max_entry_cdi>$rep_entry)) ? 1 : 0) unless($isUpdate);
				$isUpdate = (((!defined $cm_max_entry_cdi) || (defined $cm_max_entry_cdi && $cm_max_entry_cdi>$rep_entry)) ? 1 : 0) unless($isUpdate);
#print $LOG __LINE__,":[$cdi_name][$isUpdate]\n";
			}
			elsif(defined $cm_max_entry_cdi){
#				$isUpdate = 1;

#				my $rep_id;
#				my $rep_entry;
#				my $rep_delcause;
				$sth_rep_delcause->execute($cdi_id,$bul_id) or die $dbh->errstr;
				$column_number = 0;
				$sth_rep_delcause->bind_col(++$column_number, \$rep_id,   undef);
				$sth_rep_delcause->bind_col(++$column_number, \$rep_entry,   undef);
				$sth_rep_delcause->bind_col(++$column_number, \$rep_delcause,   undef);
				$sth_rep_delcause->fetch;
				$sth_rep_delcause->finish;
				unless(defined $rep_entry && $cm_max_entry_cdi<=$rep_entry){
					$isUpdate = 1;
				}
#print $LOG __LINE__,":[$ci_id][$cb_id][$md_id][$mv_id][$mr_id][$cdi_id][$bul_id]\n";
#print $LOG __LINE__,":[$cdi_name][$isUpdate]\n";
			}
			elsif(defined $cdi_id){
#				$isUpdate = ((defined $cm_max_num_cdi && $cm_max_num_cdi>0) ? 1 : 0);
			}
#print $LOG __LINE__,":[$cdi_name][$cm_max_entry_cdi][$rep_entry][$isUpdate]\n";
		}


#		next if($cnum == 0);

#print $LOG __LINE__,":\$num=[$num]\n";

		my $text;
		if($FORM{'lng'} eq 'ja'){
			$text = (defined $name_j ? $name_j : $name_e);
		}else{
			$text = $name_e;
		}
#		$text .= qq| - $cdi_name|;

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
				my $rep_density = defined $rep_density_objs && $rep_density_objs > 0 ? int(($rep_density_objs/$rep_density_ends)*100) : 0;
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
		$iconCls = qq|timgfolder_route_parts| unless(defined $iconCls);
		$iconCls = ($isUpdate ? 'warning_' : '').$iconCls if(defined $iconCls);

		my $HASH = {
			text    => $text,
			leaf    => $leaf,
			iconCls => $iconCls,
#		f_id    => $cdi_name,
#			checked => ($FORM{'use_checkbox'} eq 'true' && (defined $rep_id || $isUpdate)) ? JSON::XS::false : undef,
#			checked => ($FORM{'use_checkbox'} eq 'true' && (defined $rep_id && !defined $rep_delcause)) ? JSON::XS::false : undef,
			checked => undef,

			cls => (defined $rep_entry && !defined $cm_max_entry_cdi) ? 'delete_node' : ((!defined $rep_entry && defined $cm_max_entry_cdi) ? 'insert_node' : undef),


#		b_id     => $rep_id,
#		b_name_e => $name_e,
#		b_name_j => $name_j,
			expanded => $expanded,
			filesize => 0,
			model    => $md_abbr,
			mtime    => defined $rep_entry ? $rep_entry+0 : undef,
#		name     => $name_e,
			path     => undef,
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
			bul_id   => $bul_id,

			md_id      => $md_id,
			mv_id      => $mv_id,
			mr_id      => $mr_id,

			rep_id     => $rep_id,
			cdi_name   => $cdi_name,
			cdi_name_e => $name_e,
			cdi_name_j => $name_j,

			leaf_num => defined $leaf_num ? $leaf_num+0 : undef,
			cnum     => defined $cnum ? $cnum+0 : undef,

#			cm_max_num_cdi => defined $cm_max_num_cdi ? $cm_max_num_cdi+0 : undef,
			cm_max_entry_cdi => defined $cm_max_entry_cdi ? $cm_max_entry_cdi+0 : undef,


			rep_child_objs => defined $rep_child_objs ? $rep_child_objs+0 : undef,
			cdi_id => defined $cdi_id ? $cdi_id+0 : undef,


			rep_entry => defined $rep_entry ? $rep_entry+0 : undef,

			seg_id => $seg_id,
			seg_name => $seg_name,
			seg_color => $seg_color,
			seg_thum_bgcolor => $seg_thum_bgcolor,
			seg_thum_fgcolor => $seg_thum_fgcolor,

			cd_entry => defined $cd_entry ? $cd_entry+0 : undef,
			seg_entry => defined $seg_entry ? $seg_entry+0 : undef,
		};

		if(exists $FORM{'path'} && defined $FORM{'path'} && length $FORM{'path'}){
			my @PATH = split('/',$FORM{'path'});
			push(@PATH, $cdi_name);
			$HASH->{'path'} = join('/', @PATH);
		}


#	$HASH->{'expanded'} = JSON::XS::true if($FORM{'node'} eq 'root');

=pod
		if(defined $rep_id){
			my $sql_art =<<SQL;
select distinct
 art_id,
 artg_id
from
 history_art_file
where
 (art_id,hist_serial) in (
   select art_id,art_hist_serial from representation_art where rep_id=?
 )
SQL
			my $sth_art = $dbh->prepare($sql_art) or die $dbh->errstr;
			$sth_art->execute($rep_id) or die $dbh->errstr;
			my $art_id;
			my $artg_id;
			my $column_number = 0;
			$sth_art->bind_col(++$column_number, \$art_id,   undef);
			$sth_art->bind_col(++$column_number, \$artg_id,   undef);
			while($sth_art->fetch){
				next unless(defined $art_id && defined $artg_id);
				push(@{$HASH->{'artg_ids'}->{$artg_id}},$art_id);
				$HASH->{'art_ids'}->{$art_id} = $artg_id;
			}
			$sth_art->finish;
			undef $sth_art;
		}
=cut

		push(@TREE,$HASH);
		undef $text;
	}
	$sth->finish;
	undef $sth;
}

#my $json = to_json(\@TREE);
#my $json = &JSON::XS::encode_json(\@TREE);
#print $json;
&gzip_json(\@TREE);
#print $LOG __LINE__,":",$json,"\n";

&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\@TREE, 1), $LOG) if(defined $LOG);
close($LOG) if(defined $LOG);
