package BITS::ReCalc;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use Time::HiRes;
use Cwd;
use Clone;
use Encode;

use constant {
	DEBUG => 1
};

use Data::Dumper;
$Data::Dumper::Indent = 1;
$Data::Dumper::Sortkeys = 1;

my $JSONXS;# = JSON::XS->new->utf8->indent(0)->canonical(1);
my $JSONXS_Extensions ;# = JSON::XS->new->utf8->indent(1)->canonical(1);
BEGIN{
	$JSONXS = JSON::XS->new->utf8->indent(0)->canonical(1);#->relaxed(0);
	$JSONXS_Extensions  = JSON::XS->new->utf8->indent(1)->canonical(1)->relaxed(1);
};

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
	if($@){
		say STDERR __FILE__.':'.__LINE__.':'.$@ ;
		my($package, $file, $line, $subname, $hasargs, $wantarray, $evaltext, $is_require) = caller();
		say STDERR $package.':'.$line;
	}

	return $json_str;
}

sub encodeExtensionsJSON {
	my $json = shift;
	return &encodeJSON($json,1);
}

sub _print_time {
	my $line = shift;
	$line = __LINE__ unless(defined $line);
	if(DEBUG){
		my($epocsec, $microsec) = &Time::HiRes::gettimeofday();
		my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($epocsec);
		print STDERR sprintf("%s:%s:%4d:%04d/%02d/%02d %02d:%02d:%02d.%d\n",&Cwd::abs_path(__FILE__),__PACKAGE__,$line,$year+1900,$mon+1,$mday,$hour,$min,$sec,$microsec);
	}
}
sub _print {
	my $str = shift;
	my $line = shift;
	if(DEBUG){
		$str = '' unless(defined $str && length $str);
		if(ref $str eq 'HASH' || ref $str eq 'ARRAY'){
			$str = &encodeJSON($str,1);
		}elsif(ref $str ne ''){
			$str = &Data::Dumper::Dumper($str);
		}else{
			$str = &encodeUTF8($str);
		}
		$line = __LINE__ unless(defined $line);
		print STDERR sprintf("%s:%s:%4d:%s\n",&Cwd::abs_path(__FILE__),__PACKAGE__,$line,$str);
	}
}

sub _getParentTreeNode {
	my %arg = @_;
	my $dbh   = $arg{'dbh'};
	my $sth = $arg{'sth'};
	my $hash = $arg{'hash'};
	my $enabled_cdi_ids = $arg{'enabled_cdi_ids'};
	my $cdi_id = $arg{'cdi_id'};
	my $bul_id = $arg{'bul_id'};

#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":[$cdi_id][$bul_id][$hash]\n" if(DEBUG);
#exit;

	return unless(exists $enabled_cdi_ids->{$cdi_id}->{$bul_id});

	my $cdi_pids;
	my $cdi_pid;
	my $column_number = 0;
	$sth->execute($cdi_id,$bul_id) or die $dbh->errstr;
#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":\t",$sth->rows(),"\n" if(DEBUG);
	$column_number = 0;
	$sth->bind_col(++$column_number, \$cdi_pid,   undef);
	while($sth->fetch){
		next unless(defined $cdi_pid);
		next unless(exists $enabled_cdi_ids->{$cdi_pid}->{$bul_id});
		next if(exists $hash->{$cdi_pid} && exists $hash->{$cdi_pid}->{$bul_id});
		next if($cdi_id == $cdi_pid);
#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":\t[$cdi_id][$cdi_pid]\n"if(DEBUG);
		$hash->{$cdi_pid}->{$bul_id} = undef;
		$cdi_pids->{$cdi_pid} = undef;
	}
	$sth->finish;

	if(defined $cdi_pids){
#print STDERR &Cwd::abs_path(__FILE__).':'.__PACKAGE__.':'.__LINE__,":\t[$cdi_id][$cdi_pids]\n"if(DEBUG);
		foreach my $cdi_pid (keys(%$cdi_pids)){
			&_getParentTreeNode(dbh=>$dbh,sth=>$sth,hash=>$hash,enabled_cdi_ids=>$enabled_cdi_ids,cdi_id=>$cdi_pid,bul_id=>$bul_id);
		}
	}
}

