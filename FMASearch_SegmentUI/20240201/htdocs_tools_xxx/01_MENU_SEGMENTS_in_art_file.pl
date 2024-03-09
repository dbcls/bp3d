#!/bp3d/local/perl/bin/perl

$| = 1;
select(STDERR);
$| = 1;
select(STDOUT);


use strict;
use warnings;
use feature ':5.10';

use File::Basename;
use File::Spec::Functions qw(abs2rel catdir catfile splitdir);
use File::Path;
use File::Copy;
use DBD::Pg;
use Time::HiRes;
use IO::Compress::Gzip;
#use Hash::Merge
#Hash::Merge::set_behavior('LEFT_PRECEDENT');

use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'..','cgi_lib'),&catdir($FindBin::Bin,'..','..','cgi_lib');
use BITS::Config;
use BITS::VTK;

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
/) or exit 1;

$ENV{'AG_DB_NAME'} = $config->{'db'};
$ENV{'AG_DB_HOST'} = $config->{'host'};
$ENV{'AG_DB_PORT'} = $config->{'port'};

require "webgl_common.pl";
use cgi_lib::common;

my $dbh = &get_dbh();

my $MENU_SEGMENTS_DIR = &catdir($FindBin::Bin,'..','htdocs','MENU_SEGMENTS');
my @MENU_SEGMENTS_FILES = qx/find $MENU_SEGMENTS_DIR -type f -name "*.obj"/;
chomp @MENU_SEGMENTS_FILES;
my $MENU_SEGMENTS_PROP;


my $change_data = 0;
#[ ]がある場合、[_]に置換する
foreach (@MENU_SEGMENTS_FILES){
	chomp;
	my($name,$dir,$ext) = &File::Basename::fileparse($_,qw/.obj/);
	next unless($name =~ /[ ]+/);
	my $obj_name = $name;
	$obj_name =~ s/ /_/g;

	my $change_filename = &catfile($dir,$obj_name.'.obj');
	rename $_, $change_filename;
	$_ = $change_filename;

	my $ogz_filename = &catfile($dir,$name.'.ogz');
	rename $ogz_filename, &catfile($dir,$obj_name.'.ogz') if(-e $ogz_filename);

	$change_data = 1;
}

=pod
foreach (@MENU_SEGMENTS_FILES){
	chomp;
	my($name,$dir,$ext) = &File::Basename::fileparse($_,qw/.obj/);
	my $ogz_filename = &catfile($dir,$name.'.ogz');
	$change_data = 1 unless(-e $ogz_filename && -f $ogz_filename && -s $ogz_filename);
}

&cgi_lib::common::message($change_data,\*STDOUT);
exit;
=cut



#ダウンロードで取得するとFJIDが付加されるので削除
=pod
foreach (@MENU_SEGMENTS_FILES){
	chomp;
	my($name,$dir,$ext) = &File::Basename::fileparse($_,qw/.obj/);
	next unless($name =~ /^MM[0-9]+(.+)$/);
	my $obj_name = $1;

	my $change_filename = &catfile($dir,$obj_name.'.obj');
	rename $_, $change_filename;
	$_ = $change_filename;
}
#exit;
=cut

foreach my $file (@MENU_SEGMENTS_FILES){
	my $segment_obj_prop = $MENU_SEGMENTS_PROP->{$file} = &BITS::VTK::_getProperties($file);
	foreach (@{$segment_obj_prop->{'bounds'}}){
		$_ -= 0;
	}
	foreach (@{$segment_obj_prop->{'centerOfMass'}}){
		$_ -= 0;
	}
	foreach (@{$segment_obj_prop->{'centers'}}){
		$_ -= 0;
	}
	$segment_obj_prop->{'points'} -= 0;
	$segment_obj_prop->{'polys'} -= 0;
#	$segment_obj_prop->{'volume'} -= 0;
#	my $art_xmin = $segment_obj_prop->{'bounds'}->[0] - 0;
#	my $art_xmax = $segment_obj_prop->{'bounds'}->[1] - 0;
#	my $art_ymin = $segment_obj_prop->{'bounds'}->[2] - 0;
#	my $art_ymax = $segment_obj_prop->{'bounds'}->[3] - 0;
#	my $art_zmin = $segment_obj_prop->{'bounds'}->[4] - 0;
#	my $art_zmax = $segment_obj_prop->{'bounds'}->[5] - 0;
}
#&cgi_lib::common::message($MENU_SEGMENTS_PROP,\*STDOUT);
#exit;

