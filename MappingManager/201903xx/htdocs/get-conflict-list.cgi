#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
use BITS::ReCalc;

use BITS::ConceptArtMapPart;
my $is_subclass_cdi_name = $BITS::ConceptArtMapPart::is_subclass_cdi_name;

require "webgl_common.pl";
use cgi_lib::common;

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $cgi = CGI->new;
&getParams($cgi,\%FORM,\%COOKIE);
my($logfile,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

=pod
$FORM{ag_data}=qq|obj/bp3d/4.0|;
$FORM{f_id}=qq|root|;
$FORM{model}=qq|bp3d|;
$FORM{node}=qq|root|;
$FORM{tree}=qq|isa|;
$FORM{version}=qq|4.0|;
=cut

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
$logfile .=  sprintf(".%02d%02d%02d.%05d",$hour,$min,$sec,$$);

open(my $LOG,">> $logfile");
select($LOG);
$| = 1;
select(STDOUT);

flock($LOG,2);
print $LOG "\n[$logtime]:$0\n";
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);

#&setDefParams(\%FORM,\%COOKIE);
#&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);

#&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
#&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);

my $DATAS = {
	"datas" => [],
	"total" => 0,
	"success" => JSON::XS::false
};

$FORM{'conflict_type'} = 'conflict' unless(exists $FORM{'conflict_type'} && defined $FORM{'conflict_type'});


my $ci_id=$FORM{'ci_id'};
my $cb_id=$FORM{'cb_id'};
my $md_id=$FORM{'md_id'};
my $mv_id=$FORM{'mv_id'};

