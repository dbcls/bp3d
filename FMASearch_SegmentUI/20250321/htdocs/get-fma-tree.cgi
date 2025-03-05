#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use JSON::XS;
use Data::Dumper;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
use BITS::Config;
require "webgl_common.pl";
use cgi_lib::common;

use constant {
	DEBUG => BITS::Config::DEBUG
};

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);
$FORM{$_} = &cgi_lib::common::decodeUTF8($FORM{$_}) for(keys(%FORM));
my($logfile,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
$logfile .=  sprintf(".%02d%02d%02d.%05d",$hour,$min,$sec,$$);

my $LOG;
if(DEBUG){
	open($LOG,">> $logfile");
	select($LOG);
	$| = 1;
	select(STDOUT);

	flock($LOG,2);
	print $LOG "\n[$logtime]:$0\n";
	&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);
}
my @TREE = ();


$SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit";
sub sigexit {
	my($date) = `date`;
	$date =~ s/\s*$//g;
	print STDERR "[$date] KILL THIS CGI!![$ENV{SCRIPT_NAME}]\n";
	exit(1);
}

unless(
	exists $FORM{BITS::Config::LOCATION_HASH_CIID_KEY}   && defined $FORM{BITS::Config::LOCATION_HASH_CIID_KEY}   && $FORM{BITS::Config::LOCATION_HASH_CIID_KEY} =~ /^[0-9]+$/ &&
	exists $FORM{BITS::Config::LOCATION_HASH_CBID_KEY}   && defined $FORM{BITS::Config::LOCATION_HASH_CBID_KEY}   && $FORM{BITS::Config::LOCATION_HASH_CBID_KEY} =~ /^[0-9]+$/ &&
	exists $FORM{BITS::Config::RELATION_TYPE_NAME} && defined $FORM{BITS::Config::RELATION_TYPE_NAME} && $FORM{BITS::Config::RELATION_TYPE_NAME} =~ /_(up|down:?)$/ &&
	exists $FORM{BITS::Config::LOCATION_HASH_ID_KEY}   && defined $FORM{BITS::Config::LOCATION_HASH_ID_KEY}   && length $FORM{BITS::Config::LOCATION_HASH_ID_KEY}
){
	my $DATAS = {
		"datas" => [],
		"total" => 0,
		"success" => JSON::XS::false
	};
	$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8(qq|JSON形式が違います|);
	&gzip_json($DATAS);
	exit;
}

my $ci_id = $FORM{BITS::Config::LOCATION_HASH_CIID_KEY} - 0;
my $cb_id = $FORM{BITS::Config::LOCATION_HASH_CBID_KEY} - 0;
my $type  = $FORM{BITS::Config::RELATION_TYPE_NAME};
my $cdi_name = $FORM{BITS::Config::LOCATION_HASH_ID_KEY};

my @SORT;
if(exists $FORM{'sort'} && defined $FORM{'sort'}){
	my $sort = &cgi_lib::common::decodeJSON($FORM{'sort'});
	push(@SORT,map {
		$_->{'direction'} = 'ASC' unless(exists $_->{'direction'} && defined $_->{'direction'});
		if($_->{'property'} eq BITS::Config::LOCATION_HASH_NAME_KEY){
			$_->{'property'} = 'cd_name'
		}elsif($_->{'property'} eq BITS::Config::LOCATION_HASH_ID_KEY){
			$_->{'property'} = 'cdi_name'
		}
		$_;
	} grep {exists $_->{'property'} && defined $_->{'property'}} @$sort) if(defined $sort && ref $sort eq 'ARRAY');
}
if(scalar @SORT == 0){
	push(@SORT,{
		property  => 'cd_name',
		direction => 'ASC'
	});
}

my $column_number = 0;

my $sth_cdi = $dbh->prepare(qq|select cdi_id from concept_data_info where cdi_delcause is null and ci_id=$ci_id and cdi_name=?|) or die $dbh->errstr;
$sth_cdi->execute($cdi_name) or die $dbh->errstr;
my $cdi_id;
$column_number = 0;
$sth_cdi->bind_col(++$column_number, \$cdi_id,   undef);
$sth_cdi->fetch;
$sth_cdi->finish;
undef $sth_cdi;
&cgi_lib::common::message($cdi_id, $LOG) if(defined $LOG);

