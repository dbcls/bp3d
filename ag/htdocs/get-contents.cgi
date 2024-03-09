#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

say __LINE__ unless(exists($ENV{'REQUEST_METHOD'}));

use Image::Info qw(image_info dim);
use Image::Magick;
use Storable;
use Encode;
use JSON::XS;
use File::Path;
use File::Spec;
use File::Spec::Functions qw(catdir catfile);
use File::Basename;
use Data::Dumper;

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI::Cookie;
use Cwd;
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'API'),&Cwd::abs_path(&catdir($FindBin::Bin,'..','lib')),&Cwd::abs_path(&catdir($FindBin::Bin,'..','..','ag-common','lib'));
use cgi_lib::common;
use AG::login;

my $JSONXS = JSON::XS->new->utf8->indent(0)->canonical(1);

say __LINE__ unless(exists($ENV{'REQUEST_METHOD'}));

require "common.pl";
require "common_db.pl";

my $dbh = &get_dbh();

say __LINE__ unless(exists($ENV{'REQUEST_METHOD'}));

#open(LOG,"> $FindBin::Bin/logs/1cea17e81e368f1c1641dd506a43205f.get-contents.txt");

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);


#DEBUG 常に削除
#delete $FORM{'parent'} if(exists($FORM{'parent'}));
my $lsdb_OpenID;
my $lsdb_Auth;
my $parentURL = $FORM{'parent'} if(exists($FORM{'parent'}));
my $parent_text;
my $lsdb_Config;
my $lsdb_Identity;
if(defined $parentURL){
	($lsdb_OpenID,$lsdb_Auth) = &openidAuth($parentURL);
}elsif(exists($FORM{'openid_url'}) && exists($FORM{'openid_session'})){
	($lsdb_OpenID,$lsdb_Auth,$lsdb_Config,$lsdb_Identity) = &AG::login::openidAuthSession($FORM{'openid_url'},$FORM{'openid_session'});
}

=pod
my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
my $filetime = sprintf("%04d/%02d/%02d",$year+1900,$mon+1,$mday);
my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = fileparse($0,@extlist);
my $log_dir = &catdir($FindBin::Bin,'logs',$filetime);
if(exists $ENV{'HTTP_X_FORWARDED_FOR'}){
	my @H = split(/,\s*/,$ENV{'HTTP_X_FORWARDED_FOR'});
	$log_dir = &catdir($log_dir,$H[0]);
}elsif(exists $ENV{'REMOTE_ADDR'}){
	$log_dir = &catdir($log_dir,$ENV{'REMOTE_ADDR'});
}
$log_dir = &catdir($log_dir,$COOKIE{'ag_annotation.session'}) if(exists $COOKIE{'ag_annotation.session'});
unless(-e $log_dir){
	my $old_umask = umask(0);
	&File::Path::mkpath($log_dir,0,0777);
	umask($old_umask);
}
open(LOG,">> $log_dir/$cgi_name.txt");
flock(LOG,2);
print $LOG "\n[$logtime]:$0\n";
foreach my $key (sort keys(%FORM)){
	print $LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
}
foreach my $key (sort keys(%COOKIE)){
	print $LOG "\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
}
foreach my $key (sort keys(%ENV)){
	print $LOG "\$ENV{$key}=[",$ENV{$key},"]\n";
}
=cut
my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0, qr/\..*$/);
my $LOG = &cgi_lib::common::getLogFH(\%FORM,\%COOKIE);

$SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit";
sub sigexit {
	if(defined $LOG){
		my $date = `date`;
		$date =~ s/\s*$//g;
		say $LOG qq|Error:[$date] KILL THIS SCRIPT!!|;
	}
	exit(1);
}

say __LINE__ unless(exists($ENV{'REQUEST_METHOD'}));

&setDefParams(\%FORM,\%COOKIE);

if(exists $FORM{'ci_id'} && defined $FORM{'ci_id'} && $FORM{'ci_id'} =~ /^[0-9]+$/){
	my $ci_name;
	my $sth = $dbh->prepare(qq|select ci_name from concept_info where ci_id=?|);
	$sth->execute($FORM{'ci_id'});
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$ci_name, undef);
	$sth->fetch;
	$FORM{'ci_name'} = $ci_name if(defined $ci_name);
	$sth->finish;
	undef $sth;

	if(exists $FORM{'cb_id'} && defined $FORM{'cb_id'} && $FORM{'cb_id'} =~ /^[0-9]+$/){
		my $cb_name;
		my $sth = $dbh->prepare(qq|select cb_name from concept_build where ci_id=? and cb_id=?|);
		$sth->execute($FORM{'ci_id'},$FORM{'cb_id'});
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$cb_name, undef);
		$sth->fetch;
		$FORM{'cb_name'} = $cb_name if(defined $cb_name);
		$sth->finish;
		undef $sth;
	}
}

my $IMAGES = {};
foreach my $key (sort keys(%FORM)){
#	print $LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
	$IMAGES->{$key} = $FORM{$key} if(defined $FORM{$key} && $FORM{$key} =~ /^\w/);
}

say __LINE__ unless(exists($ENV{'REQUEST_METHOD'}));

$IMAGES->{'images'} = [];
$IMAGES->{'success'} = JSON::XS::false;


&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
#foreach my $key (sort keys(%FORM)){
#	print $LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}

say __LINE__ unless(exists($ENV{'REQUEST_METHOD'}));

my $type_name = 'conventional';
if($FORM{'t_type'} eq '1'){
}elsif($FORM{'t_type'} eq '3'){
	$type_name = 'is_a';
}elsif($FORM{'t_type'} eq '4'){
	$type_name = 'part_of';
}
my $credit = &getDefImageCredit();
#my $credit = 1;

#print qq|Content-type: text/html; charset=UTF-8\n\n|;

say __LINE__ unless(exists($ENV{'REQUEST_METHOD'}));

unless(exists($FORM{'version'})){
	$IMAGES->{'success'} = JSON::XS::false if(exists($FORM{'callback'}));
#	use JSON;
#	my $json = to_json($IMAGES);
#	my $json = &JSON::XS::encode_json($IMAGES);
#	$json = $FORM{'callback'}."(".$json.")" if(exists($FORM{'callback'}));
#	print $json;

	my $json = &cgi_lib::common::printContentJSON($IMAGES,\%FORM);
	say $LOG __LINE__.":".$json if(defined $LOG);
	exit;
}

#my $bp3d_table = &getBP3DTablename($FORM{'version'});
#unless(&existsTable($bp3d_table)){
#	$IMAGES->{'success'} = JSON::XS::false if(exists($FORM{'callback'}));
#	my $json = &JSON::XS::encode_json($IMAGES);
#	$json = $FORM{'callback'}."(".$json.")" if(exists($FORM{'callback'}));
#	print $json;
#	say $LOG __LINE__.":".$json;
#	exit;
#}

say __LINE__ unless(exists($ENV{'REQUEST_METHOD'}));

=pod
if(!exists($FORM{'tg_id'}) || !exists($FORM{'tgi_id'})){
	my $tg_id;
	my $tgi_id;
	my $sth_model_version = $dbh->prepare(qq|select tg_id,tgi_id from model_version where tgi_version=?|);
	$sth_model_version->execute($FORM{'version'});
	my $column_number = 0;
	$sth_model_version->bind_col(++$column_number, \$tg_id, undef);
	$sth_model_version->bind_col(++$column_number, \$tgi_id, undef);
	$sth_model_version->fetch;
	if(defined $tg_id && defined $tgi_id){
		$FORM{'tg_id'} = $tg_id;
		$FORM{'tgi_id'} = $tgi_id;
	}
	$sth_model_version->finish;
	undef $sth_model_version;
}
=cut

#$FORM{'version'} = "Talairach" if($FORM{'t_type'} eq "101");


if(exists($FORM{'sorttype'})){
}else{
	my $sort_key = 'order';
	if(exists($FORM{'sort'}) && defined $FORM{'sort'}){
		$sort_key = $FORM{'sort'};
	}
	$FORM{'sorttype'} = $sort_key;
}

=pod
my $cache_path = qq|cache_fma|;
unless(-e $cache_path){
	mkdir $cache_path;
	chmod 0777,$cache_path;
}
if(exists($FORM{'version'})){
	$cache_path .= qq|/$FORM{'version'}|;
	unless(-e $cache_path){
		mkdir $cache_path;
		chmod 0777,$cache_path;
	}
}
$cache_path .= qq|/contents|;
unless(-e $cache_path){
	mkdir $cache_path;
	chmod 0777,$cache_path;
}
$cache_path .= qq|/$FORM{lng}|;
unless(-e $cache_path){
	mkdir $cache_path;
	chmod 0777,$cache_path;
}
=cut

my $old_umask = umask(0);

=pod
my $cache_path = &catdir($FindBin::Bin,qq|cache_fma|,$FORM{'version'},$cgi_name,$FORM{'lng'});
&File::Path::make_path($cache_path,{mode=>0777}) unless(-e $cache_path);
my @TEMP = map {"$_=$FORM{$_}"} sort keys(%FORM);
my $cache_file = &catfile($cache_path,&Digest::MD5::md5_hex(join("&",@TEMP)));
unlink $cache_file if(-e $cache_file);#DEBUG
if(-e $cache_file && -s $cache_file){
	open(IN,"< $cache_file") or die;
	flock(IN,1);
	my $json = <IN>;
	close(IN);
	if(defined $json && length($json)>0){
		if(exists($FORM{callback})){
			print $FORM{callback},"(",$json,")";
		}else{
			print $json;
		}
		say $LOG __LINE__.":".$json;
		close($LOG);
		exit;
	}
}
my $CACHE;
open($CACHE,"> $cache_file") or die;
flock($CACHE,2);
=cut

#my $cache_path = &catdir($FindBin::Bin,qq|cache_fma|,$FORM{'version'},$cgi_name,$FORM{'lng'},$FORM{'ci_id'},$FORM{'cb_id'});
my $cache_path = &getCachePath(\%FORM,$cgi_name);
unless(-e $cache_path){
#	my $old = umask(0);
	&File::Path::make_path($cache_path,{mode=>0777});
#	umask($old);
}

my %TREE = ();
my %TREE_PATH = ();
my %SEARCH_TREE_PATH = ();
my %TREE_PATH_UC = ();

