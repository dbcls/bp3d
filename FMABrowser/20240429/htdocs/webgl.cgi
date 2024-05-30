#!/opt/services/ag/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use File::Basename;
use File::Spec::Functions qw(abs2rel catdir catfile splitdir);
use File::Path;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
use BITS::Config;

require "webgl_common.pl";
use cgi_lib::common;

my $dbh = &get_dbh();

use constant {
	DEBUG => BITS::Config::DEBUG,
	USE_HTML5 => BITS::Config::USE_HTML5,
	USE_APPCACHE => BITS::Config::USE_APPCACHE
};

my $DEFULT_LANG = 'en';

#my $EXT_PATH = qq|extjs-4.1.1|;
my $EXT_PATH = qq|ext-4.2.1.883|;
#my $THREEJS = qq|three-r52-0|;
#my $THREEJS = qq|three-r67-0|;
#my $THREEJS = qq|three-r71-0|;
#my $THREEJS = qq|three-r72-0|;
my $THREEJS = qq|three-r73-2|;

my @CSS = (
#	DEBUG ? "js/$EXT_PATH/resources/css/ext-all-debug.css" : "js/$EXT_PATH/resources/css/ext-all.css",
	DEBUG ? "js/$EXT_PATH/resources/css/ext-all-neptune-debug.css" : "js/$EXT_PATH/resources/css/ext-all-neptune.css",
#	DEBUG ? "js/$EXT_PATH/resources/css/ext-all-gray-debug.css" : "js/$EXT_PATH/resources/css/ext-all-gray.css",
#	DEBUG ? "js/$EXT_PATH/resources/css/ext-all-access-debug.css" : "js/$EXT_PATH/resources/css/ext-all-access.css",
	"js/$EXT_PATH/ux/css/CheckColumn.css",
	"js/$EXT_PATH/ag/css/ColorPickerPallet.css",
	"js/$EXT_PATH/ag/css/AgParts.css",

	"css/base.css",
	"css/anatomography.css"
);
my @JS = (
	DEBUG ? "js/jquery.js" : "js/jquery.min.js",
	DEBUG ? "get-AgDefaults.cgi" : "js/ag/AgDefaults.js",

	DEBUG ? "js/$EXT_PATH/ext-all-dev.js" : "js/$EXT_PATH/ext-all.js",
#	"js/$EXT_PATH/ext-all.js",
	"js/$EXT_PATH/src/menu/Item.js",
#	"js/$EXT_PATH/locale/ext-lang-ja.js",
	"js/$EXT_PATH/locale/ext-lang-$DEFULT_LANG.js",
#	"js/$EXT_PATH/ux/CheckColumn.js",
	"js/$EXT_PATH/ux/form/SearchField.js",
	"js/$EXT_PATH/ux/picker/TreePicker.js",
	"js/$EXT_PATH/ux/IFrame.js",

	"js/$EXT_PATH/ag/ColorPickerPallet.js",
	"js/$EXT_PATH/ag/ColorPickerPalletField.js",
	"js/$EXT_PATH/ag/AgParts.js",
	"js/$EXT_PATH/ag/AgModel.js",

	DEBUG ? "load-images.cgi" : "js/ag/load-images.js",

	"js/ag/AgLocalStorage.js",
	"js/ag/AgUtils.js",

	"js/ag/AgMain.js",
	"js/ag/AgStore.js",
	"js/ag/AgObjSearch.js",
	"js/ag/AgMiniRenderer.js",

	DEBUG ? "js/$THREEJS/build/three.js" : "js/$THREEJS/build/three.min.js"
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

unless(DEBUG){
	foreach my $cgi_target (qw/get-AgDefaults.cgi/){
		my $cgi_path = &catfile($cgi_dir,$cgi_target);

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

#my $java = qq|/usr/java/default/bin/java|;
#my $yui = qq|/ext1/project/WebGL/local/usr/src/yuicompressor-2.4.6/yuicompressor-2.4.6.jar|;
my $java = qq|/usr/bin/java|;
my $yui = qq|/opt/services/ag/local/yuicompressor-2.4.6/yuicompressor-2.4.6.jar|;
my $mini_ext = qq|.min|;

@extlist = qw|.min.css .css|;

foreach my $css (@CSS){
	$css = &catfile('static',$css) unless(-e $css);;
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
	print qq|<link rel="stylesheet" href="$css" type="text/css" media="all" charset="UTF-8">\n|;
}

print <<HTML;
<!-- Javascript -->
HTML

@extlist = qw|.min.js .js|;

foreach my $js (@JS){
	$js = &catfile('static',$js) unless(-e $js);
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
	print qq|<script type="text/javascript" src="$js" charset="utf-8"></script>\n|;
}
print <<HTML;
<title>FMABrowser</title>
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
/*
.x-form-clear-trigger {
	background-image: url(static/js/$EXT_PATH/resources/themes/images/default/form/clear-trigger.gif);
}

.x-form-search-trigger {
	background-image: url(static/js/$EXT_PATH/resources/themes/images/default/form/search-trigger.gif);
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


</style>
<script>
Ext.BLANK_IMAGE_URL = "static/js/$EXT_PATH/resources/themes/images/default/tree/s.gif";
Ext.Loader.setConfig({enabled: true});
Ext.Loader.setPath({
	'Ext.ux':'static/js/$EXT_PATH/ux',
	'Ext.ag':'static/js/$EXT_PATH/ag'
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
Ext.ag.Data = Ext.ag.Data || {};
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
	say 'Ext.ag.Data.concept_info='.&cgi_lib::common::encodeJSON($concept_info_datas).';';

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
	say 'Ext.ag.Data.concept_build='.&cgi_lib::common::encodeJSON($concept_build_datas).';';


	my $concept_art_map_part_sql=<<SQL;
select
 cmp.cmp_id,
 cmp.cmp_prefix,
 cmp.cmp_abbr,
 crl.crl_id,
 crl.crl_name,
 cmp.cmp_order
from
 concept_art_map_part as cmp
left join concept_relation_logic as crl on crl.crl_id=cmp.crl_id
where
 cmp.cmp_use and
 cmp.cmp_delcause is null and
 cmp.cmp_abbr is not null
-- and length(cmp.cmp_abbr)>0
order by
 cmp.cmp_order
SQL
	my $concept_art_map_part_datas;
	my $cmp_id;
	my $cmp_prefix;
	my $cmp_abbr;
	my $crl_id;
	my $crl_name;
	my $cmp_order;
	my $concept_art_map_part_sth = $dbh->prepare($concept_art_map_part_sql) or die $dbh->errstr;
	$concept_art_map_part_sth->execute() or die $dbh->errstr;
	$column_number = 0;
	$concept_art_map_part_sth->bind_col(++$column_number, \$cmp_id,    undef);
	$concept_art_map_part_sth->bind_col(++$column_number, \$cmp_prefix,undef);
	$concept_art_map_part_sth->bind_col(++$column_number, \$cmp_abbr,  undef);
	$concept_art_map_part_sth->bind_col(++$column_number, \$crl_id,    undef);
	$concept_art_map_part_sth->bind_col(++$column_number, \$crl_name,  undef);
	$concept_art_map_part_sth->bind_col(++$column_number, \$cmp_order, undef);
	while($concept_art_map_part_sth->fetch){
		push(@$concept_art_map_part_datas, {
			cmp_id     => defined $cmp_id ? $cmp_id-0 : undef,
			cmp_prefix => $cmp_prefix,
			cmp_abbr   => $cmp_abbr,
			crl_id     => defined $crl_id ? $crl_id-0 : undef,
			crl_name   => $crl_name,
			cmp_order  => defined $cmp_order ? $cmp_order-0 : undef,
		});
	}
	$concept_art_map_part_sth->finish;
	undef $concept_art_map_part_sth;
	undef $concept_art_map_part_sql;
	say 'Ext.ag.Data.concept_art_map_part='.&cgi_lib::common::encodeJSON($concept_art_map_part_datas).';';
}
print <<HTML;
Ext.onReady(function() {
	var config = {};
HTML
	say qq|	config.USE_HTML5 = true;| if(USE_HTML5);
	say qq|	config.DEBUG = true;| if(DEBUG);
print <<HTML
//	var app = new AgApp(config);
	FMABrowser = new AgApp(config);
});
</script>
</head>
<body>
<!--<body ondragover="return AgApp.fileDragover(event);" dragenter="return AgApp.fileDragenter(event);" ondrop="return AgApp.fileDrop(event);">-->
</body>
</html>
HTML
