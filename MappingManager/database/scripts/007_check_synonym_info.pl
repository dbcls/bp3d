#!/opt/services/ag/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use FindBin;
use File::Path;
use JSON::XS;
use DBD::Pg;
use Clone;

use lib qq|$FindBin::Bin/../../cgi_lib|;

use Getopt::Long qw(:config posix_default no_ignore_case gnu_compat);
my $config = {
	db   => 'currentset_160614',
	host => '127.0.0.1',
	port => '38300',
	ci => 1
};
&Getopt::Long::GetOptions($config,qw/
	db|d=s
	host|h=s
	port|p=s
	ci=i
	cb=i
/) or exit 1;

$ENV{'AG_DB_NAME'} = $config->{'db'};
$ENV{'AG_DB_HOST'} = $config->{'host'};
$ENV{'AG_DB_PORT'} = $config->{'port'};

require "webgl_common.pl";


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

eval{
	my $rows;
	my $column_number;
	my $sql;
	my $sth;
	my $IN;
	my $ci_id = $config->{'ci'};
	my $cb_id = exists $config->{'cb'} && defined $config->{'cb'} ? $config->{'cb'} : undef;
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
	my $cdst_name;
	my $cds_id;
	my $cds_bid;
	my $cds_added;
	my $CS_ID_HASH = {};
	my $CS_NAME_HASH = {};
	my $CS_TYPE_HASH = {};
	my $CDS_HASH = {};

	my $CDI_NAME2ID_HASH = {};
	my $CDI_ID2NAME_HASH = {};
	$sth = $dbh->prepare(qq|SELECT cdi_id,cdi_name FROM concept_data_info WHERE ci_id=?|);
	$sth->execute($ci_id) or die $dbh->errstr;
	$column_number = 0;
	$sth->bind_col(++$column_number, \$cdi_id, undef);
	$sth->bind_col(++$column_number, \$cdi_name, undef);
	while($sth->fetch){
		$CDI_NAME2ID_HASH->{$cdi_name} = $cdi_id;
		$CDI_ID2NAME_HASH->{$cdi_id} = $cdi_name;
	}
	$sth->finish;
	undef $sth;

	my $CDI_SYNONYM_HASH = &get_synonym_from_rawdata($CDI_NAME2ID_HASH,$ci_id,$cb_id);
	die __LINE__ unless(defined $CDI_SYNONYM_HASH && ref $CDI_SYNONYM_HASH eq 'HASH');

	$sql = qq|
SELECT
  cds.cds_id
 ,cds.ci_id
 ,cds.cb_id
 ,cds.cdi_id
 ,cs.cs_id
 ,cs.cs_name
 ,cdst.cdst_name
 ,cds.cds_bid
 ,cds.cds_added
FROM
  concept_data_synonym AS cds
LEFT JOIN concept_synonym AS cs ON cs.cs_id=cds.cs_id
LEFT JOIN concept_data_synonym_type AS cdst ON cdst.cdst_id=cds.cdst_id
WHERE
  cdst.cdst_name='synonym'
  AND cds.ci_id=?
  AND cds.cb_id=?
|;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;

	foreach $ci_id (sort {$b <=> $a} keys(%{$CDI_SYNONYM_HASH})){
		next unless(
					exists	$CDI_SYNONYM_HASH->{$ci_id}
			&&	defined	$CDI_SYNONYM_HASH->{$ci_id}
			&&	ref			$CDI_SYNONYM_HASH->{$ci_id} eq 'HASH'
		);
		foreach $cb_id (sort {$b <=> $a} keys(%{$CDI_SYNONYM_HASH->{$ci_id}})){
			next unless(
						exists	$CDI_SYNONYM_HASH->{$ci_id}->{$cb_id}
				&&	defined	$CDI_SYNONYM_HASH->{$ci_id}->{$cb_id}
				&&	ref			$CDI_SYNONYM_HASH->{$ci_id}->{$cb_id} eq 'HASH'
			);

			$sth->execute($ci_id,$cb_id) or die $dbh->errstr;
			$rows = $sth->rows();
			$column_number=0;
			$sth->bind_col(++$column_number, \$cds_id, undef);
			$sth->bind_col(++$column_number, \$ci_id, undef);
			$sth->bind_col(++$column_number, \$cb_id, undef);
			$sth->bind_col(++$column_number, \$cdi_id, undef);
			$sth->bind_col(++$column_number, \$cs_id, undef);
			$sth->bind_col(++$column_number, \$cs_name, undef);
			$sth->bind_col(++$column_number, \$cdst_name, undef);
			$sth->bind_col(++$column_number, \$cds_bid, undef);
			$sth->bind_col(++$column_number, \$cds_added, undef);
			my $row = 0;
			while($sth->fetch){

#				print sprintf("[%7d/%7d][%2d][%2d][%10d]\r",++$row,$rows,$ci_id,$cb_id,$cdi_id);

				next if(
							exists	$CDI_SYNONYM_HASH->{$ci_id}
					&&	defined	$CDI_SYNONYM_HASH->{$ci_id}
					&&	ref			$CDI_SYNONYM_HASH->{$ci_id} eq 'HASH'
					&&	exists	$CDI_SYNONYM_HASH->{$ci_id}->{$cb_id}
					&&	defined	$CDI_SYNONYM_HASH->{$ci_id}->{$cb_id}
					&&	ref			$CDI_SYNONYM_HASH->{$ci_id}->{$cb_id} eq 'HASH'
					&&	exists	$CDI_SYNONYM_HASH->{$ci_id}->{$cb_id}->{$cdi_id}
					&&	defined	$CDI_SYNONYM_HASH->{$ci_id}->{$cb_id}->{$cdi_id}
					&&	ref			$CDI_SYNONYM_HASH->{$ci_id}->{$cb_id}->{$cdi_id} eq 'HASH'
					&&	exists	$CDI_SYNONYM_HASH->{$ci_id}->{$cb_id}->{$cdi_id}->{$cs_name}
				);

				$CDS_HASH->{$ci_id}->{$cb_id}->{$cdi_id}->{$cs_name} = {
					cds_id => $cds_id,
					cs_id => $cs_id,
					cdst_name => $cdst_name,
					cds_bid => $cds_bid,
					cds_added => $cds_added,
					cdi_name => $CDI_ID2NAME_HASH->{$cdi_id}
				};
			}
			$sth->finish;
		}
	}
	undef $sth;

#	say "";
	&cgi_lib::common::message($CDS_HASH);

};
if($@){
	print $@,"\n";
}
exit;

