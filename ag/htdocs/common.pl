use strict;
use warnings;
use feature ':5.10';

no warnings 'redefine';

#use lib '/bp3d/ag/htdocs','/bp3d/ag/htdocs/IM';
use SetEnv;
use LWP::UserAgent;
use Encode;
use Encode::Guess;
use Digest::MD5 qw(md5 md5_hex md5_base64);
use JSON::XS;
use File::Path;
use File::Basename;
use File::Spec::Functions qw(catdir catfile);
use DBD::Pg;
use Carp;
use Compress::Zlib;
use Data::Dumper;
$Data::Dumper::Indent = 1;
$Data::Dumper::Sortkeys = 1;

use AG::API::GlobalPin;
use AG::ComDB::Twitter;

use FindBin;

my $setenv = SetEnv->new();

sub getGlobalPath() {
	return $setenv->{globalURL};
}
sub getBasePath() {
	return $setenv->{basePath};
}

#中間サーバへのパス
sub getIntermediateServerPath() {
#	my $path = qq|IM/|;
	my $path = qq|API|;
#	my $ext = qq|.cgi|;
	my $ext = qq||;
	my %CGI = (
		"animation"   => &catfile($path,"animation$ext"),
		"clip"        => &catfile($path,"clip$ext"),
		"focus"       => &catfile($path,"focus$ext"),
		"focusClip"   => &catfile($path,"focusClip$ext"),
		"image"       => &catfile($path,"image$ext"),
		"map"         => &catfile($path,"map$ext"),
		"pick"        => &catfile($path,"pick$ext"),
		"point"       => &catfile($path,"point$ext"),
		"print"       => &catfile($path,"print$ext"),
		"calcRotAxis" => &catfile($path,"calcRotAxis$ext"),
#		"point_search" => &catfile($path,"point-search.cgi",
		"pointSearch" => &catfile($path,"pointSearch"),
	);
	my $globalpin_cgi = qq|globalpin|;
	$CGI{'globalPin'} = {
		AG::API::GlobalPin::TYPE_PIN => {
			'adding' => &catfile($path,$globalpin_cgi,AG::API::GlobalPin::TYPE_PIN,AG::API::GlobalPin::CMD_ADDING),
			'update' => &catfile($path,$globalpin_cgi,AG::API::GlobalPin::TYPE_PIN,AG::API::GlobalPin::CMD_UPDATE),
			'delete' => &catfile($path,$globalpin_cgi,AG::API::GlobalPin::TYPE_PIN,AG::API::GlobalPin::CMD_DELETE),
			'search' => &catfile($path,$globalpin_cgi,AG::API::GlobalPin::TYPE_PIN,AG::API::GlobalPin::CMD_SEARCH),
			'get'    => &catfile($path,$globalpin_cgi,AG::API::GlobalPin::TYPE_PIN,AG::API::GlobalPin::CMD_GET),
			'getlist'=> &catfile($path,$globalpin_cgi,AG::API::GlobalPin::TYPE_PIN,AG::API::GlobalPin::CMD_GET_LIST),
			'auth'   => &catfile($path,$globalpin_cgi,AG::API::GlobalPin::TYPE_PIN,AG::API::GlobalPin::CMD_AUTH),
		},
		AG::API::GlobalPin::TYPE_GROUP => {
			'adding' => &catfile($path,$globalpin_cgi,AG::API::GlobalPin::TYPE_GROUP,AG::API::GlobalPin::CMD_ADDING),
			'update' => &catfile($path,$globalpin_cgi,AG::API::GlobalPin::TYPE_GROUP,AG::API::GlobalPin::CMD_UPDATE),
			'delete' => &catfile($path,$globalpin_cgi,AG::API::GlobalPin::TYPE_GROUP,AG::API::GlobalPin::CMD_DELETE),
			'search' => &catfile($path,$globalpin_cgi,AG::API::GlobalPin::TYPE_GROUP,AG::API::GlobalPin::CMD_SEARCH),
			'get'    => &catfile($path,$globalpin_cgi,AG::API::GlobalPin::TYPE_GROUP,AG::API::GlobalPin::CMD_GET),
			'getattr'=> &catfile($path,$globalpin_cgi,AG::API::GlobalPin::TYPE_GROUP,AG::API::GlobalPin::CMD_GET_ATTR),
			'getlist'=> &catfile($path,$globalpin_cgi,AG::API::GlobalPin::TYPE_GROUP,AG::API::GlobalPin::CMD_GET_LIST),
			'link'   => &catfile($path,$globalpin_cgi,AG::API::GlobalPin::TYPE_GROUP,AG::API::GlobalPin::CMD_LINK),
			'unlink' => &catfile($path,$globalpin_cgi,AG::API::GlobalPin::TYPE_GROUP,AG::API::GlobalPin::CMD_UNLINK),
			'auth'   => &catfile($path,$globalpin_cgi,AG::API::GlobalPin::TYPE_GROUP,AG::API::GlobalPin::CMD_AUTH),
		}
	};

	return \%CGI;
}

sub getDispEnv {
	return {
#納品用定義(100730)
#		'additionalModelsImpossible' => 'true',
#		'agInterfaceType' => '4',
#		'bgcolorTransparentHidden' => 'true',
#		'coordinateSystemHidden' => 'true',
#		'copyHidden' => 'true',
#		'controlPanelCollapsible' => 'false',
#		'defColorHidden' => 'true',
#		'editLSDBTermHidden' => 'true',
#		'gridHidden' => 'true',
#		'groupHidden' => 'true',
#		'informationHidden' => 'true',
#		'linkEmbedHidden' => 'true',
#		'legendPanelHidden' => 'false',
#		'pinPanelHidden' => 'false',
#		'reviewHidden' => 'false',
#		'rootVisible' => 'true',
#		'urlAnalysisHidden' => 'true',
#		'sectionalViewHidden' => 'false',
#		'palletSelectAllHidden' => 'true',
#		'sampleLatestVersionHidden' => 'true',
#		'savePanelHidden' => 'true',
#		'useImageTransform' => 'false',
#		'useUniversalID' => 'false',
#		'pallteEmptyTextHidden' => 'true',

#納品用定義(100831)
#		'additionalModelsImpossible' => 'true',
#		'agInterfaceType' => '4',
#		'bgcolorTransparentHidden' => 'true',
#		'coordinateSystemHidden' => 'true',
#		'copyHidden' => 'true',
#		'controlPanelCollapsible' => 'false',
#		'defColorHidden' => 'true',
#		'editLSDBTermHidden' => 'true',
#		'gridHidden' => 'true',
#		'groupHidden' => 'false',
#		'informationHidden' => 'true',
#		'legendPanelHidden' => 'false',
#		'linkEmbedHidden' => 'true',
#		'pinPanelHidden' => 'false',
#		'reviewHidden' => 'false',
#		'rootVisible' => 'true',
#		'urlAnalysisHidden' => 'true',
#		'sectionalViewHidden' => 'false',
#		'palletSelectAllHidden' => 'false',
#		'sampleLatestVersionHidden' => 'false',
#		'savePanelHidden' => 'true',
#		'useImageTransform' => 'false',
#		'useUniversalID' => 'false',
#		'pallteEmptyTextHidden' => 'true',

#納品用定義(101224)
#		'addPointElementHidden' => 'false',

#納品用定義(110228)
#		'linkEmbedHidden' => 'true',

#納品用定義(110318)「アナトモサーバの保守及び機能追加作業(統合DB)」
		'autoRotationHidden' => 'true',
		'shortURLHidden' => 'true',
		'useImagePost' => 'false',
#		'treeGroupHidden' => {
#			3 => 'true', #Brain(MAI,Frontal)
#			6 => 'true', #Mouse Brain
#		},
		'usePickPalletSelect' => 'false',
		'localeMenuHidden' => 'true',
		'copyThumbnailHidden' => 'true',

#納品用定義(11????)
		'wikiLinkHidden' => 'true',

#納品用定義(11????)
#		'usePickPartsSelect' => 'true',	#ピック時のパーツ選択
		'usePickPartsSelect' => 'false',	#ピック時のパーツ選択

#デバッグ用の定義
		'additionalModelsImpossible' => 'false',
		'agInterfaceType' => '5',
		'bgcolorTransparentHidden' => 'false',
		'coordinateSystemHidden' => 'false',
		'copyHidden' => 'false',
		'controlPanelCollapsible' => 'true',
		'defColorHidden' => 'false',
		'editLSDBTermHidden' => 'false',
		'gridHidden' => 'false',
		'groupHidden' => 'false',
		'informationHidden' => 'true',
		'legendPanelHidden' => 'false',
		'linkEmbedHidden' => 'false',
		'pinPanelHidden' => 'false',
		'reviewHidden' => 'false',
		'rootVisible' => 'true',
		'urlAnalysisHidden' => 'false',
		'sectionalViewHidden' => 'false',
		'palletSelectAllHidden' => 'false',
		'sampleLatestVersionHidden' => 'false',
		'savePanelHidden' => 'false',
		'useImageTransform' => 'true',
		'useUniversalID' => 'true',
		'pallteEmptyTextHidden' => 'false',
		'addPointElementHidden' => 'false',
		'autoRotationHidden' => 'false',
		'shortURLHidden' => 'false',
		'useImagePost' => 'true',
		'treeGroupHidden' => undef,
		'copyThumbnailHidden' => 'false',
		'usePickPalletSelect' => 'true',
		'localeMenuHidden' => 'false',
		'wikiLinkHidden' => 'false',


#公開環境用の定義
#		'informationHidden' => 'false',
#		'legendPanelHidden' => 'true',
#		'pinPanelHidden' => 'true',
#		'reviewHidden' => 'true',
#		'rootVisible' => 'false',
#		'urlAnalysisHidden' => 'true',
#		'sectionalViewHidden' => 'true',

#テスト環境用の定義
#		'informationHidden' => 'true',
#		'legendPanelHidden' => 'false',
#		'pinPanelHidden' => 'false',
#		'reviewHidden' => 'false',
#		'rootVisible' => 'true',
#		'urlAnalysisHidden' => 'true',
#		'sectionalViewHidden' => 'false',

#anatomo4用設定
#		'agInterfaceType' => '4',
#		'autoRotationHidden' => 'true',
#		'shortURLHidden' => 'true',

#anatomo5用設定
#		'autoRotationHidden' => 'true',
#		'shortURLHidden' => 'true',

#20110725公開用の設定
		'sectionalViewHidden' => 'true',
		'wikiLinkHidden' => 'true',
		'rootVisible' => 'false',
		'informationHidden' => 'false',
		'addPointElementHidden' => 'true',
		'coordinateSystemHidden' => 'true',
		'useUniversalID' => 'false',
		'groupHidden' => 'true',

#20111005後の公開用の設定
#2011/10/11
		'usePickPartsSelect'				=> 'true',	#ピックで色を変える機能（現状のままでOK）を公開環境に反映。
																						#HeatMap表示時には、Barは強制表示が良い。（※フラグなし、基本的に以前のソースに戻した）
#2011/10/11
		'useColorPicker'						=> 'true',	#カラーパレットではなくカラーピッカーの方がうれしい。
#2011/10/11
		'usePalletValueContextmenu'	=> 'true',	#HeatMapの最大、最小はPallet上でこのパーツの値を最大／最小にする、という選択ができるとうれしい。
#2011/10/11
		'hiddenGridColNameJ'				=> 'true',	#Anatomoタブ右側ペインのPalletにIDはデフォルト不要、代わりにKanji、Kanaを追加してほしい。
																						#（※未対応）HeatMap関連の設定は、パレットのValue近辺に統合して配置したい。

#2011/10/17
#・データが無いものはbp3dのパーツ有無を検索結果のリストに表示したい（アイコンなどでカラム幅を小さく）
#	データ有無のカラムでソートしたい（データがあるパーツだけを見たい場合がある）
		'showGridColPartsExists'		=> 'true',

#2011/10/17
#・Anatomographyタブの右側ペイン、Palletタブを一番左に移動して、デフォルト表示としたい
		'moveLeftPalletPanel'				=> 'true',

#2011/10/17
		'localeMenuIcon'						=> 'true',	#・英語-日本語切り替え、Eng→English、Jpn→日本の国旗アイコン
#2011/10/17
#・パレットのデータバージョン違いなどの反映タイミングがおかしい？
#	sampleから"Latest version"チェックを外して表示しても背景が黄色のまま
#→バグ、2011/10/18修正内容を反映済み

#2011/10/17
#・パレットの選択色を青に
#	データバージョンが異なる場合の黄色行などは色が濃くなるだけだと分かりにくい。
#→濃い色に変更

#2011/10/17
#・BP3DViewerタブのパレットデフォルト表示項目の変更
#	体積、器官系は完全削除（表示のon/offも切り替えできなくする）
#	Zmin、Zmaxはデフォルト非表示（オプションでon/off切り替えはOK）
#	（9/28の要望：Anatomographyタブのパレットは幅が狭いのでFMAIDもデフォルト非表示でOK）
		'hiddenGridColZmin'					=> 'true',
		'hiddenGridColZmax'					=> 'true',
		'removeGridColValume'				=> 'true',
		'removeGridColOrganSystem'	=> 'true',
#2011/10/17
#・Informationの著作権に関する記述を独立項目として表示させる（将来的な要望）
#	→将来的にはInformationタブ内容全体を見直し。
#	→BP3Dパレット、AnatomographyパレットのLICENSES記載をInformationタブに統合する。
#		BP3DViewerタブのパレットを右に伸ばしたい
#		Anatomographyタブは右のパネルがそのまま伸びるのが良い
		'moveLicensesPanel'					=> 'true',	#ライセンスパネルをInformationパネルへ移動

#2011/10/17
		'useIncrementalSearch'			=> 'true',	#インクメンタルサーチの使用
#2011/10/17
		'useTabTip'									=> 'true',	#タブにツールチップを表示
#2011/11/08
		'usePickPartsSelectContinu'	=> 'true',	#クリック時の動作で、次のクリックまでパーツが赤い状態を保持して欲しい（パレットとは別に選択中パーツのIDが必要？）
																						#	→他のパーツクリックで赤いパーツ変更
																						#	→何もパーツが無い所をクリックした時点でパーツの選択（赤い状態）解除
		'useClickPickTabSelect'			=> 'true',	#AnatomographyタブのPalletタブが選択されていても、クリック時にはPickタブが有効になって、Pickの動作をしてほしい
		'defaultLocaleJa'						=> 'true',	#デフォルト言語を日本語に変更

#2011/12/21
		'modifyAxisOfRotation'			=> 'true',	#Auto Rotateの回転、回転軸を正しく修正
		'dispTreeChildPartsNum'			=> 'true',	#Treeのフォルダに内包する描画可能パーツ数を表記
		'moveGridOrder'							=> 'true',	#Pickタブ・Palletタブの表示・非表示項目の並び順修正

#20111005後の修正分の非公開設定
		'usePickPartsSelect'				=> 'false',
		'useColorPicker'						=> 'false',
		'usePalletValueContextmenu'	=> 'false',
		'hiddenGridColNameJ'				=> 'false',
		'showGridColPartsExists'		=> 'false',
		'moveLeftPalletPanel'				=> 'false',
		'localeMenuIcon'						=> 'false',
		'hiddenGridColZmin'					=> 'false',
		'hiddenGridColZmax'					=> 'false',
		'removeGridColValume'				=> 'false',
		'removeGridColOrganSystem'	=> 'false',
		'moveLicensesPanel'					=> 'false',
		'useIncrementalSearch'			=> 'false',
		'useTabTip'									=> 'false',
		'usePickPartsSelectContinu'	=> 'false',
		'useClickPickTabSelect'			=> 'false',
		'defaultLocaleJa'						=> 'false',
		'modifyAxisOfRotation'			=> 'false',
		'dispTreeChildPartsNum'			=> 'false',
		'moveGridOrder'							=> 'false',


#2011/10/21公開
		'usePickPartsSelect'				=> 'true',
		'hiddenGridColNameJ'				=> 'true',
		'hiddenGridColZmin'					=> 'true',
		'hiddenGridColZmax'					=> 'true',
		'removeGridColValume'				=> 'true',
		'removeGridColOrganSystem'	=> 'true',
		'moveLeftPalletPanel'				=> 'true',
		'useColorPicker'						=> 'true',
		'localeMenuIcon'						=> 'true',

#2011/11/04公開
		'useTabTip'									=> 'true',

#2011/11/28公開
		'usePalletValueContextmenu'	=> 'true',

#2011/12/21公開
		'defaultLocaleJa'						=> 'true',

#2012/01/20公開
		'moveGridOrder'							=> 'true',

#2012/01/25公開
		'modifyAxisOfRotation'			=> 'true',

#2012/02/20公開
		'showGridColPartsExists'		=> 'true',
		'moveLicensesPanel'					=> 'true',
		'usePickPartsSelectContinu'	=> 'true',
		'useClickPickTabSelect'			=> 'true',
		'dispTreeChildPartsNum'			=> 'true',
	};
}

