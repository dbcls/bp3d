#!/opt/services/ag/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use Cwd qw(abs_path);
use File::Basename;
use File::Copy;
use File::Path;
use Archive::Extract;
use JSON::XS;
use Encode;
use Data::Dumper;
use DBD::Pg;
use Spreadsheet::Read;
use Spreadsheet::ParseExcel;
use Spreadsheet::ParseExcel::FmtJapan2;
use Spreadsheet::ParseXLSX;
use Encode;
use Encode::Guess;
use File::Spec::Functions qw(abs2rel rel2abs catdir catfile splitdir tmpdir);
use Clone;
use Time::HiRes;
use Time::Piece;
use Time::Seconds;
my $t = [&Time::HiRes::gettimeofday()];

use Getopt::Long qw(:config posix_default no_ignore_case gnu_compat);
my $config = {
	db   => exists $ENV{'AG_DB_NAME'} && defined $ENV{'AG_DB_NAME'} ? $ENV{'AG_DB_NAME'} : 'ag_public_1903xx',
	host => exists $ENV{'AG_DB_HOST'} && defined $ENV{'AG_DB_HOST'} ? $ENV{'AG_DB_HOST'} : '127.0.0.1',
	port => exists $ENV{'AG_DB_PORT'} && defined $ENV{'AG_DB_PORT'} ? $ENV{'AG_DB_PORT'} : '38300'
};
&Getopt::Long::GetOptions($config,qw/
	db|d=s
	host|h=s
	port|p=s
/) or exit 1;

$ENV{'AG_DB_HOST'} = $config->{'host'};
$ENV{'AG_DB_PORT'} = $config->{'port'};
$ENV{'AG_DB_NAME'} = $config->{'db'};

#my $lib_path;
#BEGIN{ $lib_path = dirname(abs_path($0)).qq|/../local/usr/lib/perl|; }
#use lib $lib_path;

use FindBin;
use lib $FindBin::Bin, &catdir($FindBin::Bin,'..','cgi_lib');

use BITS::Config;
use BITS::Archive;
use BITS::Obj2Hash;
#use BITS::FileConvert;
use BITS::VTK;
use BITS::Voxel;
use BITS::ConceptArtMapModified;
use BITS::ConceptArtMapPart;
use BITS::ConceptArtMapPart20190131;
#my $is_subclass_cdi_name = $BITS::ConceptArtMapPart::is_subclass_cdi_name;

require "webgl_common.pl";
use cgi_lib::common;

my $dbh = &get_dbh();

my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,qw|.pl|);

my $params_file = $ARGV[0];
exit unless(defined $params_file && -e $params_file && -f $params_file && -s $params_file);

my $log_file = &catfile($FindBin::Bin,'logs',"${cgi_name}.txt");
my $LOG;
open($LOG,"> $log_file") or die "$! [$log_file]";
select($LOG);
$| = 1;
select(STDOUT);
$| = 1;

&cgi_lib::common::message($params_file,$LOG) if(defined $LOG);
&cgi_lib::common::message(\%ENV,$LOG) if(defined $LOG);

my $RTN = &cgi_lib::common::readFileJSON($params_file);
$RTN->{'progress'}->{'value'} = 0;

$SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit";
sub sigexit {
	my($date) = `date`;
	$date =~ s/\s*$//g;
	$RTN->{'msg'} = $RTN->{'progress'}->{'msg'} = &cgi_lib::common::decodeUTF8(qq|Error:[$date] KILL THIS SCRIPT!!|);
	$RTN->{'success'} = JSON::XS::false;
	&cgi_lib::common::writeFileJSON($params_file,$RTN);
	exit(1);
}

sub _writeProgress {
	&cgi_lib::common::writeFileJSON($params_file,$RTN);
#	if(defined $LOG){
#		my($package, $file, $line, $subname, $hasargs, $wantarray, $evaltext, $is_require) = caller();
#		&cgi_lib::common::message(sprintf("%d:%f",$line,&Time::HiRes::tv_interval($t)),$LOG);
#	}
}

my @data_extlist = qw|.xls .xlsx .txt|;
my @extlist = qw|.tar .tar.gz .tgz .gz .Z .zip .bz2 .tar.bz2 .tbz .lzma .xz .tar.xz .txz|;
push(@extlist,@data_extlist);

&_writeProgress();

my $upload_file = $RTN->{'file'};
&cgi_lib::common::message($upload_file,$LOG) if(defined $LOG);

my $dir;
my @FILES;
eval{
	my $files;

	my($upload_name,$upload_dir,$upload_ext) = &File::Basename::fileparse($upload_file,@BITS::Archive::ExtList);
	$RTN->{'msg'} = $RTN->{'progress'}->{'msg'} = &cgi_lib::common::decodeUTF8(qq|Uncompress: $upload_name$upload_ext|);
	&_writeProgress();
	$files = &extract($upload_file) if(defined $upload_file && -e $upload_file && -f $upload_file && -s $upload_file);
#	&cgi_lib::common::message($files,$LOG) if(defined $LOG);
#	die "ERROR!! TEST";

#	$dbh->{'AutoCommit'} = 0;
#	$dbh->{'RaiseError'} = 1;
	eval{
		if(defined $files && ref $files eq 'ARRAY'){
			my $file_datas;
			foreach my $file (@$files){
#				&cgi_lib::common::message("\$file=[$file]",$LOG) if($LOG);
				next unless(-e $file);
				my($_name,$_dir,$_ext) = &File::Basename::fileparse($file,@data_extlist);
				next unless(length($_ext));
				&cgi_lib::common::message($_ext,$LOG) if(defined $LOG);
				$RTN->{'msg'} = $RTN->{'progress'}->{'msg'} = &cgi_lib::common::decodeUTF8(qq|Read: $_name$_ext|);
				&_writeProgress();
				if($_ext eq '.txt'){

					my @DATAS = ();
					open(my $IN,$file) or die "$! [$file]";
					while(<$IN>){
						s/\s*$//g;
						push(@DATAS,&g_encoding($_));
					}
					close($IN);

					&cgi_lib::common::message($file,$LOG) if(defined $LOG);
					&cgi_lib::common::message(scalar @DATAS,$LOG) if(defined $LOG);

#					&reg_records($RTN,\@DATAS,$file);
					push(@{$file_datas->{$file}},@DATAS);
					undef @DATAS;

				}
				elsif($_ext eq '.xls'){

					my $oExcel = Spreadsheet::ParseExcel->new;
					my $oFmtJ = Spreadsheet::ParseExcel::FmtJapan2->new(Code => 'utf8'); #sjis、jisなどのコード
					my $oBook = $oExcel->Parse($file, $oFmtJ);
					my($iR, $iC, $oWkS, $oWkC);
					for(my $iSheet=0; $iSheet < $oBook->{SheetCount} ; $iSheet++) {
						$oWkS = $oBook->{Worksheet}[$iSheet];
						my @DATAS = ();
						for(my $iR = $oWkS->{MinRow} ; defined $oWkS->{MaxRow} && $iR <= $oWkS->{MaxRow} ; $iR++) {
							my @cols = ();
							for(my $iC = $oWkS->{MinCol} ; defined $oWkS->{MaxCol} && $iC <= $oWkS->{MaxCol} ; $iC++) {
								$oWkC = $oWkS->{Cells}[$iR][$iC];
								push(@cols,$oWkC ? $oWkC->Value : undef);
							}
							push(@DATAS,join("\t",@cols));
						}

#						&reg_records($RTN,\@DATAS,$file);
						push(@{$file_datas->{$file}},@DATAS);
						undef @DATAS;
					}
				}
				elsif($_ext eq '.xlsx'){
					my $book = &Spreadsheet::Read::ReadData($file);
					next unless(defined $book);
					my $book_info = shift @$book;
					foreach my $sheet (@$book){
						my $maxrow = $sheet->{'maxrow'};
						my @DATAS = ();
						foreach my $row (1..$maxrow){
							my @cols = &Spreadsheet::Read::cellrow($sheet, $row);
							push(@DATAS,join("\t",@cols));
						}
#						&reg_records($RTN,\@DATAS,$file);
						push(@{$file_datas->{$file}},@DATAS);
						undef @DATAS;
					}
				}
			}
			if(defined $file_datas && ref $file_datas eq 'HASH'){
				my @k = keys(%$file_datas);
				if(scalar @k == 1){
					&reg_records($RTN,$file_datas->{$k[0]},$k[0]);
				}else{
					&reg_records($RTN,undef,$file_datas);
				}
			}
#			$dbh->commit();
		}
		$RTN->{'success'} = JSON::XS::true;
		$RTN->{'progress'}->{'value'} = 1;
		$RTN->{'progress'}->{'msg'} = 'end';
	};
	if($@){
		$RTN->{'success'} = JSON::XS::false;
		$RTN->{'msg'} = &cgi_lib::common::decodeUTF8($@);
		$RTN->{'progress'}->{'msg'} = 'error';
		&cgi_lib::common::message($RTN->{'msg'},$LOG) if(defined $LOG);
#		$dbh->rollback();
	}
#	$dbh->{'AutoCommit'} = 1;
#	$dbh->{'RaiseError'} = 0;
};
if($@){
	$RTN->{'success'} = JSON::XS::false;
	$RTN->{'msg'} = &cgi_lib::common::decodeUTF8($@);
	$RTN->{'progress'}->{'msg'} = 'error';
}
&_writeProgress();
exit;

use File::Find;
my @FIND_FILES;
sub find_process {
	return unless(-e $File::Find::name && -f $File::Find::name);
	push(@FIND_FILES,$File::Find::name);
}

sub extract($;$) {
	my $file = shift;
	my $prefix = shift;
	return undef unless(-e $file);

	if(defined $prefix){
		$dir = $prefix;
	}else{
#		$dir = basename($file,@extlist);
		my($_name,$_dir,$_ext) = &File::Basename::fileparse($file,@extlist);
		$dir = &catdir($_dir,$_name);
	}
	if(defined $LOG){
		&cgi_lib::common::message("\$file=[$file]",$LOG);
		&cgi_lib::common::message("\$dir=[$dir]",$LOG);
	}
	&File::Path::rmtree($dir) if(-e $dir);
	&File::Path::mkpath($dir,{mode=>0777}) unless(-e $dir);
	chmod 0777,$dir;

	my $ae;
	eval{
		$Archive::Extract::WARN = 0;
		$ae = Archive::Extract->new(archive => $file) if(-e $file);
	};
	if(defined $ae){
		my $to_path = &catdir(&tmpdir(),&File::Basename::basename($dir).qq|_$$|);
		&File::Path::rmtree($to_path) if(-e $to_path);
		&File::Path::mkpath($to_path,{mode=>0777}) unless(-e $to_path);
		chmod 0777,$to_path;
		$ae->extract(to => $to_path);

		my @EXT_FILES = glob &catfile($to_path,'*');
		&File::Copy::move($_,$dir) for(@EXT_FILES);

		@FIND_FILES = ();
		&File::Find::find(\&find_process, $dir);
		push(@FILES,@FIND_FILES);

		&File::Path::rmtree($to_path) if(-e $to_path);
	}else{
		my $to = &catfile($dir,&File::Basename::basename($file));
		&File::Copy::move($file,$to);
		push(@FILES,$to) if(-e $to);
#		push(@FILES,$file) if(-e $file);
	}
	return wantarray ? @FILES : \@FILES;
}

sub g_encoding {
	my $value = shift;
	unless(&utf8::is_utf8($value)){
		# UTF8フラグ がない場合、decode して、UTF8フラグつきにする
		my $guessed_obj = &Encode::Guess::guess_encoding($value, qw/euc-jp shift-jis/);
		$value = $guessed_obj->decode($value) if(ref $guessed_obj);
		undef $guessed_obj;
	}
	return $value;
}

sub reg_records {
	my $params = shift;
	my $datas = shift;
	my $file = shift;
	&cgi_lib::common::message($params,$LOG) if(defined $LOG);
	if(exists $params->{'cmd'} && defined $params->{'cmd'}){
		&cgi_lib::common::message($params->{'cmd'},$LOG) if(defined $LOG);
		if($params->{'cmd'} eq 'import-fma-all-list'){
			&reg_record_fmas($params,$datas);
		}elsif($params->{'cmd'} eq 'import-upload-all-list'){
			&reg_record_objs($params,$datas);
		}elsif($params->{'cmd'} eq 'import-concept-art-map'){
			&reg_record_objs($params,$datas,$file);
		}else{
			die 'Unknown Cmd ['.$params->{'cmd'}.']';
		}
	}else{
			die 'Undefined Cmd ['.$params->{'cmd'}.']';
	}
}

sub reg_record_fmas {
	my $params = shift;
	my $datas = shift;
	return unless(defined $datas && ref $datas eq 'ARRAY');

	my $KEYS = {
		cdi_name   => 'ID',
		cdi_name_j => 'Name(J)',
		cdi_name_k => 'Name(K)',
		cdi_name_l => 'Name(L)',
		cdi_syn_j  => 'Synonym(J)',
		cdi_def_j  => 'Definition(J)',
	};
	my $data_pos = 0;
	my $header;
	foreach my $data (@$datas){
		&cgi_lib::common::message(sprintf('[%05d/%05d]',++$data_pos,scalar @$datas),$LOG) if(defined $LOG);
		$RTN->{'progress'} = {
			'value' => $data_pos/scalar @$datas,
			'msg' => &cgi_lib::common::decodeUTF8(qq|[$data_pos/|.(scalar @$datas).qq|]|)
		};
		&_writeProgress();
		$data = &trim($data);
		if(index($data,'#') == 0){
			undef $header;
			$header = &get_header($data);
#	my $header = qq|#ID	Name	Name(L)	Name(J)	Name(K)	Synonym	Synonym(J)	Definition	Definition(J)	TAID	Tree|;
			undef $header unless(defined $header && defined $header->{$KEYS->{'cdi_name'}} && (defined $header->{$KEYS->{'cdi_name_l'}} || defined $header->{$KEYS->{'cdi_name_j'}} || defined $header->{$KEYS->{'cdi_name_k'}} || defined $header->{$KEYS->{'cdi_syn_j'}} || defined $header->{$KEYS->{'cdi_def_j'}}));
			&cgi_lib::common::message($header,$LOG) if(defined $LOG && defined $header);
		}elsif(defined $header){
			my $hash = &set_data2hash($header,$data);
			unless(defined $hash && defined $hash->{$KEYS->{'cdi_name'}}){
				undef $hash;
				next;
			}
			&cgi_lib::common::message($hash,$LOG) if(defined $LOG);

			$RTN->{'msg'} = &cgi_lib::common::decodeUTF8(qq|Registration: $hash->{$KEYS->{'cdi_name'}}|);
			$RTN->{'progress'}->{'msg'} = &cgi_lib::common::decodeUTF8(qq|[$data_pos/|.(scalar @$datas).qq|] $hash->{$KEYS->{'cdi_name'}}|);
			&_writeProgress();

			my $sql = qq|UPDATE concept_data_info set cdi_delcause=null,cdi_entry=now()|;
			my @bind_values;
			my @col;
			foreach my $key (keys(%$KEYS)){
				next if($key eq 'cdi_name');
				next unless(defined $header->{$KEYS->{$key}});
				push(@col,qq|$key=?|);
				push(@bind_values,$hash->{$KEYS->{$key}});
			}
			$sql .= ','.join(",",@col) if(scalar @col > 0);
			undef @col;

			$sql .= qq| WHERE ci_id=? AND cdi_name=? AND |;
			push(@bind_values,$params->{'ci_id'});
			push(@bind_values,$hash->{$KEYS->{'cdi_name'}});

			foreach my $key (keys(%$KEYS)){
				next if($key eq 'cdi_name');
				next unless(defined $header->{$KEYS->{$key}});

				if(defined $hash->{$KEYS->{$key}}){
					push(@col,qq|$key<>?|);
					push(@bind_values,$hash->{$KEYS->{$key}});
				}else{
					push(@col,qq|$key is not null|);
				}
			}
			$sql .= '('.join(" or ",@col).')';
			undef @col;

			my $sth = $dbh->prepare($sql) or die $dbh->errstr;
			$sth->execute(@bind_values) or die $dbh->errstr;
			my $rows = $sth->rows();
			if($rows>0){
				if(defined $LOG){
					&cgi_lib::common::message("\$rows=[$rows]",$LOG);
					&cgi_lib::common::message("\$sql=[$sql]",$LOG);
					&cgi_lib::common::message("\@bind_values=[".join(",",@bind_values)."]",$LOG);
				}
			}
			$sth->finish();
			undef $sth;
			undef $sql;
			undef @bind_values;
		}
	}
}

sub is_reg_obj_hash {
	my $header = shift;
	my $hash = shift;
	my $KEYS = shift;

	my $rtn = 1;
	$rtn = 0 unless(
		exists $header->{$KEYS->{'cm_entry'}} && defined $header->{$KEYS->{'cm_entry'}} && length $header->{$KEYS->{'cm_entry'}} &&
		exists $hash->{  $KEYS->{'cm_entry'}} && defined $hash->{  $KEYS->{'cm_entry'}} && length $hash->{  $KEYS->{'cm_entry'}} &&
		exists $header->{$KEYS->{'art_filename'}} && defined $header->{$KEYS->{'art_filename'}} && length $header->{$KEYS->{'art_filename'}} &&
		exists $hash->{  $KEYS->{'art_filename'}} && defined $hash->{  $KEYS->{'art_filename'}} && length $hash->{  $KEYS->{'art_filename'}} &&
		exists $header->{$KEYS->{'art_timestamp'}} && defined $header->{$KEYS->{'art_timestamp'}} && length $header->{$KEYS->{'art_timestamp'}} &&
		exists $hash->{  $KEYS->{'art_timestamp'}} && defined $hash->{  $KEYS->{'art_timestamp'}} && length $hash->{  $KEYS->{'art_timestamp'}} &&
		exists $header->{$KEYS->{'art_xmin'}} && defined $header->{$KEYS->{'art_xmin'}} && length $header->{$KEYS->{'art_xmin'}} &&
		exists $hash->{  $KEYS->{'art_xmin'}} && defined $hash->{  $KEYS->{'art_xmin'}} && length $hash->{  $KEYS->{'art_xmin'}} &&
		exists $header->{$KEYS->{'art_xmax'}} && defined $header->{$KEYS->{'art_xmax'}} && length $header->{$KEYS->{'art_xmax'}} &&
		exists $hash->{  $KEYS->{'art_xmax'}} && defined $hash->{  $KEYS->{'art_xmax'}} && length $hash->{  $KEYS->{'art_xmax'}} &&

		exists $header->{$KEYS->{'art_ymin'}} && defined $header->{$KEYS->{'art_ymin'}} && length $header->{$KEYS->{'art_ymin'}} &&
		exists $hash->{  $KEYS->{'art_ymin'}} && defined $hash->{  $KEYS->{'art_ymin'}} && length $hash->{  $KEYS->{'art_ymin'}} &&
		exists $header->{$KEYS->{'art_ymax'}} && defined $header->{$KEYS->{'art_ymax'}} && length $header->{$KEYS->{'art_ymax'}} &&
		exists $hash->{  $KEYS->{'art_ymax'}} && defined $hash->{  $KEYS->{'art_ymax'}} && length $hash->{  $KEYS->{'art_ymax'}} &&

		exists $header->{$KEYS->{'art_zmin'}} && defined $header->{$KEYS->{'art_zmin'}} && length $header->{$KEYS->{'art_zmin'}} &&
		exists $hash->{  $KEYS->{'art_zmin'}} && defined $hash->{  $KEYS->{'art_zmin'}} && length $hash->{  $KEYS->{'art_zmin'}} &&
		exists $header->{$KEYS->{'art_zmax'}} && defined $header->{$KEYS->{'art_zmax'}} && length $header->{$KEYS->{'art_zmax'}} &&
		exists $hash->{  $KEYS->{'art_zmax'}} && defined $hash->{  $KEYS->{'art_zmax'}} && length $hash->{  $KEYS->{'art_zmax'}} &&

		exists $header->{$KEYS->{'art_volume'}} && defined $header->{$KEYS->{'art_volume'}} && length $header->{$KEYS->{'art_volume'}} &&
		exists $hash->{  $KEYS->{'art_volume'}} && defined $hash->{  $KEYS->{'art_volume'}} && length $hash->{  $KEYS->{'art_volume'}} &&
		exists $header->{$KEYS->{'art_data_size'}} && defined $header->{$KEYS->{'art_data_size'}} && length $header->{$KEYS->{'art_data_size'}} &&
		exists $hash->{  $KEYS->{'art_data_size'}} && defined $hash->{  $KEYS->{'art_data_size'}} && length $hash->{  $KEYS->{'art_data_size'}} &&

#		exists $header->{$KEYS->{'art_nsn'}} && defined $header->{$KEYS->{'art_nsn'}} && length $header->{$KEYS->{'art_nsn'}} &&

		exists $header->{$KEYS->{'art_entry'}} && defined $header->{$KEYS->{'art_entry'}} && length $header->{$KEYS->{'art_entry'}} &&
		exists $hash->{  $KEYS->{'art_entry'}} && defined $hash->{  $KEYS->{'art_entry'}} && length $hash->{  $KEYS->{'art_entry'}} &&
		exists $header->{$KEYS->{'prefix_char'}} && defined $header->{$KEYS->{'prefix_char'}} && length $header->{$KEYS->{'prefix_char'}} &&
		exists $hash->{  $KEYS->{'prefix_char'}} && defined $hash->{  $KEYS->{'prefix_char'}} && length $hash->{  $KEYS->{'prefix_char'}} &&
		exists $header->{$KEYS->{'art_serial'}} && defined $header->{$KEYS->{'art_serial'}} && length $header->{$KEYS->{'art_serial'}} &&
		exists $hash->{  $KEYS->{'art_serial'}} && defined $hash->{  $KEYS->{'art_serial'}} && length $hash->{  $KEYS->{'art_serial'}} &&
		exists $header->{$KEYS->{'art_md5'}} && defined $header->{$KEYS->{'art_md5'}} && length $header->{$KEYS->{'art_md5'}} &&
		exists $hash->{  $KEYS->{'art_md5'}} && defined $hash->{  $KEYS->{'art_md5'}} && length $hash->{  $KEYS->{'art_md5'}} &&
#		exists $header->{$KEYS->{'art_cube_volume'}} && defined $header->{$KEYS->{'art_cube_volume'}} && length $header->{$KEYS->{'art_cube_volume'}} &&
#		exists $hash->{  $KEYS->{'art_cube_volume'}} && defined $hash->{  $KEYS->{'art_cube_volume'}} && length $hash->{  $KEYS->{'art_cube_volume'}} &&

		exists $header->{$KEYS->{'arto_id'}} && defined $header->{$KEYS->{'arto_id'}} && length $header->{$KEYS->{'arto_id'}}
	);
	return $rtn;
}

