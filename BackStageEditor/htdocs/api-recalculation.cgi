#!/bp3d/local/perl/bin/perl

$| = 1;

use constant {
	DEBUG => 1
};

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use Digest::MD5;
use Time::HiRes;
use File::Spec::Functions qw(abs2rel rel2abs catdir catfile splitdir);
use Time::HiRes;

my $t0 = [&Time::HiRes::gettimeofday()];

use Data::Dumper;
$Data::Dumper::Indent = 1;
$Data::Dumper::Sortkeys = 1;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
require "webgl_common.pl";
use cgi_lib::common;

use BITS::ConceptArtMapModified;
use BITS::ReCalc;

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
if(exists $ENV{'REQUEST_METHOD'}){
	my $query = CGI->new;
	&getParams($query,\%FORM,\%COOKIE);
}elsif(DEBUG){
=pod
	$FORM{'limit'} = 50;
	$FORM{'cmd'} = qq|read|;
#	$FORM{'cdi_names'} = qq|["FMA15745"]|;
#	$FORM{'cdi_names'} = qq|["FMA62955"]|;
	$FORM{'cdi_names'} = qq|["FMA3895"]|;
	$FORM{'model'} = qq|bp3d|;
	$FORM{'version'} = qq|4.1|;
	$FORM{'ag_data'} = qq|obj/bp3d/4.1|;
	$FORM{'tree'} = qq|isa|;
	$FORM{'md_id'} = 1;
	$FORM{'mv_id'} = 4;
	$FORM{'mr_id'} = 1;
	$FORM{'ci_id'} = 1;
	$FORM{'cb_id'} = 4;
	$FORM{'bul_id'} = 3;
=cut

=pod
	$FORM{_ExtVerBuild}=883;
	$FORM{_ExtVerMajor}=4;
	$FORM{_ExtVerMinor}=2;
	$FORM{_ExtVerPatch}=1;
	$FORM{_ExtVerRelease}='';
	$FORM{_dc}=1402023036369;
	$FORM{ag_data}=qq|obj/bp3d/5.0|;
	$FORM{bul_id}=3;
	$FORM{cb_id}=6;
	$FORM{cdi_names}=qq|["FMA62955"]|;
#	$FORM{'cdi_names'} = qq|["FMA3895"]|;
	$FORM{ci_id}=1;
	$FORM{cmd}=qq|read|;
	$FORM{'limit'}=500;
	$FORM{md_id}=1;
	$FORM{model}=qq|bp3d|;
	$FORM{mr_id}=1;
	$FORM{mv_id}=7;
	$FORM{tree}=qq|isa|;
	$FORM{version}=qq|5.0|;

#	$FORM{cdi_names}=qq|["FMA15746"]|;
	$FORM{cb_id}=5;
	$FORM{mv_id}=6;


	$FORM{_ExtVerBuild}=883;
	$FORM{_ExtVerMajor}=4;
	$FORM{_ExtVerMinor}=2;
	$FORM{_ExtVerPatch}=1;
	$FORM{_ExtVerRelease}='';
	$FORM{_dc}=1408920522354;
	$FORM{ag_data}='obj/bp3d/5.0brain';
	$FORM{bul_id}=3;
	$FORM{cb_id}=7;
	$FORM{cdi_names}=qq|["FMA62955"]|;
	$FORM{ci_id}=1;
	$FORM{cmd}='read';
	$FORM{'limit'}=500;
	$FORM{md_id}=1;
	$FORM{model}='bp3d';
	$FORM{mr_id}=1;
	$FORM{mv_id}=8;
	$FORM{tree}='isa';
	$FORM{version}='5.0brain'
=cut

	$FORM{'md_id'} = 1;
	$FORM{'mv_id'} = 24;
	$FORM{'mr_id'} = 1;
	$FORM{'ci_id'} = 1;
	$FORM{'cb_id'} = 11;
	$FORM{'bul_id'} = 3;
	$FORM{'force'} = 'true';
#	$FORM{'cdi_names'} = '["FMA37463"]';
	$FORM{'cdi_names'} = '[]';

}

