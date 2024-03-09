#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI::Cookie;
use Cwd;
use FindBin;

require "common.pl";
require "common_db.pl";
my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();

unless(exists($ENV{'REQUEST_METHOD'})){
#	$ENV{'REQUEST_METHOD'} = 'POST';
	$ENV{'HTTP_COOKIE'} = qq|ag_annotation.images.sort=volume; ag_annotation.images.node=ynode-2534; ag_annotation.images.path=/FMA62955/FMA61775/FMA67165/FMA67135/FMA82472/FMA67619/FMA86140; ag_annotation.locale=ja; ag_annotation.session=acb1a41ce38de0eff5969ab9b7d088fb; ag_annotation.images.tg_id=1; ag_annotation.images.disptype=thump; ag_annotation.images.md_id=1; ag_annotation.images.mv_id=3; ag_annotation.images.mr_id=2; ag_annotation.images.version=%7B%221%22%3A%224.0%22%7D; ag_annotation.images.ci_id=1; ag_annotation.images.cb_id=4; ag_annotation.images.bul_id=3; ag_annotation.images.bul_name=FMA%203.0%20is_a; ag_annotation.images.butc_num=80457; ag_annotation.images.type=3; ag_annotation.images.types=%7B%224.3%22%3A3%2C%224.0%22%3A3%2C%225.0brain%22%3A3%7D|;

	$FORM{f_id} = qq|FMA15743|;
	$FORM{version} = qq|4.0|;
	$FORM{bul_id} = qq|4|;
	$FORM{cb_id} = qq|4|;
	$FORM{ci_id} = qq|1|;
	$FORM{md_id} = qq|1|;
	$FORM{mr_id} = qq|2|;
	$FORM{mv_id} = qq|3|;
}

#&decodeForm(\%FORM);
#delete $FORM{_formdata} if(exists($FORM{_formdata}));

#&getCookie(\%COOKIE);

my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);

my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
open(LOG,"> $FindBin::Bin/logs/$COOKIE{'ag_annotation.session'}.$cgi_name.txt");
print LOG "\n[$logtime]:$0\n";
foreach my $key (sort keys(%FORM)){
	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
}
foreach my $key (sort keys(%COOKIE)){
	print LOG __LINE__,":\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
}

$FORM{lng} = $COOKIE{"ag_annotation.locale"} if(!exists($FORM{lng}) && exists($COOKIE{"ag_annotation.locale"})); #とりあえず
$FORM{lng} = "en" if(!exists($FORM{lng}));

&setDefParams(\%FORM,\%COOKIE);

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);

my $wt_version = '';;
if(exists $FORM{tg_id} && defined $FORM{tg_id} && exists $FORM{tgi_id} && defined $FORM{tgi_id}){
	$wt_version = qq|tg_id=$FORM{tg_id} and tgi_id=$FORM{tgi_id} and|;
}elsif(exists $FORM{ci_id} && defined $FORM{ci_id} && exists $FORM{cb_id} && defined $FORM{cb_id}){
	$wt_version = qq|tg_id=$FORM{ci_id} and tgi_id=$FORM{cb_id} and|;
}
print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $TREE = {
	"data"  => [],
	"total" => 0
};

if(!exists($FORM{f_id})){
#	print to_json($TREE);
	print encode_json($TREE);
#	print LOG __LINE__,":",to_json($TREE),"\n";
	print LOG __LINE__,":",&JSON::XS::encode_json($TREE),"\n";
	close(LOG);
	exit;
}

=pod
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
$cache_path .= qq|/conventional_root|;
unless(-e $cache_path){
	mkdir $cache_path;
	chmod 0777,$cache_path;
}
$cache_path .= qq|/$FORM{lng}|;
unless(-e $cache_path){
	mkdir $cache_path;
	chmod 0777,$cache_path;
}
=cut
my $cache_path = &getCachePath(\%FORM,$cgi_name);
unless(-e $cache_path){
	my $old = umask();
	&File::Path::make_path($cache_path,{mode=>0777});
	umask($old)
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
=pod
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

my $sth_parent = $dbh->prepare(qq|select tree.f_pid from tree where $wt_version tree.f_id=? and tree.t_type=1 group by tree.f_pid|);

my @ROUTE = ();
sub getParentTree {
	my $f_id = shift;
	my $route = shift;

	unless(defined $route){
		$route = $f_id;
	}else{
		$route .= qq|\t$f_id|;
	}

	my $exists_flag = 0;
	my @CHK = split(/\t/,$route);
	pop @CHK;
	for(my $i=0;$i<=$#CHK;$i++){
		next if($CHK[$i] ne $f_id);
		$exists_flag = 1;
		last;
	}

	my $f_id2 = $f_id;
#	$f_id2 =~ s/\D+$//g if($f_id2 =~ /^(?:FMA|BP)/);

	my @F_PID = ();
	unless($exists_flag){
		$sth_parent->execute($f_id2);
		if($sth_parent->rows>0){
			my $f_pid;
			my $column_number = 0;
			$sth_parent->bind_col(++$column_number, \$f_pid, undef);
			while($sth_parent->fetch){
				push(@F_PID,$f_pid);
			}
		}
		$sth_parent->finish;
	}
	if(scalar @F_PID > 0){
		foreach my $f_pid (@F_PID){
			&getParentTree($f_pid,$route);
			last if($#ROUTE>10);
		}
	}else{
		push(@ROUTE,$route) unless($exists_flag);
	}
}

&getParentTree($FORM{f_id});
@ROUTE = sort {scalar (split(/\t/,$a)) <=> scalar (split(/\t/,$b)) } sort @ROUTE;
$#ROUTE = 10 if($#ROUTE>10);
foreach my $route (@ROUTE){
	push(@{$TREE->{data}},{}) if(scalar @ROUTE>1);
	my @FIDS = split(/\t/,$route);
	foreach my $f_id (@FIDS){
		push(@{$TREE->{data}},&getFMA($dbh,\%FORM,$f_id));
	}
}

$TREE->{total} = scalar @{$TREE->{data}};

#my $json = to_json($TREE);
my $json = &JSON::XS::encode_json($TREE);
#$json =~ s/"(true|false)"/$1/mg;

print $json;
print LOG __LINE__,":",$json,"\n";

open(OUT,"> $cache_file");
print OUT $json;
close(OUT);

close(LOG);

rmdir($cache_lock);

exit;
