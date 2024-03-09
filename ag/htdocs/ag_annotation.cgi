#!/bp3d/local/perl/bin/perl

$| = 1;

use constant {
	DEBUG => exists $ENV{'AG_DEBUG'} && defined $ENV{'AG_DEBUG'} && $ENV{'AG_DEBUG'} =~ /^[01]$/ ? int($ENV{'AG_DEBUG'}) : 0
};

use strict;
use warnings;
use feature ':5.10';

use File::Basename;
use File::Spec::Functions qw(catdir catfile);
use File::Path;

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI::Cookie;

use Data::Dumper;

use Cwd;
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'API'),&Cwd::abs_path(&catdir($FindBin::Bin,'..','lib')),&Cwd::abs_path(&catdir($FindBin::Bin,'..','..','ag-common','lib'));
use AG::ComDB::Shorturl;
use cgi_lib::common;
use AG::login;

require "common.pl";
require "common_db.pl";
require "common_locale.pl";

if($ENV{REQUEST_METHOD} eq 'GET'){
#	open(LOG,">> $FindBin::Bin/logs/openid.txt");
#	select(LOG);$|=1;
#	select(STDOUT);$|=1;
	&AG::login::openid_login();
#	close(LOG);
}

my $disEnv = &getDispEnv();
my $agInterfaceType = $disEnv->{agInterfaceType};
my $gridHidden = $disEnv->{gridHidden};
my $autoRotationHidden = $disEnv->{autoRotationHidden};
my $addPointElementHidden = $disEnv->{addPointElementHidden};
my $defaultLocaleJa = $disEnv->{defaultLocaleJa};
my $modifyAxisOfRotation = $disEnv->{modifyAxisOfRotation};

$agInterfaceType = '5' unless(defined $agInterfaceType);
$gridHidden = 'false' unless(defined $gridHidden);
$autoRotationHidden = 'false' unless(defined $autoRotationHidden);
$addPointElementHidden = 'false' unless(defined $addPointElementHidden);
$defaultLocaleJa = 'true' unless(defined $defaultLocaleJa);
$modifyAxisOfRotation = 'true' unless(defined $modifyAxisOfRotation);

if(scalar @ARGV == 1 && $ARGV[0] eq "--version"){
	my $prog_file = &File::Basename::basename($0);
	print "\nProgram: $prog_file\n\n";
	foreach my $module (sort keys %INC) {
		my $full_path = $INC{$module};
		my $package = $module;
		$package =~ s/\.p[lm]$//;
		$package =~ s!/!::!g;
		my $version = "";
		eval "\$version = \$${package}::VERSION;";
		$version = "undef" if (!$version);
		printf("%7s %-20s\n", $version, $package);
	}
	exit;
}

my $dbh = &get_dbh();

my %FORM = ();
#&decodeForm(\%FORM);

my %COOKIE = ();
#&getCookie(\%COOKIE);

my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);
&checkXSS(\%FORM);

=pod
my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
my $filetime = sprintf("%04d/%02d/%02d",$year+1900,$mon+1,$mday);
my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);
my $log_dir = &catdir($FindBin::Bin,'logs',$filetime);
if(exists $ENV{'HTTP_X_FORWARDED_FOR'}){
	my @H = split(/,\s*/,$ENV{'HTTP_X_FORWARDED_FOR'});
	$log_dir = &catdir($log_dir,$H[0]);
}elsif(exists $ENV{'REMOTE_ADDR'}){
	$log_dir = &catdir($log_dir,$ENV{'REMOTE_ADDR'});
}
#$COOKIE{'ag_annotation.session'} = &makeSessionID() unless(exists($COOKIE{'ag_annotation.session'}));
$log_dir = &catdir($log_dir,$COOKIE{'ag_annotation.session'}) if(exists $COOKIE{'ag_annotation.session'});
unless(-e $log_dir){
	my $old_umask = umask(0);
	&File::Path::mkpath($log_dir,0,0777);
	umask($old_umask);
}
open(LOG,">> $log_dir/$cgi_name.txt");
flock(LOG,2);
print $LOG "\n[$logtime]:$0\n";
=cut
my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0, qr/\..*$/);
my $LOG = &cgi_lib::common::getLogFH(\%FORM,\%COOKIE);
delete $FORM{_formdata} if(exists($FORM{_formdata}));

#print $LOG __LINE__,":",Dumper($dbh),"\n";

#my $env = SetEnv->new;
#my @BP3DVERSION = ();
#push(@BP3DVERSION,@{$env->{versions}}) if(defined $env->{versions});

if($defaultLocaleJa eq 'true'){
	$FORM{lng} = $COOKIE{"ag_annotation.locale"} if(!exists($FORM{lng}) && exists($COOKIE{"ag_annotation.locale"})); #とりあえず
	$FORM{lng} = "ja" if(exists($FORM{lng}) && $FORM{lng} !~ /^(ja|en:?)$/);
	$FORM{lng} = "ja" unless(exists($FORM{lng}));
}else{
	$FORM{lng} = "en" if(exists($FORM{lng}) && $FORM{lng} !~ /^(ja|en:?)$/);
	$FORM{lng} = "en" unless(exists($FORM{lng}));
}

$FORM{t_type} = 1 unless(exists($FORM{t_type}));
#$FORM{version} = $BP3DVERSION[0] if(!exists($FORM{version}));

$agInterfaceType = '5' if(exists($FORM{tp_md}) && $agInterfaceType ne '5');

$COOKIE{'ag_annotation.session'} = &AG::login::makeSessionID() unless(exists($COOKIE{'ag_annotation.session'}));

if($ENV{REQUEST_METHOD} eq 'POST' && exists($FORM{url})){
	delete $FORM{tp_ap} if(exists $FORM{tp_ap});
	delete $FORM{query} if(exists $FORM{query});
	delete $FORM{fmaid} if(exists $FORM{fmaid});
	delete $FORM{shorten} if(exists $FORM{shorten});
}

my $shorten;
if(exists($FORM{shorten})){
=pod
#	require "common_shorturl.pl";

	my $sth = $dbh->prepare(qq|select sp_original from shorten_param where sp_shorten=?|);
	$sth->execute($FORM{shorten});
	my $column_number = 0;
	my $sp_original;
	$sth->bind_col(++$column_number, \$sp_original, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;
=cut
	$shorten = new AG::ComDB::Shorturl unless(defined $shorten);
	my $sp_original = $shorten->get_long_url($FORM{shorten});

#	print $LOG __LINE__,":\$sp_original=[$sp_original]\n";
	if(defined $sp_original){
		my %hash;
		my @info = split("&",$sp_original);
		foreach my $i (@info){
			$hash{$1} = &url_encode($2) if($i =~ /^([itvm])=(.+)$/);
		}
		if(scalar keys(%hash)>=4 || (exists $hash{i} && defined $hash{i})){
			delete $FORM{shorten};
			foreach my $key (keys(%hash)){
				$FORM{$key} = $hash{$key};
			}
		}
	}
}

#if(exists($FORM{i}) && exists($FORM{t}) && exists($FORM{p}) && exists($FORM{v})){
if(exists($FORM{tp_ap}) || exists($FORM{query}) || exists($FORM{i})){
	my $rtn = &AG::login::clearSession($COOKIE{'ag_annotation.session'});
#	print $LOG __LINE__,":\$rtn=[$rtn]\n";
}

if(exists($FORM{t})){
	if($FORM{t} =~ /^Conventional$/i){
		$FORM{t_type} = 1;
	}elsif($FORM{t} =~ /^is_a$/i || $FORM{t} =~ /^isa$/i){
		$FORM{t_type} = 3;
	}elsif($FORM{t} =~ /^PartOf$/i || $FORM{t} =~ /^Part_Of$/i){
		$FORM{t_type} = 4;
	}else{
		$FORM{t_type} = 1;
	}
	delete $FORM{t};
}
if(exists($FORM{i})){
	$FORM{fmaid} = $FORM{i};
	delete $FORM{i};
}
if(exists($FORM{p})){
	$FORM{txpath} = $FORM{p};
	delete $FORM{p};
}
if(exists($FORM{q})){
	$FORM{query} = $FORM{q};
	delete $FORM{q};
}
if(exists($FORM{v})){
	$FORM{version} = $FORM{v};
	delete $FORM{v};
}
if(exists($FORM{m})){
	my $tg_id;
	my $sth = $dbh->prepare(qq|select tg_id from tree_group where lower(tg_model)=?|);
	$sth->execute(lc($FORM{m}));
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$tg_id, undef);
	$sth->fetch;
	$FORM{tg_id} = $tg_id if(defined $tg_id);
	$sth->finish;
	undef $sth;
	undef $tg_id;
	delete $FORM{m};
}

&setDefParams(\%FORM,\%COOKIE);

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
$COOKIE{"ag_annotation.images.ci_id"}  = $FORM{ci_id}  if(exists $FORM{ci_id}  && defined $FORM{ci_id});
$COOKIE{"ag_annotation.images.cb_id"}  = $FORM{cb_id}  if(exists $FORM{cb_id}  && defined $FORM{cb_id});
$COOKIE{"ag_annotation.images.bul_id"} = $FORM{bul_id} if(exists $FORM{bul_id} && defined $FORM{bul_id});
$COOKIE{"ag_annotation.images.md_id"}  = $FORM{md_id}  if(exists $FORM{md_id}  && defined $FORM{md_id});
$COOKIE{"ag_annotation.images.mv_id"}  = $FORM{mv_id}  if(exists $FORM{mv_id}  && defined $FORM{mv_id});
$COOKIE{"ag_annotation.images.mr_id"}  = $FORM{mr_id}  if(exists $FORM{mr_id}  && defined $FORM{mr_id});

#foreach my $key (sort keys(%FORM)){
#	print $LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}
=pod
if(exists($FORM{version}) && (!exists($FORM{tg_id}) || !exists($FORM{tgi_id}))){
	my $tg_id;
	my $tgi_id;
	my $sth_tree_group_item = $dbh->prepare(qq|select tg_id,tgi_id from tree_group_item where tgi_version=? and tgi_delcause is null|);
	$sth_tree_group_item->execute($FORM{version});
	my $column_number = 0;
	$sth_tree_group_item->bind_col(++$column_number, \$tg_id, undef);
	$sth_tree_group_item->bind_col(++$column_number, \$tgi_id, undef);
	$sth_tree_group_item->fetch;
	if(defined $tg_id && defined $tgi_id){
		$FORM{tg_id} = $tg_id;
		$FORM{tgi_id} = $tgi_id;
		$COOKIE{"ag_annotation.images.tg_id"} = $tg_id;
		print $LOG __LINE__,":\$tg_id=[$tg_id]\n";
	}
	$sth_tree_group_item->finish;
	undef $sth_tree_group_item;
}

my $wt_version;
$wt_version = qq|tg_id=$FORM{tg_id} and tgi_id=$FORM{tgi_id}| if(exists($FORM{tg_id}) && exists($FORM{tgi_id}));
=cut

#DEBUG 常に削除
#delete $FORM{parent} if(exists($FORM{parent}));
my $lsdb_OpenID;
my $lsdb_Auth;
my $lsdb_Config;
my $lsdb_Identity;
my $is_success;
my $parentURL = $FORM{parent} if(exists $FORM{parent} && defined $FORM{parent});
#delete $FORM{parent} if(exists($FORM{parent}));

if(defined $parentURL){
	print $LOG __LINE__,":\n" if(defined $LOG);
	($lsdb_OpenID,$lsdb_Auth,$lsdb_Config) = &openidAuth($parentURL);
}elsif(exists($COOKIE{openid_url}) && exists($COOKIE{openid_session})){
	if(defined $LOG){
		print $LOG __LINE__,":\n";
		print $LOG __LINE__,":\$COOKIE{openid_url}=[$COOKIE{openid_url}]\n" if(defined $COOKIE{openid_url});
		print $LOG __LINE__,":\$COOKIE{openid_session}=[$COOKIE{openid_session}]\n" if(defined $COOKIE{openid_session});
	}
	($lsdb_OpenID,$lsdb_Auth,$lsdb_Config,$lsdb_Identity) = &openidAuthSession($COOKIE{openid_url},$COOKIE{openid_session});
}
$lsdb_Auth = int($lsdb_Auth) if(defined $lsdb_Auth);
if(defined $LOG){
	print $LOG __LINE__,":\$lsdb_OpenID=[$lsdb_OpenID]\n" if(defined $lsdb_OpenID);
	print $LOG __LINE__,":\$lsdb_Auth=[$lsdb_Auth]\n" if(defined $lsdb_Auth);
	print $LOG __LINE__,":\$lsdb_Config=[$lsdb_Config]\n" if(defined $lsdb_Config);
	print $LOG __LINE__,":\$lsdb_Identity=[$lsdb_Identity]\n" if(defined $lsdb_Identity);
}

my $enableDD = 'false';
$enableDD = 'true' if($lsdb_Auth);

my %CONFIG = ();
if(defined $lsdb_Config && $lsdb_Config ne ""){
	&getConfig(\%CONFIG,$lsdb_Config);
	if(!exists($FORM{height})){
		$FORM{height} = $CONFIG{height} if(exists($CONFIG{height}) && !exists($FORM{height}));
		$FORM{page}   = $CONFIG{page}   if(exists($CONFIG{page})   && !exists($FORM{page}));
		$FORM{show}   = $CONFIG{show}   if(exists($CONFIG{show})   && !exists($FORM{show}));
		$FORM{la}     = $CONFIG{la}     if(exists($CONFIG{la})     && !exists($FORM{la}));
		$FORM{query}  = $CONFIG{query}  if(exists($CONFIG{query})  && !exists($FORM{query}));
		$FORM{au}     = $CONFIG{au}     if(exists($CONFIG{au})     && !exists($FORM{au}));
		$FORM{ad}     = $CONFIG{ad}     if(exists($CONFIG{ad})     && !exists($FORM{ad}));
		$FORM{jid}    = $CONFIG{jid}    if(exists($CONFIG{jid})    && !exists($FORM{jid}));
		$FORM{iss}    = $CONFIG{iss}    if(exists($CONFIG{iss})    && !exists($FORM{iss}));
		$FORM{la}     = $CONFIG{la}     if(exists($CONFIG{la})     && !exists($FORM{la}));
		if(exists($CONFIG{dtype}) && !exists($FORM{dtype})){
			$FORM{dtype} = $CONFIG{dtype};
			$FORM{fixed} = $CONFIG{fixed} if(exists($CONFIG{fixed}) && !exists($FORM{fixed}));
		}
	}
}
my %PARENT = ();
&getParent(\%PARENT,$parentURL) if(defined $parentURL);


my $TIME_FORMAT = "Y/m/d H:i:s";

my %LOCALE = &getLocale($FORM{lng});

my $paramObj = {
	lng => $FORM{lng}
};
$paramObj->{parent} = &url_encode($FORM{parent}) if(exists $FORM{parent} && defined $FORM{parent});
$paramObj->{tp_ap}  = &url_encode($FORM{tp_ap}) if(exists $FORM{tp_ap} && defined $FORM{tp_ap});
$paramObj->{tp_md}  = &url_encode($FORM{tp_md}) if(exists $FORM{tp_md} && defined $FORM{tp_md});

=pod
if(!exists($FORM{tp_ap}) && exists($FORM{fmaid}) && !defined $wt_version){
	my $tg_id;
	my $sth_tree_group = $dbh->prepare(qq|select tg_id from tree_group where tg_delcause is null order by tg_order|);
	my $sth_tree_group_item = $dbh->prepare(qq|select tgi_id,tgi_version from tree_group_item where tg_id=? and tgi_delcause is null order by tgi_order|);
	$sth_tree_group->execute();
	my $column_number = 0;
	$sth_tree_group->bind_col(++$column_number, \$tg_id, undef);
	while($sth_tree_group->fetch){
		next unless(defined $tg_id);
		my $tgi_id;
		my $tgi_version;
		$sth_tree_group_item->execute($tg_id);
		my $column_number = 0;
		$sth_tree_group_item->bind_col(++$column_number, \$tgi_id, undef);
		$sth_tree_group_item->bind_col(++$column_number, \$tgi_version, undef);
		while($sth_tree_group_item->fetch){
			next unless(defined $tgi_id && defined $tgi_version);
			my $bp3d_table = &getBP3DTablename($tgi_version);
			next unless(defined $bp3d_table);
			my $sth_bp3d_table = $dbh->prepare(qq|select b_id from $bp3d_table where b_id=? and b_delcause is null|);
			$sth_bp3d_table->execute($FORM{fmaid});
			if($sth_bp3d_table->rows()>0){
				$FORM{tg_id} = $tg_id;
				$COOKIE{"ag_annotation.images.tg_id"} = $tg_id;
				$FORM{tgi_id} = $tgi_id;
				$FORM{version} = $tgi_version;
			}
			$sth_bp3d_table->finish;
			undef $sth_bp3d_table;
			last if(exists($FORM{tg_id}));
		}
		$sth_tree_group_item->finish;
		last if(exists($FORM{tg_id}));
	}
	$sth_tree_group->finish;
	undef $sth_tree_group;
	undef $sth_tree_group_item;

	if(exists($FORM{tg_id}) && exists($FORM{tgi_id}) && exists($FORM{version})){
		$wt_version = qq|tg_id=$FORM{tg_id} and tgi_id=$FORM{tgi_id}| ;
		$COOKIE{"ag_annotation.images.version"} = qq|{"$FORM{tg_id}":"$FORM{version}"}|;
		print &setCookie('ag_annotation.images.version',$COOKIE{"ag_annotation.images.version"}),"\n";
	}else{
		delete $FORM{fmaid};
	}
}
=cut

#print qq|Content-type: text/html; charset=UTF-8\n|;
my @cookies = ();

if((!exists $FORM{tp_ap} || !defined $FORM{tp_ap}) && exists $FORM{fmaid} && defined $FORM{fmaid}){
	my $sql=<<SQL;
select
 bu.ci_id,
 bu.cb_id,
 bu.md_id,
 bu.mv_id,
 bu.mr_id,
 bu.bul_id,
 mv.mr_version,
 cdi.cdi_name,
 bu.rep_id
from
 representation as bu
left join (select * from concept_data_info) as cdi on (cdi.ci_id=bu.ci_id and cdi.cdi_id=bu.cdi_id)
left join (select * from concept_info) as ci on (ci.ci_id=bu.ci_id)
left join (select * from concept_build) as cb on (cb.ci_id=bu.ci_id and cb.cb_id=bu.cb_id)
left join (select * from model) as md on (md.md_id=bu.md_id)
left join (select * from model_revision) as mv on (mv.md_id=bu.md_id and mv.mv_id=bu.mv_id and mv.mr_id=bu.mr_id)
left join (select * from buildup_logic) as bul on (bul.bul_id=bu.bul_id)
where
 bu.rep_delcause is null AND
SQL
	if(&isBLDID($FORM{fmaid})){
		$sql.=<<SQL;
 bu.rep_id=?
SQL
	}else{
		$sql.=<<SQL;
 cdi.cdi_name=?
SQL
	}
	$sql.=<<SQL;
order by
 ci.ci_order,
 cb.cb_order,
 md.md_order,
 mv.mr_order,
 bul.bul_order
limit 1
SQL

	$COOKIE{"ag_annotation.images.ci_id"}  = undef;
	$COOKIE{"ag_annotation.images.cb_id"}  = undef;
	$COOKIE{"ag_annotation.images.bul_id"} = undef;
	$COOKIE{"ag_annotation.images.md_id"}  = undef;
	$COOKIE{"ag_annotation.images.mv_id"}  = undef;
	$COOKIE{"ag_annotation.images.mr_id"}  = undef;

	$FORM{ci_id} = undef;
	$FORM{cb_id} = undef;
	$FORM{bul_id} = undef;
	$FORM{md_id} = undef;
	$FORM{mv_id} = undef;
	$FORM{mr_id} = undef;

	my $ci_id;
	my $cb_id;
	my $md_id;
	my $mv_id;
	my $mr_id;
	my $bul_id;
	my $mv_version;
	my $cdi_name;
	my $rep_id;
	my $sth = $dbh->prepare($sql) or die;
	$sth->execute($FORM{fmaid});
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$ci_id, undef);
	$sth->bind_col(++$column_number, \$cb_id, undef);
	$sth->bind_col(++$column_number, \$md_id, undef);
	$sth->bind_col(++$column_number, \$mv_id, undef);
	$sth->bind_col(++$column_number, \$mr_id, undef);
	$sth->bind_col(++$column_number, \$bul_id, undef);
	$sth->bind_col(++$column_number, \$mv_version, undef);
	$sth->bind_col(++$column_number, \$cdi_name, undef);
	$sth->bind_col(++$column_number, \$rep_id, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;

	$FORM{rep_id} = $rep_id;
	$FORM{ci_id} = $ci_id;
	$FORM{cb_id} = $cb_id;
	$FORM{bul_id} = $bul_id;
	$FORM{t_type} = $bul_id;

	$FORM{md_id} = $md_id;
	$FORM{mv_id} = $mv_id;
	$FORM{mr_id} = $mr_id;
	$FORM{version} = $mv_version;
	$FORM{fmaid} = $cdi_name;

	$COOKIE{"ag_annotation.images.ci_id"} = $ci_id;
	$COOKIE{"ag_annotation.images.cb_id"} = $cb_id;
	$COOKIE{"ag_annotation.images.md_id"} = $md_id;
	$COOKIE{"ag_annotation.images.mv_id"} = $mv_id;
	$COOKIE{"ag_annotation.images.mr_id"} = $mr_id;
	$COOKIE{"ag_annotation.images.bul_id"} = $bul_id;

	if(defined $FORM{md_id} && defined $FORM{mv_id} && defined $FORM{version}){
		$COOKIE{"ag_annotation.images.version"} = qq|{"$FORM{md_id}":"$FORM{version}"}|;
#		print &setCookie('ag_annotation.images.version',$COOKIE{"ag_annotation.images.version"}),"\n";
		push(@cookies,&setCookie('ag_annotation.images.version',$COOKIE{"ag_annotation.images.version"}));

#		print &setCookie('ag_annotation.images.ci_id',$COOKIE{"ag_annotation.images.ci_id"}),"\n" if(defined $COOKIE{"ag_annotation.images.ci_id"});
		push(@cookies,&setCookie('ag_annotation.images.ci_id',$COOKIE{"ag_annotation.images.ci_id"})) if(defined $COOKIE{"ag_annotation.images.ci_id"});
#		print &setCookie('ag_annotation.images.cb_id',$COOKIE{"ag_annotation.images.cb_id"}),"\n" if(defined $COOKIE{"ag_annotation.images.cb_id"});
		push(@cookies,&setCookie('ag_annotation.images.cb_id',$COOKIE{"ag_annotation.images.cb_id"})) if(defined $COOKIE{"ag_annotation.images.cb_id"});
#		print &setCookie('ag_annotation.images.md_id',$COOKIE{"ag_annotation.images.md_id"}),"\n" if(defined $COOKIE{"ag_annotation.images.md_id"});
		push(@cookies,&setCookie('ag_annotation.images.md_id',$COOKIE{"ag_annotation.images.md_id"})) if(defined $COOKIE{"ag_annotation.images.md_id"});
#		print &setCookie('ag_annotation.images.mv_id',$COOKIE{"ag_annotation.images.mv_id"}),"\n" if(defined $COOKIE{"ag_annotation.images.mv_id"});
		push(@cookies,&setCookie('ag_annotation.images.mv_id',$COOKIE{"ag_annotation.images.mv_id"})) if(defined $COOKIE{"ag_annotation.images.mv_id"});
#		print &setCookie('ag_annotation.images.mr_id',$COOKIE{"ag_annotation.images.mr_id"}),"\n" if(defined $COOKIE{"ag_annotation.images.mr_id"});
		push(@cookies,&setCookie('ag_annotation.images.mr_id',$COOKIE{"ag_annotation.images.mr_id"})) if(defined $COOKIE{"ag_annotation.images.mr_id"});
#		print &setCookie('ag_annotation.images.bul_id',$COOKIE{"ag_annotation.images.bul_id"}),"\n" if(defined $COOKIE{"ag_annotation.images.bul_id"});
		push(@cookies,&setCookie('ag_annotation.images.bul_id',$COOKIE{"ag_annotation.images.bul_id"})) if(defined $COOKIE{"ag_annotation.images.bul_id"});
	}else{
		delete $FORM{fmaid};
	}

}



