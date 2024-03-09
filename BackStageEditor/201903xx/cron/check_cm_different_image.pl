#!/bp3d/local/perl/bin/perl

$ENV{'AG_DB_HOST'} = '127.0.0.1';
$ENV{'AG_DB_PORT'} = '8543';

$| = 1;
select(STDERR);
$| = 1;
select(STDOUT);

use strict;
use warnings;
use feature ':5.10';

use File::Basename;
use File::Spec::Functions;
use File::Path;
use JSON::XS;
use Cwd qw(abs_path);
use Hash::Merge qw( merge );
Hash::Merge::set_behavior('LEFT_PRECEDENT');
use File::Path;
use File::Copy;
use List::Util;
use Math::Round;
use POSIX qw( floor :sys_wait_h);
use DBD::Pg;
use Image::Info;
use Time::HiRes qw/gettimeofday tv_interval/;
use Encode;
use Sys::CPU;
use Time::Piece;

use Data::Dumper;
$Data::Dumper::Indent = 1;
$Data::Dumper::Sortkeys = 1;

use FindBin;
my $htdocs_path;
BEGIN{
	use FindBin;
#	$htdocs_path = qq|$FindBin::Bin/../htdocs_130910|;
	$htdocs_path = qq|$FindBin::Bin/../htdocs| unless(defined $htdocs_path && -e $htdocs_path);
	print __LINE__,":BEGIN2!!\n";
}
use lib $FindBin::Bin,$htdocs_path,qq|$htdocs_path/../cgi_lib|;

require "webgl_common.pl";
use cgi_lib::common;
my $dbh = &get_dbh();

my %FORM;
$FORM{'md_id'} = 1;
#$FORM{'mv_id'} = 12;
$FORM{'mv_id'} = 13;
$FORM{'mr_id'} = 1;
$FORM{'ci_id'} = 1;
$FORM{'cb_id'} = 9;

say &cgi_lib::common::encodeJSON(\%FORM,1);

my %FMA20394;
my $cdi_id;
my $but_cids;
my $sql = 'select cdi_id,but_cids from view_buildup_tree where ci_id=? and cb_id=? and cdi_name=? and bul_id=? order by cdi_id,bul_id';
my $sth = $dbh->prepare($sql) or die $dbh->errstr;
$sth->execute($FORM{'ci_id'},$FORM{'cb_id'},'FMA20394',4) or die $dbh->errstr;
my $column_number = 0;
$sth->bind_col(++$column_number, \$cdi_id, undef);
$sth->bind_col(++$column_number, \$but_cids, undef);
while($sth->fetch){
	my $arr;
	if(defined $but_cids){
		$arr = &cgi_lib::common::decodeJSON($but_cids);
	}else{
		$arr = [];
	}
	push(@$arr,$cdi_id);
	%FMA20394 = map {$_=>undef} sort {$a<=>$b} @$arr;
}
$sth->finish;
undef $sth;


my %CDI_ID;
my $bul_id;
=pod
$sql = 'select cdi_id from buildup_tree where ci_id=? and cb_id=? group by cdi_id HAVING count(cdi_id)>1';
$sth = $dbh->prepare($sql) or die $dbh->errstr;
$sth->execute($FORM{'ci_id'},$FORM{'cb_id'}) or die $dbh->errstr;
$column_number = 0;
$sth->bind_col(++$column_number, \$cdi_id, undef);
while($sth->fetch){
	next unless(exists $FMA20394{$cdi_id});
	$CDI_ID{$cdi_id} = undef;
}
$sth->finish;
undef $sth;
=cut



$sql = 'select cdi_id,bul_id,but_cids from buildup_tree where ci_id=? and cb_id=? order by cdi_id,bul_id';
$sth = $dbh->prepare($sql) or die $dbh->errstr;
$sth->execute($FORM{'ci_id'},$FORM{'cb_id'}) or die $dbh->errstr;
$column_number = 0;
$sth->bind_col(++$column_number, \$cdi_id, undef);
$sth->bind_col(++$column_number, \$bul_id, undef);
$sth->bind_col(++$column_number, \$but_cids, undef);
while($sth->fetch){
#	next unless(exists $CDI_ID{$cdi_id});
#	if($bul_id==4){
#		next unless(exists $FMA20394{$cdi_id});
#	}
	if(defined $but_cids){
		$CDI_ID{$cdi_id}->{$bul_id} = &cgi_lib::common::decodeJSON($but_cids);
	}else{
		$CDI_ID{$cdi_id}->{$bul_id} = [];
	}
	push(@{$CDI_ID{$cdi_id}->{$bul_id}},$cdi_id);





	$CDI_ID{$cdi_id}->{$bul_id} = [map {$_-0} sort {$a<=>$b} @{$CDI_ID{$cdi_id}->{$bul_id}}];
#	say "$cdi_id,$bul_id,".(scalar @{$CDI_ID{$cdi_id}->{$bul_id}});
}
$sth->finish;
undef $sth;


