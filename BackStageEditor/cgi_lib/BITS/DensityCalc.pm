package BITS::DensityCalc;

#use strict;
#use warnings;
#use feature ':5.10';

use constant {
	DEBUG => 0,
	BLD_PREFIX_ID => 2,
	OPEN_ID => qq|system|
};

use File::Spec::Functions qw(abs2rel rel2abs catdir catfile splitdir tmpdir);
use Encode;
use DBD::Pg;
use JSON::XS;
use File::Temp;
use Cwd;
use Time::HiRes;
use Data::Dumper;
$Data::Dumper::Indent = 1;
$Data::Dumper::Sortkeys = 1;

use cgi_lib::common;
use BITS::ConceptArtMapModified;

use FindBin;
#use lib qq|$FindBin::Bin/../..|,qq|$FindBin::Bin/../../IM|;

#print __LINE__,":",$FindBin::Bin,"\n" if(DEBUG);

#require "common.pl";
#require "common_db.pl";
#my $dbh = &get_dbh();

use obj2deci;

sub _trim {
	my $str = shift;
	$str =~ s/^\s*//g;
	$str =~ s/\s*$//g;
	return $str;
}

sub get_rep_parent_id {
	my %arg = @_;
	my $dbh        = $arg{'dbh'};
	my $cdi_ids    = $arg{'cdi_ids'};
	my $route_ids  = $arg{'route_ids'};
	my $ci_id      = $arg{'ci_id'};
	my $cb_id      = $arg{'cb_id'};
	my $bul_id     = $arg{'bul_id'};
	my $md_id      = $arg{'md_id'};
	my $mv_id      = $arg{'mv_id'};
	my $mr_id      = $arg{'mr_id'};
	my $cdi_name   = $arg{'cdi_name'};
	my $cdi_id     = $arg{'cdi_id'};
	my $cdi_cid    = $arg{'cdi_cid'};
	my $use_ids    = $arg{'use_ids'};
	my $use_pids   = $arg{'use_pids'};
	my $LOG        = $arg{'LOG'};

	$use_pids = {} unless(defined $use_pids);

#	delete $arg{'dbh'};
#	&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%arg,1));

#	my $init_flag;
	unless(defined $cdi_ids){
		$cdi_ids = {};
#		$init_flag = 1;

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:get_rep_parent_id():$ci_id-$cb_id-$bul_id-$md_id-$mv_id-$mr_id.json\n| if(DEBUG);
	}

	$use_ids = &get_children_id(dbh=>$dbh, ci_id=>$ci_id,cb_id=>$cb_id,bul_id=>$bul_id,md_id=>$md_id,mv_id=>$mv_id,mr_id=>$mr_id,LOG=>$LOG) unless(defined $use_ids && ref $use_ids eq 'HASH');
	return undef unless(defined $use_ids && ref $use_ids eq 'HASH' && scalar keys(%$use_ids)>0);
#	&cgi_lib::common::message($use_ids,$LOG) if(defined $LOG);
#	&cgi_lib::common::message(scalar keys(%$use_ids),$LOG) if(defined $LOG);
#	die __LINE__;
=pod
=cut

	my %CDI_PIDS;
	my $cdi_pid;
	my $cdi_pname;


	unless(defined $cdi_name || defined $cdi_id){
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":get_rep_parent_id():\n" if(DEBUG);
		my $sql_route = '';
#		my $sql_rep = qq|select distinct rep.cdi_id,cdi_name from view_representation as rep where rep.ci_id=$ci_id and rep.cb_id=$cb_id and md_id=$md_id and mv_id=$mv_id and bul_id=$bul_id and rep_primitive and rep.cdi_id in ($sql_route) and rep.rep_delcause is null|;
		my $sql_rep;
		if(defined $md_id && defined $mv_id && defined $mr_id){
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\n" if(DEBUG);
			$sql_rep =<<SQL;
select distinct
 cm.cdi_id,
 cdi_name
from
 concept_art_map as cm
left join (
 select * from concept_data_info where cdi_delcause is null
) as cdi on cdi.ci_id=cm.ci_id and cdi.cdi_id=cm.cdi_id
where
 cm.cm_use and
 cm.cm_delcause is null and
 (cm.ci_id,cb_id,md_id,mv_id,mr_id,cm.cdi_id) in (
   select
    cm.ci_id,
    cm.cb_id,
    cm.md_id,
    cm.mv_id,
    max(cm.mr_id) as mr_id,
    cm.cdi_id
   from
    concept_art_map as cm
   where
    cm.ci_id=$ci_id and
    cm.cb_id=$cb_id and
    cm.md_id=$md_id and
    cm.mv_id=$mv_id and
    cm.mr_id<=$mr_id
--    and cm.cdi_id in ($sql_route)
   group by
    cm.ci_id,
    cm.cb_id,
    cm.md_id,
    cm.mv_id,
    cm.cdi_id
  )
SQL
		}elsif(defined $md_id && defined $mv_id){
		}else{
		}
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":get_rep_parent_id():\$sql_rep=[$sql_rep]\n" if(DEBUG);
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":get_rep_parent_id():\n" if(DEBUG);

		my $sth = $dbh->prepare($sql_rep) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":get_rep_parent_id():[",$sth->rows(),"]\n" if(DEBUG);
#exit;
		$sth->bind_col(1, \$cdi_pid, undef);
		$sth->bind_col(2, \$cdi_pname, undef);
		while($sth->fetch){
			next unless(defined $cdi_pid && defined $cdi_pname);
			next unless(exists $use_ids->{$cdi_pid});
			$CDI_PIDS{$cdi_pid} = $cdi_pname;
#			print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\$cdi_id=[$cdi_id]:\$cdi_name=[$cdi_name]\n" if(DEBUG);
		}
		$sth->finish;
		undef $sth;

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":get_rep_parent_id():\n" if(DEBUG);

#		print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\%CDI_PIDS=[".&Data::Dumper::Dumper(\%CDI_PIDS)."]\n" if(DEBUG);

	}else{

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\n" if(DEBUG);
#		print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\$cdi_id=[$cdi_id]:\$cdi_name=[$cdi_name]\n" if(DEBUG);

		if(defined $cdi_name && !defined $cdi_id){
			my $sth = $dbh->prepare(qq|select cdi_id from concept_data_info where ci_id=$ci_id and cdi_name=?|) or die $dbh->errstr;
			$sth->execute($cdi_name) or die $dbh->errstr;
			$sth->bind_col(1, \$cdi_id, undef);
			$sth->fetch;
			$sth->finish;
			undef $sth;
		}
		if(!defined $cdi_name && defined $cdi_id){
			my $sth = $dbh->prepare(qq|select cdi_name from concept_data_info where ci_id=$ci_id and cdi_id=?|) or die $dbh->errstr;
			$sth->execute($cdi_id) or die $dbh->errstr;
			$sth->bind_col(1, \$cdi_name, undef);
			$sth->fetch;
			$sth->finish;
			undef $sth;
		}

		my $cdi_name_e;
#		my $sth = $dbh->prepare(qq|select cdi_name_e from concept_data_info where ci_id=$ci_id and cdi_id=?|) or die $dbh->errstr;
		my $sth = $dbh->prepare(qq|select cd_name from concept_data where ci_id=$ci_id and cb_id=$cb_id and cdi_id=?|) or die $dbh->errstr;
		$sth->execute($cdi_id) or die $dbh->errstr;
		$sth->bind_col(1, \$cdi_name_e, undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;


		if(defined $cdi_id){
			undef $cdi_id unless(exists $use_ids->{$cdi_id});
		}

		if(defined $cdi_id){
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\n" if(DEBUG);
#			&cgi_lib::common::message("[$cdi_id][$cdi_name]") if(exists $cdi_ids->{$cdi_id});
			$cdi_ids->{$cdi_id} = {} unless(defined $cdi_ids->{$cdi_id});
			$cdi_ids->{$cdi_id}->{'cdi_name'} = $cdi_name;
			$cdi_ids->{$cdi_id}->{'name'} = lc($cdi_name_e);

			if(defined $cdi_cid){
				$cdi_ids->{$cdi_id}->{'cdi_cids'}->{$cdi_cid} = undef;
				if(exists $cdi_ids->{$cdi_cid} && exists $cdi_ids->{$cdi_cid}->{'cdi_cids'}){
					foreach my $cid (keys %{$cdi_ids->{$cdi_cid}->{'cdi_cids'}}){
						$cdi_ids->{$cdi_id}->{'cdi_cids'}->{$cid} = undef;
					}
				}
			}

			my $sql_but = qq|
select distinct
 cdi_pid,
 cdi.cdi_name,
 COALESCE(cd.cd_name,cdi.cdi_name_e)
from
 buildup_tree as but
left join (
 select
  ci_id,
  cdi_id,
  cdi_name,
  cdi_name_e
 from
  concept_data_info
) as cdi on (
 cdi.ci_id=but.ci_id and
 cdi.cdi_id=but.cdi_pid
)
left join (
 select
  ci_id,
  cb_id,
  cdi_id,
  cd_name
 from
  concept_data
) as cd on (
 cd.ci_id=but.ci_id and
 cd.cb_id=but.cb_id and
 cd.cdi_id=but.cdi_pid
)
where
 but.md_id=$md_id and
 but.mv_id=$mv_id and
 but.mr_id=$mr_id and
 but.ci_id=$ci_id and
 but.cb_id=$cb_id and
 but.cdi_id=$cdi_id and
 but.cdi_pid is not null and
 but.bul_id=$bul_id and
 but.but_delcause is null
|;

			my $cdi_pname_e;
			my $sth = $dbh->prepare($sql_but) or die $dbh->errstr;
			$sth->execute() or die $dbh->errstr;
			my $rows = $sth->rows();
			if($rows>0){
#			print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\$rows=[$rows]\n" if(DEBUG);
				$sth->bind_col(1, \$cdi_pid, undef);
				$sth->bind_col(2, \$cdi_pname, undef);
				$sth->bind_col(3, \$cdi_pname_e, undef);
				while($sth->fetch){
					next unless(defined $cdi_pid && defined $cdi_pname);
					next unless(exists $use_ids->{$cdi_pid});

					$CDI_PIDS{$cdi_pid} = $cdi_pname;

					$cdi_ids->{$cdi_id}->{'cdi_pid'}->{$cdi_pid} = $cdi_pname;
					$cdi_ids->{$cdi_id}->{'cdi_pname'}->{$cdi_pname} = lc($cdi_pname_e);
				}
			}
			$sth->finish;
			undef $sth;
		}
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\$cdi_ids=[",(scalar keys(%$cdi_ids)),"]\n" if(DEBUG);
	}
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\n" if(DEBUG);
	foreach $cdi_pid (keys %CDI_PIDS){
#		print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\$cdi_pid=[$cdi_pid]\n" if(DEBUG);
		if(exists $use_pids->{$cdi_pid}){
#			&cgi_lib::common::message("[$bul_id][$cdi_pid][$CDI_PIDS{$cdi_pid}]",$LOG) if(defined $LOG);
			next;
		}else{
			$use_pids->{$cdi_pid} = undef;
		}
		&get_rep_parent_id(dbh=>$dbh, cdi_ids=>$cdi_ids,route_ids=>$route_ids,cdi_cid=>$cdi_id,cdi_id=>$cdi_pid,cdi_name=>$CDI_PIDS{$cdi_pid},ci_id=>$ci_id,cb_id=>$cb_id,bul_id=>$bul_id,md_id=>$md_id,mv_id=>$mv_id,mr_id=>$mr_id, use_ids=>$use_ids, use_pids=>$use_pids,LOG=>$LOG);
	}

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\n" if(DEBUG);
	return wantarray ? ($cdi_ids,$route_ids,$use_ids) : $cdi_ids;

}

sub get_children_id {
	my %arg = @_;
	my $dbh       = $arg{'dbh'};
	my $cdi_pname = $arg{'cdi_name'};
	my $cdi_pid   = $arg{'cdi_id'};
	my $ci_id     = $arg{'ci_id'};
	my $cb_id     = $arg{'cb_id'};
	my $bul_id    = $arg{'bul_id'};
	my $depth     = $arg{'depth'};

	my $md_id     = $arg{'md_id'};
	my $mv_id     = $arg{'mv_id'};
	my $mr_id     = $arg{'mr_id'};

	my $LOG       = $arg{'LOG'};

#	my @IDS;

	my $hash = {};
	my $cdi_id;
	my $but_cids;

	my $sql = qq|
select cdi_id,but_pids from buildup_tree_info where bul_id=$bul_id and (md_id,mv_id,mr_id,ci_id,cb_id,cdi_id) in (
 select md_id,mv_id,mr_id,ci_id,cb_id,cdi_id from concept_art_map where cm_use and cm_delcause is null and (md_id,mv_id,mr_id,cdi_id) in (
  select md_id,mv_id,max(mr_id) as mr_id,cdi_id from concept_art_map where md_id=$md_id and mv_id=$mv_id and mr_id<=$mr_id group by md_id,mv_id,mr_id,cdi_id
 )
);
|;

	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$sth->bind_col(1, \$cdi_id, undef);
	$sth->bind_col(2, \$but_cids, undef);
	while($sth->fetch){
		next unless(defined $cdi_id);
#			push(@IDS,$cdi_id);

		$hash->{$cdi_id} = undef;
		my $cids = &JSON::XS::decode_json($but_cids) if(defined $but_cids && length $but_cids);
		if(defined $cids && ref $cids eq 'ARRAY'){
			$hash->{$_} = undef for(@$cids);
		}
	}
	$sth->finish;
	undef $sth;


	return $hash;
}

sub ins_representation {
	my %arg = @_;
	my $dbh        = $arg{'dbh'};
	my $cdi_ids    = $arg{'cdi_ids'};
	my $art_ids    = $arg{'art_ids'};
	my $ci_id      = $arg{'ci_id'};
	my $cb_id      = $arg{'cb_id'};
	my $bul_id     = $arg{'bul_id'};
	my $md_id      = $arg{'md_id'};
	my $mv_id      = $arg{'mv_id'};
	my $mr_id      = $arg{'mr_id'};
	my $cdi_id     = $arg{'cdi_id'};
	my $rep_delcause = $arg{'rep_delcause'};
	my $LOG        = $arg{'LOG'};

	unless(
		defined $ci_id &&
		defined $cb_id &&
		defined $bul_id &&
		defined $md_id &&
		defined $mv_id &&
		defined $mr_id &&
		defined $cdi_id
	){
#		print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:ins_representation():\$ci_id=[$ci_id]:\$cb_id=[$cb_id]:\$bul_id=[$bul_id]:\$md_id=[$md_id]:\$mv_id=[$mv_id]:\$mr_id=[$mr_id]:\$cdi_id=[$cdi_id]\n| if(DEBUG);
		return;
	}

	my $sql=<<SQL;
select
 rep_id,
 cdi_name
from
 view_representation
where
 ci_id=$ci_id and
-- cb_id=$cb_id and
 bul_id=$bul_id and
 md_id=$md_id and
 mv_id=$mv_id and
 mr_id=$mr_id and
 cdi_id=$cdi_id
SQL
	my $rep_id;
	my $cdi_name;
	my $sth_sel = $dbh->prepare($sql) or die $dbh->errstr;
	$sth_sel->execute() or die $dbh->errstr;
	my $rows = $sth_sel->rows();
	$sth_sel->bind_col(1, \$rep_id, undef);
	$sth_sel->bind_col(2, \$cdi_name, undef);
	$sth_sel->fetch;
	$sth_sel->finish;
	undef $sth_sel;
#	print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":ins_representation():\$rows=[$rows][$rep_id][$cdi_name][",(scalar keys(%$art_ids)),"]\n" if(DEBUG);
	if($rows>0){
#		&clear_representation_density(dbh=>$dbh, cdi_ids=>$cdi_ids, ci_id=>$ci_id, cb_id=>$cb_id, bul_id=>$bul_id, md_id=>$md_id, mv_id=>$mv_id, mr_id=>$mr_id, cdi_id=>$cdi_id );
		return 0;
	}

	my $prefix_char;
	my $sth = $dbh->prepare(qq|select prefix_char from id_prefix where prefix_id=?|) or die $dbh->errstr;
	$sth->execute(BLD_PREFIX_ID) or die $dbh->errstr;
	$sth->bind_col(1, \$prefix_char, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;
	$prefix_char = &_trim($prefix_char);

	my $rep_serial;
	my $sth = $dbh->prepare(qq|select COALESCE(max(rep_serial),0) from representation where prefix_id=?|) or die $dbh->errstr;
	$sth->execute(BLD_PREFIX_ID) or die $dbh->errstr;
	$sth->bind_col(1, \$rep_serial, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;
	$rep_serial++;
	my $rep_id = sprintf("%s",qq|$prefix_char$rep_serial|);
#	print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":ins_representation():\$rep_id=[$rep_id]\n" if(DEBUG);

	my $sql=<<SQL;
insert into representation (ci_id,cb_id,bul_id,md_id,mv_id,mr_id,cdi_id,rep_id,rep_serial,rep_delcause,rep_openid) values ($ci_id,$cb_id,$bul_id,$md_id,$mv_id,$mr_id,$cdi_id,?,?,?,?)
SQL
	my $sth_ins = $dbh->prepare($sql) or die $dbh->errstr;
	$sth_ins->execute($rep_id,$rep_serial,$rep_delcause,OPEN_ID) or die $dbh->errstr;
	$sth_ins->finish;
	undef $sth_ins;

	if(defined $art_ids){
		my $sql=<<SQL;
insert into representation_art (rep_id,art_id,art_hist_serial) values (?,?,?)
SQL
		my $sth_ins = $dbh->prepare($sql) or die $dbh->errstr;
		foreach my $key (keys(%$art_ids)){
			my($art_id,$art_hist_serial) = split(/\t/,$key);
			$sth_ins->execute($rep_id,$art_id,$art_hist_serial) or die $dbh->errstr;
			$sth_ins->finish;
		}
		undef $sth_ins;
	}

	if(defined $cdi_ids && exists $cdi_ids->{$cdi_id}->{'cdi_pid'} && defined $cdi_ids->{$cdi_id}->{'cdi_pid'} && ref $cdi_ids->{$cdi_id}->{'cdi_pid'} eq 'HASH'){
		foreach my $cdi_pid (keys(%{$cdi_ids->{$cdi_id}->{'cdi_pid'}})){
			&ins_representation(dbh=>$dbh, cdi_ids=>$cdi_ids, art_ids=>$art_ids, ci_id=>$ci_id, cb_id=>$cb_id, bul_id=>$bul_id, md_id=>$md_id, mv_id=>$mv_id, mr_id=>$mr_id, cdi_id=>$cdi_pid );
		}
	}
	return $rep_id;
}

sub clear_representation_density {
	my %arg = @_;
	my $dbh        = $arg{'dbh'};
	my $cdi_ids    = $arg{'cdi_ids'};
	my $ci_id      = $arg{'ci_id'};
	my $cb_id      = $arg{'cb_id'};
	my $bul_id     = $arg{'bul_id'};
	my $md_id      = $arg{'md_id'};
	my $mv_id      = $arg{'mv_id'};
	my $mr_id      = $arg{'mr_id'};
	my $cdi_id     = $arg{'cdi_id'};
	my $rep_delcause = $arg{'rep_delcause'};
	my $forcing    = $arg{'forcing'};
	my $LOG        = $arg{'LOG'};

	unless(
		defined $ci_id &&
		defined $cb_id &&
		defined $bul_id &&
		defined $md_id &&
		defined $mv_id &&
		defined $mr_id &&
		defined $cdi_id
	){
#		print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:clear_representation_density():\$ci_id=[$ci_id]:\$cb_id=[$cb_id]:\$bul_id=[$bul_id]:\$md_id=[$md_id]:\$mv_id=[$mv_id]:\$mr_id=[$mr_id]:\$cdi_id=[$cdi_id]\n| if(DEBUG);
		return;
	}

	my $sql=<<SQL;
select
 rep_id
from
 representation
where
 ci_id=$ci_id and
-- cb_id=$cb_id and
 bul_id=$bul_id and
 md_id=$md_id and
 mv_id=$mv_id and
 mr_id=$mr_id and
 cdi_id=$cdi_id
SQL
#	print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":clear_representation_density():\$sql=[$sql]\n" if(DEBUG);
	my $sth_sel = $dbh->prepare($sql) or die $dbh->errstr;
	$sth_sel->execute() or die $dbh->errstr;
	my $rep_id;
	$sth_sel->bind_col(1, \$rep_id, undef);
	$sth_sel->fetch;
	$sth_sel->finish;
	undef $sth_sel;
	return unless(defined $rep_id);

	my $sql=<<SQL;
update representation set
 rep_child_objs=null,
 rep_density_objs=null,
 rep_density_ends=null,
 rep_density_end_ids=null,
 rep_delcause=?
where
 rep_id=?
SQL
	unless(defined $forcing){
		if(defined $rep_delcause){
#			$sql .= qq| and rep_delcause is null|;
		}else{
			$sql .= qq| and rep_delcause is not null|;
		}
	}else{
		$sql .= qq| and (rep_child_objs is not null or rep_delcause is not null)|;
	}
	&cgi_lib::common::message("clear_representation_density():\$sql=[$sql]", $LOG) if(defined $LOG);
	&cgi_lib::common::message("clear_representation_density():\$rep_delcause=[$rep_delcause]", $LOG) if(defined $LOG);
	&cgi_lib::common::message("clear_representation_density():\$rep_id=[$rep_id]", $LOG) if(defined $LOG);
	my $sth_upd = $dbh->prepare($sql) or die $dbh->errstr;
	$sth_upd->execute($rep_delcause,$rep_id) or die $dbh->errstr;
	my $rows = $sth_upd->rows();
	$sth_upd->finish;
	undef $sth_upd;
	&cgi_lib::common::message("clear_representation_density():\$rows=[$rows]", $LOG) if(defined $LOG);
	return 0 if($rows<1);

	if(defined $cdi_ids && ref $cdi_ids eq 'HASH' && exists $cdi_ids->{$cdi_id}->{'cdi_pid'} && defined $cdi_ids->{$cdi_id}->{'cdi_pid'} && ref $cdi_ids->{$cdi_id}->{'cdi_pid'} eq 'HASH'){
		foreach my $cdi_pid (keys(%{$cdi_ids->{$cdi_id}->{'cdi_pid'}})){
			$rows += &clear_representation_density(dbh=>$dbh, cdi_ids=>$cdi_ids, ci_id=>$ci_id, cb_id=>$cb_id, bul_id=>$bul_id, md_id=>$md_id, mv_id=>$mv_id, mr_id=>$mr_id, cdi_id=>$cdi_pid, forcing=>$forcing );
		}
	}
	return $rows;
}

sub update_representation_density {
	my %arg = @_;
	my $dbh        = $arg{'dbh'};
	my $cdi_ids    = $arg{'cdi_ids'};
	my $ci_id      = $arg{'ci_id'};
	my $cb_id      = $arg{'cb_id'};
	my $bul_id     = $arg{'bul_id'};
	my $md_id      = $arg{'md_id'};
	my $mv_id      = $arg{'mv_id'};
	my $mr_id      = $arg{'mr_id'};
	my $cdi_id     = $arg{'cdi_id'};
	my $cdi_name   = $arg{'cdi_name'};
	my $rep_id     = $arg{'rep_id'};
	my $calcVolume = $arg{'calcVolume'};
	my $callback   = $arg{'callback'};
	my $LOG        = $arg{'LOG'};

	unless(
		defined $ci_id &&
		defined $cb_id &&
		defined $bul_id &&
		defined $md_id &&
		defined $mv_id &&
		defined $mr_id &&
		defined $cdi_id
	){
#		print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$ci_id=[$ci_id]:\$cb_id=[$cb_id]:\$bul_id=[$bul_id]:\$md_id=[$md_id]:\$mv_id=[$mv_id]:\$mr_id=[$mr_id]:\$cdi_id=[$cdi_id]:\$cdi_name=[$cdi_name]\n| if(DEBUG);
		return;
	}

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$ci_id=[$ci_id]:\$cb_id=[$cb_id]:\$bul_id=[$bul_id]:\$md_id=[$md_id]:\$mv_id=[$mv_id]:\$mr_id=[$mr_id]:\$cdi_id=[$cdi_id]:\$cdi_name=[$cdi_name]\n| if(DEBUG);
#my $t0 = [&Time::HiRes::gettimeofday()] if(DEBUG);

	$calcVolume = 1 unless(defined $calcVolume);

#	my $cdi_name;
	unless(defined $rep_id && defined $cdi_name){
		my $sql=<<SQL;
select
 rep_id,
 cdi_name
from
 view_representation
where
 ci_id=$ci_id and
-- cb_id=$cb_id and
 bul_id=$bul_id and
 md_id=$md_id and
 mv_id=$mv_id and
 mr_id=$mr_id and
 cdi_id=$cdi_id
SQL
		my $sth_sel = $dbh->prepare($sql) or die $dbh->errstr;
		$sth_sel->execute() or die $dbh->errstr;
		my $rep_id;
		$sth_sel->bind_col(1, \$rep_id, undef);
		$sth_sel->bind_col(2, \$cdi_name, undef);
		$sth_sel->fetch;
		$sth_sel->finish;
		undef $sth_sel;
	}
	return unless(defined $rep_id);

#	print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$rep_id=[$rep_id]:\$cdi_name=[$cdi_name]\n| if(DEBUG);
#	print "\t".__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$rep_id=[$rep_id]:\$cdi_name=[$cdi_name]\n|;

	my($ELEMENT, $COMP_DENSITY_USE_TERMS, $COMP_DENSITY_END_TERMS, $COMP_DENSITY_USE_TERM_IDS, $COMP_DENSITY_END_TERM_IDS, $COMP_DENSITY_ALL_END_TERMS, $COMP_DENSITY_ALL_END_TERM_IDS) = &BITS::ConceptArtMapModified::calcElementAndDensity(
		dbh => $dbh,
		ci_id => $ci_id,
		cb_id => $cb_id,
		md_id => $md_id,
		mv_id => $mv_id,
		mr_id => $mr_id,
		crl_id => $bul_id,
		cdi_ids => [$cdi_id],
		LOG => $LOG
	);
	my $rep_primitive=0;
	$rep_primitive = exists $ELEMENT->{$cdi_id} ? 1: 0;
	if(defined $LOG){
#		&cgi_lib::common::message($COMP_DENSITY_USE_TERMS->{$cdi_id},$LOG);
#		&cgi_lib::common::message($COMP_DENSITY_USE_TERM_IDS->{$cdi_id},$LOG);
#		&cgi_lib::common::message($COMP_DENSITY_END_TERMS->{$cdi_id},$LOG);
#		&cgi_lib::common::message($COMP_DENSITY_END_TERM_IDS->{$cdi_id},$LOG);
#		&cgi_lib::common::message($COMP_DENSITY_ALL_END_TERMS->{$cdi_id},$LOG);
#		&cgi_lib::common::message($COMP_DENSITY_ALL_END_TERM_IDS->{$cdi_id},$LOG);
#		&cgi_lib::common::message($rep_primitive,$LOG);
	}


	my %ART_IDS;
#	my $art_id;
#	my $art_hist_serial;




	#rep_primitive更新
	my $sql_representation_update_primitive=<<SQL;
UPDATE representation SET
 rep_primitive=?,
 rep_entry=now()
WHERE
 rep_id=?
RETURNING
 rep_entry
SQL
	my $sth_representation_update_primitive = $dbh->prepare($sql_representation_update_primitive);
	$sth_representation_update_primitive->execute($rep_primitive,$rep_id) or die $dbh->errstr;
	if(DEBUG){
		my $rep_entry;
		$sth_representation_update_primitive->bind_col(1, \$rep_entry, undef);
		$sth_representation_update_primitive->fetch;
		&cgi_lib::common::message($rep_entry,$LOG) if(defined $LOG);
	}
	$sth_representation_update_primitive->finish;
	undef $sth_representation_update_primitive;



	my $rep_child_objs;
	my $rep_density_objs = 0;

	$callback->(qq|Calculation density|) if(defined $callback);

	{
		%ART_IDS = ();
		my $hash;
		$hash->{$cdi_id} = undef;
		my $but_cids;
		my $sql = qq|select but_cids from buildup_tree_info where md_id=$md_id and mv_id=$mv_id and mr_id=$mr_id and ci_id=$ci_id and cb_id=$cb_id and bul_id=$bul_id and cdi_id=$cdi_id|;
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":get_children_id():\$sql=[$sql]\n" if(DEBUG);
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$sth->bind_col(1, \$but_cids, undef);
		while($sth->fetch){
			next unless(defined $but_cids);
			my $cids = &JSON::XS::decode_json($but_cids);
			next unless(defined $cids && ref $cids eq 'ARRAY');
			$hash->{$_} = undef for(@$cids);
		}
		$sth->finish;
		undef $sth;
#		&cgi_lib::common::message($hash, $LOG) if(defined $LOG);

		my $art_id;
		my $art_hist_serial;
		$sql = sprintf(qq|select art_id,art_hist_serial from concept_art_map where (md_id,mv_id,mr_id,cdi_id) in (select md_id,mv_id,max(mr_id) as mr_id,cdi_id from concept_art_map where md_id=$md_id and mv_id=$mv_id and mr_id<=$mr_id and cdi_id in (%s) group by md_id,mv_id,cdi_id)|,join(',',keys(%$hash)));
#		&cgi_lib::common::message($sql, $LOG) if(defined $LOG);
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
#		&cgi_lib::common::message($sth->rows(), $LOG) if(defined $LOG);
		$sth->bind_col(1, \$art_id, undef);
		$sth->bind_col(2, \$art_hist_serial, undef);
		while($sth->fetch){
			$ART_IDS{qq|$art_id\t$art_hist_serial|} = undef;
		}
		$sth->finish;
		undef $sth;

		$rep_child_objs = scalar keys(%ART_IDS);
		&cgi_lib::common::message(qq|[$cdi_name]=[$rep_child_objs]|, $LOG) if(defined $LOG);
	}



	my $rep_density_ends;
	my $rep_density_end_ids;
	my $rep_density_all_ends;
	my $rep_density_all_end_ids;
	$rep_density_objs = $COMP_DENSITY_USE_TERMS->{$cdi_id};
	$rep_density_ends = $COMP_DENSITY_END_TERMS->{$cdi_id};
	$rep_density_end_ids = undef;
	$rep_density_end_ids = &cgi_lib::common::encodeJSON([map {$_-=0} keys(%{$COMP_DENSITY_END_TERM_IDS->{$cdi_id}})]) if($rep_density_ends>0);

	$rep_density_all_ends = $COMP_DENSITY_ALL_END_TERMS->{$cdi_id};
	$rep_density_all_end_ids = undef;
	$rep_density_all_end_ids = &cgi_lib::common::encodeJSON([map {$_-=0} keys(%{$COMP_DENSITY_ALL_END_TERM_IDS->{$cdi_id}})]) if($rep_density_all_ends>0);

	&cgi_lib::common::message(qq|\$rep_density_ends=[$rep_density_ends]|, $LOG) if(defined $LOG);
	&cgi_lib::common::message(qq|\$rep_density_all_ends=[$rep_density_all_ends]|, $LOG) if(defined $LOG);


	my $sql_modified_count = qq|
select
 rep_entry,
 cm_modified,
 cdi_name
from
 view_representation as rep
left join (
 select * from concept_art_map_modified
) as cmm on
 rep.ci_id=cmm.ci_id AND
 rep.bul_id=cmm.bul_id AND
 rep.cdi_id=cmm.cdi_id AND
 rep.md_id=cmm.md_id AND
 rep.mv_id=cmm.mv_id AND
 rep.mr_id=cmm.mr_id 
where
 rep_delcause is null and
 (rep.ci_id,rep.bul_id,rep.cdi_id) in (select ci_id,bul_id,cdi_id from buildup_tree where md_id=$md_id and mv_id=$mv_id and mr_id=$mr_id and ci_id=$ci_id and cb_id=$cb_id and bul_id=$bul_id and cdi_pid=$cdi_id) and rep.md_id=$md_id and rep.mv_id=$mv_id and rep.mr_id=$mr_id
 and rep_entry<cm_modified
|;
#	print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$sql_modified_count=[$sql_modified_count]\n| if(DEBUG);
	my $sth = $dbh->prepare($sql_modified_count) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	my $modified_count = $sth->rows();
#	print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$modified_count=[$modified_count]\n| if(DEBUG);
	if(DEBUG){
		my $rep_entry;
		my $cm_modified;
		my $cdi_name;
		$sth->bind_col(1, \$rep_entry, undef);
		$sth->bind_col(2, \$cm_modified, undef);
		$sth->bind_col(3, \$cdi_name, undef);
		while($sth->fetch){
			&cgi_lib::common::message(qq|\$cdi_name=[$cdi_name]|,$LOG) if(defined $LOG);
			&cgi_lib::common::message(qq|\$rep_entry=[$rep_entry]:\$cm_modified=[$cm_modified]|,$LOG) if(defined $LOG);
		}
	}
	$sth->finish;
	undef $sth;

	my $update_rep_entry;
	$update_rep_entry = 0;


	my $sql_cm_entry;
	my $sth_cm_entry;

	$sql_cm_entry = qq|
SELECT
 EXTRACT(EPOCH FROM cm_modified)
FROM
 concept_art_map_modified
where
 ci_id=$ci_id AND
-- cb_id=$cb_id AND
 md_id=$md_id AND
 mv_id=$mv_id AND
 mr_id=$mr_id AND
 bul_id=$bul_id AND
 cdi_id=$cdi_id
|;
	$sth_cm_entry = $dbh->prepare($sql_cm_entry) or die $dbh->errstr;
	$sth_cm_entry->execute() or die $dbh->errstr;
	$sth_cm_entry->bind_col(1, \$update_cm_entry, undef);
	$sth_cm_entry->fetch;
	$sth_cm_entry->finish;
	undef $sth_cm_entry;
	if(defined $update_cm_entry){
		&cgi_lib::common::message($update_cm_entry,$LOG) if(defined $LOG);
		$update_rep_entry = $update_cm_entry if($update_rep_entry<$update_cm_entry);
	}
	&cgi_lib::common::message($update_rep_entry,$LOG) if(defined $LOG);



	&cgi_lib::common::message(qq|[$cdi_name]=[$rep_child_objs]|, $LOG) if(defined $LOG);

	if($rep_child_objs>0){
		my $sql_representation_update_density=<<SQL;
UPDATE representation SET
 rep_child_objs=?,
 rep_density_objs=?,
 rep_density_ends=?,
 rep_density_end_ids=?,
 rep_density_all_ends=?,
 rep_density_all_end_ids=?,
 rep_delcause=null,
 rep_entry=(TIMESTAMP WITH TIME ZONE 'epoch' + ? * INTERVAL '1 second')
WHERE
 rep_id=?
RETURNING
 rep_entry
SQL
#		print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$sql_representation_update_density=[$sql_representation_update_density]\n| if(DEBUG);
		my $sth_representation_update_density = $dbh->prepare($sql_representation_update_density);
		$sth_representation_update_density->execute($rep_child_objs,$rep_density_objs,$rep_density_ends,$rep_density_end_ids,$rep_density_all_ends,$rep_density_all_end_ids,$update_rep_entry,$rep_id) or die $dbh->errstr;
		&cgi_lib::common::message("[$rep_id]:".$sth_representation_update_density->rows(),$LOG) if(defined $LOG);
		if(DEBUG){
			my $rep_entry;
			$sth_representation_update_density->bind_col(1, \$rep_entry, undef);
			$sth_representation_update_density->fetch;
			&cgi_lib::common::message($rep_entry,$LOG) if(defined $LOG);
		}
		$sth_representation_update_density->finish;
		undef $sth_representation_update_density;

		if(defined $LOG){
			my $sql_sel=<<SQL;
select * from representation where rep_id=? and rep_delcause is null
SQL
#		print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$sql=[$sql][$rep_id]\n| if(DEBUG);
			my $sth_sel = $dbh->prepare($sql_sel) or die $dbh->errstr;
			$sth_sel->execute($rep_id) or die $dbh->errstr;
			&cgi_lib::common::message($sth_sel->rows(),$LOG);
			$sth_sel->finish;
			undef $sth_sel;
		}

		my $sql_del=<<SQL;
delete from representation_art where rep_id=?
SQL
#		print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$sql=[$sql][$rep_id]\n| if(DEBUG);
		my $sth_del = $dbh->prepare($sql_del) or die $dbh->errstr;
		$sth_del->execute($rep_id) or die $dbh->errstr;
		&cgi_lib::common::message($sth_del->rows(),$LOG) if(defined $LOG);
		$sth_del->finish;
		undef $sth_del;

	}else{
		my $sql_representation_update_density=<<SQL;
update representation set
 rep_delcause='DELETE',
 rep_entry=(TIMESTAMP WITH TIME ZONE 'epoch' + ? * INTERVAL '1 second')
where
 rep_id=?
SQL
#		print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$sql_representation_update_density=[$sql_representation_update_density]\n| if(DEBUG);
		my $sth_representation_update_density = $dbh->prepare($sql_representation_update_density);
		$sth_representation_update_density->execute($update_rep_entry,$rep_id) or die $dbh->errstr;
		&cgi_lib::common::message($sth_representation_update_density->rows(),$LOG) if(defined $LOG);
		$sth_representation_update_density->finish;
		undef $sth_representation_update_density;
	}

	my $sql=<<SQL;
insert into representation_art (rep_id,art_id,art_hist_serial) values (?,?,?)
SQL
	my $sth_ins = $dbh->prepare($sql) or die $dbh->errstr;
#	print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$sql=[$sql]\n| if(DEBUG);

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Time::HiRes::tv_interval($t0)." s\n" if(DEBUG);
#$t0 = [&Time::HiRes::gettimeofday()] if(DEBUG);

	my @bounds;
	my $bu_volume;
	my $bu_cube_volume;

#	my $tempdir = &File::Temp::tempdir( CLEANUP=>1 );
	my $tempdir = &catdir($FindBin::Bin,'..','htdocs','art_file');


	my @FILES;
	my $sth = $dbh->prepare(qq|select art_name,art_ext from history_art_file where art_id=? and hist_serial=?|) or die $dbh->errstr;
	my $sth_data = $dbh->prepare(qq|select art_data from history_art_file where art_id=? and hist_serial=?|) or die $dbh->errstr;

	foreach my $art_key (keys(%ART_IDS)){
		my($art_id,$art_hist_serial) = split(/\t/,$art_key);
		&cgi_lib::common::message(qq|$art_id,$art_hist_serial|,$LOG) if(defined $LOG);

#		print STDERR sprintf("\t%s:%4d:%s:%s:%d\n",__PACKAGE__,__LINE__,$rep_id,$art_id,$art_hist_serial);
		$sth_ins->execute($rep_id,$art_id,$art_hist_serial) or die $dbh->errstr;
		$sth_ins->finish;
#		print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():[$rep_id][$art_id][$art_hist_serial]\n| if(DEBUG);

		my $art_name;
		my $art_ext;
		$sth->execute($art_id,$art_hist_serial) or die $dbh->errstr;
		$sth->bind_col(1, \$art_name);
		$sth->bind_col(2, \$art_ext);
		$sth->fetch;
		$sth->finish;

		my $file = &catfile($tempdir,qq|$art_id$art_ext|);

		unless(-e $file){
			my $art_data;
			$sth_data->execute($art_id,$art_hist_serial) or die $dbh->errstr;
			$sth_data->bind_col(1, \$art_data, { pg_type=>DBD::Pg::PG_BYTEA });
			$sth_data->fetch;
			$sth_data->finish;

			my $fh;
			open($fh,"> $file") or die $dbh->errstr;
			flock($fh,2);
			binmode($fh);
			print $fh $art_data;
			close($fh);
		}
		push(@FILES,$file);
		&cgi_lib::common::message($file,$LOG) if(defined $LOG);
	}
	undef $sth;
	undef $sth_data;
	undef $sth_ins;

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Time::HiRes::tv_interval($t0)." s\n" if(DEBUG);
#$t0 = [&Time::HiRes::gettimeofday()] if(DEBUG);

	unless($calcVolume){
		$callback->(qq|Calculation volume (SQL)|) if(defined $callback);
		&cgi_lib::common::message(qq|Calculation volume (SQL)|,$LOG) if(defined $LOG);
		my $sql_upd=<<SQL;
update
 representation
set
 rep_xmin=art_xmin,
 rep_xmax=art_xmax,
 rep_ymin=art_ymin,
 rep_ymax=art_ymax,
 rep_zmin=art_zmin,
 rep_zmax=art_zmax,
 rep_cube_volume=round(((art_xmax-art_xmin)*(art_ymax-art_ymin)*(art_zmax-art_zmin))/1000,4)
from (
 select
  min(art_xmin) as art_xmin,
  max(art_xmax) as art_xmax,
  min(art_ymin) as art_ymin,
  max(art_ymax) as art_ymax,
  min(art_zmin) as art_zmin,
  max(art_zmax) as art_zmax
 from
  history_art_file
 where
  (art_id,hist_serial) in (select art_id,art_hist_serial from representation_art where rep_id=?)
) as a
where rep_id=?
SQL
		my $sth_upd = $dbh->prepare($sql_upd) or die $dbh->errstr;
		$sth_upd->execute($rep_id,$rep_id) or die $dbh->errstr;
		$sth_upd->finish;
		undef $sth_upd;
		undef $sql_upd;

	}else{
		$callback->(qq|Calculation volume (VTK)|) if(defined $callback);
		&cgi_lib::common::message(qq|Calculation volume (VTK)|,$LOG) if(defined $LOG);
		&cgi_lib::common::message(scalar @FILES,$LOG) if(defined $LOG);

		if(scalar @FILES > 0){
			my $prop = &obj2deci::getProperties(\@FILES);
#			&obj2deci::objDeleteAll();	#高速化の為、コメントアウト
			if(defined $prop && ref $prop eq 'HASH' && exists $prop->{'bounds'} && defined $prop->{'bounds'} && ref $prop->{'bounds'} eq 'ARRAY' && scalar @{$prop->{'bounds'}} >= 6 && exists $prop->{'volume'} && defined $prop->{'volume'}){
				@bounds = map {$_+=0;} @{$prop->{'bounds'}};
				$bu_volume = &Truncated($prop->{'volume'} / 1000);
				$bu_cube_volume = &Truncated((($bounds[1]-$bounds[0])*($bounds[3]-$bounds[2])*($bounds[5]-$bounds[4]))/1000);
			}else{
				@bounds = (0,0,0,0,0,0);
				$bu_volume = 0;
				$bu_cube_volume = 0;
			}
			&cgi_lib::common::message($prop,$LOG) if(defined $LOG);
			if($bounds[0]==1 && $bounds[1]==-1 && $bounds[2]==1 && $bounds[3]==-1 && $bounds[4]==1 && $bounds[5]==-1){
				&cgi_lib::common::message(\@FILES,$LOG) if(defined $LOG);
				die __LINE__;
			}


			my $sql = qq|update representation set rep_xmin=?,rep_xmax=?,rep_ymin=?,rep_ymax=?,rep_zmin=?,rep_zmax=?,rep_volume=?,rep_cube_volume=? where rep_id=?|;
			my $sth = $dbh->prepare($sql) or die $dbh->errstr;
			my $param_num = 0;
			$sth->bind_param(++$param_num, $bounds[0]);
			$sth->bind_param(++$param_num, $bounds[1]);
			$sth->bind_param(++$param_num, $bounds[2]);
			$sth->bind_param(++$param_num, $bounds[3]);
			$sth->bind_param(++$param_num, $bounds[4]);
			$sth->bind_param(++$param_num, $bounds[5]);
			$sth->bind_param(++$param_num, $bu_volume);
			$sth->bind_param(++$param_num, $bu_cube_volume);
			$sth->bind_param(++$param_num, $rep_id);
			$sth->execute() or die $dbh->errstr;
			my $rows = $sth->rows();
			$sth->finish();
			undef $sth;
			&cgi_lib::common::message($rows,$LOG) if(defined $LOG);
		}

	}

	$callback->(qq|Configuration calculation|) if(defined $callback);
	&cgi_lib::common::message(qq|Configuration calculation|,$LOG) if(defined $LOG);

	my $sth_upd = $dbh->prepare(qq|update representation set mca_id=get_mca_id(rep_id) where rep_id=?|) or die $dbh->errstr;
	$sth_upd->execute($rep_id) or die $dbh->errstr;
	$sth_upd->finish;
	undef $sth_upd;

	if($update_rep_entry==0){
		my $sql_representation_update_entry=qq|update representation set rep_entry=now() where rep_id=?|;
		my $sth_representation_update_entry = $dbh->prepare($sql_representation_update_entry);
		$sth_representation_update_entry->execute($rep_id) or die $dbh->errstr;
		$sth_representation_update_entry->finish;
		undef $sth_representation_update_entry;
	}else{
#		my $sql_representation_update_entry=qq|update representation set rep_entry=(TIMESTAMP WITH TIME ZONE 'epoch' + ? * INTERVAL '1 second') where rep_id=?|;
		my $sql_representation_update_entry=qq|update representation set rep_entry=(TIMESTAMP WITH TIME ZONE 'epoch' + ?) where rep_id=?|;
		my $sth_representation_update_entry = $dbh->prepare($sql_representation_update_entry);
		$sth_representation_update_entry->execute($update_rep_entry,$rep_id) or die $dbh->errstr;
		$sth_representation_update_entry->finish;
		undef $sth_representation_update_entry;
	}

	my $sql_representation_update_concept=qq|update representation set ci_id=?,cb_id=? where rep_id=?|;
	my $sth_representation_update_concept = $dbh->prepare($sql_representation_update_concept);
	$sth_representation_update_concept->execute($arg{'ci_id'},$arg{'cb_id'},$rep_id) or die $dbh->errstr;
	$sth_representation_update_concept->finish;
	undef $sth_representation_update_concept;
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'."$arg{'ci_id'},$arg{'cb_id'},$rep_id\n";
	&cgi_lib::common::message("$arg{'ci_id'},$arg{'cb_id'},$rep_id", $LOG) if(defined $LOG);
	$callback->(undef) if(defined $callback);

#	&File::Path::rmtree($tempdir,0) or die if(-d $tempdir);

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Time::HiRes::tv_interval($t0)." s\n" if(DEBUG);
#$t0 = [&Time::HiRes::gettimeofday()] if(DEBUG);

}

sub Truncated {
	my $v = shift;
	return undef unless(defined $v);
	my $rate = 10000;
	return int($v * $rate + 0.5) / $rate;
}

1;
