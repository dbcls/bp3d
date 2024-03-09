package BITS::ArtFile;

use strict;
use warnings;
use feature ':5.10';
use Data::Dumper;
use JSON::XS;
use Time::HiRes;
use DBD::Pg;
use cgi_lib::common;

use constant {
	DEBUG => 0,
	USE_BP3D_COLOR => 1,
};

sub _get_cti_cids {
	my %arg = @_;
	my $dbh   = $arg{'dbh'};
	my $ci_id = $arg{'ci_id'};
	my $cb_id = $arg{'cb_id'};
	my $md_id = $arg{'md_id'};
	my $mv_id = $arg{'mv_id'};
	my $mr_id = $arg{'mr_id'};
	my $bul_id = $arg{'bul_id'};
	my $crl_id = $arg{'crl_id'};
	my $cdi_id = $arg{'cdi_id'};
	my $cdi_name = $arg{'cdi_name'};

	die __LINE__.':'."Undefined bul_id\n" unless(defined $bul_id);
	$crl_id = $bul_id;

	die "Undefined crl_id\n" unless(defined $crl_id);
	$crl_id = 0 unless(defined $crl_id);

#	my $sql = qq|select cdi_id,cti_cids from concept_tree_info where cti_delcause is null and ci_id=$ci_id and cb_id=$cb_id and |;
#	$sql .= qq|crl_id=$crl_id and | if(defined $crl_id);
	my $sql = qq|select cdi_id,but_cids from buildup_tree_info where but_delcause is null and md_id=$md_id and mv_id=$mv_id and mr_id=$mr_id and |;
	$sql .= qq|bul_id=$bul_id and | if(defined $bul_id);

	if(defined $cdi_id || defined $cdi_name){
		unless(defined $cdi_id){
			my $sth = $dbh->prepare(qq|select cdi_id from concept_data_info where ci_id=$ci_id and cdi_name=?|) or die $dbh->errstr;
			$sth->execute($cdi_name) or die $dbh->errstr;
			$sth->bind_col(1, \$cdi_id, undef);
			$sth->fetch;
			$sth->finish;
			undef $sth;
		}
		$sql .= qq|cdi_id = $cdi_id|;
	}else{
		$sql .= qq|but_pids IS NULL|;
	}

	&cgi_lib::common::message($sql) if(DEBUG);

	my $hash;
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	if($sth->rows()>0){
		my $column_number = 0;
		my $cdi_id;
		my $cti_cids;
		$sth->bind_col(++$column_number, \$cdi_id, undef);
		$sth->bind_col(++$column_number, \$cti_cids, undef);
		while($sth->fetch){
			next unless(defined $cti_cids);
			$hash->{$_} = undef for(@{&JSON::XS::decode_json($cti_cids)});
		}
	}
	$sth->finish;
	undef $sth;

	my $cti_cids;
	push(@$cti_cids,keys(%$hash)) if(defined $hash);

	return ($cti_cids,$cdi_id);
}

sub _get_cdi_pids {
	my %arg = @_;
	my $dbh   = $arg{'dbh'};
	my $sth = $arg{'sth'};
	my $hash = $arg{'hash'};
	my $cdi_id = $arg{'cdi_id'};
	my $crl_id = $arg{'crl_id'};
	my $entry = $arg{'entry'};

#	print STDERR __LINE__.':'.__PACKAGE__.":get_all_map_cdi_names($cdi_id,$crl_id):START\n" if(DEBUG);

	my $cdi_pids;
	my $cdi_pid;
	$sth->execute($cdi_id,$crl_id) or die $dbh->errstr;
#	print STDERR __LINE__,":",$sth->rows(),"\n" if(DEBUG);
	$sth->bind_col(1, \$cdi_pid, undef);
	while($sth->fetch){
#		print STDERR __LINE__,":",$cdi_pid,"\n" if(DEBUG);
		next unless(defined $cdi_pid);
#		print STDERR __LINE__,":",$cdi_pid,"\n" if(DEBUG);
		if(exists $hash->{$cdi_pid} && exists $hash->{$cdi_pid}->{$crl_id}){
			if(defined $entry){
				next if($hash->{$cdi_pid}->{$crl_id} >= $entry);
			}else{
				next;
			}
		}
#		print STDERR __LINE__,":",$cdi_pid,"\n" if(DEBUG);
		next if($cdi_id eq $cdi_pid);
#		print STDERR __LINE__,":",$cdi_pid,"\n" if(DEBUG);
		$hash->{$cdi_pid}->{$crl_id} = $entry;
		$cdi_pids->{$cdi_pid} = undef;
	}
	$sth->finish;

	if(defined $cdi_pids){
#		print STDERR __LINE__,":",Dumper($cdi_pids),"\n";
		foreach my $cdi_pid (keys(%$cdi_pids)){
			&_get_cdi_pids(dbh=>$dbh,sth=>$sth,hash=>$hash,cdi_id=>$cdi_pid,crl_id=>$crl_id,entry=>$crl_id);
		}
#		print STDERR __LINE__.':'.__PACKAGE__.":get_all_map_cdi_names($cdi_id,$crl_id):END\n" if(DEBUG);
		return 1;
	}else{
#		print STDERR __LINE__.':'.__PACKAGE__.":get_all_map_cdi_names($cdi_id,$crl_id):END\n" if(DEBUG);
		return 0;
	}
}

