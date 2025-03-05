#!/opt/services/ag/local/perl/bin/perl

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
use Time::HiRes;

use Getopt::Long qw(:config posix_default no_ignore_case gnu_compat);
my $config = {
	db => 'ag_public_1903xx',
	host => '127.0.0.1',
	port => '38300'
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
	mv=i@
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
	$name =~ s/^02_make_//g;
	$base_path = &catdir($FindBin::Bin,'..','htdocs',$name);
	&File::Path::make_path($base_path,{chmod => 0700}) unless(-e $base_path);
	$file_prefix = &catdir($base_path,$name);
}

my $HTDOCS_DIR = &catdir($FindBin::Bin,'..','htdocs');
my $MENU_SEGMENTS_BASE_DIR = &catdir($HTDOCS_DIR,'MENU_SEGMENTS');

#my $MENU_SEGMENTS_DATA;
#my $MENU_SEGMENTS_DATA_FILE = &catdir($FindBin::Bin,'..','htdocs','MENU_SEGMENTS','MENU_SEGMENTS_in_art_file.json');
#if(-e $MENU_SEGMENTS_DATA_FILE && -f $MENU_SEGMENTS_DATA_FILE && -s $MENU_SEGMENTS_DATA_FILE){
#	$MENU_SEGMENTS_DATA = &cgi_lib::common::readFileJSON($MENU_SEGMENTS_DATA_FILE);
#}
my $t = [&Time::HiRes::gettimeofday()];

my $dbh = &get_dbh();
$dbh->{'AutoCommit'} = 0;
$dbh->{'RaiseError'} = 1;
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

	my $cdi_pid;
	my $bul_id;
	my $f_potids;
	my $cdi_pname;
	my $cdi_pname_e;

	my $f_potid;
	my $f_potname;
	my $f_potabbr;
	my $f_order;
	my $f_order_max;
	my %FMA_RELATION_TYPE;

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
	elsif(exists $config->{'mv'} && defined $config->{'mv'}){
		$sql .= sprintf(q|mr.mv_id in (%s)|,join(q|','|,@{$config->{'mv'}}));
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

	#fma_partof_type
	$sql = qq|select f_potid,f_potname,f_potabbr,f_order from fma_partof_type|;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$column_number = 0;
	$sth->bind_col(++$column_number, \$f_potid, undef);
	$sth->bind_col(++$column_number, \$f_potname, undef);
	$sth->bind_col(++$column_number, \$f_potabbr, undef);
	$sth->bind_col(++$column_number, \$f_order, undef);
	while($sth->fetch){
		$FMA_RELATION_TYPE{$f_potid} = {
			f_potid => $f_potid,
			f_potname => $f_potname,
			f_potabbr => $f_potabbr,
			f_order   => $f_order - 0
		};
		unless(defined $f_order_max){
			$f_order_max = $f_order - 0;
		}elsif($f_order_max < $f_order - 0){
			$f_order_max = $f_order - 0;
		}
	}
	$sth->finish;
	undef $sth;

	#lexicalsuper
	my $lexicalsuper;
	if(exists $config->{'lexicalsuper'} && defined $config->{'lexicalsuper'} && $config->{'lexicalsuper'}){
#=pod
	#廃止(2019/11/05)
		my $lexicalsuper_path = &catdir($FindBin::Bin,'lexicalsuper4.12');
		if(-e $lexicalsuper_path && -f $lexicalsuper_path && -r $lexicalsuper_path && -s $lexicalsuper_path){
			open(my $IN, $lexicalsuper_path) or die qq|$! [$lexicalsuper_path]|;
			while(<$IN>){
				chomp;
#				my(undef,$cdi_name,undef,undef,$cdi_pname) = split(/\s*!\s*/);
				my(undef,$cdi_name,$cdi_name_e,$cdi_pname_e,$cdi_pname) = split(/\s*!\s*/);
	#			say sprintf("[%s]\t[%s]",$cdi_name,$cdi_pname);

				if($cdi_name =~ /^FMA:*([0-9]+)$/){
					$cdi_name = $1;
					$cdi_name =~ s/^0//g;
					$cdi_name = 'FMA'.$cdi_name;
				}
				else{
					next;
				}
				if($cdi_pname =~ /^FMA:*([0-9]+)$/){
					$cdi_pname = $1;
					$cdi_pname =~ s/^0//g;
					$cdi_pname = 'FMA'.$cdi_pname;
				}
				else{
					next;
				}
	#			say sprintf("[%s]\t[%s]",$cdi_name,$cdi_pname);

				if(exists $config->{'lexicalsuper-exclude-words'} && ($cdi_name_e =~ /\b(disk|valve|ligament|artery|vein|duct) of/i || $cdi_name_e =~ /.+ of (Giacomini|Guyon|Carabelli|Clarke|Ecker|Calleja|Schwalbe|Zinn)\b/i)){
					say STDERR qq|exclude:[$cdi_name][$cdi_name_e] -> [$cdi_pname][$cdi_pname_e]|;
					next;
				}


				if(defined $lexicalsuper && ref $lexicalsuper eq 'HASH' && exists $lexicalsuper->{$cdi_name}){
					say STDERR sprintf("[WARN] Multiple parents!! child:[%s]\tparent1:[%s]\tparent2:[%s]",$cdi_name,$cdi_pname,$lexicalsuper->{$cdi_name});
				}
				$lexicalsuper->{$cdi_name} = $cdi_pname;
			}
			close($IN);
		}
#=cut
	}
#	exit;


	my $sth_sel_data = $dbh->prepare(qq|select art_data from art_file where art_id=? limit 1|) or die $dbh->errstr;
	my %ART_INFO;

	foreach my $mr_version (@VERSION){
		my $t0 = [&Time::HiRes::gettimeofday()];
		&cgi_lib::common::message($VERSION_HASH{$mr_version});

		my $art_id;
		my $cdi_id;
		my $cdi_name;
		my $cd_name;
		my $cd_name_j;
		my $cd_syn;
		my $cd_def;
		my $cd_taid;
		my $but_pids;
		my $but_cids;
		my $but_cnum;
		my $but_depth;
		my $seg_color;
		my $csg_name;
		my $art_name;
		my $art_ext;
		my $art_timestamp;
		my $art_entry;

		my $art_xmasscenter;
		my $art_ymasscenter;
		my $art_zmasscenter;
		my $art_masscenter_in_self;

		my $arts_id;
		my $arts_name;
		my $artsg_id;
		my $artsg_name;

		my $artl_id;
		my $artl_title;
		my $artl_abbr;
		my $artl_display_title;
		my $artl_prefix;
		my $artc_id;

		my %CD_DATA;
		my %CD_TREE;
		my %CD2ART;
		my $CD2ART_HASH;
		my %CD_IS_ELEMENT;
		my %ART_INFO_VERSION;
		my %CDI_NAME2ID;

#		$VERSION_HASH{$mr_version}->{'fma_orders'} = [];
		$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()} = {};

		$md_id = $VERSION_HASH{$mr_version}->{'md_id'};
		$mv_id = $VERSION_HASH{$mr_version}->{'mv_id'};
		$mr_id = $VERSION_HASH{$mr_version}->{'mr_id'};
		$ci_id = $VERSION_HASH{$mr_version}->{'ci_id'};
		$cb_id = $VERSION_HASH{$mr_version}->{'cb_id'};
=pod
		$sql = qq|
select
 cdi.cdi_id,
 cdi.cdi_name,
 COALESCE(bd.cd_name,cd.cd_name,cdi.cdi_name_e) as cd_name,
 cdi.cdi_name_j as cd_name_j,
 COALESCE(bd.cd_syn,cd.cd_syn,cdi.cdi_syn_e) as cd_syn,
 COALESCE(bd.cd_def,cd.cd_def,cdi.cdi_def_e) as cd_def,
 cdi.cdi_taid as cd_taid,
 COALESCE(bd.seg_color,cd.seg_color) as seg_color,
 COALESCE(bd.csg_name,cd.csg_name) as csg_name
from (
 select * from concept_data_info where ci_id=$ci_id
) as cdi
left join (
 select
  cd.*,
  cs.seg_color,
  csg.csg_name
 from
  concept_data as cd
 left join (
  select seg_id,seg_color,csg_id from concept_segment
 ) as cs on cs.seg_id=cd.seg_id
 left join (
  select csg_id,csg_name from concept_segment_group
 ) as csg on csg.csg_id=cs.csg_id
 where
  cd.ci_id=$ci_id and
  cd.cb_id=$cb_id
) as cd on cd.cdi_id=cdi.cdi_id
left join (
 select
  cd.*,
  cs.seg_color,
  csg.csg_name
 from
  buildup_data as cd
 left join (
  select seg_id,seg_color,csg_id from concept_segment
 ) as cs on cs.seg_id=cd.seg_id
 left join (
  select csg_id,csg_name from concept_segment_group
 ) as csg on csg.csg_id=cs.csg_id
 where
  cd.md_id=$md_id and
  cd.mv_id=$mv_id and
  cd.mr_id=$mr_id
) as bd on bd.cdi_id=cdi.cdi_id
|;
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_id, undef);
		$sth->bind_col(++$column_number, \$cdi_name, undef);
		$sth->bind_col(++$column_number, \$cd_name, undef);
		$sth->bind_col(++$column_number, \$cd_name_j, undef);
		$sth->bind_col(++$column_number, \$cd_syn, undef);
		$sth->bind_col(++$column_number, \$cd_def, undef);
		$sth->bind_col(++$column_number, \$cd_taid, undef);
		$sth->bind_col(++$column_number, \$seg_color, undef);
		$sth->bind_col(++$column_number, \$csg_name, undef);
		while($sth->fetch){
			$CD_DATA{$cdi_id} = {};
			$CD_DATA{$cdi_id}->{&BITS::Config::CONCEPT_DATA_INFO_DATA_FIELD_ID()} = $cdi_id - 0;
			$CD_DATA{$cdi_id}->{&BITS::Config::ID_DATA_FIELD_ID()} = $cdi_name;
			$CD_DATA{$cdi_id}->{&BITS::Config::NAME_DATA_FIELD_ID()} = $cd_name;
			$CD_DATA{$cdi_id}->{&BITS::Config::NAME_J_DATA_FIELD_ID()} = $cd_name_j;
			$CD_DATA{$cdi_id}->{&BITS::Config::SYNONYM_DATA_FIELD_ID()} = $cd_syn;
			$CD_DATA{$cdi_id}->{&BITS::Config::DEFINITION_DATA_FIELD_ID()} = $cd_def;
			$CD_DATA{$cdi_id}->{&BITS::Config::TA_DATA_FIELD_ID()} = defined $cd_taid ? $cd_taid : undef;
			$CD_DATA{$cdi_id}->{&BITS::Config::CONCEPT_DATA_COLOR_DATA_FIELD_ID()} = $seg_color;
			$CD_DATA{$cdi_id}->{&BITS::Config::CONCEPT_DATA_CATEGORY_DATA_FIELD_ID()} = $csg_name;

			$CDI_NAME2ID{$cdi_name} = $cdi_id - 0;
		}
		$sth->finish;
		undef $sth;
		&cgi_lib::common::message(scalar keys(%CDI_NAME2ID));
		&cgi_lib::common::message(sprintf("\ttime=%f",&Time::HiRes::tv_interval($t0)));
