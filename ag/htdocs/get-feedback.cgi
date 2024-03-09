#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use JSON::XS;
use DBI;
use DBD::Pg;
use Image::Info qw(image_info dim);
use Image::Magick;
use Storable;

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
	print LOG "\$FORM{$key}=[",$FORM{$key},"]\n";
}
foreach my $key (sort keys(%COOKIE)){
	print LOG "\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
}
#foreach my $key (sort keys(%ENV)){
#	print LOG "ENV{$key}=[",$ENV{$key},"]\n";
#}

$FORM{lng} = $COOKIE{"ag_annotation.locale"} if(!exists($FORM{lng}) && exists($COOKIE{"ag_annotation.locale"})); #とりあえず
$FORM{lng} = "en" if(!exists($FORM{lng}));
$FORM{position} = "front" if(!exists($FORM{position}));
$FORM{t_type} = 1 if(!exists($FORM{t_type}));

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);

#my $bp3d_table = &getBP3DTablename($FORM{version});


print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $FEEDBACK = {
	"feedback"   => [],
	"totalCount" => 0
};

#my $json = to_json($FEEDBACK);
#$json =~ s/"(true|false)"/$1/mg;
#print $json;
#print LOG $json,"\n";
#close(LOG);
#exit;

my $sql;
my $sth;
my $column_number = 0;

#=debug
my $t_pid;
my $t_id;
my $f_id;
my $f_pid;

my %TREE = ();
my %TREE_PATH = ();
my %TREE_NAME = ();
my %TREE_DETAIL = ();
#my $sql = qq|select t_id,t_pid from tree where tree.t_delcause is null|;
#my @LIST1 = &ExecuteSQL($sql);
#while(scalar @LIST1 > 0){
#	my($t_id,$t_pid) = split(/\t/,shift @LIST1);
#	$TREE{$t_id} = {};
#	$TREE{$t_id}->{t_pid}  = $t_pid if(defined $t_pid && $t_pid ne "");
#}
#undef @LIST1;

sub setTreeHash {
	my $cache_path = qq|cache_fma|;
	unless(-e $cache_path){
		mkdir $cache_path;
		chmod 0777,$cache_path;
	}
	if(exists($FORM{version})){
		$cache_path .= qq|/$FORM{version}|;
		unless(-e $cache_path){
			mkdir $cache_path;
			chmod 0777,$cache_path;
		}
	}
	$cache_path .= qq|/feedback|;
	unless(-e $cache_path){
		mkdir $cache_path;
		chmod 0777,$cache_path;
	}
	$cache_path .= qq|/$FORM{lng}|;
	unless(-e $cache_path){
		mkdir $cache_path;
		chmod 0777,$cache_path;
	}

	my $cache_file = qq|$cache_path/tree_storable.store|;
	my $cache_lock = qq|$cache_path/tree_storable.lock|;
	if(!-e $cache_file && !mkdir($cache_lock)){
		exit if(!exists($ENV{'REQUEST_METHOD'}));
		my $wait = 30;
		while($wait){
			if(-e $cache_lock){
				$wait--;
				sleep(1);
				next;
			}
			last;
		}
	}
	if(-e $cache_file && -s $cache_file){
		my $href = retrieve($cache_file);
		%TREE = %$href;
	}else{
		my $bp3d_table = &getBP3DTablename($FORM{version});
		my $sql_tree  = qq|select |;
		$sql_tree .= qq| tree.f_id|;
		$sql_tree .= qq|,tree.f_pid|;
		$sql_tree .= qq|,tree.t_order|;
		$sql_tree .= qq|,tree.t_type|;
		if($FORM{lng} eq "ja"){
			$sql_tree .= qq|,COALESCE(bp3d.b_name_j,bp3d.b_name_e)|;
		}else{
			$sql_tree .= qq|,bp3d.b_name_e|;
		}
		$sql_tree .= qq| from tree|;
		$sql_tree .= qq| left join (select b_id,b_name_j,b_name_e,b_delcause from $bp3d_table) as bp3d on tree.f_id = bp3d.b_id|;
		$sql_tree .= qq| where tree.t_type=1 and tree.t_delcause is null|;
		$sql_tree .= qq| and bp3d.b_delcause is null|;
		$sql_tree .= qq| order by tree.t_type,tree.t_order|;
		print LOG __LINE__,":sql_tree=[",$sql_tree,"]\n";
		my $sth_tree = $dbh->prepare($sql_tree);
		my($t_id,$t_pid,$t_order,$t_type,$f_name,$f_detail);
		$sth_tree->execute();
		if($sth_tree->rows>0){
			my $column_number = 0;
			$sth_tree->bind_col(++$column_number, \$f_id, undef);
			$sth_tree->bind_col(++$column_number, \$f_pid, undef);
			$sth_tree->bind_col(++$column_number, \$t_order, undef);
			$sth_tree->bind_col(++$column_number, \$t_type, undef);
			$sth_tree->bind_col(++$column_number, \$f_name, undef);
			while($sth_tree->fetch){
				my $tree = {};
				$tree->{f_id}     = $f_id     if(defined $f_id);
				$tree->{f_pid}    = $f_pid    if(defined $f_pid);
				$tree->{t_order}  = $t_order  if(defined $t_order);
				$tree->{t_type}   = $t_type   if(defined $t_type);
				$tree->{f_name}   = $f_name   if(defined $f_name);
				push(@{$TREE{$f_id}},$tree);
			}
		}
		$sth_tree->finish;
		undef $sth_tree;
		undef $sql_tree;

		store \%TREE, $cache_file;
		rmdir($cache_lock)
	}
}


