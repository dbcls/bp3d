#!/bp3d/local/perl/bin/perl

#
# 作成途中
#

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use FindBin;
use File::Path;
use JSON::XS;
#use Graphics::ColorObject;
#use Graphics::Color;
#use Graphics::Color::RGB;

use Clone;


use lib qq|$FindBin::Bin/../..|,qq|$FindBin::Bin/../../../lib|,qq|$FindBin::Bin/../../../../ag-common/lib|;

use Getopt::Long qw(:config posix_default no_ignore_case gnu_compat);
my $config = {
	db => 'bp3d',
	host => '127.0.0.1',
	port => '8543'
};
&Getopt::Long::GetOptions($config,qw/
	db|d=s
	host|h=s
	port|p=s
/) or exit 1;

$ENV{'AG_DB_NAME'} = $config->{'db'};
$ENV{'AG_DB_HOST'} = $config->{'host'};
$ENV{'AG_DB_PORT'} = $config->{'port'};

require "common.pl";
require "common_db.pl";
use cgi_lib::common;

=pod
CREATE TABLE view_representation_art (
 download              boolean,
 thumb                 text,
 model_component       text,
 representation_id     text,
 represented_concept   text,
 english_name          text,
 model                 text,
 compatibility_version text,
 serial                integer,
 filename              text,
 timestamp             timestamp without time zone,
 obj_xmin                  numeric(9,4),
 obj_xmax                  numeric(9,4),
 obj_ymin                  numeric(9,4),
 obj_ymax                  numeric(9,4),
 obj_zmin                  numeric(9,4),
 obj_zmax                  numeric(9,4),
 volume                numeric(9,4),
 cube_volume           numeric(10,4),
 entry                 timestamp without time zone,
 color                 text
);

INSERT INTO view_representation_art 
(
 download,
 thumb,
 model_component,
 representation_id,
 represented_concept,
 english_name,
 model,
 compatibility_version,
 serial,
 filename,
 timestamp,
 obj_xmin,
 obj_xmax,
 obj_ymin,
 obj_ymax,
 obj_zmin,
 obj_zmax,
 volume,
 cube_volume,
 entry,
 color
)

SELECT
  false::boolean            as download,
  mr_version||'/'||idp.prefix_char||'/'||substring(art.art_serial_char from 1 for 2)||'/'||substring(art.art_serial_char from 3 for 2)||'/'||art.art_id||'_16x16.gif' as thumb,
  repa.art_id                 as model_component,
  rep.rep_id                as representation_id,
  cdi.cdi_name              as represented_concept,
  cdi.cdi_name_e            as english_name,
  md.md_name_e              as model,
  mv.mv_name_e              as compatibility_version,
  repa.art_hist_serial as serial,
  art.art_name||art.art_ext             as filename,
  art.art_timestamp as timestamp,

  art.art_xmin                        as xmin,
  art.art_xmax                        as xmax,
  art.art_ymin                        as ymin,
  art.art_ymax                        as ymax,
  art.art_zmin                        as zmin,
  art.art_zmax                        as zmax,
  art.art_volume                      as volume,
  art.art_cube_volume                 as cube_volume,
  art.art_entry   as entry,
  COALESCE(cd.seg_color,bd.seg_color) as color


FROM
 representation AS rep


--LEFT JOIN concept_art_map AS cm ON cm.md_id=rep.md_id AND cm.mv_id=rep.mv_id AND cm.mr_id=rep.mr_id AND cm.cdi_id=rep.cdi_id

LEFT JOIN (
    SELECT *
    FROM representation_art
  ) repa ON repa.rep_id=rep.rep_id --AND repa.art_id=cm.art_id

LEFT JOIN (
 SELECT
  art_id,
  prefix_id,
  art_name,
  art_ext,
  art_timestamp,
  art_xmin,
  art_ymin,
  art_zmin,
  art_xmax,
  art_ymax,
  art_zmax,
  art_volume,
  art_cube_volume,
  art_entry,
  to_char( to_number(substring(art_id from '[0-9]+'),'FM9999999999'),'FM9999990000') as art_serial_char
 FROM
  art_file
) art ON art.art_id=repa.art_id


LEFT JOIN id_prefix AS idp on idp.prefix_id=art.prefix_id

LEFT JOIN concept_data_info AS cdi on cdi.ci_id=rep.ci_id AND cdi.cdi_id=rep.cdi_id

LEFT JOIN (
    SELECT model.md_id, model.md_name_e, model.md_name_j
    FROM model
  ) md ON md.md_id  = rep.md_id
LEFT JOIN (
    SELECT model_version.md_id, model_version.mv_id, model_version.mv_version, model_version.mv_name_e, model_version.mv_name_j
    FROM model_version
  ) mv ON mv.md_id = rep.md_id AND
          mv.mv_id = rep.mv_id
