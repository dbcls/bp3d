#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;

use JSON::XS;
use DBD::Pg;
use File::Spec::Functions qw(abs2rel rel2abs catdir catfile splitdir);

use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'..','cgi_lib');
require "webgl_common.pl";
use cgi_lib::common;

my $base_path;
my $art_file_prefix;
BEGIN{
	$base_path = $FindBin::Bin;
#	$art_file_prefix = &catdir($base_path,qq|art_file|);
	$art_file_prefix = &catdir($base_path,qq|fma_art_file|);
}
unless(-e $art_file_prefix){
	my $m = umask(0);
	&File::Path::mkpath($art_file_prefix,0,0777);
	umask($m);
}
#my $art_file_fmt = qq|$art_file_prefix/%s-%d%s|;

use constant {
	DEF_YRANGE => 1800,
	DEF_ART_FILE_PREFIX => qq|$art_file_prefix/%s|,
	DEF_ART_FILE_FMT => qq|%s-%d%s|
};

my $art_file_fmt = DEF_ART_FILE_FMT;

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);

my($logfile,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);
my $LOG;
my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
open($LOG,"> $logfile");
print $LOG "\n[$logtime]:$0\n";
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%ENV,1), $LOG);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM,1), $LOG);

&setDefParams(\%FORM,\%COOKIE);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM,1), $LOG);

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM,1), $LOG);
#print qq|Content-type: text/html; charset=UTF-8\n\n|;

#=pod
my $jsonStr = $FORM{'keywords'};
my $obj_files1;
my $json = &cgi_lib::common::decodeJSON($jsonStr);
if(defined $json){
	&cgi_lib::common::message(&cgi_lib::common::encodeJSON($json,1), $LOG);

	my($md_id,$md_abbr) = &getModel($dbh,$json);
	&cgi_lib::common::message($md_id, $LOG);
	&cgi_lib::common::message($md_abbr, $LOG);

	my($mv_id,$mr_id,$mr_version,$mv_name) = &getVersion($dbh,$json,$md_id);
	&cgi_lib::common::message($mv_id, $LOG);
	&cgi_lib::common::message($mr_id, $LOG);
	&cgi_lib::common::message($mr_version, $LOG);
	&cgi_lib::common::message($mv_name, $LOG);

	my($bul_id,$bul_abbr) = &getTreeName($dbh,$json);
	&cgi_lib::common::message($bul_id, $LOG);
	&cgi_lib::common::message($bul_abbr, $LOG);

	$obj_files1 = &getObjs(dbh=>$dbh,json=>$json,md_id=>$md_id,mv_id=>$mv_id,mr_id=>$mr_id,bul_id=>$bul_id,md_abbr=>$md_abbr,mr_version=>$mr_version,bul_abbr=>$bul_abbr,mv_name=>$mv_name);
	&cgi_lib::common::message(&cgi_lib::common::encodeJSON($obj_files1,1), $LOG);

#	print $LOG __LINE__,":",&Data::Dumper::Dumper($obj_files1);
#	$obj_files1 = [] unless(defined $obj_files1);

#	if(defined $obj_files1){
#	my $json = new JSON::XS;
#	$jsonStr = $json->pretty(1)->encode($obj_files1);
#		$jsonStr = &JSON::XS::encode_json($obj_files1);
#	}
}
#=cut

#print $LOG $jsonStr,"\n";
#print qq|<pre>|;
#print $jsonStr,"\n";
#print qq|</pre>|;

$obj_files1 = [] unless(defined $obj_files1);
&gzip_json($obj_files1);

print $LOG &JSON::XS::encode_json($obj_files1)."\n";
close($LOG) if(defined $LOG);
exit;

