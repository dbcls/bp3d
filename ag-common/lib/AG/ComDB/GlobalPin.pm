package AG::ComDB::GlobalPin;

use base qw/AG::ComDB/;
#use base qw/Exporter AG::ComDB/;
#use vars qw /@EXPORT/;
#@EXPORT = qw/CMD_ADDING CMD_EXCLUSION CMD_UPDATE CMD_GET CMD_SEARCH TYPE_PIN TYPE_PINGROUP true false/;

use strict;
use Digest::MD5 qw(md5_hex);
use JSON::XS;
use Carp;
#use DBI qw(:sql_types);
use DBI qw(:sql_types :utils);

use Readonly;
Readonly::Array my @COLUMN_NAMES_DB_PINGROUP_CONV => qw/gpg_id gpg_color gpg_desc gpg_desccolor gpg_descflag gpg_numflag gpg_shape gpg_size gpg_value gpg_apifadd gpg_apifexc gpg_apifref gpg_fsearch gp_count/;
Readonly::Array my @COLUMN_NAMES_JS_PINGROUP_CONV => qw/PinGroupID PinGroupPinColor PinGroupDescription PinGroupPinDescriptionColor PinGroupPinDescriptionDrawFlag PinGroupPinNumberDrawFlag PinGroupPinShape PinGroupPinSize PinGroupValue PinGroupApiAdding PinGroupApiExclusion PinGroupApiReference PinGroupSearch PinCount/;

Readonly::Array my @COLUMN_NAMES_DB_PINGROUP_EDIT => qw/gpg_id gpg_color gpg_desc gpg_desccolor gpg_descflag gpg_numflag gpg_shape gpg_size gpg_value gpg_apifadd gpg_apifexc gpg_apifref gpg_fsearch/;
Readonly::Array my @COLUMN_NAMES_DB_PINGROUP_REF  => qw/gpg_id gpg_color gpg_desc gpg_desccolor gpg_descflag gpg_numflag gpg_shape gpg_size gpg_value gpg_apifadd gpg_apifexc gpg_apifref gpg_fsearch gp_count/;
Readonly::Array my @COLUMN_NAMES_DB_PINGROUP_ATTR => qw/gpg_apifadd gpg_apifexc gpg_apifref gpg_fsearch/;

Readonly::Array my @COLUMN_NAMES_DB_PINGROUP_ADD => qw/gpg_color gpg_desc gpg_desccolor gpg_descflag gpg_numflag gpg_shape gpg_size gpg_value gpg_apifadd gpg_apifexc gpg_apifref gpg_fsearch gpg_openid/;
Readonly::Array my @COLUMN_NAMES_DB_PINGROUP_UPD => qw/gpg_color gpg_desc gpg_desccolor gpg_descflag gpg_numflag gpg_shape gpg_size gpg_value gpg_apifadd gpg_apifexc gpg_apifref gpg_fsearch/;



Readonly::Array my @COLUMN_NAMES_DB_PIN_CONV => qw/gp_id gp_x gp_y gp_z gp_avx gp_avy gp_avz gp_uvx gp_uvy gp_uvz gp_color gp_desccolor gp_numflag gp_descflag gp_shape gp_size gp_coorsysname gp_partid gp_partname gp_desc gp_version gp_value gp_radius/;
Readonly::Array my @COLUMN_NAMES_JS_PIN_CONV => qw/PinID PinX PinY PinZ PinArrowVectorX PinArrowVectorY PinArrowVectorZ PinUpVectorX PinUpVectorY PinUpVectorZ PinColor PinDescriptionColor PinNumberDrawFlag PinDescriptionDrawFlag PinShape PinSize PinCoordinateSystemName PinPartID PinPartName PinDescription Version PinValue PinRadius/;

Readonly::Array my @COLUMN_NAMES_DB_PIN_GET => qw/gp_id gp_x gp_y gp_z gp_avx gp_avy gp_avz gp_uvx gp_uvy gp_uvz gp_color gp_desccolor gp_numflag gp_descflag gp_shape gp_size gp_coorsysname gp_partid gp_partname gp_desc gp_version gp_value/;
Readonly::Array my @COLUMN_NAMES_DB_PIN_ADD =>       qw/gp_x gp_y gp_z gp_avx gp_avy gp_avz gp_uvx gp_uvy gp_uvz gp_color gp_desccolor gp_numflag gp_descflag gp_shape gp_size gp_coorsysname gp_partid gp_partname gp_desc gp_version gp_value gp_openid/;
Readonly::Array my @COLUMN_NAMES_DB_PIN_UPD =>       qw/gp_x gp_y gp_z gp_avx gp_avy gp_avz gp_uvx gp_uvy gp_uvz gp_color gp_desccolor gp_numflag gp_descflag gp_shape gp_size gp_coorsysname gp_partid gp_partname gp_desc gp_version gp_value/;

use constant {
	DEBUG => 0,
	DEBUG_PRINT => 0,
	DEBUG_WARN => 0,

#	PINID_PREFIX => 'PIN',
#	GRPPINID_PREFIX => 'GPIN',

	true => JSON::XS::true,#1,
	false => JSON::XS::false,#0,

	CMD_ADDING => 1,
	CMD_EXCLUSION => 2,
	CMD_UPDATE => 3,
	CMD_GET => 4,
	CMD_GET_ATTR => 5,
	CMD_GET_LIST => 6,
	CMD_SEARCH => 7,
	CMD_AUTH => 8,

	TYPE_PIN => 1,
	TYPE_PINGROUP => 2,

	TABLE_NAME_PIN => 'global_pin',
	TABLE_NAME_PINGROUP => 'global_pin_group',
};

use AG::DB;

sub test {
#	print "1\n" if defined $column_names_db[0];
#	print __PACKAGE__.":".__LINE__.":",(scalar @column_names_db),":",$column_names_db[1],"\n";
#	print __PACKAGE__.":".__LINE__.":",(scalar column_names_db),":",column_names_db->[1],"\n";
#	push @column_names_db,"test";
}

=pod
-- ピンとピングループの対応テーブル
DROP TABLE IF EXISTS global_pin2group;

-- ピン
DROP TABLE IF EXISTS global_pin;
DROP SEQUENCE IF EXISTS global_pin_gp_id_seq;

