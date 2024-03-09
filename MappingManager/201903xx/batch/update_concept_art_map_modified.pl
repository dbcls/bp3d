#!/bp3d/local/perl/bin/perl

$| = 1;

BEGIN{
	use FindBin;
	die "$! [$FindBin::Bin]" unless(chdir($FindBin::Bin));
}

use strict;
use warnings;
use feature ':5.10';
#use DBD::Pg;
#use Hash::Diff;

use List::MoreUtils;


#delete $ENV{'AG_DB_NAME'};
#delete $ENV{'AG_DB_HOST'};
#delete $ENV{'AG_DB_PORT'};

#my $LOG = \*STDERR;
my $LOG = \*STDOUT;

use List::MoreUtils;

use Getopt::Long qw(:config posix_default no_ignore_case gnu_compat);
my $config = {
	host => '127.0.0.1',
	port => '8543'
};
&Getopt::Long::GetOptions($config,qw/
	host|h=s
	port|p=s
	target|t=s@
	version|v=s@
/) or exit 1;

$ENV{'AG_DB_HOST'} = $config->{'host'};
$ENV{'AG_DB_PORT'} = $config->{'port'};

my @USE_CDI_NAMES;
if(exists $config->{'target'} && defined $config->{'target'} && ref $config->{'target'} eq 'ARRAY' && scalar @{$config->{'target'}}){
	foreach my $cdi_name (@{$config->{'target'}}){
		push(@USE_CDI_NAMES, $_) for(split(/[^A-Za-z0-9]/,$cdi_name));
	}
}

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
require "webgl_common.pl";
use cgi_lib::common;

&cgi_lib::common::message('$AG_DB_NAME=['.$ENV{'AG_DB_NAME'}.']', $LOG);
&cgi_lib::common::message('$AG_DB_HOST=['.$ENV{'AG_DB_HOST'}.']', $LOG);
&cgi_lib::common::message('$AG_DB_PORT=['.$ENV{'AG_DB_PORT'}.']', $LOG);

use BITS::Config;
use BITS::ArtFile;
use BITS::ConceptArtMapModified;
use obj2deci;

my $dbh = &get_dbh();

my $md_id = 1;
my $mv_id = 1;

my $ci_id;
my $cb_id;

my $column_number = 0;

unless(defined $ci_id && defined $cb_id){
	my $sql = qq|select ci_id,cb_id from model_version where md_id=? and mv_id=?|;
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute($md_id,$mv_id) or die $dbh->errstr;
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$ci_id, undef);
	$sth->bind_col(++$column_number, \$cb_id, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;
}

&cgi_lib::common::message('$md_id=['.$md_id.']', $LOG);
&cgi_lib::common::message('$mv_id=['.$mv_id.']', $LOG);
&cgi_lib::common::message('$ci_id=['.$ci_id.']', $LOG);
&cgi_lib::common::message('$cb_id=['.$cb_id.']', $LOG);

my %CDI_ID2NAME;
my %CDI_NAME2ID;
if(1){
	my $sth_cdi = $dbh->prepare(qq|select cdi_id,cdi_name from concept_data_info where cdi_delcause is null and ci_id=$ci_id|) or die $dbh->errstr;
	$sth_cdi->execute() or die $dbh->errstr;
	$column_number = 0;
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
}

#exit;
my %CM;
my $use_only_map_terms = &BITS::Config::USE_ONLY_MAP_TERMS();
if($use_only_map_terms){
	my $sth_cm = $dbh->prepare(qq|select * from concept_art_map where cm_use and cm_delcause is null and md_id=$md_id and mv_id=$mv_id|) or die $dbh->errstr;
	$sth_cm->execute() or die $dbh->errstr;
	$column_number = 0;
	while(my $hash_ref = $sth_cm->fetchrow_hashref){

		if(scalar @USE_CDI_NAMES){
			if(scalar grep {$CDI_ID2NAME{$hash_ref->{'cdi_id'}} eq $_} @USE_CDI_NAMES){
				push(@{$CM{$hash_ref->{'cdi_id'}}},$hash_ref);
			}
		}else{
			push(@{$CM{$hash_ref->{'cdi_id'}}},$hash_ref);
		}
	}
	$sth_cm->finish;
	undef $sth_cm;
	if(scalar @USE_CDI_NAMES){
		die __LINE__.':Unknown cdi_names [',join(',',sort @USE_CDI_NAMES).']' unless(scalar keys(%CM));
	}
}
#my $use_only_map_terms = (scalar keys(%CM)) ? 1 : undef;