my $sql=<<SQL;
select
 art_id,
 art_ext,
 art_id || art_ext as art_filename,
 EXTRACT(EPOCH FROM art_timestamp) as art_timestamp,
 art_md5,
 art_data_size
from
 art_file
WHERE
 art_id in (SELECT art_id FROM concept_art_map WHERE cm_use AND cm_delcause IS NULL)
-- art_id in (SELECT art_id FROM concept_art_map WHERE cm_use AND cm_delcause IS NULL AND md_id=1 AND mv_id=26 AND mr_id=1)
-- art_id='CX138'
-- art_id='CX126'
-- art_id='CX100M'
-- art_id='FJ130'
-- AND art_id='MM5249'
-- art_xmasscenter=0 and
-- art_ymasscenter=0 and
-- art_zmasscenter=0
ORDER BY
 prefix_id,
 art_serial,
 art_mirroring
SQL

my $ART;

my $art_id;
my $art_ext;
my $art_filename;
my $art_timestamp;
my $art_md5;
my $art_data_size;
my $sth = $dbh->prepare($sql) or die $dbh->errstr;
$sth->execute() or die $dbh->errstr;
my $column_number = 0;
$sth->bind_col(++$column_number, \$art_id,   undef);
$sth->bind_col(++$column_number, \$art_ext,   undef);
$sth->bind_col(++$column_number, \$art_filename,   undef);
$sth->bind_col(++$column_number, \$art_timestamp,   undef);
$sth->bind_col(++$column_number, \$art_md5,   undef);
$sth->bind_col(++$column_number, \$art_data_size,   undef);
while($sth->fetch){
	push(@$ART,{
		art_id => $art_id,
		art_ext => $art_ext,
		art_filename => $art_filename,
		art_timestamp => $art_timestamp - 0,
		art_md5 => $art_md5,
		art_data_size => $art_data_size - 0
	});
}
$sth->finish;
undef $sth;
undef $sql;

umask(0);
my $sth_sel_data = $dbh->prepare(qq|select art_data from art_file where art_id=? limit 1|) or die $dbh->errstr;

my $ART2SEG;
my $ART2SEG_DIR = &catdir($FindBin::Bin,'..','htdocs','MENU_SEGMENTS');
my $ART2SEG_PREFIX = &catfile($ART2SEG_DIR,'MENU_SEGMENTS_in_art_file');
my $ART2SEG_FILE     = qq|${ART2SEG_PREFIX}.json|;
my $ART2SEG_FILE_EXT = qq|${ART2SEG_PREFIX}_ext.json|;
my $ART2SEG_FILE_GZ  = qq|${ART2SEG_PREFIX}.jgz|;
if(-e $ART2SEG_FILE && -f $ART2SEG_FILE && -s $ART2SEG_FILE){
	$ART2SEG = &cgi_lib::common::readFileJSON($ART2SEG_FILE);
}

