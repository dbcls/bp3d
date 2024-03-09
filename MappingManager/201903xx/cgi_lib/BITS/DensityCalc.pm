package BITS::DensityCalc;

#use strict;
#use warnings;
#use feature ':5.10';

use constant {
	DEBUG => 0,
	BLD_PREFIX_ID => 2,
	OPEN_ID => qq|system|
};

use Encode;
use DBD::Pg;
use JSON::XS;
use File::Temp;
use Cwd;
use Time::HiRes;
use Data::Dumper;
$Data::Dumper::Indent = 1;
$Data::Dumper::Sortkeys = 1;

my $JSONXS;# = JSON::XS->new->utf8->indent(0)->canonical(1);
my $JSONXS_Extensions ;# = JSON::XS->new->utf8->indent(1)->canonical(1);
BEGIN{
	$JSONXS = JSON::XS->new->utf8->indent(0)->canonical(1);#->relaxed(0);
	$JSONXS_Extensions  = JSON::XS->new->utf8->indent(1)->canonical(1)->relaxed(1);
};

use FindBin;
#use lib qq|$FindBin::Bin/../..|,qq|$FindBin::Bin/../../IM|;

#print __LINE__,":",$FindBin::Bin,"\n" if(DEBUG);

#require "common.pl";
#require "common_db.pl";
#my $dbh = &get_dbh();

use obj2deci;

sub message {
	my $str = shift;
	my $fh = shift // \*STDERR;
	my($package, $file, $line, $subname, $hasargs, $wantarray, $evaltext, $is_require) = caller();
	$str = '' unless(defined $str && length $str);
	say $fh $package.':'.$line.':'.&encodeUTF8($str);
}

sub dumper {
	my $obj = shift;
	my $fh = shift // \*STDERR;
	my($package, $file, $line, $subname, $hasargs, $wantarray, $evaltext, $is_require) = caller();
	print $fh $package.':'.$line.':'.&Data::Dumper::Dumper($obj);
}

sub decodeUTF8 {
	my $str = shift;
	return $str unless(defined $str && length $str);
	$str = &Encode::decode_utf8($str) unless(&Encode::is_utf8($str));
	return $str;
}

sub encodeUTF8 {
	my $str = shift;
	return $str unless(defined $str && length $str);
	$str = &Encode::encode_utf8($str) if(&Encode::is_utf8($str));
	return $str;
}

sub decodeJSON {
	my $json_str = shift;
	my $ext = shift;
	my $json;
	return $json unless(defined $json_str && length $json_str);
	$ext = 1 unless(defined $ext);
	$json_str = &encodeUTF8($json_str);
	eval{$json = $ext ? $JSONXS_Extensions->decode($json_str) : $JSONXS->decode($json_str);};
	if($@){
		say STDERR __FILE__.':'.__LINE__.':'.$@;
		say STDERR __FILE__.':'.__LINE__.':'.$json_str;
	}
	return $json;
}

sub decodeExtensionsJSON {
	my $json_str = shift;
	return &decodeJSON($json_str,1);
}

sub encodeJSON {
	my $json = shift;
	my $ext = shift;
	$ext = 0 unless(defined $ext);
	my $json_str;
	eval{$json_str = $ext ? $JSONXS_Extensions->encode($json) : $JSONXS->encode($json);};
	say STDERR __FILE__.':'.__LINE__.':'.$@ if($@);
	return $json_str;
}

sub encodeExtensionsJSON {
	my $json = shift;
	return &encodeJSON($json,1);
}

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
	my $use_pids    = $arg{'use_pids'};

	$use_pids = {} unless(defined $use_pids);

#	delete $arg{'dbh'};
#	&message(encodeJSON(\%arg,1));