my %Q_TREE = ();
my %Q_LOADID = ();

if(!exists($FORM{c_pid}) && exists($FORM{query})){
	my $c_id;
	my $c_pid;
	my $operator = &get_ludia_operator();
	my @bind_values = ();
	my $query = &spaceEncode($FORM{query});

	$sql = qq|select c_id,c_pid from comment where comment.c_delcause is null|;
	$sth = $dbh->prepare($sql);
	$sth->execute();
	$column_number = 0;
	$sth->bind_col(++$column_number, \$c_id, undef);
	$sth->bind_col(++$column_number, \$c_pid, undef);
	while($sth->fetch){
		next unless(defined $c_id);
		$Q_TREE{$c_id} = {
			c_id  => $c_id
		};
		$Q_TREE{$c_id}->{c_pid} = $c_pid if(defined $c_pid);
	}
	$sth->finish;
	undef $sth;
	undef $sql;

#CREATE INDEX idx_comment_ludia on comment USING fulltexta ((ARRAY[c_openid,c_name,c_title,c_comment]));

	$sql = qq|select c_id,c_pid from comment where comment.c_delcause is null|;
	$sql .= qq| and (|;
#	$sql .= qq|c_openid  $operator ? or |; push(@bind_values,$FORM{query});
#	$sql .= qq|c_name    $operator ? or |; push(@bind_values,$FORM{query});
#	$sql .= qq|c_title   $operator ? or |; push(@bind_values,$FORM{query});
#	$sql .= qq|c_comment $operator ?|;     push(@bind_values,$FORM{query});
	$sql .= qq|(ARRAY[c_openid,c_name,c_title,c_comment] $operator ?)|; push(@bind_values,$query);
	$sql .= qq|)|;
	$sth = $dbh->prepare($sql);
	$sth->execute(@bind_values);
	$column_number = 0;
	$sth->bind_col(++$column_number, \$c_id, undef);
	$sth->bind_col(++$column_number, \$c_pid, undef);
	while($sth->fetch){
		next unless(defined $c_id);
		next unless(exists($Q_TREE{$c_id}));
		my $temp_pid = $c_id;
		while(defined $temp_pid){
			unless(exists($Q_TREE{$temp_pid})){
				undef $temp_pid;
				last;
			}
			if(exists($Q_TREE{$temp_pid}->{c_pid})){
				$temp_pid = $Q_TREE{$temp_pid}->{c_pid};
			}else{
				last;
			}
		}
		if(defined $temp_pid){
			$Q_LOADID{$temp_pid} = {
				c_id  => $c_id
			};
			$Q_LOADID{$temp_pid}->{c_pid} = $c_pid if(defined $c_pid);
		}
	}
	$sth->finish;
	undef $sth;
	undef $sql;
}


