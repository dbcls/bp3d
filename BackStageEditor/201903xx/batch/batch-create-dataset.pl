#!/opt/services/ag/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use DBD::Pg;
use POSIX;
use Data::Dumper;
use Cwd qw(abs_path);
use File::Basename;
use File::Spec::Functions;
use File::Copy;
use Time::Piece;
use Digest::MD5;
use Time::HiRes;
use Clone;

use Getopt::Long qw(:config posix_default no_ignore_case gnu_compat);
my $config = {
	db   => exists $ENV{'AG_DB_NAME'} && defined $ENV{'AG_DB_NAME'} ? $ENV{'AG_DB_NAME'} : 'ag_public_1903xx',
	host => exists $ENV{'AG_DB_HOST'} && defined $ENV{'AG_DB_HOST'} ? $ENV{'AG_DB_HOST'} : '127.0.0.1',
	port => exists $ENV{'AG_DB_PORT'} && defined $ENV{'AG_DB_PORT'} ? $ENV{'AG_DB_PORT'} : '38300',
	md => 1,
	mr => 1,
	ci => 1,
	version => 5,
	revision => 3,
};
&Getopt::Long::GetOptions($config,qw/
	db|d=s
	host|h=s
	port|p=s
	md=i
	mv=i
	mr=i
	ci=i
	cb=i
	version=i
	revision=i
	name=s
	objectset=s
	order=i
	file=s
/) or exit 1;

$ENV{'AG_DB_HOST'} = $config->{'host'};
$ENV{'AG_DB_PORT'} = $config->{'port'};
$ENV{'AG_DB_NAME'} = $config->{'db'};

use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'..','cgi_lib');

require "webgl_common.pl";

my $LOG = \*STDERR;

my $dbh = &get_dbh();

my $sql;
my $sth;
my $column_number;
my $ci_id;
my $cb_id;
my $cb_name;
my $mv_id;
my $mv_order;

sub error_cb {
	my $cb_id = shift;
	if(defined $cb_id){
		say STDERR qq|Unknown cb [ $cb_id ]|;
	}
	else{
		say STDERR qq|Undefined cb|;
	}

	$sql = qq|SELECT ci_id,cb_id,cb_name FROM concept_build WHERE ci_id=? AND cb_use ORDER BY cb_order|;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute($config->{'ci'}) or die $dbh->errstr;
	$column_number = 0;
	$sth->bind_col(++$column_number, \$ci_id, undef);
	$sth->bind_col(++$column_number, \$cb_id, undef);
	$sth->bind_col(++$column_number, \$cb_name, undef);
	while($sth->fetch){
		say STDERR sprintf("\t%2d : %s",$cb_id,$cb_name);
	}
	$sth->finish;
	undef $sth;
	exit 1;
}

sub check_cb {
	unless(exists $config->{'cb'} && defined $config->{'cb'} && $config->{'cb'} =~ /^[0-9]+$/){
		&error_cb();
	}
	else{
		$sql = qq|SELECT ci_id,cb_id,cb_name FROM concept_build WHERE ci_id=? AND cb_id=? AND cb_use|;
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute($config->{'ci'},$config->{'cb'}) or die $dbh->errstr;
		my $rows = $sth->rows();
		$sth->finish;
		undef $sth;
		&error_cb($config->{'cb'}) unless($rows>0);
	}
}

