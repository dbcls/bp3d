#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use JSON::XS;
use DBI;
use DBD::Pg;
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
my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = fileparse($0,@extlist);
open(LOG,">> logs/$cgi_name.$COOKIE{'ag_annotation.session'}.txt");
print LOG "\n[$logtime]:$0\n";
foreach my $key (sort keys(%FORM)){
	print LOG "\$FORM{$key}=[",$FORM{$key},"]\n";
}
foreach my $key (sort keys(%COOKIE)){
	print LOG "\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
}

$FORM{lng} = $COOKIE{"ag_annotation.locale"} if(!exists($FORM{lng}) && exists($COOKIE{"ag_annotation.locale"})); #とりあえず
$FORM{lng} = "en" if(!exists($FORM{lng}));
$FORM{position} = "rotate" if(!exists($FORM{position}));

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);

my %TREE = {};
my %VER2TREE = {};
my $sql;
my $sth;

my %TARGET_VER = ();

#全てのバージョンを取得
my %VERSION_HASH = ();
$sql = qq|select tree_group.tg_id,tg_name_j,tg_name_e,i.tgi_version from tree_group left join (select tg_id,tgi_id,tgi_version from tree_group_item) as i on i.tg_id=tree_group.tg_id order by tree_group.tg_id|;
$sth = $dbh->prepare($sql);
$sth->execute();
my $tg_id;
my $tg_name_j;
my $tg_name_e;
my $tgi_version;
my $column_number = 0;
$sth->bind_col(++$column_number, \$tg_id, undef);
$sth->bind_col(++$column_number, \$tg_name_j, undef);
$sth->bind_col(++$column_number, \$tg_name_e, undef);
$sth->bind_col(++$column_number, \$tgi_version, undef);
while($sth->fetch){
	next unless(defined $tgi_version);
#	warn __LINE__,":$tgi_version\n";
	$VERSION_HASH{$tgi_version} = {};
	$VERSION_HASH{$tgi_version}->{tg_id} = $tg_id;
	if($FORM{lng} eq "ja"){
		$VERSION_HASH{$tgi_version}->{tg_name} = (defined $tg_name_j ? $tg_name_j : $tg_name_e);
	}else{
		$VERSION_HASH{$tgi_version}->{tg_name} = $tg_name_e;
	}
	$VERSION_HASH{$tgi_version}->{table} = &getBP3DTablename($tgi_version);
}
$sth->finish;
undef $sth;



print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $WHATNEW = {
	"whatnew" => []
};

my $cache_fma_path = qq|cache_fma|;
my $app_name_path = qq|whatnew|;
sub getCachePath {
	my $version = shift;
	$version = qq|all_version| unless(defined $version);

	my $cache_path = $cache_fma_path;
	unless(-e $cache_path){
		mkdir $cache_path;
		chmod 0777,$cache_path;
	}
	$cache_path .= qq|/$version|;
	unless(-e $cache_path){
		mkdir $cache_path;
		chmod 0777,$cache_path;
	}
	$cache_path .= qq|/$app_name_path|;
	unless(-e $cache_path){
		mkdir $cache_path;
		chmod 0777,$cache_path;
	}
	$cache_path .= qq|/$FORM{lng}|;
	unless(-e $cache_path){
		mkdir $cache_path;
		chmod 0777,$cache_path;
	}
	return $cache_path;
}

my $store_lock = qq|$cache_fma_path/$app_name_path.lock|;

$SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit";
sub sigexit {
	my($date) = `date`;
	$date =~ s/\s*$//g;
	print STDERR "[$date] KILL THIS CGI!![$ENV{SCRIPT_NAME}]\n";
	rmdir $store_lock if(-e $store_lock);
	exit(1);
}

if(!mkdir($store_lock)){
	exit if(!exists($ENV{'REQUEST_METHOD'}));
	my $wait = 120;
	while($wait){
		if(-e $store_lock){
			$wait--;
			sleep(1);
			next;
		}
		next if(!mkdir($store_lock));
		last;
	}
}

