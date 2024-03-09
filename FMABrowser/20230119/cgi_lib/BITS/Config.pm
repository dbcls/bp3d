package BITS::Config;

use strict;
use warnings;
use feature ':5.10';

use Exporter;
use File::Spec::Functions qw/:ALL/;
use File::Basename;
use Cwd qw/abs_path realpath/;

use constant {
	DEBUG => exists $ENV{'AG_DEBUG'} && defined $ENV{'AG_DEBUG'} && $ENV{'AG_DEBUG'} eq '1' ? 1 : 0,
	USE_HTML5 => 1,
	USE_APPCACHE => 0,

#	USE_ONLY_MAP_TERMS => 1,	#サムネイル作成時にTermにマップされているOBJのみを使用する（従来のサムネイルを作成する場合は、undefを指定する）
	USE_ONLY_MAP_TERMS => undef,	#サムネイル作成時にTermにマップされているOBJのみを使用する（従来のサムネイルを作成する場合は、undefを指定する）

	USE_OBJ_TIMESTAMP_COMPARISON_UNIT_DATE => 'date', # date or time
	USE_OBJ_TIMESTAMP_COMPARISON_UNIT_TIME => 'time', # date or time
};
use constant {
	LOCATION_HASH_CIID_KEY   => 'ci',
	LOCATION_HASH_CBID_KEY   => 'cb',
	LOCATION_HASH_ID_KEY     => 'id',
	LOCATION_HASH_NAME_KEY   => 'name',
	LOCATION_HASH_SEARCH_KEY => 'query',

	SEARCH_ANY_MATCH_NAME      => 'anyMatch',
	SEARCH_CASE_SENSITIVE_NAME => 'caseSensitive',
	RELATION_TYPE_NAME         => 'type',

	USE_OBJ_TIMESTAMP_COMPARISON_UNIT => USE_OBJ_TIMESTAMP_COMPARISON_UNIT_TIME
};
use constant {
	CONCEPT_INFO_DATA_FIELD_ID    => 'ci_id',
	CONCEPT_BUILD_DATA_FIELD_ID   => 'cb_id',

	ID_DATA_FIELD_ID              => LOCATION_HASH_ID_KEY,
	NAME_DATA_FIELD_ID            => LOCATION_HASH_NAME_KEY,
	SYNONYM_DATA_FIELD_ID         => 'synonym',
	DEFINITION_DATA_FIELD_ID      => 'definition',

	TERM_ID_DATA_FIELD_ID         => 'term_id',
	TERM_NAME_DATA_FIELD_ID       => 'term_name',

	SNIPPET_ID_DATA_FIELD_ID      => 'snippet_id',
	SNIPPET_NAME_DATA_FIELD_ID    => 'snippet_name',
	SNIPPET_SYNONYM_DATA_FIELD_ID => 'snippet_synonym',

	IS_SHAPE_FIELD_ID             => 'is_shape',
	IS_MAPED_FIELD_ID             => 'is_maped',
	IS_CURRENT_FIELD_ID           => 'is_current',
};

#say STDERR &abs_path(&catdir(&dirname(__FILE__),'..','..'));

our $BASE_PATH   = &abs_path(&catdir(&dirname(__FILE__),'..','..'));
our $HTDOCS_PATH = &catdir($BASE_PATH,'htdocs');
our $UPLOAD_PATH = &catdir($BASE_PATH,'uploads');
our $BIN_PATH    = &catdir($BASE_PATH,'local','usr','bin');

#say STDERR $HTDOCS_PATH;

1;
