#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
require "webgl_common.pl";
use cgi_lib::common;

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
$logfile .=  sprintf(".%02d%02d%02d.%05d",$hour,$min,$sec,$$);

open(my $LOG,"> $logfile");
select($LOG);
$| = 1;
select(STDOUT);

flock($LOG,2);
print $LOG "\n[$logtime]:$0\n";
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);

#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $DATAS = {
	'datas'   => [],
	'total'   => 0,
	'success' => JSON::XS::false
};

unless(
	exists $FORM{'cmd'} && defined $FORM{'cmd'} &&
	exists $FORM{'ci_id'} && defined $FORM{'ci_id'} &&
	exists $FORM{'cb_id'} && defined $FORM{'cb_id'}
){
#	print &JSON::XS::encode_json($DATAS);
	&gzip_json($DATAS);
	exit;
}

if($FORM{'cmd'} eq 'read'){
	eval{
		my $ci_id = $FORM{'ci_id'};
		my $cb_id = $FORM{'cb_id'};

		my @SORT;
		if(defined $FORM{'sort'}){
			my $sort = &cgi_lib::common::decodeJSON($FORM{'sort'});
			push(@SORT,@$sort) if(defined $sort && ref $sort eq 'ARRAY');
		}
		if(scalar @SORT == 0){
			push(@SORT,{
				property  => 'cdi_name',
				direction => 'ASC'
			});
		}
		my $sql=<<SQL;
select
 cdi.cdi_id,
 cdi.cdi_name,
 cdi.cdi_name_j,
 cdi.cdi_name_e,
 cdi.cdi_name_k,
 cdi.cdi_name_l,
 cdi.cdi_syn_j,
 cdi.cdi_syn_e,
 cdi.cdi_def_j,
 cdi.cdi_def_e,
 cdi.cdi_taid,
 COALESCE(but2.c,1),
 COALESCE(but2.m,3)
from
 (
   select ci_id,cb_id,cdi_id from concept_data where ci_id=$ci_id AND cb_id=$cb_id
 ) as but

left join (
 select * from concept_data_info
) as cdi on
   but.ci_id=cdi.ci_id AND
   but.cdi_id=cdi.cdi_id

left join (
  select
   ci_id,
   cb_id,
   cdi_id,
   count(bul_id) as c,
   max(bul_id) as m
  from (
    select
     ci_id,
     cb_id,
     cdi_id,
     bul_id
    from
     concept_tree
    where
     ci_id=$ci_id AND
     cb_id=$cb_id
    group by
     ci_id,
     cb_id,
     cdi_id,
     bul_id
  ) as a
  group by
   ci_id,
   cb_id,
   cdi_id

) as but2 on
   but.ci_id=but2.ci_id AND
   but.cb_id=but2.cb_id AND
   but.cdi_id=but2.cdi_id

where
 cdi_delcause is null
SQL

		print $LOG __LINE__,":\$sql=[$sql]\n";

		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$DATAS->{'total'} = $sth->rows();
		$sth->finish;
		undef $sth;
		print $LOG __LINE__,":\$DATAS->{'total'}=[",$DATAS->{'total'},"]\n";

		if(scalar @SORT > 0){
			my @orderby;
			foreach (@SORT){
				next unless(exists $_->{property} && defined $_->{property} && length $_->{property});
				if($_->{property} eq 'cdi_name'){
					push(@orderby,qq|to_number(substring(cdi_name from 4),'999999') $_->{direction}|);
				}else{
					push(@orderby,qq|$_->{property} $_->{direction} NULLS LAST|);
				}
			}
			$sql .= qq| order by | . join(",",@orderby) if(scalar @orderby > 0);
		}
		$sql .= qq| limit $FORM{limit}| if(defined $FORM{limit});
		$sql .= qq| offset $FORM{start}| if(defined $FORM{start});

		print $LOG __LINE__,":\$sql=[$sql]\n";

		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;

		my $cdi_id;
		my $cdi_name;
		my $cdi_name_j;
		my $cdi_name_e;
		my $cdi_name_k;
		my $cdi_name_l;
		my $cdi_syn_j;
		my $cdi_syn_e;
		my $cdi_def_j;
		my $cdi_def_e;
		my $cdi_taid;
		my $bul_id_cnt;
		my $bul_id_max;

		my $column_number = 0;
		$sth->bind_col(++$column_number, \$cdi_id,   undef);
		$sth->bind_col(++$column_number, \$cdi_name,   undef);
		$sth->bind_col(++$column_number, \$cdi_name_j,   undef);
		$sth->bind_col(++$column_number, \$cdi_name_e,   undef);
		$sth->bind_col(++$column_number, \$cdi_name_k,   undef);
		$sth->bind_col(++$column_number, \$cdi_name_l,   undef);
		$sth->bind_col(++$column_number, \$cdi_syn_j,   undef);
		$sth->bind_col(++$column_number, \$cdi_syn_e,   undef);
		$sth->bind_col(++$column_number, \$cdi_def_j,   undef);
		$sth->bind_col(++$column_number, \$cdi_def_e,   undef);
		$sth->bind_col(++$column_number, \$cdi_taid,   undef);
		$sth->bind_col(++$column_number, \$bul_id_cnt,   undef);
		$sth->bind_col(++$column_number, \$bul_id_max,   undef);

		while($sth->fetch){

			next unless(defined $cdi_name);

			$cdi_syn_e =~ s/(;)/$1<br>/g if(defined $cdi_syn_e);

			my $bul_type;
			if($bul_id_cnt==2){
				$bul_type = 'both';
			}elsif($bul_id_max==3){
				$bul_type = 'is_a';
			}elsif($bul_id_max==4){
				$bul_type = 'part_of';
			}

			my $HASH = {
				ci_id      => $ci_id,
				cb_id      => $cb_id,
				cdi_name   => $cdi_name,
				cdi_name_j => $cdi_name_j,
				cdi_name_e => $cdi_name_e,
				cdi_name_k => $cdi_name_k,
				cdi_name_l => $cdi_name_l,
				cdi_syn_j  => $cdi_syn_j,
				cdi_syn_e  => $cdi_syn_e,
				cdi_def_j  => $cdi_def_j,
				cdi_def_e  => $cdi_def_e,
				cdi_taid   => $cdi_taid,
				tree       => $bul_type,	#あえてtree

			};

			push(@{$DATAS->{'datas'}},$HASH);
		}
		$sth->finish;
		undef $sth;

		$DATAS->{'success'} = JSON::XS::true;
	};
	if($@){
		print $LOG __LINE__,":",$@,"\n";
	}
}
#print &JSON::XS::encode_json($DATAS);
&gzip_json($DATAS);

close($LOG);
