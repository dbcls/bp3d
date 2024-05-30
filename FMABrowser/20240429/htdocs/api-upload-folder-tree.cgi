#!/opt/services/ag/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use Data::Dumper;
$Data::Dumper::Indent = 1;
$Data::Dumper::Sortkeys = 1;

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

#my $disEnv = &getDispEnv();
#my $dispTreeChildPartsNum = $disEnv->{dispTreeChildPartsNum};
my $dispTreeChildPartsNum = 'false';# unless(defined $dispTreeChildPartsNum);

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

#my @extlist = qw|.cgi .pl|;
#my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);
#my $logfile = qq|$FindBin::Bin/logs/$FORM{'cdi_name'}.$cgi_name.txt|;
#$logfile .= '.'.$FORM{'cdi_name'} if(exists $FORM{'cdi_name'} && defined $FORM{'cdi_name'});

=pod
$FORM{ag_data}=qq|obj/bp3d/4.0|;
$FORM{'cdi_name'}=qq|root|;
$FORM{model}=qq|bp3d|;
$FORM{'node'}=qq|root|;
$FORM{tree}=qq|isa|;
$FORM{version}=qq|4.0|;
=cut

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
#$logfile .= '.'.sprintf("%04d%02d%02d%02d",$year+1900,$mon+1,$mday,$hour);
$logfile .=  sprintf(".%02d%02d%02d.%05d",$hour,$min,$sec,$$);

my $LOG;
open($LOG,">> $logfile");
select($LOG);
$| = 1;
select(STDOUT);
flock($LOG,2);
print $LOG "\n[$logtime]:$0\n";
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);


#&setDefParams(\%FORM,\%COOKIE);
#&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);

#&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
#&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);

my $TREE = [];

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
	&cgi_lib::common::printContentJSON($TREE,\%FORM);
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
  COALESCE(artf.artf_id,0),
  COALESCE(artf.artf_pid,0),
  artf_name,
  artf_comment,
  EXTRACT(EPOCH FROM artf_timestamp) as artf_timestamp,
  EXTRACT(EPOCH FROM artf_entry) as artf_entry,
  child_count,
  art_count
from 
  art_folder as artf

left join (
  select
   artf_pid,
   count(artf_pid) as child_count
  from
   art_folder
  group by
   artf_pid
) as c on (c.artf_pid=artf.artf_id)

left join (
  select
   artf_id,
   count(art_id) as art_count
  from
   art_folder_file
  where
   artff_delcause is null
  group by
   artf_id
) as aff on (aff.artf_id=artf.artf_id)

where
  artf_delcause is null
SQL

	$FORM{'node'} = $FORM{'artf_pid'} if(!defined $FORM{'node'} && exists $FORM{'artf_pid'} && defined $FORM{'artf_pid'});
	unless(exists($FORM{'node'})){
#		my $json = &JSON::XS::encode_json(\@TREE);
#		print $json;
		&gzip_json($TREE);
#		print LOG __LINE__,":",$json,"\n";
		close($LOG);
		exit;
	}elsif($FORM{'node'} eq 'root'){
		$sql .= qq|and artf.artf_pid is null|;
	}elsif(exists($FORM{'artf_pid'})){
		$sql .= qq|and artf.artf_pid=?|;
	}