CREATE SEQUENCE global_pin_gp_id_seq;
CREATE TABLE global_pin (
  gp_id           text         NOT NULL CHECK (gp_id <> '') DEFAULT 'PN'||nextval('global_pin_gp_id_seq'::regclass),

  gp_x            numeric(9,4) NOT NULL,                                                       -- Pinの3次元空間上x座標  Double  
  gp_y            numeric(9,4) NOT NULL,                                                       -- Pinの3次元空間上y座標  Double  
  gp_z            numeric(9,4) NOT NULL,                                                       -- Pinの3次元空間上z座標  Double  
  gp_avx          numeric(9,4) NOT NULL,                                                       -- Pinのベクトルx要素  Double  
  gp_avy          numeric(9,4) NOT NULL,                                                       -- Pinのベクトルy要素  Double  
  gp_avz          numeric(9,4) NOT NULL,                                                       -- Pinのベクトルz要素  Double  
  gp_uvx          numeric(9,4) NOT NULL,                                                       -- PinのUpベクトルx要素  Double  
  gp_uvy          numeric(9,4) NOT NULL,                                                       -- PinのUpベクトルy要素  Double  
  gp_uvz          numeric(9,4) NOT NULL,                                                       -- PinのUpベクトルz要素  Double  
  gp_color        text         NOT NULL CHECK (gp_color ~ '[A-F0-9]{6}') DEFAULT 'FFFFFF',     -- Pinの描画色RGB(16進6桁)  文字列  
  gp_desccolor    text         NOT NULL CHECK (gp_desccolor ~ '[A-F0-9]{6}') DEFAULT 'FFFFFF', -- デスクリプション描画色RGB(16進6桁）  文字列  
  gp_numflag      boolean      NOT NULL DEFAULT true,                                          -- PinのID描画フラグ  Boolean  
  gp_descflag     boolean      NOT NULL DEFAULT false,                                         -- Pinのデスクリプション描画フラグ  Boolean  
  gp_shape        text,                                                                        -- Pin形状  文字列  
  gp_size         numeric(4,1) NOT NULL DEFAULT 10.0,                                          -- Pinのサイズ  Double  
  gp_coorsysname  text         NOT NULL CHECK (gp_coorsysname <> '') default 'bp3d',           -- Pin作成時座標系  文字列  
  gp_partid       text,                                                                        -- Pinが打たれているパーツのID（文字列）
  gp_partname     text,                                                                        -- Pinが打たれているパーツの名称（文字列）
  gp_desc         text,                                                                        -- Pinのデスクリプション  文字列  

  gp_version      text         NOT NULL CHECK (gp_version <> ''),                              -- Pin作成時バージョン  文字列  
  gp_value        text,                                                                        -- Pin値  文字列  

  gp_delcause     text,                                                                        -- Pin削除理由  文字列  
  gp_entry        timestamp without time zone NOT NULL default now(),                          -- Pin登録日時  タイムスタンプ
  gp_modified     timestamp without time zone NOT NULL default now(),                          -- Pin更新日時  タイムスタンプ
  gp_openid       text,                                                                        -- Pin登録OpenID  文字列  
  PRIMARY KEY (gp_id)
);
CREATE INDEX global_pin_gp_desc_idx ON global_pin USING btree (gp_desc);
CREATE INDEX global_pin_gp_partid_idx ON global_pin USING btree (gp_partid);
CREATE INDEX global_pin_gp_partname_idx ON global_pin USING btree (gp_partname);
CREATE INDEX global_pin_gp_x_idx ON global_pin USING btree (gp_x);
CREATE INDEX global_pin_gp_y_idx ON global_pin USING btree (gp_y);
CREATE INDEX global_pin_gp_z_idx ON global_pin USING btree (gp_z);
CREATE INDEX global_pin_gp_version_idx ON global_pin USING btree (gp_version);
CREATE INDEX global_pin_gp_openid_idx ON global_pin USING btree (gp_openid);

SELECT setval('global_pin_gp_id_seq',1,false);

DROP TRIGGER IF EXISTS trig_before_global_pin ON global_pin;
DROP FUNCTION IF EXISTS func_before_global_pin();
CREATE OR REPLACE FUNCTION func_before_global_pin() RETURNS trigger AS $$
#  elog(LOG,qq|[$_TD->{table_name}][$_TD->{event}][$_TD->{when}][$_TD->{level}]|);
  my $rtn;
  if($_TD->{event} eq 'INSERT'){
#    $rtn = qq|SKIP| unless(defined $_TD->{new}{gp_serial});
#    unless(defined $_TD->{new}{gp_serial}){
#      my $rv = spi_exec_query(qq|select nextval('global_pin_gp_serial_seq'::regclass) as gp_serial|,1);
#      $_TD->{new}{gp_serial} = int($rv->{rows}[0]->{gp_serial});
#    }
#    unless(defined $_TD->{new}{gp_id}){
#      $_TD->{new}{gp_id} = sprintf(qq|%s%d|,'PN',$_TD->{new}{gp_serial});
#      $rtn = 'MODIFY';
#    }
  }elsif($_TD->{event} eq 'UPDATE'){
  }
  unless($rtn eq qq|SKIP|){
    if(defined $_TD->{new}{gp_color}){
      my $color = $_TD->{new}{gp_color};
      $color =~ s/^#//g;
      $color =~ s/^0x//g;
      if(($color =~ /^[A-Z0-9]{6}$/i || $color =~ /^[A-Z0-9]{3}$/i) && $color =~ /^([A-Z0-9]{1,2})([A-Z0-9]{1,2})([A-Z0-9]{1,2})$/i){
        my $color = $1;
        $color .= $1 if(length($1)==1);
        $color .= $2;
        $color .= $2 if(length($2)==1);
        $color .= $3;
        $color .= $3 if(length($3)==1);
        if($_TD->{new}{gp_color} ne uc($color)){
          $_TD->{new}{gp_color} = uc($color);
          $rtn = 'MODIFY';
        }
        undef $color;
      }
      undef $color;
    }else{
      $rtn = qq|SKIP|;
    }
  }
  unless($rtn eq qq|SKIP|){
    if(defined $_TD->{new}{gp_desccolor}){
      my $color = $_TD->{new}{gp_color};
      $color =~ s/^#//g;
      $color =~ s/^0x//g;
      if(($color =~ /^[A-Z0-9]{6}$/i || $color =~ /^[A-Z0-9]{3}$/i) && $color =~ /^([A-Z0-9]{1,2})([A-Z0-9]{1,2})([A-Z0-9]{1,2})$/i){
        my $color = $1;
        $color .= $1 if(length($1)==1);
        $color .= $2;
        $color .= $2 if(length($2)==1);
        $color .= $3;
        $color .= $3 if(length($3)==1);
        if($_TD->{new}{gp_desccolor} ne uc($color)){
          $_TD->{new}{gp_desccolor} = uc($color);
          $rtn = 'MODIFY';
        }
        undef $color;
      }
      undef $color;
    }else{
      $rtn = qq|SKIP|;
    }
  }
  if(defined $rtn){
#    elog(LOG,qq|[$_TD->{table_name}][$_TD->{event}][$_TD->{when}][$_TD->{level}][$rtn]|);
    return $rtn;
  }else{
#    elog(LOG,qq|[$_TD->{table_name}][$_TD->{event}][$_TD->{when}][$_TD->{level}][]|);
    return;
  }
$$ LANGUAGE plperl;

CREATE TRIGGER trig_before_global_pin
  BEFORE INSERT OR UPDATE ON global_pin
  FOR EACH ROW EXECUTE PROCEDURE func_before_global_pin();


-- ピングループ
DROP TABLE IF EXISTS global_pin_group;
DROP SEQUENCE IF EXISTS global_pin_group_gpg_id_seq;
CREATE SEQUENCE global_pin_group_gpg_id_seq;
CREATE TABLE global_pin_group (
  gpg_id           text         NOT NULL CHECK (gpg_id <> '') DEFAULT 'PNG'||nextval('global_pin_group_gpg_id_seq'::regclass),

  gpg_color        text         NOT NULL CHECK (gpg_color ~ '[A-F0-9]{6}') DEFAULT 'FFFFFF',    -- ピングループの描画色RGB(16進6桁)  文字列  
  gpg_desc         text,                                                                        -- ピングループのデスクリプション  文字列  
  gpg_desccolor    text         NOT NULL CHECK (gpg_desccolor ~ '[A-F0-9]{6}') DEFAULT 'FFFFFF',-- ピングループのデスクリプション描画色RGB(16進6桁）  文字列  
  gpg_descflag     boolean      NOT NULL DEFAULT false,                                         -- ピングループのデスクリプション描画フラグ  Boolean  

  gpg_numflag      boolean      NOT NULL DEFAULT true,                                          -- PinのID描画フラグ  Boolean  
  gpg_shape        text,                                                                        -- Pin形状  文字列  
  gpg_size         numeric(4,1) NOT NULL DEFAULT 10.0,                                          -- Pinのサイズ  Double  

  gpg_value        text,                                                                        -- ピングループ値  文字列  
  gpg_apifadd      boolean      NOT NULL DEFAULT false,                                         -- ピングループのAPI経由のピン操作フラグ（追加）Boolean  
  gpg_apifexc      boolean      NOT NULL DEFAULT false,                                         -- ピングループのAPI経由のピン操作フラグ（除外）Boolean  
  gpg_apifref      boolean      NOT NULL DEFAULT false,                                         -- ピングループのAPI経由のピン操作フラグ（対応ピン情報の参照）Boolean  
  gpg_fsearch      boolean      NOT NULL DEFAULT false,                                         -- ピングループの検索可否フラグ Boolean  

  gpg_delcause     text,                                                                        -- ピングループの削除理由  文字列  
  gpg_entry        timestamp without time zone NOT NULL default now(),                          -- ピングループの登録日時  タイムスタンプ
  gpg_modified     timestamp without time zone NOT NULL default now(),                          -- ピングループの更新日時  タイムスタンプ
  gpg_openid       text         NOT NULL CHECK (gpg_openid <> ''),                              -- ピングループの登録OpenID  文字列  
  PRIMARY KEY (gpg_id)
);
CREATE INDEX global_pin_group_gpg_desc_idx ON global_pin_group USING btree (gpg_desc);
CREATE INDEX global_pin_group_gpg_apifadd_idx ON global_pin_group USING btree (gpg_apifadd);
CREATE INDEX global_pin_group_gpg_apifexc_idx ON global_pin_group USING btree (gpg_apifexc);
CREATE INDEX global_pin_group_gpg_apifref_idx ON global_pin_group USING btree (gpg_apifref);
CREATE INDEX global_pin_group_gpg_fsearch_idx ON global_pin_group USING btree (gpg_fsearch);
CREATE INDEX global_pin_group_gpg_openid_idx ON global_pin_group USING btree (gpg_openid);
--ALTER TABLE global_pin_group ALTER gpg_id SET DEFAULT 'PNG'||nextval('global_pin_group_gpg_id_seq'::regclass);
SELECT setval('global_pin_group_gpg_id_seq',1,false);

DROP TRIGGER IF EXISTS trig_before_global_pin_group ON global_pin_group;
DROP FUNCTION IF EXISTS func_before_global_pin_group();
CREATE OR REPLACE FUNCTION func_before_global_pin_group() RETURNS trigger AS $$
#  elog(LOG,qq|[$_TD->{table_name}][$_TD->{event}][$_TD->{when}][$_TD->{level}]|);
  my $rtn;
  if($_TD->{event} eq 'INSERT'){
#    $rtn = qq|SKIP| unless(defined $_TD->{new}{gpg_serial});
#    unless($rtn eq qq|SKIP|){
#      unless(defined $_TD->{new}{gpg_id}){
#        $_TD->{new}{gpg_id} = sprintf(qq|%s%d|,'PNG',$_TD->{new}{gpg_serial});
#        $rtn = 'MODIFY';
#      }
#    }
  }
  unless($rtn eq qq|SKIP|){
    if(defined $_TD->{new}{gpg_color}){
      my $color = $_TD->{new}{gpg_color};
      $color =~ s/^#//g;
      $color =~ s/^0x//g;
      if(($color =~ /^[A-Z0-9]{6}$/i || $color =~ /^[A-Z0-9]{3}$/i) && $color =~ /^([A-Z0-9]{1,2})([A-Z0-9]{1,2})([A-Z0-9]{1,2})$/i){
        my $color = $1;
        $color .= $1 if(length($1)==1);
        $color .= $2;
        $color .= $2 if(length($2)==1);
        $color .= $3;
        $color .= $3 if(length($3)==1);
        if($_TD->{new}{gpg_color} ne uc($color)){
          $_TD->{new}{gpg_color} = uc($color);
          $rtn = 'MODIFY';
        }
        undef $color;
      }
      undef $color;
    }else{
      $rtn = qq|SKIP|;
    }
  }
  unless($rtn eq qq|SKIP|){
    if(defined $_TD->{new}{gpg_desccolor}){
      my $color = $_TD->{new}{gp_color};
      $color =~ s/^#//g;
      $color =~ s/^0x//g;
      if(($color =~ /^[A-Z0-9]{6}$/i || $color =~ /^[A-Z0-9]{3}$/i) && $color =~ /^([A-Z0-9]{1,2})([A-Z0-9]{1,2})([A-Z0-9]{1,2})$/i){
        my $color = $1;
        $color .= $1 if(length($1)==1);
        $color .= $2;
        $color .= $2 if(length($2)==1);
        $color .= $3;
        $color .= $3 if(length($3)==1);
        if($_TD->{new}{gpg_desccolor} ne uc($color)){
          $_TD->{new}{gpg_desccolor} = uc($color);
          $rtn = 'MODIFY';
        }
        undef $color;
      }
      undef $color;
    }else{
      $rtn = qq|SKIP|;
    }
  }
  if(defined $rtn){
#    elog(LOG,qq|[$_TD->{table_name}][$_TD->{event}][$_TD->{when}][$_TD->{level}][$rtn]|);
    return $rtn;
  }else{
#    elog(LOG,qq|[$_TD->{table_name}][$_TD->{event}][$_TD->{when}][$_TD->{level}][]|);
    return;
  }
$$ LANGUAGE plperl;

CREATE TRIGGER trig_before_global_pin_group
  BEFORE INSERT ON global_pin_group
  FOR EACH ROW EXECUTE PROCEDURE func_before_global_pin_group();


-- ピンとピングループの対応テーブル
DROP TABLE IF EXISTS global_pin2group;
CREATE TABLE global_pin2group (
  gpg_id        text NOT NULL CHECK (gpg_id <> ''),
  gp_id         text NOT NULL CHECK (gp_id <> ''),
  p2g_delcause  text,                                                                        -- 対応の削除理由  文字列  
  p2g_entry     timestamp without time zone NOT NULL default now(),                          -- 対応の登録日時  タイムスタンプ
  p2g_openid    text,                                                                        -- 対応の登録OpenID  文字列  
  PRIMARY KEY (gpg_id,gp_id),
  FOREIGN KEY (gpg_id) REFERENCES global_pin_group (gpg_id) ON DELETE CASCADE,
  FOREIGN KEY (gp_id) REFERENCES global_pin (gp_id) ON DELETE CASCADE
);


--select attname from pg_attribute as pg left join (select typname,typelem from pg_type) as pt on pt.typelem=pg.atttypid where attnum > 0 and attrelid = (select relfilenode from pg_class where relname = 'global_pin') and pt.typname='_numeric';

DELETE FROM global_pin;
DELETE FROM global_pin_group;
SELECT setval('global_pin_gp_id_seq',1,false);
SELECT setval('global_pin_group_gpg_id_seq',1,false);

=cut

#sub new {
#	my $class = shift;
#	my %args = @_;
#	my $self = new AG::ComDB(%args);
#	return bless $self, $class;
#}

sub error {
	my $self = shift;
	return $self->{_error};
}
sub _set_error {
	my $self = shift;
	my $msg = shift;
	$self->{_error} = $msg;
}
sub _clear_error {
	my $self = shift;
	$self->{_error} = undef;
}

sub _cast_type {
	my $self = shift;
	my $table_name = shift;
	my $hash = shift;
	return unless(defined $table_name && defined $hash && (ref $hash eq 'HASH' || ref $hash eq 'ARRAY'));
	my $dbh = $self->get_dbh();
	my $sth = $dbh->prepare(qq|select attname from pg_attribute as pg left join (select typname,typelem from pg_type) as pt on pt.typelem=pg.atttypid where attnum > 0 and attrelid = (select relfilenode from pg_class where relname = '$table_name') and pt.typname='_numeric'|) or &Carp::croak(DBI->errstr());
	$sth->execute() or &Carp::croak(DBI->errstr());
	if($sth->rows>0){
		my $attname;
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$attname, undef);
		while($sth->fetch){
			if(ref $hash eq 'HASH'){
				next unless(exists $hash->{$attname} && defined $hash->{$attname});
				$hash->{$attname} += 0 if(DBI::sql_type_cast($hash->{$attname}, SQL_DOUBLE, DBIstcf_DISCARD_STRING)==2);
			}elsif(ref $hash eq 'ARRAY'){
				foreach my $h (@$hash){
					next unless(ref $h eq 'HASH');
					next unless(exists $h->{$attname} && defined $h->{$attname});
					$h->{$attname} += 0 if(DBI::sql_type_cast($h->{$attname}, SQL_DOUBLE, DBIstcf_DISCARD_STRING)==2);
				}
			}
		}
	}
	$sth->finish;
	undef $sth;

	my $sth = $dbh->prepare(qq|select attname from pg_attribute as pg left join (select typname,typelem from pg_type) as pt on pt.typelem=pg.atttypid where attnum > 0 and attrelid = (select relfilenode from pg_class where relname = '$table_name') and pt.typname='_bool'|) or &Carp::croak(DBI->errstr());
	$sth->execute() or &Carp::croak(DBI->errstr());
	if($sth->rows>0){
		my $attname;
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$attname, undef);
		while($sth->fetch){
			if(ref $hash eq 'HASH'){
				next unless(exists $hash->{$attname} && defined $hash->{$attname});
				$hash->{$attname} = $hash->{$attname} ? JSON::XS::true : JSON::XS::false;
			}elsif(ref $hash eq 'ARRAY'){
				foreach my $h (@$hash){
					next unless(ref $h eq 'HASH');
					next unless(exists $h->{$attname} && defined $h->{$attname});
					$h->{$attname} = $h->{$attname} ? JSON::XS::true : JSON::XS::false;
				}
			}
		}
	}
	$sth->finish;
	undef $sth;
}

