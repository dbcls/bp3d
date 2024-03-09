#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI::Cookie;
use JSON::XS;

use File::Spec::Functions qw(catdir catfile);
use Cwd;
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'API'),&Cwd::abs_path(&catdir($FindBin::Bin,'..','lib')),&Cwd::abs_path(&catdir($FindBin::Bin,'..','..','ag-common','lib'));
use cgi_lib::common;
use AG::login;

require "common.pl";
require "common_db.pl";
my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();

my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);

#&decodeForm(\%FORM);
delete $FORM{_formdata} if(exists($FORM{_formdata}));
foreach my $key (keys(%FORM)){
	next unless(exists($FORM{$key}));
	$FORM{$key} = &_trim($FORM{$key});
	delete $FORM{$key} if(length($FORM{$key})==0);
}

#my %COOKIE = ();
#&getCookie(\%COOKIE);

my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0, qr/\..*$/);
my $LOG = &cgi_lib::common::getLogFH(\%FORM,\%COOKIE);

#my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
#my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
#open(LOG,">> log.txt");
#print $LOG "\n[$logtime]:$0\n";

#foreach my $key (sort keys(%FORM)){
#	print $LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}
#foreach my $key (sort keys(%COOKIE)){
#	print $LOG __LINE__,":\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
#}

#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $RTN = {
	success => JSON::XS::false,
	msg     => undef
};

my $parentURL = $FORM{parent} if(exists($FORM{parent}));
my ($lsdb_OpenID,$lsdb_Auth);
my $lsdb_Config;
my $lsdb_Identity;
if(defined $parentURL){
	($lsdb_OpenID,$lsdb_Auth,$lsdb_Config) = &openidAuth($parentURL);
}elsif(exists($COOKIE{openid_url}) && exists($COOKIE{openid_session})){
	($lsdb_OpenID,$lsdb_Auth,$lsdb_Config,$lsdb_Identity) = &AG::login::openidAuthSession($COOKIE{openid_url},$COOKIE{openid_session});
}
print $LOG __LINE__,qq|:lsdb_Auth=[$lsdb_Auth]\n| if(defined $lsdb_Auth);

delete $FORM{f_id} if(!defined $lsdb_Auth || !$lsdb_Auth);

if(!exists($FORM{f_id})){
	$RTN->{msg} = qq|Please input FMAID|;
	my $json = &cgi_lib::common::printContentJSON($RTN,\%FORM);
	say $LOG __LINE__.':'.$json;
	close($LOG);
	exit;
}

if(!exists($FORM{f_pid})){
	$RTN->{msg} = qq|Please input Parent FMAID|;
	my $json = &cgi_lib::common::printContentJSON($RTN,\%FORM);
	say $LOG __LINE__.':'.$json;
	close($LOG);
	exit;
}

if(!(exists($FORM{b_version}) || (exists($FORM{tg_id}) && exists($FORM{tgi_id})))){
	$RTN->{msg} = qq|Please input Version|;
	my $json = &cgi_lib::common::printContentJSON($RTN,\%FORM);
	say $LOG __LINE__.':'.$json;
	close($LOG);
	exit;
}
if(
	!exists($FORM{p_coord}) ||
	!exists($FORM{p_x3d}) ||
	!exists($FORM{p_y3d}) ||
	!exists($FORM{p_z3d}) ||
	!exists($FORM{p_avx3d}) ||
	!exists($FORM{p_avy3d}) ||
	!exists($FORM{p_avz3d}) ||
	!exists($FORM{p_uvx3d}) ||
	!exists($FORM{p_uvy3d}) ||
	!exists($FORM{p_uvz3d})
){
	$RTN->{msg} = qq|Please input Coordinate|;
	my $json = &cgi_lib::common::printContentJSON($RTN,\%FORM);
	say $LOG __LINE__.':'.$json;
	close($LOG);
	exit;
}

$FORM{lng} = $COOKIE{"ag_annotation.locale"} if(!exists($FORM{lng}) && exists($COOKIE{"ag_annotation.locale"})); #とりあえず
$FORM{lng} = "en" if(!exists($FORM{lng}));

$FORM{version} = $FORM{b_version};
$FORM{b_version} = &convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);

#if(!exists($FORM{tg_id}) || !exists($FORM{tgi_id})){
#	my $tg_id;
#	my $tgi_id;
#	my $sth_tree_group_item = $dbh->prepare(qq|select tg_id,tgi_id from tree_group_item where tgi_version=?|);
#	$sth_tree_group_item->execute($FORM{b_version});
#	my $column_number = 0;
#	$sth_tree_group_item->bind_col(++$column_number, \$tg_id, undef);
#	$sth_tree_group_item->bind_col(++$column_number, \$tgi_id, undef);
#	$sth_tree_group_item->fetch;
#	if(defined $tg_id && defined $tgi_id){
#		$FORM{tg_id} = $tg_id;
#		$FORM{tgi_id} = $tgi_id;
#	}
#	$sth_tree_group_item->finish;
#	undef $sth_tree_group_item;
#}