sub getModel {
	my $dbh = shift;
	my $json = shift;

	my $md_id;
	my $md_abbr;
	my $sql =<<SQL;
select md_id,md_abbr from model where md_abbr=?
SQL
	my $sth = $dbh->prepare($sql) or croak $dbh->errstr;
	$sth->execute($json->{'Common'}->{'Model'}) or croak $dbh->errstr;
	if($sth->rows>0){
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$md_id, undef);
		$sth->bind_col(++$column_number, \$md_abbr, undef);
		$sth->fetch;
	}
	$sth->finish;
	undef $sth;
	unless(defined $md_id && defined $md_abbr){
		my $sql =<<SQL;
select md_id,md_abbr from model order by md_order limit 1
SQL
		my $sth = $dbh->prepare($sql);
		$sth->execute();
		if($sth->rows>0){
			my $column_number = 0;
			$sth->bind_col(++$column_number, \$md_id, undef);
			$sth->bind_col(++$column_number, \$md_abbr, undef);
			$sth->fetch;
			$json->{'Common'}->{'Model'} = $md_abbr;
		}
		$sth->finish;
		undef $sth;
	}
	return ($md_id,$md_abbr);
}

sub getVersion {
	my $dbh = shift;
	my $json = shift;
	my $md_id = shift;
	my $mv_id;
	my $mr_id;
	my $mr_version;
	my $mv_name;
	if(defined $json->{'Common'}->{'Version'}){
		my $sql =<<SQL;
select mv_id,mr_id,mr_version from model_revision where md_id=? and mr_version=?
SQL
		my $sth = $dbh->prepare($sql);
		$sth->execute($md_id,$json->{'Common'}->{'Version'});
		if($sth->rows>0){
			my $column_number = 0;
			$sth->bind_col(++$column_number, \$mv_id, undef);
			$sth->bind_col(++$column_number, \$mr_id, undef);
			$sth->bind_col(++$column_number, \$mr_version, undef);
			$sth->fetch;
		}
		$sth->finish;
		undef $sth;

		unless(defined $mr_version){
			my $sql =<<SQL;
select
 mr.mv_id,
 mr_id,
 mr_version
from
 model_revision as mr
left join (
    select md_id,mv_id,mv_name_e from model_version
  ) as mv on mv.md_id=mr.md_id and mv.mv_id=mr.mv_id
where
 mr.md_id=? and mv_name_e=?
order by
 mr_order limit 1
SQL
			my $sth = $dbh->prepare($sql);
			$sth->execute($md_id,$json->{'Common'}->{'Version'});
			if($sth->rows>0){
				my $column_number = 0;
				$sth->bind_col(++$column_number, \$mv_id, undef);
				$sth->bind_col(++$column_number, \$mr_id, undef);
				$sth->bind_col(++$column_number, \$mr_version, undef);
				$sth->fetch;
				$json->{'Common'}->{'Version'} = $mr_version;
			}
			$sth->finish;
			undef $sth;
		}
	}
	unless(defined $mr_version){
		my $sql =<<SQL;
select mv_id,mr_id,mr_version from model_revision where md_id=? order by mr_order limit 1
SQL
		my $sth = $dbh->prepare($sql);
		$sth->execute($md_id);
		if($sth->rows>0){
			my $column_number = 0;
			$sth->bind_col(++$column_number, \$mv_id, undef);
			$sth->bind_col(++$column_number, \$mr_id, undef);
			$sth->bind_col(++$column_number, \$mr_version, undef);
			$sth->fetch;
			$json->{'Common'}->{'Version'} = $mr_version;
		}
		$sth->finish;
		undef $sth;
	}
	if(defined $mv_id){
		my $sql =<<SQL;
select mv_name_e from model_version where md_id=? and mv_id=?
SQL
		my $sth = $dbh->prepare($sql);
		$sth->execute($md_id,$mv_id);
		if($sth->rows>0){
			my $column_number = 0;
			$sth->bind_col(++$column_number, \$mv_name, undef);
			$sth->fetch;
		}
		$sth->finish;
		undef $sth;
	}
	return ($mv_id,$mr_id,$mr_version,$mv_name);
}