#ピングループの属性を取得
sub _get_gpg_attr {
	my $self = shift;
	my %arg = @_;

	my $json = $arg{json};
	return undef unless(defined $json && (ref $json eq 'HASH' || ref $json eq 'ARRAY'));

	my @A;
	if(ref $json eq 'HASH'){
		push(@A,$json);
	}elsif(ref $json eq 'ARRAY'){
		push(@A,@$json);
	}
	my @bind_values = map { $_->{gpg_id} } grep {defined $_->{gpg_id} && length $_->{gpg_id}} @A;
	&Carp::croak('Information necessary to refer is missing.('.__LINE__.')') unless(scalar @bind_values);
	my @bind_columns = map {'?'} @bind_values;

	my $rtn_rows;
	my $rtn_array;
	my $table_name = TABLE_NAME_PINGROUP;
	my $dbh = $self->get_dbh();
	my $sth = $dbh->prepare(qq|select gpg_id,gpg_apifadd,gpg_apifexc,gpg_apifref,gpg_fsearch,gpg_openid from $table_name where gpg_id in (|.join(',',@bind_columns).qq|)|) or &Carp::croak(DBI->errstr());
	$sth->execute(@bind_values) or &Carp::croak(DBI->errstr());
	$rtn_rows = $sth->rows;
	if($rtn_rows>0){
		while(my $hash = $sth->fetchrow_hashref){
			push(@$rtn_array,$hash) if(defined $hash);
		}
	}
	$sth->finish;
	undef $sth;
#	$self->_cast_type($table_name,$rtn_hash) if(defined $rtn_hash);
	return ($rtn_rows,$rtn_array);
}