#foreach my $key (sort keys(%FORM)){
#	print $LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}

if(
	!exists($FORM{tp_ap}) &&
	!exists($FORM{query}) &&
	!exists($FORM{fmaid}) &&
	exists($COOKIE{'ag_annotation.session'})
){
	if($ENV{REQUEST_METHOD} eq 'POST' && exists($FORM{url})){
		my $url;
#		require "common_shorturl.pl";
#		if(&isShortUrl($FORM{url})){
		$shorten = new AG::ComDB::Shorturl unless(defined $shorten);
		if($shorten->isShortUrl($FORM{url})){
			my $url_json = $shorten->convert_url($FORM{url});
			my $obj = &JSON::XS::decode_json($url_json);
			if($obj->{data} && $obj->{data}->{expand}){
				if(ref $obj->{data}->{expand} eq "ARRAY"){
					$url = $obj->{data}->{expand}->[0]->{long_url};
				}else{
					$url = $obj->{data}->{expand}->{long_url};
				}
			}
		}else{
			$url = $FORM{url};
		}
		my $index_key = "?";
		my $temp_param = substr($url,index($url,$index_key)+length($index_key));
		$index_key = "tp_ap=";
		$temp_param = &url_decode(substr($temp_param,index($temp_param,$index_key)+length($index_key))) if(index($temp_param,$index_key)>=0);
		my @info = split("&",$temp_param);
		&AG::login::setSession(\@info,&AG::login::getSessionState($COOKIE{'ag_annotation.session'}),&AG::login::getSessionKeymap($COOKIE{'ag_annotation.session'}));

		my $session = &AG::login::getSession($COOKIE{'ag_annotation.session'});
		$FORM{tp_ap} = join("&",@$session) if(defined $session);
		$paramObj->{tp_ap} = &url_encode($FORM{tp_ap}) if(exists($FORM{tp_ap}));

	}elsif(exists($FORM{shorten})){
=pod
		my $sth = $dbh->prepare(qq|select sp_original from shorten_param where sp_shorten=?|);
		$sth->execute($FORM{shorten});
		my $column_number = 0;
		my $sp_original;
		$sth->bind_col(++$column_number, \$sp_original, undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;
=cut
		$shorten = new AG::ComDB::Shorturl unless(defined $shorten);
		my $sp_original = $shorten->get_long_url($FORM{shorten});

		if(defined $sp_original){
			my $index_key = "tp_ap=";
			$sp_original = &url_decode(substr($sp_original,index($sp_original,$index_key)+length($index_key))) if(index($sp_original,$index_key)>=0);
			my @info = split("&",$sp_original);
			&AG::login::setSession(\@info,&AG::login::getSessionState($COOKIE{'ag_annotation.session'}),&AG::login::getSessionKeymap($COOKIE{'ag_annotation.session'}));

			my $session = &AG::login::getSession($COOKIE{'ag_annotation.session'});
			$FORM{tp_ap} = join("&",@$session) if(defined $session);
			$paramObj->{tp_ap} = &url_encode($FORM{tp_ap}) if(exists($FORM{tp_ap}));
		}

	}else{
		my $session = &AG::login::getSession($COOKIE{'ag_annotation.session'});
		$FORM{tp_ap} = join("&",@$session) if(defined $session);
	}
}

###############################################
#JavaScript側で使用する初期値を取得（ここから）
###############################################
my @MODEL_VERSION = ();
{
	my $sql;
	$sql = qq|select mv.md_id,mv.mv_id,mv.mv_version|;
	if($FORM{lng} eq "ja"){
		$sql .= qq|,COALESCE(mv.mv_name_j,mv.mv_name_e)|;
	}else{
		$sql .= qq|,mv.mv_name_e|;
	}
	$sql .= qq| from model_version as mv left join(select * from model) as md on (md.md_id=mv.md_id) where md_use and mv_use and mv_publish and mv.mv_delcause is null order by md.md_order,mv.mv_order|;

	my $md_id;
	my $mv_id;
	my $mv_version;
	my $mv_name;
	my $sth_model_version = $dbh->prepare($sql);
	$sth_model_version->execute();
	my $column_number = 0;
	$sth_model_version->bind_col(++$column_number, \$md_id, undef);
	$sth_model_version->bind_col(++$column_number, \$mv_id, undef);
	$sth_model_version->bind_col(++$column_number, \$mv_version, undef);
	$sth_model_version->bind_col(++$column_number, \$mv_name, undef);
	while($sth_model_version->fetch){
	#	my @TEMP = ($md_id,$mv_id,$tgi_version,$tgi_name);
	#	my @TEMP = ($md_id,$mv_id,$tgi_name,$tgi_name);
		my @TEMP = ($mv_name,$md_id,$mv_id,$mv_version);
		push(@MODEL_VERSION,\@TEMP);
	}
	$sth_model_version->finish;
	undef $sth_model_version;
}

my $init_tree_group = 1;
my $init_bp3d_version = $MODEL_VERSION[0][0];

if(exists($COOKIE{"ag_annotation.images.tg_id"})){
	$init_tree_group = $COOKIE{"ag_annotation.images.tg_id"};
	if(exists($COOKIE{"ag_annotation.images.version"})){
		my $ver =  &JSON::XS::decode_json($COOKIE{"ag_annotation.images.version"});
		$init_bp3d_version = $ver->{$init_tree_group} if($ver && exists($ver->{$init_tree_group}));
	}
}

my $MODEL2TG = {};
my $TG2MODEL = {};
{
	my $tg_id;
	my $tg_model;
	my $tg_delcause;

	my $sql;
	$sql = qq|select distinct md_id,md_abbr,md_delcause from model where md_use|;
	my $sth = $dbh->prepare($sql);
	$sth->execute();
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$tg_id, undef);
	$sth->bind_col(++$column_number, \$tg_model, undef);
	$sth->bind_col(++$column_number, \$tg_delcause, undef);
	while($sth->fetch){
		next unless(defined $tg_id && defined $tg_model);
		$MODEL2TG->{$tg_model} = {
			tg_id       => $tg_id,
			tg_delcause => $tg_delcause,
			md_id       => $tg_id,
			md_delcause => $tg_delcause
		};
		$TG2MODEL->{$tg_id} = {
			tg_model    => $tg_model,
			tg_delcause => $tg_delcause,
			md_abbr     => $tg_model,
			md_delcause => $tg_delcause
		};
	}
	$sth->finish;
	undef $sth;
	undef $tg_id;
	undef $tg_model;
	undef $tg_delcause;
	undef $sql;
}
my $MODEL2TG_DATA = &JSON::XS::encode_json($MODEL2TG);
my $TG2MODEL_DATA = &JSON::XS::encode_json($TG2MODEL);
undef $MODEL2TG;
undef $TG2MODEL;

my $LATESTVER = {};
my $VER2TG = {};
{
	my $tg_id;
	my $tgi_version;
	my $tgi_name;
	my $tgi_delcause;
	my $tgi_port;

	my $sql;
	$sql = qq|select md_id,mv_version|;
	if($FORM{lng} eq "ja"){
		$sql .= qq|,COALESCE(mv_name_j,mv_name_e)|;
	}else{
		$sql .= qq|,mv_name_e|;
	}
	$sql .= qq|,mv_delcause,mv_rep_key from model_version where mv_publish order by md_id,mv_order|;

	my $sth_tree_group_item = $dbh->prepare($sql);
	$sth_tree_group_item->execute();
	my $column_number = 0;
	$sth_tree_group_item->bind_col(++$column_number, \$tg_id, undef);
	$sth_tree_group_item->bind_col(++$column_number, \$tgi_version, undef);
	$sth_tree_group_item->bind_col(++$column_number, \$tgi_name, undef);
	$sth_tree_group_item->bind_col(++$column_number, \$tgi_delcause, undef);
	$sth_tree_group_item->bind_col(++$column_number, \$tgi_port, undef);
	while($sth_tree_group_item->fetch){
		next unless(defined $tg_id && defined $tgi_version && defined $tgi_name);
		$VER2TG->{$tgi_version} = {
			tg_id        => $tg_id,
			tgi_delcause => $tgi_delcause,
			md_id        => $tg_id,
			mv_delcause  => $tgi_delcause
		};
		unless(exists($VER2TG->{$tgi_name})){
			$VER2TG->{$tgi_name} = {
				tg_id        => $tg_id,
				tgi_delcause => $tgi_delcause,
				md_id        => $tg_id,
				mv_delcause  => $tgi_delcause
			};
		}
		$LATESTVER->{$tg_id} = $tgi_name if(defined $tgi_port && !exists($LATESTVER->{$tg_id}) && !defined $tgi_delcause);
	}
	$sth_tree_group_item->finish;
	undef $sth_tree_group_item;
	undef $tg_id;
	undef $tgi_version;
	undef $tgi_delcause;
	undef $sql;
}
my $VER2TG_DATA = &JSON::XS::encode_json($VER2TG);
my $LATESTVER_DATA = &JSON::XS::encode_json($LATESTVER);
###############################################
#JavaScript側で使用する初期値を取得（ここまで）
###############################################

###############################################
#OpenID認証情報？（ここから）
###############################################
#my $user_name = '';
my $login_label = 'Login';
my $login_func = '(window.ag_extensions && ag_extensions.auth && ag_extensions.auth.login) ? ag_extensions.auth.login.createDelegate(ag_extensions.auth) : null';
if(defined $lsdb_OpenID){
	$login_label = qq|Logout|;
	if(defined $lsdb_Identity && defined $lsdb_Identity->{display}){
		$login_label .= qq| - | . $lsdb_Identity->{display};
		my $maxlength = 20;
		$login_label =~ s/^(.{0,$maxlength})\b.*$/$1.../s;

#		$user_name = $lsdb_Identity->{display};
	}else{
		$login_label .= qq| [ $lsdb_OpenID ]|;
	}
	$login_func = '(window.ag_extensions && ag_extensions.auth && ag_extensions.auth.logout) ? ag_extensions.auth.logout.createDelegate(ag_extensions.auth) : null';
}
###############################################
#OpenID認証情報？（ここまで）
###############################################

