#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI::Cookie;
use Clone qw(clone);

use Data::Dumper;
$Data::Dumper::Indent = 1;
$Data::Dumper::Sortkeys = 1;

use File::Spec::Functions qw(catdir catfile);
use Cwd;
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'API'),&Cwd::abs_path(&catdir($FindBin::Bin,'..','..','ag-common','lib'));
use cgi_lib::common;

require "common.pl";
require "common_db.pl";
my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);

#$FORM{lng} = $COOKIE{"ag_annotation.locale"} if(!exists($FORM{lng}) && exists($COOKIE{"ag_annotation.locale"})); #とりあえず
#$FORM{lng} = "ja" if(!exists($FORM{lng}));

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $file = sprintf("%04d%02d%02d%02d%02d%02d_%d",$year+1900,$mon+1,$mday,$hour,$min,$sec,$$);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);
my $LOG = &cgi_lib::common::getLogFH(\%FORM,\%COOKIE);
#open(LOG,"> $FindBin::Bin/logs/$COOKIE{'ag_annotation.session'}.$cgi_name.txt");
#print LOG "\n[$logtime]:$0\n";
#foreach my $key (sort keys(%FORM)){
#	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}
#foreach my $key (sort keys(%COOKIE)){
#	print LOG __LINE__,":\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
#}
#foreach my $key (sort keys(%ENV)){
#	print LOG "ENV{$key}=[",$ENV{$key},"]\n";
#}
#print LOG "\n";

#$FORM{tg_id} = $COOKIE{"ag_annotation.images.tg_id"} if(!exists($FORM{tg_id}) && exists($COOKIE{"ag_annotation.images.tg_id"}));

&setDefParams(\%FORM,\%COOKIE);
#foreach my $key (sort keys(%FORM)){
#	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}
#print LOG "\n";

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
#foreach my $key (sort keys(%FORM)){
#	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}
#print LOG "\n";


#my $parentURL = $FORM{parent} if(exists($FORM{parent}));
#my ($lsdb_OpenID,$lsdb_Auth);
#if(defined $parentURL){
#	($lsdb_OpenID,$lsdb_Auth) = &openidAuth($parentURL);
#}

#print qq|Content-type: text/html; charset=UTF-8\n\n|;


#if(!exists($FORM{'records'}) || !exists($FORM{'version'})){
unless(exists $FORM{'records'} && defined $FORM{'records'} && exists $FORM{'version'} && defined $FORM{'version'}){
	&cgi_lib::common::printContent(qq|{success:false,msg:"There is not Category information"}|);
#	print LOG __LINE__,qq|:{success:false,msg:"There is not Category information"}\n|;
#	close(LOG);
	exit;
}


#my $records = &JSON::XS::decode_json($FORM{'records'});
my $records = &cgi_lib::common::decodeJSON($FORM{'records'});
unless(defined $records && ref $records eq 'ARRAY'){
	&cgi_lib::common::printContent(qq|{success:false,msg:"There is not Category information"}|);
	exit;
}

my $RTN = {
	success => JSON::XS::false,
	records => undef
};

