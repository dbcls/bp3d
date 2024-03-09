#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
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

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
require "webgl_common.pl";
use cgi_lib::common;

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
my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);
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
$zip_file .= ".zip";

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

	my $art_id;
	my $art_name;
	my $art_ext;
	my $art_data;
	my $art_timestamp;
	my $artg_name;
	my $artg_timestamp;

	my $zip_prefix;

	my $sth_groups;
	my $sth_objects;

	if($FORM{'type'} eq 'pallet'){
		my $sql=<<SQL;
select distinct
 arti.art_id,
 arti.artg_id
from
 representation_art as repa
left join (
 select * from art_file_info where art_delcause is null
) as arti on
   arti.art_id=repa.art_id
where
 rep_id=?
SQL
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		my @R;
		foreach my $r (@$records){
			if(defined $r->{'artg_id'} && defined $r->{'art_id'}){
				push(@R,$r);
				next;
			}
			next unless(defined $r->{'rep_id'});

			$sth->execute($r->{'rep_id'}) or die $dbh->errstr;
			my $art_id;
			my $artg_id;
			my $column_number = 0;
			$sth->bind_col(++$column_number, \$art_id, undef);
			$sth->bind_col(++$column_number, \$artg_id, undef);
			while($sth->fetch){
				next unless(defined $art_id && defined $artg_id);
				push(@R,{
					art_id => $art_id,
					artg_id => $artg_id,
					rep_id => $r->{'rep_id'},
				});
			}
			$sth->finish;
		}
		undef $sth;

		$records = [];
		push(@$records,@R);
		$FORM{'type'} = 'objects';
	}

	if($FORM{'type'} eq 'groups'){
		my $artg_ids;
		my $artg_ids_temp = {};
		foreach my $r (@$records){
			$artg_ids_temp->{$r->{'artg_id'}} = undef if(defined $r->{'artg_id'});
		}
		$artg_ids = join(',',keys(%$artg_ids_temp)) if(scalar keys(%$artg_ids_temp) > 0);
		undef $artg_ids_temp;

		if(defined $artg_ids){
			my $sql_groups=<<SQL;
select
 arti.art_id,
 arti.art_name,
 arti.art_ext,
 art.art_data,
 EXTRACT(EPOCH FROM arti.art_timestamp) as art_timestamp,
 artg_name,
 EXTRACT(EPOCH FROM artg_timestamp) as artg_timestamp
from
 (
   select
     art_id,
     art_name,
     art_ext,
     art_timestamp,
     harti.artg_id,
     art_delcause,
     hist_event,
     hist_serial,
     artg_name,
     artg_timestamp
   from
     history_art_file_info as harti

   left join (
      select * from art_group
    ) as artg on
       artg.artg_id=harti.artg_id

   where
    atrg_use AND
    artg_delcause is null AND
    (art_id,harti.artg_id,hist_serial) in (
      select
        art_id,artg_id,max(hist_serial)
      from
        history_art_file_info
      where
        artg_id in ($artg_ids)
      group by
        art_id,artg_id
    ) AND
    hist_event in (
      select he_id from history_event where he_name in ('INSERT','UPDATE')
    )
 ) as arti

left join (
  select art_id,art_data from art_file
) as art on
   art.art_id=arti.art_id

SQL
			$sth_groups = $dbh->prepare($sql_groups) or die $dbh->errstr;
		}
	}


	elsif($FORM{'type'} eq 'objects'){
		my $art_ids;
		my $artg_ids_temp = {};
		foreach my $r (@$records){
			$artg_ids_temp->{$r->{'artg_id'}}->{$r->{'art_id'}} = undef if(defined $r->{'artg_id'} && defined $r->{'art_id'});
		}
		if(scalar keys(%$artg_ids_temp) > 0){
			my @temp;
			foreach my $artg_id (keys(%$artg_ids_temp)){
				foreach my $art_id (keys(%{$artg_ids_temp->{$artg_id}})){
					push(@temp,qq|($artg_id,'$art_id')|);
				}
			}
			$art_ids = join(',',@temp);
			undef @temp;
		}
		undef $artg_ids_temp;

		if(defined $art_ids){
			my $sql_objects=<<SQL;
select
 arti.art_id,
 arti.art_name,
 arti.art_ext,
 art.art_data,
 EXTRACT(EPOCH FROM arti.art_timestamp) as art_timestamp,
 artg_name,
 EXTRACT(EPOCH FROM artg_timestamp) as artg_timestamp
from
 (
   select
     art_id,
     art_name,
     art_ext,
     art_timestamp,
     harti.artg_id,
     art_delcause,
     hist_event,
     hist_serial,
     artg_name,
     artg_timestamp
   from
     history_art_file_info as harti

   left join (
      select * from art_group
    ) as artg on
       artg.artg_id=harti.artg_id

   where
    atrg_use AND
    artg_delcause is null AND
    (art_id,harti.artg_id,hist_serial) in (
      select
        art_id,artg_id,max(hist_serial)
      from
        history_art_file_info
      where
        (artg_id,art_id) in ($art_ids)
      group by
        art_id,artg_id
    ) AND
    hist_event in (
      select he_id from history_event where he_name in ('INSERT','UPDATE')
    )
 ) as arti

left join (
  select art_id,art_data from art_file
) as art on
   art.art_id=arti.art_id

SQL
			$sth_objects = $dbh->prepare($sql_objects) or die $dbh->errstr;
		}
	}

	my $sth;
	if(defined $sth_groups){
		$sth = $sth_groups;
	}elsif(defined $sth_objects){
		$sth = $sth_objects;
	}
	if(defined $sth){
		$sth->execute() or die $dbh->errstr;
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$art_id, undef);
		$sth->bind_col(++$column_number, \$art_name, undef);
		$sth->bind_col(++$column_number, \$art_ext, undef);
		$sth->bind_col(++$column_number, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
		$sth->bind_col(++$column_number, \$art_timestamp, undef);
		$sth->bind_col(++$column_number, \$artg_name, undef);
		$sth->bind_col(++$column_number, \$artg_timestamp, undef);
		while($sth->fetch){
			next unless(defined $art_id && defined $art_ext && defined $art_data && defined $art_timestamp && defined $artg_name && defined $artg_timestamp);

			my $file = qq|$art_id$art_ext|;
			my $path = &catfile($prefix,$file);
			unless(-e $path){
				my $OUT;
				open($OUT,"> $path") or die "$!:$path\n";
				flock($OUT,2);
				binmode($OUT, ':utf8');
				print $OUT $copyright if(defined $copyright);
=pod
			print $OUT sprintf($header_fmt,
									$art_mv_name_e,
									$art_id,
									$art_rep_id,
									$ci_name,$cb_name,$bul_name,
									$art_cdi_name,
									$art_cdi_name_e,
									sprintf("(%f,%f,%f)",$art_xmin,$art_ymin,$art_zmin),
									sprintf("(%f,%f,%f)",$art_xmax,$art_ymax,$art_zmax),
									$art_volume);
=cut
				print $OUT $art_data;
				close($OUT);
				utime($art_timestamp,$art_timestamp,$path);
			}
			$mtime=$artg_timestamp if($mtime<$artg_timestamp);


#		my $file_base_ext = &catfile($zip_prefix,$file);
#			my $file_base_ext = qq|$artg_name/$art_id$art_ext|;

			my $file_base_ext;
			if($art_name =~ /^${art_id}_/){
				$file_base_ext = sprintf(&cgi_lib::common::decodeUTF8('%s%s'),$art_name,$art_ext);
			}else{
				$file_base_ext = sprintf(&cgi_lib::common::decodeUTF8('%s_%s%s'),$art_id,$art_name,$art_ext);
			}
#			my $file_base_ext = &catfile($artg_name,sprintf(&cgi_lib::common::decodeUTF8('%s_%s%s'),$art_id,$art_name,$art_ext));

			$file_base_ext = &cgi_lib::common::decodeUTF8($file_base_ext);

			$path = &cgi_lib::common::encodeUTF8($path);
			my $encoded_filename = &cgi_lib::common::encodeUTF8($file_base_ext);
			$encoded_filename = &Encode::encode($CODE, $file_base_ext);
			my $zip_mem = $zip->addFile($path,$encoded_filename);

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