sub _get_cdi_ids {
	my %arg = @_;
	my $dbh   = $arg{'dbh'};
	my $ci_id = $arg{'ci_id'};
	my $cb_id = $arg{'cb_id'};
	my $md_id = $arg{'md_id'};
	my $mv_id = $arg{'mv_id'};
	my $mr_id = $arg{'mr_id'};

	my $cdi_names;
	if(defined $arg{'cdi_names'}){
		if(ref $arg{'cdi_names'} eq 'ARRAY'){
			$cdi_names = $arg{'cdi_names'};
		}else{
			$cdi_names = &decodeJSON($arg{'cdi_names'});
		}
	}
	return undef unless(defined $cdi_names);

	my $all_but_cids;
	my $cdi_id;
	my $bul_id;
	my $but_cids;
	my $enabled_cdi_ids;
	my $cdi_ids;
	my $sql;
	my $sth;
	my $column_number;


#	&_print($all_but_cids,__LINE__);
	&_print_time(__LINE__);


#	&_print($enabled_cdi_ids,__LINE__);
	&_print_time(__LINE__);

	$sql =<<SQL;
select
 but.cdi_id,
 but.bul_id,
 bti.but_cids,
 bti.but_pids
from
 buildup_tree as but
left join (
 select * from buildup_tree_info
) as bti on
   bti.md_id=but.md_id and
   bti.mv_id=but.mv_id and
   bti.mr_id=but.mr_id and
   bti.bul_id=but.bul_id and
   bti.cdi_id=but.cdi_id
left join (
 select * from concept_data_info
) as cdi on
   cdi.ci_id=but.ci_id and
   cdi.cdi_id=but.cdi_id
where
 but.md_id=$md_id AND
 but.mv_id=$mv_id AND
 but.mr_id=$mr_id AND
 cdi.cdi_name IN (%s)
SQL
#	&_print($sql,__LINE__);

	my $cdi_pids;
	$sth = $dbh->prepare(sprintf($sql,join(',',map {'?'} @$cdi_names))) or die $dbh->errstr;

	$sth->execute(@$cdi_names) or die $dbh->errstr;
	if($sth->rows()>0){
		my $cdi_id;
		my $bul_id;
		my $but_cids;
		my $but_pids;
		$column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_id,   undef);
		$sth->bind_col(++$column_number, \$bul_id,   undef);
		$sth->bind_col(++$column_number, \$but_cids,   undef);
		$sth->bind_col(++$column_number, \$but_pids,   undef);
		while($sth->fetch){
			next unless(defined $cdi_id && defined $bul_id);

			$cdi_ids->{$cdi_id}->{$bul_id} = undef;
			if(defined $but_cids){
				my $cdi_cids;
				eval{$cdi_cids = &JSON::XS::decode_json($but_cids);};
				if(defined $cdi_cids && ref $cdi_cids eq 'ARRAY'){
					$cdi_ids->{$_}->{$bul_id} = undef for(@$cdi_cids);
				}
			}
			if(defined $but_pids){
				my $cdi_pids;
				eval{$cdi_pids = &JSON::XS::decode_json($but_pids);};
				if(defined $cdi_pids && ref $cdi_pids eq 'ARRAY'){
					$cdi_ids->{$_}->{$bul_id} = undef for(@$cdi_pids);
				}
			}
		}
	}
	$sth->finish;
	undef $sth;


	&_print_time(__LINE__);

	&_print_time(__LINE__);

	return $cdi_ids;
}

