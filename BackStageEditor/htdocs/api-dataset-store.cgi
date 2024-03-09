#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use DBD::Pg;
use File::Copy;
use File::Spec;
use Time::HiRes;

my $t0 = [&Time::HiRes::gettimeofday()];

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
require "webgl_common.pl";
use cgi_lib::common;
use make_httpd_conf;
use BITS::ConceptArtMapModified;
use BITS::ConceptArtMapPart;
my $is_subclass_cdi_name = $BITS::ConceptArtMapPart::is_subclass_cdi_name;

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);

my($logfile,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);

$logfile .= qq|.$FORM{cmd}| if(exists $FORM{'cmd'} && defined $FORM{'cmd'} && length $FORM{'cmd'});
$logfile .=  sprintf(".%02d%02d%02d.%05d",$hour,$min,$sec,$$) if(exists $FORM{'cmd'} && defined $FORM{'cmd'} && length $FORM{'cmd'} && $FORM{'cmd'} ne 'update-progress');

open(my $LOG,"> $logfile");
select($LOG);
$| = 1;
select(STDOUT);
flock($LOG,2);
print $LOG "\n[$logtime]:$0\n";
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%ENV, 1), $LOG);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);

&setDefParams(\%FORM,\%COOKIE);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);

#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $where;
my @bind_values = ();
if(exists $FORM{'filter'} && defined $FORM{'filter'}){
	my $filter = &cgi_lib::common::decodeJSON($FORM{'filter'});
	if(defined $filter){
		my @W;
		foreach my $f (@$filter){
			next unless(exists $f->{'property'} && defined $f->{'property'} && exists $f->{'value'} && defined $f->{'value'});
			push(@W,qq|$f->{property}=?|);
			push(@bind_values,$f->{value});
		}
		$where = qq|where |.join(" AND ",@W) if(scalar @W > 0);
	}
}
#29:$FORM{'filter'}=[[{"property":"md_id","value":1}]]

$FORM{'cmd'} = 'read' unless(exists $FORM{'cmd'} && defined $FORM{'cmd'});

my $DATASET = {
	datas => [],
	total => 0,
	success => JSON::XS::false
};

=pod
$ENV{'HTTP_ACCEPT'} = 'text/event-stream' unless(exists $ENV{'REQUEST_METHOD'} && defined $ENV{'REQUEST_METHOD'});
if(exists $ENV{'HTTP_ACCEPT'} && defined $ENV{'HTTP_ACCEPT'} && $ENV{'HTTP_ACCEPT'} eq 'text/event-stream'){
	print qq|Content-type: $ENV{'HTTP_ACCEPT'}\n\n|;
	eval{
		$dbh->do("LISTEN model_version");
		LISTENLOOP: {
			my $p = 0;
			while (my $notify = $dbh->pg_notifies) {
				my ($name, $pid, $payload) = @$notify;
				print qq{data: I received notice "$name" FROM PID $pid, payload was "$payload"\n};
				$p = 1;
			}
			$dbh->ping() or die qq{Ping failed!};
			print "\n" unless($p);
			print "\n";
			sleep(1);
			redo;
		}
	};
	if($@){
		print "data: $@\n\n";
	}
	exit;
}
=cut

