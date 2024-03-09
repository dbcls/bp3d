#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use File::Basename;
use File::Spec::Functions qw(abs2rel rel2abs catdir catfile splitdir);
use File::Path;
use File::Copy;
use DBD::Pg;
use IO::Compress::Gzip; # qw(gzip $GzipError) ;
use Cwd;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|,qq|$FindBin::Bin/../../cgi_lib|;
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

my $ART2SEG;

my $HTDOCS_DIR = &catdir($FindBin::Bin,'..','htdocs');
$HTDOCS_DIR = &Cwd::abs_path($HTDOCS_DIR) if(defined $HTDOCS_DIR && length $HTDOCS_DIR && -e $HTDOCS_DIR);

my $MENU_SEGMENTS_BASE_DIR = &catdir($HTDOCS_DIR,'MENU_SEGMENTS');
my $MENU_SEGMENTS_PREFECTURES_DIR = &catdir($MENU_SEGMENTS_BASE_DIR,'PREFECTURES');
my @MENU_SEGMENTS_PREFECTURES_FILES = qx/find $MENU_SEGMENTS_PREFECTURES_DIR -type f -name "*.obj"/;
chomp @MENU_SEGMENTS_PREFECTURES_FILES;

my $MENU_SEGMENTS_CITIES_DIR = &catdir($MENU_SEGMENTS_BASE_DIR,'CITIES');
my @MENU_SEGMENTS_CITIES_FILES = qx/find $MENU_SEGMENTS_CITIES_DIR -type f -name "*.obj"/;
chomp @MENU_SEGMENTS_CITIES_FILES;

my $count = scalar @MENU_SEGMENTS_CITIES_FILES;

my $PREFECTURES_NAME2PATH;
my $CITIES_NAME2PATH;

my $PREFECTURES2CITIES;
my $PREFECTURES_PROP;
my $CITIES_PROP;

my($script_name,$script_dir,$script_ext) = &File::Basename::fileparse($0,qw/.pl/);
my $DATA_DIR = &catdir($FindBin::Bin,$script_name);
&File::Path::make_path($DATA_DIR,{chmod=>0700}) unless(-e $DATA_DIR && -d $DATA_DIR);

my $PREFECTURES_NAME2PATH_DATA_FILE = &catfile($DATA_DIR,'PREFECTURES_NAME2PATH.json');
my $CITIES_NAME2PATH_DATA_FILE = &catfile($DATA_DIR,'CITIES_NAME2PATH.json');

my $PREFECTURES2CITIES_DATA_FILE = &catfile($DATA_DIR,'PREFECTURES2CITIES.json');
my $PREFECTURES_PROP_DATA_FILE = &catfile($DATA_DIR,'PREFECTURES_PROP.json');
my $CITIES_PROP_DATA_FILE = &catfile($DATA_DIR,'CITIES_PROP.json');

if(
	-e $PREFECTURES_NAME2PATH_DATA_FILE && -f $PREFECTURES_NAME2PATH_DATA_FILE && -s $PREFECTURES_NAME2PATH_DATA_FILE &&
	-e $CITIES_NAME2PATH_DATA_FILE && -f $CITIES_NAME2PATH_DATA_FILE && -s $CITIES_NAME2PATH_DATA_FILE &&
	-e $PREFECTURES2CITIES_DATA_FILE && -f $PREFECTURES2CITIES_DATA_FILE && -s $PREFECTURES2CITIES_DATA_FILE &&
	-e $PREFECTURES_PROP_DATA_FILE && -f $PREFECTURES_PROP_DATA_FILE && -s $PREFECTURES_PROP_DATA_FILE &&
	-e $CITIES_PROP_DATA_FILE && -f $CITIES_PROP_DATA_FILE && -s $CITIES_PROP_DATA_FILE
){
	$PREFECTURES_NAME2PATH = &cgi_lib::common::readFileJSON($PREFECTURES_NAME2PATH_DATA_FILE);
	$CITIES_NAME2PATH = &cgi_lib::common::readFileJSON($CITIES_NAME2PATH_DATA_FILE);

	$PREFECTURES2CITIES = &cgi_lib::common::readFileJSON($PREFECTURES2CITIES_DATA_FILE);
	$PREFECTURES_PROP = &cgi_lib::common::readFileJSON($PREFECTURES_PROP_DATA_FILE);
	$CITIES_PROP = &cgi_lib::common::readFileJSON($CITIES_PROP_DATA_FILE);
}

