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
use BITS::ConceptArtMapPart;

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $cgi = CGI->new;
&getParams($cgi,\%FORM,\%COOKIE);
my($logfile,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

$FORM{$_} = &cgi_lib::common::decodeUTF8($FORM{$_}) for(keys(%FORM));

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
#$logfile .= '.'.sprintf("%04d%02d%02d%02d",$year+1900,$mon+1,$mday,$hour);
$logfile .=  sprintf(".%02d%02d%02d.%05d",$hour,$min,$sec,$$);

#open(my $TRACE,">> $logfile.trace");
#select($TRACE);
#$| = 1;
#select(STDOUT);
#$dbh->trace('3|SQL', $TRACE);
#$dbh->trace('3|SQL', "$logfile.trace");

open(my $LOG,">> $logfile");
select($LOG);
$| = 1;
select(STDOUT);

flock($LOG,2);
print $LOG "\n[$logtime]:$0\n";
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);

#&setDefParams(\%FORM,\%COOKIE);

#&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);

#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $DATAS = {
	"datas" => [],
	"total" => 0,
	"success" => JSON::XS::false
};

unless(
	exists $FORM{'ci_id'} && defined $FORM{'ci_id'} =~ /^[0-9]+$/
){
	$DATAS->{'msg'} = qq|JSON形式が違います|;
	&utf8::decode($DATAS->{'msg'}) unless(&Encode::is_utf8($DATAS->{'msg'}));
	&gzip_json($DATAS);
	exit;
}