if($FORM{'cmd'} eq 'read'){
	eval{
		my $sql=<<SQL;
select * FROM (
select
 mr.md_id,
 mr.mv_id,
 mr.mr_id,
 mr.mr_version,
 md_name_e,
 md_abbr,
 mv_name_e,
 mv_objects_set,
 mv_publish,
 mv_port,
 mv_frozen,
 mv_comment,
 mv_order,
 mv_use,
 mv.ci_id,
 ci.ci_name,
 mv.cb_id,
 cb.cb_name,
 cb.cb_comment,
 CASE WHEN cb.cb_comment is not null AND length(cb.cb_comment)>0 THEN ci.ci_name || ' ' || cb.cb_name || ' [' || cb.cb_comment || ']'
      ELSE ci.ci_name || ' ' || cb.cb_name
 END AS cb_display,
 mv.ci_id || '-' || mv.cb_id AS concept,
 mv.mv_name_e || ' [' || ci.ci_name || ' ' || cb.cb_name || ']' AS display,
 md_abbr || '-' || mv_name_e AS value,

 EXTRACT(EPOCH FROM mv_entry) AS mv_entry,
 EXTRACT(EPOCH FROM mr_entry) AS mr_entry,
 EXTRACT(EPOCH FROM cb_release) AS cb_release
from
 model_revision AS mr
LEFT JOIN (
  select * FROM model
 ) AS md ON md.md_id=mr.md_id
LEFT JOIN (
  select * FROM model_version
 ) AS mv ON mv.md_id=mr.md_id AND mv.mv_id=mr.mv_id
LEFT JOIN (
  select * FROM concept_info
 ) AS ci ON ci.ci_id=mv.ci_id
LEFT JOIN (
  select * FROM concept_build
--   WHERE cb_use
 ) AS cb ON cb.ci_id=mv.ci_id AND cb.cb_id=mv.cb_id
where
 md.md_use and
-- mv.mv_use and
 (mr.md_id,mr.mv_id,mr.mr_id) IN (
   select
    md_id,
    mv_id,
    max(mr_id) AS mr_id
   from
    model_revision
   where
    mr_use
   GROUP BY
    md_id,
    mv_id
 )
order by
 md_order,
 mv_order,
 mr_order
) AS a
$where
SQL

		print $LOG __LINE__,":\$sql=[",$sql,"]\n";
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		if(scalar @bind_values > 0){
			$DATASET->{'total'} = $sth->execute(@bind_values) or die $dbh->errstr;
		}else{
			$DATASET->{'total'} = $sth->execute() or die $dbh->errstr;
		}

		my($md_id,$mv_id,$mr_id,$mr_version,$md_name_e,$md_abbr,$mv_name_e,$mv_objects_set,$mv_publish,$mv_port,$mv_frozen,$mv_comment,$mv_order,$mv_use,$ci_id,$ci_name,$cb_id,$cb_name,$cb_comment,$cb_display,$concept,$display,$value,$mv_entry,$mr_entry,$cb_release);

		my $column_number = 0;
		$sth->bind_col(++$column_number, \$md_id, undef);
		$sth->bind_col(++$column_number, \$mv_id, undef);
		$sth->bind_col(++$column_number, \$mr_id, undef);
		$sth->bind_col(++$column_number, \$mr_version, undef);
		$sth->bind_col(++$column_number, \$md_name_e, undef);
		$sth->bind_col(++$column_number, \$md_abbr, undef);
		$sth->bind_col(++$column_number, \$mv_name_e, undef);
		$sth->bind_col(++$column_number, \$mv_objects_set, undef);
		$sth->bind_col(++$column_number, \$mv_publish, undef);
		$sth->bind_col(++$column_number, \$mv_port, undef);
		$sth->bind_col(++$column_number, \$mv_frozen, undef);
		$sth->bind_col(++$column_number, \$mv_comment, undef);
		$sth->bind_col(++$column_number, \$mv_order, undef);
		$sth->bind_col(++$column_number, \$mv_use, undef);
		$sth->bind_col(++$column_number, \$ci_id, undef);
		$sth->bind_col(++$column_number, \$ci_name, undef);
		$sth->bind_col(++$column_number, \$cb_id, undef);
		$sth->bind_col(++$column_number, \$cb_name, undef);
		$sth->bind_col(++$column_number, \$cb_comment, undef);
		$sth->bind_col(++$column_number, \$cb_display, undef);
		$sth->bind_col(++$column_number, \$concept, undef);
		$sth->bind_col(++$column_number, \$display, undef);
		$sth->bind_col(++$column_number, \$value, undef);
		$sth->bind_col(++$column_number, \$mv_entry, undef);
		$sth->bind_col(++$column_number, \$mr_entry, undef);
		$sth->bind_col(++$column_number, \$cb_release, undef);

		while($sth->fetch){
			my($version,$revision) = split(/\./,$mr_version);
			my $HASH = {
				md_id => $md_id+0,
				mv_id => $mv_id+0,
				mr_id => $mr_id+0,
				mv_publish => $mv_publish ? JSON::XS::true : JSON::XS::false,
				mv_port => defined $mv_port ? $mv_port+0 : undef,
				mv_frozen => $mv_frozen ? JSON::XS::true : JSON::XS::false,
				mv_comment => $mv_comment,
				mv_objects_set => $mv_objects_set,
				mv_order => $mv_order+0,
				mv_use => $mv_use ? JSON::XS::true : JSON::XS::false,
				ci_id => $ci_id+0,
				ci_name => $ci_name,
				cb_id => $cb_id+0,
				cb_name => $cb_name,
				cb_comment => $cb_comment,
				cb_display => $cb_display,
				concept   => $concept,

				md_name_e => $md_name_e,
				md_abbr => $md_abbr,
				mv_entry => $mv_entry+0,
				mr_entry => $mr_entry+0,
				mr_version => $mr_version,
				cb_release => $cb_release+0,

#				display => $mv_name_e,
#				display => qq|$mv_name_e [$ci_name $cb_name]|,
				display => $display,
		#		value   => qq|$md_id-$mv_id-$mr_id|,
#				value   => qq|$md_abbr-$mv_name_e|,
				value   => $value,
				version => $mv_name_e,
				data    => qq|obj/$md_abbr/$mv_name_e|,

				'version.version' => defined $version ? $version+0 : undef,
				'version.revision' => defined $revision ? $revision+0 : undef,

				version_version => defined $version ? $version+0 : undef,
				version_revision => defined $revision ? $revision+0 : undef,
				fmt_version => defined $version && defined $revision ? sprintf(qq|%010d%010d|,$version,$revision) : $mr_version,

			};
			push(@{$DATASET->{'datas'}},$HASH);
		}
		$sth->finish;
		undef $sth;

		$DATASET->{'total'} = scalar @{$DATASET->{'datas'}};
		$DATASET->{'success'} = JSON::XS::true;
	};
	if($@){
		$DATASET->{'msg'} = $@;
		print $LOG __LINE__,":",$@,"\n";
	}

}elsif(exists $FORM{'datas'} && defined $FORM{'datas'}){
	my $datas = &cgi_lib::common::decodeJSON($FORM{'datas'});
	if(defined $datas && ref $datas eq 'ARRAY'){

		my $sql_cbr_sel = 'select f_potid FROM concept_build_relation WHERE cbr_use AND ci_id=? AND cb_id=?';
		my $sth_cbr_sel = $dbh->prepare($sql_cbr_sel) or die $dbh->errstr;

		my $sql_bt_ins = 'INSERT INTO buildup_tree (md_id,mv_id,mr_id,ci_id,cb_id,cdi_id,cdi_pid,bul_id,f_potids) VALUES (?,?,?,?,?,?,?,?,?)';
		my $sth_bt_ins = $dbh->prepare($sql_bt_ins) or die $dbh->errstr;

		my $sql_ct_sel = 'select cdi_id,cdi_pid,bul_id,f_potids FROM concept_tree WHERE ci_id=? AND cb_id=?';
		my $sth_ct_sel = $dbh->prepare($sql_ct_sel) or die $dbh->errstr;

		my $sql_bti_ins_fmt = q|INSERT INTO buildup_tree_info
SELECT
 %d           AS md_id,
 %d           AS mv_id,
 %d           AS mr_id,
 ci_id,
 cb_id,
 cdi_id,
 cti_cnum     AS but_cnum,
 cti_cids     AS but_cids,
 cti_depth    AS but_depth,
 cti_pnum     AS but_pnum,
 cti_pids     AS but_pids,
 cti_delcause AS but_delcause,
 cti_entry    AS but_entry,
 cti_openid   AS but_openid,
 crl_id       AS bul_id
FROM
 concept_tree_info
WHERE
 ci_id=%d AND
 cb_id=%d
|;

		my $sql_btt_ins_fmt = q|INSERT INTO buildup_tree_trio
SELECT
 %d           AS md_id,
 %d           AS mv_id,
 %d           AS mr_id,
 ci_id,
 cb_id,
 cdi_pid,
 cdi_lid,
 cdi_rid,
 ctt_delcause,
 ctt_entry,
 ctt_openid
FROM
 concept_tree_trio
WHERE
 ci_id=%d AND
 cb_id=%d
|;

		my $sql_bd_ins_fmt = q|INSERT INTO buildup_data
SELECT
 %d           AS md_id,
 %d           AS mv_id,
 %d           AS mr_id,
 ci_id,
 cb_id,
 cdi_id,
 cd_name,
 cd_syn,
 cd_def,
 cd_delcause,
 cd_entry,
 cd_openid,
 phy_id,
 seg_id
FROM
 concept_data
WHERE
 ci_id=%d AND
 cb_id=%d
|;


		if($FORM{'cmd'} eq 'create'){

#$dbh->do(qq|ALTER TABLE concept_art_map DISABLE TRIGGER USER;|) or die $dbh->errstr;
#$dbh->do(qq|ALTER TABLE history_concept_art_map DISABLE TRIGGER USER;|) or die $dbh->errstr;

			$dbh->{'AutoCommit'} = 0;
			$dbh->{'RaiseError'} = 1;
			eval{
				my @MESSAGE;
				#表示順を仮更新
				my $num = scalar @$datas;
				my $sth_ver_upd = $dbh->prepare(qq|UPDATE model_version SET mv_order=mv_order+$num|) or die $dbh->errstr;
				my $sth_rev_upd = $dbh->prepare(qq|UPDATE model_revision SET mr_order=mr_order+$num|) or die $dbh->errstr;
				$sth_ver_upd->execute() or die $dbh->errstr;
				$sth_ver_upd->finish;
				$sth_rev_upd->execute() or die $dbh->errstr;
				$sth_rev_upd->finish;
				undef $sth_ver_upd;
				undef $sth_rev_upd;

				#データ追加(model_version,model_revision)
				my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
				$year+=1900;
				$mon+=1;
				my $mv_release = sprintf("%04d-%02d-%02d",$year,$mon,$mday);
				my $mv_rep_key = sprintf("%s%02d%02d",substr(sprintf("%04d",$year),2,2),$mon,$mday);
				my $mr_release = sprintf("%04d-%02d-%02d %02d:%02d:%02d",$year,$mon,$mday,$hour,$min,$sec);
				my $mr_rep_key = $mv_rep_key;
				my $mr_revision = sprintf("%s%02d%02d%02d%02d",substr(sprintf("%04d",$year),2,2),$mon,$mday,$hour,$min);
				my $sth_ver_ins = $dbh->prepare(qq|INSERT INTO model_version (md_id,mv_id,mv_version,mv_order,mv_name_e,mv_objects_set,mv_release,mv_rep_key,mv_entry,mv_openid,mv_publish,mv_modified,mv_use,ci_id,cb_id) VALUES (?,?,?,1,?,?,?,?,now(),'system',?,now(),'true',?,?)|) or die $dbh->errstr;
				my $sth_rev_ins = $dbh->prepare(qq|INSERT INTO model_revision (md_id,mv_id,mr_id,mr_version,mr_revision,mr_order,mr_release,mr_rep_key,mr_entry,mr_openid,mr_use) VALUES (?,?,?,?,?,1,?,?,now(),'system','true')|) or die $dbh->errstr;

				my $hash_copy_info;

#				$dbh->rollback;
#				&gzip_json($DATASET);
#				close($LOG);
#				exit;


				foreach my $data (@$datas){
#					my $mv_version = sprintf("%s.%s",$data->{'version'},$mr_revision);
					my $mv_version = sprintf("%s.%s.%s",$data->{'version.version'},$data->{'version.revision'},$mr_revision);

					#データ追加(model_version)
					$sth_ver_ins->execute($data->{'md_id'},$data->{'mv_id'},$mv_version,$data->{'version'},$data->{'mv_objects_set'},$mv_release,$mv_rep_key,$data->{'mv_publish'},$data->{'ci_id'},$data->{'cb_id'}) or die $dbh->errstr;
					$sth_ver_ins->finish;

					#データ追加(model_revision)
					$sth_rev_ins->execute($data->{'md_id'},$data->{'mv_id'},$data->{'mr_id'},$mv_version,$mr_revision,$mr_release,$mr_rep_key) or die $dbh->errstr;
					$sth_rev_ins->finish;

					$dbh->do(sprintf($sql_bd_ins_fmt, $data->{'md_id'}, $data->{'mv_id'}, $data->{'mr_id'}, $data->{'ci_id'}, $data->{'cb_id'})) or die $dbh->errstr;

					$dbh->do(sprintf($sql_bti_ins_fmt, $data->{'md_id'}, $data->{'mv_id'}, $data->{'mr_id'}, $data->{'ci_id'}, $data->{'cb_id'})) or die $dbh->errstr;

					$dbh->do(sprintf($sql_btt_ins_fmt, $data->{'md_id'}, $data->{'mv_id'}, $data->{'mr_id'}, $data->{'ci_id'}, $data->{'cb_id'})) or die $dbh->errstr;

					$sth_cbr_sel->execute($data->{'ci_id'},$data->{'cb_id'}) or die $dbh->errstr;
					my($f_potid,$use_f_potids);
					my $column_number = 0;
					$sth_cbr_sel->bind_col(++$column_number, \$f_potid, undef);
					while($sth_cbr_sel->fetch){
						$use_f_potids->{$f_potid} = undef;
					}
					$sth_cbr_sel->finish;

					$sth_ct_sel->execute($data->{'ci_id'},$data->{'cb_id'}) or die $dbh->errstr;
					my($cdi_id,$cdi_pid,$bul_id,$f_potids,$cdi_pids,$cdi_cids);
					$column_number = 0;
					$sth_ct_sel->bind_col(++$column_number, \$cdi_id, undef);
					$sth_ct_sel->bind_col(++$column_number, \$cdi_pid, undef);
					$sth_ct_sel->bind_col(++$column_number, \$bul_id, undef);
					$sth_ct_sel->bind_col(++$column_number, \$f_potids, undef);
					while($sth_ct_sel->fetch){
						my $is_ins = 0;
						if($bul_id==3){
							$is_ins = 1;
							$cdi_pids->{$bul_id}->{$cdi_pid} = undef if(defined $cdi_pid);
							$cdi_cids->{$bul_id}->{$cdi_id} = undef if(defined $cdi_id);
						}
						elsif($bul_id==4 && defined $f_potids && length $f_potids){
							my @F_POTIDS;
							foreach my $f_potid (split(/;/,$f_potids)){
								next unless(exists $use_f_potids->{$f_potid});
								$is_ins = 1;
								$cdi_pids->{$bul_id}->{$cdi_pid} = undef if(defined $cdi_pid);
								$cdi_cids->{$bul_id}->{$cdi_id} = undef if(defined $cdi_id);
								push(@F_POTIDS, $f_potid);
							}
							$f_potids = join(';',@F_POTIDS);
						}
						next unless($is_ins);

						$sth_bt_ins->execute($data->{'md_id'},$data->{'mv_id'},$data->{'mr_id'},$data->{'ci_id'},$data->{'cb_id'},$cdi_id,$cdi_pid,$bul_id,$f_potids) or die $dbh->errstr;
						$sth_bt_ins->finish;
						&cgi_lib::common::message(qq|cdi_id=[$cdi_id],bul_id=[$bul_id]|, $LOG);
					}
					$sth_ct_sel->finish;

					if(defined $cdi_pids && ref $cdi_pids eq 'HASH'){
						foreach my $bul_id (keys(%$cdi_pids)){
							foreach my $cdi_id (keys(%{$cdi_pids->{$bul_id}})){
								delete $cdi_pids->{$bul_id}->{$cdi_id} if(exists $cdi_cids->{$bul_id}->{$cdi_id});
							}
						}
						foreach my $bul_id (keys(%$cdi_pids)){
							foreach my $cdi_id (keys(%{$cdi_pids->{$bul_id}})){
								$sth_bt_ins->execute($data->{'md_id'},$data->{'mv_id'},$data->{'mr_id'},$data->{'ci_id'},$data->{'cb_id'},$cdi_id,undef,$bul_id,undef) or die $dbh->errstr;
								$sth_bt_ins->finish;
								&cgi_lib::common::message(qq|cdi_id=[$cdi_id],bul_id=[$bul_id]|, $LOG);
							}
						}
					}
				}
				undef $sth_ver_ins;
				undef $sth_rev_ins;


				#表示順を更新
				my $sth_md = $dbh->prepare(qq|SELECT DISTINCT md_id FROM model_version|) or die $dbh->errstr;
				my $sth_mv = $dbh->prepare(qq|SELECT mv_id FROM model_version WHERE md_id=? ORDER BY mv_order,mv_id DESC|) or die $dbh->errstr;
				my $sth_mr = $dbh->prepare(qq|SELECT mv_id,mr_id FROM model_revision WHERE md_id=? ORDER BY mr_order,mv_id DESC,mr_id DESC|) or die $dbh->errstr;
				$sth_md->execute() or die $dbh->errstr;
				my $md_id;
				$sth_md->bind_col(1, \$md_id, undef);
				while($sth_md->fetch){
					#表示順を更新(model_version)
					$sth_mv->execute($md_id) or die $dbh->errstr;
					my $mv_id;
					$sth_mv->bind_col(1, \$mv_id, undef);
					my $mv_order = 0;
					while($sth_mv->fetch){
						$mv_order++;
						$dbh->do(qq|UPDATE model_version SET mv_order=$mv_order WHERE md_id=$md_id AND mv_id=$mv_id|) or die $dbh->errstr;
					}
					$sth_mv->finish;

					#表示順を更新(model_revision)
					$sth_mr->execute($md_id) or die $dbh->errstr;
					my $mr_id;
					$sth_mr->bind_col(1, \$mv_id, undef);
					$sth_mr->bind_col(2, \$mr_id, undef);
					my $mr_order = 0;
					while($sth_mr->fetch){
						$mr_order++;
						$dbh->do(qq|UPDATE model_revision SET mr_order=$mr_order WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id|) or die $dbh->errstr;
					}
					$sth_mr->finish;
				}
				$sth_md->finish;
				undef $sth_md;
				undef $sth_mv;


				if(defined $hash_copy_info && ref $hash_copy_info eq 'HASH'){
					foreach my $key (keys(%$hash_copy_info)){
						my($md_id,$prev_mv_id,$next_mv_id) = split(/\t/,$key);
						&copy_images($md_id,$prev_mv_id,$next_mv_id);
					}
				}

				$DATASET->{'msg'} = &cgi_lib::common::decodeUTF8(join("\n",@MESSAGE)) if(scalar @MESSAGE);

				$dbh->commit();

				$dbh->do("NOTIFY model_version");

				$DATASET->{'success'} = JSON::XS::true;
			};
			if($@){
				$DATASET->{'msg'} = &cgi_lib::common::decodeUTF8($@);
				print $LOG __LINE__,":",$@,"\n";
				$dbh->rollback;
			}
			$dbh->{'AutoCommit'} = 1;
			$dbh->{'RaiseError'} = 0;

#$dbh->do(qq|ALTER TABLE concept_art_map ENABLE TRIGGER USER;|) or die $dbh->errstr;
#$dbh->do(qq|ALTER TABLE history_concept_art_map ENABLE TRIGGER USER;|) or die $dbh->errstr;

		}
		elsif($FORM{'cmd'} eq 'update'){
			my $batch_datas;
			$dbh->{'AutoCommit'} = 0;
			$dbh->{'RaiseError'} = 1;
			eval{

				#表示順を更新
				my $sth_mv_old = $dbh->prepare(qq|SELECT * FROM model_version WHERE md_id=? AND mv_id=?|) or die $dbh->errstr;
				my $sth_mv = $dbh->prepare(qq|SELECT mv_order FROM model_version WHERE md_id=? AND mv_id=?|) or die $dbh->errstr;
				my $sth_mr = $dbh->prepare(qq|SELECT mv_id,mr_id FROM model_revision WHERE md_id=? ORDER BY mr_order,mv_id DESC,mr_id DESC|) or die $dbh->errstr;

				my $sth_cm_sel = $dbh->prepare(qq|SELECT cdi_name,cmp_id FROM concept_art_map AS cm LEFT JOIN (SELECT ci_id,cdi_id,cdi_name FROM concept_data_info) AS cdi ON cdi.ci_id=cm.ci_id AND cdi.cdi_id=cm.cdi_id WHERE md_id=? AND mv_id=?|) or die $dbh->errstr;
				my $sth_cm_upd = $dbh->prepare(qq|UPDATE concept_art_map SET cb_id=?,cm_entry=now() WHERE md_id=? AND mv_id=? AND cb_id<>?|) or die $dbh->errstr;

				my $sth = $dbh->prepare(qq|UPDATE model_version SET mv_publish=?,mv_port=?,mv_frozen=?,mv_name_e=?,mv_objects_set=?,mv_comment=?,mv_order=?,mv_use=?,cb_id=?,mv_modified=now() WHERE md_id=? AND mv_id=?|) or die $dbh->errstr;
				foreach my $data (@$datas){

					$sth_mv_old->execute($data->{'md_id'},$data->{'mv_id'}) or die $dbh->errstr;
					my $mv_old = $sth_mv_old->fetchrow_hashref;
					$sth_mv_old->finish;

					my $md_id = $data->{'md_id'};
					$sth_mv->execute($md_id,$data->{'mv_id'}) or die $dbh->errstr;
					my $old_mv_order;
					$sth_mv->bind_col(1, \$old_mv_order, undef);
					$sth_mv->fetch;
					$sth_mv->finish;

					#表示順を更新(model_version)
					my $sth_mv1;
					my $sth_mv2;
					if($old_mv_order>$data->{'mv_order'}){
#						$sth_mv1 = $dbh->prepare(qq|SELECT mv_id FROM model_version WHERE md_id=? AND mv_id<>? AND mv_order<=? ORDER BY mv_order,mv_id DESC|) or die $dbh->errstr;
						$sth_mv2 = $dbh->prepare(qq|SELECT mv_id FROM model_version WHERE md_id=? AND mv_id<>? AND mv_order>=? ORDER BY mv_order,mv_id DESC|) or die $dbh->errstr;
					}else{
						$sth_mv1 = $dbh->prepare(qq|SELECT mv_id FROM model_version WHERE md_id=? AND mv_id<>? AND mv_order<=? ORDER BY mv_order,mv_id DESC|) or die $dbh->errstr;
						$sth_mv2 = $dbh->prepare(qq|SELECT mv_id FROM model_version WHERE md_id=? AND mv_id<>? AND mv_order>? ORDER BY mv_order,mv_id DESC|) or die $dbh->errstr;
					}
					my $mv_order = 0;
					if(defined $sth_mv1){
						$sth_mv1->execute($md_id,$data->{'mv_id'},$data->{'mv_order'}) or die $dbh->errstr;
						my $mv_id;
						$sth_mv1->bind_col(1, \$mv_id, undef);
						while($sth_mv1->fetch){
							$mv_order++;
							$dbh->do(qq|UPDATE model_version SET mv_order=$mv_order WHERE md_id=$md_id AND mv_id=$mv_id|) or die $dbh->errstr;
						}
						$sth_mv1->finish;
						undef $sth_mv1;
					}
					$mv_order = $data->{'mv_order'};
					$sth_mv2->execute($md_id,$data->{'mv_id'},$data->{'mv_order'}) or die $dbh->errstr;
					my $mv_id;
					$sth_mv2->bind_col(1, \$mv_id, undef);
					while($sth_mv2->fetch){
						$mv_order++;
						$dbh->do(qq|UPDATE model_version SET mv_order=$mv_order WHERE md_id=$md_id AND mv_id=$mv_id|) or die $dbh->errstr;
					}
					$sth_mv2->finish;
					undef $sth_mv2;


					#表示順を更新(model_revision)
					$sth_mr->execute($md_id) or die $dbh->errstr;
					my $mr_id;
					$sth_mr->bind_col(1, \$mv_id, undef);
					$sth_mr->bind_col(2, \$mr_id, undef);
					my $mr_order = 0;
					while($sth_mr->fetch){
						$mr_order++;
						$dbh->do(qq|UPDATE model_revision SET mr_order=$mr_order WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id|) or die $dbh->errstr;
					}
					$sth_mr->finish;

					$data->{'mv_use'} = 1 unless(exists $data->{'mv_use'} && defined $data->{'mv_use'});
					my $rows = $sth->execute($data->{'mv_publish'},$data->{'mv_port'},$data->{'mv_frozen'},$data->{'version'},$data->{'mv_objects_set'},$data->{'mv_comment'},$data->{'mv_order'},$data->{'mv_use'},$data->{'cb_id'},$data->{'md_id'},$data->{'mv_id'}) or die $dbh->errstr;
					$DATASET->{'total'} += $rows if($rows>0);
					$sth->finish;

					if($mv_old->{'cb_id'} ne $data->{'cb_id'}){
						push(@$batch_datas, $data);
					}
				}
				undef $sth;
				undef $sth_mv;
				undef $sth_mr;
				$dbh->commit();

				$dbh->do("NOTIFY model_version");

				$DATASET->{'success'} = JSON::XS::true;
			};
			if($@){
				$DATASET->{'msg'} = $@;
				print $LOG __LINE__,":",$@,"\n";
				$dbh->rollback;
			}
			$dbh->{'AutoCommit'} = 1;
			$dbh->{'RaiseError'} = 0;

			if(defined $batch_datas && ref $batch_datas eq 'ARRAY' && scalar @$batch_datas){
				$DATASET->{'sessionID'} = &_update({datas => $batch_datas});
			}
		}
		if($DATASET->{'success'} == JSON::XS::true){
			&make_httpd_conf::make_renderer_conf($dbh);
		}
	}
	else{
		$DATASET->{'msg'} = &cgi_lib::common::decodeUTF8('JSON形式が違います');
	}
}
elsif($FORM{'cmd'} eq 'update-progress'){
	eval{
		$DATASET->{'progress'} = &_update_progress(\%FORM);
		&cgi_lib::common::message($DATASET, $LOG) if(defined $LOG);
		if(exists $DATASET->{'progress'} && defined $DATASET->{'progress'}){
			$DATASET->{'success'} = JSON::XS::true;
			$DATASET->{'sessionID'} = $FORM{'sessionID'};
		}else{
			die 'Unknown Error('.__LINE__.')';
		}
	};
	if($@){
		$DATASET->{'msg'} = &cgi_lib::common::decodeUTF8($@);
		&cgi_lib::common::message($DATASET->{'msg'}, $LOG) if(defined $LOG);
		if($ENV{'HTTP_ACCEPT'} eq 'text/event-stream'){
			map {print "data: ".$_."\n"} split(/\n/,&cgi_lib::common::encodeJSON($DATASET));
			print "\n";
			exit;
		}
	}
}