sub getTreeName {
	my $dbh = shift;
	my $json = shift;
	my $bul_id;
	my $bul_abbr;
	if(defined $json->{'Common'}->{'TreeName'}){
		my $sql =<<SQL;
select bul_id,bul_abbr from buildup_logic where bul_abbr=?
SQL
		my $sth = $dbh->prepare($sql);
		$sth->execute($json->{'Common'}->{'TreeName'});
		if($sth->rows>0){
			my $column_number = 0;
			$sth->bind_col(++$column_number, \$bul_id, undef);
			$sth->bind_col(++$column_number, \$bul_abbr, undef);
			$sth->fetch;
		}
		$sth->finish;
		undef $sth;
	}
	unless(defined $bul_abbr){
		$bul_id = 3;
		$bul_abbr = 'isa';
		$json->{'Common'}->{'TreeName'} = $bul_abbr;
	}
	return ($bul_id,$bul_abbr);
}

sub getObjs {
	my %args = (@_);

	my $dbh = $args{'dbh'};
	my $json = $args{'json'};
	my $md_id = $args{'md_id'};
	my $mv_id = $args{'mv_id'};
	my $mr_id = $args{'mr_id'};
	my $bul_id = $args{'bul_id'};

	my $md_abbr = $args{'md_abbr'};
	my $mv_name = $args{'mv_name'};
	my $mr_version = $args{'mr_version'};
	my $bul_abbr = $args{'bul_abbr'};


	my $obj_files;
	my $obj_files_hash;

	if(exists $json->{'Part'} && defined $json->{'Part'} && ref $json->{'Part'} eq 'ARRAY'){
		my @cdi_names;
		my @cdi_names_e;
		my @b_cdi_names;
		my @b_cdi_names_e;
		my $Part;
		foreach my $part (@{$json->{'Part'}}){
			if(defined $part->{'PartID'}){
				push(@cdi_names,$part->{'PartID'});
				push(@b_cdi_names,'?');
				$Part->{$part->{'PartID'}} = $part;
			}elsif(defined $part->{'PartName'}){
				push(@cdi_names_e,$part->{'PartName'});
				push(@b_cdi_names_e,'?');
				$Part->{$part->{'PartName'}} = $part;
			}
		}
		if(scalar @cdi_names > 0 || scalar @cdi_names_e > 0){
			my $sql_sub =<<SQL;
select
 md_id,
 mv_id,
 max(mr_id) as mr_id,
 bul_id,
 cdi_id
from
 view_representation
where
 rep_delcause is null and
 md_id=$md_id and
 mv_id=$mv_id and
 mr_id<=$mr_id and 
SQL
			$sql_sub .= '(';
			$sql_sub .= qq|cdi_name in (| . join(qq|,|,@b_cdi_names) . qq|)| if(scalar @cdi_names > 0);
			$sql_sub .= qq| or | if(scalar @cdi_names > 0 && scalar @cdi_names_e > 0);
			$sql_sub .= qq|cdi_name_e in (| . join(qq|,|,@b_cdi_names_e) . qq|)| if(scalar @cdi_names_e > 0);
			$sql_sub .= ')';
			$sql_sub .= ' group by md_id,mv_id,bul_id,cdi_id';

print $LOG __LINE__,":\$sql_sub=[$sql_sub]\n";
print $LOG __LINE__,":\$cdi_names=['",join("','",@cdi_names),"']\n";
print $LOG __LINE__,":\$cdi_names_e=['",join("','",@cdi_names_e),"']\n";

			my $sql =<<SQL;
select
 ci_id,
 cb_id,
 cdi_id,
 md_id,
 mv_id,
 mr_id,
 bul_id,
 rep_id,
 cdi_name,
 cdi_name_e,
 cdi_name_j,
 rep_xmin,
 rep_xmax,
 rep_ymin,
 rep_ymax,
 rep_zmin,
 rep_zmax,
 rep_volume
from
 view_representation
where
 (md_id,mv_id,mr_id,bul_id,cdi_id) in ($sql_sub)
order by bul_id,rep_depth desc
SQL
print $LOG __LINE__,":\$sql=[$sql]\n";

			my @b;
			push(@b,@cdi_names) if(scalar @cdi_names > 0);
			push(@b,@cdi_names_e) if(scalar @cdi_names_e > 0);

			my $sth = $dbh->prepare($sql);
			$sth->execute(@b);
print $LOG __LINE__,":\$rows=[",$sth->rows,"]\n";
			if($sth->rows>0){

				my $sql =<<SQL;
select
 art_id,
 art_ext,
 hist_serial,
 EXTRACT(EPOCH FROM art_timestamp),
 art_data,
 art_data_size,
 art_decimate,
 art_decimate_size,
 art_xmin,
 art_xmax,
 art_ymin,
 art_ymax,
 art_zmin,
 art_zmax,
 art_volume
from
 history_art_file
where
 (art_id,hist_serial) in (
   select art_id,art_hist_serial from representation_art where rep_id=?
 )
SQL
print $LOG __LINE__,":\$sql=[$sql]\n";
				my $sth_art = $dbh->prepare($sql);

				my $d_ci_id;
				my $d_cb_id;
				my $d_cdi_id;
				my $d_md_id;
				my $d_mv_id;
				my $d_mr_id;
				my $d_bul_id;

				my $rep_id;
				my $cdi_name;
				my $cdi_name_e;
				my $cdi_name_j;

				my $rep_xmin;
				my $rep_xmax;
				my $rep_ymin;
				my $rep_ymax;
				my $rep_zmin;
				my $rep_zmax;
				my $rep_volume;

				my $column_number = 0;

				$sth->bind_col(++$column_number, \$d_ci_id, undef);
				$sth->bind_col(++$column_number, \$d_cb_id, undef);
				$sth->bind_col(++$column_number, \$d_cdi_id, undef);
				$sth->bind_col(++$column_number, \$d_md_id, undef);
				$sth->bind_col(++$column_number, \$d_mv_id, undef);
				$sth->bind_col(++$column_number, \$d_mr_id, undef);
				$sth->bind_col(++$column_number, \$d_bul_id, undef);

				$sth->bind_col(++$column_number, \$rep_id, undef);
				$sth->bind_col(++$column_number, \$cdi_name, undef);
				$sth->bind_col(++$column_number, \$cdi_name_e, undef);
				$sth->bind_col(++$column_number, \$cdi_name_j, undef);

				$sth->bind_col(++$column_number, \$rep_xmin, undef);
				$sth->bind_col(++$column_number, \$rep_xmax, undef);
				$sth->bind_col(++$column_number, \$rep_ymin, undef);
				$sth->bind_col(++$column_number, \$rep_ymax, undef);
				$sth->bind_col(++$column_number, \$rep_zmin, undef);
				$sth->bind_col(++$column_number, \$rep_zmax, undef);
				$sth->bind_col(++$column_number, \$rep_volume, undef);

				while($sth->fetch){
print $LOG __LINE__,":\$d_bul_id=[$d_bul_id]\n" if(defined $d_bul_id);
#ツリーに関係なく表示できるようにする
#					next unless($bul_id == $d_bul_id);

print $LOG __LINE__,":\$rep_id=[$rep_id]\n" if(defined $rep_id);
print $LOG __LINE__,":\$cdi_name=[$cdi_name]\n" if(defined $cdi_name);

=pod
print $LOG __LINE__,":\$rep_xmin=[$rep_xmin]\n" if(defined $rep_xmin);
print $LOG __LINE__,":\$rep_xmax=[$rep_xmax]\n" if(defined $rep_xmax);
print $LOG __LINE__,":\$rep_ymin=[$rep_ymin]\n" if(defined $rep_ymin);
print $LOG __LINE__,":\$rep_ymax=[$rep_ymax]\n" if(defined $rep_ymax);
print $LOG __LINE__,":\$rep_zmin=[$rep_zmin]\n" if(defined $rep_zmin);
print $LOG __LINE__,":\$rep_zmax=[$rep_zmax]\n" if(defined $rep_zmax);

print $LOG __LINE__,":\$xcenter=[",(($rep_xmin+$rep_xmax)/2),"]\n" if(defined $rep_xmin && defined $rep_xmax);
print $LOG __LINE__,":\$ycenter=[",(($rep_ymin+$rep_ymax)/2),"]\n" if(defined $rep_ymin && defined $rep_ymax);
print $LOG __LINE__,":\$zcenter=[",(($rep_zmin+$rep_zmax)/2),"]\n" if(defined $rep_zmin && defined $rep_zmax);
=cut

=pod
					my $a = exists $Part->{$cdi_name} ?  $Part->{$cdi_name} : (exists $Part->{$cdi_name_e} ? $Part->{$cdi_name_e} : undef);
					next unless(defined $a);
					my $b = &Clone::clone($a);

					$b->{'_files'} = [];
					$b->{'_name'} = $rep_id;

					$b->{'PartID'} = $cdi_name;
					$b->{'PartName'} = $cdi_name_e;
					$b->{'PartColor'} = qq|FFFFFF| unless(defined $b->{'PartColor'});
					$b->{'PartOpacity'} = 1 unless(defined $b->{'PartOpacity'});
					$b->{'PartOpacity'} += 0;
					$b->{'PartScalarFlag'} = $b->{'PartScalarFlag'}==JSON::XS::true ? 1 : 0;
					$b->{'UseForBoundingBoxFlag'} = $b->{'UseForBoundingBoxFlag'}==JSON::XS::true ? 1 : 0;
					$b->{'PartDeleteFlag'} = $b->{'PartDeleteFlag'}==JSON::XS::true ? 1 : 0;
=cut

					my $obj_prefix = sprintf(DEF_ART_FILE_PREFIX(),$rep_id);
					unless(-e $obj_prefix){
						my $m = umask(0);
						&File::Path::mkpath($obj_prefix,0,0777);
						umask($m);
					}

					$sth_art->execute($rep_id);
print $LOG __LINE__,":\$rows=[",$sth_art->rows,"]\n";
					if($sth_art->rows>0){
						my $art_id;
						my $art_ext;
						my $hist_serial;
						my $art_timestamp;
						my $art_data;
						my $art_data_size;
						my $art_decimate;
						my $art_decimate_size;

						my $art_xmin;
						my $art_xmax;
						my $art_ymin;
						my $art_ymax;
						my $art_zmin;
						my $art_zmax;
						my $art_volume;

						my $column_number = 0;
						$sth_art->bind_col(++$column_number, \$art_id, undef);
						$sth_art->bind_col(++$column_number, \$art_ext, undef);
						$sth_art->bind_col(++$column_number, \$hist_serial, undef);
						$sth_art->bind_col(++$column_number, \$art_timestamp, undef);
						$sth_art->bind_col(++$column_number, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
						$sth_art->bind_col(++$column_number, \$art_data_size, undef);
						$sth_art->bind_col(++$column_number, \$art_decimate, { pg_type => DBD::Pg::PG_BYTEA });
						$sth_art->bind_col(++$column_number, \$art_decimate_size, undef);

						$sth_art->bind_col(++$column_number, \$art_xmin, undef);
						$sth_art->bind_col(++$column_number, \$art_xmax, undef);
						$sth_art->bind_col(++$column_number, \$art_ymin, undef);
						$sth_art->bind_col(++$column_number, \$art_ymax, undef);
						$sth_art->bind_col(++$column_number, \$art_zmin, undef);
						$sth_art->bind_col(++$column_number, \$art_zmax, undef);

						$sth_art->bind_col(++$column_number, \$art_volume, undef);
						while($sth_art->fetch){
#							next if(exists $obj_files_hash->{$art_id});
							my $obj_file = &catfile($obj_prefix,sprintf($art_file_fmt,$art_id,$hist_serial,$art_ext));
							unless(exists $obj_files_hash->{$art_id}){
#								unless(-e $obj_file && -s $obj_file == $art_decimate_size && (stat($obj_file))[9]<=$art_timestamp){
								unless(-e $obj_file && -s $obj_file == $art_data_size && (stat($obj_file))[9]<=$art_timestamp){
									open(OUT,"> $obj_file") or die $!,"\n";
									flock(OUT,2);
									binmode(OUT);
									print OUT $art_data;
									close(OUT);

									chmod 0666,$obj_file;
									utime $art_timestamp,$art_timestamp, $obj_file;
								}
							}
							next unless(-e $obj_file && -s $obj_file);

							my $a = exists $Part->{$cdi_name} ?  $Part->{$cdi_name} : (exists $Part->{$cdi_name_e} ? $Part->{$cdi_name_e} : undef);
							next unless(defined $a);

							if(exists $obj_files_hash->{$art_id}){
								$obj_files_hash->{$art_id}->{'focused'} = JSON::XS::true if(defined $a->{'UseForBoundingBoxFlag'} && $a->{'UseForBoundingBoxFlag'} == JSON::XS::true);
							}else{
								my $b = {};


								$b->{'model'} = $md_abbr;
								$b->{'version'} = $mv_name;

								$b->{'filesize'} = $art_data_size + 0;
								$b->{'conv_size'} = $art_decimate_size+ 0;

								$b->{'xmin'} = $art_xmin+ 0;
								$b->{'xmax'} = $art_xmax+ 0;
								$b->{'ymin'} = $art_ymin+ 0;
								$b->{'ymax'} = $art_ymax+ 0;
								$b->{'zmin'} = $art_zmin+ 0;
								$b->{'zmax'} = $art_zmax+ 0;

								$b->{'volume'} = $art_volume+ 0;
								$b->{'modified'} = $art_timestamp+ 0;
								$b->{'mtime'} = $art_timestamp+ 0;

								$b->{'path'} = &abs2rel($obj_file, $base_path);

								$b->{'rep_id'} = $rep_id;
								$b->{'art_id'} = $art_id;
								$b->{'c_art_id'} = $art_id;
								$b->{'md_id'} = $md_id;
								$b->{'mv_id'} = $mv_id;
								$b->{'mr_id'} = $mr_id;
								$b->{'bul_id'} = $bul_id;
								$b->{'bul_abbr'} = $bul_abbr;

								$b->{'cdi_name'} = $cdi_name;
								$b->{'cdi_name_j'} = $cdi_name_j;
								$b->{'cdi_name_e'} = $cdi_name_e;

								$b->{'color'} = '#'.$a->{'PartColor'} if(defined $a->{'PartColor'});
								$b->{'opacity'} = $a->{'PartOpacity'}+0 if(defined $a->{'PartOpacity'});
								$b->{'remove'} = JSON::XS::true if(defined $a->{'PartDeleteFlag'} && $a->{'PartDeleteFlag'} == JSON::XS::true);
								$b->{'focused'} = JSON::XS::true if(defined $a->{'UseForBoundingBoxFlag'} && $a->{'UseForBoundingBoxFlag'} == JSON::XS::true);
								$b->{'representation'} = $a->{'PartRepresentation'} if(defined $a->{'PartRepresentation'});

								$b->{'scalar'} = $a->{'PartScalar'}+0 if(defined $a->{'PartScalar'});
								$b->{'scalar_flag'} = JSON::XS::true if(defined $a->{'PartScalarFlag'} && $a->{'PartScalarFlag'} == JSON::XS::true);

								$b->{'selected'} = JSON::XS::true;

	#							$b->{'PartOpacity'} += 0;
	#							$b->{'PartScalarFlag'} = $b->{'PartScalarFlag'}==JSON::XS::true ? 1 : 0;
	#							$b->{'UseForBoundingBoxFlag'} = $b->{'UseForBoundingBoxFlag'}==JSON::XS::true ? 1 : 0;
	#							$b->{'PartDeleteFlag'} = $b->{'PartDeleteFlag'}==JSON::XS::true ? 1 : 0;
								push(@$obj_files,$b);
	#=cut
	#							$obj_files_hash->{$art_id} = undef;
								$obj_files_hash->{$art_id} = $b;
							}
						}
					}
					$sth_art->finish;

#					push(@$obj_files,$b) if(scalar @{$b->{'_files'}});
				}
				$sth->finish;
				undef $sth;
				undef $sth_art;
			}

		}

#		$json->{'Part'} = $obj_files;
	}

#print $LOG __LINE__,":\$obj_files=['",join("','",@$obj_files),"']\n" if(defined $obj_files);



#	return $json;
	return $obj_files;
}
