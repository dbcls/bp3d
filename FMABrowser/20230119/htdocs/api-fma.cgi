#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
use BITS::Config;
use BITS::ConceptArtMapPart;
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
my($logfile,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

$FORM{$_} = &cgi_lib::common::decodeUTF8($FORM{$_}) for(keys(%FORM));

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
#$logfile .= '.'.sprintf("%04d%02d%02d%02d",$year+1900,$mon+1,$mday,$hour);
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
#&setDefParams(\%FORM,\%COOKIE);

#&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);

#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $DATAS = {
#	"datas" => [],
	"total" => 0,
	"success" => JSON::XS::false
};
#$FORM{BITS::Config::LOCATION_HASH_CBID_KEY} = 11;

unless(
	exists $FORM{BITS::Config::LOCATION_HASH_CIID_KEY} && defined $FORM{BITS::Config::LOCATION_HASH_CIID_KEY} && $FORM{BITS::Config::LOCATION_HASH_CIID_KEY} =~ /^[0-9]+$/ &&
	exists $FORM{BITS::Config::LOCATION_HASH_CBID_KEY} && defined $FORM{BITS::Config::LOCATION_HASH_CBID_KEY} && $FORM{BITS::Config::LOCATION_HASH_CBID_KEY} =~ /^[0-9]+$/
){
	$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8(qq|JSON形式が違います|);
	&gzip_json($DATAS);
	exit;
}

my $ci_id = $FORM{BITS::Config::LOCATION_HASH_CIID_KEY} - 0;
my $cb_id = $FORM{BITS::Config::LOCATION_HASH_CBID_KEY} - 0;

$dbh->{'AutoCommit'} = 0;
$dbh->{'RaiseError'} = 1;
eval{
	if(
		exists	$FORM{BITS::Config::ID_DATA_FIELD_ID} &&
		defined	$FORM{BITS::Config::ID_DATA_FIELD_ID} &&
		length	$FORM{BITS::Config::ID_DATA_FIELD_ID} &&
		exists	$FORM{BITS::Config::NAME_DATA_FIELD_ID} &&
		defined	$FORM{BITS::Config::NAME_DATA_FIELD_ID} &&
		length	$FORM{BITS::Config::NAME_DATA_FIELD_ID}
	){
		my $cdi_name = $FORM{BITS::Config::ID_DATA_FIELD_ID};
		my $cdi_name_e = $FORM{BITS::Config::NAME_DATA_FIELD_ID};
		my $cdi_id;
		my $cdi_count = 0;
		my $cd_count = 0;
		my $sth_cdi_sel = $dbh->prepare(qq|SELECT cdi_id FROM concept_data_info WHERE ci_id=? AND cdi_name=?|) or die $dbh->errstr;
		my $sth_cd_sel = $dbh->prepare(qq|SELECT cdi_id FROM concept_data WHERE ci_id=? AND cb_id=? AND cdi_id=?|) or die $dbh->errstr;
		my $sth_cdi_upd = $dbh->prepare(qq|UPDATE concept_data_info SET cdi_name_e=? WHERE ci_id=? AND cdi_id=?|) or die $dbh->errstr;
		my $sth_cd_upd = $dbh->prepare(qq|UPDATE concept_data SET cd_name=? WHERE ci_id=? AND cb_id=? AND cdi_id=?|) or die $dbh->errstr;
		my $column_number = 0;
		$sth_cdi_sel->execute($ci_id,$cdi_name) or die $dbh->errstr;
		$cdi_count = $sth_cdi_sel->rows();
		if($cdi_count>0){
			$column_number = 0;
			$sth_cdi_sel->bind_col(++$column_number, \$cdi_id, undef);
			$sth_cdi_sel->fetch;
		}
		$sth_cdi_sel->finish;

		if(defined $cdi_id){
			$sth_cd_sel->execute($ci_id,$cb_id,$cdi_id) or die $dbh->errstr;
			$cd_count = $sth_cd_sel->rows();
			$sth_cd_sel->finish;
		}

		unless($cdi_count>0 && $cd_count>0){
			my $cdi_pname;
			my $cdi_pid;
			my $cd_pcount = 0;
			$cdi_pname = $1 if($cdi_name =~ /$BITS::ConceptArtMapPart::is_subclass_cdi_name/);
			if(defined $cdi_pname && length $cdi_pname){
				$sth_cdi_sel->execute($ci_id,$cdi_pname) or die $dbh->errstr;
				if($sth_cdi_sel->rows()>0){
					$column_number = 0;
					$sth_cdi_sel->bind_col(++$column_number, \$cdi_pid, undef);
					$sth_cdi_sel->fetch;
				}
			}
			if(defined $cdi_pid){
				$sth_cd_sel->execute($ci_id,$cb_id,$cdi_pid) or die $dbh->errstr;
				$cd_pcount = $sth_cd_sel->rows();
				$sth_cd_sel->finish;
			}
			if($cd_pcount>0){
				$cdi_id = &BITS::ConceptArtMapPart::create_subclass(
					dbh   => $dbh,
					LOG   => $LOG,
					ci_id => $ci_id,
					cb_id => $cb_id,
					cdi_name=> $cdi_name
				);
			}
		}

		$sth_cdi_upd->execute($cdi_name_e,$ci_id,$cdi_id) or die $dbh->errstr;
		$sth_cdi_upd->finish;

		$sth_cd_upd->execute($cdi_name_e,$ci_id,$cb_id,$cdi_id) or die $dbh->errstr;
		$sth_cd_upd->finish;

		$dbh->commit();

		undef $sth_cdi_sel;
		undef $sth_cd_sel;
		undef $sth_cdi_upd;
		undef $sth_cd_upd;
	}
	$DATAS->{'success'} = JSON::XS::true;
};
if($@){
	$DATAS->{'msg'} = $@;
	$DATAS->{'success'} = JSON::XS::false;
	$dbh->rollback;
}
$dbh->{'AutoCommit'} = 1;
$dbh->{'RaiseError'} = 0;

&gzip_json($DATAS);

close($LOG) if(defined $LOG);

exit;