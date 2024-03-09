#!/bp3d/local/perl/bin/perl

$| = 1;

#my $target_type = $ARGV[0] if(scalar @ARGV > 0);
#if(!defined $target_type || $target_type !~ /[^0-9$]/){
#	die qq|Format type number is incorrect. [$target_type]!!\n|;
#	exit;
#}

use strict;
use lib 'IM';
#use AgSOAP;
#use LWP::UserAgent;
#use HTTP::Request::Common;
#use Image::Magick;
use JSON::XS;

die "$0 [bp3d_version]\n" if(scalar @ARGV < 1);

require "common.pl";
require "common_db.pl";
require "common_image.pl";
my $dbh = &get_dbh();
my $sth_tree_group_item = $dbh->prepare(qq|select tg_id,tgi_id from tree_group_item where tgi_version=?|);
my $sth_tree_type = $dbh->prepare(qq|select t_type from tree where tg_id=? and tgi_id=? group by t_type order by t_type|);
my $sth_tree_root = $dbh->prepare(qq|select f_id,t_iscircular from tree where tg_id=? and tgi_id=? and t_type=? and f_pid is null and t_delcause is null|);
my $sth_tree_child = $dbh->prepare(qq|select f_id,t_iscircular from tree where tg_id=? and tgi_id=? and t_type=? and f_pid=? and t_delcause is null|);

my $out_dir;

my %USE_ID = ();

my @BP3DVERSION = ();
push(@BP3DVERSION,@ARGV);
foreach my $target_version (@BP3DVERSION){
	if(defined $target_version){
		die qq|Format version number is incorrect. [$target_version]!!\n| if($target_version =~ /[^0-9\.]/);
	}else{
		die qq|Format version number is incorrect. [$target_version]!!\n|;
	}
}
warn "\@BP3DVERSION=",scalar @BP3DVERSION,"\n";
exit if(scalar @BP3DVERSION == 0);

