use strict;
use JSON::XS;
use Storable;
use File::Basename;
use Carp;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/IM|;

require "common.pl";

sub getZRangeObjects {
	my $dbh = shift;
	my $FORM = shift;
	my $LOG = shift;

#my $LOG;
#open($LOG,"> $FindBin::Bin/logs/getZRangeObjects.txt");
#flock($LOG,2);

#print $LOG "\n\n";
#foreach my $key (sort keys(%$FORM)){
#	print $LOG __LINE__,":\$FORM->{$key}=[",$FORM->{$key},"]\n";
#}

#my $bp3d_table = &getBP3DTablename($FORM->{version});
#my $wt_version = qq|tg_id=$FORM->{tg_id} and tgi_id=$FORM->{tgi_id}| if(exists($FORM->{tg_id}) && exists($FORM->{tgi_id}));

my $IMAGES = {
	"records" => [],
	"total" => 0,
	"success" => JSON::XS::false
};

my $sql_filter = '';
if(exists($FORM->{'filter'})){

	my $sql_cdi_name = qq|select cdi_id from concept_data_info where cdi_delcause is null and ci_id=$FORM->{ci_id} and cdi_name=?|;
	my $sth_cdi_name = $dbh->prepare($sql_cdi_name) or croak $dbh->errstr;

	my $table = qq|concept_data_filter|;
=pod
	unless(&existsTable($table)){
		my $sql =<<SQL;
CREATE TABLE $table (
  ci_id         integer NOT NULL,
  cb_id         integer NOT NULL,
  cdi_id        integer NOT NULL,
  cdf_id        integer NOT NULL,
  cdf_delcause  text,                                  -- 削除理由
  cdf_entry     timestamp without time zone NOT NULL,  -- 追加日時
  cdf_openid    text NOT NULL CHECK(cdf_openid<>''),   -- openid(追加)

  PRIMARY KEY (ci_id,cb_id,cdi_id,cdf_id),
  FOREIGN KEY (ci_id,cb_id) REFERENCES concept_build (ci_id,cb_id) ON DELETE CASCADE,
  FOREIGN KEY (ci_id,cdi_id) REFERENCES concept_data_info (ci_id,cdi_id) ON DELETE CASCADE,
  FOREIGN KEY (ci_id,cdf_id) REFERENCES concept_data_info (ci_id,cdi_id) ON DELETE CASCADE,
  FOREIGN KEY (ci_id,cb_id,cdi_id) REFERENCES concept_data (ci_id,cb_id,cdi_id) ON DELETE CASCADE,
  FOREIGN KEY (ci_id,cb_id,cdf_id) REFERENCES concept_data (ci_id,cb_id,cdi_id) ON DELETE CASCADE
);
SQL
		$dbh->do($sql) or die $dbh->errstr;
	}
=cut

	if(0){
		my $sql_ins = qq|insert into $table (ci_id,cb_id,cdi_id,cdf_id,cdf_entry,cdf_openid) values (?,?,?,?,'now()','system')|;
		my $sth_ins = $dbh->prepare($sql_ins) or croak $dbh->errstr;

		my $sql_filter = qq|select cdi_id from $table where ci_id=$FORM->{ci_id} and cb_id=$FORM->{cb_id} and cdi_id=? and cdf_id=?|;
		my $sth_filter = $dbh->prepare($sql_filter) or croak $dbh->errstr;

		my $sql_fma_isa = qq|select cdi_id from concept_tree where ci_id=$FORM->{ci_id} and cb_id=$FORM->{cb_id} and bul_id=? and cdi_pid=? group by cdi_id|;
		my $sth_fma_isa = $dbh->prepare($sql_fma_isa) or croak $dbh->errstr;

		sub get_cdi_id {
			my $cdf_id = shift;
			my $cdi_pid = shift;
			my $bul_id = shift;
			my $hash = shift;

			$bul_id = 3 unless(defined $bul_id);
			$hash = {} unless(defined $hash);

			my %FID = ();
			my $sth_fma;

			if($cdf_id =~ /^FMA/){
				my $cdi_id;
				$sth_cdi_name->execute($cdf_id) or croak $dbh->errstr;
				$sth_cdi_name->bind_col(1, \$cdi_id, undef);
				$sth_cdi_name->fetch;
				$sth_cdi_name->finish;
				return unless(defined $cdi_id);
				$cdf_id = $cdi_id;
			}
			if($cdi_pid =~ /^FMA/){
				my $cdi_id;
				$sth_cdi_name->execute($cdi_pid) or croak $dbh->errstr;
				$sth_cdi_name->bind_col(1, \$cdi_id, undef);
				$sth_cdi_name->fetch;
				$sth_cdi_name->finish;
				return unless(defined $cdi_id);
				$cdi_pid = $cdi_id;
			}
			$hash->{$cdi_pid} = undef;

			$sth_filter->execute($cdi_pid,$cdf_id) or croak $dbh->errstr;
			my $rows = $sth_filter->rows();
			$sth_filter->finish;
			return if($rows>0);

			$sth_ins->execute($FORM->{ci_id},$FORM->{cb_id},$cdi_pid,$cdf_id) or croak $dbh->errstr;
			$sth_ins->finish;

			$sth_fma = $sth_fma_isa;

			my $cdi_id;
			$sth_fma->execute($bul_id,$cdi_pid) or croak $dbh->errstr;
			$sth_fma->bind_col(1, \$cdi_id, undef);
			while($sth_fma->fetch){
				$FID{$cdi_id} = undef if(defined $cdi_id);
			}
			$sth_fma->finish;
			foreach my $cdi_id (keys(%FID)){
				next if(exists($hash->{$cdi_id}));
				&get_cdi_id($cdf_id,$cdi_id,$bul_id,$hash);
			}
		}

		&get_cdi_id('FMA5018','FMA5018');
		&get_cdi_id('FMA5018','FMA23881');
		&get_cdi_id('FMA5018','FMA85544');
		&get_cdi_id('FMA5018','FMA71324');

		&get_cdi_id('FMA5022','FMA5022');
		&get_cdi_id('FMA5022','FMA10474');
		&get_cdi_id('FMA5022','FMA32558');
		&get_cdi_id('FMA5022','FMA85453');

		&get_cdi_id('FMA3710','FMA3710');
		&get_cdi_id('FMA3710','FMA50722');
		&get_cdi_id('FMA3710','FMA7161',4);
		&get_cdi_id('FMA3710','FMA228642',4);
		&get_cdi_id('FMA3710','FMA228684',4);
		&get_cdi_id('FMA3710','FMA269098',4);

		&get_cdi_id('FMA3710','FMA63812');#追加(2013/04/25)
		&get_cdi_id('FMA3710','FMA63814');#追加(2013/04/25)
		&get_cdi_id('FMA3710','FMA49894',4);#追加(2013/04/25)
	}

	if(defined $FORM->{'filter'}){
		my $cdf_id;
		if($FORM->{'filter'} eq 'FMA5018' || $FORM->{'filter'} eq 'FMA5022' || $FORM->{'filter'} eq 'FMA3710'){
			$sth_cdi_name->execute($FORM->{'filter'}) or croak $dbh->errstr;
			$sth_cdi_name->bind_col(1, \$cdf_id, undef);
			$sth_cdi_name->fetch;
			$sth_cdi_name->finish;
		}

		$sql_filter = qq|select cdi_id from $table where cdf_delcause is null and ci_id=$FORM->{ci_id} and cb_id=$FORM->{cb_id}|;
		$sql_filter .= qq| and cdf_id=$cdf_id| if(defined $cdf_id);

		if(defined $cdf_id){
			$sql_filter = qq| AND bu.cdi_id IN ($sql_filter)|;
		}else{
			$sql_filter = qq| AND bu.cdi_id NOT IN ($sql_filter)|;
		}
	}
}

=pod
if(defined $FORM->{'zrate'}){
	my $sql =<<SQL;
select
 min(bu.rep_xmin),
 max(bu.rep_xmax),
 min(bu.rep_ymin),
 max(bu.rep_ymax),
 min(bu.rep_zmin),
 max(bu.rep_zmax)
from
 representation as bu
where
 bu.rep_delcause is null and 
-- bu.ci_id=$FORM->{ci_id} and 
-- bu.cb_id=$FORM->{cb_id} and 
-- bu.bul_id=$FORM->{bul_id} and
 bu.md_id=$FORM->{md_id} and 
 bu.mv_id=$FORM->{mv_id}
SQL
	my $xmin;
	my $xmax;
	my $ymin;
	my $ymax;
	my $zmin;
	my $zmax;
	my $sth = $dbh->prepare($sql) or croak $dbh->errstr;
	$sth->execute() or croak $dbh->errstr;
	$sth->bind_col(1, \$xmin, undef);
	$sth->bind_col(2, \$xmax, undef);
	$sth->bind_col(3, \$ymin, undef);
	$sth->bind_col(4, \$ymax, undef);
	$sth->bind_col(5, \$zmin, undef);
	$sth->bind_col(6, \$zmax, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;
	if(defined $zmax && defined $zmin){
		print $LOG __LINE__,":\$zmax=[$zmax]\n";
		print $LOG __LINE__,":\$zmin=[$zmin]\n";
		print $LOG __LINE__,":\$FORM->{zrate}=[$FORM->{zrate}]\n";

		my $zrange = ($zmax-$zmin);
		print $LOG __LINE__,":\$FORM->{zposition}=[$FORM->{zposition}]\n";
		$FORM->{'zposition'} = $zmax-($zrange*$FORM->{'zrate'});
		print $LOG __LINE__,":\$FORM->{zposition}=[$FORM->{zposition}]\n";
	}
}
=cut

my @bind_values = ();

my $sql_zdistance;
if(defined $FORM->{'zposition'}){
	$sql_zdistance = qq|abs((bu.rep_zmax+bu.rep_zmin)/2-?)|;
	push(@bind_values,$FORM->{'zposition'});

#	$sql_zdistance = qq|bu.rep_zmax-abs((bu.rep_zmax+bu.rep_zmin)/2-?)|;
#	push(@bind_values,$FORM->{'zposition'});

#	$sql_zdistance = qq|LEAST(bu.rep_zmax-?,?-bu.rep_zmin)|;
#	push(@bind_values,$FORM->{'zposition'});
#	push(@bind_values,$FORM->{'zposition'});
}else{
	$sql_zdistance = qq|0|;
}


my $sql =<<SQL;
select
 a.cdi_id,
 a.taid,
 a.cube_volume,
 a.density,
 a.xmin,
 a.xmax,
 a.xcenter,
 a.xrange,
 a.ymin,
 a.ymax,
 a.ycenter,
 a.yrange,
 a.zmin,
 a.zmax,
 a.zcenter,
 a.zrange,
 a.zdistance,
 a.volume,
 a.cnum
from (

select
 bu.cdi_id,
 bu.rep_xmin as xmin,
 bu.rep_xmax as xmax,
 (bu.rep_xmax+bu.rep_xmin)/2 as xcenter,
 (bu.rep_xmax-bu.rep_xmin) as xrange,
 bu.rep_ymin as ymin,
 bu.rep_ymax as ymax,
 (bu.rep_ymax+bu.rep_ymin)/2 as ycenter,
 (bu.rep_ymax-bu.rep_ymin) as yrange,
 bu.rep_zmin as zmin,
 bu.rep_zmax as zmax,
 (bu.rep_zmax+bu.rep_zmin)/2 as zcenter,
 (bu.rep_zmax-bu.rep_zmin) as zrange,
 $sql_zdistance  as zdistance,
 bu.rep_volume as volume,
 COALESCE(bu.rep_cube_volume,((bu.rep_xmax-bu.rep_xmin)*(bu.rep_ymax-bu.rep_ymin)*(bu.rep_zmax-bu.rep_zmin))/1000) as cube_volume,
-- (bu.rep_density_objs::real/bu.rep_density_ends::real) as density,
 CASE WHEN bu.rep_density_objs>0 AND bu.rep_density_ends>0 THEN (bu.rep_density_objs::real/bu.rep_density_ends::real) ELSE 0 END as density,
 but.t_cnum as cnum,
 bu.rep_primitive as primitive,
 cdi.cdi_taid as taid
from
 representation as bu

left join (
 select
  ci_id,
  cb_id,
  cdi_id,
  bul_id,
  but_cnum as t_cnum,
  but_delcause
 from
  buildup_tree
) as but on (
 but.md_id=bu.md_id and
 but.mv_id=bu.mv_id and
 but.mr_id=bu.mr_id and
 but.ci_id=bu.ci_id and
 but.cb_id=bu.cb_id and
 but.cdi_id=bu.cdi_id and
 but.bul_id=bu.bul_id
)

left join (
 select
  ci_id,
  cdi_id,
  cdi_taid
 from
  concept_data_info
 where
  cdi_delcause is null
) as cdi on (
 cdi.ci_id=bu.ci_id and
 cdi.cdi_id=bu.cdi_id
)

where
 bu.rep_delcause is null and 
 bu.rep_zmin is not null and 
 bu.rep_zmax is not null and
 (bu.ci_id,bu.cb_id,bu.md_id,bu.mv_id,bu.mr_id,bu.bul_id,bu.cdi_id) in 
  (select
    ci_id,
    cb_id,
    md_id,
    mv_id,
    max(mr_id) as mr_id,
    bul_id,
    cdi_id
   from
    representation as bu
   where
    ci_id=$FORM->{ci_id} and 
    cb_id=$FORM->{cb_id} and 
    md_id=$FORM->{md_id} and 
    mv_id=$FORM->{mv_id} and 
    mr_id<=$FORM->{mr_id} and 
    bul_id=$FORM->{bul_id} and
    rep_delcause is null
   group by
    ci_id,
    cb_id,
    md_id,
    mv_id,
    bul_id,
    cdi_id
  )
 $sql_filter
) as a
SQL





my @WHERE = ();

if(defined $FORM->{'zposition'} && defined $FORM->{'zrange'}){
	my $zmin = defined $FORM->{'zmin'} ? $FORM->{'zmin'} : $FORM->{'zposition'} - $FORM->{'zrange'} / 2;
	my $zmax = defined $FORM->{'zmax'} ? $FORM->{'zmax'} : $FORM->{'zposition'} + $FORM->{'zrange'} / 2;

	my $where;
	my $tmp_where;
	my @tmp_bind_values=();
	if(defined $FORM->{'cvmin'} && $FORM->{'cvmin'} =~ /^[0-9\.]+$/){
#		push(@$tmp_where,qq|a.cube_volume>=?|);
		push(@$tmp_where,qq|a.volume>=?|);
		push(@tmp_bind_values,$FORM->{'cvmin'});
	}
	if(defined $FORM->{'cvmax'} && $FORM->{'cvmax'} =~ /^[0-9\.]+$/){
#		push(@$tmp_where,qq|a.cube_volume<?|);
		push(@$tmp_where,qq|a.volume<?|);
		push(@tmp_bind_values,$FORM->{'cvmax'});
	}

	my $temp_where2;
	if(defined $FORM->{'density_max'} && $FORM->{'density_max'} =~ /^[0-9\.]+$/ && defined $FORM->{'density_min'} && $FORM->{'density_min'} =~ /^[0-9\.]+$/){
		push(@$temp_where2,qq|(density<? AND density>=?)|);
		push(@tmp_bind_values,$FORM->{'density_max'});
		push(@tmp_bind_values,$FORM->{'density_min'});
	}elsif(defined $FORM->{'density_max'} && $FORM->{'density_max'} =~ /^[0-9\.]+$/){
		push(@$temp_where2,qq|density<?|);
		push(@tmp_bind_values,$FORM->{'density_max'});
	}elsif(defined $FORM->{'density_min'} && $FORM->{'density_min'} =~ /^[0-9\.]+$/){
		push(@$temp_where2,qq|density>=?|);
		push(@tmp_bind_values,$FORM->{'density_min'});
	}

	if(defined $FORM->{'primitive'} && lc($FORM->{'primitive'}) eq 'true'){
		push(@$temp_where2,qq|primitive|);
	}else{
		push(@$tmp_where,qq|primitive=false|);
	}
	if(defined $temp_where2){
		push(@$tmp_where,qq|(|.join(" or ",@$temp_where2).qq|)|);
	}

#	if(defined $FORM->{'only_ta'} && lc($FORM->{'only_ta'}) eq 'true'){
#		push(@$tmp_where,qq|a.taid is not null|);
#	}


	$where = "and ".join(" and ",@$tmp_where) if(defined $tmp_where);

	push(@WHERE,qq|(a.zmin>=? and a.zmin<=?$where)|);
	push(@bind_values,$zmin);
	push(@bind_values,$zmax);
	push(@bind_values,@tmp_bind_values);

	push(@WHERE,qq|(a.zmax>=? and a.zmax<=?$where)|);
	push(@bind_values,$zmin);
	push(@bind_values,$zmax);
	push(@bind_values,@tmp_bind_values);

	push(@WHERE,qq|(a.zmin>=? and a.zmax<=?$where)|);
	push(@bind_values,$zmin);
	push(@bind_values,$zmax);
	push(@bind_values,@tmp_bind_values);

	push(@WHERE,qq|(a.zmin<=? and a.zmax>=?$where)|);
	push(@bind_values,$zmin);
	push(@bind_values,$zmax);
	push(@bind_values,@tmp_bind_values);

}else{
	my $where;
#	print $LOG __LINE__,":\$FORM->{'zmin'}=[$FORM->{'zmin'}]\n";
#	print $LOG __LINE__,":\$FORM->{'zmax'}=[$FORM->{'zmax'}]\n";

	if(
		defined $FORM->{'zmin'} && $FORM->{'zmin'} =~ /^\[.+\]$/ &&
		defined $FORM->{'zmax'} && $FORM->{'zmax'} =~ /^\[.+\]$/
	){
		eval{
			my $zmin = &JSON::XS::decode_json($FORM->{'zmin'});
			my $zmax = &JSON::XS::decode_json($FORM->{'zmax'});
			if(ref $zmin eq 'ARRAY' && ref $zmax eq 'ARRAY'){
#				print $LOG __LINE__,":\$zmin=[",scalar @$zmin,"]\n";
#				print $LOG __LINE__,":\$zmax=[",scalar @$zmax,"]\n";
				if(scalar @$zmin == 2 && scalar @$zmax == 2){
					if(
						!defined $zmax->[0]                                  && defined $zmin->[0] && $zmin->[0] =~ /^\-*[0-9\.]+$/ &&
						 defined $zmax->[1] && $zmax->[1] =~ /^\-*[0-9\.]+$/ && defined $zmin->[1] && $zmin->[1] =~ /^\-*[0-9\.]+$/
					){
						push(@$where,qq|zmax>=?|);
						push(@bind_values,$zmin->[0]);

						push(@$where,qq|zmin>=?|);
						push(@bind_values,$zmin->[1]);
						push(@$where,qq|zmin<?|);
						push(@bind_values,$zmax->[1]);
					}elsif(
						defined $zmax->[0] && $zmax->[0] =~ /^\-*[0-9\.]+$/ &&  defined $zmin->[0] && $zmin->[0] =~ /^\-*[0-9\.]+$/ &&
						defined $zmax->[1] && $zmax->[1] =~ /^\-*[0-9\.]+$/ && !defined $zmin->[1]
					){
						push(@$where,qq|zmax>=?|);
						push(@bind_values,$zmin->[0]);
						push(@$where,qq|zmax<?|);
						push(@bind_values,$zmax->[0]);

						push(@$where,qq|zmin<=?|);
						push(@bind_values,$zmax->[1]);
					}elsif(
						!defined $zmax->[0]                                  &&  defined $zmin->[0] && $zmin->[0] =~ /^\-*[0-9\.]+$/ &&
						 defined $zmax->[1] && $zmax->[1] =~ /^\-*[0-9\.]+$/ && !defined $zmin->[1]
					){
						push(@$where,qq|zmax>=?|);
						push(@bind_values,$zmin->[0]);

						push(@$where,qq|zmin<?|);
						push(@bind_values,$zmax->[1]);

					}

				}elsif(scalar @$zmin == 3 && scalar @$zmax == 3){
					if(
						!defined $zmax->[0]                                 &&  defined $zmin->[0] && $zmin->[0] =~ /^\-*[0-9\.]+$/ &&
						defined $zmax->[1] && $zmax->[1] =~ /^\-*[0-9\.]+$/ &&  defined $zmin->[1] && $zmin->[1] =~ /^\-*[0-9\.]+$/ &&
						defined $zmax->[2] && $zmax->[2] =~ /^\-*[0-9\.]+$/ && !defined $zmin->[2]
					){
#						push(@$where,qq|a.zmax>=?|);
#						push(@bind_values,$zmin->[0]);
#						push(@$where,qq|a.zmin<=?|);
#						push(@bind_values,$zmax->[2]);


						my @w;

						push(@w,qq|(zmax>=? and zmin>=? and zmin<?)|);
						push(@bind_values,$zmin->[0]);
						push(@bind_values,$zmin->[1]);
						push(@bind_values,$zmax->[1]);


						push(@w,qq|(zmax>=? and zmax<? and zmin<=?)|);
						push(@bind_values,$zmin->[1]);
						push(@bind_values,$zmax->[1]);
						push(@bind_values,$zmax->[2]);


						push(@w,qq|(a.zmax>=? and a.zmin<?)|);
						push(@bind_values,$zmin->[0]);
						push(@bind_values,$zmax->[2]);

						push(@$where,'('.join(" or ",@w).')');

					}
				}
			}
		};
	}else{
		if(defined $FORM->{'zmin'} && $FORM->{'zmin'} =~ /^\-*[0-9\.]+$/){
			push(@$where,qq|a.zmin>=?|);
			push(@bind_values,$FORM->{'zmin'});
		}
		if(defined $FORM->{'zmax'} && $FORM->{'zmax'} =~ /^\-*[0-9\.]+$/){
			push(@$where,qq|a.zmax<?|);
			push(@bind_values,$FORM->{'zmax'});
		}
	}

	if(defined $FORM->{'cvmax'} && $FORM->{'cvmax'} =~ /^[0-9\.]+$/){
#		push(@$where,qq|cube_volume<?|);
		push(@$where,qq|a.volume<?|);
		push(@bind_values,$FORM->{'cvmax'});
	}
	if(defined $FORM->{'cvmin'} && $FORM->{'cvmin'} =~ /^[0-9\.]+$/){
#		push(@$where,qq|cube_volume>=?|);
		push(@$where,qq|a.volume>=?|);
		push(@bind_values,$FORM->{'cvmin'});
	}
#	if(defined $FORM->{'only_ta'} && lc($FORM->{'only_ta'}) eq 'true'){
#		push(@$where,qq|a.taid is not null|);
#	}

	my $temp_where;
	if(defined $FORM->{'density_max'} && $FORM->{'density_max'} =~ /^[0-9\.]+$/ && defined $FORM->{'density_min'} && $FORM->{'density_min'} =~ /^[0-9\.]+$/){
		push(@$temp_where,qq|(density<? AND density>=?)|);
		push(@bind_values,$FORM->{'density_max'});
		push(@bind_values,$FORM->{'density_min'});
	}elsif(defined $FORM->{'density_max'} && $FORM->{'density_max'} =~ /^[0-9\.]+$/){
		push(@$temp_where,qq|density<?|);
		push(@bind_values,$FORM->{'density_max'});
	}elsif(defined $FORM->{'density_min'} && $FORM->{'density_min'} =~ /^[0-9\.]+$/){
		push(@$temp_where,qq|density>=?|);
		push(@bind_values,$FORM->{'density_min'});
	}
	if(defined $FORM->{'primitive'} && lc($FORM->{'primitive'}) eq 'true'){
		push(@$temp_where,qq|primitive|);
	}else{
		push(@$where,qq|primitive=false|);
	}
	if(defined $temp_where){
		push(@$where,qq|(|.join(" or ",@$temp_where).qq|)|);
	}

	push(@WHERE,join(" and ",@$where)) if(defined $where);
}

if(0 && defined $FORM->{'only_ta'}){
#	push(@WHERE,qq|a.taid is not null|);
#	push(@bind_values,$FORM->{'cvmax'});

	$sql .= qq| where |;
	$sql .= qq|(|.join(" or ",@WHERE).qq|) AND | if(scalar @WHERE > 0);
	$sql .= qq|a.taid is not null|;

}
else{
	$sql .= qq| where |.join(" or ",@WHERE) if(scalar @WHERE > 0);
}




$sql .= qq| group by a.cdi_id,a.taid,a.xmin,a.xmax,a.xcenter,a.xrange,a.ymin,a.ymax,a.ycenter,a.yrange,a.zmin,a.zmax,a.zcenter,a.zrange,a.zdistance,a.volume,a.cube_volume,a.cnum|;
$sql .= qq|,a.density|;
#$sql .= qq| order by a.zdistance,a.zrange|;
#$sql .= qq| order by a.xrange,a.zrange,a.zdistance|;

if(defined $FORM->{'zposition'} && defined $FORM->{'zrange'}){
#	$sql .= qq| order by a.cnum,a.zdistance,a.zrange,a.xrange,a.yrange|;
#	$sql .= qq| order by a.zdistance,a.zrange,a.xrange,a.yrange|;
	$sql .= qq| order by a.zdistance,a.zrange,a.xrange,a.yrange,a.density desc|;
}else{
	$sql .= qq| order by a.zmax desc,a.xcenter,a.xrange,a.ycenter,a.yrange,a.cnum|;
}
#print $LOG __LINE__,":\$sql=[$sql]\n";
#print $LOG __LINE__,":\@bind_values=[".join(",",@bind_values)."]\n";

my $sql_cdi = qq|select cdi_name from concept_data_info where cdi_delcause is null and ci_id=$FORM->{ci_id} and cdi_id=?|;
#print $LOG __LINE__,":\$sql_cdi=[$sql_cdi]\n";
my $sth_cdi = $dbh->prepare($sql_cdi) or croak $dbh->errstr;


print $LOG __LINE__.":\$sql=[$sql]\n" if(defined $LOG);
print $LOG __LINE__.":\@bind_values=[".(scalar @bind_values)."]\n" if(defined $LOG);
print $LOG __LINE__.":\@bind_values=[".join("\n",@bind_values)."]\n" if(defined $LOG);

my $sth = $dbh->prepare($sql) or croak $dbh->errstr;
if(scalar @bind_values > 0){
	$sth->execute(@bind_values) or croak $dbh->errstr;
}else{
	$sth->execute() or croak $dbh->errstr;
}
$IMAGES->{'total'} = $sth->rows();
#print $LOG __LINE__,":\$IMAGES->{'total'}=[$IMAGES->{'total'}]\n";


my $cdi_id;
my $cdi_taid;
my $column_number = 0;
$sth->bind_col(++$column_number, \$cdi_id, undef);
$sth->bind_col(++$column_number, \$cdi_taid, undef);

my %DISP_FMA = ();

#my @extlist = qw|.png .gif|;

while($sth->fetch){
	if(defined $FORM->{'only_ta'} && lc($FORM->{'only_ta'}) eq 'true'){
		next unless(defined $cdi_taid);
	}
#print $LOG __LINE__,":[$cdi_id][$name_j][$name_e][$cube_volume][$density_bp3d][$density_isa][$density_partof][$density_max][$density_min]\n";
#	push(@{$IMAGES->{'records'}},&getFMA($dbh,\%FORM,$cdi_id));

#print $LOG __LINE__,":\$cdi_id=[$cdi_id]\n";
	my $cdi_name;
	if(defined $cdi_id){
		$sth_cdi->execute($cdi_id) or croak $dbh->errstr;
		$sth_cdi->bind_col(1, \$cdi_name, undef);
		$sth_cdi->fetch;
		$sth_cdi->finish;
#print $LOG __LINE__,":\$cdi_name=[$cdi_name]\n";
	}

=pod
	if(exists($FORM->{'filter'})){
		if($FORM->{'filter'} eq 'FMA5018'){
			next unless(exists($FMA5018->{$cdi_id}));
		}elsif($FORM->{'filter'} eq 'FMA5022'){
			next unless(exists($FMA5022->{$cdi_id}));
		}elsif($FORM->{'filter'} eq 'other.obo'){
			next if(exists($FMA5018->{$cdi_id}) || exists($FMA5022->{$cdi_id}));
		}
	}
=cut

#print $LOG __LINE__,":\$cdi_id=[$cdi_id]\n";

#	my $cdi_name;
#	$sth_cdi->execute($cdi_id) or croak $dbh->errstr;
#	$sth_cdi->bind_col(1, \$cdi_name, undef);
#	$sth_cdi->fetch;
#	$sth_cdi->finish;
#print $LOG __LINE__,":\$cdi_name=[$cdi_name]\n";

	push(@{$IMAGES->{'records'}},$cdi_name) if(defined $cdi_name);
}
$sth->finish;

$IMAGES->{'total'} = scalar @{$IMAGES->{'records'}};

undef $sth;

$IMAGES->{'success'} = JSON::XS::true;

return $IMAGES;

}

1;
