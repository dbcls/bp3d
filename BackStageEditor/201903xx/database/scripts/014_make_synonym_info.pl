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

	$sql = qq|SELECT tablename FROM pg_tables WHERE tablename=?|;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute($cs_tablename) or die $dbh->errstr;
	$rows = $sth->rows();
	$sth->finish;
	undef $sth;

	&cgi_lib::common::message($rows);
#	if($rows>0){
#		say STDERR sprintf("Table already exists. [%s]",$cds_tablename);
#		exit 1;
#	}
	unless($rows>0){
		$sql=qq|
CREATE TABLE IF NOT EXISTS $cs_tablename (
  cs_id       serial NOT NULL,
  cs_name     text NOT NULL,
--  cs_type     text NOT NULL,
  cs_comment  text,
  cs_delcause text,
  cs_entry    timestamp without time zone DEFAULT now() NOT NULL,
  cs_openid   text DEFAULT 'system'::text NOT NULL,
  CONSTRAINT ${cs_tablename}_pkey PRIMARY KEY(cs_id),
  CONSTRAINT ${cs_tablename}_cs_name_unique UNIQUE (cs_name),
  CONSTRAINT ${cs_tablename}_cs_id_check CHECK ((cs_id > 0)),
  CONSTRAINT ${cs_tablename}_cs_name_check CHECK ((cs_name <> ''::text)),
--  CONSTRAINT ${cs_tablename}_cs_type_check CHECK ((cs_type = 'name'::text OR cs_type = 'synonym'::text)),
  CONSTRAINT ${cs_tablename}_cs_openid_check CHECK ((cs_openid <> ''::text))
);
|;
		$rows = $dbh->do($sql) or die $dbh->errstr;
		&cgi_lib::common::message($rows);
	}


	$sql = qq|SELECT tablename FROM pg_tables WHERE tablename=?|;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute($cdst_tablename) or die $dbh->errstr;
	$rows = $sth->rows();
	$sth->finish;
	undef $sth;

	&cgi_lib::common::message($rows);
	unless($rows>0){
		$sql=qq|
CREATE TABLE IF NOT EXISTS $cdst_tablename (
  cdst_id       serial NOT NULL,
  cdst_name     text NOT NULL,
  cdst_order    integer DEFAULT 0,
  cdst_comment  text,
  cdst_delcause text,
  cdst_entry    timestamp without time zone DEFAULT now() NOT NULL,
  cdst_openid   text DEFAULT 'system'::text NOT NULL,
  CONSTRAINT ${cdst_tablename}_pkey PRIMARY KEY(cdst_id),
  CONSTRAINT ${cdst_tablename}_unique UNIQUE (cdst_name)
);
|;
		$rows = $dbh->do($sql) or die $dbh->errstr;
		&cgi_lib::common::message($rows);

		$rows = $dbh->do(qq|INSERT INTO $cdst_tablename (cdst_name,cdst_order) VALUES ('name',1)|) or die $dbh->errstr;
		&cgi_lib::common::message($rows);
		$rows = $dbh->do(qq|INSERT INTO $cdst_tablename (cdst_name,cdst_order) VALUES ('synonym',2)|) or die $dbh->errstr;
		&cgi_lib::common::message($rows);
	}

	$sql = qq|SELECT tablename FROM pg_tables WHERE tablename=?|;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute($cds_tablename) or die $dbh->errstr;
	$rows = $sth->rows();
	$sth->finish;
	undef $sth;

	&cgi_lib::common::message($rows);
	unless($rows>0){
		$sql=qq|
CREATE TABLE IF NOT EXISTS $cds_tablename (
  cds_id       serial NOT NULL,
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
  CONSTRAINT ${cds_tablename}_pkey PRIMARY KEY(cds_id),
  CONSTRAINT ${cds_tablename}_unique UNIQUE (ci_id,cb_id,cdi_id,cs_id,cdst_id),
  CONSTRAINT ${cds_tablename}_cds_openid_check CHECK ((cds_openid <> ''::text)),
  FOREIGN KEY ( ci_id ) REFERENCES concept_info ( ci_id ) ON DELETE CASCADE,
  FOREIGN KEY ( ci_id,cb_id ) REFERENCES concept_build ( ci_id,cb_id ) ON DELETE CASCADE,
  FOREIGN KEY ( ci_id,cdi_id ) REFERENCES concept_data_info ( ci_id,cdi_id ) ON DELETE CASCADE,
  FOREIGN KEY ( ci_id,cb_id,cdi_id ) REFERENCES concept_data ( ci_id,cb_id,cdi_id ) ON DELETE CASCADE,
  FOREIGN KEY ( cs_id ) REFERENCES $cs_tablename ( cs_id ) ON DELETE CASCADE,
  FOREIGN KEY ( cds_bid ) REFERENCES $cds_tablename ( cds_id ) ON DELETE CASCADE,
  FOREIGN KEY ( cdst_id ) REFERENCES $cdst_tablename ( cdst_id ) ON DELETE CASCADE
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

	$sql = qq|SELECT cds_id,ci_id,cb_id,cdi_id,cs_id FROM $cds_tablename|;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$rows = $sth->rows();
	$column_number=0;
	$sth->bind_col(++$column_number, \$cds_id, undef);
	$sth->bind_col(++$column_number, \$ci_id, undef);
	$sth->bind_col(++$column_number, \$cb_id, undef);
	$sth->bind_col(++$column_number, \$cdi_id, undef);
	$sth->bind_col(++$column_number, \$cs_id, undef);
	while($sth->fetch){
		$CDS_HASH->{$ci_id}->{$cb_id}->{$cdi_id}->{$cs_id} = $cds_id;
	}
	$sth->finish;
	undef $sth;



	my $cb_name;
	my $cb_raw_data;
	my $CDI_NAME2ID_HASH = {};

	my $sth_ins_cs = $dbh->prepare(qq|INSERT INTO $cs_tablename (cs_name) VALUES (?) RETURNING cs_id|) or die $dbh->errstr;
	my $sth_ins_cds = $dbh->prepare(qq|INSERT INTO $cds_tablename (ci_id,cb_id,cdi_id,cs_id,cdst_id) VALUES (?,?,?,?,?)|) or die $dbh->errstr;
	my $sth_upd_cd = $dbh->prepare(qq|UPDATE concept_data SET cd_name=?,cd_syn=? WHERE ci_id=? AND cb_id=? AND cdi_id=?|);

	$sth = $dbh->prepare(qq|SELECT cdi_id,cdi_name FROM concept_data_info|);
	$sth->execute() or die $dbh->errstr;
	$column_number = 0;
	$sth->bind_col(++$column_number, \$cdi_id, undef);
	$sth->bind_col(++$column_number, \$cdi_name, undef);
	while($sth->fetch){
		$CDI_NAME2ID_HASH->{$cdi_name} = $cdi_id;
	}
	$sth->finish;
	undef $sth;


#	$sth = $dbh->prepare(qq|SELECT ci_id,cb_id,cb_name,cb_raw_data FROM concept_build WHERE cb_use ORDER BY cb_order|);
#	$sth = $dbh->prepare(qq|SELECT ci_id,cb_id,cb_name,cb_raw_data FROM concept_build WHERE cb_id<13 ORDER BY cb_order|);
	$sth = $dbh->prepare(qq|SELECT ci_id,cb_id,cb_name,cb_raw_data FROM concept_build ORDER BY cb_order|);
	$sth->execute() or die $dbh->errstr;
	$column_number = 0;
	$sth->bind_col(++$column_number, \$ci_id, undef);
	$sth->bind_col(++$column_number, \$cb_id, undef);
	$sth->bind_col(++$column_number, \$cb_name, undef);
	$sth->bind_col(++$column_number, \$cb_raw_data, { pg_type => DBD::Pg::PG_BYTEA });
	while($sth->fetch){

		say sprintf("\n[%d][%d][%s]",$ci_id,$cb_id,$cb_name);

		my $term = 0;
		my %FMA;
		my $ID;

		foreach (split(/\n/,$cb_raw_data)){
			s/\s*$//g;
			s/^\s*//g;
			if($_ eq ""){
				if($term == 1){
					my $cdi_id;
					if(defined $ID && length $ID){
						$cdi_id = $CDI_NAME2ID_HASH->{$ID} if(exists $CDI_NAME2ID_HASH->{$ID} && defined $CDI_NAME2ID_HASH->{$ID});
					}
					if(defined $cdi_id){
						print sprintf("\t[%-10s]\r",$ID);
						if(exists $FMA{'name'}){
							if(defined $FMA{'name'}){
								$FMA{'name'} =~ s/\s*$//g;
								$FMA{'name'} =~ s/^\s*//g;
								$FMA{'name'} =~ s/\s+/ /g;
								unless(length $FMA{'name'}){
									delete $FMA{'name'};
								}
								else{
									unless(exists $CS_NAME_HASH->{$FMA{'name'}} && defined $CS_NAME_HASH->{$FMA{'name'}}){
										$sth_ins_cs->execute($FMA{'name'}) or die $dbh->errstr;
										$column_number=0;
										$sth_ins_cs->bind_col(++$column_number, \$cs_id, undef);
										$sth_ins_cs->fetch;
										$sth_ins_cs->finish;
										$CS_ID_HASH->{$cs_id} = $FMA{'name'};
										$CS_NAME_HASH->{$FMA{'name'}} = $cs_id;
									}
									else{
										$cs_id = $CS_NAME_HASH->{$FMA{'name'}};
									}
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
										&&	exists	$CDS_HASH->{$ci_id}->{$cb_id}->{$cdi_id}->{$cs_id}
									){
										$sth_ins_cds->execute($ci_id,$cb_id,$cdi_id,$cs_id,$CDST_NAME_HASH->{'name'}) or die $dbh->errstr;
										$sth_ins_cds->finish;
										$CDS_HASH->{$ci_id}->{$cb_id}->{$cdi_id}->{$cs_id} = undef;
									}
								}
							}else{
								delete $FMA{'name'};
							}
						}
						if(exists $FMA{'synonym'}){
							if(defined $FMA{'synonym'} && ref $FMA{'synonym'} eq 'ARRAY'){
								my @synonym;
								foreach my $s (@{$FMA{'synonym'}}){
									next unless(defined $s);
									$s =~ s/\s*$//g;
									$s =~ s/^\s*//g;
									$s =~ s/\s+/ /g;
									next unless(length $s);
									push(@synonym, $s);

									unless(exists $CS_NAME_HASH->{$s} && defined $CS_NAME_HASH->{$s}){
										$sth_ins_cs->execute($s) or die $dbh->errstr;
										$column_number=0;
										$sth_ins_cs->bind_col(++$column_number, \$cs_id, undef);
										$sth_ins_cs->fetch;
										$sth_ins_cs->finish;
										$CS_ID_HASH->{$cs_id} = $s;
										$CS_NAME_HASH->{$s} = $cs_id;
									}
									else{
										$cs_id = $CS_NAME_HASH->{$s};
									}
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
										&&	exists	$CDS_HASH->{$ci_id}->{$cb_id}->{$cdi_id}->{$cs_id}
									){
										$sth_ins_cds->execute($ci_id,$cb_id,$cdi_id,$cs_id,$CDST_NAME_HASH->{'synonym'}) or die $dbh->errstr;
										$sth_ins_cds->finish;
										$CDS_HASH->{$ci_id}->{$cb_id}->{$cdi_id}->{$cs_id} = undef;
									}


								}
								delete $FMA{'synonym'};
								push(@{$FMA{'synonym'}},@synonym) if(scalar @synonym);
							}else{
								delete $FMA{'synonym'};
							}
						}
						my $name    = exists $FMA{'name'}    ? $FMA{'name'}    : undef;
						my $synonym = exists $FMA{'synonym'} ? join(';',@{$FMA{'synonym'}}) : undef;

						$sth_upd_cd->execute($name,$synonym,$ci_id,$cb_id,$cdi_id) or die $dbh->errstr;
						$sth_upd_cd->finish;
					}
				}
				$term = 0;
				undef $ID;
				undef %FMA;
				next;
			}
			$term = 1 if(/^\[Term\]$/);
			next if($term == 0);

			if(/^id:\s+([A-Z]{2,3}):([0-9]+)$/){
				$ID = "$1$2";
			}
			elsif(/^(name):\s+(\S+.*)$/){
				$FMA{$1} = $2;
			}
			elsif(/^(synonym):\s+\"([^\"]+)\"\s+EXACT\s+\[\]$/){
				push(@{$FMA{$1}},$2);
			}
			elsif(/^exact_synonym:\s+\"([^\"]+)\"\s+\[\]$/){#fma_obo.obo
				push(@{$FMA{'synonym'}},$1);
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

