#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use JSON::XS;

my $COMMENT = {
	"totalCount" => 0,
	"topics" => []
};
print qq|Content-type: text/html; charset=UTF-8\n\n|;
print &JSON::XS::encode_json($COMMENT);
exit;


use DBI;
use DBD::Pg;
use Image::Info qw(image_info dim);
use Image::Magick;
use File::Path;

require "common.pl";
require "common_db.pl";
my $dbh = &get_dbh();

my %FORM = ();
&decodeForm(\%FORM);
delete $FORM{_formdata} if(exists($FORM{_formdata}));

my %COOKIE = ();
&getCookie(\%COOKIE);

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
open(LOG,">> log.txt");
print LOG "\n[$logtime]:$0\n";
foreach my $key (sort keys(%FORM)){
	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
}
foreach my $key (sort keys(%COOKIE)){
	print LOG __LINE__,":\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
}
#foreach my $key (sort keys(%ENV)){
#	print LOG "ENV{$key}=[",$ENV{$key},"]\n";
#}

$FORM{lng} = $COOKIE{"ag_annotation.locale"} if(!exists($FORM{lng}) && exists($COOKIE{"ag_annotation.locale"})); #とりあえず
$FORM{lng} = "en" if(!exists($FORM{lng}));


$FORM{start} = 0 if(!exists($FORM{start}));
$FORM{limit} = 2 if(!exists($FORM{limit}));
$FORM{'sort'} = 'entry' if(!exists($FORM{'sort'}));
$FORM{'dir'} = 'DESC'   if(!exists($FORM{'dir'}));

#$FORM{tg_id} = $COOKIE{"ag_annotation.images.tg_id"} if(!exists($FORM{tg_id}) && exists($COOKIE{"ag_annotation.images.tg_id"}));
&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);


my $lsdb_OpenID;
my $lsdb_Auth;
my $parentURL = $FORM{parent} if(exists($FORM{parent}));
my $parent_text;
if(defined $parentURL){
	($lsdb_OpenID,$lsdb_Auth) = &openidAuth($parentURL);
}


my $COMMENT = {
	"totalCount" => 0,
	"topics" => []
};

print qq|Content-type: text/html; charset=UTF-8\n\n|;

unless(exists($FORM{version})){
	$COMMENT->{success} = "false" if(exists($FORM{callback}));
#	my $json = to_json($COMMENT);
	my $json = encode_json($COMMENT);
	$json =~ s/"(true|false)"/$1/mg;
	$json = $FORM{callback}."(".$json.")" if(exists($FORM{callback}));
	print $json;
	print LOG $json,"\n";
	exit;
}

my $bp3d_table = &getBP3DTablename($FORM{version});

unless(&existsTable($bp3d_table)){
	$COMMENT->{success} = "false" if(exists($FORM{callback}));
#	my $json = to_json($COMMENT);
	my $json = encode_json($COMMENT);
	$json =~ s/"(true|false)"/$1/mg;
	$json = $FORM{callback}."(".$json.")" if(exists($FORM{callback}));
	print $json;
	print LOG $json,"\n";
	exit;
}

