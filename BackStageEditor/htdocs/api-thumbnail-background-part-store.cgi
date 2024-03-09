#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;

use JSON::XS;
use DBD::Pg;
use File::Basename;
use File::Copy;
use File::Spec;
use File::Spec::Functions qw(abs2rel catdir catfile splitdir);
use Digest::MD5;
use Time::HiRes;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
require "webgl_common.pl";
use cgi_lib::common;

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);

my($logfile,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);

$logfile .= qq|.$FORM{cmd}| if(exists $FORM{cmd});

open(my $LOG,"> $logfile");
select($LOG);
$| = 1;
select(STDOUT);
flock($LOG,2);
print $LOG "\n[$logtime]:$0\n";
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%ENV,1), $LOG) if(defined $LOG);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM,1), $LOG) if(defined $LOG);
print $LOG "\n";
&setDefParams(\%FORM,\%COOKIE);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM,1), $LOG) if(defined $LOG);
print $LOG "\n";
&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM,1), $LOG) if(defined $LOG);
print $LOG "\n";
#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $where='where tbp_delcause is null';
my @bind_values = ();
if(exists $FORM{'filter'}){
	my $filter = &cgi_lib::common::decodeJSON($FORM{'filter'});
	if(defined $filter && ref $filter eq 'ARRAY'){
		my @W = ('tbp_delcause is null');
		foreach my $f (@$filter){
			next unless(exists $f->{'property'} && defined $f->{'property'} && exists $f->{'value'} && defined $f->{'value'});
			push(@W,qq|$f->{property}=?|);
			push(@bind_values,$f->{value});
		}
		$where = 'where '.join(' and ',@W) if(scalar @W > 0);
	}
}

my $orderby='';
if(exists $FORM{'sort'}){
	my $order = &cgi_lib::common::decodeJSON($FORM{'sort'});
	if(defined $order && ref $order eq 'ARRAY'){
		my @O;
		foreach my $o (@$order){
			next unless(exists $o->{'property'} && defined $o->{'property'} && exists $o->{'direction'} && defined $o->{'direction'});
			push(@O,qq|$o->{'property'} $o->{'direction'}|);
		}
		$orderby = 'order by '.join(',',@O) if(scalar @O > 0);
	}
}
#29:$FORM{'filter'}=[[{"property":"md_id","value":1}]]

$FORM{'cmd'} = 'read' unless(exists $FORM{'cmd'} && defined $FORM{'cmd'});

my $DATASET = {
	datas => [],
	total => 0,
	success => JSON::XS::false
};

