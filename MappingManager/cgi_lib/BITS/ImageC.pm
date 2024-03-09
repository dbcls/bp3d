package BITS::ImageC;

use strict;
use warnings;
use feature ':5.10';
use Image::Info;
#use Imager;
#use ImageMagick;
use File::Spec::Functions qw(abs2rel rel2abs catdir catfile splitdir);
use File::Path;
use File::Temp qw/tempdir/;
use Data::Lock;

use constant {
	DEBUG => 0,

	IMAGEMAGICK_PATH => '/bp3d/local/ImageMagick/6.7.1-0/bin/',
	IMAGEMAGICK_COLOR_REDUCTION_OPTION => '-quality 95 +dither -colors 256 -depth 8',
	TMPFS => '/dev/shm',
};
&Data::Lock::dlock(
 my %IMAGEMAGICK_COLOR_REDUCTION_OPTION = (
		'-quality' => 95,
		'+dither'  => '',
		'-colors'  =>256,
		'-depth'   => 8
	)
);

#画像リサイズ
sub resize {
	my %args = @_;
	my $in_file = $args{'in_file'};
	my $geometry = $args{'geometry'};
	my $transparent = $args{'transparent'};
	my $quality = $args{'quality'};
	my $out_file = $args{'out_file'};

	print STDERR __LINE__.':'.__PACKAGE__."::resize():START\n" if(DEBUG);

	my $hash = &Image::Info::image_info($in_file) if(defined $in_file && -e $in_file && -s $in_file);
	my $img_size = $hash->{'width'}.'x'.$hash->{'height'} if(defined $hash);
	if(defined $in_file && defined $geometry && defined $img_size){
		if($geometry ne $img_size){
			my $cmd;
			if(defined $out_file){
				$cmd = &catfile(IMAGEMAGICK_PATH,qq|convert|);
			}else{
				$cmd = &catfile(IMAGEMAGICK_PATH,qq|mogrify|);
			}
			$quality = 95 unless(defined $quality);
			my %OPT = (
				'-geometry' => $geometry,
				'-sharpen' => 0.7,
				'-quality' => $quality
			);
			$OPT{'-transparent'} = $transparent if(defined $transparent);
			my @CMD = ($cmd,%OPT,$in_file);
			push(@CMD,$out_file) if(defined $out_file);
			print STDERR __LINE__.':'.__PACKAGE__."::resize():[".join(' ',@CMD)."]\n" if(DEBUG);
			system(join(' ',@CMD));
		}
	}else{
		die __LINE__.':'.__PACKAGE__."::resize()[$in_file][$geometry][$transparent][$out_file]\n";
	}
	print STDERR __LINE__.':'.__PACKAGE__."::resize():END\n" if(DEBUG);
}

#画像合成
sub composite {
	my %args = @_;
	my $target_file = $args{'target_file'};
	my $larger_file = $args{'larger_file'};
	my $quality = $args{'quality'};
	my $out_file = $args{'out_file'};

	print STDERR __LINE__.':'.__PACKAGE__."::composite():START\n" if(DEBUG);

	if(defined $target_file && defined $larger_file && defined $out_file && -e $target_file && -s $target_file && -e $larger_file && -s $larger_file){
#		system(IMAGEMAGICK_PATH.qq|composite -gravity southeast $larger_file $target_file |.IMAGEMAGICK_COLOR_REDUCTION_OPTION.qq| $out_file|);
#		system(IMAGEMAGICK_PATH.qq|composite -gravity southeast $larger_file $target_file $out_file|);

		my $cmd = &catfile(IMAGEMAGICK_PATH,qq|composite|);
		my %C_OPT = (
			'-gravity' => 'southeast'
		);
		$quality = 0 unless(defined $quality);
		my %S_OPT = (
			'-quality' => $quality
		);
		my @CMD = ($cmd,%C_OPT,$larger_file,$target_file);
		push(@CMD,%S_OPT);
		push(@CMD,$out_file);
		print STDERR __LINE__.':'.__PACKAGE__."::composite():[".join(' ',@CMD)."]\n" if(DEBUG);
		system(join(' ',@CMD));

	}else{
		die __LINE__.':'.__PACKAGE__."::composite()[$target_file][$larger_file][$out_file]\n";
	}
	print STDERR __LINE__.':'.__PACKAGE__."::composite():END\n" if(DEBUG);
}

