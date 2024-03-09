use strict;

require "common.pl";

use Image::Magick;
use GD;
use JSON::XS;
use File::Path;
use AG::API::JSONParser;

require "common_db.pl";

my $dbh = &get_dbh();

my $lock_common_image;

#	my $image_output_type = qq|PNG8|;
my $image_output_type = qq|PNG|;	#画像出力フォーマット
my $image_color_reduction = 0;	#減色


$SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit_common_image";
sub sigexit_common_image {
	my($date) = `date`;
	$date =~ s/\s*$//g;
	print STDERR "[$date] KILL THIS CGI!![$ENV{SCRIPT_NAME}]\n";
	rmdir $lock_common_image if(defined $lock_common_image && -e $lock_common_image);
	exit(1);
}

sub make_bbox {
	my $out_dir = shift;
	my $version = shift;
	my $type = shift;
	my $f_id = shift;
	my $f_pid = shift;
	my $point_parent = shift;

	my $bbox_file = qq|$out_dir/$f_id.txt|;
	my $none_file = qq|$out_dir/$f_id.none|;
	return undef if(-e $bbox_file || -e $none_file);

	$lock_common_image = qq|$out_dir/$f_id.bbox.lock|;

	if(!mkdir($lock_common_image)){
		undef $lock_common_image;
		return undef;
	}

	unlink $bbox_file if(-e $bbox_file);
	unlink $none_file if(-e $none_file);

	my $phy_id = &get_phy_id($f_id);
	my($AgBoundingBox,$jsonObj) = &make_bbox_file($out_dir,$version,$type,$phy_id,$f_id,$f_pid,$point_parent);
	if(defined $AgBoundingBox){
		open(OUT,"> $bbox_file");
		my $json = encode_json($AgBoundingBox);
		$json =~ s/"(true|false)"/$1/mg;
		print OUT $json;
		close(OUT);
		if(
			$AgBoundingBox->{xmax} != 0 || $AgBoundingBox->{xmin} != 0 ||
			$AgBoundingBox->{ymax} != 0 || $AgBoundingBox->{ymin} != 0 ||
			$AgBoundingBox->{zmax} != 0 || $AgBoundingBox->{zmin} != 0
		){
			if(defined $type){
				my $bp3d_table = &getBP3DTablename($version);
				my $sth_update;
				if($type eq "1"){
					$sth_update = $dbh->prepare(qq|update $bp3d_table set b_xmin=?,b_xmax=?,b_ymin=?,b_ymax=?,b_zmin=?,b_zmax=? where b_id=?|);
				}elsif($type eq "3"){
					$sth_update = $dbh->prepare(qq|update $bp3d_table set b_xmin_isa=?,b_xmax_isa=?,b_ymin_isa=?,b_ymax_isa=?,b_zmin_isa=?,b_zmax_isa=? where b_id=?|);
				}elsif($type eq "4"){
					$sth_update = $dbh->prepare(qq|update $bp3d_table set b_xmin_partof=?,b_xmax_partof=?,b_ymin_partof=?,b_ymax_partof=?,b_zmin_partof=?,b_zmax_partof=? where b_id=?|);
				}
				if(defined $sth_update){
					$sth_update->execute($AgBoundingBox->{xmin},$AgBoundingBox->{xmax},$AgBoundingBox->{ymin},$AgBoundingBox->{ymax},$AgBoundingBox->{zmin},$AgBoundingBox->{zmax},$f_id);
					$sth_update->finish;
					undef $sth_update;
				}
			}
		}else{
			system(qq|touch $none_file|) unless(-e $none_file);
		}
	}
	if(-e $none_file && -s qq|$out_dir/$f_id.gif|){
		opendir(DIR,$out_dir);
		my @f = grep { /^$f_id\_.*\.(?:gif|png)$/ } readdir(DIR);
		closedir(DIR);
		foreach my $file (@f){
			my $temp = qq|$out_dir/$file|;
			next if(-z $temp);
			unlink $temp;
			system(qq|touch $temp|) if($file =~ /\.gif$/);
		}
		my $temp = qq|$out_dir/$f_id.png|;
		unlink $temp if(-e $temp);

		my $temp = qq|$out_dir/$f_id.gif|;
		if(-e $temp && -s $temp){
			unlink $temp;
			system(qq|touch $temp|);
		}
	}

	rmdir $lock_common_image if(defined $lock_common_image && -e $lock_common_image);
	undef $lock_common_image;
	return($AgBoundingBox,$jsonObj);
}