#my $env = SetEnv->new;
#my @BP3DVERSION = ();
#if(exists($env->{versions})){
#	foreach my $version (@{$env->{versions}}){
#		push(@BP3DVERSION,"$version");
#	}
#}
#my $partslist_mtime = $BP3DVERSION[0];
my $partslist_mtime;

sub getPartsList {
	$partslist_mtime = 'unknown' unless(defined $partslist_mtime);
	return (undef,$partslist_mtime);
}

sub getDefaultColor {
	return lc(qq|#F0D2A0|);
}
sub getDefaultPointColor {
	return lc(qq|#0000FF|);
}

sub getImagePath_old {
	my $fmaid = shift;
	my $position = shift;
	my $version = shift;
	my $geometry = shift;
	my $treetype = shift;
	$position = 'front' if(!defined $position || $position eq "");
	$geometry = '120x120' if(!defined $geometry || $geometry eq "");
	$treetype = '1' if(!defined $treetype || $treetype eq "");
	my $image_path;
	$image_path = qq|bp3d_images/$version| if((defined $image_path && !-e $image_path) || defined $version);
	if(!defined $version && (!defined $image_path || (defined $image_path && !-e $image_path))){
		my($partslist,$partslist_mtime) = &getPartsList();
		$image_path = qq|bp3d_images/$partslist_mtime|;
	}
	$image_path .= qq|/$treetype|;
	if($position eq "rotate"){
		return sprintf(qq|$image_path/%s_%s.gif|,$fmaid,$geometry);
	}else{
		return sprintf(qq|$image_path/%s_%s_%s.png|,$fmaid,$position,$geometry);
	}
}

sub getDefImagePosition {
	return 'front';
}
sub getDefImageGeometry {
	return '120x120';
}
sub getDefImageTreetype {
	return '1';
}
sub getDefImageCredit {
	return '0';
}
sub getImageBaseDir {
	my $version = shift;
	my $treetype = shift;
	$treetype = &getDefImageTreetype() unless(defined $treetype && $treetype ne "");

	my @DIR;
	push(@DIR,$FindBin::Bin) unless(exists $ENV{'REQUEST_METHOD'} && defined $ENV{'REQUEST_METHOD'});
	if(exists $ENV{'AG_DB_HOST'} && defined $ENV{'AG_DB_HOST'} && length $ENV{'AG_DB_HOST'} && exists $ENV{'AG_DB_PORT'} && defined $ENV{'AG_DB_PORT'} && length $ENV{'AG_DB_PORT'}){
		my $tmp_path = &catdir($FindBin::Bin,$ENV{'AG_DB_HOST'},$ENV{'AG_DB_PORT'});
		push(@DIR,$ENV{'AG_DB_HOST'},$ENV{'AG_DB_PORT'}) if(-e $tmp_path && -d $tmp_path);
	}
	push(@DIR,'bp3d_images');

	if(defined $version && $version =~ /^[0-9]+\.[0-9]+\.[0-9]+$/){
		push(@DIR,$version);
	}else{
		my($partslist,$partslist_mtime) = &getPartsList();
		push(@DIR,$partslist_mtime);
	}
	push(@DIR,$treetype) if(defined $treetype);

	return lc(&catdir(@DIR));
}

sub getBaseDirFromID {
	my $fmaid = shift;
	my $image_path = "";
	if($fmaid =~ /^(FMA|BP|FJ|REP|BLD)(.?)(.?)(.?)(.?)/){
		$image_path .= qq|/$1/|.lc(qq|$2$3/$4$5|);
	}elsif($fmaid =~ /^(.?)(.?)(.?)(.?)/){
		$image_path .= qq|/$1$2/$3$4|;
		$image_path = lc($image_path);
	}
	$image_path =~ s/\/$//g;
	return $image_path;
}

sub getImageBaseDirFromID {
	my $fmaid = shift;
	my $version = shift;
	my $treetype = shift;
	$treetype = &getDefImageTreetype() if(!defined $treetype || $treetype eq "");

	my $image_path = &getImageBaseDir($version,$treetype);
	$image_path .= &getBaseDirFromID($fmaid);
	$image_path =~ s/\/$//g;
	return $image_path;
}

sub getImageFileBasename {
	my $fmaid = shift;
	my $position = shift;
	my $geometry = shift;

	return undef unless(defined $fmaid);

	$position = &getDefImagePosition() if(!defined $position || $position eq "");
	$geometry = &getDefImageGeometry() if(!defined $geometry || $geometry eq "");

	if($position eq "rotate"){
		return sprintf(qq|%s_%s|,$fmaid,$geometry);
	}else{
		return sprintf(qq|%s_%s_%s|,$fmaid,$position,$geometry);
	}
}

sub getImageFilename {
	my $fmaid = shift;
	my $position = shift;
	my $geometry = shift;
	my $credit = shift;

	return undef unless(defined $fmaid);

	$position = &getDefImagePosition() if(!defined $position || $position eq "");
	$geometry = &getDefImageGeometry() if(!defined $geometry || $geometry eq "");
	$credit   = &getDefImageCredit()   if(!defined $credit   || $credit eq "");

	my $filename = &getImageFileBasename($fmaid,$position,$geometry);
	$filename .= '_c' if($credit ne '0');
	if($position eq "rotate"){
		$filename .= qq|.gif|;
	}else{
		$filename .= qq|.png|;
	}
	return $filename;
}

sub getImagePath {
	my $fmaid = shift;
	my $position = shift;
	my $version = shift;
	my $geometry = shift;
	my $treetype = shift;
	my $credit = shift;

	return undef unless(defined $fmaid && length $fmaid);

	$position = &getDefImagePosition() if(!defined $position || $position eq "");
	$geometry = &getDefImageGeometry() if(!defined $geometry || $geometry eq "");
	$treetype = &getDefImageTreetype() if(!defined $treetype || $treetype eq "");
	$credit   = &getDefImageCredit()   if(!defined $credit   || $credit eq "");

	my $old_image_path = &getImageBaseDir($version,$treetype);
	my $old_image_file = &catfile($old_image_path,&getImageFilename($fmaid,$position,$geometry,$credit));
	my $image_path = &getImageBaseDirFromID($fmaid,$version,$treetype);
	my $new_image_file = &catfile($image_path,&getImageFilename($fmaid,$position,$geometry,$credit));

#	if(!-e $old_image_file || !-e $new_image_file){
#	if(1 || !-e $new_image_file){
	if(-e $old_image_file && !-e $new_image_file){
		unless(-e $image_path){
			my $m = umask(0);
			&File::Path::mkpath($image_path,0,0777);
			umask($m);
		}

		my @OLD_FILES = ();
		push @OLD_FILES,sprintf(qq|%s.txt|,$fmaid);
		push @OLD_FILES,sprintf(qq|%s.none|,$fmaid);
		foreach my $e ("gif","png"){
			push @OLD_FILES,sprintf(qq|%s.%s|,$fmaid,$e);
			foreach my $g ("120x120","640x640"){
				push @OLD_FILES,sprintf(qq|%s_%s.%s|,$fmaid,$g,$e);
				push @OLD_FILES,sprintf(qq|%s_%s_c.%s|,$fmaid,$g,$e);
				foreach my $p ("front","back","left","right"){
					push @OLD_FILES,sprintf(qq|%s_%s.%s|,$fmaid,$p,$e);
					push @OLD_FILES,sprintf(qq|%s_%s_%s.%s|,$fmaid,$p,$g,$e);

					push @OLD_FILES,sprintf(qq|%s_%s_c.%s|,$fmaid,$p,$e);
					push @OLD_FILES,sprintf(qq|%s_%s_%s_c.%s|,$fmaid,$p,$g,$e);
				}
			}
		}
		foreach my $old_name (@OLD_FILES){
			my $old_path = &catfile($old_image_path,$old_name);
			my $new_path = &catfile($image_path,$old_name);
#			print LOG __LINE__,":\$old_path=[$old_path]\n";
#			print LOG __LINE__,":\$new_path=[$new_path]\n";
			if(-e $old_path && !-e $new_path){
				rename $old_path,$new_path;
				chmod 0666,$new_path;
			}
			unlink $old_path if(-e $old_path && -e $new_path);
		}
		undef @OLD_FILES;
	}
#print LOG __LINE__,":\$new_image_file=[$new_image_file]\n";
	return $new_image_file;
}






sub getImagePaths {
	my $fmaid = shift;
	my $version = shift;
	my $image_path = qq|bp3d_images/|;
	$image_path .= qq|$version/| if(defined $version);
	my @PATH = ();
	open(CMD,"find $image_path -name $fmaid\_*.* |");
	while(<CMD>){
		s/\s*$//g;
		push(@PATH,$_);
	}
	close(CMD);
	open(CMD,"find $image_path -name $fmaid\.* |");
	while(<CMD>){
		s/\s*$//g;
		push(@PATH,$_);
	}
	close(CMD);
	open(CMD,"find $image_path -name $fmaid |");
	while(<CMD>){
		s/\s*$//g;
		push(@PATH,$_);
	}
	close(CMD);
	return wantarray ? @PATH : \@PATH;
}

sub getCachePath {
	my $form = shift;
	my $cginame = shift;

	unless(defined $cginame && length $cginame){
		my @extlist = qw|.cgi .pl|;
		my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);
		$cginame = $cgi_name;
	}

	my $FindBin_Bin = $FindBin::Bin;
	if(exists $ENV{'AG_DB_HOST'} && defined $ENV{'AG_DB_HOST'} && length $ENV{'AG_DB_HOST'} && exists $ENV{'AG_DB_PORT'} && defined $ENV{'AG_DB_PORT'} && length $ENV{'AG_DB_PORT'}){
		my $tmp_path = &catdir($FindBin_Bin,$ENV{'AG_DB_HOST'},$ENV{'AG_DB_PORT'});
		$FindBin_Bin = $tmp_path if(-e $tmp_path && -d $tmp_path);
	}

	my @P = (
		$FindBin_Bin,
		qq|cache_fma|,
		exists $form->{'version'} && defined $form->{'version'} && $form->{'version'} =~ /^[0-9]+\.[0-9]+\.[0-9]+$/ ? $form->{'version'} : 'unknown',
		$cginame,
		exists $form->{'lng'} && defined $form->{'lng'} ? $form->{'lng'} : 'ja',
		exists $form->{'ci_id'} && defined $form->{'ci_id'} ? $form->{'ci_id'} : undef,
		exists $form->{'cb_id'} && defined $form->{'cb_id'} ? $form->{'cb_id'} : undef,
		exists $form->{'md_id'} && defined $form->{'md_id'} ? $form->{'md_id'} : undef,
		exists $form->{'mv_id'} && defined $form->{'mv_id'} ? $form->{'mv_id'} : undef,
		exists $form->{'mr_id'} && defined $form->{'mr_id'} ? $form->{'mr_id'} : undef,
		exists $form->{'bul_id'} && defined $form->{'bul_id'} ? $form->{'bul_id'} : undef,
		exists $form->{'position'} && defined $form->{'position'} ? $form->{'position'} : 'front'
	);
	my $path = &catdir(grep {defined $_} @P);
	return $path;
}

sub checkReferer {
	return 0 if(!exists($ENV{HTTP_REFERER}));
	my $post_cgi = "ag_annotation.cgi";	#環境に合わせて変更する
	my $post_protocol = "http:";				#環境に合わせて変更する
	my $http_host = (split(/,\s*/,(exists($ENV{HTTP_X_FORWARDED_HOST})?$ENV{HTTP_X_FORWARDED_HOST}:$ENV{HTTP_HOST})))[0];
	my $http_referer = $ENV{HTTP_REFERER};
	$http_referer =~ s/\?.*$//g;
	my $script_name;
	my $script_path;
	if(exists($ENV{SCRIPT_NAME})){
		my @TEMP = split(/\//,$ENV{SCRIPT_NAME});
		$script_name = pop @TEMP;
		$script_path = join("/",@TEMP);
		undef @TEMP;
	}
	return 0 if(!(defined $script_name && defined $script_path));
	my $check_path = qq|$post_protocol//$http_host$script_path/$post_cgi|;
	return 0 if($check_path ne $http_referer);
	return 1;
}

sub isPostMethod {
	return 0 if($ENV{REQUEST_METHOD} ne "POST");
	return &checkReferer();
}

##################################
sub checkXSS {
	my $FORM = shift;
	foreach my $key (keys(%$FORM)){
		next unless(defined $FORM->{$key});
		next unless($FORM->{$key} =~ /&lt;\s*script\s*.*?&gt/i);
		&MovedPermanently();
	}
	if(exists($FORM->{'lng'}) && defined($FORM->{'lng'}) && length($FORM->{'lng'})>0){
		$FORM->{'lng'} = lc($FORM->{'lng'});
		&MovedPermanently() unless($FORM->{'lng'} =~ /^(ja|en)$/i);
	}
}

sub MovedPermanently {
	use File::Basename;
	use File::Path;
	my @extlist = qw|.cgi|;
	my($name,$dir,$ext) = fileparse($0,@extlist);

	my $http = &getGlobalPath();
	unless(defined $http){
		$http = exists($ENV{HTTPS})?'https':'http';
		my $http_host = (split(",",(exists($ENV{HTTP_X_FORWARDED_HOST})?$ENV{HTTP_X_FORWARDED_HOST}:$ENV{HTTP_HOST})))[0];
		$http_host =~ s/\s*$//g;
		$http_host =~ s/^\s*//g;
		$http .= qq|://$http_host/$name/$name$ext|;
		$http = qq|://$http_host/$name/|;
	}
	$http .= qq|$name$ext|;

	print qq|Location:$http\n|;
	print qq|Status:301 Moved Permanently\n|;
	print qq|\n|;
	exit;
}

##################################
sub _gethtml {
	my $url = shift;
	my $referer = shift;
	return undef if(!defined $url);
	my $ua = new LWP::UserAgent;
	$ua->agent("AgentName/0.1 " . $ua->agent);
	my $req = HTTP::Request->new(GET => $url);
	$req->referer($referer) if(defined $referer);
	my $res = $ua->request($req);
	if($res->is_success){
		return $res->content;
	}else{
		return undef;
	}
}

sub url_encode($) {
	my $str = shift;
	if(defined $str && length $str){
		$str =~ s/([^\w ])/'%'.unpack('H2', $1)/eg;
		$str =~ tr/ /+/;
	}
	return $str;
}

sub url_decode($) {
	my $str = shift;
	if(defined $str && length $str){
		$str =~ tr/+/ /;
		$str =~ s/%([0-9A-Fa-f][0-9A-Fa-f])/pack('H2', $1)/eg;
	}
	return $str;
}

#------------------------------------------------------------------------------
# フォームデコード
#------------------------------------------------------------------------------
sub decodeForm {
	my $FORM = shift;
	my $formdata;
	my @pairs;

	if(exists($ENV{'REQUEST_METHOD'})){
		if($ENV{'REQUEST_METHOD'} eq "POST"){
			read(STDIN, $formdata, $ENV{'CONTENT_LENGTH'});
		}else{
			$formdata = $ENV{'QUERY_STRING'};
		}
		$FORM->{_formdata} = $formdata;
		@pairs = split(/&/,$formdata);
		foreach my $pair (@pairs) {
			my ($name, $value) = split(/=/, $pair);
			next if($value eq '');
			$value = &url_decode($value);
			unless(&Encode::is_utf8($value)){
				# UTF8フラグ がない場合、decode して、UTF8フラグつきにする
				my $guessed_obj = &Encode::Guess::guess_encoding($value, qw/euc-jp shift-jis/);
				$value = $guessed_obj->decode($value) if(ref $guessed_obj);
			}
			$value = &Encode::encode('utf8', $value) if(&Encode::is_utf8($value));
			$FORM->{$name} .= "\0" if(exists($FORM->{$name}));
			$FORM->{$name} .= $value;
		}
	}else{
		foreach my $pair (@ARGV) {
			my ($name, $value) = split(/=/, $pair);
			next if($value eq '');
			$value = &url_decode($value);
			unless(&Encode::is_utf8($value)){
				# UTF8フラグ がない場合、decode して、UTF8フラグつきにする
				my $guessed_obj = &Encode::Guess::guess_encoding($value, qw/euc-jp shift-jis/);
				$value = $guessed_obj->decode($value) if(ref $guessed_obj);
			}
			$value = &Encode::encode('utf8', $value) if(&Encode::is_utf8($value));
			$FORM->{$name} .= "\0" if(exists($FORM->{$name}));
			$FORM->{$name} .= $value;
		}
	}
}

sub getCookie {
	my $cookie = shift;
	my($xx, $name, $value);
	if(exists $ENV{'HTTP_COOKIE'} && defined $ENV{'HTTP_COOKIE'}){
		foreach $xx (split(/; */, $ENV{'HTTP_COOKIE'})) {
			($name, $value) = split(/=/, $xx);
			next unless(defined $value && length $value);
			$value =~ s/%([0-9A-Fa-f][0-9A-Fa-f])/pack("C", hex($1))/eg;
			$cookie->{$name} = $value;
		}
	}
}

sub setCookie {
	my $name = shift;
	my $val  = shift;
	my $tmp;
#	$name =~ s/(\W)/sprintf("%%%02X", unpack("C", $1))/eg;
	$val  =~ s/(\W)/sprintf("%%%02X", unpack("C", $1))/eg;
	$tmp  = "Set-Cookie: ";
	$tmp .= "$name=$val; ";
	$tmp .= "expires=Tue, 1-Jan-2030 00:00:00 GMT;";
	return($tmp);
}

sub setCookieSession {
	my $name = shift;
	my $val  = shift;
	my $tmp;
#	$name =~ s/(\W)/sprintf("%%%02X", unpack("C", $1))/eg;
	$val  =~ s/(\W)/sprintf("%%%02X", unpack("C", $1))/eg;
	$tmp  = "Set-Cookie: ";
	$tmp .= "$name=$val; ";
#	$tmp .= "expires=Tue, 1-Jan-2030 00:00:00 GMT;";
	return($tmp);
}

sub clearCookie {
	my $name = shift;
#	$name =~ s/(\W)/sprintf("%%%02X", unpack("C", $1))/eg;
	my $tmp = "Set-Cookie: ";
	$tmp .= "$name=; ";
	$tmp .= " expires=Tue, 1-Jan-1980 00:00:00 GMT;";
	return($tmp);
}

sub openidAuth {
	my $parentURL = shift;
	my($lsdb_OpenID,$lsdb_Auth,$lsdb_Config);
	if($parentURL eq "http://openid.dbcls.jp/user/tyamamot"){
		$lsdb_OpenID = "http://openid.dbcls.jp/user/tyamamot";
		$lsdb_Auth = "1";
#	if($parentURL eq "1"){
#		$lsdb_OpenID = "http://openid.dbcls.jp/user/tyamamot";
#		$lsdb_Auth = "1";
#	}elsif($parentURL eq "0"){
#		$lsdb_OpenID = "http://openid.dbcls.jp/user/tyamamot";
#		$lsdb_Auth = "0";
	}else{
		my $ua = LWP::UserAgent->new;
		$ua->timeout(60);
		my $req = new HTTP::Request GET => $parentURL;
		$req->authorization_basic('gogo', 'togo');
		my $res = $ua->request($req);
		if ($res->is_success) {
			my $parent_text = $res->content;
#			my($code, $nmatch) = getcode($parent_text);
#			$parent_text = jcode($parent_text)->utf8 if($code ne "");
			unless(&Encode::is_utf8($parent_text)){
				# UTF8フラグ がない場合、decode して、UTF8フラグつきにする
				my $guessed_obj = &Encode::Guess::guess_encoding($parent_text, qw/euc-jp shift-jis/);
				$parent_text = $guessed_obj->decode($parent_text) if(ref $guessed_obj);
			}
			($lsdb_OpenID,$lsdb_Auth,$lsdb_Config) = split(/\t/,$parent_text);
			$lsdb_Config =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg if(defined $lsdb_Config);
		}
	}
	return ($lsdb_OpenID,$lsdb_Auth,$lsdb_Config);
}

sub getConfig {
	my $hash = shift;
	my $config = shift;
	my($xx, $name, $value);
	if(defined $config){
		foreach $xx (split(/; */, $config)) {
			($name, $value) = split(/=/, $xx);
			$value =~ s/%([0-9A-Fa-f][0-9A-Fa-f])/pack("C", hex($1))/eg;
			$hash->{$name} = $value;
		}
	}
}

sub getParent {
	my $hash = shift;
	my $parentURL = shift;
	my($xx, $name, $value);
	if(defined $parentURL){
		my $i = index($parentURL,"?");
		if($i>=0){
			$hash->{url} = substr($parentURL,0,$i);
			my $formdata = substr($parentURL,$i+1);
			my @pairs = split(/&/,$formdata);
			foreach my $pair (@pairs) {
				my ($name, $value) = split(/=/, $pair);
				$value =~ tr/+/ /;
				$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
				if($value ne ''){
					$hash->{$name} .= "\0" if(exists($hash->{$name}));
					$hash->{$name} .= $value;
				}
			}
		}
	}
}


sub _urlinsp {
	my $url = shift;
#	$url =~ s/\/([^\/])/\/ $1/g;
#	$url =~ s/([\?\&])(\w)/\/$1 $2/g;
	return $url;
}

sub _trim {
	my $str = shift;
	$str =~ s/^\s*//g;
	$str =~ s/\s*$//g;
	return $str;
}

sub _hesc {
	my $str = shift;
	$str =~ s/&/&amp;/g;
	$str =~ s/</&lt;/g;
	$str =~ s/>/&gt;/g;
	$str =~ s/"/&quot;/g;
	$str =~ s/'/&#39;/g;
	return $str;
}

sub _hdesc {
	my $str = shift;
	$str =~ s/&amp;/&/g;
	$str =~ s/&lt;/</g;
	$str =~ s/&gt;/>/g;
	$str =~ s/&quot;/"/g;
	$str =~ s/&#39;/'/g;
	return $str;
}

sub _tesc {
	my $str = shift;
	$str =~ s/\r\n/\n/g;
	$str =~ s/\r\r/\n/g;
	$str =~ s/\r/\n/g;
	$str =~ s/\t/        /g;
	return $str;
}

sub convCode {
	my $str = shift;
	my($code, $nmatch) = getcode($str);

	unless(&Encode::is_utf8($str)){
		# UTF8フラグ がない場合、decode して、UTF8フラグつきにする
		my $gussed_obj = &Encode::Guess::guess_encoding($str, qw/euc-jp shift-jis/);
		$str = $gussed_obj->decode($str) if(ref $gussed_obj);
	}
	$str = jcode($str)->utf8 if($code ne "" && $code ne "utf8");
	$str = &Encode::encode_utf8($str) if(&Encode::is_utf8($str));
	return $str;
}

sub authFeedback {
	my $dbh = shift;
	my $form = shift;
	my $lsdb_Auth = shift;
	my $lsdb_OpenID = shift;

	my @bind_values = ();
	my $rows;
	my $sql;
	$sql = qq|select c_id from comment where c_id=?|;

	push(@bind_values,$form->{c_id});

	if($lsdb_Auth || (exists($form->{c_passwd}) && $form->{c_passwd} eq "gogo")){
	}elsif($lsdb_OpenID){
		$sql .= qq| AND c_openid=?|;
		push(@bind_values,$lsdb_OpenID);
	}elsif(exists($form->{c_passwd})){
		$sql .= qq| AND c_passwd=?|;
		my $c_passwd = &_trim($form->{c_passwd});
		$c_passwd = md5_hex($c_passwd."bits.cc");
		push(@bind_values,$c_passwd);
	}else{
		$sql .= qq| AND c_passwd is null|;
	}
	my $sth = $dbh->prepare($sql);
	$sth->execute(@bind_values);
	$rows = $sth->rows;
	$sth->finish();
	undef $sth;
	undef $sql;
	undef @bind_values;
	return $rows;
}

sub spaceEncode {
	my $query = shift;
	my $space = qq|　|;
	$query = &Encode::decode_utf8($query) unless(&Encode::is_utf8($query));
	$space = &Encode::decode_utf8($space) unless(&Encode::is_utf8($space));
	$query =~ s/$space/ /g;
	$query = &Encode::encode_utf_8($query);
	return $query;
}

###############################################################################
sub convertOrdinalIndicator_Eng2Num {
	my $aString = shift;
	my %conv_hash = (
		'first'       =>  '1st',
		'second'      =>  '2nd',
		'third'       =>  '3rd',
		'fourth'      =>  '4th',
		'fifth'       =>  '5th',
		'sixth'       =>  '6th',
		'seventh'     =>  '7th',
		'eighth'      =>  '8th',
		'ninth'       =>  '9th',
		'tenth'       => '10th',
		'eleventh'    => '11th',
		'twelfth'     => '12th',
		'thirteenth'  => '13th',
		'fourteenth'  => '14th',
		'fifteenth'   => '15th',
		'sixteenth'   => '16th',
		'seventeenth' => '17th',
		'eighteenth'  => '18th',
		'nineteenth'  => '19th'
	);
	foreach my $key (keys(%conv_hash)){
		my $val = $conv_hash{$key};
		$aString =~ s/\b$key\b/$val/ig;
	}
	return $aString;
}

sub convertOrdinalIndicator_Num2Eng {
	my $aString = shift;
	my %conv_hash = (
		 '1st' => 'first',
		 '2nd' => 'second',
		 '3rd' => 'third',
		 '4th' => 'fourth',
		 '5th' => 'fifth',
		 '6th' => 'sixth',
		 '7th' => 'seventh',
		 '8th' => 'eighth',
		 '9th' => 'ninth',
		'10th' => 'tenth',
		'11th' => 'eleventh',
		'12th' => 'twelfth',
		'13th' => 'thirteenth',
		'14th' => 'fourteenth',
		'15th' => 'fifteenth',
		'16th' => 'sixteenth',
		'17th' => 'seventeenth',
		'18th' => 'eighteenth',
		'19th' => 'nineteenth',
	);
	foreach my $key (keys(%conv_hash)){
		my $val = $conv_hash{$key};
		$aString =~ s/\b$key\b/$val/ig;
	}
	return $aString;
}
###############################################################################

###############################################################################
sub getBP3DTablename {
	my $version = shift;
	return undef unless(defined $version);
	my $table = "bp3d_$version";
	$table =~ s/\./_/g;
	return $table;
}

###############################################################################

###############################################################################
sub getDegenerateSameShapeIcons {
	my $dbh = shift;
	my $form = shift;
	my $fma_ids = shift;

	my $cdi_ids;
	my $sql = qq|
select
 cdi_id,
 cdi_taid
from
 concept_data_info
where
 ci_id=? AND
 cdi_name in (%s)
group by
 cdi_id,
 cdi_taid
order by
 cdi_id
|;
	my $sth = $dbh->prepare(sprintf($sql,join(",",map {'?'} @$fma_ids))) or die;
	my @bind_values = ();
	push(@bind_values,$form->{'ci_id'});
	push(@bind_values,@$fma_ids);
	$sth->execute(@bind_values);
	if($sth->rows>0){
		my $cdi_id;
		my $cdi_taid;
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_id, undef);
		$sth->bind_col(++$column_number, \$cdi_taid, undef);
		while($sth->fetch){
			$cdi_ids->{$cdi_id} = $cdi_taid if(defined $cdi_id);
		}
	}
	$sth->finish;
	undef $sth;

	my $cdi_ids_sql = join(",",map {'?'} keys(%$cdi_ids));
	@bind_values = ();
	push(@bind_values,$form->{'ci_id'});
	push(@bind_values,$form->{'cb_id'});
	push(@bind_values,$form->{'md_id'});
	push(@bind_values,$form->{'mv_id'});
	push(@bind_values,$form->{'mr_id'});
	push(@bind_values,$form->{'bul_id'});
	push(@bind_values,sort keys(%$cdi_ids));

	push(@bind_values,$form->{'ci_id'});
	push(@bind_values,sort keys(%$cdi_ids));

	$sql = qq|
select
 get_mca_id(rep.rep_id) as mca_id,
 cdi.cdi_taid,
 rep.rep_primitive,
 (rep.rep_density_objs::real/rep.rep_density_ends::real) as rep_density,
 cdi.cdi_name
from
 concept_data_info as cdi

left join (
 select * from representation where (ci_id,cb_id,md_id,mv_id,mr_id,bul_id,cdi_id) in (
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
    rep_delcause is null and
    ci_id=? and
    cb_id=? and
    md_id=? and
    mv_id=? and
    mr_id<=? and
    bul_id=? and
    cdi_id in ($cdi_ids_sql)
   group by
    ci_id,
    cb_id,
    md_id,
    mv_id,
    bul_id,
    cdi_id
 )
) as rep on
 rep.ci_id=cdi.ci_id AND
 rep.cdi_id=cdi.cdi_id

where
 rep.rep_id is not null and
 cdi.cdi_delcause is null and
 cdi.ci_id=? and
 cdi.cdi_id in ($cdi_ids_sql)
order by
 mca_id,
 cdi.cdi_taid NULLS LAST,
 rep.rep_primitive,
 rep_density DESC NULLS LAST,
 rep.rep_depth DESC NULLS LAST
|;
#print LOG __LINE__,":\$sql=[$sql]\n";
#print LOG __LINE__,":\@bind_values=[".join(",",@bind_values)."]\n";

	my $cdi_names;
	$sth = $dbh->prepare($sql) or die;
	$sth->execute(@bind_values);
	if($sth->rows>0){
		my $mca_id;
		my $cdi_taid;
		my $rep_primitive;
		my $rep_density;
		my $cdi_name;
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$mca_id, undef);
		$sth->bind_col(++$column_number, \$cdi_taid, undef);
		$sth->bind_col(++$column_number, \$rep_primitive, undef);
		$sth->bind_col(++$column_number, \$rep_density, undef);
		$sth->bind_col(++$column_number, \$cdi_name, undef);
		while($sth->fetch){
			next unless(defined $mca_id);
			if(defined $cdi_names){
				$cdi_names->{$mca_id} = $cdi_name unless(defined $cdi_names->{$mca_id});
			}else{
				$cdi_names->{$mca_id} = $cdi_name;
			}
		}
	}
	$sth->finish;
	undef $sth;
	if(defined $cdi_names){
		@$fma_ids = map {$cdi_names->{$_}} keys(%$cdi_names);
	}
}

