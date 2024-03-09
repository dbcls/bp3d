#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';


use JSON::XS;
use File::Basename;
use Cwd qw(abs_path);
use File::Spec::Functions qw(abs2rel rel2abs catdir catfile splitdir);
use CGI;
use CGI::Carp qw(fatalsToBrowser);
#use CGI::Carp::DebugScreen ( debug => 1 );
use Data::Dumper;
use DBD::Pg;
use POSIX;
use List::Util;
use Hash::Merge;
use Time::HiRes;
use Time::Piece;

my $t0 = [&Time::HiRes::gettimeofday()];

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;

use BITS::Config;
#use BITS::VTK;
#use BITS::Voxel;
#use BITS::ConceptArtMapModified;
use BITS::ConceptArtMapPart;

#use obj2deci;
require "webgl_common.pl";
use cgi_lib::common;
use AG::login;

my $is_subclass_cdi_name = $BITS::ConceptArtMapPart::is_subclass_cdi_name;
my $is_subclass_abbr_isa = $BITS::ConceptArtMapPart::is_subclass_abbr_isa;
my $is_subclass_abbr_partof = $BITS::ConceptArtMapPart::is_subclass_abbr_partof;
my $is_subclass_abbr_LR = $BITS::ConceptArtMapPart::is_subclass_abbr_LR;

my $subclass_format = $BITS::ConceptArtMapPart::subclass_format;

my $query = CGI->new;
my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
#my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);
$FORM{$_} = &cgi_lib::common::decodeUTF8($FORM{$_}) for(sort keys(%FORM));
$COOKIE{$_} = &cgi_lib::common::decodeUTF8($COOKIE{$_}) for(sort keys(%COOKIE));
if(exists($COOKIE{'ag_annotation.session'})){
	my $session_info = {};
	$session_info->{'PARAMS'}->{$_} = $FORM{$_} for(sort keys(%FORM));
	$session_info->{'COOKIE'}->{$_} = $COOKIE{$_} for(sort keys(%COOKIE));
	&AG::login::setSessionHistory($session_info);
}

my($log_file,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

#my @extlist = qw|.cgi|;
#my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);

my($epocsec,$microsec) = &Time::HiRes::gettimeofday();
my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);

$log_file .= qq|.$FORM{'cmd'}| if(exists $FORM{'cmd'});

$log_file .=  sprintf(".%02d%02d%02d.%05d",$hour,$min,$sec,$$);

my $LOG;
open($LOG,">> $log_file");
select($LOG);
$| = 1;
select(STDOUT);

if(defined $LOG){
	&cgi_lib::common::message(sprintf("\n%04d:%04d/%02d/%02d %02d:%02d:%02d.%d",__LINE__,$year+1900,$mon+1,$mday,$hour,$min,$sec,$microsec), $LOG);
	&cgi_lib::common::message(\%ENV, $LOG);
	&cgi_lib::common::message(\%FORM, $LOG);
	&cgi_lib::common::dumper($epocsec, $LOG);

}

$FORM{'cmd'} = 'read' unless(defined $FORM{'cmd'});

my $DATAS = {
	'datas' => [],
	'total' => 0,
	'success' => JSON::XS::false
};

my $ci_id=$FORM{'ci_id'};
my $cb_id=$FORM{'cb_id'};
my $md_id=$FORM{'md_id'};
my $mv_id=$FORM{'mv_id'};

