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


sub get_cdi_name_old{
	my %FORM = @_;

	my $dbh = $FORM{'dbh'};
	my $LOG = $FORM{'LOG'};

	my $cdi_name;
	$cdi_name = $FORM{'cdi_name'} if(exists $FORM{'cdi_name'} && defined $FORM{'cdi_name'} && length $FORM{'cdi_name'});
#	&cgi_lib::common::message($cdi_name, $LOG) if(defined $LOG);

	my $cmp_id = 0;
	$cmp_id = $FORM{'cmp_id'} - 0 if(exists $FORM{'cmp_id'} && defined $FORM{'cmp_id'} && length $FORM{'cmp_id'});
#	&cgi_lib::common::message($cmp_id, $LOG) if(defined $LOG);

	return undef unless(defined $cdi_name);

	if($cmp_id){
		$cdi_name = $1 if($cdi_name =~ /$is_subclass_cdi_name_old/);

		my $cmp_abbr;
		my $sth_cmp_abbr_sel = $dbh->prepare(qq|SELECT cmp_abbr FROM concept_art_map_part WHERE cmp_id=?|) or die $dbh->errstr;
		$sth_cmp_abbr_sel->execute($cmp_id) or die $dbh->errstr;
		if($sth_cmp_abbr_sel->rows()>0){
			my $column_number = 0;
			$sth_cmp_abbr_sel->bind_col(++$column_number, \$cmp_abbr, undef);
			$sth_cmp_abbr_sel->fetch;
		}
		$sth_cmp_abbr_sel->finish;
		undef $sth_cmp_abbr_sel;
		if(defined $cmp_abbr && length $cmp_abbr){
			$cdi_name = sprintf($subclass_format_old,$cdi_name,$cmp_abbr);
		}
	}
	$cdi_name = undef unless($cdi_name =~ /$is_subclass_cdi_name_old/);

	return $cdi_name;
}


sub get_cdi_name{
	my %FORM = @_;

	my $dbh = $FORM{'dbh'};
	my $LOG = $FORM{'LOG'};

	my $cdi_name;
	$cdi_name = $FORM{'cdi_name'} if(exists $FORM{'cdi_name'} && defined $FORM{'cdi_name'} && length $FORM{'cdi_name'});
#	&cgi_lib::common::message($cdi_name, $LOG) if(defined $LOG);

	my $cp_id = 0;
	$cp_id = $FORM{'cp_id'} - 0 if(exists $FORM{'cp_id'} && defined $FORM{'cp_id'} && length $FORM{'cp_id'});
#	&cgi_lib::common::message($cp_id, $LOG) if(defined $LOG);

	my $cl_id = 0;
	$cl_id = $FORM{'cl_id'} - 0 if(exists $FORM{'cl_id'} && defined $FORM{'cl_id'} && length $FORM{'cl_id'});
#	&cgi_lib::common::message($cl_id, $LOG) if(defined $LOG);

	return undef unless(defined $cdi_name);

	if($cp_id || $cl_id){
		$cdi_name = $1 if($cdi_name =~ /$is_subclass_cdi_name/);

		my $column_number = 0;
		my $cp_abbr;
		my $cl_abbr;
		if($cp_id){
			my $sth_cp_abbr_sel = $dbh->prepare(qq|SELECT cp_abbr FROM concept_part WHERE cp_use AND cp_id=?|) or die $dbh->errstr;
			$sth_cp_abbr_sel->execute($cp_id) or die $dbh->errstr;
			if($sth_cp_abbr_sel->rows()>0){
				$column_number = 0;
				$sth_cp_abbr_sel->bind_col(++$column_number, \$cp_abbr, undef);
				$sth_cp_abbr_sel->fetch;
			}
			$sth_cp_abbr_sel->finish;
			undef $sth_cp_abbr_sel;
		}
		if($cl_id){
			my $sth_cl_abbr_sel = $dbh->prepare(qq|SELECT cl_abbr FROM concept_laterality WHERE cl_use AND cl_id=?|) or die $dbh->errstr;
			$sth_cl_abbr_sel->execute($cl_id) or die $dbh->errstr;
			if($sth_cl_abbr_sel->rows()>0){
				$column_number = 0;
				$sth_cl_abbr_sel->bind_col(++$column_number, \$cl_abbr, undef);
				$sth_cl_abbr_sel->fetch;
			}
			$sth_cl_abbr_sel->finish;
			undef $sth_cl_abbr_sel;
		}

		if(defined $cl_abbr && length $cl_abbr){
			$cp_abbr = '' unless(defined $cp_abbr && length $cp_abbr);
			$cdi_name = sprintf($subclass_format,$cdi_name,$cp_abbr,$cl_abbr);
		}
	}
	$cdi_name = undef unless($cdi_name =~ /$is_subclass_cdi_name/);

	return $cdi_name;
}

sub get_cdi_names {
	my %FORM = @_;

	my $dbh = $FORM{'dbh'};
	my $LOG = $FORM{'LOG'};

	my $cdi_names;
	if(exists $FORM{'cdi_name'} && defined $FORM{'cdi_name'}){
		if(ref $FORM{'cdi_name'} eq 'ARRAY'){
			foreach my $cdi_name (@{$FORM{'cdi_name'}}){
				my $rtn_cdi_name = &get_cdi_name(%FORM, cdi_name => $cdi_name);
				push(@$cdi_names, $rtn_cdi_name) if(defined $rtn_cdi_name && length $rtn_cdi_name);
			}
		}
		elsif(ref $FORM{'cdi_name'} eq '' && length $FORM{'cdi_name'}){
			my $rtn_cdi_name = &get_cdi_name(%FORM);
			push(@$cdi_names, $rtn_cdi_name) if(defined $rtn_cdi_name && length $rtn_cdi_name);
		}
	}
	if(defined $cdi_names && ref $cdi_names eq 'ARRAY' && scalar @$cdi_names){
		return $cdi_names;
	}
	else{
		return undef;
	}
}

