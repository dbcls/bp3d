#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
require "webgl_common.pl";

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);

my($logfile,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
$logfile .=  sprintf(".%02d%02d%02d.%05d",$hour,$min,$sec,$$);
open(my $LOG,"> $logfile");
print $LOG "\n[$logtime]:$0\n";
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%ENV, 1), $LOG);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);

&setDefParams(\%FORM,\%COOKIE);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);

#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $where;
my @bind_values = ();
if(exists $FORM{'filter'}){
	my $filter;
	eval{$filter=&JSON::XS::decode_json($FORM{'filter'});};
	if(defined $filter){
		my @W;
		foreach my $f (@$filter){
			push(@W,qq|$f->{property}=?|);
			push(@bind_values,$f->{value});
		}
		$where = qq|where |.join(" and ",@W) if(scalar @W > 0);
	}
}
#29:$FORM{'filter'}=[[{"property":"md_id","value":1}]]

my $DATASET = {
	datas => [],
	total => 0,
	success => JSON::XS::false
};

my $sql=<<SQL;
select distinct
 but.ci_id,
 ci_name,
 but.cb_id,
 cb_name,
 bul.bul_id,
 bul_name_e as bul_name,
 bul_abbr,
 cb_comment
from
 model_version as but,
 concept_info as ci,
 concept_build as cb,
 buildup_logic as bul
where
 but.ci_id=ci.ci_id and
 ci.ci_use and
 but.ci_id=cb.ci_id and
 but.cb_id=cb.cb_id and
-- cb.cb_use and
-- but.bul_id=bul.bul_id and
 bul_use
SQL

if(exists $FORM{'ci_id'} && defined $FORM{'ci_id'} && length $FORM{'ci_id'}){
	$sql .= qq| AND but.ci_id=?|;
	push @bind_values, $FORM{'ci_id'};
}
if(exists $FORM{'cb_id'} && defined $FORM{'cb_id'} && length $FORM{'cb_id'}){
	$sql .= qq| AND but.cb_id=?|;
	push @bind_values, $FORM{'cb_id'};
}

print $LOG __LINE__,":\$sql=[",$sql,"]\n";
my $sth = $dbh->prepare($sql) or die $dbh->errstr;
if(scalar @bind_values > 0){
	$DATASET->{'total'} = $sth->execute(@bind_values) or die $dbh->errstr;
}else{
	$DATASET->{'total'} = $sth->execute() or die $dbh->errstr;
}

my($ci_id,$ci_name,$cb_id,$cb_name,$bul_id,$bul_name,$bul_abbr,$cb_comment);

my $column_number = 0;
$sth->bind_col(++$column_number, \$ci_id, undef);
$sth->bind_col(++$column_number, \$ci_name, undef);
$sth->bind_col(++$column_number, \$cb_id, undef);
$sth->bind_col(++$column_number, \$cb_name, undef);
$sth->bind_col(++$column_number, \$bul_id, undef);
$sth->bind_col(++$column_number, \$bul_name, undef);
$sth->bind_col(++$column_number, \$bul_abbr, undef);
$sth->bind_col(++$column_number, \$cb_comment, undef);

while($sth->fetch){
#	$display .= qq| [$cb_comment]| if(defined $cb_comment);
#	my $display = qq|$ci_name $cb_name $bul_name|;
	my $display = qq|$bul_name|;
	my $HASH = {
		ci_id => $ci_id,
		ci_name => $ci_name,
		cb_id => $cb_id,
		cb_name => $cb_name,
		bul_id => $bul_id,
		bul_name => $bul_name,
		bul_abbr => $bul_abbr,

		display => $display,
#		value   => qq|$ci_id-$cb_id-$bul_id|,
#		value   => qq|$ci_name-$cb_name-$bul_abbr|,
		value   => $bul_abbr,
		tree => $bul_abbr

	};
	push(@{$DATASET->{datas}},$HASH);
}
$sth->finish;
undef $sth;

$DATASET->{'success'} = JSON::XS::true;


#my $json = &JSON::XS::encode_json($DATASET);
#print $json;
&gzip_json($DATASET);

close($LOG);

exit;

print <<HTML;
{datas: [{
	display:    '4.0',
	value:      '1-3',
	version:    '4.0.1305021540',
	data:       'obj/bp3d/4.0',
	md_id:      1,
	mv_id:      3,
	mv_publish: true
},{
	display:    '3.0',
	value:      '1-2',
	version:    '3.0.1304161700',
	data:       'obj/bp3d/3.0',
	md_id:      1,
	mv_id:      2,
	mv_publish: true
},{
	display:    '2.0',
	value:      '1-1',
	version:    '2.0.1304161700',
	data:       'obj/bp3d/2.0',
	md_id:      1,
	mv_id:      1,
	mv_publish: true
}
HTML