sub check {
	my %arg = @_;
	my $dbh     = $arg{'dbh'};
	my $ci_id   = $arg{'ci_id'};
	my $cb_id   = $arg{'cb_id'};
#	my $bul_id  = $arg{'bul_id'};
	my $md_id   = $arg{'md_id'};
	my $mv_id   = $arg{'mv_id'};
	my $mr_id   = $arg{'mr_id'};

	&_print_time(__LINE__);

	my $cdi_names;
	unless(exists $arg{'cdi_names'} && defined $arg{'cdi_names'} && ref $arg{'cdi_names'} eq 'ARRAY'){
		my $sth = $dbh->prepare(qq|select cdi_name from view_buildup_tree where md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND cdi_pid IS NULL|) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		my $cdi_name;
		$sth->bind_col(1, \$cdi_name,   undef);
		while($sth->fetch){
			push(@$cdi_names,$cdi_name) if(defined $cdi_name);
		}
		$sth->finish;
		undef $sth;
	}else{
		$cdi_names = $arg{'cdi_names'};
	}
#	&_print($cdi_names,__LINE__);

	my $cdi_ids_hash;
	my $enabled_cdi_ids;
	delete $arg{'cdi_ids'} if(exists $arg{'cdi_ids'});
	$cdi_ids_hash = &_get_cdi_ids(
		dbh=>$dbh,
		ci_id=>$ci_id,
		cb_id=>$cb_id,
		md_id=>$md_id,
		mv_id=>$mv_id,
		mr_id=>$mr_id,
		cdi_names=>$cdi_names
	);
#	&_print($cdi_ids_hash,__LINE__);
#	&_print($enabled_cdi_ids,__LINE__);
	push(@{$arg{'cdi_ids'}},keys(%$cdi_ids_hash)) if(defined $cdi_ids_hash);

	&_print_time(__LINE__);

	return undef unless(defined $arg{'cdi_ids'});

	&_print(scalar @{$arg{'cdi_ids'}},__LINE__);
#	die __LINE__;

	my $cdi_ids;

	my $sql_cmm = sprintf(qq|
select
 cdi_id,
 bul_id,
 COALESCE(EXTRACT(EPOCH FROM cm_modified),0) as cm_modified_epoch
from
 concept_art_map_modified
where 
 md_id=$md_id AND
 mv_id=$mv_id AND
 mr_id=$mr_id AND
 cdi_id in (%s)
|,join(",",sort {$a<=>$b} @{$arg{'cdi_ids'}}));
#	&_print($sql_cmm,__LINE__);
	my %CMM_HASH;
	my $sth_cmm = $dbh->prepare($sql_cmm) or die $dbh->errstr;
	$sth_cmm->execute() or die $dbh->errstr;
	if($sth_cmm->rows()>0){
		my $cdi_id;
		my $bul_id;
		my $cm_modified_epoch;
		$sth_cmm->bind_col(1, \$cdi_id,   undef);
		$sth_cmm->bind_col(2, \$bul_id,   undef);
		$sth_cmm->bind_col(3, \$cm_modified_epoch,   undef);
		while($sth_cmm->fetch){
			next unless(defined $cdi_id && defined $bul_id && defined $cm_modified_epoch);
			$CMM_HASH{$cdi_id}->{$bul_id} = {cm_modified_epoch => $cm_modified_epoch - 0};
		}
	}
	$sth_cmm->finish;
	undef $sth_cmm;
	undef $sql_cmm;

	my $sql_rep = qq|
select cdi_id,bul_id,EXTRACT(EPOCH FROM rep_entry) as rep_entry_epoch,rep_delcause from representation where (ci_id,cb_id,md_id,mv_id,mr_id,bul_id,cdi_id) in 
(
 select
  ci_id,cb_id,md_id,mv_id,max(mr_id) as mr_id,bul_id,cdi_id
 from
  representation
 where
  md_id=$md_id AND
  mv_id=$mv_id AND
  mr_id<=$mr_id
 group by
  ci_id,cb_id,md_id,mv_id,bul_id,cdi_id
)
|;
#	&_print($sql_rep,__LINE__);
	my %REP_HASH;
	my $sth_rep = $dbh->prepare($sql_rep) or die $dbh->errstr;
	$sth_rep->execute() or die $dbh->errstr;
	if($sth_rep->rows()>0){
		my $cdi_id;
		my $bul_id;
		my $rep_entry_epoch;
		my $rep_delcause;
		$sth_rep->bind_col(1, \$cdi_id,   undef);
		$sth_rep->bind_col(2, \$bul_id,   undef);
		$sth_rep->bind_col(3, \$rep_entry_epoch,   undef);
		$sth_rep->bind_col(4, \$rep_delcause,   undef);
		while($sth_rep->fetch){
			next unless(defined $cdi_id && defined $bul_id && defined $rep_entry_epoch);
			$REP_HASH{$cdi_id}->{$bul_id} = {rep_entry_epoch => $rep_entry_epoch - 0, rep_delcause => $rep_delcause};
		}
	}
	$sth_rep->finish;
	undef $sth_rep;
	undef $sql_rep;

	foreach my $cdi_id (keys(%CMM_HASH)){
		foreach my $bul_id (keys(%{$CMM_HASH{$cdi_id}})){
			if($CMM_HASH{$cdi_id}->{$bul_id}->{'cm_modified_epoch'}>0){
				if(exists $REP_HASH{$cdi_id} && exists $REP_HASH{$cdi_id} && exists $REP_HASH{$cdi_id}->{$bul_id} && defined $REP_HASH{$cdi_id}->{$bul_id}){
					$cdi_ids->{$cdi_id}->{$bul_id} = 'update:'.__LINE__ if($CMM_HASH{$cdi_id}->{$bul_id}->{'cm_modified_epoch'}>$REP_HASH{$cdi_id}->{$bul_id}->{'rep_entry_epoch'} || defined $REP_HASH{$cdi_id}->{$bul_id}->{'rep_delcause'});
				}else{
					$cdi_ids->{$cdi_id}->{$bul_id} = 'insert:'.__LINE__;
				}
			}else{
				if(exists $REP_HASH{$cdi_id} && exists $REP_HASH{$cdi_id} && exists $REP_HASH{$cdi_id}->{$bul_id} && defined $REP_HASH{$cdi_id}->{$bul_id}){
					$cdi_ids->{$cdi_id}->{$bul_id} = 'delete:'.__LINE__ unless(defined $REP_HASH{$cdi_id}->{$bul_id}->{'rep_delcause'});
				}
			}
		}
	}
#&_print($cdi_ids,__LINE__);
	return $cdi_ids;
}

