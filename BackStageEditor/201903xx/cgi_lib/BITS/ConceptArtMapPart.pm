package BITS::ConceptArtMapPart;

=pod
use Exporter;

@ISA = (Exporter);
@EXPORT_OK = qw(extract find);
@EXPORT_FAIL = qw(move_file);
=cut

use strict;
use warnings;
use feature ':5.10';

#our $is_subclass_cdi_name = qr/^(.+)\-(L|R|P|S[1-9][0-9]{0,1})$/;

#our $is_subclass_cdi_name = qr/^(.+)\-([LRPFN])$/;
#our $is_subclass_cdi_name = qr/^(.+)\-([LRFNOPQSTUVWX])$/;
our $is_subclass_cdi_name_old = qr/^(.+)\-([LRFNOPQSTUVWX])$/;
our $is_subclass_cdi_name = qr/^(.+?)([ABCDEFGHNOPQSTUVWX]*)\-([LRU])$/;

our $is_subclass_abbr_LR = qr/^[LR]$/;

#our $is_subclass_abbr_LR_other = qr/^[PFN]$/;
#our $is_subclass_abbr_LR_other = qr/^[FNOPQSTUVWX]$/;
our $is_subclass_abbr_LR_other_old = qr/^[FNOPQSTUVWX]$/;
our $is_subclass_abbr_LR_other = qr/^[U]$/;

#our $is_subclass_abbr_isa = qr/^[LRFN]$/;
#our $is_subclass_abbr_isa = qr/^[LRFNO]$/;
our $is_subclass_abbr_isa_old = qr/^[LRFNO]$/;
our $is_subclass_abbr_isa    = qr/^[ABCDEFGHNO]$/;

our $is_subclass_abbr_partof = qr/^[PQSTUVWX]$/;

our $subclass_format_old = '%s-%s';
our $subclass_format = '%s%s-%s';

sub get_cdi_name {
	my %FORM = @_;

	my $dbh = $FORM{'dbh'};
	my $LOG = $FORM{'LOG'};

	my $cdi_name;
	$cdi_name = $FORM{'cdi_name'} if(exists $FORM{'cdi_name'} && defined $FORM{'cdi_name'} && length $FORM{'cdi_name'});

	my $bcp_id = 0;
	$bcp_id = $FORM{'bcp_id'} - 0 if(exists $FORM{'bcp_id'} && defined $FORM{'bcp_id'} && length $FORM{'bcp_id'});
#	&cgi_lib::common::message($cp_id, $LOG) if(defined $LOG);

	my $bcl_id = 0;
	$bcl_id = $FORM{'bcl_id'} - 0 if(exists $FORM{'bcl_id'} && defined $FORM{'bcl_id'} && length $FORM{'bcl_id'});
#	&cgi_lib::common::message($cl_id, $LOG) if(defined $LOG);

	return undef unless(defined $cdi_name);

	if($bcp_id || $bcp_id){
		$cdi_name = $1 if($cdi_name =~ /$is_subclass_cdi_name/);
		my $bcp_abbr = '';
		my $bcl_abbr = '';
		if($bcp_id){
			my $sth_bcp_abbr_sel = $dbh->prepare(qq|SELECT bcp_abbr FROM buildup_concept_part WHERE md_id=? AND mv_id=? AND mr_id=? AND bcp_id=?|) or die $dbh->errstr;
			$sth_bcp_abbr_sel->execute($FORM{'md_id'},$FORM{'mv_id'},$FORM{'mr_id'},$bcp_id) or die $dbh->errstr;
			if($sth_bcp_abbr_sel->rows()>0){
				my $column_number = 0;
				$sth_bcp_abbr_sel->bind_col(++$column_number, \$bcp_abbr, undef);
				$sth_bcp_abbr_sel->fetch;
			}
			$sth_bcp_abbr_sel->finish;
			undef $sth_bcp_abbr_sel;
		}
		if($bcl_id){
			my $sth_bcl_abbr_sel = $dbh->prepare(qq|SELECT bcl_abbr FROM buildup_concept_laterality WHERE md_id=? AND mv_id=? AND mr_id=? AND bcl_id=?|) or die $dbh->errstr;
			$sth_bcl_abbr_sel->execute($FORM{'md_id'},$FORM{'mv_id'},$FORM{'mr_id'},$bcl_id) or die $dbh->errstr;
			if($sth_bcl_abbr_sel->rows()>0){
				my $column_number = 0;
				$sth_bcl_abbr_sel->bind_col(++$column_number, \$bcl_abbr, undef);
				$sth_bcl_abbr_sel->fetch;
			}
			$sth_bcl_abbr_sel->finish;
			undef $sth_bcl_abbr_sel;
		}
		$cdi_name = sprintf($subclass_format,$cdi_name,$bcp_abbr,$bcl_abbr);
	}
	$cdi_name = undef unless($cdi_name =~ /$is_subclass_cdi_name/);
	return $cdi_name;
}

sub get_cdi_pname {
	my %FORM = @_;
	my $cdi_name;
	$cdi_name = $FORM{'cdi_name'} if(exists $FORM{'cdi_name'} && defined $FORM{'cdi_name'} && length $FORM{'cdi_name'});
	return undef unless(defined $cdi_name);
	my $cdi_pname;
	$cdi_pname = $1 if($cdi_name =~ /$is_subclass_cdi_name/);
	return $cdi_pname;
}

