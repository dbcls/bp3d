#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use File::Basename;
use File::Spec::Functions qw(abs2rel catdir catfile splitdir);
use File::Path;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
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

my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);

#my $EXT_PATH = qq|js/extjs-4.1.1|;
my $EXT_PATH = qq|js/ext-4.2.1.883|;

my @CSS = (
#	DEBUG ? "$EXT_PATH/resources/css/ext-all-debug.css" : "$EXT_PATH/resources/css/ext-all.css",
#	DEBUG ? "$EXT_PATH/resources/css/ext-all-neptune-debug.css" : "$EXT_PATH/resources/css/ext-all-neptune.css",
	DEBUG ? "$EXT_PATH/resources/css/ext-all-gray-debug.css" : "$EXT_PATH/resources/css/ext-all-gray.css",
#	DEBUG ? "$EXT_PATH/resources/css/ext-all-access-debug.css" : "$EXT_PATH/resources/css/ext-all-access.css",
	"$EXT_PATH/ux/css/CheckColumn.css",
	"$EXT_PATH/$cgi_name/css/ColorPickerPallet.css",
	"$EXT_PATH/$cgi_name/css/RmParts.css",
	"$EXT_PATH/ux/grid/css/GridFilters.css",
	"$EXT_PATH/ux/grid/css/RangeMenu.css",

	"css/base.css",
	"css/anatomography.css",
	"css/RmRender.css",
	"css/segment.css",
	"css/chooser.css"
);
my @JS = (
	DEBUG ? "js/jquery.js" : "js/jquery.min.js",
	DEBUG ? "get-AgDefaults.cgi" : "js/$cgi_name/RmDefaults.js",

	DEBUG ? "$EXT_PATH/ext-all-dev.js" : "$EXT_PATH/ext-all.js",
#	"$EXT_PATH/ext-all.js",
	"$EXT_PATH/src/menu/Item.js",
	"$EXT_PATH/locale/ext-lang-ja.js",
#	"$EXT_PATH/ux/CheckColumn.js",
	"$EXT_PATH/ux/form/SearchField.js",
	"$EXT_PATH/ux/picker/TreePicker.js",
	"$EXT_PATH/ux/IFrame.js",

	"$EXT_PATH/ag/ColorPickerPallet.js",
	"$EXT_PATH/ag/ColorPickerPalletField.js",
	"$EXT_PATH/ag/AgParts.js",
	"$EXT_PATH/ag/AgModel.js",


	DEBUG ? "load-images.cgi" : "js/$cgi_name/load-images.js",
#	"load-images.cgi",

	"js/$cgi_name/RmLocalStorage.js",
	"js/$cgi_name/RmUtils.js",
	"js/$cgi_name/RmURLParser.js",
	"js/$cgi_name/RmWiki.js",
	"js/$cgi_name/RmPalletUtils.js",
	"js/$cgi_name/RmFileUpload.js",
	"js/$cgi_name/RmClass.js",
	"js/$cgi_name/RmMain.js",
	"js/$cgi_name/RmStore.js",
	"js/$cgi_name/RmDatasetMng.js",
	"js/$cgi_name/RmObjEditWindow.js",
	"js/$cgi_name/RmConceptSegment.js",
	"js/$cgi_name/RmThumbnailBackgroundPart.js",
	"js/$cgi_name/RmFileDrop.js",
	"js/$cgi_name/RmMappingMng.js",
	"js/$cgi_name/RmFMABrowser.js",
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

my @extlist = qw|.min.js .js|;

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
<title>RepresentationManager</title>
<style>
.x-grid-tree-loading .x-tree-icon {
	background-image: url($EXT_PATH/resources/themes/images/default/tree/loading.gif) !important;
}
.pallet_checked {
	background-image: url($EXT_PATH/ux/css/checked.gif) !important;
}
.pallet_unchecked {
	background-image: url($EXT_PATH/ux/css/unchecked.gif) !important;
}


.x-grid3-cell-inner, .x-grid3-hd-inner {
/*	text-overflow : clip;	/* デフォルトは「ellipsis」*/
}
.x-grid-cell-inner, .x-grid-hd-inner {
	text-overflow : clip;	/* デフォルトは「ellipsis」*/
}

.x-form-clear-trigger {
	background-image: url($EXT_PATH/resources/themes/images/default/form/clear-trigger.gif);
}

.x-form-search-trigger {
	background-image: url($EXT_PATH/resources/themes/images/default/form/search-trigger.gif);
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
Ext.BLANK_IMAGE_URL = "$EXT_PATH/resources/themes/images/default/tree/s.gif";
Ext.Loader.setConfig({enabled: true});
Ext.Loader.setPath({
	'Ext.ux':'$EXT_PATH/ux',
	'Ext.${cgi_name}':'$EXT_PATH/${cgi_name}'
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
Ext.${cgi_name} = Ext.${cgi_name} || {};
Ext.${cgi_name}.Data = Ext.${cgi_name}.Data || {};
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
	$content .= "Ext.${cgi_name}.Data.concept_info=".(defined $concept_info_datas && ref $concept_info_datas eq 'ARRAY' ? &cgi_lib::common::encodeJSON($concept_info_datas) : '[]').";\n";

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
	my $column_number = 0;
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
			cb_release => $cb_release-0,
			cb_order   => $cb_order-0,
		});
	}
	$concept_build_sth->finish;
	undef $concept_build_sth;
	undef $concept_build_sql;
	$content .= "Ext.${cgi_name}.Data.concept_build=".(defined $concept_build_datas && ref $concept_build_datas eq 'ARRAY' ? &cgi_lib::common::encodeJSON($concept_build_datas) : '[]').";\n";

	my $concept_art_map_part_sql=<<SQL;
select
 cmp_id,
 cmp_title,
 cmp_abbr
from
 concept_art_map_part
where
 cmp_use and cmp_delcause is null
order by
 cmp_id
SQL

	my $cmp_datas;
	my $cmp_id;
	my $cmp_title;
	my $cmp_abbr;
	my $concept_art_map_part_sth = $dbh->prepare($concept_art_map_part_sql) or die $dbh->errstr;
	$concept_art_map_part_sth->execute() or die $dbh->errstr;
	$column_number = 0;
	$concept_art_map_part_sth->bind_col(++$column_number, \$cmp_id,   undef);
	$concept_art_map_part_sth->bind_col(++$column_number, \$cmp_title,   undef);
	$concept_art_map_part_sth->bind_col(++$column_number, \$cmp_abbr,   undef);
	while($concept_art_map_part_sth->fetch){
		push(@$cmp_datas, {
			cmp_id    => $cmp_id-0,
			cmp_title => $cmp_title,
			cmp_abbr  => $cmp_abbr,
		});
	}
	$concept_art_map_part_sth->finish;
	undef $concept_art_map_part_sth;
	undef $concept_art_map_part_sql;
	$content .= "Ext.${cgi_name}.Data.concept_art_map_part=".&cgi_lib::common::encodeJSON($cmp_datas).";\n";
#	print qq|console.log(Ext.data.StoreManager.lookup('conceptArtMapPartStore'));\n|;
}
$content .= <<HTML;
Ext.onReady(function() {
	var config = {};
HTML
	$content .= qq|	config.USE_HTML5 = true;\n| if(USE_HTML5);
	$content .= qq|	config.DEBUG = true;\n| if(DEBUG);
$content .= <<HTML;
//	var app = new RmApp(config);

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