sub getTreePath {
	my $f_id = shift;
	my $t_delcause;
	say $LOG __PACKAGE__.':'.__LINE__.qq|:getTreePath():[$f_id][|.(exists($TREE{$f_id})?1:0).']' if(defined $LOG);
	unless(exists($TREE_PATH{$f_id})){
		my $temp_fid = $f_id;
		my @p_path = ();
		while(exists($TREE{$temp_fid})){
			if(exists($TREE{$temp_fid}->{'t_delcause'}) && defined $TREE{$temp_fid}->{'t_delcause'}){
				$t_delcause = 1;
				last;
			}
#			eval{
#				print $LOG __LINE__,":\$f_pids=[",(ref $TREE{$temp_fid}->{'f_pids'}),"]\n";
				my $temp_fpid;
				if(ref $TREE{$temp_fid}->{'f_pids'} eq 'ARRAY'){
#					print $LOG __LINE__,":\$f_pids=[",(scalar @{$TREE{$temp_fid}->{'f_pids'}}),"]\n";
#					foreach $temp_fpid (@{$TREE{$temp_fid}->{'f_pids'}}){
					my $len = scalar @{$TREE{$temp_fid}->{'f_pids'}};
#					print $LOG __LINE__,":\$len=[$len]\n";
					for(my $i=0;$i<$len;$i++){
						$temp_fpid = $TREE{$temp_fid}->{'f_pids'}->[$i];
#						print $LOG __LINE__,":\$temp_fpid=[$temp_fpid]\n";
#						print $LOG __LINE__,":\$TREE{$temp_fpid}->{'t_delcause'}=[$TREE{$temp_fpid}->{'t_delcause'}]\n";
						if(exists($TREE{$temp_fpid}->{'t_delcause'}) && defined $TREE{$temp_fpid}->{'t_delcause'}){
#							print $LOG __LINE__,":next\n";
							next;
						}else{
#							print $LOG __LINE__,":last\n";
							last;
						}
					}
				}
#				print $LOG __LINE__,":\$temp_fpid=[$temp_fpid]\n";
				if(defined $temp_fpid){
					if(exists($TREE{$temp_fpid}->{'t_delcause'}) && defined $TREE{$temp_fpid}->{'t_delcause'}){
						$t_delcause = 1;
						last;
					}else{
						$temp_fid = $temp_fpid;
						unshift @p_path,$temp_fid;
					}
				}else{
					last;
				}
#			};
#			if($@){
#				print $LOG __LINE__,":",$@,"\n";
#				last;
#			}
		}
#		pop @p_path if(scalar @p_path > 0);
		$TREE_PATH{$f_id} = join("/",@p_path);
	}
	if(defined $t_delcause){
		return undef;
	}else{
		return $TREE_PATH{$f_id};
	}
}


sub getTreePathUC {
	my $f_id = shift;
	my $t_delcause;
#	say $LOG __PACKAGE__.':'.__LINE__.qq|:getTreePathUC():[$f_id][|.(exists($TREE_PATH_UC{$f_id})?1:0).']' if(defined $LOG);
	my %TREE_PATH_EXISTS;
	unless(exists($TREE_PATH_UC{$f_id})){
		my $temp_fid = $f_id;
		my @p_path = ();
#		say $LOG __PACKAGE__.':'.__LINE__.qq|:getTreePathUC():[$temp_fid][|.(exists($TREE{$temp_fid})?1:0).']' if(defined $LOG);
		while(exists($TREE{$temp_fid})){
			say $LOG __PACKAGE__.':'.__LINE__.qq|:getTreePathUC():[$temp_fid]| if(defined $LOG);
			last if(exists $TREE_PATH_EXISTS{$temp_fid});
			$TREE_PATH_EXISTS{$temp_fid} = undef;
			if(exists($TREE{$temp_fid}->{'t_delcause'}) && defined $TREE{$temp_fid}->{'t_delcause'}){
				$t_delcause = 1;
				last;
			}
#			eval{
				my $temp_fpid;
				if(ref $TREE{$temp_fid}->{'f_pids'} eq 'ARRAY'){
					my $len = scalar @{$TREE{$temp_fid}->{'f_pids'}};
					my $i;
					for($i=0;$i<$len;$i++){
						$temp_fpid = $TREE{$temp_fid}->{'f_pids'}->[$i];
						if(exists($TREE{$temp_fpid}->{'t_delcause'}) && defined $TREE{$temp_fpid}->{'t_delcause'}){
#							say $LOG __PACKAGE__.':'.__LINE__.':next' if(defined $LOG);
							next;
						}else{
#							say $LOG __PACKAGE__.':'.__LINE__.':last' if(defined $LOG);
							last;
						}
					}
					undef $temp_fpid if($i>=$len);
				}
#				say $LOG __PACKAGE__.':'.__LINE__.':$temp_fpid='.(defined $temp_fpid ? $temp_fpid : 'undef') if(defined $LOG);
				if(defined $temp_fpid){
					if(exists($TREE{$temp_fpid}->{'t_delcause'}) && defined $TREE{$temp_fpid}->{'t_delcause'}){
						$t_delcause = 1;
						last;
					}else{
						$temp_fid = $temp_fpid;
						unshift @p_path,$temp_fid;
					}
				}else{
					last;
				}
#			};
#			if($@){
#				if(defined $LOG){
#					say $LOG __PACKAGE__.':'.__LINE__.':'.$@;
#				}else{
#					say SDTERR __PACKAGE__.':'.__LINE__.':'.$@;
#				}
#				last;
#			}
		}
#		pop @p_path if(scalar @p_path > 0);
		$TREE_PATH_UC{$f_id}->{'u_path'} = (scalar @p_path > 0) ? join("/",@p_path) : undef;
		$TREE_PATH_UC{$f_id}->{'c_path'} = (defined $TREE{$f_id} && defined $TREE{$f_id}->{'f_cids'}) ? scalar @{$TREE{$f_id}->{'f_cids'}} : undef;
	}
#	say $LOG __PACKAGE__.':'.__LINE__.qq|:getTreePathUC():[$f_id][|.(defined $t_delcause ? 'undef' : $TREE_PATH_UC{$f_id}).']' if(defined $LOG);
	if(defined $t_delcause){
		return undef;
	}else{
		return $TREE_PATH_UC{$f_id};
	}
}

my $store_file = &catfile($cache_path,qq|tree_$FORM{'t_type'}\_storable.store|);
my $store_lock = &catfile($cache_path,qq|tree_$FORM{'t_type'}\_storable.lock|);

my $store_search_tree_file = &catfile($cache_path,qq|search_tree_storable.store|);

my $store_contents_tree_file;
if(exists $FORM{'disptype'} && defined $FORM{'disptype'} && $FORM{'disptype'} eq 'tree'){
	$store_contents_tree_file = &catdir($cache_path,qq|contents_tree_$FORM{'t_type'}|);
	my $pid;
	if(defined $FORM{'tree_pid'}){
		$pid = $FORM{'tree_pid'};
	}elsif(defined $FORM{'node'}){
		$pid = $FORM{'node'};
	}elsif(defined $FORM{'f_ids'}){
		my $f_ids = &cgi_lib::common::decodeJSON($FORM{'f_ids'});
		if(defined $f_ids && ref $f_ids eq 'ARRAY'){
			$pid = shift @$f_ids;
			if(defined $pid){
				delete $FORM{'f_ids'};
				$FORM{'node'} = $pid;
				$store_contents_tree_file = &catdir($store_contents_tree_file,'f_ids');
			}
		}
	}else{
		undef $store_contents_tree_file;
	}
	if(defined $store_contents_tree_file && defined $pid){
		if($pid =~ /^([^0-9]+)/){
			$store_contents_tree_file = &catdir($store_contents_tree_file,$1);
			$pid =~ s/^[^0-9]+//;
		}
		for(my $i=0;$i<length($pid);$i+=2){
			my $key = substr($pid,$i,2);
			$store_contents_tree_file = &catdir($store_contents_tree_file,$key);
		}
		unless(-e $store_contents_tree_file){
#			umask(0);
			&File::Path::mkpath($store_contents_tree_file,0,0777);
		}

		if(defined $FORM{'tree_pid'}){
			$store_contents_tree_file = &catdir($store_contents_tree_file,(defined $FORM{'position'} ? $FORM{'position'}.'_' : "").(defined $FORM{'f_depth'} ? $FORM{'f_depth'}.'_' : "").qq|tree_pid.store|);
		}else{
			$store_contents_tree_file = &catdir($store_contents_tree_file,(defined $FORM{'position'} ? $FORM{'position'}.'_' : "").qq|node.store|);
		}
	}
}

$SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit2";
sub sigexit2 {
	my($date) = `date`;
	$date =~ s/\s*$//g;
	print STDERR "[$date] KILL THIS CGI!![$ENV{SCRIPT_NAME}]\n";
	rmdir $store_lock if(-e $store_lock);
	exit(1);
}


if(!-e $store_file && !mkdir($store_lock)){
	exit if(!exists($ENV{'REQUEST_METHOD'}));
	my $wait = 30;
	while($wait){
		if(-e $store_lock){
			$wait--;
			sleep(1);
			next;
		}
		last;
	}
}
if(defined $store_contents_tree_file && -e $store_contents_tree_file && -s $store_contents_tree_file){
	my $IMAGES = retrieve($store_contents_tree_file);
#	my $json = &JSON::XS::encode_json($IMAGES);
##	say $LOG __LINE__.":".$json;
#	$json = $FORM{'callback'}."(".$json.")" if(exists($FORM{'callback'}));
#	print $json;

	my $json = &cgi_lib::common::printContentJSON($IMAGES,\%FORM);
	say $LOG __LINE__.":".$json if(defined $LOG);
	rmdir($store_lock) if(-e $store_lock);
#	close($LOG);
	exit;
}

say $LOG __PACKAGE__.':'.__LINE__.':' if(defined $LOG);

if(-e $store_search_tree_file && -s $store_search_tree_file){
	my $href = retrieve($store_search_tree_file);
	%SEARCH_TREE_PATH = %$href;
}
if(-e $store_file && -s $store_file){
	my $href = retrieve($store_file);
	%TREE = %$href;
}elsif(exists $FORM{'t_type'} && defined $FORM{'t_type'}){

	unless(exists $FORM{'ci_id'} && defined $FORM{'ci_id'} && exists $FORM{'cb_id'} && defined $FORM{'cb_id'}){
		&cgi_lib::common::printContentJSON($IMAGES,\%FORM);
		exit;
	}

	my $f_id;
	my $f_pid;
	my $t_delcause;

	my $sql = qq|select cdi_name,cdi_pname,but_delcause from view_buildup_tree where md_id=$FORM{'md_id'} and mv_id=$FORM{'mv_id'} and mr_id=$FORM{'mr_id'} and ci_id=$FORM{'ci_id'} and cb_id=$FORM{'cb_id'} and bul_id=$FORM{'t_type'} order by but_cnum desc|;

#	print $LOG __LINE__,":[$sql]\n";


	my $sth = $dbh->prepare($sql);
	$sth->execute();
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$f_id, undef);
	$sth->bind_col(++$column_number, \$f_pid, undef);
	$sth->bind_col(++$column_number, \$t_delcause, undef);
	while($sth->fetch){
		next unless(defined $f_id);
		$TREE{$f_id} = {t_delcause => $t_delcause} unless(exists($TREE{$f_id}));
		next unless(defined $f_pid);
		push(@{$TREE{$f_id}->{'f_pids'}},$f_pid);
		$TREE{$f_pid} = {t_delcause => $t_delcause} unless(exists($TREE{$f_pid}));
		push(@{$TREE{$f_pid}->{f_cids}},$f_id);
#		print $LOG __LINE__,":\n";
	}
	$sth->finish;
	undef $sth;
	store \%TREE, $store_file;

}