###############################################################################

###############################################################################

my $sth_fma;
my $sth_bp3d_bid = {};
my $sth_bp3d_fid = {};
my $sth_point;
my $sth_point_children;
my $DEF_COLOR = {};
my $sth_lsdb_term;
my $sth_lsdb_item;
my $sth_lsdb_sentence;
my $sth_lsdb_exclusion;
my $sth_buildup_tree;
my $Twitter;
my $JSONXS = JSON::XS->new->utf8->indent(0)->canonical(1);

sub getFMA {
	my $dbh = shift;
	my $form = shift;
	my $f_id = shift;
	my $LOG = shift;
	my $f_id2 = $f_id;
#	$f_id2 =~ s/\D+$//g;


#	my @extlist = qw|.cgi .pl|;
#	my($cgi_name,$cgi_dir,$cgi_ext) = fileparse($0,@extlist);


	my $old_umask = umask(0);
#	umask(0);
#	my $cache_path = &catdir($FindBin::Bin,qq|cache_fma|,$form->{'version'},qq|common|,$form->{'lng'},$form->{'ci_id'},$form->{'cb_id'},$form->{'md_id'},$form->{'mv_id'},$form->{'mr_id'},$form->{'bul_id'},$form->{'position'});
	my $cache_path = &getCachePath($form,qq|common|);
	if($f_id =~ /^([A-Za-z]+)([0-9]{2})([0-9]{1,2})/){
		$cache_path = &catdir($cache_path,$1,$2,sprintf("%02d",$3));
	}elsif($f_id =~ /^([A-Za-z]+)([0-9]{1,2})/){
		$cache_path = &catdir($cache_path,$1,'00',sprintf("%02d",$2));
	}
	&File::Path::make_path($cache_path,{mode=>0777}) unless(-e $cache_path);
	my $cache_file = &catfile($cache_path,qq|$f_id.json|);
	unlink $cache_file if(-e $cache_file);
	if(-e $cache_file && -s $cache_file){
		my $rtn;
		my $CACHE;
		my $json;
		if(open($CACHE,"< $cache_file")){
			flock($CACHE,1);
			$json = <$CACHE>;
			close($CACHE);
		}
		if(defined $json){
			eval{$rtn = $JSONXS->decode($json);};
		}
		if(defined $rtn){

			#動的に変化する情報を取り込む
			$rtn->{'tweets'} = undef;
			$rtn->{'tweet_num'} = 0;
			if(defined $rtn->{'b_id'}){
				$Twitter = new AG::ComDB::Twitter unless(defined $Twitter);
				if(exists $rtn->{'mca_id'} && defined $rtn->{'mca_id'}){
					my $mca_id = $rtn->{'mca_id'};
					my $rep_id;
					my @REP_IDS;
					my $sql = qq|select rep_id from representation where rep_delcause is null AND mca_id=? group by rep_id|;
					my $sth = $dbh->prepare($sql) or croak $dbh->errstr;
					$sth->execute($mca_id) or croak $dbh->errstr;
					my $column_number = 0;
					$sth->bind_col(++$column_number, \$rep_id, undef);
					while($sth->fetch){
						push(@REP_IDS,$rep_id) if(defined $rep_id);
					}
					$sth->finish;
					undef $sth;
					if(scalar @REP_IDS){
						$rtn->{'tweets'} = $Twitter->get_tweets(\@REP_IDS,$mca_id);
						$rtn->{'tweet_num'} = scalar @{$rtn->{'tweets'}} if(defined $rtn->{'tweets'});
					}
					undef @REP_IDS;
				}else{
					$rtn->{'tweets'} = $Twitter->get_tweets($rtn->{'b_id'});
					$rtn->{'tweet_num'} = scalar @{$rtn->{'tweets'}} if(defined $rtn->{'tweets'});
				}
			}
			return $rtn;
		}
	}

#	print LOG __LINE__,":",$0,"\n";

#	foreach my $key (sort keys(%$form)){
#		print LOG __LINE__,":\$form->{$key}=[",$form->{$key},"]\n";
#	}
#	print LOG __LINE__,":\$f_id=[$f_id]\n";
#	print LOG __LINE__,":\$f_id2=[$f_id2]\n";

#	my $bp3d_table = "bp3d_$form->{'version'}";
#	$bp3d_table =~ s/\./_/g;

	my $version = $form->{'version'};
#	my $bp3d_table = &getBP3DTablename($form->{'version'});

	my $t_type = defined $form->{'bul_id'} ? $form->{'bul_id'} : (defined $form->{'t_type'} ? $form->{'t_type'} : '1');

	unless(defined $DEF_COLOR->{$version}){
		$DEF_COLOR->{$version} = {};
		my $color_path = qq|data/$version/bp3d.color|;
		$color_path = qq|data/bp3d.color| unless(-e $color_path);
		if(-e $color_path){
			open(IN,"< $color_path");
			while(<IN>){
				s/\s*$//g;
				s/^\s*//g;
				next if(/^#/);
				my($id,$color) = split(/\t/);
				next if($id eq "" || $color eq "");
				next if(exists($DEF_COLOR->{$version}->{$id}));
				$DEF_COLOR->{$version}->{$id} = $color;
			}
			close(IN);
		}
	}
#	print STDERR __LINE__,":",&Data::Dumper::Dumper($DEF_COLOR);

	unless(defined $sth_buildup_tree->{$form->{'md_id'}}->{$form->{'mv_id'}}->{$form->{'mr_id'}}->{$form->{'ci_id'}}->{$form->{'cb_id'}}->{$form->{'bul_id'}}){
		my $sql=<<SQL;
select count(*) from buildup_tree as but
left join (select ci_id,cdi_id,cdi_name from concept_data_info) as cdi on (cdi.ci_id = but.ci_id and cdi.cdi_id = but.cdi_pid)
where 
 but.but_delcause is null and
 but.md_id=$form->{'md_id'} and
 but.mv_id=$form->{'mv_id'} and
 but.mr_id=$form->{'mr_id'} and
 but.ci_id=$form->{'ci_id'} and
 but.cb_id=$form->{'cb_id'} and
 but.bul_id=$form->{'bul_id'} and
 cdi.cdi_name=?
SQL
		$sth_buildup_tree->{$form->{'md_id'}}->{$form->{'mv_id'}}->{$form->{'mr_id'}}->{$form->{'ci_id'}}->{$form->{'cb_id'}}->{$form->{'bul_id'}} = $dbh->prepare($sql);
	}

	unless(defined $sth_fma){
		my $sql_fma =<<SQL;
select 
 cdi.cdi_name_j,
 COALESCE(cd.cd_name,bd.cd_name,cdi.cdi_name_e),
 cdi.cdi_name_k,
 cdi.cdi_name_l,
 cdi.cdi_syn_j,
 COALESCE(cd.cd_syn,bd.cd_syn,cdi.cdi_syn_e),

 COALESCE(cd.cd_def,bd.cd_def),

 COALESCE(cd.cd_delcause,bd.cd_delcause),
 EXTRACT(EPOCH FROM COALESCE(cd.cd_entry,bd.cd_entry)),
 COALESCE(cd.cd_openid,bd.cd_openid),
 cdi.cdi_taid,
 COALESCE(cd.phy_name,bd.phy_name),
 COALESCE(cd.phy_id,bd.phy_id),
 COALESCE(cd.seg_name,bd.seg_name),
 COALESCE(cd.seg_color,bd.seg_color,cs_null.seg_color) as seg_color,
 COALESCE(cd.seg_thum_bgcolor,bd.seg_thum_bgcolor,cs_null.seg_thum_bgcolor) as seg_thum_bgcolor,
 COALESCE(cd.seg_thum_bocolor,bd.seg_thum_bocolor,cs_null.seg_thum_bocolor) as seg_thum_bocolor,
 COALESCE(cd.seg_id,bd.seg_id)

from
 concept_data_info as cdi

left join (
 select
  f.*,
  p.phy_name,
  cs.seg_name,
  cs.seg_color,
  cs.seg_thum_bgcolor,
  cs.seg_thum_bocolor
 from
  concept_data as f
 left join (select phy_id,phy_name from concept_physical) as p on p.phy_id = f.phy_id
 left join (select seg_id,seg_name,seg_color,seg_thum_bgcolor,seg_thum_bocolor from concept_segment) as cs on cs.seg_id = f.seg_id
 where
  cd_delcause is null and 
  ci_id=$form->{'ci_id'} and
  cb_id=$form->{'cb_id'}
) as cd on
 cdi.cdi_id=cd.cdi_id

left join (
 select
  f.*,
  p.phy_name,
  cs.seg_name,
  cs.seg_color,
  cs.seg_thum_bgcolor,
  cs.seg_thum_bocolor
 from
  buildup_data as f
 left join (select phy_id,phy_name from concept_physical) as p on p.phy_id = f.phy_id
 left join (select seg_id,seg_name,seg_color,seg_thum_bgcolor,seg_thum_bocolor from concept_segment) as cs on cs.seg_id = f.seg_id
 where
  cd_delcause is null and 
  md_id=$form->{'md_id'} and
  mv_id=$form->{'mv_id'} and
  mr_id=$form->{'mr_id'} and
  ci_id=$form->{'ci_id'} and
  cb_id=$form->{'cb_id'}
) as bd on
 cdi.cdi_id=bd.cdi_id

 left join (select seg_id,seg_color,seg_thum_bgcolor,seg_thum_bocolor from concept_segment) as cs_null on cs_null.seg_id = 0

where
 COALESCE(cd.cd_delcause,bd.cd_delcause) is null and 
 cdi.ci_id=$form->{'ci_id'} and 
 cdi.cdi_name=?
SQL
		$sth_fma = $dbh->prepare($sql_fma);
#print LOG __LINE__,":\$sql_fma=[$sql_fma]\n";
	}
	unless(defined $sth_bp3d_bid->{$version}->{$t_type}){
		my $sql_bp3d_bid =<<SQL;
select
 rep_id,
 cdi_name,

 cdi_name_j,
 COALESCE(cd.cd_name,bd.cd_name,cdi_name_e),
 cdi_name_k,
 cdi_name_l,
 cdi_syn_j,
 COALESCE(cd.cd_syn,bd.cd_syn,cdi_syn_e),

 COALESCE(cd.cd_def,bd.cd_def,cdi_syn_e),

 rep_xmin,
 rep_xmax,
 rep_ymin,
 rep_ymax,
 rep_zmin,
 rep_zmax,
 rep_volume,
 rep_cube_volume,
 (rep_density_objs::real/rep_density_ends::real) as rep_density,
 rep_density_objs,
 rep_density_ends,
 rep_density_end_ids,
 rep_primitive,
 rep_color,
 rep_delcause,
 EXTRACT(EPOCH FROM rep_entry),
 rep_openid,
 mca_id,
 rep_depth
from
 representation as rep

left join (
 select * from concept_data_info
) as cdi on 
 cdi.ci_id = rep.ci_id and
 cdi.cdi_id = rep.cdi_id

left join (
 select * from concept_data
) as cd on 
 cd.ci_id = rep.ci_id and
 cd.cb_id = rep.cb_id and
 cd.cdi_id = rep.cdi_id

left join (
 select * from buildup_data
) as bd on 
 bd.md_id = rep.md_id and
 bd.mv_id = rep.mv_id and
 bd.mr_id = rep.mr_id and
 bd.ci_id = rep.ci_id and
 bd.cb_id = rep.cb_id and
 bd.cdi_id = rep.cdi_id

where
 rep.rep_delcause is null and
 rep.rep_id=?
SQL
		$sth_bp3d_bid->{$version}->{$t_type} = $dbh->prepare($sql_bp3d_bid);
#print LOG __LINE__,":\$sql_bp3d_bid=[$sql_bp3d_bid]\n";
	}
	unless(defined $sth_bp3d_fid->{$version}->{$t_type}){
		#concenpt_idから検索する場合は、複数ヒットする場合がある為、最新の１件を取得する
		my $sql_bp3d_fid =<<SQL;
select
 rep_id,
 cdi_name,

 cdi_name_j,
 COALESCE(cd.cd_name,bd.cd_name,cdi_name_e),
 cdi_name_k,
 cdi_name_l,
 cdi_syn_j,
 COALESCE(cd.cd_syn,bd.cd_syn,cdi_syn_e),

 COALESCE(cd.cd_def,bd.cd_def,cdi_def_e),

 rep_xmin,
 rep_xmax,
 rep_ymin,
 rep_ymax,
 rep_zmin,
 rep_zmax,
 rep_volume,
 rep_cube_volume,
 (rep_density_objs::real/rep_density_ends::real) as rep_density,
 rep_density_objs,
 rep_density_ends,
 rep_density_end_ids,
 rep_primitive,
 rep_color,
 rep_delcause,
 EXTRACT(EPOCH FROM rep_entry),
 rep_openid,
 mca_id,
 rep_depth
from representation as rep

left join (
 select * from concept_data_info
) as cdi on 
 cdi.ci_id = rep.ci_id and
 cdi.cdi_id = rep.cdi_id

left join (
 select * from concept_data
) as cd on 
 cd.ci_id = rep.ci_id and
 cd.cb_id = rep.cb_id and
 cd.cdi_id = rep.cdi_id

left join (
 select * from buildup_data
) as bd on 
 bd.md_id = rep.md_id and
 bd.mv_id = rep.mv_id and
 bd.mr_id = rep.mr_id and
 bd.ci_id = rep.ci_id and
 bd.cb_id = rep.cb_id and
 bd.cdi_id = rep.cdi_id

where
 (rep.ci_id,rep.cb_id,rep.md_id,rep.mv_id,rep.mr_id,rep.bul_id,rep.cdi_id) in (
   select
    ci_id,
    cb_id,
    md_id,
    mv_id,
    max(mr_id) as mr_id,
    bul_id,
    cdi_id
   from
    view_representation
   where
    rep_delcause is null and
    ci_id=$form->{'ci_id'} and
    cb_id=$form->{'cb_id'} and
    md_id=$form->{'md_id'} and
    mv_id=$form->{'mv_id'} and
    mr_id<=$form->{'mr_id'} and
    bul_id=$form->{'bul_id'} and
    cdi_name=?
   group by
    ci_id,
    cb_id,
    md_id,
    mv_id,
    bul_id,
    cdi_id
 )
order by
 rep_serial desc
limit 1
SQL
		$sth_bp3d_fid->{$version}->{$t_type} = $dbh->prepare($sql_bp3d_fid);
#print LOG __LINE__,":\$sql_bp3d_fid=[$sql_bp3d_fid]\n";
	}

	unless(defined $sth_point){
		my $sql_point = qq|select |;
		$sql_point .= qq| p.f_pid|;
		$sql_point .= qq|,p.p_name_j|;
		$sql_point .= qq|,p.p_name_e|;
		$sql_point .= qq|,p.p_name_k|;
		$sql_point .= qq|,p.p_name_l|;
		$sql_point .= qq|,p.p_organsys_j|;
		$sql_point .= qq|,p.p_organsys_e|;
		$sql_point .= qq|,p.p_syn_j|;
		$sql_point .= qq|,p.p_syn_e|;
		$sql_point .= qq|,p.p_label|;
		$sql_point .= qq|,p.p_delcause|;
		$sql_point .= qq|,EXTRACT(EPOCH FROM p.p_entry)|;
		$sql_point .= qq|,EXTRACT(EPOCH FROM p.p_modified)|;
		$sql_point .= qq|,p.p_e_openid|;
		$sql_point .= qq|,p.p_m_openid|;
		$sql_point .= qq| from bp3d_point as p|;
		$sql_point .= qq| where p.f_id=? and p.md_id=? and p.mv_id=? and p.p_delcause is null|;
		$sth_point = $dbh->prepare($sql_point);
	}

	my($f_name_j,$f_name_e,$f_name_k,$f_name_l,$f_syn_j,$f_syn_e,$f_def_e,$f_detail_j,$f_detail_e,$f_organsys_j,$f_organsys_e,$f_phase,$f_zmin,$f_zmax,$f_volume,$f_delcause,$f_entry,$f_modified,$e_openid,$m_openid,$f_taid,$phy_name,$phy_id,$seg_name,$seg_color,$seg_thum_bgcolor,$seg_thum_bocolor,$seg_id);
	my($b_id,$b_comid,$b_name_j,$b_name_e,$b_name_k,$b_name_l,$b_syn_j,$b_syn_e,$b_def_e,$b_organsys_j,$b_organsys_e,$b_phase,$b_xmin,$b_xmax,$b_ymin,$b_ymax,$b_zmin,$b_zmax,$b_volume,$b_cube_volume,$b_density,$b_density_objs,$b_density_ends,$b_density_end_ids,$b_primitive,$b_state,$b_color,$b_delcause,$b_entry,$b_modified,$b_e_openid,$b_m_openid);
	my($p_f_pid,$p_name_j,$p_name_e,$p_name_k,$p_name_l,$p_syn_j,$p_syn_e,$p_organsys_j,$p_organsys_e,$p_label,$p_delcause,$p_entry,$p_modified,$p_e_openid,$p_m_openid);
	my $mca_id;
	my $rep_depth;

#	my($b_density_bp3d,$b_density_end_ids_bp3d,$b_density_isa,$b_density_end_ids_isa,$b_density_partof,$b_density_end_ids_partof);

#print LOG __LINE__,":\$f_id2=[$f_id2]\n";
	$sth_fma->execute($f_id2) or croak $dbh->errstr;
#print LOG __LINE__,":\$sth_fma->rows()=[",$sth_fma->rows(),"]\n";
	my $column_number = 0;
	$sth_fma->bind_col(++$column_number, \$f_name_j, undef);
	$sth_fma->bind_col(++$column_number, \$f_name_e, undef);
	$sth_fma->bind_col(++$column_number, \$f_name_k, undef);
	$sth_fma->bind_col(++$column_number, \$f_name_l, undef);
	$sth_fma->bind_col(++$column_number, \$f_syn_j, undef);
	$sth_fma->bind_col(++$column_number, \$f_syn_e, undef);
	$sth_fma->bind_col(++$column_number, \$f_def_e, undef);
	$sth_fma->bind_col(++$column_number, \$f_delcause, undef);
	$sth_fma->bind_col(++$column_number, \$f_entry, undef);
#	$sth_fma->bind_col(++$column_number, \$f_modified, undef);
	$sth_fma->bind_col(++$column_number, \$e_openid, undef);
#	$sth_fma->bind_col(++$column_number, \$m_openid, undef);
	$sth_fma->bind_col(++$column_number, \$f_taid, undef);
	$sth_fma->bind_col(++$column_number, \$phy_name, undef);
	$sth_fma->bind_col(++$column_number, \$phy_id, undef);
	$sth_fma->bind_col(++$column_number, \$seg_name, undef);
	$sth_fma->bind_col(++$column_number, \$seg_color, undef);
	$sth_fma->bind_col(++$column_number, \$seg_thum_bgcolor, undef);
	$sth_fma->bind_col(++$column_number, \$seg_thum_bocolor, undef);
	$sth_fma->bind_col(++$column_number, \$seg_id, undef);
	$sth_fma->fetch;
	$sth_fma->finish;

#print LOG __LINE__,":\$f_syn_j=[$f_syn_j]\n";

	$sth_bp3d_bid->{$version}->{$t_type}->execute($f_id) or croak $dbh->errstr;
#print LOG __LINE__,":\$sth_bp3d_bid->{$version}->{$t_type}->rows()=[",$sth_bp3d_bid->{$version}->{$t_type}->rows(),"]\n";
	if($sth_bp3d_bid->{$version}->{$t_type}->rows()>0){
		$column_number = 0;
		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_id, undef);
		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_comid, undef);
		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_name_j, undef);
		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_name_e, undef);
		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_name_k, undef);
		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_name_l, undef);
