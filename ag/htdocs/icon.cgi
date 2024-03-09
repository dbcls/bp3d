#!/bp3d/local/perl/bin/perl

$| = 1;

#use lib 'IM';

use strict;
use DBI;
use DBD::Pg;
use JSON::XS;
#use Image::Magick;
use File::Basename;
use POSIX qw(strftime);
use HTTP::Date;
use File::Spec::Functions qw(catdir catfile rel2abs);

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI::Cookie;
#use FindBin;
#use lib $FindBin::Bin,qq|$FindBin::Bin/IM|;
use Cwd;
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'API'),&Cwd::abs_path(&catdir($FindBin::Bin,'..','lib')),&Cwd::abs_path(&catdir($FindBin::Bin,'..','..','ag-common','lib'));

require "common.pl";
require "common_db.pl";
require "common_image.pl";
my $dbh = &get_dbh();

#my @extlist = qw|.cgi|;
#my($cgi_name,$dir,$cgi_ext) = fileparse($0,@extlist);

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);

#my %FORM = ();
#&decodeForm(\%FORM);
#delete $FORM{_formdata} if(exists($FORM{_formdata}));

#my %COOKIE = ();
#&getCookie(\%COOKIE);

my $inprep = "icon/inprep.png";

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = fileparse($0,@extlist);
#open(LOG,">> $FindBin::Bin/logs/$COOKIE{'ag_annotation.session'}.$cgi_name.txt");
#flock(LOG,2);
#print LOG "\n[$logtime]:$0\n";
#foreach my $key (sort keys(%FORM)){
#	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}
#foreach my $key (sort keys(%COOKIE)){
#	print LOG __LINE__,":\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
#}
#foreach my $key (sort keys(%ENV)){
#	print LOG __LINE__,":\$ENV{$key}=[",$ENV{$key},"]\n";
#}