unless(
	defined $PREFECTURES2CITIES &&
	defined $PREFECTURES_PROP &&
	defined $CITIES_PROP
){

	foreach my $CITIES_FILE (sort @MENU_SEGMENTS_CITIES_FILES){
		my($CITIES_NAME,$dir,$ext) = &File::Basename::fileparse($CITIES_FILE,qw/.obj/);

		next if($CITIES_NAME eq 'MM2439_Pallidum HOLED');
		next if($CITIES_NAME eq 'MM2439_Pallidum_HOLED');
		next if($CITIES_NAME eq 'MM2411_EAR');
		next if($CITIES_NAME eq 'MM2412_EYE');
		next if($CITIES_NAME eq 'MM2417_PALLIUM');

	#	next unless($CITIES_NAME =~ /^(FJ|MM|CX:?)[0-9]+(.+)$/);
	#	my $obj_name = $2;
	#	say $obj_name;
	#	exit;


		printf(STDERR "[%04d] : %s\r",$count--,$CITIES_NAME);

		$CITIES_FILE = &Cwd::abs_path($CITIES_FILE) if(defined $CITIES_FILE && length $CITIES_FILE && -e $CITIES_FILE);
		$CITIES_NAME2PATH->{$CITIES_NAME} = $CITIES_FILE;

		my $obj_prop = $CITIES_PROP->{$CITIES_NAME} = &BITS::VTK::_getProperties($CITIES_FILE);
		foreach (@{$obj_prop->{'bounds'}}){
			$_ -= 0;
		}
		foreach (@{$obj_prop->{'centerOfMass'}}){
			$_ -= 0;
		}

		print STDERR "\n";
		my $POINTS = [];
		my $step = 10;
		my $x_step = ($obj_prop->{'bounds'}->[1]-$obj_prop->{'bounds'}->[0])/$step;
		my $y_step = ($obj_prop->{'bounds'}->[3]-$obj_prop->{'bounds'}->[2])/$step;
		my $z_step = ($obj_prop->{'bounds'}->[5]-$obj_prop->{'bounds'}->[4])/$step;
	#	say $x_step;
	#	say $y_step;
	#	say $z_step;
		for(my $x=$obj_prop->{'bounds'}->[0];$x<$obj_prop->{'bounds'}->[1]+$x_step;$x+=$x_step){
			for(my $y=$obj_prop->{'bounds'}->[2];$y<$obj_prop->{'bounds'}->[3]+$y_step;$y+=$y_step){
				for(my $z=$obj_prop->{'bounds'}->[4];$z<$obj_prop->{'bounds'}->[5]+$z_step;$z+=$z_step){
					push(@$POINTS,[$x,$y,$z]);
				}
			}
		}
		say scalar @$POINTS;
	#	exit;

		my $cities_inside = &BITS::VTK::pointsOutsideObject($CITIES_FILE,$POINTS);
	#	&cgi_lib::common::message($inside,\*STDOUT);
		say scalar @$cities_inside;
	#	exit;
		next unless(scalar @$cities_inside);

		foreach my $p (@$cities_inside){
			foreach (@$p){
				$_ -= 0;
			}
		}


		$ART2SEG->{$CITIES_NAME} = undef;

		my $max_incount = 0;
		my $MAX_PREFECTURES_NAME;
		foreach my $PREFECTURES_FILE (sort @MENU_SEGMENTS_PREFECTURES_FILES){
			my($PREFECTURES_NAME,$dir,$ext) = &File::Basename::fileparse($PREFECTURES_FILE,qw/.obj/);

			$PREFECTURES_NAME2PATH->{$PREFECTURES_NAME} = $PREFECTURES_FILE;

			unless(defined $PREFECTURES_PROP && exists $PREFECTURES_PROP->{$PREFECTURES_NAME}){
				my $segment_obj_prop = $PREFECTURES_PROP->{$PREFECTURES_NAME} = &BITS::VTK::_getProperties($PREFECTURES_FILE);
				foreach (@{$segment_obj_prop->{'bounds'}}){
					$_ -= 0;
				}
			}

	#		my $hash = &BITS::VTK::objectInsideObject($PREFECTURES_FILE,$CITIES_FILE);
			my $prefectures_inside = &BITS::VTK::pointsOutsideObject($PREFECTURES_FILE,$cities_inside);
			next unless(scalar @$prefectures_inside);

			my $hash;
			$hash->{'incount'} = scalar @$prefectures_inside;
			$hash->{'all'} = scalar @$cities_inside;

			if($max_incount<$hash->{'incount'}){
				$max_incount = $hash->{'incount'};
				$MAX_PREFECTURES_NAME = $PREFECTURES_NAME;
			}

	#		my $inside = &BITS::VTK::pointInsideObject($PREFECTURES_FILE,$obj_prop->{'centerOfMass'});
	#		next unless($inside);

			$dir =~ s/\/$//g;
			my @dirs = &splitdir($PREFECTURES_FILE);
			my $region = $dirs[-2];

			$ART2SEG->{$CITIES_NAME}->{$region}->{$PREFECTURES_NAME} = $hash;

	#		$PREFECTURES2CITIES->{$PREFECTURES_NAME}->{$CITIES_NAME} = undef;
		}
		if(defined $MAX_PREFECTURES_NAME){
			$PREFECTURES2CITIES->{$MAX_PREFECTURES_NAME}->{$CITIES_NAME} = undef;
		}

		unless(exists $ART2SEG->{$CITIES_NAME} && defined $ART2SEG->{$CITIES_NAME}){
			printf(STDERR "\n");
	#		printf(STDERR "%s\t%f\n",$CITIES_NAME,$obj_prop->{'volume'});

			my $min_distance;
			my $min_distance_file;
			foreach my $PREFECTURES_FILE (sort @MENU_SEGMENTS_PREFECTURES_FILES){
				my($PREFECTURES_NAME,$dir,$ext) = &File::Basename::fileparse($PREFECTURES_FILE,qw/.obj/);


				my $distance = &BITS::VTK::pointDistanceObject($PREFECTURES_FILE,$obj_prop->{'centerOfMass'});
				next if(defined $min_distance && $min_distance<$distance);
				$min_distance = $distance;
				$min_distance_file = $PREFECTURES_FILE;

			}
			if(defined $min_distance_file){
				my($PREFECTURES_NAME,$dir,$ext) = &File::Basename::fileparse($min_distance_file,qw/.obj/);
				$dir =~ s/\/$//g;
				my @dirs = &splitdir($min_distance_file);
				my $region = $dirs[-2];
				$ART2SEG->{$CITIES_NAME}->{$region}->{$PREFECTURES_NAME} = undef;

				$PREFECTURES2CITIES->{$PREFECTURES_NAME}->{$CITIES_NAME} = undef;
			}
		}



	}

	#&cgi_lib::common::message($ART2SEG,\*STDOUT);

	&cgi_lib::common::writeFileJSON(&catfile($MENU_SEGMENTS_BASE_DIR,'MENU_SEGMENTS.json'),$ART2SEG,0);
	&cgi_lib::common::writeFileJSON(&catfile($MENU_SEGMENTS_BASE_DIR,'MENU_SEGMENTS_ext.json'),$ART2SEG,1);

	&cgi_lib::common::writeFileJSON($PREFECTURES_NAME2PATH_DATA_FILE,$PREFECTURES_NAME2PATH,1);
	&cgi_lib::common::writeFileJSON($CITIES_NAME2PATH_DATA_FILE,$CITIES_NAME2PATH,1);

	&cgi_lib::common::writeFileJSON($PREFECTURES2CITIES_DATA_FILE,$PREFECTURES2CITIES,1);
	&cgi_lib::common::writeFileJSON($PREFECTURES_PROP_DATA_FILE,$PREFECTURES_PROP,1);
	&cgi_lib::common::writeFileJSON($CITIES_PROP_DATA_FILE,$CITIES_PROP,1);
}