sub make_bbox_file {
	my $out_dir = shift;
	my $version = shift;
	my $type = shift;
	my $phy_id = shift;
	my $f_id = shift;
	my $f_pid = shift;
	my $point_parent = shift;

	my $geometry_S = qq|120x120|;
	my $geometry_L = qq|640x640|;

	my $position_RO = qq|rotate|;

	my $txt_file = qq|$out_dir/$f_id.txt|;
	my $gif_file = qq|$out_dir/$f_id.gif|;
	my $gif_file_S  = qq|$out_dir/|.&getImageFilename($f_id,$position_RO,$geometry_S);#$f_id\_120x120.gif|;
	my $gif_file_L  = qq|$out_dir/|.&getImageFilename($f_id,$position_RO,$geometry_L);#$f_id\_640x640.gif
	my $gif_file_SC = qq|$out_dir/|.&getImageFilename($f_id,$position_RO,$geometry_S,'1');
	my $gif_file_LC = qq|$out_dir/|.&getImageFilename($f_id,$position_RO,$geometry_L,'1');

	return undef if(-e $txt_file);

	my $r = 204;
	my $g = 204;
	my $b = 204;
	my $color = qq|CCCCCC|;

	my $r = 153;
	my $g = 0;
	my $b = 0;
	my $color = qq|990000|;

	my $opacity;
	if(defined $phy_id){
		if($phy_id eq "1"){
			$r = 204;
			$g = 0;
			$b = 0;
			$color = qq|CC0000|;
		}elsif($phy_id eq "2"){
			$r = 74;
			$g = 74;
			$b = 255;
			$color = qq|4A4AFF|;
		}
	}

	my $soap = {};
	$soap->{Common}->{Version} = $version;
	{
		my $tg_model;
		my $sth = $dbh->prepare(qq|select b.tg_model from tree_group_item as a left join (select tg_id,tg_model from tree_group) as b on a.tg_id=b.tg_id where a.tgi_version=?|);
		$sth->execute($version);
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$tg_model, undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;
		$soap->{Common}->{Model} = $tg_model if(defined $tg_model);
	}
	return undef unless(defined $soap->{Common}->{Model});

	$soap->{Window}->{ImageWidth} = 640;
	$soap->{Window}->{ImageHeight} = 640;
	$soap->{Window}->{BackgroundColor} = 'FAFAFA';
	$soap->{Common}->{TreeName} = "bp3d";
	if(defined $type){
		if($type eq "3"){
			$soap->{Common}->{TreeName} = "isa";
		}elsif($type eq "4"){
			$soap->{Common}->{TreeName} = "partof";
		}
	}
	my $org = {};
	unless(defined $f_pid){
		$org->{PartID} = $f_id;
		$org->{PartColor} = $color;
		push @{$soap->{Part}}, $org;
	}else{
		$org->{PartID} = $f_pid;
		$org->{PartColor} = qq|F0D2A0|;
		$org->{PartOpacity} = 0.05;
		$org->{UseForBoundingBoxFlag} = JSON::XS::false;
		push @{$soap->{Part}}, $org;
		$org = {};
		$org->{PartID} = $f_id;
		$org->{PartColor} = $color;
		$org->{PartOpacity} = $opacity if(defined $opacity);
		push @{$soap->{Part}}, $org;
	}

	my $maxZoom = 0;
	my $maxcamera = "front";
	my @cameras = ("front", "left");
	my $Camera;
	foreach my $camera (@cameras) {
		$soap->{Camera}->{CameraMode} = $camera;
		$soap->{Camera}->{Zoom} = 0;
		my $json = encode_json($soap);
		my $parser = new AG::API::JSONParser($json);
		my $content = $parser->getMethodContent('focus') if(defined $parser);
		unless(defined $content){
			warn __LINE__,":ERROR!![focus]\n";
			&sigexit_common_image();
		}
		my $jsonObj = decode_json($content) if(defined $content);
		if(defined $jsonObj && defined $jsonObj->{Camera} && defined $jsonObj->{Camera}->{Zoom}){
			if(!defined $Camera || $jsonObj->{Camera}->{Zoom} < $maxZoom){
				$maxZoom = $jsonObj->{Camera}->{Zoom};
				$maxcamera = $camera;
				$Camera = $jsonObj->{Camera};
			}
		}
	}

	$soap->{Camera} = $Camera;
	$soap->{Camera}->{CameraMode} = qq|camera|;
	my $json = encode_json($soap);
	my $parser = new AG::API::JSONParser($json);
	my $content = $parser->getMethodContent('focusClip') if(defined $parser);
	unless(defined $content){
		warn __LINE__,":ERROR!![focusClip]\n";
		&sigexit_common_image();
	}
	my $jsonObj = decode_json($content) if(defined $content);
	my $AgBoundingBox;
	if(defined $jsonObj){
		$AgBoundingBox = {};
		foreach my $key (sort keys(%{$jsonObj->{BoundingBox}})){
			$AgBoundingBox->{lc($key)} = $jsonObj->{BoundingBox}->{$key} if(ref $jsonObj->{BoundingBox}->{$key} == "");
		}
	}
	undef $jsonObj;

	if(defined $AgBoundingBox &&
		$AgBoundingBox->{xmax} == 0 && $AgBoundingBox->{xmin} == 0 &&
		$AgBoundingBox->{ymax} == 0 && $AgBoundingBox->{ymin} == 0 &&
		$AgBoundingBox->{zmax} == 0 && $AgBoundingBox->{zmin} == 0
	){
		system(qq|touch $gif_file|);
		system(qq|touch $gif_file_S|);
		system(qq|touch $gif_file_L|);
		system(qq|touch $gif_file_SC|);
		system(qq|touch $gif_file_LC|);
	}

	$parser->{jsonObj}->{Camera}->{AddLongitudeDegree} = 0;
	return ($AgBoundingBox,$parser->{jsonObj});
}

