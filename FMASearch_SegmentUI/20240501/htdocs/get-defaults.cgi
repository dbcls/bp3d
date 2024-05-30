#!/opt/services/ag/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use File::Spec::Functions qw(abs2rel catdir catfile splitdir);

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
use BITS::Config;
require "webgl_common.pl";


my $query = CGI->new;


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
var Ag = Ag || {};
Ag.Def = {

	LOCALDB_PREFIX: '20220401-',

	CONCEPT_TERM_SEARCH_GRID_PAGE_SIZE: 0,

	FORMAT_CONCEPT_VALUE: '{0}-{1}',
	FORMAT_MODEL_VERSION_VALUE: '{0}-{1}',
	CONCEPT_TERM_STORE_ID: 'conceptStore',
	CONCEPT_TERM_SEARCH_STORE_ID: 'conceptSearchStore',
	CONCEPT_MATCH_LIST_STORE_ID: 'conceptMatchListStore',
	CONCEPT_PARENT_TERM_STORE_ID: 'conceptParentStore',
	CONCEPT_SELECTED_ITEMS_STORE_ID: 'conceptSelectedItemsStore',
	CONCEPT_SELECTED_TAGS_STORE_ID: 'conceptSelectedTagsStore',

	APP_NAME: '@{[BITS::Config::APP_NAME]}',
	APP_TITLE: '@{[BITS::Config::APP_TITLE]}',

	DEF_MODEL_TERM: '@{[BITS::Config::DEF_MODEL_TERM]}',
	DEF_MODEL_VERSION_TERM: '@{[BITS::Config::DEF_MODEL_VERSION_TERM]}',
	DEF_CONCEPT_INFO_TERM: '@{[BITS::Config::DEF_CONCEPT_INFO_TERM]}',
	DEF_CONCEPT_BUILD_TERM: '@{[BITS::Config::DEF_CONCEPT_BUILD_TERM]}',

	LOCATION_HASH_CIID_KEY: '@{[BITS::Config::LOCATION_HASH_CIID_KEY]}',
	LOCATION_HASH_CBID_KEY: '@{[BITS::Config::LOCATION_HASH_CBID_KEY]}',
	LOCATION_HASH_MDID_KEY: '@{[BITS::Config::LOCATION_HASH_MDID_KEY]}',
	LOCATION_HASH_MVID_KEY: '@{[BITS::Config::LOCATION_HASH_MVID_KEY]}',
	LOCATION_HASH_MRID_KEY: '@{[BITS::Config::LOCATION_HASH_MRID_KEY]}',
	LOCATION_HASH_ID_KEY: '@{[BITS::Config::LOCATION_HASH_ID_KEY]}',
	LOCATION_HASH_IDS_KEY: '@{[BITS::Config::LOCATION_HASH_IDS_KEY]}',
	LOCATION_HASH_CID_KEY: '@{[BITS::Config::LOCATION_HASH_CID_KEY]}',
	LOCATION_HASH_CIDS_KEY: '@{[BITS::Config::LOCATION_HASH_CIDS_KEY]}',
	LOCATION_HASH_NAME_KEY: '@{[BITS::Config::LOCATION_HASH_NAME_KEY]}',
	LOCATION_HASH_SEARCH_KEY: '@{[BITS::Config::LOCATION_HASH_SEARCH_KEY]}',
	LOCATION_HASH_SEARCH_EXCLUDE_KEY: '@{[BITS::Config::LOCATION_HASH_SEARCH_EXCLUDE_KEY]}',

	SEARCH_TARGET_NAME: '@{[BITS::Config::SEARCH_TARGET_NAME]}',
	SEARCH_TARGET_ELEMENT_VALUE: '@{[BITS::Config::SEARCH_TARGET_ELEMENT_VALUE]}',
	SEARCH_TARGET_WHOLE_VALUE: '@{[BITS::Config::SEARCH_TARGET_WHOLE_VALUE]}',

	SEARCH_ANY_MATCH_NAME: '@{[BITS::Config::SEARCH_ANY_MATCH_NAME]}',
	SEARCH_CASE_SENSITIVE_NAME: '@{[BITS::Config::SEARCH_CASE_SENSITIVE_NAME]}',
	RELATION_TYPE_NAME: '@{[BITS::Config::RELATION_TYPE_NAME]}',

	CONCEPT_INFO_DATA_FIELD_ID: '@{[BITS::Config::CONCEPT_INFO_DATA_FIELD_ID]}',
	CONCEPT_BUILD_DATA_FIELD_ID: '@{[BITS::Config::CONCEPT_BUILD_DATA_FIELD_ID]}',
	CONCEPT_DATA_DATA_FIELD_ID: '@{[BITS::Config::CONCEPT_DATA_DATA_FIELD_ID]}',
	CONCEPT_DATA_INFO_DATA_FIELD_ID: '@{[BITS::Config::CONCEPT_DATA_INFO_DATA_FIELD_ID]}',

	CONCEPT_DATA_COLOR_DATA_FIELD_ID: '@{[BITS::Config::CONCEPT_DATA_COLOR_DATA_FIELD_ID]}',
	CONCEPT_DATA_OPACITY_DATA_FIELD_ID: '@{[BITS::Config::CONCEPT_DATA_OPACITY_DATA_FIELD_ID]}',
	CONCEPT_DATA_VISIBLE_DATA_FIELD_ID: '@{[BITS::Config::CONCEPT_DATA_VISIBLE_DATA_FIELD_ID]}',
	CONCEPT_DATA_SELECTED_DATA_FIELD_ID: '@{[BITS::Config::CONCEPT_DATA_SELECTED_DATA_FIELD_ID]}',
	CONCEPT_DATA_DISABLED_DATA_FIELD_ID: '@{[BITS::Config::CONCEPT_DATA_DISABLED_DATA_FIELD_ID]}',
	CONCEPT_DATA_PICKED_DATA_FIELD_ID: '@{[BITS::Config::CONCEPT_DATA_PICKED_DATA_FIELD_ID]}',
	CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID: '@{[BITS::Config::CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID]}',
	CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID: '@{[BITS::Config::CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID]}',
	CONCEPT_DATA_PICKED_TYPE_ITEMS: '@{[BITS::Config::CONCEPT_DATA_PICKED_TYPE_ITEMS]}',
	CONCEPT_DATA_PICKED_TYPE_TAGS: '@{[BITS::Config::CONCEPT_DATA_PICKED_TYPE_TAGS]}',
	CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID: '@{[BITS::Config::CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID]}',
	CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID: '@{[BITS::Config::CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID]}',
	CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID: '@{[BITS::Config::CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID]}',
	CONCEPT_DATA_SELECTED_SEGMENT_TAG_DATA_FIELD_ID: '@{[BITS::Config::CONCEPT_DATA_SELECTED_SEGMENT_TAG_DATA_FIELD_ID]}',
	CONCEPT_DATA_SELECTED_CATEGORY_TAG_DATA_FIELD_ID: '@{[BITS::Config::CONCEPT_DATA_SELECTED_CATEGORY_TAG_DATA_FIELD_ID]}',

	CONCEPT_DATA_CATEGORY_DATA_FIELD_ID: '@{[BITS::Config::CONCEPT_DATA_CATEGORY_DATA_FIELD_ID]}',
	CONCEPT_DATA_RELATION_DATA_FIELD_ID: '@{[BITS::Config::CONCEPT_DATA_RELATION_DATA_FIELD_ID]}',

	MODEL_DATA_FIELD_ID: '@{[BITS::Config::MODEL_DATA_FIELD_ID]}',
	MODEL_VERSION_DATA_FIELD_ID: '@{[BITS::Config::MODEL_VERSION_DATA_FIELD_ID]}',
	MODEL_REVISION_DATA_FIELD_ID: '@{[BITS::Config::MODEL_REVISION_DATA_FIELD_ID]}',

	BUILDUP_TREE_DEPTH_FIELD_ID: '@{[BITS::Config::BUILDUP_TREE_DEPTH_FIELD_ID]}',
	VERSION_STRING_FIELD_ID: '@{[BITS::Config::VERSION_STRING_FIELD_ID]}',
	VERSION_ORDER_FIELD_ID: '@{[BITS::Config::VERSION_ORDER_FIELD_ID]}',
	USE_FOR_BOUNDING_BOX_FIELD_ID: '@{[BITS::Config::USE_FOR_BOUNDING_BOX_FIELD_ID]}',
	PART_REPRESENTATION: '@{[BITS::Config::PART_REPRESENTATION]}',
	PART_WIREFRAME_COLOR: '@{[BITS::Config::PART_WIREFRAME_COLOR]}',

	ID_DATA_FIELD_ID: '@{[BITS::Config::ID_DATA_FIELD_ID]}',
	ID_DATA_FIELD_WIDTH: @{[BITS::Config::ID_DATA_FIELD_WIDTH]},
	IDS_DATA_FIELD_ID: '@{[BITS::Config::IDS_DATA_FIELD_ID]}',
	NAME_DATA_FIELD_ID: '@{[BITS::Config::NAME_DATA_FIELD_ID]}',
	SYNONYM_DATA_FIELD_ID: '@{[BITS::Config::SYNONYM_DATA_FIELD_ID]}',
	DEFINITION_DATA_FIELD_ID: '@{[BITS::Config::DEFINITION_DATA_FIELD_ID]}',

	TERM_ID_DATA_FIELD_ID: '@{[BITS::Config::TERM_ID_DATA_FIELD_ID]}',
	TERM_NAME_DATA_FIELD_ID: '@{[BITS::Config::TERM_NAME_DATA_FIELD_ID]}',

	SNIPPET_ID_DATA_FIELD_ID: '@{[BITS::Config::SNIPPET_ID_DATA_FIELD_ID]}',
	SNIPPET_NAME_DATA_FIELD_ID: '@{[BITS::Config::SNIPPET_NAME_DATA_FIELD_ID]}',
	SNIPPET_SYNONYM_DATA_FIELD_ID: '@{[BITS::Config::SNIPPET_SYNONYM_DATA_FIELD_ID]}',

	OBJ_PATH_NAME: '@{[BITS::Config::OBJ_PATH_NAME]}',
	OBJ_EXT_NAME: '@{[BITS::Config::OBJ_EXT_NAME]}',
	OBJ_ID_DATA_FIELD_ID: '@{[BITS::Config::OBJ_ID_DATA_FIELD_ID]}',
	OBJ_IDS_DATA_FIELD_ID: '@{[BITS::Config::OBJ_IDS_DATA_FIELD_ID]}',
	OBJ_URL_DATA_FIELD_ID: '@{[BITS::Config::OBJ_URL_DATA_FIELD_ID]}',
	OBJ_TIMESTAMP_DATA_FIELD_ID: '@{[BITS::Config::OBJ_TIMESTAMP_DATA_FIELD_ID]}',
	OBJ_FILENAME_FIELD_ID: '@{[BITS::Config::OBJ_FILENAME_FIELD_ID]}',

	OBJ_X_MASS_CENTER_FIELD_ID: '@{[BITS::Config::OBJ_X_MASS_CENTER_FIELD_ID]}',
	OBJ_Y_MASS_CENTER_FIELD_ID: '@{[BITS::Config::OBJ_Y_MASS_CENTER_FIELD_ID]}',
	OBJ_Z_MASS_CENTER_FIELD_ID: '@{[BITS::Config::OBJ_Z_MASS_CENTER_FIELD_ID]}',

	OBJ_NAME_FIELD_ID: '@{[BITS::Config::OBJ_NAME_FIELD_ID]}',
	OBJ_EXT_FIELD_ID: '@{[BITS::Config::OBJ_EXT_FIELD_ID]}',
	OBJ_DATA_SIZE_FIELD_ID: '@{[BITS::Config::OBJ_DATA_SIZE_FIELD_ID]}',

	OBJ_COMMENT_FIELD_ID: '@{[BITS::Config::OBJ_COMMENT_FIELD_ID]}',
	OBJ_CATEGORY_FIELD_ID: '@{[BITS::Config::OBJ_CATEGORY_FIELD_ID]}',
	OBJ_JUDGE_FIELD_ID: '@{[BITS::Config::OBJ_JUDGE_FIELD_ID]}',
	OBJ_CLASS_FIELD_ID: '@{[BITS::Config::OBJ_CLASS_FIELD_ID]}',

	OBJ_CONCEPT_ID_DATA_FIELD_ID: '@{[BITS::Config::OBJ_CONCEPT_ID_DATA_FIELD_ID]}',

	OBJ_THUMBNAIL_PATH_FIELD_ID: '@{[BITS::Config::OBJ_THUMBNAIL_PATH_FIELD_ID]}',

	CONCEPT_DATA_INFO_ID_FIELD_ID: '@{[BITS::Config::CONCEPT_DATA_INFO_ID_FIELD_ID]}',
	CONCEPT_DATA_INFO_NAME_FIELD_ID: '@{[BITS::Config::CONCEPT_DATA_INFO_NAME_FIELD_ID]}',
	CONCEPT_DATA_INFO_NAME_E_FIELD_ID: '@{[BITS::Config::CONCEPT_DATA_INFO_NAME_E_FIELD_ID]}',

	CONCEPT_OBJ_MAP_PART_ID_FIELD_ID: '@{[BITS::Config::CONCEPT_OBJ_MAP_PART_ID_FIELD_ID]}',
	CONCEPT_OBJ_MAP_ENTRY_FIELD_ID: '@{[BITS::Config::CONCEPT_OBJ_MAP_ENTRY_FIELD_ID]}',

	SEGMENT_COLOR_FIELD_ID: '@{[BITS::Config::SEGMENT_COLOR_FIELD_ID]}',

	OBJ_X_MIN_FIELD_ID: '@{[BITS::Config::OBJ_X_MIN_FIELD_ID]}',
	OBJ_X_MAX_FIELD_ID: '@{[BITS::Config::OBJ_X_MAX_FIELD_ID]}',
	OBJ_Y_MIN_FIELD_ID: '@{[BITS::Config::OBJ_Y_MIN_FIELD_ID]}',
	OBJ_Y_MAX_FIELD_ID: '@{[BITS::Config::OBJ_Y_MAX_FIELD_ID]}',
	OBJ_Z_MIN_FIELD_ID: '@{[BITS::Config::OBJ_Z_MIN_FIELD_ID]}',
	OBJ_Z_MAX_FIELD_ID: '@{[BITS::Config::OBJ_Z_MAX_FIELD_ID]}',

	OBJ_POLYS_FIELD_ID: '@{[BITS::Config::OBJ_POLYS_FIELD_ID]}',
	OBJ_VOLUME_FIELD_ID: '@{[BITS::Config::OBJ_VOLUME_FIELD_ID]}',
	OBJ_CITIES_FIELD_ID: '@{[BITS::Config::OBJ_CITIES_FIELD_ID]}',
	OBJ_PREFECTURES_FIELD_ID: '@{[BITS::Config::OBJ_PREFECTURES_FIELD_ID]}',

	PIN_ID_FIELD_ID: '@{[BITS::Config::PIN_ID_FIELD_ID]}',
	PIN_NO_FIELD_ID: '@{[BITS::Config::PIN_NO_FIELD_ID]}',
	PIN_COORDINATE_X_FIELD_ID: '@{[BITS::Config::PIN_COORDINATE_X_FIELD_ID]}',
	PIN_COORDINATE_Y_FIELD_ID: '@{[BITS::Config::PIN_COORDINATE_Y_FIELD_ID]}',
	PIN_COORDINATE_Z_FIELD_ID: '@{[BITS::Config::PIN_COORDINATE_Z_FIELD_ID]}',
	PIN_VECTOR_X_FIELD_ID: '@{[BITS::Config::PIN_VECTOR_X_FIELD_ID]}',
	PIN_VECTOR_Y_FIELD_ID: '@{[BITS::Config::PIN_VECTOR_Y_FIELD_ID]}',
	PIN_VECTOR_Z_FIELD_ID: '@{[BITS::Config::PIN_VECTOR_Z_FIELD_ID]}',
	PIN_UP_VECTOR_X_FIELD_ID: '@{[BITS::Config::PIN_UP_VECTOR_X_FIELD_ID]}',
	PIN_UP_VECTOR_Y_FIELD_ID: '@{[BITS::Config::PIN_UP_VECTOR_Y_FIELD_ID]}',
	PIN_UP_VECTOR_Z_FIELD_ID: '@{[BITS::Config::PIN_UP_VECTOR_Z_FIELD_ID]}',
	PIN_DESCRIPTION_DRAW_FLAG_FIELD_ID: '@{[BITS::Config::PIN_DESCRIPTION_DRAW_FLAG_FIELD_ID]}',
	PIN_DESCRIPTION_COLOR_FIELD_ID: '@{[BITS::Config::PIN_DESCRIPTION_COLOR_FIELD_ID]}',
	PIN_DESCRIPTION_FIELD_ID: '@{[BITS::Config::PIN_DESCRIPTION_FIELD_ID]}',
	PIN_COLOR_FIELD_ID: '@{[BITS::Config::PIN_COLOR_FIELD_ID]}',
	PIN_SHAPE_FIELD_ID: '@{[BITS::Config::PIN_SHAPE_FIELD_ID]}',
	PIN_SIZE_FIELD_ID: '@{[BITS::Config::PIN_SIZE_FIELD_ID]}',
	PIN_COORDINATE_SYSTEM_NAME_FIELD_ID: '@{[BITS::Config::PIN_COORDINATE_SYSTEM_NAME_FIELD_ID]}',
	PIN_PART_ID_FIELD_ID: '@{[BITS::Config::PIN_PART_ID_FIELD_ID]}',
	PIN_PART_NAME_FIELD_ID: '@{[BITS::Config::PIN_PART_NAME_FIELD_ID]}',
	PIN_VISIBLE_FIELD_ID: '@{[BITS::Config::PIN_VISIBLE_FIELD_ID]}',

	SEGMENT_DATA_FIELD_ID: '@{[BITS::Config::SEGMENT_DATA_FIELD_ID]}',
	SEGMENT_ID_DATA_FIELD_ID: '@{[BITS::Config::SEGMENT_ID_DATA_FIELD_ID]}',
	SEGMENT_ORDER_DATA_FIELD_ID: '@{[BITS::Config::SEGMENT_ORDER_DATA_FIELD_ID]}',
	SYSTEM_ID_DATA_FIELD_ID: '@{[BITS::Config::SYSTEM_ID_DATA_FIELD_ID]}',
	SYSTEM10_ID_DATA_FIELD_ID: '@{[BITS::Config::SYSTEM10_ID_DATA_FIELD_ID]}',
	SYSTEM10_NAME_DATA_FIELD_ID: '@{[BITS::Config::SYSTEM10_NAME_DATA_FIELD_ID]}',

	DISTANCE_FIELD_ID: '@{[BITS::Config::DISTANCE_FIELD_ID]}',
	VOXEL_RANGE_FIELD_ID: '@{[BITS::Config::VOXEL_RANGE_FIELD_ID]}',
	CONDITIONS_FIELD_ID: '@{[BITS::Config::CONDITIONS_FIELD_ID]}',
	OBJ_POINT_FIELD_ID: '@{[BITS::Config::OBJ_POINT_FIELD_ID]}',
	TARGET_RECORD_FIELD_ID: '@{[BITS::Config::TARGET_RECORD_FIELD_ID]}',
	EXISTS_PALETTE_FIELD_ID: '@{[BITS::Config::EXISTS_PALETTE_FIELD_ID]}',

	CDS_DATA_FIELD_ID: '@{[BITS::Config::CDS_DATA_FIELD_ID]}',
	CDS_NAME_DATA_FIELD_ID: '@{[BITS::Config::CDS_NAME_DATA_FIELD_ID]}',
	CDS_BASE_NAME_DATA_FIELD_ID: '@{[BITS::Config::CDS_BASE_NAME_DATA_FIELD_ID]}',
	CDS_BASE_ID_DATA_FIELD_ID: '@{[BITS::Config::CDS_BASE_ID_DATA_FIELD_ID]}',
	CDS_ADDED_DATA_FIELD_ID: '@{[BITS::Config::CDS_ADDED_DATA_FIELD_ID]}',

	COLOR_COLUMN_WIDTH: @{[BITS::Config::COLOR_COLUMN_WIDTH]}
};


