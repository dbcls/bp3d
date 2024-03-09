use strict;
use DBD::Pg;

my $dbh = &get_dbh();

my $user = qq|bot|;
#my $user = qq|tyamamot|;

my $base_path = qq|/bp3d/ag-wiki/db|;

my $php = qq|/bp3d/local/php-5.2.17/bin/php|;

my $out_dev = "";
$out_dev = qq| >& $base_path/log2.txt| if(exists($ENV{REQUEST_METHOD}));

my $import_path = qq|/dev/shm|;
unless(-e $import_path){
	mkdir $import_path;
	chmod 0777,$import_path;
}
#my $import_image_path = qq|$import_path/thumb|;
my $import_image_path = qq|$import_path/anatomo_thumb|;

#my $wiki_path = qq|/var/www/html/project/adcatalog2/|.&getMediawikiPath();
#my $script = qq|$php $wiki_path/maintenance/importTextFile.php --user '$user'|;

sub getMediawikiPath {
	my $lang = shift;
	$lang = qq|wiki1| unless(defined $lang);
	return qq|../htdocs/$lang|;
}

sub getWikiPath {
	my $lang = shift;
	return qq|$base_path/|.&getMediawikiPath($lang);
}
sub getTextScript {
	my $lang = shift;
	my $wiki_path = &getWikiPath($lang);
	return qq|$php $wiki_path/maintenance/importTextFile.php --user '$user'|;
}
sub getImageScript {
	my $lang = shift;
	my $wiki_path = &getWikiPath($lang);
	return qq|$php $wiki_path/maintenance/importImages.php --user '$user' --overwrite $import_image_path$out_dev|;
}

#my $imp_image_script = qq|$php $wiki_path/maintenance/importImages.php --user '$user' --overwrite $import_image_path$out_dev|;

my $del_list = qq|$import_path/.list_$$.txt|;

#my $del_script = qq|$php $wiki_path/maintenance/deleteBatch.php -u '$user' $del_list$out_dev|;

my $import_file = qq|$import_path/.$$.txt|;

#my $catalog_link_url = qq|http://221.186.138.155/project/adcatalog2/adcatalog.cgi?t=|;

sub _dump {
	my $msg = shift;
	return if(exists($ENV{REQUEST_METHOD}));
	warn $msg,"\n";
}

sub exportThumb {
	my %args = (
		FH    => undef, #FILEHANDLE
		name  => undef,
		image => undef,
		geometry => qq|120x120|,
		@_
	);
	my $FH = $args{FH};
	my $th_name = $args{name};
	my $th_img  = $args{image};
	my $geometry = $args{geometry};

	my $path;
	my $file;
	eval{
		if(defined $th_img){
			my $image_info = image_info(\$th_img);
#			warn __LINE__,":\$image_info->{file_ext}=[",$image_info->{file_ext},"]\n";
			if($image_info && $image_info->{file_ext} ne ""){
				$path = "$import_image_path";
				if(!-e $path){
					mkdir $path;
					chmod 0777,$path;
				}
				$file = sprintf("%s.%s",$th_name,$image_info->{file_ext});
				$path .= qq|/$file|;
				unless(-e $path){
					my @blob = ($th_img);
					my $im = Image::Magick->new(magick=>$image_info->{file_ext});
					$im->BlobToImage(@blob);
					$im->Resize(geometry=>$geometry,blur=>0.7);
					$im->Write($path);
					undef $im;
					chmod 0666,$path;
				}
			}
		}
	};
	if($@){
		print LOG __LINE__,":\$@=[$@]\n";
		undef $path;
	}
	print $FH "[[File:$file|thumb|]]\n" if(defined $FH && defined $file && defined $path && -e $path);
#	return($path,$file);
}
sub exportTree {
	my %args = (
		FH     => undef, #FILEHANDLE
		LOCALE => undef,
		locale => undef,
		name   => undef,
		path   => undef,
		@_
	);
	my $FH    = $args{FH};
	my $LOCALE = $args{LOCALE};
	my $name  = $args{name};
	my $path  = $args{path};

	return if(!defined $FH || !defined $LOCALE || !defined $name || !defined $path || !defined $args{locale});

	print $FH <<TEXT;
===== $LOCALE->{TREE_TITLE} =====
TEXT

	my $prev_base;

	foreach my $path_arr (@$path){
		my $len = scalar @$path_arr;
warn __LINE__,":[",join("/",@$path_arr),"]\n";
		next if($len<=0);
		my $base = shift @$path_arr;
		if($prev_base ne $base){
			print $FH qq|* [[$LOCALE->{DOCUMENT_TITLE}/$base\|$base]]\n|;
			$prev_base = $base;
		}
		print $FH qq|{{Dbcatalog/classified\|base=$base/\||,join("|",@$path_arr),qq|}}\n| if(scalar @$path_arr > 0);
	}

	print $FH qq|\n|;
}
sub exportDetail {
	my %args = (
		FH     => undef, #FILEHANDLE
		LOCALE => undef,
		locale => undef,
		lsdbid => undef,
		url    => undef,
		title  => undef,
		name   => undef,
		desc   => undef,
		togotv => undef,
		@_
	);
	my $FH    = $args{FH};
	my $LOCALE = $args{LOCALE};

	return if(!defined $FH || !defined $LOCALE || !defined $args{locale});

	print $FH <<TEXT;
===== $LOCALE->{DETAIL_TITLE} =====
<!--
lsdbid:LsdbID
title:$LOCALE->{DETAIL_TITLE_TITLE}
url:$LOCALE->{DETAIL_TITLE_URL}
name:$LOCALE->{DETAIL_TITLE_NAME}
desc:$LOCALE->{DETAIL_TITLE_DESC}
togotv:$LOCALE->{DETAIL_TITLE_TOGOTV}
-->
{{Dbcatalog/detail
|lsdbid=$args{lsdbid}
|title=$args{title}
|url=$args{url}
|name=$args{name}
|desc=$args{desc}
|togotv=$args{togotv}
}}

TEXT
}