#$sql .= qq| order by tree.t_order|;
#$sql .= qq| order by tree.t_cnum desc|;
#	$sql .= qq| order by bu_cnum desc,f.cdi_name_e|;
	$sql .= qq| order by artf_name|;

	print $LOG __LINE__,":sql=[$sql]\n";
	eval{
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;

		my $expanded = JSON::XS::false;

		if($FORM{'node'} eq 'root'){
			$sth->execute() or die $dbh->errstr;
	#		$expanded = JSON::XS::true;
		}elsif(exists($FORM{'artf_pid'})){
			$sth->execute($FORM{'artf_pid'}) or die $dbh->errstr;
		}else{
			$sth->execute() or die $dbh->errstr;
		}
		print $LOG __LINE__,":rows=[",$sth->rows(),"]\n";

		my $artf_id;
		my $artf_pid;
		my $artf_name;
		my $artf_comment;
		my $artf_timestamp;
		my $artf_entry;
		my $child_count;
		my $art_count;

		my $column_number = 0;
		$sth->bind_col(++$column_number, \$artf_id,   undef);
		$sth->bind_col(++$column_number, \$artf_pid,    undef);
		$sth->bind_col(++$column_number, \$artf_name,   undef);
		$sth->bind_col(++$column_number, \$artf_comment, undef);
		$sth->bind_col(++$column_number, \$artf_timestamp,   undef);
		$sth->bind_col(++$column_number, \$artf_entry,    undef);
		$sth->bind_col(++$column_number, \$child_count,    undef);
		$sth->bind_col(++$column_number, \$art_count,    undef);

		while($sth->fetch){

			my $HASH = {
				text    => $artf_name,
				leaf    => JSON::XS::false,#$child_count ? JSON::XS::false : JSON::XS::true,
				iconCls => 'tfolder',

				artf_id => $artf_id,
				artf_pid => $artf_pid,
				artf_name => $artf_name,
				artf_comment => $artf_comment,

				artf_timestamp => defined $artf_timestamp ? $artf_timestamp-0 : undef,
				artf_entry => defined $artf_entry ? $artf_entry-0 : undef,

				art_count => defined $art_count ? $art_count-0 : undef,

#				children => $child_count>0 ? undef : []
			};

			push(@$TREE,$HASH);
	#		undef $text;
		}
		$sth->finish;
		undef $sth;
	};
	if($@){
		print $LOG __LINE__,":",$@,"\n";
		$TREE = {};
		$TREE->{'success'} = JSON::XS::false;
		$TREE->{'msg'} = $@;
		&utf8::decode($TREE->{'msg'}) unless(&Encode::is_utf8($TREE->{'msg'}));
	}
}
elsif($FORM{'cmd'} eq 'read_art_count'){
	$TREE = {};
	$sql=<<SQL;
select
 COALESCE(count(art_id),0)
from
 art_folder_file
where
 artff_delcause is null
SQL
	if(exists($FORM{'artf_id'})){
		$FORM{'artf_id'} = undef unless($FORM{'artf_id'});
		if(defined $FORM{'artf_id'}){
			$sql .= qq|and artf_id=?|;
		}else{
			$sql .= qq|and artf_id is null|;
		}
	}else{
		$sql .= qq|and artf_id is null|;
	}
	eval{
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		if(exists($FORM{'artf_id'})){
			if(defined $FORM{'artf_id'}){
				$sth->execute($FORM{'artf_id'}) or die $dbh->errstr;
			}else{
				$sth->execute() or die $dbh->errstr;
			}
		}else{
			$sth->execute() or die $dbh->errstr;
		}
		my $art_count;
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$art_count,   undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;

		if(defined $art_count){
			$TREE->{'success'} = JSON::XS::true;
			$TREE->{'art_count'} = $art_count - 0;
		}
	};
	if($@){
		print $LOG __LINE__,":",$@,"\n";
		$TREE = {};
		$TREE->{'success'} = JSON::XS::false;
		$TREE->{'msg'} = $@;
		&utf8::decode($TREE->{'msg'}) unless(&Encode::is_utf8($TREE->{'msg'}));
	}

}
elsif($FORM{'cmd'} eq 'create'){
	$TREE = {};
	$TREE->{'success'} = JSON::XS::false;

	unless(
		exists $FORM{'datas'} && defined $FORM{'datas'}
	){
		$TREE->{'msg'} = qq|JSON形式が違います|;
		&utf8::decode($TREE->{'msg'}) unless(&Encode::is_utf8($TREE->{'msg'}));
		&gzip_json($TREE);
		exit;
	}

#	$TREE->{'msg'} = 'CREATE エラー!!';
#	&utf8::decode($TREE->{'msg'}) unless(&Encode::is_utf8($TREE->{'msg'}));
#	&gzip_json($TREE);
#	exit;

	my $datas;
	$datas = &cgi_lib::common::decodeJSON($FORM{'datas'}) if(exists $FORM{'datas'} && defined $FORM{'datas'});
	if(defined $datas && ref $datas eq 'ARRAY'){
		$dbh->{'AutoCommit'} = 0;
		$dbh->{'RaiseError'} = 1;
		eval{
			my $sth_sel_new_artf_id = $dbh->prepare(qq|select COALESCE(max(artf_id)=count(artf_id),false) from art_folder|) or die $dbh->errstr;
			my $sth_sel_all_artf_id = $dbh->prepare(qq|select artf_id from art_folder order by artf_id|) or die $dbh->errstr;

#			my $sth_ins_new = $dbh->prepare(qq|insert into art_folder (artf_pid,artf_name,artf_id) values (?,?,?) RETURNING artf_id,EXTRACT(EPOCH FROM artf_timestamp),EXTRACT(EPOCH FROM artf_entry)|) or die $dbh->errstr;
			my $sth_ins_re = $dbh->prepare(qq|insert into art_folder (artf_id,artf_pid,artf_name) values (?,?,?) RETURNING artf_id,EXTRACT(EPOCH FROM artf_timestamp),EXTRACT(EPOCH FROM artf_entry)|) or die $dbh->errstr;
			my $sth_ins;

			foreach my $data (@$datas){
				my $rows;
				my $column_number = 0;
				$data->{'artf_pid'} = undef unless($data->{'artf_pid'});
				&cgi_lib::common::message($data,$LOG) if(defined $LOG);
				my @bind_params = ($data->{'artf_pid'}, $data->{'artf_name'});
				my $is_new_artf_id;
				$column_number = 0;
				$sth_sel_new_artf_id->execute() or die $dbh->errstr;
				$sth_sel_new_artf_id->bind_col(++$column_number, \$is_new_artf_id,   undef);
				$sth_sel_new_artf_id->fetch;
				$sth_sel_new_artf_id->finish;

				&cgi_lib::common::message($is_new_artf_id,$LOG) if(defined $LOG);

				unless($is_new_artf_id){
					&cgi_lib::common::message('',$LOG) if(defined $LOG);
					my $count_artf_id = 0;
					my $db_artf_id;
					$column_number = 0;
					$sth_sel_all_artf_id->execute() or die $dbh->errstr;
					$sth_sel_all_artf_id->bind_col(++$column_number, \$db_artf_id,   undef);
					while($sth_sel_all_artf_id->fetch){
						$count_artf_id++;
						&cgi_lib::common::message('$count_artf_id='.$count_artf_id,$LOG) if(defined $LOG);
						&cgi_lib::common::message('$db_artf_id='.$db_artf_id,$LOG) if(defined $LOG);
						last unless($db_artf_id==$count_artf_id);
					}
					$sth_sel_all_artf_id->finish;
					$count_artf_id = 1 unless($count_artf_id);
					$data->{'artf_id'} = $count_artf_id - 0;
					unshift @bind_params, $data->{'artf_id'};
					$sth_ins = $sth_ins_re;
				}else{
					&cgi_lib::common::message('',$LOG) if(defined $LOG);

					$sth_sel_all_artf_id->execute() or die $dbh->errstr;
					my $count_artf_id = $sth_sel_all_artf_id->rows() + 1;
					$sth_sel_all_artf_id->finish;
					unshift @bind_params, $count_artf_id;


					$sth_ins = $sth_ins_re;
				}

				&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\@bind_params,1),$LOG) if(defined $LOG);

				$sth_ins->execute( @bind_params ) or die $dbh->errstr;

				my $artf_id;
				my $artf_timestamp;
				my $artf_entry;
				$column_number = 0;
				$sth_ins->bind_col(++$column_number, \$artf_id,   undef);
				$sth_ins->bind_col(++$column_number, \$artf_timestamp,   undef);
				$sth_ins->bind_col(++$column_number, \$artf_entry,    undef);

				$sth_ins->fetch;

				$data->{'artf_id'} = $artf_id - 0;
				$data->{'artf_timestamp'} = $artf_timestamp - 0;
				$data->{'artf_entry'} = $artf_entry - 0;

				push(@{$TREE->{'datas'}},$data);

				$sth_ins->finish;
			}

			$dbh->commit();
			$dbh->do("NOTIFY art_folder");
			$TREE->{'success'} = JSON::XS::true;
		};
		if($@){
			print $LOG __LINE__,":",$@,"\n";
			$TREE->{'msg'} = $@;
			&utf8::decode($TREE->{'msg'}) unless(&Encode::is_utf8($TREE->{'msg'}));
			$dbh->rollback;
		}
		$dbh->{'AutoCommit'} = 1;
		$dbh->{'RaiseError'} = 0;
	}
}
elsif($FORM{'cmd'} eq 'update'){
	$TREE = {};
	$TREE->{'success'} = JSON::XS::false;

	unless(
		exists $FORM{'datas'} && defined $FORM{'datas'}
	){
		$TREE->{'msg'} = qq|JSON形式が違います|;
		&utf8::decode($TREE->{'msg'}) unless(&Encode::is_utf8($TREE->{'msg'}));
		&gzip_json($TREE);
		exit;
	}

#	$TREE->{'msg'} = 'UPDATE エラー!!';
#	&utf8::decode($TREE->{'msg'}) unless(&Encode::is_utf8($TREE->{'msg'}));
#	&gzip_json($TREE);
#	exit;

	my $datas;
	$datas = &cgi_lib::common::decodeJSON($FORM{'datas'}) if(exists $FORM{'datas'} && defined $FORM{'datas'});
	if(defined $datas && ref $datas eq 'ARRAY'){
		$dbh->{'AutoCommit'} = 0;
		$dbh->{'RaiseError'} = 1;
		eval{
			my $sth_upd = $dbh->prepare(qq|update art_folder set artf_pid=?,artf_name=?,artf_timestamp=now() where artf_id=? RETURNING EXTRACT(EPOCH FROM artf_timestamp)|) or die $dbh->errstr;
			foreach my $data (@$datas){
				$data->{'artf_pid'} = undef unless($data->{'artf_pid'});
				my $column_number = 0;
				$sth_upd->execute( $data->{'artf_pid'}, $data->{'artf_name'}, $data->{'artf_id'} ) or die $dbh->errstr;

				my $artf_timestamp;
				$sth_upd->bind_col(++$column_number, \$artf_timestamp,   undef);
				$sth_upd->fetch;
				$sth_upd->finish;

				$data->{'artf_timestamp'} = $artf_timestamp - 0;

				push(@{$TREE->{'datas'}},$data);
			}

			$dbh->commit();
			$dbh->do("NOTIFY art_folder");
			$TREE->{'success'} = JSON::XS::true;
		};
		if($@){
			print $LOG __LINE__,":",$@,"\n";
			$TREE->{'msg'} = $@;
			&utf8::decode($TREE->{'msg'}) unless(&Encode::is_utf8($TREE->{'msg'}));
			$dbh->rollback;
		}
		$dbh->{'AutoCommit'} = 1;
		$dbh->{'RaiseError'} = 0;
	}
}
elsif($FORM{'cmd'} eq 'destroy'){
	$TREE = {};
	$TREE->{'success'} = JSON::XS::false;

	unless(
		exists $FORM{'remove_artf_id'} && defined $FORM{'remove_artf_id'} =~ /^[0-9]+$/ &&
		exists $FORM{'datas'} && defined $FORM{'datas'}
	){
		$TREE->{'msg'} = qq|JSON形式が違います|;
		&utf8::decode($TREE->{'msg'}) unless(&Encode::is_utf8($TREE->{'msg'}));
		&gzip_json($TREE);
		exit;
	}

#	$TREE->{'msg'} = 'DELETE エラー!!';
#	&utf8::decode($TREE->{'msg'}) unless(&Encode::is_utf8($TREE->{'msg'}));
#	&gzip_json($TREE);
#	exit;

	my $datas;
	$datas = &cgi_lib::common::decodeJSON($FORM{'datas'}) if(exists $FORM{'datas'} && defined $FORM{'datas'});
	if(defined $datas && ref $datas eq 'ARRAY'){
		$dbh->{'AutoCommit'} = 0;
		$dbh->{'RaiseError'} = 1;
		eval{
&cgi_lib::common::message(&cgi_lib::common::encodeJSON($datas,1),$LOG) if(defined $LOG);

#			#何らかの原因で迷子のOBJをルートに追加する
#			my $sth = $dbh->prepare(qq|insert into art_folder_file (art_id) select art_id from art_file_info where art_id not in (select art_id from art_folder_file where artff_delcause is null) and art_delcause is null|) or die $dbh->errstr;
#			$sth->execute() or die $dbh->errstr;
#&cgi_lib::common::message($sth->rows(),$LOG) if(defined $LOG);
#			$sth->finish;
#			undef $sth;

			my %HASH = ($FORM{'remove_artf_id'}=>0);
			my @artf_ids;
			my $depth = 0;
			do{
				$depth++;
				@artf_ids = keys(%HASH);
				my $artf_id;
				my $sth = $dbh->prepare(sprintf('select COALESCE(artf_id,0) from art_folder where artf_delcause is null and COALESCE(artf_pid,0) in (%s)',join(',',map {'?'} @artf_ids))) or die $dbh->errstr;
				$sth->execute(@artf_ids) or die $dbh->errstr;
				$sth->bind_col(1, \$artf_id, undef);
				while($sth->fetch){
					next unless(defined $artf_id && length $artf_id);
					$HASH{$artf_id} = $depth unless(exists $HASH{$artf_id} && defined $HASH{$artf_id});
				}
				$sth->finish;
				undef $sth;
			}while(scalar @artf_ids < scalar keys(%HASH));
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%HASH,1),$LOG) if(defined $LOG);
			@artf_ids = map {$_-0} sort {$HASH{$b}<=>$HASH{$a}} keys(%HASH);
			undef %HASH;
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\@artf_ids,1),$LOG) if(defined $LOG);
#die "ERROR!!";

			my $sth_del_artff = $dbh->prepare(sprintf(qq|delete from art_folder_file where COALESCE(artf_id,0) in (%s)|,join(',',map {'?'} @artf_ids))) or die $dbh->errstr;
			$sth_del_artff->execute( @artf_ids ) or die $dbh->errstr;