Ag.Lang = {
	title : 'FMABrowser',

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
	conflict_list : 'Conflict list'
};
HTML

if(exists $ENV{'AG_DEBUG'} && defined $ENV{'AG_DEBUG'} && $ENV{'AG_DEBUG'} eq '1'){
	$js_src .= <<HTML;
Ag.Def.DEBUG = true;
HTML
}
if(exists $ENV{'REQUEST_METHOD'}){
	print qq|Content-type: text/javascript; charset=UTF-8\n\n|;
	print $js_src;
#exit;
}

eval{
	my @extlist = qw|.cgi|;
	my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);
	my $js_dir = &catdir($FindBin::Bin,'static','js','ag','Ag');
	my $js_name = $cgi_name;
	$js_name =~ s/^get\-//g;
	my $js_path = &catfile($js_dir,qq|$js_name.js|);
	my $js_mini_path = &catfile($js_dir,qq|$js_name.min.js|);
	my $java = qq|/usr/bin/java|;
	my $yui = qq|/opt/services/ag/local/yuicompressor/build/yuicompressor-2.4.9.jar|;

	unless(exists $ENV{'REQUEST_METHOD'}){
		say STDERR $js_dir;
		say STDERR $js_path;
		say STDERR $js_mini_path;
	}

	if(-e $js_dir && -w $js_dir){
		unless(-e $js_path && (stat($js_path))[9]>=(stat($0))[9] && -e $js_mini_path && (stat($js_mini_path))[9]>=(stat($js_path))[9]){
			unless(-e $js_path && (stat($js_path))[9]>=(stat($0))[9]){
				open(OUT,"> $js_path") or die $!;
				flock(OUT,2);
				print OUT $js_src;
				close(OUT);
				chmod 0600,$js_path if(-e $js_path);
			}
#			unless(-e $js_path){
#				print qq|Content-type: text/javascript; charset=UTF-8\n\n|;
#				print $js_src;
#				exit;
#			}
			unless(-e $js_mini_path && (stat($js_mini_path))[9]>=(stat($js_path))[9]){
				unlink $js_mini_path if(-e $js_mini_path);
				system(qq|$java -jar $yui --type js --nomunge -o $js_mini_path $js_path|) if(-e $java && -e $yui);
				chmod 0600,$js_mini_path if(-e $js_mini_path);
			}
#			unless(-e $js_mini_path){
#				print qq|Content-type: text/javascript; charset=UTF-8\n\n|;
#				print $js_src;
#				exit;
#			}
#			my $target = &abs2rel($js_mini_path,$FindBin::Bin) . '?' . (stat($js_mini_path))[9];
#			print $query->redirect($target);

#			print qq|Content-type: text/javascript; charset=UTF-8\n\n|;
#			open(IN,$js_mini_path) or die $!;
#			while(<IN>){
#				print $_;
#			}
#			close(IN);

		}
	}else{
#		print qq|Content-type: text/javascript; charset=UTF-8\n\n|;
#		print $js_src;
	}
};
if($@){
#	print qq|Content-type: text/javascript; charset=UTF-8\n\n|;
#	print $js_src;
}
