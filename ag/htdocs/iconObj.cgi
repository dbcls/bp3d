#!/bp3d/local/perl/bin/perl

$| = 1;

use lib 'IM';

use strict;
use DBI;
use DBD::Pg;
use JSON::XS;
#use Image::Magick;
use File::Basename;
use POSIX qw(strftime);
use HTTP::Date;

require "common.pl";
require "common_db.pl";
require "common_image.pl";
my $dbh = &get_dbh();

my @extlist = qw|.cgi|;
my($name,$dir,$ext) = fileparse($0,@extlist);

my %FORM = ();
&decodeForm(\%FORM);
delete $FORM{_formdata} if(exists($FORM{_formdata}));

my %COOKIE = ();
&getCookie(\%COOKIE);

my $inprep = "icon/inprep.png";

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = fileparse($0,@extlist);
my $LOG;
if(exists $ENV{REQUEST_METHOD}){
	open($LOG,">> logs/$cgi_name.$COOKIE{'ag_annotation.session'}.txt");
#	flock($LOG,2);
}else{
	open($LOG,">-");
}
print $LOG "\n[$logtime]:$0\n";
foreach my $key (sort keys(%FORM)){
	print $LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
}
foreach my $key (sort keys(%COOKIE)){
	print $LOG __LINE__,":\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
}
foreach my $key (sort keys(%ENV)){
	print $LOG __LINE__,":\$ENV{$key}=[",$ENV{$key},"]\n";
}

#$FORM{i} = 'FMA7163' unless(defined $FORM{m});
$FORM{m} = &getDefOBJModel() unless(defined $FORM{m});