my $f_id;
my $c_id;
my $c_pid;
my $ct_id;
my $c_url;
my $c_openid;
my $c_name;
my $c_email;
my $c_title;
my $c_comment;
my $c_image;
my $c_entry;
my $f_name;
my $f_detail;
my $ct_name;
my $cs_id;
my $tgi_version;
my $t_id;
my $t_type;
my $t_order;
my $f_detail;
my %HASH = ();

my $sql_tree  = qq|select |;
$sql_tree .= qq| tree.t_id|;
$sql_tree .= qq|,tree.t_pid|;
$sql_tree .= qq|,tree.t_order|;
$sql_tree .= qq|,tree.t_type|;
$sql_tree .= qq| from tree|;
$sql_tree .= qq| where tree.t_delcause is null and tree.f_id=?|;
$sql_tree .= qq| order by tree.t_type,tree.t_id|;
my $sth_tree = $dbh->prepare($sql_tree);


my $sqlb = qq|select fma.f_id,|;
if($FORM{lng} eq "ja"){
	$sqlb .= qq|COALESCE(fma.f_name_j,fma.f_name_k,fma.f_name_e) as f_name|;
}else{
	$sqlb .= qq|fma.f_name_e as f_name|;
}
$sqlb .= qq| from fma|;

my $sqlc = qq|select|;
$sqlc .= qq| comment_type.ct_id|;
$sqlc .= qq|,comment_type.ct_name|;
$sqlc .= qq| from comment_type|;
$sqlc .= qq| where comment_type.ct_delcause is null|;

my $sqls = qq|select|;
$sqls .= qq| comment_status.cs_id|;
$sqls .= qq|,comment_status.cs_name|;
$sqls .= qq| from comment_status|;
$sqls .= qq| where comment_status.cs_delcause is null|;

$sql  = qq|select|;
$sql .= qq| comment.f_id|;
$sql .= qq|,comment.c_id|;
$sql .= qq|,comment.c_pid|;
$sql .= qq|,comment.ct_id|;
$sql .= qq|,comment.c_url|;
$sql .= qq|,comment.c_openid|;
$sql .= qq|,comment.c_name|;
$sql .= qq|,comment.c_email|;
$sql .= qq|,comment.c_title|;
$sql .= qq|,comment.c_comment|;
$sql .= qq|,comment.c_image|;
$sql .= qq|,EXTRACT(EPOCH FROM comment.c_entry)|;
$sql .= qq|,f.f_name|;
$sql .= qq|,c.ct_name|;
$sql .= qq|,comment.cs_id|;
$sql .= qq|,comment.tgi_version|;
$sql .= qq|,comment.t_type|;
$sql .= qq| from comment|;
$sql .= qq| left join ($sqlb) as f on comment.f_id = f.f_id|;
$sql .= qq| left join ($sqlc) as c on comment.ct_id = c.ct_id|;
#$sql .= qq| left join ($sqls) as s on comment.cs_id = s.cs_id|;