unless(exists($FORM{tp_ap})){
	if(exists($FORM{query})){
		$paramObj->{query} = &url_encode($FORM{query}) if(exists($FORM{query}));
#		print &setCookie('ag_annotation.images.fmaid',$FORM{fmaid}),"\n" if(exists($FORM{fmaid}));
		push(@cookies,&setCookie('ag_annotation.images.fmaid',$FORM{fmaid})) if(exists($FORM{fmaid}));
#	}elsif(exists($FORM{fmaid}) && defined $wt_version){
	}elsif(exists($FORM{fmaid})){
		my $f_id = $FORM{fmaid};
		my $t_type = $FORM{t_type};
#		print &setCookie('ag_annotation.images.fmaid',$f_id),"\n";
#		print &setCookie('ag_annotation.images.type',$t_type),"\n";
		push(@cookies,&setCookie('ag_annotation.images.fmaid',$f_id));
		push(@cookies,&setCookie('ag_annotation.images.type',$t_type));

		my $types;
		if(exists($COOKIE{'ag_annotation.images.types'})){
			my $types_str = $COOKIE{'ag_annotation.images.types'};
			$types = &JSON::XS::decode_json($types_str) if(defined $types_str && $types_str ne "");
		}
		$types = {} unless(defined $types);
		$types->{$FORM{version}} = $t_type;
#		print &setCookie('ag_annotation.images.types',&JSON::XS::encode_json($types)),"\n";
		push(@cookies,&setCookie('ag_annotation.images.types',&JSON::XS::encode_json($types)));
		if(exists($FORM{position}) && $FORM{position} =~ /^(rotate|front|back|left|right:?)$/){
#			print &setCookie('ag_annotation.images.position',$FORM{position}),"\n";
			push(@cookies,&setCookie('ag_annotation.images.position',$FORM{position}));
		}

		$paramObj->{fmaid} = &url_encode($FORM{fmaid}) if(exists($FORM{fmaid}));
		unless(exists($FORM{txpath})){
			my $sth_count = $dbh->prepare(qq|select cdi_name from view_buildup_tree where md_id=$FORM{md_id} and mv_id=$FORM{mv_id} and mr_id=$FORM{mr_id} and ci_id=$FORM{ci_id} and cb_id=$FORM{cb_id} and bul_id=$FORM{bul_id} and cdi_pname=?|);
			$sth_count->execute($f_id);
			my $cnum = $sth_count->rows();
			$sth_count->finish;
			undef $sth_count;
#print $LOG __LINE__,":\$cnum=[$cnum]\n";
			my @TREE_ROUTE = ();
			if($cnum>0){
				&getTree_Path2Root(\%FORM,$f_id,\@TREE_ROUTE);
			}else{
				my $sth_tree_p = $dbh->prepare(qq|select cdi_pname,but_delcause from view_buildup_tree where md_id=$FORM{md_id} and mv_id=$FORM{mv_id} and mr_id=$FORM{mr_id} and ci_id=$FORM{ci_id} and cb_id=$FORM{cb_id} and bul_id=$FORM{bul_id} and cdi_name=?|);
				my @TREE_PID = ();
				$sth_tree_p->execute($f_id);
#print $LOG __LINE__,":\$sth_tree_p->rows=[",$sth_tree_p->rows(),"]\n";
				if($sth_tree_p->rows>0){
					my $f_pid;
					my $t_delcause;
					my $column_number = 0;
					$sth_tree_p->bind_col(++$column_number, \$f_pid, undef);
					$sth_tree_p->bind_col(++$column_number, \$t_delcause, undef);
					while($sth_tree_p->fetch){
						next if(defined $t_delcause);
						push(@TREE_PID,$f_pid);
					}
				}
				$sth_tree_p->finish;
				undef $sth_tree_p;
				if(scalar @TREE_PID > 0){
					foreach my $f_pid (@TREE_PID){
						&getTree_Path2Root(\%FORM,$f_pid,\@TREE_ROUTE);
						last if(scalar @TREE_ROUTE > 100);
					}
				}
			}
			if(scalar @TREE_ROUTE > 0){
#				@TREE_ROUTE = sort {scalar (split(/\t/,$a)) <=> scalar (split(/\t/,$b)) } sort @TREE_ROUTE;
				@TREE_ROUTE = sort {
					my @A = split(/\t/,$a);
					my @B = split(/\t/,$b);
					scalar @A <=> scalar @B
				} sort @TREE_ROUTE;
				my $route = shift @TREE_ROUTE;
				my @FIDS = reverse(split(/\t/,$route));
				pop @FIDS if($FIDS[$#FIDS] eq $f_id);
				$FORM{txpath} = "/" . join("/",@FIDS);
			}
		}
#		print &setCookie('ag_annotation.images.path',$FORM{txpath}),"\n" if(exists($FORM{txpath}));
		push(@cookies,&setCookie('ag_annotation.images.path',$FORM{txpath})) if(exists($FORM{txpath}));
	}
}else{

#	print $LOG __LINE__,":\$FORM{tp_ap}=[",$FORM{tp_ap},"]\n";
	my %TP_AP = map { my @a = split(/=/); $a[0] => $a[1] } split("&",$FORM{tp_ap});

#	print $LOG __LINE__,":",Dumper(\%TP_AP),"\n";

#=pod

	if(exists $TP_AP{bv} && defined $TP_AP{bv} && length $TP_AP{bv}){
		my $sql =<<SQL;
select
 mv_name_e
from
 model_version
where
 mv_name_e=? or ?=ANY(mv_name_alias)
SQL
		my @bind_values;
		push(@bind_values, $TP_AP{bv});
		push(@bind_values, $TP_AP{bv});
		my $sth_model_version = $dbh->prepare($sql);
		$sth_model_version->execute(@bind_values);
		my $column_number = 0;
		my $mv_name_e;
		$sth_model_version->bind_col(++$column_number, \$mv_name_e, undef);
		$sth_model_version->fetch;
		$sth_model_version->finish;
		undef $sth_model_version;
		if(defined $mv_name_e){
			$TP_AP{bv} = $mv_name_e;
			my @P;
			push(@P,"$_=$TP_AP{$_}")for(keys(%TP_AP));
			$FORM{tp_ap} = join('&',@P);
		}
	}

	if(exists($TP_AP{bv}) && exists($TP_AP{tn})){
		my $types;
		if(exists($COOKIE{'ag_annotation.images.types'})){
			my $types_str = $COOKIE{'ag_annotation.images.types'};

			$types = &JSON::XS::decode_json($types_str) if($types_str ne "");
		}
		$types = {} unless(defined $types);
		if($TP_AP{tn} eq "isa"){
			$types->{$TP_AP{bv}} = '3';
		}elsif($TP_AP{tn} eq "partof"){
			$types->{$TP_AP{bv}} = '4';
		}else{
			$types->{$TP_AP{bv}} = '1';
		}

#		print &setCookie('ag_annotation.images.types',&JSON::XS::encode_json($types)),"\n";
		push(@cookies,&setCookie('ag_annotation.images.types',&JSON::XS::encode_json($types)));
	}
	if(exists($TP_AP{bv})){
		my $versions;
		if(exists($COOKIE{'ag_annotation.images.version'})){
			my $str = $COOKIE{'ag_annotation.images.version'};
	#		$versions = from_json($str) if($str ne "");
			$versions = decode_json($str) if($str ne "");
		}
		$versions = {} unless(defined $versions);
		$versions->{$init_tree_group} = $TP_AP{bv};

#		print &setCookie('ag_annotation.images.version',&JSON::XS::encode_json($versions)),"\n";
		push(@cookies,&setCookie('ag_annotation.images.version',&JSON::XS::encode_json($versions)));
	}

}

#print &setCookie('ag_annotation.locale',$FORM{lng}),"\n" if(exists($FORM{lng}));
push(@cookies,&setCookie('ag_annotation.locale',$FORM{lng})) if(exists($FORM{lng}));
#print &setCookie('ag_annotation.session',$COOKIE{'ag_annotation.session'})," HttpOnly\n" if(exists($COOKIE{'ag_annotation.session'}));
push(@cookies,&setCookie('ag_annotation.session',$COOKIE{'ag_annotation.session'}).' HttpOnly') if(exists($COOKIE{'ag_annotation.session'}));
#print &setCookie('ag_annotation.images.tg_id',$COOKIE{'ag_annotation.images.tg_id'}),"\n" if(exists($COOKIE{'ag_annotation.images.tg_id'}));
push(@cookies,&setCookie('ag_annotation.images.tg_id',$COOKIE{'ag_annotation.images.tg_id'})) if(exists($COOKIE{'ag_annotation.images.tg_id'}));
#print qq|\n|;

if(&isIPHONE() && -e qq|iphone/main.pl|){
	require "iphone/main.pl";
	return;
}
#close(LOG);

my $param="";
my @paramArr=();
foreach my $key (sort keys %$paramObj){
	next if($key eq 'tp_ap');
	push(@paramArr,qq|$key=$paramObj->{$key}|);
}
$param='&'.join("&",@paramArr) if(scalar @paramArr > 0);
undef @paramArr;
undef $paramObj;

my $EXT_PATH = "ext-2.2.1";
#my $EXT_PATH = "ext-2.3.0";
#my $EXT_PATH = "ext-3.0.3";

my @CSS = (
	"$EXT_PATH/resources/css/ext-all.css",
#	"resources/css/xtheme-vista.css",
);
my @CSS2 = (
	"css/color-picker.ux.css",
	"css/ColorField.css",
	"css/main.css",
	"css/examples.css",
	"css/chooser.css",
	"css/file-upload.css",
	"css/column-tree.css",
	"css/samples.css",
	"css/base.css",
	"css/feedback.css",
	"css/comment.css",
	"css/anatomography.css",
	"css/IncrementalSearchField.css",
	"css/openid.css",
	"css/twitter.css",
	"css/global-pin.css",
	"css/pick-point.css"
);
unless(DEBUG){
	my $ag_css = qq|css/ag-all.css|;
	unlink $ag_css if(-e $ag_css && (stat($ag_css))[9]<(stat($0))[9]);
	if(-e $ag_css){
		foreach my $css (@CSS2){
			next unless(-e $css && -s $css);
			unlink $ag_css if((stat($ag_css))[9]<(stat($css))[9]);
			last unless(-e $ag_css);
		}
	}
	unless(-e $ag_css){
		if(open(my $OUT,'>',$ag_css)){
			local $/;
			foreach my $css (@CSS2){
				next unless(-e $css && -s $css);
				if(open(my $IN,$css)){
					my $D = <$IN>;
					close($IN);
					print $OUT $D;
				}
			}
			close($OUT);
			chmod 0600,$ag_css;
		}
	}
	if(-e $ag_css){
		push(@CSS,$ag_css);
	}else{
		push(@CSS,@CSS2);
	}
}else{
	push(@CSS,@CSS2);
}
my @JS = (
	"js/jquery.min.js",
	"$EXT_PATH/adapter/ext/ext-base.js",

#	"$EXT_PATH/adapter/jquery/jquery.js",
#	"$EXT_PATH/adapter/jquery/ext-jquery-adapter.js",

#	"$EXT_PATH/ext-all.js",
#	"$EXT_PATH/ext-all-debug-min.js",

	"$EXT_PATH/ext-all-debug.js",
);
push(@JS,"js/ext-lang-ja.js") if(exists($FORM{lng}) && $FORM{lng} eq "ja");
push(@JS,

	"js/FileUploadField.js",
	"js/SearchField.js",
	"js/SearchFieldStore.js",
	"js/SearchFMAStore.js",
	"js/SearchFieldListeners.js",
	"js/ColumnNodeUI.js",
	"js/custom.js",
	"js/states.js",
	"js/data-view-plugins.js",
	"js/color-picker.ux.js",
	"js/ColorField.js",
	"js/ColorPickerField.js",
	"js/TextFieldItem.js",
	"js/IncrementalSearchField.js",

	"js/menu/EditableItem.js",
	"js/menu/RangeMenu.js",

	"js/grid/GridFilters.js",
	"js/grid/filter/Filter.js",
	"js/grid/filter/StringFilter.js",
	"js/grid/filter/DateFilter.js",
	"js/grid/filter/ListFilter.js",
	"js/grid/filter/NumericFilter.js",
	"js/grid/filter/BooleanFilter.js",

	"ag_js/ag_copyright.js",

	"ag_js/cgi/ag_lang_$FORM{lng}.js",
	"ag_js/extensions/single-pin.js",
	"ag_js/extensions/url2text.js",
	"ag_js/extensions/import-parts-pins.js",
#	"ag_js/extensions/global-pin.js",
#	"ag_js/extensions/auth.js",
	"ag_js/extensions/tojson.js",
	"ag_js/extensions/pick-point.js",
	"ag_js/extensions/pallet-element.js",
	"ag_js/extensions/data-drop.js",

	"ag_js/ag.js",
	"ag_js/cgi/ag_common_$FORM{lng}.js",
	"ag_js/cgi/ag_annotation_$FORM{lng}.js",
	"ag_js/cgi/anatomography_$FORM{lng}.js",

	"ag_js/ag_init.js"
);

my @JS2 = ();

foreach my $cgi_target (qw/ag_lang_js.cgi ag_common_js.cgi ag_annotation_js.cgi anatomography_js.cgi/){
	my $cgi_path = &catfile($cgi_dir,$cgi_target);
	my $common_pl_path = &catfile($cgi_dir,'common.pl');
	my $js_basename = $cgi_target;
	$js_basename =~ s/js\.cgi$//g;
	foreach my $lng (qw/en ja/){
		my $js_path = &catfile($cgi_dir,'ag_js','cgi',qq|$js_basename$lng.js|);
		next unless(-e $cgi_path && (!-e $js_path || -z $js_path || (stat($js_path))[9]<(stat($cgi_path))[9] || (stat($js_path))[9]<(stat($common_pl_path))[9]));
		print $LOG __LINE__.":\$cmd=[".qq|unset REQUEST_METHOD;echo "// $cgi_pathより自動生成"> $js_path;$cgi_path lng=$lng >> $js_path|."]\n" if(defined $LOG);
		system(qq|unset REQUEST_METHOD;echo "// $cgi_pathより自動生成"> $js_path;$cgi_path lng=$lng >> $js_path|);
		chmod 0600,$js_path if(-e $js_path);
	}
}
unless(DEBUG){
	my $ag_js = qq|ag_js/ag-all-$FORM{lng}.js|;
	unlink $ag_js if(-e $ag_js && (stat($ag_js))[9]<(stat($0))[9]);
	if(-e $ag_js){
		foreach my $js (@JS){
			next unless(-e $js && -s $js);
			unlink $ag_js if((stat($ag_js))[9]<(stat($js))[9]);
			last unless(-e $ag_js);
		}
	}
	unless(-e $ag_js){
		if(open(my $OUT,'>',$ag_js)){
			local $/;
			foreach my $js (@JS){
				next unless(-e $js && -s $js);
				if(open(my $IN,$js)){
					my $D = <$IN>;
					close($IN);
					print $OUT $D;
				}
			}
			close($OUT);
			chmod 0600,$ag_js;
		}
	}
	@JS = ($ag_js) if(-e $ag_js);
}
=pod
my $lng_cgi = &catfile($cgi_dir,'ag_lang_js.cgi');
foreach my $lng (qw/en ja/){
	my $lng_js = &catfile($cgi_dir,'ag_js',qq|ag_lang_$lng.js|);
	system(qq|unset REQUEST_METHOD;$lng_cgi lng=$lng > $lng_js|) if(-e $lng_cgi && (!-e $lng_js || -z $lng_js || (stat($lng_js))[9]<(stat($lng_cgi))[9]));
	chmod 0600,$lng_js if(-e $lng_js);
}

my $lng_cgi = &catfile($cgi_dir,'ag_common_js.cgi');
foreach my $lng (qw/en ja/){
	my $lng_js = &catfile($cgi_dir,'ag_js',qq|ag_common_$lng.js|);
	system(qq|unset REQUEST_METHOD;$lng_cgi lng=$lng > $lng_js|) if(-e $lng_cgi && (!-e $lng_js || -z $lng_js || (stat($lng_js))[9]<(stat($lng_cgi))[9]));
	chmod 0600,$lng_js if(-e $lng_js);
}

my $lng_cgi = &catfile($cgi_dir,'ag_annotation_js.cgi');
foreach my $lng (qw/en ja/){
	my $lng_js = &catfile($cgi_dir,'ag_js',qq|ag_annotation_$lng.js|);
	system(qq|unset REQUEST_METHOD;$lng_cgi lng=$lng > $lng_js|) if(-e $lng_cgi && (!-e $lng_js || -z $lng_js || (stat($lng_js))[9]<(stat($lng_cgi))[9]));
	chmod 0600,$lng_js if(-e $lng_js);
}

my $lng_cgi = &catfile($cgi_dir,'anatomography_js.cgi');
foreach my $lng (qw/en ja/){
	my $lng_js = &catfile($cgi_dir,'ag_js',qq|anatomography_$lng.js|);
	system(qq|unset REQUEST_METHOD;$lng_cgi lng=$lng > $lng_js|) if(-e $lng_cgi && (!-e $lng_js || -z $lng_js || (stat($lng_js))[9]<(stat($lng_cgi))[9]));
	chmod 0600,$lng_js if(-e $lng_js);
}
=cut

my @JS_PARAM = ();

my @JS_PARAM2 = (
#	"ag_common_js.cgi",
#	"ag_annotation_js.cgi",
#	"anatomography_js.cgi",
);


#my $java = qq|/usr/bin/java|;
#my $yui = qq|/bp3d/local/yuicompressor-2.4.6/yuicompressor-2.4.6.jar|;
#my $mini_ext = qq|.min|;

my $CONTENTS =<<HTML;
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja">
<head>
<meta http-equiv="X-UA-Compatible" content="IE=EmulateIE7" />
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta http-equiv="Content-Style-Type" content="text/css" />
<meta http-equiv="Content-Script-Type" content="text/javascript" />
<meta name="Description" content="$LOCALE{BP3D_DESCRIPTION}">
HTML

my $favicon = qq|favicon.ico|;
$CONTENTS .= qq|<link rel="shortcut icon" href="favicon.ico" type="image/vnd.microsoft.icon">\n| if(defined $favicon && -e $favicon && -s $favicon);

=pod
foreach my $css (@CSS){
	next unless(-e $css);
	unless(DEBUG){
		my($css_name,$css_dir,$css_ext) = &File::Basename::fileparse($css,qw/.min.css .css/);
		if($css_ext eq '.css'){
			my $mini_css = &catfile($css_dir,$css_name.$mini_ext.$css_ext);
			if(-w $css_dir){
				unlink $mini_css if(-e $mini_css && (stat($css))[9]>(stat($mini_css))[9]);
				unless(-e $mini_css){
					system(qq|$java -jar $yui --type css --nomunge -o $mini_css $css|) if(-e $java && -e $yui);
					chmod 0600,$mini_css if(-e $mini_css);
				}
			}
			$css = $mini_css if(-e $mini_css);
		}
	}
	my $mtime = (stat($css))[9];
	print qq|<link rel="stylesheet" href="$css?$mtime" type="text/css" media="all" charset="UTF-8">\n|;
}
=cut
$CONTENTS .= &cgi_lib::common::yuiCSS(\@CSS);


$CONTENTS .= <<HTML;
<!--[if IE ]>
<link rel="stylesheet" href="css/ie.css" type="text/css" media="all">
<![endif]-->

<!-- Javascript -->
HTML
=pod
foreach my $js (@JS){
	next unless(-e $js);
	unless(DEBUG){
		my($js_name,$js_dir,$js_ext) = &File::Basename::fileparse($js,qw/.min.js .js/);
		if($js_ext eq '.js'){
			my $mini_js = &catfile($js_dir,$js_name.$mini_ext.$js_ext);
			if(-w $js_dir){
				unlink $mini_js if(-e $mini_js && (stat($js))[9]>(stat($mini_js))[9]);
				unless(-e $mini_js){
					system(qq|$java -jar $yui --type js --nomunge -o $mini_js $js|) if(-e $java && -e $yui);
					chmod 0600,$mini_js if(-e $mini_js);
				}
			}
			$js = $mini_js if(-e $mini_js);
		}
	}
	my $mtime = (stat($js))[9];
	print qq|<script type="text/javascript" src="$js?$mtime"></script>\n|;
}
=cut
if(DEBUG){
	foreach my $js (@JS){
		next unless(-e $js);
		my $mtime = (stat($js))[9];
		$CONTENTS .= qq|<script type="text/javascript" src="$js?$mtime"></script>\n|;
	}
}else{
	$CONTENTS .= &cgi_lib::common::yuiJS(\@JS,\%FORM);
}

foreach my $js (@JS_PARAM){
	next unless(-e $js);
	my $mtime = (stat($js))[9];
	$CONTENTS .= qq|<script type="text/javascript" src="$js?$mtime$param"></script>\n|;
}
=pod
foreach my $js (@JS2){
	next unless(-e $js);
	unless(DEBUG){
		my($js_name,$js_dir,$js_ext) = &File::Basename::fileparse($js,qw/.min.js .js/);
		if($js_ext eq '.js'){
			my $mini_js = &catfile($js_dir,$js_name.$mini_ext.$js_ext);
			if(-w $js_dir){
				unlink $mini_js if(-e $mini_js && (stat($js))[9]>(stat($mini_js))[9]);
				unless(-e $mini_js){
					system(qq|$java -jar $yui --type js --nomunge -o $mini_js $js|) if(-e $java && -e $yui);
					chmod 0600,$mini_js if(-e $mini_js);
				}
			}
			$js = $mini_js if(-e $mini_js);
		}
	}
	my $mtime = (stat($js))[9];
	print qq|<script type="text/javascript" src="$js?$mtime"></script>\n|;
}
=cut
$CONTENTS .= &cgi_lib::common::yuiJS(\@JS2,\%FORM);
foreach my $js (@JS_PARAM2){
	next unless(-e $js);
	my $mtime = (stat($js))[9];
	$CONTENTS .= qq|<script type="text/javascript" src="$js?$mtime$param"></script>\n|;
}
$CONTENTS .= <<HTML;
<title>$LOCALE{DOCUMENT_TITLE}</title>
<style type="text/css">
HTML
my $CSS_CONTENTS = <<HTML;
#img-detail-panel-xcollapsed {
HTML
if(exists($FORM{lng}) && $FORM{lng} eq "ja"){
#	print qq|  background: transparent url(css/img_detail_title_collapsed_ja.png) no-repeat 4px 22px;\n|;
}else{
#	print qq|  background: transparent url(css/img_detail_title_collapsed_en.png) no-repeat 5px 22px;\n|;
}
$CSS_CONTENTS .= <<HTML;
}
#anatomography_comment-xcollapsed {
HTML
if(exists($FORM{lng}) && $FORM{lng} eq "ja"){
#	print qq|  background: transparent url(css/anatomo_comment_title_collapsed_ja.png) no-repeat 4px 22px;\n|;
}else{
#	print qq|  background: transparent url(css/anatomo_comment_title_collapsed_en.png) no-repeat 5px 22px;\n|;
}
$CSS_CONTENTS .= <<HTML;
}
/*
div#navigate-range-panel div.x-form-item.x-hide-label {
	display: none;
}
div#navigate-position-panel div.x-form-item.x-hide-label {
	display: none;
}
*/
HTML

$CSS_CONTENTS = &cgi_lib::common::css_compress($CSS_CONTENTS);


$CONTENTS .= <<HTML;
$CSS_CONTENTS
</style>
HTML




$CONTENTS .=<<HTML;
<script type="text/javascript"><!--
HTML
my $JS_CONTENTS =<<HTML;
model2tg = $MODEL2TG_DATA;
tg2model = $TG2MODEL_DATA;
version2tg = $VER2TG_DATA;
latestversion = $LATESTVER_DATA;
init_tree_group = $init_tree_group;
init_bp3d_version = '$init_bp3d_version';

window.bp3d = window.bp3d || {};
bp3d.defaults = bp3d.defaults || {};
bp3d.defaults.TIME_FORMAT = "Y/m/d H:i:s";
bp3d.defaults.DATE_FORMAT = "Y/m/d";
bp3d.defaults.bp3d_version = init_bp3d_version;

gAuthTBButton = {
	text    : '$login_label',
	icon    : 'css/openid-bg.gif',
	cls     : 'x-btn-text-icon',
	handler : $login_func
};

_dump("\\n\\nSTART!!\\n\\n");
//_dump("cgipath.animation=["+cgipath.animation+"]");
var gParams = {};
HTML
if($ENV{REQUEST_METHOD} eq 'GET'){
	$JS_CONTENTS .= <<HTML;
//try{
//	gParams = Ext.urlDecode(window.location.search.substring(1));
//}catch(e){
HTML
	foreach my $key (sort keys(%FORM)){
		my $value = defined $FORM{$key} ? $FORM{$key} : '';
		$value =~ s/[^\\]"/\\"/g;
		$value =~ s/[\r\n]+//g;
		$JS_CONTENTS .= <<HTML;
	gParams.$key = "$value";
HTML
	}
	$JS_CONTENTS .= <<HTML;
//}
HTML
}else{
	foreach my $key (sort keys(%FORM)){
		my $value = defined $FORM{$key} ? $FORM{$key} : '';
		$value =~ s/[^\\]"/\\"/g;
		$value =~ s/[\r\n]+//g;
		$JS_CONTENTS .= <<HTML;
gParams.$key = "$value";
HTML
	}
}
$JS_CONTENTS .= qq|if(Ext.isEmpty(gParams.fmaid))   gParams.fmaid='$FORM{fmaid}';\n|   if(exists $FORM{fmaid} && defined $FORM{fmaid});
$JS_CONTENTS .= qq|if(Ext.isEmpty(gParams.txpath))  gParams.txpath='$FORM{txpath}';\n| if(exists $FORM{txpath} && defined $FORM{txpath});
$JS_CONTENTS .= qq|if(Ext.isEmpty(gParams.t_type))  gParams.t_type='$FORM{t_type}';\n| if(exists $FORM{t_type} && defined $FORM{t_type});
$JS_CONTENTS .= qq|if(Ext.isEmpty(gParams.version)) gParams.version='$FORM{version}';\n| if(exists $FORM{version} && defined $FORM{version});
$JS_CONTENTS .= qq|if(Ext.isEmpty(gParams.query)) gParams.query='$FORM{query}';\n| if(exists $FORM{query} && defined $FORM{query});
$JS_CONTENTS .= qq|if(!Ext.isEmpty(gParams.version)) init_bp3d_version=gParams.version;\n|;

if(exists($FORM{tp_ap}) && exists($COOKIE{'ag_annotation.session'})){
	my $value = $FORM{tp_ap};
	$value =~ s/[^\\]"/\\"/g;
	$value =~ s/[\r\n]+//g;
	$JS_CONTENTS .= <<HTML;
if(Ext.isEmpty(gParams.tp_ap)) gParams.tp_ap="$value";
HTML
}
$JS_CONTENTS .= <<HTML;
if(Ext.isEmpty(gParams.lng)) gParams.lng = '$FORM{lng}';
if(!Ext.isEmpty(gParams.tp_md)){
	gParams.tp_md = parseInt(gParams.tp_md);
}else if(!Ext.isEmpty(gParams.tp_ap) && (window.top != window || is_iPad())){
	gParams.tp_md = 1;
	gParams.tp_ct = 1;
	gParams.tp_bt = 1;
	gParams.tp_ro = 1;
	gParams.tp_gr = 1;
	gParams.tp_zo = 1;
}
HTML

$JS_CONTENTS = &cgi_lib::common::js_compress($JS_CONTENTS);