#if(!exists($FORM{b_version})){
#	my $tg_id;
#	my $version;
#	my $sth_tree_group_item = $dbh->prepare(qq|select tgi_version from tree_group_item where tg_id=? and tgi_id=?|);
#	$sth_tree_group_item->execute($FORM{tg_id},$FORM{tgi_id});
#	my $column_number = 0;
#	$sth_tree_group_item->bind_col(++$column_number, \$version, undef);
#	$sth_tree_group_item->fetch;
#	$FORM{b_version} = $version if(defined $version);
#	$sth_tree_group_item->finish;
#	undef $sth_tree_group_item;
#}

my $wt_version = qq|tg_id=$FORM{tg_id} and tgi_id=$FORM{tgi_id}|;

$FORM{f_id} = &_trim($FORM{f_id}) if(exists($FORM{f_id}));

#$FORM{version} = $FORM{b_version};#互換の為

my $record = &getFMA($dbh,\%FORM,$FORM{f_id});
#foreach my $key (keys(%$record)){
#	print $LOG __LINE__,":[$key]=[",$record->{$key},"][",(exists($record->{$key})?1:0),"][",(defined($record->{$key})?1:0),"]\n";
#}

#既にポイント以外で登録されているか確認。
if(exists($record->{b_id}) && defined($record->{b_id}) && (!exists($record->{elem_type}) || (exists($record->{elem_type}) && $record->{elem_type} ne 'bp3d_point'))){
	$RTN->{msg} = qq|Already exists.|;
	my $json = &cgi_lib::common::printContentJSON($RTN,\%FORM);
	say $LOG __LINE__.':'.$json;
	close($LOG);
	exit;
}

#既にポイントが登録されているか確認。
my $f_pid;
my $p_conventional;
my $p_is_a;
my $p_part_of;
my $sth_bp3d_point = $dbh->prepare(qq|select f_pid,p_conventional,p_is_a,p_part_of from bp3d_point where $wt_version and f_id=? and p_delcause is null|);
$sth_bp3d_point->execute($FORM{f_id});
my $count = $sth_bp3d_point->rows();
my $column_number = 0;
$sth_bp3d_point->bind_col(++$column_number, \$f_pid, undef);
$sth_bp3d_point->bind_col(++$column_number, \$p_conventional, undef);
$sth_bp3d_point->bind_col(++$column_number, \$p_is_a, undef);
$sth_bp3d_point->bind_col(++$column_number, \$p_part_of, undef);
$sth_bp3d_point->fetch;
$sth_bp3d_point->finish;
undef $sth_bp3d_point;
if($count>0){
	unless(exists($FORM{p_overwrite})){
		$RTN->{msg} = qq|Already exists. Overwrite?|;
		$RTN->{code} = 100;
		my $json = &cgi_lib::common::printContentJSON($RTN,\%FORM);
		say $LOG __LINE__.':'.$json;
		close($LOG);
		exit;
	}
	if($f_pid ne $FORM{f_pid}){
		undef $p_conventional;
		undef $p_is_a;
		undef $p_part_of;
	}
}else{
	$count = 0;
}
unless(defined $p_conventional){
	my $sth_parent = $dbh->prepare(qq|select tree.f_pid from tree where $wt_version and tree.f_id=? and tree.t_type=1 group by tree.f_pid|);
	my %PARENT = ();
	&getParentTree($sth_parent,$FORM{f_pid},\%PARENT);
	$p_conventional = join(",",keys(%PARENT))."," if(scalar keys(%PARENT)>0);
	undef $sth_parent;
	undef %PARENT;
}
unless(defined $p_is_a){
	my $sth_parent = $dbh->prepare(qq|select fma_isa.f_pid from fma_isa where fma_isa.f_id=?|);
	my %PARENT = ();
	&getParentTree($sth_parent,$FORM{f_id},\%PARENT);
	if(scalar keys(%PARENT)>0){
		my $f_id = $FORM{f_id};
		my @temp = grep { !/^$f_id$/} keys(%PARENT);
		$p_is_a = join(",",@temp)."," if(scalar @temp > 0);
		undef @temp;
		undef $f_id;
	}
	undef $sth_parent;
	undef %PARENT;
}
unless(defined $p_part_of){
	my $sth_parent = $dbh->prepare(qq|select fma_partof.f_pid from fma_partof where fma_partof.f_id=?|);
	my %PARENT = ();
	&getParentTree($sth_parent,$FORM{f_id},\%PARENT);
	if(scalar keys(%PARENT)>0){
		my $f_id = $FORM{f_id};
		my @temp = grep { !/^$f_id$/} keys(%PARENT);
		$p_part_of = join(",",@temp)."," if(scalar @temp > 0);
		undef @temp;
		undef $f_id;
	}
	undef $sth_parent;
	undef %PARENT;
}

