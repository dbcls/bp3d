#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use Archive::Zip qw( :ERROR_CODES );
use File::Spec::Functions qw(abs2rel rel2abs catdir catfile splitdir tmpdir);
use File::Basename;
use Getopt::Long qw(:config posix_default no_ignore_case gnu_compat);
my $config = {
	host => $ENV{'AG_DB_HOST'} // '127.0.0.1',
	port => $ENV{'AG_DB_PORT'} // '8543',
	db   => $ENV{'AG_DB_NAME'} // 'bp3d_manage'
};
&Getopt::Long::GetOptions($config,qw/
	host|h=s
	port|p=s
	db|d=s
	file|f=s
/) or exit 1;

$ENV{'AG_DB_HOST'} = $config->{'host'};
$ENV{'AG_DB_PORT'} = $config->{'port'};
$ENV{'AG_DB_NAME'} = $config->{'db'};

use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'..','cgi_lib'),&catdir($FindBin::Bin,'..','..','..','ag-common','lib');

require "webgl_common.pl";
use cgi_lib::common;

use BITS::ExportConceptArtMap;

my $LOG = \*STDERR;
&cgi_lib::common::message($config, $LOG);
#exit;

unless(exists $config->{'file'} && defined $config->{'file'} && length $config->{'file'} && -e $config->{'file'} && -f $config->{'file'} && -s $config->{'file'} && -r $config->{'file'}){
	exit(1);
}
my $DATAS = {
	'total' => 0,
	'success' => JSON::XS::false
};
my $FORM = &cgi_lib::common::readFileJSON($config->{'file'});
&cgi_lib::common::message($FORM, $LOG);
if(defined $FORM && ref $FORM eq 'HASH'){
	foreach my $key (keys(%$FORM)){
		$DATAS->{$key} = $FORM->{$key};
	}
}
unless(
	defined	$FORM &&
	ref			$FORM eq 'HASH' &&
	exists	$FORM->{'cmd'} &&
	defined	$FORM->{'cmd'} &&
	$FORM->{'cmd'} eq 'create' &&
	exists	$FORM->{'datas'} &&
	defined	$FORM->{'datas'} &&
	length	$FORM->{'datas'}
){
	&cgi_lib::common::writeFileJSON($config->{'file'}, $DATAS);
	exit;
}
my $datas = (exists $FORM->{'datas'} && defined $FORM->{'datas'}) ? (ref $FORM->{'datas'} eq 'ARRAY' ? $FORM->{'datas'} : &cgi_lib::common::decodeJSON($FORM->{'datas'})) : undef;
unless(
	defined	$datas &&
	ref			$datas eq 'ARRAY' &&
	scalar @$datas
){
	&cgi_lib::common::writeFileJSON($config->{'file'}, $DATAS);
	exit;
}

$DATAS->{'datas'} = $datas;
$DATAS->{'total'} = 0;
$DATAS->{'status'} = 'start';
$DATAS->{'success'} = JSON::XS::true;
&cgi_lib::common::writeFileJSON($config->{'file'}, $DATAS);


my $freeze_mapping_abs_path = &catdir(&File::Basename::dirname($config->{'file'}),'..','freeze_mapping');
my $freeze_mapping_proc_path = &catfile($freeze_mapping_abs_path,'.freeze_mapping');

