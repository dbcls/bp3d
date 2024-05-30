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
use DBD::Pg;

use BITS::ConceptArtMapModified;
use BITS::ConceptArtMapPart;

use constant {
	EXPORT_FORMAT_VERSION => '201903xx',
};

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
	my $LOG = shift;

	my $md_id = $FORM->{'md_id'};
	my $mv_id = $FORM->{'mv_id'};
	my $ci_id = $FORM->{'ci_id'};
	my $cb_id = $FORM->{'cb_id'};
=pod
	my($ELEMENT, $COMP_DENSITY_USE_TERMS, $COMP_DENSITY_END_TERMS, $COMP_DENSITY, $CDI_MAP, $CDI_MAP_ART_DATE, $CDI_ID2CID, $CDI_MAP_SUM_VOLUME_DEL_ID) = &BITS::ConceptArtMapModified::calcElementAndDensity(
		dbh     => $dbh,
		md_id   => $md_id,
		mv_id   => $mv_id,
		ci_id   => $ci_id,
		cb_id   => $cb_id
	);
=cut
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

	my $sql;
	my $sth;
	my $cdi_id;
	my $cdi_name;
	my $cti_pids;
	my $cdi_name_e;
	my $cdi_syn_e;

	$sql=<<SQL;
select
 cm.art_id,
 COALESCE(arti.artc_id,''),
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

 cmp2.cmp_title,
 COALESCE(cp.cp_title,''),
 COALESCE(cl.cl_title,''),
 COALESCE(artl.artl_title,''),

 COALESCE(cdi_parent.cdi_name,''),
 COALESCE(cdi_super.cdi_name,''),

 COALESCE(crl.crl_name,'')

from
 concept_art_map as cm

left join concept_data_info as cdi on cdi.ci_id=cm.ci_id and cdi.cdi_id=cm.cdi_id

left join concept_data_info as cdi_parent on cdi_parent.ci_id=cdi.ci_id and cdi_parent.cdi_id=cdi.cdi_pid

left join concept_data_info as cdi_super  on cdi_super.ci_id=cdi.ci_id  and cdi_super.cdi_id=cdi.cdi_super_id

left join art_file_info as arti on arti.art_id=cm.art_id

left join (
  select
   cmp_id,
   cmp_abbr
  from
   concept_art_map_part
  where
   cmp_delcause is null
) as cmp on cmp.cmp_id=cm.cmp_id

left join id_prefix as prefix on prefix.prefix_id=arti.prefix_id


left join concept_art_map_part as cmp2 on cmp2.cmp_id=cdi.cmp_id

left join concept_part as cp on cp.cp_id=cdi.cp_id

left join concept_laterality as cl on cl.cl_id=cdi.cl_id

left join art_laterality as artl on artl.artl_id=arti.artl_id

left join concept_relation_logic as crl on crl.crl_id=cp.crl_id

where
 cm.cm_use and
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

	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;

	my $art_id;
	my $artc_id;
#	my $cdi_id;
#	my $cdi_name;
#	my $cdi_name_e;
#	my $cdi_syn_e;
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
	my $cp_title;
	my $cp_abbr;
	my $cl_title;
	my $cl_abbr;
	my $artl_title;
	my $crl_name;
	my $crt_name;

	my $cdi_parent_name;
	my $cdi_parent_name_e;
	my $cdi_parent_syn_e;
	my $cdi_super_name;
	my $cdi_super_name_e;
	my $cdi_super_syn_e;

	$column_number = 0;
	$sth->bind_col(++$column_number, \$art_id,        undef);
	$sth->bind_col(++$column_number, \$artc_id,       undef);
	$sth->bind_col(++$column_number, \$cdi_id,        undef);
	$sth->bind_col(++$column_number, \$cdi_name,      undef);
	$sth->bind_col(++$column_number, \$cmp_abbr,      undef);
	$sth->bind_col(++$column_number, \$cmp_length,    undef);
	$sth->bind_col(++$column_number, \$cm_entry,      undef);
	$sth->bind_col(++$column_number, \$art_name,      undef);
	$sth->bind_col(++$column_number, \$art_ext,       undef);
	$sth->bind_col(++$column_number, \$art_timestamp, undef);
	$sth->bind_col(++$column_number, \$art_timestamp_epoch, undef);