&cgi_lib::common::message($sth_del_artff->rows(),$LOG) if(defined $LOG);
			$sth_del_artff->finish;
			undef $sth_del_artff;

			my $sth_del_artf = $dbh->prepare(sprintf(qq|delete from art_folder where COALESCE(artf_id,0) in (%s)|,join(',',map {'?'} @artf_ids))) or die $dbh->errstr;
			$sth_del_artf->execute( @artf_ids ) or die $dbh->errstr;
&cgi_lib::common::message($sth_del_artf->rows(),$LOG) if(defined $LOG);
			$sth_del_artf->finish;
			undef $sth_del_artf;

			if(exists $FORM{'remove_folder_and_object'} && defined $FORM{'remove_folder_and_object'} && $FORM{'remove_folder_and_object'} eq 'true'){

				my @art_ids;
				my $sth_art_sel = $dbh->prepare(qq|select art_id from art_file_info where art_id not in (select art_id from art_folder_file where artff_delcause is null group by art_id) and art_delcause is null|) or die $dbh->errstr;
				$sth_art_sel->execute() or die $dbh->errstr;
				my $column_number = 0;
				my $art_id;
				$sth_art_sel->bind_col(++$column_number, \$art_id,   undef);
				while($sth_art_sel->fetch){
					push(@art_ids, $art_id);
				}
				$sth_art_sel->finish;
				undef $sth_art_sel;

				if(scalar @art_ids){

					my $sql_cm_delete   = qq|delete from concept_art_map where md_id=$md_id and mv_id=$mv_id and art_id in (%s)|;
					my $sth_cm_delete   = $dbh->prepare(sprintf($sql_cm_delete,join(',',map {'?'} @art_ids))) or die $dbh->errstr;
					$sth_cm_delete->execute( @art_ids ) or die $dbh->errstr;
&cgi_lib::common::message($sth_cm_delete->rows(),$LOG) if(defined $LOG);
					$sth_cm_delete->finish;
					undef $sth_cm_delete;

#					my $sql_del_arti = 'delete from art_file_info where art_id in (%s)';
					my $sql_del_arti = qq{update art_file_info set art_delcause='DELETE ['||now()||']' where art_id in (%s)};
					my $sth_del_arti = $dbh->prepare(sprintf($sql_del_arti,join(',',map {'?'} @art_ids))) or die $dbh->errstr;
					$sth_del_arti->execute( @art_ids ) or die $dbh->errstr;
&cgi_lib::common::message($sth_del_arti->rows(),$LOG) if(defined $LOG);
					$sth_del_arti->finish;
					undef $sth_del_arti;

#					my $sql_del_art = "update art_file set art_delcause='DELETE ['||now()||']' where art_id in (%s)";
#					my $sth_del_art = $dbh->prepare(sprintf($sql_del_art,join(',',map {'?'} @art_ids))) or die $dbh->errstr;
#					$sth_del_art->execute( @art_ids ) or die $dbh->errstr;
#&cgi_lib::common::message($sth_del_art->rows(),$LOG) if(defined $LOG);
#					$sth_del_art->finish;
#					undef $sth_del_art;

				}
			}

			#どのフォルダにも属さないOBJをルートに追加する
			my $sth = $dbh->prepare(qq|insert into art_folder_file (art_id) select art_id from art_file_info where art_id not in (select art_id from art_folder_file where artff_delcause is null) and art_delcause is null|) or die $dbh->errstr;
			$sth->execute() or die $dbh->errstr;
			&cgi_lib::common::message($sth->rows(),$LOG) if(defined $LOG);
			$sth->finish;
			undef $sth;


