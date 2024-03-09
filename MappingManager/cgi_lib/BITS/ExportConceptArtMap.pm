package BITS::ExportConceptArtMap;

=pod
use Exporter;

@ISA = (Exporter);
@EXPORT_OK = qw(extract find);
@EXPORT_FAIL = qw(move_file);
=cut

use strict;
use warnings;
use feature ':5.10';

use File::Basename;
use File::Path;
use File::Spec::Functions qw(abs2rel rel2abs catdir catfile splitdir tmpdir);
use File::Copy;

use Encode;

use Archive::Zip;

sub _trim {
	my $str = shift;
	if(defined $str && length $str){
		$str =~ s/\s*$//g;
		$str =~ s/^\s*//g;
	}
	return $str;
}

sub exec {
	my $dbh = shift;
	my $FORM = shift;
	my $out_path = shift;

	my $md_id = $FORM->{'md_id'};
	my $mv_id = $FORM->{'mv_id'};
	my $ci_id = $FORM->{'ci_id'};
	my $cb_id = $FORM->{'cb_id'};

	my($ELEMENT, $COMP_DENSITY_USE_TERMS, $COMP_DENSITY_END_TERMS, $COMP_DENSITY, $CDI_MAP, $CDI_MAP_ART_DATE, $CDI_ID2CID, $CDI_MAP_SUM_VOLUME_DEL_ID) = &BITS::ConceptArtMapModified::calcElementAndDensity(
		dbh     => $dbh,
		md_id   => $md_id,
		mv_id   => $mv_id,
		ci_id   => $ci_id,
		cb_id   => $cb_id
	);

	my $art_file_base_path = &catdir($FindBin::Bin,'art_file');
	&File::Path::mkpath($art_file_base_path) unless(-e $art_file_base_path);

	$out_path = &catdir($FindBin::Bin,'download',".$$") unless(defined $out_path && length $out_path);
	&File::Path::rmtree($out_path) if(-e $out_path);
	&File::Path::mkpath($out_path);

	my ($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime();
	my @weekly = ('Sun', 'Mon', 'Tue', 'Wed', 'Thr', 'Fri', 'Sut');

	my $file = exists $FORM->{'filename'} && defined $FORM->{'filename'} && length $FORM->{'filename'} ? &_trim(&cgi_lib::common::decodeUTF8($FORM->{'filename'})) : '';
	$file = sprintf("%04d%02d%02d%02d%02d%02d", $year+1900,$month+1,$mday,$hour,$min,$sec) unless(defined $file && length $file);
	my $file_name = &catdir($out_path,'concept_art_map.txt');

	my $LF = "\n";
	my $CODE = "utf8";

	my $column_number = 0;

	my $sql=<<SQL;
select
 cm.art_id,
 cm.cdi_id,
 cdi.cdi_name,
 cmp.cmp_abbr,
 length(cmp.cmp_abbr),
-- to_char(cm.cm_entry,'YYYY-MM-DD HH24:MI:SS'),
 cm.cm_entry,

 arti.art_name,
 arti.art_ext,
-- to_char(arti.art_timestamp,'YYYY-MM-DD HH24:MI:SS'),
 arti.art_timestamp,
 EXTRACT(EPOCH FROM arti.art_timestamp),

-- arti.art_nsn,
 arti.art_mirroring,
 arti.art_comment,
 arti.art_delcause,
-- to_char(arti.art_entry,'YYYY-MM-DD HH24:MI:SS'),
 arti.art_entry,
 arti.art_modified,
 prefix.prefix_char,
 arti.art_serial,
 arti.art_md5,
 arti.art_data_size,
 arti.art_xmin,
 arti.art_xmax,
 arti.art_ymin,
 arti.art_ymax,
 arti.art_zmin,
 arti.art_zmax,
 arti.art_volume,
-- arti.art_cube_volume,
 arti.art_category,
 arti.art_judge,
 arti.art_class,
 arti.arto_id,
 arti.arto_comment,

 cmp2.cmp_title

from
 concept_art_map as cm

left join (
  select
   ci_id,
   cdi_id,
   cdi_name,
   cmp_id
  from
   concept_data_info
) as cdi on cdi.ci_id=cm.ci_id and cdi.cdi_id=cm.cdi_id

left join (
  select
   *
  from
   art_file_info
) as arti on arti.art_id=cm.art_id

left join (
  select
   cmp_id,
   cmp_abbr
  from
   concept_art_map_part
  where
   cmp_delcause is null
) as cmp on cmp.cmp_id=cm.cmp_id

left join (
 select * from id_prefix
) as prefix on prefix.prefix_id=arti.prefix_id


left join (
  select
   cmp.cmp_id,
   cmp.cmp_title
  from
   concept_art_map_part as cmp
) as cmp2 on cmp2.cmp_id=cdi.cmp_id


where
 cm.cm_delcause is null and
 arti.art_id is not null and
 cdi.cdi_name is not null and
 cm.md_id=$md_id and
 cm.mv_id=$mv_id
-- and cm.ci_id=$ci_id
-- and cm.cb_id=$cb_id
order by
 arti.prefix_id,
 arti.art_serial,
 arti.art_id
SQL

	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;

	my $art_id;
	my $cdi_id;
	my $cdi_name;
	my $cmp_abbr;
	my $cmp_length;
	my $cm_entry;
	my $art_name;
	my $art_ext;
	my $art_timestamp;
	my $art_timestamp_epoch;

#	my $art_nsn;
	my $art_mirroring;
	my $art_comment;
	my $art_delcause;
	my $art_entry;
	my $art_modified;

	my $prefix_char;
	my $art_serial;
	my $art_md5;
	my $art_data_size;
	my $art_xmin;
	my $art_xmax;
	my $art_ymin;
	my $art_ymax;
	my $art_zmin;
	my $art_zmax;
	my $art_volume;
#	my $art_cube_volume;
	my $art_category;
	my $art_judge;
	my $art_class;
	my $arto_id;
	my $arto_comment;

	my $cmp_title;
	my $crl_name;
	my $crt_name;

	$column_number = 0;
	$sth->bind_col(++$column_number, \$art_id,   undef);
	$sth->bind_col(++$column_number, \$cdi_id,   undef);
	$sth->bind_col(++$column_number, \$cdi_name,   undef);
	$sth->bind_col(++$column_number, \$cmp_abbr,   undef);
	$sth->bind_col(++$column_number, \$cmp_length,   undef);
	$sth->bind_col(++$column_number, \$cm_entry,   undef);
	$sth->bind_col(++$column_number, \$art_name,   undef);
	$sth->bind_col(++$column_number, \$art_ext,   undef);
	$sth->bind_col(++$column_number, \$art_timestamp,   undef);
	$sth->bind_col(++$column_number, \$art_timestamp_epoch,   undef);

#	$sth->bind_col(++$column_number, \$art_nsn,   undef);
	$sth->bind_col(++$column_number, \$art_mirroring,   undef);
	$sth->bind_col(++$column_number, \$art_comment,   undef);
	$sth->bind_col(++$column_number, \$art_delcause,   undef);
	$sth->bind_col(++$column_number, \$art_entry,   undef);
	$sth->bind_col(++$column_number, \$art_modified,   undef);

	$sth->bind_col(++$column_number, \$prefix_char,   undef);
	$sth->bind_col(++$column_number, \$art_serial,   undef);
	$sth->bind_col(++$column_number, \$art_md5,   undef);
	$sth->bind_col(++$column_number, \$art_data_size,   undef);
	$sth->bind_col(++$column_number, \$art_xmin,   undef);
	$sth->bind_col(++$column_number, \$art_xmax,   undef);
	$sth->bind_col(++$column_number, \$art_ymin,   undef);
	$sth->bind_col(++$column_number, \$art_ymax,   undef);
	$sth->bind_col(++$column_number, \$art_zmin,   undef);
	$sth->bind_col(++$column_number, \$art_zmax,   undef);
	$sth->bind_col(++$column_number, \$art_volume,   undef);
#	$sth->bind_col(++$column_number, \$art_cube_volume,   undef);
	$sth->bind_col(++$column_number, \$art_category,   undef);
	$sth->bind_col(++$column_number, \$art_judge,   undef);
	$sth->bind_col(++$column_number, \$art_class,   undef);
	$sth->bind_col(++$column_number, \$arto_id,   undef);
	$sth->bind_col(++$column_number, \$arto_comment,   undef);

	$sth->bind_col(++$column_number, \$cmp_title,   undef);

	my $sth_data = $dbh->prepare(qq|select art_data from art_file where art_id=? order by art_serial desc NULLS FIRST limit 1|) or die $dbh->errstr;
	my $sth_data_raw = $dbh->prepare(qq|select art_raw_data,art_raw_data_size from art_file where art_id=? order by art_serial desc NULLS FIRST limit 1|) or die $dbh->errstr;

	my $sth_group_folder = $dbh->prepare(qq|
select
 COALESCE(artf.artf_id,0) as artf_id,
 artf.artf_pid,
 COALESCE(artf.artf_name,'') as artf_name
from
 art_folder_file as artff
left join (
  select artf_id,artf_pid,artf_name from art_folder
) as artf on artf.artf_id=artff.artf_id
where
 artff.art_id=?
|) or die $dbh->errstr;

	my $sth_folder = $dbh->prepare(qq|select COALESCE(artf.artf_id,0) as artf_id,artf.artf_pid,COALESCE(artf.artf_name,'') as artf_name from art_folder as artf where COALESCE(artf.artf_id,0)=?|) or die $dbh->errstr;

#	my $header = qq|#FJID	FMA_ID	PART	MAP_DATE	FILENAME	FILE_DATE|;
	my @header_arr = qw|
FJID
FMA_ID
MAP_Timestamp
OBJ_Filename
OBJ_Timestamp

Comment
Category
Judge
Class
Xmin
Xmax
Ymin
Ymax
Zmin
Zmax
Volume
Size

art_entry
art_modified
prefix_char
art_serial
art_md5
arto_id

art_folder

SubClass
|;

	my $header = '#'.join("\t",map {$_ =~ /^[a-z]/ ? uc($_) : $_} @header_arr);

#	&utf8::decode($header) unless(&utf8::is_utf8($header));
	$header = &cgi_lib::common::decodeUTF8($header);

	($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime();
	my $timestamp = sprintf("%04d/%02d/%02d %02d:%02d:%02d", $year+1900,$month+1,$mday,$hour,$min,$sec);

	my $OUT;
	open($OUT,"> $file_name") or die "$! [$file_name]";

	&utf8::encode($timestamp) if(&utf8::is_utf8($timestamp));
	my $s = qq|#Export Date:$timestamp|;
	&utf8::decode($s) unless(&utf8::is_utf8($s));
	print $OUT &Encode::encode($CODE,$s).$LF;

	print $OUT &Encode::encode($CODE,$header).$LF;

	my $zip = Archive::Zip->new();

	my %OUTPUT_ART_ID;
	my %ORG_ART_ID;
	while($sth->fetch){

		next unless(defined $art_id && defined $cdi_name);

		my $current_use;
		if(defined $cdi_id && defined $art_id && defined $CDI_MAP_ART_DATE && ref $CDI_MAP_ART_DATE eq 'HASH' && exists $CDI_MAP_ART_DATE->{$cdi_id} && defined $CDI_MAP_ART_DATE->{$cdi_id} && ref $CDI_MAP_ART_DATE->{$cdi_id} eq 'HASH' && exists $CDI_MAP_ART_DATE->{$cdi_id}->{$art_id}){
			$current_use = JSON::XS::true;	#子供のOBJより古くない場合
		}else{
			$current_use = JSON::XS::false;
		}
		if(defined $cdi_id && $current_use == JSON::XS::true && defined $CDI_MAP_SUM_VOLUME_DEL_ID && exists $CDI_MAP_SUM_VOLUME_DEL_ID->{$cdi_id}){
			$current_use = JSON::XS::false;	#子供のOBJが親のボリュームの90%より多い場合
		}
		next if($current_use == JSON::XS::false);

		my $art_filename = qq|$art_id$art_ext|;
		my $art_file_path = &catfile($art_file_base_path,$art_filename);
		my $out_art_file_path = &catfile($out_path,$art_filename);

		my($size,$timestamp) = (0,0);
		($size,$timestamp) = (stat($art_file_path))[7,9] if(-e $art_file_path && -f $art_file_path && -s $art_file_path);

		unless($art_data_size==$size && $art_timestamp_epoch==$timestamp){
			my $art_data;
			$sth_data->execute($art_id) or die $dbh->errstr;
			$sth_data->bind_col(1, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
			$sth_data->fetch;
			$sth_data->finish;
			if(defined $art_data && open(my $OBJ,"> $art_file_path")){
				flock($OBJ,2);
				binmode($OBJ,':utf8');
				print $OBJ $art_data;
				close($OBJ);
				undef $OBJ;
			}
			undef $art_data;
			utime $art_timestamp_epoch,$art_timestamp_epoch,$art_file_path;
		}
		&File::Copy::copy($art_file_path,$out_art_file_path);
		next unless(-e $out_art_file_path && -f $out_art_file_path && -s $out_art_file_path);

		utime $art_timestamp_epoch,$art_timestamp_epoch,$out_art_file_path;


		my $art_filename_raw = qq|${art_id}_raw${art_ext}|;
		my $out_art_file_path_raw = &catfile($out_path,$art_filename_raw);
		unless(-e $out_art_file_path_raw && -f $out_art_file_path_raw && -s $out_art_file_path_raw){
			my $art_raw_data;
			my $art_raw_data_size;
			$sth_data_raw->execute($art_id) or die $dbh->errstr;
			$sth_data_raw->bind_col(1, \$art_raw_data, { pg_type => DBD::Pg::PG_BYTEA });
			$sth_data_raw->bind_col(2, \$art_raw_data_size, undef);
			$sth_data_raw->fetch;
			$sth_data_raw->finish;
			unless($art_data_size==$art_raw_data_size){
				if(defined $art_raw_data && open(my $OBJ,"> $out_art_file_path_raw")){
					flock($OBJ,2);
					binmode($OBJ,':utf8');
					print $OBJ $art_raw_data;
					close($OBJ);
					undef $OBJ;
				}
				undef $art_raw_data;
				undef $art_raw_data_size;
				next unless(-e $out_art_file_path_raw && -f $out_art_file_path_raw && -s $out_art_file_path_raw);
				utime $art_timestamp_epoch,$art_timestamp_epoch,$out_art_file_path_raw;
			}
			undef $art_raw_data;
			undef $art_raw_data_size;
		}


		$cmp_length = 0 unless(defined $cmp_length);
		$cmp_length -= 0;

		my @ART_FOLDER;
		$sth_group_folder->execute($art_id) or die $dbh->errstr;
		my $artf_id;
		my $artf_pid;
		my $artf_name;
		$column_number = 0;
		$sth_group_folder->bind_col(++$column_number, \$artf_id,   undef);
		$sth_group_folder->bind_col(++$column_number, \$artf_pid,   undef);
		$sth_group_folder->bind_col(++$column_number, \$artf_name,   undef);
		$sth_group_folder->fetch;
		$sth_group_folder->finish;
		unshift(@ART_FOLDER,$artf_name);
		while(defined $artf_pid){
			$sth_folder->execute($artf_pid) or die $dbh->errstr;
			$column_number = 0;
			$sth_folder->bind_col(++$column_number, \$artf_id,   undef);
			$sth_folder->bind_col(++$column_number, \$artf_pid,   undef);
			$sth_folder->bind_col(++$column_number, \$artf_name,   undef);
			$sth_folder->fetch;
			$sth_folder->finish;
			unshift(@ART_FOLDER,$artf_name);
		}

		if(defined $art_name && length $art_name){
			my($name,$dir,$ext) = &File::Basename::fileparse($art_name,qw|.obj|);
			$art_name = $name;
		}
		if(defined $arto_id && length $arto_id){
			my $HASH = {
				arto_id => $arto_id,
				arto_comment => $arto_comment,
			};
			$arto_id = &cgi_lib::common::encodeJSON($HASH);
		}

		my @t;
		push(@t,$art_id);
		push(@t,$cmp_length ? "$cdi_name-$cmp_abbr" : $cdi_name);
		push(@t,$cm_entry);
		push(@t,qq|$art_name$art_ext|);
		push(@t,$art_timestamp);

		push(@t,$art_comment);
		push(@t,$art_category);
		push(@t,$art_judge);
		push(@t,$art_class);
		push(@t,$art_xmin);
		push(@t,$art_xmax);
		push(@t,$art_ymin);
		push(@t,$art_ymax);
		push(@t,$art_zmin);
		push(@t,$art_zmax);
		push(@t,$art_volume);
		push(@t,$art_data_size);

#		push(@t,$art_nsn);
		push(@t,$art_entry);
		push(@t,$art_modified);
		push(@t,$prefix_char);
		push(@t,$art_serial);
		push(@t,$art_md5);
#		push(@t,$art_cube_volume);
		push(@t,$arto_id);
#		push(@t,$arto_comment);

		push(@t,'/'.join('/',@ART_FOLDER));

		push(@t,$cmp_title);
#		push(@t,$crl_name);
#		push(@t,$crt_name);

		my $o = join("\t",map {defined $_ ? $_ : ''} @t);
		&utf8::decode($o) unless(&utf8::is_utf8($o));
		print $OUT &Encode::encode($CODE,$o).$LF;

		$zip->addFile(&cgi_lib::common::encodeUTF8($out_art_file_path),&cgi_lib::common::encodeUTF8($art_filename));
		$zip->addFile(&cgi_lib::common::encodeUTF8($out_art_file_path_raw),&cgi_lib::common::encodeUTF8($art_filename_raw)) if(-e $out_art_file_path_raw && -f $out_art_file_path_raw && -s $out_art_file_path_raw);

		$OUTPUT_ART_ID{$art_id} = undef;

		if($art_mirroring){
			if($art_id =~ /^([A-Z]+[0-9]+)M$/){
				my $org_art_id = $1;
				$ORG_ART_ID{$org_art_id} = undef;
			}else{
				die "Unknown Mrror ID [$art_id]";
			}
		}
	}
	$sth->finish;
	undef $sth;
	undef %OUTPUT_ART_ID;
	undef %ORG_ART_ID;

	close($OUT);

	$zip->addFile(&cgi_lib::common::encodeUTF8($file_name),&cgi_lib::common::encodeUTF8(&File::Basename::basename($file_name)));




	@header_arr = qw|
SubClass
SubClassAbbr
SubClassDisplay
SubClassPrefix
SubClassLogic
|;
	$header = '#'.join("\t",map {$_ =~ /^[a-z]/ ? uc($_) : $_} @header_arr);

	$file_name = &catdir($out_path,'concept_art_map_part.txt');
	open($OUT,"> $file_name") or die "$! [$file_name]";
	print $OUT &Encode::encode($CODE,$s).$LF;
	print $OUT &Encode::encode($CODE,$header).$LF;

	$sql=<<SQL;
select
 cmp.cmp_title,
 cmp.cmp_abbr,
 cmp.cmp_display_title,
 cmp.cmp_prefix,
 crl.crl_name
from
 concept_art_map_part as cmp

left join (
 select * from concept_relation_logic
) as crl on crl.crl_id=cmp.crl_id

SQL
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$column_number = 0;
	my $cmp_display_title;
	my $cmp_prefix;
	$sth->bind_col(++$column_number, \$cmp_title,   undef);
	$sth->bind_col(++$column_number, \$cmp_abbr,   undef);
	$sth->bind_col(++$column_number, \$cmp_display_title,   undef);
	$sth->bind_col(++$column_number, \$cmp_prefix,   undef);
	$sth->bind_col(++$column_number, \$crl_name,   undef);
	while($sth->fetch){
		my @t;
		push(@t,$cmp_title);
		push(@t,$cmp_abbr);
		push(@t,$cmp_display_title);
		push(@t,$cmp_prefix);
		push(@t,$crl_name);
		my $o = join("\t",map {defined $_ ? $_ : ''} @t);
		&utf8::decode($o) unless(&utf8::is_utf8($o));
		print $OUT &Encode::encode($CODE,$o).$LF;
	}
	$sth->finish;
	undef $sth;
	close($OUT);
	$zip->addFile(&cgi_lib::common::encodeUTF8($file_name),&cgi_lib::common::encodeUTF8(&File::Basename::basename($file_name)));

	return $zip;
}
1;
