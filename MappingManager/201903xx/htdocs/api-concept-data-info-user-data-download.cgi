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
use Time::Piece;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;

use BITS::Config;
#use BITS::VTK;
#use BITS::Voxel;
#use BITS::ConceptArtMapModified;
#use BITS::ConceptArtMapPart;

use obj2deci;
require "webgl_common.pl";
use cgi_lib::common;
use AG::login;

#my $is_subclass_cdi_name = $BITS::ConceptArtMapPart::is_subclass_cdi_name;

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

if(defined $LOG){
	&cgi_lib::common::message($ci_id, $LOG);
	&cgi_lib::common::message($cb_id, $LOG);
	&cgi_lib::common::message($md_id, $LOG);
	&cgi_lib::common::message($mv_id, $LOG);
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



my @FIELD_ORDER = qw/sublass_FMA super_FMA super_FMA_name super_infer_FMA super_infer_FMA_name subclass_FMA_name infer infer_sentence super_infer super_infer_sentence/;


&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);
$DATAS = &cmd_read(%FORM);
&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);
if($FORM{'cmd'} eq 'read'){
	&gzip_json($DATAS);
}
elsif($FORM{'cmd'} eq 'download'){
	my $format = $FORM{'format'} || 'txt';
	my $LF = "\n";
	my $CODE = "utf8";
	if($ENV{HTTP_USER_AGENT}=~/Windows/){
		$LF = "\r\n";
		$CODE = "shiftjis";
	}elsif($ENV{HTTP_USER_AGENT}=~/Macintosh/){
		$LF = "\r";
		$CODE = "shiftjis";
	}

	my @CONTENTS;

	my $sth = $dbh->prepare(qq|select ci_name,cb_name from concept_build as cb left join(select * from concept_info) as ci on ci.ci_id=cb.ci_id where cb.ci_id=$ci_id and cb.cb_id=$cb_id|) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	my $ci_name;
	my $cb_name;
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$ci_name, undef);
	$sth->bind_col(++$column_number, \$cb_name, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;

	push(@CONTENTS, join("\t",'#'.&cgi_lib::common::encodeUTF8($ci_name),&cgi_lib::common::encodeUTF8($cb_name)));

	my $t = localtime;
	push(@CONTENTS, join("\t",'#data',&cgi_lib::common::encodeUTF8($t->cdate)));

	push(@CONTENTS, '#'.&cgi_lib::common::encodeUTF8(join("\t",map {my $a=$_;$a =~ s/_/ /g;$a} @FIELD_ORDER)));
	foreach my $data (@{$DATAS->{'datas'}}){
		push(@CONTENTS, &cgi_lib::common::encodeUTF8(join("\t",map {exists $data->{$_} && defined $data->{$_} ? $data->{$_} : ''} @FIELD_ORDER)));
	}
#	&cgi_lib::common::printContent(join("\n",@CONTENTS), 'text/plain');

	my $filename = sprintf('InferSampleOutput_%s.%s',$t->strftime('%Y%m%d%H%M%S'),$format);
	my $content = &Encode::encode($CODE,&cgi_lib::common::decodeUTF8(join($LF,@CONTENTS).$LF));
	my $contentLength = length $content;
#	my $mime = qq|application/octet-stream|;
	my $mime = qq|text/plain|;
	print qq|X-Content-Type-Options: nosniff\n|;
	print qq|Content-Type: $mime\n|;
	print qq|Content-Disposition: attachment; filename=$filename\n|;
	print qq|Last-Modified: |.&HTTP::Date::time2str(time).qq|\n|;
	print qq|Accept-Ranges: bytes\n|;
	print qq|Content-Length: $contentLength\n|;
	print qq|Pragma: no-cache\n|;
	print qq|\n|;
	print $content;
}
else{
	&gzip_json({
		datas => [],
		total => 0,
		success => JSON::XS::false
	});
}
&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);
close($LOG);
exit;


