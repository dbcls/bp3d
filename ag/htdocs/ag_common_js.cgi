#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use File::Basename;

use File::Spec::Functions qw(catdir catfile);
use Cwd;
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'API'),&Cwd::abs_path(&catdir($FindBin::Bin,'..','lib')),&Cwd::abs_path(&catdir($FindBin::Bin,'..','..','ag-common','lib'));
use cgi_lib::common;
use AG::login;

require "common.pl";
require "common_db.pl";

my $disEnv = &getDispEnv();
my $agInterfaceType = $disEnv->{agInterfaceType};
my $useImageTransform = $disEnv->{useImageTransform};
my $pallteEmptyTextHidden = $disEnv->{pallteEmptyTextHidden};
my $autoRotationHidden = $disEnv->{autoRotationHidden};
my $useImagePost = $disEnv->{useImagePost};
my $usePickPalletSelect = $disEnv->{usePickPalletSelect};
my $usePickPartsSelect = $disEnv->{usePickPartsSelect};
my $sectionalViewHidden = $disEnv->{sectionalViewHidden};
my $useColorPicker = $disEnv->{useColorPicker};
my $usePickPartsSelectContinu = $disEnv->{usePickPartsSelectContinu};
my $useClickPickTabSelect = $disEnv->{useClickPickTabSelect};
my $modifyAxisOfRotation = $disEnv->{modifyAxisOfRotation};
my $useContentsTree = $disEnv->{useContentsTree};

$agInterfaceType = '5' unless(defined $agInterfaceType);
$useImageTransform = 'true' unless(defined $useImageTransform);
$pallteEmptyTextHidden = 'false' unless(defined $pallteEmptyTextHidden);
$autoRotationHidden = 'false' unless(defined $autoRotationHidden);
$useImagePost = 'true' unless(defined $useImagePost);
$usePickPalletSelect = 'true' unless(defined $usePickPalletSelect);
$usePickPartsSelect = 'true' unless(defined $usePickPartsSelect);
$sectionalViewHidden = 'false' unless(defined $sectionalViewHidden);
$useColorPicker = 'true' unless(defined $useColorPicker);
$usePickPartsSelectContinu = 'true' unless(defined $usePickPartsSelectContinu);
$useClickPickTabSelect = 'true' unless(defined $useClickPickTabSelect);
$modifyAxisOfRotation = 'true' unless(defined $modifyAxisOfRotation);
$useContentsTree = 'true' unless(defined $useContentsTree);

#2013年度下期納品用
$useContentsTree='false';

my %LOCALE = ();

my %FORM = ();
&decodeForm(\%FORM);
delete $FORM{_formdata} if(exists($FORM{_formdata}));

my %COOKIE = ();
&getCookie(\%COOKIE);

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = fileparse($0,@extlist);
#open(LOG,"> logs/$COOKIE{'ag_annotation.session'}.$cgi_name.txt");
#print LOG "\n[$logtime]:$0\n";
#foreach my $key (sort keys(%FORM)){
#	print LOG "\$FORM{$key}=[",$FORM{$key},"]\n";
#}
#foreach my $key (sort keys(%COOKIE)){
#	print LOG "\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
#}

#if(!exists($FORM{tp_ap}) && exists($COOKIE{'ag_annotation.session'})){
#	my $session = &getSession($COOKIE{'ag_annotation.session'});
#	$FORM{tp_ap} = join("&",@$session) if(defined $session);
##	print LOG __LINE__,":\$FORM{tp_ap}=[$FORM{tp_ap}]\n";
#}

$FORM{lng} = $COOKIE{"ag_annotation.locale"} if(!exists($FORM{lng}) && exists($COOKIE{"ag_annotation.locale"})); #とりあえず
$FORM{lng} = "en" if(!exists($FORM{lng}));
$agInterfaceType = '5' if(exists($FORM{tp_md}) && $agInterfaceType ne '5');

require "anatomography_locale.pl";
my %LOCALE_ANA = &getLocale($FORM{lng});
foreach my $key (keys(%LOCALE_ANA)){
	$LOCALE{$key} = $LOCALE_ANA{$key}
}
undef %LOCALE_ANA;

require "common_locale.pl";
my %LOCALE_BP3D = &getLocale($FORM{lng});
foreach my $key (keys(%LOCALE_BP3D)){
	$LOCALE{$key} = $LOCALE_BP3D{$key}
}
undef %LOCALE_BP3D;

if(scalar @ARGV == 1 && $ARGV[0] eq "--version"){
	my($prog_cat, $prog_dir, $prog_file) = File::Spec->splitpath($0);
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


#DEBUG 常に削除
#delete $FORM{parent} if(exists($FORM{parent}));
my $lsdb_OpenID;
my $lsdb_Auth;
my $lsdb_Config;
my $lsdb_Identity;
my $is_success;
my $parentURL = $FORM{parent} if(exists($FORM{parent}));
#delete $FORM{parent} if(exists($FORM{parent}));

if(defined $parentURL){
	($lsdb_OpenID,$lsdb_Auth,$lsdb_Config) = &openidAuth($parentURL);
}elsif(exists($COOKIE{openid_url}) && exists($COOKIE{openid_session})){
	($lsdb_OpenID,$lsdb_Auth,$lsdb_Config,$lsdb_Identity) = &AG::login::openidAuthSession($COOKIE{openid_url},$COOKIE{openid_session});
}
$lsdb_Auth = int($lsdb_Auth) if(defined $lsdb_Auth);

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

my $LOADING_IMG = qq|ext-2.2.1/resources/images/default/tree/loading.gif|;
my $LOADING_MSG = qq|<div style="padding:10px;font-size:11px;"><img src="$LOADING_IMG">$LOCALE{MSG_LOADING_DATA}</div>|;

my $TIME_FORMAT = "Y/m/d H:i:s";
my $DATE_FORMAT = "Y/m/d";

my $DEF_COLOR = &getDefaultColor();
my $DEF_COLOR_VAL = $DEF_COLOR;
$DEF_COLOR_VAL =~ s/^#+//g;

my $DEF_COLOR_POINT = &getDefaultPointColor();
my $DEF_COLOR_POINT_VAL = $DEF_COLOR_POINT;
$DEF_COLOR_POINT_VAL =~ s/^#+//g;

#my $tg_id;
#my $tgi_version;
=pod
{
	my $sql;
	$sql = qq|select tg_id|;
	if($FORM{lng} eq "ja"){
		$sql .= qq|,COALESCE(tgi_name_j,tgi_name_e)|;
	}else{
		$sql .= qq|,tgi_name_e|;
	}
	$sql .= qq| from tree_group_item where tgi_port is not null and tgi_delcause is null order by tg_id,tgi_id,tgi_order|;
	my $sth_tree_group_item = $dbh->prepare($sql);
	$sth_tree_group_item->execute();
	my $column_number = 0;
	$sth_tree_group_item->bind_col(++$column_number, \$tg_id, undef);
	$sth_tree_group_item->bind_col(++$column_number, \$tgi_version, undef);
	$sth_tree_group_item->fetch;
	$sth_tree_group_item->finish;
	undef $sth_tree_group_item;
}
=cut

=pod
my @MODEL_VERSION = ();
{
	my $sql;
	$sql = qq|select mv.md_id,mv.mv_id,mv.mv_version|;
	if($FORM{lng} eq "ja"){
		$sql .= qq|,COALESCE(mv.mv_name_j,mv.mv_name_e)|;
	}else{
		$sql .= qq|,mv.mv_name_e|;
	}
	$sql .= qq| from model_version as mv left join(select * from model) as md on (md.md_id=mv.md_id) where mv.mv_delcause is null order by md.md_order,mv.mv_order|;

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

$tg_id = $MODEL_VERSION[0][1] unless(defined $tg_id);
$tgi_version = $MODEL_VERSION[0][0] unless(defined $tgi_version);
=cut

my $info_html = 'info.html';
$info_html = 'info_en.html' if(exists($FORM{lng}) && $FORM{lng} eq "en" && -e 'info_en.html');

#my $host = (split(/,\s*/,(exists($ENV{HTTP_X_FORWARDED_HOST})?$ENV{HTTP_X_FORWARDED_HOST}:$ENV{HTTP_HOST})))[0];
#my @TEMP = split("/",$ENV{REQUEST_URI});
#my $sc_name = (split(/\?/,pop @TEMP))[0];
#my $app_path = (split(/\?/,$ENV{REQUEST_URI}))[0];
#$app_path =~ s/$sc_name/ag_annotation.cgi/;
#$app_path = qq|http://$host$app_path?|;

=pod
my $init_tree_group = 1;
my $init_bp3d_version = $MODEL_VERSION[0][0];

if(exists($COOKIE{"ag_annotation.images.tg_id"})){
	$init_tree_group = $COOKIE{"ag_annotation.images.tg_id"};
	if(exists($COOKIE{"ag_annotation.images.version"})){
#		my $ver =  from_json($COOKIE{"ag_annotation.images.version"});
		my $ver =  decode_json($COOKIE{"ag_annotation.images.version"});
		$init_bp3d_version = $ver->{$init_tree_group} if($ver && exists($ver->{$init_tree_group}));
	}
}
=cut

=pod
my $MODEL2TG = {};
my $TG2MODEL = {};
{
	my $tg_id;
	my $tg_model;
	my $tg_delcause;

	my $sql;
	$sql = qq|select distinct md_id,md_abbr,md_delcause from model|;
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
my $MODEL2TG_DATA = encode_json($MODEL2TG);
my $TG2MODEL_DATA = encode_json($TG2MODEL);
undef $MODEL2TG;
undef $TG2MODEL;
=cut

=pod
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
	$sql .= qq|,mv_delcause,mv_rep_key from model_version order by md_id,mv_order|;

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
=cut
my $CGI_PATH = &JSON::XS::encode_json(&getIntermediateServerPath());


my $US_STATE_DATA = qq|{}|;
my $US_KEYMAP_DATA = qq|[]|;
#if(exists($COOKIE{'ag_annotation.session'})){
#	my $state = &getSessionState($COOKIE{'ag_annotation.session'});
#	$US_STATE_DATA = $state if(defined $state);
#	my $keymap = &getSessionKeymap($COOKIE{'ag_annotation.session'});
#	$US_KEYMAP_DATA = $keymap if(defined $keymap);
#}

my %TP_AP=();
=pod
if(exists($FORM{tp_ap})){
	my @pairs = split(/&/,$FORM{tp_ap});
	foreach my $pair (@pairs) {
		my ($name, $value) = split(/=/, $pair);
		next if($value eq '');
		$value = &url_decode($value);
		unless(utf8::is_utf8($value)){
			# UTF8フラグ がない場合、decode して、UTF8フラグつきにする
			my $guessed_obj = Encode::Guess::guess_encoding($value, qw/euc-jp shift-jis/);
			$value = $guessed_obj->decode($value) if(ref $guessed_obj);
		}
		$value = Encode::encode('utf8', $value) if(utf8::is_utf8($value));
		$TP_AP{$name} .= "\0" if(exists($TP_AP{$name}));
		$TP_AP{$name} .= $value;
	}
	if(exists($TP_AP{bv})){
		$init_bp3d_version = $TP_AP{bv};
		my $tg_id;
		my $tgi_id;
		my $sth_tree_group_item = $dbh->prepare(qq|select tg_id,tgi_id from tree_group_item where tgi_version=?|);
		$sth_tree_group_item->execute($init_bp3d_version);
		my $column_number = 0;
		$sth_tree_group_item->bind_col(++$column_number, \$tg_id, undef);
		$sth_tree_group_item->bind_col(++$column_number, \$tgi_id, undef);
		$sth_tree_group_item->fetch;
		$init_tree_group = $tg_id if(defined $tg_id);
		$sth_tree_group_item->finish;
		undef $sth_tree_group_item;
	}
}
=cut
#close(LOG);

=pod
if(exists $ENV{REQUEST_METHOD}){
	print qq|Content-type: application/javascript; charset=UTF-8\n|;
	if(exists($TP_AP{bv}) && exists($TP_AP{tn})){
		my $types;
		if(exists($COOKIE{'ag_annotation.images.types'})){
			my $types_str = $COOKIE{'ag_annotation.images.types'};
	#		$types = from_json($types_str) if($types_str ne "");
			$types = decode_json($types_str) if($types_str ne "");
		}
		$types = {} unless(defined $types);
		if($TP_AP{tn} eq "isa"){
			$types->{$TP_AP{bv}} = '3';
		}elsif($TP_AP{tn} eq "partof"){
			$types->{$TP_AP{bv}} = '4';
		}else{
			$types->{$TP_AP{bv}} = '1';
		}
	#	print &setCookie('ag_annotation.images.types',to_json($types)),"\n";
		print &setCookie('ag_annotation.images.types',encode_json($types)),"\n";
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

	#	print &setCookie('ag_annotation.images.version',to_json($versions)),"\n";
		print &setCookie('ag_annotation.images.version',encode_json($versions)),"\n";
	}

	print qq|\n|;
}
=cut

#if(exists($FORM{tp_ap})){
#	my $value = $FORM{tp_ap};
#	$value =~ s/[^\\]"/\\"/g;
#	$value =~ s/[\r\n]+//g;
#	print qq|var gCOMMON_TPAP = Ext.urlDecode("$value");\n|;
#}else{
	print qq|var gCOMMON_TPAP;\n|;
#}

print <<HTML;
var gSelNode = null;

var model2tg;
var tg2model;
var version2tg;
var latestversion;
var cgipath = $CGI_PATH;
var glb_us_state = $US_STATE_DATA;
var glb_us_keymap = $US_KEYMAP_DATA;
//glb_us_keymap.length = 0;
if(glb_us_keymap.length==0){
	glb_us_keymap = [
HTML
if($sectionalViewHidden ne 'true'){
	print <<HTML;
	{
		'order': 1,
		'key'  : 'F8',
		'code' : Ext.EventObject.F8,
		'stop' : true,
		'cmd'  : 'ag-command-menu-clip-checkbox'
	},
HTML
}
print <<HTML;
	{
		'order': 2,
		'key'  : 'F9',
		'code' : Ext.EventObject.F9,
		'stop' : true,
		'cmd'  : 'ag-command-menu-image-move-focus-center'
	},{
		'order': 3,
		'key'  : 'F10',
		'code' : Ext.EventObject.F10,
		'stop' : true,
		'cmd'  : 'ag-command-menu-image-move-focus-zoom'
	},{
		'order': 4,
		'key'  : 'UP',
		'code' : Ext.EventObject.UP,
		'shift': true,
		'stop' : true,
		'cmd'  : 'ag-command-menu-image-move-up'
	},{
		'order': 5,
		'key'  : 'DOWN',
		'code' : Ext.EventObject.DOWN,
		'shift': true,
		'stop' : true,
		'cmd'  : 'ag-command-menu-image-move-down'
	},{
		'order': 6,
		'key'  : 'LEFT',
		'code' : Ext.EventObject.LEFT,
		'shift': true,
		'stop' : true,
		'cmd'  : 'ag-command-menu-image-move-left'
	},{
		'order': 7,
		'key'  : 'RIGHT',
		'code' : Ext.EventObject.RIGHT,
		'shift': true,
		'stop' : true,
		'cmd'  : 'ag-command-menu-image-move-right'
	},{
		'order': 8,
		'key'  : 'UP',
		'code' : Ext.EventObject.UP,
		'ctrl' : true,
		'stop' : true,
		'cmd'  : 'ag-command-menu-image-rotation-up'
	},{
		'order': 9,
		'key'  : 'DOWN',
		'code' : Ext.EventObject.DOWN,
		'ctrl' : true,
		'stop' : true,
		'cmd'  : 'ag-command-menu-image-rotation-down'
	},{
		'order': 10,
		'key'  : 'LEFT',
		'code' : Ext.EventObject.LEFT,
		'ctrl' : true,
		'stop' : true,
		'cmd'  : 'ag-command-menu-image-rotation-left'
	},{
		'order': 11,
		'key'  : 'RIGHT',
		'code' : Ext.EventObject.RIGHT,
		'ctrl' : true,
		'stop' : true,
		'cmd'  : 'ag-command-menu-image-rotation-right'
	},{
		'order': 12,
		'key'  : 'UP',
		'code' : Ext.EventObject.UP,
		'alt'  : true,
		'stop' : true,
		'cmd'  : 'ag-command-menu-image-zoom-up'
	},{
		'order': 13,
		'key'  : 'DOWN',
		'code' : Ext.EventObject.DOWN,
		'alt'  : true,
		'stop' : true,
		'cmd'  : 'ag-command-menu-image-zoom-down'
	}];
	for(var i=0;i<glb_us_keymap.length;i++){
		glb_us_keymap[i].order = i+1;
	}
}

var ag_parts_store;
var ag_param_store_fields = ['version', 'method', 'viewpoint', 'rotate_h', 'rotate_v', 'image_w', 'image_h', 'bg_rgb', 'bg_transparent', 'autoscalar_f', 'scalar_max', 'scalar_min', 'colorbar_f', 'heatmap_f', 'drawsort_f', 'mov_len', 'mov_fps', 'zoom', 'move_x', 'move_y', 'move_z', 'clip_type', 'clip_depth', 'clip_paramA', 'clip_paramB', 'clip_paramC', 'clip_paramD', 'clip_method', 'clipped_cameraX', 'clipped_cameraY', 'clipped_cameraZ', 'clipped_targetX', 'clipped_targetY', 'clipped_targetZ', 'clipped_upVecX', 'clipped_upVecY', 'clipped_upVecZ', 'grid', 'grid_len', 'grid_color', 'color_rgb', 'coord', 'point_color_rgb', 'point_label', 'point_desc', 'point_pin_line', 'point_point_line', 'point_sphere'];
var ag_param_store_data = [
	'09011601',	// version
	'I',				// method
	'C',				// viewpoint
	0,					// rotate_h
	0,					// rotate_v
	400,				// image_w
	400,				// image_h
	'FFFFFF',		// bg_rgb
	NaN,				// bg_transparent
	'1',				// autoscalar_f
	NaN,				// scalar_max
	NaN,				// scalar_min
	'0',				// colorbar_f
	'0',				// heatmap_f
	'0',				// drawsort_f
	60,					// mov_len
	60,					// mov_fps
	0,					// zoom
	0,					// move_x
	0,					// move_y
	0,					// move_z
	'N',				// clip_type
	NaN,				// clip_depth
	NaN,				// clip_paramA
	NaN,				// clip_paramB
	NaN,				// clip_paramC
	NaN,				// clip_paramD
	'NS',				// clip_method
	0,					// clipped_cameraX
	0,					// clipped_cameraY
	0,					// clipped_cameraZ
	0,					// clipped_targetX
	0,					// clipped_targetY
	0,					// clipped_targetZ
	0,					// clipped_upVecX
	0,					// clipped_upVecY
	0,					// clipped_upVecZ
	'0',				// grid
	10,					// grid_len
	'008000',		// grid_color
	'$DEF_COLOR_VAL',		// color_rgb
	'bp3d',			// coordinate_system
	'$DEF_COLOR_POINT_VAL',		// point_color_rgb
	'FMA',			// point_label
	1,					// point_desc
	0,					// point_pin_line
	0,					// point_point_line
	'SM'				//point_sphere
];
var ag_param_store = new Ext.data.SimpleStore ({
	fields : ag_param_store_fields,
	data : [ag_param_store_data]
});
var anatomoImgDrag = false;
var anatomoImgDragStartX = 0;
var anatomoImgDragStartY = 0;
var anatomoPickMode = false;
var anatomoPointMode = false;
var anatomoImgEvent = false;
var anatomoMoveMode = false;
var anatomoClipDepthMode = false;
var anatomoDragModeMove = false;
var anatomoUpdateZoomValue = false;
var anatomoUpdateClipValue = false;

var DEF_ZOOM_MAX = 100;

var YRangeFromServer = null;
var glb_rotateH = 0;
var glb_rotateV = 0;
var glb_zoom_slider = 1;
var glb_zoom_timer = null;
var glb_zoom_xy = null;
var glb_zoom_delta = 0;
var glb_mousedown_timer = null;
var glb_mousedown_toggle = false;

//Pick時にパーツのＩＤを設定される
var glb_point_f_id = null;
var glb_point_color = 'FF0000';
var glb_point_pallet_index = null;
var glb_point_transactionId = null;

function remove_point_f_id(store,record,index){
//	if(record.get('f_id')==glb_point_f_id || store.getCount()==0) clear_point_f_id();
	clear_point_f_id();
}
function set_point_f_id(f_id){
	if(Ext.isEmpty(f_id)){
		clear_point_f_id();
	}else{
		glb_point_f_id = f_id;
		ag_parts_gridpanel.getStore().on('update',remove_point_f_id);
		ag_parts_gridpanel.getStore().on('remove',remove_point_f_id);
	}
}
function get_point_f_id(){
	return glb_point_f_id;
}
function clear_point_f_id(){
	if(glb_point_f_id){
		glb_point_f_id = null;
		_loadAnatomo(makeAnatomoPrm(),true);
	}
	ag_parts_gridpanel.getStore().un('update',remove_point_f_id);
	ag_parts_gridpanel.getStore().un('remove',remove_point_f_id);
}


function set_point_color(color){
	glb_point_color = color;
}
function get_point_color(){
	return glb_point_color;
}

var init_bp3d_params = {};
//var init_bp3d_md_id;
//var init_bp3d_mv_id;
//var init_bp3d_mr_id;

var init_tree_group;
var init_bp3d_version;

//PIN関連の初期値
var init_anatomo_pin_number_draw = true;
//var init_anatomo_pin_description_draw = false;
var init_anatomo_pin_description_draw = true;
var init_anatomo_pin_description_line = 0;
//var init_anatomo_pin_shape = 'SC';
var init_anatomo_pin_shape = 'PL';

var init_anatomography_image_comment_draw = false;
var init_anatomography_image_comment_title = '';
var init_anatomography_image_comment_legend = '';
var init_anatomography_image_comment_author = '';

//_dump("init_tree_group=["+init_tree_group+"]");
//_dump("init_bp3d_version=["+init_bp3d_version+"]");

var _glb_no_clip = false;

var glb_anatomo_image_url = '';
var glb_anatomo_image_still = '';
var glb_anatomo_image_rotate = '';
var glb_anatomo_editor_url = '';
//var glb_anatomo_embedded_url = '';

var glb_transactionId = null;
var glb_time = null;

var m_ag = {
	initCameraPos: new AGVec3d(2.7979888916016167, -998.4280435445771, 809.7306805551052),
	cameraPos: new AGVec3d(2.7979888916016167, -998.4280435445771, 809.7306805551052),
	initTargetPos: new AGVec3d(2.7979888916015625, -110.37168800830841, 809.7306805551052),
	targetPos: new AGVec3d(2.7979888916015625, -110.37168800830841, 809.7306805551052),
	initUpVec: new AGVec3d(0, 0, 1),
	upVec: new AGVec3d(0, 0, 1),
	initDistance: 0,
	distance: 0,
	initLongitude: 0,
	longitude: 0,
	initLatitude: 0,
	latitude: 0,
	orthoYRange: 1800,
	initOrthoYRange: 1800,
	nearClip: 1,
	farClip: 10000,
	epsilon: 0.0000001,
	PI: 3.141592653589793238462643383279,
	Camera_YRange_Min: 1.0
};


var  timeoutAnatomoID = null;
function stopUpdateAnatomo(){
	if(timeoutAnatomoID) clearTimeout(timeoutAnatomoID);
	timeoutAnatomoID=null;
}

function updateAnatomo () {
//	console.log("updateAnatomo()");
	if(Ext.isEmpty(gParams.tp_md) || gParams.tp_md != 1){
		var contentsPanel = Ext.getCmp("contents-tab-panel");
		if (!contentsPanel) {
			return;
		}
		var activePanel;
		if(contentsPanel.getXType()=='tabpanel'){
			activePanel = contentsPanel.getActiveTab();
		}else if(contentsPanel.getXType()=='panel'){
			activePanel = contentsPanel.getLayout().activeItem;
		}
		if (!activePanel || !activePanel.id || (activePanel.id != "contents-tab-anatomography-panel")) {
			return;
		}
	}
	stopUpdateAnatomo();
	timeoutAnatomoID = setTimeout(function(){ _updateAnatomo();stopUpdateAnatomo(); },100);
}

var  _timeoutAnatomoID = null;

function _loadAnatomo (params,loadMask) {
//	console.log("_loadAnatomo()");
	if(loadMask){
		try{
			var comp = Ext.getCmp('anatomography-image');
			if(Ext.isEmpty(comp.loadMask)) comp.loadMask = new Ext.LoadMask(comp.body,{removeMask:false,  msg:'REDRAWING...'});
			comp.loadMask.show();
		}catch(e){_dump(e);}
	}

	var jsonStr = null;
	try{
		jsonStr = ag_extensions.toJSON.URI2JSON(params,{
			toString:true,
			mapPin:false,
			callback:undefined
		});
	}catch(e){jsonStr = null;}

	glb_time = (new Date()).getTime();

	var img = Ext.getDom('ag_img');

	var href = '';
	if(location.href.match(/^(.+\\/)/)){
		href = RegExp.\$1;
	}
	href += cgipath.image + "?" + (jsonStr ? encodeURIComponent(jsonStr) : params);
	if(href.length<=2083){
		img.src = cgipath.image+"?" + (jsonStr ? encodeURIComponent(jsonStr) : params);
	}else{
		var params_obj = Ext.urlDecode(params);
		if(!Ext.isEmpty(glb_transactionId)){
//			console.log("_loadAnatomo():abort()");
//			console.log(glb_transactionId);
//			console.log("Ext.Ajax.abort():["+Ext.Ajax.isLoading(glb_transactionId)+"]");
			if(Ext.Ajax.isLoading(glb_transactionId)) Ext.Ajax.abort(glb_transactionId);
		}
		glb_transactionId = Ext.Ajax.request({
			url     : cgipath.image,
			method  : 'POST',
			params  : jsonStr ? jsonStr : params,
			success : function(conn,response,options){
				glb_transactionId = null;
				try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
				try{
					var src;
					if(results && results.data){
						if(params_obj.dt != results.dt) return;
						src = results.data;
					}else{
						src = conn.responseText;
					}
					if(src && src != img.src){
						img.src = src;
					}else{
						load_ag_img();
					}
				}catch(e){
					alert(e);
				}
//				console.log("_loadAnatomo():success()");
			},
			failure : function(conn,response,options){
				glb_transactionId = null;
				try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
				var msg = '[';
				if(results && results.msg){
					msg += results.msg+' ]';
				}else{
					msg += conn.status+" "+conn.statusText+' ]';
				}
				var rotateAuto = false;
				try{rotateAuto = Ext.getCmp('ag-command-image-controls-rotateAuto').getValue();}catch(e){}
				if(conn.status==400) img.src = Ext.BLANK_IMAGE_URL;
//				console.log("_loadAnatomo():failure():"+msg);
//				console.log(conn);
//				console.log(response);
//				console.log(options);
				Ext.Msg.show({
					title:' ',
					buttons: Ext.Msg.OK,
					closable: false,
					icon: Ext.Msg.ERROR,
					modal : true,
					msg : msg
				});
			},
			callback : function(options,success,response){
//				console.log("_loadAnatomo():callback()");
//				console.log(options);
//				console.log(success);
//				console.log(response);
			}
		});
//		console.log("_loadAnatomo():exec()");
//		console.log(glb_transactionId);
	}
}

function setImageTransformOrigin(aOrigin){
//_dump("setImageTransformOrigin():["+aOrigin+"]");
HTML
if($useImageTransform eq 'true'){
	print <<HTML;
	if(Ext.isGecko){

		var img_org = Ext.getDom('ag_img');
		var img = Ext.getDom('ag_img_dummy');
		if(!img && img_org){
			img = img_org.ownerDocument.createElement('img');
			img.setAttribute('id','ag_img_dummy');
			img.style.position = 'absolute';
			img.style.display = 'none';
			img_org.parentNode.appendChild(img);
		}

		if(img){
			img.style.left = '0px';
			img.style.top = '0px';
			img.style.width = img_org.offsetWidth + 'px';
			img.style.height = img_org.offsetHeight + 'px';
			img.src = img_org.src;
			img.style.opacity = '1.0';

			img.style.MozTransformOrigin = aOrigin;
			img.style.webkitTransformOrigin = aOrigin;
			img.style.transformOrigin = aOrigin;

		}

	}else if(Ext.isChrome || Ext.isSafari){
		var img = Ext.getDom('ag_img');
		if(img){
			img.style.webkitTransformOrigin = aOrigin;
			img.style.transformOrigin = aOrigin;
		}
	}
HTML
}
print <<HTML;
}

function setImageTransform(aTransform,aDisplay){
//_dump("setImageTransform():["+aTransform+"]["+aDisplay+"]");
HTML
if($useImageTransform eq 'true'){
	print <<HTML;
	if(Ext.isGecko){

		if(!aDisplay) aDisplay = false;
		var img_org = Ext.getDom('ag_img');
		var img = Ext.getDom('ag_img_dummy');
		if(!img && img_org){
			img = img_org.ownerDocument.createElement('img');
			img.setAttribute('id','ag_img_dummy');
			img.style.position = 'absolute';
			img_org.parentNode.appendChild(img);
		}

		if(img){
			img.style.left = '0px';
			img.style.top = '0px';
			img.style.width = img_org.offsetWidth + 'px';
			img.style.height = img_org.offsetHeight + 'px';
			img.src = img_org.src;
			img.style.opacity = '1.0';
			img.style.display = aDisplay ? '' : 'none';

			img.style.MozTransform = aTransform;
			img.style.webkitTransform = aTransform;
			img.style.transform = aTransform;

			if(img_org){
				if(aDisplay){
					img_org.style.opacity = '0.0';
				}else{
					img_org.style.opacity = '1.0';
				}
			}
		}

	}else if(Ext.isChrome || Ext.isSafari){
		var img = Ext.getDom('ag_img');
		if(img){
			img.style.webkitTransform = aTransform;
			img.style.transform = aTransform;
		}
	}
HTML
}
print <<HTML;
}

function anatomoImgMouseWheel(e,t) {
//_dump("anatomoImgMouseWheel():"+t.id);
	if(!t || (t.id!='ag_img' && t.id!='ag_img_dummy')) return;
	try {
		e.stopPropagation();
		e.preventDefault();
	} catch (ex) {
		e.returnValue = false;
		e.cancelBubble = true;
	}


	try{
		var delta = e.getWheelDelta();
		if(delta){
			if(anatomoClipDepthMode){
				var slider = Ext.getCmp('anatomo-clip-slider');
				if(slider && slider.rendered) slider.setValue(slider.getValue() + delta);
			}else{
				var slider = Ext.getCmp('zoom-slider');
				if(slider && slider.rendered){
					glb_zoom_delta += delta;
					if(Math.abs(Math.round(glb_zoom_delta))>=1){

						var slider_value = slider.getValue();
						if(slider_value+glb_zoom_delta>=0 && slider_value+glb_zoom_delta<DEF_ZOOM_MAX){
							var val;
							if(Ext.isGecko){
								val = (Math.round(glb_zoom_delta) / 10);
								if(val>=0){
									val += (val*0.5);
								}else{
									val += (val*0.3);
								}
								val += 1;
							}else if(Ext.isChrome || Ext.isSafari){
								val = (Math.round(glb_zoom_delta) / 10);
								val += 1;
//_dump("anatomoImgMouseWheel():val=["+val+"]");
							}
							var elemImg = Ext.get('ag_img');
							var xyImg = elemImg.getXY();
							var sizeImg = elemImg.getSize();
							var mouseX = e.xy[0] - glbImgXY[0];
							var mouseY = e.xy[1] - glbImgXY[1];

//_dump("anatomoImgMouseWheel():e.xy=["+e.xy[0]+"]["+e.xy[1]+"]["+xyImg[0]+"]["+xyImg[1]+"]["+elemImg.getLeft()+"]["+elemImg.getLeft(true)+"]["+sizeImg.width+"]["+sizeImg.height+"]");

							setImageTransformOrigin(mouseX+'px '+mouseY+'px');
							setImageTransform('scale('+val+')',true);

//_dump("anatomoImgMouseWheel():slider.getValue()=["+slider.getValue()+"]");
HTML
if($useImageTransform eq 'true'){
	print <<HTML;
							if(glb_zoom_timer) clearTimeout(glb_zoom_timer);
							glb_zoom_timer = setTimeout(function(){
								glb_zoom_xy = [];
								glb_zoom_xy[0] = e.xy[0];
								glb_zoom_xy[1] = e.xy[1];
								slider.setValue(slider.getValue() + glb_zoom_delta);
								glb_zoom_delta = 0;
								glb_zoom_timer = null;
							},500);
HTML
}else{
	print <<HTML;
							glb_zoom_xy = [];
							glb_zoom_xy[0] = e.xy[0];
							glb_zoom_xy[1] = e.xy[1];
							slider.setValue(slider.getValue() + glb_zoom_delta);
							glb_zoom_delta = 0;
HTML
}
print <<HTML;
						}
					}
				}else{
					if(Math.round(glb_zoom_slider + glb_zoom_delta + delta)>=0){
						glb_zoom_delta += delta;
						glb_zoom_slider = glb_zoom_slider + glb_zoom_delta;

						glb_zoom_xy = [];
						glb_zoom_xy[0] = e.xy[0];
						glb_zoom_xy[1] = e.xy[1];

						if(glb_zoom_xy){
							var elemImg = Ext.get('ag_img');
							var xyImg = elemImg.getXY();

							var mouseX = glb_zoom_xy[0] - xyImg[0];
							var mouseY = glb_zoom_xy[1] - xyImg[1];

							var centerX = parseInt((ag_param_store.getAt(0).data.image_w /2) -  mouseX);
							var centerY = parseInt((ag_param_store.getAt(0).data.image_h /2) -  mouseY);

							setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);
							moveTargetByMouseForOrtho(ag_param_store.getAt(0).data.image_h, centerX / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)), centerY / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)));
						}

						var prm_record = ag_param_store.getAt(0);
						prm_record.beginEdit();
						prm_record.set('zoom', glb_zoom_slider / 5);
						prm_record.endEdit();
						prm_record.commit();

						if(glb_zoom_xy){

							var elemImg = Ext.get('ag_img');
							var xyImg = elemImg.getXY();

							var mouseX = glb_zoom_xy[0] - xyImg[0];
							var mouseY = glb_zoom_xy[1] - xyImg[1];

							var moveX = parseInt(mouseX - (ag_param_store.getAt(0).data.image_w /2));
							var moveY = parseInt(mouseY - (ag_param_store.getAt(0).data.image_h /2));

							setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);
							moveTargetByMouseForOrtho(ag_param_store.getAt(0).data.image_h, moveX / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)), moveY / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)));

						}
						updateAnatomo();
						updateClipImage();

						if(glb_zoom_xy) glb_zoom_xy = null;
						glb_zoom_delta = 0;
					}
				}
			}
		}
		e.stopEvent();
	}catch(e){
		_dump("anatomoImgMouseWheel():"+e);
	}
}

function anatomoIsPickMode () {
	return anatomoPickMode;
}

function anatomoIsPointMode () {
	return anatomoPointMode;
}

function anatomoImgMouseOut(e) {
}

function anatomoImgMouseDown(e,t) {
//_dump("anatomoImgMouseDown():"+t.id);
_dump("anatomoImgMouseDown():e.button=["+e.button+"]:e.which=["+e.which+"]:e.ctrlKey=["+e.ctrlKey+"]");
	if(!t || t.id!='ag_img') return;
//	if(e.button == 2) return;
	if(e.button != 0) return;
	try {
		e.stopPropagation();
		e.preventDefault();
	} catch (ex) {
		e.returnValue = false;
		e.cancelBubble = true;
	}
	anatomoImgDrag = true;
	anatomoImgDragStartX = e.xy[0];
	anatomoImgDragStartY = e.xy[1];
	if(e.ctrlKey || e.button == 1){
		anatomoMoveMode = true;
	} else {
		anatomoMoveMode = false;
	}
_dump("anatomoImgMouseDown():anatomoImgDrag=["+anatomoImgDrag+"]:anatomoMoveMode=["+anatomoMoveMode+"]");

	if(anatomoImgDrag){
		var rotateAuto = false;
		try{rotateAuto = Ext.getCmp('ag-command-image-controls-rotateAuto').getValue();}catch(e){}
		if(rotateAuto){
HTML
if($modifyAxisOfRotation ne 'true'){
	print <<HTML;
			agRotateAuto.rotate(false);
			agRotateAuto.imgX = 0;
			agRotateAuto.imgY = 0;
			if (e.browserEvent.offsetX) {
				// IE
				agRotateAuto.imgX = e.browserEvent.offsetX;
				agRotateAuto.imgY = e.browserEvent.offsetY;
			} else {
				// FF
				var img = Ext.getDom('ag_img');
				agRotateAuto.imgX = e.browserEvent.layerX - img.offsetLeft;
				agRotateAuto.imgY = e.browserEvent.layerY - img.offsetTop;
			}
HTML
}
print <<HTML;
		}
	}

	if(anatomoDragModeMove){
		document.body.style.cursor = 'move';
	}else{
		document.body.style.cursor = 'default';
	}
	if(glb_mousedown_timer) clearTimeout(glb_mousedown_timer);
	if(e.button == 0){
		glb_mousedown_timer = setTimeout(function(){
			glb_mousedown_timer = null;

			if(anatomoDragModeMove){
				document.body.style.cursor = 'move';
			}else{
				document.body.style.cursor = 'default';
			}
			glb_mousedown_toggle = true;

			var target = (anatomoDragModeMove?Ext.get('ag-command-btn-rotate'):Ext.get('ag-command-btn-move'));
			if(!target) return;
			ag_command_toggle_exec(target);
//		},400);
		},1000); //2011-09-07
	}
}

