#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
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

open(LOG,"> $logfile");
flock(LOG,2);
print LOG "\n[$logtime]:$0\n";
foreach my $key (sort keys(%FORM)){
	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
}
#foreach my $key (sort keys(%COOKIE)){
#	print LOG "\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
#}
#foreach my $key (sort keys(%ENV)){
#	print LOG __LINE__,":\$ENV{$key}=[",$ENV{$key},"]\n";
#}

&setDefParams(\%FORM,\%COOKIE);
foreach my $key (sort keys(%FORM)){
	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
}

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
foreach my $key (sort keys(%FORM)){
	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
}

my @SORT;
if(defined $FORM{'sort'}){
	my $sort;
	eval{$sort = &JSON::XS::decode_json($FORM{'sort'});};
	push(@SORT,@$sort) if(defined $sort);
}
if(scalar @SORT == 0){
	push(@SORT,{
		property  => 'cdi_name_e',
		direction => 'ASC'
	});
}

my %SELECTED;
if(defined $FORM{'selected'}){
	my $selected;
	eval{$selected = &JSON::XS::decode_json($FORM{'selected'});};
	%SELECTED = map{ $_->{'f_id'} => $_ } @$selected if(defined $selected);
}


#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $DATAS = {
	"datas" => [],
	"total" => 0
};

my $sql=<<SQL;
select * from (
select
 rep.ci_id,
 rep.cb_id,
 rep.md_id,
 rep.mv_id,
 rep.mr_id,
 rep.bul_id,
 rep_id,
 rep_xmin,
 rep_xmax,
 to_number(to_char((rep_xmax+rep_xmin)/2,'FM99990D0000'),'99990D0000S') as rep_xcenter,
 rep_ymin,
 rep_ymax,
 to_number(to_char((rep_ymax+rep_ymin)/2,'FM99990D0000'),'99990D0000S') as rep_ycenter,
 rep_zmin,
 rep_zmax,
 to_number(to_char((rep_zmax+rep_zmin)/2,'FM99990D0000'),'99990D0000S') as rep_zcenter,
 rep_volume,
 EXTRACT(EPOCH FROM rep_entry),
 cdi_name,
 cdi_name_j,
 cdi_name_e,
 cdi_name_k,
 cdi_name_l,
 md.md_abbr,
 mv.mv_name_e,
 bul.bul_abbr
from
 view_representation as rep
left join (
  select * from model
 ) as md on md.md_id=rep.md_id
left join (
  select * from model_version
 ) as mv on mv.md_id=rep.md_id and mv.mv_id=rep.mv_id
left join (
  select * from buildup_logic
 ) as bul on bul.bul_id=rep.bul_id
where
 (rep.ci_id,rep.cb_id,rep.cdi_id,rep.md_id,rep.mv_id,rep.mr_id,rep.bul_id) in (
   select
    ci_id,cb_id,cdi_id,md_id,mv_id,max(mr_id) as mr_id,bul_id
   from
    representation
   where
    ci_id=$FORM{ci_id} AND
    cb_id=$FORM{cb_id} AND
    md_id=$FORM{md_id} AND
    mv_id=$FORM{mv_id} AND
    mr_id<=$FORM{mr_id} AND
    bul_id=$FORM{bul_id}
   group by
    ci_id,cb_id,cdi_id,md_id,mv_id,bul_id
 )
) as a
SQL

if(scalar @SORT > 0){
	my @orderby;
	foreach (@SORT){
		push(@orderby,qq|$_->{property} $_->{direction}|);
	}
	$sql .= qq| order by | . join(",",@orderby) if(scalar @orderby > 0);
}

print LOG __LINE__,":\$sql=[$sql]\n";

my $sth = $dbh->prepare($sql) or die $dbh->errstr;
$sth->execute() or die $dbh->errstr;
$DATAS->{'total'} = $sth->rows();
$sth->finish;
undef $sth;

$sql .= qq| limit $FORM{limit}| if(defined $FORM{limit});
$sql .= qq| offset $FORM{start}| if(defined $FORM{start});
my $sth = $dbh->prepare($sql) or die $dbh->errstr;
$sth->execute() or die $dbh->errstr;