my $sth_tree;

my $sql_content2tree = "";
#$sql_content2tree .= qq|select|;
#$sql_content2tree .= qq| tr_id|;
#$sql_content2tree .= qq| from content2tree|;
#$sql_content2tree .= qq| where ct_delcause is null and ct_id=?|;

$sql_content2tree .= qq|select|;
$sql_content2tree .= qq| tree.tr_id|;
$sql_content2tree .= qq| from content2tree|;
$sql_content2tree .= qq| left join (select tc_id,tr_id,tr_order from tree) as tree on tree.tr_id=content2tree.tr_id|;
$sql_content2tree .= qq| left join (select tc_id,tc_order from tree_class) as tree_class on tree.tc_id=tree_class.tc_id|;
$sql_content2tree .= qq| where ct_delcause is null and tree_class.tc_id=? and ct_id=?|;
$sql_content2tree .= qq| order by tree.tc_id,tree_class.tc_order,tree.tr_order;|;
my $sth_content2tree;

my $sql_content = "";
$sql_content .= qq|select|;
$sql_content .= qq| ct_id|;
$sql_content .= qq|,ct_dbid|;
$sql_content .= qq|,ct_url|;
$sql_content .= qq|,ct_url_e|;
$sql_content .= qq|,ct_title_j|;
$sql_content .= qq|,ct_title_e|;
$sql_content .= qq|,ct_name_j|;
$sql_content .= qq|,ct_name_e|;
$sql_content .= qq|,ct_desc_j|;
$sql_content .= qq|,ct_desc_e|;
$sql_content .= qq|,ct_togotv|;
$sql_content .= qq|,t.th_img from content|;
$sql_content .= qq| left join (select thumbnail.th_url,thumbnail.th_img from thumbnail) as t on content.ct_url = t.th_url|;
$sql_content .= qq| where ct_delcause is null and ct_id=?|;

my $sth_content;

my $sql_del_content = "";
$sql_del_content .= qq|select|;
$sql_del_content .= qq| ct_id|;
$sql_del_content .= qq|,ct_name_j|;
$sql_del_content .= qq|,ct_name_e|;
$sql_del_content .= qq|,ct_delcause|;
$sql_del_content .= qq| from content|;
$sql_del_content .= qq| where ct_id=?|;

my $sth_del_content;


my $tr_id;
my $tr_pid;
my $tr_name_j;
my $tr_name_e;

my($ct_id,$ct_dbid,$ct_url_j,$ct_url_e,$ct_title_j,$ct_title_e,$ct_name_j,$ct_name_e,$ct_desc_j,$ct_desc_e,$ct_togotv,$ct_delcause);
my $ct_url;
my $ct_title;
my $ct_name;
my $ct_desc;
my $th_img;

my $column_number = 0;

sub deleteWiki {
	my $param_ct_id = shift;
delete $ENV{REQUEST_METHOD};
print LOG __LINE__,":\n";
	eval{
		$sth_del_content = $dbh->prepare($sql_del_content) unless(defined $sth_del_content);
		$sth_del_content->execute($param_ct_id);
print LOG __LINE__,":\$sth_del_content->rows=[",$sth_del_content->rows,"]\n";
		if($sth_del_content->rows>0){
			open(OUT,"> $del_list");
			$column_number = 0;
			$sth_del_content->bind_col(++$column_number, \$ct_id, undef);
			$sth_del_content->bind_col(++$column_number, \$ct_name_j, undef);
			$sth_del_content->bind_col(++$column_number, \$ct_name_e, undef);
			$sth_del_content->bind_col(++$column_number, \$ct_delcause, undef);
			while($sth_del_content->fetch){
				next unless(defined $ct_delcause);
				if(defined $ct_name_j){
					$ct_name_j = &_trim2($ct_name_j);
					print OUT qq|$ct_name_j\n|;
				}
				if(defined $ct_name_e){
					$ct_name_e = &_trim2($ct_name_e);
					print OUT qq|$ct_name_e\n|;
				}
			}
			close(OUT);

#			print LOG __LINE__,":$del_script\n";
#			system($del_script);
#			my $exit_value = $? >> 8;
#			my $signal_num = $? & 127;
#			my $dumped_core = $? & 128;
#			print LOG __LINE__,":[$exit_value][$signal_num][$dumped_core]\n";
#			unlink $del_list if(-e $del_list);
		}
		$sth_del_content->finish;
	};
	if($@){
		print LOG __LINE__,":",$@,"\n";
	}
}