function anatomoImgMouseMove(e) {

	if(glb_mousedown_timer){
		clearTimeout(glb_mousedown_timer);
		glb_mousedown_timer = null;
	}

	if (anatomoImgDrag) {
		try {
			e.stopPropagation();
			e.preventDefault();
		} catch (ex) {
			e.returnValue = false;
			e.cancelBubble = true;
		}
HTML
if($modifyAxisOfRotation eq 'true'){
	print <<HTML;
		var rotateAuto = false;
		try{rotateAuto = Ext.getCmp('ag-command-image-controls-rotateAuto').getValue();}catch(e){}
		if(rotateAuto) return;
HTML
}
print <<HTML;
		var dX = e.xy[0] - anatomoImgDragStartX;
		var dY = e.xy[1] - anatomoImgDragStartY;
		if(anatomoMoveMode || anatomoDragModeMove) {
			document.body.style.cursor = 'move';
			var rotImgDiv = Ext.getDom("rotImgDiv");
			rotImgDiv.style.visibility = "hidden";

			setImageTransform('scale(1) translate(' + dX + 'px, ' + dY + 'px)',true);

		}else{

			var prm_record = ag_param_store.getAt(0);
			deg = (isNaN(prm_record.data.rotate_h))?0:prm_record.data.rotate_h;


			document.body.style.cursor = 'default';
			// rotateH
			var degH = Math.round(getRotateHorizontalValue()/15)*15;
			degH = degH - 15 * Math.floor(dX / 20);
			while (degH >= 360) {
				degH = degH - 360;
			}
			while (degH < 0) {
				degH = degH + 360;
			}
			// rotateV
			var degV = Math.round(getRotateVerticalValue()/15)*15;
			degV = degV + 15 * Math.floor(dY / 20);
			while (degV >= 360) {
				degV = degV - 360;
			}
			while (degV < 0) {
				degV = degV + 360;
			}

			degH = degH.toString();
			degV = degV.toString();

			var rotateHSpan = Ext.getDom("rotImgDivRotateH");
			if(rotateHSpan){
				rotateHSpan.innerHTML = "H:"+degH;
			}

			var rotateVSpan = Ext.getDom("rotImgDivRotateV");
			if(rotateVSpan){
				rotateVSpan.innerHTML = "V:"+degV;
			}

			var rotImgDiv = Ext.getDom("rotImgDiv");
			rotImgDiv.style.visibility = "visible";
			rotImgDiv.style.left = (parseInt(e.xy[0]) + 10) + "px";
			rotImgDiv.style.top = (parseInt(e.xy[1]) + 10) + "px";
			rotImgDiv.style.backgroundPosition = degH /15 * (-80) + "px " + degV / 15 * (-80) + "px";
		}
	}
}

function anatomoImgMouseUp(e) {
	if(glb_mousedown_timer){
		clearTimeout(glb_mousedown_timer);
		glb_mousedown_timer = null;
	}

	document.body.style.cursor = 'default';

	var dX = e.xy[0] - anatomoImgDragStartX;
	var dY = e.xy[1] - anatomoImgDragStartY;

	var bp3d_home_group_btn_disabled = true;
	try{bp3d_home_group_btn_disabled = Ext.getCmp('bp3d-home-group-btn').disabled;}catch(e){}

	if(bp3d_home_group_btn_disabled && anatomoIsPickMode() && !dX && !dY){
		var imgX = 0;
		var imgY = 0;
		if (e.browserEvent.offsetX) {
			// IE
			imgX = e.browserEvent.offsetX;
			imgY = e.browserEvent.offsetY;
		} else {
			// FF
			var img = Ext.getDom('ag_img');
			imgX = e.browserEvent.layerX - img.offsetLeft;
			imgY = e.browserEvent.layerY - img.offsetTop;
		}
		try {
			Ext.getCmp('anatomography-pin-grid-panel').loadMask.show();
			var params = Ext.urlDecode(makeAnatomoPrm(null,1),true);
			params.px = imgX;
			params.py = imgY;

			var jsonStr = null;
			try{
				jsonStr = ag_extensions.toJSON.URI2JSON(params,{
					toString:true,
					mapPin:false,
					callback:undefined
				});
			}catch(e){jsonStr = null;}

			var urlStr = cgipath.pick;
			Ext.Ajax.request({
				url     : urlStr,
				method  : 'POST',
				params  : jsonStr ? jsonStr : params,
				success : function (response, options) {
					try{
						var pickDataAry = [];
						var obj = Ext.util.JSON.decode(response.responseText);
//_dump(cgipath.pick+":success():obj=["+(typeof obj)+"]");
						pickDataAry = obj.Pin;
//_dump(cgipath.pick+":success():pickDataAry=["+(typeof pickDataAry)+"]");
						var pickDepth = parseInt(Ext.getCmp('anatomo_comment_pick_depth').getValue());
						var pin_no = ag_comment_store.getCount();
						var newRecord = Ext.data.Record.create(ag_comment_store_fields);
						var addrecs = [];
						for (var i=0;i<pickDataAry.length;i++){
							if(i == pickDepth) break;
							var pickData = pickDataAry[i];
//_dump(cgipath.pick+":success():pickData.PinPartID=["+(typeof pickData.PinPartID)+"]["+(pickData.PinPartID)+"]");
							if(pickData.PinPartID.match(/^clipPlaneRect_(.+)\$/)) pickData.PinPartID = RegExp.\$1;
							var addrec = new newRecord({
								no:   ++pin_no,
								oid:   pickData.PinPartID,
								organ: pickData.PinPartName,
								x3d:   pickData.PinX,
								y3d:   pickData.PinY,
								z3d:   pickData.PinZ,
								avx3d: pickData.PinArrowVectorX,
								avy3d: pickData.PinArrowVectorY,
								avz3d: pickData.PinArrowVectorZ,
								uvx3d: pickData.PinUpVectorX,
								uvy3d: pickData.PinUpVectorY,
								uvz3d: pickData.PinUpVectorZ,
								color: '0000FF',
								comment:'',
								coord: pickData.PinCoordinateSystemName
							});
/*
							addrec.beginEdit();
							addrec.set("no",   ++pin_no);
							addrec.set("oid",   pickData.PinPartID);
							addrec.set("organ", '');
							addrec.set("x3d",   pickData.PinX);
							addrec.set("y3d",   pickData.PinY);
							addrec.set("z3d",   pickData.PinZ);
							addrec.set("avx3d", pickData.PinArrowVectorX);
							addrec.set("avy3d", pickData.PinArrowVectorY);
							addrec.set("avz3d", pickData.PinArrowVectorZ);
							addrec.set("uvx3d", pickData.PinUpVectorX);
							addrec.set("uvy3d", pickData.PinUpVectorY);
							addrec.set("uvz3d", pickData.PinUpVectorZ);
							addrec.set("color", '0000FF');
							addrec.set("comment",'');
							addrec.set("coord", pickData.PinCoordinateSystemName);
							addrec.commit(true);
							addrec.endEdit();
*/
							addrecs.push(addrec);

						}
						if(addrecs.length>0){
							ag_comment_store.add(addrecs);
						}else{
							if(window.ag_extensions && window.ag_extensions.pick_point) window.ag_extensions.pick_point.hide();
						}

					}catch(e){_dump(e);}
					Ext.getCmp('anatomography-pin-grid-panel').loadMask.hide();
				},
				failure: function (response, options) {
					alert(cgipath.pick+":failure():"+response.statusText);
					Ext.getCmp('anatomography-pin-grid-panel').loadMask.hide();
				}
			});
		} catch (ex) {
			alert(ex.toString());
		}
	}

	//Pick or Pallet タブがアクティブの場合
	if(
		!anatomoIsPickMode() && !dX && !dY && Ext.getCmp('anatomo_comment_point_button') &&
		ag_comment_tabpanel && ag_comment_tabpanel.rendered &&

		(
			(
				window.ag_extensions &&
				window.ag_extensions.pallet_element &&
				(ag_comment_tabpanel.getActiveTab().id == window.ag_extensions.pallet_element.getId() || ag_comment_tabpanel.getActiveTab().id == 'anatomography-point-grid-panel' || ag_comment_tabpanel.getActiveTab().id == 'ag-parts-gridpanel')
			)
			||
			(
				(!window.ag_extensions || !window.ag_extensions.pallet_element) &&
				(ag_comment_tabpanel.getActiveTab().id == 'anatomography-point-grid-panel' || ag_comment_tabpanel.getActiveTab().id == 'ag-parts-gridpanel')
			)
		)
	) {


		if(ag_comment_tabpanel.getActiveTab().id == 'ag-parts-gridpanel'){
			if(window.ag_extensions && window.ag_extensions.pallet_element){
				window.ag_extensions.pallet_element.setActiveTab();
			}else{
				ag_comment_tabpanel.setActiveTab('anatomography-point-grid-panel');
			}
		}
		Ext.getCmp('anatomo_comment_point_button').toggle(false);
		Ext.getCmp('anatomo_comment_point_button').disable();
		var imgX = 0;
		var imgY = 0;
		if (e.browserEvent.offsetX) {
			// IE
			imgX = e.browserEvent.offsetX;
			imgY = e.browserEvent.offsetY;
		} else {
			// FF
			var img = Ext.getDom('ag_img');
			imgX = e.browserEvent.layerX - img.offsetLeft;
			imgY = e.browserEvent.layerY - img.offsetTop;
		}
		try {
			if(window.ag_extensions && window.ag_extensions.pallet_element){
				if(ag_comment_tabpanel.getActiveTab().id == window.ag_extensions.pallet_element.getId()) window.ag_extensions.pallet_element.showLoadMask();
			}
			if(ag_comment_tabpanel.getActiveTab().id == 'anatomography-point-grid-panel') Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.show();

			Ext.getCmp('ag-parts-gridpanel').loadMask.show();
			var urlStr = cgipath.point;
			var params = Ext.urlDecode(makeAnatomoPrm(null,1),true);
			params.px = imgX;
			params.py = imgY;

			var jsonStr = null;
			try{
				jsonStr = ag_extensions.toJSON.URI2JSON(params,{
					toString:true,
					mapPin:false,
					callback:undefined
				});
			}catch(e){jsonStr = null;}

			if(glb_point_transactionId){
				Ext.Ajax.abort(glb_point_transactionId);
			}

			glb_point_transactionId = Ext.Ajax.request({
				url    : urlStr,
				method : 'POST',
				params : jsonStr ? jsonStr : params,
				callback: function(options,success,response){
					glb_point_transactionId = null;
				},
				success: function (response, options) {
//					_dump(cgipath.point+":success():"+response.responseText);
//					_dump(cgipath.point+":success():"+ag_comment_tabpanel.getActiveTab().id);
					try{var pointData = Ext.util.JSON.decode(response.responseText);}catch(e){_dump(e);}
					if(Ext.isEmpty(pointData) || Ext.isEmpty(pointData.id)){
						Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.hide();
						Ext.getCmp('ag-parts-gridpanel').loadMask.hide();
						clear_point_f_id();
						var loader = Ext.getCmp('anatomography-point-editorgrid-panel').getStore();
						loader.removeAll();
						loader.baseParams = {};
						var elem = Ext.getDom('ag-point-grid-content-route');
						if(elem) elem.innerHTML = '&nbsp;';

						if(window.ag_extensions){
							if(window.ag_extensions.pallet_element){
								window.ag_extensions.pallet_element.hideLoadMask();
								window.ag_extensions.pallet_element.selectPointElement(null);
							}
							if(window.ag_extensions.pick_point) window.ag_extensions.pick_point.hide();
						}
						return;
					}

					var f_id = pointData.id;
					try{
						var tx = parseInt(parseFloat(pointData.worldPosX)*1000)/1000;
						var ty = parseInt(parseFloat(pointData.worldPosY)*1000)/1000;
						var tz = parseInt(parseFloat(pointData.worldPosZ)*1000)/1000;

						var txCmp = Ext.getCmp('anatomography-point-grid-bbar-tx-text');
						var tyCmp = Ext.getCmp('anatomography-point-grid-bbar-ty-text');
						var tzCmp = Ext.getCmp('anatomography-point-grid-bbar-tz-text');
						var dxCmp = Ext.getCmp('ag-point-grid-footer-content-distance-x-text');
						var dyCmp = Ext.getCmp('ag-point-grid-footer-content-distance-y-text');
						var dzCmp = Ext.getCmp('ag-point-grid-footer-content-distance-z-text');
						var distanceCmp = Ext.getCmp('anatomography-point-grid-bbar-distance-text');

						var txP = txCmp.getValue();txP=(txP==''?'':parseFloat(txP));
						var tyP = tyCmp.getValue();tyP=(tyP==''?0:parseFloat(tyP));
						var tzP = tzCmp.getValue();tzP=(txP==''?0:parseFloat(tzP));

						if(!isNaN(tx)){
							txCmp.setValue(tx);
							tyCmp.setValue(ty);
							tzCmp.setValue(tz);
						}

						if(!isNaN(tx) && txP != ''){
							dxCmp.setValue(parseInt(parseFloat(txP-tx)*1000)/1000);
							dyCmp.setValue(parseInt(parseFloat(tyP-ty)*1000)/1000);
							dzCmp.setValue(parseInt(parseFloat(tzP-tz)*1000)/1000);

							var distance = parseInt(Math.sqrt(Math.pow(tx-txP,2)+Math.pow(ty-tyP,2)+Math.pow(tz-tzP,2))*1000)/1000;
							distanceCmp.setValue(distance);
						}else{
							dxCmp.setValue('');
							dyCmp.setValue('');
							dzCmp.setValue('');
							distanceCmp.setValue('');
						}

					}catch(e){}

					if(f_id.match(/^clipPlaneRect_(.+)\$/)){
						f_id = RegExp.\$1;
					}else if(f_id != ""){

					}else{
						Ext.getCmp('anatomo_comment_point_button').enable();

						var loader = Ext.getCmp('anatomography-point-editorgrid-panel').getStore();
						loader.removeAll();
						loader.baseParams = {};
						var elem = Ext.getDom('ag-point-grid-content-route');
						if(elem) elem.innerHTML = '&nbsp;';
						Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.hide();
						Ext.getCmp('ag-parts-gridpanel').loadMask.hide();
						if(window.ag_extensions){
							if(window.ag_extensions.pallet_element){
								window.ag_extensions.pallet_element.hideLoadMask();
								window.ag_extensions.pallet_element.selectPointElement(null);
							}
							if(window.ag_extensions.pick_point) window.ag_extensions.pick_point.hide();
						}
						return;
					}

					if(window.ag_extensions && window.ag_extensions.pallet_element) window.ag_extensions.pallet_element.selectPointElement(f_id);
					if(get_point_f_id() == f_id){
						Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.hide();
						Ext.getCmp('ag-parts-gridpanel').loadMask.hide();
						if(window.ag_extensions){
							if(window.ag_extensions.pallet_element) window.ag_extensions.pallet_element.hideLoadMask();
							if(window.ag_extensions.pick_point) window.ag_extensions.pick_point.hide();
						}
						return;
					}
					var loader = Ext.getCmp('anatomography-point-editorgrid-panel').getStore();
					loader.removeAll();
					loader.baseParams = {};
					var elem = Ext.getDom('ag-point-grid-content-route');
					if(elem) elem.innerHTML = '&nbsp;';


HTML
if($usePickPartsSelect eq 'true'){
	print <<HTML;
					if(get_point_f_id() != f_id){
						set_point_f_id(f_id);
						var params = makeAnatomoPrm();
HTML
print <<HTML;
						_loadAnatomo(params,true);
					}
HTML
}
print <<HTML;
					if(ag_comment_tabpanel.getActiveTab().id == 'anatomography-point-grid-panel'){

						var point_loader = null;
						var pallet_loader = null;

						point_loader = anatomography_point_conventional_root_store;
						var toggle_partof = Ext.getCmp('anatomo_comment_point_toggle_partof');
						if(toggle_partof && toggle_partof.rendered) toggle_partof.toggle(true);

						var cmp = Ext.getCmp('anatomo-tree-type-combo');
						if(cmp && cmp.rendered){
							var type = cmp.getValue();
							if(toggle_partof.pressed){
								if(type == '4'){
									point_loader = anatomography_point_partof_store;
								}else if(type == '3'){
									point_loader = anatomography_point_isa_store;
								}else if(type == '1'){
									point_loader = anatomography_point_conventional_root_store;
								}
							}else if(Ext.getCmp('anatomo_comment_point_toggle_haspart').pressed){
								if(type == '4'){
									point_loader = anatomography_point_haspart_store;
								}else if(type == '3'){
									point_loader = anatomography_point_hasmember_store;
								}else if(type == '1'){
									point_loader = anatomography_point_conventional_child_store;
								}
							}
						}
						pallet_loader = anatomography_pallet_point_conventional_root_store;
						var cmp = Ext.getCmp('bp3d-tree-type-combo-ag');
						if(cmp && cmp.rendered){
							var type = cmp.getValue();
							if(type == '4'){
								pallet_loader = anatomography_pallet_point_partof_store;
							}else if(type == '3'){
								pallet_loader = anatomography_pallet_point_isa_store;
							}else if(type == '1'){
								pallet_loader = anatomography_pallet_point_conventional_root_store;
							}
						}
						if(point_loader || pallet_loader){
							if(point_loader){
								point_loader.baseParams = point_loader.baseParams || {};
								point_loader.baseParams.f_id = f_id;
								point_loader.load();
							}
							if(pallet_loader){
								pallet_loader.baseParams = pallet_loader.baseParams || {};
								pallet_loader.baseParams.f_id = f_id;
								pallet_loader.load();
							}
						}else{
							var loader = Ext.getCmp('anatomography-point-editorgrid-panel').getStore();
							loader.removeAll();
							loader.baseParams = {};
							var elem = Ext.getDom('ag-point-grid-content-route');
							if(elem) elem.innerHTML = '&nbsp;';
							Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.hide();
							Ext.getCmp('ag-parts-gridpanel').loadMask.hide();
							if(window.ag_extensions){
								if(window.ag_extensions.pallet_element) window.ag_extensions.pallet_element.hideLoadMask();
								if(window.ag_extensions.pick_point) window.ag_extensions.pick_point.hide();
							}
						}
					}else{
						Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.hide();
						Ext.getCmp('ag-parts-gridpanel').loadMask.hide();
						if(window.ag_extensions){
							if(window.ag_extensions.pallet_element) window.ag_extensions.pallet_element.hideLoadMask();
							if(window.ag_extensions.pick_point) window.ag_extensions.pick_point.hide();
						}
					}
					Ext.getCmp('anatomo_comment_point_button').enable();
				},
				failure: function (response, options) {
					try{alert(cgipath.point+":failure():"+response.status+":"+response.statusText);}catch(e){}
					Ext.getCmp('anatomo_comment_point_button').enable();
					Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.hide();
					Ext.getCmp('ag-parts-gridpanel').loadMask.hide();
					if(window.ag_extensions){
						if(window.ag_extensions.pallet_element) window.ag_extensions.pallet_element.hideLoadMask();
						if(window.ag_extensions.pick_point) window.ag_extensions.pick_point.hide();
					}
				}
			});
		} catch (ex) {
			alert(ex.toString());
			Ext.getCmp('anatomo_comment_point_button').enable();
		}
	}


	//Point Search タブがアクティブの場合
	if(
		!anatomoIsPickMode() && !dX && !dY && Ext.getCmp('anatomo_comment_point_button') &&
		ag_comment_tabpanel && ag_comment_tabpanel.rendered &&
		(ag_comment_tabpanel.getActiveTab().id == 'anatomography-point-search-panel')
	) {
		var imgX = 0;
		var imgY = 0;
		if (e.browserEvent.offsetX) {
			// IE
			imgX = e.browserEvent.offsetX;
			imgY = e.browserEvent.offsetY;
		} else {
			// FF
			var img = Ext.getDom('ag_img');
			imgX = e.browserEvent.layerX - img.offsetLeft;
			imgY = e.browserEvent.layerY - img.offsetTop;
		}
		point_search(imgX,imgY);
	}


//	_dump("anatomoImgMouseUp():anatomoImgDrag=["+anatomoImgDrag+"]");

	if(anatomoImgDrag){
		try {
			e.stopPropagation();
			e.preventDefault();
		} catch (ex) {
			e.returnValue = false;
			e.cancelBubble = true;
		}
		var rotImgDiv = Ext.getDom("rotImgDiv");
		rotImgDiv.style.visibility = "hidden";
		anatomoImgDrag = false;

//		_dump("anatomoImgMouseUp():dX=["+dX+"]");
//		_dump("anatomoImgMouseUp():dY=["+dY+"]");

		if(dX || dY){

//			_dump("anatomoImgMouseUp():anatomoMoveMode=["+anatomoMoveMode+"]");
//			_dump("anatomoImgMouseUp():anatomoDragModeMove=["+anatomoDragModeMove+"]");

			if(anatomoMoveMode || anatomoDragModeMove){

				// calc camera target
				setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);
				moveTargetByMouseForOrtho(ag_param_store.getAt(0).data.image_h, dX / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)), dY / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)));

			} else {


				var rotateAuto = false;
				try{rotateAuto = Ext.getCmp('ag-command-image-controls-rotateAuto').getValue();}catch(e){}
//				_dump("anatomoImgMouseUp():rotateAuto=["+rotateAuto+"]");
				if(rotateAuto){
HTML
if($modifyAxisOfRotation ne 'true'){
	print <<HTML;
					var px2 = 0;
					var py2 = 0;
					if (e.browserEvent.offsetX) {
						// IE
						px2 = e.browserEvent.offsetX;
						py2 = e.browserEvent.offsetY;
					} else {
						// FF
						var img = Ext.getDom('ag_img');
						px2 = e.browserEvent.layerX - img.offsetLeft;
						py2 = e.browserEvent.layerY - img.offsetTop;
					}



					var px1 = agRotateAuto.imgX;
					var py1 = agRotateAuto.imgY;
					var px2 = e.xy[0];
					var py2 = e.xy[1];

//					var urlStr = cgipath.calcRotAxis + '?' + makeAnatomoPrm();
					var urlStr = makeAnatomoPrm();
					urlStr += '&px1=' + px1 + '&py1=' +py1;
					urlStr += '&px2=' + px2 + '&py2=' +py2;

//					_dump("px=["+px1+"]["+py1+"]["+px2+"]["+py2+"]");

					Ext.Ajax.request({
						url     : cgipath.calcRotAxis,
						method  : 'POST',
						params  : urlStr,
						success : function (response, options) {
//							_dump(response.responseText);
							try{var rotAxis = Ext.util.JSON.decode(response.responseText);}catch(e){_dump(e);}
							if(!rotAxis) return;
							agRotateAuto.setRotAxis(rotAxis);

							var deg = calcRotateAxisDeg(new AGVec3d(rotAxis.rotAxisX,rotAxis.rotAxisY,rotAxis.rotAxisZ));
//							_dump("deg=["+deg.H+"]["+deg.V+"]");

							setTimeout(function(){ agRotateAuto.rotate(true); }, 0);
						},
						failure: function (response, options) {
							alert("calcRotAxis.cgi:failure():"+response.statusText);
						}
					});
HTML
}
print <<HTML;
				}else{

					// rotateH
					var deg = getRotateHorizontalValue();
					deg = deg - 15 * Math.floor(dX / 20);
					while (deg >= 360) {
						deg = deg - 360;
					}
					while (deg < 0) {
						deg = deg + 360;
					}
					setRotateHorizontalValue(deg);

					// rotateV
					var deg = getRotateVerticalValue();
					deg = deg + 15 * Math.floor(dY / 20);
					while (deg >= 360) {
						deg = deg - 360;
					}
					while (deg < 0) {
						deg = deg + 360;
					}
					setRotateVerticalValue(deg);

					if(Ext.isEmpty(gParams.tp_md) || gParams.tp_md != 1){
						if(updateRotateImg) updateRotateImg();
					}

					// calc camera target
					setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);
					addLongitude(-15 * Math.floor(dX / 20));
					addLatitude(15 * Math.floor(dY / 20));

				}

			}
			updateAnatomo();
		}
	}

	if(glb_mousedown_toggle){
		if(anatomoDragModeMove){
			ag_command_toggle_exec(Ext.get('ag-command-btn-rotate'));
		}else{
			ag_command_toggle_exec(Ext.get('ag-command-btn-move'));
		}
		document.body.style.cursor = 'default';
		glb_mousedown_toggle = false;
	}
	anatomoMoveMode = false;
}


function makeAnatomoOrganPrm(num,record,mode,aOpacity){
	var prm = "";

	if(get_point_f_id() && (Ext.isEmpty(mode) || mode!=2) && get_point_f_id() == record.data.f_id){
		prm = prm + "&ocl" + num + "=" + glb_point_color;
	}else{
		// color
		var colorstr = record.data.color.substr(1, 6);
		if(colorstr.length == 6) prm = prm + "&ocl" + num + "=" + colorstr;
	}

	// value
	if (isNaN(parseFloat(record.data.value))) {
	} else {
		prm = prm + "&osc" + num + "=" + parseFloat(record.data.value);
	}

	// Show
	if (record.data.exclude || (!Ext.isEmpty(aOpacity) && !isNaN(parseFloat(aOpacity)) && parseFloat(aOpacity) > record.data.opacity)) {
		prm = prm + "&osz" + num + "=H";
	}else if (record.data.zoom) {
		prm = prm + "&osz" + num + "=Z";
	}else{
		prm = prm + "&osz" + num + "=S";
	}
	// Opacity
//	if(record.data.opacity==0.1){
//		prm = prm + "&oop" + num + "=0.05";
//	}else{
		prm = prm + "&oop" + num + "=" + record.data.opacity;
//	}
	// representation
	if (record.data.representation == "surface") {
		prm = prm + "&orp" + num + "=S";
	} else if (record.data.representation == "wireframe") {
		prm = prm + "&orp" + num + "=W";
	} else if (record.data.representation == "points") {
		prm = prm + "&orp" + num + "=P";
	}

	//Organ Draw Child Point Flag
	prm = prm + "&odcp" + num + "=" + (record.data.point?1:0);

	return prm;
}



function makeAnatomoPrm(aMode,aOpacity){
	try{

	var prm = "";
	var prm_record = ag_param_store.getAt(0);

	// General Parameters
	var version = "09051901";
	prm = "av=" + version;
	if(!Ext.isEmpty(gParams.tp_md) && gParams.tp_md == 1){
		var size = Ext.getBody().getSize();
		prm = prm + "&iw=" + size.width;
		prm = prm + "&ih=" + size.height;
	}else{
		prm = prm + "&iw=" + prm_record.data.image_w;
		prm = prm + "&ih=" + prm_record.data.image_h;
	}
	prm = prm + "&bcl=" + prm_record.data.bg_rgb;
	if(!isNaN(prm_record.data.bg_transparent)) prm = prm + "&bga=0";

	if (isNaN(prm_record.data.scalar_max)) {
	} else {
		prm = prm + "&sx=" + prm_record.data.scalar_max;
	}
	if (isNaN(prm_record.data.scalar_min)) {
	} else {
		prm = prm + "&sn=" + prm_record.data.scalar_min;
	}
	if (prm_record.data.colorbar_f) {
		prm = prm + "&cf=" + prm_record.data.colorbar_f;
	}
	if (prm_record.data.heatmap_f) {
		prm = prm + "&hf=" + prm_record.data.heatmap_f;
	}
	// Bodyparts Version
	var bp3d_tree_group_value = init_tree_group;
	var bp3d_tree_group = Ext.getCmp('anatomo-tree-group-combo');
	if(bp3d_tree_group && bp3d_tree_group.rendered) bp3d_tree_group_value = bp3d_tree_group.getValue();
	prm = prm + "&model=" + encodeURIComponent(tg2model[bp3d_tree_group_value].tg_model);

//	if(!Ext.isEmpty(gParams.tp_md) && gParams.tp_md == 1){
//		console.log(gCOMMON_TPAP);
//	}

	var bp3d_version_value;
	var bp3d_version = Ext.getCmp('anatomo-version-combo');
	if(bp3d_version && bp3d_version.rendered){
		bp3d_version_value = bp3d_version.getValue();
	}
//_dump("makeAnatomoPrm(1):bp3d_version_value=["+bp3d_version_value+"]");
	if(!Ext.isEmpty(gParams.tp_md) && gParams.tp_md == 1){
		if(Ext.isEmpty(bp3d_version_value) && gCOMMON_TPAP) bp3d_version_value = gCOMMON_TPAP.bv;
	}
//_dump("makeAnatomoPrm(2):bp3d_version_value=["+bp3d_version_value+"]");
	if(Ext.isEmpty(bp3d_version_value)) bp3d_version_value = init_bp3d_version;

	prm = prm + "&bv=" + bp3d_version_value;

//_dump("makeAnatomoPrm(3):bp3d_version_value=["+bp3d_version_value+"]");
//_dump("makeAnatomoPrm():bp3d_tree_group_value=["+bp3d_tree_group_value+"]");

	var bp3d_type_value;
	var bp3d_type = Ext.getCmp('bp3d-tree-type-combo');
	if(bp3d_type && bp3d_type.rendered){
		bp3d_type_value = bp3d_type.getValue();
		if(!Ext.isEmpty(bp3d_type_value)){
			if(bp3d_type_value=='3' || bp3d_type_value=='is_a'){
				bp3d_type_value = 'isa';
			}else if(bp3d_type_value=='4' || bp3d_type_value=='part_of'){
				bp3d_type_value = 'partof';
			}else{
//				bp3d_type_value = 'conventional';
			}
		}
	}
	if(!Ext.isEmpty(gParams.tp_md) && gParams.tp_md == 1){
		if(Ext.isEmpty(bp3d_type_value) && gCOMMON_TPAP) bp3d_type_value = gCOMMON_TPAP.tn;
	}
	if(Ext.isEmpty(bp3d_type_value)) bp3d_type_value = 'isa';

	prm = prm + "&tn=" + bp3d_type_value;

//_dump("makeAnatomoPrm():bp3d_type_value=["+bp3d_type_value+"]");
//_dump("makeAnatomoPrm():tn=["+bp3d_type_value+"]");

	// Date
	prm = prm + "&dt=" + getDateString();

	// Draw Legend Flag
	var drawCheck = Ext.getCmp('anatomography_image_comment_draw_check');
	if(drawCheck && drawCheck.rendered){
		if(drawCheck.getValue()) prm = prm + "&dl=1";
	}else if(init_anatomography_image_comment_draw){
		prm = prm + "&dl=1";
	}
	// Draw Pin Number Flag
	var drawCheck = Ext.getCmp('anatomo_pin_number_draw_check');
	if(drawCheck && drawCheck.rendered){
		if(!drawCheck.getValue()) prm = prm + "&np=0";
	}else if(!init_anatomo_pin_number_draw){
		prm = prm + "&np=0";
	}
	// Draw Pin Description Flag
	var drawCheck = Ext.getCmp('anatomo_pin_description_draw_check');
	if(drawCheck && drawCheck.rendered){
		if(drawCheck.getValue()) prm = prm + "&dp=1";
	}else if(init_anatomo_pin_description_draw){
		prm = prm + "&dp=1";
	}

	// Camera Parameters
	// 何れかの値が不正な場合
	if(isNaN(m_ag.cameraPos.x) || isNaN(m_ag.cameraPos.y) || isNaN(m_ag.cameraPos.z) ||
		 isNaN(m_ag.targetPos.x) || isNaN(m_ag.targetPos.y) || isNaN(m_ag.targetPos.z) ||
		 isNaN(m_ag.upVec.x) || isNaN(m_ag.upVec.y) || isNaN(m_ag.upVec.z)){
		if(isNaN(m_ag.cameraPos.x) || isNaN(m_ag.cameraPos.y) || isNaN(m_ag.cameraPos.z)) m_ag.cameraPos = new AGVec3d(2.7979888916016167, -998.4280435445771, 809.7306805551052);
		if(isNaN(m_ag.targetPos.x) || isNaN(m_ag.targetPos.y) || isNaN(m_ag.targetPos.z)) m_ag.targetPos = new AGVec3d(2.7979888916015625, -110.37168800830841, 809.7306805551052);
		if(isNaN(m_ag.upVec.x) || isNaN(m_ag.upVec.y) || isNaN(m_ag.upVec.z)) m_ag.upVec = new AGVec3d(0, 0, 1);
		setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);
		var deg = calcRotateDeg();
		setRotateHorizontalValue(deg.H);
		setRotateVerticalValue(deg.V);

		if(updateRotateImg) updateRotateImg();
	}

	prm = prm + "&cx=" + roundPrm(m_ag.cameraPos.x);
	prm = prm + "&cy=" + truncationPrm(m_ag.cameraPos.y);
	prm = prm + "&cz=" + roundPrm(m_ag.cameraPos.z);
	prm = prm + "&tx=" + roundPrm(m_ag.targetPos.x);
	prm = prm + "&ty=" + truncationPrm(m_ag.targetPos.y);
	prm = prm + "&tz=" + roundPrm(m_ag.targetPos.z);
	prm = prm + "&ux=" + roundPrm(m_ag.upVec.x);
	prm = prm + "&uy=" + roundPrm(m_ag.upVec.y);
	prm = prm + "&uz=" + roundPrm(m_ag.upVec.z);
	prm = prm + "&zm=" + prm_record.data.zoom;
//_dump("prm_record.data.zoom=["+prm_record.data.zoom+"]");
HTML
if($autoRotationHidden ne 'true'){
	print <<HTML;
	var rotateAuto = false;
	try{rotateAuto = Ext.getCmp('ag-command-image-controls-rotateAuto').getValue();}catch(e){}
	if(rotateAuto){
		var orax = roundPrm(agRotateAuto.rotAxis.x);
		var oray = roundPrm(agRotateAuto.rotAxis.y);
		var oraz = roundPrm(agRotateAuto.rotAxis.z);
		var orcx = roundPrm(m_ag.targetPos.x);
		var orcy = truncationPrm(m_ag.targetPos.y);
		var orcz = roundPrm(m_ag.targetPos.z);
		if(isNaN(orax) || isNaN(oray) || isNaN(oraz) || isNaN(orcx) || isNaN(orcy) || isNaN(orcz)){
			try{Ext.getCmp('ag-command-image-controls-rotateAuto').setValue(false);}catch(e){}
			Ext.MessageBox.show({
				title   : 'Auto rotation',
				msg     : 'Value of the coordinate calculation is incorrect.',
				buttons : Ext.MessageBox.OK,
				icon    : Ext.MessageBox.ERROR
			});
		}else{
			prm = prm + "&orax=" + orax;
			prm = prm + "&oray=" + oray;
			prm = prm + "&oraz=" + oraz;
			prm = prm + "&orcx=" + orcx;
			prm = prm + "&orcy=" + orcy;
			prm = prm + "&orcz=" + orcz;
			prm = prm + "&ordg=" + agRotateAuto.angle;
			prm = prm + "&autorotate=" + agRotateAuto.dt_time;
		}
	}
HTML
}
print <<HTML;

	if(!_glb_no_clip){
		// Clip Parameters
		prm = prm + "&cm=" + prm_record.data.clip_type;
		if(prm_record.data.clip_type == 'N'){
		}else{

			var clip;
			try{clip = Ext.getCmp('anatomo-clip-predifined-plane').getValue();}catch(e){clip = undefined;}
//			if(!clip || clip == 'FREE'){
			if(clip && clip == 'FREE'){
				prm = prm + "&cd="  + (isNaN(prm_record.data.clip_depth)?'NaN':prm_record.data.clip_depth);
				prm = prm + "&cpa=" + (isNaN(prm_record.data.clip_paramA)?'NaN':roundPrm(prm_record.data.clip_paramA));
				prm = prm + "&cpb=" + (isNaN(prm_record.data.clip_paramB)?'NaN':roundPrm(prm_record.data.clip_paramB));
				prm = prm + "&cpc=" + (isNaN(prm_record.data.clip_paramC)?'NaN':roundPrm(prm_record.data.clip_paramC));
				prm = prm + "&cpd=" + (isNaN(prm_record.data.clip_paramD)?'NaN':roundPrm(prm_record.data.clip_paramD));
				prm = prm + "&ct=" + prm_record.data.clip_method;
			}else{
				prm = prm + "&cd=0";
				prm = prm + "&cpa=" + (isNaN(prm_record.data.clip_paramA)?'NaN':roundPrm(prm_record.data.clip_paramA));
				prm = prm + "&cpb=" + (isNaN(prm_record.data.clip_paramB)?'NaN':roundPrm(prm_record.data.clip_paramB));
				prm = prm + "&cpc=" + (isNaN(prm_record.data.clip_paramC)?'NaN':roundPrm(prm_record.data.clip_paramC));
				prm = prm + "&cpd=" + (isNaN(prm_record.data.clip_depth)?'NaN':prm_record.data.clip_depth);
				prm = prm + "&ct=" + prm_record.data.clip_method;
			}
		}
	}

	// Organ Parameters
	if (ag_parts_store && ag_parts_store.getCount() > 0) {

		var onum = 1;
		var pnum = 1;
		var num;

		for (var i = 0; i < ag_parts_store.getCount(); i++) {
			var record = ag_parts_store.getAt(i);
			if (!record || !record.data || (!record.data.f_id && !record.data.name_e)) return;

			if(!Ext.isEmpty(aMode) && aMode == 2){	//保存モード

				if(isPointDataRecord(record)){
					if(!record.data.f_id) continue;
					num = makeAnatomoOrganNumber(pnum);
					prm = prm + "&poid" + num + "=" + record.data.f_id;
					prm = prm + makeAnatomoOrganPointPrm(num,record);
					prm = prm + "&polb" + num + "=" + record.data.point_label;
					pnum++;
				}else{
					num = makeAnatomoOrganNumber(onum);
					if(record.data.f_id){
						prm = prm + "&oid" + num + "=" + record.data.f_id;
					}else if(record.data.name_e){
						prm = prm + "&onm" + num + "=" + record.data.name_e;
					}else{
						continue;
					}
					if(record.data.version) prm = prm + "&ov" + num + "=" + record.data.version;
					prm = prm + makeAnatomoOrganPrm(num,record,aMode,aOpacity);
					onum++;
				}
				continue;
			}

			if(record.data.tg_id == bp3d_tree_group_value){
				if(isPointDataRecord(record)){
					if(!record.data.f_id) continue;
					if(!Ext.isEmpty(prm_record.data.point_label) && record.data.point_label != prm_record.data.point_label) continue;
					num = makeAnatomoOrganNumber(pnum);
					prm = prm + "&poid" + num + "=" + record.data.f_id;
					prm = prm + makeAnatomoOrganPointPrm(num,record);
					pnum++;
					continue;
				}else{
					num = makeAnatomoOrganNumber(onum);
					if(record.data.f_id){
						prm = prm + "&oid" + num + "=" + record.data.f_id;
					}else if(record.data.name_e){
						prm = prm + "&onm" + num + "=" + record.data.name_e;
					}else{
						continue;
					}
					prm = prm + makeAnatomoOrganPrm(num,record,undefined,aOpacity);
					onum++;
					continue;
				}
			}else{
				if(Ext.isEmpty(aMode)){	//通常モード
					if(record.data.conv_id){
						var id_arr = record.data.conv_id.split(",");
						for(var ocnt=0;ocnt<id_arr.length;ocnt++){
							if(isPointDataRecord(record)){
								if(!Ext.isEmpty(prm_record.data.point_label) && record.data.point_label != prm_record.data.point_label) continue;
								num = makeAnatomoOrganNumber(pnum);
								prm = prm + "&poid" + num + "=" + id_arr[ocnt];
								prm = prm + makeAnatomoOrganPointPrm(num,record);
								pnum++;
							}else{
								num = makeAnatomoOrganNumber(onum);
								prm = prm + "&oid" + num + "=" + id_arr[ocnt];
								prm = prm + makeAnatomoOrganPrm(num,record,undefined,aOpacity);
								onum++;
							}
						}
					}else{
						if(isPointDataRecord(record)){
							if(!Ext.isEmpty(prm_record.data.point_label) && record.data.point_label != prm_record.data.point_label) continue;
							num = makeAnatomoOrganNumber(pnum);
							prm = prm + "&poid" + num + "=" + record.data.f_id;
							prm = prm + makeAnatomoOrganPointPrm(num,record);
							pnum++;
						}else{
							num = makeAnatomoOrganNumber(onum);
							prm = prm + "&onm" + num + "=" + record.data.name_e;
							prm = prm + makeAnatomoOrganPrm(num,record,undefined,aOpacity);
							onum++;
						}
					}
				}else{	//Linkモード
					if(isPointDataRecord(record)){
						if(!Ext.isEmpty(prm_record.data.point_label) && record.data.point_label != prm_record.data.point_label) continue;
						num = makeAnatomoOrganNumber(pnum);
						prm = prm + "&poid" + num + "=" + record.data.f_id;
						prm = prm + makeAnatomoOrganPointPrm(num,record);
						pnum++;
					}else{
						num = makeAnatomoOrganNumber(onum);
						prm = prm + "&oid" + num + "=" + record.data.f_id;
						if(record.data.version) prm = prm + "&ov" + num + "=" + record.data.version;
						prm = prm + makeAnatomoOrganPrm(num,record,undefined,aOpacity);
						onum++;
					}
				}
			}
		}

		if(get_point_f_id() && (Ext.isEmpty(aMode) || aMode != 2)){	//保存モード
			//Palletに存在しないパーツがピックされた場合
			var num = makeAnatomoOrganNumber(onum);
			prm = prm + "&oid" + num + "=" + get_point_f_id();
			prm = prm + "&ocl" + num + "=" + glb_point_color;
			onum++;
		}

//		if(onum>1){
//dpl	0,1,2	ピンからPin Descriptionへの線描画指定(0：ピンからDescriptionへの線描画無し、1：ピンの先端からDescriptionへの線描画、2：ピンの終端からDescriptionへの線描画）。Descriptionが描画されていないと線も描画しない。
//dpod	0,1	点構造のDescription
//dpol	0,1,2	点からPoint Descriptionへの線描画指定(0：点からDescriptionへの線描画無し、1：点の先端からDescriptionへの線描画、2：点の終端からDescriptionへの線描画）。Descriptionが描画されていないと線も描画しない。
//			prm = prm + "&dpl="+prm_record.data.point_pin_line;
//			prm = prm + "&dpod="+prm_record.data.point_desc;
//			prm = prm + "&dpol="+prm_record.data.point_point_line;
//		}
	}
	//dpl	0,1,2	ピンからPin Descriptionへの線描画指定(0：ピンからDescriptionへの線描画無し、1：ピンの先端からDescriptionへの線描画、2：ピンの終端からDescriptionへの線描画）。Descriptionが描画されていないと線も描画しない。
	prm = prm + "&dpl="+prm_record.data.point_pin_line;

	// Legend Parameters
	var drawCheck = Ext.getCmp('anatomography_image_comment_draw_check');
	if(drawCheck && drawCheck.rendered){
		if(drawCheck.getValue()){
			prm = prm + "&lp=UL";
			prm = prm + "&lc=646464";
		}
	}else if(init_anatomography_image_comment_draw){
		prm = prm + "&lp=UL";
		prm = prm + "&lc=646464";
	}

//	prm = prm + "&lt=" + encodeURIComponent(Ext.getCmp("anatomography_image_comment_title").getValue());
	var cmp = Ext.getCmp("anatomography_image_comment_title");
	if(cmp && cmp.rendered){
		var value = encodeURIComponent(cmp.getValue());
		if(value != '') prm = prm + "&lt=" + value;
	}

//	prm = prm + "&le=" + encodeURIComponent(Ext.getCmp("anatomography_image_comment_legend").getValue());
	var cmp = Ext.getCmp("anatomography_image_comment_legend");
	if(cmp && cmp.rendered){
		var value = encodeURIComponent(cmp.getValue());
		if(value != '') prm = prm + "&le=" + value;
	}

//	prm = prm + "&la=" + encodeURIComponent(Ext.getCmp("anatomography_image_comment_author").getValue());
	var cmp = Ext.getCmp("anatomography_image_comment_author");
	if(cmp && cmp.rendered){
		var value = encodeURIComponent(cmp.getValue());
		if(value != '') prm = prm + "&la=" + value;
	}

	//Grid
	if (prm_record.data.grid && prm_record.data.grid=='1') {
		prm = prm + "&gdr=true";
		prm = prm + "&gcl="+prm_record.data.grid_color;
		prm = prm + "&gtc="+prm_record.data.grid_len;
	}

	var anatomo_pin_shape_combo_value;
	try{
		anatomo_pin_shape_combo_value = Ext.getCmp("anatomo_pin_shape_combo").getValue();
	}catch(e){
		anatomo_pin_shape_combo_value = init_anatomo_pin_shape;
	}

	// color_rgb (Default parts color)
	if(!Ext.isEmpty(aMode) && aMode == 2){	//保存モード
		prm = prm + "&fcl="+prm_record.data.color_rgb;
	}

	//coordinate_system
	var coordinate_system;
	try{
		coordinate_system = Ext.getCmp("ag-coordinate-system-combo").getValue();
	}catch(e){
		coordinate_system = prm_record.data.coord;
	}
	prm = prm + "&crd="+coordinate_system;

	// Pin Parameters
	if (ag_comment_store && ag_comment_store.getCount() > 0) {

		for (var i = 0; i < ag_comment_store.getCount(); i++) {
			var prmPin = makeAnatomoPrm_Pin(ag_comment_store.getAt(i),anatomo_pin_shape_combo_value,coordinate_system);
			if(Ext.isEmpty(prmPin)) continue;
			prm = prm + '&' + prmPin;
		}
	}

	return prm;
	}catch(e){
		_dump("makeAnatomoPrm():"+e);
	}
}

