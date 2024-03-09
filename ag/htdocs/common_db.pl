#------------------------------------------------------------------------------
# 共通変数
#------------------------------------------------------------------------------
use vars qw(@ISA @EXPORT);

use DBI;
use Exporter;
use Carp;
use File::Spec;
use FindBin;

#use constant ROOT_CDI_ID => 0;
use constant ROOT_CDI_ID => undef;

my @ISA = qw(Exporter);

#use constant CONCEPT_INFO_ID_FMA => 1;

my @EXPORT = qw(get_dbh);

my $DB_user = 'postgres';
my $DB_pwd  = '';
my $DB_dbname = defined $ENV{AG_DB_NAME} ? $ENV{AG_DB_NAME} : 'bp3d';
my $DB_host = defined $ENV{AG_DB_HOST} ? $ENV{AG_DB_HOST} : '127.0.0.1';
my $DB_port = defined $ENV{AG_DB_PORT} ? $ENV{AG_DB_PORT} : '8543';#ag1
my $mydb;
my $mydb_local;

#my $LUDIA_OPERATOR='@@';
my $LUDIA_OPERATOR='%%'; #Ludiaが1.5.0以上で、PostgreSQLが8.3以上の場合、こちらを使用すること

&connectDB;

#------------------------------------------------------------------------------
# データベース共通関数
#------------------------------------------------------------------------------
sub connectDB {
	my %args = (
		dbname => $DB_dbname,
		host   => $DB_host,
		port   => $DB_port,
		user   => $DB_user,
		passwd => $DB_pwd,
		@_
	);
	my $DB_name = qq|dbname=$args{'dbname'};host=$args{'host'};port=$args{'port'}|;
#	warn __LINE__,":$DB_name\n";
	$mydb = DBI->connect("dbi:Pg:$DB_name",$args{'user'},$args{'passwd'}) or carp DBI->errstr;
	$mydb->{pg_enable_utf8} = 1 if(defined $mydb);
}

sub disconnectDB {
	$mydb->disconnect();
	undef $mydb;
}

sub get_dbh {
	return $mydb;
}

sub get_ludia_operator {
	return $LUDIA_OPERATOR;
}

sub mkpath {
	my $path = shift;
	my $m = umask();
	umask(0);
	&File::Path::mkpath($path,0,0777);
	umask($m);
}

