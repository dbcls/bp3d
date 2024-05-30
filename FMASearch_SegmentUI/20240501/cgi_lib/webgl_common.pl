use strict;
#use warnings;
use feature ':5.10';
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI::Cookie;
use JSON::XS;
use File::Basename;
use File::Path;
use File::Spec::Functions qw(abs2rel rel2abs catdir catfile splitdir);
use Clone;
use Cwd;
use Data::Dumper;

use FindBin;
my $htdocs_path;
BEGIN{
#	$htdocs_path = qq|/opt/services/ag/ag1/htdocs_130903|;
#	$htdocs_path = qq|/opt/services/ag/ag-test/htdocs_131011|;
	$htdocs_path = qq|/opt/services/ag/ag-test/htdocs| unless(defined $htdocs_path && -e $htdocs_path);
}
use lib $htdocs_path,&catdir($htdocs_path,'API'),&catdir($htdocs_path,'..','lib'),&catdir($htdocs_path,'..','..','ag-common','lib');

#DEBUG
$ENV{'AG_DB_NAME'} = 'ag_public_130930' unless(exists $ENV{'AG_DB_NAME'} && defined $ENV{'AG_DB_NAME'});
$ENV{'AG_DB_HOST'} = '127.0.0.1'        unless(exists $ENV{'AG_DB_HOST'} && defined $ENV{'AG_DB_HOST'});
$ENV{'AG_DB_PORT'} = '38300'            unless(exists $ENV{'AG_DB_PORT'} && defined $ENV{'AG_DB_PORT'});

require "common.pl";
require "common_db.pl";
use cgi_lib::common;

sub getLogDir {
	my ($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst) = localtime();
	$year+=1900;
	$mon+=1;
	my $s_year =  sprintf(qq|%04d|,$year);
	my $s_month = sprintf(qq|%02d|,$mon);
	my $s_mday =  sprintf(qq|%02d|,$mday);
	my $log_dir = &catdir($FindBin::Bin,'logs',$s_year,$s_month,$s_mday);
	&File::Path::make_path($log_dir) unless(-e $log_dir);
	return $log_dir;
}

sub getLogFile {
	my $cookie = shift;
	$cookie = {} unless(defined $cookie);
	my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0, qr/\..*$/);

	my $log_dir = &getLogDir();
	my $file_name = exists $cookie->{'ag_annotation.session'} ? qq|$cookie->{'ag_annotation.session'}.$cgi_name.txt| : qq|$cgi_name.txt|;
	my $file = &catfile($log_dir,$file_name);
	return wantarray ? ($file,$cgi_name,$cgi_dir,$cgi_ext) : $file;
}

sub makeImagePath {
	my $img_path = shift;
	my $img_name = shift;
	if($img_name =~ /^([A-Z]+)/){
		$img_path = &catdir($img_path,$1);
		if($img_name =~ /^[A-Z]+([0-9]+)/){
			my $s = sprintf("%04d",$1);
			for(my $i=0;$i<4;$i+=2){
				my $t = substr($s,$i,2);
				last if(length($t)<2);
				$img_path = &catdir($img_path,$t);
			}
		}
	}else{
		my $s = $img_name;
		for(my $i=0;$i<4;$i+=2){
			my $t = substr($s,$i,2);
			last if(length($t)<2);
			$img_path = &catdir($img_path,$t);
		}
	}
	return $img_path;
}
sub getObjImagePrefix {
	my $obj_name = shift;
	my $mr_version = shift;

	my @DIR = ($FindBin::Bin);
	push(@DIR,$ENV{'AG_DB_HOST'}) if(exists $ENV{'AG_DB_HOST'} && defined $ENV{'AG_DB_HOST'} && length $ENV{'AG_DB_HOST'});
	push(@DIR,$ENV{'AG_DB_PORT'}) if(exists $ENV{'AG_DB_PORT'} && defined $ENV{'AG_DB_PORT'} && length $ENV{'AG_DB_PORT'});
	push(@DIR,'art_images');
	my $prefix = &catdir(@DIR);
	$prefix = &catdir($prefix,$mr_version) if(defined $mr_version);
	my $img_path = &makeImagePath($prefix,$obj_name);
	my $img_prefix = &catdir($img_path,$obj_name);
	return wantarray ? ($img_prefix,$img_path) : $img_prefix;
}

sub getRepImagePrefix {
	my $mr_version = shift;
	my $bul_id = shift;
	my $cdi_name = shift;

	my @DIR = ($FindBin::Bin);
	push(@DIR,$ENV{'AG_DB_HOST'}) if(exists $ENV{'AG_DB_HOST'} && defined $ENV{'AG_DB_HOST'} && length $ENV{'AG_DB_HOST'});
	push(@DIR,$ENV{'AG_DB_PORT'}) if(exists $ENV{'AG_DB_PORT'} && defined $ENV{'AG_DB_PORT'} && length $ENV{'AG_DB_PORT'});
	push(@DIR,'bp3d_images');
	push(@DIR,$mr_version) if(defined $mr_version && length $mr_version);
	my $prefix = &catdir(@DIR);
#	return $prefix unless(defined $bul_id && defined $cdi_name);
	return $prefix unless(defined $cdi_name);
	my $img_path;
	if(defined $bul_id){
		$img_path = &makeImagePath(&catdir($prefix,$bul_id),$cdi_name);
	}else{
		$img_path = &makeImagePath($prefix,$cdi_name);
	}
	my $img_prefix = &catdir($img_path,$cdi_name);
	return wantarray ? ($img_prefix,$img_path) : $img_prefix;
}

