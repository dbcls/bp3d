#!/bp3d/local/perl/bin/perl

#
# bp3d_manage_new��
#
# current判定スクリプト
#

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use Clone;
use FindBin;
use File::Spec::Functions qw(catdir);
#use lib $FindBin::Bin,&catdir($FindBin::Bin,'..','..','cgi_lib'),&catdir($FindBin::Bin,'..','..','..','cgi_lib'),,&catdir($FindBin::Bin,'..','..','..','..','..','ag-common','lib');;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'..','cgi_lib'),,&catdir($FindBin::Bin,'..','..','..','ag-common','lib');;

use BITS::Config;

use constant {
	DEBUG => 0,
};

use Getopt::Long qw(:config posix_default no_ignore_case gnu_compat);
my $config = {
	db   => exists $ENV{'AG_DB_NAME'} && defined $ENV{'AG_DB_NAME'} ? $ENV{'AG_DB_NAME'} : 'bp3d',
	host => exists $ENV{'AG_DB_HOST'} && defined $ENV{'AG_DB_HOST'} ? $ENV{'AG_DB_HOST'} : '127.0.0.1',
	port => exists $ENV{'AG_DB_PORT'} && defined $ENV{'AG_DB_PORT'} ? $ENV{'AG_DB_PORT'} : '8543',
};
&Getopt::Long::GetOptions($config,qw/
	db|d=s
	host|h=s
	port|p=s
/) or exit 1;

$ENV{'AG_DB_HOST'} = $config->{'host'};
$ENV{'AG_DB_PORT'} = $config->{'port'};
$ENV{'AG_DB_NAME'} = $config->{'db'};

require "webgl_common.pl";
use cgi_lib::common;
use BITS::ConceptArtMapModified;
use BITS::ConceptArtMapPart;

my $dbh = &get_dbh();

#die;

my $sql;
my $sth;
my $column_number;

$dbh->do(qq|ALTER TABLE concept_art_map DISABLE TRIGGER USER;|) or die $dbh->errstr;
$dbh->do(qq|ALTER TABLE history_concept_art_map DISABLE TRIGGER USER;|) or die $dbh->errstr;