sub make_image {
	my $out_dir = shift;
	my $version = shift;
	my $type = shift;
	my $f_id = shift;
	my $f_pid = shift;
	my $point_parent = shift;

	my $none_file = qq|$out_dir/$f_id.none|;
	return undef if(-e $none_file);

	$lock_common_image = qq|$out_dir/$f_id.lock|;

	unless(mkdir($lock_common_image)){
		undef $lock_common_image;
		return undef;
	}

	my $phy_id = &get_phy_id($f_id);
	my $AgBoundingBox = &make_image_file($out_dir,$version,$type,$phy_id,$f_id,$f_pid,$point_parent);
=pod
	if(!defined $AgBoundingBox && -e $bbox_file){
		open(JSON_IN,"< $bbox_file");
		my @TEMP = <JSON_IN>;
		close(JSON_IN);
		my $json_text = join("",@TEMP);
		$json_text =~ s/\s*$//g;
		$json_text =~ s/^\s*//g;
#		$AgBoundingBox =  from_json($json_text) if($json_text ne "");
		$AgBoundingBox =  decode_json($json_text) if($json_text ne "");
	}
	if(-e $none_file && -s qq|$out_dir/$f_id.gif|){
		opendir(DIR,$out_dir);
		my @f = grep { /^$f_id\_.*\.(?:gif|png)$/ } readdir(DIR);
		closedir(DIR);
		warn __LINE__,":[$f_id]=[",(scalar @f),"]\n";
		foreach my $file (@f){
			my $temp = qq|$out_dir/$file|;
			warn __LINE__,":[$file]=[",(-s $temp),"]\n";
			next if(-z $temp);
			unlink $temp;
			system(qq|touch $temp|) if($file =~ /\.gif$/);
		}
		my $temp = qq|$out_dir/$f_id.png|;
		unlink $temp if(-e $temp);

		my $temp = qq|$out_dir/$f_id.gif|;
		if(-e $temp && -s $temp){
			unlink $temp;
			system(qq|touch $temp|);
		}
	}elsif(defined $AgBoundingBox){
		if(!-e $bbox_file){
			open(OUT,"> $bbox_file");
#			my $json = to_json($AgBoundingBox);
			my $json = encode_json($AgBoundingBox);
			$json =~ s/"(true|false)"/$1/mg;
			print OUT $json;
			close(OUT);
		}
		if(
			$AgBoundingBox->{xmax} != 0 || $AgBoundingBox->{xmin} != 0 ||
			$AgBoundingBox->{ymax} != 0 || $AgBoundingBox->{ymin} != 0 ||
			$AgBoundingBox->{zmax} != 0 || $AgBoundingBox->{zmin} != 0
		){
			if(defined $type && $type eq "1"){
				my $bp3d_table = &getBP3DTablename($version);
				my $sth_update = $dbh->prepare(qq|update $bp3d_table set b_xmin=?,b_xmax=?,b_ymin=?,b_ymax=?,b_zmin=?,b_zmax=? where b_id=?|);
				$sth_update->execute($AgBoundingBox->{xmin},$AgBoundingBox->{xmax},$AgBoundingBox->{ymin},$AgBoundingBox->{ymax},$AgBoundingBox->{zmin},$AgBoundingBox->{zmax},$f_id);
				$sth_update->finish;
				undef $sth_update;
			}
		}else{
			system(qq|touch $none_file|) unless(-e $none_file);
		}
	}
=cut

	rmdir $lock_common_image if(defined $lock_common_image && -e $lock_common_image);
	undef $lock_common_image;
	return $AgBoundingBox;
}