sub get_all_map_cdi_names {
	my %arg = @_;
	my $dbh   = $arg{'dbh'};
	my $ci_id = $arg{'ci_id'};
	my $cb_id = $arg{'cb_id'};
	my $bul_id = $arg{'bul_id'};
	my $crl_id = $arg{'crl_id'};
	my $md_id = $arg{'md_id'};
	my $mv_id = $arg{'mv_id'};
	my $mr_id = $arg{'mr_id'};
	my $use_only_map_terms = $arg{'use_only_map_terms'};

#	my $rep_primitive = $arg{'rep_primitive'};
	my $forcing = $arg{'forcing'};

	print STDERR __LINE__.':'.__PACKAGE__.":get_all_map_cdi_names():START\n" if(DEBUG);

	die __LINE__.':'."Undefined bul_id\n" unless(defined $bul_id);
	$crl_id = $bul_id;

	my %CDI_ID2NAME;
	my %CDI_NAME2ID;
	my $sth_cdi = $dbh->prepare(qq|select cdi_id,cdi_name from concept_data_info where cdi_delcause is null and ci_id=$ci_id|) or die $dbh->errstr;
	$sth_cdi->execute() or die $dbh->errstr;
	my $column_number = 0;
	my $cdi_id;
	my $cdi_name;
	$sth_cdi->bind_col(++$column_number, \$cdi_id, undef);
	$sth_cdi->bind_col(++$column_number, \$cdi_name, undef);
	while($sth_cdi->fetch){
		$CDI_ID2NAME{$cdi_id} = $cdi_name;
		$CDI_NAME2ID{$cdi_name} = $cdi_id;
	}
	$sth_cdi->finish;
	undef $sth_cdi;

	my $sql = qq|
select
 cdi_id,EXTRACT(EPOCH FROM max(cm_entry))
from
 concept_art_map as cm
where
 cm_use and
 cm_delcause is null and
 md_id=$md_id and
 mv_id=$mv_id
group by
 cdi_id
|;

	my %CDI_IDS;
	my $cm_entry;
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$column_number = 0;
	$sth->bind_col(++$column_number, \$cdi_id, undef);
	$sth->bind_col(++$column_number, \$cm_entry, undef);
	while($sth->fetch){
		next unless(defined $cdi_id);
		next unless(exists $CDI_ID2NAME{$cdi_id});
		$CDI_IDS{$cdi_id} = $cm_entry;
	}
	$sth->finish;
	undef $sth;

	my $hash;
	if(scalar keys(%CDI_IDS) > 0){
		$hash = {};
		my $cm_entry = $forcing ? time : undef;
		if(defined $use_only_map_terms){
			foreach my $cdi_id (keys(%CDI_IDS)){
				$hash->{$CDI_ID2NAME{$cdi_id}} = $forcing ? $cm_entry - 0 : $CDI_IDS{$cdi_id} - 0;
			}
		}else{
#			my $sth_cti = $dbh->prepare(sprintf(qq|select cdi_id,cti_pids from concept_tree_info where cti_delcause is null and ci_id=$ci_id and cb_id=$cb_id and crl_id=$crl_id and cdi_id in (%s)|,join(',',keys(%CDI_IDS)))) or die $dbh->errstr;
			my $sth_cti = $dbh->prepare(sprintf(qq|select cdi_id,but_pids from buildup_tree_info where but_delcause is null and md_id=$md_id and mv_id=$mv_id and mr_id=$mr_id and bul_id=$bul_id and cdi_id in (%s)|,join(',',keys(%CDI_IDS)))) or die $dbh->errstr;
			$sth_cti->execute() or die $dbh->errstr;
			$column_number = 0;
			my $cti_pids;
			$sth_cti->bind_col(++$column_number, \$cdi_id, undef);
			$sth_cti->bind_col(++$column_number, \$cti_pids, undef);
			while($sth_cti->fetch){
				next unless(defined $cdi_id);
				next unless(exists $CDI_ID2NAME{$cdi_id});
				next unless(exists $CDI_IDS{$cdi_id});

				$hash->{$CDI_ID2NAME{$cdi_id}} = $forcing ? $cm_entry - 0 : $CDI_IDS{$cdi_id} - 0;

				next unless(defined $cti_pids);
				my $pids = &cgi_lib::common::decodeJSON($cti_pids);
				next unless(defined $pids && ref $pids eq 'ARRAY');
				foreach my $pid (@$pids){
					next unless(exists $CDI_ID2NAME{$pid});
					if($forcing){
						$hash->{$CDI_ID2NAME{$pid}} = $cm_entry - 0;
					}elsif(exists $hash->{$CDI_ID2NAME{$pid}}){
						$hash->{$CDI_ID2NAME{$pid}} = $CDI_IDS{$cdi_id} - 0 if($hash->{$CDI_ID2NAME{$pid}} < $CDI_IDS{$cdi_id});
					}else{
						$hash->{$CDI_ID2NAME{$pid}} = $CDI_IDS{$cdi_id} - 0;
					}
				}
			}
			$sth_cti->finish;
			undef $sth_cti
		}
	}

	undef %CDI_IDS;
	undef $cdi_id;
	undef $cdi_name;
	undef $cm_entry;

	if(defined $hash){
		my $cdi_name;
		my $cd_entry;
		my $seg_thum_fgcolor;
		my $sth = $dbh->prepare(qq|
select
 cdi_name,
 EXTRACT(EPOCH FROM GREATEST(cd_entry,seg_entry)) as cd_entry,
 seg_thum_fgcolor
from (
select
 ci_id,
 cdi_id,
 cd_entry,
 seg_id
from
 concept_data
where
 cd_delcause is null and
 ci_id=$ci_id and
 cb_id=$cb_id
union
select
 ci_id,
 cdi_id,
 cd_entry,
 seg_id
from
 buildup_data
where
 cd_delcause is null and
 md_id=$md_id and
 mv_id=$mv_id and
 mr_id=$mr_id
) as cd
left join(select seg_id,seg_entry,seg_thum_fgcolor from concept_segment) as seg on seg.seg_id=cd.seg_id
left join (select ci_id,cdi_id,cdi_name from concept_data_info) as cdi on cdi.ci_id=cd.ci_id and cdi.cdi_id=cd.cdi_id

|) or die $dbh->errstr;

		$sth->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_id, undef);
		$sth->bind_col(++$column_number, \$cd_entry, undef);
		$sth->bind_col(++$column_number, \$seg_thum_fgcolor, undef);
		while($sth->fetch){
			next unless(exists $CDI_ID2NAME{$cdi_id});
			unless(exists $hash->{$CDI_ID2NAME{$cdi_id}}){
#				print STDERR __LINE__.':'.__PACKAGE__.":get_all_map_cdi_names():Unknown [$cdi_name]\n" if(DEBUG);
#				print STDERR __LINE__.':'.__PACKAGE__.":get_all_map_cdi_names():Unknown [$cdi_name]\n";
				next;
			}
			if(ref $hash->{$CDI_ID2NAME{$cdi_id}} eq 'HASH'){
				$hash->{$CDI_ID2NAME{$cdi_id}}->{'entry'} = $cd_entry - 0 if($hash->{$CDI_ID2NAME{$cdi_id}}->{'entry'}<$cd_entry);
			}else{
				$hash->{$CDI_ID2NAME{$cdi_id}} = $cd_entry if($hash->{$CDI_ID2NAME{$cdi_id}}<$cd_entry);
				my $entry = $hash->{$CDI_ID2NAME{$cdi_id}};
				$hash->{$CDI_ID2NAME{$cdi_id}} = {
					entry => $entry - 0,
					seg_thum_fgcolor => $seg_thum_fgcolor,
				};
			}
		}
		$sth->finish;
		undef $sth;
	}

