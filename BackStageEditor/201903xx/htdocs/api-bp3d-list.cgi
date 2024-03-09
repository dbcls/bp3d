#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
use BITS::ReCalc;
require "webgl_common.pl";
use cgi_lib::common;

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
if(exists $ENV{'REQUEST_METHOD'}){
	my $query = CGI->new;
	&getParams($query,\%FORM,\%COOKIE);
}
my($logfile,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

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
#$logfile .= '.'.sprintf("%04d%02d%02d%02d",$year+1900,$mon+1,$mday,$hour);
$logfile .=  sprintf(".%02d%02d%02d.%05d",$hour,$min,$sec,$$);

my $LOG;
if(exists $ENV{'REQUEST_METHOD'}){
	open($LOG,">> $logfile");
	flock($LOG,2);
}else{
	$LOG = \*STDERR;

	$FORM{'md_id'} = 1;
	$FORM{'mv_id'} = 26;
	$FORM{'mr_id'} = 1;
	$FORM{'ci_id'} = 1;
	$FORM{'cb_id'} = 12;
	$FORM{'bul_id'} = 3;
	$FORM{'selected'} = qq|[]|;
	$FORM{'page'} = 1;
	$FORM{'start'} = 0;
	$FORM{'limit'} = 50;
	$FORM{'sort'} = qq|[{"property":"cdi_name_e","direction":"ASC"}]|;
}
print $LOG "\n[$logtime]:$0\n";
&cgi_lib::common::message(\%FORM, $LOG);

&setDefParams(\%FORM,\%COOKIE);
&cgi_lib::common::message(\%FORM, $LOG);

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
&cgi_lib::common::message(\%FORM, $LOG);

$FORM{'cmd'} = 'read' unless(defined $FORM{'cmd'});

#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $DATAS = {
	datas => [],
	total => 0,
	success => JSON::XS::false
};
eval{
	if($FORM{'cmd'} eq 'read'){

		my @SORT;
		if(exists $FORM{'sort'} && defined $FORM{'sort'}){
			my $sort = &cgi_lib::common::decodeJSON($FORM{'sort'});
			push(@SORT,map {
				$_->{'direction'} = 'ASC' unless(exists $_->{'direction'} && defined $_->{'direction'});
				$_;
			} grep {exists $_->{'property'} && defined $_->{'property'}} @$sort) if(defined $sort && ref $sort eq 'ARRAY');
		}
		if(scalar @SORT == 0){
			push(@SORT,{
				property  => 'cdi_name_e',
				direction => 'ASC'
			});
		}

		my %SELECTED;
		if(exists $FORM{'selected'} && defined $FORM{'selected'}){
			my $selected = &cgi_lib::common::decodeJSON($FORM{'selected'});
			%SELECTED = map{
				if(exists $_->{'f_id'} && defined $_->{'f_id'}){
					$_->{'f_id'} => $_;
				}else{
					$_->{'cdi_name'} => $_;
				}
			} grep {(exists $_->{'f_id'} && defined $_->{'f_id'}) || (exists $_->{'cdi_name'} && defined $_->{'cdi_name'})} @$selected if(defined $selected && ref $selected eq 'ARRAY');
		}



		my $sql=<<SQL;
select distinct * from (
select
 rep.ci_id,
 rep.cb_id,
 rep.md_id,
 rep.mv_id,
 rep.mr_id,
 rep.bul_id,
 rep.rep_id,
 rep_xmin,
 rep_xmax,
 to_number(to_char((rep_xmax+rep_xmin)/2,'FM99990D0000'),'99990D0000S') as rep_xcenter,
 rep_ymin,
 rep_ymax,
 to_number(to_char((rep_ymax+rep_ymin)/2,'FM99990D0000'),'99990D0000S') as rep_ycenter,
 rep_zmin,
 rep_zmax,
 to_number(to_char((rep_zmax+rep_zmin)/2,'FM99990D0000'),'99990D0000S') as rep_zcenter,
 rep_volume,
 EXTRACT(EPOCH FROM rep_entry) as rep_entry,
 cdi_name,
 cdi_name_j,
 COALESCE(cd.cd_name,cdi_name_e) as cdi_name_e,
 cdi_name_k,
 cdi_name_l,
 md.md_abbr,
 mv.mv_name_e,
 mr.mr_version,
 bul.bul_abbr,
 rep_primitive,
-- to_number(to_char((rep_density_objs/rep_density_ends)*100,'FM99990D0000'),'99990D0000S') as rep_density,
 CASE WHEN rep_density_ends<>0 THEN to_number(to_char((rep_density_objs/rep_density_ends)*100,'FM99990D0000'),'99990D0000S')
      ELSE 0
 END as rep_density,


 rep_child_objs,
 mv.mv_publish,
 mv.mv_use,
 mv.mv_frozen,
 rep.cdi_id,
 CASE but.but_cids WHEN NULL THEN NULL
                   ELSE 1
 END as but_cids,
 EXTRACT(EPOCH FROM cm_modified) as cm_max_entry_cdi,
 cs.seg_id,
 seg_name,
 seg_color,
 seg_thum_bgcolor,
 seg_thum_fgcolor,
 EXTRACT(EPOCH FROM cd_entry) as cd_entry,
 EXTRACT(EPOCH FROM seg_entry) as seg_entry,

 COALESCE(EXTRACT(EPOCH FROM rep_entry),0) - COALESCE(EXTRACT(EPOCH FROM cm_modified),0) as time_diff,

 rep_serial
from (
  select
   *
  from
   buildup_tree_info
  where
   md_id=$FORM{md_id} AND
   mv_id=$FORM{mv_id} AND
   mr_id=$FORM{mr_id} AND
   bul_id=$FORM{bul_id} AND
   but_delcause IS NULL
 ) as but

left join (
  select
   *
  from
   concept_art_map_modified
  where 
   md_id=$FORM{md_id} AND
   mv_id=$FORM{mv_id} AND
   mr_id=$FORM{mr_id} AND
   bul_id=$FORM{bul_id}
 ) as cmm on cmm.cdi_id=but.cdi_id

left join (
  select * from representation where (cdi_id,md_id,mv_id,mr_id,bul_id) in (
   select
    cdi_id,md_id,mv_id,max(mr_id) as mr_id,bul_id
   from
    representation
   where
    md_id=$FORM{md_id} AND
    mv_id=$FORM{mv_id} AND
    mr_id<=$FORM{mr_id} AND
    bul_id=$FORM{bul_id}
   group by
    cdi_id,md_id,mv_id,bul_id
 )
 AND rep_delcause IS NULL

 ) as rep on rep.cdi_id=but.cdi_id


left join (
  select * from concept_data_info where ci_id=$FORM{ci_id}
 ) as cdi on cdi.cdi_id=but.cdi_id

left join (
  select * from model
 ) as md on md.md_id=cmm.md_id

left join (
  select * from model_version
 ) as mv on
   mv.md_id=cmm.md_id and
   mv.mv_id=cmm.mv_id

left join (
  select * from model_revision
 ) as mr on
   mr.md_id=cmm.md_id and
   mr.mv_id=cmm.mv_id and
   mr.mr_id=cmm.mr_id

left join (
  select * from buildup_logic
 ) as bul on bul.bul_id=cmm.bul_id

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
   but.cdi_id=cd.cdi_id

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

) as a
where
 rep_entry is not null or
 cm_max_entry_cdi is not null

SQL

		if(scalar @SORT > 0){
			my @orderby;
			foreach (@SORT){
				if($_->{property} eq 'rep_entry' || $_->{property} eq 'cm_max_entry_cdi'){
					push(@orderby,qq|$_->{property} $_->{direction} NULLS LAST|);
				}else{
					push(@orderby,qq|rep_primitive $_->{direction}|) if($_->{property} eq 'rep_density' && $_->{direction} eq 'DESC');
					push(@orderby,qq|$_->{property} $_->{direction}|);
					push(@orderby,qq|rep_primitive $_->{direction}|) if($_->{property} eq 'rep_density' && $_->{direction} eq 'ASC');
					push(@orderby,qq|rep_serial ASC|) if($_->{property} eq 'rep_density');
				}
			}
			$sql .= qq| order by | . join(",",@orderby) if(scalar @orderby > 0);
		}

		&cgi_lib::common::message("\$sql=[$sql]", $LOG) if(defined $LOG);

		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$DATAS->{'total'} = $sth->rows();
		$sth->finish;
		undef $sth;

		&cgi_lib::common::message($DATAS->{'total'}, $LOG) if(defined $LOG);

		$sql .= qq| limit $FORM{limit}| if(defined $FORM{limit});
		$sql .= qq| offset $FORM{start}| if(defined $FORM{start});
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;

		my $ci_id;
		my $cb_id;
		my $md_id;
		my $mv_id;
		my $mr_id;
		my $bul_id;

		my $rep_id;
		my $rep_xmin;
		my $rep_xmax;
		my $rep_xcenter;
		my $rep_ymin;
		my $rep_ymax;
		my $rep_ycenter;
		my $rep_zmin;
		my $rep_zmax;
		my $rep_zcenter;
		my $rep_volume;
		my $rep_entry;
		my $cdi_name;
		my $cdi_name_j;
		my $cdi_name_e;
		my $cdi_name_k;
		my $cdi_name_l;
		my $md_abbr;
		my $mv_name_e;
		my $mr_version;
		my $bul_abbr;

		my $rep_primitive;
		my $rep_density;

		my $rep_child_objs;
		my $mv_publish;
		my $mv_use;
		my $mv_frozen;
		my $cdi_id;
		my $but_cids;
		my $cm_max_entry_cdi;

		my $seg_id;
		my $seg_name;
		my $seg_color;
		my $seg_thum_bgcolor;
		my $seg_thum_fgcolor;

		my $cd_entry;
		my $seg_entry;

		my $time_diff;

		my $column_number = 0;
		$sth->bind_col(++$column_number, \$ci_id,   undef);
		$sth->bind_col(++$column_number, \$cb_id,   undef);
		$sth->bind_col(++$column_number, \$md_id,   undef);
		$sth->bind_col(++$column_number, \$mv_id,   undef);
		$sth->bind_col(++$column_number, \$mr_id,   undef);
		$sth->bind_col(++$column_number, \$bul_id,   undef);

		$sth->bind_col(++$column_number, \$rep_id,   undef);
		$sth->bind_col(++$column_number, \$rep_xmin,   undef);
		$sth->bind_col(++$column_number, \$rep_xmax,   undef);
		$sth->bind_col(++$column_number, \$rep_xcenter,   undef);

		$sth->bind_col(++$column_number, \$rep_ymin,   undef);
		$sth->bind_col(++$column_number, \$rep_ymax,   undef);
		$sth->bind_col(++$column_number, \$rep_ycenter,   undef);

		$sth->bind_col(++$column_number, \$rep_zmin,      undef);
		$sth->bind_col(++$column_number, \$rep_zmax,      undef);
		$sth->bind_col(++$column_number, \$rep_zcenter,   undef);

		$sth->bind_col(++$column_number, \$rep_volume,    undef);
		$sth->bind_col(++$column_number, \$rep_entry,     undef);
		$sth->bind_col(++$column_number, \$cdi_name,      undef);
		$sth->bind_col(++$column_number, \$cdi_name_j,    undef);
		$sth->bind_col(++$column_number, \$cdi_name_e,    undef);
		$sth->bind_col(++$column_number, \$cdi_name_k,    undef);
		$sth->bind_col(++$column_number, \$cdi_name_l,    undef);
		$sth->bind_col(++$column_number, \$md_abbr,       undef);
		$sth->bind_col(++$column_number, \$mv_name_e,     undef);
		$sth->bind_col(++$column_number, \$mr_version,     undef);
		$sth->bind_col(++$column_number, \$bul_abbr,      undef);

		$sth->bind_col(++$column_number, \$rep_primitive, undef);
		$sth->bind_col(++$column_number, \$rep_density,   undef);

		$sth->bind_col(++$column_number, \$rep_child_objs,   undef);
		$sth->bind_col(++$column_number, \$mv_publish,   undef);
		$sth->bind_col(++$column_number, \$mv_use,   undef);
		$sth->bind_col(++$column_number, \$mv_frozen,   undef);

		$sth->bind_col(++$column_number, \$cdi_id,   undef);
		$sth->bind_col(++$column_number, \$but_cids,   undef);

		$sth->bind_col(++$column_number, \$cm_max_entry_cdi,   undef);

		$sth->bind_col(++$column_number, \$seg_id,   undef);
		$sth->bind_col(++$column_number, \$seg_name,   undef);
		$sth->bind_col(++$column_number, \$seg_color,   undef);
		$sth->bind_col(++$column_number, \$seg_thum_bgcolor,   undef);
		$sth->bind_col(++$column_number, \$seg_thum_fgcolor,   undef);

		$sth->bind_col(++$column_number, \$cd_entry,   undef);
		$sth->bind_col(++$column_number, \$seg_entry,   undef);

		$sth->bind_col(++$column_number, \$time_diff,   undef);

		while($sth->fetch){
			my $isUpdate = 0;
			unless($mv_publish){
				if(defined $rep_id){
					$isUpdate = (((!defined $cm_max_entry_cdi) || (defined $cm_max_entry_cdi && $cm_max_entry_cdi>$rep_entry)) ? 1 : 0) unless($isUpdate);
				}
				elsif(defined $cm_max_entry_cdi){
					$isUpdate = 1;
				}
				elsif(defined $cdi_id){
	#				$isUpdate = ((defined $cm_max_num_cdi && $cm_max_num_cdi>0) ? 1 : 0);
				}
			}

			my $iconCls;
			$iconCls = qq|timgfolder_end_parts| unless(defined $but_cids);
			if(defined $rep_primitive){
				if($rep_primitive==1){
					$iconCls = qq|timgfolder_primitive|;
				}else{
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

			my $rep_thumb = &getImagePath($cdi_name,'rotate',$mr_version,'16x16',$bul_id);
			&cgi_lib::common::message($rep_thumb,$LOG);
			$rep_thumb = undef unless(-e $rep_thumb && -f $rep_thumb && -s $rep_thumb);

			my $HASH = {
				ci_id      => defined $ci_id  ? $ci_id - 0  : undef,
				cb_id      => defined $cb_id  ? $cb_id - 0  : undef,
				md_id      => defined $md_id  ? $md_id - 0  : undef,
				mv_id      => defined $mv_id  ? $mv_id - 0  : undef,
				mr_id      => defined $mr_id  ? $mr_id - 0  : undef,
				bul_id     => defined $bul_id ? $bul_id - 0 : undef,

				rep_id      => $rep_id,
				rep_xmin    => defined $rep_xmin    ? $rep_xmin - 0    : undef,
				rep_xmax    => defined $rep_xmax    ? $rep_xmax - 0    : undef,
				rep_xcenter => defined $rep_xcenter ? $rep_xcenter - 0 : undef,
				rep_ymin    => defined $rep_ymin    ? $rep_ymin - 0    : undef,
				rep_ymax    => defined $rep_ymax    ? $rep_ymax - 0    : undef,
				rep_ycenter => defined $rep_ycenter ? $rep_ycenter - 0 : undef,
				rep_zmin    => defined $rep_zmin    ? $rep_zmin - 0    : undef,
				rep_zmax    => defined $rep_zmax    ? $rep_zmax - 0    : undef,
				rep_zcenter => defined $rep_zcenter ? $rep_zcenter - 0 : undef,
				rep_volume  => defined $rep_volume  ? $rep_volume - 0  : undef,
				rep_entry   => defined $rep_entry   ? $rep_entry - 0   : undef,
				cdi_name    => $cdi_name,
				cdi_name_j  => $cdi_name_j,
				cdi_name_e  => $cdi_name_e,
				cdi_name_k  => $cdi_name_k,
				cdi_name_l  => $cdi_name_l,
				md_abbr     => $md_abbr,
				mv_name_e   => $mv_name_e,
				bul_abbr    => $bul_abbr,

	#			cm_max_num_cdi => defined $cm_max_num_cdi ? $cm_max_num_cdi+0 : undef,
				cm_max_entry_cdi => defined $cm_max_entry_cdi ? $cm_max_entry_cdi+0 : undef,

				rep_primitive       => $rep_primitive ? JSON::XS::true : JSON::XS::false,
				rep_density         => defined $rep_density ? $rep_density - 0 : undef,
				rep_density_iconCls => $iconCls,

				seg_id => defined $seg_id ? $seg_id - 0 : undef,
				seg_name => $seg_name,
				seg_color => $seg_color,
				seg_thum_bgcolor => $seg_thum_bgcolor,
				seg_thum_fgcolor => $seg_thum_fgcolor,

				cd_entry => defined $cd_entry ? $cd_entry+0 : undef,
				seg_entry => defined $seg_entry ? $seg_entry+0 : undef,

				time_diff => $time_diff - 0,
				rep_thumb => $rep_thumb
			};

			if(defined $SELECTED{$cdi_name}){
				foreach my $key (qw(color opacity remove selected)){
					next unless(defined $SELECTED{$cdi_name}->{$key});
					$HASH->{$key} = $SELECTED{$cdi_name}->{$key};
				}
			}
			push(@{$DATAS->{'datas'}},$HASH);
		}
		$sth->finish;
		undef $sth;
	}

	$DATAS->{'success'} = JSON::XS::true;
};
if($@){
	$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8($@);
}
#print &JSON::XS::encode_json($DATAS);
&gzip_json($DATAS);

close($LOG);