#	my $init_flag;
	unless(defined $cdi_ids){
		$cdi_ids = {};
#		$init_flag = 1;

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:get_rep_parent_id():$ci_id-$cb_id-$bul_id-$md_id-$mv_id-$mr_id.json\n| if(DEBUG);
	}

	$use_ids = &get_children_id(dbh=>$dbh, ci_id=>$ci_id,cb_id=>$cb_id,bul_id=>$bul_id,md_id=>$md_id,mv_id=>$mv_id) unless(defined $use_ids);
	return undef unless(defined $use_ids && scalar keys(%$use_ids)>0);

	unless(defined $route_ids){
		my $btr_id;


		my %ROOT_HASH_BTR;
		my $sql = qq|select btr_id from buildup_tree_route where ci_id=$ci_id and cb_id=$cb_id and bul_id=$bul_id and cdi_id in (select cdi_id from buildup_tree where ci_id=$ci_id and cb_id=$cb_id and bul_id=$bul_id and cdi_id is not null and cdi_pid is null and but_delcause is null) and btr_use|;
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":get_rep_parent_id():\$sql=[$sql]\n" if(DEBUG);
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":get_rep_parent_id():[",$sth->rows(),"]\n" if(DEBUG);
		$sth->bind_col(1, \$btr_id, undef);
		while($sth->fetch){
			next unless(defined $btr_id);
			$ROOT_HASH_BTR{$btr_id} = undef;
		}
		$sth->finish;
		undef $sth;
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":get_rep_parent_id():\n" if(DEBUG);

#		my $sql_rep = qq|select distinct cdi_id from representation where ci_id=$ci_id and cb_id=$cb_id and md_id=$md_id and mv_id=$mv_id and bul_id=$bul_id and rep_delcause is null|;
		my $sql_rep = join(",",keys(%$use_ids));

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":get_rep_parent_id():\$use_ids=[",(scalar keys(%$use_ids)),"]\n" if(DEBUG);

		{
			my $hash = {};
			my $cdi_id;
			my $but_cids;
			my $sql =<<SQL;
select
 cdi_id,
 but_cids
from
 buildup_tree
where
 but_delcause is null and
 ci_id=$ci_id and
 cb_id=$cb_id and
 bul_id=$bul_id and
 cdi_id in (
   select
    cdi_id
   from
    concept_art_map
   where
    (ci_id,cb_id,md_id,mv_id,mr_id,cdi_id) in (
      select
       ci_id,cb_id,md_id,mv_id,max(mr_id),cdi_id
      from
       concept_art_map
      where
       ci_id=$ci_id and
       cb_id=$cb_id and
       md_id=$md_id and
       mv_id=$mv_id and
       mr_id<=$mr_id and
       cdi_id in ($sql_rep)
      group by
       ci_id,cb_id,md_id,mv_id,cdi_id
    )
 )
SQL
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":get_rep_parent_id():\$sql=[$sql]\n" if(DEBUG);
			my $sth = $dbh->prepare($sql) or die $dbh->errstr;
			$sth->execute() or die $dbh->errstr;
			$sth->bind_col(1, \$cdi_id, undef);
			$sth->bind_col(2, \$but_cids, undef);
			while($sth->fetch){
				$hash->{$cdi_id} = undef;
				my $cids = &JSON::XS::decode_json($but_cids) if(defined $but_cids);
				if(defined $cids){
					foreach my $cid (@$cids){
						$hash->{$cid} = undef;
					}
				}
			}
			$sth->finish;
			undef $sth;
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":get_rep_parent_id():[",(scalar keys(%$hash)),"]\n" if(DEBUG);
			$sql_rep = join(",",keys(%$hash));
		}

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\$sql_rep=[$sql_rep]\n" if(DEBUG);
		my $sql_route = qq|select distinct btr_id from buildup_tree_route where ci_id=$ci_id and cb_id=$cb_id and cdi_id in ($sql_rep) and bul_id=$bul_id and btr_use and btr_delcause is null|;
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\$sql_route=[$sql_route]\n" if(DEBUG);

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\n" if(DEBUG);
		my $sth = $dbh->prepare($sql_route) or die $dbh->errstr;
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\n" if(DEBUG);
		$sth->execute() or die $dbh->errstr;
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":[",$sth->rows(),"]\n" if(DEBUG);
		$sth->bind_col(1, \$btr_id, undef);
		while($sth->fetch){
			next unless(defined $btr_id);

			next unless(exists $ROOT_HASH_BTR{$btr_id});

			$route_ids->{$btr_id} = undef;
		}
		$sth->finish;
		undef $sth;
#		print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\$route_ids=[".&Data::Dumper::Dumper($route_ids)."]\n" if(DEBUG);
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":get_rep_parent_id():\$route_ids=[",(scalar keys(%$route_ids)),"]\n" if(DEBUG);
	}


	my %CDI_PIDS;
	my $cdi_pid;
	my $cdi_pname;


	unless(defined $cdi_name || defined $cdi_id){
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":get_rep_parent_id():\n" if(DEBUG);
		my $sql_route = qq|select distinct cdi_id from buildup_tree_route where ci_id=$ci_id and cb_id=$cb_id and btr_id in (|.(join(",",sort keys(%$route_ids))).qq|) and bul_id=$bul_id and btr_use and btr_delcause is null|;
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
    cm.mr_id<=$mr_id and
    cm.cdi_id in ($sql_route) and
    cm.cm_use and
    cm.cm_delcause is null
   group by
    cm.ci_id,
    cm.cb_id,
    cm.md_id,
    cm.mv_id,
    cm.cdi_id
  )
SQL
		}elsif(defined $md_id && defined $mv_id){
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
    cm.cdi_id in ($sql_route) and
    cm.cm_use and
    cm.cm_delcause is null
   group by
    cm.ci_id,
    cm.cb_id,
    cm.md_id,
    cm.mv_id,
    cm.cdi_id
  )
SQL
		}else{
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\n" if(DEBUG);
			$sql_rep =<<SQL;
select distinct
 btr.cdi_pid,
 cdi_name
from
 buildup_tree_route as btr
left join (
 select ci_id,cdi_id,cdi_name from concept_data_info
) as cdi on cdi.ci_id=btr.ci_id and cdi.cdi_id=btr.cdi_pid
where
 btr.ci_id=$ci_id and
 btr.cb_id=$cb_id and
 btr.bul_id=$bul_id and
 btr.cdi_id is null and
 btr.btr_use and
 btr.btr_delcause is null
SQL
	$sql_rep .= qq| and btr.btr_id in (|.(join(",",sort keys(%$route_ids))).qq|)|;

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
		my $sth = $dbh->prepare(qq|select cdi_name_e from concept_data_info where ci_id=$ci_id and cdi_id=?|) or die $dbh->errstr;
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
#			&message("[$cdi_id][$cdi_name]") if(exists $cdi_ids->{$cdi_id});
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

#			my $sql_route = qq|select distinct btr_id from buildup_tree_route where ci_id=$ci_id and cb_id=$cb_id and bul_id=$bul_id and cdi_id=$cdi_id and btr_id in (|.(join(",",sort keys(%$route_ids))).qq|) and btr_use and btr_delcause is null|;

			my $sql_cdi = qq|left join (select ci_id,cdi_id,cdi_name,cdi_name_e from concept_data_info) as cdi on (cdi.ci_id=but.ci_id and cdi.cdi_id=but.cdi_pid)|;
			my $sql_but = qq|select distinct cdi_pid,cdi.cdi_name,cdi.cdi_name_e from buildup_tree as but $sql_cdi where but.ci_id=$ci_id and but.cb_id=$cb_id and but.cdi_id=$cdi_id and but.cdi_pid is not null and but.bul_id=$bul_id and but.but_delcause is null|;
#			my $sql_but = qq|select distinct cdi_pid,cdi.cdi_name,cdi.cdi_name_e from buildup_tree_route as but $sql_cdi where but.ci_id=$ci_id and but.cb_id=$cb_id and but.cdi_id=$cdi_id and but.cdi_pid is not null and but.bul_id=$bul_id and btr_id in (|.(join(",",sort keys(%$route_ids))).qq|) and btr_use and but.btr_delcause is null|;

#			print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":get_rep_parent_id():\$sql_cdi=[$sql_cdi]\n" if(DEBUG);
#			print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":get_rep_parent_id():\$sql_but=[$sql_but]\n" if(DEBUG);

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

					$cdi_ids->{$cdi_id}->{'cdi_pid'}->{$cdi_pid} = undef;
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
			&message("[$cdi_pid][$CDI_PIDS{$cdi_pid}]");
			next;
		}else{
			$use_pids->{$cdi_pid} = undef;
		}
		&get_rep_parent_id(dbh=>$dbh, cdi_ids=>$cdi_ids,route_ids=>$route_ids,cdi_cid=>$cdi_id,cdi_id=>$cdi_pid,cdi_name=>$CDI_PIDS{$cdi_pid},ci_id=>$ci_id,cb_id=>$cb_id,bul_id=>$bul_id,md_id=>$md_id,mv_id=>$mv_id, use_ids=>$use_ids, use_pids=>$use_pids);
	}

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\n" if(DEBUG);
	return wantarray ? ($cdi_ids,$route_ids,$use_ids) : $cdi_ids;

}

