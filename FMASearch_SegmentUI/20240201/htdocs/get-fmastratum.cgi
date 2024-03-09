#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use JSON::XS;
use Storable;
#use File::Spec;
use Data::Dumper;
use Clone;
#use Time::HiRes;

use File::Spec::Functions qw(catdir catfile);
use Cwd;
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'API'),&Cwd::abs_path(&catdir($FindBin::Bin,'..','..','ag-common','lib'));
use cgi_lib::common;

require "common.pl";
require "common_db.pl";

use constant {
	DEBUG => 1,
};

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
if(exists($ENV{'REQUEST_METHOD'})){

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI::Cookie;

	my $query = CGI->new;
	&getParams($query,\%FORM,\%COOKIE);
}else{
	&decodeForm(\%FORM);
	delete $FORM{_formdata} if(exists($FORM{_formdata}));
	&getCookie(\%COOKIE);
}

my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);
my $LOG = exists $ENV{'REQUEST_METHOD'} ? &cgi_lib::common::getLogFH(\%FORM,\%COOKIE) : \*STDERR;

if(exists($ENV{'REQUEST_METHOD'})){
	my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
	my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
#	open(LOG,"> $FindBin::Bin/logs/$COOKIE{'ag_annotation.session'}.$cgi_name.txt");
#	print LOG "\n[$logtime]:$0\n";
#	foreach my $key (sort keys(%FORM)){
#		print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#	}
#	foreach my $key (sort keys(%COOKIE)){
#		print LOG "\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
#	}
#	foreach my $key (sort keys(%ENV)){
#		print LOG "ENV{$key}=[",$ENV{$key},"]\n";
#	}
}


&setDefParams(\%FORM,\%COOKIE);

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);

my $IMAGES = {
	"images" => []
};

#warn __LINE__,":\n";

unless(exists($FORM{'f_id'})){
#	print qq|Content-type: text/html; charset=UTF-8\n\n| if(exists($ENV{'REQUEST_METHOD'}));
	my $IMAGES = {"images" => []};
	$IMAGES->{'success'} = JSON::XS::false if(exists $FORM{'callback'} && defined $FORM{'callback'} && length $FORM{'callback'});
##	my $json = to_json($IMAGES);
#	my $json = &JSON::XS::encode_json($IMAGES);
##	$json =~ s/"(true|false)"/$1/mg;
#	$json = $FORM{'callback'}.qq|($json)| if(exists $FORM{'callback'} && defined $FORM{'callback'} && length $FORM{'callback'});
#	print $json;
##	print LOG $json,"\n";
##	close(LOG);

	&cgi_lib::common::printContentJSON($IMAGES,\%FORM);

	exit;
}

my $form = &Clone::clone(\%FORM);
$form->{$_} = undef for (qw|version bul_id position|);
my $cache_path = &getCachePath($form,$cgi_name);

my $store_path = $cache_path;

$cache_path = &catdir($cache_path,&getBaseDirFromID($FORM{'f_id'}));

unless(-e $cache_path){
	my $old = umask(0);
	&File::Path::make_path($cache_path,{mode=>0777});
	umask($old)
}

my $cache_file = &catfile($cache_path,qq|$FORM{'f_id'}.txt|);
my $cache_lock = &catfile($cache_path,qq|$FORM{'f_id'}.lock|);

my $store_file = &catfile($store_path,qq|tree_storable.store|);
my $store_tree_path_file = &catfile($store_path,qq|tree_path.store|);
my $store_lock = &catfile($store_path,qq|tree_storable.lock|);

my $store_buildup_tree_file = &catfile($store_path,qq|buildup_tree.store|);
my $store_fma_file = &catfile($store_path,qq|fma.store|);


$SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit";
sub sigexit {
	my($date) = `date`;
	$date =~ s/\s*$//g;
	print STDERR qq|[$date] KILL THIS CGI!![|.exists $ENV{SCRIPT_NAME} ? $ENV{SCRIPT_NAME} : $0 . qq|]\n|;
	rmdir $cache_lock if(-e $cache_lock);
	rmdir $store_lock if(-e $store_lock);
	exit(1);
}

my $cgi_utime;
if(exists($ENV{'REQUEST_METHOD'})){
	unlink $cache_file if(-e $cache_file && (stat($cache_file))[9] <= (stat($0))[9]);
	unlink $store_file if(-e $store_file && (stat($store_file))[9] <= (stat($0))[9]);
}else{
	$cgi_utime = (stat($0))[9]+1;
}

#unlink $cache_file if(-e $cache_file && -f $cache_file);
#unlink $store_file if(-e $store_file && -f $store_file);
#unlink $store_buildup_tree_file if(-e $store_buildup_tree_file && -f $store_buildup_tree_file);
#unlink $store_fma_file if(-e $store_fma_file && -f $store_fma_file);

my $json;
my $CACHE_FH;
if(-e $cache_file){
	if(exists $ENV{'REQUEST_METHOD'}){
		open($CACHE_FH,"< $cache_file") or die qq|$! [$cache_file]|;
		flock($CACHE_FH,1);
		if(-s $cache_file){
			local $/ = undef;
			$json = <$CACHE_FH>;
		}
		close($CACHE_FH);
	}elsif(-s $cache_file){
		$json = '';
	}
}
if(defined $json){
	if(exists $ENV{'REQUEST_METHOD'}){
		&cgi_lib::common::printContentJSON($json,\%FORM);
	}else{
		utime($cgi_utime, $cgi_utime, $cache_file) if((stat($cache_file))[9] < $cgi_utime);
	}
	exit;
}

#my $t0 = [&Time::HiRes::gettimeofday()];

mkdir $cache_lock, 0777 or exit(0);

open($CACHE_FH,"> $cache_file") or die qq|$! [$cache_file]|;
#&cgi_lib::common::message("OPEN:[$cache_file]", $LOG) if(DEBUG);
flock($CACHE_FH,2);
select($CACHE_FH);
$| = 1;
select(STDERR);
$| = 1;
select(STDOUT);
#&cgi_lib::common::message(&Time::HiRes::tv_interval($t0).":[$cache_file]", $LOG) if(DEBUG);


my %TREE_TYPE = ();
my %TREE_PATH = ();
my %TREE_CHILD = ();


