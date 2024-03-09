#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use File::Basename;
use File::Spec::Functions qw(abs2rel catdir catfile splitdir);
use File::Path;
use File::Find;

use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'..','cgi_lib');
use BITS::Config;

require "webgl_common.pl";
use cgi_lib::common;

my $dbh = &get_dbh();

use constant {
	DEBUG => BITS::Config::DEBUG,
	IS_PUBLIC => BITS::Config::IS_PUBLIC,
	USE_HTML5 => BITS::Config::USE_HTML5,
	USE_APPCACHE => BITS::Config::USE_APPCACHE
};

my $DEFULT_LANG = 'en';


my $EXT_PATH = qq|ext-4.2.1.883|;

#my $EXT_CSS = 'ext-all' . (DEBUG ? '-debug' : '') . '.css';
my $EXT_CSS = 'ext-all-neptune' . (DEBUG ? '-debug' : '') . '.css';
#my $EXT_CSS = 'ext-all-gray' . (DEBUG ? '-debug' : '') . '.css';
#my $EXT_CSS = 'ext-all-access' . (DEBUG ? '-debug' : '') . '.css';

my $EXT_JS = 'ext-all' . (DEBUG ? '-dev' : '') . '.js';

#my $THREEJS = qq|three-r73-2|;
my $THREEJS = qq|three-r84|;

#my $D3JS = qq|d3/4.4.2|;
#my $D3JS = qq|d3/4.3.0|;
#my $D3JS = qq|d3/4.2.8|;
#my $D3JS = qq|d3/4.1.0|;
my $D3JS = qq|d3/3.5.17|;

my $BASE_PATH = 'static';
my $CSS_PATH = qq|$BASE_PATH/css|;
my $JS_PATH = qq|$BASE_PATH/js|;


my @CSS = (
	"$JS_PATH/$EXT_PATH/resources/css/$EXT_CSS",
	"$JS_PATH/$EXT_PATH/ux/css/CheckColumn.css",
	"$JS_PATH/$EXT_PATH/ag/css/ColorPickerPallet.css",
	"$JS_PATH/$EXT_PATH/ag/css/AgParts.css",

	"$CSS_PATH/base.css",
	"$CSS_PATH/anatomography.css"
);
my @JS = (
	DEBUG ? "$JS_PATH/jquery.js" : "$JS_PATH/jquery.min.js",

	DEBUG ? "$JS_PATH/bluebird.js" : "$JS_PATH/bluebird.min.js",

	"$JS_PATH/localForage/localforage.min.js",

	"$JS_PATH/$D3JS/d3".(DEBUG ? '' : '.min').".js",
	"$JS_PATH/$THREEJS/build/three".(DEBUG ? '' : '.min').".js",
#	"$JS_PATH/$THREEJS/examples/js/controls/OrbitControls.js",
#	"$JS_PATH/$THREEJS/examples/js/controls/TrackballControls.js",
#	"$JS_PATH/$THREEJS/examples/js/cameras/CombinedCamera.js",

	"$JS_PATH/$THREEJS/examples/js/Detector.js",
	"$JS_PATH/$THREEJS/examples/js/loaders/OBJLoader.js",
#	"$JS_PATH/$THREEJS/examples/js/loaders/BinaryLoader.js",

	"$JS_PATH/three-bits/three-bits.js",

	"$JS_PATH/$EXT_PATH/$EXT_JS",

	"$JS_PATH/$EXT_PATH/src/menu/Item.js",
#	"$JS_PATH/$EXT_PATH/locale/ext-lang-ja.js",
	"$JS_PATH/$EXT_PATH/locale/ext-lang-$DEFULT_LANG.js",
#	"$JS_PATH/$EXT_PATH/ux/CheckColumn.js",
	"$JS_PATH/$EXT_PATH/ux/form/SearchField.js",
	"$JS_PATH/$EXT_PATH/ux/form/LocalSearchField.js",
	"$JS_PATH/$EXT_PATH/ux/picker/TreePicker.js",
	"$JS_PATH/$EXT_PATH/ux/IFrame.js",

	"$JS_PATH/$EXT_PATH/ag/ColorPickerPallet.js",
	"$JS_PATH/$EXT_PATH/ag/ColorPickerPalletField.js",

	"$JS_PATH/ag/Ag.js",
	DEBUG ? "get-defaults.cgi" : "$JS_PATH/ag/Ag/defaults.js",
#	"get-defaults.cgi",

	"$JS_PATH/ag/Ag/parts.js",
	"$JS_PATH/ag/Ag/model.js",

#	DEBUG ? "load-images.cgi" : "$JS_PATH/ag/load-images.js",

	"$JS_PATH/ag/Ag/localStorage.js",
	"$JS_PATH/ag/Ag/utils.js",

	"$JS_PATH/ag/Ag/main.js",

	"$JS_PATH/ag/Ag/bind.js",
	"$JS_PATH/ag/Ag/bxtJS.js",
	"$JS_PATH/ag/Ag/store.js",

	"$JS_PATH/ag/Ag/delayedTask.js",
	"$JS_PATH/ag/Ag/template.js",
	"$JS_PATH/ag/Ag/component.js",
	"$JS_PATH/ag/Ag/component/filterPanel.js",
#	"$JS_PATH/ag/Ag/component/canvasPanel.js",
#	"$JS_PATH/ag/Ag/component/canvasPanel/settingPanel.js",
#	"$JS_PATH/ag/Ag/component/canvasPanel/rendererPanel.js",
#	"$JS_PATH/ag/Ag/component/canvasPanel/informationPanel.js",

#	"$JS_PATH/ag/Ag/component/canvasPanel/palletPanel.js",
#	"$JS_PATH/ag/Ag/component/canvasPanel/pinPanel.js",
#	"$JS_PATH/ag/Ag/component/canvasPanel/legendPanel.js",
#	"$JS_PATH/ag/Ag/component/canvasPanel/clipPanel.js",
#	"$JS_PATH/ag/Ag/component/canvasPanel/neighborPartsPanel.js",

	"$JS_PATH/ag/Ag/contextmenu.js",

	"$JS_PATH/ag/Ag/mainRenderer.js",
	"$JS_PATH/ag/Ag/subRenderer.js",
);

