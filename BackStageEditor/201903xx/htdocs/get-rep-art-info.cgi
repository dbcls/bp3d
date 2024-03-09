#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use JSON::XS;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
require "webgl_common.pl";

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);
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

open(LOG,"> $logfile");
flock(LOG,2);
print LOG "\n[$logtime]:$0\n";
foreach my $key (sort keys(%FORM)){
	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
}
#foreach my $key (sort keys(%COOKIE)){
#	print LOG "\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
#}
#foreach my $key (sort keys(%ENV)){
#	print LOG __LINE__,":\$ENV{$key}=[",$ENV{$key},"]\n";
#}

&setDefParams(\%FORM,\%COOKIE);
foreach my $key (sort keys(%FORM)){
	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
}

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
foreach my $key (sort keys(%FORM)){
	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
}

#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $DATAS = {
	"datas" => [],
	"total" => 0
};

my $sql_art;
my $rep_ids;
if(defined $FORM{'rep_ids'}){
	eval{$rep_ids = &JSON::XS::decode_json($FORM{'rep_ids'});};
	if(defined $rep_ids && ref $rep_ids eq 'ARRAY'){
=pod
		my $sql_art =<<SQL;
select distinct
 hart.art_id,
 arti.artg_id
from
 history_art_file as hart
left join (
 select * from art_file_info
) as arti on arti.art_id=hart.art_id
where
 (hart.art_id,hist_serial) in (
  select art_id,art_hist_serial from representation_art where rep_id=?
 )
SQL
=cut
		my $sql_art_fmt =<<SQL;
select distinct
 art_id,
 artg_id
from
 art_file_info
where
 art_id in (
  select
   cm.art_id
  from (
   select * from concept_art_map where (ci_id,cb_id,md_id,mv_id,mr_id,cdi_id) in (
    select ci_id,cb_id,md_id,mv_id,max(mr_id),cdi_id from concept_art_map
    where
     ci_id=$FORM{ci_id} and
     cb_id=$FORM{cb_id} and
     md_id=$FORM{md_id} and
     mv_id=$FORM{mv_id} and
     mr_id<=$FORM{mr_id}
    group by ci_id,cb_id,md_id,mv_id,cdi_id
   )
  ) as cm
  where
   cm.cm_use and
   cm.cm_delcause is null and
   cdi_id in (
     select
      cdi_id
     from
      representation
     where
      rep_id in (%s)
   )
)
SQL
		$sql_art = sprintf($sql_art_fmt,join(',',map {'?'} @$rep_ids));

	}
}
elsif(defined $FORM{'cdi_names'}){
	my $cdi_names;
	eval{$cdi_names = &JSON::XS::decode_json($FORM{'cdi_names'});};
	if(defined $cdi_names && ref $cdi_names eq 'ARRAY'){
		my $cdi_ids;
		my $sql = sprintf(qq|select cdi_id,but_cids from view_buildup_tree where ci_id=$FORM{ci_id} and cb_id=$FORM{cb_id} and bul_id=$FORM{bul_id} and cdi_name in (%s)|,join(',',map {'?'} @$cdi_names));
		print LOG __LINE__,":\$sql=[",$sql,"]\n";
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute(@$cdi_names) or die $dbh->errstr;
		while(my $row = $sth->fetchrow_hashref){
			my $but_cids = &JSON::XS::decode_json($row->{'but_cids'}) if(exists $row->{'but_cids'} && defined $row->{'but_cids'});
			if(defined $but_cids){
				foreach my $but_cid (@$but_cids){
					$cdi_ids->{$but_cid} = undef;
				}
			}
			$cdi_ids->{$row->{'cdi_id'}} = undef if(exists $row->{'cdi_id'} && defined $row->{'cdi_id'});
		}
		$sth->finish;
		undef $sth;
		push(@$rep_ids,keys(%$cdi_ids)) if(defined $cdi_ids);
		print LOG __LINE__,":\$cdi_ids=[",$cdi_ids,"]\n";
	}
	print LOG __LINE__,":\$rep_ids=[",$rep_ids,"]\n";
	if(defined $rep_ids){
		my $sql_art_fmt =<<SQL;
select distinct
 art_id,
 artg_id
from
 art_file_info
where
 art_id in (
  select
   cm.art_id
  from (
   select * from concept_art_map where (ci_id,cb_id,md_id,mv_id,mr_id,cdi_id) in (
    select ci_id,cb_id,md_id,mv_id,max(mr_id),cdi_id from concept_art_map
    where
     ci_id=$FORM{ci_id} and
     cb_id=$FORM{cb_id} and
     md_id=$FORM{md_id} and
     mv_id=$FORM{mv_id} and
     mr_id<=$FORM{mr_id}
    group by ci_id,cb_id,md_id,mv_id,cdi_id
   )
  ) as cm
  where
   cm.cm_use and
   cm.cm_delcause is null and
   cdi_id in (%s)
)
SQL
		$sql_art = sprintf($sql_art_fmt,join(',',map {'?'} @$rep_ids));
		print LOG __LINE__,":\$sql_art=[",$sql_art,"]\n";
		print LOG __LINE__,":\$rep_ids=[",join(',',@$rep_ids),"]\n";
	}
}

if(defined $sql_art && defined $rep_ids){
	my $sth_art = $dbh->prepare($sql_art) or die $dbh->errstr;

	my $HASH;
	$sth_art->execute(@$rep_ids) or die $dbh->errstr;
	my $art_id;
	my $artg_id;
	my $column_number = 0;
	$sth_art->bind_col(++$column_number, \$art_id,   undef);
	$sth_art->bind_col(++$column_number, \$artg_id,   undef);
	while($sth_art->fetch){
		next unless(defined $art_id && defined $artg_id);
		push(@{$HASH->{'artg_ids'}->{$artg_id+0}},$art_id);
		$HASH->{'art_ids'}->{$art_id} = $artg_id+0;
	}
	$sth_art->finish;
	push(@{$DATAS->{'datas'}},{data => $HASH}) if(defined $HASH);

	$DATAS->{'total'} = scalar @{$DATAS->{'datas'}};

	undef $sth_art;
}
#print &JSON::XS::encode_json($DATAS);
&gzip_json($DATAS);

close(LOG);