$CONTENTS .= <<HTML;
$JS_CONTENTS
// --></script>
</head>
<body>
HTML
if(&isCrawler()){

	my $column_number = 0;

	if(
		exists $FORM{rep_id} && defined $FORM{rep_id} &&
		exists $FORM{ci_id} && defined $FORM{ci_id} &&
		exists $FORM{cb_id} && defined $FORM{cb_id} &&
		exists $FORM{bul_id} && defined $FORM{bul_id} &&
		exists $FORM{md_id} && defined $FORM{md_id} &&
		exists $FORM{mv_id} && defined $FORM{mv_id} &&
		exists $FORM{mr_id} && defined $FORM{mr_id} &&
		exists $FORM{version} && defined $FORM{version} &&
		exists $FORM{fmaid} && defined $FORM{fmaid}
	){
		my $md_name_e;
		my $mv_name_e;
		my $ci_name;
		my $cb_name;
		my $bul_name_e;

		my $sth_model = $dbh->prepare(qq|select md_name_e from model where md_id=?|);
		$sth_model->execute($FORM{md_id});
		$column_number = 0;
		$sth_model->bind_col(++$column_number, \$md_name_e, undef);
		$sth_model->fetch;
		$sth_model->finish;
		undef $sth_model;

		my $sth_model_version = $dbh->prepare(qq|select mv_name_e from model_version where md_id=? and mv_id=?|);
		$sth_model_version->execute($FORM{md_id},$FORM{mv_id});
		$column_number = 0;
		$sth_model_version->bind_col(++$column_number, \$mv_name_e, undef);
		$sth_model_version->fetch;
		$sth_model_version->finish;
		undef $sth_model_version;

		my $sth_concept_info = $dbh->prepare(qq|select ci_name from concept_info where ci_id=?|);
		$sth_concept_info->execute($FORM{ci_id});
		$column_number = 0;
		$sth_concept_info->bind_col(++$column_number, \$ci_name, undef);
		$sth_concept_info->fetch;
		$sth_concept_info->finish;
		undef $sth_concept_info;

		my $sth_concept_build = $dbh->prepare(qq|select cb_name from concept_build where ci_id=? and cb_id=?|);
		$sth_concept_build->execute($FORM{ci_id},$FORM{cb_id});
		$column_number = 0;
		$sth_concept_build->bind_col(++$column_number, \$cb_name, undef);
		$sth_concept_build->fetch;
		$sth_concept_build->finish;
		undef $sth_concept_build;

		my $sth_buildup_logic = $dbh->prepare(qq|select bul_name_e from buildup_logic where bul_id=?|);
		$sth_buildup_logic->execute($FORM{bul_id});
		$column_number = 0;
		$sth_buildup_logic->bind_col(++$column_number, \$bul_name_e, undef);
		$sth_buildup_logic->fetch;
		$sth_buildup_logic->finish;
		undef $sth_buildup_logic;

		my $sql=<<SQL;
select
 rep_id,
 rep_xmin,
 rep_xmax,
 rep_ymin,
 rep_ymax,
 rep_zmin,
 rep_zmax,
 rep_volume,
 rep_density_objs,
 rep_density_ends,
 rep_primitive,
 cdi_name,
 cdi_name_j,
 cdi_name_e,
 cdi_name_k,
 cdi_name_l,
 cdi_syn_j,
 cdi_syn_e,
 cdi_def_j,
 cdi_def_e,
 cdi_taid
from
 view_representation
where
 rep_delcause is null AND
 rep_id=?
SQL

		my $rep_id;
		my $rep_xmin;
		my $rep_xmax;
		my $rep_ymin;
		my $rep_ymax;
		my $rep_zmin;
		my $rep_zmax;
		my $rep_volume;
		my $rep_density_objs;
		my $rep_density_ends;
		my $rep_primitive;
		my $cdi_name;
		my $cdi_name_j;
		my $cdi_name_e;
		my $cdi_name_k;
		my $cdi_name_l;
		my $cdi_syn_j;
		my $cdi_syn_e;
		my $cdi_def_j;
		my $cdi_def_e;
		my $cdi_taid;

		my $sth_rep = $dbh->prepare($sql);
		$sth_rep->execute($FORM{rep_id});
		if($sth_rep->rows()>0){
			my $HTML=<<HTML;
<table border="1" cellspacing="0" style="display:;"><tbody>
<caption>$md_name_e,$mv_name_e,$ci_name,$cb_name,$bul_name_e</caption>
HTML
			$column_number = 0;
			$sth_rep->bind_col(++$column_number, \$rep_id, undef);
			$sth_rep->bind_col(++$column_number, \$rep_xmin, undef);
			$sth_rep->bind_col(++$column_number, \$rep_xmax, undef);
			$sth_rep->bind_col(++$column_number, \$rep_ymin, undef);
			$sth_rep->bind_col(++$column_number, \$rep_ymax, undef);
			$sth_rep->bind_col(++$column_number, \$rep_zmin, undef);
			$sth_rep->bind_col(++$column_number, \$rep_zmax, undef);

			$sth_rep->bind_col(++$column_number, \$rep_volume, undef);
			$sth_rep->bind_col(++$column_number, \$rep_density_objs, undef);
			$sth_rep->bind_col(++$column_number, \$rep_density_ends, undef);
			$sth_rep->bind_col(++$column_number, \$rep_primitive, undef);

			$sth_rep->bind_col(++$column_number, \$cdi_name, undef);
			$sth_rep->bind_col(++$column_number, \$cdi_name_j, undef);
			$sth_rep->bind_col(++$column_number, \$cdi_name_e, undef);
			$sth_rep->bind_col(++$column_number, \$cdi_name_k, undef);
			$sth_rep->bind_col(++$column_number, \$cdi_name_l, undef);

			$sth_rep->bind_col(++$column_number, \$cdi_syn_j, undef);
			$sth_rep->bind_col(++$column_number, \$cdi_syn_e, undef);
			$sth_rep->bind_col(++$column_number, \$cdi_def_j, undef);
			$sth_rep->bind_col(++$column_number, \$cdi_def_e, undef);
			$sth_rep->bind_col(++$column_number, \$cdi_taid, undef);

			while($sth_rep->fetch){
				next unless(defined $rep_id);

				$cdi_name_j =~ s/[;\|]+/,/g if(defined $cdi_name_j);
				$cdi_name_e =~ s/[;\|]+/,/g if(defined $cdi_name_e);
				$cdi_name_k =~ s/[;\|]+/,/g if(defined $cdi_name_k);
				$cdi_name_l =~ s/[;\|]+/,/g if(defined $cdi_name_l);
				$cdi_syn_j  =~ s/[;\|]+/,/g if(defined $cdi_syn_j);
				$cdi_syn_e  =~ s/[;\|]+/,/g if(defined $cdi_syn_e);


				my @alts;
				push(@alts,$rep_id)     if(defined $rep_id);
				push(@alts,$cdi_name)   if(defined $cdi_name);
				push(@alts,$cdi_name_j) if(defined $cdi_name_j);
				push(@alts,$cdi_name_e) if(defined $cdi_name_e);
				push(@alts,$cdi_name_k) if(defined $cdi_name_k);
				push(@alts,$cdi_name_l) if(defined $cdi_name_l);
				push(@alts,$cdi_syn_j)  if(defined $cdi_syn_j);
				push(@alts,$cdi_syn_e)  if(defined $cdi_syn_e);
				push(@alts,$cdi_taid)   if(defined $cdi_taid);
				my $alt = join("|",@alts);

				$cdi_name_j =~ s/,+/<br\/>/g if(defined $cdi_name_j);
				$cdi_name_e =~ s/,+/<br\/>/g if(defined $cdi_name_e);
				$cdi_name_k =~ s/,+/<br\/>/g if(defined $cdi_name_k);
				$cdi_name_l =~ s/,+/<br\/>/g if(defined $cdi_name_l);
				$cdi_syn_j  =~ s/,+/<br\/>/g if(defined $cdi_syn_j);
				$cdi_syn_e  =~ s/,+/<br\/>/g if(defined $cdi_syn_e);

				$HTML .= qq|<tr>|;
				$HTML .= qq|<td>|.(defined $rep_id     ? qq|<a href="?i=$rep_id">$rep_id</a>| : qq|<br/>|).qq|</td>|;
				$HTML .= qq|<td>|.(defined $cdi_name   ? $cdi_name   : qq|<br/>|).qq|</td>|;
				$HTML .= qq|<td>|.(defined $cdi_name_j ? $cdi_name_j : qq|<br/>|).qq|</td>|;
				$HTML .= qq|<td>|.(defined $cdi_name_e ? $cdi_name_e : qq|<br/>|).qq|</td>|;
				$HTML .= qq|<td>|.(defined $cdi_name_k ? $cdi_name_k : qq|<br/>|).qq|</td>|;
				$HTML .= qq|<td>|.(defined $cdi_name_l ? $cdi_name_l : qq|<br/>|).qq|</td>|;
				$HTML .= qq|<td>|.(defined $cdi_syn_j  ? $cdi_syn_j  : qq|<br/>|).qq|</td>|;
				$HTML .= qq|<td>|.(defined $cdi_syn_e  ? $cdi_syn_e  : qq|<br/>|).qq|</td>|;
				$HTML .= qq|<td>|.(defined $cdi_taid   ? $cdi_taid   : qq|<br/>|).qq|</td>|;


				$HTML .= qq|<td><img src="icon.cgi?i=$rep_id&s=L&p=rotate" width="640" height="640" alt="$alt"/></td>|;
#				$HTML .= qq|<td><img src="icon.cgi?i=$rep_id&s=S&p=rotate" width="120" height="120" alt="$alt"/></td>|;
				$HTML .= qq|</tr>\n|;
			}
			$HTML.=<<HTML;
</tbody></table>
HTML
#			&utf8::encode($HTML) if(&utf8::is_utf8($HTML));
			$CONTENTS .= &cgi_lib::common::encodeUTF8($HTML);
		}
		$sth_rep->finish;
		undef $sth_rep;

	}else{
		my $md_id;
		my $md_name_e;
		my $mv_id;
		my $mv_name_e;
		my $mr_id;

		my $ci_id;
		my $ci_name;
		my $cb_id;
		my $cb_name;

		my $bul_id;
		my $bul_name_e;

		my $sth_model = $dbh->prepare(qq|select md_id,md_name_e from model where md_delcause is null order by md_order limit 1|);
		$sth_model->execute();
		my $column_number = 0;
		$sth_model->bind_col(++$column_number, \$md_id, undef);
		$sth_model->bind_col(++$column_number, \$md_name_e, undef);
		$sth_model->fetch;
		$sth_model->finish;
		undef $sth_model;
		if(defined $md_id){
			my $sth_model_version = $dbh->prepare(qq|select mv_id,mv_name_e from model_version where md_id=? and mv_delcause is null order by mv_order limit 1|);
			$sth_model_version->execute($md_id);
			$column_number = 0;
			$sth_model_version->bind_col(++$column_number, \$mv_id, undef);
			$sth_model_version->bind_col(++$column_number, \$mv_name_e, undef);
			$sth_model_version->fetch;
			$sth_model_version->finish;
			undef $sth_model_version;
		}
		if(defined $md_id && defined $mv_id){
			my $sth_model_revision = $dbh->prepare(qq|select mr_id from model_revision where md_id=? and mv_id=? and mr_delcause is null order by mr_order limit 1|);
			$sth_model_revision->execute($md_id,$mv_id);
			$column_number = 0;
			$sth_model_revision->bind_col(++$column_number, \$mr_id, undef);
			$sth_model_revision->fetch;
			$sth_model_revision->finish;
			undef $sth_model_revision;
		}

		my $sth_concept_info = $dbh->prepare(qq|select ci_id,ci_name from concept_info where ci_delcause is null order by ci_order limit 1|);
		$sth_concept_info->execute();
		$column_number = 0;
		$sth_concept_info->bind_col(++$column_number, \$ci_id, undef);
		$sth_concept_info->bind_col(++$column_number, \$ci_name, undef);
		$sth_concept_info->fetch;
		$sth_concept_info->finish;
		undef $sth_concept_info;
		if(defined $ci_id){
			my $sth_concept_build = $dbh->prepare(qq|select cb_id,cb_name from concept_build where ci_id=? and cb_delcause is null order by cb_order limit 1|);
			$sth_concept_build->execute($ci_id);
			$column_number = 0;
			$sth_concept_build->bind_col(++$column_number, \$cb_id, undef);
			$sth_concept_build->bind_col(++$column_number, \$cb_name, undef);
			$sth_concept_build->fetch;
			$sth_concept_build->finish;
			undef $sth_concept_build;
		}

		my $sth_buildup_logic = $dbh->prepare(qq|select bul_id,bul_name_e from buildup_logic where bul_delcause is null order by bul_order|);
		$sth_buildup_logic->execute();
		$column_number = 0;
		$sth_buildup_logic->bind_col(++$column_number, \$bul_id, undef);
		$sth_buildup_logic->bind_col(++$column_number, \$bul_name_e, undef);
		while($sth_buildup_logic->fetch){
			my $sql=<<SQL;
select
 rep_id,
 rep_xmin,
 rep_xmax,
 rep_ymin,
 rep_ymax,
 rep_zmin,
 rep_zmax,
 rep_volume,
 rep_density_objs,
 rep_density_ends,
 rep_primitive,
 cdi_name,
 cdi_name_j,
 cdi_name_e,
 cdi_name_k,
 cdi_name_l,
 cdi_syn_j,
 cdi_syn_e,
 cdi_def_j,
 cdi_def_e,
 cdi_taid
from
 view_representation
where
 rep_delcause is null AND
 (ci_id,cb_id,md_id,mv_id,mr_id,bul_id,cdi_id) in (
   select
    ci_id,
    cb_id,
    md_id,
    mv_id,
    max(mr_id) as mr_id,
    bul_id,
    cdi_id
   from
    representation
   where
    ci_id=$ci_id and cb_id=$cb_id and md_id=$md_id and mv_id=$mv_id and mr_id<=$mr_id and bul_id=$bul_id
   group by
    ci_id,
    cb_id,
    md_id,
    mv_id,
    bul_id,
    cdi_id
 )
order by
 rep_serial
SQL

			my $rep_id;
			my $rep_xmin;
			my $rep_xmax;
			my $rep_ymin;
			my $rep_ymax;
			my $rep_zmin;
			my $rep_zmax;
			my $rep_volume;
			my $rep_density_objs;
			my $rep_density_ends;
			my $rep_primitive;
			my $cdi_name;
			my $cdi_name_j;
			my $cdi_name_e;
			my $cdi_name_k;
			my $cdi_name_l;
			my $cdi_syn_j;
			my $cdi_syn_e;
			my $cdi_def_j;
			my $cdi_def_e;
			my $cdi_taid;

			my $sth_rep = $dbh->prepare($sql);
			$sth_rep->execute();
			if($sth_rep->rows()>0){
				my $HTML=<<HTML;
<table border="1" cellspacing="0" style="display:;"><tbody>
<caption>$md_name_e,$mv_name_e,$ci_name,$cb_name,$bul_name_e</caption>
HTML
				$column_number = 0;
				$sth_rep->bind_col(++$column_number, \$rep_id, undef);
				$sth_rep->bind_col(++$column_number, \$rep_xmin, undef);
				$sth_rep->bind_col(++$column_number, \$rep_xmax, undef);
				$sth_rep->bind_col(++$column_number, \$rep_ymin, undef);
				$sth_rep->bind_col(++$column_number, \$rep_ymax, undef);
				$sth_rep->bind_col(++$column_number, \$rep_zmin, undef);
				$sth_rep->bind_col(++$column_number, \$rep_zmax, undef);

				$sth_rep->bind_col(++$column_number, \$rep_volume, undef);
				$sth_rep->bind_col(++$column_number, \$rep_density_objs, undef);
				$sth_rep->bind_col(++$column_number, \$rep_density_ends, undef);
				$sth_rep->bind_col(++$column_number, \$rep_primitive, undef);

				$sth_rep->bind_col(++$column_number, \$cdi_name, undef);
				$sth_rep->bind_col(++$column_number, \$cdi_name_j, undef);
				$sth_rep->bind_col(++$column_number, \$cdi_name_e, undef);
				$sth_rep->bind_col(++$column_number, \$cdi_name_k, undef);
				$sth_rep->bind_col(++$column_number, \$cdi_name_l, undef);

				$sth_rep->bind_col(++$column_number, \$cdi_syn_j, undef);
				$sth_rep->bind_col(++$column_number, \$cdi_syn_e, undef);
				$sth_rep->bind_col(++$column_number, \$cdi_def_j, undef);
				$sth_rep->bind_col(++$column_number, \$cdi_def_e, undef);
				$sth_rep->bind_col(++$column_number, \$cdi_taid, undef);

				while($sth_rep->fetch){
					next unless(defined $rep_id);

					$cdi_name_j =~ s/[;\|]+/,/g if(defined $cdi_name_j);
					$cdi_name_e =~ s/[;\|]+/,/g if(defined $cdi_name_e);
					$cdi_name_k =~ s/[;\|]+/,/g if(defined $cdi_name_k);
					$cdi_name_l =~ s/[;\|]+/,/g if(defined $cdi_name_l);
					$cdi_syn_j  =~ s/[;\|]+/,/g if(defined $cdi_syn_j);
					$cdi_syn_e  =~ s/[;\|]+/,/g if(defined $cdi_syn_e);


					my @alts;
					push(@alts,$rep_id)     if(defined $rep_id);
					push(@alts,$cdi_name)   if(defined $cdi_name);
					push(@alts,$cdi_name_j) if(defined $cdi_name_j);
					push(@alts,$cdi_name_e) if(defined $cdi_name_e);
					push(@alts,$cdi_name_k) if(defined $cdi_name_k);
					push(@alts,$cdi_name_l) if(defined $cdi_name_l);
					push(@alts,$cdi_syn_j)  if(defined $cdi_syn_j);
					push(@alts,$cdi_syn_e)  if(defined $cdi_syn_e);
					push(@alts,$cdi_taid)   if(defined $cdi_taid);
					my $alt = join("|",@alts);

					$cdi_name_j =~ s/,+/<br\/>/g if(defined $cdi_name_j);
					$cdi_name_e =~ s/,+/<br\/>/g if(defined $cdi_name_e);
					$cdi_name_k =~ s/,+/<br\/>/g if(defined $cdi_name_k);
					$cdi_name_l =~ s/,+/<br\/>/g if(defined $cdi_name_l);
					$cdi_syn_j  =~ s/,+/<br\/>/g if(defined $cdi_syn_j);
					$cdi_syn_e  =~ s/,+/<br\/>/g if(defined $cdi_syn_e);

					$HTML .= qq|<tr>|;
					$HTML .= qq|<td>|.(defined $rep_id     ? qq|<a href="?i=$rep_id">$rep_id</a>| : qq|<br/>|).qq|</td>|;
					$HTML .= qq|<td>|.(defined $cdi_name   ? $cdi_name   : qq|<br/>|).qq|</td>|;
					$HTML .= qq|<td>|.(defined $cdi_name_j ? $cdi_name_j : qq|<br/>|).qq|</td>|;
					$HTML .= qq|<td>|.(defined $cdi_name_e ? $cdi_name_e : qq|<br/>|).qq|</td>|;
					$HTML .= qq|<td>|.(defined $cdi_name_k ? $cdi_name_k : qq|<br/>|).qq|</td>|;
					$HTML .= qq|<td>|.(defined $cdi_name_l ? $cdi_name_l : qq|<br/>|).qq|</td>|;
					$HTML .= qq|<td>|.(defined $cdi_syn_j  ? $cdi_syn_j  : qq|<br/>|).qq|</td>|;
					$HTML .= qq|<td>|.(defined $cdi_syn_e  ? $cdi_syn_e  : qq|<br/>|).qq|</td>|;
					$HTML .= qq|<td>|.(defined $cdi_taid   ? $cdi_taid   : qq|<br/>|).qq|</td>|;


					$HTML .= qq|<td><img src="icon.cgi?i=$rep_id&s=L&p=rotate" width="640" height="640" alt="$alt"/></td>|;
	#				$HTML .= qq|<td><img src="icon.cgi?i=$rep_id&s=S&p=rotate" width="120" height="120" alt="$alt"/></td>|;
					$HTML .= qq|</tr>\n|;
				}
				$HTML.=<<HTML;
</tbody></table>
HTML
#				&utf8::encode($HTML) if(&utf8::is_utf8($HTML));
				$CONTENTS .= &cgi_lib::common::encodeUTF8($HTML);
			}
			$sth_rep->finish;
			undef $sth_rep;
		}
		$sth_buildup_logic->finish;
		undef $sth_buildup_logic;
	}
}else{
$CONTENTS .= <<HTML;
<noscript>
Please enable JavaScript.
</noscript>
HTML
}
if(exists($PARENT{url})){
	$CONTENTS .= <<HTML;
	<div id="up_data" style="display:none;">
		<form id="up_data_form" method="POST" target="up_data_iframe" action="$PARENT{url}">
			<input type="hidden" name="config" value="$lsdb_Config">
HTML
	delete $PARENT{url};
	foreach my $key (keys(%PARENT)){
		$CONTENTS .= qq|<input type="hidden" name="$key" value="$PARENT{$key}">\n|;
	}
	$CONTENTS .= <<HTML;
		</form>
		<iframe name="up_data_iframe"></iframe>
	</div>
HTML
}
$CONTENTS .= <<HTML;
<div id="header" class="x-hide-display">
	<a id="locale_link" href="#" onclick="click_locale();return false;">$LOCALE{LOCALE_TITLE}</a>
	<span class="ytb-sep"></span>
	<div id="search_area"></div>
	<div id="search_label">Search:</div>
	<div class="api-title">$LOCALE{DOCUMENT_TITLE}</div>
</div>
<div style="display:none;">
	<iframe id="_location" name="_location"></iframe>