$md_id=1 unless(defined $md_id && $md_id =~ /^[1-9][0-9]*$/);
unless(defined $mv_id && $mv_id =~ /^[1-9][0-9]*$/){
	$mv_id = undef;
	$ci_id = undef;
	$cb_id = undef;
	my $sth_mv;
	if(defined $FORM{'mv_id'} && $FORM{'mv_id'} =~ /^\-[1-9][0-9]*$/){
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
	$DATAS->{'success'} = JSON::XS::true;
	&cgi_lib::common::printContentJSON($DATAS,\%FORM);
	close($LOG) if(defined $LOG);
	exit;
}
if(defined $LOG){
	&cgi_lib::common::message('$md_id='.$md_id, $LOG);
	&cgi_lib::common::message('$mv_id='.$mv_id, $LOG);
	&cgi_lib::common::message('$ci_id='.$ci_id, $LOG);
	&cgi_lib::common::message('$cb_id='.$cb_id, $LOG);
}
$FORM{'ci_id'}=$ci_id;
$FORM{'cb_id'}=$cb_id;
$FORM{'md_id'}=$md_id;
$FORM{'mv_id'}=$mv_id;


#=pod
unless(
	exists $FORM{'ci_id'} && defined $FORM{'ci_id'}
){
#	print &JSON::XS::encode_json($DATAS);
	&gzip_json($DATAS);
	exit;
}
#=cut

eval{
	my @SORT;
	if(exists $FORM{'sort'} && defined $FORM{'sort'}){
		my $sort = &cgi_lib::common::decodeJSON($FORM{'sort'});
		push(@SORT,map {
			$_->{'direction'} = 'ASC' unless(exists $_->{'direction'} && defined $_->{'direction'} && length $_->{'direction'});
			$_;
		} grep {exists $_->{'property'} && defined $_->{'property'} && length $_->{'property'}} @$sort) if(defined $sort && ref $sort eq 'ARRAY');
	}
	if(scalar @SORT == 0){
		push(@SORT,{
			property  => 'cdi_name_e',
			direction => 'ASC'
		});
	}

#	my $ci_id=$FORM{'ci_id'};

	my $sql=<<SQL;
select
 cm.cdi_id,
 cdi_name,
 cd_name as cdi_name_e,
 cmp_id,
 count(cm.cdi_id)
from
 concept_art_map as cm

LEFT JOIN (
 select ci_id,cdi_id,cdi_name from concept_data_info where cdi_delcause is null
) as cdi on
   cdi.cdi_id=cm.cdi_id AND
   cdi.ci_id=cm.ci_id

LEFT JOIN (
 select ci_id,cb_id,cdi_id,cd_name from concept_data where cd_delcause is null and ci_id=$ci_id and cb_id=$cb_id
) as cd on
   cd.cdi_id=cm.cdi_id AND
   cd.ci_id=cm.ci_id

where
 cm.cm_delcause IS NULL and
 cm.md_id=$md_id AND
 cm.mv_id=$mv_id
group by
 cm.cdi_id,
 cdi_name,
 cd_name,
 cmp_id
SQL

#	unless($FORM{'conflict_type'} eq 'children'){
#		$sql .= ' HAVING count(cm.cdi_id)>1';
#	}

	&cgi_lib::common::message("\$sql=[$sql]", $LOG);

	my $cdi_id;
	my $cdi_name;
	my $cdi_name_e;
	my $cmp_id;
	my $mapped_obj;
	my $art_id;
	my $art_filename;
	my $artg_name;

	my $HASH_CHILD;

	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$DATAS->{'total'} = $sth->rows();
	if($FORM{'conflict_type'} eq 'children'){
		$sth->execute() or die $dbh->errstr;
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_id,   undef);
		$sth->bind_col(++$column_number, \$cdi_name,   undef);
		$sth->bind_col(++$column_number, \$cdi_name_e,   undef);
		$sth->bind_col(++$column_number, \$cmp_id,   undef);
		$sth->bind_col(++$column_number, \$mapped_obj,   undef);
		while($sth->fetch){
			$HASH_CHILD->{$cdi_id} = $mapped_obj;
		}
	}
	$sth->finish;
	undef $sth;
	&cgi_lib::common::message("\$DATAS->{'total'}=[".$DATAS->{'total'}."]", $LOG);

	if(scalar @SORT > 0){
		my @orderby;
		foreach (@SORT){
			if($_->{property} eq 'rep_id'){
				push(@orderby,qq|$_->{property} $_->{direction} NULLS LAST|);
			}else{
				push(@orderby,qq|$_->{property} $_->{direction}|);
			}
		}
		$sql .= qq| order by | . join(",",@orderby) if(scalar @orderby > 0);
	}
	unless(1 || $FORM{'conflict_type'} eq 'children'){
		$sql .= qq| limit $FORM{limit}|  if(exists $FORM{limit} && defined $FORM{limit});
		$sql .= qq| offset $FORM{start}| if(exists $FORM{start} && defined $FORM{start});
	}

	&cgi_lib::common::message("\$sql=[$sql]", $LOG);

	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;



	my $column_number = 0;
	$sth->bind_col(++$column_number, \$cdi_id,   undef);
	$sth->bind_col(++$column_number, \$cdi_name,   undef);
	$sth->bind_col(++$column_number, \$cdi_name_e,   undef);
	$sth->bind_col(++$column_number, \$cmp_id,   undef);
	$sth->bind_col(++$column_number, \$mapped_obj,   undef);
#	$sth->bind_col(++$column_number, \$art_id,   undef);
#	$sth->bind_col(++$column_number, \$art_filename,   undef);
#	$sth->bind_col(++$column_number, \$artg_name,   undef);

#	my $sth_bult = $dbh->prepare(qq|select but_cids from buildup_tree where ci_id=$ci_id AND cb_id=$cb_id AND but_delcause IS NULL AND but_cids IS NOT NULL AND cdi_id=?|) or die $dbh->errstr;

	my $sth_art = $dbh->prepare(qq{
select
 cm.art_id,
 art_filename,
 art.art_entry,
 art.art_path,
 art.art_timestamp
from
 concept_art_map as cm
LEFT JOIN (
  select
   art_id,
   (art_name||art_ext) as art_filename,
   ('art_file/'||art_id||art_ext) as art_path,
   EXTRACT(EPOCH FROM art_entry) as art_entry,
   EXTRACT(EPOCH FROM art_timestamp) as art_timestamp
  from
   art_file_info
  where
   art_delcause is null
) as art on
   art.art_id=cm.art_id
where
 cm.cm_delcause IS NULL AND
 cm.md_id=$md_id AND
 cm.mv_id=$mv_id AND
 cm.cdi_id=?
}) or die $dbh->errstr;

	my $sth_aff = $dbh->prepare(qq|select COALESCE(aff.artf_id,0) as artf_id, COALESCE(af.artf_name,'/') as artf_name from art_folder_file as aff left join (select * from art_folder) as af on aff.artf_id=af.artf_id where artff_delcause is null and artf_delcause is null and art_id=? order by aff.artff_timestamp desc NULLS FIRST limit 1|) or die $dbh->errstr;

	my $sth_cmp_id_sel = $dbh->prepare(qq|select cmp_id from concept_art_map_part where cmp_abbr=?|) or die $dbh->errstr;

	while($sth->fetch){
		my $objs = [];
		if($mapped_obj>0){
			$sth_art->execute($cdi_id) or die $dbh->errstr;
			$column_number = 0;
			my $art_id;
			my $art_filename;
			my $art_entry;
			my $art_path;
			my $art_timestamp;
			$sth_art->bind_col(++$column_number, \$art_id,   undef);
			$sth_art->bind_col(++$column_number, \$art_filename,   undef);
			$sth_art->bind_col(++$column_number, \$art_entry,   undef);
			$sth_art->bind_col(++$column_number, \$art_path,   undef);
			$sth_art->bind_col(++$column_number, \$art_timestamp,   undef);
			while($sth_art->fetch){

				my $artf_id;
				my $artf_name;
				$sth_aff->execute($art_id) or die $dbh->errstr;
				$sth_aff->bind_col(1, \$artf_id, undef);
				$sth_aff->bind_col(2, \$artf_name, undef);
				$sth_aff->fetch;
				$sth_aff->finish;

				if(defined $cdi_name && $cdi_name =~ /$is_subclass_cdi_name/){
					$cdi_name = $1;
					my $cmp_abbr = $2;
					$sth_cmp_id_sel->execute($cmp_abbr) or die $dbh->errstr;
					my $cmp_rows = $sth_cmp_id_sel->rows();
					my $hash_cmp;
					$hash_cmp = $sth_cmp_id_sel->fetchrow_hashref if($cmp_rows>0);
					$sth_cmp_id_sel->finish;
					$cmp_id = $hash_cmp->{'cmp_id'} if(defined $hash_cmp && ref $hash_cmp eq 'HASH' && exists $hash_cmp->{'cmp_id'} && defined $hash_cmp->{'cmp_id'});
				}

				push(@$objs,{
					art_id        => $art_id,
					art_filename  => $art_filename,
					art_entry     => $art_entry-0,
					art_timestamp => $art_timestamp-0,
					art_path      => $art_path,
					cdi_name      => $cdi_name,
					cdi_name_e    => $cdi_name_e,
					cmp_id        => $cmp_id,
					artf_id       => $artf_id,
					artf_name     => $artf_name,
				});
			}
			$sth_art->finish;
		}
		my $mapped_obj_c = 0;
		if(defined $HASH_CHILD && ref $HASH_CHILD eq 'HASH' && $FORM{'conflict_type'} eq 'children'){
=pod
			$sth_bult->execute($cdi_id) or die $dbh->errstr;
			$column_number = 0;
			my $but_cids;
			$sth_bult->bind_col(++$column_number, \$but_cids,   undef);
			while($sth_bult->fetch){
				&cgi_lib::common::message("\$but_cids=[$but_cids]", $LOG);
				eval{$but_cids = &JSON::XS::decode_json($FORM{'but_cids'});};
				if(defined $but_cids && ref $but_cids eq 'ARRAY'){
					foreach my $but_cid (@$but_cids){
						next unless(exists $HASH_CHILD->{$but_cid} && defined $HASH_CHILD->{$but_cid});
						$mapped_obj += $HASH_CHILD->{$but_cid};
						$mapped_obj_c += $HASH_CHILD->{$but_cid};
						&cgi_lib::common::message("\$mapped_obj=[$mapped_obj]", $LOG);
					}
				}
			}
			$sth_bult->finish;
#			next if($mapped_obj<=1);
=cut
		}
#		next if($mapped_obj>1);

		my $HASH = {
			cdi_name     => $cdi_name,
			cdi_name_e   => $cdi_name_e,
			cmp_id       => $cmp_id-0,
			mapped_obj   => $mapped_obj-0,
			mapped_obj_c => $mapped_obj_c-0,
			objs         => $objs,
#			art_filename => $art_filename,
#			artg_name    => $artg_name,
		};

		push(@{$DATAS->{'datas'}},$HASH);
	}
	$sth->finish;
	undef $sth;

	$DATAS->{'success'} = JSON::XS::true;
};
if($@){
	$DATAS->{'msg'} = $@;
}
$DATAS->{'total'} -= 0;

#print &JSON::XS::encode_json($DATAS);
&gzip_json($DATAS);

close($LOG);