#unless(defined $FORM{'ci_id'} && defined $FORM{'cb_id'} && defined $FORM{'md_id'} && defined $FORM{'mv_id'} && defined $FORM{'bul_id'}){
unless(defined $FORM{'md_id'} && defined $FORM{'mv_id'} && defined $FORM{'bul_id'}){
	$RTN->{'msg'} = qq|Unknown version!!|;
}else{
	eval{
#	my $bp3d_table = &getBP3DTablename($FORM{'version'});
#	my $bp3d_id_sth = $dbh->prepare(qq|select b_id from $bp3d_table where b_comid=?|);

		my $credit = &getDefImageCredit();
		my $root;
		if(exists($FORM{'txpath'})){
			my @PATH = split(/\//,$FORM{'txpath'});
			$root = $PATH[1];
		}


		my $sql=<<SQL;
select
 ci_id,
 cb_id
from
 model_version
where
 md_id=?  and
 mv_id=?
SQL
		my $version_sth = $dbh->prepare($sql);
		$version_sth->execute($FORM{'md_id'},$FORM{'mv_id'});
		if($version_sth->rows>0){
			my $ci_id;
			my $cb_id;
			my $col_num=0;
			$version_sth->bind_col(++$col_num, \$ci_id, undef);
			$version_sth->bind_col(++$col_num, \$cb_id, undef);
			$version_sth->fetch;
			$FORM{'ci_id'} = $ci_id;
			$FORM{'cb_id'} = $cb_id;
		}
		$version_sth->finish;
		undef $version_sth;

		$sql=<<SQL;
select
 rep.rep_id,
 cdi.cdi_name,
 md.md_abbr,
 mv.mv_name_e,
 bul.bul_name_e
from
 representation as rep
left join(select * from concept_data_info) cdi on cdi.ci_id=rep.ci_id and cdi.cdi_id=rep.cdi_id
left join(select * from model) md on md.md_id=rep.md_id
left join(select * from model_version) mv on mv.md_id=rep.md_id and mv.mv_id=rep.mv_id
left join(select * from buildup_logic) bul on bul.bul_id=rep.bul_id
where
 rep.rep_delcause is null and
 rep.ci_id=?  and
 rep.cb_id=?  and
 rep.md_id=?  and
 rep.mv_id=?  and
 rep.bul_id=? and
 rep.cdi_id=(select cdi_id from concept_data_info where ci_id=? and cdi_name=?)
SQL
		my $rep_id_sth = $dbh->prepare($sql);


		$sql=<<SQL;
select
 rep.rep_id,
 cdi.cdi_name,
 md.md_abbr,
 mv.mv_name_e,
 bul.bul_name_e
from
 representation as rep
left join(select * from concept_data_info) cdi on cdi.ci_id=rep.ci_id and cdi.cdi_id=rep.cdi_id
left join(select * from model) md on md.md_id=rep.md_id
left join(select * from model_version) mv on mv.md_id=rep.md_id and mv.mv_id=rep.mv_id
left join(select * from buildup_logic) bul on bul.bul_id=rep.bul_id
where
 rep.rep_delcause is null and
 rep.ci_id=?  and
 rep.cb_id=?  and
 rep.md_id=?  and
 rep.mv_id=?  and
 rep.bul_id=? and
 rep.cdi_id = (select cdi_id from concept_data_info where ci_id=? and lower(cdi_name_e)=lower(?))
SQL
		my $rep_name_sth = $dbh->prepare($sql);

#		use Clone;
#		my $sth_bul_all;
#		if($FORM{'bul_all'} eq 'true'){
#			my $sql = qq|select bul_id from buildup_logic where bul_use AND bul_id<>? order by bul_order|;
#			$sth_bul_all = $dbh->prepare($sql);
#		}

		foreach my $record (@$records){
			next unless(defined $record && ref $record eq 'HASH');
			foreach my $key (sort keys %$record){
				delete $record->{$key} if(exists $record->{$key} && defined $record->{$key} && $record->{$key} eq "");
			}
			$record->{'conv_id'} = undef;
			$record->{'common_id'} = undef;


			my $rep_id;
			my $cdi_name;
			my $md_abbr;
			my $mv_name;
			my $bul_name;
			my $form = &Clone::clone(\%FORM);

			delete $form->{'records'};
			&cgi_lib::common::message('$form='.&cgi_lib::common::encodeJSON($form,1), $LOG) if(defined $LOG);

			if(exists $record->{'f_id'} && defined $record->{'f_id'}){
				&cgi_lib::common::message('$record='.&cgi_lib::common::encodeJSON($record,1), $LOG) if(defined $LOG);
				$rep_id_sth->execute($form->{'ci_id'},$form->{'cb_id'},$form->{'md_id'},$form->{'mv_id'},$form->{'bul_id'},$form->{'ci_id'},$record->{'f_id'});
				if($rep_id_sth->rows>0){
					my $col_num=0;
					$rep_id_sth->bind_col(++$col_num, \$rep_id, undef);
					$rep_id_sth->bind_col(++$col_num, \$cdi_name, undef);
					$rep_id_sth->bind_col(++$col_num, \$md_abbr, undef);
					$rep_id_sth->bind_col(++$col_num, \$mv_name, undef);
					$rep_id_sth->bind_col(++$col_num, \$bul_name, undef);
					$rep_id_sth->fetch;
				}
				$rep_id_sth->finish;
				if(defined $LOG){
					&cgi_lib::common::message('$rep_id=['.$rep_id.']', $LOG) if(defined $rep_id);
					&cgi_lib::common::message('$cdi_name=['.$cdi_name.']', $LOG) if(defined $cdi_name);
					&cgi_lib::common::message('$md_abbr=['.$md_abbr.']', $LOG) if(defined $md_abbr);
					&cgi_lib::common::message('$mv_name=['.$mv_name.']', $LOG) if(defined $mv_name);
					&cgi_lib::common::message('$bul_name=['.$bul_name.']', $LOG) if(defined $bul_name);
				}
			}
			unless(defined $rep_id && defined $cdi_name && defined $mv_name && defined $bul_name){
				if(exists $record->{'name_e'} && defined $record->{'name_e'}){
					if($record->{'name_e'} =~ /^FMA[0-9]+$/){
						&cgi_lib::common::message('$record='.&cgi_lib::common::encodeJSON($record,1), $LOG) if(defined $LOG);
						$rep_id_sth->execute($form->{'ci_id'},$form->{'cb_id'},$form->{'md_id'},$form->{'mv_id'},$form->{'bul_id'},$form->{'ci_id'},$record->{'name_e'});
						if($rep_id_sth->rows>0){
							my $col_num=0;
							$rep_id_sth->bind_col(++$col_num, \$rep_id, undef);
							$rep_id_sth->bind_col(++$col_num, \$cdi_name, undef);
							$rep_id_sth->bind_col(++$col_num, \$md_abbr, undef);
							$rep_id_sth->bind_col(++$col_num, \$mv_name, undef);
							$rep_id_sth->bind_col(++$col_num, \$bul_name, undef);
							$rep_id_sth->fetch;
						}
						$rep_id_sth->finish;
						if(defined $LOG){
							&cgi_lib::common::message('$rep_id=['.$rep_id.']', $LOG) if(defined $rep_id);
							&cgi_lib::common::message('$cdi_name=['.$cdi_name.']', $LOG) if(defined $cdi_name);
							&cgi_lib::common::message('$md_abbr=['.$md_abbr.']', $LOG) if(defined $md_abbr);
							&cgi_lib::common::message('$mv_name=['.$mv_name.']', $LOG) if(defined $mv_name);
							&cgi_lib::common::message('$bul_name=['.$bul_name.']', $LOG) if(defined $bul_name);
						}
					}
					unless(defined $rep_id && defined $cdi_name && defined $mv_name && defined $bul_name){
						&cgi_lib::common::message('$record='.&cgi_lib::common::encodeJSON($record,1), $LOG) if(defined $LOG);
						$rep_name_sth->execute($form->{'ci_id'},$form->{'cb_id'},$form->{'md_id'},$form->{'mv_id'},$form->{'bul_id'},$form->{'ci_id'},$record->{'name_e'});
						if($rep_name_sth->rows>0){
							my $col_num=0;
							$rep_name_sth->bind_col(++$col_num, \$rep_id, undef);
							$rep_name_sth->bind_col(++$col_num, \$cdi_name, undef);
							$rep_name_sth->bind_col(++$col_num, \$md_abbr, undef);
							$rep_name_sth->bind_col(++$col_num, \$mv_name, undef);
							$rep_name_sth->bind_col(++$col_num, \$bul_name, undef);
							$rep_name_sth->fetch;
						}
						$rep_name_sth->finish;
						if(defined $LOG){
							&cgi_lib::common::message('$rep_id=['.$rep_id.']', $LOG) if(defined $rep_id);
							&cgi_lib::common::message('$cdi_name=['.$cdi_name.']', $LOG) if(defined $cdi_name);
							&cgi_lib::common::message('$md_abbr=['.$md_abbr.']', $LOG) if(defined $md_abbr);
							&cgi_lib::common::message('$mv_name=['.$mv_name.']', $LOG) if(defined $mv_name);
							&cgi_lib::common::message('$bul_name=['.$bul_name.']', $LOG) if(defined $bul_name);
						}
					}
				}
			}

#			next unless(defined $rep_id && defined $cdi_name && defined $mv_name && defined $bul_name);
			unless(defined $rep_id && defined $cdi_name && defined $mv_name && defined $bul_name){
				$record->{'b_id'} = undef;
				$record->{'conv_id'} = undef;
				$record->{'common_id'} = undef;
				next;
			}

			$record->{'b_id'} = $rep_id;
			$record->{'conv_id'} = $rep_id;
			$record->{'common_id'} = $cdi_name;
			$record->{'version'} = $mv_name;
			$record->{'f_id'} = $cdi_name unless(exists $record->{'f_id'} && defined $record->{'f_id'});

			$record->{'ci_id'} = $form->{'ci_id'};
			$record->{'cb_id'} = $form->{'cb_id'};
			$record->{'md_id'} = $form->{'md_id'};
			$record->{'mv_id'} = $form->{'mv_id'};
			$record->{'bul_id'} = $form->{'bul_id'};
			$record->{'tg_id'} = $form->{'md_id'};
			$record->{'tgi_id'} = $form->{'mv_id'};


			my $rtn = &getFMA($dbh,$form,$record->{'f_id'});
			my $url;
			my $path_str;
			if(defined $rtn && exists $rtn->{'zmax'} && defined $rtn->{'zmax'}){

				$FORM{'position'} = &getDefImagePosition() unless(exists $FORM{'position'} && defined $FORM{'position'});

				$url = &getImagePath($record->{'f_id'},$FORM{'position'},$FORM{'version'},'120x120',$FORM{'bul_id'},$credit);
				$path_str = &getGlobalPath();
				if(defined $path_str){
					$path_str .= qq|icon.cgi|;
				}else{
					my $host = (split(/,\s*/,(exists($ENV{'HTTP_X_FORWARDED_HOST'})?$ENV{'HTTP_X_FORWARDED_HOST'}:$ENV{'HTTP_HOST'})))[0];
					my @TEMP = split("/",$ENV{'REQUEST_URI'});
					$TEMP[$#TEMP] = qq|icon.cgi|;
					$path_str = join("/",@TEMP);
					$path_str = qq|http://$host$path_str|;
				}
				$path_str = qq|$path_str?i=|;
				if(exists $rtn->{b_id} && defined $rtn->{b_id}){
					$path_str .= &url_encode($rtn->{b_id}) . qq|&p=$FORM{'position'}|;
				}else{
					$path_str .= &url_encode($record->{'f_id'}) . qq|&p=|.&url_encode($FORM{'position'}).qq|&v=|.&url_encode($mv_name).qq|&t=|.&url_encode($bul_name).qq|&m=|.&url_encode($md_abbr);
					$path_str .= qq|&r=$root| if(defined $root && $root ne "" && $root ne $record->{'f_id'});
				}
				if(-e $url && -s $url){
					my $mtime = (stat($url))[9];
					$url .= "?$mtime";
				}else{
					$url = $path_str;
				}
			}else{
				$url = "icon/inprep.png";
			}

			if(defined $rtn && ref $rtn eq 'HASH'){
				foreach my $key (keys(%$rtn)){
					$record->{$key} = $rtn->{$key};
				}
			}
			$record->{'src'} = $url;
			$record->{'srcstr'} = $path_str;
		}
		undef $rep_id_sth;
		undef $rep_name_sth;

		$sql=<<SQL;
select
 rep.rep_id,
 cdi.cdi_name,
 md.md_abbr,
 mv.mv_name_e,
 bul.bul_name_e,
 rep.bul_id
from
 representation as rep
left join(select * from concept_data_info) cdi on cdi.ci_id=rep.ci_id and cdi.cdi_id=rep.cdi_id
left join(select * from model) md on md.md_id=rep.md_id
left join(select * from model_version) mv on mv.md_id=rep.md_id and mv.mv_id=rep.mv_id
left join(select * from buildup_logic) bul on bul.bul_id=rep.bul_id
where
 rep.rep_delcause is null and
 rep.ci_id=?  and
 rep.cb_id=?  and
 rep.md_id=?  and
 rep.mv_id=?  and
 rep.bul_id IN (select bul_id from buildup_logic where bul_use AND bul_id<>? order by bul_order) and
 rep.cdi_id=(select cdi_id from concept_data_info where ci_id=? and cdi_name=?)
order by
 rep.bul_id
SQL
		$rep_id_sth = $dbh->prepare($sql);

		$sql=<<SQL;
select
 rep.rep_id,
 cdi.cdi_name,
 md.md_abbr,
 mv.mv_name_e,
 bul.bul_name_e,
 rep.bul_id
from
 representation as rep
left join(select * from concept_data_info) cdi on cdi.ci_id=rep.ci_id and cdi.cdi_id=rep.cdi_id
left join(select * from model) md on md.md_id=rep.md_id
left join(select * from model_version) mv on mv.md_id=rep.md_id and mv.mv_id=rep.mv_id
left join(select * from buildup_logic) bul on bul.bul_id=rep.bul_id
where
 rep.rep_delcause is null and
 rep.ci_id=?  and
 rep.cb_id=?  and
 rep.md_id=?  and
 rep.mv_id=?  and
 rep.bul_id IN (select bul_id from buildup_logic where bul_use AND bul_id<>? order by bul_order) and
 rep.cdi_id = (select cdi_id from concept_data_info where ci_id=? and lower(cdi_name_e)=lower(?))
order by
 rep.bul_id
SQL
		$rep_name_sth = $dbh->prepare($sql);

		foreach my $record (@$records){
			foreach my $key (sort keys %$record){
				delete $record->{$key} if(exists $record->{$key} && defined $record->{$key} && $record->{$key} eq "");
			}
			next if(defined $record->{'conv_id'} || defined $record->{'common_id'});

			my $rep_id;
			my $cdi_name;
			my $md_abbr;
			my $mv_name;
			my $bul_name;
			my $bul_id;
			if(exists $record->{'f_id'} && defined $record->{'f_id'}){
				$rep_id_sth->execute($FORM{'ci_id'},$FORM{'cb_id'},$FORM{'md_id'},$FORM{'mv_id'},$FORM{'bul_id'},$FORM{'ci_id'},$record->{'f_id'});
				if($rep_id_sth->rows>0){
					my $col_num=0;
					$rep_id_sth->bind_col(++$col_num, \$rep_id, undef);
					$rep_id_sth->bind_col(++$col_num, \$cdi_name, undef);
					$rep_id_sth->bind_col(++$col_num, \$md_abbr, undef);
					$rep_id_sth->bind_col(++$col_num, \$mv_name, undef);
					$rep_id_sth->bind_col(++$col_num, \$bul_name, undef);
					$rep_id_sth->bind_col(++$col_num, \$bul_id, undef);
					while($rep_id_sth->fetch){
						last if(defined $rep_id && defined $cdi_name && defined $mv_name && defined $bul_name && defined $bul_id);
					}
				}
				$rep_id_sth->finish;

			}elsif(exists $record->{'name_e'} && defined $record->{'name_e'}){
				if($record->{'name_e'} =~ /^FMA[0-9]+$/){
					$rep_id_sth->execute($FORM{'ci_id'},$FORM{'cb_id'},$FORM{'md_id'},$FORM{'mv_id'},$FORM{'bul_id'},$FORM{'ci_id'},$record->{'name_e'});
					if($rep_id_sth->rows>0){
						my $col_num=0;
						$rep_id_sth->bind_col(++$col_num, \$rep_id, undef);
						$rep_id_sth->bind_col(++$col_num, \$cdi_name, undef);
						$rep_id_sth->bind_col(++$col_num, \$md_abbr, undef);
						$rep_id_sth->bind_col(++$col_num, \$mv_name, undef);
						$rep_id_sth->bind_col(++$col_num, \$bul_name, undef);
						$rep_id_sth->bind_col(++$col_num, \$bul_id, undef);
						while($rep_id_sth->fetch){
							last if(defined $rep_id && defined $cdi_name && defined $mv_name && defined $bul_name && defined $bul_id);
						}
					}
					$rep_id_sth->finish;
				}
				unless(defined $rep_id && defined $cdi_name && defined $mv_name && defined $bul_name && defined $bul_id){
					$rep_name_sth->execute($FORM{'ci_id'},$FORM{'cb_id'},$FORM{'md_id'},$FORM{'mv_id'},$FORM{'bul_id'},$FORM{'ci_id'},$record->{'name_e'});
					if($rep_name_sth->rows>0){
						my $col_num=0;
						$rep_name_sth->bind_col(++$col_num, \$rep_id, undef);
						$rep_name_sth->bind_col(++$col_num, \$cdi_name, undef);
						$rep_name_sth->bind_col(++$col_num, \$md_abbr, undef);
						$rep_name_sth->bind_col(++$col_num, \$mv_name, undef);
						$rep_name_sth->bind_col(++$col_num, \$bul_name, undef);
						$rep_name_sth->bind_col(++$col_num, \$bul_id, undef);
						while($rep_name_sth->fetch){
							last if(defined $rep_id && defined $cdi_name && defined $mv_name && defined $bul_name && defined $bul_id);
						}
					}
					$rep_name_sth->finish;
				}
			}

			next unless(defined $rep_id && defined $cdi_name && defined $mv_name && defined $bul_name && defined $bul_id);

			$record->{'b_id'} = $rep_id;
			$record->{'conv_id'} = $rep_id;
			$record->{'common_id'} = $cdi_name;
			$record->{'version'} = $mv_name;
			$record->{'bul_id'} = $bul_id;
			$record->{'f_id'} = $cdi_name unless(exists $record->{'f_id'} && defined $record->{'f_id'});

			my $form = &Clone::clone(\%FORM);
			$form->{'bul_id'} = $form->{'t_type'} = $bul_id;

			$record->{'ci_id'} = $form->{'ci_id'};
			$record->{'cb_id'} = $form->{'cb_id'};
			$record->{'md_id'} = $form->{'md_id'};
			$record->{'mv_id'} = $form->{'mv_id'};
#			$record->{'bul_id'} = $form->{'bul_id'};
			$record->{'tg_id'} = $form->{'md_id'};
			$record->{'tgi_id'} = $form->{'mv_id'};


			my $rtn = &getFMA($dbh,$form,$record->{'f_id'});
			my $url;
			my $path_str;
			if(defined $rtn && exists $rtn->{'zmax'} && defined $rtn->{'zmax'}){

				$FORM{'position'} = &getDefImagePosition() unless(exists $FORM{'position'} && defined $FORM{'position'});

				$url = &getImagePath($record->{'f_id'},$form->{'position'},$form->{'version'},'120x120',$form->{'bul_id'},$credit);
				$path_str = &getGlobalPath();
				if(defined $path_str){
					$path_str .= qq|icon.cgi|;
				}else{
					my $host = (split(/,\s*/,(exists($ENV{'HTTP_X_FORWARDED_HOST'})?$ENV{'HTTP_X_FORWARDED_HOST'}:$ENV{'HTTP_HOST'})))[0];
					my @TEMP = split("/",$ENV{'REQUEST_URI'});
					$TEMP[$#TEMP] = qq|icon.cgi|;
					$path_str = join("/",@TEMP);
					$path_str = qq|http://$host$path_str|;
				}
				$path_str = qq|$path_str?i=|;
				if(exists $rtn->{b_id} && defined $rtn->{b_id}){
					$path_str .= &url_encode($rtn->{b_id}) . qq|&p=$FORM{'position'}|;
				}else{
					$path_str .= &url_encode($record->{'f_id'}) . qq|&p=|.&url_encode($form->{'position'}).qq|&v=|.&url_encode($mv_name).qq|&t=|.&url_encode($bul_name).qq|&m=|.&url_encode($md_abbr);
					$path_str .= qq|&r=$root| if(defined $root && $root ne "" && $root ne $record->{'f_id'});
				}
				if(-e $url && -s $url){
					my $mtime = (stat($url))[9];
					$url .= "?$mtime";
				}else{
					$url = $path_str;
				}
			}else{
				$url = "icon/inprep.png";
			}

			if(defined $rtn && ref $rtn eq 'HASH'){
				foreach my $key (keys(%$rtn)){
					$record->{$key} = $rtn->{$key};
				}
			}
			$record->{'src'} = $url;
			$record->{'srcstr'} = $path_str;
		}
		undef $rep_id_sth;
		undef $rep_name_sth;




		push(@{$RTN->{'records'}},@$records);
		$RTN->{success} = JSON::XS::true;

	#	print LOG __LINE__,":",$json,"\n";
	};
	if($@){
		my $msg = $@;
		$msg =~ s/\s*$//g;
		$msg =~ s/^\s*//g;
		$RTN->{'msg'} = $msg;
	#	print LOG __LINE__,":",$json,"\n";
	}
}

&cgi_lib::common::printContentJSON($RTN);
&cgi_lib::common::message('$RTN='.&cgi_lib::common::encodeJSON($RTN,1), $LOG) if(defined $LOG);

#my $json = &JSON::XS::encode_json($RTN);
#print $json;

#close(LOG);
exit;
