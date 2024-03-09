#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use File::Basename;
use File::Spec::Functions qw(abs2rel catdir catfile splitdir);
use File::Path;

use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'..','cgi_lib');
use BITS::Config;

require "webgl_common.pl";
use cgi_lib::common;
use AG::login;

my %PARAMS = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%PARAMS,\%COOKIE);
$PARAMS{$_} = &cgi_lib::common::decodeUTF8($PARAMS{$_}) for(sort keys(%PARAMS));
$COOKIE{$_} = &cgi_lib::common::decodeUTF8($COOKIE{$_}) for(sort keys(%COOKIE));

my $dbh = &get_dbh();

use constant {
	DEBUG => BITS::Config::DEBUG,
	USE_HTML5 => BITS::Config::USE_HTML5,
	USE_APPCACHE => BITS::Config::USE_APPCACHE
};

#my $EXT_PATH = qq|extjs-4.1.1|;
my $EXT_PATH = qq|ext-4.2.1.883|;
#my $THREEJS = qq|three-r52-0|;
#my $THREEJS = qq|three-r67-0|;
#my $THREEJS = qq|three-r71-0|;
#my $THREEJS = qq|three-r72-0|;
my $THREEJS = qq|three-r73-2|;

my @CSS = (
#	DEBUG ? "static/js/$EXT_PATH/resources/css/ext-all-debug.css" : "static/js/$EXT_PATH/resources/css/ext-all.css",
#	DEBUG ? "static/js/$EXT_PATH/resources/css/ext-all-neptune-debug.css" : "static/js/$EXT_PATH/resources/css/ext-all-neptune.css",
	DEBUG ? "static/js/$EXT_PATH/resources/css/ext-all-gray-debug.css" : "static/js/$EXT_PATH/resources/css/ext-all-gray.css",
#	DEBUG ? "static/js/$EXT_PATH/resources/css/ext-all-access-debug.css" : "static/js/$EXT_PATH/resources/css/ext-all-access.css",
	"static/js/$EXT_PATH/ux/css/CheckColumn.css",
	"static/js/$EXT_PATH/ag/css/ColorPickerPallet.css",
	"static/js/$EXT_PATH/ag/css/AgParts.css",
	"static/js/$EXT_PATH/ux/grid/css/GridFilters.css",
	"static/js/$EXT_PATH/ux/grid/css/RangeMenu.css",

	"static/css/base.css",
	"static/css/anatomography.css",
	"static/css/AgRender.css",
);
my @JS = (
	DEBUG ? "static/js/jquery.js" : "static/js/jquery.min.js",
	DEBUG ? "get-AgDefaults.cgi" : "static/js/ag/AgDefaults.js",

	DEBUG ? "static/js/$EXT_PATH/ext-all-dev.js" : "static/js/$EXT_PATH/ext-all.js",
#	"static/js/$EXT_PATH/ext-all.js",
	"static/js/$EXT_PATH/src/menu/Item.js",
	"static/js/$EXT_PATH/locale/ext-lang-ja.js",
#	"static/js/$EXT_PATH/ux/CheckColumn.js",
	"static/js/$EXT_PATH/ux/form/SearchField.js",
	"static/js/$EXT_PATH/ux/picker/TreePicker.js",
	"static/js/$EXT_PATH/ux/IFrame.js",

	"static/js/$EXT_PATH/ag/ColorPickerPallet.js",
	"static/js/$EXT_PATH/ag/ColorPickerPalletField.js",
	"static/js/$EXT_PATH/ag/AgParts.js",
	"static/js/$EXT_PATH/ag/AgModel.js",

	"static/js/ag/AgMiniRenderer.js",
	DEBUG ? "static/js/$THREEJS/build/three.js" : "static/js/$THREEJS/build/three.min.js",
#	"static/js/$THREEJS/build/three.js",
#	"static/js/$THREEJS/examples/js/loaders/OBJLoader.js",
#	"static/js/$THREEJS/examples/js/Detector.js",

	DEBUG ? "load-images.cgi" : "static/js/ag/load-images.js",
#	"load-images.cgi",

	"static/js/ag/AgLocalStorage.js",
	"static/js/ag/AgUtils.js",
	"static/js/ag/AgURLParser.js",
	"static/js/ag/AgRender.js",
	"static/js/ag/AgWiki.js",
	"static/js/ag/AgPalletUtils.js",
	"static/js/ag/AgFileUpload.js",
	"static/js/ag/AgClass.js",
	"static/js/ag/AgMain.js",
	"static/js/ag/AgStore.js",
	"static/js/ag/AgDatasetMng.js",
	"static/js/ag/AgObjEditWindow.js",
	"static/js/ag/AgObjInfoEditWindow.js",
	"static/js/ag/AgConceptMng.js",
	"static/js/ag/AgConceptSegment.js",
	"static/js/ag/AgThumbnailBackgroundPart.js",
	"static/js/ag/AgFileDrop.js",
	"static/js/ag/AgMappingMng.js",
	"static/js/ag/AgFMABrowser.js",
	"static/js/ag/AgFreezeMappingMng.js",
	"static/js/ag/AgCXCreate.js",
	"static/js/ag/AgCXSearch.js",
	"static/js/ag/AgObjSearch.js",
);

