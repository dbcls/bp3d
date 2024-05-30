#!/opt/services/ag/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use File::Basename;
use File::Spec::Functions;
use File::Path;
use JSON::XS;

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI::Cookie;
use HTTP::Date;
use Encode;
use Archive::Zip;
use IO::File;
use DBD::Pg;
use Time::HiRes;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
require "webgl_common.pl";
use cgi_lib::common;

use constant {
	USE_SYMLINK => 0
};

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);

#$FORM{'type'}    = qq|objects|;
#$FORM{'records'} = qq|[{"artg_id":1446,"art_id":"FJ1455","rep_id":"BP14754"}]|;

unless(defined $FORM{'records'} && defined $FORM{'type'}){
	print $query->redirect('./');
	exit;
}
my $records = &cgi_lib::common::decodeJSON($FORM{'records'});
unless(defined $records && ref $records eq 'ARRAY'){
	print $query->redirect('./');
	exit;
}

&checkXSS(\%FORM);
#&setDefParams(\%FORM,\%COOKIE);
#&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
my @extlist = qw|.cgi|;
#my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);
my($log_file,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);
my($epocsec,$microsec) = &Time::HiRes::gettimeofday();
my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);
$log_file .=  sprintf(".%02d%02d%02d.%05d",$hour,$min,$sec,$$);

my $LOG;
open($LOG,">> $log_file");
select($LOG);
$| = 1;
select(STDOUT);


#open(LOG,"> $FindBin::Bin/logs/$COOKIE{'ag_annotation.session'}.$cgi_name.$FORM{'type'}.txt");
#flock(LOG,2);
#print LOG "\n[$logtime]:$0\n";
#foreach my $key (sort keys(%FORM)){
#	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}
#foreach my $key (sort keys(%COOKIE)){
#	print LOG __LINE__,":\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
#}
#foreach my $key (sort keys(%ENV)){
#	print LOG __LINE__,":\$ENV{$key}=[",$ENV{$key},"]\n";
#}

