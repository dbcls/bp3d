#!/opt/services/ag/local/perl/bin/perl

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
					push(@orderby,qq|to_number(substring(cdi_name from 4),'999999') $_->{direction}|);
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
				ci_id      => $ci_id - 0,
				cb_id      => $cb_id - 0,
				cdi_id     => $cdi_id - 0,
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
		$DATAS->{'msg'} = $@;
		print $LOG __LINE__,":",$DATAS->{'msg'},"\n";
	}
}
elsif(lc $FORM{'cmd'} eq 'read_synonym'){
	my $cdi_id=$FORM{'cdi_id'};
	eval{

		my $sql=<<SQL;
SELECT
  cd.cdi_id
 ,cdi.cdi_name
 ,cd.cd_name
 ,cd.cd_syn
FROM
  concept_data AS cd
LEFT JOIN concept_data_info AS cdi ON cdi.ci_id=cd.ci_id AND cdi.cdi_id=cd.cdi_id
WHERE
  cd.ci_id=? AND cd.cb_id=? AND cd.cdi_id=?
SQL

		print $LOG __LINE__,":\$sql=[$sql]\n";

		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute($ci_id,$cb_id,$cdi_id) or die $dbh->errstr;
		$DATAS->{'total'} = $sth->rows();

		my $cdi_id;
		my $cdi_name;
		my $cd_name;
		my $cd_syn;
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_id,   undef);
		$sth->bind_col(++$column_number, \$cdi_name, undef);
		$sth->bind_col(++$column_number, \$cd_name,  undef);
		$sth->bind_col(++$column_number, \$cd_syn,   undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;

		if(defined $cd_syn){
			if($cd_syn =~ /;/){
				$cd_syn = [split(/;/,$cd_syn)];
			}else{
				$cd_syn = [$cd_syn];
			}
		}
		my $HASH = {
			ci_id    => $ci_id - 0,
			cb_id    => $cb_id - 0,
			cdi_id   => $cdi_id - 0,
			cdi_name => $cdi_name,
			cd_name  => $cd_name,
			cd_syn   => $cd_syn,
		};

if(1){
		my $sql_synonym=qq|
SELECT
  cds.cds_id
 ,cds.cds_bid
 ,cds.cs_id
 ,cs.cs_name
 ,cds.cds_added
 ,cds.cds_order
FROM
  concept_data_synonym AS cds
LEFT JOIN concept_synonym AS cs ON cs.cs_id=cds.cs_id
LEFT JOIN concept_data_synonym_type AS cdst ON cdst.cdst_id=cds.cdst_id
WHERE
      cds.ci_id=?
  AND cds.cb_id=?
  AND cds.cdi_id=?
  AND cdst.cdst_name='synonym'
ORDER BY
  cs.cs_name
|;
		my $sth_synonym = $dbh->prepare($sql_synonym) or die $dbh->errstr;
		$sth_synonym->execute($ci_id,$cb_id,$cdi_id) or die $dbh->errstr;
		my $cs_id;
		my $cds_id;
		my $cds_bid;
		my $cds_added;
		my $cs_name;
		my $cds_order;
		my $CDS;
		$column_number = 0;
		$sth_synonym->bind_col(++$column_number, \$cds_id,    undef);
		$sth_synonym->bind_col(++$column_number, \$cds_bid,   undef);
		$sth_synonym->bind_col(++$column_number, \$cs_id,     undef);
		$sth_synonym->bind_col(++$column_number, \$cs_name,   undef);
		$sth_synonym->bind_col(++$column_number, \$cds_added, undef);
		$sth_synonym->bind_col(++$column_number, \$cds_order, undef);
		while($sth_synonym->fetch){
			my $hash;
			$hash->{'cds_id'} = $cds_id;
			$hash->{'cds_bid'} = $cds_bid;
			$hash->{'cs_id'} = $cs_id;
			$hash->{'cs_name'} = $cs_name;
			$hash->{'cds_added'} = $cds_added eq '1' ? JSON::XS::true : JSON::XS::false;
			$hash->{'cds_order'} = $cds_order - 0;
			$hash->{'cds_added_auto'} = defined $cds_bid ? JSON::XS::true : JSON::XS::false;
			push(@{$CDS}, $hash);
		}
		$sth_synonym->finish;
		undef $sth_synonym;
		$HASH->{'cds'} = $CDS;
}

		push(@{$DATAS->{'datas'}},$HASH);

		$DATAS->{'success'} = JSON::XS::true;
	};
	if($@){
		$DATAS->{'msg'} = $@;
		print $LOG __LINE__,":",$DATAS->{'msg'},"\n";
	}
}
elsif(lc $FORM{'cmd'} eq 'update_synonym'){
	if(
				exists	$FORM{'cdi_name'}
		&&	defined	$FORM{'cdi_name'}
		&&	length	$FORM{'cdi_name'}
		&&	exists	$FORM{'cd_syn'}
		&&	defined	$FORM{'cd_syn'}
		&&	length	$FORM{'cd_syn'}
	){
		my $cdi_name = $FORM{'cdi_name'};
		my $synonym_arr = &cgi_lib::common::decodeJSON($FORM{'cd_syn'});
		if(defined $synonym_arr && ref $synonym_arr eq 'ARRAY'){

			$dbh->{'AutoCommit'} = 0;
			$dbh->{'RaiseError'} = 1;
			eval{


				my $column_number;
				my $cdi_id;
				my $cdi_id_arr;
				my $cdi_id_hash;
				my $cdi_id_added_hash;

#concept_data_info
				my $sth_cdi_sel = $dbh->prepare(qq|select cdi_id from concept_data_info where ci_id=? AND cdi_name=?|) or die $dbh->errstr;
				$sth_cdi_sel->execute($ci_id,$cdi_name) or die $dbh->errstr;
				$column_number = 0;
				$sth_cdi_sel->bind_col(++$column_number, \$cdi_id, undef);
				$sth_cdi_sel->fetch;
				$sth_cdi_sel->finish;
				undef $sth_cdi_sel;

				$cdi_id_hash->{$cdi_id} = undef if(defined $cdi_id);

#concept_synonym
				my $CS_ID2NAME;
				my $CS_NAME2ID;
				if(defined $cdi_id){
					my $cs_id;
					my $cs_name;
					my $sth_cs_sel = $dbh->prepare(qq|select cs_id,cs_name from concept_synonym|) or die $dbh->errstr;
					$sth_cs_sel->execute() or die $dbh->errstr;
					$column_number = 0;
					$sth_cs_sel->bind_col(++$column_number, \$cs_id, undef);
					$sth_cs_sel->bind_col(++$column_number, \$cs_name, undef);
					while($sth_cs_sel->fetch){
						$CS_ID2NAME->{$cs_id}->{$cs_name} = undef;
						$CS_NAME2ID->{$cs_name}->{$cs_id} = undef;
					}
					$sth_cs_sel->finish;
					undef $sth_cs_sel;
				}

#concept_data_synonym_type
				my $CDST_ID2NAME;
				my $CDST_NAME2ID;
				if(defined $cdi_id){
					my $cdst_id;
					my $cdst_name;
					my $sth_cdst_sel = $dbh->prepare(qq|SELECT cdst_id,cdst_name from concept_data_synonym_type|) or die $dbh->errstr;
					$sth_cdst_sel->execute() or die $dbh->errstr;
					$column_number = 0;
					$sth_cdst_sel->bind_col(++$column_number, \$cdst_id, undef);
					$sth_cdst_sel->bind_col(++$column_number, \$cdst_name, undef);
					while($sth_cdst_sel->fetch){
						$CDST_ID2NAME->{$cdst_id} = $cdst_name;
						$CDST_NAME2ID->{$cdst_name} = $cdst_id;
					}
					$sth_cdst_sel->finish;
					undef $sth_cdst_sel;
				}

#concept_data
				my $CD_ID2NAME;
				my $CD_ID2NAMESYN;
				my $CD_NAMESYN2ID;
				if(defined $cdi_id){
					my $cdi_id;
					my $cd_name;
					my $cd_syn;
					my $sth_cd_sel = $dbh->prepare(qq|select cdi_id,cd_name,cd_syn from concept_data where ci_id=? AND cb_id=?|) or die $dbh->errstr;
					$sth_cd_sel->execute($ci_id,$cb_id) or die $dbh->errstr;
					$column_number = 0;
					$sth_cd_sel->bind_col(++$column_number, \$cdi_id, undef);
					$sth_cd_sel->bind_col(++$column_number, \$cd_name, undef);
					$sth_cd_sel->bind_col(++$column_number, \$cd_syn, undef);
					while($sth_cd_sel->fetch){
						$cd_name =~ s/\s+/ /g;
						$cd_name =~ s/^\s+//g;
						$cd_name =~ s/\s+$//g;
						$CD_ID2NAME->{$cdi_id}= lc $cd_name;
						$CD_ID2NAMESYN->{$cdi_id}->{lc $cd_name} = undef;
						$CD_NAMESYN2ID->{lc $cd_name}->{$cdi_id} = undef;
						next unless(defined $cd_syn && length $cd_syn);
						map {
							s/\s+/ /g;
							s/^\s+//g;
							s/\s+$//g;
							$CD_ID2NAMESYN->{$cdi_id}->{lc $_} = undef;
							$CD_NAMESYN2ID->{lc $_}->{$cdi_id} = undef;
						} split(/;/,$cd_syn)
					}
					$sth_cd_sel->finish;
					undef $sth_cd_sel;
				}

#concept_tree_trio
				my $CTT;
				my $CTT_P;
				my $CTT_L;
				my $CTT_R;
				if(defined $cdi_id){
					my $cdi_pid;
					my $cdi_lid;
					my $cdi_rid;
					my $sth_ctt_sel = $dbh->prepare(qq|select cdi_pid,cdi_lid,cdi_rid from concept_tree_trio where ci_id=? AND cb_id=?|) or die $dbh->errstr;
					$sth_ctt_sel->execute($ci_id,$cb_id) or die $dbh->errstr;
					$column_number = 0;
					$sth_ctt_sel->bind_col(++$column_number, \$cdi_pid, undef);
					$sth_ctt_sel->bind_col(++$column_number, \$cdi_lid, undef);
					$sth_ctt_sel->bind_col(++$column_number, \$cdi_rid, undef);
					while($sth_ctt_sel->fetch){
						$CTT->{$cdi_pid} = $CTT_P->{$cdi_pid} = {
							cdi_lid => $cdi_lid,
							cdi_rid => $cdi_rid
						};
						$CTT->{$cdi_lid} = $CTT_L->{$cdi_lid} = {
							cdi_pid => $cdi_pid,
							cdi_rid => $cdi_rid
						};
						$CTT->{$cdi_rid} = $CTT_R->{$cdi_rid} = {
							cdi_lid => $cdi_lid,
							cdi_pid => $cdi_pid
						};
					}
					$sth_ctt_sel->finish;
					undef $sth_ctt_sel;
				}

#concept_relation_logic
				my $CRL_HASH;
				my $crt_id;

				if(defined $cdi_id){
					my $crl_id;
					my $crl_name;
					my $sth_crl_sel = $dbh->prepare(qq|select crl_id,crl_name from concept_relation_logic|) or die $dbh->errstr;
					$sth_crl_sel->execute() or die $dbh->errstr;
					$column_number = 0;
					$sth_crl_sel->bind_col(++$column_number, \$crl_id, undef);
					$sth_crl_sel->bind_col(++$column_number, \$crl_name, undef);
					while($sth_crl_sel->fetch){
						$CRL_HASH->{$crl_name} = $crl_id;
					}
					$sth_crl_sel->finish;
					undef $sth_crl_sel;
				}

#concept_relation_type
				if(defined $cdi_id){
					my $sth_crt_sel = $dbh->prepare(qq|select crt_id from concept_relation_type where crt_name=?|) or die $dbh->errstr;
					$sth_crt_sel->execute('lexicalsuper') or die $dbh->errstr;
					$column_number = 0;
					$sth_crt_sel->bind_col(++$column_number, \$crt_id, undef);
					$sth_crt_sel->fetch;
					$sth_crt_sel->finish;
					undef $sth_crt_sel;
				}

#concept_tree
				my $CT_ID_CRT_PID_HASH;
				my $CT_ID_PID_CRT_HASH;
				my $CT_PID_CRT_ID_HASH;
				my $CT_PID_ID_CRT_HASH;
				my $CT_ID_PID_ISA_HASH;
				my $CT_PID_ID_ISA_HASH;
				if(
							defined	$cdi_id
					&&	defined	$CRL_HASH
					&&	ref			$CRL_HASH eq 'HASH'
					&&	exists	$CRL_HASH->{'is_a'}
					&&	defined	$CRL_HASH->{'is_a'}
					&&	exists	$CRL_HASH->{'part_of'}
					&&	defined	$CRL_HASH->{'part_of'}
					&&	defined	$crt_id
				){

					my $sth_ct_sel = $dbh->prepare(qq|select cdi_id,cdi_pid,crl_id,crt_ids from concept_tree where ci_id=? AND cb_id=?|) or die $dbh->errstr;
					$sth_ct_sel->execute($ci_id,$cb_id) or die $dbh->errstr;
					$column_number = 0;
					my $cdi_id;
					my $cdi_pid;
					my $crl_id;
					my $crt_ids;
					$sth_ct_sel->bind_col(++$column_number, \$cdi_id, undef);
					$sth_ct_sel->bind_col(++$column_number, \$cdi_pid, undef);
					$sth_ct_sel->bind_col(++$column_number, \$crl_id, undef);
					$sth_ct_sel->bind_col(++$column_number, \$crt_ids, undef);
					while($sth_ct_sel->fetch){
						if($crl_id eq $CRL_HASH->{'is_a'}){
							$CT_ID_PID_ISA_HASH->{$cdi_id}->{$cdi_pid} = undef;
							$CT_PID_ID_ISA_HASH->{$cdi_pid}->{$cdi_id} = undef;
						}
						elsif($crl_id eq $CRL_HASH->{'part_of'}){
							next unless(defined $crt_ids && length $crt_ids);
							map {
								$CT_ID_CRT_PID_HASH->{$cdi_id}->{$_}->{$cdi_pid} = undef;
								$CT_ID_PID_CRT_HASH->{$cdi_id}->{$cdi_pid}->{$_} = undef;

								$CT_PID_CRT_ID_HASH->{$cdi_pid}->{$_}->{$cdi_id} = undef;
								$CT_PID_ID_CRT_HASH->{$cdi_pid}->{$cdi_id}->{$_} = undef;

							} split(/;/,$crt_ids);
						}
					}
					$sth_ct_sel->finish;
					undef $sth_ct_sel;
				}

#concept_synonym
#				my $CS_ID2NAME;
#				my $CS_NAME2ID;
				if(defined $cdi_id){

					my $cs_id;
					my $cs_name;
					my $sth_cs_sel = $dbh->prepare(qq|select cs_id,cs_name from concept_synonym|) or die $dbh->errstr;
					$sth_cs_sel->execute() or die $dbh->errstr;
					$column_number = 0;
					$sth_cs_sel->bind_col(++$column_number, \$cs_id, undef);
					$sth_cs_sel->bind_col(++$column_number, \$cs_name, undef);
					while($sth_cs_sel->fetch){
						$CS_ID2NAME->{$cs_id} = $cs_name;
						$CS_NAME2ID->{$cs_name} = $cs_id;
					}
					$sth_cs_sel->finish;
					undef $sth_cs_sel;

					my $sth_cs_ins = $dbh->prepare(qq|INSERT INTO concept_synonym (cs_name) VALUES (?) RETURNING cs_id|) or die $dbh->errstr;
					foreach my $synonym (@{$synonym_arr}){
						next unless(
									defined	$synonym
							&&	ref			$synonym eq 'HASH'
							&&	exists	$synonym->{'synonym'}
							&&	defined	$synonym->{'synonym'}
							&&	length	$synonym->{'synonym'}
						);
						my $cs_name = $synonym->{'synonym'};
						unless(exists $CS_NAME2ID->{$cs_name}){
							my $cs_id;
							$sth_cs_ins->execute($cs_name) or die $dbh->errstr;
							$column_number=0;
							$sth_cs_ins->bind_col(++$column_number, \$cs_id, undef);
							$sth_cs_ins->fetch;
							$sth_cs_ins->finish;

							$CS_ID2NAME->{$cs_id} = $cs_name;
							$CS_NAME2ID->{$cs_name} = $cs_id;
						}
					}
#					undef $sth_cs_ins;


					my $sth_cds_sel = $dbh->prepare(qq|SELECT cds_id FROM concept_data_synonym WHERE ci_id=? AND cb_id=? AND cdi_id=? AND cs_id=?|) or die $dbh->errstr;
					my $sth_cds_ins = $dbh->prepare(qq|INSERT INTO concept_data_synonym (ci_id,cb_id,cdi_id,cs_id,cds_added,cdst_id) VALUES (?,?,?,?,true,?) RETURNING cds_id|) or die $dbh->errstr;
					my $sth_cds_ins_b = $dbh->prepare(qq|INSERT INTO concept_data_synonym (ci_id,cb_id,cdi_id,cs_id,cds_bid,cds_added,cdst_id) VALUES (?,?,?,?,?,true,?)|) or die $dbh->errstr;
					my $sth_cds_del = $dbh->prepare(qq|DELETE FROM concept_data_synonym WHERE ci_id=? AND cb_id=? AND cdi_id=? AND cs_id=?|) or die $dbh->errstr;
					my $sth_cds_del_b = $dbh->prepare(qq|DELETE FROM concept_data_synonym WHERE ci_id=? AND cb_id=? AND cds_bid=? RETURNING cdi_id|) or die $dbh->errstr;

#					&cgi_lib::common::message($synonym_arr, $LOG) if(defined $LOG);
					foreach my $synonym (@{$synonym_arr}){
						next unless(
									defined	$synonym
							&&	ref			$synonym eq 'HASH'
							&&	exists	$synonym->{'synonym'}
							&&	defined	$synonym->{'synonym'}
							&&	length	$synonym->{'synonym'}
						);
						my $cs_name = $synonym->{'synonym'};
						my $cs_id = $CS_NAME2ID->{$cs_name};
						if($synonym->{'is_deleted'}){
#							&cgi_lib::common::message($synonym, $LOG) if(defined $LOG);
#							&cgi_lib::common::message($ci_id, $LOG) if(defined $LOG);
#							&cgi_lib::common::message($cb_id, $LOG) if(defined $LOG);
#							&cgi_lib::common::message($cdi_id, $LOG) if(defined $LOG);
#							&cgi_lib::common::message($cs_id, $LOG) if(defined $LOG);

							my $cds_id;
							$sth_cds_sel->execute($ci_id,$cb_id,$cdi_id,$cs_id) or die $dbh->errstr;
							$column_number=0;
							$sth_cds_sel->bind_col(++$column_number, \$cds_id, undef);
							$sth_cds_sel->fetch;
							$sth_cds_sel->finish;

							&cgi_lib::common::message($cds_id, $LOG) if(defined $LOG);

							my $temp_cdi_id;
							$sth_cds_del_b->execute($ci_id,$cb_id,$cds_id) or die $dbh->errstr;
							$column_number=0;
							$sth_cds_del_b->bind_col(++$column_number, \$temp_cdi_id, undef);
							while($sth_cds_del_b->fetch){
								$cdi_id_hash->{$temp_cdi_id} = undef;
							}
							$sth_cds_del_b->finish;

#							&cgi_lib::common::message($synonym, $LOG) if(defined $LOG);

							$sth_cds_del->execute($ci_id,$cb_id,$cdi_id,$cs_id) or die $dbh->errstr;
							$sth_cds_del->finish;

#							&cgi_lib::common::message($synonym, $LOG) if(defined $LOG);
						}
						elsif($synonym->{'is_edited'}){

							my $cds_id;
							$sth_cds_sel->execute($ci_id,$cb_id,$cdi_id,$cs_id) or die $dbh->errstr;
							$column_number=0;
							$sth_cds_sel->bind_col(++$column_number, \$cds_id, undef);
							$sth_cds_sel->fetch;
							$sth_cds_sel->finish;

							next if(defined $cds_id);

							$sth_cds_ins->execute($ci_id,$cb_id,$cdi_id,$cs_id,$CDST_NAME2ID->{'synonym'}) or die $dbh->errstr;
							$column_number=0;
							$sth_cds_ins->bind_col(++$column_number, \$cds_id, undef);
							$sth_cds_ins->fetch;
							$sth_cds_ins->finish;

							$cdi_id_added_hash->{$cdi_id} = {
								cds_id => $cds_id,
								cs_name => $cs_name
							};

							next unless(
										exists	$CTT->{$cdi_id}
								&&	defined	$CTT->{$cdi_id}
								&&	ref			$CTT->{$cdi_id} eq 'HASH'
								
							);

							my $cs_pname = &getParentFromName($cs_name);
							next unless(
										defined	$cs_pname
								&&	length	$cs_pname
								&&	exists	$CD_NAMESYN2ID->{lc $cs_pname}
								&&	defined	$CD_NAMESYN2ID->{lc $cs_pname}
								&&	ref			$CD_NAMESYN2ID->{lc $cs_pname} eq 'HASH'
							);

							my $is_added = 0;
							foreach my $cdi_pid (keys(%{$CD_NAMESYN2ID->{lc $cs_pname}})){
								next unless(
											exists	$CTT->{$cdi_pid}
									&&	defined	$CTT->{$cdi_pid}
									&&	ref			$CTT->{$cdi_pid} eq 'HASH'
								);
=pod
								my $cs_lname = ucfirst(lc(sprintf("%s of %s",$CD_ID2NAME->{$CTT->{$cdi_id}->{'cdi_lid'}},$CD_ID2NAME->{$CTT->{$cdi_pid}->{'cdi_lid'}})));
								my $cs_rname = ucfirst(lc(sprintf("%s of %s",$CD_ID2NAME->{$CTT->{$cdi_id}->{'cdi_rid'}},$CD_ID2NAME->{$CTT->{$cdi_pid}->{'cdi_rid'}})));

								my $cs_lid;
								my $cs_rid;
								unless(exists $CS_NAME2ID->{$cs_lname}){
									$sth_cs_ins->execute($cs_lname) or die $dbh->errstr;
									$column_number=0;
									$sth_cs_ins->bind_col(++$column_number, \$cs_lid, undef);
									$sth_cs_ins->fetch;
									$sth_cs_ins->finish;

									$CS_ID2NAME->{$cs_lid} = $cs_lname;
									$CS_NAME2ID->{$cs_lname} = $cs_lid;
								}
								else{
									$cs_lid = $CS_NAME2ID->{$cs_lname};
								}
								unless(exists $CS_NAME2ID->{$cs_rname}){
									$sth_cs_ins->execute($cs_rname) or die $dbh->errstr;
									$column_number=0;
									$sth_cs_ins->bind_col(++$column_number, \$cs_rid, undef);
									$sth_cs_ins->fetch;
									$sth_cs_ins->finish;

									$CS_ID2NAME->{$cs_rid} = $cs_rname;
									$CS_NAME2ID->{$cs_rname} = $cs_rid;
								}
								else{
									$cs_rid = $CS_NAME2ID->{$cs_rname};
								}

								my $cdi_lid = $CTT->{$cdi_id}->{'cdi_lid'};
								my $cdi_rid = $CTT->{$cdi_id}->{'cdi_rid'};

								my $cds_lid;
								my $cds_rid;
								$sth_cds_sel->execute($ci_id,$cb_id,$cdi_lid,$cs_lid) or die $dbh->errstr;
								$column_number=0;
								$sth_cds_sel->bind_col(++$column_number, \$cds_lid, undef);
								$sth_cds_sel->fetch;
								$sth_cds_sel->finish;

								$sth_cds_sel->execute($ci_id,$cb_id,$cdi_rid,$cs_rid) or die $dbh->errstr;
								$column_number=0;
								$sth_cds_sel->bind_col(++$column_number, \$cds_rid, undef);
								$sth_cds_sel->fetch;
								$sth_cds_sel->finish;

								unless(defined $cds_lid){
									$sth_cds_ins_b->execute($ci_id,$cb_id,$cdi_lid,$cs_lid,$cds_id,$CDST_NAME2ID->{'synonym'}) or die $dbh->errstr;
									$sth_cds_ins_b->finish;
								}
								unless(defined $cds_rid){
									$sth_cds_ins_b->execute($ci_id,$cb_id,$cdi_rid,$cs_rid,$cds_id,$CDST_NAME2ID->{'synonym'}) or die $dbh->errstr;
									$sth_cds_ins_b->finish;
								}
								$cdi_id_hash->{$cdi_lid} = undef;
								$cdi_id_hash->{$cdi_rid} = undef;

								$cdi_id_added_hash->{$cdi_lid} = {
									cds_id => $cds_id,
									cs_name => $cs_lname
								};
								$cdi_id_added_hash->{$cdi_rid} = {
									cds_id => $cds_id,
									cs_name => $cs_rname
								};
=cut

								foreach my $ctt_key (keys(%{$CTT->{$cdi_pid}})){

									my $cs_lname = ucfirst(lc(sprintf("%s of %s",$CD_ID2NAME->{$CTT->{$cdi_id}->{$ctt_key}},$CD_ID2NAME->{$CTT->{$cdi_pid}->{$ctt_key}})));

									my $cs_lid;
									unless(exists $CS_NAME2ID->{$cs_lname}){
										$sth_cs_ins->execute($cs_lname) or die $dbh->errstr;
										$column_number=0;
										$sth_cs_ins->bind_col(++$column_number, \$cs_lid, undef);
										$sth_cs_ins->fetch;
										$sth_cs_ins->finish;

										$CS_ID2NAME->{$cs_lid} = $cs_lname;
										$CS_NAME2ID->{$cs_lname} = $cs_lid;
									}
									else{
										$cs_lid = $CS_NAME2ID->{$cs_lname};
									}

									my $cdi_lid = $CTT->{$cdi_id}->{$ctt_key};

									my $cds_lid;
									$sth_cds_sel->execute($ci_id,$cb_id,$cdi_lid,$cs_lid) or die $dbh->errstr;
									$column_number=0;
									$sth_cds_sel->bind_col(++$column_number, \$cds_lid, undef);
									$sth_cds_sel->fetch;
									$sth_cds_sel->finish;


									unless(defined $cds_lid){
										$sth_cds_ins_b->execute($ci_id,$cb_id,$cdi_lid,$cs_lid,$cds_id,$CDST_NAME2ID->{'synonym'}) or die $dbh->errstr;
										$sth_cds_ins_b->finish;
									}
									$cdi_id_hash->{$cdi_lid} = undef;

									$cdi_id_added_hash->{$cdi_lid} = {
										cds_id => $cds_id,
										cs_name => $cs_lname
									};
								}
								$is_added = 1;
								last;
							}
							unless($is_added){
								foreach my $ctt_key (keys(%{$CTT->{$cdi_id}})){
									my $cs_lname = ucfirst(lc(sprintf("%s of %s",$CD_ID2NAME->{$CTT->{$cdi_id}->{$ctt_key}},$cs_pname)));
									my $cs_lid;
									unless(exists $CS_NAME2ID->{$cs_lname}){
										$sth_cs_ins->execute($cs_lname) or die $dbh->errstr;
										$column_number=0;
										$sth_cs_ins->bind_col(++$column_number, \$cs_lid, undef);
										$sth_cs_ins->fetch;
										$sth_cs_ins->finish;

										$CS_ID2NAME->{$cs_lid} = $cs_lname;
										$CS_NAME2ID->{$cs_lname} = $cs_lid;
									}
									else{
										$cs_lid = $CS_NAME2ID->{$cs_lname};
									}
									my $cdi_lid = $CTT->{$cdi_id}->{$ctt_key};
									my $cds_lid;
									$sth_cds_sel->execute($ci_id,$cb_id,$cdi_lid,$cs_lid) or die $dbh->errstr;
									$column_number=0;
									$sth_cds_sel->bind_col(++$column_number, \$cds_lid, undef);
									$sth_cds_sel->fetch;
									$sth_cds_sel->finish;
									unless(defined $cds_lid){
										$sth_cds_ins_b->execute($ci_id,$cb_id,$cdi_lid,$cs_lid,$cds_id,$CDST_NAME2ID->{'synonym'}) or die $dbh->errstr;
										$sth_cds_ins_b->finish;
									}
									$cdi_id_hash->{$cdi_lid} = undef;
									$cdi_id_added_hash->{$cdi_lid} = {
										cds_id => $cds_id,
										cs_name => $cs_lname
									};
								}
							}
						}
					}

					undef $sth_cs_ins;
					undef $sth_cds_sel;
					undef $sth_cds_ins;
					undef $sth_cds_ins_b;
					undef $sth_cds_del;
					undef $sth_cds_del_b;
				}

				if(defined $cdi_id_hash && ref $cdi_id_hash eq 'HASH'){
					&cgi_lib::common::message($cdi_id_hash, $LOG) if(defined $LOG);
					my $sth_cds_sel_synonym = $dbh->prepare(qq|
SELECT
  ARRAY_TO_STRING(ARRAY_AGG(a.cs_name), ';') AS cs_name
FROM (
  SELECT
   cs.cs_name
  FROM
    concept_data_synonym AS cds
  LEFT JOIN concept_synonym AS cs ON cs.cs_id=cds.cs_id
  LEFT JOIN concept_data_synonym_type AS cdst ON cdst.cdst_id=cds.cdst_id
  WHERE
       cds.ci_id=?
   AND cds.cb_id=?
   AND cds.cdi_id=?
   AND cdst.cdst_name='synonym'
  ORDER BY
    cs.cs_name
) AS a
|) or die $dbh->errstr;
					my $sth_cd_upd_synonym = $dbh->prepare(qq|UPDATE concept_data SET cd_syn=? WHERE ci_id=? AND cb_id=? AND cdi_id=?|) or die $dbh->errstr;
					my $cs_name;
					foreach my $temp_cdi_id(keys(%{$cdi_id_hash})){
						$sth_cds_sel_synonym->execute($ci_id,$cb_id,$temp_cdi_id) or die $dbh->errstr;
						$column_number=0;
						$sth_cds_sel_synonym->bind_col(++$column_number, \$cs_name, undef);
						$sth_cds_sel_synonym->fetch;
						$sth_cds_sel_synonym->finish;

						$sth_cd_upd_synonym->execute($cs_name,$ci_id,$cb_id,$temp_cdi_id) or die $dbh->errstr;
						$sth_cd_upd_synonym->finish;
						&cgi_lib::common::message($cs_name, $LOG) if(defined $LOG);
					}

					undef $sth_cds_sel_synonym;
					undef $sth_cd_upd_synonym;
				}

				if(
							defined	$cdi_id
					&&	defined	$CRL_HASH
					&&	ref			$CRL_HASH eq 'HASH'
					&&	exists	$CRL_HASH->{'part_of'}
					&&	defined	$CRL_HASH->{'part_of'}
					&&	defined	$crt_id
				){

					$cdi_id_arr = [keys(%{$cdi_id_hash})];
					my $temp_cdi_id_hash = {};
					map { $temp_cdi_id_hash->{$_} = undef } keys(%{$cdi_id_hash});
					if(defined $CT_PID_CRT_ID_HASH && ref $CT_PID_CRT_ID_HASH eq 'HASH'){
						foreach my $temp_cdi_id(@{$cdi_id_arr}){
							if(
										exists	$CT_PID_CRT_ID_HASH->{$temp_cdi_id}
								&&	defined	$CT_PID_CRT_ID_HASH->{$temp_cdi_id}
								&&	ref			$CT_PID_CRT_ID_HASH->{$temp_cdi_id} eq 'HASH'
								&&	exists	$CT_PID_CRT_ID_HASH->{$temp_cdi_id}->{$crt_id}
								&&	defined	$CT_PID_CRT_ID_HASH->{$temp_cdi_id}->{$crt_id}
								&&	ref			$CT_PID_CRT_ID_HASH->{$temp_cdi_id}->{$crt_id} eq 'HASH'
							){
								map { $temp_cdi_id_hash->{$_} = undef } keys(%{$CT_PID_CRT_ID_HASH->{$temp_cdi_id}->{$crt_id}});
							}
						}
					}
					$cdi_id_arr = [keys(%{$temp_cdi_id_hash})];
					undef $temp_cdi_id_hash;


					my $CTI_HASH;
					my $cti_cids;
					my $cti_pids;
					my $cti_depth;
					{
						my $sth_cti_sel = $dbh->prepare(qq|SELECT cdi_id,cti_cids,cti_depth,cti_pids,crl_id FROM concept_tree_info WHERE ci_id=? AND cb_id=?|) or die $dbh->errstr;
						$sth_cti_sel->execute($ci_id,$cb_id) or die $dbh->errstr;
						$column_number = 0;
						my $cdi_id;
						my $crl_id;
						$sth_cti_sel->bind_col(++$column_number, \$cdi_id, undef);
						$sth_cti_sel->bind_col(++$column_number, \$cti_cids, undef);
						$sth_cti_sel->bind_col(++$column_number, \$cti_depth, undef);
						$sth_cti_sel->bind_col(++$column_number, \$cti_pids, undef);
						$sth_cti_sel->bind_col(++$column_number, \$crl_id, undef);
						while($sth_cti_sel->fetch){
							$CTI_HASH->{$cdi_id}->{$crl_id} = {
								cti_cids => undef,
								cti_pids => undef,
								cti_depth => $cti_depth - 0
							};

							if(defined $cti_cids && length $cti_cids){
								my $cti_cids_arr = &cgi_lib::common::decodeJSON($cti_cids);
								map { $CTI_HASH->{$cdi_id}->{$crl_id}->{'cti_cids'}->{$_} = undef } @{$cti_cids_arr} if(defined $cti_cids_arr && ref $cti_cids_arr eq 'ARRAY' && scalar @{$cti_cids_arr});
							}
							if(defined $cti_pids && length $cti_pids){
								my $cti_pids_arr = &cgi_lib::common::decodeJSON($cti_pids);
								map { $CTI_HASH->{$cdi_id}->{$crl_id}->{'cti_pids'}->{$_} = undef } @{$cti_pids_arr} if(defined $cti_pids_arr && ref $cti_pids_arr eq 'ARRAY' && scalar @{$cti_pids_arr});
							}

						}
						$sth_cti_sel->finish;
						undef $sth_cti_sel;
					}

##ここから

					my $sth_ct_ins = $dbh->prepare(qq|INSERT INTO concept_tree (ci_id,cb_id,cdi_id,cdi_pid,crl_id,crt_ids) VALUES (?,?,?,?,?,?)|) or die $dbh->errstr;
					my $sth_ct_upd = $dbh->prepare(qq|UPDATE concept_tree SET crt_ids=? WHERE ci_id=? AND cb_id=? AND crl_id=? AND cdi_id=? AND cdi_pid=?|) or die $dbh->errstr;
					my $sth_ct_del = $dbh->prepare(qq|DELETE FROM concept_tree where ci_id=? AND cb_id=? AND crl_id=? AND cdi_id=? AND cdi_pid=?|) or die $dbh->errstr;

					my $sth_cti_upd = $dbh->prepare(qq|UPDATE concept_tree_info SET cti_cnum=?,cti_cids=?,cti_depth=?,cti_pnum=?,cti_pids=? WHERE ci_id=? AND cb_id=? AND cdi_id=? AND crl_id=?|) or die $dbh->errstr;

					my $UPD_ID_HASH;
					my $crl_id = $CRL_HASH->{'part_of'};

					foreach my $cdi_id (@{$cdi_id_arr}){


						if(
									defined	$CT_ID_CRT_PID_HASH
							&&	ref			$CT_ID_CRT_PID_HASH eq 'HASH'
							&&	exists	$CT_ID_CRT_PID_HASH->{$cdi_id}
							&&	defined	$CT_ID_CRT_PID_HASH->{$cdi_id}
							&&	ref			$CT_ID_CRT_PID_HASH->{$cdi_id} eq 'HASH'
							&&	exists	$CT_ID_CRT_PID_HASH->{$cdi_id}->{$crt_id}
							&&	defined	$CT_ID_CRT_PID_HASH->{$cdi_id}->{$crt_id}
							&&	ref			$CT_ID_CRT_PID_HASH->{$cdi_id}->{$crt_id} eq 'HASH'
						){
							map { delete $CT_ID_PID_CRT_HASH->{$cdi_id}->{$_}->{$crt_id} } keys(%{$CT_ID_CRT_PID_HASH->{$cdi_id}->{$crt_id}});
							my $cti_cids = {};
							$cti_cids->{$cdi_id} = undef;
							if(
										defined	$CTI_HASH
								&&	ref			$CTI_HASH eq 'HASH'
								&&	exists	$CTI_HASH->{$cdi_id}
								&&	defined	$CTI_HASH->{$cdi_id}
								&&	ref			$CTI_HASH->{$cdi_id} eq 'HASH'
								&&	exists	$CTI_HASH->{$cdi_id}->{$crl_id}
								&&	defined	$CTI_HASH->{$cdi_id}->{$crl_id}
								&&	ref			$CTI_HASH->{$cdi_id}->{$crl_id} eq 'HASH'
								&&	exists	$CTI_HASH->{$cdi_id}->{$crl_id}->{'cti_cids'}
								&&	defined	$CTI_HASH->{$cdi_id}->{$crl_id}->{'cti_cids'}
								&&	ref			$CTI_HASH->{$cdi_id}->{$crl_id}->{'cti_cids'} eq 'HASH'
							){
								map { $cti_cids->{$_} = undef; } keys(%{$CTI_HASH->{$cdi_id}->{$crl_id}->{'cti_cids'}});
							}

							foreach my $cdi_pid (keys(%{$CT_ID_PID_CRT_HASH->{$cdi_id}})){
								if(defined $CT_ID_PID_CRT_HASH->{$cdi_id}->{$cdi_pid} && ref $CT_ID_PID_CRT_HASH->{$cdi_id}->{$cdi_pid} eq 'HASH' && scalar keys(%{$CT_ID_PID_CRT_HASH->{$cdi_id}->{$cdi_pid}})>=1){
									my $crt_ids = join(';',sort {$a <=> $b} keys(%{$CT_ID_PID_CRT_HASH->{$cdi_id}->{$cdi_pid}}));
									$sth_ct_upd->execute($crt_ids,$ci_id,$cb_id,$crl_id,$cdi_id,$cdi_pid) or die $dbh->errstr;
									$sth_ct_upd->finish;
								}
								else{
									$sth_ct_del->execute($ci_id,$cb_id,$crl_id,$cdi_id,$cdi_pid) or die $dbh->errstr;
									$sth_ct_del->finish;

									delete $CT_ID_PID_CRT_HASH->{$cdi_id}->{$cdi_pid};

									my $cti_pids = {};
									$cti_pids->{$cdi_pid} = undef;
									if(
												defined	$CTI_HASH
										&&	ref			$CTI_HASH eq 'HASH'
									){
										if(
													exists	$CTI_HASH->{$cdi_pid}
											&&	defined	$CTI_HASH->{$cdi_pid}
											&&	ref			$CTI_HASH->{$cdi_pid} eq 'HASH'
											&&	exists	$CTI_HASH->{$cdi_pid}->{$crl_id}
											&&	defined	$CTI_HASH->{$cdi_pid}->{$crl_id}
											&&	ref			$CTI_HASH->{$cdi_pid}->{$crl_id} eq 'HASH'
											&&	exists	$CTI_HASH->{$cdi_pid}->{$crl_id}->{'cti_pids'}
											&&	defined	$CTI_HASH->{$cdi_pid}->{$crl_id}->{'cti_pids'}
											&&	ref			$CTI_HASH->{$cdi_pid}->{$crl_id}->{'cti_pids'} eq 'HASH'
										){
											map { $cti_pids->{$_} = undef; } keys(%{$CTI_HASH->{$cdi_pid}->{$crl_id}->{'cti_pids'}});
										}

										foreach my $cti_cid (keys(%{$cti_cids})){
											if(
														exists	$CTI_HASH->{$cti_cid}
												&&	defined	$CTI_HASH->{$cti_cid}
												&&	ref			$CTI_HASH->{$cti_cid} eq 'HASH'
												&&	exists	$CTI_HASH->{$cti_cid}->{$crl_id}
												&&	defined	$CTI_HASH->{$cti_cid}->{$crl_id}
												&&	ref			$CTI_HASH->{$cti_cid}->{$crl_id} eq 'HASH'
												&&	exists	$CTI_HASH->{$cti_cid}->{$crl_id}->{'cti_pids'}
												&&	defined	$CTI_HASH->{$cti_cid}->{$crl_id}->{'cti_pids'}
												&&	ref			$CTI_HASH->{$cti_cid}->{$crl_id}->{'cti_pids'} eq 'HASH'
											){
												my $hash = $CTI_HASH->{$cti_cid}->{$crl_id}->{'cti_pids'};
												map { delete $hash->{$_} if(exists $hash->{$_}); } keys(%{$cti_pids});

												$hash = $CTI_HASH->{$cti_cid}->{$CRL_HASH->{'FMA'}}->{'cti_pids'};
												map {
													delete $hash->{$_} if(exists $hash->{$_}) } keys(%{$cti_pids});

												$UPD_ID_HASH->{$cti_cid} = undef;
											}
										}
										foreach my $cti_pid (keys(%{$cti_pids})){
											if(
														exists	$CTI_HASH->{$cti_pid}
												&&	defined	$CTI_HASH->{$cti_pid}
												&&	ref			$CTI_HASH->{$cti_pid} eq 'HASH'
												&&	exists	$CTI_HASH->{$cti_pid}->{$crl_id}
												&&	defined	$CTI_HASH->{$cti_pid}->{$crl_id}
												&&	ref			$CTI_HASH->{$cti_pid}->{$crl_id} eq 'HASH'
												&&	exists	$CTI_HASH->{$cti_pid}->{$crl_id}->{'cti_cids'}
												&&	defined	$CTI_HASH->{$cti_pid}->{$crl_id}->{'cti_cids'}
												&&	ref			$CTI_HASH->{$cti_pid}->{$crl_id}->{'cti_cids'} eq 'HASH'
											){
												my $hash = $CTI_HASH->{$cti_pid}->{$crl_id}->{'cti_cids'};
												map { delete $hash->{$_} if(exists $hash->{$_}); } keys(%{$cti_pids});

												$hash = $CTI_HASH->{$cti_pid}->{$CRL_HASH->{'FMA'}}->{'cti_cids'};
												map { delete $hash->{$_} if(exists $hash->{$_}); } keys(%{$cti_pids});

												$UPD_ID_HASH->{$cti_pid} = undef;
											}
										}
									}
								}
							}

							delete $CT_ID_CRT_PID_HASH->{$cdi_id}->{$crt_id} if(exists $CT_ID_CRT_PID_HASH->{$cdi_id}->{$crt_id});
						}
					}

					my $sth_cds_sel = $dbh->prepare(qq|
SELECT
 cs.cs_name
FROM
  concept_data_synonym AS cds
LEFT JOIN concept_synonym AS cs ON cs.cs_id=cds.cs_id
WHERE
     cds.ci_id=?
 AND cds.cb_id=?
 AND cds.cdi_id=?
ORDER BY
  cs.cs_name
|) or die $dbh->errstr;
					foreach my $cdi_id (@{$cdi_id_arr}){
						$CD_ID2NAMESYN->{$cdi_id} = {} if(exists $CD_ID2NAMESYN->{$cdi_id});
						my $cs_name;
						$sth_cds_sel->execute($ci_id,$cb_id,$cdi_id) or die $dbh->errstr;
						$column_number=0;
						$sth_cds_sel->bind_col(++$column_number, \$cs_name, undef);
						while($sth_cds_sel->fetch){
							$CD_ID2NAMESYN->{$cdi_id}->{lc $cs_name} = undef
						}
						$sth_cds_sel->finish;
					}
					undef $sth_cds_sel;

					foreach my $cdi_id (@{$cdi_id_arr}){
						my $synonym_arr = [];
						if(exists $CD_ID2NAMESYN->{$cdi_id} && defined $CD_ID2NAMESYN->{$cdi_id} && ref $CD_ID2NAMESYN->{$cdi_id} eq 'HASH'){
							push(@{$synonym_arr}, keys(%{$CD_ID2NAMESYN->{$cdi_id}}));
						}

						foreach my $synonym (@{$synonym_arr}){
							my $p_name = &getParentFromName($synonym);
							next unless(defined $p_name && length $p_name);
							next unless(exists $CD_NAMESYN2ID->{$p_name} && defined $CD_NAMESYN2ID->{$p_name} && ref $CD_NAMESYN2ID->{$p_name} eq 'HASH');
							map { $CT_ID_CRT_PID_HASH->{$cdi_id}->{$crt_id}->{$_} = undef; } keys(%{$CD_NAMESYN2ID->{$p_name}});
						}
						if(
									exists	$CT_ID_CRT_PID_HASH->{$cdi_id}
							&&	defined $CT_ID_CRT_PID_HASH->{$cdi_id}
							&&	ref			$CT_ID_CRT_PID_HASH->{$cdi_id} eq 'HASH'
							&&	exists	$CT_ID_CRT_PID_HASH->{$cdi_id}->{$crt_id}
							&&	defined $CT_ID_CRT_PID_HASH->{$cdi_id}->{$crt_id}
							&&	ref			$CT_ID_CRT_PID_HASH->{$cdi_id}->{$crt_id} eq 'HASH'
						){



							my $cti_cids = {};
							$cti_cids->{$cdi_id} = undef;
							if(
										defined	$CTI_HASH
								&&	ref			$CTI_HASH eq 'HASH'
								&&	exists	$CTI_HASH->{$cdi_id}
								&&	defined	$CTI_HASH->{$cdi_id}
								&&	ref			$CTI_HASH->{$cdi_id} eq 'HASH'
								&&	exists	$CTI_HASH->{$cdi_id}->{$crl_id}
								&&	defined	$CTI_HASH->{$cdi_id}->{$crl_id}
								&&	ref			$CTI_HASH->{$cdi_id}->{$crl_id} eq 'HASH'
								&&	exists	$CTI_HASH->{$cdi_id}->{$crl_id}->{'cti_cids'}
								&&	defined	$CTI_HASH->{$cdi_id}->{$crl_id}->{'cti_cids'}
								&&	ref			$CTI_HASH->{$cdi_id}->{$crl_id}->{'cti_cids'} eq 'HASH'
							){
								map { $cti_cids->{$_} = undef; } keys(%{$CTI_HASH->{$cdi_id}->{$crl_id}->{'cti_cids'}});
							}


							foreach my $cdi_pid (keys(%{$CT_ID_CRT_PID_HASH->{$cdi_id}->{$crt_id}})){
								if(exists $CT_ID_PID_CRT_HASH->{$cdi_id}->{$cdi_pid}){
									$CT_ID_PID_CRT_HASH->{$cdi_id}->{$cdi_pid}->{$crt_id} = undef;
									my $crt_ids = join(';',sort {$a <=> $b} keys(%{$CT_ID_PID_CRT_HASH->{$cdi_id}->{$cdi_pid}}));
									$sth_ct_upd->execute($crt_ids,$ci_id,$cb_id,$crl_id,$cdi_id,$cdi_pid) or die $dbh->errstr;
									$sth_ct_upd->finish;
								}
								else{
									$CT_ID_PID_CRT_HASH->{$cdi_id}->{$cdi_pid}->{$crt_id} = undef;
									my $crt_ids = join(';',sort {$a <=> $b} keys(%{$CT_ID_PID_CRT_HASH->{$cdi_id}->{$cdi_pid}}));

									$sth_ct_ins->execute($ci_id,$cb_id,$cdi_id,$cdi_pid,$crl_id,$crt_ids) or die $dbh->errstr;
									$sth_ct_ins->finish;
								}
								$UPD_ID_HASH->{$cdi_pid} = undef;



								my $cti_pids = {};
								$cti_pids->{$cdi_pid} = undef;
								if(
											defined	$CTI_HASH
									&&	ref			$CTI_HASH eq 'HASH'
								){
									if(
												exists	$CTI_HASH->{$cdi_pid}
										&&	defined	$CTI_HASH->{$cdi_pid}
										&&	ref			$CTI_HASH->{$cdi_pid} eq 'HASH'
										&&	exists	$CTI_HASH->{$cdi_pid}->{$crl_id}
										&&	defined	$CTI_HASH->{$cdi_pid}->{$crl_id}
										&&	ref			$CTI_HASH->{$cdi_pid}->{$crl_id} eq 'HASH'
										&&	exists	$CTI_HASH->{$cdi_pid}->{$crl_id}->{'cti_pids'}
										&&	defined	$CTI_HASH->{$cdi_pid}->{$crl_id}->{'cti_pids'}
										&&	ref			$CTI_HASH->{$cdi_pid}->{$crl_id}->{'cti_pids'} eq 'HASH'
									){
										map { $cti_pids->{$_} = undef; } keys(%{$CTI_HASH->{$cdi_pid}->{$crl_id}->{'cti_pids'}});
									}

									foreach my $cti_cid (keys(%{$cti_cids})){
										if(
													exists	$CTI_HASH->{$cti_cid}
											&&	defined	$CTI_HASH->{$cti_cid}
											&&	ref			$CTI_HASH->{$cti_cid} eq 'HASH'
											&&	exists	$CTI_HASH->{$cti_cid}->{$crl_id}
											&&	defined	$CTI_HASH->{$cti_cid}->{$crl_id}
											&&	ref			$CTI_HASH->{$cti_cid}->{$crl_id} eq 'HASH'
											&&	exists	$CTI_HASH->{$cti_cid}->{$crl_id}->{'cti_pids'}
											&&	defined	$CTI_HASH->{$cti_cid}->{$crl_id}->{'cti_pids'}
											&&	ref			$CTI_HASH->{$cti_cid}->{$crl_id}->{'cti_pids'} eq 'HASH'
										){
											my $hash = $CTI_HASH->{$cti_cid}->{$crl_id}->{'cti_pids'};
											map { $hash->{$_} = undef; } keys(%{$cti_pids});

											$hash = $CTI_HASH->{$cti_cid}->{$CRL_HASH->{'FMA'}}->{'cti_pids'};
											map { $hash->{$_} = undef; } keys(%{$cti_pids});

											$UPD_ID_HASH->{$cti_cid} = undef;
										}
									}
									foreach my $cti_pid (keys(%{$cti_pids})){
										if(
													exists	$CTI_HASH->{$cti_pid}
											&&	defined	$CTI_HASH->{$cti_pid}
											&&	ref			$CTI_HASH->{$cti_pid} eq 'HASH'
											&&	exists	$CTI_HASH->{$cti_pid}->{$crl_id}
											&&	defined	$CTI_HASH->{$cti_pid}->{$crl_id}
											&&	ref			$CTI_HASH->{$cti_pid}->{$crl_id} eq 'HASH'
											&&	exists	$CTI_HASH->{$cti_pid}->{$crl_id}->{'cti_cids'}
											&&	defined	$CTI_HASH->{$cti_pid}->{$crl_id}->{'cti_cids'}
											&&	ref			$CTI_HASH->{$cti_pid}->{$crl_id}->{'cti_cids'} eq 'HASH'
										){
											my $hash = $CTI_HASH->{$cti_pid}->{$crl_id}->{'cti_cids'};
											map { $hash->{$_} = undef; } keys(%{$cti_pids});

											$hash = $CTI_HASH->{$cti_pid}->{$CRL_HASH->{'FMA'}}->{'cti_cids'};
											map { $hash->{$_} = undef; } keys(%{$cti_pids});

											$UPD_ID_HASH->{$cti_pid} = undef;
										}
									}
								}
							}
						}
					}

					if(defined $UPD_ID_HASH && ref $UPD_ID_HASH eq 'HASH'){
						my $upd_id_arr;
						foreach my $upd_id (keys(%{$UPD_ID_HASH})){
							next unless(exists $CTI_HASH->{$upd_id} && defined $CTI_HASH->{$upd_id} && ref $CTI_HASH->{$upd_id} eq 'HASH');
							push(@{$upd_id_arr}, $upd_id);
						}
						foreach my $crl_id ($CRL_HASH->{'part_if'}, $CRL_HASH->{'FMA'}){

							$upd_id_arr = [sort {$CTI_HASH->{$a}->{$crl_id}->{'cti_depth'} <=> $CTI_HASH->{$b}->{$crl_id}->{'cti_depth'}} @{$upd_id_arr}];
							foreach my $upd_id (@{$upd_id_arr}){

								my $max_cti_depth = -1;
								my $cti_cnum = 0;
								my $cti_pnum = 0;
								my $temp_cti_cids;
								my $temp_cti_pids;
								if(
											exists	$CTI_HASH->{$upd_id}->{$crl_id}
									&&	defined	$CTI_HASH->{$upd_id}->{$crl_id}
									&&	ref			$CTI_HASH->{$upd_id}->{$crl_id} eq 'HASH'
									&&	exists	$CTI_HASH->{$upd_id}->{$crl_id}->{'cti_cids'}
									&&	defined	$CTI_HASH->{$upd_id}->{$crl_id}->{'cti_cids'}
									&&	ref			$CTI_HASH->{$upd_id}->{$crl_id}->{'cti_cids'} eq 'HASH'
								){
									my $cti_cids_arr = [sort {$a <=> $b} keys(%{$CTI_HASH->{$upd_id}->{$crl_id}->{'cti_cids'}})];
									$cti_cnum = scalar @{$cti_cids_arr};
									$temp_cti_cids = &cgi_lib::common::encodeJSON($cti_cids_arr);
								}
								if(
											exists	$CTI_HASH->{$upd_id}->{$crl_id}
									&&	defined	$CTI_HASH->{$upd_id}->{$crl_id}
									&&	ref			$CTI_HASH->{$upd_id}->{$crl_id} eq 'HASH'
									&&	exists	$CTI_HASH->{$upd_id}->{$crl_id}->{'cti_pids'}
									&&	defined	$CTI_HASH->{$upd_id}->{$crl_id}->{'cti_pids'}
									&&	ref			$CTI_HASH->{$upd_id}->{$crl_id}->{'cti_pids'} eq 'HASH'
								){
									my $cti_pids_arr = [sort {$a <=> $b} keys(%{$CTI_HASH->{$upd_id}->{$crl_id}->{'cti_pids'}})];
									foreach my $cti_pid (@{$cti_pids_arr}){
										next unless(
													exists	$CTI_HASH->{$cti_pid}
											&&	defined	$CTI_HASH->{$cti_pid}
											&&	ref			$CTI_HASH->{$cti_pid} eq 'HASH'
											&&	exists	$CTI_HASH->{$cti_pid}->{$crl_id}
											&&	defined	$CTI_HASH->{$cti_pid}->{$crl_id}
											&&	ref			$CTI_HASH->{$cti_pid}->{$crl_id} eq 'HASH'
											&&	exists	$CTI_HASH->{$cti_pid}->{$crl_id}->{'cti_depth'}
											&&	defined	$CTI_HASH->{$cti_pid}->{$crl_id}->{'cti_depth'}
										);
										$max_cti_depth = $CTI_HASH->{$cti_pid}->{$crl_id}->{'cti_depth'} if($max_cti_depth < $CTI_HASH->{$cti_pid}->{$crl_id}->{'cti_depth'});
									}
									$cti_pnum = scalar @{$cti_pids_arr};
									$temp_cti_pids = &cgi_lib::common::encodeJSON($cti_pids_arr);
								}
								$max_cti_depth++;

								$sth_cti_upd->execute($cti_cnum,$temp_cti_cids,$max_cti_depth,$cti_pnum,$temp_cti_pids,$ci_id,$cb_id,$upd_id,$crl_id) or die $dbh->errstr;
								$sth_cti_upd->finish;
							}

						}
					}


					undef $sth_ct_ins;
					undef $sth_ct_upd;
					undef $sth_ct_del;
					undef $sth_cti_upd;
				}

				&cgi_lib::common::message($cdi_id_added_hash, $LOG) if(defined $LOG);

				if(defined $cdi_id_added_hash && ref $cdi_id_added_hash eq 'HASH'){
					&cgi_lib::common::message($cdi_id_added_hash, $LOG) if(defined $LOG);

					my $sth_ct_sel = $dbh->prepare(qq|select cdi_id from concept_tree where ci_id=? AND cb_id=? AND cdi_pid=? AND crl_id=? AND crt_ids LIKE ?|) or die $dbh->errstr;
					my $sth_cs_ins = $dbh->prepare(qq|INSERT INTO concept_synonym (cs_name) VALUES (?) RETURNING cs_id|) or die $dbh->errstr;
					my $sth_cds_sel = $dbh->prepare(qq|SELECT cds_id FROM concept_data_synonym WHERE ci_id=? AND cb_id=? AND cdi_id=? AND cs_id=?|) or die $dbh->errstr;
					my $sth_cds_ins_b = $dbh->prepare(qq|INSERT INTO concept_data_synonym (ci_id,cb_id,cdi_id,cs_id,cds_bid,cds_added,cdst_id) VALUES (?,?,?,?,?,true,?) RETURNING cds_id|) or die $dbh->errstr;


					my $sth_cds_sel_synonym = $dbh->prepare(qq|
SELECT
  ARRAY_TO_STRING(ARRAY_AGG(a.cs_name), ';') AS cs_name
FROM (
  SELECT
   cs.cs_name
  FROM
    concept_data_synonym AS cds
  LEFT JOIN concept_synonym AS cs ON cs.cs_id=cds.cs_id
  LEFT JOIN concept_data_synonym_type AS cdst ON cdst.cdst_id=cds.cdst_id
  WHERE
       cds.ci_id=?
   AND cds.cb_id=?
   AND cds.cdi_id=?
   AND cdst.cdst_name='synonym'
  ORDER BY
    cs.cs_name
) AS a
|) or die $dbh->errstr;
					my $sth_cd_upd_synonym = $dbh->prepare(qq|UPDATE concept_data SET cd_syn=? WHERE ci_id=? AND cb_id=? AND cdi_id=?|) or die $dbh->errstr;

					foreach my $cdi_pid (keys(%{$cdi_id_added_hash})){

						$sth_ct_sel->execute($ci_id,$cb_id,$cdi_pid,$CRL_HASH->{'part_of'},'%'.$crt_id.'%') or die $dbh->errstr;
						$column_number = 0;
						my $cdi_id;
						$sth_ct_sel->bind_col(++$column_number, \$cdi_id, undef);
						while($sth_ct_sel->fetch){
							&cgi_lib::common::message($cdi_id, $LOG) if(defined $LOG);
							next unless(exists $CD_ID2NAME->{$cdi_id} && defined $CD_ID2NAME->{$cdi_id} && length $CD_ID2NAME->{$cdi_id});
							&cgi_lib::common::message($CD_ID2NAME->{$cdi_id}, $LOG) if(defined $LOG);
							my $cs_pname = $cdi_id_added_hash->{$cdi_pid}->{'cs_name'};
							&cgi_lib::common::message($cs_pname, $LOG) if(defined $LOG);
							my $cds_bid = $cdi_id_added_hash->{$cdi_pid}->{'cds_id'};
							my $cs_name = ucfirst(lc(sprintf("%s of %s",&getChildFromName($CD_ID2NAME->{$cdi_id}), $cs_pname)));
							my $cs_id;
							my $cds_id;
							&cgi_lib::common::message($cs_name, $LOG) if(defined $LOG);
							unless(exists $CS_NAME2ID->{$cs_name}){
								$sth_cs_ins->execute($cs_name) or die $dbh->errstr;
								$column_number=0;
								$sth_cs_ins->bind_col(++$column_number, \$cs_id, undef);
								$sth_cs_ins->fetch;
								$sth_cs_ins->finish;

								$CS_ID2NAME->{$cs_id} = $cs_name;
								$CS_NAME2ID->{$cs_name} = $cs_id;
							}
							else{
								$cs_id = $CS_NAME2ID->{$cs_name};
							}
							$sth_cds_sel->execute($ci_id,$cb_id,$cdi_id,$cs_id) or die $dbh->errstr;
							$column_number=0;
							$sth_cds_sel->bind_col(++$column_number, \$cds_id, undef);
							$sth_cds_sel->fetch;
							$sth_cds_sel->finish;

							unless(defined $cds_id){
								$sth_cds_ins_b->execute($ci_id,$cb_id,$cdi_id,$cs_id,$cds_bid,$CDST_NAME2ID->{'synonym'}) or die $dbh->errstr;
								$column_number=0;
								$sth_cds_ins_b->bind_col(++$column_number, \$cds_id, undef);
								$sth_cds_ins_b->fetch;
								$sth_cds_ins_b->finish;
								&cgi_lib::common::message($cds_id, $LOG) if(defined $LOG);
							}
							else{
								&cgi_lib::common::message($cds_id, $LOG) if(defined $LOG);
							}

							$sth_cds_sel_synonym->execute($ci_id,$cb_id,$cdi_id) or die $dbh->errstr;
							$column_number=0;
							$sth_cds_sel_synonym->bind_col(++$column_number, \$cs_name, undef);
							$sth_cds_sel_synonym->fetch;
							$sth_cds_sel_synonym->finish;

							$sth_cd_upd_synonym->execute($cs_name,$ci_id,$cb_id,$cdi_id) or die $dbh->errstr;
							$sth_cd_upd_synonym->finish;


						}
						$sth_ct_sel->finish;

					}
					undef $sth_ct_sel;
					undef $sth_cs_ins;
					undef $sth_cds_sel;
					undef $sth_cds_ins_b;
					undef $sth_cds_sel_synonym;
					undef $sth_cd_upd_synonym;
				}

				$dbh->commit;
#				$dbh->rollback;
				$DATAS->{'success'} = JSON::XS::true;

			};
			if($@){
				$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8($@);
				&cgi_lib::common::message($DATAS->{'msg'}, $LOG) if(defined $LOG);
				$DATAS->{'success'} = JSON::XS::false;

				$dbh->rollback;
			}
			$dbh->{'AutoCommit'} = 1;
			$dbh->{'RaiseError'} = 0;

		}
	}


}
&gzip_json($DATAS);