if(defined $PREFECTURES_NAME2PATH && ref $PREFECTURES_NAME2PATH eq 'HASH'){
	foreach my $key (keys %$PREFECTURES_NAME2PATH){
		$PREFECTURES_NAME2PATH->{$key} = &rel2abs($PREFECTURES_NAME2PATH->{$key},$FindBin::Bin);
	}
}
if(defined $CITIES_NAME2PATH && ref $CITIES_NAME2PATH eq 'HASH'){
	foreach my $key (keys %$CITIES_NAME2PATH){
		$CITIES_NAME2PATH->{$key} = &rel2abs($CITIES_NAME2PATH->{$key},$FindBin::Bin);
	}
}

if(defined $PREFECTURES2CITIES){
	my $ROOT_DATA = {
		'expanded' => JSON::XS::true,
		'children' => []
	};

	my $CITIES_DATA = {					# unfound対応(2019/12/27)
		'text' => 'unfound',			# unfound対応(2019/12/27)
		'leaf' => JSON::XS::true,	# unfound対応(2019/12/27)
		'xmin' => 0,							# unfound対応(2019/12/27)
		'xmax' => 0,							# unfound対応(2019/12/27)
		'ymin' => 0,							# unfound対応(2019/12/27)
		'ymax' => 0,							# unfound対応(2019/12/27)
		'zmin' => 0,							# unfound対応(2019/12/27)
		'zmax' => 0,							# unfound対応(2019/12/27)
		'cities_id' => 0					# unfound対応(2019/12/27)
	};													# unfound対応(2019/12/27)
	$CITIES_DATA->{&BITS::Config::LOCATION_HASH_NAME_KEY()} = 'unfound';	# unfound対応(2019/12/27)
	push(@{$ROOT_DATA->{'children'}}, $CITIES_DATA);											# unfound対応(2019/12/27)


	my $PREFECTURES_ID = 0;
	my $CITIES_ID = 0;
	my $SEGMENT_ORDER = 0;

	foreach my $PREFECTURES_NAME (
		sort { &cmp_data($a,$b,$PREFECTURES_PROP) }
		keys(%$PREFECTURES2CITIES)
	){
		my($name,$dir,$ext) = &File::Basename::fileparse($PREFECTURES_NAME2PATH->{$PREFECTURES_NAME},qw/.obj/);
		my $gz_file = &catfile($dir,qq|$name.ogz|);
		unless(-e $gz_file && -f $gz_file && -s $gz_file){
			&IO::Compress::Gzip::gzip( $PREFECTURES_NAME2PATH->{$PREFECTURES_NAME} => $gz_file, Level => IO::Compress::Gzip::Z_BEST_COMPRESSION ) or die "gzip failed: $IO::Compress::Gzip::GzipError\n";
		}

		foreach my $CITIES_NAME (
			sort { &cmp_data($a,$b,$CITIES_PROP) }
			keys(%{$PREFECTURES2CITIES->{$PREFECTURES_NAME}})
		){
			my $text = &normalization_name($CITIES_NAME);
			my $CITIES_DATA = {
				'text' => $text,
				'leaf' => JSON::XS::true,
				'xmin' => $CITIES_PROP->{$CITIES_NAME}->{'bounds'}->[0],
				'xmax' => $CITIES_PROP->{$CITIES_NAME}->{'bounds'}->[1],
				'ymin' => $CITIES_PROP->{$CITIES_NAME}->{'bounds'}->[2],
				'ymax' => $CITIES_PROP->{$CITIES_NAME}->{'bounds'}->[3],
				'zmin' => $CITIES_PROP->{$CITIES_NAME}->{'bounds'}->[4],
				'zmax' => $CITIES_PROP->{$CITIES_NAME}->{'bounds'}->[5],
				'cities_id' => ++$CITIES_ID
			};

			my($name,$dir,$ext) = &File::Basename::fileparse($CITIES_NAME2PATH->{$CITIES_NAME},qw/.obj/);
			$CITIES_DATA->{&BITS::Config::LOCATION_HASH_NAME_KEY()} = $name;
			my $gz_file = &catfile($dir,qq|$name.ogz|);
			unless(-e $gz_file && -f $gz_file && -s $gz_file){
				&IO::Compress::Gzip::gzip( $CITIES_NAME2PATH->{$CITIES_NAME} => $gz_file, Level => IO::Compress::Gzip::Z_BEST_COMPRESSION ) or die "gzip failed: $IO::Compress::Gzip::GzipError\n";
			}
			$CITIES_DATA->{&BITS::Config::OBJ_URL_DATA_FIELD_ID()} = &abs2rel(&Cwd::abs_path($gz_file), $HTDOCS_DIR);

			if($CITIES_NAME =~ /^(FJ|MM|CX:?)([0-9]+M*)/){
				$CITIES_DATA->{&BITS::Config::OBJ_ID_DATA_FIELD_ID()} = $1.$2;
			}else{
				$CITIES_DATA->{&BITS::Config::OBJ_ID_DATA_FIELD_ID()} = $CITIES_NAME;
			}

			push(@{$ROOT_DATA->{'children'}}, $CITIES_DATA);
		}
	}

	my $CITIES_PREFIX = &catfile($MENU_SEGMENTS_BASE_DIR,'CITIES');

	my $CITIES_FILE_EXT = qq|${CITIES_PREFIX}_ext.json|;
	&cgi_lib::common::writeFileJSON($CITIES_FILE_EXT,$ROOT_DATA,1);

	my $CITIES_FILE = qq|${CITIES_PREFIX}.json|;
	&cgi_lib::common::writeFileJSON($CITIES_FILE,$ROOT_DATA,0);

	my $CITIES_FILE_GZ = qq|${CITIES_PREFIX}.jgz|;
	unlink $CITIES_FILE_GZ if(-e $CITIES_FILE_GZ && -f $CITIES_FILE_GZ);
#	&IO::Compress::Gzip::gzip( $CITIES_FILE => $CITIES_FILE_GZ, Level => IO::Compress::Gzip::Z_BEST_COMPRESSION ) or die "gzip failed: $IO::Compress::Gzip::GzipError\n";


#	my $PREFECTURES = {
#		'expanded' => JSON::XS::true,
#		'children' => []
#	};
	my $PREFECTURES;


	while(<DATA>){
		chomp;
		if(/^\t+/){
			if(/^\t+\s*(.+)\s*\(([0-9,\s]+)\)\s*$/){
				my $cities = $1;
				my $cities_ids = [split(/\s*,\s*/,$2)];
				$cities =~ s/\s+$//g;
				$cities =~ s/^\s+//g;
#				say sprintf("[%s]\t[%s]\t[%s]",$prefectures,$cities,join(',',@$cities_ids));
				my $CITIES_DATA = {
					'text' => sprintf("%s (%s)", $cities, join(',',@$cities_ids)),
					'segment' => $cities,
					'cities_ids' => join(',',@$cities_ids),
#					'prefectures' => $prefectures,
					'leaf' => JSON::XS::true,
				};
				my $prefectures = $PREFECTURES->[-1];
				foreach my $cities_id (@$cities_ids){
					my $cities = $ROOT_DATA->{'children'}->[$cities_id-1];

#					$CITIES_DATA->{'cities'} = [] unless(exists $CITIES_DATA->{'cities'} && defined $CITIES_DATA->{'cities'} && ref $CITIES_DATA->{'cities'} eq 'ARRAY');
#					$prefectures->{'cities'} = [] unless(exists $prefectures->{'cities'} && defined $prefectures->{'cities'} && ref $prefectures->{'cities'} eq 'ARRAY');
#					push(@{$CITIES_DATA->{'cities'}}, $cities);
#					push(@{$prefectures->{'cities'}}, $cities);

					$CITIES_DATA->{'xmin'} = $cities->{'xmin'} unless(exists $CITIES_DATA->{'xmin'} && defined $CITIES_DATA->{'xmin'});
					$CITIES_DATA->{'xmin'} = $cities->{'xmin'} if($CITIES_DATA->{'xmin'} > $cities->{'xmin'});
					$CITIES_DATA->{'ymin'} = $cities->{'ymin'} unless(exists $CITIES_DATA->{'ymin'} && defined $CITIES_DATA->{'ymin'});
					$CITIES_DATA->{'ymin'} = $cities->{'ymin'} if($CITIES_DATA->{'ymin'} > $cities->{'ymin'});
					$CITIES_DATA->{'zmin'} = $cities->{'zmin'} unless(exists $CITIES_DATA->{'zmin'} && defined $CITIES_DATA->{'zmin'});
					$CITIES_DATA->{'zmin'} = $cities->{'zmin'} if($CITIES_DATA->{'zmin'} > $cities->{'zmin'});

					$CITIES_DATA->{'xmax'} = $cities->{'xmax'} unless(exists $CITIES_DATA->{'xmax'} && defined $CITIES_DATA->{'xmax'});
					$CITIES_DATA->{'xmax'} = $cities->{'xmax'} if($CITIES_DATA->{'xmax'} < $cities->{'xmax'});
					$CITIES_DATA->{'ymax'} = $cities->{'ymax'} unless(exists $CITIES_DATA->{'ymax'} && defined $CITIES_DATA->{'ymax'});
					$CITIES_DATA->{'ymax'} = $cities->{'ymax'} if($CITIES_DATA->{'ymax'} < $cities->{'ymax'});
					$CITIES_DATA->{'zmax'} = $cities->{'zmax'} unless(exists $CITIES_DATA->{'zmax'} && defined $CITIES_DATA->{'zmax'});
					$CITIES_DATA->{'zmax'} = $cities->{'zmax'} if($CITIES_DATA->{'zmax'} < $cities->{'zmax'});

					$prefectures->{'xmin'} = $cities->{'xmin'} unless(exists $prefectures->{'xmin'} && defined $prefectures->{'xmin'});
					$prefectures->{'xmin'} = $cities->{'xmin'} if($prefectures->{'xmin'} > $cities->{'xmin'});
					$prefectures->{'ymin'} = $cities->{'ymin'} unless(exists $prefectures->{'ymin'} && defined $prefectures->{'ymin'});
					$prefectures->{'ymin'} = $cities->{'ymin'} if($prefectures->{'ymin'} > $cities->{'ymin'});
					$prefectures->{'zmin'} = $cities->{'zmin'} unless(exists $prefectures->{'zmin'} && defined $prefectures->{'zmin'});
					$prefectures->{'zmin'} = $cities->{'zmin'} if($prefectures->{'zmin'} > $cities->{'zmin'});

					$prefectures->{'xmax'} = $cities->{'xmax'} unless(exists $prefectures->{'xmax'} && defined $prefectures->{'xmax'});
					$prefectures->{'xmax'} = $cities->{'xmax'} if($prefectures->{'xmax'} < $cities->{'xmax'});
					$prefectures->{'ymax'} = $cities->{'ymax'} unless(exists $prefectures->{'ymax'} && defined $prefectures->{'ymax'});
					$prefectures->{'ymax'} = $cities->{'ymax'} if($prefectures->{'ymax'} < $cities->{'ymax'});
					$prefectures->{'zmax'} = $cities->{'zmax'} unless(exists $prefectures->{'zmax'} && defined $prefectures->{'zmax'});
					$prefectures->{'zmax'} = $cities->{'zmax'} if($prefectures->{'zmax'} < $cities->{'zmax'});
				}
				push(@{$PREFECTURES->[-1]->{'children'}}, $CITIES_DATA);
			}
		}
		else{
			my $text = $_;
			$text =~ s/\s+$//g;
			$text =~ s/^\s+//g;

			push(@$PREFECTURES, {
				'text' => $text,
				'segment' => $text,
				'expanded' => JSON::XS::true,
				'leaf' => JSON::XS::false,
				'children' => []
			});

		}
	}

	push(@$PREFECTURES, {						# unfound対応(2019/12/27)
		'text' => 'unfound (0)',			# unfound対応(2019/12/27)
		'segment' => 'unfound',				# unfound対応(2019/12/27)
		'expanded' => JSON::XS::true,	# unfound対応(2019/12/27)
		'leaf' => JSON::XS::true,			# unfound対応(2019/12/27)
		'cities_ids' => '0'						# unfound対応(2019/12/27)
	});															# unfound対応(2019/12/27)


#=pod
	my $PREFECTURES2CITIES_PREFIX = &catfile($MENU_SEGMENTS_BASE_DIR,'PREFECTURES2CITIES');

	my $PREFECTURES2CITIES_FILE_EXT = qq|${PREFECTURES2CITIES_PREFIX}_ext.json|;
	&cgi_lib::common::writeFileJSON($PREFECTURES2CITIES_FILE_EXT,$PREFECTURES,1);

	my $PREFECTURES2CITIES_FILE = qq|${PREFECTURES2CITIES_PREFIX}.json|;
	&cgi_lib::common::writeFileJSON($PREFECTURES2CITIES_FILE,$PREFECTURES,0);

	my $PREFECTURES2CITIES_FILE_GZ = qq|${PREFECTURES2CITIES_PREFIX}.jgz|;
	unlink $PREFECTURES2CITIES_FILE_GZ if(-e $PREFECTURES2CITIES_FILE_GZ && -f $PREFECTURES2CITIES_FILE_GZ);
#	&IO::Compress::Gzip::gzip( $PREFECTURES2CITIES_FILE => $PREFECTURES2CITIES_FILE_GZ, Level => IO::Compress::Gzip::Z_BEST_COMPRESSION ) or die "gzip failed: $IO::Compress::Gzip::GzipError\n";
#=cut
}