sub create_subclass {
	my %FORM = @_;

	my $dbh=$FORM{'dbh'};
	my $LOG=$FORM{'LOG'};

	&cgi_lib::common::message(\%FORM, $LOG) if(defined $LOG);

	my $ci_id=$FORM{'ci_id'};
	my $cb_id=$FORM{'cb_id'};
	my $md_id=$FORM{'md_id'};
	my $mv_id=$FORM{'mv_id'};
	my $mr_id=$FORM{'mr_id'};

	my $cdi_name = &get_cdi_name(%FORM);
#	&cgi_lib::common::message($cdi_name, $LOG) if(defined $LOG);
	return undef unless(defined $cdi_name);
	return undef unless($cdi_name =~ /$is_subclass_cdi_name/);
	my $cdi_pname = $1;
	my $bcp_abbr = $2;
	my $bcl_abbr = $3;

	$cdi_pname = $FORM{'cdi_pname'} if(exists $FORM{'cdi_pname'} && defined $FORM{'cdi_pname'} && length $FORM{'cdi_pname'});
	my $cdi_sname;
	$cdi_sname = $FORM{'cdi_sname'} if(exists $FORM{'cdi_sname'} && defined $FORM{'cdi_sname'} && length $FORM{'cdi_sname'});


#	my $cmp_id;
	my $bcp_id;
	my $bcp_title;
	my $bcl_id;
	my $bcl_title;

	my $exists_check_trio = $FORM{'exists_check_trio'} // 1;

	my $cdi_id;
	my $cdi_name_e;
	my $column_number;
	my $sth;

	my $cdi_pid;
	my $cdi_pname_e;
	my $seg_id;
	my $phy_id;

	my $cdi_sid;
	my $cdi_sname_e;

=pod
	$sth = $dbh->prepare(qq|
SELECT
 cdi.cdi_id,
 COALESCE(cd.cd_name,bd.cd_name,cdi.cdi_name_e),
 COALESCE(cd.seg_id,bd.seg_id,0),
 COALESCE(cd.phy_id,bd.phy_id,1)
FROM
 concept_data_info AS cdi

LEFT JOIN (
 SELECT * FROM concept_data WHERE ci_id=$ci_id AND cb_id=$cb_id
) AS cd ON
 cd.ci_id=cdi.ci_id AND
 cd.cdi_id=cdi.cdi_id

LEFT JOIN (
 SELECT * FROM buildup_data WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id
) AS bd ON
 bd.ci_id=cdi.ci_id AND
 bd.cdi_id=cdi.cdi_id

WHERE
 cdi.ci_id=$ci_id AND
 cdi_name=?
|) or die $dbh->errstr;
=cut
	$sth = $dbh->prepare(qq|
SELECT
 cdi.cdi_id,
 COALESCE(cd.cd_name,cdi.cdi_name_e),
 COALESCE(cd.seg_id,0),
 COALESCE(cd.phy_id,1)
FROM
 concept_data_info AS cdi

LEFT JOIN (
 SELECT * FROM concept_data WHERE ci_id=$ci_id AND cb_id=$cb_id
) AS cd ON
 cd.ci_id=cdi.ci_id AND
 cd.cdi_id=cdi.cdi_id

WHERE
 cdi.ci_id=$ci_id AND
 cdi_name=?
|) or die $dbh->errstr;

	$sth->execute($cdi_pname) or die $dbh->errstr;
	if($sth->rows()>0){
		$column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_pid, undef);
		$sth->bind_col(++$column_number, \$cdi_pname_e, undef);
		$sth->bind_col(++$column_number, \$seg_id, undef);
		$sth->bind_col(++$column_number, \$phy_id, undef);
		$sth->fetch;
	}
	$sth->finish;
	undef $sth;

	return undef unless(defined $cdi_pid && defined $cdi_pname_e);

	if(defined $cdi_sname && length $cdi_sname){
		$sth = $dbh->prepare(qq|
SELECT
 cdi.cdi_id,
 COALESCE(cd.cd_name,cdi.cdi_name_e)
FROM
 concept_data_info AS cdi

LEFT JOIN (
 SELECT * FROM concept_data WHERE ci_id=$ci_id AND cb_id=$cb_id
) AS cd ON
 cd.ci_id=cdi.ci_id AND
 cd.cdi_id=cdi.cdi_id

WHERE
 cdi.ci_id=$ci_id AND
 cdi_name=?
|) or die $dbh->errstr;

		$sth->execute($cdi_sname) or die $dbh->errstr;
		if($sth->rows()>0){
			$column_number = 0;
			$sth->bind_col(++$column_number, \$cdi_sid, undef);
			$sth->bind_col(++$column_number, \$cdi_sname_e, undef);
			$sth->fetch;
		}
		$sth->finish;
		undef $sth;
	}

=pod
	#LRの時にtrioテーブルに親が登録されているか確認
	if($exists_check_trio && defined $cmp_abbr && length $cmp_abbr && $cmp_abbr =~ /$is_subclass_abbr_LR/){
		my $cdi_lid;
		my $cdi_rid;
		my $cdi_lname;
		my $cdi_rname;
		my $sql_ctt_sel = qq|
SELECT
 ctt.cdi_lid,
 ctt.cdi_rid,
 lcdi.cdi_name,
 rcdi.cdi_name
FROM
 buildup_tree_trio AS ctt
LEFT JOIN (
 select * from concept_data_info
) AS lcdi ON lcdi.ci_id=ctt.ci_id AND lcdi.cdi_id=ctt.cdi_lid
LEFT JOIN (
 select * from concept_data_info
) AS rcdi ON rcdi.ci_id=ctt.ci_id AND rcdi.cdi_id=ctt.cdi_rid
WHERE
 ctt.md_id=$md_id AND ctt.mv_id=$mv_id AND ctt.mr_id=$mr_id AND ctt.cdi_pid=?
|;
		my $sth_ctt_sel = $dbh->prepare($sql_ctt_sel) or die $dbh->errstr;
		$sth_ctt_sel->execute($cdi_pid) or die $dbh->errstr;
		if($sth_ctt_sel->rows()){
			$column_number = 0;
			$sth_ctt_sel->bind_col(++$column_number, \$cdi_lid, undef);
			$sth_ctt_sel->bind_col(++$column_number, \$cdi_rid, undef);
			$sth_ctt_sel->bind_col(++$column_number, \$cdi_lname, undef);
			$sth_ctt_sel->bind_col(++$column_number, \$cdi_rname, undef);
			$sth_ctt_sel->fetch;
		}
		$sth_ctt_sel->finish;
		undef $sth_ctt_sel;

		#LRの時にtrioテーブルに自分以外の組み合わせで既に登録されている場合
		my $msg_fmt = &cgi_lib::common::decodeUTF8("[ %s ]を使用して下さい");
		if($cmp_abbr eq 'L' && defined $cdi_lname && $cdi_lname ne $cdi_name){
			die sprintf($msg_fmt,$cdi_lname);
		}
		elsif($cmp_abbr eq 'R' && defined $cdi_rname && $cdi_rname ne $cdi_name){
			die sprintf($msg_fmt,$cdi_rname);
		}
	}
=cut

	#inferでの親を検索（ここから）
