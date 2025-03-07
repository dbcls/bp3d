<?php

# This file was automatically generated by the MediaWiki installer.
# If you make manual changes, please keep track in case you need to
# recreate them later.
#
# See includes/DefaultSettings.php for all configurable settings
# and their default values, but don't forget to make changes in _this_
# file, not there.
#
# Further documentation for configuration settings may be found at:
# http://www.mediawiki.org/wiki/Manual:Configuration_settings

# If you customize your file layout, set $IP to the directory that contains
# the other MediaWiki files. It will be used as a base to locate files.
if( defined( 'MW_INSTALL_PATH' ) ) {
	$IP = MW_INSTALL_PATH;
} else {
	$IP = dirname( __FILE__ );
}

$path = array( $IP, "$IP/includes", "$IP/languages" );
set_include_path( implode( PATH_SEPARATOR, $path ) . PATH_SEPARATOR . get_include_path() );

require_once( "$IP/includes/DefaultSettings.php" );

# If PHP's memory limit is very low, some operations may fail.
# ini_set( 'memory_limit', '20M' );

if ( $wgCommandLineMode ) {
	if ( isset( $_SERVER ) && array_key_exists( 'REQUEST_METHOD', $_SERVER ) ) {
		die( "This script must be run from the command line\n" );
	}
}
## Uncomment this to disable output compression
# $wgDisableOutputCompression = true;

$wgSitename         = "BodyParts3D Wiki";

## The URL base path to the directory containing the wiki;
## defaults for all runtime URL paths are based off of this.
## For more information on customizing the URLs please see:
## http://www.mediawiki.org/wiki/Manual:Short_URL
#$wgScriptPath       = "/project/anatomo_wiki/en";
$wgScriptPath       = "/bp3d/wiki";
$wgScriptExtension  = ".php";
#$wgScriptPath	    = "/wiki";
#$wgScript           = "$wgScriptPath/index.php";
#$wgRedirectScript   = "$wgScriptPath/redirect.php";
#$wgArticlePath      = "$wgScriptPath/$1";

#$wgUsePathInfo=true;
#$wgUsePathInfo=false;

## UPO means: this is also a user preference option

$wgEnableEmail      = false;
$wgEnableUserEmail  = false; # UPO

$wgEmergencyContact = "root@localhost";
$wgPasswordSender = "root@localhost";

$wgEnotifUserTalk = false; # UPO
$wgEnotifWatchlist = false; # UPO
$wgEmailAuthentication = false;

## Database settings
$wgDBtype           = "postgres";
$wgDBserver         = "localhost";
$wgDBname           = "ag_wiki";
$wgDBuser           = "wikiuser";
$wgDBpassword       = "togo";

# Postgres specific settings
$wgDBport           = "38320";
$wgDBmwschema       = "mediawiki";
$wgDBts2schema      = "public";

## Shared memory settings
$wgMainCacheType = CACHE_NONE;
$wgMemCachedServers = array();

## To enable image uploads, make sure the 'images' directory
## is writable, then set this to true:
$wgEnableUploads       = false;
$wgUseImageMagick = true;
$wgImageMagickConvertCommand = "/usr/bin/convert";

## If you use ImageMagick (or any other shell command) on a
## Linux server, this will need to be set to the name of an
## available UTF-8 locale
$wgShellLocale = "en_US.utf8";

## If you want to use image uploads under safe mode,
## create the directories images/archive, images/thumb and
## images/temp, and make them all writable. Then uncomment
## this, if it's not already uncommented:
# $wgHashedUploadDirectory = false;

## If you have the appropriate support software installed
## you can enable inline LaTeX equations:
$wgUseTeX           = false;

$wgLocalInterwiki   = strtolower( $wgSitename );

$wgLanguageCode = "en";

$wgSecretKey = "f17a11ef331fbf436eae80cfa52348bc689f372cc0848eec602485f33892b288";

## Default skin: you can change the default skin. Use the internal symbolic
## names, ie 'standard', 'nostalgia', 'cologneblue', 'monobook':
$wgDefaultSkin = 'monobook';

