package obj2deci;

use strict;
#use warnings;
#use feature ':5.10';
use vars qw($VERSION);
$VERSION = "0.01";

use JSON::XS;
use File::Copy;
use File::Basename;


use Inline Python => <<'PYTHON';
import sys
sys.path.append('../cgi_lib')
from obj2deci import obj2deci

od = obj2deci()

def getProperties(files):
	return od.getProperties(files)

def obj2normals(files,prefix):
	return od.normals(files,prefix)

#ポリゴンを削減
def quadricDecimation(files,prefix,reduction=.9):
	return od.quadricDecimation(files,prefix,reduction)

def booleanOperationRate(files1,files2,prefix=None):
	return od.booleanOperationRate(files1,files2,prefix)

#リフレクション（ミラーリング）
def reflection(files,prefix):
	return od.reflection(files,prefix)

def objDeleteAll():
	return od.objDeleteAll()
PYTHON

use constant {
	OBJ_EXT_LIST => ['.obj'],
	DEF_MIN_POLYS => 800,

#	DEF_REDUCTION => 0.85,
	DEF_REDUCTION => 0.8
};

sub obj2deci {
	my $obj_file = shift;
	my $prefix = shift;

	my $obj_normals_file = qq|$prefix.obj|;
	my $prefix_deci = qq|$prefix.deci|;
	my $obj_deci_file = qq|$prefix_deci.obj|;
	my $attr_file = qq|$prefix.attr|;
	my $deci_attr_file = qq|$prefix.deci.attr|;

	my $obj_mtime = (stat($obj_file))[9];
	my $obj_prop = &getProperties($obj_file);
	&obj2normals($obj_file,$prefix);
	my $mtl_file = qq|$prefix.mtl|;
	if(-e $mtl_file){
#		warn __LINE__,":",&File::Basename::basename($mtl_file),"\n";
		unlink $mtl_file;
	}
	my $temp_obj_normals_file = qq|$obj_normals_file.$$|;
	system(qq{sed -e "/^mtllib/d" "$obj_normals_file" | sed -e "/^#/d" | sed -e "/^ *\$/d" | sed -e "/^\$/d" > "$temp_obj_normals_file";mv "$temp_obj_normals_file" "$obj_normals_file"});

	next unless(-e $obj_normals_file);
	$obj_file = $obj_normals_file;
	utime $obj_mtime,$obj_mtime,$obj_normals_file;

	my $deci_prop;
	my $reduction = DEF_REDUCTION;
	if($obj_prop->{polys}>DEF_MIN_POLYS){
		my $polys = $obj_prop->{polys}*(1-$reduction);
		$reduction = DEF_MIN_POLYS/$obj_prop->{polys} if($polys<DEF_MIN_POLYS);
#		warn $reduction,"\n";
		&quadricDecimation($obj_file,$prefix_deci,$reduction);
		my $deci_mtl = qq|$prefix_deci.mtl|;
		if(-e $deci_mtl){
			unlink $deci_mtl;
		}
		my $temp_obj_deci_file = qq|$obj_deci_file.$$|;
		system(qq{sed -e "/^mtllib/d" "$obj_deci_file" | sed -e "/^#/d" | sed -e "/^ *\$/d" | sed -e "/^\$/d" > "$temp_obj_deci_file";mv "$temp_obj_deci_file" "$obj_deci_file"});
	}else{
		&File::Copy::copy($obj_file,$obj_deci_file);
	}
	utime $obj_mtime,$obj_mtime,$obj_deci_file;
	&objDeleteAll();
}

sub Truncated {
	my $v = shift;
	return undef unless(defined $v);
	my $rate = 100000;
	return int($v * $rate + 0.5) / $rate;
}

1;
