#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use JSON::XS;

require "common.pl";
require "common_db.pl";
my $dbh = &get_dbh();

my %FORM = ();
&decodeForm(\%FORM);
delete $FORM{_formdata} if(exists($FORM{_formdata}));

my %COOKIE = ();
&getCookie(\%COOKIE);

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
open(LOG,">> log.txt");
print LOG "\n[$logtime]:$0\n";
foreach my $key (sort keys(%FORM)){
	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
}
foreach my $key (sort keys(%COOKIE)){
	print LOG __LINE__,":\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
}

$FORM{lng} = $COOKIE{"ag_annotation.locale"} if(!exists($FORM{lng}) && exists($COOKIE{"ag_annotation.locale"})); #とりあえず
$FORM{lng} = "en" if(!exists($FORM{lng}));

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);

my $wt_version = qq|tg_id=$FORM{tg_id} and tgi_id=$FORM{tgi_id}|;

print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $TREE = {
	"data"  => [],
	"total" => 0
};

if(!exists($FORM{f_id})){
#	print to_json($TREE);
	print encode_json($TREE);
#	print LOG __LINE__,":",to_json($TREE),"\n";
	print LOG __LINE__,":",encode_json($TREE),"\n";
	close(LOG);
	exit;
}

my $cache_path = qq|cache_fma|;
unless(-e $cache_path){
	mkdir $cache_path;
	chmod 0777,$cache_path;
}
if(exists($FORM{version})){
	$cache_path .= qq|/$FORM{version}|;
	unless(-e $cache_path){
		mkdir $cache_path;
		chmod 0777,$cache_path;
	}
}
$cache_path .= qq|/conventional_child|;
unless(-e $cache_path){
	mkdir $cache_path;
	chmod 0777,$cache_path;
}
$cache_path .= qq|/$FORM{lng}|;
unless(-e $cache_path){
	mkdir $cache_path;
	chmod 0777,$cache_path;
}

my $cache_file = qq|$cache_path/$FORM{f_id}.txt|;
my $cache_lock = qq|$cache_path/$FORM{f_id}.lock|;
if(!-e $cache_file && !mkdir($cache_lock)){
	exit if(!exists($ENV{'REQUEST_METHOD'}));
	my $wait = 30;
	while($wait){
		if(-e $cache_lock){
			$wait--;
			sleep(1);
			next;
		}
		last;
	}
}
=debug
if(-e $cache_file && -s $cache_file){
	open(IN,"< $cache_file");
	my @CACHE = <IN>;
	close(IN);
	my $json = join('',@CACHE);
	print $json;
	print LOG $json,"\n";
	close(LOG);
	exit;
}
=cut

my $sql = qq|select tree.f_id from tree where $wt_version and tree.f_pid=? and tree.t_type=1 group by tree.f_id|;
print LOG __LINE__,qq|:\$sql=[$sql]\n|;
my $sth_conventional  = $dbh->prepare($sql);


my $f_cid;
my @RTN = ();

my $f_id = $FORM{f_id};

print LOG __LINE__,":$f_id\n";

push(@RTN,&getFMA($dbh,\%FORM,$f_id));

$f_id =~ s/\D+$//g if($f_id =~/^(?:FMA|BP)/);
;
$sth_conventional->execute($f_id);
print LOG __LINE__,":",$sth_conventional->rows(),"\n";

my $column_number = 0;
$sth_conventional->bind_col(++$column_number, \$f_cid, undef);
while($sth_conventional->fetch){
	print LOG $f_cid,"\n";
	push(@RTN,&getFMA($dbh,\%FORM,$f_cid));
}
$sth_conventional->finish;

my %HASH = ();

foreach my $hash (@RTN){
	next if(exists($HASH{$hash->{f_id}}));
	$HASH{$hash->{f_id}} = 1;
	push(@{$TREE->{data}},$hash);
}
#@{$TREE->{data}} = @{$TREE->{data}};
$TREE->{total} = scalar @{$TREE->{data}};

#my $json = to_json($TREE);
my $json = encode_json($TREE);
$json =~ s/"(true|false)"/$1/mg;

print $json;
print LOG __LINE__,":",$json,"\n";

open(OUT,"> $cache_file");
print OUT $json;
close(OUT);

close(LOG);

rmdir($cache_lock);

exit;