sub create_subclass {
	my %FORM = @_;

	my $dbh = $FORM{'dbh'};
	my $LOG = $FORM{'LOG'};
#	&cgi_lib::common::message('create_subclass()', $LOG) if(defined $LOG);

#	&cgi_lib::common::message(\%FORM, $LOG) if(defined $LOG);
#	&cgi_lib::common::dumper(\%FORM, $LOG) if(defined $LOG);

	my $ci_id=$FORM{'ci_id'};
	my $cb_id=$FORM{'cb_id'};
	my $md_id=$FORM{'md_id'};
	my $mv_id=$FORM{'mv_id'};
	my $crl_id=$FORM{'crl_id'};

#	my $super_name=$FORM{'super_name'};
#	my $synonym=$FORM{'synonym'};

#	my $cdi_name;
#	$cdi_name = $FORM{'cdi_name'} if(exists $FORM{'cdi_name'} && defined $FORM{'cdi_name'} && length $FORM{'cdi_name'});

#	&cgi_lib::common::dumper(\%FORM, $LOG) if(defined $LOG);
	my $cdi_name = &get_cdi_name(%FORM);
#	&cgi_lib::common::message($cdi_name, $LOG) if(defined $LOG);
	return undef unless(defined $cdi_name);
	return undef unless($cdi_name =~ /$is_subclass_cdi_name/);
	my $cdi_pname = $1;
#	my $cmp_abbr = $2;
	my $cp_abbr = $2;
	my $cl_abbr = $3;

#	my $cmp_id = 0;
#	$cmp_id = $FORM{'cmp_id'} - 0 if(exists $FORM{'cmp_id'} && defined $FORM{'cmp_id'} && length $FORM{'cmp_id'});
#	my $cmp_id;
#	my $cmp_title;
	my $cp_id;
	my $cp_title;
	my $cl_id;
	my $cl_title;

	my $exists_check_trio = $FORM{'exists_check_trio'} // 1;

#	&cgi_lib::common::message("[$cdi_name][$exists_check_trio]", $LOG) if(defined $LOG);

	my $cdi_id;
	my $cdi_name_e;
	my $column_number;
	my $sth;

#	&cgi_lib::common::message("\$cdi_name=[$cdi_name]", $LOG) if(defined $LOG);
#	&cgi_lib::common::message("\$cdi_pname=[$cdi_pname]", $LOG) if(defined $LOG);
#	&cgi_lib::common::message("\$cmp_abbr=[$cmp_abbr]", $LOG) if(defined $LOG);

	my $cdi_pid;
	my $cdi_pname_e;
	my $seg_id;
	$sth = $dbh->prepare("SELECT cdi.cdi_id,cd_name,seg_id FROM concept_data_info as cdi,concept_data as cd WHERE cdi.ci_id=cd.ci_id AND cdi.cdi_id=cd.cdi_id AND cdi.ci_id=$ci_id AND cd.cb_id=$cb_id AND cdi_name=?") or die $dbh->errstr;
	$sth->execute($cdi_pname) or die $dbh->errstr;
	if($sth->rows()>0){
		$column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_pid, undef);
		$sth->bind_col(++$column_number, \$cdi_pname_e, undef);
		$sth->bind_col(++$column_number, \$seg_id, undef);
		$sth->fetch;
	}
	$sth->finish;
	undef $sth;
#	&cgi_lib::common::message("[$cdi_pname]:[$seg_id]", $LOG) if(defined $LOG);
#	&cgi_lib::common::message("\$cdi_name=[$cdi_name]", $LOG) if(defined $LOG);

	return undef unless(defined $cdi_pid && defined $cdi_pname_e);

=pod
	#LRの時にtrioテーブルに親が登録されているか確認
#	&cgi_lib::common::message("[$cdi_name][$exists_check_trio][$cmp_abbr]", $LOG) if(defined $LOG);
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
 concept_tree_trio AS ctt
LEFT JOIN (
 select * from concept_data_info
) AS lcdi ON lcdi.ci_id=ctt.ci_id AND lcdi.cdi_id=ctt.cdi_lid
LEFT JOIN (
 select * from concept_data_info
) AS rcdi ON rcdi.ci_id=ctt.ci_id AND rcdi.cdi_id=ctt.cdi_rid
WHERE
 ctt.ci_id=$ci_id AND ctt.cb_id=$cb_id AND ctt.cdi_pid=$cdi_pid
|;

#		&cgi_lib::common::message($sql_ctt_sel, $LOG) if(defined $LOG);
#		&cgi_lib::common::message($cdi_pid, $LOG) if(defined $LOG);

		my $sth_ctt_sel = $dbh->prepare($sql_ctt_sel) or die $dbh->errstr;
		$sth_ctt_sel->execute() or die $dbh->errstr;
#		&cgi_lib::common::message($sth_ctt_sel->rows(), $LOG) if(defined $LOG);
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
#		&cgi_lib::common::message("[$cdi_name][$exists_check_trio][$cmp_abbr][$cdi_lname]", $LOG) if(defined $LOG);
#		&cgi_lib::common::message("[$cdi_name][$exists_check_trio][$cmp_abbr][$cdi_rname]", $LOG) if(defined $LOG);
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
	my $infer_crl_id;
	my $temp_crt_ids;
	my $temp_crl_id;