print qq|Content-type: text/html; charset=UTF-8\n\n|;
if(USE_HTML5){
	print <<HTML;
<!DOCTYPE html>
HTML
	print qq|<html lang="$DEFULT_LANG"|;
}else{
	print <<HTML;
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
HTML
	print qq|<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="$DEFULT_LANG" lang="$DEFULT_LANG"|;
}
if(USE_APPCACHE){
	print qq| manifest="webgl.appcache"|;
}
print qq|>\n|;
print <<HTML;
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta http-equiv="Content-Style-Type" content="text/css" />
<meta http-equiv="Content-Script-Type" content="text/javascript" />
<meta http-equiv="X-UA-Compatible" content="chrome=1">
<meta name="viewport" content="width=device-width, user-scalable=no, minimum-scale=1.0, maximum-scale=1.0">
HTML

my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);

=pod
unless(DEBUG){
	foreach my $cgi_target (qw/get-AgDefaults.cgi load-images.cgi/){
		my $cgi_path = &catfile($cgi_dir,$cgi_target);
		next unless(-e $cgi_path && -x $cgi_path);
		my $js_basename = $cgi_target;
		$js_basename =~ s/.cgi$//g;
		$js_basename =~ s/^get\-//g;

		my $js_path = &catfile($cgi_dir,'static','js','ag',qq|$js_basename.js|);

	#	next unless(-e $cgi_path && (!-e $js_path || -z $js_path || (stat($js_path))[9]<(stat($cgi_path))[9]));

	#	print LOG __LINE__.":\$cmd=[".qq|unset REQUEST_METHOD;echo "// $cgi_pathより自動生成"> $js_path;$cgi_path >> $js_path|."]\n";
		system(qq|unset REQUEST_METHOD;echo "// $cgi_pathより自動生成"> $js_path;$cgi_path >> $js_path|);
		chmod 0600,$js_path if(-e $js_path);
	}
}
=cut