my($logfile,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

=pod
$FORM{ag_data}=qq|obj/bp3d/4.0|;
$FORM{f_id}=qq|root|;
$FORM{model}=qq|bp3d|;
$FORM{node}=qq|root|;
$FORM{tree}=qq|isa|;
$FORM{version}=qq|4.0|;
=cut

my $cookie_path="/";
if(exists $ENV{'REQUEST_URI'} && defined $ENV{'REQUEST_URI'}){
	$cookie_path=$ENV{'REQUEST_URI'};
	$cookie_path=~s/[^\/]*$//g;
}elsif(exists $ENV{'SCRIPT_URL'} && defined $ENV{'SCRIPT_URL'}){
	$cookie_path=$ENV{'SCRIPT_URL'};
	$cookie_path=~s/[^\/]*$//g;
}

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
#my STDERR;
if(exists $ENV{'REQUEST_METHOD'}){
	if(DEBUG){
		$logfile .= '.'.$FORM{'cmd'} if(exists $FORM{'cmd'} && defined $FORM{'cmd'});
#		$logfile .= '.'.sprintf("%04d%02d%02d%02d",$year+1900,$mon+1,$mday,$hour);
		close(STDERR);
		open(STDERR,">> $logfile");
		select(STDERR);
		$| = 1;
		select(STDOUT);

		flock(STDERR,2);
		print STDERR "\n[$logtime]:$0\n";
#		print STDERR __LINE__,":",&Data::Dumper::Dumper(\%FORM),"\n";
		&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%ENV,1));
#		&cgi_lib::common::message(cgi_lib::common::encodeJSON(\%ENV,1));
		&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM,1));
#		&cgi_lib::common::message(cgi_lib::common::encodeJSON(\%FORM,1));
#		foreach my $key (sort keys(%FORM)){
#			print STDERR __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#		}
#foreach my $key (sort keys(%COOKIE)){
#	print STDERR "\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
#}
#foreach my $key (sort keys(%ENV)){
#	print STDERR __LINE__,":\$ENV{$key}=[",$ENV{$key},"]\n";
#}
	}
}elsif(DEBUG){
#	STDERR = STDERR;
}
#&setDefParams(\%FORM,\%COOKIE);
#foreach my $key (sort keys(%FORM)){
#	print STDERR __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}

#&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
#foreach my $key (sort keys(%FORM)){
#	print STDERR __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}


my $DATAS = {
	'datas'   => [],
	'total'   => 0,
	'msg'     => undef,
	'success' => JSON::XS::false
};

if(DEBUG){
	$FORM{'cmd'} = 'read' unless(defined $FORM{'cmd'});
}

unless(
	defined $FORM{'cmd'}
){
#	print &JSON::XS::encode_json($DATAS);
	&gzip_json($DATAS);
	exit;
}