my %SEGMENT_ZRANGE;
if(1){
	my $sth_cszr_sel = $dbh->prepare(qq|select cszr_id,cszr_min,cszr_max from concept_segment_zrange where cszr_delcause is null|) or die $dbh->errstr;
	$sth_cszr_sel->execute() or die $dbh->errstr;
	my $column_number = 0;
	my $cszr_id;
	my $cszr_min;
	my $cszr_max;
	$sth_cszr_sel->bind_col(++$column_number, \$cszr_id, undef);
	$sth_cszr_sel->bind_col(++$column_number, \$cszr_min, undef);
	$sth_cszr_sel->bind_col(++$column_number, \$cszr_max, undef);
	while($sth_cszr_sel->fetch){
		$SEGMENT_ZRANGE{$cszr_id} = {
			'min' => $cszr_min,
			'max' => $cszr_max,
		};
	}
	$sth_cszr_sel->finish;
	undef $sth_cszr_sel;
}
my %SEGMENT_VALUME;
if(1){
	my $sth_csv_sel = $dbh->prepare(qq|select csv_id,csv_min,csv_max from concept_segment_volume where csv_delcause is null|) or die $dbh->errstr;
	$sth_csv_sel->execute() or die $dbh->errstr;
	my $column_number = 0;
	my $csv_id;
	my $csv_min;
	my $csv_max;
	$sth_csv_sel->bind_col(++$column_number, \$csv_id, undef);
	$sth_csv_sel->bind_col(++$column_number, \$csv_min, undef);
	$sth_csv_sel->bind_col(++$column_number, \$csv_max, undef);
	while($sth_csv_sel->fetch){
		$SEGMENT_VALUME{$csv_id}= {
			'min' => $csv_min,
			'max' => $csv_max,
		};
	}
	$sth_csv_sel->finish;
	undef $sth_csv_sel;
}

my $tbp_max_enter;
if(1){
	my $sth_tbp_enter = $dbh->prepare(qq|select EXTRACT(EPOCH FROM max(tbp_enter)) from thumbnail_background_part where md_id=$md_id and mv_id=$mv_id and ci_id=$ci_id|) or die $dbh->errstr;
	$sth_tbp_enter->execute() or die $dbh->errstr;
	$column_number = 0;
	$sth_tbp_enter->bind_col(++$column_number, \$tbp_max_enter, undef);
	$sth_tbp_enter->fetch;
	$sth_tbp_enter->finish;
	undef $sth_tbp_enter;
}
$tbp_max_enter = 0 unless(defined $tbp_max_enter);
&cgi_lib::common::message('$tbp_max_enter='.$tbp_max_enter, $LOG);

#$dbh->do(qq|update concept_art_map_modified set cm_delcause='DELETE' where md_id=$md_id AND mv_id=$mv_id|) or die $dbh->errstr;

my $sth_get_mca_id = $dbh->prepare(qq|select get_mca_id(?)|) or die $dbh->errstr;
my $sth_get_mca_prep = $dbh->prepare(qq|select mca_xmin,mca_xmax,mca_ymin,mca_ymax,mca_zmin,mca_zmax,mca_volume from mapping_concepts_arts where mca_id=?|) or die $dbh->errstr;
my $sth_set_mca_prep = $dbh->prepare(qq|update mapping_concepts_arts set mca_xmin=?,mca_xmax=?,mca_ymin=?,mca_ymax=?,mca_zmin=?,mca_zmax=?,mca_volume=? where mca_id=?|) or die $dbh->errstr;

my $art_file_prefix = &catdir($FindBin::Bin,'art_file');
&File::Path::make_path($art_file_prefix,{verbose => 0, mode => 0777}) unless(-e $art_file_prefix);
my $art_file_fmt = &catdir($art_file_prefix,'%s%s');