#if(-e $store_file && -s $store_file){
#	my $href = retrieve($store_file);
#	%TREE = %$href;
#
#	my $href = retrieve($store2_file);
#	%VER2TREE = %$href;
#}else{
#	my($t_id,$t_pid,$f_id,$f_pid,$t_delcause,$t_type,$tgi_version,$tg_name_j,$tg_name_e);
#	my $sql = qq|select t_id,t_pid,f_id,f_pid,t_delcause,t_type,i.tgi_version from tree|;
#	$sql .= qq| left join (select tg_id,tgi_id,tgi_version from tree_group_item) as i on i.tg_id=tree.tg_id and i.tgi_id=tree.tgi_id|;
#	$sql .= qq| order by t_type,f_id|;
#	my $sth = $dbh->prepare($sql);
#	$sth->execute();
#	$sth->bind_columns(undef, \($t_id,$t_pid,$f_id,$f_pid,$t_delcause,$t_type,$tgi_version));
#	while($sth->fetch){
#		$TREE{$tgi_version} = {} unless(exists($TREE{$tgi_version}));
#		unless(exists($TREE{$tgi_version}->{$f_id})){
#			$TREE{$tgi_version}->{$f_id} = {};
#			$TREE{$tgi_version}->{$f_id}->{f_pid} = $f_pid;
#			$TREE{$tgi_version}->{$f_id}->{t_type} = $t_type;
#			$TREE{$tgi_version}->{$f_id}->{t_delcause} = $t_delcause if(defined $t_delcause && $t_delcause ne "");
#		}
#
#		$VER2TREE{$tgi_version} = {} unless(exists($VER2TREE{$tgi_version}));
#		$VER2TREE{$tgi_version}->{$f_id} = {} unless(exists($VER2TREE{$tgi_version}->{$f_id}));
#		unless(exists($VER2TREE{$tgi_version}->{$f_id}->{$t_type})){
#			$VER2TREE{$tgi_version}->{$f_id}->{$t_type} = {};
#			$VER2TREE{$tgi_version}->{$f_id}->{$t_type}->{t_id} = $t_id;
#			$VER2TREE{$tgi_version}->{$f_id}->{$t_type}->{t_pid} = $t_pid if(defined $t_pid);
#			$VER2TREE{$tgi_version}->{$f_id}->{$t_type}->{f_pid} = $f_pid if(defined $f_pid);
#			$VER2TREE{$tgi_version}->{$f_id}->{$t_type}->{t_delcause} = $t_delcause if(defined $t_delcause && $t_delcause ne "");
#		}
#	}
#
#	store \%TREE, $store_file;
#	store \%VER2TREE, $store2_file;
#	rmdir($store_lock);
#}

my $sth;

my $f_id;
my $t_id;
my $s_name;
my $name;
my $detail;
my $entry;
my $modified;
my $version;
my $state;
my $comment;
my $c_image;
my $tgi_version;
my %HASH = ();

my %FMA = ();


#最初にコメントから情報取得
my $sqlb = qq|select fma.f_id,|;
if($FORM{lng} eq "ja"){
	$sqlb .= qq|COALESCE(fma.f_name_j,fma.f_name_k,fma.f_name_e) as name|;
}else{
	$sqlb .= qq|COALESCE(fma.f_name_e,fma.f_name_j,fma.f_name_k) as name|;
}
$sqlb .= qq| from fma|;

$sql = qq|select comment.f_id,comment.c_comment,EXTRACT(EPOCH FROM comment.c_entry),f.name,comment.c_image,comment.tgi_version from comment left join ($sqlb) as f on comment.f_id = f.f_id where comment.c_entry >= (current_timestamp - interval '7 day') and comment.f_id <> '0'|;
$sql .= qq| order by comment.c_entry desc limit 10|;
print LOG __LINE__,":sql=[$sql]\n";
$sth = $dbh->prepare($sql);
$sth->execute();
#$sth->bind_columns(undef, \($t_id,$comment,$entry,$t_pid,$s_name,$name,$detail));
my $column_number = 0;
$sth->bind_col(++$column_number, \$f_id, undef);
$sth->bind_col(++$column_number, \$comment, undef);
$sth->bind_col(++$column_number, \$entry, undef);
$sth->bind_col(++$column_number, \$name, undef);
$sth->bind_col(++$column_number, \$c_image, { pg_type => DBD::Pg::PG_BYTEA });
$sth->bind_col(++$column_number, \$tgi_version, undef);

