#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use File::Spec;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
use BITS::Config;
require "webgl_common.pl";

my $dbh = &get_dbh();

my $query = CGI->new;

my $sql=<<SQL;
select prefix_id,prefix_char from id_prefix where prefix_delcause is null and prefix_id not in (2,3,4) order by prefix_order
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
my $DEF_PREFIX_DATAS = &JSON::XS::encode_json($PREFIX_DATAS);

my $sql=<<SQL;
select
 ci_id,
 ci_name
from
 concept_info
where
 ci_use and ci_delcause is null
order by
 ci_order
SQL
my $sth = $dbh->prepare($sql) or die $dbh->errstr;
$sth->execute() or die $dbh->errstr;
my($ci_id,$cb_id,$bul_id,$ci_name,$cb_name,$bul_name,$bul_abbr);
my $column_number = 0;
$sth->bind_col(++$column_number, \$ci_id, undef);
$sth->bind_col(++$column_number, \$ci_name, undef);
$sth->fetch;
$sth->finish;
undef $sth;
$ci_id = 0 unless(defined $ci_id);

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

my $USE_OBJ_TIMESTAMP_COMPARISON_UNIT = &BITS::Config::USE_OBJ_TIMESTAMP_COMPARISON_UNIT();
my $USE_OBJ_TIMESTAMP_COMPARISON_UNIT_DATE = &BITS::Config::USE_OBJ_TIMESTAMP_COMPARISON_UNIT_DATE();
my $USE_OBJ_TIMESTAMP_COMPARISON_UNIT_TIME = &BITS::Config::USE_OBJ_TIMESTAMP_COMPARISON_UNIT_TIME();

my $js_src =<<HTML;
var AgDef = {
	LOCALDB_PREFIX: '20190531-'
//	LOCALDB_PREFIX: '20181019-'
//	LOCALDB_PREFIX: '20181018-'
//	LOCALDB_PREFIX: '20180913-'
//	LOCALDB_PREFIX: '170403-'
//	LOCALDB_PREFIX: '161110-'
//	LOCALDB_PREFIX: '160914-'
//	LOCALDB_PREFIX: '160829-'
//	LOCALDB_PREFIX: '160418-'
//	LOCALDB_PREFIX: '151228-'
//	LOCALDB_PREFIX: '150812-'
//	LOCALDB_PREFIX: '130725-'
//	LOCALDB_PREFIX: '130801-'
};

var DEF_VALUES = {
	ci_id : $ci_id
};

var DEF_UPLOAD_FILE_MAX_SIZE = 1024 * 1024 * 1000;

var DEF_COLOR = '#F0D2A0';
var DEF_COLOR_HEX = 0xF0D2A0;

var DEF_PREFIX = '$def_prefix_char';
var DEF_PREFIX_ID = $def_prefix_id;
var MAINTAIN_UPLOAD_DIRECTORY_STRUCTURE = false;
var MAINTAIN_UPLOAD_DIRECTORY_STRUCTURE_TEXT = 'アップロードディレクトリ構造を維持';

var DEF_MODEL = 'bp3d';
var DEF_VERSION = '4.3i';
var DEF_TREE = 'isa';

var DEF_CONCEPT_INFO = '$ci_name';
var DEF_CONCEPT_BUILD = '3.2.1-inference';

var DEF_COORDINATESYSTEM = 'bp3d';