say $LOG __PACKAGE__.':'.__LINE__.':' if(defined $LOG);

if(exists $FORM{'disptype'} && defined $FORM{'disptype'} && $FORM{'disptype'} eq 'tree' && !defined $FORM{'tree_pid'} && defined $FORM{'node'} && $FORM{'node'} ne 'search' && !defined $FORM{'txpath'}){
	my $txpath = &getTreePath($FORM{'node'});
	$FORM{'txpath'} = qq|/$txpath/$FORM{'node'}| if(defined $txpath && $txpath ne "");
}

say $LOG __PACKAGE__.':'.__LINE__.':' if(defined $LOG);

my $sth_tree_p = $dbh->prepare(qq|select cdi_pname,but_delcause from view_buildup_tree where md_id=$FORM{'md_id'} and mv_id=$FORM{'mv_id'} and mr_id=$FORM{'mr_id'} and ci_id=$FORM{'ci_id'} and cb_id=$FORM{'cb_id'} and bul_id=? and cdi_name=?|);
my @TREE_ROUTE = ();

say $LOG __PACKAGE__.':'.__LINE__.':' if(defined $LOG);

my $sth_point_children;
unless(defined $sth_point_children){
	my $sql = qq|select |;
	$sql .= qq| p.p_label,count(*)|;
	$sql .= qq| from bp3d_point as p|;
	$sql .= qq| where p.f_pid=? and p.tg_id=? and p.tgi_id=? and p.p_delcause is null|;
	$sql .= qq| group by p.p_label|;
	$sql .= qq| order by p.p_label|;
	$sth_point_children = $dbh->prepare($sql);
}

say $LOG __PACKAGE__.':'.__LINE__.':' if(defined $LOG);

sub getPointInfo {
	my $fma = shift;
	if(exists($fma->{point_parent}) && defined($fma->{point_parent})){
		foreach my $p_fma (@{$fma->{point_parent}}){
			next if(!exists($p_fma->{'f_id'}) || !defined($p_fma->{'f_id'}));
			my $path = &getTreePath($p_fma->{'f_id'});
			next unless(defined $path);
			if($FORM{'t_type'} eq '1'){
				$p_fma->{'f_id'} = qq|<a href="#" onclick="click_conventional('$p_fma->{'f_id'}','$path');return false;">$p_fma->{'f_id'}</a>|;
			}elsif($FORM{'t_type'} eq '3'){
				$p_fma->{'f_id'} = qq|<a href="#" onclick="click_isa('$p_fma->{'f_id'}','$path');return false;">$p_fma->{'f_id'}</a>|;
			}elsif($FORM{'t_type'} eq '4'){
				$p_fma->{'f_id'} = qq|<a href="#" onclick="click_partof('$p_fma->{'f_id'}','$path');return false;">$p_fma->{'f_id'}</a>|;
			}
		}
	}else{
		my $f_id2 = $fma->{'f_id'};
#		$f_id2 =~ s/\D+$//g;
		$sth_point_children->execute($f_id2,$FORM{'tg_id'},$FORM{'tgi_id'});
		my $column_number = 0;
		my $c_p_label;
		my $c_p_count;
		$sth_point_children->bind_col(++$column_number, \$c_p_label, undef);
		$sth_point_children->bind_col(++$column_number, \$c_p_count, undef);
		while($sth_point_children->fetch){
			push(@{$fma->{point_children}},{
				point_label => $c_p_label,
				point_count => qq|<a href="#" onclick="click_point_children('$f_id2','$c_p_label');return false;">$c_p_count</a>|
			});
		}
		$sth_point_children->finish;
	}
}

say $LOG __PACKAGE__.':'.__LINE__.':' if(defined $LOG);

if(exists $FORM{'fma_ids'} && defined $FORM{'fma_ids'} && length $FORM{'fma_ids'}){
	my $path_str = &getGlobalPath();
	if(defined $path_str){
		$path_str .= qq|icon.cgi|;
	}else{
		my $host = (split(/,\s*/,(exists($ENV{'HTTP_X_FORWARDED_HOST'})?$ENV{'HTTP_X_FORWARDED_HOST'}:$ENV{'HTTP_HOST'})))[0];
		my @TEMP = split("/",$ENV{'REQUEST_URI'});
		$TEMP[$#TEMP] = qq|icon.cgi|;
		$path_str = join("/",@TEMP);
		$path_str = qq|http://$host$path_str|;
	}
&cgi_lib::common::message($path_str, $LOG) if(defined $LOG);
	my $f_ids = &cgi_lib::common::decodeJSON($FORM{'fma_ids'});
	if(defined $f_ids && ref $f_ids eq 'ARRAY'){
		if(exists $FORM{'degenerate_same_shape_icons'} && defined $FORM{'degenerate_same_shape_icons'} && $FORM{'degenerate_same_shape_icons'} eq 'true'){
			&getDegenerateSameShapeIcons($dbh,\%FORM,$f_ids);
		}
	say $LOG __PACKAGE__.':'.__LINE__.':' if(defined $LOG);
		for(my $cnt=0;$cnt<scalar @$f_ids;$cnt++){
			my $fma = &getFMA($dbh,\%FORM,$f_ids->[$cnt],$LOG);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON($fma,1), $LOG) if(defined $LOG);
			$fma->{'src'} = "icon/inprep.png" if($fma->{'src'} eq "resources/images/default/s.gif");
			if(exists $fma->{'b_id'} && defined $fma->{'b_id'}){
				$fma->{'srcstr'} = qq|$path_str?i=| . &url_encode($fma->{'b_id'}) . qq|&p=$FORM{'position'}|;
			}else{
				my $p = &url_encode(exists $FORM{'position'} && defined $FORM{'position'} ? $FORM{'position'} : 'front');
				my $v = &url_encode(exists $FORM{'version_name'} && defined $FORM{'version_name'} ? $FORM{'version_name'} : (exists $FORM{'version'} && defined $FORM{'version'} ? $FORM{'version'} : ''));
				my $m = &url_encode(exists $FORM{'tg_model'} && defined $FORM{'tg_model'} ? $FORM{'tg_model'} : (exists $FORM{'tg_id'} && defined $FORM{'tg_id'} ? $FORM{'tg_id'} : ''));
				$fma->{'srcstr'} = qq|$path_str?i=| . &url_encode($f_ids->[$cnt]) . qq|&p=$p&v=$v&t=$type_name&m=$m|;
			}
			&getPointInfo($fma);

			if(exists $FORM{'disptype'} && defined $FORM{'disptype'} && $FORM{'disptype'} eq 'tree' && !defined $fma->{'u_path'}){
				my $txpath = &getTreePath($fma->{'f_id'});
				if(defined $txpath && $txpath ne ""){
					$fma->{'u_path'} = $txpath;
				}else{
					$fma->{'u_path'} = 'ctg_';
				}
			}
			if(defined $fma->{'density_ends'} && ref $fma->{'density_ends'} eq 'ARRAY'){
#	say $LOG __PACKAGE__.':'.__LINE__.':' if(defined $LOG);
#	say $LOG __PACKAGE__.':'.__LINE__.':'.$JSONXS->encode($fma->{'density_ends'}) if(defined $LOG);
				foreach my $ends (@{$fma->{'density_ends'}}){
					my $hash = &getTreePathUC($ends->{'f_id'});
					if(defined $hash){
#	say $LOG __PACKAGE__.':'.__LINE__.':'.$JSONXS->encode($hash) if(defined $LOG);
						$ends->{$_} = $hash->{$_} for(keys(%$hash));
					}
				}
			}
	say $LOG __PACKAGE__.':'.__LINE__.':' if(defined $LOG);
			push(@{$IMAGES->{'images'}},$fma);
		}
	&cgi_lib::common::dumper($IMAGES->{'images'},$LOG) if(defined $LOG);
		@{$IMAGES->{'images'}} =
			sort { defined $b->{'density'}        ? $b->{'density'}        : 0 <=> defined $a->{'density'}        ? $a->{'density'}        : 0 }
			sort { defined $b->{'primitive'}      ? $b->{'primitive'}      : 0 <=> defined $a->{'primitive'}      ? $a->{'primitive'}      : 0 }
			sort { defined $b->{'used_parts_num'} ? $b->{'used_parts_num'} : 0 <=> defined $a->{'used_parts_num'} ? $a->{'used_parts_num'} : 0 }
			sort { $a->{'name_e'} cmp $b->{'name_e'} }
			@{$IMAGES->{'images'}};

		if(defined $FORM{'sorttype'}){
			my $st = $FORM{'sorttype'};
			if($st =~ /^(zmax|volume|lastmod|tweet_num|density)$/){
				@{$IMAGES->{'images'}} = sort {
					if(defined $b->{$st} && defined $a->{$st}){
						$b->{$st} <=> $a->{$st}
					}elsif(defined $b->{$st}){
						1;
					}elsif(defined $a->{$st}){
						-1;
					}else{
						0;
					}
				} @{$IMAGES->{'images'}};
			}
			elsif($st =~ /^(taid)$/){
				@{$IMAGES->{'images'}} = sort {
					if(defined $b->{$st} && defined $a->{$st}){
						$a->{$st} cmp $b->{$st}
					}elsif(defined $b->{$st}){
						1;
					}elsif(defined $a->{$st}){
						-1;
					}else{
						0;
					}
				} @{$IMAGES->{'images'}};
			}
			elsif($st =~ /^(zmin)$/){
	#			@{$IMAGES->{'images'}} = sort {$a->{$st} <=> $b->{$st} } @{$IMAGES->{'images'}};
				@{$IMAGES->{'images'}} = sort {
					if(defined $b->{$st} && defined $a->{$st}){
						$b->{$st} <=> $a->{$st}
					}elsif(defined $b->{$st}){
						1;
					}elsif(defined $a->{$st}){
						-1;
					}else{
						0;
					}
				} @{$IMAGES->{'images'}};
			}
			else{
				$st = qq|b_$st| if($FORM{'t_type'} eq '1' && $st eq 'id');
				@{$IMAGES->{'images'}} = sort {
					if(defined $a->{'density'} && defined $b->{'density'}){
						0;
					}elsif(defined $a->{'density'}){
						-1;
					}elsif(defined $b->{'density'}){
						1;
					}
				} sort {
					if(defined $a->{$st} && defined $b->{$st}){
						$a->{$st} cmp $b->{$st};
					}elsif(defined $a->{$st}){
						-1;
					}elsif(defined $b->{$st}){
						1;
					}else{
						0;
					}
				} @{$IMAGES->{'images'}};
			}
		}else{
		}
	}
say $LOG __PACKAGE__.':'.__LINE__.':' if(defined $LOG);
	$IMAGES->{'success'} = JSON::XS::true if(exists($FORM{'callback'}));
	my $json = &cgi_lib::common::printContentJSON($IMAGES,\%FORM);
	say $LOG __LINE__.":".$json if(defined $LOG);
	rmdir($store_lock) if(-e $store_lock);
	umask($old_umask);
	exit;
}

