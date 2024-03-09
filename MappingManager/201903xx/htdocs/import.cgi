#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;

exit unless(exists $ENV{'REQUEST_METHOD'});

use CGI;
use CGI::Carp qw(fatalsToBrowser);
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
use cgi_lib::common;

my $dbh = &get_dbh();

my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,qw|.cgi|);
my $upload_dir = &catdir($FindBin::Bin,$cgi_name);

my $LOG;
open($LOG,"> $FindBin::Bin/logs/$cgi_name.txt");
select($LOG);
$| = 1;
select(STDOUT);
$| = 1;

my $RTN = {
	'success' => JSON::XS::true
};

$SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit";
sub sigexit {
	my($date) = `date`;
	$date =~ s/\s*$//g;
	$RTN->{'msg'} = $RTN->{'progress'}->{'msg'} = qq|Error:[$date] KILL THIS SCRIPT!!|;
	$RTN->{'success'} = JSON::XS::false;
	&gzip_json($RTN);
	exit(1);
}

my @data_extlist = qw|.xls .xlsx .txt|;
my @extlist = qw|.tar .tar.gz .tgz .gz .Z .zip .bz2 .tar.bz2 .tbz .lzma .xz .tar.xz .txz|;
push(@extlist,@data_extlist);

my $query = CGI->new;
my @params = $query->param();
my %PARAMS = ();
foreach my $param (@params){
	$PARAMS{$param} = defined $query->param($param) ? $query->param($param) : undef;
	$PARAMS{$param} = undef if(defined $PARAMS{$param} && length($PARAMS{$param})==0);
}

if($query->cgi_error) {
	$RTN->{'msg'} = &cgi_lib::common::decodeUTF8($query->cgi_error);
	&gzip_json($RTN);
	exit 0;
}

my $old_umask = umask(0);
my $out_path = &catdir($FindBin::Bin,'temp');
unless(-e $out_path){
	&File::Path::mkpath($out_path,0,0777);
	chmod 0777,$out_path;
}

my $time_md5;
if(exists $PARAMS{'sessionID'} && defined $PARAMS{'sessionID'} && length $PARAMS{'sessionID'}){
	$time_md5 = $PARAMS{'sessionID'};
}else{
	use Digest::MD5;
	use Time::HiRes;
	$time_md5 = &Digest::MD5::md5_hex(&Time::HiRes::time());
}
my $params_file = &catfile($out_path,qq|$time_md5.json|);
if(exists $PARAMS{'sessionID'} && defined $PARAMS{'sessionID'} && length $PARAMS{'sessionID'}){
	$RTN = &cgi_lib::common::readFileJSON($params_file);
	if($RTN->{'progress'}->{'msg'} =~ /^end$/i || $RTN->{'progress'}->{'msg'} =~ /error/i){
		&cgi_lib::common::message(&cgi_lib::common::encodeJSON($RTN,1),$LOG);
		&cgi_lib::common::message($RTN->{'file'},$LOG);
		my $dir;
		$dir = &File::Basename::dirname($RTN->{'file'}) if(exists $RTN->{'file'} && defined $RTN->{'file'} && length $RTN->{'file'});
		&cgi_lib::common::message($dir,$LOG) if(defined $dir);
		&File::Path::rmtree($dir) if(defined $dir && length $dir && -e $dir && -d $dir);
		unlink $params_file if(-e $params_file && -f $params_file);
	}
	delete $RTN->{'file'};
	&gzip_json($RTN);
	exit 0;
}else{
	$RTN->{'sessionID'} = $time_md5;
	$RTN->{'ci_id'} = $PARAMS{'ci_id'} - 0;
	$RTN->{'cmd'} = $PARAMS{'cmd'};
	&cgi_lib::common::writeFileJSON($params_file,$RTN);
}

my $file_fh = $query->upload('file');
unless(defined $file_fh){
	$RTN->{'msg'} = &cgi_lib::common::decodeUTF8($query->cgi_error);
	&gzip_json($RTN);
	exit 0;
}

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $upload_time = sprintf("%04d%02d%02d_%02d%02d%02d_%05d",$year+1900,$mon+1,$mday,$hour,$min,$sec,$$);
my $temp_upload_dir = &catdir($upload_dir,$upload_time);

unless(-e $temp_upload_dir){
	umask(0);
	&File::Path::mkpath($temp_upload_dir,{mode=>0777});
	chmod 0777,$temp_upload_dir;
}

my $upload_file;
if(defined $file_fh){
	my($name,$dir,$ext) = &File::Basename::fileparse(&cgi_lib::common::decodeUTF8(&File::Basename::basename($file_fh)),@extlist);
	$name =~ s/\s/_/g;
	$upload_file = &catfile($temp_upload_dir,"$name$ext");
	&File::Copy::copy($file_fh,$upload_file);
	if(exists $PARAMS{'last'} && defined $PARAMS{'last'} && $PARAMS{'last'} =~ /^[0-9]+$/){
		$PARAMS{'last'} /= 1000;
		utime $PARAMS{'last'},$PARAMS{'last'},$upload_file;
	}
}
$RTN->{'file'} = $upload_file;
&cgi_lib::common::writeFileJSON($params_file,$RTN);

my $prog_basename = qq|batch-$cgi_name|;
my $prog = &catfile($FindBin::Bin,'..','batch',qq|$prog_basename.pl|);
if(-e $prog && -x $prog){
	my $pid = fork;
	if(defined $pid){
		if($pid == 0){
			my $logdir = &getLogDir();
			my $f1 = &catfile($logdir,qq|$prog_basename.log|);
			my $f2 = &catfile($logdir,qq|$prog_basename.err|);
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
#&cgi_lib::common::writeFileJSON($params_file,$RTN);
delete $RTN->{'file'};
&gzip_json($RTN);