=cut
#####
		$sql = qq|
select
 cdi.cdi_id,
 cdi.cdi_name,
 cdi.cdi_name_e AS cd_name,
 cdi.cdi_name_j AS cd_name_j,
 cdi.cdi_syn_e AS cd_syn,
 cdi.cdi_def_e AS cd_def,
 cdi.cdi_taid AS cd_taid
FROM
  concept_data_info AS cdi
WHERE
  ci_id=$ci_id
|;
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_id, undef);
		$sth->bind_col(++$column_number, \$cdi_name, undef);
		$sth->bind_col(++$column_number, \$cd_name, undef);
		$sth->bind_col(++$column_number, \$cd_name_j, undef);
		$sth->bind_col(++$column_number, \$cd_syn, undef);
		$sth->bind_col(++$column_number, \$cd_def, undef);
		$sth->bind_col(++$column_number, \$cd_taid, undef);
		while($sth->fetch){
			$CD_DATA{$cdi_id} = {};
			$CD_DATA{$cdi_id}->{&BITS::Config::CONCEPT_DATA_INFO_DATA_FIELD_ID()} = $cdi_id - 0;
			$CD_DATA{$cdi_id}->{&BITS::Config::ID_DATA_FIELD_ID()} = $cdi_name;
			$CD_DATA{$cdi_id}->{&BITS::Config::NAME_DATA_FIELD_ID()} = $cd_name;
			$CD_DATA{$cdi_id}->{&BITS::Config::NAME_J_DATA_FIELD_ID()} = $cd_name_j;
			$CD_DATA{$cdi_id}->{&BITS::Config::SYNONYM_DATA_FIELD_ID()} = $cd_syn;
			$CD_DATA{$cdi_id}->{&BITS::Config::DEFINITION_DATA_FIELD_ID()} = $cd_def;
			$CD_DATA{$cdi_id}->{&BITS::Config::TA_DATA_FIELD_ID()} = defined $cd_taid ? $cd_taid : undef;

			$CDI_NAME2ID{$cdi_name} = $cdi_id - 0;
		}
		$sth->finish;
		undef $sth;
		&cgi_lib::common::message(scalar keys(%CD_DATA));
		&cgi_lib::common::message(scalar keys(%CDI_NAME2ID));
		&cgi_lib::common::message(sprintf("\ttime=%f",&Time::HiRes::tv_interval($t0)));
####
		$sql = qq|
select
 cd.cdi_id,
 cd.cd_name AS cd_name,
 cd.cd_syn AS cd_syn,
 cd.cd_def AS cd_def,
 cd.seg_color AS seg_color,
 cd.csg_name AS csg_name
from (
 select
  cd.*,
  cs.seg_color,
  csg.csg_name
 from
  concept_data as cd
 left join (
  select seg_id,seg_color,csg_id from concept_segment
 ) as cs on cs.seg_id=cd.seg_id
 left join (
  select csg_id,csg_name from concept_segment_group
 ) as csg on csg.csg_id=cs.csg_id
 where
  cd.ci_id=$ci_id and
  cd.cb_id=$cb_id
) AS cd
|;
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_id, undef);
		$sth->bind_col(++$column_number, \$cd_name, undef);
		$sth->bind_col(++$column_number, \$cd_syn, undef);
		$sth->bind_col(++$column_number, \$cd_def, undef);
		$sth->bind_col(++$column_number, \$seg_color, undef);
		$sth->bind_col(++$column_number, \$csg_name, undef);
		while($sth->fetch){
			$CD_DATA{$cdi_id} = {} unless(exists $CD_DATA{$cdi_id} && defined $CD_DATA{$cdi_id} && ref $CD_DATA{$cdi_id} eq 'HASH');
			$CD_DATA{$cdi_id}->{&BITS::Config::CONCEPT_DATA_INFO_DATA_FIELD_ID()} = $cdi_id - 0;
			$CD_DATA{$cdi_id}->{&BITS::Config::NAME_DATA_FIELD_ID()} = $cd_name;
			$CD_DATA{$cdi_id}->{&BITS::Config::SYNONYM_DATA_FIELD_ID()} = $cd_syn if(defined $cd_syn && length $cd_syn);
			$CD_DATA{$cdi_id}->{&BITS::Config::DEFINITION_DATA_FIELD_ID()} = $cd_def if(defined $cd_def && length $cd_def);
			$CD_DATA{$cdi_id}->{&BITS::Config::CONCEPT_DATA_COLOR_DATA_FIELD_ID()} = $seg_color if(defined $seg_color && length $seg_color);
			$CD_DATA{$cdi_id}->{&BITS::Config::CONCEPT_DATA_CATEGORY_DATA_FIELD_ID()} = $csg_name if(defined $csg_name && length $csg_name);
		}
		$sth->finish;
		undef $sth;
		&cgi_lib::common::message(scalar keys(%CD_DATA));
		&cgi_lib::common::message(sprintf("\ttime=%f",&Time::HiRes::tv_interval($t0)));
####
		$sql = qq|
select
 bd.cdi_id,
 bd.cd_name AS cd_name,
 bd.cd_syn AS cd_syn,
 bd.cd_def AS cd_def,
 bd.seg_color AS seg_color,
 bd.csg_name AS csg_name
FROM (
 select
  cd.*,
  cs.seg_color,
  csg.csg_name
 from
  buildup_data as cd
 left join (
  select seg_id,seg_color,csg_id from concept_segment
 ) as cs on cs.seg_id=cd.seg_id
 left join (
  select csg_id,csg_name from concept_segment_group
 ) as csg on csg.csg_id=cs.csg_id
 where
  cd.md_id=$md_id and
  cd.mv_id=$mv_id and
  cd.mr_id=$mr_id
) AS bd
|;
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_id, undef);
		$sth->bind_col(++$column_number, \$cd_name, undef);
		$sth->bind_col(++$column_number, \$cd_syn, undef);
		$sth->bind_col(++$column_number, \$cd_def, undef);
		$sth->bind_col(++$column_number, \$seg_color, undef);
		$sth->bind_col(++$column_number, \$csg_name, undef);
		while($sth->fetch){
			$CD_DATA{$cdi_id} = {} unless(exists $CD_DATA{$cdi_id} && defined $CD_DATA{$cdi_id} && ref $CD_DATA{$cdi_id} eq 'HASH');
			$CD_DATA{$cdi_id}->{&BITS::Config::CONCEPT_DATA_INFO_DATA_FIELD_ID()} = $cdi_id - 0;
			$CD_DATA{$cdi_id}->{&BITS::Config::NAME_DATA_FIELD_ID()} = $cd_name;
			$CD_DATA{$cdi_id}->{&BITS::Config::SYNONYM_DATA_FIELD_ID()} = $cd_syn if(defined $cd_syn && length $cd_syn);
			$CD_DATA{$cdi_id}->{&BITS::Config::DEFINITION_DATA_FIELD_ID()} = $cd_def if(defined $cd_def && length $cd_def);
			$CD_DATA{$cdi_id}->{&BITS::Config::CONCEPT_DATA_COLOR_DATA_FIELD_ID()} = $seg_color if(defined $seg_color && length $seg_color);
			$CD_DATA{$cdi_id}->{&BITS::Config::CONCEPT_DATA_CATEGORY_DATA_FIELD_ID()} = $csg_name if(defined $csg_name && length $csg_name);
		}
		$sth->finish;
		undef $sth;
		&cgi_lib::common::message(scalar keys(%CD_DATA));
		&cgi_lib::common::message(sprintf("\ttime=%f",&Time::HiRes::tv_interval($t0)));
####

		$sql = qq|
SELECT
 cds.cdi_id,
 cs.cs_name,
 cds_b.cdi_id,
 cs_b.cs_name,
 cds.cds_added
FROM
 buildup_data_synonym AS cds
LEFT JOIN concept_data_synonym_type AS cdst ON cdst.cdst_id=cds.cdst_id
LEFT JOIN concept_synonym AS cs ON cs.cs_id=cds.cs_id
LEFT JOIN buildup_data_synonym AS cds_b ON cds_b.cdst_id=cds.cds_bid
LEFT JOIN concept_synonym AS cs_b ON cs_b.cs_id=cds_b.cs_id
WHERE
     cds.md_id=$md_id
 AND cds.mv_id=$mv_id
 AND cds.mr_id=$mr_id
 AND cdst.cdst_name='synonym'
ORDER BY
 cds.cdi_id,
 cs.cs_name
|;
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		my $cs_name;
		my $cdi_bid;
		my $cs_bname;
		my $cds_added;
		$column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_id, undef);
		$sth->bind_col(++$column_number, \$cs_name, undef);
		$sth->bind_col(++$column_number, \$cdi_bid, undef);
		$sth->bind_col(++$column_number, \$cs_bname, undef);
		$sth->bind_col(++$column_number, \$cds_added, undef);
		while($sth->fetch){
			next unless(exists $CD_DATA{$cdi_id} && defined $CD_DATA{$cdi_id} && ref $CD_DATA{$cdi_id} eq 'HASH');
			my $cds = {};
			$cds->{&BITS::Config::CDS_NAME_DATA_FIELD_ID()} = $cs_name;
			$cds->{&BITS::Config::CDS_ADDED_DATA_FIELD_ID()} = $cds_added ? JSON::XS::true : JSON::XS::false;
			if(defined $cdi_bid && exists $CD_DATA{$cdi_bid} && defined $CD_DATA{$cdi_bid} && ref $CD_DATA{$cdi_bid} eq 'HASH'){
				$cds->{&BITS::Config::CDS_BASE_ID_DATA_FIELD_ID()} = $CD_DATA{$cdi_bid}->{&BITS::Config::NAME_DATA_FIELD_ID()};
				$cds->{&BITS::Config::CDS_BASE_NAME_DATA_FIELD_ID()} = $cs_bname;
			}
			push(@{$CD_DATA{$cdi_id}->{&BITS::Config::CDS_DATA_FIELD_ID()}}, $cds);
		}
		$sth->finish;
		undef $sth;
		&cgi_lib::common::message(sprintf("\ttime=%f",&Time::HiRes::tv_interval($t0)));


		&cgi_lib::common::message(scalar keys(%CD_DATA));
#		&cgi_lib::common::message('CALL system_color()');
		my $SYSTE_COLOR = &system_color($dbh,$md_id,$mv_id,$mr_id,$ci_id,$cb_id);