sub getWikiTree {
	my $param_tr_id = shift;
	my $path_j = shift;
	my $path_e = shift;

	my $tr_pid;
	my $tr_name_j;
	my $tr_name_e;
	my $tc_id;

	my $sql_tree = "";
	$sql_tree .= qq|select|;
	$sql_tree .= qq| tr_pid|;
	$sql_tree .= qq|,tr_name_j|;
	$sql_tree .= qq|,tr_name_e|;
	$sql_tree .= qq|,tc_id|;
	$sql_tree .= qq| from tree|;
	$sql_tree .= qq| where tr_delcause is null and tr_id=?|;
	my $sth_tree = $dbh->prepare($sql_tree);
	$sth_tree->execute($param_tr_id);
	if($sth_tree->rows>0){
		$column_number = 0;
		$sth_tree->bind_col(++$column_number, \$tr_pid, undef);
		$sth_tree->bind_col(++$column_number, \$tr_name_j, undef);
		$sth_tree->bind_col(++$column_number, \$tr_name_e, undef);
		$sth_tree->bind_col(++$column_number, \$tc_id, undef);
		$sth_tree->fetch;
		$sth_tree->finish;
		undef $sth_tree;
		unshift(@$path_j,$tr_name_j) if(defined $tr_name_j);
		unshift(@$path_e,$tr_name_e) if(defined $tr_name_e);
		if(defined $tr_pid){
			&getWikiTree($tr_pid,$path_j,$path_e);
		}else{
			my $tc_name_j;
			my $tc_name_e;
			my $sql_tree_class = qq|select|;
			$sql_tree_class   .= qq| tc_name_j|;
			$sql_tree_class   .= qq|,tc_name_e|;
			$sql_tree_class   .= qq| from tree_class|;
			$sql_tree_class   .= qq| where tc_id=? and tc_delcause is null|;
			my $sth_tree_class = $dbh->prepare($sql_tree_class);
			$sth_tree_class->execute($tc_id);
			my $column_number = 0;
			$sth_tree_class->bind_col(++$column_number, \$tc_name_j, undef);
			$sth_tree_class->bind_col(++$column_number, \$tc_name_e, undef);
			$sth_tree_class->fetch;
			$sth_tree_class->finish;
			undef $sth_tree_class;
			unshift(@$path_j,$tc_name_j) if(defined $tc_name_j);
			unshift(@$path_e,$tc_name_e) if(defined $tc_name_e);
		}
	}else{
		$sth_tree->finish;
		undef $sth_tree;
	}
}