#	&cgi_lib::common::message($cmp_abbr, $LOG);
	my $infer_cdi_pids;
	my $infer_bul_id;
	my $temp_f_potids;
	my $temp_bul_id;
	if(defined $bcp_abbr && length $bcp_abbr){
		if($bcp_abbr =~ /$is_subclass_abbr_isa/){
			$temp_bul_id = 3;
#			$infer_bul_id = 4;	#20190131 変更
		}elsif($bcp_abbr =~ /$is_subclass_abbr_partof/){
			$temp_bul_id = 4;
			$infer_bul_id = 3;	#20190131 変更
		}
#		&cgi_lib::common::message($infer_bul_id, $LOG);
=pod
		if(defined $infer_bul_id){
			my $partof_pids;
			my $sth_ct_sel = $dbh->prepare("SELECT cdi_pid,f_potids FROM buildup_tree WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND cdi_id=$cdi_pid AND bul_id=$infer_bul_id AND cdi_pid IS NOT NULL") or die $dbh->errstr;
			$sth_ct_sel->execute() or die $dbh->errstr;
			if($sth_ct_sel->rows()>0){
				$column_number = 0;
				my $relation_pid;
				my $relation_f_potids;
				$sth_ct_sel->bind_col(++$column_number, \$relation_pid, undef);
				$sth_ct_sel->bind_col(++$column_number, \$relation_f_potids, undef);
				while($sth_ct_sel->fetch){
					if($cmp_abbr =~ /$is_subclass_abbr_LR/){
						$partof_pids->{$relation_pid} = undef;
					}elsif($cmp_abbr =~ /$is_subclass_abbr_LR_other/){
						if(defined $relation_f_potids){
							foreach my $relation_crt_id (split(/;/,$relation_f_potids)){
								$infer_cdi_pids->{$relation_pid}->{$relation_crt_id} = undef;
							}
						}else{
							$infer_cdi_pids->{$relation_pid} = undef;
						}
					}
				}
			}
			$sth_ct_sel->finish;
			undef $sth_ct_sel;

			if(defined $partof_pids && ref $partof_pids eq 'HASH' && scalar keys(%$partof_pids)){
				my $sth_ctt_sel = $dbh->prepare(sprintf("SELECT cdi_lid,cdi_rid FROM buildup_tree_trio WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND cdi_pid IN (%s)",join(',',keys(%$partof_pids)))) or die $dbh->errstr;
				$sth_ctt_sel->execute() or die $dbh->errstr;
				if($sth_ctt_sel->rows()>0){
					$column_number = 0;
					my $cdi_lid;
					my $cdi_rid;
					$sth_ctt_sel->bind_col(++$column_number, \$cdi_lid, undef);
					$sth_ctt_sel->bind_col(++$column_number, \$cdi_rid, undef);
					while($sth_ctt_sel->fetch){
						if($cmp_abbr eq 'L'){
							$infer_cdi_pids->{$cdi_lid} = {};
						}elsif($cmp_abbr eq 'R'){
							$infer_cdi_pids->{$cdi_rid} = {};
						}
					}
				}
				$sth_ctt_sel->finish;
				undef $sth_ctt_sel;

				if(defined $infer_cdi_pids && ref $infer_cdi_pids eq 'HASH' && scalar keys(%$infer_cdi_pids)){
					my $sth_ct_sel = $dbh->prepare(sprintf("SELECT cdi_id,f_potids FROM buildup_tree WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND bul_id=$infer_bul_id AND cdi_id IN (%s)",join(',',keys(%$infer_cdi_pids)))) or die $dbh->errstr;
					$sth_ct_sel->execute() or die $dbh->errstr;
					if($sth_ct_sel->rows()>0){
						$column_number = 0;
						my $relation_pid;
						my $relation_f_potids;
						$sth_ct_sel->bind_col(++$column_number, \$relation_pid, undef);
						$sth_ct_sel->bind_col(++$column_number, \$relation_f_potids, undef);
						while($sth_ct_sel->fetch){
							if(defined $relation_f_potids){
								foreach my $relation_f_potid (split(/;/,$relation_f_potids)){
									$infer_cdi_pids->{$relation_pid}->{$relation_f_potid} = undef;
								}
							}
						}
					}
					$sth_ct_sel->finish;
					undef $sth_ct_sel;
				}
			}
		}
=cut
		if(defined $infer_bul_id && $infer_bul_id == 3){
			my $sth_ct_sel = $dbh->prepare("SELECT cdi_pid FROM buildup_tree WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=$cdi_pid AND bul_id=$infer_bul_id") or die $dbh->errstr;
			$sth_ct_sel->execute() or die $dbh->errstr;
			if($sth_ct_sel->rows()>0){
				$column_number = 0;
				my $relation_pid;
				$sth_ct_sel->bind_col(++$column_number, \$relation_pid, undef);
				while($sth_ct_sel->fetch){
					$infer_cdi_pids->{$relation_pid} = undef;
				}
			}
			$sth_ct_sel->finish;
			undef $sth_ct_sel;
		}
		if(defined $temp_bul_id && $temp_bul_id == 4){
			my $partof_pids;
#			my $sth_ct_sel = $dbh->prepare("SELECT f_potids FROM buildup_tree WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND cdi_id=$cdi_pid AND bul_id=$temp_bul_id GROUP BY f_potids") or die $dbh->errstr;	#20190131 変更
			my $sth_ct_sel = $dbh->prepare("SELECT f_potid FROM fma_partof_type WHERE f_potname='regional_part_of'") or die $dbh->errstr;
			$sth_ct_sel->execute() or die $dbh->errstr;
			if($sth_ct_sel->rows()>0){
				$column_number = 0;
				my $relation_f_potids;
				$sth_ct_sel->bind_col(++$column_number, \$relation_f_potids, undef);
				while($sth_ct_sel->fetch){
					foreach my $relation_f_potid (split(/;/,$relation_f_potids)){
						$temp_f_potids->{$relation_f_potid} = undef;
					}
				}
			}
			$sth_ct_sel->finish;
			undef $sth_ct_sel;
#			&cgi_lib::common::message($temp_f_potids, $LOG);
		}
	}
	else{
		$temp_bul_id = 3;
	}
	if(defined $cdi_sid && defined $temp_bul_id && $temp_bul_id == 3){
		$infer_bul_id = 4;
	}
	if(defined $cdi_sid && defined $infer_bul_id){
		$infer_cdi_pids = {};

		if($infer_bul_id == 4){
			my $f_potid;
			my $sth_crt_sel = $dbh->prepare("SELECT f_potid FROM fma_partof_type WHERE crt_name='regional_part_of'") or die $dbh->errstr;
			$sth_crt_sel->execute() or die $dbh->errstr;
			if($sth_crt_sel->rows()>0){
				$column_number = 0;
				$sth_crt_sel->bind_col(++$column_number, \$f_potid, undef);
				$sth_crt_sel->fetch;
			}
			$sth_crt_sel->finish;
			undef $sth_crt_sel;
			$infer_cdi_pids->{$cdi_sid}->{$f_potid} = undef;
		}
		else{
			$infer_cdi_pids->{$cdi_sid} = undef;
		}
	}



#	&cgi_lib::common::message($infer_cdi_pids, $LOG);
	#inferでの親を検索（ここまで）
=pod
	my $cmp_title;
#	my $temp_bul_id;
#	my $temp_f_potid;
	if(defined $cmp_abbr && length $cmp_abbr){
		my $sth_cmp_abbr_sel = $dbh->prepare(qq|select cmp_id,COALESCE(cmp_prefix,cmp_title) from concept_art_map_part where md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND cmp_abbr=?|) or die $dbh->errstr;
		$sth_cmp_abbr_sel->execute($cmp_abbr) or die $dbh->errstr;
		if($sth_cmp_abbr_sel->rows()>0){
			$column_number = 0;
			$sth_cmp_abbr_sel->bind_col(++$column_number, \$cmp_id, undef);
			$sth_cmp_abbr_sel->bind_col(++$column_number, \$cmp_title, undef);
			$sth_cmp_abbr_sel->fetch;
		}
		$sth_cmp_abbr_sel->finish;
		undef $sth_cmp_abbr_sel;
	}
=cut
	if(defined $bcp_abbr && length $bcp_abbr){
		my $sth_bcp_abbr_sel = $dbh->prepare(qq|SELECT bcp_id,COALESCE(bcp_prefix,bcp_title) FROM buildup_concept_part WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND bcp_abbr=?|) or die $dbh->errstr;
		$sth_bcp_abbr_sel->execute($bcp_abbr) or die $dbh->errstr;
#		&cgi_lib::common::message($sth_cmp_abbr_sel->rows(), $LOG);
		if($sth_bcp_abbr_sel->rows()>0){
			$column_number = 0;
			$sth_bcp_abbr_sel->bind_col(++$column_number, \$bcp_id, undef);
			$sth_bcp_abbr_sel->bind_col(++$column_number, \$bcp_title, undef);
			$sth_bcp_abbr_sel->fetch;
		}
		$sth_bcp_abbr_sel->finish;
		undef $sth_bcp_abbr_sel;
	}
	else{
		$bcp_id = 0;
		$bcp_title = '';
	}
	if(defined $bcl_abbr && length $bcl_abbr){
		my $sth_bcl_abbr_sel = $dbh->prepare(qq|SELECT bcl_id,COALESCE(bcl_prefix,bcl_title) FROM buildup_concept_laterality WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND bcl_abbr=?|) or die $dbh->errstr;
		$sth_bcl_abbr_sel->execute($bcl_abbr) or die $dbh->errstr;
#		&cgi_lib::common::message($sth_cmp_abbr_sel->rows(), $LOG);
		if($sth_bcl_abbr_sel->rows()>0){
			$column_number = 0;
			$sth_bcl_abbr_sel->bind_col(++$column_number, \$bcl_id, undef);
			$sth_bcl_abbr_sel->bind_col(++$column_number, \$bcl_title, undef);
			$sth_bcl_abbr_sel->fetch;
		}
		$sth_bcl_abbr_sel->finish;
		undef $sth_bcl_abbr_sel;
	}
	else{
		die sprintf('unknown concept_laterality [%s]',$cdi_name);
		$bcl_id = 0;
		$bcl_title = '';
	}



	my $cd_name = lc($cdi_pname_e);