#		&cgi_lib::common::message('RETURN system_color()');
		if(defined $SYSTE_COLOR && ref $SYSTE_COLOR eq 'HASH' && scalar keys(%$SYSTE_COLOR)){
			&cgi_lib::common::message(scalar keys(%$SYSTE_COLOR));

			foreach my $cdi_id (keys(%CD_DATA)){
				$CD_DATA{$cdi_id}->{&BITS::Config::CONCEPT_DATA_COLOR_DATA_FIELD_ID()} = $unclassified_group_color;
				$CD_DATA{$cdi_id}->{&BITS::Config::SYSTEM_ID_DATA_FIELD_ID()} = $unclassified_group_name;
			}

			foreach my $cdi_id (keys(%$SYSTE_COLOR)){
				unless(exists $CD_DATA{$cdi_id} && defined $CD_DATA{$cdi_id} && ref $CD_DATA{$cdi_id} eq 'HASH'){
					&cgi_lib::common::message("Unknown [$cdi_id]");
					next;
				}
				$CD_DATA{$cdi_id}->{$_} = $SYSTE_COLOR->{$cdi_id}->{$_} for(keys(%{$SYSTE_COLOR->{$cdi_id}}));
			}
		}
		&cgi_lib::common::message(scalar keys(%CD_DATA));
#		&cgi_lib::common::message(\%CD_DATA);
#		die __LINE__;
		&cgi_lib::common::message(sprintf("\ttime=%f",&Time::HiRes::tv_interval($t0)));

		$sql = qq|
select
 cm.cdi_id,
 cm.art_id,
 arti.art_name,
 arti.art_ext,
 EXTRACT(EPOCH FROM arti.art_timestamp) as art_timestamp,
 EXTRACT(EPOCH FROM arti.art_entry) as art_entry
 ,arti.artc_id
from
 concept_art_map as cm

left join (
 select * from art_file_info
) as arti on
 cm.art_id=arti.art_id

where
 cm.cm_use and
 cm.cm_delcause is null and
 (cm.md_id,cm.mv_id,cm.mr_id,cm.cdi_id) in (select md_id,mv_id,max(mr_id),cdi_id from concept_art_map where md_id=$md_id and mv_id=$mv_id and mr_id<=$mr_id group by md_id,mv_id,cdi_id)
|;
#		&cgi_lib::common::message($sql);

		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_id, undef);
		$sth->bind_col(++$column_number, \$art_id, undef);

		$sth->bind_col(++$column_number, \$art_name, undef);
		$sth->bind_col(++$column_number, \$art_ext, undef);
		$sth->bind_col(++$column_number, \$art_timestamp, undef);
		$sth->bind_col(++$column_number, \$art_entry, undef);

		$sth->bind_col(++$column_number, \$artc_id, undef);

#		$sth->bind_col(++$column_number, \$art_xmasscenter, undef);
#		$sth->bind_col(++$column_number, \$art_ymasscenter, undef);
#		$sth->bind_col(++$column_number, \$art_zmasscenter, undef);
#		$sth->bind_col(++$column_number, \$art_masscenter_in_self, undef);

#		$sth->bind_col(++$column_number, \$arts_id, undef);
#		$sth->bind_col(++$column_number, \$arts_name, undef);
#		$sth->bind_col(++$column_number, \$artsg_id, undef);
#		$sth->bind_col(++$column_number, \$artsg_name, undef);

		while($sth->fetch){
			$CD2ART{$cdi_id}->{$art_id} = undef;
			$CD_IS_ELEMENT{$cdi_id} = undef;
			unless(exists $ART_INFO{$art_id}){
				$ART_INFO{$art_id} = {};
				$ART_INFO{$art_id}->{&BITS::Config::OBJ_FILENAME_FIELD_ID()} = $art_name.$art_ext;
				$ART_INFO{$art_id}->{&BITS::Config::OBJ_TIMESTAMP_DATA_FIELD_ID()} = $art_timestamp - 0;

				$ART_INFO{$art_id}->{&BITS::Config::CONCEPT_DATA_COLOR_DATA_FIELD_ID()} = $CD_DATA{$cdi_id}->{&BITS::Config::CONCEPT_DATA_COLOR_DATA_FIELD_ID()};
				$ART_INFO{$art_id}->{&BITS::Config::CONCEPT_DATA_CATEGORY_DATA_FIELD_ID()} = $CD_DATA{$cdi_id}->{&BITS::Config::CONCEPT_DATA_CATEGORY_DATA_FIELD_ID()};
				$ART_INFO{$art_id}->{&BITS::Config::ID_DATA_FIELD_ID()} = $CD_DATA{$cdi_id}->{&BITS::Config::ID_DATA_FIELD_ID()};

				$ART_INFO{$art_id}->{&BITS::Config::OBJ_CONCEPT_ID_DATA_FIELD_ID()} = defined $artc_id ? $artc_id : undef;

#				$ART_INFO{$art_id}->{&BITS::Config::OBJ_X_MASS_CENTER_FIELD_ID()} = $art_xmasscenter - 0;
#				$ART_INFO{$art_id}->{&BITS::Config::OBJ_Y_MASS_CENTER_FIELD_ID()} = $art_ymasscenter - 0;
#				$ART_INFO{$art_id}->{&BITS::Config::OBJ_Z_MASS_CENTER_FIELD_ID()} = $art_zmasscenter - 0;
#				$ART_INFO{$art_id}->{&BITS::Config::OBJ_MASS_CENTER_IN_SELF_FIELD_ID()} = $art_masscenter_in_self - 0 ? JSON::XS::true : JSON::XS::false;

#				$ART_INFO{$art_id}->{&BITS::Config::OBJ_SEGMENT_ID_FIELD_ID()} = defined $arts_id ? $arts_id - 0 : undef;
#				$ART_INFO{$art_id}->{&BITS::Config::OBJ_SEGMENT_NAME_FIELD_ID()} = $arts_name;

#				$ART_INFO{$art_id}->{&BITS::Config::OBJ_SEGMENT_GROUP_ID_FIELD_ID()} = defined $artsg_id ? $artsg_id - 0 : undef;
#				$ART_INFO{$art_id}->{&BITS::Config::OBJ_SEGMENT_GROUP_NAME_FIELD_ID()} = $artsg_name;

				my $file = &catdir($FindBin::Bin,'art_file',$art_id.$art_ext);
				unless(-e $file && -f $file && -s $file){
					my $art_data;
					$sth_sel_data->execute($art_id) or die $dbh->errstr;
					$sth_sel_data->bind_col(1, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
					$sth_sel_data->fetch;
					$sth_sel_data->finish;
					if(defined $art_data && open(my $OBJ,"> $file")){
						flock($OBJ,2);
						binmode($OBJ,':utf8');
						print $OBJ $art_data;
						close($OBJ);
						undef $OBJ;
						utime $art_timestamp,$art_timestamp,$file;
					}
					undef $art_data;
				}
#				my $file_gz = &catdir($FindBin::Bin,'art_file',qq|$art_id.ogz|);
#				unless(-e $file_gz && -f $file_gz && -s $file_gz){
#					&IO::Compress::Gzip::gzip( $file => $file_gz, Level => IO::Compress::Gzip::Z_BEST_COMPRESSION ) or die "gzip failed: $IO::Compress::Gzip::GzipError\n";
#				}
#				my $zopfli = '/opt/services/ag/local/zopfli/zopfli';
#				if(-e $zopfli && -f $zopfli && -x $zopfli){
#					$file_gz = &catdir($FindBin::Bin,'art_file',qq|$art_id.obj.gz|);
#					system(qq|$zopfli $file|) unless(-e $file_gz);
#				}


				my $obj_prop = &BITS::VTK::_getProperties($file);
				$ART_INFO{$art_id}->{&BITS::Config::OBJ_POLYS_FIELD_ID()}  = $obj_prop->{'polys'} - 0;
				$ART_INFO{$art_id}->{&BITS::Config::OBJ_POINTS_FIELD_ID()} = $obj_prop->{'points'} - 0;
#				$ART_INFO{$art_id}->{&BITS::Config::OBJ_VOLUME_FIELD_ID()} = $obj_prop->{'volume'} - 0;

				$ART_INFO{$art_id}->{&BITS::Config::OBJ_X_MIN_FIELD_ID()} = $obj_prop->{'bounds'}->[0] - 0;
				$ART_INFO{$art_id}->{&BITS::Config::OBJ_X_MAX_FIELD_ID()} = $obj_prop->{'bounds'}->[1] - 0;
				$ART_INFO{$art_id}->{&BITS::Config::OBJ_Y_MIN_FIELD_ID()} = $obj_prop->{'bounds'}->[2] - 0;
				$ART_INFO{$art_id}->{&BITS::Config::OBJ_Y_MAX_FIELD_ID()} = $obj_prop->{'bounds'}->[3] - 0;
				$ART_INFO{$art_id}->{&BITS::Config::OBJ_Z_MIN_FIELD_ID()} = $obj_prop->{'bounds'}->[4] - 0;
				$ART_INFO{$art_id}->{&BITS::Config::OBJ_Z_MAX_FIELD_ID()} = $obj_prop->{'bounds'}->[5] - 0;

				$ART_INFO{$art_id}->{&BITS::Config::OBJ_X_CENTER_FIELD_ID()} = $obj_prop->{'centers'}->[0] - 0;
				$ART_INFO{$art_id}->{&BITS::Config::OBJ_Y_CENTER_FIELD_ID()} = $obj_prop->{'centers'}->[1] - 0;
				$ART_INFO{$art_id}->{&BITS::Config::OBJ_Z_CENTER_FIELD_ID()} = $obj_prop->{'centers'}->[2] - 0;

				$ART_INFO{$art_id}->{&BITS::Config::OBJ_X_MASS_CENTER_FIELD_ID()} = $obj_prop->{'centerOfMass'}->[0] - 0;
				$ART_INFO{$art_id}->{&BITS::Config::OBJ_Y_MASS_CENTER_FIELD_ID()} = $obj_prop->{'centerOfMass'}->[1] - 0;
				$ART_INFO{$art_id}->{&BITS::Config::OBJ_Z_MASS_CENTER_FIELD_ID()} = $obj_prop->{'centerOfMass'}->[2] - 0;


#				if(defined $MENU_SEGMENTS_DATA && ref $MENU_SEGMENTS_DATA eq 'HASH' && exists $MENU_SEGMENTS_DATA->{$art_id} && defined $MENU_SEGMENTS_DATA->{$art_id} && ref $MENU_SEGMENTS_DATA->{$art_id} eq 'HASH'){
#					foreach my $segment (keys(%{$MENU_SEGMENTS_DATA->{$art_id}})){
#						if(uc($segment) eq 'CITIES'){
#							foreach my $part (keys(%{$MENU_SEGMENTS_DATA->{$art_id}->{$segment}})){
#								my $hash = $MENU_SEGMENTS_DATA->{$art_id}->{$segment}->{$part};
#								delete $hash->{'all'};
#								$ART_INFO{$art_id}->{&BITS::Config::OBJ_CITIES_FIELD_ID()}->{$part} = $hash;
#							}
#						}
#						elsif(uc($segment) eq 'PREFECTURES'){
#							foreach my $part (keys(%{$MENU_SEGMENTS_DATA->{$art_id}->{$segment}})){
#								my $hash = $MENU_SEGMENTS_DATA->{$art_id}->{$segment}->{$part};
#								delete $hash->{'all'};
#								$ART_INFO{$art_id}->{&BITS::Config::OBJ_PREFECTURES_FIELD_ID()}->{$part} = $hash;
#							}
#						}
#					}
#				}

			}

			#各バージョンで異なる可能性がある為、毎回更新する
			$ART_INFO{$art_id}->{&BITS::Config::CONCEPT_DATA_COLOR_DATA_FIELD_ID()} = $CD_DATA{$cdi_id}->{&BITS::Config::CONCEPT_DATA_COLOR_DATA_FIELD_ID()};
			$ART_INFO{$art_id}->{&BITS::Config::CONCEPT_DATA_CATEGORY_DATA_FIELD_ID()} = $CD_DATA{$cdi_id}->{&BITS::Config::CONCEPT_DATA_CATEGORY_DATA_FIELD_ID()};
			$ART_INFO{$art_id}->{&BITS::Config::ID_DATA_FIELD_ID()} = $CD_DATA{$cdi_id}->{&BITS::Config::ID_DATA_FIELD_ID()};

			$ART_INFO_VERSION{$art_id} = $ART_INFO{$art_id};
		}
		$sth->finish;
		undef $sth;

		&cgi_lib::common::message(scalar keys(%CD2ART));
		&cgi_lib::common::message(sprintf("\ttime=%f",&Time::HiRes::tv_interval($t0)));

		if(1){
			my $temp_bul_id = 'none';
			foreach $cdi_id (keys(%CD2ART)){
				$cdi_name = $CD_DATA{$cdi_id}->{&BITS::Config::ID_DATA_FIELD_ID()};
				next unless($cdi_name =~ /^(FMA[0-9]+)/);
				my $cdi_pname = $1;
				next unless(exists $CDI_NAME2ID{$cdi_pname});
				my $cdi_pid = $CDI_NAME2ID{$cdi_pname};
				foreach $art_id (keys(%{$CD2ART{$cdi_id}})){
					$CD2ART_HASH->{$cdi_pid}->{$temp_bul_id}->{$art_id} = undef;
				}
			}
		}

		&cgi_lib::common::message(scalar keys(%CD2ART));

		$sql = sprintf(qq|select cdi_id,but_pids,bul_id from buildup_tree_info where md_id=$md_id and mv_id=$mv_id and mr_id=$mr_id and cdi_id in (%s)|,join(',',keys(%CD2ART)));
		my $temp_bul_id;
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_id, undef);
		$sth->bind_col(++$column_number, \$but_pids, undef);
		$sth->bind_col(++$column_number, \$temp_bul_id, undef);
		while($sth->fetch){
			next unless(exists $CD_DATA{$cdi_id});
			next unless(exists $CD2ART{$cdi_id});

#			$but_pids = undef;
			$but_pids = &cgi_lib::common::decodeJSON($but_pids) if(defined $but_pids && length $but_pids);
			unless(defined $but_pids && ref $but_pids eq 'ARRAY'){
				&cgi_lib::common::message($CD_DATA{$cdi_id});
				&cgi_lib::common::message($but_pids);
				&cgi_lib::common::message($temp_bul_id);
				die __LINE__ if($temp_bul_id eq '0');
				next;
			}
			if($temp_bul_id eq '0'){
				foreach my $but_pid (@$but_pids){
					next unless(exists $CD_DATA{$but_pid});
					foreach $art_id (keys(%{$CD2ART{$cdi_id}})){
						$CD2ART{$but_pid}->{$art_id} = undef;
					}
				}
			}
			else{
				foreach $art_id (keys(%{$CD2ART{$cdi_id}})){
					$CD2ART_HASH->{$cdi_id}->{$temp_bul_id}->{$art_id} = undef;
				}
				foreach my $but_pid (@$but_pids){
					next unless(exists $CD_DATA{$but_pid});
					foreach $art_id (keys(%{$CD2ART{$cdi_id}})){
						$CD2ART_HASH->{$but_pid}->{$temp_bul_id}->{$art_id} = undef;
					}
				}
			}
		}
		$sth->finish;
		undef $sth;

		&cgi_lib::common::message(scalar keys(%CD2ART));
		&cgi_lib::common::message(sprintf("\ttime=%f",&Time::HiRes::tv_interval($t0)));