#	print STDERR __LINE__.':'.__PACKAGE__.":get_all_map_cdi_names(".(defined $hash ? scalar keys(%$hash) : undef)."):END\n" if(DEBUG);
	return $hash;
}

sub get_all_unmap_cdi_names {
	my %arg = @_;
	my $dbh   = $arg{'dbh'};
	my $ci_id = $arg{'ci_id'};
	my $cb_id = $arg{'cb_id'};
	my $bul_id = $arg{'bul_id'};
	my $crl_id = $arg{'crl_id'};
	my $md_id = $arg{'md_id'};
	my $mv_id = $arg{'mv_id'};
	my $all_map_cdi_names = $arg{'all_map_cdi_names'};

	my $hash;
	return $hash;

	print STDERR __LINE__.':'.__PACKAGE__.":get_all_unmap_cdi_names():START\n" if(DEBUG);

	die __LINE__.':'."Undefined bul_id\n" unless(defined $bul_id);
	$crl_id = $bul_id;

	my $sql;
	unless($crl_id eq '0'){
		$sql = qq|select cdi_name from concept_tree as ct left join (select ci_id,cdi_id,cdi_name from concept_data_info) as cdi on cdi.ci_id=ct.ci_id and cdi.cdi_id=ct.cdi_id where ct.ci_id=$ci_id and ct.cb_id=$cb_id and crl_id=$crl_id|;
	}else{
		$sql = qq|select cdi_name from concept_tree as ct left join (select ci_id,cdi_id,cdi_name from concept_data_info) as cdi on cdi.ci_id=ct.ci_id and cdi.cdi_id=ct.cdi_id where ct.ci_id=$ci_id and ct.cb_id=$cb_id|;
	}
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	my $cdi_name;
	$sth->bind_col(1, \$cdi_name, undef);
	while($sth->fetch){
#		next if(exists $all_map_cdi_names->{$cdi_name} && exists $all_map_cdi_names->{$cdi_name}->{$crl_id});
		next if(exists $all_map_cdi_names->{$cdi_name});
		next if(exists $hash->{$cdi_name});
#		$hash->{$cdi_name}->{$crl_id} = undef;
		$hash->{$cdi_name} = undef;
	}
	$sth->finish;
	undef $sth;


	print STDERR __LINE__.':'.__PACKAGE__.":get_all_unmap_cdi_names(".(defined $hash ? scalar keys(%$hash) : undef)."):END\n" if(DEBUG);

	return $hash;
}

