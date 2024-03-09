#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use Image::Info qw(image_info dim);
use Image::Magick;
use DBI;
use DBD::Pg;
use JSON::XS;
use File::Basename;

use File::Spec::Functions qw(catdir catfile);
use Cwd;
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'API'),&Cwd::abs_path(&catdir($FindBin::Bin,'..','lib')),&Cwd::abs_path(&catdir($FindBin::Bin,'..','..','ag-common','lib'));
use cgi_lib::common;
use AG::login;

require "common.pl";
require "common_db.pl";

my $dbh = &get_dbh();

#no JSON::XS;
#use JSON;

my %FORM = ();
&decodeForm(\%FORM);
delete $FORM{_formdata} if(exists($FORM{_formdata}));

my %COOKIE = ();
&getCookie(\%COOKIE);

$FORM{lng} = $COOKIE{"ag_annotation.locale"} if(!exists($FORM{lng}) && exists($COOKIE{"ag_annotation.locale"})); #とりあえず
$FORM{lng} = "en" if(!exists($FORM{lng}));
#$FORM{position} = "front" if(!exists($FORM{position}));

#DEBUG 常に削除
#delete $FORM{parent} if(exists($FORM{parent}));
my $parentURL = $FORM{parent} if(exists($FORM{parent}));
my $lsdb_OpenID;
my $lsdb_Auth;
my $lsdb_Config;
my $lsdb_Identity;
if(defined $parentURL){
	($lsdb_OpenID,$lsdb_Auth,$lsdb_Config) = &openidAuth($parentURL);
}elsif(exists($COOKIE{openid_url}) && exists($COOKIE{openid_session})){
	($lsdb_OpenID,$lsdb_Auth,$lsdb_Config,$lsdb_Identity) = &AG::login::openidAuthSession($COOKIE{openid_url},$COOKIE{openid_session});
}
$lsdb_Auth = int($lsdb_Auth) if(defined $lsdb_Auth);


my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = fileparse($0,@extlist);
#open(LOG,"> logs/$COOKIE{'ag_annotation.session'}.$cgi_name.txt");
#print LOG "\n[$logtime]:$0\n";
#foreach my $key (sort keys(%FORM)){
#	print LOG "\$FORM{$key}=[",$FORM{$key},"]\n";
#}
#foreach my $key (sort keys(%COOKIE)){
#	print LOG "COOKIE{$key}=[",$COOKIE{$key},"]\n";
#}
#foreach my $key (sort keys(%ENV)){
#	print LOG "ENV{$key}=[",$ENV{$key},"]\n";
#}
#delete $FORM{_formdata} if(exists($FORM{_formdata}));

my $sql_fma = qq|select |;
$sql_fma .= qq| f.f_name_j|;
$sql_fma .= qq|,f.f_name_e|;
$sql_fma .= qq|,f.f_name_k|;
$sql_fma .= qq|,f.f_name_l|;
$sql_fma .= qq|,f.f_syn_j|;
$sql_fma .= qq|,f.f_syn_e|;
$sql_fma .= qq|,f.f_detail_j|;
$sql_fma .= qq|,f.f_detail_e|;
$sql_fma .= qq|,f.f_organsys_j|;
$sql_fma .= qq|,f.f_organsys_e|;
$sql_fma .= qq|,f.f_phase|;
$sql_fma .= qq|,f.f_zmin|;
$sql_fma .= qq|,f.f_zmax|;
$sql_fma .= qq|,f.f_volume|;
$sql_fma .= qq|,f.f_delcause|;
$sql_fma .= qq|,EXTRACT(EPOCH FROM f.f_entry)|;
$sql_fma .= qq|,EXTRACT(EPOCH FROM f.f_modified)|;
$sql_fma .= qq|,f.e_openid|;
$sql_fma .= qq|,f.m_openid|;
$sql_fma .= qq|,f.f_taid|;
$sql_fma .= qq|,p.phy_name|;
$sql_fma .= qq|,f.phy_id|;
$sql_fma .= qq| from fma as f|;
$sql_fma .= qq| left join (select phy_id,phy_name from fma_physical) as p on p.phy_id = f.phy_id|;
$sql_fma .= qq| where  f.f_id=?|;
#my $sth_fma = $dbh->prepare($sql_fma);
my $sth_fma;

