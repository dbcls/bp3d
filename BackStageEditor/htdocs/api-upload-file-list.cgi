#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use File::Basename;
use Cwd qw(abs_path);
use File::Spec;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
#use CGI::Carp::DebugScreen ( debug => 1 );
use Data::Dumper;
use DBD::Pg;
use POSIX;
use Time::HiRes;
use List::Util;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;

use BITS::Config;
use BITS::VTK;
use BITS::Voxel;
use BITS::ConceptArtMapModified;

use obj2deci;
require "webgl_common.pl";
use cgi_lib::common;

my $query = CGI->new;
my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
#my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);
my($log_file,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

#my @extlist = qw|.cgi|;
#my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);

my $t0 = [&Time::HiRes::gettimeofday()];
my($epocsec,$microsec) = &Time::HiRes::gettimeofday();
my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);

#my $log_file = qq|$FindBin::Bin/logs/$cgi_name.txt|;
$log_file .= qq|.$FORM{'cmd'}| if(exists $FORM{'cmd'});

$log_file .= qq|.artg_ids| if(exists $FORM{'artg_ids'});
$log_file .= qq|.art_datas| if(exists $FORM{'art_datas'});
#$log_file .=  sprintf(".%04d%02d%02d%02d",$year+1900,$mon+1,$mday,$hour);
$log_file .=  sprintf(".%02d%02d%02d.%05d",$hour,$min,$sec,$$);

open(my $LOG,">> $log_file");
select($LOG);
$| = 1;
select(STDOUT);

if(defined $LOG){
	&cgi_lib::common::message(sprintf("\n%04d:%04d/%02d/%02d %02d:%02d:%02d.%d",__LINE__,$year+1900,$mon+1,$mday,$hour,$min,$sec,$microsec), $LOG);
	&cgi_lib::common::dumper(\%FORM, $LOG);

	#$epocsec = &Time::HiRes::tv_interval($t0);
	&cgi_lib::common::dumper($epocsec, $LOG);

}

$FORM{'cmd'} = 'read' unless(defined $FORM{'cmd'});
#$FORM{'start'} = 0 unless(defined $FORM{'start'});
#$FORM{'limit'} = 25 unless(defined $FORM{'limit'});

#$FORM{'name'} = qq|120406_liver_divided01_obj|;

#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $DATAS = {
	'datas' => [],
	'total' => 0,
	'success' => JSON::XS::false
};

=pod
eval{
	die "error!!";
};
if($@){
	$DATAS->{'msg'} = $@;
}
my $json = &cgi_lib::common::encodeJSON($DATAS);
print $json;
close(LOG);
exit;
=cut


=pod
http://192.168.1.237/WebGL/130710/api-upload-file-list.cgi?cmd=search&md_id=1&mv_id=3&mr_id=2&ci_id=1&cb_id=4&bul_id=3&limit=10&art_id=FJ3660
=cut

=pod
$FORM{'art_point'} = qq|{"x":41.81039175449132,"y":-147.36891142464657,"z":805.2097610111996}|;
$FORM{'model'} = qq|bp3d|;
$FORM{'version'} = qq|4.0|;
$FORM{'ag_data'} = qq|obj/bp3d/4.0|;
$FORM{'tree'} = qq|isa|;
$FORM{'md_id'} = qq|1|;
$FORM{'mv_id'} = qq|3|;
$FORM{'mr_id'} = qq|2|;
$FORM{'ci_id'} = qq|1|;
$FORM{'cb_id'} = qq|4|;
$FORM{'bul_id'} = qq|3|;
$FORM{'art_id'} = qq|FJ3484|;
$FORM{'conditions'} = qq|{"parts_map":true,"version":[{"md_id":1,"mv_id":3,"mr_id":2}]}|;
$FORM{'start'} = qq|0|;
$FORM{'limit'} = qq|10|;
=cut



