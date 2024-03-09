#!/bp3d/local/perl/bin/perl

use strict;

use Encode::Guess;
use Data::Dumper;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;

require "webgl_common.pl";

my $dbh = &get_dbh();

my %REPS;

eval{
	my $sql=<<SQL;
select mv.ci_id,mv.cb_id,mv.md_id,mv.mv_id,mr.mr_id,mr.mr_version from model_version as mv
left join (select * from model_revision where mr_use and mr_delcause IS NULL) as mr on (mr.md_id=mv.md_id AND mr.mv_id=mv.mv_id)
where
 mv_delcause is NULL AND
 mv_use AND
 mv_frozen
order by
 mv_order,
 mr_order
SQL
	my $sth_mv = $dbh->prepare($sql) or die $dbh->errstr;
	$sth_mv->execute() or die $dbh->errstr;
	my $ci_id;
	my $cb_id;
	my $md_id;
	my $mv_id;
	my $mr_id;
	my $mr_version;
	my $col_num=0;
	$sth_mv->bind_col(++$col_num, \$ci_id, undef);
	$sth_mv->bind_col(++$col_num, \$cb_id, undef);
	$sth_mv->bind_col(++$col_num, \$md_id, undef);
	$sth_mv->bind_col(++$col_num, \$mv_id, undef);
	$sth_mv->bind_col(++$col_num, \$mr_id, undef);
	$sth_mv->bind_col(++$col_num, \$mr_version, undef);
	while($sth_mv->fetch){
		print STDERR "\n[$mr_version]\n";
		my $sql=<<SQL;
select rep_id,EXTRACT(EPOCH FROM rep_entry),rep_entry from representation where rep_delcause is NULL AND (ci_id,cb_id,cdi_id,md_id,mv_id,mr_id) IN (
  select
   ci_id,cb_id,cdi_id,md_id,mv_id,max(mr_id)
  from
   representation
  where
   ci_id=$ci_id AND
   cb_id=$cb_id AND
   md_id=$md_id AND
   mv_id=$mv_id AND
   mr_id<=$mr_id
  group by
   ci_id,cb_id,cdi_id,md_id,mv_id
)
order by rep_serial desc
SQL
		my $sth_rep = $dbh->prepare($sql) or die $dbh->errstr;

		my $sql_map_art_date = qq|
select EXTRACT(EPOCH FROM max(cm_entry)),max(cm_entry) from concept_art_map where (ci_id,cb_id,md_id,mv_id,mr_id,cdi_id) in (
  select ci_id,cb_id,md_id,mv_id,max(mr_id) as mr_id,cdi_id from concept_art_map where ci_id=$ci_id AND cb_id=$cb_id AND md_id=$md_id AND mv_id=$mv_id AND mr_id<=$mr_id group by ci_id,cb_id,md_id,mv_id,cdi_id
) AND (art_id,art_hist_serial) in (
  select art_id,art_hist_serial from representation_art where rep_id=?
)
|;
		my $sth_map_art_date = $dbh->prepare($sql_map_art_date) or die $dbh->errstr;



		$sth_rep->execute() or die $dbh->errstr;
		my $rep_id;
		my $rep_entry_epoch;
		my $rep_entry;
		$col_num=0;
		$sth_rep->bind_col(++$col_num, \$rep_id, undef);
		$sth_rep->bind_col(++$col_num, \$rep_entry_epoch, undef);
		$sth_rep->bind_col(++$col_num, \$rep_entry, undef);
		while($sth_rep->fetch){
			$sth_map_art_date->execute($rep_id) or die $dbh->errstr;
			my $cm_entry_epoch;
			my $cm_entry;
			$col_num=0;
			$sth_map_art_date->bind_col(++$col_num, \$cm_entry_epoch, undef);
			$sth_map_art_date->bind_col(++$col_num, \$cm_entry, undef);
			$sth_map_art_date->fetch;
			$sth_map_art_date->finish;
			if(defined $cm_entry_epoch){
				if($cm_entry_epoch>$rep_entry_epoch){
					print STDERR "\r\tupdate!![$rep_id][$rep_entry]->[$cm_entry]\r";
					$REPS{$rep_id} = $cm_entry;
#					print STDERR $sql_map_art_date,"\n";
#					exit;
				}
			}else{
				print STDERR "\n\tNo map data!![$rep_id]\n";
			}
		}
		$sth_rep->finish;
		undef $sth_rep;
		undef $sth_map_art_date;
	}
	$sth_mv->finish;
	undef $sth_mv;
};
if($@){
	print __LINE__,":",$@,"\n";
	exit;
}
print STDERR "\n";

if(scalar keys(%REPS) > 0){
	$dbh->{AutoCommit} = 0;
	$dbh->{RaiseError} = 1;
	eval{
		my $sql = qq|update representation set rep_entry=? where rep_id=?|;
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		foreach my $rep_id (keys(%REPS)){
			$sth->execute($REPS{$rep_id},$rep_id) or die $dbh->errstr;
			$sth->finish;
		}
		undef $sth;

		$dbh->commit();
	#	$dbh->rollback;
	};
	if($@){
		print __LINE__,":",$@,"\n";
		$dbh->rollback;
	}
	$dbh->{AutoCommit} = 1;
	$dbh->{RaiseError} = 0;
}