$dbh->{'AutoCommit'} = 0;
$dbh->{'RaiseError'} = 1;
eval{

	my $LOG;

	my $ci_id;
	my $cb_id;
	my $md_id;
	my $mv_id;
	my $mr_id;

	my $cdi_id;
	my $cdi_name;
	my $cdi_name_e;

	my $VERSION;
	my $CONCEPT;
	$sth = $dbh->prepare(qq|select md_id from model where md_use and md_delcause is null|) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$column_number = 0;
	$sth->bind_col(++$column_number, \$md_id, undef);
	while($sth->fetch){
		next unless(defined $md_id);
		$VERSION->{$md_id} = {};
	}
	$sth->finish;
	undef $sth;

	$sth = $dbh->prepare(qq|select mv_id,ci_id,cb_id from model_version where mv_use and mv_delcause is null and md_id=?|) or die $dbh->errstr;
	foreach $md_id (keys(%{$VERSION})){
		$sth->execute($md_id) or die $dbh->errstr;
		$column_number = 0;
		$sth->bind_col(++$column_number, \$mv_id, undef);
		$sth->bind_col(++$column_number, \$ci_id, undef);
		$sth->bind_col(++$column_number, \$cb_id, undef);
		while($sth->fetch){
			next unless(defined $mv_id);
			$VERSION->{$md_id}->{$mv_id} = {};
			$CONCEPT->{$md_id}->{$mv_id} = {
				ci_id => $ci_id,
				cb_id => $cb_id
			};
		}
		$sth->finish;
	}
	undef $sth;

	$sth = $dbh->prepare(qq|select mr_id from model_revision where mr_use and mr_delcause is null and md_id=? and mv_id=?|) or die $dbh->errstr;
	foreach $md_id (keys(%{$VERSION})){
		foreach $mv_id (keys(%{$VERSION->{$md_id}})){
			$sth->execute($md_id,$mv_id) or die $dbh->errstr;
			$column_number = 0;
			$sth->bind_col(++$column_number, \$mr_id, undef);
			while($sth->fetch){
				next unless(defined $mr_id);
				$VERSION->{$md_id}->{$mv_id}->{$mr_id} = undef;
			}
			$sth->finish;
		}
	}
	undef $sth;

	my $USE_VERSION;
	$sth = $dbh->prepare(qq|select md_id,mv_id,mr_id from buildup_concept_part group by md_id,mv_id,mr_id|) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$column_number = 0;
	$sth->bind_col(++$column_number, \$md_id, undef);
	$sth->bind_col(++$column_number, \$mv_id, undef);
	$sth->bind_col(++$column_number, \$mr_id, undef);
	while($sth->fetch){
		next unless(defined $mr_id);
		$USE_VERSION->{$md_id}->{$mv_id}->{$mr_id} = undef;
	}
	$sth->finish;
	undef $sth;


#	&cgi_lib::common::message(scalar keys(%{$NAME2CDI}));
#	&cgi_lib::common::message($BITS::ConceptArtMapPart::is_subclass_cdi_name);
#	&cgi_lib::common::message($BITS::ConceptArtMapPart::is_subclass_abbr_LR);

	my $CDI2NAME;
	my $CDI2NAME_E;
	my $NAME2CDI;

	foreach $md_id (sort {$b <=> $a} keys(%{$VERSION})){
		foreach $mv_id (sort {$b <=> $a} keys(%{$VERSION->{$md_id}})){
			$ci_id = $CONCEPT->{$md_id}->{$mv_id}->{'ci_id'};
			$cb_id = $CONCEPT->{$md_id}->{$mv_id}->{'cb_id'};

			unless(exists $NAME2CDI->{$ci_id}){
				$sth = $dbh->prepare(qq|select cdi_id,cdi_name,cdi_name_e from concept_data_info where ci_id=$ci_id|) or die $dbh->errstr;
				$sth->execute() or die $dbh->errstr;
				$column_number = 0;
				$sth->bind_col(++$column_number, \$cdi_id, undef);
				$sth->bind_col(++$column_number, \$cdi_name, undef);
				$sth->bind_col(++$column_number, \$cdi_name_e, undef);
				while($sth->fetch){
					next unless(defined $cdi_id && defined $cdi_name && defined $cdi_name_e);
					$CDI2NAME->{$ci_id}->{$cdi_id} = $cdi_name;
					$CDI2NAME_E->{$ci_id}->{$cdi_id} = $cdi_name_e;
					$NAME2CDI->{$ci_id}->{$cdi_name} = $cdi_id;
				}
				$sth->finish;
				undef $sth;
			}

			foreach $mr_id (sort {$b <=> $a} keys(%{$VERSION->{$md_id}->{$mv_id}})){

				next unless(exists $USE_VERSION->{$md_id}->{$mv_id}->{$mr_id});

				foreach $cdi_name (sort {$a cmp $b} keys(%{$NAME2CDI->{$ci_id}})){
					next unless($cdi_name =~ /$BITS::ConceptArtMapPart::is_subclass_cdi_name/);
					my $cdi_pname = $1;
			#		my $cmp_abbr = $2;
					my $cmp_abbr = $3;
			#		&cgi_lib::common::message(sprintf("%s\t%s\t%s",$cdi_name,$cdi_pname,$cmp_abbr));
					next unless($cmp_abbr =~ /$BITS::ConceptArtMapPart::is_subclass_abbr_LR/);
					die __LINE__ unless(exists $NAME2CDI->{$ci_id}->{$cdi_pname});
					my $cdi_pid = $NAME2CDI->{$ci_id}->{$cdi_pname};
					die __LINE__ unless(exists $CDI2NAME_E->{$ci_id}->{$cdi_pid});
					&cgi_lib::common::message(sprintf("%d\t%d\t%d\t%s\t%s\t%s",$md_id,$mv_id,$mr_id,$cdi_name,$cdi_pname,$cmp_abbr));
					&BITS::ConceptArtMapPart::create_subclass(
						dbh => $dbh,
						md_id => $md_id,
						mv_id => $mv_id,
						mr_id => $mr_id,
						ci_id => $ci_id,
						cb_id => $cb_id,
						cdi_name => $cdi_name,
					);
				}
			}
			$dbh->commit();
		}
	}

	$dbh->commit();
#=cut
};
if($@){
	&cgi_lib::common::message($@);
	$dbh->rollback;
}
$dbh->{'AutoCommit'} = 1;
$dbh->{'RaiseError'} = 0;

$dbh->do(qq|ALTER TABLE concept_art_map ENABLE TRIGGER USER;|) or die $dbh->errstr;
$dbh->do(qq|ALTER TABLE history_concept_art_map ENABLE TRIGGER USER;|) or die $dbh->errstr;