#	if(defined $cmp_abbr && length $cmp_abbr){
	if(defined $cp_abbr && length $cp_abbr){
#		if($cmp_abbr =~ /$is_subclass_abbr_isa/){
		if($cp_abbr =~ /$is_subclass_abbr_isa/){
			$temp_crl_id = 3;
#			$infer_crl_id = 4;	#20190131 変更
#		}elsif($cmp_abbr =~ /$is_subclass_abbr_partof/){
		}elsif($cp_abbr =~ /$is_subclass_abbr_partof/){
			$temp_crl_id = 4;
			$infer_crl_id = 3;	#20190131 変更
		}
#		&cgi_lib::common::message($infer_crl_id, $LOG);
=pod
		if(defined $infer_crl_id){
			my $partof_pids;
			my $sth_ct_sel = $dbh->prepare("SELECT cdi_pid,crt_ids FROM concept_tree WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=$cdi_pid AND crl_id=$infer_crl_id") or die $dbh->errstr;
			$sth_ct_sel->execute() or die $dbh->errstr;
			if($sth_ct_sel->rows()>0){
				$column_number = 0;
				my $relation_pid;
				my $relation_crt_ids;
				$sth_ct_sel->bind_col(++$column_number, \$relation_pid, undef);
				$sth_ct_sel->bind_col(++$column_number, \$relation_crt_ids, undef);
				while($sth_ct_sel->fetch){
					if($cmp_abbr =~ /$is_subclass_abbr_LR/){
						$partof_pids->{$relation_pid} = undef;
					}elsif($cmp_abbr =~ /$is_subclass_abbr_LR_other/){
						if(defined $relation_crt_ids){
							foreach my $relation_crt_id (split(/;/,$relation_crt_ids)){
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
				my $sth_ctt_sel = $dbh->prepare(sprintf("SELECT cdi_lid,cdi_rid FROM concept_tree_trio WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_pid IN (%s)",join(',',keys(%$partof_pids)))) or die $dbh->errstr;
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
					my $sth_ct_sel = $dbh->prepare(sprintf("SELECT cdi_id,crt_ids FROM concept_tree WHERE ci_id=$ci_id AND cb_id=$cb_id AND crl_id=$infer_crl_id AND cdi_id IN (%s)",join(',',keys(%$infer_cdi_pids)))) or die $dbh->errstr;
					$sth_ct_sel->execute() or die $dbh->errstr;
					if($sth_ct_sel->rows()>0){
						$column_number = 0;
						my $relation_pid;
						my $relation_crt_ids;
						$sth_ct_sel->bind_col(++$column_number, \$relation_pid, undef);
						$sth_ct_sel->bind_col(++$column_number, \$relation_crt_ids, undef);
						while($sth_ct_sel->fetch){
							if(defined $relation_crt_ids){
								foreach my $relation_crt_id (split(/;/,$relation_crt_ids)){
									$infer_cdi_pids->{$relation_pid}->{$relation_crt_id} = undef;
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
		if(defined $infer_crl_id && $infer_crl_id == 3){
			my $sth_ct_sel = $dbh->prepare("SELECT cdi_pid FROM concept_tree WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=$cdi_pid AND crl_id=$infer_crl_id") or die $dbh->errstr;
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

		if(defined $temp_crl_id && $temp_crl_id == 4){
#			my $sth_crt_sel = $dbh->prepare("SELECT crt_ids FROM concept_tree WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=$cdi_pid AND crl_id=$temp_crl_id GROUP BY crt_ids") or die $dbh->errstr;	#20190131 変更
			my $sth_crt_sel = $dbh->prepare("SELECT crt_id FROM concept_relation_type WHERE crt_name='regional_part_of'") or die $dbh->errstr;
			$sth_crt_sel->execute() or die $dbh->errstr;
			if($sth_crt_sel->rows()>0){
				$column_number = 0;
				my $relation_crt_ids;
				$sth_crt_sel->bind_col(++$column_number, \$relation_crt_ids, undef);
				while($sth_crt_sel->fetch){
					foreach my $relation_crt_id (split(/;/,$relation_crt_ids)){
						$temp_crt_ids->{$relation_crt_id} = undef;
					}
				}
			}
			$sth_crt_sel->finish;
			undef $sth_crt_sel;
#			&cgi_lib::common::message($temp_crt_ids, $LOG);
		}
	}
	else{
		$temp_crl_id = 3;
	}


#	&cgi_lib::common::message($infer_cdi_pids, $LOG);
	#inferでの親を検索（ここまで）


#	my $temp_crt_id;
#	&cgi_lib::common::message($cmp_abbr, $LOG);
=pod
	if(defined $cmp_abbr && length $cmp_abbr){
		my $sth_cmp_abbr_sel = $dbh->prepare(qq|SELECT cmp_id,COALESCE(cmp_prefix,cmp_title) FROM concept_art_map_part WHERE cmp_abbr=?|) or die $dbh->errstr;
		$sth_cmp_abbr_sel->execute($cmp_abbr) or die $dbh->errstr;
#		&cgi_lib::common::message($sth_cmp_abbr_sel->rows(), $LOG);
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
	if(defined $cp_abbr && length $cp_abbr){
		my $sth_cp_abbr_sel = $dbh->prepare(qq|SELECT cp_id,COALESCE(cp_prefix,cp_title) FROM concept_part WHERE cp_abbr=?|) or die $dbh->errstr;
		$sth_cp_abbr_sel->execute($cp_abbr) or die $dbh->errstr;
#		&cgi_lib::common::message($sth_cmp_abbr_sel->rows(), $LOG);
		if($sth_cp_abbr_sel->rows()>0){
			$column_number = 0;
			$sth_cp_abbr_sel->bind_col(++$column_number, \$cp_id, undef);
			$sth_cp_abbr_sel->bind_col(++$column_number, \$cp_title, undef);
			$sth_cp_abbr_sel->fetch;
		}
		$sth_cp_abbr_sel->finish;
		undef $sth_cp_abbr_sel;
	}
	else{
		$cp_id = 0;
		$cp_title = '';
	}
	if(defined $cl_abbr && length $cl_abbr){
		my $sth_cl_abbr_sel = $dbh->prepare(qq|SELECT cl_id,COALESCE(cl_prefix,cl_title) FROM concept_laterality WHERE cl_abbr=?|) or die $dbh->errstr;
		$sth_cl_abbr_sel->execute($cl_abbr) or die $dbh->errstr;
#		&cgi_lib::common::message($sth_cmp_abbr_sel->rows(), $LOG);
		if($sth_cl_abbr_sel->rows()>0){
			$column_number = 0;
			$sth_cl_abbr_sel->bind_col(++$column_number, \$cl_id, undef);
			$sth_cl_abbr_sel->bind_col(++$column_number, \$cl_title, undef);
			$sth_cl_abbr_sel->fetch;
		}
		$sth_cl_abbr_sel->finish;
		undef $sth_cl_abbr_sel;
	}
	else{
		die sprintf('unknown concept_laterality [%s]',$cdi_name);
		$cl_id = 0;
		$cl_title = '';
	}


	my $cd_name = lc($cdi_pname_e);
=pod
	unless(defined $cmp_title && length $cmp_title){
#		$cd_name = sprintf('%s %s',$cmp_title,$cd_name);
#		&cgi_lib::common::message($cd_name, $LOG);

		if($cmp_abbr eq 'R'){
			$cmp_title = 'RIGHT';
		}
		elsif($cmp_abbr eq 'L'){
			$cmp_title = 'LEFT';
		}
		elsif($cmp_abbr eq 'N'){
			$cmp_title = 'PROXIMAL';
		}
		elsif($cmp_abbr eq 'F'){
			$cmp_title = 'DISTAL';
		}
		elsif($cmp_abbr eq 'O'){
			$cmp_title = 'OTHER';
		}
		elsif($cmp_abbr eq 'P'){
			$cmp_title = 'PROPER PART OF';
		}
		elsif($cmp_abbr eq 'Q' || $cmp_abbr =~ /^[STUVWX]$/){
			$cmp_title = 'A named part of';
		}
	}
	if(defined $cmp_title && length $cmp_title){
		$cd_name = sprintf('%s %s',$cmp_title,$cd_name);
	}
=cut
	if(defined $cp_title && length $cp_title){
		$cd_name = sprintf('%s %s',$cp_title,$cd_name);
	}
	if(defined $cl_title && length $cl_title){
		$cd_name = sprintf('%s %s',$cl_title,$cd_name);
	}


#	&cgi_lib::common::message($cd_name, $LOG);


	$sth = $dbh->prepare("SELECT cdi.cdi_id,COALESCE(cd_name,cdi_name_e) FROM concept_data_info as cdi LEFT JOIN (SELECT * FROM concept_data WHERE ci_id=$ci_id AND cb_id=$cb_id) AS cd ON cd.cdi_id=cdi.cdi_id WHERE cdi.ci_id=$ci_id AND cdi_name=?") or die $dbh->errstr;
	$sth->execute($cdi_name) or die $dbh->errstr;
#	&cgi_lib::common::message($sth->rows(), $LOG) if(defined $LOG);
	if($sth->rows()>0){
		$column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_id, undef);
		$sth->bind_col(++$column_number, \$cdi_name_e, undef);
		$sth->fetch;
	}
	$sth->finish;
	undef $sth;

#	&cgi_lib::common::message("\$cdi_id=[$cdi_id]", $LOG) if(defined $LOG);
#	&cgi_lib::common::message("\$cdi_name_e=[$cdi_name_e]", $LOG) if(defined $LOG);

	unless(defined $cdi_id){

		my $sth_cdi_sel = $dbh->prepare("SELECT COALESCE(MAX(cdi_id),0)+1 FROM concept_data_info WHERE ci_id=$ci_id") or die $dbh->errstr;
		$sth_cdi_sel->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth_cdi_sel->bind_col(++$column_number, \$cdi_id, undef);
		$sth_cdi_sel->fetch;
		$sth_cdi_sel->finish;
		undef $sth_cdi_sel;

#		my $sth_cdi_ins = $dbh->prepare("INSERT INTO concept_data_info (ci_id,cdi_id,cdi_name,cdi_name_e,cdi_entry,cdi_openid,is_user_data,cmp_id) VALUES ($ci_id,$cdi_id,?,?,now(),'system'::text,true,?)") or die $dbh->errstr;
#		$sth_cdi_ins->execute($cdi_name,$cd_name,$cmp_id) or die $dbh->errstr;
		my $sth_cdi_ins = $dbh->prepare("INSERT INTO concept_data_info (ci_id,cdi_id,cdi_name,cdi_name_e,cdi_entry,cdi_openid,is_user_data,cp_id,cl_id,cdi_pid) VALUES ($ci_id,$cdi_id,?,?,now(),'system'::text,true,?,?,?)") or die $dbh->errstr;
		$sth_cdi_ins->execute($cdi_name,$cd_name,$cp_id,$cl_id,$cdi_pid) or die $dbh->errstr;
		$sth_cdi_ins->finish;
		undef $sth_cdi_ins;
	}

	return undef unless(defined $cdi_id);

#	&cgi_lib::common::message("\$cd_name=[$cd_name]", $LOG) if(defined $LOG);
#	unless(defined $cdi_name_e && length $cdi_name_e){
	{
		my $sth_cdi_upd = $dbh->prepare("UPDATE concept_data_info SET cdi_name_e=? WHERE ci_id=$ci_id AND cdi_id=?") or die $dbh->errstr;
		$sth_cdi_upd->execute($cd_name,$cdi_id) or die $dbh->errstr;
		$sth_cdi_upd->finish;
		undef $sth_cdi_upd;
		$cdi_name_e = $cd_name;
	}

	my $super_id;
	if(exists $FORM{'super_name'}){
		if(defined $FORM{'super_name'} && length $FORM{'super_name'}){
			my $super_name = $FORM{'super_name'};
			my $sth_cdi_sel = $dbh->prepare("SELECT cdi_id FROM concept_data_info WHERE ci_id=$ci_id AND cdi_name=?") or die $dbh->errstr;
			$sth_cdi_sel->execute($super_name) or die $dbh->errstr;
			if($sth_cdi_sel->rows()>0){
				$column_number = 0;
				$sth_cdi_sel->bind_col(++$column_number, \$super_id, undef);
				$sth_cdi_sel->fetch;
			}
			$sth_cdi_sel->finish;
			undef $sth_cdi_sel;
		}
		my $sth_cdi_upd = $dbh->prepare("UPDATE concept_data_info SET cdi_super_id=? WHERE ci_id=$ci_id AND cdi_id=?") or die $dbh->errstr;
		$sth_cdi_upd->execute($super_id,$cdi_id) or die $dbh->errstr;
		$sth_cdi_upd->finish;
		undef $sth_cdi_upd;
	}

	$super_id=undef;
	{
		my $sth_cdi_sel = $dbh->prepare("SELECT cdi_super_id FROM concept_data_info WHERE ci_id=$ci_id AND cdi_id=?") or die $dbh->errstr;
		$sth_cdi_sel->execute($cdi_id) or die $dbh->errstr;
		if($sth_cdi_sel->rows()>0){
			$column_number = 0;
			$sth_cdi_sel->bind_col(++$column_number, \$super_id, undef);
			$sth_cdi_sel->fetch;
		}
		$sth_cdi_sel->finish;
		undef $sth_cdi_sel;
	}
	if(defined $super_id && defined $temp_crl_id && $temp_crl_id == 3){
		$infer_crl_id = 4;
	}

	if(defined $super_id && defined $infer_crl_id){
		$infer_cdi_pids = {};

		if($infer_crl_id == 4){
			my $relation_crt_id;
			my $sth_crt_sel = $dbh->prepare("SELECT crt_id FROM concept_relation_type WHERE crt_name='regional_part_of'") or die $dbh->errstr;
			$sth_crt_sel->execute() or die $dbh->errstr;
			if($sth_crt_sel->rows()>0){
				$column_number = 0;
				$sth_crt_sel->bind_col(++$column_number, \$relation_crt_id, undef);
				$sth_crt_sel->fetch;
			}
			$sth_crt_sel->finish;
			undef $sth_crt_sel;
			$infer_cdi_pids->{$super_id}->{$relation_crt_id} = undef;
		}
		else{
			$infer_cdi_pids->{$super_id} = undef;
		}
	}

	if(exists $FORM{'synonym'}){
		my $synonym = $FORM{'synonym'};
		my $sth_cdi_upd = $dbh->prepare("UPDATE concept_data_info SET cdi_syn_e=? WHERE ci_id=$ci_id AND cdi_id=?") or die $dbh->errstr;
		$sth_cdi_upd->execute($synonym,$cdi_id) or die $dbh->errstr;
		$sth_cdi_upd->finish;
		undef $sth_cdi_upd;
	}
	elsif(exists $FORM{'cdi_syn_e'}){
		my $synonym = $FORM{'cdi_syn_e'};
		my $sth_cdi_upd = $dbh->prepare("UPDATE concept_data_info SET cdi_syn_e=? WHERE ci_id=$ci_id AND cdi_id=?") or die $dbh->errstr;
		$sth_cdi_upd->execute($synonym,$cdi_id) or die $dbh->errstr;
		$sth_cdi_upd->finish;
		undef $sth_cdi_upd;
	}


	my $sth_cd_sel = $dbh->prepare("SELECT cdi_id FROM concept_data WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=$cdi_id") or die $dbh->errstr;
	$sth_cd_sel->execute() or die $dbh->errstr;
	my $cd_rows = $sth_cd_sel->rows();
	$sth_cd_sel->finish;
	undef $sth_cd_sel;
	unless($cd_rows>0){
		$seg_id = 0 unless(defined $seg_id);
		my $sth_cd_ins = $dbh->prepare("INSERT INTO concept_data (ci_id,cb_id,cdi_id,cd_name,cd_entry,cd_openid,seg_id) VALUES ($ci_id,$cb_id,$cdi_id,?,now(),'system'::text,?)") or die $dbh->errstr;
		$sth_cd_ins->execute($cd_name,$seg_id) or die $dbh->errstr;
		$sth_cd_ins->finish;
		undef $sth_cd_ins;
	}
#	unless(defined $cdi_name_e && length $cdi_name_e){
	{
		$seg_id = 0 unless(defined $seg_id);
		my $sth_cd_upd = $dbh->prepare("UPDATE concept_data SET cd_name=?,seg_id=? WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=?") or die $dbh->errstr;
		$sth_cd_upd->execute($cd_name,$seg_id,$cdi_id) or die $dbh->errstr;
		$sth_cd_upd->finish;
		undef $sth_cd_upd;
	}
	if(exists $FORM{'synonym'}){
		my $synonym = $FORM{'synonym'};
		my $sth_cd_upd = $dbh->prepare("UPDATE concept_data SET cd_syn=? WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=?") or die $dbh->errstr;
		$sth_cd_upd->execute($synonym,$cdi_id) or die $dbh->errstr;
		$sth_cd_upd->finish;
		undef $sth_cd_upd;
	}
	elsif(exists $FORM{'cdi_syn_e'}){
		my $synonym = $FORM{'cdi_syn_e'};
		my $sth_cd_upd = $dbh->prepare("UPDATE concept_data SET cd_syn=? WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=?") or die $dbh->errstr;
		$sth_cd_upd->execute($synonym,$cdi_id) or die $dbh->errstr;
		$sth_cd_upd->finish;
		undef $sth_cd_upd;
	}

=pod
	#LRの時にtrioテーブルに自分を登録（ここから）
	if($exists_check_trio && defined $cmp_abbr && length $cmp_abbr && $cmp_abbr =~ /$is_subclass_abbr_LR/){
		my $sql_ctt_sel = "SELECT cdi_pid FROM concept_tree_trio WHERE ci_id=$ci_id AND cb_id=$cb_id AND " . ($cmp_abbr eq 'L' ? "cdi_lid" : "cdi_rid") . "=?";
		my $sth_ctt_sel = $dbh->prepare($sql_ctt_sel) or die $dbh->errstr;
		$sth_ctt_sel->execute($cdi_id) or die $dbh->errstr;
		my $ctt_rows = $sth_ctt_sel->rows();
		$sth_ctt_sel->finish;
		undef $sth_ctt_sel;
		unless($ctt_rows>0){
			#反対側の情報を取得
			my $opposite_side_cdi_name = sprintf($subclass_format_old,$cdi_pname,($cmp_abbr eq 'L' ? 'R' : 'L'));
#			&cgi_lib::common::message($opposite_side_cdi_name, $LOG);
			my $opposite_side_cdi_id = &create_subclass(
				dbh   => $dbh,
				LOG   => $LOG,
				ci_id => $ci_id,
				cb_id => $cb_id,
				md_id => $md_id,
				mv_id => $mv_id,
				crl_id=> $crl_id,
				cmp_id=> 0,
				cdi_name=> $opposite_side_cdi_name,
				exists_check_trio=> 0,
			);
#			&cgi_lib::common::message($opposite_side_cdi_id, $LOG);
			return undef unless(defined $opposite_side_cdi_id);

			my $sth_ctt_ins = $dbh->prepare("INSERT INTO concept_tree_trio (ci_id,cb_id,cdi_pid,cdi_lid,cdi_rid) VALUES ($ci_id,$cb_id,$cdi_pid,?,?)") or die $dbh->errstr;
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

	my $temp_concept_tree_infos;

	if(defined $temp_crl_id){
		my $sth_cd_sel = $dbh->prepare("SELECT cdi_id FROM concept_tree WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=$cdi_id AND cdi_pid=$cdi_pid AND crl_id=$temp_crl_id") or die $dbh->errstr;
		$sth_cd_sel->execute() or die $dbh->errstr;
		my $cd_rows = $sth_cd_sel->rows();
		$sth_cd_sel->finish;
		undef $sth_cd_sel;

#		&cgi_lib::common::message($cd_rows, $LOG) if(defined $LOG);
		unless($cd_rows>0){
			my $temp_crt_id;
			$temp_crt_id = join(';',map {$_-0} sort {$a <=> $b} keys(%$temp_crt_ids)) if(defined $temp_crt_ids && ref $temp_crt_ids eq 'HASH' && scalar keys(%$temp_crt_ids));
			my $sth_cd_ins = $dbh->prepare("INSERT INTO concept_tree (ci_id,cb_id,cdi_id,cdi_pid,crl_id,crt_ids) VALUES ($ci_id,$cb_id,$cdi_id,$cdi_pid,$temp_crl_id,?)") or die $dbh->errstr;
			$sth_cd_ins->execute($temp_crt_id) or die $dbh->errstr;
			$sth_cd_ins->finish;
			undef $sth_cd_ins;
		}

		push(@$temp_concept_tree_infos,{
			cdi_pids => [$cdi_pid],
			crl_id  => $temp_crl_id
		});
	}
#	&cgi_lib::common::message($temp_concept_tree_infos, $LOG) if(defined $LOG);
#=pod
	if(defined $infer_crl_id && defined $infer_cdi_pids && ref $infer_cdi_pids eq 'HASH' && scalar keys(%$infer_cdi_pids)){
		my $sth_cd_sel = $dbh->prepare("SELECT cdi_id FROM concept_tree WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=$cdi_id AND cdi_pid=? AND crl_id=$infer_crl_id") or die $dbh->errstr;
		my $sth_cd_ins = $dbh->prepare("INSERT INTO concept_tree (ci_id,cb_id,cdi_id,cdi_pid,crl_id,crt_ids) VALUES ($ci_id,$cb_id,$cdi_id,?,$infer_crl_id,?)") or die $dbh->errstr;
		foreach my $relation_pid (keys(%$infer_cdi_pids)){
			$sth_cd_sel->execute($relation_pid) or die $dbh->errstr;
			my $cd_rows = $sth_cd_sel->rows();
			$sth_cd_sel->finish;

#			&cgi_lib::common::message($cd_rows, $LOG) if(defined $LOG);
			unless($cd_rows>0){
				my $relation_crl_id;
				$relation_crl_id = join(';',map {$_-0} sort {$a <=> $b} keys(%{$infer_cdi_pids->{$relation_pid}}))  if(defined $infer_cdi_pids->{$relation_pid} && ref $infer_cdi_pids->{$relation_pid} eq 'HASH' && scalar keys(%{$infer_cdi_pids->{$relation_pid}}));
				$sth_cd_ins->execute($relation_pid,$relation_crl_id) or die $dbh->errstr;
				$sth_cd_ins->finish;
			}
		}

		push(@$temp_concept_tree_infos,{
			cdi_pids => [keys(%$infer_cdi_pids)],
			crl_id  => $infer_crl_id
		});

		undef $sth_cd_sel;
		undef $sth_cd_ins;
	}
#=cut
#	&cgi_lib::common::message($temp_concept_tree_infos, $LOG) if(defined $LOG);

	if(defined $temp_concept_tree_infos && ref $temp_concept_tree_infos eq 'ARRAY' && scalar @$temp_concept_tree_infos){
		my $cdi_pids;
		foreach my $temp_concept_tree_info (@$temp_concept_tree_infos){
			foreach my $cdi_pid (@{$temp_concept_tree_info->{'cdi_pids'}}){
				$cdi_pids->{$cdi_pid} = undef;
			}
		}
		if(defined $cdi_pids && ref $cdi_pids eq 'HASH' && scalar keys(%$cdi_pids)){
			push(@$temp_concept_tree_infos,{
				cdi_pids => [keys(%$cdi_pids)],
				crl_id  => 0
			});
		}
	}
#	&cgi_lib::common::message($temp_concept_tree_infos, $LOG) if(defined $LOG);

	if(defined $temp_concept_tree_infos && ref $temp_concept_tree_infos eq 'ARRAY' && scalar @$temp_concept_tree_infos){
#		my $sth_cti_sel = $dbh->prepare("SELECT cti_cids,cti_depth,cti_pids FROM concept_tree_info WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=? AND crl_id=?") or die $dbh->errstr;
		my $sth_cti_sel = $dbh->prepare("SELECT cti_cids FROM concept_tree_info WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=? AND crl_id=?") or die $dbh->errstr;
		my $sth_cti_upd = $dbh->prepare("UPDATE concept_tree_info SET cti_cnum=?,cti_cids=? WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=? AND crl_id=?") or die $dbh->errstr;
		my $sth_cti_ins = $dbh->prepare("INSERT INTO concept_tree_info (cti_depth,cti_pnum,cti_pids,ci_id,cb_id,cdi_id,crl_id) VALUES (?,?,?,$ci_id,$cb_id,?,?)") or die $dbh->errstr;

		foreach my $temp_concept_tree_info (@$temp_concept_tree_infos){

#			&cgi_lib::common::message($temp_concept_tree_info, $LOG) if(defined $LOG);

			my $temp_crl_id2 = $temp_concept_tree_info->{'crl_id'};

			$sth_cti_sel->execute($cdi_id,$temp_crl_id2) or die $dbh->errstr;
			my $cti_rows = $sth_cti_sel->rows();
			$sth_cti_sel->finish;

			next if($cti_rows>0);

			my $cdi_pids = $temp_concept_tree_info->{'cdi_pids'};
			my $sth_cti_sels = $dbh->prepare(sprintf("SELECT cti_depth,cti_pids FROM concept_tree_info WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id in (%s) AND crl_id=%d",join(',',@$cdi_pids),$temp_crl_id2)) or die $dbh->errstr;

			my $max_cti_depth = 0;
			my %cti_pids_hash = map {$_=>undef} @$cdi_pids;

			my $cti_cnum;
			my $cti_cids;
			my $cti_depth;
			my $cti_pnum;
			my $cti_pids;
			$sth_cti_sels->execute() or die $dbh->errstr;
			$column_number = 0;
			$sth_cti_sels->bind_col(++$column_number, \$cti_depth, undef);
			$sth_cti_sels->bind_col(++$column_number, \$cti_pids, undef);
			while($sth_cti_sels->fetch){
				$cti_depth += 1;
				$max_cti_depth = $cti_depth if($max_cti_depth < $cti_depth);

				$cti_pids = &cgi_lib::common::decodeJSON($cti_pids) if(defined $cti_pids);
				$cti_pids = [] unless(defined $cti_pids && ref $cti_pids eq 'ARRAY');

				$cti_pids_hash{$_} = undef  for(@$cti_pids);
			}
			$sth_cti_sels->finish;
			undef $sth_cti_sels;

			$cti_pids = [map {$_-0} keys(%cti_pids_hash)];
			$cti_pnum = scalar @$cti_pids;
			$cti_pids = &cgi_lib::common::encodeJSON([sort {$a<=>$b} @$cti_pids]);

			$sth_cti_ins->execute($max_cti_depth,$cti_pnum,$cti_pids,$cdi_id,$temp_crl_id2) or die $dbh->errstr;
			$sth_cti_ins->finish;

	#		$cti_pids = [map {$_-0} keys(%cti_pids_hash)];
			$cti_pids = [$cdi_pid];

			foreach my $cti_pid (@$cti_pids){
				$sth_cti_sel->execute($cti_pid,$temp_crl_id2) or die $dbh->errstr;
				$column_number = 0;
				$sth_cti_sel->bind_col(++$column_number, \$cti_cids, undef);
				$sth_cti_sel->fetch;
				$sth_cti_sel->finish;

				$cti_cids = &cgi_lib::common::decodeJSON($cti_cids) if(defined $cti_cids);
				$cti_cids = [] unless(defined $cti_cids && ref $cti_cids eq 'ARRAY');
				push(@$cti_cids,$cdi_id-0);
				my %cti_cids_hash = map {$_=>undef} @$cti_cids;
				$cti_cids = [map {$_-0} keys(%cti_cids_hash)];
				$cti_cnum = scalar @$cti_cids;
				$cti_cids = &cgi_lib::common::encodeJSON([sort {$a<=>$b} @$cti_cids]);

				$sth_cti_upd->execute($cti_cnum,$cti_cids,$cti_pid,$temp_crl_id2) or die $dbh->errstr;
				$sth_cti_upd->finish;
			}
		}

		undef $sth_cti_sel;
		undef $sth_cti_upd;
		undef $sth_cti_ins;
	}

	return $cdi_id;
}

sub clear_subclass_tree_old {
	my %FORM = @_;

	my $dbh = $FORM{'dbh'};
	my $LOG = $FORM{'LOG'};
#	&cgi_lib::common::message('clear_subclass_tree_old()', $LOG) if(defined $LOG);

#	&cgi_lib::common::dumper(\%FORM, $LOG) if(defined $LOG);

	my $ci_id=$FORM{'ci_id'};
	my $cb_id=$FORM{'cb_id'};

#	my $cdi_name;
#	$cdi_name = $FORM{'cdi_name'} if(exists $FORM{'cdi_name'} && defined $FORM{'cdi_name'} && length $FORM{'cdi_name'});

	my $cdi_id;
	$cdi_id = $FORM{'cdi_id'} if(exists $FORM{'cdi_id'} && defined $FORM{'cdi_id'} && length $FORM{'cdi_id'});

	my $column_number;
	my $sth;

	unless(defined $cdi_id){
		my $cdi_name = &get_cdi_name_old(%FORM);
		return undef unless(defined $cdi_name);
		return undef unless($cdi_name =~ /$is_subclass_cdi_name_old/);

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

#	&cgi_lib::common::message($cdi_id, $LOG) if(defined $LOG);

	my @cdi_pids;
	my $sth_ct_sel = $dbh->prepare("SELECT cdi_pid FROM concept_tree WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=$cdi_id AND cdi_pid IS NOT NULL GROUP BY cdi_pid") or die $dbh->errstr;
	$sth_ct_sel->execute() or die $dbh->errstr;
	if($sth_ct_sel->rows()>0){
		my $cdi_pid;
		$column_number = 0;
		$sth_ct_sel->bind_col(++$column_number, \$cdi_pid, undef);
		while($sth_ct_sel->fetch){
			push(@cdi_pids, $cdi_pid) if(defined $cdi_pid);
		}
	}
	$sth_ct_sel->finish;
	undef $sth_ct_sel;

	&cgi_lib::common::message(sprintf("%d\t%d",$cdi_id,scalar @cdi_pids), $LOG) if(defined $LOG);

	if(scalar @cdi_pids){
		my $sth_cti_upd = $dbh->prepare("UPDATE concept_tree_info SET cti_cnum=?,cti_cids=? WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=? AND crl_id=?") or die $dbh->errstr;
		my $sth_cti_sel = $dbh->prepare(sprintf("SELECT cdi_id,crl_id,cti_cids FROM concept_tree_info WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id IN (%s)",join(',',map {'?'} @cdi_pids))) or die $dbh->errstr;
		$sth_cti_sel->execute(@cdi_pids) or die $dbh->errstr;
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
		$dbh->do(qq|DELETE FROM concept_data WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=$cdi_id|) or die $dbh->errstr;
	}
}

sub clear_subclass_tree {
	my %FORM = @_;

	my $dbh = $FORM{'dbh'};
	my $LOG = $FORM{'LOG'};
#	&cgi_lib::common::message('clear_subclass_tree()', $LOG) if(defined $LOG);

#	&cgi_lib::common::dumper(\%FORM, $LOG) if(defined $LOG);

	my $ci_id=$FORM{'ci_id'};
	my $cb_id=$FORM{'cb_id'};

#	my $cdi_name;
#	$cdi_name = $FORM{'cdi_name'} if(exists $FORM{'cdi_name'} && defined $FORM{'cdi_name'} && length $FORM{'cdi_name'});

	my $cdi_ids;
	$cdi_ids = [$FORM{'cdi_id'}] if(exists $FORM{'cdi_id'} && defined $FORM{'cdi_id'} && length $FORM{'cdi_id'});

	my $column_number;
	my $sth;

	unless(defined $cdi_ids){
		my $cdi_names = &get_cdi_names(%FORM);
		return undef unless(defined $cdi_names && ref $cdi_names eq 'ARRAY');

		my $cdi_id;
		$sth = $dbh->prepare("SELECT cdi_id FROM concept_data_info WHERE ci_id=$ci_id AND cdi_name=?") or die $dbh->errstr;
		foreach my $cdi_name (@$cdi_names){
			$sth->execute($cdi_name) or die $dbh->errstr;
			if($sth->rows()>0){
				$column_number = 0;
				$sth->bind_col(++$column_number, \$cdi_id, undef);
				$sth->fetch;
				push(@$cdi_ids, $cdi_id-0) if(defined $cdi_id && length $cdi_id);
			}
			$sth->finish;
		}
		undef $sth;
	}
	return unless(defined $cdi_ids && ref $cdi_ids eq 'ARRAY' && scalar @$cdi_ids);

	foreach my $cdi_id (@$cdi_ids){

		my @cdi_pids;
		my $sth_ct_sel = $dbh->prepare("SELECT cdi_pid FROM concept_tree WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=$cdi_id AND cdi_pid IS NOT NULL GROUP BY cdi_pid") or die $dbh->errstr;
		$sth_ct_sel->execute() or die $dbh->errstr;
		if($sth_ct_sel->rows()>0){
			my $cdi_pid;
			$column_number = 0;
			$sth_ct_sel->bind_col(++$column_number, \$cdi_pid, undef);
			while($sth_ct_sel->fetch){
				push(@cdi_pids, $cdi_pid) if(defined $cdi_pid);
			}
		}
		$sth_ct_sel->finish;
		undef $sth_ct_sel;

		if(scalar @cdi_pids){
			my $sth_cti_upd = $dbh->prepare("UPDATE concept_tree_info SET cti_cnum=?,cti_cids=? WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=? AND crl_id=?") or die $dbh->errstr;
			my $sth_cti_sel = $dbh->prepare(sprintf("SELECT cdi_id,crl_id,cti_cids FROM concept_tree_info WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id IN (%s)",join(',',map {'?'} @cdi_pids))) or die $dbh->errstr;
			$sth_cti_sel->execute(@cdi_pids) or die $dbh->errstr;
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
			$dbh->do(qq|DELETE FROM concept_data WHERE ci_id=$ci_id AND cb_id=$cb_id AND cdi_id=$cdi_id|) or die $dbh->errstr;
		}
	}
}

=pod
SELECT
 cdi.cdi_id,
 cdi.cdi_name,
 cti.cti_depth
FROM
 concept_tree_info AS cti
LEFT JOIN (
 SELECT * FROM concept_data_info
) AS cdi ON cdi.ci_id=cti.ci_id AND cdi.cdi_id=cti.cdi_id
LEFT JOIN (
 SELECT * FROM concept_art_map
) AS cm ON cm.ci_id=cti.ci_id AND cm.cdi_id=cti.cdi_id

WHERE
 cdi.is_user_data AND
-- cm.cm_use AND
-- cm.cm_delcause IS NULL AND
 cti.crl_id=0 AND
 cti.ci_id=1 AND
 cti.cb_id=11
ORDER BY
 cti.cti_depth,
 cdi.cdi_name
=cut

sub all_list_subclass_old {
	my %FORM = @_;

	my $dbh = $FORM{'dbh'};
	my $LOG = $FORM{'LOG'};

#	&cgi_lib::common::dumper(\%FORM, $LOG) if(defined $LOG);

	my $ci_id=$FORM{'ci_id'};
	my $cb_id=$FORM{'cb_id'};

	my $ALL_LIST;

	my $sth = $dbh->prepare(qq|
SELECT
 cdi.cdi_id,
 cdi.cdi_name
FROM
 concept_data_info AS cdi

WHERE
 cdi.is_user_data AND
 cdi.ci_id=$ci_id
ORDER BY
 cdi.cdi_name
|) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
#	&cgi_lib::common::message($sth->rows(), $LOG);
	if($sth->rows()>0){
		my $column_number = 0;
		my $cdi_id;
		my $cdi_name;
		$sth->bind_col(++$column_number, \$cdi_id, undef);
		$sth->bind_col(++$column_number, \$cdi_name, undef);
		while($sth->fetch){
			push(@$ALL_LIST, {
				cdi_id => $cdi_id - 0,
				cdi_name => $cdi_name
			});
		}
	}
	$sth->finish;
	undef $sth;

	return $ALL_LIST;
}

sub all_list_subclass {
	my %FORM = @_;

	my $dbh = $FORM{'dbh'};
	my $LOG = $FORM{'LOG'};

#	&cgi_lib::common::dumper(\%FORM, $LOG) if(defined $LOG);

	my $ci_id=$FORM{'ci_id'};
	my $cb_id=$FORM{'cb_id'};

	my $ALL_LIST;

	my $sth = $dbh->prepare(qq|
SELECT
 cdi.cdi_id,
 cdi.cdi_name,
 cti.cti_depth
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
ORDER BY
 cti.cti_depth,
 cdi.cdi_name
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
				cti_depth => $cti_depth - 0,
			});
		}
	}
	$sth->finish;
	undef $sth;

	return $ALL_LIST;
}

sub all_use_list_subclass {
	my %FORM = @_;

	my $dbh = $FORM{'dbh'};
	my $LOG = $FORM{'LOG'};
#	&cgi_lib::common::message('all_use_list_subclass()', $LOG) if(defined $LOG);

	&cgi_lib::common::dumper(\%FORM, $LOG) if(defined $LOG);

	my $ci_id=$FORM{'ci_id'};
	my $cb_id=$FORM{'cb_id'};

	my $ALL_LIST;
	my $sth;

	if(exists $FORM{'cdi_name'} && defined $FORM{'cdi_name'}){
		my $cdi_names = &get_cdi_names(%FORM);
		if(defined $cdi_names && ref $cdi_names eq 'ARRAY' && scalar @$cdi_names){

			$sth = $dbh->prepare(sprintf(qq|
SELECT
  cdi.cdi_id
 ,cdi.cdi_name
-- ,cdip.cdi_id AS cdi_pid
-- ,cdip.cdi_name AS cdi_pname
FROM
  concept_art_map AS cm
LEFT JOIN
  concept_data_info AS cdi ON cm.ci_id=cdi.ci_id AND cm.cdi_id=cdi.cdi_id

LEFT JOIN
  concept_data_info AS cdip ON cm.ci_id=cdip.ci_id AND cdip.cdi_name=regexp_replace(cdi.cdi_name, E'^(FMA[0-9]+).*\$', E'\\\\1')
LEFT JOIN
  concept_data AS cd ON cd.ci_id=cdip.ci_id AND cd.cdi_id=cdip.cdi_id

WHERE
 cdi.is_user_data
 AND cm.cm_use
 AND cm.cm_delcause IS NULL
 AND cd.ci_id=$ci_id
 AND cd.cb_id=$cb_id
 AND cdi.cdi_name IN (%s)
GROUP BY
 cdi.cdi_id
 ,cdi.cdi_name
-- ,cdip.cdi_id
-- ,cdip.cdi_name
|,join(',',map {'?'} @$cdi_names))) or die $dbh->errstr;

			$sth->execute(@$cdi_names) or die $dbh->errstr;

		}
	}
	else{
		my $sql = qq|
SELECT
  cdi.cdi_id
 ,cdi.cdi_name
-- ,cdip.cdi_id AS cdi_pid
-- ,cdip.cdi_name AS cdi_pname
FROM
  concept_art_map AS cm
LEFT JOIN
  concept_data_info AS cdi ON cm.ci_id=cdi.ci_id AND cm.cdi_id=cdi.cdi_id

LEFT JOIN
  concept_data_info AS cdip ON cm.ci_id=cdip.ci_id AND cdip.cdi_name=regexp_replace(cdi.cdi_name, E'^(FMA[0-9]+).*\$', E'\\\\1')
LEFT JOIN
  concept_data AS cd ON cd.ci_id=cdip.ci_id AND cd.cdi_id=cdip.cdi_id

WHERE
 cdi.is_user_data
 AND cm.cm_use
 AND cm.cm_delcause IS NULL
 AND cd.ci_id=$ci_id
 AND cd.cb_id=$cb_id
GROUP BY
 cdi.cdi_id
 ,cdi.cdi_name
-- ,cdip.cdi_id
-- ,cdip.cdi_name
|;
		&cgi_lib::common::message($sql, $LOG) if(defined $LOG);
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
	}

	if(defined $sth){
		if($sth->rows()>0){
			my $column_number = 0;
			my $cdi_id;
			my $cdi_name;
			my $cdi_pname;
			$sth->bind_col(++$column_number, \$cdi_id, undef);
			$sth->bind_col(++$column_number, \$cdi_name, undef);
#			$sth->bind_col(++$column_number, \$cdi_pname, undef);
			while($sth->fetch){
				&cgi_lib::common::message($cdi_name, $LOG) if(defined $LOG);
				push(@$ALL_LIST, {
					cdi_id => $cdi_id - 0,
					cdi_name => $cdi_name,
#					cdi_pname => $cdi_pname,
				});
			}
		}
		$sth->finish;
		undef $sth;
#		&cgi_lib::common::message($ALL_LIST, $LOG) if(defined $LOG);
#		die __LINE__;
	}

	return $ALL_LIST;
}

sub all_clear_subclass_tree_old {
	my %FORM = @_;

	my $dbh = $FORM{'dbh'};
	my $LOG = $FORM{'LOG'};

	&cgi_lib::common::message('all_clear_subclass_tree_old()', $LOG) if(defined $LOG);

	my $ALL_LIST = &all_list_subclass_old(%FORM);
#	&cgi_lib::common::message($ALL_LIST, $LOG) if(defined $LOG);
#	die __LINE__;
	if(defined $ALL_LIST && ref $ALL_LIST eq 'ARRAY' && scalar @$ALL_LIST){
		&clear_subclass_tree_old(%FORM, cdi_id=>$_->{'cdi_id'}, cdi_name=>$_->{'cdi_name'} ) for(@$ALL_LIST);
	}
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

sub all_recreate_subclass {
	my %FORM = @_;

	my $dbh = $FORM{'dbh'};
	my $LOG = $FORM{'LOG'};
#	&cgi_lib::common::message('all_recreate_subclass()', $LOG) if(defined $LOG);

	if(exists $FORM{'cdi_name'} && defined  $FORM{'cdi_name'} && length  $FORM{'cdi_name'}){
#		&cgi_lib::common::message($FORM{'cdi_name'}, $LOG) if(defined $LOG);
		&clear_subclass_tree(%FORM);
		my $ALL_USE_LIST = &all_use_list_subclass(%FORM);
#		&cgi_lib::common::message($ALL_USE_LIST, $LOG) if(defined $LOG);
		if(defined $ALL_USE_LIST && ref $ALL_USE_LIST eq 'ARRAY' && scalar @$ALL_USE_LIST){
			my %HASH_ALL_USE_LIST = map { $_->{'cdi_name'} => $_->{'cdi_id'} } @$ALL_USE_LIST;
			my $cdi_names = &get_cdi_names(%FORM);
			if(defined $cdi_names && ref $cdi_names eq 'ARRAY'){
				foreach my $cdi_name (@$cdi_names){
#					&cgi_lib::common::message($cdi_name, $LOG) if(defined $LOG);
					my $cdi_id;
					$cdi_id = &create_subclass( %FORM, cdi_name => $cdi_name ) if(exists $HASH_ALL_USE_LIST{$cdi_name});
#					&cgi_lib::common::message($cdi_id, $LOG) if(defined $LOG);
				}
			}
		}
	}
	else{
		my $ALL_LIST = &all_list_subclass(%FORM);
#		&cgi_lib::common::message(defined $ALL_LIST ? ref $ALL_LIST : '', $LOG) if(defined $LOG);
		if(defined $ALL_LIST && ref $ALL_LIST eq 'ARRAY' && scalar @$ALL_LIST){
#			&cgi_lib::common::message(scalar @$ALL_LIST, $LOG) if(defined $LOG);
			foreach my $data (reverse @$ALL_LIST){
#				&cgi_lib::common::message($data->{'cdi_name'}, $LOG) if(defined $LOG);
				&clear_subclass_tree(%FORM, cdi_id=>$data->{'cdi_id'}, cdi_name=>$data->{'cdi_name'} );
			}
		}
		my $ALL_USE_LIST = &all_use_list_subclass(%FORM);
		if(defined $ALL_USE_LIST && ref $ALL_USE_LIST eq 'ARRAY' && scalar @$ALL_USE_LIST){
			&cgi_lib::common::message(scalar @$ALL_USE_LIST, $LOG) if(defined $LOG);
#			&cgi_lib::common::message($ALL_USE_LIST, $LOG) if(defined $LOG);
#			die __LINE__;
			foreach my $data (@$ALL_USE_LIST){
#				&cgi_lib::common::message($data->{'cdi_name'}, $LOG) if(defined $LOG);
				unless(defined &create_subclass( %FORM, cdi_name=>$data->{'cdi_name'} )){
#					&cgi_lib::common::message($data->{'cdi_name'}, $LOG) if(defined $LOG);
					&cgi_lib::common::message($data, $LOG) if(defined $LOG);
					die __LINE__;
				}
			}
		}
	}
}

sub get_trio_name {
	my %FORM = @_;

	my $dbh = $FORM{'dbh'};
	my $LOG = $FORM{'LOG'};

#	&cgi_lib::common::message(\%FORM, $LOG) if(defined $LOG);
#	&cgi_lib::common::dumper(\%FORM, $LOG) if(defined $LOG);

	my $ci_id=$FORM{'ci_id'};
	my $cb_id=$FORM{'cb_id'};

	my $cdi_name = &get_cdi_name(%FORM);
	return undef unless(defined $cdi_name);
	return undef unless($cdi_name =~ /$is_subclass_cdi_name/);
	my $cdi_pname = $1;
#	my $cmp_abbr = $2;
	my $cp_abbr = $2;
	my $cl_abbr = $3;

	my $column_number;
	my $sth;
	my $cdi_pid;
	$sth = $dbh->prepare("SELECT cdi_id FROM concept_data_info WHERE ci_id=$ci_id AND cdi_name=?") or die $dbh->errstr;
	$sth->execute($cdi_pname) or die $dbh->errstr;
	if($sth->rows()>0){
		$column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_pid, undef);
		$sth->fetch;
	}
	$sth->finish;
	undef $sth;

	return undef unless(defined $cdi_pid);

#	if(defined $cmp_abbr && length $cmp_abbr && $cmp_abbr =~ /$is_subclass_abbr_LR/){
	if(defined $cl_abbr && length $cl_abbr && $cl_abbr =~ /$is_subclass_abbr_LR/){
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
 concept_tree_trio AS ctt
LEFT JOIN (
 select * from concept_data_info
) AS lcdi ON lcdi.ci_id=ctt.ci_id AND lcdi.cdi_id=ctt.cdi_lid
LEFT JOIN (
 select * from concept_data_info
) AS rcdi ON rcdi.ci_id=ctt.ci_id AND rcdi.cdi_id=ctt.cdi_rid
WHERE
 ctt.ci_id=$ci_id AND ctt.cb_id=$cb_id AND ctt.cdi_pid=?
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

#		if($cmp_abbr eq 'L' && defined $cdi_lname && $cdi_lname ne $cdi_name){
		if($cl_abbr eq 'L' && defined $cdi_lname && $cdi_lname ne $cdi_name){
			$cdi_name = $cdi_lname;
		}
#		elsif($cmp_abbr eq 'R' && defined $cdi_rname && $cdi_rname ne $cdi_name){
		elsif($cl_abbr eq 'R' && defined $cdi_rname && $cdi_rname ne $cdi_name){
			$cdi_name = $cdi_rname;
		}
	}
	return $cdi_name;
}

1;