sub get_art_file {
	my %arg = @_;
	my $dbh   = $arg{'dbh'};
	my $ci_id = $arg{'ci_id'};
	my $cb_id = $arg{'cb_id'};
	my $bul_id = $arg{'bul_id'};
	my $crl_id = $arg{'crl_id'};
	my $md_id = $arg{'md_id'};
	my $mv_id = $arg{'mv_id'};
	my $mr_id = $arg{'mr_id'};
	my $cdi_id = $arg{'cdi_id'};
	my $cdi_name = $arg{'cdi_name'};
	my $use_only_map_terms = $arg{'use_only_map_terms'};

	die __LINE__.':'."Undefined bul_id\n" unless(defined $bul_id);
	$crl_id = $bul_id;

	if(DEBUG){
		print STDERR __LINE__.':'.__PACKAGE__.":get_art_file():START\n";
		print STDERR __LINE__.':'.__PACKAGE__.":get_art_file():\t\$ci_id=[$ci_id]\n"       if(defined $ci_id);
		print STDERR __LINE__.':'.__PACKAGE__.":get_art_file():\t\$cb_id=[$cb_id]\n"       if(defined $cb_id);
		print STDERR __LINE__.':'.__PACKAGE__.":get_art_file():\t\$crl_id=[$crl_id]\n"     if(defined $crl_id);
		print STDERR __LINE__.':'.__PACKAGE__.":get_art_file():\t\$md_id=[$md_id]\n"       if(defined $md_id);
		print STDERR __LINE__.':'.__PACKAGE__.":get_art_file():\t\$mv_id=[$mv_id]\n"       if(defined $mv_id);
		print STDERR __LINE__.':'.__PACKAGE__.":get_art_file():\t\$cdi_id=[$cdi_id]\n"     if(defined $cdi_id);
		print STDERR __LINE__.':'.__PACKAGE__.":get_art_file():\t\$cdi_name=[$cdi_name]\n" if(defined $cdi_name);
	}

	my($art_id,$art_ext);
	my $rows;
	my $cti_cids;
	if(defined $use_only_map_terms){
		unless(defined $cdi_id){
			if(defined $cdi_name){
				my $sth = $dbh->prepare(qq|select cdi_id from concept_data_info where ci_id=$ci_id and cdi_name=?|) or die $dbh->errstr;
				$sth->execute($cdi_name) or die $dbh->errstr;
				$sth->bind_col(1, \$cdi_id, undef);
				$sth->fetch;
				$sth->finish;
				undef $sth;
			}
		}
	}else{
		($cti_cids,$cdi_id) = &_get_cti_cids(
			dbh=>$dbh,
			md_id=>$md_id,
			mv_id=>$mv_id,
			mr_id=>$mr_id,
			ci_id=>$ci_id,
			cb_id=>$cb_id,
			bul_id=>$bul_id,
			crl_id=>$crl_id,
			cdi_id=>$cdi_id,
			cdi_name=>$cdi_name
		);
		if(DEBUG){
			print STDERR __LINE__.':'.__PACKAGE__.":get_art_file():\t\$cdi_id=[$cdi_id]\n";
			print STDERR __LINE__.':'.__PACKAGE__.":get_art_file():\t\$cti_cids=[$cti_cids]\n" if(defined $cti_cids);
		}
	}
	push(@$cti_cids,$cdi_id) if(defined $cdi_id);
	if(defined $cti_cids){
		my $fmt =<<SQL;
select
 art_id,
 art_ext
from
 art_file_info
where
 art_id in (
     select
      art_id
     from
      concept_art_map
     where
      cm_use and
      cm_delcause is null and
      md_id=$md_id and mv_id=$mv_id and cdi_id in (%s)
 )
SQL
		my $sth = $dbh->prepare(sprintf($fmt,join(',',@$cti_cids))) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$art_id, undef);
		$sth->bind_col(++$column_number, \$art_ext, undef);
		while($sth->fetch){
			push(@$rows,{
				art_id => $art_id,
				art_ext => $art_ext
			});
		}
		$sth->finish;
		undef $sth;
	}

	print STDERR __LINE__.':'.__PACKAGE__.":get_art_file():END\n" if(DEBUG);

	return defined $rows ? (wantarray ? @$rows : $rows) : undef;
}