## For attaching licensing metadata to pages, and displaying an
## appropriate copyright notice / icon. GNU Free Documentation
## License and Creative Commons licenses are supported so far.
# $wgEnableCreativeCommonsRdf = true;
$wgRightsPage = ""; # Set to the title of a wiki page that describes your license/copyright
$wgRightsUrl = "";
$wgRightsText = "";
$wgRightsIcon = "";
# $wgRightsCode = ""; # Not yet used

$wgDiff3 = "/usr/bin/diff3";

# When you make changes to this configuration file, this will make
# sure that cached pages are cleared.
$wgCacheEpoch = max( $wgCacheEpoch, gmdate( 'YmdHis', @filemtime( __FILE__ ) ) );

#######################################
# ここから追加した情報
#######################################

## default timezone
date_default_timezone_set('Asia/Tokyo');
$wgLocaltimezone = "Asia/Tokyo";
$wgLocalTZoffset = date("Z") / 60;

## To enable image uploads, make sure the 'images' directory
## is writable, then set this to true:
$wgEnableUploads       = true;
$wgFileExtensions = array( 'png', 'gif', 'jpg', 'jpeg' );

#skin
#$wgDefaultSkin = 'adcatalog';

#logo
$wgLogo = "$wgScriptPath/images/bp3d.png";

#Favicon
#$wgFavicon = "$wgScriptPath/images/favicon.ico";

#匿名ユーザ編集不可設定
$wgDefaultUserOptions ['editsection'] = false;

#グループの権限は下記のURLを参照
#http://www.mediawiki.org/wiki/Manual:User_rights/ja
#トークページの作成 (createtalk)
$wgGroupPermissions['*']['createtalk'] = false;
$wgGroupPermissions['user']['createtalk'] = false;

#編集APIの使用 (writeapi)
$wgGroupPermissions['*']['writeapi'] = false;
$wgGroupPermissions['user']['writeapi'] = false;

#自動承認された利用者
$wgGroupPermissions['autoconfirmed']['autoconfirmed'] = false;	//半保護されたページの編集 (autoconfirmed)

#登録ユーザの権限
$wgGroupPermissions['user']['upload'] = false;	//ファイルのアップロード (upload)
$wgGroupPermissions['user']['reupload-shared'] = false;	//共有メディア・リポジトリ上のファイルのローカルでの上書き (reupload-shared)
$wgGroupPermissions['user']['reupload'] = false;	//存在するファイルの上書き (reupload)
$wgGroupPermissions['user']['purge'] = false;	//確認を省略したサイトキャッシュの破棄 (purge)
$wgGroupPermissions['user']['minoredit'] = false;	//細部の編集の印づけ (minoredit)

#匿名ユーザ及び管理者グループ以外は編集タブ非表示設定
$wgGroupPermissions['*']['edit'] = false;
$wgGroupPermissions['user']['edit'] = false;
$wgGroupPermissions['sysop']['edit'] = true;

#匿名ユーザ及び管理者グループ以外は移動タブ非表示設定
$wgGroupPermissions['*']['move'] = false;
$wgGroupPermissions['user']['move'] = false;
$wgGroupPermissions['user']['move-subpages']    = false;
$wgGroupPermissions['user']['move-rootuserpages'] = false; // can move root userpages
$wgGroupPermissions['sysop']['move'] = true;

#匿名ユーザ及び管理者グループ以外はページの新規作成不可
$wgGroupPermissions['*']['createpage'] = false;
$wgGroupPermissions['user']['createpage'] = false;
$wgGroupPermissions['sysop']['createpage'] = true;

#bp3dグループの追加＆権限の設定
$wgGroupPermissions['bp3d']['move']             = true;
$wgGroupPermissions['bp3d']['move-subpages']    = true;
#$wgGroupPermissions['bp3d']['move-rootuserpages'] = true; //利用者ページ本体の移動 (move-rootuserpages)
#$wgGroupPermissions['bp3d']['movefile']         = true;	// Disabled for now due to possible bugs and security concerns
$wgGroupPermissions['bp3d']['read']             = true;
$wgGroupPermissions['bp3d']['edit']             = true;
$wgGroupPermissions['bp3d']['createpage']       = true;
#$wgGroupPermissions['bp3d']['createtalk']       = true;
$wgGroupPermissions['bp3d']['writeapi']         = true;
$wgGroupPermissions['bp3d']['upload']           = true;
$wgGroupPermissions['bp3d']['reupload']         = true;
$wgGroupPermissions['bp3d']['reupload-shared']  = true;
$wgGroupPermissions['bp3d']['minoredit']        = true;
$wgGroupPermissions['bp3d']['purge']            = true; // can use ?action=purge without clicking "ok"

