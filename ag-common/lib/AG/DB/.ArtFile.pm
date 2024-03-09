package AG::DB;

use strict;
use warnings;
use feature ':5.10';

use DBD::Pg;
use AG::Representation;

sub get_artfile_obj_format_data {
	my $self = shift;
	my $PARAMS = shift // {};
	my $copyright = shift;

	my $LOG = $PARAMS->{__LOG__};
	my $type = $PARAMS->{type} // 'ARRAY';

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

	my $RTN = [];
	my $dbh = $self->get_dbh();

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

		if(defined $PARAMS->{'ids'}){
			my $ids;
			eval{$ids = &JSON::XS::decode_json($PARAMS->{'ids'});};
			if(defined $ids && ref $ids eq 'ARRAY'){
				$sql .= qq| and art.art_id in ('| . join(qq|','|,@$ids) . qq|')|;
			}
		}
		$sql .= qq| order by rep2.rep_depth desc|;

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

			my @OUT;
			push @OUT, $copyright if(defined $copyright);
			push @OUT, sprintf($header_fmt,
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
			push @OUT, $art_data;

			if($type eq 'HASH'){
				$RTN->{$art_id} = {
					data => join("\n",@OUT)
				};
			}else{
				push @$RTN, join("\n",@OUT);
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

sub get_artfile_obj_format_data_old {
	my $self = shift;
	my $PARAMS = shift // {};
	my $copyright = shift;

	my $LOG = $PARAMS->{__LOG__};

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

	my $dbh = $self->get_dbh();

	my $art_id;
	my $art_ext;
	my $art_data;
	my $art_entry;
	my $ci_name;
	my $cb_name;
	my $bul_name;
	my $cdi_name;
	my $cdi_name_e;
	my $rep_id;
	my $art_xmin;
	my $art_xmax;
	my $art_ymin;
	my $art_ymax;
	my $art_zmin;
	my $art_zmax;
	my $art_volume;
	my $art_rep_id;
	my $art_cdi_name;
	my $art_cdi_name_e;
	my $art_mv_name_e;

	my $zip_prefix;

	my $sql=<<SQL;
select distinct
 art.art_id,
 art.art_ext,
 art.art_data,
 art.art_timestamp,
 ci.ci_name,
 cb.cb_name,
 bul.bul_name_e,
 cdi.cdi_name,
 cdi.cdi_name_e,
 rep.rep_id,
 art.art_xmin,
 art.art_xmax,
 art.art_ymin,
 art.art_ymax,
 art.art_zmin,
 art.art_zmax,
 art.art_volume,
 repa2.rep_id,
 repa2.cdi_name,
 repa2.cdi_name_e,
 repa2.mv_name_e
from
 representation_art as rep
left join (
  select
   art_id,
   art_ext,
   art_data,
   EXTRACT(EPOCH FROM art_timestamp) as art_timestamp,
   hist_serial,
   art_xmin,
   art_xmax,
   art_ymin,
   art_ymax,
   art_zmin,
   art_zmax,
   art_volume
  from
   history_art_file
) as art on
  art.art_id=rep.art_id and
  art.hist_serial=rep.art_hist_serial

left join (
  select rep_id,ci_id,cb_id,md_id,mv_id,mr_id,bul_id,cdi_id from representation
) as rep2 on
  rep2.rep_id=rep.rep_id

left join (
  select ci_id,cb_id,cdi_id,cd_name from concept_data
) as cd on
  cd.ci_id=rep2.ci_id and
  cd.cb_id=rep2.cb_id and
  cd.cdi_id=rep2.cdi_id

left join (
  select ci_id,cdi_id,cdi_name,cdi_name_e from concept_data_info
) as cdi on
  cdi.ci_id=cd.ci_id and
  cdi.cdi_id=cd.cdi_id

left join (
  select ci_id,ci_name from concept_info
) as ci on
  ci.ci_id=rep2.ci_id

left join (
  select ci_id,cb_id,cb_name from concept_build
) as cb on
  cb.ci_id=rep2.ci_id and
  cb.cb_id=rep2.cb_id

left join (
  select bul_id,bul_name_e from buildup_logic
) as bul on
  bul.bul_id=rep2.bul_id

LEFT JOIN (
    SELECT
     repa.art_id,
     repa.art_hist_serial,
     cdi.cdi_name,
     cdi.cdi_name_e,
     mv.mv_name_e,
     rep.rep_id,
     rep.ci_id,
     rep.cb_id,
     rep.md_id,
     rep.mv_id,
     rep.mr_id,
     rep.bul_id
    FROM
     (select * from view_concept_art_map where (md_id,mv_id,mr_id,ci_id,cb_id,cdi_id) in (select md_id,mv_id,max(mr_id) as mr_id,ci_id,cb_id,cdi_id from view_concept_art_map where cm_use and cm_delcause is null group by md_id,mv_id,ci_id,cb_id,cdi_id)) as repa
    LEFT JOIN (
        SELECT ci_id,cdi_id,cdi_name,cdi_name_e FROM concept_data_info
      ) cdi on
          cdi.ci_id=repa.ci_id AND 
          cdi.cdi_id=repa.cdi_id
    LEFT JOIN (
        SELECT md_id,mv_id,mv_name_e FROM model_version
      ) mv on
          mv.md_id=repa.md_id AND 
          mv.mv_id=repa.mv_id
    LEFT JOIN (
        SELECT rep_id,ci_id,cb_id,bul_id,md_id,mv_id,mr_id,cdi_id from representation where rep_delcause is null
      ) rep on
         rep.ci_id=repa.ci_id AND
         rep.cb_id=repa.cb_id AND
         rep.md_id=repa.md_id AND
         rep.mv_id=repa.mv_id AND
         rep.mr_id=repa.mr_id AND
         rep.cdi_id=repa.cdi_id
  ) repa2 ON
    repa2.ci_id = rep2.ci_id AND
    repa2.cb_id = rep2.cb_id AND
    repa2.md_id = rep2.md_id AND
    repa2.mv_id = rep2.mv_id AND
    repa2.mr_id = rep2.mr_id AND
    repa2.bul_id = rep2.bul_id AND
    repa2.art_id = rep.art_id AND
    repa2.art_hist_serial = rep.art_hist_serial

where
 rep.rep_id IN ('%s')
SQL


	my $rep_ids;

	if(defined $PARAMS->{'rep_id'}){
		push(@$rep_ids,$PARAMS->{'rep_id'});
	}elsif(defined $PARAMS->{'rep_ids'}){
		push(@$rep_ids,@{$PARAMS->{'rep_ids'}});
	}
	if(defined $rep_ids && scalar @$rep_ids){
		my $md_id;
		my $mv_id;
		my $mr_id;
		my $bul_id;
		my $params_rep_id;
		my $sql_rep = qq|select md_id,mv_id,mr_id,bul_id,rep_id from representation where rep_id in (|.(join(',',map {'?'} @$rep_ids)).')';
		my $sth_rep = $dbh->prepare($sql_rep) or die $dbh->errstr;

		my $sql_but_cids = qq|select cdi_id,but_cids from buildup_tree WHERE (ci_id,cb_id,bul_id,cdi_id) in (select ci_id,cb_id,bul_id,cdi_id from representation where rep_id=?)|;
		my $sth_but_cids = $dbh->prepare($sql_but_cids) or die $dbh->errstr;

		$sth_rep->execute(@$rep_ids) or die $dbh->errstr;
		my $column_number = 0;
		$sth_rep->bind_col(++$column_number, \$md_id, undef);
		$sth_rep->bind_col(++$column_number, \$mv_id, undef);
		$sth_rep->bind_col(++$column_number, \$mr_id, undef);
		$sth_rep->bind_col(++$column_number, \$bul_id, undef);
		$sth_rep->bind_col(++$column_number, \$params_rep_id, undef);
		while($sth_rep->fetch){

			my $cdi_id;
			my $but_cids;
			$sth_but_cids->execute($params_rep_id) or die $dbh->errstr;
			my $column_number = 0;
			$sth_but_cids->bind_col(++$column_number, \$cdi_id, undef);
			$sth_but_cids->bind_col(++$column_number, \$but_cids, undef);
			$sth_but_cids->fetch;
			$sth_but_cids->finish;

			if(defined $but_cids){
				eval{$but_cids = &JSON::XS::decode_json($but_cids);};
			}
			$but_cids = [] unless(defined $but_cids);
			push(@$but_cids,$cdi_id);

			my $sql_rep_ids = qq|
        select
         rep_id
        from
         representation
        where
         (md_id,mv_id,mr_id,bul_id,cdi_id) in (
           select
            md_id,mv_id,max(mr_id) as mr_id,bul_id,cdi_id
           from
            representation
           where
            bul_id<>? AND
            (md_id,mv_id,cdi_id) IN (
              select
               md_id,mv_id,cdi_id
              from
               representation
              where
               rep_id in (
                   select
                    rep_id
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
               )
              group by
               md_id,mv_id,cdi_id
            )
           group by
            md_id,mv_id,bul_id,cdi_id
         )
|;

#print $LOG __PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($but_cids) if(defined $LOG);
			my $sth_rep_ids = $dbh->prepare(sprintf($sql_rep_ids,join(",",@$but_cids))) or die $dbh->errstr;
#	print $LOG __PACKAGE__.':'.__LINE__,qq|:\$sql_rep_ids=[|.sprintf($sql_rep_ids,join(",",@$but_cids)).qq|]\n|;
			$sth_rep_ids->execute($bul_id,$md_id,$mv_id,$mr_id,$bul_id) or die $dbh->errstr;
			my $rep_id;
			$column_number = 0;
			$sth_rep_ids->bind_col(++$column_number, \$rep_id, undef);
			while($sth_rep_ids->fetch){
				push(@$rep_ids,$rep_id);
			}
			$sth_rep_ids->finish;
			undef $sth_rep_ids;

		}
		$sth_rep->finish;
		undef $sth_rep;
		undef $sth_but_cids;
	}


	if(defined $PARAMS->{'ids'}){
		my $ids;
		eval{$ids = &JSON::XS::decode_json($PARAMS->{'ids'});};
		if(defined $ids && ref $ids eq 'ARRAY'){
			$sql .= qq| and art.art_id in ('| . join(qq|','|,@$ids) . qq|')|;
		}
	}

#	print $LOG __PACKAGE__.':'.__LINE__,":\$sql=[$sql]\n";
#print $LOG __PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($rep_ids) if(defined $LOG);
	if(defined $rep_ids && scalar @$rep_ids){

		my %use_art_id;

		my %temp_rep_ids = map {$_=>undef} @$rep_ids;
#print $LOG __PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper(\%temp_rep_ids) if(defined $LOG);
say $LOG __PACKAGE__.':'.__LINE__.':'.(scalar keys(%temp_rep_ids)) if(defined $LOG);

#		my $sth = $dbh->prepare(sprintf($sql,join("','",@$rep_ids))) or die $dbh->errstr;
		my $sth = $dbh->prepare(sprintf($sql,join("','",keys %temp_rep_ids))) or die $dbh->errstr;

#		$sth->execute($PARAMS->{'rep_id'}) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
#		print $LOG __PACKAGE__.':'.__LINE__,":\$sth->rows()=[",$sth->rows(),"]\n";
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$art_id, undef);
		$sth->bind_col(++$column_number, \$art_ext, undef);
		$sth->bind_col(++$column_number, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
		$sth->bind_col(++$column_number, \$art_entry, undef);
		$sth->bind_col(++$column_number, \$ci_name, undef);
		$sth->bind_col(++$column_number, \$cb_name, undef);
		$sth->bind_col(++$column_number, \$bul_name, undef);
		$sth->bind_col(++$column_number, \$cdi_name, undef);
		$sth->bind_col(++$column_number, \$cdi_name_e, undef);
		$sth->bind_col(++$column_number, \$rep_id, undef);
		$sth->bind_col(++$column_number, \$art_xmin, undef);
		$sth->bind_col(++$column_number, \$art_xmax, undef);
		$sth->bind_col(++$column_number, \$art_ymin, undef);
		$sth->bind_col(++$column_number, \$art_ymax, undef);
		$sth->bind_col(++$column_number, \$art_zmin, undef);
		$sth->bind_col(++$column_number, \$art_zmax, undef);
		$sth->bind_col(++$column_number, \$art_volume, undef);
		$sth->bind_col(++$column_number, \$art_rep_id, undef);
		$sth->bind_col(++$column_number, \$art_cdi_name, undef);
		$sth->bind_col(++$column_number, \$art_cdi_name_e, undef);
		$sth->bind_col(++$column_number, \$art_mv_name_e, undef);
		while($sth->fetch){
			next unless(defined $art_id && defined $art_ext && defined $art_data && defined $art_entry && defined $cdi_name);

			next if(exists $use_art_id{$art_id});
			$use_art_id{$art_id} = undef;

			my @OUT;
			push @OUT, $copyright if(defined $copyright);
			push @OUT, sprintf($header_fmt,
									$art_mv_name_e,
									$art_id,
									$art_rep_id,
									$ci_name,$cb_name,$bul_name,
									$art_cdi_name,
									$art_cdi_name_e,
									sprintf("(%f,%f,%f)",$art_xmin,$art_ymin,$art_zmin),
									sprintf("(%f,%f,%f)",$art_xmax,$art_ymax,$art_zmax),
									$art_volume);
			push @OUT, $art_data;

			push @$RTN, join("\n",@OUT);
		}
		$sth->finish;
		undef $sth;
	}
	return $RTN;
}

1;