#if(!exists($FORM{tg_id}) || !exists($FORM{tgi_id})){
#	my $tg_id;
#	my $tgi_id;
#	my $sth_tree_group_item = $dbh->prepare(qq|select tg_id,tgi_id from tree_group_item where tgi_version=?|);
#	$sth_tree_group_item->execute($FORM{version});
#	my $column_number = 0;
#	$sth_tree_group_item->bind_col(++$column_number, \$tg_id, undef);
#	$sth_tree_group_item->bind_col(++$column_number, \$tgi_id, undef);
#	$sth_tree_group_item->fetch;
#	if(defined $tg_id && defined $tgi_id){
#		$FORM{tg_id} = $tg_id;
#		$FORM{tgi_id} = $tgi_id;
#	}
#	$sth_tree_group_item->finish;
#	undef $sth_tree_group_item;
#}
my $wt_version = qq|tg_id=$FORM{tg_id} and tgi_id=$FORM{tgi_id}|;
my $tgi_version;
my @tgi_versions;
my $sth_tree_group_item = $dbh->prepare(qq|select tgi_version from tree_group_item where tg_id=?|);
$sth_tree_group_item->execute($FORM{tg_id});
my $column_number = 0;
$sth_tree_group_item->bind_col(++$column_number, \$tgi_version, undef);
while($sth_tree_group_item->fetch){
	push(@tgi_versions,qq|comment.tgi_version='$tgi_version'|) if(defined $tgi_version);
}
$sth_tree_group_item->finish;
undef $sth_tree_group_item;
my $wt_version = "(".join(" or ",@tgi_versions).")";



my @bind_values = ();
my $sql;
$sql  = qq|select|;
$sql .= qq| comment.f_id|;
$sql .= qq|,comment.c_id|;
$sql .= qq|,comment.c_pid|;
$sql .= qq|,comment.c_openid|;
$sql .= qq|,comment.c_name|;
$sql .= qq|,comment.c_email|;
$sql .= qq|,comment.c_title|;
$sql .= qq|,comment.c_comment|;
$sql .= qq|,comment.c_image|;
$sql .= qq|,EXTRACT(EPOCH FROM comment.c_entry)|;
if($FORM{lng} eq "ja"){
	$sql .= qq|,COALESCE(f.f_name_j,f.f_name_e)|;
}else{
	$sql .= qq|,f.f_name_e|;
}
$sql .= qq|,comment.ct_id|;
$sql .= qq|,comment.cs_id|;
$sql .= qq|,comment.tgi_version|;
if($FORM{lng} eq "ja"){
	$sql .= qq|,COALESCE(tree_type.t_name_j,tree_type.t_name_e)|;
}else{
	$sql .= qq|,tree_type.t_name_e|;
}
$sql .= qq| from comment|;
$sql .= qq| left join (select f_id,f_name_j,f_name_e,f_delcause from fma) as f on comment.f_id = f.f_id|;
$sql .= qq| left join (select t_type,t_name_j,t_name_e,t_delcause from tree_type) as tree_type on comment.t_type = tree_type.t_type|;
$sql .= qq| where|;
$sql .= qq| comment.c_delcause is null and f.f_delcause is null|;
if(exists($FORM{f_id})){
	$sql .= qq| and (|;
	$sql .= qq| comment.f_id ~ ? or|; push(@bind_values,$FORM{f_id}.qq|[^0-9]|);
	$sql .= qq| comment.f_id ~ ?|;    push(@bind_values,$FORM{f_id}.qq|\$|);
	$sql .= qq|)|;
}
if(exists($FORM{c_pid})){
	$sql .= qq| and comment.c_pid = ?|; push(@bind_values,$FORM{c_pid});
}else{
	$sql .= qq| and comment.c_pid is null|;
}
$sql .= qq| and $wt_version|;
$sql .= qq| order by c_$FORM{'sort'} $FORM{'dir'} offset $FORM{start} limit $FORM{limit};|;

print LOG __LINE__,":SQL=[",$sql,"]\n";

my($f_id,$c_id,$c_pid,$c_openid,$c_name,$c_email,$c_title,$c_comment,$c_image,$c_entry,$ct_id,$cs_id,$tgi_version,$t_name);
my $sth = $dbh->prepare($sql);



my($f_name_j,$f_name_e,$f_name);
my($t_id,$t_pid,$t_order,$t_type);

