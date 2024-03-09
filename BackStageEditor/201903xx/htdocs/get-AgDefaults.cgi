#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use File::Spec;
use Time::HiRes;
my $t0 = [&Time::HiRes::gettimeofday()];

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
require "webgl_common.pl";
use cgi_lib::common;

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);
my($log_file,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);
my($epocsec,$microsec) = &Time::HiRes::gettimeofday();
my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);
$log_file .=  sprintf(".%02d%02d%02d.%05d",$hour,$min,$sec,$$);

open(my $LOG,">> $log_file");
select($LOG);
$| = 1;
select(STDOUT);


my $sql=<<SQL;
select md_id,md_name_e,md_abbr from model where md_use order by md_order limit 1
SQL
my $sth = $dbh->prepare($sql) or die $dbh->errstr;
$sth->execute() or die $dbh->errstr;
my($md_id,$md_name_e,$md_abbr,$def_md_id);
my $column_number = 0;
$sth->bind_col(++$column_number, \$md_id, undef);
$sth->bind_col(++$column_number, \$md_name_e, undef);
$sth->bind_col(++$column_number, \$md_abbr, undef);
$sth->fetch;
$sth->finish;
undef $sth;
$def_md_id = $md_id unless(defined $def_md_id);

&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

my $sql=<<SQL;
select prefix_id,prefix_char from id_prefix where prefix_delcause is null and prefix_id not in (2,3,4) order by prefix_id desc
SQL
my $sth = $dbh->prepare($sql) or die $dbh->errstr;
$sth->execute() or die $dbh->errstr;
my($prefix_id,$prefix_char,$def_prefix_id,$def_prefix_char);
my $PREFIX_DATAS = {
	datas => []
};
my $column_number = 0;
$sth->bind_col(++$column_number, \$prefix_id, undef);
$sth->bind_col(++$column_number, \$prefix_char, undef);
while($sth->fetch){
	push(@{$PREFIX_DATAS->{'datas'}},{
		value => $prefix_id,
		display => $prefix_char,
		prefix_id => $prefix_id,
		prefix_char => $prefix_char
	});
	$def_prefix_id = $prefix_id unless(defined $def_prefix_id);
	$def_prefix_char = $prefix_char unless(defined $def_prefix_char);
}
$sth->finish;
undef $sth;

&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

my $DEF_PREFIX_DATAS = &cgi_lib::common::encodeJSON($PREFIX_DATAS);

&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

$dbh->do('update concept_build set cb_order=max_cb_id-cb_id+1 from (select ci_id,max(cb_id) as max_cb_id from concept_build group by ci_id) as cb where concept_build.ci_id=cb.ci_id and cb_order is null;') or die $dbh->errstr;
&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

my $sql=<<SQL;
select distinct
 but.ci_id,
 ci_name,
 but.cb_id,
 cb_name,
 but.bul_id,
 bul_name_e as bul_name,
 bul_abbr,
 ci_order,
 cb_order,
 bul_order
from
 (select ci_id,cb_id,bul_id from concept_tree group by ci_id,cb_id,bul_id) as but,
 concept_info as ci,
 concept_build as cb,
 buildup_logic as bul
where
 but.ci_id=ci.ci_id and
 ci.ci_use and
 but.ci_id=cb.ci_id and
 but.cb_id=cb.cb_id and
 cb.cb_use and
 but.bul_id=bul.bul_id and
 bul_use
order by
 ci_order,
 cb_order,
 bul_order
limit 1
SQL
my $sth = $dbh->prepare($sql) or die $dbh->errstr;
$sth->execute() or die $dbh->errstr;
my($ci_id,$cb_id,$bul_id,$ci_name,$cb_name,$bul_name,$bul_abbr);
my $column_number = 0;
$sth->bind_col(++$column_number, \$ci_id, undef);
$sth->bind_col(++$column_number, \$ci_name, undef);
$sth->bind_col(++$column_number, \$cb_id, undef);
$sth->bind_col(++$column_number, \$cb_name, undef);
$sth->bind_col(++$column_number, \$bul_id, undef);
$sth->bind_col(++$column_number, \$bul_name, undef);
$sth->bind_col(++$column_number, \$bul_abbr, undef);
$sth->fetch;
$sth->finish;
undef $sth;

&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