sub cmd_read {
	my %FORM = @_;
	my $DATAS = {
		'datas' => [],
		'total' => 0,
		'success' => JSON::XS::false
	};
	my $ci_id=$FORM{'ci_id'};
	my $cb_id=$FORM{'cb_id'};
	my $md_id=$FORM{'md_id'};
	my $mv_id=$FORM{'mv_id'};

	return $DATAS unless(
		defined $ci_id && $ci_id =~ /^[0-9]+$/ &&
		defined $cb_id && $cb_id =~ /^[0-9]+$/ &&
		defined $md_id && $md_id =~ /^[0-9]+$/ &&
		defined $mv_id && $mv_id =~ /^[0-9]+$/
	);

	$dbh->{'AutoCommit'} = 0;
	$dbh->{'RaiseError'} = 1;
	eval{
		my @bind_values;
		my $sql;
		my $sql_fmt;
		my $sth;
		my $column_number;

		my $cdi_id;
		my $cdi_pid;
		my $cdi_name;
		my $cd_name;
		my $cdi_pname;
		my $cd_pname;
		my $crl_name;
		my $cmp_title;
		my $cmp_prefix;
		my $cmp_abbr;
		my $cmp_crl_name;

		my %SUBCLASS_DATA_HASH;

		$sql=q|
select
  cdi_id,
  cdi_name,
  regexp_replace(cdi_name,'^(FMA[0-9]+)\-.$','\\\\1')
from
  concept_data_info
where
 is_user_data AND (ci_id,cdi_id) in (
   select
     ci_id,
     cdi_id
   from
     concept_art_map
   where
    cm_use and ci_id=?
)
|;
#		&cgi_lib::common::message($sql, $LOG) if(defined $LOG);

		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute($ci_id) or die $dbh->errstr;

		$column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_id, undef);
		$sth->bind_col(++$column_number, \$cdi_name, undef);
		$sth->bind_col(++$column_number, \$cdi_pname, undef);
		while($sth->fetch){

#			&cgi_lib::common::message($cdi_pname, $LOG) if(defined $LOG);

			$SUBCLASS_DATA_HASH{$cdi_name} = {
				cdi_id    => $cdi_id,
				cdi_name  => $cdi_name,
				cdi_pname => $cdi_pname
			};
		}
		$sth->finish;
		undef $sth;

#		&cgi_lib::common::message(scalar keys(%SUBCLASS_DATA_HASH), $LOG) if(defined $LOG);

		if(scalar keys(%SUBCLASS_DATA_HASH)){
			my %PNAME_HASH = map {$SUBCLASS_DATA_HASH{$_}->{'cdi_pname'} => undef} keys(%SUBCLASS_DATA_HASH);
#			&cgi_lib::common::message(\%PNAME_HASH, $LOG) if(defined $LOG);
#			&cgi_lib::common::message(scalar keys(%PNAME_HASH), $LOG) if(defined $LOG);

			$sql_fmt=q|
select
  cdi_id,
  cdi_name
from
  concept_data_info
where
 ci_id=? AND
 cdi_name IN (%s)
|;
			$sql=sprintf($sql_fmt, join(',',map {'?'} keys(%PNAME_HASH)));
#			&cgi_lib::common::message($sql, $LOG) if(defined $LOG);
			$sth = $dbh->prepare($sql) or die $dbh->errstr;
			$sth->execute($ci_id,keys(%PNAME_HASH)) or die $dbh->errstr;
			undef %PNAME_HASH;
			my %PID_HASH;

			$column_number = 0;
			$sth->bind_col(++$column_number, \$cdi_pid, undef);
			$sth->bind_col(++$column_number, \$cdi_pname, undef);
			while($sth->fetch){
				$PNAME_HASH{$cdi_pname} = $cdi_pid;
				$PID_HASH{$cdi_pid} = $cdi_pname;
			}
			$sth->finish;
			undef $sth;


			$sql_fmt=q|
select
  cdi_id
from
  concept_data
where
 ci_id=? AND
 cb_id=? AND
 cdi_id IN (%s)
|;
			my %EXISTS_PID_HASH;

			$sql=sprintf($sql_fmt, join(',',map {'?'} keys(%PID_HASH)));
			&cgi_lib::common::message($sql, $LOG) if(defined $LOG);
			$sth = $dbh->prepare($sql) or die $dbh->errstr;
			$sth->execute($ci_id,$cb_id,keys(%PID_HASH)) or die $dbh->errstr;
			$column_number = 0;
			$sth->bind_col(++$column_number, \$cdi_pid, undef);
			while($sth->fetch){
				$EXISTS_PID_HASH{$cdi_pid} = undef;
			}
			$sth->finish;
			undef $sth;



			&cgi_lib::common::message(scalar keys(%SUBCLASS_DATA_HASH), $LOG) if(defined $LOG);

			foreach my $cdi_name (keys(%SUBCLASS_DATA_HASH)){
				my $cdi_pname = $SUBCLASS_DATA_HASH{$cdi_name}->{'cdi_pname'};
				my $cdi_pid = $PNAME_HASH{$cdi_pname};
				delete $SUBCLASS_DATA_HASH{$cdi_name} unless(exists $EXISTS_PID_HASH{$cdi_pid});
			}

			&cgi_lib::common::message(scalar keys(%SUBCLASS_DATA_HASH), $LOG) if(defined $LOG);

#			&cgi_lib::common::message(\%PNAME_HASH, $LOG) if(defined $LOG);

		}
		if(0 && scalar keys(%SUBCLASS_DATA_HASH)){

			$sql_fmt=<<SQL;
select
-- ct.cdi_id,
 cdi.cdi_name,
 COALESCE(cd.cd_name,cdi.cdi_name_e),
-- ct.cdi_pid,
 cdip.cdi_name,
 COALESCE(cdp.cd_name,cdip.cdi_name_e),
-- ct.crl_id,
 crl.crl_name,
-- cdi.cmp_id,
 COALESCE(cmp.cmp_display_title,cmp.cmp_title),
 cmp_prefix,
 cmp.cmp_abbr,
-- cmp.crl_id,
 cmpcrl.crl_name
from
 concept_tree as ct

left join (
 select * from concept_data_info
) as cdi on cdi.ci_id=ct.ci_id and cdi.cdi_id=ct.cdi_id

left join (
 select * from concept_data_info
) as cdip on cdip.ci_id=ct.ci_id and cdip.cdi_id=ct.cdi_pid

left join (
 select * from concept_data
) as cd on cd.ci_id=ct.ci_id and cd.cb_id=ct.cb_id and cd.cdi_id=ct.cdi_id

left join (
 select * from concept_data
) as cdp on cdp.ci_id=ct.ci_id and cdp.cb_id=ct.cb_id and cdp.cdi_id=ct.cdi_pid

left join (
 select * from concept_relation_logic
) as crl on crl.crl_id=ct.crl_id

left join (
 select * from concept_art_map_part
) as cmp on cmp.cmp_id=cdi.cmp_id

left join (
 select * from concept_relation_logic
) as cmpcrl on cmpcrl.crl_id=cmp.crl_id

where
 ct.ci_id=? and ct.cb_id=? and ct.cdi_id in (%s)

order by
 cdi.cdi_name,
 ct.crl_id
SQL

#			$sql=sprintf($sql_fmt, join(',',map {'?'} keys(%PID_HASH)));


		}
		else{
			$sql=<<SQL;
select
-- ct.cdi_id,
 cdi.cdi_name,
 COALESCE(cd.cd_name,cdi.cdi_name_e),
-- ct.cdi_pid,
 cdip.cdi_name,
 COALESCE(cdp.cd_name,cdip.cdi_name_e),
-- ct.crl_id,
 crl.crl_name,
-- cdi.cmp_id,
 COALESCE(cmp.cmp_display_title,cmp.cmp_title),
 cmp_prefix,
 cmp.cmp_abbr,
-- cmp.crl_id,
 cmpcrl.crl_name
from
 concept_tree as ct

left join (
 select * from concept_data_info
) as cdi on cdi.ci_id=ct.ci_id and cdi.cdi_id=ct.cdi_id

left join (
 select * from concept_data_info
) as cdip on cdip.ci_id=ct.ci_id and cdip.cdi_id=ct.cdi_pid

left join (
 select * from concept_data
) as cd on cd.ci_id=ct.ci_id and cd.cb_id=ct.cb_id and cd.cdi_id=ct.cdi_id

left join (
 select * from concept_data
) as cdp on cdp.ci_id=ct.ci_id and cdp.cb_id=ct.cb_id and cdp.cdi_id=ct.cdi_pid

left join (
 select * from concept_relation_logic
) as crl on crl.crl_id=ct.crl_id

left join (
 select * from concept_art_map_part
) as cmp on cmp.cmp_id=cdi.cmp_id

left join (
 select * from concept_relation_logic
) as cmpcrl on cmpcrl.crl_id=cmp.crl_id

where
 ct.cb_id=$cb_id and (ct.ci_id,ct.cdi_id) in (select ci_id,cdi_id from concept_art_map where cm_use and (ci_id,cdi_id) in ( select ci_id,cdi_id from concept_data_info where ci_id=$ci_id AND is_user_data))

order by
 cdi.cdi_name,
 ct.crl_id
SQL
		}
		&cgi_lib::common::message($sql, $LOG) if(defined $LOG);

		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;



		my %DATAS_HASH;

		$column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_name, undef);
		$sth->bind_col(++$column_number, \$cd_name, undef);
		$sth->bind_col(++$column_number, \$cdi_pname, undef);
		$sth->bind_col(++$column_number, \$cd_pname, undef);
		$sth->bind_col(++$column_number, \$crl_name, undef);
		$sth->bind_col(++$column_number, \$cmp_title, undef);
		$sth->bind_col(++$column_number, \$cmp_prefix, undef);
		$sth->bind_col(++$column_number, \$cmp_abbr, undef);
		$sth->bind_col(++$column_number, \$cmp_crl_name, undef);
		while($sth->fetch){
			unless(exists $DATAS_HASH{$cdi_name}){
				$DATAS_HASH{$cdi_name} = {
					'__order__'   => scalar keys(%DATAS_HASH),
					'sublass_FMA' => $cdi_name
				};
			}
			if($crl_name eq $cmp_crl_name){
				$DATAS_HASH{$cdi_name}->{'super_FMA'} = $cdi_pname;
				$DATAS_HASH{$cdi_name}->{'super_FMA_name'} = $cd_pname;
			}else{
				$DATAS_HASH{$cdi_name}->{'super_infer_FMA'} = $cdi_pname;
				$DATAS_HASH{$cdi_name}->{'super_infer_FMA_name'} = $cd_pname;
			}
			if(exists $DATAS_HASH{$cdi_name}->{'super_FMA_name'}){
				my $fmt;
				if(defined $cmp_prefix && length $cmp_prefix){
					$fmt = $cmp_prefix;
				}
				elsif($cmp_abbr eq 'R'){
					$fmt = 'RIGHT';
				}
				elsif($cmp_abbr eq 'L'){
					$fmt = 'LEFT';
				}
				elsif($cmp_abbr eq 'N'){
					$fmt = 'PROXIMAL';
				}
				elsif($cmp_abbr eq 'F'){
					$fmt = 'DISTAL';
				}
				elsif($cmp_abbr eq 'O'){
					$fmt = 'OTHER';
				}
				elsif($cmp_abbr eq 'P'){
					$fmt = 'PROPER PART OF';
				}
				elsif($cmp_abbr eq 'Q' || $cmp_abbr =~ /^[STUVWX]$/){
					$fmt = 'A named part of';
				}
				$fmt .= ' %s' if(defined $fmt && length $fmt);

				$DATAS_HASH{$cdi_name}->{'subclass_FMA_name'} = sprintf($fmt,$DATAS_HASH{$cdi_name}->{'super_FMA_name'}) if(defined $fmt);


				if($cmp_crl_name eq 'is_a'){
					$DATAS_HASH{$cdi_name}->{'infer_sentence'} = sprintf('%s is-a %s',$cdi_name,$DATAS_HASH{$cdi_name}->{'super_FMA_name'});
				}else{
					$DATAS_HASH{$cdi_name}->{'infer_sentence'} = sprintf('%s is-part-of %s',$cdi_name,$DATAS_HASH{$cdi_name}->{'super_FMA_name'});
				}

			}
			if(exists $DATAS_HASH{$cdi_name}->{'super_FMA'}){
				if($cmp_crl_name eq 'is_a'){
					$DATAS_HASH{$cdi_name}->{'infer'} = sprintf('%s is-a %s',$cdi_name,$DATAS_HASH{$cdi_name}->{'super_FMA'});
				}else{
					$DATAS_HASH{$cdi_name}->{'infer'} = sprintf('%s is-part-of %s',$cdi_name,$DATAS_HASH{$cdi_name}->{'super_FMA'});
				}
			}

			if(exists $DATAS_HASH{$cdi_name}->{'super_infer_FMA'}){
				if($cmp_crl_name eq 'is_a'){
					$DATAS_HASH{$cdi_name}->{'super_infer'} = sprintf('%s is-part-of %s',$cdi_name,$DATAS_HASH{$cdi_name}->{'super_infer_FMA'});
				}else{
					$DATAS_HASH{$cdi_name}->{'super_infer'} = sprintf('%s is-a %s',$cdi_name,$DATAS_HASH{$cdi_name}->{'super_infer_FMA'});
				}
			}

			if(exists $DATAS_HASH{$cdi_name}->{'super_infer_FMA_name'}){
				if($cmp_crl_name eq 'is_a'){
					$DATAS_HASH{$cdi_name}->{'super_infer_sentence'} = sprintf('%s is-part-of %s',$cdi_name,$DATAS_HASH{$cdi_name}->{'super_infer_FMA_name'});
				}else{
					$DATAS_HASH{$cdi_name}->{'super_infer_sentence'} = sprintf('%s is-a %s',$cdi_name,$DATAS_HASH{$cdi_name}->{'super_infer_FMA_name'});
				}
			}

		}
		$sth->finish;
		undef $sth;

		$DATAS->{'datas'} = [map {delete $DATAS_HASH{$_}->{'__order__'};$DATAS_HASH{$_}} sort { $DATAS_HASH{$a}->{'__order__'} <=> $DATAS_HASH{$b}->{'__order__'} } keys(%DATAS_HASH)];

		$DATAS->{'total'} = scalar keys(%DATAS_HASH);
		$DATAS->{'success'} = JSON::XS::true;
	};
	if($@){
		$DATAS->{'success'} = JSON::XS::false;
		$DATAS->{'total'} = 0;
		$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8($@);

		&cgi_lib::common::message($@, $LOG) if(defined $LOG);
	}
	$dbh->rollback;
	$dbh->{'AutoCommit'} = 1;
	$dbh->{'RaiseError'} = 0;
	return $DATAS;
}
