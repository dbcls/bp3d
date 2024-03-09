#!/bp3d/local/perl/bin/perl

select(STDERR);
$| = 1;
select(STDOUT);
$| = 1;

use strict;
exit 1 unless(defined $ARGV[0] && -e $ARGV[0]);

#use CGI;
#use CGI::Carp qw(fatalsToBrowser);
use Cwd qw(abs_path);
use File::Basename;
use File::Spec::Functions;
use File::Copy;
use File::Path;
use JSON::XS;
use Encode;
use DBD::Pg;
use Digest::MD5;
use Time::HiRes;
use Cwd;

use constant {
	DEBUG => 1
};
my $json = JSON::XS->new->utf8->indent( DEBUG )->canonical(1);
if(DEBUG){
	use Data::Dumper;
	$Data::Dumper::Indent = 1;
	$Data::Dumper::Sortkeys = 1;
}

#$CGI::POST_MAX = 1024 * 1024 * 1000;	# 1024 * 1KBytes = 1MBytes.

#my $lib_path;
#BEGIN{ $lib_path = dirname(abs_path($0)).qq|/../local/usr/lib/perl|; }
#use lib $lib_path;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;

use BITS::Config;
use BITS::Archive;
use BITS::Obj2Hash;
#use BITS::FileConvert;
use BITS::VTK;
use BITS::Voxel;

require "webgl_common.pl";
use cgi_lib::common;

my $dbh = &get_dbh();

my $RTN = {
	success => JSON::XS::true,
	progress => {
		'value' => 0,
		'msg' => 'start'
	}
};

my $PARAMS;
$PARAMS = &cgi_lib::common::readFileJSON($ARGV[0]) if(scalar @ARGV && defined $ARGV[0] && -e $ARGV[0] && -f $ARGV[0]);

exit 1 unless(defined $PARAMS && ref $PARAMS eq 'HASH');
&saveStatus($RTN);

$SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit";
sub sigexit {
	my($date) = `date`;
	$date =~ s/\s*$//g;
	$RTN->{'msg'} = $RTN->{'progress'}->{'msg'} = qq|Error:[$date] KILL THIS SCRIPT!!|;
	$RTN->{'success'} = JSON::XS::false;
	&saveStatus($RTN);
	exit(1);
}

#delete $PARAMS->{'upload_file'};

