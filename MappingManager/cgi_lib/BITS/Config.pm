package BITS::Config;

use strict;
use warnings;
use feature ':5.10';

use Exporter;
use File::Spec::Functions;

use constant {
	DEBUG => 1,
	USE_HTML5 => 1,
	USE_APPCACHE => 0,

#	USE_ONLY_MAP_TERMS => 1,	#サムネイル作成時にTermにマップされているOBJのみを使用する（従来のサムネイルを作成する場合は、undefを指定する）
	USE_ONLY_MAP_TERMS => undef,	#サムネイル作成時にTermにマップされているOBJのみを使用する（従来のサムネイルを作成する場合は、undefを指定する）

	USE_OBJ_TIMESTAMP_COMPARISON_UNIT_DATE => 'date', # date or time
	USE_OBJ_TIMESTAMP_COMPARISON_UNIT_TIME => 'time', # date or time
};
use constant {
	USE_OBJ_TIMESTAMP_COMPARISON_UNIT => USE_OBJ_TIMESTAMP_COMPARISON_UNIT_TIME
};

our $BASE_PATH   = qq|/bp3d/MappingManager|;
our $HTDOCS_PATH = &catdir($BASE_PATH,'htdocs');
our $UPLOAD_PATH = &catdir($BASE_PATH,'uploads');
our $BIN_PATH    = &catdir($BASE_PATH,'local','usr','bin');

1;