my $dbh = &get_dbh();
#$dbh->{'AutoCommit'} = 0;
#$dbh->{'RaiseError'} = 1;
eval{
	my $sth_ins = $dbh->prepare('INSERT INTO freeze_mapping (fm_timestamp,fm_point,fm_comment,fm_status) VALUES (?,?,?,?) RETURNING fm_id,EXTRACT(EPOCH FROM fm_timestamp)') or die $dbh->errstr;
	my $sth_upd = $dbh->prepare('UPDATE freeze_mapping SET fm_status=? WHERE fm_id=?') or die $dbh->errstr;
	my $sth_del = $dbh->prepare('DELETE FROM freeze_mapping WHERE fm_id=?') or die $dbh->errstr;

	foreach my $data (@$datas){
		my $fm_id;
		eval{
			if($data->{'fm_point'}==JSON::XS::true){
				$dbh->do('UPDATE freeze_mapping SET fm_point=false') or die $dbh->errstr;
			}

			$sth_ins->execute($data->{'fm_timestamp'},$data->{'fm_point'},$data->{'fm_comment'},$DATAS->{'status'}) or die $dbh->errstr;
			$DATAS->{'total'} += $sth_ins->rows();
			my $column_number = 0;
			my $fm_timestamp;
			$sth_ins->bind_col(++$column_number, \$fm_id, undef);
			$sth_ins->bind_col(++$column_number, \$fm_timestamp, undef);
			$sth_ins->fetch;
			$sth_ins->finish;

			$data->{'fm_id'} = $fm_id if(defined $fm_id);

			chmod 0700, $freeze_mapping_abs_path;

			my $OUT;
			open($OUT, ">> $freeze_mapping_proc_path") or die "$! [$freeze_mapping_proc_path]";
			flock($OUT, 2);
			say $OUT $$;
			close($OUT);

			my $out_path = &catdir($freeze_mapping_abs_path,".$$");
			&File::Path::rmtree($out_path) if(-e $out_path);
			&File::Path::mkpath($out_path);

			$data->{'fm_status'} = $DATAS->{'status'} = 'export_obj';
			&cgi_lib::common::writeFileJSON($config->{'file'}, $DATAS);
			$sth_upd->execute($data->{'fm_status'}, $fm_id) or die $dbh->errstr;
			$sth_upd->finish;

			my $zip = &BITS::ExportConceptArtMap::exec($dbh,$FORM,$out_path,$LOG);

			my ($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime($fm_timestamp);
			my @weekly = ('Sun', 'Mon', 'Tue', 'Wed', 'Thr', 'Fri', 'Sut');
			my $file = sprintf("freeze_mapping_%04d%02d%02d%02d%02d%02d", $year+1900,$month+1,$mday,$hour,$min,$sec);
			my $zip_file = &catfile($freeze_mapping_abs_path,qq|$file.zip|);

			$data->{'fm_status'} = $DATAS->{'status'} = 'zip';
			&cgi_lib::common::writeFileJSON($config->{'file'}, $DATAS);
			$sth_upd->execute($data->{'fm_status'}, $fm_id) or die $dbh->errstr;
			$sth_upd->finish;

			die 'write error' unless($zip->writeToFileNamed($zip_file) == AZ_OK);

			undef $zip;
			chmod 0400, $zip_file;
			utime $fm_timestamp, $fm_timestamp, $zip_file or die $!;

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

			&File::Path::rmtree($out_path) if(-e $out_path);
			unless(-e $freeze_mapping_proc_path && -f $freeze_mapping_proc_path && -s $freeze_mapping_proc_path){
				chmod 0500, $freeze_mapping_abs_path;
				unlink $freeze_mapping_proc_path if(-e $freeze_mapping_proc_path && -f $freeze_mapping_proc_path);
			}

			$data->{'fm_status'} = $DATAS->{'status'} = 'finish';
			$sth_upd->execute($data->{'fm_status'}, $fm_id) or die $dbh->errstr;
			$sth_upd->finish;
		};
		if($@){
			$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8($@);
			$DATAS->{'status'} = 'error';

			if(defined $fm_id){
				$sth_del->execute($fm_id) or die $dbh->errstr;
				$sth_del->finish;
			}
		}
	}
	undef $sth_ins;
	undef $sth_upd;
	undef $sth_del;

	$DATAS->{'msg'} = undef;

#	$dbh->commit;
};
if($@){
	$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8($@);
	$DATAS->{'status'} = 'error';
	&cgi_lib::common::message($@, $LOG);
#	$dbh->rollback;
	$DATAS->{'success'} = JSON::XS::false;
}
#$dbh->{'AutoCommit'} = 1;
#$dbh->{'RaiseError'} = 0;

&cgi_lib::common::writeFileJSON($config->{'file'}, $DATAS);
exit;