while($sth->fetch){
	next if(exists($FMA{$f_id}));

	$comment =~ s/\n/<br>/g if(defined $comment);

	utf8::decode($name) if(defined $name && !utf8::is_utf8($name));
	utf8::decode($comment) if(defined $comment && !utf8::is_utf8($comment));

	$FMA{$f_id} = {};
	$FMA{$f_id}->{id} = $f_id;
	$FMA{$f_id}->{entry} = $entry;
	$FMA{$f_id}->{name} = $name;
	$FMA{$f_id}->{detail} = $comment if(defined $comment);
	$FMA{$f_id}->{icon} = (defined $c_image?"image_add.png":"comment_add.png");
	$FMA{$f_id}->{version} = $tgi_version;
	if(defined $tgi_version){
		if(exists($VERSION_HASH{$tgi_version})){
			$FMA{$f_id}->{tg_id} = $VERSION_HASH{$tgi_version}->{tg_id};
			$FMA{$f_id}->{tg_name} = $VERSION_HASH{$tgi_version}->{tg_name};
		}
		$TARGET_VER{$tgi_version} = "";
	}
}
$sth->finish;
undef $sth;


#全てのテーブルから最終更新日を取得
my $last_modified;
my @sql_arr = ();
foreach my $tgi_version (keys(%VERSION_HASH)){
	$sql = qq|select max(b_modified) as last_modified from $VERSION_HASH{$tgi_version}->{table}|;
	push(@sql_arr,$sql);
}
$sql = qq|select max(last_modified) as last_modified from (| . join(" union ",@sql_arr) . qq|) as a|;
print LOG __LINE__,":sql=[$sql]\n";
$sth = $dbh->prepare($sql);
$sth->execute();
$sth->bind_columns(undef, \($last_modified));
$sth->fetch;
undef $sth;


my @sql_arr = ();
foreach my $tgi_version (keys(%VERSION_HASH)){
	$sql = qq|select b_id as id,|;
	if($FORM{lng} eq "ja"){
		$sql .= qq|COALESCE(b_name_j,b_name_k,b_name_e) as name|;
	}else{
		$sql .= qq|COALESCE(b_name_e,b_name_j,b_name_k) as name|;
	}
	$sql .= qq|,b_entry as entry,b_modified as modified,'$tgi_version' as version,b_state as state,b_delcause as delcause from $VERSION_HASH{$tgi_version}->{table}|;
#	$sql .= qq| where b_modified >= (timestamp '$last_modified' - interval '7 day') and b_delcause is null order by b_modified desc,b_name_e asc|;
	push(@sql_arr,$sql);
}

$sql = qq|select id,name,EXTRACT(EPOCH FROM entry),EXTRACT(EPOCH FROM modified),version,state from (| . join(" union ",@sql_arr) . qq|) as a|;
$sql .= qq| where modified >= (timestamp '$last_modified' - interval '7 day') and delcause is null and state is not null order by modified desc,name asc limit 10|;


print LOG __LINE__,":sql=[$sql]\n";