if(exists($FORM{f_id}) || exists($FORM{c_pid})){
	$sth->execute(@bind_values);
}else{
	$sth->execute();
}
if($sth->rows>0){
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$f_id, undef);
	$sth->bind_col(++$column_number, \$c_id, undef);
	$sth->bind_col(++$column_number, \$c_pid, undef);
	$sth->bind_col(++$column_number, \$c_openid, undef);
	$sth->bind_col(++$column_number, \$c_name, undef);
	$sth->bind_col(++$column_number, \$c_email, undef);
	$sth->bind_col(++$column_number, \$c_title, undef);
	$sth->bind_col(++$column_number, \$c_comment, undef);
	$sth->bind_col(++$column_number, \$c_image, { pg_type => DBD::Pg::PG_BYTEA });
	$sth->bind_col(++$column_number, \$c_entry, undef);
	$sth->bind_col(++$column_number, \$f_name, undef);
	$sth->bind_col(++$column_number, \$ct_id, undef);
	$sth->bind_col(++$column_number, \$cs_id, undef);
	$sth->bind_col(++$column_number, \$tgi_version, undef);
	$sth->bind_col(++$column_number, \$t_name, undef);
	while($sth->fetch){

		my $url;
		my $url_thumb;
		my $image_info = image_info(\$c_image) if(defined $c_image);
		if(defined $image_info){
			my @blob = ($c_image);
			my $im = Image::Magick->new(magick=>$image_info->{file_ext});
			$im->BlobToImage(@blob);

			$url = "comment_images";
			mkdir($url) if(!-e $url);
			chmod 0777,$url;
			$url .= sprintf("/%06d.%s",$c_id,$image_info->{file_ext});
			$url_thumb = sprintf("comment_images/%06d_60x60.%s",$c_id,$image_info->{file_ext});
			$im->Write($url);
			chmod 0666,$url;

			$im->Resize(geometry=>"60x60",blur=>0.7);
			$im->Write($url_thumb);
			chmod 0666,$url_thumb;

			undef $im;
			undef @blob;
		}
		undef $image_info;

		my $fma_url = &getImagePath($f_id,undef,$FORM{version});
		$fma_url = "icon/inprep.png" if(!-e $fma_url);

		my $form = {};
		foreach my $key (keys(%FORM)){
			$form->{$key} = $FORM{$key};
		}
		$form->{version} = $tgi_version;
print LOG __LINE__,":\$tgi_version=[",$tgi_version,"]\n";
		&convRendererVersion2VersionName($dbh,$form);
print LOG __LINE__,":\$form->{version}=[",$form->{version},"]\n";

		my $HASH = {
			f_id      => $f_id,
			c_id      => $c_id,
			c_pid     => $c_pid,
			c_openid  => $c_openid,
			c_name    => $c_name,
			c_email   => $c_email,
			c_title   => $c_title,
			c_comment => $c_comment,
			c_entry   => $c_entry,
			c_image   => $url,
			c_image_thumb => $url_thumb,
			c_fma_image => $fma_url,
			ct_id     => $ct_id,
			cs_id     => $cs_id,
#			tgi_version => $tgi_version,
			tgi_version => $form->{version},
			t_name    => $t_name,
#			c_fma_name  => $f_name,
			c_reply   => ()
		};
		foreach my $key (keys(%$HASH)){
			utf8::decode($HASH->{$key}) if(defined $HASH->{$key});
		}

		push(@{$COMMENT->{topics}},$HASH);
		undef $url;
		undef $url_thumb;
	}
}
$sth->finish;
undef $sth;



my $totalCount;
$sql = qq|select count(f_id) from comment where comment.f_id = ? and comment.c_pid is null and comment.c_delcause is null|;
my $sth = $dbh->prepare($sql);
$sth->execute($FORM{f_id});
$sth->bind_columns(undef, \($totalCount));
$sth->fetch;
$sth->finish;
undef $sth;

$COMMENT->{totalCount} = $totalCount;

#my $json = to_json($COMMENT);
my $json = encode_json($COMMENT);
$json =~ s/"(true|false)"/$1/mg;
print $json;
print LOG $json,"\n";
close(LOG);

exit;