$md_id=1 unless(defined $md_id && $md_id =~ /^[1-9][0-9]*$/);
unless(defined $mv_id && $mv_id =~ /^[1-9][0-9]*$/){
	$mv_id = undef;
	$ci_id = undef;
	$cb_id = undef;
	my $sth_mv;
	if(defined $FORM{'mv_id'} && $FORM{'mv_id'} =~ /^\-[1-9][0-9]*$/){
		$sth_mv = $dbh->prepare("select mv_id from model_version where mv_delcause is null and mv_use and md_id=? order by mv_id desc limit 2") or die $dbh->errstr;
		$sth_mv->execute($md_id) or die $dbh->errstr;
		if($sth_mv->rows()>1){
			$sth_mv->bind_col(1, \$mv_id, undef);
			while($sth_mv->fetch){}
		}
		$sth_mv->finish;
		undef $sth_mv;
	}else{
		$sth_mv = $dbh->prepare("select max(mv_id) from model_version where mv_delcause is null and mv_use and md_id=?") or die $dbh->errstr;
		$sth_mv->execute($md_id) or die $dbh->errstr;
		$sth_mv->bind_col(1, \$mv_id, undef);
		$sth_mv->fetch;
		$sth_mv->finish;
		undef $sth_mv;
	}
	if(defined $mv_id){
		$sth_mv = $dbh->prepare("select ci_id,cb_id from model_version where md_id=? and mv_id=?") or die $dbh->errstr;
		$sth_mv->execute($md_id,$mv_id) or die $dbh->errstr;
		$sth_mv->bind_col(1, \$ci_id, undef);
		$sth_mv->bind_col(2, \$cb_id, undef);
		$sth_mv->fetch;
		$sth_mv->finish;
		undef $sth_mv;
	}
}

if(defined $LOG){
	&cgi_lib::common::message($ci_id, $LOG);
	&cgi_lib::common::message($cb_id, $LOG);
	&cgi_lib::common::message($md_id, $LOG);
	&cgi_lib::common::message($mv_id, $LOG);
}

unless(defined $ci_id && defined $cb_id && defined $md_id && defined $mv_id){
	$DATAS->{'success'} = JSON::XS::true;
	&cgi_lib::common::printContentJSON($DATAS,\%FORM);
	close($LOG) if(defined $LOG);
	exit;
}


if(defined $LOG){
	&cgi_lib::common::message('$md_id='.$md_id, $LOG);
	&cgi_lib::common::message('$mv_id='.$mv_id, $LOG);
	&cgi_lib::common::message('$ci_id='.$ci_id, $LOG);
	&cgi_lib::common::message('$cb_id='.$cb_id, $LOG);
}

unless(
	defined $ci_id && $ci_id =~ /^[0-9]+$/ &&
	defined $cb_id && $cb_id =~ /^[0-9]+$/
){
	&gzip_json($DATAS);
	&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);
	close($LOG) if(defined $LOG);
	exit;
}

$FORM{'ci_id'}=$ci_id;
$FORM{'cb_id'}=$cb_id;
$FORM{'md_id'}=$md_id;
$FORM{'mv_id'}=$mv_id;


#&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);
#$DATAS = &cmd_read(%FORM);
&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);
if($FORM{'cmd'} eq 'read'){
	$DATAS = &cmd_read(%FORM);
}
elsif($FORM{'cmd'} eq 'update'){
	$DATAS = &cmd_update(%FORM);
}
&gzip_json($DATAS);
&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);
close($LOG) if(defined $LOG);
exit;


