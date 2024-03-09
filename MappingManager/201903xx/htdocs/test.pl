#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

say join(',',split('','?'x5));

=pod
use JSON::XS;
use File::Basename;
use Cwd qw(abs_path);
use File::Spec::Functions qw(abs2rel rel2abs catdir catfile splitdir);
use CGI;
use CGI::Carp qw(fatalsToBrowser);
#use CGI::Carp::DebugScreen ( debug => 1 );
use Data::Dumper;
use DBD::Pg;
use POSIX;
use List::Util;
use Hash::Merge;
use Time::HiRes;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;

use BITS::Config;
use BITS::VTK;
use BITS::Voxel;
use BITS::ConceptArtMapModified;

use obj2deci;
require "webgl_common.pl";
use cgi_lib::common;
use AG::login;
use BITS::ConceptArtMapModified;

#my $is_subclass_cdi_name = qr/^(.+)\-([LRPS])([0-9]*)$/;
my $is_subclass_cdi_name = qr/^(.+)\-(L|R|P|S[1-9][0-9]{0,1})$/;

#my $cdi_name = 'FMA53135-R';
my $cdi_name = 'FMA53135-S9';
my $cdi_pname;
my $cmp_abbr;
my $cmp_number;
#if($cdi_name =~ /^(.+)\-([LRPS])([0-9]*)$/){
if($cdi_name =~ /$is_subclass_cdi_name/){
	$cdi_pname = $1;
	$cmp_abbr = $2;
	$cmp_number = $3;
}

&cgi_lib::common::message($cdi_pname);
&cgi_lib::common::message($cmp_abbr);
&cgi_lib::common::message($cmp_number);
=cut

my $test = qq|
SELECT
 cdi.ci_id
 ,cdi.cdi_name
-- ,cdip.cdi_id AS cdi_pid
-- ,cdip.cdi_name AS cdi_pname
FROM
 concept_art_map AS cm
LEFT JOIN
 concept_data_info AS cdi ON cm.ci_id=cdi.ci_id AND cm.cdi_id=cdi.cdi_id
LEFT JOIN
 concept_data_info AS cdip ON cm.ci_id=cdip.ci_id AND cdip.cdi_name=regexp_replace(cdi.cdi_name, '^(FMA[0-9]+).*\$', '\\\\1')
LEFT JOIN
 concept_data AS cd ON cd.ci_id=cdip.ci_id AND cd.cdi_id=cdip.cdi_id
WHERE
 cdi.is_user_data
 AND cm.cm_use
 AND cm.cm_delcause IS NULL
 AND cd.ci_id=1
 AND cd.cb_id=13
GROUP BY
 cdi.ci_id
 ,cdi.cdi_name
-- ,cdip.cdi_id
-- ,cdip.cdi_name
|;
say $test;
