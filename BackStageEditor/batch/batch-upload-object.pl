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
my $dbh = &get_dbh();

my $RTN = {
	success => JSON::XS::true,
	progress => {
		'value' => 0,
		'msg' => 'start'
	}
};

my $PARAMS;
{
	my $IN;
	open($IN,"< $ARGV[0]") or die $!;
	flock($IN,1);
	my @DATAS = <$IN>;
	close($IN);
	$PARAMS = $json->decode(join('',@DATAS));
	undef @DATAS;
}
exit 1 unless(defined $PARAMS);
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
	my $upload_file = shift;
	return unless(defined $upload_file && -e $upload_file);
	my($group_name,$group_dir,$group_ext) = &File::Basename::fileparse($upload_file,@BITS::Archive::ExtList);

	my $prefix_id = $PARAMS->{'prefix_id'};
	unless(defined $prefix_id){
		$RTN->{'msg'} = $RTN->{'progress'}->{'msg'} = qq|Error:Unknown prefix_id [$prefix_id]!!|;
		$RTN->{'success'} = JSON::XS::false;
		&saveStatus($RTN);
		exit(1);
	}

	my $CODE = "UTF8";
	my $encode = "utf8";
	if($PARAMS->{'HTTP_USER_AGENT'}=~/Windows/){
		$CODE = "SJIS";
		$encode = "shift-jis";
	}elsif($PARAMS->{'HTTP_USER_AGENT'}=~/Macintosh/){
		$CODE = "SJIS";
		$encode = "shift-jis";
	}

	$RTN->{'msg'} = $RTN->{'progress'}->{'msg'} = qq|Uncompress: $group_name$group_ext|;
	&saveStatus($RTN);

	my $upload_dir = $BITS::Config::UPLOAD_PATH;
	my $prefix = &catdir($upload_dir,qq|.$group_name|);
	&File::Path::rmtree($prefix) if(-e $prefix);
	my $FILES;
	eval{
		$FILES = &BITS::Archive::extract($upload_file,$prefix,$encode);
	};
	if($@){
		$RTN->{'msg'} = $RTN->{'progress'}->{'msg'} = qq|$@ [$group_name$group_ext]|;
		$RTN->{'success'} = JSON::XS::false;
		&saveStatus($RTN);
		exit(1);
	}
	unless(defined $FILES && ref $FILES eq 'ARRAY' && scalar @$FILES){
		$RTN->{'msg'} = $RTN->{'progress'}->{'msg'} = qq|You can not extract the files. [$group_name$group_ext]|;
		$RTN->{'success'} = JSON::XS::false;
		&saveStatus($RTN);
		exit(1);
	}

#	if(DEBUG){
#		print &Data::Dumper::Dumper($FILES);
#		$RTN->{'msg'} = $RTN->{'progress'}->{'msg'} = qq|You can not extract the files. [$group_name$group_ext]|;
#		$RTN->{'success'} = JSON::XS::false;
#		&saveStatus($RTN);
#		exit(1);
#	}

#	die qq|You can not extract the files. [$group_name$group_ext]|;
#	die qq|exit.|;


	$dbh->do(qq|SET CLIENT_ENCODING TO '$CODE'|);


	my $openid = qq|system|;
	my $sql =<<SQL;
insert into art_file (
  md_id,
  mv_id,
  mr_id,
  artg_id,
  prefix_id,
  art_name,
  art_ext,
  art_timestamp,
  art_md5,
  art_data,
  art_data_size,
  art_decimate,
  art_decimate_size,
  art_xmin,
  art_xmax,
  art_ymin,
  art_ymax,
  art_zmin,
  art_zmax,
  art_volume,
  art_cube_volume,
  art_openid
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
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  '$openid'
)
RETURNING art_id
;
SQL
	my $sth_art_ins = $dbh->prepare($sql) or die $dbh->errstr;


	my $sql =<<SQL;
insert into art_file (
  md_id,
  mv_id,
  mr_id,
  artg_id,
  prefix_id,
  art_name,
  art_ext,
  art_timestamp,
  art_md5,
  art_data,
  art_data_size,
  art_decimate,
  art_decimate_size,
  art_xmin,
  art_xmax,
  art_ymin,
  art_ymax,
  art_zmin,
  art_zmax,
  art_volume,
  art_cube_volume,
  art_id,
  art_openid
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
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  '$openid'
)
;
SQL
	my $sth_art_ins2 = $dbh->prepare($sql) or die $dbh->errstr;


	my $sql =<<SQL;
update art_file set
  md_id=?,
  mv_id=?,
  mr_id=?,
  artg_id=?,
  prefix_id=?,
  art_name=?,
  art_ext=?,
  art_timestamp=?,
  art_md5=?,
  art_data=?,
  art_data_size=?,
  art_decimate=?,
  art_decimate_size=?,
  art_xmin=?,
  art_xmax=?,
  art_ymin=?,
  art_ymax=?,
  art_zmin=?,
  art_zmax=?,
  art_volume=?,
  art_cube_volume=?,
  art_openid='$openid'