#画像合成（一括）
sub composite_bulk {
	my %args = @_;
	my $target_file = $args{'target_file'};
	my $larger_file = $args{'larger_file'};
	my $out_file = $args{'out_file'};

	my $larger_geometry = $args{'larger_geometry'};
	my $larger_transparent = $args{'larger_transparent'};

	print STDERR __LINE__.':'.__PACKAGE__."::composite_bulk():START\n" if(DEBUG);

	if(defined $target_file && defined $larger_file && defined $out_file && -e $target_file && -s $target_file && -e $larger_file && -s $larger_file){

		my @CMD = ();
		my $composite = &catfile(IMAGEMAGICK_PATH,qq|composite|);
		my $convert = &catfile(IMAGEMAGICK_PATH,qq|convert|);
		my $mogrify = &catfile(IMAGEMAGICK_PATH,qq|mogrify|);

		#画像リサイズ
		my %RESIZE_OPT = (
			'-geometry' => $larger_geometry,
			'-sharpen' => 0.7,
			'-quality' => 0
		);
		$RESIZE_OPT{'-transparent'} = $larger_transparent if(defined $larger_transparent);
		push(@CMD,$convert,%RESIZE_OPT,$larger_file,'-');

		#画像合成
		my %COMP_OPT1 = (
			'-gravity' => 'southeast'
		);
		my %COMP_OPT2 = (
			'-quality' => 0
		);
		push(@CMD,'|',$composite,%COMP_OPT1,'-',$target_file,%COMP_OPT2,'-');

		#合成画像減色
		push(@CMD,'|',$convert,%IMAGEMAGICK_COLOR_REDUCTION_OPTION,'-',$out_file);

		#ターゲット画像減色
		push(@CMD,';',$mogrify,%IMAGEMAGICK_COLOR_REDUCTION_OPTION,$target_file);

		print STDERR __LINE__.':'.__PACKAGE__."::composite_bulk():[".join(' ',@CMD)."]\n" if(DEBUG);
#		system(@CMD);
		system(join(' ',@CMD));

	}else{
		die __LINE__.':'.__PACKAGE__."::composite_bulk()[$target_file][$larger_file][$out_file]\n";
	}
	print STDERR __LINE__.':'.__PACKAGE__."::composite_bulk():END\n" if(DEBUG);
}

#色
sub colors {
	my %args = @_;
	my $file = $args{'file'};
	use Image::Magick;
	my $image = Image::Magick->new;
	$image->Read($file);
	my($depth,$type,$colors) = $image->Get('depth','type','colors');
	undef $image;
	return ($depth,$type,$colors);
}