#		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_organsys_j, undef);
#		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_organsys_e, undef);
		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_syn_j, undef);
		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_syn_e, undef);
		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_def_e, undef);
#		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_phase, undef);
		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_xmin, undef);
		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_xmax, undef);
		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_ymin, undef);
		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_ymax, undef);
		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_zmin, undef);
		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_zmax, undef);
		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_volume, undef);
		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_cube_volume, undef);
		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_density, undef);
		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_density_objs, undef);
		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_density_ends, undef);
		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_density_end_ids, undef);
		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_primitive, undef);
#		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_state, undef);
		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_color, undef);
		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_delcause, undef);
		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_entry, undef);
#		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_modified, undef);
		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_e_openid, undef);
#		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_m_openid, undef);
#		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_density_bp3d, undef);
#		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_density_end_ids_bp3d, undef);
#		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_density_isa, undef);
#		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_density_end_ids_isa, undef);
#		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_density_partof, undef);
#		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$b_density_end_ids_partof, undef);
		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$mca_id, undef);
		$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$rep_depth, undef);
		$sth_bp3d_bid->{$version}->{$t_type}->fetch;
		$sth_bp3d_bid->{$version}->{$t_type}->finish;
#print LOG __LINE__,":\$b_syn_j=[$b_syn_j]\n";
	}else{
		$sth_bp3d_fid->{$version}->{$t_type}->execute($f_id2) or croak $dbh->errstr;
#print LOG __LINE__,":\$sth_bp3d_fid->{$version}->{$t_type}->rows()=[",$sth_bp3d_fid->{$version}->{$t_type}->rows(),"]\n";
		$column_number = 0;
		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_id, undef);
		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_comid, undef);
		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_name_j, undef);
		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_name_e, undef);
		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_name_k, undef);
		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_name_l, undef);