my @cookies;
unless(exists($COOKIE{'ag_annotation.session'})){
	$COOKIE{'ag_annotation.session'} = &AG::login::makeSessionID();
	push(@cookies,&setCookie('ag_annotation.session',$COOKIE{'ag_annotation.session'}).' HttpOnly');
}
if(exists($COOKIE{'ag_annotation.session'})){
	my $session_info = {};
#	$session_info->{'ENV'}->{$_} = &cgi_lib::common::decodeUTF8($ENV{$_}) for(sort keys(%ENV));
	$session_info->{'PARAMS'}->{$_} = &cgi_lib::common::decodeUTF8($PARAMS{$_}) for(sort keys(%PARAMS));
	$session_info->{'COOKIE'}->{$_} = &cgi_lib::common::decodeUTF8($COOKIE{$_}) for(sort keys(%COOKIE));
	&AG::login::setSession($session_info,&AG::login::getSessionState($COOKIE{'ag_annotation.session'}),&AG::login::getSessionKeymap($COOKIE{'ag_annotation.session'}));
	&AG::login::setSessionHistory($session_info);
}

my $content = '';
#print qq|Content-type: text/html; charset=UTF-8\n\n|;
if(USE_HTML5){
	$content .= <<HTML;
<!DOCTYPE html>
HTML
	$content .= qq|<html lang="ja"|;
}else{
	$content .= <<HTML;
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
HTML
	$content .= qq|<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja"|;
}
if(USE_APPCACHE){
	$content .= qq| manifest="webgl.appcache"|;
}
$content .= qq|>\n|;
$content .= <<HTML;
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta http-equiv="Content-Style-Type" content="text/css" />
<meta http-equiv="Content-Script-Type" content="text/javascript" />
<!--<meta http-equiv="X-UA-Compatible" content="chrome=1">-->
<meta name="viewport" content="width=device-width, user-scalable=no, minimum-scale=1.0, maximum-scale=1.0">
HTML

#my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,qw|.cgi|);

unless(DEBUG){
	foreach my $cgi_target (qw/get-AgDefaults.cgi load-images.cgi/){
		my $cgi_path = &catfile($cgi_dir,$cgi_target);

		my $js_basename = $cgi_target;
		$js_basename =~ s/.cgi$//g;
		$js_basename =~ s/^get\-//g;

		my $js_path = &catfile($cgi_dir,'js','ag',qq|$js_basename.js|);

	#	next unless(-e $cgi_path && (!-e $js_path || -z $js_path || (stat($js_path))[9]<(stat($cgi_path))[9]));

	#	print LOG __LINE__.":\$cmd=[".qq|unset REQUEST_METHOD;echo "// $cgi_pathより自動生成"> $js_path;$cgi_path >> $js_path|."]\n";
		system(qq|unset REQUEST_METHOD;echo "// $cgi_pathより自動生成"> $js_path;$cgi_path >> $js_path|);
		chmod 0600,$js_path if(-e $js_path);
	}
}

