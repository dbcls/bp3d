#!/opt/services/ag/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use Time::Piece;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
use BITS::Config;
require "webgl_common.pl";
use cgi_lib::common;
use BITS::ConceptArtMapModified;

use constant {
	DEBUG => BITS::Config::DEBUG
};

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);
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

my $LOG;
if(DEBUG){
	open($LOG,">> $logfile");
	select($LOG);
	$| = 1;
	select(STDOUT);

	flock($LOG,2);
	print $LOG "\n[$logtime]:$0\n";
	&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);
}
#&setDefParams(\%FORM,\%COOKIE);

#&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);

#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $DATAS = {
	"datas" => [],
	"total" => 0,
	"success" => JSON::XS::false
};
#$FORM{BITS::Config::LOCATION_HASH_CBID_KEY} = 11;

unless(
	exists $FORM{BITS::Config::LOCATION_HASH_CIID_KEY} && defined $FORM{BITS::Config::LOCATION_HASH_CIID_KEY} && $FORM{BITS::Config::LOCATION_HASH_CIID_KEY} =~ /^[0-9]+$/ &&
	exists $FORM{BITS::Config::LOCATION_HASH_CBID_KEY} && defined $FORM{BITS::Config::LOCATION_HASH_CBID_KEY} && $FORM{BITS::Config::LOCATION_HASH_CBID_KEY} =~ /^[0-9]+$/
){
	$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8(qq|JSON形式が違います|);
	&gzip_json($DATAS);
	exit;
}

$FORM{'cmd'} = 'read' unless(exists $FORM{'cmd'} && defined $FORM{'cmd'} && length $FORM{'cmd'});

my $ci_id = $FORM{BITS::Config::LOCATION_HASH_CIID_KEY} - 0;
my $cb_id = $FORM{BITS::Config::LOCATION_HASH_CBID_KEY} - 0;

my $anyMatch = 1;
my $caseSensitive = 0;

