#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
#use Image::Info qw(image_info dim);
#use Image::Magick;
#use Storable;
#use SetEnv;
use File::Basename;
use File::Path;
use File::Spec::Functions qw(abs2rel catdir catfile);
use Digest::MD5 qw(md5 md5_hex md5_base64);
#use Clone;
use List::Util qw(max);

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
require "webgl_common.pl";
use cgi_lib::common;

#require "$FindBin::Bin/common_zrangeobject.pl";
my $dbh = &get_dbh();

use constant {
	DEBUG => 1,
};

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);

#my $env = SetEnv->new;
#my @BP3DVERSION = ();
#foreach my $version (@{$env->{versions}}){
#	push(@BP3DVERSION,"$version");
#}

#DEBUG 常に削除
#delete $FORM{parent} if(exists($FORM{parent}));
#my $lsdb_OpenID;
#my $lsdb_Auth;
#my $parentURL = $FORM{parent} if(exists($FORM{parent}));
#my $parent_text;
#if(defined $parentURL){
#	($lsdb_OpenID,$lsdb_Auth) = &openidAuth($parentURL);
#}

my @FILTER = ();
=pod
my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
my $filetime = sprintf("%04d/%02d/%02d",$year+1900,$mon+1,$mday);
my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);
my $log_dir = &catdir($FindBin::Bin,'logs',$filetime);
if(exists $ENV{'HTTP_X_FORWARDED_FOR'}){
	my @H = split(/,\s*/,$ENV{'HTTP_X_FORWARDED_FOR'});
	$log_dir = &catdir($log_dir,$H[0]);
}elsif(exists $ENV{'REMOTE_ADDR'}){
	$log_dir = &catdir($log_dir,$ENV{'REMOTE_ADDR'});
}
$log_dir = &catdir($log_dir,$COOKIE{'ag_annotation.session'}) if(exists $COOKIE{'ag_annotation.session'});
unless(-e $log_dir){
	my $old_umask = umask(0);
	&File::Path::mkpath($log_dir,0,0777);
	umask($old_umask);
}
open(LOG,">> $log_dir/$cgi_name.txt");
flock(LOG,2);
print $LOG "\n[$logtime]:$0\n";
foreach my $key (sort keys(%FORM)){
	print $LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
}
=cut
my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0, qr/\..*$/);
my $LOG = &cgi_lib::common::getLogFH(\%FORM,\%COOKIE);

foreach my $key (sort keys(%FORM)){
	if($key =~ /filter/){
		my $key2 = &url_decode($key);
#		print $LOG __LINE__,":\$FORM{$key2}=[",$FORM{$key},"]\n";
		if($key2 =~ /^filter\[([0-9]+)\]\[data\]\[type\]$/){
			my $idx = $1;
			$FILTER[$idx]->{data}->{type} = $FORM{$key};
		}elsif($key2 =~ /^filter\[([0-9]+)\]\[data\]\[comparison\]$/){
			my $idx = $1;
			$FILTER[$idx]->{data}->{comparison} = $FORM{$key};
		}elsif($key2 =~ /^filter\[([0-9]+)\]\[data\]\[value\]$/){
			my $idx = $1;
			$FILTER[$idx]->{data}->{value} = $FORM{$key};
		}elsif($key2 =~ /^filter\[([0-9]+)\]\[field\]$/){
			my $idx = $1;
			$FILTER[$idx]->{field} = $FORM{$key};
		}
	}else{
#		print $LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
	}
}

$SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit";
sub sigexit{
	my($date) = `date`;
	$date =~ s/\s*$//g;
	print STDERR "[$date] KILL THIS CGI!![$ENV{SCRIPT_NAME}]\n";
	exit(1);
}

#####
#####
#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $IMAGES = {
	"datas" => [],
	"total" => 0,
	"success" => JSON::XS::false
};

my $ci_id=$FORM{'ci_id'};
my $cb_id=$FORM{'cb_id'};
my $md_id=$FORM{'md_id'};
my $mv_id=$FORM{'mv_id'};
my $crl_id=$FORM{'crl_id'};