#		&cgi_lib::common::message($CD2ART_HASH);
#die __LINE__;

		my $max_but_depth;
		$sql = qq|select COALESCE(max(but_depth),0)+1 from buildup_tree_info where md_id=$md_id and mv_id=$mv_id and mr_id=$mr_id and bul_id=0|;
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth->bind_col(++$column_number, \$max_but_depth, undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;
		&cgi_lib::common::message($max_but_depth);
		$max_but_depth -= 0;
#		foreach $art_id (keys(%ART_INFO)){
		foreach $art_id (keys(%ART_INFO_VERSION)){
#			foreach my $key (keys(%{$ART_INFO{$art_id}})){
			foreach my $key (&BITS::Config::CONCEPT_DATA_COLOR_DATA_FIELD_ID(),&BITS::Config::CONCEPT_DATA_CATEGORY_DATA_FIELD_ID(),&BITS::Config::ID_DATA_FIELD_ID(),&BITS::Config::OBJ_CONCEPT_ID_DATA_FIELD_ID()){
				$VERSION_HASH{$mr_version}->{&BITS::Config::OBJ_IDS_DATA_FIELD_ID()}->{$art_id}->{$key} = $ART_INFO{$art_id}->{$key};
			}
		}
		&cgi_lib::common::message(sprintf("\ttime=%f",&Time::HiRes::tv_interval($t0)));


		if(exists $config->{'verbose'}){
			$sql = qq|select cdi_id,but_depth,but_pids,but_cids from buildup_tree_info where md_id=$md_id and mv_id=$mv_id and mr_id=$mr_id and bul_id=0 order by but_depth desc|;
		}
		else{
			my $sql_fmt = qq|select cdi_id,but_depth,NULL,NULL from buildup_tree_info where md_id=$md_id and mv_id=$mv_id and mr_id=$mr_id and bul_id=0 and cdi_id in (%s) order by but_depth desc|;
			$sql = sprintf($sql_fmt,join(',',keys(%CD2ART)));
		}
		#&cgi_lib::common::message($sql);

		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_id, undef);
		$sth->bind_col(++$column_number, \$but_depth, undef);
		$sth->bind_col(++$column_number, \$but_pids, undef);
		$sth->bind_col(++$column_number, \$but_cids, undef);
		while($sth->fetch){
			next unless(exists $CD_DATA{$cdi_id});
			unless(exists $config->{'verbose'}){
				next unless(exists $CD2ART{$cdi_id});
			}

			$cdi_name = $CD_DATA{$cdi_id}->{&BITS::Config::ID_DATA_FIELD_ID()};
			$cd_name = $CD_DATA{$cdi_id}->{&BITS::Config::NAME_DATA_FIELD_ID()};
#			push(@{$VERSION_HASH{$mr_version}->{'fma_orders'}}, $cdi_name);
			unless(defined $cdi_name && length $cdi_name){
				&cgi_lib::common::message($cdi_id);
				&cgi_lib::common::message($CD_DATA{$cdi_id});
				die __LINE__;
			}

			foreach my $key (keys(%{$CD_DATA{$cdi_id}})){
				$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{$key} = $CD_DATA{$cdi_id}->{$key};
			}

			$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{&BITS::Config::BUILDUP_TREE_DEPTH_FIELD_ID()} = $but_depth;
			$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{&BITS::Config::OBJ_IDS_DATA_FIELD_ID()} = [sort keys(%{$CD2ART{$cdi_id}})] if(exists $CD2ART{$cdi_id});
			if(exists $CD2ART_HASH->{$cdi_id} && defined $CD2ART_HASH->{$cdi_id} && ref $CD2ART_HASH->{$cdi_id} eq 'HASH'){
				foreach my $temp_bul_id (qw/3 4 none/){
					if(exists $CD2ART_HASH->{$cdi_id}->{$temp_bul_id} && defined $CD2ART_HASH->{$cdi_id}->{$temp_bul_id} && ref $CD2ART_HASH->{$cdi_id}->{$temp_bul_id} eq 'HASH'){
						my $key = &BITS::Config::OBJ_IDS_DATA_FIELD_ID() . '_' . ($temp_bul_id eq '3' ? 'isa' : ($temp_bul_id eq '4' ? 'partof' : 'none'));
						$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{$key} = [sort keys(%{$CD2ART_HASH->{$cdi_id}->{$temp_bul_id}})];
					}
				}
			}

			$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{&BITS::Config::CONCEPT_DATA_IS_ELEMENT_DATA_FIELD_ID()} = exists $CD_IS_ELEMENT{$cdi_id} ? JSON::XS::true : JSON::XS::false;


			$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{lc($cd_name)} = $cdi_name;

			if(exists $config->{'verbose'}){

				$but_pids = &cgi_lib::common::decodeJSON($but_pids) if(defined $but_pids && length $but_pids);
				if(defined $but_pids && ref $but_pids eq 'ARRAY'){
					$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{'ancestor'} = [];
					foreach my $but_pid (@$but_pids){
						next unless(exists $CD_DATA{$but_pid});
						my $cdi_pname = $CD_DATA{$but_pid}->{&BITS::Config::ID_DATA_FIELD_ID()};
#						foreach my $key (keys(%{$CD_DATA{$cdi_id}})){
#							$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{'parent'}->{$cdi_pname}->{$key} = $CD_DATA{$but_pid}->{$key};
#						}
						push(@{$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{'ancestor'}}, $cdi_pname);
					}
					$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{'#ancestor'} = scalar @{$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{'ancestor'}};
				}
				else{
					$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{'#ancestor'} = 0;
				}

				$but_cids = &cgi_lib::common::decodeJSON($but_cids) if(defined $but_cids && length $but_cids);
				if(defined $but_cids && ref $but_cids eq 'ARRAY'){
					$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{'descendants'} = [];
					foreach my $but_cid (@$but_cids){
						next unless(exists $CD_DATA{$but_cid});
						my $but_cname = $CD_DATA{$but_cid}->{&BITS::Config::ID_DATA_FIELD_ID()};
						push(@{$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{'descendants'}}, $but_cname);
					}
					$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{'#descendants'} = scalar @{$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{'descendants'}};
				}
				else{
					$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{'#descendants'} = 0;
				}
			}
		}
		$sth->finish;
		undef $sth;
		&cgi_lib::common::message(sprintf("\ttime=%f",&Time::HiRes::tv_interval($t0)));

		if(exists $config->{'verbose'}){
			my $bul_id;
			$sql = qq|select cdi_id,but_depth,but_pids,but_cids,bul_id from buildup_tree_info where md_id=$md_id and mv_id=$mv_id and mr_id=$mr_id and bul_id<>0 order by but_depth desc|;
			$sth = $dbh->prepare($sql) or die $dbh->errstr;
			$sth->execute() or die $dbh->errstr;
			$column_number = 0;
			$sth->bind_col(++$column_number, \$cdi_id, undef);
			$sth->bind_col(++$column_number, \$but_depth, undef);
			$sth->bind_col(++$column_number, \$but_pids, undef);
			$sth->bind_col(++$column_number, \$but_cids, undef);
			$sth->bind_col(++$column_number, \$bul_id, undef);
			while($sth->fetch){
				next unless(exists $CD_DATA{$cdi_id});
#				next unless(exists $CD2ART{$cdi_id});

				$cdi_name = $CD_DATA{$cdi_id}->{&BITS::Config::ID_DATA_FIELD_ID()};
				$cd_name = $CD_DATA{$cdi_id}->{&BITS::Config::NAME_DATA_FIELD_ID()};

				my $suffix;
				if($bul_id==3){
					$suffix = '_isa';
				}
				elsif($bul_id==4){
					$suffix = '_partof';
				}
				next unless(defined $bul_id && length $bul_id);

				$but_pids = &cgi_lib::common::decodeJSON($but_pids) if(defined $but_pids && length $but_pids);
				if(defined $but_pids && ref $but_pids eq 'ARRAY'){
					$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{'ancestor'.$suffix} = [];
					foreach my $but_pid (@$but_pids){
						next unless(exists $CD_DATA{$but_pid});
						my $cdi_pname = $CD_DATA{$but_pid}->{&BITS::Config::ID_DATA_FIELD_ID()};
#						foreach my $key (keys(%{$CD_DATA{$cdi_id}})){
#							$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{'parent'}->{$cdi_pname}->{$key} = $CD_DATA{$but_pid}->{$key};
#						}
						push(@{$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{'ancestor'.$suffix}}, $cdi_pname);
					}
					$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{'#ancestor'.$suffix} = scalar @{$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{'ancestor'.$suffix}};
				}
				else{
					$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{'#ancestor'.$suffix} = 0;
				}

				$but_cids = &cgi_lib::common::decodeJSON($but_cids) if(defined $but_cids && length $but_cids);
				if(defined $but_cids && ref $but_cids eq 'ARRAY'){
					$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{'descendants'.$suffix} = [];
					foreach my $but_cid (@$but_cids){
						next unless(exists $CD_DATA{$but_cid});
						my $but_cname = $CD_DATA{$but_cid}->{&BITS::Config::ID_DATA_FIELD_ID()};
						push(@{$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{'descendants'.$suffix}}, $but_cname);
					}
					$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{'#descendants'.$suffix} = scalar @{$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{'descendants'.$suffix}};
				}
				else{
					$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{'#descendants'.$suffix} = 0;
				}
			}
			$sth->finish;
			undef $sth;
		}



		my %USE_FMA_RELATION_TYPE;
		$sql = qq|