sub error_mv {
	my $message = shift;
	my $mv_id = shift;
	say STDERR sprintf("%s mv [ %s ]",$message,$mv_id);
	exit 1;
}
sub check_mv {
	if(exists $config->{'mv'} && defined $config->{'mv'}){
		if($config->{'mv'} =~ /^[0-9]+$/){
			$sql = qq|SELECT mv_id FROM model_version WHERE md_id=? AND mv_id=?|;
			$sth = $dbh->prepare($sql) or die $dbh->errstr;
			$sth->execute($config->{'md'},$config->{'mv'}) or die $dbh->errstr;
			my $rows = $sth->rows();
			$sth->finish;
			undef $sth;
#			&error_mv('exists',$config->{'mv'}) if($rows>0);
			return 1 if($rows>0);
		}
		else{
			&error_mv('unknown');
		}
	}
	else{
		$sql = qq|SELECT MAX(mv_id) FROM model_version WHERE md_id=?|;
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute($config->{'md'}) or die $dbh->errstr;
		$column_number = 0;
		$sth->bind_col(++$column_number, \$mv_id, undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;
		#&cgi_lib::common::message($mv_id, $LOG);
		$mv_id = 0 unless(defined $mv_id);
		$config->{'mv'} = $mv_id+1;
	}
	return 0;
}

sub error_name {
	my $name = shift;
	if(defined $name){
		say STDERR qq|exists name [ $name ]|;
	}
	else{
		say STDERR qq|Undefined name|;
	}
	exit 1;
}

sub check_name {
	unless(exists $config->{'name'} && defined $config->{'name'} && length $config->{'name'}){
		&error_name();
	}
	else{
		$sql = qq|SELECT mv_id FROM model_version WHERE md_id=? AND mv_name_e=?|;
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute($config->{'md'},$config->{'name'}) or die $dbh->errstr;
		my $rows = $sth->rows();
		$sth->finish;
		undef $sth;
		&error_name($config->{'name'}) if($rows>0);
	}
}

sub error_objectset {
	say STDERR qq|Undefined objectset|;
	exit 1;
}

sub check_objectset {
	unless(exists $config->{'objectset'} && defined $config->{'objectset'} && length $config->{'objectset'}){
		&error_objectset();
	}
}

sub check_order {
	unless(exists $config->{'order'} && defined $config->{'order'} && $config->{'order'} =~ /^[0-9]+$/){
		$sql = qq|SELECT MAX(mv_order) FROM model_version WHERE md_id=?|;
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute($config->{'md'}) or die $dbh->errstr;
		$column_number = 0;
		$sth->bind_col(++$column_number, \$mv_order, undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;
		#&cgi_lib::common::message($mv_id, $LOG);
		$mv_order = 0 unless(defined $mv_order);
		$config->{'order'} = $mv_order+1;
	}
}

sub create_dataset {
#	$dbh->{'AutoCommit'} = 0;
#	$dbh->{'RaiseError'} = 1;
	eval{
		my $sql_cbr_sel = 'select f_potid FROM concept_build_relation WHERE cbr_use AND ci_id=? AND cb_id=?';
		my $sth_cbr_sel = $dbh->prepare($sql_cbr_sel) or die $dbh->errstr;

		my $sql_bt_ins = 'INSERT INTO buildup_tree (md_id,mv_id,mr_id,ci_id,cb_id,cdi_id,cdi_pid,bul_id,f_potids) VALUES (?,?,?,?,?,?,?,?,?)';
		my $sth_bt_ins = $dbh->prepare($sql_bt_ins) or die $dbh->errstr;

		my $sql_ct_sel = 'select cdi_id,cdi_pid,bul_id,f_potids FROM concept_tree WHERE ci_id=? AND cb_id=?';
		my $sth_ct_sel = $dbh->prepare($sql_ct_sel) or die $dbh->errstr;

		my $sql_cds_sel = sprintf(qq|
SELECT
  cds.cdi_id
 ,cds.cs_id
 ,cds.cdst_id
 ,bds.cds_id
FROM
  concept_data_synonym AS cds
LEFT JOIN
  concept_data_synonym AS cds_b ON cds_b.cds_id=cds.cds_bid
LEFT JOIN
  (SELECT * FROM buildup_data_synonym WHERE md_id=%d AND mv_id=%d AND mr_id=%d) AS bds
   ON bds.ci_id=cds_b.ci_id AND bds.cb_id=cds_b.cb_id AND bds.cdi_id=cds_b.cdi_id AND bds.cdst_id=cds_b.cdst_id
WHERE
     cds.ci_id=?
 AND cds.cb_id=?
 AND cds.cds_bid IS NOT NULL
|,$config->{'md'},$config->{'mv'},$config->{'mr'});
		my $sth_cds_sel = $dbh->prepare($sql_cds_sel) or die $dbh->errstr;

		my $sql_bds_upd = 'UPDATE buildup_data_synonym SET cds_bid=? WHERE md_id=? AND mv_id=? AND mr_id=? AND ci_id=? AND cb_id=? AND cdi_id=? AND cs_id=? AND cdst_id=?';
		my $sth_bds_upd = $dbh->prepare($sql_bds_upd) or die $dbh->errstr;


		my $sql_bti_ins_fmt = q|INSERT INTO buildup_tree_info
SELECT
 %d           AS md_id,
 %d           AS mv_id,
 %d           AS mr_id,
 ci_id,
 cb_id,
 cdi_id,
 cti_cnum     AS but_cnum,
 cti_cids     AS but_cids,
 cti_depth    AS but_depth,
 cti_pnum     AS but_pnum,
 cti_pids     AS but_pids,
 cti_delcause AS but_delcause,
 cti_entry    AS but_entry,
 cti_openid   AS but_openid,
 crl_id       AS bul_id
FROM
 concept_tree_info
WHERE
 ci_id=%d AND
 cb_id=%d
|;

		my $sql_btt_ins_fmt = q|INSERT INTO buildup_tree_trio
SELECT
 %d           AS md_id,
 %d           AS mv_id,
 %d           AS mr_id,
 ci_id,
 cb_id,
 cdi_pid,
 cdi_lid,
 cdi_rid,
 ctt_delcause,
 ctt_entry,
 ctt_openid
FROM
 concept_tree_trio
WHERE
 ci_id=%d AND
 cb_id=%d
|;

		my $sql_bd_ins_fmt = q|INSERT INTO buildup_data
SELECT
 %d           AS md_id,
 %d           AS mv_id,
 %d           AS mr_id,
 ci_id,
 cb_id,
 cdi_id,
 cd_name,
 cd_syn,
 cd_def,
 cd_delcause,
 cd_entry,
 cd_openid,
 phy_id,
 seg_id
FROM
 concept_data
WHERE
 ci_id=%d AND
 cb_id=%d
|;

		my $sql_bds_ins_fmt = q|INSERT INTO buildup_data_synonym
(md_id,mv_id,mr_id, ci_id, cb_id, cdi_id, cs_id, cdst_id, cds_added, cds_order, cds_comment, cds_delcause, cds_entry, cds_openid)
SELECT
 %d           AS md_id,
 %d           AS mv_id,
 %d           AS mr_id,
 ci_id,
 cb_id,
 cdi_id,
 cs_id,
 cdst_id,
 cds_added,
 cds_order,
 cds_comment,
 cds_delcause,
 cds_entry,
 cds_openid
FROM
 concept_data_synonym
WHERE
 ci_id=%d AND
 cb_id=%d
|;



		#mv_orderを更新
		my $sth_ver_upd = $dbh->prepare(qq|UPDATE model_version SET mv_order=mv_order+1 WHERE md_id=? AND mv_order>=?|) or die $dbh->errstr;
		$sth_ver_upd->execute($config->{'md'},$config->{'order'}) or die $dbh->errstr;
		$sth_ver_upd->finish;
		undef $sth_ver_upd;

		#データ追加(model_version,model_revision)
		my $t = localtime;
		my $mv_release = $t->ymd('-');
		my $mv_rep_key = $t->strftime('%y%m%d');
		my $mr_release = $t->strftime('%Y-%m-%d %H:%M:%S');
		my $mr_rep_key = $mv_rep_key;
		my $mr_revision = $t->strftime('%y%m%d%H%M');
		my $mv_version = sprintf("%s.%s.%s",$config->{'version'},$config->{'revision'},$mr_revision);

		my $sth_ver_ins = $dbh->prepare(qq|INSERT INTO model_version (md_id,mv_id,mv_version,mv_order,mv_name_e,mv_objects_set,mv_release,mv_rep_key,mv_entry,mv_openid,mv_publish,mv_modified,mv_use,ci_id,cb_id) VALUES (?,?,?,?,?,?,?,?,now(),'system',false,now(),'true',?,?)|) or die $dbh->errstr;
		my $sth_rev_ins = $dbh->prepare(qq|INSERT INTO model_revision (md_id,mv_id,mr_id,mr_version,mr_revision,mr_order,mr_release,mr_rep_key,mr_entry,mr_openid,mr_use) VALUES (?,?,?,?,?,1,?,?,now(),'system','true')|) or die $dbh->errstr;

		my $hash_copy_info;

		#データ追加(model_version)
		$sth_ver_ins->execute($config->{'md'},$config->{'mv'},$mv_version,$config->{'order'},$config->{'name'},$config->{'objectset'},$mv_release,$mv_rep_key,$config->{'ci'},$config->{'cb'}) or die $dbh->errstr;
		$sth_ver_ins->finish;
		undef $sth_ver_ins;

		#データ追加(model_revision)
		$sth_rev_ins->execute($config->{'md'},$config->{'mv'},$config->{'mr'},$mv_version,$mr_revision,$mr_release,$mr_rep_key) or die $dbh->errstr;
		$sth_rev_ins->finish;
		undef $sth_rev_ins;

		$dbh->do(sprintf($sql_bd_ins_fmt, $config->{'md'}, $config->{'mv'}, $config->{'mr'}, $config->{'ci'}, $config->{'cb'})) or die $dbh->errstr;
		$dbh->do(sprintf($sql_bti_ins_fmt, $config->{'md'}, $config->{'mv'}, $config->{'mr'}, $config->{'ci'}, $config->{'cb'})) or die $dbh->errstr;
		$dbh->do(sprintf($sql_btt_ins_fmt, $config->{'md'}, $config->{'mv'}, $config->{'mr'}, $config->{'ci'}, $config->{'cb'})) or die $dbh->errstr;

		$sth_cbr_sel->execute($config->{'ci'},$config->{'cb'}) or die $dbh->errstr;
		my($f_potid,$use_f_potids);
		my $column_number = 0;
		$sth_cbr_sel->bind_col(++$column_number, \$f_potid, undef);
		while($sth_cbr_sel->fetch){
			$use_f_potids->{$f_potid} = undef;
		}
		$sth_cbr_sel->finish;

		$sth_ct_sel->execute($config->{'ci'},$config->{'cb'}) or die $dbh->errstr;
		my($cdi_id,$cdi_pid,$bul_id,$f_potids,$cdi_pids,$cdi_cids);
		$column_number = 0;
		$sth_ct_sel->bind_col(++$column_number, \$cdi_id, undef);
		$sth_ct_sel->bind_col(++$column_number, \$cdi_pid, undef);
		$sth_ct_sel->bind_col(++$column_number, \$bul_id, undef);
		$sth_ct_sel->bind_col(++$column_number, \$f_potids, undef);
		while($sth_ct_sel->fetch){
			my $is_ins = 0;
			if($bul_id==3){
				$is_ins = 1;
				$cdi_pids->{$bul_id}->{$cdi_pid} = undef if(defined $cdi_pid);
				$cdi_cids->{$bul_id}->{$cdi_id} = undef if(defined $cdi_id);
			}
			elsif($bul_id==4 && defined $f_potids && length $f_potids){
				my @F_POTIDS;
				foreach my $f_potid (split(/;/,$f_potids)){
					next unless(exists $use_f_potids->{$f_potid});
					$is_ins = 1;
					$cdi_pids->{$bul_id}->{$cdi_pid} = undef if(defined $cdi_pid);
					$cdi_cids->{$bul_id}->{$cdi_id} = undef if(defined $cdi_id);
					push(@F_POTIDS, $f_potid);
				}
				$f_potids = join(';',@F_POTIDS);
			}
			next unless($is_ins);

			$sth_bt_ins->execute($config->{'md'},$config->{'mv'},$config->{'mr'},$config->{'ci'},$config->{'cb'},$cdi_id,$cdi_pid,$bul_id,$f_potids) or die $dbh->errstr;
			$sth_bt_ins->finish;
			#&cgi_lib::common::message(qq|cdi_id=[$cdi_id],bul_id=[$bul_id]|, $LOG);
		}
		$sth_ct_sel->finish;

		if(defined $cdi_pids && ref $cdi_pids eq 'HASH'){
			foreach my $bul_id (keys(%$cdi_pids)){
				foreach my $cdi_id (keys(%{$cdi_pids->{$bul_id}})){
					delete $cdi_pids->{$bul_id}->{$cdi_id} if(exists $cdi_cids->{$bul_id}->{$cdi_id});
				}
			}
			foreach my $bul_id (keys(%$cdi_pids)){
				foreach my $cdi_id (keys(%{$cdi_pids->{$bul_id}})){
					$sth_bt_ins->execute($config->{'md'},$config->{'mv'},$config->{'mr'},$config->{'ci'},$config->{'cb'},$cdi_id,undef,$bul_id,undef) or die $dbh->errstr;
					$sth_bt_ins->finish;
					#&cgi_lib::common::message(qq|cdi_id=[$cdi_id],bul_id=[$bul_id]|, $LOG);
				}
			}
		}

		$dbh->do(sprintf($sql_bds_ins_fmt, $config->{'md'}, $config->{'mv'}, $config->{'mr'}, $config->{'ci'}, $config->{'cb'})) or die $dbh->errstr;

		$sth_cds_sel->execute($config->{'ci'},$config->{'cb'}) or die $dbh->errstr;
		my($cs_id,$cdst_id,$cds_id);
		$column_number = 0;
		$sth_cds_sel->bind_col(++$column_number, \$cdi_id, undef);
		$sth_cds_sel->bind_col(++$column_number, \$cs_id, undef);
		$sth_cds_sel->bind_col(++$column_number, \$cdst_id, undef);
		$sth_cds_sel->bind_col(++$column_number, \$cds_id, undef);
		while($sth_cds_sel->fetch){
			$sth_bds_upd->execute($cds_id,$config->{'md'},$config->{'mv'},$config->{'mr'},$config->{'ci'},$config->{'cb'},$cdi_id,$cs_id,$cdst_id) or die $dbh->errstr;
			$sth_bds_upd->finish;
		}
		$sth_cds_sel->finish;

#		$dbh->commit();
	};
	if($@){
		my $msg = &cgi_lib::common::decodeUTF8($@);
#		$dbh->rollback;

		&cgi_lib::common::message($msg, $LOG);
		exit 1;
	}
#	$dbh->{'AutoCommit'} = 1;
#	$dbh->{'RaiseError'} = 0;
}

sub create_import_param_file {
	if(exists $config->{'file'} && defined $config->{'file'} && length $config->{'file'} && -f $config->{'file'} && -r $config->{'file'} && -s $config->{'file'}){
		my($file_size,$file_mtime) = (stat($config->{'file'}))[7,9];
		my $t = localtime;
		my $temp_dir = &catdir($FindBin::Bin,'temp',,sprintf("%s_%05d",$t->strftime('%Y%m%d_%H%M%S'),$$));
		unless(-e $temp_dir){
			my $old_umask = umask(0);
			&File::Path::mkpath($temp_dir,{mode=>0777});
			chmod 0777,$temp_dir;
			umask($old_umask);
		}
		my $basename = &cgi_lib::common::decodeUTF8(&File::Basename::basename($config->{'file'}));
		my $temp_file = &catfile($temp_dir,$basename);
		&File::Copy::copy($config->{'file'},$temp_file);

		my $time_md5 = &Digest::MD5::md5_hex(&Time::HiRes::time());
		my $params_file = &catfile($temp_dir,qq|$time_md5.json|);
		my $params_txt_file = &catfile($temp_dir,qq|$time_md5.txt|);
		my $RTN = {
			'file' => $temp_file,
			'name' => $basename,
			'size' => $file_size,
			'last' => $file_mtime * 1000,
			'model' => 'bp3d',
			'version' => $config->{'name'},
			'ag_data' => qq|obj/bp3d/$config->{'name'}|,
			'tree' => 'isa',
			'md_id' => $config->{'md'} - 0,
			'mv_id' => $config->{'mv'} - 0,
			'mr_id' => $config->{'mr'} - 0,
			'ci_id' => $config->{'ci'} - 0,
			'cb_id' => $config->{'cb'} - 0,
			'bul_id' => 3,
			'current_datas' => undef,
			'cmd' => 'import-concept-art-map',
		};
		&cgi_lib::common::writeFileJSON($params_file,$RTN,1);
		#say $params_file;

		my @args;
		push(@args,&catfile($FindBin::Bin,'batch-import.pl'));
#		push(@args,&catfile($FindBin::Bin,'test.pl'));
		push(@args,qq|--db=$config->{'db'}|);
		push(@args,qq|--host=$config->{'host'}|);
		push(@args,qq|--port=$config->{'port'}|);
		push(@args,$params_file);
		&cgi_lib::common::message(join(' ',@args), $LOG);
		system(@args) == 0 or die "system @args failed: $?";

		&File::Path::rmtree($temp_dir);
	}
}

sub main {
	unless(&check_mv()){
		&check_cb();
		&check_name();
		&check_objectset();
		&check_order();
		&create_dataset();
	}
	&cgi_lib::common::message($config, $LOG);

	&create_import_param_file();

}

&main();