my $href;
if(-e $store_file){
	if(open(STORE,$store_file)){
#		&cgi_lib::common::message(&Time::HiRes::tv_interval($t0).":[$store_file]", $LOG) if(DEBUG);
		flock(STORE,1);
		if(-s $store_file){
#			&cgi_lib::common::message(&Time::HiRes::tv_interval($t0).":[$store_file]", $LOG) if(DEBUG);
			$href = &Storable::fd_retrieve(*STORE) or die;
#			&cgi_lib::common::message(&Time::HiRes::tv_interval($t0).":[$store_file]", $LOG) if(DEBUG);
		}
		close(STORE);
	}
	%TREE_TYPE = %$href if(defined $href);
}
unless(defined $href){
	if(open(STORE,"> $store_file")){
		flock(STORE,2);

		my $t_id;
		my $t_pid;
		my $t_type;
		my $f_id;
		my $f_pid;
		my $t_delcause;
		my $sth = $dbh->prepare(qq|select cdi_id,cdi_pid,bul_id,cdi_name,cdi_pname,but_delcause from view_buildup_tree where md_id=$FORM{md_id} and mv_id=$FORM{mv_id} and mr_id=$FORM{mr_id} and bul_id in (select bul_id from buildup_logic where bul_rep_key in ('I','P'))|);
		$sth->execute() or die $dbh->errstr;
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$t_id, undef);
		$sth->bind_col(++$column_number, \$t_pid, undef);
		$sth->bind_col(++$column_number, \$t_type, undef);
		$sth->bind_col(++$column_number, \$f_id, undef);
		$sth->bind_col(++$column_number, \$f_pid, undef);
		$sth->bind_col(++$column_number, \$t_delcause, undef);
		while($sth->fetch){
			$TREE_TYPE{$t_type} = {} unless(exists $TREE_TYPE{$t_type});
			$TREE_TYPE{$t_type}->{$f_id} = {t_delcause => $t_delcause} unless(exists $TREE_TYPE{$t_type}->{$f_id});
	#		push(@{$TREE_TYPE{$t_type}->{$f_id}->{f_pids}},$f_pid) if(defined $f_pid);

			$TREE_TYPE{$t_type}->{$f_id}->{'t_delcause'} = undef if(defined $TREE_TYPE{$t_type}->{$f_id}->{'t_delcause'} && !defined $t_delcause);

		}
		$sth->finish;
		undef $sth;

		&Storable::store_fd(\%TREE_TYPE, *STORE) or die;
		close(STORE);
	}
#	&cgi_lib::common::message(&Time::HiRes::tv_interval($t0).":[$store_file]", $LOG) if(DEBUG);
}else{
#	&cgi_lib::common::message(&Time::HiRes::tv_interval($t0).":[$store_file]", $LOG) if(DEBUG);
}
=pod
my $sql_tree = qq|select|;
$sql_tree .= qq| tree.f_id|;
$sql_tree .= qq|,t2.cnum|;
$sql_tree .= qq| from tree|;
$sql_tree .= qq| left join (select COALESCE(count(f_id),0) as cnum,f_pid,t_type from tree where $wt_version group by f_pid,t_type) as t2 on tree.f_id=t2.f_pid and tree.t_type=t2.t_type|;
$sql_tree .= qq| where $wt_version and t_delcause is null and tree.t_type=? and tree.f_pid=?|;
=cut
my $sql_tree =<<SQL;
select
 tree.cdi_name
,t2.cnum
from
 view_buildup_tree as tree
left join (
    select
     md_id,
     mv_id,
     mr_id,
     ci_id,
     cb_id,
     COALESCE(count(cdi_id),0) as cnum,
     cdi_pid,
     bul_id
    from
     buildup_tree
    where
     md_id=$FORM{md_id} and 
     mv_id=$FORM{mv_id} and 
     mr_id=$FORM{mr_id}
    group by
     md_id,
     mv_id,
     mr_id,
     ci_id,
     cb_id,
     cdi_pid,
     bul_id
  ) as t2 on
     tree.md_id=t2.md_id and 
     tree.mv_id=t2.mv_id and 
     tree.mr_id=t2.mr_id and 
     tree.cdi_id=t2.cdi_pid and 
     tree.bul_id=t2.bul_id
where
 tree.md_id=$FORM{md_id} and 
 tree.mv_id=$FORM{mv_id} and 
 tree.mr_id=$FORM{mr_id} and 
 tree.but_delcause is null and 
 tree.bul_id=? and 
 tree.cdi_pname=?
SQL
my $sth_tree = $dbh->prepare($sql_tree) or die $dbh->errstr;


my $sql_fmatree = qq|
select
 cdi.cdi_name_j,
 COALESCE(f.cd_name,cdi.cdi_name_e),
 cdi.cdi_name_k,
 cdi.cdi_name_l,
 f.cd_delcause,
 COALESCE(t2.cnum,0)
from (
 select
  cdi_id,
  cd_name,
  cd_delcause
 from
  concept_data
 where
  ci_id=$FORM{ci_id} and
  cb_id=$FORM{cb_id}
 union
 select
  cdi_id,
  cd_name,
  cd_delcause
 from
  buildup_data
 where
  md_id=$FORM{md_id} and
  mv_id=$FORM{mv_id} and
  mr_id=$FORM{mr_id}
) as f
left join (
 select 
  COALESCE(count(cdi_id),0) as cnum,
  cdi_pid,
  bul_id
 from
  buildup_tree
 where
  md_id=$FORM{md_id} and
  mv_id=$FORM{mv_id} and
  mr_id=$FORM{mr_id}
 group by
  cdi_pid,
  bul_id
) as t2 on 
 f.cdi_id=t2.cdi_pid and
 t2.bul_id=?
left join (select * from concept_data_info where ci_id=$FORM{ci_id}) as cdi on f.cdi_id=cdi.cdi_id
where
 cdi.cdi_name=?
|;
my $sth_fmatree = $dbh->prepare($sql_fmatree) or die $dbh->errstr;

my $sql_buildup_tree = qq|select cdi_id from view_buildup_tree where md_id=$FORM{md_id} AND mv_id=$FORM{mv_id} AND mr_id=$FORM{mr_id} AND bul_id=? AND cdi_name=? AND cdi_pname=? AND but_delcause is null limit 1|;
my $sth_buildup_tree = $dbh->prepare($sql_buildup_tree);
my $sql_buildup_tree_root = qq|select cdi_id from view_buildup_tree where md_id=$FORM{md_id} AND mv_id=$FORM{mv_id} AND mr_id=$FORM{mr_id} AND bul_id=? AND cdi_name=? AND cdi_pname is null AND but_delcause is null limit 1|;
my $sth_buildup_tree_root = $dbh->prepare($sql_buildup_tree_root);

