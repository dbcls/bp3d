#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';


use JSON::XS;
use File::Basename;
use Cwd qw(abs_path);
use File::Spec::Functions qw(abs2rel rel2abs catdir catfile splitdir);
use CGI;
use CGI::Carp qw(fatalsToBrowser);
#use CGI::Carp::DebugScreen ( debug => 1 );
use Data::Dumper;
use DBD::Pg;
use POSIX;
use List::Util;
use Hash::Merge;
use Time::HiRes;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;

use BITS::Config;
use BITS::VTK;
use BITS::Voxel;
use BITS::ConceptArtMapModified;

use obj2deci;
require "webgl_common.pl";
use cgi_lib::common;
use AG::login;
use BITS::ConceptArtMapModified;

my $query = CGI->new;
my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
#my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);
$FORM{$_} = &cgi_lib::common::decodeUTF8($FORM{$_}) for(sort keys(%FORM));
$COOKIE{$_} = &cgi_lib::common::decodeUTF8($COOKIE{$_}) for(sort keys(%COOKIE));
if(exists($COOKIE{'ag_annotation.session'})){
	my $session_info = {};
	$session_info->{'PARAMS'}->{$_} = $FORM{$_} for(sort keys(%FORM));
	$session_info->{'COOKIE'}->{$_} = $COOKIE{$_} for(sort keys(%COOKIE));
	&AG::login::setSessionHistory($session_info);
}

my($log_file,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

#my @extlist = qw|.cgi|;
#my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);

my $t0 = [&Time::HiRes::gettimeofday()];
my($epocsec,$microsec) = &Time::HiRes::gettimeofday();
my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);

#my $log_file = qq|$FindBin::Bin/logs/$cgi_name.txt|;
$log_file .= qq|.$FORM{'cmd'}| if(exists $FORM{'cmd'});

$log_file .= qq|.artg_ids| if(exists $FORM{'artg_ids'});
$log_file .= qq|.art_datas| if(exists $FORM{'art_datas'});
#$log_file .=  sprintf(".%04d%02d%02d%02d",$year+1900,$mon+1,$mday,$hour);
$log_file .=  sprintf(".%02d%02d%02d.%05d",$hour,$min,$sec,$$);

my $LOG;
open($LOG,">> $log_file");
select($LOG);
$| = 1;
select(STDOUT);

if(defined $LOG){
	&cgi_lib::common::message(sprintf("\n%04d:%04d/%02d/%02d %02d:%02d:%02d.%d",__LINE__,$year+1900,$mon+1,$mday,$hour,$min,$sec,$microsec), $LOG);
	&cgi_lib::common::message(\%ENV, $LOG);
	&cgi_lib::common::message(\%FORM, $LOG);

	#$epocsec = &Time::HiRes::tv_interval($t0);
	&cgi_lib::common::dumper($epocsec, $LOG);

}

$FORM{'cmd'} = 'read' unless(defined $FORM{'cmd'});
#$FORM{'start'} = 0 unless(defined $FORM{'start'});
#$FORM{'limit'} = 25 unless(defined $FORM{'limit'});

#$FORM{'name'} = qq|120406_liver_divided01_obj|;

#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $DATAS = {
	'datas' => [],
	'total' => 0,
	'success' => JSON::XS::false
};

my $ci_id=$FORM{'ci_id'};
my $cb_id=$FORM{'cb_id'};
my $md_id=$FORM{'md_id'};
my $mv_id=$FORM{'mv_id'};
my $crl_id=$FORM{'crl_id'};

$md_id=1 unless(defined $md_id && $md_id =~ /^[1-9][0-9]*$/);
unless(defined $mv_id && $mv_id =~ /^[1-9][0-9]*$/){
	$mv_id = undef;
	$ci_id = undef;
	$cb_id = undef;
	my $sth_mv;
	if(defined $FORM{'mv_id'} && $FORM{'mv_id'} =~ /^\-[1-9][0-9]*$/){
		$sth_mv = $dbh->prepare("select mv_id from model_version where mv_delcause is null and mv_use and md_id=? order by mv_id desc limit 2") or die $dbh->errstr;
		$sth_mv->execute($md_id) or die $dbh->errstr;
		if($sth_mv->rows()>1){
			$sth_mv->bind_col(1, \$mv_id, undef);
			while($sth_mv->fetch){}
		}
		$sth_mv->finish;
		undef $sth_mv;
	}else{
		$sth_mv = $dbh->prepare("select max(mv_id) from model_version where mv_delcause is null and mv_use and md_id=?") or die $dbh->errstr;
		$sth_mv->execute($md_id) or die $dbh->errstr;
		$sth_mv->bind_col(1, \$mv_id, undef);
		$sth_mv->fetch;
		$sth_mv->finish;
		undef $sth_mv;
	}
	if(defined $mv_id){
		$sth_mv = $dbh->prepare("select ci_id,cb_id from model_version where md_id=? and mv_id=?") or die $dbh->errstr;
		$sth_mv->execute($md_id,$mv_id) or die $dbh->errstr;
		$sth_mv->bind_col(1, \$ci_id, undef);
		$sth_mv->bind_col(2, \$cb_id, undef);
		$sth_mv->fetch;
		$sth_mv->finish;
		undef $sth_mv;
	}
}