#my $java = qq|/usr/java/default/bin/java|;
#my $yui = qq|/ext1/project/WebGL/local/usr/src/yuicompressor-2.4.6/yuicompressor-2.4.6.jar|;
my $java = qq|/usr/bin/java|;
#my $yui = qq|/bp3d/local/yuicompressor-2.4.6/yuicompressor-2.4.6.jar|;
my $yui = qq|/bp3d/local/yuicompressor/build/yuicompressor-2.4.9.jar|;
my $mini_ext = qq|.min|;
my $logs_stdout = &catfile($FindBin::Bin,'logs','yuicompressor.log');
my $logs_stderr = &catfile($FindBin::Bin,'logs','yuicompressor.err');
@extlist = qw|.min.css .css|;

foreach my $css (@CSS){
	next unless(-e $css);

	unless(DEBUG){
		my($css_name,$css_dir,$css_ext) = &File::Basename::fileparse($css,@extlist);
		if(defined $css_ext && length($css_ext)>0 && $css_ext eq '.css'){
			my $mini_css = &catfile($css_dir,$css_name.$mini_ext.$css_ext);
			if(-w $css_dir){
				unlink $mini_css if(-e $mini_css && ((stat($css))[9]>(stat($mini_css))[9] || (stat($0))[9]>(stat($mini_css))[9]));
				unless(-e $mini_css){
					system(qq|$java -jar $yui --type css --nomunge -o $mini_css $css 1>>$logs_stdout 2>>$logs_stderr|) if(-e $java && -e $yui);
					chmod 0666,$mini_css if(-e $mini_css);
				}
			}
			$css = $mini_css if(-e $mini_css);
		}
	}
	$css .= '?'.(stat($css))[9] unless(USE_APPCACHE);
	print qq|<link rel="stylesheet" href="$css" type="text/css" media="all" charset="UTF-8">\n|;
}

print <<HTML;
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
					system(qq|$java -jar $yui --type js --nomunge -o $mini_js $js 1>>$logs_stdout 2>>$logs_stderr|) if(-e $java && -e $yui);
					chmod 0666,$mini_js if(-e $mini_js);
				}
			}
			$js = $mini_js if(-e $mini_js);
		}
	}
	$js .= '?'.(stat($js))[9] unless(USE_APPCACHE);
	print qq|<script type="text/javascript" src="$js" charset="utf-8"></script>\n|;
}
print <<HTML;
<title>@{[BITS::Config::APP_TITLE]}</title>
<style>
.x-tip .x-tip-body {
	overflow: visible;
	white-space: nowrap;
}
.x-grid-tree-loading .x-tree-icon {
	background-image: url($JS_PATH/$EXT_PATH/resources/themes/images/default/tree/loading.gif) !important;
}
.pallet_checked {
	background-image: url($JS_PATH/$EXT_PATH/ux/css/checked.gif) !important;
}
.pallet_unchecked {
	background-image: url($JS_PATH/$EXT_PATH/ux/css/unchecked.gif) !important;
}


.x-grid3-cell-inner, .x-grid3-hd-inner {
/*	text-overflow : clip;	/* デフォルトは「ellipsis」*/
}
.x-grid-cell-inner, .x-grid-hd-inner {
	text-overflow : clip;	/* デフォルトは「ellipsis」*/
}
/*
.x-form-clear-trigger {
	background-image: url($JS_PATH/$EXT_PATH/resources/themes/images/default/form/clear-trigger.gif);
}

.x-form-search-trigger {
	background-image: url($JS_PATH/$EXT_PATH/resources/themes/images/default/form/search-trigger.gif);
}
*/
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

table.concept-build-list tbody tr:nth-child(odd) {
	background: #f0f0f0;
	border-color: #f0f0f0;
}
table.concept-build-list tbody tr.x-boundlist-selected:nth-child(odd) {
	background: #c1ddf1;
	border-color: #c1ddf1;
}

table.concept-build-list tbody tr:nth-child(odd):hover {
	background: #d6e8f6;
	border-color: #d6e8f6;
}