my %EXISTS_BUILDUP_TREE;
if(-e $store_buildup_tree_file){
	my $href;
	if(open(STORE,$store_buildup_tree_file)){
		flock(STORE,1);
		if(-s $store_buildup_tree_file){
			$href = &Storable::fd_retrieve(*STORE) or die;
		}
		close(STORE);
	}
	%EXISTS_BUILDUP_TREE = %$href if(defined $href);
}
my $EXISTS_BUILDUP_TREE_count = 0;
sub exists_buildup_tree {
	my $t_type = shift;
	my $f_id   = shift;
	my $f_pid  = shift;
	my $rtn = 0;
	if(defined $f_pid){
		if(exists $EXISTS_BUILDUP_TREE{$t_type} && exists $EXISTS_BUILDUP_TREE{$t_type}->{$f_id} && exists $EXISTS_BUILDUP_TREE{$t_type}->{$f_id}->{$f_pid}){
			$rtn = $EXISTS_BUILDUP_TREE{$t_type}->{$f_id}->{$f_pid};
		}else{
			$sth_buildup_tree->execute($t_type,$f_id,$f_pid) or die $dbh->errstr;
			$rtn = 1 if($sth_buildup_tree->rows()>0);
			$sth_buildup_tree->finish;
			$EXISTS_BUILDUP_TREE{$t_type}->{$f_id}->{$f_pid} = $rtn;
			$EXISTS_BUILDUP_TREE_count++;
		}
	}
	else{
		if(exists $EXISTS_BUILDUP_TREE{$t_type} && exists $EXISTS_BUILDUP_TREE{$t_type}->{$f_id} && exists $EXISTS_BUILDUP_TREE{$f_id}->{'root'}){
			$rtn = $EXISTS_BUILDUP_TREE{$t_type}->{$f_id}->{'root'};
		}else{
			$sth_buildup_tree_root->execute($t_type,$f_id) or die $dbh->errstr;
			$rtn = 1 if($sth_buildup_tree_root->rows()>0);
			$sth_buildup_tree_root->finish;
			$EXISTS_BUILDUP_TREE{$t_type}->{$f_id}->{'root'} = $rtn;
			$EXISTS_BUILDUP_TREE_count++;
		}
	}
#	if(defined $LOG){
#		$f_pid = '' unless(defined $f_pid);
#		&cgi_lib::common::message(qq|\$t_type=[$t_type],\$f_id=[$f_id],\$f_pid=[$f_pid],\$rtn=[$rtn]|, $LOG);
#	}
	return $rtn;
}

my %FMA;
if(-e $store_fma_file){
	my $href;
	if(open(STORE,$store_fma_file)){
		flock(STORE,1);
		if(-s $store_fma_file){
			$href = &Storable::fd_retrieve(*STORE) or die;
		}
		close(STORE);
	}
	%FMA = %$href if(defined $href);
}
my $FMA_count = scalar keys(%FMA);
sub getFMA_local {
	my $f_id = shift;
	my $t_type = shift;
	$t_type = 1 unless(defined $t_type);

	my $f_id2 = $f_id;
#	$f_id2 =~ s/\D+$//g;

	unless(exists $FMA{$t_type} && defined $FMA{$t_type} && ref $FMA{$t_type} eq 'HASH' && exists $FMA{$t_type}->{$f_id2}){

#&cgi_lib::common::message(&Time::HiRes::tv_interval($t0).":[$store_file]", $LOG) if(DEBUG);
		my($f_name_j,$f_name_e,$f_name_k,$f_name_l,$f_delcause,$cnum);

		$sth_fmatree->execute($t_type,$f_id2) or die $dbh->errstr;
		my $column_number = 0;
		$sth_fmatree->bind_col(++$column_number, \$f_name_j, undef);
		$sth_fmatree->bind_col(++$column_number, \$f_name_e, undef);
		$sth_fmatree->bind_col(++$column_number, \$f_name_k, undef);
		$sth_fmatree->bind_col(++$column_number, \$f_name_l, undef);
		$sth_fmatree->bind_col(++$column_number, \$f_delcause, undef);
		$sth_fmatree->bind_col(++$column_number, \$cnum, undef);
		$sth_fmatree->fetch;
		$sth_fmatree->finish;

		my $name;
		my $organsys;
		if($FORM{'lng'} eq "ja"){
			$name = (defined $f_name_j ? $f_name_j : $f_name_e);
		}else{
			$name = $f_name_e;
		}

		$FMA{$t_type}->{$f_id2} = {
			f_id       => $f_id,
			name_j     => $f_name_j,
			name_e     => $f_name_e,
			name_k     => $f_name_k,
			name_l     => $f_name_l,
			name       => $name,
			cnum       => $cnum,
			c_path     => undef,
			t_delcause => undef
		};
#&cgi_lib::common::message(&Time::HiRes::tv_interval($t0).":[$store_file]", $LOG) if(DEBUG);
	}
	return &Clone::clone($FMA{$t_type}->{$f_id2});
}

=pod
my $sth_isa_p = $dbh->prepare(qq|select fma_isa.f_pid from fma_isa where fma_isa.f_id=?|);
my $sth_isa_c = $dbh->prepare(qq|select fma_isa.f_id  from fma_isa where fma_isa.f_pid=?|);
my $sth_isa_b = $dbh->prepare(qq|select tree.f_id,tree.t_delcause from tree where $wt_version and tree.f_pid is null and tree.t_type=3|);
=cut

my $sth_isa_p = $dbh->prepare(qq|select cdi_pname from view_buildup_tree where md_id=$FORM{md_id} and mv_id=$FORM{mv_id} and mr_id=$FORM{mr_id} and bul_id=3 and cdi_name=?|);
my $sth_isa_c = $dbh->prepare(qq|select cdi_name  from view_buildup_tree where md_id=$FORM{md_id} and mv_id=$FORM{mv_id} and mr_id=$FORM{mr_id} and bul_id=3 and cdi_pname=?|);
my $sth_isa_b = $dbh->prepare(qq|select cdi_name,but_delcause from view_buildup_tree where md_id=$FORM{md_id} and mv_id=$FORM{mv_id} and mr_id=$FORM{mr_id} and cdi_pname is null and bul_id=3|);
my @ISA_ROUTE = ();