SELECT
 bt.cdi_id,
 bt.cdi_pid,
 bt.bul_id,
 COALESCE(bt.f_potids,'0'),
 cdi1.cdi_name,
 cdi2.cdi_name AS cdi_pname,
 COALESCE(cd.cd_name,cdi2.cdi_name_e) AS cdi_pname_e
FROM
 buildup_tree AS bt

LEFT JOIN concept_data_info AS cdi1 ON cdi1.ci_id=bt.ci_id AND cdi1.cdi_id=bt.cdi_id
LEFT JOIN concept_data_info AS cdi2 ON cdi2.ci_id=bt.ci_id AND cdi2.cdi_id=bt.cdi_pid

LEFT JOIN (SELECT * FROM concept_data WHERE ci_id=$ci_id AND cb_id=$cb_id) AS cd ON cd.ci_id=bt.ci_id AND cd.cdi_id=bt.cdi_pid


WHERE
 md_id=$md_id AND
 mv_id=$mv_id AND
 mr_id=$mr_id
|;
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_id, undef);
		$sth->bind_col(++$column_number, \$cdi_pid, undef);
		$sth->bind_col(++$column_number, \$bul_id, undef);
		$sth->bind_col(++$column_number, \$f_potids, undef);
		$sth->bind_col(++$column_number, \$cdi_name, undef);
		$sth->bind_col(++$column_number, \$cdi_pname, undef);
		$sth->bind_col(++$column_number, \$cdi_pname_e, undef);
		while($sth->fetch){
			next unless(defined $cdi_pname && length $cdi_pname);

			unless(exists $VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}){
#				say STDERR sprintf("[WARN] unknown FMAID!! child:[%s][%d]",$cdi_name,__LINE__);
				next;
			}
#			unless(exists $VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_pname}){
#				say STDERR sprintf("[WARN] unknown FMAID!! parent:[%s][%d]",$cdi_pname,__LINE__);
#				next;
#			}

			my @P_POTIDS = split(/[^0-9]+/,$f_potids);
			if(scalar @P_POTIDS){
				foreach my $f_potid (@P_POTIDS){
					next unless(exists $FMA_RELATION_TYPE{$f_potid});
					my $f_potname = $FMA_RELATION_TYPE{$f_potid}->{'f_potname'};
					$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{&BITS::Config::CONCEPT_DATA_RELATION_DATA_FIELD_ID()}->{$f_potname}->{$cdi_pname} = $cdi_pname_e;
					$USE_FMA_RELATION_TYPE{$f_potname} = $FMA_RELATION_TYPE{$f_potid}->{'f_order'};
				}
			}

		}
		$sth->finish;
		undef $sth;
		&cgi_lib::common::message(sprintf("\ttime=%f",&Time::HiRes::tv_interval($t0)));

		if(defined $lexicalsuper && ref $lexicalsuper eq 'HASH'){

			$sql = qq|
SELECT
-- cd.cdi_id,
 COALESCE(cd.cd_name,cdi.cdi_name_e) AS cdi_name_e
FROM
 concept_data AS cd

LEFT JOIN concept_data_info AS cdi ON cdi.ci_id=cd.ci_id AND cdi.cdi_id=cd.cdi_id

WHERE
 cd.ci_id=$ci_id AND
 cd.cb_id=$cb_id AND
 cdi.cdi_name=?
|;
			$sth = $dbh->prepare($sql) or die $dbh->errstr;

			my $f_potname = 'lexicalsuper';

			foreach my $cdi_name (keys(%{$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}})){
				next unless(exists $lexicalsuper->{$cdi_name});
				$cdi_pname = $lexicalsuper->{$cdi_name};
#				unless(exists $VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_pname}){
#					say STDERR sprintf("[WARN] unknown FMAID!! parent:[%s][%d]",$cdi_pname,__LINE__);
#					next;
#				}

				$cdi_pname_e = undef;
				$sth->execute($cdi_pname) or die $dbh->errstr;
				$column_number = 0;
				$sth->bind_col(++$column_number, \$cdi_pname_e, undef);
				$sth->fetch;
				$sth->finish;
				unless(defined $cdi_pname_e){
					say STDERR sprintf("[WARN] unknown FMAID!! parent:[%s][%d]",$cdi_pname,__LINE__);
					next;
				}

				$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name}->{&BITS::Config::CONCEPT_DATA_RELATION_DATA_FIELD_ID()}->{$f_potname}->{$cdi_pname} = $cdi_pname_e;

				$USE_FMA_RELATION_TYPE{$f_potname} = $f_order_max+1;
			}

			undef $sth;
		}

		if(scalar keys(%USE_FMA_RELATION_TYPE)){
			push(@{$VERSION_HASH{$mr_version}->{&BITS::Config::CONCEPT_DATA_RELATION_DATA_FIELD_ID()}}, sort {$USE_FMA_RELATION_TYPE{$a} <=> $USE_FMA_RELATION_TYPE{$b}} keys(%USE_FMA_RELATION_TYPE));
		}




#		&cgi_lib::common::message(scalar @{$VERSION_HASH{$mr_version}->{'fma_orders'}});
		&cgi_lib::common::message(scalar keys(%{$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}}));
		&cgi_lib::common::message(sprintf("\ttime=%f",&Time::HiRes::tv_interval($t0)));

#		last;
	}

	foreach my $art_id (keys(%ART_INFO)){
		foreach my $key (&BITS::Config::CONCEPT_DATA_COLOR_DATA_FIELD_ID(),&BITS::Config::CONCEPT_DATA_CATEGORY_DATA_FIELD_ID(),&BITS::Config::ID_DATA_FIELD_ID()){
			delete $ART_INFO{$art_id}->{$key};
		}
	}