sub make_image_file {
	my $out_dir = shift;
	my $version = shift;
	my $type = shift;
	my $phy_id = shift;
	my $f_id = shift;
	my $f_pid = shift;
	my $point_parent = shift;


#回転画像を生成しない場合
#	my $FILE_NUM = 4;
##	my $addLongitude = 90;
#回転画像を生成する場合
	my $FILE_NUM = 72;
##	my $addLongitude = 5;

	my $addLongitude = 360/$FILE_NUM;


	my $dispose = 'Background';
#	my $dispose = 'none';

	my $blur = 0.7;
	my $geometry_S = qq|120x120|;
	my $geometry_L = qq|640x640|;

	my $position_RO = qq|rotate|;
	my $position_F  = qq|front|;
	my $position_L  = qq|left|;
	my $position_B  = qq|back|;
	my $position_R  = qq|right|;

	my $txt_file = qq|$out_dir/$f_id.txt|;
	my $gif_file = qq|$out_dir/$f_id.gif|;
	my $gif_file_S  = qq|$out_dir/|.&getImageFilename($f_id,$position_RO,$geometry_S);#$f_id\_120x120.gif|;
	my $gif_file_L  = qq|$out_dir/|.&getImageFilename($f_id,$position_RO,$geometry_L);#$f_id\_640x640.gif
	my $gif_file_SC = qq|$out_dir/|.&getImageFilename($f_id,$position_RO,$geometry_S,'1');
	my $gif_file_LC = qq|$out_dir/|.&getImageFilename($f_id,$position_RO,$geometry_L,'1');


	return undef if(-e $txt_file && -e $gif_file && -e $gif_file_S && -e $gif_file_L && -e $gif_file_SC && -e $gif_file_LC);

	my $png_file_F_L  = qq|$out_dir/|.&getImageFilename($f_id,$position_F,$geometry_L);
	my $png_file_F_LC = qq|$out_dir/|.&getImageFilename($f_id,$position_F,$geometry_L,'1');
	my $png_file_F_S  = qq|$out_dir/|.&getImageFilename($f_id,$position_F,$geometry_S);
	my $png_file_F_SC = qq|$out_dir/|.&getImageFilename($f_id,$position_F,$geometry_S,'1');

	my $png_file_L_L  = qq|$out_dir/|.&getImageFilename($f_id,$position_L,$geometry_L);
	my $png_file_L_LC = qq|$out_dir/|.&getImageFilename($f_id,$position_L,$geometry_L,'1');
	my $png_file_L_S  = qq|$out_dir/|.&getImageFilename($f_id,$position_L,$geometry_S);
	my $png_file_L_SC = qq|$out_dir/|.&getImageFilename($f_id,$position_L,$geometry_S,'1');

	my $png_file_B_L  = qq|$out_dir/|.&getImageFilename($f_id,$position_B,$geometry_L);
	my $png_file_B_LC = qq|$out_dir/|.&getImageFilename($f_id,$position_B,$geometry_L,'1');
	my $png_file_B_S  = qq|$out_dir/|.&getImageFilename($f_id,$position_B,$geometry_S);
	my $png_file_B_SC = qq|$out_dir/|.&getImageFilename($f_id,$position_B,$geometry_S,'1');

	my $png_file_R_L  = qq|$out_dir/|.&getImageFilename($f_id,$position_R,$geometry_L);
	my $png_file_R_LC = qq|$out_dir/|.&getImageFilename($f_id,$position_R,$geometry_L,'1');
	my $png_file_R_S  = qq|$out_dir/|.&getImageFilename($f_id,$position_R,$geometry_S);
	my $png_file_R_SC = qq|$out_dir/|.&getImageFilename($f_id,$position_R,$geometry_S,'1');

#回転画像を生成しない場合
	if($FILE_NUM==4 &&
		 -e $png_file_F_L && -e $png_file_F_LC && -e $png_file_F_S && -e $png_file_F_SC &&
		 -e $png_file_L_L && -e $png_file_L_LC && -e $png_file_L_S && -e $png_file_L_SC &&
		 -e $png_file_B_L && -e $png_file_B_LC && -e $png_file_B_S && -e $png_file_B_SC &&
		 -e $png_file_R_L && -e $png_file_R_LC && -e $png_file_R_S && -e $png_file_R_SC
	){
		return undef;
	}
	unlink $gif_file if(-e $gif_file);

#warn __LINE__,":[$version][$f_id][$f_pid]\n";

	my $temp_file = qq|$out_dir/_$$.gif|;

	my $base_img_dir = qq|$out_dir/png|;
	mkdir $base_img_dir if(!-e $base_img_dir);
	chmod 0777,$base_img_dir;

	my $img_dir = qq|$base_img_dir/$f_id|;

	my @IMG_FILES = ();
	if(-e $img_dir){
		opendir(DIR,$img_dir);
		@IMG_FILES = sort grep /\.png$/, readdir(DIR);
		closedir(DIR);
	}

#	if(scalar @IMG_FILES == 72 && -e $gif_file && (!-e $gif_file_S || !-e $gif_file_L)){
#	if(scalar @IMG_FILES == $FILE_NUM && -e $gif_file && (!-e $gif_file_S || !-e $gif_file_L || !-e $gif_file_SC || !-e $gif_file_LC)){
	if(scalar @IMG_FILES == 72 && -e $gif_file && (!-e $gif_file_S || !-e $gif_file_L || !-e $gif_file_SC || !-e $gif_file_LC)){
#warn qq|$version\t$f_id\t$f_pid\n|;
		my $im_gif_S = Image::Magick->new();
		my $im_gif_L = Image::Magick->new();

		foreach my $img_file (@IMG_FILES){
			my $im = Image::Magick->new();
			$im->Read(qq|$img_dir/$img_file|);
			$im->Resize(geometry=>$geometry_S,blur=>$blur);
			push(@$im_gif_S, $im);
			undef $im;

			my $im = Image::Magick->new();
			$im->Read(qq|$img_dir/$img_file|);
			push(@$im_gif_L, $im);
			undef $im;
		}
		$im_gif_S->Set(dispose=>'Background', delay=>0, loop=>0);
		$im_gif_S->Write($temp_file);
		@$im_gif_S = ();
		undef $im_gif_S;
		rename $temp_file,$gif_file_S if(-e $temp_file);
		chmod 0666,$gif_file_S;

		$im_gif_L->Set(dispose=>'Background', delay=>0, loop=>0);
		$im_gif_L->Write($temp_file);
		@$im_gif_L = ();
		undef $im_gif_L;
		rename $temp_file,$gif_file_L if(-e $temp_file);
		chmod 0666,$gif_file_L;

		return undef if(-e $txt_file);
	}

	my $r = 204;
	my $g = 204;
	my $b = 204;
	my $color = qq|CCCCCC|;

	my $r = 153;
	my $g = 0;
	my $b = 0;
	my $color = qq|990000|;

	my $opacity;
	if(defined $phy_id){
		if($phy_id eq "1"){
			$r = 204;
			$g = 0;
			$b = 0;
			$color = qq|CC0000|;
		}elsif($phy_id eq "2"){
			$r = 74;
			$g = 74;
			$b = 255;
			$color = qq|4A4AFF|;
#			$opacity = 0.5;
		}
	}

#	return if(!defined $phy_id || $phy_id ne "2");

#warn qq|$version\t$f_id\t$f_pid\t[$phy_id]\n|;

#	use AgSOAP;
#	my $soap = AgSOAP->new;
	my $soap = {};

#	$soap->{AgDataset}->{bp3dObjDir} = "obj_".$version;
	$soap->{Common}->{Version} = $version;
	{
		my $tg_model;
		my $sth = $dbh->prepare(qq|select b.tg_model from tree_group_item as a left join (select tg_id,tg_model from tree_group) as b on a.tg_id=b.tg_id where a.tgi_version=?|);
		$sth->execute($version);
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$tg_model, undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;
		$soap->{Common}->{Model} = $tg_model if(defined $tg_model);
	}
	return undef unless(defined $soap->{Common}->{Model});
#warn __LINE__,":",$soap->{Common}->{Model},"\n";

#	$soap->{AgProp}->{winSizeX} = 640;
#	$soap->{AgProp}->{winSizeY} = 640;
	$soap->{Window}->{ImageWidth} = 640;
	$soap->{Window}->{ImageHeight} = 640;

#	$soap->{AgProp}->{bgR} = 250;
#	$soap->{AgProp}->{bgG} = 250;
#	$soap->{AgProp}->{bgB} = 250;
	$soap->{Window}->{BackgroundColor} = 'FAFAFA';

#	$soap->{AgProp}->{outFileImageFormat} = "png24";

#	$soap->{AgProp}->{treeFileName} = "bp3d.tree";
#	if(defined $type){
#		if($type eq "3"){
#			$soap->{AgProp}->{treeFileName} = "fma_isa_bp3d.tree";
#		}elsif($type eq "4"){
#			$soap->{AgProp}->{treeFileName} = "fma_partof_bp3d.tree";
#		}
#	}
	$soap->{Common}->{TreeName} = "bp3d";
	if(defined $type){
		if($type eq "3"){
			$soap->{Common}->{TreeName} = "isa";
		}elsif($type eq "4"){
			$soap->{Common}->{TreeName} = "partof";
		}
	}

#warn __LINE__,":\$f_pid=[$f_pid]\n" if(defined $f_pid);
#warn __LINE__,":\$f_id=[$f_id]\n" if(defined $f_id);

#	my $org = AgOrgan->new;
	my $org = {};
	unless(defined $f_pid){
#		$org->{id} = $f_id;
#		$org->{r} = $r;
#		$org->{g} = $g;
#		$org->{b} = $b;
#		push @{$soap->{AgOrgan}}, $org;
		$org->{PartID} = $f_id;
		$org->{PartColor} = $color;
		push @{$soap->{Part}}, $org;
	}else{
#		$org->{id} = $f_pid;
#		$org->{opacity} = 0.05;
#		$org->{usedForTotalBBox} = "false";
#		push @{$soap->{AgOrgan}}, $org;
		$org->{PartID} = $f_pid;
		$org->{PartColor} = qq|F0D2A0|;
		$org->{PartOpacity} = 0.05;
		$org->{UseForBoundingBoxFlag} = JSON::XS::false;
		push @{$soap->{Part}}, $org;
=pod
		if(defined $point_parent){
			$org = AgOrgan->new;
			$org->{id} = ref $point_parent eq "ARRAY" ? $point_parent->[0]->{f_id} : ref $point_parent eq "HASH" ? $point_parent->{f_id} : $point_parent;
			push @{$soap->{AgOrgan}}, $org;

			my $sth_bp3d_point = $dbh->prepare(qq|select p_name_e, p_label, p_coord, p_x3d, p_y3d, p_z3d, p_avx3d, p_avy3d, p_avz3d, p_uvx3d, p_uvy3d, p_uvz3d from bp3d_point where f_id=?|);
			$sth_bp3d_point->execute($f_id);
			my $p_name_e;
			my $p_label;
			my $p_coord;
			my $p_x3d;
			my $p_y3d;
			my $p_z3d;
			my $p_avx3d;
			my $p_avy3d;
			my $p_avz3d;
			my $p_uvx3d;
			my $p_uvy3d;
			my $p_uvz3d;
			my $column_number = 0;
			$sth_bp3d_point->bind_col(++$column_number, \$p_name_e, undef);
			$sth_bp3d_point->bind_col(++$column_number, \$p_label, undef);
			$sth_bp3d_point->bind_col(++$column_number, \$p_coord, undef);
			$sth_bp3d_point->bind_col(++$column_number, \$p_x3d, undef);
			$sth_bp3d_point->bind_col(++$column_number, \$p_y3d, undef);
			$sth_bp3d_point->bind_col(++$column_number, \$p_z3d, undef);
			$sth_bp3d_point->bind_col(++$column_number, \$p_avx3d, undef);
			$sth_bp3d_point->bind_col(++$column_number, \$p_avy3d, undef);
			$sth_bp3d_point->bind_col(++$column_number, \$p_avz3d, undef);
			$sth_bp3d_point->bind_col(++$column_number, \$p_uvx3d, undef);
			$sth_bp3d_point->bind_col(++$column_number, \$p_uvy3d, undef);
			$sth_bp3d_point->bind_col(++$column_number, \$p_uvz3d, undef);
			$sth_bp3d_point->fetch;
			$sth_bp3d_point->finish;
			undef $sth_bp3d_point;

			my $po = AgPoint->new();
			$po->{id} = $f_id;
			$po->{name} = $p_name_e;
			$po->{label} = $p_label;
			$po->{worldPosX} = $p_x3d;
			$po->{worldPosY} = $p_y3d;
			$po->{worldPosZ} = $p_z3d;
			$po->{arrVecX} = $p_avx3d;
			$po->{arrVecY} = $p_avy3d;
			$po->{arrVecZ} = $p_avz3d;
			$po->{upVecX} = $p_uvx3d;
			$po->{upVecY} = $p_uvy3d;
			$po->{upVecZ} = $p_uvz3d;
			$po->{coordId} = $p_coord;

			$po->{r} = 74;
			$po->{g} = 74;
			$po->{b} = 255;

			push @{$soap->{AgPoint}}, $po;

		}else{
=cut
#			$org = AgOrgan->new;
#			$org->{id} = $f_id;
#			$org->{r} = $r;
#			$org->{g} = $g;
#			$org->{b} = $b;
#			$org->{opacity} = $opacity if(defined $opacity);
#			push @{$soap->{AgOrgan}}, $org;
			$org = {};
			$org->{PartID} = $f_id;
			$org->{PartColor} = $color;
			$org->{PartOpacity} = $opacity if(defined $opacity);
			push @{$soap->{Part}}, $org;
=pod
		}
=cut
	}

#	warn __LINE__,":",scalar @{$soap->{AgOrgan}},"\n";
#	warn __LINE__,":",scalar @{$soap->{Part}},"\n";

#	my $maxyrange = 0;
	my $maxZoom = 0;
	my $maxcamera = "front";

#	@cameras = ("front", "left", "back", "right");
	my @cameras = ("front", "left");

#	$soap->{AgCamera}->{yRange} = 1800;

#open OUT,">tmp_image/$f_id.txt";

#	foreach my $camera (@cameras) {
#		$soap->{AgCamera}->{cameraMode} = $camera;
#		$soap->sendGetImageWithMarker();
#		if ($soap->{LastResponse} =~ /<ns:yrange>([\d\.]+)<\/ns:yrange>/) {
#			my $yrange = $1;
#			if ($yrange ne "200.0" && $yrange > $maxyrange) {
#				$maxyrange = $yrange;
#				$maxcamera = $camera;
#			}
#		}
#	}

	my $Camera;
	foreach my $camera (@cameras) {
		$soap->{Camera}->{CameraMode} = $camera;
		$soap->{Camera}->{Zoom} = 0;
		my $json = encode_json($soap);
		my $parser = new AG::API::JSONParser($json);
		my $content = $parser->getMethodContent('focus') if(defined $parser);
		unless(defined $content){
			warn __LINE__,":ERROR!![focus]\n";
			&sigexit_common_image();
		}
		my $jsonObj = decode_json($content) if(defined $content);
		if(defined $jsonObj && defined $jsonObj->{Camera} && defined $jsonObj->{Camera}->{Zoom}){
#			warn __LINE__,":\$camera=[$camera]:\$jsonObj->{Camera}->{Zoom}=[$jsonObj->{Camera}->{Zoom}]\n";
			if(!defined $Camera || $jsonObj->{Camera}->{Zoom} < $maxZoom){
				$maxZoom = $jsonObj->{Camera}->{Zoom};
				$maxcamera = $camera;
				$Camera = $jsonObj->{Camera};
			}
		}
	}
#close OUT;

#	warn __LINE__,":\$maxcamera=[$maxcamera]:\$maxyrange=[$maxyrange]\n";
#	warn __LINE__,":\$maxcamera=[$maxcamera]:\$maxZoom=[$maxZoom]\n";

#	$soap->{AgCamera}->{cameraMode} = $maxcamera;
#	$soap->sendGetImageWithMarker();

	$soap->{Camera} = $Camera;
	$soap->{Camera}->{CameraMode} = qq|camera|;
	my $json = encode_json($soap);
	my $parser = new AG::API::JSONParser($json);
	my $content = $parser->getMethodContent('focusClip') if(defined $parser);
	unless(defined $content){
		warn __LINE__,":ERROR!![focusClip]\n";
		&sigexit_common_image();
	}
	my $jsonObj = decode_json($content) if(defined $content);

#	warn __LINE__,":",$soap->{LastRequest}."\n\n\n";
#	warn __LINE__,":",$soap->{LastResponse}."\n\n\n";
#	warn __LINE__,":",$soap->{ImgURL}."\n\n\n";



	my $AgBoundingBox;
	if(defined $jsonObj){
		$AgBoundingBox = {};
		foreach my $key (sort keys(%{$jsonObj->{BoundingBox}})){
			$AgBoundingBox->{lc($key)} = $jsonObj->{BoundingBox}->{$key} if(ref $jsonObj->{BoundingBox}->{$key} == "");
		}
	}
	if(defined $AgBoundingBox &&
		$AgBoundingBox->{xmax} == 0 && $AgBoundingBox->{xmin} == 0 &&
		$AgBoundingBox->{ymax} == 0 && $AgBoundingBox->{ymin} == 0 &&
		$AgBoundingBox->{zmax} == 0 && $AgBoundingBox->{zmin} == 0
	){
		system(qq|touch $gif_file|);
		system(qq|touch $gif_file_S|);
		system(qq|touch $gif_file_L|);
		system(qq|touch $gif_file_SC|);
		system(qq|touch $gif_file_LC|);
	}

	return $AgBoundingBox if(-e $gif_file);
	return $AgBoundingBox if(-e $gif_file && -e $img_dir);
	unless(-e $img_dir){
		return $AgBoundingBox unless(mkdir($img_dir));
		chmod 0777,$img_dir;
	}
=pod
	if($FILE_NUM==4 && !-e $gif_file){
		$soap->{AgCamera}->{cameraMode} = $maxcamera;
		$soap->{AgCamera}->{changeYRange} = -0.5 unless(defined $point_parent);
		$soap->{AgCamera}->{addLongitude} = 0;
		$soap->sendGetAnimationGif();
		my $imgurl = $soap->{ImgURL};
		warn __LINE__,":$f_id:",$imgurl,"\n";
		my $ua = LWP::UserAgent->new;
		my $req = HTTP::Request->new(GET => $imgurl);
		my $res = $ua->request($req);
		my $content = $res->content();
		open(OUT,"> $gif_file");
		binmode(OUT);
		print OUT $content;
		close(OUT);

		open(OUT,"> $gif_file_L");
		binmode(OUT);
		print OUT $content;
		close(OUT);

		$soap->{AgProp}->{winSizeX} = 120;
		$soap->{AgProp}->{winSizeY} = 120;
		$soap->{AgCamera}->{cameraMode} = $maxcamera;
		$soap->{AgCamera}->{changeYRange} = -0.5 unless(defined $point_parent);
		$soap->{AgCamera}->{addLongitude} = 0;
		$soap->sendGetAnimationGif();
		my $imgurl = $soap->{ImgURL};
		warn __LINE__,":$f_id:",$imgurl,"\n";
		my $ua = LWP::UserAgent->new;
		my $req = HTTP::Request->new(GET => $imgurl);
		my $res = $ua->request($req);
		my $content = $res->content();
		open(OUT,"> $gif_file_S");
		binmode(OUT);
		print OUT $content;
		close(OUT);

		$soap->{AgProp}->{winSizeX} = 640;
		$soap->{AgProp}->{winSizeY} = 640;
	}
=cut


	if(scalar @IMG_FILES != $FILE_NUM || !-e $img_dir){
		unlink $gif_file if(-e $gif_file);
		mkdir $img_dir if(!-e $img_dir);
		chmod 0777,$img_dir;
		my $credit;
		for(my $i=0;$i<360;$i+=$addLongitude) {

			my $angle = $i;
			if ($maxcamera eq "left") {
				$angle -= 90;
				$angle += 360 if ($angle < 0);
			}
			my $img_file = "$img_dir/".sprintf("%03d", $angle).".png";
			next if(-e $img_file);

#			$soap->{AgCamera}->{cameraMode} = $maxcamera;
#			$soap->{AgCamera}->{changeYRange} = -0.5 unless(defined $point_parent);
#			$soap->{AgCamera}->{addLongitude} = $i;
#			$soap->sendGetImageWithMarker();


			$parser->{jsonObj}->{Camera}->{AddLongitudeDegree} = $i+0;

#			warn __LINE__,":\$AddLongitudeDegree=[$parser->{jsonObj}->{Camera}->{AddLongitudeDegree}]:\$Zoom=[$parser->{jsonObj}->{Camera}->{Zoom}]\n";

			$parser->{json} = encode_json($parser->{jsonObj});
#			my $json = encode_json($soap);
#			my $parser = new AG::API::JSONParser($json);

			my $content = $parser->getMethodPicture('image') if(defined $parser);


#			my $imgurl = $soap->{ImgURL};
#			my $ua = LWP::UserAgent->new;
#			my $req = HTTP::Request->new(GET => $imgurl);
#			my $res = $ua->request($req);
#			my $content = $res->content();

#			eval{
#				my $image = GD::Image->newFromPngData($content, 1);
#				$content = $image->png;
#				undef $image;
#			};

			#何らかの原因でpngファイルの生成に失敗した場合に備えフォーマットチェック
			my $im;
			if(defined $content){
				$im = Image::Magick->new();
				$im->BlobToImage($content);
				my $magick = $im->Get('magick');
				if($magick ne "PNG"){
					warn __LINE__,qq|:ERROR!![$version\t$f_id\t$f_pid\t[$phy_id]\t[$magick]]\n|;
					warn __LINE__,qq|:ERROR!![|,$parser->getContentStatus(),qq|]\n|;
					warn __LINE__,qq|:ERROR!![|,$parser->getContent(),qq|]\n|;
					&sigexit_common_image();
					return undef;
				}
			}elsif(defined $parser){
				warn __LINE__,qq|:ERROR!![|,$parser->getContentStatus(),qq|]\n|;
				warn __LINE__,qq|:ERROR!![|,$parser->getContent(),qq|]\n|;
				&sigexit_common_image();
			}else{
				warn __LINE__,qq|:ERROR!![Unknown ???]\n|;
				&sigexit_common_image();
			}

			#減色してみる
			$im->Quantize(colors=>256,dither=>'True','dither-method'=>'Floyd-Steinberg') if($image_color_reduction);

			if($angle == 0){

				$im->Write(qq|$image_output_type:$png_file_F_L|);
				chmod 0666,$png_file_F_L;

				&makeCreditImageFile($im,$png_file_F_LC);
				chmod 0666,$png_file_F_LC;

				$im->Resize(geometry=>$geometry_S,blur=>$blur);
				$im->Write(qq|$image_output_type:$png_file_F_S|);
				chmod 0666,$png_file_F_S;

				&makeCreditImageFile($im,$png_file_F_SC,'S');
				chmod 0666,$png_file_F_SC;

			}elsif($angle == 90){

				$im->Write(qq|$image_output_type:$png_file_L_L|);
				chmod 0666,$png_file_L_L;

				&makeCreditImageFile($im,$png_file_L_LC);
				chmod 0666,$png_file_L_LC;

				$im->Resize(geometry=>$geometry_S,blur=>$blur);
				$im->Write(qq|$image_output_type:$png_file_L_S|);
				chmod 0666,$png_file_L_S;

				&makeCreditImageFile($im,$png_file_L_SC,'S');
				chmod 0666,$png_file_L_SC;

			}elsif($angle == 180){

				$im->Write(qq|$image_output_type:$png_file_B_L|);
				chmod 0666,$png_file_B_L;

				&makeCreditImageFile($im,$png_file_B_LC);
				chmod 0666,$png_file_B_LC;

				$im->Resize(geometry=>$geometry_S,blur=>$blur);
				$im->Write(qq|$image_output_type:$png_file_B_S|);
				chmod 0666,$png_file_B_S;

				&makeCreditImageFile($im,$png_file_B_SC,'S');
				chmod 0666,$png_file_B_SC;

			}elsif($angle == 270){

				$im->Write(qq|$image_output_type:$png_file_R_L|);
				chmod 0666,$png_file_R_L;

				&makeCreditImageFile($im,$png_file_R_LC);
				chmod 0666,$png_file_R_LC;

				$im->Resize(geometry=>$geometry_S,blur=>$blur);
				$im->Write(qq|$image_output_type:$png_file_R_S|);
				chmod 0666,$png_file_R_S;

				&makeCreditImageFile($im,$png_file_R_SC,'S');
				chmod 0666,$png_file_R_SC;
			}

			undef $im;

			#必ず正面からの画像が生成される訳ではないので一度ファイルに保存する
			open OUT,"> $img_file";
			binmode(OUT);
#			print OUT $res->content();
			print OUT $content;
			close OUT;
		}
	}

	if($FILE_NUM==72 && !-e $gif_file){
		my $im_gif = Image::Magick->new();
		my $im_gif_S = Image::Magick->new();
		my $im_gif_L = Image::Magick->new();
		my $im_gif_SC = Image::Magick->new();
		my $im_gif_LC = Image::Magick->new();

		opendir(DIR,$img_dir);
		@IMG_FILES = sort grep /\.png$/, readdir(DIR);
		closedir(DIR);

		foreach my $img_file (@IMG_FILES){
			my $im = Image::Magick->new();
			$im->Read(qq|$img_dir/$img_file|);
			$im->Resize(geometry=>$geometry_S,blur=>$blur);
			push(@$im_gif, $im);
			undef $im;

			my $im = Image::Magick->new();
			$im->Read(qq|$img_dir/$img_file|);
			$im->Resize(geometry=>$geometry_S,blur=>$blur);
			push(@$im_gif_S, $im);
			push(@$im_gif_SC, &makeCreditImageMagick($im,'S'));
			undef $im;

			my $im = Image::Magick->new();
			$im->Read(qq|$img_dir/$img_file|);
			push(@$im_gif_L, $im);
			push(@$im_gif_LC, &makeCreditImageMagick($im));
			undef $im;
		}
		$im_gif->Set(dispose=>$dispose, delay=>0, loop=>0);
		$im_gif->Write($temp_file);
		@$im_gif = ();
		undef $im_gif;
		rename $temp_file,$gif_file if(-e $temp_file);
		chmod 0666,$gif_file;

		$im_gif_S->Set(dispose=>$dispose, delay=>0, loop=>0);
		$im_gif_S->Write($temp_file);
		@$im_gif_S = ();
		undef $im_gif_S;
		rename $temp_file,$gif_file_S if(-e $temp_file);
		chmod 0666,$gif_file_S;

		$im_gif_L->Set(dispose=>$dispose, delay=>0, loop=>0);
		$im_gif_L->Write($temp_file);
		@$im_gif_L = ();
		undef $im_gif_L;
		rename $temp_file,$gif_file_L if(-e $temp_file);
		chmod 0666,$gif_file_L;

		$im_gif_SC->Set(dispose=>$dispose, delay=>0, loop=>0);
		$im_gif_SC->Write($temp_file);
		@$im_gif_SC = ();
		undef $im_gif_SC;
		rename $temp_file,$gif_file_SC if(-e $temp_file);
		chmod 0666,$gif_file_SC;

		$im_gif_LC->Set(dispose=>$dispose, delay=>0, loop=>0);
		$im_gif_LC->Write($temp_file);
		@$im_gif_LC = ();
		undef $im_gif_LC;
		rename $temp_file,$gif_file_LC if(-e $temp_file);
		chmod 0666,$gif_file_LC;
	}

	if(-e $img_dir){
		opendir(DIR,$img_dir);
		@IMG_FILES = sort grep /\.png$/, readdir(DIR);
		closedir(DIR);
		if(scalar @IMG_FILES > 0){
			eval{rmtree($img_dir);}; #NFSでマウントしている場合、エラーになる
			eval{
				if(-e $img_dir){
					foreach my $img_file (@IMG_FILES){
						unlink qq|$img_dir/$img_file| if(-e qq|$img_dir/$img_file|);
					}
					rmdir($img_dir);
				}
			};
		}
	}

#exit;
	return $AgBoundingBox;
}