sub getISA_Path2Root {
	my $f_id = shift;
	my $route = shift;
	my $f_id2 = $f_id;
#	$f_id2 =~ s/\D+$//g;

	unless(defined $route){
		$route = $f_id;
	}else{
		$route .= qq|\t$f_id|;
	}

	my @F_PID = ();
	$sth_isa_p->execute($f_id2) or die $dbh->errstr;
	if($sth_isa_p->rows>0){
		my $f_pid;
		my $column_number = 0;
		$sth_isa_p->bind_col(++$column_number, \$f_pid, undef);
		while($sth_isa_p->fetch){
			push(@F_PID,$f_pid);
		}
	}
	$sth_isa_p->finish;
	if(scalar @F_PID > 0){
		foreach my $f_pid (@F_PID){
			&getISA_Path2Root($f_pid,$route);
			last if(scalar @ISA_ROUTE > 100);
		}
	}else{
		push(@ISA_ROUTE,$route);
	}
}
sub getISA_Children {
	my $f_id = shift;
	my $f_id2 = $f_id;
#	$f_id2 =~ s/\D+$//g;

	my $t_type = 3;
	my @RTN = ();

	$sth_isa_c->execute($f_id2) or die $dbh->errstr;
	my $f_cid;
	my $column_number = 0;
	$sth_isa_c->bind_col(++$column_number, \$f_cid, undef);
	while($sth_isa_c->fetch){
		my $rtn = &getFMA_local($f_cid,$t_type);
		$rtn->{'c_path'} = $TREE_PATH{$t_type}->{$f_cid} if(exists($TREE_PATH{$t_type}->{$f_cid}));
		push(@RTN,$rtn);
	}
	$sth_isa_c->finish;
	@RTN = sort {$a->{'name_e'} cmp $b->{'name_e'}} @RTN;
	return wantarray ? @RTN : \@RTN;
}
sub getISA_Brother {
	my $f_id = shift;
	my $f_id2 = $f_id;
#	$f_id2 =~ s/\D+$//g;

	my $t_type = 3;
	my @RTN = ();
	my @F_PID = ();
	my $f_pid;

	$sth_isa_p->execute($f_id2) or die $dbh->errstr;
	my $column_number = 0;
	$sth_isa_p->bind_col(++$column_number, \$f_pid, undef);
	while($sth_isa_p->fetch){
		push(@F_PID,$f_pid);
	}
	$sth_isa_p->finish;
	if(scalar @F_PID > 0){
		foreach my $f_pid (@F_PID){
			my $rtn = &getFMA_local($f_pid,$t_type);
			$rtn->{'c_path'} = $TREE_PATH{$t_type}->{$f_pid} if(exists($TREE_PATH{$t_type}->{$f_pid}));
			push(@{$rtn->{'children'}},&getISA_Children($f_pid));
			if(exists($rtn->{'children'})){
				my %tmp = ();
				@{$rtn->{'children'}} = grep( !$tmp{$_->{'f_id'}}++, @{$rtn->{'children'}} );
			}
			push(@RTN,$rtn) if(exists($rtn->{'children'}) && scalar @{$rtn->{'children'}}>0);
		}
	}else{
		my $rtn = {
			f_id       => undef,
			name_j     => undef,
			name_e     => undef,
			name_k     => undef,
			name_l     => undef,
			name       => undef,
			cnum       => undef,
			c_path     => undef,
			t_delcause => undef
		};
		$sth_isa_b->execute() or die $dbh->errstr;
		my $f_cid;
		my $f_cdelcause;
		my $column_number = 0;
		$sth_isa_b->bind_col(++$column_number, \$f_cid, undef);
		$sth_isa_b->bind_col(++$column_number, \$f_cdelcause, undef);
		while($sth_isa_b->fetch){
			my $fma = &getFMA_local($f_cid,$t_type);
#			$fma->{'c_path'} = $TREE_PATH{$t_type}->{$f_cid} if(exists($TREE_PATH{$t_type}->{$f_cid}));
			$fma->{'c_path'} = $f_cid unless(defined $f_cdelcause);
			push(@{$rtn->{'children'}},$fma);
		}
		if(exists($rtn->{'children'})){
#			my %tmp = ($f_id2=>1);
			my %tmp = ();
			@{$rtn->{'children'}} = grep( !$tmp{$_->{'f_id'}}++, @{$rtn->{'children'}} );
		}
		if(exists($rtn->{'children'}) && scalar @{$rtn->{'children'}}>0){
			@{$rtn->{'children'}} = sort {$a->{'name_e'} cmp $b->{'name_e'}} @{$rtn->{'children'}};
			push(@RTN,$rtn);
		}
		$sth_isa_b->finish;
	}
	@RTN = sort {$a->{'name_e'} cmp $b->{'name_e'}} @RTN;
	return wantarray ? @RTN : \@RTN;
}

my $sth_partof_p = $dbh->prepare(qq|select cdi_pname,f_potids from view_buildup_tree where md_id=$FORM{md_id} and mv_id=$FORM{mv_id} and mr_id=$FORM{mr_id} and bul_id=4 and cdi_name=?|);
my $sth_partof_c = $dbh->prepare(qq|select cdi_name,f_potids  from view_buildup_tree where md_id=$FORM{md_id} and mv_id=$FORM{mv_id} and mr_id=$FORM{mr_id} and bul_id=4 and cdi_pname=?|);
my $sth_partof_b = $dbh->prepare(qq|select cdi_name from view_buildup_tree where md_id=$FORM{md_id} and mv_id=$FORM{mv_id} and mr_id=$FORM{mr_id} and cdi_pname is null and bul_id=4|);
#my $sth_partof_type = $dbh->prepare(qq|select f_potname,f_potabbr from fma_partof_type where f_potid=?|);
my $sth_partof_type = $dbh->prepare(qq|select f_potname,f_potabbr,f_potid from fma_partof_type|);

my $but_cids_hash;
if(0){
	my $cdi_id;
	my $but_cids;
	my $column_number = 0;
	my $sth_view_buildup_tree = $dbh->prepare(qq|select cdi_id,but_cids from view_buildup_tree where md_id=$FORM{md_id} and mv_id=$FORM{mv_id} and mr_id=$FORM{mr_id} and bul_id=4 and cdi_name='FMA20394'|);
	$sth_view_buildup_tree->execute() or die $dbh->errstr;
	$sth_view_buildup_tree->bind_col(++$column_number, \$cdi_id, undef);
	$sth_view_buildup_tree->bind_col(++$column_number, \$but_cids, undef);
	$sth_view_buildup_tree->fetch;
	$sth_view_buildup_tree->finish;
	undef $sth_view_buildup_tree;
	$but_cids = &cgi_lib::common::decodeJSON($but_cids) if(defined $but_cids);
	$but_cids = [] unless(defined $but_cids && ref $but_cids eq 'ARRAY');
	push(@$but_cids,$cdi_id) if(defined $cdi_id);

	if(scalar @$but_cids){
		my $sth_concept_data_info = $dbh->prepare(qq|select cdi_name from concept_data_info where ci_id=$FORM{ci_id} and cdi_id in (|.join(',',map {'?'} @$but_cids).qq|)|);
		my $cdi_name;
		$sth_concept_data_info->execute(@$but_cids) or die $dbh->errstr;
		$sth_concept_data_info->bind_col(1, \$cdi_name, undef);
		while($sth_concept_data_info->fetch){
			$but_cids_hash->{$cdi_name} = undef if(defined $cdi_name);
		}
		$sth_concept_data_info->finish;
		undef $sth_concept_data_info;
	}
}
#&cgi_lib::common::message(&cgi_lib::common::encodeJSON($but_cids_hash,1),$LOG) if(defined $LOG);