table.term-search-list tbody tr:nth-child(odd) {
	background: #f0f0f0;
	border-color: #f0f0f0;
}
table.term-search-list tbody tr:nth-child(odd):hover {
	background: #d6e8f6;
	border-color: #d6e8f6;
}

table.term-search-list td strong {
	background-color: #ffff99;
}

tr.term-search-list td div.x-grid-cell-inner {
	white-space: normal;
}
tr.term-search-list td strong {
	background-color: #ffff99;
}

[draggable] {
	-ms-user-select: none;
	-moz-user-select: none;
	-khtml-user-select: none;
	-webkit-user-select: none;
	user-select: none;
	-khtml-user-drag: element;
	-webkit-user-drag: element;
}

table.draggable-data {
	border-collapse: collapse;
	border-spacing: 4px;
/*	border: 1px solid gray;*/
}
table.draggable-data th,
table.draggable-data td {
/*	border: 1px solid gray;*/
/*	padding: 4px;*/
}

.draggable, .draggable label {
	cursor: move;
}

.draggable-hover {
	background: #d6e8f6;
}

.bp3d-tab-filter {
	left: 0px  !important;
}
.bp3d-tab-canvas {
	left: auto  !important;
	right: 0px  !important;
}

.bp3d-form-cb-label {
	white-space: nowrap;
}

a.bp3d-word-button {
	border: 1px solid gray;
	border-radius: 4px;
/*	padding: 2px 2px 0 2px;*/
	padding: 0 2px 0 1px;
	background: gray;
	color: white;
	text-decoration: none;
}
a.bp3d-word-button.bp3d-word-button-selected {
	border-color: #1D7BCA;
	background: #1D7BCA;
}
tr.bp3d-grid-data-row-selected>td.x-grid-cell {
/*	background: #B5DEFF;*/
}
div.bp3d-term {
	line-height: 1.5em;
	display: inline-block;
	margin: 0;
	margin-right: 0.25em;
	white-space: nowrap;
/*	white-space: normal;*/
}
td.bp3d-grid-cell-segment div.x-grid-cell-inner {
	white-space: normal;
}
/*
td.bp3d-grid-cell div.x-grid-cell-inner {
	white-space: normal;
}
*/

td.bp3d-grid-cell-fmaid {
/*	cursor: pointer;*/
}

td.bp3d-grid-cell-synonym div.x-grid-cell-inner,
td.bp3d-grid-cell-relation div.x-grid-cell-inner {
	white-space: normal;
}

a.bp3d-word-underline:link,
a.bp3d-word-underline:visited {
	color: black;
}

</style>
<script>
Ext.BLANK_IMAGE_URL = "$JS_PATH/$EXT_PATH/resources/themes/images/default/tree/s.gif";
Ext.Loader.setConfig({enabled: true});
Ext.Loader.setPath({
	'Ext.ux':'$JS_PATH/$EXT_PATH/ux',
	'Ext.ag':'$JS_PATH/$EXT_PATH/ag'
});
Ext.require([
	'*',
//	'Ext.ux.RowExpander',
//	'Ext.ux.grid.FiltersFeature'
]);
//IE11対策
if(!Ext.isIE){
	var ua = navigator.userAgent;
	if( ua.match(/MSIE/) || ua.match(/Trident/) ) {
		Ext.isIE = true;
		Ext.isIE11 = true;
		Ext.docMode = document.documentMode;
		if(Ext.isGecko) Ext.isGecko = false;
	}
}

if(window.localforage){
	localforage.config({
		driver: [
			localforage.INDEXEDDB,
			localforage.WEBSQL,
			localforage.LOCALSTORAGE
		],
//		name: 'ag-obj'
	});
	window.aglocalforage = localforage.createInstance({
		name: 'ag-store',
		storeName: 'urlvalue'
	});
	window.agstorelocalforage = localforage.createInstance({
		name: 'ag-store',
		storeName: 'storevalue'
	});
}

