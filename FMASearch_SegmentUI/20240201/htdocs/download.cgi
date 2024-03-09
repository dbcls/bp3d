#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use DBD::Pg;
use JSON::XS;
use File::Spec::Functions qw(catdir catfile);
use File::Temp qw/tempfile tempdir/;
use Encode;
use Archive::Zip;
#$Archive::Zip::UNICODE = 1;

use IO::File;

use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'..','cgi_lib');
use BITS::Config;
use BITS::ConceptArtMap;
require "webgl_common.pl";
use cgi_lib::common;

use constant {
	DEBUG => BITS::Config::DEBUG
};

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);
my($logfile,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

$FORM{$_} = &cgi_lib::common::decodeUTF8($FORM{$_}) for(keys(%FORM));


my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
$logfile .=  sprintf(".%02d%02d%02d.%05d",$hour,$min,$sec,$$);


my $LOG;
if(DEBUG){
	open($LOG,">> $logfile");
	select($LOG);
	$| = 1;
	select(STDOUT);

	flock($LOG,2);
	print $LOG "\n[$logtime]:$0\n";
	&cgi_lib::common::message(\%FORM, $LOG);
}


unless(
	exists $FORM{&BITS::Config::LOCATION_HASH_MDID_KEY()} && defined $FORM{&BITS::Config::LOCATION_HASH_MDID_KEY()} && $FORM{&BITS::Config::LOCATION_HASH_MDID_KEY()} =~ /^[0-9]+$/ &&
	exists $FORM{&BITS::Config::LOCATION_HASH_MVID_KEY()} && defined $FORM{&BITS::Config::LOCATION_HASH_MVID_KEY()} && $FORM{&BITS::Config::LOCATION_HASH_MVID_KEY()} =~ /^[0-9]+$/ &&
	exists $FORM{&BITS::Config::LOCATION_HASH_CIID_KEY()} && defined $FORM{&BITS::Config::LOCATION_HASH_CIID_KEY()} && $FORM{&BITS::Config::LOCATION_HASH_CIID_KEY()} =~ /^[0-9]+$/ &&
	exists $FORM{&BITS::Config::LOCATION_HASH_CBID_KEY()} && defined $FORM{&BITS::Config::LOCATION_HASH_CBID_KEY()} && $FORM{&BITS::Config::LOCATION_HASH_CBID_KEY()} =~ /^[0-9]+$/ &&
	exists $FORM{&BITS::Config::LOCATION_HASH_IDS_KEY()}  && defined $FORM{&BITS::Config::LOCATION_HASH_IDS_KEY()}  && length $FORM{&BITS::Config::LOCATION_HASH_IDS_KEY()}
){
	&cgi_lib::common::message("", $LOG) if(defined $LOG);
	&cgi_lib::common::printNotFound();
}

my $md_id = $FORM{&BITS::Config::LOCATION_HASH_MDID_KEY()} - 0;
my $mv_id = $FORM{&BITS::Config::LOCATION_HASH_MVID_KEY()} - 0;
my $mr_id = ($FORM{&BITS::Config::LOCATION_HASH_MRID_KEY()} // 1) - 0;
my $ci_id = $FORM{&BITS::Config::LOCATION_HASH_CIID_KEY()} - 0;
my $cb_id = $FORM{&BITS::Config::LOCATION_HASH_CBID_KEY()} - 0;

my $zip_file = sprintf("%04d%02d%02d%02d%02d%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);

my $LF = "\n";
my $CODE = "utf8";
#=pod
if(exists $ENV{'HTTP_USER_AGENT'} && defined $ENV{'HTTP_USER_AGENT'}){
	if($ENV{'HTTP_USER_AGENT'}=~/Windows/){
		$LF = "\r\n";
		$CODE = "shiftjis";
	}elsif($ENV{'HTTP_USER_AGENT'}=~/Macintosh/){
		$LF = "\r";
		$CODE = "shiftjis";
	}
}
#=cut
my $zip = Archive::Zip->new();
my $mtime=0;
my $copyright_file = &catdir($FindBin::Bin,$cgi_name,qq|copyright.txt|);
my $prefix;
$prefix = &tempdir('.'.$cgi_name.'.XXXXXXXXXX', DIR => &catdir($FindBin::Bin,$cgi_name,'tmp'), UNLINK => 1);
$prefix = &catdir($FindBin::Bin,$cgi_name,$$) unless(defined $prefix);
&File::Path::make_path($prefix,{chmod => 0700}) unless(-e $prefix && -d $prefix);

my $copyright;
if(-e $copyright_file){
	my $IN;
	if(open($IN,$copyright_file)){
		my $old = $/;
		$/ = undef;
		$copyright = <$IN>;
		$/ = $old;
		close($IN);
	}
}

#&File::Path::rmtree($prefix,{safe => 1}) if(-e $prefix);
#exit;


if(0){

}
else{

	my $params = {
		dbh      => $dbh,
		md_id    => $md_id,
		mv_id    => $mv_id,
		mr_id    => $mr_id,
		ci_id    => $ci_id,
		cb_id    => $cb_id,
		type     => 'HASH',
		'__LOG__'=> $LOG
	};
	if(exists $FORM{&BITS::Config::LOCATION_HASH_IDS_KEY()} && defined $FORM{&BITS::Config::LOCATION_HASH_IDS_KEY()}){
		my $ids = &cgi_lib::common::decodeJSON($FORM{&BITS::Config::LOCATION_HASH_IDS_KEY()});
		if(defined $ids){
			$params->{&BITS::Config::LOCATION_HASH_IDS_KEY()} = $ids;
		}else{
			$params->{&BITS::Config::LOCATION_HASH_IDS_KEY()} = $FORM{&BITS::Config::LOCATION_HASH_IDS_KEY()};
		}
	}
	if(exists $FORM{'filename'} && defined $FORM{'filename'} && length $FORM{'filename'}){
		$zip_file = &cgi_lib::common::decodeUTF8($FORM{'filename'});
		$zip_file =~ s/[^A-Za-z0-9]/_/g;
	}
	my $filename = &cgi_lib::common::decodeUTF8($zip_file);
	$filename .= &cgi_lib::common::decodeUTF8('/') if(length $filename);

	my $datas = &BITS::ConceptArtMap::get_artfile_obj_format_data($params,$copyright);
	if(defined $datas){
		foreach my $art_id (keys(%$datas)){

			my $file = $art_id.$datas->{$art_id}->{'art_ext'};
			my $path = &catfile($prefix,$file);

			unless(-e $path){
				my $OUT;
				open($OUT,"> $path") or die "$!:$path\n";
				flock($OUT,2);
				binmode($OUT);
				print $OUT $datas->{$art_id}->{'head'};
				print $OUT $datas->{$art_id}->{'body'};
				close($OUT);
				utime($datas->{$art_id}->{'art_entry'},$datas->{$art_id}->{'art_entry'},$path);
			}

			$mtime = $datas->{$art_id}->{'art_entry'} if($mtime<$datas->{$art_id}->{'art_entry'});

#			$path = &cgi_lib::common::encodeUTF8($path);

			my $artc_id = $datas->{$art_id}->{'artc_id'};
			my $cdi_name_e = $datas->{$art_id}->{'cdi_name_e'};
			$cdi_name_e =~ s/[^A-Za-z0-9]+/_/g;

#			my $file_base_ext = $art_id.'_'.$datas->{$art_id}->{'cdi_name'}.'_'.$cdi_name_e.$datas->{$art_id}->{'art_ext'};
			my $file_base_ext = (defined $artc_id ? $artc_id : $art_id).'_'.$datas->{$art_id}->{'cdi_name'}.'_'.$cdi_name_e.$datas->{$art_id}->{'art_ext'};

			$file_base_ext = &cgi_lib::common::decodeUTF8($file_base_ext);

#			my $encoded_filename = &cgi_lib::common::encodeUTF8($filename.$file_base_ext);
			my $encoded_filename = &Encode::encode($CODE, $filename.$file_base_ext);
#			my $encoded_filename = $filename.$file_base_ext;
			my $zip_mem = $zip->addFile($path,$encoded_filename);


		}
	}


	$zip_file .= qq|.zip|;
#	&utf8::encode($zip_file) if(&utf8::is_utf8($zip_file));

	$zip_file = &cgi_lib::common::encodeUTF8($zip_file);

}

my $stdout = IO::File->new->fdopen(fileno(STDOUT), "w") || croak($!);
$stdout->printflush("Content-Type: application/zip\n");
$stdout->printflush("Content-Disposition: filename=$zip_file\n");
$stdout->printflush("Last-Modified: ".&HTTP::Date::time2str($mtime)."\n");
$stdout->printflush("Pragma: no-cache\n\n");
$zip->writeToFileHandle($stdout, 0);
$stdout->close;

&File::Path::rmtree($prefix,{safe => 1}) if(-e $prefix);

#print qq|Content-type: text/html; charset=UTF-8\n\n|;
#close(LOG);