sub get_children_id {
	my %arg = @_;
	my $dbh       = $arg{'dbh'};
	my $hash      = $arg{'hash'};
	my $cdi_pname = $arg{'cdi_name'};
	my $cdi_pid   = $arg{'cdi_id'};
	my $ci_id     = $arg{'ci_id'};
	my $cb_id     = $arg{'cb_id'};
	my $bul_id    = $arg{'bul_id'};
	my $depth     = $arg{'depth'};

	my $md_id     = $arg{'md_id'};
	my $mv_id     = $arg{'mv_id'};

=pod
	my $init_flag;
	unless(defined $hash){
		$init_flag = 1;

		my $prefix = qq|$FindBin::Bin/|. __PACKAGE__;
		my $old_umask = umask();
		umask(0);
		&File::Path::mkpath($prefix,0,0777) unless(-e $prefix);
		my $path = File::Spec->catdir($prefix,qq|get_children_id-$ci_id-$cb_id-$bul_id.json|);
		if(-e $path){
			my $CACHE;
			if(open($CACHE,$path)){
				flock($CACHE,1);
				my @TEMP = <$CACHE>;
				close($CACHE);
				$hash = &JSON::XS::decode_json(join('',@TEMP));
			}
		}
		return $hash if(defined $hash);
	}
=cut

	my @IDS;
	unless(defined $hash){

		$hash = {};
		my $cdi_id;
		my $but_cids;
		my $sql = qq|select cdi_id,but_cids from buildup_tree where ci_id=$ci_id and cb_id=$cb_id and bul_id=$bul_id and cdi_id is not null and cdi_pid is null and but_delcause is null|;
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":get_children_id():\$sql=[$sql]\n" if(DEBUG);
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$sth->bind_col(1, \$cdi_id, undef);
		$sth->bind_col(2, \$but_cids, undef);
		while($sth->fetch){
			next unless(defined $cdi_id);
			push(@IDS,$cdi_id);

			$hash->{$cdi_id} = undef;
			my $cids = &JSON::XS::decode_json($but_cids) if(defined $but_cids);
			if(defined $cids){
				foreach my $cid (@$cids){
					$hash->{$cid} = undef;
				}
			}
		}
		$sth->finish;
		undef $sth;

	}else{
		$depth = 0 unless(defined $depth);

		if(defined $cdi_pname && !defined $cdi_pid){
			my $sth = $dbh->prepare(qq|select cdi_id from concept_data_info where ci_id=$ci_id and cdi_name=?|) or die $dbh->errstr;
			$sth->execute($cdi_pname) or die $dbh->errstr;
			$sth->bind_col(1, \$cdi_pid, undef);
			$sth->fetch;
			$sth->finish;
			undef $sth;
		}
		if(!defined $cdi_pname && defined $cdi_pid){
			my $sth = $dbh->prepare(qq|select cdi_name from concept_data_info where ci_id=$ci_id and cdi_id=?|) or die $dbh->errstr;
			$sth->execute($cdi_pid) or die $dbh->errstr;
			$sth->bind_col(1, \$cdi_pname, undef);
			$sth->fetch;
			$sth->finish;
			undef $sth;
		}

#		return if(defined $cdi_pname && exists $hash->{$cdi_pname});
		return if(defined $cdi_pid && exists $hash->{$cdi_pid});


#		$hash->{$cdi_pname} = undef if(defined $cdi_pname);
		$hash->{$cdi_pid} = undef if(defined $cdi_pid);

		my $cdi_id;
		my $but_cids;
		my $sth = $dbh->prepare(qq|select cdi_id,but_cids from buildup_tree where ci_id=$ci_id and cb_id=$cb_id and bul_id=$bul_id and cdi_pid=? and but_delcause is null|) or die $dbh->errstr;
		$sth->execute($cdi_pid) or die $dbh->errstr;
		$sth->bind_col(1, \$cdi_id, undef);
		$sth->bind_col(2, \$but_cids, undef);
		while($sth->fetch){
			next unless(defined $cdi_id);
			push(@IDS,$cdi_id);

			$hash->{$cdi_id} = undef;
			my $cids = &JSON::XS::decode_json($but_cids) if(defined $but_cids);
			if(defined $cids){
				foreach my $cid (@$cids){
					$hash->{$cid} = undef;
				}
			}
		}
		$sth->finish;
		undef $sth;
	}
#	foreach my $cdi_id (@IDS){
#		&get_children_id(dbh=>$dbh, hash=>$hash,cdi_id=>$cdi_id,ci_id=>$ci_id,cb_id=>$cb_id,bul_id=>$bul_id,depth=>$depth+1,md_id=>$md_id,mv_id=>$mv_id);
#	}

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":get_children_id():\$hash=[",(scalar keys(%$hash)),"]\n" if(DEBUG);


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
 cb_id=$cb_id and
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
 cb_id=$cb_id and
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
#	print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":clear_representation_density():\$sql=[$sql]\n" if(DEBUG);
	my $sth_upd = $dbh->prepare($sql) or die $dbh->errstr;
	$sth_upd->execute($rep_delcause,$rep_id) or die $dbh->errstr;
	my $rows = $sth_upd->rows();
	$sth_upd->finish;
	undef $sth_upd;
#	print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":clear_representation_density():\$rows=[$rows]\n" if(DEBUG);
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

	unless(
		defined $ci_id &&
		defined $cb_id &&
		defined $bul_id &&
		defined $md_id &&
		defined $mv_id &&
		defined $mr_id &&
		defined $cdi_id
	){
		print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$ci_id=[$ci_id]:\$cb_id=[$cb_id]:\$bul_id=[$bul_id]:\$md_id=[$md_id]:\$mv_id=[$mv_id]:\$mr_id=[$mr_id]:\$cdi_id=[$cdi_id]:\$cdi_name=[$cdi_name]\n| if(DEBUG);
		return;
	}

print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$ci_id=[$ci_id]:\$cb_id=[$cb_id]:\$bul_id=[$bul_id]:\$md_id=[$md_id]:\$mv_id=[$mv_id]:\$mr_id=[$mr_id]:\$cdi_id=[$cdi_id]:\$cdi_name=[$cdi_name]\n| if(DEBUG);
my $t0 = [&Time::HiRes::gettimeofday()] if(DEBUG);

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
 cb_id=$cb_id and
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

	my %ART_IDS;
	my $art_id;
	my $art_hist_serial;
	my $prefix_id;
	my $art_serial;
	my $art_mirroring;

	#指定ノードの末端へのroute_idを取得
	my $btr_id;
	my %HASH_BTR;
	my $sql_btr = qq|select btr_id from buildup_tree_route where ci_id=$ci_id and cb_id=$cb_id and bul_id=$bul_id and cdi_id=$cdi_id and btr_use group by btr_id|;
	my $sth = $dbh->prepare($sql_btr) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$sth->bind_col(1, \$btr_id, undef);
	while($sth->fetch){
		next unless(defined $btr_id);
		$HASH_BTR{$btr_id} = undef;
	}
	$sth->finish;
	undef $sth;

print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Time::HiRes::tv_interval($t0)." s\n" if(DEBUG);
$t0 = [&Time::HiRes::gettimeofday()] if(DEBUG);

	#route_idから末端ノードを取得
	my %HASH_END;
	my %HASH_BTR2END;
	if(scalar keys(%HASH_BTR) > 0){
		my $cdi_id_end;
		my $btr_id;
#		my $sth = $dbh->prepare(qq|select distinct cdi_pid,btr_id from buildup_tree_route where ci_id=$ci_id and cb_id=$cb_id and bul_id=$bul_id and cdi_id is null and btr_use and btr_id in (|.join(",",keys(%HASH_BTR)).qq|)|) or die $dbh->errstr;
		my $sth = $dbh->prepare(qq|select cdi_pid,btr_id from buildup_tree_route where ci_id=$ci_id and cb_id=$cb_id and bul_id=$bul_id and cdi_id is null and btr_use and btr_id in ($sql_btr) group by cdi_pid,btr_id|) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$sth->bind_col(1, \$cdi_id_end, undef);
		$sth->bind_col(2, \$btr_id, undef);
		while($sth->fetch){
			next unless(defined $cdi_id_end && defined $btr_id);
			$HASH_END{$cdi_id_end} = $btr_id;
			$HASH_BTR2END{$btr_id} = $cdi_id_end;
		}
		$sth->finish;
		undef $sth;
	}

print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Time::HiRes::tv_interval($t0)." s\n" if(DEBUG);
$t0 = [&Time::HiRes::gettimeofday()] if(DEBUG);

	#rep_primitive更新
=pod
	my $rep_primitive=0;
	my $but_cids;
	my $sth = $dbh->prepare(qq|select but_cids from buildup_tree where ci_id=$ci_id and cb_id=$cb_id and bul_id=$bul_id and cdi_id=$cdi_id and but_delcause is null|) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	my $but_rows = $sth->rows();
	if($but_rows>0){
		$sth->bind_col(1, \$but_cids, undef);
		$sth->fetch;
	}
	$sth->finish;
	undef $sth;
	$rep_primitive=1 if($but_rows>0 && !defined $but_cids);
	if($rep_primitive==0 && defined $but_cids){
		my $a;
		eval{$a = &JSON::XS::decode_json($but_cids);};
		if(defined $a && ref $a eq 'ARRAY' && scalar @$a > 0){
#			print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$but_cids=[|.(scalar @$a).qq|]\n| if(DEBUG);
			my $sql_fmt=<<SQL;
select cm_id from concept_art_map where
(ci_id,cb_id,md_id,mv_id,mr_id,cdi_id) in (
  select
   ci_id,cb_id,md_id,mv_id,max(mr_id),cdi_id
  from
   concept_art_map
  where
   ci_id=$ci_id and cb_id=$cb_id and md_id=$md_id and mv_id=$mv_id and mr_id<=$mr_id
  group by
   ci_id,cb_id,md_id,mv_id,cdi_id
)
and cm_use
and cm_delcause is null
and cdi_id in (%s)
SQL
			my $sql = sprintf($sql_fmt,join(",",@$a));
#			print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$sql=[$sql]\n| if(DEBUG);
			my $sth = $dbh->prepare($sql) or die $dbh->errstr;
			$sth->execute() or die $dbh->errstr;
			my $rows = $sth->rows();
			$sth->finish;
			undef $sth;
			$rep_primitive=1 if($rows==0);
		}
	}
=cut

	my $rep_primitive=0;
	$rep_primitive = 1 unless(exists $cdi_ids->{$cdi_id}->{'cdi_cids'} && defined $cdi_ids->{$cdi_id}->{'cdi_cids'} && ref $cdi_ids->{$cdi_id}->{'cdi_cids'} eq 'HASH');

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Time::HiRes::tv_interval($t0)." s\n" if(DEBUG);
#$t0 = [&Time::HiRes::gettimeofday()] if(DEBUG);

	if(DEBUG){
#		print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$but_rows=[$but_rows]\n|;
#		print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$but_cids=[$but_cids]\n|;
#		print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$rep_primitive=[$rep_primitive]\n|;
#		die "aa" if(defined $but_cids && $rep_primitive);
	}

	my $sql_representation_update_primitive=<<SQL;
update representation set
 rep_primitive=?,
 rep_entry=now()
where
 rep_id=?
SQL
	my $sth_representation_update_primitive = $dbh->prepare($sql_representation_update_primitive);
	$sth_representation_update_primitive->execute($rep_primitive,$rep_id) or die $dbh->errstr;
	$sth_representation_update_primitive->finish;
	undef $sth_representation_update_primitive;



	my $rep_child_objs;
	my $rep_density_objs = 0;
	my $rep_density_ends;
	my $rep_density_end_ids;
	my $rep_density_all_ends;
	my $rep_density_all_end_ids;

	my $sql=<<SQL;
select
 art_id,
 hist_serial,
 prefix_id,
 art_serial,
 art_mirroring
from
 history_art_file
where
 (art_id,hist_serial) in (
   select
    art_id,
    art_hist_serial
   from
    concept_art_map
   where
    cm_use and
    (ci_id,cb_id,md_id,mv_id,mr_id,cdi_id) in (
      select
       ci_id,
       cb_id,
       md_id,
       mv_id,
       max(mr_id) as mr_id,
       cdi_id
      from
       concept_art_map
      where
       cm_use and
       cm_delcause is null and
       ci_id=? and
       cb_id=? and
       md_id=? and
       mv_id=? and
       mr_id<=? and
       cdi_id=?
      group by
       ci_id,
       cb_id,
       md_id,
       mv_id,
       cdi_id
    )
 )
SQL
	my $sth_rep5 = $dbh->prepare($sql);


	my $sql_pri_fmt=<<SQL;
select distinct cdi_id from representation where
 (md_id,mv_id,mr_id,ci_id,cb_id,bul_id,cdi_id) in (
   select 
    md_id,
    mv_id,
    max(mr_id) as mr_id,
    ci_id,
    cb_id,
    bul_id,
    cdi_id
   from
    representation
   where
    md_id=$md_id and
    mv_id=$mv_id and
    mr_id<=$mr_id and
    ci_id=$ci_id and
    cb_id=$cb_id and
    bul_id=$bul_id and
    rep_primitive and
    rep_delcause is null and
    cdi_id in (%s)
   group by
    md_id,
    mv_id,
    ci_id,
    cb_id,
    bul_id,
    cdi_id
 )
SQL

print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Time::HiRes::tv_interval($t0)." s\n" if(DEBUG);
$t0 = [&Time::HiRes::gettimeofday()] if(DEBUG);

	my $sql_btr_fmt=qq|select distinct cdi_id,btr_id from buildup_tree_route where ci_id=$ci_id and cb_id=$cb_id and bul_id=$bul_id and btr_use and cdi_id in (%s) order by btr_id|;

	if(exists $cdi_ids->{$cdi_id}->{'cdi_cids'} && defined $cdi_ids->{$cdi_id}->{'cdi_cids'} && ref $cdi_ids->{$cdi_id}->{'cdi_cids'} eq 'HASH'){
		my $cdi_cids_rows = scalar keys(%{$cdi_ids->{$cdi_id}->{'cdi_cids'}});
		my $cdi_cids_row = 0;
		foreach my $cdi_cid (keys(%{$cdi_ids->{$cdi_id}->{'cdi_cids'}})){
			$cdi_cids_row++;
#			print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":$ci_id,$cb_id,$md_id,$mv_id,$mr_id,$cdi_cid\n" if(DEBUG);
			$sth_rep5->execute($ci_id,$cb_id,$md_id,$mv_id,$mr_id,$cdi_cid) or die $dbh->errstr;
			$sth_rep5->bind_col(1, \$art_id, undef);
			$sth_rep5->bind_col(2, \$art_hist_serial, undef);
			$sth_rep5->bind_col(3, \$prefix_id, undef);
			$sth_rep5->bind_col(4, \$art_serial, undef);
			$sth_rep5->bind_col(5, \$art_mirroring, undef);
			while($sth_rep5->fetch){
				$ART_IDS{qq|$art_id\t$art_hist_serial|} = undef;
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper(\%ART_IDS) if(DEBUG);

				if($art_mirroring){
					my $sql =<<SQL;
select
 cm_id,
 art_id,
 art_hist_serial
from
 concept_art_map
where
 (ci_id,cb_id,md_id,mv_id,mr_id,cdi_id) in (
   select
    ci_id,
    cb_id,
    md_id,
    mv_id,
    max(mr_id) as mr_id,cdi_id
   from
    concept_art_map
   where
    ci_id=$ci_id and
    cb_id=$cb_id and
    md_id=$md_id and
    mv_id=$mv_id and
    mr_id<=$mr_id
   group by
    ci_id,
    cb_id,
    md_id,
    mv_id,cdi_id
 ) and
 cm_delcause is null and
 cm_use and
 cdi_id=$cdi_cid and
 (art_id,art_hist_serial) in (
   select
    art_id,
    max(hist_serial) as hist_serial
   from
    history_art_file
   where
    prefix_id=$prefix_id and
    art_serial=$art_serial and
    art_mirroring=FALSE
   group by
    art_id
 )
SQL
					my $cm_id;
					my $art_id_m;
					my $art_hist_serial_m;
					my $sth = $dbh->prepare($sql) or die $dbh->errstr;
					$sth->execute() or die $dbh->errstr;
					$sth->bind_col(1, \$cm_id, undef);
					$sth->bind_col(2, \$art_id_m, undef);
					$sth->bind_col(3, \$art_hist_serial_m, undef);
					my $rows = $sth->rows();
					$sth->fetch;
					$sth->finish;
					undef $sth;
					if($rows>0){
#						print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":$art_id:$art_mirroring:$cm_id:$rows\n" if(DEBUG);
#						print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":$art_id_m:$art_hist_serial_m\n" if(DEBUG);
#						print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":$sql\n" if(DEBUG);
#						exit;
						$ART_IDS{qq|$art_id_m\t$art_hist_serial_m|} = undef;
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper(\%ART_IDS) if(DEBUG);
					}
				}else{
					my $sql =<<SQL;
select
 cm_id,
 art_id,
 art_hist_serial
from
 concept_art_map
where
 (ci_id,cb_id,md_id,mv_id,mr_id,cdi_id) in (
   select
    ci_id,
    cb_id,
    md_id,
    mv_id,
    max(mr_id) as mr_id,cdi_id
   from
    concept_art_map
   where
    ci_id=$ci_id and
    cb_id=$cb_id and
    md_id=$md_id and
    mv_id=$mv_id and
    mr_id<=$mr_id
   group by
    ci_id,
    cb_id,
    md_id,
    mv_id,cdi_id
 ) and
 cm_delcause is null and
 cm_use and
 cdi_id=$cdi_cid and
 (art_id,art_hist_serial) in (
   select
    art_id,
    max(hist_serial) as hist_serial
   from
    history_art_file
   where
    prefix_id=$prefix_id and
    art_serial=$art_serial and
    art_mirroring
   group by
    art_id
 )
SQL
					my $cm_id;
					my $art_id_m;
					my $art_hist_serial_m;
					my $sth = $dbh->prepare($sql) or die $dbh->errstr;
					$sth->execute() or die $dbh->errstr;
					$sth->bind_col(1, \$cm_id, undef);
					$sth->bind_col(2, \$art_id_m, undef);
					$sth->bind_col(3, \$art_hist_serial_m, undef);
					my $rows = $sth->rows();
					$sth->fetch;
					$sth->finish;
					undef $sth;
					if($rows>0){
#						print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":$art_id:$art_mirroring:$cm_id:$rows\n" if(DEBUG);
#						print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":$art_id_m:$art_hist_serial_m\n" if(DEBUG);
#						print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":$sql\n" if(DEBUG);
#						exit;
						$ART_IDS{qq|$art_id_m\t$art_hist_serial_m|} = undef;
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper(\%ART_IDS) if(DEBUG);
					}
				}
			}
			$sth_rep5->finish;

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Time::HiRes::tv_interval($t0)." s\n" if(DEBUG);
#$t0 = [&Time::HiRes::gettimeofday()] if(DEBUG);

			$callback->(qq|Get Object ($cdi_cids_row/$cdi_cids_rows)|) if(defined $callback);

		}

		my %PRI;
		my $cdi_id_pri;
		my $sql=sprintf($sql_pri_fmt,join(",",keys(%{$cdi_ids->{$cdi_id}->{'cdi_cids'}})));
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$sth->bind_col(1, \$cdi_id_pri, undef);
		$rep_density_objs += $sth->rows();
		while($sth->fetch){
			$PRI{$cdi_id_pri} = undef if(defined $cdi_id_pri);
		}
		$sth->finish;
		undef $sth;

		if(scalar keys(%PRI) > 0){
			my $sql=sprintf($sql_btr_fmt,join(",",keys(%PRI)));
			my $cdi_id_temp;
			my $btr_id;
			my $sth = $dbh->prepare($sql) or die $dbh->errstr;
			$sth->execute() or die $dbh->errstr;
			$sth->bind_col(1, \$cdi_id_temp, undef);
			$sth->bind_col(2, \$btr_id, undef);
			while($sth->fetch){
				next unless(defined $btr_id && defined $cdi_id_temp && exists($HASH_BTR2END{$btr_id}));
				$HASH_BTR2END{$btr_id} = $cdi_id_temp;
			}
			$sth->finish;
			undef $sth;
		}
#	}else{
#		$rep_density_objs = 0;
	}

	$callback->(qq|Calculation density|) if(defined $callback);

print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Time::HiRes::tv_interval($t0)." s\n" if(DEBUG);
$t0 = [&Time::HiRes::gettimeofday()] if(DEBUG);
	{
		my %PRI;
		my $cdi_id_pri;
#		my $sql=qq|select distinct cdi_id from representation where md_id=$md_id and mv_id=$mv_id and mr_id=$mr_id and ci_id=$ci_id and cb_id=$cb_id and bul_id=$bul_id and rep_primitive and rep_delcause is null and cdi_id=$cdi_id|;
		my $sql=sprintf($sql_pri_fmt,qq|$cdi_id|);
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$sth->bind_col(1, \$cdi_id_pri, undef);
		$rep_density_objs += $sth->rows();
		while($sth->fetch){
			$PRI{$cdi_id_pri} = undef if(defined $cdi_id_pri);
		}
		$sth->finish;
		undef $sth;

		if(scalar keys(%PRI) > 0){
			my $sql=sprintf($sql_btr_fmt,join(",",keys(%PRI)));
			my $cdi_id_temp;
			my $btr_id;
			my $sth = $dbh->prepare($sql) or die $dbh->errstr;
			$sth->execute() or die $dbh->errstr;
			$sth->bind_col(1, \$cdi_id_temp, undef);
			$sth->bind_col(2, \$btr_id, undef);
			while($sth->fetch){
				next unless(defined $btr_id && defined $cdi_id_temp && exists($HASH_BTR2END{$btr_id}));
				$HASH_BTR2END{$btr_id} = $cdi_id_temp;
			}
			$sth->finish;
			undef $sth;
		}

	}

print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Time::HiRes::tv_interval($t0)." s\n" if(DEBUG);
$t0 = [&Time::HiRes::gettimeofday()] if(DEBUG);

	$sth_rep5->execute($ci_id,$cb_id,$md_id,$mv_id,$mr_id,$cdi_id) or die $dbh->errstr;
	$sth_rep5->bind_col(1, \$art_id, undef);
	$sth_rep5->bind_col(2, \$art_hist_serial, undef);
	$sth_rep5->bind_col(3, \$prefix_id, undef);
	$sth_rep5->bind_col(4, \$art_serial, undef);
	$sth_rep5->bind_col(5, \$art_mirroring, undef);
	while($sth_rep5->fetch){
		$ART_IDS{qq|$art_id\t$art_hist_serial|} = undef;
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper(\%ART_IDS) if(DEBUG);

		if($art_mirroring){
			my $sql =<<SQL;
select
 cm_id,
 art_id,
 art_hist_serial
from
 concept_art_map
where
 (ci_id,cb_id,md_id,mv_id,mr_id,cdi_id) in (
   select
    ci_id,
    cb_id,
    md_id,
    mv_id,
    max(mr_id) as mr_id,cdi_id
   from
    concept_art_map
   where
    ci_id=$ci_id and
    cb_id=$cb_id and
    md_id=$md_id and
    mv_id=$mv_id and
    mr_id<=$mr_id
   group by
    ci_id,
    cb_id,
    md_id,
    mv_id,cdi_id
 ) and
 cm_delcause is null and
 cm_use and
 cdi_id=$cdi_id and
 (art_id,art_hist_serial) in (
   select
    art_id,
    max(hist_serial) as hist_serial
   from
    history_art_file
   where
    prefix_id=$prefix_id and
    art_serial=$art_serial and
    art_mirroring=FALSE
   group by
    art_id
 )
SQL
			my $cm_id;
			my $art_id_m;
			my $art_hist_serial_m;
			my $sth = $dbh->prepare($sql) or die $dbh->errstr;
			$sth->execute() or die $dbh->errstr;
			$sth->bind_col(1, \$cm_id, undef);
			$sth->bind_col(2, \$art_id_m, undef);
			$sth->bind_col(3, \$art_hist_serial_m, undef);
			my $rows = $sth->rows();
			$sth->fetch;
			$sth->finish;
			undef $sth;
			if($rows>0){
#				print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":$art_id:$art_mirroring:$cm_id:$rows\n" if(DEBUG);
#				print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":$art_id_m:$art_hist_serial_m\n" if(DEBUG);
#						print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":$sql\n" if(DEBUG);
#						exit;
				$ART_IDS{qq|$art_id_m\t$art_hist_serial_m|} = undef;
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper(\%ART_IDS) if(DEBUG);
			}
		}else{
			my $sql =<<SQL;
select
 cm_id,
 art_id,
 art_hist_serial
from
 concept_art_map
where
 (ci_id,cb_id,md_id,mv_id,mr_id,cdi_id) in (
   select
    ci_id,
    cb_id,
    md_id,
    mv_id,
    max(mr_id) as mr_id,cdi_id
   from
    concept_art_map
   where
    ci_id=$ci_id and
    cb_id=$cb_id and
    md_id=$md_id and
    mv_id=$mv_id and
    mr_id<=$mr_id
   group by
    ci_id,
    cb_id,
    md_id,
    mv_id,cdi_id
 ) and
 cm_delcause is null and
 cm_use and
 cdi_id=$cdi_id and
 (art_id,art_hist_serial) in (
   select
    art_id,
    max(hist_serial) as hist_serial
   from
    history_art_file
   where
    prefix_id=$prefix_id and
    art_serial=$art_serial and
    art_mirroring
   group by
    art_id
 )
SQL
			my $cm_id;
			my $art_id_m;
			my $art_hist_serial_m;
			my $sth = $dbh->prepare($sql) or die $dbh->errstr;
			$sth->execute() or die $dbh->errstr;
			$sth->bind_col(1, \$cm_id, undef);
			$sth->bind_col(2, \$art_id_m, undef);
			$sth->bind_col(3, \$art_hist_serial_m, undef);
			my $rows = $sth->rows();
			$sth->fetch;
			$sth->finish;
			undef $sth;
			if($rows>0){
#				print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":$art_id:$art_mirroring:$cm_id:$rows\n" if(DEBUG);
#				print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":$art_id_m:$art_hist_serial_m\n" if(DEBUG);
#						print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":$sql\n" if(DEBUG);
#						exit;
				$ART_IDS{qq|$art_id_m\t$art_hist_serial_m|} = undef;
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper(\%ART_IDS) if(DEBUG);
			}
		}

	}
	$sth_rep5->finish;
	undef $sth_rep5;

print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Time::HiRes::tv_interval($t0)." s\n" if(DEBUG);
$t0 = [&Time::HiRes::gettimeofday()] if(DEBUG);

	$rep_child_objs = scalar keys(%ART_IDS);


	my %HASH_END2;
	foreach (keys(%HASH_BTR2END)){
		$HASH_END2{$HASH_BTR2END{$_}} = undef;
	}

#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\%HASH_END2=[",scalar keys(%HASH_END2),"]\n" if(DEBUG);
#print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.":\$cdi_cids=[",scalar keys(%{$cdi_ids->{$cdi_id}->{'cdi_cids'}}),"]\n" if(DEBUG);


	my $rep_density_ends = scalar keys(%HASH_END2);
	my $rep_density_end_ids;
	if($rep_density_ends>0){
		my @END_IDS = keys(%HASH_END2);
		$rep_density_end_ids = &JSON::XS::encode_json(\@END_IDS);
	}

	my $rep_density_all_ends = scalar keys(%HASH_END);
	my $rep_density_all_end_ids;
	if($rep_density_all_ends>0){
		my @END_IDS = keys(%HASH_END);
		$rep_density_all_end_ids = &JSON::XS::encode_json(\@END_IDS);
	}

#	print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\t\$rep_child_objs=[$rep_child_objs]\n| if(DEBUG);
#	print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\t\$rep_density=[$rep_density_objs][$rep_density_ends][|,($rep_density_objs/$rep_density_ends),qq|]\n| if(DEBUG);
#	print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\t[$rep_density_all_ends]\n| if(DEBUG);

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
 rep.cb_id=cmm.cb_id AND
 rep.bul_id=cmm.bul_id AND
 rep.cdi_id=cmm.cdi_id AND
 rep.md_id=cmm.md_id AND
 rep.mv_id=cmm.mv_id AND
 rep.mr_id=cmm.mr_id 
where
 rep_delcause is null and
 (rep.ci_id,rep.cb_id,rep.bul_id,rep.cdi_id) in (select ci_id,cb_id,bul_id,cdi_id from buildup_tree where ci_id=$ci_id and cb_id=$cb_id and bul_id=$bul_id and cdi_pid=$cdi_id) and rep.md_id=$md_id and rep.mv_id=$mv_id and rep.mr_id=$mr_id
 and rep_entry<cm_modified
|;
	print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$sql_modified_count=[$sql_modified_count]\n| if(DEBUG);
	my $sth = $dbh->prepare($sql_modified_count) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	my $modified_count = $sth->rows();
	print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$modified_count=[$modified_count]\n| if(DEBUG);
	if(DEBUG){
		my $rep_entry;
		my $cm_modified;
		my $cdi_name;
		$sth->bind_col(1, \$rep_entry, undef);
		$sth->bind_col(2, \$cm_modified, undef);
		$sth->bind_col(3, \$cdi_name, undef);
		while($sth->fetch){
			print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$rep_entry=[$rep_entry]:\$cm_modified=[$cm_modified]:\$cdi_name=[$cdi_name]\n|;
		}
	}
	$sth->finish;
	undef $sth;

	my $sql_rep_entry;
	if($modified_count>0){
		$sql_rep_entry = qq|select EXTRACT(EPOCH FROM COALESCE(min(rep_entry),now())) as min_rep_entry from representation where (ci_id,cb_id,bul_id,cdi_id) in (select ci_id,cb_id,bul_id,cdi_id from buildup_tree where ci_id=$ci_id and cb_id=$cb_id and bul_id=$bul_id and cdi_pid=$cdi_id) and md_id=$md_id and mv_id=$mv_id and mr_id=$mr_id|;
	}else{
		$sql_rep_entry = qq|select EXTRACT(EPOCH FROM COALESCE(max(rep_entry),now())) as min_rep_entry from representation where (ci_id,cb_id,bul_id,cdi_id) in (select ci_id,cb_id,bul_id,cdi_id from buildup_tree where ci_id=$ci_id and cb_id=$cb_id and bul_id=$bul_id and cdi_pid=$cdi_id) and md_id=$md_id and mv_id=$mv_id and mr_id=$mr_id|;
	}
	print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$sql_rep_entry=[$sql_rep_entry]\n| if(DEBUG);
	my $sth = $dbh->prepare($sql_rep_entry) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	my $update_rep_entry;
	$sth->bind_col(1, \$update_rep_entry, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;
	print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$update_rep_entry=[$update_rep_entry]\n| if(DEBUG);


	my $sql_cm_entry = qq|select EXTRACT(EPOCH FROM max(cm_entry)) as max_cm_entry from concept_art_map where ci_id=$ci_id and cb_id=$cb_id and md_id=$md_id and mv_id=$mv_id and mr_id=$mr_id and cdi_id=$cdi_id|;
	my $sth = $dbh->prepare($sql_cm_entry) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	my $update_cm_entry;
	$sth->bind_col(1, \$update_cm_entry, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;
	if(defined $update_cm_entry){
		print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$update_rep_entry=[$update_rep_entry]:\$update_cm_entry=[$update_cm_entry]\n| if(DEBUG);
		$update_rep_entry = $update_cm_entry if($update_rep_entry<$update_cm_entry);
	}
	print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$update_rep_entry=[$update_rep_entry]\n| if(DEBUG);


	if($rep_child_objs>0){
		my $sql_representation_update_density=<<SQL;
update representation set
 rep_child_objs=?,
 rep_density_objs=?,
 rep_density_ends=?,
 rep_density_end_ids=?,
 rep_density_all_ends=?,
 rep_density_all_end_ids=?,
 rep_delcause=null,
 rep_entry=(TIMESTAMP WITH TIME ZONE 'epoch' + ? * INTERVAL '1 second')
where
 rep_id=?
SQL
#		print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$sql_representation_update_density=[$sql_representation_update_density]\n| if(DEBUG);
		my $sth_representation_update_density = $dbh->prepare($sql_representation_update_density);
		$sth_representation_update_density->execute($rep_child_objs,$rep_density_objs,$rep_density_ends,$rep_density_end_ids,$rep_density_all_ends,$rep_density_all_end_ids,$update_rep_entry,$rep_id) or die $dbh->errstr;
		$sth_representation_update_density->finish;
		undef $sth_representation_update_density;

		my $sql=<<SQL;
delete from representation_art where rep_id=?
SQL
#		print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$sql=[$sql][$rep_id]\n| if(DEBUG);
		my $sth_del = $dbh->prepare($sql) or die $dbh->errstr;
		$sth_del->execute($rep_id) or die $dbh->errstr;
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
		$sth_representation_update_density->finish;
		undef $sth_representation_update_density;
	}

	my $sql=<<SQL;
insert into representation_art (rep_id,art_id,art_hist_serial) values (?,?,?)
SQL
	my $sth_ins = $dbh->prepare($sql) or die $dbh->errstr;
#	print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$sql=[$sql]\n| if(DEBUG);

print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Time::HiRes::tv_interval($t0)." s\n" if(DEBUG);
$t0 = [&Time::HiRes::gettimeofday()] if(DEBUG);

	my @bounds;
	my $bu_volume;
	my $bu_cube_volume;

#	my $tempdir = &File::Temp::tempdir( CLEANUP=>1 );
	my $tempdir = File::Spec->catdir($FindBin::Bin,'..','htdocs','art_file');


	my @FILES;
	my $sth = $dbh->prepare(qq|select art_name,art_ext from history_art_file where art_id=? and hist_serial=?|) or die $dbh->errstr;
	my $sth_data = $dbh->prepare(qq|select art_data from history_art_file where art_id=? and hist_serial=?|) or die $dbh->errstr;

	foreach my $art_key (keys(%ART_IDS)){
		my($art_id,$art_hist_serial) = split(/\t/,$art_key);

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

		my $file = File::Spec->catfile($tempdir,qq|$art_id$art_ext|);

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
	}
	undef $sth;
	undef $sth_data;
	undef $sth_ins;

print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Time::HiRes::tv_interval($t0)." s\n" if(DEBUG);
$t0 = [&Time::HiRes::gettimeofday()] if(DEBUG);

	unless($calcVolume){
		$callback->(qq|Calculation volume (SQL)|) if(defined $callback);
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

		if(scalar @FILES > 0){
			my $prop = &obj2deci::getProperties(\@FILES);
			&obj2deci::objDeleteAll();

			@bounds = map {$_+=0;} @{$prop->{bounds}};
			$bu_volume = &Truncated($prop->{volume} / 1000);
			$bu_cube_volume = &Truncated((($bounds[1]-$bounds[0])*($bounds[3]-$bounds[2])*($bounds[5]-$bounds[4]))/1000);

#			print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\@bounds=[|,join(",",@bounds),qq|]\n| if(DEBUG);
#			print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$bu_volume=[$bu_volume]\n| if(DEBUG);
#			print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.qq|:update_representation_density():\$bu_cube_volume=[$bu_cube_volume]\n| if(DEBUG);

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
		}

	}

	$callback->(qq|Configuration calculation|) if(defined $callback);

	my $sth_upd = $dbh->prepare(qq|update representation set mca_id=get_mca_id(rep_id) where rep_id=?|) or die $dbh->errstr;
	$sth_upd->execute($rep_id) or die $dbh->errstr;
	$sth_upd->finish;
	undef $sth_upd;

	$callback->(undef) if(defined $callback);

#	&File::Path::rmtree($tempdir,0) or die if(-d $tempdir);

print &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__.':'.&Time::HiRes::tv_interval($t0)." s\n" if(DEBUG);
$t0 = [&Time::HiRes::gettimeofday()] if(DEBUG);

}

sub Truncated {
	my $v = shift;
	return undef unless(defined $v);
	my $rate = 10000;
	return int($v * $rate + 0.5) / $rate;
}

1;