#画像減色
sub color_reduction {
	my %args = @_;
	my $in_file = $args{'in_file'};
	my $out_file = $args{'out_file'};

	if(DEBUG){
		print STDERR __LINE__.':'.__PACKAGE__."::color_reduction():START\n";
#		print STDERR __LINE__.':'.__PACKAGE__."::color_reduction():\t\$in_file=[$in_file]\n";
#		print STDERR __LINE__.':'.__PACKAGE__."::color_reduction():\t\$out_file=[$out_file]\n";
	}

	my $cmd;
	if(defined $out_file){
		$cmd = &catfile(IMAGEMAGICK_PATH,qq|convert|);
	}else{
		$cmd = &catfile(IMAGEMAGICK_PATH,qq|mogrify|);
	}
=pod
	if(defined $in_file && -e $in_file && -s $in_file){
		$cmd .= ' '.IMAGEMAGICK_COLOR_REDUCTION_OPTION;
	}
	else{
		die __LINE__.':'.__PACKAGE__."::color_reduction()[$in_file]\n";
	}
	my @CMD = ($cmd,%IMAGEMAGICK_COLOR_REDUCTION_OPTION,$in_file)
	$cmd .= qq| $in_file|;
	$cmd .= qq| $out_file| if(defined $out_file);
#	print STDERR __LINE__.':'.__PACKAGE__."::color_reduction():\t\$cmd=[$cmd]\n";
	system($cmd);
=cut

	my @CMD = ($cmd,%IMAGEMAGICK_COLOR_REDUCTION_OPTION,$in_file);
	push(@CMD,$out_file) if(defined $out_file);
	print STDERR __LINE__.':'.__PACKAGE__."::color_reduction():[".join(' ',@CMD)."]\n" if(DEBUG);
	system(join(' ',@CMD));


	my($depth,$type,$colors) = &colors(file=>(defined $out_file && -e $out_file && -s $out_file ? $out_file : $in_file));

	if(DEBUG){
		print STDERR __LINE__.':'.__PACKAGE__."::color_reduction():END\n";
		if($colors > 256){
			print STDERR __LINE__.':'.__PACKAGE__."::color_reduction():\t\$depth=[$depth]\n";
			print STDERR __LINE__.':'.__PACKAGE__."::color_reduction():\t\$type=[$type]\n";
			print STDERR __LINE__.':'.__PACKAGE__."::color_reduction():\t\$colors=[$colors]\n";
		}
#		print STDERR __LINE__.':'.__PACKAGE__."::color_reduction():\t\$maxcolors=[$maxcolors]\n";
#		print STDERR __LINE__.':'.__PACKAGE__."::color_reduction():\t\$getchannels=[$getchannels]\n";
#		die __LINE__.':'.__PACKAGE__."::color_reduction()[$in_file]\n";
	}
	return ($depth,$type,$colors);
}

#アニメーションGIF作成
sub animatedGIF {
	my %args = @_;
	my $in_files = $args{'in_files'};
	my $out_file = $args{'out_file'};
	my $geometry = $args{'geometry'};
	my $delay = $args{'delay'};
	print STDERR __LINE__.':'.__PACKAGE__."::animatedGIF():START\n" if(DEBUG);
	if(defined $in_files && ref $in_files eq 'ARRAY' && defined $out_file){
		my $cmd = &catfile(IMAGEMAGICK_PATH,qq|convert|);
		my %OPT = (
			'-dispose' => 'Background',
			'-delay' => defined $delay ? $delay : 0,
			'-loop' => 0,
			'-quality' => 95
		);
		if(defined $geometry){
			$OPT{'-geometry'} = $geometry;
			$OPT{'-sharpen'} = 0.7;
		}
		my @CMD = ($cmd,%OPT,@$in_files,$out_file);
		print STDERR __LINE__.':'.__PACKAGE__."::color_reduction():[".join(' ',@CMD)."]\n" if(DEBUG);
		system(join(' ',@CMD));


#		if(defined $geometry){
#			system(IMAGEMAGICK_PATH.qq|convert -geometry $geometry -sharpen 0.7 -dispose Background -delay 0 -loop 0 |.join(" ",@$in_files).qq| $out_file|);
#		}else{
#			system(IMAGEMAGICK_PATH.qq|convert -dispose Background -delay 0 -loop 0 |.join(" ",@$in_files).qq| $out_file|);
#		}
	}
	else{
		die __LINE__.':'.__PACKAGE__."::animgif()[$in_files][$out_file][$geometry]\n";
	}
	print STDERR __LINE__.':'.__PACKAGE__."::animatedGIF():END\n" if(DEBUG);
}


sub get_tmppath {
	my $lock_no = shift;
	if(defined $lock_no){
		return &catdir(TMPFS,$lock_no);
	}else{
		return &File::Temp::tempdir(DIR => TMPFS);
	}
}

sub unlink_tmppath {
#	my $path = &get_tmppath();
#	&File::Path::remove_tree($path) if(-e $path);
}

1;