say $LOG __PACKAGE__.':'.__LINE__.':' if(defined $LOG);

if(exists($FORM{'objs'})){
#print $LOG __LINE__,":\$FORM{'version'}=[$FORM{'version'}]\n";
#	my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
#	print $LOG __LINE__.':'.sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec)."\n";

	my $model = defined $FORM{'model'} ? $FORM{'model'} : (defined $FORM{'md_abbr'} ? $FORM{'md_abbr'} : 'bp3d');
	my $version = $FORM{'version'};
	my %version2id = ();
	my $path_str = &getGlobalPath();
	if(defined $path_str){
		$path_str .= qq|icon.cgi|;
	}else{
		my $host = (split(/,\s*/,(exists($ENV{'HTTP_X_FORWARDED_HOST'})?$ENV{'HTTP_X_FORWARDED_HOST'}:$ENV{'HTTP_HOST'})))[0];
		my @TEMP = split("/",$ENV{'REQUEST_URI'});
		$TEMP[$#TEMP] = qq|icon.cgi|;
		$path_str = join("/",@TEMP);
		$path_str = qq|http://$host$path_str|;
	}
	my $tg_id;
	my $tgi_id;
#	my $sth_model_version = $dbh->prepare(qq|select tg_id,tgi_id from model_version where tgi_version=?|);
	my $sql_model_version=<<SQL;
select
 mr.md_id,
 mr.mv_id,
 mr.mr_id
from
 model_revision mr
left join (select md_id,md_abbr from model) md on md.md_id=mr.md_id
where
 md.md_abbr=? and
 mr.mr_version=?
order by
 mr_order
SQL
	my $sth_model_version = $dbh->prepare($sql_model_version);

	my $objs = &JSON::XS::decode_json($FORM{'objs'});

#	my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
#	print $LOG __LINE__.':'.sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec)."\n";
#	use Time::HiRes;
	use Clone;
	my $sth_bul_all;
	if(exists $FORM{'bul_all'} && defined $FORM{'bul_all'} && $FORM{'bul_all'} eq 'true'){
		my $sql = qq|select bul_id from buildup_logic where bul_use AND bul_id<>? order by bul_order|;
		$sth_bul_all = $dbh->prepare($sql);
	}

	for(my $cnt=0;$cnt<scalar @$objs;$cnt++){

#		my $st = [&Time::HiRes::gettimeofday()];
#		my $et;

		if(exists($objs->[$cnt]->{'model'}) && defined $objs->[$cnt]->{'model'}){
			$FORM{'model'} = $objs->[$cnt]->{'model'};
		}else{
			$FORM{'model'} = $model;
		}
		if(exists($objs->[$cnt]->{'version'}) && defined $objs->[$cnt]->{'version'}){
			$FORM{'version'} = $objs->[$cnt]->{'version'};
#print $LOG __LINE__,":",Dumper($objs->[$cnt]),"\n";
			delete $FORM{'mv_id'};
			delete $FORM{'mr_id'};
			&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
		}else{
			$FORM{'version'} = $version;
		}

#print $LOG __LINE__,":\$version=[$version]\n";
#print $LOG __LINE__,":\$FORM{'version'}=[$FORM{'version'}]\n";
#print $LOG __LINE__,":\$FORM{'model'}=[$FORM{'model'}]\n";

		unless(exists($version2id{$FORM{'version'}})){
			eval{
				my $mr_id;
				$sth_model_version->execute($FORM{'model'},$FORM{'version'});
				my $column_number = 0;
				$sth_model_version->bind_col(++$column_number, \$tg_id, undef);
				$sth_model_version->bind_col(++$column_number, \$tgi_id, undef);
				$sth_model_version->bind_col(++$column_number, \$mr_id, undef);
				$sth_model_version->fetch;
				if(defined $tg_id && defined $tgi_id){
					$version2id{$FORM{'version'}} = {
						tg_id  => $tg_id,
						tgi_id => $tgi_id,
						md_id  => $tg_id,
						mv_id  => $tgi_id,
						mr_id  => $mr_id
					};
				}
				$sth_model_version->finish;
			};
			if($@){
#				print $LOG __LINE__,":",$@,"\n";
			}
		}
		$FORM{'md_id'} = $version2id{$FORM{'version'}}->{'md_id'};
		$FORM{'mv_id'} = $version2id{$FORM{'version'}}->{'mv_id'};
		$FORM{'mr_id'} = $version2id{$FORM{'version'}}->{'mr_id'};

#print $LOG __LINE__,":\$FORM{'md_id'}=[$FORM{'md_id'}]\n";
#print $LOG __LINE__,":\$FORM{'mv_id'}=[$FORM{'mv_id'}]\n";
#print $LOG __LINE__,":\$FORM{'mr_id'}=[$FORM{'mr_id'}]\n";
#		$et = &Time::HiRes::tv_interval( $st, [&Time::HiRes::gettimeofday()]);
#		print $LOG __LINE__.':'.$et."\n";

=pod
CREATE INDEX idx_concept_data_info_cdi_name_e_lower ON concept_data_info ((lower(cdi_name_e)));
CREATE INDEX idx_concept_data_info_cdi_name_l_lower ON concept_data_info ((lower(cdi_name_l)));
CREATE INDEX idx_concept_data_info_cdi_name_j ON concept_data_info (cdi_name_j);
CREATE INDEX idx_concept_data_info_cdi_name_k ON concept_data_info (cdi_name_k);
=cut

		if(!exists($objs->[$cnt]->{'f_id'}) && (exists($objs->[$cnt]->{'name_e'}) || exists($objs->[$cnt]->{'name_j'}) || exists($objs->[$cnt]->{'name_l'}) || exists($objs->[$cnt]->{'name_k'}))){
#			$bp3d_table = &getBP3DTablename($FORM{'version'});
			my $f_id;
			my @where = ();
			my @param = ();
			if(exists($objs->[$cnt]->{'name_e'})){
#				$objs->[$cnt]->{'name_e'} = Encode::encode_utf8($objs->[$cnt]->{'name_e'}) if(utf8::is_utf8($objs->[$cnt]->{'name_e'}));
#				push(@where,qq|cdi_name_e ilike ?|);
				if($objs->[$cnt]->{'name_e'} =~ /^FMA[0-9]+$/){
					push(@where,qq|cdi_name = ?|);
				}else{
					push(@where,qq|lower(cdi_name_e) = lower(?)|);
				}
				push(@param,$objs->[$cnt]->{'name_e'});
			}
			if(exists($objs->[$cnt]->{'name_j'})){
#				$objs->[$cnt]->{'name_j'} = Encode::encode_utf8(Encode::decode_utf8($objs->[$cnt]->{'name_j'})) if(utf8::is_utf8($objs->[$cnt]->{'name_j'}));
				push(@where,qq|cdi_name_j = ?|);
				push(@param,$objs->[$cnt]->{'name_j'});
			}
			if(exists($objs->[$cnt]->{'name_l'})){
#				$objs->[$cnt]->{'name_l'} = Encode::encode_utf8($objs->[$cnt]->{'name_l'}) if(utf8::is_utf8($objs->[$cnt]->{'name_l'}));
#				push(@where,qq|cdi_name_l ilike ?|);
				push(@where,qq|lower(cdi_name_l) = lower(?)|);
				push(@param,$objs->[$cnt]->{'name_l'});
			}
			if(exists($objs->[$cnt]->{'name_k'})){
#				$objs->[$cnt]->{'name_k'} = Encode::encode_utf8($objs->[$cnt]->{'name_k'}) if(utf8::is_utf8($objs->[$cnt]->{'name_k'}));
				push(@where,qq|cdi_name_k = ?|);
				push(@param,$objs->[$cnt]->{'name_k'});
			}
			my $sql = qq|select cdi_name from concept_data_info where ci_id=$FORM{'ci_id'} and |.join(" and ",@where);
			my $sth = $dbh->prepare($sql);
			$sth->execute(@param);
			$sth->bind_col(1, \$f_id, undef);
			$sth->fetch;
			$sth->finish;
			undef $sth;

#			$et = &Time::HiRes::tv_interval( $st, [&Time::HiRes::gettimeofday()]);
#			print $LOG __LINE__.':'.$et."\n";

			if(!defined $f_id && exists($objs->[$cnt]->{'name_e'})){
				@where = ();
				@param = ();
				if(exists($objs->[$cnt]->{'name_e'})){
					push(@where,qq|cdi_name_e~*?|);
					push(@param,$objs->[$cnt]->{'name_e'});
				}
				$sql = qq|select cdi_name from concept_data_info where ci_id=$FORM{'ci_id'} and |.join(" and ",@where);
				$sth = $dbh->prepare($sql);
				$sth->execute(@param);
				$sth->bind_col(1, \$f_id, undef);
				$sth->fetch;
				$sth->finish;
				undef $sth;
			}
#print $LOG __LINE__,":\$f_id=[$f_id],\$objs->[$cnt]->{'name_j'}=[$objs->[$cnt]->{'name_j'}][",(utf8::is_utf8($objs->[$cnt]->{'name_j'})?1:0),"]\n";
			if(!defined $f_id && exists($objs->[$cnt]->{'name_j'})){
				@where = ();
				@param = ();
				if(exists($objs->[$cnt]->{'name_j'})){
					push(@where,qq|cdi_name_j=?|);
					push(@param,$objs->[$cnt]->{'name_j'});
				}
				$sql = qq|select cdi_name from concept_data_info where ci_id=$FORM{'ci_id'} and |.join(" and ",@where);
				$sth = $dbh->prepare($sql);
				$sth->execute(@param);
				$sth->bind_col(1, \$f_id, undef);
				$sth->fetch;
#print $LOG __LINE__,":\$f_id=[$f_id]\n";
				$sth->finish;
				undef $sth;

#				$et = &Time::HiRes::tv_interval( $st, [&Time::HiRes::gettimeofday()]);
#				print $LOG __LINE__.':'.$et."\n";
			}
			$objs->[$cnt]->{'f_id'} = $f_id;
		}
		next unless(exists $objs->[$cnt]->{'f_id'} && defined $objs->[$cnt]->{'f_id'} && length $objs->[$cnt]->{'f_id'});

#		$et = &Time::HiRes::tv_interval( $st, [&Time::HiRes::gettimeofday()]);
#		print $LOG __LINE__.':'.$et."\n";

		my $fma;
		eval{
			$fma = &getFMA($dbh,\%FORM,$objs->[$cnt]->{'f_id'},$LOG);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON($fma,1), $LOG) if(defined $LOG);

			unless(exists $fma->{'b_id'} && defined $fma->{'b_id'}){
				if(defined $sth_bul_all){
					my $form = &Clone::clone(\%FORM);
					my $bul_id;
					$sth_bul_all->execute($FORM{'bul_id'});
					$sth_bul_all->bind_col(1, \$bul_id, undef);
					while($sth_bul_all->fetch){
						$form->{'bul_id'} = $form->{'t_type'} = $bul_id;
						$fma = &getFMA($dbh,$form,$objs->[$cnt]->{'f_id'},$LOG);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON($fma,1), $LOG) if(defined $LOG);
						last if(exists $fma->{'b_id'} && defined $fma->{'b_id'});
					}
					$sth_bul_all->finish;
				}
			}


			$fma->{'src'} = "icon/inprep.png" if($fma->{'src'} eq "resources/images/default/s.gif");
			if(exists $fma->{'b_id'} && defined $fma->{'b_id'}){
#				$fma->{'srcstr'} = qq|$path_str?i=| . &url_encode($fma->{'b_id'}) . qq|&p=$FORM{'position'}&c=1|;
				$fma->{'srcstr'} = qq|$path_str?i=| . &url_encode($fma->{'b_id'}) . qq|&p=|.($FORM{'position'} // 'front');
			}else{

				my $position = 'front';
				$position = $FORM{'position'} if(exists $FORM{'position'} && exists $FORM{'position'} && length $FORM{'position'});
				my $version =  exists $FORM{'version_name'} && defined $FORM{'version_name'} && length $FORM{'version_name'} ? $FORM{'version_name'} : $FORM{'version'};
				my $model =  exists $FORM{'tg_model'} && defined $FORM{'tg_model'} && length $FORM{'tg_model'} ? $FORM{'tg_model'} : $FORM{'tg_id'};
				$model = exists $FORM{'model'} && defined $FORM{'model'} && length $FORM{'model'} ? $FORM{'model'} : $FORM{'ci_id'} unless(defined $model);

				$fma->{'srcstr'} = qq|$path_str?i=| . &url_encode($objs->[$cnt]->{'f_id'}) . qq|&p=|.&url_encode($position).qq|&v=|.&url_encode($version).qq|&t=$type_name&m=|.&url_encode($model);
				say $LOG __LINE__.':$fma->{srcstr}=['.$fma->{'srcstr'}.']';
			}
			$fma->{'id'} = $objs->[$cnt]->{'id'} if($objs->[$cnt]->{'id'});
			&getPointInfo($fma);
		};
		if($@){
#			print $LOG __LINE__,":",$@,"\n";
		}
		push(@{$IMAGES->{'images'}},$fma);

#		my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
#		print $LOG __LINE__.':'.sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec)."\n";
#		$et = &Time::HiRes::tv_interval( $st, [&Time::HiRes::gettimeofday()]);
#		print $LOG __LINE__.':'.$et."\n";
	}

	undef $sth_model_version;
	undef $sth_bul_all;

	$IMAGES->{'success'} = JSON::XS::true if(exists($FORM{'callback'}));
#	use JSON;
#	my $json = to_json($IMAGES);
#	my $json = &JSON::XS::encode_json($IMAGES);
##	print $CACHE $json;
#	$json = $FORM{'callback'}."(".$json.")" if(exists($FORM{'callback'}));
#	print $json;

	my $json = &cgi_lib::common::printContentJSON($IMAGES,\%FORM);
	say $LOG __LINE__.":".$json if(defined $LOG);
	rmdir($store_lock) if(-e $store_lock);

	umask($old_umask);
#	close($CACHE);
#	close($LOG);

#	my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
#	print $LOG __LINE__.':'.sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec)."\n";
	exit;
}