#my $java = qq|/usr/java/default/bin/java|;
#my $yui = qq|/ext1/project/WebGL/local/usr/src/yuicompressor-2.4.6/yuicompressor-2.4.6.jar|;
my $java = qq|/usr/bin/java|;
my $yui = qq|/bp3d/local/yuicompressor-2.4.6/yuicompressor-2.4.6.jar|;
my $mini_ext = qq|.min|;

my @extlist = qw|.min.css .css|;

foreach my $css (@CSS){
	next unless(-e $css);

	unless(DEBUG){
		my($css_name,$css_dir,$css_ext) = &File::Basename::fileparse($css,@extlist);
		if(defined $css_ext && length($css_ext)>0 && $css_ext eq '.css'){
			my $mini_css = &catfile($css_dir,$css_name.$mini_ext.$css_ext);
			if(-w $css_dir){
				unlink $mini_css if(-e $mini_css && ((stat($css))[9]>(stat($mini_css))[9] || (stat($0))[9]>(stat($mini_css))[9]));
				unless(-e $mini_css){
					system(qq|$java -jar $yui --type css --nomunge -o $mini_css $css|) if(-e $java && -e $yui);
					chmod 0666,$mini_css if(-e $mini_css);
				}
			}
			$css = $mini_css if(-e $mini_css);
		}
	}
	$css .= '?'.(stat($css))[9] unless(USE_APPCACHE);
	$content .= qq|<link rel="stylesheet" href="$css" type="text/css" media="all" charset="UTF-8">\n|;
}

$content .= <<HTML;
<!-- Javascript -->
HTML

@extlist = qw|.min.js .js|;

foreach my $js (@JS){
	next unless(-e $js);

	unless(DEBUG){
		my($js_name,$js_dir,$js_ext) = &File::Basename::fileparse($js,@extlist);
		if(defined $js_ext && length($js_ext)>0 && $js_ext eq '.js'){
			my $mini_js = &catfile($js_dir,$js_name.$mini_ext.$js_ext);
			if(-w $js_dir){
				unlink $mini_js if(-e $mini_js && ((stat($js))[9]>(stat($mini_js))[9] || (stat($0))[9]>(stat($mini_js))[9]));
				unless(-e $mini_js){
#					print qq|<!-- $java -jar $yui --type js --nomunge -o $mini_js $js -->\n|;
					system(qq|$java -jar $yui --type js --nomunge -o $mini_js $js|) if(-e $java && -e $yui);
					chmod 0666,$mini_js if(-e $mini_js);
				}
			}
			$js = $mini_js if(-e $mini_js);
		}
	}
	$js .= '?'.(stat($js))[9] unless(USE_APPCACHE);
	$content .= qq|<script type="text/javascript" src="$js" charset="utf-8"></script>\n|;
}
$content .= <<HTML;
<title>MappingManager</title>
<style>
.x-grid-tree-loading .x-tree-icon {
	background-image: url(static/js/$EXT_PATH/resources/themes/images/default/tree/loading.gif) !important;
}
.pallet_checked {
	background-image: url(static/js/$EXT_PATH/ux/css/checked.gif) !important;
}
.pallet_unchecked {
	background-image: url(static/js/$EXT_PATH/ux/css/unchecked.gif) !important;
}


.x-grid3-cell-inner, .x-grid3-hd-inner {
/*	text-overflow : clip;	/* デフォルトは「ellipsis」*/
}
.x-grid-cell-inner, .x-grid-hd-inner {
	text-overflow : clip;	/* デフォルトは「ellipsis」*/
}

.x-form-clear-trigger {
	background-image: url(static/js/$EXT_PATH/resources/themes/images/default/form/clear-trigger.gif);
}

