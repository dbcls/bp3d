#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

#my $val = "18_Unclassified";
#$val =~ s/^(\d+).+$/$1/g;
#say sprintf("%d",($val-0));
#exit;

use JSON::XS;
use DBD::Pg;
use File::Spec::Functions qw(abs2rel rel2abs catdir catfile splitdir);
use IO::Compress::Gzip; # qw(gzip $GzipError) ;

use Getopt::Long qw(:config posix_default no_ignore_case gnu_compat);
my $config = {
	db => 'bp3d',
	host => '127.0.0.1',
	port => '8543'
};
&Getopt::Long::GetOptions($config,qw/
	db|d=s
	host|h=s
	port|p=s
	verbose|v
	force-link|fl
	verbose|v
	target|t=s@
	version|v=s@
	lexicalsuper
	lexicalsuper-exclude-words
/) or exit 1;

$ENV{'AG_DB_NAME'} = $config->{'db'};
$ENV{'AG_DB_HOST'} = $config->{'host'};
$ENV{'AG_DB_PORT'} = $config->{'port'};

use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'..','cgi_lib');
use BITS::Config;
require "webgl_common.pl";
use cgi_lib::common;
use BITS::VTK;

#if(exists $config->{'lexicalsuper'} && defined $config->{'lexicalsuper'} && $config->{'lexicalsuper'}){
#	&cgi_lib::common::message($config);
#}
#exit;


our $COLORGROUP2COLOR;
our $unclassified_group_id;
our $unclassified_group_name;
our $unclassified_group_color;

my $base_path;
my $file_prefix;
BEGIN{
	my($name,$dir,$ext) = &File::Basename::fileparse($0, qr/\..*$/);
	$name =~ s/^04_make_//g;
	$base_path = &catdir($FindBin::Bin,'..','htdocs','renderer_file');
	&File::Path::make_path($base_path,{chmod => 0700}) unless(-e $base_path);
	$file_prefix = &catdir($base_path,$name);
}

my $dbh = &get_dbh();
eval{
	my $sql;
	my $sth;
	my $column_number;

	my @VERSION;
	my %VERSION_HASH;
	my $md_id;
	my $mv_id;
	my $mr_id;
	my $ci_id;
	my $cb_id;
	my $mr_version;
	my $mv_name_e;
	my $mv_order;
	my $mr_order;
	my $mv_port;

	$sql = qq|
select
  mr.md_id
 ,mr.mv_id
 ,mr.mr_id
 ,mv.ci_id
 ,mv.cb_id
 ,mr.mr_version
 ,mv.mv_name_e
 ,mv.mv_order
 ,mr.mr_order
 ,mv.mv_port
from
  model_revision as mr
left join model_version as mv on mv.md_id=mr.md_id and mv.mv_id=mr.mv_id
left join model as md on md.md_id=mr.md_id
where
|;

	if(exists $config->{'version'} && defined $config->{'version'}){
		$sql .= sprintf(q|mr.mr_version in ('%s')|,join(q|','|,@{$config->{'version'}}));
	}
	else{
		$sql .= qq|
 mr.mr_use and
-- mv.mv_publish and
 mv.mv_use and
 mv.mv_frozen and
 md.md_use
|;
	}

	$sql .= qq|
order by
 mv.mv_order,
 mr.mr_order
|;

	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$column_number = 0;
	$sth->bind_col(++$column_number, \$md_id, undef);
	$sth->bind_col(++$column_number, \$mv_id, undef);
	$sth->bind_col(++$column_number, \$mr_id, undef);
	$sth->bind_col(++$column_number, \$ci_id, undef);
	$sth->bind_col(++$column_number, \$cb_id, undef);
	$sth->bind_col(++$column_number, \$mr_version, undef);
	$sth->bind_col(++$column_number, \$mv_name_e, undef);
	$sth->bind_col(++$column_number, \$mv_order, undef);
	$sth->bind_col(++$column_number, \$mr_order, undef);
	$sth->bind_col(++$column_number, \$mv_port, undef);
	while($sth->fetch){
		push(@VERSION, $mv_name_e);
		$VERSION_HASH{$mv_name_e} = {};

		$VERSION_HASH{$mv_name_e}->{&BITS::Config::VERSION_STRING_FIELD_ID()} = $mv_name_e;
		$VERSION_HASH{$mv_name_e}->{&BITS::Config::VERSION_ORDER_FIELD_ID()} = $mv_order;
		$VERSION_HASH{$mv_name_e}->{&BITS::Config::VERSION_PORT_FIELD_ID()} = $mv_port;
		$VERSION_HASH{$mv_name_e}->{&BITS::Config::RENDERER_VERSION_STRING_FIELD_ID()} = $mr_version;

		$VERSION_HASH{$mv_name_e}->{&BITS::Config::MODEL_DATA_FIELD_ID()} = $md_id;
		$VERSION_HASH{$mv_name_e}->{&BITS::Config::MODEL_VERSION_DATA_FIELD_ID()} = $mv_id;
		$VERSION_HASH{$mv_name_e}->{&BITS::Config::MODEL_REVISION_DATA_FIELD_ID()} = $mr_id;
		$VERSION_HASH{$mv_name_e}->{&BITS::Config::CONCEPT_INFO_DATA_FIELD_ID()} = $ci_id;
		$VERSION_HASH{$mv_name_e}->{&BITS::Config::CONCEPT_BUILD_DATA_FIELD_ID()} = $cb_id;

		$VERSION_HASH{$mr_version} = $mv_name_e;
	}
	$sth->finish;
	undef $sth;

	&cgi_lib::common::message(\%VERSION_HASH);
	&cgi_lib::common::message(scalar @VERSION);

	my $json_file = qq|${file_prefix}_ext.json|;
#	unless(-e $json_file && -f $json_file && -s $json_file){
		&cgi_lib::common::message($json_file);
		&cgi_lib::common::writeFileJSON($json_file,\%VERSION_HASH,1);
#	}

	$json_file = qq|$file_prefix.json|;
	my($name,$dir,$ext) = &File::Basename::fileparse($json_file,qw/.json/);
#	unless(-e $json_file && -f $json_file && -s $json_file){
		&cgi_lib::common::message($json_file);
		&cgi_lib::common::writeFileJSON($json_file,\%VERSION_HASH,0);

#		my($name,$dir,$ext) = &File::Basename::fileparse($json_file,qw/.json/);
		my $gz_file = &catfile($dir,qq|$name.jgz|);
		unlink $gz_file if(-e $gz_file && -f $gz_file);
#	&IO::Compress::Gzip::gzip( $json_file => $gz_file, Level => IO::Compress::Gzip::Z_BEST_COMPRESSION ) or die "gzip failed: $IO::Compress::Gzip::GzipError\n";
#	}
};
if($@){
	&cgi_lib::common::message($@);
}

exit;