$sth = $dbh->prepare($sql);
$sth->execute();
$sth->bind_columns(undef, \($f_id,$name,$entry,$modified,$version,$state));
while($sth->fetch){
	if(exists($FMA{$f_id}) && ($FMA{$f_id}->{entry}>($modified>$entry?$modified:$entry))){
#		warn $t_id,"\n";
		next ;
	}
	delete $FMA{$f_id} if(exists($FMA{$f_id}));

	utf8::decode($name) if(defined $name && !utf8::is_utf8($name));

	$FMA{$f_id} = {};
	$FMA{$f_id}->{id} = $f_id;
	$FMA{$f_id}->{name} = $name;
#	$FMA{$f_id}->{detail} = $detail if(defined $detail);
	$FMA{$f_id}->{entry} = $modified;
	$FMA{$f_id}->{icon} = ($state eq "update" ?"arrow_up.png":"add.png");
	$FMA{$f_id}->{version} = $version;
	if(defined $version){
		if(exists($VERSION_HASH{$version})){
			$FMA{$f_id}->{tg_id} = $VERSION_HASH{$version}->{tg_id};
			$FMA{$f_id}->{tg_name} = $VERSION_HASH{$version}->{tg_name};
		}
		$TARGET_VER{$version} = "";
	}
}
$sth->finish;
undef $sth;


my @sql_arr = ();
foreach my $tgi_version (keys(%VERSION_HASH)){
	$sql = qq|select b_id as id,|;
	if($FORM{lng} eq "ja"){
		$sql .= qq|COALESCE(b_name_j,b_name_k,b_name_e) as name|;
	}else{
		$sql .= qq|COALESCE(b_name_e,b_name_j,b_name_k) as name|;
	}
	$sql .= qq|,b_entry as entry,b_modified as modified,'$tgi_version' as version,b_delcause as delcause from $VERSION_HASH{$tgi_version}->{table}|;
#	$sql .= qq| where b_modified >= (timestamp '$last_modified' - interval '7 day') and b_delcause is null order by b_modified desc,b_name_e asc|;
	push(@sql_arr,$sql);
}

$sql = qq|select f_id as id,|;
if($FORM{lng} eq "ja"){
	$sql .= qq|COALESCE(f_name_j,f_name_k,f_name_e) as name|;
}else{
	$sql .= qq|COALESCE(f_name_e,f_name_j,f_name_k) as name|;
}
$sql .= qq|,f_entry as entry,f_modified as modified,null as version,f_delcause as delcause from fma|;
#$sql .= qq| where f_modified >= (timestamp '$last_modified' - interval '7 day') and f_delcause is null order by f_modified desc,f_name_k asc limit 10|;

push(@sql_arr,$sql);
$sql = qq|select id,name,EXTRACT(EPOCH FROM entry),EXTRACT(EPOCH FROM modified),version from (| . join(" union ",@sql_arr) . qq|) as a|;
$sql .= qq| where modified >= (timestamp '$last_modified' - interval '7 day') and delcause is null order by modified desc,name asc limit 10|;


print LOG __LINE__,":sql=[$sql]\n";

$sth = $dbh->prepare($sql);
$sth->execute();
$sth->bind_columns(undef, \($f_id,$name,$entry,$modified,$version));
while($sth->fetch){
	if(exists($FMA{$f_id}) && ($FMA{$f_id}->{entry}>($modified>$entry?$modified:$entry))){
#		warn $t_id,"\n";
		next ;
	}
	delete $FMA{$f_id} if(exists($FMA{$f_id}));

	utf8::decode($name) if(defined $name && !utf8::is_utf8($name));

	$FMA{$f_id} = {};
	$FMA{$f_id}->{id} = $f_id;
	$FMA{$f_id}->{name} = $name;
#	$FMA{$f_id}->{detail} = $detail if(defined $detail);
	$FMA{$f_id}->{entry} = $modified;
	$FMA{$f_id}->{icon} = ($modified>$entry?"arrow_up.png":"add.png");
	$FMA{$f_id}->{version} = $version;
	if(defined $version){
		if(exists($VERSION_HASH{$version})){
			$FMA{$f_id}->{tg_id} = $VERSION_HASH{$version}->{tg_id};
			$FMA{$f_id}->{tg_name} = $VERSION_HASH{$version}->{tg_name};
		}
		$TARGET_VER{$version} = "";
	}
}
$sth->finish;
undef $sth;