sub setDefParams {
	my $form = shift;
	my $cookie = shift;

	unless(defined $form->{'lng'}){
		$form->{'lng'} = $form->{'locale'} if(!exists($form->{'lng'}) && exists($form->{'locale'}));
		$form->{'lng'} = $cookie->{'ag_annotation.locale'} if(!exists($form->{'lng'}) && defined $cookie && exists($cookie->{'ag_annotation.locale'}));
	}
	$form->{'lng'} = 'en' unless(defined $form->{'lng'});

	unless(defined $form->{'bul_id'}){
		$form->{'bul_id'} = $form->{'ag_annotation.images.bul_id'} if(exists $form->{'ag_annotation.images.bul_id'} && defined $form->{'ag_annotation.images.bul_id'});
		$form->{'bul_id'} = $cookie->{'ag_annotation.images.bul_id'} if(defined $cookie && exists $cookie->{'ag_annotation.images.bul_id'} && defined $cookie->{'ag_annotation.images.bul_id'});
		$form->{'bul_id'} = $form->{'t_type'} if(exists $form->{'t_type'} && defined $form->{'t_type'});
		$form->{'bul_id'} = &get_def_buildup_logic_id() + "" unless(defined $form->{'bul_id'});
	}
	$form->{'t_type'} = $form->{'bul_id'};

	#廃止予定の値
	if(exists($form->{'t_depth'}) && defined $form->{'t_depth'}){
		$form->{'t_depth'} = int($form->{'t_depth'});
	}else{
		$form->{'t_depth'} = 2;
	}

	unless(defined $form->{'ci_id'}){
		$form->{'ci_id'} = $form->{'ag_annotation.images.ci_id'} if(exists $form->{'ag_annotation.images.ci_id'} && defined $form->{'ag_annotation.images.ci_id'});
		$form->{'ci_id'} = $cookie->{'ag_annotation.images.ci_id'} if(defined $cookie && exists $cookie->{'ag_annotation.images.ci_id'} && defined $cookie->{'ag_annotation.images.ci_id'});
	}
	$form->{'ci_id'} = &get_def_concept_info_id() unless(defined $form->{'ci_id'});

	unless(defined $form->{'cb_id'}){
		$form->{'cb_id'} = $form->{'ag_annotation.images.cb_id'} if(exists $form->{'ag_annotation.images.cb_id'} && defined $form->{'ag_annotation.images.cb_id'});
		$form->{'cb_id'} = $cookie->{'ag_annotation.images.cb_id'} if(defined $cookie && exists $cookie->{'ag_annotation.images.cb_id'} && defined $cookie->{'ag_annotation.images.cb_id'});
	}

	unless(defined $form->{'cb_id'}){
		my($ci_id,$cb_id) = &get_concent_build_id_from_buildup_logic_id(ci_id => $form->{'ci_id'},bul_id => $form->{'bul_id'});
		if(defined $ci_id && defined $cb_id){
			$form->{'ci_id'} = $ci_id;
			$form->{'cb_id'} = $cb_id;
		}
	}

	unless(defined $form->{'md_id'}){
		$form->{'md_id'} = $form->{'ag_annotation.images.md_id'} if(exists $form->{'ag_annotation.images.md_id'} && defined $form->{'ag_annotation.images.md_id'});
		$form->{'md_id'} = $cookie->{'ag_annotation.images.md_id'} if(!defined $form->{'md_id'} && defined $cookie && exists $cookie->{'ag_annotation.images.md_id'} && defined $cookie->{'ag_annotation.images.md_id'});
		$form->{'md_id'} = &get_def_model_id() unless(defined $form->{'md_id'});
	}

	if(exists($form->{'md_id'}) && (!exists($form->{'mv_id'}) || !exists($form->{'mr_id'}))){
		my $dbh = &get_dbh();
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
  select md_id,md_abbr,md_use from model
 ) as md on mr.md_id=md.md_id
left join (
  select md_id,mv_id,mv_name_e,mv_name_j,mv_order,mv_use,mv_publish from model_version
 ) as mv on mr.md_id=mv.md_id and mr.mv_id=mv.mv_id

where
 md_use and
 mv_use and
 mv_publish and
 mr_use and
SQL
		my @bind_values = ();
		$sql .= qq|mr.md_id=?|;
		push(@bind_values,$form->{'md_id'});
		if(exists $form->{'version'}){
			$sql .= qq| and |;
			if(exists($form->{lng}) && $form->{lng} eq 'ja'){
				$sql .= qq|COALESCE(mv_name_j,mv_name_e)=?|;
			}else{
				$sql .= qq|mv_name_e=?|;
			}
			push(@bind_values,$form->{'version'});
		}
		$sql .= qq| order by mv_order,mr_order limit 1|;

		my $sth_model_version = $dbh->prepare($sql);
		$sth_model_version->execute(@bind_values);
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
		}
		$sth_model_version->finish;
		undef $sth_model_version;

	}

	unless(defined $form->{'mv_id'}){
		$form->{'mv_id'} = $form->{'ag_annotation.images.mv_id'} if(exists $form->{'ag_annotation.images.mv_id'} && defined $form->{'ag_annotation.images.mv_id'});
		$form->{'mv_id'} = $cookie->{'ag_annotation.images.mv_id'} if(!defined $form->{'mv_id'} && defined $cookie && exists $cookie->{'ag_annotation.images.mv_id'} && defined $cookie->{'ag_annotation.images.mv_id'});
		$form->{'mv_id'} = &get_def_model_version_id($form->{'md_id'}) unless(defined $form->{'mv_id'});
	}

	unless(defined $form->{'mr_id'}){
		$form->{'mr_id'} = $form->{'ag_annotation.images.mr_id'} if(exists $form->{'ag_annotation.images.mr_id'} && defined $form->{'ag_annotation.images.mr_id'});
		$form->{'mr_id'} = $cookie->{'ag_annotation.images.mr_id'} if(!defined $form->{'mr_id'} && defined $cookie && exists $cookie->{'ag_annotation.images.mr_id'} && defined $cookie->{'ag_annotation.images.mr_id'});
		$form->{'mr_id'} = &get_def_model_revision_id($form->{'md_id'},$form->{'mv_id'}) unless(defined $form->{'mr_id'});
	}
}