say $LOG __PACKAGE__.':'.__LINE__.':' if(defined $LOG);

my $sql =<<SQL;
select 
 but.cdi_id,
 but.cdi_pid,
 but.bul_id,
 cdi.cdi_name,
 COALESCE(but2.num,0)
from
 buildup_tree as but
left join (
 select
  md_id,
  mv_id,
  mr_id,
  ci_id,
  cb_id,
  bul_id,
  cdi_pid,
  count(cdi_pid) as num
 from
  buildup_tree
 group by
  md_id,
  mv_id,
  mr_id,
  ci_id,
  cb_id,
  bul_id,
  cdi_pid
) as but2 on (
 but.md_id = but2.md_id and
 but.mv_id = but2.mv_id and
 but.mr_id = but2.mr_id and
 but.ci_id = but2.ci_id and
 but.cb_id = but2.cb_id and
 but.cdi_id = but2.cdi_pid and
 but.bul_id = but2.bul_id
)
left join (select ci_id,cdi_id,cdi_name,cdi_delcause from concept_data_info) as cdi on (but.ci_id = cdi.ci_id and but.cdi_id = cdi.cdi_id)
left join (select ci_id,cdi_id,cdi_name,cdi_delcause from concept_data_info) as cdi2 on (but.ci_id = cdi2.ci_id and but.cdi_pid = cdi2.cdi_id)
where
 but.md_id=$FORM{'md_id'} and
 but.mv_id=$FORM{'mv_id'} and
 but.mr_id=$FORM{'mr_id'} and
 but.ci_id=$FORM{'ci_id'} and
 but.cb_id=$FORM{'cb_id'} and
 but.but_delcause is null and
 cdi.cdi_delcause is null and
 cdi2.cdi_delcause is null and 
SQL

