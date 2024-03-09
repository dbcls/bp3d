package BITS::FileConvert;

#use strict;
#use warnings;
#use feature ':5.10';

use Exporter;

@ISA = (Exporter);
#@EXPORT_OK = qw(obj2gts );
#@EXPORT_FAIL = qw(Normal divideScalar lengthSq len normalize);

use POSIX;
use Math::Round;
use File::Basename;

use Inline Python;


my @extlist = qw|.obj .gts .pl|;

sub obj2gts($$) {
	my $obj_file = shift;
	my $gts_file = shift;

	return undef unless(-e $obj_file && -r $obj_file && -s $obj_file);

	my($name,$dir,$ext) = fileparse($obj_file,@extlist);

	my %RTN = ();
	my $IN;
	my $OUT;

	my %V_HASH = ();
	my %L_HASH = ();
	my %T_HASH = ();

	my %V_CONV = ();

	my $v_cnt = 0;
	my $l_cnt = 0;

	open($IN,"< $obj_file") || die qq|[$obj_file] $!\n|;
	while(<$IN>){
		chomp;
		next if(/^#/);
		my @TEMP = split(/\s+/);
		if($TEMP[0] eq 'v'){
			$v_cnt++;
			shift @TEMP;
			foreach (@TEMP){ $_ += 0; };

			my $v_key = join(" ",@TEMP);
			if(defined $V_HASH{$v_key}){
				$V_CONV{$v_cnt} = $V_HASH{$v_key};
			}else{
				push(@{$RTN{v}},$v_key);
				my $idx = scalar @{$RTN{v}};
				$V_HASH{$v_key} = $idx;
				$V_CONV{$v_cnt} = $idx;
			}
		}elsif($TEMP[0] eq 'f'){
			my @V = ();
			push(@V,(split(/\//,$TEMP[1]))[0]+0);
			push(@V,(split(/\//,$TEMP[2]))[0]+0);
			push(@V,(split(/\//,$TEMP[3]))[0]+0);

			die "$name:Unknown POINT!![$V[0]]\n" unless(defined $V_CONV{$V[0]});
			die "$name:Unknown POINT!![$V[1]]\n" unless(defined $V_CONV{$V[1]});
			die "$name:Unknown POINT!![$V[2]]\n" unless(defined $V_CONV{$V[2]});

			if($V_CONV{$V[0]} == $V_CONV{$V[1]}){
#				warn "$name:1:DUP Point!!$V_CONV{$V[0]} $V_CONV{$V[1]}\n";
				next;
			}
			if($V_CONV{$V[1]} == $V_CONV{$V[2]}){
#				warn "$name:2:DUP Point!!$V_CONV{$V[1]} $V_CONV{$V[2]}\n";
				next;
			}
			if($V_CONV{$V[2]} == $V_CONV{$V[0]}){
#				warn "$name:3:DUP Point!!$V_CONV{$V[2]} $V_CONV{$V[0]}\n";
				next;
			}

			my @T = ();

			my $l_key1_1 = qq|$V_CONV{$V[0]} $V_CONV{$V[1]}|;
			my $l_key1_2 = qq|$V_CONV{$V[1]} $V_CONV{$V[0]}|;
			if(defined $L_HASH{$l_key1_1} || defined $L_HASH{$l_key1_2}){
				if(defined $L_HASH{$l_key1_1}){
					push(@T,$L_HASH{$l_key1_1});
				}elsif(defined $L_HASH{$l_key1_2}){
					push(@T,$L_HASH{$l_key1_2});
				}
			}else{
				$l_cnt++;
				$L_HASH{$l_key1_1} = $l_cnt;
				$L_HASH{$l_key1_2} = $l_cnt;
				push(@{$RTN{l}},$l_key1_1);
				push(@T,$l_cnt);
			}

			my $l_key2_1 = qq|$V_CONV{$V[1]} $V_CONV{$V[2]}|;
			my $l_key2_2 = qq|$V_CONV{$V[2]} $V_CONV{$V[1]}|;
			if(defined $L_HASH{$l_key2_1} || defined $L_HASH{$l_key2_2}){
				if(defined $L_HASH{$l_key2_1}){
					push(@T,$L_HASH{$l_key2_1});
				}elsif(defined $L_HASH{$l_key2_2}){
					push(@T,$L_HASH{$l_key2_2});
				}
			}else{
				$l_cnt++;
				$L_HASH{$l_key2_1} = $l_cnt;
				$L_HASH{$l_key2_2} = $l_cnt;
				push(@{$RTN{l}},$l_key2_1);
				push(@T,$l_cnt);
			}

			my $l_key3_1 = qq|$V_CONV{$V[2]} $V_CONV{$V[0]}|;
			my $l_key3_2 = qq|$V_CONV{$V[0]} $V_CONV{$V[2]}|;
			if(defined $L_HASH{$l_key3_1} || defined $L_HASH{$l_key3_2}){
				if(defined $L_HASH{$l_key3_1}){
					push(@T,$L_HASH{$l_key3_1});
				}elsif(defined $L_HASH{$l_key3_2}){
					push(@T,$L_HASH{$l_key3_2});
				}
			}else{
				$l_cnt++;
				$L_HASH{$l_key3_1} = $l_cnt;
				$L_HASH{$l_key3_2} = $l_cnt;
				push(@{$RTN{l}},$l_key3_1);
				push(@T,$l_cnt);
			}

#			warn "$name:NOT T!![",scalar @T,"]\n" if(scalar @T !=3);
			my $t_key = join(" ",sort @T);
			if(defined $T_HASH{$t_key}){
#				warn "$name:DUP T!![$t_key]\n";
			}else{
				push(@{$RTN{t}},join(" ",@T));
			}
			$T_HASH{$t_key} = "";
		}
	}
	close($IN);

	$RTN{vertices_num} = defined $RTN{v} ? scalar @{$RTN{v}} : 0;
	$RTN{edges_num}    = defined $RTN{l} ? scalar @{$RTN{l}} : 0;
	$RTN{faces_num}    = defined $RTN{t} ? scalar @{$RTN{t}} : 0;

	open($OUT,"> $gts_file");
	print $OUT $RTN{vertices_num}," ",$RTN{edges_num}," ",$RTN{faces_num},"\n";
	print $OUT join("\n",@{$RTN{v}}),"\n" if(defined $RTN{v});
	print $OUT join("\n",@{$RTN{l}}),"\n" if(defined $RTN{l});
	print $OUT join("\n",@{$RTN{t}}),"\n" if(defined $RTN{t});
	close($OUT);

	return \%RTN;
}

sub gts2obj($$) {
	my $gts_file = shift;
	my $obj_file = shift;

	return undef unless(-e $gts_file && -r $gts_file && -s $gts_file);

	my %RTN = ();
	my $IN;
	my $OUT;

	my @DATA = ();
	open($IN,"< $gts_file") || die qq|[$gts_file] $!\n|;
	while(<$IN>){
		chomp;
		next if(/^#/);
		push(@DATA,$_);
	}
	close($IN);

	my($v_num,$l_num,$t_num) = split(/\s+/,shift @DATA);
	$RTN{vertices_num} = $v_num;
	$RTN{edges_num} = $l_num;
	$RTN{faces_num} = $t_num;
	for(my $cnt=0;$cnt<$v_num;$cnt++){
		my $data = shift @DATA; 
		my @TEMP = split(/\s+/,$data);
		die "V ERROR!![$data]\n" if(scalar @TEMP != 3);
		push(@{$RTN{v}},$data);
	}
	my @L = ();
	for(my $cnt=0;$cnt<$l_num;$cnt++){
		my $data = shift @DATA; 
		my @TEMP = split(/\s+/,$data);
		die "L ERROR!![$data]\n" if(scalar @TEMP != 2);
		push(@L,\@TEMP);
	}
	for(my $cnt=0;$cnt<$t_num;$cnt++){
		my $data = shift @DATA; 
		my @TEMP = split(/\s+/,$data);
		die "T ERROR!![$data]\n" if(scalar @TEMP != 3);

		my %H = ();
		foreach my $temp (@TEMP){
			foreach my $l (@{$L[$temp-1]}){
				$H{$l} = "";
			}
		}
		die "TL ERROR!![",join(" ",sort keys(%H)),"]\n" if(scalar keys(%H) != 3);
		push(@{$RTN{f}},join(" ",sort keys(%H)));
	}

	open($OUT,"> $obj_file");
	foreach my $f (@{$RTN{v}}){
		print $OUT "v $f\n";
	}
	foreach my $f (@{$RTN{f}}){
		print $OUT "f $f\n";
	}
	close($OUT);

	return \%RTN;
}

__DATA__
__Python__

import vtk

def obj2normals(file,prefix):

	renderWindow = vtk.vtkRenderWindow()
	renderWindow.SetSize(500,500)

	renderer = vtk.vtkRenderer()
	renderWindow.AddRenderer(renderer)

	#.obj形式の読み込み
	object = vtk.vtkOBJReader()
	object.SetFileName(file)
	object.Update()

	#ラプラシアンスムージングを使用して点の座標を調整するフィルタ
	smoother = vtk.vtkSmoothPolyDataFilter()
	smoother.SetInput(object.GetOutput())
	smoother.FeatureEdgeSmoothingOn()
	smoother.Update()

	#ポリゴンメッシュの法線を計算する
	normals = vtk.vtkPolyDataNormals()
	normals.SetInputConnection(smoother.GetOutputPort())
	normals.ComputePointNormalsOn()
	normals.Update()

	#推定体積、面積、三角形メッシュの形状指数
	mass = vtk.vtkMassProperties()
	mass.SetInputConnection(normals.GetOutputPort())
	mass.Update()

#		cm3 = mass.GetVolume()
#		cm3 = cm3 / 1000	#; // mm^3->cm^3に変換

	mapper = vtk.vtkPolyDataMapper()
	mapper.SetInputConnection(normals.GetOutputPort())

	actor = vtk.vtkActor()
	actor.SetMapper(mapper)

	renderer.AddActor(actor)

	objExporter = vtk.vtkOBJExporter()
	objExporter.SetRenderWindow(renderWindow)
	objExporter.SetFilePrefix(prefix)
	objExporter.Write()

	renderer.RemoveActor(actor)

	return mass.GetVolume()