if(lc $FORM{'cmd'} eq 'read'){

	$anyMatch = (exists $FORM{BITS::Config::SEARCH_ANY_MATCH_NAME} && defined $FORM{BITS::Config::SEARCH_ANY_MATCH_NAME}) ? 1 : 0;
	$caseSensitive = (exists $FORM{BITS::Config::SEARCH_CASE_SENSITIVE_NAME} && defined $FORM{BITS::Config::SEARCH_CASE_SENSITIVE_NAME}) ? 1 : 0;

	eval{
	#	my $operator = &get_ludia_operator();
		my $query;
		my @QUERY;
		my $space = &cgi_lib::common::decodeUTF8(qq|　|);
		if(exists $FORM{BITS::Config::LOCATION_HASH_SEARCH_KEY} && defined $FORM{BITS::Config::LOCATION_HASH_SEARCH_KEY}){
			$query = $FORM{BITS::Config::LOCATION_HASH_SEARCH_KEY};
			$query = &cgi_lib::common::decodeUTF8($query);
			$query =~ s/$space/ /g;
			$query =~ s/\s{2,}/ /g;
			$query =~ s/^\s+//g;
			$query =~ s/\s+$//g;

			if(defined $query && length $query){
				@QUERY = split(/\s+/,$query);
			}else{
				undef $query;
				$DATAS->{'success'} = JSON::XS::true;
				&gzip_json($DATAS);
				exit;
			}
		}
		my @SORT;
		if(exists $FORM{'sort'} && defined $FORM{'sort'}){
			my $sort = &cgi_lib::common::decodeJSON($FORM{'sort'});
			push(@SORT,map {
				$_->{'direction'} = 'ASC' unless(exists $_->{'direction'} && defined $_->{'direction'});
				if($_->{'property'} eq BITS::Config::LOCATION_HASH_NAME_KEY){
					$_->{'property'} = 'cd_name'
				}elsif($_->{'property'} eq BITS::Config::LOCATION_HASH_ID_KEY){
					$_->{'property'} = 'cdi_name'
				}
				$_;
			} grep {exists $_->{'property'} && defined $_->{'property'}} @$sort) if(defined $sort && ref $sort eq 'ARRAY');
		}
		if(scalar @SORT == 0){
			push(@SORT,{
				property  => 'cd_name',
				direction => 'ASC'
			});
		}

		my @QUERY_COLUMNS = qw/cdi_name cd_name cd_syn/;
		my $sql_cdi_name = 'cdi_name';
		my $sql_cdi_name_e = 'cd_name';
		my $sql_cdi_syn_e = 'cd_syn';
=pod
	if(defined $query){
		my $sql_max_length='select max(g) from (select GREATEST(length(cdi_name_e),length(cdi_syn_e)) as g from concept_data_info) as a';
		my $sth_max_length = $dbh->prepare($sql_max_length);
		$sth_max_length->execute() or die $dbh->errstr;
		my $column_number = 0;
		my $max_length;
		$sth_max_length->bind_col(++$column_number, \$max_length,   undef);
		$sth_max_length->fetch;
		$sth_max_length->finish;
		undef $sth_max_length;

		$sql_cdi_name   = qq|COALESCE(pgs2snippet1(1, $max_length, 1, '<b>', '</b>', -1, '$query', cdi_name), cdi_name)|;
		$sql_cdi_name_e = qq|COALESCE(pgs2snippet1(1, $max_length, 1, '<b>', '</b>', -1, '$query', cdi_name_e), cdi_name_e)|;
		$sql_cdi_syn_e  = qq|COALESCE(pgs2snippet1(1, $max_length, 1, '<b>', '</b>', -1, '$query', cdi_syn_e), cdi_syn_e)|;
	}
=cut
		$sql_cdi_name   .= ' as snippet_cdi_name';
		$sql_cdi_name_e .= ' as snippet_cdi_name_e';
		$sql_cdi_syn_e  .= ' as snippet_cdi_syn_e';

		my $sql=<<SQL;
select
 cdi_name  as cdi_name,
 cd_name   as cdi_name_e,
 cd_syn    as cdi_syn_e,
 cd_def    as cdi_def_e,
 cd.cdi_id,

 cdi_name  as snippet_cdi_name,
 cd_name   as snippet_cdi_name_e,
 cd_syn    as snippet_cdi_syn_e
from
 concept_data as cd

left join (
 select
  ci_id,
  cdi_id,
  cdi_name,
  is_user_data
 from
  concept_data_info
) as cdi on
   cdi.ci_id=cd.ci_id and
   cdi.cdi_id=cd.cdi_id

where
-- cdi.is_user_data=false AND
 cd_delcause is null AND
 cd.ci_id=$ci_id AND
 cd.cb_id=$cb_id
SQL
		if(defined $query){
#		$sql.=<<SQL;
#  AND (ARRAY[cdi_name,cdi_name_j,cdi_name_e,cdi_name_k,cdi_name_l,art_id] $operator ?)
#SQL

#		$sql.=<<SQL;
#  AND (ARRAY[cdi_name,cdi_name_e,cdi_syn_e] $operator ?)
#SQL

			my @W;
#		my @Q = split(/\s+/,$query);
			foreach my $c (@QUERY_COLUMNS){
				my @C;
				foreach my $q (@QUERY){
					if($anyMatch){
						if($caseSensitive){
							push(@C,qq|$c ~ '$q'|);
						}else{
							push(@C,qq|$c ~* '$q'|);
						}
					}else{
						if($caseSensitive){
							push(@C,qq|$c ~ E'\\\\y$q\\\\y'|);
						}else{
							push(@C,qq|$c ~* E'\\\\y$q\\\\y'|);
						}
					}
				}
				push(@W, '('.join(" and ",@C).')');
			}
			$sql.= ' AND (' . join(" or ",@W) . ')';

		}
		elsif(exists $FORM{BITS::Config::LOCATION_HASH_NAME_KEY} && defined $FORM{BITS::Config::LOCATION_HASH_NAME_KEY} && length $FORM{BITS::Config::LOCATION_HASH_NAME_KEY}){
			$FORM{BITS::Config::LOCATION_HASH_NAME_KEY} =~ s/$space/ /g;
#		$FORM{BITS::Config::LOCATION_HASH_NAME_KEY} =~ s/\s{2,}/ /g;
			$sql.=<<SQL;
  AND  lower(cd_name)=lower(?)
SQL
		}
		elsif(exists $FORM{BITS::Config::LOCATION_HASH_ID_KEY} && defined $FORM{BITS::Config::LOCATION_HASH_ID_KEY} && length $FORM{BITS::Config::LOCATION_HASH_ID_KEY}){
			if($FORM{BITS::Config::LOCATION_HASH_ID_KEY} =~ /^([0-9]+)$/){
				$FORM{BITS::Config::LOCATION_HASH_ID_KEY} = "FMA$1";
			}elsif($FORM{BITS::Config::LOCATION_HASH_ID_KEY} =~ /^(FMA)[^0-9]*?([0-9]+)$/i){
				$FORM{BITS::Config::LOCATION_HASH_ID_KEY} = "$1$2";
			}
			$FORM{BITS::Config::LOCATION_HASH_ID_KEY} =~ s/$space//g;
			$FORM{BITS::Config::LOCATION_HASH_ID_KEY} =~ s/\s+//g;
			$FORM{BITS::Config::LOCATION_HASH_ID_KEY} = uc($FORM{BITS::Config::LOCATION_HASH_ID_KEY});
			$sql.=<<SQL;
  AND cdi_name=?
SQL
		}

		print $LOG __LINE__.":\$sql=[$sql]\n" if(defined $LOG);

		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		if(defined $query){
			my @bind_values;
#		push(@bind_values,qq|*D+ $query|);

#		my @Q = split(/\s+/,$query);
#		foreach my $c (@QUERY_COLUMNS){
#			foreach my $q (@QUERY){
#				push(@bind_values,$q);
#			}
#		}

			print $LOG __LINE__.":\@bind_values=[".&cgi_lib::common::encodeUTF8(join(",",@bind_values))."]\n" if(defined $LOG);

			if(scalar @bind_values){
				$sth->execute(@bind_values) or die $dbh->errstr;
			}else{
				$sth->execute() or die $dbh->errstr;
			}

		}elsif(exists $FORM{BITS::Config::LOCATION_HASH_NAME_KEY} && defined $FORM{BITS::Config::LOCATION_HASH_NAME_KEY}){
			$sth->execute($FORM{BITS::Config::LOCATION_HASH_NAME_KEY}) or die $dbh->errstr;
		}elsif(exists $FORM{BITS::Config::LOCATION_HASH_ID_KEY} && defined $FORM{BITS::Config::LOCATION_HASH_ID_KEY}){
			$sth->execute($FORM{BITS::Config::LOCATION_HASH_ID_KEY}) or die $dbh->errstr;
		}else{
			$sth->execute() or die $dbh->errstr;
		}
		print $LOG __LINE__.":\$sth->rows()=[".$sth->rows()."]\n" if(defined $LOG);
		$DATAS->{'total'} = $sth->rows();
		$sth->finish;
		print $LOG __LINE__.":\$DATAS->{'total'}=[",$DATAS->{'total'},"]\n" if(defined $LOG);

		if($DATAS->{'total'} == 0 && exists $FORM{BITS::Config::LOCATION_HASH_NAME_KEY} && defined $FORM{BITS::Config::LOCATION_HASH_NAME_KEY} && length $FORM{BITS::Config::LOCATION_HASH_NAME_KEY}){
			my $cdi_name_e = $FORM{BITS::Config::LOCATION_HASH_NAME_KEY};
			$FORM{BITS::Config::LOCATION_HASH_NAME_KEY} =~ s/\s{2,}/ /g;
			unless($cdi_name_e eq $FORM{BITS::Config::LOCATION_HASH_NAME_KEY} && length $FORM{BITS::Config::LOCATION_HASH_NAME_KEY}){
				$sth->execute($FORM{BITS::Config::LOCATION_HASH_NAME_KEY}) or die $dbh->errstr;
				print $LOG __LINE__.":\$sth->rows()=[".$sth->rows()."]\n" if(defined $LOG);
				$DATAS->{'total'} = $sth->rows();
				$sth->finish;
				print $LOG __LINE__.":\$DATAS->{'total'}=[",$DATAS->{'total'},"]\n" if(defined $LOG);
			}
		}
		undef $sth;

		if($DATAS->{'total'}>0){
			if(scalar @SORT > 0){
				my @orderby;
				foreach (@SORT){
					push(@orderby,qq|$_->{property} $_->{direction}|);
				}
				$sql .= qq| order by | . join(",",@orderby) if(scalar @orderby > 0);
			}
			$sql .= qq| limit $FORM{limit}| if(defined $FORM{limit});
			$sql .= qq| offset $FORM{start}| if(defined $FORM{start});

			print $LOG __LINE__.":\$sql=[$sql]\n" if(defined $LOG);

			$sth = $dbh->prepare($sql) or die $dbh->errstr;
			if(defined $query){
				my @bind_values;

				print $LOG __LINE__.":\@bind_values=[".&cgi_lib::common::encodeUTF8(join(",",@bind_values))."]\n" if(defined $LOG);

				if(scalar @bind_values){
					$sth->execute(@bind_values) or die $dbh->errstr;
				}else{
					$sth->execute() or die $dbh->errstr;
				}

			}elsif(exists $FORM{BITS::Config::LOCATION_HASH_NAME_KEY} && defined $FORM{BITS::Config::LOCATION_HASH_NAME_KEY}){
				$sth->execute($FORM{BITS::Config::LOCATION_HASH_NAME_KEY}) or die $dbh->errstr;
			}elsif(exists $FORM{BITS::Config::LOCATION_HASH_ID_KEY} && defined $FORM{BITS::Config::LOCATION_HASH_ID_KEY}){
				$sth->execute($FORM{BITS::Config::LOCATION_HASH_ID_KEY}) or die $dbh->errstr;
			}else{
				$sth->execute() or die $dbh->errstr;
			}
			if($sth->rows()>0){
				my $cdi_name;
				my $cdi_name_e;
				my $cdi_name_l;
				my $cdi_syn_e;
				my $cdi_def_e;
				my $cdi_id;

				my $snippet_cdi_name;
				my $snippet_cdi_name_e;
				my $snippet_cdi_syn_e;

				my $column_number = 0;
				$sth->bind_col(++$column_number, \$cdi_name,   undef);
				$sth->bind_col(++$column_number, \$cdi_name_e,   undef);
				$sth->bind_col(++$column_number, \$cdi_syn_e,   undef);
				$sth->bind_col(++$column_number, \$cdi_def_e,   undef);
				$sth->bind_col(++$column_number, \$cdi_id,   undef);

				$sth->bind_col(++$column_number, \$snippet_cdi_name,   undef);
				$sth->bind_col(++$column_number, \$snippet_cdi_name_e,   undef);
				$sth->bind_col(++$column_number, \$snippet_cdi_syn_e,   undef);


				my $sth_bul = $dbh->prepare(qq|select bul_id,bul_name_e from buildup_logic where bul_delcause is null and bul_use|) or die $dbh->errstr;
				$sth_bul->execute() or die $dbh->errstr;
				my $bul_id;
				my $bul_name_e;
				my %BUL;
				$column_number = 0;
				$sth_bul->bind_col(++$column_number, \$bul_id,   undef);
				$sth_bul->bind_col(++$column_number, \$bul_name_e,   undef);
				while($sth_bul->fetch){
					next unless(defined $bul_id && defined $bul_name_e);
					$BUL{$bul_id} = lc($bul_name_e);
				}
				$sth_bul->finish;
				undef $sth_bul;

				my $sql_ct_up;
				my $sql_ct_down;
				if(&existsTable('fma_partof_type')){
					$sql_ct_up = sprintf(qq|select cdi_pid,bul_id,f_potids from concept_tree where ci_id=$ci_id and cb_id=$cb_id and cdi_id=? and cdi_pid is not null and bul_id in (%s)|,join(',',sort keys(%BUL)));
					$sql_ct_down = sprintf(qq|select cdi_id,bul_id,f_potids from concept_tree where ci_id=$ci_id and cb_id=$cb_id and cdi_pid=? and cdi_id is not null and bul_id in (%s)|,join(',',sort keys(%BUL)));
				}else{
					$sql_ct_up = sprintf(qq|select cdi_pid,crl_id,crt_ids from concept_tree where ci_id=$ci_id and cb_id=$cb_id and cdi_id=? and cdi_pid is not null and crl_id in (%s)|,join(',',sort keys(%BUL)));
					$sql_ct_down = sprintf(qq|select cdi_id,crl_id,crt_ids from concept_tree where ci_id=$ci_id and cb_id=$cb_id and cdi_pid=? and cdi_id is not null and crl_id in (%s)|,join(',',sort keys(%BUL)));
				}

				my $sth_ct_up = $dbh->prepare($sql_ct_up) or die $dbh->errstr;
				my $sth_ct_down = $dbh->prepare($sql_ct_down) or die $dbh->errstr;


				my $sql_cdi=<<SQL;
select
 cd.cdi_id,
 cdi_name,
 cd_name
from 
 concept_data as cd

left join (
 select ci_id,cdi_id,cdi_name,is_user_data from concept_data_info
) as cdi on cdi.ci_id=cd.ci_id and cdi.cdi_id=cd.cdi_id

where
-- cdi.is_user_data=false AND
 cd_delcause is null AND
 cd.ci_id=$ci_id AND
 cd.cb_id=$cb_id AND
 cd.cdi_id in (%s)
SQL

				my $sql_cbr;
				if(&existsTable('fma_partof_type')){
					$sql_cbr = qq|select cbr.f_potid,f_potname from concept_build_relation as cbr left join (select f_potid,f_potname from fma_partof_type) as fpt on fpt.f_potid=cbr.f_potid where ci_id=$ci_id and cb_id=$cb_id and cbr_use|;
				}else{
					$sql_cbr = qq|select cbr.crt_id,crt_name from concept_build_relation as cbr left join (select crt_id,crt_name from concept_relation_type) as fpt on fpt.crt_id=cbr.crt_id where ci_id=$ci_id and cb_id=$cb_id and cbr_use|;
				}
				my $sth_cbr = $dbh->prepare($sql_cbr) or die $dbh->errstr;
				$sth_cbr->execute() or die $dbh->errstr;
				my $f_potid;
				my $f_potname;
				my %CBR;
				$column_number = 0;
				$sth_cbr->bind_col(++$column_number, \$f_potid,   undef);
				$sth_cbr->bind_col(++$column_number, \$f_potname,   undef);
				while($sth_cbr->fetch){
					next unless(defined $f_potid && defined $f_potname);
					$CBR{$f_potid} = $f_potname;
				}
				$sth_cbr->finish;
				undef $sth_cbr;

				while($sth->fetch){
					if(defined $cdi_syn_e){
						if($cdi_syn_e =~ /;/){
							$cdi_syn_e = [split(/;/,$cdi_syn_e)];
						}else{
							$cdi_syn_e = [$cdi_syn_e];
						}
					}

					if(defined $query){
						$snippet_cdi_name = &snippet($snippet_cdi_name, \@QUERY);
						$snippet_cdi_name_e = &snippet($snippet_cdi_name_e, \@QUERY);
						$snippet_cdi_syn_e = &snippet($snippet_cdi_syn_e, \@QUERY);

						if(defined $snippet_cdi_syn_e){
							if($snippet_cdi_syn_e =~ /;/){
								$snippet_cdi_syn_e = '<div><div style=""><label class="'.BITS::Config::SYNONYM_DATA_FIELD_ID.'">'.join('</label></div><div style="margin-top:4px;"><label class="'.BITS::Config::SYNONYM_DATA_FIELD_ID.'">',split(/;/,$snippet_cdi_syn_e)).'</label></div></div>';
							}else{
								$snippet_cdi_syn_e = '<div><div style=""><label class="'.BITS::Config::SYNONYM_DATA_FIELD_ID.'">'.$snippet_cdi_syn_e.'</label></div></div>';
							}
						}
					}else{
						$snippet_cdi_name = undef;
						$snippet_cdi_name_e = undef;
						$snippet_cdi_syn_e = undef;
					}

					my $HASH = {};
					$HASH->{BITS::Config::CONCEPT_INFO_DATA_FIELD_ID}    = $ci_id-0;
					$HASH->{BITS::Config::CONCEPT_BUILD_DATA_FIELD_ID}   = $cb_id-0;
					$HASH->{BITS::Config::ID_DATA_FIELD_ID}              = $cdi_name;
					$HASH->{BITS::Config::NAME_DATA_FIELD_ID}            = $cdi_name_e;
					$HASH->{BITS::Config::SYNONYM_DATA_FIELD_ID}         = $cdi_syn_e;
					$HASH->{BITS::Config::DEFINITION_DATA_FIELD_ID}      = $cdi_def_e;
					$HASH->{BITS::Config::SNIPPET_ID_DATA_FIELD_ID}      = $snippet_cdi_name;
					$HASH->{BITS::Config::SNIPPET_NAME_DATA_FIELD_ID}    = $snippet_cdi_name_e;
					$HASH->{BITS::Config::SNIPPET_SYNONYM_DATA_FIELD_ID} = $snippet_cdi_syn_e;

					unless(defined $query){


						my %USE_KEYS;
						my %CDI_IDS;

						my $ct_cdi_id;
						my $bul_id;
						my $f_potids;
						$sth_ct_up->execute($cdi_id) or die $dbh->errstr;
						$column_number = 0;
						$sth_ct_up->bind_col(++$column_number, \$ct_cdi_id,   undef);
						$sth_ct_up->bind_col(++$column_number, \$bul_id,   undef);
						$sth_ct_up->bind_col(++$column_number, \$f_potids,   undef);
						while($sth_ct_up->fetch){
							next unless(defined $ct_cdi_id && defined $bul_id);
							next unless(exists $BUL{$bul_id} && defined $BUL{$bul_id});
							if(defined $f_potids && length $f_potids){
								foreach my $f_potid (split(/;/,$f_potids)){
									next unless(exists $CBR{$f_potid} && defined $CBR{$f_potid});
									my $rel_key = $CBR{$f_potid} . '_up';
									$USE_KEYS{$rel_key} = undef;
									$HASH->{$rel_key} = $HASH->{$rel_key} // [];
									push(@{$HASH->{$rel_key}},{cdi_id=>$ct_cdi_id});
									$CDI_IDS{$ct_cdi_id} = undef;
								}
							}else{
								my $rel_key = $BUL{$bul_id} . '_up';
								$USE_KEYS{$rel_key} = undef;
								$HASH->{$rel_key} = $HASH->{$rel_key} // [];
								push(@{$HASH->{$rel_key}},{cdi_id=>$ct_cdi_id});
								$CDI_IDS{$ct_cdi_id} = undef;
							}
						}
						$sth_ct_up->finish;


						$sth_ct_down->execute($cdi_id) or die $dbh->errstr;
						$column_number = 0;
						$sth_ct_down->bind_col(++$column_number, \$ct_cdi_id,   undef);
						$sth_ct_down->bind_col(++$column_number, \$bul_id,   undef);
						$sth_ct_down->bind_col(++$column_number, \$f_potids,   undef);
						while($sth_ct_down->fetch){
							next unless(defined $ct_cdi_id && defined $bul_id);
							next unless(exists $BUL{$bul_id} && defined $BUL{$bul_id});
							if(defined $f_potids && length $f_potids){
								foreach my $f_potid (split(/;/,$f_potids)){
									next unless(exists $CBR{$f_potid} && defined $CBR{$f_potid});
									my $rel_key = $CBR{$f_potid} . '_down';
									$USE_KEYS{$rel_key} = undef;
									$HASH->{$rel_key} = $HASH->{$rel_key} // [];
									push(@{$HASH->{$rel_key}},{cdi_id=>$ct_cdi_id});
									$CDI_IDS{$ct_cdi_id} = undef;
								}
							}else{
								my $rel_key = $BUL{$bul_id} . '_down';
								$USE_KEYS{$rel_key} = undef;
								$HASH->{$rel_key} = $HASH->{$rel_key} // [];
								push(@{$HASH->{$rel_key}},{cdi_id=>$ct_cdi_id});
								$CDI_IDS{$ct_cdi_id} = undef;
							}
						}
						$sth_ct_down->finish;

						my %CDI_NAMES;
						my %CDI_NAMES_E;
						if(scalar keys(%CDI_IDS)){
							my $sth_cdi = $dbh->prepare(sprintf($sql_cdi,join(',',keys(%CDI_IDS)))) or die $dbh->errstr;
							$sth_cdi->execute() or die $dbh->errstr;
							$column_number = 0;
							my $cdi_id;
							my $cdi_name;
							my $cdi_name_e;
							$sth_cdi->bind_col(++$column_number, \$cdi_id,   undef);
							$sth_cdi->bind_col(++$column_number, \$cdi_name,   undef);
							$sth_cdi->bind_col(++$column_number, \$cdi_name_e,   undef);
							while($sth_cdi->fetch){
								next unless(defined $cdi_id && defined $cdi_name && defined $cdi_name_e);
								$CDI_NAMES{$cdi_id} = $cdi_name;
								$CDI_NAMES_E{$cdi_id} = $cdi_name_e;
							}
							$sth_cdi->finish;
							undef $sth_cdi;
						}

						my %CDI_MAPS;
						my %CDI_CTIS;
						if(scalar keys(%CDI_IDS)){
							my $sql_cam = qq|select cdi_id,art_id from concept_art_map where ci_id=$ci_id and cm_use and cm_delcause is null group by cdi_id,art_id|;
							my $sth_cam = $dbh->prepare($sql_cam) or die $dbh->errstr;
							$sth_cam->execute() or die $dbh->errstr;
							$column_number = 0;
							my $cdi_id;
							my $art_id;
							$sth_cam->bind_col(++$column_number, \$cdi_id,   undef);
							$sth_cam->bind_col(++$column_number, \$art_id,   undef);
							while($sth_cam->fetch){
								next unless(defined $cdi_id && defined $art_id);
								push(@{$CDI_MAPS{$cdi_id}}, $art_id);
								$CDI_CTIS{$cdi_id} = undef;
							}
							$sth_cam->finish;
							undef $sth_cam;
						}
						if(scalar keys(%CDI_MAPS)){
							my $sql_cti = sprintf(qq|SELECT cti_pids FROM concept_tree_info WHERE ci_id=$ci_id AND cb_id=$cb_id AND cti_pnum>0 AND cti_pids IS NOT NULL AND crl_id=0 AND cdi_id IN (%s)|,join(',',map {'?'} keys(%CDI_MAPS)));
							my $sth_cti = $dbh->prepare($sql_cti) or die $dbh->errstr;
							$sth_cti->execute(keys(%CDI_MAPS)) or die $dbh->errstr;
							$column_number = 0;
							my $cti_pids;
							$sth_cti->bind_col(++$column_number, \$cti_pids,   undef);
							while($sth_cti->fetch){
								next unless(defined $cti_pids);
								$cti_pids = &cgi_lib::common::decodeJSON($cti_pids);
								if(defined $cti_pids && ref $cti_pids eq 'ARRAY' && scalar @{$cti_pids}){
									map { $CDI_CTIS{$_} = undef; } @{$cti_pids};
								}
							}
							$sth_cti->finish;
							undef $sth_cti;
						}
					
	#				$HASH->{BITS::Config::IS_SHAPE_FIELD_ID} = exists $CDI_MAPS{$cdi_id} ? JSON::XS::true : JSON::XS::false;
						$HASH->{BITS::Config::IS_SHAPE_FIELD_ID} = exists $CDI_CTIS{$cdi_id} ? JSON::XS::true : JSON::XS::false;
						$HASH->{BITS::Config::IS_MAPED_FIELD_ID} = exists $CDI_MAPS{$cdi_id} ? JSON::XS::true : JSON::XS::false;
						$HASH->{BITS::Config::IS_CURRENT_FIELD_ID} = exists $CDI_MAPS{$cdi_id} ? JSON::XS::true : JSON::XS::false;

					my $md_id;
						my $mv_id;
						$md_id=1 unless(defined $md_id && $md_id =~ /^[1-9][0-9]*$/);
						unless(defined $mv_id && $mv_id =~ /^[1-9][0-9]*$/){
							$mv_id = undef;
#							$ci_id = undef;
#							$cb_id = undef;
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
#							if(defined $mv_id){
#								$sth_mv = $dbh->prepare("select ci_id,cb_id from model_version where md_id=? and mv_id=?") or die $dbh->errstr;
#								$sth_mv->execute($md_id,$mv_id) or die $dbh->errstr;
#								$sth_mv->bind_col(1, \$ci_id, undef);
#								$sth_mv->bind_col(2, \$cb_id, undef);
#								$sth_mv->fetch;
#								$sth_mv->finish;
#								undef $sth_mv;
#							}
						}

						if(exists $CDI_MAPS{$cdi_id}){
	#					&cgi_lib::common::message($CDI_NAMES{$cdi_id}, $LOG) if(defined $LOG);
							$HASH->{BITS::Config::IS_CURRENT_FIELD_ID} = &checkCurrent(
								dbh     => $dbh,
								md_id   => $md_id,
								mv_id   => $mv_id,
								ci_id   => $ci_id,
								cb_id   => $cb_id,
								cdi_id  => $cdi_id,
								art_ids => $CDI_MAPS{$cdi_id},
		#						LOG => $LOG
							);
		#					&cgi_lib::common::message($HASH->{BITS::Config::IS_CURRENT_FIELD_ID}, $LOG) if(defined $LOG);
						}



						@SORT = ();
						if(exists $FORM{'sort'} && defined $FORM{'sort'}){
							my $sort = &cgi_lib::common::decodeJSON($FORM{'sort'});
							push(@SORT,map {
								$_->{'direction'} = 'ASC' unless(exists $_->{'direction'} && defined $_->{'direction'});
								$_;
							} grep {exists $_->{'property'} && defined $_->{'property'}} @$sort) if(defined $sort && ref $sort eq 'ARRAY');
						}
						if(scalar @SORT == 0){
							push(@SORT,{
								property  => BITS::Config::LOCATION_HASH_NAME_KEY,
								direction => 'ASC'
							});
						}

#&cgi_lib::common::message($cb_id, $LOG) if(defined $LOG);

						foreach my $use_key (keys(%USE_KEYS)){
							next unless(exists $HASH->{$use_key} && defined $HASH->{$use_key} && ref $HASH->{$use_key} eq 'ARRAY');
							foreach my $hash (@{$HASH->{$use_key}}){
								my $cdi_id = $hash->{'cdi_id'};
								delete $hash->{'cdi_id'};
								$hash->{BITS::Config::ID_DATA_FIELD_ID} = $CDI_NAMES{$cdi_id} if(exists $CDI_NAMES{$cdi_id} && defined $CDI_NAMES{$cdi_id} && length $CDI_NAMES{$cdi_id});
								$hash->{BITS::Config::NAME_DATA_FIELD_ID} = $CDI_NAMES_E{$cdi_id} if(exists $CDI_NAMES_E{$cdi_id} && defined $CDI_NAMES_E{$cdi_id} && length $CDI_NAMES_E{$cdi_id});


								$hash->{BITS::Config::IS_SHAPE_FIELD_ID} = exists $CDI_CTIS{$cdi_id} ? JSON::XS::true : JSON::XS::false;
								$hash->{BITS::Config::IS_MAPED_FIELD_ID} = exists $CDI_MAPS{$cdi_id} ? JSON::XS::true : JSON::XS::false;
								$hash->{BITS::Config::IS_CURRENT_FIELD_ID} = exists $CDI_MAPS{$cdi_id} ? JSON::XS::true : JSON::XS::false;

								if(exists $CDI_MAPS{$cdi_id}){
									$hash->{BITS::Config::IS_CURRENT_FIELD_ID} = &checkCurrent(
										dbh     => $dbh,
										md_id   => $md_id,
										mv_id   => $mv_id,
										ci_id   => $ci_id,
										cb_id   => $cb_id,
										cdi_id  => $cdi_id,
										art_ids => $CDI_MAPS{$cdi_id},
		#								LOG => $LOG
									);
								}

							}
		#					$HASH->{$use_key} = [sort {$a->{'cdi_name_e'} cmp $b->{'cdi_name_e'}} @{$HASH->{$use_key}}];
							if(scalar @SORT > 0){
								foreach (@SORT){
									if(uc($_->{'direction'}) eq 'ASC'){
										$HASH->{$use_key} = [sort {
											if(exists $_->{'property'} && defined $_->{'property'}){
												$a->{$_->{'property'}} cmp $b->{$_->{'property'}}
											}else{
												0;
											}
										} @{$HASH->{$use_key}}];
									}else{
										$HASH->{$use_key} = [sort {
											if(exists $_->{'property'} && defined $_->{'property'}){
												$b->{$_->{'property'}} cmp $a->{$_->{'property'}}
											}else{
												0;
											}
										} @{$HASH->{$use_key}}];
									}
								}
							}
						}

#&cgi_lib::common::message($cb_id, $LOG) if(defined $LOG);

						my $CDS;
						my $sth_tables = $dbh->prepare(qq|SELECT tablename FROM pg_tables WHERE tablename=? OR  tablename=?|) or die $dbh->errstr;
						$sth_tables->execute('concept_synonym','concept_data_synonym') or die $dbh->errstr;
						my $rows_tables = $sth_tables->rows();
						$sth_tables->finish;
						undef $sth_tables;
						if($rows_tables==2){
							my $sql_synonym=qq|
SELECT
  cds.cds_id
 ,cds.cds_bid
 ,cds.cs_id
 ,cs.cs_name
 ,cds.cds_added
 ,cds.cds_order
FROM
  concept_data_synonym AS cds
LEFT JOIN concept_synonym AS cs ON cs.cs_id=cds.cs_id
LEFT JOIN concept_data_synonym_type AS cdst ON cdst.cdst_id=cds.cdst_id
WHERE
      cds.ci_id=?
  AND cds.cb_id=?
  AND cds.cdi_id=?
  AND cdst.cdst_name='synonym'
ORDER BY
  cs.cs_name
|;
							my $sth_synonym = $dbh->prepare($sql_synonym) or die $dbh->errstr;
#							&cgi_lib::common::message($ci_id, $LOG) if(defined $LOG);
#							&cgi_lib::common::message($cb_id, $LOG) if(defined $LOG);
#							&cgi_lib::common::message($cdi_id, $LOG) if(defined $LOG);
							$sth_synonym->execute($ci_id,$cb_id,$cdi_id) or die $dbh->errstr;
							my $cs_id;
							my $cds_id;
							my $cds_bid;
							my $cds_added;
							my $cs_name;
							my $cds_order;
							$column_number = 0;
							$sth_synonym->bind_col(++$column_number, \$cds_id,    undef);
							$sth_synonym->bind_col(++$column_number, \$cds_bid,   undef);
							$sth_synonym->bind_col(++$column_number, \$cs_id,     undef);
							$sth_synonym->bind_col(++$column_number, \$cs_name,   undef);
							$sth_synonym->bind_col(++$column_number, \$cds_added, undef);
							$sth_synonym->bind_col(++$column_number, \$cds_order, undef);
							while($sth_synonym->fetch){
								my $hash;
								$hash->{BITS::Config::CDS_ID_DATA_FIELD_ID} = $cds_id;
								$hash->{BITS::Config::CDS_BID_DATA_FIELD_ID} = $cds_bid;
								$hash->{BITS::Config::CS_ID_DATA_FIELD_ID} = $cs_id;
								$hash->{BITS::Config::CS_NAME_DATA_FIELD_ID} = $cs_name;
								$hash->{BITS::Config::CDS_ADDED_DATA_FIELD_ID} = $cds_added eq '1' ? JSON::XS::true : JSON::XS::false;
								$hash->{BITS::Config::CDS_ORDER_DATA_FIELD_ID} = $cds_order - 0;
								$hash->{BITS::Config::CDS_ADDED_AUTO_DATA_FIELD_ID} = defined $cds_bid ? JSON::XS::true : JSON::XS::false;
								push(@{$CDS}, $hash);
							}
							$sth_synonym->finish;
							undef $sth_synonym;
						}
						$HASH->{BITS::Config::CDS_DATA_FIELD_ID} = $CDS;
					}
					push(@{$DATAS->{'datas'}},$HASH);
				}
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
}
elsif(lc $FORM{'cmd'} eq 'update_synonym'){
	&cgi_lib::common::message(\%FORM, $LOG) if(defined $LOG);
	&cgi_lib::common::message(&cgi_lib::common::decodeJSON($FORM{BITS::Config::SYNONYM_DATA_FIELD_ID}), $LOG) if(defined $LOG);
	if(
				exists	$FORM{BITS::Config::ID_DATA_FIELD_ID}
		&&	defined	$FORM{BITS::Config::ID_DATA_FIELD_ID}
		&&	length	$FORM{BITS::Config::ID_DATA_FIELD_ID}
		&&	exists	$FORM{BITS::Config::SYNONYM_DATA_FIELD_ID}
		&&	defined	$FORM{BITS::Config::SYNONYM_DATA_FIELD_ID}
		&&	length	$FORM{BITS::Config::SYNONYM_DATA_FIELD_ID}
#		&& 0
	){
		my $cdi_name = $FORM{BITS::Config::ID_DATA_FIELD_ID};
		my $synonym_arr = &cgi_lib::common::decodeJSON($FORM{BITS::Config::SYNONYM_DATA_FIELD_ID});
		if(defined $synonym_arr && ref $synonym_arr eq 'ARRAY'){

			$dbh->{'AutoCommit'} = 0;
			$dbh->{'RaiseError'} = 1;
			eval{

				my $column_number;
				my $cdi_id;
				my $cdi_id_arr;
				my $cdi_id_hash;
				my $cdi_id_added_hash;

#concept_data_info
				my $sth_cdi_sel = $dbh->prepare(qq|select cdi_id from concept_data_info where ci_id=? AND cdi_name=?|) or die $dbh->errstr;
				$sth_cdi_sel->execute($ci_id,$cdi_name) or die $dbh->errstr;
				$column_number = 0;
				$sth_cdi_sel->bind_col(++$column_number, \$cdi_id, undef);
				$sth_cdi_sel->fetch;
				$sth_cdi_sel->finish;
				undef $sth_cdi_sel;

				$cdi_id_hash->{$cdi_id} = undef if(defined $cdi_id);

#concept_synonym
				my $CS_ID2NAME;
				my $CS_NAME2ID;
				if(defined $cdi_id){
					my $cs_id;
					my $cs_name;
					my $sth_cs_sel = $dbh->prepare(qq|select cs_id,cs_name from concept_synonym|) or die $dbh->errstr;
					$sth_cs_sel->execute() or die $dbh->errstr;
					$column_number = 0;
					$sth_cs_sel->bind_col(++$column_number, \$cs_id, undef);
					$sth_cs_sel->bind_col(++$column_number, \$cs_name, undef);
					while($sth_cs_sel->fetch){
						$CS_ID2NAME->{$cs_id}->{$cs_name} = undef;
						$CS_NAME2ID->{$cs_name}->{$cs_id} = undef;
					}
					$sth_cs_sel->finish;
					undef $sth_cs_sel;
				}

#concept_data_synonym_type
				my $CDST_ID2NAME;
				my $CDST_NAME2ID;
				if(defined $cdi_id){
					my $cdst_id;
					my $cdst_name;
					my $sth_cdst_sel = $dbh->prepare(qq|SELECT cdst_id,cdst_name from concept_data_synonym_type|) or die $dbh->errstr;
					$sth_cdst_sel->execute() or die $dbh->errstr;
					$column_number = 0;
					$sth_cdst_sel->bind_col(++$column_number, \$cdst_id, undef);
					$sth_cdst_sel->bind_col(++$column_number, \$cdst_name, undef);
					while($sth_cdst_sel->fetch){
						$CDST_ID2NAME->{$cdst_id} = $cdst_name;
						$CDST_NAME2ID->{$cdst_name} = $cdst_id;
					}
					$sth_cdst_sel->finish;
					undef $sth_cdst_sel;
				}

#concept_data
				my $CD_ID2NAME;
				my $CD_ID2NAMESYN;
				my $CD_NAMESYN2ID;
				if(defined $cdi_id){
					my $cdi_id;
					my $cd_name;
					my $cd_syn;
					my $sth_cd_sel = $dbh->prepare(qq|select cdi_id,cd_name,cd_syn from concept_data where ci_id=? AND cb_id=?|) or die $dbh->errstr;
					$sth_cd_sel->execute($ci_id,$cb_id) or die $dbh->errstr;
					$column_number = 0;
					$sth_cd_sel->bind_col(++$column_number, \$cdi_id, undef);
					$sth_cd_sel->bind_col(++$column_number, \$cd_name, undef);
					$sth_cd_sel->bind_col(++$column_number, \$cd_syn, undef);
					while($sth_cd_sel->fetch){
						$cd_name =~ s/\s+/ /g;
						$cd_name =~ s/^\s+//g;
						$cd_name =~ s/\s+$//g;
						$CD_ID2NAME->{$cdi_id}= lc $cd_name;
						$CD_ID2NAMESYN->{$cdi_id}->{lc $cd_name} = undef;
						$CD_NAMESYN2ID->{lc $cd_name}->{$cdi_id} = undef;
						next unless(defined $cd_syn && length $cd_syn);
						map {
							s/\s+/ /g;
							s/^\s+//g;
							s/\s+$//g;
							$CD_ID2NAMESYN->{$cdi_id}->{lc $_} = undef;
							$CD_NAMESYN2ID->{lc $_}->{$cdi_id} = undef;
						} split(/;/,$cd_syn)
					}
					$sth_cd_sel->finish;
					undef $sth_cd_sel;
				}

#concept_tree_trio
				my $CTT;
				my $CTT_P;
				my $CTT_L;
				my $CTT_R;
				if(defined $cdi_id){
					my $cdi_pid;
					my $cdi_lid;
					my $cdi_rid;
					my $sth_ctt_sel = $dbh->prepare(qq|select cdi_pid,cdi_lid,cdi_rid from concept_tree_trio where ci_id=? AND cb_id=?|) or die $dbh->errstr;
					$sth_ctt_sel->execute($ci_id,$cb_id) or die $dbh->errstr;
					$column_number = 0;
					$sth_ctt_sel->bind_col(++$column_number, \$cdi_pid, undef);
					$sth_ctt_sel->bind_col(++$column_number, \$cdi_lid, undef);
					$sth_ctt_sel->bind_col(++$column_number, \$cdi_rid, undef);
					while($sth_ctt_sel->fetch){
						$CTT_P->{$cdi_pid} = $CTT->{$cdi_pid} = {
							cdi_lid => $cdi_lid,
							cdi_rid => $cdi_rid
						};
						$CTT_L->{$cdi_lid} = $CTT->{$cdi_lid} = {
							cdi_pid => $cdi_pid,
							cdi_rid => $cdi_rid
						};
						$CTT_R->{$cdi_rid} = $CTT->{$cdi_rid} = {
							cdi_lid => $cdi_lid,
							cdi_pid => $cdi_pid
						};
					}
					$sth_ctt_sel->finish;
					undef $sth_ctt_sel;
				}

#concept_relation_logic
				my $CRL_HASH;
				my $crt_id;

				if(defined $cdi_id){
					my $crl_id;
					my $crl_name;
					my $sth_crl_sel = $dbh->prepare(qq|select crl_id,crl_name from concept_relation_logic|) or die $dbh->errstr;
					$sth_crl_sel->execute() or die $dbh->errstr;
					$column_number = 0;
					$sth_crl_sel->bind_col(++$column_number, \$crl_id, undef);
					$sth_crl_sel->bind_col(++$column_number, \$crl_name, undef);
					while($sth_crl_sel->fetch){
						$CRL_HASH->{$crl_name} = $crl_id;
					}
					$sth_crl_sel->finish;
					undef $sth_crl_sel;
				}

#concept_relation_type
				if(defined $cdi_id){
					my $sth_crt_sel = $dbh->prepare(qq|select crt_id from concept_relation_type where crt_name=?|) or die $dbh->errstr;
					$sth_crt_sel->execute('lexicalsuper') or die $dbh->errstr;
					$column_number = 0;
					$sth_crt_sel->bind_col(++$column_number, \$crt_id, undef);
					$sth_crt_sel->fetch;
					$sth_crt_sel->finish;
					undef $sth_crt_sel;
				}

#concept_tree
				my $CT_ID_CRT_PID_HASH;
				my $CT_ID_PID_CRT_HASH;
				my $CT_PID_CRT_ID_HASH;
				my $CT_PID_ID_CRT_HASH;
				my $CT_ID_PID_ISA_HASH;
				my $CT_PID_ID_ISA_HASH;
				if(
							defined	$cdi_id
					&&	defined	$CRL_HASH
					&&	ref			$CRL_HASH eq 'HASH'
					&&	exists	$CRL_HASH->{'is_a'}
					&&	defined	$CRL_HASH->{'is_a'}
					&&	exists	$CRL_HASH->{'part_of'}
					&&	defined	$CRL_HASH->{'part_of'}
					&&	defined	$crt_id
				){

					my $sth_ct_sel = $dbh->prepare(qq|select cdi_id,cdi_pid,crl_id,crt_ids from concept_tree where ci_id=? AND cb_id=?|) or die $dbh->errstr;
					$sth_ct_sel->execute($ci_id,$cb_id) or die $dbh->errstr;
					$column_number = 0;
					my $cdi_id;
					my $cdi_pid;
					my $crl_id;
					my $crt_ids;
					$sth_ct_sel->bind_col(++$column_number, \$cdi_id, undef);
					$sth_ct_sel->bind_col(++$column_number, \$cdi_pid, undef);
					$sth_ct_sel->bind_col(++$column_number, \$crl_id, undef);
					$sth_ct_sel->bind_col(++$column_number, \$crt_ids, undef);
					while($sth_ct_sel->fetch){
						if($crl_id eq $CRL_HASH->{'is_a'}){
							$CT_ID_PID_ISA_HASH->{$cdi_id}->{$cdi_pid} = undef;
							$CT_PID_ID_ISA_HASH->{$cdi_pid}->{$cdi_id} = undef;
						}
						elsif($crl_id eq $CRL_HASH->{'part_of'}){
							next unless(defined $crt_ids && length $crt_ids);
							map {
								$CT_ID_CRT_PID_HASH->{$cdi_id}->{$_}->{$cdi_pid} = undef;
								$CT_ID_PID_CRT_HASH->{$cdi_id}->{$cdi_pid}->{$_} = undef;

								$CT_PID_CRT_ID_HASH->{$cdi_pid}->{$_}->{$cdi_id} = undef;
								$CT_PID_ID_CRT_HASH->{$cdi_pid}->{$cdi_id}->{$_} = undef;

							} split(/;/,$crt_ids);
						}
					}
					$sth_ct_sel->finish;
					undef $sth_ct_sel;
				}

#concept_synonym
#				my $CS_ID2NAME;
#				my $CS_NAME2ID;
				if(defined $cdi_id){

					my $cs_id;
					my $cs_name;
					my $sth_cs_sel = $dbh->prepare(qq|select cs_id,cs_name from concept_synonym|) or die $dbh->errstr;
					$sth_cs_sel->execute() or die $dbh->errstr;
					$column_number = 0;
					$sth_cs_sel->bind_col(++$column_number, \$cs_id, undef);
					$sth_cs_sel->bind_col(++$column_number, \$cs_name, undef);
					while($sth_cs_sel->fetch){
						$CS_ID2NAME->{$cs_id} = $cs_name;
						$CS_NAME2ID->{$cs_name} = $cs_id;
					}
					$sth_cs_sel->finish;
					undef $sth_cs_sel;

					my $sth_cs_ins = $dbh->prepare(qq|INSERT INTO concept_synonym (cs_name) VALUES (?) RETURNING cs_id|) or die $dbh->errstr;
					foreach my $synonym (@{$synonym_arr}){
						next unless(
									defined	$synonym
							&&	ref			$synonym eq 'HASH'
							&&	exists	$synonym->{BITS::Config::SYNONYM_DATA_FIELD_ID}
							&&	defined	$synonym->{BITS::Config::SYNONYM_DATA_FIELD_ID}
							&&	length	$synonym->{BITS::Config::SYNONYM_DATA_FIELD_ID}
						);
						my $cs_name = $synonym->{BITS::Config::SYNONYM_DATA_FIELD_ID};
						unless(exists $CS_NAME2ID->{$cs_name}){
							my $cs_id;
							$sth_cs_ins->execute($cs_name) or die $dbh->errstr;
							$column_number=0;
							$sth_cs_ins->bind_col(++$column_number, \$cs_id, undef);
							$sth_cs_ins->fetch;
							$sth_cs_ins->finish;

							$CS_ID2NAME->{$cs_id} = $cs_name;
							$CS_NAME2ID->{$cs_name} = $cs_id;
						}
					}
#					undef $sth_cs_ins;


					my $sth_cds_sel = $dbh->prepare(qq|SELECT cds_id FROM concept_data_synonym WHERE ci_id=? AND cb_id=? AND cdi_id=? AND cs_id=?|) or die $dbh->errstr;
					my $sth_cds_ins = $dbh->prepare(qq|INSERT INTO concept_data_synonym (ci_id,cb_id,cdi_id,cs_id,cds_added,cdst_id) VALUES (?,?,?,?,true,?) RETURNING cds_id|) or die $dbh->errstr;
					my $sth_cds_ins_b = $dbh->prepare(qq|INSERT INTO concept_data_synonym (ci_id,cb_id,cdi_id,cs_id,cds_bid,cds_added,cdst_id) VALUES (?,?,?,?,?,true,?)|) or die $dbh->errstr;
					my $sth_cds_del = $dbh->prepare(qq|DELETE FROM concept_data_synonym WHERE ci_id=? AND cb_id=? AND cdi_id=? AND cs_id=?|) or die $dbh->errstr;
					my $sth_cds_del_b = $dbh->prepare(qq|DELETE FROM concept_data_synonym WHERE ci_id=? AND cb_id=? AND cds_bid=? RETURNING cdi_id|) or die $dbh->errstr;

#					&cgi_lib::common::message($synonym_arr, $LOG) if(defined $LOG);
					foreach my $synonym (@{$synonym_arr}){
						next unless(
									defined	$synonym
							&&	ref			$synonym eq 'HASH'
							&&	exists	$synonym->{BITS::Config::SYNONYM_DATA_FIELD_ID}
							&&	defined	$synonym->{BITS::Config::SYNONYM_DATA_FIELD_ID}
							&&	length	$synonym->{BITS::Config::SYNONYM_DATA_FIELD_ID}
						);
						my $cs_name = $synonym->{BITS::Config::SYNONYM_DATA_FIELD_ID};
						my $cs_id = $CS_NAME2ID->{$cs_name};
						if($synonym->{BITS::Config::CDS_DELETED_DATA_FIELD_ID}){
#							&cgi_lib::common::message($synonym, $LOG) if(defined $LOG);
#							&cgi_lib::common::message($ci_id, $LOG) if(defined $LOG);
#							&cgi_lib::common::message($cb_id, $LOG) if(defined $LOG);
#							&cgi_lib::common::message($cdi_id, $LOG) if(defined $LOG);
#							&cgi_lib::common::message($cs_id, $LOG) if(defined $LOG);

							my $cds_id;
							$sth_cds_sel->execute($ci_id,$cb_id,$cdi_id,$cs_id) or die $dbh->errstr;
							$column_number=0;
							$sth_cds_sel->bind_col(++$column_number, \$cds_id, undef);
							$sth_cds_sel->fetch;
							$sth_cds_sel->finish;

							&cgi_lib::common::message($cds_id, $LOG) if(defined $LOG);

							my $temp_cdi_id;
							$sth_cds_del_b->execute($ci_id,$cb_id,$cds_id) or die $dbh->errstr;
							$column_number=0;
							$sth_cds_del_b->bind_col(++$column_number, \$temp_cdi_id, undef);
							while($sth_cds_del_b->fetch){
								$cdi_id_hash->{$temp_cdi_id} = undef;
							}
							$sth_cds_del_b->finish;

#							&cgi_lib::common::message($synonym, $LOG) if(defined $LOG);

							$sth_cds_del->execute($ci_id,$cb_id,$cdi_id,$cs_id) or die $dbh->errstr;
							$sth_cds_del->finish;

#							&cgi_lib::common::message($synonym, $LOG) if(defined $LOG);
						}
						elsif($synonym->{BITS::Config::CDS_EDITED_DATA_FIELD_ID}){

							my $cds_id;
							$sth_cds_sel->execute($ci_id,$cb_id,$cdi_id,$cs_id) or die $dbh->errstr;
							$column_number=0;
							$sth_cds_sel->bind_col(++$column_number, \$cds_id, undef);
							$sth_cds_sel->fetch;
							$sth_cds_sel->finish;

							next if(defined $cds_id);

							$sth_cds_ins->execute($ci_id,$cb_id,$cdi_id,$cs_id,$CDST_NAME2ID->{'synonym'}) or die $dbh->errstr;
							$column_number=0;
							$sth_cds_ins->bind_col(++$column_number, \$cds_id, undef);
							$sth_cds_ins->fetch;
							$sth_cds_ins->finish;

							$cdi_id_added_hash->{$cdi_id} = {
								cds_id => $cds_id,
								cs_name => $cs_name
							};

							next unless(
										exists	$CTT->{$cdi_id}
								&&	defined	$CTT->{$cdi_id}
								&&	ref			$CTT->{$cdi_id} eq 'HASH'
							);

							my $cs_pname = &getParentFromName($cs_name);
							next unless(
										defined	$cs_pname
								&&	length	$cs_pname
								&&	exists	$CD_NAMESYN2ID->{lc $cs_pname}
								&&	defined	$CD_NAMESYN2ID->{lc $cs_pname}
								&&	ref			$CD_NAMESYN2ID->{lc $cs_pname} eq 'HASH'
							);

							my $is_added = 0;
							foreach my $cdi_pid (keys(%{$CD_NAMESYN2ID->{lc $cs_pname}})){
								next unless(
											exists	$CTT->{$cdi_pid}
									&&	defined	$CTT->{$cdi_pid}
									&&	ref			$CTT->{$cdi_pid} eq 'HASH'
								);
=pod
								my $cs_lname = ucfirst(lc(sprintf("%s of %s",$CD_ID2NAME->{$CTT->{$cdi_id}->{'cdi_lid'}},$CD_ID2NAME->{$CTT->{$cdi_pid}->{'cdi_lid'}})));
								my $cs_rname = ucfirst(lc(sprintf("%s of %s",$CD_ID2NAME->{$CTT->{$cdi_id}->{'cdi_rid'}},$CD_ID2NAME->{$CTT->{$cdi_pid}->{'cdi_rid'}})));

								my $cs_lid;
								my $cs_rid;
								unless(exists $CS_NAME2ID->{$cs_lname}){
									$sth_cs_ins->execute($cs_lname) or die $dbh->errstr;
									$column_number=0;
									$sth_cs_ins->bind_col(++$column_number, \$cs_lid, undef);
									$sth_cs_ins->fetch;
									$sth_cs_ins->finish;

									$CS_ID2NAME->{$cs_lid} = $cs_lname;
									$CS_NAME2ID->{$cs_lname} = $cs_lid;
								}
								else{
									$cs_lid = $CS_NAME2ID->{$cs_lname};
								}
								unless(exists $CS_NAME2ID->{$cs_rname}){
									$sth_cs_ins->execute($cs_rname) or die $dbh->errstr;
									$column_number=0;
									$sth_cs_ins->bind_col(++$column_number, \$cs_rid, undef);
									$sth_cs_ins->fetch;
									$sth_cs_ins->finish;

									$CS_ID2NAME->{$cs_rid} = $cs_rname;
									$CS_NAME2ID->{$cs_rname} = $cs_rid;
								}
								else{
									$cs_rid = $CS_NAME2ID->{$cs_rname};
								}

								my $cdi_lid = $CTT->{$cdi_id}->{'cdi_lid'};
								my $cdi_rid = $CTT->{$cdi_id}->{'cdi_rid'};

								my $cds_lid;
								my $cds_rid;
								$sth_cds_sel->execute($ci_id,$cb_id,$cdi_lid,$cs_lid) or die $dbh->errstr;
								$column_number=0;
								$sth_cds_sel->bind_col(++$column_number, \$cds_lid, undef);
								$sth_cds_sel->fetch;
								$sth_cds_sel->finish;

								$sth_cds_sel->execute($ci_id,$cb_id,$cdi_rid,$cs_rid) or die $dbh->errstr;
								$column_number=0;
								$sth_cds_sel->bind_col(++$column_number, \$cds_rid, undef);
								$sth_cds_sel->fetch;
								$sth_cds_sel->finish;

								unless(defined $cds_lid){
									$sth_cds_ins_b->execute($ci_id,$cb_id,$cdi_lid,$cs_lid,$cds_id,$CDST_NAME2ID->{'synonym'}) or die $dbh->errstr;
									$sth_cds_ins_b->finish;
								}
								unless(defined $cds_rid){
									$sth_cds_ins_b->execute($ci_id,$cb_id,$cdi_rid,$cs_rid,$cds_id,$CDST_NAME2ID->{'synonym'}) or die $dbh->errstr;
									$sth_cds_ins_b->finish;
								}
								$cdi_id_hash->{$cdi_lid} = undef;
								$cdi_id_hash->{$cdi_rid} = undef;

								$cdi_id_added_hash->{$cdi_lid} = {
									cds_id => $cds_id,
									cs_name => $cs_lname
								};
								$cdi_id_added_hash->{$cdi_rid} = {
									cds_id => $cds_id,
									cs_name => $cs_rname
								};
=cut
								foreach my $ctt_key (keys(%{$CTT->{$cdi_pid}})){
									my $cs_lname = ucfirst(lc(sprintf("%s of %s",$CD_ID2NAME->{$CTT->{$cdi_id}->{$ctt_key}},$CD_ID2NAME->{$CTT->{$cdi_pid}->{$ctt_key}})));
									my $cs_lid;
									unless(exists $CS_NAME2ID->{$cs_lname}){
										$sth_cs_ins->execute($cs_lname) or die $dbh->errstr;
										$column_number=0;
										$sth_cs_ins->bind_col(++$column_number, \$cs_lid, undef);
										$sth_cs_ins->fetch;
										$sth_cs_ins->finish;

										$CS_ID2NAME->{$cs_lid} = $cs_lname;
										$CS_NAME2ID->{$cs_lname} = $cs_lid;
									}
									else{
										$cs_lid = $CS_NAME2ID->{$cs_lname};
									}
									my $cdi_lid = $CTT->{$cdi_id}->{$ctt_key};
									my $cds_lid;
									$sth_cds_sel->execute($ci_id,$cb_id,$cdi_lid,$cs_lid) or die $dbh->errstr;
									$column_number=0;
									$sth_cds_sel->bind_col(++$column_number, \$cds_lid, undef);
									$sth_cds_sel->fetch;
									$sth_cds_sel->finish;
									unless(defined $cds_lid){
										$sth_cds_ins_b->execute($ci_id,$cb_id,$cdi_lid,$cs_lid,$cds_id,$CDST_NAME2ID->{'synonym'}) or die $dbh->errstr;
										$sth_cds_ins_b->finish;
									}
									$cdi_id_hash->{$cdi_lid} = undef;
									$cdi_id_added_hash->{$cdi_lid} = {
										cds_id => $cds_id,
										cs_name => $cs_lname
									};
								}
								$is_added = 1;
								last;
							}
							unless($is_added){
								foreach my $ctt_key (keys(%{$CTT->{$cdi_id}})){
									my $cs_lname = ucfirst(lc(sprintf("%s of %s",$CD_ID2NAME->{$CTT->{$cdi_id}->{$ctt_key}},$cs_pname)));
									my $cs_lid;
									unless(exists $CS_NAME2ID->{$cs_lname}){
										$sth_cs_ins->execute($cs_lname) or die $dbh->errstr;
										$column_number=0;
										$sth_cs_ins->bind_col(++$column_number, \$cs_lid, undef);
										$sth_cs_ins->fetch;
										$sth_cs_ins->finish;

										$CS_ID2NAME->{$cs_lid} = $cs_lname;
										$CS_NAME2ID->{$cs_lname} = $cs_lid;
									}
									else{
										$cs_lid = $CS_NAME2ID->{$cs_lname};
									}
									my $cdi_lid = $CTT->{$cdi_id}->{$ctt_key};
									my $cds_lid;
									$sth_cds_sel->execute($ci_id,$cb_id,$cdi_lid,$cs_lid) or die $dbh->errstr;
									$column_number=0;
									$sth_cds_sel->bind_col(++$column_number, \$cds_lid, undef);
									$sth_cds_sel->fetch;
									$sth_cds_sel->finish;
									unless(defined $cds_lid){
										$sth_cds_ins_b->execute($ci_id,$cb_id,$cdi_lid,$cs_lid,$cds_id,$CDST_NAME2ID->{'synonym'}) or die $dbh->errstr;
										$sth_cds_ins_b->finish;
									}
									$cdi_id_hash->{$cdi_lid} = undef;
									$cdi_id_added_hash->{$cdi_lid} = {
										cds_id => $cds_id,
										cs_name => $cs_lname
									};
								}
							}
						}
					}

					undef $sth_cs_ins;
					undef $sth_cds_sel;
					undef $sth_cds_ins;
					undef $sth_cds_ins_b;
					undef $sth_cds_del;
					undef $sth_cds_del_b;
				}

				if(defined $cdi_id_hash && ref $cdi_id_hash eq 'HASH'){
					&cgi_lib::common::message($cdi_id_hash, $LOG) if(defined $LOG);
					my $sth_cds_sel_synonym = $dbh->prepare(qq|
SELECT
  ARRAY_TO_STRING(ARRAY_AGG(a.cs_name), ';') AS cs_name
FROM (
  SELECT
   cs.cs_name
  FROM
    concept_data_synonym AS cds
  LEFT JOIN concept_synonym AS cs ON cs.cs_id=cds.cs_id
  LEFT JOIN concept_data_synonym_type AS cdst ON cdst.cdst_id=cds.cdst_id
  WHERE
       cds.ci_id=?
   AND cds.cb_id=?
   AND cds.cdi_id=?
   AND cdst.cdst_name='synonym'
  ORDER BY
    cs.cs_name
) AS a
|) or die $dbh->errstr;
					my $sth_cd_upd_synonym = $dbh->prepare(qq|UPDATE concept_data SET cd_syn=? WHERE ci_id=? AND cb_id=? AND cdi_id=?|) or die $dbh->errstr;
					my $cs_name;
					foreach my $temp_cdi_id(keys(%{$cdi_id_hash})){
						$sth_cds_sel_synonym->execute($ci_id,$cb_id,$temp_cdi_id) or die $dbh->errstr;
						$column_number=0;
						$sth_cds_sel_synonym->bind_col(++$column_number, \$cs_name, undef);
						$sth_cds_sel_synonym->fetch;
						$sth_cds_sel_synonym->finish;

						$sth_cd_upd_synonym->execute($cs_name,$ci_id,$cb_id,$temp_cdi_id) or die $dbh->errstr;
						$sth_cd_upd_synonym->finish;
						&cgi_lib::common::message($cs_name, $LOG) if(defined $LOG);
					}

					undef $sth_cds_sel_synonym;
					undef $sth_cd_upd_synonym;
				}

				if(
							defined	$cdi_id
					&&	defined	$CRL_HASH
					&&	ref			$CRL_HASH eq 'HASH'
					&&	exists	$CRL_HASH->{'part_of'}
					&&	defined	$CRL_HASH->{'part_of'}
					&&	defined	$crt_id
				){

					$cdi_id_arr = [keys(%{$cdi_id_hash})];
					my $temp_cdi_id_hash = {};
					map { $temp_cdi_id_hash->{$_} = undef } keys(%{$cdi_id_hash});
					if(defined $CT_PID_CRT_ID_HASH && ref $CT_PID_CRT_ID_HASH eq 'HASH'){
						foreach my $temp_cdi_id(@{$cdi_id_arr}){
							if(
										exists	$CT_PID_CRT_ID_HASH->{$temp_cdi_id}
								&&	defined	$CT_PID_CRT_ID_HASH->{$temp_cdi_id}
								&&	ref			$CT_PID_CRT_ID_HASH->{$temp_cdi_id} eq 'HASH'
								&&	exists	$CT_PID_CRT_ID_HASH->{$temp_cdi_id}->{$crt_id}
								&&	defined	$CT_PID_CRT_ID_HASH->{$temp_cdi_id}->{$crt_id}
								&&	ref			$CT_PID_CRT_ID_HASH->{$temp_cdi_id}->{$crt_id} eq 'HASH'
							){
								map { $temp_cdi_id_hash->{$_} = undef } keys(%{$CT_PID_CRT_ID_HASH->{$temp_cdi_id}->{$crt_id}});
							}
						}
					}
					$cdi_id_arr = [keys(%{$temp_cdi_id_hash})];
					undef $temp_cdi_id_hash;


					my $CTI_HASH;
					my $cti_cids;
					my $cti_pids;
					my $cti_depth;
					{
						my $sth_cti_sel = $dbh->prepare(qq|SELECT cdi_id,cti_cids,cti_depth,cti_pids,crl_id FROM concept_tree_info WHERE ci_id=? AND cb_id=?|) or die $dbh->errstr;
						$sth_cti_sel->execute($ci_id,$cb_id) or die $dbh->errstr;
						$column_number = 0;
						my $cdi_id;
						my $crl_id;
						$sth_cti_sel->bind_col(++$column_number, \$cdi_id, undef);
						$sth_cti_sel->bind_col(++$column_number, \$cti_cids, undef);
						$sth_cti_sel->bind_col(++$column_number, \$cti_depth, undef);
						$sth_cti_sel->bind_col(++$column_number, \$cti_pids, undef);
						$sth_cti_sel->bind_col(++$column_number, \$crl_id, undef);
						while($sth_cti_sel->fetch){
							$CTI_HASH->{$cdi_id}->{$crl_id} = {
								cti_cids => undef,
								cti_pids => undef,
								cti_depth => $cti_depth - 0
							};

							if(defined $cti_cids && length $cti_cids){
								my $cti_cids_arr = &cgi_lib::common::decodeJSON($cti_cids);
								map { $CTI_HASH->{$cdi_id}->{$crl_id}->{'cti_cids'}->{$_} = undef } @{$cti_cids_arr} if(defined $cti_cids_arr && ref $cti_cids_arr eq 'ARRAY' && scalar @{$cti_cids_arr});
							}
							if(defined $cti_pids && length $cti_pids){
								my $cti_pids_arr = &cgi_lib::common::decodeJSON($cti_pids);
								map { $CTI_HASH->{$cdi_id}->{$crl_id}->{'cti_pids'}->{$_} = undef } @{$cti_pids_arr} if(defined $cti_pids_arr && ref $cti_pids_arr eq 'ARRAY' && scalar @{$cti_pids_arr});
							}

						}
						$sth_cti_sel->finish;
						undef $sth_cti_sel;
					}

##ここから

					my $sth_ct_ins = $dbh->prepare(qq|INSERT INTO concept_tree (ci_id,cb_id,cdi_id,cdi_pid,crl_id,crt_ids) VALUES (?,?,?,?,?,?)|) or die $dbh->errstr;
					my $sth_ct_upd = $dbh->prepare(qq|UPDATE concept_tree SET crt_ids=? WHERE ci_id=? AND cb_id=? AND crl_id=? AND cdi_id=? AND cdi_pid=?|) or die $dbh->errstr;
					my $sth_ct_del = $dbh->prepare(qq|DELETE FROM concept_tree where ci_id=? AND cb_id=? AND crl_id=? AND cdi_id=? AND cdi_pid=?|) or die $dbh->errstr;

					my $sth_cti_upd = $dbh->prepare(qq|UPDATE concept_tree_info SET cti_cnum=?,cti_cids=?,cti_depth=?,cti_pnum=?,cti_pids=? WHERE ci_id=? AND cb_id=? AND cdi_id=? AND crl_id=?|) or die $dbh->errstr;

					my $UPD_ID_HASH;
					my $crl_id = $CRL_HASH->{'part_of'};

					foreach my $cdi_id (@{$cdi_id_arr}){


						if(
									defined	$CT_ID_CRT_PID_HASH
							&&	ref			$CT_ID_CRT_PID_HASH eq 'HASH'
							&&	exists	$CT_ID_CRT_PID_HASH->{$cdi_id}
							&&	defined	$CT_ID_CRT_PID_HASH->{$cdi_id}
							&&	ref			$CT_ID_CRT_PID_HASH->{$cdi_id} eq 'HASH'
							&&	exists	$CT_ID_CRT_PID_HASH->{$cdi_id}->{$crt_id}
							&&	defined	$CT_ID_CRT_PID_HASH->{$cdi_id}->{$crt_id}
							&&	ref			$CT_ID_CRT_PID_HASH->{$cdi_id}->{$crt_id} eq 'HASH'
						){
							map { delete $CT_ID_PID_CRT_HASH->{$cdi_id}->{$_}->{$crt_id} } keys(%{$CT_ID_CRT_PID_HASH->{$cdi_id}->{$crt_id}});
							my $cti_cids = {};
							$cti_cids->{$cdi_id} = undef;
							if(
										defined	$CTI_HASH
								&&	ref			$CTI_HASH eq 'HASH'
								&&	exists	$CTI_HASH->{$cdi_id}
								&&	defined	$CTI_HASH->{$cdi_id}
								&&	ref			$CTI_HASH->{$cdi_id} eq 'HASH'
								&&	exists	$CTI_HASH->{$cdi_id}->{$crl_id}
								&&	defined	$CTI_HASH->{$cdi_id}->{$crl_id}
								&&	ref			$CTI_HASH->{$cdi_id}->{$crl_id} eq 'HASH'
								&&	exists	$CTI_HASH->{$cdi_id}->{$crl_id}->{'cti_cids'}
								&&	defined	$CTI_HASH->{$cdi_id}->{$crl_id}->{'cti_cids'}
								&&	ref			$CTI_HASH->{$cdi_id}->{$crl_id}->{'cti_cids'} eq 'HASH'
							){
								map { $cti_cids->{$_} = undef; } keys(%{$CTI_HASH->{$cdi_id}->{$crl_id}->{'cti_cids'}});
							}

							foreach my $cdi_pid (keys(%{$CT_ID_PID_CRT_HASH->{$cdi_id}})){
								if(defined $CT_ID_PID_CRT_HASH->{$cdi_id}->{$cdi_pid} && ref $CT_ID_PID_CRT_HASH->{$cdi_id}->{$cdi_pid} eq 'HASH' && scalar keys(%{$CT_ID_PID_CRT_HASH->{$cdi_id}->{$cdi_pid}})>=1){
									my $crt_ids = join(';',sort {$a <=> $b} keys(%{$CT_ID_PID_CRT_HASH->{$cdi_id}->{$cdi_pid}}));
									$sth_ct_upd->execute($crt_ids,$ci_id,$cb_id,$crl_id,$cdi_id,$cdi_pid) or die $dbh->errstr;
									$sth_ct_upd->finish;
								}
								else{
									$sth_ct_del->execute($ci_id,$cb_id,$crl_id,$cdi_id,$cdi_pid) or die $dbh->errstr;
									$sth_ct_del->finish;

									delete $CT_ID_PID_CRT_HASH->{$cdi_id}->{$cdi_pid};

									my $cti_pids = {};
									$cti_pids->{$cdi_pid} = undef;
									if(
												defined	$CTI_HASH
										&&	ref			$CTI_HASH eq 'HASH'
									){
										if(
													exists	$CTI_HASH->{$cdi_pid}
											&&	defined	$CTI_HASH->{$cdi_pid}
											&&	ref			$CTI_HASH->{$cdi_pid} eq 'HASH'
											&&	exists	$CTI_HASH->{$cdi_pid}->{$crl_id}
											&&	defined	$CTI_HASH->{$cdi_pid}->{$crl_id}
											&&	ref			$CTI_HASH->{$cdi_pid}->{$crl_id} eq 'HASH'
											&&	exists	$CTI_HASH->{$cdi_pid}->{$crl_id}->{'cti_pids'}
											&&	defined	$CTI_HASH->{$cdi_pid}->{$crl_id}->{'cti_pids'}
											&&	ref			$CTI_HASH->{$cdi_pid}->{$crl_id}->{'cti_pids'} eq 'HASH'
										){
											map { $cti_pids->{$_} = undef; } keys(%{$CTI_HASH->{$cdi_pid}->{$crl_id}->{'cti_pids'}});
										}

										foreach my $cti_cid (keys(%{$cti_cids})){
											if(
														exists	$CTI_HASH->{$cti_cid}
												&&	defined	$CTI_HASH->{$cti_cid}
												&&	ref			$CTI_HASH->{$cti_cid} eq 'HASH'
												&&	exists	$CTI_HASH->{$cti_cid}->{$crl_id}
												&&	defined	$CTI_HASH->{$cti_cid}->{$crl_id}
												&&	ref			$CTI_HASH->{$cti_cid}->{$crl_id} eq 'HASH'
												&&	exists	$CTI_HASH->{$cti_cid}->{$crl_id}->{'cti_pids'}
												&&	defined	$CTI_HASH->{$cti_cid}->{$crl_id}->{'cti_pids'}
												&&	ref			$CTI_HASH->{$cti_cid}->{$crl_id}->{'cti_pids'} eq 'HASH'
											){
												my $hash = $CTI_HASH->{$cti_cid}->{$crl_id}->{'cti_pids'};
												map { delete $hash->{$_} if(exists $hash->{$_}); } keys(%{$cti_pids});

												$hash = $CTI_HASH->{$cti_cid}->{$CRL_HASH->{'FMA'}}->{'cti_pids'};
												map {
													delete $hash->{$_} if(exists $hash->{$_}) } keys(%{$cti_pids});

												$UPD_ID_HASH->{$cti_cid} = undef;
											}
										}
										foreach my $cti_pid (keys(%{$cti_pids})){
											if(
														exists	$CTI_HASH->{$cti_pid}
												&&	defined	$CTI_HASH->{$cti_pid}
												&&	ref			$CTI_HASH->{$cti_pid} eq 'HASH'
												&&	exists	$CTI_HASH->{$cti_pid}->{$crl_id}
												&&	defined	$CTI_HASH->{$cti_pid}->{$crl_id}
												&&	ref			$CTI_HASH->{$cti_pid}->{$crl_id} eq 'HASH'
												&&	exists	$CTI_HASH->{$cti_pid}->{$crl_id}->{'cti_cids'}
												&&	defined	$CTI_HASH->{$cti_pid}->{$crl_id}->{'cti_cids'}
												&&	ref			$CTI_HASH->{$cti_pid}->{$crl_id}->{'cti_cids'} eq 'HASH'
											){
												my $hash = $CTI_HASH->{$cti_pid}->{$crl_id}->{'cti_cids'};
												map { delete $hash->{$_} if(exists $hash->{$_}); } keys(%{$cti_pids});

												$hash = $CTI_HASH->{$cti_pid}->{$CRL_HASH->{'FMA'}}->{'cti_cids'};
												map { delete $hash->{$_} if(exists $hash->{$_}); } keys(%{$cti_pids});

												$UPD_ID_HASH->{$cti_pid} = undef;
											}
										}
									}
								}
							}

							delete $CT_ID_CRT_PID_HASH->{$cdi_id}->{$crt_id} if(exists $CT_ID_CRT_PID_HASH->{$cdi_id}->{$crt_id});
						}
					}

					my $sth_cds_sel = $dbh->prepare(qq|
SELECT
 cs.cs_name
FROM
  concept_data_synonym AS cds
LEFT JOIN concept_synonym AS cs ON cs.cs_id=cds.cs_id
WHERE
     cds.ci_id=?
 AND cds.cb_id=?
 AND cds.cdi_id=?
ORDER BY
  cs.cs_name
|) or die $dbh->errstr;
					foreach my $cdi_id (@{$cdi_id_arr}){
						$CD_ID2NAMESYN->{$cdi_id} = {} if(exists $CD_ID2NAMESYN->{$cdi_id});
						my $cs_name;
						$sth_cds_sel->execute($ci_id,$cb_id,$cdi_id) or die $dbh->errstr;
						$column_number=0;
						$sth_cds_sel->bind_col(++$column_number, \$cs_name, undef);
						while($sth_cds_sel->fetch){
							$CD_ID2NAMESYN->{$cdi_id}->{lc $cs_name} = undef
						}
						$sth_cds_sel->finish;
					}
					undef $sth_cds_sel;

					foreach my $cdi_id (@{$cdi_id_arr}){
						my $synonym_arr = [];
						if(exists $CD_ID2NAMESYN->{$cdi_id} && defined $CD_ID2NAMESYN->{$cdi_id} && ref $CD_ID2NAMESYN->{$cdi_id} eq 'HASH'){
							push(@{$synonym_arr}, keys(%{$CD_ID2NAMESYN->{$cdi_id}}));
						}

						foreach my $synonym (@{$synonym_arr}){
							my $p_name = &getParentFromName($synonym);
							next unless(defined $p_name && length $p_name);
							next unless(exists $CD_NAMESYN2ID->{$p_name} && defined $CD_NAMESYN2ID->{$p_name} && ref $CD_NAMESYN2ID->{$p_name} eq 'HASH');
							map { $CT_ID_CRT_PID_HASH->{$cdi_id}->{$crt_id}->{$_} = undef; } keys(%{$CD_NAMESYN2ID->{$p_name}});
						}
						if(
									exists	$CT_ID_CRT_PID_HASH->{$cdi_id}
							&&	defined $CT_ID_CRT_PID_HASH->{$cdi_id}
							&&	ref			$CT_ID_CRT_PID_HASH->{$cdi_id} eq 'HASH'
							&&	exists	$CT_ID_CRT_PID_HASH->{$cdi_id}->{$crt_id}
							&&	defined $CT_ID_CRT_PID_HASH->{$cdi_id}->{$crt_id}
							&&	ref			$CT_ID_CRT_PID_HASH->{$cdi_id}->{$crt_id} eq 'HASH'
						){



							my $cti_cids = {};
							$cti_cids->{$cdi_id} = undef;
							if(
										defined	$CTI_HASH
								&&	ref			$CTI_HASH eq 'HASH'
								&&	exists	$CTI_HASH->{$cdi_id}
								&&	defined	$CTI_HASH->{$cdi_id}
								&&	ref			$CTI_HASH->{$cdi_id} eq 'HASH'
								&&	exists	$CTI_HASH->{$cdi_id}->{$crl_id}
								&&	defined	$CTI_HASH->{$cdi_id}->{$crl_id}
								&&	ref			$CTI_HASH->{$cdi_id}->{$crl_id} eq 'HASH'
								&&	exists	$CTI_HASH->{$cdi_id}->{$crl_id}->{'cti_cids'}
								&&	defined	$CTI_HASH->{$cdi_id}->{$crl_id}->{'cti_cids'}
								&&	ref			$CTI_HASH->{$cdi_id}->{$crl_id}->{'cti_cids'} eq 'HASH'
							){
								map { $cti_cids->{$_} = undef; } keys(%{$CTI_HASH->{$cdi_id}->{$crl_id}->{'cti_cids'}});
							}


							foreach my $cdi_pid (keys(%{$CT_ID_CRT_PID_HASH->{$cdi_id}->{$crt_id}})){
								if(exists $CT_ID_PID_CRT_HASH->{$cdi_id}->{$cdi_pid}){
									$CT_ID_PID_CRT_HASH->{$cdi_id}->{$cdi_pid}->{$crt_id} = undef;
									my $crt_ids = join(';',sort {$a <=> $b} keys(%{$CT_ID_PID_CRT_HASH->{$cdi_id}->{$cdi_pid}}));
									$sth_ct_upd->execute($crt_ids,$ci_id,$cb_id,$crl_id,$cdi_id,$cdi_pid) or die $dbh->errstr;
									$sth_ct_upd->finish;
								}
								else{
									$CT_ID_PID_CRT_HASH->{$cdi_id}->{$cdi_pid}->{$crt_id} = undef;
									my $crt_ids = join(';',sort {$a <=> $b} keys(%{$CT_ID_PID_CRT_HASH->{$cdi_id}->{$cdi_pid}}));

									$sth_ct_ins->execute($ci_id,$cb_id,$cdi_id,$cdi_pid,$crl_id,$crt_ids) or die $dbh->errstr;
									$sth_ct_ins->finish;
								}
								$UPD_ID_HASH->{$cdi_pid} = undef;



								my $cti_pids = {};
								$cti_pids->{$cdi_pid} = undef;
								if(
											defined	$CTI_HASH
									&&	ref			$CTI_HASH eq 'HASH'
								){
									if(
												exists	$CTI_HASH->{$cdi_pid}
										&&	defined	$CTI_HASH->{$cdi_pid}
										&&	ref			$CTI_HASH->{$cdi_pid} eq 'HASH'
										&&	exists	$CTI_HASH->{$cdi_pid}->{$crl_id}
										&&	defined	$CTI_HASH->{$cdi_pid}->{$crl_id}
										&&	ref			$CTI_HASH->{$cdi_pid}->{$crl_id} eq 'HASH'
										&&	exists	$CTI_HASH->{$cdi_pid}->{$crl_id}->{'cti_pids'}
										&&	defined	$CTI_HASH->{$cdi_pid}->{$crl_id}->{'cti_pids'}
										&&	ref			$CTI_HASH->{$cdi_pid}->{$crl_id}->{'cti_pids'} eq 'HASH'
									){
										map { $cti_pids->{$_} = undef; } keys(%{$CTI_HASH->{$cdi_pid}->{$crl_id}->{'cti_pids'}});
									}

									foreach my $cti_cid (keys(%{$cti_cids})){
										if(
													exists	$CTI_HASH->{$cti_cid}
											&&	defined	$CTI_HASH->{$cti_cid}
											&&	ref			$CTI_HASH->{$cti_cid} eq 'HASH'
											&&	exists	$CTI_HASH->{$cti_cid}->{$crl_id}
											&&	defined	$CTI_HASH->{$cti_cid}->{$crl_id}
											&&	ref			$CTI_HASH->{$cti_cid}->{$crl_id} eq 'HASH'
											&&	exists	$CTI_HASH->{$cti_cid}->{$crl_id}->{'cti_pids'}
											&&	defined	$CTI_HASH->{$cti_cid}->{$crl_id}->{'cti_pids'}
											&&	ref			$CTI_HASH->{$cti_cid}->{$crl_id}->{'cti_pids'} eq 'HASH'
										){
											my $hash = $CTI_HASH->{$cti_cid}->{$crl_id}->{'cti_pids'};
											map { $hash->{$_} = undef; } keys(%{$cti_pids});

											$hash = $CTI_HASH->{$cti_cid}->{$CRL_HASH->{'FMA'}}->{'cti_pids'};
											map { $hash->{$_} = undef; } keys(%{$cti_pids});

											$UPD_ID_HASH->{$cti_cid} = undef;
										}
									}
									foreach my $cti_pid (keys(%{$cti_pids})){
										if(
													exists	$CTI_HASH->{$cti_pid}
											&&	defined	$CTI_HASH->{$cti_pid}
											&&	ref			$CTI_HASH->{$cti_pid} eq 'HASH'
											&&	exists	$CTI_HASH->{$cti_pid}->{$crl_id}
											&&	defined	$CTI_HASH->{$cti_pid}->{$crl_id}
											&&	ref			$CTI_HASH->{$cti_pid}->{$crl_id} eq 'HASH'
											&&	exists	$CTI_HASH->{$cti_pid}->{$crl_id}->{'cti_cids'}
											&&	defined	$CTI_HASH->{$cti_pid}->{$crl_id}->{'cti_cids'}
											&&	ref			$CTI_HASH->{$cti_pid}->{$crl_id}->{'cti_cids'} eq 'HASH'
										){
											my $hash = $CTI_HASH->{$cti_pid}->{$crl_id}->{'cti_cids'};
											map { $hash->{$_} = undef; } keys(%{$cti_pids});

											$hash = $CTI_HASH->{$cti_pid}->{$CRL_HASH->{'FMA'}}->{'cti_cids'};
											map { $hash->{$_} = undef; } keys(%{$cti_pids});

											$UPD_ID_HASH->{$cti_pid} = undef;
										}
									}
								}
							}
						}
					}

					if(defined $UPD_ID_HASH && ref $UPD_ID_HASH eq 'HASH'){
						my $upd_id_arr;
						foreach my $upd_id (keys(%{$UPD_ID_HASH})){
							next unless(exists $CTI_HASH->{$upd_id} && defined $CTI_HASH->{$upd_id} && ref $CTI_HASH->{$upd_id} eq 'HASH');
							push(@{$upd_id_arr}, $upd_id);
						}
						foreach my $crl_id ($CRL_HASH->{'part_if'}, $CRL_HASH->{'FMA'}){

							$upd_id_arr = [sort {$CTI_HASH->{$a}->{$crl_id}->{'cti_depth'} <=> $CTI_HASH->{$b}->{$crl_id}->{'cti_depth'}} @{$upd_id_arr}];
							foreach my $upd_id (@{$upd_id_arr}){

								my $max_cti_depth = -1;
								my $cti_cnum = 0;
								my $cti_pnum = 0;
								my $temp_cti_cids;
								my $temp_cti_pids;
								if(
											exists	$CTI_HASH->{$upd_id}->{$crl_id}
									&&	defined	$CTI_HASH->{$upd_id}->{$crl_id}
									&&	ref			$CTI_HASH->{$upd_id}->{$crl_id} eq 'HASH'
									&&	exists	$CTI_HASH->{$upd_id}->{$crl_id}->{'cti_cids'}
									&&	defined	$CTI_HASH->{$upd_id}->{$crl_id}->{'cti_cids'}
									&&	ref			$CTI_HASH->{$upd_id}->{$crl_id}->{'cti_cids'} eq 'HASH'
								){
									my $cti_cids_arr = [sort {$a <=> $b} keys(%{$CTI_HASH->{$upd_id}->{$crl_id}->{'cti_cids'}})];
									$cti_cnum = scalar @{$cti_cids_arr};
									$temp_cti_cids = &cgi_lib::common::encodeJSON($cti_cids_arr);
								}
								if(
											exists	$CTI_HASH->{$upd_id}->{$crl_id}
									&&	defined	$CTI_HASH->{$upd_id}->{$crl_id}
									&&	ref			$CTI_HASH->{$upd_id}->{$crl_id} eq 'HASH'
									&&	exists	$CTI_HASH->{$upd_id}->{$crl_id}->{'cti_pids'}
									&&	defined	$CTI_HASH->{$upd_id}->{$crl_id}->{'cti_pids'}
									&&	ref			$CTI_HASH->{$upd_id}->{$crl_id}->{'cti_pids'} eq 'HASH'
								){
									my $cti_pids_arr = [sort {$a <=> $b} keys(%{$CTI_HASH->{$upd_id}->{$crl_id}->{'cti_pids'}})];
									foreach my $cti_pid (@{$cti_pids_arr}){
										next unless(
													exists	$CTI_HASH->{$cti_pid}
											&&	defined	$CTI_HASH->{$cti_pid}
											&&	ref			$CTI_HASH->{$cti_pid} eq 'HASH'
											&&	exists	$CTI_HASH->{$cti_pid}->{$crl_id}
											&&	defined	$CTI_HASH->{$cti_pid}->{$crl_id}
											&&	ref			$CTI_HASH->{$cti_pid}->{$crl_id} eq 'HASH'
											&&	exists	$CTI_HASH->{$cti_pid}->{$crl_id}->{'cti_depth'}
											&&	defined	$CTI_HASH->{$cti_pid}->{$crl_id}->{'cti_depth'}
										);
										$max_cti_depth = $CTI_HASH->{$cti_pid}->{$crl_id}->{'cti_depth'} if($max_cti_depth < $CTI_HASH->{$cti_pid}->{$crl_id}->{'cti_depth'});
									}
									$cti_pnum = scalar @{$cti_pids_arr};
									$temp_cti_pids = &cgi_lib::common::encodeJSON($cti_pids_arr);
								}
								$max_cti_depth++;

								$sth_cti_upd->execute($cti_cnum,$temp_cti_cids,$max_cti_depth,$cti_pnum,$temp_cti_pids,$ci_id,$cb_id,$upd_id,$crl_id) or die $dbh->errstr;
								$sth_cti_upd->finish;
							}

						}
					}


					undef $sth_ct_ins;
					undef $sth_ct_upd;
					undef $sth_ct_del;
					undef $sth_cti_upd;
				}

				&cgi_lib::common::message($cdi_id_added_hash, $LOG) if(defined $LOG);

				if(defined $cdi_id_added_hash && ref $cdi_id_added_hash eq 'HASH'){
					&cgi_lib::common::message($cdi_id_added_hash, $LOG) if(defined $LOG);

					my $sth_ct_sel = $dbh->prepare(qq|select cdi_id from concept_tree where ci_id=? AND cb_id=? AND cdi_pid=? AND crl_id=? AND crt_ids LIKE ?|) or die $dbh->errstr;
					my $sth_cs_ins = $dbh->prepare(qq|INSERT INTO concept_synonym (cs_name) VALUES (?) RETURNING cs_id|) or die $dbh->errstr;
					my $sth_cds_sel = $dbh->prepare(qq|SELECT cds_id FROM concept_data_synonym WHERE ci_id=? AND cb_id=? AND cdi_id=? AND cs_id=?|) or die $dbh->errstr;
					my $sth_cds_ins_b = $dbh->prepare(qq|INSERT INTO concept_data_synonym (ci_id,cb_id,cdi_id,cs_id,cds_bid,cds_added,cdst_id) VALUES (?,?,?,?,?,true,?) RETURNING cds_id|) or die $dbh->errstr;


					my $sth_cds_sel_synonym = $dbh->prepare(qq|
SELECT
  ARRAY_TO_STRING(ARRAY_AGG(a.cs_name), ';') AS cs_name
FROM (
  SELECT
   cs.cs_name
  FROM
    concept_data_synonym AS cds
  LEFT JOIN concept_synonym AS cs ON cs.cs_id=cds.cs_id
  LEFT JOIN concept_data_synonym_type AS cdst ON cdst.cdst_id=cds.cdst_id
  WHERE
       cds.ci_id=?
   AND cds.cb_id=?
   AND cds.cdi_id=?
   AND cdst.cdst_name='synonym'
  ORDER BY
    cs.cs_name
) AS a
|) or die $dbh->errstr;
					my $sth_cd_upd_synonym = $dbh->prepare(qq|UPDATE concept_data SET cd_syn=? WHERE ci_id=? AND cb_id=? AND cdi_id=?|) or die $dbh->errstr;

					foreach my $cdi_pid (keys(%{$cdi_id_added_hash})){

						$sth_ct_sel->execute($ci_id,$cb_id,$cdi_pid,$CRL_HASH->{'part_of'},'%'.$crt_id.'%') or die $dbh->errstr;
						$column_number = 0;
						my $cdi_id;
						$sth_ct_sel->bind_col(++$column_number, \$cdi_id, undef);
						while($sth_ct_sel->fetch){
							&cgi_lib::common::message($cdi_id, $LOG) if(defined $LOG);
							next unless(exists $CD_ID2NAME->{$cdi_id} && defined $CD_ID2NAME->{$cdi_id} && length $CD_ID2NAME->{$cdi_id});
							&cgi_lib::common::message($CD_ID2NAME->{$cdi_id}, $LOG) if(defined $LOG);
							my $cs_pname = $cdi_id_added_hash->{$cdi_pid}->{'cs_name'};
							&cgi_lib::common::message($cs_pname, $LOG) if(defined $LOG);
							my $cds_bid = $cdi_id_added_hash->{$cdi_pid}->{'cds_id'};
							my $cs_name = ucfirst(lc(sprintf("%s of %s",&getChildFromName($CD_ID2NAME->{$cdi_id}), $cs_pname)));
							my $cs_id;
							my $cds_id;
							&cgi_lib::common::message($cs_name, $LOG) if(defined $LOG);
							unless(exists $CS_NAME2ID->{$cs_name}){
								$sth_cs_ins->execute($cs_name) or die $dbh->errstr;
								$column_number=0;
								$sth_cs_ins->bind_col(++$column_number, \$cs_id, undef);
								$sth_cs_ins->fetch;
								$sth_cs_ins->finish;

								$CS_ID2NAME->{$cs_id} = $cs_name;
								$CS_NAME2ID->{$cs_name} = $cs_id;
							}
							else{
								$cs_id = $CS_NAME2ID->{$cs_name};
							}
							$sth_cds_sel->execute($ci_id,$cb_id,$cdi_id,$cs_id) or die $dbh->errstr;
							$column_number=0;
							$sth_cds_sel->bind_col(++$column_number, \$cds_id, undef);
							$sth_cds_sel->fetch;
							$sth_cds_sel->finish;

							unless(defined $cds_id){
								$sth_cds_ins_b->execute($ci_id,$cb_id,$cdi_id,$cs_id,$cds_bid,$CDST_NAME2ID->{'synonym'}) or die $dbh->errstr;
								$column_number=0;
								$sth_cds_ins_b->bind_col(++$column_number, \$cds_id, undef);
								$sth_cds_ins_b->fetch;
								$sth_cds_ins_b->finish;
								&cgi_lib::common::message($cds_id, $LOG) if(defined $LOG);
							}
							else{
								&cgi_lib::common::message($cds_id, $LOG) if(defined $LOG);
							}

							$sth_cds_sel_synonym->execute($ci_id,$cb_id,$cdi_id) or die $dbh->errstr;
							$column_number=0;
							$sth_cds_sel_synonym->bind_col(++$column_number, \$cs_name, undef);
							$sth_cds_sel_synonym->fetch;
							$sth_cds_sel_synonym->finish;

							$sth_cd_upd_synonym->execute($cs_name,$ci_id,$cb_id,$cdi_id) or die $dbh->errstr;
							$sth_cd_upd_synonym->finish;


						}
						$sth_ct_sel->finish;

					}
					undef $sth_ct_sel;
					undef $sth_cs_ins;
					undef $sth_cds_sel;
					undef $sth_cds_ins_b;
					undef $sth_cds_sel_synonym;
					undef $sth_cd_upd_synonym;
				}

				$dbh->commit;
#				$dbh->rollback;
				$DATAS->{'success'} = JSON::XS::true;
			};
			if($@){
				$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8($@);
				&cgi_lib::common::message($DATAS->{'msg'}, $LOG) if(defined $LOG);
				$DATAS->{'success'} = JSON::XS::false;

				$dbh->rollback;
			}
			$dbh->{'AutoCommit'} = 1;
			$dbh->{'RaiseError'} = 0;

		}
	}
}

&gzip_json($DATAS);

close($LOG) if(defined $LOG);

exit;

sub snippet {
	my $column = shift;
#	return $column;
	my $querys = shift;
	if(defined $column && length $column && defined $querys && ref $querys eq 'ARRAY' && scalar @$querys){
		my $num = scalar @$querys;
		my %match_pos;
		foreach my $query (@$querys){
			my $q;
			if($anyMatch){
				if($caseSensitive){
					$q =  qr/$query/;
				}else{
					$q =  qr/$query/i;
				}
			}else{
				if($caseSensitive){
					$q =  qr/\b$query\b/;
				}else{
					$q =  qr/\b$query\b/i;
				}
			}
			next unless($column =~ $q);
			$match_pos{$&} = length $`;	#`
			$num--;
		}
#		say STDERR __LINE__.':['.$num.']['.$column.']';
		unless($num){

			%match_pos = ();
#		say STDERR __LINE__.':['.$num.']['.$column.']';

			foreach my $query (@$querys){

				my $q;
				if($anyMatch){
					if($caseSensitive){
						$q =  qr/$query/;
					}else{
						$q =  qr/$query/i;
					}
				}else{
					if($caseSensitive){
						$q =  qr/\b$query\b/;
					}else{
						$q =  qr/\b$query\b/i;
					}
				}

				my $l_column = '';
				my $r_column = $column;
#				say STDERR __LINE__.':['.$query.']';
#				while($r_column =~ /\b$query\b/i){
				while($r_column =~ $q){
					$l_column .= $`;	#`
					my $m_pos = length $l_column;
					my $m_str = $&;
					$l_column .= $m_str;
					if(exists $match_pos{$m_pos}){
						$match_pos{$m_pos} = $m_str if(length $match_pos{$m_pos} < length $m_str);
					}else{
						$match_pos{$m_pos} = $m_str;
					}
					$r_column = $';	#'
				}
			}
#		say STDERR __LINE__.':['.$num.']['.$column.']';
#		say STDERR __LINE__.':['.join(',',keys(%match_pos)).']';


			my @match_keys = map {$match_pos{$_}} sort {
				if($a == $b){
					length $match_pos{$b} <=> length $match_pos{$a};
				}else{
					$a <=> $b;
				}
			} keys(%match_pos);

#		say STDERR __LINE__.':['.join(',',@match_keys).']';

			my $org_column = $column;
			my $rep_column = '';
			foreach my $query (@match_keys){

				my $q;
				if($anyMatch){
					if($caseSensitive){
						$q =  qr/$query/;
					}else{
						$q =  qr/$query/i;
					}
				}else{
					if($caseSensitive){
						$q =  qr/\b$query\b/;
					}else{
						$q =  qr/\b$query\b/i;
					}
				}

				if($org_column =~ $q){
					$rep_column .= $`;	#`;
					$rep_column .= '<strong>' . $& . '</strong>';
					$org_column = $';	#'
				}else{
					last;
				}
			}
			if($rep_column){
				$column = $rep_column;
				$column .= $org_column if($org_column);
			}
		}
	}
	return $column;
}

sub checkCurrent {
	my %arg = @_;
	my $dbh    = $arg{'dbh'};
	my $ci_id  = $arg{'ci_id'};
	my $cb_id  = $arg{'cb_id'};
	my $md_id  = $arg{'md_id'};
	my $mv_id  = $arg{'mv_id'};
	my $cdi_id = $arg{'cdi_id'};
	my $art_ids = $arg{'art_ids'};
	my $LOG;# = $arg{'LOG'};

	my $sth_cdi_sel = $dbh->prepare(qq|select cdi_name from concept_data_info where ci_id=$ci_id AND cdi_id=?|) or die $dbh->errstr;
	my %CDI2NAME;
	my $column_number = 0;

	my ($ELEMENT, $COMP_DENSITY_USE_TERMS, $COMP_DENSITY_END_TERMS, $COMP_DENSITY, $CDI_MAP, $CDI_MAP_ART_DATE, $CDI_ID2CID, $CDI_MAP_SUM_VOLUME_DEL_ID, $CDI_DESC_OBJ_OLD_DEL_ID) = &BITS::ConceptArtMapModified::calcElementAndDensity(
		dbh     => $dbh,
		md_id   => $md_id,
		mv_id   => $mv_id,
		ci_id   => $ci_id,
		cb_id   => $cb_id,
		cdi_ids => [$cdi_id],
		LOG => $LOG
	);
=pod
	if(defined $LOG){
		&cgi_lib::common::message($ELEMENT, $LOG);
		&cgi_lib::common::message($COMP_DENSITY_USE_TERMS, $LOG);
		&cgi_lib::common::message($COMP_DENSITY_END_TERMS, $LOG);
		&cgi_lib::common::message($COMP_DENSITY, $LOG);
		&cgi_lib::common::message($CDI_MAP, $LOG);
		&cgi_lib::common::message($CDI_MAP_ART_DATE, $LOG);
		&cgi_lib::common::message($CDI_ID2CID, $LOG);
		&cgi_lib::common::message($CDI_MAP_SUM_VOLUME_DEL_ID, $LOG);
		&cgi_lib::common::message($CDI_DESC_OBJ_OLD_DEL_ID, $LOG);
	}
=cut
	my $current_use = JSON::XS::false;
	my $current_use_reason;
	foreach my $art_id (@{$art_ids}){
		if(defined $cdi_id && defined $art_id && defined $CDI_MAP_ART_DATE && ref $CDI_MAP_ART_DATE eq 'HASH' && exists $CDI_MAP_ART_DATE->{$cdi_id} && defined $CDI_MAP_ART_DATE->{$cdi_id} && ref $CDI_MAP_ART_DATE->{$cdi_id} eq 'HASH' && exists $CDI_MAP_ART_DATE->{$cdi_id}->{$art_id}){
			$current_use = JSON::XS::true;	#子供のOBJより古くない場合
			$current_use_reason = undef;
		}
		elsif(
			defined $cdi_id &&
			defined $art_id &&
			defined $CDI_DESC_OBJ_OLD_DEL_ID &&
			ref     $CDI_DESC_OBJ_OLD_DEL_ID eq 'HASH' &&
			exists  $CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id} &&
			defined $CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id} &&
			ref     $CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id} eq 'HASH' &&
			exists  $CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id}->{$art_id} &&
			defined $CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id}->{$art_id} &&
			ref     $CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id}->{$art_id} eq 'HASH' &&
			exists  $CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id}->{$art_id}->{'max_cdi_id'} &&
			defined $CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id}->{$art_id}->{'max_cdi_id'}
		){
			$current_use = JSON::XS::false;

			my $max_cdi_id = $CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id}->{$art_id}->{'max_cdi_id'};
			my $max_art_timestamp = localtime($CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id}->{$art_id}->{'max_art_timestamp'});

			if($CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id}->{$art_id}->{'max_cdi_id'} eq $CDI_DESC_OBJ_OLD_DEL_ID->{$cdi_id}->{$art_id}->{'del_cdi_id'}){
				$current_use_reason = sprintf('Older than other OBJ [%s]', $max_art_timestamp->strftime('%Y/%m/%d %H:%M:%S'));
			}
			else{
				my $max_cdi_name;
				unless(exists $CDI2NAME{$max_cdi_id} && defined $CDI2NAME{$max_cdi_id}){
					$sth_cdi_sel->execute($max_cdi_id) or die $dbh->errstr;
					$column_number = 0;
					$sth_cdi_sel->bind_col(++$column_number, \$max_cdi_name, undef);
					$sth_cdi_sel->fetch;
					$sth_cdi_sel->finish;
					$CDI2NAME{$max_cdi_id} = $max_cdi_name;
				}
				else{
					$max_cdi_name = $CDI2NAME{$max_cdi_id};
				}
				$current_use_reason = sprintf('It is older than descendant OBJ [%s][%s]', $max_cdi_name, $max_art_timestamp->strftime('%Y/%m/%d %H:%M:%S'));
			}
		}
		else{
			$current_use = JSON::XS::false;
			if(defined $cdi_id){
				$current_use_reason = 'Older than the other OBJ or descendants of OBJ';
			}
			else{
				$current_use_reason = undef;
			}
		}

	#					&cgi_lib::common::message($current_use, $LOG) if(defined $LOG);
		if(defined $cdi_id && $current_use == JSON::XS::true && defined $CDI_MAP_SUM_VOLUME_DEL_ID && exists $CDI_MAP_SUM_VOLUME_DEL_ID->{$cdi_id}){
			$current_use = JSON::XS::false;	#子供のOBJが親のボリュームの90%より多い場合
			$current_use_reason = 'Descendants of OBJ is more than 90% of the parent of the volume';
		}
		last if($current_use == JSON::XS::true);
	}
	return $current_use;
}