sub cmd_read {
	my %FORM = @_;
	my $DATAS = {
		'datas' => [],
		'total' => 0,
		'success' => JSON::XS::false
	};
	my $ci_id=$FORM{'ci_id'};
	my $cb_id=$FORM{'cb_id'};
	my $cdi_name=$FORM{'cdi_name'};

	return $DATAS unless(defined $cdi_name && length $cdi_name);

	my $sql;
	my $sth;
	my $column_number;

	my $cdi_id;
	my $cdi_name_e;
	my $cdi_syn_e;
	my $cdi_pid;
	my $cdi_pname;
	my $cdi_pname_e;
	my $cdi_super_id;
	my $cdi_super_name;
	my $crl_id;

	my $cdi_super_class_id;
	my $cdi_super_class_name;
	my $cdi_super_part_id;
	my $cdi_super_part_name;

	my $datas;
	my $cdi_ids_hash;
	my $cdi_names_hash;

	my $cp_abbr;
	my $cl_abbr;
	my $temp_cdi_name;
	my $temp_cp_id;
	my $temp_cl_id;

	return $DATAS unless($cdi_name =~ /$is_subclass_cdi_name/);

	$cdi_pname = $1;
	$cp_abbr = $2;
	$cl_abbr = $3;

	if(defined $LOG){
		&cgi_lib::common::message($cdi_name, $LOG);
		&cgi_lib::common::message($cdi_pname, $LOG);
		&cgi_lib::common::message($cp_abbr, $LOG);
		&cgi_lib::common::message($cl_abbr, $LOG);
	}

	my $temp_crl_id = 3;
	my $infer_crl_id = 4;
	if($cp_abbr =~ /$is_subclass_abbr_partof/){
		$temp_crl_id = 4;
		$infer_crl_id = 3;
	}

	if(defined $LOG){
		&cgi_lib::common::message($temp_crl_id, $LOG);
		&cgi_lib::common::message($infer_crl_id, $LOG);
	}

	$sql=qq|
SELECT
  cdi.cdi_id,
  COALESCE(cd.cd_name,cdi.cdi_name_e)
FROM
  concept_data_info AS cdi
LEFT JOIN
  (SELECT * FROM concept_data WHERE ci_id=$ci_id AND cb_id=$cb_id) AS cd ON cd.ci_id=cdi.ci_id AND cd.cdi_id=cdi.cdi_id
WHERE
 cdi.ci_id=$ci_id AND cdi.cdi_name=?
|;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute($cdi_pname) or die $dbh->errstr;
	if($sth->rows()>0){
		$column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_pid, undef);
		$sth->bind_col(++$column_number, \$cdi_pname_e, undef);
		$sth->fetch;
		$cdi_pid -= 0 if(defined $cdi_pid);
	}
	$sth->finish;
	undef $sth;

	return $DATAS unless(defined $cdi_pid);


	$sql=q|
SELECT
  cdi1.cdi_id,
  cdi1.cdi_name,
  cdi1.cdi_name_e,
  cdi1.cdi_syn_e,
  cdi1.cdi_super_id,
  cdi2.cdi_name,
  cdi1.cp_id,
  cdi1.cl_id
FROM
  concept_data_info AS cdi1
LEFT JOIN
  concept_data_info AS cdi2 ON cdi1.ci_id=cdi2.ci_id AND cdi1.cdi_super_id=cdi2.cdi_id
WHERE
 cdi1.ci_id=? AND cdi1.cdi_pid=?