my $sql=<<SQL;
select * from (
select
 mr.md_id,
 mr.mv_id,
 mr.mr_id,
 mr.mr_version,
 md_abbr,
 mv_name_e,
 mv_publish
from
 model_revision as mr
left join (
  select * from model
 ) as md on md.md_id=mr.md_id
left join (
  select * from model_version
 ) as mv on mv.md_id=mr.md_id and mv.mv_id=mr.mv_id
where
 md.md_use and
 mv.mv_use and
 (mr.md_id,mr.mv_id,mr.mr_id) in (
   select
    md_id,
    mv_id,
    max(mr_id) as mr_id
   from
    model_revision
   where
    mr_use
   group by
    md_id,
    mv_id
 )
order by
 md_order,
 mv_order,
 mr_order
) as a
where
 md_id=$md_id
limit 1
SQL
my $sth = $dbh->prepare($sql) or die $dbh->errstr;
$sth->execute() or die $dbh->errstr;
my($md_id,$mv_id,$mr_id,$mr_version,$md_abbr,$mv_name_e);
my $column_number = 0;
$sth->bind_col(++$column_number, \$md_id, undef);
$sth->bind_col(++$column_number, \$mv_id, undef);
$sth->bind_col(++$column_number, \$mr_id, undef);
$sth->bind_col(++$column_number, \$mr_version, undef);
$sth->bind_col(++$column_number, \$md_abbr, undef);
$sth->bind_col(++$column_number, \$mv_name_e, undef);
$sth->fetch;
$sth->finish;
undef $sth;

&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

my $DEF_IMG_BASE_URL = qq|http://lifesciencedb.jp/bp3d/|;
if(defined $ENV{'HTTP_X_FORWARDED_HOST'}){
	if($ENV{'HTTP_X_FORWARDED_HOST'} =~ /^lifesciencedb\.jp:32888/){
		$DEF_IMG_BASE_URL = qq|http://lifesciencedb.jp:32888/bp3d-38321/|;
	}elsif($ENV{'HTTP_X_FORWARDED_HOST'} =~ /^221\.186\.138\.155/){
		$DEF_IMG_BASE_URL = qq|http://221.186.138.155/bp3d-38321/|;
	}
}else{
	$DEF_IMG_BASE_URL = qq|http://192.168.1.237/bp3d-38321/|;
}

my $js_src =<<HTML;
var AgDef = {
	LOCALDB_PREFIX: '160418-backstageeditor-'
//	LOCALDB_PREFIX: '151228-'
//	LOCALDB_PREFIX: '150812-'
//	LOCALDB_PREFIX: '130725-'
//	LOCALDB_PREFIX: '130801-'
};

var DEF_VALUES = {
	md_id : $md_id,
	mv_id : $mv_id,
	mr_id : $mr_id,
	ci_id : $ci_id,
	cb_id : $cb_id,
	bul_id : $bul_id
};

var DEF_UPLOAD_FILE_MAX_SIZE = 2147483648;//2GB

var DEF_COLOR = '#F0D2A0';
var DEF_COLOR_HEX = 0xF0D2A0;

var DEF_MODEL = '$md_abbr';
var DEF_MODEL_ID = $def_md_id;
var DEF_VERSION = '$mv_name_e';

var DEF_PREFIX = '$def_prefix_char';
var DEF_PREFIX_ID = $def_prefix_id;


var DEF_CONCEPT_INFO = '$ci_name';
var DEF_CONCEPT_BUILD = '$cb_name';
var DEF_TREE = '$bul_abbr';

var DEF_AG_DATA = 'obj/$md_abbr/$mv_name_e';
//var DEF_TREE = DEF_MODEL+'-'+DEF_TREE;

var DEF_VERSION_COMBO = DEF_MODEL+'-'+DEF_VERSION;
var DEF_TREE_COMBO = DEF_MODEL+'-'+DEF_TREE;

var DEF_COORDINATESYSTEM = 'bp3d';

var DEF_MODEL_DATAS = {datas: [{
	display: '$md_name_e',
	value:   '$md_abbr',
	md_id:   $md_id,
	md_abbr: '$md_abbr'
}]};
var DEF_PREFIX_DATAS = $DEF_PREFIX_DATAS;

var DEF_UPLOAD_FILE_PAGE_SIZE = 25;
var DEF_PARTS_GRID_PAGE_SIZE = 50;
var DEF_FMA_SEARCH_GRID_PAGE_SIZE = 50;
var DEF_ERROR_TWITTER_GRID_PAGE_SIZE = 25;
var DEF_FIND_FILE_PAGE_SIZE = 10;
var DEF_PICK_SEAECH_MAX_RANGE = 20;
//var DEF_IMG_BASE_URL = 'http://lifesciencedb.jp/bp3d/';
//var DEF_IMG_BASE_URL = 'http://221.186.138.155/bp3d-38321/';
var DEF_IMG_BASE_URL = '$DEF_IMG_BASE_URL';