undef $ART2SEG if($change_data);
#unless(defined $ART2SEG && ref $ART2SEG eq 'HASH'){
if(1){
#	undef $ART2SEG if(defined $ART2SEG);
	$ART2SEG = $ART2SEG || {};

	my $t = [&Time::HiRes::gettimeofday()];

	my $dir = &catdir($FindBin::Bin,'art_file');
	#my $dir_mirror = &catdir($FindBin::Bin,'art_file_mirror');
	my $count = scalar @$ART;
	foreach my $art (@$ART){
		my $t0 = [&Time::HiRes::gettimeofday()];

		my $art_id = $art->{art_id};
		my $art_filename = $art->{art_filename};
		my $art_timestamp = $art->{art_timestamp};
		my $file = &catfile($dir,$art_filename);
		my $remove_file = &catfile($dir,$art_id);
		unlink $remove_file if(-e $remove_file && -f $remove_file);

		printf(STDERR "[%04d]\t%s",$count--,$art_id);

#		delete $ART2SEG->{$art_id} if($art_id eq 'MM7214');	# DEBUG

		if(defined $ART2SEG && ref $ART2SEG eq 'HASH' && exists $ART2SEG->{$art_id} && defined $ART2SEG->{$art_id} && ref $ART2SEG->{$art_id} eq 'HASH' && scalar keys(%{$ART2SEG->{$art_id}}) > 0){
			print STDERR "\texists\n";
			next;
		}
		else{													# unfound対応(2019/12/27)
			delete $ART2SEG->{$art_id};	# unfound対応(2019/12/27)
		}															# unfound対応(2019/12/27)

		if(defined $ART2SEG && ref $ART2SEG eq 'HASH' && exists $ART2SEG->{$art_id} && defined $ART2SEG->{$art_id} && ref $ART2SEG->{$art_id} eq 'HASH' && scalar keys(%{$ART2SEG->{$art_id}}) > 0){
			printf(STDERR "\n");

			delete $ART2SEG->{$art_id}->{'CITIES'}->{'MM2439_Pallidum HOLED'} if(exists $ART2SEG->{$art_id}->{'CITIES'} && defined $ART2SEG->{$art_id}->{'CITIES'} && ref $ART2SEG->{$art_id}->{'CITIES'} eq 'HASH' && exists $ART2SEG->{$art_id}->{'CITIES'}->{'MM2439_Pallidum HOLED'});
			delete $ART2SEG->{$art_id}->{'CITIES'}->{'MM2439_Pallidum_HOLED'} if(exists $ART2SEG->{$art_id}->{'CITIES'} && defined $ART2SEG->{$art_id}->{'CITIES'} && ref $ART2SEG->{$art_id}->{'CITIES'} eq 'HASH' && exists $ART2SEG->{$art_id}->{'CITIES'}->{'MM2439_Pallidum_HOLED'});
			delete $ART2SEG->{$art_id}->{'CITIES'}->{'MM2411_EAR'} if(exists $ART2SEG->{$art_id}->{'CITIES'} && defined $ART2SEG->{$art_id}->{'CITIES'} && ref $ART2SEG->{$art_id}->{'CITIES'} eq 'HASH' && exists $ART2SEG->{$art_id}->{'CITIES'}->{'MM2411_EAR'});
			delete $ART2SEG->{$art_id}->{'CITIES'}->{'MM2412_EYE'} if(exists $ART2SEG->{$art_id}->{'CITIES'} && defined $ART2SEG->{$art_id}->{'CITIES'} && ref $ART2SEG->{$art_id}->{'CITIES'} eq 'HASH' && exists $ART2SEG->{$art_id}->{'CITIES'}->{'MM2412_EYE'});
			delete $ART2SEG->{$art_id}->{'CITIES'}->{'MM2417_PALLIUM'} if(exists $ART2SEG->{$art_id}->{'CITIES'} && defined $ART2SEG->{$art_id}->{'CITIES'} && ref $ART2SEG->{$art_id}->{'CITIES'} eq 'HASH' && exists $ART2SEG->{$art_id}->{'CITIES'}->{'MM2417_PALLIUM'});

			next;
		}

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
		if(-e $file && -f $file && -s $file){
			my ($atime,$utime) = (stat($file))[8,9];
			utime($art_timestamp, $art_timestamp, $file) unless($utime==$art_timestamp);
		}
		else{
			printf(STDERR "\tunknown file\n");
			next;
		}

		my $obj_prop = &BITS::VTK::_getProperties($file);
		foreach (@{$obj_prop->{'bounds'}}){
			$_ -= 0;
		}
		foreach (@{$obj_prop->{'centerOfMass'}}){
			$_ -= 0;
		}
		foreach (@{$obj_prop->{'centers'}}){
			$_ -= 0;
		}
		$obj_prop->{'points'} -= 0;
		$obj_prop->{'polys'} -= 0;
	#	$obj_prop->{'volume'} -= 0;

	#	$art = &Hash::Merge::merge($art,$obj_prop);
		$art->{'prop'} = &Clone::clone($obj_prop);

	#	&cgi_lib::common::message($art,\*STDOUT);
	#	die __LINE__;

	#	&cgi_lib::common::message($obj_prop,\*STDOUT);
	#	my $obj_xmin = $obj_prop->{'bounds'}->[0] - 0;
	#	my $obj_xmax = $obj_prop->{'bounds'}->[1] - 0;
	#	my $obj_ymin = $obj_prop->{'bounds'}->[2] - 0;
	#	my $obj_ymax = $obj_prop->{'bounds'}->[3] - 0;
	#	my $obj_zmin = $obj_prop->{'bounds'}->[4] - 0;
	#	my $obj_zmax = $obj_prop->{'bounds'}->[5] - 0;

	#	say '';
		printf(STDERR "\t%d\t%d",$obj_prop->{'points'},$obj_prop->{'polys'});

	#	my $incount = 0;
		foreach my $segment_file (sort @MENU_SEGMENTS_FILES){
	#		next unless($segment_file eq '/ext1/project/WebGL/20170531/tools_170531/20170605/MENU_SEGMENTS/cities/M_THIGH-R.obj');
	#		next unless($segment_file eq '/ext1/project/WebGL/20170531/tools_170531/20170605/MENU_SEGMENTS/prefectures/_ARM2-R.obj');

			my($name,$dir,$ext) = &File::Basename::fileparse($segment_file,qw/.obj/);
			next if($name eq 'MM2439_Pallidum HOLED');
			next if($name eq 'MM2439_Pallidum_HOLED');
			next if($name eq 'MM2411_EAR');
			next if($name eq 'MM2412_EYE');
			next if($name eq 'MM2417_PALLIUM');

#=pod
			my $segment_obj_prop = $MENU_SEGMENTS_PROP->{$segment_file};
			next if($segment_obj_prop->{'bounds'}->[0] > $obj_prop->{'bounds'}->[1]);
			next if($segment_obj_prop->{'bounds'}->[1] < $obj_prop->{'bounds'}->[0]);
			next if($segment_obj_prop->{'bounds'}->[2] > $obj_prop->{'bounds'}->[3]);
			next if($segment_obj_prop->{'bounds'}->[3] < $obj_prop->{'bounds'}->[2]);
			next if($segment_obj_prop->{'bounds'}->[4] > $obj_prop->{'bounds'}->[5]);
			next if($segment_obj_prop->{'bounds'}->[5] < $obj_prop->{'bounds'}->[4]);
#=cut

			$dir =~ s/\/$//g;
			my @dirs = &splitdir($segment_file);
			my $region = $dirs[-2];
	#		say $dir;
	#		say &catfile($region,$name);

	##		my $hash = &BITS::VTK::objectInsideObject($segment_file,$file);
			my $hash = &BITS::VTK::objectOutsideObject($segment_file,$file);

	#		my $segment_obj_prop = $MENU_SEGMENTS_PROP->{$segment_file};
	#		my $out_bounds = 0;
	#		$out_bounds = 1 if($segment_obj_prop->{'bounds'}->[0] > $obj_prop->{'bounds'}->[1]);
	#		$out_bounds = 1 if($segment_obj_prop->{'bounds'}->[1] < $obj_prop->{'bounds'}->[0]);
	#		$out_bounds = 1 if($segment_obj_prop->{'bounds'}->[2] > $obj_prop->{'bounds'}->[3]);
	#		$out_bounds = 1 if($segment_obj_prop->{'bounds'}->[3] < $obj_prop->{'bounds'}->[2]);
	#		$out_bounds = 1 if($segment_obj_prop->{'bounds'}->[4] > $obj_prop->{'bounds'}->[5]);
	#		$out_bounds = 1 if($segment_obj_prop->{'bounds'}->[5] < $obj_prop->{'bounds'}->[4]);
	#		my $hash = {
	#			incount => 0,
	#			all => 0
	#		};
	#		$hash = &BITS::VTK::objectOutsideObject($segment_file,$file) unless($out_bounds);

			my $inside = &BITS::VTK::pointInsideObject($segment_file,$obj_prop->{'centerOfMass'});
#			if($art_id eq 'MM5249'){
#				&cgi_lib::common::message($name,\*STDOUT);
#				&cgi_lib::common::message($hash,\*STDOUT);
#				&cgi_lib::common::message($inside,\*STDOUT);
#			}

			next unless($hash->{'incount'} || $inside);

			$hash->{'all'} -= 0;
			$hash->{'rate'} = $hash->{'incount'}>0 && $hash->{'all'}>0 ? $hash->{'incount'} / $hash->{'all'} : 0;

			$hash->{'inside'} = $inside ? JSON::XS::true : JSON::XS::false;

			$ART2SEG->{$art_id}->{$region}->{$name} = $hash;

	#		if($inside){
	#			&cgi_lib::common::message($ART2SEG,\*STDOUT);
	#			die __LINE__;
	#		}
#			if($art_id eq 'MM5249'){
#				&cgi_lib::common::message($ART2SEG->{$art_id},\*STDOUT);
#				die __LINE__;
#			}

	#		if($inside && $hash->{'incount'}<=0){
	#			&cgi_lib::common::message($art_id,\*STDOUT);
	#			&cgi_lib::common::message($region,\*STDOUT);
	#			&cgi_lib::common::message($name,\*STDOUT);
	#			&cgi_lib::common::message($hash,\*STDOUT);
	#			die __LINE__;
	#		}

	#		$incount += $hash->{'incount'};

	#		&cgi_lib::common::message($ART2SEG->{$art_id}->{$region}->{$name});
	#		exit;
	#		if($incount){
	#			&cgi_lib::common::message($segment_obj_prop,\*STDOUT);
	#			last;
	#		}
		}
	#	if($incount){
	#		&cgi_lib::common::message($obj_prop,\*STDOUT);
	#		last;
	#	}

	#	say STDERR "\nUnknown region [$art_id]" unless($incount);
	#	say "\nExists region [$art_id]" if($incount);

#		$ART2SEG->{$art_id} = {} unless(exists $ART2SEG->{$art_id} && defined $ART2SEG->{$art_id} && ref $ART2SEG->{$art_id} eq 'HASH');	# unfound対応(2019/12/27)
#		if(exists $ART2SEG->{$art_id} && defined $ART2SEG->{$art_id} && ref $ART2SEG->{$art_id} eq 'HASH'){			# unfound対応(2002/08/06
#			my $inside_count = 0;																																									# unfound対応(2002/08/06
#			my $region = 'CITIES';																																								# unfound対応(2002/08/06
#			foreach my $name (keys(%{$ART2SEG->{$art_id}->{$region}})){																						# unfound対応(2002/08/06
#				next if($ART2SEG->{$art_id}->{$region}->{$name}->{'inside'} == JSON::XS::false);										# unfound対応(2002/08/06
#				$inside_count++;																																										# unfound対応(2002/08/06
#				last;																																																# unfound対応(2002/08/06
#			}																																																			# unfound対応(2002/08/06
#			unless($inside_count){																																								# unfound対応(2002/08/06
#				delete $ART2SEG->{$art_id};																																					# unfound対応(2002/08/06
#			}																																																			# unfound対応(2002/08/06)
#		}																																																				# unfound対応(2002/08/06
		unless(exists $ART2SEG->{$art_id} && defined $ART2SEG->{$art_id} && ref $ART2SEG->{$art_id} eq 'HASH'){	# unfound対応(2019/12/27)
			my $name = 'unfound';																																									# unfound対応(2019/12/27)
			foreach my $region (qw/PREFECTURES CITIES/){																													# unfound対応(2019/12/27)
				$ART2SEG->{$art_id}->{$region}->{$name} = {																													# unfound対応(2019/12/27)
					'all' => 0,																																												# unfound対応(2019/12/27)
					'incount' => 0,																																										# unfound対応(2019/12/27)
					'inside' => JSON::XS::false,																																			# unfound対応(2019/12/27)
					'outcount' => 0,																																									# unfound対応(2019/12/27)
					'rate' => 0																																												# unfound対応(2019/12/27)
				};																																																	# unfound対応(2019/12/27)
			}																																																			# unfound対応(2019/12/27)
		}																																																				# unfound対応(2019/12/27)

		printf(STDERR "\ttime=%f\n",&Time::HiRes::tv_interval($t0));

	}
	&cgi_lib::common::message(&Time::HiRes::tv_interval($t),\*STDERR);

	#&cgi_lib::common::message($ART2SEG,\*STDOUT);

	&cgi_lib::common::writeFileJSON($ART2SEG_FILE_EXT,$ART2SEG,1);
	&cgi_lib::common::writeFileJSON($ART2SEG_FILE,$ART2SEG,0);

	unlink $ART2SEG_FILE_GZ if(-e $ART2SEG_FILE_GZ && -f $ART2SEG_FILE_GZ);
#	&IO::Compress::Gzip::gzip( $ART2SEG_FILE => $ART2SEG_FILE_GZ, Level => IO::Compress::Gzip::Z_BEST_COMPRESSION ) or die "gzip failed: $IO::Compress::Gzip::GzipError\n";
}

