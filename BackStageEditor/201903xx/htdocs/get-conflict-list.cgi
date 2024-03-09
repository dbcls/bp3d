#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
use BITS::ReCalc;
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

&setDefParams(\%FORM,\%COOKIE);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);

my $DATAS = {
	"datas" => [],
	"total" => 0,
	"success" => JSON::XS::false
};

$FORM{'conflict_type'} = 'conflict' unless(exists $FORM{'conflict_type'} && defined $FORM{'conflict_type'});

#=pod
unless(
	exists $FORM{'md_id'} && defined $FORM{'md_id'} &&
	exists $FORM{'mv_id'} && defined $FORM{'mv_id'} &&
	exists $FORM{'mr_id'} && defined $FORM{'mr_id'} &&
	exists $FORM{'ci_id'} && defined $FORM{'ci_id'} &&
	exists $FORM{'cb_id'} && defined $FORM{'cb_id'}
){
#	print &JSON::XS::encode_json($DATAS);
	&gzip_json($DATAS);
	exit;
}
#=cut

eval{
	my @SORT;
	if(defined $FORM{'sort'}){
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

	my $md_id=$FORM{'md_id'};
	my $mv_id=$FORM{'mv_id'};
	my $mr_id=$FORM{'mr_id'};
	my $ci_id=$FORM{'ci_id'};
	my $cb_id=$FORM{'cb_id'};

	my $sql=<<SQL;
select
 cm.cdi_id,
 cdi_name,
 cdi_name_e,
 cmp_id,
 count(cm.cdi_id)
from
 (select * from concept_art_map where (cdi_id,ci_id,cb_id,md_id,mv_id,mr_id) in (select cdi_id,ci_id,cb_id,md_id,mv_id,max(mr_id) from concept_art_map where ci_id=$ci_id AND cb_id=$cb_id AND md_id=$md_id AND mv_id=$mv_id AND mr_id<=$mr_id group by cdi_id,ci_id,cb_id,md_id,mv_id)) as cm

LEFT JOIN (
 select ci_id,cdi_id,cdi_name,cdi_name_e from concept_data_info where cdi_delcause is null
) as cdi on
   cdi.cdi_id=cm.cdi_id AND
   cdi.ci_id=cm.ci_id

where
 cm.cm_use AND
 cm.cm_delcause IS NULL
group by
 cm.cdi_id,
 cdi_name,
 cdi_name_e,
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
		$sql .= qq| limit $FORM{limit}| if(defined $FORM{limit});
		$sql .= qq| offset $FORM{start}| if(defined $FORM{start});
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

	my $sth_bult = $dbh->prepare(qq|select but_cids from buildup_tree where ci_id=$ci_id AND cb_id=$cb_id AND but_delcause IS NULL AND but_cids IS NOT NULL AND cdi_id=?|) or die $dbh->errstr;

	my $sth_art = $dbh->prepare(qq/
select
 cm.art_id,
 art_filename,
 art.artg_id,
 artg_name,
 art.art_entry,
 art.art_path
from
 (select * from concept_art_map where (cdi_id,ci_id,cb_id,md_id,mv_id,mr_id) in (select cdi_id,ci_id,cb_id,md_id,mv_id,max(mr_id) from concept_art_map where cdi_id=? AND ci_id=$ci_id AND cb_id=$cb_id AND md_id=$md_id AND mv_id=$mv_id AND mr_id<=$mr_id group by cdi_id,ci_id,cb_id,md_id,mv_id)) as cm
LEFT JOIN (
  select art_id,(art_name||art_ext) as art_filename,(art_id||art_ext) as art_path,artg_id,EXTRACT(EPOCH FROM art_entry) as art_entry from art_file_info where art_delcause is null
) as art on
   art.art_id=cm.art_id
LEFT JOIN (
  select artg_id,artg_name from art_group where atrg_use AND artg_delcause is null
) as artg on
    artg.artg_id=art.artg_id
where
 cm.cm_use AND
 cm.cm_delcause IS NULL
/) or die $dbh->errstr;

	while($sth->fetch){
		my $objs = [];
		if($mapped_obj>0){
			$sth_art->execute($cdi_id) or die $dbh->errstr;
			$column_number = 0;
			my $art_id;
			my $art_filename;
			my $artg_id;
			my $artg_name;
			my $art_entry;
			my $art_path;
			$sth_art->bind_col(++$column_number, \$art_id,   undef);
			$sth_art->bind_col(++$column_number, \$art_filename,   undef);
			$sth_art->bind_col(++$column_number, \$artg_id,   undef);
			$sth_art->bind_col(++$column_number, \$artg_name,   undef);
			$sth_art->bind_col(++$column_number, \$art_entry,   undef);
			$sth_art->bind_col(++$column_number, \$art_path,   undef);
			while($sth_art->fetch){
				push(@$objs,{
					cm_use       => JSON::XS::true,
					art_id       => $art_id,
					art_filename => $art_filename,
					artg_id      => $artg_id,
					artg_name    => $artg_name,
					art_entry    => $art_entry,
					art_path     => $art_path,
					cdi_name     => $cdi_name,
					cdi_name_e   => $cdi_name_e,
					cmp_id       => $cmp_id,
				});
			}
			$sth_art->finish;
		}
		my $mapped_obj_c = 0;
		if(defined $HASH_CHILD && ref $HASH_CHILD eq 'HASH' && $FORM{'conflict_type'} eq 'children'){
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
#print &JSON::XS::encode_json($DATAS);
&gzip_json($DATAS);

close($LOG);
