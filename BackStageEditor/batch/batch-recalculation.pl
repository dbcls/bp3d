#!/bp3d/local/perl/bin/perl

use constant {
	CALC_VOLUME => 1,
};

select(STDERR);
$| = 1;
select(STDOUT);
$| = 1;

use strict;
use warnings;
use feature ':5.10';

use File::Spec::Functions;
use Encode;
use JSON::XS;
use Cwd;
#use Data::Dumper;
use Time::HiRes;


use Getopt::Long qw(:config posix_default no_ignore_case gnu_compat);
my $config = {
	host => exists $ENV{'AG_DB_HOST'} ? $ENV{'AG_DB_HOST'} : '127.0.0.1',
	port => exists $ENV{'AG_DB_PORT'} ? $ENV{'AG_DB_PORT'} : '8543',
	verbose => 0,
	DEBUG => 0
};
&Getopt::Long::GetOptions($config,qw/
	host|h=s
	port|p=s
	verbose|v
	DEBUG|D
/) or exit 1;

$ENV{'AG_DB_HOST'} = $config->{'host'};
$ENV{'AG_DB_PORT'} = $config->{'port'};

#my $json_debug = JSON::XS->new->utf8->indent(1)->canonical(1);

#print $json_debug->encode($config);
#&callback(&Encode::encode_utf8("テスト"));
#exit;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
use BITS::DensityCalc;

require "webgl_common.pl";
use cgi_lib::common;

unless(exists $ENV{'REQUEST_METHOD'}){
	use CGI::Carp qw/!fatalsToBrowser/;
	no CGI::Carp;
	no Carp;
}

my $LOG;
#$LOG = \*STDERR if($config->{'DEBUG'} || $config->{'verbose'});
$LOG = \*STDERR if($config->{'DEBUG'});
#&cgi_lib::common::message($config,$LOG) if(defined $LOG);
#die __LINE__;
exit 1 unless(defined $ARGV[0] && -e $ARGV[0] && -f $ARGV[0] && -s $ARGV[0]);

#my $json = JSON::XS->new->utf8->indent( $config->{'DEBUG'} )->canonical(1);
#$Data::Dumper::Indent = 1;
#$Data::Dumper::Sortkeys = 1;

my $FORM;
if(-e $ARGV[0] && -f $ARGV[0] && -s $ARGV[0]){
	$FORM = &cgi_lib::common::readFileJSON($ARGV[0]);
}
exit 1 unless(defined $FORM && ref $FORM eq 'HASH');

&cgi_lib::common::message(ref $FORM,$LOG) if(defined $LOG);
&cgi_lib::common::message([sort keys(%$FORM)],$LOG) if(defined $LOG);

my $dbh = &get_dbh();

$SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit";
sub sigexit {
	my($date) = `date`;
	$date =~ s/\s*$//g;
	&callback("Error:[$date] KILL THIS SCRIPT!!");
	exit(1);
}

my $work_path;
#if($config->{'DEBUG'}){
#	my @extlist = qw|.json|;
#	my($name,$dir,$ext) = &File::Basename::fileparse($ARGV[0],@extlist);
#	$work_path = &catfile($dir,qq|$name.txt|);
#}
&recalc($FORM);
if($config->{'verbose'}){
	print "\n";
}

sub callback {
	my $msg = shift;
	my $val = shift;
	my $recalc_data = shift;

	$val = 0 unless(defined $val);

#	if($config->{'DEBUG'}){
#		$msg = &Encode::encode_utf8($msg) if(&Encode::is_utf8($msg));
#		print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\$msg=[$msg]\n";
#	}

	$msg = &cgi_lib::common::decodeUTF8($msg);
	if($config->{'verbose'}){
		if($config->{'DEBUG'}){
#			print STDERR sprintf("[%3d%]:%-76s\n",int($val*100+0.5),$msg);
		}else{
			print STDERR sprintf("\r".'[%3d%%]:%-76s',int($val*100+0.5),$msg);
		}
	}else{
		$FORM->{'msg'} = $msg;
		$FORM->{'value'} = $val;
		$FORM->{'recalc_data'} = $recalc_data;
#		push(@{$FORM->{'recalc_datas'}},$recalc_data) if(defined $recalc_data);

		unless(exists $ENV{'REQUEST_METHOD'}){
			&cgi_lib::common::message($FORM);
		}

		if(defined $ARGV[0] && -e $ARGV[0] && -f $ARGV[0] && -s $ARGV[0]){
#			open(my $OUT,"> $ARGV[0]") or die $!;
#			flock($OUT,2);
#			print $OUT &cgi_lib::common::encodeUTF8($FORM);
#			close($OUT);
			&cgi_lib::common::writeFileJSON($ARGV[0],$FORM,1);
		}
	}
}

