package BITS::FreeFormObj;

#use strict;
#use warnings;
#use feature ':5.10';

use Exporter;

@ISA = (Exporter);
@EXPORT_OK = qw(Archive2Obj);
#@EXPORT_FAIL = qw(move_file);

use strict;
use Cwd qw(abs_path);
use File::Basename;
use File::Spec;
use File::Copy;
use File::Path;
use JSON::XS;
use Encode;

use BITS::Config;
use BITS::Archive;
use BITS::Obj2Hash;

my $htdocs_dir = $BITS::Config::HTDOCS_PATH;
my $upload_dir = $BITS::Config::UPLOAD_PATH;
my $bin_dir = $BITS::Config::BIN_PATH;

my @extlist = qw|.obj .json .a3|;

sub Obj2Json($$;$) {
	my $obj_file = shift;
	my $json_file = shift;
	my $a3_file = shift;
	return undef unless(-e $obj_file);

	my($name,$dir,$ext) = fileparse($obj_file,@extlist);
	my $conv_obj_prefix = File::Spec->catfile($dir,qq|$name.conv|);
	my $conv_obj_file = qq|$conv_obj_prefix$ext|;
	my $conv_mtl_file = qq|$conv_obj_prefix.mtl|;

#	warn __PACKAGE__,":",__LINE__,":\$conv_obj_prefix=[$conv_obj_prefix]\n";
#	warn __PACKAGE__,":",__LINE__,":\$conv_obj_file=[$conv_obj_file]\n";

	my $volume;
	my $points;
	my $polys;
	my $org_points;
	my $org_polys;
	my $reduction_rate;
	my $obj2mass = qq|$bin_dir/obj2mass.py|;
	if(-x $obj2mass){
		my $IN;
		open($IN,qq/$obj2mass "$obj_file" "$conv_obj_prefix"|/) || die qq|[$obj2mass] $!\n|;
		my $old = $/;
		$/ = undef;
		my $data = <$IN>;
		my($n,$v,$p1,$p2,$r,$o1,$o2) = split(/\t/,$data);
		close($IN);
		$/ = $old;
		$volume = $v+0 if(defined $v);
		$points = $p1+0 if(defined $p1);
		$polys  = $p2+0 if(defined $p2);
		$reduction_rate = $r +0 if(defined $r);
		$org_points     = $o1+0 if(defined $o1);
		$org_polys      = $o2+0 if(defined $o2);
	}

	my $json;
	if(-e $conv_obj_file){
		$json = &BITS::Obj2Hash::convert($conv_obj_file);
	}elsif(-e $obj_file){
		$json = &BITS::Obj2Hash::convert($obj_file);
	}
#	warn __PACKAGE__,":",__LINE__,":\$json=[$json]\n";
#	unlink $conv_obj_file if(-e $conv_obj_file);
#	unlink $conv_mtl_file if(-e $conv_mtl_file);
	return undef unless(defined $json);

	my($org_size,$org_mtime) = (stat($obj_file))[7,9];

	my $RTN = {
		name    => $name,
		mtime   => $org_mtime,
		size    => $org_size,
		conv_mtime => $json->{mtime},
		conv_size  => $json->{size},
		xmax    => $json->{xmax},
		ymax    => $json->{ymax},
		zmax    => $json->{zmax},
		xmin    => $json->{xmin},
		ymin    => $json->{ymin},
		zmin    => $json->{zmin},
		xcenter => $json->{xcenter},
		ycenter => $json->{ycenter},
		zcenter => $json->{zcenter}
	};
	$RTN->{volume} = &BITS::Obj2Hash::Truncated($volume/1000) if(defined $volume);
	$RTN->{points} = $points if(defined $points);
	$RTN->{polys}  = $polys  if(defined $polys);
	$RTN->{reduction_rate} = $reduction_rate if(defined $reduction_rate);
	$RTN->{org_points}     = $org_points     if(defined $org_points);
	$RTN->{org_polys}      = $org_polys      if(defined $org_polys);

	delete $json->{mtime};
	delete $json->{size};
	delete $json->{xmax};
	delete $json->{ymax};
	delete $json->{zmax};
	delete $json->{xmin};
	delete $json->{ymin};
	delete $json->{zmin};
	delete $json->{xcenter};
	delete $json->{ycenter};
	delete $json->{zcenter};

	open(OUT,"> $json_file");
	print OUT encode_json($json);
	close(OUT);
	my($json_size,$json_mtime) = (stat($json_file))[7,9];
	$RTN->{json_size} = $json_size;
	$RTN->{json_mtime} = $json_mtime;

	if(defined $a3_file){
		my $a3 = &BITS::Obj2Hash::convertA3($conv_obj_file);
		if(defined $a3){
			delete $a3->{mtime};
			delete $a3->{size};
			delete $a3->{xmax};
			delete $a3->{ymax};
			delete $a3->{zmax};
			delete $a3->{xmin};
			delete $a3->{ymin};
			delete $a3->{zmin};
			delete $a3->{xcenter};
			delete $a3->{ycenter};
			delete $a3->{zcenter};

			open(OUT,"> $a3_file");
			print OUT encode_json($a3);
			close(OUT);
		}
	}

	return $RTN;
}