my $ci_id;
my $cb_id;
my $md_id;
my $mv_id;
my $mr_id;
my $bul_id;

my $rep_id;
my $rep_xmin;
my $rep_xmax;
my $rep_xcenter;
my $rep_ymin;
my $rep_ymax;
my $rep_ycenter;
my $rep_zmin;
my $rep_zmax;
my $rep_zcenter;
my $rep_volume;
my $rep_entry;
my $cdi_name;
my $cdi_name_j;
my $cdi_name_e;
my $cdi_name_k;
my $cdi_name_l;
my $md_abbr;
my $mv_name_e;
my $bul_abbr;

my $column_number = 0;
$sth->bind_col(++$column_number, \$ci_id,   undef);
$sth->bind_col(++$column_number, \$cb_id,   undef);
$sth->bind_col(++$column_number, \$md_id,   undef);
$sth->bind_col(++$column_number, \$mv_id,   undef);
$sth->bind_col(++$column_number, \$mr_id,   undef);
$sth->bind_col(++$column_number, \$bul_id,   undef);

$sth->bind_col(++$column_number, \$rep_id,   undef);
$sth->bind_col(++$column_number, \$rep_xmin,   undef);
$sth->bind_col(++$column_number, \$rep_xmax,   undef);
$sth->bind_col(++$column_number, \$rep_xcenter,   undef);

$sth->bind_col(++$column_number, \$rep_ymin,   undef);
$sth->bind_col(++$column_number, \$rep_ymax,   undef);
$sth->bind_col(++$column_number, \$rep_ycenter,   undef);

$sth->bind_col(++$column_number, \$rep_zmin,   undef);
$sth->bind_col(++$column_number, \$rep_zmax,   undef);
$sth->bind_col(++$column_number, \$rep_zcenter,   undef);

$sth->bind_col(++$column_number, \$rep_volume,   undef);
$sth->bind_col(++$column_number, \$rep_entry,   undef);
$sth->bind_col(++$column_number, \$cdi_name,   undef);
$sth->bind_col(++$column_number, \$cdi_name_j,   undef);
$sth->bind_col(++$column_number, \$cdi_name_e,   undef);
$sth->bind_col(++$column_number, \$cdi_name_k,   undef);
$sth->bind_col(++$column_number, \$cdi_name_l,   undef);
$sth->bind_col(++$column_number, \$md_abbr,   undef);
$sth->bind_col(++$column_number, \$mv_name_e,   undef);
$sth->bind_col(++$column_number, \$bul_abbr,   undef);
while($sth->fetch){
	my $HASH = {
		ci_id      => $ci_id,
		cb_id      => $cb_id,
		md_id      => $md_id,
		mv_id      => $mv_id,
		mr_id      => $mr_id,
		bul_id      => $bul_id,

		rep_id      => $rep_id,
		rep_xmin    => $rep_xmin,
		rep_xmax    => $rep_xmax,
		rep_xcenter => $rep_xcenter,
		rep_ymin    => $rep_ymin,
		rep_ymax    => $rep_ymax,
		rep_ycenter => $rep_ycenter,
		rep_zmin    => $rep_zmin,
		rep_zmax    => $rep_zmax,
		rep_zcenter => $rep_zcenter,
		rep_volume  => $rep_volume,
		rep_entry   => $rep_entry,
		cdi_name    => $cdi_name,
		cdi_name_j  => $cdi_name_j,
		cdi_name_e  => $cdi_name_e,
		cdi_name_k  => $cdi_name_k,
		cdi_name_l  => $cdi_name_l,
		md_abbr     => $md_abbr,
		mv_name_e   => $mv_name_e,
		bul_abbr    => $bul_abbr,
	};

	if(defined $SELECTED{$cdi_name}){
		foreach my $key (qw(color opacity remove selected)){
			next unless(defined $SELECTED{$cdi_name}->{$key});
			$HASH->{$key} = $SELECTED{$cdi_name}->{$key};
		}
	}

	push(@{$DATAS->{'datas'}},$HASH);
}
$sth->finish;
undef $sth;

#print &JSON::XS::encode_json($DATAS);
&gzip_json($DATAS);

close(LOG);
