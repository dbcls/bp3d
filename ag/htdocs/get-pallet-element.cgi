#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

#say __LINE__ unless(exists($ENV{'REQUEST_METHOD'}));

#say $0;
#say $FindBin::Bin;
#exit;

use Encode;
use JSON::XS;
use File::Path;
use File::Spec::Functions qw(catdir catfile);
use File::Basename;
use Data::Dumper;
use Storable;

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI::Cookie;
use Cwd;
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'API'),&Cwd::abs_path(&catdir($FindBin::Bin,'..','..','ag-common','lib'));
#use lib $FindBin::Bin,&catdir($FindBin::Bin,'API'),&catdir($FindBin::Bin,'..','..','ag-common','lib');
use cgi_lib::common;
use AG::Representation;

#say __LINE__ unless(exists($ENV{'REQUEST_METHOD'}));

require "common.pl";
require "common_db.pl";

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $LOG;

$SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit";
sub sigexit {
	if(defined $LOG){
		my $date = `date`;
		$date =~ s/\s*$//g;
		say $LOG qq|Error:[$date] KILL THIS SCRIPT!!|;
	}
	exit(1);
}

unless(exists($ENV{'REQUEST_METHOD'})){
#	$ENV{'REQUEST_METHOD'} = 'POST';
	$ENV{'HTTP_COOKIE'} = qq|ag_annotation.images.sort=volume; ag_annotation.images.node=ynode-2534; ag_annotation.images.path=/FMA62955/FMA61775/FMA67165/FMA67135/FMA82472/FMA67619/FMA86140; ag_annotation.locale=ja; ag_annotation.session=acb1a41ce38de0eff5969ab9b7d088fb; ag_annotation.images.tg_id=1; ag_annotation.images.disptype=thump; ag_annotation.images.md_id=1; ag_annotation.images.mv_id=3; ag_annotation.images.mr_id=2; ag_annotation.images.version=%7B%221%22%3A%224.0%22%7D; ag_annotation.images.ci_id=1; ag_annotation.images.cb_id=4; ag_annotation.images.bul_id=3; ag_annotation.images.bul_name=FMA%203.0%20is_a; ag_annotation.images.butc_num=80457; ag_annotation.images.type=3; ag_annotation.images.types=%7B%224.3%22%3A3%2C%224.0%22%3A3%2C%225.0brain%22%3A3%7D|;

#	$FORM{datas} = qq|[{"b_id":null,"f_id":"FMA15737","cb_id":7,"ci_id":1,"md_id":1,"mr_id":2,"mv_id":3,"bul_id":3},{"b_id":null,"f_id":"FMA14540","cb_id":7,"ci_id":1,"md_id":1,"mr_id":2,"mv_id":3,"bul_id":3},{"b_id":null,"f_id":"FMA256237","cb_id":7,"ci_id":1,"md_id":1,"mr_id":2,"mv_id":3,"bul_id":3}]|;
#	$FORM{datas} = qq|[{"b_id":"BP6554","f_id":"FMA83929","cb_id":4,"ci_id":1,"md_id":1,"mr_id":2,"mv_id":3,"bul_id":3}]|;
#	$FORM{datas} = qq|[{"b_id":null,"f_id":"FMA83929","cb_id":7,"ci_id":1,"md_id":1,"mr_id":2,"mv_id":3,"bul_id":3}]|;
#	$FORM{datas} = qq|[{"b_id":null,"f_id":"FMA83929","cb_id":7,"ci_id":1,"md_id":1,"mr_id":2,"mv_id":3,"bul_id":3},{"b_id":null,"f_id":"FMA86140","cb_id":7,"ci_id":1,"md_id":1,"mr_id":2,"mv_id":3,"bul_id":3}]|;
	$FORM{datas} = qq|[{"b_id":null,"f_id":"FMA62955","cb_id":7,"ci_id":1,"md_id":1,"mr_id":2,"mv_id":3,"bul_id":3}]|;
	$FORM{limit} = 100;

#	$FORM{datas} = qq|[{"b_id":"BP7759","f_id":"FMA61775","cb_id":4,"ci_id":1,"md_id":1,"mr_id":2,"mv_id":3,"bul_id":3}]|;
	$FORM{datas} = qq|[{"b_id":"BP9334","f_id":"FMA7197","cb_id":"4","ci_id":1,"md_id":1,"mr_id":2,"mv_id":3,"bul_id":4}]|;
	$COOKIE{'ag_annotation.images.locale'} = 'ja';
#	&run();
#	exit;

	my $datas;
	my $sth = $dbh->prepare(qq|
select
 rep_id,
 md_id,
 mv_id,
 mr_id,
 ci_id,
 cb_id,
 bul_id,
 cdi_name
from
 view_representation
where
 rep_delcause is null
order by
-- rep_depth,
 rep_serial
|) or die $dbh->errstr;

	$sth->execute() or die $dbh->errstr;
	my $rep_id;
	my $md_id;
	my $mv_id;
	my $mr_id;
	my $ci_id;
	my $cb_id;
	my $bul_id;
	my $cdi_name;
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$rep_id, undef);
	$sth->bind_col(++$column_number, \$md_id, undef);
	$sth->bind_col(++$column_number, \$mv_id, undef);
	$sth->bind_col(++$column_number, \$mr_id, undef);
	$sth->bind_col(++$column_number, \$ci_id, undef);
	$sth->bind_col(++$column_number, \$cb_id, undef);
	$sth->bind_col(++$column_number, \$bul_id, undef);
	$sth->bind_col(++$column_number, \$cdi_name, undef);
	while($sth->fetch){
		push(@$datas,{
			b_id => $rep_id,
			f_id => $cdi_name,
			md_id => $md_id,
			mv_id => $mv_id,
			mr_id => $mr_id,
			ci_id => $ci_id,
			cb_id => $cb_id,
			bul_id => $bul_id
		});
	}
	$sth->finish;
	undef $sth;

	if(defined $datas){
		foreach my $data (@$datas){
			$FORM{limit} = 0;
			$FORM{datas} = &cgi_lib::common::encodeJSON([$data]);
			foreach my $locale (qw/ja en/){
				$COOKIE{'ag_annotation.images.locale'} = $locale;
				&run();
			}
		}
	}
}
else{
	&run();
}
sub run {
	my $query = CGI->new;
	&getParams($query,\%FORM,\%COOKIE);

	my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0, qr/\..*$/);
	$LOG = &cgi_lib::common::getLogFH(\%FORM,\%COOKIE);


	&setDefParams(\%FORM,\%COOKIE);

	my $RTN = {
		'datas' => [],
		'total' => 0,
		'success' => JSON::XS::false
	};
	eval{
		my $datas = &cgi_lib::common::decodeJSON($FORM{datas});
		if(defined $datas && ref $datas eq 'ARRAY'){

			my $cookie_bul_id = $COOKIE{'ag_annotation.images.bul_id'} if(exists $COOKIE{'ag_annotation.images.bul_id'} && defined $COOKIE{'ag_annotation.images.bul_id'});
			my $cookie_cb_id  = $COOKIE{'ag_annotation.images.cb_id'} if(exists $COOKIE{'ag_annotation.images.cb_id'} && defined $COOKIE{'ag_annotation.images.cb_id'});
			my $cookie_ci_id  = $COOKIE{'ag_annotation.images.ci_id'} if(exists $COOKIE{'ag_annotation.images.ci_id'} && defined $COOKIE{'ag_annotation.images.ci_id'});
			my $cookie_md_id  = $COOKIE{'ag_annotation.images.md_id'} if(exists $COOKIE{'ag_annotation.images.md_id'} && defined $COOKIE{'ag_annotation.images.md_id'});
			my $cookie_mr_id  = $COOKIE{'ag_annotation.images.mr_id'} if(exists $COOKIE{'ag_annotation.images.mr_id'} && defined $COOKIE{'ag_annotation.images.mr_id'});
			my $cookie_mv_id  = $COOKIE{'ag_annotation.images.mv_id'} if(exists $COOKIE{'ag_annotation.images.mv_id'} && defined $COOKIE{'ag_annotation.images.mv_id'});
			my $lng    = $COOKIE{'ag_annotation.images.locale'} if(exists $COOKIE{'ag_annotation.images.locale'} && defined $COOKIE{'ag_annotation.images.locale'});

			my $sth_cdi = $dbh->prepare(qq|select cdi_id from concept_data_info where ci_id=? and cdi_name=?|) or die $dbh->errstr;

			my $sth = $dbh->prepare(qq|
select
 rep.rep_id,
 mr.mr_version
from
 representation as rep

left join (
 select md_id,mv_id,mr_id,mr_version from model_revision
) as mr on
 mr.md_id=rep.md_id and
 mr.mv_id=rep.mv_id and
 mr.mr_id=rep.mr_id

where
 rep.rep_delcause is null and 
 (rep.md_id,rep.mv_id,rep.mr_id,rep.bul_id,rep.cdi_id) in (
  select
   md_id,
   mv_id,
   max(mr_id) as mr_id,
   bul_id,
   cdi_id
  from
   representation
  where
   rep_delcause is null and md_id=? and mv_id=? and mr_id<=? and bul_id=? and cdi_id=?
  group by
   md_id,
   mv_id,
   bul_id,
   cdi_id
 )
|) or die $dbh->errstr;

			my $sth_exclude = $dbh->prepare(qq|
select
 rep.rep_id,
 mr.mr_version
from
 representation as rep

left join (
 select md_id,mv_id,mr_id,mr_version from model_revision
) as mr on
 mr.md_id=rep.md_id and
 mr.mv_id=rep.mv_id and
 mr.mr_id=rep.mr_id

where
 rep.rep_delcause is null and 
 (rep.md_id,rep.mv_id,rep.mr_id,rep.bul_id,rep.cdi_id) in (
  select
   md_id,
   mv_id,
   max(mr_id) as mr_id,
   bul_id,
   cdi_id
  from
   representation
  where
   rep_delcause is null and md_id=? and mv_id=? and mr_id<=? and bul_id<>? and cdi_id=?
  group by
   md_id,
   mv_id,
   bul_id,
   cdi_id
 )
|) or die $dbh->errstr;

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

			my $RTN_HASH_DATAS;

			foreach my $data (@$datas){
				say __PACKAGE__.':'.__FILE__.':'.__LINE__.':$data='.&cgi_lib::common::encodeJSON($data,1) unless(exists($ENV{'REQUEST_METHOD'}));
				my $rep_id;
				my $mr_version;

				my $md_id  = $cookie_md_id;
				my $mv_id  = $cookie_mv_id;
				my $mr_id  = $cookie_mr_id;
				my $ci_id  = $cookie_ci_id;
				my $cb_id  = $cookie_cb_id;
				my $bul_id = $cookie_bul_id;

				if(exists $data->{b_id} && defined $data->{b_id} && length $data->{b_id}){
					$rep_id = $data->{b_id};

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

					say __PACKAGE__.':'.__FILE__.':'.__LINE__.':' unless(exists($ENV{'REQUEST_METHOD'}));
					say __PACKAGE__.':'.__FILE__.':'.__LINE__.':$md_id='.($md_id  // $data->{md_id}) unless(exists($ENV{'REQUEST_METHOD'}));
				}else{
					my $cdi_id;
					$sth_cdi->execute(
						$ci_id  // $data->{ci_id},
						$data->{f_id}
					) or die $dbh->errstr;
					$sth_cdi->bind_col(1, \$cdi_id, undef);
					$sth_cdi->fetch;
					$sth_cdi->finish;

					if(defined $cdi_id){
						say __PACKAGE__.':'.__FILE__.':'.__LINE__.':$cdi_id='.$cdi_id unless(exists($ENV{'REQUEST_METHOD'}));
						$sth->execute(
							$md_id  // $data->{md_id},
							$mv_id  // $data->{mv_id},
							$mr_id  // $data->{mr_id},
		#					$ci_id  // $data->{ci_id},
		#					$cb_id  // $data->{cb_id},
							$bul_id // $data->{bul_id},
							$cdi_id
						) or die $dbh->errstr;
						$sth->bind_col(1, \$rep_id, undef);
						$sth->bind_col(2, \$mr_version, undef);
						$sth->fetch;
						$sth->finish;

						unless(defined $rep_id && defined $mr_version){
							$sth_exclude->execute(
								$md_id  // $data->{md_id},
								$mv_id  // $data->{mv_id},
								$mr_id  // $data->{mr_id},
			#					$ci_id  // $data->{ci_id},
			#					$cb_id  // $data->{cb_id},
								$bul_id // $data->{bul_id},
								$cdi_id
							) or die $dbh->errstr;
							$sth_exclude->bind_col(1, \$rep_id, undef);
							$sth_exclude->bind_col(2, \$mr_version, undef);
							$sth_exclude->fetch;
							$sth_exclude->finish;
						}

					}
					say __PACKAGE__.':'.__FILE__.':'.__LINE__.':' unless(exists($ENV{'REQUEST_METHOD'}));
				}

				next unless(defined $rep_id && defined $mr_version);

				say __PACKAGE__.':'.__FILE__.':'.__LINE__.':$md_id='.($md_id  // $data->{md_id}) unless(exists($ENV{'REQUEST_METHOD'}));
				say __PACKAGE__.':'.__FILE__.':'.__LINE__.':$mv_id='.($mv_id  // $data->{mv_id}) unless(exists($ENV{'REQUEST_METHOD'}));
				say __PACKAGE__.':'.__FILE__.':'.__LINE__.':$mr_id='.($mr_id  // $data->{mr_id}) unless(exists($ENV{'REQUEST_METHOD'}));
				say __PACKAGE__.':'.__FILE__.':'.__LINE__.':$ci_id='.($ci_id  // $data->{ci_id}) unless(exists($ENV{'REQUEST_METHOD'}));
				say __PACKAGE__.':'.__FILE__.':'.__LINE__.':$cb_id='.($cb_id  // $data->{cb_id}) unless(exists($ENV{'REQUEST_METHOD'}));
				say __PACKAGE__.':'.__FILE__.':'.__LINE__.':$bul_id='.($bul_id  // $data->{bul_id}) unless(exists($ENV{'REQUEST_METHOD'}));

				say __PACKAGE__.':'.__FILE__.':'.__LINE__.':$rep_id='.$rep_id unless(exists($ENV{'REQUEST_METHOD'}));
				say __PACKAGE__.':'.__FILE__.':'.__LINE__.':$mr_version='.$mr_version unless(exists($ENV{'REQUEST_METHOD'}));

				my $params = {
					lng => $lng,
					version => $mr_version,
					md_id => $md_id  // $data->{md_id},
					mv_id => $mv_id  // $data->{mv_id},
					mr_id => $mr_id  // $data->{mr_id},
					ci_id => $ci_id  // $data->{ci_id},
					cb_id => $cb_id  // $data->{cb_id},
					bul_id => $bul_id // $data->{bul_id},
				};
				my $cache_path = &catdir(&getCachePath($params),&getArtBaseDirFromName($rep_id));
				say __PACKAGE__.':'.__FILE__.':'.__LINE__.':$cache_path='.$cache_path unless(exists($ENV{'REQUEST_METHOD'}));
				unless(-e $cache_path){
					my $old_umask = umask(0);
					&File::Path::make_path($cache_path,{mode=>0777});
					umask($old_umask);
				}
				my $cache_file = &catfile($cache_path,qq|$rep_id.store|);
				say __PACKAGE__.':'.__FILE__.':'.__LINE__.':$cache_file='.$cache_file unless(exists($ENV{'REQUEST_METHOD'}));
				say $LOG __PACKAGE__.':'.__FILE__.':'.__LINE__.':$cache_file='.$cache_file if(defined $LOG);

#				next;
#				exit;

				my $ALL_HASH_DATAS;

#				unlink $cache_file if(!exists($ENV{'REQUEST_METHOD'}) && -e $cache_file && -z $cache_file);
#				unlink $cache_file if(exists($ENV{'REQUEST_METHOD'}) && -e $cache_file && -z $cache_file);
#				unlink $cache_file if(-e $cache_file); #DEBUG

				if(-e $cache_file){
					$ALL_HASH_DATAS = &Storable::lock_retrieve($cache_file) if(-s $cache_file && -r $cache_file);
				}
				else{
					my $HASH_DATAS = &AG::Representation::get_element($dbh,$rep_id,$LOG);
					if(defined $HASH_DATAS){
						foreach my $cdi_name (keys(%$HASH_DATAS)){
							my $HASH = $HASH_DATAS->{$cdi_name};
							$HASH->{lng} = $lng;
							my $FMA = &getFMA($dbh,$HASH,$cdi_name);
							$ALL_HASH_DATAS->{$cdi_name} = $FMA;
						}
					}


					if(defined $ALL_HASH_DATAS && ref $ALL_HASH_DATAS eq 'HASH'){
						&Storable::lock_nstore($ALL_HASH_DATAS,$cache_file);
					}else{
						if(open(my $O,qq|> $cache_file|)){
							close($O);
						}
					}
				}
				if(defined $ALL_HASH_DATAS && ref $ALL_HASH_DATAS eq 'HASH'){
					unless(defined $RTN_HASH_DATAS){
						$RTN_HASH_DATAS = &Clone::clone($ALL_HASH_DATAS);
					}else{
						foreach my $key (keys(%$ALL_HASH_DATAS)){
							next if(exists $RTN_HASH_DATAS->{$key});
							$RTN_HASH_DATAS->{$key} = &Clone::clone($ALL_HASH_DATAS->{$key});
						}
					}
				}
			}
			undef $sth;

			undef $sth_rep_mr;
			undef $sth_cdi;

			if(defined $RTN_HASH_DATAS && ref $RTN_HASH_DATAS eq 'HASH'){
				$RTN->{'total'} = scalar keys(%$RTN_HASH_DATAS);
				if($RTN->{'total'}<=$FORM{limit}){
					push(@{$RTN->{'datas'}},map {$RTN_HASH_DATAS->{$_}} keys(%$RTN_HASH_DATAS));
				}else{
					$RTN->{'msg'} = qq|too many parts|;
				}
			}

	#		say __PACKAGE__.':'.__FILE__.':'.__LINE__.':%REP_IDS='.(scalar keys(%REP_IDS)) unless(exists($ENV{'REQUEST_METHOD'}));
	#		say __PACKAGE__.':'.__FILE__.':'.__LINE__.':%REP_IDS='.&cgi_lib::common::encodeJSON(\%REP_IDS,1) unless(exists($ENV{'REQUEST_METHOD'}));
	#		say __PACKAGE__.':'.__FILE__.':'.__LINE__.':%CDI_IDS='.&cgi_lib::common::encodeJSON(\%CDI_IDS,1) unless(exists($ENV{'REQUEST_METHOD'}));
	#		exit;


		}
		if(scalar @{$RTN->{'datas'}}){
			@{$RTN->{'datas'}} = sort {$a->{'name_e'} cmp $b->{'name_e'}} @{$RTN->{'datas'}};
		}
		$RTN->{'success'} = JSON::XS::true;
	};
	if($@){
		say $LOG __PACKAGE__.':'.__FILE__.':'.__LINE__.':'.$@ if(defined $LOG);
		die __PACKAGE__.':'.__FILE__.':'.__LINE__.':'.$@ unless(exists($ENV{'REQUEST_METHOD'}));
	}
	my $json = &cgi_lib::common::printContentJSON($RTN,\%FORM);
	say $LOG __PACKAGE__.':'.__FILE__.':'.__LINE__.':'.$json if(defined $LOG);

	#print __PACKAGE__.':'.__FILE__.':'.__LINE__.':$RTN='.&Data::Dumper::Dumper($RTN) unless(exists($ENV{'REQUEST_METHOD'}));
	say $LOG __PACKAGE__.':'.__FILE__.':'.__LINE__.':$RTN->{datas}='.(scalar @{$RTN->{'datas'}}) if(defined $LOG);

	unless(exists($ENV{'REQUEST_METHOD'})){
		$RTN->{'datas'} = [];
		say __PACKAGE__.':'.__FILE__.':'.__LINE__.':$RTN='.&cgi_lib::common::encodeJSON($RTN);
	}
}