</div>
<select name="opacity" id="opacity" style="display: none;">
	<option value="1.0">1.0</option>
	<option value="0.9">0.9</option>
	<option value="0.8">0.8</option>
	<option value="0.7">0.7</option>
	<option value="0.6">0.6</option>
	<option value="0.5">0.5</option>
	<option value="0.4">0.4</option>
	<option value="0.3">0.3</option>
	<option value="0.2">0.2</option>
	<option value="0.1">0.1</option>
	<option value="0.0">0.0</option>
</select>
<select name="representation" id="representation" style="display: none;">
	<option value="surface">surface</option>
	<option value="wireframe">wireframe</option>
	<option value="points">points</option>
</select>

<div id="contents-tab-feedback-contents-panel-render" class="x-hide-display"></div>
<div id="contents-tab-feedback-panel-render" class="x-hide-display"></div>
<div id="contents-tab-bodyparts-panel-render" class="x-hide-display">aaa</div>
<div id="view-images-detail-annotation-dataview-render" class="x-hide-display"></div>
<div id="bp3d-detail-annotation-dataview-render" class="x-hide-display"></div>
<form id="link-form" target="_blank" class="x-hide-display"></form>
<form method="GET" id="comment-link-form" target="_blank" class="x-hide-display"></form>
<form method="GET" action="http://lifesciencedb.jp/ag/lookup" id="ag-link-form" target="_blank" class="x-hide-display">
<input type="hidden" name="q" value=""/>
</form>

<div id="ag-command-box" align="center" class="x-hide-display" style="">
	<div id="ag-command-image-controls-render"></div>
	<div id="ag-command-window-controls-render"></div>
</div>

<div id="ag-command-clip-box">
</div>


<div id="ag-image-box" align="center" class="x-hide-display" style="vertical-align:middle;">
	<table width="100%" height="100%">
		<tr>
			<td align="center" valign="center" style="position:relative;">
			</td>
		</tr>
	</table>
</div>


<div id="bp3d-contents-detail-wiki-panel-render" class="x-hide-display">
	<iframe id="bp3d-contents-detail-wiki-panel-iframe" width="100%" height="100%" frameborder=0></iframe>
</div>

<!--
<div id="navigate-north-panel-content" align="center" class="x-hide-display">
	<table cellpadding=0 cellspacing=0><tbody><tr>
		<td><img src="css/1.png" align=center width=44 height=44></td>
		<td style="padding-left:1em;"><label style="white-space:nowrap;">$LOCALE{BUILD_UP} by&nbsp;</label><label id="navigate-north-buildup" style="white-space:nowrap;"></label></td>
	</tr></tbody></table>
</div>
-->

<div id="navigate-north-panel-content" class="x-hide-display">
	<table cellpadding=0 cellspacing=0><tbody>
	<tr>
		<td valign="top"><img src="css/1.png" align=center width=44 height=44></td>
		<td style="padding-left:0px;">
			<label style="white-space:nowrap;display:none;">$LOCALE{BUILD_UP} by&nbsp;</label><label id="navigate-north-buildup" style="white-space:nowrap;display:none;"></label>

			<table cellpadding=0 cellspacing=2><tbody>
				<tr>
					<td colspan="3"><label style="white-space:nowrap;font-size:11px;">
						<label style="white-space:nowrap;font-size:11px;">Parts of <a href="$LOCALE{FMA_DESCRIPTION_URL}" target="_blank"><label id="bp3d-concept-info-label">FMA</label></a> (<label id="bp3d-concept-build-label">3.0</label>) concepts<a href="#" onclick="return click_information_button({hash:'#FMA'});"><img src="css/information.png" width=12 height=12></a></label>
					</td>
				</tr>
				<tr>
					<td style="padding-left:0em;" align="center" valign="middle"><input type="radio" name="navigate-north-panel-content-radio" id="navigate-north-panel-content-radio-isa" value="3"/></td>
					<td align="left" valign="middle" nowrap>
						<label style="white-space:nowrap;font-size:18px;" for="navigate-north-panel-content-radio-isa">IS-A Tree</label>
						<label style="white-space:nowrap;font-size:18px;" for="navigate-north-panel-content-radio-isa" id="navigate-north-panel-content-label-3" class="navigate-north-panel-content-label"></label>
					</td>
				</tr>
				<tr>
					<td style="padding-left:0em;" align="center" valign="middle"><input type="radio" name="navigate-north-panel-content-radio" id="navigate-north-panel-content-radio-partof" value="4" /></td>
					<td align="left" valign="middle" nowrap>
						<label style="white-space:nowrap;font-size:18px;" for="navigate-north-panel-content-radio-partof">HAS PART Tree</label>
						<label style="white-space:nowrap;font-size:18px;" for="navigate-north-panel-content-radio-partof" id="navigate-north-panel-content-label-4" class="navigate-north-panel-content-label"></label>
					</td>
				</tr>
			</tbody></table>

		</td>
	</tr>
	</tbody></table>
</div>


<div id="ag-command-image-controls-content" align="left" class="x-hide-display">
	<table cellpadding="0" cellspacing="0" boder="0" width="100%">
		<!-- image rotation -->
		<tr><td colspan="2" class="ag_command_title"><div>Image rotation</div></td></tr>
		<tr><td colspan="2" class="ag_command">
			<table align="center">
				<tr>
					<td align="center">
						<table border="0" cellpadding="0" cellspacing="0" align="center">
							<tr><td></td><td></td><td><img class="point_cursor" src="img/rotate_u.png" onclick="rotateVertical(-15);" /></td><td></td><td></td></tr>
							<tr>
								<td><img class="point_cursor" src="img/rotate_l90.png" onclick="rotateHorizontal(90);" /></td>
								<td><img class="point_cursor" src="img/rotate_l.png" onclick="rotateHorizontal(15);" /></td>
								<td></td>
								<td><img class="point_cursor" src="img/rotate_r.png" onclick="rotateHorizontal(-15);" /></td>
								<td><img class="point_cursor" src="img/rotate_r90.png" onclick="rotateHorizontal(-90);" /></td>
							</tr>
							<tr><td></td><td></td><td><img class="point_cursor" src="img/rotate_d.png" onclick="rotateVertical(15);" /></td><td></td><td></td></tr>
						</table>
					</td>
				</tr>
				<tr>
					<td align="center">
						<table border="0" cellpadding="0" cellspacing="0" align="center" width="60">
							<tr>
								<td class="ag_command_rotation_label">H:</td><td class="ag_command_rotation_value"><div id="ag-command-rotation-horizontal-render"></div></td>
								<td class="ag_command_rotation_label">V:</td><td class="ag_command_rotation_value"><div id="ag-command-rotation-vertical-render"></div></td>
							</tr>
						</table>
					</td>
				</tr>
			</table>
		</td></tr>
		<tr><td colspan="2" class="ag_command">
			<div align="center">
				<div id="rotateImgDiv" style="position:relative;overflow:hidden;width:62px;height:124px;border:1px solid #ccc;">
					<img id="rotateImg" style="position:absolute;left:-31px;width:124px;height:124px;" src="img_angle/000_000.png" />
				</div>
			</div>
		</td></tr>
HTML
if($autoRotationHidden ne 'true'){
	$CONTENTS .= <<HTML;
		<!-- rotate auto -->
		<tr><td colspan="2" class="ag_command_title"><div><div id="ag-command-image-controls-rotateAuto-render">Auto rotation</div></div></td></tr>
		<tr>
			<td colspan="2" class="ag_command">
				<table cellpadding="0" cellspacing="0" boder="0" align="center">
					<tr>
						<td class="ag_command_rotation_label">Rotation angles:</td>
						<td colspan="2" class="ag_command_rotation_value"><div id="ag-command-image-controls-rotateAuto-angles-render"></div></td>
					</tr>
					<tr><td style="line-height:2px;"><br/></td></tr>
					<tr>
						<td class="ag_command_rotation_label">Minimum time interval:</td>
						<td class="ag_command_rotation_value" width="25"><div id="ag-command-image-controls-rotateAuto-interval-render"></div></td>
						<td style="vertical-align: bottom;" width="20"><label id="ag-command-image-controls-rotateAuto-interval-unit-label" class="ag_command x-form-cb-label">s</label></td>
					</tr>
HTML
	if($modifyAxisOfRotation eq 'true'){
		$CONTENTS .= <<HTML;
					<tr><td style="line-height:2px;"><br/></td></tr>
					<tr>
						<td class="ag_command_rotation_label" style="vertical-align: middle;">Axis of rotation angle:</td>
						<td class="ag_command_rotation_value" style="vertical-align: middle;text-align:right;"><label id="ag-command-image-controls-rotateAuto-axis-label" class="ag_command x-form-cb-label"></label></td>
					</tr>
					<tr><td style="line-height:2px;"><br/></td></tr>
					<tr>
						<td class="ag_command_rotation_label" style="vertical-align: middle;">Now angle:</td>
						<td class="ag_command_rotation_value" style="vertical-align: middle;text-align:right;"><label id="ag-command-image-controls-rotateAuto-now-angle-label" class="ag_command x-form-cb-label"></label></td>
					</tr>
HTML
	}
	$CONTENTS .= <<HTML;
				</table>
			</td>
		</tr>
HTML
}
$CONTENTS .= <<HTML;
		<tr><td colspan="2" class="ag_command_separator"><br/></td></tr>
	</table>
</div>

<div id="ag-command-window-controls-content" align="center" class="x-hide-display">
	<table cellpadding="0" cellspacing="0" boder="0" width="100%" style="border:0px transparent solid;">
		<!-- window size -->
		<tr><td colspan="2" class="ag_command_title"><div>Window size</div></td></tr>
		<tr>
			<td class="ag_command_label"><img src="css/arrow_width.png"/></td>
			<td>
				<table cellpadding="0" cellspacing="0" boder="0"><tr>
					<td class="ag_command"><div id="ag-command-windowsize-width-render"></div></td><td valign="bottom"><label class="ag_command x-form-cb-label" style="font-family:arial,tahoma,helvetica,sans-serif;font-size:12px;margin-left:4px;margin-bottom:4px;">px</label></td>
				</tr></table>
			</td>
		</tr>
		<tr>
			<td class="ag_command_label"><img src="css/arrow_height.png"/></td>
			<td>
				<table cellpadding="0" cellspacing="0" boder="0"><tr>
					<td class="ag_command"><div id="ag-command-windowsize-height-render"></div></td><td valign="bottom"><label class="ag_command x-form-cb-label" style="font-family:arial,tahoma,helvetica,sans-serif;font-size:12px;margin-left:4px;margin-bottom:4px;">px</label></td>
				</tr></table>
			</td>
		</tr>

		<tr>
			<td colspan="2" class="ag_command">
				<table cellpadding="0" cellspacing="0" boder="0" align="left">
					<tr>
						<td valign="top"><div id="ag-command-windowsize-autosize-checkbox-render"></div></td>
					</tr>
				</table>
			</td>
		</tr>

		<!-- background color -->
		<tr><td colspan="2" class="ag_command_title"><div>Background color</div></td></tr>
		<tr>
			<td class="ag_command_label" style="text-align:center;"><img src="css/color_pallet.png"/></td>
			<td class="ag_command"><div id="ag-command-bgcolor-render"></div></td>
		</tr>
		<tr>
			<td colspan="2" class="ag_command">
				<table cellpadding="0" cellspacing="0" boder="0" align="left">
					<tr>
						<td valign="top"><div id="ag-command-bgcolor-transparent-checkbox-render"></div></td>
					</tr>
				</table>
			</td>
		</tr>

		<!-- color map -->
		<tr><td colspan="2" class="ag_command_title"><div>Choropleth</div></td></tr>
		<tr><td class="ag_command_label">MAX:</td><td class="ag_command"><div id="ag-command-colormap-max-render"></div></td></tr>
		<tr><td class="ag_command_label">MIN:</td><td class="ag_command"><div id="ag-command-colormap-min-render"></div></td></tr>
		<tr><td class="ag_command_label">On / Off:</td><td class="ag_command" style="text-align:center;"><div id="ag-command-colormap-bar-render"></div></td></tr>

		<!-- Default parts color -->
		<tr><td colspan="2" class="ag_command_title"><div>Default parts color</div></td></tr>
		<tr>
			<td class="ag_command_label" style="text-align:center;"><img src="css/color_pallet.png"/></td>
			<td class="ag_command"><div id="ag-command-default-parts-color-render"></div></td>
		</tr>

		<!-- Default pick color -->
		<tr><td colspan="2" class="ag_command_title"><div>Default pick color</div></td></tr>
		<tr>
			<td class="ag_command_label" style="text-align:center;"><img src="css/color_pallet.png"/></td>
			<td class="ag_command"><div id="ag-command-default-pick-color-render"></div></td>
		</tr>
HTML
if($addPointElementHidden ne 'true'){
	$CONTENTS .= <<HTML;
		<!-- Point parts -->
		<tr><td colspan="2" class="ag_command_title"><div>Point</div></td></tr>
		<tr>
			<td class="ag_command_label" style="text-align:center;"><img src="css/color_pallet.png"/></td>
			<td class="ag_command"><div id="ag-command-default-point-parts-color-render"></div></td>
		</tr>
		<tr>
			<td colspan="2" class="ag_command">
				<table cellpadding="0" cellspacing="0" boder="0" align="left">
					<tr>
						<td class="ag_command_label" style="text-align:center;">Sphere:</td>
						<td class="ag_command"><div id="ag-command-point-sphere-render"></div></td>
					</tr>
				</table>
			</td>
		</tr>
		<tr>
			<td class="ag_command_label" style="text-align:left;" colspan="2">Classification Label:</td>
		</tr>
		<tr>
			<td class="ag_command_label" style="text-align:left;"></td>
			<td class="ag_command"><div id="ag-command-point-label-render"></div></td>
		</tr>
		<tr>
			<td colspan="2" class="ag_command">
				<table cellpadding="0" cellspacing="0" boder="0" align="left">
					<tr>
						<td class="ag_command_label" style="text-align:center;">Description:</td>
						<td class="ag_command"><div id="ag-command-point-description-render"></div></td>
					</tr>
				</table>
			</td>
		</tr>
		<tr>
			<td colspan="2" class="ag_command">
				<div id="ag-command-point-description-command-div" style="padding-left:4px;">
					<table cellpadding="0" cellspacing="0" boder="0" align="left">
						<tr>
							<td class="ag_command_label" style="text-align:left;">Draw Point Indication Line:</td>
						</tr>
						<tr>
							<td class="ag_command"><div id="ag-command-point-description-draw-point-indication-line-render"  style="float:right;"></div></td>
						</tr>
					</table>
				</div>
			</td>
		</tr>
HTML
}
$CONTENTS .= <<HTML;
		<tr><td colspan="2" class="ag_command_separator"><br/></td></tr>
	</table>
</div>


<div id="ag-command-sectional-view-content" align="center" class="x-hide-display">
	<table cellpadding="0" cellspacing="0" boder="0" width="100%">
		<!-- clip -->
		<tr><td colspan="2" class="ag_command_title"><div><div id="ag-command-clip-checkbox-render">Clip</div>&nbsp;On/Off</div></td></tr>
		<tr>
			<td colspan="2" class="ag_command">
				<table cellpadding="0" cellspacing="0" boder="0" align="center">
					<tr>
						<td class="ag_command"><div id="ag-command-clip-method-render"></div></td>
						<td class="ag_command"><div id="ag-command-clip-predifined-render"></div></td>
					</tr>
				</table>
			</td>
		</tr>
		<tr>
			<td colspan="2" class="ag_command">
				<table cellpadding="0" cellspacing="0" boder="0" align="right">
					<tr>
						<td valign="top"><div id="ag-command-clip-fix-checkbox-render"></div></td>
						<td valign="top"><div id="ag-command-clip-reverse-checkbox-render"></div></td>
					</tr>
				</table>
			</td>
		</tr>
		<tr>
			<td colspan="2" class="ag_command">
				<table cellpadding="0" cellspacing="0" boder="0" align="center" width="100%">
					<tr>
						<td valign="middle" align="right" width="20"><img id='anatomo-clip-slider-down-button' src="img/icon_move_left.gif" onclick="anatomoClipDownButton();"/></td>
						<td valign="middle"><div id="ag-command-clip-slider-render"></div></td>
						<td valign="middle" align="left" width="20"><img id='anatomo-clip-slider-up-button' src="img/icon_move_right.gif" onclick="anatomoClipUpButton();"/></td></tr>
					</tr>
				</table>
			</td>
		</tr>
		<tr>
			<td colspan="2"class="ag_command">
				<table cellpadding="0" cellspacing="0" boder="0" align="center">
					<tr><td rowspan="2"><div id="ag-command-clip-text-render"></div></td><td><img id='anatomo-clip-text-up-button' src="css/spinner-up.png" onclick="anatomoClipUpButton();"/></td><td rowspan="2" valign="bottom"><label id='anatomo-clip-unit-label' class="x-form-cb-label" style="font-family:arial,tahoma,helvetica,sans-serif;font-size:10px;">mm</label></td></tr>
					<tr><td><img id='anatomo-clip-text-down-button' src="css/spinner-down.png" onclick="anatomoClipDownButton();"/></td></tr>
				</table>
			</td>
		</tr>
		<tr>
			<td colspan="2" class="ag_command"  align="center">
				<div id="clipImgDiv" class="clipImgDiv" style="position:relative;overflow:hidden;left:10px;width:136px;height:301px;border:1px solid #ccc;">
					<img id="clipImg" style="position:absolute;left:0px;top:0px;width:136px;height:301px;" src="img_angle/000_000.png" />
					<div id="clipImgLine" style="display:none;position:absolute;left:0px;top:0px;width:254px;height:1px;border-top:1px solid red;border-left:1px solid red;"></div>
				</div>
			</td>
		</tr>
		<tr><td colspan="2" class="ag_command_separator"><br/></td></tr>
	</table>
</div>

<div id="ag-point-grid-content" align="center" class="x-hide-display">
	<table id="ag-point-grid-content-table" cellpadding="0" cellspacing="0" boder="0">
		<tr>
			<td class="ag_grid_command"><div class="x-toolbar x-small-editor" align="left" id="ag-comment-point-type-render"></div></td>
			<td class="ag_grid_command"><div class="x-toolbar x-small-editor" align="center" id="ag-comment-point-toggle-partof-render"></div></td>
			<td class="ag_grid_command"><div class="x-toolbar x-small-editor" align="center" id="ag-comment-point-toggle-haspart-render"></div></td>
		</tr>
		<tr>
			<td colspan="4" class="ag_grid_command_title">
				<table cellpadding="0" cellspacing="0" boder="0" width="100%"></tr>
					<td width="50"><div style="border-top-width:0px;border-bottom-width:1px;"><label>Path</label></div></td>
					<td><div id="ag-point-grid-content-route" style="border-top-width:0px;border-bottom-width:1px;">&nbsp;</div></td>
				</tr></table>
			</td>
		</tr>
	</table>
</div>

<div id="ag-point-grid-footer-content" align="center" class="x-hide-display">
	<table id="ag-point-grid-footer-content-table" cellpadding="0" cellspacing="0" boder="0">
		<tr>
			<td class="ag_grid_command" style="width:56px;"><div class="x-toolbar x-small-editor" style="width:56px;height:20px;line-height:20px;" align="right">Coordinate</div></td>
			<td class="ag_grid_command" style="width:72px;"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;font-weight:normal;" align="center" id="ag-point-grid-footer-content-coordinate-x-render">X:</div></td>
			<td class="ag_grid_command" style="width:72px;"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;font-weight:normal;" align="center" id="ag-point-grid-footer-content-coordinate-y-render">Y:</div></td>
			<td class="ag_grid_command" style="width:72px;"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;font-weight:normal;" align="center" id="ag-point-grid-footer-content-coordinate-z-render">Z:</div></td>
			<td class="ag_grid_command"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;border-right:0px;" align="left" id="ag-point-grid-footer-content-coordinate-render"> </div></td>
		</tr>
		<tr>
			<td class="ag_grid_command"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;" align="right">Distance</div></td>
			<td class="ag_grid_command"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;font-weight:normal;" align="center" id="ag-point-grid-footer-content-distance-x-render">X:</div></td>
			<td class="ag_grid_command"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;font-weight:normal;" align="center" id="ag-point-grid-footer-content-distance-y-render">Y:</div></td>
			<td class="ag_grid_command"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;font-weight:normal;" align="center" id="ag-point-grid-footer-content-distance-z-render">Z:</div></td>
			<td class="ag_grid_command"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;border-right:0px;" align="left" id="ag-point-grid-footer-content-distance-render"> </div></td>
		</tr>
	</table>
</div>

