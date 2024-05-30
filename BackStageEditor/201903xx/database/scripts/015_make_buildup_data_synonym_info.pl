#!/opt/services/ag/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use FindBin;
use File::Path;
use JSON::XS;
use DBD::Pg;

use lib qq|$FindBin::Bin/../..|,qq|$FindBin::Bin/../../../lib|,qq|$FindBin::Bin/../../../../ag-common/lib|;

use Getopt::Long qw(:config posix_default no_ignore_case gnu_compat);
my $config = {
	db   => 'ag_public_1903xx',
	host => '127.0.0.1',
	port => '38300'
};
&Getopt::Long::GetOptions($config,qw/
	db|d=s
	host|h=s
	port|p=s
/) or exit 1;

$ENV{'AG_DB_NAME'} = $config->{'db'};
$ENV{'AG_DB_HOST'} = $config->{'host'};
$ENV{'AG_DB_PORT'} = $config->{'port'};

use cgi_lib::common;
require "common_db.pl";


my $dbh = &get_dbh();

sub error {
	select(STDERR);
	$| = 1;
	say qq|$0|;
	say qq|#optins :|;
	say qq|# --db,-d   : database name [default:$config->{'db'}]|;
	say qq|# --host,-h : database host [default:$config->{'host'}]|;
	say qq|# --port,-p : database port [default:$config->{'port'}]|;
	exit 1;
}

#exit 0;

=pod
=cut