|;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute($ci_id,$cdi_pid) or die $dbh->errstr;
	if($sth->rows()>0){
		$column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_id, undef);
		$sth->bind_col(++$column_number, \$temp_cdi_name, undef);
		$sth->bind_col(++$column_number, \$cdi_name_e, undef);
		$sth->bind_col(++$column_number, \$cdi_syn_e, undef);
		$sth->bind_col(++$column_number, \$cdi_super_id, undef);
		$sth->bind_col(++$column_number, \$cdi_super_name, undef);
		$sth->bind_col(++$column_number, \$temp_cp_id, undef);
		$sth->bind_col(++$column_number, \$temp_cl_id, undef);
		while($sth->fetch){
			$cdi_id -= 0 if(defined $cdi_id);
			$cdi_pid -= 0 if(defined $cdi_pid);
			$cdi_super_id -= 0 if(defined $cdi_super_id);
			$temp_cp_id -= 0 if(defined $temp_cp_id);
			$temp_cl_id -= 0 if(defined $temp_cl_id);
			$cdi_ids_hash->{$cdi_id} = $cdi_names_hash->{$temp_cdi_name} = {
				cdi_id         => $cdi_id,
				cdi_name       => $temp_cdi_name,
				cdi_name_e     => $cdi_name_e,
				cdi_syn_e      => $cdi_syn_e,
				cdi_pid        => $cdi_pid,
				cdi_pname      => $cdi_pname,
				cdi_super_id   => $cdi_super_id,
				cdi_super_name => $cdi_super_name,
				cp_id          => $temp_cp_id,
				cl_id          => $temp_cl_id,
			};
			push(@$datas, $cdi_ids_hash->{$cdi_id});
		}
	}
	$sth->finish;
	undef $sth;

	if(defined $LOG){
		&cgi_lib::common::message($cdi_ids_hash, $LOG);
		&cgi_lib::common::message($cdi_names_hash, $LOG);
		&cgi_lib::common::message($datas, $LOG);
	}

	if(defined $datas && ref $datas eq 'ARRAY' && scalar @$datas){
		my @ids = keys(%$cdi_ids_hash);
		$sql=sprintf(q|
SELECT
  ct.cdi_id,
  ct.cdi_pid,
  cdi.cdi_name,
  ct.crl_id
FROM
  concept_tree AS ct
LEFT JOIN
  concept_data_info AS cdi ON ct.ci_id=cdi.ci_id AND ct.cdi_pid=cdi.cdi_id
WHERE
 ct.ci_id=? AND ct.cb_id=? AND ct.cdi_id in (%s)
|,join(',',map {'?'} @ids));
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute($ci_id,$cb_id,@ids) or die $dbh->errstr;
		if($sth->rows()>0){
			my $cdi_ct_pid;
			my $cdi_ct_pname;
			$column_number = 0;
			$sth->bind_col(++$column_number, \$cdi_id, undef);
			$sth->bind_col(++$column_number, \$cdi_ct_pid, undef);
			$sth->bind_col(++$column_number, \$cdi_ct_pname, undef);
			$sth->bind_col(++$column_number, \$crl_id, undef);
			while($sth->fetch){
				next unless(
					exists	$cdi_ids_hash->{$cdi_id} &&
					defined	$cdi_ids_hash->{$cdi_id} &&
					ref			$cdi_ids_hash->{$cdi_id} eq 'HASH' &&
					exists	$cdi_ids_hash->{$cdi_id}->{'cdi_name'} &&
					defined	$cdi_ids_hash->{$cdi_id}->{'cdi_name'}
				);
				$temp_cdi_name = $cdi_ids_hash->{$cdi_id}->{'cdi_name'};

				next unless($temp_cdi_name =~ /$is_subclass_cdi_name/);

				my $temp_cp_abbr = $2;

				my $temp_crl_id = 3;
				my $infer_crl_id = 4;
				if($temp_cp_abbr =~ /$is_subclass_abbr_partof/){
					$temp_crl_id = 4;
					$infer_crl_id = 3;
				}


				if($temp_crl_id==3){
					if($temp_crl_id==$crl_id){
						$cdi_ids_hash->{$cdi_id}->{'cdi_super_class_id'} = $cdi_ct_pid-0;
						$cdi_ids_hash->{$cdi_id}->{'cdi_super_class_name'} = $cdi_ct_pname;
					}
					else{
						$cdi_ids_hash->{$cdi_id}->{'cdi_super_part_id'} = $cdi_ct_pid-0;
						$cdi_ids_hash->{$cdi_id}->{'cdi_super_part_name'} = $cdi_ct_pname;
					}
				}
				else{
					if($temp_crl_id==$crl_id){
						$cdi_ids_hash->{$cdi_id}->{'cdi_super_part_id'} = $cdi_ct_pid-0;
						$cdi_ids_hash->{$cdi_id}->{'cdi_super_part_name'} = $cdi_ct_pname;
					}
					else{
						$cdi_ids_hash->{$cdi_id}->{'cdi_super_class_id'} = $cdi_ct_pid-0;
						$cdi_ids_hash->{$cdi_id}->{'cdi_super_class_name'} = $cdi_ct_pname;
					}
				}
			}
		}
		$sth->finish;
		undef $sth;
	}

	if(defined $LOG){
		&cgi_lib::common::message($cdi_ids_hash, $LOG);
		&cgi_lib::common::message($cdi_names_hash, $LOG);
		&cgi_lib::common::message($datas, $LOG);
	}


	if(defined $cdi_pid){
		my $concept_laterality_hash;
		my @temp_cl_abbrs;
		my $temp_cl_id;
		my $temp_cl_abbr;
		my $temp_cl_prefix;
		if($cl_abbr =~ /$is_subclass_abbr_LR/){
			@temp_cl_abbrs = qw/L R/;
		}
		else{
			@temp_cl_abbrs = qw/U/;
		}
		$sql=sprintf(q|
SELECT
  cl_id,
  cl_abbr,
  cl_prefix
FROM
  concept_laterality
WHERE
 cl_use AND cl_abbr in (%s)
|,join(',',map {'?'} @temp_cl_abbrs));
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute(@temp_cl_abbrs) or die $dbh->errstr;
		if($sth->rows()>0){
			$column_number = 0;
			$sth->bind_col(++$column_number, \$temp_cl_id, undef);
			$sth->bind_col(++$column_number, \$temp_cl_abbr, undef);
			$sth->bind_col(++$column_number, \$temp_cl_prefix, undef);
			while($sth->fetch){
				$concept_laterality_hash->{$temp_cl_abbr} = {
					cl_id => $temp_cl_id - 0,
					cl_abbr => $temp_cl_abbr,
					cl_prefix => $temp_cl_prefix,
				};
			}
		}
		$sth->finish;
		undef $sth;

		#未登録の場合
		my $temp_cp_id;
		my $temp_cp_abbr;
		my $temp_cp_prefix;
		my $temp_crl_id;
		my $temp_crl_name;
		my $add_cdi_names_hash;
		$sql=q|
SELECT
  cp.cp_id,
  cp.cp_abbr,
  cp.cp_prefix,
  cp.crl_id,
  crl.crl_name
FROM
  concept_part AS cp
LEFT JOIN
  concept_relation_logic AS crl ON crl.crl_id=cp.crl_id
WHERE
 cp_use
|;
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		if($sth->rows()>0){
			$column_number = 0;
			$sth->bind_col(++$column_number, \$temp_cp_id, undef);
			$sth->bind_col(++$column_number, \$temp_cp_abbr, undef);
			$sth->bind_col(++$column_number, \$temp_cp_prefix, undef);
			$sth->bind_col(++$column_number, \$temp_crl_id, undef);
			$sth->bind_col(++$column_number, \$temp_crl_name, undef);
			while($sth->fetch){
				next unless(defined $temp_cp_abbr && length $temp_cp_abbr);

				foreach my $temp_cl_abbr (@temp_cl_abbrs){

					my $temp_cdi_name = sprintf($subclass_format,$cdi_pname,$temp_cp_abbr,$temp_cl_abbr);
					my $temp_cdi_name_e = (defined $temp_cp_prefix && length $temp_cp_prefix) ? sprintf('%s %s', $temp_cp_prefix, $cdi_pname_e) : $cdi_pname_e;

					if(exists $cdi_names_hash->{$temp_cdi_name}){
						$cdi_names_hash->{$temp_cdi_name}->{'cdi_name_e'} = $temp_cdi_name_e unless(exists $cdi_names_hash->{$temp_cdi_name}->{'cdi_name_e'});
						$cdi_names_hash->{$temp_cdi_name}->{'crl_id'}     = $temp_crl_id - 0 unless(exists $cdi_names_hash->{$temp_cdi_name}->{'crl_id'});
						$cdi_names_hash->{$temp_cdi_name}->{'crl_name'}   = $temp_crl_name   unless(exists $cdi_names_hash->{$temp_cdi_name}->{'crl_name'});
						$cdi_names_hash->{$temp_cdi_name}->{'cp_id'}      = $temp_cp_id - 0  unless(exists $cdi_names_hash->{$temp_cdi_name}->{'cp_id'});
						$cdi_names_hash->{$temp_cdi_name}->{'cp_abbr'}    = $temp_cp_abbr    unless(exists $cdi_names_hash->{$temp_cdi_name}->{'cp_abbr'});
						$cdi_names_hash->{$temp_cdi_name}->{'cl_abbr'}    = $temp_cl_abbr    unless(exists $cdi_names_hash->{$temp_cdi_name}->{'cl_abbr'});
						unless(exists $cdi_names_hash->{$temp_cdi_name}->{'cl_id'}){
							$cdi_names_hash->{$temp_cdi_name}->{'cl_id'} = $concept_laterality_hash->{$temp_cl_abbr}->{'cl_id'} if(exists $concept_laterality_hash->{$temp_cl_abbr});
						}
						next;
					}
					$add_cdi_names_hash->{$temp_cdi_name} = {
						cdi_name   => $temp_cdi_name,
						cdi_name_e => $temp_cdi_name_e,
						crl_id     => $temp_crl_id - 0,
						crl_name   => $temp_crl_name,
						cp_id      => $temp_cp_id - 0,
						cp_abbr    => $temp_cp_abbr,
						cl_abbr    => $temp_cl_abbr,
					};
					$add_cdi_names_hash->{$temp_cdi_name}->{'cl_id'} = $concept_laterality_hash->{$temp_cl_abbr}->{'cl_id'} if(exists $concept_laterality_hash->{$temp_cl_abbr});
				}
			}
		}
		$sth->finish;
		undef $sth;

		&cgi_lib::common::message($cdi_id, $LOG) if(defined $LOG);
		if(defined $LOG){
#			&cgi_lib::common::message($cdi_ids_hash, $LOG);
			&cgi_lib::common::message($cdi_names_hash, $LOG);
#			&cgi_lib::common::message($datas, $LOG);
		}

		if(defined $add_cdi_names_hash && ref $add_cdi_names_hash eq 'HASH' && scalar keys(%$add_cdi_names_hash)){

			if(defined $LOG){
				&cgi_lib::common::message([sort keys(%$add_cdi_names_hash)], $LOG);
			}

			foreach my $temp_cdi_name (keys(%$add_cdi_names_hash)){

				my $temp_crl_id = $add_cdi_names_hash->{$temp_cdi_name}->{'crl_id'};
				my $infer_crl_id = 4;
				if($temp_crl_id == 4){
					$infer_crl_id = 3;
				}

				$cdi_names_hash->{$temp_cdi_name} = {
					cdi_id         => undef,
					cdi_name       => $temp_cdi_name,
					cdi_name_e     => $add_cdi_names_hash->{$temp_cdi_name}->{'cdi_name_e'},
					cdi_syn_e      => undef,
					cdi_pid        => $cdi_pid,
					cdi_pname      => $cdi_pname,
					cdi_super_id   => undef,
					cdi_super_name => undef,
					cp_id          => $add_cdi_names_hash->{$temp_cdi_name}->{'cp_id'},
					cp_abbr        => $add_cdi_names_hash->{$temp_cdi_name}->{'cp_abbr'},
					cl_id          => $add_cdi_names_hash->{$temp_cdi_name}->{'cl_id'},
					cl_abbr        => $add_cdi_names_hash->{$temp_cdi_name}->{'cl_abbr'},
					crl_id         => $add_cdi_names_hash->{$temp_cdi_name}->{'crl_id'},
					crl_name       => $add_cdi_names_hash->{$temp_cdi_name}->{'crl_name'},
				};
				push(@$datas, $cdi_names_hash->{$temp_cdi_name});

				if($temp_crl_id==3){
					$cdi_names_hash->{$temp_cdi_name}->{'cdi_super_class_id'} = $cdi_pid-0;
					$cdi_names_hash->{$temp_cdi_name}->{'cdi_super_class_name'} = $cdi_pname;
				}else{
					$cdi_names_hash->{$temp_cdi_name}->{'cdi_super_part_id'} = $cdi_pid-0;
					$cdi_names_hash->{$temp_cdi_name}->{'cdi_super_part_name'} = $cdi_pname;

					$sql=q|
SELECT
  ct.cdi_pid,
  cdi.cdi_name
FROM
  concept_tree AS ct
LEFT JOIN
  concept_data_info AS cdi ON ct.ci_id=cdi.ci_id AND ct.cdi_pid=cdi.cdi_id
WHERE
 ct.ci_id=? AND ct.cb_id=? AND ct.cdi_id=? AND ct.crl_id=?
|;
					$sth = $dbh->prepare($sql) or die $dbh->errstr;
					$sth->execute($ci_id,$cb_id,$cdi_pid,$infer_crl_id) or die $dbh->errstr;
					if($sth->rows()>0){
						$column_number = 0;
						$sth->bind_col(++$column_number, \$cdi_super_class_id, undef);
						$sth->bind_col(++$column_number, \$cdi_super_class_name, undef);
						$sth->fetch;
					}
					$sth->finish;
					undef $sth;

					$cdi_names_hash->{$temp_cdi_name}->{'cdi_super_class_id'} = $cdi_super_class_id-0;
					$cdi_names_hash->{$temp_cdi_name}->{'cdi_super_class_name'} = $cdi_super_class_name;
				}
			}
		}
	}

	if(defined $LOG){
#		&cgi_lib::common::message($cdi_ids_hash, $LOG);
		&cgi_lib::common::message($cdi_names_hash, $LOG);
#		&cgi_lib::common::message($datas, $LOG);
	}

	if(defined $datas && ref $datas eq 'ARRAY' && scalar @$datas){
		push(@{$DATAS->{'datas'}}, @$datas);
		$DATAS->{'total'} = scalar @$datas;
	}
	$DATAS->{'success'} = JSON::XS::true;

	return $DATAS;
}