.x-form-search-trigger {
	background-image: url(static/js/$EXT_PATH/resources/themes/images/default/form/search-trigger.gif);
}

.x-livesearch-match {
	font-weight: bold;
	background-color: #ffff99;
}

div#error-twitter-window td.x-grid-cell-rep_id div.x-grid-cell-inner a {
	color: rgb(0, 0, 238);
}

div#find-object-window td.x-grid-cell-art_thumb div.x-grid-cell-inner,
div#error-twitter-window td.x-grid-cell-icon div.x-grid-cell-inner
{
	padding: 2px;
	min-height: 44px;
}

div#find-object-window td.x-grid-cell-cdi_name div.x-grid-cell-inner,
div#find-object-window td.x-grid-cell-cdi_name_e div.x-grid-cell-inner,
div#find-object-window td.x-grid-cell-group div.x-grid-cell-inner,
div#find-object-window td.x-grid-cell-filename div.x-grid-cell-inner
/*
,div#error-twitter-window td.x-grid-cell-cdi_name_e div.x-grid-cell-inner
,div#error-twitter-window td.x-grid-cell-cdi_name_j div.x-grid-cell-inner
,div#error-twitter-window td.x-grid-cell-cdi_name_k div.x-grid-cell-inner
,div#error-twitter-window td.x-grid-cell-cdi_name_l div.x-grid-cell-inner
,div#error-twitter-window td.x-grid-cell-tw_date div.x-grid-cell-inner
,div#error-twitter-window td.x-grid-cell-tw_text div.x-grid-cell-inner
,div#error-twitter-window td.x-grid-cell-rtw_fixed_date div.x-grid-cell-inner
,div#error-twitter-window td.x-grid-cell-rtw_fixed_comment div.x-grid-cell-inner
*/
{
	white-space: normal;
}

div#error-twitter-window div.x-grid-cell-inner {
	max-height:88px;
	height:62px;
}

div.x-grid-cell-inner div.cell-renderer-string {
	white-space:normal;
}
div.x-grid-cell-inner div.cell-renderer-date {
	white-space:normal;
	text-align:center;
	max-width: 106px;
}
div.x-grid-cell-inner div.cell-renderer-boolean,
div.x-grid-cell-inner div.cell-renderer-link
{
	text-align:center;
}

div.x-grid-cell-inner div.cell-separator {
	border-top:1px dotted #e0e0e0;
	margin: 3px 0 2px;
}

body.x-body div.x-grid-cell-inner.art_tmb_path {
	padding: 2px 0px 0px 4px;
}
body.x-body.x-chrome div.x-grid-cell-inner.art_tmb_path {
	padding: 2px 0px 0px 3px;
}
body.x-body.x-gecko div.x-grid-cell-inner.art_tmb_path {
	padding: 0px 0px 3px 3px;
}

