#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use Time::Piece;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
use BITS::ReCalc;
require "webgl_common.pl";
use cgi_lib::common;
use AG::login;

$SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit";
sub sigexit {
	my($date) = `date`;
	$date =~ s/\s*$//g;
	print STDERR "[$date] KILL THIS CGI!![$ENV{SCRIPT_NAME}]\n";
	exit(1);
}


my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);
$FORM{$_} = &cgi_lib::common::decodeUTF8($FORM{$_}) for(sort keys(%FORM));
$COOKIE{$_} = &cgi_lib::common::decodeUTF8($COOKIE{$_}) for(sort keys(%COOKIE));
if(exists($COOKIE{'ag_annotation.session'})){
	my $session_info = {};
	$session_info->{'PARAMS'}->{$_} = $FORM{$_} for(sort keys(%FORM));
	$session_info->{'COOKIE'}->{$_} = $COOKIE{$_} for(sort keys(%COOKIE));
	&AG::login::setSessionHistory($session_info);
}

my($logfile,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

$FORM{'cmd'} = 'read' unless(defined $FORM{'cmd'});
$logfile .= '.'.$FORM{'cmd'};

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
#$logfile .= '.'.sprintf("%04d%02d%02d%02d",$year+1900,$mon+1,$mday,$hour);
$logfile .=  sprintf(".%02d%02d%02d.%05d",$hour,$min,$sec,$$);

my $LOG;
open($LOG,">> $logfile");
flock($LOG,2);
print $LOG "\n[$logtime]:$0\n";
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);


#&setDefParams(\%FORM,\%COOKIE);
#&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);

#&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
#&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);

my $DATAS = {
	'datas'   => [],
	'total'   => 0,
	'msg'     => undef,
	'success' => JSON::XS::false
};

my $ci_id=$FORM{'ci_id'};
my $cb_id=$FORM{'cb_id'};
my $md_id=$FORM{'md_id'};
my $mv_id=$FORM{'mv_id'};

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
if(defined $LOG){
	&cgi_lib::common::message('$md_id='.$md_id, $LOG);
	&cgi_lib::common::message('$mv_id='.$mv_id, $LOG);
	&cgi_lib::common::message('$ci_id='.$ci_id, $LOG);
	&cgi_lib::common::message('$cb_id='.$cb_id, $LOG);
}
$FORM{'ci_id'}=$ci_id;
$FORM{'cb_id'}=$cb_id;
$FORM{'md_id'}=$md_id;
$FORM{'mv_id'}=$mv_id;



$FORM{'cmd'} = 'read' unless(defined $FORM{'cmd'});

my $sql;

