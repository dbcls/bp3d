#!/bp3d/local/perl/bin/perl

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use File::Basename;
use Cwd qw(abs_path);
use File::Spec;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;

use BITS::Config;
require "webgl_common.pl";
use cgi_lib::common;

my $query = CGI->new;
my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
&getParams($query,\%FORM,\%COOKIE);
my($log_file,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

#my @extlist = qw|.cgi|;
#my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);

$FORM{'cmd'} = 'read' unless(defined $FORM{'cmd'});
$log_file .= '.'.$FORM{'cmd'};

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
$log_file .=  sprintf(".%02d%02d%02d.%05d",$hour,$min,$sec,$$);

my $LOG;
open($LOG,">> $log_file");
print $LOG sprintf("\n%04d:%04d/%02d/%02d %02d:%02d:%02d\n",__LINE__,$year+1900,$mon+1,$mday,$hour,$min,$sec);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);

$FORM{'start'} = 0 unless(defined $FORM{'start'});
$FORM{'limit'} = 25 unless(defined $FORM{'limit'});




#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $DATAS = {
	'datas' => [],
	'total' => 0,
	'success' => JSON::XS::false
};

#		my $to = File::Spec->catfile($dir,$name,qq|all.json|);

=pod
my $data_dir = $BITS::Config::UPLOAD_PATH;
opendir(DIR,$data_dir) || die "[$data_dir] $!\n";
my @DIRS = map {qq|$data_dir/$_|} sort grep {$_ =~ /^[^\.]/ && -f qq|$data_dir/$_/all.json|} readdir(DIR);
closedir(DIR);