sub get_def_model_id {
	my $dbh = &get_dbh();
	my $md_id;
	my $sth = $dbh->prepare(qq|select md_id from model order by md_order limit 1|) or croak DBI->errstr;
	$sth->execute() or croak DBI->errstr;
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$md_id, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;
	croak "undefined md_id!!" unless(defined $md_id);
	return $md_id;
}

sub get_def_model_version_id {
	my $md_id = shift;
	my $dbh = &get_dbh();
	$md_id = &get_def_model_id() unless(defined $md_id);
	my $mv_id;
	my $sth = $dbh->prepare(qq|select mv_id from model_version where md_id=? order by mv_order limit 1|) or croak DBI->errstr;
	$sth->execute($md_id) or croak DBI->errstr;
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$mv_id, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;
	croak "undefined mv_id!!" unless(defined $mv_id);
	return $mv_id;
}

sub get_def_model_revision_id {
	my $md_id = shift;
	my $mv_id = shift;
	my $dbh = &get_dbh();
	$md_id = &get_def_model_id() unless(defined $md_id);
	$mv_id = &get_def_model_version_id() unless(defined $mv_id);
	my $mr_id;
	my $sth = $dbh->prepare(qq|select mr_id from model_revision where md_id=? and mv_id=? order by mr_order limit 1|) or croak DBI->errstr;
	$sth->execute($md_id,$mv_id) or croak DBI->errstr;
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$mr_id, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;
	croak "undefined mr_id!!" unless(defined $mr_id);
	return $mr_id;
}

sub get_def_buildup_logic_id {
	my $dbh = &get_dbh();
	my $bul_id;
	my $sth = $dbh->prepare(qq|select bul_id from buildup_logic order by bul_order limit 1|) or croak DBI->errstr;
	$sth->execute() or croak DBI->errstr;
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$bul_id, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;
	croak "undefined bul_id!!" unless(defined $bul_id);
	return $bul_id;
}

sub get_def_concept_info_id {
	my $dbh = &get_dbh();
	my $ci_id;
	my $sth = $dbh->prepare(qq|select ci_id from concept_info where ci_name='FMA'|) or croak DBI->errstr;
	$sth->execute() or croak DBI->errstr;
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$ci_id, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;
	croak "undefined ci_id!!" unless(defined $ci_id);
	return $ci_id;
}

sub get_concent_build_id_from_buildup_logic_id {
	my %arg = @_;
	my $dbh = &get_dbh();

	croak "undefined bul_id!!" unless(defined $arg{bul_id});

	my $ci_id = $arg{ci_id} if(exists $arg{ci_id});
	unless(defined $ci_id){
		my $sth = $dbh->prepare(qq|select ci_id from concept_info where ci_name='FMA'|) or croak DBI->errstr;
		$sth->execute() or croak DBI->errstr;
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$ci_id, undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;
	}

	my $cb_id;
	my $sth = $dbh->prepare(qq|select max(cb_id) from buildup_tree where ci_id=? and bul_id=? and but_delcause is null|) or croak DBI->errstr;
	$sth->execute($ci_id,$arg{bul_id}) or croak DBI->errstr;
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$cb_id, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;

	return wantarray ? ($ci_id,$cb_id) : [$ci_id,$cb_id];

}
###############################################################################

####################################
#OBJのイメージ関するもの（ここから）
####################################
sub getArtImageBaseDir {
	my $image_path = '';
	$image_path = qq|$FindBin::Bin/| unless(defined $ENV{'REQUEST_METHOD'});
	$image_path .= qq|art_images|;
	return lc($image_path);
}

