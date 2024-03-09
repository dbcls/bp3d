#!/bp3d/local/perl/bin/perl

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

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
use BITS::ConceptArtMapModified;
use BITS::ConceptArtMapPart;
my $is_subclass_cdi_name = $BITS::ConceptArtMapPart::is_subclass_cdi_name;

require "webgl_common.pl";
use cgi_lib::common;

unless(exists $ENV{'REQUEST_METHOD'}){
	use CGI::Carp qw/!fatalsToBrowser/;
	no CGI::Carp;
	no Carp;
}

my $LOG;
$LOG = \*STDERR if($config->{'DEBUG'});
exit 1 unless(defined $ARGV[0] && -e $ARGV[0] && -f $ARGV[0] && -s $ARGV[0]);

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

&recalc($FORM);
if($config->{'verbose'}){
	print "\n";
}

sub callback {
	my $msg = shift;
	my $val = shift;

	$val = 0 unless(defined $val);

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

		unless(exists $ENV{'REQUEST_METHOD'}){
			&cgi_lib::common::message($FORM);
		}

		if(defined $ARGV[0] && -e $ARGV[0] && -f $ARGV[0] && -s $ARGV[0]){
			&cgi_lib::common::writeFileJSON($ARGV[0],$FORM,1);
		}
	}
}