my @ROUTE = ();
my @ROUTE_CIRCULAR = ();
my %ROUTE_CIRCULAR_HASH = ();
sub getPartof_Path2Root {
	my $f_id = shift;
	my $potype = shift;
	my $route = shift;
	my $f_id2 = $f_id;
#	$f_id2 =~ s/\D+$//g;

	my @TEMP_ROUTE = ();
	push(@TEMP_ROUTE,@$route) if(defined $route);

	my $exists_flag = scalar grep {$_->{'f_id'} eq $f_id} @TEMP_ROUTE;
#	foreach my $temp (@TEMP_ROUTE){
#		next if(!($temp->{'f_id'} eq $f_id));
#		$exists_flag = 1;
#		last;
#	}

	$sth_partof_p->execute($f_id2) or die $dbh->errstr;
	$sth_partof_c->execute($f_id2) or die $dbh->errstr;

#warn __LINE__,":",$sth_partof_p->rows,"\n";
#warn __LINE__,":",$sth_partof_c->rows,"\n";

	push(@TEMP_ROUTE,{f_id=>$f_id,f_potids=>$potype}) if($sth_partof_p->rows>0 || $sth_partof_c->rows>0);

	$sth_partof_p->finish;
	$sth_partof_c->finish;

	my @PARENT = ();

	unless($exists_flag){

		$sth_partof_p->execute($f_id2) or die $dbh->errstr;
		if($sth_partof_p->rows>0){
			my $f_pid;
			my $f_potids;
			my $column_number = 0;
			$sth_partof_p->bind_col(++$column_number, \$f_pid, undef);
			$sth_partof_p->bind_col(++$column_number, \$f_potids, undef);
			while($sth_partof_p->fetch){
				next unless(&exists_buildup_tree(4,$f_id2,$f_pid));
				push(@PARENT,{f_pid=>$f_pid,f_potids=>$f_potids});
			}
		}
		$sth_partof_p->finish;

	}
	else{#Circular reference
		$TEMP_ROUTE[-1]->{"circular_reference"} = 1;
	}


#warn __LINE__,":",$#TEMP_ROUTE,"\n";

	if(scalar @PARENT > 0){
		foreach my $parent (@PARENT){
			my $f_pid = $parent->{'f_pid'};
 			next unless((!defined $but_cids_hash || exists $but_cids_hash->{$f_pid}) && &exists_buildup_tree(4,$f_id2,$f_pid));
			my $f_potids = $parent->{'f_potids'};
			&getPartof_Path2Root($f_pid,$f_potids,\@TEMP_ROUTE);
			last if(scalar @ROUTE > 1000);
		}
	}elsif($#TEMP_ROUTE>=0){
		if(exists($TEMP_ROUTE[-1]->{"circular_reference"})){
			if(scalar @ROUTE_CIRCULAR <= 10){
				push(@ROUTE_CIRCULAR,\@TEMP_ROUTE) unless(exists($ROUTE_CIRCULAR_HASH{$TEMP_ROUTE[-1]->{'f_id'}}));
				$ROUTE_CIRCULAR_HASH{$TEMP_ROUTE[-1]->{'f_id'}} = "";
			}
		}else{
			push(@ROUTE,\@TEMP_ROUTE);
		}
	}
}
sub getPartof_Children {
	my $f_id = shift;
	my $f_id2 = $f_id;
#	$f_id2 =~ s/\D+$//g;

	my $t_type = 4;
	my @RTN = ();
	my $f_cid;
	my $f_cpotids;

	if(!defined $but_cids_hash || exists $but_cids_hash->{$f_id2}){
		$sth_partof_c->execute($f_id2) or die $dbh->errstr;
		my $column_number = 0;
		$sth_partof_c->bind_col(++$column_number, \$f_cid, undef);
		$sth_partof_c->bind_col(++$column_number, \$f_cpotids, undef);
		while($sth_partof_c->fetch){
			next unless((!defined $but_cids_hash || exists $but_cids_hash->{$f_cid}) && &exists_buildup_tree($t_type,$f_cid,$f_id2));
			my $rtn = &getFMA_local($f_cid,$t_type);
			$rtn->{'c_path'} = $TREE_PATH{$t_type}->{$f_cid} if(exists($TREE_PATH{$t_type}->{$f_cid}));
			foreach my $f_potid (split(/;/,$f_cpotids)){
				push(@{$rtn->{'potype'}},&getPartofType($f_potid));
			}
			push(@RTN,$rtn);
		}
		$sth_partof_c->finish;
		@RTN = sort {$a->{'name_e'} cmp $b->{'name_e'}} @RTN;
		@RTN = sort {$a->{'potype'}->[0]->{'potid'} <=> $b->{'potype'}->[0]->{'potid'}} @RTN;
	}
	return wantarray ? @RTN : \@RTN;
}

sub getPartof_Brother {
	my $f_id = shift;
	my $f_id2 = $f_id;
#	$f_id2 =~ s/\D+$//g;

	my $t_type = 4;
	my @RTN = ();
	my @PARENT = ();
	my $f_pid;
	my $f_potids;

	$sth_partof_p->execute($f_id2) or die $dbh->errstr;
	my $column_number = 0;
	$sth_partof_p->bind_col(++$column_number, \$f_pid, undef);
	$sth_partof_p->bind_col(++$column_number, \$f_potids, undef);
	while($sth_partof_p->fetch){
		next unless((!defined $but_cids_hash || exists $but_cids_hash->{$f_pid}) && &exists_buildup_tree($t_type,$f_id2,$f_pid));
		push(@PARENT,{f_pid=>$f_pid,f_potids=>$f_potids});
	}
	$sth_partof_p->finish;
	if(scalar @PARENT > 0){
		foreach my $parent (@PARENT){
			my $f_pid = $parent->{'f_pid'};
			next unless(!defined $but_cids_hash || exists $but_cids_hash->{$f_pid});
			my $f_potids = $parent->{'f_potids'};
			my $rtn = &getFMA_local($f_pid,$t_type);
			$rtn->{'c_path'} = $TREE_PATH{$t_type}->{$f_pid} if(exists($TREE_PATH{$t_type}->{$f_pid}));
			$rtn->{'potype'} = undef;
			push(@{$rtn->{'children'}},&getPartof_Children($f_pid));
			if(exists $rtn->{'children'} && defined $rtn->{'children'} && ref $rtn->{'children'} eq 'ARRAY' && scalar @{$rtn->{'children'}}>0){
				my %tmp = ();
				@{$rtn->{'children'}} = grep { (!defined $but_cids_hash || exists $but_cids_hash->{$_->{'f_id'}}) && &exists_buildup_tree($t_type,$_->{'f_id'},$f_pid) } grep( !$tmp{$_->{'f_id'}}++, @{$rtn->{'children'}} );
				foreach my $c (@{$rtn->{'children'}}){
					my $f_id = $c->{'f_id'};
					if(defined $c->{'c_path'}){
						$c->{'c_path'} = undef unless(&exists_buildup_tree($t_type,$f_id,$f_pid));
					}
				}
			}

			push(@RTN,$rtn) if(exists($rtn->{'children'}) && scalar @{$rtn->{'children'}}>0);
		}
		@RTN = sort {$a->{'name_e'} cmp $b->{'name_e'}} @RTN;
	}else{
	}
	return wantarray ? @RTN : \@RTN;
}

my %PART_OF_TYPE;
sub getPartofType {
	my $f_potid = shift;

	unless(exists $PART_OF_TYPE{$f_potid}){
		my $f_potid_temp;
		my $f_potname;
		my $f_potabbr;
#		$sth_partof_type->execute($f_potid) or die $dbh->errstr;
		$sth_partof_type->execute() or die $dbh->errstr;
		if($sth_partof_type->rows>0){
			my $column_number = 0;
			$sth_partof_type->bind_col(++$column_number, \$f_potname, undef);
			$sth_partof_type->bind_col(++$column_number, \$f_potabbr, undef);
			$sth_partof_type->bind_col(++$column_number, \$f_potid_temp, undef);
#			$sth_partof_type->fetch;
			while($sth_partof_type->fetch){
				$PART_OF_TYPE{$f_potid_temp} = {potid=>$f_potid_temp,potabbr=>$f_potabbr,potname=>$f_potname};
			}
		}
		$sth_partof_type->finish;
#		$PART_OF_TYPE{$f_potid} = {potid=>$f_potid,potabbr=>$f_potabbr,potname=>$f_potname};
#&cgi_lib::common::message(&cgi_lib::common::encodeJSON($PART_OF_TYPE{$f_potid},1),$LOG) if(defined $LOG);
#&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%PART_OF_TYPE,1),$LOG) if(defined $LOG);
	};
	return $PART_OF_TYPE{$f_potid};
}