#		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_organsys_j, undef);
#		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_organsys_e, undef);
		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_syn_j, undef);
		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_syn_e, undef);
		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_def_e, undef);
#		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_phase, undef);
		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_xmin, undef);
		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_xmax, undef);
		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_ymin, undef);
		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_ymax, undef);
		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_zmin, undef);
		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_zmax, undef);
		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_volume, undef);
		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_cube_volume, undef);
		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_density, undef);
		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_density_objs, undef);
		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_density_ends, undef);
		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_density_end_ids, undef);
		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_primitive, undef);
#		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_state, undef);
		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_color, undef);
		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_delcause, undef);
		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_entry, undef);
#		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_modified, undef);
		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_e_openid, undef);
#		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_m_openid, undef);
#		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_density_bp3d, undef);
#		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_density_end_ids_bp3d, undef);
#		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_density_isa, undef);
#		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_density_end_ids_isa, undef);
#		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_density_partof, undef);
#		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$b_density_end_ids_partof, undef);
		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$mca_id, undef);
		$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$rep_depth, undef);
		$sth_bp3d_fid->{$version}->{$t_type}->fetch;
		$sth_bp3d_fid->{$version}->{$t_type}->finish;
#print LOG __LINE__,":\$b_syn_j=[$b_syn_j]\n";
	}