</style>
<script>
Ext.BLANK_IMAGE_URL = "static/js/$EXT_PATH/resources/themes/images/default/tree/s.gif";
Ext.Loader.setConfig({enabled: true});
Ext.Loader.setPath({
	'Ext.ux':'js/$EXT_PATH/ux',
	'Ext.ag':'js/$EXT_PATH/ag'
});
Ext.require([
	'*',
//	'Ext.ux.RowExpander',
//	'Ext.ux.grid.FiltersFeature'
]);
//IE11対策
if(!Ext.isIE){
	var ua = navigator.userAgent;
	if( ua.match(/MSIE/) || ua.match(/Trident/) || ua.match(/Edge/) ) {
		Ext.isIE = true;
		Ext.isIE11 = true;
		Ext.docMode = document.documentMode;
		if(Ext.isGecko) Ext.isGecko = false;
		if(Ext.isChrome) Ext.isChrome = false;
		if(Ext.isWebKit) Ext.isWebKit = false;
	}
}
Ext.ag.Data = Ext.ag.Data || {};
HTML
if(1){
	my $concept_info_sql=<<SQL;
select
 ci_id,
 ci_name,
 ci_order
from
 concept_info
where
 ci_use and ci_delcause is null
order by
 ci_order
SQL
	my $concept_info_datas;
	my $ci_id;
	my $ci_name;
	my $ci_order;
	my $concept_info_sth = $dbh->prepare($concept_info_sql) or die $dbh->errstr;
	$concept_info_sth->execute() or die $dbh->errstr;
	my $column_number = 0;
	$concept_info_sth->bind_col(++$column_number, \$ci_id,   undef);
	$concept_info_sth->bind_col(++$column_number, \$ci_name,   undef);
	$concept_info_sth->bind_col(++$column_number, \$ci_order,   undef);
	while($concept_info_sth->fetch){
		push(@$concept_info_datas, {
			ci_id    => $ci_id-0,
			ci_name  => $ci_name,
			ci_order => $ci_order-0,
		});
	}
	$concept_info_sth->finish;
	undef $concept_info_sth;
	undef $concept_info_sql;
	$content .= 'Ext.ag.Data.concept_info='.(defined $concept_info_datas && ref $concept_info_datas eq 'ARRAY' ? &cgi_lib::common::encodeJSON($concept_info_datas) : '[]').";\n";
	undef $concept_info_datas;

	my $concept_build_sql=<<SQL;
select
 cb.ci_id,
 ci_name,
 cb_id,
 cb_name,
 cb_release,
 cb_order
from
 concept_build as cb
left join (
 select ci_id,ci_name from concept_info
) as ci on ci.ci_id=cb.ci_id
where
 cb_use and cb_delcause is null
order by
 cb_order
SQL
	my $concept_build_datas;
	my $cb_id;
	my $cb_name;
	my $cb_release;
	my $cb_order;
	my $concept_build_sth = $dbh->prepare($concept_build_sql) or die $dbh->errstr;
	$concept_build_sth->execute() or die $dbh->errstr;
	$column_number = 0;
	$concept_build_sth->bind_col(++$column_number, \$ci_id,   undef);
	$concept_build_sth->bind_col(++$column_number, \$ci_name,   undef);
	$concept_build_sth->bind_col(++$column_number, \$cb_id,   undef);
	$concept_build_sth->bind_col(++$column_number, \$cb_name,   undef);
	$concept_build_sth->bind_col(++$column_number, \$cb_release,   undef);
	$concept_build_sth->bind_col(++$column_number, \$cb_order,   undef);
	while($concept_build_sth->fetch){
		push(@$concept_build_datas, {
			ci_id      => $ci_id-0,
			cb_id      => $cb_id-0,
			ci_name    => $ci_name,
			cb_name    => $cb_name,
			cb_release => $cb_release, #-0,
			cb_order   => $cb_order-0,
		});
	}
	$concept_build_sth->finish;
	undef $concept_build_sth;
	undef $concept_build_sql;
	$content .= 'Ext.ag.Data.concept_build='.(defined $concept_build_datas && ref $concept_build_datas eq 'ARRAY' ? &cgi_lib::common::encodeJSON($concept_build_datas) : '[]').";\n";
	undef $concept_build_datas;

	my $concept_build_relation_sql=<<SQL;
select
 cbr.ci_id,
 cbr.cb_id,
 cbr.crt_id,
 crt.crt_name
from
 concept_build_relation as cbr

left join (
 select ci_id,cb_id,cb_use from concept_build
) as cb on cb.ci_id=cbr.ci_id and cb.cb_id=cbr.cb_id

left join (
 select * from concept_relation_type
) as crt on crt.crt_id=cbr.crt_id

where
 cb.cb_use AND
 cbr.cbr_use
order by
 cbr.ci_id,
 cbr.cb_id,
 crt.crt_order
SQL
	my $concept_build_relation_datas;
	my $crt_id;
	my $crt_name;
	my $concept_build_relation_sth = $dbh->prepare($concept_build_relation_sql) or die $dbh->errstr;
	$concept_build_relation_sth->execute() or die $dbh->errstr;
	$column_number = 0;
	$concept_build_relation_sth->bind_col(++$column_number, \$ci_id,   undef);
	$concept_build_relation_sth->bind_col(++$column_number, \$cb_id,   undef);
	$concept_build_relation_sth->bind_col(++$column_number, \$crt_id,   undef);
	$concept_build_relation_sth->bind_col(++$column_number, \$crt_name,   undef);
	while($concept_build_relation_sth->fetch){
		push(@$concept_build_relation_datas, {
			ci_id    => $ci_id-0,
			cb_id    => $cb_id-0,
			crt_id   => $crt_id-0,
			crt_name => $crt_name
		});
	}
	$concept_build_relation_sth->finish;
	undef $concept_build_relation_sth;
	undef $concept_build_relation_sql;
	$content .= 'Ext.ag.Data.concept_build_relation='.(defined $concept_build_relation_datas && ref $concept_build_relation_datas eq 'ARRAY' ? &cgi_lib::common::encodeJSON($concept_build_relation_datas) : '[]').";\n";
	undef $concept_build_relation_datas;

	my $concept_relation_logic_sql=<<SQL;
select
 crl_id,
 crl_name,
 crl_abbr,
 crl_order
from
 concept_relation_logic
where
 crl_use and crl_delcause is null
order by
 crl_order
SQL
	my $crl_datas;
	my $crl_id;
	my $crl_name;
	my $crl_abbr;
	my $crl_order;
	my $concept_relation_logic_sth = $dbh->prepare($concept_relation_logic_sql) or die $dbh->errstr;
	$concept_relation_logic_sth->execute() or die $dbh->errstr;
	$column_number = 0;
	$concept_relation_logic_sth->bind_col(++$column_number, \$crl_id,   undef);
	$concept_relation_logic_sth->bind_col(++$column_number, \$crl_name,   undef);
	$concept_relation_logic_sth->bind_col(++$column_number, \$crl_abbr,   undef);
	$concept_relation_logic_sth->bind_col(++$column_number, \$crl_order,   undef);
	while($concept_relation_logic_sth->fetch){
		push(@$crl_datas, {
			crl_id    => $crl_id-0,
			crl_name  => $crl_name,
			crl_abbr  => $crl_abbr,
			crl_order => $crl_order-0
		});
	}
	$concept_relation_logic_sth->finish;
	undef $concept_relation_logic_sth;
	undef $concept_relation_logic_sql;
	$content .= 'Ext.ag.Data.concept_relation_logic='.&cgi_lib::common::encodeJSON($crl_datas).";\n";
	undef $crl_datas;

	my $concept_art_map_part_sql=<<SQL;
select
 cmp.cmp_id,
 COALESCE(cmp.cmp_display_title,cmp.cmp_title),
 cmp.cmp_abbr,
 cmp.cmp_prefix,
 cmp.crl_id,
 crl.crl_name,
 crl.crl_abbr,
 cmp.cmp_order
from
 concept_art_map_part as cmp

left join (
 select
  crl_id,
  crl_name,
  crl_abbr
 from
  concept_relation_logic
) as crl on crl.crl_id=cmp.crl_id

where
 cmp.cmp_use and
 cmp.cmp_delcause is null
order by
 cmp.cmp_order,
 cmp.cmp_id
SQL
	my $cmp_datas;
	my $cmp_id;
	my $cmp_title;
	my $cmp_abbr;
	my $cmp_prefix;
	my $cmp_order;
	my $concept_art_map_part_sth = $dbh->prepare($concept_art_map_part_sql) or die $dbh->errstr;
	$concept_art_map_part_sth->execute() or die $dbh->errstr;
	$column_number = 0;
	$concept_art_map_part_sth->bind_col(++$column_number, \$cmp_id,   undef);
	$concept_art_map_part_sth->bind_col(++$column_number, \$cmp_title,   undef);
	$concept_art_map_part_sth->bind_col(++$column_number, \$cmp_abbr,   undef);
	$concept_art_map_part_sth->bind_col(++$column_number, \$cmp_prefix,   undef);
	$concept_art_map_part_sth->bind_col(++$column_number, \$crl_id,   undef);
	$concept_art_map_part_sth->bind_col(++$column_number, \$crl_name,   undef);
	$concept_art_map_part_sth->bind_col(++$column_number, \$crl_abbr,   undef);
	$concept_art_map_part_sth->bind_col(++$column_number, \$cmp_order,   undef);
	while($concept_art_map_part_sth->fetch){
		push(@$cmp_datas, {
			cmp_id     => $cmp_id-0,
			cmp_title  => $cmp_title,
			cmp_abbr   => $cmp_abbr,
			cmp_prefix => $cmp_prefix,
			crl_id     => defined $crl_id ? $crl_id-0 : undef,
			crl_name   => $crl_name,
			crl_abbr   => $crl_abbr,
			cmp_order  => $cmp_order-0,
		});
	}
	$concept_art_map_part_sth->finish;
	undef $concept_art_map_part_sth;
	undef $concept_art_map_part_sql;
	$content .= 'Ext.ag.Data.concept_art_map_part='.(defined $cmp_datas && ref $cmp_datas eq 'ARRAY' ? &cgi_lib::common::encodeJSON($cmp_datas) : '[]').";\n";
#	$content .= 'Ext.ag.Data.concept_art_map_part_select='.(defined $cmp_datas && ref $cmp_datas eq 'ARRAY' ? &cgi_lib::common::encodeJSON([grep {defined $_ && ref $_ eq 'HASH' && $_->{'cmp_id'}>0} @$cmp_datas]) : '[]').";\n";
	$content .= 'Ext.ag.Data.concept_art_map_part_select='.(defined $cmp_datas && ref $cmp_datas eq 'ARRAY' ? &cgi_lib::common::encodeJSON($cmp_datas) : '[]').";\n";
	undef $cmp_datas;





	my $concept_part_sql=<<SQL;
select
 cp.cp_id,
 COALESCE(cp.cp_display_title,cp.cp_title),
 cp.cp_abbr,
 cp.cp_prefix,
 cp.crl_id,
 crl.crl_name,
 crl.crl_abbr,
 cp.cp_order
from
 concept_part as cp

left join (
 select
  crl_id,
  crl_name,
  crl_abbr
 from
  concept_relation_logic
) as crl on crl.crl_id=cp.crl_id

where
 cp.cp_use and
 cp.cp_delcause is null
order by
 cp.cp_order,
 cp.cp_id
SQL
	my $cp_datas;
	my $cp_id;
	my $cp_title;
	my $cp_abbr;
	my $cp_prefix;
	my $cp_order;
	my $concept_part_sth = $dbh->prepare($concept_part_sql) or die $dbh->errstr;
	$concept_part_sth->execute() or die $dbh->errstr;
	$column_number = 0;
	$concept_part_sth->bind_col(++$column_number, \$cp_id,   undef);
	$concept_part_sth->bind_col(++$column_number, \$cp_title,   undef);
	$concept_part_sth->bind_col(++$column_number, \$cp_abbr,   undef);
	$concept_part_sth->bind_col(++$column_number, \$cp_prefix,   undef);
	$concept_part_sth->bind_col(++$column_number, \$crl_id,   undef);
	$concept_part_sth->bind_col(++$column_number, \$crl_name,   undef);
	$concept_part_sth->bind_col(++$column_number, \$crl_abbr,   undef);
	$concept_part_sth->bind_col(++$column_number, \$cp_order,   undef);
	while($concept_part_sth->fetch){
		push(@$cp_datas, {
			cp_id     => $cp_id-0,
			cp_title  => $cp_title,
			cp_abbr   => $cp_abbr,
			cp_prefix => $cp_prefix,
			crl_id     => defined $crl_id ? $crl_id-0 : undef,
			crl_name   => $crl_name,
			crl_abbr   => $crl_abbr,
			cp_order  => $cp_order-0,
		});
	}
	$concept_part_sth->finish;
	undef $concept_part_sth;
	undef $concept_part_sql;
	$content .= 'Ext.ag.Data.concept_part='.(defined $cp_datas && ref $cp_datas eq 'ARRAY' ? &cgi_lib::common::encodeJSON($cp_datas) : '[]').";\n";
	$content .= 'Ext.ag.Data.concept_part_select='.(defined $cp_datas && ref $cp_datas eq 'ARRAY' ? &cgi_lib::common::encodeJSON($cp_datas) : '[]').";\n";
	undef $cp_datas;






	my $concept_laterality_sql=<<SQL;
select
 cl.cl_id,
 COALESCE(cl.cl_display_title,cl.cl_title),
 cl.cl_abbr,
 cl.cl_prefix,
 cl.cl_order
from
 concept_laterality as cl

where
 cl.cl_use and
 cl.cl_delcause is null
order by
 cl.cl_order,
 cl.cl_id
SQL
	my $cl_datas;
	my $cl_id;
	my $cl_title;
	my $cl_abbr;
	my $cl_prefix;
	my $cl_order;
	my $concept_laterality_sth = $dbh->prepare($concept_laterality_sql) or die $dbh->errstr;
	$concept_laterality_sth->execute() or die $dbh->errstr;
	$column_number = 0;
	$concept_laterality_sth->bind_col(++$column_number, \$cl_id,   undef);
	$concept_laterality_sth->bind_col(++$column_number, \$cl_title,   undef);
	$concept_laterality_sth->bind_col(++$column_number, \$cl_abbr,   undef);
	$concept_laterality_sth->bind_col(++$column_number, \$cl_prefix,   undef);
	$concept_laterality_sth->bind_col(++$column_number, \$cl_order,   undef);
	while($concept_laterality_sth->fetch){
		push(@$cl_datas, {
			cl_id     => $cl_id-0,
			cl_title  => $cl_title,
			cl_abbr   => $cl_abbr,
			cl_prefix => $cl_prefix,
			cl_order  => $cl_order-0,
		});
	}
	$concept_laterality_sth->finish;
	undef $concept_laterality_sth;
	undef $concept_laterality_sql;
	$content .= 'Ext.ag.Data.concept_laterality='.(defined $cl_datas && ref $cl_datas eq 'ARRAY' ? &cgi_lib::common::encodeJSON($cl_datas) : '[]').";\n";
	$content .= 'Ext.ag.Data.concept_laterality_select='.(defined $cl_datas && ref $cl_datas eq 'ARRAY' ? &cgi_lib::common::encodeJSON($cl_datas) : '[]').";\n";
	undef $cl_datas;

}
$content .= <<HTML;
Ext.onReady(function() {
	var config = {};
HTML
$content .= qq|	config.USE_HTML5 = true;\n| if(USE_HTML5);
$content .= qq|	config.DEBUG = true;\n| if(DEBUG);
$content .= <<HTML;
	var app = new AgApp(config);

	Ext.getBody().on({
		dragover: function(e){
			e.preventDefault();
			return false;
		},
		dragenter: function(e){
			e.preventDefault();
			return false;
		},
		drop: function(e){
			e.preventDefault();
			return false;
		}
	});
});
function cancel(event) {
	if(event && event.preventDefault) event.preventDefault();
	return false;
}
</script>
</head>
<body>
<!--
<body ondragover="return false;" dragenter="return false;" ondrop="return false;">
<body ondragover="return cancel(event);" dragenter="return cancel(event);" ondrop="return cancel(event);">
-->
</body>
</html>
HTML

&cgi_lib::common::printContent(&cgi_lib::common::html_compress($content),undef,\@cookies);
#&cgi_lib::common::printContent($content,undef,\@cookies);
#&cgi_lib::common::message(&cgi_lib::common::html_compress($content));
