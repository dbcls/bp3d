package renderer;

use strict;
use vars qw($VERSION @ISA @EXPORT);
$VERSION = "0.01";

use Exporter;
use FindBin;
#use lib "$FindBin::Bin/../lib";

@ISA=qw(Exporter);

use constant DEF_PORT => 5016;

@EXPORT = qw/DEF_PORT/;

use Inline (
	Config => 
		DIRECTORY => qq|$FindBin::Bin/_Inline|,
);

use Inline Python => <<'END_OF_PYTHON_CODE';
import sys
sys.path.append('/bp3d/BackStageEditor/cron')
from obj2image import OBJ2IMAGE
#import obj2image
from bp3d_objs import BP3D_OBJS

def new_bp3d_objs():
	return BP3D_OBJS()

def new_obj2image(bp3d_objs,useRenderer,size,maxAzimuth):
	return OBJ2IMAGE(bp3d_objs,useRenderer,size,maxAzimuth)
#	return obj2image(bp3d_objs,useRenderer)

#op = obj2image()
#op = None

#def obj2animgif(size,color,obj_files1,obj_files2,dest_prefix,yRange,largerbbox,largerbboxYRange):
#	if size:
#		op.setSize(size)
#	if color:
#		op.setColor(color)
#	return op.animgif(obj_files1,obj_files2,dest_prefix,yRange,largerbbox,largerbboxYRange)

#def obj2png(size,color,obj_files1,obj_files2,dest_prefix,angle,yRange,largerbbox,largerbboxYRange):
#	if size:
#		op.setSize(size)
#	if color:
#		op.setColor(color)
#	return op.png(obj_files1,obj_files2,dest_prefix,angle,yRange,largerbbox,largerbboxYRange)

#def bound(obj_files):
#	return op.bound(obj_files)

#def python_end():
#	op.__del__()
END_OF_PYTHON_CODE

1;