#	$VERSION_HASH{&BITS::Config::OBJ_IDS_DATA_FIELD_ID()} = \%ART_INFO;
	printf(STDERR "\ttime=%f\n",&Time::HiRes::tv_interval($t));


	foreach my $mr_version (sort keys(%VERSION_HASH)){
		next unless(ref $VERSION_HASH{$mr_version} eq 'HASH');
		say $mr_version;
		my $SYSTEM;
		foreach my $cdi_name (keys(%{$VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}})){
			my $hash = $VERSION_HASH{$mr_version}->{&BITS::Config::IDS_DATA_FIELD_ID()}->{$cdi_name};
			next unless(ref $hash eq 'HASH');
#			&cgi_lib::common::message($hash);
#			die __LINE__;
			next unless($hash->{'is_element'});
			$SYSTEM->{$hash->{'system_id'}} = 0 unless(exists $SYSTEM->{$hash->{'system_id'}});
			$SYSTEM->{$hash->{'system_id'}}++;
		}
		foreach my $system_id (sort keys(%{$SYSTEM})){
			say sprintf("\t%15s\t%3d",$system_id,$SYSTEM->{$system_id});
		}
	}
	printf(STDERR "\ttime=%f\n",&Time::HiRes::tv_interval($t));


	if(1){
		my $json = \%VERSION_HASH;
		foreach my $version (sort keys(%{$json})){
			next unless(
						defined	$json->{$version}
				&&	ref			$json->{$version} eq 'HASH'
				&&	exists	$json->{$version}->{'ids'}
				&&	defined	$json->{$version}->{'ids'}
				&&	ref			$json->{$version}->{'ids'} eq 'HASH'
			);
			&cgi_lib::common::message($version);
			my $ids = $json->{$version}->{'ids'};
			foreach my $cdi_name (sort keys(%{$ids})){
				if($cdi_name =~ /^(FMA[0-9]+)[A-Z]\-[LRU]$/){
					my $cdi_rname = $1;
					my $cdi = $ids->{$cdi_name};

					next if(
								defined	$cdi
						&&	ref			$cdi eq 'HASH'
						&&	exists	$cdi->{&BITS::Config::CONCEPT_DATA_RELATION_DATA_FIELD_ID()}
						&&	defined	$cdi->{&BITS::Config::CONCEPT_DATA_RELATION_DATA_FIELD_ID()}
						&&	ref			$cdi->{&BITS::Config::CONCEPT_DATA_RELATION_DATA_FIELD_ID()} eq 'HASH'
						&&	exists	$cdi->{&BITS::Config::CONCEPT_DATA_RELATION_DATA_FIELD_ID()}->{'lexicalsuper'}
						&&	defined	$cdi->{&BITS::Config::CONCEPT_DATA_RELATION_DATA_FIELD_ID()}->{'lexicalsuper'}
						&&	ref			$cdi->{&BITS::Config::CONCEPT_DATA_RELATION_DATA_FIELD_ID()}->{'lexicalsuper'} eq 'HASH'
						&&	scalar keys(%{$cdi->{&BITS::Config::CONCEPT_DATA_RELATION_DATA_FIELD_ID()}->{'lexicalsuper'}})
					);

					my $cdi_r = $ids->{$cdi_rname};
					if(
								defined	$cdi_r
						&&	ref			$cdi_r eq 'HASH'
						&&	exists	$cdi_r->{&BITS::Config::CONCEPT_DATA_RELATION_DATA_FIELD_ID()}
						&&	defined	$cdi_r->{&BITS::Config::CONCEPT_DATA_RELATION_DATA_FIELD_ID()}
						&&	ref			$cdi_r->{&BITS::Config::CONCEPT_DATA_RELATION_DATA_FIELD_ID()} eq 'HASH'
						&&	exists	$cdi_r->{&BITS::Config::CONCEPT_DATA_RELATION_DATA_FIELD_ID()}->{'lexicalsuper'}
						&&	defined	$cdi_r->{&BITS::Config::CONCEPT_DATA_RELATION_DATA_FIELD_ID()}->{'lexicalsuper'}
						&&	ref			$cdi_r->{&BITS::Config::CONCEPT_DATA_RELATION_DATA_FIELD_ID()}->{'lexicalsuper'} eq 'HASH'
					){
						my $lexicalsuper = $cdi_r->{&BITS::Config::CONCEPT_DATA_RELATION_DATA_FIELD_ID()}->{'lexicalsuper'};
						foreach my $cdi_pname (keys(%{$lexicalsuper})){
							$cdi->{&BITS::Config::CONCEPT_DATA_RELATION_DATA_FIELD_ID()}->{'lexicalsuper'}->{$cdi_pname} = $lexicalsuper->{$cdi_pname};
						}
					}
					next;
				}
				elsif($cdi_name =~ /^(FMA[0-9]+)\-[LRU]$/){
					my $cdi_rname = $1;
					my $cdi = $ids->{$cdi_name};
					my $cdi_r = $ids->{$cdi_rname};
					$cdi->{&BITS::Config::CONCEPT_DATA_RELATION_DATA_FIELD_ID()} = undef;
					if(
								defined	$cdi_r
						&&	ref			$cdi_r eq 'HASH'
						&&	exists	$cdi_r->{&BITS::Config::CONCEPT_DATA_RELATION_DATA_FIELD_ID()}
						&&	defined	$cdi_r->{&BITS::Config::CONCEPT_DATA_RELATION_DATA_FIELD_ID()}
						&&	ref			$cdi_r->{&BITS::Config::CONCEPT_DATA_RELATION_DATA_FIELD_ID()} eq 'HASH'
					){
						$cdi->{&BITS::Config::CONCEPT_DATA_RELATION_DATA_FIELD_ID()} = {};
						foreach my $relation_name (keys(%{$cdi_r->{&BITS::Config::CONCEPT_DATA_RELATION_DATA_FIELD_ID()}})){
							my $relation = $cdi_r->{&BITS::Config::CONCEPT_DATA_RELATION_DATA_FIELD_ID()}->{$relation_name};
							next unless(
										defined	$relation
								&&	ref			$relation eq 'HASH'
							);
							$cdi->{&BITS::Config::CONCEPT_DATA_RELATION_DATA_FIELD_ID()}->{$relation_name} = {};
							foreach my $cdi_pname (keys(%{$relation})){
								$cdi->{&BITS::Config::CONCEPT_DATA_RELATION_DATA_FIELD_ID()}->{$relation_name}->{$cdi_pname} = $relation->{$cdi_pname};
							}
						}
					}
					if(
								defined	$cdi_r
						&&	ref			$cdi_r eq 'HASH'
						&&	exists	$cdi_r->{&BITS::Config::SYNONYM_DATA_FIELD_ID()}
						&&	defined	$cdi_r->{&BITS::Config::SYNONYM_DATA_FIELD_ID()}
						&&	length	$cdi_r->{&BITS::Config::SYNONYM_DATA_FIELD_ID()}
					){
						$cdi->{&BITS::Config::SYNONYM_DATA_FIELD_ID()} = $cdi_r->{&BITS::Config::SYNONYM_DATA_FIELD_ID()};
					}
				}
				else{
					next;
				}
			}
		}
	}
	printf(STDERR "\ttime=%f\n",&Time::HiRes::tv_interval($t));

	if(1){
		mkdir($file_prefix) unless(-e $file_prefix);
		foreach my $version (sort keys(%VERSION_HASH)){
			my $json = $VERSION_HASH{$version};
			next if(
						defined	$json
				&&	ref			$json eq 'HASH'
				&&	exists	$json->{'ids'}
				&&	defined	$json->{'ids'}
				&&	ref			$json->{'ids'} eq 'HASH'
			);
			&cgi_lib::common::message($version);
			my $version_name = $json;
			my $out_json = {};
			$out_json->{$version} = $version_name;
			$out_json->{$version_name} = $VERSION_HASH{$version_name};

			my $json_file = &catfile($file_prefix,qq|${version_name}_ext.json|);
			next if(-e $json_file && -f $json_file && -r $json_file && -s $json_file);
			&cgi_lib::common::writeFileJSON($json_file,$out_json,1);
			$json_file = &catfile($file_prefix,qq|${version_name}.json|);
			&cgi_lib::common::writeFileJSON($json_file,$out_json,0);
			my($name,$dir,$ext) = &File::Basename::fileparse($json_file,qw/.json/);
			my $gz_file = &catfile($dir,qq|$name.jgz|);
			unlink $gz_file if(-e $gz_file && -f $gz_file);
		}
#		$dbh->rollback;
#		exit;
	}
	printf(STDERR "\ttime=%f\n",&Time::HiRes::tv_interval($t));

	if(0){
		my $out_dir = &catdir($FindBin::Bin,'objs');
		mkdir($out_dir) unless(-e $out_dir);
		foreach my $version (sort keys(%VERSION_HASH)){
			my $json = $VERSION_HASH{$version};
			next unless(
						defined	$json
				&&	ref			$json eq 'HASH'
				&&	exists	$json->{&BITS::Config::OBJ_IDS_DATA_FIELD_ID()}
				&&	defined	$json->{&BITS::Config::OBJ_IDS_DATA_FIELD_ID()}
				&&	ref			$json->{&BITS::Config::OBJ_IDS_DATA_FIELD_ID()} eq 'HASH'
			);
			&cgi_lib::common::message($version);

			my $art_ids = $json->{&BITS::Config::OBJ_IDS_DATA_FIELD_ID()};
			foreach my $art_id (keys(%{$art_ids})){

				my $out_file = &catfile($out_dir,qq|${art_id}.obj|);
				next if(-e $out_file && -f $out_file && -s $out_file);
				open(my $OUT,'>',$out_file);
				say $OUT qq|o $art_id|;

				my $in_file = &catdir($FindBin::Bin,'art_file',qq|${art_id}.obj|);
				open(my $IN,'<',$in_file);
				local $/ = undef;
				my $data = <$IN>;
				close($IN);

				print $OUT $data;
				close($OUT);
			}
		}
	}
	if(0){
		foreach my $version (sort keys(%VERSION_HASH)){
			my $json = $VERSION_HASH{$version};
			next unless(
						defined	$json
				&&	ref			$json eq 'HASH'
				&&	exists	$json->{&BITS::Config::OBJ_IDS_DATA_FIELD_ID()}
				&&	defined	$json->{&BITS::Config::OBJ_IDS_DATA_FIELD_ID()}
				&&	ref			$json->{&BITS::Config::OBJ_IDS_DATA_FIELD_ID()} eq 'HASH'
			);
			&cgi_lib::common::message($version);
			my $all_file = &catdir($file_prefix,qq|${version}.obj|);
#			unlink $all_file if(-e $all_file);
			next if(-e $all_file && -f $all_file && -s $all_file);
			open(my $OUT,'>',$all_file);
			say $OUT qq|g $version|;

			my $art_ids = $json->{&BITS::Config::OBJ_IDS_DATA_FIELD_ID()};
			foreach my $art_id (keys(%{$art_ids})){
				say $OUT qq|o $art_id|;
				my $file = &catdir($FindBin::Bin,'art_file',qq|${art_id}.obj|);
				open(my $IN,'<',$file);
				local $/ = undef;
				my $data = <$IN>;
				close($IN);
				print $OUT $data;
			}
			close($OUT);
		}
	}
	if(0){
		my $all_file = &catdir($file_prefix,qq|all.obj|);
		unless(-e $all_file && -f $all_file && -s $all_file){
			open(my $OUT,'>',$all_file);
			foreach my $art_id (sort keys(%ART_INFO)){
				say $OUT qq|o $art_id|;
				my $file = &catdir($FindBin::Bin,'art_file',qq|${art_id}.obj|);
				open(my $IN,'<',$file);
				local $/ = undef;
				my $data = <$IN>;
				close($IN);
				print $OUT $data;
			}
			close($OUT);
		}
	}


	my $json_file = qq|${file_prefix}_ext.json|;
#	unless(-e $json_file && -f $json_file && -s $json_file){
	if(1){
		&cgi_lib::common::message($json_file);
		&cgi_lib::common::writeFileJSON($json_file,\%VERSION_HASH,1);
	}

	$json_file = qq|$file_prefix.json|;
	my($name,$dir,$ext) = &File::Basename::fileparse($json_file,qw/.json/);