#			$dbh->rollback;
			$dbh->commit();
			$dbh->do("NOTIFY art_folder");
			$dbh->do("NOTIFY art_folder_file");
			$dbh->do("NOTIFY art_file") if(exists $FORM{'remove_folder_and_object'} && defined $FORM{'remove_folder_and_object'} && $FORM{'remove_folder_and_object'} eq 'true');
			$TREE->{'success'} = JSON::XS::true;
		};
		if($@){
			$TREE->{'msg'} = &cgi_lib::common::decodeUTF8($@);
			&cgi_lib::common::message($TREE->{'msg'}, $LOG);
			$dbh->rollback;
		}
		$dbh->{'AutoCommit'} = 1;
		$dbh->{'RaiseError'} = 0;
	}
}
else{
	$TREE = {};
	$TREE->{'success'} = JSON::XS::false;
	$TREE->{'msg'} = 'Unknown command ['.&cgi_lib::common::decodeUTF8($FORM{'cmd'}).']';
}

#my $json = to_json(\@TREE);
#my $json = &JSON::XS::encode_json(\@TREE);
#print $json;
&gzip_json($TREE);
#print $LOG __LINE__,":",$json,"\n";

&cgi_lib::common::message(&cgi_lib::common::encodeJSON($TREE,1),$LOG) if(defined $LOG);

close($LOG);
exit;

=debug




=cut