sub importWiki {
	my $param_ct_id = shift;
	my $param_update_tree = shift;
	$param_update_tree = 1 unless(defined $param_update_tree);
delete $ENV{REQUEST_METHOD};

	$sth_content2tree = $dbh->prepare($sql_content2tree) unless(defined $sth_content2tree);
	$sth_content      = $dbh->prepare($sql_content)      unless(defined $sth_content);

	my @PATH_J = ();
	my @PATH_E = ();
	my %TRIDS = ();

	my $tc_id;
	my $tc_name_j;
	my $tc_name_e;
	my $column_number;

	my %LOCALE_J = &getLocale('ja');
	my %LOCALE_E = &getLocale('en');

	my $sql_tree_class = qq|select|;
	$sql_tree_class   .= qq| tc_id|;
	$sql_tree_class   .= qq|,tc_name_j|;
	$sql_tree_class   .= qq|,tc_name_e|;
	$sql_tree_class   .= qq| from tree_class|;
	$sql_tree_class   .= qq| where tc_delcause is null|;
	$sql_tree_class   .= qq| order by tc_order,tc_id|;
	my $sth_tree_class = $dbh->prepare($sql_tree_class);
	$sth_tree_class->execute();
	$column_number = 0;
	$sth_tree_class->bind_col(++$column_number, \$tc_id, undef);
	$sth_tree_class->bind_col(++$column_number, \$tc_name_j, undef);
	$sth_tree_class->bind_col(++$column_number, \$tc_name_e, undef);
	while($sth_tree_class->fetch){
		$sth_content2tree->execute($tc_id,$param_ct_id);
		if($sth_content2tree->rows>0){
			$column_number = 0;
			$sth_content2tree->bind_col(++$column_number, \$tr_id, undef);
			while($sth_content2tree->fetch){
				next unless(defined $tr_id);
				$TRIDS{$tr_id} = "";

				my @TEMP_J = ();
				my @TEMP_E = ();
				&getWikiTree($tr_id,\@TEMP_J,\@TEMP_E);
				if(scalar @TEMP_J > 0 && scalar @TEMP_E > 0){
					push(@PATH_J,\@TEMP_J);
					push(@PATH_E,\@TEMP_E);
				}
			}
		}else{
			my @TEMP_J = ();
			my @TEMP_E = ();
			push(@TEMP_J,$tc_name_j);
			push(@TEMP_E,$tc_name_e);
#			push(@TEMP_J,$LOCALE_J{'TREE_UNCLASS_TITLE_'.$tc_id});
#			push(@TEMP_E,$LOCALE_E{'TREE_UNCLASS_TITLE_'.$tc_id});
			push(@TEMP_J,$LOCALE_J{'TREE_UNCLASS_TITLE_0'});
			push(@TEMP_E,$LOCALE_E{'TREE_UNCLASS_TITLE_0'});
			push(@PATH_J,\@TEMP_J);
			push(@PATH_E,\@TEMP_E);
		}
		$sth_content2tree->finish;
	}
	$sth_tree_class->finish;
	undef $sth_tree_class;

	&updateWikiTree(\%TRIDS) if($param_update_tree && scalar(keys(%TRIDS))>0);

	my $sql_tree_class = qq|select|;
	$sql_tree_class   .= qq| tc_name_j|;
	$sql_tree_class   .= qq|,tc_name_e|;
	$sql_tree_class   .= qq| from tree_class|;
	$sql_tree_class   .= qq| where tc_id=1 and tc_delcause is null|;
	my $sth_tree_class = $dbh->prepare($sql_tree_class);
	$sth_tree_class->execute();
	$column_number = 0;
	$sth_tree_class->bind_col(++$column_number, \$tc_name_j, undef);
	$sth_tree_class->bind_col(++$column_number, \$tc_name_e, undef);
	$sth_tree_class->fetch;
	$sth_tree_class->finish;
	undef $sth_tree_class;

	$sth_content->execute($param_ct_id);

	$column_number = 0;
	$sth_content->bind_col(++$column_number, \$ct_id, undef);
	$sth_content->bind_col(++$column_number, \$ct_dbid, undef);
	$sth_content->bind_col(++$column_number, \$ct_url_j, undef);
	$sth_content->bind_col(++$column_number, \$ct_url_e, undef);
	$sth_content->bind_col(++$column_number, \$ct_title_j, undef);
	$sth_content->bind_col(++$column_number, \$ct_title_e, undef);
	$sth_content->bind_col(++$column_number, \$ct_name_j, undef);
	$sth_content->bind_col(++$column_number, \$ct_name_e, undef);
	$sth_content->bind_col(++$column_number, \$ct_desc_j, undef);
	$sth_content->bind_col(++$column_number, \$ct_desc_e, undef);
	$sth_content->bind_col(++$column_number, \$ct_togotv, undef);
	$sth_content->bind_col(++$column_number, \$th_img, { pg_type => DBD::Pg::PG_BYTEA });
	while($sth_content->fetch){

		$ct_url_j = &_trim2($ct_url_j) if(defined $ct_url_j);
		$ct_url_e = &_trim2($ct_url_e) if(defined $ct_url_e);
		$ct_title_j = &_trim2($ct_title_j) if(defined $ct_title_j);
		$ct_title_e = &_trim2($ct_title_e) if(defined $ct_title_e);
		$ct_name_j = &_trim2($ct_name_j) if(defined $ct_name_j);
		$ct_name_e = &_trim2($ct_name_e) if(defined $ct_name_e);
		$ct_desc_j = &_trim2($ct_desc_j) if(defined $ct_desc_j);
		$ct_desc_e = &_trim2($ct_desc_e) if(defined $ct_desc_e);
		$ct_togotv = &_trim2($ct_togotv) if(defined $ct_togotv);

warn __LINE__,"\$ct_id=[$ct_id]\n";
warn __LINE__,"\$ct_title_j=[$ct_title_j]\n";
warn __LINE__,"\$ct_title_e=[$ct_title_e]\n";
warn __LINE__,"\$ct_name_j=[$ct_name_j]\n";
warn __LINE__,"\$ct_name_e=[$ct_name_e]\n";

		my $th_name_j = (defined $ct_title_e ? $ct_title_e : defined $ct_name_e ? $ct_name_e : defined $ct_title_j ? $ct_title_j : $ct_name_j);
		my $name_j = (defined $ct_title_j ? $ct_title_j : defined $ct_name_j ? $ct_name_j : defined $ct_title_e ? $ct_title_e : $ct_name_e);
		my $name_e = (defined $ct_title_e ? $ct_title_e : $ct_name_e);

		if(defined $ct_title_j || defined $ct_title_e || defined $ct_name_j || defined $ct_name_e){
			my $locale = "ja";
			my %LOCALE = &getLocale($locale);

			$import_file = qq|$import_path/.$ct_id\_$locale.txt|;

			my $OUT;
			open($OUT,"> $import_file");

			my $ct_desc = defined $ct_desc_j ? $ct_desc_j : $ct_desc_e;
			print $OUT qq|\n$ct_desc\n\n| if(defined $ct_desc);

#			&exportThumb(FH=>$OUT,name=>$th_name_j,image=>$th_img);
#			print $OUT qq|__TOC__\n|;

			print $OUT qq|{\|width="100%"\n|;
			print $OUT qq|\|valign="top"\|__TOC__\n|;
			print $OUT qq|\|valign="top"\||;
			&exportThumb(FH=>$OUT,name=>$th_name_j,image=>$th_img);
			print $OUT qq|\|}\n|;


			if(scalar @PATH_J > 0 && scalar @PATH_E > 0){
				&exportTree(FH=>$OUT,locale=>$locale,LOCALE=>\%LOCALE,name=>$tc_name_j,path=>\@PATH_J);
			}

			&exportDetail(
				FH     => $OUT,
				LOCALE => \%LOCALE,
				locale => $locale,
				lsdbid => $ct_dbid,
				url    => defined $ct_url_j ? $ct_url_j : $ct_url_e,
#				title  => defined $ct_title_j ? $ct_title_j : $ct_title_e,
				name   => defined $ct_name_j ? $ct_name_j : $ct_name_e,
#				desc   => defined $ct_desc_j ? $ct_desc_j : $ct_desc_e,
				togotv => $ct_togotv
			);

			print $OUT qq|\n----\n<div id="adcatalog-link">[[dbcatalog-link:{{PAGENAMEE}}\|{{PAGENAME}} ($LOCALE{DOCUMENT_TITLE})]]</div>\n|;

			print $OUT qq|[[Category:$LOCALE{DOCUMENT_TITLE}\|$ct_name]]\n|;

			print $OUT qq|\n\n[[en:$name_e]]\n| if(defined $name_e);
			close($OUT);
			chmod 0666,$import_file if(-e $import_file);

			my $script = &getTextScript($locale);
			my $command = qq|$script --title "$name_j" $import_file$out_dev|;
			print LOG __LINE__,":$command\n";
			system($command);
			my $exit_value = $? >> 8;
			my $signal_num = $? & 127;
			my $dumped_core = $? & 128;
			print LOG __LINE__,":[$exit_value][$signal_num][$dumped_core]\n";
			unlink $import_file if(-e $import_file);
		}
		if(defined $ct_title_e || defined $ct_name_e){
			my $locale = "en";
			my %LOCALE = &getLocale($locale);

			$import_file = qq|$import_path/.$ct_id\_$locale.txt|;

			my $OUT;
			open($OUT,"> $import_file");

			&exportThumb(FH=>$OUT,name=>$name_e,image=>$th_img);

			if(scalar @PATH_J > 0 && scalar @PATH_E > 0){
				&exportTree(FH=>$OUT,locale=>$locale,LOCALE=>\%LOCALE,name=>$tc_name_e,path=>\@PATH_E);
			}

			&exportDetail(
				FH     => $OUT,
				LOCALE => \%LOCALE,
				locale => $locale,
				lsdbid => $ct_dbid,
				url    => defined $ct_url_e ? $ct_url_e : $ct_url_j,
				title  => $ct_title_e,
				name   => $ct_name_e,
				desc   => $ct_desc_e,
				togotv => $ct_togotv
			);

			print $OUT qq|\n----\n<div id="adcatalog-link">[[dbcatalog-link:{{PAGENAMEE}}\|{{PAGENAME}} ($LOCALE{DOCUMENT_TITLE})]]</div>\n|;

			print $OUT qq|[[Category:$LOCALE{DOCUMENT_TITLE}\|$name_e]]\n|;

			print $OUT qq|\n\n[[ja:$name_j]]\n| if(defined $name_j);
			close($OUT);
			chmod 0666,$import_file if(-e $import_file);

			my $script = &getTextScript($locale);
			my $command = qq|$script --title "$name_e" $import_file$out_dev|;
			print LOG __LINE__,":$command\n";
			system($command);
			my $exit_value = $? >> 8;
			my $signal_num = $? & 127;
			my $dumped_core = $? & 128;
			print LOG __LINE__,":[$exit_value][$signal_num][$dumped_core]\n";
			unlink $import_file if(-e $import_file);
		}
	}

	if(-e $import_image_path){
		my @FILES = ();
		if(opendir (DIR, $import_image_path)){
			@FILES = grep {-e "$import_image_path/$_"} readdir(DIR);
			closedir(DIR);
		}
		if(scalar @FILES > 0){
			foreach my $locale ("ja","en"){
				sleep(1);
				my $imp_image_script = &getImageScript($locale);
				print LOG __LINE__,":$imp_image_script\n";
				system($imp_image_script);
				my $exit_value = $? >> 8;
				my $signal_num = $? & 127;
				my $dumped_core = $? & 128;
				print LOG __LINE__,":[$exit_value][$signal_num][$dumped_core]\n";
			}

			foreach (@FILES){
				my $file = qq|$import_image_path/$_|;
				unlink $file if(-e $file);
			}
		}
#		rmdir $import_image_path;
	}

	$sth_content->finish;
	undef $sth_content;

#	unlink $import_file if(-e $import_file);
}