#http://192.168.1.229:38321/icon.cgi?q=2.0/FMA52735_back_640x640.png
#http://192.168.1.229:38321/bp3d_images/3.0/FMA7157_front_120x120.png
#http://192.168.1.229:38321/bp3d_images/3.0/FMA7157_120x120.gif
#http://192.168.1.229:38321/bp3d_images/2.0/FMA78448_left_640x640.png
if(exists($FORM{'q'}) && defined $FORM{'q'}){
	if(-e qq|bp3d_images/$FORM{'q'}|){
		print qq|Location:bp3d_images/$FORM{'q'}\n\n|;
#		print LOG __LINE__,qq|:Location:bp3d_images/$FORM{'q'}\n|;
		exit;
	}else{
		if($FORM{'q'} =~ /^([0-9\.]+)\/(BP|FMA)([0-9]+)_([a-z]+)_([0-9x]+)\.png/){
			my $s = $5;
			if($s eq qq|640x640|){
				$s = 'L';
			}else{
				$s = 'S';
			}
			my $QUERY_STRING = qq|i=$2$3&v=$1&m=bp3d&p=$4&s=$s&t=conventional&c=1|;
			my $form = {};
			$form->{'tg_id'} = 1;
			$form->{'version'} = $1;
			&convVersionName2RendererVersion($dbh,$form,\%COOKIE);
			my $img_file = &getImagePath($2.$3,$4,$form->{'version'},qq|$5|,'1','1');
#			print LOG __LINE__,qq|:\$img_file=[$img_file]\n|;
			if(-e $img_file && -s $img_file){
				my $mtime = (stat($img_file))[9];
				print qq|Status:301\n|;
				print qq|Location:$img_file?$mtime\n\n|;
#				print LOG __LINE__,qq|:Location:$img_file?$mtime\n|;
			}else{
				print qq|Location:$cgi_name$cgi_ext?$QUERY_STRING\n\n|;
				print __LINE__,qq|:Location:$cgi_name$cgi_ext?$QUERY_STRING\n\n|;
			}
			exit;
		}elsif($FORM{'q'} =~ /^([0-9\.]+)\/(BP|FMA)([0-9]+)_([0-9x]+)\.gif/){
			my $s = $4;
			if($s eq qq|640x640|){
				$s = 'L';
			}else{
				$s = 'S';
			}
			my $QUERY_STRING = qq|i=$2$3&v=$1&m=bp3d&p=rotate&s=$s&t=conventional&c=1|;
			my $form = {};
			$form->{'tg_id'} = 1;
			$form->{'version'} = $1;
			&convVersionName2RendererVersion($dbh,$form,\%COOKIE);
			my $img_file = &getImagePath($2.$3,'rotate',$form->{'version'},$4,'1','1');
#			print LOG __LINE__,qq|:\$img_file=[$img_file]\n|;
			if(-e $img_file && -s $img_file){
				my $mtime = (stat($img_file))[9];
				print qq|Status:301\n|;
				print qq|Location:$img_file?$mtime\n\n|;
#				print LOG __LINE__,qq|:Location:$img_file?$mtime\n|;
			}else{
				print qq|Location:$cgi_name$cgi_ext?$QUERY_STRING\n\n|;
#				print LOG __LINE__,qq|:Location:$cgi_name$cgi_ext?$QUERY_STRING\n\n|;
			}
			exit;
		}elsif($FORM{'q'} =~ /^([0-9\.]+)\/.+\/(BP|FMA)([0-9]+)_([a-z]+)_([0-9x]+)\.png/){
			my $s = $5;
			if($s eq qq|640x640|){
				$s = 'L';
			}else{
				$s = 'S';
			}
			my $QUERY_STRING = qq|i=$2$3&v=$1&m=bp3d&p=$4&s=$s&t=conventional&c=1|;
			my $form = {};
			$form->{'tg_id'} = 1;
			$form->{'version'} = $1;
			&convVersionName2RendererVersion($dbh,$form,\%COOKIE);
			my $img_file = &getImagePath($2.$3,$4,$form->{'version'},qq|$5|,'1','1');
#			print LOG __LINE__,qq|:\$img_file=[$img_file]\n|;
			if(-e $img_file && -s $img_file){
				my $mtime = (stat($img_file))[9];
				print qq|Status:301\n|;
				print qq|Location:$img_file?$mtime\n\n|;
#				print LOG __LINE__,qq|:Location:$img_file?$mtime\n|;
			}else{
				print qq|Location:$cgi_name$cgi_ext?$QUERY_STRING\n\n|;
#				print LOG __LINE__,qq|:Location:$cgi_name$cgi_ext?$QUERY_STRING\n\n|;
			}
			exit;
		}elsif($FORM{'q'} =~ /^([0-9\.]+)\/.+\/(BP|FMA)([0-9]+)_([0-9x]+)\.gif/){
			my $s = $4;
			if($s eq qq|640x640|){
				$s = 'L';
			}else{
				$s = 'S';
			}
			my $QUERY_STRING = qq|i=$2$3&v=$1&m=bp3d&p=rotate&s=$s&t=conventional&c=1|;
			my $form = {};
			$form->{'tg_id'} = 1;
			$form->{'version'} = $1;
			&convVersionName2RendererVersion($dbh,$form,\%COOKIE);
			my $img_file = &getImagePath($2.$3,'rotate',$form->{'version'},$4,'1','1');
#			print LOG __LINE__,qq|:\$img_file=[$img_file]\n|;
			if(-e $img_file && -s $img_file){
				my $mtime = (stat($img_file))[9];
				print qq|Status:301\n|;
				print qq|Location:$img_file?$mtime\n\n|;
#				print LOG __LINE__,qq|:Location:$img_file?$mtime\n|;
			}else{
				print qq|Location:$cgi_name$cgi_ext?$QUERY_STRING\n\n|;
#				print LOG __LINE__,qq|:Location:$cgi_name$cgi_ext?$QUERY_STRING\n\n|;
			}
			exit;
		}
	}
}

