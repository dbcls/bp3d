// /ext1/project/WebGL/htdocs/get-AgDefaults.cgiより自動生成
var AgDef = {
	LOCALDB_PREFIX: '150812-'
//	LOCALDB_PREFIX: '130725-'
//	LOCALDB_PREFIX: '130801-'
};

var DEF_VALUES = {
	md_id : 1,
	mv_id : 9,
	mr_id : 1,
	ci_id : 1,
	cb_id : 4,
	bul_id : 3
};

var DEF_UPLOAD_FILE_MAX_SIZE = 1024 * 1024 * 1000;

var DEF_COLOR = '#F0D2A0';
var DEF_COLOR_HEX = 0xF0D2A0;

var DEF_MODEL = 'bp3d';
var DEF_MODEL_ID = 1;
var DEF_VERSION = '5.0heart';

var DEF_PREFIX = 'MM';
var DEF_PREFIX_ID = 5;


var DEF_CONCEPT_INFO = 'FMA';
var DEF_CONCEPT_BUILD = '3.0';
var DEF_TREE = 'isa';

var DEF_AG_DATA = 'obj/bp3d/5.0heart';
//var DEF_TREE = DEF_MODEL+'-'+DEF_TREE;

var DEF_VERSION_COMBO = DEF_MODEL+'-'+DEF_VERSION;
var DEF_TREE_COMBO = DEF_MODEL+'-'+DEF_TREE;

var DEF_COORDINATESYSTEM = 'bp3d';

var DEF_MODEL_DATAS = {datas: [{
	display: 'BodyParts3D',
	value:   'bp3d',
	md_id:   1,
	md_abbr: 'bp3d'
}]};
var DEF_PREFIX_DATAS = {"datas":[{"prefix_char":"MM","value":5,"prefix_id":5,"display":"MM"},{"prefix_char":"FJ","value":1,"prefix_id":1,"display":"FJ"}]};

var DEF_UPLOAD_FILE_PAGE_SIZE = 25;
var DEF_PARTS_GRID_PAGE_SIZE = 50;
var DEF_FMA_SEARCH_GRID_PAGE_SIZE = 50;
var DEF_ERROR_TWITTER_GRID_PAGE_SIZE = 25;
var DEF_FIND_FILE_PAGE_SIZE = 10;
var DEF_PICK_SEAECH_MAX_RANGE = 20;
//var DEF_IMG_BASE_URL = 'http://lifesciencedb.jp/bp3d/';
//var DEF_IMG_BASE_URL = 'http://221.186.138.155/bp3d-38321/';
var DEF_IMG_BASE_URL = 'http://lifesciencedb.jp/bp3d/';

//var bp3d_lng = {
var AgLang = {
//	version : 'Version',
	version : 'Font set',
	revision: 'Revision',
//	version_signage : 'Version表記',
	version_signage : 'Font set表記',

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
//	save   : 'Save',
//	cancel : 'Cancel',
//	close  : 'Close',

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

	dataset_mng : 'データセット管理',

	recalculation : '再計算',
	error_recalculation_is_publish : '公開中の為、再計算できません',

	error_twitter: 'Twitterエラーレポート管理',
	error_file_size: 'ファイルサイズが{0}を超えています',
	error_folder_find: '「{0}」は「{1}」上に存在しません',
	error_twitter_fix_title: 'Error Report Fix',
	error_save: '保存に失敗しました',

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