$md_id=1 unless(defined $md_id && $md_id =~ /^[1-9][0-9]*$/);
unless(defined $mv_id && $mv_id =~ /^[1-9][0-9]*$/){
	$mv_id = undef;
	$ci_id = undef;
	$cb_id = undef;
	my $sth_mv;
	if(defined $FORM{'mv_id'} && $FORM{'mv_id'} =~ /^\-[1-9][0-9]*$/){
#		$mv_id += $FORM{'mv_id'};
		$sth_mv = $dbh->prepare("select mv_id from model_version where mv_delcause is null and mv_use and md_id=? order by mv_id desc limit 2") or die $dbh->errstr;
		$sth_mv->execute($md_id) or die $dbh->errstr;
		if($sth_mv->rows()>1){
			$sth_mv->bind_col(1, \$mv_id, undef);
			while($sth_mv->fetch){}
		}
		$sth_mv->finish;
		undef $sth_mv;
	}else{
		$sth_mv = $dbh->prepare("select max(mv_id) from model_version where mv_delcause is null and mv_use and md_id=?") or die $dbh->errstr;
		$sth_mv->execute($md_id) or die $dbh->errstr;
		$sth_mv->bind_col(1, \$mv_id, undef);
		$sth_mv->fetch;
		$sth_mv->finish;
		undef $sth_mv;
	}
	if(defined $mv_id){
		$sth_mv = $dbh->prepare("select ci_id,cb_id from model_version where md_id=? and mv_id=?") or die $dbh->errstr;
		$sth_mv->execute($md_id,$mv_id) or die $dbh->errstr;
		$sth_mv->bind_col(1, \$ci_id, undef);
		$sth_mv->bind_col(2, \$cb_id, undef);
		$sth_mv->fetch;
		$sth_mv->finish;
		undef $sth_mv;
	}
}

unless(defined $ci_id && defined $cb_id && defined $md_id && defined $mv_id){
	$IMAGES->{'success'} = JSON::XS::true;
	&cgi_lib::common::printContentJSON($IMAGES,\%FORM);
	close($LOG) if(defined $LOG);
	exit;
}

#$crl_id = 3 unless(defined $crl_id);
#$crl_id = 4 unless(defined $crl_id);
$crl_id = 0 unless(defined $crl_id);

if(defined $LOG){
	&cgi_lib::common::message('$md_id='.$md_id, $LOG);
	&cgi_lib::common::message('$mv_id='.$mv_id, $LOG);
	&cgi_lib::common::message('$ci_id='.$ci_id, $LOG);
	&cgi_lib::common::message('$cb_id='.$cb_id, $LOG);
	&cgi_lib::common::message('$crl_id='.$crl_id, $LOG);
}
$FORM{'ci_id'}=$ci_id;
$FORM{'cb_id'}=$cb_id;
$FORM{'md_id'}=$md_id;
$FORM{'mv_id'}=$mv_id;
$FORM{'crl_id'}=$crl_id;

#77:$FORM{'segments'}=[[{"disp":"Head","value":"head","zmin":1431.1,"zmax":null},{"disp":"Upper body","value":"body","zmin":914.2,"zmax":1431.1},{"disp":"Leg","value":"leg","zmin":null,"zmax":914.2},{"disp":"Head+Upper body","value":"head-body","zmin":"[1431.1,914.2]","zmax":"[null,1431.1]"},{"disp":"Upper body+Leg","value":"body-leg","zmin":"[914.2 , null]","zmax":"[1431.1,914.2]"},{"disp":"All","value":"all","zmin":"[1431.1,914.2,null]","zmax":"[null,1431.1,914.2]"},{"disp":"None","value":"none","zmin":null,"zmax":null}]]
#78:$FORM{'volumes'}=[[{"disp":"10未満","value":"x-10","min":null,"max":10},{"disp":"10以上100未満","value":"10-100","min":10,"max":100},{"disp":"100以上1000未満","value":"100-1000","min":100,"max":1000},{"disp":"1000以上","value":"1000-x","min":1000,"max":null}]]

#my $cache_file = qq|$FindBin::Bin/cache_fma/$FORM{'version'}/$cgi_name/|;
#my $cache_path = &catdir($FindBin::Bin,qq|cache_fma|,$FORM{'version'},$cgi_name);

my %CDI_ID2NAME;
my %CDI_NAME2ID;
if(1){
	my $sth_cdi = $dbh->prepare(qq|select cdi_id,cdi_name from concept_data_info where cdi_delcause is null and ci_id=$ci_id|) or die $dbh->errstr;
	$sth_cdi->execute() or die $dbh->errstr;
	my $column_number = 0;
	my $cdi_id;
	my $cdi_name;
	$sth_cdi->bind_col(++$column_number, \$cdi_id, undef);
	$sth_cdi->bind_col(++$column_number, \$cdi_name, undef);
	while($sth_cdi->fetch){
		$CDI_ID2NAME{$cdi_id} = $cdi_name;
		$CDI_NAME2ID{$cdi_name} = $cdi_id;
	}
	$sth_cdi->finish;
	undef $sth_cdi;
}

