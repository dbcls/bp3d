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

my $USE_OBJ_TIMESTAMP_COMPARISON_UNIT = &BITS::Config::USE_OBJ_TIMESTAMP_COMPARISON_UNIT();
my $USE_OBJ_TIMESTAMP_COMPARISON_UNIT_DATE = &BITS::Config::USE_OBJ_TIMESTAMP_COMPARISON_UNIT_DATE();
my $USE_OBJ_TIMESTAMP_COMPARISON_UNIT_TIME = &BITS::Config::USE_OBJ_TIMESTAMP_COMPARISON_UNIT_TIME();

my $js_src =<<HTML;
var AgDef = {
	LOCALDB_PREFIX: '160418-',
//	LOCALDB_PREFIX: '151228-'
//	LOCALDB_PREFIX: '150812-'
//	LOCALDB_PREFIX: '130725-'
//	LOCALDB_PREFIX: '130801-'

	CONCEPT_TERM_SEARCH_GRID_PAGE_SIZE: 50,
	FORMAT_CONCEPT_VALUE: '{0}-{1}',
	CONCEPT_TERM_STORE_ID: 'conceptStore',
	CONCEPT_TERM_SEARCH_STORE_ID: 'conceptSearchStore',

	LOCATION_HASH_CIID_KEY: '@{[BITS::Config::LOCATION_HASH_CIID_KEY]}',
	LOCATION_HASH_CBID_KEY: '@{[BITS::Config::LOCATION_HASH_CBID_KEY]}',
	LOCATION_HASH_ID_KEY: '@{[BITS::Config::LOCATION_HASH_ID_KEY]}',
	LOCATION_HASH_NAME_KEY: '@{[BITS::Config::LOCATION_HASH_NAME_KEY]}',
	LOCATION_HASH_SEARCH_KEY: '@{[BITS::Config::LOCATION_HASH_SEARCH_KEY]}',

	SEARCH_ANY_MATCH_NAME: '@{[BITS::Config::SEARCH_ANY_MATCH_NAME]}',
	SEARCH_CASE_SENSITIVE_NAME: '@{[BITS::Config::SEARCH_CASE_SENSITIVE_NAME]}',
	RELATION_TYPE_NAME: '@{[BITS::Config::RELATION_TYPE_NAME]}',

	CONCEPT_INFO_DATA_FIELD_ID: '@{[BITS::Config::CONCEPT_INFO_DATA_FIELD_ID]}',
	CONCEPT_BUILD_DATA_FIELD_ID: '@{[BITS::Config::CONCEPT_BUILD_DATA_FIELD_ID]}',

	ID_DATA_FIELD_ID: '@{[BITS::Config::ID_DATA_FIELD_ID]}',
	NAME_DATA_FIELD_ID: '@{[BITS::Config::NAME_DATA_FIELD_ID]}',
	SYNONYM_DATA_FIELD_ID: '@{[BITS::Config::SYNONYM_DATA_FIELD_ID]}',
	DEFINITION_DATA_FIELD_ID: '@{[BITS::Config::DEFINITION_DATA_FIELD_ID]}',

	TERM_ID_DATA_FIELD_ID: '@{[BITS::Config::TERM_ID_DATA_FIELD_ID]}',
	TERM_NAME_DATA_FIELD_ID: '@{[BITS::Config::TERM_NAME_DATA_FIELD_ID]}',

	SNIPPET_ID_DATA_FIELD_ID: '@{[BITS::Config::SNIPPET_ID_DATA_FIELD_ID]}',
	SNIPPET_NAME_DATA_FIELD_ID: '@{[BITS::Config::SNIPPET_NAME_DATA_FIELD_ID]}',
	SNIPPET_SYNONYM_DATA_FIELD_ID: '@{[BITS::Config::SNIPPET_SYNONYM_DATA_FIELD_ID]}',

	IS_SHAPE_FIELD_ID: '@{[BITS::Config::IS_SHAPE_FIELD_ID]}',
	IS_MAPED_FIELD_ID: '@{[BITS::Config::IS_MAPED_FIELD_ID]}',
	IS_CURRENT_FIELD_ID: '@{[BITS::Config::IS_CURRENT_FIELD_ID]}',

	CDS_DATA_FIELD_ID: '@{[BITS::Config::CDS_DATA_FIELD_ID]}',
	CDS_ADDED_DATA_FIELD_ID: '@{[BITS::Config::CDS_ADDED_DATA_FIELD_ID]}',
	CDS_ADDED_AUTO_DATA_FIELD_ID: '@{[BITS::Config::CDS_ADDED_AUTO_DATA_FIELD_ID]}',
	CDS_EDITED_DATA_FIELD_ID: '@{[BITS::Config::CDS_EDITED_DATA_FIELD_ID]}',
	CDS_DELETED_DATA_FIELD_ID: '@{[BITS::Config::CDS_DELETED_DATA_FIELD_ID]}',
	CDS_ORDER_DATA_FIELD_ID: '@{[BITS::Config::CDS_ORDER_DATA_FIELD_ID]}',
	CS_NAME_DATA_FIELD_ID: '@{[BITS::Config::CS_NAME_DATA_FIELD_ID]}',
	CS_ID_DATA_FIELD_ID: '@{[BITS::Config::CS_ID_DATA_FIELD_ID]}',
	CDS_ID_DATA_FIELD_ID: '@{[BITS::Config::CDS_ID_DATA_FIELD_ID]}',
	CDS_BID_DATA_FIELD_ID: '@{[BITS::Config::CDS_BID_DATA_FIELD_ID]}'
};

var USE_OBJ_TIMESTAMP_COMPARISON_UNIT = '$USE_OBJ_TIMESTAMP_COMPARISON_UNIT';
var USE_OBJ_TIMESTAMP_COMPARISON_UNIT_DATE = '$USE_OBJ_TIMESTAMP_COMPARISON_UNIT_DATE';
var USE_OBJ_TIMESTAMP_COMPARISON_UNIT_TIME = '$USE_OBJ_TIMESTAMP_COMPARISON_UNIT_TIME';

var AgLang = {
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

	remove_from_current : 'cut',
	never_current : 'Never Current',
	cm_entry: 'Map date',
	cmp_abbr : 'SUB',
	'new' : 'New',
	existing_attribute : 'Token HX',
	artf_names : 'Folder',
	upload_modified: 'Upload date',
	current : 'current',
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
	my $js_dir = &catdir($FindBin::Bin,'static','js','ag');
	my $js_name = $cgi_name;
	$js_name =~ s/^get\-//g;
	my $js_path = &catfile($js_dir,qq|$js_name.js|);
	my $js_mini_path = &catfile($js_dir,qq|$js_name.mini.js|);
	my $java = qq|/usr/bin/java|;
	my $yui = qq|/opt/services/ag/local/yuicompressor-2.4.6/yuicompressor-2.4.6.jar|;

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
#			my $target = &abs2rel($js_mini_path,$FindBin::Bin) . '?' . (stat($js_mini_path))[9];
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