close($LOG);

exit;

sub getParentFromName {
	my $name = shift;
	my $p_name;
	if($name =~ /.+ of .+/i){
		unless(
			$name !~ /\b(tributary|branch) of .+/i &&
			(
				$name =~ /\b(complex|tree|network|set) of .+/i ||
				$name =~ /\b(disk|valve|ligament|artery|vein|duct|mater|joint) of .+/i ||
				$name =~ /.+ of (Giacomini|Guyon|Carabelli|Clarke|Ecker|Calleja|Schwalbe|Zinn)\b/i
			)
		){
			my @TEMP = split(' of ',$name);
			shift @TEMP;
			$p_name = join(' of ',@TEMP);
		}
	}
	return $p_name;
}

sub getChildFromName {
	my $name = shift;
	if($name =~ /.+ of .+/i){
		unless(
			$name !~ /\b(tributary|branch) of .+/i &&
			(
				$name =~ /\b(complex|tree|network|set) of .+/i ||
				$name =~ /\b(disk|valve|ligament|artery|vein|duct|mater|joint) of .+/i ||
				$name =~ /.+ of (Giacomini|Guyon|Carabelli|Clarke|Ecker|Calleja|Schwalbe|Zinn)\b/i
			)
		){
			my @TEMP = split(' of ',$name);
			$name = shift @TEMP;
		}
	}
	return $name;
}