if($FORM{'cmd'} eq 'read'){
	eval{
		my $cdi_names = &cgi_lib::common::decodeJSON($FORM{'cdi_names'});
		my $cdi_ids;
		my $cdi_pids;
		my $ci_id = $FORM{'ci_id'};
		my $cb_id = $FORM{'cb_id'};

		my $md_id = $FORM{'md_id'};
		my $mv_id = $FORM{'mv_id'};
		my $mr_id = $FORM{'mr_id'};

		&cgi_lib::common::message('tv_interval('.$$.'):'.&Time::HiRes::tv_interval($t0)) if(DEBUG);

		if(exists $FORM{'force'} && defined $FORM{'force'} && $FORM{'force'} eq 'true'){
			$dbh->{'AutoCommit'} = 0;
			$dbh->{'RaiseError'} = 1;
			eval{
				my $sql_rep_upd = sprintf(qq|update representation set rep_delcause='[%s] force' where md_id=$md_id and mv_id=$mv_id|,$0);
				&cgi_lib::common::message($sql_rep_upd) if(DEBUG);
				my $rows_rep_upd = $dbh->do($sql_rep_upd) or die $dbh->errstr;
				&cgi_lib::common::message($rows_rep_upd) if(DEBUG);


				my $sql_cmm_del_modified = qq|delete from concept_art_map_modified where md_id=$md_id and mv_id=$mv_id|;
				&cgi_lib::common::message($sql_cmm_del_modified) if(DEBUG);
				my $del_rows = $dbh->do($sql_cmm_del_modified) or die $dbh->errstr;
				&cgi_lib::common::message($del_rows) if(DEBUG);

				my $sth_cm_sel = $dbh->prepare(qq|select cdi_id from concept_art_map where cm_use and cm_delcause is null and (md_id,mv_id,mr_id,cdi_id) in (select md_id,mv_id,max(mr_id),cdi_id from concept_art_map where md_id=? and mv_id=? and mr_id<=? group by md_id,mv_id,cdi_id) group by cdi_id|) or die $dbh->errstr;
				$sth_cm_sel->execute($md_id,$mv_id,$mr_id) or die $dbh->errstr;
				&cgi_lib::common::message($sth_cm_sel->rows()) if(DEBUG);
				my $column_number = 0;
				my $cdi_id;
				$sth_cm_sel->bind_col(++$column_number, \$cdi_id,   undef);
				while($sth_cm_sel->fetch){
					next unless(defined $cdi_id);
					$cdi_ids->{$cdi_id} = undef;
				}
				$sth_cm_sel->finish;
				undef $sth_cm_sel;

&cgi_lib::common::message(scalar keys(%$cdi_ids));

				if(scalar keys(%$cdi_ids)){
					my $CM_MODIFIED = &BITS::ConceptArtMapModified::exec(
							dbh => $dbh,
							ci_id => $ci_id,
							cb_id => $cb_id,
							md_id => $md_id,
							mv_id => $mv_id,
							mr_id => $mr_id,
							cdi_ids => [keys(%$cdi_ids)],
							LOG => \*STDERR
					);
					if(defined $CM_MODIFIED && ref $CM_MODIFIED eq 'HASH'){
						&cgi_lib::common::message(scalar keys(%$CM_MODIFIED));
#						&cgi_lib::common::message($CM_MODIFIED);

					}
				}
				undef $cdi_ids;

&cgi_lib::common::message('');


				$dbh->commit();
			};
			if($@){
				$DATAS->{'success'} = JSON::XS::false;
				$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8($@);
				&cgi_lib::common::message($DATAS->{'msg'}) if(DEBUG);
				$dbh->rollback();
			}
			$dbh->{'AutoCommit'} = 1;
			$dbh->{'RaiseError'} = 0;
#			exit;
		}

		&cgi_lib::common::message('tv_interval('.$$.'):'.&Time::HiRes::tv_interval($t0)) if(DEBUG);

		if(defined $cdi_names && ref $cdi_names eq 'ARRAY' && scalar @$cdi_names){
			undef $cdi_ids;
			$cdi_ids = &BITS::ReCalc::check(
				dbh => $dbh,
				ci_id => $ci_id,
				cb_id => $cb_id,

				md_id => $md_id,
				mv_id => $mv_id,
				mr_id => $mr_id,

				cdi_names => $cdi_names
			);
			&cgi_lib::common::message('tv_interval('.$$.'):'.&Time::HiRes::tv_interval($t0)) if(DEBUG);
			&cgi_lib::common::message(scalar keys(%$cdi_ids)) if(DEBUG && defined $cdi_ids && ref $cdi_ids eq 'HASH');
		}else{
			$cdi_ids = &BITS::ReCalc::check(
				dbh => $dbh,
				ci_id => $ci_id,
				cb_id => $cb_id,
				md_id => $md_id,
				mv_id => $mv_id,
				mr_id => $mr_id
			);
			&cgi_lib::common::message('tv_interval('.$$.'):'.&Time::HiRes::tv_interval($t0)) if(DEBUG);
			&cgi_lib::common::message(scalar keys(%$cdi_ids)) if(DEBUG && defined $cdi_ids && ref $cdi_ids eq 'HASH');
		}

		if(defined $cdi_ids){
#			&cgi_lib::common::message(scalar keys(%$cdi_ids)) if(DEBUG);

			my @SORT;
			if(defined $FORM{'sort'}){
				my $sorts = &cgi_lib::common::decodeJSON($FORM{'sort'});
				push(@SORT,@$sorts) if(defined $sorts && ref $sorts eq 'ARRAY');
			}
			if(scalar @SORT == 0){
				push(@SORT,{
					property  => 'cdi_name',
					direction => 'ASC'
				});
			}
			my $sql=<<SQL;
select 
 cdi.cdi_id,
 cdi.cdi_name,
 cdi.cdi_name_j,
 COALESCE(cd.cd_name,bd.cd_name,cdi.cdi_name_e),
 cdi.cdi_name_k,
 cdi.cdi_name_l,
 cdi.cdi_syn_j,
 COALESCE(cd.cd_syn,bd.cd_syn,cdi.cdi_syn_e),
 cdi.cdi_def_j,
 COALESCE(cd.cd_def,bd.cd_def,cdi.cdi_def_e),
 cdi.cdi_taid,
 rep.rep_id,
 but.bul_id,
 bti.but_depth,
 rep.ci_id,
 rep.cb_id,
 rep.md_id,
 rep.mv_id,
 rep.mr_id,
 bul.bul_name_e,
 bul.bul_abbr
from
 buildup_tree as but

left join (
 select * from buildup_logic
) as bul on
   but.bul_id=bul.bul_id

left join (
 select
  *
 from
  buildup_tree_info
 where
  md_id=$md_id AND
  mv_id=$mv_id AND
  mr_id=$mr_id

) as bti on
   bti.bul_id=but.bul_id AND
   bti.cdi_id=but.cdi_id

left join (
 select * from concept_data_info
) as cdi on
   but.ci_id=cdi.ci_id AND
   but.cdi_id=cdi.cdi_id

left join (
 select * from concept_data where ci_id=$ci_id and cb_id=$cb_id
) as cd on
   but.cdi_id=cd.cdi_id

left join (
 select * from buildup_data where md_id=$md_id and mv_id=$mv_id and mr_id=$mr_id
) as bd on
   but.cdi_id=bd.cdi_id

left join (
  select * from representation where (md_id,mv_id,mr_id,bul_id,cdi_id) in (
    select
     md_id,mv_id,max(mr_id),bul_id,cdi_id
    from
     representation
    where
     md_id=$md_id AND
     mv_id=$mv_id AND
     mr_id<=$mr_id
    group by
     md_id,mv_id,bul_id,cdi_id
  )

) as rep on
   but.bul_id=rep.bul_id AND
   but.cdi_id=rep.cdi_id

where
 bul.bul_use AND
 but.md_id=$md_id AND
 but.mv_id=$mv_id AND
 but.mr_id=$mr_id
SQL

			my $h;
			foreach my $cdi_id (keys(%$cdi_ids)){
				foreach my $bul_id (keys(%{$cdi_ids->{$cdi_id}})){
					push(@{$h->{$bul_id}},$cdi_id);
				}
			}
			my $w;
			foreach my $bul_id (keys(%$h)){
				push(@$w,qq|(but.bul_id=$bul_id AND cdi.cdi_id in (|. join(",",sort {$a<=>$b} @{$h->{$bul_id}}) . qq|))|);
				&cgi_lib::common::message('$bul_id=['.$bul_id.']['.(scalar @{$h->{$bul_id}}).']') if(DEBUG);
			}
			if(defined $w){
				$sql .= qq| AND (| . join(" OR ",@$w) . qq|)\n|;
			}
#=pod
			$sql.=<<SQL;
group by
 cdi.cdi_id,
 cdi.cdi_name,
 cdi.cdi_name_j,
 COALESCE(cd.cd_name,bd.cd_name,cdi.cdi_name_e),
 cdi.cdi_name_k,
 cdi.cdi_name_l,
 cdi.cdi_syn_j,
 COALESCE(cd.cd_syn,bd.cd_syn,cdi.cdi_syn_e),
 cdi.cdi_def_j,
 COALESCE(cd.cd_def,bd.cd_def,cdi.cdi_def_e),
 cdi.cdi_taid,
 rep.rep_id,
 but.bul_id,
 bti.but_depth,
 rep.ci_id,
 rep.cb_id,
 rep.md_id,
 rep.mv_id,
 rep.mr_id,
 bul.bul_name_e,
 bul.bul_abbr
SQL
#=cut
			$sql .= qq| order by but.bul_id,bti.but_depth desc|;

			&cgi_lib::common::message($sql) if(DEBUG);

			&cgi_lib::common::message('tv_interval('.$$.'):'.&Time::HiRes::tv_interval($t0)) if(DEBUG);

			my $sth = $dbh->prepare($sql) or die $dbh->errstr;
			$sth->execute() or die $dbh->errstr;

			&cgi_lib::common::message('tv_interval('.$$.'):'.&Time::HiRes::tv_interval($t0)) if(DEBUG);

			$DATAS->{'total'} = $sth->rows();
			&cgi_lib::common::message('$DATAS->{total}=['.$DATAS->{'total'}.']') if(DEBUG);

			my $cdi_id;
			my $cdi_name;
			my $cdi_name_j;
			my $cdi_name_e;
			my $cdi_name_k;
			my $cdi_name_l;
			my $cdi_syn_j;
			my $cdi_syn_e;
			my $cdi_def_j;
			my $cdi_def_e;
			my $cdi_taid;
			my $rep_id;
			my $bul_id;
			my $but_depth;
			my $rep_ci_id;
			my $rep_cb_id;
			my $rep_md_id;
			my $rep_mv_id;
			my $rep_mr_id;
			my $bul_name_e;
			my $bul_abbr;

#			my $sth_but_cids = $dbh->prepare("select but_cids from buildup_tree_info where md_id=$md_id and mv_id=$mv_id and mr_id=$mr_id and ci_id=$ci_id and cb_id=$cb_id and bul_id=? and cdi_id=?") or die $dbh->errstr;
			my $sth_but_cids = $dbh->prepare("select but_cids from buildup_tree_info where md_id=$md_id and mv_id=$mv_id and mr_id=$mr_id and bul_id=? and cdi_id=?") or die $dbh->errstr;
##			my $sth_but_depth = $dbh->prepare("select max(but_depth) from buildup_tree_info where md_id=$md_id and mv_id=$mv_id and mr_id=$mr_id and ci_id=$ci_id and cb_id=$cb_id and bul_id=?") or die $dbh->errstr;
#			my $sth_but_depth = $dbh->prepare("select max(but_depth) from buildup_tree_info where md_id=$md_id and mv_id=$mv_id and mr_id=$mr_id and bul_id=?") or die $dbh->errstr;

			my $column_number = 0;
			$sth->bind_col(++$column_number, \$cdi_id,   undef);
			$sth->bind_col(++$column_number, \$cdi_name,   undef);
			$sth->bind_col(++$column_number, \$cdi_name_j,   undef);
			$sth->bind_col(++$column_number, \$cdi_name_e,   undef);
			$sth->bind_col(++$column_number, \$cdi_name_k,   undef);
			$sth->bind_col(++$column_number, \$cdi_name_l,   undef);
			$sth->bind_col(++$column_number, \$cdi_syn_j,   undef);
			$sth->bind_col(++$column_number, \$cdi_syn_e,   undef);
			$sth->bind_col(++$column_number, \$cdi_def_j,   undef);
			$sth->bind_col(++$column_number, \$cdi_def_e,   undef);
			$sth->bind_col(++$column_number, \$cdi_taid,   undef);
			$sth->bind_col(++$column_number, \$rep_id,   undef);
			$sth->bind_col(++$column_number, \$bul_id,   undef);
			$sth->bind_col(++$column_number, \$but_depth,   undef);
			$sth->bind_col(++$column_number, \$rep_ci_id,   undef);
			$sth->bind_col(++$column_number, \$rep_cb_id,   undef);
			$sth->bind_col(++$column_number, \$rep_md_id,   undef);
			$sth->bind_col(++$column_number, \$rep_mv_id,   undef);
			$sth->bind_col(++$column_number, \$rep_mr_id,   undef);
			$sth->bind_col(++$column_number, \$bul_name_e,   undef);
			$sth->bind_col(++$column_number, \$bul_abbr,   undef);

			my %all_datas;
#			my %max_but_depth;

			while($sth->fetch){

				next unless(defined $cdi_id);

				my $HASH = {
#					ci_id     => $rep_ci_id || $ci_id+0,
#					cb_id     => $rep_cb_id || $cb_id+0,
#					md_id     => $rep_md_id || $md_id+0,
#					mv_id     => $rep_mv_id || $mv_id+0,
#					mr_id     => $rep_mr_id || $mr_id+0,
					ci_id     => $ci_id+0,
					cb_id     => $cb_id+0,
					md_id     => $md_id+0,
					mv_id     => $mv_id+0,
					mr_id     => $mr_id+0,
					cdi_id    => $cdi_id,
					bul_id    => $bul_id + 0,
					rep_id    => $rep_id,
					but_depth => $but_depth+0
				};

#				unless(exists $max_but_depth{$bul_id}){
#					$sth_but_depth->execute($bul_id) or die $dbh->errstr;
#					$column_number = 0;
#					$sth_but_depth->bind_col(++$column_number, \$but_depth,   undef);
#					$sth_but_depth->fetch;
#					$sth_but_depth->finish;
#					$max_but_depth{$bul_id} = $but_depth + 0 if(defined $but_depth);
#				}

				$all_datas{$bul_id}->{$cdi_id} = $HASH;
				$sth_but_cids->execute($bul_id,$cdi_id) or die $dbh->errstr;
				$column_number = 0;
				my $but_cids;
				$sth_but_cids->bind_col(++$column_number, \$but_cids,   undef);
				$sth_but_cids->fetch;
				$sth_but_cids->finish;
				if(defined $but_cids){
					$all_datas{$bul_id}->{$cdi_id}->{'but_cids'} = &JSON::XS::decode_json($but_cids);
				}else{
					$all_datas{$bul_id}->{$cdi_id}->{'but_cids'} = undef;
				}
				push(@{$DATAS->{'all_datas'}},$HASH);
			}
			$sth->finish;
			undef $sth;

			&cgi_lib::common::message('tv_interval('.$$.'):'.&Time::HiRes::tv_interval($t0)) if(DEBUG);
#die __LINE__;

			delete $_->{'but_cids'} for @{$DATAS->{'all_datas'}};

			&cgi_lib::common::message('tv_interval('.$$.'):'.&Time::HiRes::tv_interval($t0)) if(DEBUG);

			@{$DATAS->{'all_datas'}} = sort {$a->{'bul_id'} <=> $b->{'bul_id'}} sort {$b->{'but_depth'} <=> $a->{'but_depth'}} @{$DATAS->{'all_datas'}};

			&cgi_lib::common::message('tv_interval('.$$.'):'.&Time::HiRes::tv_interval($t0)) if(DEBUG);
#			&cgi_lib::common::message('$DATAS->{total}=['.$DATAS->{'total'}.']') if(DEBUG);
#			&cgi_lib::common::message(&cgi_lib::common::encodeJSON($DATAS->{'all_datas'},1)) if(DEBUG);


			$sql .= qq| limit $FORM{'limit'}| if(exists $FORM{'limit'} && defined $FORM{'limit'} && $FORM{'limit'} =~ /^[0-9]+$/);
			$sql .= qq| offset $FORM{'start'}| if(exists $FORM{'start'} && defined $FORM{'start'} && $FORM{'start'} =~ /^[0-9]+$/);

#			print STDERR __LINE__,":\$sql=[$sql]\n" if(DEBUG);

			&cgi_lib::common::message('tv_interval('.$$.'):'.&Time::HiRes::tv_interval($t0)) if(DEBUG);

			$sth = $dbh->prepare($sql) or die $dbh->errstr;
			$sth->execute() or die $dbh->errstr;

			&cgi_lib::common::message('tv_interval('.$$.'):'.&Time::HiRes::tv_interval($t0)) if(DEBUG);

			undef $cdi_id;
			undef $cdi_name;
			undef $cdi_name_j;
			undef $cdi_name_e;
			undef $cdi_name_k;
			undef $cdi_name_l;
			undef $cdi_syn_j;
			undef $cdi_syn_e;
			undef $cdi_def_j;
			undef $cdi_def_e;
			undef $cdi_taid;
			undef $rep_id;
			undef $bul_id;
			undef $but_depth;
			undef $rep_ci_id;
			undef $rep_cb_id;
			undef $rep_md_id;
			undef $rep_mv_id;
			undef $rep_mr_id;
			undef $bul_name_e;
			undef $bul_abbr;

			$column_number = 0;
			$sth->bind_col(++$column_number, \$cdi_id,     undef);
			$sth->bind_col(++$column_number, \$cdi_name,   undef);
			$sth->bind_col(++$column_number, \$cdi_name_j, undef);
			$sth->bind_col(++$column_number, \$cdi_name_e, undef);
			$sth->bind_col(++$column_number, \$cdi_name_k, undef);
			$sth->bind_col(++$column_number, \$cdi_name_l, undef);
			$sth->bind_col(++$column_number, \$cdi_syn_j,  undef);
			$sth->bind_col(++$column_number, \$cdi_syn_e,  undef);
			$sth->bind_col(++$column_number, \$cdi_def_j,  undef);
			$sth->bind_col(++$column_number, \$cdi_def_e,  undef);
			$sth->bind_col(++$column_number, \$cdi_taid,   undef);
			$sth->bind_col(++$column_number, \$rep_id,     undef);
			$sth->bind_col(++$column_number, \$bul_id,     undef);
			$sth->bind_col(++$column_number, \$but_depth,  undef);
			$sth->bind_col(++$column_number, \$rep_ci_id,  undef);
			$sth->bind_col(++$column_number, \$rep_cb_id,  undef);
			$sth->bind_col(++$column_number, \$rep_md_id,  undef);
			$sth->bind_col(++$column_number, \$rep_mv_id,  undef);
			$sth->bind_col(++$column_number, \$rep_mr_id,  undef);
			$sth->bind_col(++$column_number, \$bul_name_e, undef);
			$sth->bind_col(++$column_number, \$bul_abbr,   undef);

			$column_number = 0;

			while($sth->fetch){

				next unless(defined $cdi_name);

				$cdi_syn_e =~ s/(;)/$1<br>/g if(defined $cdi_syn_e);


#				my $bul_type;
#				if($bul_id==2){
#					$bul_type = 'both';
#				}elsif($bul_id==3){
#					$bul_type = 'is_a';
#				}elsif($bul_id==4){
#					$bul_type = 'part_of';
#				}

unless(exists $ENV{'REQUEST_METHOD'}){
	$column_number++;
	print STDERR sprintf("%2d\t%2d\t%-10s\t%-9s\t%-7s\t%-7s\t%s\n",$column_number,$but_depth,$cdi_ids->{$cdi_id}->{$bul_id},$cdi_name,$bul_name_e,defined $rep_id ? $rep_id : '',$cdi_name_e);
}

				my $HASH = {
#					ci_id      => $rep_ci_id || $ci_id+0,
#					cb_id      => $rep_cb_id || $cb_id+0,
#					md_id      => $rep_md_id || $md_id+0,
#					mv_id      => $rep_mv_id || $mv_id+0,
#					mr_id      => $rep_mr_id || $mr_id+0,
					ci_id      => $ci_id+0,
					cb_id      => $cb_id+0,
					md_id      => $md_id+0,
					mv_id      => $mv_id+0,
					mr_id      => $mr_id+0,
					cdi_id     => $cdi_id + 0,
					cdi_name   => $cdi_name,
#					cdi_name_j => $cdi_name_j,
					cdi_name_e => $cdi_name_e,
#					cdi_name_k => $cdi_name_k,
#					cdi_name_l => $cdi_name_l,
#					cdi_syn_j  => $cdi_syn_j,
#					cdi_syn_e  => $cdi_syn_e,
#					cdi_def_j  => $cdi_def_j,
#					cdi_def_e  => $cdi_def_e,
#					cdi_taid   => $cdi_taid,
					rep_id     => $rep_id,
					bul_id     => $bul_id + 0,
					bul_name_e => $bul_name_e,
					bul_abbr   => $bul_abbr,
					but_depth  => exists $all_datas{$bul_id}->{$cdi_id}->{'but_depth'} ? $all_datas{$bul_id}->{$cdi_id}->{'but_depth'} : $but_depth,

					style => (exists $cdi_ids->{$cdi_id} && exists $cdi_ids->{$cdi_id}->{$bul_id} && defined $cdi_ids->{$cdi_id}->{$bul_id} && $cdi_ids->{$cdi_id}->{$bul_id} =~ /^delete/) ? qq|color:red;text-decoration:line-through;| : (defined $rep_id ? undef : 'color:blue;')

				};

				push(@{$DATAS->{'datas'}},$HASH);
			}
			$sth->finish;
			undef $sth;

			@{$DATAS->{'datas'}} = sort {$a->{'bul_id'} <=> $b->{'bul_id'}} sort {$b->{'but_depth'} <=> $a->{'but_depth'}} @{$DATAS->{'datas'}};

		}
		$DATAS->{'total'} -= 0;
		$DATAS->{'success'} = JSON::XS::true;
		&cgi_lib::common::message('tv_interval('.$$.'):'.&Time::HiRes::tv_interval($t0)) if(DEBUG);
	};
	if($@){
		$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8($@);
		&cgi_lib::common::message($DATAS->{'msg'}) if(DEBUG);
	}
}
elsif($FORM{'cmd'} eq 'recalc'){
	eval{
		$DATAS->{'sessionID'} = &recalc(\%FORM);
		if(defined $DATAS->{'sessionID'}){
			$DATAS->{'success'} = JSON::XS::true;
		}else{
			$DATAS->{'msg'} = qq|???|;
		}
	};
	if($@){
		$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8($@);
		&cgi_lib::common::message($DATAS->{'msg'}) if(DEBUG);
	}
}
elsif($FORM{'cmd'} eq 'recalc-progress'){
	eval{
		if($ENV{'HTTP_ACCEPT'} eq 'text/event-stream'){
			print qq|Content-type: $ENV{'HTTP_ACCEPT'}\n\n|;
			while(1){
				$DATAS->{'success'} = JSON::XS::false;
				delete $DATAS->{'sessionID'};
				$DATAS->{'progress'} = &recalc_progress(\%FORM);
				if(defined $DATAS->{'progress'}){
					$DATAS->{'success'} = JSON::XS::true;
					$DATAS->{'sessionID'} = $FORM{'sessionID'};
				}else{
					die 'Unknown Error('.__LINE__.')';
				}
				map {print "data: ".$_."\n"} split(/\n/,&cgi_lib::common::encodeJSON($DATAS));
				print "\n";
				&Time::HiRes::sleep(0.5);
			}
		}else{
			$DATAS->{'progress'} = &recalc_progress(\%FORM);
			if(exists $DATAS->{'progress'} && defined $DATAS->{'progress'}){
				$DATAS->{'success'} = JSON::XS::true;
				$DATAS->{'sessionID'} = $FORM{'sessionID'};
			}else{
				die 'Unknown Error('.__LINE__.')';
			}
		}
	};
	if($@){
		$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8($@);
		&cgi_lib::common::message($DATAS->{'msg'}) if(DEBUG);
		if($ENV{'HTTP_ACCEPT'} eq 'text/event-stream'){
			map {print "data: ".$_."\n"} split(/\n/,&cgi_lib::common::encodeJSON($DATAS));
			print "\n";
			exit;
		}
	}
}
elsif($FORM{'cmd'} eq 'recalc-cancel'){
	eval{
		&recalc_cancel(\%FORM);
		$DATAS->{'success'} = JSON::XS::true;
		$DATAS->{'sessionID'} = $FORM{'sessionID'};
	};
	if($@){
		$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8($@);
		&cgi_lib::common::message($DATAS->{'msg'}) if(DEBUG);
	}
}
elsif($FORM{'cmd'} eq 'cancel'){
	if(exists $COOKIE{'recalc.sessionID'} && defined $COOKIE{'recalc.sessionID'}){
		print "Set-Cookie: ",CGI::Cookie->new(-name=>'recalc.sessionID',-value=>'',-expires=>'-3M',-path=>$cookie_path),"\n";
		$DATAS->{'success'} = JSON::XS::true;
	}
}
else{
}