unless(defined $ci_id && defined $cb_id && defined $md_id && defined $mv_id){
	$DATAS->{'success'} = JSON::XS::true;
	&cgi_lib::common::printContentJSON($DATAS,\%FORM);
	close($LOG) if(defined $LOG);
	exit;
}

$crl_id = 0 unless(defined $crl_id);
#$crl_id = 3 unless(defined $crl_id);

if(defined $LOG){
	&cgi_lib::common::message('$md_id='.$md_id, $LOG);
	&cgi_lib::common::message('$mv_id='.$mv_id, $LOG);
	&cgi_lib::common::message('$ci_id='.$ci_id, $LOG);
	&cgi_lib::common::message('$cb_id='.$cb_id, $LOG);
	&cgi_lib::common::message('$crl_id='.$crl_id, $LOG);
}
$FORM{'ci_id'}=$ci_id;
$FORM{'cb_id'}=$cb_id;
$FORM{'md_id'}=$md_id;
$FORM{'mv_id'}=$mv_id;
$FORM{'crl_id'}=$crl_id;


#umask(0);
my $freeze_mapping_abs_path = &catdir($FindBin::Bin,'freeze_mapping');
&File::Path::mkpath($freeze_mapping_abs_path,{mode=>0500}) unless(-e $freeze_mapping_abs_path);
my $freeze_mapping_proc_path = &catfile($freeze_mapping_abs_path,'.freeze_mapping');
chmod 0500, $freeze_mapping_abs_path unless(-e $freeze_mapping_proc_path && -f $freeze_mapping_proc_path && -s $freeze_mapping_proc_path);


