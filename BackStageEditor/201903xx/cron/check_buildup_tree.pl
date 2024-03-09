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

my %HASH;
my $cdi_name;
my $cdi_pname;
my $bul_id;
my $sql = 'select cdi_name,cdi_pname,bul_id from view_buildup_tree where ci_id=? and cb_id=? and cdi_pid is not null';
my $sth = $dbh->prepare($sql) or die $dbh->errstr;
$sth->execute($FORM{'ci_id'},$FORM{'cb_id'}) or die $dbh->errstr;
my $column_number = 0;
$sth->bind_col(++$column_number, \$cdi_name, undef);
$sth->bind_col(++$column_number, \$cdi_pname, undef);
$sth->bind_col(++$column_number, \$bul_id, undef);
while($sth->fetch){
	next unless(defined $bul_id && defined $cdi_pname && defined $cdi_name);
	$HASH{$bul_id}->{$cdi_pname}->{$cdi_name} = undef;
}
$sth->finish;
undef $sth;

foreach $bul_id (sort {$a <=> $b} keys(%HASH)){
	foreach $cdi_pname (keys(%{$HASH{$bul_id}})){
		foreach $cdi_name (keys(%{$HASH{$bul_id}->{$cdi_pname}})){
			say qq|$bul_id,$cdi_name,$cdi_pname| if(exists $HASH{$bul_id}->{$cdi_name}->{$cdi_pname});
		}
	}
}