sub reg_record_objs {
	my $params = shift;
	my $datas = shift;
	my $file = shift;

	my $KEYS_defaults = {
		art_id        => 'FJID',
		cdi_name      => 'FMA_ID',
		cdi_name_e    => 'FMA_NAME',
		cdi_syn_e     => 'FMA_SYNONYM',
		art_comment   => 'Comment',
		art_category  => 'Category',
		art_judge     => 'Judge',
		art_class     => 'Class',

		cm_entry      => 'MAP_Timestamp',
		art_filename  => 'OBJ_Filename',
		art_timestamp => 'OBJ_Timestamp',

		art_xmin      => 'Xmin',
		art_xmax      => 'Xmax',
		art_ymin      => 'Ymin',
		art_ymax      => 'Ymax',
		art_zmin      => 'Zmin',
		art_zmax      => 'Zmax',
		art_volume    => 'Volume',
		art_data_size => 'Size',

		art_nsn         => uc('art_nsn'),
		art_entry       => uc('art_entry'),
		prefix_char     => uc('prefix_char'),
		art_serial      => uc('art_serial'),
		art_md5         => uc('art_md5'),
		art_cube_volume => uc('art_cube_volume'),
		arto_id         => uc('arto_id'),
		arto_comment    => uc('arto_comment'),
		art_folder      => uc('art_folder'),

		cmp_title         => 'SubClass',
		cmp_abbr          => 'SubClassAbbr',
		cmp_display_title => 'SubClassDisplay',
		cmp_prefix        => 'SubClassPrefix',
		cmp_bul_name_e    => 'SubClassLogic'
	};

	my $KEYS_201903xx = {
		art_id        => 'FJID',
		artc_id       => 'OBJID',
		cdi_name      => 'FMA_ID',
		cdi_name_e    => 'FMA_NAME',
		cdi_syn_e     => 'FMA_SYNONYM',
		art_comment   => 'Comment',
		art_category  => 'Category',
		art_judge     => 'Judge',
		art_class     => 'Class',

		cm_entry      => 'MAP_Timestamp',
		art_filename  => 'OBJ_Filename',
		art_timestamp => 'OBJ_Timestamp',

		art_xmin      => 'Xmin',
		art_xmax      => 'Xmax',
		art_ymin      => 'Ymin',
		art_ymax      => 'Ymax',
		art_zmin      => 'Zmin',
		art_zmax      => 'Zmax',
		art_volume    => 'Volume',
		art_data_size => 'Size',

		art_nsn         => uc('art_nsn'),
		art_entry       => uc('art_entry'),
		prefix_char     => uc('prefix_char'),
		art_serial      => uc('art_serial'),
		art_md5         => uc('art_md5'),
		art_cube_volume => uc('art_cube_volume'),
		arto_id         => uc('arto_id'),
		arto_comment    => uc('arto_comment'),
		art_folder      => uc('art_folder'),

		cmp_title         => 'SubClass',
		cmp_abbr          => 'SubClassAbbr',
		cmp_display_title => 'SubClassDisplay',
		cmp_prefix        => 'SubClassPrefix',
		cmp_bul_name_e    => 'SubClassLogic',

		bcp_title         => 'SubPart',
		bcp_abbr          => 'SubPartAbbr',
		bcp_display_title => 'SubPartDisplay',
		bcp_prefix        => 'SubPartPrefix',
		bcp_bul_name_e    => 'SubPartLogic',

		bcl_title         => 'Laterality',
		bcl_abbr          => 'LateralityAbbr',
		bcl_display_title => 'LateralityDisplay',
		bcl_prefix        => 'LateralityPrefix',

		artl_title         => 'OBJ_Laterality',
		artl_abbr          => 'OBJ_LateralityAbbr',
		artl_display_title => 'OBJ_LateralityDisplay',
		artl_prefix        => 'OBJ_LateralityPrefix',

		cdi_pname => 'FMA_ID_Parent',
		cdi_sname => 'FMA_ID_Super',

		cdi_name_base     => 'FMA_ID_Base',
		cd_synonym_base     => 'FMA_SYNONYM_Base',

		concept_relation_logic => 'ConceptRelationLogic',
		concept_relation_types => 'ConceptRelationTypes',
		cti_cnames     => 'FMA_ID_Descendants',
		cti_pnames     => 'FMA_ID_Ancestor',
		cti_depth    => 'Depth',

		seg_name         => 'SegmentName',
		seg_color        => 'SegmentColor',
		seg_thum_bgcolor => 'SegmentThumbnailBackgroundColor',
		seg_thum_bocolor => 'SegmentThumbnailBorderColor',
		seg_thum_fgcolor => 'SegmentThumbnailForegroundColor',
		csg_name         => 'SegmentGroupName',
		cdi_ids          => 'FMA_IDs',
		cdf_name         => 'CDF_NAME',

		is_user_data => uc('isUserData')
	};

	my $KEYS = $KEYS_defaults;
	my $format_version = 'defaults';

	my $column_number;

	my $dir;
	my $concept_art_map_part;
	my $concept_part;
	my $concept_laterality;
	my $art_laterality;

	my $concept_segment;
	my $concept_data;
	my $concept_data_synonym;
	my $concept_tree;
	my $concept_tree_info;

	if(defined $file && ref $file eq 'HASH'){
		my $D;
		foreach my $f (keys(%$file)){
			my($_name,$_dir,$_ext) = &File::Basename::fileparse($f,@data_extlist);
			&cgi_lib::common::message($_name,$LOG) if(defined $LOG);
			$D->{$_name} = $file->{$f};
			$dir = &File::Basename::dirname($f) if(defined $f && -e $f && -f $f && $_name eq 'concept_art_map');
		}
		if(defined $D && ref $D eq 'HASH'){
			if(exists $D->{'concept_art_map'} && defined $D->{'concept_art_map'} && ref $D->{'concept_art_map'} eq 'ARRAY'){
				$datas = $D->{'concept_art_map'};

				foreach my $data (@{$D->{'concept_art_map'}}){
					$data = &trim($data);
					next unless(defined $data);
					last unless(index($data,'#') == 0);
					my($header_key,@header_values) = split(/:/,substr($data,1));
					my $header_value = join(':',@header_values);
					if($header_key eq 'Version'){
						if($header_value eq '201903xx'){
							$KEYS = $KEYS_201903xx;
							$format_version = '201903xx';
						}
					}
				}
			}
			if(exists $D->{'concept_art_map_part'} && defined $D->{'concept_art_map_part'} && ref $D->{'concept_art_map_part'} eq 'ARRAY'){
#				my $concept_art_map_part = $D->{'concept_art_map_part'};
				my $header;
				foreach my $data (@{$D->{'concept_art_map_part'}}){
					$data = &trim($data);
					next unless(defined $data);
					if(index($data,'#') == 0){
						undef $header;
						$header = &get_header($data);
						undef $header unless(defined $header && ref $header eq 'HASH' && exists $header->{$KEYS->{'cmp_title'}} && exists $header->{$KEYS->{'cmp_abbr'}} && exists $header->{$KEYS->{'cmp_prefix'}} && exists $header->{$KEYS->{'cmp_bul_name_e'}});
#						&cgi_lib::common::message($header,,$LOG) if(defined $LOG && defined $header)
					}elsif(defined $header){
						my $hash = &set_data2hash($header,$data);
						unless(defined $hash && ref $header eq 'HASH' && exists $hash->{$KEYS->{'cmp_title'}} && defined $hash->{$KEYS->{'cmp_title'}} && length $hash->{$KEYS->{'cmp_title'}}){
							undef $hash;
							next;
						}
						push(@$concept_art_map_part, $hash);
						next;
					}
				}
				&cgi_lib::common::message(sprintf("concept_art_map_part:[%d]",scalar @{$concept_art_map_part}),$LOG) if(defined $LOG);
			}
			if(exists $D->{'concept_part'} && defined $D->{'concept_part'} && ref $D->{'concept_part'} eq 'ARRAY'){
				my $header;
				foreach my $data (@{$D->{'concept_part'}}){
					$data = &trim($data);
					next unless(defined $data);
					if(index($data,'#') == 0){
						undef $header;
						$header = &get_header($data);
						undef $header unless(defined $header && ref $header eq 'HASH' && exists $header->{$KEYS->{'bcp_title'}} && exists $header->{$KEYS->{'bcp_abbr'}} && exists $header->{$KEYS->{'bcp_display_title'}} && exists $header->{$KEYS->{'bcp_prefix'}} && exists $header->{$KEYS->{'bcp_bul_name_e'}});
#						&cgi_lib::common::message($header,$LOG) if(defined $LOG && defined $header)
					}elsif(defined $header){
						my $hash = &set_data2hash($header,$data);
						unless(defined $hash && ref $header eq 'HASH' && exists $hash->{$KEYS->{'bcp_title'}} && defined $hash->{$KEYS->{'bcp_title'}} && length $hash->{$KEYS->{'bcp_title'}}){
							undef $hash;
							next;
						}
						push(@$concept_part, $hash);
						next;
					}
				}
				&cgi_lib::common::message(sprintf("concept_part:[%d]",scalar @{$concept_part}),$LOG) if(defined $LOG);
			}
			if(exists $D->{'concept_laterality'} && defined $D->{'concept_laterality'} && ref $D->{'concept_laterality'} eq 'ARRAY'){
				my $header;
				foreach my $data (@{$D->{'concept_laterality'}}){
					$data = &trim($data);
					next unless(defined $data);
					if(index($data,'#') == 0){
						undef $header;
						$header = &get_header($data);
						undef $header unless(defined $header && ref $header eq 'HASH' && exists $header->{$KEYS->{'bcl_title'}} && exists $header->{$KEYS->{'bcl_abbr'}} && exists $header->{$KEYS->{'bcl_display_title'}} && exists $header->{$KEYS->{'bcl_prefix'}});
#						&cgi_lib::common::message($header,$LOG) if(defined $LOG && defined $header)
					}elsif(defined $header){
						my $hash = &set_data2hash($header,$data);
						unless(defined $hash && ref $header eq 'HASH' && exists $hash->{$KEYS->{'bcl_title'}} && defined $hash->{$KEYS->{'bcl_title'}} && length $hash->{$KEYS->{'bcl_title'}}){
							undef $hash;
							next;
						}
						push(@$concept_laterality, $hash);
						next;
					}
				}
				&cgi_lib::common::message(sprintf("concept_laterality:[%d]",scalar @{$concept_laterality}),$LOG) if(defined $LOG);
			}
			if(exists $D->{'art_laterality'} && defined $D->{'art_laterality'} && ref $D->{'art_laterality'} eq 'ARRAY'){
				my $header;
				foreach my $data (@{$D->{'art_laterality'}}){
					$data = &trim($data);
					next unless(defined $data);
					if(index($data,'#') == 0){
						undef $header;
						$header = &get_header($data);
						undef $header unless(defined $header && ref $header eq 'HASH' && exists $header->{$KEYS->{'artl_title'}} && exists $header->{$KEYS->{'artl_abbr'}} && exists $header->{$KEYS->{'artl_display_title'}} && exists $header->{$KEYS->{'artl_prefix'}});
#						&cgi_lib::common::message($header,$LOG) if(defined $LOG && defined $header)
					}elsif(defined $header){
						my $hash = &set_data2hash($header,$data);
						unless(defined $hash && ref $header eq 'HASH' && exists $hash->{$KEYS->{'artl_title'}} && defined $hash->{$KEYS->{'artl_title'}} && length $hash->{$KEYS->{'artl_title'}}){
							undef $hash;
							next;
						}
						push(@$art_laterality, $hash);
						next;
					}
				}
				&cgi_lib::common::message(sprintf("art_laterality:[%d]",scalar @{$art_laterality}),$LOG) if(defined $LOG);
			}


			if(exists $D->{'concept_segment'} && defined $D->{'concept_segment'} && ref $D->{'concept_segment'} eq 'ARRAY'){
				&cgi_lib::common::message(sprintf("concept_segment:[%d]",scalar @{$D->{'concept_segment'}}),$LOG) if(defined $LOG);
				my $header;
				foreach my $data (@{$D->{'concept_segment'}}){
					$data = &trim($data);
					next unless(defined $data);
					if(index($data,'#') == 0){
						undef $header;
						$header = &get_header($data);
#						&cgi_lib::common::message($header,$LOG) if(defined $LOG && defined $header);
						unless(
									defined	$header
							&&	ref			$header eq 'HASH'
							&&	exists	$header->{$KEYS->{'seg_name'}}
							&&	exists	$header->{$KEYS->{'seg_color'}}
							&&	exists	$header->{$KEYS->{'seg_thum_bgcolor'}}
							&&	exists	$header->{$KEYS->{'seg_thum_bocolor'}}
							&&	exists	$header->{$KEYS->{'seg_thum_fgcolor'}}
							&&	exists	$header->{$KEYS->{'csg_name'}}
							&&	exists	$header->{$KEYS->{'cdi_ids'}}
							&&	exists	$header->{$KEYS->{'cdf_name'}}
						){
							undef $header;
						}
#						&cgi_lib::common::message($header,$LOG) if(defined $LOG && defined $header);
					}elsif(defined $header){
						my $hash = &set_data2hash($header,$data);
#						&cgi_lib::common::message($hash,$LOG) if(defined $LOG && defined $hash);
						unless(
									defined	$hash
							&&	ref			$header eq 'HASH'
							&&	exists	$hash->{$KEYS->{'seg_name'}}
							&&	defined	$hash->{$KEYS->{'seg_name'}}
							&&	length	$hash->{$KEYS->{'seg_name'}}
						){
							undef $hash;
							next;
						}
						push(@$concept_segment, $hash);
						next;
					}
				}
				&cgi_lib::common::message(sprintf("concept_segment:[%d]",scalar @{$concept_segment}),$LOG) if(defined $LOG);
			}

			if(exists $D->{'concept_data'} && defined $D->{'concept_data'} && ref $D->{'concept_data'} eq 'ARRAY'){
				&cgi_lib::common::message(sprintf("concept_data:[%d]",scalar @{$D->{'concept_data'}}),$LOG) if(defined $LOG);
				my $header;
				foreach my $data (@{$D->{'concept_data'}}){
					$data = &trim($data);
					next unless(defined $data);
					if(index($data,'#') == 0){
						undef $header;
						$header = &get_header($data);
						unless(
									defined	$header
							&&	ref			$header eq 'HASH'
							&&	exists	$header->{$KEYS->{'cdi_name'}}
							&&	exists	$header->{$KEYS->{'cdi_name_e'}}
							&&	exists	$header->{$KEYS->{'cdi_syn_e'}}
							&&	exists	$header->{$KEYS->{'seg_name'}}
							&&	exists	$header->{$KEYS->{'is_user_data'}}
							&&	exists	$header->{$KEYS->{'cmp_title'}}
							&&	exists	$header->{$KEYS->{'bcp_title'}}
							&&	exists	$header->{$KEYS->{'bcl_title'}}
							&&	exists	$header->{$KEYS->{'cdi_pname'}}
							&&	exists	$header->{$KEYS->{'cdi_sname'}}
						){
							undef $header;
						}
#						&cgi_lib::common::message($header,$LOG) if(defined $LOG && defined $header);
					}elsif(defined $header){
						my $hash = &set_data2hash($header,$data);
#						&cgi_lib::common::message($hash,$LOG) if(defined $LOG && defined $hash);
						unless(
									defined	$hash
							&&	ref			$header eq 'HASH'
							&&	exists	$hash->{$KEYS->{'cdi_name'}}
							&&	defined	$hash->{$KEYS->{'cdi_name'}}
							&&	length	$hash->{$KEYS->{'cdi_name'}}
							&&	exists	$hash->{$KEYS->{'cdi_name_e'}}
							&&	defined	$hash->{$KEYS->{'cdi_name_e'}}
							&&	length	$hash->{$KEYS->{'cdi_name_e'}}
						){
							undef $hash;
							next;
						}
						push(@$concept_data, $hash);
						next;
					}
				}
				&cgi_lib::common::message(sprintf("concept_data:[%d]",scalar @{$concept_data}),$LOG) if(defined $LOG);
			}
			if(exists $D->{'concept_data_synonym'} && defined $D->{'concept_data_synonym'} && ref $D->{'concept_data_synonym'} eq 'ARRAY'){
				my $header;
				foreach my $data (@{$D->{'concept_data_synonym'}}){
					$data = &trim($data);
					next unless(defined $data);
					if(index($data,'#') == 0){
						undef $header;
						$header = &get_header($data);
						unless(
									defined	$header
							&&	ref			$header eq 'HASH'
							&&	exists	$header->{$KEYS->{'cdi_name'}}
							&&	exists	$header->{$KEYS->{'cdi_syn_e'}}
							&&	exists	$header->{$KEYS->{'cdi_name_base'}}
							&&	exists	$header->{$KEYS->{'cd_synonym_base'}}
						){
							undef $header;
						}
#						&cgi_lib::common::message($header,$LOG) if(defined $LOG && defined $header)
					}elsif(defined $header){
						my $hash = &set_data2hash($header,$data);
						unless(
									defined	$hash
							&&	ref			$header eq 'HASH'
							&&	exists	$hash->{$KEYS->{'cdi_name'}}
							&&	defined	$hash->{$KEYS->{'cdi_name'}}
							&&	length	$hash->{$KEYS->{'cdi_name'}}
							&&	exists	$hash->{$KEYS->{'cdi_syn_e'}}
							&&	defined	$hash->{$KEYS->{'cdi_syn_e'}}
							&&	length	$hash->{$KEYS->{'cdi_syn_e'}}
						){
							undef $hash;
							next;
						}
						push(@$concept_data_synonym, $hash);
						next;
					}
				}
				&cgi_lib::common::message(sprintf("concept_data_synonym:[%d]",scalar @{$concept_data_synonym}),$LOG) if(defined $LOG);
			}
			if(exists $D->{'concept_tree'} && defined $D->{'concept_tree'} && ref $D->{'concept_tree'} eq 'ARRAY'){
				my $header;
				foreach my $data (@{$D->{'concept_tree'}}){
					$data = &trim($data);
					next unless(defined $data);
					if(index($data,'#') == 0){
						undef $header;
						$header = &get_header($data);
						unless(
									defined	$header
							&&	ref			$header eq 'HASH'
							&&	exists	$header->{$KEYS->{'cdi_name'}}
							&&	exists	$header->{$KEYS->{'cdi_pname'}}
							&&	exists	$header->{$KEYS->{'concept_relation_logic'}}
							&&	exists	$header->{$KEYS->{'concept_relation_types'}}
						){
							undef $header;
						}
#						&cgi_lib::common::message($header,$LOG) if(defined $LOG && defined $header)
					}elsif(defined $header){
						my $hash = &set_data2hash($header,$data);
						unless(
									defined	$hash
							&&	ref			$header eq 'HASH'
							&&	exists	$hash->{$KEYS->{'cdi_name'}}
							&&	defined	$hash->{$KEYS->{'cdi_name'}}
							&&	length	$hash->{$KEYS->{'cdi_name'}}
							&&	exists	$hash->{$KEYS->{'cdi_pname'}}
							&&	defined	$hash->{$KEYS->{'cdi_pname'}}
							&&	length	$hash->{$KEYS->{'cdi_pname'}}
							&&	exists	$hash->{$KEYS->{'concept_relation_logic'}}
							&&	defined	$hash->{$KEYS->{'concept_relation_logic'}}
							&&	length	$hash->{$KEYS->{'concept_relation_logic'}}
						){
							undef $hash;
							next;
						}
						push(@$concept_tree, $hash);
						next;
					}
				}
				&cgi_lib::common::message(sprintf("concept_tree:[%d]",scalar @{$concept_tree}),$LOG) if(defined $LOG);
			}
			if(exists $D->{'concept_tree_info'} && defined $D->{'concept_tree_info'} && ref $D->{'concept_tree_info'} eq 'ARRAY'){
				my $header;
				foreach my $data (@{$D->{'concept_tree_info'}}){
					$data = &trim($data);
					next unless(defined $data);
					if(index($data,'#') == 0){
						undef $header;
						$header = &get_header($data);
						unless(
									defined	$header
							&&	ref			$header eq 'HASH'
							&&	exists	$header->{$KEYS->{'cdi_name'}}
							&&	exists	$header->{$KEYS->{'cti_cnames'}}
							&&	exists	$header->{$KEYS->{'cti_pnames'}}
							&&	exists	$header->{$KEYS->{'concept_relation_logic'}}
							&&	exists	$header->{$KEYS->{'cti_depth'}}
						){
							undef $header;
						}
#						&cgi_lib::common::message($header,$LOG) if(defined $LOG && defined $header)
					}elsif(defined $header){
						my $hash = &set_data2hash($header,$data);
						unless(
									defined	$hash
							&&	ref			$header eq 'HASH'
							&&	exists	$hash->{$KEYS->{'cdi_name'}}
							&&	defined	$hash->{$KEYS->{'cdi_name'}}
							&&	length	$hash->{$KEYS->{'cdi_name'}}
							&&	exists	$hash->{$KEYS->{'concept_relation_logic'}}
							&&	defined	$hash->{$KEYS->{'concept_relation_logic'}}
							&&	length	$hash->{$KEYS->{'concept_relation_logic'}}
						){
							undef $hash;
							next;
						}
						push(@$concept_tree_info, $hash);
						next;
					}
				}
				&cgi_lib::common::message(sprintf("concept_tree_info:[%d]",scalar @{$concept_tree_info}),$LOG) if(defined $LOG);
			}


		}
	}
	elsif(defined $file && -e $file && -f $file){
		my($_name,$_dir,$_ext) = &File::Basename::fileparse($file,@data_extlist);
		$dir = &File::Basename::dirname($file) if(defined $file && -e $file && -f $file);
	}

#	if(defined $LOG){
#		&cgi_lib::common::message($concept_art_map_part,$LOG);
#		&cgi_lib::common::message($concept_part,$LOG);
#		&cgi_lib::common::message($concept_laterality,$LOG);
#		&cgi_lib::common::message($art_laterality,$LOG);
#		die __LINE__ unless(defined $concept_part && defined $concept_laterality && defined $art_laterality);
#	}

	return unless(defined $datas && ref $datas eq 'ARRAY' && scalar @$datas);

	if($format_version eq 'defaults'){
		unless(defined $concept_art_map_part && ref $concept_art_map_part eq 'ARRAY' && scalar @$concept_art_map_part){
			$concept_art_map_part = [];
			$concept_art_map_part->[0]->{$KEYS->{'cmp_title'}} = 'itself';
			$concept_art_map_part->[0]->{$KEYS->{'cmp_abbr'}}   = '';

			$concept_art_map_part->[1]->{$KEYS->{'cmp_title'}}  = 'Left';
			$concept_art_map_part->[1]->{$KEYS->{'cmp_abbr'}}   = 'L';
			$concept_art_map_part->[1]->{$KEYS->{'cmp_prefix'}} = 'LEFT PART OF';
			$concept_art_map_part->[1]->{$KEYS->{'cmp_bul_name_e'}} = 'is_a';

			$concept_art_map_part->[2]->{$KEYS->{'cmp_title'}}  = 'Right';
			$concept_art_map_part->[2]->{$KEYS->{'cmp_abbr'}}   = 'R';
			$concept_art_map_part->[2]->{$KEYS->{'cmp_prefix'}} = 'RIGHT PART OF';
			$concept_art_map_part->[2]->{$KEYS->{'cmp_bul_name_e'}} = 'is_a';

			$concept_art_map_part->[3]->{$KEYS->{'cmp_title'}}  = 'Proper';
			$concept_art_map_part->[3]->{$KEYS->{'cmp_abbr'}}   = 'P';
			$concept_art_map_part->[3]->{$KEYS->{'cmp_display_title'}} = 'Proper or Trunk';
			$concept_art_map_part->[3]->{$KEYS->{'cmp_prefix'}} = 'TRUNK OF';
			$concept_art_map_part->[3]->{$KEYS->{'cmp_bul_name_e'}} = 'part_of';

			$concept_art_map_part->[4]->{$KEYS->{'cmp_title'}}  = 'Far';
			$concept_art_map_part->[4]->{$KEYS->{'cmp_abbr'}}   = 'F';
			$concept_art_map_part->[4]->{$KEYS->{'cmp_display_title'}} = 'Distal (Far)';
			$concept_art_map_part->[4]->{$KEYS->{'cmp_prefix'}} = 'DISTAL';
			$concept_art_map_part->[4]->{$KEYS->{'cmp_bul_name_e'}} = 'is_a';

			$concept_art_map_part->[5]->{$KEYS->{'cmp_title'}}  = 'Near';
			$concept_art_map_part->[5]->{$KEYS->{'cmp_abbr'}}   = 'N';
			$concept_art_map_part->[5]->{$KEYS->{'cmp_display_title'}} = 'Proximal (Near)';
			$concept_art_map_part->[5]->{$KEYS->{'cmp_prefix'}} = 'PROXIMAL';
			$concept_art_map_part->[5]->{$KEYS->{'cmp_bul_name_e'}} = 'is_a';

			$concept_art_map_part->[6]->{$KEYS->{'cmp_title'}}  = 'Other';
			$concept_art_map_part->[6]->{$KEYS->{'cmp_abbr'}}   = 'O';
			$concept_art_map_part->[6]->{$KEYS->{'cmp_display_title'}} = 'Other';
			$concept_art_map_part->[6]->{$KEYS->{'cmp_prefix'}} = 'OTHER';
			$concept_art_map_part->[6]->{$KEYS->{'cmp_bul_name_e'}} = 'is_a';
		}
	}

	&cgi_lib::common::message(sprintf("%f",&Time::HiRes::tv_interval($t)),$LOG) if(defined $LOG);
	#インポートしたconcept_art_map_part情報をDBへ反映
	if(defined $concept_art_map_part && ref $concept_art_map_part eq 'ARRAY' && scalar @$concept_art_map_part){
		my $buildup_logic = {};
		my $bul_id;
		my $bul_name_e;
		my $sth_sel;

		$sth_sel = $dbh->prepare("SELECT bul_id,bul_name_e FROM buildup_logic") or die $dbh->errstr;
		$sth_sel->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth_sel->bind_col(++$column_number, \$bul_id, undef);
		$sth_sel->bind_col(++$column_number, \$bul_name_e, undef);
		while($sth_sel->fetch){
			$buildup_logic->{$bul_name_e} = $bul_id - 0;
		}
		$sth_sel->finish;
		undef $sth_sel;

		my $max_cmp_id;
		$sth_sel = $dbh->prepare(qq|SELECT COALESCE(MAX(cmp_id),-1) FROM concept_art_map_part WHERE md_id=? AND mv_id=? AND mr_id=?|) or die $dbh->errstr;
		$sth_sel->execute($params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'}) or die $dbh->errstr;
		$column_number = 0;
		$sth_sel->bind_col(++$column_number, \$max_cmp_id, undef);
		$sth_sel->fetch;
		$sth_sel->finish;
		undef $sth_sel;

		$sth_sel = $dbh->prepare(qq|SELECT cmp_abbr FROM concept_art_map_part WHERE md_id=? AND mv_id=? AND mr_id=? AND cmp_title=?|) or die $dbh->errstr;
		my $sth_upd = $dbh->prepare(qq|UPDATE concept_art_map_part SET cmp_abbr=?,cmp_display_title=?,cmp_prefix=?,cmp_use=true,cmp_delcause=NULL,bul_id=? WHERE md_id=? AND mv_id=? AND mr_id=? AND cmp_title=?|) or die $dbh->errstr;
		my $sth_ins = $dbh->prepare(qq|INSERT INTO concept_art_map_part (md_id,mv_id,mr_id,cmp_id,cmp_title,cmp_abbr,cmp_display_title,cmp_prefix,cmp_use,bul_id) VALUES (?,?,?,?,?,?,?,?,true,?)|) or die $dbh->errstr;
#		if(defined $LOG){
#			&cgi_lib::common::message($concept_art_map_part,$LOG);
#			die __LINE__;
#		}
		foreach my $p (@$concept_art_map_part){
			foreach my $k (keys(%$p)){
				$p->{$k} = undef if(defined $p->{$k} && !defined &trim($p->{$k}));
			}
			my $cmp_title = $p->{$KEYS->{'cmp_title'}};
			next unless(defined $cmp_title && length $cmp_title);
			my $cmp_abbr = $p->{$KEYS->{'cmp_abbr'}} || '';
			my $cmp_display_title = $p->{$KEYS->{'cmp_display_title'}} || '';
			my $cmp_prefix = $p->{$KEYS->{'cmp_prefix'}} || '';
			my $bul_name_e = $p->{$KEYS->{'cmp_bul_name_e'}};

			my $bul_id;
			$bul_id = $buildup_logic->{$bul_name_e} if(defined $bul_name_e && length $bul_name_e && exists $buildup_logic->{$bul_name_e} && defined $buildup_logic->{$bul_name_e});

			$sth_sel->execute($params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'},$cmp_title) or die $dbh->errstr;
			my $rows = $sth_sel->rows;
			$sth_sel->finish;
			if($rows>0){
				$sth_upd->execute($cmp_abbr,$cmp_display_title,$cmp_prefix,$bul_id,$params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'},$cmp_title) or die $dbh->errstr;
				$sth_upd->finish;
			}
			else{
				$max_cmp_id++;
				$sth_ins->execute($params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'},$max_cmp_id,$cmp_title,$cmp_abbr,$cmp_display_title,$cmp_prefix,$bul_id) or die $dbh->errstr;
				$sth_ins->finish;
			}
		}
		undef $sth_sel;
		undef $sth_upd;
		undef $sth_ins;

#		if(defined $LOG){
#			&cgi_lib::common::message($concept_art_map_part,$LOG);
#			$sth_sel = $dbh->prepare(qq|SELECT * FROM concept_art_map_part WHERE md_id=? AND mv_id=? AND mr_id=? ORDER BY cmp_id|) or die $dbh->errstr;
#			$sth_sel->execute($params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'}) or die $dbh->errstr;
#			while(my $hash_ref = $sth_sel->fetchrow_hashref){
#				&cgi_lib::common::message($hash_ref,$LOG);
#			}
#			$sth_sel->finish;
#			undef $sth_sel;
#		}
	}
	&cgi_lib::common::message(sprintf("%f",&Time::HiRes::tv_interval($t)),$LOG) if(defined $LOG);

	#インポートしたconcept_part情報をbuildup_concept_partテーブルへ反映
	if(defined $concept_part && ref $concept_part eq 'ARRAY' && scalar @$concept_part){
		my $buildup_logic = {};
		my $bul_id;
		my $bul_name_e;
		my $sth_sel;

		$sth_sel = $dbh->prepare("SELECT bul_id,bul_name_e FROM buildup_logic") or die $dbh->errstr;
		$sth_sel->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth_sel->bind_col(++$column_number, \$bul_id, undef);
		$sth_sel->bind_col(++$column_number, \$bul_name_e, undef);
		while($sth_sel->fetch){
			$buildup_logic->{$bul_name_e} = $bul_id - 0;
		}
		$sth_sel->finish;
		undef $sth_sel;

		my $max_bcp_id;
		$sth_sel = $dbh->prepare(qq|SELECT COALESCE(MAX(bcp_id),-1) FROM buildup_concept_part WHERE md_id=? AND mv_id=? AND mr_id=?|) or die $dbh->errstr;
		$sth_sel->execute($params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'}) or die $dbh->errstr;
		$column_number = 0;
		$sth_sel->bind_col(++$column_number, \$max_bcp_id, undef);
		$sth_sel->fetch;
		$sth_sel->finish;
		undef $sth_sel;

		$sth_sel = $dbh->prepare(qq|SELECT bcp_abbr FROM buildup_concept_part WHERE md_id=? AND mv_id=? AND mr_id=? AND bcp_title=?|) or die $dbh->errstr;
		my $sth_upd = $dbh->prepare(qq|UPDATE buildup_concept_part SET bcp_abbr=?,bcp_display_title=?,bcp_prefix=?,bcp_use=true,bcp_delcause=NULL,bul_id=? WHERE md_id=? AND mv_id=? AND mr_id=? AND bcp_title=?|) or die $dbh->errstr;
		my $sth_ins = $dbh->prepare(qq|INSERT INTO buildup_concept_part (md_id,mv_id,mr_id,bcp_id,bcp_title,bcp_abbr,bcp_display_title,bcp_prefix,bcp_use,bul_id) VALUES (?,?,?,?,?,?,?,?,true,?)|) or die $dbh->errstr;
#		if(defined $LOG){
#			&cgi_lib::common::message($concept_art_map_part,$LOG);
#			die __LINE__;
#		}
		foreach my $p (@$concept_part){
			foreach my $k (keys(%$p)){
				$p->{$k} = undef if(defined $p->{$k} && !defined &trim($p->{$k}));
			}
			my $bcp_title = $p->{$KEYS->{'bcp_title'}};
			next unless(defined $bcp_title && length $bcp_title);
			my $bcp_abbr = $p->{$KEYS->{'bcp_abbr'}} || '';
			my $bcp_display_title = $p->{$KEYS->{'bcp_display_title'}} || '';
			my $bcp_prefix = $p->{$KEYS->{'bcp_prefix'}} || '';
			my $bul_name_e = $p->{$KEYS->{'bcp_bul_name_e'}};

			my $bul_id;
			$bul_id = $buildup_logic->{$bul_name_e} if(defined $bul_name_e && length $bul_name_e && exists $buildup_logic->{$bul_name_e} && defined $buildup_logic->{$bul_name_e});

			$sth_sel->execute($params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'},$bcp_title) or die $dbh->errstr;
			my $rows = $sth_sel->rows;
			$sth_sel->finish;
			if($rows>0){
				$sth_upd->execute($bcp_abbr,$bcp_display_title,$bcp_prefix,$bul_id,$params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'},$bcp_title) or die $dbh->errstr;
				$sth_upd->finish;
			}
			else{
				$max_bcp_id++;
				$sth_ins->execute($params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'},$max_bcp_id,$bcp_title,$bcp_abbr,$bcp_display_title,$bcp_prefix,$bul_id) or die $dbh->errstr;
				$sth_ins->finish;
			}
		}
		undef $sth_sel;
		undef $sth_upd;
		undef $sth_ins;

#		if(defined $LOG){
#			&cgi_lib::common::message($concept_part,$LOG);
#			$sth_sel = $dbh->prepare(qq|SELECT * FROM buildup_concept_part WHERE md_id=? AND mv_id=? AND mr_id=? ORDER BY bcp_id|) or die $dbh->errstr;
#			$sth_sel->execute($params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'}) or die $dbh->errstr;
#			while(my $hash_ref = $sth_sel->fetchrow_hashref){
#				&cgi_lib::common::message($hash_ref,$LOG);
#			}
#			$sth_sel->finish;
#			undef $sth_sel;
#		}
	}
	&cgi_lib::common::message(sprintf("%f",&Time::HiRes::tv_interval($t)),$LOG) if(defined $LOG);

	#インポートしたconcept_laterality情報をbuildup_concept_lateralityテーブルへ反映
	if(defined $concept_laterality && ref $concept_laterality eq 'ARRAY' && scalar @$concept_laterality){
		my $sth_sel;

		my $max_bcl_id;
		$sth_sel = $dbh->prepare(qq|SELECT COALESCE(MAX(bcl_id),-1) FROM buildup_concept_laterality WHERE md_id=? AND mv_id=? AND mr_id=?|) or die $dbh->errstr;
		$sth_sel->execute($params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'}) or die $dbh->errstr;
		$column_number = 0;
		$sth_sel->bind_col(++$column_number, \$max_bcl_id, undef);
		$sth_sel->fetch;
		$sth_sel->finish;
		undef $sth_sel;

		$sth_sel = $dbh->prepare(qq|SELECT bcl_abbr FROM buildup_concept_laterality WHERE md_id=? AND mv_id=? AND mr_id=? AND bcl_title=?|) or die $dbh->errstr;
		my $sth_upd = $dbh->prepare(qq|UPDATE buildup_concept_laterality SET bcl_abbr=?,bcl_display_title=?,bcl_prefix=?,bcl_use=true,bcl_delcause=NULL WHERE md_id=? AND mv_id=? AND mr_id=? AND bcl_title=?|) or die $dbh->errstr;
		my $sth_ins = $dbh->prepare(qq|INSERT INTO buildup_concept_laterality (md_id,mv_id,mr_id,bcl_id,bcl_title,bcl_abbr,bcl_display_title,bcl_prefix,bcl_use) VALUES (?,?,?,?,?,?,?,?,true)|) or die $dbh->errstr;
#		if(defined $LOG){
#			&cgi_lib::common::message($concept_art_map_part,$LOG);
#			die __LINE__;
#		}
		foreach my $p (@$concept_laterality){
			foreach my $k (keys(%$p)){
				$p->{$k} = undef if(defined $p->{$k} && !defined &trim($p->{$k}));
			}
			my $bcl_title = $p->{$KEYS->{'bcl_title'}};
			next unless(defined $bcl_title && length $bcl_title);
			my $bcl_abbr = $p->{$KEYS->{'bcl_abbr'}} || '';
			my $bcl_display_title = $p->{$KEYS->{'bcl_display_title'}} || '';
			my $bcl_prefix = $p->{$KEYS->{'bcl_prefix'}} || '';

			$sth_sel->execute($params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'},$bcl_title) or die $dbh->errstr;
			my $rows = $sth_sel->rows;
			$sth_sel->finish;
			if($rows>0){
				$sth_upd->execute($bcl_abbr,$bcl_display_title,$bcl_prefix,$params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'},$bcl_title) or die $dbh->errstr;
				$sth_upd->finish;
			}
			else{
				$max_bcl_id++;
				$sth_ins->execute($params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'},$max_bcl_id,$bcl_title,$bcl_abbr,$bcl_display_title,$bcl_prefix) or die $dbh->errstr;
				$sth_ins->finish;
			}
		}
		undef $sth_sel;
		undef $sth_upd;
		undef $sth_ins;

#		if(defined $LOG){
#			&cgi_lib::common::message($concept_laterality,$LOG);
#			$sth_sel = $dbh->prepare(qq|SELECT * FROM buildup_concept_laterality WHERE md_id=? AND mv_id=? AND mr_id=? ORDER BY bcl_id|) or die $dbh->errstr;
#			$sth_sel->execute($params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'}) or die $dbh->errstr;
#			while(my $hash_ref = $sth_sel->fetchrow_hashref){
#				&cgi_lib::common::message($hash_ref,$LOG);
#			}
#			$sth_sel->finish;
#			undef $sth_sel;
#		}
	}
	&cgi_lib::common::message(sprintf("%f",&Time::HiRes::tv_interval($t)),$LOG) if(defined $LOG);

	#インポートしたart_laterality情報をart_lateralityテーブルへ反映
	if(defined $art_laterality && ref $art_laterality eq 'ARRAY' && scalar @$art_laterality){
		my $sth_sel;

		my $max_artl_id;
		$sth_sel = $dbh->prepare(qq|SELECT COALESCE(MAX(artl_id),-1) FROM art_laterality|) or die $dbh->errstr;
		$sth_sel->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth_sel->bind_col(++$column_number, \$max_artl_id, undef);
		$sth_sel->fetch;
		$sth_sel->finish;
		undef $sth_sel;

		$sth_sel = $dbh->prepare(qq|SELECT artl_abbr FROM art_laterality WHERE artl_title=?|) or die $dbh->errstr;
		my $sth_upd = $dbh->prepare(qq|UPDATE art_laterality SET artl_abbr=?,artl_display_title=?,artl_prefix=?,artl_use=true,artl_delcause=NULL WHERE artl_title=?|) or die $dbh->errstr;
		my $sth_ins = $dbh->prepare(qq|INSERT INTO art_laterality (artl_id,artl_title,artl_abbr,artl_display_title,artl_prefix,artl_use) VALUES (?,?,?,?,?,true)|) or die $dbh->errstr;
#		if(defined $LOG){
#			&cgi_lib::common::message($concept_art_map_part,$LOG);
#			die __LINE__;
#		}
		foreach my $p (@$art_laterality){
			foreach my $k (keys(%$p)){
				$p->{$k} = undef if(defined $p->{$k} && !defined &trim($p->{$k}));
			}
			my $artl_title = $p->{$KEYS->{'artl_title'}};
			next unless(defined $artl_title && length $artl_title);
			my $artl_abbr = $p->{$KEYS->{'artl_abbr'}} || '';
			my $artl_display_title = $p->{$KEYS->{'artl_display_title'}} || '';
			my $artl_prefix = $p->{$KEYS->{'artl_prefix'}} || '';

			$sth_sel->execute($artl_title) or die $dbh->errstr;
			my $rows = $sth_sel->rows;
			$sth_sel->finish;
			if($rows>0){
				$sth_upd->execute($artl_abbr,$artl_display_title,$artl_prefix,$artl_title) or die $dbh->errstr;
				$sth_upd->finish;
			}
			else{
				$max_artl_id++;
				$sth_ins->execute($max_artl_id,$artl_title,$artl_abbr,$artl_display_title,$artl_prefix) or die $dbh->errstr;
				$sth_ins->finish;
			}
		}
		undef $sth_sel;
		undef $sth_upd;
		undef $sth_ins;

#		if(defined $LOG){
#			&cgi_lib::common::message($art_laterality,$LOG);
#			$sth_sel = $dbh->prepare(qq|SELECT * FROM art_laterality ORDER BY artl_id|) or die $dbh->errstr;
#			$sth_sel->execute() or die $dbh->errstr;
#			while(my $hash_ref = $sth_sel->fetchrow_hashref){
#				&cgi_lib::common::message($hash_ref,$LOG);
#			}
#			$sth_sel->finish;
#			undef $sth_sel;
#		}
	}
	&cgi_lib::common::message(sprintf("%f",&Time::HiRes::tv_interval($t)),$LOG) if(defined $LOG);

	#インポートしたconcept_segment情報をconcept_segmentテーブルへ反映
	if(defined $concept_segment && ref $concept_segment eq 'ARRAY' && scalar @$concept_segment){
		&cgi_lib::common::message(sprintf("%f",&Time::HiRes::tv_interval($t)),$LOG) if(defined $LOG);

		#concept_data_info
		my $cdi_id;
		my $cdi_name;
		my $CDI_HASH;
		my $sth_sel_cdi = $dbh->prepare_cached(qq|SELECT cdi_id,cdi_name FROM concept_data_info WHERE ci_id=?|) or die $dbh->errstr;
		$sth_sel_cdi->execute($params->{'ci_id'}) or die $dbh->errstr;
		$column_number = 0;
		$sth_sel_cdi->bind_col(++$column_number, \$cdi_id, undef);
		$sth_sel_cdi->bind_col(++$column_number, \$cdi_name, undef);
		while($sth_sel_cdi->fetch){
			$cdi_id = $cdi_id - 0;
			$CDI_HASH->{$cdi_name} = $cdi_id;
		}
		$sth_sel_cdi->finish;
		undef $sth_sel_cdi;

		#concept_segment
		my $seg_id;
		my $seg_name;
		my $SEG_HASH;
		my $sth_sel_seg = $dbh->prepare_cached(qq|SELECT seg_id,seg_name FROM concept_segment|) or die $dbh->errstr;
		$sth_sel_seg->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth_sel_seg->bind_col(++$column_number, \$seg_id, undef);
		$sth_sel_seg->bind_col(++$column_number, \$seg_name, undef);
		while($sth_sel_seg->fetch){
			$SEG_HASH->{$seg_name} = $seg_id - 0;
		}
		$sth_sel_seg->finish;
		undef $sth_sel_seg;

		#concept_segment_group
		my $max_csg_id = -1;
		my $csg_id;
		my $csg_name;
		my $CSG_HASH;
		my $sth_sel_csg = $dbh->prepare(qq|SELECT csg_id,csg_name FROM concept_segment_group|) or die $dbh->errstr;
		$sth_sel_csg->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth_sel_csg->bind_col(++$column_number, \$csg_id, undef);
		$sth_sel_csg->bind_col(++$column_number, \$csg_name, undef);
		while($sth_sel_csg->fetch){
			$CSG_HASH->{$csg_name} = $csg_id - 0;
			$max_csg_id = $csg_id - 0 if($max_csg_id < $csg_id - 0);
		}
		$sth_sel_csg->finish;
		undef $sth_sel_csg;

		my $sth_ins_seg = $dbh->prepare(qq|INSERT INTO concept_segment (seg_name,seg_color,seg_thum_bgcolor,seg_thum_bocolor,seg_thum_fgcolor,csg_id,cdf_name,cdi_ids) VALUES (?,?,?,?,?,?,?,?) RETURNING csg_id|) or die $dbh->errstr;
		my $sth_upd_seg = $dbh->prepare(qq|UPDATE concept_segment SET seg_color=?,seg_thum_bgcolor=?,seg_thum_bocolor=?,seg_thum_fgcolor=?,csg_id=?,cdf_name=?,cdi_ids=? WHERE seg_id=?|) or die $dbh->errstr;

		my $sth_ins_csg = $dbh->prepare(qq|INSERT INTO concept_segment_group (csg_id,csg_name) VALUES (?,?)|) or die $dbh->errstr;

		foreach my $p (@{$concept_segment}){
			map { $p->{$_} = undef unless(defined $p->{$_} && length &trim($p->{$_})) } keys(%{$p});
			&cgi_lib::common::message($p,$LOG) if(defined $LOG);
			my $seg_name = $p->{$KEYS->{'seg_name'}};
			my $seg_color = $p->{$KEYS->{'seg_color'}};
			my $seg_thum_bgcolor = $p->{$KEYS->{'seg_thum_bgcolor'}};
			my $seg_thum_bocolor = $p->{$KEYS->{'seg_thum_bocolor'}};
			my $seg_thum_fgcolor = $p->{$KEYS->{'seg_thum_fgcolor'}};
			my $csg_name = $p->{$KEYS->{'csg_name'}};
			my $cdi_ids = $p->{$KEYS->{'cdi_ids'}};
			my $cdf_name = $p->{$KEYS->{'cdf_name'}};

			next unless(defined $seg_name && length $seg_name);

			if(defined $cdi_ids && length $cdi_ids){
				my $cdi_ids_arr = &cgi_lib::common::decodeJSON($cdi_ids);
				my $temp_arr = [map {$CDI_HASH->{$_}} grep {exists $CDI_HASH->{$_} && defined $CDI_HASH->{$_}} @{$cdi_ids_arr}] if(defined $cdi_ids_arr && ref $cdi_ids_arr eq 'ARRAY' && scalar @{$cdi_ids_arr});
				$cdi_ids = &cgi_lib::common::decodeUTF8(&cgi_lib::common::encodeJSON($temp_arr)) if(defined $temp_arr && ref $temp_arr eq 'ARRAY' && scalar @{$temp_arr});
			}
			my $csg_id;
			if(defined $csg_name && length $csg_name){
				&cgi_lib::common::message(sprintf("seg_name=[%s]",$seg_name),$LOG) if(defined $LOG);
				unless(exists $CSG_HASH->{$csg_name} && defined $CSG_HASH->{$csg_name}){
					$max_csg_id++;
					$csg_id = $max_csg_id;
					$sth_ins_csg->execute($csg_id,$csg_name) or die $dbh->errstr;
					$sth_ins_seg->finish;
					$CSG_HASH->{$csg_name} = $csg_id;
				}
				else{
					$csg_id = $CSG_HASH->{$csg_name};
				}
			}
			else{
				&cgi_lib::common::message(sprintf("seg_name=[null]"),$LOG) if(defined $LOG);
			}

			unless(exists $SEG_HASH->{$seg_name} && defined $SEG_HASH->{$seg_name}){
				&cgi_lib::common::message(sprintf("[new][%s]",$seg_name),$LOG) if(defined $LOG);
				$sth_ins_seg->execute(
					 $seg_name
					,$seg_color
					,$seg_thum_bgcolor
					,$seg_thum_bocolor
					,$seg_thum_fgcolor
					,$csg_id
					,$cdf_name
					,$cdi_ids
				) or die $dbh->errstr;
				my $seg_id;
				$column_number = 0;
				$sth_ins_seg->bind_col(++$column_number, \$seg_id, undef);
				$sth_ins_seg->fetch;
				$sth_ins_seg->finish;
				$SEG_HASH->{$seg_name} = $seg_id - 0;
			}
			else{
				&cgi_lib::common::message(sprintf("[%d][%s]",$SEG_HASH->{$seg_name},$seg_name),$LOG) if(defined $LOG);
				my $seg_id = $SEG_HASH->{$seg_name};
				$sth_upd_seg->execute(
					 $seg_color
					,$seg_thum_bgcolor
					,$seg_thum_bocolor
					,$seg_thum_fgcolor
					,$csg_id
					,$cdf_name
					,$cdi_ids
					,$seg_id
				) or die $dbh->errstr;
				$sth_upd_seg->finish;
			}
		}
		undef $sth_ins_seg;
		undef $sth_upd_seg;
		undef $sth_ins_csg;
	}

	#インポートしたconcept_data情報をbuildup_dataテーブルへ反映
	if(defined $concept_data && ref $concept_data eq 'ARRAY' && scalar @$concept_data){
		&cgi_lib::common::message(sprintf("%f",&Time::HiRes::tv_interval($t)),$LOG) if(defined $LOG);
		#concept_data_info
		my $max_cdi_id = -1;
		my $cdi_id;
		my $cdi_name;
		my $CDI_HASH;
		my $sth_sel_cdi = $dbh->prepare_cached(qq|SELECT cdi_id,cdi_name FROM concept_data_info WHERE ci_id=?|) or die $dbh->errstr;
		$sth_sel_cdi->execute($params->{'ci_id'}) or die $dbh->errstr;
		$column_number = 0;
		$sth_sel_cdi->bind_col(++$column_number, \$cdi_id, undef);
		$sth_sel_cdi->bind_col(++$column_number, \$cdi_name, undef);
		while($sth_sel_cdi->fetch){
			$cdi_id = $cdi_id - 0;
			$max_cdi_id = $cdi_id if($cdi_id>$max_cdi_id);
			$CDI_HASH->{$cdi_name} = $cdi_id;
		}
		$sth_sel_cdi->finish;
		undef $sth_sel_cdi;

		#concept_segment
		my $seg_id;
		my $seg_name;
		my $SEG_HASH;
		my $sth_sel_seg = $dbh->prepare_cached(qq|SELECT seg_id,seg_name FROM concept_segment|) or die $dbh->errstr;
		$sth_sel_seg->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth_sel_seg->bind_col(++$column_number, \$seg_id, undef);
		$sth_sel_seg->bind_col(++$column_number, \$seg_name, undef);
		while($sth_sel_seg->fetch){
			$SEG_HASH->{$seg_name} = $seg_id - 0;
		}
		$sth_sel_seg->finish;
		undef $sth_sel_seg;

		#concept_art_map_part
		my $cmp_id;
		my $cmp_title;
		my $CMP_HASH;
		my $sth_sel_cmp = $dbh->prepare(qq|SELECT cmp_id,cmp_title FROM concept_art_map_part WHERE md_id=? AND mv_id=? AND mr_id=?|) or die $dbh->errstr;
		$sth_sel_cmp->execute($params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'}) or die $dbh->errstr;
		$column_number = 0;
		$sth_sel_cmp->bind_col(++$column_number, \$cmp_id, undef);
		$sth_sel_cmp->bind_col(++$column_number, \$cmp_title, undef);
		while($sth_sel_cmp->fetch){
			$CMP_HASH->{$cmp_title} = $cmp_id - 0;
		}
		$sth_sel_cmp->finish;
		undef $sth_sel_cmp;

		#buildup_concept_part
		my $bcp_id;
		my $bcp_title;
		my $BCP_HASH;
		my $sth_sel_bcp = $dbh->prepare(qq|SELECT bcp_id,bcp_title FROM buildup_concept_part WHERE md_id=? AND mv_id=? AND mr_id=?|) or die $dbh->errstr;
		$sth_sel_bcp->execute($params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'}) or die $dbh->errstr;
		$column_number = 0;
		$sth_sel_bcp->bind_col(++$column_number, \$bcp_id, undef);
		$sth_sel_bcp->bind_col(++$column_number, \$bcp_title, undef);
		while($sth_sel_bcp->fetch){
			$BCP_HASH->{$bcp_title} = $bcp_id - 0;
		}
		$sth_sel_bcp->finish;
		undef $sth_sel_bcp;

		#buildup_concept_laterality
		my $bcl_id;
		my $bcl_title;
		my $BCL_HASH;
		my $sth_sel_bcl = $dbh->prepare(qq|SELECT bcl_id,bcl_title FROM buildup_concept_laterality WHERE md_id=? AND mv_id=? AND mr_id=?|) or die $dbh->errstr;
		$sth_sel_bcl->execute($params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'}) or die $dbh->errstr;
		$column_number = 0;
		$sth_sel_bcl->bind_col(++$column_number, \$bcl_id, undef);
		$sth_sel_bcl->bind_col(++$column_number, \$bcl_title, undef);
		while($sth_sel_bcl->fetch){
			$BCL_HASH->{$bcl_title} = $bcl_id - 0;
		}
		$sth_sel_bcl->finish;
		undef $sth_sel_bcl;

		my $BD_HASH;
		my $sth_sel_bd = $dbh->prepare_cached(qq|SELECT cdi_id FROM buildup_data WHERE md_id=? AND mv_id=? AND mr_id=? AND ci_id=? AND cb_id=?|) or die $dbh->errstr;
		$sth_sel_bd->execute($params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'},$params->{'ci_id'},$params->{'cb_id'}) or die $dbh->errstr;
		$column_number = 0;
		$sth_sel_bd->bind_col(++$column_number, \$cdi_id, undef);
		while($sth_sel_bd->fetch){
			$BD_HASH->{$cdi_id} = 0;
		}
		$sth_sel_bd->finish;
		undef $sth_sel_bd;

		my $sth_ins_cdi = $dbh->prepare(qq|INSERT INTO concept_data_info (ci_id,cdi_id,cdi_name,cdi_name_e,cdi_syn_e,is_user_data) VALUES (?,?,?,?,?,?)|) or die $dbh->errstr;
		my $sth_ins_bd = $dbh->prepare(qq|INSERT INTO buildup_data (md_id,mv_id,mr_id,ci_id,cb_id,cdi_id,cd_name,cd_syn,seg_id,cmp_id,bcp_id,bcl_id,cdi_pid,cdi_sid) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)|) or die $dbh->errstr;
		my $sth_upd_bd = $dbh->prepare(qq|UPDATE buildup_data SET cd_syn=?,seg_id=?,cmp_id=?,bcp_id=?,bcl_id=?,cdi_pid=?,cdi_sid=? WHERE md_id=? AND mv_id=? AND mr_id=? AND ci_id=? AND cb_id=? AND cdi_id=?|) or die $dbh->errstr;

		foreach my $p (@{$concept_data}){
			map { $p->{$_} = undef unless(defined $p->{$_} && length &trim($p->{$_})) } keys(%{$p});
			my $cdi_name = $p->{$KEYS->{'cdi_name'}};
			my $cdi_name_e = $p->{$KEYS->{'cdi_name_e'}};
			my $cdi_syn_e = $p->{$KEYS->{'cdi_syn_e'}};
			my $seg_name = $p->{$KEYS->{'seg_name'}};
			my $is_user_data = $p->{$KEYS->{'is_user_data'}};
			my $cmp_title = $p->{$KEYS->{'cmp_title'}};
			my $bcp_title = $p->{$KEYS->{'bcp_title'}};
			my $bcl_title = $p->{$KEYS->{'bcl_title'}};
			my $cdi_pname = $p->{$KEYS->{'cdi_pname'}};
			my $cdi_sname = $p->{$KEYS->{'cdi_sname'}};
			my $cdi_id;
			my $seg_id;
			my $cmp_id;
			my $bcp_id;
			my $bcl_id;
			my $cdi_pid;
			my $cdi_sid;

			$is_user_data = $is_user_data - 0 if(defined $is_user_data);

			if(exists $CDI_HASH->{$cdi_name} && defined $CDI_HASH->{$cdi_name}){
#				&cgi_lib::common::message(sprintf("[%d][%s]",$CDI_HASH->{$cdi_name},$cdi_name),$LOG) if(defined $LOG);
				$cdi_id = $CDI_HASH->{$cdi_name};
			}
			else{
				$max_cdi_id++;
#				&cgi_lib::common::message(sprintf("[%d][%s]",$max_cdi_id,$cdi_name),$LOG) if(defined $LOG);
				$sth_ins_cdi->execute($params->{'ci_id'},$max_cdi_id,$cdi_name,$cdi_name_e,$cdi_syn_e,$is_user_data) or die $dbh->errstr;
				$sth_ins_cdi->finish;
				$cdi_id = $CDI_HASH->{$cdi_name} = $max_cdi_id;
			}
#			&cgi_lib::common::message($seg_name,$LOG) if(defined $LOG);
			$seg_id = $SEG_HASH->{$seg_name} if(defined $seg_name && length $seg_name && exists $SEG_HASH->{$seg_name} && defined $SEG_HASH->{$seg_name});
			$cmp_id = $CMP_HASH->{$cmp_title} if(defined $cmp_title && length $cmp_title && exists $CMP_HASH->{$cmp_title} && defined $CMP_HASH->{$cmp_title});
			$bcp_id = $BCP_HASH->{$bcp_title} if(defined $bcp_title && length $bcp_title && exists $BCP_HASH->{$bcp_title} && defined $BCP_HASH->{$bcp_title});
			$bcl_id = $BCL_HASH->{$bcl_title} if(defined $bcl_title && length $bcl_title && exists $BCL_HASH->{$bcl_title} && defined $BCL_HASH->{$bcl_title});
			$cdi_pid = $CDI_HASH->{$cdi_pname} if(defined $cdi_pname && length $cdi_pname && exists $CDI_HASH->{$cdi_pname} && defined $CDI_HASH->{$cdi_pname});
			$cdi_sid = $CDI_HASH->{$cdi_sname} if(defined $cdi_sname && length $cdi_sname && exists $CDI_HASH->{$cdi_sname} && defined $CDI_HASH->{$cdi_sname});

			unless(exists $BD_HASH->{$cdi_id}){
				$sth_ins_bd->execute(
					 $params->{'md_id'}
					,$params->{'mv_id'}
					,$params->{'mr_id'}
					,$params->{'ci_id'}
					,$params->{'cb_id'}
					,$cdi_id
					,$cdi_name_e
					,$cdi_syn_e
					,$seg_id
					,$cmp_id
					,$bcp_id
					,$bcl_id
					,$cdi_pid
					,$cdi_sid
				) or die $dbh->errstr;
				$sth_ins_bd->finish;
				$BD_HASH->{$cdi_id} = 0;
#				&cgi_lib::common::message($cdi_id,$LOG) if(defined $LOG);
			}
			else{
				$sth_upd_bd->execute(
					 $cdi_syn_e
					,$seg_id
					,$cmp_id
					,$bcp_id
					,$bcl_id
					,$cdi_pid
					,$cdi_sid
					,$params->{'md_id'}
					,$params->{'mv_id'}
					,$params->{'mr_id'}
					,$params->{'ci_id'}
					,$params->{'cb_id'}
					,$cdi_id
				) or die $dbh->errstr;
				$sth_upd_bd->finish;
#				&cgi_lib::common::message($cdi_id,$LOG) if(defined $LOG);
			}
			$BD_HASH->{$cdi_id}++;
		}


		undef $sth_ins_cdi;
		undef $sth_ins_bd;
		undef $sth_upd_bd;
	}
	&cgi_lib::common::message(sprintf("%f",&Time::HiRes::tv_interval($t)),$LOG) if(defined $LOG);


	#インポートしたconcept_data_synonym情報をbuildup_data_synonymテーブルへ反映
	if(defined $concept_data_synonym && ref $concept_data_synonym eq 'ARRAY' && scalar @$concept_data_synonym){
		#concept_data_info
		my $cdi_id;
		my $cdi_name;
		my $CDI_HASH;
		my $sth_sel_cdi = $dbh->prepare_cached(qq|SELECT cdi_id,cdi_name FROM concept_data_info WHERE ci_id=?|) or die $dbh->errstr;
		$sth_sel_cdi->execute($params->{'ci_id'}) or die $dbh->errstr;
		$column_number = 0;
		$sth_sel_cdi->bind_col(++$column_number, \$cdi_id, undef);
		$sth_sel_cdi->bind_col(++$column_number, \$cdi_name, undef);
		while($sth_sel_cdi->fetch){
			$cdi_id = $cdi_id - 0;
			$CDI_HASH->{$cdi_name} = $cdi_id;
		}
		$sth_sel_cdi->finish;
		undef $sth_sel_cdi;

		#concept_synonym
		my $cs_id;
		my $cs_name;
		my $CS_HASH;
		my $sth_sel_cs = $dbh->prepare(qq|SELECT cs_id,cs_name FROM concept_synonym|) or die $dbh->errstr;
		$sth_sel_cs->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth_sel_cs->bind_col(++$column_number, \$cs_id, undef);
		$sth_sel_cs->bind_col(++$column_number, \$cs_name, undef);
		while($sth_sel_cs->fetch){
			$CS_HASH->{$cs_name} = $cs_id - 0;
		}
		$sth_sel_cs->finish;
		undef $sth_sel_cs;

		#buildup_data
		my $BD_HASH;
		my $sth_sel_bd = $dbh->prepare_cached(qq|SELECT cdi_id FROM buildup_data WHERE md_id=? AND mv_id=? AND mr_id=? AND ci_id=? AND cb_id=?|) or die $dbh->errstr;
		$sth_sel_bd->execute($params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'},$params->{'ci_id'},$params->{'cb_id'}) or die $dbh->errstr;
		$column_number = 0;
		$sth_sel_bd->bind_col(++$column_number, \$cdi_id, undef);
		while($sth_sel_bd->fetch){
			$BD_HASH->{$cdi_id} = undef;
		}
		$sth_sel_bd->finish;
		undef $sth_sel_bd;

		#buildup_data_synonym
		my $cds_id;
		my $BDS_HASH;
		my $sth_sel_bds = $dbh->prepare(qq|
SELECT
  cds_id
 ,cdi_id
 ,cs_id
FROM
  buildup_data_synonym AS cds
LEFT JOIN concept_data_synonym_type AS cdst ON cdst.cdst_id=cds.cdst_id
WHERE
  md_id=? AND mv_id=? AND mr_id=? AND ci_id=? AND cb_id=? AND cdst.cdst_name='synonym'
|) or die $dbh->errstr;
		$sth_sel_bds->execute($params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'},$params->{'ci_id'},$params->{'cb_id'}) or die $dbh->errstr;
		$column_number = 0;
		$sth_sel_bds->bind_col(++$column_number, \$cds_id, undef);
		$sth_sel_bds->bind_col(++$column_number, \$cdi_id, undef);
		$sth_sel_bds->bind_col(++$column_number, \$cs_id, undef);
		while($sth_sel_bds->fetch){
			$BDS_HASH->{$cdi_id}->{$cs_id} = $cds_id;
		}
		$sth_sel_bds->finish;
		undef $sth_sel_bds;

		#concept_data_synonym_type
		my $cdst_id;
		my $sth_sel_bdst = $dbh->prepare(qq|SELECT cdst_id FROM concept_data_synonym_type WHERE cdst_name='synonym'|) or die $dbh->errstr;
		$sth_sel_bdst->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth_sel_bdst->bind_col(++$column_number, \$cdst_id, undef);
		$sth_sel_bdst->fetch;
		$sth_sel_bdst->finish;
		undef $sth_sel_bdst;

		my $sth_ins_cs = $dbh->prepare(qq|INSERT INTO concept_synonym (cs_name) VALUES (?) RETURNING cs_id|) or die $dbh->errstr;
		my $sth_ins_bds = $dbh->prepare(qq|INSERT INTO buildup_data_synonym (md_id,mv_id,mr_id,ci_id,cb_id,cdi_id,cs_id,cdst_id) VALUES (?,?,?,?,?,?,?,$cdst_id) RETURNING cds_id|) or die $dbh->errstr;

		foreach my $p (@{$concept_data_synonym}){
			map { $p->{$_} = undef unless(defined $p->{$_} && length &trim($p->{$_})) } keys(%{$p});
			my $cdi_name = $p->{$KEYS->{'cdi_name'}};
			my $cs_name = $p->{$KEYS->{'cdi_syn_e'}};
			my $cdi_bname = $p->{$KEYS->{'cdi_name_base'}};
			my $cs_bname = $p->{$KEYS->{'cd_synonym_base'}};

			next unless(defined $cdi_name && length $cdi_name && exists $CDI_HASH->{$cdi_name} && defined $CDI_HASH->{$cdi_name});
			next unless(defined $cs_name && length $cs_name);

			my $cdi_id = $CDI_HASH->{$cdi_name};
			my $cs_id;

			unless(exists $CS_HASH->{$cs_name} && defined $CS_HASH->{$cs_name}){
				$sth_ins_cs->execute($cs_name) or die $dbh->errstr;
				$column_number=0;
				$sth_ins_cs->bind_col(++$column_number, \$cs_id, undef);
				$sth_ins_cs->fetch;
				$sth_ins_cs->finish;
				$CS_HASH->{$cs_name} = $cs_id;
			}
			else{
				$cs_id = $CS_HASH->{$cs_name};
			}
			unless(
						exists	$BDS_HASH->{$cdi_id}
				&&	defined	$BDS_HASH->{$cdi_id}
				&&	ref			$BDS_HASH->{$cdi_id} eq 'HASH'
				&&	exists	$BDS_HASH->{$cdi_id}->{$cs_id}
				&&	defined	$BDS_HASH->{$cdi_id}->{$cs_id}
			){
				$sth_ins_bds->execute($params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'},$params->{'ci_id'},$params->{'cb_id'},$cdi_id,$cs_id) or die $dbh->errstr;
				$column_number = 0;
				$sth_ins_bds->bind_col(++$column_number, \$cds_id, undef);
				$sth_ins_bds->fetch;
				$sth_ins_bds->finish;
				$BDS_HASH->{$cdi_id}->{$cs_id} = $cds_id;
			}
		}
		undef $sth_ins_cs;
		undef $sth_ins_bds;

		my $sth_upd_bds_added = $dbh->prepare(qq|UPDATE buildup_data_synonym SET cds_added=true WHERE md_id=? AND mv_id=? AND mr_id=? AND ci_id=? AND cb_id=? AND cdi_id=? AND cs_id=? AND cdst_id=$cdst_id|) or die $dbh->errstr;
		my $sth_upd_bds_bid = $dbh->prepare(qq|UPDATE buildup_data_synonym SET cds_bid=? WHERE md_id=? AND mv_id=? AND mr_id=? AND ci_id=? AND cb_id=? AND cdi_id=? AND cs_id=? AND cdst_id=$cdst_id|) or die $dbh->errstr;
		foreach my $p (@{$concept_data_synonym}){
			map { $p->{$_} = undef unless(defined $p->{$_} && length &trim($p->{$_})) } keys(%{$p});
			my $cdi_name = $p->{$KEYS->{'cdi_name'}};
			my $cs_name = $p->{$KEYS->{'cdi_syn_e'}};
			my $cdi_bname = $p->{$KEYS->{'cdi_name_base'}};
			my $cs_bname = $p->{$KEYS->{'cd_synonym_base'}};

			if(
						defined	$cdi_name
				&&	length	$cdi_name
				&&	exists	$CDI_HASH->{$cdi_name}
				&&	defined	$CDI_HASH->{$cdi_name}
				&&	defined	$cs_name
				&&	length	$cs_name
				&&	defined	$cdi_bname
				&&	length	$cdi_bname
				&&	exists	$CDI_HASH->{$cdi_bname}
				&&	defined $CDI_HASH->{$cdi_bname}
				&&	defined	$cs_bname
				&&	length	$cs_bname
			){
				my $cdi_id = $CDI_HASH->{$cdi_name};
				my $cs_id = $CS_HASH->{$cs_name};
				my $cdi_bid = $CDI_HASH->{$cdi_bname};
				my $cs_bid = $CS_HASH->{$cs_bname};
				my $cds_bid = $BDS_HASH->{$cdi_bid}->{$cs_bid};

				if(defined $LOG){
					my $sth_sel = $dbh->prepare_cached('SELECT * FROM buildup_data_synonym WHERE cds_id=?');
					$sth_sel->execute($cds_bid);
					my $bds_data = $sth_sel->fetchrow_hashref;
					$sth_sel->finish;
					undef $sth_sel;
#					&cgi_lib::common::message($bds_data,$LOG);
					undef $bds_data;

					$sth_sel = $dbh->prepare_cached(qq|SELECT * FROM buildup_data_synonym WHERE md_id=? AND mv_id=? AND mr_id=? AND ci_id=? AND cb_id=? AND cdi_id=? AND cs_id=? AND cdst_id=$cdst_id|);
					$sth_sel->execute($params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'},$params->{'ci_id'},$params->{'cb_id'},$cdi_bid,$cs_bid);
					$bds_data = $sth_sel->fetchrow_hashref;
					$sth_sel->finish;
					undef $sth_sel;
#					&cgi_lib::common::message($bds_data,$LOG);
					undef $bds_data;
				}

				$sth_upd_bds_bid->execute($cds_bid,$params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'},$params->{'ci_id'},$params->{'cb_id'},$cdi_id,$cs_id) or die $dbh->errstr;
				$sth_upd_bds_bid->finish;

				$sth_upd_bds_added->execute($params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'},$params->{'ci_id'},$params->{'cb_id'},$cdi_bid,$cs_bid) or die $dbh->errstr;
				$sth_upd_bds_added->finish;
			}
		}
		undef $sth_upd_bds_added;
		undef $sth_upd_bds_bid;

		foreach my $p (@{$concept_data_synonym}){
			map { $p->{$_} = undef unless(defined $p->{$_} && length &trim($p->{$_})) } keys(%{$p});
			my $cdi_name = $p->{$KEYS->{'cdi_name'}};
			my $cs_name = $p->{$KEYS->{'cdi_syn_e'}};
			next unless(defined $cdi_name && length $cdi_name && exists $CDI_HASH->{$cdi_name} && defined $CDI_HASH->{$cdi_name});
			next unless(defined $cs_name && length $cs_name);

			my $cdi_id = $CDI_HASH->{$cdi_name};
			my $cs_id = $CS_HASH->{$cs_name};
			delete $BDS_HASH->{$cdi_id}->{$cs_id};
		}
		my $sth_del_bds = $dbh->prepare(qq|DELETE FROM buildup_data_synonym WHERE cds_id=?|) or die $dbh->errstr;
		foreach my $cdi_id (keys(%{$BDS_HASH})){
			foreach my $cs_id (keys(%{$BDS_HASH->{$cdi_id}})){
				$sth_del_bds->execute($BDS_HASH->{$cdi_id}->{$cs_id}) or die $dbh->errstr;
				$sth_del_bds->finish;
			}
		}
		undef $sth_del_bds;
	}
	&cgi_lib::common::message(sprintf("%f",&Time::HiRes::tv_interval($t)),$LOG) if(defined $LOG);


	#インポートしたconcept_tree情報をbuildup_treeテーブルへ反映
	if(defined $concept_tree && ref $concept_tree eq 'ARRAY' && scalar @$concept_tree){
		#concept_data_info
		my $cdi_id;
		my $cdi_name;
		my $CDI_HASH;
		my $sth_sel_cdi = $dbh->prepare_cached(qq|SELECT cdi_id,cdi_name FROM concept_data_info WHERE ci_id=?|) or die $dbh->errstr;
		$sth_sel_cdi->execute($params->{'ci_id'}) or die $dbh->errstr;
		$column_number = 0;
		$sth_sel_cdi->bind_col(++$column_number, \$cdi_id, undef);
		$sth_sel_cdi->bind_col(++$column_number, \$cdi_name, undef);
		while($sth_sel_cdi->fetch){
			$CDI_HASH->{$cdi_name} = $cdi_id - 0;
		}
		$sth_sel_cdi->finish;
		undef $sth_sel_cdi;

		#buildup_logic
		my $bul_id;
		my $bul_name_e;
		my $BUL_HASH;
		my $sth_sel_bul = $dbh->prepare_cached(qq|SELECT bul_id,bul_name_e FROM buildup_logic|) or die $dbh->errstr;
		$sth_sel_bul->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth_sel_bul->bind_col(++$column_number, \$bul_id, undef);
		$sth_sel_bul->bind_col(++$column_number, \$bul_name_e, undef);
		while($sth_sel_bul->fetch){
			$BUL_HASH->{$bul_name_e} = $bul_id - 0;
		}
		$sth_sel_bul->finish;
		undef $sth_sel_bul;

		#fma_partof_type
		my $f_potid;
		my $f_potname;
		my $FPT_HASH;
		my $sth_sel_fpt = $dbh->prepare(qq|SELECT f_potid,f_potname FROM fma_partof_type|) or die $dbh->errstr;
		$sth_sel_fpt->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth_sel_fpt->bind_col(++$column_number, \$f_potid, undef);
		$sth_sel_fpt->bind_col(++$column_number, \$f_potname, undef);
		while($sth_sel_fpt->fetch){
			$FPT_HASH->{$f_potname} = $f_potid - 0;
		}
		$sth_sel_fpt->finish;
		undef $sth_sel_fpt;

		#buildup_tree
		my $cdi_pid;
#		my $bul_id;
		my $f_potids;
		my $BT_HASH;
		my $sth_sel_bt = $dbh->prepare(qq|SELECT cdi_id,cdi_pid,bul_id,f_potids FROM buildup_tree WHERE md_id=? AND mv_id=? AND mr_id=? AND ci_id=? AND cb_id=? AND cdi_pid IS NOT NULL|) or die $dbh->errstr;
		$sth_sel_bt->execute($params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'},$params->{'ci_id'},$params->{'cb_id'}) or die $dbh->errstr;
		$column_number = 0;
		$sth_sel_bt->bind_col(++$column_number, \$cdi_id, undef);
		$sth_sel_bt->bind_col(++$column_number, \$cdi_pid, undef);
		$sth_sel_bt->bind_col(++$column_number, \$bul_id, undef);
		$sth_sel_bt->bind_col(++$column_number, \$f_potids, undef);
		while($sth_sel_bt->fetch){
			$BT_HASH->{$cdi_id}->{$cdi_pid}->{$bul_id} = $f_potids;
		}
		$sth_sel_bt->finish;
		undef $sth_sel_bt;

		my $sth_ins_bt = $dbh->prepare(qq|INSERT INTO buildup_tree (md_id,mv_id,mr_id,ci_id,cb_id,cdi_id,cdi_pid,bul_id,f_potids) VALUES (?,?,?,?,?,?,?,?,?)|) or die $dbh->errstr;
		my $sth_upd_bt = $dbh->prepare(qq|UPDATE buildup_tree SET f_potids=? WHERE md_id=? AND mv_id=? AND mr_id=? AND ci_id=? AND cb_id=? AND cdi_id=? AND cdi_pid=? AND bul_id=?|) or die $dbh->errstr;

		foreach my $p (@{$concept_tree}){
			map { $p->{$_} = undef unless(defined $p->{$_} && length &trim($p->{$_})) } keys(%{$p});
			my $cdi_name = $p->{$KEYS->{'cdi_name'}};
			my $cdi_pname = $p->{$KEYS->{'cdi_pname'}};
			my $bul_name_e = $p->{$KEYS->{'concept_relation_logic'}};
			my $f_potnames = $p->{$KEYS->{'concept_relation_types'}};
			my $cdi_id;
			my $cdi_pid;
			my $bul_id;
			my $f_potids;
			if(defined $CDI_HASH && ref $CDI_HASH eq 'HASH'){
				$cdi_id = $CDI_HASH->{$cdi_name} if(defined $cdi_name && length $cdi_name && exists $CDI_HASH->{$cdi_name} && defined $CDI_HASH->{$cdi_name});
				$cdi_pid = $CDI_HASH->{$cdi_pname} if(defined $cdi_pname && length $cdi_pname && exists $CDI_HASH->{$cdi_pname} && defined $CDI_HASH->{$cdi_pname});
			}
			if(defined $bul_name_e && length $bul_name_e && defined $BUL_HASH && ref $BUL_HASH eq 'HASH' && exists $BUL_HASH->{$bul_name_e} && defined $BUL_HASH->{$bul_name_e}){
				$bul_id = $BUL_HASH->{$bul_name_e};
			}
			if(defined $f_potnames && length $f_potnames && defined $FPT_HASH && ref $FPT_HASH eq 'HASH'){
				$f_potids =  join(';', sort {$a <=> $b} map {$FPT_HASH->{$_}} grep {exists $FPT_HASH->{$_}} split(/;/,$f_potnames));
				$f_potids = undef unless(defined $f_potids && length $f_potids);
			}

			if(		defined $BT_HASH
				&&	ref			$BT_HASH eq 'HASH'
				&&	exists	$BT_HASH->{$cdi_id}
				&&	defined	$BT_HASH->{$cdi_id}
				&&	ref			$BT_HASH->{$cdi_id} eq 'HASH'
				&&	exists	$BT_HASH->{$cdi_id}->{$cdi_pid}
				&&	defined	$BT_HASH->{$cdi_id}->{$cdi_pid}
				&&	ref			$BT_HASH->{$cdi_id}->{$cdi_pid} eq 'HASH'
				&&	exists	$BT_HASH->{$cdi_id}->{$cdi_pid}->{$bul_id}
			){
				$sth_upd_bt->execute(
					 $f_potids
					,$params->{'md_id'}
					,$params->{'mv_id'}
					,$params->{'mr_id'}
					,$params->{'ci_id'}
					,$params->{'cb_id'}
					,$cdi_id
					,$cdi_pid
					,$bul_id
				) or die $dbh->errstr;
				$sth_upd_bt->finish;

				delete $BT_HASH->{$cdi_id}->{$cdi_pid}->{$bul_id};
			}
			else{
				$sth_ins_bt->execute(
					 $params->{'md_id'}
					,$params->{'mv_id'}
					,$params->{'mr_id'}
					,$params->{'ci_id'}
					,$params->{'cb_id'}
					,$cdi_id
					,$cdi_pid
					,$bul_id
					,$f_potids
				) or die $dbh->errstr;
				$sth_ins_bt->finish;
			}
		}
		undef $sth_ins_bt;
		undef $sth_upd_bt;

		if(defined $BT_HASH && ref $BT_HASH eq 'HASH'){
			my $sth_del_bt = $dbh->prepare(qq|DELETE FROM buildup_tree WHERE md_id=? AND mv_id=? AND mr_id=? AND ci_id=? AND cb_id=? AND cdi_id=? AND cdi_pid=? AND bul_id=?|) or die $dbh->errstr;
			foreach my $cdi_id (keys(%{$BT_HASH})){
				foreach my $cdi_pid (keys(%{$BT_HASH->{$cdi_id}})){
					foreach my $bul_id (keys(%{$BT_HASH->{$cdi_id}->{$cdi_pid}})){
						$sth_del_bt->execute(
							 $params->{'md_id'}
							,$params->{'mv_id'}
							,$params->{'mr_id'}
							,$params->{'ci_id'}
							,$params->{'cb_id'}
							,$cdi_id
							,$cdi_pid
							,$bul_id
						) or die $dbh->errstr;
						$sth_del_bt->finish;
					}
				}
			}
			undef $sth_del_bt;
		}

 	}
	&cgi_lib::common::message(sprintf("%f",&Time::HiRes::tv_interval($t)),$LOG) if(defined $LOG);

	#インポートしたconcept_tree_info情報をbuildup_tree_infoテーブルへ反映
	if(defined $concept_tree_info && ref $concept_tree_info eq 'ARRAY' && scalar @$concept_tree_info){
		#concept_data_info
		my $cdi_id;
		my $cdi_name;
		my $CDI_HASH;
		my $sth_sel_cdi = $dbh->prepare_cached(qq|SELECT cdi_id,cdi_name FROM concept_data_info WHERE ci_id=?|) or die $dbh->errstr;
		$sth_sel_cdi->execute($params->{'ci_id'}) or die $dbh->errstr;
		$column_number = 0;
		$sth_sel_cdi->bind_col(++$column_number, \$cdi_id, undef);
		$sth_sel_cdi->bind_col(++$column_number, \$cdi_name, undef);
		while($sth_sel_cdi->fetch){
			$CDI_HASH->{$cdi_name} = $cdi_id - 0;
		}
		$sth_sel_cdi->finish;
		undef $sth_sel_cdi;

		#buildup_logic
		my $bul_id;
		my $bul_name_e;
		my $BUL_HASH;
		my $sth_sel_bul = $dbh->prepare_cached(qq|SELECT bul_id,bul_name_e FROM buildup_logic|) or die $dbh->errstr;
		$sth_sel_bul->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth_sel_bul->bind_col(++$column_number, \$bul_id, undef);
		$sth_sel_bul->bind_col(++$column_number, \$bul_name_e, undef);
		while($sth_sel_bul->fetch){
			$BUL_HASH->{$bul_name_e} = $bul_id - 0;
		}
		$sth_sel_bul->finish;
		undef $sth_sel_bul;

		#buildup_tree_info
#		my $bul_id;
		my $BTI_HASH;
		my $sth_sel_bti = $dbh->prepare(qq|SELECT cdi_id,bul_id FROM buildup_tree_info WHERE md_id=? AND mv_id=? AND mr_id=? AND ci_id=? AND cb_id=?|) or die $dbh->errstr;
		$sth_sel_bti->execute($params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'},$params->{'ci_id'},$params->{'cb_id'}) or die $dbh->errstr;
		$column_number = 0;
		$sth_sel_bti->bind_col(++$column_number, \$cdi_id, undef);
		$sth_sel_bti->bind_col(++$column_number, \$bul_id, undef);
		while($sth_sel_bti->fetch){
			$BTI_HASH->{$cdi_id}->{$bul_id} = undef;
		}
		$sth_sel_bti->finish;
		undef $sth_sel_bti;

		my $sth_ins_bti = $dbh->prepare(qq|INSERT INTO buildup_tree_info (md_id,mv_id,mr_id,ci_id,cb_id,cdi_id,but_cnum,but_cids,but_depth,but_pnum,but_pids,bul_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)|) or die $dbh->errstr;
		my $sth_upd_bti = $dbh->prepare(qq|UPDATE buildup_tree_info SET but_cnum=?,but_cids=?,but_depth=?,but_pnum=?,but_pids=? WHERE md_id=? AND mv_id=? AND mr_id=? AND ci_id=? AND cb_id=? AND cdi_id=? AND bul_id=?|) or die $dbh->errstr;

		foreach my $p (@{$concept_tree_info}){
			map { $p->{$_} = undef unless(defined $p->{$_} && length &trim($p->{$_})) } keys(%{$p});
			my $cdi_name   = $p->{$KEYS->{'cdi_name'}};
			my $cti_cnames = $p->{$KEYS->{'cti_cnames'}};
			my $cti_pnames = $p->{$KEYS->{'cti_pnames'}};
			my $cti_depth  = $p->{$KEYS->{'cti_depth'}};
			my $bul_name_e = $p->{$KEYS->{'concept_relation_logic'}};
			my $cdi_id;
			my $but_cnum = 0;
			my $but_cids;
			my $but_depth = defined $cti_depth ? $cti_depth - 0 : 0;
			my $but_pnum = 0;
			my $but_pids;
			my $bul_id;

			if(
						defined	$CDI_HASH
				&&	ref			$CDI_HASH eq 'HASH'
				&&	defined	$cdi_name
				&&	length	$cdi_name
				&&	exists	$CDI_HASH->{$cdi_name}
				&&	defined	$CDI_HASH->{$cdi_name}
			){
				$cdi_id = $CDI_HASH->{$cdi_name};
			}
			if(
						defined	$bul_name_e
				&&	length	$bul_name_e
				&&	defined	$BUL_HASH
				&&	ref			$BUL_HASH eq 'HASH'
				&&	exists	$BUL_HASH->{$bul_name_e}
				&&	defined	$BUL_HASH->{$bul_name_e}
			){
				$bul_id = $BUL_HASH->{$bul_name_e};
			}

			if(defined	$CDI_HASH && ref $CDI_HASH eq 'HASH'){
				if(defined $cti_cnames && length $cti_cnames){
					my $cti_cnames_arr = &cgi_lib::common::decodeJSON($cti_cnames);
					if(defined $cti_cnames_arr && ref $cti_cnames_arr eq 'ARRAY' && scalar @{$cti_cnames_arr}){
						my $temp_arr = [sort {$a<=>$b} map {$CDI_HASH->{$_}} grep {exists $CDI_HASH->{$_}} @{$cti_cnames_arr}];
						if(defined $temp_arr && ref $temp_arr eq 'ARRAY' && scalar @{$temp_arr}){
							$but_cids = &cgi_lib::common::encodeJSON($temp_arr);
							$but_cnum = scalar @{$temp_arr};
						}
					}
				}
				if(defined $cti_pnames && length $cti_pnames){
					my $cti_pnames_arr = &cgi_lib::common::decodeJSON($cti_pnames);
					if(defined $cti_pnames_arr && ref $cti_pnames_arr eq 'ARRAY' && scalar @{$cti_pnames_arr}){
						my $temp_arr = [sort {$a<=>$b} map {$CDI_HASH->{$_}} grep {exists $CDI_HASH->{$_}} @{$cti_pnames_arr}];
						if(defined $temp_arr && ref $temp_arr eq 'ARRAY' && scalar @{$temp_arr}){
							$but_pids = &cgi_lib::common::encodeJSON($temp_arr);
							$but_pnum = scalar @{$temp_arr};
						}
					}
				}
			}

			if(		defined $BTI_HASH
				&&	ref			$BTI_HASH eq 'HASH'
				&&	exists	$BTI_HASH->{$cdi_id}
				&&	defined	$BTI_HASH->{$cdi_id}
				&&	ref			$BTI_HASH->{$cdi_id} eq 'HASH'
				&&	exists	$BTI_HASH->{$cdi_id}->{$bul_id}
			){
				$sth_upd_bti->execute(
					 $but_cnum
					,$but_cids
					,$but_depth
					,$but_pnum
					,$but_pids
					,$params->{'md_id'}
					,$params->{'mv_id'}
					,$params->{'mr_id'}
					,$params->{'ci_id'}
					,$params->{'cb_id'}
					,$cdi_id
					,$bul_id
				) or die $dbh->errstr;
				$sth_upd_bti->finish;

				delete $BTI_HASH->{$cdi_id}->{$bul_id};
			}
			else{
				$sth_ins_bti->execute(
					 $params->{'md_id'}
					,$params->{'mv_id'}
					,$params->{'mr_id'}
					,$params->{'ci_id'}
					,$params->{'cb_id'}
					,$cdi_id
					,$but_cnum
					,$but_cids
					,$but_depth
					,$but_pnum
					,$but_pids
					,$bul_id
				) or die $dbh->errstr;
				$sth_ins_bti->finish;
			}
		}
		undef $sth_ins_bti;
		undef $sth_upd_bti;

		if(defined $BTI_HASH && ref $BTI_HASH eq 'HASH'){
			my $sth_del_bti = $dbh->prepare(qq|DELETE FROM buildup_tree_info WHERE md_id=? AND mv_id=? AND mr_id=? AND ci_id=? AND cb_id=? AND cdi_id=? AND bul_id=?|) or die $dbh->errstr;
			foreach my $cdi_id (keys(%{$BTI_HASH})){
				foreach my $bul_id (keys(%{$BTI_HASH->{$cdi_id}})){
					$sth_del_bti->execute(
						 $params->{'md_id'}
						,$params->{'mv_id'}
						,$params->{'mr_id'}
						,$params->{'ci_id'}
						,$params->{'cb_id'}
						,$cdi_id
						,$bul_id
					) or die $dbh->errstr;
					$sth_del_bti->finish;
				}
			}
			undef $sth_del_bti;
		}
 	}
	&cgi_lib::common::message(sprintf("%f",&Time::HiRes::tv_interval($t)),$LOG) if(defined $LOG);

#die 'DEBUG';

	my $sth_id_prefix = $dbh->prepare(qq|SELECT prefix_id FROM id_prefix WHERE prefix_char=?|) or die $dbh->errstr;
	my $sth_art_file = $dbh->prepare(qq|SELECT art_id,art_serial FROM history_art_file WHERE md5(art_data)=md5(?) AND art_data=? AND prefix_id=? ORDER BY art_serial DESC,hist_serial DESC|) or die $dbh->errstr;

	my $sql_art_sel =<<SQL;
select
 prefix_id,
 art_serial,
 art_name,
 art_ext,
 art_timestamp
from
 art_file
where art_id=?
SQL
	my $sth_art_sel = $dbh->prepare($sql_art_sel) or die $dbh->errstr;

	my $sql_art_mirror_ins =<<SQL;
INSERT INTO art_file (
  prefix_id,
  art_id,
  art_serial,
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
  art_cube_volume,
  art_nsn,
  art_mirroring,
  art_entry,
  art_decimate,
  art_decimate_size,
  artg_id,
  artl_id,
  artc_id,
  art_openid
) VALUES (
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
  ?,
  ?,
  ?,
  'system'
)
;
SQL
	my $sth_art_mirror_ins = $dbh->prepare($sql_art_mirror_ins) or die $dbh->errstr;
	my $sth_art_ins = $dbh->prepare($sql_art_mirror_ins) or die $dbh->errstr;

	my $sth_art_upd2 = $dbh->prepare('UPDATE art_file SET art_delcause=NULL WHERE art_delcause IS NOT NULL AND art_id=?') or die $dbh->errstr;


	my $sth_art_upd_artc = $dbh->prepare('UPDATE art_file SET artl_id=?,artc_id=? WHERE art_id=?') or die $dbh->errstr;
	my $sth_arti_upd_artc = $dbh->prepare('UPDATE art_file_info SET artl_id=?,artc_id=? WHERE art_id=?') or die $dbh->errstr;


	my $sql_insert_art_file_info =<<SQL;
INSERT INTO
 art_file_info
 (
 art_id,
 art_name,
 art_ext,
 art_timestamp,
 art_nsn,
 art_mirroring,
 artg_id,
 artl_id,
 artc_id,
 art_entry,
 art_openid
 )
SELECT
 art_id,
 art_name,
 art_ext,
 art_timestamp,
 art_nsn,
 art_mirroring,
 artg_id,
 artl_id,
 artc_id,
 art_entry,
 art_openid
FROM
 art_file
WHERE
 art_id IN (SELECT art_id FROM art_file WHERE art_delcause is NULL AND art_id NOT IN (SELECT art_id FROM art_file_info))
SQL

	my $sql_update_art_file_info =<<SQL;
UPDATE ONLY
 art_file_info
SET
 art_nsn = art_file.art_nsn,
 art_mirroring = art_file.art_mirroring
FROM
 art_file
WHERE
 art_file_info.art_id = art_file.art_id AND art_file.art_delcause IS NULL;
SQL

	$dbh->do(qq|DROP TRIGGER IF EXISTS trig_before_art_file ON art_file CASCADE|) or die $dbh->errstr;
	$dbh->do(qq|DROP TRIGGER IF EXISTS trig_after_art_file ON art_file CASCADE|) or die $dbh->errstr;
	$dbh->do(qq|UPDATE art_file SET artg_id=arti.artg_id FROM (SELECT art_id,artg_id FROM art_file_info) AS arti WHERE art_file.art_id=arti.art_id AND art_file.artg_id<>arti.artg_id|) or die $dbh->errstr;
#update art_file set artg_id=4249 WHERE art_id='MM533';

	$dbh->do(qq|
CREATE TRIGGER trig_before_art_file
    BEFORE INSERT OR DELETE OR UPDATE ON art_file
    FOR EACH ROW
    EXECUTE PROCEDURE func_before_art_file();
|) or die $dbh->errstr;

	$dbh->do(qq|
CREATE TRIGGER trig_after_art_file
    AFTER INSERT OR DELETE OR UPDATE ON art_file
    FOR EACH ROW
    EXECUTE PROCEDURE func_after_art_file();
|) or die $dbh->errstr;


	$dbh->do(qq|SELECT pg_catalog.setval('art_folder_artf_id_seq',(SELECT max(artf_id) FROM art_folder))|) or die $dbh->errstr;

	my $sth_artf_sel = $dbh->prepare(qq|SELECT artf_id FROM art_folder WHERE COALESCE(artf_pid,0)=COALESCE(?,0) AND artf_name=?|) or die $dbh->errstr;
	my $sth_artf_ins = $dbh->prepare(qq|INSERT INTO art_folder (artf_pid,artf_name,artf_timestamp,artf_use) VALUES (?,?,now(),true) RETURNING artf_id|) or die $dbh->errstr;
	my $sth_artf_upd = $dbh->prepare(qq|UPDATE art_folder set artf_use=true,artf_delcause=null WHERE artf_id=?|) or die $dbh->errstr;

	my $sth_artg_sel = $dbh->prepare(qq|SELECT artg_id FROM art_group WHERE artg_name=?|) or die $dbh->errstr;
	my $sth_artg_ins = $dbh->prepare(qq|INSERT INTO art_group (artg_name,artf_id,artg_timestamp,atrg_use,artg_openid) VALUES (?,?,now(),true,'system') RETURNING artg_id|) or die $dbh->errstr;
	my $sth_artg_upd = $dbh->prepare(qq|UPDATE art_group set atrg_use=true,artg_delcause=null WHERE artg_id=?|) or die $dbh->errstr;
	my $sth_artg_sel_art_id = $dbh->prepare(qq|SELECT artg_id FROM art_file WHERE art_id=?|) or die $dbh->errstr;

	my $sql_cm_sel = qq|SELECT * FROM concept_art_map WHERE ci_id=? AND cb_id=? AND md_id=? AND mv_id=? AND mr_id=? AND art_id=?|;
	my $sth_cm_sel = $dbh->prepare($sql_cm_sel) or die $dbh->errstr;

	my $sql_cm_del = qq|DELETE FROM concept_art_map WHERE ci_id=? AND cb_id=? AND md_id=? AND mv_id=? AND mr_id=? AND art_id=?|;
	my $sth_cm_del = $dbh->prepare($sql_cm_del) or die $dbh->errstr;

	my $sql_cm_upd = qq|UPDATE concept_art_map set cm_use=true,cm_delcause=null,cm_entry=now(),cdi_id=?,cmp_id=? WHERE ci_id=? AND cb_id=? AND md_id=? AND mv_id=? AND mr_id=? AND art_id=?|;
	my $sth_cm_upd = $dbh->prepare($sql_cm_upd) or die $dbh->errstr;

	my $sql_cm_ins = qq|INSERT INTO concept_art_map (ci_id,cb_id,md_id,mv_id,mr_id,art_id,cdi_id,cmp_id,cm_use,cm_entry,cm_openid) VALUES (?,?,?,?,?,?,?,?,true,now(),'system')|;
	my $sth_cm_ins = $dbh->prepare($sql_cm_ins) or die $dbh->errstr;

	my $sth_cm_ins2 = $dbh->prepare(qq|INSERT INTO concept_art_map (ci_id,cb_id,md_id,mv_id,mr_id,art_id,cdi_id,cmp_id,cm_id,cm_serial,cm_use,cm_entry,cm_openid) VALUES (?,?,?,?,?,?,?,?,?,?,true,now(),'system')|) or die $dbh->errstr;

	my $sth_cm_max_sel = $dbh->prepare(qq|SELECT COALESCE(MAX(cm_serial),0) FROM concept_art_map|) or die $dbh->errstr;
	my $sth_hcm_max_sel = $dbh->prepare(qq|SELECT COALESCE(MAX(cm_serial),0) FROM history_concept_art_map|) or die $dbh->errstr;
	my $sth_id_prefix_sel = $dbh->prepare(qq|SELECT prefix_char FROM id_prefix WHERE prefix_id=?|) or die $dbh->errstr;
	my $cm_prefix_char;
	$sth_id_prefix_sel->execute(3) or die $dbh->errstr;
	$sth_id_prefix_sel->bind_col(1, \$cm_prefix_char, undef);
	$sth_id_prefix_sel->fetch;
	$sth_id_prefix_sel->finish();
	undef $sth_id_prefix_sel;

	my $sth_hcm_sel = $dbh->prepare(qq|SELECT cm_id,cm_serial FROM history_concept_art_map WHERE ci_id=? AND cb_id=? AND md_id=? AND mv_id=? AND mr_id<=? AND art_id=? ORDER BY cm_serial limit 1|) or die $dbh->errstr;
	my $sth_hmap_upd = $dbh->prepare(qq|UPDATE history_concept_art_map SET hist_timestamp=cm_entry WHERE ci_id=? AND cb_id=? AND md_id=? AND mv_id=? AND mr_id=? AND hist_event IN (SELECT he_id FROM history_event WHERE he_delcause IS NULL AND he_name IN ('INSERT','UPDATE'))|) or die $dbh->errstr;

	my $sql_cdi_sel = qq|SELECT cdi_id FROM concept_data_info WHERE ci_id=? AND cdi_name=?|;
	my $sth_cdi_sel = $dbh->prepare($sql_cdi_sel) or die $dbh->errstr;

	my $sql_cd_sel = qq|SELECT cdi_id FROM concept_data WHERE ci_id=? AND cb_id=? AND cdi_id=?|;
	my $sth_cd_sel = $dbh->prepare($sql_cd_sel) or die $dbh->errstr;

	my $sql_bd_sel = qq|SELECT cdi_id FROM buildup_data WHERE md_id=? AND mv_id=? AND mr_id=? AND ci_id=? AND cb_id=? AND cdi_id=?|;
	my $sth_bd_sel = $dbh->prepare($sql_bd_sel) or die $dbh->errstr;

	my $sth_arta_sel = $dbh->prepare(qq|SELECT * FROM art_annotation WHERE art_id=?|) or die $dbh->errstr;
	my $sth_arta_del = $dbh->prepare(qq|DELETE FROM art_annotation WHERE art_id=?|) or die $dbh->errstr;
	my $sql_arta_ins = qq|INSERT INTO art_annotation (art_entry,art_openid,art_comment,art_category,art_judge,art_class,art_id) VALUES (now(),'system',?,?,?,?,?)|;
	my $sth_arta_ins = $dbh->prepare($sql_arta_ins) or die $dbh->errstr;
	my $sql_arta_upd = qq|UPDATE art_annotation set art_entry=now(),art_openid='system',art_comment=?,art_category=?,art_judge=?,art_class=? WHERE art_id=?|;
	my $sth_arta_upd = $dbh->prepare($sql_arta_upd) or die $dbh->errstr;

	my $sth_arto_sel = $dbh->prepare(qq|SELECT * FROM art_org_info WHERE art_id=?|) or die $dbh->errstr;
	my $sth_arto_del = $dbh->prepare(qq|DELETE FROM art_org_info WHERE art_id=?|) or die $dbh->errstr;
	my $sql_arto_ins = qq|INSERT INTO art_org_info (arto_entry,arto_openid,arto_id,arto_comment,art_id) VALUES (now(),'system',?,?,?)|;
	my $sth_arto_ins = $dbh->prepare($sql_arto_ins) or die $dbh->errstr;
	my $sql_arto_upd = qq|UPDATE art_org_info set arto_entry=now(),arto_openid='system',arto_id=?,arto_comment=? WHERE art_id=?|;
	my $sth_arto_upd = $dbh->prepare($sql_arto_upd) or die $dbh->errstr;

	my $sql_cdi_sel_all = qq|SELECT cdi_id,cdi_name FROM concept_data_info WHERE ci_id=?|;
	my $sth_cdi_sel_all = $dbh->prepare($sql_cdi_sel_all) or die $dbh->errstr;
	my $cdi_id;
	my $cdi_name;
	my %CDI_NAME;
	$sth_cdi_sel_all->execute($params->{'ci_id'}) or die $dbh->errstr;
	$sth_cdi_sel_all->bind_col(1, \$cdi_id, undef);
	$sth_cdi_sel_all->bind_col(2, \$cdi_name, undef);
	while($sth_cdi_sel_all->fetch){
		next unless(defined $cdi_id && defined $cdi_name);
		$CDI_NAME{$cdi_name} = $cdi_id - 0;
	}
	$sth_cdi_sel_all->finish();
	undef $sth_cdi_sel_all;

	my $sql_cmp_sel_all = qq|SELECT cmp_id,cmp_title,cmp_abbr FROM concept_art_map_part WHERE md_id=? AND mv_id=? AND mr_id=? AND cmp_use AND cmp_delcause IS NULL|;
	my $sth_cmp_sel_all = $dbh->prepare($sql_cmp_sel_all) or die $dbh->errstr;
	my $cmp_id;
	my $cmp_title;
	my $cmp_abbr;
	my %CMP_ABBR_ID;
	my %CMP_TITLE_ID;
	$sth_cmp_sel_all->execute($params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'}) or die $dbh->errstr;
	&cgi_lib::common::message($sth_cmp_sel_all->rows(),$LOG) if(defined $LOG);
	$column_number = 0;
	$sth_cmp_sel_all->bind_col(++$column_number, \$cmp_id, undef);
	$sth_cmp_sel_all->bind_col(++$column_number, \$cmp_title, undef);
	$sth_cmp_sel_all->bind_col(++$column_number, \$cmp_abbr, undef);
	while($sth_cmp_sel_all->fetch){
		next unless(defined $cmp_id);
		$CMP_ABBR_ID{$cmp_abbr} = $cmp_id - 0 if(defined $cmp_abbr);
		$CMP_TITLE_ID{$cmp_title} = $cmp_id - 0 if(defined $cmp_title);
	}
	$sth_cmp_sel_all->finish();
	undef $sth_cmp_sel_all;

#	if(defined $LOG){
#		&cgi_lib::common::message(\%CMP_TITLE_ID,$LOG);
#		&cgi_lib::common::message(\%CMP_ABBR_ID,$LOG);
##		die __LINE__;
#	}

	my $sql_bcp_sel_all = qq|SELECT bcp_id,bcp_title,bcp_abbr FROM buildup_concept_part WHERE md_id=? AND mv_id=? AND mr_id=? AND bcp_use AND bcp_delcause IS NULL|;
	my $sth_bcp_sel_all = $dbh->prepare($sql_bcp_sel_all) or die $dbh->errstr;
	my $bcp_id;
	my $bcp_title;
	my $bcp_abbr;
	my %BCP_ABBR_ID;
	my %BCP_TITLE_ID;
	$sth_bcp_sel_all->execute($params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'}) or die $dbh->errstr;
	&cgi_lib::common::message($sth_bcp_sel_all->rows(),$LOG) if(defined $LOG);
	if($sth_bcp_sel_all->rows()>0){
		$column_number = 0;
		$sth_bcp_sel_all->bind_col(++$column_number, \$bcp_id, undef);
		$sth_bcp_sel_all->bind_col(++$column_number, \$bcp_title, undef);
		$sth_bcp_sel_all->bind_col(++$column_number, \$bcp_abbr, undef);
		while($sth_bcp_sel_all->fetch){
			next unless(defined $bcp_id);
			$BCP_ABBR_ID{$bcp_abbr} = $bcp_id - 0 if(defined $bcp_abbr);
			$BCP_TITLE_ID{$bcp_title} = $bcp_id - 0 if(defined $bcp_title);
		}
	}
	$sth_bcp_sel_all->finish();
	undef $sth_bcp_sel_all;

#	if(defined $LOG){
#		&cgi_lib::common::message(\%BCP_TITLE_ID,$LOG);
#		&cgi_lib::common::message(\%BCP_ABBR_ID,$LOG);
##		die __LINE__;
#	}
	&cgi_lib::common::message(sprintf("%f",&Time::HiRes::tv_interval($t)),$LOG) if(defined $LOG);

	my $sql_bcl_sel_all = qq|SELECT bcl_id,bcl_title,bcl_abbr FROM buildup_concept_laterality WHERE md_id=? AND mv_id=? AND mr_id=? AND bcl_use AND bcl_delcause IS NULL|;
	my $sth_bcl_sel_all = $dbh->prepare($sql_bcl_sel_all) or die $dbh->errstr;
	my $bcl_id;
	my $bcl_title;
	my $bcl_abbr;
	my %BCL_ABBR_ID;
	my %BCL_TITLE_ID;
	$sth_bcl_sel_all->execute($params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'}) or die $dbh->errstr;
	&cgi_lib::common::message($sth_bcl_sel_all->rows(),$LOG) if(defined $LOG);
	if($sth_bcl_sel_all->rows()>0){
		$column_number = 0;
		$sth_bcl_sel_all->bind_col(++$column_number, \$bcl_id, undef);
		$sth_bcl_sel_all->bind_col(++$column_number, \$bcl_title, undef);
		$sth_bcl_sel_all->bind_col(++$column_number, \$bcl_abbr, undef);
		while($sth_bcl_sel_all->fetch){
			next unless(defined $bcl_id);
			$BCL_ABBR_ID{$bcl_abbr} = $bcl_id - 0 if(defined $bcl_abbr);
			$BCL_TITLE_ID{$bcl_title} = $bcl_id - 0 if(defined $bcl_title);
		}
	}
	$sth_bcl_sel_all->finish();
	undef $sth_bcl_sel_all;

#	if(defined $LOG){
#		&cgi_lib::common::message(\%BCL_TITLE_ID,$LOG);
#		&cgi_lib::common::message(\%BCL_ABBR_ID,$LOG);
##		die __LINE__;
#	}
	&cgi_lib::common::message(sprintf("%f",&Time::HiRes::tv_interval($t)),$LOG) if(defined $LOG);

	my $sql_artl_sel_all = qq|SELECT artl_id,artl_title,artl_abbr FROM art_laterality WHERE artl_use AND artl_delcause IS NULL|;
	my $sth_artl_sel_all = $dbh->prepare($sql_artl_sel_all) or die $dbh->errstr;
	my $artl_id;
	my $artl_title;
	my $artl_abbr;
	my %ARTL_ABBR_ID;
	my %ARTL_TITLE_ID;
	$sth_artl_sel_all->execute() or die $dbh->errstr;
	&cgi_lib::common::message($sth_artl_sel_all->rows(),$LOG) if(defined $LOG);
	$column_number = 0;
	$sth_artl_sel_all->bind_col(++$column_number, \$artl_id, undef);
	$sth_artl_sel_all->bind_col(++$column_number, \$artl_title, undef);
	$sth_artl_sel_all->bind_col(++$column_number, \$artl_abbr, undef);
	while($sth_artl_sel_all->fetch){
		next unless(defined $artl_id);
		$ARTL_ABBR_ID{$artl_abbr} = $artl_id - 0 if(defined $artl_abbr);
		$ARTL_TITLE_ID{$artl_title} = $artl_id - 0 if(defined $artl_title);
	}
	$sth_artl_sel_all->finish();
	undef $sth_artl_sel_all;

#	if(defined $LOG){
#		&cgi_lib::common::message(\%ARTL_TITLE_ID,$LOG);
#		&cgi_lib::common::message(\%ARTL_ABBR_ID,$LOG);
##		die __LINE__;
#	}
	&cgi_lib::common::message(sprintf("%f",&Time::HiRes::tv_interval($t)),$LOG) if(defined $LOG);

	my $sql_cm_sel_all = qq|SELECT art_id,cdi_id FROM concept_art_map WHERE (ci_id,cb_id,md_id,mv_id,mr_id,art_id) IN (SELECT ci_id,cb_id,md_id,mv_id,max(mr_id),art_id FROM concept_art_map WHERE ci_id=? AND cb_id=? AND md_id=? AND mv_id=? AND mr_id<=? GROUP BY ci_id,cb_id,md_id,mv_id,art_id)|;
	my $sth_cm_sel_all = $dbh->prepare($sql_cm_sel_all) or die $dbh->errstr;
	my $art_id;
	my %MAPPED_ART_ID;
	my %USE_CDI_ID;
	$sth_cm_sel_all->execute($params->{'ci_id'},$params->{'cb_id'},$params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'}) or die $dbh->errstr;
	$sth_cm_sel_all->bind_col(1, \$art_id, undef);
	$sth_cm_sel_all->bind_col(2, \$cdi_id, undef);
	while($sth_cm_sel_all->fetch){
		$MAPPED_ART_ID{$art_id} = 0 if(defined $art_id);
#		$USE_CDI_ID{$cdi_id} = undef if(defined $cdi_id);
	}
	$sth_cm_sel_all->finish();
	undef $sth_cm_sel_all;

	&cgi_lib::common::message('['.(scalar @$datas).']',$LOG) if(defined $LOG);
	my $data_pos = 0;

	umask(0);
	my $art_path = &catdir($FindBin::Bin,'..','art_file');
	&File::Path::mkpath($art_path,{mode=>0777}) unless(-e $art_path);

	$RTN->{'messages'} = [];

	my %art_id_2_hash;
	my $header;
	my $total = scalar @$datas;
	foreach my $data (@$datas){
		$data_pos++;
#		&cgi_lib::common::message(sprintf('[%05d/%05d]',$data_pos,$total),$LOG);
#		$RTN->{'progress'} = {
#			'value' => $data_pos/scalar @$datas,
#			'msg' => &cgi_lib::common::decodeUTF8(qq|[$data_pos/$total]|)
#		};
#		&_writeProgress();

		$data = &trim($data);
		next unless(defined $data);
		if(index($data,'#') == 0){
			undef $header;
			$header = &get_header($data);
#	my $header = qq|#FJID	BPID	Use_Map	FMA_ID	FMA_Name	FMA_Synonym	OBJ_Filename	OBJ_Group	OBJ_Timestamp	Comment	Category	Judge	Class|;
			undef $header unless(defined $header && exists $header->{$KEYS->{'art_id'}} && (exists $header->{$KEYS->{'cdi_name'}} || exists $header->{$KEYS->{'art_comment'}} || exists $header->{$KEYS->{'art_category'}} || exists $header->{$KEYS->{'art_judge'}} || exists $header->{$KEYS->{'art_class'}}));
			&cgi_lib::common::message($header,,$LOG) if(defined $LOG && defined $header)
		}elsif(defined $header){
			my $hash = &set_data2hash($header,$data);
			unless(defined $hash && exists $hash->{$KEYS->{'art_id'}} && defined $hash->{$KEYS->{'art_id'}}){
				undef $hash;
				next;
			}
			$art_id_2_hash{$hash->{$KEYS->{'art_id'}}} = $hash;
			next;
		}
	}
	unless(defined $header){
		&cgi_lib::common::message('header無し',$LOG) if(defined $LOG);
		$RTN->{'progress'} = {
			'value' => 1,
			'msg' => &cgi_lib::common::decodeUTF8(qq|[1]|)
		};
		&cgi_lib::common::writeFileJSON($params_file,$RTN);
		return;
	}
	&cgi_lib::common::message(sprintf("%f",&Time::HiRes::tv_interval($t)),$LOG) if(defined $LOG);

	#既存のOBJと同じかの確認
	$data_pos = 0;
	$total = (scalar keys %art_id_2_hash)*2;
	my $exec_ins = 0;
	foreach my $hash_art_id (sort {$a cmp $b} keys %art_id_2_hash){
		my $hash = $art_id_2_hash{$hash_art_id};
		$data_pos++;
#		&cgi_lib::common::message(sprintf('[%05d/%05d] %s',$data_pos,$total,$hash_art_id),$LOG) if(defined $LOG);
		$RTN->{'progress'} = {
			'value' => $data_pos/$total,
			'msg' => &cgi_lib::common::decodeUTF8(qq|[$data_pos/$total] $hash_art_id|)
		};
		&_writeProgress();

		my $art_mirroring = 0;
		my $org_art_id;
		my $mir_art_id;
		if($hash_art_id =~ /^([A-Z]+[0-9]+)M$/){
			$org_art_id = $1;
			$mir_art_id = $hash_art_id;
			$art_mirroring = 1;
		}else{
			$org_art_id = $hash_art_id;
			$mir_art_id = $hash_art_id.'M';
		}

		my $artl_title;
		my $artl_id = 0;
		if(exists $KEYS->{'artl_title'} && defined $KEYS->{'artl_title'} && length $KEYS->{'artl_title'} && exists $hash->{$KEYS->{'artl_title'}} && defined $hash->{$KEYS->{'artl_title'}}){
			$artl_title = $hash->{$KEYS->{'artl_title'}};
			$artl_id = $ARTL_TITLE_ID{$artl_title} if(defined $artl_title && length $artl_title && exists $ARTL_TITLE_ID{$artl_title} && defined $ARTL_TITLE_ID{$artl_title});
		}

		my $artc_id;
		if(exists $KEYS->{'artc_id'} && defined $KEYS->{'artc_id'} && length $KEYS->{'artc_id'} && exists $hash->{$KEYS->{'artc_id'}} && defined $hash->{$KEYS->{'artc_id'}} && length $hash->{$KEYS->{'artc_id'}}){
			$artc_id = $hash->{$KEYS->{'artc_id'}};
		}

		my $art_data;
		if(defined $dir && -e $dir && -d $dir){
			my $obj_raw_file = &catfile($dir,sprintf('%s_raw.obj',$hash->{$KEYS->{'art_id'}}));
#			&cgi_lib::common::message($obj_raw_file,$LOG) if(defined $LOG);
			$art_data = &readObjFile($obj_raw_file) if(-e $obj_raw_file && -f $obj_raw_file && -s $obj_raw_file);
		}

		my $obj_file;
		if(defined $dir && -e $dir && -d $dir){
			$obj_file = &catfile($dir,sprintf('%s.obj',$hash->{$KEYS->{'art_id'}}));
#			&cgi_lib::common::message($obj_file,$LOG) if(defined $LOG);
		}
		unless(defined $art_data && length $art_data){
			unless(
				defined $obj_file && -e $obj_file && -f $obj_file && -s $obj_file &&
				&is_reg_obj_hash($header,$hash,$KEYS)
			){
				&cgi_lib::common::message('情報不足',$LOG) if(defined $LOG);
				next;
			}
		}
		$art_data = &readObjFile($obj_file) if(defined $obj_file && -e $obj_file && -f $obj_file && -s $obj_file);
		unless(defined $art_data && length $art_data){
			&cgi_lib::common::message('データ無し',$LOG) if(defined $LOG);
			next;
		}

		$sth_id_prefix->execute($hash->{$KEYS->{'prefix_char'}}) or die $dbh->errstr;
		my $prefix_id;
		$column_number = 0;
		$sth_id_prefix->bind_col(++$column_number, \$prefix_id, undef);
		$sth_id_prefix->fetch;
		$sth_id_prefix->finish;
		unless(defined $prefix_id && $prefix_id =~ /^[0-9]+$/){
			&cgi_lib::common::message('prefix_id無し',$LOG) if(defined $LOG);
			next;
		}

		my $db_art_id;
		my $db_art_serial;
		$column_number = 0;
		$sth_art_file->execute($art_data,$art_data,$prefix_id) or die $dbh->errstr;
#&cgi_lib::common::message('確認:'.$sth_art_file->rows(),$LOG) if(defined $LOG);
		$sth_art_file->bind_col(++$column_number, \$db_art_id, undef);
		$sth_art_file->bind_col(++$column_number, \$db_art_serial, undef);
		while($sth_art_file->fetch){
			last if(defined $db_art_id && $db_art_id eq $hash_art_id);
		}
		$sth_art_file->finish;
#		if(defined $db_art_id){
#			unless($db_art_id eq $hash_art_id){
#				push(@{$RTN->{'messages'}}, qq|[$hash_art_id]<>[$db_art_id] |.&cgi_lib::common::decodeUTF8('登録されているIDが異なります'));
#				&cgi_lib::common::message(qq|[$hash_art_id]<>[$db_art_id] |.&cgi_lib::common::decodeUTF8('登録されているIDが異なります'),$LOG) if(defined $LOG);
#			}else{
#				$sth_art_upd2->execute($hash_art_id) or die $dbh->errstr;
#				if($sth_art_upd2->rows()>0){
#					$exec_ins++;
#				}
#				$sth_art_upd2->finish();
##				&cgi_lib::common::message('登録済み',$LOG) if(defined $LOG);
#			}
#		}
		if(defined $db_art_id && $db_art_id eq $hash_art_id){
			$sth_art_upd2->execute($hash_art_id) or die $dbh->errstr;
			if($sth_art_upd2->rows()>0){
				$exec_ins++;
			}
			$sth_art_upd2->finish();

			$sth_art_upd_artc->execute($artl_id,$artc_id,$hash_art_id) or die $dbh->errstr;
			$sth_art_upd_artc->finish();
			$sth_arti_upd_artc->execute($artl_id,$artc_id,$hash_art_id) or die $dbh->errstr;
			$sth_arti_upd_artc->finish();

		}
		else{
#			&cgi_lib::common::message('未登録',$LOG) if(defined $LOG);

			my($art_name,$art_dir,$art_ext) = &File::Basename::fileparse($hash->{$KEYS->{'art_filename'}},qw|.obj|);
			my $art_nsn = exists $hash->{$KEYS->{'art_nsn'}} && defined $hash->{$KEYS->{'art_nsn'}} ? $hash->{$KEYS->{'art_nsn'}} - 0 : 0;
			my $art_cube_volume = exists $hash->{$KEYS->{'art_cube_volume'}} && defined $hash->{$KEYS->{'art_cube_volume'}} ? $hash->{$KEYS->{'art_cube_volume'}} - 0 : &Truncated(($hash->{$KEYS->{'art_xmax'}}-$hash->{$KEYS->{'art_xmin'}})*($hash->{$KEYS->{'art_ymax'}}-$hash->{$KEYS->{'art_ymin'}})*($hash->{$KEYS->{'art_zmax'}}-$hash->{$KEYS->{'art_zmin'}})/1000);

			$column_number = 0;
			$sth_art_sel->execute($hash_art_id) or die $dbh->errstr;
			my $art_id_rows = $sth_art_sel->rows();
			$sth_art_sel->finish();
			if($art_id_rows>0){

				$sth_art_upd_artc->execute($artl_id,$artc_id,$hash_art_id) or die $dbh->errstr;
				$sth_art_upd_artc->finish();
				$sth_arti_upd_artc->execute($artl_id,$artc_id,$hash_art_id) or die $dbh->errstr;
				$sth_arti_upd_artc->finish();

			}else{

				my $artg_id;
				$column_number = 0;
#				$sth_artg_sel->execute($params->{'filename'}) or die $dbh->errstr;
				$sth_artg_sel->execute($art_name) or die $dbh->errstr;
				$sth_artg_sel->bind_col(++$column_number, \$artg_id, undef);
				$sth_artg_sel->fetch;
				$sth_artg_sel->finish;
				if(defined $artg_id){
					$sth_artg_upd->execute($artg_id) or die $dbh->errstr;
					$sth_artg_upd->finish;
				}else{
#&cgi_lib::common::message($params,$LOG) if(defined $LOG);
					my $artf_id;
					if(exists $hash->{$KEYS->{'art_folder'}} && defined $hash->{$KEYS->{'art_folder'}} && length $hash->{$KEYS->{'art_folder'}}){
						my @art_folder = split('/',$hash->{$KEYS->{'art_folder'}});
						for(@art_folder){
							next unless(length $_);
							my $artf_name = $_;
							my $artf_pid = $artf_id;
							$sth_artf_sel->execute($artf_pid,$artf_name) or die $dbh->errstr;
							$column_number = 0;
							$sth_artf_sel->bind_col(++$column_number, \$artf_id, undef);
							$sth_artf_sel->fetch;
							$sth_artf_sel->finish;
							if(defined $artf_id){
								$sth_artf_upd->execute($artf_id) or die $dbh->errstr;
								$sth_artf_upd->finish;
							}else{
								$sth_artf_ins->execute($artf_pid,$artf_name) or die $dbh->errstr;
								$column_number = 0;
								$sth_artf_ins->bind_col(++$column_number, \$artf_id, undef);
								$sth_artf_ins->fetch;
								$sth_artf_ins->finish;
							}
						}
&cgi_lib::common::message($artf_id,$LOG) if(defined $LOG);
#die __LINE__;
					}

					$column_number = 0;
					$sth_artg_ins->execute($art_name,$artf_id) or die $dbh->errstr;
					$sth_artg_ins->bind_col(++$column_number, \$artg_id, undef);
					$sth_artg_ins->fetch;
					$sth_artg_ins->finish;
				}

				my $obj_deci_prefix = &catfile($dir,$hash->{$KEYS->{'art_id'}}.qq|.deci|);
				my $obj_deci_file = qq|$obj_deci_prefix.obj|;
				&BITS::VTK::quadricDecimation($obj_file,$obj_deci_prefix);
				my $art_decimate = &readObjFile($obj_deci_file);
				my $art_decimate_size = length($art_decimate);

&cgi_lib::common::message($hash,$LOG) if(defined $LOG);
				$column_number = 0;
				$sth_art_ins->bind_param(++$column_number, $prefix_id);
				$sth_art_ins->bind_param(++$column_number, $hash->{$KEYS->{'art_id'}});
				$sth_art_ins->bind_param(++$column_number, $hash->{$KEYS->{'art_serial'}});
				$sth_art_ins->bind_param(++$column_number, $art_name);
				$sth_art_ins->bind_param(++$column_number, $art_ext);
				$sth_art_ins->bind_param(++$column_number, $hash->{$KEYS->{'art_timestamp'}});
				$sth_art_ins->bind_param(++$column_number, $hash->{$KEYS->{'art_md5'}});
				$sth_art_ins->bind_param(++$column_number, $art_data, { pg_type => DBD::Pg::PG_BYTEA });
				$sth_art_ins->bind_param(++$column_number, $hash->{$KEYS->{'art_data_size'}});
				$sth_art_ins->bind_param(++$column_number, $hash->{$KEYS->{'art_xmin'}});
				$sth_art_ins->bind_param(++$column_number, $hash->{$KEYS->{'art_xmax'}});
				$sth_art_ins->bind_param(++$column_number, $hash->{$KEYS->{'art_ymin'}});
				$sth_art_ins->bind_param(++$column_number, $hash->{$KEYS->{'art_ymax'}});
				$sth_art_ins->bind_param(++$column_number, $hash->{$KEYS->{'art_zmin'}});
				$sth_art_ins->bind_param(++$column_number, $hash->{$KEYS->{'art_zmax'}});
				$sth_art_ins->bind_param(++$column_number, $hash->{$KEYS->{'art_volume'}});
				$sth_art_ins->bind_param(++$column_number, $art_cube_volume);
				$sth_art_ins->bind_param(++$column_number, $art_nsn);
				$sth_art_ins->bind_param(++$column_number, $art_mirroring);
				$sth_art_ins->bind_param(++$column_number, $hash->{$KEYS->{'art_entry'}});
				$sth_art_ins->bind_param(++$column_number, $art_decimate, { pg_type => DBD::Pg::PG_BYTEA });
				$sth_art_ins->bind_param(++$column_number, $art_decimate_size);

#				$sth_art_ins->bind_param(++$column_number, $params->{'md_id'});
#				$sth_art_ins->bind_param(++$column_number, $params->{'mv_id'});
#				$sth_art_ins->bind_param(++$column_number, $params->{'mr_id'});
				$sth_art_ins->bind_param(++$column_number, $artg_id);

				$sth_art_ins->bind_param(++$column_number, $artl_id);
				$sth_art_ins->bind_param(++$column_number, $artc_id);

				$sth_art_ins->execute() or die $dbh->errstr;
	&cgi_lib::common::message('登録:'.$sth_art_ins->rows(),$LOG) if(defined $LOG);
				$sth_art_ins->finish();
			}
			$exec_ins++;
		}
	}
&cgi_lib::common::message('登録数:'.$exec_ins,$LOG) if(defined $LOG);
	if($exec_ins){
		$dbh->do($sql_insert_art_file_info) or die $dbh->errstr;
		$dbh->do($sql_update_art_file_info) or die $dbh->errstr;
	}
	&cgi_lib::common::message(sprintf("%f",&Time::HiRes::tv_interval($t)),$LOG) if(defined $LOG);

######2024/05/13 CUT START
=pod
	my %CDI_NAME2DEPTH;
	{
		my $FORM = &Clone::clone($params);
		$FORM->{'dbh'} = $dbh;
		$FORM->{'LOG'} = $LOG;

		if($format_version eq '201903xx'){
			&BITS::ConceptArtMapPart::all_clear_subclass_tree(%$FORM);
			%CDI_NAME2DEPTH = &BITS::ConceptArtMapPart::all_use_list_depth(%$FORM);
		}
		else{
			&BITS::ConceptArtMapPart20190131::all_clear_subclass_tree(%$FORM);
			%CDI_NAME2DEPTH = &BITS::ConceptArtMapPart20190131::all_use_list_depth(%$FORM);
		}
	}
	&cgi_lib::common::message(sprintf("%f",&Time::HiRes::tv_interval($t)),$LOG) if(defined $LOG);
	my %SUBCLASS;
	foreach my $hash_art_id (keys %art_id_2_hash){
		my $hash = $art_id_2_hash{$hash_art_id};
		my $cdi_name;
		my $cdi_name_e;
		my $cdi_syn_e;
		my $cmp_title;
		my $cmp_id;
		my $bcp_title;
		my $bcp_id;
		my $bcl_title;
		my $bcl_id;
		if(exists $header->{$KEYS->{'cdi_name'}} && defined $header->{$KEYS->{'cdi_name'}}){
			$cdi_name = $hash->{$KEYS->{'cdi_name'}} if(exists $hash->{$KEYS->{'cdi_name'}} && defined $hash->{$KEYS->{'cdi_name'}} && length $hash->{$KEYS->{'cdi_name'}});
		}
		if(exists $header->{$KEYS->{'cdi_name_e'}} && defined $header->{$KEYS->{'cdi_name_e'}}){
			$cdi_name_e = $hash->{$KEYS->{'cdi_name_e'}} if(exists $hash->{$KEYS->{'cdi_name_e'}} && defined $hash->{$KEYS->{'cdi_name_e'}} && length $hash->{$KEYS->{'cdi_name_e'}});
		}
		if(exists $header->{$KEYS->{'cdi_syn_e'}} && defined $header->{$KEYS->{'cdi_syn_e'}}){
			$cdi_syn_e = $hash->{$KEYS->{'cdi_syn_e'}} if(exists $hash->{$KEYS->{'cdi_syn_e'}} && defined $hash->{$KEYS->{'cdi_syn_e'}} && length $hash->{$KEYS->{'cdi_syn_e'}});
		}

		if(exists $KEYS->{'cmp_title'} && defined $KEYS->{'cmp_title'} && exists $header->{$KEYS->{'cmp_title'}} && defined $header->{$KEYS->{'cmp_title'}}){
			$cmp_title = $hash->{$KEYS->{'cmp_title'}} if(exists $hash->{$KEYS->{'cmp_title'}} && defined $hash->{$KEYS->{'cmp_title'}} && length $hash->{$KEYS->{'cmp_title'}});
		}
		$cmp_id = $CMP_TITLE_ID{$cmp_title} if(defined $cmp_title && exists $CMP_TITLE_ID{$cmp_title});

		if(exists $KEYS->{'bcp_title'} && defined $KEYS->{'bcp_title'} && exists $header->{$KEYS->{'bcp_title'}} && defined $header->{$KEYS->{'bcp_title'}}){
			$bcp_title = $hash->{$KEYS->{'bcp_title'}} if(exists $hash->{$KEYS->{'bcp_title'}} && defined $hash->{$KEYS->{'bcp_title'}} && length $hash->{$KEYS->{'bcp_title'}});
		}
		$bcp_id = $BCP_TITLE_ID{$bcp_title} if(defined $bcp_title && exists $BCP_TITLE_ID{$bcp_title});

		if(exists $KEYS->{'bcl_title'} && defined $KEYS->{'bcl_title'} && exists $header->{$KEYS->{'bcl_title'}} && defined $header->{$KEYS->{'bcl_title'}}){
			$bcl_title = $hash->{$KEYS->{'bcl_title'}} if(exists $hash->{$KEYS->{'bcl_title'}} && defined $hash->{$KEYS->{'bcl_title'}} && length $hash->{$KEYS->{'bcl_title'}});
		}
		$bcl_id = $BCL_TITLE_ID{$bcl_title} if(defined $bcl_title && exists $BCL_TITLE_ID{$bcl_title});

		if(defined $LOG){
			&cgi_lib::common::message(defined $hash_art_id ? $hash_art_id : '',$LOG);
			&cgi_lib::common::message(defined $cdi_name ? $cdi_name : '',$LOG);
			&cgi_lib::common::message(defined $cmp_title ? $cmp_title : '',$LOG);
			&cgi_lib::common::message(defined $cmp_id ? $cmp_id : '',$LOG);
			&cgi_lib::common::message(defined $bcp_title ? $bcp_title : '',$LOG);
			&cgi_lib::common::message(defined $bcp_id ? $bcp_id : '',$LOG);
			&cgi_lib::common::message(defined $bcl_title ? $bcl_title : '',$LOG);
			&cgi_lib::common::message(defined $bcl_id ? $bcl_id : '',$LOG);
		}
		if(defined $cdi_name){
			&cgi_lib::common::message(defined $cdi_name ? $cdi_name : '',$LOG) if(defined $LOG);
			my $FORM = &Clone::clone($params);
			$FORM->{'cdi_name'} = $cdi_name;
			$FORM->{'cmp_id'} = $cmp_id;
			$FORM->{'bcp_id'} = $bcp_id;
			$FORM->{'bcl_id'} = $bcl_id;

			delete $FORM->{'dbh'} if(exists $FORM->{'dbh'});
			delete $FORM->{'LOG'} if(exists $FORM->{'LOG'});
			&cgi_lib::common::message($FORM,$LOG) if(defined $LOG);

			$FORM->{'dbh'} = $dbh;
			$FORM->{'LOG'} = $LOG;
			if($format_version eq '201903xx'){
				$cdi_name = &BITS::ConceptArtMapPart::get_cdi_name(%$FORM);
			}
			else{
				$cdi_name = &BITS::ConceptArtMapPart20190131::get_cdi_name(%$FORM);
			}
		}
		&cgi_lib::common::message(defined $cdi_name ? $cdi_name : '',$LOG) if(defined $LOG);
		unless(defined $cdi_name){
			&cgi_lib::common::message('none subclass',$LOG) if(defined $LOG);
			next;
		}
		die qq|Mismatch $KEYS->{'cdi_name'}:[$hash->{$KEYS->{'cdi_name'}}]:[$cdi_name]| unless($hash->{$KEYS->{'cdi_name'}} eq  $cdi_name);

		my $cdi_pname;
		my $cdi_pname_e;
		my $cdi_psyn_e;
		my $cdi_sname;
		my $cdi_sname_e;
		my $cdi_ssyn_e;
		if(exists $header->{$KEYS->{'cdi_pname'}} && defined $header->{$KEYS->{'cdi_pname'}}){
			$cdi_pname = $hash->{$KEYS->{'cdi_pname'}} if(exists $hash->{$KEYS->{'cdi_pname'}} && defined $hash->{$KEYS->{'cdi_pname'}} && length $hash->{$KEYS->{'cdi_pname'}});
		}
		if(exists $header->{$KEYS->{'cdi_pname_e'}} && defined $header->{$KEYS->{'cdi_pname_e'}}){
			$cdi_pname_e = $hash->{$KEYS->{'cdi_pname_e'}} if(exists $hash->{$KEYS->{'cdi_pname_e'}} && defined $hash->{$KEYS->{'cdi_pname_e'}} && length $hash->{$KEYS->{'cdi_pname_e'}});
		}
		if(exists $header->{$KEYS->{'cdi_psyn_e'}} && defined $header->{$KEYS->{'cdi_psyn_e'}}){
			$cdi_psyn_e = $hash->{$KEYS->{'cdi_psyn_e'}} if(exists $hash->{$KEYS->{'cdi_psyn_e'}} && defined $hash->{$KEYS->{'cdi_psyn_e'}} && length $hash->{$KEYS->{'cdi_psyn_e'}});
		}

		if(exists $header->{$KEYS->{'cdi_sname'}} && defined $header->{$KEYS->{'cdi_sname'}}){
			$cdi_sname = $hash->{$KEYS->{'cdi_sname'}} if(exists $hash->{$KEYS->{'cdi_sname'}} && defined $hash->{$KEYS->{'cdi_sname'}} && length $hash->{$KEYS->{'cdi_sname'}});
		}
		if(exists $header->{$KEYS->{'cdi_sname_e'}} && defined $header->{$KEYS->{'cdi_sname_e'}}){
			$cdi_sname_e = $hash->{$KEYS->{'cdi_sname_e'}} if(exists $hash->{$KEYS->{'cdi_sname_e'}} && defined $hash->{$KEYS->{'cdi_sname_e'}} && length $hash->{$KEYS->{'cdi_sname_e'}});
		}
		if(exists $header->{$KEYS->{'cdi_ssyn_e'}} && defined $header->{$KEYS->{'cdi_ssyn_e'}}){
			$cdi_ssyn_e = $hash->{$KEYS->{'cdi_ssyn_e'}} if(exists $hash->{$KEYS->{'cdi_ssyn_e'}} && defined $hash->{$KEYS->{'cdi_ssyn_e'}} && length $hash->{$KEYS->{'cdi_ssyn_e'}});
		}
		unless(defined $cdi_pname && length $cdi_pname){
			if(defined $cdi_name){
				my $FORM = &Clone::clone($params);
				$FORM->{'cdi_name'}  = $cdi_name;
				$FORM->{'cmp_id'}    = $cmp_id;
				$FORM->{'bcp_title'} = $bcp_title;
				$FORM->{'bcp_id'}    = $bcp_id;
				$FORM->{'bcl_title'} = $bcl_title;
				$FORM->{'bcl_id'}    = $bcl_id;
				$FORM->{'dbh'} = $dbh;
				$FORM->{'LOG'} = $LOG;
				if($format_version eq '201903xx'){
					$cdi_pname = &BITS::ConceptArtMapPart::get_cdi_pname(%$FORM);
				}
				else{
					$cdi_pname = &BITS::ConceptArtMapPart20190131::get_cdi_pname(%$FORM);
				}
			}
		}
		&cgi_lib::common::message(defined $cdi_pname ? $cdi_pname : '',$LOG) if(defined $LOG);
		unless(defined $cdi_pname && exists $CDI_NAME2DEPTH{$cdi_pname} && defined $CDI_NAME2DEPTH{$cdi_pname}){
			&cgi_lib::common::message('unknown subclass parent',$LOG) if(defined $LOG);
			next;
		}

		&cgi_lib::common::message($cdi_name,$LOG) if(defined $LOG);
		$SUBCLASS{$cdi_name} = {
			cdi_pname => $cdi_pname,
			cmp_title => $cmp_title,
			cmp_id    => $cmp_id,
			bcp_title => $bcp_title,
			bcp_id    => $bcp_id,
			bcl_title => $bcl_title,
			bcl_id    => $bcl_id,
			cdi_pname => $cdi_pname,
			cdi_pid   => defined $cdi_pname && length $cdi_pname && exists $CDI_NAME{$cdi_pname} && defined $CDI_NAME{$cdi_pname} ? $CDI_NAME{$cdi_pname} : undef,
			cdi_sname => $cdi_sname,
			cdi_sid   => defined $cdi_sname && length $cdi_sname && exists $CDI_NAME{$cdi_sname} && defined $CDI_NAME{$cdi_sname} ? $CDI_NAME{$cdi_sname} : undef,
			but_depth => $CDI_NAME2DEPTH{$cdi_pname}
		};
	}
	&cgi_lib::common::message(sprintf("%f",&Time::HiRes::tv_interval($t)),$LOG) if(defined $LOG);
	foreach my $cdi_name (sort {$SUBCLASS{$a}->{'but_depth'} <=> $SUBCLASS{$b}->{'but_depth'}} keys %SUBCLASS){
		&cgi_lib::common::message($format_version,$LOG) if(defined $LOG);
		&cgi_lib::common::message($cdi_name,$LOG) if(defined $LOG);
		my $FORM = &Clone::clone($params);
		$FORM->{'cdi_name'}  = $cdi_name;
		$FORM->{'cmp_id'}    = $SUBCLASS{$cdi_name}->{'cmp_id'};
		$FORM->{'bcp_id'}    = $SUBCLASS{$cdi_name}->{'bcp_id'};
		$FORM->{'bcl_id'}    = $SUBCLASS{$cdi_name}->{'bcl_id'};
		$FORM->{'cdi_pname'} = $SUBCLASS{$cdi_name}->{'cdi_pname'};
		$FORM->{'cdi_pid'}   = $SUBCLASS{$cdi_name}->{'cdi_pid'};
		$FORM->{'cdi_sname'} = $SUBCLASS{$cdi_name}->{'cdi_sname'};
		$FORM->{'cdi_sid'}   = $SUBCLASS{$cdi_name}->{'cdi_sid'};

		delete $FORM->{'dbh'} if(exists $FORM->{'dbh'});
		delete $FORM->{'LOG'} if(exists $FORM->{'LOG'});
		&cgi_lib::common::message($FORM,$LOG) if(defined $LOG);

		$FORM->{'dbh'} = $dbh;
		$FORM->{'LOG'} = $LOG;
		if($format_version eq '201903xx'){
			&BITS::ConceptArtMapPart::create_subclass(%$FORM);
		}
		else{
			&BITS::ConceptArtMapPart20190131::create_subclass(%$FORM);
		}

		my $cdi_id;
		unless(exists $CDI_NAME{$cdi_name} && defined $CDI_NAME{$cdi_name} && length $CDI_NAME{$cdi_name}){
			&cgi_lib::common::message("\$cdi_name=[$cdi_name]",$LOG) if(defined $LOG && defined $cdi_name);
			$sth_cdi_sel->execute($params->{'ci_id'},$cdi_name) or die $dbh->errstr;
			$sth_cdi_sel->bind_col(1, \$cdi_id, undef);
			$sth_cdi_sel->fetch;
			$sth_cdi_sel->finish();
			&cgi_lib::common::message("\$cdi_id=[$cdi_id]",$LOG) if(defined $LOG && defined $cdi_id);
			die qq|Unknown $KEYS->{'cdi_name'}:[$cdi_name}]| unless(defined $cdi_id);

			$CDI_NAME{$cdi_name} = $cdi_id;
		}
	}
	&_writeProgress();
	&cgi_lib::common::message(sprintf("%f",&Time::HiRes::tv_interval($t)),$LOG) if(defined $LOG);
=cut
######2024/05/13 CUT END

#	$data_pos = 0;
#	$total = scalar keys %art_id_2_hash;
	foreach my $hash_art_id (sort {$a cmp $b} keys %art_id_2_hash){
		my $hash = $art_id_2_hash{$hash_art_id};
		$data_pos++;
		&cgi_lib::common::message(sprintf('[%05d/%05d]',$data_pos,$total),$LOG) if(defined $LOG);
		$RTN->{'progress'} = {
			'value' => $data_pos/$total,
			'msg' => &cgi_lib::common::decodeUTF8(qq|[$data_pos/$total]|)
		};
		&_writeProgress();

#		&cgi_lib::common::message($hash,,$LOG);
#		next;

		$RTN->{'msg'} = &cgi_lib::common::decodeUTF8(qq|Registration: $hash->{$KEYS->{'art_id'}}|);
		$RTN->{'progress'}->{'msg'} = &cgi_lib::common::decodeUTF8(qq|[$data_pos/$total] $hash->{$KEYS->{'art_id'}}|);
		&_writeProgress();

		my $org_art_id;
		my $mirror_art_id;
		my $art_mirroring;

		if($hash->{$KEYS->{'art_id'}} =~ /^([A-Z]+[0-9]+)M$/){
			$org_art_id = $1;
			$mirror_art_id = $hash->{$KEYS->{'art_id'}};
			$art_mirroring = 1;
		}else{
			$art_mirroring = 0;
		}
		&_writeProgress();


		if(defined $mirror_art_id){

			$sth_art_sel->execute($mirror_art_id) or die $dbh->errstr;
			my $mirror_rows = $sth_art_sel->rows();
			$sth_art_sel->finish();
			$sth_art_sel->execute($art_id) or die $dbh->errstr;
			my $original_rows = $sth_art_sel->rows();
			$sth_art_sel->finish();

			if($mirror_rows==0 && $original_rows==0){
				undef $hash;
				next;
			}elsif($mirror_rows==0 && $original_rows>0){

				$sth_art_sel->execute($art_id) or die $dbh->errstr;
				my $rows = $sth_art_sel->rows();

#				if(defined $LOG){
#					&cgi_lib::common::message("\$art_id=[$art_id]",$LOG);
#					&cgi_lib::common::message("\$rows=[$rows]",$LOG);
#				}

				my($prefix_id,$art_serial,$art_name,$art_ext,$art_timestamp);
				if($rows>0){
					$column_number = 0;
					$sth_art_sel->bind_col(++$column_number, \$prefix_id, undef);
					$sth_art_sel->bind_col(++$column_number, \$art_serial, undef);
					$sth_art_sel->bind_col(++$column_number, \$art_name, undef);
					$sth_art_sel->bind_col(++$column_number, \$art_ext, undef);
					$sth_art_sel->bind_col(++$column_number, \$art_timestamp, undef);
					$sth_art_sel->fetch;
				}
				$sth_art_sel->finish;
				undef $sth_art_sel;

				if(defined $art_id && defined $art_ext){
					my $org_file_path = &catfile($art_path,qq|$art_id$art_ext|);
					my $mir_file_prefix = &catfile($art_path,$mirror_art_id);
					my $mir_file_path = qq|$mir_file_prefix$art_ext|;
					my $mir_prop = &BITS::VTK::reflection($org_file_path,$mir_file_prefix);
					die __LINE__,qq|:ERROR: reflection()[$mir_file_path]| unless(defined $mir_prop);
					if(
						defined $mir_prop &&
						ref $mir_prop eq 'HASH' &&
						exists $mir_prop->{'bounds'} &&
						defined $mir_prop->{'bounds'} &&
						ref $mir_prop->{'bounds'} eq 'ARRAY' &&
						scalar @{$mir_prop->{'bounds'}} == 6
					){
						my $art_xmin = $mir_prop->{'bounds'}->[0] - 0;
						my $art_xmax = $mir_prop->{'bounds'}->[1] - 0;
						my $art_ymin = $mir_prop->{'bounds'}->[2] - 0;
						my $art_ymax = $mir_prop->{'bounds'}->[3] - 0;
						my $art_zmin = $mir_prop->{'bounds'}->[4] - 0;
						my $art_zmax = $mir_prop->{'bounds'}->[5] - 0;
						my $art_volume = defined $mir_prop->{'volume'} && $mir_prop->{'volume'} > 0 ?  &Truncated($mir_prop->{'volume'} / 1000) : 0;
						my $art_cube_volume = &Truncated(($art_xmax-$art_xmin)*($art_ymax-$art_ymin)*($art_zmax-$art_zmin)/1000);

						if(-e $mir_file_path && -s $mir_file_path){
							my $art_data = &readObjFile($mir_file_path);
							my $art_data_size = length($art_data);
							if($art_data_size>0){
								my $art_md5 = &Digest::MD5::md5_hex($art_data);

								my $artg_id;
								$column_number = 0;
								$sth_artg_sel_art_id->execute($art_id) or die $dbh->errstr;
								$sth_artg_sel_art_id->bind_col(++$column_number, \$artg_id, undef);
								$sth_artg_sel_art_id->fetch;
								$sth_artg_sel_art_id->finish;

								my $obj_deci_prefix = &catfile($dir,$mirror_art_id.qq|.deci|);
								my $obj_deci_file = qq|$obj_deci_prefix.obj|;
								&BITS::VTK::quadricDecimation($mir_file_path,$obj_deci_prefix);
								my $art_decimate = &readObjFile($obj_deci_file);
								my $art_decimate_size = length($art_decimate);

								my $param_num = 0;
								$sth_art_mirror_ins->bind_param(++$param_num, $prefix_id);
								$sth_art_mirror_ins->bind_param(++$param_num, $mirror_art_id);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_serial);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_name);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_ext);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_timestamp);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_md5);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_data, { pg_type => DBD::Pg::PG_BYTEA });
								$sth_art_mirror_ins->bind_param(++$param_num, $art_data_size);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_xmin);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_xmax);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_ymin);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_ymax);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_zmin);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_zmax);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_volume);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_cube_volume);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_mirroring);

								$sth_art_mirror_ins->bind_param(++$param_num, undef);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_decimate, { pg_type => DBD::Pg::PG_BYTEA });
								$sth_art_mirror_ins->bind_param(++$param_num, $art_decimate_size);

#								$sth_art_mirror_ins->bind_param(++$param_num, $params->{'md_id'});
#								$sth_art_mirror_ins->bind_param(++$param_num, $params->{'mv_id'});
#								$sth_art_mirror_ins->bind_param(++$param_num, $params->{'mr_id'});
								$sth_art_mirror_ins->bind_param(++$param_num, $artg_id);

								$sth_art_mirror_ins->bind_param(++$param_num, 0);
								$sth_art_mirror_ins->bind_param(++$param_num, undef);

								$sth_art_mirror_ins->execute() or die $dbh->errstr;
								$mirror_rows = $sth_art_mirror_ins->rows();
								$sth_art_mirror_ins->finish();

								$dbh->do($sql_insert_art_file_info) or die $dbh->errstr;
								$dbh->do($sql_update_art_file_info) or die $dbh->errstr;

								&BITS::Voxel::insVoxelData($dbh,$mirror_art_id,0,$art_data);
							}
						}
					}
				}

			}else{
				#データは既に存在するので何もしない
			}
		}
		&_writeProgress();


		#art_idがtableに存在するか確認
		$sth_art_sel->execute($hash->{$KEYS->{'art_id'}}) or die $dbh->errstr;
		my $art_id_rows = $sth_art_sel->rows();
		$sth_art_sel->finish();
#		&cgi_lib::common::message("\$art_id_rows=[$art_id_rows]",$LOG) if(defined $LOG);
		next unless($art_id_rows>0);

		&_writeProgress();
#		&cgi_lib::common::message(sprintf("%f",&Time::HiRes::tv_interval($t)),$LOG) if(defined $LOG);

		if(exists $header->{$KEYS->{'cdi_name'}} && defined $header->{$KEYS->{'cdi_name'}}){
			unless(exists $hash->{$KEYS->{'cdi_name'}} && defined $hash->{$KEYS->{'cdi_name'}}){
				&cgi_lib::common::message(undef,$LOG) if(defined $LOG);

				my @bind_values;
				push(@bind_values,$params->{'ci_id'},$params->{'cb_id'},$params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'});
				push(@bind_values,$hash->{$KEYS->{'art_id'}});
				$sth_cm_del->execute(@bind_values) or die $dbh->errstr;
				$sth_cm_del->finish();
				undef @bind_values;

			}
			else{
#				&cgi_lib::common::message(undef,$LOG) if(defined $LOG);

				my $cdi_id;
				my $cdi_name;

				my $cmp_title;
				my $cmp_abbr = '';
				my $cmp_id;

#				if($hash->{$KEYS->{'cdi_name'}} =~ /^([A-Z]+[0-9]+)\-*([A-Z]*)$/){
#					$cdi_name = $1;
#					$cmp_abbr = $2 || '';
#				}
				$cdi_name = exists $KEYS->{'cdi_name'} && defined $KEYS->{'cdi_name'} && exists $hash->{$KEYS->{'cdi_name'}} && defined $hash->{$KEYS->{'cdi_name'}} ? $hash->{$KEYS->{'cdi_name'}} : undef;
				$cmp_title = exists $KEYS->{'cmp_title'} && defined $KEYS->{'cmp_title'} && exists $hash->{$KEYS->{'cmp_title'}} && defined $hash->{$KEYS->{'cmp_title'}} ? $hash->{$KEYS->{'cmp_title'}} : undef;
				die qq|Unknown $KEYS->{'cdi_name'}:[$hash->{$KEYS->{'cdi_name'}}]| unless(defined $cdi_name);
				if($format_version eq 'defaults'){
					if(defined $cmp_title && exists $CMP_TITLE_ID{$cmp_title}){
						$cmp_id = $CMP_TITLE_ID{$cmp_title};
					}
					elsif(defined $cmp_abbr && exists $CMP_ABBR_ID{$cmp_abbr}){
						$cmp_id = $CMP_ABBR_ID{$cmp_abbr};
					}
					unless(defined $cmp_id){
						&cgi_lib::common::message($hash,$LOG) if(defined $LOG);
						&cgi_lib::common::message(\%CMP_TITLE_ID,$LOG) if(defined $LOG);
						&cgi_lib::common::message(\%CMP_ABBR_ID,$LOG) if(defined $LOG);
					}
					die qq|Unknown $KEYS->{'cdi_name'}:[$hash->{$KEYS->{'cdi_name'}}][$cmp_title][$cmp_abbr]| unless(defined $cmp_id);
				}
				else{
					$cmp_id = 0;
				}
#				{
#					my $FORM = &Clone::clone($params);
#					$FORM->{'cdi_name'} = $cdi_name;
#					$FORM->{'cmp_id'} = $cmp_id;
#					$FORM->{'dbh'} = $dbh;
#					$FORM->{'LOG'} = $LOG;
#					&BITS::ConceptArtMapPart::create_subclass(%$FORM);
#				}
				unless(exists $CDI_NAME{$cdi_name} && defined $CDI_NAME{$cdi_name} && length $CDI_NAME{$cdi_name}){
					&cgi_lib::common::message(qq|Unknown $KEYS->{'cdi_name'}:[$hash->{$KEYS->{'cdi_name'}}]|,$LOG) if(defined $LOG);

					if(exists $MAPPED_ART_ID{$hash->{$KEYS->{'art_id'}}}){
						my @bind_values;
						push(@bind_values,$params->{'ci_id'},$params->{'cb_id'},$params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'});
						push(@bind_values,$hash->{$KEYS->{'art_id'}});
						$sth_cm_del->execute(@bind_values) or die $dbh->errstr;
						$sth_cm_del->finish();
						undef @bind_values;

						delete $MAPPED_ART_ID{$hash->{$KEYS->{'art_id'}}};
					}


#					&cgi_lib::common::message("\$cdi_name=[$cdi_name]",$LOG) if(defined $LOG && defined $cdi_name);
#					$sth_cdi_sel->execute($params->{'ci_id'},$cdi_name) or die $dbh->errstr;
#					$sth_cdi_sel->bind_col(1, \$cdi_id, undef);
#					$sth_cdi_sel->fetch;
#					$sth_cdi_sel->finish();
#					&cgi_lib::common::message("\$cdi_id=[$cdi_id]",$LOG) if(defined $LOG && defined $cdi_id);
#					die qq|Unknown $KEYS->{'cdi_name'}:[$hash->{$KEYS->{'cdi_name'}}]| unless(defined $cdi_id);
				}
				else{
					$cdi_id = $CDI_NAME{$cdi_name};
				}
#				&cgi_lib::common::message(undef,$LOG) if(defined $LOG);

				if(defined $cdi_id){
					$sth_cd_sel->execute($params->{'ci_id'},$params->{'cb_id'},$cdi_id) or die $dbh->errstr;
					my $cd_sel_rows = $sth_cd_sel->rows();
					$sth_cd_sel->finish();
#					&cgi_lib::common::message($cd_sel_rows,$LOG) if(defined $LOG);
					unless($cd_sel_rows>0){
						$sth_bd_sel->execute($params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'},$params->{'ci_id'},$params->{'cb_id'},$cdi_id) or die $dbh->errstr;
						$cd_sel_rows = $sth_bd_sel->rows();
						$sth_bd_sel->finish();
#						&cgi_lib::common::message($cd_sel_rows,$LOG) if(defined $LOG);
					}
					unless($cd_sel_rows>0){
#						&cgi_lib::common::message(undef,$LOG) if(defined $LOG);
						$cdi_id = undef;
						my @bind_values;
						push(@bind_values,$params->{'ci_id'},$params->{'cb_id'},$params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'});
						push(@bind_values,$hash->{$KEYS->{'art_id'}});
						$sth_cm_del->execute(@bind_values) or die $dbh->errstr;
						$sth_cm_del->finish();
						undef @bind_values;
						die __LINE__;
					}
				}

				$USE_CDI_ID{$cdi_id} = undef if(defined $cdi_id);

				if(exists $MAPPED_ART_ID{$hash->{$KEYS->{'art_id'}}}){
					$sth_cm_upd->execute($cdi_id,$cmp_id,$params->{'ci_id'},$params->{'cb_id'},$params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'},$hash->{$KEYS->{'art_id'}}) or die $dbh->errstr;
					$sth_cm_upd->finish();
					$MAPPED_ART_ID{$hash->{$KEYS->{'art_id'}}}++;
				}
				elsif(defined $cdi_id){
					my $cm_id;
					my $cm_serial;
					$sth_hcm_sel->execute($params->{'ci_id'},$params->{'cb_id'},$params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'},$hash->{$KEYS->{'art_id'}}) or die $dbh->errstr;
					$sth_hcm_sel->bind_col(1, \$cm_id, undef);
					$sth_hcm_sel->bind_col(2, \$cm_serial, undef);
					$sth_hcm_sel->fetch;
					$sth_hcm_sel->finish();

					unless(defined $cm_id && defined $cm_serial){

						my $hcm_serial;
						$sth_hcm_max_sel->execute() or die $dbh->errstr;
						$sth_hcm_max_sel->bind_col(1, \$hcm_serial, undef);
						$sth_hcm_max_sel->fetch;
						$sth_hcm_max_sel->finish();

						$sth_cm_max_sel->execute() or die $dbh->errstr;
						$sth_cm_max_sel->bind_col(1, \$cm_serial, undef);
						$sth_cm_max_sel->fetch;
						$sth_cm_max_sel->finish();

						$cm_serial = $hcm_serial if($cm_serial<$hcm_serial);
						$cm_serial += 1;

						$cm_id = sprintf(qq|%s%d|,$cm_prefix_char,$cm_serial);
					}

					if(defined $cm_id && defined $cm_serial){
#						&cgi_lib::common::message(undef,$LOG) if(defined $LOG);
						$sth_cm_ins2->execute($params->{'ci_id'},$params->{'cb_id'},$params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'},$hash->{$KEYS->{'art_id'}},$cdi_id,$cmp_id,$cm_id,$cm_serial) or die $dbh->errstr;
						$sth_cm_ins2->finish();
					}else{
#						$sth_cm_max_sel->execute() or die $dbh->errstr;
#						$sth_cm_max_sel->bind_col(1, \$cm_serial, undef);
#						$sth_cm_max_sel->fetch;
#						$sth_cm_max_sel->finish();
#						&cgi_lib::common::message($cm_serial + 1,$LOG) if(defined $LOG);
#						&cgi_lib::common::message(sprintf("[%d][%d][%d][%d][%d][%s][%d][%d]",$params->{'ci_id'},$params->{'cb_id'},$params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'},$hash->{$KEYS->{'art_id'}},$cdi_id,$cmp_id),$LOG) if(defined $LOG);
#						&cgi_lib::common::message(undef,$LOG) if(defined $LOG);
						$sth_cm_ins->execute($params->{'ci_id'},$params->{'cb_id'},$params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'},$hash->{$KEYS->{'art_id'}},$cdi_id,$cmp_id) or die $dbh->errstr;
						$sth_cm_ins->finish();
					}
					$MAPPED_ART_ID{$hash->{$KEYS->{'art_id'}}} = ($MAPPED_ART_ID{$hash->{$KEYS->{'art_id'}}} || 0) +1;
				}
			}
		}
		&_writeProgress();

		if(
			(defined $header->{$KEYS->{'art_comment'}} || defined $header->{$KEYS->{'art_category'}} || defined $header->{$KEYS->{'art_judge'}} || defined $header->{$KEYS->{'art_class'}}) &&
			(defined $hash->{$KEYS->{'art_comment'}} || defined $hash->{$KEYS->{'art_category'}} || defined $hash->{$KEYS->{'art_judge'}} || defined $hash->{$KEYS->{'art_class'}})
		){
			$sth_arta_sel->execute($hash->{$KEYS->{'art_id'}}) or die $dbh->errstr;
			my $rows = $sth_arta_sel->rows();
			$sth_arta_sel->finish();
			if($rows){
				$sth_arta_upd->execute($hash->{$KEYS->{'art_comment'}},$hash->{$KEYS->{'art_category'}},$hash->{$KEYS->{'art_judge'}},$hash->{$KEYS->{'art_class'}},$hash->{$KEYS->{'art_id'}}) or die $dbh->errstr;
				$sth_arta_upd->finish();
			}else{
				$sth_arta_ins->execute($hash->{$KEYS->{'art_comment'}},$hash->{$KEYS->{'art_category'}},$hash->{$KEYS->{'art_judge'}},$hash->{$KEYS->{'art_class'}},$hash->{$KEYS->{'art_id'}}) or die $dbh->errstr;
				$sth_arta_ins->finish();
			}
		}else{
			$sth_arta_del->execute($hash->{$KEYS->{'art_id'}}) or die $dbh->errstr;
			$sth_arta_del->finish();
		}
		&_writeProgress();

		if(defined $header->{$KEYS->{'arto_id'}} && defined $hash->{$KEYS->{'arto_id'}}){
			my $arto_id;
			my $arto_comment;
			my $arto = &cgi_lib::common::decodeJSON($hash->{$KEYS->{'arto_id'}});
			if(defined $arto && ref $arto eq 'HASH'){
				$arto_id = $arto->{'arto_id'};
				$arto_comment = $arto->{'arto_comment'};
			}
			if(defined $arto_id || defined $arto_comment){
				$sth_arto_sel->execute($hash->{$KEYS->{'art_id'}}) or die $dbh->errstr;
				my $rows = $sth_arto_sel->rows();
				$sth_arto_sel->finish();
				if($rows){
					$sth_arto_upd->execute($arto_id,$arto_comment,$hash->{$KEYS->{'art_id'}}) or die $dbh->errstr;
					$sth_arto_upd->finish();
				}else{
					$sth_arto_ins->execute($arto_id,$arto_comment,$hash->{$KEYS->{'art_id'}}) or die $dbh->errstr;
					$sth_arto_ins->finish();
				}
			}else{
				$sth_arto_del->execute($hash->{$KEYS->{'art_id'}}) or die $dbh->errstr;
				$sth_arto_del->finish();
			}
		}else{
			$sth_arto_del->execute($hash->{$KEYS->{'art_id'}}) or die $dbh->errstr;
			$sth_arto_del->finish();
		}

		&_writeProgress();


		undef $hash;
	}

	&_writeProgress();
	&cgi_lib::common::message(\%MAPPED_ART_ID,,$LOG) if(defined $LOG);
	&cgi_lib::common::message(sprintf("%f",&Time::HiRes::tv_interval($t)),$LOG) if(defined $LOG);

	my @DELETE_MAPPED_ART_ID = grep {$MAPPED_ART_ID{$_}==0} keys(%MAPPED_ART_ID);
	if(defined $LOG){
		&cgi_lib::common::message('['.(scalar @DELETE_MAPPED_ART_ID).']',$LOG);
		&cgi_lib::common::message(\@DELETE_MAPPED_ART_ID,,$LOG);
	}
	if(scalar @DELETE_MAPPED_ART_ID){

		&cgi_lib::common::message(qq|DELETE Other Mapping|,$LOG) if(defined $LOG);
		$RTN->{'progress'} = {
			'value' => 1,
			'msg' => &cgi_lib::common::decodeUTF8(qq|DELETE Other Mapping|)
		};
		&_writeProgress();

		my $sql_cm_del_all = sprintf(qq|DELETE FROM concept_art_map WHERE ci_id=? AND cb_id=? AND md_id=? AND mv_id=? AND mr_id<=? AND art_id IN (%s)|,join(',',map {'?'} @DELETE_MAPPED_ART_ID));;
		my $sth_cm_del_all = $dbh->prepare($sql_cm_del_all) or die $dbh->errstr;
		$sth_cm_del_all->execute($params->{'ci_id'},$params->{'cb_id'},$params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'},@DELETE_MAPPED_ART_ID) or die $dbh->errstr;
		$sth_cm_del_all->finish();
		undef $sth_cm_del_all;
	}

	&cgi_lib::common::message(qq|UPDATE Mapping Date|,$LOG) if(defined $LOG);
	$RTN->{'progress'} = {
		'value' => 0,
		'msg' => &cgi_lib::common::decodeUTF8(qq|UPDATE Mapping Date|)
	};
	&_writeProgress();
	&cgi_lib::common::message(sprintf("%f",&Time::HiRes::tv_interval($t)),$LOG) if(defined $LOG);

	my $sth_cmm_upd_modified = $dbh->prepare(qq|UPDATE concept_art_map_modified set cm_modified=null WHERE ci_id=? AND cb_id=? AND md_id=? AND mv_id=? AND mr_id=?|) or die $dbh->errstr;
	$sth_cmm_upd_modified->execute($params->{'ci_id'},$params->{'cb_id'},$params->{'md_id'},$params->{'mv_id'},$params->{'mr_id'}) or die $dbh->errstr;
	&cgi_lib::common::message($sth_cmm_upd_modified->rows(),$LOG) if(defined $LOG);
	$sth_cmm_upd_modified->finish;

	&cgi_lib::common::message(\%USE_CDI_ID,$LOG) if(defined $LOG);
	if(scalar keys(%USE_CDI_ID) > 0){
		sub callback {
			my $msg = shift;
			my $value = shift;
			$value = 1 unless(defined $value);
			if(defined $LOG){
				&cgi_lib::common::message($msg,$LOG);
				&cgi_lib::common::message($value,$LOG);
			}
			$RTN->{'progress'} = {
				'value' => $value,
				'msg' => sprintf(&cgi_lib::common::decodeUTF8(qq|UPDATE Mapping Date [ %s ]|),&cgi_lib::common::decodeUTF8($msg))
			};
			&_writeProgress();
		}
		&cgi_lib::common::message($params,$LOG) if(defined $LOG);
		my $CM_MODIFIED = &BITS::ConceptArtMapModified::exec(
			dbh => $dbh,
			ci_id => $params->{'ci_id'},
			cb_id => $params->{'cb_id'},
			md_id => $params->{'md_id'},
			mv_id => $params->{'mv_id'},
			mr_id => $params->{'mr_id'},
			cdi_ids => [keys(%USE_CDI_ID)],
			callback => \&callback,
			LOG => $LOG
		);
		&cgi_lib::common::message($CM_MODIFIED,$LOG) if(defined $LOG);
	}
	&_writeProgress();
	&cgi_lib::common::message(sprintf("%f",&Time::HiRes::tv_interval($t)),$LOG) if(defined $LOG);
}

sub trim {
	my $str = shift;
	return undef unless(defined $str);
	$str =~ s/^\s*//g;
	$str =~ s/\s*$//g;
	$str = undef if(length($str)==0);
	return $str;
}

sub get_header {
	my $data = shift;
	return undef unless(index($data,'#') == 0);

	my $idx = 0;
	my %h = map {
		$_ = &trim($_);
		$_ => $idx++;
	} split(/\t/,substr($data,1));
	return \%h;
}

sub set_data2hash {
	my $header = shift;
	my $data = shift;
	my @d = split(/\t/,$data);
	my $h;
	foreach my $key (keys(%$header)){
		next unless(exists $header->{$key} && defined $header->{$key});
		$h->{$key} = &trim(&cgi_lib::common::decodeUTF8($d[$header->{$key}]));
	}
	return $h;
}