#$dbh->{'AutoCommit'} = 0;
#$dbh->{'RaiseError'} = 1;
eval{
	my $rows;
	my $column_number;
	my $sql;
	my $sth;
	my $IN;
	my $md_id;
	my $mv_id;
	my $mr_id;
	my $ci_id;
	my $cb_id;
	my $cdi_id;
	my $cdi_name;
	my $cdi_syn;
	my $cd_name;
	my $cd_syn;
	my $cs_tablename = 'concept_synonym';
	my $cds_tablename = 'concept_data_synonym';
	my $cdst_tablename = 'concept_data_synonym_type';
	my $bds_tablename = 'buildup_data_synonym';
	my $cs_id;
	my $cs_name;
	my $cs_type;
	my $cds_id;
	my $cdst_id;
	my $cdst_name;
	my $CS_ID_HASH = {};
	my $CS_NAME_HASH = {};
	my $CS_TYPE_HASH = {};
	my $CDS_HASH = {};
	my $CDST_HASH = {};
	my $CDST_ID_HASH = {};
	my $CDST_NAME_HASH = {};
	my $BDS_HASH = {};

if(1){
#	&upd_data_from_rawdata();
#	exit;

#	$rows = $dbh->do(qq|DROP TABLE IF EXISTS $cds_tablename CASCADE|) or die $dbh->errstr;
#	&cgi_lib::common::message($rows);
#	$rows = $dbh->do(qq|DROP TABLE IF EXISTS $cdst_tablename CASCADE|) or die $dbh->errstr;
#	&cgi_lib::common::message($rows);
#	$rows = $dbh->do(qq|DROP TABLE IF EXISTS $cs_tablename CASCADE|) or die $dbh->errstr;
#	&cgi_lib::common::message($rows);
#	$rows = $dbh->do(qq|ALTER TABLE IF EXISTS concept_tree DROP COLUMN IF EXISTS cds_id CASCADE|) or die $dbh->errstr;
#	&cgi_lib::common::message($rows);
#	$rows = $dbh->do(qq|ALTER TABLE IF EXISTS concept_tree DROP COLUMN IF EXISTS cds_bid CASCADE|) or die $dbh->errstr;
#	&cgi_lib::common::message($rows);
#	$rows = $dbh->do(qq|DROP TABLE IF EXISTS $bds_tablename CASCADE|) or die $dbh->errstr;
#	&cgi_lib::common::message($rows);

	$sql = qq|SELECT tablename FROM pg_tables WHERE tablename=?|;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute($bds_tablename) or die $dbh->errstr;
	$rows = $sth->rows();
	$sth->finish;
	undef $sth;

	&cgi_lib::common::message($rows);
	unless($rows>0){
		$sql=qq|
CREATE TABLE IF NOT EXISTS $bds_tablename (
  cds_id       serial NOT NULL,
  md_id        integer NOT NULL,
  mv_id        integer NOT NULL,
  mr_id        integer NOT NULL,
  ci_id        integer NOT NULL,
  cb_id        integer NOT NULL,
  cdi_id       integer NOT NULL,
  cs_id        integer NOT NULL,
  cds_bid      integer,
  cdst_id      integer NOT NULL,
  cds_added    boolean NOT NULL DEFAULT false,
  cds_order    integer DEFAULT 0,
  cds_comment  text,
  cds_delcause text,
  cds_entry    timestamp without time zone DEFAULT now() NOT NULL,
  cds_openid   text DEFAULT 'system'::text NOT NULL,
  CONSTRAINT ${bds_tablename}_pkey PRIMARY KEY(cds_id),
  CONSTRAINT ${bds_tablename}_unique UNIQUE (md_id,mv_id,mr_id,ci_id,cb_id,cdi_id,cs_id,cdst_id),
  CONSTRAINT ${bds_tablename}_cds_openid_check CHECK ((cds_openid <> ''::text)),
  FOREIGN KEY ( ci_id ) REFERENCES concept_info ( ci_id ) ON DELETE CASCADE,
  FOREIGN KEY ( ci_id, cb_id ) REFERENCES concept_build ( ci_id,cb_id ) ON DELETE CASCADE,
  FOREIGN KEY ( ci_id, cdi_id ) REFERENCES concept_data_info ( ci_id,cdi_id ) ON DELETE CASCADE,
  FOREIGN KEY ( md_id, mv_id, mr_id, ci_id, cb_id, cdi_id ) REFERENCES buildup_data ( md_id, mv_id, mr_id, ci_id,cb_id,cdi_id ) ON DELETE CASCADE,
  FOREIGN KEY ( cs_id ) REFERENCES $cs_tablename ( cs_id ) ON DELETE CASCADE,
  FOREIGN KEY ( cds_bid ) REFERENCES $bds_tablename ( cds_id ) ON DELETE CASCADE,
  FOREIGN KEY ( cdst_id ) REFERENCES $cdst_tablename ( cdst_id ) ON DELETE CASCADE,
  FOREIGN KEY ( md_id ) REFERENCES model(md_id) ON DELETE CASCADE,
  FOREIGN KEY ( md_id, mv_id ) REFERENCES model_version(md_id, mv_id) ON DELETE CASCADE,
  FOREIGN KEY ( md_id, mv_id, mr_id ) REFERENCES model_revision(md_id, mv_id, mr_id) ON DELETE CASCADE
);
|;
		$rows = $dbh->do($sql) or die $dbh->errstr;
		&cgi_lib::common::message($rows);
	}

	$sql = qq|SELECT cs_id,cs_name FROM $cs_tablename|;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$rows = $sth->rows();
	$column_number=0;
	$sth->bind_col(++$column_number, \$cs_id, undef);
	$sth->bind_col(++$column_number, \$cs_name, undef);
	while($sth->fetch){
		$CS_ID_HASH->{$cs_id} = $cs_name;
		$CS_NAME_HASH->{$cs_name} = $cs_id;
	}
	$sth->finish;
	undef $sth;

	$sql = qq|SELECT cdst_id,cdst_name FROM $cdst_tablename|;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$rows = $sth->rows();
	$column_number=0;
	$sth->bind_col(++$column_number, \$cdst_id, undef);
	$sth->bind_col(++$column_number, \$cdst_name, undef);
	while($sth->fetch){
		$CDST_ID_HASH->{$cdst_id} = $cdst_name;
		$CDST_NAME_HASH->{$cdst_name} = $cdst_id;
	}
	$sth->finish;
	undef $sth;

	$sql = qq|SELECT ci_id,cb_id,cdi_id,cs_id,cdst_id FROM $cds_tablename|;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$rows = $sth->rows();
	$column_number=0;
	$sth->bind_col(++$column_number, \$ci_id, undef);
	$sth->bind_col(++$column_number, \$cb_id, undef);
	$sth->bind_col(++$column_number, \$cdi_id, undef);
	$sth->bind_col(++$column_number, \$cs_id, undef);
	$sth->bind_col(++$column_number, \$cdst_id, undef);
	while($sth->fetch){
		$CDS_HASH->{$ci_id}->{$cb_id}->{$cdi_id}->{$cs_id} = $cdst_id;
	}
	$sth->finish;
	undef $sth;

	$sql = qq|SELECT cds_id,md_id,mv_id,mr_id,ci_id,cb_id,cdi_id,cs_id FROM $bds_tablename|;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$rows = $sth->rows();
	$column_number=0;
	$sth->bind_col(++$column_number, \$cds_id, undef);
	$sth->bind_col(++$column_number, \$md_id, undef);
	$sth->bind_col(++$column_number, \$mv_id, undef);
	$sth->bind_col(++$column_number, \$mr_id, undef);
	$sth->bind_col(++$column_number, \$ci_id, undef);
	$sth->bind_col(++$column_number, \$cb_id, undef);
	$sth->bind_col(++$column_number, \$cdi_id, undef);
	$sth->bind_col(++$column_number, \$cs_id, undef);
	while($sth->fetch){
		$BDS_HASH->{$md_id}->{$mv_id}->{$mr_id}->{$ci_id}->{$cb_id}->{$cdi_id}->{$cs_id} = $cds_id;
	}
	$sth->finish;
	undef $sth;



	my $cb_name;
	my $cb_raw_data;
	my $CDI_NAME2ID_HASH = {};

	my $sth_ins_cs = $dbh->prepare(qq|INSERT INTO $cs_tablename (cs_name) VALUES (?) RETURNING cs_id|) or die $dbh->errstr;
	my $sth_ins_bds = $dbh->prepare(qq|INSERT INTO $bds_tablename (md_id,mv_id,mr_id,ci_id,cb_id,cdi_id,cs_id,cdst_id) VALUES (?,?,?,?,?,?,?,?)|) or die $dbh->errstr;



	$sql = qq|
SELECT
  cd.md_id
 ,cd.mv_id
 ,cd.mr_id
 ,cd.ci_id
 ,cd.cb_id
 ,cd.cdi_id
 ,cd.cd_name
FROM
  buildup_data AS cd
ORDER BY
  cd.md_id DESC
 ,cd.mv_id DESC
 ,cd.mr_id DESC
 ,cd.ci_id DESC
 ,cd.cb_id DESC
 ,cd.cdi_id
|;

	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$rows = $sth->rows();
	$column_number=0;
	$sth->bind_col(++$column_number, \$md_id, undef);
	$sth->bind_col(++$column_number, \$mv_id, undef);
	$sth->bind_col(++$column_number, \$mr_id, undef);
	$sth->bind_col(++$column_number, \$ci_id, undef);
	$sth->bind_col(++$column_number, \$cb_id, undef);
	$sth->bind_col(++$column_number, \$cdi_id, undef);
	$sth->bind_col(++$column_number, \$cd_name, undef);
#	$sth->bind_col(++$column_number, \$cd_syn, undef);
#	$sth->bind_col(++$column_number, \$cdi_name, undef);
	my $row = 0;
	my $prev_md_id;
	my $prev_mv_id;
	my $prev_mr_id;
	my $prev_ci_id;
	my $prev_cb_id;
	while($sth->fetch){
		unless(
					defined $prev_md_id
			&&	defined $prev_mv_id
			&&	defined $prev_mr_id
			&&	defined $prev_ci_id
			&&	defined $prev_cb_id
			&&					$prev_md_id eq $md_id
			&&					$prev_mv_id eq $mv_id
			&&					$prev_mr_id eq $mr_id
			&&					$prev_ci_id eq $ci_id
			&&					$prev_cb_id eq $cb_id
		){
			$prev_md_id = $md_id;
			$prev_mv_id = $mv_id;
			$prev_mr_id = $mr_id;
			$prev_ci_id = $ci_id;
			$prev_cb_id = $cb_id;
			say '';
		}
		print sprintf("[%8d/%8d][%2d][%2d][%2d][%2d][%2d][%10d]\r",++$row,$rows,$md_id,$mv_id,$mr_id,$ci_id,$cb_id,$cdi_id);
#		print sprintf("[%7d/%7d][%2d][%2d][%10d][%s][%s]\n",++$row,$rows,$ci_id,$cb_id,$cdi_id,$cd_name,defined $cd_syn ? $cd_syn : '');
#		print sprintf("[%7d/%7d]\n",++$row,$rows);


		next if(
					exists	$BDS_HASH->{$md_id}
			&&	defined	$BDS_HASH->{$md_id}
			&&	ref			$BDS_HASH->{$md_id} eq 'HASH'
			&&	exists	$BDS_HASH->{$md_id}->{$mv_id}
			&&	defined	$BDS_HASH->{$md_id}->{$mv_id}
			&&	ref			$BDS_HASH->{$md_id}->{$mv_id} eq 'HASH'
			&&	exists	$BDS_HASH->{$md_id}->{$mv_id}->{$mr_id}
			&&	defined	$BDS_HASH->{$md_id}->{$mv_id}->{$mr_id}
			&&	ref			$BDS_HASH->{$md_id}->{$mv_id}->{$mr_id} eq 'HASH'
			&&	exists	$BDS_HASH->{$md_id}->{$mv_id}->{$mr_id}->{$ci_id}
			&&	defined	$BDS_HASH->{$md_id}->{$mv_id}->{$mr_id}->{$ci_id}
			&&	ref			$BDS_HASH->{$md_id}->{$mv_id}->{$mr_id}->{$ci_id} eq 'HASH'
			&&	exists	$BDS_HASH->{$md_id}->{$mv_id}->{$mr_id}->{$ci_id}->{$cb_id}
			&&	defined	$BDS_HASH->{$md_id}->{$mv_id}->{$mr_id}->{$ci_id}->{$cb_id}
			&&	ref			$BDS_HASH->{$md_id}->{$mv_id}->{$mr_id}->{$ci_id}->{$cb_id} eq 'HASH'
			&&	exists	$BDS_HASH->{$md_id}->{$mv_id}->{$mr_id}->{$ci_id}->{$cb_id}->{$cdi_id}
			&&	defined	$BDS_HASH->{$md_id}->{$mv_id}->{$mr_id}->{$ci_id}->{$cb_id}->{$cdi_id}
			&&	ref			$BDS_HASH->{$md_id}->{$mv_id}->{$mr_id}->{$ci_id}->{$cb_id}->{$cdi_id}
		);

		unless(
					exists	$CDS_HASH->{$ci_id}
			&&	defined	$CDS_HASH->{$ci_id}
			&&	ref			$CDS_HASH->{$ci_id}  eq 'HASH'
			&&	exists	$CDS_HASH->{$ci_id}->{$cb_id}
			&&	defined	$CDS_HASH->{$ci_id}->{$cb_id}
			&&	ref			$CDS_HASH->{$ci_id}->{$cb_id}  eq 'HASH'
			&&	exists	$CDS_HASH->{$ci_id}->{$cb_id}->{$cdi_id}
			&&	defined	$CDS_HASH->{$ci_id}->{$cb_id}->{$cdi_id}
			&&	ref			$CDS_HASH->{$ci_id}->{$cb_id}->{$cdi_id}  eq 'HASH'
		){
			if(defined $cd_name && length $cd_name){
				$cd_name =~ s/\s+/ /g;
				$cd_name =~ s/^\s+//g;
				$cd_name =~ s/\s+$//g;
				unless(exists $CS_NAME_HASH->{$cd_name} && defined $CS_NAME_HASH->{$cd_name}){
					$sth_ins_cs->execute($cd_name) or die $dbh->errstr;
					$column_number=0;
					$sth_ins_cs->bind_col(++$column_number, \$cs_id, undef);
					$sth_ins_cs->fetch;
					$sth_ins_cs->finish;
					$CS_ID_HASH->{$cs_id} = $cd_name;
					$CS_NAME_HASH->{$cd_name} = $cs_id;
				}
				else{
					$cs_id = $CS_NAME_HASH->{$cd_name};
				}
				
				$sth_ins_bds->execute($md_id,$mv_id,$mr_id,$ci_id,$cb_id,$cdi_id,$cs_id,$CDST_NAME_HASH->{'name'}) or die $dbh->errstr;
				$sth_ins_bds->finish;
				$BDS_HASH->{$md_id}->{$mv_id}->{$mr_id}->{$ci_id}->{$cb_id}->{$cdi_id}->{$cs_id} = undef;
			}
		}
		else{
			foreach my $cs_id (sort {$a <=> $b} keys(%{$CDS_HASH->{$ci_id}->{$cb_id}->{$cdi_id}})){
				my $cdst_id = $CDS_HASH->{$ci_id}->{$cb_id}->{$cdi_id}->{$cs_id};
				$sth_ins_bds->execute($md_id,$mv_id,$mr_id,$ci_id,$cb_id,$cdi_id,$cs_id,$cdst_id) or die $dbh->errstr;
				$sth_ins_bds->finish;
				$BDS_HASH->{$md_id}->{$mv_id}->{$mr_id}->{$ci_id}->{$cb_id}->{$cdi_id}->{$cs_id} = undef;
			}
		}

	}
	$sth->finish;
	undef $sth;




}

#	$dbh->commit();
};
if($@){
	print $@,"\n";
#	$dbh->rollback;
}
#$dbh->{'AutoCommit'} = 1;
#$dbh->{'RaiseError'} = 0;

#print STDERR __LINE__.':ANALYZE;'."\n";
#$dbh->do(qq|ANALYZE;|) or die $!;