if(defined $PREFECTURES_NAME2PATH && ref $PREFECTURES_NAME2PATH eq 'HASH'){
	foreach my $key (keys %$PREFECTURES_NAME2PATH){
		$PREFECTURES_NAME2PATH->{$key} = &abs2rel($PREFECTURES_NAME2PATH->{$key},$FindBin::Bin);
	}
	&cgi_lib::common::writeFileJSON($PREFECTURES_NAME2PATH_DATA_FILE,$PREFECTURES_NAME2PATH,1);
}
if(defined $CITIES_NAME2PATH && ref $CITIES_NAME2PATH eq 'HASH'){
	foreach my $key (keys %$CITIES_NAME2PATH){
		$CITIES_NAME2PATH->{$key} = &abs2rel($CITIES_NAME2PATH->{$key},$FindBin::Bin);
	}
	&cgi_lib::common::writeFileJSON($CITIES_NAME2PATH_DATA_FILE,$CITIES_NAME2PATH,1);
}


exit;

sub normalization_name {
	my $value = shift;

	my $id;

	$value = $1 if($value =~ /^MM[0-9]+(.+)$/);

	$value = $1 . '(M)' if($value =~ /^M_+(.+)$/);
	$value = $1 if($value =~ /^_+(.+)$/);

	if($value =~ /^City\-([0-9]+)_(.+)$/i){
		$id = $1;
		$value = $2;
	}


	$value = $1 . $2 . 'L' if($value =~ /^(.+)([-_])R\(M\)$/);
	$value = $1 . $2 . 'L' if($value =~ /^(.+)([0-9]+)R\(M\)$/);

	$value = $1 . $2 . '-L' if($value =~ /^(.+)(_TRI)\(M\)$/);
	$value = $1 . $2 . '-R' if($value =~ /^(.+)(_TRI)$/);

	$value = $1 . $2 . 'L' . $3 if($value =~ /^(.+)([0-9]+)R(_\(scapula\))\(M\)$/);


	$value = $1 . '-' . $2 if($value =~ /^(.+)-_([LR])$/);
	$value = $1 . '-' . $2 if($value =~ /^(.+)_([LR])$/);

	return wantarray ? ($value,$id) : $value;
}