my %SEGMENT_ZRANGE_ID2ABBR;
my %SEGMENT_ZRANGE_ABBR2ID;
if(1){
	my $sth_cszr_sel = $dbh->prepare(qq|select cszr_id,cszr_abbr from concept_segment_zrange where cszr_delcause is null|) or die $dbh->errstr;
	$sth_cszr_sel->execute() or die $dbh->errstr;
	my $column_number = 0;
	my $cszr_id;
	my $cszr_abbr;
	$sth_cszr_sel->bind_col(++$column_number, \$cszr_id, undef);
	$sth_cszr_sel->bind_col(++$column_number, \$cszr_abbr, undef);
	while($sth_cszr_sel->fetch){
		$SEGMENT_ZRANGE_ID2ABBR{$cszr_id} = $cszr_abbr;
		$SEGMENT_ZRANGE_ABBR2ID{$cszr_abbr} = $cszr_id;
	}
	$sth_cszr_sel->finish;
	undef $sth_cszr_sel;
}
my %SEGMENT_VALUME_ID2ABBR;
my %SEGMENT_VALUME_ABBR2ID;
if(1){
	my $sth_csv_sel = $dbh->prepare(qq|select csv_id,csv_abbr from concept_segment_volume where csv_delcause is null|) or die $dbh->errstr;
	$sth_csv_sel->execute() or die $dbh->errstr;
	my $column_number = 0;
	my $csv_id;
	my $csv_abbr;
	$sth_csv_sel->bind_col(++$column_number, \$csv_id, undef);
	$sth_csv_sel->bind_col(++$column_number, \$csv_abbr, undef);
	while($sth_csv_sel->fetch){
		$SEGMENT_VALUME_ID2ABBR{$csv_id}= $csv_abbr;
		$SEGMENT_VALUME_ABBR2ID{$csv_abbr}= $csv_id;
	}
	$sth_csv_sel->finish;
	undef $sth_csv_sel;
}

my %USE_CDI_ID;
unless(exists $FORM{'cdi_id'} && defined $FORM{'cdi_id'} && exists $CDI_NAME2ID{$FORM{'cdi_id'}} && defined $CDI_NAME2ID{$FORM{'cdi_id'}}){
	if(exists $FORM{'degenerate_same_shape_icons'} && defined $FORM{'degenerate_same_shape_icons'} && $FORM{'degenerate_same_shape_icons'} eq 'true'){
		my $sth = $dbh->prepare(qq|select cmm.cdi_id,mca_id,max(cti_depth) as cti_depth from concept_art_map_modified as cmm,(select ci_id,cb_id,crl_id,cdi_id,max(cti_depth) as cti_depth from concept_tree_info group by ci_id,cb_id,crl_id,cdi_id) as cti where cmm.ci_id=cti.ci_id and cmm.cb_id=cti.cb_id and cmm.crl_id=cti.crl_id and cmm.cdi_id=cti.cdi_id and cmm.md_id=$md_id and cmm.mv_id=$mv_id and cmm.ci_id=$ci_id and cmm.cb_id=$cb_id and cmm.crl_id=$crl_id group by cmm.cdi_id,mca_id order by mca_id,cti_depth desc;|) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		my %USE_MCA_ID;
		while(my $hash_ref = $sth->fetchrow_hashref){
			next if(exists $USE_MCA_ID{$hash_ref->{'mca_id'}});
			$USE_MCA_ID{$hash_ref->{'mca_id'}} = undef;
			$USE_CDI_ID{$hash_ref->{'cdi_id'}} = undef;
		}
		$sth->finish;
		undef $sth;
		undef %USE_MCA_ID;
	}
}

my $tbp_max_enter;
if(1){
	my $sth_tbp_enter = $dbh->prepare(qq|select EXTRACT(EPOCH FROM max(tbp_enter)) from thumbnail_background_part where md_id=$md_id and mv_id=$mv_id and ci_id=$ci_id|) or die $dbh->errstr;
	$sth_tbp_enter->execute() or die $dbh->errstr;
	my $column_number = 0;
	$sth_tbp_enter->bind_col(++$column_number, \$tbp_max_enter, undef);
	$sth_tbp_enter->fetch;
	$sth_tbp_enter->finish;
	undef $sth_tbp_enter;
}
$tbp_max_enter = 0 unless(defined $tbp_max_enter);

my %CDI2ENTRY;
if(1){
	my $sth_cd = $dbh->prepare(qq|select cdi_id,EXTRACT(EPOCH FROM MAX(GREATEST(cd_entry,seg_entry))) as cd_entry from concept_data as cd left join(select seg_id,seg_entry,seg_thum_fgcolor from concept_segment) as seg on seg.seg_id=cd.seg_id where cd_delcause is null and ci_id=$ci_id and cb_id=$cb_id GROUP BY cdi_id|) or die $dbh->errstr;
	my $cdi_id;
	my $cd_entry;
	$sth_cd->execute() or die $dbh->errstr;
	my $column_number = 0;
	$sth_cd->bind_col(++$column_number, \$cdi_id, undef);
	$sth_cd->bind_col(++$column_number, \$cd_entry, undef);
	while($sth_cd->fetch){
		next unless(defined $cdi_id && defined $cd_entry);
		$CDI2ENTRY{$cdi_id} = $cd_entry - 0;
	}
	$sth_cd->finish;
	undef $sth_cd;
}

my $sth_mca = $dbh->prepare(qq|select md5(art_ids_arr) from mapping_concepts_arts where mca_id=?|) or die $dbh->errstr;