#if($FORM{'cmd'} eq 'read' && exists $FORM{'art_id'} && defined $FORM{'art_id'}){
if($FORM{'cmd'} eq 'read'){

	my $sql=<<SQL;
SELECT
 fm_id,
 EXTRACT(EPOCH FROM fm_timestamp) as fm_timestamp,
 fm_point,
 fm_comment,
 fm_status
FROM
 freeze_mapping
WHERE
 fm_delcause is null
ORDER BY
 fm_id
SQL

	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$DATAS->{'total'} = $sth->rows();
	my $column_number = 0;
	my $fm_id;
	my $fm_timestamp;
	my $fm_point;
	my $fm_comment;
	my $fm_status;
	$sth->bind_col(++$column_number, \$fm_id, undef);
	$sth->bind_col(++$column_number, \$fm_timestamp, undef);
	$sth->bind_col(++$column_number, \$fm_point, undef);
	$sth->bind_col(++$column_number, \$fm_comment, undef);
	$sth->bind_col(++$column_number, \$fm_status, undef);
	while($sth->fetch){
		push(@{$DATAS->{'datas'}},{
			fm_id => $fm_id,
			fm_timestamp => $fm_timestamp - 0,
			fm_point => $fm_point ? JSON::XS::true : JSON::XS::false,
			fm_comment => $fm_comment,
			fm_status => $fm_status,
		});
	}
	$sth->finish;
	undef $sth;


	$DATAS->{'success'} = JSON::XS::true;
}
elsif($FORM{'cmd'} eq 'create'){
	$DATAS->{'pid'} = &cmd_create(%FORM, LOG=>$LOG);
	$DATAS->{'success'} = exists $DATAS->{'pid'} && defined $DATAS->{'pid'} ? JSON::XS::true : JSON::XS::false;
}
elsif($FORM{'cmd'} eq 'pregress'){
	my $rtn = &cmd_create(%FORM, LOG=>$LOG);
	if(defined $rtn && ref $rtn eq 'HASH'){
		foreach my $key (keys(%$rtn)){
			$DATAS->{$key} = $rtn->{$key};
		}
	}
}
elsif(exists $FORM{'datas'} && defined $FORM{'datas'} && length $FORM{'datas'}){
	my $datas = &cgi_lib::common::decodeJSON($FORM{'datas'});
	if(defined $datas && ref $datas eq 'ARRAY' && scalar @$datas){
		$dbh->{'AutoCommit'} = 0;
		$dbh->{'RaiseError'} = 1;
		eval{
			my $sth;
			if($FORM{'cmd'} eq 'create'){
				$sth = $dbh->prepare('INSERT INTO freeze_mapping (fm_timestamp,fm_point,fm_comment) VALUES (?,?,?) RETURNING fm_id,EXTRACT(EPOCH FROM fm_timestamp)') or die $dbh->errstr;
			}
			elsif($FORM{'cmd'} eq 'update'){
				$sth = $dbh->prepare('UPDATE freeze_mapping SET fm_point=?,fm_comment=?,fm_modified=now() WHERE fm_id=?') or die $dbh->errstr;
			}
			elsif($FORM{'cmd'} eq 'destroy'){
				$sth = $dbh->prepare('DELETE FROM freeze_mapping WHERE fm_id=? RETURNING EXTRACT(EPOCH FROM fm_timestamp)') or die $dbh->errstr;
			}
			foreach my $data (@$datas){
				if($FORM{'cmd'} eq 'create'){
					use Archive::Zip qw( :ERROR_CODES );

					if($data->{'fm_point'}==JSON::XS::true){
						$dbh->do('UPDATE freeze_mapping SET fm_point=false') or die $dbh->errstr;
					}

					$sth->execute($data->{'fm_timestamp'},$data->{'fm_point'},$data->{'fm_comment'}) or die $dbh->errstr;
					$DATAS->{'total'} += $sth->rows();
					my $column_number = 0;
					my $fm_id;
					my $fm_timestamp;
					$sth->bind_col(++$column_number, \$fm_id, undef);
					$sth->bind_col(++$column_number, \$fm_timestamp, undef);
					$sth->fetch;
					$sth->finish;
					undef $sth;

					chmod 0700, $freeze_mapping_abs_path;

					my $OUT;
					open($OUT, ">> $freeze_mapping_proc_path") or die "$! [$freeze_mapping_proc_path]";
					flock($OUT, 2);
					say $OUT $$;
					close($OUT);

					my $out_path = &catdir($freeze_mapping_abs_path,".$$");
					&File::Path::rmtree($out_path) if(-e $out_path);
					&File::Path::mkpath($out_path);

					use BITS::ExportConceptArtMap;
					my $zip = &BITS::ExportConceptArtMap::exec($dbh,\%FORM,$out_path,$LOG);

					&cgi_lib::common::message('',$LOG) if(defined $LOG);

					my ($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime($fm_timestamp);
					my @weekly = ('Sun', 'Mon', 'Tue', 'Wed', 'Thr', 'Fri', 'Sut');
					my $file = sprintf("freeze_mapping_%04d%02d%02d%02d%02d%02d", $year+1900,$month+1,$mday,$hour,$min,$sec);
					my $zip_file = &catfile($freeze_mapping_abs_path,qq|$file.zip|);

					&cgi_lib::common::message('',$LOG) if(defined $LOG);

					die 'write error' unless($zip->writeToFileNamed($zip_file) == AZ_OK);

					&cgi_lib::common::message('',$LOG) if(defined $LOG);

					undef $zip;
					chmod 0400, $zip_file;
					utime $fm_timestamp, $fm_timestamp, $zip_file or die $!;

					&cgi_lib::common::message('',$LOG) if(defined $LOG);

					open($OUT, "+< $freeze_mapping_proc_path") or die "$! [$freeze_mapping_proc_path]";
					flock($OUT, 2);
					local $/ = undef;
					my @PROC = grep {$_ != $$} split(/[\r\n]+/,<$OUT>);
					my $proc = join("\n",@PROC);
					if(length $proc){
						$proc .= "\n";
						print $OUT $proc;
						truncate $OUT,length($proc);
					}else{
						truncate $OUT,0;
					}
					close($OUT);

					&cgi_lib::common::message('',$LOG) if(defined $LOG);

					&File::Path::rmtree($out_path) if(-e $out_path);
#					chmod 0500, $freeze_mapping_abs_path;
					unless(-e $freeze_mapping_proc_path && -f $freeze_mapping_proc_path && -s $freeze_mapping_proc_path){
						chmod 0500, $freeze_mapping_abs_path;
						unlink $freeze_mapping_proc_path if(-e $freeze_mapping_proc_path && -f $freeze_mapping_proc_path);
					}

					&cgi_lib::common::message('',$LOG) if(defined $LOG);

					last;
				}
				elsif($FORM{'cmd'} eq 'update'){
					if($data->{'fm_point'}==JSON::XS::true){
						$dbh->do('UPDATE freeze_mapping SET fm_point=false') or die $dbh->errstr;
					}
					$sth->execute($data->{'fm_point'},$data->{'fm_comment'},$data->{'fm_id'}) or die $dbh->errstr;
					$sth->finish;
					$DATAS->{'total'}++;
				}
				elsif($FORM{'cmd'} eq 'destroy'){
					$sth->execute($data->{'fm_id'}) or die $dbh->errstr;
					my $column_number = 0;
					my $fm_timestamp;
					$sth->bind_col(++$column_number, \$fm_timestamp, undef);
					$sth->fetch;
					$sth->finish;

					my ($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime($fm_timestamp);
					my @weekly = ('Sun', 'Mon', 'Tue', 'Wed', 'Thr', 'Fri', 'Sut');
					my $file = sprintf("freeze_mapping_%04d%02d%02d%02d%02d%02d", $year+1900,$month+1,$mday,$hour,$min,$sec);
					my $zip_file = &catfile($freeze_mapping_abs_path,qq|$file.zip|);
					if(-e $freeze_mapping_abs_path){
						chmod 0700, $freeze_mapping_abs_path;
						unlink $zip_file if(-e $zip_file);
						chmod 0500, $freeze_mapping_abs_path;
					}

					$DATAS->{'total'}++;
				}
				else{
					next;
				}
			}
			$dbh->commit;
			undef $sth;
			$DATAS->{'success'} = JSON::XS::true;
		};
		if($@){
			$DATAS->{'success'} = JSON::XS::false;
			$DATAS->{'total'} = 0;
			$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8($@);
			$dbh->rollback;
		}
		$dbh->{'AutoCommit'} = 1;
		$dbh->{'RaiseError'} = 0;
	}
	else{
		$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8(qq|JSON形式が違います|);
	}
}
elsif($FORM{'cmd'} eq 'download'){
	my $zip_file;
	if(exists $FORM{'fm_id'} && defined $FORM{'fm_id'} && $FORM{'fm_id'} =~ /^[0-9]+$/){
		my $sth = $dbh->prepare('SELECT EXTRACT(EPOCH FROM fm_timestamp) FROM freeze_mapping WHERE fm_id=?') or die $dbh->errstr;
		$sth->execute($FORM{'fm_id'}) or die $dbh->errstr;
		my $column_number = 0;
		my $fm_timestamp;
		$sth->bind_col(++$column_number, \$fm_timestamp, undef);
		$sth->fetch;
		$sth->finish;
		if(defined $fm_timestamp && $fm_timestamp =~ /^[0-9]+$/){
			my ($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime($fm_timestamp);
			my @weekly = ('Sun', 'Mon', 'Tue', 'Wed', 'Thr', 'Fri', 'Sut');
			my $file = sprintf("freeze_mapping_%04d%02d%02d%02d%02d%02d", $year+1900,$month+1,$mday,$hour,$min,$sec);
			$zip_file = &catfile($freeze_mapping_abs_path,qq|$file.zip|);
		}
	}
	if(defined $zip_file && -e $zip_file){
		my $zip_rel_file = &abs2rel($zip_file,$FindBin::Bin);
		print "Location: $zip_rel_file\n\n";
		exit;
=pod
		my($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,$atime,$mtime,$ctime,$blksize,$blocks) = stat($zip_file);
		my $filename = &File::Basename::basename($zip_file);
		$filename = &cgi_lib::common::encodeUTF8($filename);

		print "Pragma: no-cache\n";
		print "Content-Type: application/zip\n";
		print "Content-Disposition: filename=$filename\n";
		print "Last-Modified: ".&HTTP::Date::time2str($mtime)."\n";
		print "Accept-Ranges: bytes\n";
		print "Content-Length: $size\n";
		print "Pragma: no-cache\n";
		print "\n";
		binmode(STDOUT);
		open(my $OUT, zip_file) or die "$! [zip_file]";
		binmode($OUT);
		flock($OUT, 1);
=cut


	}else{
		&cgi_lib::common::printNotFound();
	}
}
else{
	$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8(qq|JSON形式が違います|);
}

#$epocsec = &Time::HiRes::tv_interval($t0);
#($sec,$min) = localtime($epocsec);
&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

#my $json = &cgi_lib::common::encodeJSON($DATAS);
#print $json;
&gzip_json($DATAS);
#print $LOG $json,"\n";
#print $LOG __LINE__.":",&Data::Dumper::Dumper($DATAS),"\n";

#$epocsec = &Time::HiRes::tv_interval($t0);
#($sec,$min) = localtime($epocsec);
&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

#&cgi_lib::common::message(&cgi_lib::common::encodeJSON($DATAS,1), $LOG) if(defined $LOG);
close($LOG);

exit;

=pod
DROP TABLE IF EXISTS freeze_mapping CASCADE;
CREATE TABLE freeze_mapping (
  fm_id        serial                      not null,
  fm_timestamp timestamp without time zone not null default now(),
  fm_point     boolean                     not null default false,
  fm_comment   text,
--  fm_raw_data  bytea                       not null,
  fm_delcause  text,
  fm_entry     timestamp without time zone not null default now(),
  fm_modified  timestamp without time zone not null default now(),
  fm_openid    text                        not null default 'system'::text
);
ALTER TABLE freeze_mapping ADD PRIMARY KEY (fm_id);
ALTER TABLE freeze_mapping ADD CONSTRAINT freeze_mapping_fm_timestamp_unique UNIQUE (fm_timestamp);

INSERT INTO freeze_mapping (fm_timestamp,fm_entry,fm_modified) VALUES ('2016-10-05 14:51:07','2016-10-05 14:51:07','2016-10-05 14:51:07');
INSERT INTO freeze_mapping (fm_timestamp,fm_entry,fm_modified) VALUES ('2016-10-17 09:52:53','2016-10-17 09:52:53','2016-10-17 09:52:53');
=cut


sub cmd_create {
	my %FORM = @_;
	my $LOG = $FORM{'LOG'};
	delete $FORM{'LOG'};
	delete $FORM{'_dc'};

	my $prog_basename = qq|batch-create-freeze-mapping|;
	if(exists $FORM{'cmd'} && defined $FORM{'cmd'} && $FORM{'cmd'} eq 'create' && exists $FORM{'datas'} && defined $FORM{'datas'} && length $FORM{'datas'}){
		my $DATAS = {
			'datas' => [],
			'total' => 0,
			'success' => JSON::XS::false
		};
		my $prog = &catfile($FindBin::Bin,'..','batch',qq|$prog_basename.pl|);
		if(-e $prog && -x $prog){
			my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
			my $mfmt = sprintf("%04d%02d%02d%02d%02d%02d.%d",$year+1900,$mon+1,$mday,$hour,$min,$sec,$$);
			my $param_file = &catfile($FindBin::Bin,'temp',qq|$prog_basename.$mfmt.json|);
			&cgi_lib::common::writeFileJSON($param_file, \%FORM);

			my @OPTIONS;
			push(@OPTIONS, sprintf('--host=%s',$ENV{'AG_DB_HOST'})) if(exists $ENV{'AG_DB_HOST'} && defined $ENV{'AG_DB_HOST'});
			push(@OPTIONS, sprintf('--port=%s',$ENV{'AG_DB_PORT'})) if(exists $ENV{'AG_DB_PORT'} && defined $ENV{'AG_DB_PORT'});
			push(@OPTIONS, sprintf('--db=%s',  $ENV{'AG_DB_NAME'})) if(exists $ENV{'AG_DB_NAME'} && defined $ENV{'AG_DB_NAME'});
			push(@OPTIONS, sprintf('--file=%s',$param_file));
			my $options = join(' ',@OPTIONS);

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
					exec(qq|nice -n 19 $prog $options|);
					exit(1);
				}else{
					return $mfmt;
				}
			}else{
				die("Can't execute program");
			}
		}
	}
	elsif(exists $FORM{'cmd'} && defined $FORM{'cmd'} && $FORM{'cmd'} eq 'pregress' && exists $FORM{'pid'} && defined $FORM{'pid'} && length $FORM{'pid'}){
		my $param_file = &catfile($FindBin::Bin,'temp',sprintf("%s.%s.json",$prog_basename,$FORM{'pid'}));
		my $DATAS = &cgi_lib::common::readFileJSON($param_file);
		if(defined $DATAS && ref $DATAS eq 'HASH' && exists $DATAS->{'status'} && defined $DATAS->{'status'} && $DATAS->{'status'} =~ /^(finish|error:?)$/i){
			unlink $param_file;
		}
		return $DATAS;
	}
}
