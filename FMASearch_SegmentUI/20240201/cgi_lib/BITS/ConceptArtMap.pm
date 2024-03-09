package BITS::ConceptArtMap;

use strict;
use warnings;
use feature ':5.10';
use DBD::Pg;

use BITS::Config;

sub get_artfile_obj_format_data {
	my $PARAMS = shift // {};
	my $copyright = shift;

	my $LOG = $PARAMS->{'__LOG__'};
	my $type = $PARAMS->{'type'} // 'HASH';
	my $dbh = $PARAMS->{'dbh'};

	my $md_id = $PARAMS->{'md_id'};
	my $mv_id = $PARAMS->{'mv_id'};
	my $mr_id = $PARAMS->{'mr_id'};
	my $ci_id = $PARAMS->{'ci_id'};
	my $cb_id = $PARAMS->{'cb_id'};
	my $bul_id = 0;

	$copyright =~ s/\s*$//g if(defined $copyright);

	print $LOG __PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($PARAMS) if(defined $LOG);

	my $header_fmt = <<TEXT;
#
# Compatibility version : %s
# File ID : %s
# Build-up logic : %s %s
# Concept ID : %s
# English name : %s
# Bounds(mm): %s-%s
# Volume(cm3): %f
#
TEXT

	my $RTN;

	my $rep_ids;


	my $ALL_ELEMENT_HASH_DATAS;
	if(exists $PARAMS->{&BITS::Config::LOCATION_HASH_IDS_KEY()} && defined $PARAMS->{&BITS::Config::LOCATION_HASH_IDS_KEY()} && ref $PARAMS->{&BITS::Config::LOCATION_HASH_IDS_KEY()} eq 'ARRAY' && scalar @{$PARAMS->{&BITS::Config::LOCATION_HASH_IDS_KEY()}}){

		my $sql;
		my $sth;
		my $column_number;

		my $mv_name_e;
		my $ci_name;
		my $cb_name;

		$sql=<<SQL;
select
 mv_name_e
from
 model_version
where
 md_id=$md_id and
 mv_id=$mv_id
SQL

		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth->bind_col(++$column_number, \$mv_name_e, undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;


		$sql=<<SQL;
select
 ci_name
from
 concept_info
where
 ci_id=$ci_id
SQL

		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth->bind_col(++$column_number, \$ci_name, undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;

		$sql=<<SQL;
select
 cb_name
from
 concept_build
where
 ci_id=$ci_id and
 cb_id=$cb_id
SQL

		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth->bind_col(++$column_number, \$cb_name, undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;



		my $ids = $PARAMS->{&BITS::Config::LOCATION_HASH_IDS_KEY()};

		$sql=<<SQL;
select
 bti.cdi_id,
 bti.but_cids
from
 buildup_tree_info as bti
left join (
 select cdi_id,cdi_name from concept_data_info where ci_id=$ci_id
) as cdi on (cdi.cdi_id=bti.cdi_id)
where
 bti.md_id=$md_id and
 bti.mv_id=$mv_id and
 bti.mr_id=$mr_id and
 bti.bul_id=$bul_id and
 cdi.cdi_name IN ('%s')
SQL

		$sth = $dbh->prepare(sprintf($sql,join("','",@$ids))) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;

		my $cdi_id;
		my $but_cids;
		my $cdi_ids_hash;

		my $art_id;
		my $art_ids_hash;

		my $cdi_name;
		my $cdi_name_e;

		$column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_id, undef);
		$sth->bind_col(++$column_number, \$but_cids, undef);
		while($sth->fetch){
			$cdi_ids_hash->{$cdi_id} = undef if(defined $cdi_id);
			$but_cids = &cgi_lib::common::decodeJSON($but_cids) if(defined $but_cids);
			if(defined $but_cids && ref $but_cids eq 'ARRAY' && scalar @$but_cids){
				$cdi_ids_hash->{$_} = undef for(@$but_cids);
			}
		}
		$sth->finish;
		undef $sth;

		if(defined $cdi_ids_hash){

			$sql=<<SQL;
select
 art_id,
 cdi_id
from
 concept_art_map
where
 cm_use and
 cm_delcause is null and
 md_id=$md_id and
 mv_id=$mv_id and
 mr_id=$mr_id and
 cdi_id IN (%s)
SQL

			$sth = $dbh->prepare(sprintf($sql,join(',',keys(%$cdi_ids_hash)))) or die $dbh->errstr;
			$sth->execute() or die $dbh->errstr;

			undef $cdi_ids_hash;

			$column_number = 0;
			$sth->bind_col(++$column_number, \$art_id, undef);
			$sth->bind_col(++$column_number, \$cdi_id, undef);
			while($sth->fetch){
				next unless(defined $art_id && defined $cdi_id);
				$art_ids_hash->{$art_id} = $cdi_id;
				$cdi_ids_hash->{$cdi_id} = undef;
			}
			$sth->finish;
			undef $sth;
		}

		if(defined $art_ids_hash && defined $cdi_ids_hash){

			$sql=<<SQL;
select
 cdi.cdi_id,
 cdi.cdi_name,
 COALESCE(cd.cd_name,cdi.cdi_name_e) as cdi_name_e
from
 concept_data_info as cdi
left join (
 select cdi_id,cd_name from concept_data where ci_id=$ci_id and cb_id=$cb_id
) as cd on (cd.cdi_id=cdi.cdi_id)
where
 cdi.ci_id=$ci_id and
 cdi.cdi_id IN (%s)
SQL

			$sth = $dbh->prepare(sprintf($sql,join(',',keys(%$cdi_ids_hash)))) or die $dbh->errstr;
			$sth->execute() or die $dbh->errstr;

			undef $cdi_ids_hash;

			$column_number = 0;
			$sth->bind_col(++$column_number, \$cdi_id, undef);
			$sth->bind_col(++$column_number, \$cdi_name, undef);
			$sth->bind_col(++$column_number, \$cdi_name_e, undef);
			while($sth->fetch){
				$cdi_ids_hash->{$cdi_id} = {
					cdi_name => $cdi_name,
					cdi_name_e => $cdi_name_e,
				};
			}
			$sth->finish;
			undef $sth;
		}

		if(defined $art_ids_hash && defined $cdi_ids_hash){

			$sql=<<SQL;
select
 art.art_id,
 art.art_ext,
 EXTRACT(EPOCH FROM art.art_timestamp),
 art.art_xmin,
 art.art_xmax,
 art.art_ymin,
 art.art_ymax,
 art.art_zmin,
 art.art_zmax,
 art.art_volume,
 art.artc_id
from
 art_file as art
where
 art.art_id IN ('%s')
SQL

			my $sth_data = $dbh->prepare(qq|select art_data from art_file where art_id=?|) or die $dbh->errstr;

			$sth = $dbh->prepare(sprintf($sql,join("','",keys %$art_ids_hash))) or die $dbh->errstr;
			$sth->execute() or die $dbh->errstr;

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
			my $artc_id;

			$column_number = 0;
			$sth->bind_col(++$column_number, \$art_id, undef);
			$sth->bind_col(++$column_number, \$art_ext, undef);
			$sth->bind_col(++$column_number, \$art_entry, undef);
			$sth->bind_col(++$column_number, \$art_xmin, undef);
			$sth->bind_col(++$column_number, \$art_xmax, undef);
			$sth->bind_col(++$column_number, \$art_ymin, undef);
			$sth->bind_col(++$column_number, \$art_ymax, undef);
			$sth->bind_col(++$column_number, \$art_zmin, undef);
			$sth->bind_col(++$column_number, \$art_zmax, undef);
			$sth->bind_col(++$column_number, \$art_volume, undef);
			$sth->bind_col(++$column_number, \$artc_id, undef);

			while($sth->fetch){
				next unless(defined $art_id && defined $art_ext && defined $art_entry);


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

				$cdi_id = $art_ids_hash->{$art_id};
				$cdi_name = $cdi_ids_hash->{$cdi_id}->{'cdi_name'};
				$cdi_name_e = $cdi_ids_hash->{$cdi_id}->{'cdi_name_e'};

				my @HEAD;
				push @HEAD, $copyright if(defined $copyright);
				push @HEAD, sprintf($header_fmt,
										$mv_name_e,
#										$art_id,
										$artc_id,
										$ci_name,
										$cb_name,
										$cdi_name,
										$cdi_name_e,
										sprintf("(%f,%f,%f)",$art_xmin,$art_ymin,$art_zmin),
										sprintf("(%f,%f,%f)",$art_xmax,$art_ymax,$art_zmax),
										$art_volume);


				$RTN->{$art_id} = {
					mv_name_e => $mv_name_e,,
					ci_name => $ci_name,
					cb_name => $cb_name,
					cdi_name => $cdi_name,
					cdi_name_e => $cdi_name_e,

					art_id => $art_id,
					art_xmin => $art_xmin,
					art_ymin => $art_ymin,
					art_zmin => $art_zmin,
					art_xmax => $art_xmax,
					art_ymax => $art_ymax,
					art_zmax => $art_zmax,
					art_volume => $art_volume,
					artc_id => $artc_id,
					art_ext => $art_ext,
					art_entry => $art_entry,

					head => join("\n",@HEAD),
					body => $art_data
				};
			}
			$sth->finish;
			undef $sth;
			undef $sth_data;
		}

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