my $sql;
if(!exists($FORM{'f_id'})){
	$IMAGES->{'success'} = JSON::XS::false if(exists $FORM{'callback'} && defined $FORM{'callback'} && length $FORM{'callback'});
#	my $json = to_json($IMAGES);
	my $json = &JSON::XS::encode_json($IMAGES);
#	$json =~ s/"(true|false)"/$1/mg;
	$json = $FORM{'callback'}.qq|($json)| if(exists $FORM{'callback'} && defined $FORM{'callback'} && length $FORM{'callback'});
	print $json;
#	print LOG $json,"\n";
	exit;
}else{
	$sql=<<SQL;
select
 cdi.cdi_name
,cdi.cdi_name_j
,COALESCE(f.cd_name,cdi.cdi_name_e)
from (
 select
  cdi_id,
  cd_name
 from
  concept_data
 where
  ci_id=$FORM{ci_id} and
  cb_id=$FORM{cb_id}
 union
 select
  cdi_id,
  cd_name
 from
  buildup_data
 where
  md_id=$FORM{md_id} and
  mv_id=$FORM{mv_id} and
  mr_id=$FORM{mr_id}
) as f
left join (select * from concept_data_info where ci_id=$FORM{ci_id}) as cdi on f.cdi_id=cdi.cdi_id
where
 cdi.cdi_name=?
SQL
}

&cgi_lib::common::message($sql, $LOG) if(defined $LOG);


my $sth = $dbh->prepare($sql);

my $f_id2 = $FORM{'f_id'};
#$f_id2 =~ s/\D+$//g;
$sth->execute($f_id2) or die $dbh->errstr;


my($a_fmaid,$a_name_j,$a_name_e);

my $column_number = 0;
$sth->bind_col(++$column_number, \$a_fmaid, undef);
$sth->bind_col(++$column_number, \$a_name_j, undef);
$sth->bind_col(++$column_number, \$a_name_e, undef);

my %DISP_FMA = ();