my %CDI;
my $cdi_name;
my $cdi_name_e;
my $sql_cdi = 'select cdi_id,cdi_name,cdi_name_e from concept_data_info where ci_id=?';
my $sth_cdi = $dbh->prepare($sql_cdi) or die $dbh->errstr;
$sth_cdi->execute($FORM{'ci_id'}) or die $dbh->errstr;
$column_number = 0;
$sth_cdi->bind_col(++$column_number, \$cdi_id, undef);
$sth_cdi->bind_col(++$column_number, \$cdi_name, undef);
$sth_cdi->bind_col(++$column_number, \$cdi_name_e, undef);
while($sth_cdi->fetch){
	$CDI{$cdi_id} = {
		cdi_name => $cdi_name,
		cdi_name_e => $cdi_name_e
	};
}
$sth_cdi->finish;
undef $sth_cdi;


my %BUL;
my $bul_name_e;
my $sql_bul = 'select bul_id,bul_name_e from buildup_logic where bul_use and bul_delcause is null';
my $sth_bul = $dbh->prepare($sql_bul) or die $dbh->errstr;
$sth_bul->execute() or die $dbh->errstr;
$column_number = 0;
$sth_bul->bind_col(++$column_number, \$bul_id, undef);
$sth_bul->bind_col(++$column_number, \$bul_name_e, undef);
while($sth_bul->fetch){
	$BUL{$bul_id} = $bul_name_e;
}
$sth_bul->finish;
undef $sth_bul;



my %ART_ID;
my $art_id;
my $sql_fmt = 'select art_id from concept_art_map where cm_use and cm_delcause is null and md_id=? and mv_id=? and cdi_id in (%s) group by art_id';
foreach $cdi_id (sort {$a<=>$b} keys(%CDI_ID)){
	foreach $bul_id (sort {$a<=>$b} keys(%{$CDI_ID{$cdi_id}})){
#		$sql = sprintf($sql_fmt,join(',',map {'?'} @{$CDI_ID{$cdi_id}->{$bul_id}}));
		$sql = sprintf($sql_fmt,join(',',sort {$a<=>$b} @{$CDI_ID{$cdi_id}->{$bul_id}}));
		say STDERR $CDI{$cdi_id}->{'cdi_name'}.",$bul_id";
#		say STDERR $sql;
#		say $CDI{$cdi_id}->{'cdi_name'}.",$bul_id";
#		say $sql;
#		exit;
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
#		$sth->execute($FORM{'md_id'},$FORM{'mv_id'},@{$CDI_ID{$cdi_id}->{$bul_id}}) or die $dbh->errstr;
		$sth->execute($FORM{'md_id'},$FORM{'mv_id'}) or die $dbh->errstr;
		$column_number = 0;
		$sth->bind_col(++$column_number, \$art_id, undef);
		while($sth->fetch){
			push(@{$ART_ID{$cdi_id}->{$bul_id}},$art_id);
		}
		$sth->finish;
		undef $sth;

		next;
		print $CDI{$cdi_id}->{'cdi_name'}.",$bul_id,";
		unless(exists $ART_ID{$cdi_id} && exists $ART_ID{$cdi_id}->{$bul_id}){
			say "SKIP!!";
		}else{
			say (scalar @{$ART_ID{$cdi_id}->{$bul_id}});
		}
	}
}

foreach $cdi_id (sort {$a<=>$b} keys(%ART_ID)){
	my @bul_ids = sort {$a<=>$b} keys(%{$ART_ID{$cdi_id}});
	next unless(scalar @bul_ids == 2);
	next if(scalar @{$ART_ID{$cdi_id}->{$bul_ids[0]}} == scalar @{$ART_ID{$cdi_id}->{$bul_ids[1]}});
	say $CDI{$cdi_id}->{'cdi_name'}."\t".$CDI{$cdi_id}->{'cdi_name_e'}."\t".(scalar @{$ART_ID{$cdi_id}->{$bul_ids[0]}})."\t".(scalar @{$ART_ID{$cdi_id}->{$bul_ids[1]}});
}