sub getCmImagePrefix {
	my $mr_version = shift;
	my $bul_id = shift;
	my $cdi_name = shift;

	my @DIR = ($FindBin::Bin);
	push(@DIR,$ENV{'AG_DB_HOST'}) if(exists $ENV{'AG_DB_HOST'} && defined $ENV{'AG_DB_HOST'} && length $ENV{'AG_DB_HOST'});
	push(@DIR,$ENV{'AG_DB_PORT'}) if(exists $ENV{'AG_DB_PORT'} && defined $ENV{'AG_DB_PORT'} && length $ENV{'AG_DB_PORT'});
	push(@DIR,'cm_images');
	push(@DIR,$mr_version) if(defined $mr_version && length $mr_version);
	my $prefix = &catdir(@DIR);

#	return $prefix unless(defined $bul_id && defined $cdi_name);
	return $prefix unless(defined $cdi_name);
	my $img_path;
	if(defined $bul_id){
		$img_path = &makeImagePath(&catdir($prefix,$bul_id),$cdi_name);
	}else{
		$img_path = &makeImagePath($prefix,$cdi_name);
	}
	my $img_prefix = &catdir($img_path,$cdi_name);
	return wantarray ? ($img_prefix,$img_path) : $img_prefix;
}

sub getImageFileList {
	my $img_prefix = shift;

	my @SIZES = ([640,640],[120,120],[40,40],[16,16]);
	my @DIR = qw|front left back right|;

	my $sizeL = shift @SIZES;
	my $sizeM = shift @SIZES;
	my $sizeS = shift @SIZES;
	my $sizeXS = shift @SIZES;

	my $sizeStrL = join("x",@$sizeL);
	my $sizeStrM = join("x",@$sizeM);
	my $sizeStrS = join("x",@$sizeS);
	my $sizeStrXS = join("x",@$sizeXS);

	my $gif_prefix_fmt = qq|%s_%s|;
	my $gif_fmt = qq|$gif_prefix_fmt.gif|;

	my $png_prefix_fmt = qq|%s_%s_%s|;
	my $png_fmt = qq|$png_prefix_fmt.png|;

	my $imgsL;
	my $imgsM;
	my $imgsS;
	my $imgsXS;

	push(@$imgsL,sprintf($gif_fmt,$img_prefix,$sizeStrL));
	foreach my $dir (@DIR){
		push(@$imgsL,sprintf($png_fmt,$img_prefix,$dir,$sizeStrL));
	}

	push(@$imgsM,sprintf($gif_fmt,$img_prefix,$sizeStrM));
	foreach my $dir (@DIR){
		push(@$imgsM,sprintf($png_fmt,$img_prefix,$dir,$sizeStrM));
	}

	push(@$imgsS,sprintf($gif_fmt,$img_prefix,$sizeStrS));
	foreach my $dir (@DIR){
		push(@$imgsS,sprintf($png_fmt,$img_prefix,$dir,$sizeStrS));
	}

	push(@$imgsXS,sprintf($gif_fmt,$img_prefix,$sizeStrXS));
	foreach my $dir (@DIR){
		push(@$imgsXS,sprintf($png_fmt,$img_prefix,$dir,$sizeStrXS));
	}

	my $RTN;
	if(wantarray){
		push(@$RTN,@$imgsL);
		push(@$RTN,@$imgsM);
		push(@$RTN,@$imgsS);
		push(@$RTN,@$imgsXS);
		return @$RTN;
	}else{
		$RTN = {
			'imgsL'=>$imgsL,
			'imgsM'=>$imgsM,
			'imgsS'=>$imgsS,
			'imgsXS'=>$imgsXS,

			'sizeL'=>$sizeL,
			'sizeM'=>$sizeM,
			'sizeS'=>$sizeS,
			'sizeXS'=>$sizeXS,

			'sizeStrL'=>$sizeStrL,
			'sizeStrM'=>$sizeStrM,
			'sizeStrS'=>$sizeStrS,
			'sizeStrXS'=>$sizeStrXS,

			'gif_prefix_fmt'=>$gif_prefix_fmt,
			'gif_fmt'=>$gif_fmt,

			'png_prefix_fmt'=>$png_prefix_fmt,
			'png_fmt'=>$png_fmt,
		};
		return $RTN;
	}

}

sub getApachectlPath {
	my $path = &Cwd::abs_path(&rel2abs(&catdir($htdocs_path,'..','..','local','apache','bin','apachectl')));
	return $path;
}

sub Truncated {
	my $v = shift;
	return undef unless(defined $v);
	my $rate = 100000;
	return int($v * $rate + 0.5) / $rate;
}

sub readFile {
	my $path = shift;
#	return undef unless(defined $path && -f $path);
	return undef unless(defined $path);
#	print __LINE__,":\$path=[$path]\n";
	my $rtn;
	my $IN;
	if(open($IN,$path)){
		my $old  = $/;
		undef $/;
		$rtn = <$IN>;
		$/ = $old;
		close($IN);
	}
	return $rtn;
}

sub readObjFile {
	my $path = shift;
	return undef unless(defined $path && -f $path && -s $path);

	my $cmd = sprintf(qq{sed -e "/^mtllib/d" "%s" | sed -e "/^#/d" | sed -e "/^ *\$/d" |},$path);
	my $rtn;
	if(open(my $IN,$cmd)){
		local $/ = undef;
		$rtn = <$IN>;
		close($IN);
	}
	return $rtn;
}

1;