sub getParentFromName {
	my $name = shift;
	my $p_name;
	if($name =~ /.+ of .+/i){
		unless(
			$name !~ /\b(tributary|branch) of .+/i &&
			(
				$name =~ /\b(complex|tree|network|set) of .+/i ||
				$name =~ /\b(disk|valve|ligament|artery|vein|duct|mater|joint) of .+/i ||
				$name =~ /.+ of (Giacomini|Guyon|Carabelli|Clarke|Ecker|Calleja|Schwalbe|Zinn)\b/i
			)
		){
			my @TEMP = split(' of ',$name);
			shift @TEMP;
			$p_name = join(' of ',@TEMP);
		}
	}
	return $p_name;
}

sub getChildFromName {
	my $name = shift;
	if($name =~ /.+ of .+/i){
		unless(
			$name !~ /\b(tributary|branch) of .+/i &&
			(
				$name =~ /\b(complex|tree|network|set) of .+/i ||
				$name =~ /\b(disk|valve|ligament|artery|vein|duct|mater|joint) of .+/i ||
				$name =~ /.+ of (Giacomini|Guyon|Carabelli|Clarke|Ecker|Calleja|Schwalbe|Zinn)\b/i
			)
		){
			my @TEMP = split(' of ',$name);
			$name = shift @TEMP;
		}
	}
	return $name;
}