#	unless(-e $json_file && -f $json_file && -s $json_file){
	if(1){
		&cgi_lib::common::message($json_file);
		&cgi_lib::common::writeFileJSON($json_file,\%VERSION_HASH,0);

#		my($name,$dir,$ext) = &File::Basename::fileparse($json_file,qw/.json/);
		my $gz_file = &catfile($dir,qq|$name.jgz|);
		unlink $gz_file if(-e $gz_file && -f $gz_file);
#	&IO::Compress::Gzip::gzip( $json_file => $gz_file, Level => IO::Compress::Gzip::Z_BEST_COMPRESSION ) or die "gzip failed: $IO::Compress::Gzip::GzipError\n";
	}


	$json_file = &catfile($dir,qq|art_file_info_ext.json|);
#	unless(-e $json_file && -f $json_file && -s $json_file){
	if(1){
		&cgi_lib::common::message($json_file);
		&cgi_lib::common::writeFileJSON($json_file,\%ART_INFO,1);
	}

	$json_file = &catfile($dir,qq|art_file_info.json|);
#	unless(-e $json_file && -f $json_file && -s $json_file){
	if(1){
		&cgi_lib::common::message($json_file);
		my $gz_file = &catfile($dir,qq|art_file_info.jgz|);
		&cgi_lib::common::writeFileJSON($json_file,\%ART_INFO,0);
		unlink $gz_file if(-e $gz_file && -f $gz_file);
#	&IO::Compress::Gzip::gzip( $json_file => $gz_file, Level => IO::Compress::Gzip::Z_BEST_COMPRESSION ) or die "gzip failed: $IO::Compress::Gzip::GzipError\n";
	}

	$dbh->rollback;
};
if($@){
	&cgi_lib::common::message($@);
	$dbh->rollback;
}
$dbh->{'AutoCommit'} = 1;
$dbh->{'RaiseError'} = 0;

exit;