#if($FORM{'cmd'} eq 'read' && exists $FORM{'art_id'} && defined $FORM{'art_id'}){
if($FORM{'cmd'} eq 'read'){
	eval{
		unless(
			exists $FORM{'md_id'} && defined $FORM{'md_id'} && $FORM{'md_id'} =~ /^[0-9]+$/ &&
			exists $FORM{'mv_id'} && defined $FORM{'mv_id'} && $FORM{'mv_id'} =~ /^[0-9]+$/ &&
			exists $FORM{'mr_id'} && defined $FORM{'mr_id'} && $FORM{'mr_id'} =~ /^[0-9]+$/ &&
			exists $FORM{'ci_id'} && defined $FORM{'ci_id'} && $FORM{'ci_id'} =~ /^[0-9]+$/ &&
			exists $FORM{'cb_id'} && defined $FORM{'cb_id'} && $FORM{'cb_id'} =~ /^[0-9]+$/ &&
			exists $FORM{'bul_id'} && defined $FORM{'bul_id'} && $FORM{'bul_id'} =~ /^[0-9]+$/
		){
			&gzip_json($DATAS);
			exit;
		}

		my $selected_art_ids;
		if(exists $FORM{'selected_art_ids'} && defined $FORM{'selected_art_ids'}){
			$selected_art_ids = &cgi_lib::common::decodeJSON($FORM{'selected_art_ids'});
		};

#if($FORM{'cmd'} eq 'read'){
		my $md_id=$FORM{'md_id'};
		my $mv_id=$FORM{'mv_id'};
		my $mr_id=$FORM{'mr_id'};
		my $ci_id=$FORM{'ci_id'};
		my $cb_id=$FORM{'cb_id'};
		my $bul_id=$FORM{'bul_id'};

		my $where_artg_id;

		if(exists $FORM{'artg_ids'} && defined $FORM{'artg_ids'}){
			my $artg_ids = &cgi_lib::common::decodeJSON($FORM{'artg_ids'});
			if(defined $artg_ids && ref $artg_ids eq 'ARRAY' && scalar @$artg_ids > 0){
				my $artg_id = join(",",@$artg_ids);
	#			$where_artg_id = qq|where art.artg_id in ($artg_id)|;
				$where_artg_id = qq|where artg_id in ($artg_id)|;
			}
			unless(exists $FORM{'sort'} && defined $FORM{'sort'}){
				my @S = ({'property'=>'artg_name','direction'=>'ASC'},{'property'=>'art_name','direction'=>'ASC'});
				$FORM{'sort'} = &cgi_lib::common::encodeJSON(\@S);
			}
		}
#高速化が目的の処理
		elsif(exists $FORM{'art_datas'} && defined $FORM{'art_datas'}){
			my $art_datas = &cgi_lib::common::decodeJSON($FORM{'art_datas'});
			if(defined $art_datas && ref $art_datas eq 'ARRAY' && scalar @$art_datas > 0){
				my @datas;
				foreach my $art_data (@$art_datas){
					push(@datas,qq|('$art_data->{art_id}',$art_data->{artg_id})|);
				}
				$where_artg_id = qq|where (art_id,artg_id) in (|.join(',',@datas).qq|)|;
			}
#			delete $FORM{'sort'} if(exists $FORM{'sort'} && defined $FORM{'sort'});
		}
		elsif(exists $FORM{'art_mirroring_id'} && defined $FORM{'art_mirroring_id'}){
			my $sql=<<SQL;
select 
 hafi.artg_id
from
 (
  select art_id,artg_id from art_file_info
  where
   art_id=?
  group by
   art_id,artg_id
 ) as hafi

LEFT JOIN (
  select artg_id,count(artg_id) as art_count from art_file_info
  group by artg_id
) as c on c.artg_id=hafi.artg_id
order by art_count
limit 1
SQL
			my $sth = $dbh->prepare($sql) or die $dbh->errstr;
			$sth->execute($FORM{'art_mirroring_id'}) or die $dbh->errstr;
			my $artg_id;
			$sth->bind_col(1, \$artg_id, undef);
			$sth->fetch;
			$sth->finish;
			undef $sth;
			$where_artg_id = sprintf(qq|where (art_id,artg_id) in (('%s',%d))|,$FORM{'art_mirroring_id'},$artg_id) if(defined $artg_id);
		}

		if(defined $where_artg_id){
			my $sql=<<SQL;
select * from (
select
 arti.art_id,
 hart.art_hist_serial,
 arti.art_name,
 arti.art_ext,
 arti.art_mirroring,
 arti.artg_id,
 artg_name,
 EXTRACT(EPOCH FROM arti.art_entry) as arti_entry
from
 (select *
  from
   art_file_info
  where
   (art_id) in (select art_id from art_file_info $where_artg_id group by art_id)
 ) as arti

--グループ情報
left join (
   select * from art_group
 ) as artg on
    artg.artg_id=arti.artg_id

left join (
   select
    art_id,
    max(hist_serial) as art_hist_serial
   from
    history_art_file
   where
    hist_event in (select he_id from history_event where he_name in ('INSERT','UPDATE'))
   group by art_id
 ) as hart on
    hart.art_id=arti.art_id
) as a
SQL

			print $LOG __LINE__,qq|:\$sql=[$sql]\n|;

			my $column_number;
			my $sth_md = $dbh->prepare(qq|select md_abbr from model where md_id=$md_id|) or die $dbh->errstr;
			$sth_md->execute() or die $dbh->errstr;
			my $md_abbr;
			$column_number = 0;
			$sth_md->bind_col(++$column_number, \$md_abbr, undef);
			$sth_md->fetch;
			$sth_md->finish;
			undef $sth_md;

			my $sth_mv = $dbh->prepare(qq|select mv_name_e from model_version where md_id=$md_id AND mv_id=$mv_id|) or die $dbh->errstr;
			$sth_mv->execute() or die $dbh->errstr;
			my $mv_name_e;
			$column_number = 0;
			$sth_mv->bind_col(++$column_number, \$mv_name_e, undef);
			$sth_mv->fetch;
			$sth_mv->finish;
			undef $sth_mv;

			my $sth_bul = $dbh->prepare(qq|select bul_abbr from buildup_logic where bul_id=$bul_id|) or die $dbh->errstr;
			$sth_bul->execute() or die $dbh->errstr;
			my $bul_abbr;
			$column_number = 0;
			$sth_bul->bind_col(++$column_number, \$bul_abbr, undef);
			$sth_bul->fetch;
			$sth_bul->finish;
			undef $sth_bul;


			my $sql_art =<<SQL;
select 
 EXTRACT(EPOCH FROM art_timestamp) as art_timestamp,
 art_md5,
 art_data_size,
 art_xmin,
 art_xmax,
 art_ymin,
 art_ymax,
 art_zmin,
 art_zmax,
 to_number(to_char((art_xmax+art_xmin)/2,'FM99990D0000'),'99990D0000S') as art_xcenter,
 to_number(to_char((art_ymax+art_ymin)/2,'FM99990D0000'),'99990D0000S') as art_ycenter,
 to_number(to_char((art_zmax+art_zmin)/2,'FM99990D0000'),'99990D0000S') as art_zcenter,
 art_volume,
 art_cube_volume
from
 art_file
where
 art_id=?
SQL
			my $sth_art = $dbh->prepare($sql_art) or die $dbh->errstr;


			my $sql_arto =<<SQL;
select 
 EXTRACT(EPOCH FROM arto_entry) as arto_entry,
 arto_id,
 arto_comment,
 arti.art_name as arto_name,
 arti.art_ext as arto_ext,
 artg.artg_id as artog_id,
 artg.artg_name as artog_name
from
 art_org_info as arto
left join (
 select * from art_file_info
) as arti on arti.art_id=arto.arto_id
left join (
 select * from art_group
) as artg on artg.artg_id=arti.artg_id
where
arto.art_id=?
SQL
			my $sth_arto = $dbh->prepare($sql_arto) or die $dbh->errstr;

			my $sql_arta =<<SQL;
select
 EXTRACT(EPOCH FROM art_entry) as art_entry,
 art_comment,
 art_category,
 art_judge,
 art_class
from
 art_annotation
where
 art_id=?
SQL
			my $sth_arta = $dbh->prepare($sql_arta) or die $dbh->errstr;


			my $sql_artg =<<SQL;
select artg_name from art_group where artg_id=?
SQL
			my $sth_artg = $dbh->prepare($sql_artg) or die $dbh->errstr;

			my $sql_cdi =<<SQL;
select 
 cdi_name,
 cdi_name_e,
 map.cdi_id,
 art_hist_serial,
 map.ci_id,
 map.cb_id,
 map.md_id,
 map.mv_id,
 map.mr_id
from
 (
   select * from concept_art_map
   where
     (art_id,art_hist_serial,ci_id,cb_id,md_id,mv_id,mr_id) in (
        select
         art_id,
         max(art_hist_serial) as art_hist_serial,
         ci_id,
         cb_id,
         md_id,
         mv_id,
         mr_id
        from
         concept_art_map
        where
        (art_id,ci_id,cb_id,md_id,mv_id,mr_id) in (
          select
           art_id,
           ci_id,
           cb_id,
           md_id,
           mv_id,
           max(mr_id) as mr_id
          from
           concept_art_map
          where
          (art_id,ci_id,cb_id,md_id,mv_id) in (
            select
             art_id,
             ci_id,
             cb_id,
             md_id,
             max(mv_id) as mv_id
            from
             concept_art_map
            where
             cm_delcause is null and
             art_id=? AND
             ci_id=$ci_id and
--             cb_id=$cb_id and
             md_id=$md_id and
             mv_id<=$mv_id
            group by
             art_id,
             ci_id,
             cb_id,
             md_id
            order by mv_id desc
            limit 1
          )
          group by
           art_id,
           ci_id,
           cb_id,
           md_id,
           mv_id
          order by mr_id desc
          limit 1
        )
        group by
         art_id,
         ci_id,
         cb_id,
         md_id,
         mv_id,
         mr_id
        order by art_hist_serial desc
        limit 1
      )
    order by cm_entry desc
    limit 1
 ) as map
left join (
   select * from concept_data_info
 ) as cdi on
    cdi.ci_id=map.ci_id and
    cdi.cdi_id=map.cdi_id
limit 1
SQL
			print $LOG __LINE__,qq|:\$sql_cdi=[$sql_cdi]\n|;
			my $sth_cdi = $dbh->prepare($sql_cdi) or die $dbh->errstr;

			my $sql_rep =<<SQL;
select
 rep.rep_id
 ,rep.mr_id,
 map.cm_use,
 map.cmp_id
from
(
 select * from concept_art_map
 where
  cm_use and
  cm_delcause is null and
  (art_id,ci_id,cb_id,md_id,mv_id,mr_id) in (
   select art_id,ci_id,cb_id,md_id,mv_id,max(mr_id) as mr_id from concept_art_map
   where
    art_id=? and
    ci_id=? and cb_id=? and md_id=? and mv_id=?
   group by
    art_id,ci_id,cb_id,md_id,mv_id
  )
) as map

left join (
   select
    *
   from
    representation
   where
    (ci_id,cb_id,md_id,mv_id,mr_id,bul_id,cdi_id) in (
     select
      ci_id,cb_id,md_id,mv_id,max(mr_id) as mr_id,bul_id,cdi_id
     from
      representation
     where
      bul_id=$bul_id
     group by
      ci_id,cb_id,md_id,mv_id,bul_id,cdi_id
   )
 ) as rep on
    rep.ci_id=map.ci_id and
    rep.cb_id=map.cb_id and
    rep.md_id=map.md_id and
    rep.mv_id=map.mv_id and
    rep.mr_id=map.mr_id and
    rep.cdi_id=map.cdi_id
SQL
			print $LOG __LINE__,qq|:\$sql_rep=[$sql_rep]\n|;
			my $sth_rep = $dbh->prepare($sql_rep) or die $dbh->errstr;

			my $sql_repa =<<SQL;
select
  repa.rep_id
from
  representation_art as repa
where
  repa.rep_id          = ? and
  repa.art_id          = ? and
  repa.art_hist_serial = ?
SQL
			print $LOG __LINE__,qq|:\$sql_repa=[$sql_repa]\n|;
			my $sth_repa = $dbh->prepare($sql_repa) or die $dbh->errstr;


			my $sql_cm =<<SQL;
select
 COALESCE(map.cm_use,false)
from
(
 select cm_use from concept_art_map
 where
  cm_delcause is null and
  (art_id,md_id,mv_id,mr_id) in (
   select art_id,md_id,mv_id,max(mr_id) as mr_id from concept_art_map
   where
    art_id=? and
    md_id=? and mv_id=?
   group by
    art_id,md_id,mv_id
  )
 order by cm_entry desc
 limit 1
) as map
SQL
			print $LOG __LINE__,qq|:\$sql_cm=[$sql_cm]\n|;
			my $sth_cm = $dbh->prepare($sql_cm) or die $dbh->errstr;







			my $sth_data = $dbh->prepare(qq|select art_data from history_art_file where art_id=? AND hist_serial=?|) or die $dbh->errstr;

#			($epocsec,$microsec) = &Time::HiRes::gettimeofday();
#			my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);
#			print $LOG sprintf("%04d:%04d/%02d/%02d %02d:%02d:%02d.%d\n",__LINE__,$year+1900,$mon+1,$mday,$hour,$min,$sec,$microsec);
			#$epocsec = &Time::HiRes::tv_interval($t0);
			#($sec,$min) = localtime($epocsec);
			&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

			my $sth = $dbh->prepare($sql) or die $dbh->errstr;
			$sth->execute() or die $dbh->errstr;
			$DATAS->{'total'} = $sth->rows();
	#		$sth->finish;
	#		undef $sth;

#			($epocsec,$microsec) = &Time::HiRes::gettimeofday();
#			my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);
#			print $LOG sprintf("%04d:%04d/%02d/%02d %02d:%02d:%02d.%d\n",__LINE__,$year+1900,$mon+1,$mday,$hour,$min,$sec,$microsec);
			#$epocsec = &Time::HiRes::tv_interval($t0);
			#($sec,$min) = localtime($epocsec);
			&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

			if($DATAS->{'total'}>0){
#				if(exists $FORM{'sort'} && defined $FORM{'sort'}){
#					my $SORT;
#					eval{$SORT = &cgi_lib::common::decodeJSON($FORM{'sort'});};
#					if(defined $SORT){
#						my @S = ();
#						foreach my $s (@$SORT){
#							next if($s->{'property'} eq 'selected');
#							push(@S,qq|$s->{property} $s->{direction}|);
#						}
#						$sql .= qq| ORDER BY |.join(",",@S);
#
#						$sth->finish() if(defined $sth);
#						undef $sth;
#					}
#				}

				my %SORT_KEYS;
				my $SORT;
				if(exists $FORM{'sort'} && defined $FORM{'sort'}){
					$SORT = &cgi_lib::common::decodeJSON($FORM{'sort'});
					%SORT_KEYS = map { $_->{'property'} => defined $_->{'direction'} ? uc($_->{'direction'}) : 'ASC' } @$SORT if(defined $SORT && ref $SORT eq 'ARRAY');
				}

				my %FILTER_KEYS;
				my $FILTER;
				if(exists $FORM{'filter'} && defined $FORM{'filter'}){
					$FILTER = &cgi_lib::common::decodeJSON($FORM{'filter'});
					%FILTER_KEYS = map { $_->{'property'} => $_->{'value'} } @$FILTER if(defined $FILTER && ref $FILTER eq 'ARRAY');
				}


#				if(exists $FORM{'limit'} && defined $FORM{'limit'} && $FORM{'limit'} =~ /^[0-9]+$/){
#					$sql .= qq| LIMIT $FORM{'limit'}|;
#
#					$sth->finish() if(defined $sth);
#					undef $sth;
#				}
#				if(exists $FORM{'start'} && defined $FORM{'start'} && $FORM{'start'} =~ /^[0-9]+$/){
#					$sql .= qq| OFFSET $FORM{'start'}|;
#
#					$sth->finish() if(defined $sth);
#					undef $sth;
#				}

				unless(defined $sth){
					print $LOG __LINE__,qq|:\$sql=[$sql]\n|;

#					($epocsec,$microsec) = &Time::HiRes::gettimeofday();
#					my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);
#					print $LOG sprintf("%04d:%04d/%02d/%02d %02d:%02d:%02d.%d\n",__LINE__,$year+1900,$mon+1,$mday,$hour,$min,$sec,$microsec);
					#$epocsec = &Time::HiRes::tv_interval($t0);
					#($sec,$min) = localtime($epocsec);
					&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

					$sth = $dbh->prepare($sql) or die $dbh->errstr;

#					($epocsec,$microsec) = &Time::HiRes::gettimeofday();
#					my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);
#					print $LOG sprintf("%04d:%04d/%02d/%02d %02d:%02d:%02d.%d\n",__LINE__,$year+1900,$mon+1,$mday,$hour,$min,$sec,$microsec);
					#$epocsec = &Time::HiRes::tv_interval($t0);
					#($sec,$min) = localtime($epocsec);
					&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

					$sth->execute() or die $dbh->errstr;

#					($epocsec,$microsec) = &Time::HiRes::gettimeofday();
#					my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);
#					print $LOG sprintf("%04d:%04d/%02d/%02d %02d:%02d:%02d.%d\n",__LINE__,$year+1900,$mon+1,$mday,$hour,$min,$sec,$microsec);
					#$epocsec = &Time::HiRes::tv_interval($t0);
					#($sec,$min) = localtime($epocsec);
					&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);
				}

				my $sth_art_file_info = $dbh->prepare(qq|select art_name,art_ext,art_group.artg_id,artg_name from art_file_info left join (select * from art_group) as art_group on (art_group.artg_id=art_file_info.artg_id) where art_file_info.art_id=?|) or die $dbh->errstr;

				my %ART2CDI;
				if(exists $SORT_KEYS{'cdi_name'} || exists $SORT_KEYS{'cdi_name_e'}){
					my $sth_all_art2cdi = $dbh->prepare(qq|
select
 art_id,cdi_id,cdi_name,cdi_name_e
from
 view_concept_art_map
where
 cm_delcause is null and
 (art_id,md_id,mv_id,mr_id) in (
  select art_id,md_id,mv_id,max(mr_id) as mr_id from concept_art_map
  where
   md_id=$md_id and mv_id=$mv_id
  group by
   art_id,md_id,mv_id
 )
|) or die $dbh->errstr;
					my $art_id;
					my $cdi_id;
					my $cdi_name;
					my $cdi_name_e;
					$sth_all_art2cdi->execute() or die $dbh->errstr;
					my $column_number = 0;
					$sth_all_art2cdi->bind_col(++$column_number, \$art_id, undef);
					$sth_all_art2cdi->bind_col(++$column_number, \$cdi_id, undef);
					$sth_all_art2cdi->bind_col(++$column_number, \$cdi_name, undef);
					$sth_all_art2cdi->bind_col(++$column_number, \$cdi_name_e, undef);
					while($sth_all_art2cdi->fetch){
						$ART2CDI{$art_id} = {
							cdi_id => $cdi_id,
							cdi_name => $cdi_name,
							cdi_name_e => $cdi_name_e,
						};
					}
					$sth_all_art2cdi->finish;
					undef $sth_all_art2cdi;
				}

				my %ART2REP;
				if(exists $SORT_KEYS{'rep_id'}){
					my %CDI2ART;
					my $sth_all_art2cdi = $dbh->prepare(qq|
select
 art_id,cdi_id
from
 concept_art_map
where
 cm_use and
 cm_delcause is null and
 (art_id,md_id,mv_id,mr_id) in (
  select art_id,md_id,mv_id,max(mr_id) as mr_id from concept_art_map
  where
   md_id=$md_id and
   mv_id=$mv_id and
   mr_id<=$mr_id
  group by
   art_id,md_id,mv_id
 )
|) or die $dbh->errstr;
					my $art_id;
					my $cdi_id;
					my $cdi_name;
					my $cdi_name_e;
					$sth_all_art2cdi->execute() or die $dbh->errstr;
					my $column_number = 0;
					$sth_all_art2cdi->bind_col(++$column_number, \$art_id, undef);
					$sth_all_art2cdi->bind_col(++$column_number, \$cdi_id, undef);
					while($sth_all_art2cdi->fetch){
						$CDI2ART{$cdi_id} = $art_id;
					}
					$sth_all_art2cdi->finish;
					undef $sth_all_art2cdi;

					my $sql_all_cdi2rep = sprintf(qq|
select
  rep_id,
  cdi_id
from
  representation
where
  rep_delcause is null and
  (cdi_id,md_id,mv_id,mr_id,bul_id) in (
   select cdi_id,md_id,mv_id,max(mr_id) as mr_id,bul_id from representation
   where
    md_id=$md_id and
    mv_id=$mv_id and
    mr_id<=$mr_id and
    bul_id=$bul_id and
    cdi_id in (%s)
   group by
    cdi_id,md_id,mv_id,bul_id
  )
|,join(',',sort keys(%CDI2ART)));

					my $sth_all_cdi2rep = $dbh->prepare($sql) or die $dbh->errstr;

					my $rep_id;
#					my $cdi_id;
					$sth_all_cdi2rep->execute() or die $dbh->errstr;
					$column_number = 0;
					$sth_all_cdi2rep->bind_col(++$column_number, \$rep_id, undef);
					$sth_all_cdi2rep->bind_col(++$column_number, \$cdi_id, undef);
					while($sth_all_cdi2rep->fetch){
						next unless(exists $CDI2ART{$cdi_id});
						$ART2REP{$CDI2ART{$cdi_id}} = $rep_id;
					}
					$sth_all_cdi2rep->finish;
					undef $sth_all_cdi2rep;


					undef %CDI2ART;
				}



				my $column_number = 0;
				my $art_id;
				my $art_hist_serial;
#				my $art_thumb;
				my $art_name;
				my $art_ext;
				my $art_timestamp;
				my $art_modified;
				my $art_md5;
				my $arti_entry;

#				my $art_data;
				my $art_data_size;

				my $art_xmin;
				my $art_xmax;
				my $art_ymin;
				my $art_ymax;
				my $art_zmin;
				my $art_zmax;

				my $art_xcenter;
				my $art_ycenter;
				my $art_zcenter;

				my $art_volume;
				my $art_cube_volume;
				my $art_comment;
				my $art_mirroring;
				my $art_category;
				my $art_judge;
				my $art_class;
				my $artg_id;
				my $artg_name;

				my $arto_id;
				my $arto_comment;
				my $arto_name;
				my $arto_ext;
				my $artog_id;
				my $artog_name;


				$sth->bind_col(++$column_number, \$art_id, undef);
				$sth->bind_col(++$column_number, \$art_hist_serial, undef);
				$sth->bind_col(++$column_number, \$art_name, undef);
				$sth->bind_col(++$column_number, \$art_ext, undef);
				$sth->bind_col(++$column_number, \$art_mirroring, undef);
				$sth->bind_col(++$column_number, \$artg_id, undef);
				$sth->bind_col(++$column_number, \$artg_name, undef);
				$sth->bind_col(++$column_number, \$arti_entry, undef);
=pod
				$sth->bind_col(++$column_number, \$art_modified, undef);

				$sth->bind_col(++$column_number, \$art_md5, undef);

				$sth->bind_col(++$column_number, \$art_data_size, undef);

				$sth->bind_col(++$column_number, \$art_xmin, undef);
				$sth->bind_col(++$column_number, \$art_xmax, undef);
				$sth->bind_col(++$column_number, \$art_ymin, undef);
				$sth->bind_col(++$column_number, \$art_ymax, undef);
				$sth->bind_col(++$column_number, \$art_zmin, undef);
				$sth->bind_col(++$column_number, \$art_zmax, undef);

				$sth->bind_col(++$column_number, \$art_xcenter, undef);
				$sth->bind_col(++$column_number, \$art_ycenter, undef);
				$sth->bind_col(++$column_number, \$art_zcenter, undef);

				$sth->bind_col(++$column_number, \$art_volume, undef);
				$sth->bind_col(++$column_number, \$art_cube_volume, undef);

				$sth->bind_col(++$column_number, \$art_comment, undef);
				$sth->bind_col(++$column_number, \$art_category, undef);
				$sth->bind_col(++$column_number, \$art_judge, undef);
				$sth->bind_col(++$column_number, \$art_class, undef);

				$sth->bind_col(++$column_number, \$artg_name, undef);

				$sth->bind_col(++$column_number, \$arto_id, undef);
				$sth->bind_col(++$column_number, \$arto_comment, undef);
				$sth->bind_col(++$column_number, \$arto_name, undef);
				$sth->bind_col(++$column_number, \$arto_ext, undef);
				$sth->bind_col(++$column_number, \$artog_id, undef);
				$sth->bind_col(++$column_number, \$artog_name, undef);
=cut


				while($sth->fetch){
		#					my $path = File::Spec->catdir($BITS::Config::UPLOAD_PATH,$artg_name);
		#			my $group_path = File::Spec->catdir($FindBin::Bin,'art_file',$artg_name);
					my $group_abs_path = File::Spec->catdir($FindBin::Bin,'art_file');
					my $group_rel_path = File::Spec->abs2rel($group_abs_path,$FindBin::Bin);

		#print $LOG __LINE__,":\$path=[$path]\n";
		#print $LOG __LINE__,":\$path=[$path]\n";
					unless(-e $group_abs_path){
						umask(0);
						&File::Path::mkpath($group_abs_path,{mode=>0777});
					}
					my $file_name = $art_name;
					$file_name .= $art_ext unless($art_name =~ /$art_ext$/);

		#					$path = File::Spec->catfile($path,$file_name);
	#				$path = File::Spec->catfile($path,qq|$art_id$art_ext|);
					my $file_path = File::Spec->catfile($group_abs_path,qq|$art_id-$art_hist_serial$art_ext|);

		#print $LOG __LINE__,":\$path=[$path]\n";

					my $path = &File::Basename::basename($file_path);


					my $art_timestamp;
					my $art_md5;
					my $art_data_size;
					my $art_xmin;
					my $art_xmax;
					my $art_ymin;
					my $art_ymax;
					my $art_zmin;
					my $art_zmax;
					my $art_xcenter;
					my $art_ycenter;
					my $art_zcenter;
					my $art_volume;
					my $art_cube_volume;
					if(
						!-e $file_path ||
						(exists $FORM{'art_datas'} && defined $FORM{'art_datas'})
						|| exists $SORT_KEYS{'mtime'}
#						|| exists $SORT_KEYS{'art_md5'}
#						|| exists $SORT_KEYS{'art_data_size'}
#						|| exists $SORT_KEYS{'art_xmin'}
#						|| exists $SORT_KEYS{'art_xmax'}
#						|| exists $SORT_KEYS{'art_ymin'}
#						|| exists $SORT_KEYS{'art_ymax'}
#						|| exists $SORT_KEYS{'art_zmin'}
#						|| exists $SORT_KEYS{'art_zmax'}
#						|| exists $SORT_KEYS{'art_xcenter'}
#						|| exists $SORT_KEYS{'art_ycenter'}
#						|| exists $SORT_KEYS{'art_zcenter'}
#						|| exists $SORT_KEYS{'art_volume'}
#						|| exists $SORT_KEYS{'art_cube_volume'}
						|| exists $SORT_KEYS{'xmin'}
						|| exists $SORT_KEYS{'xmax'}
						|| exists $SORT_KEYS{'ymin'}
						|| exists $SORT_KEYS{'ymax'}
						|| exists $SORT_KEYS{'zmin'}
						|| exists $SORT_KEYS{'zmax'}
						|| exists $SORT_KEYS{'xcenter'}
						|| exists $SORT_KEYS{'ycenter'}
						|| exists $SORT_KEYS{'zcenter'}
						|| exists $SORT_KEYS{'volume'}
						|| exists $SORT_KEYS{'art_data_size'}
					){
						$sth_art->execute($art_id) or die $dbh->errstr;
						$column_number = 0;
						$sth_art->bind_col(++$column_number, \$art_timestamp, undef);
						$sth_art->bind_col(++$column_number, \$art_md5, undef);
						$sth_art->bind_col(++$column_number, \$art_data_size, undef);
						$sth_art->bind_col(++$column_number, \$art_xmin, undef);
						$sth_art->bind_col(++$column_number, \$art_xmax, undef);
						$sth_art->bind_col(++$column_number, \$art_ymin, undef);
						$sth_art->bind_col(++$column_number, \$art_ymax, undef);
						$sth_art->bind_col(++$column_number, \$art_zmin, undef);
						$sth_art->bind_col(++$column_number, \$art_zmax, undef);
						$sth_art->bind_col(++$column_number, \$art_xcenter, undef);
						$sth_art->bind_col(++$column_number, \$art_ycenter, undef);
						$sth_art->bind_col(++$column_number, \$art_zcenter, undef);
						$sth_art->bind_col(++$column_number, \$art_volume, undef);
						$sth_art->bind_col(++$column_number, \$art_cube_volume, undef);
						$sth_art->fetch;
						$sth_art->finish;
					}

					if(defined $art_data_size && defined $art_timestamp){
						my($s,$t) = (stat($file_path))[7,9] if(-e $file_path);
						unless($s==$art_data_size && $t==$art_timestamp){
							print $LOG __LINE__,":\$file_path=[$file_path]\n";
							my $art_data;
#							my $sth_data = $dbh->prepare(qq|select art_data from history_art_file where art_id=? AND hist_serial=?|) or die $dbh->errstr;
							$sth_data->execute($art_id,$art_hist_serial) or die $dbh->errstr;
							$sth_data->bind_col(1, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
							$sth_data->fetch;
							$sth_data->finish;
#							undef $sth_data;

							if(defined $art_data && open(OBJ,"> $file_path")){
								flock(OBJ,2);
								binmode(OBJ);
								print OBJ $art_data;
								close(OBJ);
								utime $art_timestamp,$art_timestamp,$file_path;
							}
							undef $art_data;
						}
					}


					my $arta_entry;
					my $art_comment;
					my $art_mirroring;
					my $art_category;
					my $art_judge;
					my $art_class;
					if(
						(exists $FORM{'art_datas'} && defined $FORM{'art_datas'})
						|| exists $SORT_KEYS{'mtime'}
						|| exists $SORT_KEYS{'art_comment'}
						|| exists $SORT_KEYS{'art_category'}
						|| exists $SORT_KEYS{'art_judge'}
						|| exists $SORT_KEYS{'art_class'}
					){
						$sth_arta->execute($art_id) or die $dbh->errstr;
						$column_number = 0;
						$sth_arta->bind_col(++$column_number, \$arta_entry, undef);
						$sth_arta->bind_col(++$column_number, \$art_comment, undef);
						$sth_arta->bind_col(++$column_number, \$art_category, undef);
						$sth_arta->bind_col(++$column_number, \$art_judge, undef);
						$sth_arta->bind_col(++$column_number, \$art_class, undef);
						$sth_arta->fetch;
						$sth_arta->finish;
					}

					my $arto_entry;
					my $arto_id;
					my $arto_comment;
					my $arto_name;
					my $arto_ext;
					my $artog_id;
					my $artog_name;
					if(
						(exists $FORM{'art_datas'} && defined $FORM{'art_datas'})
						|| exists $SORT_KEYS{'mtime'}
						|| exists $SORT_KEYS{'arto_comment'}
						|| exists $SORT_KEYS{'arto_name'}
						|| exists $SORT_KEYS{'arto_ext'}
						|| exists $SORT_KEYS{'artog_id'}
						|| exists $SORT_KEYS{'artog_name'}
					){
						$sth_arto->execute($art_id) or die $dbh->errstr;
						$column_number = 0;
						$sth_arto->bind_col(++$column_number, \$arto_entry, undef);
						$sth_arto->bind_col(++$column_number, \$arto_id, undef);
						$sth_arto->bind_col(++$column_number, \$arto_comment, undef);
						$sth_arto->bind_col(++$column_number, \$arto_name, undef);
						$sth_arto->bind_col(++$column_number, \$arto_ext, undef);
						$sth_arto->bind_col(++$column_number, \$artog_id, undef);
						$sth_arto->bind_col(++$column_number, \$artog_name, undef);
						$sth_arto->fetch;
						$sth_arto->finish;
					}

#					my $artg_name;
#					$sth_artg->execute($artg_id) or die $dbh->errstr;
#					$column_number = 0;
#					$sth_artg->bind_col(++$column_number, \$artg_name, undef);
#					$sth_artg->fetch;
#					$sth_artg->finish;

					my @max_timestamp;
					push(@max_timestamp, $arti_entry) if(defined $arti_entry);
					push(@max_timestamp, $art_timestamp) if(defined $art_timestamp);
					push(@max_timestamp, $arta_entry) if(defined $arta_entry);
					push(@max_timestamp, $arto_entry) if(defined $arto_entry);
					my $art_modified = &List::Util::max(@max_timestamp);
#=cut

					my $cdi_name;
					my $cdi_name_e;
					my $rep_id;
					my $mr_id;
					my $cm_use;
					my $cmp_id;
					my $use_rep_id;

					if(
						(exists $FORM{'art_datas'} && defined $FORM{'art_datas'})
#						|| exists $SORT_KEYS{'cdi_name'}
#						|| exists $SORT_KEYS{'cdi_name_e'}
#						|| exists $SORT_KEYS{'rep_id'}
					){
						my $cm_cdi_id;
						my $cm_art_hist_serial;
						my $cm_ci_id;
						my $cm_cb_id;
						my $cm_md_id;
						my $cm_mv_id;
						my $cm_mr_id;
						$sth_cdi->execute($art_id) or die $dbh->errstr;
						$column_number = 0;
						$sth_cdi->bind_col(++$column_number, \$cdi_name, undef);
						$sth_cdi->bind_col(++$column_number, \$cdi_name_e, undef);
						$sth_cdi->bind_col(++$column_number, \$cm_cdi_id, undef);
						$sth_cdi->bind_col(++$column_number, \$cm_art_hist_serial, undef);
						$sth_cdi->bind_col(++$column_number, \$cm_ci_id, undef);
						$sth_cdi->bind_col(++$column_number, \$cm_cb_id, undef);
						$sth_cdi->bind_col(++$column_number, \$cm_md_id, undef);
						$sth_cdi->bind_col(++$column_number, \$cm_mv_id, undef);
						$sth_cdi->bind_col(++$column_number, \$cm_mr_id, undef);
#						$sth_cdi->bind_col(++$column_number, \$cm_use, undef);
						$sth_cdi->fetch;
						$sth_cdi->finish;

#						$sth_rep->execute($art_id,$cm_ci_id,$cm_cb_id,$cm_md_id,$cm_mv_id,$cm_mr_id) or die $dbh->errstr;
						$sth_rep->execute($art_id,$ci_id,$cb_id,$md_id,$mv_id) or die $dbh->errstr;
						$column_number = 0;
						$sth_rep->bind_col(++$column_number, \$rep_id, undef);
						$sth_rep->bind_col(++$column_number, \$mr_id, undef);
						$sth_rep->bind_col(++$column_number, \$cm_use, undef);
						$sth_rep->bind_col(++$column_number, \$cmp_id, undef);
						$sth_rep->fetch;
						$sth_rep->finish;

						$sth_repa->execute($rep_id,$art_id,$cm_art_hist_serial) or die $dbh->errstr;
						$column_number = 0;
						$sth_repa->bind_col(++$column_number, \$use_rep_id, undef);
						$sth_repa->fetch;
						$sth_repa->finish;

#						print $LOG __LINE__,qq|:\$art_id=[$art_id]\n|;
#						print $LOG __LINE__,qq|:\$art_hist_serial=[$art_hist_serial]\n|;
#						print $LOG __LINE__,qq|:\$cdi_name=[$cdi_name]\n|;
#						print $LOG __LINE__,qq|:\$cdi_name_e=[$cdi_name_e]\n|;
#						print $LOG __LINE__,qq|:\$rep_id=[$rep_id]\n|;
#						print $LOG __LINE__,qq|:\$mr_id=[$mr_id]\n|;
#						print $LOG __LINE__,qq|:\$cm_use=[$cm_use]\n|;
#						print $LOG __LINE__,qq|:\$use_rep_id=[$use_rep_id]\n|;
					}
					elsif(exists $FILTER_KEYS{'cm_use'}){
						$sth_cm->execute($art_id,$md_id,$mv_id) or die $dbh->errstr;
						$column_number = 0;
						$sth_cm->bind_col(++$column_number, \$cm_use, undef);
						$sth_cm->fetch;
						$sth_cm->finish;
					}

					if(exists $FILTER_KEYS{'cm_use'}){
						next unless(defined $cm_use && $cm_use == JSON::XS::true);
					}


					if(defined $rep_id && defined $use_rep_id){
						unless($rep_id eq $use_rep_id){
							$rep_id = undef;
							$use_rep_id = undef;
						}
					}elsif(defined $rep_id){
						$rep_id = undef;
						$use_rep_id = undef;
					}

					my $selected = JSON::XS::false;
					if(defined $selected_art_ids && exists $selected_art_ids->{$artg_id} && defined $selected_art_ids->{$artg_id} && exists  $selected_art_ids->{$artg_id}->{$art_id}){
						$selected = JSON::XS::true;
					}

					my $arto_filename;
					if(defined $arto_id && $arto_id =~ /[^A-Za-z0-9]/){
						my @arto_ids = split(/[^A-Za-z0-9]+/,$arto_id);
						my @artog_ids;
						my @artog_names;
						my @arto_filenames;

#						my $sth_art_file_info = $dbh->prepare(qq|select art_name,art_ext,art_group.artg_id,artg_name from art_file_info left join (select * from art_group) as art_group on (art_group.artg_id=art_file_info.artg_id) where art_file_info.art_id=?|) or die $dbh->errstr;
						foreach my $temp_art_id (@arto_ids){
							$sth_art_file_info->execute($temp_art_id) or die $dbh->errstr;
							my $temp_art_name;
							my $temp_art_ext;
							my $temp_artg_id;
							my $temp_artg_name;
							$sth_art_file_info->bind_col(1, \$temp_art_name, undef);
							$sth_art_file_info->bind_col(2, \$temp_art_ext, undef);
							$sth_art_file_info->bind_col(3, \$temp_artg_id, undef);
							$sth_art_file_info->bind_col(4, \$temp_artg_name, undef);
							while($sth_art_file_info->fetch){
								push(@artog_ids,$temp_artg_id);
								push(@artog_names,$temp_artg_name);
								push(@arto_filenames,qq|$temp_art_name$temp_art_ext|);
							}
							$sth_art_file_info->finish;
						}
#						undef $sth_art_file_info;

						my $joinChar = '+';
						$arto_id = join($joinChar,@arto_ids);
						$artog_id = join($joinChar,@artog_ids);
						$artog_name = join($joinChar,@artog_names);
						$arto_filename = join($joinChar,@arto_filenames);
					}


					push(@{$DATAS->{'datas'}},{

						#Old I/O
						name  => $file_name,
						group => $artg_name,
						grouppath => $group_rel_path,
						path  => $path,
						mtime => defined $art_modified ? $art_modified + 0 : undef,

						xmin   => defined $art_xmin ? $art_xmin + 0 : undef,
						xmax   => defined $art_xmax ? $art_xmax + 0 : undef,
						ymin   => defined $art_ymin ? $art_ymin + 0 : undef,
						ymax   => defined $art_ymax ? $art_ymax + 0 : undef,
						zmin   => defined $art_zmin ? $art_zmin + 0 : undef,
						zmax   => defined $art_zmax ? $art_zmax + 0 : undef,
						volume => defined $art_volume ? $art_volume + 0 : undef,

						xcenter => defined $art_xcenter ? $art_xcenter + 0 : undef,
						ycenter => defined $art_ycenter ? $art_ycenter + 0 : undef,
						zcenter => defined $art_zcenter ? $art_zcenter + 0 : undef,

						selected => $selected,

						#New I/O
						art_id          => $art_id,
						art_hist_serial => defined $art_hist_serial ? $art_hist_serial + 0 : undef,
#						art_thumb       => $art_thumb,
						art_thumb       => undef,
						art_name        => $art_name,
						art_timestamp   => defined $art_timestamp ? $art_timestamp + 0 : undef,
						art_modified    => defined $art_modified ? $art_modified + 0 : undef,
						art_data_size   => defined $art_data_size ? $art_data_size + 0 : undef,

						art_xmin       => defined $art_xmin ? $art_xmin + 0 : undef,
						art_xmax       => defined $art_xmax ? $art_xmax + 0 : undef,
						art_ymin       => defined $art_ymin ? $art_ymin + 0 : undef,
						art_ymax       => defined $art_ymax ? $art_ymax + 0 : undef,
						art_zmin       => defined $art_zmin ? $art_zmin + 0 : undef,
						art_zmax       => defined $art_zmax ? $art_zmax + 0 : undef,

						art_xcenter    => defined $art_xcenter ? $art_xcenter + 0 : undef,
						art_ycenter    => defined $art_ycenter ? $art_ycenter + 0 : undef,
						art_zcenter    => defined $art_zcenter ? $art_zcenter + 0 : undef,

						art_volume     => defined $art_volume ? $art_volume + 0 : undef,
						art_comment    => $art_comment,
						art_mirroring  => $art_mirroring ? JSON::XS::true : JSON::XS::false,,
						art_category   => $art_category,
						art_judge      => $art_judge,
						art_class      => $art_class,

						artg_id        => defined $artg_id ? $artg_id + 0 : undef,
						artg_name      => $artg_name,

						arto_id        => $arto_id,
						arto_comment   => $arto_comment,
	#					arto_name      => $arto_name,
	#					arto_ext       => $arto_ext,
						artog_id       => defined $artog_id ? $artog_id + 0 : undef,
						artog_name     => $artog_name,
						arto_filename  => defined $arto_filename ? $arto_filename : (defined $arto_name && defined $arto_ext ? qq|$arto_name$arto_ext| : undef),

						cdi_name       => $cdi_name,
						cdi_name_e     => $cdi_name_e,
						rep_id         => $rep_id,
						use_rep_id     => $use_rep_id,

						md_id          => $md_id + 0,
						md_abbr        => $md_abbr,
						mv_id          => $mv_id + 0,
						mv_name_e      => $mv_name_e,

						mr_id          => defined $mr_id ? $mr_id + 0 : undef,
						bul_id         => $bul_id + 0,
						bul_abbr       => $bul_abbr,

#						cm_use         => defined $cm_use ? ($cm_use ? JSON::XS::true : JSON::XS::false) : undef,
						cm_use         => ($cm_use ? JSON::XS::true : JSON::XS::false),

						cmp_id         => (defined $cmp_id ? $cmp_id-0 : 0),

						filename       => $file_name,

#						diff_volume        => $diff_volume,
#						diff_cube_volume   => $diff_cube_volume,
#						distance_xyz       => $distance_xyz,
#						distance_voxel     => $distance_voxel,
#						collision_rate     => $collision_rate,
#						collision_rate_obj => $collision_rate_obj

					});

					#$epocsec = &Time::HiRes::tv_interval($t0);
					#($sec,$min) = localtime($epocsec);
					&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

				}
				$sth->finish;
				undef $sth;

#				($epocsec,$microsec) = &Time::HiRes::gettimeofday();
#				my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);
#				print $LOG sprintf("%04d:%04d/%02d/%02d %02d:%02d:%02d.%d\n",__LINE__,$year+1900,$mon+1,$mday,$hour,$min,$sec,$microsec);
				#$epocsec = &Time::HiRes::tv_interval($t0);
				#($sec,$min) = localtime($epocsec);
				&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);


				$DATAS->{'total'} = scalar @{$DATAS->{'datas'}};
#=pod
				if($DATAS->{'total'}>0 && defined $SORT && ref $SORT eq 'ARRAY'){
					foreach my $s (reverse @$SORT){
						if($s->{'direction'} eq 'ASC'){
							if(
								$s->{'property'} eq 'artg_name' ||
								$s->{'property'} eq 'group' ||
								$s->{'property'} eq 'art_name' ||
								$s->{'property'} eq 'name' ||
								$s->{'property'} eq 'art_id' ||
								$s->{'property'} eq 'filename' ||
								$s->{'property'} eq 'art_category' ||
								$s->{'property'} eq 'art_class'    ||
								$s->{'property'} eq 'art_comment'  ||
								$s->{'property'} eq 'art_judge'    ||
								$s->{'property'} eq 'arto_comment' ||
								$s->{'property'} eq 'arto_name'    ||
								$s->{'property'} eq 'arto_ext'     ||
								$s->{'property'} eq 'artog_id'     ||
								$s->{'property'} eq 'artog_name'
							){
								@{$DATAS->{'datas'}} = sort { $a->{$s->{'property'}} cmp $b->{$s->{'property'}} }@{$DATAS->{'datas'}};
							}
							elsif(
								$s->{'property'} eq 'cdi_name' ||
								$s->{'property'} eq 'cdi_name_e'
							){
								@{$DATAS->{'datas'}} = sort { $ART2CDI{$a->{'art_id'}}->{$s->{'property'}} cmp $ART2CDI{$b->{'art_id'}}->{$s->{'property'}} }@{$DATAS->{'datas'}};
							}
							elsif(
								$s->{'property'} eq 'rep_id'
							){
								@{$DATAS->{'datas'}} = sort { $ART2REP{$a->{'art_id'}} cmp $ART2REP{$b->{'art_id'}} }@{$DATAS->{'datas'}};
							}
							else{
								@{$DATAS->{'datas'}} = sort { $a->{$s->{'property'}} <=> $b->{$s->{'property'}} }@{$DATAS->{'datas'}};
							}
						}
						else{
							if(
								$s->{'property'} eq 'artg_name' ||
								$s->{'property'} eq 'group' ||
								$s->{'property'} eq 'art_name' ||
								$s->{'property'} eq 'name' ||
								$s->{'property'} eq 'art_id' ||
								$s->{'property'} eq 'filename' ||
								$s->{'property'} eq 'art_category' ||
								$s->{'property'} eq 'art_class'    ||
								$s->{'property'} eq 'art_comment'  ||
								$s->{'property'} eq 'art_judge'    ||
								$s->{'property'} eq 'arto_comment' ||
								$s->{'property'} eq 'arto_name'    ||
								$s->{'property'} eq 'arto_ext'     ||
								$s->{'property'} eq 'artog_id'     ||
								$s->{'property'} eq 'artog_name'
							){
								@{$DATAS->{'datas'}} = sort { $b->{$s->{'property'}} cmp $a->{$s->{'property'}} }@{$DATAS->{'datas'}};
							}
							elsif(
								$s->{'property'} eq 'cdi_name' ||
								$s->{'property'} eq 'cdi_name_e'
							){
								@{$DATAS->{'datas'}} = sort { $ART2CDI{$b->{'art_id'}}->{$s->{'property'}} cmp $ART2CDI{$a->{'art_id'}}->{$s->{'property'}} }@{$DATAS->{'datas'}};
							}
							elsif(
								$s->{'property'} eq 'rep_id'
							){
								@{$DATAS->{'datas'}} = sort { $ART2REP{$b->{'art_id'}} cmp $ART2REP{$a->{'art_id'}} }@{$DATAS->{'datas'}};
							}
							else{
								@{$DATAS->{'datas'}} = sort { $b->{$s->{'property'}} <=> $a->{$s->{'property'}} }@{$DATAS->{'datas'}};
							}
						}
					}
				}
#=cut
			}

			$sth->finish() if(defined $sth);
			undef $sth;
		}

		$DATAS->{'success'} = JSON::XS::true;
	};
	if($@){
		$DATAS->{'success'} = JSON::XS::false;
		$DATAS->{'total'} = 0;
		$DATAS->{'msg'} = $@;
		&utf8::decode($DATAS->{'msg'}) unless(&Encode::is_utf8($DATAS->{'msg'}));
	}

}elsif($FORM{'cmd'} eq 'update'){
	&cgi_lib::common::message($FORM{'cmd'}, $LOG) if(defined $LOG);

=pod
43:$FORM{art_category}=[hepatic artery]
43:$FORM{art_class}=[1]
43:$FORM{art_comment}=[morphology checked OK]
43:$FORM{art_ids}=[["FJ2386"]]
43:$FORM{art_judge}=[]
43:$FORM{cdi_name}=[FMA70447]
43:$FORM{cmd}=[update]
43:$FORM{fieldset-1394-checkbox}=[on]
43:$FORM{'mirror_same_concept'}=[on]

43:$FORM{art_category}=[hepatic artery]
43:$FORM{art_class}=[1]
43:$FORM{art_comment}=[morphology checked OK]
43:$FORM{art_ids}=[["FJ2386"]]
43:$FORM{art_judge}=[]
43:$FORM{cb_id}=[4]
43:$FORM{cdi_name}=[FMA70447]
43:$FORM{ci_id}=[1]
43:$FORM{cmd}=[update]
43:$FORM{'mirror'}=[on]
43:$FORM{mirror_cdi_name}=[FMA70455]
=cut

	my $art_ids = &cgi_lib::common::decodeJSON($FORM{'art_ids'});
	if(defined $art_ids && ref $art_ids eq 'ARRAY'){
		$dbh->{'AutoCommit'} = 0;
		$dbh->{'RaiseError'} = 1;
		eval{

			my $sth_model_version = $dbh->prepare(qq|select mv_publish,mv_frozen from model_version where md_id=? AND mv_id=?|) or die $dbh->errstr;
			$sth_model_version->execute($FORM{'md_id'},$FORM{'mv_id'}) or die $dbh->errstr;
			my $column_number = 0;
			my $mv_publish;
			my $mv_frozen;
			$sth_model_version->bind_col(++$column_number, \$mv_publish, undef);
			$sth_model_version->bind_col(++$column_number, \$mv_frozen, undef);
			$sth_model_version->fetch;
			$sth_model_version->finish;
			undef $sth_model_version;
#			die &Encode::decode_utf8('公開中の為、編集できません') if($mv_publish);
#			die &Encode::decode_utf8('編集不可の為、編集できません') if($mv_frozen);

#			die "error!!";
			my $cdi_id;
			if(exists $FORM{'cdi_name'}){
				my $sth_cdi_sel = $dbh->prepare(qq|select cdi_id from concept_data_info where ci_id=? AND cdi_name=?|) or die $dbh->errstr;
				$sth_cdi_sel->execute($FORM{'ci_id'},$FORM{'cdi_name'}) or die $dbh->errstr;
				my $column_number = 0;
				$sth_cdi_sel->bind_col(++$column_number, \$cdi_id, undef);
				$sth_cdi_sel->fetch;
				$sth_cdi_sel->finish;
				undef $sth_cdi_sel;
			}

			my $openid = qq|system|;

			my $sql =<<SQL;
select
 arti.artg_id,
 artg_name,
 prefix_id,
 art_serial,
 arti.art_name,
 arti.art_ext,
 arti.art_timestamp
from
 art_file as art
left join (
 select * from art_file_info
) as arti on
   arti.art_id=art.art_id
left join (
 select * from art_group
) as artg on
   artg.artg_id=arti.artg_id
where art.art_id=?
SQL
			my $sth_art_sel = $dbh->prepare($sql) or die $dbh->errstr;

			$sql =<<SQL;
insert into art_file (
  md_id,
  mv_id,
  mr_id,
  artg_id,
  prefix_id,
  art_id,
  art_serial,
  art_name,
  art_ext,
  art_timestamp,
  art_md5,
  art_data,
  art_data_size,
  art_decimate,
  art_decimate_size,
  art_xmin,
  art_xmax,
  art_ymin,
  art_ymax,
  art_zmin,
  art_zmax,
  art_volume,
  art_cube_volume,
  art_mirroring,
  art_openid
) values (
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  'true',
  '$openid'
)
;
SQL
			my $sth_art_mirror_ins = $dbh->prepare($sql) or die $dbh->errstr;

			$sql =<<SQL;
insert into art_file_info (
  artg_id,
  art_id,
  art_name,
  art_ext,
  art_timestamp,
  art_mirroring,
  art_openid
) values (
  ?,
  ?,
  ?,
  ?,
  ?,
  'true',
  '$openid'
)
;
SQL
			my $sth_arti_mirror_ins = $dbh->prepare($sql) or die $dbh->errstr;

			my $sth_arta_sel = $dbh->prepare(qq|select art_comment,art_category,art_judge,art_class from art_annotation where art_id=?|) or die $dbh->errstr;
			my $sth_arta_upd = $dbh->prepare(qq|update art_annotation set art_comment=?,art_category=?,art_judge=?,art_class=?,art_entry=now() where art_id=?|) or die $dbh->errstr;
			my $sth_arta_ins = $dbh->prepare(qq|insert into art_annotation (art_comment,art_category,art_judge,art_class,art_id,art_entry,art_openid) values (?,?,?,?,?,now(),'$openid')|) or die $dbh->errstr;

			my $sth_map_sel = $dbh->prepare(qq|select cdi_id,cm_comment,cm_use from concept_art_map where art_id=? and ci_id=? and cb_id=? and md_id=? and mv_id=? and mr_id=?|) or die $dbh->errstr;
#			my $sth_map_sel = $dbh->prepare(qq|select cdi_id,cm_comment,cm_use,cmp_id from concept_art_map where art_id=? and ci_id=? and cb_id=? and md_id=? and mv_id=? and mr_id=?|) or die $dbh->errstr;
			my $sth_map_upd = $dbh->prepare(qq|update concept_art_map set cdi_id=?,cm_comment=?,cm_use=?,cm_entry=now() where art_id=? and ci_id=? and cb_id=? and md_id=? and mv_id=? and mr_id=?|) or die $dbh->errstr;
#			my $sth_map_upd = $dbh->prepare(qq|update concept_art_map set cdi_id=?,cm_comment=?,cm_use=?,cmp_id=?,cm_entry=now() where art_id=? and ci_id=? and cb_id=? and md_id=? and mv_id=? and mr_id=?|) or die $dbh->errstr;
			my $sth_map_ins = $dbh->prepare(qq|insert into concept_art_map (cdi_id,cm_comment,cm_use,art_id,ci_id,cb_id,md_id,mv_id,mr_id,cm_entry,cm_openid) values (?,?,?,?,?,?,?,?,?,now(),'$openid')|) or die $dbh->errstr;
#			my $sth_map_ins = $dbh->prepare(qq|insert into concept_art_map (cdi_id,cm_comment,cm_use,cmp_id,art_id,ci_id,cb_id,md_id,mv_id,mr_id,cm_entry,cm_openid) values (?,?,?,?,?,?,?,?,?,?,now(),'$openid')|) or die $dbh->errstr;
			my $sth_map_del = $dbh->prepare(qq|delete from concept_art_map where art_id=? and ci_id=? and cb_id=? and md_id=? and mv_id=? and mr_id=? RETURNING cm_entry|) or die $dbh->errstr;

			my $sth_hmap_upd = $dbh->prepare(qq|update history_concept_art_map set cm_comment=? where art_id=? and ci_id=? and cb_id=? and md_id=? and mv_id=? and mr_id=? and cm_entry=? and hist_event=(select he_id from history_event where he_name='DELETE')|) or die $dbh->errstr;

			my $sth_map_upd_set_mirror = $dbh->prepare(qq|update concept_art_map set cm_use=?,cm_entry=now() where art_id=? and ci_id=? and cb_id=? and md_id=? and mv_id=? and mr_id=? and cm_use<>?|) or die $dbh->errstr;

			foreach my $art_id (@$art_ids){
				$sth_arta_sel->execute($art_id) or die $dbh->errstr;
				my $rows = $sth_arta_sel->rows();
				my($art_comment,$art_category,$art_judge,$art_class);
				if($rows>0){
					my $column_number = 0;
					$sth_arta_sel->bind_col(++$column_number, \$art_comment, undef);
					$sth_arta_sel->bind_col(++$column_number, \$art_category, undef);
					$sth_arta_sel->bind_col(++$column_number, \$art_judge, undef);
					$sth_arta_sel->bind_col(++$column_number, \$art_class, undef);
					$sth_arta_sel->fetch;
				}
				$sth_arta_sel->finish;
				print $LOG __LINE__,qq|:\$rows=[$rows]\n|;
#				next unless($rows>0);
				unless(
					$FORM{'art_comment'} eq $art_comment &&
					$FORM{'art_category'} eq $art_category &&
					$FORM{'art_judge'} eq $art_judge &&
					$FORM{'art_class'} eq $art_class
				){
					$art_comment = $FORM{'art_comment'} unless($FORM{'art_comment'} eq $art_comment);
					$art_category = $FORM{'art_category'} unless($FORM{'art_category'} eq $art_category);
					$art_judge = $FORM{'art_judge'} unless($FORM{'art_judge'} eq $art_judge);
					$art_class = $FORM{'art_class'} unless($FORM{'art_class'} eq $art_class);
					if($rows>0){
						$sth_arta_upd->execute($art_comment,$art_category,$art_judge,$art_class,$art_id) or die $dbh->errstr;
						my $rows = $sth_arta_upd->rows();
						$sth_arta_upd->finish;
						print $LOG __LINE__,qq|:\$rows=[$rows]\n|;
					}else{
						$sth_arta_ins->execute($art_comment,$art_category,$art_judge,$art_class,$art_id) or die $dbh->errstr;
						my $rows = $sth_arta_ins->rows();
						$sth_arta_ins->finish;
						print $LOG __LINE__,qq|:\$rows=[$rows]\n|;
					}
				}

				if(exists $FORM{'cdi_name'}){
					$sth_map_sel->execute($art_id,$FORM{'ci_id'},$FORM{'cb_id'},$FORM{'md_id'},$FORM{'mv_id'},$FORM{'mr_id'}) or die $dbh->errstr;
					my $rows = $sth_map_sel->rows();
					print $LOG __LINE__,qq|:\$rows=[$rows]\n|;
					my($map_cdi_id,$cm_comment,$cm_use);
					if($rows>0){
						my $column_number = 0;
						$sth_map_sel->bind_col(++$column_number, \$map_cdi_id, undef);
						$sth_map_sel->bind_col(++$column_number, \$cm_comment, undef);
						$sth_map_sel->bind_col(++$column_number, \$cm_use, undef);
						$sth_map_sel->fetch;
					}
					$sth_map_sel->finish;

					print $LOG __LINE__,qq|:\$cm_use=[$cm_use]\n|;
					if(defined $cm_use && $cm_use){
						$cm_use = 'true';
					}else{
						$cm_use = 'false';
					}
					$FORM{'cm_use'} = 'false' unless(defined $FORM{'cm_use'});

					unless(
						$map_cdi_id eq $cdi_id &&
						$cm_comment eq $FORM{'cm_comment'} &&
						$cm_use     eq $FORM{'cm_use'}
					){
						unless($mv_publish || $mv_frozen){
							if($rows>0){
								if(defined $cdi_id){
									$sth_map_upd->execute($cdi_id,$FORM{'cm_comment'},$FORM{'cm_use'},$art_id,$FORM{'ci_id'},$FORM{'cb_id'},$FORM{'md_id'},$FORM{'mv_id'},$FORM{'mr_id'}) or die $dbh->errstr;
									my $rows = $sth_map_upd->rows();
									$sth_map_upd->finish;
									print $LOG __LINE__,qq|:\$rows=[$rows]\n|;
								}else{
									$sth_map_del->execute($art_id,$FORM{'ci_id'},$FORM{'cb_id'},$FORM{'md_id'},$FORM{'mv_id'},$FORM{'mr_id'}) or die $dbh->errstr;
									my $del_rows = $sth_map_del->rows();
									my $cm_entry;
									if($del_rows>0){
										my $column_number = 0;
										$sth_map_del->bind_col(++$column_number, \$cm_entry, undef);
										$sth_map_del->fetch;
									}
									$sth_map_del->finish;

									if($del_rows>0 && defined $FORM{'cm_comment'}){
										#削除レコードにコメントを追加
										$sth_hmap_upd->execute($FORM{'cm_comment'},$art_id,$FORM{'ci_id'},$FORM{'cb_id'},$FORM{'md_id'},$FORM{'mv_id'},$FORM{'mr_id'},$cm_entry) or die $dbh->errstr;
										$sth_hmap_upd->finish;
									}
								}
							}elsif(defined $cdi_id){
								$sth_map_ins->execute($cdi_id,$FORM{'cm_comment'},$FORM{'cm_use'},$art_id,$FORM{'ci_id'},$FORM{'cb_id'},$FORM{'md_id'},$FORM{'mv_id'},$FORM{'mr_id'}) or die $dbh->errstr;
								$sth_map_ins->finish;
							}
						}else{
							die &Encode::decode_utf8('編集不可の為、編集できません') if($mv_frozen);
							die &Encode::decode_utf8('公開中の為、編集できません') if($mv_publish);
						}
					}
				}

				if(defined $FORM{'mirror'} && $FORM{'mirror'} eq 'on'){
					my $mirror_art_id = $1.'M' if($art_id =~ /^([A-Z]+[0-9]+)/);
					if(defined $mirror_art_id && $mirror_art_id eq $art_id){
						undef $mirror_art_id;
					}
					if(defined $mirror_art_id){
print $LOG __LINE__,":\$mirror_art_id=[$mirror_art_id]\n";
						$sth_art_sel->execute($mirror_art_id) or die $dbh->errstr;
						my $mirror_rows = $sth_art_sel->rows();
						$sth_art_sel->finish;
print $LOG __LINE__,":\$mirror_rows=[$mirror_rows]\n";
						unless($mirror_rows>0){
							$sth_art_sel->execute($art_id) or die $dbh->errstr;
							my $rows = $sth_art_sel->rows();
print $LOG __LINE__,":\$art_id=[$art_id]\n";
print $LOG __LINE__,":\$rows=[$rows]\n";
							my($artg_id,$artg_name,$prefix_id,$art_serial,$art_name,$art_ext,$art_timestamp);
							if($rows>0){
								my $column_number = 0;
								$sth_art_sel->bind_col(++$column_number, \$artg_id, undef);
								$sth_art_sel->bind_col(++$column_number, \$artg_name, undef);
								$sth_art_sel->bind_col(++$column_number, \$prefix_id, undef);
								$sth_art_sel->bind_col(++$column_number, \$art_serial, undef);
								$sth_art_sel->bind_col(++$column_number, \$art_name, undef);
								$sth_art_sel->bind_col(++$column_number, \$art_ext, undef);
								$sth_art_sel->bind_col(++$column_number, \$art_timestamp, undef);
								$sth_art_sel->fetch;
							}
							$sth_art_sel->finish;
print $LOG __LINE__,":\$artg_name=[$artg_name]\n";
print $LOG __LINE__,":\$art_ext=[$art_ext]\n";
							if(defined $artg_name && defined $art_ext){
								umask(0);
#								my $group_abs_path = File::Spec->catdir($FindBin::Bin,'art_file',$artg_name);
								my $group_abs_path = File::Spec->catdir($FindBin::Bin,'art_file');
								&File::Path::mkpath($group_abs_path,{mode=>0777}) unless(-e $group_abs_path);
								my $org_file_path = File::Spec->catfile($group_abs_path,qq|$art_id-0$art_ext|);
								my $mir_file_prefix = File::Spec->catfile($group_abs_path,$mirror_art_id);
								my $mir_file_path = qq|$mir_file_prefix$art_ext|;
								my $mir_prop = &BITS::VTK::reflection($org_file_path,$mir_file_prefix);
								die __LINE__,qq|:ERROR: reflection()[$mir_file_path]| unless(defined $mir_prop);
								if(defined $mir_prop){
									my $art_xmin = $mir_prop->{bounds}->[0];
									my $art_xmax = $mir_prop->{bounds}->[1];
									my $art_ymin = $mir_prop->{bounds}->[2];
									my $art_ymax = $mir_prop->{bounds}->[3];
									my $art_zmin = $mir_prop->{bounds}->[4];
									my $art_zmax = $mir_prop->{bounds}->[5];
									my $art_volume = defined $mir_prop->{volume} && $mir_prop->{volume} > 0 ?  &Truncated($mir_prop->{volume} / 1000) : 0;
									my $art_cube_volume = &Truncated(($art_xmax-$art_xmin)*($art_ymax-$art_ymin)*($art_zmax-$art_zmin)/1000);

									if(-e $mir_file_path && -s $mir_file_path){
										my $cmd = qq{sed -e "/^mtllib/d" "$mir_file_path" | sed -e "/^#/d" | sed -e "/^ *\$/d" |};
										my $art_data = &readFile($cmd);
										my $art_data_size = length($art_data);
										if($art_data_size>0){
											my $art_md5 = &Digest::MD5::md5_hex($art_data);

											my $mir_file_deci_prefix = File::Spec->catfile($group_abs_path,qq|$mirror_art_id.deci|);
											my $mir_file_deci_path = qq|$mir_file_deci_prefix$art_ext|;

											&BITS::VTK::quadricDecimation($mir_file_path,$mir_file_deci_prefix);
											if(-e $mir_file_deci_path && -s $mir_file_deci_path){
												my $cmd = qq{sed -e "/^mtllib/d" "$mir_file_deci_path" | sed -e "/^#/d" | sed -e "/^ *\$/d" |};
												my $art_decimate = &readFile($cmd);
												my $art_decimate_size = length($art_decimate);
												if($art_decimate_size>0){
													my $param_num = 0;
													$sth_art_mirror_ins->bind_param(++$param_num, $FORM{'md_id'});
													$sth_art_mirror_ins->bind_param(++$param_num, $FORM{'mv_id'});
													$sth_art_mirror_ins->bind_param(++$param_num, $FORM{'mr_id'});
													$sth_art_mirror_ins->bind_param(++$param_num, $artg_id);
													$sth_art_mirror_ins->bind_param(++$param_num, $prefix_id);
													$sth_art_mirror_ins->bind_param(++$param_num, $mirror_art_id);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_serial);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_name);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_ext);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_timestamp);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_md5);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_data, { pg_type => DBD::Pg::PG_BYTEA });
													$sth_art_mirror_ins->bind_param(++$param_num, $art_data_size);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_decimate, { pg_type => DBD::Pg::PG_BYTEA });
													$sth_art_mirror_ins->bind_param(++$param_num, $art_decimate_size);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_xmin);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_xmax);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_ymin);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_ymax);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_zmin);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_zmax);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_volume);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_cube_volume);
													$sth_art_mirror_ins->execute() or die $dbh->errstr;
													$mirror_rows = $sth_art_mirror_ins->rows();
													$sth_art_mirror_ins->finish();

													$sth_arti_mirror_ins->execute($artg_id,$mirror_art_id,$art_name,$art_ext,$art_timestamp) or die $dbh->errstr;
													$sth_arti_mirror_ins->finish();

													&BITS::Voxel::insVoxelData($dbh,$mirror_art_id,0,$art_data);
												}
											}else{
												die __LINE__,qq|:ERROR: quadricDecimation()[$mir_file_deci_path]|;
											}
										}
									}
								}
							}
						}
						if($mirror_rows>0){

							$sth_arta_sel->execute($mirror_art_id) or die $dbh->errstr;
							my $rows = $sth_arta_sel->rows();
							my($art_comment,$art_category,$art_judge,$art_class);
							if($rows>0){
								my $column_number = 0;
								$sth_arta_sel->bind_col(++$column_number, \$art_comment, undef);
								$sth_arta_sel->bind_col(++$column_number, \$art_category, undef);
								$sth_arta_sel->bind_col(++$column_number, \$art_judge, undef);
								$sth_arta_sel->bind_col(++$column_number, \$art_class, undef);
								$sth_arta_sel->fetch;
							}
							$sth_arta_sel->finish;
							unless(
								$FORM{'art_comment'} eq $art_comment &&
								$FORM{'art_category'} eq $art_category &&
								$FORM{'art_judge'} eq $art_judge &&
								$FORM{'art_class'} eq $art_class
							){
								$art_comment = $FORM{'art_comment'} unless($FORM{'art_comment'} eq $art_comment);
								$art_category = $FORM{'art_category'} unless($FORM{'art_category'} eq $art_category);
								$art_judge = $FORM{'art_judge'} unless($FORM{'art_judge'} eq $art_judge);
								$art_class = $FORM{'art_class'} unless($FORM{'art_class'} eq $art_class);
								if($rows>0){
									$sth_arta_upd->execute($art_comment,$art_category,$art_judge,$art_class,$mirror_art_id) or die $dbh->errstr;
									$sth_arta_upd->finish;
								}else{
									$sth_arta_ins->execute($art_comment,$art_category,$art_judge,$art_class,$mirror_art_id) or die $dbh->errstr;
									$sth_arta_ins->finish;
								}
							}

							if(exists $FORM{'mirror_same_concept'} || exists $FORM{'mirror_cdi_name'}){
								my $mirror_cdi_id;
								my $mirror_cm_comment = $FORM{'cm_comment'};
								my $mirror_cm_use = $FORM{'cm_use'};
								if(defined $FORM{'mirror_same_concept'} && defined $cdi_id){
									$mirror_cdi_id = $cdi_id;
								}elsif(defined $FORM{'mirror_cdi_name'}){
									my $sth_cdi_sel = $dbh->prepare(qq|select cdi_id from concept_data_info where ci_id=? AND cdi_name=?|) or die $dbh->errstr;
									$sth_cdi_sel->execute($FORM{'ci_id'},$FORM{'mirror_cdi_name'}) or die $dbh->errstr;
									my $column_number = 0;
									$sth_cdi_sel->bind_col(++$column_number, \$mirror_cdi_id, undef);
									$sth_cdi_sel->fetch;
									$sth_cdi_sel->finish;
									undef $sth_cdi_sel;
								}

								$sth_map_sel->execute($mirror_art_id,$FORM{'ci_id'},$FORM{'cb_id'},$FORM{'md_id'},$FORM{'mv_id'},$FORM{'mr_id'}) or die $dbh->errstr;
								my $rows = $sth_map_sel->rows();
								my($map_cdi_id,$cm_comment,$cm_use);
								if($rows>0){
									my $column_number = 0;
									$sth_map_sel->bind_col(++$column_number, \$map_cdi_id, undef);
									$sth_map_sel->bind_col(++$column_number, \$cm_comment, undef);
									$sth_map_sel->bind_col(++$column_number, \$cm_use, undef);
									$sth_map_sel->fetch;
								}
								$sth_map_sel->finish;

								if(defined $cm_use && $cm_use){
									$cm_use = 'true';
								}else{
									$cm_use = 'false';
								}

								unless(
									$map_cdi_id eq $mirror_cdi_id &&
									$cm_comment eq $mirror_cm_comment &&
									$cm_use     eq $mirror_cm_use
								){
									unless($mv_publish || $mv_frozen){
										if($rows>0){
											if(defined $mirror_cdi_id){
												$sth_map_upd->execute($mirror_cdi_id,$mirror_cm_comment,$mirror_cm_use,$mirror_art_id,$FORM{'ci_id'},$FORM{'cb_id'},$FORM{'md_id'},$FORM{'mv_id'},$FORM{'mr_id'}) or die $dbh->errstr;
												$sth_map_upd->finish;
											}else{
												$sth_map_del->execute($mirror_art_id,$FORM{'ci_id'},$FORM{'cb_id'},$FORM{'md_id'},$FORM{'mv_id'},$FORM{'mr_id'}) or die $dbh->errstr;
												my $del_rows = $sth_map_del->rows();
												my $cm_entry;
												if($del_rows>0){
													my $column_number = 0;
													$sth_map_del->bind_col(++$column_number, \$cm_entry, undef);
													$sth_map_del->fetch;
												}
												$sth_map_del->finish;
												if($del_rows>0){
													#削除レコードにコメントを追加
													$sth_hmap_upd->execute($mirror_cm_comment,$art_id,$FORM{'ci_id'},$FORM{'cb_id'},$FORM{'md_id'},$FORM{'mv_id'},$FORM{'mr_id'},$cm_entry) or die $dbh->errstr;
													$sth_hmap_upd->finish;
												}
											}
										}elsif(defined $mirror_cdi_id){
											$sth_map_ins->execute($mirror_cdi_id,$mirror_cm_comment,$mirror_cm_use,$mirror_art_id,$FORM{'ci_id'},$FORM{'cb_id'},$FORM{'md_id'},$FORM{'mv_id'},$FORM{'mr_id'}) or die $dbh->errstr;
											$sth_map_ins->finish;
										}
									}else{
										die &Encode::decode_utf8('編集不可の為、編集できません') if($mv_frozen);
										die &Encode::decode_utf8('公開中の為、編集できません') if($mv_publish);
									}
								}
							}

						}
					}
				}
				if(defined $FORM{'set_same_use_setting_mirror_part'} && $FORM{'set_same_use_setting_mirror_part'} eq 'true'){
					my $target_art_id;
					my $is_mirror_id;
					if($art_id =~ /^([A-Z]+[0-9]+)(M*)/){
						$target_art_id = $1;
						$is_mirror_id = $2;
					}
					if(defined $target_art_id){
						$target_art_id .= 'M' unless($is_mirror_id);
print $LOG __LINE__,":\$target_art_id=[$target_art_id]\n";
						$sth_map_upd_set_mirror->execute($FORM{'cm_use'},$target_art_id,$FORM{'ci_id'},$FORM{'cb_id'},$FORM{'md_id'},$FORM{'mv_id'},$FORM{'mr_id'},$FORM{'cm_use'}) or die $dbh->errstr;
						my $rows = $sth_map_upd_set_mirror->rows();
						$sth_map_upd_set_mirror->finish;
						print $LOG __LINE__,qq|:\$rows=[$rows]\n|;
					}
				}
			}
			undef $sth_arta_sel;




			my %ART_IDS;
			foreach my $art_id (@$art_ids){
				$ART_IDS{$art_id} = undef;
				if(defined $FORM{'mirror'} && $FORM{'mirror'} eq 'on'){
					my $mirror_art_id = $1.'M' if($art_id =~ /^([A-Z]+[0-9]+)/);
					undef $mirror_art_id if(defined $mirror_art_id && $mirror_art_id eq $art_id);
					$ART_IDS{$mirror_art_id} = undef if(defined $mirror_art_id);
				}
				if(defined $FORM{'set_same_use_setting_mirror_part'} && $FORM{'set_same_use_setting_mirror_part'} eq 'true'){
					my $target_art_id;
					my $is_mirror_id;
					if($art_id =~ /^([A-Z]+[0-9]+)(M*)/){
						$target_art_id = $1;
						$is_mirror_id = $2;
					}
					if(defined $target_art_id){
						$target_art_id .= 'M' unless($is_mirror_id);
						$ART_IDS{$target_art_id} = undef;
					}
				}
			}
			if(scalar keys(%ART_IDS) > 0){
				&BITS::ConceptArtMapModified::exec(
					dbh => $dbh,
					ci_id => $FORM{'ci_id'},
					cb_id => $FORM{'cb_id'},
					md_id => $FORM{'md_id'},
					mv_id => $FORM{'mv_id'},
					mr_id => $FORM{'mr_id'},
					art_ids => [keys(%ART_IDS)]
				);
			}
			undef %ART_IDS;

			$dbh->commit();
			$dbh->do("NOTIFY art_file");
			$dbh->do("NOTIFY concept_art_map");
