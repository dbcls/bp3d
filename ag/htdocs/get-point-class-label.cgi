#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use JSON::XS;
#use File::Basename;

require "common.pl";
require "common_db.pl";
my $dbh = &get_dbh();

my %FORM = ();
&decodeForm(\%FORM);
delete $FORM{_formdata} if(exists($FORM{_formdata}));

my %COOKIE = ();
&getCookie(\%COOKIE);

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $file = sprintf("%04d%02d%02d%02d%02d%02d_%d",$year+1900,$mon+1,$mday,$hour,$min,$sec,$$);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);

#my @extlist = qw|.cgi|;
#my($name,$dir,$ext) = fileparse($0,@extlist);

#open(LOG,">> ./tmp_image/$name.txt");
open(LOG,">> log.txt");
print LOG "\n[$logtime]:$0\n";
foreach my $key (sort keys(%FORM)){
	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
}
foreach my $key (sort keys(%COOKIE)){
	print LOG __LINE__,":\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
}
#foreach my $key (sort keys(%ENV)){
#	print LOG "ENV{$key}=[",$ENV{$key},"]\n";
#}



print qq|Content-type: text/html; charset=UTF-8\n\n|;


if(!exists($FORM{version})){
	print qq|{success:false,msg:"There is not Category information"}|;
	print LOG __LINE__,qq|:{success:false,msg:"There is not Category information"}\n|;
	close(LOG);
	exit;
}

$FORM{lng} = $COOKIE{"ag_annotation.locale"} if(!exists($FORM{lng}) && exists($COOKIE{"ag_annotation.locale"})); #とりあえず
$FORM{lng} = "en" if(!exists($FORM{lng}));

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);

my $wt_version = qq|tg_id=$FORM{tg_id} and tgi_id=$FORM{tgi_id}|;

my $RTN = {
	success => JSON::XS::true,
	records => [{
		disp  => 'ALL',
		value => '',
	}]
};

my $sql = qq|select p_label from bp3d_point where $wt_version and p_delcause is null group by p_label order by p_label|;
print LOG __LINE__,":\$sql=[",$sql,"]\n";

my $p_label;
my $sth_bp3d_point = $dbh->prepare($sql);
$sth_bp3d_point->execute();
my $count = $sth_bp3d_point->rows();
my $column_number = 0;
$sth_bp3d_point->bind_col(++$column_number, \$p_label, undef);
while($sth_bp3d_point->fetch){
	push(@{$RTN->{records}},{
		disp  => $p_label,
		value => $p_label,
	});
}
$sth_bp3d_point->finish;
undef $sth_bp3d_point;

my $json = encode_json($RTN);
print $json;
print LOG __LINE__,":",$json,"\n";

close(LOG);
exit;