sub getArtBaseDirFromName {
	my $name = shift;
	my $image_path;
	if($name =~ /^([A-Z]{2,})(.?)(.?)(.?)(.?)/){
		$image_path = qq|/$1/|.lc(qq|$2$3/$4$5|);
	}else{
		my $t = $name;
		$t =~ s/\s+//g;
		$image_path = lc("/". substr($t,0,2) . "/" . substr($t,2,2));
	}
	$image_path =~ s/\/$//g;
	return $image_path;
}

sub getDefModel {
	my $dbh = &get_dbh();
	my $md_abbr;
	my $sth = $dbh->prepare(qq|select md_abbr from model where md_delcause is null order by md_order limit 1|) or croak DBI->errstr;
	$sth->execute() or croak DBI->errstr;
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$md_abbr, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;
	return $md_abbr;
}

sub getArtImageDir {
	my $name = shift;
	my $model = shift;
	$model = &getDefModel() unless(defined $model && length($model)>0);
	my $image_path = &getArtImageBaseDir();
	$image_path .= qq|/$model|;
	$image_path .= &getArtBaseDirFromName($name);
	$image_path =~ s/\/$//g;
	return $image_path;
}

sub getArtImageFileBasename {
	my $name = shift;
	my $position = shift;
	my $geometry = shift;
	my $credit = shift;

	return undef unless(defined $name);

	$position = &getDefImagePosition() unless(defined $position && length($position)>0);
	$geometry = &getDefImageGeometry() unless(defined $geometry && length($geometry)>0);
	$credit   = &getDefImageCredit()   unless(defined $credit && length($credit)>0);

	my $filename;
	if($position eq "rotate"){
		$filename =  sprintf(qq|%s_%s|,$name,$geometry);
	}else{
		$filename =  sprintf(qq|%s_%s_%s|,$name,$geometry,$position);
	}
	$filename .= '_c' if($credit ne '0');

	return $filename;
}

sub getArtImageFileExtension {
	my $position = shift;

	$position = &getDefImagePosition() unless(defined $position && length($position)>0);
	my $extension;
	if($position eq "rotate"){
		$extension = qq|.gif|;
	}else{
		$extension = qq|.png|;
	}
	return $extension;
}

sub getArtImagePrefix {
	my $name = shift;
	my $model = shift;
	my $position = shift;
	my $geometry = shift;
	my $version = shift;
	my $credit = shift;

	my $image_path = &getArtImageDir($name,$model);
	my $image_prefix = sprintf(qq|$image_path/%s|,&getArtImageFileBasename($name,$position,$geometry,$credit));

	unless(-e $image_path){
		my $m = umask();
		umask(0);
		&File::Path::mkpath($image_path,0,0777);
		umask($m);
	}
	return $image_prefix;
}

sub getArtPath {
	my $name = shift;
	my $model = shift;
	my $version = shift;
	$model = &getDefModel() unless(defined $model && length($model)>0);
	my($n,$d,$e) = fileparse($name,".obj");
	my $prefix = '';
	$prefix = qq|$FindBin::Bin/| unless(defined $ENV{'REQUEST_METHOD'});
	$prefix .= qq|obj/$model|;
	$prefix .= qq|/$version| if(defined $version && length($version)>0);
	$prefix .= qq|/$n.obj|;
	unless(-e $prefix){
		$n =~ s/_/ /g;
		if(-e qq|/ext1/project/WebGL/uploads/DBCLS__FUJIEDA3.0/$n.obj|){
			return qq|/ext1/project/WebGL/uploads/DBCLS__FUJIEDA3.0/$n.obj|;
		}elsif(-e qq|/ext1/project/WebGL/uploads/DBCLS__FUJIEDA2.0/$n.obj|){
			return qq|/ext1/project/WebGL/uploads/DBCLS__FUJIEDA2.0/$n.obj|;
		}
	}
	return $prefix;
}

####################################
#OBJのイメージ関するもの（ここまで）
####################################

####################################
#RepresentationIDのイメージ関するもの（ここから）
####################################
sub getBLDImageBaseDir {
	my $image_path = '';
	$image_path = qq|$FindBin::Bin/| unless(defined $ENV{'REQUEST_METHOD'});
	$image_path .= qq|bldup_images|;
#	&mkpath($image_path) unless(-d $image_path);
	return lc($image_path);
}