#	$sth->bind_col(++$column_number, \$art_nsn,   undef);
	$sth->bind_col(++$column_number, \$art_mirroring, undef);
	$sth->bind_col(++$column_number, \$art_comment,   undef);
	$sth->bind_col(++$column_number, \$art_delcause,  undef);
	$sth->bind_col(++$column_number, \$art_entry,     undef);
	$sth->bind_col(++$column_number, \$art_modified,  undef);

	$sth->bind_col(++$column_number, \$prefix_char,   undef);
	$sth->bind_col(++$column_number, \$art_serial,    undef);
	$sth->bind_col(++$column_number, \$art_md5,       undef);
	$sth->bind_col(++$column_number, \$art_data_size, undef);
	$sth->bind_col(++$column_number, \$art_xmin,      undef);
	$sth->bind_col(++$column_number, \$art_xmax,      undef);
	$sth->bind_col(++$column_number, \$art_ymin,      undef);
	$sth->bind_col(++$column_number, \$art_ymax,      undef);
	$sth->bind_col(++$column_number, \$art_zmin,      undef);
	$sth->bind_col(++$column_number, \$art_zmax,      undef);
	$sth->bind_col(++$column_number, \$art_volume,    undef);
#	$sth->bind_col(++$column_number, \$art_cube_volume,   undef);
	$sth->bind_col(++$column_number, \$art_category,  undef);
	$sth->bind_col(++$column_number, \$art_judge,     undef);
	$sth->bind_col(++$column_number, \$art_class,     undef);
	$sth->bind_col(++$column_number, \$arto_id,       undef);
	$sth->bind_col(++$column_number, \$arto_comment,  undef);

	$sth->bind_col(++$column_number, \$cmp_title,     undef);
	$sth->bind_col(++$column_number, \$cp_title,      undef);
	$sth->bind_col(++$column_number, \$cl_title,      undef);
	$sth->bind_col(++$column_number, \$artl_title,    undef);

	$sth->bind_col(++$column_number, \$cdi_parent_name, undef);
	$sth->bind_col(++$column_number, \$cdi_super_name,  undef);

	$sth->bind_col(++$column_number, \$crl_name,   undef);

#	$sth->bind_col(++$column_number, \$cdi_name_e,  undef);
#	$sth->bind_col(++$column_number, \$cdi_syn_e,   undef);

#	$sth->bind_col(++$column_number, \$cdi_parent_name_e,  undef);
#	$sth->bind_col(++$column_number, \$cdi_parent_syn_e,   undef);

#	$sth->bind_col(++$column_number, \$cdi_super_name_e,  undef);
#	$sth->bind_col(++$column_number, \$cdi_super_syn_e,   undef);

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
OBJID
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

SubPart
Laterality
OBJ_Laterality

FMA_ID_Parent
FMA_ID_Super

SubPartLogic
|;

	my $header = '#'.join("\t",map {$_ =~ /^[a-z]/ ? uc($_) : $_} @header_arr);