$dbh->{AutoCommit} = 0;
$dbh->{RaiseError} = 1;
my $rows;
eval{
	my $sth;
	my $param_num;
	my $max_c_id;
	my $image;

	my $paths = &getImagePaths($FORM{f_id},$FORM{b_version});
	print $LOG __LINE__,":\$paths=[",(scalar @$paths),"]\n";
	foreach my $path (@$paths){
		print $LOG __LINE__,":\$path=[",$path,"]\n";
		next unless(-e $path);
		if(-f $path){
			unlink $path;
		}elsif(-d $path){
			opendir(DIR, $path);
			my @files = sort grep {-f "$path/$_"} readdir(DIR);
			closedir(DIR);
			foreach my $file (@files){
				print $LOG __LINE__,":\$file=[",$file,"]\n";
				unlink qq|$path/$file|;
			}
			rmdir $path;
		}
	}

	$param_num = 0;
	if(exists($FORM{p_delcause}) || exists($FORM{p_delcause_old})){
		$sth = $dbh->prepare(q{ update bp3d_point set p_delcause=?,p_m_openid=?,p_modified='now()' where $wt_version and f_id=? });
		$sth->bind_param(++$param_num, $FORM{p_delcause});
		$sth->bind_param(++$param_num, $lsdb_OpenID);
		$sth->bind_param(++$param_num, $FORM{f_id});
		$sth->execute();
		$rows = $sth->rows;
		$sth->finish;
		undef $sth;
	}else{
		if($count>0){
			$sth = $dbh->prepare(qq{ update bp3d_point set f_pid=?,p_name_e=?,p_name_j=?,p_name_k=?,p_name_l=?,p_organsys_e=?,p_organsys_j=?,p_syn_e=?,p_syn_j=?,p_label=?,p_conventional=?,p_is_a=?,p_part_of=?,p_coord=?,p_x3d=?,p_y3d=?,p_z3d=?,p_avx3d=?,p_avy3d=?,p_avz3d=?,p_uvx3d=?,p_uvy3d=?,p_uvz3d=?,p_m_openid=?,p_modified='now()',p_delcause=null where tg_id=? and tgi_id=? and f_id=? });
		}else{
			$sth = $dbh->prepare(qq{ insert into bp3d_point (f_pid,p_name_e,p_name_j,p_name_k,p_name_l,p_organsys_e,p_organsys_j,p_syn_e,p_syn_j,p_label,p_conventional,p_is_a,p_part_of,p_coord,p_x3d,p_y3d,p_z3d,p_avx3d,p_avy3d,p_avz3d,p_uvx3d,p_uvy3d,p_uvz3d,p_e_openid,p_m_openid,p_entry,p_modified,tg_id,tgi_id,f_id) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'now()','now()',?,?,?) });
		}

		if(exists($FORM{p_syn_e})){
			$FORM{p_syn_e} =~ s/\x0D\x0A|\x0D|\x0A/\n/mg;
			$FORM{p_syn_e} =~ s/^\s*//mg;
			$FORM{p_syn_e} =~ s/\s*$//mg;
			$FORM{p_syn_e} =~ s/\n/\|/mg;
			$FORM{p_syn_e} =~ s/\|{2,}/\|/mg;
		}
		if(exists($FORM{p_syn_j})){
			$FORM{p_syn_j} =~ s/\x0D\x0A|\x0D|\x0A/\n/mg;
			$FORM{p_syn_j} =~ s/^\s*//mg;
			$FORM{p_syn_j} =~ s/\s*$//mg;
			$FORM{p_syn_j} =~ s/\n/\|/mg;
			$FORM{p_syn_j} =~ s/\|{2,}/\|/mg;
		}

		$FORM{p_name_e} = $record->{name_e} if(!exists($FORM{p_name_e}) && exists($record->{name_e}));
		$FORM{p_name_j} = $record->{name_j} if(!exists($FORM{p_name_j}) && exists($record->{name_j}));
		$FORM{p_name_k} = $record->{name_k} if(!exists($FORM{p_name_k}) && exists($record->{name_k}));
		$FORM{p_name_l} = $record->{name_l} if(!exists($FORM{p_name_l}) && exists($record->{name_l}));
		$FORM{p_organsys_e} = $record->{organsys_e} if(!exists($FORM{p_organsys_e}) && exists($record->{organsys_e}));
		$FORM{p_organsys_j} = $record->{organsys_j} if(!exists($FORM{p_organsys_j}) && exists($record->{organsys_j}));
		$FORM{p_syn_e} = $record->{syn_e} if(!exists($FORM{p_syn_e}) && exists($record->{syn_e}));
		$FORM{p_syn_j} = $record->{syn_j} if(!exists($FORM{p_syn_j}) && exists($record->{syn_j}));

		$sth->bind_param(++$param_num, $FORM{f_pid});
		$sth->bind_param(++$param_num, $FORM{p_name_e});
		$sth->bind_param(++$param_num, $FORM{p_name_j});
		$sth->bind_param(++$param_num, $FORM{p_name_k});
		$sth->bind_param(++$param_num, $FORM{p_name_l});
		$sth->bind_param(++$param_num, $FORM{p_organsys_e});
		$sth->bind_param(++$param_num, $FORM{p_organsys_j});
		$sth->bind_param(++$param_num, $FORM{p_syn_e});
		$sth->bind_param(++$param_num, $FORM{p_syn_j});
		$sth->bind_param(++$param_num, $FORM{p_label});
		$sth->bind_param(++$param_num, $p_conventional);
		$sth->bind_param(++$param_num, $p_is_a);
		$sth->bind_param(++$param_num, $p_part_of);
		$sth->bind_param(++$param_num, $FORM{p_coord});
		$sth->bind_param(++$param_num, $FORM{p_x3d});
		$sth->bind_param(++$param_num, $FORM{p_y3d});
		$sth->bind_param(++$param_num, $FORM{p_z3d});
		$sth->bind_param(++$param_num, $FORM{p_avx3d});
		$sth->bind_param(++$param_num, $FORM{p_avy3d});
		$sth->bind_param(++$param_num, $FORM{p_avy3d});
		$sth->bind_param(++$param_num, $FORM{p_uvx3d});
		$sth->bind_param(++$param_num, $FORM{p_uvy3d});
		$sth->bind_param(++$param_num, $FORM{p_uvz3d});
		$sth->bind_param(++$param_num, $lsdb_OpenID);
		$sth->bind_param(++$param_num, $lsdb_OpenID) if($count==0);
		$sth->bind_param(++$param_num, $FORM{tg_id});
		$sth->bind_param(++$param_num, $FORM{tgi_id});
		$sth->bind_param(++$param_num, $FORM{f_id});

		$sth->execute();
		$rows = $sth->rows;
		$sth->finish;
		undef $sth;
	}
	$dbh->commit();

	$RTN->{success} = JSON::XS::true;
	$RTN->{record}  = &getFMA($dbh,\%FORM,$FORM{f_id});