//var bp3d_lng = {
var AgLang = {
//	version : 'Version',
	version : 'Font set',
	revision: 'Revision',
//	version_signage : 'Version表記',
	version_signage : 'Font set表記',

	objects_set : 'Objects set',
	objects_set_signage : 'Objects set表記',

//	group_version : 'Group / Version',
	group_version : 'Group / Font set',

	tree : 'Tree',
	model : 'Model',
	prefix : 'Prefix',

	rep_list : 'Representation List',
//	rep_id : 'Representation',
	rep_id : 'BPID',
	rep_density : 'Model / Concept density',
	rep_primitive : 'Representation method',
//	cdi_name : 'Represented concept',
	cdi_name : 'FMAID',
	cdi_names : 'FMAID(s)',
//	art_id : 'Model component',
	art_id : 'FJID',
	art_ids : 'FJID(s)',
	mca_id : 'MAPID',

	cdi_name_j : 'Japanese',
	cdi_name_e : 'Name',
	cdi_name_k : 'Kana',
	cdi_name_l : 'Latina',

	cdi_syn_e : 'Synonym',
	cdi_syn_j : 'Synonym(Jpn)',

	ok   : 'OK',
	save   : 'Save',
	cancel : 'Cancel',
	close  : 'Close',

	history    : 'History',
	hist_event : 'Operation',
	user : 'User',

	comment    : 'Comment',
	class_name : 'Class',
	category   : 'Category',
	judge      : 'Judge',
	file_name  : 'Filename',
	file_size  : 'Size',

	group : 'Group Name',

	arto_id : 'Org.FJID',
	arto_filename : 'Org.Filename',
	artog_name : 'Org.Group Name',

	xmin   : 'XMin(mm)',
	xmax   : 'XMax(mm)',
	xcenter: 'XCenter(mm)',
	ymin   : 'YMin(mm)',
	ymax   : 'YMax(mm)',
	ycenter: 'YCenter(mm)',
	zmin   : 'ZMin(mm)',
	zmax   : 'ZMax(mm)',
	zcenter: 'ZCenter(mm)',
	volume : 'Volume(cm<sup>3</sup>)',
	timestamp: 'Timestamp',
	modified: 'Modified',

	pick_search: 'Neighbor Search',
	voxel_range: 'Voxel Range(mm<sup>3</sup>)',
	volume_find: 'Search Upload Parts',
	tree_find: 'Find Tree',
	parts_find: 'Select Parts',
	parts_mirroring_find: 'Select Mirroring Parts',
	parts_org_find: 'Select Orginal Parts',
	approximate_volume: 'Approximate value of the volume(cm<sup>3</sup>)',
	distance_xyz: 'Distance CenterXYZ(mm)',
	distance_voxel: 'Distance(mm)',
	collision_detection: 'Collision detection',
	diff_volume: 'Diff Vol(cm<sup>3</sup>)',
	diff_cube_volume: 'Diff Cube Vol(cm<sup>3</sup>)',
	collision_rate: 'Intersection(%)',

	publish : '公開',
	publish_label: '公開する',
	publish_state: '<b style="color:red;">公開</b>',
	'private' : '非公開',
	port : 'Port',
	order : 'Order',
	renderer : 'Renderer',
	renderer_mng : 'レンダラーサーバ管理',
	renderer_version : 'Renderer version',

	add : 'Add',
	remove : 'Delete',
	merge : 'Merge',

	edit : '編集',
	editable : '編集可',
	not_editable : '編集不可',
	not_editable_label : '編集不可にする',
	not_editable_state : '<b style="color:red;">編集不可</b>',

	use : 'Use',
	ip : 'IP',

	copy: 'Copy',
	file_info: 'FMA mapping',
	filter: 'Filter',

	seg_color: 'Color',	//パーツパレット登録時のデフォルト色
	seg_color_full: 'Pallet color',	//パーツパレット登録時のデフォルト色
	seg_thum_fgcolor: 'Thum(fg)',	//サムネイルイメージ作成時の色
	seg_thum_fgcolor_full: 'Thumbnail Image color',	//サムネイルイメージ作成時の色
	seg_thum_bgcolor: 'Thum(bg)',	//サムネイル背景色
	seg_thum_bgcolor_full: 'Thumbnail Background color',	//サムネイル背景色
	properties : 'Color property',
	seg_name: 'Segment',
	segment_color: 'Segment Color',	//セグメントカラー
	segment_color_mng: 'Segment Color 管理',	//セグメントカラー管理
	set_segment_recursively: 'Set segment recursively',	//再帰的にセグメントを設定
	thumbnail_background_part: 'Thumbnail Background Part',	//サムネイル背景パーツ

	save : '保存',
	cancel : '取消',
	reset : 'リセット',
	close  : '閉じる',

	'export' : 'Export',
	'import' : 'Import',
	'import_confirm' : 'インポートした内容でデータベースを更新します。よろしいですか？',

//	fma_edit_list: 'ALL FMA List',
	all_fma_list: 'ALL FMA List',
	all_upload_parts_list: 'ALL Upload Parts List',
	format_html : 'HTML形式',
	format_excel_xlsx : 'Excel形式(.xlsx)',
	format_excel : 'Excel(97-2003)形式(.xls)',
	format_tsv : 'タブ区切り形式',
	format_zip : 'マッピング情報',

	subclass_list: 'Subclass List',

	concept_mng : 'Concept管理',
	build_signage : 'Build表記',

	dataset_mng : 'データセット管理',

	recalculation : '再計算',
	recalculation_force : '強制的に再計算',
	error_recalculation_is_publish : '公開中の為、再計算できません',

	error_twitter: 'Twitterエラーレポート管理',
	error_file_size: 'ファイルサイズが{0}を超えています',
	error_folder_find: '「{0}」は「{1}」上に存在しません',
	error_twitter_fix_title: 'Error Report Fix',
	error_save: '保存に失敗しました',
	error_delete: '削除に失敗しました',

	error_arto_id: 'オリジナルのFJIDを指定して下さい',
	error_cdi_name: '指定されたFMAIDは存在しません',
	error_port : 'Renderer Port番号を指定して下さい',

	window_alignment : 'ウィンドウ整列',
	fma_corresponding_change : 'FMA対応変更',
	fma_corresponding_change_mode : 'FMA対応変更モード',
	fma_corresponding_change_dialog_message : 'FMA対応情報を指定してください。',
	fma_corresponding_change_dialog_error_message : 'FMA対応情報を解析できません',
	conflict_list : 'Conflict list'
};
HTML