#foreach my $crl_id (qw/0 3 4/){
foreach my $crl_id (qw/0/){

	my $cur_cm_modified = &BITS::ConceptArtMapModified::exec(
		dbh => $dbh,
		md_id => $md_id,
		mv_id => $mv_id,
		crl_id => $crl_id,
		cdi_names => (scalar @USE_CDI_NAMES ? \@USE_CDI_NAMES : undef),
		use_only_map_terms => $use_only_map_terms,
		LOG => $LOG
	);
	if(defined $cur_cm_modified){
#	&cgi_lib::common::message(&cgi_lib::common::encodeJSON($cur_cm_modified,1), $LOG);
		&cgi_lib::common::message(scalar keys(%$cur_cm_modified), $LOG);
	}
#exit;

	my $new_cm_modified;
	if(0){
		$new_cm_modified = &BITS::ConceptArtMapModified::exec(
			dbh => $dbh,
			md_id => $md_id,
			mv_id => $mv_id+1,
			crl_id => $crl_id,
			cdi_names => (scalar @USE_CDI_NAMES ? \@USE_CDI_NAMES : undef),
			use_only_map_terms => $use_only_map_terms,
			LOG => $LOG
		);
	}
	my $diff_cm_modified = &BITS::ConceptArtMapModified::diff($new_cm_modified,$cur_cm_modified) if(defined $new_cm_modified);
	&cgi_lib::common::message(&cgi_lib::common::encodeJSON($diff_cm_modified,1), $LOG) if(defined $diff_cm_modified);
#&cgi_lib::common::message(&cgi_lib::common::encodeJSON($cur_cm_modified,1), $LOG) if(defined $cur_cm_modified);
#exit;

	my($ELEMENT, $COMP_DENSITY_USE_TERMS, $COMP_DENSITY_END_TERMS, $COMP_DENSITY, $CDI_MAP, $CDI_MAP_ART_DATE, $CDI_ID2CID, $CDI_MAP_SUM_VOLUME_DEL_ID) = &BITS::ConceptArtMapModified::calcElementAndDensity(
		dbh => $dbh,
		md_id  => $md_id,
		mv_id  => $mv_id,
		crl_id => $crl_id,
		ci_id  => $ci_id,
		cb_id  => $cb_id,
		cdi_ids => [keys %$cur_cm_modified],
		LOG => $LOG
	);

	&cgi_lib::common::message(scalar keys(%$ELEMENT), $LOG) if(defined $ELEMENT);
	&cgi_lib::common::message(scalar keys(%$COMP_DENSITY_USE_TERMS), $LOG) if(defined $COMP_DENSITY_USE_TERMS);
	&cgi_lib::common::message(scalar keys(%$COMP_DENSITY_END_TERMS), $LOG) if(defined $COMP_DENSITY_END_TERMS);
	&cgi_lib::common::message(scalar keys(%$COMP_DENSITY), $LOG) if(defined $COMP_DENSITY);
	&cgi_lib::common::message(scalar grep {!exists $ELEMENT->{$_} && defined $COMP_DENSITY->{$_} && $COMP_DENSITY->{$_}>0} keys(%$COMP_DENSITY), $LOG) if(defined $COMP_DENSITY);

#exit;
#next;

#	$dbh->do(qq|update concept_art_map_modified set cm_delcause='DELETE' where md_id=$md_id AND mv_id=$mv_id AND crl_id=$crl_id|) or die $dbh->errstr;


#my $cdi_id = 2203;
#foreach my $cdi_id (keys(%$COMP_DENSITY_USE_TERMS)){
#	print $cdi_id."\n";
#	exit;
#}
#&cgi_lib::common::message($COMP_DENSITY_USE_TERMS->{$cdi_id}, $LOG) if(defined $COMP_DENSITY_USE_TERMS);
#&cgi_lib::common::message($COMP_DENSITY_END_TERMS->{$cdi_id}, $LOG) if(defined $COMP_DENSITY_END_TERMS);
#&cgi_lib::common::message($COMP_DENSITY->{$cdi_id}, $LOG) if(defined $COMP_DENSITY);

#exit;



#	my $all_map_cdi_names;
#$all_map_cdi_names = &BITS::ArtFile::get_all_map_cdi_names(dbh=>$dbh,md_id=>$md_id,mv_id=>$mv_id,ci_id=>$ci_id,cb_id=>$cb_id);
#&cgi_lib::common::message(&cgi_lib::common::encodeJSON($all_map_cdi_names,1), $LOG) if(defined $all_map_cdi_names);
#	&cgi_lib::common::message(scalar keys(%$all_map_cdi_names), $LOG) if(defined $all_map_cdi_names);
#	&cgi_lib::common::message(scalar keys(%$cur_cm_modified), $LOG) if(defined $cur_cm_modified);


	&cgi_lib::common::message(scalar keys(%$cur_cm_modified), $LOG) if(defined $cur_cm_modified);

	my %ART_MAP_SUM_VOLUME_DEL_ID;
	if(scalar keys(%$CDI_MAP_SUM_VOLUME_DEL_ID)>0){
		my $sth_cm = $dbh->prepare(sprintf(qq|select * from concept_art_map where cm_use and cm_delcause is null and md_id=$md_id and mv_id=$mv_id and cdi_id in (%s)|,join(',',keys(%$CDI_MAP_SUM_VOLUME_DEL_ID)))) or die $dbh->errstr;
		$sth_cm->execute() or die $dbh->errstr;
		while(my $hash_ref = $sth_cm->fetchrow_hashref){
			$ART_MAP_SUM_VOLUME_DEL_ID{$hash_ref->{'art_id'}} = undef;
		}
		$sth_cm->finish;
		undef $sth_cm;
	}

	my $count = 0;
	foreach my $cdi_id (keys(%$cur_cm_modified)){
		if(defined $use_only_map_terms){
			next unless(exists $CM{$cdi_id});
			next unless(exists $CDI_MAP_ART_DATE->{$cdi_id});
		}

		printf("\r[%4d]",++$count);
		my $art_files = &BITS::ArtFile::get_art_file(
			dbh    => $dbh,
			md_id  => $md_id,
			mv_id  => $mv_id,
			ci_id  => $ci_id,
			cb_id  => $cb_id,
			crl_id => $crl_id,
			cdi_id => $cdi_id,
			use_only_map_terms => $use_only_map_terms
		);
		unless(defined $art_files && ref $art_files eq 'ARRAY'){
			&cgi_lib::common::message($art_files, $LOG);
			&cgi_lib::common::message('$md_id='.$md_id, $LOG);
			&cgi_lib::common::message('$mv_id='.$mv_id, $LOG);
			&cgi_lib::common::message('$ci_id='.$ci_id, $LOG);
			&cgi_lib::common::message('$cb_id='.$cb_id, $LOG);
			&cgi_lib::common::message('$crl_id='.$crl_id, $LOG);
			&cgi_lib::common::message('$cdi_id='.$cdi_id."[$CDI_ID2NAME{$cdi_id}]", $LOG);
			delete $cur_cm_modified->{$cdi_id};
			next;
		}
		die __LINE__.':'.$cdi_id."\n" unless(exists $cur_cm_modified->{$cdi_id});

		$art_files = [grep { !exists $ART_MAP_SUM_VOLUME_DEL_ID{$_->{'art_id'}} } @$art_files];
		next unless(scalar @$art_files);

#if($cdi_id == $CDI_NAME2ID{'FMA52568'}){
#	&cgi_lib::common::message(scalar @$art_files, $LOG);
#}

#&cgi_lib::common::message($art_files, $LOG);

#	$cur_cm_modified->{$cdi_id}->{'art_files'} = $art_files;
#	foreach my $af (@$art_files){
#		&cgi_lib::common::message("\n".$cdi_id.':'.$CDI_ID2NAME{$cdi_id}.':'.$af->{'art_id'}, $LOG) unless(exists $CDI_MAP_ART_DATE->{$cdi_id}->{$af->{'art_id'}});
#	}
		if(defined $use_only_map_terms){
			$cur_cm_modified->{$cdi_id}->{'art_files'} = [grep { exists $CDI_MAP_ART_DATE->{$cdi_id}->{$_->{'art_id'}} } @$art_files];
		}else{
	#		push(@{$cur_cm_modified->{$cdi_id}->{'art_files'}},@$art_files);
			if(exists $CDI_ID2CID->{$cdi_id} && defined $CDI_ID2CID->{$cdi_id} && ref $CDI_ID2CID->{$cdi_id} eq 'ARRAY'){
				foreach my $cdi_cid (@{$CDI_ID2CID->{$cdi_id}}){
					next unless(exists $CDI_MAP_ART_DATE->{$cdi_cid});
					push(@{$cur_cm_modified->{$cdi_id}->{'art_files'}},grep { exists $CDI_MAP_ART_DATE->{$cdi_cid}->{$_->{'art_id'}} } @$art_files);
				}
			}
			elsif(exists $CDI_MAP_ART_DATE->{$cdi_id} && defined $CDI_MAP_ART_DATE->{$cdi_id} && ref $CDI_MAP_ART_DATE->{$cdi_id} eq 'HASH'){
				$cur_cm_modified->{$cdi_id}->{'art_files'} = [grep { exists $CDI_MAP_ART_DATE->{$cdi_id}->{$_->{'art_id'}} } @$art_files];
			}
		}

		if(exists $cur_cm_modified->{$cdi_id}->{'art_files'} && defined $cur_cm_modified->{$cdi_id}->{'art_files'} && ref $cur_cm_modified->{$cdi_id}->{'art_files'} eq 'ARRAY'){
			$cur_cm_modified->{$cdi_id}->{'art_files'} = [&List::MoreUtils::uniq(@{$cur_cm_modified->{$cdi_id}->{'art_files'}})];
		}

#if($cdi_id == $CDI_NAME2ID{'FMA52568'}){
#	&cgi_lib::common::message(scalar @{$cur_cm_modified->{$cdi_id}->{'art_files'}}, $LOG);
#}

#	&cgi_lib::common::message($CDI_ID2NAME{$cdi_id}.':'.(scalar @$art_files), $LOG);
#	if(exists $cur_cm_modified->{$cdi_id}->{'art_files'} && defined $cur_cm_modified->{$cdi_id}->{'art_files'} && ref $cur_cm_modified->{$cdi_id}->{'art_files'} eq 'ARRAY'){
#		&cgi_lib::common::message((scalar @{$cur_cm_modified->{$cdi_id}->{'art_files'}}), $LOG);
#	}else{
#		die __LINE__;
#	}
#	say '';
	}
	say '';
#exit;

	$dbh->do(qq|update concept_art_map_modified set cm_delcause='DELETE' where md_id=$md_id AND mv_id=$mv_id AND crl_id=$crl_id|) or die $dbh->errstr;


	my $sth_cmm_sel = $dbh->prepare(qq|select EXTRACT(EPOCH FROM cm_modified) from concept_art_map_modified where md_id=$md_id AND mv_id=$mv_id AND crl_id=$crl_id AND cdi_id=?|) or die $dbh->errstr;
	my $sth_cmm_upd = $dbh->prepare(qq|update concept_art_map_modified set cm_modified=?,cm_delcause=?,mca_id=?,ci_id=$ci_id,cb_id=$cb_id where md_id=$md_id AND mv_id=$mv_id AND crl_id=$crl_id AND cdi_id=?|) or die $dbh->errstr;
	my $sth_cmm_ins = $dbh->prepare(qq|insert into concept_art_map_modified (cm_modified,cm_delcause,ci_id,cb_id,md_id,mv_id,crl_id,mca_id,cdi_id) VALUES (?,?,$ci_id,$cb_id,$md_id,$mv_id,$crl_id,?,?)|) or die $dbh->errstr;
	my $sth_cmm_upd_xyz = $dbh->prepare(qq|update concept_art_map_modified set cm_xmin=?,cm_xmax=?,cm_ymin=?,cm_ymax=?,cm_zmin=?,cm_zmax=?,cm_volume=?,cm_density_use_terms=?,cm_density_end_terms=?,cm_density=?,cm_primitive=?,cszr_id=?,csv_id=? where md_id=$md_id AND mv_id=$mv_id AND crl_id=$crl_id AND cdi_id=?|) or die $dbh->errstr;
#my $sth_cmm_upd_xyz = $dbh->prepare(qq|update concept_art_map_modified set cm_xmin=?,cm_xmax=?,cm_ymin=?,cm_ymax=?,cm_zmin=?,cm_zmax=?,cm_volume=?,cm_density_use_terms=?,cm_density_end_terms=?,cm_density=?,cm_primitive=?,cszr_id=?,csv_id=?,mca_id=null where md_id=? AND mv_id=? AND cdi_id=?|) or die $dbh->errstr;



	my @USE_CDI_IDS = sort {scalar @{$cur_cm_modified->{$a}->{'art_files'}} <=> scalar @{$cur_cm_modified->{$b}->{'art_files'}}} grep {exists $cur_cm_modified->{$_}->{'art_files'}} keys(%$cur_cm_modified);
	&cgi_lib::common::message(scalar @USE_CDI_IDS, $LOG);
	$count = scalar @USE_CDI_IDS;
	foreach my $cdi_id (@USE_CDI_IDS){
		printf("\r[%4d]%7s",--$count,'');
		my @FILES;
		foreach my $art_file (@{$cur_cm_modified->{$cdi_id}->{'art_files'}}){
			my $file = sprintf($art_file_fmt,$art_file->{'art_id'},$art_file->{'art_ext'});
			&BITS::ArtFile::load_art_file_fromDB(dbh=>$dbh,art_id=>$art_file->{'art_id'},art_file_fmt=>$art_file_fmt) unless(-e $file);
			if(-e $file && -f $file && -s $file){
				push(@FILES, $file);
			}else{
				warn __LINE__.':'."Unknown file [$file]\n";
			}
		}
		@FILES = &List::MoreUtils::uniq(@FILES) if(scalar @FILES>1);
		printf("\r[%4d]:[%4d]",$count,scalar @FILES);
		my $prop;
#	my $prop = &obj2deci::getProperties(\@FILES);
##	&cgi_lib::common::message(&cgi_lib::common::encodeJSON($prop,1), $LOG) if(defined $prop);
#	next unless(defined $prop && ref $prop eq 'HASH' && exists $prop->{'bounds'} && defined $prop->{'bounds'} && ref $prop->{'bounds'} eq 'ARRAY' && scalar @{$prop->{'bounds'}} >= 6 && exists $prop->{'volume'} && defined $prop->{'volume'});

		my $mca_id;
		if(1){
			$sth_get_mca_id->execute(join(',',map {$_->{'art_id'}} @{$cur_cm_modified->{$cdi_id}->{'art_files'}})) or die $dbh->errstr;
			my $column_number = 0;
			$sth_get_mca_id->bind_col(++$column_number, \$mca_id, undef);
			$sth_get_mca_id->fetch;
			$sth_get_mca_id->finish;
			unless(defined $mca_id && length $mca_id){
				undef $mca_id;
			}else{
#if($cdi_id == $CDI_NAME2ID{'FMA52568'}){
#	&cgi_lib::common::message($mca_id, $LOG);
#}
				$sth_get_mca_prep->execute($mca_id) or die $dbh->errstr;
				$column_number = 0;
				my $mca_xmin;
				my $mca_xmax;
				my $mca_ymin;
				my $mca_ymax;
				my $mca_zmin;
				my $mca_zmax;
				my $mca_volume;
				$sth_get_mca_prep->bind_col(++$column_number, \$mca_xmin, undef);
				$sth_get_mca_prep->bind_col(++$column_number, \$mca_xmax, undef);
				$sth_get_mca_prep->bind_col(++$column_number, \$mca_ymin, undef);
				$sth_get_mca_prep->bind_col(++$column_number, \$mca_ymax, undef);
				$sth_get_mca_prep->bind_col(++$column_number, \$mca_zmin, undef);
				$sth_get_mca_prep->bind_col(++$column_number, \$mca_zmax, undef);
				$sth_get_mca_prep->bind_col(++$column_number, \$mca_volume, undef);
				$sth_get_mca_prep->fetch;
				$sth_get_mca_prep->finish;

				if($mca_zmin==0 && $mca_zmax==0 && $mca_volume==0){
=pod
say '';
&cgi_lib::common::message(scalar @FILES, $LOG);
					$prop = &obj2deci::getProperties(\@FILES);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON($prop,1), $LOG) if(defined $prop);
					next unless(defined $prop && ref $prop eq 'HASH' && exists $prop->{'bounds'} && defined $prop->{'bounds'} && ref $prop->{'bounds'} eq 'ARRAY' && scalar @{$prop->{'bounds'}} >= 6 && exists $prop->{'volume'} && defined $prop->{'volume'});
					$prop->{'volume'} = defined $prop->{'volume'} && $prop->{'volume'} > 0 ?  &BITS::ConceptArtMapModified::Truncated($prop->{'volume'} / 1000) : 0;

					$sth_set_mca_prep->execute($prop->{'bounds'}->[0],$prop->{'bounds'}->[1],$prop->{'bounds'}->[2],$prop->{'bounds'}->[3],$prop->{'bounds'}->[4],$prop->{'bounds'}->[5],$prop->{'volume'},$mca_id) or die $dbh->errstr;
					$sth_set_mca_prep->finish;
=cut

					my $sth_art_prop = $dbh->prepare(sprintf(qq|select MIN(art_xmin),MAX(art_xmax),MIN(art_ymin),MAX(art_ymax),MIN(art_zmin),MAX(art_zmax),SUM(art_volume) from art_file where art_id in (%s)|, join(',',map {'?'} @{$cur_cm_modified->{$cdi_id}->{'art_files'}}) )) or die $dbh->errstr;
					$sth_art_prop->execute(map {$_->{'art_id'}} @{$cur_cm_modified->{$cdi_id}->{'art_files'}}) or die $dbh->errstr;
					$column_number = 0;
					$sth_art_prop->bind_col(++$column_number, \$mca_xmin, undef);
					$sth_art_prop->bind_col(++$column_number, \$mca_xmax, undef);
					$sth_art_prop->bind_col(++$column_number, \$mca_ymin, undef);
					$sth_art_prop->bind_col(++$column_number, \$mca_ymax, undef);
					$sth_art_prop->bind_col(++$column_number, \$mca_zmin, undef);
					$sth_art_prop->bind_col(++$column_number, \$mca_zmax, undef);
					$sth_art_prop->bind_col(++$column_number, \$mca_volume, undef);
					$sth_art_prop->fetch;
					$sth_art_prop->finish;
					undef $sth_art_prop;

					$sth_set_mca_prep->execute($mca_xmin,$mca_xmax,$mca_ymin,$mca_ymax,$mca_zmin,$mca_zmax,$mca_volume,$mca_id) or die $dbh->errstr;
					$sth_set_mca_prep->finish;

					push(@{$prop->{'bounds'}}, $mca_xmin);
					push(@{$prop->{'bounds'}}, $mca_xmax);
					push(@{$prop->{'bounds'}}, $mca_ymin);
					push(@{$prop->{'bounds'}}, $mca_ymax);
					push(@{$prop->{'bounds'}}, $mca_zmin);
					push(@{$prop->{'bounds'}}, $mca_zmax);
					$prop->{'volume'} = $mca_volume;

				}else{
					push(@{$prop->{'bounds'}}, $mca_xmin);
					push(@{$prop->{'bounds'}}, $mca_xmax);
					push(@{$prop->{'bounds'}}, $mca_ymin);
					push(@{$prop->{'bounds'}}, $mca_ymax);
					push(@{$prop->{'bounds'}}, $mca_zmin);
					push(@{$prop->{'bounds'}}, $mca_zmax);
					$prop->{'volume'} = $mca_volume;
				}



#			&cgi_lib::common::message('$mca_id='.$mca_id, $LOG) if(defined $mca_id);
				$mca_id -= 0;
			}
		}

		$sth_cmm_sel->execute($cdi_id) or die $dbh->errstr;
		my $cmm_rows = $sth_cmm_sel->rows();
		$sth_cmm_sel->finish;

#	my $cm_delcause='DELETE';
		my $cm_delcause;
		unless($cmm_rows>0){
			$sth_cmm_ins->execute($cur_cm_modified->{$cdi_id}->{'cm_entry'},$cm_delcause,$mca_id,$cdi_id) or die $dbh->errstr;
			$sth_cmm_ins->finish;
		}else{
			$sth_cmm_upd->execute($cur_cm_modified->{$cdi_id}->{'cm_entry'},$cm_delcause,$mca_id,$cdi_id) or die $dbh->errstr;
			$sth_cmm_upd->finish;
		}

		my $bounds = $prop->{'bounds'};
#	my $cm_volume = defined $prop->{'volume'} && $prop->{'volume'} > 0 ?  &BITS::ConceptArtMapModified::Truncated($prop->{'volume'} / 1000) : 0;
		my $cm_volume = $prop->{'volume'};

		$_ -= 0 for(@$bounds);
		my $b = {
			xmin => $bounds->[0],
			xmax => $bounds->[1],
			ymin => $bounds->[2],
			ymax => $bounds->[3],
			zmin => $bounds->[4],
			zmax => $bounds->[5],
			volume => $cm_volume
		};

		my $cszr_id = 0;
		foreach my $temp_cszr_id (keys(%SEGMENT_ZRANGE)){
			if(defined $SEGMENT_ZRANGE{$temp_cszr_id}->{'min'} && defined $SEGMENT_ZRANGE{$temp_cszr_id}->{'max'}){
				if($b->{'zmin'} >= $SEGMENT_ZRANGE{$temp_cszr_id}->{'min'} && $b->{'zmax'} < $SEGMENT_ZRANGE{$temp_cszr_id}->{'max'}){
					$cszr_id = $temp_cszr_id;
					last;
				}
			}elsif(defined $SEGMENT_ZRANGE{$temp_cszr_id}->{'min'}){
				if($b->{'zmin'} >= $SEGMENT_ZRANGE{$temp_cszr_id}->{'min'}){
					$cszr_id = $temp_cszr_id;
					last;
				}
			}elsif(defined $SEGMENT_ZRANGE{$temp_cszr_id}->{'max'}){
				if($b->{'zmax'} < $SEGMENT_ZRANGE{$temp_cszr_id}->{'max'}){
					$cszr_id = $temp_cszr_id;
					last;
				}
			}
		}

		my $csv_id = 0;
		foreach my $temp_csv_id (keys(%SEGMENT_VALUME)){
			if(defined $SEGMENT_VALUME{$temp_csv_id}->{'min'} && defined $SEGMENT_VALUME{$temp_csv_id}->{'max'}){
				if($cm_volume >= $SEGMENT_VALUME{$temp_csv_id}->{'min'} && $cm_volume < $SEGMENT_VALUME{$temp_csv_id}->{'max'}){
					$csv_id = $temp_csv_id;
					last;
				}
			}elsif(defined $SEGMENT_VALUME{$temp_csv_id}->{'min'}){
				if($cm_volume >= $SEGMENT_VALUME{$temp_csv_id}->{'min'}){
					$csv_id = $temp_csv_id;
					last;
				}
			}elsif(defined $SEGMENT_VALUME{$temp_csv_id}->{'max'}){
				if($cm_volume < $SEGMENT_VALUME{$temp_csv_id}->{'max'}){
					$csv_id = $temp_csv_id;
					last;
				}
			}
		}

#&cgi_lib::common::message('['.$cdi_id.']['.$COMP_DENSITY->{$cdi_id}.']', $LOG);

		my $cm_primitive = exists $ELEMENT->{$cdi_id} ? 1: 0;
		$sth_cmm_upd_xyz->execute(
			$b->{'xmin'},
			$b->{'xmax'},
			$b->{'ymin'},
			$b->{'ymax'},
			$b->{'zmin'},
			$b->{'zmax'},
			$cm_volume,
			$COMP_DENSITY_USE_TERMS->{$cdi_id},
			$COMP_DENSITY_END_TERMS->{$cdi_id},
			$COMP_DENSITY->{$cdi_id},
			$cm_primitive,
			$cszr_id,
			$csv_id,
			$cdi_id
		) or die $dbh->errstr;
		$sth_cmm_upd_xyz->finish;

	}
	say '';
}
