package BITS::Obj2Hash;

use strict;
use warnings;
use feature ':5.10';

use parent 'Exporter';

#our @ISA = (Exporter);
our @EXPORT_OK = qw(convert);
our @EXPORT_FAIL = qw(Normal divideScalar lengthSq len normalize);

use strict;
use POSIX;
use Math::Round;
#use Cwd qw(abs_path);
#use File::Basename;
#use File::Path qw(mkpath);
#use JSON::XS;

#my @extlist = qw|.obj .json|;

sub convert($) {
	my $file = shift;

	return undef unless(-e $file && -r $file && -s $file);

	my($size,$mtime) = (stat($file))[7,9];
	my %OUT = (size=>$size,mtime=>$mtime);
	my $IN;

	open($IN,"< $file") || die qq|[$file] $!\n|;
	while(<$IN>){
		chomp;
		next if(/^#/);
		my @TEMP = split(/\s+/);
		if($TEMP[0] eq 'v'){
			shift @TEMP;
			foreach (@TEMP){ $_ += 0; };
			push(@{$OUT{vertices}},@TEMP);

			$OUT{xmax} = $TEMP[0] if(!defined $OUT{xmax} || $OUT{xmax} < $TEMP[0]);
			$OUT{ymax} = $TEMP[1] if(!defined $OUT{ymax} || $OUT{ymax} < $TEMP[1]);
			$OUT{zmax} = $TEMP[2] if(!defined $OUT{zmax} || $OUT{zmax} < $TEMP[2]);

			$OUT{xmin} = $TEMP[0] if(!defined $OUT{xmin} || $OUT{xmin} > $TEMP[0]);
			$OUT{ymin} = $TEMP[1] if(!defined $OUT{ymin} || $OUT{ymin} > $TEMP[1]);
			$OUT{zmin} = $TEMP[2] if(!defined $OUT{zmin} || $OUT{zmin} > $TEMP[2]);

		}elsif($TEMP[0] eq 'vn'){
			shift @TEMP;
			foreach (@TEMP){ $_ += 0; };
			push(@{$OUT{vn}},@TEMP);
		}elsif($TEMP[0] eq 'f'){
			my @V = ();
			my @N = ();
			($V[0],$N[0]) = (split(/\//,$TEMP[1]))[0,2];
			($V[1],$N[1]) = (split(/\//,$TEMP[2]))[0,2];
			($V[2],$N[2]) = (split(/\//,$TEMP[3]))[0,2];
#			warn qq|$V[0],$N[0]\n| unless($V[0] == $N[0]);
#			warn qq|$V[1],$N[1]\n| unless($V[1] == $N[1]);
#			warn qq|$V[2],$N[2]\n| unless($V[2] == $N[2]);
			$V[0]--;
			$V[1]--;
			$V[2]--;
			push(@{$OUT{indices}},@V);
		}
	}
	close($IN);

	$OUT{xcenter} = ($OUT{xmax} - $OUT{xmin}) / 2 + $OUT{xmin} if(defined $OUT{xmax} && defined $OUT{xmin});
	$OUT{ycenter} = ($OUT{ymax} - $OUT{ymin}) / 2 + $OUT{ymin} if(defined $OUT{ymax} && defined $OUT{ymin});
	$OUT{zcenter} = ($OUT{zmax} - $OUT{zmin}) / 2 + $OUT{zmin} if(defined $OUT{zmax} && defined $OUT{zmin});

	$OUT{xmax} = &Truncated($OUT{xmax}) if(defined $OUT{xmax});
	$OUT{ymax} = &Truncated($OUT{ymax}) if(defined $OUT{ymax});
	$OUT{zmax} = &Truncated($OUT{zmax}) if(defined $OUT{zmax});
	$OUT{xmin} = &Truncated($OUT{xmin}) if(defined $OUT{xmin});
	$OUT{ymin} = &Truncated($OUT{ymin}) if(defined $OUT{ymin});
	$OUT{zmin} = &Truncated($OUT{zmin}) if(defined $OUT{zmin});

	$OUT{xcenter} = &Truncated($OUT{xcenter}) if(defined $OUT{xcenter});
	$OUT{ycenter} = &Truncated($OUT{ycenter}) if(defined $OUT{ycenter});
	$OUT{zcenter} = &Truncated($OUT{zcenter}) if(defined $OUT{zcenter});

#warn "Z:$OUT{zmax}:$OUT{zmin}:$OUT{zcenter}\n";

	if(!defined $OUT{vn} || scalar @{$OUT{vn}} == 0){
		$OUT{vn} = [];
		$OUT{fn} = [];

		my @FN = ();	#面法線
		my $l = scalar @{$OUT{indices}};
		for(my $i=0;$i<$l;$i+=3){
			my @v = ();
			for(my $j=0;$j<3;$j++){
				my $p = $OUT{indices}->[$i+$j]*3;
				$v[$j] = [$OUT{vertices}->[$p],$OUT{vertices}->[$p+1],$OUT{vertices}->[$p+2]];
			}
			my $n = &Normal(@v);
			foreach (@$n){
				push(@{$OUT{fn}},&Truncated($_));
			}
			for(my $j=0;$j<3;$j++){
				my $p = $OUT{indices}->[$i+$j];
				push(@{$FN[$p]},$n);
			}
		}

		my @VN = ();	#頂点法線
		for(my $i=0;$i<$l;$i++){
			my $p = $OUT{indices}->[$i];
			my $vnl = scalar @{$FN[$p]};
			my $s = [0,0,0];
			for(my $j=0;$j<$vnl;$j++){
				$s = &Add($s,$FN[$p]->[$j]);
			}
			my $vn = &normalize($s);

			$OUT{vn}->[$p*3+0] = &Truncated($vn->[0]);
			$OUT{vn}->[$p*3+1] = &Truncated($vn->[1]);
			$OUT{vn}->[$p*3+2] = &Truncated($vn->[2]);

		}
	}

#	return encode_json(\%OUT);
	return \%OUT;
}


sub convertA3($) {
	my $file = shift;

	return undef unless(-e $file && -r $file && -s $file);

	my($size,$mtime) = (stat($file))[7,9];
	my %OUT = (size=>$size,mtime=>$mtime);
	my $IN;

	open($IN,"< $file") || die qq|[$file] $!\n|;
	while(<$IN>){
		chomp;
		next if(/^#/);
		my @TEMP = split(/\s+/);
		if($TEMP[0] eq 'v'){
			shift @TEMP;
			foreach (@TEMP){ $_ += 0; };
			push(@{$OUT{vertices}},\@TEMP);

			$OUT{xmax} = $TEMP[0] if(!defined $OUT{xmax} || $OUT{xmax} < $TEMP[0]);
			$OUT{ymax} = $TEMP[1] if(!defined $OUT{ymax} || $OUT{ymax} < $TEMP[1]);
			$OUT{zmax} = $TEMP[2] if(!defined $OUT{zmax} || $OUT{zmax} < $TEMP[2]);

			$OUT{xmin} = $TEMP[0] if(!defined $OUT{xmin} || $OUT{xmin} > $TEMP[0]);
			$OUT{ymin} = $TEMP[1] if(!defined $OUT{ymin} || $OUT{ymin} > $TEMP[1]);
			$OUT{zmin} = $TEMP[2] if(!defined $OUT{zmin} || $OUT{zmin} > $TEMP[2]);

#		}elsif($TEMP[0] eq 'vn'){
#			shift @TEMP;
#			foreach (@TEMP){ $_ += 0; };
#			push(@{$OUT{vn}},@TEMP);
		}elsif($TEMP[0] eq 'f'){
			my @V = ();
			my @N = ();
			($V[0],$N[0]) = (split(/\//,$TEMP[1]))[0,2];
			($V[1],$N[1]) = (split(/\//,$TEMP[2]))[0,2];
			($V[2],$N[2]) = (split(/\//,$TEMP[3]))[0,2];
#			warn qq|$V[0],$N[0]\n| unless($V[0] == $N[0]);
#			warn qq|$V[1],$N[1]\n| unless($V[1] == $N[1]);
#			warn qq|$V[2],$N[2]\n| unless($V[2] == $N[2]);
			$V[0]--;
			$V[1]--;
			$V[2]--;
			push(@{$OUT{faces}},\@V);
		}
	}
	close($IN);

	$OUT{xcenter} = ($OUT{xmax} - $OUT{xmin}) / 2 + $OUT{xmin} if(defined $OUT{xmax} && defined $OUT{xmin});
	$OUT{ycenter} = ($OUT{ymax} - $OUT{ymin}) / 2 + $OUT{ymin} if(defined $OUT{ymax} && defined $OUT{ymin});
	$OUT{zcenter} = ($OUT{zmax} - $OUT{zmin}) / 2 + $OUT{zmin} if(defined $OUT{zmax} && defined $OUT{zmin});

	$OUT{xmax} = &Truncated($OUT{xmax}) if(defined $OUT{xmax});
	$OUT{ymax} = &Truncated($OUT{ymax}) if(defined $OUT{ymax});
	$OUT{zmax} = &Truncated($OUT{zmax}) if(defined $OUT{zmax});
	$OUT{xmin} = &Truncated($OUT{xmin}) if(defined $OUT{xmin});
	$OUT{ymin} = &Truncated($OUT{ymin}) if(defined $OUT{ymin});
	$OUT{zmin} = &Truncated($OUT{zmin}) if(defined $OUT{zmin});

	$OUT{xcenter} = &Truncated($OUT{xcenter}) if(defined $OUT{xcenter});
	$OUT{ycenter} = &Truncated($OUT{ycenter}) if(defined $OUT{ycenter});
	$OUT{zcenter} = &Truncated($OUT{zcenter}) if(defined $OUT{zcenter});

	return \%OUT;
}


sub Truncated {
	my $v = shift;
	return undef unless(defined $v);
	my $rate = 100000;
	return int($v * $rate + 0.5) / $rate;
}

sub Normal {
	my $v1 = shift;
	my $v2 = shift;
	my $v3 = shift;

	my $vx = ($v1->[1] - $v3->[1]) * ($v2->[2] - $v3->[2]) - ($v1->[2] - $v3->[2]) * ($v2->[1] - $v3->[1]);
	my $vy = ($v1->[2] - $v3->[2]) * ($v2->[0] - $v3->[0]) - ($v1->[0] - $v3->[0]) * ($v2->[2] - $v3->[2]);
	my $vz = ($v1->[0] - $v3->[0]) * ($v2->[1] - $v3->[1]) - ($v1->[1] - $v3->[1]) * ($v2->[0] - $v3->[0]);
	my $va = sqrt(pow($vx,2) + pow($vy,2) + pow($vz,2));

	return [
		$vx==0 ? 0 : $vx/$va,
		$vy==0 ? 0 : $vy/$va,
		$vz==0 ? 0 : $vz/$va
	];
}

sub Add {
	my $v1 = shift;
	my $v2 = shift;
	return [
		$v1->[0] + $v2->[0],
		$v1->[1] + $v2->[1],
		$v1->[2] + $v2->[2]
	];
}

sub divideScalar {
	my $v = shift;
	my $s = shift;
	my $r = [];
	if($s){
		$r->[0] = $v->[0] / $s;
		$r->[1] = $v->[1] / $s;
		$r->[2] = $v->[2] / $s;
	}else{
		$r->[0] = 0;
		$r->[1] = 0;
		$r->[2] = 0;
	}
	return $r;
};

sub lengthSq {
	my $v = shift;
	return $v->[0] * $v->[0] + $v->[1] * $v->[1] + $v->[2] * $v->[2];
};

sub len {
	my $v = shift;
	return sqrt( &lengthSq($v) );
}

sub normalize {
	my $v = shift;
	return &divideScalar($v, &len($v) );
}

1;