#Server定義
#GlobalIDと違う場合は、定義する
#$wgServerName = "221.186.138.155";
#$wgServerName = "192.168.1.224";
#$wgServerName = "192.168.1.237:38321";
$wgServerName = "lifesciencedb.jp";

$wgProto = 'http';
$wgServer = $wgProto.'://' . $wgServerName;

require_once("$IP/extensions/OpenID/OpenID.setup.php");
$wgOpenIDServerStorePath = "$IP/extensions/OpenID/tmp/openidserver/";
$wgOpenIDConsumerStorePath = "$IP/extensions/OpenID/tmp/openidconsumer/";
$wgTrustRoot = "$wgServer$wgScriptPath";

require_once("$IP/extensions/ParserFunctions/ParserFunctions.php");
require_once("$IP/extensions/Variables/Variables.php");
require_once("$IP/extensions/Loops/Loops.php");

#Extension:AdCatalog
require_once("$IP/extensions/AdCatalog/AdCatalog.setup.php");

#log output
$wgDebugLogFile = "$IP/tmp/log.txt";
#$wgShowDebug            = true;
$wgShowExceptionDetails = true;

#外部サイトのファイルを直接埋め込むことを許可
#$wgAllowExternalImagesFrom = 'http://lifesciencedb.jp/';
#$wgAllowExternalImages = false;
$wgAllowExternalImages = true;

#カスタムの名前空間を定義
$wgExtraNamespaces = array(
	100 => "FMA",									#FMA用
	101 => "FMA_talk",
	102 => "isa",									#Is_a用
	103 => "isa_talk",
	104 => "partof",							#Part_of用
	105 => "partof_talk",
	106 => "OBJ",									#未使用
	107 => "OBJ_talk",						#未使用
	108 => "density",							#表現密度用
	109 => "density_talk",
	110 => "FMA_Comment",					#FMAコメント用
	111 => "FMA_Comment_talk",
	112 => "OBJ_Comment",					#未使用
	113 => "OBJ_Comment_talk",		#未使用
	114 => "In_Bodyparts3D",			#未使用
	115 => "In_Bodyparts3D_talk",	#未使用
	116 => "BP3D",								#BP3Dオブジェクト用
	117 => "BP3D_talk",
	118 => "FMAtoBP3D",						#FMAに対応するオブジェクト用
	119 => "FMAtoBP3D_talk",
	120 => "BP3D_Comment",				#BP3Dオブジェクトコメント用
	121 => "BP3D_Comment_talk"
);
$wgContentNamespaces[] = 100;
$wgContentNamespaces[] = 101;
$wgContentNamespaces[] = 102;
$wgContentNamespaces[] = 103;
$wgContentNamespaces[] = 104;
$wgContentNamespaces[] = 105;
$wgContentNamespaces[] = 106;
$wgContentNamespaces[] = 107;
$wgContentNamespaces[] = 108;
$wgContentNamespaces[] = 109;
$wgContentNamespaces[] = 110;
$wgContentNamespaces[] = 111;
$wgContentNamespaces[] = 112;
$wgContentNamespaces[] = 113;
$wgContentNamespaces[] = 114;
$wgContentNamespaces[] = 115;
$wgContentNamespaces[] = 116;
$wgContentNamespaces[] = 117;
$wgContentNamespaces[] = 118;
$wgContentNamespaces[] = 119;
$wgContentNamespaces[] = 120;
$wgContentNamespaces[] = 121;


#サブページを許可する
$wgNamespacesWithSubpages = array(
	NS_MAIN => true,
	NS_TEMPLATE => true,
	NS_FILE => true,
	100 => true,
	102 => true,
	104 => true,
	106 => true,
	108 => true,
	110 => true,
	112 => true,
	114 => true,
	116 => true,
	118 => true,
	120 => true
);

#最初の文字に小文字を許す 
$wgCapitalLinks = false;

#キャッシュを無効にする
$wgCachePages = false;
$wgCacheEpoch = 'date +%Y%m%d%H%M%S';

#$wgSaveDeletedFiles = true;
