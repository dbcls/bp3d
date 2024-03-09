#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;

use CGI;
use CGI::Carp qw(fatalsToBrowser);
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
use File::Spec::Functions qw(abs2rel rel2abs catdir catfile splitdir);
use Time::Piece;
use Time::Seconds;

use constant {
	DEBUG => 1
};
my $json = JSON::XS->new->utf8->indent( 0 )->canonical(1);
if(DEBUG){
	use Data::Dumper;
	$Data::Dumper::Indent = 1;
	$Data::Dumper::Sortkeys = 1;
}

$CGI::POST_MAX = 1024 * 1024 * 1000;	# 1024 * 1KBytes = 1MBytes.

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

=pod
my $CODE = "UTF8";
if($ENV{'HTTP_USER_AGENT'}=~/Windows/){
	$CODE = "SJIS";
}elsif($ENV{'HTTP_USER_AGENT'}=~/Macintosh/){
	$CODE = "SJIS";
}
$dbh->do(qq|SET CLIENT_ENCODING TO '$CODE'|);
=cut


my %PARAMS = ();
my %COOKIE = ();
my $upload_file;
my $RTN = {
	success => JSON::XS::false
};
if(exists $ENV{'REQUEST_METHOD'} && defined $ENV{'REQUEST_METHOD'}){
	my $query = CGI->new;
#	my @params = $query->param();
#	foreach my $param (@params){
#		$PARAMS{$param} = defined $query->param($param) ? $query->param($param) : undef;
#		$PARAMS{$param} = undef if(defined $PARAMS{$param} && length($PARAMS{$param})==0);
#	}
	&getParams($query,\%PARAMS,\%COOKIE);
	my($logfile,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

	my $LOG;
	open($LOG,">> $logfile");
	if(defined $LOG){
		select($LOG);
		$| = 1;
		select(STDOUT);
	}

	my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime();
	if(defined $LOG){
		print $LOG sprintf("\n%04d:%04d/%02d/%02d %02d:%02d:%02d\n",__LINE__,$year+1900,$mon+1,$mday,$hour,$min,$sec);
		print $LOG __LINE__.':%ENV='.&Data::Dumper::Dumper(\%ENV);
		print $LOG __LINE__.':%PARAMS='.&Data::Dumper::Dumper(\%PARAMS);
	}

	eval{
		unless(defined $PARAMS{'md_id'}){
			my $md_id;
			my $sth = $dbh->prepare(qq|select md_id from model where md_abbr='bp3d'|) or die $dbh->errstr;
			$sth->execute() or die $dbh->errstr;
			$sth->bind_col(1, \$md_id, undef);
			$sth->fetch;
			$sth->finish;
			undef $sth;
			$PARAMS{'md_id'} = $md_id;
		}
		unless(defined $PARAMS{'mv_id'} && defined $PARAMS{'mr_id'}){
			my $mv_id;
			my $mr_id;
			my $sth;
			if(defined $PARAMS{'mv_id'}){
				$sth = $dbh->prepare(qq|select mv_id,mr_id from model_revision where md_id=? AND mv_id=? order by mr_id DESC|) or die $dbh->errstr;
				$sth->execute($PARAMS{'md_id'},$PARAMS{'mv_id'}) or die $dbh->errstr;
			}else{
				$sth = $dbh->prepare(qq|select mv_id,mr_id from model_revision where md_id=? order by mv_id DESC,mr_id DESC|) or die $dbh->errstr;
				$sth->execute($PARAMS{'md_id'}) or die $dbh->errstr;
			}
			$sth->bind_col(1, \$mv_id, undef);
			$sth->bind_col(2, \$mr_id, undef);
			$sth->fetch;
			$sth->finish;
			undef $sth;
			$PARAMS{'mv_id'} = $mv_id;
			$PARAMS{'mr_id'} = $mr_id;
		}

		unless(defined $PARAMS{'prefix_id'}){
			my $prefix_char = exists $PARAMS{'prefix_char'} && defined $PARAMS{'prefix_char'} ? $PARAMS{'prefix_char'} : 'FJ';
			my $prefix_id;
			my $sth = $dbh->prepare(qq|select prefix_id from id_prefix where prefix_char=?|);
			$sth->execute($prefix_char) or die $dbh->errstr;
			$sth->bind_col(1, \$prefix_id, undef);
			$sth->fetch;
			$sth->finish;
			undef $sth;
			$PARAMS{'prefix_id'} = $prefix_id;
		}

		if(defined $PARAMS{'artf_id'} && $PARAMS{'artf_id'}==0){
			$PARAMS{'artf_id'} = undef;
		}
	};
	if($@){
		$RTN->{'success'} = JSON::XS::false;
		$RTN->{'msg'} = &Encode::decode_utf8('Error: '.$@);
		&gzip_json($RTN);
		exit 0;
	}

	my $out_path = &catdir($FindBin::Bin,'temp');
	unless(-e $out_path){
		&File::Path::mkpath($out_path,0,0777);
		chmod 0777,$out_path;
	}

	if($ENV{'REQUEST_METHOD'} eq 'POST'){

#		print qq|Content-type: text/html; charset=UTF-8\n\n|;
		my $file_fh = $query->upload('file') || $query->upload('file1');

		print $LOG __LINE__.':$file_fh='.&Data::Dumper::Dumper($file_fh) if(defined $LOG);

		if(!(exists $PARAMS{'file'} && defined $PARAMS{'file'} || exists $PARAMS{'file1'} && defined $PARAMS{'file1'}) || !defined $file_fh || $query->cgi_error) {
			if($query->cgi_error){
				$RTN->{'msg'} = &Encode::decode_utf8($query->cgi_error);
			}else{
				$RTN->{'msg'} = &Encode::decode_utf8('Undefined Upload file');
			}
			&gzip_json($RTN);
			exit 0;
		}
		eval{
			if(exists $PARAMS{'file'} && defined $PARAMS{'file'}){
				$upload_file = &catdir($BITS::Config::UPLOAD_PATH,&File::Basename::basename($PARAMS{'file'}));
				delete $PARAMS{'file'};
				unlink $upload_file if(-e $upload_file);

				$file_fh = $query->upload('file');
				print $LOG __LINE__.':$file_fh='.&Data::Dumper::Dumper($file_fh) if(defined $LOG);
				print $LOG __LINE__.':$upload_file='.$upload_file."\n" if(defined $LOG);
				&File::Copy::copy($file_fh,$upload_file) if(defined $file_fh);

#				if(defined $file_fh){
#					open(OUT,"> $upload_file") or die $!.qq| [$upload_file]|;
#					binmode(OUT);
#					my $buffer;
#					while(read($file_fh, $buffer, 1024)){
#						print OUT $buffer;
#					}
#					close(OUT);
#				}
				$PARAMS{'upload_file'} = $upload_file if(-e $upload_file && -s $upload_file);
			}
			elsif(exists $PARAMS{'file1'} && defined $PARAMS{'file1'}){
				$PARAMS{'upload_files'} = [];
				my $key;
				for(my $i=1;;$i++){
					$key = qq|file$i|;
					last unless(exists $PARAMS{$key} && defined $PARAMS{$key});
					$file_fh = $query->upload($key);
					print $LOG __LINE__.':$file_fh='.&Data::Dumper::Dumper($file_fh) if(defined $LOG);
					next unless(defined $file_fh);

					$upload_file = &catdir($BITS::Config::UPLOAD_PATH,&File::Basename::basename($PARAMS{$key}));
					delete $PARAMS{$key};
					unlink $upload_file if(-e $upload_file);
					&File::Copy::copy($file_fh,$upload_file);
					push(@{$PARAMS{'upload_files'}},$upload_file) if(-e $upload_file && -s $upload_file);
				}
			}


			#オリジナルのIDが指定されている場合、実際に存在するIDのみ使用する
			if(
				exists $PARAMS{'art_org_info'} && defined $PARAMS{'art_org_info'} &&
				exists $PARAMS{'arto_id'} && defined $PARAMS{'arto_id'} && length $PARAMS{'arto_id'}
			){
				my %arto_ids;
				my @arto_ids;
				my $arto_id;
				my @temp_ids = split(/[^A-Za-z0-9]+/,$PARAMS{'arto_id'});
				my $sql_arti_sel = qq|select art_id from history_art_file_info where art_id in (|.join(",",map {'?'} @temp_ids).qq|) group by art_id|;
				my $sth_arti_sel = $dbh->prepare($sql_arti_sel) or die $dbh->errstr;
				$sth_arti_sel->execute(@temp_ids) or die $dbh->errstr;
				$sth_arti_sel->bind_col(1, \$arto_id, undef);
				while($sth_arti_sel->fetch){
					$arto_ids{$arto_id} = undef;
				}
				$sth_arti_sel->finish;
				undef $sth_arti_sel;
				foreach $arto_id (@temp_ids){
					push(@arto_ids,$arto_id) if(exists $arto_ids{$arto_id});
				}

				if(scalar @arto_ids > 0){
	#			if(scalar @arto_ids == scalar @temp_ids){
					$arto_id = join(";",@arto_ids);
				}else{
					undef $arto_id;

	#				unlink $PARAMS{'upload_file'} if(-e $PARAMS{'upload_file'});
	#				$RTN->{'msg'} = &Encode::decode_utf8(qq|オリジナルIDに存在しないIDが指定されています|);
	#				&gzip_json($RTN);
	#				exit 0;

				}
				if(defined $arto_id){
					$PARAMS{'arto_id'} = $arto_id;
				}else{
					$PARAMS{'art_org_info'} = undef;
					$PARAMS{'arto_id'} = undef;
				}
			}

			if(defined $LOG){
				print $LOG __LINE__.':%PARAMS='.&Data::Dumper::Dumper(\%PARAMS);
			}

			my $prog_basename = qq|batch-$cgi_name|;
			my $prog = &catfile($FindBin::Bin,'..','batch',qq|$prog_basename.pl|);
			if(-e $prog && -x $prog){
				my $time_md5 = &Digest::MD5::md5_hex(&Time::HiRes::time());
				$RTN->{'sessionID'} = $PARAMS{'sessionID'} = $time_md5;
				$PARAMS{'prefix'} = &catdir($out_path,$time_md5);
				$PARAMS{'HTTP_USER_AGENT'} = $ENV{'HTTP_USER_AGENT'};
				$PARAMS{'success'} = JSON::XS::true;

				my $params_file = &catfile($out_path,qq|$time_md5.json|);
				open(my $OUT,"> $params_file") or die $!;
				flock($OUT,2);
				print $OUT $json->encode(\%PARAMS);
				close($OUT);
				chmod 0666,$params_file;
				$RTN->{'mtime'} = (stat($params_file))[9];

				my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
				my $mfmt = $RTN->{'mfmt'} = sprintf("%04d%02d%02d%02d%02d%02d.%d",$year+1900,$mon+1,$mday,$hour,$min,$sec,$$);

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
						exec(qq|nice -n 19 $prog $params_file|);
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
			$RTN->{'success'} = JSON::XS::false;
			$RTN->{'msg'} = &Encode::decode_utf8('Error: '.$@);
		}

		&gzip_json($RTN);
	}
	elsif($ENV{'REQUEST_METHOD'} eq 'GET'){
		my $buf = '';
		my $params_file = &catfile($out_path,qq|$PARAMS{'sessionID'}.json|);

		print $LOG __LINE__.':$params_file='.$params_file."\n" if(defined $LOG);

		eval{
			if(-e $params_file){
				my $params_file_t = localtime((stat($params_file))[9]);
				my $current_t = localtime;
				my $diff_t = $current_t-$params_file_t;
				if($diff_t->seconds>10){
					unlink $params_file if(-e $params_file);

					my $mfmt = $PARAMS{'mfmt'};
					my $prog_basename = qq|batch-$cgi_name|;
					my $logdir = &getLogDir();
					my $f1 = &catfile($logdir,qq|$prog_basename.log.$mfmt|);
					my $f2 = &catfile($logdir,qq|$prog_basename.err.$mfmt|);
					if(-e $f2 && -s $f2){
						local $/ = undef;
						open(my $IN,$f2) or die $!;
						flock($IN,1);
						$buf = <$IN>;
						close($IN);
					}
					$buf = 'Timeout!!' if(length($buf) == 0);
					die $buf;
				}
			}

			local $/ = undef;
			open(my $IN,$params_file) or die $!;
			flock($IN,1);
			$buf = <$IN>;
			close($IN);
			print $LOG __LINE__.':$buf='.$buf."\n" if(defined $LOG);
			$RTN = $json->decode($buf);
			if($RTN->{'success'} == JSON::XS::false || lc($RTN->{'progress'}->{'msg'}) eq 'end'){
				unlink $params_file if(-e $params_file);
			}
			print $LOG __LINE__.':%RTN='.&Data::Dumper::Dumper($RTN) if(defined $LOG);
			$buf = $json->encode($RTN);
		};
		if($@){
			$RTN->{'success'} = JSON::XS::false;
			$RTN->{'msg'} = &Encode::decode_utf8('Error: '.$@);
			print $LOG __LINE__.':%RTN='.&Data::Dumper::Dumper($RTN) if(defined $LOG);
			$buf = $json->encode($RTN);
		}
		print $LOG __LINE__.':$buf='.$buf."\n" if(defined $LOG);

		my %HTTP_ACCEPT = map {$_ => undef } split(/,\s*/,$ENV{'HTTP_ACCEPT'});
		if(exists $HTTP_ACCEPT{'text/event-stream'}){
			print qq|Content-Type: text/event-stream; charset=UTF-8\n|;
			print qq|Cache-Control: no-cache\n\n|;
			print qq|data: $buf\n\n|;
		}else{
			print qq|Content-type: text/html; charset=UTF-8\n|;
			print qq|Cache-Control: no-cache\n\n|;
			print qq|$buf\n\n|;
		}
	}
	exit;
}
else{
=pod
	$upload_file = qq|/bp3d/BackStageEditor/uploads/DBCLS__FUJIEDA5.0.zip|;
	$PARAMS{'md_id'} = 1;
	$PARAMS{'mv_id'} = 7;
	$PARAMS{'mr_id'} = 1;

	$PARAMS{'prefix_char'} = 'FJ';
	$PARAMS{'prefix_id'} = 1;

	$ENV{'HTTP_USER_AGENT'}= qq|Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36|;
=cut
	exit;
}





#=cut

=pod
#use File::Find;
#&File::Find::find( \&print_file_name, qq|/ext1/project/WebGL/uploads| );

my $L=<<LIST;
LIST

my @LL = split(/\n/,$L);

use File::DirList;
my $LIST = &File::DirList::list($upload_dir,'n',1,1,0);
if(defined $LIST && ref $LIST eq 'ARRAY'){
#	print Dumper($LIST),"\n";
	foreach my $list (@$LIST){
		my $f = &catdir($upload_dir,$list->[13]);
		next unless(-f $f);
		my($n,$d,$e) = &File::Basename::fileparse($f,grep {$_ ne ".obj"} @BITS::Archive::ExtList);
		next unless(defined $e && length($e)>0);

		my @U = grep {$_ eq $f} @LL;
		next if(scalar @U>0);

		print __LINE__,":[$f]\n";
		&reg_files($f);
	}
}
exit;

=cut

#&reg_files(qq|/ext1/project/WebGL/uploads/DBCLS__FUJIEDA_111027_brainArtery_rightSideOnly.zip|);


sub reg_files {
	my $dbh = shift;
	my $PARAMS = shift;
	my $upload_file = shift;
	return unless(defined $upload_file && -e $upload_file);
	my($group_name,$group_dir,$group_ext) = &File::Basename::fileparse($upload_file,@BITS::Archive::ExtList);

	my $CODE = "UTF8";
	my $encode = "utf8";
	if($ENV{'HTTP_USER_AGENT'}=~/Windows/){
		$CODE = "SJIS";
		$encode = "shift-jis";
	}elsif($ENV{'HTTP_USER_AGENT'}=~/Macintosh/){
		$CODE = "SJIS";
		$encode = "shift-jis";
	}

	my $upload_dir = $BITS::Config::UPLOAD_PATH;
	my $prefix = &catdir($upload_dir,qq|.$group_name|);
	&File::Path::rmtree($prefix) if(-e $prefix);
	my $FILES = &BITS::Archive::extract($upload_file,$prefix,$encode);
	die qq|You can not extract the files. [$group_name$group_ext]| unless(defined $FILES && ref $FILES eq 'ARRAY');
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


	foreach my $file (@$FILES){
		next unless(-s $file);
#			print __LINE__,":\$file=[$file]\n";

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

		my $art_xmin = $obj_prop->{'bounds'}->[0];
		my $art_xmax = $obj_prop->{'bounds'}->[1];
		my $art_ymin = $obj_prop->{'bounds'}->[2];
		my $art_ymax = $obj_prop->{'bounds'}->[3];
		my $art_zmin = $obj_prop->{'bounds'}->[4];
		my $art_zmax = $obj_prop->{'bounds'}->[5];
		my $art_volume = defined $obj_prop->{'volume'} && $obj_prop->{'volume'} > 0 ?  &Truncated($obj_prop->{'volume'} / 1000) : 0;
		my $art_cube_volume = &Truncated(($art_xmax-$art_xmin)*($art_ymax-$art_ymin)*($art_zmax-$art_zmin)/1000);

		&BITS::VTK::obj2normals($org_file,$obj_prefix);

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
		my $sth_art_file = $dbh->prepare(qq|select art_id from art_file where md5(art_data)=md5(?) AND art_data=? order by art_serial desc limit 1|) or die $dbh->errstr;
		$sth_art_file->execute($art_data,$art_data) or die $dbh->errstr;
		my $art_file_rows = $sth_art_file->rows();
		if($art_file_rows>0){
			$sth_art_file->bind_col(1, \$art_id, undef);
			$sth_art_file->fetch;
		}
		$sth_art_file->finish;
#warn __LINE__,":[$obj_file][$art_md5][$org_art_md5][$art_id]\n";

		#オリジナルのファイルでも確認する
		unless(defined $art_id){
			$sth_art_file->execute($org_art_data,$org_art_data) or die $dbh->errstr;
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
			my $sth_art_file = $dbh->prepare(qq|select art_id,hist_serial from history_art_file where md5(art_data)=md5(?) AND art_data=? order by art_serial asc,hist_serial desc limit 1|) or die $dbh->errstr;
			$sth_art_file->execute($art_data,$art_data) or die $dbh->errstr;
			if($sth_art_file->rows()>0){
				$sth_art_file->bind_col(1, \$art_id, undef);
				$sth_art_file->bind_col(2, \$hist_serial, undef);
				$sth_art_file->fetch;
			}
			$sth_art_file->finish;

			#オリジナルのファイルでも確認する
			unless(defined $art_id){
				$sth_art_file->execute($org_art_data,$org_art_data) or die $dbh->errstr;
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
				my $sth_art_group_ins = $dbh->prepare(qq|insert into art_group (md_id,mv_id,mr_id,artg_id,artg_name,artg_timestamp,atrg_use,artg_openid) values (?,?,?,?,?,?,true,?)|) or die $dbh->errstr;
				$sth_art_group_ins->execute($PARAMS->{'md_id'},$PARAMS->{'mv_id'},$PARAMS->{'mr_id'},$artg_id,$group_name,$artg_timestamp,$openid) or die $dbh->errstr;
				$sth_art_group_ins->finish;
				undef $sth_art_group_ins;
			}else{
				my $sth_art_group_ins = $dbh->prepare(qq|insert into art_group (md_id,mv_id,mr_id,artg_name,artg_timestamp,atrg_use,artg_openid) values (?,?,?,?,?,true,?) RETURNING artg_id|) or die $dbh->errstr;
				$sth_art_group_ins->execute($PARAMS->{'md_id'},$PARAMS->{'mv_id'},$PARAMS->{'mr_id'},$group_name,$artg_timestamp,$openid) or die $dbh->errstr;
				$sth_art_group_ins->bind_col(1, \$artg_id, undef);
				$sth_art_group_ins->fetch;
				$sth_art_group_ins->finish;
				undef $sth_art_group_ins;
			}
		}else{
			my $temp_artg_timestamp_epoch;
			my $temp_artg_timestamp;
			my $sth_art_group = $dbh->prepare(qq|select EXTRACT(EPOCH FROM artg_timestamp) from art_group where artg_id=?|) or die $dbh->errstr;
			$sth_art_group->execute($artg_id) or die $dbh->errstr;
			$sth_art_group->bind_col(1, \$temp_artg_timestamp_epoch, undef);
			$sth_art_group->fetch;
			$sth_art_group->finish;
			undef $sth_art_group;
			if(defined $temp_artg_timestamp_epoch){
				my($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime($temp_artg_timestamp_epoch);
				$year = $year + 1900;
				$month  += 1;
				$temp_artg_timestamp = sprintf("%04d-%02d-%02d %02d:%02d:%02d",$year,$month,$mday,$hour,$min,$sec);
			}
			if($artg_timestamp ne $temp_artg_timestamp){
				my $sth_art_group_upd = $dbh->prepare(qq|update art_group set artg_timestamp=? where artg_id=?|) or die $dbh->errstr;
				$sth_art_group_upd->execute($artg_timestamp,$artg_id) or die $dbh->errstr;
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

			my $sth_arto_sel = $dbh->prepare(qq|select * from art_org_info where art_id=?|) or die $dbh->errstr;
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

	&make_art_images(\@LIST);

	undef @LIST;
}
#=cut
#print qq|Content-type: text/html; charset=UTF-8\n\n|;
#print qq|{success:true,file:"$PARAMS{'file'}"}|;

$dbh->{AutoCommit} = 0;
$dbh->{RaiseError} = 1;
eval{
	&reg_files($dbh,\%PARAMS,$upload_file);
	$dbh->commit;
	$RTN->{'file'} = &Encode::decode_utf8($PARAMS{'file'});
	$RTN->{'success'} = JSON::XS::true;
};
if($@){
	$RTN->{'msg'} = $@;
	$dbh->rollback;
}
$dbh->{AutoCommit} = 1;
$dbh->{RaiseError} = 0;

print $json->encode($RTN);
print "\n" unless(exists $ENV{'REQUEST_METHOD'} && defined $ENV{'REQUEST_METHOD'});

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

=pod
sub print_file_name {
#	return if(-d $_);

	my($name,$dir,$ext) = &File::Basename::fileparse($File::Find::name,grep {$_ ne ".obj"} @BITS::Archive::ExtList);
	return unless(defined $ext && length($ext)>0);
	return if($name =~ /^\./);

#	print $File::Find::name,"\n";
#	print qq|[$name][$dir][$ext]\n|;
#	exit;

	&reg_files($File::Find::name);
}

=cut

sub make_art_images {
	my $LIST = shift;


	return undef unless(defined $LIST && ref $LIST eq 'ARRAY' && scalar @$LIST > 0);

	my $prog_basename = qq|make_art_image|;
	my $prog_name = qq|$prog_basename.pl|;
	my $prog_dir = &catdir($FindBin::Bin,'..','cron');
	my $prog = &catfile($prog_dir,$prog_name);
	return undef unless(-e $prog && -x $prog);

	my $sessionID = &Digest::MD5::md5_hex(&Time::HiRes::time());
	my $out_path = &catdir($FindBin::Bin,'temp');
	my $params_file = &catfile($out_path,qq|$sessionID.json|);
	open(OUT,"> $params_file") or die $!;
	flock(OUT,2);
	print OUT $json->encode($LIST);
	close(OUT);
	chmod 0666,$params_file;

	my $pid = fork;
	if(defined $pid){
		if($pid == 0){

			my $logdir = &getLogDir();
			my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
			my $f1 = &catfile($logdir,qq|$prog_basename.log|.sprintf(".%04d%02d%02d%02d%02d%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec));
			my $f2 = &catfile($logdir,qq|$prog_basename.err|.sprintf(".%04d%02d%02d%02d%02d%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec));

			close(STDOUT);
			close(STDERR);
			open STDOUT, "> $f1" || die "[$f1] $!\n";
			open STDERR, "> $f2" || die "[$f2] $!\n";
			close(STDIN);
			chdir $prog_dir;
			warn __LINE__,":\$prog_dir=[$prog_dir]\n";
			warn __LINE__,":\$cmd=[nice -n 19 $prog $params_file]\n";
			exec(qq|nice -n 19 $prog $params_file|);
			exit(1);
		}
	}else{
		die("Can't execute program");
	}

	return $sessionID;
}