if($FORM{'cmd'} eq 'read'){
	eval{
		my $sql=<<SQL;
select
 md_id,
 mv_id,
 tbp.ci_id,
 tbp.cdi_id,
 tbp_use,
 cdi_name,
 cdi_name_e
from
 thumbnail_background_part as tbp
left join (
  select ci_id,cdi_id,cdi_name,cdi_name_e from concept_data_info
) cdi on cdi.ci_id=tbp.ci_id and cdi.cdi_id=tbp.cdi_id
$where
$orderby
SQL

		print $LOG __LINE__,":\$sql=[",$sql,"]\n";
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		if(scalar @bind_values > 0){
			$DATASET->{total} = $sth->execute(@bind_values) or die $dbh->errstr;
		}else{
			$DATASET->{total} = $sth->execute() or die $dbh->errstr;
		}

		my($md_id,$mv_id,$ci_id,$cdi_id,$tbp_use,$cdi_name,$cdi_name_e);

		my $column_number = 0;
		$sth->bind_col(++$column_number, \$md_id, undef);
		$sth->bind_col(++$column_number, \$mv_id, undef);
		$sth->bind_col(++$column_number, \$ci_id, undef);
		$sth->bind_col(++$column_number, \$cdi_id, undef);
		$sth->bind_col(++$column_number, \$tbp_use, undef);
		$sth->bind_col(++$column_number, \$cdi_name, undef);
		$sth->bind_col(++$column_number, \$cdi_name_e, undef);

		while($sth->fetch){
			my $HASH = {
				md_id => $md_id+0,
				mv_id => $mv_id+0,
#				ci_id => $ci_id+0,
#				cdi_id => $cdi_id+0,
				tbp_use => $tbp_use ? JSON::XS::true : JSON::XS::false,
				cdi_name => $cdi_name,
				cdi_name_org => $cdi_name,
				cdi_name_e => $cdi_name_e
			};
			push(@{$DATASET->{'datas'}},$HASH);
		}
		$sth->finish;
		undef $sth;

		$DATASET->{'total'} = scalar @{$DATASET->{'datas'}};
		$DATASET->{'success'} = JSON::XS::true;
	};
	if($@){
		$DATASET->{'msg'} = $@;
		print $LOG __LINE__,":",$@,"\n";
	}

}
elsif(exists $FORM{'datas'} && defined $FORM{'datas'}){
	my $datas = &cgi_lib::common::decodeJSON($FORM{'datas'});
	if(defined $datas && ref $datas eq 'ARRAY' && scalar @$datas){
		if($FORM{'cmd'} eq 'create'){

#$dbh->do(qq|ALTER TABLE concept_art_map DISABLE TRIGGER USER;|) or die $dbh->errstr;
#$dbh->do(qq|ALTER TABLE history_concept_art_map DISABLE TRIGGER USER;|) or die $dbh->errstr;

			$dbh->{'AutoCommit'} = 0;
			$dbh->{'RaiseError'} = 1;
			eval{

				my $sql_sel=<<SQL;
select
 *
from
 thumbnail_background_part
where
 md_id=? and
 mv_id=? and
 ci_id=? and
 cdi_id=?
SQL

				my $sql_ins=<<SQL;
insert into thumbnail_background_part (
 md_id,
 mv_id,
 ci_id,
 cdi_id,
 tbp_use,
 tbp_enter
) values (
 ?,
 ?,
 ?,
 ?,
 ?,
 now()
)
SQL

				my $sql_upd=<<SQL;
update thumbnail_background_part set
 tbp_use=?,
 tbp_delcause=null,
 tbp_enter=now()
where
 md_id=? and
 mv_id=? and
 ci_id=? and
 cdi_id=?
SQL

				my $sth_sel = $dbh->prepare($sql_sel) or die $dbh->errstr;
				my $sth_ins = $dbh->prepare($sql_ins) or die $dbh->errstr;
				my $sth_upd = $dbh->prepare($sql_upd) or die $dbh->errstr;

				my $sql_mv='select ci_id from model_version where md_id=? and mv_id=?';
				my $sth_mv = $dbh->prepare($sql_mv) or die $dbh->errstr;

				my $sql_cdi='select cdi_id from concept_data_info where ci_id=? and cdi_name=?';
				my $sth_cdi = $dbh->prepare($sql_cdi) or die $dbh->errstr;

				foreach my $data (@$datas){
					next unless(
						exists $data->{'md_id'}    && defined $data->{'md_id'}    && $data->{'md_id'} &&
						exists $data->{'mv_id'}    && defined $data->{'mv_id'}    && $data->{'mv_id'} &&
						exists $data->{'cdi_name'} && defined $data->{'cdi_name'} && $data->{'cdi_name'} &&
						exists $data->{'tbp_use'}  && defined $data->{'tbp_use'}
					);

					my $ci_id;
					$sth_mv->execute($data->{'md_id'},$data->{'mv_id'}) or die $dbh->errstr;
					my $column_number = 0;
					$sth_mv->bind_col(++$column_number, \$ci_id, undef);
					$sth_mv->fetch;
					$sth_mv->finish;
					next unless(defined $ci_id);

					my $cdi_id;
					$sth_cdi->execute($ci_id,$data->{'cdi_name'}) or die $dbh->errstr;
					$column_number = 0;
					$sth_cdi->bind_col(++$column_number, \$cdi_id, undef);
					$sth_cdi->fetch;
					$sth_cdi->finish;
					next unless(defined $cdi_id);

					$data->{'tbp_use'} = $data->{'tbp_use'} ? 'true' : 'false';

					$sth_sel->execute($data->{'md_id'},$data->{'mv_id'},$ci_id,$cdi_id) or die $dbh->errstr;
					my $rows = $sth_sel->rows();
					$sth_sel->finish;
#					if(defined $LOG){
#						&cgi_lib::common::message('$data->{md_id}='.$data->{'md_id'},$LOG);
#						&cgi_lib::common::message('$data->{mv_id}='.$data->{'mv_id'},$LOG);
#						&cgi_lib::common::message('$ci_id='.$ci_id,$LOG);
#						&cgi_lib::common::message('$cdi_id='.$cdi_id,$LOG);
#						&cgi_lib::common::message('$rows='.$rows,$LOG);
#					}

					my $param_num=0;
					if($rows>0){
						$sth_upd->bind_param(++$param_num, $data->{'tbp_use'}, undef);
						$sth_upd->bind_param(++$param_num, $data->{'md_id'}, undef);
						$sth_upd->bind_param(++$param_num, $data->{'mv_id'}, undef);
						$sth_upd->bind_param(++$param_num, $ci_id, undef);
						$sth_upd->bind_param(++$param_num, $cdi_id, undef);
						$sth_upd->execute() or die $dbh->errstr;
						$DATASET->{'total'} += $sth_upd->rows();
						$sth_upd->finish;
					}else{
						$sth_ins->bind_param(++$param_num, $data->{'md_id'}, undef);
						$sth_ins->bind_param(++$param_num, $data->{'mv_id'}, undef);
						$sth_ins->bind_param(++$param_num, $ci_id, undef);
						$sth_ins->bind_param(++$param_num, $cdi_id, undef);
						$sth_ins->bind_param(++$param_num, $data->{'tbp_use'}, undef);
						$sth_ins->execute() or die $dbh->errstr;
						$DATASET->{'total'} += $sth_ins->rows();
						$sth_ins->finish;
					}
					undef $ci_id;
					undef $cdi_id;
				}
				undef $sth_ins;
				undef $sth_mv;
				undef $sth_cdi;

				$dbh->commit();

				$DATASET->{'success'} = JSON::XS::true;
			};
			if($@){
				$DATASET->{'msg'} = $@;
				print $LOG __LINE__,":",$@,"\n";
				$dbh->rollback;
			}
			$dbh->{'AutoCommit'} = 1;
			$dbh->{'RaiseError'} = 0;
		}
		elsif($FORM{'cmd'} eq 'update'){
			$dbh->{'AutoCommit'} = 0;
			$dbh->{'RaiseError'} = 1;
			eval{
				my $sql_upd=<<SQL;
update thumbnail_background_part set
 cdi_id=?,
 tbp_use=?,
 tbp_delcause=null,
 tbp_enter=now()
where
 md_id=? and
 mv_id=? and
 ci_id=? and
 cdi_id=?
SQL
				my $sth_upd = $dbh->prepare($sql_upd) or die $dbh->errstr;

				my $sql_mv='select ci_id from model_version where md_id=? and mv_id=?';
				my $sth_mv = $dbh->prepare($sql_mv) or die $dbh->errstr;

				my $sql_cdi='select cdi_id from concept_data_info where ci_id=? and cdi_name=?';
				my $sth_cdi = $dbh->prepare($sql_cdi) or die $dbh->errstr;

				foreach my $data (@$datas){
					next unless(
						exists $data->{'md_id'}    && defined $data->{'md_id'}    && $data->{'md_id'} &&
						exists $data->{'mv_id'}    && defined $data->{'mv_id'}    && $data->{'mv_id'} &&
						exists $data->{'cdi_name'} && defined $data->{'cdi_name'} && $data->{'cdi_name'} &&
						exists $data->{'cdi_name_org'} && defined $data->{'cdi_name_org'} && $data->{'cdi_name_org'} &&
						exists $data->{'tbp_use'}  && defined $data->{'tbp_use'}
					);

					my $ci_id;
					$sth_mv->execute($data->{'md_id'},$data->{'mv_id'}) or die $dbh->errstr;
					my $column_number = 0;
					$sth_mv->bind_col(++$column_number, \$ci_id, undef);
					$sth_mv->fetch;
					$sth_mv->finish;
					next unless(defined $ci_id);

					my $cdi_id;
					$sth_cdi->execute($ci_id,$data->{'cdi_name'}) or die $dbh->errstr;
					$column_number = 0;
					$sth_cdi->bind_col(++$column_number, \$cdi_id, undef);
					$sth_cdi->fetch;
					$sth_cdi->finish;
					next unless(defined $cdi_id);

					my $cdi_id_org;
					$sth_cdi->execute($ci_id,$data->{'cdi_name_org'}) or die $dbh->errstr;
					$column_number = 0;
					$sth_cdi->bind_col(++$column_number, \$cdi_id_org, undef);
					$sth_cdi->fetch;
					$sth_cdi->finish;
					next unless(defined $cdi_id_org);

					$data->{'tbp_use'} = $data->{'tbp_use'} ? 'true' : 'false';

					my $param_num=0;
					$sth_upd->bind_param(++$param_num, $cdi_id, undef);
					$sth_upd->bind_param(++$param_num, $data->{'tbp_use'}, undef);
					$sth_upd->bind_param(++$param_num, $data->{'md_id'}, undef);
					$sth_upd->bind_param(++$param_num, $data->{'mv_id'}, undef);
					$sth_upd->bind_param(++$param_num, $ci_id, undef);
					$sth_upd->bind_param(++$param_num, $cdi_id_org, undef);
					$sth_upd->execute() or die $dbh->errstr;
					$DATASET->{'total'} += $sth_upd->rows();
					$sth_upd->finish;
				}
				undef $sth_upd;
				undef $sth_mv;
				undef $sth_cdi;
				$dbh->commit();

				$DATASET->{'success'} = JSON::XS::true;
			};
			if($@){
				$DATASET->{'msg'} = $@;
				print $LOG __LINE__,":",$@,"\n";
				$dbh->rollback;
				$DATASET->{'success'} = JSON::XS::false;
			}
			$dbh->{'AutoCommit'} = 1;
			$dbh->{'RaiseError'} = 0;
		}
		elsif($FORM{'cmd'} eq 'destroy'){
			$dbh->{'AutoCommit'} = 0;
			$dbh->{'RaiseError'} = 1;
			eval{
=pod
				my $sql_del=<<SQL;
delete
from
 thumbnail_background_part
where
 md_id=? and
 mv_id=? and
 ci_id=? and
 cdi_id=?
SQL
=cut
				my $sql_del=<<SQL;
update thumbnail_background_part set
 tbp_delcause='DELETE',
 tbp_enter=now()
where
 md_id=? and
 mv_id=? and
 ci_id=? and
 cdi_id=?
SQL
				my $sth_del = $dbh->prepare($sql_del) or die $dbh->errstr;

				my $sql_mv='select ci_id from model_version where md_id=? and mv_id=?';
				my $sth_mv = $dbh->prepare($sql_mv) or die $dbh->errstr;

				my $sql_cdi='select cdi_id from concept_data_info where ci_id=? and cdi_name=?';
				my $sth_cdi = $dbh->prepare($sql_cdi) or die $dbh->errstr;

				foreach my $data (@$datas){
					next unless(
						exists $data->{'md_id'}    && defined $data->{'md_id'}    && $data->{'md_id'} &&
						exists $data->{'mv_id'}    && defined $data->{'mv_id'}    && $data->{'mv_id'} &&
						exists $data->{'cdi_name'} && defined $data->{'cdi_name'} && $data->{'cdi_name'}
					);

					my $ci_id;
					$sth_mv->execute($data->{'md_id'},$data->{'mv_id'}) or die $dbh->errstr;
					my $column_number = 0;
					$sth_mv->bind_col(++$column_number, \$ci_id, undef);
					$sth_mv->fetch;
					$sth_mv->finish;
					next unless(defined $ci_id);

					my $cdi_id;
					$sth_cdi->execute($ci_id,$data->{'cdi_name'}) or die $dbh->errstr;
					$column_number = 0;
					$sth_cdi->bind_col(++$column_number, \$cdi_id, undef);
					$sth_cdi->fetch;
					$sth_cdi->finish;
					next unless(defined $cdi_id);

					my $param_num=0;
					$sth_del->bind_param(++$param_num, $data->{'md_id'}, undef);
					$sth_del->bind_param(++$param_num, $data->{'mv_id'}, undef);
					$sth_del->bind_param(++$param_num, $ci_id, undef);
					$sth_del->bind_param(++$param_num, $cdi_id, undef);
					$sth_del->execute() or die $dbh->errstr;
					$DATASET->{'total'} += $sth_del->rows();
					$sth_del->finish;
				}
				undef $sth_del;
				undef $sth_mv;
				undef $sth_cdi;

				$dbh->commit();

				$DATASET->{'success'} = JSON::XS::true;
			};
			if($@){
				$DATASET->{'msg'} = $@;
				print $LOG __LINE__,":",$@,"\n";
				$dbh->rollback;
				$DATASET->{'success'} = JSON::XS::false;
			}
			$dbh->{'AutoCommit'} = 1;
			$dbh->{'RaiseError'} = 0;
		}
	}
}