Ag.data = Ag.data || {};
HTML
if(1){
	my $concept_info_sql=<<SQL;
select
 ci.ci_id,
 ci_name,
 ci_order
from
 concept_info as ci

left join (
 select ci_id,count(cb_id) as cb_id_num from concept_build where cb_use and cb_delcause is null group by ci_id
) as cb on cb.ci_id=ci.ci_id

where
 ci_use and
 ci_delcause is null and
 cb_id_num>0
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
			ci_id      => $ci_id-0,
			ci_name    => $ci_name,
			ci_order   => $ci_order-0,
		});
	}
	$concept_info_sth->finish;
	undef $concept_info_sth;
	undef $concept_info_sql;
	say 'Ag.data.concept_info='.&cgi_lib::common::encodeJSON($concept_info_datas).';';

	my $concept_build_sql=<<SQL;
select
 ci.ci_id,
 ci.ci_name,
 cb.cb_id,
 cb.cb_name,
 EXTRACT(EPOCH FROM cb.cb_release),
 cb.cb_order
from
 concept_build as cb
left join (
 select * from concept_info
) as ci on ci.ci_id=cb.ci_id
where
 cb.cb_use and
 cb.cb_delcause is null
order by
 cb.cb_order
SQL
	my $concept_build_datas;
#	my $ci_id;
#	my $ci_name;
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
			ci_name    => $ci_name,
			cb_id      => $cb_id-0,
			cb_name    => $cb_name,
			cb_release => $cb_release-0,
			cb_order   => $cb_order-0,
		});
	}
	$concept_build_sth->finish;
	undef $concept_build_sth;
	undef $concept_build_sql;
	say 'Ag.data.concept_build='.&cgi_lib::common::encodeJSON($concept_build_datas).';';



	my $model_version_sql=<<SQL;
select
 mv.md_id,
 mv.mv_id,
 mr.mr_id,
 mv.ci_id,
 mv.cb_id,
 md_name_e,
 mv_name_e,
 ci_name,
 cb_name,
 mv_order,
 mr_version
from
 model_version as mv

left join (
 select md_id,md_name_e from model
) as md on md.md_id=mv.md_id

left join (
 select md_id,mv_id,mr_id,mr_version from model_revision
 where (md_id,mv_id,mr_id) in (select md_id,mv_id,max(mr_id) as mr_id from model_revision group by md_id,mv_id)
) as mr on mr.md_id=mv.md_id and mr.mv_id=mv.mv_id

left join (
 select ci_id,ci_name from concept_info
) as ci on ci.ci_id=mv.ci_id

left join (
 select
  ci_id,
  cb_id,
  cb_name,
  EXTRACT(EPOCH FROM cb.cb_release),
  cb_order
 from
  concept_build as cb
) as cb on cb.ci_id=mv.ci_id and cb.cb_id=mv.cb_id

where
 mv_use and
 mv_frozen and
 mv_delcause is null
order by
 mv_order
SQL
	my $model_version_datas;
	my $md_id;
	my $mv_id;
	my $mr_id;
#	my $ci_id;
#	my $cb_id;
	my $md_name_e;
	my $mv_name_e;