#	my $json = encode_json($RTN);
#	print $json;
#	print $LOG __LINE__,":",$json,"\n";
};
if($@){
#	my $msg = $@;
	$dbh->rollback;

#	$msg =~ s/\s*$//g;
#	$msg =~ s/^\s*//g;
#	my $RTN = {
#		"success" => JSON::XS::false,
#		"msg"     => $msg
#	};
#	my $json = encode_json($RTN);
#	print $json;
#	print $LOG __LINE__,":",$json,"\n";
}
$dbh->{AutoCommit} = 1;
$dbh->{RaiseError} = 0;

my $json = &cgi_lib::common::printContentJSON($RTN,\%FORM);
say $LOG __LINE__.':'.$json;

close($LOG);
exit;

sub getParentTree {
	my $sth = shift;
	my $f_id = shift;
	my $route = shift;

	print $LOG __LINE__,qq|:\$f_id=[$f_id]:|,(scalar keys(%$route)),qq|\n|;

	return if(exists($route->{$f_id}));
	$route->{$f_id} = 1;

	my @F_PID = ();
	$sth->execute($f_id);
	if($sth->rows>0){
		my $f_pid;
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$f_pid, undef);
		while($sth->fetch){
			next unless(defined $f_pid);
			print $LOG __LINE__,qq|:\$f_pid=[$f_pid]:|,(scalar keys(%$route)),qq|\n|;
			push(@F_PID,$f_pid);
		}
	}
	$sth->finish;

	return if(scalar @F_PID == 0);

	foreach my $f_pid (@F_PID){
		&getParentTree($sth,$f_pid,$route);
	}
}
