#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use JSON::XS;
use File::Basename;
use File::Spec::Functions qw(abs2rel catdir catfile splitdir);
use File::Path;
use Cwd qw(abs_path);
use File::Spec;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'..','cgi_lib');
use BITS::Config;

use constant {
	DEBUG => BITS::Config::DEBUG
};

my @extlist = qw|.cgi|;
my($cgi_basename,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);
my $cgi_name = qq|$cgi_basename$cgi_ext|;

#my $EXTJS = qq|extjs-4.1.0|;
#my $EXTJS = qq|extjs-4.1.1|;
my $EXTJS = qq|ext-4.2.1.883|;
#my $THREEJS = qq|three-r48|;
#my $THREEJS = qq|three-r49-19|;
#my $THREEJS = qq|three-r50-0|;
#my $THREEJS = qq|three-r51-0|;
#my $THREEJS = qq|three-r52-0|;
#my $THREEJS = qq|three-r67-0|;
#my $THREEJS = qq|three-r71-0|;
#my $THREEJS = qq|three-r72-0|;
my $THREEJS = qq|three-r73-2|;
#my $THREEJS = qq|three-r84|;
print <<HTML;
Content-type: text/html; charset=UTF-8

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta http-equiv="Content-Style-Type" content="text/css" />
<meta http-equiv="Content-Script-Type" content="text/javascript" />
<meta http-equiv="X-UA-Compatible" content="chrome=1">
<meta name="viewport" content="width=device-width, user-scalable=no, minimum-scale=1.0, maximum-scale=1.0">
HTML

#my $java = qq|/usr/java/default/bin/java|;
#my $yui = qq|/ext1/project/WebGL/local/usr/src/yuicompressor-2.4.6/yuicompressor-2.4.6.jar|;
my $java = qq|/usr/bin/java|;
my $yui = qq|/bp3d/local/yuicompressor-2.4.6/yuicompressor-2.4.6.jar|;
my $mini_ext = qq|.min|;

my @extlist = qw|.min.css .css|;

my @CSS = (
	"static/js/$EXTJS/resources/css/ext-all.css",
#	"static/js/$EXTJS/ux/css/CheckColumn.css",
#	"static/js/$EXTJS/ag/css/ColorPickerPallet.css"
	"static/css/AgRender.css"
);
foreach my $css (@CSS){
	next unless(-e $css);
#	$css .= "?".(stat($css))[9];
#	print qq|<link rel="stylesheet" href="$css" type="text/css" media="all">\n|;

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
	my $mtime = (stat($css))[9];
	print qq|<link rel="stylesheet" href="$css?$mtime" type="text/css" media="all" charset="UTF-8">\n|;
}

my @extlist = qw|.min.js .js|;