sub isBLDID {
	my $bu_id = shift;
	return undef if($bu_id =~ /^FMA[0-9]+$/);
	if($bu_id =~ /^([A-Z]{2,}?)([0-9]+)$/){
		my @BLD = ($1,$2);
		return wantarray ? @BLD : \@BLD;
	}
	if($bu_id =~ /^([A-Z]{2,}?)([A-Za-z0-9])\-([A-Za-z0-9]+)\-([A-Za-z0-9])([A-Za-z0-9])([0-9]{6})([0-9]{6})([0-9]{2})$/){
		my @BLD = ($1,$2,$3,$4,$5,$6,$7,$8);
		return wantarray ? @BLD : \@BLD;
	}
	return undef;
}

sub getBLDBaseDirFromName {
	my $name = shift;
	my $image_path;
#	if($name =~ /^([A-Z]{2,}?)([A-Za-z0-9])\-([A-Za-z0-9]+)\-([A-Za-z0-9])([A-Za-z0-9])([0-9]{6})([0-9]{6})([0-9]{2})$/){
	my $p = &isBLDID($name);
#warn __LINE__,":\$p=[$p]\n";
	if(defined $p){
		$image_path = '/'.join("/",@$p);
	}elsif($name =~ /^([A-Z]{2,})(...?)(...?)/){
		$image_path = qq|/$1/|.lc(qq|$2/$3|);
	}else{
		my $t = $name;
		$t =~ s/\s+//g;
		$image_path = lc("/". substr($t,0,2) . "/" . substr($t,2,2));
	}
	$image_path =~ s/\/$//g;
	$image_path =~ s/^\///g;
	return $image_path;
}

sub getBLDImageDir {
	my $name = shift;
	my $image_path = File::Spec->catdir(&getBLDImageBaseDir(),&getBLDBaseDirFromName($name));
#	$image_path =~ s/\/$//g;
#	&mkpath($image_path) unless(-d $image_path);
	return $image_path;
}

sub getBLDImageFileBasename {
	my $name = shift;
	my $position = shift;
	my $geometry = shift;
	my $credit = shift;

	return undef unless(defined $name);

	$position = &getDefImagePosition() unless(defined $position && length($position)>0);
	$geometry = &getDefImageGeometry() unless(defined $geometry && length($geometry)>0);
	$credit   = &getDefImageCredit()   unless(defined $credit && length($credit)>0);

	my $filename = sprintf(qq|%s_%s|,$name,$geometry);
	$filename .= '_c' if($credit ne '0');
	$filename .=  sprintf(qq|_%s|,$position) if($position ne "rotate");

	return $filename;
}

sub getBLDImageFileExtension {
	my $position = shift;

	$position = &getDefImagePosition() unless(defined $position && length($position)>0);
	my $extension;
	if($position eq "rotate"){
		$extension = qq|.gif|;
	}else{
		$extension = qq|.png|;
	}
	return $extension;
}

sub getBLDImagePrefix {
	my $name = shift;
	my $position = shift;
	my $geometry = shift;
	my $credit = shift;

	my $image_path = &getBLDImageDir($name);
	my $image_prefix = sprintf(qq|$image_path/%s|,&getBLDImageFileBasename($name,$position,$geometry,$credit));

	unless(-e $image_path){
		my $m = umask();
		umask(0);
		&File::Path::mkpath($image_path,0,0777);
		umask($m);
	}
	return $image_prefix;
}

sub getBLDImagePath {
	my $name = shift;
	my $position = shift;
	my $geometry = shift;
	my $credit = shift;
	my $image_prefix = &getBLDImagePrefix($name,$position,$geometry,$credit);
	my $extension = &getBLDImageFileExtension($position);
	return qq|$image_prefix$extension|;
}