my $SEG2ART;
my $SEG2ART_INSIDE;

#my $UNFOUND_SEG2ART;
my $UNFOUND_SEG2ART_INSIDE;

foreach my $art_id (keys(%$ART2SEG)){
	my $inside_count = 0;																																									# unfound対応(2002/08/06
	my $region = 'CITIES';																																								# unfound対応(2002/08/06
	foreach my $name (keys(%{$ART2SEG->{$art_id}->{$region}})){																						# unfound対応(2002/08/06
		next if($ART2SEG->{$art_id}->{$region}->{$name}->{'inside'} == JSON::XS::false);										# unfound対応(2002/08/06
		$inside_count++;																																										# unfound対応(2002/08/06
		last;																																																# unfound対応(2002/08/06
	}																																																			# unfound対応(2002/08/06
	foreach my $region (keys(%{$ART2SEG->{$art_id}})){
		foreach my $name (keys(%{$ART2SEG->{$art_id}->{$region}})){
			$SEG2ART->{$region}->{$name}->{$art_id} = $ART2SEG->{$art_id}->{$region}->{$name} if($ART2SEG->{$art_id}->{$region}->{$name}->{'incount'});																	# unfound対応(2019/12/27)
			if($ART2SEG->{$art_id}->{$region}->{$name}->{'inside'} && $inside_count){
				$SEG2ART_INSIDE->{$region}->{$name}->{$art_id} = $ART2SEG->{$art_id}->{$region}->{$name} ;																# unfound対応(2019/12/27)
			}
			else{
				$SEG2ART_INSIDE->{$region}->{'unfound'}->{$art_id} = $ART2SEG->{$art_id}->{$region}->{$name} unless($inside_count);																# unfound対応(2019/12/27)
			}
		}
	}
}