#print LOG __LINE__,"\$f_id=[$f_id]\n";
#print LOG __LINE__,"\$f_id2=[$f_id2]\n";
#print LOG __LINE__,"\$b_density_end_ids=[$b_density_end_ids]\n";
#print LOG __LINE__,"\$b_primitive=[$b_primitive]\n";

=pod
	if(exists($form->{'md_id'}) && exists($form->{'mv_id'})){
		$sth_point->execute($f_id2,$form->{'md_id'},$form->{'mv_id'});
		my $column_number = 0;
		$sth_point->bind_col(++$column_number, \$p_f_pid, undef);
		$sth_point->bind_col(++$column_number, \$p_name_j, undef);
		$sth_point->bind_col(++$column_number, \$p_name_e, undef);
		$sth_point->bind_col(++$column_number, \$p_name_k, undef);
		$sth_point->bind_col(++$column_number, \$p_name_l, undef);
		$sth_point->bind_col(++$column_number, \$p_organsys_j, undef);
		$sth_point->bind_col(++$column_number, \$p_organsys_e, undef);
		$sth_point->bind_col(++$column_number, \$p_syn_j, undef);
		$sth_point->bind_col(++$column_number, \$p_syn_e, undef);
		$sth_point->bind_col(++$column_number, \$p_label, undef);
		$sth_point->bind_col(++$column_number, \$p_delcause, undef);
		$sth_point->bind_col(++$column_number, \$p_entry, undef);
		$sth_point->bind_col(++$column_number, \$p_modified, undef);
		$sth_point->bind_col(++$column_number, \$p_e_openid, undef);
		$sth_point->bind_col(++$column_number, \$p_m_openid, undef);
		$sth_point->fetch;
		$sth_point->finish;
	}
=cut

	my $text;
	my $organsys;
	if(!(exists $form->{'lng'} && defined $form->{'lng'}) || $form->{'lng'} eq "ja"){
		if(defined $f_name_j || defined $b_name_j || defined $p_name_j){
#			$text = (defined $f_name_j ? $f_name_j : defined $b_name_j ? $b_name_j : $p_name_j);
			$text = (defined $b_name_j ? $b_name_j : defined $f_name_j ? $f_name_j : $p_name_j);#2011/09/30 tyamamot 和名からカナを削除する関係で、bp3dテーブルの情報を優先する
		}else{
			$text = (defined $f_name_e ? $f_name_e : defined $b_name_e ? $b_name_e : $p_name_e);
		}
		if(defined $b_organsys_j || defined $p_organsys_j){
			$organsys = (defined $b_organsys_j ? $b_organsys_j : $p_organsys_j);
		}else{
			$organsys = (defined $b_organsys_e ? $b_organsys_e : $p_organsys_e);
		}
	}else{
		$text = (defined $f_name_e ? $f_name_e : defined $b_name_e ? $b_name_e : $p_name_e);
		$organsys = defined $b_organsys_e ? $b_organsys_e : $p_organsys_e;
	}

	if(!defined $b_comid && defined $f_id && $f_id =~ /^FMA\d+$/){
		$b_comid = $f_id;
	}

	my $but_cnum = 0;
	if(defined $f_id){
		$sth_buildup_tree->{$form->{'md_id'}}->{$form->{'mv_id'}}->{$form->{'mr_id'}}->{$form->{'ci_id'}}->{$form->{'cb_id'}}->{$form->{'bul_id'}}->execute($f_id) or croak $dbh->errstr;
		$sth_buildup_tree->{$form->{'md_id'}}->{$form->{'mv_id'}}->{$form->{'mr_id'}}->{$form->{'ci_id'}}->{$form->{'cb_id'}}->{$form->{'bul_id'}}->bind_col(1, \$but_cnum, undef);
		$sth_buildup_tree->{$form->{'md_id'}}->{$form->{'mv_id'}}->{$form->{'mr_id'}}->{$form->{'ci_id'}}->{$form->{'cb_id'}}->{$form->{'bul_id'}}->fetch;
		$sth_buildup_tree->{$form->{'md_id'}}->{$form->{'mv_id'}}->{$form->{'mr_id'}}->{$form->{'ci_id'}}->{$form->{'cb_id'}}->{$form->{'bul_id'}}->finish;
	}