sub reg_files {
	my $dbh = shift;
	my $PARAMS = shift;
#	my $upload_file = shift;
	my $upload_file_info = shift;
	my $upload_file;

	if(defined $upload_file_info && ref $upload_file_info eq 'HASH' && exists $upload_file_info->{'local_path'}){
		$upload_file = $upload_file_info->{'local_path'};
	}else{
		$upload_file = $upload_file_info;
	}

	return unless(defined $upload_file);
	unless(ref $upload_file){
		$upload_file = &cgi_lib::common::decodeUTF8($upload_file);
		return unless(-e $upload_file);
	}

	my($upload_name,$upload_dir,$upload_ext) = &File::Basename::fileparse($upload_file,@BITS::Archive::ExtList);

	my $prefix_id = $PARAMS->{'prefix_id'} - 0;
	unless(defined $prefix_id){
		$RTN->{'msg'} = $RTN->{'progress'}->{'msg'} = qq|Error:Unknown prefix_id [$prefix_id]!!|;
		$RTN->{'success'} = JSON::XS::false;
		&saveStatus($RTN);
		exit(1);
	}

	my $artf_id;
	$artf_id = $PARAMS->{'artf_id'} - 0 if(exists $PARAMS->{'artf_id'} && defined $PARAMS->{'artf_id'});

	my $files;
	$files = &cgi_lib::common::decodeJSON($PARAMS->{'files'}) if(exists $PARAMS->{'files'} && defined $PARAMS->{'files'} && length $PARAMS->{'files'});

	my $CODE = "UTF8";
	my $encode = "utf8";
	if($PARAMS->{'HTTP_USER_AGENT'}=~/Windows/){
		$CODE = "SJIS";
		$encode = "shift-jis";
	}elsif($PARAMS->{'HTTP_USER_AGENT'}=~/Macintosh/){
		$CODE = "SJIS";
		$encode = "shift-jis";
	}

	$RTN->{'msg'} = $RTN->{'progress'}->{'msg'} = &cgi_lib::common::decodeUTF8(qq|Uncompress: $upload_name$upload_ext|);
	&saveStatus($RTN);

	my $upload_dir = $BITS::Config::UPLOAD_PATH;
	my $prefix = &catdir($upload_dir,qq|.$upload_name|);
	&File::Path::rmtree($prefix) if(-e $prefix);
	my $FILES;
	eval{
		$FILES = &BITS::Archive::extract($upload_file,$prefix,$encode);
	};
	if($@){
		$RTN->{'msg'} = $RTN->{'progress'}->{'msg'} = &cgi_lib::common::decodeUTF8(qq|$@ [$upload_name$upload_ext]|);
		$RTN->{'success'} = JSON::XS::false;
		&saveStatus($RTN);
		exit(1);
	}
	unless(defined $FILES && ref $FILES eq 'ARRAY' && scalar @$FILES){
		$RTN->{'msg'} = $RTN->{'progress'}->{'msg'} = &cgi_lib::common::decodeUTF8(qq|You can not extract the files. [$upload_name$upload_ext]|);
		$RTN->{'success'} = JSON::XS::false;
		&saveStatus($RTN);
		exit(1);
	}

#	if(DEBUG){
#		print &Data::Dumper::Dumper($FILES);
#		$RTN->{'msg'} = $RTN->{'progress'}->{'msg'} = qq|You can not extract the files. [$upload_name$upload_ext]|;
#		$RTN->{'success'} = JSON::XS::false;
#		&saveStatus($RTN);
#		exit(1);
#	}

#	die qq|You can not extract the files. [$upload_name$upload_ext]|;
#	die qq|exit.|;


	$dbh->do(qq|SET CLIENT_ENCODING TO '$CODE'|);


	my $openid = qq|system|;
	my $sql =<<SQL;
insert into art_file (
  prefix_id,
  art_name,
  art_ext,
  art_timestamp,
  art_md5,
  art_data,
  art_data_size,
  art_xmin,
  art_xmax,
  art_ymin,
  art_ymax,
  art_zmin,
  art_zmax,
  art_volume,
  art_raw_data,
  art_raw_data_size
) values (
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?
)
RETURNING art_id
SQL
	my $sth_art_ins = $dbh->prepare($sql) or die $dbh->errstr;


	$sql =<<SQL;
update art_file set
  art_name=?,
  art_ext=?,
  art_timestamp=?,
  art_delcause=null,
  art_modified=now()
where
  art_id=?
SQL
	my $sth_art_upd = $dbh->prepare($sql) or die $dbh->errstr;

	$sql =<<SQL;
update art_file_info set
  art_name=?,
  art_ext=?,
  art_timestamp=?,
  art_modified=now(),
  art_delcause=null
where
  art_id=?
SQL
	my $sth_arti_upd = $dbh->prepare($sql) or die $dbh->errstr;

	my $sql_insert_art_file_info =<<SQL;
INSERT INTO
 art_file_info
 (
 art_id,
 art_name,
 art_ext,
 art_timestamp,
 art_mirroring,
 art_entry,
 art_openid,
 prefix_id,
 art_serial,
 art_md5,
 art_data_size,
 art_xmin,
 art_xmax,
 art_ymin,
 art_ymax,
 art_zmin,
 art_zmax,
 art_volume
 )
SELECT
 art_id,
 art_name,
 art_ext,
 art_timestamp,
 art_mirroring,
 art_entry,
 art_openid,
 prefix_id,
 art_serial,
 art_md5,
 art_data_size,
 art_xmin,
 art_xmax,
 art_ymin,
 art_ymax,
 art_zmin,
 art_zmax,
 art_volume
FROM
 art_file
WHERE
 art_id=?
SQL
	my $sth_arti_ins = $dbh->prepare($sql_insert_art_file_info) or die $dbh->errstr;


	my $sth_artff_sel = $dbh->prepare(qq|select * from art_folder_file where COALESCE(artf_id,0)=COALESCE(?,0) and art_id=?|) or die $dbh->errstr;
	my $sth_artff_ins = $dbh->prepare(qq|insert into art_folder_file (artf_id,art_id) values (?,?)|) or die $dbh->errstr;

	$dbh->do(qq|SELECT pg_catalog.setval('art_folder_artf_id_seq',(select max(artf_id) from art_folder))|) or die $dbh->errstr;
	my $sth_artf_sel = $dbh->prepare(qq|select artf_id from art_folder where artf_use and COALESCE(artf_pid,0)=COALESCE(?,0) and artf_name=?|) or die $dbh->errstr;
	my $sth_artf_ins = $dbh->prepare(qq|insert into art_folder (artf_pid,artf_name,artf_use) values (?,?,true) RETURNING artf_id|) or die $dbh->errstr;

	my @LIST = ();

	my $artg_timestamp;
	if(-e $upload_file){
		my($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime((stat($upload_file))[9]);
		$year = $year + 1900;
		$month  += 1;
		$artg_timestamp = sprintf("%04d-%02d-%02d %02d:%02d:%02d",$year,$month,$mday,$hour,$min,$sec);
	}else{
		my($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime();
		$year = $year + 1900;
		$month  += 1;
		$artg_timestamp = sprintf("%04d-%02d-%02d %02d:%02d:%02d",$year,$month,$mday,$hour,$min,$sec);
	}

	my @extlist = qw|.obj .json|;

	my $progress = 0;

	foreach my $file (@$FILES){
		&Encode::from_to($file,$encode,'utf8');
		&cgi_lib::common::message($file);
	}

	$FILES = [sort {-l $b <=> -l $a} @$FILES];
	foreach my $file (@$FILES){
		&cgi_lib::common::message($file);
	}
#die __LINE__;

	foreach my $file (@$FILES){

#		&Encode::from_to($file,$encode,'utf8');
		my $basename = &File::Basename::basename($file);

		$progress++;
		$RTN->{'msg'} = &cgi_lib::common::decodeUTF8(qq|Registration: $upload_name$upload_ext|);
		$RTN->{'progress'} = {
			'value' => $progress/(scalar @$FILES + 1),
			'msg' => &cgi_lib::common::decodeUTF8(qq|[$progress/|.(scalar @$FILES).qq|] $basename|)
		};
		&saveStatus($RTN);

		&cgi_lib::common::message($upload_file_info);
		my $rel_path;
		my $rel_dir_path;
		if(-e $prefix && -d $prefix){
			$rel_path = &abs2rel($file,$prefix);
		}else{
			$rel_path = &abs2rel($file,$upload_dir);
		}
		if(exists $PARAMS->{'maintain_upload_directory_structure'} && defined $PARAMS->{'maintain_upload_directory_structure'} && $PARAMS->{'maintain_upload_directory_structure'} eq '1'){
			$rel_dir_path = &File::Basename::dirname($rel_path);
		}else{
			$rel_dir_path = '.';
		}
		&cgi_lib::common::message($rel_path);
		&cgi_lib::common::message($rel_dir_path);
		&cgi_lib::common::message($file);
		&cgi_lib::common::message(-s $file);
#		die __LINE__;

		next unless(-s $file);
#			print __LINE__,":\$file=[$file]\n";
		open(my $IN,$file) or die qq|$! [$file]|;
		my @DATAS = <$IN>;
		close($IN);
		my @v =  grep(/^v\s+\S+\s+\S+\s+\S+/, @DATAS);
		my @vn = grep(/^vn\s+\S+\s+\S+\s+\S+/, @DATAS);
		my @f =  grep(/^f\s+\S+\s+\S+\s+\S+/, @DATAS);

#		print __LINE__.':'.(scalar @v)."\n";
#		print __LINE__.':'.(scalar @vn)."\n";
#		print __LINE__.':'.(scalar @f)."\n";

		&cgi_lib::common::message(scalar @v);
		&cgi_lib::common::message(scalar @vn);
		&cgi_lib::common::message(scalar @f);

		next unless(scalar @v && scalar @vn && scalar @f);
		undef @v;
		undef @vn;
		undef @f;

		my($name,$dir,$ext) = &File::Basename::fileparse($file,@extlist);
		my($obj_org_size,$obj_org_mtime) = (stat($file))[7,9];

		my $obj_prefix = &catfile($dir,$name);
		my $obj_norm_prefix = qq|$obj_prefix.norm|;
		my $obj_deci_prefix = qq|$obj_prefix.deci|;
		my $obj_org_prefix  = qq|$obj_prefix.org|;

		my $obj_ext = qq|.obj|;
		my $obj_file = qq|$obj_prefix$obj_ext|;
		my $obj_norm_file = qq|$obj_norm_prefix$obj_ext|;
		my $obj_raw_file = qq|$obj_org_prefix$obj_ext|;
		my $obj_deci_file = qq|$obj_deci_prefix$obj_ext|;

		&cgi_lib::common::message(&File::Basename::basename($upload_file_info->{'local_path'}));
		&cgi_lib::common::message(&File::Basename::basename($file));

		if(defined $files && ref $files eq 'HASH' && exists $files->{qq|$name$ext|} && defined $files->{qq|$name$ext|} && ref $files->{qq|$name$ext|} eq 'HASH'){
			&cgi_lib::common::message($files->{qq|$name$ext|}->{'last'});
			$obj_org_mtime = $files->{qq|$name$ext|}->{'last'} - 0;
		}
		elsif(defined $upload_file_info && ref $upload_file_info eq 'HASH' && exists $upload_file_info->{'last'}){
			if(exists $upload_file_info->{'local_path'} && defined $upload_file_info->{'local_path'} && length $upload_file_info->{'local_path'}){
				my $local_basename = &File::Basename::basename(&cgi_lib::common::decodeUTF8($upload_file_info->{'local_path'}));
				my $file_basename = &File::Basename::basename(&cgi_lib::common::decodeUTF8($file));
				&cgi_lib::common::message($local_basename);
				&cgi_lib::common::message($file_basename);
				if($local_basename eq $file_basename){
					&cgi_lib::common::message($upload_file_info->{'last'});
					$obj_org_mtime = $upload_file_info->{'last'} - 0;
				}
			}
		}else{
			&cgi_lib::common::message(scalar @$FILES);
			&cgi_lib::common::message($upload_file_info);
		}

		my $art_ext = $ext;
		my($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime($obj_org_mtime);
		$year = $year + 1900;
		$month  += 1;
		my $art_timestamp = sprintf("%04d-%02d-%02d %02d:%02d:%02d",$year,$month,$mday,$hour,$min,$sec);


		&File::Copy::move($file,$obj_raw_file);
		utime $obj_org_mtime,$obj_org_mtime,$obj_raw_file;

		my $obj_org_prop = &BITS::VTK::getProperties($obj_raw_file);
		next unless(defined $obj_org_prop && ref $obj_org_prop eq 'HASH' && ref $obj_org_prop->{'bounds'} eq 'ARRAY');

		&cgi_lib::common::dumper($obj_org_prop);

		my $art_xmin = $obj_org_prop->{'bounds'}->[0] - 0;
		my $art_xmax = $obj_org_prop->{'bounds'}->[1] - 0;
		my $art_ymin = $obj_org_prop->{'bounds'}->[2] - 0;
		my $art_ymax = $obj_org_prop->{'bounds'}->[3] - 0;
		my $art_zmin = $obj_org_prop->{'bounds'}->[4] - 0;
		my $art_zmax = $obj_org_prop->{'bounds'}->[5] - 0;
		my $art_volume = defined $obj_org_prop->{'volume'} && $obj_org_prop->{'volume'} > 0 ?  &Truncated($obj_org_prop->{'volume'} / 1000) : 0;
#		my $art_cube_volume = &Truncated(($art_xmax-$art_xmin)*($art_ymax-$art_ymin)*($art_zmax-$art_zmin)/1000);

#		print __LINE__."\n";
		&BITS::VTK::obj2normals($obj_raw_file,$obj_norm_prefix);
#		print __LINE__."\n";
		next unless(-e $obj_norm_file && -s $obj_norm_file);
#		print __LINE__."\n";

		my $art_data = &readObjFile($obj_norm_file);
		my $art_data_size = length($art_data);
		unless($art_data_size>0){
#				warn "Unknown size [$art_data_size][$obj_norm_file]\n";
			next;
		}

		my $art_md5 = &Digest::MD5::md5_hex($art_data);

		my $art_id;
		my $art_name = $name;
#		my $sth_art_file = $dbh->prepare(qq|select art_id from art_file where md5(art_data)=md5(?) AND art_data=? AND prefix_id=? order by art_serial desc limit 1|) or die $dbh->errstr;
#		$sth_art_file->execute($art_data,$art_data,$prefix_id) or die $dbh->errstr;
		my $sth_art_file = $dbh->prepare(qq|select art_id from art_file where md5(art_data)=md5(?) AND art_data=? order by prefix_id desc,art_serial desc limit 1|) or die $dbh->errstr;
		$sth_art_file->execute($art_data,$art_data) or die $dbh->errstr;
		my $art_file_rows = $sth_art_file->rows();
		if($art_file_rows>0){
			$sth_art_file->bind_col(1, \$art_id, undef);
			$sth_art_file->fetch;
		}
		$sth_art_file->finish;

		my $art_raw_data;

		#オリジナルのファイルでも確認する
		unless(defined $art_id){
			$art_raw_data = &readObjFile($obj_raw_file);

			$sth_art_file->execute($art_raw_data,$art_raw_data) or die $dbh->errstr;
			$art_file_rows = $sth_art_file->rows();
			if($art_file_rows>0){
				$sth_art_file->bind_col(1, \$art_id, undef);
				$sth_art_file->fetch;
			}
			$sth_art_file->finish;
			if(defined $art_id){

				$art_data = $art_raw_data;
				$art_data_size = length($art_raw_data);
				$art_md5 = &Digest::MD5::md5_hex($art_raw_data);

				$art_xmin = undef;
				$art_xmax = undef;
				$art_ymin = undef;
				$art_ymax = undef;
				$art_zmin = undef;
				$art_zmax = undef;
				$art_volume = undef;
#				$art_cube_volume = undef;

#				my $sth = $dbh->prepare(qq|select art_xmin,art_xmax,art_ymin,art_ymax,art_zmin,art_zmax,art_volume,art_cube_volume from art_file where art_id=?|) or die $dbh->errstr;
				my $sth = $dbh->prepare(qq|select art_xmin,art_xmax,art_ymin,art_ymax,art_zmin,art_zmax,art_volume from art_file where art_id=?|) or die $dbh->errstr;
				$sth->execute($art_id) or die $dbh->errstr;
				my $rows = $sth->rows();
				if($rows>0){
					my $column_number = 0;
					$sth->bind_col(++$column_number, \$art_xmin, undef);
					$sth->bind_col(++$column_number, \$art_xmax, undef);
					$sth->bind_col(++$column_number, \$art_ymin, undef);
					$sth->bind_col(++$column_number, \$art_ymax, undef);
					$sth->bind_col(++$column_number, \$art_zmin, undef);
					$sth->bind_col(++$column_number, \$art_zmax, undef);
					$sth->bind_col(++$column_number, \$art_volume, undef);
#					$sth->bind_col(++$column_number, \$art_cube_volume, undef);
					$sth->fetch;
				}
				$sth->finish;
				undef $sth;
			}
		}

		undef $sth_art_file;

		my $param_num = 0;
		unless(defined $art_id){
			my $art_raw_data = &readFile($obj_raw_file);
			my $art_raw_data_size = length($art_raw_data);

			$param_num = 0;
			$sth_art_ins->bind_param(++$param_num, $PARAMS->{'prefix_id'});
			$sth_art_ins->bind_param(++$param_num, $art_name);
			$sth_art_ins->bind_param(++$param_num, $art_ext);
			$sth_art_ins->bind_param(++$param_num, $art_timestamp);
			$sth_art_ins->bind_param(++$param_num, $art_md5);
			$sth_art_ins->bind_param(++$param_num, $art_data, { pg_type => DBD::Pg::PG_BYTEA });
			$sth_art_ins->bind_param(++$param_num, $art_data_size);
			$sth_art_ins->bind_param(++$param_num, $art_xmin);
			$sth_art_ins->bind_param(++$param_num, $art_xmax);
			$sth_art_ins->bind_param(++$param_num, $art_ymin);
			$sth_art_ins->bind_param(++$param_num, $art_ymax);
			$sth_art_ins->bind_param(++$param_num, $art_zmin);
			$sth_art_ins->bind_param(++$param_num, $art_zmax);
			$sth_art_ins->bind_param(++$param_num, $art_volume);
			$sth_art_ins->bind_param(++$param_num, $art_raw_data, { pg_type => DBD::Pg::PG_BYTEA });
			$sth_art_ins->bind_param(++$param_num, $art_raw_data_size);
			$sth_art_ins->execute() or die $dbh->errstr;
			my $rows = $sth_art_ins->rows();
			$sth_art_ins->bind_col(1, \$art_id, undef);
			$sth_art_ins->fetch;
			$sth_art_ins->finish();

			&cgi_lib::common::message($art_id);

			$sth_arti_ins->execute($art_id) or die $dbh->errstr;
			$sth_arti_ins->finish();

			&BITS::Voxel::insVoxelData($dbh,$art_id,$art_data);
		}
		else{
			if($art_name =~ /^${art_id}_/){
				$art_name =~ s/^${art_id}_//g;
			}
			$param_num = 0;
			$sth_art_upd->bind_param(++$param_num, $art_name);
			$sth_art_upd->bind_param(++$param_num, $art_ext);
			$sth_art_upd->bind_param(++$param_num, $art_timestamp);
			$sth_art_upd->bind_param(++$param_num, $art_id);
			$sth_art_upd->execute() or die $dbh->errstr;
			$sth_art_upd->finish();

			$param_num = 0;
			$sth_arti_upd->bind_param(++$param_num, $art_name);
			$sth_arti_upd->bind_param(++$param_num, $art_ext);
			$sth_arti_upd->bind_param(++$param_num, $art_timestamp);
			$sth_arti_upd->bind_param(++$param_num, $art_id);
			$sth_arti_upd->execute() or die $dbh->errstr;
			my $arti_upd_rows = $sth_arti_upd->rows();
			$sth_arti_upd->finish();
			if($arti_upd_rows<1){
				$sth_arti_ins->execute($art_id) or die $dbh->errstr;
				$sth_arti_ins->finish();
			}
		}

		if(defined $art_id){

			if(defined $PARAMS->{'art_org_info'} && defined $PARAMS->{'arto_id'}){
				my $sth_arto_upd = $dbh->prepare(qq|update art_file_info set arto_id=?,arto_comment=? where art_id=?|) or die $dbh->errstr;
				$sth_arto_upd->execute($PARAMS->{'arto_id'},$PARAMS->{'arto_comment'},$art_id) or die $dbh->errstr;
				$sth_arto_upd->finish;
				undef $sth_arto_upd;
			}else{
				my $sth_arto_del = $dbh->prepare(qq|update art_file_info set arto_id=NULL,arto_comment=NULL where art_id=?|) or die $dbh->errstr;
				$sth_arto_del->execute($art_id) or die $dbh->errstr;
				$sth_arto_del->finish;
				undef $sth_arto_del;
			}
		}

		if(-e $obj_norm_file){
			utime $obj_org_mtime,$obj_org_mtime,$obj_norm_file;
			my $copy_file = &catfile($FindBin::Bin,'..','art_file',qq|$art_id$art_ext|);
			if(-e $copy_file && -f $copy_file){
				my($copy_size,$copy_mtime) = (stat($copy_file))[7,9];
				unlink $copy_file unless($copy_size == $art_data_size && $copy_mtime == $obj_org_mtime);
			}
			unless(-e $copy_file && -f $copy_file){
				&File::Copy::copy($obj_norm_file,$copy_file);
				utime $obj_org_mtime,$obj_org_mtime,$copy_file;
			}
		}

		if(defined $art_id){
			my $temp_artf_id = $artf_id;
			unless($rel_dir_path eq '.'){
				my @dirs = &splitdir($rel_dir_path);
#				&cgi_lib::common::message(\@dirs);
				foreach my $dir (@dirs){
					$sth_artf_sel->execute($temp_artf_id,$dir) or die $dbh->errstr;
					my $artf_rows = $sth_artf_sel->rows();
					if($artf_rows>0){
						my $column_number = 0;
						$sth_artf_sel->bind_col(++$column_number, \$temp_artf_id, undef);
						$sth_artf_sel->fetch;
					}
					$sth_artf_sel->finish;
					unless($artf_rows>0){
						$sth_artf_ins->execute($temp_artf_id,$dir) or die $dbh->errstr;
						my $column_number = 0;
						$sth_artf_ins->bind_col(++$column_number, \$temp_artf_id, undef);
						$sth_artf_ins->fetch;
						$sth_artf_ins->finish;
					}
					die __LINE__ unless(defined $temp_artf_id);
				}
			}
			$sth_artff_sel->execute($temp_artf_id,$art_id) or die $dbh->errstr;
			my $artff_rows = $sth_artff_sel->rows();
			$sth_artff_sel->finish;
			unless($artff_rows){
				$sth_artff_ins->execute($temp_artf_id,$art_id) or die $dbh->errstr;
				$sth_artff_ins->finish;
			}
			&cgi_lib::common::message(qq|$art_id,$temp_artf_id,$artff_rows|);
		}

		push(@LIST,{
			name       => $name,
			mtime      => $obj_org_mtime,
			size       => $obj_org_size,
			xmin       => $obj_org_prop->{'bounds'}->[0] - 0,
			xmax       => $obj_org_prop->{'bounds'}->[1] - 0,
			ymin       => $obj_org_prop->{'bounds'}->[2] - 0,
			ymax       => $obj_org_prop->{'bounds'}->[3] - 0,
			zmin       => $obj_org_prop->{'bounds'}->[4] - 0,
			zmax       => $obj_org_prop->{'bounds'}->[5] - 0,
			xcenter    => $obj_org_prop->{'centers'}->[0] - 0,
			ycenter    => $obj_org_prop->{'centers'}->[1] - 0,
			zcenter    => $obj_org_prop->{'centers'}->[2] - 0,
			org_points => $obj_org_prop->{'points'} - 0,
			org_polys  => $obj_org_prop->{'polys'} - 0,
			volume     => defined $obj_org_prop->{'volume'} && $obj_org_prop->{'volume'} > 0 ?  &Truncated($obj_org_prop->{'volume'} / 1000) : 0,
			art_id     => $art_id,
			art_name   => $art_name,
			art_ext    => $art_ext,
			art_md5    => $art_md5
		});
#die "exit.";
	}


	if(-e $prefix){
		if(scalar @LIST > 0){
			@LIST = sort {$b->{'zcenter'} <=> $a->{'zcenter'}} @LIST;
			&cgi_lib::common::writeFileJSON(&catfile($prefix,qq|all.json|),\@LIST);

			my($name,$dir,$ext) = &File::Basename::fileparse($upload_file,@BITS::Archive::ExtList);
			my $to = &catdir($upload_dir,$name);
			&File::Path::rmtree($to) if(-e $to);
			&File::Copy::move($prefix,$to);
		}
	}
#	undef @LIST;
	return \@LIST;

#	$dbh->do($sql_insert_art_file_info) or die $dbh->errstr;
}

$dbh->{'AutoCommit'} = 0;
$dbh->{'RaiseError'} = 1;
eval{
	&cgi_lib::common::message($PARAMS);
	my $list;
	my $upload_file = $PARAMS->{'upload_file'} if(exists $PARAMS->{'upload_file'} && defined $PARAMS->{'upload_file'});
	my $upload_files = $PARAMS->{'upload_files'} if(exists $PARAMS->{'upload_files'} && defined $PARAMS->{'upload_files'} && ref $PARAMS->{'upload_files'} eq 'ARRAY');
	if(defined $upload_file){
		&cgi_lib::common::message($upload_file);
		push(@$list, @{&reg_files($dbh,$PARAMS,$upload_file)});
	}elsif(defined $upload_files){
		&cgi_lib::common::message($upload_files);
		foreach my $_upload_file (@$upload_files){
			push(@$list, @{&reg_files($dbh,$PARAMS,$_upload_file)});
		}
	}else{
		die qq|Undefined Upload file|;
	}
#	die __LINE__;
	$dbh->commit;
	$dbh->do("NOTIFY art_file");
	if(defined $upload_file){
		my($upload_name,$upload_dir,$upload_ext);
		if(defined $upload_file && ref $upload_file eq 'HASH' && exists $upload_file->{'local_path'}){
			($upload_name,$upload_dir,$upload_ext) = &File::Basename::fileparse(&cgi_lib::common::decodeUTF8($upload_file->{'local_path'}),@BITS::Archive::ExtList);
		}else{
			($upload_name,$upload_dir,$upload_ext) = &File::Basename::fileparse(&cgi_lib::common::decodeUTF8($upload_file),@BITS::Archive::ExtList);
		}
		$RTN->{'file'} = &cgi_lib::common::decodeUTF8(qq|$upload_name$upload_ext|);
	}elsif(defined $upload_files){
		$RTN->{'files'} = [];
		foreach my $_upload_file (@$upload_files){
			my($upload_name,$upload_dir,$upload_ext);
			if(defined $_upload_file && ref $_upload_file eq 'HASH' && exists $_upload_file->{'local_path'}){
				($upload_name,$upload_dir,$upload_ext) = &File::Basename::fileparse(&cgi_lib::common::decodeUTF8($_upload_file->{'local_path'}),@BITS::Archive::ExtList);
			}else{
				($upload_name,$upload_dir,$upload_ext) = &File::Basename::fileparse(&cgi_lib::common::decodeUTF8($_upload_file),@BITS::Archive::ExtList);
			}
			push(@{$RTN->{'files'}},&cgi_lib::common::decodeUTF8(qq|$upload_name$upload_ext|));
		}
	}
	$RTN->{'success'} = JSON::XS::true;
	$RTN->{'progress'}->{'value'} = 1;
	$RTN->{'progress'}->{'msg'} = 'end';



	my $prog_basename = qq|make_art_image|;
	my $prog = &catfile($FindBin::Bin,'..','cron',qq|$prog_basename.pl|);
	if(-e $prog && -x $prog){
		my @PARAMS;
		push(@PARAMS,'-h',$ENV{'AG_DB_HOST'});
		push(@PARAMS,'-p',$ENV{'AG_DB_PORT'});

		if(defined $list && ref $list eq 'ARRAY' && scalar @$list){
			my %H = map {$_->{'art_id'} => undef} @$list;
			push(@PARAMS,'-o',join(',',sort {$a cmp $b} keys(%H)));
		}
		my $params = join(' ',@PARAMS);

		my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
		my $mfmt = sprintf("%04d%02d%02d%02d%02d%02d.%d",$year+1900,$mon+1,$mday,$hour,$min,$sec,$$);

		my $pid = fork;
		if(defined $pid){
			if($pid == 0){
				my $logdir = &getLogDir();
				my $f1 = &catfile($logdir,qq|$prog_basename.log.$mfmt|);
				my $f2 = &catfile($logdir,qq|$prog_basename.err.$mfmt|);
				close(STDOUT);
				close(STDERR);
				open STDOUT, "> $f1" || die "[$f1] $!\n";
				open STDERR, "> $f2" || die "[$f2] $!\n";
				close(STDIN);
				exec(qq|nice -n 19 $prog $params|);
				exit(1);
			}else{
				$RTN->{'success'} = JSON::XS::true;
			}
		}else{
			die("Can't execute program");
		}
	}

};
if($@){
	$RTN->{'msg'} = &cgi_lib::common::decodeUTF8($@);
	$dbh->rollback;
	$RTN->{'success'} = JSON::XS::false;
	$RTN->{'progress'}->{'msg'} = &cgi_lib::common::decodeUTF8('Error:'.$@);
}
$dbh->{'AutoCommit'} = 1;
$dbh->{'RaiseError'} = 0;


&saveStatus($RTN);

exit;

sub saveStatus {
	my $RTN = shift;
	&cgi_lib::common::message(&cgi_lib::common::encodeJSON($RTN,1));
	&cgi_lib::common::writeFileJSON($ARGV[0],$RTN);
}