sub makeCreditImage {
	my $im = shift;
	my $size = shift;
	$size = '' unless(defined $size);
	my @blobs = $im->ImageToBlob();
	my $copyImg = GD::Image->newFromPng("img/copyright$size.png", 1);
	my $image = GD::Image->newFromPngData($blobs[0], 1);
	my ($dstW, $dstH) = $image->getBounds();
	my ($srcW, $srcH) = $copyImg->getBounds();
	$image->copy($copyImg, $dstW - $srcW, $dstH - $srcH, 0, 0, $srcW, $srcH);
	return $image;
}

sub makeCreditImageMagick {
	my $im = shift;
	my $size = shift;
	my $image = &makeCreditImage($im,$size);
	my @blob = ($image->png);
	my $new_im = Image::Magick->new();
	$new_im->BlobToImage(@blob);
	return $new_im;
}

sub makeCreditImageFile {
	my $im = shift;
	my $filename = shift;
	my $size = shift;
	my $image = &makeCreditImage($im,$size);
#	open IMGOUT, ">".$filename;
#	binmode(IMGOUT);
#	print IMGOUT $image->png;
#	close IMGOUT;
	my @blob = ($image->png);
	my $im = Image::Magick->new();
	$im->BlobToImage(@blob);
	$im->Quantize(colors=>256,dither=>'True','dither-method'=>'Floyd-Steinberg') if($image_color_reduction);
	$im->Write(qq|$image_output_type:$filename|);
	undef $image;
	undef $im;
}

sub _trim {
	my $str = shift;
	$str =~ s/^\s*//g;
	$str =~ s/\s*$//g;
	return $str;
}

sub cp {
	my @tmpfile;
	return if(open(CPIN,"<$_[0]") == undef);
	if(open(OUT,">$_[1]") == undef){
		close(CPIN);
		return;
	}
	binmode(CPIN);
	binmode(OUT);
	@tmpfile = <CPIN>;
	print OUT @tmpfile;
	close(CPIN);
	close(OUT);
}

sub mv {
	&cp($_[0],$_[1]);
	unlink($_[0]);
}

1;