oncheck_anatomo_grid_check = function(checkbox, fChecked){
	var prm_record = ag_param_store.getAt(0);
	prm_record.beginEdit();
	if (fChecked) {
		prm_record.set('grid', '1');
	} else {
		prm_record.set('grid', '0');
	}
	prm_record.endEdit();
	prm_record.commit();

	if(fChecked){
		try{
			Ext.get('ag-command-grid-len-label').show(false);
			Ext.get('ag-command-grid-color-label').show(false);
		}catch(e){}
		try{
			Ext.get('ag-image-grid-box').setHeight(66,{
				callback:function(){
					try{
						Ext.getCmp('ag-command-grid-len-combobox').enable();
						Ext.getCmp('ag-command-grid-len-combobox').show(false);
					}catch(e){}
					Ext.getCmp('ag-command-grid-color-field').enable();
					Ext.getCmp('ag-command-grid-color-field').show(false);
				}
			});
		}catch(e){}
	}else{
		try{
			Ext.get('ag-command-grid-len-label').hide(false);
			Ext.get('ag-command-grid-color-label').hide(false);
		}catch(e){}
		try{
			Ext.get('ag-image-grid-box').setHeight(19,true);
		}catch(e){}

		try{
			Ext.getCmp('ag-command-grid-len-combobox').hide(false);
			Ext.getCmp('ag-command-grid-len-combobox').disable();
		}catch(e){}
		Ext.getCmp('ag-command-grid-color-field').hide(false);
		Ext.getCmp('ag-command-grid-color-field').disable();
	}
	updateAnatomo();
}

/* iPad用 */
var anatomoImgDragStart_dX = null;
var anatomoImgDragStart_dY = null;
var anatomoImgDragStart_degH = null;
var anatomoImgDragStart_degV = null;

var anatomoImgMoveStartX = null;
var anatomoImgMoveStartY = null;
var anatomoImgMoveStart_dX = null;
var anatomoImgMoveStart_dY = null;

var curScale = null;
var chgScale = null;
var curRotation = null;

is_iPad = function(){
	if(navigator.userAgent.match(/^Mozilla\\/5\\.0\\s\\(iPad;\\s*U;\\s(CPU\\s*[^;]+);[^\\)]+\\)/)){
		return true;
	}else{
		return false;
	}
}

imgTouchStart = function(e){
	e.preventDefault();
//_dump("imgTouchStart()");

	if(!e.touches) e.touches = [];
	for(var key in e){
		if(typeof e[key] == "function"){
		}else{
//			_dump('touchstart():'+key+"=["+e[key]+"]");
		}
	}

	if(e.touches && e.touches.length>1){
		anatomoImgDragStartX = null;
		anatomoImgDragStartY = null;
		anatomoImgDragStart_dX = null;
		anatomoImgDragStart_dY = null;

		anatomoImgMoveStartX = e.targetTouches[0].pageX;
		anatomoImgMoveStartY = e.targetTouches[0].pageY;
		anatomoImgMoveStart_dX = 0;
		anatomoImgMoveStart_dY = 0;
		return;
	}else{
		if(e.targetTouches && e.targetTouches.length>0){
			anatomoImgDragStartX = e.targetTouches[0].pageX;
			anatomoImgDragStartY = e.targetTouches[0].pageY;
		}else{
			anatomoImgDragStartX = e.pageX;
			anatomoImgDragStartY = e.pageY;
		}
		anatomoImgDragStart_dX = null;
		anatomoImgDragStart_dY = null;

		anatomoImgMoveStartX = null;
		anatomoImgMoveStartY = null;
		anatomoImgMoveStart_dX = null;
		anatomoImgMoveStart_dY = null;
	}
};
imgTouchMove = function(e){
	e.preventDefault();
//_dump("imgTouchMove(2)");

//_dump('touchmove:'+e.touches.length+","+e.targetTouches[0].pageX+","+e.targetTouches[0].pageY+","+chgScale+","+chgScale);

	if(anatomoImgDragStartX == null || anatomoImgDragStartY == null){
		if(anatomoImgMoveStartX != null && anatomoImgMoveStartY != null){
			anatomoImgMoveStart_dX = e.targetTouches[0].pageX - anatomoImgMoveStartX;
			anatomoImgMoveStart_dY = e.targetTouches[0].pageY - anatomoImgMoveStartY;

			if(chgScale == null) e.target.style.webkitTransform = 'translate(' + anatomoImgMoveStart_dX + 'px, ' + anatomoImgMoveStart_dY + 'px)';

		}
		return;
	}


	var dX = e.targetTouches[0].pageX - anatomoImgDragStartX;
	var dY = e.targetTouches[0].pageY - anatomoImgDragStartY;

//_dump('touchmove:'+e.touches.length+","+e.targetTouches[0].pageX+","+e.targetTouches[0].pageY+","+dX+","+dY);

	anatomoImgDragStart_dX = dX;
	anatomoImgDragStart_dY = dY;

	if(e.touches.length>1){
		return;
	}

	var rotateHSpan = document.getElementById("rotateH");
	var rotateVSpan = document.getElementById("rotateV");

	var degH = getRotateHorizontalValue();
	degH = degH - 15 * Math.floor(dX / 20);
	while (degH >= 360) {
		degH = degH - 360;
	}
	while (degH < 0) {
		degH = degH + 360;
	}

	var degV = getRotateVerticalValue();
	degV = degV + 15 * Math.floor(dY / 20);
	while (degV >= 360) {
		degV = degV - 360;
	}
	while (degV < 0) {
		degV = degV + 360;
	}

	degH = degH.toString();
	degV = degV.toString();

	anatomoImgDragStart_degH = degH;
	anatomoImgDragStart_degV = degV;

	var rotateHSpan = document.getElementById("rotImgDivRotateH");
	if(rotateHSpan){
		rotateHSpan.innerHTML = "H:"+degH;
	}

	var rotateVSpan = document.getElementById("rotImgDivRotateV");
	if(rotateVSpan){
		rotateVSpan.innerHTML = "V:"+degV;
	}

	var rotImgDiv = document.getElementById("rotImgDiv");
	if(rotImgDiv){
		rotImgDiv.style.left = (parseInt(e.targetTouches[0].pageX) - 130) + "px";
		rotImgDiv.style.top  = (parseInt(e.targetTouches[0].pageY) + 0)   + "px";

		var posX = (degH / 15 * (-80));
		var posY = (degV / 15 * (-80));

		if(posX<=-960 && posY<=-960){
			posX += 960;
			posY += 960;
			rotImgDiv.style.backgroundImage = "url(iphone/img/rotImg_iphone_rb.png)";
		}else if(posX<=-960){
			posX += 960;
			rotImgDiv.style.backgroundImage = "url(iphone/img/rotImg_iphone_rt.png)";
		}else if(posY<=-960){
			posY += 960;
			rotImgDiv.style.backgroundImage = "url(iphone/img/rotImg_iphone_lb.png)";
		}else{
			rotImgDiv.style.backgroundImage = "url(iphone/img/rotImg_iphone_lt.png)";
		}
		rotImgDiv.style.backgroundPositionX = posX + "px";
		rotImgDiv.style.backgroundPositionY = posY + "px";

		rotImgDiv.style.visibility = "visible";
	}

//_dump("degH=["+degH+"],degV=["+degV+"]");
//_dump(rotImgDiv.style.backgroundPosition);
};
imgTouchEnd = function(e){
	e.preventDefault();
//_dump("imgTouchEnd()");

//_dump('touchend:'+anatomoImgDragStart_dX+","+anatomoImgDragStart_dY);

	var rotImgDiv = document.getElementById("rotImgDiv");
	if(rotImgDiv) rotImgDiv.style.visibility = "hidden";

	if(anatomoImgDragStartX == null || anatomoImgDragStartY == null || anatomoImgDragStart_dX == null || anatomoImgDragStart_dY == null){
		if(anatomoImgMoveStartX == null || anatomoImgMoveStartY == null || anatomoImgMoveStart_dX == null || anatomoImgMoveStart_dY == null){
			if(anatomoImgDragStartX == null || anatomoImgDragStartY == null){
			 element_selected(e);
			}else{
				try{
					var img = document.getElementById('ag_img');
					var imgX = anatomoImgDragStartX - img.x;
					var imgY = anatomoImgDragStartY - img.y;
//_dump('touchend():&px=' + img.x + '&py=' +img.y);
				}catch(ex){
					alert(ex);
					return;
				}

//_dump('touchend():&px=' + imgX + '&py=' +imgY);

//				var urlStr = cgipath.point+'?' + makeAnatomoPrm() + '&px=' + imgX + '&py=' +imgY;

				var params = Ext.urlDecode(makeAnatomoPrm());
				params.px = imgX;
				params.py = imgY;

				var jsonStr = null;
				try{
					jsonStr = ag_extensions.toJSON.URI2JSON(params,{
						toString:true,
						mapPin:false,
						callback:undefined
					});
				}catch(e){jsonStr = null;}

				Ext.Ajax.request({
					url     : cgipath.point,
					method  : 'POST',
					params  : jsonStr ? jsonStr : params,
					success : function (response, options) {

//						var f_id = response.responseText;
						var f_id;
						try{var pointData = Ext.util.JSON.decode(response.responseText);}catch(e){_dump(e);}
						if(pointData) f_id = pointData.id;



						if(!f_id || !f_id.match(/^(?:FMA|BP)\\d+/)){
							return;
						}

						getPickList(f_id,'partof');

					},
					failure: function (response, options) {
						alert(cgipath.point+":failure():"+response.statusText);
					}
				});
			}
		}
		anatomoImgDragStart_dX = null;
		anatomoImgDragStartdY = null;
		return;
	}

	var dX = anatomoImgDragStart_dX;
	var dY = anatomoImgDragStart_dY;

	try{
		setRotateHorizontalValue(anatomoImgDragStart_degH);
		setRotateVerticalValue(anatomoImgDragStart_degV);

		setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);
		addLongitude(-15 * Math.floor(dX / 20));
		addLatitude(15 * Math.floor(dY / 20));

		updateAnatomo();

		anatomoImgDragStart_dX = null;
		anatomoImgDragStart_dY = null;

	}catch(ex){
		_dump(ex);
	}
};
imgGestureStart = function(e){
	e.preventDefault();
//_dump("imgGestureStart()");
	if(curScale == null) curScale = 1;
};
imgGestureChange = function(e){
	e.preventDefault();
//_dump("imgGestureChange()");

	chgScale = e.scale;
	chgScale *= curScale;
	if(chgScale<1) chgScale = 1;

//_dump("gesturechange:["+ e.scale + "]["+ curScale + "]["+ chgScale + "]");

	e.target.style.webkitTransform = 'scale(' + e.scale + ') translate(' + anatomoImgMoveStart_dX + 'px, ' + anatomoImgMoveStart_dY + 'px)';

	var value = chgScale - 1;
	if(value<0) value = 0;
	if(value>6) value = 6;

	var prm_record = ag_param_store.getAt(0);
	prm_record.beginEdit();
	prm_record.set('zoom', value);
	prm_record.endEdit();
	prm_record.commit();

	var rotImgDiv = document.getElementById("rotImgDiv");
	if(rotImgDiv) rotImgDiv.style.visibility = "hidden";
};
imgGestureEnd = function(e){
	e.preventDefault();
//_dump("imgGestureEnd()");

	var dX = anatomoImgMoveStart_dX;
	var dY = anatomoImgMoveStart_dY;

	setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);
	moveTargetByMouseForOrtho(ag_param_store.getAt(0).data.image_h, dX / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)), dY / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)));

	updateAnatomo();

	curScale = chgScale;
	chgScale = null;
};

ag_command_zoom_menu_slider_syncThumb_task = new Ext.util.DelayedTask(function(){
	var slider = Ext.getCmp('zoom-slider');
	if(!slider || !slider.rendered) return;
	slider.syncThumb();
});

anatomography_image_render = function(comp,aOptions,aCB){
//	try{
		if(Ext.isEmpty(gParams.tp_md)){
			gParams.tp_ct = 1;
			gParams.tp_bt = 1;
			gParams.tp_ro = 1;
			gParams.tp_gr = 1;
			gParams.tp_zo = 1;
		}

		if(window.top != window && is_iPad()){
			delete gParams.tp_ct;
			delete gParams.tp_bt;
			delete gParams.tp_ro;
			delete gParams.tp_gr;
			delete gParams.tp_zo;
		}

		if(is_iPad()){
			var imageElem = document.getElementById('ag_img');
			if(imageElem){
				imageElem.addEventListener('touchstart',imgTouchStart,false);
				imageElem.addEventListener('touchmove', imgTouchMove, false);
				imageElem.addEventListener('touchend',  imgTouchEnd,  false);

				imageElem.addEventListener('gesturestart', imgGestureStart,  false);
				imageElem.addEventListener('gesturechange',imgGestureChange, false);
				imageElem.addEventListener('gestureend',   imgGestureEnd,    false);

				imageElem.addEventListener('load',function(e){
					e.target.style.webkitTransform = 'scale(1) translate(0px, 0px)';
					e.target.style.webkitTransformStyle = 'flat';
					e.target.style.left = '0px';
					e.target.style.top  = '0px';
				},false);
			}
			Ext.getDom('ag-image-command-box').style.opacity = '1';
			if(false){
				Ext.get('ag-command-ipad').removeClass('x-hide-display');
			}
		}

		comp.on("resize", function(comp,adjWidth,adjHeight,rawWidth,rawHeight){
			setImageWindowSize();
		});

		var ag_img = Ext.get('ag_img');
		if(ag_img){
			ag_img.on("load", function(e){
				var ag_img_frame = Ext.get("ag_img_frame");
				if(ag_img_frame){
					var load_image = e.getTarget();
					ag_img_frame.dom.style.width = load_image.width + 'px';
					ag_img_frame.dom.style.height = load_image.height + 'px';
				}
				var cmp = Ext.getCmp('anatomography-image');
				if(cmp && cmp.rendered && cmp.loadMask) cmp.loadMask.hide();
			});
			ag_img.on("contextmenu", function(e){
//				_dump("contextmenu");
//				e.stopEvent();
			});
		}



		if(Ext.isEmpty(gParams.tp_ct)){
			Ext.get('ag-image-command-box').setVisibilityMode(Ext.Element.DISPLAY);
			Ext.get('ag-image-command-box').hide();
		}

		Ext.get('ag-image-rotate-box').removeClass('x-hide-display');

		if(Ext.isEmpty(gParams.tp_bt)){
			Ext.get('ag-image-button-box').setVisibilityMode(Ext.Element.DISPLAY);
			Ext.get('ag-image-button-box').hide();
		}

		if(is_iPad()){
			Ext.get('ag-image-zoom-text-box').setVisibilityMode(Ext.Element.DISPLAY);
			Ext.get('ag-image-zoom-text-box').hide();
		}

		var prm_record = ag_param_store.getAt(0);

		setTimeout(function(){
			if(Ext.isEmpty(gParams.tp_zo)){
				Ext.get('ag-image-zoom-box').setVisibilityMode(Ext.Element.DISPLAY);
				Ext.get('ag-image-zoom-box').hide();
			}else if(Ext.isIE){
/* IEで表示しなので修正の必要あり
				var elem = Ext.getDom('ag-command-zoom-btn-down');
				if(elem){
					var parentNode = elem.parentNode;
					parentNode.removeChild(elem);
					elem = parentNode.ownerDocument.createElement('a');
					elem.setAttribute('id','ag-command-zoom-btn-down');
					parentNode.appendChild(elem);
				}
*/
			}
HTML
if($agInterfaceType eq '5'){
	print <<HTML;
			var d_height = 190;
			if(Ext.isEmpty(gParams.tp_ro) && Ext.isEmpty(gParams.tp_gr)){
				d_height -= 90;
			}else if(Ext.isEmpty(gParams.tp_ro)){
				d_height -= 26;
			}else if(Ext.isEmpty(gParams.tp_gr)){
				d_height -= 74;
			}
			if(is_iPad()) d_height -= 24;

			var size = comp.getSize();
			var slider_height = size.height-d_height;
			if(slider_height<20) slider_height = 20;
			if(slider_height>100) slider_height = 100;
			Ext.get('ag-command-zoom-slider-render').setHeight(slider_height);
HTML
}
print <<HTML;
			new Ext.Slider({
				renderTo: 'ag-command-zoom-slider-render',
				id: 'zoom-slider',
				value : prm_record.data.zoom,
HTML
if($agInterfaceType eq '5'){
	print <<HTML;
				height: slider_height,
				vertical: true,
HTML
}elsif($agInterfaceType eq '4'){
	print <<HTML;
				width: 90,
				vertical: false,
HTML
}
print <<HTML;
				hidden : Ext.isEmpty(gParams.tp_zo),
				minValue: 0,
				maxValue: DEF_ZOOM_MAX-1,
				increment: 1,
				plugins: new Ext.ux.SliderTip(),
				listeners: {
					'change' : {
						fn : function (slider, value) {
//_dump("zoom-slider.change():value=["+value+"]");
							if(glb_zoom_xy){
								var elemImg = Ext.get('ag_img');
//								var xyImg = elemImg.getXY();
								var xyImg = glbImgXY;
								var mouseX = glb_zoom_xy[0] - xyImg[0];
								var mouseY = glb_zoom_xy[1] - xyImg[1];
								var centerX = parseInt((ag_param_store.getAt(0).data.image_w /2) -  mouseX);
								var centerY = parseInt((ag_param_store.getAt(0).data.image_h /2) -  mouseY);
								setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);
								moveTargetByMouseForOrtho(ag_param_store.getAt(0).data.image_h, centerX / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)), centerY / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)));
							}
							var prm_record = ag_param_store.getAt(0);
							prm_record.beginEdit();
							prm_record.set('zoom', value / 5);
							prm_record.endEdit();
							prm_record.commit();
							anatomoUpdateZoomValueText(value + 1);
							if(glb_zoom_xy){
								var elemImg = Ext.get('ag_img');
//								var xyImg = elemImg.getXY();
								var xyImg = glbImgXY;
								var mouseX = glb_zoom_xy[0] - xyImg[0];
								var mouseY = glb_zoom_xy[1] - xyImg[1];
								var moveX = parseInt(mouseX - (ag_param_store.getAt(0).data.image_w /2));
								var moveY = parseInt(mouseY - (ag_param_store.getAt(0).data.image_h /2));
								setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);
								moveTargetByMouseForOrtho(ag_param_store.getAt(0).data.image_h, moveX / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)), moveY / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)));
							}
							updateAnatomo();
							updateClipImage();
							if(glb_zoom_xy) glb_zoom_xy = null;
						},
						scope  : this
					},
					'render' : {
						fn : function(slider){
							if(glb_zoom_slider){
								var textField = Ext.getCmp('zoom-value-text');
								var slider = Ext.getCmp('zoom-slider');
								if(slider && slider.rendered && textField && textField.rendered){
//_dump("zoom-slider.render():glb_zoom_slider=["+glb_zoom_slider+"]");
									slider.setValue(glb_zoom_slider-1);
									glb_zoom_slider = null;
									ag_command_zoom_menu_slider_syncThumb_task.delay(1000);
								}
							}
						},
						scope:this
					}
				}
			});
		},100);

		new Ext.form.NumberField ({
			ctCls : 'x-small-editor',
			renderTo: 'ag-command-zoom-text-render',
			id: 'zoom-value-text',
			width: 28,
			value : prm_record.data.zoom+1,
			allowBlank : false,
			allowDecimals : false,
			allowNegative : false,
			selectOnFocus : true,
			hidden : Ext.isEmpty(gParams.tp_zo),
			maxValue : DEF_ZOOM_MAX,
			minValue : 1,
			listeners: {
				'change': {
					fn : function(textField,newValue,oldValue){
						if (anatomoUpdateZoomValue) {
							return;
						}
						var value = isNaN(parseInt(newValue, 10))?oldValue:parseInt(newValue, 10);
						if (value < 1) {
							value = 1;
						}
						if (value > DEF_ZOOM_MAX) {
							value = DEF_ZOOM_MAX
						}
						textField.setValue(value);
						var slider = Ext.getCmp('zoom-slider');
						if(slider && slider.rendered){
//_dump("zoom-value-text.change():["+value+"]");
							slider.setValue(value - 1);
							ag_command_zoom_menu_slider_syncThumb_task.delay(1000);
						}
					},
					scope:this
				},
				'valid': {
					fn : function(textField){
						var value = textField.getValue();
						var slider = Ext.getCmp('zoom-slider');
						if(slider && slider.rendered){
//_dump("zoom-value-text.valid():["+value+"]");
							slider.setValue(value - 1);
							ag_command_zoom_menu_slider_syncThumb_task.delay(1000);
						}
					},
					scope:this
				},
				'render': {
					fn : function(textField){
						if(glb_zoom_slider){
							var slider = Ext.getCmp('zoom-slider');
							if(slider && slider.rendered){
//_dump("zoom-value-text.render():glb_zoom_slider=["+glb_zoom_slider+"]");
								slider.setValue(glb_zoom_slider-1);
								glb_zoom_slider = null;
								ag_command_zoom_menu_slider_syncThumb_task.delay(1000);
							}
						}
					},
					scope:this
				}
			}
		});

		var ag_command_rotate_menu_hide_task = new Ext.util.DelayedTask(function(){
			var button = Ext.getCmp('ag-command-rotate-button');
			if(!button || !button.rendered) return;
			if(button.hasVisibleMenu()) button.hideMenu();
		});
HTML
if($agInterfaceType eq '5'){
	print <<HTML;
		new Ext.Button({
			ctCls : 'x-small-editor',
			renderTo: 'ag-command-rotate-button-render',
			id: 'ag-command-rotate-button',
			width: 30,
			text:'Rotate',
			hidden : Ext.isEmpty(gParams.tp_ro),
			menu: {
				id: 'ag-command-rotate-menu',
				cls : 'ag-command-rotate-menu',
				items : [{
					text   : 'H:0,V:0',
					icon   : "img_angle/000_000.png",
					itemCls: 'x-menu-item ag-command-rotate-menu-item',
					handler: function(){ setRotate(0,0); }
				},{
					text   : 'H:45,V:0',
					icon   : "img_angle/045_000.png",
					itemCls: 'x-menu-item ag-command-rotate-menu-item',
					handler: function(){ setRotate(45,0); }
				},{
					text   : 'H:90,V:0',
					icon   : "img_angle/090_000.png",
					itemCls: 'x-menu-item ag-command-rotate-menu-item',
					handler: function(){ setRotate(90,0); }
				},{
					text   : 'H:180,V:0',
					icon   : "img_angle/180_000.png",
					itemCls: 'x-menu-item ag-command-rotate-menu-item',
					handler: function(){ setRotate(180,0); }
				},{
					text   : 'H:270,V:0',
					icon   : "img_angle/270_000.png",
					itemCls: 'x-menu-item ag-command-rotate-menu-item',
					handler: function(){ setRotate(270,0); }
				},{
					text   : 'H:315,V:0',
					icon   : "img_angle/315_000.png",
					itemCls: 'x-menu-item ag-command-rotate-menu-item',
					handler: function(){ setRotate(315,0); }
				},{
					text   : 'H:180,V:90',
					icon   : "img_angle/180_090.png",
					itemCls: 'x-menu-item ag-command-rotate-menu-item',
					handler: function(){ setRotate(180,90); }
				},{
					text   : 'H:0,V:270',
					icon   : "img_angle/000_270.png",
					itemCls: 'x-menu-item ag-command-rotate-menu-item',
					handler: function(){ setRotate(0,270); }
				}]
			}
		});


		Ext.QuickTips.register({
			target: 'ag-command-btn-rotate',
			text: get_ag_lang('TOOLTIP_ROTATE')
		});
		Ext.QuickTips.register({
			target: 'ag-command-btn-move',
			text: get_ag_lang('TOOLTIP_MOVE')
		});
		Ext.QuickTips.register({
			target: 'ag-command-focus-center-button',
			text: get_ag_lang('TOOLTIP_FOCUS_CENTER')
		});
		Ext.QuickTips.register({
			target: 'ag-command-focus-button',
			text: get_ag_lang('TOOLTIP_FOCUS')
		});

HTML
}
if($autoRotationHidden ne 'true'){
	print <<HTML;
		new Ext.form.Checkbox({
			ctCls    : 'x-small-editor',
			id       : 'ag-command-autorotate-chechbox',
			checked  : false,
			listeners: {
				'check': function(checkbox,checked){
					Ext.getCmp('ag-command-image-controls-rotateAuto').setValue(checked);
				},
				scope:this
			}
		}).render('ag-command-autorotate-chechbox-render','ag-command-autorotate-chechbox-label');
		if(gDispAnatomographyPanel){
			var elem = Ext.get('ag-command-autorotate-chechbox-render');
			if(elem){
				elem.setVisibilityMode(Ext.Element.DISPLAY);
				elem.hide();
			}
			Ext.get('ag-command-autorotate-chechbox-label').hide();
		}
HTML
}
print <<HTML;

		if(Ext.isEmpty(gParams.tp_gr)){
			try{
				Ext.get('ag-image-grid-box').setVisibilityMode(Ext.Element.DISPLAY);
				Ext.get('ag-image-grid-box').hide();
			}catch(e){}
		}

		new Ext.form.Checkbox ({
			ctCls : 'x-small-editor',
			renderTo: 'ag-command-grid-render',
			id: 'ag-command-grid-show-check',
			width: 45,
			checked: (prm_record.data.grid=='1')?true:false,
			hidden : Ext.isEmpty(gParams.tp_gr),
			listeners: {
				'render': function(checkbox){
					checkbox.on('check',oncheck_anatomo_grid_check);
					if(checkbox.checked){
						try{Ext.get('ag-image-grid-box').setHeight(66);}catch(e){}
						try{Ext.getCmp('ag-command-grid-len-combobox').show();}catch(e){}
					}else{
						try{Ext.getCmp('ag-command-grid-len-combobox').hide();}catch(e){}
						try{Ext.get('ag-image-grid-box').setHeight(19);}catch(e){}
					}
				},
				scope:this
			}
		});