sub get_max_map_info {
	my %arg = @_;
	my $dbh     = $arg{'dbh'};
	my $ci_id   = $arg{'ci_id'};
	my $cb_id   = $arg{'cb_id'};
	my $bul_id  = $arg{'bul_id'};
	my $md_id   = $arg{'md_id'};
	my $mv_id   = $arg{'mv_id'};
	my $mr_id   = $arg{'mr_id'};
	my $cdi_id   = $arg{'cdi_id'};
	my $but_cids = $arg{'but_cids'};

	my $cm_max_num_cdi;
	my $cm_max_entry_cdi;
#	return wantarray ? ($cm_max_num_cdi,$cm_max_entry_cdi) : [$cm_max_num_cdi,$cm_max_entry_cdi];

	my $sth_cmm = $dbh->prepare(qq|select EXTRACT(EPOCH FROM cm_modified) from concept_art_map_modified where ci_id=? AND cb_id=? AND md_id=? AND mv_id=? AND mr_id=? AND bul_id=? AND cdi_id=?|) or die $dbh->errstr;
	$sth_cmm->execute($ci_id,$cb_id,$md_id,$mv_id,$mr_id,$bul_id,$cdi_id) or die $dbh->errstr;
	$sth_cmm->bind_col(1, \$cm_max_entry_cdi, undef);
	$sth_cmm->fetch;
	$sth_cmm->finish;
	undef $sth_cmm;
	return wantarray ? ($cm_max_num_cdi,$cm_max_entry_cdi) : [$cm_max_num_cdi,$cm_max_entry_cdi];


	unless(defined $but_cids){
		my $sth = $dbh->prepare(qq|select but_cids from buildup_tree_info where but_delcause is null AND md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND ci_id=$ci_id AND cb_id=$cb_id AND bul_id=$bul_id AND cdi_id=$cdi_id|) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$sth->bind_col(1, \$but_cids, undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;
	}
	my $but_cids_arr = &JSON::XS::decode_json($but_cids) if(defined $but_cids);
	push(@$but_cids_arr,$cdi_id);

	my $sql_cm_max_num_cdi = sprintf(qq|
select cm_use,count(*),EXTRACT(EPOCH FROM max(cm_entry)) from concept_art_map where cm_use and cm_delcause is null and (ci_id,cb_id,md_id,mv_id,mr_id,cdi_id) in (
  select ci_id,cb_id,md_id,mv_id,max(mr_id) as mr_id,cdi_id from concept_art_map where ci_id=$ci_id AND cb_id=$cb_id AND md_id=$md_id AND mv_id=$mv_id AND mr_id<=$mr_id AND cdi_id in (%s) group by ci_id,cb_id,md_id,mv_id,cdi_id
) group by cm_use
|,join(',',@$but_cids_arr));

	undef $but_cids_arr;

	my $sth_cm_max_num_cdi = $dbh->prepare($sql_cm_max_num_cdi) or die $dbh->errstr;
	$sth_cm_max_num_cdi->execute() or die $dbh->errstr;
	my $column_number = 0;
	my $cm_use;
	my $cm_count;
	my $cm_entry;
	$sth_cm_max_num_cdi->bind_col(++$column_number, \$cm_use, undef);
	$sth_cm_max_num_cdi->bind_col(++$column_number, \$cm_count, undef);
	$sth_cm_max_num_cdi->bind_col(++$column_number, \$cm_entry, undef);
	while($sth_cm_max_num_cdi->fetch){
		if($cm_use){
			$cm_max_num_cdi = 0 unless(defined $cm_max_num_cdi);
			$cm_max_num_cdi += $cm_count;
		}
		$cm_max_entry_cdi = $cm_entry if(defined $cm_max_entry_cdi && $cm_max_entry_cdi < $cm_entry || !defined $cm_max_entry_cdi)
	}
	$sth_cm_max_num_cdi->finish;
	undef $sth_cm_max_num_cdi;
	undef $sql_cm_max_num_cdi;

	return wantarray ? ($cm_max_num_cdi,$cm_max_entry_cdi) : [$cm_max_num_cdi,$cm_max_entry_cdi];
}

1;