sub getBLDArtFilesPath {
	my $bu_id = shift;
	my $out_dir = shift;

	my $dbh = &get_dbh();

	my $prefix = '';
	if(defined $out_dir){
		$prefix = $out_dir;
	}else{
		$prefix = qq|$FindBin::Bin/| unless(defined $ENV{'REQUEST_METHOD'});
		$prefix = File::Spec->catdir($prefix,qq|bld_objs|,&getBLDBaseDirFromName($bu_id));
#		$prefix = File::Spec->catdir($prefix,&getBLDBaseDirFromName($bu_id),qq|art_files|);
	}
#	$prefix .= qq|bld_objs|;
#	$prefix .= &getBLDBaseDirFromName($bu_id);
#	$prefix .= qq|/$bu_id|;
#	$prefix .= qq|/art_files|;

#	$prefix .= qq|/$revision|;
	unless(-e $prefix){
		my $m = umask();
		umask(0);
		&File::Path::mkpath($prefix,0,0777);
		umask($m);
	}

	my @FILES;

	my $art_id;
	my $art_ext;
	my $art_data;
	my $art_entry;

	my $sql=<<SQL;;
select
 o.art_id,
 o.art_ext,
 o.art_data,
 EXTRACT(EPOCH FROM o.art_timestamp)
from
 buildup_concept as b
left join (select rep_id,hist_serial,art_id,art_hist_serial,rep_delcause from history_representation) as r on (r.rep_id=b.rep_id and r.hist_serial=b.rep_hist_serial)
left join (select art_id,hist_serial,art_ext,art_data,art_timestamp,art_delcause from history_art_file) as o on (o.art_id=r.art_id and o.hist_serial=r.art_hist_serial)
where
 r.rep_delcause is null
 and o.art_delcause is null
 and b.bu_id=?
SQL
	my $sth = $dbh->prepare($sql) or croak DBI->errstr;
	$sth->execute($bu_id) or croak DBI->errstr;
	warn __LINE__,":\$sth->rows()=[",$sth->rows(),"]\n";
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$art_id, undef);
	$sth->bind_col(++$column_number, \$art_ext, undef);
	$sth->bind_col(++$column_number, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
	$sth->bind_col(++$column_number, \$art_entry, undef);
	while($sth->fetch){
		next unless(defined $art_id && defined $art_data && defined $art_entry);
		my $objfile = qq|$prefix/$art_id$art_ext|;
		if(-e $objfile){
			push(@FILES,$objfile);
			next;
		}
		my $OUT;
		open($OUT,"> $objfile") or die "$!:$objfile\n";
		flock($OUT,2);
		binmode($OUT);
		print $OUT $art_data;
		close($OUT);
		utime($art_entry,$art_entry,$objfile);
		push(@FILES,$objfile);
	}
	$sth->finish;
	undef $sth;

	if(scalar @FILES > 0){
		return wantarray ? @FILES : \@FILES;
	}else{
		return undef;
	}
}

####################################
#RepresentationIDのイメージ関するもの（ここまで）
####################################







###############################################################################
sub ExecuteSQL {
	my $sql = $_[0];
	my @DATA = ();
	my $sth = $mydb->prepare($sql);
	$sth->execute();
	while(my @row = $sth->fetchrow_array()){
		push(@DATA,join("\t",@row));
		undef @row;
	}
	$sth->finish();
	undef $sth;
	return(@DATA);
}

sub existsTable {
	my $tablename = shift;
	return 0 unless(defined $tablename);
	my $dbh = &get_dbh();
	my $sth = $dbh->prepare(qq|select tablename from pg_tables where tablename=?|);
	$sth->execute($tablename);
	my $rows = $sth->rows();
	undef $sth;
	return $rows;
}

sub existsTableColumn {
	my $tablename = shift;
	my $columnname = shift;
	return 0 unless(defined $tablename && defined $columnname);
	my $dbh = &get_dbh();
	my $sth = $dbh->prepare(qq|SELECT column_name FROM information_schema.columns WHERE table_name=? AND column_name=?|);
	$sth->execute($tablename,$columnname);
	my $rows = $sth->rows();
	undef $sth;
	return $rows;
}