my $tg_model;
if(exists($FORM{m})){
	my $sql = qq|select tg_id,tg_model from tree_group where |;
	if($FORM{m} =~ /^[0-9]+$/){
		$sql .= qq|tg_id=?|;
	}else{
		$sql .= qq|lower(tg_model)=?|;
	}
	my $tg_id;
	my $sth = $dbh->prepare($sql);
	$sth->execute(lc($FORM{m}));
	$sth->bind_col(1, \$tg_id, undef);
	$sth->bind_col(2, \$tg_model, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;
	if(defined $tg_id){
		$FORM{m} = $tg_id;
	}else{
		delete $FORM{m};
	}

	unless(exists($FORM{v})){
		my $sql = qq|select tgi_name_e from tree_group_item where tg_id=? and tgi_delcause is null order by tgi_order limit 1|;
		my $tgi_name_e;
		my $sth = $dbh->prepare($sql);
		$sth->execute($FORM{m});
		$sth->bind_col(1, \$tgi_name_e, undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;
		$FORM{v} = $tgi_name_e if(defined $tgi_name_e);
	}

}
print $LOG __LINE__,":\$tg_model=[$tg_model]\n";

sub print_path {
	my $path = shift;
	my $p_path;
	if(defined $path){
		if(-e $path){
			$p_path = $path;
		}else{
			print qq|Status: $path\n\n|;
			return;
		}
	}else{
		$p_path = $inprep;
	}
	my $mtime;
	my $size;
#	($size,$mtime) = (stat($path))[7,9] if($ENV{REQUEST_METHOD} eq "GET" && defined $path && -e $path && -s $path);
	($size,$mtime) = (stat($path))[7,9] if(defined $path && -e $path && -s $path);
	my $datetime = strftime("%a, %d %b %Y %H:%M:%S %z", gmtime($mtime));
	if($ENV{REQUEST_METHOD} eq "GET" && defined $mtime && (!exists($FORM{_dc}) || $FORM{_dc} ne $mtime)){
		my $QUERY_STRING = $ENV{QUERY_STRING};
		$QUERY_STRING =~ s/[&]*_dc=[0-9]+// if(defined $QUERY_STRING && length($QUERY_STRING)>0);
		$QUERY_STRING =~ s/^&+//g if(defined $QUERY_STRING && length($QUERY_STRING)>0);
		$QUERY_STRING .= "&" if(defined $QUERY_STRING && length($QUERY_STRING)>0);
		$QUERY_STRING .= "_dc=$mtime";
		print qq|Location:$name$ext?$QUERY_STRING\n\n|;
		print $LOG __LINE__,qq|:Location:$name$ext?$QUERY_STRING\n|;
	}elsif($p_path eq $inprep){
		print qq|Location:$inprep\n\n|;
		print $LOG __LINE__,qq|:Location:$inprep\n|;
	}else{
		my $mime = qx{file -bi $p_path};
		$mime =~ s/\s*$//g;
		print qq|Content-type: $mime;\n|;
		print qq|Last-Modified: "|,&HTTP::Date::time2str($mtime),qq|\n|;
		print qq|Accept-Ranges: bytes\n|;
		print qq|Content-Length: $size\n|;
		print "\n";
		if($ENV{REQUEST_METHOD} eq "GET"){
			open(IN,$p_path);
			binmode(IN);
			binmode(STDOUT);
			print $_ while(<IN>);
			close(IN);
		}else{
			print $p_path,"\n";
		}
	}
}

unless(exists($FORM{i}) && exists($FORM{v}) && exists($FORM{m})){
	&print_path('404 Not Found');
	close($LOG);
	exit;
}

#&print_path();
#close($LOG);
#exit;


$COOKIE{"ag_annotation.images.tg_id"}=$FORM{m};

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);

$FORM{p} = &getDefImagePosition() unless(exists($FORM{p}));
$FORM{s} = 'S' unless(exists($FORM{s}));

=pod
if(exists($FORM{t})){
	$FORM{t} = lc $FORM{t};
	delete $FORM{t} unless($FORM{t} =~ /^conventional|bp3d|is_a|isa|part_of|partof$/);
}
$FORM{t} = 'conventional' unless(exists($FORM{t}));

$FORM{c} = &getDefImageCredit() unless(exists($FORM{c}));

my $t_type = 1;
if($FORM{t} =~ /^conventional|bp3d$/){
}elsif($FORM{t} =~ /^is_a|isa$/){
	$t_type = 3;
}elsif($FORM{t} =~ /^part_of|partof$/){
	$t_type = 4;
}
=cut
$inprep = "icon/inprep_L.png" if($FORM{s} eq "S" && -e "icon/inprep_L.png");


$FORM{i} =~ s/\s*$//g;
$FORM{i} =~ s/^\s*//g;
$FORM{i} =~ s/\s{2,}/ /g;
$FORM{i} =~ s/\..*$//g;

$FORM{p} =~ s/\s*$//g;
$FORM{p} =~ s/^\s*//g;
$FORM{p} =~ s/\s{2,}/ /g;

#$FORM{c} =~ s/\s*$//g;
#$FORM{c} =~ s/^\s*//g;
#$FORM{c} = '1' if($FORM{c} ne '0' && $FORM{c} ne '1');

my $size = '120x120';
$size = uc($FORM{s}) eq 'L' ? '640x640' : $FORM{s} =~ /^([0-9]{2,}x[0-9]{2,})$/ ? $1 :'120x120';
my $img_prefix = &getOBJImagePrefix($FORM{i},$tg_model,$FORM{p},$size,$FORM{v},$FORM{c});
my $img_extension = &getOBJImageFileExtension($FORM{p});
my $img_dir = &getOBJImageDir($FORM{i},$tg_model);
my $url = qq|$img_prefix$img_extension|;

print $LOG __LINE__,qq|:\$url=[$url]\n|;
#undef $url unless(-e $url);
#print $LOG __LINE__,qq|:\$url=[$url]\n|;
#unless(defined $url){
#	&print_path();
#	close($LOG);
#	exit;
#}
print $LOG __LINE__,qq|:\$url=[$url]\n|;
if(defined $url && -e $url && -s $url){
	&print_path($url);
	close($LOG);
	exit;
}

my $angle;
if(lc($FORM{p}) eq 'front'){
	$angle = 0;
}elsif(lc($FORM{p}) eq 'left'){
	$angle = 90;
}elsif(lc($FORM{p}) eq 'back'){
	$angle = 180;
}elsif(lc($FORM{p}) eq 'right'){
	$angle = 270;
}
print $LOG __LINE__,qq|:\$angle=[$angle]\n|;

#&print_path();
&print_path('202 Accepted') unless(defined $angle);
#exit;

my $obj_path = &getOBJPath($FORM{i},$tg_model,$FORM{v});
print $LOG __LINE__,qq|:\$obj_path=[$obj_path]\n|;
if(-e $obj_path){
	my $img_basedir = &getOBJImageBaseDir();
	my $img_prefix = &getOBJImagePrefix($FORM{i},$tg_model,'rotate',$size,$FORM{v},$FORM{c});
	my $lock_file = qq|$img_prefix.lock|;
	my $param_file = qq|$img_prefix.json|;
	if(!-e $param_file && mkdir($lock_file)){
		my $PARAM = {
			src => [$obj_path],
			dest => $img_prefix,
			size => $size,
			angle => defined $angle ? $angle+0 : undef
		};
		open(OUT,"> $param_file");
		print OUT encode_json($PARAM);
		close(OUT);
		rmdir $lock_file if(-e $lock_file);
#		exit;

	}
	if(-e $param_file){

		if(defined $angle){
			my $cmd = qq|./obj2image.pl "$param_file"|;
			print $LOG __LINE__,":\$cmd=[$cmd]\n";
			system($cmd);
#			unlink $param_file if(-e $param_file);
			if(defined $url && -e $url && -s $url){
				&print_path($url);
			}else{
				&print_path('204 No Content');
			}
			close(STDERR);
			close(STDOUT);
		}else{
			my $pid = fork;
			if(defined $pid){
				if($pid == 0){
					my $f1 = "tmp_image/$cgi_name.obj2image.log";
					my $f2 = "tmp_image/$cgi_name.obj2image.err";
					close(STDERR);
					close(STDOUT);
					open STDOUT, ">> $f1" || die "[$f1] $!\n";
					open STDERR, ">> $f2" || die "[$f2] $!\n";
					close(STDIN);
					my $cmd = qq|nice -n 19 ./obj2image.pl "$img_basedir"|;
					print $LOG __LINE__,":\$cmd=[$cmd]\n";
					system($cmd);
#					unlink $param_file if(-e $param_file);
					exit($?);
				}else{
					close(STDERR);
					close(STDOUT);
					print $LOG __LINE__,":\$pid=[$pid]\n";
					waitpid($pid,0);
					print $LOG __LINE__,":\$pid=[$pid]\n";
#					rmdir $lock_file if(-e $lock_file);
#					unlink $param_file if(-e $param_file);
				}
			}else{
				rmdir $lock_file if(-e $lock_file);
				unlink $param_file if(-e $param_file);
				die("Can't execute program");
			}
		}
#	}elsif(-e $param_file){
#		my $cmd;
#		if(defined $angle){
#			$cmd = qq|./obj2image.pl "$param_file"|;
#		}else{
#			$cmd = qq|nice -n 19 ./obj2image.pl "$img_basedir"|;
#		}
#		print $LOG __LINE__,":\$cmd=[$cmd]\n";
	}
}

close($LOG);

