package AG::Representation;

use strict;
use warnings;
use feature ':5.10';
use DBD::Pg;

sub get_element {
	my $dbh = shift;
	my $rep_id = shift;
	my $LOG = shift;

	my $ALL_HASH_DATAS;

	my $sth_rep_mr = $dbh->prepare(qq|
select
 mr.mr_version,
 rep.md_id,
 rep.mv_id,
 rep.mr_id,
 rep.ci_id,
 rep.cb_id,
 rep.bul_id
from
 representation as rep

left join (
 select md_id,mv_id,mr_id,mr_version from model_revision
) as mr on
 mr.md_id=rep.md_id and
 mr.mv_id=rep.mv_id and
 mr.mr_id=rep.mr_id

where
 rep.rep_id=?
|) or die $dbh->errstr;

	my $md_id;
	my $mv_id;
	my $mr_id;
	my $ci_id;
	my $cb_id;
	my $bul_id;
	my $mr_version;

	$sth_rep_mr->execute($rep_id) or die $dbh->errstr;
	my $column_number = 0;
	$sth_rep_mr->bind_col(++$column_number, \$mr_version, undef);
	$sth_rep_mr->bind_col(++$column_number, \$md_id, undef);
	$sth_rep_mr->bind_col(++$column_number, \$mv_id, undef);
	$sth_rep_mr->bind_col(++$column_number, \$mr_id, undef);
	$sth_rep_mr->bind_col(++$column_number, \$ci_id, undef);
	$sth_rep_mr->bind_col(++$column_number, \$cb_id, undef);
	$sth_rep_mr->bind_col(++$column_number, \$bul_id, undef);
	$sth_rep_mr->fetch;
	$sth_rep_mr->finish;
	undef $sth_rep_mr;
=pod
	my $sth_but_cids = $dbh->prepare(qq|
select
 cdi_id,
 but_cids,
 ci_id,
 cb_id,
 bul_id
from
 buildup_tree
where
 but_delcause is null and
 (ci_id,cb_id,bul_id,cdi_id) in (
   select
    ci_id,
    cb_id,
    bul_id,
    cdi_id
   from
    representation
   where
    rep_delcause is null and
    rep_id=?
 )
|) or die $dbh->errstr;
=cut
	my $sth_but_cids = $dbh->prepare(qq|
select
 cdi_id,
 but_cids,
 ci_id,
 cb_id,
 bul_id
from
 buildup_tree_info
where
 but_delcause is null and
 (md_id,mv_id,mr_id,ci_id,cb_id,bul_id,cdi_id) in (
   select
    md_id,
    mv_id,
    mr_id,
    ci_id,
    cb_id,
    bul_id,
    cdi_id
   from
    representation
   where
    rep_delcause is null and
    rep_id=?
 )
|) or die $dbh->errstr;


	my %REP_IDS;
	my %CDI_IDS;

	my %BUT_CIDS;
	my %BUT_CIDS_EXC;
	my $cdi_id;
	my $but_cids;
	my $but_ci_id;
	my $but_cb_id;
	my $but_bul_id;
	$sth_but_cids->execute($rep_id) or die $dbh->errstr;
	$column_number = 0;
	$sth_but_cids->bind_col(++$column_number, \$cdi_id, undef);
	$sth_but_cids->bind_col(++$column_number, \$but_cids, undef);
	$sth_but_cids->bind_col(++$column_number, \$but_ci_id, undef);
	$sth_but_cids->bind_col(++$column_number, \$but_cb_id, undef);
	$sth_but_cids->bind_col(++$column_number, \$but_bul_id, undef);
	while($sth_but_cids->fetch){
		$but_cids = &cgi_lib::common::decodeJSON($but_cids);
		if(defined $but_cids && ref $but_cids eq 'ARRAY'){
			foreach my $but_cid (@$but_cids){
				$BUT_CIDS{$but_cid} = {
					ci_id => $but_ci_id,
					cb_id => $but_cb_id,
					bul_id => $but_bul_id
				};
			}
		}
		if(defined $cdi_id){
			$BUT_CIDS{$cdi_id} = {
				ci_id => $but_ci_id,
				cb_id => $but_cb_id,
				bul_id => $but_bul_id
			};
		}
	}
	$sth_but_cids->finish;
	say __PACKAGE__.':'.__FILE__.':'.__LINE__.':%BUT_CIDS='.(scalar keys(%BUT_CIDS)) unless(exists($ENV{'REQUEST_METHOD'}));


	if(scalar keys(%BUT_CIDS)){
		my $sql_rep_ids = qq|
 select
  rep_id,
  cdi_id,
  rep_primitive
 from
  representation
 where
  (md_id,mv_id,mr_id,cdi_id) in (
      select
       md_id,mv_id,max(mr_id) as mr_id,cdi_id
      from
       representation
      where
       md_id=? and mv_id=? and mr_id<=? and bul_id=? and cdi_id in (%s) and rep_delcause is null
      group by
       md_id,mv_id,cdi_id
   )
|;

		my $sth_rep_ids = $dbh->prepare(sprintf($sql_rep_ids,join(',',keys(%BUT_CIDS)))) or die $dbh->errstr;
		%BUT_CIDS = ();
		$sth_rep_ids->execute(
			$md_id,
			$mv_id,
			$mr_id,
			$bul_id,
		) or die $dbh->errstr;
		my $rep_rep_id;
		my $rep_cdi_id;
		my $rep_rep_primitive;
		$column_number = 0;
		$sth_rep_ids->bind_col(++$column_number, \$rep_rep_id, undef);
		$sth_rep_ids->bind_col(++$column_number, \$rep_cdi_id, undef);
		$sth_rep_ids->bind_col(++$column_number, \$rep_rep_primitive, undef);
		while($sth_rep_ids->fetch){
			$REP_IDS{$rep_rep_id} = $rep_rep_primitive if(defined $rep_rep_id);
			$BUT_CIDS{$rep_cdi_id} = $rep_rep_primitive if(defined $rep_cdi_id);
		}
		$sth_rep_ids->finish;
		undef $sth_rep_ids;
		undef $sql_rep_ids;
		undef $rep_rep_id;
		undef $rep_cdi_id;
		undef $rep_rep_primitive;

		say __PACKAGE__.':'.__FILE__.':'.__LINE__.':%BUT_CIDS='.(scalar keys(%BUT_CIDS)) unless(exists($ENV{'REQUEST_METHOD'}));
		say __PACKAGE__.':'.__FILE__.':'.__LINE__.':%REP_IDS='.(scalar keys(%REP_IDS)) unless(exists($ENV{'REQUEST_METHOD'}));
	}
	if(scalar keys(%BUT_CIDS)){
		my %CDI_IDS_EXC;
		my $sql_rep_ids_exclude = qq|
 select
  rep_id,
  cdi_id,
  rep_primitive
 from
  representation
 where
  (md_id,mv_id,mr_id,cdi_id) in (
      select
       md_id,mv_id,max(mr_id) as mr_id,cdi_id
      from
       representation
      where
       md_id=? and mv_id=? and mr_id<=? and bul_id<>? and cdi_id in (%s) and rep_delcause is null
      group by
       md_id,mv_id,cdi_id
   )
|;
		my $sth_rep_ids_exclude = $dbh->prepare(sprintf($sql_rep_ids_exclude,join(',',keys(%BUT_CIDS)))) or die $dbh->errstr;
		$sth_rep_ids_exclude->execute(
			$md_id,
			$mv_id,
			$mr_id,
			$bul_id,
		) or die $dbh->errstr;
		my $rep_rep_id;
		my $rep_cdi_id;
		my $rep_rep_primitive;
		$column_number = 0;
		$sth_rep_ids_exclude->bind_col(++$column_number, \$rep_rep_id, undef);
		$sth_rep_ids_exclude->bind_col(++$column_number, \$rep_cdi_id, undef);
		$sth_rep_ids_exclude->bind_col(++$column_number, \$rep_rep_primitive, undef);
		while($sth_rep_ids_exclude->fetch){
			$CDI_IDS_EXC{$rep_cdi_id} = undef if(defined $rep_cdi_id);
		}
		$sth_rep_ids_exclude->finish;

		undef $sth_rep_ids_exclude;
		undef $rep_rep_id;
		undef $rep_cdi_id;
		undef $rep_rep_primitive;

		say __PACKAGE__.':'.__FILE__.':'.__LINE__.':%CDI_IDS_EXC='.(scalar keys(%CDI_IDS_EXC)) unless(exists($ENV{'REQUEST_METHOD'}));
		if(scalar keys(%CDI_IDS_EXC)){
#			my $sth_but_cids_exclude = $dbh->prepare(sprintf(qq|select cdi_id,but_cids,ci_id,cb_id,bul_id from buildup_tree where but_delcause is null and ci_id=? and cb_id=? and bul_id<>? and cdi_id in (%s)|,keys(%CDI_IDS_EXC))) or die $dbh->errstr;
#			my $sth_but_cids_exclude = $dbh->prepare(sprintf(qq|select cdi_id,but_cids,ci_id,cb_id,bul_id from buildup_tree_info where but_delcause is null and ci_id=? and cb_id=? and bul_id<>? and cdi_id in (%s)|,keys(%CDI_IDS_EXC))) or die $dbh->errstr;
			my $sth_but_cids_exclude = $dbh->prepare(sprintf(qq|select cdi_id,but_cids,ci_id,cb_id,bul_id from buildup_tree_info where but_delcause is null and md_id=? and mv_id=? and mr_id=? and ci_id=? and cb_id=? and bul_id<>? and cdi_id in (%s)|,keys(%CDI_IDS_EXC))) or die $dbh->errstr;

			my $cdi_id;
			my $but_cids;
			my $but_ci_id;
			my $but_cb_id;
			my $but_bul_id;
			$sth_but_cids_exclude->execute(
				$md_id,
				$mv_id,
				$mr_id,
				$ci_id,
				$cb_id,
				$bul_id,
			) or die $dbh->errstr;
			my $column_number = 0;
			$sth_but_cids_exclude->bind_col(++$column_number, \$cdi_id, undef);
			$sth_but_cids_exclude->bind_col(++$column_number, \$but_cids, undef);
			$sth_but_cids_exclude->bind_col(++$column_number, \$but_ci_id, undef);
			$sth_but_cids_exclude->bind_col(++$column_number, \$but_cb_id, undef);
			$sth_but_cids_exclude->bind_col(++$column_number, \$but_bul_id, undef);
			while($sth_but_cids_exclude->fetch){
				$but_cids = &cgi_lib::common::decodeJSON($but_cids);
				if(defined $but_cids && ref $but_cids eq 'ARRAY'){
					foreach my $but_cid (@$but_cids){
						$BUT_CIDS_EXC{$but_cid} = {
							ci_id => $but_ci_id,
							cb_id => $but_cb_id,
							bul_id => $but_bul_id
						};
					}
				}
				if(defined $cdi_id){
					$BUT_CIDS_EXC{$cdi_id} = {
						ci_id => $but_ci_id,
						cb_id => $but_cb_id,
						bul_id => $but_bul_id
					};
				}
			}
			$sth_but_cids_exclude->finish;
			undef $sth_but_cids_exclude;
			say __PACKAGE__.':'.__FILE__.':'.__LINE__.':%BUT_CIDS_EXC='.(scalar keys(%BUT_CIDS_EXC)) unless(exists($ENV{'REQUEST_METHOD'}));


			my $sth_rep_ids_exclude = $dbh->prepare(sprintf($sql_rep_ids_exclude,join(',',keys(%BUT_CIDS_EXC)))) or die $dbh->errstr;
			$sth_rep_ids_exclude->execute(
				$md_id,
				$mv_id,
				$mr_id,
				$bul_id,
			) or die $dbh->errstr;
			my $rep_rep_id;
			my $rep_cdi_id;
			my $rep_rep_primitive;
			$column_number = 0;
			$sth_rep_ids_exclude->bind_col(++$column_number, \$rep_rep_id, undef);
			$sth_rep_ids_exclude->bind_col(++$column_number, \$rep_cdi_id, undef);
			$sth_rep_ids_exclude->bind_col(++$column_number, \$rep_rep_primitive, undef);
			while($sth_rep_ids_exclude->fetch){
				$REP_IDS{$rep_rep_id} = undef if(defined $rep_rep_id);
			}
			$sth_rep_ids_exclude->finish;

			undef $sth_rep_ids_exclude;
			undef $rep_rep_id;
			undef $rep_cdi_id;
			undef $rep_rep_primitive;

		}
		undef $sql_rep_ids_exclude;
	}

	say __PACKAGE__.':'.__FILE__.':'.__LINE__.':%REP_IDS='.(scalar keys(%REP_IDS)) unless(exists($ENV{'REQUEST_METHOD'}));

	if(scalar keys(%REP_IDS)){
		 my $sql_cm = qq|
select
 rep.md_id,
 rep.mv_id,
 rep.mr_id,
 rep.ci_id,
 rep.cb_id,
 rep.cdi_id,
 rep.cdi_name,
 rep.cdi_name_e,
 mr.mr_version,
 rep.rep_id,
 rep.bul_id,
 mv.mv_name_e,
 bul.bul_name_e,
 ci.ci_name,
 cb.cb_name,
 rep.rep_depth
from
 view_representation as rep

left join (
 select * from model_version
) as mv on
 mv.md_id=rep.md_id and
 mv.mv_id=rep.mv_id

left join (
 select * from model_revision
) as mr on
 mr.md_id=rep.md_id and
 mr.mv_id=rep.mv_id and
 mr.mr_id=rep.mr_id

left join (
 select * from buildup_logic
) as bul on
 bul.bul_id=rep.bul_id

left join (
 select * from concept_info
) as ci on
 ci.ci_id=rep.ci_id

left join (
 select * from concept_build
) as cb on
 cb.ci_id=rep.ci_id and
 cb.cb_id=rep.cb_id

where
 EXISTS (
  select
   1
  from
   concept_art_map as cm
  where
   cm.cm_use and
   cm.cm_delcause is null and
   rep.md_id=cm.md_id and
   rep.mv_id=cm.mv_id and
   rep.ci_id=cm.ci_id and
   rep.cb_id=cm.cb_id and
   rep.cdi_id=cm.cdi_id
 ) and
 rep_id in ('%s')
|;
		my $sth_cm = $dbh->prepare(sprintf($sql_cm,join("','",keys(%REP_IDS)))) or die $dbh->errstr;
		$sth_cm->execute() or die $dbh->errstr;
		my $rows = $sth_cm->rows();

		say __PACKAGE__.':'.__FILE__.':'.__LINE__.':$rows='.$rows unless(exists($ENV{'REQUEST_METHOD'}));
#			exit;
		say $LOG __PACKAGE__.':'.__FILE__.':'.__LINE__.':$rows='.$rows if(defined $LOG);

		my $cm_cb_id;
		my $cm_ci_id;
		my $cm_md_id;
		my $cm_mr_id;
		my $cm_mv_id;
		my $cm_cdi_id;
		my $cm_cdi_name;
		my $cm_cdi_name_e;
		my $cm_mr_version;

		my $rep_rep_id;
		my $rep_bul_id;

		my $mv_name_e;
		my $bul_name_e;
		my $ci_name;
		my $cb_name;
		my $rep_depth;



		my $column_number = 0;
		$sth_cm->bind_col(++$column_number, \$cm_md_id, undef);
		$sth_cm->bind_col(++$column_number, \$cm_mv_id, undef);
		$sth_cm->bind_col(++$column_number, \$cm_mr_id, undef);
		$sth_cm->bind_col(++$column_number, \$cm_ci_id, undef);
		$sth_cm->bind_col(++$column_number, \$cm_cb_id, undef);
		$sth_cm->bind_col(++$column_number, \$cm_cdi_id, undef);
		$sth_cm->bind_col(++$column_number, \$cm_cdi_name, undef);
		$sth_cm->bind_col(++$column_number, \$cm_cdi_name_e, undef);
		$sth_cm->bind_col(++$column_number, \$cm_mr_version, undef);
		$sth_cm->bind_col(++$column_number, \$rep_rep_id, undef);
		$sth_cm->bind_col(++$column_number, \$rep_bul_id, undef);
		$sth_cm->bind_col(++$column_number, \$mv_name_e, undef);
		$sth_cm->bind_col(++$column_number, \$bul_name_e, undef);
		$sth_cm->bind_col(++$column_number, \$ci_name, undef);
		$sth_cm->bind_col(++$column_number, \$cb_name, undef);
		$sth_cm->bind_col(++$column_number, \$rep_depth, undef);
		while($sth_cm->fetch){
			my $HASH = {
				md_id => $cm_md_id,
				mv_id => $cm_mv_id,
				mr_id => $cm_mr_id,
				ci_id => $cm_ci_id,
				cb_id => $cm_cb_id,
				cdi_name => $cm_cdi_name,
				cdi_name_e => $cm_cdi_name_e,
				mr_version => $cm_mr_version,
				rep_id => $rep_rep_id,
				bul_id => $rep_bul_id,

				mv_name_e => $mv_name_e,
				bul_name_e => $bul_name_e,
				ci_name => $ci_name,
				cb_name => $cb_name,
				rep_depth => $rep_depth,

				f_id => $cm_cdi_name,
				version => $cm_mr_version,
#								lng => $lng,
			};
			$ALL_HASH_DATAS->{$cm_cdi_name} = $HASH;
		}
		$sth_cm->finish;
		undef $sth_cm;


	}
	return $ALL_HASH_DATAS;
}