<div id="navigate-position-panel-content" align="center" class="x-hide-display">

	<div id="navigate-position-panel-base-fx">
		<table border=0 cellspacing=0 cellpadding=0 class="position_base" style="">
			<tbody>
				<tr>
					<td align="center">
						<div style="width:292px;height:64px;overflow:hidden;">
							<table border=0 cellspacing=0 cellpadding=0 class="position_show_only" style="" align="center">
								<tbody>
									<tr>
										<td class="position_show_only_label" style="width:25px;"><label style="display:none;">Show Only</label></td>
										<td class="position_show_only_image position_show_only_image_Bone" style=""><img src="css/Bone_60x60.png"/><br/>Bone</td>
										<td class="position_show_only_image position_show_only_image_Muscle" style=""><img src="css/Muscle_60x60.png"/><br/>Muscle</td>
										<td class="position_show_only_image position_show_only_image_Vessel" style=""><img src="css/Vessel_60x60.png"/><br/>Vessel</td>
										<td class="position_show_only_image position_show_only_image_Internal" style=""><img src="css/Internal_60x60.png"/><br/>Internal</td>
										<td class="position_show_only_image position_show_only_image_All" style=""><img src="css/All_60x60.png"/><br/>All</td>
									</tr>
								</tbody>
							</table>
						</div>
					</td>
				</tr>
			</tbody>
		</table>

		<table border=0 cellspacing=0 cellpadding=0 class="navigate_position_panel_density" style="border:0px;">
			<tbody>
				<tr><td align="center">
					<div style="background:#ffffff;border:1px solid #cccccc;width: 210px;margin:0px auto;padding: 2px;">
						<table border=0 cellspacing=0 cellpadding=0><tbody>
							<tr>
								<td valign="top"><input type="checkbox" name="navigate-position-panel-only-taid" id="navigate-position-panel-only-taid" value="true"></td>
								<td valign="top" class="navigate_position_panel_only_taid"><label for="navigate-position-panel-only-taid" style="font-size:11px;">Show only TA matches(*)</label></td>
							</tr>
							<tr>
								<td valign="top" colspan="2" class="navigate_position_panel_only_taid"><label for="navigate-position-panel-only-taid">* listed in Terminologia Anatomica</label></td>
							</tr>
						</tbody></table>
					</div>
				</td></tr>
			</tbody>
		</table>

		<table border=0 cellspacing=0 cellpadding=0 class="navigate_position_panel_density" style="">
			<tbody>
				<tr><td><label>Representation Type</label><a href="#" onclick="return click_information_button({hash:'#Data_types'});"><img src="css/information.png" style="width:12px;height:12px;"></a></td></tr>
				<tr><td style="text-align:center;">
					<table border=0 cellspacing=0 cellpadding=0 align="center" style="width:230px;text-align:center;">
						<tbody>
<!--
							<tr>
								<td>
									<table border=0 cellspacing=0 cellpadding=0 class="navigate_position_panel_density_item select_item" style="">
										<tbody><tr>
											<td><input type="radio" name="navigate-position-panel-density-radio-name" id="navigate-position-panel-density-radio-name-any" value="any" checked></td>
											<td><label for="navigate-position-panel-density-radio-name-any">Any</label>&nbsp;<img src="css/075.png" align=center><img src="css/100.png" align=center><img src="css/primitive.png" align=center></td>
										</tr></tbody>
									</table>
								</td>
							</tr>
							<tr>
								<td>
									<table border=0 cellspacing=0 cellpadding=0 class="navigate_position_panel_density_item" style="">
										<tbody><tr>
											<td><input type="radio" name="navigate-position-panel-density-radio-name" id="navigate-position-panel-density-radio-name-primitive" value="primitive"></td>
											<td><label for="navigate-position-panel-density-radio-name-primitive">$LOCALE{ELEMENT}</label>&nbsp;<img src="css/primitive.png" align=center></td>
										</tr></tbody>
									</table>
								</td>
							</tr>
							<tr>
								<td>
									<table border=0 cellspacing=0 cellpadding=0 class="navigate_position_panel_density_item" style="">
										<tbody><tr>
											<td><input type="radio" name="navigate-position-panel-density-radio-name" id="navigate-position-panel-density-radio-name-100" value="100-inf"></td>
											<td><label for="navigate-position-panel-density-radio-name-100">$LOCALE{ELEMENT_COMPOUND}</label>&nbsp;<img src="css/primitive.png" align=center><img src="css/100.png" align=center></td>
										</tr></tbody>
									</table>
								</td>
							</tr>
-->

							<tr>
								<td>
									<table border=0 cellspacing=0 cellpadding=0 class="navigate_position_panel_density_item" style="">
										<tbody><tr>
											<td><input type="checkbox" name="navigate-position-panel-density-checkbox-name-element" id="navigate-position-panel-density-checkbox-name-element" value="element" checked></td>
											<td><label for="navigate-position-panel-density-checkbox-name-element">$LOCALE{ELEMENT}</label>&nbsp;<img src="css/primitive.png" align=center></td>
										</tr></tbody>
									</table>
								</td>
							</tr>
							<tr>
								<td>
									<table border=0 cellspacing=0 cellpadding=0 class="navigate_position_panel_density_item" style="">
										<tbody><tr>
											<td><input type="checkbox" name="navigate-position-panel-density-checkbox-name-complete-compound" id="navigate-position-panel-density-checkbox-name-complete-compound" value="complete-compound" checked></td>
											<td><label for="navigate-position-panel-density-checkbox-name-complete-compound">$LOCALE{COMPLETE_COMPOUND}</label>&nbsp;<img src="css/100.png" align=center></td>
										</tr></tbody>
									</table>
								</td>
							</tr>
							<tr>
								<td>
									<table border=0 cellspacing=0 cellpadding=0 class="navigate_position_panel_density_item" style="">
										<tbody><tr>
											<td><input type="checkbox" name="navigate-position-panel-density-checkbox-name-incomplete-compound" id="navigate-position-panel-density-checkbox-name-incomplete-compound" value="incomplete-compound" checked></td>
											<td><label for="navigate-position-panel-density-checkbox-name-incomplete-compound">$LOCALE{INCOMPLETE_COMPOUND}</label>&nbsp;<img src="css/075.png" align=center></td>
										</tr></tbody>
									</table>
								</td>
							</tr>


						</tbody>
					</table>
				</td></tr>

<!--
				<tr><td>
					<table border=0 cellspacing=0 cellpadding=0><tbody>
						<tr>
							<td valign="top"><input type="checkbox" name="navigate-position-panel-only-taid" id="navigate-position-panel-only-taid" value="true"></td>
							<td valign="top" class="navigate_position_panel_only_taid"><label for="navigate-position-panel-only-taid">Show only TA matches(*)</label></td>
						</tr>
						<tr>
							<td valign="top" colspan="2" class="navigate_position_panel_only_taid"><label for="navigate-position-panel-only-taid">* listed in Terminologia Anatomica</label></td>
						</tr>
					</tbody></table>
				</td></tr>
-->
			</tbody>
		</table>

	</div>

	<div id="navigate-position-panel-base">
		<img id="navigate-position-panel-img" src="css/human_body_front_085.png" />
		<img id="navigate-position-panel-img2" src="css/human_body_right_085.png" />
	</div>
	<div id="navigate-position-panel-head-disable" style="display:none;"></div>
	<div id="navigate-position-panel-tail-disable" style="display:none;"></div>
	<div id="navigate-position-panel-line"  style="display:none;"></div>
	<div id="navigate-position-panel-event"></div>


	<div id="navigate-position-panel-range-combobox-render"></div>
	<div id="navigate-position-panel-zmax-numberfield-render"></div>
	<div id="navigate-position-panel-zmin-numberfield-render"></div>
	<div id="navigate-position-panel-filter-combobox-render"></div>
	<div id="navigate-position-panel-cube-volume-combobox-render"></div>
	<div id="navigate-position-panel-cube-volume-zmax-numberfield-render"></div>
	<div id="navigate-position-panel-cube-volume-zmin-numberfield-render"></div>
	<div id="navigate-position-panel-zposition-numberfield-render"></div>
	<div id="navigate-position-panel-range-label-render"></div>
</div>

<div id="navigate-range-panel-content" align="center" class="x-hide-display">
	<div id="navigate-range-panel-base">
		<div id="navigate-range-panel-base1" style="display:none;">
			<div id="navigate-range-panel-event-head" class="navigate-range-panel-event">
				<label class="navigate-range-panel-label">H</label>
				<label class="navigate-range-panel-value"></label>
			</div>
			<div id="navigate-range-panel-event-body" class="navigate-range-panel-event">
				<label class="navigate-range-panel-label">U</label>
				<label class="navigate-range-panel-value"></label>
			</div>
			<div id="navigate-range-panel-event-leg" class="navigate-range-panel-event">
				<label class="navigate-range-panel-label">L</label>
				<label class="navigate-range-panel-value"></label>
			</div>
			<div id="navigate-range-panel-event-head-body" class="navigate-range-panel-event">
				<label class="navigate-range-panel-label">H+U</label>
				<label class="navigate-range-panel-value"></label>
			</div>
			<div id="navigate-range-panel-event-body-leg" class="navigate-range-panel-event">
				<label class="navigate-range-panel-label">U+L</label>
				<label class="navigate-range-panel-value"></label>
			</div>
			<div id="navigate-range-panel-event-all" class="navigate-range-panel-event">
				<label class="navigate-range-panel-label">H+U+L</label>
				<label class="navigate-range-panel-value"></label>
			</div>
		</div>

		<div id="navigate-range-panel-base2">
			<table border=0 cellspacing=0 cellpadding=0 class="range_base" style="">
				<tbody>
					<tr>
						<td colspan="6" align="left">
							<table border=0 cellspacing=0 cellpadding=0 class="range_show_only" style="" align="left">
								<tbody>
									<tr>
										<td class="range_show_only_label" style=""><label style="display:none;">Show Only</label></td>
										<td class="range_show_only_image range_show_only_image_Bone" style=""><img src="css/Bone_60x60.png"/><br/>Bone</td>
										<td class="range_show_only_image range_show_only_image_Muscle" style=""><img src="css/Muscle_60x60.png"/><br/>Muscle</td>
										<td class="range_show_only_image range_show_only_image_Vessel" style=""><img src="css/Vessel_60x60.png"/><br/>Vessel</td>
										<td class="range_show_only_image range_show_only_image_Internal" style=""><img src="css/Internal_60x60.png"/><br/>Internal</td>
										<td class="range_show_only_image range_show_only_image_All" style=""><img src="css/All_60x60.png"/><br/>All</td>
									</tr>
								</tbody>
							</table>
						</td>
					</tr>
					<tr>
						<td colspan="6" align="center">
							<table border=0 cellspacing=0 cellpadding=0 style="border-width:0px;padding:0px;margin:4px;">
								<tbody>
									<tr>
										<td colspan="2"></td>
										<td colspan="4" class="range_BCV_title">$LOCALE{DETAIL_TITLE_VOLUME} [cc]</td>
									</tr>
									<tr class="range_BCV_label">
										<td></td>
										<td width="4"></td>
										<td><div>&lt;10</div></td>
										<td><div>10<br>-<br>100</div></td>
										<td><div>100<br>-<br>1000</div></td>
										<td><div>1000&lt;</div></td>
										<td><div>Any</div></td>
									</tr>
									<tr>
										<td align="center" class="range_border range_border_left range_border_right">
											<table border=0 cellspacing=0 cellpadding=0 class="range_value">
												<tbody>
													<tr><td class="range_segment range_segment_label">

															<div class="range_segment range_segment_HU range_segment_area range_segment_area_HU">&nbsp</div>
															<div class="range_segment range_segment_UL range_segment_area range_segment_area_UL">&nbsp</div>

															<div class="range_segment_label">Segment</div>
															<div class="range_segment range_segment_H"><img src="css/H_50x50.png"/></div>
															<div class="range_segment range_segment_HU">H+U</div>
															<div class="range_segment range_segment_U"><img src="css/U_50x50.png"/></div>
															<div class="range_segment range_segment_UL">U+L</div>
															<div class="range_segment range_segment_L"><img src="css/L_50x50.png"/></div>
															<div class="range_segment range_segment_HUL">H+U+L</div>

													</td></tr>
												</tbody>
											</table>
										</td>
										<td></td>
										<td align="center" class="range_border range_border_left">
											<table border=0 cellspacing=0 cellpadding=0 class="range_value">
												<tbody>
													<tr><td class="range_segment range_segment_inf-10 range_value">
														<div class="range_segment range_segment_HU range_segment_area range_segment_area_HU">&nbsp</div>
														<div class="range_segment range_segment_UL range_segment_area range_segment_area_UL">&nbsp</div>

														<div class="range_segment_label">&nbsp;</div>
														<div class="range_segment range_segment_H   range_value">-</div>
														<div class="range_segment range_segment_HU  range_value">-</div>
														<div class="range_segment range_segment_U   range_value">-</div>
														<div class="range_segment range_segment_UL  range_value">-</div>
														<div class="range_segment range_segment_L   range_value">-</div>
														<div class="range_segment range_segment_HUL range_value">-</div>
													</td></tr>
												</tbody>
											</table>
										</td>
										<td align="center" class="range_border">
											<table border=0 cellspacing=0 cellpadding=0 class="range_value">
												<tbody>
													<tr><td class="range_segment range_segment_10-100 range_value">
														<div class="range_segment range_segment_HU range_segment_area range_segment_area_HU">&nbsp</div>
														<div class="range_segment range_segment_UL range_segment_area range_segment_area_UL">&nbsp</div>

														<div class="range_segment_label">&nbsp;</div>
														<div class="range_segment range_segment_H   range_value">-</div>
														<div class="range_segment range_segment_HU  range_value">-</div>
														<div class="range_segment range_segment_U   range_value">-</div>
														<div class="range_segment range_segment_UL  range_value">-</div>
														<div class="range_segment range_segment_L   range_value">-</div>
														<div class="range_segment range_segment_HUL range_value">-</div>
													</td></tr>
												</tbody>
											</table>
										</td>
										<td align="center" class="range_border">
											<table border=0 cellspacing=0 cellpadding=0 class="range_value">
												<tbody>
													<tr><td class="range_segment range_segment_100-1000 range_value">
														<div class="range_segment range_segment_HU range_segment_area range_segment_area_HU">&nbsp</div>
														<div class="range_segment range_segment_UL range_segment_area range_segment_area_UL">&nbsp</div>

														<div class="range_segment_label">&nbsp;</div>
														<div class="range_segment range_segment_H   range_value">-</div>
														<div class="range_segment range_segment_HU  range_value">-</div>
														<div class="range_segment range_segment_U   range_value">-</div>
														<div class="range_segment range_segment_UL  range_value">-</div>
														<div class="range_segment range_segment_L   range_value">-</div>
														<div class="range_segment range_segment_HUL range_value">-</div>
													</td></tr>
												</tbody>
											</table>
										</td>
										<td align="center" class="range_border range_border_right">
											<table border=0 cellspacing=0 cellpadding=0 class="range_value">
												<tbody>
													<tr><td class="range_segment range_segment_1000-inf range_value">
														<div class="range_segment range_segment_HU range_segment_area range_segment_area_HU">&nbsp</div>
														<div class="range_segment range_segment_UL range_segment_area range_segment_area_UL">&nbsp</div>

														<div class="range_segment_label">&nbsp;</div>
														<div class="range_segment range_segment_H   range_value">-</div>
														<div class="range_segment range_segment_HU  range_value">-</div>
														<div class="range_segment range_segment_U   range_value">-</div>
														<div class="range_segment range_segment_UL  range_value">-</div>
														<div class="range_segment range_segment_L   range_value">-</div>
														<div class="range_segment range_segment_HUL range_value">-</div>
													</td></tr>
												</tbody>
											</table>
										</td>
									</tr>
								</tbody>
							</table>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<div id="navigate-range-panel-base-fx">
			<table border=0 cellspacing=0 cellpadding=0 class="range_base" style="">
				<tbody>
					<tr>
						<td align="center">
							<table border=0 cellspacing=0 cellpadding=0 class="range_show_only" style="" align="center">
								<tbody>
									<tr>
										<td class="range_show_only_label" style="width:25px;"><label style="display:none;">Show Only</label></td>
										<td class="range_show_only_image range_show_only_image_Bone" style=""><img src="css/Bone_60x60.png"/><br/>Bone</td>
										<td class="range_show_only_image range_show_only_image_Muscle" style=""><img src="css/Muscle_60x60.png"/><br/>Muscle</td>
										<td class="range_show_only_image range_show_only_image_Vessel" style=""><img src="css/Vessel_60x60.png"/><br/>Vessel</td>
										<td class="range_show_only_image range_show_only_image_Internal" style=""><img src="css/Internal_60x60.png"/><br/>Internal</td>
										<td class="range_show_only_image range_show_only_image_All" style=""><img src="css/All_60x60.png"/><br/>All</td>
									</tr>
								</tbody>
							</table>
						</td>
					</tr>

					<tr><td align="center">
						<div style="background:#ffffff;border:1px solid #cccccc;width: 210px;margin:0px auto;padding: 2px;">
							<table border=0 cellspacing=0 cellpadding=0 align="center"><tbody>
								<tr>
									<td valign="top"><input type="checkbox" name="navigate-range-panel-only-taid" id="navigate-range-panel-only-taid" value="true"></td>
									<td valign="top" class="navigate_range_panel_only_taid"><label for="navigate-range-panel-only-taid" style="font-size:11px;">Show only TA matches(*)</label></td>
								</tr>
								<tr>
									<td valign="top" colspan="2" class="navigate_range_panel_only_taid"><label for="navigate-range-panel-only-taid">* listed in Terminologia Anatomica</label></td>
								</tr>
							</tbody></table>
						</div>
					</td></tr>

					<tr>
						<td>
							<table border=0 cellspacing=0 cellpadding=0 style="border-width:0px;padding:0px;margin:4px;">
								<tbody>
									<tr>
										<td colspan="2"></td>
										<td colspan="5" class="range_BCV_title"><div style="font-weight:bold;margin-bottom:2px;">$LOCALE{DETAIL_TITLE_VOLUME} [cc]</div></td>
									</tr>
									<tr class="range_BCV_label">
										<td></td>
										<td style="width:4px;"></td>
										<td><div>&lt;0.1</div></td>
										<td><div>0.1<br>-<br>0.35</div></td>
										<td><div>0.35<br>-<br>1</div></td>
										<td><div>1<br>-<br>10</div></td>
										<td><div>10&lt;</div></td>
										<td><div>Any</div></td>
									</tr>
									<tr>
										<td align="center" class="">
											<table border=0 cellspacing=0 cellpadding=0 class="range_border range_border_left range_border_right range_border_top">
												<tbody>
													<tr><td class="range_segment range_segment_label">
														<div class="range_segment_base">
															<div class="range_segment_label">Segment<br>Range</div>
															<div class="range_segment range_segment_H"><img src="css/H_50x50.png"/></div>
															<div class="range_segment range_segment_U"><img src="css/U_50x50.png"/></div>
															<div class="range_segment range_segment_L"><img src="css/L_50x50.png"/></div>
															<div class="range_segment_label" style="height:36px;margin:0 0;padding:6px 0 0;"><label>Bridging</label><br><label>more than</label><br><label>one seg.</label></div>

														</div>
													</td></tr>
												</tbody>
											</table>

											<table border=0 cellspacing=0 cellpadding=0 class="range_value range_border range_border_left range_border_right range_border_bottom">
												<tbody>
													<tr><td class="range_segment range_segment_label">
														<div class="range_segment_base">
															<div class="range_segment range_segment_ANY">Any</div>
														</div>
													</td></tr>
												</tbody>
											</table>

										</td>
										<td></td>

										<td align="center" class="">
											<table border=0 cellspacing=0 cellpadding=0 class="range_value range_border range_border_left range_border_top range_segment_inf-01 range_segment_area_HUL">
												<tbody>
													<tr><td class="range_segment range_segment_inf-01 range_value">
														<div class="range_segment_base">
															<div class="range_segment_label">&nbsp;</div>
															<div class="range_segment range_segment_H   range_value">-</div>
															<div class="range_segment range_segment_U   range_value">-</div>
															<div class="range_segment range_segment_L   range_value">-</div>
															<div class="range_segment range_segment_HUL range_value">-</div>
														</div>
													</td></tr>
												</tbody>
											</table>
											<table border=0 cellspacing=0 cellpadding=0 class="range_value range_border range_border_left range_border_bottom range_segment_inf-01 range_segment_area_ANY">
												<tbody>
													<tr><td class="range_segment range_segment_inf-01 range_value">
														<div class="range_segment_base">
															<div class="range_segment range_segment_ANY range_value">-</div>
														</div>
													</td></tr>
												</tbody>
											</table>
										</td>

										<td align="center" class="">
											<table border=0 cellspacing=0 cellpadding=0 class="range_value range_border range_border_left range_border_top range_segment_01-1 range_segment_area_HUL">
												<tbody>
													<tr><td class="range_segment range_segment_01-1 range_value">
														<div class="range_segment_base">
															<div class="range_segment_label">&nbsp;</div>
															<div class="range_segment range_segment_H   range_value">-</div>
															<div class="range_segment range_segment_U   range_value">-</div>
															<div class="range_segment range_segment_L   range_value">-</div>
															<div class="range_segment range_segment_HUL range_value">-</div>
														</div>
													</td></tr>
												</tbody>
											</table>
											<table border=0 cellspacing=0 cellpadding=0 class="range_value range_border range_border_left range_border_bottom range_segment_01-1 range_segment_area_ANY">
												<tbody>
													<tr><td class="range_segment range_segment_01-1 range_value">
														<div class="range_segment_base">
															<div class="range_segment range_segment_ANY range_value">-</div>
														</div>
													</td></tr>
												</tbody>
											</table>
										</td>

										<td align="center" class="">
											<table border=0 cellspacing=0 cellpadding=0 class="range_value range_border range_border_left range_border_top range_segment_1-10 range_segment_area_HUL">
												<tbody>
													<tr><td class="range_segment range_segment_1-10 range_value">
														<div class="range_segment_base">
															<div class="range_segment_label">&nbsp;</div>
															<div class="range_segment range_segment_H   range_value">-</div>
															<div class="range_segment range_segment_U   range_value">-</div>
															<div class="range_segment range_segment_L   range_value">-</div>
															<div class="range_segment range_segment_HUL range_value">-</div>
														</div>
													</td></tr>
												</tbody>
											</table>
											<table border=0 cellspacing=0 cellpadding=0 class="range_value range_border range_border_left range_border_bottom range_segment_1-10 range_segment_area_ANY">
												<tbody>
													<tr><td class="range_segment range_segment_1-10 range_value">
														<div class="range_segment_base">
															<div class="range_segment range_segment_ANY range_value">-</div>
														</div>
													</td></tr>
												</tbody>
											</table>
										</td>

										<td align="center" class="">
											<table border=0 cellspacing=0 cellpadding=0 class="range_value range_border range_border_top range_segment_10-100 range_segment_area_HUL">
												<tbody>
													<tr><td class="range_segment range_segment_10-100 range_value">
														<div class="range_segment_base">
															<div class="range_segment_label">&nbsp;</div>
															<div class="range_segment range_segment_H   range_value">-</div>
															<div class="range_segment range_segment_U   range_value">-</div>
															<div class="range_segment range_segment_L   range_value">-</div>
															<div class="range_segment range_segment_HUL range_value">-</div>
														</div>
													</td></tr>
												</tbody>
											</table>

											<table border=0 cellspacing=0 cellpadding=0 class="range_value range_border range_border_bottom range_segment_10-100 range_segment_area_ANY">
												<tbody>
													<tr><td class="range_segment range_segment_10-100 range_value">
														<div class="range_segment_base">
															<div class="range_segment range_segment_ANY range_value">-</div>
														</div>
													</td></tr>
												</tbody>
											</table>

										</td>
										<td align="center" class="">
											<table border=0 cellspacing=0 cellpadding=0 class="range_value range_border range_border_top range_segment_100-inf range_segment_area_HUL">
												<tbody>
													<tr><td class="range_segment range_segment_100-inf range_value">
														<div class="range_segment_base">
															<div class="range_segment_label">&nbsp;</div>
															<div class="range_segment range_segment_H   range_value">-</div>
															<div class="range_segment range_segment_U   range_value">-</div>
															<div class="range_segment range_segment_L   range_value">-</div>
															<div class="range_segment range_segment_HUL range_value">-</div>
														</div>
													</td></tr>
												</tbody>
											</table>

											<table border=0 cellspacing=0 cellpadding=0 class="range_value range_border range_border_bottom range_segment_100-inf range_segment_area_ANY">
												<tbody>
													<tr><td class="range_segment range_segment_100-inf range_value">
														<div class="range_segment_base">
															<div class="range_segment range_segment_ANY range_value">-</div>
														</div>
													</td></tr>
												</tbody>
											</table>

										</td>

										<td align="center" class="">
											<table border=0 cellspacing=0 cellpadding=0 class="range_value range_border range_border_right range_border_top range_segment_any range_segment_area_HUL">
												<tbody>
													<tr><td class="range_segment range_segment_any range_value">
														<div class="range_segment_base">
															<div class="range_segment_label">&nbsp;</div>
															<div class="range_segment range_segment_H   range_value">-</div>
															<div class="range_segment range_segment_U   range_value">-</div>
															<div class="range_segment range_segment_L   range_value">-</div>
															<div class="range_segment range_segment_HUL range_value">-</div>
														</div>
													</td></tr>
												</tbody>
											</table>

											<table border=0 cellspacing=0 cellpadding=0 class="range_value range_border range_border_right range_border_bottom range_segment_any range_segment_area_ANY">
												<tbody>
													<tr><td class="range_segment range_segment_any range_value">
														<div class="range_segment_base">
															<div class="range_segment range_segment_ANY range_value">-</div>
														</div>
													</td></tr>
												</tbody>
											</table>

										</td>
									</tr>
								</tbody>
							</table>
						</td>
					</tr>

					<tr>
						<td>
							<table border=0 cellspacing=0 cellpadding=0 class="navigate_range_panel_density" style="">
								<tbody>
									<tr><td><label>Representation Type</label><a href="#" onclick="return click_information_button({hash:'#Data_types'});"><img src="css/information.png" style="width:12px;height:12px;"></a></td></tr>
									<tr><td style="text-align:center;">
										<table border=0 cellspacing=0 cellpadding=0 align="center" style="width:230px;text-align:center;">
											<tbody>