eval{
	my $operator = &get_ludia_operator();
	my $query;
	if(exists $FORM{'query'} && defined $FORM{'query'}){
		$query = $FORM{'query'};
		my $space = qq|　|;
		$query = &cgi_lib::common::decodeUTF8($query);
		$space = &cgi_lib::common::decodeUTF8($space);
		$query =~ s/$space/ /g;
		$query =~ s/\s{2,}/ /g;
#		$query = &cgi_lib::common::encodeUTF8($query);
	}
	my @SORT;
	if(exists $FORM{'sort'} && defined $FORM{'sort'}){
		my $sort = &cgi_lib::common::decodeJSON($FORM{'sort'});
		push(@SORT,map {
			$_->{'direction'} = 'ASC' unless(exists $_->{'direction'} && defined $_->{'direction'});
			$_;
		} grep {exists $_->{'property'} && defined $_->{'property'}} @$sort) if(defined $sort && ref $sort eq 'ARRAY');
	}
	if(scalar @SORT == 0){
		push(@SORT,{
			property  => 'cdi_name_e',
			direction => 'ASC'
		});
	}

	my $sql=<<SQL;
select
 cdi.ci_id,
 cdi_name,
 cdi_name_j,
 cdi_name_e,
 cdi_name_k,
 cdi_name_l,
 cdi.cdi_id,
 COALESCE(cm.art_num,0) as art_num
-- cm.art_num
from 
 concept_data_info as cdi

left join (
  select
   ci_id,
   cdi_id,
   count(*) as art_num
  from
   concept_art_map as cm
  WHERE
   cm_delcause is null
  GROUP BY
   ci_id,
   cdi_id
) as cm on
  cm.ci_id=cdi.ci_id AND
  cm.cdi_id=cdi.cdi_id

where (cdi.ci_id,cdi.cdi_id) in (
 select
  cdi.ci_id,
  cdi.cdi_id
 from 
  concept_data_info as cdi
 left join (
  select
   ci_id,
   cdi_id,
   art_id
  from
   concept_art_map
  WHERE
   cm_delcause is null
 ) as cm on
  cm.ci_id=cdi.ci_id AND
  cm.cdi_id=cdi.cdi_id

 where
  cdi_delcause is null AND
  cdi.ci_id=$FORM{'ci_id'}
SQL
	if(exists $FORM{'query'} && defined $FORM{'query'}){
#		$sql.=<<SQL;
#  AND (ARRAY[cdi_name,cdi_name_j,cdi_name_e,cdi_name_k,cdi_name_l,art_id] $operator ?)
#SQL
		$sql.=<<SQL;
  AND (ARRAY[cdi_name,cdi_name_j,cdi_name_e,cdi_name_k,cdi_name_l] $operator ?)
SQL
	}elsif(exists $FORM{'cdi_name_e'} && defined $FORM{'cdi_name_e'}){
		$sql.=<<SQL;
  AND  lower(cdi_name_e)=lower(?)
SQL
	}elsif(exists $FORM{'cdi_name'} && defined $FORM{'cdi_name'}){
		if(exists $FORM{'cmp_id'} && defined $FORM{'cmp_id'} && $FORM{'cmp_id'}){
			my $trio_cdi_name = &BITS::ConceptArtMapPart::get_trio_name(%FORM, dbh=>$dbh, LOG=>$LOG);
			&cgi_lib::common::message($trio_cdi_name, $LOG);
			$FORM{'cdi_name'} = $trio_cdi_name if(defined $trio_cdi_name && length $trio_cdi_name && $FORM{'cdi_name'} ne $trio_cdi_name);
			delete $FORM{'cmp_id'};
		}

		$sql.=<<SQL;
  AND lower(cdi_name)=lower(?)
SQL
	}
	$sql.=<<SQL;
)
SQL

	print $LOG __LINE__.":\$sql=[$sql]\n";

	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	if(exists $FORM{'query'} && defined $FORM{'query'}){
		my @bind_values;
		push(@bind_values,qq|*D+ $query|);
		$sth->execute(@bind_values) or die $dbh->errstr;
		print $LOG __LINE__.":\@bind_values=[".&cgi_lib::common::encodeUTF8(join(",",@bind_values))."]\n";
	}elsif(exists $FORM{'cdi_name_e'} && defined $FORM{'cdi_name_e'}){
		$sth->execute($FORM{'cdi_name_e'}) or die $dbh->errstr;
	}elsif(exists $FORM{'cdi_name'} && defined $FORM{'cdi_name'}){
		$sth->execute($FORM{'cdi_name'}) or die $dbh->errstr;
	}else{
		$sth->execute() or die $dbh->errstr;
	}
	print $LOG __LINE__.":\$sth->rows()=[".$sth->rows()."]\n";
	$DATAS->{'total'} = $sth->rows();
	$sth->finish;
	undef $sth;
	print $LOG __LINE__.":\$DATAS->{'total'}=[",$DATAS->{'total'},"]\n";

	if($DATAS->{'total'}>0){
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
		$sql .= qq| limit $FORM{limit}| if(defined $FORM{limit});
		$sql .= qq| offset $FORM{start}| if(defined $FORM{start});

		print $LOG __LINE__.":\$sql=[$sql]\n";

		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		if(exists $FORM{'query'} && defined $FORM{'query'}){
			my @bind_values;
			push(@bind_values,qq|*D+ $query|);
			$sth->execute(@bind_values) or die $dbh->errstr;
		}elsif(exists $FORM{'cdi_name_e'} && defined $FORM{'cdi_name_e'}){
			$sth->execute($FORM{'cdi_name_e'}) or die $dbh->errstr;
		}elsif(exists $FORM{'cdi_name'} && defined $FORM{'cdi_name'}){
			$sth->execute($FORM{'cdi_name'}) or die $dbh->errstr;
		}else{
			$sth->execute() or die $dbh->errstr;
		}
		if($sth->rows()>0){
			my $sth_cm = $dbh->prepare('select art_id,cmp_id from concept_art_map where cm_delcause is null and ci_id=? and cdi_id=? order by art_id') or die $dbh->errstr;

			my $sql_cm = 'select art_id from concept_art_map where cm_delcause is null and ci_id=? and cdi_id=? group by art_id';
			my $sth_art = $dbh->prepare("select art_id,art_xmin,art_xmax,art_ymin,art_ymax,art_zmin,art_zmax from art_file_info where art_delcause is null and art_id in ($sql_cm) order by art_id") or die $dbh->errstr;
			my $sth_art_group = $dbh->prepare("select min(art_xmin),max(art_xmax),min(art_ymin),max(art_ymax),min(art_zmin),max(art_zmax) from art_file_info where art_delcause is null and art_id in ($sql_cm)") or die $dbh->errstr;

			my $ci_id;
			my $cdi_name;
			my $cdi_name_j;
			my $cdi_name_e;
			my $cdi_name_k;
			my $cdi_name_l;
			my $cdi_id;
			my $art_num;

			my $column_number = 0;
			$sth->bind_col(++$column_number, \$ci_id,   undef);
			$sth->bind_col(++$column_number, \$cdi_name,   undef);
			$sth->bind_col(++$column_number, \$cdi_name_j,   undef);
			$sth->bind_col(++$column_number, \$cdi_name_e,   undef);
			$sth->bind_col(++$column_number, \$cdi_name_k,   undef);
			$sth->bind_col(++$column_number, \$cdi_name_l,   undef);
			$sth->bind_col(++$column_number, \$cdi_id,   undef);
			$sth->bind_col(++$column_number, \$art_num,   undef);

			while($sth->fetch){
				my $art_ids = [];
				my $art_xmin;
				my $art_xmax;
				my $art_ymin;
				my $art_ymax;
				my $art_zmin;
				my $art_zmax;
				if(defined $ci_id && defined $cdi_id && defined $art_num && $art_num>0){
					my $art_id;
					my $cmp_id;
					my %CMP;
					$sth_cm->execute($ci_id,$cdi_id) or die $dbh->errstr;
					$column_number = 0;
					$sth_cm->bind_col(++$column_number, \$art_id,   undef);
					$sth_cm->bind_col(++$column_number, \$cmp_id,   undef);
					while($sth_cm->fetch){
						next unless(defined $art_id);
						$CMP{$art_id} = $cmp_id-0;
					}
					$sth_cm->finish;


					$sth_art->execute($ci_id,$cdi_id) or die $dbh->errstr;
					$column_number = 0;
					$sth_art->bind_col(++$column_number, \$art_id,   undef);
					$sth_art->bind_col(++$column_number, \$art_xmin,   undef);
					$sth_art->bind_col(++$column_number, \$art_xmax,   undef);
					$sth_art->bind_col(++$column_number, \$art_ymin,   undef);
					$sth_art->bind_col(++$column_number, \$art_ymax,   undef);
					$sth_art->bind_col(++$column_number, \$art_zmin,   undef);
					$sth_art->bind_col(++$column_number, \$art_zmax,   undef);
					while($sth_art->fetch){
						next unless(defined $art_id);
						push(@$art_ids,{
							art_id   => $art_id,
							art_xmin => $art_xmin-0,
							art_xmax => $art_xmax-0,
							art_ymin => $art_ymin-0,
							art_ymax => $art_ymax-0,
							art_zmin => $art_zmin-0,
							art_zmax => $art_zmax-0,
							cmp_id   => $CMP{$art_id},
						});
					}
					$sth_art->finish;

					$art_xmin = undef;
					$art_xmax = undef;
					$art_ymin = undef;
					$art_ymax = undef;
					$art_zmin = undef;
					$art_zmax = undef;

					$sth_art_group->execute($ci_id,$cdi_id) or die $dbh->errstr;
					$column_number = 0;
					$sth_art_group->bind_col(++$column_number, \$art_xmin,   undef);
					$sth_art_group->bind_col(++$column_number, \$art_xmax,   undef);
					$sth_art_group->bind_col(++$column_number, \$art_ymin,   undef);
					$sth_art_group->bind_col(++$column_number, \$art_ymax,   undef);
					$sth_art_group->bind_col(++$column_number, \$art_zmin,   undef);
					$sth_art_group->bind_col(++$column_number, \$art_zmax,   undef);
					$sth_art_group->fetch;
					$sth_art_group->finish;

					$art_xmin -= 0 if(defined $art_xmin);
					$art_xmax -= 0 if(defined $art_xmax);
					$art_ymin -= 0 if(defined $art_ymin);
					$art_ymax -= 0 if(defined $art_ymax);
					$art_zmin -= 0 if(defined $art_zmin);
					$art_zmax -= 0 if(defined $art_zmax);
				}

				my $HASH = {
					ci_id      => $ci_id-0,
					cdi_id     => $cdi_id-0,
					cdi_name   => $cdi_name,
					cdi_name_j => $cdi_name_j,
					cdi_name_e => $cdi_name_e,
					cdi_name_k => $cdi_name_k,
					cdi_name_l => $cdi_name_l,
					art_num    => defined $art_num ? $art_num-0 : undef,
					art_ids    => $art_ids,

					art_xmin    => $art_xmin,
					art_xmax    => $art_xmax,
					art_ymin    => $art_ymin,
					art_ymax    => $art_ymax,
					art_zmin    => $art_zmin,
					art_zmax    => $art_zmax,
				};

				push(@{$DATAS->{'datas'}},$HASH);
			}
			undef $sth_art;
			undef $sth_art_group;
		}
		$sth->finish;
		undef $sth;
	}
	$DATAS->{'success'} = JSON::XS::true;
};
if($@){
	$DATAS->{'msg'} = $@;
	$DATAS->{'success'} = JSON::XS::false;
}

&gzip_json($DATAS);

close($LOG);