var DEF_MODEL_DATAS = {datas: [{
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

var USE_OBJ_TIMESTAMP_COMPARISON_UNIT = '$USE_OBJ_TIMESTAMP_COMPARISON_UNIT';
var USE_OBJ_TIMESTAMP_COMPARISON_UNIT_DATE = '$USE_OBJ_TIMESTAMP_COMPARISON_UNIT_DATE';
var USE_OBJ_TIMESTAMP_COMPARISON_UNIT_TIME = '$USE_OBJ_TIMESTAMP_COMPARISON_UNIT_TIME';

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

	art_filename  : 'Filename',
	art_folder : 'Folder',
	art_category : 'Category',
	art_class : 'Class',
	art_comment : 'Comment',
	art_judge : 'Judge',
	art_data_size : 'Size',
	art_xmin   : 'XMin(mm)',
	art_xmax   : 'XMax(mm)',
	art_xcenter: 'XCenter(mm)',
	art_ymin   : 'YMin(mm)',
	art_ymax   : 'YMax(mm)',
	art_ycenter: 'YCenter(mm)',
	art_zmin   : 'ZMin(mm)',
	art_zmax   : 'ZMax(mm)',
	art_zcenter: 'ZCenter(mm)',

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
//	cdi_name : 'id',

//	art_id : 'Model component',
	art_id : 'FJID',
	art_ids : 'FJID(s)',
	mca_id : 'MAPID',
	artf_names : 'Folder',

	make_sub : 'Make SUB',
	cmp_abbr : 'SUB',
	cp_abbr : 'SUB',
	cl_abbr : 'R/L',

	cdi_name_j : 'Japanese',
	cdi_name_e : 'Name',
//	cdi_name_e : 'name',
	cdi_name_k : 'Kana',
	cdi_name_l : 'Latina',

	cdi_syn_e : 'Synonym',
//	cdi_syn_e : 'synonym',
	cdi_syn_j : 'synonym(Jpn)',

	cdi_def_e : 'Definition',
//	cdi_def_e : 'definition',

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
	arto_comment : 'Org.Comment',

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
	cm_entry: 'Map date',
	upload_modified: 'Upload date',
	change_modified: 'Change date',

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

	concept_mng : 'Concept管理',
	build_signage : 'Build表記',

	add : 'Add',
	remove : 'Delete',

	edit : '編集',
	editable : '編集可',
	not_editable : '編集不可',
	not_editable_label : '編集不可にする',
	not_editable_state : '<b style="color:red;">編集不可</b>',

	not_found : 'not found',


	'new' : 'New',
	use : 'Use',
	ip : 'IP',

	copy: 'Copy',
	file_info: 'FMA mapping',
	filter: 'Filter',

	FMABrowser : 'FMABrowser',
//	mapping_mng : 'Mapping Manager',
//	subject : 'subject',
//	attribute : 'attribute',
//	existing_attribute : 'Existing + new attribute',
//	parent_attribute : 'Parent + new attribute',
	mapping_mng : 'Dictionary builder',
	subclass_list: 'Subclass List',
	subject : 'Meaning',
	attribute : 'Token',
	existing_attribute : 'Token HX',
	current : 'current',
	replace : 'replace',
	append : 'append',
	parent_attribute : 'Shell token',
	parent_attribute_parent : 'parent',
	parent_attribute_ancestor : 'ancestor',
	history_attribute : 'history attribute',
//	remove_from_current : 'remove from current',
//	remove_from_current : 'remove mapping',
	remove_from_current : 'cut',
	never_current : 'Never Current',


	fma_window : 'FMA',

	seg_color: 'Pallet',	//パーツパレット登録時のデフォルト色
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

	dataset_mng : 'データセット管理',

	recalculation : '再計算',
	error_recalculation_is_publish : '公開中の為、再計算できません',

	error_twitter: 'Twitterエラーレポート管理',
	error_file_size: 'ファイルサイズが{0}を超えています',
	error_folder_find: '「{0}」は「{1}」上に存在しません',
	error_twitter_fix_title: 'Error Report Fix',
	error_save: '保存に失敗しました',
	error_delete: '削除に失敗しました',
	error_submit: '登録に失敗しました',

	error_arto_id: 'オリジナルのFJIDを指定して下さい',
	error_cdi_name: '指定されたFMAIDは存在しません',
	error_port : 'Renderer Port番号を指定して下さい',

	'window' : 'ウィンドウ',
	window_alignment : 'ウィンドウ整列',
	fma_corresponding_change : 'FMA対応変更',
	fma_corresponding_change_mode : 'FMA対応変更モード',
	fma_corresponding_change_dialog_message : 'FMA対応情報を指定してください。',
	fma_corresponding_change_dialog_error_message : 'FMA対応情報を解析できません',
	fma_corresponding_link_break : 'FMA対応削除',
	conflict_list : 'Conflict list',

	freeze_mapping : 'Freeze mapping',
	corrected_reference_point : 'Corrected reference point',
	edited : 'edited',

	cx_create: 'CX Create',
	cx_create_folder: 'Folder',
	cx_create_folder_labelWidth: 37,

	cx_search: 'CX OBJ filename Search',
	cx_search_empty_text: 'CX OBJ filename Search (AND search)',
	cx_search_folder: 'Folder',
	cx_search_folder_labelWidth: 37,

	obj_search: 'OBJ filename Search',
	obj_search_empty_text: 'OBJ filename Search (AND search)',
	obj_search_folder: 'Folder',
	obj_search_folder_labelWidth: 37
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