sub recalc {
	my $FORM = shift;
	&callback('Start',0.1);
	my $all_datas;

	$all_datas = &cgi_lib::common::decodeJSON($FORM->{'all_datas'}) if(exists $FORM->{'all_datas'} && defined $FORM->{'all_datas'} && ref $FORM->{'all_datas'} eq '');
	delete $FORM->{'all_datas'};

#my $t0 = [&Time::HiRes::gettimeofday()] if($config->{'DEBUG'});
#my $t0 = [&Time::HiRes::gettimeofday()];

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\n" if($config->{'DEBUG'});

	if(defined $all_datas && ref $all_datas eq 'ARRAY'){

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\n" if($config->{'DEBUG'});

		$dbh->{'AutoCommit'} = 0;
		$dbh->{'RaiseError'} = 1;
		eval{
			my $IDS;
=pod
			if(DEBUG && -e $work_path && -s $work_path){
				open(IN,"< $work_path") or die $!;
				flock(IN,1);
				my @DATAS = <IN>;
				close(IN);
				$IDS = &cgi_lib::common::decodeUTF8(join('',@DATAS));
				undef @DATAS;
			}
=cut


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


			my $rows = scalar @$all_datas;
			my $row = 0;
			my $sth_cdi = $dbh->prepare(qq|select cdi_name from concept_data_info where ci_id=? and cdi_id=? and cdi_delcause is null|) or die $dbh->errstr;
			my $sth_bul = $dbh->prepare(qq|select bul_name_e from buildup_logic where bul_id=? and bul_use and bul_delcause is null|) or die $dbh->errstr;
			my $sth_rep_upd = $dbh->prepare(qq|update representation set cszr_id=?,csv_id=? where rep_id=?|) or die $dbh->errstr;
			my $col_num;
			foreach my $data (@$all_datas){
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($data) if($config->{'DEBUG'});
#print STDERR __PACKAGE__.':'.__LINE__.":[$data->{'ci_id'}]:[$data->{'cdi_id'}]\n" if($config->{'DEBUG'});
				$row++;
				unless(exists $data->{'cdi_name'} && defined $data->{'cdi_name'}){
					my $cdi_name;
					$col_num = 0;
					$sth_cdi->execute($data->{'ci_id'},$data->{'cdi_id'}) or die $dbh->errstr;
					$sth_cdi->bind_col(++$col_num, \$cdi_name, undef);
					$sth_cdi->fetch;
					$sth_cdi->finish;
					next unless(defined $cdi_name);
					$data->{'cdi_name'} = $cdi_name;
				}

				unless(exists $data->{'bul_name'} && defined $data->{'bul_name'}){
					my $bul_name;
					$col_num = 0;
					$sth_bul->execute($data->{'bul_id'}) or die $dbh->errstr;
					$sth_bul->bind_col(++$col_num, \$bul_name, undef);
					$sth_bul->fetch;
					$sth_bul->finish;
					next unless(defined $bul_name);
					$data->{'bul_name'} = $bul_name;
				}

				my $is_user_data = JSON::XS::false;
				{
					my $sth_cdi = $dbh->prepare(qq|select is_user_data from concept_data_info where ci_id=$data->{'ci_id'} and cdi_id=$data->{'cdi_id'} and cdi_delcause is null|) or die $dbh->errstr;
					$sth_cdi->execute() or die $dbh->errstr;
					$sth_cdi->bind_col(1, \$is_user_data, undef);
					$sth_cdi->fetch;
					$sth_cdi->finish;
					undef $sth_cdi;
					$is_user_data = (defined $is_user_data && $is_user_data ? JSON::XS::true : JSON::XS::false);
				}
#				next unless($is_user_data == JSON::XS::true);
#				next if($is_user_data == JSON::XS::true);
#				next unless($data->{'cdi_name'} eq 'FMA53135');
#				next unless($data->{'cdi_name'} eq 'FMA53165');
#				next unless($data->{'cdi_name'} eq 'FMA19236');
#				next unless($data->{'cdi_name'} eq 'FMA19234');

				&callback(qq|ReCalc: [$data->{'cdi_name'}][$data->{'bul_name'}] ($row/$rows)|,$row/($rows+1),$data);
&cgi_lib::common::message(qq|ReCalc: [$data->{'cdi_name'}][$data->{'bul_name'}] ($row/$rows)|,$LOG) if(defined $LOG);


#				sleep(2);
#				next;

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Time::HiRes::tv_interval($t0)." s\n" if($config->{'DEBUG'});
#$t0 = [&Time::HiRes::gettimeofday()] if($config->{'DEBUG'});

				if(defined $data->{'rep_id'}){
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\n" if($config->{'DEBUG'});
#print STDERR __PACKAGE__.':'.__LINE__.":\n" if($config->{'DEBUG'});

&cgi_lib::common::message('CALL &BITS::DensityCalc::clear_representation_density()',$LOG) if(defined $LOG);

					my $rtn_rows = &BITS::DensityCalc::clear_representation_density(
						dbh     => $dbh,
						ci_id   => $data->{'ci_id'},
						cb_id   => $data->{'cb_id'},
						bul_id  => $data->{'bul_id'},
						md_id   => $data->{'md_id'},
						mv_id   => $data->{'mv_id'},
						mr_id   => $data->{'mr_id'},
						cdi_id  => $data->{'cdi_id'},
						forcing => 1,
						LOG     => $LOG
					);
#					print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\$rtn_rows=[$rtn_rows]\n" if($config->{'DEBUG'});

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Time::HiRes::tv_interval($t0)." s\n" if($config->{'DEBUG'});
#$t0 = [&Time::HiRes::gettimeofday()] if($config->{'DEBUG'});
				}
				unless(defined $data->{'rep_id'}){
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\n" if($config->{'DEBUG'});
#print STDERR __PACKAGE__.':'.__LINE__.":\n" if($config->{'DEBUG'});
&cgi_lib::common::message('CALL &BITS::DensityCalc::ins_representation()',$LOG) if(defined $LOG);

					$data->{'rep_id'} = &BITS::DensityCalc::ins_representation(
						dbh     => $dbh,
						ci_id   => $data->{'ci_id'},
						cb_id   => $data->{'cb_id'},
						bul_id  => $data->{'bul_id'},
						md_id   => $data->{'md_id'},
						mv_id   => $data->{'mv_id'},
						mr_id   => $data->{'mr_id'},
						cdi_id  => $data->{'cdi_id'},
						LOG     => $LOG
					);

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Time::HiRes::tv_interval($t0)." s\n" if($config->{'DEBUG'});
#$t0 = [&Time::HiRes::gettimeofday()] if($config->{'DEBUG'});
				}
				if(defined $data->{'rep_id'}){
#print STDERR __PACKAGE__.':'.__LINE__.":\n" if($config->{'DEBUG'});

					&callback(qq|Create: Concept information [$data->{'bul_name'}]|,$row/($rows+1),$data);

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":".$data->{'rep_id'}."\n" if($config->{'DEBUG'});
					my($cdi_ids,$route_ids,$use_ids);
					my @k = ($data->{'ci_id'},$data->{'cb_id'},$data->{'bul_id'},$data->{'md_id'},$data->{'mv_id'},$data->{'mr_id'});
					my $key = join("\t",@k);
					unless(exists $IDS->{$key} && defined $IDS->{$key}){
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\n" if($config->{'DEBUG'});
#die __LINE__;
=pod
						($cdi_ids,$route_ids,$use_ids) = &BITS::DensityCalc::get_rep_parent_id(dbh=>$dbh,ci_id=>$data->{'ci_id'},cb_id=>$data->{'cb_id'},bul_id=>$data->{'bul_id'},md_id=>$data->{'md_id'},mv_id=>$data->{'mv_id'},mr_id=>$data->{'mr_id'});
						$IDS->{$key}->{'cdi_ids'} = $cdi_ids;
						$IDS->{$key}->{'route_ids'} = $route_ids;
						$IDS->{$key}->{'use_ids'} = $use_ids;

						if($config->{'DEBUG'}){
							open(OUT,"> $work_path") or die $!;
							flock(OUT,2);
							print OUT &cgi_lib::common::encodeUTF8($IDS);
							close(OUT);
							chmod 0666,$work_path;
						}
print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($cdi_ids) if($config->{'DEBUG'});
print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Time::HiRes::tv_interval($t0)." s\n" if($config->{'DEBUG'});
$t0 = [&Time::HiRes::gettimeofday()] if($config->{'DEBUG'});
=cut


#						my $sql = qq|select cdi_id,cdi_pid,but_cids,cdi_name,cdi_pname from view_buildup_tree where ci_id=$data->{'ci_id'} and cb_id=$data->{'cb_id'} and bul_id=$data->{'bul_id'} and but_delcause is null|;
						my $sql = qq|select cdi_id,cdi_pid,but_cids,cdi_name,cdi_pname from view_buildup_tree where ci_id=$data->{'ci_id'} and cb_id=$data->{'cb_id'} and bul_id=$data->{'bul_id'}|;
						my $sth = $dbh->prepare($sql) or die $dbh->errstr;

						my $BUT;
						$sth->execute() or die $dbh->errstr;
						my $cdi_id;
						my $cdi_pid;
						my $but_cids;
						my $cdi_name;
						my $cdi_pname;
						$sth->bind_col(1, \$cdi_id, undef);
						$sth->bind_col(2, \$cdi_pid, undef);
						$sth->bind_col(3, \$but_cids, undef);
						$sth->bind_col(4, \$cdi_name, undef);
						$sth->bind_col(5, \$cdi_pname, undef);
						while($sth->fetch){
							next unless(defined $cdi_id);
							my $cids;
							$cids = &cgi_lib::common::decodeJSON($but_cids) if(defined $but_cids);
							push(@$BUT,{
								cdi_id    => $cdi_id,
								cdi_pid   => $cdi_pid,
								but_cids  => $cids,
								cdi_name  => $cdi_name,
								cdi_pname => $cdi_pname,
							});
						}
						$sth->finish;
						undef $sth;

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($BUT) if($config->{'DEBUG'});
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Time::HiRes::tv_interval($t0)." s\n" if($config->{'DEBUG'});
#$t0 = [&Time::HiRes::gettimeofday()] if($config->{'DEBUG'});

						my $sth_cdi = $dbh->prepare(qq|select cdi.cdi_id,COALESCE(cd.cd_name,cdi.cdi_name_e,'') from concept_data_info as cdi left join (select cdi_id,cd_name from concept_data where ci_id=$data->{'ci_id'} and cb_id=$data->{'cb_id'} and cd_delcause is null) as cd on cdi.cdi_id=cd.cdi_id where cdi.ci_id=$data->{'ci_id'} and cdi.cdi_delcause is null|) or die $dbh->errstr;
						my $CDI;
						$sth_cdi->execute() or die $dbh->errstr;
#						my $cdi_id;
						my $cdi_name_e;
						$sth_cdi->bind_col(1, \$cdi_id, undef);
						$sth_cdi->bind_col(2, \$cdi_name_e, undef);
						while($sth_cdi->fetch){
							next unless(defined $cdi_id);
							$CDI->{$cdi_id} = lc($cdi_name_e);
						}
						$sth_cdi->finish;
						undef $sth_cdi;

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($CDI) if($config->{'DEBUG'});
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Time::HiRes::tv_interval($t0)." s\n" if($config->{'DEBUG'});
#$t0 = [&Time::HiRes::gettimeofday()] if($config->{'DEBUG'});

						my $sql_cm = qq|
select
 cdi_id
from
 concept_art_map
where
 (ci_id,cb_id,md_id,mv_id,mr_id,cdi_id) in (
  select
   ci_id,cb_id,md_id,mv_id,max(mr_id) as mr_id,cdi_id
  from
   concept_art_map
  where
   ci_id=$data->{'ci_id'} and
   cb_id=$data->{'cb_id'} and
   md_id=$data->{'md_id'} and
   mv_id=$data->{'mv_id'} and
   mr_id<=$data->{'mr_id'}
  group by
   ci_id,cb_id,md_id,mv_id,cdi_id
)
 and cm_use
 and cm_delcause is null
group by
 cdi_id
|;
						my $sth_cm = $dbh->prepare($sql_cm) or die $dbh->errstr;
						my $CM;
						$sth_cm->execute() or die $dbh->errstr;
#						my $cdi_id;
						$sth_cm->bind_col(1, \$cdi_id, undef);
						while($sth_cm->fetch){
							next unless(defined $cdi_id);
							$CM->{$cdi_id} = undef;
						}
						$sth_cm->finish;
						undef $sth_cm;

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($CM) if($config->{'DEBUG'});
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Time::HiRes::tv_interval($t0)." s\n" if($config->{'DEBUG'});
#$t0 = [&Time::HiRes::gettimeofday()] if($config->{'DEBUG'});

						my $CDI_IDS;
						foreach my $but (@$BUT){
							my $cdi_id = $but->{'cdi_id'};
							my $cdi_pid = $but->{'cdi_pid'};
							my $cids = $but->{'but_cids'};
							my $cdi_name = $but->{'cdi_name'};
							my $cdi_pname = $but->{'cdi_pname'};

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.$cdi_name.':'.$is_user_data."\n" if($config->{'DEBUG'});
#next unless($is_user_data == JSON::XS::true);
#die __LINE__;

							push(@$cids,$cdi_id);
							my @CIDS = grep {exists $CM->{$_}} @$cids;
							my $cids_rows = scalar @CIDS;
							$CDI_IDS->{$cdi_id} = {} if($cids_rows);
							if($cids_rows){
								$CDI_IDS->{$cdi_id}->{'cdi_cids'}->{$_} = undef for(@CIDS);
								delete $CDI_IDS->{$cdi_id}->{'cdi_cids'}->{$cdi_id};
								delete $CDI_IDS->{$cdi_id}->{'cdi_cids'} if(scalar keys(%{$CDI_IDS->{$cdi_id}->{'cdi_cids'}}) == 0);
							}

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($but) if($config->{'DEBUG'});
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.qq|\$cids_rows=[$cids_rows]|."\n" if($config->{'DEBUG'});

							next unless($cids_rows);

							$CDI_IDS->{$cdi_id}->{'cdi_name'} = $cdi_name;
							$CDI_IDS->{$cdi_id}->{'name'} = $CDI->{$cdi_id} if(exists $CDI->{$cdi_id} && defined $CDI->{$cdi_id});

							if(defined $cdi_pid){
								$CDI_IDS->{$cdi_id}->{'cdi_pid'}->{$cdi_pid} = undef;
								$CDI_IDS->{$cdi_id}->{'cdi_pname'}->{$cdi_pname} = $CDI->{$cdi_pid};
							}

						}
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($CDI_IDS) if($config->{'DEBUG'});
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Time::HiRes::tv_interval($t0)." s\n" if($config->{'DEBUG'});
#$t0 = [&Time::HiRes::gettimeofday()] if($config->{'DEBUG'});
#						undef $CDI_IDS;
#die "DEBUG";

						$IDS->{$key}->{'cdi_ids'} = $cdi_ids = $CDI_IDS;
						$IDS->{$key}->{'route_ids'} = undef;
						$IDS->{$key}->{'use_ids'} = undef;



					}else{

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\n" if($config->{'DEBUG'});
						$cdi_ids = $IDS->{$key}->{'cdi_ids'};
						$route_ids = $IDS->{$key}->{'route_ids'};
						$use_ids = $IDS->{$key}->{'use_ids'};
					}
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\n" if($config->{'DEBUG'});
#next unless($is_user_data == JSON::XS::true);

					&callback(qq|ReCalc: [$data->{'cdi_name'}][$data->{'bul_name'}] ($row/$rows)|,$row/($rows+1),$data);

&cgi_lib::common::message('CALL &BITS::DensityCalc::update_representation_density()',$LOG) if(defined $LOG);

					&BITS::DensityCalc::update_representation_density(
						dbh        => $dbh,
						ci_id      => $data->{'ci_id'},
						cb_id      => $data->{'cb_id'},
						bul_id     => $data->{'bul_id'},
						md_id      => $data->{'md_id'},
						mv_id      => $data->{'mv_id'},
						mr_id      => $data->{'mr_id'},
						cdi_id     => $data->{'cdi_id'},
						cdi_name   => $data->{'cdi_name'},
						rep_id     => $data->{'rep_id'},
						cdi_ids    => $cdi_ids,
						calcVolume => CALC_VOLUME,
						callback   => sub {
							my $msg = shift;
							if(defined $msg){
								&callback(qq|ReCalc: [$data->{'cdi_name'}][$data->{'bul_name'}][$msg] ($row/$rows)|,$row/($rows+1),$data);
							}else{
								&callback(qq|ReCalc: [$data->{'cdi_name'}][$data->{'bul_name'}] ($row/$rows)|,$row/($rows+1),$data);
							}
						},
						LOG     => $LOG
					);

					my $rep_hash_ref;
					{
						my $sql_sel=<<SQL;
select * from representation where rep_id=? and rep_delcause is null
SQL
						my $sth_sel = $dbh->prepare($sql_sel) or die $dbh->errstr;
						$sth_sel->execute($data->{'rep_id'}) or die $dbh->errstr;
						&cgi_lib::common::message($sth_sel->rows(),$LOG) if(defined $LOG);
						$rep_hash_ref = $sth_sel->fetchrow_hashref;
						$sth_sel->finish;
						undef $sth_sel;
					}

#die;
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Time::HiRes::tv_interval($t0)." s\n" if($config->{'DEBUG'});
#$t0 = [&Time::HiRes::gettimeofday()] if($config->{'DEBUG'});

					if(defined $rep_hash_ref && ref $rep_hash_ref eq 'HASH'){
						my $b = $rep_hash_ref;
						my $cm_volume = $b->{'rep_volume'};
						my $cszr_id = 0;
						foreach my $temp_cszr_id (keys(%SEGMENT_ZRANGE)){
							if(defined $SEGMENT_ZRANGE{$temp_cszr_id}->{'min'} && defined $SEGMENT_ZRANGE{$temp_cszr_id}->{'max'}){
								if($b->{'rep_zmin'} >= $SEGMENT_ZRANGE{$temp_cszr_id}->{'min'} && $b->{'rep_zmax'} < $SEGMENT_ZRANGE{$temp_cszr_id}->{'max'}){
									$cszr_id = $temp_cszr_id;
									last;
								}
							}elsif(defined $SEGMENT_ZRANGE{$temp_cszr_id}->{'min'}){
								if($b->{'rep_zmin'} >= $SEGMENT_ZRANGE{$temp_cszr_id}->{'min'}){
									$cszr_id = $temp_cszr_id;
									last;
								}
							}elsif(defined $SEGMENT_ZRANGE{$temp_cszr_id}->{'max'}){
								if($b->{'rep_zmax'} < $SEGMENT_ZRANGE{$temp_cszr_id}->{'max'}){
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
						$sth_rep_upd->execute($cszr_id,$csv_id,$b->{'rep_id'}) or die $dbh->errstr;
						$sth_rep_upd->finish;

#						if($b->{'rep_primitive'}){
#							&cgi_lib::common::message($b->{'rep_primitive'}."\t".$b->{'rep_primitive'}, \*STDERR);
#						}
					}
				}
				$dbh->commit() unless($config->{'DEBUG'});
			}
			undef $sth_cdi;
			undef $sth_bul;
			undef $sth_rep_upd;

#die "DEBUG" if($config->{'DEBUG'});

			if($config->{'DEBUG'}){
				$dbh->rollback();
				&cgi_lib::common::message('$dbh->rollback()',$LOG) if(defined $LOG);
			}else{
				$dbh->commit();
				&cgi_lib::common::message('$dbh->commit()',$LOG) if(defined $LOG);
			}
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\n" if($config->{'DEBUG'});
			&callback('End',1);
		};
		if($@){
			$dbh->rollback();
			print STDERR "\n" if($config->{'verbose'});
			&callback('Error:'.$@,1);
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":".$@."\n" if($config->{'DEBUG'});
		}
		$dbh->{'AutoCommit'} = 1;
		$dbh->{'RaiseError'} = 0;
	}
	else{
		&callback('End',1);
	}

#	print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Time::HiRes::tv_interval($t0)." s\n" if($config->{'DEBUG'});

}