sub setContents {
	my $sth = shift;
	my $inprep = &catfile('icon','inprep.png');
	while(my $hash_ref = $sth->fetchrow_hashref){
		my $cdi_name = $CDI_ID2NAME{$hash_ref->{'cdi_id'}};
		next unless(defined $cdi_name);
#		my $img_prefix = &getCmImagePrefix($md_id,$mv_id,undef,$cdi_name);
#		my $img_prefix = &getMcaImagePrefix($hash_ref->{'mca_id'});

		$sth_mca->execute($hash_ref->{'mca_id'}) or die $dbh->errstr;
		my $column_number = 0;
		my $art_ids_md5;
		$sth_mca->bind_col(++$column_number, \$art_ids_md5, undef);
		$sth_mca->fetch;
		$sth_mca->finish;
		my $img_prefix = &getMcaImagePrefix($art_ids_md5);

&cgi_lib::common::message($cdi_name // '',$LOG);
&cgi_lib::common::message($img_prefix // '',$LOG);

		my $img = &getImageFileList($img_prefix, [undef,[120,120],undef,[16,16]]);
&cgi_lib::common::message($img // '',$LOG);
		my $img_paths;
#		foreach my $imgsizekey (qw/imgsL imgsM imgsS imgsXS/){
		foreach my $imgsizekey (qw/imgsM imgsXS/){
#			say STDERR __LINE__.':'.$imgsizekey;
			next unless(exists $img->{$imgsizekey} && defined $img->{$imgsizekey} && ref $img->{$imgsizekey} eq 'ARRAY');
			foreach my $imgpath (@{$img->{$imgsizekey}}){
#				next unless(-e $imgpath && -f $imgpath && -s $imgpath);
				$img_paths = $img_paths || {};
				if(-e $imgpath && -f $imgpath && -s $imgpath){

					my $mtime = (stat($imgpath))[9];

#					&cgi_lib::common::message('$imgpath='.$imgpath, $LOG) if(defined $LOG);
#					&cgi_lib::common::message('$mtime='.$mtime, $LOG) if(defined $LOG);

#					&cgi_lib::common::message('$cm_modified_epoch='.$hash_ref->{'cm_modified_epoch'}, $LOG) if(defined $LOG);
#					&cgi_lib::common::message('$tbp_max_enter='.$tbp_max_enter, $LOG) if(defined $LOG);
#					&cgi_lib::common::message('$CDI2ENTRY='.$CDI2ENTRY{$hash_ref->{'cdi_id'}}, $LOG) if(defined $LOG);
#					&cgi_lib::common::message('max='.int(&max($hash_ref->{'cm_modified_epoch'},$tbp_max_enter,$CDI2ENTRY{$hash_ref->{'cdi_id'}})), $LOG) if(defined $LOG);

					my $mmax = int(&max($hash_ref->{'cm_modified_epoch'},$tbp_max_enter,$CDI2ENTRY{$hash_ref->{'cdi_id'}}));


#					push(@{$img_paths->{$imgsizekey}}, $mtime==$mmax ? &abs2rel($imgpath,$FindBin::Bin).'?'.$mtime : $inprep);
					push(@{$img_paths->{$imgsizekey}}, &abs2rel($imgpath,$FindBin::Bin).'?'.$mtime);
				}else{
					push(@{$img_paths->{$imgsizekey}}, $inprep);
				}
			}
		}
		my $primitive = $hash_ref->{'cm_primitive'} ? JSON::XS::true : JSON::XS::false;
		my $density = $hash_ref->{'cm_density'} - 0;
		my $density_icon;
		my $icon_dir = &catdir('css','16x16');
		if($primitive){
			$density_icon = &catfile($icon_dir,'primitive.png');
		}elsif($density<=0.00){
			$density_icon = &catfile($icon_dir,'route_parts.png');
		}elsif($density<=0.05){
			$density_icon = &catfile($icon_dir,'005.png');
		}elsif($density<=0.15){
			$density_icon = &catfile($icon_dir,'015.png');
		}elsif($density<=0.25){
			$density_icon = &catfile($icon_dir,'025.png');
		}elsif($density<=0.35){
			$density_icon = &catfile($icon_dir,'035.png');
		}elsif($density<=0.45){
			$density_icon = &catfile($icon_dir,'045.png');
		}elsif($density<=0.5){
			$density_icon = &catfile($icon_dir,'050.png');
		}elsif($density<=0.55){
			$density_icon = &catfile($icon_dir,'055.png');
		}elsif($density<=0.65){
			$density_icon = &catfile($icon_dir,'065.png');
		}elsif($density<=0.85){
			$density_icon = &catfile($icon_dir,'085.png');
		}elsif($density<=0.95){
			$density_icon = &catfile($icon_dir,'095.png');
		}elsif($density<=0.99){
			$density_icon = &catfile($icon_dir,'099.png');
		}else{
			$density_icon = &catfile($icon_dir,'100.png');
		}

		my $HAHS = {
			cdi_id => $cdi_name,
			cdi_name => $hash_ref->{'cd_name'},
			cdi_synonym => exists $hash_ref->{'cd_syn'} && defined $hash_ref->{'cd_syn'} && length $hash_ref->{'cd_syn'} ? [split(/;/,$hash_ref->{'cd_syn'})] : undef,
			cdi_definition => $hash_ref->{'cd_def'},
			bgcolor => $hash_ref->{'seg_thum_bgcolor'},
			primitive => $primitive,
			density => $density,
			density_icon => $density_icon,
			volume => $hash_ref->{'cm_volume'} - 0,
			xmin => $hash_ref->{'cm_xmin'} - 0,
			xmax => $hash_ref->{'cm_xmax'} - 0,
			ymin => $hash_ref->{'cm_ymin'} - 0,
			ymax => $hash_ref->{'cm_ymax'} - 0,
			zmin => $hash_ref->{'cm_zmin'} - 0,
			zmax => $hash_ref->{'cm_zmax'} - 0,
			img_paths => $img_paths,
			modified => $hash_ref->{'cm_modified_epoch'} - 0,
		};
		push(@{$IMAGES->{'datas'}}, $HAHS);
	}
	$sth->finish;
#	$IMAGES->{'ci_id'}=$ci_id-0;
#	$IMAGES->{'cb_id'}=$cb_id-0;
#	$IMAGES->{'md_id'}=$md_id-0;
#	$IMAGES->{'mv_id'}=$mv_id-0;
	$IMAGES->{'total'} = scalar @{$IMAGES->{'datas'}};
	$IMAGES->{'success'} = JSON::XS::true;
}

if(
	exists $FORM{'segment'} && defined $FORM{'segment'} &&
	exists $FORM{'range'} && defined $FORM{'range'} &&
	exists $FORM{'volume'} && defined $FORM{'volume'}
){
	my @bind_values;
	my $sql = qq|select *,EXTRACT(EPOCH FROM cmm.cm_modified) as cm_modified_epoch from concept_art_map_modified as cmm,concept_data as cd,concept_segment as cs where cmm.ci_id=cd.ci_id and cmm.cb_id=cd.cb_id and cmm.cdi_id=cd.cdi_id and cd.seg_id=cs.seg_id and|;
	if($FORM{'segment'} eq 'all'){
		$sql .= qq||;
	}else{
		$sql .= qq| cs.csg_id in (select csg_id from concept_segment_group where csg_delcause is null and csg_name=?) and|;
		push(@bind_values, $FORM{'segment'});
	}
	$sql .= qq| cm_delcause is null and cmm.md_id=$md_id and cmm.mv_id=$mv_id and cmm.crl_id=$crl_id|;

	$sql .= sprintf(qq| and cmm.cdi_id in (%s)|,join(',',keys(%USE_CDI_ID))) if(scalar keys(%USE_CDI_ID));


	my $cszr_id = $SEGMENT_ZRANGE_ABBR2ID{$FORM{'range'}};
	$sql .= qq| and cszr_id=$cszr_id| if(defined $cszr_id);
	my $csv_id = $SEGMENT_VALUME_ABBR2ID{$FORM{'volume'}};
	$sql .= qq| and csv_id=$csv_id| if(defined $csv_id);

	if(exists $FORM{'representation_type'} && defined $FORM{'representation_type'}){
		my $representation_type = &cgi_lib::common::decodeJSON($FORM{'representation_type'});
		if(defined $representation_type && ref $representation_type eq 'HASH'){
			$representation_type = undef if(
				exists $representation_type->{'element'} && defined $representation_type->{'element'} && $representation_type->{'element'} &&
				exists $representation_type->{'complete_compound'} && defined $representation_type->{'complete_compound'} && $representation_type->{'complete_compound'} &&
				exists $representation_type->{'incomplete_compound'} && defined $representation_type->{'incomplete_compound'} && $representation_type->{'incomplete_compound'}
			);
		}
		if(defined $representation_type && ref $representation_type eq 'HASH'){
			$representation_type = undef if(
				exists $representation_type->{'element'} && defined $representation_type->{'element'} && !$representation_type->{'element'} &&
				exists $representation_type->{'complete_compound'} && defined $representation_type->{'complete_compound'} && !$representation_type->{'complete_compound'} &&
				exists $representation_type->{'incomplete_compound'} && defined $representation_type->{'incomplete_compound'} && !$representation_type->{'incomplete_compound'}
			);
		}
		if(defined $representation_type && ref $representation_type eq 'HASH'){
			my $representation_type_where = [];
			push(@$representation_type_where, 'cm_primitive')                                           if(exists $representation_type->{'element'}             && defined $representation_type->{'element'}             && $representation_type->{'element'});
			push(@$representation_type_where, '(cm_density=1 and cm_primitive=false)')                  if(exists $representation_type->{'complete_compound'}   && defined $representation_type->{'complete_compound'}   && $representation_type->{'complete_compound'});
#			push(@$representation_type_where, '(cm_density>0 and cm_density<1 and cm_primitive=false)') if(exists $representation_type->{'incomplete_compound'} && defined $representation_type->{'incomplete_compound'} && $representation_type->{'incomplete_compound'});
			push(@$representation_type_where, '(cm_density<1 and cm_primitive=false)') if(exists $representation_type->{'incomplete_compound'} && defined $representation_type->{'incomplete_compound'} && $representation_type->{'incomplete_compound'});
			if(scalar @$representation_type_where){
				$sql .= ' AND ('.join(' OR ', @$representation_type_where).')';
			}
		}
	}

#	$sql .= qq| limit 3|;# if(defined $csv_id);
	$sql .= qq| order by cm_volume desc|;# if(defined $csv_id);

	&cgi_lib::common::message('$sql='.$sql, $LOG) if(defined $LOG);

	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	if(@bind_values){
		$sth->execute(@bind_values) or die $dbh->errstr;
	}else{
		$sth->execute() or die $dbh->errstr;
	}
	&setContents($sth);
	undef $sth;

}
elsif(exists $FORM{'cdi_id'} && defined $FORM{'cdi_id'} && exists $CDI_NAME2ID{$FORM{'cdi_id'}} && defined $CDI_NAME2ID{$FORM{'cdi_id'}}){
	my $cdi_pid = $CDI_NAME2ID{$FORM{'cdi_id'}};
	my $sth;
	my $column_number;
	my $cti_cids;

#=pod
#一階層ずつ辿る場合は、こちらのSQLを使用
	my $sql;
	if($crl_id eq '0'){
		$sql =<<SQL;
select
 *,EXTRACT(EPOCH FROM cmm.cm_modified) as cm_modified_epoch
from
 concept_art_map_modified as cmm,
 concept_data as cd,
 concept_segment as cs,
 (select ci_id,cb_id,cdi_id,cdi_pid from concept_tree group by ci_id,cb_id,cdi_id,cdi_pid) as ct
where
 cmm.ci_id=cd.ci_id and
 cmm.cb_id=cd.cb_id and
 cmm.cdi_id=cd.cdi_id and
 cd.seg_id=cs.seg_id and
 cmm.ci_id=ct.ci_id and
 cmm.cb_id=ct.cb_id and
 cmm.cdi_id=ct.cdi_id and
 cmm.md_id=$md_id and
 cmm.mv_id=$mv_id and
 cmm.ci_id=$ci_id and
 cmm.cb_id=$cb_id and
 cmm.crl_id=$crl_id and
 ct.cdi_pid=$cdi_pid
SQL
	}else{
		$sql =<<SQL;
select
 *,EXTRACT(EPOCH FROM cmm.cm_modified) as cm_modified_epoch
from
 concept_art_map_modified as cmm,
 concept_data as cd,
 concept_segment as cs,
 (select ci_id,cb_id,crl_id,cdi_id,cdi_pid from concept_tree group by ci_id,cb_id,crl_id,cdi_id,cdi_pid) as ct
where
 cmm.ci_id=cd.ci_id and
 cmm.cb_id=cd.cb_id and
 cmm.cdi_id=cd.cdi_id and
 cd.seg_id=cs.seg_id and
 cmm.ci_id=ct.ci_id and
 cmm.cb_id=ct.cb_id and
 cmm.crl_id=ct.crl_id and
 cmm.cdi_id=ct.cdi_id and
 cmm.md_id=$md_id and
 cmm.mv_id=$mv_id and
 cmm.ci_id=$ci_id and
 cmm.cb_id=$cb_id and
 cmm.crl_id=$crl_id and
 ct.cdi_pid=$cdi_pid
SQL
	}
	my %USE_CDI_ID;
	if(exists $FORM{'degenerate_same_shape_icons'} && defined $FORM{'degenerate_same_shape_icons'} && $FORM{'degenerate_same_shape_icons'} eq 'true'){
		my $sth;
		if($crl_id eq '0'){
			$sth = $dbh->prepare(qq|select cmm.cdi_id,mca_id,max(cti_depth) as cti_depth from concept_art_map_modified as cmm,(select ci_id,cb_id,cdi_id,max(cti_depth) as cti_depth from concept_tree_info group by ci_id,cb_id,cdi_id) as cti where cmm.ci_id=cti.ci_id and cmm.cb_id=cti.cb_id and cmm.cdi_id=cti.cdi_id and cmm.md_id=$md_id and cmm.mv_id=$mv_id and cmm.ci_id=$ci_id and cmm.cb_id=$cb_id and cmm.cdi_id in (select cdi_id from concept_tree where ci_id=$ci_id and cb_id=$cb_id and cdi_pid=$cdi_pid group by cdi_id) group by cmm.cdi_id,mca_id order by mca_id,cti_depth desc;|) or die $dbh->errstr;
		}else{
			$sth = $dbh->prepare(qq|select cmm.cdi_id,mca_id,max(cti_depth) as cti_depth from concept_art_map_modified as cmm,(select ci_id,cb_id,crl_id,cdi_id,max(cti_depth) as cti_depth from concept_tree_info group by ci_id,cb_id,crl_id,cdi_id) as cti where cmm.ci_id=cti.ci_id and cmm.cb_id=cti.cb_id and cmm.crl_id=cti.crl_id and cmm.cdi_id=cti.cdi_id and cmm.md_id=$md_id and cmm.mv_id=$mv_id and cmm.ci_id=$ci_id and cmm.cb_id=$cb_id and cmm.crl_id=$crl_id and cmm.cdi_id in (select cdi_id from concept_tree where ci_id=$ci_id and cb_id=$cb_id and crl_id=$crl_id and cdi_pid=$cdi_pid group by cdi_id) group by cmm.cdi_id,mca_id order by mca_id,cti_depth desc;|) or die $dbh->errstr;
		}
		$sth->execute() or die $dbh->errstr;
		my %USE_MCA_ID;
		while(my $hash_ref = $sth->fetchrow_hashref){
			next if(exists $USE_MCA_ID{$hash_ref->{'mca_id'}});
			$USE_MCA_ID{$hash_ref->{'mca_id'}} = undef;
			$USE_CDI_ID{$hash_ref->{'cdi_id'}} = undef;
		}
		$sth->finish;
		undef $sth;
		undef %USE_MCA_ID;
	}

#=cut
=pod
#全子孫を表示する場合は、こちらのSQLを使用する
	$sth = $dbh->prepare(qq|select cti_cids from concept_tree_info where ci_id=$ci_id and cb_id=$cb_id and cdi_id=$cdi_pid|) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$column_number = 0;
	$sth->bind_col(++$column_number, \$cti_cids, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;
	$cti_cids = &cgi_lib::common::decodeJSON($cti_cids) if(defined $cti_cids);
	undef $cti_cids unless(defined $cti_cids && ref $cti_cids eq 'ARRAY' && scalar @$cti_cids);

	my $sql =<<SQL;
select
 *,EXTRACT(EPOCH FROM cmm.cm_modified) as cm_modified_epoch
from
 concept_art_map_modified as cmm,
 concept_data as cd,
 concept_segment as cs
where
 cmm.ci_id=cd.ci_id and
 cmm.cb_id=cd.cb_id and
 cmm.cdi_id=cd.cdi_id and
 cd.seg_id=cs.seg_id
SQL
=cut



	$sql .= sprintf(qq| and cmm.cdi_id in (%s)|,join(',',sort {$a<=>$b} @$cti_cids)) if(defined $cti_cids);
	$sql .= sprintf(qq| and cmm.cdi_id in (%s)|,join(',',sort {$a<=>$b} keys(%USE_CDI_ID))) if(scalar keys(%USE_CDI_ID));
	$sql .= qq| order by cm_volume desc|;

	&cgi_lib::common::message('$sql='.$sql, $LOG) if(defined $LOG);

	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	&setContents($sth);
	undef $sth;
}
elsif(exists $FORM{'segment'} && defined $FORM{'segment'}){
	my $counts;
	my $sth;

	my $onlyTA;
	my $where = '';
	if(exists $FORM{'representation_type'} && defined $FORM{'representation_type'}){
		my $representation_type = &cgi_lib::common::decodeJSON($FORM{'representation_type'});
#&cgi_lib::common::message($representation_type,$LOG);
		if(defined $representation_type && ref $representation_type eq 'HASH'){
			$onlyTA = 1 if(exists $representation_type->{'only_taid'} && defined $representation_type->{'only_taid'} && $representation_type->{'only_taid'});
		}
		if(defined $representation_type && ref $representation_type eq 'HASH'){
			$representation_type = undef if(
				exists $representation_type->{'element'} && defined $representation_type->{'element'} && $representation_type->{'element'} &&
				exists $representation_type->{'complete_compound'} && defined $representation_type->{'complete_compound'} && $representation_type->{'complete_compound'} &&
				exists $representation_type->{'incomplete_compound'} && defined $representation_type->{'incomplete_compound'} && $representation_type->{'incomplete_compound'}
			);
		}
		if(defined $representation_type && ref $representation_type eq 'HASH'){
			$representation_type = undef if(
				exists $representation_type->{'element'} && defined $representation_type->{'element'} && !$representation_type->{'element'} &&
				exists $representation_type->{'complete_compound'} && defined $representation_type->{'complete_compound'} && !$representation_type->{'complete_compound'} &&
				exists $representation_type->{'incomplete_compound'} && defined $representation_type->{'incomplete_compound'} && !$representation_type->{'incomplete_compound'}
			);
		}
#&cgi_lib::common::message($representation_type,$LOG);
		if(defined $representation_type && ref $representation_type eq 'HASH'){
			my $representation_type_where = [];
#			push(@$representation_type_where, 'cm_primitive='.($representation_type->{'element'}?'true':'false')) if(exists $representation_type->{'element'} && defined $representation_type->{'element'});
#			push(@$representation_type_where, '(cm_density=1 and cm_primitive=false)') if(exists $representation_type->{'complete_compound'} && defined $representation_type->{'complete_compound'} && $representation_type->{'complete_compound'});
#			push(@$representation_type_where, '(cm_density>0 and cm_density<1)') if(exists $representation_type->{'incomplete_compound'} && defined $representation_type->{'incomplete_compound'} && $representation_type->{'incomplete_compound'});

			push(@$representation_type_where, 'cm_primitive')                                           if(exists $representation_type->{'element'}             && defined $representation_type->{'element'}             && $representation_type->{'element'});
			push(@$representation_type_where, '(cm_density=1 and cm_primitive=false)')                  if(exists $representation_type->{'complete_compound'}   && defined $representation_type->{'complete_compound'}   && $representation_type->{'complete_compound'});
#			push(@$representation_type_where, '(cm_density>0 and cm_density<1 and cm_primitive=false)') if(exists $representation_type->{'incomplete_compound'} && defined $representation_type->{'incomplete_compound'} && $representation_type->{'incomplete_compound'});
			push(@$representation_type_where, '(cm_density<1 and cm_primitive=false)') if(exists $representation_type->{'incomplete_compound'} && defined $representation_type->{'incomplete_compound'} && $representation_type->{'incomplete_compound'});

&cgi_lib::common::message($representation_type_where,$LOG);
			if(scalar @$representation_type_where){
				$where = ' AND ('.join(' OR ', @$representation_type_where).')';
&cgi_lib::common::message($where,$LOG);
			}
		}
	}

	if($FORM{'segment'} eq 'all'){
		$sth = $dbh->prepare(qq|select cszr_id,csv_id,count(cdi_id) from concept_art_map_modified where cm_delcause is null and md_id=$md_id and mv_id=$mv_id and crl_id=$crl_id $where group by cszr_id,csv_id|) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
	}
	elsif(length $FORM{'segment'}){
		$sth = $dbh->prepare(qq|select cmm.cszr_id,cmm.csv_id,count(cmm.cdi_id) from concept_art_map_modified as cmm,concept_data as cd,concept_segment as cs where cmm.cm_delcause is null and cmm.md_id=$md_id and cmm.mv_id=$mv_id and cmm.crl_id=$crl_id and cmm.ci_id=cd.ci_id and cmm.cb_id=cd.cb_id and cmm.cdi_id=cd.cdi_id and cs.seg_id=cd.seg_id  and cs.csg_id in (select csg_id from concept_segment_group where csg_delcause is null and csg_name=?) $where group by cmm.cszr_id,cmm.csv_id|) or die $dbh->errstr;
		$sth->execute($FORM{'segment'}) or die $dbh->errstr;
	}
	if(defined $sth){
		my $column_number = 0;
		my $cszr_id;
		my $csv_id;
		my $count;
		$sth->bind_col(++$column_number, \$cszr_id, undef);
		$sth->bind_col(++$column_number, \$csv_id, undef);
		$sth->bind_col(++$column_number, \$count, undef);
		while($sth->fetch){
			next unless(exists $SEGMENT_ZRANGE_ID2ABBR{$cszr_id});
			next unless(exists $SEGMENT_VALUME_ID2ABBR{$csv_id});
			$counts = $counts || {};
			$counts->{$SEGMENT_ZRANGE_ID2ABBR{$cszr_id}}->{$SEGMENT_VALUME_ID2ABBR{$csv_id}} = $count - 0;
		}
		$sth->finish;
		undef $sth;
	}

	if(defined $counts && ref $counts eq 'HASH'){
		my $any_abbr = 'ANY';
		foreach my $cszr_abbr (keys(%$counts)){
			my $count = 0;
			foreach my $csv_abbr (keys(%{$counts->{$cszr_abbr}})){
				$count += $counts->{$cszr_abbr}->{$csv_abbr};
			}
			$counts->{$cszr_abbr}->{$any_abbr} = $count;
		}
		$counts->{$any_abbr} = {};
		foreach my $cszr_abbr (keys(%$counts)){
			next if($cszr_abbr eq $any_abbr);
			foreach my $csv_abbr (keys(%{$counts->{$cszr_abbr}})){
				$counts->{$any_abbr}->{$csv_abbr} = 0 unless(defined $counts->{$any_abbr}->{$csv_abbr});
				$counts->{$any_abbr}->{$csv_abbr} += $counts->{$cszr_abbr}->{$csv_abbr};
			}
		}

#		$IMAGES->{'ci_id'}=$ci_id-0;
#		$IMAGES->{'cb_id'}=$cb_id-0;
#		$IMAGES->{'md_id'}=$md_id-0;
#		$IMAGES->{'mv_id'}=$mv_id-0;
		$IMAGES->{'counts'} = $counts;
		$IMAGES->{'success'} = JSON::XS::true;
	}
}


my $json = &cgi_lib::common::printContentJSON($IMAGES,\%FORM);

if(defined $LOG){
	print $LOG __LINE__,":",$json,"\n";
	close($LOG);
}
exit;