if(exists $ENV{'REQUEST_METHOD'}){
#	print qq|Content-type: text/html; charset=UTF-8\n\n|;
#	print &JSON::XS::encode_json($DATAS);
	&gzip_json($DATAS);
}
close(STDERR) if(DEBUG);

exit;

sub getParentTreeNode {
	my $sth = shift;
	my $hash = shift;
	my $enabled_cdi_ids = shift;
	my $cdi_id = shift;
	my $bul_id = shift;




	my $cdi_pids;
	my $cdi_pid;
	my $column_number = 0;
	$sth->execute($cdi_id,$bul_id) or die $dbh->errstr;
#print STDERR __LINE__,":",$sth->rows(),"\n";
	$column_number = 0;
	$sth->bind_col(++$column_number, \$cdi_pid,   undef);
	while($sth->fetch){
		next unless(defined $cdi_pid);
		next unless(exists $enabled_cdi_ids->{$cdi_pid}->{$bul_id});
		next if(exists $hash->{$cdi_pid} && exists $hash->{$cdi_pid}->{$bul_id});
		next if($cdi_id == $cdi_pid);
#print STDERR __LINE__,":[$cdi_id][$cdi_pid]\n";
		$hash->{$cdi_pid}->{$bul_id} = undef;
		$cdi_pids->{$cdi_pid} = undef;
	}
	$sth->finish;

	foreach my $cdi_pid (keys(%$cdi_pids)){
		&getParentTreeNode($sth,$hash,$enabled_cdi_ids,$cdi_pid,$bul_id);
	}
}

