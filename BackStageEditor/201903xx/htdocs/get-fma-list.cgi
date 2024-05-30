#!/opt/services/ag/local/perl/bin/perl

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
my $cgi = CGI->new;
&getParams($cgi,\%FORM,\%COOKIE);
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

open(my $LOG,">> $logfile");
select($LOG);
$| = 1;
select(STDOUT);

flock($LOG,2);
print $LOG "\n[$logtime]:$0\n";
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);

&setDefParams(\%FORM,\%COOKIE);

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);

#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $DATAS = {
	"datas" => [],
	"total" => 0,
	"success" => JSON::XS::false
};

unless(
	(exists $FORM{'query'}      && defined $FORM{'query'})      ||
	(exists $FORM{'cdi_name_e'} && defined $FORM{'cdi_name_e'}) ||
	(exists $FORM{'cdi_name'}   && defined $FORM{'cdi_name'})
){
#	print &JSON::XS::encode_json($DATAS);
	&gzip_json($DATAS);
	exit;
}

eval{
	my $operator = &get_ludia_operator();
	my $query;
	if(exists $FORM{'query'} && defined  $FORM{'query'}){
		$query = $FORM{'query'};
		my $space = qq|　|;
		&utf8::decode($query) unless(&utf8::is_utf8($query));
		&utf8::decode($space) unless(&utf8::is_utf8($space));
		$query =~ s/$space/ /g;
		&utf8::encode($query);
	}
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
	unshift(@SORT,{
		property  => 'is_rep',
		direction => 'DESC'
	});

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
 cdi.ci_id,
 rep.cb_id,
 rep.md_id,
 rep.mv_id,
 rep.mr_id,
 rep.bul_id,
 rep_id,
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
 EXTRACT(EPOCH FROM rep_entry),
 cdi_name,
 cdi_name_j,
 COALESCE(cd.cd_name,bd.cd_name,cdi_name_e) as cdi_name_e,
 cdi_name_k,
 cdi_name_l,
 md.md_abbr,
 mv.mv_name_e,
 bul.bul_abbr,
 CASE
  WHEN rep_id is null THEN 0::integer
  ELSE 1::integer
 END as is_rep,
 rep_primitive,
 CASE
  WHEN rep_density_objs is null or rep_density_ends is null THEN 0::integer
  ELSE rep_density_objs/rep_density_ends
 END as rep_density,
 bti.but_cnum,

 rep_child_objs,
 mv.mv_publish,
 mv.mv_use,
 mv.mv_frozen,
 cdi.cdi_id,
 bti.but_cids,
 EXTRACT(EPOCH FROM cm_modified) as cm_max_entry_cdi,

 COALESCE(cd.seg_id,bd.seg_id,0) as seg_id,
 COALESCE(cd.seg_name,bd.seg_name) as seg_name,
 COALESCE(cd.seg_color,bd.seg_color) as seg_color,
 COALESCE(cd.seg_thum_bgcolor,bd.seg_thum_bgcolor) as seg_thum_bgcolor,
 COALESCE(cd.seg_thum_fgcolor,bd.seg_thum_fgcolor) as seg_thum_fgcolor,

 COALESCE(EXTRACT(EPOCH FROM rep_entry),0) - COALESCE(EXTRACT(EPOCH FROM cm_modified),0) as time_diff

from 
  concept_data_info as cdi

left join (
  select
   *
  from
   representation
  WHERE
   rep_delcause is null AND
   (ci_id,cb_id,cdi_id,md_id,mv_id,mr_id,bul_id) in (
     select
       ci_id,cb_id,cdi_id,md_id,mv_id,max(mr_id) as mr_id,bul_id
     from
       representation
     where
       ci_id=$FORM{ci_id} AND
       cb_id=$FORM{cb_id} AND
       md_id=$FORM{md_id} AND
       mv_id=$FORM{mv_id} AND
       mr_id<=$FORM{mr_id} AND
       bul_id=$FORM{bul_id}
     group by
       ci_id,cb_id,cdi_id,md_id,mv_id,bul_id
   )


 ) as rep on
    rep.ci_id=cdi.ci_id AND
    rep.cdi_id=cdi.cdi_id

left join (
  select * from model
 ) as md on md.md_id=rep.md_id
left join (
  select * from model_version
 ) as mv on mv.md_id=rep.md_id and mv.mv_id=rep.mv_id
left join (
  select * from buildup_logic
 ) as bul on bul.bul_id=rep.bul_id

left join (
  select * from buildup_tree
  where
   md_id=$FORM{md_id} AND
   mv_id=$FORM{mv_id} AND
   mr_id=$FORM{mr_id} AND
   bul_id=$FORM{bul_id}
--   and but_delcause is null
 ) as but on
    but.ci_id=cdi.ci_id and
    but.cdi_id=cdi.cdi_id

left join (
  select * from buildup_tree_info
  where
   md_id=$FORM{md_id} AND
   mv_id=$FORM{mv_id} AND
   mr_id=$FORM{mr_id} AND
   ci_id=$FORM{ci_id} AND
   cb_id=$FORM{cb_id} AND
   bul_id=$FORM{bul_id}

 ) as bti on
    bti.ci_id=cdi.ci_id and
    bti.cdi_id=cdi.cdi_id

left join (
  select ci_id,cdi_id,count(bul_id) as c,max(bul_id) as m from (
    select
     ci_id,
     cdi_id,
     bul_id
    from
     buildup_tree
    where
     md_id=$FORM{md_id} AND
     mv_id=$FORM{mv_id} AND
     mr_id=$FORM{mr_id} AND
     but_delcause is null
    group by
     ci_id,cdi_id,bul_id
  ) as a
  group by a.ci_id,a.cdi_id
) as but2 on
   cdi.ci_id=but2.ci_id AND
   cdi.cdi_id=but2.cdi_id

left join (
  select * from concept_art_map_modified where ci_id=$FORM{ci_id} AND cb_id=$FORM{cb_id} AND md_id=$FORM{md_id} AND mv_id=$FORM{mv_id} AND mr_id=$FORM{mr_id} AND bul_id=$FORM{bul_id}
) as cmm on
    cmm.cdi_id=cdi.cdi_id

left join (
 select
  cd.*,
  seg_name,
  seg_color,
  seg_thum_bgcolor,
  seg_thum_fgcolor
 from
  concept_data as cd
 left join (
  select
   seg_id,
   seg_name,
   seg_color,
   seg_thum_bgcolor,
   seg_thum_fgcolor
  from
   concept_segment
  where
   seg_delcause is null
 ) as cs on
    cs.seg_id=cd.seg_id
 where
  ci_id=$FORM{'ci_id'} AND
  cb_id=$FORM{'cb_id'} AND
  cd_delcause is null
) as cd on
   cdi.cdi_id=cd.cdi_id

left join (
 select
  bd.*,
  seg_name,
  seg_color,
  seg_thum_bgcolor,
  seg_thum_fgcolor
 from
  buildup_data as bd
 left join (
  select
   seg_id,
   seg_name,
   seg_color,
   seg_thum_bgcolor,
   seg_thum_fgcolor
  from
   concept_segment
  where
   seg_delcause is null
 ) as cs on
    cs.seg_id=bd.seg_id
 where
  md_id=$FORM{md_id} AND
  mv_id=$FORM{mv_id} AND
  mr_id=$FORM{mr_id} AND
  cd_delcause is null
) as bd on
   cdi.cdi_id=bd.cdi_id


where
  but2.cdi_id is not null AND
--  but.but_delcause is null AND
  cdi.cdi_delcause is null AND
  (cdi.ci_id,cdi.cdi_id) in (
 select
   ci_id,
   cdi_id
 from
   concept_data_info
 where
SQL
	if(exists $FORM{'query'} && defined  $FORM{'query'}){
#		$sql.=<<SQL;
#   (ARRAY[cdi_name,cdi_name_j,cdi_name_e,cdi_name_k,cdi_name_l] $operator ?) AND
#SQL
#		$sql.=<<SQL;
#   senna.to_tsvector(cdi_name_j || ' ' || cdi_name_e || ' ' || cdi_name_k || ' ' || cdi_name_l) @@ senna.to_tsquery(?) AND
#SQL
		$sql.=<<SQL;
   cdi_name || ' ' || cdi_name_j || ' ' || cdi_name_e || ' ' || cdi_name_k || ' ' || cdi_name_l ilike ? AND
SQL
	}elsif(exists $FORM{'cdi_name_e'} && defined  $FORM{'cdi_name_e'}){
		$sql.=<<SQL;
   lower(cdi_name_e)=lower(?) AND
SQL
	}elsif(exists $FORM{'cdi_name'} && defined  $FORM{'cdi_name'}){
		$sql.=<<SQL;
   lower(cdi_name)=lower(?) AND
SQL
	}
	$sql.=<<SQL;
   cdi_delcause is null
SQL
	if(exists $FORM{'query'} && defined  $FORM{'query'}){
		$sql.=<<SQL;
UNION

 select
   ci_id,
   cdi_id
 from
   representation
 where
   rep_id ~* ? AND
   rep_delcause is null AND
   (ci_id,cb_id,cdi_id,md_id,mv_id,mr_id,bul_id) in (
     select
       ci_id,cb_id,cdi_id,md_id,mv_id,max(mr_id) as mr_id,bul_id
     from
       representation
     where
       ci_id=$FORM{ci_id} AND
       cb_id=$FORM{cb_id} AND
       md_id=$FORM{md_id} AND
       mv_id=$FORM{mv_id} AND
       mr_id<=$FORM{mr_id} AND
       bul_id=$FORM{bul_id}
     group by
       ci_id,cb_id,cdi_id,md_id,mv_id,bul_id
   )
SQL
	}
	$sql.=<<SQL;
)
) as a
SQL

	print $LOG __LINE__,":\$sql=[$sql]\n";

	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	if(exists $FORM{'query'} && defined  $FORM{'query'}){
		my @bind_values;
#		push(@bind_values,qq|*D+ $query|);
##		push(@bind_values,$query);
#		push(@bind_values,$query);
		push(@bind_values,'%'.$query.'%');
		push(@bind_values,$query);
		print $LOG __LINE__,":\@bind_values=[",join(",",@bind_values),"]\n";
		$sth->execute(@bind_values) or die $dbh->errstr;
	}elsif(exists $FORM{'cdi_name_e'} && defined  $FORM{'cdi_name_e'}){
		$sth->execute($FORM{'cdi_name_e'}) or die $dbh->errstr;
	}elsif(exists $FORM{'cdi_name'} && defined  $FORM{'cdi_name'}){
		$sth->execute($FORM{'cdi_name'}) or die $dbh->errstr;
	}
	$DATAS->{'total'} = $sth->rows();
	$sth->finish;
	undef $sth;
	print $LOG __LINE__,":\$DATAS->{'total'}=[",$DATAS->{'total'},"]\n";

	if(scalar @SORT > 0){
		my @orderby;
		foreach (@SORT){
			if($_->{property} eq 'rep_id'){
				push(@orderby,qq|$_->{property} $_->{direction} NULLS LAST|);
			}else{
				push(@orderby,qq|$_->{property} $_->{direction}|);
			}
		}
		$sql .= qq| order by | . join(",",@orderby) if(scalar @orderby > 0);
	}
	$sql .= qq| limit $FORM{limit}| if(defined $FORM{limit});
	$sql .= qq| offset $FORM{start}| if(defined $FORM{start});

	print $LOG __LINE__,":\$sql=[$sql]\n";

	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	if(exists $FORM{'query'} && defined  $FORM{'query'}){
		my @bind_values;
		push(@bind_values,qq|*D+ $query|);
#		push(@bind_values,$query);
		push(@bind_values,$query);
		print $LOG __LINE__,":\@bind_values=[",join(",",@bind_values),"]\n";
		$sth->execute(@bind_values) or die $dbh->errstr;
	}elsif(exists $FORM{'cdi_name_e'} && defined  $FORM{'cdi_name_e'}){
		$sth->execute($FORM{'cdi_name_e'}) or die $dbh->errstr;
	}elsif(exists $FORM{'cdi_name'} && defined  $FORM{'cdi_name'}){
		$sth->execute($FORM{'cdi_name'}) or die $dbh->errstr;
	}

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
	my $bul_abbr;
	my $but_cnum;

	my $is_rep;

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

	$sth->bind_col(++$column_number, \$rep_zmin,   undef);
	$sth->bind_col(++$column_number, \$rep_zmax,   undef);
	$sth->bind_col(++$column_number, \$rep_zcenter,   undef);

	$sth->bind_col(++$column_number, \$rep_volume,   undef);
	$sth->bind_col(++$column_number, \$rep_entry,   undef);
	$sth->bind_col(++$column_number, \$cdi_name,   undef);
	$sth->bind_col(++$column_number, \$cdi_name_j,   undef);
	$sth->bind_col(++$column_number, \$cdi_name_e,   undef);
	$sth->bind_col(++$column_number, \$cdi_name_k,   undef);
	$sth->bind_col(++$column_number, \$cdi_name_l,   undef);
	$sth->bind_col(++$column_number, \$md_abbr,   undef);
	$sth->bind_col(++$column_number, \$mv_name_e,   undef);
	$sth->bind_col(++$column_number, \$bul_abbr,   undef);

	$sth->bind_col(++$column_number, \$is_rep,   undef);

	$sth->bind_col(++$column_number, \$rep_primitive,   undef);
	$sth->bind_col(++$column_number, \$rep_density,   undef);
	$sth->bind_col(++$column_number, \$but_cnum,   undef);

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

	$sth->bind_col(++$column_number, \$time_diff,   undef);

	while($sth->fetch){

#		my $cm_max_num_cdi;
#		my $cm_max_entry_cdi;
		my $isUpdate = 0;
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
			}
			elsif(defined $cm_max_entry_cdi){
				$isUpdate = 1;
			}
			elsif(defined $cdi_id){
#				$isUpdate = ((defined $cm_max_num_cdi && $cm_max_num_cdi>0) ? 1 : 0);
			}
		}

		my $iconCls;
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
		}elsif(defined $but_cnum && $but_cnum>0){
			$iconCls = qq|timgfolder_route_parts|;
		}elsif(defined $but_cnum && $but_cnum==0){
			$iconCls = qq|timgfolder_end_parts|;
		}
		$iconCls = ($isUpdate ? 'warning_' : '').$iconCls if(defined $iconCls);

		my $HASH = {
			ci_id      => $ci_id,
			cb_id      => $cb_id,
			md_id      => $md_id,
			mv_id      => $mv_id,
			mr_id      => $mr_id,
			bul_id      => $bul_id,

			rep_id      => $rep_id,
	#		rep_id      => $is_rep,

			rep_xmin    => defined $rep_entry ? $rep_xmin - 0 : 0,
			rep_xmax    => defined $rep_entry ? $rep_xmax - 0 : 0,
			rep_xcenter => defined $rep_entry ? $rep_xcenter - 0 : 0,
			rep_ymin    => defined $rep_entry ? $rep_ymin - 0 : 0,
			rep_ymax    => defined $rep_entry ? $rep_ymax - 0 : 0,
			rep_ycenter => defined $rep_entry ? $rep_ycenter - 0 : 0,
			rep_zmin    => defined $rep_entry ? $rep_zmin - 0 : 0,
			rep_zmax    => defined $rep_entry ? $rep_zmax - 0 : 0,
			rep_zcenter => defined $rep_entry ? $rep_zcenter - 0 : 0,
			rep_volume  => defined $rep_entry ? $rep_volume - 0 : 0,
			rep_entry   => defined $rep_entry ? $rep_entry - 0 : 0,
			cdi_name    => $cdi_name,
			cdi_name_j  => $cdi_name_j,
			cdi_name_e  => $cdi_name_e,
			cdi_name_k  => $cdi_name_k,
			cdi_name_l  => $cdi_name_l,
			md_abbr     => $md_abbr,
			mv_name_e   => $mv_name_e,
			bul_abbr    => $bul_abbr,
#			but_cnum    => $but_cnum,

			rep_primitive       => $rep_primitive ? JSON::XS::true : JSON::XS::false,
			rep_density         => $rep_density,
			rep_density_iconCls => $iconCls,

#			cm_max_num_cdi => defined $cm_max_num_cdi ? $cm_max_num_cdi+0 : undef,
			cm_max_entry_cdi => defined $cm_max_entry_cdi ? $cm_max_entry_cdi+0 : undef,

			seg_id        => $seg_id,
			seg_name        => $seg_name,
			seg_color        => $seg_color,
			seg_thum_bgcolor => $seg_thum_bgcolor,
			seg_thum_fgcolor => $seg_thum_fgcolor,

			time_diff => $time_diff - 0,

			disabled    => defined $rep_id ? JSON::XS::false : JSON::XS::true
		};

		if(exists $SELECTED{$cdi_name} && defined $SELECTED{$cdi_name}){
			foreach my $key (qw/color opacity remove selected/){
				next unless(exists $SELECTED{$cdi_name}->{$key} && defined $SELECTED{$cdi_name}->{$key});
				$HASH->{$key} = $SELECTED{$cdi_name}->{$key};
			}
		}

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

		push(@{$DATAS->{'datas'}},$HASH);
	}
	$sth->finish;
	undef $sth;

	$DATAS->{'success'} = JSON::XS::true;
};
if($@){
	$DATAS->{'msg'} = $@;
}
#print &JSON::XS::encode_json($DATAS);
&gzip_json($DATAS);

close($LOG);