#print LOG __LINE__,":\$b_id=[$b_id],\$b_zmin=[$b_zmin],\$b_zmax=[$b_zmax],\$b_volume=[$b_volume],\$b_cube_volume=[$b_cube_volume]\n";

	my $icon_path = &getImagePath($f_id,'rotate',$form->{'version'},'16x16',$form->{'t_type'});

	my $rtn = {
		f_id       => $f_id,
#		b_id       => (defined $b_id ? $b_id : defined $p_f_pid ? $f_id : undef),
		b_id       => $b_id,
		common_id  => (defined $b_comid ? $b_comid : defined $p_f_pid ? $f_id : undef),
#		name_j     => (defined $f_name_j ? $f_name_j : defined $b_name_j ? $b_name_j : $p_name_j),
		name_j     => (defined $b_name_j ? $b_name_j : defined $f_name_j ? $f_name_j : $p_name_j),#2011/09/30 tyamamot 和名からカナを削除する関係で、bp3dテーブルの情報を優先する
		name_e     => (defined $f_name_e ? $f_name_e : defined $b_name_e ? $b_name_e : $p_name_e),
#		name_k     => (defined $f_name_k ? $f_name_k : defined $b_name_k ? $b_name_k : $p_name_k),#2011/09/30 tyamamot 和名からカナを削除する関係で、bp3dテーブルの情報を優先する
		name_k     => (defined $b_name_k ? $b_name_k : defined $f_name_k ? $f_name_k : $p_name_k),
		name_l     => (defined $f_name_l ? $f_name_l : defined $b_name_l ? $b_name_l : $p_name_l),
		syn_j      => (defined $f_syn_j ? $f_syn_j : defined $b_syn_j ? $b_syn_j : $p_syn_j),
		syn_e      => (defined $f_syn_e ? $f_syn_e : defined $b_syn_e ? $b_syn_e : $p_syn_e),
		def_e      => (defined $f_def_e ? $f_def_e : $b_def_e),
		organsys_j => defined $b_organsys_j ? $b_organsys_j : $p_organsys_j,
		organsys_e => defined $b_organsys_e ? $b_organsys_e : $p_organsys_e,
		text       => $text,
		name       => $text,
		organsys   => $organsys,
		phase      => $b_phase,
		xmin       => defined $b_xmin ? $b_xmin+0 : undef,
		xmax       => defined $b_xmin ? $b_xmax+0 : undef,
		ymin       => defined $b_xmin ? $b_ymin+0 : undef,
		ymax       => defined $b_xmin ? $b_ymax+0 : undef,
		zmin       => defined $b_xmin ? $b_zmin+0 : undef,
		zmax       => defined $b_xmin ? $b_zmax+0 : undef,
		volume     => defined $b_xmin ? $b_volume+0 : undef,
		cube_volume=> defined $b_xmin ? $b_cube_volume+0 : undef,
		primitive  => $b_primitive ? JSON::XS::true : JSON::XS::false,
		state      => (defined $b_state ? $b_state : undef),
		taid       => $f_taid,
		physical   => $phy_name,
		phy_id     => $phy_id,
		segment    => $seg_name,
		seg_color  => $seg_color,
		seg_thum_bgcolor=> $seg_thum_bgcolor,
		seg_thum_bocolor=> $seg_thum_bocolor,
		seg_id     => $seg_id,
		version    => defined $form->{'version_name'} ? $form->{'version_name'} : $version,
		md_id      => (exists($form->{'md_id'}) ? $form->{'md_id'}+0 : undef),
		mv_id      => (exists($form->{'mv_id'}) ? $form->{'mv_id'}+0 : undef),
		mr_id      => (exists($form->{'mr_id'}) ? $form->{'mr_id'}+0 : undef),
		ci_id      => (exists($form->{'ci_id'}) ? $form->{'ci_id'}+0 : undef),
		cb_id      => (exists($form->{'cb_id'}) ? $form->{'cb_id'} +0: undef),
		bul_id     => (exists($form->{'bul_id'}) ? $form->{'bul_id'}+0 : undef),

		mca_id     => $mca_id,
		rep_depth  => $rep_depth,

		icon       => defined $icon_path && -e $icon_path ? qq|$icon_path?|.(stat($icon_path))[9] : undef,

#		elem_type  => (defined $p_f_pid ? 'bp3d_point' : defined $b_id ? "bp3d_$version" : undef),
		elem_type  => undef,
#		point_label=> $p_label,
#		point_parent=> undef,
#		point_children=> undef,

#		def_color  => $b_color,
		color  => $seg_color,
		def_color  => $seg_color,

		but_cnum   => $but_cnum,
#		entry      => (defined $b_entry?$b_entry:$f_entry),
		entry      => defined $b_entry?$b_entry+0:undef,
		lastmod    => (defined $b_entry?$b_entry+0:$f_entry),
		delcause   => (defined $b_delcause?$b_delcause:$f_delcause),
		openid     => (defined $b_e_openid?$b_e_openid:$e_openid)
	};

	#各IDに対応する名称を取得(START)
	$rtn->{'model'} = undef;
	$rtn->{'model_version'} = undef;
	$rtn->{'concept_info'} = undef;
	$rtn->{'concept_build'} = undef;
	$rtn->{'buildup_logic'} = undef;
	if(defined $rtn->{'md_id'}){
		my $md_name;
		my $sth = $dbh->prepare(qq|select md_name_e from model where md_id=?|);
		$sth->execute($rtn->{'md_id'});
		my $column_number = 0;
		$sth->bind_col(1, \$md_name, undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;
		$rtn->{'model'} = $md_name;

		if(defined $rtn->{'mv_id'}){
			my $mv_name;
			my $sth = $dbh->prepare(qq|select mv_name_e from model_version where md_id=? and mv_id=?|);
			$sth->execute($rtn->{'md_id'},$rtn->{'mv_id'});
			my $column_number = 0;
			$sth->bind_col(1, \$mv_name, undef);
			$sth->fetch;
			$sth->finish;
			undef $sth;
			$rtn->{'model_version'} = $mv_name;
		}
	}
	if(defined $rtn->{'ci_id'}){
		my $ci_name;
		my $sth = $dbh->prepare(qq|select ci_name from concept_info where ci_id=?|);
		$sth->execute($rtn->{'ci_id'});
		my $column_number = 0;
		$sth->bind_col(1, \$ci_name, undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;
		$rtn->{'concept_info'} = $ci_name;

		if(defined $rtn->{'cb_id'}){
			my $cb_name;
			my $sth = $dbh->prepare(qq|select cb_name from concept_build where ci_id=? and cb_id=?|);
			$sth->execute($rtn->{'ci_id'},$rtn->{'cb_id'});
			my $column_number = 0;
			$sth->bind_col(1, \$cb_name, undef);
			$sth->fetch;
			$sth->finish;
			undef $sth;
			$rtn->{'concept_build'} = $cb_name;
		}
	}
	if(defined $rtn->{'bul_id'}){
		my $bul_name;
		my $sth = $dbh->prepare(qq|select bul_name_e from buildup_logic where bul_id=?|);
		$sth->execute($rtn->{'bul_id'});
		my $column_number = 0;
		$sth->bind_col(1, \$bul_name, undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;
		$rtn->{'buildup_logic'} = $bul_name;
	}
	#各IDに対応する名称を取得(END)


	#bu_idのRevisionを取得(START)
	$rtn->{bu_revision} = undef;
	if(defined $rtn->{'b_id'} && defined $rtn->{'f_id'} && defined $rtn->{'md_id'} && defined $rtn->{'mv_id'} && defined $rtn->{'mr_id'} && defined $rtn->{'ci_id'} && defined $rtn->{'cb_id'} && defined $rtn->{'bul_id'}){
		my $sql=<<SQL;
select rep_id from representation bu
left join (select ci_id,cdi_id,cdi_name from concept_data_info) cdi on cdi.ci_id=bu.ci_id and cdi.cdi_id=bu.cdi_id
where bu.md_id=? and bu.mv_id=? and bu.mr_id=? and bu.ci_id=? and bu.cb_id=? and bu.bul_id=? and cdi.cdi_name=?
SQL
		my $sth = $dbh->prepare($sql);
		$sth->execute($rtn->{'md_id'},$rtn->{'mv_id'},$rtn->{'mr_id'},$rtn->{'ci_id'},$rtn->{'cb_id'},$rtn->{'bul_id'},$rtn->{'f_id'});
		my $rows = $sth->rows();
		$sth->finish;
		undef $sth;
		$rtn->{bu_revision} = 0;
		$rtn->{bu_revision} = $rows-1 if($rows>0);
	}
	#bu_idのRevisionを取得(END)


	$rtn->{'used_parts_num'} = undef;
	$rtn->{'used_parts'} = undef;
	if(defined $b_id){
		my $sql =<<SQL;
select distinct hart.art_id,hart.hist_serial,hart.art_serial from representation as bu
left join(select * from representation_art) as buc on (buc.rep_id=bu.rep_id)
left join(select art_id,art_serial,hist_serial from history_art_file) as hart on (hart.art_id=buc.art_id and hart.hist_serial=buc.art_hist_serial)
where bu.rep_id=?
order by hart.art_serial,hart.hist_serial
SQL
		my @used_parts;
		my $art_id;
		my $art_hist_serial;
		my $sth = $dbh->prepare($sql);
		$sth->execute($b_id);
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$art_id, undef);
		$sth->bind_col(++$column_number, \$art_hist_serial, undef);
		while($sth->fetch){
			next unless(defined $art_id && defined $art_hist_serial);
			push(@used_parts,$art_id);
		}
		$sth->finish;
		undef $sth;
		if(scalar @used_parts>0){
			$rtn->{'used_parts'} = join(",",@used_parts);
			$rtn->{'used_parts_num'} = scalar @used_parts;
		}
	}


	my $max_density_ends_num = 10;

	$rtn->{'density'} = undef;
	$rtn->{'density_icon'} = undef;
	$rtn->{'density_ends'} = undef;
	$rtn->{'density_ends_num'} = undef;
	if(defined $b_density && $b_density>0){
		if($b_density<=0.5){
			$rtn->{'density_icon'} = qq|005|;
		}elsif($b_density<=0.15){
			$rtn->{'density_icon'} = qq|015|;
		}elsif($b_density<=0.25){
			$rtn->{'density_icon'} = qq|025|;
		}elsif($b_density<=0.35){
			$rtn->{'density_icon'} = qq|035|;
		}elsif($b_density<=0.45){
			$rtn->{'density_icon'} = qq|045|;
		}elsif($b_density<=0.55){
			$rtn->{'density_icon'} = qq|055|;
		}elsif($b_density<=0.65){
			$rtn->{'density_icon'} = qq|065|;
		}elsif($b_density<=0.75){
			$rtn->{'density_icon'} = qq|075|;
		}elsif($b_density<=0.85){
			$rtn->{'density_icon'} = qq|085|;
		}elsif($b_density<=0.95){
			$rtn->{'density_icon'} = qq|095|;
		}elsif($b_density<1.0){
			$rtn->{'density_icon'} = qq|099|;
		}elsif($b_density>=1){
#			$b_density = 1;
			if($b_primitive){
				$rtn->{'density_icon'} = qq|primitive|;
			}else{
				$rtn->{'density_icon'} = qq|100|;
			}
		}
		$rtn->{'density'} = int($b_density*10000)/100;
	}
#print LOG __LINE__,"\$b_density_end_ids=[$b_density_end_ids]\n";
	if(defined $b_density_end_ids){
		my $end_ids = $JSONXS->decode($b_density_end_ids);
		$rtn->{'density_ends_num'} = scalar @$end_ids;
		if($rtn->{'density_ends_num'}<=$max_density_ends_num){
#			my $md_abbr = defined $form->{'md_abbr'} ? $form->{'md_abbr'} : 'bp3d';
#			my $obj_path = qq|obj/$md_abbr/$form->{'version'}|;

			my $sth = $dbh->prepare(qq|select cdi_name from concept_data_info where ci_id=? and cdi_id=?|);

#			my $sth_primitive = $dbh->prepare(qq|select rep_primitive from view_representation where ci_id=? and cb_id=? and cdi_id=? and md_id=? and mv_id=? and mr_id=? and bul_id=? and rep_primitive|);
			my $sth_primitive = $dbh->prepare(qq|select rep_primitive from representation where ci_id=? and cb_id=? and cdi_id=? and md_id=? and mv_id=? and mr_id<=? and bul_id=? and rep_primitive and rep_delcause is null|);

			foreach my $cdi_id (@$end_ids){
				my $objid;
				$sth->execute($form->{'ci_id'},$cdi_id);
				my $column_number = 0;
				$sth->bind_col(++$column_number, \$objid, undef);
				$sth->fetch;
				$sth->finish;

				$sth_primitive->execute($form->{'ci_id'},$form->{'cb_id'},$cdi_id,$form->{'md_id'},$form->{'mv_id'},$form->{'mr_id'},$form->{'bul_id'});
				my $rep_primitive = $sth_primitive->rows();
				$sth_primitive->finish;

#				my $path = qq|$obj_path/$objid.obj|;
#				print LOG __LINE__,"\$path=[$path]\n";
				my $obj_hash = {
					f_id => $objid,
#					path => -e $path ? $path : undef
					path => undef,
#					primitive => -e $path ? JSON::XS::true : JSON::XS::false
					primitive => $rep_primitive>0 ? JSON::XS::true : JSON::XS::false
				};

				my $path = &getImagePath($objid,$form->{'position'},$form->{'version'},'40x40',$form->{'t_type'});
				$path = &getImagePath($objid,$form->{'position'},$form->{'version'},'120x120',$form->{'t_type'}) unless(defined $path && -e $path);

				if(defined $path && -e $path){
					my $mtime = (stat($path))[9];
					$obj_hash->{path} = qq|$path?$mtime|;
				}

				my $obji2 = $objid;
				$obji2 =~ s/\D+$//g;

				my $obj_f_name_j;
				my $obj_f_name_e;
				my $obj_b_id;
				my $obj_b_comid;
				my $obj_b_name_j;
				my $obj_b_name_e;
				$sth_fma->execute($obji2);
				$column_number = 0;
				$sth_fma->bind_col(++$column_number, \$obj_f_name_j, undef);
				$sth_fma->bind_col(++$column_number, \$obj_f_name_e, undef);
				$sth_fma->fetch;
				$sth_fma->finish;

				$sth_bp3d_bid->{$version}->{$t_type}->execute($objid);
				if($sth_bp3d_bid->{$version}->{$t_type}->rows()>0){
					$column_number = 0;
					$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$obj_b_id, undef);
					$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$obj_b_comid, undef);
					$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$obj_b_name_j, undef);
					$sth_bp3d_bid->{$version}->{$t_type}->bind_col(++$column_number, \$obj_b_name_e, undef);
					$sth_bp3d_bid->{$version}->{$t_type}->fetch;
					$sth_bp3d_bid->{$version}->{$t_type}->finish;
				}else{
					$sth_bp3d_fid->{$version}->{$t_type}->execute($obji2);
					$column_number = 0;
					$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$obj_b_id, undef);
					$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$obj_b_comid, undef);
					$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$obj_b_name_j, undef);
					$sth_bp3d_fid->{$version}->{$t_type}->bind_col(++$column_number, \$obj_b_name_e, undef);
					$sth_bp3d_fid->{$version}->{$t_type}->fetch;
					$sth_bp3d_fid->{$version}->{$t_type}->finish;
				}

				$obj_hash->{'b_id'} = $obj_b_id;
				$obj_hash->{'name'} = defined $form->{'lng'} && $form->{'lng'} eq 'ja' && defined $obj_f_name_j ? $obj_f_name_j : (defined $obj_b_name_j ? $obj_b_name_j : $obj_f_name_e);
				$obj_hash->{'name'} = &Encode::decode_utf8($obj_hash->{'name'}) unless(&Encode::is_utf8($obj_hash->{'name'}));
				push(@{$rtn->{'density_ends'}},$obj_hash);
			}
			undef $sth;
			undef $sth_primitive;

			@{$rtn->{'density_ends'}} = sort {
				if($a->{'primitive'} == $b->{'primitive'}){
					$a->{'f_id'} cmp $b->{'f_id'};
				}elsif($a->{'primitive'}){
					-1;
				}elsif($b->{'primitive'}){
					1;
				}else{
					0;
				}
			} @{$rtn->{'density_ends'}};
			my $no = 0;
			foreach my $ends (@{$rtn->{'density_ends'}}){
				$ends->{'no'} = ++$no;
			}
		}else{
			$rtn->{'density_ends'} = sprintf(qq|too many children (%d)|,$rtn->{'density_ends_num'});
		}
	}

	$rtn->{'tweets'} = undef;
	$rtn->{'tweet_num'} = 0;
	if(defined $b_id){
		$Twitter = new AG::ComDB::Twitter unless(defined $Twitter);
		if(exists $rtn->{'mca_id'} && defined $rtn->{'mca_id'}){
			my $mca_id = $rtn->{'mca_id'};
			my $rep_id;
			my @REP_IDS;
			my $sql = qq|select rep_id from representation where rep_delcause is null AND mca_id=? group by rep_id|;
			my $sth = $dbh->prepare($sql) or croak $dbh->errstr;
			$sth->execute($mca_id) or croak $dbh->errstr;
			my $column_number = 0;
			$sth->bind_col(++$column_number, \$rep_id, undef);
			while($sth->fetch){
				push(@REP_IDS,$rep_id) if(defined $rep_id);
			}
			$sth->finish;
			undef $sth;
			if(scalar @REP_IDS){
				$rtn->{'tweets'} = $Twitter->get_tweets(\@REP_IDS);
				$rtn->{'tweet_num'} = scalar @{$rtn->{'tweets'}} if(defined $rtn->{'tweets'});
			}
			undef @REP_IDS;
		}else{
			$rtn->{'tweets'} = $Twitter->get_tweets($b_id);
			$rtn->{'tweet_num'} = scalar @{$rtn->{'tweets'}} if(defined $rtn->{'tweets'});
		}
	}

	my $txt_file;
	my $path = defined $rtn->{'b_id'} ? &getImagePath($f_id,$form->{'position'},$form->{'version'},'120x120',$form->{'t_type'}) : undef;
	print $LOG __LINE__.":\$path=[$path][".(-e $path?1:0)."]\n" if(defined $path && defined $LOG);
	unless(defined $path && -e $path && -s $path){
		$path = &getImagePath($f_id,$form->{'position'},$form->{'version'},'120x120',$form->{'t_type'});
		print $LOG __LINE__.":\$path=[$path][".(-e $path?1:0)."]\n" if(defined $path && defined $LOG);
	}
#	unless(defined $path && -e $path && -s $path){
#		$path = &getImagePath($f_id,$form->{'position'},$form->{'version'},'120x120',$form->{'t_type'}==3 ? 4 : 3);
#		print $LOG __LINE__.":\$path=[$path][".(-e $path?1:0)."]\n" if(defined $path && defined $LOG);
#	}

	if(defined $path && -e $path){
		my $mtime = (stat($path))[9];
		$rtn->{'src'} = $path . "?$mtime";
	}else{
		$rtn->{'src'} = "resources/images/default/s.gif";
	}

	if(defined $p_f_pid){
		push(@{$rtn->{point_parent}},&getFMA($dbh,$form,$p_f_pid));
	}else{
	}

	my $CACHE;
	if(open($CACHE,qq|> $cache_file|)){
		flock($CACHE,2);
		print $CACHE $JSONXS->encode($rtn);
		close($CACHE);
		chmod 0666,$cache_file;
	}
	umask($old_umask);

	return $rtn;
}