LEFT JOIN (
    SELECT md_id, mv_id, mr_id, mr_version
    FROM model_revision
  ) mr ON mr.md_id = rep.md_id AND
          mr.mv_id = rep.mv_id AND
          mr.mr_id = rep.mr_id

LEFT JOIN (
 SELECT ci_id, cb_id, cdi_id, seg_color, seg_thum_bgcolor
 FROM concept_data as cd
 LEFT JOIN (
  SELECT seg_id, seg_color, seg_thum_bgcolor
  FROM concept_segment
 ) cs ON cd.seg_id = cs.seg_id

) cd ON cd.ci_id = rep.ci_id AND
        cd.cb_id = rep.cb_id AND
        cd.cdi_id = rep.cdi_id

LEFT JOIN (
 SELECT md_id, mv_id, mr_id, cdi_id, seg_color, seg_thum_bgcolor
 FROM buildup_data as bd
 LEFT JOIN (
  SELECT seg_id, seg_color, seg_thum_bgcolor
  FROM concept_segment
 ) cs ON bd.seg_id = cs.seg_id

) bd ON bd.md_id = rep.md_id AND
        bd.mv_id = rep.mv_id AND
        bd.mr_id = rep.mr_id AND
        bd.cdi_id = rep.cdi_id

WHERE
 rep_primitive AND
 rep_delcause IS NULL AND
(
 rep.ci_id,
 rep.cb_id,
 rep.md_id,
 rep.mv_id,
 rep.mr_id,
 rep.bul_id,
 rep.cdi_id
) IN (
 SELECT
  ci_id,
  cb_id,
  md_id,
  mv_id,
  mr_id,
  bul_id,
  regexp_split_to_table(regexp_replace(regexp_replace(COALESCE(but_cids,''),'[^0-9]+$','')||','||cdi_id ,'^[^0-9]+',''),'[^0-9]+')::integer
 FROM
  buildup_tree_info
 WHERE
--  but_cids IS NOT NULL AND
  (
   ci_id,
   cb_id,
   cdi_id,
   md_id,
   mv_id,
   mr_id,
   bul_id
  ) IN (
   SELECT
    ci_id,
    cb_id,
    cdi_id,
    md_id,
    mv_id,
    mr_id,
    bul_id
   FROM
    representation
   WHERE
    rep_delcause is null
  )
)
;
=cut

my $dbh = &get_dbh();