print qq|Content-type: text/javascript; charset=UTF-8\n\n| if(exists $ENV{REQUEST_METHOD});
print $js_src;
exit;

eval{
	my @extlist = qw|.cgi|;
	my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);
	my $js_dir = File::Spec->catdir($FindBin::Bin,'js','ag');
	my $js_name = $cgi_name;
	$js_name =~ s/^get\-//g;
	my $js_path = File::Spec->catfile($js_dir,qq|$js_name.js|);
	my $js_mini_path = File::Spec->catfile($js_dir,qq|$js_name.mini.js|);
	my $java = qq|/usr/bin/java|;
	my $yui = qq|/bp3d/local/yuicompressor-2.4.6/yuicompressor-2.4.6.jar|;

	if(-e $js_dir && -w $js_dir){
		unless(-e $js_path && (stat($js_path))[9]>=(stat($0))[9] && -e $js_mini_path && (stat($js_mini_path))[9]>=(stat($js_path))[9]){
			unless(-e $js_path && (stat($js_path))[9]>=(stat($0))[9]){
				open(OUT,"> $js_path") or die $!;
				flock(OUT,2);
				print OUT $js_src;
				close(OUT);
				chmod 0666,$js_path if(-e $js_path);
			}
			unless(-e $js_path){
				print qq|Content-type: text/javascript; charset=UTF-8\n\n|;
				print $js_src;
				exit;
			}
			unless(-e $js_mini_path && (stat($js_mini_path))[9]>=(stat($js_path))[9]){
				unlink $js_mini_path if(-e $js_mini_path);
				system(qq|$java -jar $yui --type js --nomunge -o $js_mini_path $js_path|) if(-e $java && -e $yui);
				chmod 0666,$js_mini_path if(-e $js_mini_path);
			}
			unless(-e $js_mini_path){
				print qq|Content-type: text/javascript; charset=UTF-8\n\n|;
				print $js_src;
				exit;
			}
#			my $target = File::Spec->abs2rel($js_mini_path,$FindBin::Bin) . '?' . (stat($js_mini_path))[9];
#			print $query->redirect($target);

			print qq|Content-type: text/javascript; charset=UTF-8\n\n|;
			open(IN,$js_mini_path) or die $!;
			while(<IN>){
				print $_;
			}
			close(IN);

		}
	}else{
		print qq|Content-type: text/javascript; charset=UTF-8\n\n|;
		print $js_src;
	}
};
if($@){
	print qq|Content-type: text/javascript; charset=UTF-8\n\n|;
	print $js_src;
}