foreach my $target_version (@BP3DVERSION){
	warn qq|version:[$target_version]\n|;

	my %BP3D_STATE_NEW_HASH = ();
	my %BP3D_STATE_UPDATE_HASH = ();
	my $bp3d_table = &getBP3DTablename($target_version);
	my $b_id;
	my $b_state;
	my $sth_state = $dbh->prepare(qq|select b_id,b_state from $bp3d_table where b_state is not null order by b_state,b_id|);
	$sth_state->execute();
	my $column_number = 0;
	$sth_state->bind_col(++$column_number, \$b_id, undef);
	$sth_state->bind_col(++$column_number, \$b_state, undef);
	while($sth_state->fetch){
		next unless(defined $b_state);
		if($b_state eq 'new'){
			$BP3D_STATE_NEW_HASH{$b_id} = $b_state;
		}elsif($b_state eq 'update'){
			$BP3D_STATE_UPDATE_HASH{$b_id} = $b_state;
		}
	}
	$sth_state->finish;
	undef $sth_state;

	my $tg_id;
	my $tgi_id;
	$sth_tree_group_item->execute($target_version);
	my $column_number = 0;
	$sth_tree_group_item->bind_col(++$column_number, \$tg_id, undef);
	$sth_tree_group_item->bind_col(++$column_number, \$tgi_id, undef);
	$sth_tree_group_item->fetch;
	$sth_tree_group_item->finish;
	if(!defined $tg_id || !defined $tgi_id){
		warn qq|Unlnown TG_ID or TGI_ID\n|;
		next;
	}

	my @T_TYPE = ();
	my $t_type;
	$sth_tree_type->execute($tg_id,$tgi_id);
	my $column_number = 0;
	$sth_tree_type->bind_col(++$column_number, \$t_type, undef);
	while($sth_tree_type->fetch){
		next unless(defined $t_type);
		push(@T_TYPE,$t_type);
	}
	$sth_tree_type->finish;
	if(scalar @T_TYPE == 0){
		warn qq|Unlnown T_TYPE\n|;
		next;
	}

	foreach my $target_type (@T_TYPE){
#		next if($target_type ne '3');
#		next if($target_type ne '4');
#		next if($target_type ne '1');

		$out_dir = qq|bp3d_images/$target_version|;
		if(!-e $out_dir){
			mkdir $out_dir;
			chmod 0777,$out_dir;
		}
		$out_dir .= qq|/$target_type|;
		if(!-e $out_dir){
			mkdir $out_dir;
			chmod 0777,$out_dir;
		}

		my $data_file = qq|data/$target_version/|;
		if($target_type eq '1'){
			$data_file .= qq|bp3d.txt|;
		}elsif($target_type eq '3'){
			$data_file .= qq|fma_isa_bp3d.txt|;
		}elsif($target_type eq '4'){
			$data_file .= qq|fma_partof_bp3d.txt|;
		}
warn qq|\$target_type=[$target_type]\n|;
warn qq|\$data_file=[$data_file]\n|;

		unless(-e $data_file){
			warn __LINE__,":No exists[$data_file]!!\n";
			next;
		}

		my %EXISTS_ID = ();
		if(-e $data_file){
			if(open(IN,"< $data_file")){
				while(<IN>){
					next if(/^#/);
					my $f_id = (split(/\t/))[0];
					$EXISTS_ID{$f_id} = "";
warn qq|\$f_id=[$f_id]\n|;
				}
			}
		}
		my $bp3d_total = scalar keys(%EXISTS_ID);
		my $bp3d_count = $bp3d_total;

		my @ROOTS = ();
		my %ROOTS2CI = ();
		my $f_id;
		my $t_iscircular;
		$sth_tree_root->execute($tg_id,$tgi_id,$target_type);
		my $column_number = 0;
		$sth_tree_root->bind_col(++$column_number, \$f_id, undef);
		$sth_tree_root->bind_col(++$column_number, \$t_iscircular, undef);
		while($sth_tree_root->fetch){
			next unless(defined $f_id);
			push(@ROOTS,$f_id);
			$ROOTS2CI{$f_id} = $t_iscircular;
		}
		$sth_tree_root->finish;

warn __LINE__,":\@ROOTS=[",scalar @ROOTS,"]\n";

		if(scalar @ROOTS == 0){
			warn qq|Unlnown ROOTS\n|;
			next;
		}

		my %ROOT2CHILDS = ();
		foreach my $root_id (@ROOTS){
			my $image_path = &getImageBasePath($root_id,$target_version,$target_type);
			my $box_file = qq|$image_path/$root_id.txt|;
			my $none_file = qq|$image_path/$root_id.none|;
			if(exists($EXISTS_ID{$root_id})){
warn __LINE__,qq|:$target_version\t$target_type\t$root_id\t\t$image_path\t\t$bp3d_count/$bp3d_total\n|;
				unless(-e $box_file){
					&make_bbox($image_path,$target_version,$target_type,$root_id);
				}elsif(!-e $none_file){
					&updateBBox($dbh,$root_id,$box_file,$target_version,$target_type);
				}
				$bp3d_count--;
			}elsif(!-e $none_file){
				system("touch $none_file");
				open(OUT,"> $box_file");
				print OUT qq|{"ymax":0,"zmax":0,"ymin":0,"zmin":0,"xmax":0,"xmin":0}|;
				close(OUT);
			}
			next if($ROOTS2CI{$root_id} == 1);

			%USE_ID = ();
			push(@{$ROOT2CHILDS{$root_id}},&getChild($tg_id,$tgi_id,$target_type,$root_id));
			@{$ROOT2CHILDS{$root_id}} = grep(  !$USE_ID{$_}++, @{$ROOT2CHILDS{$root_id}} );
			warn "$root_id=",scalar @{$ROOT2CHILDS{$root_id}},"\n";
			undef %USE_ID;

			my $total = scalar @{$ROOT2CHILDS{$root_id}};
			my $count = $total;
			if(scalar keys(%BP3D_STATE_NEW_HASH) > 0){
				foreach my $f_id (@{$ROOT2CHILDS{$root_id}}){
					next unless(exists($BP3D_STATE_NEW_HASH{$f_id}));
					$image_path = &getImageBasePath($f_id,$target_version,$target_type);
					$box_file = qq|$image_path/$f_id.txt|;
					$none_file = qq|$image_path/$f_id.none|;
					if(exists($EXISTS_ID{$f_id})){
warn __LINE__,qq|:$target_version\t$target_type\t$f_id\t$root_id\t$image_path\t$count/$total\t$bp3d_count/$bp3d_total\tB\tNEW\n|;
						unless(-e $box_file){
							&make_bbox($image_path,$target_version,$target_type,$f_id,$root_id);
						}elsif(!-e $none_file){
							&updateBBox($dbh,$f_id,$box_file,$target_version,$target_type);
						}
						$bp3d_count--;
					}elsif(!-e $none_file){
						system("touch $none_file");
						open(OUT,"> $box_file");
						print OUT qq|{"ymax":0,"zmax":0,"ymin":0,"zmin":0,"xmax":0,"xmin":0}|;
						close(OUT);
					}
					$count--;
				}
			}

			if(scalar keys(%BP3D_STATE_UPDATE_HASH) > 0){
				foreach my $f_id (@{$ROOT2CHILDS{$root_id}}){
					next unless(exists($BP3D_STATE_UPDATE_HASH{$f_id}));
					$image_path = &getImageBasePath($f_id,$target_version,$target_type);
					$box_file = qq|$image_path/$f_id.txt|;
					$none_file = qq|$image_path/$f_id.none|;
					if(exists($EXISTS_ID{$f_id})){
warn __LINE__,qq|:$target_version\t$target_type\t$f_id\t$root_id\t$image_path\t$count/$total\t$bp3d_count/$bp3d_total\tB\tUPDATE\n|;
						unless(-e $box_file){
							&make_bbox($image_path,$target_version,$target_type,$f_id,$root_id);
						}elsif(!-e $none_file){
							&updateBBox($dbh,$f_id,$box_file,$target_version,$target_type);
						}
						$bp3d_count--;
					}elsif(!-e $none_file){
						system("touch $none_file");
						open(OUT,"> $box_file");
						print OUT qq|{"ymax":0,"zmax":0,"ymin":0,"zmin":0,"xmax":0,"xmin":0}|;
						close(OUT);
					}
					$count--;
				}
			}

			foreach my $f_id (@{$ROOT2CHILDS{$root_id}}){
				next if(exists($BP3D_STATE_NEW_HASH{$f_id}));
				next if(exists($BP3D_STATE_UPDATE_HASH{$f_id}));
				$image_path = &getImageBasePath($f_id,$target_version,$target_type);
				$box_file = qq|$image_path/$f_id.txt|;
				$none_file = qq|$image_path/$f_id.none|;
				if(exists($EXISTS_ID{$f_id})){
warn __LINE__,qq|:$target_version\t$target_type\t$f_id\t$root_id\t$image_path\t$count/$total\t$bp3d_count/$bp3d_total\tB\n|;
					unless(-e $box_file){
						&make_bbox($image_path,$target_version,$target_type,$f_id,$root_id);
					}elsif(!-e $none_file){
						&updateBBox($dbh,$f_id,$box_file,$target_version,$target_type);
					}
					$bp3d_count--;
				}elsif(!-e $none_file){
					system("touch $none_file");
					open(OUT,"> $box_file");
					print OUT qq|{"ymax":0,"zmax":0,"ymin":0,"zmin":0,"xmax":0,"xmin":0}|;
					close(OUT);
				}
				$count--;
			}

		}
	}

	next;


	foreach my $target_type (@T_TYPE){
#		next if($target_type ne '4');
#		next if($target_type ne '1');

		$out_dir = qq|bp3d_images/$target_version|;
		if(!-e $out_dir){
			mkdir $out_dir;
			chmod 0777,$out_dir;
		}
		$out_dir .= qq|/$target_type|;
		if(!-e $out_dir){
			mkdir $out_dir;
			chmod 0777,$out_dir;
		}

		my $data_file = qq|data/$target_version/|;
		if($target_type eq '1'){
			$data_file .= qq|bp3d.txt|;
		}elsif($target_type eq '3'){
			$data_file .= qq|fma_isa_bp3d.txt|;
		}elsif($target_type eq '4'){
			$data_file .= qq|fma_partof_bp3d.txt|;
		}

		unless(-e $data_file){
			warn __LINE__,":No exists[$data_file]!!\n";
			next;
		}

		my %EXISTS_ID = ();
		if(-e $data_file){
			if(open(IN,"< $data_file")){
				while(<IN>){
					next if(/^#/);
					my $f_id = (split(/\t/))[0];
					$EXISTS_ID{$f_id} = "";
				}
			}
		}
		my $bp3d_total = scalar keys(%EXISTS_ID);
		my $bp3d_count = $bp3d_total;

		my @ROOTS = ();
		my %ROOTS2CI = ();
		my $f_id;
		my $t_iscircular;
		$sth_tree_root->execute($tg_id,$tgi_id,$target_type);
		my $column_number = 0;
		$sth_tree_root->bind_col(++$column_number, \$f_id, undef);
		$sth_tree_root->bind_col(++$column_number, \$t_iscircular, undef);
		while($sth_tree_root->fetch){
			next unless(defined $f_id);
			push(@ROOTS,$f_id);
			$ROOTS2CI{$f_id} = $t_iscircular;
		}
		$sth_tree_root->finish;
		if(scalar @ROOTS == 0){
			warn qq|Unlnown ROOTS\n|;
			next;
		}

		my %ROOT2CHILDS = ();
		foreach my $root_id (@ROOTS){
			my $image_path;
			if(exists($EXISTS_ID{$root_id})){
				$image_path = &getImageBasePath($root_id,$target_version,$target_type);
warn qq|$target_version\t$target_type\t$root_id\t\t$image_path\t\t$bp3d_count/$bp3d_total\n|;
				&make_image($image_path,$target_version,$target_type,$root_id);
				$bp3d_count--;
			}
			next if($ROOTS2CI{$root_id} == 1);

			%USE_ID = ();
			push(@{$ROOT2CHILDS{$root_id}},&getChild($tg_id,$tgi_id,$target_type,$root_id));
			@{$ROOT2CHILDS{$root_id}} = grep(  !$USE_ID{$_}++, @{$ROOT2CHILDS{$root_id}} );
			warn "$root_id=",scalar @{$ROOT2CHILDS{$root_id}},"\n";
			undef %USE_ID;

			my $total = scalar @{$ROOT2CHILDS{$root_id}};
			my $count = $total;
			if(scalar keys(%BP3D_STATE_NEW_HASH) > 0){
				foreach my $f_id (@{$ROOT2CHILDS{$root_id}}){
					next unless(exists($BP3D_STATE_NEW_HASH{$f_id}));
					if(exists($EXISTS_ID{$f_id})){
						$image_path = &getImageBasePath($f_id,$target_version,$target_type);
warn qq|$target_version\t$target_type\t$f_id\t$root_id\t$image_path\t$count/$total\t$bp3d_count/$bp3d_total\tI\tNEW\n|;
						&make_image($image_path,$target_version,$target_type,$f_id,$root_id);
						$bp3d_count--;
					}
					$count--;
				}
			}

			if(scalar keys(%BP3D_STATE_UPDATE_HASH) > 0){
				foreach my $f_id (@{$ROOT2CHILDS{$root_id}}){
					next unless(exists($BP3D_STATE_UPDATE_HASH{$f_id}));
					if(exists($EXISTS_ID{$f_id})){
						$image_path = &getImageBasePath($f_id,$target_version,$target_type);
warn qq|$target_version\t$target_type\t$f_id\t$root_id\t$image_path\t$count/$total\t$bp3d_count/$bp3d_total\tI\tUPDATE\n|;
						&make_image($image_path,$target_version,$target_type,$f_id,$root_id);
						$bp3d_count--;
					}
					$count--;
				}
			}

			foreach my $f_id (@{$ROOT2CHILDS{$root_id}}){
				next if(exists($BP3D_STATE_NEW_HASH{$f_id}));
				next if(exists($BP3D_STATE_UPDATE_HASH{$f_id}));
				if(exists($EXISTS_ID{$f_id})){
					$image_path = &getImageBasePath($f_id,$target_version,$target_type);
warn qq|$target_version\t$target_type\t$f_id\t$root_id\t$image_path\t$count/$total\t$bp3d_count/$bp3d_total\tI\n|;
					&make_image($image_path,$target_version,$target_type,$f_id,$root_id);
					$bp3d_count--;
				}
				$count--;
			}

		}
	}

}
exit;

sub getImageBasePath {
	my $fmaid = shift;
	my $version = shift;
	my $treetype = shift;

	my $image_path = &getImageBaseDirFromID($fmaid,$version,$treetype);
	unless(-e $image_path){
		mkpath($image_path);
		my @TEMP = split(/\//,$image_path);
		my $temp = "";
		foreach my $d (@TEMP){
			$temp .= "/" if(length($temp)>0);
			$temp .= $d;
			chmod 0777,$temp;
		}
	}
	return $image_path;
}

sub getChild {
	my $tg_id = shift;
	my $tgi_id = shift;
	my $t_type = shift;
	my $f_pid = shift;
	my @F_IDS = ();
	my %ID2CI = ();
	my @RTN = ();
	my $f_id;
	my $t_iscircular;

	if(exists($USE_ID{$f_pid})){
#		warn __LINE__,":$f_pid\n";
		return wantarray ? @RTN : \@RTN;
	}
	$USE_ID{$f_pid} = undef;

	$sth_tree_child->execute($tg_id,$tgi_id,$t_type,$f_pid);
	my $column_number = 0;
	$sth_tree_child->bind_col(++$column_number, \$f_id, undef);
	$sth_tree_child->bind_col(++$column_number, \$t_iscircular, undef);
	while($sth_tree_child->fetch){
		next unless(defined $f_id);
		push(@F_IDS,$f_id);
		$ID2CI{$f_id} = $t_iscircular;
	}
	$sth_tree_child->finish;
	foreach $f_id (@F_IDS){
#		next if($ID2CI{$f_id} == 1);
		push(@RTN,&getChild($tg_id,$tgi_id,$t_type,$f_id));
	}
	push(@F_IDS,@RTN);
	undef @RTN;
	undef %ID2CI;
	return wantarray ? @F_IDS : \@F_IDS;
}

sub updateBBox {
	my $dbh = shift;
	my $f_id = shift;
	my $box_file = shift;
	my $target_version = shift;
	my $target_type = shift;

	my $IN;
	if(open($IN,"< $box_file")){
		flock($IN,1);
		my $box_str = <$IN>;
		close($IN);
warn __LINE__,qq|:[$target_version][$target_type][$f_id][$box_file][$box_str]\n|;
		my $AgBoundingBox;
		eval{$AgBoundingBox = &JSON::XS::decode_json($box_str);};
		if(defined $AgBoundingBox){
			my $bp3d_table = &getBP3DTablename($target_version);
			my $sth_update;
			if($target_type eq "1"){
				$sth_update = $dbh->prepare(qq|update $bp3d_table set b_xmin=?,b_xmax=?,b_ymin=?,b_ymax=?,b_zmin=?,b_zmax=? where b_id=?|);
			}elsif($target_type eq "3"){
				$sth_update = $dbh->prepare(qq|update $bp3d_table set b_xmin_isa=?,b_xmax_isa=?,b_ymin_isa=?,b_ymax_isa=?,b_zmin_isa=?,b_zmax_isa=? where b_id=?|);
			}elsif($target_type eq "4"){
				$sth_update = $dbh->prepare(qq|update $bp3d_table set b_xmin_partof=?,b_xmax_partof=?,b_ymin_partof=?,b_ymax_partof=?,b_zmin_partof=?,b_zmax_partof=? where b_id=?|);
			}
			if(defined $sth_update){
				$sth_update->execute($AgBoundingBox->{xmin},$AgBoundingBox->{xmax},$AgBoundingBox->{ymin},$AgBoundingBox->{ymax},$AgBoundingBox->{zmin},$AgBoundingBox->{zmax},$f_id);
				my $rows = $sth_update->rows();
				$sth_update->finish;
				undef $sth_update;
#warn qq|\$rows=[$rows]\n|;
				if($rows==0){
					my $sth_insert;
					if($target_type eq "1"){
						$sth_insert = $dbh->prepare(qq|insert into $bp3d_table (b_xmin,b_xmax,b_ymin,b_ymax,b_zmin,b_zmax,b_id,b_entry,b_modified,b_e_openid,b_m_openid) values (?,?,?,?,?,?,?,now(),now(),'system','system')|);
					}elsif($target_type eq "3"){
						$sth_insert = $dbh->prepare(qq|insert into $bp3d_table (b_xmin_isa,b_xmax_isa,b_ymin_isa,b_ymax_isa,b_zmin_isa,b_zmax_isa,b_id,b_entry,b_modified,b_e_openid,b_m_openid) values (?,?,?,?,?,?,?,now(),now(),'system','system')|);
					}elsif($target_type eq "4"){
						$sth_insert = $dbh->prepare(qq|insert into $bp3d_table (b_xmin_partof,b_xmax_partof,b_ymin_partof,b_ymax_partof,b_zmin_partof,b_zmax_partof,b_id,b_entry,b_modified,b_e_openid,b_m_openid) values (?,?,?,?,?,?,?,now(),now(),'system','system')|);
					}
					if(defined $sth_insert){
						$sth_insert->execute($AgBoundingBox->{xmin},$AgBoundingBox->{xmax},$AgBoundingBox->{ymin},$AgBoundingBox->{ymax},$AgBoundingBox->{zmin},$AgBoundingBox->{zmax},$f_id);
						my $rows = $sth_insert->rows();
						$sth_insert->finish;
						undef $sth_insert;
#warn qq|\$rows=[$rows]\n|;
					}
				}
			}
		}
	}

}
