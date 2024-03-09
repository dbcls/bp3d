#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use DBD::Pg;
use File::Copy;
use File::Spec;

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
$logfile .=  sprintf(".%02d%02d%02d.%05d",$hour,$min,$sec,$$);

open(my $LOG,"> $logfile");
select($LOG);
$| = 1;
select(STDOUT);
flock($LOG,2);
print $LOG "\n[$logtime]:$0\n";
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%ENV, 1), $LOG);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);

my $ci_id=$FORM{'ci_id'};
my $cb_id=$FORM{'cb_id'};
my $md_id=$FORM{'md_id'};
my $mv_id=$FORM{'mv_id'};
my $crl_id=$FORM{'crl_id'};

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

my $where;
my @bind_values = ();
if(exists $FORM{'filter'} && defined $FORM{'filter'}){
	my $filter = &cgi_lib::common::decodeJSON($FORM{'filter'});
	if(defined $filter){
		my @W;
		foreach my $f (@$filter){
			next unless(exists $f->{'property'} && defined $f->{'property'} && exists $f->{'value'} && defined $f->{'value'});
			push(@W,qq|$f->{property}=?|);
			push(@bind_values,$f->{value});
		}
		$where = qq|where |.join(" and ",@W) if(scalar @W > 0);
	}
}
$where = '' unless(defined $where && length $where);
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
select * from (
select
 mv.md_id,
 mv.mv_id,

 mv.mv_version,
 md_name_e,
 md_abbr,
 mv_name_e,

 mv_comment,

 mv.ci_id,
 ci.ci_name,
 mv.cb_id,
 cb.cb_name,
 cb.cb_comment,
 CASE WHEN cb.cb_comment is not null and length(cb.cb_comment)>0 THEN ci.ci_name || ' ' || cb.cb_name || ' [' || cb.cb_comment || ']'
      ELSE ci.ci_name || ' ' || cb.cb_name
 END as cb_display,

 mv.mv_name_e || ' [' || ci.ci_name || ' ' || cb.cb_name || ']' as display,
 mv.mv_version as value,

 EXTRACT(EPOCH FROM mv_entry) as mv_entry,
 EXTRACT(EPOCH FROM mv_modified) as mv_modified,

 EXTRACT(EPOCH FROM cb_release) as cb_release
from
 model_version as mv
left join (
  select * from model
 ) as md on md.md_id=mv.md_id

left join (
  select * from concept_info
 ) as ci on ci.ci_id=mv.ci_id
left join (
  select
   ci_id,
   cb_id,
   cb_name,
   cb_release,
   cb_comment
  from
   concept_build
 ) as cb on cb.ci_id=mv.ci_id and cb.cb_id=mv.cb_id
where
 md.md_use

order by
 md_order,
 mv_order
) as a
$where
SQL

		print $LOG __LINE__,":\$sql=[",$sql,"]\n";
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		if(scalar @bind_values > 0){
			$DATASET->{'total'} = $sth->execute(@bind_values) or die $dbh->errstr;
		}else{
			$DATASET->{'total'} = $sth->execute() or die $dbh->errstr;
		}

		my($md_id,$mv_id,$mr_id,$mv_version,$md_name_e,$md_abbr,$mv_name_e,$mv_objects_set,$mv_publish,$mv_port,$mv_frozen,$mv_comment,$mv_order,$mv_use,$ci_id,$ci_name,$cb_id,$cb_name,$cb_comment,$cb_display,$concept,$display,$value,$mv_entry,$mv_modified,$cb_release);

		my $column_number = 0;
		$sth->bind_col(++$column_number, \$md_id, undef);
		$sth->bind_col(++$column_number, \$mv_id, undef);

		$sth->bind_col(++$column_number, \$mv_version, undef);
		$sth->bind_col(++$column_number, \$md_name_e, undef);
		$sth->bind_col(++$column_number, \$md_abbr, undef);
		$sth->bind_col(++$column_number, \$mv_name_e, undef);

		$sth->bind_col(++$column_number, \$mv_comment, undef);


		$sth->bind_col(++$column_number, \$ci_id, undef);
		$sth->bind_col(++$column_number, \$ci_name, undef);
		$sth->bind_col(++$column_number, \$cb_id, undef);
		$sth->bind_col(++$column_number, \$cb_name, undef);
		$sth->bind_col(++$column_number, \$cb_comment, undef);
		$sth->bind_col(++$column_number, \$cb_display, undef);

		$sth->bind_col(++$column_number, \$display, undef);
		$sth->bind_col(++$column_number, \$value, undef);

		$sth->bind_col(++$column_number, \$mv_entry, undef);
		$sth->bind_col(++$column_number, \$mv_modified, undef);

		$sth->bind_col(++$column_number, \$cb_release, undef);

		while($sth->fetch){

			my $HASH = {
				md_id => $md_id - 0,
				mv_id => $mv_id - 0,

				ci_id => $ci_id - 0,
				ci_name => $ci_name,
				cb_id => $cb_id - 0,
				cb_name => $cb_name,
				cb_comment => $cb_comment,
				cb_display => $cb_display,

				md_name_e => $md_name_e,
				md_abbr => $md_abbr,
				mv_entry => $mv_entry - 0,
				mv_modified => $mv_modified - 0,

				mv_version => $mv_version,
				cb_release => $cb_release+0,

				display => $display,

				value   => $value,
				version => $mv_name_e

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

}elsif(exists $FORM{'datas'} && defined $FORM{'datas'}){
	my $datas = &cgi_lib::common::decodeJSON($FORM{'datas'});
	if(defined $datas && ref $datas eq 'ARRAY'){
		if($FORM{'cmd'} eq 'create'){
		}
		elsif($FORM{'cmd'} eq 'update'){
			$dbh->{'AutoCommit'} = 0;
			$dbh->{'RaiseError'} = 1;
			eval{
				my $sth_mv_upd = $dbh->prepare(qq|update model_version set cb_id=?,mv_modified=now() where md_id=? AND mv_id=?|) or die $dbh->errstr;

				foreach my $data (@$datas){
					$sth_mv_upd->execute($data->{'cb_id'},$data->{'md_id'},$data->{'mv_id'}) or die $dbh->errstr;
					$sth_mv_upd->finish;
				}
				undef $sth_mv_upd;

				$dbh->commit();

				$dbh->do("NOTIFY model_version");

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
	}
	else{
		$DATASET->{'msg'} = &cgi_lib::common::decodeUTF8('JSON形式が違います');
	}
}

#my $json = &JSON::XS::encode_json($DATASET);
#print $json;
&gzip_json($DATASET);
close($LOG);
exit;