sub Archive2Obj($) {
	my $archive_file = shift;
	my $prefix = basename($archive_file,@BITS::Archive::ExtList);
	$prefix = File::Spec->catdir($upload_dir,qq|.$prefix|);
	my $FILES = &BITS::Archive::extract($archive_file,$prefix);
	return unless(defined $FILES);

	my @LIST = ();

	foreach my $file (@$FILES){
		my($name,$dir,$ext) = fileparse($file,@extlist);
		my $json_file = File::Spec->catfile($dir,qq|$name.json|);
		unlink($json_file) if(-e $json_file);

		my $json = &Obj2Json($file,$json_file);
		next unless(defined $json);
		push(@LIST,$json);
	}

	if(scalar @LIST > 0){
		@LIST = sort {$b->{zcenter} <=> $a->{zcenter}} @LIST;
		my $all = File::Spec->catfile($prefix,qq|all.json|);
		open(OUT,"> $all");
		print OUT encode_json(\@LIST);
		close(OUT);

		my $name = basename($archive_file,@BITS::Archive::ExtList);
		my $to = File::Spec->catdir($upload_dir,$name);
		rmtree($to) if(-e $to);
		&File::Copy::move($prefix,$to);

		my $js_uploads = File::Spec->catdir($htdocs_dir,'js','uploads',$name);
		mkpath($js_uploads,{mode=>0777}) unless(-e $js_uploads);
		chmod 0777,$js_uploads;
		unlink $js_uploads if(-e $js_uploads);
		symlink $to, $js_uploads;
	}
	undef @LIST;
}

sub DeleteObj($) {
	my $dir = shift;
#	my $name = basename($dir,@BITS::Archive::ExtList);
	my $name = basename($dir);
	my $js_uploads = File::Spec->catdir($htdocs_dir,'js','uploads',$name);
	unlink $js_uploads if(-e $js_uploads);

	my $to = File::Spec->catdir($upload_dir,$name);
	rmtree($to) if(-e $to);
}

sub RenameObj($) {
	my $old_name = shift;
	my $new_name = shift;

#	my $old_dirname = basename($old_name,@BITS::Archive::ExtList);
#	my $new_dirname = basename($new_name,@BITS::Archive::ExtList);
	my $old_dirname = basename($old_name);
	my $new_dirname = basename($new_name);
	my $js_uploads = File::Spec->catdir($htdocs_dir,'js','uploads',$old_dirname);
	unlink $js_uploads if(-e $js_uploads);

	my $old_path = File::Spec->catdir($upload_dir,$old_dirname);
	if(-e $old_path){
		my($atime,$mtime,$ctime) = (stat($old_path))[8..10];
		my $new_path = File::Spec->catdir($upload_dir,$new_name);
		&File::Copy::move($old_path,$new_path);
		if(-e $new_path){
			my $js_uploads = File::Spec->catdir($htdocs_dir,'js','uploads',$new_dirname);
			symlink $new_path, $js_uploads;
			utime $atime,$mtime,$new_path;
		}
	}
}

1;
