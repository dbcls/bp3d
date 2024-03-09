#!/bp3d/local/perl/bin/perl

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
	say STDERR qq|$0 model_id model_version_id model_revision_id| ;
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
if(scalar @ARGV < 3){
	&error();
}

$md_id = $ARGV[0];
$mv_id = $ARGV[1];
$mr_id = $ARGV[2];

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

open(my $OUT,"> $log_file") or die "$! [$log_file]";
select($OUT);
$| = 1;
binmode($OUT,':utf8');


my %FORM;
$FORM{'md_id'} = $md_id-0;
$FORM{'mv_id'} = $mv_id-0;
$FORM{'mr_id'} = $mr_id-0;
$FORM{'ci_id'} = $ci_id-0;
$FORM{'cb_id'} = $cb_id-0;

#say &cgi_lib::common::encodeJSON(\%FORM,1);
#exit;

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

my $rows = scalar keys(%CDI_NAMES);
foreach my $cdi_name (sort keys(%CDI_NAMES)){
#	print STDERR sprintf("\r[%7d]:[%-10s]:",$rows,$cdi_name);
	my $num = 0;
	my %ART_IDS;
	my $art_files = &BITS::ArtFile::get_art_file(dbh=>$dbh,md_id=>$md_id,mv_id=>$mv_id,mr_id=>$mr_id,ci_id=>$ci_id,cb_id=>$cb_id,cdi_name=>$cdi_name);
	if(defined $art_files && ref $art_files eq 'ARRAY'){
		$ART_IDS{$_->{'art_id'}} = undef for(@$art_files);

		$num = scalar keys(%ART_IDS);
		say $cdi_name."\t".$num."\t".join(',',sort keys(%ART_IDS));
	}

#	foreach my $bul_id (sort keys(%{$CDI_NAMES{$cdi_name}})){
#		my $art_files = &get_art_file(dbh=>$dbh,md_id=>$md_id,mv_id=>$mv_id,mr_id=>$mr_id,ci_id=>$ci_id,cb_id=>$cb_id,cdi_name=>$cdi_name,bul_id=>$bul_id);
#		if(defined $art_files && ref $art_files eq 'ARRAY'){
#			$ART_IDS{$_->{'art_id'}} = undef for(@$art_files);
#		}
#	}
#	$num = scalar keys(%ART_IDS);
#	say $cdi_name."\t".$rows."\t".join(',',sort keys(%ART_IDS));

	print STDERR sprintf("\r[%7d]:[%-10s]:[%5d]",$rows,$cdi_name,$num);
#	print STDERR sprintf("[%5d]",$num);
	$rows--;
}
print STDERR "\n";

close($OUT);
exit;
=pod
sub _get_but_cids {
	my %arg = @_;
	my $dbh   = $arg{'dbh'};
	my $ci_id = $arg{'ci_id'};
	my $cb_id = $arg{'cb_id'};
	my $bul_id = $arg{'bul_id'};
	my $cdi_id = $arg{'cdi_id'};
	my $cdi_name = $arg{'cdi_name'};

	my $fmt = qq|select cdi_id,but_cids from %s where but_delcause is null and ci_id=$ci_id and cb_id=$cb_id and |;
	$fmt .= qq|bul_id=$bul_id and | if(defined $bul_id);
	if(defined $cdi_id || defined $cdi_name){
		$fmt .= qq|%s = ?|;
	}else{
		$fmt .= qq|cdi_pid is null|;
	}
#	if(DEBUG){
#		print STDERR __LINE__.':'.__PACKAGE__.":get_but_cids():\t\$fmt=[$fmt]\n";
#	}
	my $sth;
	my $but_cids;
	my $hash;
	if(defined $cdi_id){
		$sth = $dbh->prepare(sprintf($fmt,'buildup_tree','cdi_id')) or die $dbh->errstr;
		$sth->execute($cdi_id) or die $dbh->errstr;
	}elsif(defined $cdi_name){
		$sth = $dbh->prepare(sprintf($fmt,'view_buildup_tree','cdi_name')) or die $dbh->errstr;
		$sth->execute($cdi_name) or die $dbh->errstr;
	}else{
		$sth = $dbh->prepare(sprintf($fmt,'buildup_tree')) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
	}
	if(defined $sth){
		while(my $row = $sth->fetchrow_hashref){
			$cdi_id = $row->{'cdi_id'} if(!defined $cdi_id && defined $row->{'cdi_id'});
			next unless(defined $row->{'but_cids'});
			$hash->{$_} = undef for(@{&JSON::XS::decode_json($row->{'but_cids'})});
		}
		$sth->finish;
		undef $sth;
#		push(@$but_cids,keys(%$hash)) if(defined $hash);

		unless(defined $bul_id){
			if(defined $but_cids){
				$sth = $dbh->prepare(qq|select but_cids from buildup_tree where but_delcause is null and ci_id=$ci_id and cb_id=$cb_id and cdi_id=? and but_cids is not null|) or die $dbh->errstr;
				foreach my $cid (@$but_cids){
					$sth->execute($cid) or die $dbh->errstr;
					while(my $row = $sth->fetchrow_hashref){
						next unless(defined $row->{'but_cids'});
						$hash->{$_} = undef for(@{&JSON::XS::decode_json($row->{'but_cids'})});
					}
					$sth->finish;
				}
				undef $sth;
				undef $but_cids;
#				push(@$but_cids,keys(%$hash)) if(defined $hash);
			}
		}

		push(@$but_cids,keys(%$hash)) if(defined $hash);
	}
	return ($but_cids,$cdi_id);
}