my @bind_values = ();
my @LIST1 = ();
unless(exists($FORM{'node'}) || exists($FORM{'f_ids'}) || exists($FORM{'f_depth'}) || exists($FORM{'tree_pid'})){
	$IMAGES->{'success'} = JSON::XS::false if(exists($FORM{'callback'}));
#	use JSON;
#	my $json = to_json($IMAGES);
#	my $json = &JSON::XS::encode_json($IMAGES);
#	$json = $FORM{'callback'}."(".$json.")" if(exists($FORM{'callback'}));
#	print $json;
	my $json = &cgi_lib::common::printContentJSON($IMAGES,\%FORM);
	say $LOG __LINE__.":".$json if(defined $LOG);
	rmdir($store_lock) if(-e $store_lock);
	exit;
}elsif(exists $FORM{'node'} && defined $FORM{'node'} && $FORM{'node'} eq "root"){
	$sql .= qq|but.cdi_pid is null and but.bul_id=$FORM{'bul_id'}|;
}elsif(exists($FORM{'f_ids'})){

#	use JSON;
#	my $f_ids = from_json($FORM{'f_ids'});
	my $f_ids = &JSON::XS::decode_json($FORM{'f_ids'});
	my @BLDS;
	my @CONS;
	for(my $cnt=0;$cnt<scalar @$f_ids;$cnt++){
		if($f_ids->[$cnt] =~ /^BP/){
#			push(@BLDS,"'".$f_ids->[$cnt]."'");
			push(@BLDS,$f_ids->[$cnt]);
		}else{
#			push(@CONS,"'".$f_ids->[$cnt]."'");
			push(@CONS,$f_ids->[$cnt]);
		}
	}
	if(scalar @BLDS > 0){
		my $sql = qq|select cdi_name from view_representation where ci_id=$FORM{'ci_id'} and cb_id=$FORM{'cb_id'} and md_id=$FORM{'md_id'} and mv_id=$FORM{'mv_id'} and bul_id=$FORM{'bul_id'} and rep_id in (|.join(",",map {"'".$_."'"} @BLDS).qq|)|;
#		print $LOG __LINE__,":\$sql=[$sql]\n";
		my $sth = $dbh->prepare($sql) or die;
		$sth->execute();
#		print $LOG __LINE__,":\$sth->rows=[".$sth->rows."]\n";
		if($sth->rows>0){
			@BLDS = ();
			my $cdi_name;
			my $column_number = 0;
			$sth->bind_col(++$column_number, \$cdi_name, undef);
			while($sth->fetch){
				push(@CONS,$cdi_name) if(defined $cdi_name);
			}
		}
		$sth->finish;
		undef $sth;
	}
#	print $LOG __LINE__,":\@BLDS=[".join(",",@BLDS)."]\n";
#	print $LOG __LINE__,":\@CONS=[".join(",",@CONS)."]\n";
	if(scalar @CONS > 0 && exists $FORM{'degenerate_same_shape_icons'} && defined $FORM{'degenerate_same_shape_icons'} && $FORM{'degenerate_same_shape_icons'} eq 'true'){
		&getDegenerateSameShapeIcons($dbh,\%FORM,\@CONS);
	}


	$sql  = qq|select|;
	$sql .= qq| cdi_name as f_id|;
	$sql .= qq|,cdi_name as common_id|;
	$sql .= qq|,cdi_name_j as name_j|;
	$sql .= qq|,cdi_name_e as name_e|;
	$sql .= qq|,cdi_name_k as name_k|;
	$sql .= qq|,cdi_name_l as name_l|;
	$sql .= qq|,cdi_taid   as taid|;
	$sql .= qq|,rep_xmin as xmin|;
	$sql .= qq|,rep_xmax as xmax|;
	$sql .= qq|,rep_ymin as ymin|;
	$sql .= qq|,rep_ymax as ymax|;
	$sql .= qq|,rep_zmin as zmin|;
	$sql .= qq|,rep_zmax as zmax|;
	$sql .= qq|,rep_volume as volume|;
	$sql .= qq|,rep_cube_volume as cube_volume|;
	$sql .= qq|,(rep_density_objs::real/rep_density_ends::real) as density|;

	$sql .= qq|,rep_primitive as primitive|;
	$sql .= qq|,EXTRACT(EPOCH FROM rep_entry) as entry|;
	$sql .= qq|,EXTRACT(EPOCH FROM rep_entry) as lastmod|;
	$sql .= qq| from view_representation as bp3d|;
	$sql .= qq| left join (select ci_id,cb_id,cdi_id,seg_id from concept_data) as cd on cd.ci_id = bp3d.ci_id AND cd.cb_id = bp3d.cb_id AND cd.cdi_id = bp3d.cdi_id|;
	$sql .= qq| left join (select seg_id,seg_name,seg_color,seg_thum_bgcolor,seg_thum_bocolor from concept_segment) as cs on cs.seg_id = cd.seg_id|;
	$sql .= qq| where bp3d.ci_id=$FORM{'ci_id'} and bp3d.cb_id=$FORM{'cb_id'} and bp3d.md_id=$FORM{'md_id'} and bp3d.mv_id=$FORM{'mv_id'} and bp3d.bul_id=$FORM{'bul_id'}|;

	$sql .= " and rep_id in (". join(",",map {"'".$_."'"} @BLDS).")" if(scalar @BLDS > 0);
	$sql .= " and cdi_name in (". join(",",map {"'".$_."'"} @CONS).")" if(scalar @CONS > 0);

	if(exists($FORM{'dir'}) && exists($FORM{'sort'})){
		my $key = $FORM{'sort'};
		$key = 'rep_id' if($key eq 'b_id');
		$sql .= qq| order by $key $FORM{'dir'}|;
	}else{
	}
		print $LOG __LINE__,":\$sql=[$sql]\n" if(defined $LOG);

}elsif(exists $FORM{'node'} && defined $FORM{'node'} && $FORM{'node'} eq "search" && exists($FORM{'query'})){
	my $operator = &get_ludia_operator();
	my $query = &cgi_lib::common::decodeUTF8($FORM{'query'});
	my $space = &cgi_lib::common::decodeUTF8(qq|　|);
#	&utf8::decode($query) unless(&utf8::is_utf8($query));
#	&utf8::decode($space) unless(&utf8::is_utf8($space));
	$query =~ s/$space/ /g;
#	&utf8::encode($query);
	$query = &cgi_lib::common::encodeUTF8($query);
	$sql .= qq|((|;
#	my @QUERY = split(/\s+/,$query);
#	for(my $cnt=0;$cnt<scalar @QUERY;$cnt++){
#		$sql .= qq| and | if($cnt>0);
#		$sql .= qq|ARRAY[f.f_id,f.f_name_j,f.f_name_e,f.f_name_k,f.f_name_l,f.f_syn_j,f.f_syn_e,f.f_taid] $operator ?|; push(@bind_values,$QUERY[$cnt]);
#	}
	$sql .= qq|ARRAY[cdi.cdi_name,cdi.cdi_name_j,cdi.cdi_name_e,cdi.cdi_name_k,cdi.cdi_name_l,cdi.cdi_syn_j,cdi.cdi_syn_e,cdi.cdi_taid] $operator ?|; push(@bind_values,qq|*D+ $query|);


	$sql .= qq|))|;
	$sql .= qq| and bp3d.rep_delcause is null|;
	$sql .= qq| and but.bul_id <= 4| if(!$lsdb_Auth);
#}elsif($FORM{'node'} eq "point"){
#	$sql  = qq|select|;
#	$sql .= qq| f_id|;
#	$sql .= qq| from bp3d_point|;
#	$sql .= qq| where ci_id=$FORM{'ci_id'} and cb_id=$FORM{'cb_id'} and |;
#	$sql .= qq| p_delcause is null|;

}elsif(exists($FORM{'f_depth'}) && exists($FORM{'tree_pid'})){
	$sql  = qq|
select
 but.cdi_id,
 but.cdi_pid,
 but.bul_id,
 cdi.cdi_name,
 COALESCE(but1.num,0)
from
 buildup_tree as but
left join (
 select
  md_id,
  mv_id,
  mr_id,
  ci_id,
  cb_id,
  bul_id,
  cdi_pid,
  count(cdi_pid) as num
 from
  buildup_tree
 group by
  md_id,
  mv_id,
  mr_id,
  ci_id,
  cb_id,
  bul_id,
  cdi_pid
) as but1 on (
 but.md_id = but1.md_id and
 but.mv_id = but1.mv_id and
 but.mr_id = but1.mr_id and
 but.ci_id = but1.ci_id and
 but.cb_id = but1.cb_id and
 but.cdi_id = but1.cdi_pid and
 but.bul_id = but1.bul_id
)
left join (select ci_id,cdi_id,cdi_name,cdi_delcause from concept_data_info) as cdi on (but.ci_id = cdi.ci_id and but.cdi_id = cdi.cdi_id)
left join (select ci_id,cdi_id,cdi_name,cdi_delcause from concept_data_info) as cdi2 on (but.ci_id = cdi2.ci_id and but.cdi_pid = cdi2.cdi_id)
where
 but.md_id=$FORM{'md_id'} and
 but.mv_id=$FORM{'mv_id'} and
 but.mr_id=$FORM{'mr_id'} and
 but.ci_id=$FORM{'ci_id'} and
 but.cb_id=$FORM{'cb_id'} and
 but.bul_id=? and
 cdi2.cdi_name=? and
 but_delcause is null
order by
 cdi.cdi_name_e
|;

	push(@bind_values,$FORM{'t_type'});
	push(@bind_values,$FORM{'tree_pid'});

}else{
	if(exists $FORM{'txpath'} && defined $FORM{'txpath'}){
		my @TEMP = split(/\//,$FORM{'txpath'});
		my $f_id = pop @TEMP;
		$FORM{'node'} = $f_id if($f_id);
	}
	if(exists $FORM{'node'} && defined $FORM{'node'} && $FORM{'node'} =~ /^ctg_/){
		if(!exists($FORM{'pid'})){
			$FORM{'pid'} = $FORM{'node'};
			$FORM{'pid'} =~ s/^ctg_//g;
		}
		$sql .= qq|but.cdi_pid=?|;
		push(@bind_values,$FORM{'pid'});
#	}elsif($FORM{'node'} =~ /^(?:FMA|BP|TAL)/){
	}else{
#print $LOG __LINE__,":\n";
		$FORM{'pid'} = $FORM{'node'} unless(exists($FORM{'pid'}));
		$sql .= qq|cdi2.cdi_name=?|;
		push(@bind_values,$FORM{'node'});
	}

	if(exists($FORM{'t_type'})){
		$sql .= qq| and but.bul_id=?|;
		push(@bind_values,$FORM{'t_type'});
	}
}

if(exists $FORM{'node'} && defined $FORM{'node'} && $FORM{'node'} eq "search"){
	$IMAGES->{totalCount} = 0;
	if(scalar @bind_values > 0){

#print $LOG __LINE__,":sql=[$sql]\n";

		my $sth = $dbh->prepare($sql);
		$sth->execute(@bind_values);
		$IMAGES->{totalCount} = $sth->rows();
		$sth->finish;
		undef $sth;
	}
}

if(!exists($FORM{'f_ids'}) && !exists($FORM{'f_depth'}) && !exists($FORM{'tree_pid'}) && (!exists $FORM{'node'} || !defined $FORM{'node'} || $FORM{'node'} ne "point")){
	$sql .= qq| order by |;
#	if(exists($FORM{'sorttype'})){
#		if($FORM{'sorttype'} eq "order"){
#			$sql .= qq|but.t_$FORM{'sorttype'},|;
#		}elsif($FORM{'sorttype'} eq "id"){
#			$sql .= qq|f.f_$FORM{'sorttype'},|;
#		}
#	}
	$sql .= qq|but.bul_id,cdi.cdi_name|;
}

my $sth_count;
if(exists $FORM{'node'} && defined $FORM{'node'} && $FORM{'node'} eq "search"){
	if(scalar @bind_values > 0){
		if(exists($FORM{limit})){
			$sql .= qq| limit $FORM{limit}|;
		}else{
			$sql .= qq| limit 400|;
		}
		$sql .= qq| offset $FORM{start}| if(exists($FORM{start}));
	}
	$sth_count = $dbh->prepare(qq|select cdi_name from tree where ci_id=$FORM{'ci_id'} and cb_id=$FORM{'cb_id'} and but.cdi_pname=? and but.bul_id=$FORM{'t_type'}|)
}

#print $LOG __LINE__,":sql=[$sql]\n";

my $sth = $dbh->prepare($sql) or die($sql);

if(scalar @bind_values > 0){
	$sth->execute(@bind_values) or die($sql);
}elsif(exists($FORM{'pid'})){
	$sth->execute($FORM{'pid'}) or die($sql);
}else{
	$sth->execute() or die($sql);
}
#print $LOG __LINE__,":rows=[",$sth->rows(),"]\n";

my($t_id,$t_pid,$a_order,$t_type,$a_fmaid,$f_taid,$a_name_j,$a_name_e,$a_name_k,$a_name_l,$a_syn_j,$a_syn_e,$a_organsys_j,$a_organsys_e,$a_phase,$f_zmin,$f_zmax,$f_volume,$a_delcause,$a_entry,$a_modified,$e_openid,$m_openid,$num,$phy_name,$phy_id,$b_state);

my $column_number = 0;
if(!exists($FORM{'f_ids'}) && (!exists $FORM{'node'} || !defined $FORM{'node'} || $FORM{'node'} ne "point")){
	$sth->bind_col(++$column_number, \$t_id, undef);
	$sth->bind_col(++$column_number, \$t_pid, undef);
#	$sth->bind_col(++$column_number, \$a_order, undef);
	$sth->bind_col(++$column_number, \$t_type, undef);
}
$sth->bind_col(++$column_number, \$a_fmaid, undef);

#print $LOG __LINE__,":\$column_number=[",$column_number,"]\n";

if(!exists($FORM{'f_ids'}) && (!exists $FORM{'node'} || !defined $FORM{'node'} || $FORM{'node'} ne "point")){
	$sth->bind_col(++$column_number, \$num, undef);
}else{
	$num = 0;
}
my %DISP_FMA = ();



my $root;
if(exists $FORM{'txpath'} && defined $FORM{'txpath'}){
	my @PATH = split(/\//,$FORM{'txpath'});
	$root = $PATH[1];
}

while($sth->fetch){
	if(exists $FORM{'node'} && defined $FORM{'node'} && $FORM{'node'} eq "search"){
		next if(exists($DISP_FMA{$a_fmaid}));
		$DISP_FMA{$a_fmaid} = $a_fmaid;
	}
	my $rtn = &getFMA($dbh,\%FORM,$a_fmaid,$LOG);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON($rtn,1), $LOG) if(defined $LOG);
#print $LOG __LINE__,":\$a_fmaid=[",$a_fmaid,"]\n";
#print $LOG __LINE__,":\$rtn=[",$rtn,"]\n";
#	if(defined $rtn){
#		foreach my $key (sort keys(%$rtn)){
#			print $LOG __LINE__,":\$rtn->{$key}=[$rtn->{$key}]\n";
#		}
#	}

	my $url;
	my $path_str;
#	if(defined $rtn && exists $rtn->{'zmax'} && defined $rtn->{'zmax'}){
#		$url = &getImagePath($a_fmaid,$FORM{'position'},$FORM{'version'},'120x120',$FORM{'t_type'},$credit);
	if(defined $rtn){
		$rtn->{'src'} = "icon/inprep.png" if($rtn->{'src'} eq "resources/images/default/s.gif");
		$url = $rtn->{'src'};
&cgi_lib::common::message($url, $LOG) if(defined $LOG);

		$path_str = &getGlobalPath();
		if(defined $path_str){
			$path_str .= qq|icon.cgi|;
		}else{
			my $host = (split(/,\s*/,(exists($ENV{'HTTP_X_FORWARDED_HOST'})?$ENV{'HTTP_X_FORWARDED_HOST'}:$ENV{'HTTP_HOST'})))[0];
			my @TEMP = split("/",$ENV{'REQUEST_URI'});
			$TEMP[$#TEMP] = qq|icon.cgi|;
			$path_str = join("/",@TEMP);
			$path_str = qq|http://$host$path_str|;
		}

		$path_str = qq|$path_str?i=|;
		my $p = &url_encode(exists $FORM{'position'} && defined $FORM{'position'} ? $FORM{'position'} : 'front');
		if(exists $rtn->{'b_id'} && defined $rtn->{'b_id'}){
#			$path_str .= &url_encode($rtn->{'b_id'}) . qq|&p=$FORM{'position'}&c=1|;
			$path_str .= &url_encode($rtn->{'b_id'}) . qq|&p=$p|;
		}else{

			my $v = &url_encode(exists $FORM{'version_name'} && defined $FORM{'version_name'} ? $FORM{'version_name'} : (exists $FORM{'version'} && defined $FORM{'version'} ? $FORM{'version'} : ''));
			my $m = &url_encode(exists $FORM{'tg_model'} && defined $FORM{'tg_model'} ? $FORM{'tg_model'} : (exists $FORM{'tg_id'} && defined $FORM{'tg_id'} ? $FORM{'tg_id'} : ''));

			$path_str .= &url_encode($a_fmaid) . qq|&p=$p&v=$v&t=$type_name&m=$m|;
			$path_str .= qq|&r=$root| if(defined $root && $root ne "" && $root ne "$a_fmaid");
		}
#		if(-e $url && -s $url){
#			$url .= '?'.(stat($url))[9];
#		}else{
#			$url = $path_str;
#		}
	}else{
		$url = "icon/inprep.png";
	}
&cgi_lib::common::message($url, $LOG) if(defined $LOG);

#print $LOG __LINE__,":[$url][",(-s $url),"]\n";

	my $HASH = {};
	foreach my $key (keys(%$rtn)){
		$HASH->{$key} = $rtn->{$key};
	}

	$HASH->{'id'} = $t_id;
	$HASH->{'pid'} = $t_pid;
	$HASH->{'t_type'} = $t_type;
	$HASH->{'src'} = $url;
	$HASH->{'srcstr'} = $path_str;
	$HASH->{'f_id'} = $a_fmaid;

	if(exists $FORM{'node'} && defined $FORM{'node'} && $FORM{'node'} eq "search"){
		$SEARCH_TREE_PATH{$FORM{'t_type'}} = {} unless(exists($SEARCH_TREE_PATH{$FORM{'t_type'}}));
		if(exists($SEARCH_TREE_PATH{$FORM{'t_type'}}->{$a_fmaid})){
			$HASH->{'search_c_path'} = $SEARCH_TREE_PATH{$FORM{'t_type'}}->{$a_fmaid};
		}else{
			@TREE_ROUTE = ();
			$sth_count->execute($a_fmaid);
			$num = $sth_count->rows();
			$sth_count->finish;
			if($num > 0){#枝がある場合は、自分のパスを作成
#				&getTree_Path2Root($FORM{'t_type'},$a_fmaid,\@TREE_ROUTE);
				&getTree_Path2Root(\%FORM,$a_fmaid,\@TREE_ROUTE);
			}else{#枝がない場合は、親のパスを作成
				my @TREE_PID = ();
				$sth_tree_p->execute($FORM{'t_type'},$a_fmaid);
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
				if(scalar @TREE_PID > 0){
					foreach my $f_pid (@TREE_PID){
#						&getTree_Path2Root($FORM{'t_type'},$f_pid,\@TREE_ROUTE);
						&getTree_Path2Root(\%FORM,$f_pid,\@TREE_ROUTE);
						last if(scalar @TREE_ROUTE > 100);
					}
				}
			}
			if(scalar @TREE_ROUTE > 0){
				@TREE_ROUTE = sort {scalar (split(/\t/,$a)) <=> scalar (split(/\t/,$b)) } sort @TREE_ROUTE;
				my $route = shift @TREE_ROUTE;
				my @FIDS = reverse(split(/\t/,$route));
				$HASH->{'search_c_path'} = join("/",@FIDS);
				$SEARCH_TREE_PATH{$FORM{'t_type'}}->{$a_fmaid} = $HASH->{'search_c_path'};
			}
		}
	}
	$HASH->{'search_c_path'} = undef unless(exists($HASH->{'search_c_path'}));

#print $LOG __LINE__,":\$a_fmaid=[",$a_fmaid,"],\$num=[",$num,"]\n";
	$HASH->{'u_path'} = undef;
	$HASH->{'c_path'} = undef;
	$HASH->{'state'} = undef;

#	if($num > 0 && exists($TREE{$a_fmaid})){
	if($num > 0 && exists($TREE{$a_fmaid}) && $FORM{'node'} ne "search"){
		my $t_delcause;
		my $temp_fid = $a_fmaid;
		my @p_path = ();
		while(exists($TREE{$temp_fid})){
			unshift @p_path,$temp_fid;
			if(exists($TREE{$temp_fid}->{'t_delcause'}) && defined $TREE{$temp_fid}->{'t_delcause'}){
				$t_delcause = 1;
				last;
			}
#			eval{
				my $temp_fpid;
				foreach $temp_fpid (@{$TREE{$temp_fid}->{'f_pids'}}){
					if(exists($TREE{$temp_fpid}->{'t_delcause'}) && defined $TREE{$temp_fpid}->{'t_delcause'}){
						next;
					}else{
						last;
					}
				}
				if(defined $temp_fpid){
					if(exists($TREE{$temp_fpid}->{'t_delcause'}) && defined $TREE{$temp_fpid}->{'t_delcause'}){
#print $LOG __LINE__,":\$temp_fpid=[",$temp_fpid,"]\n";
						$t_delcause = 1;
						last;
					}else{
						$temp_fid = $temp_fpid;
					}
				}else{
					last;
				}
#			};
#			if($@){
#				print $LOG __LINE__,":",$@,"\n";
#				last;
#			}
		}
		$TREE_PATH{$a_fmaid} = join("/",@p_path);

#print $LOG __LINE__,":\$TREE_PATH{$a_fmaid}=[",$TREE_PATH{$a_fmaid},"]\n";
#print $LOG __LINE__,":\$t_delcause=[",$t_delcause,"]\n";

		unless(defined $t_delcause){
			$HASH->{'c_path'} = $TREE_PATH{$a_fmaid};
		}else{
			undef $t_delcause;
		}
	}

#	delete $HASH->{'state'};
	$HASH->{'state'} = $rtn->{'state'} if(defined $rtn->{'state'} && defined $t_type && $t_type eq "1");

	&getPointInfo($HASH);

	delete $HASH->{'delcause'};
	delete $HASH->{'m_openid'};
	if($lsdb_Auth){
		$HASH->{'delcause'} = $rtn->{'delcause'};
		$HASH->{'m_openid'} = $rtn->{'openid'};
	}

	if(exists $FORM{'disptype'} && defined $FORM{'disptype'} && $FORM{'disptype'} eq 'tree'){
		$FORM{'f_depth'} = 1 unless(exists $FORM{'f_depth'} && defined $FORM{'f_depth'});
		$HASH->{'style'} .= qq|margin-left:|. ($FORM{'f_depth'}*6) .qq|em;|;
		$HASH->{'tree_depth'} = $FORM{'f_depth'};
		$HASH->{c_num} = $num;

		if(defined $HASH->{'c_path'}){
			$HASH->{'u_path'} = $HASH->{'c_path'};
			$HASH->{'c_path'} = undef;
		}

		$HASH->{'u_path'} = undef;
		$HASH->{'c_path'} = undef;
		$HASH->{'state'} = undef;
	}

	unless(defined $HASH->{'u_path'}){
		my $txpath = &getTreePath($a_fmaid);
#print $LOG __LINE__,":[$a_fmaid]=[$txpath]\n";
#		if(defined $txpath && $txpath ne ""){
#			$HASH->{'u_path'} = $txpath;
#		}else{
#			$HASH->{'u_path'} = 'ctg_';
#		}
	}

	push(@{$IMAGES->{'images'}},$HASH);

#	undef $name;
#	undef $organsys;
}
$sth->finish;

#print $LOG __LINE__,":\$IMAGES->{'images'}=[",(scalar @{$IMAGES->{'images'}}),"]\n";

if(scalar @{$IMAGES->{'images'}} > 0){
	#ソート順が未指定の場合、指定されたfma_id順に並べなおす
	if(exists $FORM{'f_ids'} && defined $FORM{'f_ids'} && !exists($FORM{'dir'}) && !exists($FORM{'sort'})){
		my %HASH = ();
		foreach my $fma (@{$IMAGES->{'images'}}){
			$HASH{$fma->{'f_id'}} = $fma;
		}
		$IMAGES->{'images'} = ();
#		use JSON;
#		my $f_ids = from_json($FORM{'f_ids'});
		my $f_ids = &JSON::XS::decode_json($FORM{'f_ids'});
		for(my $cnt=0;$cnt<scalar @$f_ids;$cnt++){
			push(@{$IMAGES->{'images'}},$HASH{$f_ids->[$cnt]}) if(exists($HASH{$f_ids->[$cnt]}));
		}
	}
	unless(exists $FORM{'f_ids'} && defined $FORM{'f_ids'}){

		@{$IMAGES->{'images'}} =
			sort { defined $b->{'density'}        ? $b->{'density'}        : 0 <=> defined $a->{'density'}        ? $a->{'density'}        : 0 }
			sort { defined $b->{'primitive'}      ? $b->{'primitive'}      : 0 <=> defined $a->{'primitive'}      ? $a->{'primitive'}      : 0 }
			sort { defined $b->{'used_parts_num'} ? $b->{'used_parts_num'} : 0 <=> defined $a->{'used_parts_num'} ? $a->{'used_parts_num'} : 0 }
			sort { $a->{'name_e'}         cmp $b->{'name_e'}         }
			@{$IMAGES->{'images'}};

		if(exists $FORM{'sorttype'} && defined $FORM{'sorttype'}){
			my $st = $FORM{'sorttype'};
			if($st =~ /^(zmax|volume|lastmod|tweet_num|density)$/){
				@{$IMAGES->{'images'}} = sort {
					if(defined $b->{$st} && defined $a->{$st}){
						$b->{$st} <=> $a->{$st}
					}elsif(defined $b->{$st}){
						1;
					}elsif(defined $a->{$st}){
						-1;
					}else{
						0;
					}
				} @{$IMAGES->{'images'}};
			}
			elsif($st =~ /^(taid)$/){
				@{$IMAGES->{'images'}} = sort {
					if(defined $b->{$st} && defined $a->{$st}){
						$a->{$st} cmp $b->{$st}
					}elsif(defined $b->{$st}){
						1;
					}elsif(defined $a->{$st}){
						-1;
					}else{
						0;
					}
				} @{$IMAGES->{'images'}};
			}
			elsif($st =~ /^(zmin)$/){
#				@{$IMAGES->{'images'}} = sort {$a->{$st} <=> $b->{$st} } @{$IMAGES->{'images'}};
				@{$IMAGES->{'images'}} = sort {
					if(defined $b->{$st} && defined $a->{$st}){
						$b->{$st} <=> $a->{$st}
					}elsif(defined $b->{$st}){
						1;
					}elsif(defined $a->{$st}){
						-1;
					}else{
						0;
					}
				} @{$IMAGES->{'images'}};
			}
			elsif($st =~ /^(name_j|name_k|name_e|name_l)$/){
				@{$IMAGES->{'images'}} = sort {
					if(defined $a->{'density'} && defined $b->{'density'}){
						0;
					}elsif(defined $a->{'density'}){
						-1;
					}elsif(defined $b->{'density'}){
						1;
					}
				} sort {
					if(defined $a->{$st} && defined $b->{$st}){
						$a->{$st} cmp $b->{$st};
					}elsif(defined $a->{$st}){
						-1;
					}elsif(defined $b->{$st}){
						1;
					}else{
						0;
					}
				} @{$IMAGES->{'images'}};
			}
		}else{
##			if($FORM{'lng'} eq 'ja'){
##				@{$IMAGES->{'images'}} = sort {$a->{'name_j'} cmp $b->{'name_j'}} @{$IMAGES->{'images'}};
##			}else{
#				@{$IMAGES->{'images'}} = sort {$a->{'name_e'} cmp $b->{'name_e'}} @{$IMAGES->{'images'}};
##			}
#			@{$IMAGES->{'images'}} = sort {defined $b->{'density'} <=> defined $a->{'density'}} sort {defined $b->{'used_parts_num'} <=> defined $a->{'used_parts_num'}} @{$IMAGES->{'images'}};
		}
	}
}

#print $LOG __LINE__,":\$IMAGES->{'images'}=[",(scalar @{$IMAGES->{'images'}}),"]\n";

if(0 && exists($FORM{'pid'})){

	my $t_ppid;
	$t_ppid = 1;

	if(defined $t_ppid){
		my $sql  = qq|
select
 but.cdi_id,
 but.cdi_pid,
 but.bul_id,
 cdi.cdi_name,
 COALESCE(t.num,0)
from
 buildup_tree as but
left join (
 select
  md_id,
  mv_id,
  mr_id,
  ci_id,
  cb_id,
  bul_id,
  cdi_pid,
  count(cdi_pid) as num
 from
  buildup_tree
 group by
  md_id,
  mv_id,
  mr_id,
  ci_id,
  cb_id,
  bul_id,
  cdi_pid
) as t on (
 but.md_id = t.md_id and
 but.mv_id = t.mv_id and
 but.mr_id = t.mr_id and
 but.ci_id = t.ci_id and
 but.cb_id = t.cb_id and
 but.cdi_id = t.cdi_pid and
 but.bul_id = t.bul_id
)
left join (select ci_id,cdi_id,cdi_name,cdi_delcause from concept_data_info) as cdi on (but.ci_id = cdi.ci_id and but.cdi_id = cdi.cdi_id)
where
 but.md_id=$FORM{'md_id'} and
 but.mv_id=$FORM{'mv_id'} and
 but.mr_id=$FORM{'mr_id'} and
 but.ci_id=$FORM{'ci_id'} and
 but.cb_id=$FORM{'cb_id'} and
|;

		if($FORM{'node'} =~ /^ctg_/){
			$sql .= qq|but.cdi_id = ? and but.but_delcause is null and cdi.cdi_delcause is null|;
		}else{
			$sql .= qq|cdi.cdi_name = ? and but.but_delcause is null and cdi.cdi_delcause is null|;
		}

		$sql .= qq| and but.bul_id=?| if(exists($FORM{'t_type'}));
		my @bind_values = ();
		push(@bind_values,$FORM{'pid'});
		push(@bind_values,$FORM{'t_type'}) if(exists($FORM{'t_type'}));

#print $LOG __LINE__,":sql=[$sql]\n";
#print $LOG __LINE__,":bind_values=[",join("\n",@bind_values),"]\n";

		$sth = $dbh->prepare($sql) or die;
		$sth->execute(@bind_values);
		if($sth->rows>0){
			$column_number = 0;
			$sth->bind_col(++$column_number, \$t_id, undef);
			$sth->bind_col(++$column_number, \$t_pid, undef);
#			$sth->bind_col(++$column_number, \$a_order, undef);
			$sth->bind_col(++$column_number, \$t_type, undef);
			$sth->bind_col(++$column_number, \$a_fmaid, undef);
			$sth->bind_col(++$column_number, \$num, undef);
			$sth->fetch;

			my $rtn = &getFMA($dbh,\%FORM,$a_fmaid,$LOG);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON($rtn,1), $LOG) if(defined $LOG);
#			my $url = &getImagePath($a_fmaid,$FORM{'position'},$FORM{'version'},'120x120',$FORM{'t_type'},$credit);
			$rtn->{'src'} = "icon/inprep.png" if($rtn->{'src'} eq "resources/images/default/s.gif");
			my $url = $rtn->{'src'};

			my $path_str = &getGlobalPath();
			if(defined $path_str){
				$path_str .= qq|icon.cgi|;
			}else{
				my $host = (split(/,\s*/,(exists($ENV{'HTTP_X_FORWARDED_HOST'})?$ENV{'HTTP_X_FORWARDED_HOST'}:$ENV{'HTTP_HOST'})))[0];
				my @TEMP = split("/",$ENV{'REQUEST_URI'});
				$TEMP[$#TEMP] = qq|icon.cgi|;
				$path_str = join("/",@TEMP);
				$path_str = qq|http://$host$path_str|;
			}

#			$path_str = qq|$path_str?i=| . &url_encode($a_fmaid) . qq|&p=$FORM{'position'}&v=|.&url_encode($FORM{'version_name'}?$FORM{'version_name'}:$FORM{'version'}).qq|&t=$type_name&c=$credit&m=|.&url_encode(exists($FORM{'tg_model'})?$FORM{'tg_model'}:$FORM{'tg_id'});

			my $p = &url_encode(exists $FORM{'position'} && defined $FORM{'position'} ? $FORM{'position'} : 'front');
			my $v = &url_encode(exists $FORM{'version_name'} && defined $FORM{'version_name'} ? $FORM{'version_name'} : (exists $FORM{'version'} && defined $FORM{'version'} ? $FORM{'version'} : ''));
			my $m = &url_encode(exists $FORM{'tg_model'} && defined $FORM{'tg_model'} ? $FORM{'tg_model'} : (exists $FORM{'tg_id'} && defined $FORM{'tg_id'} ? $FORM{'tg_id'} : ''));

			$path_str = qq|$path_str?i=| . &url_encode($a_fmaid) . qq|&p=$p&v=$v&t=$type_name&c=1&m=$m|;
			$path_str .= qq|&r=$root| if(defined $root && $root ne "" && $root ne "$a_fmaid");

#			if(-e $url && -s $url){
#				my $mtime = (stat($url))[9];
#				$url .= "?$mtime";
#			}else{
#				$url = $path_str;
#			}

			my $HASH = {};
			foreach my $key (keys(%$rtn)){
				$HASH->{$key} = $rtn->{$key};
			}
			$HASH->{'id'} = $t_id;
			$HASH->{'pid'} = $t_pid;
			$HASH->{'t_type'} = $t_type;
			$HASH->{'src'} = $url;
			$HASH->{'srcstr'} = $path_str;
			$HASH->{'f_id'} = $a_fmaid;

			if($num > 0 && exists($TREE{$a_fmaid})){
				my $temp_fid = $a_fmaid;
				my @p_path = ();
				while(exists($TREE{$temp_fid})){
					unshift @p_path,$temp_fid;
					if(exists($TREE{$temp_fid}->{'f_pids'}) && defined $TREE{$temp_fid}->{'f_pids'}){
						$temp_fid = $TREE{$temp_fid}->{'f_pids'}->[0];
					}else{
						last;
					}
				}
				pop @p_path if(scalar @p_path > 0);
				$TREE_PATH{$a_fmaid} = join("/",@p_path);

				if(exists($TREE_PATH{$a_fmaid}) && $TREE_PATH{$a_fmaid} ne ""){
					$HASH->{'u_path'} = $TREE_PATH{$a_fmaid};
				}else{
					$HASH->{'u_path'} = 'ctg_';
				}

				if(exists($FORM{'txpath'})){
					my $txpath = $FORM{'txpath'};
					$txpath =~ s/^\/+//g;
					@p_path = split(/\//,$txpath);
					pop @p_path if(scalar @p_path > 0);
					$TREE_PATH{$a_fmaid} = join("/",@p_path);

					if(exists($TREE_PATH{$a_fmaid}) && $TREE_PATH{$a_fmaid} ne ""){
						$HASH->{'u_path'} = $TREE_PATH{$a_fmaid};
					}else{
						$HASH->{'u_path'} = 'ctg_';
					}
				}
			}

			delete $HASH->{'state'};
			$HASH->{'state'} = $rtn->{'state'} if(defined $rtn->{'state'} && defined $t_type && $t_type eq "1");

			&getPointInfo($HASH);

			delete $HASH->{'delcause'};
			delete $HASH->{'m_openid'};
			if($lsdb_Auth){
				$HASH->{'delcause'} = $rtn->{'delcause'};
				$HASH->{'m_openid'} = $rtn->{'openid'};
			}

			if(exists $FORM{'disptype'} && defined $FORM{'disptype'} && $FORM{'disptype'} eq 'tree'){
				delete $IMAGES->{'images'};
				$HASH->{'tree_depth'} = 0;
			}

			unshift(@{$IMAGES->{'images'}},$HASH);
		}
	}
}

undef $sth;

#print $LOG __LINE__,":\$IMAGES->{'images'}=[",(scalar @{$IMAGES->{'images'}}),"]\n";

$IMAGES->{'success'} = JSON::XS::true if(exists($FORM{'callback'}));
#foreach my $key (sort keys(%$IMAGES)){
#	print $LOG __LINE__,":$key=[",(ref $IMAGES->{$key}),"][",$IMAGES->{$key},"]\n";
#}
#use JSON;
#my $json = to_json($IMAGES);
#my $json = &JSON::XS::encode_json($IMAGES);
#print $CACHE $json;

#say $LOG __LINE__.":".$json;
#$json = $FORM{'callback'}."(".$json.")" if(exists($FORM{'callback'}));
#print $json;
my $json = &cgi_lib::common::printContentJSON($IMAGES,\%FORM);
say $LOG __LINE__.":".$json if(defined $LOG);

store \%SEARCH_TREE_PATH, $store_search_tree_file;

store $IMAGES, $store_contents_tree_file if(defined $store_contents_tree_file);

rmdir($store_lock) if(-e $store_lock);

umask($old_umask);

#close($CACHE);
#close($LOG);
exit;

