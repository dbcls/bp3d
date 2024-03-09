#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use JSON::XS;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
use BITS::ReCalc;
require "webgl_common.pl";
use cgi_lib::common;

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $cgi = CGI->new;
&getParams($cgi,\%FORM,\%COOKIE);
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
$logfile .= '.'.sprintf("%04d%02d%02d%02d",$year+1900,$mon+1,$mday,$hour);

open(my $LOG,">> $logfile");
select($LOG);
$| = 1;
select(STDOUT);

flock($LOG,2);
print $LOG "\n[$logtime]:$0\n";
foreach my $key (sort keys(%FORM)){
	print $LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
}

#&setDefParams(\%FORM,\%COOKIE);
#&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);

my $DATAS = {
	"datas" => [],
	"total" => 0,
	"success" => JSON::XS::false
};

#=pod
unless(
	exists $FORM{'ci_id'} && defined $FORM{'ci_id'}
){
	&gzip_json($DATAS);
	exit;
}
#=cut

eval{
	my @SORT;
	if(defined $FORM{'sort'}){
		my $sort = &cgi_lib::common::decodeJSON($FORM{'sort'});
		push(@SORT,@$sort) if(defined $sort);
	}
	if(scalar @SORT == 0){
		push(@SORT,{
			property  => 'cmp_id',
			direction => 'ASC'
		});
	}

	my $ci_id=$FORM{'ci_id'};

	my $sql=<<SQL;
select
 cmp_id,
 cmp_title,
 cmp_abbr,
 cmp_prefix,
 cmp_order
from
 concept_art_map_part
WHERE
 cmp_use
SQL

	print $LOG __LINE__,":\$sql=[$sql]\n";

	my $cmp_id;
	my $cmp_title;
	my $cmp_abbr;
	my $cmp_prefix;
	my $cmp_order;

	if(scalar @SORT > 0){
		my @orderby;
		push(@orderby,qq|$_->{property} $_->{direction}|) for(@SORT);
		$sql .= qq| order by | . join(",",@orderby) if(scalar @orderby > 0);
	}

	print $LOG __LINE__,":\$sql=[$sql]\n";

	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$DATAS->{'total'} = $sth->rows();



	my $column_number = 0;
	$sth->bind_col(++$column_number, \$cmp_id,   undef);
	$sth->bind_col(++$column_number, \$cmp_title,   undef);
	$sth->bind_col(++$column_number, \$cmp_abbr,   undef);
	$sth->bind_col(++$column_number, \$cmp_prefix,   undef);
	$sth->bind_col(++$column_number, \$cmp_order,   undef);

	while($sth->fetch){
		my $HASH = {
			cmp_id     => $cmp_id-0,
			cmp_title  => $cmp_title,
			cmp_abbr   => $cmp_abbr,
			cmp_prefix => $cmp_prefix,
			cmp_order  => $cmp_order-0,
		};
		push(@{$DATAS->{'datas'}},$HASH);
	}
	$sth->finish;
	undef $sth;

	$DATAS->{'success'} = JSON::XS::true;
};
if($@){
	$DATAS->{'msg'} = $@;
}
#print &JSON::XS::encode_json($DATAS);
&gzip_json($DATAS);

close($LOG);