my $sql_child = $sql;
$sql_child .= qq| where comment.c_delcause is null and comment.c_pid=?|;
$sql_child .= qq| order by comment.c_entry asc|;
sub getCommentChild {
	my $c_pid = shift;

	my $ch_f_id;
	my $ch_c_id;
	my $ch_c_pid;
	my $ch_ct_id;
	my $ch_c_url;
	my $ch_c_openid;
	my $ch_c_name;
	my $ch_c_email;
	my $ch_c_title;
	my $ch_c_comment;
	my $ch_c_image;
	my $ch_c_entry;
	my $ch_f_name;
	my $ch_f_detail;
	my $ch_ct_name;
	my $ch_f_detail;
	my $ch_cs_id;
#	my $ch_cs_name;

	my %HASH = ();
	my @RTN = ();
	my $sth_child = $dbh->prepare($sql_child);
	$sth_child->execute($c_pid);

	$column_number = 0;
	$sth_child->bind_col(++$column_number, \$ch_f_id, undef);
	$sth_child->bind_col(++$column_number, \$ch_c_id, undef);
	$sth_child->bind_col(++$column_number, \$ch_c_pid, undef);
	$sth_child->bind_col(++$column_number, \$ch_ct_id, undef);
	$sth_child->bind_col(++$column_number, \$ch_c_url, undef);
	$sth_child->bind_col(++$column_number, \$ch_c_openid, undef);
	$sth_child->bind_col(++$column_number, \$ch_c_name, undef);
	$sth_child->bind_col(++$column_number, \$ch_c_email, undef);
	$sth_child->bind_col(++$column_number, \$ch_c_title, undef);
	$sth_child->bind_col(++$column_number, \$ch_c_comment, undef);
	$sth_child->bind_col(++$column_number, \$ch_c_image, { pg_type => DBD::Pg::PG_BYTEA });
	$sth_child->bind_col(++$column_number, \$ch_c_entry, undef);
	$sth_child->bind_col(++$column_number, \$ch_f_name, undef);
	$sth_child->bind_col(++$column_number, \$ch_ct_name, undef);
	$sth_child->bind_col(++$column_number, \$ch_cs_id, undef);
#	$sth_child->bind_col(++$column_number, \$ch_cs_name, undef);

	while($sth_child->fetch){

		$ch_c_comment =~ s/\n/<br>/g if(defined $ch_c_comment);

		my $image_info = image_info(\$ch_c_image) if(defined $ch_c_image);
		if(defined $image_info){
			my @blob = ($ch_c_image);
			my $im = Image::Magick->new(magick=>$image_info->{file_ext});
			$im->BlobToImage(@blob);

			$ch_c_image = "comment_images/$ch_f_id";
			mkdir($ch_c_image) if(!-e $ch_c_image);
			chmod 0777,$ch_c_image;
			$ch_c_image .= "/$c_id.".$image_info->{file_ext};
			$im->Write($ch_c_image);
			chmod 0666,$ch_c_image;
			undef $im;
			undef @blob;
		}
		undef $image_info;

		my $c_fma_image;
		if(exists($FORM{version})){
print LOG __LINE__,"\$FORM{version}=[$FORM{version}]\n";
			&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
			$c_fma_image = &getImagePath($ch_f_id,undef,$FORM{version});
		}
		if(defined $c_fma_image && -e $c_fma_image){
			my $c_fma_image_modified = (stat($c_fma_image))[9];
			my $f_image = "comment_images/$ch_f_id.png";
			if(-e $f_image){
				my($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,$atime,$mtime,$ctime,$blksize,$blocks) = stat($f_image);
				unlink $f_image if($mtime<$c_fma_image_modified);
			}
			if(!-e $f_image){
				my $im = Image::Magick->new;
				$im->Read($c_fma_image);
				my $geometry = "32x32";
				$im->Resize(geometry=>$geometry,blur=>0.7);
				$im->Write($f_image);
				undef $im;
			}
			$c_fma_image = $f_image . '?' . $c_fma_image_modified;
		}else{
			$c_fma_image = "icon/inprep.png";
		}

		my $HASH = {
			f_id        => $ch_f_id,
			c_id        => $ch_c_id,
			c_pid       => $ch_c_pid,
			ct_id       => $ch_ct_id,
			c_url       => $ch_c_url,
			c_openid    => $ch_c_openid,
			c_name      => $ch_c_name,
			c_email     => $ch_c_email,
			c_title     => $ch_c_title,
			c_comment   => $ch_c_comment,
			c_image     => $ch_c_image,
			c_entry     => $ch_c_entry,
			c_fma_image => $c_fma_image,
			f_name      => $ch_f_name,
			ct_name     => $ch_ct_name,
			cs_id       => $ch_cs_id,
#			cs_name     => $ch_cs_name
		};
		foreach my $key (keys(%$HASH)){
			print LOG __LINE__,":[$key][",ref $HASH->{$key},"][",$HASH->{$key},"]\n";
			utf8::decode($HASH->{$key}) if(defined $HASH->{$key});
		}

		push(@RTN,$HASH);
	}
	$sth_child->finish;
	undef $sth_child;

	for(my $i=0;$i<scalar @RTN;$i++){
		$RTN[$i]->{c_child} = &getCommentChild($RTN[$i]->{c_id});
	}

	return wantarray ? @RTN : \@RTN;
}