foreach my $dir (@DIRS){
	my ($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,$atime,$mtime,$ctime,$blksize,$blocks) = stat($dir);

	opendir(DIR,$dir) || die "[$dir] $!\n";
	my @FILES = map {qq|$dir/$_|} grep {$_ =~ /^[^\.]/ && $_ =~ /\.obj$/ && $_ !~ /\.org\.obj$/ && -f qq|$dir/$_|} readdir(DIR);
	closedir(DIR);

	my $dir_name = &File::Basename::basename($dir);

	push(@{$DATAS->{'datas'}},{
		name  => $dir_name,
		path  => qq|js/uploads/$dir_name|,
		ino   => $ino,
		num   => scalar @FILES,
		mtime => $mtime
	});
}
=cut
if($FORM{'cmd'} eq 'read'){

	my %selected_artg_ids;
	if(exists $FORM{'selected_artg_ids'} && defined $FORM{'selected_artg_ids'}){
		my $artg_ids;
		eval{$artg_ids = &JSON::XS::decode_json($FORM{'selected_artg_ids'});};
		if(defined $artg_ids && ref $artg_ids eq 'ARRAY'){
			%selected_artg_ids = map {$_ => JSON::XS::true} @$artg_ids;
		}
	};

	my $sql =<<SQL;
select
 artg.artg_id,
 artg_name,
 EXTRACT(EPOCH FROM artg_timestamp) as artg_timestamp,
 atrg_use,
 artg_comment,
 artg_delcause,
 EXTRACT(EPOCH FROM artg_entry) as artg_entry,
 artg_openid,
 COALESCE(art_count,0),
 COALESCE(map_count,0),
 COALESCE(chk_count,0),
 COALESCE(use_map_count,0),
 artg.artf_id,
 artf_name
from
 (select * from art_group where artg_id in (select artg_id from art_file_info where art_delcause is null group by artg_id)) as artg
left join (
  select
   artg_id,
   count(artg_id) as art_count
  from
   art_file_info
  group by
   artg_id
) as f on (f.artg_id=artg.artg_id)

left join (
  select artg_id,count(artg_id) as map_count from (
    select
      artg_id,
      harti.art_id,
      count(map.cdi_id)
    from
      art_file_info as harti
    left join (
      select * from concept_art_map where cm_delcause is null
    ) as map on map.art_id=harti.art_id
    left join (select art_id from art_file_info where art_delcause is null) as arti on (arti.art_id=harti.art_id)
    where
      map.cm_delcause is null and
      harti.art_delcause is null and
      arti.art_id is not null
    group by
      artg_id,
      harti.art_id
    HAVING
      count(map.cdi_id)=0
  ) as a group by artg_id
) as m on (m.artg_id=artg.artg_id)

left join (
  select
   artg_id,
   count(artg_id) as chk_count
  from (
    select distinct
     artg_id,
     harti.art_id
    from
      art_file_info as harti
    left join (
       select * from art_annotation
     ) as arta on
        arta.art_id=harti.art_id
    left join (select art_id from art_file_info where art_delcause is null) as arti on (arti.art_id=harti.art_id)

    where
     art_delcause is null and
     arta.art_comment is null and
     arta.art_category is null and
     arta.art_judge is null and
     arta.art_class is null and
     arti.art_id is not null
  ) as a
  group by
   artg_id
) as c on (c.artg_id=artg.artg_id)

left join (
  select artg_id,count(artg_id) as use_map_count from (
    select
      artg_id,
      harti.art_id,
      count(map.cdi_id)
    from
      art_file_info as harti
    left join (
      select * from concept_art_map where cm_delcause is null
    ) as map on map.art_id=harti.art_id
    left join (select art_id from art_file_info where art_delcause is null) as arti on (arti.art_id=harti.art_id)
    where
      map.cm_use and
      map.cm_delcause is null and
      harti.art_delcause is null and
      arti.art_id is not null
    group by
      artg_id,
      harti.art_id
    HAVING
      count(map.cdi_id)!=0
  ) as a group by artg_id
) as u on (u.artg_id=artg.artg_id)

left join (
  select
   artf_id,
   artf_name
  from
   art_folder
  where
   artf_use and
   artf_delcause is null
) as fo on (fo.artf_id=artg.artf_id)

where
 atrg_use and
 artg_delcause is null
 and COALESCE(art_count,0)>0
SQL

#	if(exists $FORM{'artf_id'} && defined $FORM{'artf_id'} && $FORM{'artf_id'}){
#		$sql .= qq| and artg.artf_id=$FORM{'artf_id'}|;
#	}else{
#		$sql .= qq| and artg.artf_id is null|;
#	}

	print $LOG __LINE__,":",$sql,"\n";

	eval{
		my $sth_all_cm_count = $dbh->prepare("select mv_name_e,mv_order from concept_art_map as cm left join (select * from model_version) as mv on (cm.md_id=mv.md_id and cm.mv_id=mv.mv_id) where cm_use and cm_delcause is null and art_id in (select art_id from art_file_info where artg_id=?) group by mv_name_e,mv_order order by mv_order") or die $dbh->errstr;

		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		if($sth->rows>0){
			my $column_number = 0;
			my $artg_id;
			my $artg_name;
			my $artg_timestamp;
			my $atrg_use;
			my $artg_comment;
			my $artg_delcause;
			my $artg_entry;
			my $artg_openid;
			my $art_count;
			my $map_count;
			my $chk_count;
			my $use_map_count;
			my $artf_id;
			my $artf_name;
			$sth->bind_col(++$column_number, \$artg_id, undef);
			$sth->bind_col(++$column_number, \$artg_name, undef);
			$sth->bind_col(++$column_number, \$artg_timestamp, undef);
			$sth->bind_col(++$column_number, \$atrg_use, undef);
			$sth->bind_col(++$column_number, \$artg_comment, undef);
			$sth->bind_col(++$column_number, \$artg_delcause, undef);
			$sth->bind_col(++$column_number, \$artg_entry, undef);
			$sth->bind_col(++$column_number, \$artg_openid, undef);
			$sth->bind_col(++$column_number, \$art_count, undef);
			$sth->bind_col(++$column_number, \$map_count, undef);
			$sth->bind_col(++$column_number, \$chk_count, undef);
			$sth->bind_col(++$column_number, \$use_map_count, undef);
			$sth->bind_col(++$column_number, \$artf_id, undef);
			$sth->bind_col(++$column_number, \$artf_name, undef);
			while($sth->fetch){

				$sth_all_cm_count->execute($artg_id) or die $dbh->errstr;
				my $all_cm_count = $sth_all_cm_count->rows();
				my $all_cm_count_mv_name_e = [];
				if($all_cm_count>0){
					my $mv_name_e;
					$column_number = 0;
					$sth_all_cm_count->bind_col(++$column_number, \$mv_name_e, undef);
					while($sth_all_cm_count->fetch){
						push(@$all_cm_count_mv_name_e,$mv_name_e) if(defined $mv_name_e && length $mv_name_e);
					}
				}
				$sth_all_cm_count->finish;


				push(@{$DATAS->{'datas'}},{
					#Old I/O
					name  => $artg_name,
	#				path  => qq|js/uploads/$artg_name|,
	#				path  => qq|art_file/$artg_name|,
					path  => qq|art_file|,
					ino   => $artg_id + 0,
					num   => $art_count + 0,
					mtime => $artg_timestamp + 0,

					selected => exists $selected_artg_ids{$artg_id} ? JSON::XS::true : JSON::XS::false,

					#New I/O
					artg_id        => $artg_id + 0,
					artg_name      => $artg_name,
					artg_timestamp => $artg_timestamp + 0,
					atrg_use       => $atrg_use ? JSON::XS::true: JSON::XS::false,
					artg_comment   => $artg_comment,
					artg_delcause  => $artg_delcause,
					artg_entry     => $artg_entry + 0,
					artg_openid    => $artg_openid,
					art_count      => $art_count + 0,
					nomap_count    => $map_count + 0,
					nochk_count    => $chk_count + 0,
					use_map_count  => $use_map_count + 0,
					all_cm_map_versions => $all_cm_count_mv_name_e,

					artf_id        => defined $artf_id ? $artf_id + 0 : undef,
					artf_name      => $artf_name,
				});
			}
		}
		$sth->finish;
		undef $sth;

		$DATAS->{'total'} = scalar @{$DATAS->{'datas'}};
		$DATAS->{'success'} = JSON::XS::true;
	};
	if($@){
		print $LOG __LINE__,":",$@,"\n";
		$DATAS->{'msg'} = $@;
	}
}
elsif($FORM{'cmd'} eq 'update'){
	my $datas;
	if(exists $FORM{'datas'} && defined $FORM{'datas'}){
		$datas = &cgi_lib::common::decodeJSON($FORM{'datas'});
	}
	if(defined $datas && ref $datas eq 'ARRAY'){
		$dbh->{AutoCommit} = 0;
		$dbh->{RaiseError} = 1;
		eval{
			my $sth_artg_name      = $dbh->prepare(qq|update art_group set artg_name=? where artg_id=?|) or die $dbh->errstr;
			my $sth_artg_delcause  = $dbh->prepare(qq|update art_group set artg_delcause=? where artg_id=?|) or die $dbh->errstr;
			my $sth_artg_artf      = $dbh->prepare(qq|update art_group set artf_id=? where artg_id=?|) or die $dbh->errstr;
			my $sth_artg_artf_null = $dbh->prepare(qq|update art_group set artf_id=null where artg_id=?|) or die $dbh->errstr;

			foreach my $data (@$datas){
				if($data->{'name'} ne $data->{'artg_name'}){
					&cgi_lib::common::message(&cgi_lib::common::encodeJSON($data,1),$LOG) if(defined $LOG);
					$sth_artg_name->execute( $data->{'artg_name'}, $data->{'artg_id'}) or die $dbh->errstr;
					$sth_artg_name->finish;
				}elsif(defined $data->{'artg_delcause'} && length $data->{'artg_delcause'}){
					&cgi_lib::common::message(&cgi_lib::common::encodeJSON($data,1),$LOG) if(defined $LOG);
					$sth_artg_delcause->execute( $data->{'artg_delcause'}, $data->{'artg_id'}) or die $dbh->errstr;
					$sth_artg_delcause->finish;
				}else{
					if($data->{'artf_id'}){
						&cgi_lib::common::message(&cgi_lib::common::encodeJSON($data,1),$LOG) if(defined $LOG);
						$sth_artg_artf->execute( $data->{'artf_id'}, $data->{'artg_id'}) or die $dbh->errstr;
						$sth_artg_artf->finish;
					}else{
						&cgi_lib::common::message(&cgi_lib::common::encodeJSON($data,1),$LOG) if(defined $LOG);
						$sth_artg_artf_null->execute( $data->{'artg_id'}) or die $dbh->errstr;
						$sth_artg_artf_null->finish;
					}
				}
			}
			undef $sth_artg_name;
			undef $sth_artg_delcause;
			undef $sth_artg_artf;
			undef $sth_artg_artf_null;

			$dbh->commit();
			$dbh->do("NOTIFY art_group");
			$DATAS->{'success'} = JSON::XS::true;
		};
		if($@){
			print $LOG __LINE__,":",$@,"\n";
			$DATAS->{'msg'} = $@;
			$dbh->rollback;
		}
		$dbh->{AutoCommit} = 1;
		$dbh->{RaiseError} = 0;
	}
}
elsif($FORM{'cmd'} eq 'destroy'){
	my $datas;
	if(exists $FORM{'datas'} && defined $FORM{'datas'}){
		$datas = &cgi_lib::common::decodeJSON($FORM{'datas'});
	}
	if(defined $datas && ref $datas eq 'ARRAY'){
		$dbh->{AutoCommit} = 0;
		$dbh->{RaiseError} = 1;
		eval{

			my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
			my $del_time = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
			my $artg_delcause = qq|DELETE [$del_time]|;

			my $sth_arto_delete = $dbh->prepare(qq|delete from art_org_info where art_id in (select art_id from art_file_info where artg_id=?)|) or die $dbh->errstr;
			my $sth_arta_delete = $dbh->prepare(qq|delete from art_annotation where art_id in (select art_id from art_file_info where artg_id=?)|) or die $dbh->errstr;
			my $sth_arti_delete = $dbh->prepare(qq|delete from art_file_info where artg_id=?|) or die $dbh->errstr;
			my $sth_art_delete  = $dbh->prepare(qq|delete from art_file where artg_id=?|) or die $dbh->errstr;
			my $sth_artg_delete = $dbh->prepare(qq|delete from art_group where artg_id=?|) or die $dbh->errstr;

			my $sth_artg_select = $dbh->prepare(qq|select * from art_group where artg_id in (select artg_id from (select art_id,artg_id from history_art_file union select art_id,artg_id from art_file_info) as a where art_id in (select art_id from (select art_id,artg_id from history_art_file union select art_id,artg_id from art_file_info) as a where artg_id=?) group by artg_id)|) or die $dbh->errstr;

			my $sth_artg_delcause = $dbh->prepare(qq|update art_group set artg_delcause=?,atrg_use=false where artg_id=?|) or die $dbh->errstr;
			my $sth_map_delcause = $dbh->prepare(qq|update concept_art_map set cm_use=false where art_id in (select art_id from art_file_info where artg_id=?)|) or die $dbh->errstr;
			foreach my $data (@$datas){
				next unless(defined $data->{'artg_id'});

				$sth_map_delcause->execute($data->{'artg_id'}) or die $dbh->errstr;
				$sth_map_delcause->finish;

				$sth_arto_delete->execute($data->{'artg_id'}) or die $dbh->errstr;
				$sth_arto_delete->finish;

				$sth_arta_delete->execute($data->{'artg_id'}) or die $dbh->errstr;
				$sth_arta_delete->finish;

				$sth_arti_delete->execute($data->{'artg_id'}) or die $dbh->errstr;
				$sth_arti_delete->finish;

				$sth_artg_select->execute($data->{'artg_id'}) or die $dbh->errstr;
				my $artg_rows = $sth_artg_select->rows();
				$sth_artg_select->finish;
				print $LOG __LINE__,":\$artg_rows=[$artg_rows]\n";
				if($artg_rows<=1){
					$sth_art_delete->execute($data->{'artg_id'}) or die $dbh->errstr;
					$sth_art_delete->finish;
				}

				$sth_artg_delete->execute($data->{'artg_id'}) or die $dbh->errstr;
				$sth_artg_delete->finish;
				next;


				$sth_artg_delcause->execute($artg_delcause,$data->{'artg_id'}) or die $dbh->errstr;
				$sth_artg_delcause->finish;
			}
			undef $sth_map_delcause;
			undef $sth_artg_delcause;

			undef $sth_arto_delete;
			undef $sth_arta_delete;
			undef $sth_arti_delete;
			undef $sth_art_delete;
			undef $sth_artg_delete;


			$dbh->commit();
			$dbh->do("NOTIFY art_group");
			$DATAS->{'success'} = JSON::XS::true;
		};
		if($@){
			print $LOG __LINE__,":",$@,"\n";
			$DATAS->{'msg'} = $@;
			$dbh->rollback;
		}
		$dbh->{AutoCommit} = 1;
		$dbh->{RaiseError} = 0;
	}
}
#my $json = &JSON::XS::encode_json($DATAS);
#print $json;
&gzip_json($DATAS);

exit;