#my $zip_file = qq|bp3d_polygon_data.zip|;
my $zip_file = exists $FORM{'filename'} && defined $FORM{'filename'} && length $FORM{'filename'} ? &_trim(&cgi_lib::common::decodeUTF8($FORM{'filename'})) : '';
$zip_file = sprintf("%04d%02d%02d%02d%02d%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec) unless(defined $zip_file && length $zip_file);
$zip_file .= '.zip';

my $LF = "\n";
my $CODE = "utf8";
if($ENV{'HTTP_USER_AGENT'}=~/Windows/){
	$LF = "\r\n";
	$CODE = "shiftjis";
}elsif($ENV{'HTTP_USER_AGENT'}=~/Macintosh/){
	$LF = "\r";
	$CODE = "shiftjis";
}
my $zip = Archive::Zip->new();
my $mtime=0;
my $copyright_file = &catdir($FindBin::Bin,$cgi_name,qq|copyright.txt|);
my $prefix = &catdir($FindBin::Bin,$cgi_name,$$);

my $header_fmt = <<TEXT;
#
# Compatibility version : %s
# File ID : %s
# Representation ID : %s
# Build-up logic : %s %s %s
# Concept ID : %s
# English name : %s
# Bounds(mm): %s-%s
# Volume(cm3): %f
#
TEXT

my $copyright;
if(-e $copyright_file){
	my $IN;
	if(open($IN,$copyright_file)){
		binmode($IN, ':utf8');
		local $/ = undef;
		$copyright = <$IN>;
		close($IN);
	}
}

{
	umask(0);
	&File::Path::mkpath($prefix,0,0777) unless(-e $prefix);

	my $sth_objects;
	my @art_ids;
	my %hash_art_ids;

	if($FORM{'type'} eq 'pallet'){
		my @R;
		foreach my $r (@$records){
			push(@R,$r) if(exists $r->{'art_id'} && defined $r->{'art_id'} && length $r->{'art_id'});
		}
		$records = [];
		push(@$records,@R);
		$FORM{'type'} = 'objects';
	}
	elsif($FORM{'type'} eq 'folder'){

		my %HASH;
		foreach my $r (@$records){
			$HASH{$r->{'artf_id'}} = undef if(exists $r->{'artf_id'} && defined $r->{'artf_id'} && length $r->{'artf_id'});
		}
		my @artf_ids;
		do{
			@artf_ids = keys(%HASH);
			my $artf_id;
			my $sth = $dbh->prepare(sprintf('select COALESCE(artf_id,0) from art_folder where artf_delcause is null and COALESCE(artf_pid,0) in (%s)',join(',',map {'?'} @artf_ids))) or die $dbh->errstr;
			$sth->execute(@artf_ids) or die $dbh->errstr;
			$sth->bind_col(1, \$artf_id, undef);
			while($sth->fetch){
				next unless(defined $artf_id && length $artf_id);
				$HASH{$artf_id} = undef;
			}
			$sth->finish;
			undef $sth;
		}while(scalar @artf_ids < scalar keys(%HASH));

		@artf_ids = keys(%HASH);
		$records = [];
		my $art_id;
		my $artf_id;
		my $sth = $dbh->prepare(sprintf('select art_id,COALESCE(artf_id,0) from art_folder_file where artff_delcause is null and COALESCE(artf_id,0) in (%s) order by artff_timestamp desc',join(',',map {'?'} @artf_ids))) or die $dbh->errstr;
		$sth->execute(@artf_ids) or die $dbh->errstr;
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$art_id, undef);
		$sth->bind_col(++$column_number, \$artf_id, undef);
		while($sth->fetch){
			next unless(defined $art_id && length $art_id);
			push(@$records,{
				art_id => $art_id,
				artf_id => $artf_id
			});
		}
		$sth->finish;
		undef $sth;
		$FORM{'type'} = 'objects';
	}
	if($FORM{'type'} eq 'objects'){
		foreach my $r (@$records){
#			$hash_art_ids{$r->{'art_id'}} = exists $r->{'artf_id'} && defined $r->{'artf_id'} ? $r->{'artf_id'} : undef if(exists $r->{'art_id'} && defined $r->{'art_id'} && length $r->{'art_id'});

			next unless(exists $r->{'art_id'} && defined $r->{'art_id'} && length $r->{'art_id'});
			my $artf_id = exists $r->{'artf_id'} && defined $r->{'artf_id'} ? $r->{'artf_id'} : undef;
			if(exists $hash_art_ids{$r->{'art_id'}}){
#				next;
				push(@{$hash_art_ids{$r->{'art_id'}}},$artf_id) if(defined $artf_id);
			}else{
				push(@{$hash_art_ids{$r->{'art_id'}}},$artf_id);
			}
		}
		@art_ids = keys(%hash_art_ids);

		if(scalar @art_ids){
			my $sql_objects=<<SQL;
select
 arti.art_id,
 arti.art_name,
 arti.art_ext,
 art.art_data,
 art.art_raw_data,
 EXTRACT(EPOCH FROM arti.art_timestamp) as art_timestamp
from
 art_file_info as arti
left join (
  select art_id,art_data,art_raw_data from art_file
) as art on
   art.art_id=arti.art_id
where
 arti.art_delcause is null and
 arti.art_id in (%s)
SQL
			$sth_objects = $dbh->prepare(sprintf($sql_objects,join(',',map {'?'} @art_ids))) or die $dbh->errstr;
		}
	}

	my $sth;
	$sth = $sth_objects if(defined $sth_objects);
	if(defined $sth){

		my $sth_art_folder = $dbh->prepare(qq|select COALESCE(artf_pid,0),COALESCE(artf_name,'/') from art_folder where artf_delcause is null and COALESCE(artf_id,0)=?|) or die $dbh->errstr;
		my %artf_path;
		my %art_mem;

		$sth->execute(@art_ids) or die $dbh->errstr;
		my $column_number = 0;
		my $art_id;
		my $art_name;
		my $art_ext;
		my $art_data;
		my $art_raw_data;
		my $art_timestamp;
		$sth->bind_col(++$column_number, \$art_id, undef);
		$sth->bind_col(++$column_number, \$art_name, undef);
		$sth->bind_col(++$column_number, \$art_ext, undef);
		$sth->bind_col(++$column_number, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
		$sth->bind_col(++$column_number, \$art_raw_data, { pg_type => DBD::Pg::PG_BYTEA });
		$sth->bind_col(++$column_number, \$art_timestamp, undef);
		while($sth->fetch){
			next unless(defined $art_id && defined $art_ext && defined $art_data && defined $art_timestamp);

			my $file = qq|$art_id$art_ext|;
			my $path = &catfile($prefix,$file);
			unless(-e $path){
				my $OUT;
				open($OUT,"> $path") or die "$!:$path\n";
				flock($OUT,2);
				binmode($OUT, ':utf8');
				print $OUT $copyright if(defined $copyright && length $copyright);
				if(defined $art_raw_data && length $art_raw_data){
					print $OUT $art_raw_data;
				}else{
					print $OUT $art_data;
				}
				close($OUT);
				utime($art_timestamp,$art_timestamp,$path);
			}
			$mtime=$art_timestamp if($mtime<$art_timestamp);

			my $file_base_ext;
			if($art_name =~ /^${art_id}_/){
				$file_base_ext = sprintf(&cgi_lib::common::decodeUTF8('%s%s'),$art_name,$art_ext);
			}else{
				$file_base_ext = sprintf(&cgi_lib::common::decodeUTF8('%s_%s%s'),$art_id,$art_name,$art_ext);
			}
#			my $file_base_ext = sprintf(&cgi_lib::common::decodeUTF8('%s_%s%s'),$art_id,$art_name,$art_ext);

			$path = &cgi_lib::common::encodeUTF8($path);
			if(defined $hash_art_ids{$art_id}){
				foreach my $artf_id (@{$hash_art_ids{$art_id}}){
					unless(defined $artf_id && exists $artf_path{$artf_id} && defined $artf_path{$artf_id}){
						my @artf_names = ();
						if($artf_id!=0){
							my $temp_artf_pid = $artf_id;
							do{
								my $temp_artf_name;
								$sth_art_folder->execute($temp_artf_pid) or die $dbh->errstr;
								$column_number = 0;
								$sth_art_folder->bind_col(++$column_number, \$temp_artf_pid, undef);
								$sth_art_folder->bind_col(++$column_number, \$temp_artf_name, undef);
								$sth_art_folder->fetch;
								$sth_art_folder->finish;
								unshift(@artf_names,$temp_artf_name) if(defined $temp_artf_name);
							}while(defined $temp_artf_pid && $temp_artf_pid ne '0');
						}
						$artf_path{$artf_id} = join('/',@artf_names);
						$artf_path{$artf_id} .= '/' if(length $artf_path{$artf_id});
					}
					if(defined $artf_id){
						if(USE_SYMLINK){
							unless(exists $art_mem{$art_id}){
								$art_mem{$art_id} = $zip->addFile($path,&Encode::encode($CODE, $artf_path{$artf_id}.$file_base_ext));
							}else{
								my $fileName = &Encode::decode($CODE, $art_mem{$art_id}->fileName());
								my $zipName = $artf_path{$artf_id}.$file_base_ext;
								$fileName = &abs2rel($fileName,$artf_path{$artf_id});
								my $member = $zip->addString(&Encode::encode($CODE, $fileName),&Encode::encode($CODE, $zipName));
								$member->setLastModFileDateTimeFromUnix($art_mem{$art_id}->lastModTime());
								$member->{'externalFileAttributes'} = 0xA1FF0000;
							}
						}else{
							$zip->addFile($path,&Encode::encode($CODE, $artf_path{$artf_id}.$file_base_ext));
						}
					}else{
						if(USE_SYMLINK){
							unless(exists $art_mem{$art_id}){
								$art_mem{$art_id} = $zip->addFile($path,&Encode::encode($CODE, $file_base_ext));
							}else{
								my $fileName = &Encode::decode($CODE, $art_mem{$art_id}->fileName());
								my $zipName = $file_base_ext;
								my $member = $zip->addString(&Encode::encode($CODE, $fileName),&Encode::encode($CODE, $zipName));
								$member->setLastModFileDateTimeFromUnix($art_mem{$art_id}->lastModTime());
								$member->{'externalFileAttributes'} = 0xA1FF0000;
							}
						}else{
							$zip->addFile($path,&Encode::encode($CODE, $file_base_ext));
						}
					}
				}
			}else{
				if(USE_SYMLINK){
					unless(exists $art_mem{$art_id}){
						$art_mem{$art_id} = $zip->addFile($path,&Encode::encode($CODE, $file_base_ext));
					}else{
						my $fileName = &Encode::decode($CODE, $art_mem{$art_id}->fileName());
						my $zipName = $file_base_ext;
						my $member = $zip->addString(&Encode::encode($CODE, $fileName),&Encode::encode($CODE, $zipName));
						$member->setLastModFileDateTimeFromUnix($art_mem{$art_id}->lastModTime());
						$member->{'externalFileAttributes'} = 0xA1FF0000;
					}
				}else{
					$zip->addFile($path,&Encode::encode($CODE, $file_base_ext));
				}
			}

		}
		$sth->finish;
		undef $sth;


	}
}
#BPmmm_PARTSNAME

$zip_file = &cgi_lib::common::encodeUTF8($zip_file);

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