#my $json = &JSON::XS::encode_json($DATASET);
#print $json;
&gzip_json($DATASET);
close($LOG);
exit;

print <<HTML;
{datas: [{
	display:    '4.0',
	value:      '1-3',
	version:    '4.0.1305021540',
	data:       'obj/bp3d/4.0',
	md_id:      1,
	mv_id:      3,
	mv_publish: true
},{
	display:    '3.0',
	value:      '1-2',
	version:    '3.0.1304161700',
	data:       'obj/bp3d/3.0',
	md_id:      1,
	mv_id:      2,
	mv_publish: true
},{
	display:    '2.0',
	value:      '1-1',
	version:    '2.0.1304161700',
	data:       'obj/bp3d/2.0',
	md_id:      1,
	mv_id:      1,
	mv_publish: true
}
HTML

sub copy_images {
	my $md_id = shift;
	my $prev_mv_id = shift;
	my $next_mv_id = shift;


	if(defined $md_id && defined $prev_mv_id && defined $next_mv_id){

		my $prog_basename = qq|copy_rep_image|;
		my $prog = File::Spec->catfile($FindBin::Bin,qq|../cron|,qq|$prog_basename.pl|);
		if(-e $prog && -X $prog){
			my $pid = fork;
			if(defined $pid){
				if($pid == 0){
					my $f1 = "$FindBin::Bin/logs/$prog_basename.log";
					my $f2 = "$FindBin::Bin/logs/$prog_basename.err";
					close(STDOUT);
					close(STDERR);
					open STDOUT, ">> $f1" || die "[$f1] $!\n";
					open STDERR, ">> $f2" || die "[$f2] $!\n";
					close(STDIN);
					exec(qq|nice -n 19 $prog $md_id $prev_mv_id $next_mv_id|);
					exit(1);
				}
			}else{
				die("Can't execute program");
			}
		}
	}
	return;
}

sub _update {
	my $FORM = shift;
	my $sessionID;
	if(defined $FORM){
		my $out_path = &catdir($FindBin::Bin,'temp');
		my $prog_basename = qq|batch-dataset-store|;
		my $prog = &catfile($FindBin::Bin,'..','batch',qq|$prog_basename.pl|);
		if(-e $prog && -x $prog){
			$sessionID = &Digest::MD5::md5_hex(&Time::HiRes::time());
			$FORM->{'sessionID'} = $sessionID;
			$FORM->{'prefix'} = &catdir($out_path,$sessionID);

			my $params_file = &catfile($out_path,qq|$sessionID.json|);
			&cgi_lib::common::message('$params_file=['.$params_file.']',$LOG) if(defined $LOG);
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

sub _update_progress {
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
		delete $progress->{'prefix'}    if(exists $progress->{'prefix'});
		delete $progress->{'sessionID'} if(exists $progress->{'sessionID'});
		delete $progress->{'datas'}     if(exists $progress->{'datas'});
		unlink $params_file if(exists $progress->{'msg'} && defined $progress->{'msg'} && lc($progress->{'msg'}) eq 'end' && -e $params_file);
	}

	return $progress;
}