sub get_art_file_bbox {
	my %arg = @_;
	my $dbh   = $arg{'dbh'};
	my $ci_id = $arg{'ci_id'};
	my $cb_id = $arg{'cb_id'};
	my $bul_id = $arg{'bul_id'};
	my $crl_id = $arg{'crl_id'};
	my $md_id = $arg{'md_id'};
	my $mv_id = $arg{'mv_id'};
	my $mr_id = $arg{'mr_id'};
	my $cdi_id = $arg{'cdi_id'};
	my $cdi_name = $arg{'cdi_name'};
	my $use_only_map_terms = $arg{'use_only_map_terms'};

	die __LINE__.':'."Undefined bul_id\n" unless(defined $bul_id);
	$crl_id = $bul_id;

	print STDERR __LINE__.':'.__PACKAGE__.":get_art_file_bbox():START\n" if(DEBUG);
#	&cgi_lib::common::dumper(\%arg);
#	my($package, $file, $line) = caller();
#	&cgi_lib::common::dumper($package);
#	&cgi_lib::common::dumper($file);
#	&cgi_lib::common::dumper($line);

	my($art_xmin,$art_xmax,$art_ymin,$art_ymax,$art_zmin,$art_zmax);

	my $cti_cids;
	if(defined $use_only_map_terms){
		unless(defined $cdi_id){
			if(defined $cdi_name){
				my $sth = $dbh->prepare(qq|select cdi_id from concept_data_info where ci_id=$ci_id and cdi_name=?|) or die $dbh->errstr;
				$sth->execute($cdi_name) or die $dbh->errstr;
				$sth->bind_col(1, \$cdi_id, undef);
				$sth->fetch;
				$sth->finish;
				undef $sth;
			}
		}
	}else{
		($cti_cids,$cdi_id) = &_get_cti_cids(
			dbh=>$dbh,
			md_id=>$md_id,
			mv_id=>$mv_id,
			mr_id=>$mr_id,
			ci_id=>$ci_id,
			cb_id=>$cb_id,
			cb_id=>$cb_id,
			bul_id=>$bul_id,
			crl_id=>$crl_id,
			cdi_id=>$cdi_id,
			cdi_name=>$cdi_name
		);
	}
	push(@$cti_cids,$cdi_id) if(defined $cdi_id);
	if(defined $cti_cids){
		my $fmt =<<SQL;
select
 min(art_xmin),
 max(art_xmax),
 min(art_ymin),
 max(art_ymax),
 min(art_zmin),
 max(art_zmax)
from
 art_file
where
 art_id in (
     select
      art_id
     from
      concept_art_map
     where
      cm_use and
      cm_delcause is null and
      md_id=$md_id and mv_id=$mv_id and cdi_id in (%s)
 )
SQL
		my $sth = $dbh->prepare(sprintf($fmt,join(',',@$cti_cids))) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$art_xmin, undef);
		$sth->bind_col(++$column_number, \$art_xmax, undef);
		$sth->bind_col(++$column_number, \$art_ymin, undef);
		$sth->bind_col(++$column_number, \$art_ymax, undef);
		$sth->bind_col(++$column_number, \$art_zmin, undef);
		$sth->bind_col(++$column_number, \$art_zmax, undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;
	}

	print STDERR __LINE__.':'.__PACKAGE__.":get_art_file_bbox():END\n" if(DEBUG);

	return wantarray ? ($art_xmin,$art_xmax,$art_ymin,$art_ymax,$art_zmin,$art_zmax) : [$art_xmin,$art_xmax,$art_ymin,$art_ymax,$art_zmin,$art_zmax];
}

