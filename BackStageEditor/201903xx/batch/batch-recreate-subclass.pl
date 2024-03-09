#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use Getopt::Long qw(:config posix_default no_ignore_case gnu_compat);
my $config = {
	host => $ENV{'AG_DB_HOST'} // '127.0.0.1',
	port => $ENV{'AG_DB_PORT'} // '8543'
};
&Getopt::Long::GetOptions($config,qw/
	host|h=s
	port|p=s
	md_id=i
	mv_id=i
	mr_id=i
	ci_id=i
	cb_id=i
	cdi_name=s
	debug
/) or exit 1;

$ENV{'AG_DB_HOST'} = $config->{'host'};
$ENV{'AG_DB_PORT'} = $config->{'port'};

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;

require "webgl_common.pl";
use cgi_lib::common;

use BITS::ConceptArtMapPart;

my $LOG = \*STDERR;

my $dbh = &get_dbh();
$dbh->{'AutoCommit'} = 0;
$dbh->{'RaiseError'} = 1;
eval{
#	&cgi_lib::common::message($config, $LOG);
	if(exists $config->{'md_id'} && exists $config->{'mv_id'} && exists $config->{'mr_id'} && exists $config->{'ci_id'} && exists $config->{'cb_id'}){
		my $md_id = $config->{'md_id'} - 0;
		my $mv_id = $config->{'mv_id'} - 0;
		my $mr_id = $config->{'mr_id'} - 0;
		my $ci_id = $config->{'ci_id'} - 0;
		my $cb_id = $config->{'cb_id'} - 0;
		my $cdi_name = $config->{'cdi_name'};
		&BITS::ConceptArtMapPart::all_recreate_subclass(
			dbh => $dbh,
			LOG => $LOG,
			md_id => $md_id,
			mv_id => $mv_id,
			mr_id => $mr_id,
			ci_id => $ci_id,
			cb_id => $cb_id,
			cdi_name => $cdi_name,
		);
	}else{
#		&cgi_lib::common::message($dbh->do("select * from concept_tree where cdi_id=105003"));
#		&cgi_lib::common::message($dbh->do("select * from concept_tree where cdi_id in (105019,105126)"));
#		&cgi_lib::common::message($dbh->do(q|select cdi_id from concept_tree where cb_id=11 and crl_id=4 and cdi_id in (select cdi_id from concept_data_info where cdi_name in ( select substring(cdi_name,0,length(cdi_name)-2) from concept_data_info where cdi_name like '%-L' ))|));

		my $sth_cb_sel = $dbh->prepare(q|
SELECT
 mv.ci_id,
 mv.cb_id,
 mr.md_id,
 mr.mv_id,
 mr.mr_id
FROM
 model_revision AS mr
LEFT JOIN (
 SELECT * FROM model_version
) AS mv ON
 mv.md_id=mr.md_id AND
 mv.mv_id=mr.mv_id
WHERE
 mr_use AND
 mv_use
--  AND mv_publish
ORDER BY
 mv_order,
 mr_order
|) or die $dbh->errstr;
		$sth_cb_sel->execute() or die $dbh->errstr;
		if($sth_cb_sel->rows()>0){
			my $ci_id;
			my $cb_id;
			my $md_id;
			my $mv_id;
			my $mr_id;
			my $column_number = 0;
			$sth_cb_sel->bind_col(++$column_number, \$ci_id, undef);
			$sth_cb_sel->bind_col(++$column_number, \$cb_id, undef);
			$sth_cb_sel->bind_col(++$column_number, \$md_id, undef);
			$sth_cb_sel->bind_col(++$column_number, \$mv_id, undef);
			$sth_cb_sel->bind_col(++$column_number, \$mr_id, undef);
			while($sth_cb_sel->fetch){
				&cgi_lib::common::message("[$ci_id][$cb_id][$md_id][$mv_id][$mr_id]", $LOG);
				&BITS::ConceptArtMapPart::all_recreate_subclass(
					dbh => $dbh,
					LOG => $LOG,
					ci_id => $ci_id - 0,
					cb_id => $cb_id - 0,
					md_id => $md_id - 0,
					mv_id => $mv_id - 0,
					mr_id => $mr_id - 0,
				);
			}
		}
		$sth_cb_sel->finish;
		undef $sth_cb_sel;

#		&cgi_lib::common::message($dbh->do("select * from concept_tree where cdi_id=105003"));
#		&cgi_lib::common::message($dbh->do("select * from concept_tree where cdi_id in (105019,105126)"));
#		&cgi_lib::common::message($dbh->do(q|select cdi_id from concept_tree where cb_id=11 and crl_id=4 and cdi_id in (select cdi_id from concept_data_info where cdi_name in ( select substring(cdi_name,0,length(cdi_name)-2) from concept_data_info where cdi_name like '%-L' ))|));
	}
	$dbh->commit;
};
if($@){
	&cgi_lib::common::message($@, $LOG);
	$dbh->rollback;
}
$dbh->{'AutoCommit'} = 1;
$dbh->{'RaiseError'} = 0;

=pod
select cdi_id from concept_data_info where cdi_name='FMA60996-P';

select cdi_name,substr(cdi_name,1,length(cdi_name)-2),length(cdi_name) from concept_data_info where cdi_name like '%-L';
select cdi_name,substr(cdi_name,1,3),length(cdi_name) from concept_data_info where cdi_name like '%-L';

select cdi_id from concept_data_info where cdi_name in (
select cdi_name || '-L' from concept_data_info where cdi_id in (
 select cdi_id from concept_tree where cb_id=9 and crl_id=4 and cdi_id in (select cdi_id from concept_data_info where cdi_name in ( select substring(cdi_name,1,length(cdi_name)-2) from concept_data_info where cdi_name like '%-L' ))
)
);

select cdi_name from concept_data_info where cdi_id in (
select cdi_id from concept_tree where cdi_id in (
 select cdi_id from concept_data_info where cdi_name like '%-P'
)
);
=cut