=pod
	if(defined $cmp_title && length $cmp_title){
		$cd_name = sprintf('%s %s',$cmp_title,$cd_name);
	}
	elsif($cmp_abbr eq 'P'){
		$cd_name = sprintf('Proper %s',$cd_name);
	}
	elsif($cmp_abbr eq 'L'){
		$cd_name = sprintf('Left %s',$cd_name);
	}
	elsif($cmp_abbr eq 'R'){
		$cd_name = sprintf('Right %s',$cd_name);
	}
=cut
	if(defined $bcp_title && length $bcp_title){
		$cd_name = sprintf('%s %s',$bcp_title,$cd_name);
	}
	if(defined $bcl_title && length $bcl_title){
		$cd_name = sprintf('%s %s',$bcl_title,$cd_name);
	}

	$sth = $dbh->prepare("SELECT cdi.cdi_id,COALESCE(cd_name,cdi_name_e) FROM concept_data_info as cdi LEFT JOIN (SELECT * FROM concept_data WHERE ci_id=$ci_id AND cb_id=$cb_id) AS cd ON cd.cdi_id=cdi.cdi_id WHERE cdi.ci_id=$ci_id AND cdi_name=?") or die $dbh->errstr;
	$sth->execute($cdi_name) or die $dbh->errstr;
	if($sth->rows()>0){
		$column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_id, undef);
		$sth->bind_col(++$column_number, \$cdi_name_e, undef);
		$sth->fetch;
	}
	$sth->finish;
	undef $sth;

	unless(defined $cdi_id){

		my $sth_cdi_sel = $dbh->prepare("SELECT COALESCE(MAX(cdi_id),0)+1 FROM concept_data_info WHERE ci_id=$ci_id") or die $dbh->errstr;
		$sth_cdi_sel->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth_cdi_sel->bind_col(++$column_number, \$cdi_id, undef);
		$sth_cdi_sel->fetch;
		$sth_cdi_sel->finish;
		undef $sth_cdi_sel;

		my $sth_cdi_ins = $dbh->prepare("INSERT INTO concept_data_info (ci_id,cdi_id,cdi_name,cdi_name_e,cdi_entry,cdi_openid,is_user_data) VALUES ($ci_id,$cdi_id,?,?,now(),'system'::text,true)") or die $dbh->errstr;
		$sth_cdi_ins->execute($cdi_name,$cd_name) or die $dbh->errstr;
		$sth_cdi_ins->finish;
		undef $sth_cdi_ins;
	}

	return undef unless(defined $cdi_id);

#	unless(defined $cdi_name_e && length $cdi_name_e){
	{
		my $sth_cdi_upd = $dbh->prepare("UPDATE concept_data_info SET cdi_name_e=? WHERE ci_id=$ci_id AND cdi_id=?") or die $dbh->errstr;
		$sth_cdi_upd->execute($cd_name,$cdi_id) or die $dbh->errstr;
		$sth_cdi_upd->finish;
		undef $sth_cdi_upd;
		$cdi_name_e = $cd_name;
	}

	my $sth_cd_sel = $dbh->prepare("SELECT cdi_id FROM buildup_data WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=$cdi_id") or die $dbh->errstr;
	$sth_cd_sel->execute() or die $dbh->errstr;
	my $cd_rows = $sth_cd_sel->rows();
	$sth_cd_sel->finish;
	undef $sth_cd_sel;
	unless($cd_rows>0){
		my $sth_cd_ins = $dbh->prepare("INSERT INTO buildup_data (md_id,mv_id,mr_id,ci_id,cb_id,cdi_id,cd_name,cd_entry,cd_openid,seg_id,phy_id,bcp_id,bcl_id,cdi_pid,cdi_sid) VALUES ($md_id,$mv_id,$mr_id,$ci_id,$cb_id,$cdi_id,?,now(),'system'::text,?,?,?,?,?,?)") or die $dbh->errstr;
		$sth_cd_ins->execute($cd_name,$seg_id,$phy_id,$bcp_id,$bcl_id,$cdi_pid,$cdi_sid) or die $dbh->errstr;
		$sth_cd_ins->finish;
		undef $sth_cd_ins;
	}
	{
		$seg_id = 0 unless(defined $seg_id);
		$phy_id = 1 unless(defined $phy_id);
		my $sth_cd_upd = $dbh->prepare("UPDATE buildup_data SET cd_name=?,seg_id=?,phy_id=?,bcp_id=?,bcl_id=?,cdi_pid=?,cdi_sid=? WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND cdi_id=?") or die $dbh->errstr;
		$sth_cd_upd->execute($cd_name,$seg_id,$phy_id,$bcp_id,$bcl_id,$cdi_pid,$cdi_sid,$cdi_id) or die $dbh->errstr;
		$sth_cd_upd->finish;
		undef $sth_cd_upd;
	}
=pod
	#LRの時にtrioテーブルに自分を登録（ここから）
	if($exists_check_trio && defined $cmp_abbr && length $cmp_abbr && $cmp_abbr =~ /$is_subclass_abbr_LR/){
		my $sql_ctt_sel = "SELECT cdi_pid FROM buildup_tree_trio WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND " . ($cmp_abbr eq 'L' ? "cdi_lid" : "cdi_rid") . "=?";
		my $sth_ctt_sel = $dbh->prepare($sql_ctt_sel) or die $dbh->errstr;
		$sth_ctt_sel->execute($cdi_id) or die $dbh->errstr;
		my $ctt_rows = $sth_ctt_sel->rows();
		$sth_ctt_sel->finish;
		undef $sth_ctt_sel;
		unless($ctt_rows>0){
			#反対側の情報を取得
			my $opposite_side_cdi_name = sprintf('%s-%s',$cdi_pname,($cmp_abbr eq 'L' ? 'R' : 'L'));
#			&cgi_lib::common::message($opposite_side_cdi_name, $LOG);
			my $opposite_side_cdi_id = &create_subclass(
				dbh   => $dbh,
				LOG   => $LOG,
				ci_id => $ci_id,
				cb_id => $cb_id,
				md_id => $md_id,
				mv_id => $mv_id,
				mr_id => $mr_id,
				cmp_id=> 0,
				cdi_name=> $opposite_side_cdi_name,
				exists_check_trio=> 0,
			);
#			&cgi_lib::common::message($opposite_side_cdi_id, $LOG);
			return undef unless(defined $opposite_side_cdi_id);

			my $sth_ctt_ins = $dbh->prepare("INSERT INTO buildup_tree_trio (md_id,mv_id,mr_id,ci_id,cb_id,cdi_pid,cdi_lid,cdi_rid) VALUES ($md_id,$mv_id,$mr_id,$ci_id,$cb_id,$cdi_pid,?,?)") or die $dbh->errstr;
			if($cmp_abbr eq 'L'){
				$sth_ctt_ins->execute($cdi_id,$opposite_side_cdi_id) or die $dbh->errstr;
			}else{
				$sth_ctt_ins->execute($opposite_side_cdi_id,$cdi_id) or die $dbh->errstr;
			}
#			&cgi_lib::common::message($sth_ctt_ins->rows(), $LOG);
			$sth_ctt_ins->finish;
			undef $sth_ctt_ins;
		}
	}
	#trioテーブルに自分を登録（ここまで）