&gzip_json($DATASET);
exit;


sub make_art_images {
	my $LIST = shift;
	my $sessionID;

	return unless(defined $LIST && ref $LIST eq 'ARRAY' && scalar @$LIST > 0);

	my $prog_basename = qq|make_art_image|;
	my $prog = &catfile($FindBin::Bin,'..','cron',qq|$prog_basename.pl|);
	return unless(-e $prog && -X $prog);

	my $sessionID = &Digest::MD5::md5_hex(&Time::HiRes::time());
	my $out_path = &catdir($FindBin::Bin,'temp');
	my $params_file = &catfile($out_path,qq|$sessionID.json|);
	open(OUT,"> $params_file") or die $!;
	flock(OUT,2);
	print OUT &JSON::XS::encode_json($LIST);
	close(OUT);
	chmod 0666,$params_file;

	my $pid = fork;
	if(defined $pid){
		if($pid == 0){
			my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
			$year = sprintf("%04d",$year+1900);
			$mon  = sprintf("%02d",$mon+1);
			$mday = sprintf("%02d",$mday);
			my $d = &catdir($FindBin::Bin,'logs',$year,$mon,$mday);
			&File::Path::make_path($d) unless(-e $d);
			my $f1 = &catfile($d,qq|$prog_basename.log|);
			my $f2 = &catfile($d,qq|$prog_basename.err|);
			close(STDOUT);
			close(STDERR);
			open STDOUT, ">> $f1" || die "[$f1] $!\n";
			open STDERR, ">> $f2" || die "[$f2] $!\n";
			close(STDIN);
			exec(qq|nice -n 19 $prog $params_file|);
			exit(1);
		}
	}else{
		die("Can't execute program");
	}
}

sub make_cm_images {
	my $prog_basename = qq|make_cm_image|;
	my $prog = &catfile($FindBin::Bin,'..','cron',qq|$prog_basename.pl|);
	return unless (-e $prog && -X $prog);

	my $pid = fork;
	if(defined $pid){
		if($pid == 0){
			my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
			$year = sprintf("%04d",$year+1900);
			$mon  = sprintf("%02d",$mon+1);
			$mday = sprintf("%02d",$mday);
			my $d = &catdir($FindBin::Bin,'logs',$year,$mon,$mday);
			&File::Path::make_path($d) unless(-e $d);
			my $f1 = &catfile($d,qq|$prog_basename.log|);
			my $f2 = &catfile($d,qq|$prog_basename.err|);
			close(STDOUT);
			close(STDERR);
			open STDOUT, ">> $f1" || die "[$f1] $!\n";
			open STDERR, ">> $f2" || die "[$f2] $!\n";
			close(STDIN);
			exec(qq|nice -n 19 $prog|);
			exit(1);
		}
	}else{
		die("Can't execute program");
	}
}