if(exists $FORM{'i'} && defined $FORM{'i'}){
		my $sql_rep =<<SQL;
select
 rep.ci_id,
 rep.cb_id,
 rep.md_id,
 rep.mv_id,
 rep.mr_id,
 rep.bul_id,
 rep.cdi_name,
 md_abbr,
 mr_version,
 bul_name_e,
 mca_id
from view_representation as rep
left join (select md_id,md_abbr from model) as md on (md.md_id = rep.md_id)
left join (select md_id,mv_id,mr_id,mr_version from model_revision) as mr on (mr.md_id = rep.md_id and mr.mv_id = rep.mv_id and mr.mr_id = rep.mr_id)
left join (select bul_id,bul_name_e from buildup_logic) as bul on (bul.bul_id = rep.bul_id)
where
 rep.rep_id=?
SQL
	my $ci_id;
	my $cb_id;
	my $md_id;
	my $mv_id;
	my $mr_id;
	my $bul_id;
	my $cdi_name;
	my $md_abbr;
	my $mr_version;
	my $bul_name_e;
	my $mca_id;
	my $sth_rep = $dbh->prepare($sql_rep);
	$sth_rep->execute($FORM{'i'});
	if($sth_rep->rows()>0){
		$sth_rep->bind_col(1, \$ci_id, undef);
		$sth_rep->bind_col(2, \$cb_id, undef);
		$sth_rep->bind_col(3, \$md_id, undef);
		$sth_rep->bind_col(4, \$mv_id, undef);
		$sth_rep->bind_col(5, \$mr_id, undef);
		$sth_rep->bind_col(6, \$bul_id, undef);
		$sth_rep->bind_col(7, \$cdi_name, undef);
		$sth_rep->bind_col(8, \$md_abbr, undef);
		$sth_rep->bind_col(9, \$mr_version, undef);
		$sth_rep->bind_col(10, \$bul_name_e, undef);
		$sth_rep->bind_col(11, \$mca_id, undef);
		$sth_rep->fetch;
	}
	$sth_rep->finish;
	undef $sth_rep;

	$FORM{'ci_id'} = $ci_id if(defined $ci_id);
	$FORM{'cb_id'} = $cb_id if(defined $cb_id);
	$FORM{'md_id'} = $md_id if(defined $md_id);
	$FORM{'mv_id'} = $mv_id if(defined $mv_id);
	$FORM{'mr_id'} = $mr_id if(defined $mr_id);
	$FORM{'bul_id'} = $bul_id if(defined $bul_id);

	$FORM{'i'} = $cdi_name if(defined $cdi_name);
#	$FORM{'i'} = $mca_id if(defined $mca_id);
	$FORM{'m'} = $md_abbr if(defined $md_abbr);
	$FORM{'v'} = $mr_version if(defined $mr_version);
	$FORM{'t'} = $bul_name_e if(defined $bul_name_e);

	delete $FORM{'c'};
}

