#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use File::Basename;
use File::Spec::Functions qw(catdir catfile);
use JSON::XS;

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI::Cookie;

use Data::Dumper;
$Data::Dumper::Indent = 1;
$Data::Dumper::Sortkeys = 1;

use Cwd;
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'API'),&Cwd::abs_path(&catdir($FindBin::Bin,'..','..','ag-common','lib'));
use cgi_lib::common;

use constant VIEW_PREFIX => qq|reference_|;

require "common.pl";
require "common_db.pl";

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);
&checkXSS(\%FORM);

my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0, qr/\..*$/);
my $log_filename = $cgi_name;
$log_filename .= qq|.$FORM{'type'}| if(exists $FORM{'type'} && defined $FORM{'type'} && length $FORM{'type'});
my $LOG = &cgi_lib::common::getLogFH(\%FORM,\%COOKIE,$log_filename);

&setDefParams(\%FORM,\%COOKIE);
&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);

my $RTN = {
	success => JSON::XS::true,
	msg => undef
};

unless(exists $FORM{'rep_ids'} && defined $FORM{'rep_ids'} && length $FORM{'rep_ids'}){
	&cgi_lib::common::printContentJSON($RTN,\%FORM);
	exit;
}
my $rep_ids = &cgi_lib::common::decodeJSON($FORM{'rep_ids'});
unless(defined $rep_ids && ref $rep_ids eq 'ARRAY'){
	&cgi_lib::common::printContentJSON($RTN,\%FORM);
	exit;
}
eval{
	my %rep_ids_hash = map {$_->{'rep_id'} => $_} @$rep_ids;
	my %art_hash;

	print $LOG __LINE__.':%FORM='.&Data::Dumper::Dumper(\%FORM);

#	my $sql_rep_art = sprintf(qq|select rep_art.rep_id,ci_id,cb_id,md_id,mv_id,rep.rep_depth,art_id,art_hist_serial from representation_art as rep_art LEFT JOIN (select rep_id,ci_id,cb_id,md_id,mv_id,rep_depth from representation) as rep on rep.rep_id=rep_art.rep_id WHERE rep_art.rep_id in ('%s') ORDER BY rep.rep_depth|,join("','",map {$_->{'rep_id'}} @$rep_ids));
	my $sql_rep_art = sprintf(qq|select rep_art.rep_id,ci_id,cb_id,md_id,mv_id,rep.rep_depth,art_id,art_hist_serial from representation_art as rep_art LEFT JOIN (select rep_id,ci_id,cb_id,md_id,mv_id,rdt_depth as rep_depth from renderer_tree) as rep on rep.rep_id=rep_art.rep_id WHERE rep_art.rep_id in ('%s') ORDER BY rep.rep_depth|,join("','",map {$_->{'rep_id'}} @$rep_ids));
	say $LOG __LINE__.':$sql_rep_art='.$sql_rep_art;
	my $sth_rep_art = $dbh->prepare($sql_rep_art) or die $dbh->errstr;
	$sth_rep_art->execute() or die $dbh->errstr;
	my $column_number = 0;
	my $rep_id;
	my $ci_id;
	my $cb_id;
	my $md_id;
	my $mv_id;
	my $rep_depth;
	my $art_id;
	my $art_hist_serial;
	$sth_rep_art->bind_col(++$column_number, \$rep_id, undef);
	$sth_rep_art->bind_col(++$column_number, \$ci_id, undef);
	$sth_rep_art->bind_col(++$column_number, \$cb_id, undef);
	$sth_rep_art->bind_col(++$column_number, \$md_id, undef);
	$sth_rep_art->bind_col(++$column_number, \$mv_id, undef);
	$sth_rep_art->bind_col(++$column_number, \$rep_depth, undef);
	$sth_rep_art->bind_col(++$column_number, \$art_id, undef);
	$sth_rep_art->bind_col(++$column_number, \$art_hist_serial, undef);
	while($sth_rep_art->fetch){
		$art_hash{$art_id} = {
			exclude => $rep_ids_hash{$rep_id}->{'exclude'},
			opacity => $rep_ids_hash{$rep_id}->{'opacity'}
		};
	}
	$sth_rep_art->finish;
	undef $sth_rep_art;
	print $LOG __LINE__.':%art_hash='.&Data::Dumper::Dumper(\%art_hash);

	my @art_ids = grep {!$art_hash{$_}->{'exclude'} && $art_hash{$_}->{'opacity'}-0>0} keys(%art_hash);
	print $LOG __LINE__.':@art_ids='.&Data::Dumper::Dumper(\@art_ids);

	if(
		scalar @art_ids &&
		defined $ci_id &&
		defined $cb_id &&
		defined $md_id &&
		defined $mv_id
	){
		my $sql_cm = sprintf(qq|select distinct cdi_id from (select * from concept_art_map where (ci_id,cb_id,md_id,mv_id,mr_id,cdi_id) in (select ci_id,cb_id,md_id,mv_id,max(mr_id),cdi_id from concept_art_map group by ci_id,cb_id,md_id,mv_id,cdi_id)) as cm WHERE md_id=$md_id AND mv_id=$mv_id AND art_id in ('%s') AND cm_use AND cm_delcause IS NULL|,join("','",@art_ids));
		say $LOG __LINE__.':$sql_cm='.$sql_cm;
		my $sth_cm = $dbh->prepare($sql_cm) or die $dbh->errstr;
		$sth_cm->execute() or die $dbh->errstr;
		$column_number = 0;
		my $cdi_id;
		my @cdi_ids;
		$sth_cm->bind_col(++$column_number, \$cdi_id, undef);
		while($sth_cm->fetch){
			push(@cdi_ids,$cdi_id) if(defined $cdi_id);
		}
		$sth_cm->finish;
		undef $sth_cm;
		print $LOG __LINE__.':@cdi_ids='.&Data::Dumper::Dumper(\@cdi_ids);

		if(scalar @cdi_ids){
			my $sql_rep = sprintf(qq|select distinct rep_id from (select * from representation where (ci_id,cb_id,md_id,mv_id,mr_id,cdi_id) in (select ci_id,cb_id,md_id,mv_id,max(mr_id),cdi_id from representation group by ci_id,cb_id,md_id,mv_id,cdi_id)) as cm WHERE md_id=$md_id AND mv_id=$mv_id AND cdi_id in (%s) AND rep_delcause IS NULL|,join(",",@cdi_ids));
			say $LOG __LINE__.':$sql_rep='.$sql_rep;
			my $sth_rep = $dbh->prepare($sql_rep) or die $dbh->errstr;
			$sth_rep->execute() or die $dbh->errstr;
			$column_number = 0;
			my $rep_id;
			my @rep_ids;
			$sth_rep->bind_col(++$column_number, \$rep_id, undef);
			while($sth_rep->fetch){
				push(@rep_ids,$rep_id) if(defined $rep_id);
			}
			$sth_rep->finish;
			undef $sth_rep;

			$RTN->{'rep_ids'} = \@rep_ids;
			$RTN->{'art_ids'} = \@art_ids;
		}
	}
};
&cgi_lib::common::printContentJSON($RTN,\%FORM);
