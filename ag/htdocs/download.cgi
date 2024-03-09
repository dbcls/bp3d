#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use File::Basename;
use File::Spec;
use File::Spec::Functions qw(catdir catfile);
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
use File::Temp qw/tempfile tempdir/;

use Cwd;
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'API'),&Cwd::abs_path(&catdir($FindBin::Bin,'..','..','ag-common','lib'));
use cgi_lib::common;
use AG::Representation;

require "common.pl";
require "common_db.pl";

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);

unless(exists $ENV{'REQUEST_METHOD'}){
	$ENV{'HTTP_USER_AGENT'} = qq|Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.94 Safari/537.36|;

	$COOKIE{'ag_annotation.session'} = qq|acb1a41ce38de0eff5969ab9b7d088fb|;
	$FORM{'rep_id'} = qq|BP9334|;
	$FORM{'type'} = qq|art_file|;
	$FORM{'all_downloads'} = 1;
	#|| defined $FORM{'ids'})
}

unless(
	defined $COOKIE{'ag_annotation.session'} &&
	defined $FORM{'rep_id'} &&
	defined $FORM{'type'} &&
	(defined $FORM{'all_downloads'} || defined $FORM{'ids'})
){
	print $query->redirect("./");
#	print qq|Content-type: text/html; charset=UTF-8\n\n|;
	exit;
}

&checkXSS(\%FORM);

my $LOG = &cgi_lib::common::getLogFH(\%FORM,\%COOKIE);

&setDefParams(\%FORM,\%COOKIE);
&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = fileparse($0,@extlist);
#open(LOG,"> $FindBin::Bin/logs/$COOKIE{'ag_annotation.session'}.$cgi_name.$FORM{'type'}.txt");
#flock(LOG,2);
#print $LOG "\n[$logtime]:$0\n";
#foreach my $key (sort keys(%FORM)){
#	print $LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}
#foreach my $key (sort keys(%COOKIE)){
#	print $LOG __LINE__,":\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
#}
#foreach my $key (sort keys(%ENV)){
#	print $LOG __LINE__,":\$ENV{$key}=[",$ENV{$key},"]\n";
#}

my $zip_file = qq|bp3d_polygon_data|;

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
#my $prefix = &catdir($FindBin::Bin,$cgi_name,$$);
my $prefix;
$prefix = &tempdir($cgi_name.'.XXXXXXXXXX', DIR => &catdir($FindBin::Bin,$cgi_name), UNLINK => 1);
unless(exists $ENV{'REQUEST_METHOD'}){
	say STDERR __PACKAGE__.':'.__LINE__.':'.$prefix;
}
$prefix = &catdir($FindBin::Bin,$cgi_name,$$) unless(defined $prefix);

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

unless(-e $prefix){
	my $old_umask = umask(0);
	&File::Path::mkpath($prefix,0,0777);
	umask($old_umask);
}