if(defined $cdi_id){
	$sth_cdi = $dbh->prepare(qq|select cdi_name,cd_name from concept_data as cd left join(select ci_id,cdi_id,cdi_name from concept_data_info) as cdi on cdi.ci_id=cd.ci_id and cdi.cdi_id=cd.cdi_id where cd_delcause is null and cd.ci_id=$ci_id and cd.cb_id=$cb_id and cd.cdi_id=?|) or die $dbh->errstr;

	my $sth_bul = $dbh->prepare(qq|select bul_id,bul_name_e from buildup_logic where bul_delcause is null and bul_use|) or die $dbh->errstr;
	$sth_bul->execute() or die $dbh->errstr;
	my $bul_id;
	my $bul_name_e;
	my %BUL_ID2NAME;
	my %BUL_NAME2ID;
	$column_number = 0;
	$sth_bul->bind_col(++$column_number, \$bul_id,   undef);
	$sth_bul->bind_col(++$column_number, \$bul_name_e,   undef);
	while($sth_bul->fetch){
		next unless(defined $bul_id && defined $bul_name_e);
		$BUL_ID2NAME{$bul_id} = lc($bul_name_e);
		$BUL_NAME2ID{lc($bul_name_e)} = $bul_id;
	}
	$sth_bul->finish;
	undef $sth_bul;
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%BUL_ID2NAME, 1), $LOG) if(defined $LOG);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%BUL_NAME2ID, 1), $LOG) if(defined $LOG);

	my $bul_ids = join(',',sort keys(%BUL_ID2NAME));
	my $sth_ct_up = $dbh->prepare(qq|select ct.cdi_pid,ct.bul_id,ct.f_potids from concept_tree as ct where ct.ci_id=$ci_id and ct.cb_id=$cb_id and ct.cdi_id=? and ct.cdi_pid is not null and ct.bul_id in ($bul_ids)|) or die $dbh->errstr;
	my $sth_ct_down = $dbh->prepare(qq|select ct.cdi_id,ct.bul_id,ct.f_potids from concept_tree as ct where ct.ci_id=$ci_id and ct.cb_id=$cb_id and ct.cdi_pid=? and ct.cdi_id is not null and ct.bul_id in ($bul_ids)|) or die $dbh->errstr;

	my $sth_cbr = $dbh->prepare(qq|select cbr.f_potid,f_potname from concept_build_relation as cbr left join (select f_potid,f_potname from fma_partof_type) as fpt on fpt.f_potid=cbr.f_potid where ci_id=$ci_id and cb_id=$cb_id and cbr_use|) or die $dbh->errstr;
	$sth_cbr->execute() or die $dbh->errstr;
	my $f_potid;
	my $f_potname;
	my %CBR_ID2NAME;
	my %CBR_NAME2ID;
	$column_number = 0;
	$sth_cbr->bind_col(++$column_number, \$f_potid,   undef);
	$sth_cbr->bind_col(++$column_number, \$f_potname,   undef);
	while($sth_cbr->fetch){
		next unless(defined $f_potid && defined $f_potname);
		$CBR_ID2NAME{$f_potid} = $f_potname;
		$CBR_NAME2ID{$f_potname} = $f_potid;
	}
	$sth_cbr->finish;
	undef $sth_cbr;
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%CBR_ID2NAME, 1), $LOG) if(defined $LOG);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%CBR_NAME2ID, 1), $LOG) if(defined $LOG);

	if($FORM{BITS::Config::RELATION_TYPE_NAME} =~ /^(.+)_(up|down)$/){
		my $relation = $1;
		my $direction = $2;
		my $sth_ct;
		if($direction eq 'up'){
			$sth_ct = $sth_ct_up;
		}elsif($direction eq 'down'){
			$sth_ct = $sth_ct_down;
		}
		if(defined $sth_ct){
			$sth_ct->execute($cdi_id) or die $dbh->errstr;
			if($sth_ct->rows()>0){
				$column_number = 0;
				my $ct_cdi_id;
				my $ct_bul_id;
				my $ct_f_potids;
				$sth_ct->bind_col(++$column_number, \$ct_cdi_id,   undef);
				$sth_ct->bind_col(++$column_number, \$ct_bul_id,   undef);
				$sth_ct->bind_col(++$column_number, \$ct_f_potids,   undef);
				while($sth_ct->fetch){
					next unless(defined $ct_cdi_id && defined $ct_bul_id);
					if($relation eq 'is_a'){
						next unless($BUL_NAME2ID{$relation} == $ct_bul_id);
						push(@TREE,{
#							ci_id => $ci_id - 0,
#							cb_id => $cb_id - 0,
							cdi_id => $ct_cdi_id - 0
						});
					}elsif(defined $ct_f_potids && length $ct_f_potids && exists $CBR_NAME2ID{$relation} && defined $CBR_NAME2ID{$relation}){
						foreach my $f_potid (split(/;/,$ct_f_potids)){
							next unless(exists $CBR_ID2NAME{$f_potid} && defined $CBR_ID2NAME{$f_potid});
							next unless($f_potid == $CBR_NAME2ID{$relation});
							push(@TREE,{
#								ci_id => $ci_id - 0,
#								cb_id => $cb_id - 0,
								cdi_id => $ct_cdi_id - 0
							});
						}
					}
				}
			}
			$sth_ct->finish;
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\@TREE, 1), $LOG) if(defined $LOG);

			foreach my $hash (@TREE){
				$sth_ct->execute($hash->{'cdi_id'}) or die $dbh->errstr;
				if($sth_ct->rows()>0){
					my $cnum = 0;
					$column_number = 0;
					my $ct_cdi_id;
					my $ct_bul_id;
					my $ct_f_potids;
					$sth_ct->bind_col(++$column_number, \$ct_cdi_id,   undef);
					$sth_ct->bind_col(++$column_number, \$ct_bul_id,   undef);
					$sth_ct->bind_col(++$column_number, \$ct_f_potids,   undef);
					while($sth_ct->fetch){
						next unless(defined $ct_cdi_id && defined $ct_bul_id);
						if($relation eq 'is_a'){
							next unless($BUL_NAME2ID{$relation} == $ct_bul_id);
							$cnum++;
						}elsif(defined $ct_f_potids && length $ct_f_potids && exists $CBR_NAME2ID{$relation} && defined $CBR_NAME2ID{$relation}){
							foreach my $f_potid (split(/;/,$ct_f_potids)){
								next unless(exists $CBR_ID2NAME{$f_potid} && defined $CBR_ID2NAME{$f_potid});
								next unless($f_potid == $CBR_NAME2ID{$relation});
								$cnum++;
							}
						}
					}
					$hash->{'cnum'} = $cnum;
					$hash->{'leaf'} = $cnum ? JSON::XS::false : JSON::XS::true;
				}else{
					$hash->{'cnum'} = 0;
					$hash->{'leaf'} = JSON::XS::true
				}
				$sth_ct->finish;
			}
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\@TREE, 1), $LOG) if(defined $LOG);
		}
	}
	foreach my $hash (@TREE){
		$sth_cdi->execute($hash->{'cdi_id'}) or die $dbh->errstr;
		my $cdi_name;
		my $cdi_name_e;
		$column_number = 0;
		$sth_cdi->bind_col(++$column_number, \$cdi_name,   undef);
		$sth_cdi->bind_col(++$column_number, \$cdi_name_e,   undef);
		$sth_cdi->fetch;
		$sth_cdi->finish;
#		$hash->{'cdi_name'} = $cdi_name;
#		$hash->{'cdi_name_e'} = $cdi_name_e;
		$hash->{BITS::Config::TERM_ID_DATA_FIELD_ID} = $cdi_name;
		$hash->{BITS::Config::TERM_NAME_DATA_FIELD_ID} = $cdi_name_e;
		delete $hash->{'cdi_id'};
	}
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\@TREE, 1), $LOG) if(defined $LOG);

#	@TREE = map {$_->{'cdi_id'} -= 0;$_} sort {$a->{'cdi_name_e'} cmp $b->{'cdi_name_e'}} @TREE;
	if(scalar @SORT > 0){
		foreach (@SORT){
			if(uc($_->{'direction'}) eq 'ASC'){
				@TREE = sort {$a->{$_->{'property'}} cmp $b->{$_->{'property'}}} @TREE;
			}else{
				@TREE = sort {$b->{$_->{'property'}} cmp $a->{$_->{'property'}}} @TREE;
			}
		}
	}
#	@TREE = map {$_->{'cdi_id'} -= 0;$_} @TREE;


}
&gzip_json(\@TREE);

close($LOG) if(defined $LOG);
