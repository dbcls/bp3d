#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use File::Basename;
use File::Spec::Functions qw(abs2rel catdir catfile splitdir);
use File::Path;

use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'..','cgi_lib');
use BITS::Config;

require "webgl_common.pl";
use cgi_lib::common;

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
#my $THREEJS = qq|three-r84|;

my @CSS = (
	DEBUG ? "static/js/$EXT_PATH/resources/css/ext-all-debug.css" : "static/js/$EXT_PATH/resources/css/ext-all.css",
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
	"static/js/ag/AgConceptMng.js",
	"static/js/ag/AgDatasetMng.js",
	"static/js/ag/AgDatasetMerge.js",
	"static/js/ag/AgSelectDataset.js",
	"static/js/ag/AgObjEditWindow.js",
	"static/js/ag/AgConceptSegment.js",
	"static/js/ag/AgThumbnailBackgroundPart.js",
	"static/js/ag/AgFileDrop.js",
);

print qq|Content-type: text/html; charset=UTF-8\n\n|;
if(USE_HTML5){
	print <<HTML;
<!DOCTYPE html>
HTML
	print qq|<html lang="ja"|;
}else{
	print <<HTML;
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
HTML
	print qq|<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja"|;
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
	foreach my $cgi_target (qw/get-AgDefaults.cgi load-images.cgi/){
		my $cgi_path = File::Spec->catfile($cgi_dir,$cgi_target);

		my $js_basename = $cgi_target;
		$js_basename =~ s/.cgi$//g;
		$js_basename =~ s/^get\-//g;

		my $js_path = File::Spec->catfile($cgi_dir,'js','ag',qq|$js_basename.js|);

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
			my $mini_css = File::Spec->catfile($css_dir,$css_name.$mini_ext.$css_ext);
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

my @extlist = qw|.min.js .js|;

foreach my $js (@JS){
	next unless(-e $js);

	unless(DEBUG){
		my($js_name,$js_dir,$js_ext) = &File::Basename::fileparse($js,@extlist);
		if(defined $js_ext && length($js_ext)>0 && $js_ext eq '.js'){
			my $mini_js = File::Spec->catfile($js_dir,$js_name.$mini_ext.$js_ext);
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
<title>BackStageEditor</title>
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
	my $sql=<<SQL;
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
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	my $total = $sth->rows();
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$cmp_id,   undef);
	$sth->bind_col(++$column_number, \$cmp_title,   undef);
	$sth->bind_col(++$column_number, \$cmp_abbr,   undef);
	while($sth->fetch){
		push(@$cmp_datas, {
			cmp_id    => $cmp_id-0,
			cmp_title => $cmp_title,
			cmp_abbr  => $cmp_abbr,
		});
	}
	$sth->finish;
	undef $sth;
	print 'Ext.ag.Data.concept_art_map_part='.&cgi_lib::common::encodeJSON($cmp_datas).";\n";
#	print qq|console.log(Ext.data.StoreManager.lookup('conceptArtMapPartStore'));\n|;
}
print <<HTML;
Ext.onReady(function() {
	var config = {};
HTML
	print qq|	config.USE_HTML5 = true;\n| if(USE_HTML5);
	print qq|	config.DEBUG = true;\n| if(DEBUG);
print <<HTML
	var app = new AgApp(config);
});
/*
\$(document).ready(function(){
	\$(document).on('drop',function(e){
		console.log(e);
	});
});
*/
</script>
</head>
<body>
<!--<body ondragover="return AgApp.fileDragover(event);" dragenter="return AgApp.fileDragenter(event);" ondrop="return AgApp.fileDrop(event);">-->
</body>
</html>
HTML
