#!/bp3d/local/perl/bin/perl

#
# check_cm_use_obj.plを使用して生成されたファイルを対象とする
# コマンドラインでの再計算する為、batch-recalculation.plを実行する為のパラメータファイルを生成
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
	say STDERR qq|$0 model_id model_version_id model_revision_id check_cm_use_obj_result_file| ;
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
my $check_cm_use_obj_result_file = $ARGV[3];
unless(-e $check_cm_use_obj_result_file && -f $check_cm_use_obj_result_file && -s $check_cm_use_obj_result_file){
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

use BITS::ArtFile;

my @extlist = qw|.pl|;
my($name,$dir,$ext) = &File::Basename::fileparse($0,@extlist);
my $log_file = &catfile($dir,sprintf('%s_%s_%s_%s_%s.txt',$name,$ENV{'AG_DB_HOST'},$ENV{'AG_DB_PORT'},$mr_version,$mv_name_e));
my $json_file = &catfile($dir,sprintf('%s_%s_%s_%s_%s.json',$name,$ENV{'AG_DB_HOST'},$ENV{'AG_DB_PORT'},$mr_version,$mv_name_e));

open(my $OUT_TXT,"> $log_file") or die "$! [$log_file]";
select($OUT_TXT);
$| = 1;
binmode($OUT_TXT,':utf8');
select(STDOUT);


my %FORM;
$FORM{'md_id'} = $md_id-0;
$FORM{'mv_id'} = $mv_id-0;
$FORM{'mr_id'} = $mr_id-0;
$FORM{'ci_id'} = $ci_id-0;
$FORM{'cb_id'} = $cb_id-0;

my %RESULT_CDI;
open(my $IN, $check_cm_use_obj_result_file) or die "$! [$check_cm_use_obj_result_file]";
while(<$IN>){
	chomp;
	my($cdi_name,$obj_num,$objs) = split(/\t/);
#	$RESULT_CDI{$cdi_name} = [split(/,/,$objs)];
	$RESULT_CDI{$cdi_name} = $objs;
}
close($IN);

my %CDI_NAMES;
my $cdi_name;
my $bul_id;
my $sql = 'select cdi_name from view_buildup_tree where ci_id=? and cb_id=? group by cdi_name';
my $sth = $dbh->prepare($sql) or die $dbh->errstr;
$sth->execute($FORM{'ci_id'},$FORM{'cb_id'}) or die $dbh->errstr;
my $column_number = 0;
$sth->bind_col(++$column_number, \$cdi_name, undef);
while($sth->fetch){
	next unless(defined $cdi_name);
	$CDI_NAMES{$cdi_name} = undef;
}
$sth->finish;
undef $sth;

my $sql_bul = 'select cdi_id,bul_id,max(but_depth) from view_buildup_tree where but_delcause is null and ci_id=? and cb_id=? and cdi_name=? group by cdi_id,bul_id';
my $sth_bul = $dbh->prepare($sql_bul) or die $dbh->errstr;

my $sql_rep = 'select rep_id from representation where (ci_id,cb_id,md_id,mv_id,mr_id,bul_id,cdi_id) in (select ci_id,cb_id,md_id,mv_id,max(mr_id),bul_id,cdi_id from representation where ci_id=? and cb_id=? and md_id=? and mv_id=? and mr_id<=? and bul_id=? and cdi_id=? group by ci_id,cb_id,md_id,mv_id,bul_id,cdi_id)';
my $sth_rep = $dbh->prepare($sql_rep) or die $dbh->errstr;

my @OUT_DATAS = ();
my $rows = scalar keys(%CDI_NAMES);
foreach my $cdi_name (sort keys(%CDI_NAMES)){
	my $num = 0;
	my %ART_IDS;
	my $art_files = &BITS::ArtFile::get_art_file(dbh=>$dbh,md_id=>$md_id,mv_id=>$mv_id,mr_id=>$mr_id,ci_id=>$ci_id,cb_id=>$cb_id,cdi_name=>$cdi_name);
	if(defined $art_files && ref $art_files eq 'ARRAY'){
		$ART_IDS{$_->{'art_id'}} = undef for(@$art_files);
		$num = scalar keys(%ART_IDS);
		my $art_ids = join(',',sort keys(%ART_IDS));

		unless(exists $RESULT_CDI{$cdi_name} && $RESULT_CDI{$cdi_name} eq $art_ids){

			my @REP_IDS;
			my $cdi_id;
			my $bul_id;
			my $but_depth;
			$sth_bul->execute($FORM{'ci_id'},$FORM{'cb_id'},$cdi_name) or die $dbh->errstr;
			$column_number = 0;
			$sth_bul->bind_col(++$column_number, \$cdi_id, undef);
			$sth_bul->bind_col(++$column_number, \$bul_id, undef);
			$sth_bul->bind_col(++$column_number, \$but_depth, undef);
			while($sth_bul->fetch){
				next unless(defined $cdi_id && defined $bul_id);

				my $b_art_files = &BITS::ArtFile::get_art_file(dbh=>$dbh,md_id=>$md_id,mv_id=>$mv_id,mr_id=>$mr_id,ci_id=>$ci_id,cb_id=>$cb_id,cdi_name=>$cdi_name,,bul_id=>$bul_id);
				next unless(defined $b_art_files && ref $b_art_files eq 'ARRAY' && scalar @$b_art_files);

				my $rep_id;
				$sth_rep->execute($FORM{'ci_id'},$FORM{'cb_id'},$FORM{'md_id'},$FORM{'mv_id'},$FORM{'mr_id'},$bul_id,$cdi_id) or die $dbh->errstr;
				$column_number = 0;
				$sth_rep->bind_col(++$column_number, \$rep_id, undef);
				$sth_rep->fetch;
				$sth_rep->finish;

				my $HASH = {
					'ci_id'     => $ci_id+0,
					'cb_id'     => $cb_id+0,
					'md_id'     => $md_id+0,
					'mv_id'     => $mv_id+0,
					'mr_id'     => $mr_id+0,
					'cdi_id'    => $cdi_id + 0,
					'bul_id'    => $bul_id + 0,
					'rep_id'    => $rep_id,
					'but_depth' => $but_depth+0
				};
				push(@OUT_DATAS,$HASH);

				push(@REP_IDS,$rep_id) if(defined $rep_id);
			}
			$sth_bul->finish;

			say $OUT_TXT (exists $RESULT_CDI{$cdi_name} ? 'U' : 'N')."\t".join(',',sort @REP_IDS)."\t".$cdi_name."\t".$num."\t".$art_ids;
		}

	}
	print STDERR sprintf("\r[%7d]:[%-10s]:[%5d]",$rows,$cdi_name,$num);
#	print STDERR sprintf("[%7d]:[%-10s]:[%5d]\n",$rows,$cdi_name,$num);
	$rows--;
}
print STDERR "\n";

close($OUT_TXT);

if(scalar @OUT_DATAS){
	@OUT_DATAS = sort {$a->{'bul_id'} <=> $b->{'bul_id'}} sort {$b->{'but_depth'} <=> $a->{'but_depth'}} @OUT_DATAS;
	my $DATAS = {
		'ci_id'     => $ci_id+0,
		'cb_id'     => $cb_id+0,
		'md_id'     => $md_id+0,
		'mv_id'     => $mv_id+0,
		'mr_id'     => $mr_id+0,
		'all_datas' => &JSON::XS::encode_json(\@OUT_DATAS)
	};
	open(my $OUT_JSON,"> $json_file") or die "$! [$json_file]";
	print $OUT_JSON $JSONXS->encode($DATAS);
	close($OUT_JSON);
}elsif(-e $json_file){
	unlink $json_file;
}

undef $sth_bul;
undef $sth_rep