my $child_pid;
sub execBackground {
#	warn __LINE__,":execBackground()\n";
	if($child_pid = fork){
		waitpid $child_pid, 0;
	}elsif(defined $child_pid){
		close(STDOUT);
#		close(STDERR);
#		close(STDIN);
		exec(@_);
		exit;
	}else{
		exit(1);
	}
}

sub _updateWikiTreeClass {
	my $param_OUT_J = shift;
	my $param_OUT_E = shift;
	my $param_tr_pid = shift;
	my $param_depth = shift;
	my $param_href_j = shift;
	my $param_href_e = shift;

	my $tr_id;
	my $tr_name_j;
	my $tr_name_e;
	my $column_number;

	my $sql_tree = qq|select|;
	$sql_tree   .= qq| tr_id|;
	$sql_tree   .= qq|,tr_name_j|;
	$sql_tree   .= qq|,tr_name_e|;
	$sql_tree   .= qq| from tree|;
	$sql_tree   .= qq| where tr_pid=? and tr_delcause is null|;
	$sql_tree   .= qq| order by tr_order|;
	my $sth_tree = $dbh->prepare($sql_tree);
	$sth_tree->execute($param_tr_pid);
	$column_number = 0;
	$sth_tree->bind_col(++$column_number, \$tr_id, undef);
	$sth_tree->bind_col(++$column_number, \$tr_name_j, undef);
	$sth_tree->bind_col(++$column_number, \$tr_name_e, undef);
	while($sth_tree->fetch){
		for(my $i=0;$i<$param_depth;$i++){
			print $param_OUT_J qq|*|;
		}
		for(my $i=0;$i<$param_depth;$i++){
			print $param_OUT_E qq|*|;
		}

		print $param_OUT_J qq|[[$param_href_j/$tr_name_j\|$tr_name_j]]\n|;
		print $param_OUT_E qq|[[$param_href_e/$tr_name_e\|$tr_name_e]]\n|;

		&_updateWikiTreeClass($param_OUT_J,$param_OUT_E,$tr_id,$param_depth+1,qq|$param_href_j/$tr_name_j|,qq|$param_href_e/$tr_name_e|);
	}
	$sth_tree->finish;
	undef $sth_tree;
}