sub load_art_file_fromDB {
	my %args = @_;
	my $dbh   = $args{'dbh'};
	my $art_id = $args{'art_id'};
	my $art_file_fmt = $args{'art_file_fmt'};

	my $sql=<<SQL;;
select
 art_ext,
 art_data,
 art_data_size,
 EXTRACT(EPOCH FROM art_timestamp)
from
 art_file
where
 art_id=?
SQL
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute($art_id) or die $dbh->errstr;
#	print __LINE__,":\$sth->rows()=[",$sth->rows(),"]\n";
	my $column_number = 0;
	my $art_ext;
	my $art_data;
	my $art_data_size;
	my $art_entry;
	$sth->bind_col(++$column_number, \$art_ext, undef);
	$sth->bind_col(++$column_number, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
	$sth->bind_col(++$column_number, \$art_data_size, undef);
	$sth->bind_col(++$column_number, \$art_entry, undef);
	while($sth->fetch){
		next unless(defined $art_data && defined $art_data_size && defined $art_entry);
		my $objfile = sprintf($art_file_fmt,$art_id,$art_ext);
		my $size = -s $objfile;
		my $mtime = 0;
		$mtime = (stat($objfile))[9] if(-e $objfile);
		unless(-e $objfile && $size == $art_data_size && $mtime>=$art_entry){
#			print __LINE__,":Write [$objfile]\n";
			my $OUT;
			if(-e $objfile){
				open($OUT,"+< $objfile") or die "$!:$objfile\n";
			}else{
				open($OUT,"> $objfile") or die "$!:$objfile\n";
			}
			flock($OUT,2);
			unless(tell($OUT)==$art_data_size){
				seek($OUT,0,0);
				binmode($OUT);
				print $OUT $art_data;
				truncate($OUT,tell($OUT));
			}
			close($OUT);
			utime($art_entry,$art_entry,$objfile);
		}
	}
	$sth->finish;
	undef $sth;
}

sub get_def_colors {
	my %arg = @_;
	my $dbh   = $arg{'dbh'};

	my $DEF_COLOR;
	my $DEF_FG_COLOR;
	my $seg_color;
	my $seg_thum_fgcolor;
	my $seg_entry;

	my $sth = $dbh->prepare(qq|select seg_color,seg_thum_fgcolor,EXTRACT(EPOCH FROM seg_entry) from concept_segment where seg_id=0|) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$seg_color, undef);
	$sth->bind_col(++$column_number, \$seg_thum_fgcolor, undef);
	$sth->bind_col(++$column_number, \$seg_entry, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;
	if(defined $seg_color){
		$seg_color =~ s/^#//g;
		push(@$DEF_COLOR,hex(uc(substr($seg_color,0,2)))/255);
		push(@$DEF_COLOR,hex(uc(substr($seg_color,2,2)))/255);
		push(@$DEF_COLOR,hex(uc(substr($seg_color,4,2)))/255);
	}
	if(defined $seg_thum_fgcolor){
		$seg_thum_fgcolor =~ s/^#//g;
		push(@$DEF_FG_COLOR,hex(uc(substr($seg_thum_fgcolor,0,2)))/255);
		push(@$DEF_FG_COLOR,hex(uc(substr($seg_thum_fgcolor,2,2)))/255);
		push(@$DEF_FG_COLOR,hex(uc(substr($seg_thum_fgcolor,4,2)))/255);
	}
	return ($DEF_COLOR,$DEF_FG_COLOR,$seg_entry);
}
sub get_all_colors {
	my %arg = @_;
	my $dbh   = $arg{'dbh'};
	my $ci_id = $arg{'ci_id'};
	my $cb_id = $arg{'cb_id'};
	my $md_id = $arg{'md_id'};
	my $mv_id = $arg{'mv_id'};
	my $mr_id = $arg{'mr_id'};

	print STDERR __LINE__.':'.__PACKAGE__.":get_all_colors():START\n" if(DEBUG);

	my($DEF_COLOR,$DEF_FG_COLOR,$def_seg_entry) = &get_def_colors(dbh=>$dbh);
	my $DEF_COLOR_ART;
	my $DEF_COLOR_ART_TIMESTAMP;
	if(USE_BP3D_COLOR){
		my $sql = qq|
select
 art_id,
 seg_thum_fgcolor,
 EXTRACT(EPOCH FROM seg_entry)
from (
 select
  cdi_id,
  seg_id
 from
  concept_data
 where
  cd_delcause is null and
  ci_id=$ci_id and
  cb_id=$cb_id
 union
 select
  cdi_id,
  seg_id
 from
  buildup_data
 where
  cd_delcause is null and
  md_id=$md_id and
  mv_id=$mv_id and
  mr_id=$mr_id
) as cd

left join (
   select
    cdi_id,
    art_id
   from
    concept_art_map
   WHERE
    cm_use AND
    cm_delcause IS NULL AND
    (md_id,mv_id,mr_id,cdi_id) IN (select md_id,mv_id,max(mr_id),cdi_id from concept_art_map where md_id=$md_id AND mv_id=$mv_id AND mr_id<=$mr_id group by md_id,mv_id,cdi_id)
) as cm on
   cm.cdi_id=cd.cdi_id
left join (
 select * from concept_segment
) as seg on cd.seg_id=seg.seg_id
where
 art_id is not null
|;
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		my $column_number = 0;
		my $art_id;
		my $color;
		my $seg_entry;
		$sth->bind_col(++$column_number, \$art_id, undef);
		$sth->bind_col(++$column_number, \$color, undef);
		$sth->bind_col(++$column_number, \$seg_entry, undef);
		while($sth->fetch){
			next unless(defined $art_id && defined $color);
			next if(defined $DEF_COLOR_ART && exists $DEF_COLOR_ART->{$art_id});

			$color =~ s/^#//g;

			push(@{$DEF_COLOR_ART->{$art_id}},hex(uc(substr($color,0,2)))/255);
			push(@{$DEF_COLOR_ART->{$art_id}},hex(uc(substr($color,2,2)))/255);
			push(@{$DEF_COLOR_ART->{$art_id}},hex(uc(substr($color,4,2)))/255);

			$DEF_COLOR_ART_TIMESTAMP->{$art_id} = defined $seg_entry ? $seg_entry : $def_seg_entry;
		}
		$sth->finish;
		undef $sth;
		undef $art_id;
		undef $color;
		undef $seg_entry;
	}

	print STDERR __LINE__.':'.__PACKAGE__.":get_all_colors():END\n" if(DEBUG);

	return ($DEF_COLOR_ART,$DEF_COLOR,$DEF_FG_COLOR,$DEF_COLOR_ART_TIMESTAMP);

}

1;