if(0){

}
else{

	my $params = {
		dbh      => $dbh,
		type     => 'HASH',
		'__LOG__'=> $LOG
	};
	if(exists $FORM{'rep_id'} && defined $FORM{'rep_id'}){
		if(ref $FORM{'rep_id'} eq 'ARRAY'){
			$params->{'rep_ids'} = $FORM{'rep_id'};
		}elsif(length $FORM{'rep_id'}){
			my $rep_id;
			eval{$rep_id = &JSON::XS::decode_json($FORM{'rep_id'});};
			if(defined $rep_id){
				if(ref $rep_id eq 'ARRAY'){
					$params->{'rep_ids'} = $rep_id;
				}else{
					$params->{'rep_id'} = $rep_id;
				}
			}else{
				$params->{'rep_id'} = $FORM{'rep_id'};
			}
		}
	}
	if(exists $FORM{'ids'} && defined $FORM{'ids'}){
		if(ref $FORM{'ids'} eq 'ARRAY'){
			$params->{'ids'} = $FORM{'ids'};
		}elsif(length $FORM{'ids'}){
			my $ids;
			eval{$ids = &JSON::XS::decode_json($FORM{'ids'});};
			if(defined $ids){
				$params->{'ids'} = $ids;
			}else{
				$params->{'ids'} = $FORM{'ids'};
			}
		}
	}
	if(exists $FORM{'exclusion_ids'} && defined $FORM{'exclusion_ids'}){
		if(ref $FORM{'exclusion_ids'} eq 'ARRAY'){
			$params->{'exclusion_ids'} = $FORM{'exclusion_ids'};
		}elsif(length $FORM{'exclusion_ids'}){
			my $exclusion_ids;
			eval{$exclusion_ids = &JSON::XS::decode_json($FORM{'exclusion_ids'});};
			if(defined $exclusion_ids){
				$params->{'exclusion_ids'} = $exclusion_ids;
			}else{
				$params->{'exclusion_ids'} = $FORM{'exclusion_ids'};
			}
		}
	}

	if(exists $FORM{'filename'} && defined $FORM{'filename'} && length $FORM{'filename'}){
		$zip_file = &cgi_lib::common::decodeUTF8($FORM{'filename'});
		$zip_file =~ s/[^A-Za-z0-9]/_/g;
	}else{
		my $rep_ids;
		if(exists $params->{'rep_ids'} && defined $params->{'rep_ids'} && ref $params->{'rep_ids'} eq 'ARRAY'){
			push(@$rep_ids,@{$params->{'rep_ids'}});
		}elsif(exists $params->{'rep_id'} && defined $params->{'rep_id'}){
			push(@$rep_ids,$params->{'rep_id'});
		}
		if(defined $rep_ids){
			my $sql=sprintf(qq|
select
 rep.rep_id,
 ci.ci_name,
 cb.cb_name,
 bul.bul_name_e,
 cdi.cdi_name,
 cdi.cdi_name_e
from
 representation as rep

left join (
 select * from concept_info
) as ci on 
   ci.ci_id=rep.ci_id

left join (
 select * from concept_build
) as cb on 
   cb.ci_id=rep.ci_id and
   cb.cb_id=rep.cb_id

left join (
 select * from buildup_logic
) as bul on 
   bul.bul_id=rep.bul_id

left join (
 select * from concept_data_info
) as cdi on 
   cdi.ci_id=rep.ci_id and
   cdi.cdi_id=rep.cdi_id
where
 rep.rep_id in (%s)
|,join(",",map {qq|'$_'|} @$rep_ids));
			print $LOG __LINE__,":\$sql=[",$sql,"]\n";

			my $rep_id;
			my $ci_name;
			my $cb_name;
			my $bul_name;
			my $cdi_name;
			my $cdi_name_e;

			my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		#	$sth->execute($FORM{'rep_id'}) or die $dbh->errstr;
			$sth->execute() or die $dbh->errstr;
		#	print $LOG __LINE__,":\$sth->rows()=[",$sth->rows(),"]\n";
			my $column_number = 0;
			$sth->bind_col(++$column_number, \$rep_id, undef);
			$sth->bind_col(++$column_number, \$ci_name, undef);
			$sth->bind_col(++$column_number, \$cb_name, undef);
			$sth->bind_col(++$column_number, \$bul_name, undef);
			$sth->bind_col(++$column_number, \$cdi_name, undef);
			$sth->bind_col(++$column_number, \$cdi_name_e, undef);
			$sth->fetch;
			$sth->finish;
			undef $sth;


			$bul_name =~ s/_//g;
			$zip_file = qq|$rep_id\_$ci_name$cb_name\_$bul_name\_$cdi_name\_$cdi_name_e|;
			$zip_file =~ s/[^A-Za-z0-9\_]/_/g;
			$zip_file .= qq|_PARTIAL| if(exists $FORM{'ids'} && defined $FORM{'ids'} && length $FORM{'ids'});
		}
	}

	my $datas = &AG::Representation::get_artfile_obj_format_data($params,$copyright);
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

			$path = &cgi_lib::common::encodeUTF8($path);

			my $file_base_ext = $art_id.'_'.$datas->{$art_id}->{'rep_id'}.'_'.$datas->{$art_id}->{'cdi_name'}.'_'.$datas->{$art_id}->{'cdi_name_e'}.$datas->{$art_id}->{'art_ext'};

			$file_base_ext = &cgi_lib::common::decodeUTF8($file_base_ext);

			my $filename = &cgi_lib::common::decodeUTF8($zip_file);
			$filename .= &cgi_lib::common::decodeUTF8('/') if(length $filename);

#			my $encoded_filename = &cgi_lib::common::encodeUTF8($filename.$file_base_ext);
			my $encoded_filename = &Encode::encode($CODE, $filename.$file_base_ext);
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