sub getIndexnamesFromTablename {
	my $tablename = shift;
	return undef unless(defined $tablename);
	my @RTN = ();
	my $dbh = &get_dbh();
	my $sth = $dbh->prepare(qq|select indexname from pg_indexes where tablename=?|);
	$sth->execute($tablename);
	my $rows = $sth->rows();
	my $indexname;
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$indexname, undef);
	while($sth->fetch){
		push(@RTN,$indexname) if(defined $indexname);
	}
	$sth->finish;
	undef $sth;
	return wantarray ? @RTN : \@RTN;
}

sub existsView {
	my $viewname = shift;
	return 0 unless(defined $viewname);
	my $dbh = &get_dbh();
	my $sth = $dbh->prepare(qq|select viewname from pg_views where viewname=?|);
	$sth->execute($viewname);
	my $rows = $sth->rows();
	undef $sth;
	return $rows;
}

sub getDbTableColumns {
	my $tablename = shift;
	return undef unless(defined $tablename);
	my @RTN = ();
	my $dbh = &get_dbh();
#	my $sth = $dbh->prepare(qq|select * from information_schema.columns where table_name=?|);
	my $sth = $dbh->prepare(qq|select column_name,data_type,ordinal_position from information_schema.columns where table_name=?|);
	$sth->execute($tablename);
	while(my $href = $sth->fetchrow_hashref){
		push(@RTN,$href);
	}
	$sth->finish;
	undef $sth;
	return scalar @RTN > 0 ? (wantarray ? @RTN : \@RTN) : undef;
}

my $sth_tree_path2root;
sub getTree_Path2Root {
	my $form = shift;
	my $f_id = shift;
	my $TREE_ROUTE = shift;
	my $route = shift;

	my $dbh = &get_dbh();
#	$sth_tree_path2root = $dbh->prepare(qq|select f_pid,t_delcause from tree where f_id=? and t_type=? and tg_id=? and tgi_id=?|) unless(defined $sth_tree_path2root);
	$sth_tree_path2root = $dbh->prepare(qq|select cdi_pname,but_delcause from view_buildup_tree where cdi_name=? and bul_id=? and ci_id=? and cb_id=?|) unless(defined $sth_tree_path2root);

	my $exists_flag;
	my $t_delcause_flag;

	unless(defined $route){
		$route = $f_id;
	}else{
		my @TEMP_ROUTE = split(/\t/,$route);
		foreach my $temp_fid (@TEMP_ROUTE){
			next if(!($temp_fid eq $f_id));
			$exists_flag = 1;
			last;
		}
		$route .= qq|\t$f_id|;
	}

	my @F_PID = ();
	unless(defined $exists_flag){
		$sth_tree_path2root->execute($f_id,$form->{bul_id},$form->{ci_id},$form->{cb_id});
		if($sth_tree_path2root->rows>0){
			my $f_pid;
			my $t_delcause;
			my $column_number = 0;
			$sth_tree_path2root->bind_col(++$column_number, \$f_pid, undef);
			$sth_tree_path2root->bind_col(++$column_number, \$t_delcause, undef);
			while($sth_tree_path2root->fetch){
				if(defined $t_delcause){
					$t_delcause_flag = 1;
				}else{
					push(@F_PID,$f_pid);
				}
			}
		}
		$sth_tree_path2root->finish;
	}
	if(scalar @F_PID > 0){
		foreach my $f_pid (@F_PID){
			&getTree_Path2Root($form,$f_pid,$TREE_ROUTE,$route);
			last if(scalar @TREE_ROUTE > 100);
		}
	}elsif(!defined $exists_flag && !defined $t_delcause_flag){
		push(@$TREE_ROUTE,$route);
	}
}

my $sth_fma_phy;
sub get_phy_id {
	my $f_id = shift;
	my $phy_id;
	my $dbh = &get_dbh();
	$f_id =~ s/\D+$//g if($f_id =~ /^FMA\d+/);
	$sth_fma_phy = $dbh->prepare(qq|select phy_id from fma where f_id=?|) unless(defined $sth_fma_phy);
	$sth_fma_phy->execute($f_id);
	my $column_number = 0;
	$sth_fma_phy->bind_col(++$column_number, \$phy_id, undef);
	$sth_fma_phy->fetch;
	$sth_fma_phy->finish;
	return $phy_id;
}

1;