#			$dbh->rollback;

			$DATAS->{'success'} = JSON::XS::true;
		};
		if($@){
			print $LOG __LINE__,":",$@,"\n";
			$DATAS->{'msg'} = $@;
			&utf8::decode($DATAS->{'msg'}) unless(&Encode::is_utf8($DATAS->{'msg'}));

			$dbh->rollback;
		}
		$dbh->{'AutoCommit'} = 1;
		$dbh->{'RaiseError'} = 0;

	}else{
		$DATAS->{'msg'} = qq|JSON形式が違います|;
		&utf8::decode($DATAS->{'msg'}) unless(&Encode::is_utf8($DATAS->{'msg'}));
	}
}
elsif($FORM{'cmd'} eq 'update_ver2'){
	&cgi_lib::common::message($FORM{'cmd'}, $LOG) if(defined $LOG);

	#$epocsec = &Time::HiRes::tv_interval($t0);
	#($sec,$min) = localtime($epocsec);
	&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

=pod
43:$FORM{art_category}=[hepatic artery]
43:$FORM{art_class}=[1]
43:$FORM{art_comment}=[morphology checked OK]
43:$FORM{art_ids}=[["FJ2386"]]
43:$FORM{art_judge}=[]
43:$FORM{cdi_name}=[FMA70447]
43:$FORM{cmd}=[update]
43:$FORM{fieldset-1394-checkbox}=[on]
43:$FORM{'mirror_same_concept'}=[on]

43:$FORM{art_category}=[hepatic artery]
43:$FORM{art_class}=[1]
43:$FORM{art_comment}=[morphology checked OK]
43:$FORM{art_ids}=[["FJ2386"]]
43:$FORM{art_judge}=[]
43:$FORM{cb_id}=[4]
43:$FORM{cdi_name}=[FMA70447]
43:$FORM{ci_id}=[1]
43:$FORM{cmd}=[update]
43:$FORM{'mirror'}=[on]
43:$FORM{mirror_cdi_name}=[FMA70455]
=cut

	my $datas = &cgi_lib::common::decodeJSON($FORM{'datas'});
	if(defined $datas && ref $datas eq 'ARRAY'){

#print $LOG __LINE__,":",&Data::Dumper::Dumper($datas),"\n";

		$dbh->{'AutoCommit'} = 0;
		$dbh->{'RaiseError'} = 1;
		eval{


			my $openid = qq|system|;

			my $sql =<<SQL;
select
 arti.artg_id,
 artg_name,
 prefix_id,
 art_serial,
 arti.art_name,
 arti.art_ext,
 arti.art_timestamp
from
 art_file as art
left join (
 select * from art_file_info
) as arti on
   arti.art_id=art.art_id
left join (
 select * from art_group
) as artg on
   artg.artg_id=arti.artg_id
where art.art_id=?
SQL
			my $sth_art_sel = $dbh->prepare($sql) or die $dbh->errstr;

			$sql =<<SQL;
insert into art_file (
  md_id,
  mv_id,
  mr_id,
  artg_id,
  prefix_id,
  art_id,
  art_serial,
  art_name,
  art_ext,
  art_timestamp,
  art_md5,
  art_data,
  art_data_size,
  art_decimate,
  art_decimate_size,
  art_xmin,
  art_xmax,
  art_ymin,
  art_ymax,
  art_zmin,
  art_zmax,
  art_volume,
  art_cube_volume,
  art_mirroring,
  art_openid
) values (
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  'true',
  '$openid'
)
;
SQL
			my $sth_art_mirror_ins = $dbh->prepare($sql) or die $dbh->errstr;

			$sql =<<SQL;
insert into art_file_info (
  artg_id,
  art_id,
  art_name,
  art_ext,
  art_timestamp,
  art_mirroring,
  art_openid
) values (
  ?,
  ?,
  ?,
  ?,
  ?,
  'true',
  '$openid'
)
;
SQL
			my $sth_arti_mirror_ins = $dbh->prepare($sql) or die $dbh->errstr;

			my $sth_arta_sel = $dbh->prepare(qq|select art_comment,art_category,art_judge,art_class from art_annotation where art_id=?|) or die $dbh->errstr;
			my $sth_arta_upd = $dbh->prepare(qq|update art_annotation set art_comment=?,art_category=?,art_judge=?,art_class=?,art_entry=now() where art_id=?|) or die $dbh->errstr;
			my $sth_arta_ins = $dbh->prepare(qq|insert into art_annotation (art_comment,art_category,art_judge,art_class,art_id,art_entry,art_openid) values (?,?,?,?,?,now(),'$openid')|) or die $dbh->errstr;

#			my $sth_map_sel = $dbh->prepare(qq|select cdi_id,cm_comment,cm_use from concept_art_map where art_id=? and ci_id=? and cb_id=? and md_id=? and mv_id=? and mr_id=?|) or die $dbh->errstr;
			my $sth_map_sel = $dbh->prepare(qq|select cdi_id,cm_comment,cm_use,cmp_id from concept_art_map where art_id=? and ci_id=? and cb_id=? and md_id=? and mv_id=? and mr_id=?|) or die $dbh->errstr;
#			my $sth_map_upd = $dbh->prepare(qq|update concept_art_map set cdi_id=?,cm_comment=?,cm_use=?,cm_entry=now() where art_id=? and ci_id=? and cb_id=? and md_id=? and mv_id=? and mr_id=?|) or die $dbh->errstr;
			my $sth_map_upd = $dbh->prepare(qq|update concept_art_map set cdi_id=?,cm_comment=?,cm_use=?,cmp_id=?,cm_entry=now() where art_id=? and ci_id=? and cb_id=? and md_id=? and mv_id=? and mr_id=?|) or die $dbh->errstr;
#			my $sth_map_ins = $dbh->prepare(qq|insert into concept_art_map (cdi_id,cm_comment,cm_use,art_id,ci_id,cb_id,md_id,mv_id,mr_id,cm_entry,cm_openid) values (?,?,?,?,?,?,?,?,?,now(),'$openid')|) or die $dbh->errstr;
			my $sth_map_ins = $dbh->prepare(qq|insert into concept_art_map (cdi_id,cm_comment,cm_use,cmp_id,art_id,ci_id,cb_id,md_id,mv_id,mr_id,cm_entry,cm_openid) values (?,?,?,?,?,?,?,?,?,?,now(),'$openid')|) or die $dbh->errstr;

			my $sth_map_del = $dbh->prepare(qq|delete from concept_art_map where art_id=? and ci_id=? and cb_id=? and md_id=? and mv_id=? and mr_id=? RETURNING cm_entry|) or die $dbh->errstr;

			my $sth_hmap_upd = $dbh->prepare(qq|update history_concept_art_map set cm_comment=? where art_id=? and ci_id=? and cb_id=? and md_id=? and mv_id=? and mr_id=? and cm_entry=? and hist_event=(select he_id from history_event where he_name='DELETE')|) or die $dbh->errstr;

			my $sth_map_upd_set_mirror = $dbh->prepare(qq|update concept_art_map set cm_use=?,cm_entry=now() where art_id=? and ci_id=? and cb_id=? and md_id=? and mv_id=? and mr_id=? and cm_use<>?|) or die $dbh->errstr;

			my $sth_model_version = $dbh->prepare(qq|select mv_publish,mv_frozen from model_version where md_id=? AND mv_id=?|) or die $dbh->errstr;
			$sth_model_version->execute($FORM{'md_id'},$FORM{'mv_id'}) or die $dbh->errstr;
			my $column_number = 0;
			my $mv_publish;
			my $mv_frozen;
			$sth_model_version->bind_col(++$column_number, \$mv_publish, undef);
			$sth_model_version->bind_col(++$column_number, \$mv_frozen, undef);
			$sth_model_version->fetch;
			$sth_model_version->finish;
			undef $sth_model_version;
#			die &Encode::decode_utf8('公開中の為、編集できません') if($mv_publish);
#			die &Encode::decode_utf8('編集不可の為、編集できません') if($mv_frozen);

#			die "error!!";


			my $sth_cdi_sel = $dbh->prepare(qq|select cdi_id from concept_data_info where ci_id=? AND cdi_name=?|) or die $dbh->errstr;

			#$epocsec = &Time::HiRes::tv_interval($t0);
			#($sec,$min) = localtime($epocsec);
			&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

			foreach my $data (@$datas){
				my $art_id = (exists $data->{'art_id'} && defined $data->{'art_id'}) ? $data->{'art_id'} : undef;
				next unless(defined $art_id);

				my $cdi_id;
				if(exists $data->{'cdi_name'} && defined $data->{'cdi_name'}){
					$sth_cdi_sel->execute($FORM{'ci_id'},$data->{'cdi_name'}) or die $dbh->errstr;
					my $column_number = 0;
					$sth_cdi_sel->bind_col(++$column_number, \$cdi_id, undef);
					$sth_cdi_sel->fetch;
					$sth_cdi_sel->finish;
				}

				$sth_arta_sel->execute($art_id) or die $dbh->errstr;
				my $rows = $sth_arta_sel->rows();
				my($art_comment,$art_category,$art_judge,$art_class);
				if($rows>0){
					my $column_number = 0;
					$sth_arta_sel->bind_col(++$column_number, \$art_comment, undef);
					$sth_arta_sel->bind_col(++$column_number, \$art_category, undef);
					$sth_arta_sel->bind_col(++$column_number, \$art_judge, undef);
					$sth_arta_sel->bind_col(++$column_number, \$art_class, undef);
					$sth_arta_sel->fetch;
				}
				$sth_arta_sel->finish;
				print $LOG __LINE__,qq|:\$rows=[$rows]\n|;
#				next unless($rows>0);
				unless(
					defined $art_comment && exists $data->{'art_comment'} && defined $data->{'art_comment'} && $data->{'art_comment'} eq $art_comment &&
					defined $art_category && exists $data->{'art_category'} && defined $data->{'art_category'} && $data->{'art_category'} eq $art_category &&
					defined $art_judge && exists $data->{'art_judge'} && defined $data->{'art_judge'} && $data->{'art_judge'} eq $art_judge &&
					defined $art_class && exists $data->{'art_class'} && defined $data->{'art_class'} && $data->{'art_class'} eq $art_class
				){
					$art_comment = $data->{'art_comment'}   unless(defined $art_comment && exists $data->{'art_comment'} && defined $data->{'art_comment'} && $data->{'art_comment'} eq $art_comment);
					$art_category = $data->{'art_category'} unless(defined $art_category && exists $data->{'art_category'} && defined $data->{'art_category'} && $data->{'art_category'} eq $art_category);
					$art_judge = $data->{'art_judge'}       unless(defined $art_judge && exists $data->{'art_judge'} && defined $data->{'art_judge'} && $data->{'art_judge'} eq $art_judge);
					$art_class = $data->{'art_class'}       unless(defined $art_class && exists $data->{'art_class'} && defined $data->{'art_class'} && $data->{'art_class'} eq $art_class);
					if($rows>0){
						$sth_arta_upd->execute($art_comment,$art_category,$art_judge,$art_class,$art_id) or die $dbh->errstr;
						my $rows = $sth_arta_upd->rows();
						$sth_arta_upd->finish;
						print $LOG __LINE__,qq|:\$rows=[$rows]\n|;
					}else{
						$sth_arta_ins->execute($art_comment,$art_category,$art_judge,$art_class,$art_id) or die $dbh->errstr;
						my $rows = $sth_arta_ins->rows();
						$sth_arta_ins->finish;
						print $LOG __LINE__,qq|:\$rows=[$rows]\n|;
					}
				}

#				if(defined $cdi_id){
					$sth_map_sel->execute($art_id,$FORM{'ci_id'},$FORM{'cb_id'},$FORM{'md_id'},$FORM{'mv_id'},$FORM{'mr_id'}) or die $dbh->errstr;
					$rows = $sth_map_sel->rows();
					print $LOG __LINE__,qq|:\$rows=[$rows]\n|;
					my($map_cdi_id,$cm_comment,$cm_use,$cmp_id);
					if($rows>0){
						my $column_number = 0;
						$sth_map_sel->bind_col(++$column_number, \$map_cdi_id, undef);
						$sth_map_sel->bind_col(++$column_number, \$cm_comment, undef);
						$sth_map_sel->bind_col(++$column_number, \$cm_use, undef);
						$sth_map_sel->bind_col(++$column_number, \$cmp_id, undef);
						$sth_map_sel->fetch;
					}
					$sth_map_sel->finish;

					print $LOG __LINE__,qq|:\$cm_use=[$cm_use]\n|;
					if(defined $cm_use && $cm_use){
						$cm_use = 1;
					}else{
						$cm_use = 0;
					}
					if(exists $data->{'cm_use'} && defined $data->{'cm_use'} && $data->{'cm_use'}){
						$data->{'cm_use'} = 1;
					}else{
						$data->{'cm_use'} = 0;
					}

					if(defined $cmp_id){
						$cmp_id -= 0;
					}else{
						$cmp_id = 0;
					}
					if(exists $data->{'cmp_id'} && defined $data->{'cmp_id'}){
						$data->{'cmp_id'} -= 0;
					}else{
						$data->{'cmp_id'} = 0;
					}

					unless(
						defined $map_cdi_id &&
						defined $cdi_id &&
						$map_cdi_id eq $cdi_id &&
						defined $cm_comment && exists $data->{'cm_comment'} && defined $data->{'cm_comment'} && $cm_comment eq $data->{'cm_comment'} &&
						$cm_use == $data->{'cm_use'} &&
						$cmp_id == $data->{'cmp_id'}
					){
						unless($mv_publish || $mv_frozen){
							if($rows>0){
								if(defined $cdi_id){
									$sth_map_upd->execute($cdi_id,$data->{'cm_comment'},$data->{'cm_use'},$data->{'cmp_id'},$art_id,$FORM{'ci_id'},$FORM{'cb_id'},$FORM{'md_id'},$FORM{'mv_id'},$FORM{'mr_id'}) or die $dbh->errstr;
									my $rows = $sth_map_upd->rows();
									$sth_map_upd->finish;
									print $LOG __LINE__,qq|:\$rows=[$rows]\n|;
								}else{
									$sth_map_del->execute($art_id,$FORM{'ci_id'},$FORM{'cb_id'},$FORM{'md_id'},$FORM{'mv_id'},$FORM{'mr_id'}) or die $dbh->errstr;
									my $del_rows = $sth_map_del->rows();
									my $cm_entry;
									if($del_rows>0){
										my $column_number = 0;
										$sth_map_del->bind_col(++$column_number, \$cm_entry, undef);
										$sth_map_del->fetch;
									}
									$sth_map_del->finish;

									if($del_rows>0 && defined $data->{'cm_comment'}){
										#削除レコードにコメントを追加
										$sth_hmap_upd->execute($data->{'cm_comment'},$art_id,$FORM{'ci_id'},$FORM{'cb_id'},$FORM{'md_id'},$FORM{'mv_id'},$FORM{'mr_id'},$cm_entry) or die $dbh->errstr;
										$sth_hmap_upd->finish;
									}
								}
							}elsif(defined $cdi_id){
								$sth_map_ins->execute($cdi_id,$data->{'cm_comment'},$data->{'cm_use'},$data->{'cmp_id'},$art_id,$FORM{'ci_id'},$FORM{'cb_id'},$FORM{'md_id'},$FORM{'mv_id'},$FORM{'mr_id'}) or die $dbh->errstr;
								$sth_map_ins->finish;
							}
						}else{
							die &Encode::decode_utf8('編集不可の為、編集できません') if($mv_frozen);
							die &Encode::decode_utf8('公開中の為、編集できません') if($mv_publish);
						}
					}
#				}

				if(defined $data->{'mirror'} && $data->{'mirror'}){
					my $mirror_art_id = $1.'M' if($art_id =~ /^([A-Z]+[0-9]+)/);
					if(defined $mirror_art_id && $mirror_art_id eq $art_id){
						undef $mirror_art_id;
					}
					if(defined $mirror_art_id){
print $LOG __LINE__,":\$mirror_art_id=[$mirror_art_id]\n";
						$sth_art_sel->execute($mirror_art_id) or die $dbh->errstr;
						my $mirror_rows = $sth_art_sel->rows();
						$sth_art_sel->finish;
print $LOG __LINE__,":\$mirror_rows=[$mirror_rows]\n";
						unless($mirror_rows>0){
							$sth_art_sel->execute($art_id) or die $dbh->errstr;
							my $rows = $sth_art_sel->rows();
print $LOG __LINE__,":\$art_id=[$art_id]\n";
print $LOG __LINE__,":\$rows=[$rows]\n";
							my($artg_id,$artg_name,$prefix_id,$art_serial,$art_name,$art_ext,$art_timestamp);
							if($rows>0){
								my $column_number = 0;
								$sth_art_sel->bind_col(++$column_number, \$artg_id, undef);
								$sth_art_sel->bind_col(++$column_number, \$artg_name, undef);
								$sth_art_sel->bind_col(++$column_number, \$prefix_id, undef);
								$sth_art_sel->bind_col(++$column_number, \$art_serial, undef);
								$sth_art_sel->bind_col(++$column_number, \$art_name, undef);
								$sth_art_sel->bind_col(++$column_number, \$art_ext, undef);
								$sth_art_sel->bind_col(++$column_number, \$art_timestamp, undef);
								$sth_art_sel->fetch;
							}
							$sth_art_sel->finish;
print $LOG __LINE__,":\$artg_name=[$artg_name]\n";
print $LOG __LINE__,":\$art_ext=[$art_ext]\n";
							if(defined $artg_name && defined $art_ext){
								umask(0);
#								my $group_abs_path = File::Spec->catdir($FindBin::Bin,'art_file',$artg_name);
								my $group_abs_path = File::Spec->catdir($FindBin::Bin,'art_file');
								&File::Path::mkpath($group_abs_path,{mode=>0777}) unless(-e $group_abs_path);
								my $org_file_path = File::Spec->catfile($group_abs_path,qq|$art_id-0$art_ext|);
								my $mir_file_prefix = File::Spec->catfile($group_abs_path,$mirror_art_id);
								my $mir_file_path = qq|$mir_file_prefix$art_ext|;
								my $mir_prop = &BITS::VTK::reflection($org_file_path,$mir_file_prefix);
								die __LINE__,qq|:ERROR: reflection()[$mir_file_path]| unless(defined $mir_prop);
								if(defined $mir_prop){
									my $art_xmin = $mir_prop->{bounds}->[0];
									my $art_xmax = $mir_prop->{bounds}->[1];
									my $art_ymin = $mir_prop->{bounds}->[2];
									my $art_ymax = $mir_prop->{bounds}->[3];
									my $art_zmin = $mir_prop->{bounds}->[4];
									my $art_zmax = $mir_prop->{bounds}->[5];
									my $art_volume = defined $mir_prop->{volume} && $mir_prop->{volume} > 0 ?  &Truncated($mir_prop->{volume} / 1000) : 0;
									my $art_cube_volume = &Truncated(($art_xmax-$art_xmin)*($art_ymax-$art_ymin)*($art_zmax-$art_zmin)/1000);

									if(-e $mir_file_path && -s $mir_file_path){
										my $cmd = qq{sed -e "/^mtllib/d" "$mir_file_path" | sed -e "/^#/d" | sed -e "/^ *\$/d" |};
										my $art_data = &readFile($cmd);
										my $art_data_size = length($art_data);
										if($art_data_size>0){
											my $art_md5 = &Digest::MD5::md5_hex($art_data);

											my $mir_file_deci_prefix = File::Spec->catfile($group_abs_path,qq|$mirror_art_id.deci|);
											my $mir_file_deci_path = qq|$mir_file_deci_prefix$art_ext|;

											&BITS::VTK::quadricDecimation($mir_file_path,$mir_file_deci_prefix);
											if(-e $mir_file_deci_path && -s $mir_file_deci_path){
												my $cmd = qq{sed -e "/^mtllib/d" "$mir_file_deci_path" | sed -e "/^#/d" | sed -e "/^ *\$/d" |};
												my $art_decimate = &readFile($cmd);
												my $art_decimate_size = length($art_decimate);
												if($art_decimate_size>0){
													my $param_num = 0;
													$sth_art_mirror_ins->bind_param(++$param_num, $FORM{'md_id'});
													$sth_art_mirror_ins->bind_param(++$param_num, $FORM{'mv_id'});
													$sth_art_mirror_ins->bind_param(++$param_num, $FORM{'mr_id'});
													$sth_art_mirror_ins->bind_param(++$param_num, $artg_id);
													$sth_art_mirror_ins->bind_param(++$param_num, $prefix_id);
													$sth_art_mirror_ins->bind_param(++$param_num, $mirror_art_id);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_serial);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_name);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_ext);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_timestamp);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_md5);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_data, { pg_type => DBD::Pg::PG_BYTEA });
													$sth_art_mirror_ins->bind_param(++$param_num, $art_data_size);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_decimate, { pg_type => DBD::Pg::PG_BYTEA });
													$sth_art_mirror_ins->bind_param(++$param_num, $art_decimate_size);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_xmin);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_xmax);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_ymin);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_ymax);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_zmin);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_zmax);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_volume);
													$sth_art_mirror_ins->bind_param(++$param_num, $art_cube_volume);
													$sth_art_mirror_ins->execute() or die $dbh->errstr;
													$mirror_rows = $sth_art_mirror_ins->rows();
													$sth_art_mirror_ins->finish();

													$sth_arti_mirror_ins->execute($artg_id,$mirror_art_id,$art_name,$art_ext,$art_timestamp) or die $dbh->errstr;
													$sth_arti_mirror_ins->finish();

													&BITS::Voxel::insVoxelData($dbh,$mirror_art_id,0,$art_data);
												}
											}else{
												die __LINE__,qq|:ERROR: quadricDecimation()[$mir_file_deci_path]|;
											}
										}
									}
								}
							}
						}
						if($mirror_rows>0){

							$sth_arta_sel->execute($mirror_art_id) or die $dbh->errstr;
							my $rows = $sth_arta_sel->rows();
							my($art_comment,$art_category,$art_judge,$art_class);
							if($rows>0){
								my $column_number = 0;
								$sth_arta_sel->bind_col(++$column_number, \$art_comment, undef);
								$sth_arta_sel->bind_col(++$column_number, \$art_category, undef);
								$sth_arta_sel->bind_col(++$column_number, \$art_judge, undef);
								$sth_arta_sel->bind_col(++$column_number, \$art_class, undef);
								$sth_arta_sel->fetch;
							}
							$sth_arta_sel->finish;
							unless(
								$data->{'art_comment'} eq $art_comment &&
								$data->{'art_category'} eq $art_category &&
								$data->{'art_judge'} eq $art_judge &&
								$data->{'art_class'} eq $art_class
							){
								$art_comment = $data->{'art_comment'} unless($data->{'art_comment'} eq $art_comment);
								$art_category = $data->{'art_category'} unless($data->{'art_category'} eq $art_category);
								$art_judge = $data->{'art_judge'} unless($data->{'art_judge'} eq $art_judge);
								$art_class = $data->{'art_class'} unless($data->{'art_class'} eq $art_class);
								if($rows>0){
									$sth_arta_upd->execute($art_comment,$art_category,$art_judge,$art_class,$mirror_art_id) or die $dbh->errstr;
									$sth_arta_upd->finish;
								}else{
									$sth_arta_ins->execute($art_comment,$art_category,$art_judge,$art_class,$mirror_art_id) or die $dbh->errstr;
									$sth_arta_ins->finish;
								}
							}

							if(exists $data->{'mirror_same_concept'} && defined $data->{'mirror_same_concept'} || exists $data->{'mirror_cdi_name'} && defined $data->{'mirror_cdi_name'}){
								my $mirror_cdi_id;
								my $mirror_cm_comment = $data->{'cm_comment'};
								my $mirror_cm_use = $data->{'cm_use'};
								my $mirror_cmp_id = $data->{'cmp_id'};
								if(defined $data->{'mirror_same_concept'} && $data->{'mirror_same_concept'} && defined $cdi_id && length $cdi_id){
									$mirror_cdi_id = $cdi_id;
								}elsif(defined $data->{'mirror_cdi_name'} && length $data->{'mirror_cdi_name'}){


									$sth_cdi_sel->execute($FORM{'ci_id'},$data->{'mirror_cdi_name'}) or die $dbh->errstr;
									my $column_number = 0;
									$sth_cdi_sel->bind_col(++$column_number, \$mirror_cdi_id, undef);
									$sth_cdi_sel->fetch;
									$sth_cdi_sel->finish;

								}

								$sth_map_sel->execute($mirror_art_id,$FORM{'ci_id'},$FORM{'cb_id'},$FORM{'md_id'},$FORM{'mv_id'},$FORM{'mr_id'}) or die $dbh->errstr;
								my $rows = $sth_map_sel->rows();
								my($map_cdi_id,$cm_comment,$cm_use,$cmp_id);
								if($rows>0){
									my $column_number = 0;
									$sth_map_sel->bind_col(++$column_number, \$map_cdi_id, undef);
									$sth_map_sel->bind_col(++$column_number, \$cm_comment, undef);
									$sth_map_sel->bind_col(++$column_number, \$cm_use, undef);
									$sth_map_sel->bind_col(++$column_number, \$cmp_id, undef);
									$sth_map_sel->fetch;
								}
								$sth_map_sel->finish;

								if(defined $cm_use && $cm_use){
									$cm_use = 1;
								}else{
									$cm_use = 0;
								}
								if(defined $cmp_id){
									$cmp_id -= 0;
								}else{
									$cmp_id = 0;
								}

								unless(
									$map_cdi_id eq $mirror_cdi_id &&
									$cm_comment eq $mirror_cm_comment &&
									$cm_use     == $mirror_cm_use &&
									$cmp_id     == $mirror_cmp_id
								){
									unless($mv_publish || $mv_frozen){
										if($rows>0){
											if(defined $mirror_cdi_id){
												$sth_map_upd->execute($mirror_cdi_id,$mirror_cm_comment,$mirror_cm_use,$mirror_cmp_id,$mirror_art_id,$FORM{'ci_id'},$FORM{'cb_id'},$FORM{'md_id'},$FORM{'mv_id'},$FORM{'mr_id'}) or die $dbh->errstr;
												$sth_map_upd->finish;
											}else{
												$sth_map_del->execute($mirror_art_id,$FORM{'ci_id'},$FORM{'cb_id'},$FORM{'md_id'},$FORM{'mv_id'},$FORM{'mr_id'}) or die $dbh->errstr;
												my $del_rows = $sth_map_del->rows();
												my $cm_entry;
												if($del_rows>0){
													my $column_number = 0;
													$sth_map_del->bind_col(++$column_number, \$cm_entry, undef);
													$sth_map_del->fetch;
												}
												$sth_map_del->finish;
												if($del_rows>0){
													#削除レコードにコメントを追加
													$sth_hmap_upd->execute($mirror_cm_comment,$art_id,$FORM{'ci_id'},$FORM{'cb_id'},$FORM{'md_id'},$FORM{'mv_id'},$FORM{'mr_id'},$cm_entry) or die $dbh->errstr;
													$sth_hmap_upd->finish;
												}
											}
										}elsif(defined $mirror_cdi_id){
											$sth_map_ins->execute($mirror_cdi_id,$mirror_cm_comment,$mirror_cm_use,$mirror_cmp_id,$mirror_art_id,$FORM{'ci_id'},$FORM{'cb_id'},$FORM{'md_id'},$FORM{'mv_id'},$FORM{'mr_id'}) or die $dbh->errstr;
											$sth_map_ins->finish;
										}
									}else{
										die &Encode::decode_utf8('編集不可の為、編集できません') if($mv_frozen);
										die &Encode::decode_utf8('公開中の為、編集できません') if($mv_publish);
									}
								}
							}

						}
					}
				}
				if(defined $data->{'set_same_use_setting_mirror_part'} && $data->{'set_same_use_setting_mirror_part'}){
					my $target_art_id;
					my $is_mirror_id;
					if($art_id =~ /^([A-Z]+[0-9]+)(M*)/){
						$target_art_id = $1;
						$is_mirror_id = $2;
					}
					if(defined $target_art_id){
						$target_art_id .= 'M' unless($is_mirror_id);
print $LOG __LINE__,":\$target_art_id=[$target_art_id]\n";
						$sth_map_upd_set_mirror->execute($data->{'cm_use'},$target_art_id,$FORM{'ci_id'},$FORM{'cb_id'},$FORM{'md_id'},$FORM{'mv_id'},$FORM{'mr_id'},$data->{'cm_use'}) or die $dbh->errstr;
						my $rows = $sth_map_upd_set_mirror->rows();
						$sth_map_upd_set_mirror->finish;
						print $LOG __LINE__,qq|:\$rows=[$rows]\n|;
					}
				}


			}
			undef $sth_arta_sel;

			#$epocsec = &Time::HiRes::tv_interval($t0);
			#($sec,$min) = localtime($epocsec);
			&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

			my %ART_IDS;
			foreach my $data (@$datas){
				my $art_id = (exists $data->{'art_id'} && defined $data->{'art_id'}) ? $data->{'art_id'} : undef;
				next unless(defined $art_id);
				$ART_IDS{$art_id} = undef;
				if(defined $data->{'mirror'} && $data->{'mirror'}){
					my $mirror_art_id = $1.'M' if($art_id =~ /^([A-Z]+[0-9]+)/);
					undef $mirror_art_id if(defined $mirror_art_id && $mirror_art_id eq $art_id);
					next unless(defined $mirror_art_id);
					$ART_IDS{$mirror_art_id} = undef;
				}
				if(defined $data->{'set_same_use_setting_mirror_part'} && $data->{'set_same_use_setting_mirror_part'} eq 'true'){
					my $target_art_id;
					my $is_mirror_id;
					if($art_id =~ /^([A-Z]+[0-9]+)(M*)/){
						$target_art_id = $1;
						$is_mirror_id = $2;
					}
					if(defined $target_art_id){
						$target_art_id .= 'M' unless($is_mirror_id);
						$ART_IDS{$target_art_id} = undef;
					}
				}
			}

			#$epocsec = &Time::HiRes::tv_interval($t0);
			#($sec,$min) = localtime($epocsec);
			&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

			if(scalar keys(%ART_IDS) > 0){
				&BITS::ConceptArtMapModified::exec(
					dbh => $dbh,
					ci_id => $FORM{'ci_id'},
					cb_id => $FORM{'cb_id'},
					md_id => $FORM{'md_id'},
					mv_id => $FORM{'mv_id'},
					mr_id => $FORM{'mr_id'},
					art_ids => [keys(%ART_IDS)],
					LOG => $LOG
				);

				#$epocsec = &Time::HiRes::tv_interval($t0);
				#($sec,$min) = localtime($epocsec);
				&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

#				my @P = map {'?'} keys(%ART_IDS);
				my $sql_history_art_file_info_sel  = sprintf(qq|
select distinct
 artg_id
from
  (select * from history_art_file_info where (art_id,artg_id,hist_serial) in (select art_id,artg_id,max(hist_serial) from history_art_file_info group by art_id,artg_id)) as arti
where
 art_delcause is null
 and (hist_event) in (
  select distinct he_id from history_event where he_name in ('INSERT','UPDATE')
 )
 and art_id in (%s)
|,join(',',map {'?'} keys(%ART_IDS)));
				print $LOG __LINE__.':'.$sql_history_art_file_info_sel."\n";
				print $LOG __LINE__.':'.join(',',keys(%ART_IDS))."\n";
				my $sth_history_art_file_info_sel  = $dbh->prepare($sql_history_art_file_info_sel) or die $dbh->errstr;

				$sth_history_art_file_info_sel->execute(keys(%ART_IDS)) or die $dbh->errstr;
				my $rows = $sth_history_art_file_info_sel->rows();
				my %ARTG_IDS;
				my $artg_id;
				if($rows>0){
					my $column_number = 0;
					$sth_history_art_file_info_sel->bind_col(++$column_number, \$artg_id, undef);
					while($sth_history_art_file_info_sel->fetch){
						$ARTG_IDS{$artg_id} = undef if(defined $artg_id);
					}
				}
				$sth_history_art_file_info_sel->finish;
				undef $sth_history_art_file_info_sel;
				undef $sql_history_art_file_info_sel;

				#$epocsec = &Time::HiRes::tv_interval($t0);
				#($sec,$min) = localtime($epocsec);
				&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

				if(scalar keys(%ARTG_IDS)){
					print $LOG __LINE__.':'.join(',',(sort {$a<=>$b} keys(%ARTG_IDS)))."\n";

				my $sql_art_group_sel  = sprintf(qq|
select
 artg.artg_id,
 COALESCE(art_count,0),
 COALESCE(map_count,0),
 COALESCE(chk_count,0),
 COALESCE(use_map_count,0)
from
 art_group as artg
left join (
  select
   artg_id,
   count(artg_id) as art_count
  from (
    select distinct
     artg_id,
     harti.art_id
    from
      (select artg_id,art_id,art_delcause,hist_event from history_art_file_info where (art_id,artg_id,hist_serial) in (select art_id,artg_id,max(hist_serial) from history_art_file_info group by art_id,artg_id)) as harti
    left join (select art_id from art_file_info where art_delcause is null) as arti on (arti.art_id=harti.art_id)
    where
     art_delcause is null
     and (hist_event) in (
      select distinct he_id from history_event where he_name in ('INSERT','UPDATE')
     )
     and arti.art_id is not null
  ) as a
  group by
   artg_id
) as f on (f.artg_id=artg.artg_id)

left join (
  select artg_id,count(artg_id) as map_count from (
    select
      artg_id,
      harti.art_id,
      count(map.cdi_id)
    from
      (select artg_id,art_id,art_delcause,hist_event from history_art_file_info where (art_id,artg_id,hist_serial) in (select art_id,artg_id,max(hist_serial) from history_art_file_info group by art_id,artg_id)) as harti
    left join (
      select * from concept_art_map where cm_delcause is null
    ) as map on map.art_id=harti.art_id
    left join (select art_id from art_file_info where art_delcause is null) as arti on (arti.art_id=harti.art_id)
    where
      map.cm_delcause is null and
      harti.art_delcause is null and
      (harti.hist_event) in (
        select distinct he_id from history_event where he_name in ('INSERT','UPDATE')
      )
     and arti.art_id is not null
    group by
      artg_id,
      harti.art_id
    HAVING
      count(map.cdi_id)=0
  ) as a group by artg_id
) as m on (m.artg_id=artg.artg_id)

left join (
  select
   artg_id,
   count(artg_id) as chk_count
  from (
    select distinct
     artg_id,
     harti.art_id
    from
      (select artg_id,art_id,art_delcause,hist_event from history_art_file_info where (art_id,artg_id,hist_serial) in (select art_id,artg_id,max(hist_serial) from history_art_file_info group by art_id,artg_id)) as harti
    left join (
       select * from art_annotation
     ) as arta on
        arta.art_id=harti.art_id
    left join (select art_id from art_file_info where art_delcause is null) as arti on (arti.art_id=harti.art_id)
    where
     art_delcause is null and
     arta.art_comment is null and
     arta.art_category is null and
     arta.art_judge is null and
     arta.art_class is null and
     (hist_event) in (
       select distinct he_id from history_event where he_name in ('INSERT','UPDATE')
     )
     and arti.art_id is not null
  ) as a
  group by
   artg_id
) as c on (c.artg_id=artg.artg_id)
left join (
  select artg_id,count(artg_id) as use_map_count from (
    select
      artg_id,
      harti.art_id,
      count(map.cdi_id)
    from
      (select artg_id,art_id,art_delcause,hist_event from history_art_file_info where (art_id,artg_id,hist_serial) in (select art_id,artg_id,max(hist_serial) from history_art_file_info group by art_id,artg_id)) as harti
    left join (
      select * from concept_art_map where cm_delcause is null
    ) as map on map.art_id=harti.art_id
    left join (select art_id from art_file_info where art_delcause is null) as arti on (arti.art_id=harti.art_id)
    where
      map.cm_use and
      map.cm_delcause is null and
      harti.art_delcause is null and
      (harti.hist_event) in (
        select distinct he_id from history_event where he_name in ('INSERT','UPDATE')
      )
     and arti.art_id is not null
    group by
      artg_id,
      harti.art_id
    HAVING
      count(map.cdi_id)!=0
  ) as a group by artg_id
) as u on (u.artg_id=artg.artg_id)

where
 atrg_use and
 artg_delcause is null
 and artg.artg_id in (%s)
|,join(',',map {'?'} keys(%ARTG_IDS)));
					print $LOG __LINE__.':'.$sql_art_group_sel."\n";
					print $LOG __LINE__.':'.join(',',keys(%ARTG_IDS))."\n";
					my $sth_art_group_sel  = $dbh->prepare($sql_art_group_sel) or die $dbh->errstr;


					my $sth_all_cm_count = $dbh->prepare('select mv_name_e,mv_order from concept_art_map as cm left join (select * from model_version) as mv on (cm.md_id=mv.md_id and cm.mv_id=mv.mv_id) where cm_use and cm_delcause is null and art_id in (select art_id from history_art_file_info where artg_id=? and hist_event in (select distinct he_id from history_event where he_name in (\'INSERT\',\'UPDATE\'))) group by mv_name_e,mv_order order by mv_order') or die $dbh->errstr;

					$sth_art_group_sel->execute(keys(%ARTG_IDS)) or die $dbh->errstr;
					my $rows = $sth_art_group_sel->rows();
					my $artg_id;
					my $art_count;
					my $map_count;
					my $chk_count;
					my $use_map_count;
					if($rows>0){
						my $column_number = 0;
						$sth_art_group_sel->bind_col(++$column_number, \$artg_id, undef);
						$sth_art_group_sel->bind_col(++$column_number, \$art_count, undef);
						$sth_art_group_sel->bind_col(++$column_number, \$map_count, undef);
						$sth_art_group_sel->bind_col(++$column_number, \$chk_count, undef);
						$sth_art_group_sel->bind_col(++$column_number, \$use_map_count, undef);
						while($sth_art_group_sel->fetch){

							$sth_all_cm_count->execute($artg_id) or die $dbh->errstr;
							my $all_cm_count = $sth_all_cm_count->rows();
							my $all_cm_count_mv_name_e = [];
							if($all_cm_count>0){
								my $mv_name_e;
								$column_number = 0;
								$sth_all_cm_count->bind_col(++$column_number, \$mv_name_e, undef);
								while($sth_all_cm_count->fetch){
									push(@$all_cm_count_mv_name_e,$mv_name_e) if(defined $mv_name_e && length $mv_name_e);
								}
							}
							$sth_all_cm_count->finish;


							push(@{$DATAS->{'datas'}},{
								artg_id        => $artg_id + 0,
								art_count      => $art_count + 0,
								nomap_count    => $map_count + 0,
								nochk_count    => $chk_count + 0,
								use_map_count  => $use_map_count + 0,
								all_cm_map_versions => $all_cm_count_mv_name_e,
							});
						}
						$DATAS->{'total'} = scalar @{$DATAS->{'datas'}};
					}
					$sth_art_group_sel->finish;
					undef $sth_art_group_sel;
					undef $sql_art_group_sel;

				}
				undef %ARTG_IDS;
			}
			undef %ART_IDS;

			#$epocsec = &Time::HiRes::tv_interval($t0);
			#($sec,$min) = localtime($epocsec);
			&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

			$dbh->commit();
			$dbh->do("NOTIFY art_file");
			$dbh->do("NOTIFY concept_art_map");