my $sql_entry;
$sql_entry = qq|select|;
$sql_entry .= qq| comment.c_id|;
$sql_entry .= qq|,EXTRACT(EPOCH FROM comment.c_entry)|;
$sql_entry .= qq| from comment|;
$sql_entry .= qq| where comment.c_delcause is null and comment.c_pid=?|;
$sql_entry .= qq| order by comment.c_entry desc limit 1|;
my $sth_entry = $dbh->prepare($sql_entry);
sub getCommentChildEntry {
	my $c_pid = shift;

	my $ch_c_id;
	my $ch_c_entry;

	my %HASH = ();
	my @RTN = ();
	$sth_entry->execute($c_pid);

	$column_number = 0;
	$sth_entry->bind_col(++$column_number, \$ch_c_id, undef);
	$sth_entry->bind_col(++$column_number, \$ch_c_entry, undef);

	while($sth_entry->fetch){
		my $HASH = {
			c_id        => $ch_c_id,
			c_entry     => $ch_c_entry
		};
		push(@RTN,$HASH);
	}
	$sth_entry->finish;

	for(my $i=0;$i<scalar @RTN;$i++){
		push(@RTN,&getCommentChildEntry($RTN[$i]->{c_id}));
	}
	return wantarray ? @RTN : \@RTN;
}


my @bind_values = ();
my $where;
my $sql_parent = $sql;
if(exists($FORM{c_pid})){
	$where = qq| where comment.c_delcause is null and comment.c_pid = ?|;
	$sql_parent .= $where;
	$sql_parent .= qq| order by comment.c_entry asc|;
}else{
	$where = qq| where comment.c_delcause is null and comment.c_pid is null|;

	if(exists($FORM{cs_id}) && $FORM{cs_id} ne "0"){
		$where .= qq| and comment.cs_id=?|;
		push(@bind_values,$FORM{cs_id});
	}

	if(exists($FORM{query})){
		my @temp_arr = ();
		foreach my $loadid (keys(%Q_LOADID)){
			push(@temp_arr,qq|c_id=?|);
			push(@bind_values,$loadid);
		}
		$where .= " and (" . join(" or ",@temp_arr) . ")" if(scalar @temp_arr > 0);
	}

	$sql_parent .= $where;
	if($FORM{sort} ne 'c_modified'){
		$sql_parent .= qq| order by $FORM{sort} $FORM{dir}|;
		$sql_parent .= qq|,| if(exists($FORM{sort}));
		$sql_parent .= qq| comment.c_entry desc|;
	}else{
	}

#	if($FORM{sort} eq 'cs_name'

}
$sql_parent .= qq| limit $FORM{limit}| if(exists($FORM{limit}));
$sql_parent .= qq| offset $FORM{start}| if(exists($FORM{start}));

#print __LINE__,":sql_parent=[$sql_parent]\n";
print LOG __LINE__,":sql_parent=[$sql_parent]\n";
my $sth_parent = $dbh->prepare($sql_parent);
if(exists($FORM{c_pid})){
	$sth_parent->execute($FORM{c_pid});
}else{
	$sth_parent->execute(@bind_values);
}

my $sth_count = $dbh->prepare(qq|select c_id from comment $where|);
if(exists($FORM{c_pid})){
	$sth_count->execute($FORM{c_pid});
}else{
	$sth_count->execute(@bind_values);
}
$FEEDBACK->{totalCount} = $sth_count->rows;
undef $sth_count;

$column_number = 0;
$sth_parent->bind_col(++$column_number, \$f_id, undef);
$sth_parent->bind_col(++$column_number, \$c_id, undef);
$sth_parent->bind_col(++$column_number, \$c_pid, undef);
$sth_parent->bind_col(++$column_number, \$ct_id, undef);
$sth_parent->bind_col(++$column_number, \$c_url, undef);
$sth_parent->bind_col(++$column_number, \$c_openid, undef);
$sth_parent->bind_col(++$column_number, \$c_name, undef);
$sth_parent->bind_col(++$column_number, \$c_email, undef);
$sth_parent->bind_col(++$column_number, \$c_title, undef);
$sth_parent->bind_col(++$column_number, \$c_comment, undef);
$sth_parent->bind_col(++$column_number, \$c_image, { pg_type => DBD::Pg::PG_BYTEA });
$sth_parent->bind_col(++$column_number, \$c_entry, undef);
$sth_parent->bind_col(++$column_number, \$f_name, undef);
$sth_parent->bind_col(++$column_number, \$ct_name, undef);
$sth_parent->bind_col(++$column_number, \$cs_id, undef);
$sth_parent->bind_col(++$column_number, \$tgi_version, undef);
$sth_parent->bind_col(++$column_number, \$t_type, undef);