sub getFMA {
	my $f_id = shift;
	my $f_id2 = $f_id;
#	$f_id2 =~ s/\D+$//g;

	my($f_name_j,$f_name_e,$f_name_k,$f_name_l,$f_syn_j,$f_syn_e,$f_detail_j,$f_detail_e,$f_organsys_j,$f_organsys_e,$f_phase,$f_zmin,$f_zmax,$f_volume,$f_delcause,$f_entry,$f_modified,$e_openid,$m_openid,$f_taid,$phy_name,$phy_id);

	$sth_fma->execute($f_id2);
	my $column_number = 0;
	$sth_fma->bind_col(++$column_number, \$f_name_j, undef);
	$sth_fma->bind_col(++$column_number, \$f_name_e, undef);
	$sth_fma->bind_col(++$column_number, \$f_name_k, undef);
	$sth_fma->bind_col(++$column_number, \$f_name_l, undef);
	$sth_fma->bind_col(++$column_number, \$f_syn_j, undef);
	$sth_fma->bind_col(++$column_number, \$f_syn_e, undef);
	$sth_fma->bind_col(++$column_number, \$f_detail_j, undef);
	$sth_fma->bind_col(++$column_number, \$f_detail_e, undef);
	$sth_fma->bind_col(++$column_number, \$f_organsys_j, undef);
	$sth_fma->bind_col(++$column_number, \$f_organsys_e, undef);
	$sth_fma->bind_col(++$column_number, \$f_phase, undef);
	$sth_fma->bind_col(++$column_number, \$f_zmin, undef);
	$sth_fma->bind_col(++$column_number, \$f_zmax, undef);
	$sth_fma->bind_col(++$column_number, \$f_volume, undef);
	$sth_fma->bind_col(++$column_number, \$f_delcause, undef);
	$sth_fma->bind_col(++$column_number, \$f_entry, undef);
	$sth_fma->bind_col(++$column_number, \$f_modified, undef);
	$sth_fma->bind_col(++$column_number, \$e_openid, undef);
	$sth_fma->bind_col(++$column_number, \$m_openid, undef);
	$sth_fma->bind_col(++$column_number, \$f_taid, undef);
	$sth_fma->bind_col(++$column_number, \$phy_name, undef);
	$sth_fma->bind_col(++$column_number, \$phy_id, undef);
	$sth_fma->fetch;
	$sth_fma->finish;

	my $name;
	my $organsys;
	if(!exists($FORM{lng}) || $FORM{lng} eq "ja"){
		$name = (defined $f_name_j ? $f_name_j : $f_name_e);
		$organsys = (defined $f_organsys_j ? $f_organsys_j : $f_organsys_e);
	}else{
		$name = $f_name_e;
		$organsys = $f_organsys_e;
	}

	my $rtn = {
		f_id       => $f_id,
		name       => $name,
		name_j     => $f_name_j,
		name_e     => $f_name_e,
		name_k     => $f_name_k,
		name_l     => $f_name_l,
		syn_j      => $f_syn_j,
		syn_e      => $f_syn_e,
		detail_j   => $f_detail_j,
		detail_e   => $f_detail_e,
		organsys_j => $f_organsys_j,
		organsys_e => $f_organsys_e,
		organsys   => $organsys,
		phase      => $f_phase,
		zmin       => $f_zmin,
		zmax       => $f_zmax,
		volume     => $f_volume,
		taid       => $f_taid,
		physical   => $phy_name,
		phy_id     => $phy_id,
		lastmod    => $f_modified
	};

	$rtn->{color} = "";
	$rtn->{value} = "";
	$rtn->{zoom} = "false";
	$rtn->{exclude} = "false";
	$rtn->{opacity} = "1.0";
	$rtn->{representation} = "surface";

	return $rtn;
}