my $SEG2ART_PREFIX = &catfile($ART2SEG_DIR,'SEG2ART');
my $SEG2ART_FILE_EXT = qq|${SEG2ART_PREFIX}_ext.json|;
&cgi_lib::common::writeFileJSON($SEG2ART_FILE_EXT,$SEG2ART,1);

my $SEG2ART_FILE = qq|${SEG2ART_PREFIX}.json|;
&cgi_lib::common::writeFileJSON($SEG2ART_FILE,$SEG2ART,0);

my $SEG2ART_FILE_GZ = qq|${SEG2ART_PREFIX}.jgz|;
unlink $SEG2ART_FILE_GZ if(-e $SEG2ART_FILE_GZ && -f $SEG2ART_FILE_GZ);
#&IO::Compress::Gzip::gzip( $SEG2ART_FILE => $SEG2ART_FILE_GZ, Level => IO::Compress::Gzip::Z_BEST_COMPRESSION ) or die "gzip failed: $IO::Compress::Gzip::GzipError\n";




my $SEG2ART_INSIDE_PREFIX = &catfile($ART2SEG_DIR,'SEG2ART_INSIDE');
my $SEG2ART_INSIDE_FILE_EXT = qq|${SEG2ART_INSIDE_PREFIX}_ext.json|;
&cgi_lib::common::writeFileJSON($SEG2ART_INSIDE_FILE_EXT,$SEG2ART_INSIDE,1);

my $SEG2ART_INSIDE_FILE = qq|${SEG2ART_INSIDE_PREFIX}.json|;
&cgi_lib::common::writeFileJSON($SEG2ART_INSIDE_FILE,$SEG2ART_INSIDE,0);

my $SEG2ART_INSIDE_FILE_GZ = qq|${SEG2ART_INSIDE_PREFIX}.jgz|;
unlink $SEG2ART_INSIDE_FILE_GZ if(-e $SEG2ART_INSIDE_FILE_GZ && -f $SEG2ART_INSIDE_FILE_GZ);
#&IO::Compress::Gzip::gzip( $SEG2ART_INSIDE_FILE => $SEG2ART_INSIDE_FILE_GZ, Level => IO::Compress::Gzip::Z_BEST_COMPRESSION ) or die "gzip failed: $IO::Compress::Gzip::GzipError\n";