$dbh->{AutoCommit} = 0;
$dbh->{RaiseError} = 1;
eval{
	my $table_name = 'view_representation_art';
	unless(&existsTable($table_name)){
		$dbh->do(qq|
CREATE TABLE view_representation_art (
 rep_id                text not null,
 download              boolean,
 thumb                 text,
 model_component       text not null,
 representation_id     text,
 represented_concept   text,
 english_name          text,
 model                 text,
 compatibility_version text,
 serial                integer,
 filename              text,
 timestamp             timestamp without time zone,
 obj_xmin                  numeric(9,4),
 obj_xmax                  numeric(9,4),
 obj_ymin                  numeric(9,4),
 obj_ymax                  numeric(9,4),
 obj_zmin                  numeric(9,4),
 obj_zmax                  numeric(9,4),
 volume                numeric(9,4),
 cube_volume           numeric(10,4),
 entry                 timestamp without time zone,
 color                 text,
 PRIMARY KEY (rep_id,model_component)
);
|) or die $dbh->errstr;
	}


	my $sql;
	my $sth;
	my $column_number;
	my $rep_id;
	my $REP;
	$sth = $dbh->prepare(qq|
SELECT
 rep_id
FROM
 representation AS rep
LEFT JOIN (
    SELECT
     md_id,
     mv_id,
     mv_use
    FROM
     model_version
  ) mv ON mv.md_id = rep.md_id AND
          mv.mv_id = rep.mv_id
WHERE
 rep_delcause IS NULL AND
 mv_use
|) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$column_number = 0;
	$sth->bind_col(++$column_number, \$rep_id, undef);
	while($sth->fetch){
		$REP->{$rep_id} = undef if(defined $rep_id);
	}
	$sth->finish;
	undef $sth;

	$sql=<<SQL;
SELECT
  false::boolean            as download,
  mr_version||'/'||idp.prefix_char||'/'||substring(art.art_serial_char from 1 for 2)||'/'||substring(art.art_serial_char from 3 for 2)||'/'||art.art_id||'_16x16.gif' as thumb,
  cm.art_id                 as model_component,
  rep.rep_id                as representation_id,
  cdi.cdi_name              as represented_concept,
  cdi.cdi_name_e            as english_name,
  md.md_name_e              as model,
  mv.mv_name_e              as compatibility_version,
  repa.art_hist_serial as serial,
  art.art_name||art.art_ext             as filename,
  art.art_timestamp as timestamp,

  art.art_xmin                        as obj_xmin,
  art.art_xmax                        as obj_xmax,
  art.art_ymin                        as obj_ymin,
  art.art_ymax                        as obj_ymax,
  art.art_zmin                        as obj_zmin,
  art.art_zmax                        as obj_zmax,
  art.art_volume                      as volume,
  art.art_cube_volume                 as cube_volume,
  art.art_entry   as entry,
  COALESCE(cd.seg_color,bd.seg_color) as color


FROM
 representation AS rep


LEFT JOIN concept_art_map AS cm ON cm.md_id=rep.md_id AND cm.mv_id=rep.mv_id AND cm.mr_id=rep.mr_id AND cm.cdi_id=rep.cdi_id
LEFT JOIN (
 SELECT
  art_id,
  prefix_id,
  art_name,
  art_ext,
  art_timestamp,
  art_xmin,
  art_ymin,
  art_zmin,
  art_xmax,
  art_ymax,
  art_zmax,
  art_volume,
  art_cube_volume,
  art_entry,
  to_char( to_number(substring(art_id from '[0-9]+'),'FM9999999999'),'FM9999990000') as art_serial_char
 FROM
  art_file
) art ON art.art_id=cm.art_id

LEFT JOIN (
    SELECT *
    FROM representation_art
  ) repa ON repa.rep_id=rep.rep_id AND repa.art_id=cm.art_id

LEFT JOIN id_prefix AS idp on idp.prefix_id=art.prefix_id

LEFT JOIN concept_data_info AS cdi on cdi.ci_id=rep.ci_id AND cdi.cdi_id=rep.cdi_id

LEFT JOIN (
    SELECT model.md_id, model.md_name_e, model.md_name_j
    FROM model
  ) md ON md.md_id  = rep.md_id
LEFT JOIN (
    SELECT model_version.md_id, model_version.mv_id, model_version.mv_version, model_version.mv_name_e, model_version.mv_name_j, model_version.mv_use
    FROM model_version
  ) mv ON mv.md_id = rep.md_id AND
          mv.mv_id = rep.mv_id
LEFT JOIN (
    SELECT md_id, mv_id, mr_id, mr_version
    FROM model_revision
  ) mr ON mr.md_id = rep.md_id AND
          mr.mv_id = rep.mv_id AND
          mr.mr_id = rep.mr_id

LEFT JOIN (
 SELECT ci_id, cb_id, cdi_id, seg_color, seg_thum_bgcolor
 FROM concept_data as cd
 LEFT JOIN (
  SELECT seg_id, seg_color, seg_thum_bgcolor
  FROM concept_segment
 ) cs ON cd.seg_id = cs.seg_id

) cd ON cd.ci_id = rep.ci_id AND
        cd.cb_id = rep.cb_id AND
        cd.cdi_id = rep.cdi_id

LEFT JOIN (
 SELECT md_id, mv_id, mr_id, cdi_id, seg_color, seg_thum_bgcolor
 FROM buildup_data as bd
 LEFT JOIN (
  SELECT seg_id, seg_color, seg_thum_bgcolor
  FROM concept_segment
 ) cs ON bd.seg_id = cs.seg_id

) bd ON bd.md_id = rep.md_id AND
        bd.mv_id = rep.mv_id AND
        bd.mr_id = rep.mr_id AND
        bd.cdi_id = rep.cdi_id

WHERE
 rep_primitive AND
 rep_delcause IS NULL AND
 mv.mv_use AND
(
 rep.ci_id,
 rep.cb_id,
 rep.md_id,
 rep.mv_id,
 rep.mr_id,
 rep.bul_id,
 rep.cdi_id
) IN (
 SELECT
  ci_id,
  cb_id,
  md_id,
  mv_id,
  mr_id,
  bul_id,
  regexp_split_to_table(regexp_replace(regexp_replace(COALESCE(but_cids,''),'[^0-9]+\$','')||','||cdi_id ,'^[^0-9]+',''),'[^0-9]+')::integer
 FROM
  buildup_tree_info
 WHERE
--  but_cids IS NOT NULL AND
  (
   ci_id,
   cb_id,
   cdi_id,
   md_id,
   mv_id,
   mr_id,
   bul_id
  ) IN (
   SELECT
    ci_id,
    cb_id,
    cdi_id,
    md_id,
    mv_id,
    mr_id,
    bul_id
   FROM
    representation
   WHERE
    rep_id=?
  )
)
SQL


	my $sql_cm=<<SQL;
SELECT
 art_id,
 art_hist_serial,
 cdi_id
FROM
 concept_art_map AS cm

WHERE
 cm_use AND
 cm_delcause IS NULL AND
(
 cm.md_id,
 cm.mv_id,
 cm.cdi_id
) IN (
 SELECT
  md_id,
  mv_id,
  regexp_split_to_table(regexp_replace(regexp_replace(COALESCE(but_cids,''),'[^0-9]+$','')||','||cdi_id ,'^[^0-9]+',''),'[^0-9]+')::integer
 FROM
  buildup_tree_info
 WHERE
  (
   ci_id,
   cb_id,
   cdi_id,
   md_id,
   mv_id,
   mr_id,
   bul_id
  ) IN (
   SELECT
    ci_id,
    cb_id,
    cdi_id,
    md_id,
    mv_id,
    mr_id,
    bul_id
   FROM
    representation
   WHERE
    rep_delcause is null
    AND rep_id=?
  )
)
GROUP BY
 cdi_id
;
SQL

	if(defined $REP && ref $REP eq 'HASH'){
		$sth = $dbh->prepare($sql) or die $dbh->errstr;

		my $sth_count = $dbh->prepare(qq|SELECT * FROM view_representation_art WHERE rep_id=?|) or die $dbh->errstr;
		my $sth_cm = $dbh->prepare($sql_cm) or die $dbh->errstr;
		my $sth_rep = $dbh->prepare(qq|SELECT * FROM representation WHERE rep_delcause IS NULL AND rep_id=?|) or die $dbh->errstr;

		my $sth_del = $dbh->prepare(qq|DELETE FROM view_representation_art WHERE rep_id=?|) or die $dbh->errstr;

		my $total = scalar keys(%$REP);
		my $count = 0;
		foreach my $rep_id (sort keys(%$REP)){
			$count++;

			$sth_count->execute($rep_id) or die $dbh->errstr;
			my $rows = $sth_count->rows();
			$sth_count->finish;

			$sth_rep->execute($rep_id) or die $dbh->errstr;
			my $rep_hash_ref = $sth_rep->fetchrow_hashref();
			$sth_rep->finish;
			next unless(defined $rep_hash_ref && ref $rep_hash_ref eq 'HASH');


			$sth_cm->execute($rep_id) or die $dbh->errstr;
			my $rows_cm = $sth_cm->rows();

			my $CHILD_IDS;
			my $art_id;
			my $art_hist_serial;
			my $cdi_id;
			$column_number = 0;
			$sth_cm->bind_col(++$column_number, \$art_id, undef);
			$sth_cm->bind_col(++$column_number, \$art_hist_serial, undef);
			$sth_cm->bind_col(++$column_number, \$cdi_id, undef);
			while($sth_cm->fetch){
				next unless(defined $art_id && defined $art_hist_serial && defined $cdi_id);
				$CHILD_IDS->{$art_id} = {
					art_id => $art_id,
					art_hist_serial => $art_hist_serial,
					cdi_id => $cdi_id,
					md_id  => $rep_hash_ref->{'md_id'},
					mv_id  => $rep_hash_ref->{'mv_id'},
					mr_id  => $rep_hash_ref->{'mr_id'},
					ci_id  => $rep_hash_ref->{'ci_id'},
					cb_id  => $rep_hash_ref->{'cb_id'},
					bul_id => $rep_hash_ref->{'bul_id'},
				};
			}
			$sth_cm->finish;

			next if($rows>0 && $rows==$rows_cm);

			if($rows_cm>0){
				$sth_del->execute($rep_id) or die $dbh->errstr;
				$sth_del->finish;
			}

			say STDERR sprintf("%s [%d/%d]",$rep_id,$count,$total);

			$sth->execute($rep_id) or die $dbh->errstr;
			while(my $hash_ref = $sth->fetchrow_hashref){

				next unless(exists $hash_ref->{'model_component'} && defined $hash_ref->{'model_component'} && length $hash_ref->{'model_component'});

				my $clone = &Clone::clone($hash_ref);
				$clone->{'rep_id'} = $rep_id;
#				push(@{$REP->{$rep_id}}, $clone);

				&cgi_lib::common::message($clone);

				my @C;
				my @V;
				my @B;
				foreach my $key (sort keys(%{$clone})){
					push(@C,$key);
					push(@B,'?');
					push(@V,$clone->{$key});
				}
				my $s = $dbh->prepare(sprintf("INSERT INTO view_representation_art (%s) VALUES (%s)",join(',',@C),join(',',@B))) or die $dbh->errstr;
				$s->execute(@V) or warn sprintf("%s [%s]", $dbh->errstr, join(',',@V));
				$s->finish;
				undef $s;
			}
			$sth->finish;

			$dbh->commit();
		}
		undef $sth;
		undef $sth_count;
		undef $sth_cm;
		undef $sth_del;
	}



	$dbh->commit();
};
if($@){
	print $@."\n";
	$dbh->rollback;
}
$dbh->{AutoCommit} = 1;
$dbh->{RaiseError} = 0;