<!--
												<tr>
													<td>
														<table border=0 cellspacing=0 cellpadding=0 class="navigate_range_panel_density_item select_item" style="">
															<tbody><tr>
																<td><input type="radio" name="navigate-range-panel-density-radio-name" id="navigate-range-panel-density-radio-name-any" value="any" checked></td>
																<td><label for="navigate-range-panel-density-radio-name-any">Any</label>&nbsp;<img src="css/075.png" align=center><img src="css/100.png" align=center><img src="css/primitive.png" align=center></td>
															</tr></tbody>
														</table>
													</td>
												</tr>
												<tr>
													<td>
														<table border=0 cellspacing=0 cellpadding=0 class="navigate_range_panel_density_item" style="">
															<tbody><tr>
																<td><input type="radio" name="navigate-range-panel-density-radio-name" id="navigate-range-panel-density-radio-name-primitive" value="primitive"></td>
																<td><label for="navigate-range-panel-density-radio-name-primitive">$LOCALE{ELEMENT}</label>&nbsp;<img src="css/primitive.png" align=center></td>
															</tr></tbody>
														</table>
													</td>
												</tr>
												<tr>
													<td>
														<table border=0 cellspacing=0 cellpadding=0 class="navigate_range_panel_density_item" style="">
															<tbody><tr>
																<td><input type="radio" name="navigate-range-panel-density-radio-name" id="navigate-range-panel-density-radio-name-100" value="100-inf"></td>
																<td><label for="navigate-range-panel-density-radio-name-100">$LOCALE{ELEMENT_COMPOUND}</label>&nbsp;<img src="css/primitive.png" align=center><img src="css/100.png" align=center></td>
															</tr></tbody>
														</table>
													</td>
												</tr>
-->

												<tr>
													<td>
														<table border=0 cellspacing=0 cellpadding=0 class="navigate_range_panel_density_item" style="">
															<tbody><tr>
																<td><input type="checkbox" name="navigate-range-panel-density-checkbox-name-element" id="navigate-range-panel-density-checkbox-name-element" value="element" checked></td>
																<td><label for="navigate-range-panel-density-checkbox-name-element">$LOCALE{ELEMENT}</label>&nbsp;<img src="css/primitive.png" align=center></td>
															</tr></tbody>
														</table>
													</td>
												</tr>
												<tr>
													<td>
														<table border=0 cellspacing=0 cellpadding=0 class="navigate_range_panel_density_item" style="">
															<tbody><tr>
																<td><input type="checkbox" name="navigate-range-panel-density-checkbox-name-complete-compound" id="navigate-range-panel-density-checkbox-name-complete-compound" value="complete-compound" checked></td>
																<td><label for="navigate-range-panel-density-checkbox-name-complete-compound">$LOCALE{COMPLETE_COMPOUND}</label>&nbsp;<img src="css/100.png" align=center></td>
															</tr></tbody>
														</table>
													</td>
												</tr>
												<tr>
													<td>
														<table border=0 cellspacing=0 cellpadding=0 class="navigate_range_panel_density_item" style="">
															<tbody><tr>
																<td><input type="checkbox" name="navigate-range-panel-density-checkbox-name-incomplete-compound" id="navigate-range-panel-density-checkbox-name-incomplete-compound" value="incomplete-compound" checked></td>
																<td><label for="navigate-range-panel-density-checkbox-name-incomplete-compound">$LOCALE{INCOMPLETE_COMPOUND}</label>&nbsp;<img src="css/075.png" align=center></td>
															</tr></tbody>
														</table>
													</td>
												</tr>

											</tbody>
										</table>
									</td></tr>
<!--
									<tr><td>
										<table border=0 cellspacing=0 cellpadding=0><tbody>
											<tr>
												<td valign="top"><input type="checkbox" name="navigate-range-panel-only-taid" id="navigate-range-panel-only-taid" value="true"></td>
												<td valign="top" class="navigate_range_panel_only_taid"><label for="navigate-range-panel-only-taid">Show only TA matches(*)</label></td>
											</tr>
											<tr>
												<td valign="top" colspan="2" class="navigate_range_panel_only_taid"><label for="navigate-range-panel-only-taid">* listed in Terminologia Anatomica</label></td>
											</tr>
										</tbody></table>
									</td></tr>
-->
								</tbody>
							</table>

						</td>
					</tr>

				</tbody>
			</table>
			<div id="navigate-range-panel-filter-combobox-render"></div>
			<div id="navigate-range-panel-cube-volume-combobox-render"></div>
			<div id="navigate-range-panel-cube-volume-zmax-numberfield-render"></div>
			<div id="navigate-range-panel-cube-volume-zmin-numberfield-render"></div>
			<div id="navigate-range-panel-range-combobox-render"></div>
			<div id="navigate-range-panel-zmax-numberfield-render"></div>
			<div id="navigate-range-panel-zmin-numberfield-render"></div>
			<div id="navigate-range-panel-condition-textfield-render"></div>
			<div id="navigate-range-panel-num-numberfield-render"></div>
		</div>
	</div>
</div>

<div id="bp3d-content-panel-header-contentEl" align="" class="x-hide-display">
	<table cellpadding="0" cellspacing="0" boder="0" width=100%>
		<tbody>
			<tr>
				<td width=44 align="center" valign="top" rowspan="2">
					<img src="css/2.png" width=44 height=44>
				</td>
				<td width=100 align="center" rowspan="2">
					<div id="bp3d-content-panel-header-content-view-combobox-render" style="margin-left:10px;display:none;"></div>
					<table cellpadding="0" cellspacing="0" boder="0" id="bp3d-content-panel-header-content-view-render">
						<tbody>
							<tr>
								<td style="width:32px;">
									<div id="bp3d-content-panel-header-content-view-thump-render" style="margin:0px 4px;width:24px;height:21px;"></div>
								</td>
								<td style="width:32px;">
									<div id="bp3d-content-panel-header-content-view-list-render" style="margin:0px 4px;width:24px;height:21px;"></div>
								</td>
							</tr>
						</tbody>
					</table>
				</td>
				<td width=80>
					<table cellpadding="0" cellspacing="0" boder="0" style="width:80px;">
						<tbody>
							<tr style="">
								<td align="center" style="width:80px;">
									<label style="">View</label>
								</td>
							</tr>
							<tr style="height:30px;">
								<td align="" style="width:80px;">
									<div id="bp3d-content-panel-header-content-position-combobox-render"></div>
								</td>
							</tr>
						</tbody>
					</table>
				</td>
				<td width=100>
					<table cellpadding="0" cellspacing="0" boder="0" style="width:100px;">
						<tbody>
							<tr>
								<td align="center">
									<label style="">Sort by</label>
								</td>
							</tr>
							<tr style="height:30px;">
								<td style="width:120px;">
									<div id="bp3d-content-panel-header-content-sort-combobox-render"></div>
								</td>
							</tr>
						</tbody>
					</table>
				</td>
				<td rowspan="2">
					<table cellpadding="0" cellspacing="0" boder="0" width="" style="margin-left:50px;">
						<tbody>
							<tr style="height:23px;">
								<td colspan="" style="">
									<table cellpadding="0" cellspacing="0" boder="0" style="">
										<tbody>
											<tr>
												<td valign="middle" nowrap style="padding-left:1.5em;"><label style="font-size:14px;">Models for concepts in</label></td>
												<td valign="middle" nowrap style="font-size:14px;font-weight:bold;padding-left:0.5em;"><label style="">&quot;</label><label id="bp3d-buildup-logic-contents-label" style=""></label><label>&quot;</label></td>
											</tr>
										</tbody>
									</table>
								</td>
							</tr>
							<tr style="height:32px;">
								<td>
									<table cellpadding="0" cellspacing="0" boder="0" style="">
										<tbody>
											<tr>
												<td rowspan="2"><label style="line-height:18px;vertical-align:top;margin-left:1em;white-space:nowrap;">$LOCALE{ELEMENT_PRIMARY}:</label><img src="css/primitive.png"></td>
												<td align="right" rowspan=2><label style="margin-left:1em;margin-right:0.5em;white-space:nowrap;">$LOCALE{COMPOUND_SECONDARY}:</label></td>
												<td align="center"><label style="">Good</label></td>
												<td align="center"><label style="">--</label></td>
												<td align="center"><label style="">poor</label></td>
											</tr>
											<tr>
												<td align="center"><img src="css/100.png"></td>
												<td align="center"><img src="css/035.png"></td>
												<td align="center"><img src="css/015.png"></td>
											<tr>
										</tbody>
									</table>
								</td>
							</tr>
						</tbody>
					</table>
				</td>
			</tr>
			<tr>
				<td colspan=2 nowrap>

<input type="checkbox" name="bp3d-content-panel-header-content-degenerate-same-shape-icons" id="bp3d-content-panel-header-content-degenerate-same-shape-icons" value="true" checked><label for="bp3d-content-panel-header-content-degenerate-same-shape-icons">Show only Unique models</label>

				</td>
			</tr>
		</tbody>
	</table>
</div>

HTML
if($agInterfaceType eq '4'){
	$CONTENTS .= <<HTML;
<div id="ag-image-rotate-box" align="left" class="x-hide-display">
	<table cellpadding="0" cellspacing="0" boder="0" align="center" width="80" height="53" style="float:left;"><tr>
		<td align="center" valign="middle"><a id="ag-command-btn-move" class="ag_command_btn" href="#"></a></td>
		<td align="center" valign="middle"><a id="ag-command-btn-rotate" class="ag_command_btn" href="#"></a></td>
	</tr></table>

	<a id="ag-image-rotate-front" class="ag_image_rotate" href="#" onclick="setRotate(  0,0);this.blur();return false;">
<!--		<img src="img_angle/000_000.png"/>-->
		<table><tr><td valign="bottom" align="left">H:0</td><td valign="bottom" align="right">V:0</td></tr></table>
	</a>
	<a id="ag-image-rotate-left" class="ag_image_rotate" href="#" onclick="setRotate( 90,0);this.blur();return false;">
<!--		<img src="img_angle/075_000.png"/>-->
		<table><tr><td valign="bottom" align="left">H:90</td><td valign="bottom" align="right">V:0</td></tr></table>
	</a>
	<a id="ag-image-rotate-back" class="ag_image_rotate" href="#" onclick="setRotate(180,0);this.blur();return false;">
<!--		<img src="img_angle/180_000.png"/>-->
		<table><tr><td valign="bottom" align="left">H:180</td><td valign="bottom" align="right">V:0</td></tr></table>
	</a>
	<a id="ag-image-rotate-right" class="ag_image_rotate" href="#" onclick="setRotate(270,0);this.blur();return false;">
<!--		<img src="img_angle/285_000.png"/>-->
		<table><tr><td valign="bottom" align="left">H:270</td><td valign="bottom" align="right">V:0</td></tr></table>
	</a>
	<a id="ag-image-rotate-top" class="ag_image_rotate" href="#" onclick="setRotate(180,90);this.blur();return false;">
<!--		<img src="img_angle/180_105.png"/>-->
		<table><tr><td valign="bottom" align="left">H:180</td><td valign="bottom" align="right">V:90</td></tr></table>
	</a>
	<a id="ag-image-rotate-bottom" class="ag_image_rotate" href="#" onclick="setRotate(0,270);this.blur();return false;">
<!--		<img src="img_angle/000_285.png"/>-->
		<table><tr><td valign="bottom" align="left">H:0</td><td valign="bottom" align="right">V:270</td></tr></table>
	</a>
	<div style="float:left;">
		<div>
			<a href="#" onclick="try{_dump('click');ag_focus(false,true);this.blur();return false;}catch(e){_dump(e);}" style="float:left;margin:4px 1px 4px 2px;"><img src="css/focus_center.png"/></a>
			<a href="#" onclick="try{_dump('click');ag_focus(false);this.blur();return false;}catch(e){_dump(e);}" style="float:left;margin:4px 1px 4px 2px;"><img src="css/focus_zoom.png"/></a>
		</div>
		<div>
			<div id="ag-command-autorotate-chechbox-render"></div>
		</div>
	</div>

HTML
	$CONTENTS .= qq|	<div style="float:right;"|;
	$CONTENTS .= qq| class="x-hide-display"| if($gridHidden eq 'true');
	$CONTENTS .= qq|>\n|;
$CONTENTS .= <<HTML;
		<table class="ag-image-grid-box-class" cellpadding="0" cellspacing="0" boder="0" height="30">
			<tr><td colspan="2" class="ag_command_title"><div><div id="ag-command-grid-render">Grid</div>&nbsp;On/Off</div></td>
			<tr>
				<td class="ag_command" width="72" height="20" style="padding-bottom:0px;"><div id="ag-command-grid-color-render"></div></td>
				<td class="ag_command" width="63" style="padding-bottom:0px;"><div id="ag-command-grid-len-render"></div></td>
			</tr>
		</table>
	</div>

	<div style="float:right;">
		<table class="ag-image-zoom-box-class" cellpadding="0" cellspacing="0" boder="0" height="30">
			<tr><td colspan="4" class="ag_command_title"><div>Zoom</div></td></tr>
			<tr>
				<td valign="middle" align="right" width="20"><img src="img/icon_move_left.gif" onclick="anatomoZoomDownButton();"/></td>
				<td valign="middle"><div id="ag-command-zoom-slider-render"></div></td>
				<td valign="middle" align="left" width="20"><img src="img/icon_move_right.gif" onclick="anatomoZoomUpButton();"/></td>
				<td valign="middle">
					<table cellpadding="0" cellspacing="0" boder="0" align="center">
						<tr><td rowspan="2"><div id="ag-command-zoom-text-render"></div></td><td><img src="css/spinner-up.png" onclick="anatomoZoomUpButton();"/></td></tr>
						<tr><td><img src="css/spinner-down.png" onclick="anatomoZoomDownButton();"/></td></tr>
					</table>
				</td>
			</tr>
		</table>
	</div>
</div>
HTML
}
$CONTENTS .= <<HTML;

<div id="anatomography-image-contentEl" class="x-hide-display" style="position:relative;">
	<table width="100%" height="100%" cellpadding="0" cellspacing="0">
		<tr><td align="center" valign="center" style="position:relative;">
			<img id="ag_img" src="resources/images/default/s.gif">
		</td></tr>
	</table>
	<div id="ag-copyright" class="x-hide-display">
		<label>&copy;2010 DBCLS - <a id="ag-copyright-link" href="#" target="_blank" onclick="this.blur();">Anatomography</a>
	</div>

