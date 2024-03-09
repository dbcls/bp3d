#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use File::Spec::Functions qw(abs2rel rel2abs catdir catfile splitdir);

use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'..','cgi_lib');
require "webgl_common.pl";
use cgi_lib::common;

$SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit";
sub sigexit {
	my($date) = `date`;
	$date =~ s/\s*$//g;
	print STDERR "[$date] KILL THIS CGI!![$ENV{SCRIPT_NAME}]\n";
	exit(1);
}

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);
my($logfile,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

=pod
$FORM{ag_data}=qq|obj/bp3d/4.0|;
$FORM{f_id}=qq|root|;
$FORM{model}=qq|bp3d|;
$FORM{node}=qq|root|;
$FORM{tree}=qq|isa|;
$FORM{version}=qq|4.0|;
=cut

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
$logfile .=  sprintf(".%02d%02d%02d.%05d",$hour,$min,$sec,$$);

open(my $LOG,"> $logfile");
select($LOG);
$| = 1;
select(STDOUT);

flock($LOG,2);
print $LOG "\n[$logtime]:$0\n";
&cgi_lib::common::message(\%ENV, $LOG);
&cgi_lib::common::message(\%FORM, $LOG);

#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $DATAS = {
	'datas'   => [],
	'total'   => 0,
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

unless(
	exists $FORM{'cmd'} && defined $FORM{'cmd'} &&
	exists $FORM{'ci_id'} && defined $FORM{'ci_id'}
){
#	print &JSON::XS::encode_json($DATAS);
	&gzip_json($DATAS);
	exit;
}

if($FORM{'cmd'} eq 'read'){
	eval{
#		my $ci_id = $FORM{'ci_id'};

		my @SORT;
		if(exists $FORM{'sort'} && defined $FORM{'sort'}){
			my $so = &cgi_lib::common::decodeJSON($FORM{'sort'});
			push(@SORT,@$so) if(defined $so && ref $so eq 'ARRAY');
		}
		if(scalar @SORT == 0){
			push(@SORT,{
				property  => 'cdi_name',
				direction => 'ASC'
			});
		}
#=pod
		my $sql=<<SQL;
select
 cdi.cdi_id,
 cdi.cdi_name,
 cdi.cdi_name_j,
 COALESCE(cd.cd_name,cdi.cdi_name_e),
 cdi.cdi_name_k,
 cdi.cdi_name_l,
 cdi.cdi_syn_j,
 COALESCE(cd.cd_syn,cdi.cdi_syn_e),
 cdi.cdi_def_j,
 COALESCE(cd.cd_def,cdi.cdi_def_e),
 cdi.cdi_taid
from
 concept_data_info as cdi


LEFT JOIN (
  SELECT
   cdi_id,
   cd_name,
   cd_syn,
   cd_def
  FROM
   concept_data
  WHERE
   ci_id=$ci_id AND
   cb_id=$cb_id
 ) cd ON cd.cdi_id = cdi.cdi_id

where
 COALESCE(cdi.is_user_data,false)=false and
 cdi.cdi_delcause is null
 and cdi.ci_id=$ci_id
SQL
#=cut
=pod
=cut
		print $LOG __LINE__,":\$sql=[$sql]\n";

		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$DATAS->{'total'} = $sth->rows();
		$sth->finish;
		undef $sth;
		print $LOG __LINE__,":\$DATAS->{'total'}=[",$DATAS->{'total'},"]\n";

		if(scalar @SORT > 0){
			my @orderby;
			foreach (@SORT){
				next unless(exists $_->{property} && defined $_->{property} && length $_->{property});
				if($_->{property} eq 'cdi_name'){
					push(@orderby,qq|to_number(substring(cdi_name from 4),'9999999') $_->{direction}|);
				}else{
					push(@orderby,qq|$_->{property} $_->{direction} NULLS LAST|);
				}
			}
			$sql .= qq| order by | . join(",",@orderby) if(scalar @orderby > 0);
		}
		$sql .= qq| limit $FORM{'limit'}| if(defined $FORM{'limit'});
		$sql .= qq| offset $FORM{'start'}| if(defined $FORM{'start'});

		print $LOG __LINE__,":\$sql=[$sql]\n";

		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;

		my $cdi_id;
		my $cdi_name;
		my $cdi_name_j;
		my $cdi_name_e;
		my $cdi_name_k;
		my $cdi_name_l;
		my $cdi_syn_j;
		my $cdi_syn_e;
		my $cdi_def_j;
		my $cdi_def_e;
		my $cdi_taid;

		my $column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_id,   undef);
		$sth->bind_col(++$column_number, \$cdi_name,   undef);
		$sth->bind_col(++$column_number, \$cdi_name_j,   undef);
		$sth->bind_col(++$column_number, \$cdi_name_e,   undef);
		$sth->bind_col(++$column_number, \$cdi_name_k,   undef);
		$sth->bind_col(++$column_number, \$cdi_name_l,   undef);
		$sth->bind_col(++$column_number, \$cdi_syn_j,   undef);
		$sth->bind_col(++$column_number, \$cdi_syn_e,   undef);
		$sth->bind_col(++$column_number, \$cdi_def_j,   undef);
		$sth->bind_col(++$column_number, \$cdi_def_e,   undef);
		$sth->bind_col(++$column_number, \$cdi_taid,   undef);

		while($sth->fetch){

			next unless(defined $cdi_name);

#			$cdi_syn_e =~ s/(;)/$1<br>/g if(defined $cdi_syn_e);

			my $HASH = {
				ci_id      => $ci_id-0,
				cdi_name   => $cdi_name,
#				cdi_name_j => $cdi_name_j,
				cdi_name_e => $cdi_name_e,
#				cdi_name_k => $cdi_name_k,
#				cdi_name_l => $cdi_name_l,
#				cdi_syn_j  => $cdi_syn_j,
#				cdi_syn_e  => $cdi_syn_e,
#				cdi_def_j  => $cdi_def_j,
#				cdi_def_e  => $cdi_def_e,
#				cdi_taid   => $cdi_taid
			};

			push(@{$DATAS->{'datas'}},$HASH);
		}
		$sth->finish;
		undef $sth;

		$DATAS->{'success'} = JSON::XS::true;
	};
	if($@){
		print $LOG __LINE__,":",$@,"\n";
	}
}
#print &JSON::XS::encode_json($DATAS);
&gzip_json($DATAS);

close($LOG);