sub system_color {
	my $dbh = shift;
	my $md_id = shift;
	my $mv_id = shift;
	my $mr_id = shift;
	my $ci_id = shift;
	my $cb_id = shift;

	my $bul_id = 3;
	my $element_coloring_table_file = &catfile($FindBin::Bin,'..','tools','element_coloring_table.txt');
	my $group2color_file = &catfile($FindBin::Bin,'..','tools','group2color.txt');

	my $SYSTE_COLOR;

	my $concept_info_data_sql=<<SQL;
select
 cdi_id,
 cdi_name
from
 concept_data_info
where
 ci_id in (select ci_id from model_revision as mr left join (select * from model_version) as mv on mv.md_id=mr.md_id and mv.mv_id=mr.mv_id where mr_use and mv_use)
SQL
	my $CDI_NAME2ID;
	my $CDI_ID2NAME;
	my $cdi_id;
	my $cdi_name;
	my $concept_info_data_sth = $dbh->prepare($concept_info_data_sql) or die $dbh->errstr;
	$concept_info_data_sth->execute() or die $dbh->errstr;
	my $column_number = 0;
	$concept_info_data_sth->bind_col(++$column_number, \$cdi_id,   undef);
	$concept_info_data_sth->bind_col(++$column_number, \$cdi_name,   undef);
	while($concept_info_data_sth->fetch){
		$CDI_NAME2ID->{$cdi_name} = $cdi_id;
		$CDI_ID2NAME->{$cdi_id} = $cdi_name;
	}
	$concept_info_data_sth->finish;
	undef $concept_info_data_sth;
	undef $concept_info_data_sql;

	my $FMA_HASH;
	open(my $IN, $element_coloring_table_file) or die "$! [$element_coloring_table_file]";
	while(<$IN>){
		chomp;
#		my($FMA,$e1,$FMA_name,$e2,$color_group) = split(/\t/);
		my($FMA,$FMA_name,$color_group) = split(/\t/);
		next unless(defined $FMA && length $FMA);
		$FMA =~ s/^[^0-9]+//g;
		$FMA =~ s/[^0-9]+$//g;
		unless($FMA =~ /^[0-9]+$/){
			&cgi_lib::common::message($FMA) if(defined $FMA && length $FMA);
			next;
		}
		my $cdi_name = "FMA$FMA";
		unless(exists $CDI_NAME2ID->{$cdi_name} && defined $CDI_NAME2ID->{$cdi_name}){
			say STDERR "Unknown [$cdi_name]";
			next;
		}
		my $cdi_id = $CDI_NAME2ID->{$cdi_name};

		$color_group =~ s/^0+//g;
		my $color_group_id = 0;
		$color_group_id = $1 - 1 if($color_group =~ /^([0-9]+)/);
		$color_group = uc $color_group unless($color_group =~ /^[0-9]+_Unclassified$/i);

		$FMA_HASH = {} unless(defined $FMA_HASH && ref $FMA_HASH eq 'HASH');
		if(exists $FMA_HASH->{$cdi_id} && defined $FMA_HASH->{$cdi_id} && $FMA_HASH->{$cdi_id}->{'color_group'} ne $color_group){
			&cgi_lib::common::message("exists $cdi_name");
		}
		$FMA_HASH->{$cdi_id} = {
			cdi_pid => $cdi_id,
			cdi_pname => $cdi_name,
			color_group => $color_group,
			color_group_id => $color_group_id,
			but_depth => 0
		};
	}
	close($IN);
#	&cgi_lib::common::message($FMA_HASH);
#	die __LINE__;

	unless(defined $COLORGROUP2COLOR && ref $COLORGROUP2COLOR eq 'HASH'){
		if(defined $group2color_file && -e $group2color_file && -f $group2color_file && -s $group2color_file){
			my $COLORGROUP10;
			open(my $IN, $group2color_file) or die "$! [$group2color_file]";
			while(<$IN>){
				chomp;
				my($color_group,$color,$color_group10_id,$color_group10_name) = split(/:/);

				next unless(defined $color_group && defined $color);

				$color_group =~ s/\s*$//g;
				$color_group =~ s/^\s*//g;
				$color =~ s/\s*$//g;
				$color =~ s/^\s*//g;

				next unless(length $color_group && length $color);

				my $color_group_id;
				$color_group_id = $1 - 1 if($color_group =~ /^([0-9]+)/);
				next unless(defined $color_group_id);

				if(defined $color_group10_id && length $color_group10_id){
					$color_group10_id =~ s/\s*$//g;
					$color_group10_id =~ s/^\s*//g;
				}
				else{
					$color_group10_id = undef;
				}
				if(defined $color_group10_name){
					$color_group10_name =~ s/\s*$//g;
					$color_group10_name =~ s/^\s*//g;
				}
				else{
					$color_group10_name = undef;
				}

				$color_group = uc $color_group unless($color_group =~ /^[0-9]+_Unclassified$/i);

#				&cgi_lib::common::message(sprintf("[%s][%s]",$color_group,$color));

				$COLORGROUP2COLOR->{$color_group_id}->{&BITS::Config::SYSTEM_ID_DATA_FIELD_ID()} = $color_group;
				$COLORGROUP2COLOR->{$color_group_id}->{&BITS::Config::CONCEPT_DATA_COLOR_DATA_FIELD_ID()} = $color;
				$COLORGROUP2COLOR->{$color_group_id}->{&BITS::Config::SYSTEM10_ID_DATA_FIELD_ID()} = $color_group10_id;
				$COLORGROUP2COLOR->{$color_group_id}->{&BITS::Config::SYSTEM10_NAME_DATA_FIELD_ID()} = $color_group10_name;
				$COLORGROUP10->{$color_group10_id} = $color_group10_name if(defined $color_group10_id && defined $color_group10_name);

				next if(defined $unclassified_group_name);
				$unclassified_group_id = $1 - 1 if($color_group =~ /^([0-9]+)/);
				my $color_group_name = $color_group;
				$color_group_name =~ s/^[0-9_]+//g;
				next unless(lc $color_group_name eq 'unclassified');
				$unclassified_group_name = $color_group;
				$unclassified_group_color = $color;
			}
			close($IN);

#			&cgi_lib::common::message($COLORGROUP10);
#			die __LINE__;

			unless(defined $unclassified_group_name){
				if(defined $COLORGROUP2COLOR && ref $COLORGROUP2COLOR eq 'HASH'){
					$unclassified_group_id = scalar keys(%$COLORGROUP2COLOR);
					$unclassified_group_name = sprintf("%d_Unclassified", (scalar keys(%$COLORGROUP2COLOR))+1);
					$unclassified_group_color = '#F0D2A0';
					$COLORGROUP2COLOR->{$unclassified_group_id}->{&BITS::Config::SYSTEM_ID_DATA_FIELD_ID()} = $unclassified_group_name;
					$COLORGROUP2COLOR->{$unclassified_group_id}->{&BITS::Config::CONCEPT_DATA_COLOR_DATA_FIELD_ID()} = $unclassified_group_color;
					if(defined $COLORGROUP10 && ref $COLORGROUP10 eq 'HASH'){
						$COLORGROUP2COLOR->{$unclassified_group_id}->{&BITS::Config::SYSTEM10_ID_DATA_FIELD_ID()} = sprintf("C%d", (scalar keys(%$COLORGROUP10))+1);
						$COLORGROUP2COLOR->{$unclassified_group_id}->{&BITS::Config::SYSTEM10_NAME_DATA_FIELD_ID()} = 'Unclassified';
					}
					else{
						$COLORGROUP2COLOR->{$unclassified_group_id}->{&BITS::Config::SYSTEM10_ID_DATA_FIELD_ID()} = undef;
						$COLORGROUP2COLOR->{$unclassified_group_id}->{&BITS::Config::SYSTEM10_NAME_DATA_FIELD_ID()} = undef;
					}
				}
			}
		}
		if(defined $COLORGROUP2COLOR && ref $COLORGROUP2COLOR eq 'HASH'){
			my @SYSTEM_COLOR;
#			foreach my $group (sort {int($a)<=>int($b)} keys(%$COLORGROUP2COLOR)){
			foreach my $group_id (sort {$a<=>$b} keys(%$COLORGROUP2COLOR)){
				my $hash = {};
#				$hash->{&BITS::Config::SYSTEM_ID_DATA_FIELD_ID()} = $group;
				$hash->{&BITS::Config::SYSTEM_ID_DATA_FIELD_ID()} = $COLORGROUP2COLOR->{$group_id}->{&BITS::Config::SYSTEM_ID_DATA_FIELD_ID()};
				$hash->{&BITS::Config::CONCEPT_DATA_COLOR_DATA_FIELD_ID()} = $COLORGROUP2COLOR->{$group_id}->{&BITS::Config::CONCEPT_DATA_COLOR_DATA_FIELD_ID()};
				$hash->{&BITS::Config::SYSTEM10_ID_DATA_FIELD_ID()} = $COLORGROUP2COLOR->{$group_id}->{&BITS::Config::SYSTEM10_ID_DATA_FIELD_ID()};
				$hash->{&BITS::Config::SYSTEM10_NAME_DATA_FIELD_ID()} = $COLORGROUP2COLOR->{$group_id}->{&BITS::Config::SYSTEM10_NAME_DATA_FIELD_ID()};
				push(@SYSTEM_COLOR, $hash);
			}

#			&cgi_lib::common::message(\@SYSTEM_COLOR);
#			die __LINE__;

			my $datas = {'datas' => \@SYSTEM_COLOR};

			my $SYSTEM_COLOR_FILE = &catfile($MENU_SEGMENTS_BASE_DIR, qq|SYSTEM_COLOR.json|);
			&cgi_lib::common::writeFileJSON($SYSTEM_COLOR_FILE,$datas,0);

			my $SYSTEM_COLOR_FILE_EXT = &catfile($MENU_SEGMENTS_BASE_DIR, qq|SYSTEM_COLOR_ext.json|);
			&cgi_lib::common::writeFileJSON($SYSTEM_COLOR_FILE_EXT,$datas,1);

			my $SYSTEM_COLOR_FILE_GZ = &catfile($MENU_SEGMENTS_BASE_DIR, qq|SYSTEM_COLOR.jgz|);
			unlink $SYSTEM_COLOR_FILE_GZ if(-e $SYSTEM_COLOR_FILE_GZ && -f $SYSTEM_COLOR_FILE_GZ);
#			&IO::Compress::Gzip::gzip( $SYSTEM_COLOR_FILE => $SYSTEM_COLOR_FILE_GZ, Level => IO::Compress::Gzip::Z_BEST_COMPRESSION ) or die "gzip failed: $IO::Compress::Gzip::GzipError\n";
		}
	}

#	&cgi_lib::common::message($COLORGROUP2COLOR);
#	die __LINE__;

	if(defined $FMA_HASH && ref $FMA_HASH eq 'HASH' && scalar keys(%$FMA_HASH)){

		my $cdi_id;
		my $but_cids;
		my $but_depth;

		my $buildup_tree_info_sql=<<SQL;
select
 cdi_id,
 but_cids,
 but_depth
from
 buildup_tree_info
where
 (md_id,mv_id,mr_id,bul_id,cdi_id) in
 (
  select
   md_id,
   mv_id,
   max(mr_id) as mr_id,
   bul_id,
   cdi_id
  from
   buildup_tree_info
  where
   md_id=$md_id and
   mv_id=$mv_id and
   mr_id=$mr_id and
   bul_id=$bul_id and
   cdi_id in (%s)
  group by
   md_id,
   mv_id,
   bul_id,
   cdi_id
 )
ORDER BY
  but_depth DESC
;
SQL

		my $buildup_tree_info_sth;

#		&cgi_lib::common::message(sprintf($buildup_tree_info_sql,join(',',map {'?'} keys(%$FMA_HASH))));
#		&cgi_lib::common::message([map {$_-0} keys(%$FMA_HASH)]);

		my $EXISTS_CIDS = {};

		$buildup_tree_info_sth = $dbh->prepare(sprintf($buildup_tree_info_sql,join(',',map {'?'} keys(%$FMA_HASH)))) or die $dbh->errstr;
		$buildup_tree_info_sth->execute(map {$_-0} keys(%$FMA_HASH)) or die $dbh->errstr;
		$column_number = 0;
		$buildup_tree_info_sth->bind_col(++$column_number, \$cdi_id,    undef);
		$buildup_tree_info_sth->bind_col(++$column_number, \$but_cids,  undef);
		$buildup_tree_info_sth->bind_col(++$column_number, \$but_depth, undef);
		while($buildup_tree_info_sth->fetch){
			unless(exists $FMA_HASH->{$cdi_id} && defined $FMA_HASH->{$cdi_id}){
				&cgi_lib::common::message("Unknown [$CDI_ID2NAME->{$cdi_id}]");
				next;
			}
			$FMA_HASH->{$cdi_id}->{'but_depth'} = $but_depth - 0;

			$FMA_HASH->{$cdi_id}->{'but_cids'} = undef;
			next unless(defined $but_cids && length $but_cids);

#		&cgi_lib::common::message($cdi_id);
#		&cgi_lib::common::message($but_cids);

			$but_cids = &cgi_lib::common::decodeJSON($but_cids);
			if(defined $but_cids && ref $but_cids eq 'ARRAY' && scalar @{$but_cids}){
				map {
					unless(exists $EXISTS_CIDS->{$_}){
						$FMA_HASH->{$cdi_id}->{'but_cids'}->{$_} = undef;
						$EXISTS_CIDS->{$_} = $cdi_id;
					}
				} @{$but_cids};
			}else{
				&cgi_lib::common::message($but_cids);
			}
		}
		$buildup_tree_info_sth->finish;
		undef $buildup_tree_info_sth;
		undef $buildup_tree_info_sql;

#		&cgi_lib::common::message($EXISTS_CIDS);
#		die __LINE__;

		undef $EXISTS_CIDS;

	#exit;

		foreach my $cdi_id (keys(%$FMA_HASH)){

			my $but_cids = $FMA_HASH->{$cdi_id}->{'but_cids'};
			my $color_group = $FMA_HASH->{$cdi_id}->{'color_group'};
			my $cdi_pname = $CDI_ID2NAME->{$cdi_id};

			if(defined $but_cids && ref $but_cids eq 'HASH' && scalar keys(%$but_cids)){
				foreach my $but_cid (keys(%$but_cids)){
					if(exists $FMA_HASH->{$but_cid} && defined $FMA_HASH->{$but_cid} && $FMA_HASH->{$but_cid}->{'color_group'} ne $color_group && $FMA_HASH->{$but_cid}->{'but_depth'} > $FMA_HASH->{$cdi_id}->{'but_depth'}){


	#					&cgi_lib::common::message("exists\t$CDI_ID2NAME->{$but_cid}\t$cdi_pname\t$color_group\t$FMA_HASH->{$but_cid}->{'cdi_pname'}\t$FMA_HASH->{$but_cid}->{'color_group'}");
						if(exists $FMA_HASH->{$but_cid}->{'but_cids'} && defined $FMA_HASH->{$but_cid}->{'but_cids'} && ref $FMA_HASH->{$but_cid}->{'but_cids'} eq 'HASH'){
							foreach (keys(%{$FMA_HASH->{$but_cid}->{'but_cids'}})){
								delete $FMA_HASH->{$cdi_id}->{'but_cids'}->{$_} if(exists $FMA_HASH->{$cdi_id}->{'but_cids'}->{$_});
							}
						}
						delete $FMA_HASH->{$cdi_id}->{'but_cids'}->{$but_cid} if(exists $FMA_HASH->{$cdi_id}->{'but_cids'}->{$but_cid});
					}
				}
			}
		}

		foreach my $cdi_id (keys(%$FMA_HASH)){

			my $color_group = $FMA_HASH->{$cdi_id}->{'color_group'};
			my $color_group_id = $FMA_HASH->{$cdi_id}->{'color_group_id'};
			my $cdi_pname = $CDI_ID2NAME->{$cdi_id};

			my $but_cids = $FMA_HASH->{$cdi_id}->{'but_cids'};
			if(defined $but_cids && ref $but_cids eq 'HASH' && scalar keys(%$but_cids)){
				foreach my $but_cid (keys(%$but_cids)){

					if(exists $FMA_HASH->{$but_cid} && defined $FMA_HASH->{$but_cid} && $FMA_HASH->{$but_cid}->{'color_group'} ne $color_group){
						&cgi_lib::common::message("exists\t$CDI_ID2NAME->{$but_cid}\t$cdi_pname\t$color_group\t$FMA_HASH->{$but_cid}->{'cdi_pname'}\t$FMA_HASH->{$but_cid}->{'color_group'}");
						next;
					}
					$FMA_HASH->{$but_cid} = {
						cdi_pid => $cdi_id,
						cdi_pname => $cdi_pname,
						color_group => $color_group,
						color_group_id => $color_group_id
					};

				}
			}
		}

		foreach my $cdi_id (sort {$FMA_HASH->{$a}->{'color_group_id'} <=> $FMA_HASH->{$b}->{'color_group_id'}} sort {$CDI_ID2NAME->{$a} cmp $CDI_ID2NAME->{$b}} keys(%$FMA_HASH)){
			my $color_group_id = $FMA_HASH->{$cdi_id}->{'color_group_id'};
			my $color_group = $FMA_HASH->{$cdi_id}->{'color_group'};
			my $cdi_name = $CDI_ID2NAME->{$cdi_id};
			my $color = defined $COLORGROUP2COLOR && exists $COLORGROUP2COLOR->{$color_group_id} && defined $COLORGROUP2COLOR->{$color_group_id} ? $COLORGROUP2COLOR->{$color_group_id}->{&BITS::Config::CONCEPT_DATA_COLOR_DATA_FIELD_ID()} : '';
			my $system10_id = defined $COLORGROUP2COLOR && exists $COLORGROUP2COLOR->{$color_group_id} && defined $COLORGROUP2COLOR->{$color_group_id} ? $COLORGROUP2COLOR->{$color_group_id}->{&BITS::Config::SYSTEM10_ID_DATA_FIELD_ID()} : undef;
			my $system10_name = defined $COLORGROUP2COLOR && exists $COLORGROUP2COLOR->{$color_group_id} && defined $COLORGROUP2COLOR->{$color_group_id} ? $COLORGROUP2COLOR->{$color_group_id}->{&BITS::Config::SYSTEM10_NAME_DATA_FIELD_ID()} : undef;
#			say $cdi_name."\t".$cdi_id."\t".$color_group."\t".$color;

			$SYSTE_COLOR->{$cdi_id} = {};
			$SYSTE_COLOR->{$cdi_id}->{&BITS::Config::CONCEPT_DATA_INFO_DATA_FIELD_ID()} = $cdi_id - 0;
			$SYSTE_COLOR->{$cdi_id}->{&BITS::Config::ID_DATA_FIELD_ID()} = $cdi_name;
			$SYSTE_COLOR->{$cdi_id}->{&BITS::Config::CONCEPT_DATA_COLOR_DATA_FIELD_ID()} = $color;
			$SYSTE_COLOR->{$cdi_id}->{&BITS::Config::SYSTEM_ID_DATA_FIELD_ID()} = $color_group;
			$SYSTE_COLOR->{$cdi_id}->{&BITS::Config::SYSTEM10_ID_DATA_FIELD_ID()} = $system10_id;
			$SYSTE_COLOR->{$cdi_id}->{&BITS::Config::SYSTEM10_NAME_DATA_FIELD_ID()} = $system10_name;
		}

	#	my $OUT;

#		&cgi_lib::common::message($FMA_HASH);
#		&cgi_lib::common::message($SYSTE_COLOR);
#		die __LINE__;

	}else{
		say STDERR __LINE__;
	}
	return $SYSTE_COLOR;
}