sub get_artfile_obj_format_data {
	my $PARAMS = shift // {};
	my $copyright = shift;

	my $LOG = $PARAMS->{'__LOG__'};
	my $type = $PARAMS->{type} // 'ARRAY';
#	my $type = $PARAMS->{type} // 'HASH';
	my $dbh = $PARAMS->{dbh};

	$copyright =~ s/\s*$//g if(defined $copyright);

	print $LOG __PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($PARAMS) if(defined $LOG);

	my $header_fmt = <<TEXT;
#
# Compatibility version : %s
# File ID : %s
# Representation ID : %s
# Build-up logic : %s %s %s
# Concept ID : %s
# English name : %s
# Bounds(mm): %s-%s
# Volume(cm3): %f
#
TEXT

	my $RTN;

	my $rep_ids;

	if(defined $PARAMS->{'rep_id'}){
		push(@$rep_ids,$PARAMS->{'rep_id'});
	}elsif(defined $PARAMS->{'rep_ids'}){
		push(@$rep_ids,@{$PARAMS->{'rep_ids'}});
	}

	my $ALL_ELEMENT_HASH_DATAS;
	if(defined $rep_ids && scalar @$rep_ids){
		foreach my $rep_id (@$rep_ids){
			my $ELEMENT_HASH_DATAS = &AG::Representation::get_element($dbh,$rep_id,$LOG);
			if(defined $ELEMENT_HASH_DATAS){
				foreach my $cdi_name (keys(%$ELEMENT_HASH_DATAS)){
					my $rep_id = $ELEMENT_HASH_DATAS->{$cdi_name}->{rep_id};
					$ALL_ELEMENT_HASH_DATAS->{$rep_id} = $ELEMENT_HASH_DATAS->{$cdi_name};
				}
			}
		}
	}
	if(defined $ALL_ELEMENT_HASH_DATAS){
		unless(exists($ENV{'REQUEST_METHOD'})){
			print STDERR __PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($ALL_ELEMENT_HASH_DATAS);
			say STDERR __PACKAGE__.':'.__LINE__.':$ALL_ELEMENT_HASH_DATAS='.(scalar keys(%$ALL_ELEMENT_HASH_DATAS));
		}

		my $sql=<<SQL;
select
 rep.rep_id,
 art.art_id,
 art.art_ext,
-- art.art_data,
 art.art_timestamp,
 art.art_xmin,
 art.art_xmax,
 art.art_ymin,
 art.art_ymax,
 art.art_zmin,
 art.art_zmax,
 art.art_volume
from
 representation_art as rep
left join (
 select rep_id,rep_depth from representation
) as rep2 on
  rep2.rep_id=rep.rep_id

left join (
  select
   art_id,
   art_ext,
   art_data,
   EXTRACT(EPOCH FROM art_timestamp) as art_timestamp,
   art_xmin,
   art_xmax,
   art_ymin,
   art_ymax,
   art_zmin,
   art_zmax,
   art_volume
  from
   art_file
) as art on
  art.art_id=rep.art_id
where
 rep.rep_id IN ('%s')
SQL

		my %exclusion_ids;
		if(defined $PARAMS->{'exclusion_ids'}){
			my $ids;
			if(ref $PARAMS->{'exclusion_ids'} eq 'ARRAY'){
				push(@$ids,@{$PARAMS->{'exclusion_ids'}});
			}elsif(length $PARAMS->{'exclusion_ids'}){
				eval{$ids = &JSON::XS::decode_json($PARAMS->{'exclusion_ids'});};
				push(@$ids,$PARAMS->{'exclusion_ids'}) unless(defined $ids);
	print $LOG __PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($ids) if(defined $LOG);
			}
			if(defined $ids && ref $ids eq 'ARRAY'){
				%exclusion_ids = map {$_=>undef} @$ids;
				$sql .= qq| and art.art_id not in ('| . join(qq|','|,@$ids) . qq|')|;
			}
		}

		if(defined $PARAMS->{'ids'}){
			my $ids;
			if(ref $PARAMS->{'ids'} eq 'ARRAY'){
				push(@$ids,@{$PARAMS->{'ids'}});
			}elsif(length $PARAMS->{'ids'}){
				eval{$ids = &JSON::XS::decode_json($PARAMS->{'ids'});};
				push(@$ids,$PARAMS->{'ids'}) unless(defined $ids);
			}
			if(defined $ids && ref $ids eq 'ARRAY'){
#				$sql .= qq| and art.art_id in ('| . join(qq|','|,grep {!exists $exclusion_ids{$_}} @$ids) . qq|')|;
				$sql .= qq| and art.art_id in ('| . join(qq|','|,@$ids) . qq|')|;
			}
		}
		$sql .= qq| order by rep2.rep_depth desc|;

		print $LOG __PACKAGE__.':'.__LINE__.':'.$sql if(defined $LOG);

		my $sth_data = $dbh->prepare(qq|select art_data from art_file where art_id=?|) or die $dbh->errstr;

		my $sth = $dbh->prepare(sprintf($sql,join("','",keys %$ALL_ELEMENT_HASH_DATAS))) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;

		my $rep_id;
		my $art_id;
		my $art_ext;
		my $art_data;
		my $art_entry;
		my $art_xmin;
		my $art_xmax;
		my $art_ymin;
		my $art_ymax;
		my $art_zmin;
		my $art_zmax;
		my $art_volume;

		my $column_number = 0;
		$sth->bind_col(++$column_number, \$rep_id, undef);
		$sth->bind_col(++$column_number, \$art_id, undef);
		$sth->bind_col(++$column_number, \$art_ext, undef);
#		$sth->bind_col(++$column_number, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
		$sth->bind_col(++$column_number, \$art_entry, undef);
		$sth->bind_col(++$column_number, \$art_xmin, undef);
		$sth->bind_col(++$column_number, \$art_xmax, undef);
		$sth->bind_col(++$column_number, \$art_ymin, undef);
		$sth->bind_col(++$column_number, \$art_ymax, undef);
		$sth->bind_col(++$column_number, \$art_zmin, undef);
		$sth->bind_col(++$column_number, \$art_zmax, undef);
		$sth->bind_col(++$column_number, \$art_volume, undef);

		my %use_art_id;

		while($sth->fetch){
#			next unless(defined $art_id && defined $art_ext && defined $art_data && defined $art_entry && defined $rep_id);
			next unless(defined $art_id && defined $art_ext && defined $art_entry && defined $rep_id);

			if(exists $use_art_id{$art_id}){
				unless(exists($ENV{'REQUEST_METHOD'})){
					say STDERR __PACKAGE__.':'.__LINE__.':exists=['.$art_id.']['.$rep_id.']['.$use_art_id{$art_id}.']';
				}
				next;
			}

			my $art_data;
			$sth_data->execute($art_id) or die $dbh->errstr;
			$sth_data->bind_col(1, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
			$sth_data->fetch;
			$sth_data->finish;
			unless(defined $art_data){
				unless(exists($ENV{'REQUEST_METHOD'})){
					say STDERR __PACKAGE__.':'.__LINE__.':None art_data';
				}
				next;
			}

			$use_art_id{$art_id} = $rep_id;

			my @HEAD;
			push @HEAD, $copyright if(defined $copyright);
			push @HEAD, sprintf($header_fmt,
									$ALL_ELEMENT_HASH_DATAS->{$rep_id}->{mv_name_e},
									$art_id,
									$rep_id,
									$ALL_ELEMENT_HASH_DATAS->{$rep_id}->{ci_name},
									$ALL_ELEMENT_HASH_DATAS->{$rep_id}->{cb_name},
									$ALL_ELEMENT_HASH_DATAS->{$rep_id}->{bul_name_e},
									$ALL_ELEMENT_HASH_DATAS->{$rep_id}->{cdi_name},
									$ALL_ELEMENT_HASH_DATAS->{$rep_id}->{cdi_name_e},
									sprintf("(%f,%f,%f)",$art_xmin,$art_ymin,$art_zmin),
									sprintf("(%f,%f,%f)",$art_xmax,$art_ymax,$art_zmax),
									$art_volume);
#			push @OUT, $art_data;

			if($type eq 'HASH'){
				$RTN->{$art_id} = {
					mv_name_e => $ALL_ELEMENT_HASH_DATAS->{$rep_id}->{mv_name_e},
					ci_name => $ALL_ELEMENT_HASH_DATAS->{$rep_id}->{ci_name},
					cb_name => $ALL_ELEMENT_HASH_DATAS->{$rep_id}->{cb_name},
					bul_name_e => $ALL_ELEMENT_HASH_DATAS->{$rep_id}->{bul_name_e},
					cdi_name => $ALL_ELEMENT_HASH_DATAS->{$rep_id}->{cdi_name},
					cdi_name_e => $ALL_ELEMENT_HASH_DATAS->{$rep_id}->{cdi_name_e},

					art_id => $art_id,
					rep_id => $rep_id,
					art_xmin => $art_xmin,
					art_ymin => $art_ymin,
					art_zmin => $art_zmin,
					art_xmax => $art_xmax,
					art_ymax => $art_ymax,
					art_zmax => $art_zmax,
					art_volume => $art_volume,
					art_ext => $art_ext,
					art_entry => $art_entry,

					head => join("\n",@HEAD),
					body => $art_data
				};
			}else{
				push @HEAD, $art_data;
				push @$RTN, join("\n",@HEAD);
			}
		}
		$sth->finish;
		undef $sth;
		undef $sth_data;

	}
	unless(exists($ENV{'REQUEST_METHOD'})){
		if(ref $RTN eq 'ARRAY'){
			say STDERR __PACKAGE__.':'.__LINE__.':$RTN='.(scalar @$RTN);
		}elsif(ref $RTN eq 'HASH'){
			say STDERR __PACKAGE__.':'.__LINE__.':$RTN='.(scalar keys %$RTN);
		}
	}
	return $RTN;
}

1;