sub convVersionName2RendererVersion($$$) {
	my $dbh = shift;
	my $form = shift;
	my $cookie = shift;

	$form->{'md_id'} = $cookie->{'ag_annotation.images.md_id'} if(!exists($form->{'md_id'}) && exists($cookie->{'ag_annotation.images.md_id'}));
	$form->{'version'} = $form->{'v'} if(!exists($form->{'version'}) && exists($form->{'v'}));

#print LOG __LINE__,":\$form->{'md_id'}=[$form->{'md_id'}]\n";
#print LOG __LINE__,":\$form->{'version'}=[$form->{'version'}]\n";

	if(exists($form->{'version'})){
		my $md_id;
		my $mv_id;
		my $mr_id;
		my $mv_version;
		my $md_abbr;
		my $sql =<<SQL;
select
 mr.md_id,
 mr.mv_id,
 mr_version,
 md_abbr,
 mr.mr_id
from
 model_revision as mr 
left join (
  select md_id,md_abbr from model
 ) as md on mr.md_id=md.md_id
left join (
  select md_id,mv_id,mv_name_e,mv_name_j,mv_order from model_version
 ) as mv on mr.md_id=mv.md_id and mr.mv_id=mv.mv_id

where 
SQL
		my $sth_model_version;
		if(exists($form->{'md_id'})){
			my @bind_values = ();
			$sql .= qq|mr.md_id=? and |;
			push(@bind_values,$form->{'md_id'});
			if(exists($form->{'lng'}) && $form->{'lng'} eq 'ja'){
				$sql .= qq|COALESCE(mv_name_j,mv_name_e)=?|;
			}else{
				$sql .= qq|mv_name_e=?|;
			}
			push(@bind_values,$form->{'version'});

			if(exists($form->{'mv_id'})){
				$sql .= qq| and mr.mv_id=?|;
				push(@bind_values,$form->{'mv_id'});
			}
			if(exists($form->{'mr_id'})){
				$sql .= qq| and mr.mr_id=?|;
				push(@bind_values,$form->{'mr_id'});
			}
			$sql .= qq| order by mr_order,mv_order|;

			$sth_model_version = $dbh->prepare($sql);
			$sth_model_version->execute(@bind_values);
		}else{
			if(exists($form->{'lng'}) && $form->{'lng'} eq 'ja'){
				$sql .= qq|COALESCE(mv_name_j,mv_name_e)=?|;
			}else{
				$sql .= qq|mv_name_e=?|;
			}
			$sql .= qq| order by mr_order,mv_order|;
			$sth_model_version = $dbh->prepare($sql);
			$sth_model_version->execute($form->{'version'});
		}
		my $column_number = 0;
		$sth_model_version->bind_col(++$column_number, \$md_id, undef);
		$sth_model_version->bind_col(++$column_number, \$mv_id, undef);
		$sth_model_version->bind_col(++$column_number, \$mv_version, undef);
		$sth_model_version->bind_col(++$column_number, \$md_abbr, undef);
		$sth_model_version->bind_col(++$column_number, \$mr_id, undef);
		$sth_model_version->fetch;
		if(defined $md_id && defined $mv_id && defined $mr_id && defined $mv_version){
			$form->{'md_id'} = $md_id;
			$form->{'mv_id'} = $mv_id;
			$form->{'mr_id'} = $mr_id;
			$form->{'version_name'} = $form->{'version'} if(exists($form->{'version'}));
			$form->{'version'} = $mv_version;
			$form->{'md_abbr'} = $md_abbr if(defined $md_abbr);
			$form->{'v'} = $mv_version if(exists($form->{'v'}));
		}
		$sth_model_version->finish;
		undef $sth_model_version;
	}

#print LOG __LINE__,":\$form->{'version'}=[$form->{'version'}]\n";

	return $form->{'version'};
}

sub convRendererVersion2VersionName($$) {
	my $dbh = shift;
	my $form = shift;
#	my $cookie = shift;

#print LOG __LINE__,":\$form->{'md_id'}=[$form->{'md_id'}]\n";
#print LOG __LINE__,":\$form->{'version'}=[$form->{'version'}]\n";

	if(exists($form->{'version'})){
		my $md_id;
		my $mv_id;
		my $mr_id;
		my $mv_name;
		my $sql = qq|select mr.md_id,mr.mv_id,mr_id|;
		if(exists($form->{'lng'}) && $form->{'lng'} eq 'ja'){
			$sql .= qq|COALESCE(mv_name_j,mv_name_e)|;
		}else{
			$sql .= qq|mv_name_e|;
		}
		$sql .= qq| from model_revision as mr left join (select md_id,mv_id,mv_name_e,mv_name_j from model_version) mv on mv.md_id=mr.md_id and mv.mv_id=mr.mv_id|;
		$sql .= qq| where mr_version=?|;

		my $sth_model_version;
		$sth_model_version = $dbh->prepare($sql);
		$sth_model_version->execute($form->{'version'});

		my $column_number = 0;
		$sth_model_version->bind_col(++$column_number, \$md_id, undef);
		$sth_model_version->bind_col(++$column_number, \$mv_id, undef);
		$sth_model_version->bind_col(++$column_number, \$mr_id, undef);
		$sth_model_version->bind_col(++$column_number, \$mv_name, undef);
		$sth_model_version->fetch;
		if(defined $md_id && defined $mv_id && defined $mv_name){
			$form->{'md_id'} = $md_id;
			$form->{'mv_id'} = $mv_id;
			$form->{'mr_id'} = $mr_id;
			$form->{'version_renderer'} = $form->{'version'};
			$form->{'version'} = $mv_name;
		}
		$sth_model_version->finish;
		undef $sth_model_version;
	}

#print LOG __LINE__,":\$form->{'version'}=[$form->{'version'}]\n";

	return $form->{'version'};
}

###############################################################################

sub isIPHONE {
#Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16
#Mozilla/5.0 (iPod; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16
#Mozilla/5.0 (iPhone; U; CPU iPhone OS 2_2_1 like Mac OS X; en-us) AppleWebKit/525.18.1 (KHTML, like Gecko) Version/3.1.1 Mobile/5H11 Safari/525.20
#Mozilla/5.0 (iPod; U; CPU iPhone OS 2_2_1 like Mac OS X; en-us) AppleWebKit/525.18.1 (KHTML, like Gecko) Version/3.1.1 Mobile/5H11 Safari/525.20
#Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/4A102 Safari/419.3
#Mozilla/5.0 (iPod; U; CPU like Mac OS X; en) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/4A102 Safari/419.3
	if(exists $ENV{HTTP_USER_AGENT} && defined $ENV{HTTP_USER_AGENT} && $ENV{HTTP_USER_AGENT} =~ /^Mozilla\/5\.0\s\((iPhone|iPod);\s*U;\s(CPU\s*[^;]+);[^\)]+\)/){
		return 1;
#	}elsif($ENV{HTTP_USER_AGENT} =~ /KHTML/ && $ENV{HTTP_USER_AGENT} !~ /Chrome/){
#		return 1;
	}else{
		return 0;
	}
}

sub isIPAD {
#Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16
#Mozilla/5.0 (iPod; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16
#Mozilla/5.0 (iPhone; U; CPU iPhone OS 2_2_1 like Mac OS X; en-us) AppleWebKit/525.18.1 (KHTML, like Gecko) Version/3.1.1 Mobile/5H11 Safari/525.20
#Mozilla/5.0 (iPod; U; CPU iPhone OS 2_2_1 like Mac OS X; en-us) AppleWebKit/525.18.1 (KHTML, like Gecko) Version/3.1.1 Mobile/5H11 Safari/525.20
#Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/4A102 Safari/419.3
#Mozilla/5.0 (iPod; U; CPU like Mac OS X; en) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/4A102 Safari/419.3
	if(exists $ENV{HTTP_USER_AGENT} && defined $ENV{HTTP_USER_AGENT} && $ENV{HTTP_USER_AGENT} =~ /^Mozilla\/5\.0\s\(iPad;\s*U;\s(CPU\s*[^;]+);[^\)]+\)/){
		return 1;
#	}elsif($ENV{HTTP_USER_AGENT} =~ /KHTML/ && $ENV{HTTP_USER_AGENT} !~ /Chrome/){
#		return 1;
	}else{
		return 0;
	}
}

sub isCrawler {
	if(exists $ENV{HTTP_USER_AGENT} && defined $ENV{HTTP_USER_AGENT} && $ENV{HTTP_USER_AGENT} =~ /(Googlebot|Crawler|bingbot|msnbot|Twitterbot|TweetmemeBot|UnwindFetchor|TwitterIrcGateway|Crowsnest|Yeti|SemrushBot|AhrefsBot)/i){
#	if($ENV{HTTP_USER_AGENT} =~ /(Crawler|bingbot|Twitterbot|TweetmemeBot|UnwindFetchor|TwitterIrcGateway|Crowsnest|Yeti|SemrushBot|AhrefsBot)/i){
		return 1;
	}else{
		return 0;
	}
}

sub useGZip {
	my $usegzip;
	if(exists $ENV{'HTTP_ACCEPT_ENCODING'} && defined $ENV{'HTTP_ACCEPT_ENCODING'}){
		foreach my $enc (split(/\s*,\s*/,$ENV{'HTTP_ACCEPT_ENCODING'})){
			$enc =~ s/;.*$//s;
			next unless($enc =~ /^(x-)?gzip$/);
			$usegzip = $enc;
			last;
		}
	}
	return $usegzip;
}

sub gzip_json {
	my $DATAS = shift;
	my $contentType = shift;
	$contentType = 'text/html' unless(defined $contentType && length $contentType);
	my $usegzip = &useGZip();
	print qq|Content-Encoding: $usegzip\n| if(defined $usegzip);
	print qq|Content-type: $contentType; charset=UTF-8\n\n|;
	my $content = $JSONXS->encode($DATAS);
	$content= &Compress::Zlib::memGzip($content) if(defined $usegzip);
	print $content;
}

###############################################################################
sub getParams {
	my $query = shift;
	my $PARAMS = shift || {};
	my $cookie = shift;

#	$query->autoEscape(0);
#	$query->charset('utf-8');

	my @params = $query->param();
	foreach my $param (@params){
		next if(exists $PARAMS->{$param} && defined $PARAMS->{$param});
		if(defined $query->param($param)){
			my @P = $query->param($param);
			if(scalar @P > 1){
				$PARAMS->{$param} = [];
				push(@{$PARAMS->{$param}},@P);
			}else{
				$PARAMS->{$param} = $P[0];
			}
		}else{
			$PARAMS->{$param} = undef;
		}
		if(defined $PARAMS->{$param}){
			if(ref $PARAMS->{$param} eq 'ARRAY' && scalar @{$PARAMS->{$param}} == 0){
				$PARAMS->{$param} = undef;
			}elsif(length($PARAMS->{$param})==0){
				$PARAMS->{$param} = undef;
			}
		}
	}
	my @url_params = $query->url_param();
	foreach my $url_param (@url_params){
		next unless(defined $url_param && length $url_param);
		next if(exists $PARAMS->{$url_param} && defined $PARAMS->{$url_param});
		if(defined $query->url_param($url_param)){
			my @P = $query->url_param($url_param);
			if(scalar @P > 1){
				$PARAMS->{$url_param} = [];
				push(@{$PARAMS->{$url_param}},@P);
			}else{
				$PARAMS->{$url_param} = $P[0];
			}
		}else{
			$PARAMS->{$url_param} = undef;
		}
		if(defined $PARAMS->{$url_param}){
			if(ref $PARAMS->{$url_param} eq 'ARRAY' && scalar $PARAMS->{$url_param} == 0){
				$PARAMS->{$url_param} = undef 
			}elsif(length($PARAMS->{$url_param})==0){
				$PARAMS->{$url_param} = undef 
			}
		}
	}
	my @cookie_params = $query->cookie();
	foreach my $cookie_param (@cookie_params){
		if(defined $cookie){
			$cookie->{$cookie_param} = defined $query->cookie($cookie_param) ? $query->cookie($cookie_param) : undef;
		}else{
			next unless($cookie_param =~ /^ag_annotation/);

			my $param = $cookie_param;
			$param =~ s/^ag_annotation\.images\.//;
			$param =~ s/^ag_annotation\.//;

			next if(exists $PARAMS->{$param} && defined $PARAMS->{$param});
			$PARAMS->{$param} = defined $query->cookie($cookie_param) ? $query->cookie($cookie_param) : undef;
			unless(defined $PARAMS->{$param}){
				delete $PARAMS->{$param};
				next;
			}elsif(defined $PARAMS->{$param} && length($PARAMS->{$param})==0){
				delete $PARAMS->{$param};
				next;
			}
			$PARAMS->{$cookie_param} = $PARAMS->{$param};
		}
	}
	return $PARAMS;
}
=pod
sub mkpath {
	my $path = shift;
	my $m = umask();
	umask(0);
	&File::Path::mkpath($path,0,0777);
	umask($m);
}
=cut

1;
