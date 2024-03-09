#!/bp3d/local/perl/bin/perl

use lib '/bp3d/ag1/htdocs','/bp3d/ag1/htdocs/IM';

$| = 1;

#my $target_type = $ARGV[0] if(scalar @ARGV > 0);
#if(!defined $target_type || $target_type !~ /[^0-9$]/){
#	die qq|Format type number is incorrect. [$target_type]!!\n|;
#	exit;
#}

use strict;
#use AgSOAP;
#use LWP::UserAgent;
#use HTTP::Request::Common;
#use Image::Magick;
#use JSON;

die "$0 [bp3d_version]\n" if(scalar @ARGV < 1);

require "common.pl";
require "common_db.pl";
require "common_shorturl.pl";

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


	my $tg_id;
	my $tgi_id;
	$sth_tree_group_item->execute($target_version);
	my $column_number = 0;
	$sth_tree_group_item->bind_col(++$column_number, \$tg_id, undef);
	$sth_tree_group_item->bind_col(++$column_number, \$tgi_id, undef);
	$sth_tree_group_item->fetch;
	$sth_tree_group_item->finish;
	if(!defined $tg_id || !defined $tgi_id){
		warn qq|Unknown TG_ID or TGI_ID\n|;
		next;
	}

	my @T_TYPE = (1);

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
			warn qq|Unknown ROOTS\n|;
			next;
		}

		my $BASE_URL = qq|http://lifesciencedb.jp/bp3d|;

		my %ROOT2CHILDS = ();
		foreach my $root_id (@ROOTS){
			my $form = {
				lng    => 'ja',
				tg_id    => $tg_id,
				tgi_id   => $tgi_id,
				position => 'front',
				version  => $target_version,
				t_type   => $target_type,
				tg_model => 'bp3d'
			};
			my $type_name = qq|conventional|;
			my $fma = &getFMA($dbh,$form,$root_id);
			unless(defined $fma){
				exit;
			}
			my $icon_url = &get_iconURL($root_id,$type_name,$form,$BASE_URL);
			my $oop001 = qq|1.0|;
			my $ocl001 = qq|CC0000|;
			my $ag_param = qq|&oid001=$root_id&ocl001=$ocl001&osz001=Z&oop001=$oop001&orp001=S&odcp001=0|;
			my $ag_url = &get_agURL($ag_param,$BASE_URL);
			&printFMA($fma,$icon_url,$ag_url);

			next if($ROOTS2CI{$root_id} == 1);

			$oop001 = qq|0.05|;
			$ocl001 = qq|f0d2a0|;

			%USE_ID = ();
			push(@{$ROOT2CHILDS{$root_id}},&getChild($tg_id,$tgi_id,$target_type,$root_id));
			@{$ROOT2CHILDS{$root_id}} = grep(  !$USE_ID{$_}++, @{$ROOT2CHILDS{$root_id}} );
			warn "$root_id=",scalar @{$ROOT2CHILDS{$root_id}},"\n";
			undef %USE_ID;

			my $total = scalar @{$ROOT2CHILDS{$root_id}};
			my $count = $total;


			foreach my $f_id (@{$ROOT2CHILDS{$root_id}}){

				my $fma = &getFMA($dbh,$form,$f_id);
				unless(defined $fma){
					exit;
				}
				my $icon_url = &get_iconURL($f_id,$type_name,$form,$BASE_URL);
				my $ag_param = qq|&oid001=$root_id&ocl001=$ocl001&osz001=Z&oop001=$oop001&orp001=S&odcp001=0|;
				$ag_param .= qq|&oid002=$f_id&ocl002=CC0000&osz002=Z&oop002=1.0&orp002=S&odcp002=0|;
				my $ag_url = &get_agURL($ag_param,$BASE_URL);
				&printFMA($fma,$icon_url,$ag_url);
				$count--;
			}

		}
	}
}
exit;

sub get_iconURL {
	my $f_id = shift;
	my $type_name = shift;
	my $form = shift;
	my $BASE_URL = shift;
	my $iconURL = qq|icon.cgi?i=| . &url_encode($f_id) . qq|&p=$form->{position}&v=|.&url_encode($form->{version_name}?$form->{version_name}:$form->{version}).qq|&t=$type_name&c=0&m=|.&url_encode(exists($form->{tg_model})?$form->{tg_model}:$form->{tg_id}).qq|&s=L|;
	return (defined $BASE_URL ? qq|$BASE_URL/| : "") . $iconURL;
}

sub get_ag_param {
	return qq|av=09051901&iw=640&ih=640&bcl=FFFFFF&bga=0&cf=0&hf=1&model=bp3d&bv=3.0&tn=conventional&dt=20111202192808&cx=-0.622&cy=-984.5667&cz=828.6308&tx=-0.622&ty=-96.5107&tz=828.6308&ux=0&uy=0&uz=1&zm=0&cm=N&dpl=0&dpod=1&dpol=0&crd=bp3d|;
}

sub get_agURL {
	my $ag_param = shift;
	my $BASE_URL = shift;
	$ag_param = &get_ag_param() . $ag_param;
	my $ag_url = qq|$BASE_URL/?tp_ap=| . &url_encode($ag_param);
	my $json = &convert_url($ag_url);
	my $data = decode_json($json);
	return $data->{data}->{url};
}

sub printFMA {
	my $fma = shift;
	my $icon_url = shift;
	my $ag_url = shift;

	print (defined $fma->{name_j} ? Encode::encode_utf8($fma->{name_j}) : "");
	print qq|\t|;
	print qq|$icon_url|;
	print qq|\t|;
	print qq|$ag_url|;
	print qq|\t|;
	print qq|$fma->{name_e}|;
	print qq|\t|;
	print qq|$fma->{name_l}|;
	print qq|\t|;
	print (defined $fma->{name_j} ? Encode::encode_utf8($fma->{name_j}) : "");
	print qq|\n|;
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