HTML
if(0 && $useColorPicker eq 'true'){
	print <<HTML;
		new Ext.ux.ColorPickerField({
HTML
}else{
	print <<HTML;
		new Ext.ux.ColorField({
HTML
}
print <<HTML;
			ctCls : 'x-small-editor',
HTML
if($agInterfaceType eq '5'){
	print qq|			width: 54,\n|;
}elsif($agInterfaceType eq '4'){
	print qq|			width: 69,\n|;
}
print <<HTML;
			renderTo:'ag-command-grid-color-render',
			id:'ag-command-grid-color-field',
			value:prm_record.data.grid_color,
			disabled: (prm_record.data.grid=='1')?false:true,
			hidden: (prm_record.data.grid=='1')?false:true,
			editable: false,
			hideTrigger : is_iPad(),
			colors: palette_color2,
			colorsItemCls: 'x-color-palette x-color-palette-grid',
			colorsOptionMenu: false,
			listeners: {
				select: function (e, color) {
					var prm_record = ag_param_store.getAt(0);
					prm_record.beginEdit();
					prm_record.set('grid_color', color);
					prm_record.endEdit();
					prm_record.commit();
					updateAnatomo();
				},
				render: function(checkbox){
					try{
						if(prm_record.data.grid=='1'){
							Ext.get('ag-command-grid-color-label').show(false);
						}else{
							Ext.get('ag-command-grid-color-label').hide(false);
						}
					}catch(e){}
				},
				scope:this
			}
		});

		new Ext.form.ComboBox({
			ctCls : 'x-small-editor',
			renderTo:'ag-command-grid-len-render',
			id: 'ag-command-grid-len-combobox',
			editable: false,
			mode: 'local',
			lazyInit: false,
			displayField: 'disp',
			valueField: 'value',
HTML
if($agInterfaceType eq '5'){
	print qq|			width: 54,\n|;
}elsif($agInterfaceType eq '4'){
	print qq|			width: 64,\n|;
}
print <<HTML;
			value: (isNaN(prm_record.data.grid_len))?'':prm_record.data.grid_len,
			disabled: (prm_record.data.grid=='1')?false:true,
			hidden: (prm_record.data.grid=='1')?false:true,
			hideTrigger : is_iPad(),
			triggerAction: 'all',
			store: new Ext.data.SimpleStore({
				fields: ['disp', 'value'],
				data : [
					['1mm', 1],
					['5mm', 5],
					['10mm', 10],
					['50mm', 50],
					['100mm', 100]
				]
			}),
			listeners: {
				'render': function(combo){
					try{
						if(prm_record.data.grid=='1'){
							Ext.get('ag-command-grid-len-label').show(false);
						}else{
							Ext.get('ag-command-grid-len-label').hide(false);
						}
					}catch(e){}
				},
				'select' : function(combo, record, index) {
					var prm_record = ag_param_store.getAt(0);
					prm_record.beginEdit();
					prm_record.set('grid_len', record.data.value);
					prm_record.endEdit();
					prm_record.commit();
					updateAnatomo();
				},
				scope:this
			}
		});

		if(aCB) (aCB)();
//	}catch(e){
//		_dump("anatomography_image_render():"+e);
//	}
};


function ag_init(){
//_dump("ag_init():["+Ext.isEmpty(gParams.tp_ap)+"]");

	if(!Ext.isEmpty(gParams.tp_md) && gParams.tp_md == 1){
		gDispAnatomographyPanel = true;
		var anatomography_image = new Ext.Panel({
			contentEl  : 'anatomography-image-contentEl',
			id         : 'anatomography-image',
			region     : 'center',
			autoScroll : false,
			border     : false,
			bodyStyle  : 'background-color:#f8f8f8;overflow:hidden;',
			listeners : {
				"render": function(comp){
					comp.loadMask = new Ext.LoadMask(comp.body,{removeMask:false});
					setTimeout(function(){ comp.loadMask.show(); },0);
					anatomography_image_render(comp,undefined,function(){
						anatomography_init();
						setImageWindowSize();
						comp.loadMask.hide();
					});
				},
				scope:this
			}
		});

		var viewport = new Ext.Viewport({
			layout:'border',
			monitorResize:true,
			items:anatomography_image,
			listeners : {
				'resize' : function(){
				},scope:this
			}
		});
		makeRotImgDiv();

		Ext.get('ag-copyright').removeClass('x-hide-display');
		Ext.getDom('ag-copyright-link').setAttribute("href",location.pathname+"?tp_ap="+encodeURIComponent(gParams.tp_ap));
	}

	if(gParams && !Ext.isEmpty(gParams.tp_ap)){
		try{var position = Ext.getCmp('positionSelect').getValue();}catch(e){}
		var f_ids = [];
		var t_type = '3';
		var tpap_param = analyzeTPAP(gParams.tp_ap);
		if(tpap_param && ((tpap_param.parts && tpap_param.parts.length>0) || (tpap_param.point_parts && tpap_param.point_parts.length>0) || (tpap_param.pins && tpap_param.pins.length>0))){

			var tgi_version = null;
			if(tpap_param.common && tpap_param.common.bp3d_version){
//_dump("ag_init():tpap_param.common.bp3d_version=["+tpap_param.common.bp3d_version+"]");
				tgi_version = tpap_param.common.bp3d_version;
				var tg_id = tpap_param.common.tg_id ? tpap_param.common.tg_id : undefined;
				if(tg_id==undefined && tpap_param.common.model && model2tg[tpap_param.common.model]) tg_id = model2tg[tpap_param.common.model].tg_id;
				if(tg_id==undefined && version2tg[tgi_version]) tg_id = version2tg[tgi_version].tg_id;
				if(tg_id && (!version2tg[tgi_version] || version2tg[tgi_version].tgi_delcause)){
					if(Ext.isEmpty(latestversion[tg_id])) return;
					tgi_version = latestversion[tg_id];
				}

//_dump("ag_init():tgi_version=["+tgi_version+"]");

				var cmp = Ext.getCmp('bp3d-version-combo');
				if(cmp && cmp.rendered) cmp.setValue(tgi_version);
				var cmp = Ext.getCmp('anatomo-version-combo');
				if(cmp && cmp.rendered) cmp.setValue(tgi_version);
			}

			if(tpap_param.common && tpap_param.common.treename){
				if(tpap_param.common.treename=='isa'){
					t_type = '3';
				}else if(tpap_param.common.treename=='partof'){
					t_type = '4';
				}
				var cmp = Ext.getCmp('bp3d-tree-type-combo');
				if(cmp && cmp.rendered) cmp.setValue(t_type);
				var cmp = Ext.getCmp('bp3d-tree-type-combo-ag');
				if(cmp && cmp.rendered) cmp.setValue(t_type);
			}

			if(tpap_param.parts && tpap_param.parts.length>0){
//_dump("ag_init():tpap_param.parts.length=["+tpap_param.parts.length+"]");
				for(var i=0,len=tpap_param.parts.length;i<len;i++){
//_dump("ag_init():["+i+"]:id=["+tpap_param.parts[i].id+"]");
//_dump("ag_init():["+i+"]:f_id=["+tpap_param.parts[i].f_id+"]");
					if(tpap_param.parts[i].id){
						if(Ext.isEmpty(tpap_param.parts[i].version)){
							f_ids.push({f_id:tpap_param.parts[i].id});
						}else{
							f_ids.push({f_id:tpap_param.parts[i].id,version:tpap_param.parts[i].version});
						}
					}else if(tpap_param.parts[i].f_id){
						if(Ext.isEmpty(tpap_param.parts[i].version)){
							f_ids.push({f_id:tpap_param.parts[i].f_id});
						}else{
							f_ids.push({f_id:tpap_param.parts[i].f_id,version:tpap_param.parts[i].version});
						}
					}
				}
			}
//_dump("ag_init():f_ids.length=["+f_ids.length+"]");

			if(tpap_param.point_parts && tpap_param.point_parts.length>0){
				for(var i=0,len=tpap_param.point_parts.length;i<len;i++){
					if(tpap_param.point_parts[i].id){
						if(Ext.isEmpty(tpap_param.point_parts[i].version)){
							f_ids.push({f_id:tpap_param.point_parts[i].id});
						}else{
							f_ids.push({f_id:tpap_param.point_parts[i].id,version:tpap_param.point_parts[i].version});
						}
					}else if(tpap_param.point_parts[i].f_id){
						if(Ext.isEmpty(tpap_param.point_parts[i].version)){
							f_ids.push({f_id:tpap_param.point_parts[i].f_id});
						}else{
							f_ids.push({f_id:tpap_param.point_parts[i].f_id,version:tpap_param.point_parts[i].version});
						}
					}
				}
			}
//_dump("ag_init():f_ids.length=["+f_ids.length+"]");
			if(f_ids.length>0){
				var params = {
					objs : Ext.util.JSON.encode(f_ids)
				};
//_dump("ag_init():params.objs=["+params.objs+"]");
				if(!Ext.isEmpty(position)) params.position = position;
				if(tgi_version){
					params.version = tgi_version;
				}
//_dump("ag_init():params.version=["+params.version+"]");
				if(tpap_param.common && tpap_param.common.model){
					params.model = tpap_param.common.model;
				}

				params.t_type = t_type;
//				bp3d_contents_store.on('load',load_bp3d_contents_store,this,{single:true});
//				bp3d_contents_store.load({params:params});

				bp3d_contents_load_store.on('load',load_bp3d_contents_store,this,{single:true});
				bp3d_contents_load_store.load({params:params});

			}else{

				var runner = new Ext.util.TaskRunner();
				var task = {
					run: function(){
						var contents_tabs = Ext.getCmp('contents-tab-panel');
						if(contents_tabs){
							runner. stop(this);
							load_bp3d_contents_store(bp3d_contents_load_store,[],{});
						}
					},
					interval: 1000 //1 second
				}
				runner.start(task);

//				setTimeout(function(){
//					load_bp3d_contents_store(bp3d_contents_load_store,[],{});
//				},5000);
			}
		}
	}
}



function get_bp3d_contents_store_fields(){
	return [
		'id',
		'pid',
		't_type',
		'name',
		'src',
		'srcstr',
		'f_id',
		'b_id',
		'common_id',
		'name_j',
		'name_e',
		'name_k',
		'name_l',
		'syn_j',
		'syn_e',
		'def_e',
		'organsys_j',
		'organsys_e',
		'organsys',
		'phase',
		{name:'xmin',   type:'float'},
		{name:'xmax',   type:'float'},
		{name:'ymin',   type:'float'},
		{name:'ymax',   type:'float'},
		{name:'zmin',   type:'float'},
		{name:'zmax',   type:'float'},
		{name:'volume', type:'float'},
		{name:'density', type:'float'},
		'used_parts',
		{name:'used_parts_num',type:'int'},
		'density_icon',
		'density_ends',
		{name:'density_ends_num',type:'int'},
		{name:'primitive',type:'boolean'},
		'taid',
		'physical',
		{name:'phy_id',type:'int'},
		'segment',
		'seg_color',
		'seg_thum_bgcolor',
		'seg_thum_bocolor',
		{name:'seg_id',type:'int'},
		'lsdb_term',
		'version',
		{name:'tg_id',type:'int',convert:function(v,r){
			if(Ext.isEmpty(v)){
				return r.md_id;
			}else{
				return v;
			}
		}},
		{name:'tgi_id',type:'int',convert:function(v,r){
			if(Ext.isEmpty(v)){
				return r.mv_id;
			}else{
				return v;
			}
		}},
		{name:'bul_id',type:'int'},
		{name:'cb_id',type:'int'},
		{name:'ci_id',type:'int'},
		{name:'md_id',type:'int'},
		{name:'mv_id',type:'int'},
		{name:'mr_id',type:'int'},
		{name:'but_cnum',type:'int'},
		{name:'icon',type:'string'},

		{name:'tweet_num',type:'int',defaultValue:0},
		{name:'tweets',type:'auto'},
		'mca_id',

		'model',
		'model_version',
		'concept_info',
		'concept_build',
		'buildup_logic',
		{name:'bu_revision',type:'int'},

		'state',
		'def_color',
		{name:'point',type:'boolean'},
		'elem_type',
		'point_label',
		'point_parent',
		'point_children',
		{name:'entry', type:'date', dateFormat:'timestamp'},
		{name:'lastmod', type:'date', dateFormat:'timestamp'},
HTML
if($lsdb_Auth){
print <<HTML;
		'delcause',
		'm_openid',
HTML
}
print <<HTML;
		'search_c_path',
		'c_path',
		'u_path',
		'is_a',
		'part_of',
		'has_part',
		'is_a_path2root',
		'is_a_brother',
		'is_a_children',
		'partof_path2root',
		'partof_path2root_circular',
		'partof_brother',
		'partof_children'
HTML
if($useContentsTree eq 'true'){
	print <<HTML;
		,'style',
		{name:'c_num', type:'int'},
		{name:'tree_depth', type:'int'}
HTML
}
print <<HTML;
	];
}

bp3d_contents_store = new Ext.data.JsonStore({
	url: 'get-contents.cgi',
	pruneModifiedRecords : true,
	root: 'images',
	fields: get_bp3d_contents_store_fields(),
	listeners: {
		'beforeload' : {
			fn:function(self,options){
//				_dump("bp3d_contents_store.beforeload()");
				try{
					self.baseParams = self.baseParams || {};
					delete gParams.parent;
					if(!Ext.isEmpty(gParams.parent)) self.baseParams.parent = gParams.parent;
					self.baseParams.lng = gParams.lng;

					delete self.baseParams.t_type;
					try{var treeType = Ext.getCmp('bp3d-tree-type-combo').getValue();}catch(e){treeType=undefined;}
					if(!Ext.isEmpty(treeType)) self.baseParams.t_type = treeType;

					try{var position = Ext.getCmp('positionSelect').getValue();}catch(e){position=undefined;}
					if(!Ext.isEmpty(position)) self.baseParams.position = position;

					self.baseParams.sorttype = '';
					try{var bp3d_sorttype = Ext.getCmp('sortSelect').getValue();}catch(e){_dump("bp3d_contents_store.beforeload():e=["+e+"]");bp3d_sorttype=undefined;}
					if(!Ext.isEmpty(bp3d_sorttype)) self.baseParams.sorttype = bp3d_sorttype;


					delete self.baseParams.version;
					if(options.params && options.params.version){
						self.baseParams.version = options.params.version;
						init_bp3d_version = options.params.version;
					}else{
						try{
							self.baseParams.version = Ext.getCmp('bp3d-version-combo').getValue();
						}catch(e){
							_dump("bp3d_contents_store.beforeload():e=["+e+"]");
						}
					}
					if(Ext.isEmpty(self.baseParams.version)) self.baseParams.version = init_bp3d_version;

					try{var detailEl = Ext.getCmp('img-detail-panel').body;}catch(e){}
					try{var commentDetailEl = Ext.getCmp('comment-detail-panel').body;}catch(e){}

					if(detailEl) detailEl.update('$LOADING_MSG');
					if(commentDetailEl) commentDetailEl.update('$LOADING_MSG');

					var bp3d_contents_detail_annotation_panel = Ext.getCmp('bp3d-contents-detail-annotation-panel');
					if(bp3d_contents_detail_annotation_panel){
						bp3d_contents_detail_annotation_panel.disable();
						if(bp3d_contents_detail_annotation_panel.bottomToolbar) bp3d_contents_detail_annotation_panel.bottomToolbar.disable();
					}
HTML
if($useContentsTree eq 'true'){
	print <<HTML;
					var bp3d_tree_depth_combo = Ext.getCmp('bp3d-tree-depth-combo');
					if(bp3d_tree_depth_combo) bp3d_tree_depth_combo.disable();
HTML
}
print <<HTML;
//					for(var key in self.baseParams){
//						_dump("bp3d_contents_store.beforeload():["+key+"]=["+self.baseParams[key]+"]");
//					}

					for(var key in init_bp3d_params){
						if(key.match(/_id\$/)) self.baseParams[key] = init_bp3d_params[key];
					}

					try{var treeType = Ext.getCmp('bp3d-tree-type-combo').getValue();}catch(e){treeType=undefined;}
					if(!Ext.isEmpty(treeType)) self.baseParams.bul_id = treeType;

					try{
						var store = Ext.getCmp('bp3d-version-combo').getStore();
						var idx = store.findBy(function(record,id){
							if(record.data.tgi_version==self.baseParams.version) return true;
						});
						if(idx>=0){
							var record = store.getAt(idx);
							if(record){
								self.baseParams.md_id = record.data.md_id;
								self.baseParams.mv_id = record.data.mv_id;
								self.baseParams.mr_id = record.data.mr_id;
								self.baseParams.ci_id = record.data.ci_id;
								self.baseParams.cb_id = record.data.cb_id;
							}
						}
					}catch(e){}


					self.baseParams.degenerate_same_shape_icons = false;
					if(\$("input#bp3d-content-panel-header-content-degenerate-same-shape-icons:checked").val()) self.baseParams.degenerate_same_shape_icons = true;
//					console.log("self.baseParams.degenerate_same_shape_icons=["+self.baseParams.degenerate_same_shape_icons+"]");

				}catch(e){
					_dump("bp3d_contents_store.beforeload():"+e);
				}
			},
			scope:this
		},
		'datachanged':{
			fn:function(self){
//				_dump("bp3d_contents_store.datachanged()");
				try{
//					var bp3d_contents_dataview = Ext.getCmp('bp3d-contents-dataview');
					var bp3d_contents_dataview = getViewImages();
					if(bp3d_contents_dataview){
						setTimeout(function(){
							try{
								bp3d_contents_dataview.show();
								var num = -1;
								var id = null;
								var fmaid = Cookies.get('ag_annotation.images.fmaid');
//								_dump("bp3d_contents_store.datachanged():fmaid=["+fmaid+"]");
								if(fmaid){
									num = self.find("f_id",fmaid);
									if(num<0){
//										Cookies.set('ag_annotation.images.fmaid','');
									}else{
//										var record = self.getAt(num);
//										if(record) id = record.data.id;
									}
								}
//								_dump("bp3d_contents_store.datachanged():fmaid=["+fmaid+"]["+num+"]");
								if(num<0){
									num = 0;
								}
								if(num>=0){
									bp3d_contents_dataview.select(num);
/*
									var element = bp3d_contents_dataview.getEl();
									if(element){
										element.dom.scrollTop = 0;
										var dom = Ext.getDom("contents_"+id);
										if(id && dom){
											element.dom.parentNode.scrollTop = dom.offsetTop - 4;
										}else{
											element.dom.parentNode.scrollTop = 0;
										}
									}
*/
									var element = bp3d_contents_dataview.getEl();
									if(element){
										element.dom.scrollTop = 0;
										var nodes = bp3d_contents_dataview.getSelectedNodes();
										if(nodes && nodes.length){
											var dom = nodes[0];
											if(dom){
												element.dom.parentNode.scrollTop = dom.offsetTop - 4;
											}else{
												element.dom.parentNode.scrollTop = 0;
											}
										}
									}

								}else{
									showDetails();
								}
								var chooserCmp = Ext.getCmp('img-chooser-view');
								var detailCmp = Ext.getCmp('img-detail-panel');
								var chooserEl = chooserCmp.body;
								var filterCmp = Ext.getCmp('filter');
								var sortCmp = Ext.getCmp('sortSelect');
								var positionCmp = Ext.getCmp('positionSelect');
								var disptypeCmp = Ext.getCmp('disptypeSelect');
HTML
if($useContentsTree eq 'true'){
	print <<HTML;
								var bp3d_tree_depth_combo = Ext.getCmp('bp3d-tree-depth-combo');
HTML
}
print <<HTML;
								var addcommentCmp = Ext.getCmp('btn-add-comment');

								if(bp3d_contents_dataview.store.getRange().length>0){
									if(chooserCmp) chooserCmp.show();
									if(detailCmp) detailCmp.show();
									if(chooserEl) chooserEl.show();
									if(filterCmp) filterCmp.enable();
									if(sortCmp) sortCmp.enable();
									if(positionCmp) positionCmp.enable();
									if(disptypeCmp) disptypeCmp.enable();
HTML
if($useContentsTree eq 'true'){
	print <<HTML;
									if(bp3d_tree_depth_combo && disptypeCmp && disptypeCmp.getValue()=='tree'){
										bp3d_tree_depth_combo.enable();
										if(filterCmp) filterCmp.disable();
										if(sortCmp) sortCmp.disable();
									}
HTML
}
print <<HTML;
									if(addcommentCmp) addcommentCmp.enable();
								}else{
									if(addcommentCmp) addcommentCmp.disable();
								}

							}catch(e){alert(e)}
						},250);
					}
				}catch(e){
					_dump("bp3d_contents_store.datachanged():"+e);
				}
			},scope:this},
		'load': {
			fn: function(store,records){

//				_dump("bp3d_contents_store.load("+records.length+")");
				if(store.reader.jsonData){
//					_dump(store.reader.jsonData);
					for(var key in store.reader.jsonData){
						if(
							typeof store.reader.jsonData[key] != 'number' &&
							typeof store.reader.jsonData[key] != 'string' &&
							typeof store.reader.jsonData[key] != 'boolean'
						) continue;
						init_bp3d_params[key] = store.reader.jsonData[key];
//						_dump("bp3d_contents_store.load():["+key+"]=["+init_bp3d_params[key]+"]["+(typeof init_bp3d_params[key])+"]");
					}
				}
				var buildup_logic = ' Tree of ';
				var ci_name = 'FMA';
				var cb_name = '3.0';
				if(store.reader.jsonData.ci_name) ci_name = store.reader.jsonData.ci_name;
				if(store.reader.jsonData.cb_name) cb_name = store.reader.jsonData.cb_name;
				Ext.get('bp3d-buildup-logic-contents-label').update((init_bp3d_params.bul_id==3 ? 'IS-A' : 'HAS-PART')+buildup_logic+ci_name+cb_name);

				Ext.get('bp3d-concept-info-label').update(ci_name);
				Ext.get('bp3d-concept-build-label').update(cb_name);

				try{filter_func();}catch(e){}
			},scope:this
		},
		'loadexception': {
			fn:function(){

Ext.get('bp3d-buildup-logic-contents-label').update('');

				_dump("bp3d_contents_store.loadexception()");
				try{
					var viewport = Ext.getCmp('viewport');
					if(viewport && viewport.loadMask){
						viewport.loadMask.hide();
						delete viewport.loadMask;
						var contents_tabs = Ext.getCmp('contents-tab-panel');
						if(contents_tabs) contents_tabs.setActiveTab('contents-tab-bodyparts-panel');
					}
				}catch(e){}
				try{
//					var bp3d_contents_dataview = Ext.getCmp('bp3d-contents-dataview');
					var bp3d_contents_dataview = getViewImages();
					if(bp3d_contents_dataview) bp3d_contents_dataview.hide();

					var chooserEl = Ext.getCmp('img-chooser-view').body;
					if(chooserEl) chooserEl.hide();
					try{
						var detailEl = Ext.getCmp('img-detail-panel').body;
						if(detailEl) detailEl.update('');
					}catch(e){}

					var filterCmp = Ext.getCmp('filter');
					if(filterCmp) filterCmp.disable();

					var sortCmp = Ext.getCmp('sortSelect');
					if(sortCmp) sortCmp.disable();

					var positionCmp = Ext.getCmp('positionSelect');
					if(positionCmp) positionCmp.disable();

					var disptypeCmp = Ext.getCmp('disptypeSelect');
					if(disptypeCmp) disptypeCmp.disable();

HTML
if($useContentsTree eq 'true'){
	print <<HTML;
					var bp3d_tree_depth_combo = Ext.getCmp('bp3d-tree-depth-combo');
					if(bp3d_tree_depth_combo) bp3d_tree_depth_combo.disable();
HTML
}
print <<HTML;

					var addcommentCmp = Ext.getCmp('btn-add-comment');
					if(addcommentCmp) addcommentCmp.disable();
				}catch(e){
					_dump("bp3d_contents_store.loadexception():"+e);
				}
			},scope:this
		}
	}
});

bp3d_contents_load_store = new Ext.data.JsonStore({
	url: 'get-contents.cgi',
	pruneModifiedRecords : true,
	root: 'images',
	fields: get_bp3d_contents_store_fields(),
	listeners: {
		'beforeload' : {
			fn:function(self,options){
				_dump("bp3d_contents_load_store.beforeload()");
				_dump(options);
				try{
					self.baseParams = self.baseParams || {};
					delete gParams.parent;
					if(!Ext.isEmpty(gParams.parent)) self.baseParams.parent = gParams.parent;
					self.baseParams.lng = gParams.lng;

					delete self.baseParams.t_type;
					try{var treeType = Ext.getCmp('bp3d-tree-type-combo').getValue();}catch(e){treeType=undefined;}
					if(!Ext.isEmpty(treeType)) self.baseParams.t_type = treeType;

					try{var position = Ext.getCmp('positionSelect').getValue();}catch(e){position=undefined;}
					if(!Ext.isEmpty(position)) self.baseParams.position = position;

					self.baseParams.sorttype = '';
					try{var bp3d_sorttype = Ext.getCmp('sortSelect').getValue();}catch(e){_dump("bp3d_contents_store.beforeload():e=["+e+"]");bp3d_sorttype=undefined;}
					if(!Ext.isEmpty(bp3d_sorttype)) self.baseParams.sorttype = bp3d_sorttype;

					delete self.baseParams.version;
					if(options.params && options.params.version){
						self.baseParams.version = options.params.version;
						init_bp3d_version = options.params.version;
						try{
							var store = Ext.getCmp('bp3d-version-combo').getStore();
						}catch(e){
							_dump("bp3d_contents_load_store.beforeload():e=["+e+"]");
						}
					}else{
						try{
							self.baseParams.version = Ext.getCmp('bp3d-version-combo').getValue();
						}catch(e){
							_dump("bp3d_contents_load_store.beforeload():e=["+e+"]");
						}
					}
					if(Ext.isEmpty(self.baseParams.version)) self.baseParams.version = init_bp3d_version;

					_dump(self.baseParams);

				}catch(e){
					_dump("bp3d_contents_load_store.beforeload():"+e);
				}
			},
			scope:this
		},
		'datachanged' : {
			fn:function(self,options){
				_dump("bp3d_contents_load_store.datachanged()");
			}
		},
		load: {
			fn:function(store,records){
				_dump("bp3d_contents_load_store.load("+records.length+")");
				if(store.reader.jsonData){
					_dump(store.reader.jsonData);
					for(var key in store.reader.jsonData){
						if(
							typeof store.reader.jsonData[key] != 'number' &&
							typeof store.reader.jsonData[key] != 'string'
						) continue;
						init_bp3d_params[key] = store.reader.jsonData[key];
//						_dump("bp3d_contents_load_store.load():["+key+"]=["+init_bp3d_params[key]+"]["+(typeof init_bp3d_params[key])+"]");
					}
				}
			}
		},
		' loadexception' : {
			fn:function(self,records){
				_dump("bp3d_contents_load_store.loadexception()");
			}
		}
	}
});





var ag_put_usersession_task = new Ext.util.DelayedTask(function(){
//_dump("ag_put_usersession_task():["+makeAnatomoPrm()+"]");
//_dump("ag_put_usersession_task():["+makeAnatomoPrm(2)+"]");
	Ext.Ajax.request({
		url       : 'put-usersession.cgi',
		method    : 'POST',
		params    : {
			info  : makeAnatomoPrm(2),
			state : Ext.util.JSON.encode(glb_us_state),
			keymap : Ext.util.JSON.encode(glb_us_keymap)
		},
		success   : function(conn,response,options,aParam){
//			_dump("ag_put_usersession_task():put-usersession.cgi:success");
		},
		failure : function(conn,response,options){
//			_dump("ag_put_usersession_task():put-usersession.cgi:failure");
		}
	});
});

var ag_keymap_fields = [
	{name : 'order', type : 'int'},
	{name : 'key',   type : 'string'},
	{name : 'code',  type : 'int'},
	{name : 'shift', type : 'boolean', defaultValue : false},
	{name : 'ctrl',  type : 'boolean', defaultValue : false},
	{name : 'alt',   type : 'boolean', defaultValue : false},
	{name : 'stop',  type : 'boolean', defaultValue : true},
	{name : 'cmd',   type : 'string'}
];

var ag_keymap_store = new Ext.data.JsonStore({
	root   : 'keymaps',
	fields : ag_keymap_fields,
	sortInfo : {
		field     : 'order',
		direction : 'ASC'
	},
	totalProperty : glb_us_keymap.length,
	data : {
		keymaps : glb_us_keymap
	},
	listeners : {
		'add' : function(store,records,index){
//			_dump("ag_keymap_store:add()");
		},
		'remove' : function(store,record,index){
//			_dump("ag_keymap_store:remove()");
		},
		'update' : function(store,record,operation){
//			_dump("ag_keymap_store:update()");
		}
	}
});
//_dump("ag_keymap_store=["+ag_keymap_store.getCount()+"]");



function agKeyMapCB(k,e){
	var contents_tabs = Ext.getCmp('contents-tab-panel');
	if(contents_tabs.getActiveTab().id != 'contents-tab-anatomography-panel') return;
	var shiftKey = e.shiftKey?true:false;
	var ctrlKey = e.ctrlKey?true:false;
	var altKey = e.altKey?true:false;
	var index = ag_keymap_store.findBy(function(record,id){
		var key = record.get('key');
		var code = Ext.EventObject[key];
		var shift = record.get('shift');
		var ctrl = record.get('ctrl');
		var alt = record.get('alt');
		return (k==code && shift==shiftKey && ctrl==ctrlKey && alt==altKey)?true:false;
	});
//	_dump("agKeyMapCB():index=["+index+"]");
	if(index<0) return;
	var record = ag_keymap_store.getAt(index);
	var cmd = record.get('cmd');
	var stop = record.get('stop');
	var cmp = cmd?Ext.getCmp(cmd):undefined;
	if(!cmp) return;
	if(cmp.xtype=='checkbox'){
		cmp.show();
		cmp.setChecked(cmp.checked?false:true)
		cmp.hide();
		if(stop) e.stopEvent();
	}else{
		if(cmp.fireEvent('click',cmp) && stop) e.stopEvent();
	}
}
var agKeyMapNames = [];
var agKeyMapNameToCode = {};
var agKeyMapCodeToName = {};
for(var key in Ext.EventObject){
	if(typeof Ext.EventObject[key] != 'number') continue;
	switch (key){
		case 'button':
		case 'A':
		case 'B':
		case 'C':
		case 'D':
		case 'E':
		case 'F':
		case 'G':
		case 'H':
		case 'I':
		case 'J':
		case 'K':
		case 'L':
		case 'M':
		case 'N':
		case 'O':
		case 'P':
		case 'Q':
		case 'R':
		case 'S':
		case 'T':
		case 'U':
		case 'V':
		case 'W':
		case 'X':
		case 'Y':
		case 'Z':
		case 'ZERO':
		case 'ONE':
		case 'TWO':
		case 'THREE':
		case 'FOUR':
		case 'FIVE':
		case 'SIX':
		case 'SEVEN':
		case 'EIGHT':
		case 'NINE':
		case 'NUM_ZERO':
		case 'NUM_ONE':
		case 'NUM_TWO':
		case 'NUM_THREE':
		case 'NUM_FOUR':
		case 'NUM_FIVE':
		case 'NUM_SIX':
		case 'NUM_SEVEN':
		case 'NUM_EIGHT':
		case 'NUM_NINE':
		case 'ALT':
		case 'CONTROL':
		case 'SHIFT':
			continue
	}
	agKeyMapNames.push(key);
	agKeyMapCodeToName[Ext.EventObject[key]] = key;
	agKeyMapNameToCode[key] = {
		code : Ext.EventObject[key]
	};
}
agKeyMapNames.sort();

var agKeyMap;
function agKeyMapExec(){
	if(window.agKeyMap){
		window.agKeyMap.disable();
		window.agKeyMap = undefined;
		delete window.agKeyMap;
	}
	var hash = {};
	var hash_key;
	var KeyMapConfig = [];
	var len = ag_keymap_store.getCount();
	var i;
	for(i=0;i<len;i++){
		var record = ag_keymap_store.getAt(i);
		var key = record.get('key');
		var code = Ext.EventObject[key];
		var shift = record.get('shift');
		var ctrl = record.get('ctrl');
		var alt = record.get('alt');
		var stop = record.get('stop');
//		_dump("["+i+"]:["+key+"]["+code+"]["+shift+"]["+ctrl+"]["+alt+"]["+stop+"]");
		hash_key = code;
		hash_key += '\t'+shift;
		hash_key += '\t'+ctrl;
		hash_key += '\t'+alt;
		hash_key += '\t'+stop;
		if(hash[hash_key]) continue;
		KeyMapConfig.push({
			key       : code,
			shift     : shift,
			ctrl      : ctrl,
			alt       : alt,
			fn        : agKeyMapCB,
			scope     : this,
			stopEvent : stop
		});
		hash[hash_key] = true;
	}
	window.agKeyMap = new Ext.KeyMap(document, KeyMapConfig);
	KeyMapConfig = undefined;
}
agKeyMapExec();
HTML
=pod
Ext.BLANK_IMAGE_URL = "resources/images/default/s.gif";

var _dump = function(aStr){
	if(window.dump) window.dump("main.cgi:"+aStr+"\\n")
	try{if(console && console.log) console.log(aStr);}catch(e){}
};

captureEvents = function(observable) {
	Ext.util.Observable.capture(
		observable,
		function(eventName) {
			_dump(eventName);
		},
		this
	);
};

var Cookies = {};
Cookies.set = function(aKey, aVal, aExpires){
//	if(aKey=="ag_annotation.images.type"){
//		_dump("Cookies.set():["+aKey+"]["+aVal+"]["+aExpires+"]");
//	}
	if(aExpires == undefined) aExpires = true;
	if(aExpires){
		var xDay = new Date;
		xDay.setDate(xDay.getDate() + 30); //30 Days after
		xDay = xDay.toGMTString(); //GMT format
		document.cookie = aKey + '=' + escape(aVal) + '; expires=' + xDay + ';';
	}else{
		document.cookie = aKey + '=' + escape(aVal) + ';';
	}
}

Cookies.get = function(name,defvalue){
	if(defvalue == undefined) defvalue = null;
	var arg = name + "=";
	var alen = arg.length;
	var clen = document.cookie.length;
	var i = 0;
	var j = 0;
	while(i < clen){
		j = i + alen;
		if (document.cookie.substring(i, j) == arg){
			var rtnval = Cookies.getCookieVal(j);
//			if(name=="ag_annotation.images.type"){
//				_dump("Cookies.set():["+name+"]["+defvalue+"]["+rtnval+"]");
//			}
			if(rtnval == "") rtnval = defvalue;
			return rtnval;
		}
		i = document.cookie.indexOf(" ", i) + 1;
		if(i == 0)
			break;
	}
//	if(name=="ag_annotation.images.type"){
//		_dump("Cookies.set():["+name+"]["+defvalue+"]");
//	}
	return defvalue;
};

Cookies.clear = function(name) {
//	_dump("Cookies.clear():["+name+"]");
	if(Cookies.get(name)){
		document.cookie = name + "=" +
			"; expires=Thu, 01-Jan-70 00:00:01 GMT";
	}
};

Cookies.getCookieVal = function(offset){
	var endstr = document.cookie.indexOf(";", offset);
	if(endstr == -1){
		endstr = document.cookie.length;
	}
	return unescape(document.cookie.substring(offset, endstr));
};

/////////////////////////////////////////////////////////////////////////////////////////////////////
function anatomo_fixlen_format (num, len) {
	var retStr = num + "";
	while(retStr.length < len) {
		retStr = "0" + retStr;
	}
	return retStr;
}

function anatomo_float_format (num) {
	var scalar = num.toString();
	if (scalar == "NaN") {
		return "NANANANANANA";
	}
	if (scalar.indexOf("e-", 0) >= 0) {
		scalar = "0.0";
	}
	var nums = new Array();
	if (scalar.indexOf(".", 0) >= 0) {
		nums = scalar.split(".");
	} else {
		nums[0] = scalar;
		nums[1] = "";
	}
	var fMinus = false;
	if (nums[0].indexOf("-", 0) >= 0) {
		fMinus = true;
		nums[0] = nums[0].replace("-", "");
	}
	if (nums[0] > 65535) {
		nums[0] = 65535;
	}
	while (nums[0].length < 5) {
		nums[0] = "0" + nums[0];
	}
	while (nums[1].length < 5) {
		nums[1] = nums[1] + "0";
	}
	if (nums[1].length > 5) {
		nums[1] = nums[1].substr(0, 5);
	}
	if (fMinus) {
		return "M" + nums[0] + "." + nums[1];
	} else {
		return "P" + nums[0] + "." + nums[1];
	}
}

function AGVec3d (x, y, z) {
	this.x = x;
	this.y = y;
	this.z = z;
}


function agDifferenceD3 (v0, v1, out) {
	out.x = parseFloat(v0.x) - parseFloat(v1.x);
	out.y = parseFloat(v0.y) - parseFloat(v1.y);
	out.z = parseFloat(v0.z) - parseFloat(v1.z);
}

function agInnerProductD3 (v0, v1) {
	return parseFloat(v0.x * v1.x) + parseFloat(v0.y * v1.y) + parseFloat(v0.z * v1.z);
}

function agOuterProductD3 (v0, v1, out) {
	out.x = parseFloat(v0.y * v1.z) - parseFloat(v1.y * v0.z);
	out.y = parseFloat(v0.z * v1.x) - parseFloat(v1.z * v0.x);
	out.z = parseFloat(v0.x * v1.y) - parseFloat(v1.x * v0.y);
}

function agNormalizeD3 (v0, out) {
	var len;
	len = parseFloat(v0.x * v0.x) + parseFloat(v0.y * v0.y) + parseFloat(v0.z * v0.z);
	len = Math.sqrt(len);
	if (len == 0) {
		return false;
	}
	out.x = v0.x / len;
	out.y = v0.y / len;
	out.z = v0.z / len;
	return true;
}

function agCopyD3 (v0, out) {
	out.x = v0.x;
	out.y = v0.y;
	out.z = v0.z;
}

function agIsZero (x) {
	return (((parseFloat(x)<parseFloat(m_ag.epsilon)) && (parseFloat(x)>(-parseFloat(m_ag.epsilon)))) ? true : false);
}

function agDeg2Rad (deg) {
	return deg * m_ag.PI / 180;
}

function agRad2Deg (rad) {
	return rad * 180 / m_ag.PI;
}




function getCameraPos () {
	return m_ag.cameraPos;
}

function getTargetPos () {
	return m_ag.targetPos;
}

function getYRange () {
	return m_ag.orthoYRange;
}

function getYRangeFromServer(aCB) {
	var img = document.getElementById("clipImg");
	var urlStr = img.src;
	urlStr = urlStr.replace(/^[^\?]+/,"getYRange.cgi");

	var yRange = "";
	Ext.Ajax.request({
		url: urlStr,
		success : function (response, options) {
			yRange = response.responseText;

			YRangeFromServer = parseFloat(yRange);
			if(aCB) (aCB)(YRangeFromServer);
		},
		failure : function (response, options) {
		}
	});
}

function getNear () {
	return m_ag.nearClip;
}

function getFar () {
	return m_ag.farClip;
}

function calcRotateDeg () {
	var CTx = m_ag.targetPos.x - m_ag.cameraPos.x;
	var CTy = m_ag.targetPos.y - m_ag.cameraPos.y;
	var CTz = m_ag.targetPos.z - m_ag.cameraPos.z;

	// Calculate Rotate H
	var radH = Math.acos(CTy / Math.sqrt(CTx*CTx + CTy * CTy));
	var degH = radH / Math.PI * 180;
	if (CTx > 0) degH = 360 - degH;
	while (degH >= 360) {
		degH = degH - 360;
	}
	if (m_ag.upVec.z < 0) {
		degH = degH + 180;
		while (degH >= 360) {
			degH = degH - 360;
		}
	}

	// Calculate Rotate V
	var UnitX = -1 * Math.sin(degH / 180 * Math.PI);
	var UnitY = Math.cos(degH / 180 * Math.PI);
	var UnitZ = 0;
	var radV = Math.acos((CTx * UnitX + CTy * UnitY + CTz * UnitZ) / Math.sqrt((CTx * CTx + CTy * CTy + CTz * CTz) * (UnitX * UnitX + UnitY * UnitY + UnitZ * UnitZ)));
	if(isNaN(radV)) radV = 0;
	var degV = radV / Math.PI * 180;
	if (CTz > 0) degV = 360 - degV;
	while (degV >= 360) {
		degV = degV - 360;
	}

	degH = Math.round(degH);
	degV = Math.round(degV);

	while (degH >= 360) {
		degH = degH - 360;
	}
	while (degV >= 360) {
		degV = degV - 360;
	}

//	if(degV%15) degV += (degV%15)>=8?(15-(degV%15)):(degV%15)-15;
//	if(degH%15) degH += (degH%15)>=8?(15-(degH%15)):(degH%15)-15;

//	while (degH >= 360) {
//		degH = degH - 360;
//	}
//	while (degV >= 360) {
//		degV = degV - 360;
//	}

	return {H:degH,V:degV};
}

function calcCameraPos () {
	var eyeLongitudeRadian = agDeg2Rad(m_ag.longitude);
	var eyeLatitudeRadian = agDeg2Rad(m_ag.latitude);
	var eyeTargetDistance = m_ag.distance;

	var target = m_ag.targetPos;
	var eye = m_ag.cameraPos;
	var yAxis = m_ag.upVec;

	var zAxis = new AGVec3d(null, null, null);
	var xAxis = new AGVec3d(null, null, null);
	var tmp0 = new AGVec3d(null, null, null);
	var remind;

	var cEyeLongitude = Math.cos(eyeLongitudeRadian);
	var sEyeLongitude = Math.sin(eyeLongitudeRadian);
	var cEyeLatitude = Math.cos(eyeLatitudeRadian);
	var sEyeLatitude = Math.sin(eyeLatitudeRadian);

	zAxis.x = cEyeLatitude * cEyeLongitude;
	zAxis.y = cEyeLatitude * sEyeLongitude;
	zAxis.z = sEyeLatitude;

	tmp0.x = cEyeLongitude;
	tmp0.y = sEyeLongitude;
	tmp0.z = 0;

	if(parseFloat(zAxis.z) >= parseFloat(m_ag.epsilon)){
		agOuterProductD3( zAxis, tmp0, xAxis );
		agNormalizeD3( xAxis, xAxis );
		agOuterProductD3( zAxis, xAxis, yAxis );
		agNormalizeD3( yAxis, yAxis );
	}
	else if(parseFloat(zAxis.z) < -parseFloat(m_ag.epsilon)){
		agOuterProductD3(tmp0, zAxis, xAxis);
		agNormalizeD3(xAxis, xAxis);
		agOuterProductD3(zAxis, xAxis, yAxis);
		agNormalizeD3(yAxis, yAxis);
	}
	else{ // zAxis.z == 0
		remind =  Math.round(m_ag.latitude) % 360;
		remind = remind < 0 ? -remind : remind;

		if( remind > 175 && remind < 185 ){
			yAxis.x = 0;
			yAxis.y = 0;
			yAxis.z = -1;
		}else{
			yAxis.x = 0;
			yAxis.y = 0;
			yAxis.z = 1;
		}
	}

	eye.x = parseFloat(zAxis.x) * parseFloat(eyeTargetDistance) + parseFloat(target.x);
	eye.y = parseFloat(zAxis.y) * parseFloat(eyeTargetDistance) + parseFloat(target.y);
	eye.z = parseFloat(zAxis.z) * parseFloat(eyeTargetDistance) + parseFloat(target.z);

	var posDif = parseFloat(888.056);
	var tmpDeg = calcRotateDeg();
	if (tmpDeg.H == 0 && tmpDeg.V == 0) {
		m_ag.cameraPos.x = m_ag.targetPos.x;
		m_ag.cameraPos.y = m_ag.targetPos.y - posDif;
		m_ag.cameraPos.z = m_ag.targetPos.z;
	} else if (tmpDeg.H == 90 && tmpDeg.V == 0) {
		m_ag.cameraPos.x = m_ag.targetPos.x + posDif;
		m_ag.cameraPos.y = m_ag.targetPos.y;
		m_ag.cameraPos.z = m_ag.targetPos.z;
	} else if (tmpDeg.H == 180 && tmpDeg.V == 0) {
		m_ag.cameraPos.x = m_ag.targetPos.x;
		m_ag.cameraPos.y = m_ag.targetPos.y + posDif;
		m_ag.cameraPos.z = m_ag.targetPos.z;
	} else if (tmpDeg.H == 270 && tmpDeg.V == 0) {
		m_ag.cameraPos.x = m_ag.targetPos.x - posDif;
		m_ag.cameraPos.y = m_ag.targetPos.y;
		m_ag.cameraPos.z = m_ag.targetPos.z;
	}
}

function setCameraAndTarget (cam, tar, upVec, isInitData) {
	var tc = new AGVec3d(null, null, null);	// camera  -> target
	agDifferenceD3(cam, tar, tc);
	var tc_len = agInnerProductD3(tc, tc);
	tc_len = Math.sqrt(tc_len);
	if (agIsZero(tc_len)) {
		return false;
	}

	var ntc = new AGVec3d(null, null, null);	// |camera  -> target|
	var inv_tc_len = 1 / tc_len;
	ntc.x = tc.x * inv_tc_len;
	ntc.y = tc.y * inv_tc_len;
	ntc.z = tc.z * inv_tc_len;

	var vz = new AGVec3d(0, 0, 1); // zaxis

	// calc latitude
	var latitude = 90;
	if (upVec.z >= 0) {
		latitude = 90 - agRad2Deg(Math.acos(agInnerProductD3(ntc, vz)));
	} else {
		latitude = 90 + agRad2Deg(Math.acos(agInnerProductD3(ntc, vz)));
	}

	// calc longitude
	var longitude = 0;
	var ntc_xy = new AGVec3d(tc.x, tc.y, 0);

	if (agNormalizeD3(ntc_xy, ntc_xy)) {
		var vx = new AGVec3d(1, 0, 0);
		if (upVec.z >= 0) {
		} else {
			ntc_xy.x = -ntc_xy.x;
			ntc_xy.y = -ntc_xy.y;
			ntc_xy.z = 0;
		}
		var tmp = agRad2Deg(Math.acos(agInnerProductD3(ntc_xy, vx)));
		if (ntc_xy.y >= 0) {
			longitude = tmp;
		} else {
			longitude = -tmp;
		}
	} else {
		var vx = new AGVec3d(1, 0, 0);
		var nup_xy = new AGVec3d(null, null, null);
		if (ntc.z >= 0) {
			nup_xy.x = -upVec.x;
			nup_xy.y = -upVec.y;
			nup_xy.z = 0;
		} else {
			nup_xy.x = upVec.x;
			nup_xy.y = upVec.y;
			nup_xy.z = 0;
		}
		if (!agNormalizeD3(nup_xy, nup_xy)) {
		}
		var tmp = agRad2Deg(Math.acos(agInnerProductD3(nup_xy, vx)));
		if (nup_xy.y >= 0) {
			longitude = tmp;
		} else {
			longitude = -tmp;
		}
	}

	m_ag.targetPos.x = tar.x;
	m_ag.targetPos.y = tar.y;
	m_ag.targetPos.z = tar.z;
	m_ag.distance = tc_len;

	m_ag.longitude = longitude;
	m_ag.latitude = latitude;

	calcCameraPos();

	if (isInitData) {
		agCopyD3 (m_ag.targetPos, m_ag.initTargetPos);
		m_ag.initLongitude = m_ag.longitude;
		m_ag.initLatitude = m_ag.latitude;
		m_ag.initDistance = m_ag.distance;
	}
	return true;
}

function setYRange (yRange, isInitData) {
	if (yRange > m_ag.Camera_YRange_Min) {
		m_ag.orthoYRange = yRange;
		if (isInitData) {
			m_ag.initOrthoYRange = yRange;
		}
		return true;
	} else {
		return false;
	}
}

function changeYRange (d, base) {
	var ratio = 1.0;
	if (d > 0) {
		ratio = Math.pow(base, d);
	} else if (d < 0) {
		ratio = Math.pow(base, d);
	}
	var tmp = m_ag.orthoYRange * ratio;
	if (tmp < m_ag.Camera_YRange_Min) {
		tmp = m_ag.Camera_YRange_Min;
	}
	m_ag.orthoYRange = tmp;
}

function setNear (nearClip) {
	m_ag.nearClip = nearClip;
	return true;
}

function setFar (farClip) {
	m_ag.farClip = farClip;
	return false;
}

function addLongitude (d) {
	m_ag.longitude = m_ag.longitude + d;
	calcCameraPos();
}

function addLatitude (d) {
	m_ag.latitude = m_ag.latitude + d;
	calcCameraPos();
}

function moveTargetByMouseForOrtho (winHeight, dx, dy) {
	var rx = -dx * m_ag.orthoYRange / winHeight;
	var ry = dy * m_ag.orthoYRange / winHeight;

	// latitude
	eyeLongitudeRadian = agDeg2Rad(m_ag.longitude);

	// logitude
	eyeLatitudeRadian = agDeg2Rad(m_ag.latitude);

	var cEyeLongitude = Math.cos(eyeLongitudeRadian);
	var sEyeLongitude = Math.sin(eyeLongitudeRadian);
	var cEyeLatitude = Math.cos(eyeLatitudeRadian);
	var sEyeLatitude = Math.sin(eyeLatitudeRadian);

	var zAxis = new AGVec3d(null, null, null);
	var xAxis = new AGVec3d(null, null, null);
	var yAxis = new AGVec3d(null, null, null);
	var tmp0 = new AGVec3d(null, null, null);
	var remind;

	yAxis.x = cEyeLatitude * cEyeLongitude;
	yAxis.y = cEyeLatitude * sEyeLongitude;
	yAxis.z = sEyeLatitude;

	tmp0.x = cEyeLongitude;
	tmp0.y = sEyeLongitude;
	tmp0.z = 0.0;

	if(yAxis.z >= parseFloat(m_ag.epsilon)){
		agOuterProductD3(yAxis, tmp0, xAxis);
		agOuterProductD3(yAxis, xAxis, zAxis);
	}
	else if(yAxis.z < -parseFloat(m_ag.epsilon)){
		agOuterProductD3(tmp0, yAxis, xAxis);
		agOuterProductD3(yAxis, xAxis, zAxis);
	} else {	// yAxis.z == 0
		remind = Math.round(m_ag.latitude) % 360;
		remind = remind < 0 ? -remind : remind;

		if(remind > 175 && remind < 185){
			zAxis.x = 0.0;
			zAxis.y = 0.0;
			zAxis.z = -1.0;
		}else{
			zAxis.x = 0.0;
			zAxis.y = 0.0;
			zAxis.z = 1.0;
		}
		agOuterProductD3(zAxis, yAxis, xAxis);
	}

	var norm = new AGVec3d(null, null, null);
	if(agNormalizeD3(xAxis, norm)) {
		agCopyD3(norm, xAxis);
	}
	if(agNormalizeD3(zAxis, norm)) {
		agCopyD3(norm, zAxis);
	}

	m_ag.targetPos.x = parseFloat(m_ag.targetPos.x) + parseFloat(xAxis.x * rx) + parseFloat(zAxis.x * ry);
	m_ag.targetPos.y = parseFloat(m_ag.targetPos.y) + parseFloat(xAxis.y * rx) + parseFloat(zAxis.y * ry);
	m_ag.targetPos.z = parseFloat(m_ag.targetPos.z) + parseFloat(xAxis.z * rx) + parseFloat(zAxis.z * ry);

	calcCameraPos();
}

function changeYRange (d, base) {
	var ratio = 1.0;
	if (d > 0) {
		ratio = Math.pow(base, d);
	} else if (d < 0) {
		ratio = Math.pow(base, d);
	}
	var tmp = m_ag.orthoYRange * ratio;
	if (tmp < m_ag.Camera_YRange_Min) {
		tmp = m_ag.Camera_YRange_Min;
	}
	m_ag.orthoYRange = tmp;
}

function calcRotateAxisDeg (upVec) {

	var V = [upVec.x,upVec.y,upVec.z];

	var X = [1.0,0.0,0.0];// Ｘ軸方向ベクトル
	var Y = [0.0,1.0,0.0];// Ｙ軸方向ベクトル
	var Z = [0.0,0.0,1.0];// Ｚ軸方向ベクトル
	var XV,YV,ZV,VV; //_内積
	var VL;          //_|V|
	var k;           //_x,y,zインデクス
	var pi;          //_円周率
	var rx,ry,rz;    //_ラヂアン
	var dx,dy,dz;    //_度

	//_内積の計算
	XV = YV = ZV = VV = 0;
	for(k=0;k<3;k++){
		XV += X[k]*V[k];
		YV += Y[k]*V[k];
		ZV += Z[k]*V[k];
		VV += V[k]*V[k];
	}
	//_角度の計算
	VL = Math.sqrt(VV);
	rx = Math.acos(XV/VL);
	ry = Math.acos(YV/VL);
	rz = Math.acos(ZV/VL);
	//_ラヂアン→度換算
	pi = Math.PI;
	dx = 180*rx/pi;
	dy = 180*ry/pi;
	dz = 180*rz/pi;
	//_表示
//	_dump("X=["+rx+"]["+dx+"]");
//	_dump("Y=["+ry+"]["+dy+"]");
//	_dump("Z=["+rz+"]["+dz+"]");


	var degH = 0;
	var degV = 0;

	var CTx = upVec.x;
	var CTy = upVec.y;
	var CTz = upVec.z;

//	_dump("CTx=["+CTx+"]");
//	_dump("CTy=["+CTy+"]");
//	_dump("CTz=["+CTz+"]");

	// Calculate Rotate H
	var radH = Math.acos(CTy / Math.sqrt(CTx*CTx + CTy * CTy));
//	_dump("radH=["+radH+"]");
	if(isNaN(radH)) radH = 0;
	var degH = radH / Math.PI * 180;

	// Calculate Rotate V
	var UnitX = -1 * Math.sin(degH / 180 * Math.PI);
	var UnitY = Math.cos(degH / 180 * Math.PI);
	var UnitZ = 0;
	var radV = Math.acos((CTx * UnitX + CTy * UnitY + CTz * UnitZ) / Math.sqrt((CTx * CTx + CTy * CTy + CTz * CTz) * (UnitX * UnitX + UnitY * UnitY + UnitZ * UnitZ)));
	if(isNaN(radV)) radV = 0;
	var degV = radV / Math.PI * 180;

//	_dump("deg=["+degH+"]["+degV+"]");


	return {H:degH,V:degV};
}
/////////////////////////////////////////////////////////////////////////////////////////////////////
function _updateAnatomo () {
	glb_anatomo_image_url='';
	glb_anatomo_editor_url='';

	glb_anatomo_image_still = '';
	glb_anatomo_image_rotate = '';

//	glb_anatomo_embedded_url='';

//	try{Ext.getCmp('anatomography-image').loadMask.show();}catch(e){}
	try{
		var img = Ext.getDom('ag_img');
		if(img && img.src){
			var params = makeAnatomoPrm();
//_dump("_updateAnatomo():anatomoImgEvent=["+anatomoImgEvent+"]");
			if(!anatomoImgEvent){
				var elem = Ext.get('ag_img');
				if(elem){

					if(Ext.isGecko){
						var base_div = Ext.get('anatomography-image-contentEl');
						Ext.EventManager.on(base_div,"mousedown", function(e,t) {anatomoImgMouseDown(e,t);});
						Ext.EventManager.on(base_div,"mousemove", function(e,t) {anatomoImgMouseMove(e,t);});
						Ext.EventManager.on(base_div,"mouseup",   function(e,t) {anatomoImgMouseUp(e,t);});
						Ext.EventManager.on(base_div,"mouseout",  function(e,t) {anatomoImgMouseOut(e,t);});
						Ext.EventManager.on(base_div,"mousewheel",function(e,t) {anatomoImgMouseWheel(e,t);});
						Ext.EventManager.on(base_div,"dblclick",  function(e,t) {anatomoImgDblClick(e,t);});
					}else{
						elem.on("mousedown", function(e,t) {anatomoImgMouseDown(e,t);});
						elem.on("mousemove", function(e,t) {anatomoImgMouseMove(e,t);});
						elem.on("mouseup",   function(e,t) {anatomoImgMouseUp(e,t);});
						elem.on("mouseout",  function(e,t) {anatomoImgMouseOut(e,t);});
						elem.on("mousewheel",function(e,t) {anatomoImgMouseWheel(e,t);});
						elem.on("dblclick",  function(e,t) {anatomoImgDblClick(e,t);});
					}

					elem.on("abort", function(e) {
//_dump("_updateAnatomo():ag_img:abort()");
						try{Ext.getCmp('anatomography-image').loadMask.hide();}catch(e){}
						var img = Ext.getDom('ag_img');
						if(img){
							img.src = "resources/images/default/s.gif";
							setImageTransform('scale(1) translate(0px,0px)');
						}
						Ext.Msg.show({
							title:'$LOCALE{TITLE_AG}',
							buttons: Ext.Msg.OK,
							closable: false,
							icon: Ext.Msg.ERROR,
							modal : true,
							msg : 'Image loading aborted.'
						});
					});
					elem.on("error", function(e){
//_dump("_updateAnatomo():ag_img:error()");
						try{Ext.getCmp('anatomography-image').loadMask.hide();}catch(e){}
						var img = Ext.getDom('ag_img');
						if(img){
							img.src = "resources/images/default/s.gif";
							setImageTransform('scale(1) translate(0px,0px)');
						}
						var error_params = makeAnatomoPrm();
						var params = Ext.urlDecode(error_params,true);
						if(Ext.isEmpty(params.oid001)) return;//部品未指定時のエラーは何もしない
						Ext.Ajax.request({
							url:cgipath.image,
							params: Ext.urlDecode(error_params, true),
							method: 'POST',
							callback: function(options,success,response){
//_dump("success=["+success+"]");
								if(success) return;

								var msg = 'Failed to load the image.';
								if(!success){
									msg += ' [' + response.status + ':' + response.statusText + ']';
									Ext.Msg.show({
										title:'$LOCALE{TITLE_AG}',
										buttons: Ext.Msg.OK,
										closable: false,
										icon: Ext.Msg.ERROR,
										modal : true,
										msg : msg
									});
								}
							}
						});
					});
					elem.on("load", function(e){
//_dump("_updateAnatomo():ag_img:load()");
						try{Ext.getCmp('anatomography-image').loadMask.hide();}catch(e){}
						var date = new Date();
//_dump("_updateAnatomo():time2=["+glb_time+"]["+date.getTime()+"]");
						var time = date.getTime() - glb_time;
						date.setTime(time);
						var s = date.getSeconds();
						var ms = date.getMilliseconds();
//_dump("_updateAnatomo():img=[load]:"+s+"."+ms);

//_dump("_updateAnatomo():img=[load]:"+params);
						setImageTransform('scale(1) translate(0px,0px)');
						var elemImg = Ext.get('ag_img');
						glbImgXY = elemImg.getXY();

						ag_put_usersession_task.delay(1000);
					});
				}
				anatomoImgEvent = true;
			}

			_loadAnatomo(params);
		}

//		glb_anatomo_image_url = img.src;
		try{
//			var editURL = img.src;
			var editURL = getEditUrl();
			editURL += cgipath.image;

//			editURL = editURL.replace(/#.*/, "");
//			editURL = editURL.replace(/\\?.*/, "");

			glb_anatomo_image_still = glb_anatomo_image_rotate = makeAnatomoPrm();

			glb_anatomo_image_url = editURL + "?" + glb_anatomo_image_still;

//_dump("glb_anatomo_image_url=["+glb_anatomo_image_url+"]");
//			_dump("_updateAnatomo():1334");
//			img.src = "css/loading.gif";
		}catch(e){}
	}catch(e){
		if(e.name && e.message){
//			alert("_updateAnatomo():"+e.name+":"+e.message);
//			_dump("_updateAnatomo():"+e.name+":"+e.message);
		}else{
//			alert("_updateAnatomo():"+e);
//			_dump("_updateAnatomo():"+e);
		}
		try{img.src = "resources/images/default/s.gif";}catch(e){}
//		_dump("_updateAnatomo():1344");
	}
	try{
		var editURL = getEditUrl();
		editURL += "?tp_ap=" + encodeURIComponent(makeAnatomoPrm(1));
		glb_anatomo_editor_url = editURL;
//		glb_anatomo_embedded_url = getEmbedIFrameUrl(editURL);
	}catch(e){}

//	try{Ext.getCmp('anatomography-image').loadMask.hide();}catch(e){}
}

function getEmbedIFrameUrl(editURL){
	return '<iframe width="425" height="350" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="'+editURL+'"></iframe><br />$LOCALE{LICENSE_EMBED}<br /><small><a href="'+editURL+'" target="_blank" style="color:#0000FF;text-align:left">$LOCALE{ANATOMO_OPEN}</a></small>';
}
function getEmbedImgUrl(editURL){
	return '<img src="'+editURL+'"><br />$LOCALE{LICENSE_EMBED}';
}
function getEmbedAUrl(editURL){
	return '<a href="'+editURL+'">BodyParts3D</a>';
}

function getEditUrl(){
	var editURL = document.URL;
	return editURL.replace(/#.*/, "").replace(/\\?.*/, "").replace(/[^\\/]+\$/, "");
}

function setRotateHorizontalValue(value) {
	value = (isNaN(value))?0:parseInt(value);

//	var span = document.getElementById("rotateH");
//	span.setAttribute("value", value);
//	span.innerHTML = value;

	var prm_record = ag_param_store.getAt(0);
	prm_record.beginEdit();
	prm_record.set('rotate_h', value);
	prm_record.endEdit();
	prm_record.commit();

	try{Ext.getCmp("rotateH").setValue(value);}catch(e){}
}

function setRotateVerticalValue(value) {
	value = (isNaN(value))?0:parseInt(value);

//	var span = document.getElementById("rotateV");
//	span.setAttribute("value", value);
//	span.innerHTML = value;

	var prm_record = ag_param_store.getAt(0);
	prm_record.beginEdit();
	prm_record.set('rotate_v', value);
	prm_record.endEdit();
	prm_record.commit();

	try{Ext.getCmp("rotateV").setValue(value);}catch(e){}
}

function getRotateHorizontalValue() {
//	var span = document.getElementById("rotateH");
//	span.setAttribute("value", deg);
//	span.innerHTML = deg;
	try{
		return parseInt(Ext.getCmp("rotateH").getValue());
	}catch(e){
		var prm_record = ag_param_store.getAt(0);
		return prm_record.data.rotate_h;
	}
}

function getRotateVerticalValue() {
//	var span = document.getElementById("rotateV");
//	span.setAttribute("value", deg);
//	span.innerHTML = deg;
	try{
		return parseInt(Ext.getCmp("rotateV").getValue());
	}catch(e){
		var prm_record = ag_param_store.getAt(0);
		return prm_record.data.rotate_v;
	}
}

function makeRotImgDiv () {
	return;
	rotImgDiv = document.createElement("div");
	rotImgDiv.setAttribute("id", "rotImgDiv");
	rotImgDiv.setAttribute("align", "center");
	rotImgDiv.style.position = 'absolute';
	rotImgDiv.style.border = '1px solid #3c3c3c';
	rotImgDiv.style.background = '#f0f0f0';
	rotImgDiv.style.MozOpacity = 0.75;
	rotImgDiv.style.opacity = 0.75;
	rotImgDiv.style.filter = "alpha(opacity='75')";
	rotImgDiv.style.width = "80px";
	rotImgDiv.style.height = "80px";
	rotImgDiv.style.backgroundImage = "url('img/rotImg.png')";
	rotImgDiv.style.backgroundRepeat = "no-repeat";
	rotImgDiv.style.visibility = "hidden";
	rotImgDiv.style.left = "-100px";
	rotImgDiv.style.top = "-100px";
	document.body.appendChild(rotImgDiv);
}

function anatomoImgMoveCenter(x,y){
	var centerX = parseInt((ag_param_store.getAt(0).data.image_w /2) -  x);
	var centerY = parseInt((ag_param_store.getAt(0).data.image_h /2) -  y);
	var image_h = ag_param_store.getAt(0).data.image_h;
	var zoom = ag_param_store.getAt(0).data.zoom;
	moveTargetByMouseForOrtho(image_h, centerX / parseFloat(Math.pow(2, zoom)), centerY / parseFloat(Math.pow(2, zoom)));
	setImageTransform('scale(1) translate(' + centerX + 'px, ' + centerY + 'px)',true);
	stopUpdateAnatomo();
	_updateAnatomo();
}
function anatomoImgDblClick(e,t){
//_dump("anatomoImgDblClick():"+t.id);
	if(!t || t.id!='ag_img') return;
	try {
		e.stopPropagation();
		e.preventDefault();
	} catch (ex) {
		e.returnValue = false;
		e.cancelBubble = true;
	}

	var elemImg = Ext.get('ag_img');
	var xyImg = elemImg.getXY();
	var mouseX = e.xy[0] - xyImg[0];
	var mouseY = e.xy[1] - xyImg[1];
	anatomoImgMoveCenter(mouseX,mouseY);
//	var centerX = parseInt((ag_param_store.getAt(0).data.image_w /2) -  mouseX);
//	var centerY = parseInt((ag_param_store.getAt(0).data.image_h /2) -  mouseY);
//	moveTargetByMouseForOrtho(ag_param_store.getAt(0).data.image_h, centerX / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)), centerY / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)));
//	setImageTransform('scale(1) translate(' + centerX + 'px, ' + centerY + 'px)',true);
//	stopUpdateAnatomo();
//	_updateAnatomo();
}

function makeAnatomoOrganPointPrm(num,record){
	var prm = "";

	// Point Color
	var colorstr = record.data.color.substr(1, 6);
	if(colorstr.length == 6) prm = prm + "&pocl" + num + "=" + colorstr;

	// Point Remove
	prm = prm + "&porm" + num + "=";
	if (record.data.exclude) {
		prm = prm + "1";
	}else{
		prm = prm + "0";
	}

	// Point Opacity
	prm = prm + "&poop" + num + "=";
//	if(record.data.opacity==0.1){
//		prm = prm + "0.05";
//	}else{
		prm = prm + record.data.opacity;
//	}

	// Point Representation
	if (record.data.representation == "surface") {
		prm = prm + "&pore" + num + "=S";
	} else if (record.data.representation == "wireframe") {
		prm = prm + "&pore" + num + "=W";
	} else if (record.data.representation == "points") {
		prm = prm + "&pore" + num + "=P";
	}

	// Point Sphere
	var prm_record = ag_param_store.getAt(0);
	prm = prm + "&posh" + num + "=" + prm_record.data.point_sphere;

	return prm;
}

function isNumber(v){
	return((typeof v)==='number' && isFinite(v));
}

function roundPrm(value){
	try{if(!isNumber(value)) value = Number(value);}catch(e){}
	return Math.round(value*10000)/10000;
}

function truncationPrm(value){
	try{if(!isNumber(value)) value = Number(value);}catch(e){}
	return parseInt(value*10000)/10000;
}

function makeAnatomoPrm_Pin(record,anatomo_pin_shape_combo_value,coordinate_system,properties){

	if(Ext.isEmpty(record) || Ext.isEmpty(record.data)) return undefined;

	properties = properties || {};
	var data = Ext.apply({},properties,record.data);
 
	if(Ext.isEmpty(anatomo_pin_shape_combo_value)){
		try{
			anatomo_pin_shape_combo_value = Ext.getCmp("anatomo_pin_shape_combo").getValue();
		}catch(e){
			anatomo_pin_shape_combo_value = init_anatomo_pin_shape;
		}
	}

	//coordinate_system
	if(Ext.isEmpty(coordinate_system)){
		try{
			coordinate_system = Ext.getCmp("ag-coordinate-system-combo").getValue();
		}catch(e){
			coordinate_system = prm_record.data.coord;
		}
	}
	var prm = '';
	try{
		var no = parseInt(data.no);
		var num = makeAnatomoOrganNumber(no);
		// No
		prm = prm + "pno" + num + "=" + no.toString();
		// 3Dx
		prm = prm + "&px" + num + "=" + roundPrm(data.x3d);
		// 3Dy
		prm = prm + "&py" + num + "=" + roundPrm(data.y3d);
		// 3Dz
		prm = prm + "&pz" + num + "=" + roundPrm(data.z3d);
		// ArrVec3Dx
		prm = prm + "&pax" + num + "=" + roundPrm(data.avx3d);
		// ArrVec3Dy
		prm = prm + "&pay" + num + "=" + roundPrm(data.avy3d);
		// ArrVec3Dz
		prm = prm + "&paz" + num + "=" + roundPrm(data.avz3d);
		// UpVec3Dx
		prm = prm + "&pux" + num + "=" + roundPrm(data.uvx3d);
		// UpVec3Dy
		prm = prm + "&puy" + num + "=" + roundPrm(data.uvy3d);
		// UpVec3Dz
		prm = prm + "&puz" + num + "=" + roundPrm(data.uvz3d);
		// Draw Pin Description
		var drawCheck = Ext.getCmp('anatomo_pin_description_draw_check');
		if(drawCheck && drawCheck.rendered){
			if(drawCheck.getValue()){
				prm = prm + "&pdd" + num + "=1";
				prm = prm + "&pdc" + num + "=" + data.color;
			}else{
			}
		}else if(init_anatomo_pin_description_draw){
			prm = prm + "&pdd" + num + "=1";
			prm = prm + "&pdc" + num + "=" + data.color;
		}
		// Point Shape
		prm = prm + "&ps" + num + "=" + anatomo_pin_shape_combo_value;
		// ForeRGB
		prm = prm + "&pcl" + num + "=" + data.color;
		// OrganID
		prm = prm + "&poi" + num + "=" + encodeURIComponent(data.oid);
		// OrganName
		prm = prm + "&pon" + num + "=" + encodeURIComponent(data.organ);
		// Comment
		prm = prm + "&pd" + num + "=" + (Ext.isEmpty(data.comment) ? '' : encodeURIComponent(data.comment));

		//coordinate_system
		if(!Ext.isEmpty(data.coord)){
			prm = prm + "&pcd" + num + "=" + encodeURIComponent(data.coord);
		}else if(!Ext.isEmpty(coordinate_system)){
			prm = prm + "&pcd" + num + "=" + encodeURIComponent(coordinate_system);
		}
	}catch(e){
		_dump(e);
		prm = undefined;
	}
//	console.log("prm=["+prm+"]");
	return prm;
}

function getDateString () {
	var now = new Date();
	var year = now.getFullYear();
	var mon = now.getMonth() + 1;
	var day = now.getDate();
	var hour = now.getHours();
	var min = now.getMinutes();
	var sec = now.getSeconds();
	if(mon < 10) mon = "0" + mon;
	if(day < 10) day = "0" + day;
	if(hour< 10) hour = "0" + hour;
	if(min < 10) min = "0" + min;
	if(sec < 10) sec = "0" + sec;
	return "" + year + mon + day + hour + min + sec;
}

setImageWindowSize = function(){
	var checkcmp = Ext.getCmp('anatomo-windowsize-autosize-check');
	if(checkcmp && checkcmp.rendered && !checkcmp.getValue()) return;
	var comp = Ext.getCmp('anatomography-image');
	if(!comp || !comp.rendered) return;
	var size = comp.getSize();
	try{
		var w = parseInt(size.width);
//		var w = parseInt((size.width-10)/10)*10;
//		w = (w<100?100:(w>900?900:w));
		w = (w<100?100:w);
		var h = parseInt(size.height);
//		var h = parseInt((size.height-10)/10)*10;
//		h = (h<100?100:(h>900?900:h));
		h = (h<100?100:h);
		var wc = Ext.getCmp('anatomo-width-combo');
		var hc = Ext.getCmp('anatomo-height-combo');
		if(wc && wc.rendered && hc && hc.rendered){
			wc.setValue(w);
			hc.setValue(h);
		}
		var prm_record = ag_param_store.getAt(0);
		prm_record.beginEdit();
		prm_record.set('image_w', w);
		prm_record.set('image_h', h);
		prm_record.endEdit();
		prm_record.commit();
		updateAnatomo();

	}catch(e){
		_dump("setImageWindowSize():"+e);
	}
};

getConvertIdList = function(records,store){
//_dump("getConvertIdList():records=["+records.length+"]");
	var recs = [];
	for(var i=0;i<records.length;i++){
		var rec = {
			tg_id   : records[i].get('tg_id'),
			tgi_id  : records[i].get('tgi_id'),
			version : records[i].get('version'),
			f_id    : records[i].get('f_id'),

			ci_id   : records[i].get('ci_id'),
			cb_id   : records[i].get('cb_id'),
			bul_id  : records[i].get('bul_id'),
			md_id   : records[i].get('md_id'),
			mv_id   : records[i].get('mv_id'),
			mr_id   : records[i].get('mr_id')
		};
		recs.push(rec);
	}
	var params = {
		parent  : (Ext.isEmpty(gParams.parent)?'':gParams.parent),
		lng     : gParams.lng,
		records : Ext.util.JSON.encode(recs)
	}
	try{
		params.version = Ext.getCmp('bp3d-version-combo').getValue();
//		_dump("getConvertIdList():params.version=["+params.version+"]");
	}catch(e){}
	if(Ext.isEmpty(params.version)) params.version=init_bp3d_version;

	try{
		var bp3d_version_combo = Ext.getCmp('bp3d-version-combo');
		var bp3d_version_store = bp3d_version_combo.getStore();
		var bp3d_version_idx = bp3d_version_store.find('tgi_version',new RegExp('^'+bp3d_version_combo.getValue()+'\$'));
		var bp3d_version_rec;
		var bp3d_version_disp_value;
		if(bp3d_version_idx>=0) bp3d_version_rec = bp3d_version_store.getAt(bp3d_version_idx);
		if(bp3d_version_rec){
			params.md_id = bp3d_version_rec.get('md_id');
			params.mv_id = bp3d_version_rec.get('mv_id');
			params.mr_id = bp3d_version_rec.get('mr_id');
		}
	}catch(e){}
	try{
		var bp3d_tree_combo = Ext.getCmp('bp3d-tree-type-combo');
		var bp3d_tree_store = bp3d_tree_combo.getStore();
		var bp3d_tree_idx = bp3d_tree_store.find('t_type',new RegExp('^'+bp3d_tree_combo.getValue()+'\$'));
		var bp3d_tree_rec;
		var bp3d_tree_disp_value;
		if(bp3d_tree_idx>=0) bp3d_tree_rec = bp3d_tree_store.getAt(bp3d_tree_idx);
		if(bp3d_tree_rec){
			params.bul_id = bp3d_tree_rec.get('bul_id');
			params.ci_id = bp3d_tree_rec.get('ci_id');
			params.cb_id = bp3d_tree_rec.get('cb_id');
		}
	}catch(e){}


	var params = Ext.urlEncode(params)
//_dump("getConvertIdList():params=["+params+"]");

	hideConvIDColumn();

	var window_title = "";
	Ext.Ajax.request({
		url     : 'get-convert-id-list.cgi',
		method  : 'POST',
		params  : params,
		success : function(conn,response,options){
			try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
			if(!results || results.success == false){
				var msg = '';
				if(results && results.msg) msg += ' ['+results.msg+' ]';
				Ext.MessageBox.show({
					title   : window_title,
					msg     : msg,
					buttons : Ext.MessageBox.OK,
					icon    : Ext.MessageBox.ERROR
				});
				return;
			}
			try{
				if(results.records){
					try{var tg_id = Ext.getCmp('bp3d-tree-group-combo').getValue();}catch(e){tg_id=init_tree_group;}
					var i;
					for(i=0;i<results.records.length;i++){
						var idx = store.find('b_id',new RegExp("^"+results.records[i].b_id+"\$"));
						if(idx<0) idx = store.find('f_id',new RegExp("^"+results.records[i].f_id+"\$"));
						if(idx<0) continue;
						var record = store.getAt(idx);
						record.beginEdit();
						if(results.records[i].conv_id && results.records[i].conv_id instanceof Array){
							record.set('conv_id',results.records[i].conv_id.join(","));
						}else{
							record.set('conv_id',results.records[i].conv_id);
						}
						for(var key in results.records[i]){
							if(key == 'conv_id') continue;
							record.set(key,results.records[i][key]);
						}
						record.commit(true);
						record.endEdit();
					}
					var records = store.getRange();
					store.removeAll();
					store.add(records);
					showConvIDColumn();
				}
				_updateAnatomo();
			}catch(e){
				_dump(e);
			}
		},
		failure : function(conn,response,options){
			try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
			var msg = '[';
			if(results && results.msg){
				msg += results.msg+' ]';
			}else{
				msg += conn.status+" "+conn.statusText+' ]';
			}
			Ext.MessageBox.show({
				title   : window_title,
				msg     : msg,
				buttons : Ext.MessageBox.OK,
				icon    : Ext.MessageBox.ERROR
			});
		}
	});
};

load_bp3d_contents_store = function(self,records,options){
_dump("load_bp3d_contents_store():records=["+records.length+"]");
_dump("load_bp3d_contents_store():["+Ext.isEmpty(gParams.tp_ap)+"]");
	try{reset_func();}catch(e){}
//	try{
		if(!Ext.isEmpty(gParams.tp_ap)){
			var tp_ap = gParams.tp_ap;
//						delete gParams.tp_ap;

			var tpap_param = analyzeTPAP(tp_ap);
			if(!tpap_param) return;
//_dump("bp3d_contents_store.load():tpap_param.parts=["+(tpap_param.parts?tpap_param.parts.length:0)+"]");

			var contents_tabs = Ext.getCmp('contents-tab-panel');

//2011-09-28 コメントアウト
//2011-09-30 各設定が正しく定義されない為、とりあえずタブをカレントにする
			if(((tpap_param.parts && tpap_param.parts.length>0 && records.length>0) || (tpap_param.pins && tpap_param.pins.length>0)) && contents_tabs){
				if(contents_tabs.getXType()=='tabpanel'){
					contents_tabs.setActiveTab('contents-tab-anatomography-panel');
				}else if(contents_tabs.getXType()=='panel'){
					contents_tabs.getLayout().setActiveItem('contents-tab-anatomography-panel');
				}
			}


			var fma_rec = {};
			for(var i=0,len=records.length;i<len;i++){
				var record = records[i].copy();
				var f_id = record.get('f_id');
				fma_rec[f_id] = record;
//_dump("bp3d_contents_store.load():record=["+i+"]["+record.data.f_id+"]["+record.data.name_e+"]");
			}

			try{var prm_record = (ag_param_store?ag_param_store.getAt(0):undefined);}catch(e){}

//_dump("bp3d_contents_store.load():prm_record.data.clip_depth=["+prm_record.data.clip_depth+"]");

			if(tpap_param.common != null && prm_record != undefined && prm_record != null){
				prm_record.beginEdit();
				if(!Ext.isEmpty(tpap_param.common.method)) prm_record.set('method',tpap_param.common.method);
				if(!Ext.isEmpty(tpap_param.common.viewpoint)) prm_record.set('viewpoint',tpap_param.common.viewpoint);
				if(gParams.tp_md){
					if(!Ext.isEmpty(tpap_param.common.image_w)) prm_record.set('image_w',tpap_param.common.image_w);
					if(!Ext.isEmpty(tpap_param.common.image_h)) prm_record.set('image_h',tpap_param.common.image_h);
				}
				if(!Ext.isEmpty(tpap_param.common.bg_rgb)) prm_record.set('bg_rgb',tpap_param.common.bg_rgb);
				prm_record.set('bg_transparent',Ext.isEmpty(tpap_param.common.bg_transparent)?NaN:0);
				if(!Ext.isEmpty(tpap_param.common.autoscalar_f)) prm_record.set('autoscalar_f',tpap_param.common.autoscalar_f);
				if(!Ext.isEmpty(tpap_param.common.colorbar_f)) prm_record.set('colorbar_f',tpap_param.common.colorbar_f);
				if(!Ext.isEmpty(tpap_param.common.heatmap_f)) prm_record.set('heatmap_f',tpap_param.common.heatmap_f);
				if(!Ext.isEmpty(tpap_param.common.drawsort_f)) prm_record.set('drawsort_f',tpap_param.common.drawsort_f);
				if(!Ext.isEmpty(tpap_param.common.mov_len)) prm_record.set('mov_len',tpap_param.common.mov_len);
				if(!Ext.isEmpty(tpap_param.common.mov_fps)) prm_record.set('mov_fps',tpap_param.common.mov_fps);

				if(gParams.tp_md){
					if(!Ext.isEmpty(tpap_param.common.image_w)){
						var elemW = Ext.getCmp('anatomo-width-combo');
						if(elemW && elemW.rendered) elemW.setValue(tpap_param.common.image_w);
					}
					if(!Ext.isEmpty(tpap_param.common.image_h)){
						var elemH = Ext.getCmp('anatomo-height-combo');
						if(elemH && elemH.rendered) elemH.setValue(tpap_param.common.image_h);
					}
					if(!Ext.isEmpty(tpap_param.common.image_w) || !Ext.isEmpty(tpap_param.common.image_h)){
						var elemC = Ext.getCmp('anatomo-windowsize-autosize-check');
						if(elemC && elemC.rendered) elemC.setValue(false);
					}
				}

				var elemBGCOLOR = Ext.getCmp('anatomo-bgcp');
				if(elemBGCOLOR && elemBGCOLOR.rendered) elemBGCOLOR.setValue('#'+tpap_param.common.bg_rgb);

				var elemBGTransparent = Ext.getCmp('anatomo-bgcolor-transparent-check');
				if(elemBGTransparent && elemBGTransparent.rendered) elemBGTransparent.setValue(Ext.isEmpty(tpap_param.common.bg_transparent)?false:true);

				if(!Ext.isEmpty(tpap_param.common.rotate_h) && !Ext.isEmpty(tpap_param.common.rotate_v)){
					setRotateHorizontalValue(tpap_param.common.rotate_h);
					setRotateVerticalValue(tpap_param.common.rotate_v);
					if(Ext.isEmpty(gParams.tp_md) || gParams.tp_md != 1){
						if(updateRotateImg) updateRotateImg();
					}
				}

				if(!Ext.isEmpty(tpap_param.common.scalar_max)){
					prm_record.set('scalar_max',tpap_param.common.scalar_max);
					var elem = Ext.getCmp('scalar-max-textfield');
					if(elem && elem.rendered) elem.setValue(tpap_param.common.scalar_max);
				}
				if(!Ext.isEmpty(tpap_param.common.scalar_min)){
					prm_record.set('scalar_min',tpap_param.common.scalar_min);
					var elem = Ext.getCmp('scalar-min-textfield');
					if(elem && elem.rendered) elem.setValue(tpap_param.common.scalar_min);
				}
				if(!Ext.isEmpty(tpap_param.common.colorbar_f) && parseInt(tpap_param.common.colorbar_f)>0){
					var elem = Ext.getCmp('show-colorbar-check');
					if(elem && elem.rendered) elem.setValue(true);
				}
				if(!Ext.isEmpty(tpap_param.common.heatmap_f) && parseInt(tpap_param.common.heatmap_f)>0){
					var elem = Ext.getCmp('show-heatmap-check');
					if(elem && elem.rendered) elem.setValue(true);
				}

//_dump("bp3d_contents_store.load():tpap_param.common.zoom=["+tpap_param.common.zoom+"]");
				if(!Ext.isEmpty(tpap_param.common.zoom)){
					prm_record.set('zoom',parseFloat(tpap_param.common.zoom));
					glb_zoom_slider = prm_record.data.zoom*5+1;
//_dump("bp3d_contents_store.load():glb_zoom_slider=["+glb_zoom_slider+"]");
//								var cmp = Ext.getCmp('zoom-value-text');
//								if(cmp && cmp.rendered) cmp.setValue(glb_zoom_slider+1);
					var cmp = Ext.getCmp('zoom-slider');
					if(cmp && cmp.rendered){
						cmp.setValue(glb_zoom_slider-1);
						ag_command_zoom_menu_slider_syncThumb_task.delay(1000);
					}
				}
				if(!Ext.isEmpty(tpap_param.common.move_x)) prm_record.set('move_x',tpap_param.common.move_x);
				if(!Ext.isEmpty(tpap_param.common.move_y)) prm_record.set('move_y',tpap_param.common.move_y);
				if(!Ext.isEmpty(tpap_param.common.move_z)) prm_record.set('move_z',tpap_param.common.move_z);
				if(!Ext.isEmpty(tpap_param.common.clip_depth)) prm_record.set('clip_depth',tpap_param.common.clip_depth);
				if(!Ext.isEmpty(tpap_param.common.clip_method)) prm_record.set('clip_method',tpap_param.common.clip_method);

				if(!Ext.isEmpty(tpap_param.common.bp3d_version)){
					init_bp3d_version = tpap_param.common.bp3d_version;
//_dump("bp3d_contents_store.load():init_bp3d_version=["+init_bp3d_version+"]");
					if(tpap_param.common.tg_id){
						init_tree_group = tpap_param.common.tg_id;
					}else if(tpap_param.common.model && model2tg[tpap_param.common.model]){
						init_tree_group = model2tg[tpap_param.common.model].tg_id;
					}else if(version2tg[init_bp3d_version] && version2tg[init_bp3d_version].tg_id){
						init_tree_group = version2tg[init_bp3d_version].tg_id;
					}
					if(version2tg[init_bp3d_version].tgi_delcause){
						if(Ext.isEmpty(latestversion[init_tree_group])) return;
						init_bp3d_version = latestversion[init_tree_group];
					}
//_dump("bp3d_contents_store.load():init_bp3d_version=["+init_bp3d_version+"]");

					var cmp = Ext.getCmp('bp3d-version-combo');
					if(cmp && cmp.rendered) cmp.setValue(init_bp3d_version);
					var cmp = Ext.getCmp('anatomo-version-combo');
					if(cmp && cmp.rendered) cmp.setValue(init_bp3d_version);
				}

				if(!Ext.isEmpty(tpap_param.common.grid)){
					prm_record.set('grid',tpap_param.common.grid);
					var elem = Ext.getCmp('ag-command-grid-show-check');
					if(elem && elem.rendered) elem.setValue(tpap_param.common.grid=='1'?true:false);
				}
				if(!Ext.isEmpty(tpap_param.common.grid_color)){
					var elem = Ext.getCmp('ag-command-grid-color-field');
					if(elem && elem.rendered) elem.setValue('#'+tpap_param.common.grid_color);
					prm_record.set('grid_color', tpap_param.common.grid_color);
				}
				if(!Ext.isEmpty(tpap_param.common.grid_len)){
					var elem = Ext.getCmp('ag-command-grid-len-combobox');
					if(elem && elem.rendered) elem.setValue(tpap_param.common.grid_len);
					prm_record.set('grid_len', tpap_param.common.grid_len);
				}

				if(Ext.isEmpty(tpap_param.common.coord)) tpap_param.common.coord = 'bp3d';
//_dump("bp3d_contents_store.load():tpap_param.common.coord=["+tpap_param.common.coord+"]");
				var elem = Ext.getCmp('ag-coordinate-system-combo');
				if(elem && elem.rendered){
					elem.setValue(tpap_param.common.coord);
//_dump("bp3d_contents_store.load():elem.getValue=["+elem.getValue()+"]");
				}
				prm_record.set('coord',tpap_param.common.coord);


				if(Ext.isEmpty(tpap_param.common.color_rgb)) tpap_param.common.color_rgb = '$DEF_COLOR_VAL';
				var elem = Ext.getCmp('anatomo-default-parts-color');
				if(elem && elem.rendered) elem.setValue(tpap_param.common.color_rgb);
				prm_record.set('color_rgb',tpap_param.common.color_rgb);

				if(Ext.isEmpty(tpap_param.common.point_color_rgb)) tpap_param.common.point_color_rgb = '$DEF_COLOR_POINT_VAL';
				var elem = Ext.getCmp('anatomo-default-point-parts-color');
				if(elem && elem.rendered) elem.setValue(tpap_param.common.point_color_rgb);
				prm_record.set('point_color_rgb',tpap_param.common.point_color_rgb);

				if(!Ext.isEmpty(tpap_param.common.point_desc)){
					prm_record.set('point_desc',tpap_param.common.point_desc);
					var elem = Ext.getCmp('ag-command-point-description-check');
					if(elem && elem.rendered) elem.setValue(tpap_param.common.point_desc);
				}
				if(!Ext.isEmpty(tpap_param.common.point_pin_line)){
					init_anatomo_pin_description_line = tpap_param.common.point_pin_line;
					prm_record.set('point_pin_line',tpap_param.common.point_pin_line);
					var elem = Ext.getCmp('anatomo_pin_description_draw_pin_indication_line_combo');
					if(elem && elem.rendered) elem.setValue(tpap_param.common.point_pin_line);
				}
				if(!Ext.isEmpty(tpap_param.common.point_point_line)){
					prm_record.set('point_point_line',tpap_param.common.point_point_line);
					var elem = Ext.getCmp('ag-command-point-description-draw-point-indication-line-combo');
					if(elem && elem.rendered) elem.setValue(tpap_param.common.point_point_line);
				}
				if(!Ext.isEmpty(tpap_param.common.point_sphere)){
					prm_record.set('point_sphere',tpap_param.common.point_sphere);
					var elem = Ext.getCmp('ag-command-point-sphere-combo');
					if(elem && elem.rendered) elem.setValue(tpap_param.common.point_sphere);
				}


				//PIN関連
				if(!Ext.isEmpty(tpap_param.common.pin)){
					init_anatomo_pin_description_draw = tpap_param.common.pin ? true : false;
					var elem = Ext.getCmp('anatomo_pin_description_draw_check');
					if(elem && elem.rendered) elem.setValue(init_anatomo_pin_description_draw);
				}
				if(!Ext.isEmpty(tpap_param.common.pinno)){
					init_anatomo_pin_number_draw = tpap_param.common.pinno ? true : false;
					var elem = Ext.getCmp('anatomo_pin_number_draw_check');
					if(elem && elem.rendered) elem.setValue(init_anatomo_pin_number_draw);
				}


				if(!Ext.isEmpty(tpap_param.camera)){
					if(!Ext.isEmpty(tpap_param.camera.cameraPos)){
						m_ag.cameraPos.x = tpap_param.camera.cameraPos.x;
						m_ag.cameraPos.y = tpap_param.camera.cameraPos.y;
						m_ag.cameraPos.z = tpap_param.camera.cameraPos.z;
					}
					if(!Ext.isEmpty(tpap_param.camera.targetPos)){
						m_ag.targetPos.x = tpap_param.camera.targetPos.x;
						m_ag.targetPos.y = tpap_param.camera.targetPos.y;
						m_ag.targetPos.z = tpap_param.camera.targetPos.z;
					}
					if(!Ext.isEmpty(tpap_param.camera.upVec)){
						m_ag.upVec.x = tpap_param.camera.upVec.x;
						m_ag.upVec.y = tpap_param.camera.upVec.y;
						m_ag.upVec.z = tpap_param.camera.upVec.z;
					}
//_dump("m_ag.targetPos.x=["+(typeof m_ag.targetPos.x)+"]["+m_ag.targetPos.x+"]");
//_dump("m_ag.cameraPos=["+m_ag.cameraPos.x+"]["+m_ag.cameraPos.y+"]["+m_ag.cameraPos.z+"]");
//_dump("m_ag.targetPos=["+m_ag.targetPos.x+"]["+m_ag.targetPos.y+"]["+m_ag.targetPos.z+"]");
//_dump("m_ag.upVec=["+m_ag.upVec.x+"]["+m_ag.upVec.y+"]["+m_ag.upVec.z+"]");

					if(!Ext.isEmpty(tpap_param.camera.cameraPos) && !Ext.isEmpty(tpap_param.camera.targetPos) && !Ext.isEmpty(tpap_param.camera.upVec)){
						setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);

						var deg = calcRotateDeg();
						tpap_param.common.rotate_h = deg.H;
						tpap_param.common.rotate_v = deg.V;
						setRotateHorizontalValue(deg.H);
						setRotateVerticalValue(deg.V);

						if(Ext.isEmpty(gParams.tp_md) || gParams.tp_md != 1){
							if(updateRotateImg) updateRotateImg();
						}
					}
				}

				if(!Ext.isEmpty(tpap_param.clip) && !Ext.isEmpty(tpap_param.clip.type) && tpap_param.clip.type != 'N'){
					if(!Ext.isEmpty(tpap_param.clip.type))   prm_record.set('clip_type',tpap_param.clip.type);
					if(!Ext.isEmpty(tpap_param.clip.depth))  prm_record.set('clip_depth',parseFloat(tpap_param.clip.depth));
					if(!Ext.isEmpty(tpap_param.clip.method)) prm_record.set('clip_method',tpap_param.clip.method);
					if(!Ext.isEmpty(tpap_param.clip.paramA)) prm_record.set('clip_paramA',parseFloat(tpap_param.clip.paramA));
					if(!Ext.isEmpty(tpap_param.clip.paramB)) prm_record.set('clip_paramB',parseFloat(tpap_param.clip.paramB));
					if(!Ext.isEmpty(tpap_param.clip.paramC)) prm_record.set('clip_paramC',parseFloat(tpap_param.clip.paramC));
					if(!Ext.isEmpty(tpap_param.clip.paramD)) prm_record.set('clip_paramD',parseFloat(tpap_param.clip.paramD));

					if(prm_record.data.clip_paramA != 0 && prm_record.data.clip_paramB != 0 && prm_record.data.clip_paramB != 0){
					}else{
						if(prm_record.data.clip_paramB){
							prm_record.set('clip_depth', (tpap_param.clip.paramD*prm_record.data.clip_paramB));
						}else if(prm_record.data.clip_paramA){
							prm_record.set('clip_depth', (tpap_param.clip.paramD*prm_record.data.clip_paramA));
						}else if(prm_record.data.clip_paramC){
							prm_record.set('clip_depth', (tpap_param.clip.paramD*prm_record.data.clip_paramC));
						}
						prm_record.set('clip_depth', tpap_param.clip.paramD);
					}

					var anatomo_clip_check = Ext.getCmp('anatomo-clip-check');
					var anatomo_clip_method_combo = Ext.getCmp('anatomo-clip-method-combo');
					var anatomo_clip_predifined_plane = Ext.getCmp('anatomo-clip-predifined-plane');
					var anatomo_clip_fix_check = Ext.getCmp('anatomo-clip-fix-check');
					var anatomo_clip_reverse_check = Ext.getCmp('anatomo-clip-reverse-check');
					var anatomo_clip_slider = Ext.getCmp('anatomo-clip-slider');
					var anatomo_clip_value_text = Ext.getCmp('anatomo-clip-value-text');

					var anatomo_clip_slider_up_button = Ext.get('anatomo-clip-slider-up-button');
					var anatomo_clip_slider_down_button = Ext.get('anatomo-clip-slider-down-button');
					var anatomo_clip_text_up_button = Ext.get('anatomo-clip-text-up-button');
					var anatomo_clip_text_down_button = Ext.get('anatomo-clip-text-down-button');
					var anatomo_clip_unit_label = Ext.get('anatomo-clip-unit-label');
					var clipImgDiv = Ext.get('clipImgDiv');

					if(anatomo_clip_check) anatomo_clip_check.un('check',oncheck_anatomo_clip_check);
					if(anatomo_clip_method_combo) anatomo_clip_method_combo.un('select',onselect_anatomo_clip_method_combo);
					if(anatomo_clip_predifined_plane) anatomo_clip_predifined_plane.un('select',onselect_anatomo_clip_predifined_plane);
					if(anatomo_clip_fix_check) anatomo_clip_fix_check.un('check',oncheck_anatomo_clip_fix_check);
					if(anatomo_clip_reverse_check) anatomo_clip_reverse_check.un('check',oncheck_anatomo_clip_reverse_check);
					if(anatomo_clip_slider) anatomo_clip_slider.un('change',onchange_anatomo_clip_slider);
					if(anatomo_clip_value_text) anatomo_clip_value_text.un('change',onchange_anatomo_clip_value_text);

					if(anatomo_clip_check && anatomo_clip_check.rendered) anatomo_clip_check.setValue(true);

					var clip = 'FREE';
					var clip_param = 1;
					var clip_depth = 0;
//_dump("anatomo_clip_predifined_plane=["+anatomo_clip_predifined_plane+"]");
					if(anatomo_clip_predifined_plane && anatomo_clip_predifined_plane.rendered){
						if(prm_record.data.clip_paramA != 0 && prm_record.data.clip_paramB != 0 && prm_record.data.clip_paramB != 0){
							clip_param = prm_record.data.clip_paramD;
							clip_depth = Math.round(parseFloat(tpap_param.clip.depth));
							if(anatomo_clip_fix_check && anatomo_clip_fix_check.rendered) anatomo_clip_fix_check.setValue(true);
						}else{
							if(prm_record.data.clip_paramA != 0){
								clip = 'RL';
								clip_param = prm_record.data.clip_paramA;
							}else if(prm_record.data.clip_paramB != 0){
								clip = 'FB';
								clip_param = prm_record.data.clip_paramB;
							}else if(prm_record.data.clip_paramC != 0){
								clip = 'TB';
								clip_param = prm_record.data.clip_paramC;
							}
							anatomo_clip_predifined_plane.setValue(clip);
							clip_depth = Math.round(parseFloat(tpap_param.clip.paramD*clip_param*-1));
						}
					}
					if(clip_param<0 && anatomo_clip_reverse_check && anatomo_clip_reverse_check.rendered) anatomo_clip_reverse_check.setValue(true);

					if(anatomo_clip_slider && anatomo_clip_slider.rendered) anatomo_clip_slider.setValue(clip_depth);
					if(anatomo_clip_value_text && anatomo_clip_value_text.rendered) anatomo_clip_value_text.setValue(clip_depth);

					if(anatomo_clip_method_combo && anatomo_clip_method_combo.rendered) anatomo_clip_method_combo.setValue(tpap_param.clip.method);

					if(anatomo_clip_method_combo && anatomo_clip_method_combo.rendered) anatomo_clip_method_combo.show();
					if(anatomo_clip_predifined_plane && anatomo_clip_predifined_plane.rendered) anatomo_clip_predifined_plane.show();
					if(anatomo_clip_fix_check && anatomo_clip_fix_check.rendered && clip=='FREE') anatomo_clip_fix_check.show();
					if(anatomo_clip_reverse_check && anatomo_clip_reverse_check.rendered) anatomo_clip_reverse_check.show();
					if(anatomo_clip_slider && anatomo_clip_slider.rendered) anatomo_clip_slider.show();
					if(anatomo_clip_value_text && anatomo_clip_value_text.rendered) anatomo_clip_value_text.show();

					if(anatomo_clip_slider_up_button) anatomo_clip_slider_up_button.show();
					if(anatomo_clip_slider_down_button) anatomo_clip_slider_down_button.show();
					if(anatomo_clip_text_up_button) anatomo_clip_text_up_button.show();
					if(anatomo_clip_text_down_button) anatomo_clip_text_down_button.show();
					if(anatomo_clip_unit_label) anatomo_clip_unit_label.show();
					if(clip!='FREE' && clipImgDiv) clipImgDiv.show();

					if(anatomo_clip_predifined_plane && anatomo_clip_predifined_plane.rendered){
						if(anatomo_clip_predifined_plane.getValue() == "FB") {
							setClipImage(90,0,setClipLine);
						}else{
							setClipImage(0,0,setClipLine);
						}
					}

					if(anatomo_clip_check) anatomo_clip_check.on('check',oncheck_anatomo_clip_check);
					if(anatomo_clip_method_combo) anatomo_clip_method_combo.on('select',onselect_anatomo_clip_method_combo);
					if(anatomo_clip_predifined_plane) anatomo_clip_predifined_plane.on('select',onselect_anatomo_clip_predifined_plane);
					if(anatomo_clip_fix_check) anatomo_clip_fix_check.on('check',oncheck_anatomo_clip_fix_check);
					if(anatomo_clip_reverse_check) anatomo_clip_reverse_check.on('check',oncheck_anatomo_clip_reverse_check);
					if(anatomo_clip_slider) anatomo_clip_slider.on('change',onchange_anatomo_clip_slider);
					if(anatomo_clip_value_text) anatomo_clip_value_text.on('change',onchange_anatomo_clip_value_text);
				}
				prm_record.commit();
				prm_record.endEdit();
			}

			var new_recs = [];
//_dump("tpap_param.parts=["+tpap_param.parts.length+"]");
			if(tpap_param.parts && tpap_param.parts.length>0){
				for(var i=0,len=tpap_param.parts.length;i<len;i++){
					var part = tpap_param.parts[i];
					var f_id = part.id;
					if(!f_id && part.f_id) f_id = part.f_id;
//_dump("f_id=["+i+"]["+f_id+"]");
					if(Ext.isEmpty(fma_rec[f_id])) continue;
					var record = fma_rec[f_id];
					record.beginEdit();

//_dump("part.color=["+part.color+"]");
					if(!Ext.isEmpty(part.show)){
						record.set('color',(part.color=="NANANA"?"":"#"+part.color));
						record.set('value',(part.value=="NANANANANANA"?"":parseFloat((part.value.substr(0,1)=="M"?"-":"")+part.value.substr(1))));
						record.set('zoom', (part.show=="Z"?true:false));
						record.set('opacity',(parseFloat(part.opacity)/100));
					}else{
						record.set('color',  (!Ext.isEmpty(part.color)?('#'+part.color):'#'+prm_record.data.color_rgb));
						record.set('value',  part.value);
						record.set('zoom',   false);
						record.set('exclude',part.exclude);
						record.set('opacity',part.opacity);
						record.set('point',  part.point);
					}
					record.set('representation',(part.representation=="S"?"surface":(part.representation=="W"?"wireframe":(part.representation=="P"?"points":""))));

//_dump("record.data.color=["+record.data.color+"]");

					record.commit(true);
					record.endEdit();
					new_recs.push(record);
//_dump("record.data.tg_id=["+record.data.tg_id+"]");
				}
			}
//_dump("new_recs=["+new_recs.length+"]");


			if(tpap_param.point_parts && tpap_param.point_parts.length>0){
				for(var i=0,len=tpap_param.point_parts.length;i<len;i++){
					var part = tpap_param.point_parts[i];
					var f_id = part.id;
					if(!f_id && part.f_id) f_id = part.f_id;
//_dump("f_id=["+i+"]["+f_id+"]");
					if(Ext.isEmpty(fma_rec[f_id])) continue;
					var record = fma_rec[f_id];
					record.beginEdit();
					record.set('color',  (!Ext.isEmpty(part.color)?('#'+part.color):'#'+prm_record.data.point_color_rgb));
					record.set('value',  part.value);
					record.set('zoom',   false);
					record.set('exclude',part.exclude);
					record.set('opacity',part.opacity);
					record.set('point',  false);
					record.set('representation',(part.representation=="S"?"surface":(part.representation=="W"?"wireframe":(part.representation=="P"?"points":""))));

//_dump("record.data.color=["+record.data.color+"]");

					record.commit(true);
					record.endEdit();
					new_recs.push(record);
//_dump("record.data.tg_id=["+record.data.tg_id+"]");
				}
			}


			var ag_parts_gridpanel = Ext.getCmp('ag-parts-gridpanel');
			if(ag_parts_gridpanel){
				var store = ag_parts_gridpanel.getStore();
				store.add(new_recs);
				getConvertIdList(new_recs,store);
			}

			var anatomo_comment_store = null;
			var ag_pin_grid_panel = Ext.getCmp('anatomography-pin-grid-panel');
			if(ag_pin_grid_panel) anatomo_comment_store = ag_pin_grid_panel.getStore();

			if(anatomo_comment_store){
				anatomo_comment_store.removeAll();
				if(tpap_param.comments && tpap_param.comments.length>0){
					for (var i = 0, len = tpap_param.comments.length; i < len; i++) {
						var comment = tpap_param.comments[i];
						anatomo_comment_store.loadData([[parseIntTPAP(comment.no), comment.id, comment.name, parseFloatTPAP(comment.c3d.x), parseFloatTPAP(comment.c3d.y), parseFloatTPAP(comment.c3d.z), comment.point.rgb, comment.comment]], true);
					}
				}else if(tpap_param.pins && tpap_param.pins.length>0 && ag_comment_store_fields){
					var newRecord = Ext.data.Record.create(ag_comment_store_fields);
					var addrecs = [];
					for(var i=0,len=tpap_param.pins.length;i<len;i++){
						var pin = tpap_param.pins[i];
						var addrec = new newRecord({});

						addrec.beginEdit();
						addrec.set("no",pin.no);
						addrec.set("x3d",pin.x3d);
						addrec.set("y3d",pin.y3d);
						addrec.set("z3d",pin.z3d);
						addrec.set("avx3d",pin.avx3d);
						addrec.set("avy3d",pin.avy3d);
						addrec.set("avz3d",pin.avz3d);
						addrec.set("uvx3d",pin.uvx3d);
						addrec.set("uvy3d",pin.uvy3d);
						addrec.set("uvz3d",pin.uvz3d);
						addrec.set("color",pin.color);
						addrec.set("oid",pin.organid);
						addrec.set("organ",pin.organname);
						addrec.set("comment",(pin.comment?pin.comment:""));
						addrec.set("coord",pin.coord);
						addrec.commit(true);
						addrec.endEdit();
						addrecs.push(addrec);

						init_anatomo_pin_description_draw = pin.draw;
						init_anatomo_pin_shape = pin.shape;

						var cmp = Ext.getCmp('anatomo_pin_description_draw_check');
						if(cmp && cmp.rendered) cmp.setValue(pin.draw);

						var cmp = Ext.getCmp('anatomo_pin_description_draw_pin_indication_line_combo');
						if(cmp && cmp.rendered){
							if(pin.draw){
								cmp.enable();
							}else{
								cmp.disable();
							}
						}

						var cmp = Ext.getCmp('anatomo_pin_shape_combo');
						if(cmp && cmp.rendered) cmp.setValue(pin.shape);
					}
					anatomo_comment_store.add(addrecs);
				}
			}

			init_anatomography_image_comment_title = '';
			init_anatomography_image_comment_legend = '';
			init_anatomography_image_comment_author = '';

			if(!Ext.isEmpty(tpap_param.legendinfo)){
				if(!Ext.isEmpty(tpap_param.legendinfo.title)) init_anatomography_image_comment_title = tpap_param.legendinfo.title;
				if(!Ext.isEmpty(tpap_param.legendinfo.legend)) init_anatomography_image_comment_legend = tpap_param.legendinfo.legend;
				if(!Ext.isEmpty(tpap_param.legendinfo.author)) init_anatomography_image_comment_author = tpap_param.legendinfo.author;
				if(!Ext.isEmpty(tpap_param.legendinfo.position) && !Ext.isEmpty(tpap_param.legendinfo.color)){
					init_anatomography_image_comment_draw = true;
				}else{
					init_anatomography_image_comment_draw = false;
				}
			}

			var cmp = Ext.getCmp("anatomography_image_comment_title");
			if(cmp && cmp.rendered) cmp.setValue(init_anatomography_image_comment_title);

			var cmp = Ext.getCmp("anatomography_image_comment_legend");
			if(cmp && cmp.rendered) cmp.setValue(init_anatomography_image_comment_legend);

			var cmp = Ext.getCmp("anatomography_image_comment_author");
			if(cmp && cmp.rendered) cmp.setValue(init_anatomography_image_comment_author);

			var cmp = Ext.getCmp('anatomography_image_comment_draw_check');
			if(cmp && cmp.rendered) cmp.setValue(init_anatomography_image_comment_draw);


//2011-09-28 コメントアウト
//			if(tpap_param.parts && tpap_param.parts.length>0 && records.length>0 && contents_tabs) contents_tabs.setActiveTab('contents-tab-anatomography-panel');
//

			if(!Ext.isEmpty(gParams.tp_md) && gParams.tp_md == 1){
//_dump("CALL updateAnatomo()");
				setImageWindowSize();
			}

		}
//_dump("bp3d_contents_store.load():prm_record.data.clip_depth=["+prm_record.data.clip_depth+"]");
//	}catch(e){
//		_dump("bp3d_contents_store.load():"+e);
//	}
};

get_bp3d_buildup_logic = function(){
	var bul_id = init_bp3d_params['bul_id'] ? init_bp3d_params['bul_id'] : 3;
	try{
		bul_id = Ext.getCmp('bp3d-tree-type-combo').getValue();
	}catch(e){}
	return bul_id;
};

/////////////////////////////////////////////////////////////////////////////////////////////////////
afterLayout = function(panel){
	try{
		if(!Ext.isIE) return;
		if(!panel.rendered) return;
		if(panel.collapsed) panel.expand(false);
		var box = panel.getBox();
		if(box.x==0 && box.y==0) return;
		var width  = Ext.isEmpty(panel.initialConfig.minWidth) ?box.width :panel.initialConfig.minWidth;
		var height = Ext.isEmpty(panel.initialConfig.minHeight)?box.height:panel.initialConfig.minHeight;
		if((box.width<width && height > 0) || (width > 0 && box.height<height)){
			panel.setSize(width,height);
			panel.ownerCt.doLayout();
		}
	}catch(e){
		_dump("afterLayout():"+e);
	}
};


Ext.menu.RangeMenu.prototype.icons = {
	gt: 'css/greater_then.png',
	lt: 'css/less_then.png',
	eq: 'css/equals.png'
};
Ext.grid.filter.StringFilter.prototype.icon = 'css/find.png';

if(!String.prototype.ellipse) {
	String.prototype.ellipse = function(maxLength){
//		if(this.length > maxLength){
//			return this.substr(0, maxLength-3) + '...';
//		}
		return this;
	};
}

if(!String.prototype.sprintf) {
	String.prototype.sprintf = function(args___) {
		var rv = [], i = 0, v, width, precision, sign, idx, argv = arguments, next = 0;
		var s = (this + "     ").split(""); // add dummy 5 chars.
		var unsign = function(val) { return (val >= 0) ? val : val % 0x100000000 + 0x100000000; };
		var getArg = function() { return argv[idx ? idx - 1 : next++]; };

		for(;i<s.length-5;++i){
			if(s[i] !== "%"){
				rv.push(s[i]);
				continue;
			}
			++i, idx = 0, precision = undefined;

			// arg-index-specifier
			if (!isNaN(parseInt(s[i])) && s[i + 1] === "\$") { idx = parseInt(s[i]); i += 2; }
			// sign-specifier
			sign = (s[i] !== "#") ? false : ++i, true;
			// width-specifier
			width = (isNaN(parseInt(s[i]))) ? 0 : parseInt(s[i++]);
			// precision-specifier
			if (s[i] === "." && !isNaN(parseInt(s[i + 1]))) { precision = parseInt(s[i + 1]); i += 2; }

			switch(s[i]){
				case "d": v = parseInt(getArg()).toString(); break;
				case "u": v = parseInt(getArg()); if (!isNaN(v)) { v = unsign(v).toString(); } break;
				case "o": v = parseInt(getArg()); if (!isNaN(v)) { v = (sign ? "0"  : "") + unsign(v).toString(8); } break;
				case "x": v = parseInt(getArg()); if (!isNaN(v)) { v = (sign ? "0x" : "") + unsign(v).toString(16); } break;
				case "X": v = parseInt(getArg()); if (!isNaN(v)) { v = (sign ? "0X" : "") + unsign(v).toString(16).toUpperCase(); } break;
				case "f": v = parseFloat(getArg()).toFixed(precision); break;
				case "c": width = 0; v = getArg(); v = (typeof v === "number") ? String.fromCharCode(v) : NaN; break;
				case "s": width = 0; v = getArg().toString(); if (precision) { v = v.substring(0, precision); } break;
				case "%": width = 0; v = s[i]; break;
				default:  width = 0; v = "%" + ((width) ? width.toString() : "") + s[i].toString(); break;
			}
			if(isNaN(v)){ v = v.toString(); }
			(v.length < width) ? rv.push(" ".repeat(width - v.length), v) : rv.push(v);
		}
		return rv.join("");
	};
}
if(!String.prototype.repeat){
	String.prototype.repeat = function(n) {
		var rv = [], i = 0, sz = n || 1, s = this.toString();
		for (; i < sz; ++i) { rv.push(s); }
		return rv.join("");
	};
}

function parseFloatTPAP(str){
	try{
		return str=="NANANANANANA"?NaN:parseFloat((str.substr(0,1)=="M"?"-":"")+str.substr(1).replace(/^0+/,""));
	}catch(e){
		return NaN;
	}
}

function parseIntTPAP(str){
	try{
		return parseInt(str.replace(/^0+/,""));
	}catch(e){
		return NaN;
	}
}

function analyzeTPAP(tp_ap,aOpts){

	var defOpts = {
		pin: {
			url_prefix : null
		}
	};
	aOpts = aOpts||{};
	var convOpts = {};
	for(var key in defOpts){
		convOpts[key] = Ext.apply({},aOpts[key]||{},defOpts[key]);
	}

	var param = {};
	var param_arr = tp_ap.split("|");
	if(param_arr.length<1) return undefined;
	if(param_arr.length==1){

		//修正中（とりあえず、パーツの情報を受け取れるように修正）2009/09/09
		var tp_ap_obj = Ext.urlDecode(tp_ap,true);
		if(tp_ap_obj && Ext.isEmpty(tp_ap_obj.av)) tp_ap_obj.av = "09051901";

		if(tp_ap_obj && tp_ap_obj.av){
			if(tp_ap_obj.av == "09051901"){
				param.common = {};
				param.common.version = tp_ap_obj.av;
				if(!Ext.isEmpty(tp_ap_obj.iw)) param.common.image_w = tp_ap_obj.iw;
				if(!Ext.isEmpty(tp_ap_obj.ih)) param.common.image_h = tp_ap_obj.ih;
				if(!Ext.isEmpty(tp_ap_obj.bcl)) param.common.bg_rgb = tp_ap_obj.bcl.toUpperCase();
				if(!Ext.isEmpty(tp_ap_obj.bga)) param.common.bg_transparent = tp_ap_obj.bga;
				if(!Ext.isEmpty(tp_ap_obj.sx)) param.common.scalar_max = tp_ap_obj.sx;
				if(!Ext.isEmpty(tp_ap_obj.sn)) param.common.scalar_min = tp_ap_obj.sn;
				if(!Ext.isEmpty(tp_ap_obj.cf)) param.common.colorbar_f = tp_ap_obj.cf;
				if(!Ext.isEmpty(tp_ap_obj.hf)) param.common.heatmap_f = tp_ap_obj.hf;
				if(!Ext.isEmpty(tp_ap_obj.model)) param.common.model = tp_ap_obj.model;
				if(!Ext.isEmpty(tp_ap_obj.bv)) param.common.bp3d_version = tp_ap_obj.bv;
				if(!Ext.isEmpty(tp_ap_obj.tn)) param.common.treename = tp_ap_obj.tn;
				if(!Ext.isEmpty(tp_ap_obj.dt)) param.common.date = tp_ap_obj.dt;
				if(!Ext.isEmpty(tp_ap_obj.dl)) param.common.legend = tp_ap_obj.dl;
				if(!Ext.isEmpty(tp_ap_obj.dp)) param.common.pin = tp_ap_obj.dp;
				if(!Ext.isEmpty(tp_ap_obj.zm)) param.common.zoom = tp_ap_obj.zm;
				if(!Ext.isEmpty(tp_ap_obj.crd)) param.common.coord = tp_ap_obj.crd;
				if(!Ext.isEmpty(tp_ap_obj.fcl)) param.common.color_rgb = tp_ap_obj.fcl;

				param.common.pinno = 1;
				if(!Ext.isEmpty(tp_ap_obj.np)) param.common.pinno = tp_ap_obj.np;

				if(!Ext.isEmpty(tp_ap_obj.gdr)){
					param.common.grid = (tp_ap_obj.gdr=='true'?'1':'0');
				}else{
					param.common.grid = '0';
				}
				if(!Ext.isEmpty(tp_ap_obj.gcl)) param.common.grid_color = tp_ap_obj.gcl;
				if(!Ext.isEmpty(tp_ap_obj.gtc)) param.common.grid_len = tp_ap_obj.gtc;

				if(
					!Ext.isEmpty(tp_ap_obj.cx) || !Ext.isEmpty(tp_ap_obj.cy) || !Ext.isEmpty(tp_ap_obj.cz) ||
					!Ext.isEmpty(tp_ap_obj.tx) || !Ext.isEmpty(tp_ap_obj.ty) || !Ext.isEmpty(tp_ap_obj.tz) ||
					!Ext.isEmpty(tp_ap_obj.ux) || !Ext.isEmpty(tp_ap_obj.uy) || !Ext.isEmpty(tp_ap_obj.uz)
				){
					param.camera = {};
					if(!Ext.isEmpty(tp_ap_obj.cx) && !Ext.isEmpty(tp_ap_obj.cy) && !Ext.isEmpty(tp_ap_obj.cz) && !isNaN(tp_ap_obj.cx) && !isNaN(tp_ap_obj.cy) && !isNaN(tp_ap_obj.cz)){
						param.camera.cameraPos = {};
						if(!Ext.isEmpty(tp_ap_obj.cx)) param.camera.cameraPos.x = parseFloat(tp_ap_obj.cx);
						if(!Ext.isEmpty(tp_ap_obj.cy)) param.camera.cameraPos.y = parseFloat(tp_ap_obj.cy);
						if(!Ext.isEmpty(tp_ap_obj.cz)) param.camera.cameraPos.z = parseFloat(tp_ap_obj.cz);
					}
					if(!Ext.isEmpty(tp_ap_obj.tx) && !Ext.isEmpty(tp_ap_obj.ty) && !Ext.isEmpty(tp_ap_obj.tz) && !isNaN(tp_ap_obj.tx) && !isNaN(tp_ap_obj.ty) && !isNaN(tp_ap_obj.tz)){
						param.camera.targetPos = {};
						if(!Ext.isEmpty(tp_ap_obj.tx)) param.camera.targetPos.x = parseFloat(tp_ap_obj.tx);
						if(!Ext.isEmpty(tp_ap_obj.ty)) param.camera.targetPos.y = parseFloat(tp_ap_obj.ty);
						if(!Ext.isEmpty(tp_ap_obj.tz)) param.camera.targetPos.z = parseFloat(tp_ap_obj.tz);
					}
					if(!Ext.isEmpty(tp_ap_obj.ux) && !Ext.isEmpty(tp_ap_obj.uy) && !Ext.isEmpty(tp_ap_obj.uz) && !isNaN(tp_ap_obj.ux) && !isNaN(tp_ap_obj.uy) && !isNaN(tp_ap_obj.uz)){
						param.camera.upVec = {};
						if(!Ext.isEmpty(tp_ap_obj.ux)) param.camera.upVec.x = parseFloat(tp_ap_obj.ux);
						if(!Ext.isEmpty(tp_ap_obj.uy)) param.camera.upVec.y = parseFloat(tp_ap_obj.uy);
						if(!Ext.isEmpty(tp_ap_obj.uz)) param.camera.upVec.z = parseFloat(tp_ap_obj.uz);
					}
				}

				if(
					!Ext.isEmpty(tp_ap_obj.cm)  || !Ext.isEmpty(tp_ap_obj.cd)  || !Ext.isEmpty(tp_ap_obj.ct)  ||
					!Ext.isEmpty(tp_ap_obj.cpa) || !Ext.isEmpty(tp_ap_obj.cpb) || !Ext.isEmpty(tp_ap_obj.cpc) || !Ext.isEmpty(tp_ap_obj.cpd)
				){
					param.clip = {};
					if(!Ext.isEmpty(tp_ap_obj.cm)) param.clip.type = tp_ap_obj.cm;
					if(!Ext.isEmpty(tp_ap_obj.cd)) param.clip.depth = tp_ap_obj.cd;
					if(!Ext.isEmpty(tp_ap_obj.ct)) param.clip.method = tp_ap_obj.ct;
					if(!Ext.isEmpty(tp_ap_obj.cpa)) param.clip.paramA = parseFloat(tp_ap_obj.cpa);
					if(!Ext.isEmpty(tp_ap_obj.cpb)) param.clip.paramB = parseFloat(tp_ap_obj.cpb);
					if(!Ext.isEmpty(tp_ap_obj.cpc)) param.clip.paramC = parseFloat(tp_ap_obj.cpc);
					if(!Ext.isEmpty(tp_ap_obj.cpd)) param.clip.paramD = parseFloat(tp_ap_obj.cpd);
				}

				if(!Ext.isEmpty(tp_ap_obj.oid001) || !Ext.isEmpty(tp_ap_obj.onm001)){
					var prm_record = ag_param_store.getAt(0);
					param.parts = [];
					for(var i=0;;i++){
						var num = makeAnatomoOrganNumber(i+1);
						if(Ext.isEmpty(tp_ap_obj['oid'+num]) && Ext.isEmpty(tp_ap_obj['onm'+num])) break;
						var parts = {
							color   : prm_record.data.color_rgb,
							value   : '',
							exclude : false,
							zoom    : false,
							opacity : 1.0,
							representation : 'S',
							point   : false
						};
						if(!Ext.isEmpty(tp_ap_obj['oid'+num])) parts.f_id = tp_ap_obj['oid'+num];
						if(!Ext.isEmpty(tp_ap_obj['onm'+num])) parts.f_nm = tp_ap_obj['onm'+num];
						if(!Ext.isEmpty(tp_ap_obj['ocl'+num])) parts.color = tp_ap_obj['ocl'+num].toUpperCase();
						if(!Ext.isEmpty(tp_ap_obj['osc'+num])) parts.value = tp_ap_obj['osc'+num];
						if(!Ext.isEmpty(tp_ap_obj['osz'+num])){
							if(tp_ap_obj['osz'+num] == 'H'){
								parts.exclude = true;
							}else if(tp_ap_obj['osz'+num] == 'Z'){
								parts.zoom = true;
							}
						}
						if(!Ext.isEmpty(tp_ap_obj['oop'+num])) parts.opacity = tp_ap_obj['oop'+num];
						if(!Ext.isEmpty(tp_ap_obj['orp'+num])) parts.representation = tp_ap_obj['orp'+num];
						if(!Ext.isEmpty(tp_ap_obj['ov'+num])) parts.version = tp_ap_obj['ov'+num];
						if(!Ext.isEmpty(tp_ap_obj['odcp'+num])) parts.point = tp_ap_obj['odcp'+num]=='1'?true:false;
//_dump("parts.point=["+parts.point+"]");
						param.parts.push(parts);
					}
				}
				if(!Ext.isEmpty(tp_ap_obj.lp) || !Ext.isEmpty(tp_ap_obj.lc) || !Ext.isEmpty(tp_ap_obj.lt) || !Ext.isEmpty(tp_ap_obj.le) || !Ext.isEmpty(tp_ap_obj.la)){
					param.legendinfo = {};
					if(!Ext.isEmpty(tp_ap_obj.lp)) param.legendinfo.position = tp_ap_obj.lp;
					if(!Ext.isEmpty(tp_ap_obj.lc)) param.legendinfo.color = tp_ap_obj.lc.toUpperCase();
					if(!Ext.isEmpty(tp_ap_obj.lt)) param.legendinfo.title = tp_ap_obj.lt;
					if(!Ext.isEmpty(tp_ap_obj.le)) param.legendinfo.legend = tp_ap_obj.le;
					if(!Ext.isEmpty(tp_ap_obj.la)) param.legendinfo.author = tp_ap_obj.la;
				}
				if(!Ext.isEmpty(tp_ap_obj.pno001)){
					param.pins = [];

					var pinRecord = Ext.data.Record.create(ag_comment_store_fields);

					for(var i=0;;i++){
						var num = makeAnatomoOrganNumber(i+1);
						if(Ext.isEmpty(tp_ap_obj['pno'+num])) break;
						var pin = {};
						pin.no = i+1;
						if(!Ext.isEmpty(tp_ap_obj['px'+num]))  pin.x3d = tp_ap_obj['px'+num];
						if(!Ext.isEmpty(tp_ap_obj['py'+num]))  pin.y3d = tp_ap_obj['py'+num];
						if(!Ext.isEmpty(tp_ap_obj['pz'+num]))  pin.z3d = tp_ap_obj['pz'+num];
						if(!Ext.isEmpty(tp_ap_obj['pax'+num])) pin.avx3d = tp_ap_obj['pax'+num];
						if(!Ext.isEmpty(tp_ap_obj['pay'+num])) pin.avy3d = tp_ap_obj['pay'+num];
						if(!Ext.isEmpty(tp_ap_obj['paz'+num])) pin.avz3d = tp_ap_obj['paz'+num];
						if(!Ext.isEmpty(tp_ap_obj['pux'+num])) pin.uvx3d = tp_ap_obj['pux'+num];
						if(!Ext.isEmpty(tp_ap_obj['puy'+num])) pin.uvy3d = tp_ap_obj['puy'+num];
						if(!Ext.isEmpty(tp_ap_obj['puz'+num])) pin.uvz3d = tp_ap_obj['puz'+num];
						if(!Ext.isEmpty(tp_ap_obj['pdd'+num])) pin.draw = tp_ap_obj['pdd'+num];
						if(!Ext.isEmpty(tp_ap_obj['pdc'+num])) pin.tcolor = tp_ap_obj['pdc'+num].toUpperCase();
						if(!Ext.isEmpty(tp_ap_obj['ps'+num]))  pin.shape = tp_ap_obj['ps'+num];
						if(!Ext.isEmpty(tp_ap_obj['pcl'+num])) pin.color = tp_ap_obj['pcl'+num].toUpperCase();
						if(!Ext.isEmpty(tp_ap_obj['poi'+num])){
							pin.oid = tp_ap_obj['poi'+num];
							pin.organid = tp_ap_obj['poi'+num];
						}
						if(!Ext.isEmpty(tp_ap_obj['pon'+num])){
							pin.organ = tp_ap_obj['pon'+num];
							pin.organname = tp_ap_obj['pon'+num];
						}
						if(!Ext.isEmpty(tp_ap_obj['pd'+num]))  pin.comment = tp_ap_obj['pd'+num];
						if(!Ext.isEmpty(tp_ap_obj['pcd'+num])) pin.coord = tp_ap_obj['pcd'+num];

						if(convOpts.pin.url_prefix){
							var newPartsRecord = Ext.data.Record.create(bp3d_parts_store_fields);
							var numParts = makeAnatomoOrganNumber(1);
							var prm_record = ag_param_store.getAt(0);
							var parts_record = new newPartsRecord({
								'f_id'          : pin.oid,
								'exclude'       : false,
								'color'         : '#'+prm_record.data.color_rgb,
								'value'         : '',
								'zoom'          : false,
								'opacity'       : '1.0',
								'representation': 'surface',
								'point'         : false
							});
							var prmParts = "oid" + numParts + "=" + pin.oid;
							prmParts += makeAnatomoOrganPrm(numParts,parts_record,null,null);

							var newPinRecord = new pinRecord(pin);
							var pinPrm = makeAnatomoPrm_Pin(newPinRecord,undefined,undefined,{no:1});

							var params = Ext.urlDecode(prmParts);
							if(pinPrm) params = Ext.apply({},Ext.urlDecode(pinPrm),params);

							if(pinPrm) pin.url = convOpts.pin.url_prefix + encodeURIComponent(Ext.urlEncode(params));

							newPartsRecord = undefined;
							numParts = undefined;
							prm_record = undefined;
							parts_record = undefined;
							newPinRecord = undefined;
						}
						param.pins.push(pin);
					}
					pinRecord = undefined;
				}

				if(!Ext.isEmpty(tp_ap_obj.poid001)){
					var prm_record = ag_param_store.getAt(0);
					param.point_parts = [];
					for(var i=0;;i++){
						var num = makeAnatomoOrganNumber(i+1);
						if(Ext.isEmpty(tp_ap_obj['poid'+num])) break;
						var parts = {
							color   : prm_record.data.point_color_rgb,
							value   : '',
							exclude : false,
							zoom    : false,
							opacity : 1.0,
							representation : 'S',
							point   : false
						};
						if(!Ext.isEmpty(tp_ap_obj['poid'+num])) parts.f_id = tp_ap_obj['poid'+num];
						if(!Ext.isEmpty(tp_ap_obj['pocl'+num])) parts.color = tp_ap_obj['pocl'+num].toUpperCase();
						if(!Ext.isEmpty(tp_ap_obj['porm'+num])) parts.exclude = tp_ap_obj['porm'+num]=='1'?true:false;
						if(!Ext.isEmpty(tp_ap_obj['poop'+num])) parts.opacity = tp_ap_obj['poop'+num];
						if(!Ext.isEmpty(tp_ap_obj['pore'+num])) parts.representation = tp_ap_obj['pore'+num];
						if(!Ext.isEmpty(tp_ap_obj['posh'+num])){
							parts.point_sphere = tp_ap_obj['posh'+num];
							param.common.point_sphere = tp_ap_obj['posh'+num];
						}
						param.point_parts.push(parts);
					}
				}
				if(!Ext.isEmpty(tp_ap_obj.dpod)) param.common.point_desc = tp_ap_obj.dpod;
				if(!Ext.isEmpty(tp_ap_obj.dpl)) param.common.point_pin_line = tp_ap_obj.dpl;
				if(!Ext.isEmpty(tp_ap_obj.dpol)) param.common.point_point_line = tp_ap_obj.dpol;
				return param;
			}else{
				return undefined;
			}
		}else{
			return undefined;
		}
	}

	var prm_info = param_arr.shift();
	var p = prm_info.split(":");
	param.common = {};
	param.common.version = p[0];

	if(param.common.version == "08020601" || param.common.version == "08110101"){
		param.common.method = p[1].substr(0,1);
		param.common.viewpoint = p[1].substr(1,1);
		param.common.rotate_h = parseIntTPAP(p[1].substr(2,3));
		param.common.rotate_v = parseIntTPAP(p[1].substr(5,3));
		param.common.image_w = parseIntTPAP(p[1].substr(8,4));
		param.common.image_h = parseIntTPAP(p[1].substr(12,4));
		param.common.bg_rgb = p[1].substr(16,6);
		param.common.autoscalar_f = p[1].substr(22,1);
		param.common.scalar_max = parseFloatTPAP(p[1].substr(23,12));
		param.common.scalar_min = parseFloatTPAP(p[1].substr(35,12));
		param.common.colorbar_f = p[1].substr(47,1);
		param.common.drawsort_f = p[1].substr(48,1);
		param.common.mov_len = parseIntTPAP(p[1].substr(49,2));
		param.common.mov_fps = parseIntTPAP(p[1].substr(51,2));

	}else if(param.common.version == "09011601"){
		param.common.method = p[1].substr(0,1);
		param.common.viewpoint = p[1].substr(1,1);
		param.common.rotate_h = parseIntTPAP(p[1].substr(2,3));
		param.common.rotate_v = parseIntTPAP(p[1].substr(5,3));
		param.common.image_w = parseIntTPAP(p[1].substr(8,4));
		param.common.image_h = parseIntTPAP(p[1].substr(12,4));
		param.common.bg_rgb = p[1].substr(16,6);
		param.common.autoscalar_f = p[1].substr(22,1);
		param.common.scalar_max = parseFloatTPAP(p[1].substr(23,12));
		param.common.scalar_min = parseFloatTPAP(p[1].substr(35,12));
		param.common.colorbar_f = p[1].substr(47,1);
		param.common.drawsort_f = p[1].substr(48,1);
		param.common.mov_len = parseIntTPAP(p[1].substr(49,2));
		param.common.mov_fps = parseIntTPAP(p[1].substr(51,2));

		param.common.zoom = parseFloatTPAP(p[1].substr(53,12));
		param.common.move_x = parseFloatTPAP(p[1].substr(65,12));
		param.common.move_y = parseFloatTPAP(p[1].substr(77,12));
		param.common.move_z = parseFloatTPAP(p[1].substr(89,12));
		param.common.clip_depth = parseFloatTPAP(p[1].substr(101,12));
		param.common.clip_method = p[1].substr(113,1);
	}

	if(param_arr.length>0 && param.common.version == "08020601"){
		param.parts = [];
		for(var i=0,len=param_arr.length;i<len;i++){
			var p = param_arr[i].split(":");
			param.parts.push({
				id : p[0],
				color : (p.length<=2?p[1]:"").substr(0,6),
				value : (p.length<=2?p[1]:"").substr(6,12),
				show : (p.length<=2?p[1]:"").substr(18,1),
				opacity : (p.length<=2?p[1]:"").substr(19,3),
				representation : (p.length<=2?p[1]:"").substr(22,1)
			});
		}
	}else if(param_arr.length>0 && (param.common.version == "08110101" || param.common.version == "09011601")){
		param.parts = [];
		var parts_info = param_arr.shift();
		var parts_arr = parts_info.split("\@");
		for(var i=0,len=parts_arr.length;i<len;i++){
			var p = parts_arr[i].split(":");
			param.parts.push({
				id : p[0],
				color : (p.length<=2?p[1]:"").substr(0,6),
				value : (p.length<=2?p[1]:"").substr(6,12),
				show : (p.length<=2?p[1]:"").substr(18,1),
				opacity : (p.length<=2?p[1]:"").substr(19,3),
				representation : (p.length<=2?p[1]:"").substr(22,1)
			});
		}
	}

	if(param_arr.length>0 && (param.common.version == "08110101" || param.common.version == "09011601")){
		param.comments = [];

		var comments_info = param_arr.shift();
		var comments_arr = comments_info.split("\@");
		for(var i=0,len=comments_arr.length;i<len;i++){
			var p = comments_arr[i].split(":");
			param.comments.push({
				no : p[0].substr(0,3),
				c3d : {
					x : p[0].substr(3,12),
					y : p[0].substr(15,12),
					z : p[0].substr(27,12)
				},
				point : {
					shape : (p.length>=2?p[1]:"").substr(0,2),
					rotation : (p.length>=2?p[1]:"").substr(2,3),
					rgb : (p.length>=2?p[1]:"").substr(5,6),
					edge_rgb : (p.length>=2?p[1]:"").substr(11,6)
				},
				id : (p.length>=3?p[2]:""),
				name : (p.length>=4?p[3]:""),
				comment : (p.length>=5?p[4]:"")
			});
		}

	}
	return param;
}

function URI2Text(aURIString,aOpts){
	if(Ext.isEmpty(aURIString)) return undefined;

	var defOpts = {
		target: {
			common: true,
			camera: true,
			clip: true,
			parts: true,
			point_parts: true,
			legendinfo: true,
			pins: true
		},
		pin: {
			url_prefix : null
		}
	};
	aOpts = aOpts||{};
	var convOpts = {};
	for(var key in defOpts){
		convOpts[key] = Ext.apply({},aOpts[key]||{},defOpts[key]);
	}

	var tpap_param;
	if(typeof aURIString == 'string'){
		var search = "";
		if(aURIString.indexOf("?")>=0){
			search = aURIString.replace(/^.+\\?(.*)\$/g,"\$1");
		}else{
			return undefined;
		}
		var params = Ext.urlDecode(search);
		if(Ext.isEmpty(params.tp_ap)) params.tp_ap = search;
		tpap_param = analyzeTPAP(params.tp_ap,convOpts);
	}else if(typeof aURIString == 'object'){
		tpap_param = aURIString;
	}
	if(Ext.isEmpty(tpap_param)) return undefined;

	var key_len = 9;
	var text_value = "";
	var key_value;
	if(convOpts.target.common && !Ext.isEmpty(tpap_param.common)){

		//Version of script
		if(!Ext.isEmpty(tpap_param.common.version)){
			key_value = 'VERSION';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + tpap_param.common.version + "\\n";
		}

		//Screen size
		if(!Ext.isEmpty(tpap_param.common.image_w) && !Ext.isEmpty(tpap_param.common.image_h)){
			key_value = 'SIZE';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - W:" + tpap_param.common.image_w + ';H:' + tpap_param.common.image_h + "\\n";
		}

		//back ground color
		if(!Ext.isEmpty(tpap_param.common.bg_rgb)){
			key_value = 'BGCOLOR';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + tpap_param.common.bg_rgb + "\\n";
		}
		if(!Ext.isEmpty(tpap_param.common.bg_transparent)){
			key_value = 'BGTRANS';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + "1\\n";
		}

		//max and min for scholor color system、with ot w/o color bars
		if(!Ext.isEmpty(tpap_param.common.scalar_max) && !Ext.isEmpty(tpap_param.common.scalar_min)){
			key_value = 'SCCOLOR';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - MAX:" + tpap_param.common.scalar_max + ';MIN:' + tpap_param.common.scalar_min + "\\n";
		}
		if(!Ext.isEmpty(tpap_param.common.colorbar_f)){
			key_value = 'COLORBAR';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + tpap_param.common.colorbar_f + "\\n";
		}
		if(!Ext.isEmpty(tpap_param.common.heatmap_f)){
			key_value = 'HEATMAP';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + tpap_param.common.heatmap_f + "\\n";
		}

		//BodyParts3Dのバージョン
		if(!Ext.isEmpty(tpap_param.common.bp3d_version)){
			key_value = 'BP3DVER';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + tpap_param.common.bp3d_version + "\\n";
		}

		//Tree Name
		if(!Ext.isEmpty(tpap_param.common.treename)){
			key_value = 'TREENAME';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + tpap_param.common.treename + "\\n";
		}

		//作成日付
		if(!Ext.isEmpty(tpap_param.common.date)){
			key_value = 'DATE';
			while(key_value.length<key_len) key_value += ' ';
			var date_str = tpap_param.common.date;
			if(date_str.match(/^([0-9]{4})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})\$/)){
				var date = new Date(RegExp.\$1, RegExp.\$2, RegExp.\$3, RegExp.\$4, RegExp.\$5, RegExp.\$6);
				date_str = date.toString();
				date_str = date_str.replace(/\\(.+\$/,"").replace(/\\s+\$/,"");
			}
			text_value += key_value + " - " + date_str + "\\n";
		}

		//Legend描画フラグ
		if(!Ext.isEmpty(tpap_param.common.legend)){
			key_value = 'DRAWNOTE';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + tpap_param.common.legend + "\\n";
		}

		//Pin描画フラグ
		if(!Ext.isEmpty(tpap_param.common.pin)){
			key_value = 'DRAWPIN';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + tpap_param.common.pin + "\\n";
		}
		if(!Ext.isEmpty(tpap_param.common.pinno)){
			key_value = 'DRAWPINNO';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + tpap_param.common.pinno + "\\n";
		}

		//Zoom
		if(!Ext.isEmpty(tpap_param.common.zoom)){
			key_value = 'ZOOM';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + ((tpap_param.common.zoom*5)+1) + "\\n";
		}

		//Grid
		if(!Ext.isEmpty(tpap_param.common.grid)){
			key_value = 'GRID';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + tpap_param.common.grid + "\\n";
			if(!Ext.isEmpty(tpap_param.common.grid_color)){
				key_value = '  COLOR';
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + tpap_param.common.grid_color + "\\n";
			}
			if(!Ext.isEmpty(tpap_param.common.grid_len)){
				key_value = '  INTER';
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + tpap_param.common.grid_len + "\\n";
			}
		}

		//coordinate_system
		if(!Ext.isEmpty(tpap_param.common.coord)){
			key_value = 'COORD';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + tpap_param.common.coord + "\\n";
		}

		//Point
		if(!Ext.isEmpty(tpap_param.common.point_desc) && tpap_param.common.point_desc){
			key_value = 'POINTDESC';
			text_value += key_value + "\\n";
			key_value = '  SHOW';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + tpap_param.common.point_desc + "\\n";

			if(!Ext.isEmpty(tpap_param.common.point_pin_line)){
				key_value = '  PIN';
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + tpap_param.common.point_pin_line + "\\n";
			}

			if(!Ext.isEmpty(tpap_param.common.point_point_line)){
				key_value = '  POINT';
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + tpap_param.common.point_point_line + "\\n";
			}

			if(!Ext.isEmpty(tpap_param.common.point_sphere)){
				key_value = '  SPHERE';
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + (tpap_param.common.point_sphere=='SL'?'Large':tpap_param.common.point_sphere=='SM'?'Medium':'Small') + "\\n";
			}

		}
	}

	if(convOpts.target.camera && !Ext.isEmpty(tpap_param.camera)){
		key_value = 'CAMERA';
//		while(key_value.length<key_len) key_value += ' ';
		text_value += key_value + "\\n";

		if(!Ext.isEmpty(tpap_param.camera.cameraPos)){
			key_value = '  COORD';	//coordination of camera and object(x,y,z)
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - X:" + tpap_param.camera.cameraPos.x + ';Y:' + tpap_param.camera.cameraPos.y + ';Z:' + tpap_param.camera.cameraPos.z + "\\n";
		}
		if(!Ext.isEmpty(tpap_param.camera.targetPos)){
			key_value = '  VECTOR';	//direction of camera(x,y,z)
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - X:" + tpap_param.camera.targetPos.x + ';Y:' + tpap_param.camera.targetPos.y + ';Z:' + tpap_param.camera.targetPos.z + "\\n";
		}
		if(!Ext.isEmpty(tpap_param.camera.upVec)){
			key_value = '  UP';	//magnify
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - X:" + tpap_param.camera.upVec.x + ';Y:' + tpap_param.camera.upVec.y + ';Z:' + tpap_param.camera.upVec.z + "\\n";
		}
	}

HTML
if($sectionalViewHidden ne 'true'){
	print <<HTML;
	if(convOpts.target.clip && !Ext.isEmpty(tpap_param.clip)){
		key_value = 'CLIP';
//		while(key_value.length<key_len) key_value += ' ';
		text_value += key_value + "\\n";
		if(!Ext.isEmpty(tpap_param.clip.type)){
			key_value = '  TYPE';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + (tpap_param.clip.type=='D'?'depth':(tpap_param.clip.type=='P'?'plane':'none')) + "\\n";
		}
		if(!Ext.isEmpty(tpap_param.clip.depth)){
			key_value = '  DEPTH';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + tpap_param.clip.depth + "\\n";
		}
		if(!Ext.isEmpty(tpap_param.clip.method)){
			key_value = '  METHOD';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + (tpap_param.clip.method=='S'?'section1':(tpap_param.clip.method=='NS'?'section1_normal':'normal')) + "\\n";
		}
		if(!Ext.isEmpty(tpap_param.clip.paramA) && !Ext.isEmpty(tpap_param.clip.paramB) && !Ext.isEmpty(tpap_param.clip.paramC) && !Ext.isEmpty(tpap_param.clip.paramD)){
			key_value = '  PARAM';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - ";
			text_value += "A:" + tpap_param.clip.paramA + ";";
			text_value += "B:" + tpap_param.clip.paramB + ";";
			text_value += "C:" + tpap_param.clip.paramC + ";";
			text_value += "D:" + tpap_param.clip.paramD;
			text_value += "\\n";
		}
	}
HTML
}
print <<HTML;



	if(convOpts.target.parts && !Ext.isEmpty(tpap_param.parts) && tpap_param.parts.length>0){
		key_value = 'PARTS';
		text_value += key_value + "\\n";

		for(var p=0,len=tpap_param.parts.length;p<len;p++){
			var part = tpap_param.parts[p];

			if(!Ext.isEmpty(part.f_id)){
				key_value = '  ID';	//臓器ID(FMAID)
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + part.f_id + "\\n";
			}
			if(!Ext.isEmpty(part.f_nm)){
				key_value = '  NAME';	//臓器NAME
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + part.f_nm + "\\n";
			}
			if(!Ext.isEmpty(part.version)){
				key_value = '  VERSION';	//バージョン
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + part.version + "\\n";
			}
			if(!Ext.isEmpty(part.color)){
				key_value = '  COLOR';	//臓器色(RGB)
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + part.color + "\\n";
			}
			if(!Ext.isEmpty(part.value)){
				key_value = '  SCALAR';	//スカラー値
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + part.value + "\\n";
			}
			if(!Ext.isEmpty(part.opacity)){
				key_value = '  OPACITY';	//不透明度
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + part.opacity + "\\n";
			}
			if(!Ext.isEmpty(part.representation)){
				key_value = '  REPRE';	//表現方法
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + (part.representation=='P'?'points':(part.representation=='W'?'wireframe':'surface')) + "\\n";
			}
			if(!Ext.isEmpty(part.exclude) || !Ext.isEmpty(part.zoom)){
				key_value = '  STATE';	//状態フラグ
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + (part.exclude?'delete':(part.zoom?'focus':'show')) + "\\n";
			}
			if(!Ext.isEmpty(part.point)){
				key_value = '  POINT';	//POINT表示フラグ
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + (part.point?1:0) + "\\n";
			}
		}
	}


	if(convOpts.target.point_parts && !Ext.isEmpty(tpap_param.point_parts) && tpap_param.point_parts.length>0){
		key_value = 'POINTPARTS';
		text_value += key_value + "\\n";

		for(var p=0,len=tpap_param.point_parts.length;p<len;p++){
			var part = tpap_param.point_parts[p];

			if(!Ext.isEmpty(part.f_id)){
				key_value = '  ID';	//臓器ID(FMAID)
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + part.f_id + "\\n";
			}
			if(!Ext.isEmpty(part.f_nm)){
				key_value = '  NAME';	//臓器NAME
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + part.f_nm + "\\n";
			}
			if(!Ext.isEmpty(part.version)){
				key_value = '  VERSION';	//バージョン
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + part.version + "\\n";
			}
			if(!Ext.isEmpty(part.color)){
				key_value = '  COLOR';	//臓器色(RGB)
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + part.color + "\\n";
			}
			if(!Ext.isEmpty(part.value)){
				key_value = '  SCALAR';	//スカラー値
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + part.value + "\\n";
			}
			if(!Ext.isEmpty(part.opacity)){
				key_value = '  OPACITY';	//不透明度
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + part.opacity + "\\n";
			}
			if(!Ext.isEmpty(part.representation)){
				key_value = '  REPRE';	//表現方法
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + (part.representation=='P'?'points':(part.representation=='W'?'wireframe':'surface')) + "\\n";
			}
			if(!Ext.isEmpty(part.exclude) || !Ext.isEmpty(part.zoom)){
				key_value = '  STATE';	//状態フラグ
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + (part.exclude?'delete':(part.zoom?'focus':'show')) + "\\n";
			}
		}
	}


	if(convOpts.target.legendinfo && !Ext.isEmpty(tpap_param.legendinfo)){
		key_value = 'NOTE';
//		while(key_value.length<key_len) key_value += ' ';
		text_value += key_value + "\\n";

		if(!Ext.isEmpty(tpap_param.legendinfo.title)){
			key_value = '  TITLE';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - ";
			text_value += tpap_param.legendinfo.title;
			text_value += "\\n";
		}

		if(!Ext.isEmpty(tpap_param.legendinfo.legend)){
			key_value = '  LEGEND';
			while(key_value.length<key_len) key_value += ' ';
			var text_arr = tpap_param.legendinfo.legend.replace(/0x0d0x0a|0x0d|0x0a|\\r\\n/g,"\\n").replace(/\\n\$/g,"").split("\\n");
			text_value += key_value + " - " + text_arr[0] + "\\n";
			if(text_arr.length>1){
				key_value = '';
				while(key_value.length<key_len) key_value += ' ';
				for(var text_cnt=1;text_cnt<text_arr.length;text_cnt++){
					text_value += key_value + "   " + text_arr[text_cnt] + "\\n";
				}
			}
		}

		if(!Ext.isEmpty(tpap_param.legendinfo.author)){
			key_value = '  AUTHOR';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - ";
			text_value += tpap_param.legendinfo.author;
			text_value += "\\n";
		}

		if(!Ext.isEmpty(tpap_param.legendinfo.position)){
			key_value = '  DISP';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - ";
			text_value += tpap_param.legendinfo.position;
			text_value += "\\n";
		}

		if(!Ext.isEmpty(tpap_param.legendinfo.color)){
			key_value = '  COLOR';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - ";
			text_value += tpap_param.legendinfo.color;
			text_value += "\\n";
		}
	}

	if(convOpts.target.pins && !Ext.isEmpty(tpap_param.pins) && tpap_param.pins.length>0){
		key_value = 'PIN';
//		while(key_value.length<key_len) key_value += ' ';
		text_value += key_value + "\\n";

		for(var p=0,len=tpap_param.pins.length;p<len;p++){
			var pin = tpap_param.pins[p];

			if(!Ext.isEmpty(pin.no)){
				key_value = '  NO';	//ピン番号
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + pin.no + "\\n";
			}

			if(!Ext.isEmpty(pin.organid)){
				key_value = '  ID';	//臓器ID (FMAID)
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + pin.organid + "\\n";
			}

			if(!Ext.isEmpty(pin.organname)){
				key_value = '  ORGAN';	//臓器名
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + pin.organname + "\\n";
			}

			if(!Ext.isEmpty(pin.comment)){
				key_value = '  DESC';	//PINの説明
				while(key_value.length<key_len) key_value += ' ';
				var text_arr = pin.comment.replace(/0x0d0x0a|0x0d|0x0a|\\r\\n/g,"\\n").replace(/\\n\$/g,"").split("\\n");
				text_value += key_value + " - " + text_arr[0] + "\\n";
				if(text_arr.length>1){
					key_value = '';
					while(key_value.length<key_len) key_value += ' ';
					for(var text_cnt=1;text_cnt<text_arr.length;text_cnt++){
						text_value += key_value + "   " + text_arr[text_cnt] + "\\n";
					}
				}
			}

			if(!Ext.isEmpty(pin.shape)){
				key_value = '  SHAPE';	//PINの形状
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + (pin.shape=='PS'?'Pin S':(pin.shape=='PM'?'Pin M':(pin.shape=='PL'?'Pin L':(pin.shape=='CC'?'Corn':'Circle')))) + "\\n";
			}

			if(!Ext.isEmpty(pin.color)){
				key_value = '  PCOLOR';	//PINの色
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + pin.color + "\\n";
			}

			if(!Ext.isEmpty(pin.tcolor)){
				key_value = '  TCOLOR';	//説明の色
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + pin.tcolor + "\\n";
			}

			if(!Ext.isEmpty(pin.draw)){
				key_value = '  DRAW';	//PINの説明表示・非表示
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + pin.draw + "\\n";
			}

			if(!Ext.isEmpty(pin.x3d) && !Ext.isEmpty(pin.y3d) && !Ext.isEmpty(pin.z3d)){
				key_value = '  COORD';	//ピン座標
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - X:" + pin.x3d + ";Y:" + pin.y3d + ";Z:" + pin.z3d + "\\n";
			}

			if(!Ext.isEmpty(pin.avx3d) && !Ext.isEmpty(pin.avy3d) && !Ext.isEmpty(pin.avz3d)){
				key_value = '  VECTOR';	//法線ベクトル
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - X:" + pin.avx3d + ";Y:" + pin.avy3d + ";Z:" + pin.avz3d + "\\n";
			}

			if(!Ext.isEmpty(pin.uvx3d) && !Ext.isEmpty(pin.uvy3d) && !Ext.isEmpty(pin.uvz3d)){
				key_value = '  UP';	//上方向を示す座標
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - X:" + pin.uvx3d + ";Y:" + pin.uvy3d + ";Z:" + pin.uvz3d + "\\n";
			}

			if(!Ext.isEmpty(pin.coord)){
				key_value = '  SCOORD';	//描画座標系
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + pin.coord + "\\n";
			}

			if(!Ext.isEmpty(pin.url)){
				key_value = '  URL';	//描画座標系
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + pin.url + "\\n";
			}
		}
	}

	if(text_value == "") return undefined;
	return text_value + '//\\n\\n';
}