while($sth->fetch){
	my $name;
	if($FORM{'lng'} eq "ja"){
		$name = (defined $a_name_j ? $a_name_j : $a_name_e);
	}else{
		$name = $a_name_e;
	}
#warn __LINE__,":\n";

	my $HASH = {
		name       => $name,
		f_id       => $a_fmaid
	};

	if(defined $a_fmaid){
		my $t_type = 3;
		&getISA_Path2Root($a_fmaid);
		if(scalar @ISA_ROUTE > 0){

#print LOG __LINE__,":",Dumper(\@ISA_ROUTE),"\n";

			@ISA_ROUTE = sort {scalar (split(/\t/,$a)) <=> scalar (split(/\t/,$b)) } sort @ISA_ROUTE;
			foreach my $route (@ISA_ROUTE){
				my @f_paths;
				my $t_path = "";
				my @FIDS = reverse(split(/\t/,$route));
				foreach my $f_id (@FIDS){
					last if(defined $TREE_TYPE{$t_type}->{$f_id}->{'t_delcause'});
					push(@f_paths, $f_id);
					$t_path = join('/', @f_paths);

					$TREE_PATH{$t_type} = {} unless(exists($TREE_PATH{$t_type}));
					unless(exists($TREE_PATH{$t_type}->{$f_id})){
						$TREE_PATH{$t_type}->{$f_id} = $t_path;
					}elsif(length($TREE_PATH{$t_type}->{$f_id})>length($t_path)){
						$TREE_PATH{$t_type}->{$f_id} = $t_path;
					}elsif($TREE_PATH{$t_type}->{$f_id}>$t_path){
						$TREE_PATH{$t_type}->{$f_id} = $t_path;
					}
#warn __LINE__,":\$TREE_PATH{$t_type}->{$f_id}=[$TREE_PATH{$t_type}->{$f_id}]\n";
				}
			}
#print LOG __LINE__,":",Dumper($TREE_PATH{$t_type}),"\n";

			if(exists($TREE_PATH{$t_type})){
				$TREE_CHILD{$t_type} = {} unless(exists($TREE_CHILD{$t_type}));
				foreach my $f_pid (keys(%{$TREE_PATH{$t_type}})){
					$TREE_CHILD{$t_type}->{$f_pid} = 0 unless(exists($TREE_CHILD{$t_type}->{$f_pid}));
					my $f_id;
					my $cnum;
					$sth_tree->execute($t_type,$f_pid) or die $dbh->errstr;
					$TREE_CHILD{$t_type}->{$f_pid} += $sth_tree->rows();
					my $column_number = 0;
					$sth_tree->bind_col(++$column_number, \$f_id, undef);
					$sth_tree->bind_col(++$column_number, \$cnum, undef);
					while($sth_tree->fetch){
						my $t_path = $TREE_PATH{$t_type}->{$f_pid};
						$t_path .= qq|/$f_id| if(defined $cnum && $cnum>0);
						unless(exists($TREE_PATH{$t_type}->{$f_id})){
							$TREE_PATH{$t_type}->{$f_id} = $t_path;
						}elsif(length($TREE_PATH{$t_type}->{$f_id})>length($t_path)){
							$TREE_PATH{$t_type}->{$f_id} = $t_path;
						}elsif($TREE_PATH{$t_type}->{$f_id} gt $t_path){
							$TREE_PATH{$t_type}->{$f_id} = $t_path;
						}
					}
					$sth_tree->finish;
#print LOG __LINE__,":\$TREE_CHILD{$t_type}->{$f_pid}=[$TREE_CHILD{$t_type}->{$f_pid}]\n";
				}
			}

			$#ISA_ROUTE = 10 if($#ISA_ROUTE>10);
			foreach my $route (@ISA_ROUTE){
				my $ITEMS;
				my @f_paths;
				my $t_path = "";
				my @FIDS = reverse(split(/\t/,$route));
#print LOG __LINE__,":",Dumper(\@FIDS),"\n";
				my $f_pid;
				foreach my $f_id (@FIDS){
#print LOG __LINE__,":\$f_id=[$f_id]\n";
					push(@f_paths, $f_id) if(exists($TREE_CHILD{$t_type}) && exists($TREE_CHILD{$t_type}->{$f_id}) && $TREE_CHILD{$t_type}->{$f_id} > 0);
					$t_path = join('/', @f_paths);
					my $rtn = &getFMA_local($f_id,$t_type);
#print LOG __LINE__,":\$t_path=[$t_path]\n";
					if(defined $t_path){
						$rtn->{'c_path'} = $t_path;
					}

					if(defined $rtn->{'c_path'}){
						$rtn->{'c_path'} = undef unless(&exists_buildup_tree($t_type,$f_id,$f_pid));
					}

					push(@{$ITEMS->{'fma'}},$rtn);
					$f_pid = $f_id;
				}
				if(exists($ITEMS->{'fma'}) && scalar @{$ITEMS->{'fma'}} > 0){
					@{$ITEMS->{'fma'}} = reverse @{$ITEMS->{'fma'}};
					push(@{$HASH->{'is_a_path2root'}},$ITEMS);
				}
			}
		}

		$HASH->{'is_a_brother'} = &getISA_Brother($a_fmaid);
		$HASH->{'is_a_brother'} = undef if(scalar @{$HASH->{'is_a_brother'}} == 0);

		$HASH->{'is_a_children'} = &getISA_Children($a_fmaid);
		$HASH->{'is_a_children'} = undef if(scalar @{$HASH->{'is_a_children'}} == 0);

		my $t_type = 4;
		&getPartof_Path2Root($a_fmaid) if(!defined $but_cids_hash || exists $but_cids_hash->{$a_fmaid});
#print LOG __LINE__,":",scalar @ROUTE,"\n";
#print LOG __LINE__,":",Dumper(\@ROUTE),"\n";
		if(scalar @ROUTE > 0){
#			@ROUTE = sort {scalar @$a <=> scalar @$b} sort {$a->[(scalar @$a)-1]->{'f_id'} cmp $b->[(scalar @$b)-1]->{'f_id'} } @ROUTE;
			@ROUTE = sort {
				if($a->[-1]->{'f_id'} eq 'FMA20394' && $b->[-1]->{'f_id'}  eq 'FMA20394'){
					scalar @$a <=> scalar @$b;
				}elsif($a->[-1]->{'f_id'} eq 'FMA20394'){
					-1;
				}elsif($b->[-1]->{'f_id'}  eq 'FMA20394'){
					1;
				}else{
					0;
				}
			} sort {scalar @$a <=> scalar @$b} sort {$a->[-1]->{'f_id'} cmp $b->[-1]->{'f_id'} } @ROUTE;

			foreach my $route (@ROUTE){
				my @f_paths;
				my $t_path = "";
				my @TEMP_ROUTE = reverse(@$route);
				foreach my $temp (@TEMP_ROUTE){
					my $f_id = $temp->{'f_id'};
					last if(defined $TREE_TYPE{$t_type}->{$f_id}->{'t_delcause'});

					my $f_id = $temp->{'f_id'};
					push(@f_paths,$f_id);
					$t_path = join('/',@f_paths);

					$TREE_PATH{$t_type} = {} unless(exists($TREE_PATH{$t_type}));
					unless(exists($TREE_PATH{$t_type}->{$f_id})){
						$TREE_PATH{$t_type}->{$f_id} = $t_path;
					}elsif(length($TREE_PATH{$t_type}->{$f_id})>length($t_path)){
						$TREE_PATH{$t_type}->{$f_id} = $t_path;
					}elsif($TREE_PATH{$t_type}->{$f_id} gt $t_path){
						$TREE_PATH{$t_type}->{$f_id} = $t_path;
					}
				}
			}
			if(exists($TREE_PATH{$t_type})){
				foreach my $f_pid (keys(%{$TREE_PATH{$t_type}})){
					$TREE_CHILD{$t_type}->{$f_pid} = 0 unless(exists($TREE_CHILD{$t_type}->{$f_pid}));
					my $f_id;
					my $cnum;
					$sth_tree->execute($t_type,$f_pid) or die $dbh->errstr;
					$TREE_CHILD{$t_type}->{$f_pid} += $sth_tree->rows();
					my $column_number = 0;
					$sth_tree->bind_col(++$column_number, \$f_id, undef);
					$sth_tree->bind_col(++$column_number, \$cnum, undef);
					while($sth_tree->fetch){
						my $t_path = $TREE_PATH{$t_type}->{$f_pid};
						$t_path .= qq|/$f_id| if(defined $cnum && $cnum>0);
						if(!exists($TREE_PATH{$t_type}->{$f_id})){
							$TREE_PATH{$t_type}->{$f_id} = $t_path;
						}elsif(length($TREE_PATH{$t_type}->{$f_id})>length($t_path)){
							$TREE_PATH{$t_type}->{$f_id} = $t_path;
						}elsif($TREE_PATH{$t_type}->{$f_id} gt $t_path){
							$TREE_PATH{$t_type}->{$f_id} = $t_path;
						}
					}
					$sth_tree->finish;
				}
			}

#&cgi_lib::common::message(&cgi_lib::common::encodeJSON($TREE_TYPE{$t_type},1),$LOG) if(defined $LOG);
#&cgi_lib::common::message(&cgi_lib::common::encodeJSON($TREE_CHILD{$t_type},1),$LOG) if(defined $LOG);

			$#ROUTE = 10 if($#ROUTE>10);
			foreach my $route (@ROUTE){
#&cgi_lib::common::message(&cgi_lib::common::encodeJSON($route,1),$LOG) if(defined $LOG);
				my $ITEMS;
				my $t_delcause;
				my @f_paths;
				my $t_path = "";
#				my @TEMP_ROUTE = ();
#				for(my $rcnt=0;$rcnt<scalar @$route;$rcnt++){
#					my $temp = {
#						f_id => $route->[$rcnt]->{'f_id'},
#						f_potids => $route->[$rcnt]->{'f_potids'}
#					};
#					push(@TEMP_ROUTE,$temp);
#				}
				my @TEMP_ROUTE = map {{
						f_id => $_->{'f_id'},
						f_potids => $_->{'f_potids'}
				}} @$route;
				for(my $rcnt=0;$rcnt<$#TEMP_ROUTE;$rcnt++){
					$TEMP_ROUTE[$rcnt]->{'f_potids'} = $TEMP_ROUTE[$rcnt+1]->{'f_potids'};
					$TEMP_ROUTE[$rcnt+1]->{'f_potids'} = undef;
				}
				@TEMP_ROUTE = reverse(@TEMP_ROUTE);
				my $f_pid;
				foreach my $temp (@TEMP_ROUTE){
#&cgi_lib::common::message(&cgi_lib::common::encodeJSON($temp,1),$LOG) if(defined $LOG);
					my $f_id = $temp->{'f_id'};
					push(@f_paths, $f_id) if(exists($TREE_CHILD{$t_type}) && exists($TREE_CHILD{$t_type}->{$f_id}) && $TREE_CHILD{$t_type}->{$f_id} > 0);
					my $f_potids = $temp->{'f_potids'};
					$t_path = join('/', @f_paths);
					my $rtn = &getFMA_local($f_id,$t_type);
					unless(defined $t_delcause){
						$t_delcause = $TREE_TYPE{$t_type}->{$f_id}->{'t_delcause'};
						if(!defined $t_delcause && defined $t_path){
							$rtn->{'c_path'} = $t_path;
						}
					}elsif(exists($TREE_PATH{$t_type}->{$f_id})){
						$rtn->{'c_path'} = $TREE_PATH{$t_type}->{$f_id};
					}else{
						$rtn->{'c_path'} = undef;
					}
					if(defined $f_potids){
						foreach my $f_potid (split(/;/,$f_potids)){
							push(@{$rtn->{'potype'}},&getPartofType($f_potid));
						}
					}else{
						$rtn->{'potype'} = undef;
					}

					if(defined $rtn->{'c_path'}){
						$rtn->{'c_path'} = undef unless(&exists_buildup_tree($t_type,$f_id,$f_pid));
					}

					push(@{$ITEMS->{'fma'}},$rtn);

					undef $f_potids;
					$f_pid = $f_id;
				}
				if(exists($ITEMS->{'fma'}) && scalar @{$ITEMS->{'fma'}} > 0){
					@{$ITEMS->{'fma'}} = reverse @{$ITEMS->{'fma'}};
					push(@{$HASH->{'partof_path2root'}},$ITEMS);
				}
				undef $t_delcause;
			}
		}else{
			$HASH->{'partof_path2root'} = undef;
		}


		if(scalar @ROUTE_CIRCULAR > 0){
			@ROUTE_CIRCULAR = sort {scalar @$a <=> scalar @$b} sort {$a->[-1]->{'f_id'} cmp $b->[-1]->{'f_id'} } @ROUTE_CIRCULAR;
			$#ROUTE_CIRCULAR = 10 if($#ROUTE_CIRCULAR>10);
			foreach my $route (@ROUTE_CIRCULAR){
				my $ITEMS;
				my $t_delcause;
				my @f_paths;
				my $t_path = "";

				my $rpos=(scalar @$route-1);
				my $rcnt=(scalar @$route-2);
				my $circular_class = "circular";
				$route->[$rpos]->{'circular'} = $circular_class;

#warn "\n\n";
#warn __LINE__,":$route->[$rpos]->{'f_id'},$route->[$rpos]->{'f_potids'},$route->[$rpos]->{'circular'}\n";

				for(;$rcnt>=0;$rcnt--){
					$route->[$rcnt]->{'circular'} = $circular_class;
#warn __LINE__,":$route->[$rcnt]->{'f_id'},$route->[$rcnt]->{'f_potids'},$route->[$rcnt]->{'circular'}\n";
#					$circular_class = undef if($route->[$rpos]->{'f_id'} eq $route->[$rcnt]->{'f_id'} && $route->[$rpos]->{'f_potids'} eq $route->[$rcnt]->{'f_potids'});
					$circular_class = undef if($route->[$rpos]->{'f_id'} eq $route->[$rcnt]->{'f_id'});
				}

				my @TEMP_ROUTE = ();
				for(my $rcnt=0;$rcnt<scalar @$route;$rcnt++){
					my $temp = {
						f_id => $route->[$rcnt]->{'f_id'},
						f_potids => $route->[$rcnt]->{'f_potids'},
						circular => $route->[$rcnt]->{'circular'},
					};
					push(@TEMP_ROUTE,$temp);
				}

				for(my $rcnt=0;$rcnt<(scalar @TEMP_ROUTE-1);$rcnt++){
					$TEMP_ROUTE[$rcnt]->{'f_potids'} = $TEMP_ROUTE[$rcnt+1]->{'f_potids'};
					$TEMP_ROUTE[$rcnt+1]->{'f_potids'} = undef;
				}
				@TEMP_ROUTE = reverse(@TEMP_ROUTE);
				my $f_pid;
				foreach my $temp (@TEMP_ROUTE){
					my $f_id = $temp->{'f_id'};
					push(@f_paths, $f_id);
					my $f_potids = $temp->{'f_potids'};
					$t_path = join('/', @f_paths);
					my $rtn = &getFMA_local($f_id,$t_type);
					unless(defined $t_delcause){
						$t_delcause = $TREE_TYPE{$t_type}->{$f_id}->{'t_delcause'};
						if(!defined $t_delcause && defined $t_path){
							$t_path =~ s/^\///g;
							$rtn->{'c_path'} = $t_path;
						}
					}elsif(exists($TREE_PATH{$t_type}->{$f_id})){
						$rtn->{'c_path'} = $TREE_PATH{$t_type}->{$f_id};
					}else{
						$rtn->{'c_path'} = undef;
					}
					if(defined $f_potids){
						foreach my $f_potid (split(/;/,$f_potids)){
							push(@{$rtn->{'potype'}},&getPartofType($f_potid));
						}
					}else{
						$rtn->{'potype'} = undef;
					}

					if(defined $rtn->{'c_path'}){
						$rtn->{'c_path'} = undef unless(&exists_buildup_tree($t_type,$f_id,$f_pid));
					}


					$rtn->{'circular'} = $temp->{'circular'};
					push(@{$ITEMS->{'fma'}},$rtn);

					undef $f_potids;
					$f_pid = $f_id;
				}
				if(exists($ITEMS->{'fma'}) && scalar @{$ITEMS->{'fma'}} > 0){
					@{$ITEMS->{'fma'}} = reverse @{$ITEMS->{'fma'}};
					push(@{$HASH->{'partof_path2root_circular'}},$ITEMS);
				}
				undef $t_delcause;
			}
#exit;
		}


		$HASH->{'partof_brother'} = !defined $but_cids_hash || exists $but_cids_hash->{$a_fmaid} ? &getPartof_Brother($a_fmaid) : [];
		$HASH->{'partof_brother'} = undef if(scalar @{$HASH->{'partof_brother'}} == 0);
		$HASH->{'partof_children'} = !defined $but_cids_hash || exists $but_cids_hash->{$a_fmaid} ? &getPartof_Children($a_fmaid) : [];
		$HASH->{'partof_children'} = undef if(scalar @{$HASH->{'partof_children'}} == 0);
	}
	push(@{$IMAGES->{'images'}},$HASH);

	undef $name;
}
$sth->finish;