my $dir;
if(!exists($FORM{type}) || $FORM{type} eq "sample"){
	$dir = "samples";

	opendir(DIR,$dir);
	my @FILES = sort grep { -f "$dir/$_" } readdir(DIR);
	close(DIR);
	my %FILES_HASH = ();
	foreach (@FILES){
		my $f = $_;
		$f =~ s/\..+$//g;
#		print LOG __LINE__,":\$f=[$f]\n";
		$FILES_HASH{$f} = "";
	}

	my $sth = $dbh->prepare(qq|select sp_id,sp_info,sp_image from sample|);
	$sth->execute();
	my $sp_id;
	my $sp_info;
	my $sp_image;
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$sp_id, undef);
	$sth->bind_col(++$column_number, \$sp_info, undef);
	$sth->bind_col(++$column_number, \$sp_image, { pg_type => DBD::Pg::PG_BYTEA });
	while($sth->fetch){
		my $file_path = qq|$dir/$sp_id|;
		my $file_txt = qq|$file_path.txt|;
		if(defined $sp_info && (!-e $file_txt || -z $file_txt)){
#			print LOG __LINE__,":\$file_txt=[$file_txt]\n";
			open(OUT,"> $file_txt");
			print OUT $sp_info;
			close(OUT);
		}
		if(defined $sp_image){
			my $image_info = image_info(\$sp_image);
			if(defined $image_info){
#				print LOG __LINE__,":\$image_info->{file_ext}=[$image_info->{file_ext}]\n";
				my $file_img = qq|$file_path.$image_info->{file_ext}|;
				if(!-e $file_img || -z $file_img){
#					print LOG __LINE__,":\$file_img=[$file_img]\n";
					open(OUT,"> $file_img");
					binmode(OUT);
					print OUT $sp_image;
					close(OUT);
				}
			}
		}
#		print LOG __LINE__,":\$sp_id=[$sp_id]\n";
		delete $FILES_HASH{$sp_id} if(exists($FILES_HASH{$sp_id}));
	}
	$sth->finish;
	undef $sth;

	foreach my $fh (keys(%FILES_HASH)){
		foreach my $f (@FILES){
			next unless($f =~ /^$fh\..+/);
			unlink qq|$dir/$f|;
#			print LOG __LINE__,":$dir/$f\n";
		}
	}
}elsif($FORM{type} eq "user" && defined $lsdb_OpenID){
	use Digest::MD5 qw(md5 md5_hex md5_base64);
	$dir = "users/".md5_hex($lsdb_OpenID."bits.cc");
	unless(-e $dir){
		mkdir $dir;
		chmod 0777,$dir;
	}

	opendir(DIR,$dir);
	my @FILES = sort grep { -f "$dir/$_" } readdir(DIR);
	close(DIR);
	my %FILES_HASH = ();
	foreach (@FILES){
		my $f = $_;
		$f =~ s/\..+$//g;
		$FILES_HASH{$f} = "";
	}

	my $sth = $dbh->prepare(qq|select sv_id,sv_info,sv_image from save where sv_openid=?|);
	$sth->execute($lsdb_OpenID);
	my $sv_id;
	my $sv_info;
	my $sv_image;
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$sv_id, undef);
	$sth->bind_col(++$column_number, \$sv_info, undef);
	$sth->bind_col(++$column_number, \$sv_image, { pg_type => DBD::Pg::PG_BYTEA });
	while($sth->fetch){
		my $file_path = qq|$dir/$sv_id|;
		my $file_txt = qq|$file_path.txt|;
		if(defined $sv_info && (!-e $file_txt || -z $file_txt)){
			next if(-e $file_txt && -s $file_txt);
			open(OUT,"> $file_txt");
			print OUT $sv_info;
			close(OUT);
		}
		if(defined $sv_image){
			my $image_info = image_info(\$sv_image);
			if(defined $image_info){
				my $file_img = qq|$file_path.$image_info->{file_ext}|;
				if(!-e $file_img || -z $file_img){
					open(OUT,"> $file_img");
					binmode(OUT);
					print OUT $sv_image;
					close(OUT);
				}
			}
		}
		delete $FILES_HASH{$sv_id} if(exists($FILES_HASH{$sv_id}));
	}
	$sth->finish;
	undef $sth;

	foreach my $fh (keys(%FILES_HASH)){
		foreach my $f (@FILES){
			next unless($f =~ /^$fh\..+/);
			unlink qq|$dir/$f|;
		}
	}
}

opendir(DIR, $dir) || die "can't opendir $dir: $!";
my @FILES = sort grep { -f "$dir/$_" && $_ =~ /\.txt$/ } readdir(DIR);
closedir DIR;

my $SAMPLES = {
	"images" => []
};