if(exists($FORM{'m'})){
	my $sql = qq|select md_id from model where |;
	if($FORM{'m'} =~ /^[0-9]+$/){
		$sql .= qq|md_id=?|;
	}else{
		$sql .= qq|lower(md_abbr)=?|;
	}
	my $md_id;
	my $sth = $dbh->prepare($sql);
	$sth->execute(lc($FORM{'m'}));
	$sth->bind_col(1, \$md_id, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;
	if(defined $md_id){
		$FORM{'m'} = $md_id;

		unless(exists($FORM{'v'})){
			my $sql = qq|select mv_name_e from model_version where md_id=? and mv_delcause is null order by mv_order limit 1|;
			my $mv_name_e;
			my $sth = $dbh->prepare($sql);
			$sth->execute($FORM{'m'});
			$sth->bind_col(1, \$mv_name_e, undef);
			$sth->fetch;
			$sth->finish;
			undef $sth;
			$FORM{'v'} = $mv_name_e if(defined $mv_name_e);
		}

	}else{
		delete $FORM{'m'};
	}

}

sub print_path {
	my $path = shift;
	my $p_path;
	if(defined $path && -e $path){
		$p_path = $path;
	}else{
		$p_path = $inprep;
	}
	my $mtime;
	my $size;
	($size,$mtime) = (stat($path))[7,9] if($ENV{'REQUEST_METHOD'} eq 'GET' && defined $path && -e $path && -s $path);
	my $datetime = strftime("%a, %d %b %Y %H:%M:%S %z", gmtime($mtime));
	if($ENV{'REQUEST_METHOD'} eq 'GET' && defined $mtime && (!exists($FORM{'_dc'}) || $FORM{'_dc'} ne $mtime)){
		my $QUERY_STRING = $ENV{QUERY_STRING};
		$QUERY_STRING =~ s/[&]*_dc=[0-9]+// if(defined $QUERY_STRING && length($QUERY_STRING)>0);
		$QUERY_STRING =~ s/^&+//g if(defined $QUERY_STRING && length($QUERY_STRING)>0);
		$QUERY_STRING .= "&" if(defined $QUERY_STRING && length($QUERY_STRING)>0);
		$QUERY_STRING .= "_dc=$mtime";
		print qq|Location:$cgi_name$cgi_ext?$QUERY_STRING\n\n|;
#		print LOG __LINE__,qq|:Location:$cgi_name$cgi_ext?$QUERY_STRING\n|;
	}elsif($p_path eq $inprep){
		print qq|Location:$inprep\n\n|;
#		print LOG __LINE__,qq|:Location:$inprep\n|;
	}else{

		while(defined $p_path && -f $p_path && -l $p_path){
			my $l = -s $p_path ? readlink($p_path) : undef;
			$l = &rel2abs($l,&File::Basename::dirname($p_path)) if(defined $l && !-e $l);
			$p_path = $l;
		}
		if(defined $p_path && -f $p_path && -s $p_path){
			my $mime = qx{file -bi $p_path};
			$mime =~ s/\s*$//g;
			if($mime eq 'application/x-not-regular-file'){
				if($p_path =~ /\.gif$/){
					$mime = qq|image/gif; charset=binary|;
				}elsif($p_path =~ /\.png$/){
					$mime = qq|image/png; charset=binary|;
				}
			}
	#		print LOG __LINE__,qq|:$p_path\n|;
	#		print LOG __LINE__,qq|:Content-type: $mime;\n|;
			print qq|Content-type: $mime;\n|;
			print qq|Last-Modified: |,&HTTP::Date::time2str($mtime),qq|\n|;
			print qq|Accept-Ranges: bytes\n|;
			print qq|Content-Length: $size\n|;
			print "\n";
			open(IN,$p_path);
			binmode(IN);
			binmode(STDOUT);
			print $_ while(<IN>);
			close(IN);
		}

	}
}

$FORM{'p'} = &getDefImagePosition() unless(exists($FORM{'p'}));
$FORM{'s'} = 'S' unless(exists($FORM{'s'}));
$FORM{'c'} = &getDefImageCredit() unless(exists($FORM{'c'}));

my $geometry = uc($FORM{'s'}) eq 'L' ? '640x640' : ($FORM{'s'} =~ /^([0-9]{2,}x[0-9]{2,})$/ ? $1 :'120x120');

unless(exists($FORM{'i'}) && exists($FORM{'v'}) && exists($FORM{'m'})){
	&print_path();
#	close(LOG);
	exit;
}



$COOKIE{'ag_annotation.images.tg_id'}=$FORM{'m'};

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);

if(exists($FORM{'t'})){
	$FORM{'t'} = lc $FORM{'t'};
	delete $FORM{'t'} unless($FORM{'t'} =~ /^conventional|bp3d|is_a|isa|part_of|partof$/);
}
$FORM{'t'} = 'conventional' unless(exists($FORM{'t'}));


my $t_type = 1;
if($FORM{'t'} =~ /^conventional|bp3d$/){
}elsif($FORM{'t'} =~ /^is_a|isa$/){
	$t_type = 3;
}elsif($FORM{'t'} =~ /^part_of|partof$/){
	$t_type = 4;
}
$inprep = "icon/inprep_L.png" if($FORM{'s'} eq "S" && -e "icon/inprep_L.png");


$FORM{'i'} =~ s/\s*$//g;
$FORM{'i'} =~ s/^\s*//g;
$FORM{'i'} =~ s/\s{2,}/ /g;

$FORM{'p'} =~ s/\s*$//g;
$FORM{'p'} =~ s/^\s*//g;
$FORM{'p'} =~ s/\s{2,}/ /g;

$FORM{'c'} =~ s/\s*$//g;
$FORM{'c'} =~ s/^\s*//g;
$FORM{'c'} = '1' if($FORM{'c'} ne '0' && $FORM{'c'} ne '1');

