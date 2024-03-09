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
#my $json = JSON::XS->new->utf8->indent( 0 )->canonical(1);
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
use cgi_lib::common;
use AG::login;

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
	$PARAMS{$_} = &cgi_lib::common::decodeUTF8($PARAMS{$_}) for(sort keys(%PARAMS));
	$COOKIE{$_} = &cgi_lib::common::decodeUTF8($COOKIE{$_}) for(sort keys(%COOKIE));
	if(exists($COOKIE{'ag_annotation.session'})){
		my $session_info = {};
		$session_info->{'PARAMS'}->{$_} = $PARAMS{$_} for(sort keys(%PARAMS));
		$session_info->{'COOKIE'}->{$_} = $COOKIE{$_} for(sort keys(%COOKIE));
		&AG::login::setSessionHistory($session_info);
	}

	my($logfile,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

	my($epocsec,$microsec) = &Time::HiRes::gettimeofday();
	my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);
	$logfile .=  sprintf(".%02d%02d%02d.%05d",$hour,$min,$sec,$$);

	my $LOG;
	open($LOG,">> $logfile");
	if(defined $LOG){
		select($LOG);
		$| = 1;
		select(STDOUT);
	}

	my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime();
	if(defined $LOG){
		&cgi_lib::common::message(sprintf("\n%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec), $LOG);
		&cgi_lib::common::dumper(\%ENV, $LOG);
		&cgi_lib::common::dumper(\%PARAMS, $LOG);
	}

	eval{
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

	my $old_umask = umask(0);
	my $out_path = &catdir($FindBin::Bin,'temp');
	unless(-e $out_path){
		&File::Path::mkpath($out_path,0,0777);
		chmod 0777,$out_path;
	}

	if($ENV{'REQUEST_METHOD'} eq 'POST'){

#		print qq|Content-type: text/html; charset=UTF-8\n\n|;
		my $file_fh = $query->upload('file') || $query->upload('file1');

		&cgi_lib::common::dumper($file_fh, $LOG) if(defined $LOG);

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

				my $files;
				$files = &cgi_lib::common::decodeJSON($PARAMS{'files'}) if(exists $PARAMS{'files'} && defined $PARAMS{'files'});
				$files = [{}] unless(defined $files && ref $files eq 'ARRAY' && scalar @$files);
				my @DIR = ($BITS::Config::UPLOAD_PATH);
				push(@DIR, $files->[0]->{'path'}) if(exists $files->[0]->{'path'} && defined $files->[0]->{'path'} && length $files->[0]->{'path'});
				push(@DIR, &File::Basename::basename($PARAMS{'file'}));

				$upload_file = &catdir(@DIR);
				delete $PARAMS{'file'};
				unlink $upload_file if(-e $upload_file);

				$file_fh = $query->upload('file');
				if(defined $LOG){
					&cgi_lib::common::dumper($file_fh, $LOG);
					&cgi_lib::common::message('$upload_file='.$upload_file, $LOG);
				}
				if(defined $file_fh){
					my $upload_dir = &File::Basename::dirname($upload_file);
					&File::Path::mkpath($upload_dir,0,0777) unless(-e $upload_dir);
					&File::Copy::copy($file_fh,$upload_file);
				}

				if(-e $upload_file && -s $upload_file){
#					my $files;
#					$files = &cgi_lib::common::decodeJSON($PARAMS{'files'}) if(exists $PARAMS{'files'} && defined $PARAMS{'files'});
					if(defined $files && ref $files eq 'ARRAY' && scalar @$files){
						$PARAMS{'upload_file'} = $files->[0];
					}else{
						$PARAMS{'upload_file'} = {};
					}
					$PARAMS{'upload_file'}->{'local_path'} = $upload_file;
				}
			}
			elsif(exists $PARAMS{'file1'} && defined $PARAMS{'file1'}){
				my $files;
				$files = &cgi_lib::common::decodeJSON($PARAMS{'files'}) if(exists $PARAMS{'files'} && defined $PARAMS{'files'});
				$PARAMS{'upload_files'} = [];
				my $key;
				for(my $i=1;;$i++){
					$key = qq|file$i|;
					last unless(exists $PARAMS{$key} && defined $PARAMS{$key});
					$file_fh = $query->upload($key);
					&cgi_lib::common::dumper($file_fh, $LOG) if(defined $LOG);
					next unless(defined $file_fh);

					my $file;
					$file = $files->[$i-1] if(defined $files && ref $files eq 'ARRAY' && scalar @$files);
					$file = {} unless(defined $file && ref $file eq 'HASH');
					my @DIR = ($BITS::Config::UPLOAD_PATH);
					push(@DIR, $file->{'path'}) if(exists $file->{'path'} && defined $file->{'path'} && length $file->{'path'});
					push(@DIR, &File::Basename::basename($PARAMS{$key}));

					$upload_file = &catdir(@DIR);
					delete $PARAMS{$key};
					unlink $upload_file if(-e $upload_file);
					my $upload_dir = &File::Basename::dirname($upload_file);
					&File::Path::mkpath($upload_dir,0,0777) unless(-e $upload_dir);
					&File::Copy::copy($file_fh,$upload_file);
					if(-e $upload_file && -s $upload_file){
						if(exists $file->{'last'} && defined $file->{'last'} && $file->{'last'} > 0){
							my $mtime = $file->{'last'};
							utime($mtime,$mtime,$upload_file);
						}
						$file->{'local_path'} = $upload_file;
						push(@{$PARAMS{'upload_files'}},$file);
					}
				}
				$PARAMS{'upload_files'} = [sort {-l $b->{'local_path'} <=> -l $a->{'local_path'}} @{$PARAMS{'upload_files'}}];
			}
			delete $PARAMS{'files'} if(exists $PARAMS{'files'} && defined $PARAMS{'files'});
			if(defined $LOG){
				&cgi_lib::common::message(\%PARAMS, $LOG);
			}
			unless(exists $PARAMS{'upload_file'} || exists $PARAMS{'upload_files'}){
				$RTN->{'msg'} = &Encode::decode_utf8('Undefined Upload file');
				&gzip_json($RTN);
				exit 0;
			}
#die __LINE__;

			#オリジナルのIDが指定されている場合、実際に存在するIDのみ使用する
			if(
				exists $PARAMS{'art_org_info'} && defined $PARAMS{'art_org_info'} &&
				exists $PARAMS{'arto_id'} && defined $PARAMS{'arto_id'} && length $PARAMS{'arto_id'}
			){
				my %arto_ids;
				my @arto_ids;
				my $arto_id;
				my @temp_ids = split(/[^A-Za-z0-9]+/,$PARAMS{'arto_id'});
				my $sql_arti_sel = qq|select art_id from art_file_info where art_id in (|.join(",",map {'?'} @temp_ids).qq|) group by art_id|;
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
					$arto_id = join(";",@arto_ids);
				}else{
					undef $arto_id;
				}
				if(defined $arto_id){
					$PARAMS{'arto_id'} = $arto_id;
				}else{
					$PARAMS{'art_org_info'} = undef;
					$PARAMS{'arto_id'} = undef;
				}
			}

			if(defined $LOG){
				&cgi_lib::common::dumper(\%PARAMS, $LOG);
			}

			my $prog_basename = qq|batch-$cgi_name|;
			my $prog = &catfile($FindBin::Bin,'..','batch',qq|$prog_basename.pl|);
			if(-e $prog && -x $prog){
				my $time_md5 = &Digest::MD5::md5_hex(&Time::HiRes::time());
				$RTN->{'sessionID'} = $PARAMS{'sessionID'} = $time_md5;
				$PARAMS{'prefix'} = &catdir($out_path,$time_md5);
				$PARAMS{'HTTP_USER_AGENT'} = $ENV{'HTTP_USER_AGENT'};
				$PARAMS{'COOKIE'} = \%COOKIE;
				$PARAMS{'success'} = JSON::XS::true;

				my $params_file = &catfile($out_path,qq|$time_md5.json|);
				open(my $OUT,"> $params_file") or die $!;
				flock($OUT,2);
				print $OUT &cgi_lib::common::encodeJSON(\%PARAMS);
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

		&cgi_lib::common::message('$params_file='.$params_file, $LOG) if(defined $LOG);

		eval{
			if(-e $params_file){
				my $params_file_t = localtime((stat($params_file))[9]);
				my $current_t = localtime;
				my $diff_t = $current_t-$params_file_t;
				if($diff_t->seconds>60){
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
			&cgi_lib::common::message('$buf='.$buf, $LOG) if(defined $LOG);
			$RTN = &cgi_lib::common::decodeJSON($buf);
			if(!defined $RTN || $RTN->{'success'} == JSON::XS::false || lc($RTN->{'progress'}->{'msg'}) eq 'end'){
#				unlink $params_file if(-e $params_file);
			}
			unless(defined $RTN){
				$RTN = {
					'success' => JSON::XS::false
				};
			}
			&cgi_lib::common::message(&cgi_lib::common::encodeJSON($RTN,1), $LOG) if(defined $LOG);
			$buf = &cgi_lib::common::encodeJSON($RTN);
		};
		if($@){
			$RTN->{'success'} = JSON::XS::false;
			$RTN->{'msg'} = &Encode::decode_utf8('Error: '.$@);
			&cgi_lib::common::message(&cgi_lib::common::encodeJSON($RTN,1), $LOG) if(defined $LOG);
			$buf = &cgi_lib::common::encodeJSON($RTN);
		}
		&cgi_lib::common::message('$buf='.$buf, $LOG) if(defined $LOG);

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
	exit;
}