=cut
	my $temp_buildup_tree_infos;

	if(defined $temp_bul_id){
		my $sth_cd_sel = $dbh->prepare("SELECT cdi_id FROM buildup_tree WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND cdi_id=$cdi_id AND cdi_pid=$cdi_pid AND bul_id=$temp_bul_id") or die $dbh->errstr;
		$sth_cd_sel->execute() or die $dbh->errstr;
		my $cd_rows = $sth_cd_sel->rows();
		$sth_cd_sel->finish;
		undef $sth_cd_sel;

		unless($cd_rows>0){
			my $temp_f_potid;
			$temp_f_potid = join(';',map {$_-0} sort {$a <=> $b} keys(%$temp_f_potids)) if(defined $temp_f_potids && ref $temp_f_potids eq 'HASH' && scalar keys(%$temp_f_potids));
			my $sth_cd_ins = $dbh->prepare("INSERT INTO buildup_tree (md_id,mv_id,mr_id,ci_id,cb_id,cdi_id,cdi_pid,bul_id,f_potids) VALUES ($md_id,$mv_id,$mr_id,$ci_id,$cb_id,$cdi_id,$cdi_pid,$temp_bul_id,?)") or die $dbh->errstr;
			$sth_cd_ins->execute($temp_f_potid) or die $dbh->errstr;
			$sth_cd_ins->finish;
			undef $sth_cd_ins;
		}

		push(@$temp_buildup_tree_infos,{
			cdi_pids => [$cdi_pid],
			bul_id   => $temp_bul_id
		});
	}

	if(defined $infer_bul_id && defined $infer_cdi_pids && ref $infer_cdi_pids eq 'HASH' && scalar keys(%$infer_cdi_pids)){
		my $sth_cd_sel = $dbh->prepare("SELECT cdi_id FROM buildup_tree WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND cdi_id=$cdi_id AND cdi_pid=? AND bul_id=$infer_bul_id") or die $dbh->errstr;
		my $sth_cd_ins = $dbh->prepare("INSERT INTO buildup_tree (md_id,mv_id,mr_id,ci_id,cb_id,cdi_id,cdi_pid,bul_id,f_potids) VALUES ($md_id,$mv_id,$mr_id,$ci_id,$cb_id,$cdi_id,?,$infer_bul_id,?)") or die $dbh->errstr;
		foreach my $relation_pid (keys(%$infer_cdi_pids)){
			$sth_cd_sel->execute($relation_pid) or die $dbh->errstr;
			my $cd_rows = $sth_cd_sel->rows();
			$sth_cd_sel->finish;

			unless($cd_rows>0){
				my $relation_f_potid;
				$relation_f_potid = join(';',map {$_-0} sort {$a <=> $b} keys(%{$infer_cdi_pids->{$relation_pid}}))  if(defined $infer_cdi_pids->{$relation_pid} && ref $infer_cdi_pids->{$relation_pid} eq 'HASH' && scalar keys(%{$infer_cdi_pids->{$relation_pid}}));
				$sth_cd_ins->execute($relation_pid,$relation_f_potid) or die $dbh->errstr;
				$sth_cd_ins->finish;
			}
		}

		push(@$temp_buildup_tree_infos,{
			cdi_pids => [keys(%$infer_cdi_pids)],
			bul_id   => $infer_bul_id
		});

		undef $sth_cd_sel;
		undef $sth_cd_ins;
	}


	if(defined $temp_buildup_tree_infos && ref $temp_buildup_tree_infos eq 'ARRAY' && scalar @$temp_buildup_tree_infos){
		my $cdi_pids;
		foreach my $temp_buildup_tree_info (@$temp_buildup_tree_infos){
			foreach my $cdi_pid (@{$temp_buildup_tree_info->{'cdi_pids'}}){
				$cdi_pids->{$cdi_pid} = undef;
			}
		}
		if(defined $cdi_pids && ref $cdi_pids eq 'HASH' && scalar keys(%$cdi_pids)){
			push(@$temp_buildup_tree_infos,{
				cdi_pids => [keys(%$cdi_pids)],
				bul_id  => 0
			});
		}
	}


	if(defined $temp_buildup_tree_infos && ref $temp_buildup_tree_infos eq 'ARRAY' && scalar @$temp_buildup_tree_infos){

#		my $sth_cti_sel = $dbh->prepare("SELECT cdi_id FROM buildup_tree_info WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=$cdi_id AND bul_id=$temp_bul_id2") or die $dbh->errstr;
#		my $sth_cti_sel = $dbh->prepare("SELECT but_cids,but_depth,but_pids FROM buildup_tree_info WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=? AND bul_id=?") or die $dbh->errstr;
		my $sth_cti_sel = $dbh->prepare("SELECT but_cids FROM buildup_tree_info WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=? AND bul_id=?") or die $dbh->errstr;
		my $sth_cti_ins = $dbh->prepare("INSERT INTO buildup_tree_info (but_depth,but_pnum,but_pids,md_id,mv_id,mr_id,ci_id,cb_id,cdi_id,bul_id) VALUES (?,?,?,$md_id,$mv_id,$mr_id,$ci_id,$cb_id,?,?)") or die $dbh->errstr;
		my $sth_cti_upd = $dbh->prepare("UPDATE buildup_tree_info SET but_cnum=?,but_cids=? WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=? AND bul_id=?") or die $dbh->errstr;

		foreach my $temp_buildup_tree_info (@$temp_buildup_tree_infos){

#			&cgi_lib::common::message($temp_buildup_tree_info, $LOG) if(defined $LOG);

			my $temp_bul_id2 = $temp_buildup_tree_info->{'bul_id'};

			$sth_cti_sel->execute($cdi_id,$temp_bul_id2) or die $dbh->errstr;
			my $cti_rows = $sth_cti_sel->rows();
			$sth_cti_sel->finish;

			next if($cti_rows>0);

			my $cdi_pids = $temp_buildup_tree_info->{'cdi_pids'};
			my $sth_cti_sels = $dbh->prepare(sprintf("SELECT but_depth,but_pids FROM buildup_tree_info WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND ci_id=$ci_id AND cb_id=$cb_id AND cdi_id in (%s) AND bul_id=%d",join(',',@$cdi_pids),$temp_bul_id2)) or die $dbh->errstr;

			my $max_but_depth = 0;
			my %hash_but_pids = map {$_=>undef} @$cdi_pids;

			my $but_cnum;
			my $but_cids;
			my $but_depth;
			my $but_pnum;
			my $but_pids;
			$sth_cti_sels->execute() or die $dbh->errstr;
			$column_number = 0;
			$sth_cti_sels->bind_col(++$column_number, \$but_depth, undef);
			$sth_cti_sels->bind_col(++$column_number, \$but_pids, undef);
			while($sth_cti_sels->fetch){
				$but_depth += 1;
				$max_but_depth = $but_depth if($max_but_depth<$but_depth);

				$but_pids = &cgi_lib::common::decodeJSON($but_pids) if(defined $but_pids);
				$but_pids = [] unless(defined $but_pids);

				$hash_but_pids{$_} = undef  for(@$but_pids);

			}
			$sth_cti_sels->finish;
			undef $sth_cti_sels;

			$but_pids = [map {$_-0} keys(%hash_but_pids)];
			$but_pnum = scalar @$but_pids;
			$but_pids = &cgi_lib::common::encodeJSON([sort {$a<=>$b} @$but_pids]);

			$sth_cti_ins->execute($max_but_depth,$but_pnum,$but_pids,$cdi_id,$temp_bul_id2) or die $dbh->errstr;
			$sth_cti_ins->finish;

			$but_pids = [sort {$a<=>$b} map {$_-0} keys(%hash_but_pids)];

			foreach my $but_pid (@$but_pids){
				$sth_cti_sel->execute($but_pid,$temp_bul_id2) or die $dbh->errstr;
				my $rows_cti_sel = $sth_cti_sel->rows();
				if($rows_cti_sel>0){
					$column_number = 0;
					$sth_cti_sel->bind_col(++$column_number, \$but_cids, undef);
					$sth_cti_sel->fetch;
				}
				$sth_cti_sel->finish;
				next unless($rows_cti_sel>0);

				$but_cids = &cgi_lib::common::decodeJSON($but_cids) if(defined $but_cids);
				$but_cids = [] unless(defined $but_cids);
				push(@$but_cids,$cdi_id-0);
				my %hash_but_cids = map {$_=>undef} @$but_cids;
				$but_cids = [map {$_-0} keys(%hash_but_cids)];
				$but_cnum = scalar @$but_cids;
				$but_cids = &cgi_lib::common::encodeJSON([sort {$a<=>$b} @$but_cids]);

				$sth_cti_upd->execute($but_cnum,$but_cids,$but_pid,$temp_bul_id2) or die $dbh->errstr;
				$sth_cti_upd->finish;
			}
		}
		undef $sth_cti_sel;
		undef $sth_cti_ins;
		undef $sth_cti_upd;
	}
	return $cdi_id;
}