#	my $ci_name;
#	my $cb_name;
	my $mv_order;
	my $mr_version;
	my $model_version_sth = $dbh->prepare($model_version_sql) or die $dbh->errstr;
	$model_version_sth->execute() or die $dbh->errstr;
	$column_number = 0;
	$model_version_sth->bind_col(++$column_number, \$md_id,   undef);
	$model_version_sth->bind_col(++$column_number, \$mv_id,   undef);
	$model_version_sth->bind_col(++$column_number, \$mr_id,   undef);
	$model_version_sth->bind_col(++$column_number, \$ci_id,   undef);
	$model_version_sth->bind_col(++$column_number, \$cb_id,   undef);
	$model_version_sth->bind_col(++$column_number, \$md_name_e,   undef);
	$model_version_sth->bind_col(++$column_number, \$mv_name_e,   undef);
	$model_version_sth->bind_col(++$column_number, \$ci_name,   undef);
	$model_version_sth->bind_col(++$column_number, \$cb_name,   undef);
	$model_version_sth->bind_col(++$column_number, \$mv_order,   undef);
	$model_version_sth->bind_col(++$column_number, \$mr_version,   undef);
	while($model_version_sth->fetch){
		my $hash = {
#			md_id      => $md_id-0,
#			mv_id      => $mv_id-0,
#			ci_id      => $ci_id-0,
#			cb_id      => $cb_id-0,
			md_name    => $md_name_e,
			mv_name    => $mv_name_e,
			ci_name    => $ci_name,
			cb_name    => $cb_name,
			mv_order   => $mv_order-0,
			mr_version => $mr_version,
		};
		$hash->{BITS::Config::LOCATION_HASH_MDID_KEY} = $md_id-0;
		$hash->{BITS::Config::LOCATION_HASH_MVID_KEY} = $mv_id-0;
		$hash->{BITS::Config::LOCATION_HASH_MRID_KEY} = $mr_id-0;
		$hash->{BITS::Config::LOCATION_HASH_CIID_KEY} = $ci_id-0;
		$hash->{BITS::Config::LOCATION_HASH_CBID_KEY} = $cb_id-0;
		push(@$model_version_datas, $hash);
	}
	$model_version_sth->finish;
	undef $model_version_sth;
	undef $model_version_sql;
	say 'Ag.data.model_version='.&cgi_lib::common::encodeJSON($model_version_datas).';';

=pod
	my $renderer_data;
	my $renderer_file = &catfile($FindBin::Bin,'renderer_file','renderer_file.json');
	if(-e $renderer_file && -f $renderer_file && -s $renderer_file){
		$renderer_data = &cgi_lib::common::readFileJSON($renderer_file);
	}
	$renderer_data = {} unless(defined $renderer_data && ref $renderer_data eq 'HASH');
	say 'Ag.data.renderer='.&cgi_lib::common::encodeJSON($renderer_data).';';
=cut

}
#環境変数からターゲットバージョンを取得
if(exists $ENV{'AG_FMA_SEARCH_TARGET_VERSION'} && defined $ENV{'AG_FMA_SEARCH_TARGET_VERSION'}){
	say 'Ag.Def.DEF_MODEL_VERSION_TERM="'.$ENV{'AG_FMA_SEARCH_TARGET_VERSION'}.'";';
}
my $files_hash = {};
=pod
open(my $IN,qq{/bin/find $FindBin::Bin -type f -name "*.jgz|});
while(<$IN>){
	my $path = $_;
	$path =~ s/\s*$//g;
	$path =~ s/^\s*//g;
	next unless(-e $path && -f $path && -r $path && -s $path);
	my $filename = &File::Basename::basename($path);
	my $mtime = (stat($path))[9];
	$files_hash->{$filename} = $mtime;
}
close($IN);
=cut
sub file_mtime {
	my $path = $_;
	return unless(-e $path && -f $path && -r $path && -s $path);
	my($filename,$dir,$suffix) = &File::Basename::fileparse($path,'.jgz');
	return unless(defined $suffix && length $suffix);
	my $mtime = (stat($path))[9];
	$files_hash->{qq|$filename$suffix|} = $mtime;
}
&File::Find::find(\&file_mtime, $FindBin::Bin);

if(defined $files_hash && ref $files_hash eq 'HASH'){
	say 'Ag.Def.DEF_FILE_MTIME='.&cgi_lib::common::encodeJSON($files_hash).';';
}

print <<HTML;
Ext.onReady(function() {
	var config = {};
HTML
	say qq|	config.USE_HTML5 = true;| if(USE_HTML5);
	say qq|	config.DEBUG = true;| if(DEBUG);
	say qq|	config.IS_PUBLIC = true;| if(IS_PUBLIC);
print <<HTML
	Ext.QuickTips.init();
	Ext.state.Manager.setProvider(new Ext.state.LocalStorageProvider({prefix:Ag.Def.LOCALDB_PREFIX}));
//	THREE.Cache.enabled = true;
	var AgApp = new Ag(config);
});
</script>
</head>
<body>
<!--<body ondragover="return AgApp.fileDragover(event);" dragenter="return AgApp.fileDragenter(event);" ondrop="return AgApp.fileDrop(event);">-->
</body>
</html>
HTML