sub cmp_name {
	my $value = shift;
	$value = $1 if($value =~ /^([A-Z]+)/);
	return $value;
}

sub cmp_data {
	my $a = shift;
	my $b = shift;
	my $PROP = shift;

	my ($a_text,$a_id) = &normalization_name($a);
	my ($b_text,$b_id) = &normalization_name($b);

	printf(STDERR "[%s]<=>[%s] : [%d]<=>[%d]\n",$a,$b,defined $a_id ? $a_id : 0,defined $b_id ? $b_id : 0) if(defined $a_id || defined $b_id);

	if(defined $a_id && defined $b_id){

		printf(STDERR "[%s]<=>[%s] : [%d]<=>[%d] : %d\n",$a,$b,$a_id,$b_id,$a_id <=> $b_id);

		return $a_id <=> $b_id;
	}

	my $a_cmp = &cmp_name($a_text);
	my $b_cmp = &cmp_name($b_text);

	if(length($a_cmp) && $a_cmp eq $b_cmp){
		return $a_text cmp $b_text;
	}
	elsif($PROP->{$b}->{'bounds'}->[5] != $PROP->{$a}->{'bounds'}->[5]){
		return $PROP->{$b}->{'bounds'}->[5] <=> $PROP->{$a}->{'bounds'}->[5];
	}
	elsif($PROP->{$a}->{'bounds'}->[2] != $PROP->{$b}->{'bounds'}->[2]){
		return $PROP->{$a}->{'bounds'}->[2] <=> $PROP->{$b}->{'bounds'}->[2];
	}
	elsif($PROP->{$a}->{'bounds'}->[0] != $PROP->{$b}->{'bounds'}->[0]){
		return $PROP->{$a}->{'bounds'}->[0] <=> $PROP->{$b}->{'bounds'}->[0];
	}
	return 0;
}


__DATA__
HEAD
	pallium (1,2)
	basal (3)
	stem  (4)
FACE
	eye (7,8)
	nose (9)
	ear (5,6)
	mouth (10)
NECK
	throat (12)
	nape (11)
CHEST
	chest (15,16)
	mediastinum (14)
	retromediastinum (13)
	infrascapular (17,18)
ARM
	shoulder (19,20,21,22, 24,25,26,27)
	upper arm (23,28)
	elbow (45,49)
	fore arm (46,50)
	wrist (47, 51)
	hand (48, 52)
ABDOMEN
	upper (29, 30, 31)
	middle  (32,33, 34)
	lumbar (35,36,37)
	lower (38,40,41)
	genital (43,44)
	pelvis (42)
LEG
	hip (39,53,57)
	thigh/ham (54,55,56,58,59,60)
	knee (61,66)
	shin/calf (62,63,67,68)
	uncle (64,69)
	foot (65,70)