sub updateWikiTreeClass {
	my $tc_id;
	my $tc_name_j;
	my $tc_name_e;
	my $tr_id;
	my $tr_name_j;
	my $tr_name_e;
	my $column_number;

	my %LOCALE_J = &getLocale('ja');
	my %LOCALE_E = &getLocale('en');

	my $sql_tree_class = qq|select|;
	$sql_tree_class   .= qq| tc_id|;
	$sql_tree_class   .= qq|,tc_name_j|;
	$sql_tree_class   .= qq|,tc_name_e|;
	$sql_tree_class   .= qq| from tree_class|;
	$sql_tree_class   .= qq| where tc_delcause is null order by tc_order|;
	my $sth_tree_class = $dbh->prepare($sql_tree_class);


#各カタログのページを生成（ここから）
	my $import_file_j = qq|$import_path/.$$\_tree_class_j.txt|;
	my $import_file_e = qq|$import_path/.$$\_tree_class_e.txt|;
	my $OUT_J;
	my $OUT_E;
	open($OUT_J,"> $import_file_j");
	open($OUT_E,"> $import_file_e");

#親階層へのリンク生成（日本語）
	print $OUT_J qq|<< [[$LOCALE_J{DOCUMENT_TITLE}]]\n|;

#親階層へのリンク生成（英語）
	print $OUT_E qq|<< [[$LOCALE_E{DOCUMENT_TITLE}]]\n|;

	$sth_tree_class->execute();
	$column_number = 0;
	$sth_tree_class->bind_col(++$column_number, \$tc_id, undef);
	$sth_tree_class->bind_col(++$column_number, \$tc_name_j, undef);
	$sth_tree_class->bind_col(++$column_number, \$tc_name_e, undef);
	while($sth_tree_class->fetch){
		print $OUT_J qq|*[[$LOCALE_J{DOCUMENT_TITLE}/$tc_name_j\|$tc_name_j]]\n|;
		print $OUT_E qq|*[[$LOCALE_E{DOCUMENT_TITLE}/$tc_name_e\|$tc_name_e]]\n|;
	}
	print $OUT_J qq|\n\n[[en:$LOCALE_E{DOCUMENT_TITLE}]]\n|;
	print $OUT_E qq|\n\n[[ja:$LOCALE_J{DOCUMENT_TITLE}]]\n|;

	close($OUT_J);
	close($OUT_E);

	if(-e $import_file_j){
		my $script = &getTextScript('ja');
		my $command = qq|$script --title "$LOCALE_J{DOCUMENT_TITLE}" $import_file_j$out_dev|;
		print LOG __LINE__,":$command\n";
		system($command);
		my $exit_value = $? >> 8;
		my $signal_num = $? & 127;
		my $dumped_core = $? & 128;
		print LOG __LINE__,":[$exit_value][$signal_num][$dumped_core]\n";
		unlink $import_file_j;
	}

	if(-e $import_file_e){
		my $script = &getTextScript('en');
		my $command = qq|$script --title "$LOCALE_E{DOCUMENT_TITLE}" $import_file_e$out_dev|;
		print LOG __LINE__,":$command\n";
		system($command);
		my $exit_value = $? >> 8;
		my $signal_num = $? & 127;
		my $dumped_core = $? & 128;
		print LOG __LINE__,":[$exit_value][$signal_num][$dumped_core]\n";
		unlink $import_file_e;
	}
	$sth_tree_class->finish;
#各カタログのページを生成（ここまで）

	$sth_tree_class->execute();
	$column_number = 0;
	$sth_tree_class->bind_col(++$column_number, \$tc_id, undef);
	$sth_tree_class->bind_col(++$column_number, \$tc_name_j, undef);
	$sth_tree_class->bind_col(++$column_number, \$tc_name_e, undef);
	while($sth_tree_class->fetch){
		my $import_file_j = qq|$import_path/.$$\_tree_class_j.txt|;
		my $import_file_e = qq|$import_path/.$$\_tree_class_e.txt|;
		my $OUT_J;
		my $OUT_E;
		open($OUT_J,"> $import_file_j");
		open($OUT_E,"> $import_file_e");

	#親階層へのリンク生成（日本語）
		print $OUT_J qq|<< [[$LOCALE_J{DOCUMENT_TITLE}\|$LOCALE_J{DOCUMENT_TITLE}]] / [[$LOCALE_J{DOCUMENT_TITLE}/$tc_name_j\|$tc_name_j]]\n|;

	#親階層へのリンク生成（英語）
		print $OUT_E qq|<< [[$LOCALE_E{DOCUMENT_TITLE}\|$LOCALE_E{DOCUMENT_TITLE}]] / [[$LOCALE_E{DOCUMENT_TITLE}/$tc_name_e\|$tc_name_e]]\n|;

		$tc_name_j = qq|$LOCALE_J{DOCUMENT_TITLE}/$tc_name_j|;
		$tc_name_e = qq|$LOCALE_E{DOCUMENT_TITLE}/$tc_name_e|;

		my $sql_tree = qq|select|;
		$sql_tree   .= qq| tr_id|;
		$sql_tree   .= qq|,tr_name_j|;
		$sql_tree   .= qq|,tr_name_e|;
		$sql_tree   .= qq| from tree|;
		$sql_tree   .= qq| where tc_id=? and tr_pid is null and tr_delcause is null|;
		$sql_tree   .= qq| order by tr_order|;
		my $sth_tree = $dbh->prepare($sql_tree);
		$sth_tree->execute($tc_id);
		$column_number = 0;
		$sth_tree->bind_col(++$column_number, \$tr_id, undef);
		$sth_tree->bind_col(++$column_number, \$tr_name_j, undef);
		$sth_tree->bind_col(++$column_number, \$tr_name_e, undef);
		while($sth_tree->fetch){

			print $OUT_J qq|*[[$tc_name_j/$tr_name_j\|$tr_name_j]]\n|;
			print $OUT_E qq|*[[$tc_name_e/$tr_name_e\|$tr_name_e]]\n|;

			&_updateWikiTreeClass($OUT_J,$OUT_E,$tr_id,2,qq|$tc_name_j/$tr_name_j|,qq|$tc_name_e/$tr_name_e|);

		}
		$sth_tree->finish;
		undef $sth_tree;


		print $OUT_J qq|\n\n[[en:$tc_name_e]]\n|;
		print $OUT_E qq|\n\n[[ja:$tc_name_j]]\n|;

		close($OUT_J);
		close($OUT_E);


		if(-e $import_file_j){
			my $script = &getTextScript('ja');
			my $command = qq|$script --title "$tc_name_j" $import_file_j$out_dev|;
			print LOG __LINE__,":$command\n";
			system($command);
			my $exit_value = $? >> 8;
			my $signal_num = $? & 127;
			my $dumped_core = $? & 128;
			print LOG __LINE__,":[$exit_value][$signal_num][$dumped_core]\n";
			unlink $import_file_j;
		}

		if(-e $import_file_e){
			my $script = &getTextScript('en');
			my $command = qq|$script --title "$tc_name_e" $import_file_e$out_dev|;
			print LOG __LINE__,":$command\n";
			system($command);
			my $exit_value = $? >> 8;
			my $signal_num = $? & 127;
			my $dumped_core = $? & 128;
			print LOG __LINE__,":[$exit_value][$signal_num][$dumped_core]\n";
			unlink $import_file_e;
		}
	}
	$sth_tree_class->finish;
	undef $sth_tree_class;
}