#ピンとピングループの結び付け関数
sub _tied {
	my $self = shift;
	my %arg = (
		cmd => CMD_ADDING,# or CMD_EXCLUSION
		forcing => false,
		@_
	);

	my $json = $arg{json};
	return undef unless(defined $json && (ref $json eq 'HASH' || ref $json eq 'ARRAY'));

	$self->_convDBColumnNames($json);

	my $openid = $arg{openid};
	my $cmd = $arg{cmd};
	my $forcing = $arg{forcing};
#	$forcing = false unless($forcing == true && defined $openid && length $openid);
#	$forcing = false;

	my $rtn_rows = 0;
	$self->_clear_error();

	my $dbh = $self->get_dbh();
	$dbh->{AutoCommit} = 0;
	$dbh->{RaiseError} = 1;
	eval{
		my @A;
		if(ref $json eq 'HASH'){
			push(@A,$json);
		}elsif(ref $json eq 'ARRAY'){
			push(@A,@$json);
		}
		my $sth_ins;
		my $sth_del;
		my $sth_sel = $dbh->prepare(qq|select * from global_pin2group where gpg_id=? and gp_id=?|) or &Carp::croak(DBI->errstr());
		if($cmd == CMD_ADDING){
			$sth_ins = $dbh->prepare(qq|insert into global_pin2group (gpg_id,gp_id,p2g_entry,p2g_openid) values (?,?,'now()',?)|) or &Carp::croak(DBI->errstr());
		}elsif($cmd == CMD_EXCLUSION){
			$sth_del = $dbh->prepare(qq|delete from global_pin2group where gpg_id=? and gp_id=?|) or &Carp::croak(DBI->errstr());
		}
		foreach my $a (@A){
			my $gp_id = $a->{gp_id};
			my $gpg_id = $a->{gpg_id};

			my ($gpg_attr_rows,$gpg_attr_array) = $self->_get_gpg_attr(%arg,json=>$a);
			my $gpg_attr = $gpg_attr_array->[0];
			my ($global_pin_rows,$global_pin_array) = $self->_execute_pin_reference(%arg,json=>$a,cmd=>CMD_GET,type=>TYPE_PIN);
			my $global_pin = $global_pin_array->[0];
			if(defined $gpg_attr && defined $global_pin && ref $global_pin eq 'HASH'){
				if($cmd == CMD_ADDING){
#					$gpg_attr->{gpg_apifadd} = true if($forcing);
					if($gpg_attr->{gpg_apifadd} || $gpg_attr->{gpg_openid} eq $openid){
#					if($gpg_attr->{gpg_apifadd} || defined $openid){
						$sth_sel->execute($gpg_id,$gp_id) or &Carp::croak(DBI->errstr());
						if($sth_sel->rows()==0){
							$sth_ins->execute($gpg_id,$gp_id,$openid) or &Carp::croak(DBI->errstr());
							$rtn_rows += $sth_ins->rows();
							$sth_ins->finish;
						}
						$sth_sel->finish;
					}else{
						&Carp::croak(qq|Adding a pin is a non-permit.(|.__LINE__.')');
					}
				}
				elsif($cmd == CMD_EXCLUSION){
#					$gpg_attr->{gpg_apifexc} = true if($forcing);
					if($gpg_attr->{gpg_apifexc} || $gpg_attr->{gpg_openid} eq $openid){
#					if($gpg_attr->{gpg_apifexc} || defined $openid){
						$sth_del->execute($gpg_id,$gp_id) or &Carp::croak(DBI->errstr());
						$rtn_rows += $sth_del->rows();
						$sth_del->finish;
					}else{
						&Carp::croak(qq|Excluding pin is non-permit.(|.__LINE__.')');
					}
				}
				undef $gpg_attr;
			}else{
				unless(defined $gpg_attr){
					&Carp::croak(qq|The specified group does not exist.(|.__LINE__.')');
				}else{
					&Carp::croak(qq|Pin that is specified does not exist.(|.__LINE__.')');
				}
			}
			undef $gp_id;
			undef $gpg_id;
			undef $global_pin;
			undef $gpg_attr;
			undef $gpg_attr_rows;
			undef $gpg_attr_array;
			undef $global_pin_rows;
			undef $global_pin_array;
		}
		undef $sth_sel;
		undef $sth_ins;
		undef $sth_del;
		$dbh->commit();
	};
	if($@){
		$self->_set_error($@);
		$dbh->rollback;
		undef $rtn_rows;
	}
	$dbh->{AutoCommit} = 1;
	$dbh->{RaiseError} = 0;

	return $rtn_rows;
}

sub _execute_pin {
	my $self = shift;
	my %arg = (
		type => TYPE_PIN,
		@_
	);
	my $rows;
	my $rtn;
	return $rtn unless($arg{type} == TYPE_PIN);

	my $json = $arg{json};
	return undef unless(defined $json && (ref $json eq 'HASH' || ref $json eq 'ARRAY'));

	$arg{db_column_names} = \@COLUMN_NAMES_DB_PIN_GET;
	if($arg{cmd} == CMD_ADDING || $arg{cmd} == CMD_EXCLUSION || $arg{cmd} == CMD_UPDATE){
		&_log("",__LINE__);
		($rows,$rtn) = $self->_execute_pin_edit(%arg);
	}elsif($arg{cmd} == CMD_GET || $arg{cmd} == CMD_GET_LIST || $arg{cmd} == CMD_SEARCH){
		&_log("",__LINE__);
		($rows,$rtn) = $self->_execute_pin_reference(%arg);
	}
	return ($rows,$rtn);
}

sub _execute_pin_edit {
	my $self = shift;
	my %arg = (
		cmd => CMD_ADDING,
		type => TYPE_PIN,
		@_
	);
	&_log("",__LINE__);
	return undef unless($arg{type} == TYPE_PIN);

	my $json = $arg{json};
	return undef unless(defined $json && (ref $json eq 'HASH' || ref $json eq 'ARRAY'));

	&_log("",__LINE__);

	my $openid = $arg{openid};
	my $cmd = $arg{cmd};
	my $type = $arg{type};
	my $cookie = $arg{cookie};

	my $rtn_rows = 0;
	my $rtn_array;
	$self->_clear_error();

	my $dbh = $self->get_dbh();
	$dbh->{AutoCommit} = 0;
	$dbh->{RaiseError} = 1;
	eval{
		my $table_name = TABLE_NAME_PIN;

		&_log("\$json=[".(ref $json)."]",__LINE__);
		my @A;
		if(ref $json eq 'HASH'){
			push(@A,$json);
		}elsif(ref $json eq 'ARRAY'){
			push(@A,@$json);
		}
		&_log("\@A=[".(scalar @A)."]",__LINE__);


		my $sth_sel_cdi;
		if($cmd == CMD_ADDING || $cmd == CMD_UPDATE){
			my $ci_id = $cookie->{'ag_annotation.images.ci_id'} if(defined $cookie);
			unless(defined $ci_id){
				my $sth_sel = $dbh->prepare(qq|select ci_id from dblink(?,'select max(ci_id) as ci_id from concept_data_info') as cdi(ci_id integer)|) or &Carp::croak(DBI->errstr());
				$sth_sel->execute(AG::DB::DB_LINK,$a->{gp_partid}) or &Carp::croak(DBI->errstr());
				if($sth_sel->rows()>0){
					my $column_number = 0;
					$sth_sel->bind_col(++$column_number, \$ci_id, undef);
					undef $column_number;
					$sth_sel->fetch;
				}
				$sth_sel->finish;
				undef $sth_sel;
			}
			if(defined $ci_id){
				$sth_sel_cdi = $dbh->prepare(qq|select cdi_name_e from dblink(?,'select cdi_name,cdi_name_e from concept_data_info where ci_id=$ci_id') as cdi(cdi_name text,cdi_name_e text) where cdi_name=?|) or &Carp::croak(DBI->errstr());
			}
		}

		foreach my $a (@A){
			my $rtn_hash;
			if($cmd == CMD_ADDING){
				&_log("",__LINE__);
				&Carp::croak('Information necessary to register is missing.('.__LINE__.')') unless(
					defined $a->{gp_x}   &&
					defined $a->{gp_y}   &&
					defined $a->{gp_z}   &&
					defined $a->{gp_avx} &&
					defined $a->{gp_avy} &&
					defined $a->{gp_avz} &&
					defined $a->{gp_uvx} &&
					defined $a->{gp_uvy} &&
					defined $a->{gp_uvz} &&
					defined $a->{gp_version}
				);
				$a->{gp_openid} = $openid if(!defined $a->{gp_openid} && defined $openid);

				if(exists $a->{gp_partid} && defined $a->{gp_partid} && defined $sth_sel_cdi){
					unless(exists $a->{gp_partname} && defined $a->{gp_partname}){
						my $gp_partname;
						$sth_sel_cdi->execute(AG::DB::DB_LINK,$a->{gp_partid}) or &Carp::croak(DBI->errstr());
						if($sth_sel_cdi->rows()>0){
							my $column_number = 0;
							$sth_sel_cdi->bind_col(++$column_number, \$gp_partname, undef);
							undef $column_number;
							$sth_sel_cdi->fetch;
						}
						$sth_sel_cdi->finish;
						$a->{gp_partname} = $gp_partname if(defined $gp_partname);
						undef $gp_partname;
					}
				}

				my @column_names;
				my @column_values;
				my @bind_values;
				my $key;
				foreach $key (@COLUMN_NAMES_DB_PIN_ADD){
					next unless(defined $a->{$key});
					push(@column_names,$key);
					push(@column_values,'?');
					push(@bind_values,$a->{$key});
				}

				my $sth_ins = $dbh->prepare(qq|insert into $table_name (|.join(",",@column_names).qq|) values (|.join(",",@column_values).qq|) RETURNING |.join(",",@{$arg{db_column_names}})) or &Carp::croak(DBI->errstr());
				$sth_ins->execute(@bind_values) or &Carp::croak(DBI->errstr());
				my $rows = $sth_ins->rows();
				if($rows>0){
					$rtn_rows += $rows;
					$rtn_hash = $sth_ins->fetchrow_hashref;
				}
				$sth_ins->finish;
				undef $sth_ins;
				undef @column_names;
				undef @column_values;
				undef @bind_values;
				undef $key;
				undef $rows;
			}
			else{
				&_log("",__LINE__);
				&Carp::croak('Information necessary to register is missing.('.__LINE__.')') unless(defined $a->{gp_id} && defined $openid);
				if($cmd == CMD_EXCLUSION){
					&_log("",__LINE__);
					my $sth_del = $dbh->prepare(qq|delete from $table_name where gp_id=? and gp_openid=? RETURNING |.join(",",@{$arg{db_column_names}})) or &Carp::croak(DBI->errstr());
					$sth_del->execute($a->{gp_id},$openid) or &Carp::croak(DBI->errstr());
					my $rows = $sth_del->rows();
					if($rows>0){
						$rtn_rows += $rows;
						$rtn_hash = $sth_del->fetchrow_hashref;
					}
					$sth_del->finish;
					undef $sth_del;
					undef $rows;
				}
				elsif($cmd == CMD_UPDATE){
					&_log("",__LINE__);

					if(exists $a->{gp_partid} && defined $a->{gp_partid} && defined $sth_sel_cdi){
						unless(exists $a->{gp_partname} && defined $a->{gp_partname}){
							my $gp_partname;
							$sth_sel_cdi->execute(AG::DB::DB_LINK,$a->{gp_partid}) or &Carp::croak(DBI->errstr());
							if($sth_sel_cdi->rows()>0){
								my $column_number = 0;
								$sth_sel_cdi->bind_col(++$column_number, \$gp_partname, undef);
								undef $column_number;
								$sth_sel_cdi->fetch;
							}
							$sth_sel_cdi->finish;
							$a->{gp_partname} = $gp_partname if(defined $gp_partname);
							undef $gp_partname;
						}
					}

					my @column_names;
					my @bind_values;
					my $key;
					foreach $key (@COLUMN_NAMES_DB_PIN_UPD){
						next unless(defined $a->{$key});
						push(@column_names,qq|$key=?|);
						push(@bind_values,$a->{$key});
					}
					$key = qq|gp_modified|;
					push(@column_names,qq|$key='now()'|);
					push(@bind_values,$a->{gp_id});
					push(@bind_values,$openid);
					my $sql = qq|update $table_name set |.join(",",@column_names).qq| where gp_id=? and gp_openid=? RETURNING |.join(",",@{$arg{db_column_names}});
					my $sth_upd = $dbh->prepare($sql) or &Carp::croak(DBI->errstr());
					$sth_upd->execute(@bind_values) or &Carp::croak(DBI->errstr());
					my $rows = $sth_upd->rows();
					if($rows>0){
						$rtn_rows += $rows;
						$rtn_hash = $sth_upd->fetchrow_hashref;
					}
					$sth_upd->finish;
					undef $sth_upd;
					undef @column_names;
					undef @bind_values;
					undef $key;
					undef $sql;
					undef $rows;
				}
			}
			if(defined $rtn_hash){
				$self->_cast_type($table_name,$rtn_hash);
				push(@$rtn_array,$rtn_hash);
			}
		}
		undef $sth_sel_cdi;
		$dbh->commit() if($rtn_rows);
	};
	if($@){
		$self->_set_error($@);
		$dbh->rollback;
		undef $rtn_rows;
		undef $rtn_array;
	}
	$dbh->{AutoCommit} = 1;
	$dbh->{RaiseError} = 0;

	return ($rtn_rows,$rtn_array);
}

sub _execute_pin_reference {
	my $self = shift;
	my %arg = (
		cmd => CMD_GET,
		type => TYPE_PIN,
		@_
	);
	return undef unless($arg{type} == TYPE_PIN);

	my $json = $arg{json};
	return undef unless(defined $json && (ref $json eq 'HASH' || ref $json eq 'ARRAY'));

	my $openid = $arg{openid};
	my $cmd = $arg{cmd};
	my $type = $arg{type};

	my $rtn_rows;
	my $rtn_array;
	$self->_clear_error();

	my $dbh = $self->get_dbh();
	$dbh->{RaiseError} = 1;
	eval{
		my $table_name = TABLE_NAME_PIN;
		if($cmd == CMD_GET){
			my @A;
			if(ref $json eq 'HASH'){
				push(@A,$json);
			}elsif(ref $json eq 'ARRAY'){
				push(@A,@$json);
			}
			my @bind_values = map { $_->{gp_id} } grep {defined $_->{gp_id} && length $_->{gp_id}} @A;
			&Carp::croak('Information necessary to refer is missing.('.__LINE__.')') unless(scalar @bind_values);
			my @bind_columns = map { '?' } @bind_values;
			my $column_names = defined $arg{db_column_names} ? join(",",@{$arg{db_column_names}}) : '*';
			my $sth_sel = $dbh->prepare(qq|select $column_names from global_pin where gp_id in (|.join(',',@bind_columns).qq|)|) or &Carp::croak(DBI->errstr());
			$sth_sel->execute(@bind_values) or &Carp::croak(DBI->errstr());
			$rtn_rows = $sth_sel->rows();
			if($rtn_rows>0){
				while(my $hash = $sth_sel->fetchrow_hashref){
					push(@$rtn_array,$hash) if(defined $hash);
				}
			}
			$sth_sel->finish;
			undef $sth_sel;
			undef @bind_values;
			undef @bind_columns;
			undef $column_names;
			undef @A;
		}
		elsif($cmd == CMD_SEARCH){
			&_log("",__LINE__);
			if(ref $json eq 'HASH'){
				my @where_column_names = qw/gp_partid gp_partname gp_desc/;
				my @filter_column_names = qw/gp_id gp_version/;
				my %coordinate_column_names = map {$_=> exists $json->{$_} && defined $json->{$_} ? $json->{$_} : undef} qw/gp_x gp_y gp_z gp_radius PinX2 PinY2 PinZ2/;
				my @bind_columns;
				my @bind_values;
				my $column_names = defined $arg{db_column_names} ? join(",",@{$arg{db_column_names}}) : '*';

				foreach my $c (@where_column_names){
					next unless(exists $json->{$c} && defined $json->{$c} && length $json->{$c});
					push(@bind_columns,qq|$c ~* ?|);
					push(@bind_values,qq|.*$json->{$c}.*|);
				}
				foreach my $c (@filter_column_names){
					next unless(exists $json->{$c} && defined $json->{$c} && length $json->{$c});
					push(@bind_columns,qq|$c = ?|);
					push(@bind_values,$json->{$c});
				}
				if(
					defined $coordinate_column_names{gp_x} && length $coordinate_column_names{gp_x} &&
					defined $coordinate_column_names{gp_y} && length $coordinate_column_names{gp_y} &&
					defined $coordinate_column_names{gp_z} && length $coordinate_column_names{gp_z} &&
					defined $coordinate_column_names{gp_radius} && length $coordinate_column_names{gp_radius}
				){
					push(@bind_columns,qq|abs(sqrt(power(gp_x - ?,2)+power(gp_y - ?,2)+power(gp_z - ?,2)))<=?|);
					push(@bind_values,$json->{gp_x});
					push(@bind_values,$json->{gp_y});
					push(@bind_values,$json->{gp_z});
					push(@bind_values,$json->{gp_radius});
				}else{
					if(defined $coordinate_column_names{gp_x} && length $coordinate_column_names{gp_x}){
						push(@bind_columns,qq|gp_x>?|);
						push(@bind_values,$json->{gp_x});
					}
					if(defined $coordinate_column_names{gp_y} && length $coordinate_column_names{gp_y}){
						push(@bind_columns,qq|gp_y>?|);
						push(@bind_values,$json->{gp_y});
					}
					if(defined $coordinate_column_names{gp_z} && length $coordinate_column_names{gp_z}){
						push(@bind_columns,qq|gp_z>?|);
						push(@bind_values,$json->{gp_z});
					}
					if(defined $coordinate_column_names{PinX2} && length $coordinate_column_names{PinX2}){
						push(@bind_columns,qq|gp_x<?|);
						push(@bind_values,$json->{PinX2});
					}
					if(defined $coordinate_column_names{PinY2} && length $coordinate_column_names{PinY2}){
						push(@bind_columns,qq|gp_y<?|);
						push(@bind_values,$json->{PinY2});
					}
					if(defined $coordinate_column_names{PinZ2} && length $coordinate_column_names{PinZ2}){
						push(@bind_columns,qq|gp_z<?|);
						push(@bind_values,$json->{PinZ2});
					}
				}
				my $sql = qq|select $column_names from global_pin|;
				$sql .= qq| where |.join(" and ",@bind_columns) if(scalar @bind_columns);
				if(defined $arg{'sort'}){
					$sql .= qq| order by $arg{'sort'}|;
					$sql .= qq| $arg{dir}| if(defined $arg{dir});
				}
				my $sth_sel = $dbh->prepare($sql) or &Carp::croak(DBI->errstr());
				if(scalar @bind_values){
					$sth_sel->execute(@bind_values) or &Carp::croak(DBI->errstr());
				}else{
					$sth_sel->execute() or &Carp::croak(DBI->errstr());
				}
				$rtn_rows = $sth_sel->rows();
				if($rtn_rows>0){
					if(defined $arg{start} || defined $arg{limit}){
						$sth_sel->finish;
						undef $sth_sel;
						$sql .= qq| offset $arg{start}| if(defined $arg{start});
						$sql .= qq| limit $arg{limit}| if(defined $arg{limit});
						$sth_sel = $dbh->prepare($sql) or &Carp::croak(DBI->errstr());
						if(scalar @bind_values){
							$sth_sel->execute(@bind_values) or &Carp::croak(DBI->errstr());
						}else{
							$sth_sel->execute() or &Carp::croak(DBI->errstr());
						}
					}
					while(my $hash = $sth_sel->fetchrow_hashref){
						push(@$rtn_array,$hash) if(defined $hash);
					}
				}
				$sth_sel->finish;
				undef $sth_sel;
			}
		}
		elsif($cmd == CMD_GET_LIST){
			&_log("",__LINE__);
#			&Carp::croak('Information necessary to refer is missing.('.__LINE__.')') unless(defined $arg{gpg_id});
			my $gp_ids;

			&_log("\$json=[".(&JSON::XS::encode_json($json))."]",__LINE__);
			my @A;
			if(ref $json eq 'HASH'){
				push(@A,$json);
			}elsif(ref $json eq 'ARRAY'){
				push(@A,@$json);
			}
			my @bind_values = map { $_->{gpg_id} } grep {defined $_->{gpg_id} && length $_->{gpg_id}} @A;
			my $bind_count = scalar grep {exists $_->{gpg_id}} @A;
			&_log("\@A=[".(scalar @A)."]",__LINE__);
			&_log("\@bind_values=[".(scalar @bind_values)."]",__LINE__);
			&_log("\$bind_count=[$bind_count]",__LINE__);
			&_log("",__LINE__);

#			my $bind_count = scalar grep {defined $_->{gpg_id}} @A;
#			print __PACKAGE__.":".__LINE__.":\$bind_count=[$bind_count]<br>\n" if(DEBUG);

			if(scalar @bind_values){
				my @bind_columns = map {'?'} @bind_values;
				my $sql = qq|select p2g.gp_id from global_pin2group as p2g left join (select * from |.TABLE_NAME_PINGROUP.qq|) as g on g.gpg_id=p2g.gpg_id where |;
				if(defined $arg{openid}){
#ログインしていれば、参照可とする
					$sql .= qq|(g.gpg_apifref OR g.gpg_openid=?) AND |;
					unshift(@bind_values,$arg{openid});
				}else{
					$sql .= qq|g.gpg_apifref AND | unless($arg{forcing});
				}
				$sql .= qq|p2g.gpg_id in (|.join(',',@bind_columns).qq|) group by p2g.gp_id|;
				my $sth_sel = $dbh->prepare($sql) or &Carp::croak(DBI->errstr());
				$sth_sel->execute(@bind_values) or &Carp::croak(DBI->errstr());
				my $gp_id;
				my $column_number = 0;
				$sth_sel->bind_col(++$column_number, \$gp_id, undef);
				while($sth_sel->fetch){
					next unless(defined $gp_id);
					push(@$gp_ids,$gp_id);
				}
				$sth_sel->finish;
				undef $sth_sel;
				undef @bind_columns;
				undef $gp_id;
				undef $column_number;
				undef $sql;
			}
			undef @bind_values;

			my $where;
			if(defined $gp_ids && scalar @$gp_ids){
				my @bind_columns = map {'?'} @$gp_ids;
				$where = qq/gp_id in (/.join(',',@bind_columns).qq/)/;
				push(@bind_values,@$gp_ids);
				undef @bind_columns;
			}
			if(defined $where || $bind_count==0){
				my $column_names = defined $arg{db_column_names} ? join(",",@{$arg{db_column_names}}) : '*';
				my $sql = qq|select $column_names from $table_name|;
				$sql .= qq| where $where| if(defined $where);
				if(defined $arg{'sort'}){
					$sql .= qq| order by $arg{'sort'}|;
					$sql .= qq| $arg{dir}| if(defined $arg{dir});
				}
				&_log("\$sql=[$sql]",__LINE__);
				&_log("\@bind_values=[".join(",",@bind_values)."]",__LINE__);
				my $sth_sel = $dbh->prepare($sql) or &Carp::croak(DBI->errstr());
				if(scalar @bind_values){
					$sth_sel->execute(@bind_values) or &Carp::croak(DBI->errstr());
				}else{
					$sth_sel->execute() or &Carp::croak(DBI->errstr());
				}
				$rtn_rows = $sth_sel->rows();
				if($rtn_rows>0){
					if(defined $arg{start} || defined $arg{limit}){
						$sth_sel->finish;
						undef $sth_sel;
						$sql .= qq| offset $arg{start}| if(defined $arg{start});
						$sql .= qq| limit $arg{limit}| if(defined $arg{limit});
						$sth_sel = $dbh->prepare($sql) or &Carp::croak(DBI->errstr());
						if(scalar @bind_values){
							$sth_sel->execute(@bind_values) or &Carp::croak(DBI->errstr());
						}else{
							$sth_sel->execute() or &Carp::croak(DBI->errstr());
						}
					}
					while(my $hash = $sth_sel->fetchrow_hashref){
						push(@$rtn_array,$hash) if(defined $hash);
					}
				}
				$sth_sel->finish;
				undef $sth_sel;
				&_log("\$rtn_rows=[$rtn_rows]",__LINE__);
			}else{
				$rtn_rows = 0;
			}
		}
		$self->_cast_type($table_name,$rtn_array) if(defined $rtn_array);
	};
	if($@){
		$self->_set_error($@);
		undef $rtn_rows;
		undef $rtn_array;
	}
	$dbh->{RaiseError} = 0;

	return ($rtn_rows,$rtn_array);
}

sub _execute_pin_group {
	my $self = shift;
	my %arg = (
		type => TYPE_PINGROUP,
		forcing => false,
		@_
	);
	my $rows;
	my $rtn;
	return ($rows,$rtn) unless($arg{type} == TYPE_PINGROUP);

	my $json = $arg{json};
	return undef unless(defined $json && (ref $json eq 'HASH' || ref $json eq 'ARRAY'));

	if($arg{cmd} == CMD_ADDING || $arg{cmd} == CMD_EXCLUSION || $arg{cmd} == CMD_UPDATE){
		$arg{db_column_names} = \@COLUMN_NAMES_DB_PINGROUP_EDIT;
		($rows,$rtn) = $self->_execute_pin_group_edit(%arg);
	}elsif($arg{cmd} == CMD_GET || $arg{cmd} == CMD_GET_LIST || $arg{cmd} == CMD_SEARCH){
		$arg{db_column_names} = \@COLUMN_NAMES_DB_PINGROUP_REF;
		($rows,$rtn) = $self->_execute_pin_group_reference(%arg);
	}elsif($arg{cmd} == CMD_GET_ATTR){
		$arg{db_column_names} = \@COLUMN_NAMES_DB_PINGROUP_ATTR;
		($rows,$rtn) = $self->_get_gpg_attr(%arg);
		if(defined $rtn && ref $rtn eq 'HASH'){
			delete $rtn->{gpg_openid};
			$rtn->{gpg_id} = $arg{gpg_id};
			$self->_cast_type(TABLE_NAME_PINGROUP,$rtn);
		}
	}
	return ($rows,$rtn);
}

sub _execute_pin_group_edit {
	my $self = shift;
	my %arg = (
		cmd => CMD_ADDING,
		type => TYPE_PINGROUP,
		@_
	);
	return undef unless($arg{type} == TYPE_PINGROUP);

	my $json = $arg{json};
	return undef unless(defined $json && (ref $json eq 'HASH' || ref $json eq 'ARRAY'));

	my $openid = $arg{openid};
	&Carp::croak('Information necessary to register is missing.('.__LINE__.')') unless(defined $openid);

	my $cmd = $arg{cmd};
	my $type = $arg{type};

	my $rtn_rows = 0;
	my $rtn_array;
	$self->_clear_error();

	my $dbh = $self->get_dbh();
	$dbh->{AutoCommit} = 0;
	$dbh->{RaiseError} = 1;
	eval{
		my $table_name = TABLE_NAME_PINGROUP;

		my @A;
		if(ref $json eq 'HASH'){
			push(@A,$json);
		}elsif(ref $json eq 'ARRAY'){
			push(@A,@$json);
		}
		foreach my $a (@A){
			if($cmd == CMD_ADDING){

				$a->{gpg_openid} = $openid unless(defined $a->{gpg_openid});

				my @column_names;
				my @column_values;
				my @bind_values;
				my $key;
				foreach $key (@COLUMN_NAMES_DB_PINGROUP_ADD){
					next unless(defined $a->{$key});
					push(@column_names,$key);
					push(@column_values,'?');
					push(@bind_values,$a->{$key});
				}
				my $sth_ins = $dbh->prepare(qq|insert into $table_name (|.join(",",@column_names).qq|) values (|.join(",",@column_values).qq|) RETURNING |.join(",",@{$arg{db_column_names}})) or &Carp::croak(DBI->errstr());
				$sth_ins->execute(@bind_values) or &Carp::croak(DBI->errstr());
				my $rows = $sth_ins->rows();
				if($rows>0){
					$rtn_rows += $rows;
					while(my $hash = $sth_ins->fetchrow_hashref){
						push(@$rtn_array,$hash) if(defined $hash);
					}
				}
				$sth_ins->finish;
				undef $sth_ins;

				undef @column_names;
				undef @column_values;
				undef @bind_values;
				undef $key;
			}
			else{
				&Carp::croak('Information necessary to register is missing.('.__LINE__.')') unless(defined $a->{gpg_id});
				if($cmd == CMD_EXCLUSION){
					my $sth_del = $dbh->prepare(qq|delete from $table_name where gpg_id=? and gpg_openid=? RETURNING |.join(",",@{$arg{db_column_names}})) or &Carp::croak(DBI->errstr());
					$sth_del->execute($a->{gpg_id},$openid) or &Carp::croak(DBI->errstr());
					my $rows = $sth_del->rows();
					if($rows>0){
						$rtn_rows += $rows;
						while(my $hash = $sth_del->fetchrow_hashref){
							push(@$rtn_array,$hash) if(defined $hash);
						}
					}
					$sth_del->finish;
					undef $sth_del;
				}
				elsif($cmd == CMD_UPDATE){
					my @column_names;
					my @bind_values;
					my $key;
					foreach $key (@COLUMN_NAMES_DB_PINGROUP_UPD){
						next unless(defined $a->{$key});
						push(@column_names,qq|$key=?|);
						push(@bind_values,$a->{$key});
					}
					$key = qq|gpg_modified|;
					push(@column_names,qq|$key='now()'|);
					push(@bind_values,$a->{gpg_id});
					push(@bind_values,$openid);
					my $sth_upd = $dbh->prepare(qq|update $table_name set |.join(",",@column_names).qq| where gpg_id=? and gpg_openid=? RETURNING |.join(",",@{$arg{db_column_names}})) or &Carp::croak(DBI->errstr());
					$sth_upd->execute(@bind_values) or &Carp::croak(DBI->errstr());
					my $rows = $sth_upd->rows();
					if($rows>0){
						$rtn_rows += $rows;
						while(my $hash = $sth_upd->fetchrow_hashref){
							push(@$rtn_array,$hash) if(defined $hash);
						}
					}
					$sth_upd->finish;
					undef $sth_upd;
					undef @column_names;
					undef @bind_values;
					undef $key;
				}
			}
		}
		$self->_cast_type($table_name,$rtn_array) if(defined $rtn_array);
		$dbh->commit() if($rtn_rows);
	};
	if($@){
		$self->_set_error($@);
		$dbh->rollback;
		undef $rtn_rows;
		undef $rtn_array;
	}
	$dbh->{AutoCommit} = 1;
	$dbh->{RaiseError} = 0;

	return ($rtn_rows,$rtn_array);
}

sub _execute_pin_group_reference {
	my $self = shift;
	my %arg = (
		cmd => CMD_GET,
		type => TYPE_PINGROUP,
		forcing => false,
		@_
	);
	return undef unless($arg{type} == TYPE_PINGROUP);

	my $json = $arg{json};
	return undef unless(defined $json && (ref $json eq 'HASH' || ref $json eq 'ARRAY'));

	my $openid = $arg{openid};
	my $cmd = $arg{cmd};
	my $type = $arg{type};
	my $forcing = $arg{forcing};

	my $rtn_rows;
	my $rtn_array;
	$self->_clear_error();

	my $dbh = $self->get_dbh();
	$dbh->{RaiseError} = 1;
	eval{
		my $table_name = TABLE_NAME_PINGROUP;
		if($cmd == CMD_GET){
			my @A;
			if(ref $json eq 'HASH'){
				push(@A,$json);
			}elsif(ref $json eq 'ARRAY'){
				push(@A,@$json);
			}
			my @bind_values = map { $_->{gpg_id} } grep {defined $_->{gpg_id} && length $_->{gpg_id}} @A;
			&Carp::croak('Information necessary to refer is missing.('.__LINE__.')') unless(scalar @bind_values);
			my @bind_columns = map { '?' } @bind_values;
			my $column_names = defined $arg{db_column_names} ? join(",",grep {$_ !~ /^gp_/} @{$arg{db_column_names}}) : '*';
			my $sth_sel = $dbh->prepare(qq|select $column_names from $table_name where gpg_id in (|.join(',',@bind_columns).qq|)|) or &Carp::croak(DBI->errstr());
			$sth_sel->execute(@bind_values) or &Carp::croak(DBI->errstr());
			$rtn_rows = $sth_sel->rows();
			if($rtn_rows>0){
				while(my $hash = $sth_sel->fetchrow_hashref){
					push(@$rtn_array,$hash) if(defined $hash);
				}
			}
			$sth_sel->finish;
			undef $sth_sel;
			if(defined $arg{db_column_names} && scalar grep {$_ =~ /^gp_count/} @{$arg{db_column_names}}){
				my $sth_sel = $dbh->prepare(qq|select * from global_pin2group where gpg_id=?|) or &Carp::croak(DBI->errstr());
				foreach my $a (@$rtn_array){
					my($gpg_attr_rows,$gpg_attr_array) = $self->_get_gpg_attr(%arg,json=>$a);
					my $gpg_attr = $gpg_attr_array->[0] if(defined $gpg_attr_array);
					next unless(defined $gpg_attr);
					$gpg_attr->{gpg_apifref} = true if($forcing || $arg{openid} eq $gpg_attr->{gpg_openid});
					next unless($gpg_attr->{gpg_apifref});
					$sth_sel->execute($a->{gpg_id}) or &Carp::croak(DBI->errstr());
					$a->{gp_count} = $sth_sel->rows();
					$sth_sel->finish;
				}
				undef $sth_sel;
			}
		}
		elsif($cmd == CMD_SEARCH){
			if(ref $json eq 'HASH'){
				my @where_column_names = qw/gpg_desc/;
				my @bind_columns;
				my @bind_values;
				my $column_names = defined $arg{db_column_names} ? join(",",grep {$_ !~ /^gp_/} @{$arg{db_column_names}}) : '*';

				foreach my $c (@where_column_names){
					next unless(exists $json->{$c} && defined $json->{$c});
					push(@bind_columns,qq|$c ~* ?|);
					push(@bind_values,qq|.*$json->{$c}.*|);
				}
				if(defined $arg{openid}){
					push(@bind_columns,qq|(gpg_fsearch or gpg_openid=?)|);
					push(@bind_values,$arg{openid});
				}else{
					push(@bind_columns,qq|gpg_fsearch|) unless($arg{forcing});
				}
				my $sql = qq|select $column_names from $table_name|;
				$sql .= qq| where |.join(" and ",@bind_columns) if(scalar @bind_columns);
				if(defined $arg{'sort'}){
					$sql .= qq| order by $arg{'sort'}|;
					$sql .= qq| $arg{dir}| if(defined $arg{dir});
				}
				my $sth_sel = $dbh->prepare($sql) or &Carp::croak(DBI->errstr());
				if(scalar @bind_values){
					$sth_sel->execute(@bind_values) or &Carp::croak(DBI->errstr());
				}else{
					$sth_sel->execute() or &Carp::croak(DBI->errstr());
				}
				$rtn_rows = $sth_sel->rows();
				if($rtn_rows>0){
					if(defined $arg{start} || defined $arg{limit}){
						$sth_sel->finish;
						undef $sth_sel;
						$sql .= qq| offset $arg{start}| if(defined $arg{start});
						$sql .= qq| limit $arg{limit}| if(defined $arg{limit});
						$sth_sel = $dbh->prepare($sql) or &Carp::croak(DBI->errstr());
						if(scalar @bind_values){
							$sth_sel->execute(@bind_values) or &Carp::croak(DBI->errstr());
						}else{
							$sth_sel->execute() or &Carp::croak(DBI->errstr());
						}
					}
					while(my $hash = $sth_sel->fetchrow_hashref){
						push(@$rtn_array,$hash) if(defined $hash);
					}
				}
				$sth_sel->finish;
				undef $sth_sel;

				if(defined $rtn_array){
					if(scalar grep {$_ =~ /^gp_count$/} @{$arg{db_column_names}}){
						my $sth_sel = $dbh->prepare(qq|select * from global_pin2group where gpg_id=?|) or &Carp::croak(DBI->errstr());
						foreach my $a (@$rtn_array){
							my($gpg_attr_rows,$gpg_attr_array) = $self->_get_gpg_attr(%arg,json=>$a);
							my $gpg_attr = $gpg_attr_array->[0] if(defined $gpg_attr_array);
							next unless(defined $gpg_attr && ref $gpg_attr eq 'HASH');
							$gpg_attr->{gpg_apifref} = true if($forcing || $arg{openid} eq $gpg_attr->{gpg_openid});
							next unless($gpg_attr->{gpg_apifref});
							$sth_sel->execute($a->{gpg_id}) or &Carp::croak(DBI->errstr());
							$a->{gp_count} = $sth_sel->rows();
							$sth_sel->finish;
						}
						undef $sth_sel;
					}
				}
			}
		}
		elsif($cmd == CMD_GET_LIST){
#			&Carp::croak('Information necessary to refer is missing.('.__LINE__.')') unless(defined $arg{gp_id});
			my $gpg_ids;
			my @A;
			if(ref $json eq 'HASH'){
				push(@A,$json);
			}elsif(ref $json eq 'ARRAY'){
				push(@A,@$json);
			}
			my @bind_values = map { $_->{gp_id} } grep {defined $_->{gp_id} && length $_->{gp_id}} @A;
			my $bind_count = scalar grep {exists $_->{gp_id}} @A;

			if(scalar @bind_values){
				my @bind_columns = map {'?'} @bind_values;
				my $sql = qq|select p2g.gpg_id from global_pin2group as p2g left join (select * from |.TABLE_NAME_PINGROUP.qq|) as g on g.gpg_id=p2g.gpg_id where |;
				if(defined $arg{openid}){
					$sql .= qq|(g.gpg_apifref OR g.gpg_openid=?) AND |;
					unshift(@bind_values,$arg{openid});
				}else{
					$sql .= qq|g.gpg_apifref AND |;
				}
				$sql .= qq|p2g.gp_id in (|.join(',',@bind_columns).qq|) group by p2g.gpg_id|;
				my $sth_sel = $dbh->prepare($sql) or &Carp::croak(DBI->errstr());
				$sth_sel->execute(@bind_values) or &Carp::croak(DBI->errstr());
				my $gpg_id;
				my $column_number = 0;
				$sth_sel->bind_col(++$column_number, \$gpg_id, undef);
				while($sth_sel->fetch){
					next unless(defined $gpg_id);
					push(@$gpg_ids,$gpg_id);
				}
				$sth_sel->finish;
				undef $sth_sel;
				undef @bind_columns;
				undef $gpg_id;
				undef $column_number;
				undef $sql;
			}
			undef @bind_values;

			my $where;
			if(defined $gpg_ids && scalar @$gpg_ids){
				my @bind_columns = map {'?'} @$gpg_ids;
				$where = qq/gpg_id in (/.join(',',@bind_columns).qq/)/;
				push(@bind_values,@$gpg_ids);
				undef @bind_columns;
			}
			if(defined $where || $bind_count==0){
				my $column_names = defined $arg{db_column_names} ? join(",",grep {$_ !~ /^gp_/} @{$arg{db_column_names}}) : '*';
				my $sql = qq|select $column_names from $table_name|;
				$sql .= qq| where $where| if(defined $where);
				if(defined $arg{'sort'}){
					$sql .= qq| order by $arg{'sort'}|;
					$sql .= qq| $arg{dir}| if(defined $arg{dir});
				}
				&_log("\$sql=[$sql]",__LINE__);
				my $sth_sel = $dbh->prepare($sql) or &Carp::croak(DBI->errstr());
				if(scalar @bind_values){
					$sth_sel->execute(@bind_values) or &Carp::croak(DBI->errstr());
				}else{
					$sth_sel->execute() or &Carp::croak(DBI->errstr());
				}
				$rtn_rows = $sth_sel->rows();
				if($rtn_rows>0){
					if(defined $arg{start} || defined $arg{limit}){
						$sth_sel->finish;
						undef $sth_sel;
						$sql .= qq| offset $arg{start}| if(defined $arg{start});
						$sql .= qq| limit $arg{limit}| if(defined $arg{limit});
						$sth_sel = $dbh->prepare($sql) or &Carp::croak(DBI->errstr());
						if(scalar @bind_values){
							$sth_sel->execute(@bind_values) or &Carp::croak(DBI->errstr());
						}else{
							$sth_sel->execute() or &Carp::croak(DBI->errstr());
						}
					}
					while(my $hash = $sth_sel->fetchrow_hashref){
						push(@$rtn_array,$hash) if(defined $hash);
					}
				}
				$sth_sel->finish;
				undef $sth_sel;
				&_log("\$rtn_rows=[$rtn_rows]",__LINE__);
			}else{
				$rtn_rows = 0;
			}
		}
		$self->_cast_type($table_name,$rtn_array) if(defined $rtn_array);
	};
	if($@){
		$self->_set_error($@);
	}
	$dbh->{RaiseError} = 0;

	return ($rtn_rows,$rtn_array);
}

sub _convDBColumnNames {
	my $self = shift;
	my $arg = shift;

	return unless (defined $arg && (ref $arg eq 'HASH' || ref $arg eq 'ARRAY'));

	my @db_column_names;
	my @js_column_names;

	push(@db_column_names,@COLUMN_NAMES_DB_PINGROUP_CONV);
	push(@db_column_names,@COLUMN_NAMES_DB_PIN_CONV);

	push(@js_column_names,@COLUMN_NAMES_JS_PINGROUP_CONV);
	push(@js_column_names,@COLUMN_NAMES_JS_PIN_CONV);

	if(ref $arg eq 'HASH'){
		for(my $i=0;$i<scalar @js_column_names;$i++){
			next unless(exists $arg->{$js_column_names[$i]});
			$arg->{$db_column_names[$i]} = $arg->{$js_column_names[$i]};
			delete $arg->{$js_column_names[$i]};
		}
	}elsif(ref $arg eq 'ARRAY'){
		my $this_func_name = (caller 0)[3];
		foreach my $r (@$arg){
			$self->$this_func_name($r);
		}
	}

	undef @db_column_names;
	undef @js_column_names;
}

sub _convJSColumnNames {
	my $self = shift;
	my $arg = shift;

	return unless (defined $arg && (ref $arg eq 'HASH' || ref $arg eq 'ARRAY'));

	my @db_column_names;
	my @js_column_names;

	push(@db_column_names,@COLUMN_NAMES_DB_PINGROUP_CONV);
	push(@db_column_names,@COLUMN_NAMES_DB_PIN_CONV);

	push(@js_column_names,@COLUMN_NAMES_JS_PINGROUP_CONV);
	push(@js_column_names,@COLUMN_NAMES_JS_PIN_CONV);

	if(ref $arg eq 'HASH'){
		my $r = $arg;
		for(my $i=0;$i<scalar @db_column_names;$i++){
			next unless(exists $r->{$db_column_names[$i]});
			$r->{$js_column_names[$i]} = $r->{$db_column_names[$i]};
			delete $r->{$db_column_names[$i]};
		}
	}elsif(ref $arg eq 'ARRAY'){
		my $this_func_name = (caller 0)[3];
		foreach my $r (@$arg){
			$self->$this_func_name($r);
		}
	}

	undef @db_column_names;
	undef @js_column_names;
}

sub _execute {
	my $self = shift;
	my %arg = (
		cmd => CMD_ADDING,
		type => TYPE_PIN,
		forcing => false,
		@_
	);
	my $rows;
	my $rtn;
	if($arg{type} == TYPE_PIN){
		&_log("",__LINE__);
		$self->_convDBColumnNames($arg{json});
		($rows,$rtn) = $self->_execute_pin(%arg);
	}
	elsif($arg{type} == TYPE_PINGROUP){
		&_log("",__LINE__);
		$self->_convDBColumnNames($arg{json});
		($rows,$rtn) = $self->_execute_pin_group(%arg);
	}
	$self->_convJSColumnNames($rtn);
	return ($rows,$rtn);
}

sub addPin {
	my $self = shift;
	my %arg = @_;
	&_log("",__LINE__);
	$arg{cmd} = CMD_ADDING;
	$arg{type} = TYPE_PIN;
	$arg{forcing} = false;
	my($rows,$rtn) = $self->_execute(%arg);
	&Carp::croak($self->error()) if(defined $self->error());
	return ($rows,$rtn);
}
sub removePin {
	my $self = shift;
	my %arg = @_;
	$arg{cmd} = CMD_EXCLUSION;
	$arg{type} = TYPE_PIN;
	$arg{forcing} = false;
	my($rows,$rtn) = $self->_execute(%arg);
	&Carp::croak($self->error()) if(defined $self->error());
	return ($rows,$rtn);
}

sub updatePin {
	my $self = shift;
	my %arg = @_;
	$arg{cmd} = CMD_UPDATE;
	$arg{type} = TYPE_PIN;
	$arg{forcing} = false;
	my($rows,$rtn) = $self->_execute(%arg);
	&Carp::croak($self->error()) if(defined $self->error());
	return ($rows,$rtn);
}

sub getPin {
	my $self = shift;
	my %arg = @_;
	$arg{cmd} = CMD_GET;
	$arg{type} = TYPE_PIN;
	$arg{forcing} = false;
	my($rows,$rtn) = $self->_execute(%arg);
	&Carp::croak($self->error()) if(defined $self->error());
	return ($rows,$rtn);
}

sub getPinList {
	my $self = shift;
	my %arg = @_;
	&_log("",__LINE__);
	$arg{cmd} = CMD_GET_LIST;
	$arg{type} = TYPE_PIN;
	$arg{forcing} = false;
	my($rows,$rtn) = $self->_execute(%arg);
	&Carp::croak($self->error()) if(defined $self->error());
	return ($rows,$rtn);
}

sub getPinListForcing {
	my $self = shift;
	my %arg = @_;
	&_log("",__LINE__);
	$arg{cmd} = CMD_GET_LIST;
	$arg{type} = TYPE_PIN;
	$arg{forcing} = true;
	my($rows,$rtn) = $self->_execute(%arg);
	&Carp::croak($self->error()) if(defined $self->error());
	return ($rows,$rtn);
}

sub searchPin {
	my $self = shift;
	my %arg = @_;
	$arg{cmd} = CMD_SEARCH;
	$arg{type} = TYPE_PIN;
	$arg{forcing} = false;
	my($rows,$rtn) = $self->_execute(%arg);
	&Carp::croak($self->error()) if(defined $self->error());
	return ($rows,$rtn);
}

sub addPinGroup {
	my $self = shift;
	my %arg = @_;
	$arg{cmd} = CMD_ADDING;
	$arg{type} = TYPE_PINGROUP;
	$arg{forcing} = false;
	my($rows,$rtn) = $self->_execute(%arg);
	&Carp::croak($self->error()) if(defined $self->error());
	return ($rows,$rtn);
}
sub removePinGroup {
	my $self = shift;
	my %arg = @_;
	$arg{cmd} = CMD_EXCLUSION;
	$arg{type} = TYPE_PINGROUP;
	$arg{forcing} = false;
	my($rows,$rtn) = $self->_execute(%arg);
	&Carp::croak($self->error()) if(defined $self->error());
	return ($rows,$rtn);
}

sub updatePinGroup {
	my $self = shift;
	my %arg = @_;
	$arg{cmd} = CMD_UPDATE;
	$arg{type} = TYPE_PINGROUP;
	$arg{forcing} = false;
	my($rows,$rtn) = $self->_execute(%arg);
	&Carp::croak($self->error()) if(defined $self->error());
	return ($rows,$rtn);
}

sub getPinGroup {
	my $self = shift;
	my %arg = @_;
	$arg{cmd} = CMD_GET;
	$arg{type} = TYPE_PINGROUP;
	$arg{forcing} = false;
	my($rows,$rtn) = $self->_execute(%arg);
	&Carp::croak($self->error()) if(defined $self->error());
	return ($rows,$rtn);
}

sub getPinGroupForcing {
	my $self = shift;
	my %arg = @_;
	$arg{cmd} = CMD_GET;
	$arg{type} = TYPE_PINGROUP;
	$arg{forcing} = true;
	my($rows,$rtn) = $self->_execute(%arg);
	&Carp::croak($self->error()) if(defined $self->error());
	return ($rows,$rtn);
}

sub searchPinGroup {
	my $self = shift;
	my %arg = @_;
	$arg{cmd} = CMD_SEARCH;
	$arg{type} = TYPE_PINGROUP;
	$arg{forcing} = false;
	my($rows,$rtn) = $self->_execute(%arg);
	&Carp::croak($self->error()) if(defined $self->error());
	return ($rows,$rtn);
}

sub searchPinGroupForcing {
	my $self = shift;
	my %arg = @_;
	$arg{cmd} = CMD_SEARCH;
	$arg{type} = TYPE_PINGROUP;
	$arg{forcing} = true;
	my($rows,$rtn) = $self->_execute(%arg);
	&Carp::croak($self->error()) if(defined $self->error());
	return ($rows,$rtn);
}

sub getPinGroupAttr {
	my $self = shift;
	my %arg = @_;
	$arg{cmd} = CMD_GET_ATTR;
	$arg{type} = TYPE_PINGROUP;
	$arg{forcing} = false;
	my($rows,$rtn) = $self->_execute(%arg);
	&Carp::croak($self->error()) if(defined $self->error());
	return ($rows,$rtn);
}

sub getPinGroupList {
	my $self = shift;
	my %arg = @_;
	$arg{cmd} = CMD_GET_LIST;
	$arg{type} = TYPE_PINGROUP;
	$arg{forcing} = false;
	my($rows,$rtn) = $self->_execute(%arg);
	&Carp::croak($self->error()) if(defined $self->error());
	return ($rows,$rtn);
}

sub linkPinGroup {
	my $self = shift;
	my %arg = @_;
	$arg{cmd} = CMD_ADDING;
	$arg{forcing} = false;
	my $rtn_rows = $self->_tied(%arg);
	&Carp::croak($self->error()) if(defined $self->error());
	return $rtn_rows;
}

sub linkPinGroupForcing {
	my $self = shift;
	my %arg = @_;
	$arg{cmd} = CMD_ADDING;
	$arg{forcing} = true;
	my $rtn_rows = $self->_tied(%arg);
	&Carp::croak($self->error()) if(defined $self->error());
	return $rtn_rows;
}

sub unlinkPinGroup {
	my $self = shift;
	my %arg = @_;
	$arg{cmd} = CMD_EXCLUSION;
	$arg{forcing} = false;
	my $rtn_rows = $self->_tied(%arg);
	&Carp::croak($self->error()) if(defined $self->error());
	return $rtn_rows;
}

sub unlinkPinGroupForcing {
	my $self = shift;
	my %arg = @_;
	$arg{cmd} = CMD_EXCLUSION;
	$arg{forcing} = true;
	my $rtn_rows = $self->_tied(%arg);
	&Carp::croak($self->error()) if(defined $self->error());
	return $rtn_rows;
}

sub auth {
	my $self = shift;
	my %arg = @_;

	my $json = $arg{json};
	return undef unless(defined $json && (ref $json eq 'HASH' || ref $json eq 'ARRAY'));
	$self->_convDBColumnNames($json);

#	&Carp::croak('Information necessary to refer is missing.('.__LINE__.')') unless(defined $arg{openid} && (defined $json->{gpg_id} || defined $json->{gp_id}));
	&Carp::croak('Information necessary to refer is missing.('.__LINE__.')') unless(defined $json->{gpg_id} || defined $json->{gp_id});
	my $rtn_rows = 0;
	if(defined $arg{openid}){
		my $dbh = $self->get_dbh();
		if(defined $json->{gpg_id}){
			my $table_name = TABLE_NAME_PINGROUP;
			my $sth = $dbh->prepare(qq|select * from $table_name where gpg_openid=? and gpg_id=?|) or &Carp::croak(DBI->errstr());
			$sth->execute($arg{openid},$json->{gpg_id}) or &Carp::croak(DBI->errstr());
			$rtn_rows = $sth->rows;
			$sth->finish;
			undef $sth;
		}elsif(defined $json->{gp_id}){
			my $table_name = TABLE_NAME_PIN;
			my $sth = $dbh->prepare(qq|select * from $table_name where gp_openid=? and gp_id=?|) or &Carp::croak(DBI->errstr());
			$sth->execute($arg{openid},$json->{gp_id}) or &Carp::croak(DBI->errstr());
			$rtn_rows = $sth->rows;
			$sth->finish;
			undef $sth;
		}
		&Carp::croak($self->error()) if(defined $self->error());
	}
	return $rtn_rows;
}

sub _log {
	my $msg = shift;
	my $line = shift;
	return unless(DEBUG || DEBUG_PRINT || DEBUG_WARN);
	print __PACKAGE__.":$line:$msg<br>\n" if(DEBUG_PRINT);
	warn __PACKAGE__.":$line:$msg\n" if(DEBUG_WARN);
#	warn __PACKAGE__.":$line:$msg\n";
}

1;