my @JS = (
#	"static/js/jquery-dev.js",
	DEBUG ? "static/js/jquery.js" : "static/js/jquery.min.js",
	"static/js/ag/AgDefaults.js",
#	"get-AgDefaults.cgi",
	DEBUG ? "static/js/$EXTJS/ext-all-dev.js" : "static/js/$EXTJS/ext-all.js",
#	"static/js/$EXTJS/ext-all.js",
	"static/js/$EXTJS/ag/AgModel.js",
	"static/js/ag/AgURLParser.js",
	"static/js/ag/AgSubRenderer.js",
	"static/js/ag/AgTestRenderer.js",

	DEBUG ? "static/js/$THREEJS/build/three.js" : "static/js/$THREEJS/build/three.min.js",
	"static/js/$THREEJS/examples/js/loaders/OBJLoader.js",
	"static/js/$THREEJS/examples/js/Detector.js",
	"static/js/three-bits/three-bits.js",

	"static/js/ag/AgClass.js",
	"static/js/ag/AgGrid.js",
#	"static/js/ag/AgGridLine.js",
	"static/js/ag/AgPin.js",
	"static/js/ag/AgColorHeatMap.js",
#	"static/js/ag/AgShader.js",

#	"static/js/$THREEJS/examples/js/loaders/OBJLoader.js",
#	"static/js/$THREEJS/examples/js/loaders/VTKLoader.js",
#	"static/js/$THREEJS/examples/js/Detector.js",

#	"static/js/$THREEJS/examples/js/Stats.js",
#	"static/js/$THREEJS/examples/js/DAT.GUI.min.js",
#	"static/js/$THREEJS/src/materials/MeshLambertMaterial.js",
#	"static/js/$THREEJS/src/textures/Texture.js"
#	"static/js/$THREEJS/src/core/Geometry.js",
#	"static/js/$THREEJS/src/core/Vertex.js",
#	"static/js/$THREEJS/src/materials/LineBasicMaterial.js",
#	"static/js/$THREEJS/src/objects/Line.js",
#	"static/js/$THREEJS/src/renderers/WebGLRenderer.js"
#	"static/js/$THREEJS/src/extras/controls/TrackballControls.js",
#	"static/js/$THREEJS/src/core/Object3D.js",
#	"static/js/$THREEJS/src/core/Ray.js",
#	"static/js/$THREEJS/src/extras/helpers/CameraHelper.js",
#	"static/js/$THREEJS/src/renderers/WebGLRenderer.js"

	"static/js/ag/AgLocalStorage.js",
	"static/js/ag/AgMainRenderer.js",
);
foreach my $js (@JS){
	next unless(-e $js);

#	$js .= "?".(stat($js))[9];
#	print qq|<script src="$js" type="text/javascript" charset="utf-8"></script>\n|;
#	next;

	unless(DEBUG){
		my($js_name,$js_dir,$js_ext) = &File::Basename::fileparse($js,@extlist);
		if(defined $js_ext && length($js_ext)>0 && $js_ext eq '.js'){
			my $mini_js = File::Spec->catfile($js_dir,$js_name.$mini_ext.$js_ext);
			if(-w $js_dir){
				unlink $mini_js if(-e $mini_js && ((stat($js))[9]>(stat($mini_js))[9] || (stat($0))[9]>(stat($mini_js))[9]));
				unless(-e $mini_js){
					system(qq|$java -jar $yui --type js --nomunge -o $mini_js $js|) if(-e $java && -e $yui);
					chmod 0666,$mini_js if(-e $mini_js);
				}
			}
			$js = $mini_js if(-e $mini_js);
		}
	}
	my $mtime = (stat($js))[9];
	print qq|<script type="text/javascript" src="$js?$mtime" charset="utf-8"></script>\n|;
}
print <<HTML;
<title>$cgi_basename</title>
<style>
.pin_label {
	font-family: Arial;
/*	text-shadow: -1px 1px 1px rgb(0,0,0);*/
	margin-left: 25px;
}
</style>
<script>
Ext.BLANK_IMAGE_URL = "static/js/$EXTJS/resources/themes/images/default/tree/s.gif";
Ext.Loader.setConfig({enabled: true});
//Ext.Loader.setPath('Ext.ux', 'js/$EXTJS/ux');
//Ext.Loader.setPath('Ext.ag', 'js/$EXTJS/ag');
Ext.require(['*']);
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
</script>

<script type="x-shader/x-vertex" id="clip_vs">
	varying vec2 vUv;
	varying vec4 worldPosition;
	void main() {
		worldPosition = objectMatrix * vec4( position, 1.0 );
		vUv = uv;
		gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
	}
</script>

<script type="x-shader/x-fragment" id="clip_fs">
	varying vec2 vUv;
	uniform sampler2D texture;

	varying vec4 worldPosition;
	uniform float xClippingPlaneMax;
	uniform float xClippingPlaneMin;
	uniform float yClippingPlaneMax;
	uniform float yClippingPlaneMin;
	uniform float zClippingPlaneMax;
	uniform float zClippingPlaneMin;

	void main() {
		vec4 tcolor = texture2D( texture, vUv );
		gl_FragColor = tcolor;

		if(worldPosition.x<xClippingPlaneMin) discard;
		if(worldPosition.x>xClippingPlaneMax) discard;
		if(worldPosition.z<zClippingPlaneMin) discard;
		if(worldPosition.z>zClippingPlaneMax) discard;
		if(worldPosition.y<yClippingPlaneMin) discard;
		if(worldPosition.y>yClippingPlaneMax) discard;
	}
</script>

</head>
<!--<body ondragover="return cancel(event);" dragenter="return cancel(event);" ondrop="return Drop(event);">-->
<body>
</body>
</html>
HTML