function Text2URI(aFlatTextString,aOpts){
	if(!aFlatTextString) return "";

	var defOpts = {
		target: {
			common: true,
			camera: true,
			clip: true,
			parts: true,
			point_parts: true,
			legendinfo: true,
			pins: true
		}
	};
	aOpts = aOpts||{};
	var convOpts = {};
	for(var key in defOpts){
		convOpts[key] = Ext.apply({},aOpts[key]||{},defOpts[key]);
	}

	var text_arr = aFlatTextString.replace(/0x0d0x0a|0x0d|0x0a|\\r\\n/g,"\\n").replace(/\\n\$/g,"").split("\\n");
	var param = {};
	var camera = 0;
	var clip = 0;
	var parts = 0;
	var point_parts = 0;
	var note = 0;
	var pin = 0;
	var grid = 0;
	var point_desc = 0;
	var parts_no = "";
	var pin_no = "";
	for(var i=0,len=text_arr.length;i<len;i++){
		next_line:
		if(convOpts.target.common && text_arr[i].match(/^VERSION\\s+-\\s+([0-9]{8})\$/)){
			param.av = RegExp.\$1;
		}else if(convOpts.target.common && text_arr[i].match(/^SIZE\\s+-\\s+W:([0-9]+);H:([0-9]+)\$/)){
			param.iw = RegExp.\$1;
			param.ih = RegExp.\$2;
		}else if(convOpts.target.common && text_arr[i].match(/^BGCOLOR\\s+-\\s+([0-9A-Fa-f]{6})\$/)){
			param.bcl = RegExp.\$1;
		}else if(convOpts.target.common && text_arr[i].match(/^BGTRANS\\s+-\\s+([0-9]+)\$/)){
			param.bga = "0";
		}else if(convOpts.target.common && text_arr[i].match(/^SCCOLOR\\s+-\\s+MAX:([0-9]+);MIN:([0-9]+)\$/)){
			param.sx = RegExp.\$1;
			param.sn = RegExp.\$2;
		}else if(convOpts.target.common && text_arr[i].match(/^COLORBAR\\s+-\\s+([0-9]+)\$/)){
			param.cf = RegExp.\$1;
		}else if(convOpts.target.common && text_arr[i].match(/^HEATMAP\\s+-\\s+([0-9]+)\$/)){
			param.hf = RegExp.\$1;
		}else if(convOpts.target.common && text_arr[i].match(/^BP3DVER\\s+-\\s+([0-9\\.]+)\$/)){
			param.bv = RegExp.\$1;
		}else if(convOpts.target.common && text_arr[i].match(/^TREENAME\\s+-\\s+([A-Za-z]+)\$/)){
			param.tn = RegExp.\$1;
		}else if(convOpts.target.common && text_arr[i].match(/^DATE\\s+-\\s+(\\S.+)\$/)){
			param.dt = RegExp.\$1;
			if(param.dt.match(/[^0-9]+/)){
				var date = new Date(param.dt);
				var yy = date.getYear();
				var mm = date.getMonth();
				var dd = date.getDate();
				var h = date.getHours();
				var m = date.getMinutes();
				var s = date.getSeconds();
				if(yy < 2000) { yy += 1900; }
				if(mm < 10) { mm = "0" + mm; }
				if(dd < 10) { dd = "0" + dd; }
				param.dt = "" + yy + mm + dd + h + m + s;
			}
		}else if(convOpts.target.common && text_arr[i].match(/^DRAWNOTE\\s+-\\s+([0-9]+)\$/)){
			param.dl = RegExp.\$1;
		}else if(convOpts.target.common && text_arr[i].match(/^DRAWPIN\\s+-\\s+([0-9]+)\$/)){
			param.dp = RegExp.\$1;
		}else if(convOpts.target.common && text_arr[i].match(/^DRAWPINNO\\s+-\\s+([01]+)\$/)){
			param.np = RegExp.\$1;
		}else if(convOpts.target.common && text_arr[i].match(/^ZOOM\\s+-\\s+([0-9]+)\$/)){
			param.zm = RegExp.\$1;
			param.zm = (param.zm-1)/5;
		}else if(convOpts.target.common && (text_arr[i].match(/^GRID\\s+-\\s+([01]+)\$/) || grid)){
			if(!grid){
				param.gdr = RegExp.\$1;
				param.gdr = param.gdr=='1'?'true':'false';
				grid = 1;
			}else if(text_arr[i].match(/^\\s+COLOR\\s+-\\s+([0-9A-Fa-f]{6})\$/)){
				param.gcl = RegExp.\$1;
			}else if(text_arr[i].match(/^\\s+INTER\\s+-\\s+([0-9]+)\$/)){
				param.gtc = RegExp.\$1;
			}else{
				grid = 0;
				i--;
				continue;
			}

		}else if(convOpts.target.common && (text_arr[i].match(/^POINTDESC\\s*\$/) || point_desc)){
			if(!point_desc){
				point_desc = 1;
				param.dpod = 1;
			}else if(text_arr[i].match(/^PIN\\s+-\\s+([012]+)\$/)){
				param.dpl = RegExp.\$1;
			}else if(text_arr[i].match(/^POINT\\s+-\\s+([012]+)\$/)){
				param.dpol = RegExp.\$1;
			}else{
				point_desc = 0;
				i--;
				continue;
			}

		}else if(convOpts.target.common && text_arr[i].match(/^COORD\\s+-\\s+([A-Za-z0-9]+)\$/)){
			param.crd = RegExp.\$1;
		}else if(convOpts.target.camera && (text_arr[i].match(/^CAMERA\\s*\$/) || camera)){
			if(!camera){
				camera = 1;
			}else if(text_arr[i].match(/^\\s+COORD\\s+-\\s+X:([0-9\\.\\-]+);Y:([0-9\\.\\-]+);Z:([0-9\\.\\-]+)\$/)){
				param.cx = RegExp.\$1;
				param.cy = RegExp.\$2;
				param.cz = RegExp.\$3;
			}else if(text_arr[i].match(/^\\s+VECTOR\\s+-\\s+X:([0-9\\.\\-]+);Y:([0-9\\.\\-]+);Z:([0-9\\.\\-]+)\$/)){
				param.tx = RegExp.\$1;
				param.ty = RegExp.\$2;
				param.tz = RegExp.\$3;
			}else if(text_arr[i].match(/^\\s+UP\\s+-\\s+X:([0-9\\.\\-]+);Y:([0-9\\.\\-]+);Z:([0-9\\.\\-]+)\$/)){
				param.ux = RegExp.\$1;
				param.uy = RegExp.\$2;
				param.uz = RegExp.\$3;
			}else{
				camera = 0;
				i--;
				continue;
			}
		}else if(convOpts.target.clip && (text_arr[i].match(/^CLIP\\s*\$/) || clip)){
			if(!clip){
				clip = 1;
			}else if(text_arr[i].match(/^\\s+TYPE\\s+-\\s+(\\S+)\$/)){
				param.cm = RegExp.\$1;
				if(param.cm == 'depth'){
					param.cm = 'D';
				}else if(param.cm == 'plane'){
					param.cm = 'P';
				}else{
					param.cm = 'N';
				}
			}else if(text_arr[i].match(/^\\s+DEPTH\\s+-\\s+(\\S+)\$/)){
				param.cd = RegExp.\$1;
			}else if(text_arr[i].match(/^\\s+METHOD\\s+-\\s+(\\S+)\$/)){
				param.ct = RegExp.\$1;
				if(param.ct == 'section1'){
					param.ct = 'S';
				}else if(param.ct == 'section1_normal'){
					param.ct = 'NS';
				}else{
					param.ct = 'N';
				}
			}else if(text_arr[i].match(/^\\s+PARAM\\s+-\\s+A:([0-9\\.\\-]+);B:([0-9\\.\\-]+);C:([0-9\\.\\-]+);D:([0-9\\.\\-]+)\$/)){
				param.cpa = RegExp.\$1;
				param.cpb = RegExp.\$2;
				param.cpc = RegExp.\$3;
				param.cpd = RegExp.\$4;
			}else{
				clip = 0;
				i--;
				continue;
			}
		}else if(convOpts.target.parts && (text_arr[i].match(/^PARTS\\s*\$/) || parts)){
			if(!parts){
				parts = 1;
			}else if(text_arr[i].match(/^\\s+ID\\s+-\\s+(\\S+)\$/)){
				var val = RegExp.\$1;
				parts++;
//				parts_no = (parts-1)+"";
//				while (parts_no.length < 3) parts_no = "0" + parts_no;
				parts_no = makeAnatomoOrganNumber(parts-1);
				param["oid"+parts_no] = val;
			}else if(text_arr[i].match(/^\\s+NAME\\s+-\\s+(.+)\$/)){
				var val = RegExp.\$1;
				parts++;
//				parts_no = (parts-1)+"";
//				while (parts_no.length < 3) parts_no = "0" + parts_no;
				parts_no = makeAnatomoOrganNumber(parts-1);
				param["onm"+parts_no] = val;
			}else if(text_arr[i].match(/^\\s+VERSION\\s+-\\s+([0-9\\.]+)\$/)){
				param["ov"+parts_no] = RegExp.\$1;
			}else if(text_arr[i].match(/^\\s+COLOR\\s+-\\s+#*([0-9A-Fa-f]{6})\$/)){
				param["ocl"+parts_no] = RegExp.\$1;
			}else if(text_arr[i].match(/^\\s+SCALAR\\s+-\\s+(\\S+)\$/)){
				param["osc"+parts_no] = RegExp.\$1;
			}else if(text_arr[i].match(/^\\s+OPACITY\\s+-\\s+([0-9\\.]+)\$/)){
				param["oop"+parts_no] = RegExp.\$1;
			}else if(text_arr[i].match(/^\\s+REPRE\\s+-\\s+(\\S+)\$/)){
				param["orp"+parts_no] = RegExp.\$1;
				if(param["orp"+parts_no] == 'surface'){
					param["orp"+parts_no] = 'S';
				}else if(param["orp"+parts_no] == 'wireframe'){
					param["orp"+parts_no] = 'W';
				}else if(param["orp"+parts_no] == 'points'){
					param["orp"+parts_no] = 'P';
				}
			}else if(text_arr[i].match(/^\\s+STATE\\s+-\\s+(\\S+)\$/)){
				param["osz"+parts_no] = RegExp.\$1;
				if(param["osz"+parts_no] == 'show'){
					param["osz"+parts_no] = 'S';
				}else if(param["osz"+parts_no] == 'focus'){
					param["osz"+parts_no] = 'Z';
				}else if(param["osz"+parts_no] == 'delete'){
					param["osz"+parts_no] = 'H';
				}
			}else if(text_arr[i].match(/^\\s+POINT\\s+-\\s+(\\S+)\$/)){
				param["odcp"+parts_no] = RegExp.\$1;
			}else{
				parts = 0;
				i--;
				continue;
			}
		}else if(convOpts.target.point_parts && (text_arr[i].match(/^POINTPARTS\\s*\$/) || point_parts)){
			if(!point_parts){
				point_parts = 1;
			}else if(text_arr[i].match(/^\\s+ID\\s+-\\s+(\\S+)\$/)){
				var val = RegExp.\$1;
				parts++;
//				parts_no = (parts-1)+"";
//				while (parts_no.length < 3) parts_no = "0" + parts_no;
				parts_no = makeAnatomoOrganNumber(parts-1);
				param["oid"+parts_no] = val;
			}else if(text_arr[i].match(/^\\s+NAME\\s+-\\s+(.+)\$/)){
				var val = RegExp.\$1;
				parts++;
//				parts_no = (parts-1)+"";
//				while (parts_no.length < 3) parts_no = "0" + parts_no;
				parts_no = makeAnatomoOrganNumber(parts-1);
				param["onm"+parts_no] = val;
			}else if(text_arr[i].match(/^\\s+VERSION\\s+-\\s+([0-9\\.]+)\$/)){
				param["ov"+parts_no] = RegExp.\$1;
			}else if(text_arr[i].match(/^\\s+COLOR\\s+-\\s+#*([0-9A-Fa-f]{6})\$/)){
				param["ocl"+parts_no] = RegExp.\$1;
			}else if(text_arr[i].match(/^\\s+SCALAR\\s+-\\s+(\\S+)\$/)){
				param["osc"+parts_no] = RegExp.\$1;
			}else if(text_arr[i].match(/^\\s+OPACITY\\s+-\\s+([0-9\\.]+)\$/)){
				param["oop"+parts_no] = RegExp.\$1;
			}else if(text_arr[i].match(/^\\s+REPRE\\s+-\\s+(\\S+)\$/)){
				param["orp"+parts_no] = RegExp.\$1;
				if(param["orp"+parts_no] == 'surface'){
					param["orp"+parts_no] = 'S';
				}else if(param["orp"+parts_no] == 'wireframe'){
					param["orp"+parts_no] = 'W';
				}else if(param["orp"+parts_no] == 'points'){
					param["orp"+parts_no] = 'P';
				}
			}else if(text_arr[i].match(/^\\s+STATE\\s+-\\s+(\\S+)\$/)){
				param["osz"+parts_no] = RegExp.\$1;
				if(param["osz"+parts_no] == 'show'){
					param["osz"+parts_no] = 'S';
				}else if(param["osz"+parts_no] == 'focus'){
					param["osz"+parts_no] = 'Z';
				}else if(param["osz"+parts_no] == 'delete'){
					param["osz"+parts_no] = 'H';
				}
			}else{
				point_parts = 0;
				i--;
				continue;
			}
		}else if(convOpts.target.legendinfo && (text_arr[i].match(/^NOTE\\s*\$/) || note)){
			if(!note){
				note = 1;
			}else if(text_arr[i].match(/^\\s+TITLE\\s+-\\s+(\\S.*)\$/)){
				param.lt = RegExp.\$1;
			}else if(text_arr[i].match(/^\\s+LEGEND\\s+-\\s+(\\S.*)\$/) || text_arr[i].match(/^\\s{9,}(\\S.*)\$/)){
				if(text_arr[i].match(/^\\s+LEGEND\\s+-\\s+(\\S.*)\$/)){
					param.le = RegExp.\$1;
				}else if(text_arr[i].match(/^\\s{9,}(\\S.*)\$/)){
					param.le += ' ' + RegExp.\$1;
				}
			}else if(text_arr[i].match(/^\\s+AUTHOR\\s+-\\s+(\\S.*)\$/)){
				param.la = RegExp.\$1;
			}else if(text_arr[i].match(/^\\s+DISP\\s+-\\s+(\\S.*)\$/)){
				param.lp = RegExp.\$1;
			}else if(text_arr[i].match(/^\\s+COLOR\\s+-\\s+#*([0-9A-Fa-f]{6})\$/)){
				param.lc = RegExp.\$1;
			}else{
				note = 0;
				i--;
				continue;
			}
		}else if(convOpts.target.pins && (text_arr[i].match(/^PIN\\s*\$/) || pin)){
			if(!pin){
				pin = 1;
			}else if(text_arr[i].match(/^\\s+NO\\s+-\\s+([0-9]+)\$/)){
				var val = RegExp.\$1;
//				pin_no = val+"";
//				while (pin_no.length < 3) pin_no = "0" + pin_no;
				pin_no = makeAnatomoOrganNumber(val-0);
				param["pno"+pin_no] = val;
			}else if(text_arr[i].match(/^\\s+ID\\s+-\\s+(\\S.*)\$/)){
				param["poi"+pin_no] = RegExp.\$1;
			}else if(text_arr[i].match(/^\\s+ORGAN\\s+-\\s+(\\S.*)\$/)){
				param["pon"+pin_no] = RegExp.\$1;
			}else if(text_arr[i].match(/^\\s+DESC\\s+-\\s+(\\S.*)\$/) || text_arr[i].match(/^\\s{9,}(\\S.*)\$/)){
				param["pd"+pin_no] = RegExp.\$1;
			}else if(text_arr[i].match(/^\\s+SHAPE\\s+-\\s+(\\S.*)\$/)){
				param["ps"+pin_no] = RegExp.\$1;
				if(param["ps"+pin_no] == 'Corn'){
					param["ps"+pin_no] = 'CC';
				}else if(param["ps"+pin_no] == 'Pin L'){
					param["ps"+pin_no] = 'PL';
				}else if(param["ps"+pin_no] == 'Pin M'){
					param["ps"+pin_no] = 'PM';
				}else if(param["ps"+pin_no] == 'Pin S'){
					param["ps"+pin_no] = 'PS';
				}else{
					param["ps"+pin_no] = 'SC';
				}
			}else if(text_arr[i].match(/^\\s+PCOLOR\\s+-\\s+#*([0-9A-Fa-f]{6})\$/)){
				param["pcl"+pin_no] = RegExp.\$1;
			}else if(text_arr[i].match(/^\\s+TCOLOR\\s+-\\s+#*([0-9A-Fa-f]{6})\$/)){
				param["pcl"+pin_no] = RegExp.\$1;
			}else if(text_arr[i].match(/^\\s+DRAW\\s+-\\s+(\\S.*)\$/)){
				param["pdd"+pin_no] = RegExp.\$1;
			}else if(text_arr[i].match(/^\\s+COORD\\s+-\\s+X:([0-9\\.\\-]+);Y:([0-9\\.\\-]+);Z:([0-9\\.\\-]+)\$/)){
				param["px"+pin_no] = RegExp.\$1;
				param["py"+pin_no] = RegExp.\$2;
				param["pz"+pin_no] = RegExp.\$3;
			}else if(text_arr[i].match(/^\\s+VECTOR\\s+-\\s+X:([0-9\\.\\-]+);Y:([0-9\\.\\-]+);Z:([0-9\\.\\-]+)\$/)){
				param["pax"+pin_no] = RegExp.\$1;
				param["pay"+pin_no] = RegExp.\$2;
				param["paz"+pin_no] = RegExp.\$3;
			}else if(text_arr[i].match(/^\\s+UP\\s+-\\s+X:([0-9\\.\\-]+);Y:([0-9\\.\\-]+);Z:([0-9\\.\\-]+)\$/)){
				param["pux"+pin_no] = RegExp.\$1;
				param["puy"+pin_no] = RegExp.\$2;
				param["puz"+pin_no] = RegExp.\$3;
			}else if(text_arr[i].match(/^\\s+SCOORD\\s+-\\s+(\\S.*)\$/)){
				param["coord"+pin_no] = RegExp.\$1;
			}else if(text_arr[i].match(/^\\s+URL\\s+-\\s+(\\S.*)\$/)){
			}else{
				pin = 0;
				i--;
				continue;
			}
		}
	}


	var search = Ext.urlEncode(param);
	var editURL = getEditUrl();
	editURL = editURL + "?tp_ap=" + encodeURIComponent(search);
	return editURL;
}


var bp3d_parts_store_fields = [
	{name:'f_id'},
	{name:'b_id'},
	{name:'name_j'},
	{name:'name_e'},
	{name:'name_k'},
	{name:'name_l'},
	{name:'phase'},
	{name:'version'},
	{name:'tg_id',convert:function(v,r){
		if(Ext.isEmpty(v)){
			return r.md_id;
		}else{
			return v;
		}
	}},
	{name:'tgi_id',convert:function(v,r){
		if(Ext.isEmpty(v)){
			return r.mv_id;
		}else{
			return v;
		}
	}},
	{name:'entry',type: 'date', dateFormat: 'timestamp'},
	{name:'xmin',type:'float'},
	{name:'xmax',type:'float'},
	{name:'ymin',type:'float'},
	{name:'ymax',type:'float'},
	{name:'zmin',type:'float'},
	{name:'zmax',type:'float'},
	{name:'volume',type:'float'},
	{name:'organsys'},
	{name:'color'},
	{name:'value'},
	{name:'zoom',type:'boolean'},
	{name:'exclude',type:'boolean'},
	{name:'opacity',type:'float'},
	{name:'representation'},
	{name:'def_color'},
	{name:'conv_id'},
	{name:'common_id'},
	{name:'point',type:'boolean'},
	{name:'elem_type'},
	{name:'point_label'},
	{name:'bul_id',type:'int'},
	{name:'cb_id',type:'int'},
	{name:'ci_id',type:'int'},
	{name:'md_id',type:'int'},
	{name:'mv_id',type:'int'},
	{name:'mr_id',type:'int'},
	{name:'but_cnum',type:'int'},
	{name:'icon',type:'string'},

	{name:'tweet_num',type:'int',defaultValue:0},
	{name:'tweets',type:'auto'},

	'model',
	'model_version',
	'concept_info',
	'concept_build',
	'buildup_logic',
	{name:'bu_revision',type:'int'}
];

bp3d_parts_store = new Ext.data.SimpleStore({
	fields : bp3d_parts_store_fields,
	root   : 'records',
	listeners : {
		"add" : function(store,records,index){
			addPartslistGrid(store,records,index);
		},
		"remove" : function(store,record,index){
			removePartslistGrid(store,record,index);
		},
		"update" : function(store,record,operation){
			updatePartslistGrid(store,record,operation);
		},
		"clear" : function(store){
		}
	}
})
bp3d_parts_store.loadData([]);

var ag_comment_store_fields = [
	{name:'no'},
	{name:'oid'},
	{name:'organ'},
	{name:'x3d'},
	{name:'y3d'},
	{name:'z3d'},
	{name:'avx3d'},
	{name:'avy3d'},
	{name:'avz3d'},
	{name:'uvx3d'},
	{name:'uvy3d'},
	{name:'uvz3d'},
	{name:'color'},
	{name:'comment'},
	{name:'name_j'},
	{name:'name_k'},
	{name:'name_l'},
	{name:'coord'}
];
var ag_comment_store = new Ext.data.SimpleStore({
	fields : ag_comment_store_fields,
	root : 'records',
	listeners : {
		'add' : function(store,records,index){
			if(Ext.isEmpty(records) || records.length==0 || index<0) return;

			var grid = Ext.getCmp('anatomography-pin-grid-panel');
			if(grid && grid.rendered){
				setTimeout(function(){try{
					grid.getView().focusRow(index);
					grid. getSelectionModel().selectRow(index);
				}catch(e){}},100);
			}

			var pick_data = {f_ids:[]};
			for(var i=0;i<records.length;i++){
				pick_data.f_ids.push(records[i].data.oid);
			}
			pick_data.f_ids = Ext.util.JSON.encode(pick_data.f_ids);
			try{pick_data.version = Ext.getCmp('bp3d-version-combo').getValue();}catch(e){pick_data.version='$tgi_version';}

			if(init_bp3d_params.version) pick_data.version = init_bp3d_params.version;
			if(init_bp3d_params.t_type) pick_data.t_type = init_bp3d_params.t_type;
			if(init_bp3d_params.tgi_id) pick_data.tgi_id = init_bp3d_params.tgi_id;
			if(init_bp3d_params.md_id) pick_data.md_id = init_bp3d_params.md_id;
			if(init_bp3d_params.mv_id) pick_data.mv_id = init_bp3d_params.mv_id;
			if(init_bp3d_params.mr_id) pick_data.mr_id = init_bp3d_params.mr_id;
			if(init_bp3d_params.bul_id) pick_data.bul_id = init_bp3d_params.bul_id;
			if(init_bp3d_params.cb_id) pick_data.cb_id = init_bp3d_params.cb_id;
			if(init_bp3d_params.ci_id) pick_data.ci_id = init_bp3d_params.ci_id;

			Ext.Ajax.request({
				url     : 'get-contents.cgi',
				method  : 'POST',
				params  : Ext.urlEncode(pick_data),
				success : function(conn,response,options){
					try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
					if(results && results.images && results.images.length>0){
						for(var i=0;i<results.images.length;i++){
							var startIndex = 0;
							while(1){
								var rtnIndex = ag_comment_store.find('oid',new RegExp("^"+results.images[i].f_id+"\$"),startIndex,true,true);
								if(rtnIndex>=startIndex){
									var rec = ag_comment_store.getAt(rtnIndex);
									if(rec){
										rec.beginEdit();
										rec.set("organ", results.images[i].name_e);
										rec.set("name_j",results.images[i].name_j);
										rec.set("name_k",results.images[i].name_k);
										rec.set("name_l",results.images[i].name_l);
										rec.commit();
										rec.endEdit();
									}
									startIndex = rtnIndex +1;
								}else{
									break;
								}
							}
						}
					}
					updateAnatomo();
				},
				failure : function(conn,response,options){
					updateAnatomo();
				}
			});
		},
		'remove' : function(store,record,index){
		},
		'update' : function(store,record,operation){
		},
		'clear' : function(store){
		}
	}
});

fma_search_store = new Ext.data.JsonStore({
	url: 'get-fma.cgi',
	pruneModifiedRecords : true,
	totalProperty : 'total',
	root: 'records',
//	remoteSort: true,
//	sortInfo: {field: 'volume', direction: 'DESC'},
	fields: [
		'f_id',
		'b_id',
		'name_j',
		'name_e',
		'name_k',
		'name_l',
		'syn_j',
		'syn_e',
		'def_e',
		'organsys_j',
		'organsys_e',
		'text',
		'name',
		'organsys',
		'phase',
		{name:'xmin',   type:'float'},
		{name:'xmax',   type:'float'},
		{name:'ymin',   type:'float'},
		{name:'ymax',   type:'float'},
		{name:'zmin',   type:'float'},
		{name:'zmax',   type:'float'},
		{name:'volume', type:'float'},
		'taid',
		'physical',
		'phy_id',
		'version',
		'tg_id',
		'tgi_id',
		{name:'md_id',type:'int'},
		{name:'mv_id',type:'int'},
		{name:'mr_id',type:'int'},
		{name:'ci_id',type:'int'},
		{name:'cb_id',type:'int'},
		{name:'bul_id',type:'int'},

		{name:'tweet_num',type:'int',defaultValue:0},
		{name:'tweets',type:'auto'},

		'model',
		'model_version',
		'concept_info',
		'concept_build',
		'buildup_logic',
		{name:'icon',type:'string'},
		{name:'bu_revision',type:'int'},
		'state',
		'def_color',
		{name:'entry', type:'date', dateFormat:'timestamp'},
		{name:'lastmod', type:'date', dateFormat:'timestamp'}
	],
	listeners: {
		'beforeload' : {
			fn:function(self,options){
				try{
					self.baseParams = self.baseParams || {};
					delete gParams.parent;
					if(!Ext.isEmpty(gParams.parent)) self.baseParams.parent = gParams.parent;
					self.baseParams.lng = gParams.lng;
					try{var bp3d_version = Ext.getCmp('bp3d-version-combo').getValue();}catch(e){_dump("fma_search_store.beforeload():e=["+e+"]");bp3d_version='$MODEL_VERSION[0][0]';}
					if(!Ext.isEmpty(bp3d_version)) self.baseParams.version = bp3d_version;
				}catch(e){
					_dump("fma_search_store.beforeload():"+e);
				}
				for(var key in init_bp3d_params){
					if(key.match(/_id\$/)) self.baseParams[key] = init_bp3d_params[key];
				}
			},
			scope:this
		},
		'load': {
			fn:function(self,records,options){
			},
			scope:this,
			single:true
		},
		'datachanged':{
			fn:function(self){
			},scope:this
		},
		'loadexception': {
			fn:function(){
			},scope:this
		}
	}
});

var addPartslistGrid_timer = null;
function addPartslistGrid(store,records,index){
	var zoom = false;
//_dump("addPartslistGrid():gDispAnatomographyPanel=["+gDispAnatomographyPanel+"]");
	if(!gDispAnatomographyPanel){
		zoom = true;
		for(var i=store.getCount()-1;i>=0;i--){
			try{
				var record = store.getAt(i);
				if(record) record.set('zoom',true);
			}catch(e){}
		}
	}

	ag_parts_store = store;
	if(zoom){
		if(addPartslistGrid_timer) clearTimeout(addPartslistGrid_timer);
		addPartslistGrid_timer = setTimeout(function(){
			addPartslistGrid_timer = null;
			ag_focus(true);
		},500);
	}else{
		if(!updateClipImage()) updateAnatomo();
	}
	update_anatomography_point_grid(records);
	try{update_ag_fma_search_grid(records);}catch(e){}

	setTimeout(function(){
		try{
			var sel = ag_parts_gridpanel.getSelectionModel();
			try{sel.clearSelections();}catch(e){}
			var g_store = ag_parts_gridpanel.getStore();
			var g_count = g_store.getCount();
			for(var i=0;i<g_count;i++){
				var record = g_store.getAt(i);
				if(record.get('zoom') && !sel.isSelected(i)) sel.selectRow(i,true);
			}
		}catch(e){}
	},0);
	setEmptyGridText();
}

function removePartslistGrid(store,record,index){
	if(store.getCount()==0){
		var cmp = Ext.getCmp('contents-tab-panel');
		if(cmp && cmp.getActiveTab().id == 'contents-tab-bodyparts-panel'){
			gDispAnatomographyPanel = false;
		}
		Ext.getCmp('bp3d-home-group-btn').disable();
		try{
			var bp3d_grid = Ext.getCmp('control-tab-partslist-panel');
			if(bp3d_grid){
				var cmodel = bp3d_grid.getColumnModel();
				var index = cmodel.getIndexById('conv_id');
				cmodel.setHidden(index,true);
			}else{
				bp3d_grid = undefined;
			}
		}catch(e){}
		try{
			var ag_grid = Ext.getCmp('ag-parts-gridpanel');
			if(ag_grid){
				var cmodel = ag_grid.getColumnModel();
				var index = cmodel.getIndexById('conv_id');
				cmodel.setHidden(index,true);
			}else{
				ag_grid = undefined;
			}
		}catch(e){}
	}

	ag_parts_store = store;
	if(!updateClipImage()) updateAnatomo();
	update_anatomography_point_grid(record);
	try{update_ag_fma_search_grid(record);}catch(e){}

	setTimeout(function(){
		try{
			var sel = ag_parts_gridpanel.getSelectionModel();
			try{sel.clearSelections();}catch(e){}
			var g_store = ag_parts_gridpanel.getStore();
			var g_count = g_store.getCount();
			for(var i=0;i<g_count;i++){
				var record = g_store.getAt(i);
				if(record.get('zoom') && !sel.isSelected(i)) sel.selectRow(i,true);
			}
		}catch(e){
			_dump("removePartslistGrid():"+e);
		}
	},0);
	setEmptyGridText();
}

function updatePartslistGrid(store,record,operation){
	ag_parts_store = store;
	if(!updateClipImage()) updateAnatomo();
	update_anatomography_point_grid(record);
	try{update_ag_fma_search_grid(record);}catch(e){}
}

var resizeGridPanelColumns = function(grid){
	try{
		var column = grid.getColumnModel();
		var innerWidth = grid.getInnerWidth();
		var totalWidth = column.getTotalWidth(false);
		var columnCount = column.getColumnCount();
		var columnNum = 0;
		for(var i=0;i<columnCount;i++){
			if(column.isHidden(i)){
				continue;
			}
			if(column.isHidden(i) || column.isFixed(i) || !column.isResizable(i) || column.config[i].resizable){
				innerWidth -= column.getColumnWidth(i);
				continue;
			}
			if(column.isResizable(i)) columnNum++;
		}
		if(columnNum==0) return;
		var columnWidth = parseInt((innerWidth-21)/columnNum);
		for(var i=0;i<columnCount;i++){
			if(column.isHidden(i) || column.isFixed(i) || !column.isResizable(i) || column.config[i].resizable) continue;
			if(column.isResizable(i)) column.setColumnWidth(i,columnWidth);
		}
	}catch(e){
		for(var ekey in e){
			_dump('resizeGridPanelColumns():'+ekey+'=['+e[ekey]+']');
		}
	}
};

var saveHiddenGridPanelColumns = function(grid,id){
	if(Ext.isEmpty(id)) id = grid.getId();
	var columnModel = grid.getColumnModel();
	var count = columnModel.getColumnCount();
	var hash = {};
	for(var i=0;i<count;i++){
		if(columnModel.isFixed(i)) continue;
		hash[columnModel.getColumnId(i)] = columnModel.isHidden(i);
	}
	glb_us_state[id+'-columns-hidden'] = hash;

	ag_put_usersession_task.delay(1000);

//	var json = Ext.util.JSON.encode(hash);
//	Cookies.set(id+'-columns-hidden',json);
Cookies.clear(id+'-columns-hidden');
//_dump("saveHiddenGridPanelColumns():"+json);
};

var isPointDataRecord = function(record){
	if(record.data.elem_type=='bp3d_point') return true;
	return false;
};
var isNoneDataRecord = function(record){
	if(!Ext.isEmpty(record.data.zmax)) return false;
	if(!Ext.isEmpty(record.data.elem_type) && isPointDataRecord(record)) return false;
	return true;
};

var restoreHiddenGridPanelColumns = function(grid,id){
	if(Ext.isEmpty(id)) id = grid.getId();
	if(Ext.isEmpty(glb_us_state[id+'-columns-hidden'])) return;
	var hash = glb_us_state[id+'-columns-hidden'];

//	var json = Cookies.get(id+'-columns-hidden');
//_dump("restoreHiddenGridPanelColumns():"+json);
//	if(!json) return;
	var columnModel = grid.getColumnModel();
//	var hash = Ext.util.JSON.decode(json);
	for(var key in hash){
		var index = columnModel.getIndexById(key);
		if(index<0) continue;
		if(columnModel.isFixed(index)) continue;
		columnModel.setHidden(index,hash[key]);
	}
};

setEmptyGridText = function(){
	return;
};

var point_search = function(imgX,imgY,voxelRadius){
	if(Ext.isEmpty(voxelRadius) || (voxelRadius-0)<5) voxelRadius = 5;
	try{
		ag_comment_tabpanel.getActiveTab().loadMask.show();

		\$(Ext.getCmp('ag-point-search-editorgrid-panel').getBottomToolbar().items.last().el).text('- / -')

		Ext.getCmp('ag-point-search-header-content-more-button').setDisabled(true);

		glb_point_f_id = null;
		var params = makeAnatomoPrm();
		_loadAnatomo(params,true);

		var store = Ext.getCmp('ag-point-search-editorgrid-panel').getStore();
		store.removeAll();
		delete store.baseParams.f_id;

		Ext.getCmp('ag-point-search-header-content-screen-x-text').setValue(imgX);
		Ext.getCmp('ag-point-search-header-content-screen-y-text').setValue(imgY);
		var cr = Ext.getCmp('ag-point-search-header-content-voxel-range-text');
		if(cr){
			cr.setValue(voxelRadius);
			cr.fireEvent('change',cr,voxelRadius);
		}

		var cx = Ext.getCmp('ag-point-search-header-content-coordinate-x-text');
		if(cx){
			cx.setValue('');
			cx.fireEvent('change',cx,'');
		}
		var cy = Ext.getCmp('ag-point-search-header-content-coordinate-y-text');
		if(cy){
			cy.setValue('');
			cy.fireEvent('change',cy,'');
		}
		var cz = Ext.getCmp('ag-point-search-header-content-coordinate-z-text');
		if(cz){
			cz.setValue('');
			cz.fireEvent('change',cz,'');
		}

		var urlStr = cgipath.pointSearch;
		var params = Ext.urlDecode(makeAnatomoPrm(null,1),true);
		params.px = imgX;
		params.py = imgY;
		params.vr = voxelRadius;
		Ext.Ajax.request({
			url    : urlStr,
			method : 'POST',
			params : params,
			success: function (response, options) {
				try{var pointData = Ext.util.JSON.decode(response.responseText);}catch(e){_dump(e);}
				if(Ext.isEmpty(pointData) || Ext.isEmpty(pointData.id)){
					ag_comment_tabpanel.getActiveTab().loadMask.hide();
					return;
				}

				Ext.getCmp('ag-point-search-header-content-more-button').setDisabled(false);

				var tx = parseInt(parseFloat(pointData.worldPosX)*1000)/1000;
				var ty = parseInt(parseFloat(pointData.worldPosY)*1000)/1000;
				var tz = parseInt(parseFloat(pointData.worldPosZ)*1000)/1000;

				var cx = Ext.getCmp('ag-point-search-header-content-coordinate-x-text');
				if(cx){
					cx.setValue(tx);
					cx.fireEvent('change',cx,tx);
				}
				var cy = Ext.getCmp('ag-point-search-header-content-coordinate-y-text');
				if(cy){
					cy.setValue(ty);
					cy.fireEvent('change',cy,ty);
				}
				var cz = Ext.getCmp('ag-point-search-header-content-coordinate-z-text');
				if(cz){
					cz.setValue(tz);
					cz.fireEvent('change',cz,tz);
				}

				var store = Ext.getCmp('ag-point-search-editorgrid-panel').getStore();
				store.baseParams.f_id = pointData.id;
				var newRecord = Ext.data.Record.create(ag_point_search_fields);
				var recs = [];
				Ext.each(pointData.ids,function(o,i,a){
					recs.push(new newRecord(o));
				});
				store.add(recs)

				\$(Ext.getCmp('ag-point-search-editorgrid-panel').getBottomToolbar().items.last().el).text(pointData.ids.length + ' / ' + pointData.total)

				Ext.getCmp('ag-point-search-header-content-more-button').setDisabled(pointData.ids.length<pointData.total?true:false);

				glb_point_f_id = pointData.id;
				var params = makeAnatomoPrm();
				_loadAnatomo(params,true);
				ag_comment_tabpanel.getActiveTab().loadMask.hide();
			},
			failure: function (response, options) {
				try{alert(cgipath.pointSearch+":failure():"+response.status+":"+response.statusText);}catch(e){}
				ag_comment_tabpanel.getActiveTab().loadMask.hide();
			}
		});
	}catch(e){
		try{
			ag_comment_tabpanel.getActiveTab().loadMask.hide();
		}catch(e){}
	}
};



function add_bp3d_parts_store_parts_from_TPAP(tp_ap,aCB){
	var tpap_param = analyzeTPAP(tp_ap);
	if(Ext.isEmpty(tpap_param)) return;
	var newRecord = Ext.data.Record.create(bp3d_parts_store_fields);
	var addrecs = [];

	if(tpap_param.parts && tpap_param.parts.length>0 && bp3d_parts_store_fields){
		var prm_record = ag_param_store.getAt(0);
//		console.log(tpap_param.parts);
		for(var j=0,len=tpap_param.parts.length;j<len;j++){
			var parts = tpap_param.parts[j];

			var idx=-1;
			if(!Ext.isEmpty(parts.f_id)){
				idx = bp3d_parts_store.find('f_id',new RegExp('^'+parts.f_id+'\$'));
			}else if(!Ext.isEmpty(parts.b_id)){
				idx = bp3d_parts_store.find('b_id',new RegExp('^'+parts.b_id+'\$'));
			}
			if(idx>=0) continue;

			var addrec = new newRecord({});
			addrec.beginEdit();
			for(var fcnt=0;fcnt<addrec.fields.items.length;fcnt++){
				var fname = addrec.fields.items[fcnt].name;
				var fdefaultValue = addrec.fields.items[fcnt].defaultValue;
				addrec.set(fname,fdefaultValue);
			}

			if(!Ext.isEmpty(parts.f_id)) addrec.set("f_id",parts.f_id);
			if(!Ext.isEmpty(parts.f_nm)) addrec.set("name_e",parts.f_nm);
			if(!Ext.isEmpty(parts.color)) addrec.set("color",'#'+parts.color);
			if(!Ext.isEmpty(parts.value)) addrec.set("value",parts.value);
			if(!Ext.isEmpty(parts.exclude)) addrec.set("exclude",parts.exclude);
			if(!Ext.isEmpty(parts.zoom)) addrec.set("zoom",parts.zoom);
			if(!Ext.isEmpty(parts.opacity)) addrec.set("opacity",parts.opacity);
			if(!Ext.isEmpty(parts.representation)) addrec.set("representation",parts.representation);
			if(!Ext.isEmpty(parts.point)) addrec.set("point",parts.point);
			if(!Ext.isEmpty(parts.b_id)){
				addrec.set("b_id",parts.b_id);
				if(!Ext.isEmpty(parts.conv_id)){
					addrec.set("conv_id",parts.conv_id);
				}else{
					addrec.set("conv_id",parts.b_id);
				}
			}

			addrec.commit(true);
			addrec.endEdit();
			addrecs.push(addrec);
		}
	}
	if(addrecs.length>0) bp3d_parts_store.add(addrecs);
	return addrecs;
}

function add_comment_store_pins_from_TPAP(tp_ap){
	var tpap_param = analyzeTPAP(tp_ap);
	if(Ext.isEmpty(tpap_param)) return;

	var newRecord = Ext.data.Record.create(ag_comment_store_fields);
	var addrecs = [];
	var pin_no = ag_comment_store.getCount();

	if(tpap_param.comments && tpap_param.comments.length>0){
		for (var i = 0, len = tpap_param.comments.length; i < len; i++) {
			var comment = tpap_param.comments[i];
			var addrec = new newRecord({});
			addrec.beginEdit();
			for(var fcnt=0;fcnt<addrec.fields.items.length;fcnt++){
				var fname = addrec.fields.items[fcnt].name;
				var fdefaultValue = addrec.fields.items[fcnt].defaultValue;
				addrec.set(fname,fdefaultValue);
			}
			addrec.set("no",   ++pin_no);
			addrec.set("x3d",    parseFloatTPAP(comment.c3d.x));
			addrec.set("y3d",    parseFloatTPAP(comment.c3d.y));
			addrec.set("z3d",    parseFloatTPAP(comment.c3d.z));
			addrec.set("avx3d",  "");
			addrec.set("avy3d",  "");
			addrec.set("avz3d",  "");
			addrec.set("uvx3d",  "");
			addrec.set("uvy3d",  "");
			addrec.set("uvz3d",  "");
			addrec.set("color",  comment.point.rgb);
			addrec.set("oid",    comment.id);
			addrec.set("organ",  comment.name);
			addrec.set("comment",(comment.comment?comment.comment:""));
			addrec.set("coord",  "");
			addrec.commit(true);
			addrec.endEdit();
			addrecs.push(addrec);
		}
	}else if(tpap_param.pins && tpap_param.pins.length>0 && ag_comment_store_fields){
		for(var j=0,len=tpap_param.pins.length;j<len;j++){
			var pin = tpap_param.pins[j];
			var addrec = new newRecord({});
			addrec.beginEdit();
			for(var fcnt=0;fcnt<addrec.fields.items.length;fcnt++){
				var fname = addrec.fields.items[fcnt].name;
				var fdefaultValue = addrec.fields.items[fcnt].defaultValue;
				addrec.set(fname,fdefaultValue);
			}
			addrec.set("no",++pin_no);
			addrec.set("x3d",pin.x3d);
			addrec.set("y3d",pin.y3d);
			addrec.set("z3d",pin.z3d);
			addrec.set("avx3d",pin.avx3d);
			addrec.set("avy3d",pin.avy3d);
			addrec.set("avz3d",pin.avz3d);
			addrec.set("uvx3d",pin.uvx3d);
			addrec.set("uvy3d",pin.uvy3d);
			addrec.set("uvz3d",pin.uvz3d);
			addrec.set("color",pin.color);
			addrec.set("oid",pin.organid);
			addrec.set("organ",pin.organname);
			addrec.set("comment",(pin.comment?pin.comment:""));
			addrec.set("coord",  pin.coord);
			addrec.commit(true);
			addrec.endEdit();
			addrecs.push(addrec);
		}
	}
	if(addrecs.length>0) ag_comment_store.add(addrecs);
}


function export_parts_pins(aOpts){

	aOpts = Ext.apply({},aOpts||{},{
		title    : 'Export',
		width    : 500,
		height   : 500,
		plain    : true,
		modal    : true,
		resizable: true,
		animateTarget: null
	});

	var cur_text = URI2Text(glb_anatomo_editor_url,{target:{pins:false}});
	var cur_url = Text2URI(cur_text,{target:{pins:false}});

	var convOpts = {
		target: {
			common: false,
			camera: false,
			clip: false,
			parts: true,
			point_parts: false,
			legendinfo: false,
			pins: true
		},
		pin: {
			url_prefix : cur_url+encodeURIComponent('&')
		}
	};


	function get_text(){
		var value = URI2Text(glb_anatomo_editor_url,convOpts);
		return value;
	}
	var text_value = get_text();
	if(Ext.isEmpty(text_value)) return;

	var url_short_value = "";
	var url_long_value = Text2URI(text_value,convOpts);
	if(Ext.isEmpty(url_long_value)) return;

	function change_checked(field,checked){
		convOpts.target[field.name] = checked;
		text_value = get_text();
		url_short_value = "";
		url_long_value = "";
		if(text_value != ""){
			url_long_value = Text2URI(text_value,convOpts);
			if(url_long_value != ""){
				update_open_url2text(url_long_value,function(url){
					url_short_value = url;
					Ext.getCmp('ag_export_short_url_textfield').setValue(url_short_value);
				});
			}
		}
		Ext.getCmp('ag_export_table_textarea').setValue(text_value);
		Ext.getCmp('ag_export_long_url_textfield').setValue(url_long_value);
		Ext.getCmp('ag_export_short_url_textfield').setValue(url_short_value);
	}

	var win = new Ext.Window({
		title       : aOpts.title,
		animateTarget: aOpts.animateTarget,
		width       : aOpts.width,
		height      : aOpts.height,
		plain       : aOpts.plain,
		bodyStyle   : 'padding:5px;',
		buttonAlign : 'right',
		modal       : aOpts.modal,
		resizable   : aOpts.resizable,
		items       : [{
			xtype:'fieldset',
			title: 'Export',
			autoHeight: true,
			layout: 'table',
			layoutConfig: {
				columns: 2
			},
			items:[{
				xtype: 'checkbox',
				boxLabel: 'Parts',
				name: 'parts',
				checked: convOpts.target.parts,
				width: 100,
				listeners: {
					check: change_checked
				}
			},{
				xtype: 'checkbox',
				boxLabel: 'Pins',
				name: 'pins',
				checked: convOpts.target.pins,
				width: 100,
				listeners: {
					check: change_checked
				}
			}]
		},{
			xtype:'fieldset',
			title: 'Message URL',
			autoHeight: true,
			labelAlign: 'right',
			labelWidth: 40,
			items:[{
				xtype         : 'textfield',
				id            : 'ag_export_short_url_textfield',
				fieldLabel    : 'Short',
				anchor        : '100%',
				readOnly      : true,
				selectOnFocus : true,
				value         : url_short_value,
				listeners: {
					render: function(comp){
						update_open_url2text(url_long_value,function(url){
							comp.setValue(url);
						});
					}
				}
			},{
				xtype         : 'textfield',
				id            : 'ag_export_long_url_textfield',
				fieldLabel    : 'Long',
				anchor        : '100%',
				readOnly      : true,
				selectOnFocus : true,
				value         : url_long_value
			}]
		},{
			xtype:'fieldset',
			title: 'Table',
			autoHeight: true,
			layout: 'fit',
			items: [{
				xtype: 'textarea',
				id: 'ag_export_table_textarea',
				style: 'font-family:Courier;monospace;',
				readOnly: true,
				selectOnFocus: true,
				value: text_value,
				anchor: '100%',
				height: 220
			}]
		}],
		buttons : [{
			text: 'Close',
			handler: function(){
				win.close();
			}
		}]
	});
	win.show();
}
HTML
=cut