sub cmd_update {
	my %FORM = @_;
	my $DATAS = {
		'datas' => [],
		'total' => 0,
		'success' => JSON::XS::false
	};
#	my $ci_id=$FORM{'ci_id'};
#	my $cb_id=$FORM{'cb_id'};
	my $datas = exists $FORM{'datas'} && defined $FORM{'datas'} && length $FORM{'datas'} ? &decodeJSON($FORM{'datas'}) : undef;
	if(defined $datas && ref $datas eq 'ARRAY' && scalar @$datas){

		$dbh->{'AutoCommit'} = 0;
		$dbh->{'RaiseError'} = 1;
		eval{

			my $sth_cb_sel = $dbh->prepare("SELECT ci_id,cb_id FROM concept_build WHERE cb_use ORDER BY cb_order") or die $dbh->errstr;
			$sth_cb_sel->execute() or die $dbh->errstr;
			if($sth_cb_sel->rows()>0){
				my $ci_id;
				my $cb_id;
				my $column_number = 0;
				$sth_cb_sel->bind_col(++$column_number, \$ci_id, undef);
				$sth_cb_sel->bind_col(++$column_number, \$cb_id, undef);
				while($sth_cb_sel->fetch){
					foreach my $data (@$datas){
						&cgi_lib::common::dumper($data, $LOG) if(defined $LOG);
						&BITS::ConceptArtMapPart::clear_subclass_tree(%$data, ci_id=>$ci_id, cb_id=>$cb_id, dbh => $dbh, LOG => $LOG);


						my $cdi_name = $data->{'cdi_name'};
						next unless($cdi_name =~ /$is_subclass_cdi_name/);
						my $cdi_pname = $1;
						my $cp_abbr = $2;
						my $cl_abbr = $3;
						my $super_name;
						my $crl_id = 3;
						my $infer_crl_id = 4;
						if($cp_abbr =~ /$is_subclass_abbr_partof/){
							$super_name = exists $data->{'cdi_super_class_name'} && defined $data->{'cdi_super_class_name'} && length $data->{'cdi_super_class_name'} ? $data->{'cdi_super_class_name'} : undef;
							$crl_id = 4;
							$infer_crl_id = 3;
						}
						else{
							$super_name = exists $data->{'cdi_super_part_name'} && defined $data->{'cdi_super_part_name'} && length $data->{'cdi_super_part_name'} ? $data->{'cdi_super_part_name'} : undef;
						}

						&BITS::ConceptArtMapPart::create_subclass(%$data, super_name=>$super_name, ci_id=>$ci_id, cb_id=>$cb_id, dbh => $dbh, LOG => $LOG);
					}
				}
			}
			$sth_cb_sel->finish;
			undef $sth_cb_sel;
			$dbh->commit;

			$DATAS->{'success'} = JSON::XS::true;
		};
		if($@){
			&cgi_lib::common::message($@, $LOG);
			$DATAS->{'success'} = JSON::XS::false;
			$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8($@);
			$dbh->rollback;
		}
		$dbh->{'AutoCommit'} = 1;
		$dbh->{'RaiseError'} = 0;
	}
	return $DATAS;
}