while($sth_parent->fetch){

#	$c_comment =~ s/\n/<br>/g if(defined $c_comment);

	my $c_image_thumb;
	my $image_info = image_info(\$c_image) if(defined $c_image);
	if(defined $image_info && exists($image_info->{file_ext})){
		my @blob = ($c_image);
		my $im = Image::Magick->new(magick=>$image_info->{file_ext});
		$im->BlobToImage(@blob);

		$c_image = "comment_images";
		mkdir($c_image) if(!-e $c_image);
		chmod 0777,$c_image;
#		$c_image .= "/$c_id.".$image_info->{file_ext};
		$c_image .= sprintf("/%06d.",$c_id) . $image_info->{file_ext};

		$im->Write($c_image);
		chmod 0666,$c_image;

		$c_image_thumb = sprintf("comment_images/%06d_120x120.",$c_id) . $image_info->{file_ext};
		$im->Resize(geometry=>"120x120",blur=>0.7);
		$im->Write($c_image_thumb);
		chmod 0666,$c_image_thumb;

		undef $im;
		undef @blob;
	}else{
		undef $c_image;
	}
	undef $image_info;


#	my $c_rowtitle = sprintf("%8s&nbsp;&nbsp;%s",$f_id,$f_name);

#	$cs_name = qq|<span class="pending">$cs_name</span>| if($cs_name eq "Pending");

	my $HASH = {
		f_id          => $f_id,
		c_id          => $c_id,
		c_pid         => $c_pid,
		ct_id         => $ct_id,
		c_url         => $c_url,
		c_openid      => $c_openid,
		c_name        => $c_name,
		c_email       => $c_email,
#		c_rowtitle    => $c_rowtitle,
		c_title       => $c_title,
		c_comment     => $c_comment,
		c_image       => $c_image,
		c_image_thumb => $c_image_thumb,
		c_entry       => $c_entry,
#		c_fma_image   => $c_fma_image,
#		f_name        => $f_name,
#		f_detail      => $f_detail,
		ct_name       => $ct_name,
		cs_id         => $cs_id,
		tgi_version   => $tgi_version
	};
	foreach my $key (keys(%$HASH)){
		utf8::decode($HASH->{$key}) if(defined $HASH->{$key});
	}

#	$HASH->{c_fmas} = ();

	if(defined $f_id){
		my @F_ID = split(/,/,$f_id);
		my $geometry = "32x32";
		$geometry = "76x76" if(scalar @F_ID == 1);
		if(defined $tgi_version){
			$FORM{version} = $tgi_version;
			&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
			&setTreeHash();
		}else{
			delete $FORM{version};
			%TREE = ();
		}
		foreach $f_id (@F_ID){

			my $FMA_HASH = {fma_id => $f_id};

			my $c_fma_image;
			if(defined $tgi_version){
				my $form = {};
				foreach my $key (keys(%FORM)){
					$form->{$key} = $FORM{$key};
				}
				$form->{version} = $tgi_version;
				&convVersionName2RendererVersion($dbh,$form,\%COOKIE);
				$c_fma_image = &getImagePath($f_id,undef,$form->{version},undef,$t_type);
				undef $form;
			}
print LOG __LINE__,":\$c_fma_image=[$c_fma_image]\n";
			if(defined $c_fma_image && -e $c_fma_image){
				my $c_fma_image_modified = (stat($c_fma_image))[9];
				my $f_image = "comment_images/$f_id\_$geometry.png";
				if(-e $f_image){
					my $mtime = (stat($f_image))[9];
					unlink $f_image if($mtime<$c_fma_image_modified);
				}
				if(!-e $f_image){
					my $im = Image::Magick->new;
					$im->Read($c_fma_image);
					$im->Resize(geometry=>$geometry,blur=>0.7);
					$im->Write($f_image);
					undef $im;
				}
				$c_fma_image = $f_image . '?' . $c_fma_image_modified;
			}else{
				$c_fma_image = "icon/inprep.png";
			}
			$FMA_HASH->{fma_image} = $c_fma_image;
			undef $c_fma_image;

			if(exists($TREE{$f_id})){
				if(!exists($TREE_PATH{$f_id}) || !exists($TREE_NAME{$f_id})){
					my $temp_pid = $f_id;
					my @p_path = ();
					my @p_name = ();
					while(exists($TREE{$temp_pid})){
						unshift @p_path,$temp_pid;
						unshift @p_name,$TREE{$temp_pid}->[0]->{f_name};
						$temp_pid = $TREE{$temp_pid}->[0]->{f_pid};
					}
					pop @p_path if(exists($TREE{$f_id}->[0]->{f_pid}) && $TREE{$f_id}->[0]->{f_pid} ne "");
					$TREE_PATH{$f_id} = join("/",@p_path);
					$TREE_NAME{$f_id} = join("/",@p_name);
				}
				push(@{$FMA_HASH->{fma_path}},$TREE_PATH{$f_id});
				push(@{$FMA_HASH->{fma_names}},$TREE_NAME{$f_id});
				$FMA_HASH->{fma_name} = $TREE{$f_id}->[0]->{f_name} if(!exists($FMA_HASH->{fma_name}));
				my $TREE_HASH = {
					t_order => $TREE{$f_id}->[0]->{t_order},
					t_type  => $TREE{$f_id}->[0]->{t_type}
				};
				push(@{$FMA_HASH->{fma_tree}},$TREE_HASH);
			}
			push(@{$HASH->{c_fmas}},$FMA_HASH);
		}
	}else{
		my $FMA_HASH = {
			fma_image => "icon/inprep.png"
		};
		push(@{$HASH->{c_fmas}},$FMA_HASH);
	}

#	my @c_child_entry = &getCommentChildEntry($c_id);
#	@c_child_entry = sort {$b->{c_entry} <=> $a->{c_entry}} @c_child_entry;
#	$HASH->{c_child_entry} = $c_child_entry[0]->{c_entry};


	push(@{$FEEDBACK->{feedback}},$HASH);

	undef $c_image_thumb;
}
$sth_parent->finish;
undef $sth_parent;