where
  art_id=?
;
SQL
	my $sth_art_upd = $dbh->prepare($sql) or die $dbh->errstr;


	my $sql =<<SQL;
insert into art_file_info (
  artg_id,
  art_id,
  art_name,
  art_ext,
  art_timestamp,
  art_openid
) values (
  ?,
  ?,
  ?,
  ?,
  ?,
  '$openid'
)
;
SQL
	my $sth_arti_ins = $dbh->prepare($sql) or die $dbh->errstr;



	my @LIST = ();
	my $artg_id;

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


	my $progress = 0;
	foreach my $file (@$FILES){
		my $basename = &File::Basename::basename($file);
		&Encode::from_to($basename,$encode,'utf8');
		$progress++;
		$RTN->{'msg'} = qq|Registration: $group_name$group_ext|;
		$RTN->{'progress'} = {
			'value' => $progress/(scalar @$FILES + 1),
			'msg' => qq|[$progress/|.(scalar @$FILES).qq|] $basename|
		};
		&saveStatus($RTN);

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

		next unless(scalar @v && scalar @vn && scalar @f);
		undef @v;
		undef @vn;
		undef @f;

		my @extlist = qw|.obj .json|;
		my($name,$dir,$ext) = &File::Basename::fileparse($file,@extlist);
		my($obj_size,$obj_mtime) = (stat($file))[7,9];
		my $obj_prefix = &catfile($dir,$name);
		my $obj_deci_prefix = &catfile($dir,$name.qq|.deci|);
		my $org_file = qq|$obj_prefix.org.obj|;
		my $obj_file = qq|$obj_prefix.obj|;
		my $obj_deci_file = qq|$obj_deci_prefix.obj|;

		my $art_ext = $ext;
		my($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime($obj_mtime);
		$year = $year + 1900;
		$month  += 1;
		my $art_timestamp = sprintf("%04d-%02d-%02d %02d:%02d:%02d",$year,$month,$mday,$hour,$min,$sec);


		&File::Copy::move($file,$org_file);
		my $obj_prop = &BITS::VTK::getProperties($org_file);
		print &Data::Dumper::Dumper($obj_prop);

		my $art_xmin = $obj_prop->{'bounds'}->[0];
		my $art_xmax = $obj_prop->{'bounds'}->[1];
		my $art_ymin = $obj_prop->{'bounds'}->[2];
		my $art_ymax = $obj_prop->{'bounds'}->[3];
		my $art_zmin = $obj_prop->{'bounds'}->[4];
		my $art_zmax = $obj_prop->{'bounds'}->[5];
		my $art_volume = defined $obj_prop->{'volume'} && $obj_prop->{'volume'} > 0 ?  &Truncated($obj_prop->{'volume'} / 1000) : 0;
		my $art_cube_volume = &Truncated(($art_xmax-$art_xmin)*($art_ymax-$art_ymin)*($art_zmax-$art_zmin)/1000);

#		print __LINE__."\n";
		&BITS::VTK::obj2normals($org_file,$obj_prefix);
#		print __LINE__."\n";
		next if(-e $obj_file && -z $obj_file);
#		print __LINE__."\n";

		my $cmd = qq{sed -e "/^mtllib/d" "$obj_file" | sed -e "/^#/d" | sed -e "/^ *\$/d" |};
		my $art_data = &readFile($cmd);
		my $art_data_size = length($art_data);
		unless($art_data_size>0){
#				warn "Unknown size [$art_data_size][$obj_file]\n";
			next;
		}

		my $cmd = qq{sed -e "/^mtllib/d" "$org_file" | sed -e "/^#/d" | sed -e "/^ *\$/d" |};
		my $org_art_data = &readFile($cmd);
		my $org_art_data_size = length($org_art_data);
#		unless($art_data_size>0){
#				warn "Unknown size [$art_data_size][$obj_file]\n";
#			next;
#		}
		my $art_decimate;

		my $art_md5 = &Digest::MD5::md5_hex($art_data);
		my $org_art_md5 = &Digest::MD5::md5_hex($org_art_data);

		my $art_id;
		my $art_name = $name;
		my $sth_art_file = $dbh->prepare(qq|select art_id from art_file where md5(art_data)=md5(?) AND art_data=? AND prefix_id=? order by art_serial desc limit 1|) or die $dbh->errstr;
		$sth_art_file->execute($art_data,$art_data,$prefix_id) or die $dbh->errstr;
		my $art_file_rows = $sth_art_file->rows();
		if($art_file_rows>0){
			$sth_art_file->bind_col(1, \$art_id, undef);
			$sth_art_file->fetch;
		}
		$sth_art_file->finish;
#warn __LINE__,":[$obj_file][$art_md5][$org_art_md5][$art_id]\n";

		#オリジナルのファイルでも確認する
		unless(defined $art_id){
			$sth_art_file->execute($org_art_data,$org_art_data,$prefix_id) or die $dbh->errstr;
			my $art_file_rows = $sth_art_file->rows();
			if($art_file_rows>0){
				$sth_art_file->bind_col(1, \$art_id, undef);
				$sth_art_file->fetch;
			}
			$sth_art_file->finish;
			if(defined $art_id){
				$art_data = $org_art_data;
				$art_data_size = $org_art_data_size;
				$art_md5 = $org_art_md5;

				undef $sth_art_file;

				$art_xmin = undef;
				$art_xmax = undef;
				$art_ymin = undef;
				$art_ymax = undef;
				$art_zmin = undef;
				$art_zmax = undef;
				$art_volume = undef;
				$art_cube_volume = undef;

				$sth_art_file = $dbh->prepare(qq|select art_xmin,art_xmax,art_ymin,art_ymax,art_zmin,art_zmax,art_volume,art_cube_volume,art_decimate from art_file where art_id=?|) or die $dbh->errstr;
				$sth_art_file->execute($art_id) or die $dbh->errstr;
				my $art_file_rows = $sth_art_file->rows();
				if($art_file_rows>0){
					my $column_number = 0;
					$sth_art_file->bind_col(++$column_number, \$art_xmin, undef);
					$sth_art_file->bind_col(++$column_number, \$art_xmax, undef);
					$sth_art_file->bind_col(++$column_number, \$art_ymin, undef);
					$sth_art_file->bind_col(++$column_number, \$art_ymax, undef);
					$sth_art_file->bind_col(++$column_number, \$art_zmin, undef);
					$sth_art_file->bind_col(++$column_number, \$art_zmax, undef);
					$sth_art_file->bind_col(++$column_number, \$art_volume, undef);
					$sth_art_file->bind_col(++$column_number, \$art_cube_volume, undef);
					$sth_art_file->bind_col(++$column_number, \$art_decimate, { pg_type => DBD::Pg::PG_BYTEA });
					$sth_art_file->fetch;
				}
				$sth_art_file->finish;
			}
		}

		undef $sth_art_file;
#warn __LINE__,":[$obj_file][$art_md5][$org_art_md5][$art_id]\n";

		#過去のデータから検索
		unless(defined $art_id){
			my $hist_serial;
			my $sth_art_file = $dbh->prepare(qq|select art_id,hist_serial from history_art_file where md5(art_data)=md5(?) AND art_data=? AND prefix_id=? order by art_serial asc,hist_serial desc limit 1|) or die $dbh->errstr;
			$sth_art_file->execute($art_data,$art_data,$prefix_id) or die $dbh->errstr;
			if($sth_art_file->rows()>0){
				$sth_art_file->bind_col(1, \$art_id, undef);
				$sth_art_file->bind_col(2, \$hist_serial, undef);
				$sth_art_file->fetch;
			}
			$sth_art_file->finish;

			#オリジナルのファイルでも確認する
			unless(defined $art_id){
				$sth_art_file->execute($org_art_data,$org_art_data,$prefix_id) or die $dbh->errstr;
				my $art_file_rows = $sth_art_file->rows();
				if($art_file_rows>0){
					$sth_art_file->bind_col(1, \$art_id, undef);
					$sth_art_file->bind_col(2, \$hist_serial, undef);
					$sth_art_file->fetch;
				}
				$sth_art_file->finish;
				if(defined $art_id && defined $hist_serial){
					$art_data = $org_art_data;
					$art_data_size = $org_art_data_size;
					$art_md5 = $org_art_md5;

					undef $sth_art_file;

					$art_xmin = undef;
					$art_xmax = undef;
					$art_ymin = undef;
					$art_ymax = undef;
					$art_zmin = undef;
					$art_zmax = undef;
					$art_volume = undef;
					$art_cube_volume = undef;

					$sth_art_file = $dbh->prepare(qq|select art_xmin,art_xmax,art_ymin,art_ymax,art_zmin,art_zmax,art_volume,art_cube_volume,art_decimate from history_art_file where art_id=? and hist_serial=?|) or die $dbh->errstr;
					$sth_art_file->execute($art_id,$hist_serial) or die $dbh->errstr;
					my $art_file_rows = $sth_art_file->rows();
					if($art_file_rows>0){
						my $column_number = 0;
						$sth_art_file->bind_col(++$column_number, \$art_xmin, undef);
						$sth_art_file->bind_col(++$column_number, \$art_xmax, undef);
						$sth_art_file->bind_col(++$column_number, \$art_ymin, undef);
						$sth_art_file->bind_col(++$column_number, \$art_ymax, undef);
						$sth_art_file->bind_col(++$column_number, \$art_zmin, undef);
						$sth_art_file->bind_col(++$column_number, \$art_zmax, undef);
						$sth_art_file->bind_col(++$column_number, \$art_volume, undef);
						$sth_art_file->bind_col(++$column_number, \$art_cube_volume, undef);
						$sth_art_file->bind_col(++$column_number, \$art_decimate, { pg_type => DBD::Pg::PG_BYTEA });
						$sth_art_file->fetch;
					}
					$sth_art_file->finish;
				}
			}
			undef $sth_art_file;
		}

#warn __LINE__,":[$obj_file][$art_md5][$org_art_md5][$art_id]\n";
#warn __LINE__,":\$art_group_rows=[$art_group_rows]\n";

		my $art_group_rows = 0;
		unless(defined $artg_id){
			my $sth_art_group = $dbh->prepare(qq|select artg_id from art_group where artg_name=?|) or die $dbh->errstr;
			$sth_art_group->execute($group_name) or die $dbh->errstr;
			$art_group_rows = $sth_art_group->rows();
			$sth_art_group->bind_col(1, \$artg_id, undef);
			$sth_art_group->fetch;
			$sth_art_group->finish;
			undef $sth_art_group;
		}else{
			my $sth_art_group = $dbh->prepare(qq|select artg_id from art_group where artg_id=?|) or die $dbh->errstr;
			$sth_art_group->execute($artg_id) or die $dbh->errstr;
			$art_group_rows = $sth_art_group->rows();
			$sth_art_group->finish;
			undef $sth_art_group;
		}
		unless(defined $artg_id){
			my $sth_art_group = $dbh->prepare(qq|select artg_id from history_art_group where artg_name=?|) or die $dbh->errstr;
			$sth_art_group->execute($group_name) or die $dbh->errstr;
			$sth_art_group->bind_col(1, \$artg_id, undef);
			$sth_art_group->fetch;
			$sth_art_group->finish;
			undef $sth_art_group;
		}

#warn __LINE__,":\$artg_id=[$artg_id]\n";
#warn __LINE__,":\$art_group_rows=[$art_group_rows]\n";

		unless(defined $artg_id && $art_group_rows>0){
			if(defined $artg_id){
				my $sth_art_group_ins = $dbh->prepare(qq|insert into art_group (md_id,mv_id,mr_id,artg_id,artg_name,artg_timestamp,atrg_use,artg_openid,artf_id) values (?,?,?,?,?,?,true,?,?)|) or die $dbh->errstr;
				$sth_art_group_ins->execute($PARAMS->{'md_id'},$PARAMS->{'mv_id'},$PARAMS->{'mr_id'},$artg_id,$group_name,$artg_timestamp,$openid,$PARAMS->{'artf_id'}) or die $dbh->errstr;
				$sth_art_group_ins->finish;
				undef $sth_art_group_ins;
			}else{
				my $sth_art_group_ins = $dbh->prepare(qq|insert into art_group (md_id,mv_id,mr_id,artg_name,artg_timestamp,atrg_use,artg_openid,artf_id) values (?,?,?,?,?,true,?,?) RETURNING artg_id|) or die $dbh->errstr;
				$sth_art_group_ins->execute($PARAMS->{'md_id'},$PARAMS->{'mv_id'},$PARAMS->{'mr_id'},$group_name,$artg_timestamp,$openid,$PARAMS->{'artf_id'}) or die $dbh->errstr;
				$sth_art_group_ins->bind_col(1, \$artg_id, undef);
				$sth_art_group_ins->fetch;
				$sth_art_group_ins->finish;
				undef $sth_art_group_ins;
			}
		}else{
			my $temp_artg_timestamp_epoch;
			my $temp_artg_timestamp;
			my $temp_artf_id;
			my $sth_art_group = $dbh->prepare(qq|select EXTRACT(EPOCH FROM artg_timestamp),artf_id from art_group where artg_id=?|) or die $dbh->errstr;
			$sth_art_group->execute($artg_id) or die $dbh->errstr;
			$sth_art_group->bind_col(1, \$temp_artg_timestamp_epoch, undef);
			$sth_art_group->bind_col(2, \$temp_artf_id, undef);
			$sth_art_group->fetch;
			$sth_art_group->finish;
			undef $sth_art_group;
			if(defined $temp_artg_timestamp_epoch){
				my($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime($temp_artg_timestamp_epoch);
				$year = $year + 1900;
				$month  += 1;
				$temp_artg_timestamp = sprintf("%04d-%02d-%02d %02d:%02d:%02d",$year,$month,$mday,$hour,$min,$sec);
			}
			if($artg_timestamp ne $temp_artg_timestamp || $PARAMS->{'artf_id'} ne $temp_artf_id){
				my $sth_art_group_upd = $dbh->prepare(qq|update art_group set artg_timestamp=?,artf_id=? where artg_id=?|) or die $dbh->errstr;
				$sth_art_group_upd->execute($artg_timestamp,$PARAMS->{'artf_id'},$artg_id) or die $dbh->errstr;
				$sth_art_group_upd->finish;
				undef $sth_art_group_upd;
			}
		}


		unless(defined $art_id && $art_file_rows>0){
			unless(defined $art_decimate){
				&BITS::VTK::quadricDecimation($org_file,$obj_deci_prefix);
				my $cmd = qq{sed -e "/^mtllib/d" "$obj_deci_file" | sed -e "/^#/d" | sed -e "/^ *\$/d" |};
				$art_decimate = &readFile($cmd);
			}
			my $art_decimate_size = length($art_decimate);


#				$art_name = qq|$group_name/$name$ext|;
			my $param_num = 0;
			if(defined $art_id){

				my $sth_art_file = $dbh->prepare(qq|select art_id from art_file where art_id=?|) or die $dbh->errstr;
				$sth_art_file->execute($art_id) or die $dbh->errstr;
				my $art_file_rows = $sth_art_file->rows();
				$sth_art_file->finish;
				undef $sth_art_file;

				my $sth;
				if($art_file_rows>0){
=pod
					my $sql =<<SQL;
select
  md_id,
  mv_id,
  mr_id,
  artg_id,
  prefix_id,
  art_name,
  art_ext,
  EXTRACT(EPOCH FROM art_timestamp),
  art_md5,
  art_data,
  art_data_size,
  art_decimate,
  art_decimate_size,
  art_xmin,
  art_xmax,
  art_ymin,
  art_ymax,
  art_zmin,
  art_zmax,
  art_volume,
  art_cube_volume
from
  art_file
where
  art_id=?
SQL

					my $temp_md_id;
					my $temp_mv_id;
					my $temp_mr_id;
					my $temp_artg_id;
					my $temp_prefix_id;
					my $temp_art_name;
					my $temp_art_ext;
					my $temp_art_timestamp_epoch;
					my $temp_art_timestamp;
					my $temp_art_md5;
					my $temp_art_data;
					my $temp_art_data_size;
					my $temp_art_decimate;
					my $temp_art_decimate_size;
					my $temp_art_xmin;
					my $temp_art_xmax;
					my $temp_art_ymin;
					my $temp_art_ymax;
					my $temp_art_zmin;
					my $temp_art_zmax;
					my $temp_art_volume;
					my $temp_art_cube_volume;

					my $sth_art_file = $dbh->prepare($sql) or die $dbh->errstr;
					$sth_art_file->execute($art_id) or die $dbh->errstr;
					if($sth_art_file->rows()>0){
						my $column_number = 0;
						$sth_art_file->bind_col(++$column_number, \$temp_md_id, undef);
						$sth_art_file->bind_col(++$column_number, \$temp_mv_id, undef);
						$sth_art_file->bind_col(++$column_number, \$temp_mr_id, undef);
						$sth_art_file->bind_col(++$column_number, \$temp_artg_id, undef);
						$sth_art_file->bind_col(++$column_number, \$temp_prefix_id, undef);
						$sth_art_file->bind_col(++$column_number, \$temp_art_name, undef);
						$sth_art_file->bind_col(++$column_number, \$temp_art_ext, undef);
						$sth_art_file->bind_col(++$column_number, \$temp_art_timestamp_epoch, undef);
						$sth_art_file->bind_col(++$column_number, \$temp_art_md5, undef);
						$sth_art_file->bind_col(++$column_number, \$temp_art_data, { pg_type => DBD::Pg::PG_BYTEA });
						$sth_art_file->bind_col(++$column_number, \$temp_art_data_size, undef);
						$sth_art_file->bind_col(++$column_number, \$temp_art_decimate, { pg_type => DBD::Pg::PG_BYTEA });
						$sth_art_file->bind_col(++$column_number, \$temp_art_decimate_size, undef);
						$sth_art_file->bind_col(++$column_number, \$temp_art_xmin, undef);
						$sth_art_file->bind_col(++$column_number, \$temp_art_xmax, undef);
						$sth_art_file->bind_col(++$column_number, \$temp_art_ymin, undef);
						$sth_art_file->bind_col(++$column_number, \$temp_art_ymax, undef);
						$sth_art_file->bind_col(++$column_number, \$temp_art_zmin, undef);
						$sth_art_file->bind_col(++$column_number, \$temp_art_zmax, undef);
						$sth_art_file->bind_col(++$column_number, \$temp_art_volume, undef);
						$sth_art_file->bind_col(++$column_number, \$temp_art_cube_volume, undef);
						$sth_art_file->fetch;
					}
					$sth_art_file->finish;
					undef $sth_art_file;

					if(defined $temp_art_timestamp_epoch){
						my($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime($temp_art_timestamp_epoch);
						$year = $year + 1900;
						$month  += 1;
						$temp_art_timestamp = sprintf("%04d-%02d-%02d %02d:%02d:%02d",$year,$month,$mday,$hour,$min,$sec);
					}
					unless(
						$PARAMS->{'md_id'} eq $temp_md_id &&
						$PARAMS->{'mv_id'} eq $temp_mv_id &&
						$PARAMS->{'mr_id'} eq $temp_mr_id &&
						$artg_id eq $temp_artg_id &&
						$PARAMS->{'prefix_id'} eq $temp_prefix_id &&
						$art_name eq $temp_art_name &&
						$art_ext eq $temp_art_ext &&
						$art_timestamp eq $temp_art_timestamp &&
						$art_md5 eq $temp_art_md5 &&
						$art_data eq $temp_art_data &&
						$art_data_size eq $temp_art_data_size &&
						$art_decimate eq $temp_art_decimate &&
						$art_decimate_size eq $temp_art_decimate_size &&
						$art_xmin eq $temp_art_xmin &&
						$art_xmax eq $temp_art_xmax &&
						$art_ymin eq $temp_art_ymin &&
						$art_ymax eq $temp_art_ymax &&
						$art_zmin eq $temp_art_zmin &&
						$art_zmax eq $temp_art_zmax &&
						$art_volume eq $temp_art_volume &&
						$art_cube_volume eq $temp_art_cube_volume
					){
						$sth = $sth_art_upd;
					}
=cut
				}else{
					$sth = $sth_art_ins2;
				}
				if(defined $sth){
					$sth->bind_param(++$param_num, $PARAMS->{'md_id'});
					$sth->bind_param(++$param_num, $PARAMS->{'mv_id'});
					$sth->bind_param(++$param_num, $PARAMS->{'mr_id'});
					$sth->bind_param(++$param_num, $artg_id);
					$sth->bind_param(++$param_num, $PARAMS->{'prefix_id'});
					$sth->bind_param(++$param_num, $art_name);
					$sth->bind_param(++$param_num, $art_ext);
					$sth->bind_param(++$param_num, $art_timestamp);
					$sth->bind_param(++$param_num, $art_md5);
					$sth->bind_param(++$param_num, $art_data, { pg_type => DBD::Pg::PG_BYTEA });
					$sth->bind_param(++$param_num, $art_data_size);
					$sth->bind_param(++$param_num, $art_decimate, { pg_type => DBD::Pg::PG_BYTEA });
					$sth->bind_param(++$param_num, $art_decimate_size);
					$sth->bind_param(++$param_num, $art_xmin);
					$sth->bind_param(++$param_num, $art_xmax);
					$sth->bind_param(++$param_num, $art_ymin);
					$sth->bind_param(++$param_num, $art_ymax);
					$sth->bind_param(++$param_num, $art_zmin);
					$sth->bind_param(++$param_num, $art_zmax);
					$sth->bind_param(++$param_num, $art_volume);
					$sth->bind_param(++$param_num, $art_cube_volume);
					$sth->bind_param(++$param_num, $art_id);
					$sth->execute() or die $dbh->errstr;
					$sth->finish();
				}
			}else{
				$sth_art_ins->bind_param(++$param_num, $PARAMS->{'md_id'});
				$sth_art_ins->bind_param(++$param_num, $PARAMS->{'mv_id'});
				$sth_art_ins->bind_param(++$param_num, $PARAMS->{'mr_id'});
				$sth_art_ins->bind_param(++$param_num, $artg_id);
				$sth_art_ins->bind_param(++$param_num, $PARAMS->{'prefix_id'});
				$sth_art_ins->bind_param(++$param_num, $art_name);
				$sth_art_ins->bind_param(++$param_num, $art_ext);
				$sth_art_ins->bind_param(++$param_num, $art_timestamp);
				$sth_art_ins->bind_param(++$param_num, $art_md5);
				$sth_art_ins->bind_param(++$param_num, $art_data, { pg_type => DBD::Pg::PG_BYTEA });
				$sth_art_ins->bind_param(++$param_num, $art_data_size);
				$sth_art_ins->bind_param(++$param_num, $art_decimate, { pg_type => DBD::Pg::PG_BYTEA });
				$sth_art_ins->bind_param(++$param_num, $art_decimate_size);
				$sth_art_ins->bind_param(++$param_num, $art_xmin);
				$sth_art_ins->bind_param(++$param_num, $art_xmax);
				$sth_art_ins->bind_param(++$param_num, $art_ymin);
				$sth_art_ins->bind_param(++$param_num, $art_ymax);
				$sth_art_ins->bind_param(++$param_num, $art_zmin);
				$sth_art_ins->bind_param(++$param_num, $art_zmax);
				$sth_art_ins->bind_param(++$param_num, $art_volume);
				$sth_art_ins->bind_param(++$param_num, $art_cube_volume);
				$sth_art_ins->execute() or die $dbh->errstr;
				my $rows = $sth_art_ins->rows();
				$sth_art_ins->bind_col(1, \$art_id, undef);
				$sth_art_ins->fetch;
				$sth_art_ins->finish();
			}

			&BITS::Voxel::insVoxelData($dbh,$art_id,0,$art_data);
		}

		if(defined $art_id){

			my $sth_arti_sel = $dbh->prepare(qq|select art_name,art_ext,artg_id,EXTRACT(EPOCH FROM art_timestamp) from art_file_info where art_id=?|) or die $dbh->errstr;
			$sth_arti_sel->execute($art_id) or die $dbh->errstr;
			my $arti_rows = $sth_arti_sel->rows();
			$sth_arti_sel->finish;
			undef $sth_arti_sel;

			unless($arti_rows>0){
				my $param_num = 0;
				$sth_arti_ins->bind_param(++$param_num, $artg_id);
				$sth_arti_ins->bind_param(++$param_num, $art_id);
				$sth_arti_ins->bind_param(++$param_num, $art_name);
				$sth_arti_ins->bind_param(++$param_num, $art_ext);
				$sth_arti_ins->bind_param(++$param_num, $art_timestamp);
				$sth_arti_ins->execute() or die $dbh->errstr;
				$sth_arti_ins->finish();
			}else{
				my $temp_art_name;
				my $temp_art_ext;
				my $temp_art_timestamp;
				my $temp_art_timestamp_epoch;
				my $temp_artg_id;

				my $sth_arti_sel = $dbh->prepare(qq|select art_name,art_ext,artg_id,EXTRACT(EPOCH FROM art_timestamp) from art_file_info where art_id=?|) or die $dbh->errstr;
				$sth_arti_sel->execute($art_id) or die $dbh->errstr;
				$sth_arti_sel->bind_col(1, \$temp_art_name, undef);
				$sth_arti_sel->bind_col(2, \$temp_art_ext, undef);
				$sth_arti_sel->bind_col(3, \$temp_artg_id, undef);
				$sth_arti_sel->bind_col(4, \$temp_art_timestamp_epoch, undef);
				$sth_arti_sel->fetch;
				$sth_arti_sel->finish;
				undef $sth_arti_sel;
				if(defined $temp_art_timestamp_epoch){
					my($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime($temp_art_timestamp_epoch);
					$year = $year + 1900;
					$month  += 1;
					$temp_art_timestamp = sprintf("%04d-%02d-%02d %02d:%02d:%02d",$year,$month,$mday,$hour,$min,$sec);
				}
				unless(
					$art_name eq $temp_art_name &&
					$art_ext eq $temp_art_ext &&
					$artg_id eq $temp_artg_id &&
					$art_timestamp eq $temp_art_timestamp
				){
					my $sth_arti_upd = $dbh->prepare(qq|update art_file_info set art_name=?,art_ext=?,artg_id=?,art_timestamp=? where art_id=?|) or die $dbh->errstr;
					$sth_arti_upd->execute($art_name,$art_ext,$artg_id,$art_timestamp,$art_id) or die $dbh->errstr;
					$sth_arti_upd->finish;
					undef $sth_arti_upd;
				}
			}

			my $sth_arto_sel = $dbh->prepare(qq|select art_id from art_org_info where art_id=?|) or die $dbh->errstr;
			$sth_arto_sel->execute($art_id) or die $dbh->errstr;
			my $sth_arto_rows = $sth_arto_sel->rows();
			$sth_arto_sel->finish;
			undef $sth_arto_sel;

			if(defined $PARAMS->{'art_org_info'} && defined $PARAMS->{'arto_id'}){
				if($sth_arto_rows>0){
					my $sth_arto_upd = $dbh->prepare(qq|update art_org_info set arto_id=?,arto_comment=?,arto_entry=now(),arto_openid='system' where art_id=?|) or die $dbh->errstr;
					$sth_arto_upd->execute($PARAMS->{'arto_id'},$PARAMS->{'arto_comment'},$art_id) or die $dbh->errstr;
					$sth_arto_upd->finish;
					undef $sth_arto_upd;
				}else{
					my $sth_arto_ins = $dbh->prepare(qq|insert into art_org_info (arto_id,arto_comment,arto_entry,arto_openid,art_id) values (?,?,now(),'system',?)|) or die $dbh->errstr;
					$sth_arto_ins->execute($PARAMS->{'arto_id'},$PARAMS->{'arto_comment'},$art_id) or die $dbh->errstr;
					$sth_arto_ins->finish;
					undef $sth_arto_ins;
				}
			}elsif($sth_arto_rows>0){
				my $sth_arto_del = $dbh->prepare(qq|delete from art_org_info where art_id=?|) or die $dbh->errstr;
				$sth_arto_del->execute($art_id) or die $dbh->errstr;
				$sth_arto_del->finish;
				undef $sth_arto_del;
			}
		}

#			print __LINE__,qq|:[$group_name][$obj_file]\n| unless(defined $art_id);

		utime $obj_mtime,$obj_mtime,$obj_file if(-e $obj_file);

		push(@LIST,{
			name       => $name,
			mtime      => $obj_mtime,
			size       => $obj_size,
			xmin       => $obj_prop->{'bounds'}->[0],
			xmax       => $obj_prop->{'bounds'}->[1],
			ymin       => $obj_prop->{'bounds'}->[2],
			ymax       => $obj_prop->{'bounds'}->[3],
			zmin       => $obj_prop->{'bounds'}->[4],
			zmax       => $obj_prop->{'bounds'}->[5],
			xcenter    => $obj_prop->{'centers'}->[0],
			ycenter    => $obj_prop->{'centers'}->[1],
			zcenter    => $obj_prop->{'centers'}->[2],
			org_points => $obj_prop->{'points'},
			org_polys  => $obj_prop->{'polys'},
			volume     => defined $obj_prop->{'volume'} && $obj_prop->{'volume'} > 0 ?  &Truncated($obj_prop->{'volume'} / 1000) : 0,
			art_id     => $art_id,
			art_name   => $art_name,
			art_ext    => $art_ext,
			art_md5    => $art_md5
		});
#die "exit.";
	}

#print Dumper(\@LIST),"\n";
#&File::Path::rmtree($prefix) if(-e $prefix);
#return;

	if(scalar @LIST > 0){
		@LIST = sort {$b->{'zcenter'} <=> $a->{'zcenter'}} @LIST;
		my $all = &catfile($prefix,qq|all.json|);
		open(OUT,"> $all");
		print OUT $json->encode(\@LIST);
		close(OUT);

		my($name,$dir,$ext) = &File::Basename::fileparse($upload_file,@BITS::Archive::ExtList);
		my $to = &catdir($upload_dir,$name);
		&File::Path::rmtree($to) if(-e $to);
		&File::Copy::move($prefix,$to);

		my $htdocs_dir = $BITS::Config::HTDOCS_PATH;
		my $js_uploads = qq|$htdocs_dir/js/uploads|;
		&File::Path::mkpath($js_uploads,{mode=>0777}) unless(-e $js_uploads);
		chmod 0777,$js_uploads;
		$js_uploads .= qq|/$name|;
		unlink $js_uploads if(-e $js_uploads);
		symlink $to, $js_uploads;
	}

#バックグラウンドでは動作しない
#		&make_art_images(\@LIST);

	undef @LIST;
}
#=cut
#print qq|Content-type: text/html; charset=UTF-8\n\n|;
#print qq|{success:true,file:"$PARAMS{'file'}"}|;

$dbh->{AutoCommit} = 0;
$dbh->{RaiseError} = 1;
eval{
	my $upload_file = $PARAMS->{'upload_file'} if(exists $PARAMS->{'upload_file'} && defined $PARAMS->{'upload_file'} && -e $PARAMS->{'upload_file'});
	my $upload_files = $PARAMS->{'upload_files'} if(exists $PARAMS->{'upload_files'} && defined $PARAMS->{'upload_files'} && ref $PARAMS->{'upload_files'} eq 'ARRAY');
	if(defined $upload_file){
		&reg_files($dbh,$PARAMS,$upload_file);
	}elsif(defined $upload_files){
		foreach my $_upload_file (@$upload_files){
			&reg_files($dbh,$PARAMS,$_upload_file);
		}
	}else{
		die qq|Undefined Upload file|;
	}
	$dbh->commit;
	$dbh->do("NOTIFY art_file");
	if(defined $upload_file){
		my($group_name,$group_dir,$group_ext) = &File::Basename::fileparse($upload_file,@BITS::Archive::ExtList);
		$RTN->{'file'} = &Encode::decode_utf8(qq|$group_name$group_ext|);
	}elsif(defined $upload_files){
		$RTN->{'files'} = [];
		foreach my $_upload_file (@$upload_files){
			my($group_name,$group_dir,$group_ext) = &File::Basename::fileparse($_upload_file,@BITS::Archive::ExtList);
			push(@{$RTN->{'files'}},&Encode::decode_utf8(qq|$group_name$group_ext|));
		}
	}
	$RTN->{'success'} = JSON::XS::true;
	$RTN->{'progress'}->{'value'} = 1;
	$RTN->{'progress'}->{'msg'} = 'end';
};
if($@){
	$RTN->{'msg'} = &Encode::decode_utf8($@);
	$dbh->rollback;
	$RTN->{'success'} = JSON::XS::false;
	$RTN->{'progress'}->{'msg'} = 'Error:'.$RTN->{'msg'};
}
$dbh->{AutoCommit} = 1;
$dbh->{RaiseError} = 0;


&saveStatus($RTN);

exit;

sub Truncated {
	my $v = shift;
	return undef unless(defined $v);
	my $rate = 100000;
	return int($v * $rate + 0.5) / $rate;
}

sub readFile {
	my $path = shift;
#	return undef unless(defined $path && -f $path);
	return undef unless(defined $path);
#	print __LINE__,":\$path=[$path]\n";
	my $rtn;
	my $IN;
	if(open($IN,$path)){
		my $old  = $/;
		undef $/;
		$rtn = <$IN>;
		$/ = $old;
		close($IN);
	}
	return $rtn;
}

sub saveStatus {
	my $RTN = shift;
	my $OUT;
	open($OUT,"> $ARGV[0]") or die $!;
	flock($OUT,2);
	print $OUT $json->encode($RTN);
	close($OUT);
}