if($FORM{'cmd'} eq 'read'){
	$sql=<<SQL;
select
  COALESCE(artf_id,0),
  art_id,
  artff_comment,
  EXTRACT(EPOCH FROM artff_timestamp) as artff_timestamp,
  EXTRACT(EPOCH FROM artff_entry) as artff_entry
from 
  art_folder_file
where
  artff_delcause is null
SQL

	my @artf_ids;
	push(@artf_ids, $FORM{'drag_artf_id'}) if(exists $FORM{'drag_artf_id'} && defined $FORM{'drag_artf_id'} && $FORM{'drag_artf_id'} =~ /^[0-9]+$/);
	push(@artf_ids, $FORM{'drop_artf_id'}) if(exists $FORM{'drop_artf_id'} && defined $FORM{'drop_artf_id'} && $FORM{'drop_artf_id'} =~ /^[0-9]+$/);
	if(exists $FORM{'drag_artf_ids'} && defined $FORM{'drag_artf_ids'} && length $FORM{'drag_artf_ids'}){
		my $drag_artf_ids = &cgi_lib::common::decodeJSON($FORM{'drag_artf_ids'});
		push(@artf_ids,@$drag_artf_ids) if(defined $drag_artf_ids && ref $drag_artf_ids eq 'ARRAY');
	}
	if(scalar @artf_ids){
		$sql .= sprintf(qq|and COALESCE(artf_id,0) in (%s)|,join(',',map {'?'} keys %{{ map {$_ => undef} @artf_ids}}));
	}

	my $art_ids;
	$art_ids = &cgi_lib::common::decodeJSON($FORM{'drop_art_ids'}) if(exists $FORM{'drop_art_ids'} && defined $FORM{'drop_art_ids'} && length $FORM{'drop_art_ids'});
	$sql .= sprintf(qq|and art_id in (%s)|,join(',',map {'?'} @$art_ids)) if(defined $art_ids && ref $art_ids eq 'ARRAY' && scalar @$art_ids);

	my @bind;
	push(@bind,@artf_ids);
	push(@bind,@$art_ids) if(defined $art_ids && ref $art_ids eq 'ARRAY' && scalar @$art_ids);

	print $LOG __LINE__,":sql=[$sql]\n";
	eval{
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		if(scalar @bind){
			$sth->execute(@bind) or die $dbh->errstr;
		}else{
			$sth->execute() or die $dbh->errstr;
		}
		$DATAS->{'total'} = $sth->rows();
		$DATAS->{'total'} -= 0;
		if($DATAS->{'total'}>0){
			my $artf_id;
			my $art_id;
			my $artff_comment;
			my $artff_timestamp;
			my $artff_entry;

			my $column_number = 0;
			$sth->bind_col(++$column_number, \$artf_id,   undef);
			$sth->bind_col(++$column_number, \$art_id,    undef);
			$sth->bind_col(++$column_number, \$artff_comment,   undef);
			$sth->bind_col(++$column_number, \$artff_timestamp,   undef);
			$sth->bind_col(++$column_number, \$artff_entry, undef);

			while($sth->fetch){
				push(@{$DATAS->{'datas'}},{
					artf_id => $artf_id,
					art_id => $art_id,
					artff_comment => $artff_comment,
					artff_timestamp => defined $artff_timestamp ? $artff_timestamp-0 : undef,
					artff_entry => defined $artff_entry ? $artff_entry-0 : undef,
				});
			}
		}
		$sth->finish;
		undef $sth;
		$DATAS->{'success'} = JSON::XS::true;
	};
	if($@){
		print $LOG __LINE__.':'.$@."\n";
		$DATAS->{'success'} = JSON::XS::false;
		$DATAS->{'msg'} = $@;
	}
}
elsif($FORM{'cmd'} eq 'create'){
	unless(
		exists $FORM{'datas'} && defined $FORM{'datas'}
	){
		$DATAS->{'msg'} = qq|JSON形式が違います|;
		&utf8::decode($DATAS->{'msg'}) unless(&Encode::is_utf8($DATAS->{'msg'}));
		&gzip_json($DATAS);
		exit;
	}
	my $datas;
	$datas = &cgi_lib::common::decodeJSON($FORM{'datas'}) if(exists $FORM{'datas'} && defined $FORM{'datas'});
	if(defined $datas && ref $datas eq 'ARRAY'){
		$dbh->{'AutoCommit'} = 0;
		$dbh->{'RaiseError'} = 1;
		eval{
			my $sth_ins = $dbh->prepare(qq|insert into art_folder_file (artf_id,art_id,artff_entry,artff_timestamp) values (?,?,?,?)|) or die $dbh->errstr;
			my $time = localtime(time)->strftime('%Y-%m-%d %H:%M:%S');
			my %artf_ids;
			foreach my $data (@$datas){
				next unless(exists $data->{'artf_id'} && defined $data->{'artf_id'} && length $data->{'artf_id'} && exists $data->{'art_id'} && defined $data->{'art_id'} && length $data->{'art_id'});

				my $artf_id;
				my $art_id;
				my $artff_entry = $time;
				my $artff_timestamp = $time;
				$artf_id         = ($data->{'artf_id'} eq '0' ? undef :$data->{'artf_id'});
				$art_id          = $data->{'art_id'};
				$artff_entry     = localtime($data->{'artff_entry'})->strftime('%Y-%m-%d %H:%M:%S')     if(exists $data->{'artff_entry'}     && defined $data->{'artff_entry'});
				$artff_timestamp = localtime($data->{'artff_timestamp'})->strftime('%Y-%m-%d %H:%M:%S') if(exists $data->{'artff_timestamp'} && defined $data->{'artff_timestamp'});

				$sth_ins->execute( $artf_id, $art_id, $artff_entry, $artff_timestamp) or die $dbh->errstr;
				$sth_ins->finish;

				$artf_ids{defined $artf_id ? $artf_id : '0'} = undef;
			}

			if(scalar keys(%artf_ids)){
				my $sth_sel = $dbh->prepare(qq|select count(*) from art_folder_file where COALESCE(artf_id,0) = ?|) or die $dbh->errstr;
				foreach my $artf_id (keys(%artf_ids)){
					$sth_sel->execute($artf_id) or die $dbh->errstr;
					my $HASH = {
						artf_id => $artf_id-0,
						art_count => 0
					};
					if($sth_sel->rows()>0){
						my $art_count;
						my $column_number = 0;
						$sth_sel->bind_col(++$column_number, \$art_count, undef);
						$sth_sel->fetch;
						$HASH->{'art_count'} = $art_count-0;
					}
					$sth_sel->finish;
					push(@{$DATAS->{'datas'}},$HASH);
				}
				undef $sth_sel;
			}

			$dbh->commit();
			$dbh->do("NOTIFY art_folder_file");
			$DATAS->{'success'} = JSON::XS::true;
		};
		if($@){
			print $LOG __LINE__.':'.$@."\n";
			$DATAS->{'msg'} = $@;
			$dbh->rollback;
		}
		$dbh->{'AutoCommit'} = 1;
		$dbh->{'RaiseError'} = 0;
	}
}
elsif($FORM{'cmd'} eq 'destroy'){
	unless(
		exists $FORM{'datas'} && defined $FORM{'datas'}
	){
		$DATAS->{'msg'} = qq|JSON形式が違います|;
		&utf8::decode($DATAS->{'msg'}) unless(&Encode::is_utf8($DATAS->{'msg'}));
		&gzip_json($DATAS);
		exit;
	}
	my $datas;
	$datas = &cgi_lib::common::decodeJSON($FORM{'datas'}) if(exists $FORM{'datas'} && defined $FORM{'datas'});
	if(defined $datas && ref $datas eq 'ARRAY'){
		$dbh->{'AutoCommit'} = 0;
		$dbh->{'RaiseError'} = 1;
		eval{
			my $sth_del = $dbh->prepare(qq|delete from art_folder_file where COALESCE(artf_id,0)=? and art_id=?|) or die $dbh->errstr;
			my %artf_ids;
			foreach my $data (@$datas){
				my $artf_id;
				my $art_id;
				$artf_id = $data->{'artf_id'} if(exists $data->{'artf_id'} && defined $data->{'artf_id'});
				$art_id  = $data->{'art_id'}  if(exists $data->{'art_id'}  && defined $data->{'art_id'});
				next unless(defined $artf_id && defined $art_id);
				$artf_ids{$artf_id} = undef;

				$sth_del->execute( $artf_id, $art_id) or die $dbh->errstr;
				$sth_del->finish;
			}

			if(scalar keys(%artf_ids)){
				my $sth_sel = $dbh->prepare(qq|select count(*) from art_folder_file where COALESCE(artf_id,0) = ?|) or die $dbh->errstr;
				foreach my $artf_id (keys(%artf_ids)){
					$sth_sel->execute($artf_id) or die $dbh->errstr;
					my $HASH = {
						artf_id => $artf_id-0,
						art_count => 0
					};
					if($sth_sel->rows()>0){
						my $art_count;
						my $column_number = 0;
						$sth_sel->bind_col(++$column_number, \$art_count, undef);
						$sth_sel->fetch;
						$HASH->{'art_count'} = $art_count-0;
					}
					$sth_sel->finish;
					push(@{$DATAS->{'datas'}},$HASH);
				}
				undef $sth_sel;
			}

			$dbh->commit();
			$dbh->do("NOTIFY art_folder_file");
			$DATAS->{'success'} = JSON::XS::true;
		};
		if($@){
			print $LOG __LINE__.':'.$@."\n";
			$DATAS->{'msg'} = $@;
			$dbh->rollback;
		}
		$dbh->{'AutoCommit'} = 1;
		$dbh->{'RaiseError'} = 0;
	}
}
else{
	$DATAS->{'success'} = JSON::XS::false;
	$DATAS->{'msg'} = 'Unknown command ['.&cgi_lib::common::decodeUTF8($FORM{'cmd'}).']';
}

&gzip_json($DATAS);
print $LOG __LINE__.':'.&cgi_lib::common::encodeJSON($DATAS,1);

close($LOG);
exit;

=debug




=cut