sub get_synonym_from_rawdata {
	my $CDI_NAME2ID_HASH = shift;
	my $ci_id = shift;
	my $cb_id = shift;

	my @where;
	my @bind_values;

	if(defined $ci_id){
		push(@where, qq|ci_id=?|);
		push(@bind_values, $ci_id);
	}
	if(defined $cb_id){
		push(@where, qq|cb_id=?|);
		push(@bind_values, $cb_id);
	}

	my $cb_name;
	my $cb_raw_data;
	my $column_number = 0;
	my $sql;
	my $sth;
	my $cdi_id;
	my $cdi_name;
	my $CDI_HASH = {};

	my $cs_tablename = 'concept_synonym';
	my $cds_tablename = 'concept_data_synonym';
	my $cdst_tablename = 'concept_data_synonym_type';
	my $rows;
	my $cs_id;
	my $cs_name;
	my $CS_ID_HASH;
	my $CS_NAME_HASH;
	my $cdst_id;
	my $cdst_name;

	my $CDST_ID_HASH;
	my $CDST_NAME_HASH;
	my $cds_id;
	my $CDS_HASH;

	unless(defined $CDI_NAME2ID_HASH){
		$sth = $dbh->prepare(qq|SELECT cdi_id,cdi_name FROM concept_data_info WHERE ci_id=?|);
		$sth->execute($ci_id) or die $dbh->errstr;
		$column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_id, undef);
		$sth->bind_col(++$column_number, \$cdi_name, undef);
		while($sth->fetch){
			$CDI_NAME2ID_HASH->{$cdi_name} = $cdi_id;
		}
		$sth->finish;
		undef $sth;
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
	if(scalar @where){
		$sql .= ' WHERE ' . join(' AND ', @where);
	}
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	if(scalar @bind_values){
		$sth->execute(@bind_values) or die $dbh->errstr;
	}
	else{
		$sth->execute() or die $dbh->errstr;
	}
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

	my $sth_ins_cs = $dbh->prepare(qq|INSERT INTO $cs_tablename (cs_name) VALUES (?) RETURNING cs_id|) or die $dbh->errstr;
	my $sth_ins_cds = $dbh->prepare(qq|INSERT INTO $cds_tablename (ci_id,cb_id,cdi_id,cs_id,cds_order,cdst_id) VALUES (?,?,?,?,?,?)|) or die $dbh->errstr;

	$sql = qq|SELECT ci_id,cb_id,cb_name,cb_raw_data FROM concept_build|;
	if(scalar @where){
		$sql .= ' WHERE ' . join(' AND ', @where);
	}
	$sql .= qq| ORDER BY cb_order|;
	$sth = $dbh->prepare($sql);
	if(scalar @bind_values){
		$sth->execute(@bind_values) or die $dbh->errstr;
	}
	else{
		$sth->execute() or die $dbh->errstr;
	}
	$column_number = 0;
	$sth->bind_col(++$column_number, \$ci_id, undef);
	$sth->bind_col(++$column_number, \$cb_id, undef);
	$sth->bind_col(++$column_number, \$cb_name, undef);
	$sth->bind_col(++$column_number, \$cb_raw_data, { pg_type => DBD::Pg::PG_BYTEA });
	while($sth->fetch){

#		say sprintf("\n[%d][%d][%s]",$ci_id,$cb_id,$cb_name);

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
#						print sprintf("\t[%-10s]\r",$ID);
						if(exists $FMA{'synonym'}){
							if(defined $FMA{'synonym'} && ref $FMA{'synonym'} eq 'ARRAY'){
								my $synonym;
								foreach my $s (@{$FMA{'synonym'}}){
									next unless(defined $s);
									$s =~ s/\s*$//g;
									$s =~ s/^\s*//g;
									$s =~ s/\s+/ /g;
#									$s =~ s/;/:/g;
									next unless(length $s);

									$synonym->{$s} = undef;

									$cs_id = undef;
									unless(exists $CS_NAME_HASH->{$s}){
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
										$sth_ins_cds->execute($ci_id,$cb_id,$cdi_id,$cs_id,0,$CDST_NAME_HASH->{'synonym'}) or die $dbh->errstr;
										$sth_ins_cds->finish;
										$CDS_HASH->{$ci_id}->{$cb_id}->{$cdi_id}->{$cs_id} = undef;
									}

								}
								$CDI_HASH->{$ci_id}->{$cb_id}->{$cdi_id} = &Clone::clone($synonym) if(defined $synonym && ref $synonym eq 'HASH');
							}
						}
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
			elsif(/^(synonym):\s+\"([^\"]+)\"\s+EXACT\s+\[\]$/){
				push(@{$FMA{$1}},$2);
			}
			elsif(/^exact_synonym:\s+\"([^\"]+)\"\s+\[\]$/){#fma_obo.obo
				push(@{$FMA{'synonym'}},$1);
			}
		}
#		last if($cb_id == 24);
	}
	$sth->finish;
	undef $sth;

	return $CDI_HASH;
}

sub getParentFromName {
	my $name = shift;
	my $p_name;
	if($name =~ /.+ of .+/i){
		unless(
			$name !~ /\b(tributary|branch) of .+/i &&
			(
				$name =~ /\b(complex|tree|network|set) of .+/i ||
				$name =~ /\b(disk|valve|ligament|artery|vein|duct|mater|joint) of .+/i ||
				$name =~ /.+ of (Giacomini|Guyon|Carabelli|Clarke|Ecker|Calleja|Schwalbe|Zinn)\b/i
			)
		){
			my @TEMP = split(' of ',$name);
			shift @TEMP;
			$p_name = join(' of ',@TEMP);
		}
	}
	return $p_name;
}
