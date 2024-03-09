#!/bp3d/local/perl/bin/perl

#
# make_recalculation_param_file.plを使用して生成されたテキストファイルを対象とする
# 再生成対応のサムネイルファイルを削除する
#

$| = 1;
select(STDERR);
$| = 1;
select(STDOUT);

use strict;
use warnings;
use feature ':5.10';

use File::Basename;
use File::Spec::Functions qw(abs2rel rel2abs catdir catfile devnull);
use File::Path;
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

use JSON::XS;
my $JSONXS = JSON::XS->new->utf8->indent(1)->canonical(1);

use constant {
	DEBUG=>0
};

use FindBin;
my $htdocs_path;
BEGIN{
	use FindBin;
#	$htdocs_path = qq|$FindBin::Bin/../htdocs_130910|;
	$htdocs_path = qq|$FindBin::Bin/../htdocs| unless(defined $htdocs_path && -e $htdocs_path);
#	print __LINE__,":BEGIN2!!\n";
}
use lib $FindBin::Bin,$htdocs_path,qq|$htdocs_path/../cgi_lib|;
use cgi_lib::common;


use Getopt::Long qw(:config posix_default no_ignore_case gnu_compat);
my $config = {
	host => '127.0.0.1',
	port => '8543'
};
&Getopt::Long::GetOptions($config,qw/
	host|h=s
	port|p=s
/) or exit 1;

$ENV{'AG_DB_HOST'} = $config->{'host'};
$ENV{'AG_DB_PORT'} = $config->{'port'};
#say &cgi_lib::common::encodeJSON(\%ENV,1);
#exit;

require "webgl_common.pl";
my $dbh = &get_dbh();

my $md_id;
my $mv_id;
my $mr_id;
sub error {
	say STDERR qq|$0 model_id model_version_id model_revision_id make_recalculation_param_file_result_text_file| ;
	say STDERR qq|#optins :| ;
	say STDERR qq|# --host,-h : database host [default:$config->{'host'}]| ;
	say STDERR qq|# --port,-p : database port [default:$config->{'port'}]| ;
	say STDERR qq|#model_id:model_version_id:model_revision_id:| ;
	my $sql=qq|select mr.md_id,mr.mv_id,mr.mr_id,mr.mr_version,mv_name_e from model_revision as mr left join (select * from model_version) mv on (mv.md_id=mr.md_id and mv.mv_id=mr.mv_id) order by mr.md_id,mr.mv_id,mr.mr_id|;
	my $mr_version;
	my $mv_name_e;
	my $sth = $dbh->prepare($sql);
	$sth->execute();
	$sth->bind_col(1, \$md_id, undef);
	$sth->bind_col(2, \$mv_id, undef);
	$sth->bind_col(3, \$mr_id, undef);
	$sth->bind_col(4, \$mr_version, undef);
	$sth->bind_col(5, \$mv_name_e, undef);
	while($sth->fetch){
		say STDERR sprintf("      %2d :             %2d :              %2d : %-14s : %s",$md_id,$mv_id,$mr_id,$mr_version,$mv_name_e);
	}
	$sth->finish;
	undef $sth;
	exit 1;
}
if(scalar @ARGV < 4){
	&error();
}

$md_id = $ARGV[0];
$mv_id = $ARGV[1];
$mr_id = $ARGV[2];
my $make_recalculation_param_file_result_text_file = $ARGV[3];
unless(-e $make_recalculation_param_file_result_text_file && -f $make_recalculation_param_file_result_text_file && -s $make_recalculation_param_file_result_text_file){
	&error();
}

my $ci_id;
my $cb_id;
{
	my $sql=qq|select ci_id,cb_id from model_version where md_id=? and mv_id=?|;
	my $sth = $dbh->prepare($sql);
	$sth->execute($md_id,$mv_id);
	$sth->bind_col(1, \$ci_id, undef);
	$sth->bind_col(2, \$cb_id, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;
}

my $mr_version;
my $mv_name_e;
{
	my $sql=qq|select mr.mr_version,mv_name_e from model_revision as mr left join (select * from model_version) mv on (mv.md_id=mr.md_id and mv.mv_id=mr.mv_id) where mr.md_id=? and mr.mv_id=? and mr.mr_id=? order by mr.md_id,mr.mv_id,mr.mr_id|;
	my $sth = $dbh->prepare($sql);
	$sth->execute($md_id,$mv_id,$mr_id);
	$sth->bind_col(1, \$mr_version, undef);
	$sth->bind_col(2, \$mv_name_e, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;
}

unless(defined $ci_id && defined $cb_id && defined $mr_version && defined $mv_name_e){
	&error();
}

my %RESULT_CDI;
open(my $IN, $make_recalculation_param_file_result_text_file) or die "$! [$make_recalculation_param_file_result_text_file]";
while(<$IN>){
	chomp;
	my($status,$rep_ids,$cdi_name,$obj_num,$objs) = split(/\t/);
	if($status eq 'U' && length $rep_ids){
		$RESULT_CDI{$cdi_name} = $objs;
	}elsif($status eq 'U'){
		say STDERR "Unknown rep_id [$status][$rep_ids][$cdi_name]";
		$RESULT_CDI{$cdi_name} = $objs;
	}elsif(length $rep_ids){
		say STDERR "Unknown Stats [$status][$rep_ids][$cdi_name]";
		$RESULT_CDI{$cdi_name} = $objs;
	}
}
close($IN);

foreach my $cdi_name (sort keys(%RESULT_CDI)){
	my($img_prefix,$img_path) = &getCmImagePrefix($mr_version,undef,$cdi_name);
	next unless(-e $img_path && -d $img_path);
	say STDERR "[$cdi_name]";#[$img_prefix,$img_path]";
	foreach (glob "${img_prefix}*"){
		say STDERR "\tunlink $_";
		unlink $_ ;
	}
}

exit;