sub recalc {
	my $FORM = shift;
	my $val = 0;
	my $val_step = 0.005;
	&callback('Start',$val);
	my $datas;

	$datas =  $FORM->{'datas'} if(exists $FORM->{'datas'} && defined $FORM->{'datas'} && ref $FORM->{'datas'} eq 'ARRAY');
	delete $FORM->{'datas'};

#my $t0 = [&Time::HiRes::gettimeofday()] if($config->{'DEBUG'});
#my $t0 = [&Time::HiRes::gettimeofday()];

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\n" if($config->{'DEBUG'});

	if(defined $datas && ref $datas eq 'ARRAY'){

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\n" if($config->{'DEBUG'});

		$dbh->{'AutoCommit'} = 0;
		$dbh->{'RaiseError'} = 1;
		eval{
			my $sql_cbr_sel = 'select f_potid FROM concept_build_relation WHERE cbr_use AND ci_id=? AND cb_id=?';
			my $sth_cbr_sel = $dbh->prepare($sql_cbr_sel) or die $dbh->errstr;

			my $sql_bt_ins = 'INSERT INTO buildup_tree (md_id,mv_id,mr_id,ci_id,cb_id,cdi_id,cdi_pid,bul_id,f_potids) VALUES (?,?,?,?,?,?,?,?,?)';
			my $sth_bt_ins = $dbh->prepare($sql_bt_ins) or die $dbh->errstr;

			my $sql_ct_sel = 'select cdi_id,cdi_pid,bul_id,f_potids FROM concept_tree WHERE ci_id=? AND cb_id=?';
			my $sth_ct_sel = $dbh->prepare($sql_ct_sel) or die $dbh->errstr;

			my $sql_bti_ins_fmt = q|INSERT INTO buildup_tree_info
SELECT
 %d           AS md_id,
 %d           AS mv_id,
 %d           AS mr_id,
 ci_id,
 cb_id,
 cdi_id,
 cti_cnum     AS but_cnum,
 cti_cids     AS but_cids,
 cti_depth    AS but_depth,
 cti_pnum     AS but_pnum,
 cti_pids     AS but_pids,
 cti_delcause AS but_delcause,
 cti_entry    AS but_entry,
 cti_openid   AS but_openid,
 crl_id       AS bul_id
FROM
 concept_tree_info
WHERE
 ci_id=%d AND
 cb_id=%d
|;

			my $sql_btt_ins_fmt = q|INSERT INTO buildup_tree_trio
SELECT
 %d           AS md_id,
 %d           AS mv_id,
 %d           AS mr_id,
 ci_id,
 cb_id,
 cdi_pid,
 cdi_lid,
 cdi_rid,
 ctt_delcause,
 ctt_entry,
 ctt_openid
FROM
 concept_tree_trio
WHERE
 ci_id=%d AND
 cb_id=%d
|;

		my $sql_bd_ins_fmt = q|INSERT INTO buildup_data
SELECT
 %d           AS md_id,
 %d           AS mv_id,
 %d           AS mr_id,
 ci_id,
 cb_id,
 cdi_id,
 cd_name,
 cd_syn,
 cd_def,
 cd_delcause,
 cd_entry,
 cd_openid,
 phy_id,
 seg_id
FROM
 concept_data
WHERE
 ci_id=%d AND
 cb_id=%d
|;

			my $sth_cm_sel = $dbh->prepare(qq|SELECT cdi_name,cmp_id FROM concept_art_map AS cm LEFT JOIN (SELECT ci_id,cdi_id,cdi_name FROM concept_data_info) AS cdi ON cdi.ci_id=cm.ci_id AND cdi.cdi_id=cm.cdi_id WHERE md_id=? AND mv_id=?|) or die $dbh->errstr;
			my $sth_cm_upd = $dbh->prepare(qq|UPDATE concept_art_map SET cb_id=?,cm_entry=now() WHERE md_id=? AND mv_id=? AND cb_id<>?|) or die $dbh->errstr;

#			my $sth_cmm_upd = $dbh->prepare(qq|UPDATE concept_art_map_modified SET cb_id=? WHERE md_id=? AND mv_id=? AND cb_id<>?|) or die $dbh->errstr;
#			my $sth_cmm_upd2 = $dbh->prepare(qq|UPDATE concept_art_map_modified SET cm_modified=null WHERE md_id=? AND mv_id=?|) or die $dbh->errstr;

			my $column_number;

			foreach my $data (@$datas){
				foreach my $table (qw/buildup_data buildup_tree buildup_tree_info renderer_tree concept_art_map_modified buildup_tree_trio/){
					$val += $val_step;
					&callback(sprintf('clear table [%s]',$table),$val);
					$dbh->do(sprintf(q|DELETE FROM %s WHERE md_id=%d AND mv_id=%d|,$table, $data->{'md_id'}, $data->{'mv_id'})) or die $dbh->errstr;
				}
			}
			foreach my $data (@$datas){
				$val += $val_step;
				&callback('create data [buildup_data]',$val);
				$dbh->do(sprintf($sql_bd_ins_fmt, $data->{'md_id'}, $data->{'mv_id'}, $data->{'mr_id'}, $data->{'ci_id'}, $data->{'cb_id'})) or die $dbh->errstr;

				$val += $val_step;
				&callback('create data [buildup_tree_info]',$val);
				$dbh->do(sprintf($sql_bti_ins_fmt, $data->{'md_id'}, $data->{'mv_id'}, $data->{'mr_id'}, $data->{'ci_id'}, $data->{'cb_id'})) or die $dbh->errstr;

				$val += $val_step;
				&callback('create data [buildup_tree_trio]',$val);
				$dbh->do(sprintf($sql_btt_ins_fmt, $data->{'md_id'}, $data->{'mv_id'}, $data->{'mr_id'}, $data->{'ci_id'}, $data->{'cb_id'})) or die $dbh->errstr;

				$val += $val_step;
				&callback('create data [buildup_tree]',$val);

				$sth_cbr_sel->execute($data->{'ci_id'},$data->{'cb_id'}) or die $dbh->errstr;
				my($f_potid,$use_f_potids);
				my $column_number = 0;
				$sth_cbr_sel->bind_col(++$column_number, \$f_potid, undef);
				while($sth_cbr_sel->fetch){
					$use_f_potids->{$f_potid} = undef;
				}
				$sth_cbr_sel->finish;

				$sth_ct_sel->execute($data->{'ci_id'},$data->{'cb_id'}) or die $dbh->errstr;
				my($cdi_id,$cdi_pid,$bul_id,$f_potids,$cdi_pids,$cdi_cids);
				$column_number = 0;
				$sth_ct_sel->bind_col(++$column_number, \$cdi_id, undef);
				$sth_ct_sel->bind_col(++$column_number, \$cdi_pid, undef);
				$sth_ct_sel->bind_col(++$column_number, \$bul_id, undef);
				$sth_ct_sel->bind_col(++$column_number, \$f_potids, undef);
				while($sth_ct_sel->fetch){
					my $is_ins = 0;
					if($bul_id==3){
						$is_ins = 1;
						$cdi_pids->{$bul_id}->{$cdi_pid} = undef if(defined $cdi_pid);
						$cdi_cids->{$bul_id}->{$cdi_id} = undef if(defined $cdi_id);
					}
					elsif($bul_id==4 && defined $f_potids && length $f_potids){
						my @F_POTIDS;
						foreach my $f_potid (split(/;/,$f_potids)){
							next unless(exists $use_f_potids->{$f_potid});
							$is_ins = 1;
							$cdi_pids->{$bul_id}->{$cdi_pid} = undef if(defined $cdi_pid);
							$cdi_cids->{$bul_id}->{$cdi_id} = undef if(defined $cdi_id);
							push(@F_POTIDS, $f_potid);
						}
						$f_potids = join(';',@F_POTIDS);
					}
					next unless($is_ins);

					$sth_bt_ins->execute($data->{'md_id'},$data->{'mv_id'},$data->{'mr_id'},$data->{'ci_id'},$data->{'cb_id'},$cdi_id,$cdi_pid,$bul_id,$f_potids) or die $dbh->errstr;
					$sth_bt_ins->finish;

				}
				$sth_ct_sel->finish;

				if(defined $cdi_pids && ref $cdi_pids eq 'HASH'){
					foreach my $bul_id (keys(%$cdi_pids)){
						foreach my $cdi_id (keys(%{$cdi_pids->{$bul_id}})){
							delete $cdi_pids->{$bul_id}->{$cdi_id} if(exists $cdi_cids->{$bul_id}->{$cdi_id});
						}
					}
					foreach my $bul_id (keys(%$cdi_pids)){
						foreach my $cdi_id (keys(%{$cdi_pids->{$bul_id}})){
							$sth_bt_ins->execute($data->{'md_id'},$data->{'mv_id'},$data->{'mr_id'},$data->{'ci_id'},$data->{'cb_id'},$cdi_id,undef,$bul_id,undef) or die $dbh->errstr;
							$sth_bt_ins->finish;
						}
					}
				}
			}

			my $sub_datas;
			foreach my $data (@$datas){
				$sth_cm_sel->execute($data->{'md_id'},$data->{'mv_id'}) or die $dbh->errstr;
				$column_number = 0;
				my $cdi_name;
				my $cmp_id;
				$sth_cm_sel->bind_col(++$column_number, \$cdi_name, undef);
				$sth_cm_sel->bind_col(++$column_number, \$cmp_id, undef);
				while($sth_cm_sel->fetch){
					$cmp_id -= 0 if(defined $cmp_id);
					next unless((defined $cdi_name && $cdi_name =~ /$is_subclass_cdi_name/) || (defined $cmp_id && $cmp_id));

					my $FORM = &Clone::clone($data);
					$FORM->{'cdi_name'} = $cdi_name;
					$FORM->{'cmp_id'} = $cmp_id;
					$FORM->{'dbh'} = $dbh;
					$FORM->{'LOG'} = $LOG;

					push(@$sub_datas, $FORM);
				}
				$sth_cm_sel->finish;
			}

			if(defined $sub_datas && ref $sub_datas eq 'ARRAY' && scalar @$sub_datas){
				my $total = scalar @$sub_datas;
				my $count = 0;
				foreach my $data (@$sub_datas){
					&callback(sprintf('create sub class [%s]',$data->{'cdi_name'}),++$count/$total);
					&BITS::ConceptArtMapPart::create_subclass(%$data);
				}
			}

			foreach my $data (@$datas){
				$sth_cm_upd->execute($data->{'cb_id'},$data->{'md_id'},$data->{'mv_id'},$data->{'cb_id'}) or die $dbh->errstr;
				$sth_cm_upd->finish;

#				$sth_cmm_upd->execute($data->{'cb_id'},$data->{'md_id'},$data->{'mv_id'},$data->{'cb_id'}) or die $dbh->errstr;
#				$sth_cmm_upd->finish;

#				$sth_cmm_upd2->execute($data->{'md_id'},$data->{'mv_id'}) or die $dbh->errstr;
#				$sth_cmm_upd2->finish;


				my $CM_MODIFIED = &BITS::ConceptArtMapModified::exec(
					dbh => $dbh,
					md_id => $data->{'md_id'},
					mv_id => $data->{'mv_id'},
					mr_id => $data->{'mr_id'},
					LOG => $LOG,
					callback => sub {
						my $msg = shift;
						my $value = shift;
						$value = 1 unless(defined $value);
						if(defined $LOG){
							&cgi_lib::common::message($msg,$LOG);
							&cgi_lib::common::message($value,$LOG);
						}
						&callback(sprintf(&cgi_lib::common::decodeUTF8(qq|UPDATE Mapping Date [ %s ]|),&cgi_lib::common::decodeUTF8($msg)),$value);
					}
				);
				&cgi_lib::common::message($CM_MODIFIED,$LOG) if(defined $LOG);

			}

			if($config->{'DEBUG'}){
				$dbh->rollback();
				&cgi_lib::common::message('$dbh->rollback()',$LOG) if(defined $LOG);
			}else{
				$dbh->commit();
				&cgi_lib::common::message('$dbh->commit()',$LOG) if(defined $LOG);
			}
			&callback('End',1);
		};
		if($@){
			$dbh->rollback();
			print STDERR "\n" if($config->{'verbose'});
			&callback('Error:'.$@,1);
		}
		$dbh->{'AutoCommit'} = 1;
		$dbh->{'RaiseError'} = 0;
	}
	else{
		&callback('End',1);
	}
}
