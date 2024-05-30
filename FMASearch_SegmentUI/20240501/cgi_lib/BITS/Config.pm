package BITS::Config;

use strict;
use warnings;
use feature ':5.10';

use Exporter;
use File::Spec::Functions;

use constant {
#	DEBUG => exists $ENV{'AG_DB_PORT'} && defined $ENV{'AG_DB_PORT'} && $ENV{'AG_DB_PORT'} eq '38300' ? 1 : 0,
	DEBUG => exists $ENV{'AG_DEBUG'} && defined $ENV{'AG_DEBUG'} && $ENV{'AG_DEBUG'} ? 1 : 0,
	IS_PUBLIC => exists $ENV{'AG_IS_PUBLIC'} && defined $ENV{'AG_IS_PUBLIC'} && $ENV{'AG_IS_PUBLIC'} ? 1 : 0,
#	DEBUG => 1,
	USE_HTML5 => 1,
	USE_APPCACHE => 0
};
use constant {
	APP_NAME   => 'FMASearch',
	APP_TITLE   => 'FMASearch',

	DEF_MODEL_TERM => 'BodyParts3D',
	DEF_MODEL_VERSION_TERM => '20161017i4',
	DEF_CONCEPT_INFO_TERM => 'FMA',
#	DEF_CONCEPT_BUILD_TERM => '3.2.1-inference',
	DEF_CONCEPT_BUILD_TERM => '4.3.0-inference',

	LOCATION_HASH_CIID_KEY   => 'ci',
	LOCATION_HASH_CBID_KEY   => 'cb',
	LOCATION_HASH_MDID_KEY   => 'md',
	LOCATION_HASH_MVID_KEY   => 'mv',
	LOCATION_HASH_MRID_KEY   => 'mr',
	LOCATION_HASH_ID_KEY     => 'id',
	LOCATION_HASH_IDS_KEY    => 'ids',
	LOCATION_HASH_CID_KEY    => 'cid',
	LOCATION_HASH_CIDS_KEY    => 'cids',
	LOCATION_HASH_NAME_KEY   => 'name',
	LOCATION_HASH_SEARCH_KEY => 'query',
	LOCATION_HASH_SEARCH_EXCLUDE_KEY => 'exclude',

	SEARCH_TARGET_NAME      => 'searchTarget',
	SEARCH_TARGET_ELEMENT_VALUE => 1,
	SEARCH_TARGET_WHOLE_VALUE    => 2,
	SEARCH_ANY_MATCH_NAME      => 'anyMatch',
	SEARCH_CASE_SENSITIVE_NAME => 'caseSensitive',
	RELATION_TYPE_NAME         => 'type'
};
use constant {
	CONCEPT_INFO_DATA_FIELD_ID      => 'ci_id',
	CONCEPT_BUILD_DATA_FIELD_ID     => 'cb_id',
	CONCEPT_DATA_DATA_FIELD_ID      => 'cd_id',
	CONCEPT_DATA_INFO_DATA_FIELD_ID => 'cdi_id',
	CONCEPT_DATA_IS_ELEMENT_DATA_FIELD_ID => 'is_element',

	CONCEPT_DATA_COLOR_DATA_FIELD_ID => 'color',
	CONCEPT_DATA_OPACITY_DATA_FIELD_ID => 'opacity',
	CONCEPT_DATA_VISIBLE_DATA_FIELD_ID => 'visible',
	CONCEPT_DATA_SELECTED_DATA_FIELD_ID => 'selected',
	CONCEPT_DATA_DISABLED_DATA_FIELD_ID => 'disabled',
	CONCEPT_DATA_PICKED_DATA_FIELD_ID => 'picked',
	CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID => 'picked_type',
	CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID => 'picked_order',
	CONCEPT_DATA_PICKED_TYPE_ITEMS => 'items',
	CONCEPT_DATA_PICKED_TYPE_TAGS => 'tags',
	CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID => 'selected_pick',
	CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID => 'selected_tag',
	CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID => 'selected_word_tag',
	CONCEPT_DATA_SELECTED_SEGMENT_TAG_DATA_FIELD_ID => 'selected_segment_tag',
	CONCEPT_DATA_SELECTED_CATEGORY_TAG_DATA_FIELD_ID => 'selected_category_tag',

	CONCEPT_DATA_CATEGORY_DATA_FIELD_ID => 'category',

	CONCEPT_DATA_RELATION_DATA_FIELD_ID => 'relation',

	IS_PIBLISH_DATA_FIELD_ID      => 'mv_publish',

	MODEL_DATA_FIELD_ID           => 'md_id',
	MODEL_VERSION_DATA_FIELD_ID   => 'mv_id',
	MODEL_REVISION_DATA_FIELD_ID  => 'mr_id',

	BUILDUP_TREE_DEPTH_FIELD_ID  => 'depth',
	VERSION_STRING_FIELD_ID  => 'version',
	VERSION_ORDER_FIELD_ID  => 'order',
	VERSION_PORT_FIELD_ID  => 'port',
	RENDERER_VERSION_STRING_FIELD_ID  => 'renderer_version',
	USE_FOR_BOUNDING_BOX_FIELD_ID  => 'UseForBoundingBoxFlag',
	PART_REPRESENTATION => 'PartRepresentation',
	PART_WIREFRAME_COLOR => 'PartWireframeColor',

	ID_DATA_FIELD_ID              => LOCATION_HASH_ID_KEY,
	ID_DATA_FIELD_WIDTH           => 100,
	IDS_DATA_FIELD_ID             => LOCATION_HASH_IDS_KEY,
	NAME_DATA_FIELD_ID            => LOCATION_HASH_NAME_KEY,
	NAME_J_DATA_FIELD_ID            => 'name_j',
	SYNONYM_DATA_FIELD_ID         => 'synonym',
	DEFINITION_DATA_FIELD_ID      => 'definition',
	TA_DATA_FIELD_ID            => 'ta',

	TERM_ID_DATA_FIELD_ID         => 'term_id',
	TERM_NAME_DATA_FIELD_ID       => 'term_name',

	SNIPPET_ID_DATA_FIELD_ID      => 'snippet_id',
	SNIPPET_NAME_DATA_FIELD_ID    => 'snippet_name',
	SNIPPET_SYNONYM_DATA_FIELD_ID => 'snippet_synonym',

	OBJ_PATH_NAME => 'art_file',
	OBJ_EXT_NAME => '.obj',
	OBJ_ID_DATA_FIELD_ID => 'art_id',
	OBJ_IDS_DATA_FIELD_ID => 'art_ids',
	OBJ_URL_DATA_FIELD_ID => 'url',
	OBJ_TIMESTAMP_DATA_FIELD_ID => 'art_timestamp',
	OBJ_FILENAME_FIELD_ID => 'art_filename',
	OBJ_X_MASS_CENTER_FIELD_ID => 'art_xmasscenter',
	OBJ_Y_MASS_CENTER_FIELD_ID => 'art_ymasscenter',
	OBJ_Z_MASS_CENTER_FIELD_ID => 'art_zmasscenter',
	OBJ_MASS_CENTER_IN_SELF_FIELD_ID => 'art_masscenter_in_self',

	OBJ_NAME_FIELD_ID => 'art_name',
	OBJ_EXT_FIELD_ID => 'art_ext',
	OBJ_DATA_SIZE_FIELD_ID => 'art_data_size',

	OBJ_COMMENT_FIELD_ID => 'art_comment',
	OBJ_CATEGORY_FIELD_ID => 'art_category',
	OBJ_JUDGE_FIELD_ID => 'art_judge',
	OBJ_CLASS_FIELD_ID => 'art_class',

	OBJ_CONCEPT_ID_DATA_FIELD_ID => 'artc_id',

	OBJ_THUMBNAIL_PATH_FIELD_ID => 'thumbnail_path',

	CONCEPT_OBJ_MAP_PART_ID_FIELD_ID => 'cmp_id',
	CONCEPT_OBJ_MAP_ENTRY_FIELD_ID => 'cm_entry',

	SEGMENT_COLOR_FIELD_ID => 'seg_color',


	OBJ_SEGMENT_ID_FIELD_ID => 'arts_id',
	OBJ_SEGMENT_NAME_FIELD_ID => 'arts_name',
	OBJ_SEGMENT_GROUP_ID_FIELD_ID => 'artsg_id',
	OBJ_SEGMENT_GROUP_NAME_FIELD_ID => 'artsg_name',

	OBJ_POLYS_FIELD_ID => 'art_polys',
	OBJ_VOLUME_FIELD_ID => 'art_volume',

	OBJ_X_MIN_FIELD_ID    => 'art_xmin',
	OBJ_X_MAX_FIELD_ID    => 'art_xmax',
	OBJ_Y_MIN_FIELD_ID    => 'art_ymin',
	OBJ_Y_MAX_FIELD_ID    => 'art_ymax',
	OBJ_Z_MIN_FIELD_ID    => 'art_zmin',
	OBJ_Z_MAX_FIELD_ID    => 'art_zmax',

	OBJ_X_CENTER_FIELD_ID => 'art_xcenter',
	OBJ_Y_CENTER_FIELD_ID => 'art_ycenter',
	OBJ_Z_CENTER_FIELD_ID => 'art_zcenter',

	OBJ_POINTS_FIELD_ID => 'art_points',
	OBJ_CITIES_FIELD_ID => 'art_cities',
	OBJ_PREFECTURES_FIELD_ID => 'art_prefectures',

	SEGMENT_DATA_FIELD_ID => 'segment',
	SEGMENT_ID_DATA_FIELD_ID => 'segment_id',
	SEGMENT_ORDER_DATA_FIELD_ID => 'segment_order',
	SYSTEM_ID_DATA_FIELD_ID  => 'system_id',
	SYSTEM10_ID_DATA_FIELD_ID  => 'system10_id',
	SYSTEM10_NAME_DATA_FIELD_ID  => 'system10_name',

	DISTANCE_FIELD_ID  => 'distance_voxel',
	VOXEL_RANGE_FIELD_ID  => 'voxel_range',
	CONDITIONS_FIELD_ID  => 'conditions',
	OBJ_POINT_FIELD_ID  => 'art_point',
	TARGET_RECORD_FIELD_ID => 'target_record',
	EXISTS_PALETTE_FIELD_ID => 'exists_palette',

	CDS_DATA_FIELD_ID          => 'cds',
	CDS_NAME_DATA_FIELD_ID      => 'synonym',
	CDS_BASE_NAME_DATA_FIELD_ID => 'base_synonym',
	CDS_BASE_ID_DATA_FIELD_ID   => 'base_id',
	CDS_ADDED_DATA_FIELD_ID     => 'added',

#	COLOR_COLUMN_WIDTH => 52
	COLOR_COLUMN_WIDTH => 32
};
use constant {
	CONCEPT_DATA_INFO_ID_FIELD_ID => CONCEPT_DATA_INFO_DATA_FIELD_ID,
	CONCEPT_DATA_INFO_NAME_FIELD_ID => LOCATION_HASH_ID_KEY,
	CONCEPT_DATA_INFO_NAME_E_FIELD_ID => LOCATION_HASH_NAME_KEY,
};
use constant {
	PIN_ID_FIELD_ID => 'uuid',
	PIN_NO_FIELD_ID => 'no',

	PIN_COORDINATE_X_FIELD_ID => 'coordinate_x',
	PIN_COORDINATE_Y_FIELD_ID => 'coordinate_y',
	PIN_COORDINATE_Z_FIELD_ID => 'coordinate_z',

	PIN_VECTOR_X_FIELD_ID => 'vector_x',
	PIN_VECTOR_Y_FIELD_ID => 'vector_y',
	PIN_VECTOR_Z_FIELD_ID => 'vector_z',

	PIN_UP_VECTOR_X_FIELD_ID => 'up_vector_x',
	PIN_UP_VECTOR_Y_FIELD_ID => 'up_vector_y',
	PIN_UP_VECTOR_Z_FIELD_ID => 'up_vector_z',

	PIN_DESCRIPTION_DRAW_FLAG_FIELD_ID => 'description_draw_flag',
	PIN_DESCRIPTION_COLOR_FIELD_ID => 'description_color',
	PIN_DESCRIPTION_FIELD_ID => 'description',

	PIN_COLOR_FIELD_ID => CONCEPT_DATA_COLOR_DATA_FIELD_ID,
	PIN_SHAPE_FIELD_ID => 'shape',
	PIN_SIZE_FIELD_ID => 'size',
	PIN_COORDINATE_SYSTEM_NAME_FIELD_ID => 'coordinate_system_name',

	PIN_PART_ID_FIELD_ID => ID_DATA_FIELD_ID,
	PIN_PART_NAME_FIELD_ID => NAME_DATA_FIELD_ID,

	PIN_VISIBLE_FIELD_ID => CONCEPT_DATA_VISIBLE_DATA_FIELD_ID,
};

our $BASE_PATH   = qq|/opt/services/ag/|.APP_NAME;
our $HTDOCS_PATH = &catdir($BASE_PATH,'htdocs');
our $UPLOAD_PATH = &catdir($BASE_PATH,'uploads');
our $ART_FILE_PATH = &catdir($HTDOCS_PATH,OBJ_PATH_NAME);
our $BIN_PATH    = &catdir($BASE_PATH,'local','usr','bin');

1;
