#!/bp3d/local/perl/bin/perl

use strict;
use warnings;
use feature ':5.10';

use Parallel::ForkManager;
use Time::Piece;
use File::Spec::Functions qw(catdir catfile);
use Clone;
use Sys::CPU;
use Cwd;
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'API'),&Cwd::abs_path(&catdir($FindBin::Bin,'..','..','ag-common','lib'));
use cgi_lib::common;

require "common.pl";
require "common_db.pl";

my $max_procs = &Sys::CPU::cpu_count();

my $dbh = &get_dbh();
my $ci_id;
my $cb_id;

sub print_error {
	warn qq|#concept_info_id:concept_build_id:\n| ;
	my $sql=<<SQL;
select info.ci_id,cb_id,ci_name,cb_name,cb_release,cb_comment from concept_build
left join (select ci_id,ci_name from concept_info where ci_delcause IS NULL) as info on (concept_build.ci_id=info.ci_id)
where cb_delcause IS NULL and cb_use
order by cb_release,info.ci_id,cb_id;
SQL
	my $ci_name;
	my $cb_name;
	my $cb_release;
	my $cb_comment;
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$sth->bind_col(1, \$ci_id, undef);
	$sth->bind_col(2, \$cb_id, undef);
	$sth->bind_col(3, \$ci_name, undef);
	$sth->bind_col(4, \$cb_name, undef);
	$sth->bind_col(5, \$cb_release, undef);
	$sth->bind_col(6, \$cb_comment, undef);
	while($sth->fetch){
		say STDERR sprintf("              %-2s:              %-2s: %-5s: %-13s: %-10s : %s",$ci_id,$cb_id,$ci_name,$cb_name,$cb_release,$cb_comment // '');
	}
	$sth->finish;
	undef $sth;
	exit 1;
}

$SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit";
sub sigexit {
	my $t = localtime;
	my $date = $t->cdate;
	print STDERR qq|[$date] KILL THIS CGI!![|.(exists $ENV{SCRIPT_NAME} ? $ENV{SCRIPT_NAME} : $0) . qq|]\n|;
	exit(1);
}


my $sql;
my $sth;
my $cdi_name;
#my $bul_id;
my @FMAS;



$sql = qq|
select
 ci_id,
 cb_id,
 cdi_name
from
 view_buildup_tree as but
where
 but_delcause is null and (ci_id,cb_id) in (
  select ci_id,cb_id from concept_build where cb_delcause is null and cb_use group by ci_id,cb_id
)
group by
 but.ci_id,
 but.cb_id,
 cdi_name
order by
 but.ci_id desc,
 but.cb_id desc,
 cdi_name
|;
$sth = $dbh->prepare($sql) or die $dbh->errstr;
$sth->execute() or die $dbh->errstr;
$sth->bind_col(1, \$ci_id, undef);
$sth->bind_col(2, \$cb_id, undef);
$sth->bind_col(3, \$cdi_name, undef);
#$sth->bind_col(4, \$bul_id, undef);
while($sth->fetch){
	push @FMAS, {
		ci_id => $ci_id,
		cb_id => $cb_id,
		cdi_name => $cdi_name,
#		bul_id => $bul_id,
	};
}
$sth->finish;
undef $sth;


my $pm = new Parallel::ForkManager($max_procs);
$pm->run_on_finish(
	sub {
		my ($pid, $exit_code, $ident) = @_;
		if($exit_code){
			say STDERR qq|** $ident just got out of the pool with PID $pid and exit code: $exit_code|;
			exit 1;
		}
	}
);

my $cgi_name = 'get-fmastratum';

my $prog = &catfile($FindBin::Bin, qq|$cgi_name.cgi|);
my $cgi_utime = (stat($prog))[9]+1;

my $total = (scalar @FMAS) * 2;
my $num = $total;
foreach my $fma (@FMAS){
	foreach my $lng (qw/ja en/){
		$num--;

		my $form = &Clone::clone($fma);
		$form->{'lng'} = $lng;
		$form->{'bul_id'} = undef;

#		my $cmd = qq|$prog ci_id=$fma->{ci_id} cb_id=$fma->{cb_id} bul_id=$fma->{bul_id} lng=$lng f_id=$fma->{cdi_name} 1>/dev/null|;
		my $cmd = qq|$prog ci_id=$form->{ci_id} cb_id=$form->{cb_id} lng=$form->{lng} f_id=$form->{cdi_name} 1>/dev/null|;
		say STDERR qq|[$num/$total] $cmd|;

		my $cache_path = &getCachePath($form,$cgi_name);
		$cache_path = &catdir($cache_path,&getBaseDirFromID($form->{cdi_name}));
		my $cache_file = &catfile($cache_path,qq|$form->{cdi_name}.txt|);
		if(-e $cache_file && -f $cache_file && -s $cache_file){
			utime($cgi_utime, $cgi_utime, $cache_file) if((stat($cache_file))[9] < $cgi_utime);
			next;
		}else{
#			say $cache_file;
#			exit;
		}

		$pm->start and next;
		system($cmd);
		if ($? == -1) {
			say STDERR qq|failed to execute: $!|;
			$pm->finish($?);
		}
		elsif ($? & 127) {
			say STDERR sprintf(qq|child died with signal %d, %s coredump|, ($? & 127),  ($? & 128) ? 'with' : 'without');
			$pm->finish($?);
		}
		elsif ($? >> 8) {
			say STDERR sprintf(qq|child exited with value %d|, $? >> 8);
			$pm->finish($?);
		}
		else{
			$pm->finish;
		}
	}
}
$pm->wait_all_children;