sub get_art_file {
	my %arg = @_;
	my $dbh   = $arg{'dbh'};
	my $ci_id = $arg{'ci_id'};
	my $cb_id = $arg{'cb_id'};
	my $bul_id = $arg{'bul_id'};
	my $md_id = $arg{'md_id'};
	my $mv_id = $arg{'mv_id'};
	my $mr_id = $arg{'mr_id'};
	my $cdi_id = $arg{'cdi_id'};
	my $cdi_name = $arg{'cdi_name'};

	if(DEBUG){
		print STDERR __LINE__.':'.__PACKAGE__.":get_art_file():START\n";
		print STDERR __LINE__.':'.__PACKAGE__.":get_art_file():\t\$ci_id=[$ci_id]\n"       if(defined $ci_id);
		print STDERR __LINE__.':'.__PACKAGE__.":get_art_file():\t\$cb_id=[$cb_id]\n"       if(defined $cb_id);
		print STDERR __LINE__.':'.__PACKAGE__.":get_art_file():\t\$bul_id=[$bul_id]\n"     if(defined $bul_id);
		print STDERR __LINE__.':'.__PACKAGE__.":get_art_file():\t\$md_id=[$md_id]\n"       if(defined $md_id);
		print STDERR __LINE__.':'.__PACKAGE__.":get_art_file():\t\$mv_id=[$mv_id]\n"       if(defined $mv_id);
		print STDERR __LINE__.':'.__PACKAGE__.":get_art_file():\t\$mr_id=[$mr_id]\n"       if(defined $cdi_id);
		print STDERR __LINE__.':'.__PACKAGE__.":get_art_file():\t\$cdi_id=[$cdi_id]\n"     if(defined $mr_id);
		print STDERR __LINE__.':'.__PACKAGE__.":get_art_file():\t\$cdi_name=[$cdi_name]\n" if(defined $cdi_name);
	}

	my($art_id,$art_ext,$hist_serial);
	my $rows;
	my $but_cids;
	($but_cids,$cdi_id) = &_get_but_cids(dbh=>$dbh,ci_id=>$ci_id,cb_id=>$cb_id,cdi_id=>$cdi_id,cdi_name=>$cdi_name,bul_id=>$bul_id);
	if(defined $but_cids && ref $but_cids eq 'ARRAY'){
		my %HASH = map {$_=>undef} @$but_cids;
		foreach my $but_cid (@$but_cids){
			my($t_but_cids,$t_cdi_id) = &_get_but_cids(dbh=>$dbh,ci_id=>$ci_id,cb_id=>$cb_id,cdi_id=>$but_cid);
			if(defined $t_but_cids && ref $t_but_cids eq 'ARRAY'){
				$HASH{$_} = undef for(@$t_but_cids);
			}
			$HASH{$t_cdi_id} = undef if(defined $t_cdi_id)
		}
		$but_cids = [keys(%HASH)];
	}

	if(DEBUG){
		print STDERR __LINE__.':'.__PACKAGE__.":get_art_file():\t\$cdi_id=[$cdi_id]\n";
		print STDERR __LINE__.':'.__PACKAGE__.":get_art_file():\t\$but_cids=[$but_cids]\n";
	}
	push(@$but_cids,$cdi_id) if(defined $cdi_id);
	if(defined $but_cids){
		my $fmt =<<SQL;
select
 art_id,
 art_ext,
 hist_serial
from
 history_art_file
where
 (art_id,hist_serial) in (
     select
      art_id,art_hist_serial
     from
      concept_art_map
     where
      cm_id in (
          select
           cm_id
          from
           concept_art_map
          where
           cm_use and
           cm_delcause is null and
           (md_id,mv_id,mr_id,cdi_id) in (
               select
                md_id,mv_id,max(mr_id) as mr_id,cdi_id
               from
                concept_art_map
               where
                md_id=$md_id and mv_id=$mv_id and mr_id<=$mr_id and cdi_id in (%s)
               group by
                md_id,mv_id,cdi_id
            )
      )
     group by
      art_id,art_hist_serial
 )

SQL
		my $sth = $dbh->prepare(sprintf($fmt,join(',',@$but_cids))) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$art_id, undef);
		$sth->bind_col(++$column_number, \$art_ext, undef);
		$sth->bind_col(++$column_number, \$hist_serial, undef);
		while($sth->fetch){
			push(@$rows,{
				art_id => $art_id,
				art_ext => $art_ext,
				hist_serial => $hist_serial,
			});
		}
		$sth->finish;
		undef $sth;
	}

	print STDERR __LINE__.':'.__PACKAGE__.":get_art_file():END\n" if(DEBUG);

	return defined $rows ? (wantarray ? @$rows : $rows) : undef;
}
=cut