sub clear_subclass_tree {
	my %FORM = @_;

	my $dbh = $FORM{'dbh'};
	my $LOG = $FORM{'LOG'};

#	&cgi_lib::common::dumper(\%FORM, $LOG) if(defined $LOG);

	my $ci_id=$FORM{'ci_id'};
	my $cb_id=$FORM{'cb_id'};
	my $md_id=$FORM{'md_id'};
	my $mv_id=$FORM{'mv_id'};
	my $mr_id=$FORM{'mr_id'};

#	my $cdi_name;
#	$cdi_name = $FORM{'cdi_name'} if(exists $FORM{'cdi_name'} && defined $FORM{'cdi_name'} && length $FORM{'cdi_name'});

	my $cdi_id;
	$cdi_id = $FORM{'cdi_id'} if(exists $FORM{'cdi_id'} && defined $FORM{'cdi_id'} && length $FORM{'cdi_id'});

	my $column_number;
	my $sth;

	unless(defined $cdi_id){
		my $cdi_name = &get_cdi_name(%FORM);
		return undef unless(defined $cdi_name);
		return undef unless($cdi_name =~ /$is_subclass_cdi_name/);

		$sth = $dbh->prepare("SELECT cdi_id FROM concept_data_info WHERE ci_id=$ci_id AND cdi_name=?") or die $dbh->errstr;
		$sth->execute($cdi_name) or die $dbh->errstr;
#		&cgi_lib::common::message($sth->rows(), $LOG) if(defined $LOG);
		if($sth->rows()>0){
			$column_number = 0;
			$sth->bind_col(++$column_number, \$cdi_id, undef);
			$sth->fetch;
		}
		$sth->finish;
		undef $sth;
	}
	return unless(defined $cdi_id);

	my %hash_cdi_pids;
	$sth = $dbh->prepare("SELECT cti_pids FROM concept_tree_info WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=?") or die $dbh->errstr;
	$sth->execute($cdi_id) or die $dbh->errstr;
	if($sth->rows()>0){
		$column_number = 0;
		my $cti_pids;
		$sth->bind_col(++$column_number, \$cti_pids, undef);
		while($sth->fetch){
			$cti_pids = &cgi_lib::common::decodeJSON($cti_pids) if(defined $cti_pids);
			$cti_pids = [] unless(defined $cti_pids && ref $cti_pids eq 'ARRAY');
			$hash_cdi_pids{$_} = undef for(@$cti_pids);
		}
	}
	$sth->finish;
	undef $sth;

	$sth = $dbh->prepare("SELECT cdi_pid FROM concept_tree WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=$cdi_id AND cdi_pid IS NOT NULL GROUP BY cdi_pid") or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	if($sth->rows()>0){
		my $cdi_pid;
		$column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_pid, undef);
		while($sth->fetch){
			$hash_cdi_pids{$cdi_pid} = undef if(defined $cdi_pid);
		}
	}
	$sth->finish;
	undef $sth;

	if(scalar keys(%hash_cdi_pids)){
		my $sth_cti_upd = $dbh->prepare("UPDATE concept_tree_info SET cti_cnum=?,cti_cids=? WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=? AND crl_id=?") or die $dbh->errstr;
		my $sth_cti_sel = $dbh->prepare(sprintf("SELECT cdi_id,crl_id,cti_cids FROM concept_tree_info WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id IN (%s)",join(',',map {'?'} keys(%hash_cdi_pids)))) or die $dbh->errstr;
		$sth_cti_sel->execute(keys(%hash_cdi_pids)) or die $dbh->errstr;
		if($sth_cti_sel->rows()>0){
			my $cdi_pid;
			my $crl_id;
			my $cti_cids;
			my $cti_cnum;
			$column_number = 0;
			$sth_cti_sel->bind_col(++$column_number, \$cdi_pid, undef);
			$sth_cti_sel->bind_col(++$column_number, \$crl_id, undef);
			$sth_cti_sel->bind_col(++$column_number, \$cti_cids, undef);
			while($sth_cti_sel->fetch){

				$cti_cids = &cgi_lib::common::decodeJSON($cti_cids) if(defined $cti_cids);
				$cti_cids = [] unless(defined $cti_cids && ref $cti_cids eq 'ARRAY');
				my %cti_cids_hash = map {$_=>undef} @$cti_cids;
				next unless(exists $cti_cids_hash{$cdi_id});
				delete $cti_cids_hash{$cdi_id};
				$cti_cids = [map {$_-0} keys(%cti_cids_hash)];
				$cti_cnum = scalar @$cti_cids;
				if($cti_cnum>0){
					$cti_cids = &cgi_lib::common::encodeJSON([sort {$a<=>$b} @$cti_cids]);
				}else{
					$cti_cids = undef;
				}
				$sth_cti_upd->execute($cti_cnum,$cti_cids,$cdi_pid,$crl_id) or die $dbh->errstr;
				$sth_cti_upd->finish;
			}
		}
		$sth_cti_sel->finish;
		undef $sth_cti_sel;
		undef $sth_cti_upd;

		$dbh->do(qq|DELETE FROM concept_tree_info WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=$cdi_id|) or die $dbh->errstr;
		$dbh->do(qq|DELETE FROM concept_tree WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=$cdi_id|) or die $dbh->errstr;
	}