foreach my $version (keys(%TARGET_VER)){
#	warn __LINE__,":$version\n";
	my $cache_path = &getCachePath($version);
	my $store_file = qq|$cache_path/tree1_storable.store|;
	my $store2_file = qq|$cache_path/tree2_storable.store|;
	if(-e $store_file && -s $store_file && -e $store2_file && -s $store2_file){
		my $href = retrieve($store_file);
		$TREE{$version} = $href;
		my $href = retrieve($store2_file);
		$VER2TREE{$version} = $href;
	}else{
		my($t_id,$t_pid,$f_id,$f_pid,$t_delcause,$t_type,$tgi_version,$tg_name_j,$tg_name_e);
		$sql  = qq|select t_id,t_pid,f_id,f_pid,t_delcause,t_type,i.tgi_version from tree|;
		$sql .= qq| left join (select tg_id,tgi_id,tgi_version from tree_group_item) as i on i.tg_id=tree.tg_id and i.tgi_id=tree.tgi_id|;
		$sql .= qq| where i.tgi_version=?|;
		$sql .= qq| order by t_type,f_id|;
		my $sth = $dbh->prepare($sql);
		$sth->execute($version);
		$sth->bind_columns(undef, \($t_id,$t_pid,$f_id,$f_pid,$t_delcause,$t_type,$tgi_version));
		while($sth->fetch){
			$TREE{$tgi_version} = {} unless(exists($TREE{$tgi_version}));
			unless(exists($TREE{$tgi_version}->{$f_id})){
				$TREE{$tgi_version}->{$f_id} = {};
				$TREE{$tgi_version}->{$f_id}->{f_pid} = $f_pid;
				$TREE{$tgi_version}->{$f_id}->{t_type} = $t_type;
				$TREE{$tgi_version}->{$f_id}->{t_delcause} = $t_delcause if(defined $t_delcause && $t_delcause ne "");
			}
			$VER2TREE{$tgi_version} = {} unless(exists($VER2TREE{$tgi_version}));
			$VER2TREE{$tgi_version}->{$f_id} = {} unless(exists($VER2TREE{$tgi_version}->{$f_id}));
			unless(exists($VER2TREE{$tgi_version}->{$f_id}->{$t_type})){
				$VER2TREE{$tgi_version}->{$f_id}->{$t_type} = {};
				$VER2TREE{$tgi_version}->{$f_id}->{$t_type}->{t_id} = $t_id;
				$VER2TREE{$tgi_version}->{$f_id}->{$t_type}->{t_pid} = $t_pid if(defined $t_pid);
				$VER2TREE{$tgi_version}->{$f_id}->{$t_type}->{f_pid} = $f_pid if(defined $f_pid);
				$VER2TREE{$tgi_version}->{$f_id}->{$t_type}->{t_delcause} = $t_delcause if(defined $t_delcause && $t_delcause ne "");
			}
		}
		store $TREE{$version}, $store_file;
		store $VER2TREE{$version}, $store2_file;
	}
}
rmdir($store_lock) if(-e $store_lock);


$sql = qq|select |;
if($FORM{lng} eq "ja"){
	$sql .= qq|COALESCE(f_name_j,f_name_k,f_name_e)|;
}else{
	$sql .= qq|COALESCE(f_name_e,f_name_j,f_name_k)|;
}
$sql .= qq| from fma where f_id=?|;
print LOG __LINE__,":sql=[$sql]\n";
$sth = $dbh->prepare($sql);

my %FMA_TEMP = ();