if(!exists($FORM{c_pid}) && $FORM{sort} eq 'c_modified'){
	my $len = scalar @{$FEEDBACK->{feedback}};
	for(my $i=0;$i<$len;$i++){
#		$FEEDBACK->{feedback}->[$i]->{c_child} = &getCommentChild($FEEDBACK->{feedback}->[$i]->{c_id});
		my @c_child_entry = &getCommentChildEntry($FEEDBACK->{feedback}->[$i]->{c_id});
		@c_child_entry = sort {$b->{c_entry} <=> $a->{c_entry}} @c_child_entry;
		$FEEDBACK->{feedback}->[$i]->{c_child_entry} = $c_child_entry[0]->{c_entry};
		undef @c_child_entry;
	}
	@{$FEEDBACK->{feedback}} = sort {$b->{c_child_entry} <=> $a->{c_child_entry}} @{$FEEDBACK->{feedback}};
}

#my $json = to_json($FEEDBACK);
my $json = encode_json($FEEDBACK);
$json =~ s/"(true|false)"/$1/mg;
print $json;
print LOG $json,"\n";

close(LOG);
exit;

__END__
			{name: 'f_id',        type:'string'},
			{name: 'c_id',        type:'int'},
			{name: 'c_openid',    type:'string'},
			{name: 'c_name',      type:'string'},
			{name: 'c_email',     type:'string'},
			{name: 'c_title',     type:'string'},
			{name: 'c_comment',   type:'string'},
			{name: 'c_entry',     type:'date', dateFormat:'timestamp'},
			{name: 'c_image',     type:'string'},
			{name: 'c_fma_image', type:'string'},
			{name: 'c_fma_name',  type:'string'},
			{name: 'c_reply'},
			{name: 'c_path'},
			{name: 'c_names'},
			{name: 'c_tree'}