#	&cgi_lib::common::message('', $LOG) if(defined $LOG);

	%hash_cdi_pids = ();
	$sth = $dbh->prepare("SELECT but_pids FROM buildup_tree_info WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND cdi_id=?") or die $dbh->errstr;
	$sth->execute($cdi_id) or die $dbh->errstr;
	if($sth->rows()>0){
		$column_number = 0;
		my $but_pids;
		$sth->bind_col(++$column_number, \$but_pids, undef);
		while($sth->fetch){
			$but_pids = &cgi_lib::common::decodeJSON($but_pids) if(defined $but_pids);
			$but_pids = [] unless(defined $but_pids && ref $but_pids eq 'ARRAY');
			$hash_cdi_pids{$_} = undef for(@$but_pids);
		}
	}
	$sth->finish;
	undef $sth;

#	&cgi_lib::common::message('', $LOG) if(defined $LOG);

	$sth = $dbh->prepare("SELECT cdi_pid FROM buildup_tree WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND cdi_id=$cdi_id AND cdi_pid IS NOT NULL GROUP BY cdi_pid") or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	if($sth->rows()>0){
		my $cdi_pid;
		$column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_pid, undef);
		while($sth->fetch){
			$hash_cdi_pids{$cdi_pid} = undef if(defined $cdi_pid);
		}
	}
	$sth->finish;
	undef $sth;

#	&cgi_lib::common::message('', $LOG) if(defined $LOG);

	if(scalar keys(%hash_cdi_pids)){
		my $sth_cti_upd = $dbh->prepare("UPDATE buildup_tree_info SET but_cnum=?,but_cids=? WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND cdi_id=? AND bul_id=?") or die $dbh->errstr;
		my $sth_cti_sel = $dbh->prepare(sprintf("SELECT cdi_id,bul_id,but_cids FROM buildup_tree_info WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND cdi_id IN (%s)",join(',',map {'?'} keys(%hash_cdi_pids)))) or die $dbh->errstr;
		$sth_cti_sel->execute(keys(%hash_cdi_pids)) or die $dbh->errstr;
		if($sth_cti_sel->rows()>0){
			&cgi_lib::common::message($sth_cti_sel->rows(), $LOG) if(defined $LOG);
			my $rows = $sth_cti_sel->rows();
			my $cdi_pid;
			my $bul_id;
			my $but_cids;
			my $but_cnum;
			$column_number = 0;
			$sth_cti_sel->bind_col(++$column_number, \$cdi_pid, undef);
			$sth_cti_sel->bind_col(++$column_number, \$bul_id, undef);
			$sth_cti_sel->bind_col(++$column_number, \$but_cids, undef);
			while($sth_cti_sel->fetch){

				print $LOG sprintf("[%3d]\r",$rows--) if(defined $LOG);
#		&cgi_lib::common::message('', $LOG) if(defined $LOG);

				$but_cids = &cgi_lib::common::decodeJSON($but_cids) if(defined $but_cids);
				$but_cids = [] unless(defined $but_cids && ref $but_cids eq 'ARRAY');
				my %but_cids_hash = map {$_=>undef} @$but_cids;
				next unless(exists $but_cids_hash{$cdi_id});
#		&cgi_lib::common::message('', $LOG) if(defined $LOG);
				delete $but_cids_hash{$cdi_id};
				$but_cids = [map {$_-0} keys(%but_cids_hash)];
				$but_cnum = scalar @$but_cids;
				if($but_cnum>0){
					$but_cids = &cgi_lib::common::encodeJSON([sort {$a<=>$b} @$but_cids]);
				}else{
					$but_cids = undef;
				}
				$sth_cti_upd->execute($but_cnum,$but_cids,$cdi_pid,$bul_id) or die $dbh->errstr;
				$sth_cti_upd->finish;
#		&cgi_lib::common::message('', $LOG) if(defined $LOG);
			}
			say $LOG '' if(defined $LOG);
		}
		$sth_cti_sel->finish;
		undef $sth_cti_sel;
		undef $sth_cti_upd;

#		&cgi_lib::common::message('', $LOG) if(defined $LOG);

		$dbh->do(qq|DELETE FROM buildup_tree_info WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND cdi_id=$cdi_id|) or die $dbh->errstr;
		$dbh->do(qq|DELETE FROM buildup_tree WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND cdi_id=$cdi_id|) or die $dbh->errstr;
	}

#	&cgi_lib::common::message('', $LOG) if(defined $LOG);
}

sub all_list_subclass {
	my %FORM = @_;

	my $dbh = $FORM{'dbh'};
	my $LOG = $FORM{'LOG'};

#	&cgi_lib::common::dumper(\%FORM, $LOG) if(defined $LOG);

	my $ci_id=$FORM{'ci_id'};
	my $cb_id=$FORM{'cb_id'};
	my $md_id=$FORM{'md_id'};
	my $mv_id=$FORM{'mv_id'};
	my $mr_id=$FORM{'mr_id'};

	my $ALL_LIST;

	my $sth = $dbh->prepare(qq|
SELECT * FROM (
SELECT
 cdi.cdi_id AS id,
 cdi.cdi_name AS name,
 cti.cti_depth AS depth
FROM
 concept_tree_info AS cti
LEFT JOIN (
 SELECT * FROM concept_data_info
) AS cdi ON cdi.ci_id=cti.ci_id AND cdi.cdi_id=cti.cdi_id

WHERE
 cdi.is_user_data AND
 cti.crl_id=0 AND
 cti.ci_id=$ci_id AND
 cti.cb_id=$cb_id

UNION

SELECT
 cdi.cdi_id AS id,
 cdi.cdi_name AS name,
 bti.but_depth AS depth
FROM
 buildup_tree_info AS bti
LEFT JOIN (
 SELECT * FROM concept_data_info
) AS cdi ON cdi.ci_id=bti.ci_id AND cdi.cdi_id=bti.cdi_id

WHERE
 cdi.is_user_data AND
 bti.bul_id=0 AND
 bti.md_id=$md_id AND
 bti.mv_id=$mv_id AND
 bti.md_id=$md_id
) AS a

ORDER BY
 depth,
 name
|) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
#	&cgi_lib::common::message($sth->rows(), $LOG);
	if($sth->rows()>0){
		my $column_number = 0;
		my $cdi_id;
		my $cdi_name;
		my $cti_depth;
		$sth->bind_col(++$column_number, \$cdi_id, undef);
		$sth->bind_col(++$column_number, \$cdi_name, undef);
		$sth->bind_col(++$column_number, \$cti_depth, undef);
		while($sth->fetch){
			push(@$ALL_LIST, {
				cdi_id => $cdi_id - 0,
				cdi_name => $cdi_name,
				depth => $cti_depth - 0,
			});
		}
	}
	$sth->finish;
	undef $sth;

	return $ALL_LIST;
}

sub all_use_list_depth {
	my %FORM = @_;

	my $dbh = $FORM{'dbh'};
	my $LOG = $FORM{'LOG'};

#	&cgi_lib::common::dumper(\%FORM, $LOG) if(defined $LOG);

	my $ci_id=$FORM{'ci_id'};
	my $cb_id=$FORM{'cb_id'};
	my $md_id=$FORM{'md_id'};
	my $mv_id=$FORM{'mv_id'};
	my $mr_id=$FORM{'mr_id'};

	my $ALL_LIST;

	my %CDI_NAME2DEPTH;
	my $sth = $dbh->prepare(qq|
SELECT
 cdi.cdi_name,
 but_depth
FROM
 buildup_tree_info AS bti
LEFT JOIN (
 SELECT * FROM concept_data_info
) AS cdi ON cdi.ci_id=bti.ci_id AND cdi.cdi_id=bti.cdi_id
WHERE
 bti.md_id=$md_id AND
 bti.mv_id=$mv_id AND
 bti.mr_id=$mr_id AND
 bti.bul_id=0
|) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
#	&cgi_lib::common::message($sth->rows(), $LOG);
	if($sth->rows()>0){
		my $column_number = 0;
		my $cdi_name;
		my $but_depth;
		$sth->bind_col(++$column_number, \$cdi_name, undef);
		$sth->bind_col(++$column_number, \$but_depth, undef);
		while($sth->fetch){
			$CDI_NAME2DEPTH{$cdi_name} = $but_depth - 0;
		}
	}
	$sth->finish;
	undef $sth;

	return %CDI_NAME2DEPTH;
}