#	&utf8::decode($header) unless(&utf8::is_utf8($header));
	$header = &cgi_lib::common::decodeUTF8($header);

	($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime();
	my $timestamp = sprintf("%04d/%02d/%02d %02d:%02d:%02d", $year+1900,$month+1,$mday,$hour,$min,$sec);

	my $OUT;
	open($OUT,"> $file_name") or die "$! [$file_name]";

	&utf8::encode($timestamp) if(&utf8::is_utf8($timestamp));
#	my $s = qq|#Export Date:$timestamp|;
#	&utf8::decode($s) unless(&utf8::is_utf8($s));
	my $export_date = &Encode::encode($CODE,&cgi_lib::common::decodeUTF8(qq|#Export Date:$timestamp|)).$LF;
	my $version = &Encode::encode($CODE,&cgi_lib::common::decodeUTF8(sprintf(qq|#Version:%s|, EXPORT_FORMAT_VERSION))).$LF;

	print $OUT $export_date;
	print $OUT $version;

	print $OUT &Encode::encode($CODE,$header).$LF;

	my $zip = Archive::Zip->new();

	my %OUTPUT_ART_ID;
	my %ORG_ART_ID;
	while($sth->fetch){

		next unless(defined $art_id && defined $cdi_name);

#		say $LOG sprintf("%s:%d:%s:%s",__PACKAGE__,__LINE__,$art_id,$cdi_name) if(defined $LOG);
=pod
		my $current_use;
		if(defined $cdi_id && defined $art_id && defined $CDI_MAP_ART_DATE && ref $CDI_MAP_ART_DATE eq 'HASH' && exists $CDI_MAP_ART_DATE->{$cdi_id} && defined $CDI_MAP_ART_DATE->{$cdi_id} && ref $CDI_MAP_ART_DATE->{$cdi_id} eq 'HASH' && exists $CDI_MAP_ART_DATE->{$cdi_id}->{$art_id}){
			$current_use = JSON::XS::true;	#子供のOBJより古くない場合
		}else{
			$current_use = JSON::XS::false;
		}
		if($current_use == JSON::XS::false){
			say $LOG sprintf("%s:%d:%s:%s",__PACKAGE__,__LINE__,$art_id,$cdi_name) if(defined $LOG);
			next;
		}
		if(defined $cdi_id && $current_use == JSON::XS::true && defined $CDI_MAP_SUM_VOLUME_DEL_ID && exists $CDI_MAP_SUM_VOLUME_DEL_ID->{$cdi_id}){
			$current_use = JSON::XS::false;	#子供のOBJが親のボリュームの90%より多い場合
		}
		if($current_use == JSON::XS::false){
			say $LOG sprintf("%s:%d:%s:%s",__PACKAGE__,__LINE__,$art_id,$cdi_name) if(defined $LOG);
			next;
		}
=cut
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
#		say $LOG sprintf("%s:%d:%s",__PACKAGE__,__LINE__,$out_art_file_path_raw) if(defined $LOG);
		unless(-e $out_art_file_path_raw && -f $out_art_file_path_raw && -s $out_art_file_path_raw){
#			say $LOG sprintf("%s:%d:%s",__PACKAGE__,__LINE__,$art_id) if(defined $LOG);
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
		push(@t,$artc_id);

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

#		push(@t,$cmp_title);

		push(@t,$cp_title);
		push(@t,$cl_title);
		push(@t,$artl_title);

		push(@t,$cdi_parent_name);
		push(@t,$cdi_super_name);

		push(@t,$crl_name);

#		push(@t,$cdi_name_e);
#		push(@t,$cdi_syn_e);

#		push(@t,$cdi_parent_name_e);
#		push(@t,$cdi_parent_syn_e);

#		push(@t,$cdi_super_name_e);
#		push(@t,$cdi_super_syn_e);

#		push(@t,$crl_name);
#		push(@t,$crt_name);

		my $o = join("\t",map {defined $_ ? $_ : ''} @t);
		&utf8::decode($o) unless(&utf8::is_utf8($o));
		print $OUT &Encode::encode($CODE,$o).$LF;

		$zip->addFile(&cgi_lib::common::encodeUTF8($out_art_file_path),&cgi_lib::common::encodeUTF8($art_filename));
		$zip->addFile(&cgi_lib::common::encodeUTF8($out_art_file_path_raw),&cgi_lib::common::encodeUTF8($art_filename_raw)) if(-e $out_art_file_path_raw && -f $out_art_file_path_raw && -s $out_art_file_path_raw);

		$OUTPUT_ART_ID{$art_id} = undef;

#		if($art_mirroring){
#			if($art_id =~ /^([A-Z]+[0-9]+)M$/){
#				my $org_art_id = $1;
#				$ORG_ART_ID{$org_art_id} = undef;
#			}else{
#				die "Unknown Mrror ID [$art_id]";
#			}
#		}
	}
	$sth->finish;
	undef $sth;
	undef %OUTPUT_ART_ID;
	undef %ORG_ART_ID;

	close($OUT);

	$zip->addFile(&cgi_lib::common::encodeUTF8($file_name),&cgi_lib::common::encodeUTF8(&File::Basename::basename($file_name)));



#=pod
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
	print $OUT $export_date;
	print $OUT $version;
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

order by
 cmp.cmp_order
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
#=cut

	@header_arr = qw|
SubPart
SubPartAbbr
SubPartDisplay
SubPartPrefix
SubPartLogic
|;
	$header = '#'.join("\t",map {$_ =~ /^[a-z]/ ? uc($_) : $_} @header_arr);

	$file_name = &catdir($out_path,'concept_part.txt');
	open($OUT,"> $file_name") or die "$! [$file_name]";
	print $OUT $export_date;
	print $OUT $version;
	print $OUT &Encode::encode($CODE,$header).$LF;

	$sql=<<SQL;
select
 cp.cp_title,
 cp.cp_abbr,
 cp.cp_display_title,
 cp.cp_prefix,
 crl.crl_name
from
 concept_part as cp

left join (
 select * from concept_relation_logic
) as crl on crl.crl_id=cp.crl_id

order by
 cp.cp_order

SQL
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$column_number = 0;
	my $cp_display_title;
	my $cp_prefix;
	$sth->bind_col(++$column_number, \$cp_title,   undef);
	$sth->bind_col(++$column_number, \$cp_abbr,   undef);
	$sth->bind_col(++$column_number, \$cp_display_title,   undef);
	$sth->bind_col(++$column_number, \$cp_prefix,   undef);
	$sth->bind_col(++$column_number, \$crl_name,   undef);
	while($sth->fetch){
		my @t;
		push(@t,$cp_title);
		push(@t,$cp_abbr);
		push(@t,$cp_display_title);
		push(@t,$cp_prefix);
		push(@t,$crl_name);
		my $o = join("\t",map {defined $_ ? $_ : ''} @t);
		&utf8::decode($o) unless(&utf8::is_utf8($o));
		print $OUT &Encode::encode($CODE,$o).$LF;
	}
	$sth->finish;
	undef $sth;
	close($OUT);
	$zip->addFile(&cgi_lib::common::encodeUTF8($file_name),&cgi_lib::common::encodeUTF8(&File::Basename::basename($file_name)));


	@header_arr = qw|
Laterality
LateralityAbbr
LateralityDisplay
LateralityPrefix
|;
	$header = '#'.join("\t",map {$_ =~ /^[a-z]/ ? uc($_) : $_} @header_arr);

	$file_name = &catdir($out_path,'concept_laterality.txt');
	open($OUT,"> $file_name") or die "$! [$file_name]";
	print $OUT $export_date;
	print $OUT $version;
	print $OUT &Encode::encode($CODE,$header).$LF;

	$sql=<<SQL;
select
 cl.cl_title,
 cl.cl_abbr,
 cl.cl_display_title,
 cl.cl_prefix
from
 concept_laterality as cl
order by
 cl.cl_order
SQL
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$column_number = 0;
	my $cl_display_title;
	my $cl_prefix;
	$sth->bind_col(++$column_number, \$cl_title,   undef);
	$sth->bind_col(++$column_number, \$cl_abbr,   undef);
	$sth->bind_col(++$column_number, \$cl_display_title,   undef);
	$sth->bind_col(++$column_number, \$cl_prefix,   undef);
	while($sth->fetch){
		my @t;
		push(@t,$cl_title);
		push(@t,$cl_abbr);
		push(@t,$cl_display_title);
		push(@t,$cl_prefix);
		my $o = join("\t",map {defined $_ ? $_ : ''} @t);
		&utf8::decode($o) unless(&utf8::is_utf8($o));
		print $OUT &Encode::encode($CODE,$o).$LF;
	}
	$sth->finish;
	undef $sth;
	close($OUT);
	$zip->addFile(&cgi_lib::common::encodeUTF8($file_name),&cgi_lib::common::encodeUTF8(&File::Basename::basename($file_name)));



	@header_arr = qw|
OBJ_Laterality
OBJ_LateralityAbbr
OBJ_LateralityDisplay
OBJ_LateralityPrefix
|;
	$header = '#'.join("\t",map {$_ =~ /^[a-z]/ ? uc($_) : $_} @header_arr);

	$file_name = &catdir($out_path,'art_laterality.txt');
	open($OUT,"> $file_name") or die "$! [$file_name]";
	print $OUT $export_date;
	print $OUT $version;
	print $OUT &Encode::encode($CODE,$header).$LF;

	$sql=<<SQL;
select
 artl.artl_title,
 artl.artl_abbr,
 artl.artl_display_title,
 artl.artl_prefix
from
 art_laterality as artl
order by
 artl.artl_order
SQL
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$column_number = 0;
	my $artl_abbr;
	my $artl_display_title;
	my $artl_prefix;
	$sth->bind_col(++$column_number, \$artl_title,   undef);
	$sth->bind_col(++$column_number, \$artl_abbr,   undef);
	$sth->bind_col(++$column_number, \$artl_display_title,   undef);
	$sth->bind_col(++$column_number, \$artl_prefix,   undef);
	while($sth->fetch){
		my @t;
		push(@t,$artl_title);
		push(@t,$artl_abbr);
		push(@t,$artl_display_title);
		push(@t,$artl_prefix);
		my $o = join("\t",map {defined $_ ? $_ : ''} @t);
		&utf8::decode($o) unless(&utf8::is_utf8($o));
		print $OUT &Encode::encode($CODE,$o).$LF;
	}
	$sth->finish;
	undef $sth;
	close($OUT);
	$zip->addFile(&cgi_lib::common::encodeUTF8($file_name),&cgi_lib::common::encodeUTF8(&File::Basename::basename($file_name)));

#	say $LOG sprintf("%s:%d:%s",__PACKAGE__,__LINE__,'END') if(defined $LOG);



	@header_arr = qw|
SegmentName
SegmentColor
SegmentThumbnailBackgroundColor
SegmentThumbnailBorderColor
SegmentThumbnailForegroundColor
SegmentGroupName
FMA_IDs
cdf_name
|;
	$header = '#'.join("\t",map {$_ =~ /^[a-z]/ ? uc($_) : $_} @header_arr);

	$file_name = &catdir($out_path,'concept_segment.txt');
	open($OUT,"> $file_name") or die "$! [$file_name]";
	print $OUT $export_date;
	print $OUT $version;
	print $OUT &Encode::encode($CODE,$header).$LF;

	my $CDI_HASH;
	$sql=<<SQL;
SELECT
  cdi.cdi_id
 ,cdi.cdi_name
FROM
 concept_data_info AS cdi
WHERE
 cdi.ci_id=$ci_id
SQL
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;

	$column_number = 0;
	$sth->bind_col(++$column_number, \$cdi_id,        undef);
	$sth->bind_col(++$column_number, \$cdi_name,      undef);
	while($sth->fetch){
		$CDI_HASH->{$cdi_id} = $cdi_name;
	}
	$sth->finish;
	undef $sth;

	$sql=<<SQL;
SELECT
  sg.seg_name
 ,sg.seg_color
 ,sg.seg_thum_bgcolor
 ,sg.seg_thum_bocolor
 ,sg.seg_thum_fgcolor
 ,sg.cdi_ids
 ,sgg.csg_name
 ,sg.cdf_name
FROM
 concept_segment AS sg
LEFT JOIN concept_segment_group AS sgg ON sgg.csg_id=sg.csg_id
SQL
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$column_number = 0;
	my $seg_name;
	my $seg_color;
	my $seg_thum_bgcolor;
	my $seg_thum_bocolor;
	my $seg_thum_fgcolor;
	my $cdi_ids;
	my $csg_name;
	my $cdf_name;
	$sth->bind_col(++$column_number, \$seg_name,         undef);
	$sth->bind_col(++$column_number, \$seg_color,        undef);
	$sth->bind_col(++$column_number, \$seg_thum_bgcolor, undef);
	$sth->bind_col(++$column_number, \$seg_thum_bocolor, undef);
	$sth->bind_col(++$column_number, \$seg_thum_fgcolor, undef);
	$sth->bind_col(++$column_number, \$cdi_ids,          undef);
	$sth->bind_col(++$column_number, \$csg_name,         undef);
	$sth->bind_col(++$column_number, \$cdf_name,         undef);
	while($sth->fetch){
		if(defined $cdi_ids && length $cdi_ids){
			my $cdi_ids_arr = &cgi_lib::common::decodeJSON($cdi_ids);
			if(defined $cdi_ids_arr && ref $cdi_ids_arr eq 'ARRAY'){
				my $temp_arr = [map {$CDI_HASH->{$_}} grep { exists $CDI_HASH->{$_} && defined $CDI_HASH->{$_} } @{$cdi_ids_arr}];
				$cdi_ids = &cgi_lib::common::decodeUTF8(&cgi_lib::common::encodeJSON($temp_arr)) if(defined $temp_arr && ref $temp_arr eq 'ARRAY' && scalar @{$temp_arr});
			}
		}
		my @t;
		push(@t,$seg_name);
		push(@t,$seg_color);
		push(@t,$seg_thum_bgcolor);
		push(@t,$seg_thum_bocolor);
		push(@t,$seg_thum_fgcolor);
		push(@t,$csg_name);
		push(@t,$cdi_ids);
		push(@t,$cdf_name);
		my $o = join("\t",map {defined $_ ? $_ : ''} @t);
		&utf8::decode($o) unless(&utf8::is_utf8($o));
		print $OUT &Encode::encode($CODE,$o).$LF;
	}
	$sth->finish;
	undef $sth;
	close($OUT);
	$zip->addFile(&cgi_lib::common::encodeUTF8($file_name),&cgi_lib::common::encodeUTF8(&File::Basename::basename($file_name)));




	@header_arr = qw|
FMA_ID
FMA_NAME
FMA_SYNONYM
SegmentName
isUserData
SubClass
SubPart
Laterality
FMA_ID_Parent
FMA_ID_Super
|;
	$header = '#'.join("\t",map {$_ =~ /^[a-z]/ ? uc($_) : $_} @header_arr);

	$file_name = &catdir($out_path,'concept_data.txt');
	open($OUT,"> $file_name") or die "$! [$file_name]";
	print $OUT $export_date;
	print $OUT $version;
	print $OUT &Encode::encode($CODE,$header).$LF;

=pod
	my $CDI_HASH;
	$sql=<<SQL;
select
 cdi.cdi_id,
 cdi.cdi_name
from
 concept_data_info as cdi
where
 cdi.ci_id=$ci_id
SQL
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;

	$column_number = 0;
	$sth->bind_col(++$column_number, \$cdi_id,        undef);
	$sth->bind_col(++$column_number, \$cdi_name,      undef);
	while($sth->fetch){
		$CDI_HASH->{$cdi_id} = $cdi_name;
	}
	$sth->finish;
	undef $sth;
=cut

#	my $seg_name;
	my $is_user_data;
	my $cdi_pid;
	my $cdi_sid;
	$sql=<<SQL;
select
 cdi.cdi_name,
 COALESCE(cd.cd_name, ''),
 COALESCE(cd.cd_syn, ''),
 COALESCE(seg.seg_name, ''),
 cdi.is_user_data,
 cmp.cmp_title,
 cp.cp_title,
 cl.cl_title,
 cdi.cdi_pid,
 cdi.cdi_super_id
from
 concept_data as cd
left join concept_data_info as cdi on cdi.ci_id=cd.ci_id and cdi.cdi_id=cd.cdi_id
left join concept_segment as seg on seg.seg_id=cd.seg_id
left join concept_art_map_part as cmp on cmp.cmp_id=cdi.cmp_id
left join concept_part as cp on cp.cp_id=cdi.cp_id
left join concept_laterality as cl on cl.cl_id=cdi.cl_id
where
 cd.ci_id=$ci_id and cd.cb_id=$cb_id and
 cdi.cdi_name is not null
order by
 cdi.cdi_name
SQL
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;

	$column_number = 0;
	$sth->bind_col(++$column_number, \$cdi_name,     undef);
	$sth->bind_col(++$column_number, \$cdi_name_e,   undef);
	$sth->bind_col(++$column_number, \$cdi_syn_e,    undef);
	$sth->bind_col(++$column_number, \$seg_name,     undef);
	$sth->bind_col(++$column_number, \$is_user_data, undef);
	$sth->bind_col(++$column_number, \$cmp_title,    undef);
	$sth->bind_col(++$column_number, \$cp_title,     undef);
	$sth->bind_col(++$column_number, \$cl_title,     undef);
	$sth->bind_col(++$column_number, \$cdi_pid,      undef);
	$sth->bind_col(++$column_number, \$cdi_sid,      undef);

	while($sth->fetch){
		my $cdi_pname = '';
		my $cdi_sname = '';
		if(defined $CDI_HASH && ref $CDI_HASH eq 'HASH'){
			$cdi_pname =  $CDI_HASH->{$cdi_pid} if(defined $cdi_pid && exists $CDI_HASH->{$cdi_pid} && defined $CDI_HASH->{$cdi_pid});
			$cdi_sname =  $CDI_HASH->{$cdi_sid} if(defined $cdi_sid && exists $CDI_HASH->{$cdi_sid} && defined $CDI_HASH->{$cdi_sid});
		}
		my @t;
		push(@t,$cdi_name);
		push(@t,$cdi_name_e);
		push(@t,$cdi_syn_e);
		push(@t,$seg_name);
		push(@t,$is_user_data);
		push(@t,$cmp_title);
		push(@t,$cp_title);
		push(@t,$cl_title);
		push(@t,$cdi_pname);
		push(@t,$cdi_sname);
		my $o = join("\t",map {defined $_ ? $_ : ''} @t);
		&utf8::decode($o) unless(&utf8::is_utf8($o));
		print $OUT &Encode::encode($CODE,$o).$LF;
	}
	$sth->finish;
	undef $sth;

	close($OUT);
	$zip->addFile(&cgi_lib::common::encodeUTF8($file_name),&cgi_lib::common::encodeUTF8(&File::Basename::basename($file_name)));


	@header_arr = qw|
FMA_ID
FMA_SYNONYM
FMA_ID_Base
FMA_SYNONYM_Base
|;
	$header = '#'.join("\t",map {$_ =~ /^[a-z]/ ? uc($_) : $_} @header_arr);

	$file_name = &catdir($out_path,'concept_data_synonym.txt');
	open($OUT,"> $file_name") or die "$! [$file_name]";
	print $OUT $export_date;
	print $OUT $version;
	print $OUT &Encode::encode($CODE,$header).$LF;

	my $cs_name;
	my $cs_bname;
	my $cdi_bname;
	$sql=<<SQL;
SELECT
  cdi.cdi_name
 ,cs.cs_name
 ,cdi_b.cdi_name
 ,cs_b.cs_name
FROM
 concept_data_synonym AS cds
LEFT JOIN concept_data_info AS cdi ON cdi.cdi_id=cds.cdi_id
LEFT JOIN concept_synonym AS cs ON cs.cs_id=cds.cs_id
LEFT JOIN concept_data_synonym_type AS cdst ON cdst.cdst_id=cds.cdst_id
LEFT JOIN concept_data_synonym AS cds_b ON cds_b.cds_id=cds.cds_bid
LEFT JOIN concept_data_info AS cdi_b ON cdi_b.cdi_id=cds_b.cdi_id
LEFT JOIN concept_synonym AS cs_b ON cs_b.cs_id=cds_b.cs_id
WHERE
     cds.ci_id=$ci_id
 AND cds.cb_id=$cb_id
 AND cdst.cdst_name='synonym'
ORDER BY
  cdi.cdi_name
 ,cdi_b.cdi_name
SQL
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;

	$column_number = 0;
	$sth->bind_col(++$column_number, \$cdi_name,  undef);
	$sth->bind_col(++$column_number, \$cs_name,   undef);
	$sth->bind_col(++$column_number, \$cdi_bname, undef);
	$sth->bind_col(++$column_number, \$cs_bname,  undef);
	while($sth->fetch){
		my @t;
		push(@t,$cdi_name);
		push(@t,$cs_name);
		push(@t,$cdi_bname);
		push(@t,$cs_bname);
		my $o = join("\t",map {defined $_ ? $_ : ''} @t);
		&utf8::decode($o) unless(&utf8::is_utf8($o));
		print $OUT &Encode::encode($CODE,$o).$LF;
	}
	$sth->finish;
	undef $sth;

	close($OUT);
	$zip->addFile(&cgi_lib::common::encodeUTF8($file_name),&cgi_lib::common::encodeUTF8(&File::Basename::basename($file_name)));



	@header_arr = qw|
FMA_ID
FMA_ID_Parent
ConceptRelationLogic
ConceptRelationTypes
|;
	$header = '#'.join("\t",map {$_ =~ /^[a-z]/ ? uc($_) : $_} @header_arr);

	$file_name = &catdir($out_path,'concept_tree.txt');
	open($OUT,"> $file_name") or die "$! [$file_name]";
	print $OUT $export_date;
	print $OUT $version;
	print $OUT &Encode::encode($CODE,$header).$LF;

	my $CRT_HASH;
	my $crt_id;
	$sql=<<SQL;
select
 crt.crt_id,
 crt.crt_name
from
 concept_relation_type as crt
SQL
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;

	$column_number = 0;
	$sth->bind_col(++$column_number, \$crt_id,        undef);
	$sth->bind_col(++$column_number, \$crt_name,      undef);
	while($sth->fetch){
		$CRT_HASH->{$crt_id} = $crt_name;
	}
	$sth->finish;
	undef $sth;

	if(defined $CDI_HASH && ref $CDI_HASH eq 'HASH' && defined $CRT_HASH && ref $CRT_HASH eq 'HASH'){
		my $cdi_pid;
		my $crt_ids;
		$sql=<<SQL;
select
 ct.cdi_id,
 ct.cdi_pid,
 crl.crl_name,
 ct.crt_ids
from
 concept_tree as ct
left join concept_relation_logic as crl on crl.crl_id=ct.crl_id
where
 ct.ci_id=$ci_id and ct.cb_id=$cb_id
SQL
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;

		$column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_id,       undef);
		$sth->bind_col(++$column_number, \$cdi_pid,      undef);
		$sth->bind_col(++$column_number, \$crl_name,     undef);
		$sth->bind_col(++$column_number, \$crt_ids,      undef);
		while($sth->fetch){
			next unless(exists $CDI_HASH->{$cdi_id} && defined $CDI_HASH->{$cdi_id} && length $CDI_HASH->{$cdi_id});

			my $cdi_name = $CDI_HASH->{$cdi_id};
			my $cdi_pname = (exists $CDI_HASH->{$cdi_pid} && defined $CDI_HASH->{$cdi_pid} && length $CDI_HASH->{$cdi_pid}) ? $CDI_HASH->{$cdi_pid} : '';
			my $crt_names = '';


			if(defined $crt_ids && length $crt_ids){
				my $HASH;
				foreach my $crt_id (split(/;/,$crt_ids)){
					next unless(exists $CRT_HASH->{$crt_id} && defined $CRT_HASH->{$crt_id} && length $CRT_HASH->{$crt_id});
					$HASH->{$CRT_HASH->{$crt_id}} = undef;
				}
				$crt_names = join(';',sort {$a cmp $b} keys(%{$HASH})) if(defined $HASH && ref $HASH eq 'HASH');
			}

			my @t;
			push(@t,$cdi_name);
			push(@t,$cdi_pname);
			push(@t,$crl_name);
			push(@t,$crt_names);
			my $o = join("\t",map {defined $_ ? $_ : ''} @t);
			&utf8::decode($o) unless(&utf8::is_utf8($o));
			print $OUT &Encode::encode($CODE,$o).$LF;
		}
		$sth->finish;
		undef $sth;
	}
	close($OUT);
	$zip->addFile(&cgi_lib::common::encodeUTF8($file_name),&cgi_lib::common::encodeUTF8(&File::Basename::basename($file_name)));




	@header_arr = qw|
FMA_ID
FMA_ID_Descendants
FMA_ID_Ancestor
ConceptRelationLogic
Depth
|;
	$header = '#'.join("\t",map {$_ =~ /^[a-z]/ ? uc($_) : $_} @header_arr);

	$file_name = &catdir($out_path,'concept_tree_info.txt');
	open($OUT,"> $file_name") or die "$! [$file_name]";
	print $OUT $export_date;
	print $OUT $version;
	print $OUT &Encode::encode($CODE,$header).$LF;

	my $CTI_HASH;
	my $cti_cids;
	my $cti_depth;
	$sql=<<SQL;
select
 cti.cdi_id,
 cdi.cdi_name,
 cti.cti_cids,
 cti.cti_pids,
 crl.crl_name,
 cti.cti_depth
from
 concept_tree_info as cti
left join concept_data_info as cdi on cdi.ci_id=cti.ci_id and cdi.cdi_id=cti.cdi_id
left join concept_relation_logic as crl on crl.crl_id=cti.crl_id
where
 cti.ci_id=$ci_id and cti.cb_id=$cb_id
SQL
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;

	$column_number = 0;
	$sth->bind_col(++$column_number, \$cdi_id,        undef);
	$sth->bind_col(++$column_number, \$cdi_name,      undef);
	$sth->bind_col(++$column_number, \$cti_cids,      undef);
	$sth->bind_col(++$column_number, \$cti_pids,      undef);
	$sth->bind_col(++$column_number, \$crl_name,      undef);
	$sth->bind_col(++$column_number, \$cti_depth,     undef);
	while($sth->fetch){
#		$CDI_HASH->{$cdi_id} = $cdi_name;
		my $hash = $CTI_HASH->{$cdi_name}->{$crl_name} = {
			cdi_name => $cdi_name,
			cti_depth => $cti_depth - 0,
			cti_cids => undef,
			cti_pids => undef
		};
		if(defined $cti_cids && length $cti_cids){
			my $cti_cids_arr = &cgi_lib::common::decodeJSON($cti_cids);
			if(defined $cti_cids_arr && ref $cti_cids_arr eq 'ARRAY' && scalar @{$cti_cids_arr}){
				push(@{$hash->{'cti_cids'}}, @{$cti_cids_arr});
			}
		}
		if(defined $cti_pids && length $cti_pids){
			my $cti_pids_arr = &cgi_lib::common::decodeJSON($cti_pids);
			if(defined $cti_pids_arr && ref $cti_pids_arr eq 'ARRAY' && scalar @{$cti_pids_arr}){
				push(@{$hash->{'cti_pids'}}, @{$cti_pids_arr});
			}
		}
	}
	$sth->finish;
	undef $sth;

	if(defined $CTI_HASH && ref $CTI_HASH eq 'HASH'){
		foreach my $cdi_name (sort {$a cmp $b} keys(%{$CTI_HASH})){
			foreach my $crl_name (sort {$a cmp $b} keys(%{$CTI_HASH->{$cdi_name}})){
				my $hash = $CTI_HASH->{$cdi_name}->{$crl_name};
				my $cti_depth = $hash->{'cti_depth'};
				my $cti_cnames = '';
				if(
					exists	$hash->{'cti_cids'} &&
					defined	$hash->{'cti_cids'} &&
					ref			$hash->{'cti_cids'} eq 'ARRAY'
				){
					my $cti_cnames_hash;
					map { $cti_cnames_hash->{$CDI_HASH->{$_}} = undef if(exists $CDI_HASH->{$_} && defined $CDI_HASH->{$_} && length $CDI_HASH->{$_}) } @{$hash->{'cti_cids'}};
					$cti_cnames = &cgi_lib::common::encodeJSON([sort {$a cmp $b} keys(%{$cti_cnames_hash})]) if(defined $cti_cnames_hash && ref $cti_cnames_hash eq 'HASH');
				}
				my $cti_pnames = '';
				if(
					exists	$hash->{'cti_pids'} &&
					defined	$hash->{'cti_pids'} &&
					ref			$hash->{'cti_pids'} eq 'ARRAY'
				){
					my $cti_pnames_hash;
					map { $cti_pnames_hash->{$CDI_HASH->{$_}} = undef if(exists $CDI_HASH->{$_} && defined $CDI_HASH->{$_} && length $CDI_HASH->{$_}) } @{$hash->{'cti_pids'}};
					$cti_pnames = &cgi_lib::common::encodeJSON([sort {$a cmp $b} keys(%{$cti_pnames_hash})]) if(defined $cti_pnames_hash && ref $cti_pnames_hash eq 'HASH');
				}

				my @t;
				push(@t,$cdi_name);
				push(@t,$cti_cnames);
				push(@t,$cti_pnames);
				push(@t,$crl_name);
				push(@t,$cti_depth);
				my $o = join("\t",map {defined $_ ? $_ : ''} @t);
				&utf8::decode($o) unless(&utf8::is_utf8($o));
				print $OUT &Encode::encode($CODE,$o).$LF;

			}
		}
	}

	close($OUT);
	$zip->addFile(&cgi_lib::common::encodeUTF8($file_name),&cgi_lib::common::encodeUTF8(&File::Basename::basename($file_name)));


	return $zip;
}
1;
