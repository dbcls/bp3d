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

#&setDefParams(\%FORM,\%COOKIE);
#&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);

#&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
#&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);

#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $where;
my @bind_values = ();
if(exists $FORM{'filter'} && defined $FORM{'filter'} && length $FORM{'filter'}){
	my $filter = &cgi_lib::common::decodeJSON($FORM{'filter'});
	if(defined $filter && ref $filter eq 'ARRAY'){
		my @W;
		foreach my $f (@$filter){
			next unless(exists $f->{property} && defined $f->{property} && length $f->{property});
			if(exists $f->{value} && defined $f->{value} && length $f->{value}){
				push(@W,qq|$f->{property}=?|);
				push(@bind_values,$f->{value});
			}else{
				push(@W,qq|$f->{property} is null|);
			}
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
 ci.ci_id,
 ci.ci_name,
 cb.cb_id,
 cb.cb_name,
 cb.cb_comment,
 cb.cb_filename,
 EXTRACT(EPOCH FROM cb_release) as cb_release,
 cb_order,
 cb_use,
 CASE WHEN cb.cb_comment is not null and length(cb.cb_comment)>0 THEN ci.ci_name || ' ' || cb.cb_name || ' [' || cb.cb_comment || ']'
      ELSE ci.ci_name || ' ' || cb.cb_name
 END as display,
 ci.ci_id || '-' || cb.cb_id as value
from
 concept_info as ci
left join (
  select * from concept_build
--  where cb_use
 ) as cb on cb.ci_id=ci.ci_id
where
 ci.ci_use
-- and cb.cb_use
order by
 ci_order,
 cb_order
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

		my($ci_id,$ci_name,$cb_id,$cb_name,$cb_comment,$cb_filename,$cb_release,$cb_order,$cb_use,$display,$value);

		my $column_number = 0;
		$sth->bind_col(++$column_number, \$ci_id, undef);
		$sth->bind_col(++$column_number, \$ci_name, undef);
		$sth->bind_col(++$column_number, \$cb_id, undef);
		$sth->bind_col(++$column_number, \$cb_name, undef);
		$sth->bind_col(++$column_number, \$cb_comment, undef);
		$sth->bind_col(++$column_number, \$cb_filename, undef);
		$sth->bind_col(++$column_number, \$cb_release, undef);
		$sth->bind_col(++$column_number, \$cb_order, undef);
		$sth->bind_col(++$column_number, \$cb_use, undef);
		$sth->bind_col(++$column_number, \$display, undef);
		$sth->bind_col(++$column_number, \$value, undef);

		while($sth->fetch){
			my $HASH = {
				ci_id       => $ci_id - 0,
				ci_name     => $ci_name,
				cb_id       => $cb_id - 0,
				cb_name     => $cb_name,
				cb_filename => $cb_filename,
				cb_release  => $cb_release - 0,
				cb_order    => $cb_order - 0,
				cb_use      => $cb_use ? JSON::XS::true : JSON::XS::false,
				cb_comment  => $cb_comment,

				display => $display,
				value   => $value,

			};
			push(@{$DATASET->{'datas'}},$HASH);
		}
		$sth->finish;
		undef $sth;

		$DATASET->{'total'} = scalar @{$DATASET->{'datas'}};
		$DATASET->{'success'} = JSON::XS::true;
	};
	if($@){
		$DATASET->{'msg'} = &cgi_lib::common::decodeUTF8($@);
		&cgi_lib::common::message($@,$LOG);
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
				my $sth = $dbh->prepare(qq|update concept_build set cb_name=?,cb_release=?,cb_order=?,cb_use=?,cb_comment=? where ci_id=? and cb_id=?|) or die $dbh->errstr;
				foreach my $data (@$datas){
					my $rows = $sth->execute($data->{'cb_name'},$data->{'cb_release'},$data->{'cb_order'},$data->{'cb_use'},$data->{'cb_comment'},$data->{'ci_id'},$data->{'cb_id'}) or die $dbh->errstr;
					$DATASET->{'total'} += $rows if($rows>0);
					$sth->finish;
				}
				undef $sth;
				$dbh->commit();

				$DATASET->{'success'} = JSON::XS::true;
			};
			if($@){
				$DATASET->{'msg'} = &cgi_lib::common::decodeUTF8($@);
				&cgi_lib::common::message($@,$LOG);
				$dbh->rollback;
			}
			$dbh->{'AutoCommit'} = 1;
			$dbh->{'RaiseError'} = 0;
		}
	}
}

#my $json = &JSON::XS::encode_json($DATASET);
#print $json;
&gzip_json($DATASET);

close($LOG);