sub _updateWikiTree {
	my $param_tr_ids = shift;
	return unless(defined $param_tr_ids);

	my %LOCALE_J = &getLocale('ja');
	my %LOCALE_E = &getLocale('en');

	my $sql_tree = qq|select|;
	$sql_tree   .= qq| tr_name_j|;
	$sql_tree   .= qq|,tr_name_e|;
	$sql_tree   .= qq| from tree|;
	$sql_tree   .= qq| where tr_pid=? and tr_delcause is null|;
	$sql_tree   .= qq| order by tr_order|;
	my $sth_tree = $dbh->prepare($sql_tree);

	my $sql_content2tree_j = qq|select|;
	$sql_content2tree_j   .= qq| COALESCE(content.ct_title_j,content.ct_title_e,content.ct_name_j,content.ct_name_e)|;
	$sql_content2tree_j   .= qq| from content2tree|;
	$sql_content2tree_j   .= qq| left join (select ct_title_j,ct_title_e,ct_name_j,ct_name_e,ct_id,ct_delcause from content) as content on content2tree.ct_id=content.ct_id|;
	$sql_content2tree_j   .= qq| where tr_id=? and content2tree.ct_delcause is null and content.ct_delcause is null|;
	$sql_content2tree_j   .= qq| order by content.ct_title_j|;
	my $sth_content2tree_j = $dbh->prepare($sql_content2tree_j);

	my $sql_content2tree_e = qq|select|;
	$sql_content2tree_e   .= qq| COALESCE(content.ct_title_e,content.ct_name_e)|;
	$sql_content2tree_e   .= qq| from content2tree|;
	$sql_content2tree_e   .= qq| left join (select ct_title_e,ct_name_e,ct_id,ct_delcause from content) as content on content2tree.ct_id=content.ct_id|;
	$sql_content2tree_e   .= qq| where tr_id=? and content2tree.ct_delcause is null and content.ct_delcause is null|;
	$sql_content2tree_e   .= qq| order by content.ct_title_e|;
	my $sth_content2tree_e = $dbh->prepare($sql_content2tree_e);


	foreach my $tr_id (keys(%$param_tr_ids)){
		my $import_file_j = qq|$import_path/.$$\_$tr_id\_j.txt|;
		my $import_file_e = qq|$import_path/.$$\_$tr_id\_e.txt|;
		my $OUT_J;
		my $OUT_E;
		open($OUT_J,"> $import_file_j");
		open($OUT_E,"> $import_file_e");

		my $tr_name_j;
		my $tr_name_e;
		my $ct_name;

		my @TEMP_J = ();
		my @TEMP_E = ();
		&getWikiTree($tr_id,\@TEMP_J,\@TEMP_E);

		#タイトル生成（日本語）
		unshift(@TEMP_J,$LOCALE_J{DOCUMENT_TITLE});
		my $title_j = join("/",@TEMP_J);

		#タイトル生成（英語）
		unshift(@TEMP_E,$LOCALE_E{DOCUMENT_TITLE});
		my $title_e = join("/",@TEMP_E);

		#親階層へのリンク生成（日本語）
		print $OUT_J qq|<< |;
		my $len = scalar @TEMP_J;
		for(my $i=0;$i<$len;$i++){
			my $href = join("/",@TEMP_J[0..$i]);
			my $text = $TEMP_J[$i];
			print $OUT_J qq|[[$href\|$text]]|;
			print $OUT_J qq| / |if($i<$len-1);
		}
		print $OUT_J qq|\n|;

		#親階層へのリンク生成（英語）
		print $OUT_E qq|<< |;
		my $len = scalar @TEMP_E;
		for(my $i=0;$i<$len;$i++){
			my $href = join("/",@TEMP_E[0..$i]);
			my $text = $TEMP_E[$i];
			print $OUT_E qq|[[$href\|$text]]|;
			print $OUT_E qq| / |if($i<$len-1);
		}
		print $OUT_E qq|\n|;

		#子階層へのリンク生成
		$sth_tree->execute($tr_id);
		my $column_number = 0;
		$sth_tree->bind_col(++$column_number, \$tr_name_j, undef);
		$sth_tree->bind_col(++$column_number, \$tr_name_e, undef);
		while($sth_tree->fetch){
			if(defined $tr_name_j){
				my $href = qq|$title_j/$tr_name_j|;
				my $text = $tr_name_j;
				print $OUT_J qq|*[[$href\|$text]]\n|;
			}
			if(defined $tr_name_e){
				my $href = qq|$title_e/$tr_name_e|;
				my $text = $tr_name_e;
				print $OUT_E qq|*[[$href\|$text]]\n|;
			}
		}
		$sth_tree->finish;

		#コンテンツへのリンク生成(日本語）
		$sth_content2tree_j->execute($tr_id);
		if($sth_content2tree_j->rows>0){
			$column_number = 0;
			$sth_content2tree_j->bind_col(++$column_number, \$ct_name, undef);
			while($sth_content2tree_j->fetch){
				print $OUT_J qq|*[[$ct_name]]\n| if(defined $ct_name);
			}
		}
		$sth_content2tree_j->finish;

		#コンテンツへのリンク生成(英語）
		$sth_content2tree_e->execute($tr_id);
		if($sth_content2tree_e->rows>0){
			$column_number = 0;
			$sth_content2tree_e->bind_col(++$column_number, \$ct_name, undef);
			while($sth_content2tree_e->fetch){
				print $OUT_E qq|*[[$ct_name]]\n| if(defined $ct_name);
			}
		}
		$sth_content2tree_e->finish;

		undef $tr_name_j;
		undef $tr_name_e;
		undef $ct_name;

		print $OUT_J qq|\n\n[[en:$title_e\||,$TEMP_E[$#TEMP_E],qq|]]\n|;
		print $OUT_E qq|\n\n[[ja:$title_j\||,$TEMP_J[$#TEMP_J],qq|]]\n|;

		close($OUT_J);
		close($OUT_E);

#warn __LINE__,":[$title_j]\n";

		if(-e $import_file_j){
			my $script = &getTextScript('ja');
			my $command = qq|$script --title "$title_j" $import_file_j$out_dev|;
			print LOG __LINE__,":$command\n";
			system($command);
			my $exit_value = $? >> 8;
			my $signal_num = $? & 127;
			my $dumped_core = $? & 128;
			print LOG __LINE__,":[$exit_value][$signal_num][$dumped_core]\n";
#				unlink $import_file_j;
		}

		if(-e $import_file_e){
			my $script = &getTextScript('en');
			my $command = qq|$script --title "$title_e" $import_file_e$out_dev|;
			print LOG __LINE__,":$command\n";
			system($command);
			my $exit_value = $? >> 8;
			my $signal_num = $? & 127;
			my $dumped_core = $? & 128;
			print LOG __LINE__,":[$exit_value][$signal_num][$dumped_core]\n";
#				unlink $import_file_e;
		}
	}
	undef $sth_tree;
}

sub updateWikiTree {
	my $param_tr_ids = shift;

	my %LOCALE_J = &getLocale('ja');
	my %LOCALE_E = &getLocale('en');

	my $tc_id;
	my $tc_name_j;
	my $tc_name_e;

	unless(defined $param_tr_ids){
		$param_tr_ids = {};
		my $sql_tree_class = qq|select|;
		$sql_tree_class   .= qq| tc_id|;
		$sql_tree_class   .= qq|,tc_name_j|;
		$sql_tree_class   .= qq|,tc_name_e|;
		$sql_tree_class   .= qq| from tree_class|;
		$sql_tree_class   .= qq| where tc_delcause is null order by tc_order|;
		my $sth_tree_class = $dbh->prepare($sql_tree_class);
		$sth_tree_class->execute();
		my $column_number = 0;
		$sth_tree_class->bind_col(++$column_number, \$tc_id, undef);
		$sth_tree_class->bind_col(++$column_number, \$tc_name_j, undef);
		$sth_tree_class->bind_col(++$column_number, \$tc_name_e, undef);
		while($sth_tree_class->fetch){
			my $tr_id;
			my $sql_tree = qq|select|;
			$sql_tree   .= qq| tr_id|;
			$sql_tree   .= qq| from tree|;
			$sql_tree   .= qq| where tc_id=? and tr_delcause is null|;
			my $sth_tree = $dbh->prepare($sql_tree);
			$sth_tree->execute($tc_id);
			my $column_number = 0;
			$sth_tree->bind_col(++$column_number, \$tr_id, undef);
			while($sth_tree->fetch){
				next unless(defined $tr_id);
				$param_tr_ids->{$tr_id} = "";
			}
			$sth_tree->finish;
			undef $sth_tree;
		}
		$sth_tree_class->finish;
		undef $sth_tree_class;
	}
	&_updateWikiTree($param_tr_ids);

	&updateWikiTreeClass();

}

1;