sub all_use_list_subclass {
	my %FORM = @_;

	my $dbh = $FORM{'dbh'};
	my $LOG = $FORM{'LOG'};

#	&cgi_lib::common::dumper(\%FORM, $LOG) if(defined $LOG);

	my $ci_id=$FORM{'ci_id'};
	my $cb_id=$FORM{'cb_id'};
	my $md_id=$FORM{'md_id'};
	my $mv_id=$FORM{'mv_id'};
	my $mr_id=$FORM{'mr_id'};

	my $ALL_LIST;

	my %CDI_NAME2DEPTH = &all_use_list_depth(%FORM);

	my $sth = $dbh->prepare(qq|
SELECT
 cdi.cdi_id,
 cdi.cdi_name
FROM
 concept_data_info AS cdi
LEFT JOIN (
 SELECT * FROM concept_art_map WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id
) AS cm ON cm.ci_id=cdi.ci_id AND cm.cdi_id=cdi.cdi_id
LEFT JOIN (
 SELECT * FROM concept_data WHERE ci_id=$ci_id AND cb_id=$cb_id
) AS cd ON cd.ci_id=cdi.ci_id AND cd.cdi_id=cdi.cdi_id

LEFT JOIN (
 SELECT * FROM buildup_data WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id
) AS bd ON bd.ci_id=cdi.ci_id AND bd.cdi_id=cdi.cdi_id

WHERE
 cdi.is_user_data AND
 cm.cm_use AND
 cm.cm_delcause IS NULL AND
 cdi.ci_id=$ci_id AND
 COALESCE(cd.cdi_id,bd.cdi_id) IS NOT NULL
GROUP BY
 cdi.cdi_id,
 cdi.cdi_name
ORDER BY
 cdi.cdi_name
|) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
#	&cgi_lib::common::message($sth->rows(), $LOG);
	if($sth->rows()>0){
		my $column_number = 0;
		my $cdi_id;
		my $cdi_name;
		my $cdi_pname;
		$sth->bind_col(++$column_number, \$cdi_id, undef);
		$sth->bind_col(++$column_number, \$cdi_name, undef);
		while($sth->fetch){
			my $cdi_pname = $cdi_name;
			$cdi_pname = $1 if($cdi_pname =~ /$is_subclass_cdi_name/);

			push(@$ALL_LIST, {
				cdi_id => $cdi_id - 0,
				cdi_name => $cdi_name,
				but_depth => $CDI_NAME2DEPTH{$cdi_pname} || 0
			});

		}
	}
	$sth->finish;
	undef $sth;

	$ALL_LIST = [sort {$a->{'but_depth'} <=> $b->{'but_depth'}} @$ALL_LIST] if(defined $ALL_LIST && ref $ALL_LIST eq 'ARRAY' && scalar @$ALL_LIST);

	return $ALL_LIST;
}

sub all_clear_subclass_tree {
	my %FORM = @_;

	my $dbh = $FORM{'dbh'};
	my $LOG = $FORM{'LOG'};

	my $ALL_LIST = &all_list_subclass(%FORM);
	if(defined $ALL_LIST && ref $ALL_LIST eq 'ARRAY' && scalar @$ALL_LIST){
		&clear_subclass_tree(%FORM, cdi_id=>$_->{'cdi_id'}, cdi_name=>$_->{'cdi_name'} ) for(@$ALL_LIST);
	}
}

sub all_create_subclass {
	my %FORM = @_;

	my $dbh = $FORM{'dbh'};
	my $LOG = $FORM{'LOG'};

	my $ALL_LIST = &all_use_list_subclass(%FORM);
	if(defined $ALL_LIST && ref $ALL_LIST eq 'ARRAY' && scalar @$ALL_LIST){
		&create_subclass(%FORM, cdi_name=>$_->{'cdi_name'} ) for(@$ALL_LIST);
	}
}

sub all_recreate_subclass {
	my %FORM = @_;

	my $dbh = $FORM{'dbh'};
	my $LOG = $FORM{'LOG'};

	if(exists $FORM{'cdi_name'} && defined  $FORM{'cdi_name'} && length  $FORM{'cdi_name'}){
		&cgi_lib::common::message($FORM{'cdi_name'}, $LOG) if(defined $LOG);
		&clear_subclass_tree(%FORM);
		my $ALL_USE_LIST = &all_use_list_subclass(%FORM);
		if(defined $ALL_USE_LIST && ref $ALL_USE_LIST eq 'ARRAY' && scalar @$ALL_USE_LIST){
			my %HASH_ALL_USE_LIST = map { $_->{'cdi_name'} => $_->{'cdi_id'} } @$ALL_USE_LIST;
			if(exists $HASH_ALL_USE_LIST{$FORM{'cdi_name'}}){
#				&cgi_lib::common::message($cdi_id, $LOG) if(defined $LOG);
				my $cdi_id = &create_subclass( %FORM );
				&cgi_lib::common::message($cdi_id, $LOG) if(defined $LOG);
			}
		}
	}
	else{
		my $ALL_LIST = &all_list_subclass(%FORM);
#		&cgi_lib::common::message(defined $ALL_LIST ? ref $ALL_LIST : '', $LOG) if(defined $LOG);
		if(defined $ALL_LIST && ref $ALL_LIST eq 'ARRAY' && scalar @$ALL_LIST){
			my $total = scalar @$ALL_LIST;
#			&cgi_lib::common::message(scalar @$ALL_LIST, $LOG) if(defined $LOG);
			foreach my $data (reverse @$ALL_LIST){
#				&cgi_lib::common::message($data->{'cdi_name'}, $LOG) if(defined $LOG);
				print $LOG sprintf("Clear:[%5d][%s]\n",$total--,$data->{'cdi_name'}) if(defined $LOG);
				&clear_subclass_tree(%FORM, cdi_id=>$data->{'cdi_id'}, cdi_name=>$data->{'cdi_name'} );
			}
			say $LOG '' if(defined $LOG);
		}
		my $ALL_USE_LIST = &all_use_list_subclass(%FORM);
		if(defined $ALL_USE_LIST && ref $ALL_USE_LIST eq 'ARRAY' && scalar @$ALL_USE_LIST){
#			&cgi_lib::common::message(scalar @$ALL_USE_LIST, $LOG) if(defined $LOG);
			my $total = scalar @$ALL_USE_LIST;
			foreach my $data (@$ALL_USE_LIST){
#				&cgi_lib::common::message($data->{'cdi_name'}, $LOG) if(defined $LOG);
				print $LOG sprintf("Create:[%5d][%-12s]\r",$total--,$data->{'cdi_name'}) if(defined $LOG);
				unless(defined &create_subclass( %FORM, cdi_name=>$data->{'cdi_name'} )){
					&cgi_lib::common::message($data->{'cdi_name'}, $LOG) if(defined $LOG);
					die __LINE__;
				}
			}
			say $LOG '' if(defined $LOG);
		}
	}
}

1;