foreach $f_id (keys(%FMA)){

	my $version = $FMA{$f_id}->{version};
	next if(!exists($TREE{$version}->{$f_id}));
	my $t_type = $TREE{$version}->{$f_id}->{t_type};


	my $del = 0;
	my @p_name = ();
	my @p_path = ();
	my $temp_id = $f_id;
	while(exists($VER2TREE{$version}->{$temp_id}->{$t_type})){
#		warn __LINE__,":\$f_id=[$temp_id][$t_type]\n";
		if(exists($VER2TREE{$version}->{$temp_id}->{$t_type}->{t_delcause})){
			$del = 1;
			last;
		}
		if(exists($FMA{$temp_id})){

#			warn __LINE__,":",$FMA{$temp_id}->{name},"\n";

			unshift @p_name,$FMA{$temp_id}->{name};
		}else{
			if(!exists($FMA_TEMP{$temp_id})){
#				warn $f_id,"\n";
				$FMA_TEMP{$temp_id}->{name} = $temp_id;


				$sth->execute($temp_id);
#				$sth->bind_columns(undef, \($name,$detail,$entry,$modified));
				$sth->bind_columns(undef, \($name));
				while($sth->fetch){
					$FMA_TEMP{$temp_id} = {};
					$FMA_TEMP{$temp_id}->{name} = $name;
				}
				$sth->finish;
			}
			unshift @p_name,$FMA_TEMP{$temp_id}->{name} if(exists($FMA_TEMP{$temp_id}));
		}
		unshift @p_path,$temp_id;
		$temp_id = $VER2TREE{$version}->{$temp_id}->{$t_type}->{f_pid};
	}
#	warn __LINE__,":\$del=[$del]\n";
	next if($del);

	pop @p_name;
	pop @p_path;

#	print "[$t_id][",join("/",@p_name),"][",join("/",@p_path),"][$s_name][$name][$detail]\n";

	my $tree_title = join("/",@p_name);
	if(!exists($HASH{$tree_title})){
		$HASH{$tree_title} = {};
		$HASH{$tree_title}->{title} = $tree_title;
		$HASH{$tree_title}->{fma} = ();
	}

#	$FMA{$f_id}->{detail} = '<i>'.$FMA{$f_id}->{s_name}.'</i>' if(!exists($FMA{$f_id}->{detail}));

	my $path = &getImagePath($f_id,$FORM{position},$version);
	my $S_HASH = {};
	$S_HASH->{id} = $f_id;
	$S_HASH->{name} = $FMA{$f_id}->{name};

	$S_HASH->{detail} = (utf8::is_utf8($FMA{$f_id}->{detail}) ? $FMA{$f_id}->{detail} : Encode::decode_utf8($FMA{$f_id}->{detail})) if(exists($FMA{$f_id}->{detail}));

	$S_HASH->{image} = $path;
	$S_HASH->{icon} = $FMA{$f_id}->{icon};
#	$S_HASH->{txpath} = "ctg_".join("/ctg_",@p_path);
	$S_HASH->{txpath} = join("/",@p_path);
	$S_HASH->{entry} = $FMA{$f_id}->{entry};

	my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($FMA{$f_id}->{entry});
	$S_HASH->{entry} = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);

#	$S_HASH->{version} = $FMA{$f_id}->{version};
	my $form = {};
	foreach my $key (keys(%FORM)){
		$form->{$key} = $FORM{$key};
	}
	$form->{version} = $FMA{$f_id}->{version};
	$S_HASH->{version}= &convRendererVersion2VersionName($dbh,$form);



	$S_HASH->{tg_id} = $FMA{$f_id}->{tg_id};
	$S_HASH->{tg_name} = $FMA{$f_id}->{tg_name};
	push(@{$HASH{$tree_title}->{fma}},$S_HASH);

#	warn __LINE__,":\n";
}
undef $sth;


foreach my $key (sort keys(%HASH)){
	@{$HASH{$key}->{fma}} = sort {$b->{entry} <=> $a->{entry}} @{$HASH{$key}->{fma}};
	push(@{$WHATNEW->{whatnew}},$HASH{$key});
}
@{$WHATNEW->{whatnew}} = sort {$a->{title} cmp $b->{title}} @{$WHATNEW->{whatnew}};

#exit;



#my $json = to_json($WHATNEW);
my $json = encode_json($WHATNEW);
$json =~ s/"(true|false)"/$1/mg;
print $json;
print LOG __LINE__,":",$json,"\n";

close(LOG);
exit;