sub recalc {
	my $FORM = shift;
	my $sessionID;
	my $all_datas;
	$all_datas = &cgi_lib::common::decodeJSON($FORM->{'all_datas'});
	if(defined $all_datas){
		my $out_path = &catdir($FindBin::Bin,'temp');
		my $prog_basename = qq|batch-recalculation|;
		my $prog = &catfile($FindBin::Bin,'..','batch',qq|$prog_basename.pl|);
		if(-e $prog && -x $prog){
			$sessionID = &Digest::MD5::md5_hex(&Time::HiRes::time());
			$FORM->{'sessionID'} = $sessionID;
			$FORM->{'prefix'} = &catdir($out_path,$sessionID);

			my $params_file = &catfile($out_path,qq|$sessionID.json|);
			&cgi_lib::common::message('$params_file=['.$params_file.']') if(DEBUG);
			&cgi_lib::common::writeFileJSON($params_file,$FORM);
			chmod 0666,$params_file;

			my $temp_params_file = &catfile($out_path,qq|$sessionID.txt|);
			&cgi_lib::common::writeFileJSON($temp_params_file,$FORM,1);
			chmod 0666,$temp_params_file;

#			die("Can't execute program [$prog]");

			my $pid = fork;
			if(defined $pid){
				if($pid == 0){
					my $logdir = &getLogDir();
					my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
					my $f1 = &catfile($logdir,qq|$prog_basename.log|.sprintf(".%04d%02d%02d%02d%02d%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec));
					my $f2 = &catfile($logdir,qq|$prog_basename.err|.sprintf(".%04d%02d%02d%02d%02d%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec));
					close(STDOUT);
					close(STDERR);
					open STDOUT, "> $f1" || die "[$f1] $!\n";
					open STDERR, "> $f2" || die "[$f2] $!\n";
					close(STDIN);
					exec(qq|nice -n 19 $prog $params_file|);
					exit(1);
				}
			}else{
				die("Can't execute program [$prog $params_file]");
			}
		}
	}
	return $sessionID;
}

sub recalc_progress {
	my $FORM = shift;
	my $sessionID = $FORM->{'sessionID'};

	my $out_path = &catdir($FindBin::Bin,'temp');
	my $params_file = &catfile($out_path,qq|$sessionID.json|);

	my $progress;
	if(-e $params_file){
		while(1){
			$progress = &cgi_lib::common::readFileJSON($params_file);
			last if(defined $progress);
			&Time::HiRes::sleep(0.5);
		}
		delete $progress->{'prefix'}       if(exists $progress->{'prefix'});
		delete $progress->{'sessionID'}    if(exists $progress->{'sessionID'});
		delete $progress->{'cmd'}          if(exists $progress->{'cmd'});
		delete $progress->{'all_datas'}    if(exists $progress->{'all_datas'});
		delete $progress->{'recalc_datas'} if(exists $progress->{'recalc_datas'});


		unlink $params_file if(exists $progress->{'msg'} && defined $progress->{'msg'} && lc($progress->{'msg'}) eq 'end' && -e $params_file);
	}

	return $progress;
}

sub recalc_cancel {
	my $FORM = shift;
	my $sessionID = $FORM->{'sessionID'};

	my $out_path = &catdir($FindBin::Bin,'temp');
	my $params_file = &catfile($out_path,qq|$sessionID.json|);

	unlink $params_file or die $! if(-e $params_file);
}