my %VERSION2LABEL = ();
{
	my $sql;
	$sql = qq|select a.tg_id,tgi_version|;
	if($FORM{lng} eq "ja"){
		$sql .= qq|,COALESCE(tgi_name_j,tgi_name_e)|;
	}else{
		$sql .= qq|,tgi_name_e|;
	}
	$sql .= qq|,b.tg_model|;
	$sql .= qq| from tree_group_item as a|;
	$sql .= qq| left join (select tg_id,tg_model from tree_group) as b on a.tg_id=b.tg_id|;

	my $tg_id;
	my $tgi_version;
	my $tgi_name;
	my $tg_model;
	my $sth_tree_group_item = $dbh->prepare($sql);
	$sth_tree_group_item->execute();
	my $column_number = 0;
	$sth_tree_group_item->bind_col(++$column_number, \$tg_id, undef);
	$sth_tree_group_item->bind_col(++$column_number, \$tgi_version, undef);
	$sth_tree_group_item->bind_col(++$column_number, \$tgi_name, undef);
	$sth_tree_group_item->bind_col(++$column_number, \$tg_model, undef);
	while($sth_tree_group_item->fetch){
		next unless(defined $tg_id && defined $tgi_version && defined $tgi_name && defined $tg_model);
		$VERSION2LABEL{$tgi_version} = {
			tg_id    => $tg_id,
			tg_model => $tg_model,
			tgi_name => $tgi_name
		};
	}
	$sth_tree_group_item->finish;
	undef $sth_tree_group_item;
}

foreach my $file (@FILES){
	my $id = $file;
	$id =~ s/\.txt$//g;
	my $path = qq|$dir/$file|;
	next if(!-e $path);
	my %HASH = ();
	open(IN,"< $path");
	while(<IN>){
		my($key,@VALS) = split(/\t/);
		$HASH{$key} = join("\t",@VALS);
	}
	close(IN);
	next unless(exists($HASH{param}));
#	my $param = from_json($HASH{param});
	utf8::decode($HASH{title});
#print LOG __LINE__,":[",$HASH{param},"]\n";
	my $param = decode_json($HASH{param});
	my $IMAGE = {
		id   => qq|AGSMP$id|,
		name => $HASH{title},
		src  => qq|$dir/$HASH{thumb}|,
		partslist => []
	};
	if(exists($param->{partslist})){
		foreach my $parts (@{$param->{partslist}}){
			next unless(exists($parts->{f_id}));

			$parts->{version} = $VERSION2LABEL{$parts->{version}}->{tgi_name} if(exists($parts->{version}) && exists($VERSION2LABEL{$parts->{version}}));

			push(@{$IMAGE->{partslist}},$parts);
			next;

			my $rtn = &getFMA($parts->{f_id});
			$rtn->{zoom} = $parts->{zoom};
			$rtn->{exclude} = $parts->{exclude};
			if(exists($HASH{qualified})){
				$rtn->{color} = $parts->{color};
				$rtn->{value} = $parts->{value};
				$rtn->{opacity} = $parts->{opacity};
				$rtn->{representation} = $parts->{representation};
			}
			push(@{$IMAGE->{partslist}},$rtn);
		}
	}
	if(exists($HASH{environment}) && exists($param->{baseparam})){
		$IMAGE->{baseparam} = $param->{baseparam};
		$IMAGE->{cameraprm} = $param->{cameraprm} if(exists($param->{cameraprm}));
		if(exists($param->{environment})){
			if(exists($param->{environment}->{bp3dversion}) && exists($VERSION2LABEL{$param->{environment}->{bp3dversion}}) && (!exists($param->{environment}->{tg_id}) || !exists($param->{environment}->{model}))){
				$param->{environment}->{tg_id} = $VERSION2LABEL{$param->{environment}->{bp3dversion}}->{tg_id};
				$param->{environment}->{model} = $VERSION2LABEL{$param->{environment}->{bp3dversion}}->{tg_model};
				$param->{environment}->{bp3dversion} = $VERSION2LABEL{$param->{environment}->{bp3dversion}}->{tgi_name};
			}
			$IMAGE->{environment} = $param->{environment};
		}
	}
	if(exists($HASH{description}) && exists($param->{anatomoprm})){
		if(exists($param->{anatomoprm}->{bv}) && exists($VERSION2LABEL{$param->{anatomoprm}->{bv}}) && !exists($param->{anatomoprm}->{model})){
			$param->{anatomoprm}->{model} = $VERSION2LABEL{$param->{anatomoprm}->{bv}}->{tg_model};
			$param->{anatomoprm}->{bv} = $VERSION2LABEL{$param->{anatomoprm}->{bv}}->{tgi_name};
#print LOG __LINE__,":",$param->{anatomoprm}->{model},"\n";
		}
		$IMAGE->{anatomoprm} = $param->{anatomoprm};
	}
	push(@{$SAMPLES->{images}},$IMAGE);
}

#my $json = to_json($SAMPLES);
my $json = encode_json($SAMPLES);
$json =~ s/"(true|false)"/$1/mg;

print qq|Content-type: text/html; charset=UTF-8\n\n|;

print $json;
#print LOG __LINE__,":",$json,"\n";

#close(LOG);
exit;