undef $sth;

$IMAGES->{'success'} = JSON::XS::true if(exists $FORM{'callback'} && defined $FORM{'callback'} && length $FORM{'callback'});
#my $json = to_json($IMAGES);
#my $json = &JSON::XS::encode_json($IMAGES);
my $json = &cgi_lib::common::printContentJSON($IMAGES,\%FORM);

print $CACHE_FH $json;
close($CACHE_FH);
chmod 0666,$cache_file;


if($EXISTS_BUILDUP_TREE_count){
	if(open(STORE,"> $store_buildup_tree_file")){
		flock(STORE,2);
		&Storable::store_fd(\%EXISTS_BUILDUP_TREE, *STORE) or die;
		close(STORE);
	}
}
if($FMA_count < scalar keys(%FMA)){
	if(open(STORE,"> $store_fma_file")){
		flock(STORE,2);
		&Storable::store_fd(\%FMA, *STORE) or die;
		close(STORE);
	}
}

#$json = $FORM{'callback'}.qq|($json)| if(exists $FORM{'callback'} && defined $FORM{'callback'} && length $FORM{'callback'});
#print $json;

#print $json;
#print LOG __LINE__,":",$json,"\n";


#close(LOG);

#store \%TREE_PATH, $store_tree_path_file;

rmdir $cache_lock if(-e $cache_lock);
rmdir $store_lock if(-e $store_lock);

#&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(DEBUG);

exit;