HTML
if($agInterfaceType eq '5'){
	$CONTENTS .= <<HTML;

	<div id="ag-image-command-box" align="center">

		<div id="ag-image-rotate-box" align="center" class="x-hide-display" style="position:relative; width:76px;background-color:transparent;">
			<table id="ag-image-button-box" cellpadding="0" cellspacing="0" boder="0" align="center" width="70" height="36" style="float:center;"><tr>
				<td align="center" valign="middle"><a id="ag-command-btn-move" class="ag_command_btn" href="#"></a></td>
				<td align="center" valign="middle"><a id="ag-command-btn-rotate" class="ag_command_btn" href="#"></a></td>
			</tr></table>

			<div id="ag-command-ipad" class="x-hide-display">
				<a id="ag-command-btn-grid" class="ag_command_btn" href="#"></a>
				<div id="ag-command-grid-color-ipad"></div>
				<select id="ag-command-grid-len-ipad" size="1">
					<option value="1">1mm</option>
					<option value="5">5mm</option>
					<option value="10">10mm</option>
					<option value="50">50mm</option>
					<option value="100">100mm</option>
				</select>
			</div>

			<div id="ag-command-rotate-button-render"></div>

			<a href="#" onclick="try{_dump('click');ag_focus(false,true);this.blur();return false;}catch(e){_dump(e);}" style="float:left;margin:4px 1px 4px 2px;"><img id="ag-command-focus-center-button" src="css/focus_center.png"/></a>
			<a href="#" onclick="try{_dump('click');ag_focus(false);this.blur();return false;}catch(e){_dump(e);}" style="float:left;margin:4px 1px 4px 2px;"><img id="ag-command-focus-button" src="css/focus_zoom.png"/></a>
			<div id="ag-command-autorotate-chechbox-render"><label id="ag-command-autorotate-chechbox-label">Auto<br>rotation</label></div>
HTML
	$CONTENTS .= qq|			<div id="ag-image-grid-box" style="float:center;width:80px;height:19px;overflow:hidden;"|;
	$CONTENTS .= qq| class="x-hide-display"| if($gridHidden eq 'true');
	$CONTENTS .= qq|>\n|;
	$CONTENTS .= <<HTML;
				<table class="ag-image-grid-box-class" cellpadding="0" cellspacing="0" boder="0" style="width:78px;height:62px;">
					<tr><td colspan="2" class="ag_command_title" style="padding-bottom:2px;vertical-align: top;"><div><div id="ag-command-grid-render">Grid</div>&nbsp;On/Off</div></td>
					<tr><td class="ag_command" style="padding-bottom:0px;padding-left:2px;"><div id="ag-command-grid-color-render"></div></td></tr>
					<tr><td class="ag_command" style="padding-bottom:0px;padding-left:2px;"><div id="ag-command-grid-len-render"></div></td></tr>
				</table>
			</div>

			<div id="ag-image-zoom-box" style="float:center;">
				<div style="width:46px;height:15px;margin-top:4px;overflow:hidden;" align="center"><a id="ag-command-zoom-btn-up" href="#" onclick="anatomoZoomUpButton();this.blur();return false;"><br/></a></div>
				<div id="ag-command-zoom-slider-render" style="width:46px;height:300px;"></div>
				<div style="position:relative;width:46px;height:15px;overflow:hidden;" align="center"><a id="ag-command-zoom-btn-down" href="#" onclick="anatomoZoomDownButton();this.blur();return false;"><br/></a></div>
				<table id="ag-image-zoom-text-box" cellpadding="0" cellspacing="0" boder="0" align="center" width="46">
					<tr><td rowspan="2"><div id="ag-command-zoom-text-render"></div></td><td><div style="width:16px;height:10px;overflow:hidden;"><a id="ag-command-zoom-spinner-up" href="#" onclick="anatomoZoomUpButton();this.blur();return false;"></a></div></td></tr>
					<tr><td><div style="width:16px;height:10px;overflow:hidden;"><a id="ag-command-zoom-spinner-down" href="#" onclick="anatomoZoomDownButton();this.blur();return false;"></a></div></td></tr>
				</table>
			</div>
		</div>

	</div>
HTML
}


$CONTENTS .= <<HTML;
</div>

<div id="rotImgDiv">
	<table cellpadding="2" cellspacing="0"><tr><td id="rotImgDivRotateH" align="left"></td><td id="rotImgDivRotateV" align="right"></td></tr></table>
</div>

<div id="ag-link-window-contentEl" class="x-hide-display">
	<table cellpadding="0" cellspacing="0" boder="0" align="center" style="width:100%;">
		<tbody>
			<tr><td colspan="3"><div id="ag-link-window-page-reproduction-label-renderTo" style="font-size:1.5em;color:#15428b;"></div></td></tr>
			<tr><td colspan="3"><div style="position:relative;height:24px;"><div id="ag-link-window-page-reproduction-textfield-renderTo" style="position:absolute;left:10px;right:10px;"></div></div></td></tr>

			<tr><td colspan="3"><hr size="1"></td></tr>

			<tr><td colspan="3">
				<table cellpadding="0" cellspacing="0" boder="0" align="left" style="width:100%;">
					<tbody><tr>
						<td><div id="ag-link-window-image-re-use-label-renderTo" style="font-size:1.5em;color:#15428b;white-space: nowrap;"></div></td>
						<td>
							<table cellpadding="0" cellspacing="0" boder="0" align="left" style="width:120px;">
								<tbody><tr>
									<td><div id="ag-link-window-image-re-use-size-label-renderTo" style="font-size:1.1em;color:#15428b;maring-left:2em;"></div></td>
									<td>
										<table cellpadding="0" cellspacing="0" boder="0" align="left" style="width:100px;border:1px solid #c0c0c0;">
											<tbody><tr>
												<td><div id="ag-link-window-image-re-use-size-s-button-renderTo"></div></td>
												<td><div id="ag-link-window-image-re-use-size-m-button-renderTo"></div></td>
												<td><div id="ag-link-window-image-re-use-size-l-button-renderTo"></div></td>
											</tr></tbody>
										</table>
									</td>
								</tr></tbody>
							</table>
						</td>
					</tr></tbody>
				</table>
			</td></tr>
			<tr>
				<td style="width:40px;"><div id="ag-link-window-image-re-use-still-label-renderTo" style="margin-left:1em;"></div></td>
				<td style="width:200px;"><div style="position:relative;height:24px;"><div id="ag-link-window-image-re-use-still-textfield-renderTo" style="position:absolute;left:10px;right:10px;"></div></div></td>
				<td style="width:50px;"><div id="ag-link-window-image-re-use-still-button-renderTo"></div></td>
			</tr>
			<tr>
				<td style="width:40px;"><div id="ag-link-window-image-re-use-rotate-label-renderTo" style="margin-left:1em;"></div></td>
				<td style="width:200px;"><div style="position:relative;height:24px;"><div id="ag-link-window-image-re-use-rotate-textfield-renderTo" style="position:absolute;left:10px;right:10px;"></div></div></td>
				<td style="width:50px;"><div id="ag-link-window-image-re-use-rotate-button-renderTo"></div></td>
			</tr>

			<tr><td colspan="3"><hr size="1"></td></tr>

			<tr><td colspan="3"><div id="ag-link-window-url-checkbox-renderTo"></div></td></tr>

			<tr><td colspan="3"><hr size="1"></td></tr>
			<tr><td colspan="3"><div id="ag-link-window-url-table-fieldset-renderTo"></div></td></tr>

		</tbody>
	</table>
</div>

<div id="ag-embed-window-contentEl" class="x-hide-display">
	<table cellpadding="0" cellspacing="0" boder="0" align="center" style="width:100%;">
		<tbody>
			<tr><td colspan="3"><div id="ag-embed-window-page-reproduction-label-renderTo" style="font-size:1.5em;color:#15428b;"></div></td></tr>
			<tr><td colspan="3"><div style="position:relative;height:24px;"><div id="ag-embed-window-page-reproduction-textfield-renderTo" style="position:absolute;left:10px;right:10px;"></div></div></td></tr>

			<tr><td colspan="3"><hr size="1"></td></tr>

			<tr><td colspan="3">
				<table cellpadding="0" cellspacing="0" boder="0" align="left" style="width:100%;">
					<tbody><tr>
						<td><div id="ag-embed-window-image-re-use-label-renderTo" style="font-size:1.5em;color:#15428b;white-space: nowrap;"></div></td>
						<td>
							<table cellpadding="0" cellspacing="0" boder="0" align="left" style="width:120px;">
								<tbody><tr>
									<td><div id="ag-embed-window-image-re-use-size-label-renderTo" style="font-size:1.1em;color:#15428b;maring-left:2em;"></div></td>
									<td>
										<table cellpadding="0" cellspacing="0" boder="0" align="left" style="width:100px;border:1px solid #c0c0c0;">
											<tbody><tr>
												<td><div id="ag-embed-window-image-re-use-size-s-button-renderTo"></div></td>
												<td><div id="ag-embed-window-image-re-use-size-m-button-renderTo"></div></td>
												<td><div id="ag-embed-window-image-re-use-size-l-button-renderTo"></div></td>
											</tr></tbody>
										</table>
									</td>
								</tr></tbody>
							</table>
						</td>
					</tr></tbody>
				</table>
			</td></tr>
			<tr>
				<td style="width:40px;"><div id="ag-embed-window-image-re-use-still-label-renderTo" style="margin-left:1em;"></div></td>
				<td style="width:300px;"><div style="position:relative;height:24px;"><div id="ag-embed-window-image-re-use-still-textfield-renderTo" style="position:absolute;left:10px;right:10px;"></div></div></td>
				<td style="width:50px;"><div id="ag-embed-window-image-re-use-still-button-renderTo"></div></td>
			</tr>
			<tr>
				<td style="width:40px;"><div id="ag-embed-window-image-re-use-rotate-label-renderTo" style="margin-left:1em;"></div></td>
				<td style="width:300px;"><div style="position:relative;height:24px;"><div id="ag-embed-window-image-re-use-rotate-textfield-renderTo" style="position:absolute;left:10px;right:10px;"></div></div></td>
				<td style="width:50px;"><div id="ag-embed-window-image-re-use-rotate-button-renderTo"></div></td>
			</tr>

			<tr><td colspan="3"><hr size="1"></td></tr>

			<tr><td colspan="3"><div id="ag-embed-window-embed-label-renderTo" style="font-size:1.5em;color:#15428b;"></div></td></tr>
			<tr><td colspan="3"><div style="position:relative;height:68px;"><div id="ag-embed-window-embed-textarea-renderTo" style="position:absolute;left:10px;right:10px;"></div></div></td></tr>

			<tr><td colspan="3"><hr size="1"></td></tr>

			<tr><td colspan="3"><div id="ag-embed-window-url-checkbox-renderTo"></div></td></tr>
		</tbody>
	</table>
</div>

<div id="bp3d-link-window-contentEl" class="x-hide-display">
	<table cellpadding="0" cellspacing="0" boder="0" align="center" style="width:100%;">
		<tbody>
<!--
			<tr>
				<td colspan="3"><div id="bp3d-link-window-image-re-use-label-renderTo" style="font-size:1.5em;color:#15428b;white-space: nowrap;"></div></td>
			</tr>
-->
			<tr>
				<td style="width:30px;"><div id="bp3d-link-window-image-re-use-view-label-renderTo" style="margin-left:1em;"></div></td>
				<td colspan="2">
					<table cellpadding="0" cellspacing="0" boder="0" align="left" style="width:250px;margin-left:1em;">
						<tbody><tr>
							<td><div id="bp3d-link-window-image-re-use-view-rotate-button-renderTo"></div></td>
							<td><div id="bp3d-link-window-image-re-use-view-f-button-renderTo"></div></td>
							<td><div id="bp3d-link-window-image-re-use-view-b-button-renderTo"></div></td>
							<td><div id="bp3d-link-window-image-re-use-view-l-button-renderTo"></div></td>
							<td><div id="bp3d-link-window-image-re-use-view-r-button-renderTo"></div></td>
						</tr></tbody>
					</table>
				</td>
			</tr>
			<tr>
				<td style="width:30px;"><div id="bp3d-link-window-image-re-use-size-label-renderTo" style="margin-left:1em;"></div></td>
				<td colspan="2">
					<table cellpadding="0" cellspacing="0" boder="0" align="left" style="width:66px;margin-left:1em;">
						<tbody><tr>
							<td><div id="bp3d-link-window-image-re-use-size-s-button-renderTo"></div></td>
							<td><div id="bp3d-link-window-image-re-use-size-l-button-renderTo"></div></td>
						</tr></tbody>
					</table>
				</td>
			</tr>
			<tr>
				<td style="width:30px;"><div id="bp3d-link-window-image-re-use-still-label-renderTo" style="margin-left:1em;"></div></td>
				<td colspan="2"><div style="position:relative;height:24px;"><div id="bp3d-link-window-image-re-use-still-textfield-renderTo" style="position:absolute;left:10px;right:10px;"></div></div></td>
			</tr>
			<tr>
				<td colspan="2"></td>
				<td style="width:50px;"><div id="bp3d-link-window-image-re-use-still-button-renderTo"></div></td>
			</tr>
		</tbody>
	</table>
</div>

<div id="ag-comment-panel-header-contentEl" align="" class="x-hide-display">
	<table cellpadding="0" cellspacing="0" boder="0" width=100%>
		<tbody>
			<tr>
				<td width=44 align="center" valign="top" rowspan=2>
					<img src="css/5.png" width=44 height=44>
				</td>
				<td colspan=2 nowrap>
					<label>Option : Import map URL</label>
				</td>
			</tr>
			<tr>
				<td>
					<a href="#" style="float:left;width:auto;margin-left:1em;" onclick="ag_extensions.import_parts_pins.openWindow({title:'URL to pallet',animateTarget:Ext.get(this)});return false;"><img src="css/btn_URLtoPallet.png"></a>
<!--
					<table border="0" cellpadding="0" cellspacing="0" class="x-btn-wrap x-btn " style="float:left;width:auto;margin-left:1em;width:106px;"><tbody><tr>
						<td class="x-btn-left"><i>&nbsp;</i></td>
						<td class="x-btn-center"><em unselectable="on"><button class="x-btn-text" type="button" onclick="ag_extensions.import_parts_pins.openWindow({title:'URL to pallet',animateTarget:Ext.get(this)})">URL to pallet</button></em></td><td class="x-btn-right"><i>&nbsp;</i></td>
					</tr></tbody></table>
-->
				</td>
				<td>
					<a href="#" style="float:left;width:auto;margin-left:1em;" onclick="ag_extensions.url2text.openWindow({title:'decode URL',animateTarget:Ext.get(this)});return false;"><img src="css/btn_decodeURL.png"></a>
<!--
<table border="0" cellpadding="0" cellspacing="0" class="x-btn-wrap x-btn " style="float:left;width:auto;margin-left:0.5em;width:106px;"><tbody><tr><td class="x-btn-left"><i>&nbsp;</i></td><td class="x-btn-center"><em unselectable="on"><button class="x-btn-text" type="button" onclick="ag_extensions.url2text.openWindow({title:'decode URL',animateTarget:Ext.get(this)})">decode URL</button></em></td><td class="x-btn-right"><i>&nbsp;</i></td></tr></tbody></table>
-->
				</td>
			</tr>
		</tbody>
	</table>
</div>
<!--
<div id="ag-point-search-header-content" align="center" class="x-hide-display">
	<table id="ag-point-search-header-content-table" cellpadding="0" cellspacing="0" boder="0">
		<tr><td>
			<table cellpadding="0" cellspacing="0" boder="0" width="100%"><tr>
				<td class="ag_grid_command" style="width:76px;"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;" align="right">Screen(pixel)</div></td>
				<td class="ag_grid_command" style="width:50px;">
					<table cellpadding="0" cellspacing="0" boder="0" width="100%"><tr>
						<td class="ag_grid_command"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;font-weight:normal;border-right-width:0px;" align="right">X:</div></td>
						<td class="ag_grid_command"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;font-weight:normal;" align="left" id="ag-point-search-header-content-distance-x-render"></div></td>
					</tr></table>
				</td>
				<td class="ag_grid_command" style="width:50px;">
					<table cellpadding="0" cellspacing="0" boder="0" width="100%"><tr>
						<td class="ag_grid_command"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;font-weight:normal;border-right-width:0px;" align="right">Y:</div></td>
						<td class="ag_grid_command"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;font-weight:normal;" align="left" id="ag-point-search-header-content-distance-y-render"></div></td>
					</tr></table>
				</td>

				<td class="ag_grid_command" style="width:74px;"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;" align="right">Range(mm3)</div></td>
				<td class="ag_grid_command" style="width:36px;"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;font-weight:normal;" align="center" id="ag-point-search-header-content-distance-z-render"></div></td>

				<td class="" style="background:#d0def0;"><div style="height:20px;line-height:20px;border-right:0px;" align="center" id="ag-point-search-header-content-distance-render"></div></td>
			</tr></table>
		</td></tr>
		<tr><td>
			<table cellpadding="0" cellspacing="0" boder="0" width="100%"><tr>
				<td class="ag_grid_command" style="width:88px;"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;" align="right">Coordinate(mm)</div></td>
				<td class="ag_grid_command" style="width:72px;">
					<table cellpadding="0" cellspacing="0" boder="0" width="100%"><tr>
						<td class="ag_grid_command"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;font-weight:normal;border-right-width:0px;" align="right">X:</div></td>
						<td class="ag_grid_command"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;font-weight:normal;" align="left" id="ag-point-search-header-content-coordinate-x-render"></div></td>
					</tr></table>
				</td>
				<td class="ag_grid_command" style="width:72px;">
					<table cellpadding="0" cellspacing="0" boder="0" width="100%"><tr>
						<td class="ag_grid_command"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;font-weight:normal;border-right-width:0px;" align="right">Y:</div></td>
						<td class="ag_grid_command"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;font-weight:normal;" align="left" id="ag-point-search-header-content-coordinate-y-render"></div></td>
					</tr></table>
				</td>
				<td class="ag_grid_command" style="width:72px;">
					<table cellpadding="0" cellspacing="0" boder="0" width="100%"><tr>
						<td class="ag_grid_command"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;font-weight:normal;border-right-width:0px;" align="right">Z:</div></td>
						<td class="ag_grid_command"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;font-weight:normal;" align="left" id="ag-point-search-header-content-coordinate-z-render"></div></td>
					</tr></table>
				</td>
				<td class="ag_grid_command"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;border-right:0px;" align="left" id="ag-point-search-header-content-coordinate-render"> </div></td>
			</tr></table>
		</td></tr>
	</table>
</div>
-->
<div id="ag-point-search-header-content" align="center" class="x-hide-display">
	<table id="ag-point-search-header-content-table" cellpadding="0" cellspacing="0" boder="0">
		<tr><td>
			<table cellpadding="0" cellspacing="0" boder="0" width="100%"><tr>
				<td class="ag_grid_command" style="width:66px;"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;" align="right">Origin(mm)</div></td>
				<td class="ag_grid_command" style="width:72px;">
					<table cellpadding="0" cellspacing="0" boder="0" width="100%"><tr>
						<td class="ag_grid_command"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;font-weight:normal;border-right-width:0px;" align="right">X:</div></td>
						<td class="ag_grid_command"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;font-weight:normal;width:53px;text-align:right;padding:2px 4px 2px 2px;font-size:1.1em;" align="left" id="ag-point-search-header-content-coordinate-x-render"></div></td>
					</tr></table>
				</td>
				<td class="ag_grid_command" style="width:72px;">
					<table cellpadding="0" cellspacing="0" boder="0" width="100%"><tr>
						<td class="ag_grid_command"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;font-weight:normal;border-right-width:0px;" align="right">Y:</div></td>
						<td class="ag_grid_command"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;font-weight:normal;width:53px;text-align:right;padding:2px 4px 2px 2px;font-size:1.1em;" align="left" id="ag-point-search-header-content-coordinate-y-render"></div></td>
					</tr></table>
				</td>
				<td class="ag_grid_command" style="width:72px;">
					<table cellpadding="0" cellspacing="0" boder="0" width="100%"><tr>
						<td class="ag_grid_command"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;font-weight:normal;border-right-width:0px;" align="right">Z:</div></td>
						<td class="ag_grid_command"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;font-weight:normal;width:53px;text-align:right;padding:2px 4px 2px 2px;font-size:1.1em;" align="left" id="ag-point-search-header-content-coordinate-z-render"></div></td>
					</tr></table>
				</td>
				<td class="ag_grid_command"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;border-right:0px;" align="left" id="ag-point-search-header-content-coordinate-render"> </div></td>
			</tr></table>
		</td></tr>
	</table>
		<tr><td>
			<table cellpadding="0" cellspacing="0" boder="0" width="100%"><tr>
<!--
				<td class="ag_grid_command" style="width:76px;"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;" align="right">Screen(pixel)</div></td>
				<td class="ag_grid_command" style="width:50px;">
					<table cellpadding="0" cellspacing="0" boder="0" width="100%"><tr>
						<td class="ag_grid_command"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;font-weight:normal;border-right-width:0px;" align="right">X:</div></td>
						<td class="ag_grid_command"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;font-weight:normal;" align="left" id="ag-point-search-header-content-distance-x-render"></div></td>
					</tr></table>
				</td>
				<td class="ag_grid_command" style="width:50px;">
					<table cellpadding="0" cellspacing="0" boder="0" width="100%"><tr>
						<td class="ag_grid_command"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;font-weight:normal;border-right-width:0px;" align="right">Y:</div></td>
						<td class="ag_grid_command"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;font-weight:normal;" align="left" id="ag-point-search-header-content-distance-y-render"></div></td>
					</tr></table>
				</td>
-->
				<td class="ag_grid_command" style="width:68px;"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;" align="right">Radius(mm)</div></td>
				<td class="ag_grid_command" style="width:36px;"><div class="x-toolbar x-small-editor" style="height:20px;line-height:20px;font-weight:normal;width:29px;text-align:right;padding:2px 4px 2px 2px;font-size:1.1em;" align="center" id="ag-point-search-header-content-distance-z-render"></div></td>

				<td class="" style="background:#d0def0;"><div style="height:20px;line-height:20px;border-right:0px;padding-left:10px;" align="left" id="ag-point-search-header-content-distance-render"></div></td>
			</tr></table>
		</td></tr>
</div>

<form method="POST" id="ag-open-url-form" class="x-hide-display"><textarea id="ag-open-url-form-url" name="url"></textarea></form>
<form method="POST" id="ag-post-form" class="x-hide-display"></form>
<form method="POST" id="ag-print-form" class="x-hide-display"></form>

</body>
</html>
HTML

#print $LOG __LINE__,":",&Data::Dumper::Dumper(\@cookies);

&cgi_lib::common::printContent(&cgi_lib::common::html_compress($CONTENTS),undef,\@cookies);