#			$dbh->rollback;

			$DATAS->{'success'} = JSON::XS::true;
		};
		if($@){
			print $LOG __LINE__,":",$@,"\n";
			$DATAS->{'msg'} = $@;
			&utf8::decode($DATAS->{'msg'}) unless(&Encode::is_utf8($DATAS->{'msg'}));

			$dbh->rollback;
		}
		$dbh->{'AutoCommit'} = 1;
		$dbh->{'RaiseError'} = 0;

	}else{
		$DATAS->{'msg'} = qq|JSON形式が違います|;
		&utf8::decode($DATAS->{'msg'}) unless(&Encode::is_utf8($DATAS->{'msg'}));
	}
}

elsif($FORM{'cmd'} eq 'update_concept_art_map'){

#	$DATAS->{'success'} = JSON::XS::false;
#	&gzip_json($DATAS);
#	exit;

	unless(
		exists $FORM{'md_id'} && defined $FORM{'md_id'} &&
		exists $FORM{'mv_id'} && defined $FORM{'mv_id'} &&
		exists $FORM{'mr_id'} && defined $FORM{'mr_id'} &&
		exists $FORM{'ci_id'} && defined $FORM{'ci_id'} &&
		exists $FORM{'cb_id'} && defined $FORM{'cb_id'} &&
		exists $FORM{'datas'} && defined $FORM{'datas'}
	){
		$DATAS->{'msg'} = qq|JSON形式が違います|;
		&utf8::decode($DATAS->{'msg'}) unless(&Encode::is_utf8($DATAS->{'msg'}));
		&gzip_json($DATAS);
		exit;
	}


	my $datas = &cgi_lib::common::decodeJSON($FORM{'datas'});
	if(defined $datas && ref $datas eq 'ARRAY'){
		$dbh->{'AutoCommit'} = 0;
		$dbh->{'RaiseError'} = 1;
		eval{
			my $md_id = $FORM{'md_id'};
			my $mv_id = $FORM{'mv_id'};

			my $sth_model_version = $dbh->prepare(qq|select mv_publish,mv_frozen from model_version where md_id=$md_id AND mv_id=$mv_id|) or die $dbh->errstr;
			$sth_model_version->execute() or die $dbh->errstr;
			my $column_number = 0;
			my $mv_publish;
			my $mv_frozen;
			$sth_model_version->bind_col(++$column_number, \$mv_publish, undef);
			$sth_model_version->bind_col(++$column_number, \$mv_frozen, undef);
			$sth_model_version->fetch;
			$sth_model_version->finish;
			undef $sth_model_version;
			die &Encode::decode_utf8('公開中の為、編集できません') if($mv_publish);
			die &Encode::decode_utf8('編集不可の為、編集できません') if($mv_frozen);

			my $mr_id = $FORM{'mr_id'};
			my $ci_id = $FORM{'ci_id'};
			my $cb_id = $FORM{'cb_id'};
			my $comment = $FORM{'comment'} || 'FMA対応モードにて削除';
			$comment = &Encode::decode_utf8($comment) unless(&Encode::is_utf8($comment));

			my $openid = qq|system|;
			my $sth_map_sel_1  = $dbh->prepare(qq|select cdi_id,cm_use,cmp_id from concept_art_map where art_id=? and ci_id=$ci_id and cb_id=$cb_id and md_id=$md_id and mv_id=$mv_id and mr_id=$mr_id|) or die $dbh->errstr;
			my $sth_map_sel_2  = $dbh->prepare(qq|select cdi_id,cm_use,cmp_id from concept_art_map where cdi_id=? and art_id=? and ci_id=$ci_id and cb_id=$cb_id and md_id=$md_id and mv_id=$mv_id and mr_id=$mr_id|) or die $dbh->errstr;

			my $sth_map_ins  = $dbh->prepare(qq|insert into concept_art_map (cm_use,cmp_id,cdi_id,art_id,ci_id,cb_id,md_id,mv_id,mr_id,cm_entry,cm_openid) values (?,?,?,?,$ci_id,$cb_id,$md_id,$mv_id,$mr_id,now(),'$openid')|) or die $dbh->errstr;

			my $sth_map_upd_1  = $dbh->prepare(qq|update concept_art_map set cm_use=?,cmp_id=?,cdi_id=?,cm_entry=now() where art_id=? and ci_id=$ci_id and cb_id=$cb_id and md_id=$md_id and mv_id=$mv_id and mr_id=$mr_id|) or die $dbh->errstr;
			my $sth_map_upd_2  = $dbh->prepare(qq|update concept_art_map set cm_use=?,cmp_id=?,cm_entry=now() where cdi_id=? and art_id=? and ci_id=$ci_id and cb_id=$cb_id and md_id=$md_id and mv_id=$mv_id and mr_id=$mr_id|) or die $dbh->errstr;

			my $sth_map_del_1  = $dbh->prepare(qq|delete from concept_art_map where art_id=? and ci_id=$ci_id and cb_id=$cb_id and md_id=$md_id and mv_id=$mv_id and mr_id=$mr_id RETURNING cm_entry|) or die $dbh->errstr;
			my $sth_map_del_2  = $dbh->prepare(qq|delete from concept_art_map where cdi_id=? and art_id=? and ci_id=$ci_id and cb_id=$cb_id and md_id=$md_id and mv_id=$mv_id and mr_id=$mr_id RETURNING cm_entry|) or die $dbh->errstr;

			my $sth_hmap_upd = $dbh->prepare(qq|update history_concept_art_map set cm_comment=? where art_id=? and ci_id=$ci_id and cb_id=$cb_id and md_id=$md_id and mv_id=$mv_id and mr_id=$mr_id and cm_entry=? and hist_event=(select he_id from history_event where he_name='DELETE')|) or die $dbh->errstr;
			my $sth_cdi_sel  = $dbh->prepare(qq|select cdi_id from concept_data_info where ci_id=$ci_id AND cdi_name=?|) or die $dbh->errstr;

			my $sth_history_art_file_info_sel  = $dbh->prepare(qq|select artg_id from history_art_file_info where art_id=?|) or die $dbh->errstr;

			my %ART_IDS;
			my $hash_artg_id;
			foreach my $data (@$datas){
				my $art_id = (exists $data->{'art_id'} && defined $data->{'art_id'}) ? $data->{'art_id'} : undef;
				next unless(defined $art_id);
				$ART_IDS{$art_id} = undef;

				my $cdi_name = (exists $data->{'cdi_name'} && defined $data->{'cdi_name'} && length $data->{'cdi_name'}) ? $data->{'cdi_name'} : undef;
				my $cm_use = (exists $data->{'cm_use'} && defined $data->{'cm_use'} && $data->{'cm_use'} == JSON::XS::true) ? 'true' : 'false';
				my $cmp_id = (exists $data->{'cmp_id'} && defined $data->{'cmp_id'}) ? $data->{'cmp_id'}-0 : 0;

				my $cdi_id;
				my $column_number;
				if(defined $cdi_name){
					$sth_cdi_sel->execute($cdi_name) or die $dbh->errstr;
					$column_number = 0;
					$sth_cdi_sel->bind_col(++$column_number, \$cdi_id, undef);
					$sth_cdi_sel->fetch;
					$sth_cdi_sel->finish;
				}

				my $sel_rows = 0;
				my $map_cdi_id;
				my $map_cm_use;
				my $map_cmp_id;
				if(0 && defined $cdi_id){
					$sth_map_sel_2->execute($cdi_id,$art_id) or die $dbh->errstr;
					$sel_rows = $sth_map_sel_2->rows();
					$column_number = 0;
					$sth_map_sel_2->bind_col(++$column_number, \$map_cdi_id, undef);
					$sth_map_sel_2->bind_col(++$column_number, \$map_cm_use, undef);
					$sth_map_sel_2->bind_col(++$column_number, \$map_cmp_id, undef);
					$sth_map_sel_2->fetch;
					$sth_map_sel_2->finish;
				}else{
					$sth_map_sel_1->execute($art_id) or die $dbh->errstr;
					$sel_rows = $sth_map_sel_1->rows();
					$column_number = 0;
					$sth_map_sel_1->bind_col(++$column_number, \$map_cdi_id, undef);
					$sth_map_sel_1->bind_col(++$column_number, \$map_cm_use, undef);
					$sth_map_sel_1->bind_col(++$column_number, \$map_cmp_id, undef);
					$sth_map_sel_1->fetch;
					$sth_map_sel_1->finish;
				}
				if(defined $map_cm_use){
					$map_cm_use = $map_cm_use ? 'true' : 'false';
				}else{
					$map_cm_use = '';
				}
				if(defined $map_cmp_id){
					$map_cmp_id -= 0;
				}else{
					$map_cmp_id = 0;
				}

				if($sel_rows>0){
					unless(defined $cdi_id && $cm_use eq 'true'){
						$sth_map_del_1->execute($art_id) or die $dbh->errstr;
						my $del_rows = $sth_map_del_1->rows();
						my $cm_entry;
						if($del_rows>0){
							my $column_number = 0;
							$sth_map_del_1->bind_col(++$column_number, \$cm_entry, undef);
							$sth_map_del_1->fetch;
						}
						$sth_map_del_1->finish;

						if(defined $cm_entry){
							#削除レコードにコメントを追加
							$sth_hmap_upd->execute($comment,$art_id,$cm_entry) or die $dbh->errstr;
							$sth_hmap_upd->finish;
						}
					}else{
						unless(defined $cdi_id && $cdi_id eq $map_cdi_id && $cm_use eq $map_cm_use && $cmp_id == $map_cmp_id){
							$sth_map_upd_1->execute($cm_use,$cmp_id,$cdi_id,$art_id) or die $dbh->errstr;
							$sth_map_upd_1->finish;
						}
					}
				}
				elsif(defined $cdi_id){
					$sth_map_ins->execute($cm_use,$cmp_id,$cdi_id,$art_id) or die $dbh->errstr;
					$sth_map_ins->finish;
				}
=pod
				else{
					$sth_map_del->execute($art_id) or die $dbh->errstr;
					my $del_rows = $sth_map_del->rows();
					my $cm_entry;
					if($del_rows>0){
						my $column_number = 0;
						$sth_map_del->bind_col(++$column_number, \$cm_entry, undef);
						$sth_map_del->fetch;
					}
					$sth_map_del->finish;

					if(defined $cm_entry){
						#削除レコードにコメントを追加
						$sth_hmap_upd->execute($comment,$art_id,$cm_entry) or die $dbh->errstr;
						$sth_hmap_upd->finish;
					}
				}
=cut
				{
					$sth_history_art_file_info_sel->execute($art_id) or die $dbh->errstr;
					my $artg_id;
					$column_number = 0;
					$sth_history_art_file_info_sel->bind_col(++$column_number, \$artg_id, undef);
					while($sth_history_art_file_info_sel->fetch){
						$hash_artg_id->{$artg_id} = undef if(defined $artg_id);
						$artg_id = undef;
					}
					$sth_history_art_file_info_sel->finish;
				}

			}

			if(scalar keys(%ART_IDS) > 0){
				&BITS::ConceptArtMapModified::exec(
					dbh => $dbh,
					ci_id => $FORM{'ci_id'},
					cb_id => $FORM{'cb_id'},
					md_id => $FORM{'md_id'},
					mv_id => $FORM{'mv_id'},
					mr_id => $FORM{'mr_id'},
					art_ids => [keys(%ART_IDS)],
					LOG => $LOG
				);
			}

			$dbh->commit();
			$dbh->do("NOTIFY concept_art_map");
			$DATAS->{'success'} = JSON::XS::true;


			if(defined $hash_artg_id && ref $hash_artg_id eq 'HASH'){
				my $artg_ids = join(',',sort {$a<=>$b} keys(%$hash_artg_id));
my $sql=qq|
select
 artg.artg_id,
 COALESCE(map_count,0),
 COALESCE(use_map_count,0)
from
 art_group as artg
left join (
  select artg_id,count(artg_id) as map_count from (
    select
      artg_id,
      hart.art_id,
      count(map.cdi_id)
    from
      (select * from history_art_file_info where (art_id,artg_id,hist_serial) in (select art_id,artg_id,max(hist_serial) from history_art_file_info group by art_id,artg_id)) as hart
    left join (
      select * from concept_art_map where cm_delcause is null
    ) as map on map.art_id=hart.art_id
    where
      map.cm_delcause is null and
      hart.art_delcause is null and
      (hart.hist_event) in (
        select distinct he_id from history_event where he_name in ('INSERT','UPDATE')
      )
    group by
      artg_id,
      hart.art_id
    HAVING
      count(map.cdi_id)=0
  ) as a group by artg_id
) as m on (m.artg_id=artg.artg_id)
left join (
  select artg_id,count(artg_id) as use_map_count from (
    select
      artg_id,
      harti.art_id,
      count(map.cdi_id)
    from
      (select artg_id,art_id,art_delcause,hist_event from history_art_file_info where (art_id,artg_id,hist_serial) in (select art_id,artg_id,max(hist_serial) from history_art_file_info group by art_id,artg_id)) as harti
    left join (
      select * from concept_art_map where cm_delcause is null
    ) as map on map.art_id=harti.art_id
    left join (select art_id from art_file_info where art_delcause is null) as arti on (arti.art_id=harti.art_id)
    where
      map.cm_use and
      map.cm_delcause is null and
      harti.art_delcause is null and
      (harti.hist_event) in (
        select distinct he_id from history_event where he_name in ('INSERT','UPDATE')
      )
     and arti.art_id is not null
    group by
      artg_id,
      harti.art_id
    HAVING
      count(map.cdi_id)!=0
  ) as a group by artg_id
) as u on (u.artg_id=artg.artg_id)
where
 atrg_use and
 artg_delcause is null
 and artg.artg_id in ($artg_ids)
|;

				eval{
					my $sth_all_cm_count = $dbh->prepare('select mv_name_e,mv_order from concept_art_map as cm left join (select * from model_version) as mv on (cm.md_id=mv.md_id and cm.mv_id=mv.mv_id) where cm_use and cm_delcause is null and art_id in (select art_id from history_art_file_info where artg_id=? and hist_event in (select distinct he_id from history_event where he_name in (\'INSERT\',\'UPDATE\'))) group by mv_name_e,mv_order order by mv_order') or die $dbh->errstr;

					my $sth = $dbh->prepare($sql) or die $dbh->errstr;
					$sth->execute() or die $dbh->errstr;
					if($sth->rows>0){
						my $column_number = 0;
						my $artg_id;
						my $artg_name;
						my $artg_timestamp;
						my $atrg_use;
						my $artg_comment;
						my $artg_delcause;
						my $artg_entry;
						my $artg_openid;
						my $art_count;
						my $map_count;
						my $use_map_count;
						my $chk_count;
						my $artf_id;
						my $artf_name;
						$sth->bind_col(++$column_number, \$artg_id, undef);
						$sth->bind_col(++$column_number, \$map_count, undef);
						$sth->bind_col(++$column_number, \$use_map_count, undef);
						while($sth->fetch){

							$sth_all_cm_count->execute($artg_id) or die $dbh->errstr;
							my $all_cm_count = $sth_all_cm_count->rows();
							my $all_cm_count_mv_name_e = [];
							if($all_cm_count>0){
								my $mv_name_e;
								$column_number = 0;
								$sth_all_cm_count->bind_col(++$column_number, \$mv_name_e, undef);
								while($sth_all_cm_count->fetch){
									push(@$all_cm_count_mv_name_e,$mv_name_e) if(defined $mv_name_e && length $mv_name_e);
								}
							}
							$sth_all_cm_count->finish;

							push(@{$DATAS->{'art_group_datas'}},{
								artg_id        => $artg_id + 0,
								nomap_count    => $map_count + 0,
								use_map_count  => $use_map_count + 0,
								all_cm_map_versions => $all_cm_count_mv_name_e,
							});
						}
					}
					$sth->finish;
					undef $sth;

					$DATAS->{'art_group_total'} = scalar @{$DATAS->{'art_group_datas'}};
#					$DATAS->{'success'} = JSON::XS::true;
				};
				if($@){
#					print $LOG __LINE__,":",$@,"\n";
					$DATAS->{'msg'} = $@;
				}

			}

		};
		if($@){
			print $LOG __LINE__,":",$@,"\n";
			$DATAS->{'msg'} = $@;
			&utf8::decode($DATAS->{'msg'}) unless(&Encode::is_utf8($DATAS->{'msg'}));

			$dbh->rollback;
		}
		$dbh->{'AutoCommit'} = 1;
		$dbh->{'RaiseError'} = 0;

	}else{
		$DATAS->{'msg'} = qq|JSON形式が違います|;
		&utf8::decode($DATAS->{'msg'}) unless(&Encode::is_utf8($DATAS->{'msg'}));
	}
}
elsif($FORM{'cmd'} eq 'destroy'){

	unless(
		exists $FORM{'md_id'} && defined $FORM{'md_id'} &&
		exists $FORM{'mv_id'} && defined $FORM{'mv_id'} &&
		exists $FORM{'mr_id'} && defined $FORM{'mr_id'} &&
		exists $FORM{'ci_id'} && defined $FORM{'ci_id'} &&
		exists $FORM{'cb_id'} && defined $FORM{'cb_id'} &&
		exists $FORM{'datas'} && defined $FORM{'datas'}
	){
		$DATAS->{'msg'} = qq|JSON形式が違います|;
		&utf8::decode($DATAS->{'msg'}) unless(&Encode::is_utf8($DATAS->{'msg'}));
		&gzip_json($DATAS);
		exit;
	}


	my $datas = &cgi_lib::common::decodeJSON($FORM{'datas'});
	if(defined $datas && ref $datas eq 'ARRAY'){
		$dbh->{'AutoCommit'} = 0;
		$dbh->{'RaiseError'} = 1;
		eval{
=pod
			my $md_id = $FORM{'md_id'};
			my $mv_id = $FORM{'mv_id'};

			my $sth_model_version = $dbh->prepare(qq|select mv_publish,mv_frozen from model_version where md_id=$md_id AND mv_id=$mv_id|) or die $dbh->errstr;
			$sth_model_version->execute() or die $dbh->errstr;
			my $column_number = 0;
			my $mv_publish;
			my $mv_frozen;
			$sth_model_version->bind_col(++$column_number, \$mv_publish, undef);
			$sth_model_version->bind_col(++$column_number, \$mv_frozen, undef);
			$sth_model_version->fetch;
			$sth_model_version->finish;
			undef $sth_model_version;
			die &Encode::decode_utf8('公開中の為、編集できません') if($mv_publish);
			die &Encode::decode_utf8('編集不可の為、編集できません') if($mv_frozen);
=cut

			my $sth_all_cm_count = $dbh->prepare('select art_id from concept_art_map where cm_use and cm_delcause is null and art_id=?') or die $dbh->errstr;

#			my $sth_cm_select   = $dbh->prepare(qq|select md_id,mv_id,mv_publish,mv_frozen from model_version where (md_id,mv_id) in (select md_id,mv_id concept_art_map where cm_use and cm_delcause is null and art_id=?)|) or die $dbh->errstr;

			my $sth_arto_delete = $dbh->prepare(qq|delete from art_org_info where art_id=?|) or die $dbh->errstr;
			my $sth_arta_delete = $dbh->prepare(qq|delete from art_annotation where art_id=?|) or die $dbh->errstr;
			my $sth_arti_delete = $dbh->prepare(qq|delete from art_file_info where art_id=?|) or die $dbh->errstr;
			my $sth_art_delete  = $dbh->prepare(qq|delete from art_file where art_id=?|) or die $dbh->errstr;
#			my $sth_cm_delete   = $dbh->prepare(qq|delete from concept_art_map where art_id=?|) or die $dbh->errstr;

#			my $sth_artg_delete = $dbh->prepare(qq|delete from art_group where artg_id=?|) or die $dbh->errstr;

#			my %ART_IDS;

			foreach my $data (@$datas){
				my $art_id = (exists $data->{'art_id'} && defined $data->{'art_id'}) ? $data->{'art_id'} : undef;
				next unless(defined $art_id);

				$sth_all_cm_count->execute($art_id) or die $dbh->errstr;
				my $all_cm_count = $sth_all_cm_count->rows();
				$sth_all_cm_count->finish;
				next if($all_cm_count>0);

#				$ART_IDS{$art_id} = undef;

				$sth_arto_delete->execute($art_id) or die $dbh->errstr;
				$sth_arto_delete->finish;

				$sth_arta_delete->execute($art_id) or die $dbh->errstr;
				$sth_arta_delete->finish;

				$sth_arti_delete->execute($art_id) or die $dbh->errstr;
				$sth_arti_delete->finish;

				$sth_art_delete->execute($art_id) or die $dbh->errstr;
				$sth_art_delete->finish;

#				$sth_cm_delete->execute($art_id) or die $dbh->errstr;
#				$sth_cm_delete->finish;

			}

#			if(scalar keys(%ART_IDS) > 0){
#				&BITS::ConceptArtMapModified::exec(
#					dbh => $dbh,
#					ci_id => $FORM{'ci_id'},
#					cb_id => $FORM{'cb_id'},
#					md_id => $FORM{'md_id'},
#					mv_id => $FORM{'mv_id'},
#					mr_id => $FORM{'mr_id'},
#					art_ids => [keys(%ART_IDS)],
#					LOG => $LOG
#				);
#			}

			$dbh->commit();
			$dbh->do("NOTIFY art_file");
			$dbh->do("NOTIFY concept_art_map");
			$DATAS->{'success'} = JSON::XS::true;
		};
		if($@){
			print $LOG __LINE__,":",$@,"\n";
			$DATAS->{'msg'} = $@;
			&utf8::decode($DATAS->{'msg'}) unless(&Encode::is_utf8($DATAS->{'msg'}));

			$dbh->rollback;
		}
		$dbh->{'AutoCommit'} = 1;
		$dbh->{'RaiseError'} = 0;
	}else{
		$DATAS->{'msg'} = qq|JSON形式が違います|;
		&utf8::decode($DATAS->{'msg'}) unless(&Encode::is_utf8($DATAS->{'msg'}));
	}
}


#$epocsec = &Time::HiRes::tv_interval($t0);
#($sec,$min) = localtime($epocsec);
&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

#my $json = &cgi_lib::common::encodeJSON($DATAS);
#print $json;
&gzip_json($DATAS);
#print $LOG $json,"\n";
#print $LOG __LINE__,":",&Data::Dumper::Dumper($DATAS),"\n";

#$epocsec = &Time::HiRes::tv_interval($t0);
#($sec,$min) = localtime($epocsec);
&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

&cgi_lib::common::message(&cgi_lib::common::encodeJSON($DATAS,1), $LOG) if(defined $LOG);

close($LOG);

exit;

sub Truncated {
	my $v = shift;
	return undef unless(defined $v);
	my $rate = 100000;
	return int($v * $rate + 0.5) / $rate;
}

sub readFile {
	my $path = shift;
#	return undef unless(defined $path && -f $path);
	return undef unless(defined $path);
#	print __LINE__,":\$path=[$path]\n";
	my $rtn;
	my $IN;
	if(open($IN,$path)){
		my $old  = $/;
		undef $/;
		$rtn = <$IN>;
		$/ = $old;
		close($IN);
	}
	return $rtn;
}