my $none_file;
my $img_file = &getImagePath($FORM{'i'},$FORM{'p'},$FORM{'v'},$geometry,$t_type,$FORM{'c'});
my $url = $img_file;
#print LOG __LINE__,qq|:\$url=[$url]\n|;
unless(-e $url){
	my @TEMP = split(/\//,$img_file);
	pop @TEMP;
	my $path = join("/",@TEMP);
	undef @TEMP;
	$none_file = qq|$path/$FORM{'i'}.none|;
#print LOG __LINE__,qq|:\$none_file=[$none_file]\n|;
	unless(-e $none_file){
		my $json_file = qq|$path/$FORM{'i'}.txt|;
#print LOG __LINE__,qq|:\$json_file=[$json_file]\n|;
		if(-e $json_file){
			open(JSON_IN,"< $json_file");
			my @TEMP = <JSON_IN>;
			close(JSON_IN);
			my $json_text = join("",@TEMP);
#			my $AgBoundingBox = from_json($json_text);
			my $AgBoundingBox = decode_json($json_text);
#			if(
#				$AgBoundingBox->{xmax} eq "0.0" && $AgBoundingBox->{xmin} eq "0.0" &&
#				$AgBoundingBox->{ymax} eq "0.0" && $AgBoundingBox->{ymin} eq "0.0" &&
#				$AgBoundingBox->{zmax} eq "0.0" && $AgBoundingBox->{zmin} eq "0.0"
#			){
			if(
				$AgBoundingBox->{xmax} == 0 && $AgBoundingBox->{xmin} == 0 &&
				$AgBoundingBox->{ymax} == 0 && $AgBoundingBox->{ymin} == 0 &&
				$AgBoundingBox->{zmax} == 0 && $AgBoundingBox->{zmin} == 0
			){
				undef $url;
				system(qq|touch $none_file|);
			}
		}else{
			undef $url;
		}
	}else{
		undef $url;
	}
}
#print LOG __LINE__,qq|:\$url=[$url]\n|;
unless(defined $url){
	&print_path();
#	close(LOG);
	exit;
}
#print LOG __LINE__,qq|:\$url=[$url]\n|;
if(-e $url && -s $url){
	&print_path($url);
#	close(LOG);
	exit;
}

&print_path();
#close(LOG);


unless(defined $none_file){
	my @TEMP = split(/\//,$img_file);
	pop @TEMP;
	my $path = join("/",@TEMP);
	undef @TEMP;
	$none_file = qq|$path/$FORM{'i'}.none|;
}
exit if(-e $none_file);

#exit;

#exit if($t_type ne "1");

#close(STDERR);
#close(STDOUT);

my @TEMP = split(/\//,$url);
pop @TEMP;
my @PATH = ();
my $path;
foreach (@TEMP){
	push(@PATH,$_);
	$path = join("/",@PATH);
	next if(-e $path);
	mkdir $path;
	chmod 0777,$path;
}

my $basedir = &getImageBaseDir($FORM{'v'},$t_type);
my $param_file = qq|$basedir/$FORM{'i'}.prm|;
unless(-e $param_file){
	my $PARAM = {
		out_dir => $path,
		version => $FORM{'v'},
		type    => $t_type,
		f_id    => $FORM{'i'},
		f_pid   => exists($FORM{'r'})?$FORM{'r'}:undef
	};
	open(OUT,"> $param_file");
#	my $json = to_json($PARAM);
	my $json = &JSON::XS::encode_json($PARAM);
	print OUT $json;
	close(OUT);
}

my $pid = fork;
if(defined $pid){
	if($pid == 0){
		my $f1 = "tmp_image/make_thumbnail_batch.log";
		my $f2 = "tmp_image/make_thumbnail_batch.err";
		close(STDOUT);
		close(STDERR);
		open STDOUT, ">> $f1" || die "[$f1] $!\n";
		open STDERR, ">> $f2" || die "[$f2] $!\n";
		close(STDIN);
		exec(qq|nice -n 19 ./make_thumbnail_batch.pl $basedir|);
#		exec(qq|nohup ./make_thumbnail_batch.pl $basedir|);
		exit(1);
	}
}else{
	die("Can't execute program");
}
