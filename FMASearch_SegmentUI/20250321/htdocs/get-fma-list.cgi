#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use DBD::Pg;
use JSON::XS;
use Search::QueryParser::SQL;
use File::Spec::Functions qw(catdir catfile);
use Time::HiRes;
#use Text::MeCab;
#my $mecab = Text::MeCab->new();

use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'..','cgi_lib'),q|/bp3d/ag-common/lib|;
use BITS::Config;
require "webgl_common.pl";
use cgi_lib::common;

use constant {
	DEBUG => BITS::Config::DEBUG
};

my $LOG;

#my $query = CGI->new;
#&main($query);

my($name,$dir,$ext) = &File::Basename::fileparse($0, qr/\..*$/);
if($ext eq '.fcgi'){
	use CGI::Fast;
	while (my $q = CGI::Fast->new) {
		&main($q);
	}
}
elsif(exists $ENV{'REQUEST_METHOD'} && defined $ENV{'REQUEST_METHOD'} && length $ENV{'REQUEST_METHOD'}){
#	use CGI;
	&main(CGI->new());
}

sub main {
	my $query = shift;

	my $t0 = [&Time::HiRes::gettimeofday()];

	my $dbh = &get_dbh();

	my %FORM = ();
	my %COOKIE = ();
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

	if(DEBUG){
		open($LOG,">> $logfile");
		select($LOG);
		$| = 1;
		select(STDOUT);

		flock($LOG,2);
		print $LOG "\n[$logtime]:$0\n";
		&cgi_lib::common::message(\%FORM, $LOG);
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
		exists $FORM{BITS::Config::LOCATION_HASH_MDID_KEY} && defined $FORM{BITS::Config::LOCATION_HASH_MDID_KEY} && $FORM{BITS::Config::LOCATION_HASH_MDID_KEY} =~ /^[0-9]+$/ &&
		exists $FORM{BITS::Config::LOCATION_HASH_MVID_KEY} && defined $FORM{BITS::Config::LOCATION_HASH_MVID_KEY} && $FORM{BITS::Config::LOCATION_HASH_MVID_KEY} =~ /^[0-9]+$/ &&
		exists $FORM{BITS::Config::LOCATION_HASH_CIID_KEY} && defined $FORM{BITS::Config::LOCATION_HASH_CIID_KEY} && $FORM{BITS::Config::LOCATION_HASH_CIID_KEY} =~ /^[0-9]+$/ &&
		exists $FORM{BITS::Config::LOCATION_HASH_CBID_KEY} && defined $FORM{BITS::Config::LOCATION_HASH_CBID_KEY} && $FORM{BITS::Config::LOCATION_HASH_CBID_KEY} =~ /^[0-9]+$/
	){
		&cgi_lib::common::message("", $LOG) if(defined $LOG);
		$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8(qq|JSON形式が違います|);
		&gzip_json($DATAS);
		exit;
	}

	my $md_id = $FORM{BITS::Config::LOCATION_HASH_MDID_KEY} - 0;
	my $mv_id = $FORM{BITS::Config::LOCATION_HASH_MVID_KEY} - 0;
	my $mr_id = ($FORM{BITS::Config::LOCATION_HASH_MRID_KEY} // 1) - 0;
	my $ci_id = $FORM{BITS::Config::LOCATION_HASH_CIID_KEY} - 0;
	my $cb_id = $FORM{BITS::Config::LOCATION_HASH_CBID_KEY} - 0;

	my $crl_id = 0;

	my $searchTarget = 1;
	my $anyMatch = 1;
	my $caseSensitive = 0;

	$searchTarget = (exists $FORM{BITS::Config::SEARCH_TARGET_NAME} && defined $FORM{BITS::Config::SEARCH_TARGET_NAME} && $FORM{BITS::Config::SEARCH_TARGET_NAME} =~ /^[12]$/) ? $FORM{BITS::Config::SEARCH_TARGET_NAME} - 0 : 0;
	$anyMatch = (exists $FORM{BITS::Config::SEARCH_ANY_MATCH_NAME} && defined $FORM{BITS::Config::SEARCH_ANY_MATCH_NAME}) ? 1 : 0;
	$caseSensitive = (exists $FORM{BITS::Config::SEARCH_CASE_SENSITIVE_NAME} && defined $FORM{BITS::Config::SEARCH_CASE_SENSITIVE_NAME}) ? 1 : 0;

	my $ELEMENT2ART_IDS;

	eval{
		my @QUERY_COLUMNS = qw/cdi_name cd_name cd_syn/;

		my $operator = &get_ludia_operator();
		my $query;
		my $query_parse;
		my @QUERY;
		my $exclude;
		my @EXCLUDE;
		my $space = &cgi_lib::common::decodeUTF8(qq|　|);
		if(exists $FORM{BITS::Config::LOCATION_HASH_SEARCH_KEY} && defined $FORM{BITS::Config::LOCATION_HASH_SEARCH_KEY}){
			$query = $FORM{BITS::Config::LOCATION_HASH_SEARCH_KEY};
			$query = &cgi_lib::common::decodeUTF8($query);
			$query =~ s/$space/ /g;
			$query =~ s/\s{2,}/ /g;
			$query =~ s/^\s+//g;
			$query =~ s/\s+$//g;

			my $QUERY_HASH;

			my $column_fuzzy_op = $caseSensitive ? '~' : '~*';
			my $column_fuzzy_not_op = $caseSensitive ? '!~' : '!~*';
			my $column_type = 'char';

			my $column_callback = sub {
				my ($col, $op, $val) = @_;
				&cgi_lib::common::message("[$col][$op][$val]", $LOG) if(defined $LOG);
				$QUERY_HASH->{$val} = undef if($op eq '=');
				if($anyMatch){
					if($op eq '='){
						return "$col $column_fuzzy_op '$val'";
					}else{
						return "$col $column_fuzzy_not_op '$val'";
					}
				}else{
					if($op eq '='){
						return "$col $column_fuzzy_op E'\\\\y$val\\\\y'";
					}else{
						return "$col $column_fuzzy_not_op E'\\\\y$val\\\\y'";
					}
				}

				return "$col $op '$val'";
			};

			my $column_orm_callback = sub {
				my ($col, $op, $val) = @_;
				&cgi_lib::common::message("[$col][$op][$val]", $LOG) if(defined $LOG);
				return( $col => { $op => $val } );
			};

			my $columns;
			foreach my $col (@QUERY_COLUMNS){
				$columns->{$col} = {
					name => $col,
					type => $column_type,
					fuzzy_op => $column_fuzzy_op,
					fuzzy_not_op => $column_fuzzy_not_op,
					callback => \&$column_callback,
					orm_callback => \&$column_orm_callback
				};
			}

			my $parser = Search::QueryParser::SQL->new(
	#			columns => [qw( cdi_name cd_name cd_syn )]
				columns => $columns
			);
			eval{
				$query_parse = $parser->parse($query, 1); # 1 for explicit AND
			};
			if($@){
				&cgi_lib::common::message($@, $LOG) if(defined $LOG);
				$DATAS->{'success'} = JSON::XS::true;
				&gzip_json($DATAS);
				exit;
			}
			my $q = $query_parse . "";
			&cgi_lib::common::message($QUERY_HASH, $LOG) if(defined $LOG);

			if(defined $query && length $query){
				if(defined $query_parse){
					@QUERY = keys(%$QUERY_HASH);
				}else{
					@QUERY = split(/\s+/,$query);
				}
				push(@{$DATAS->{BITS::Config::LOCATION_HASH_SEARCH_KEY}}, @QUERY);
			}else{
				undef $query;
				$DATAS->{'success'} = JSON::XS::true;
				&gzip_json($DATAS);
				exit;
			}
		}
		if(exists $FORM{BITS::Config::LOCATION_HASH_SEARCH_EXCLUDE_KEY} && defined $FORM{BITS::Config::LOCATION_HASH_SEARCH_EXCLUDE_KEY}){
			$exclude = $FORM{BITS::Config::LOCATION_HASH_SEARCH_EXCLUDE_KEY};
			$exclude = &cgi_lib::common::decodeUTF8($exclude);
			$exclude =~ s/$space/ /g;
			$exclude =~ s/\s{2,}/ /g;
			$exclude =~ s/^\s+//g;
			$exclude =~ s/\s+$//g;

			if(defined $exclude && length $exclude){
				@EXCLUDE = split(/\s+/,$exclude);
			}else{
				undef $exclude;
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

		my $sql_cdi_name = 'cdi_name';
		my $sql_cdi_name_e = 'cd_name';
		my $sql_cdi_syn_e = 'cd_syn';

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
SQL
		if(&existsTable('buildup_data')){
			$sql.=<<SQL;
(
 SELECT
  ci_id,
  cb_id,
  cdi_id,
  cd_name,
  cd_syn,
  cd_def,
  cd_delcause
 FROM concept_data
 UNION
 SELECT
  ci_id,
  cb_id,
  cdi_id,
  cd_name,
  cd_syn,
  cd_def,
  cd_delcause
 FROM
  buildup_data WHERE md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id
)
SQL
		}else{
			$sql.=<<SQL;
 concept_data
SQL
		}

		$sql.=<<SQL;
 AS cd

LEFT JOIN (
 select ci_id,cdi_id,cdi_name from concept_data_info
) as cdi on cdi.ci_id=cd.ci_id AND cdi.cdi_id=cd.cdi_id

where
 cd_delcause is null AND
 cd.ci_id=$ci_id AND
 cd.cb_id=$cb_id
SQL

		my $sql_org = $sql;

		my @bind_values;

		unless(defined $query_parse){
			if(defined $exclude){
				my @W;
				foreach my $c (@QUERY_COLUMNS){
					my @C;
					foreach my $q (@EXCLUDE){
						if($anyMatch){
							if($caseSensitive){
								push(@C,qq|$c !~ '$q'|);
							}else{
								push(@C,qq|$c !~* '$q'|);
							}
						}else{
							if($caseSensitive){
								push(@C,qq|$c !~ E'\\\\y$q\\\\y'|);
							}else{
								push(@C,qq|$c !~* E'\\\\y$q\\\\y'|);
							}
						}
					}
					push(@W, '('.join(" AND ",@C).')');
				}
				$sql.= ' AND (' . join(" AND ",@W) . ')';

			}
		}

		&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

		if(defined $query_parse){
			&cgi_lib::common::message($query_parse, $LOG) if(defined $LOG);
#		&cgi_lib::common::message($query_parse->dbi, $LOG) if(defined $LOG);
#		&cgi_lib::common::message($query_parse->rdbo, $LOG) if(defined $LOG);

#		&cgi_lib::common::message($QUERY_HASH, $LOG) if(defined $LOG);
#		@QUERY = keys(%$QUERY_HASH);

			$sql.= ' AND (' . $query_parse . ')';
		}
		elsif(defined $query){
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
				push(@W, '('.join(" AND ",@C).')');
			}
			$sql.= ' AND (' . join(" or ",@W) . ')';

		}
		elsif(exists $FORM{BITS::Config::LOCATION_HASH_NAME_KEY} && defined $FORM{BITS::Config::LOCATION_HASH_NAME_KEY} && length $FORM{BITS::Config::LOCATION_HASH_NAME_KEY}){
			$FORM{BITS::Config::LOCATION_HASH_NAME_KEY} =~ s/$space/ /g;
#		$FORM{BITS::Config::LOCATION_HASH_NAME_KEY} =~ s/\s{2,}/ /g;
			$sql.=<<SQL;
  AND  lower(cd_name)=lower(?)
SQL
			push(@bind_values, $FORM{BITS::Config::LOCATION_HASH_NAME_KEY});
			&cgi_lib::common::message(scalar @bind_values, $LOG) if(defined $LOG);
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
			push(@bind_values, $FORM{BITS::Config::LOCATION_HASH_ID_KEY});
			&cgi_lib::common::message(scalar @bind_values, $LOG) if(defined $LOG);
		}

		elsif(exists $FORM{BITS::Config::LOCATION_HASH_IDS_KEY} && defined $FORM{BITS::Config::LOCATION_HASH_IDS_KEY} && length $FORM{BITS::Config::LOCATION_HASH_IDS_KEY}){
			my $IDS = &cgi_lib::common::decodeJSON($FORM{BITS::Config::LOCATION_HASH_IDS_KEY});
			delete $FORM{BITS::Config::LOCATION_HASH_IDS_KEY};
			if(defined $IDS && ref $IDS eq 'ARRAY' && scalar @$IDS){

				my $sql_fmt;
				if(&existsTable('buildup_tree_info')){
					if(&existsTableColumn('buildup_tree_info','md_id')){
						$sql_fmt = qq|
select cdi_id,but_cids from buildup_tree_info where md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND ci_id=$ci_id AND cb_id=$cb_id AND bul_id=$crl_id AND but_delcause is null AND (ci_id,cdi_id) in (select ci_id,cdi_id from concept_data_info where ci_id=$ci_id AND cdi_name in (%s) AND cdi_delcause is null)
|;
					}else{
						$sql_fmt = qq|
select cdi_id,but_cids from buildup_tree_info where ci_id=$ci_id AND cb_id=$cb_id AND bul_id=$crl_id AND but_delcause is null AND (ci_id,cdi_id) in (select ci_id,cdi_id from concept_data_info where ci_id=$ci_id AND cdi_name in (%s) AND cdi_delcause is null)
|;
					}
				}else{
					$sql_fmt = qq|
select cdi_id,cti_cids from concept_tree_info where ci_id=$ci_id AND cb_id=$cb_id AND crl_id=$crl_id AND cti_delcause is null AND (ci_id,cdi_id) in (select ci_id,cdi_id from concept_data_info where ci_id=$ci_id AND cdi_name in (%s) AND cdi_delcause is null)
|;
				}

				my $sth = $dbh->prepare(sprintf($sql_fmt,join(',',map {'?'} @$IDS))) or die $dbh->errstr;
				$sth->execute(@$IDS) or die $dbh->errstr;
				my $HASH_IDS = {};
				if($sth->rows()>0){
					my $column_number = 0;
					my $cdi_id;
					my $cti_cids;
					$sth->bind_col(++$column_number, \$cdi_id,   undef);
					$sth->bind_col(++$column_number, \$cti_cids,   undef);
					while($sth->fetch){
						$HASH_IDS->{$cdi_id} = undef if(defined $cdi_id);
						if(defined $cti_cids){
							$cti_cids = &cgi_lib::common::decodeJSON($cti_cids);
							if(defined $cti_cids && ref $cti_cids eq 'ARRAY' && scalar @$cti_cids){
								$HASH_IDS->{$_} = undef for(@$cti_cids);
							}
						}
					}
				}
				$sth->finish;
				undef $sth;
				undef $IDS if(defined $IDS);
				if(scalar keys(%$HASH_IDS)){
#				&cgi_lib::common::message($HASH_IDS, $LOG) if(defined $LOG);
#				my $ELEMENT_IDS = &get_element_cdi_ids($dbh,$md_id,$mv_id);
#				if(defined $ELEMENT_IDS && ref $ELEMENT_IDS eq 'ARRAY' && scalar @$ELEMENT_IDS){
#					foreach my $element_id (@$ELEMENT_IDS){
#						push(@$IDS, $element_id - 0) if(exists $HASH_IDS->{$element_id});
#					}
#				}
					$ELEMENT2ART_IDS = &get_element_art_ids($dbh,$md_id,$mv_id);
#				&cgi_lib::common::message($ELEMENT2ART_IDS, $LOG) if(defined $LOG);
					if(defined $ELEMENT2ART_IDS && ref $ELEMENT2ART_IDS eq 'HASH' && scalar keys(%$ELEMENT2ART_IDS)){
						foreach my $element_id (keys(%$ELEMENT2ART_IDS)){
							push(@$IDS, $element_id - 0) if(exists $HASH_IDS->{$element_id});
						}
					}
				}
				undef $HASH_IDS;
#			&cgi_lib::common::message($IDS, $LOG) if(defined $LOG);
				if(defined $IDS && ref $IDS eq 'ARRAY' && scalar @$IDS){
					$sql .= sprintf(' AND cd.cdi_id IN (%s)',join(',',map {'?'} @$IDS));
					push(@bind_values, @$IDS);
					&cgi_lib::common::message(scalar @bind_values, $LOG) if(defined $LOG);
				}
				else{
					$DATAS->{'success'} = JSON::XS::true;
					&gzip_json($DATAS);
					exit;
				}
			}
			else{
				&cgi_lib::common::message("", $LOG) if(defined $LOG);
				$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8(qq|JSON形式が違います|);
				&gzip_json($DATAS);
				exit;
			}
		}

		#ダブルクリック時にpart_ofの一階層上のFMAを選択する処理（未実装）
		elsif(exists $FORM{BITS::Config::LOCATION_HASH_CID_KEY} && defined $FORM{BITS::Config::LOCATION_HASH_CID_KEY} && length $FORM{BITS::Config::LOCATION_HASH_CID_KEY}){
			if($FORM{BITS::Config::LOCATION_HASH_CID_KEY} =~ /^FMA[0-9]+/){
				my $_sql;
				if(&existsTable('buildup_tree')){
					if(&existsTableColumn('buildup_tree','md_id')){
						$_sql = qq|select cdi_pid from buildup_tree AS T LEFT JOIN (SELECT * FROM concept_data_info) AS C ON C.ci_id=T.ci_id AND C.cdi_id=T.cdi_id where T.md_id=$md_id AND T.mv_id=$mv_id AND T.mr_id=$mr_id AND T.ci_id=$ci_id AND T.cb_id=$cb_id AND T.bul_id=4 AND C.cdi_name=?|;
					}else{
						$_sql = qq|select cdi_pid from buildup_tree AS T LEFT JOIN (SELECT * FROM concept_data_info) AS C ON C.ci_id=T.ci_id AND C.cdi_id=T.cdi_id where T.ci_id=$ci_id AND T.cb_id=$cb_id AND T.bul_id=4 AND C.cdi_name=?|;
					}
				}else{
					if(&existsTableColumn('concept_tree','bul_id')){
						$_sql = qq|select cdi_pid from concept_tree AS T LEFT JOIN (SELECT * FROM concept_data_info) AS C ON C.ci_id=T.ci_id AND C.cdi_id=T.cdi_id where T.ci_id=$ci_id AND T.cb_id=$cb_id AND T.bul_id=4 AND C.cdi_name=?|;
					}else{
						$_sql = qq|select cdi_pid from concept_tree AS T LEFT JOIN (SELECT * FROM concept_data_info) AS C ON C.ci_id=T.ci_id AND C.cdi_id=T.cdi_id where T.ci_id=$ci_id AND T.cb_id=$cb_id AND T.crl_id=4 AND C.cdi_name=?|;
					}
				}
				my $sth = $dbh->prepare($_sql) or die $dbh->errstr;
				$sth->execute($FORM{BITS::Config::LOCATION_HASH_CID_KEY}) or die $dbh->errstr;
				my $HASH_IDS;
				if($sth->rows()>0){
					my $column_number = 0;
					my $cdi_pid;
					$sth->bind_col(++$column_number, \$cdi_pid,   undef);
					while($sth->fetch){
						$HASH_IDS->{$cdi_pid} = undef if(defined $cdi_pid);
					}
				}
				$sth->finish;
				undef $sth;

				&cgi_lib::common::message($HASH_IDS, $LOG) if(defined $LOG);

				if(defined $HASH_IDS && ref $HASH_IDS eq 'HASH' && scalar keys(%$HASH_IDS)){
					$sql .= sprintf(' AND cd.cdi_id IN (%s)',join(',',map {'?'} keys(%$HASH_IDS)));
					push(@bind_values, keys(%$HASH_IDS));
					&cgi_lib::common::message(scalar @bind_values, $LOG) if(defined $LOG);
				}
				else{
					$DATAS->{'success'} = JSON::XS::true;
					&gzip_json($DATAS);
					exit;
				}
			}
			else{
				&cgi_lib::common::message("", $LOG) if(defined $LOG);
				$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8(qq|JSON形式が違います|);
				&gzip_json($DATAS);
				exit;
			}
		}

		&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

		my $cdi_cids;
		if(exists $FORM{BITS::Config::LOCATION_HASH_CIDS_KEY} && defined $FORM{BITS::Config::LOCATION_HASH_CIDS_KEY} && length $FORM{BITS::Config::LOCATION_HASH_CIDS_KEY}){
			$cdi_cids = &cgi_lib::common::decodeJSON($FORM{BITS::Config::LOCATION_HASH_CIDS_KEY});
			delete $FORM{BITS::Config::LOCATION_HASH_CIDS_KEY};

			if(defined $cdi_cids && ref $cdi_cids eq 'ARRAY'){
				&cgi_lib::common::message(scalar @$cdi_cids, $LOG) if(defined $LOG);
			}else{
				&cgi_lib::common::message(0, $LOG) if(defined $LOG);
			}
#			&cgi_lib::common::message($cdi_cids, $LOG) if(defined $LOG);
		}

		&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

		my $ELEMENTS;
		my $USE_ELEMENTS;
		$USE_ELEMENTS = $ELEMENTS = &get_elements($dbh,$md_id,$mv_id,$cdi_cids);

		&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);
#		&cgi_lib::common::message($searchTarget, $LOG) if(defined $LOG);
#		&cgi_lib::common::message($ELEMENTS, $LOG) if(defined $LOG);

		my $ELEMENT_IDS_HASH;
		if(defined $searchTarget && $searchTarget){
			my $ELEMENT_IDS;

			my $CITIES;
			my $CITIES_FILE = &catdir($FindBin::Bin,'MENU_SEGMENTS','CITIES.json');
			if(-e $CITIES_FILE && -f $CITIES_FILE && -s $CITIES_FILE){
				$CITIES = &cgi_lib::common::readFileJSON($CITIES_FILE);
			}
			if(defined $CITIES && ref $CITIES eq 'HASH' && exists $CITIES->{'children'} && defined $CITIES->{'children'} && ref $CITIES->{'children'} eq 'ARRAY' && scalar @{$CITIES->{'children'}}){
				if(exists $FORM{'cities_ids'} && defined $FORM{'cities_ids'} && length $FORM{'cities_ids'}){
					my $cities_ids = [map {$_-0} grep {$_ =~ /^[0-9]+$/} split(/,/,$FORM{'cities_ids'})];
#					&cgi_lib::common::message($cities_ids, $LOG) if(defined $LOG);
					if(defined $cities_ids && ref $cities_ids eq 'ARRAY' && scalar @$cities_ids){

						my $segments;
						foreach my $cities_id (@$cities_ids){
							next unless(defined $CITIES->{'children'}->[$cities_id-0] && ref $CITIES->{'children'}->[$cities_id-0] eq 'HASH' && exists $CITIES->{'children'}->[$cities_id-0]->{'name'} && defined $CITIES->{'children'}->[$cities_id-0]->{'name'} && length $CITIES->{'children'}->[$cities_id-0]->{'name'});
#							push(@$segments, sprintf("CITIES/%s", $CITIES->{'children'}->[$cities_id-1]->{'name'}));	# unfound対応(2019/12/27)
							push(@$segments, sprintf("CITIES/%s", $CITIES->{'children'}->[$cities_id-0]->{'name'}));	# unfound対応(2019/12/27)
						}
						$FORM{'segments'} = &cgi_lib::common::encodeJSON($segments) if(defined $segments && ref $segments eq 'ARRAY' && scalar @$segments);
#						&cgi_lib::common::message($FORM{'segments'}, $LOG) if(exists $FORM{'segments'} && defined $LOG);
					}
				}
				else{
					my $segments;
					foreach my $cities (@{$CITIES->{'children'}}){
						next unless(defined $cities && ref $cities eq 'HASH' && exists $cities->{'name'} && defined $cities->{'name'} && length $cities->{'name'});
						push(@$segments, sprintf("CITIES/%s", $cities->{'name'}));
					}
#					&cgi_lib::common::message($segments, $LOG) if(defined $LOG);
					$FORM{'segments'} = &cgi_lib::common::encodeJSON($segments) if(defined $segments && ref $segments eq 'ARRAY' && scalar @$segments);
				}
			}
			if(exists $FORM{'segments'} && defined $FORM{'segments'} && length $FORM{'segments'}){
				my $segments = &cgi_lib::common::decodeJSON($FORM{'segments'});
#				&cgi_lib::common::message($segments, $LOG) if(defined $LOG);
				if(defined $segments && ref $segments eq 'ARRAY' && scalar @$segments){
					my $SEG2ART;
#					my $SEG2ART_FILE = &catdir($FindBin::Bin,'MENU_SEGMENTS','SEG2ART.json');
					my $SEG2ART_FILE = &catdir($FindBin::Bin,'MENU_SEGMENTS', (exists $FORM{'SEG2ART'} && defined $FORM{'SEG2ART'} && length $FORM{'SEG2ART'} ? $FORM{'SEG2ART'} : 'SEG2ART_INSIDE').'.json');
					&cgi_lib::common::message($SEG2ART_FILE, $LOG) if(defined $LOG);
					if(-e $SEG2ART_FILE && -f $SEG2ART_FILE && -s $SEG2ART_FILE){
						$SEG2ART = &cgi_lib::common::readFileJSON($SEG2ART_FILE);
					}
#					&cgi_lib::common::message($SEG2ART, $LOG) if(defined $LOG);
					if(defined $SEG2ART && ref $SEG2ART eq 'HASH'){
						$USE_ELEMENTS = undef;
						my $USE_SEG2ART;
						foreach my $segment (@$segments){
							my($seg_region,$seg_name) = split('/',$segment);
							next unless(exists $SEG2ART->{$seg_region} && defined $SEG2ART->{$seg_region} && ref $SEG2ART->{$seg_region} eq 'HASH');
							next unless(exists $SEG2ART->{$seg_region}->{$seg_name} && defined $SEG2ART->{$seg_region}->{$seg_name} && ref $SEG2ART->{$seg_region}->{$seg_name} eq 'HASH');
#							&cgi_lib::common::message($seg_region, $LOG) if(defined $LOG);
#							&cgi_lib::common::message($seg_name, $LOG) if(defined $LOG);
							$USE_SEG2ART->{$_} = undef for(keys(%{$SEG2ART->{$seg_region}->{$seg_name}}));
#							if(defined $LOG){
#								&cgi_lib::common::message(sprintf("%s\t%s\t%s",$seg_name,$seg_region,$_), $LOG) for(keys(%{$SEG2ART->{$seg_region}->{$seg_name}}));
#							}
						}
#				&cgi_lib::common::message($USE_SEG2ART, $LOG) if(defined $LOG);
	#					my $ELEMENTS = &get_elements($dbh,$md_id,$mv_id);
						if(defined $ELEMENTS && ref $ELEMENTS eq 'ARRAY' && scalar @$ELEMENTS){
#							&cgi_lib::common::message($ELEMENTS, $LOG) if(defined $LOG);
							foreach my $element (@$ELEMENTS){
								my $art_id = $element->{&BITS::Config::OBJ_ID_DATA_FIELD_ID()};
#				&cgi_lib::common::message($art_id, $LOG) if(defined $LOG);
#								&cgi_lib::common::message($element, $LOG) if(defined $LOG && $element->{&BITS::Config::OBJ_ID_DATA_FIELD_ID()} eq 'MM7214');
								next unless(exists $USE_SEG2ART->{$art_id});
#				&cgi_lib::common::message($art_id, $LOG) if(defined $LOG);
								push(@$ELEMENT_IDS, $element->{&BITS::Config::CONCEPT_DATA_INFO_DATA_FIELD_ID()});
#								&cgi_lib::common::message($element, $LOG) if(defined $LOG && $element->{&BITS::Config::CONCEPT_DATA_INFO_DATA_FIELD_ID()}==108031);
#								&cgi_lib::common::message($element, $LOG) if(defined $LOG && $element->{&BITS::Config::OBJ_ID_DATA_FIELD_ID()} eq 'MM7214');
								push(@$USE_ELEMENTS, $element);
							}
						}
	#					undef $ELEMENTS;
						&cgi_lib::common::message('', $LOG) if(defined $LOG);
					}
					else{
						$ELEMENT_IDS = &get_element_cdi_ids($dbh,$md_id,$mv_id,$cdi_cids);
						&cgi_lib::common::message('', $LOG) if(defined $LOG);
					}
				}
				else{
					$ELEMENT_IDS = &get_element_cdi_ids($dbh,$md_id,$mv_id,$cdi_cids);
					&cgi_lib::common::message('', $LOG) if(defined $LOG);
				}
			}
			else{
				$ELEMENT_IDS = &get_element_cdi_ids($dbh,$md_id,$mv_id,$cdi_cids);
				&cgi_lib::common::message('', $LOG) if(defined $LOG);
#				&cgi_lib::common::message($ELEMENT_IDS, $LOG) if(defined $LOG);
			}
#		$ELEMENT_IDS = &get_element_cdi_ids($dbh,$md_id,$mv_id) unless(defined $ELEMENT_IDS && ref $ELEMENT_IDS eq 'ARRAY');

			&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

			if(defined $ELEMENT_IDS && ref $ELEMENT_IDS eq 'ARRAY'){
				&cgi_lib::common::message(scalar @$ELEMENT_IDS, $LOG) if(defined $LOG);
			}else{
				&cgi_lib::common::message(0, $LOG) if(defined $LOG);
			}
#			&cgi_lib::common::message($ELEMENT_IDS, $LOG) if(defined $LOG);


#		&cgi_lib::common::message($ELEMENT_IDS, $LOG) if(defined $LOG);
			if(defined $ELEMENT_IDS && ref $ELEMENT_IDS eq 'ARRAY' && scalar @$ELEMENT_IDS){
				$ELEMENT_IDS_HASH = {map {$_=>undef} @$ELEMENT_IDS};
				&cgi_lib::common::message(scalar keys(%$ELEMENT_IDS_HASH), $LOG) if(defined $LOG);
			}
			if(defined $ELEMENT_IDS && ref $ELEMENT_IDS eq 'ARRAY' && scalar @$ELEMENT_IDS && $searchTarget==BITS::Config::SEARCH_TARGET_WHOLE_VALUE){
				my $sql_fmt;
				if(&existsTable('buildup_tree_info')){
					if(&existsTableColumn('buildup_tree_info','md_id')){
#						$sql_fmt = qq|select but_pids from buildup_tree_info where md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND ci_id=$ci_id AND cb_id=$cb_id AND bul_id=$crl_id AND but_delcause is null AND but_pids is not null AND cdi_id in (%s)|;
						$sql_fmt = qq|select but_pids,cdi_id from buildup_tree_info where md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND ci_id=$ci_id AND cb_id=$cb_id AND bul_id=$crl_id AND but_delcause is null AND but_pids is not null|;
					}else{
#						$sql_fmt = qq|select but_pids from buildup_tree_info where ci_id=$ci_id AND cb_id=$cb_id AND bul_id=$crl_id AND but_delcause is null AND but_pids is not null AND cdi_id in (%s)|;
						$sql_fmt = qq|select but_pids,cdi_id from buildup_tree_info where ci_id=$ci_id AND cb_id=$cb_id AND bul_id=$crl_id AND but_delcause is null AND but_pids is not null|;
					}
				}else{
#					$sql_fmt = qq|select cti_pids from concept_tree_info where ci_id=$ci_id AND cb_id=$cb_id AND crl_id=$crl_id AND cti_delcause is null AND cti_pids is not null AND cdi_id in (%s)|;
					$sql_fmt = qq|select cti_pids,cdi_id from concept_tree_info where ci_id=$ci_id AND cb_id=$cb_id AND crl_id=$crl_id AND cti_delcause is null AND cti_pids is not null|;
				}
				&cgi_lib::common::message($sql_fmt, $LOG) if(defined $LOG);

#				&cgi_lib::common::message(sprintf($sql_fmt,join(',',map {'?'} @$ELEMENT_IDS)), $LOG) if(defined $LOG);

#				my $sth = $dbh->prepare(sprintf($sql_fmt,join(',',map {'?'} @$ELEMENT_IDS))) or die $dbh->errstr;
#				$sth->execute(@$ELEMENT_IDS) or die $dbh->errstr;
				my $sth = $dbh->prepare($sql_fmt) or die $dbh->errstr;
				$sth->execute() or die $dbh->errstr;
				my $HASH_IDS = {};
				if($sth->rows()>0){
					my $column_number = 0;
					my $cti_pids;
					my $cdi_id;
					$sth->bind_col(++$column_number, \$cti_pids,   undef);
					$sth->bind_col(++$column_number, \$cdi_id,   undef);
					while($sth->fetch){
#						next unless(defined $cti_pids);
						next unless(defined $cti_pids && defined $cdi_id);
						next unless(exists $ELEMENT_IDS_HASH->{$cdi_id});
						$cti_pids = &cgi_lib::common::decodeJSON($cti_pids);
						next unless(defined $cti_pids && ref $cti_pids eq 'ARRAY' && scalar @$cti_pids);
						$HASH_IDS->{$_}->{$cdi_id} = undef for(@$cti_pids);
					}
				}
				$sth->finish;
				undef $sth;

				if(exists $ENV{'AG_LEXICALSUPER'} && defined $ENV{'AG_LEXICALSUPER'} && length $ENV{'AG_LEXICALSUPER'} && -e $ENV{'AG_LEXICALSUPER'} && -f $ENV{'AG_LEXICALSUPER'} && -s $ENV{'AG_LEXICALSUPER'} && -r $ENV{'AG_LEXICALSUPER'}){
					&cgi_lib::common::message($ENV{'AG_LEXICALSUPER'}, $LOG) if(defined $LOG);

					my $lexicalsuper;
					my $lexicalsuper_path = $ENV{'AG_LEXICALSUPER'};
					open(my $IN, $lexicalsuper_path) or die qq|$! [$lexicalsuper_path]|;
					while(<$IN>){
						chomp;
						my(undef,$cdi_name,undef,undef,$cdi_pname) = split(/\s*!\s*/);
			#			say sprintf("[%s]\t[%s]",$cdi_name,$cdi_pname);

						if($cdi_name =~ /^FMA:*([0-9]+)$/){
							$cdi_name = $1;
			#				$cdi_name =~ s/^0//g;
							$cdi_name = 'FMA'.$cdi_name;
						}
						else{
							next;
						}
						if($cdi_pname =~ /^FMA:*([0-9]+)$/){
							$cdi_pname = $1;
			#				$cdi_pname =~ s/^0//g;
							$cdi_pname = 'FMA'.$cdi_pname;
						}
						else{
							next;
						}
			#			say sprintf("[%s]\t[%s]",$cdi_name,$cdi_pname);

#						if(defined $lexicalsuper && ref $lexicalsuper eq 'HASH' && exists $lexicalsuper->{$cdi_name}){
#							say STDERR sprintf("[WARN] Multiple parents!! child:[%s]\tparent1:[%s]\tparent2:[%s]",$cdi_name,$cdi_pname,$lexicalsuper->{$cdi_name});
#						}
						$lexicalsuper->{$cdi_name} = $cdi_pname;
					}
					close($IN);

				}

#				push(@$ELEMENT_IDS, keys(%$HASH_IDS));
				&cgi_lib::common::message($ELEMENT_IDS_HASH, $LOG) if(defined $LOG);
				$ELEMENT_IDS_HASH->{$_} = $HASH_IDS->{$_} for(keys(%$HASH_IDS));
				&cgi_lib::common::message($ELEMENT_IDS_HASH, $LOG) if(defined $LOG);

				undef $HASH_IDS;
			}
#			if(defined $ELEMENT_IDS && ref $ELEMENT_IDS eq 'ARRAY' && scalar @$ELEMENT_IDS){
#				$sql .= sprintf(' AND cd.cdi_id IN (%s)',join(',',map {'?'} @$ELEMENT_IDS));
#				push(@bind_values, @$ELEMENT_IDS);
#			}
			if(defined $ELEMENT_IDS_HASH && ref $ELEMENT_IDS_HASH eq 'HASH' && scalar keys(%$ELEMENT_IDS_HASH)){
				$sql .= sprintf(' AND cd.cdi_id IN (%s)',join(',',map {'?'} keys(%$ELEMENT_IDS_HASH)));
				push(@bind_values, keys(%$ELEMENT_IDS_HASH));
				&cgi_lib::common::message(scalar @bind_values, $LOG) if(defined $LOG);
			}
			undef $ELEMENT_IDS;
#			undef $ELEMENT_IDS_HASH;

		}

#		&cgi_lib::common::message($sql, $LOG) if(defined $LOG);
#		&cgi_lib::common::message(scalar @bind_values, $LOG) if(defined $LOG);
#		&cgi_lib::common::message(\@bind_values, $LOG) if(defined $LOG);
		&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

#		&cgi_lib::common::message($sql, $LOG) if(defined $LOG);
#		&cgi_lib::common::message(\@bind_values, $LOG) if(defined $LOG);

		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		if(scalar @bind_values){
			$sth->execute(@bind_values) or die $dbh->errstr;
		}else{
			$sth->execute() or die $dbh->errstr;
		}
		&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);
		print $LOG __LINE__.":\$sth->rows()=[".$sth->rows()."]\n" if(defined $LOG);
		$DATAS->{'total'} = $sth->rows();

		#子供のIDのみで再検索
		if($DATAS->{'total'}>0 && defined $ELEMENT_IDS_HASH && ref $ELEMENT_IDS_HASH eq 'HASH' && scalar keys(%$ELEMENT_IDS_HASH) && $searchTarget==BITS::Config::SEARCH_TARGET_WHOLE_VALUE){
			my $HASH_IDS;

			my $cdi_name;
			my $cdi_name_e;
			my $cdi_name_l;
			my $cdi_syn_e;
			my $cdi_def_e;
			my $cdi_id;
			my $column_number = 0;
			$sth->bind_col(++$column_number, \$cdi_name,   undef);
			$sth->bind_col(++$column_number, \$cdi_name_e,   undef);
			$sth->bind_col(++$column_number, \$cdi_syn_e,   undef);
			$sth->bind_col(++$column_number, \$cdi_def_e,   undef);
			$sth->bind_col(++$column_number, \$cdi_id,   undef);
			while($sth->fetch){
				next unless(exists $ELEMENT_IDS_HASH->{$cdi_id});
				if(defined $ELEMENT_IDS_HASH->{$cdi_id} && ref $ELEMENT_IDS_HASH->{$cdi_id} eq 'HASH'){
					foreach my $cdi_cid (keys(%{$ELEMENT_IDS_HASH->{$cdi_id}})){
						$HASH_IDS->{$cdi_cid} = undef;
					}
				}
				else{
					$HASH_IDS->{$cdi_id} = undef;
				}
			}
			$sth->finish;
			undef $sth;

			$sql = $sql_org;
			@bind_values = keys(%$HASH_IDS);
			$sql .= sprintf(' AND cd.cdi_id IN (%s)',join(',',map {'?'} @bind_values));
			$sth = $dbh->prepare($sql) or die $dbh->errstr;
			$sth->execute(@bind_values) or die $dbh->errstr;
			$DATAS->{'total'} = $sth->rows();
		}
		undef $ELEMENT_IDS_HASH if(defined $ELEMENT_IDS_HASH);

		my $USE_IDS;

		if($DATAS->{'total'}>0){

			my $RENDER_INFO;
			if(
				exists	$FORM{'system_ids'} &&
				defined	$FORM{'system_ids'} &&
				exists	$FORM{'version'} &&
				defined	$FORM{'version'}
			){
				my $version = $FORM{'version'};
				my $system_ids = &cgi_lib::common::decodeJSON($FORM{'system_ids'});
				if(defined $system_ids && ref $system_ids eq 'ARRAY' && scalar @$system_ids){
					my $system_ids_hash = {};
					$system_ids_hash->{$_} = undef for(@$system_ids);
					my $RENDER_INFO_FILE = &catdir($FindBin::Bin,'renderer_file','renderer_file.json');
					my $ALL_RENDER_INFO;
					$ALL_RENDER_INFO = &cgi_lib::common::readFileJSON($RENDER_INFO_FILE) if(-e $RENDER_INFO_FILE && -f $RENDER_INFO_FILE && -s $RENDER_INFO_FILE);
					if(
						defined	$ALL_RENDER_INFO &&
						ref			$ALL_RENDER_INFO eq 'HASH' &&
						exists	$ALL_RENDER_INFO->{$version} &&
						defined	$ALL_RENDER_INFO->{$version} &&
						ref			$ALL_RENDER_INFO->{$version} eq 'HASH' &&
						exists	$ALL_RENDER_INFO->{$version}->{'ids'} &&
						defined	$ALL_RENDER_INFO->{$version}->{'ids'} &&
						ref			$ALL_RENDER_INFO->{$version}->{'ids'} eq 'HASH'
					){
						foreach my $cdi_name (keys(%{$ALL_RENDER_INFO->{$version}->{'ids'}})){
							next unless(
								exists	$ALL_RENDER_INFO->{$version}->{'ids'}->{$cdi_name} &&
								defined	$ALL_RENDER_INFO->{$version}->{'ids'}->{$cdi_name} &&
								ref			$ALL_RENDER_INFO->{$version}->{'ids'}->{$cdi_name} eq 'HASH' &&
								exists	$ALL_RENDER_INFO->{$version}->{'ids'}->{$cdi_name}->{BITS::Config::SYSTEM_ID_DATA_FIELD_ID} &&
								defined	$ALL_RENDER_INFO->{$version}->{'ids'}->{$cdi_name}->{BITS::Config::SYSTEM_ID_DATA_FIELD_ID}
							);
							my $system_id = $ALL_RENDER_INFO->{$version}->{'ids'}->{$cdi_name}->{BITS::Config::SYSTEM_ID_DATA_FIELD_ID};
							next unless(exists $system_ids_hash->{$system_id});
							$RENDER_INFO->{$cdi_name} = $ALL_RENDER_INFO->{$version}->{'ids'}->{$cdi_name};
						}
					}
				}
			}
			&cgi_lib::common::message($RENDER_INFO, $LOG) if(defined $LOG);

			my $buildup_tree_sql;
			if(&existsTable('buildup_tree')){
				if(&existsTableColumn('buildup_tree','md_id')){
					$buildup_tree_sql = qq|SELECT C.cdi_name,C.cdi_name_e,L.bul_name_e FROM buildup_tree AS T LEFT JOIN concept_data_info AS C ON C.ci_id=T.ci_id AND C.cdi_id=T.cdi_pid LEFT JOIN buildup_logic AS L ON L.bul_id=T.bul_id WHERE T.md_id=$md_id AND T.mv_id=$mv_id AND T.mr_id=$mr_id AND T.ci_id=$ci_id AND T.cb_id=$cb_id AND T.cdi_id=?|;
				}else{
					$buildup_tree_sql = qq|SELECT C.cdi_name,C.cdi_name_e,L.bul_name_e FROM buildup_tree AS T LEFT JOIN concept_data_info AS C ON C.ci_id=T.ci_id AND C.cdi_id=T.cdi_pid LEFT JOIN buildup_logic AS L ON L.bul_id=T.bul_id WHERE T.ci_id=$ci_id AND T.cb_id=$cb_id AND T.cdi_id=?|;
				}
			}else{
				if(&existsTableColumn('concept_tree','bul_id')){
					$buildup_tree_sql = qq|SELECT C.cdi_name,C.cdi_name_e,L.bul_name_e FROM concept_tree AS T LEFT JOIN concept_data_info AS C ON C.ci_id=T.ci_id AND C.cdi_id=T.cdi_pid LEFT JOIN concept_relation_logic AS L ON L.bul_id=T.bul_id WHERE T.ci_id=$ci_id AND T.cb_id=$cb_id AND T.cdi_id=?|;
				}else{
					$buildup_tree_sql = qq|SELECT C.cdi_name,C.cdi_name_e,L.crl_name   FROM concept_tree AS T LEFT JOIN concept_data_info AS C ON C.ci_id=T.ci_id AND C.cdi_id=T.cdi_pid LEFT JOIN concept_relation_logic AS L ON L.crl_id=T.crl_id WHERE T.ci_id=$ci_id AND T.cb_id=$cb_id AND T.cdi_id=?|;
				}
			}
			my $buildup_tree_sth = $dbh->prepare($buildup_tree_sql) or die $dbh->errstr;
			my $cdi_pname;
			my $cdi_pname_e;
			my $bul_name;



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

			while($sth->fetch){
				if(defined $ELEMENT_IDS_HASH){
					next unless(defined $cdi_id);
					next unless(exists $ELEMENT_IDS_HASH->{$cdi_id});
				}
				if(defined $RENDER_INFO && ref $RENDER_INFO eq 'HASH'){
					next unless(defined $cdi_name);
					next unless(exists $RENDER_INFO->{$cdi_name});
				}

				if(defined $cdi_syn_e){
					if($cdi_syn_e =~ /;/){
#						$cdi_syn_e = '<div><div style="" draggable="true"><label class="cdi_syn_e">'.join('</label></div><div style="margin-top:4px;" draggable="true"><label class="cdi_syn_e">',split(/;/,$cdi_syn_e)).'</label></div></div>';
						$cdi_syn_e = [split(/;/,$cdi_syn_e)];
					}else{
#						$cdi_syn_e = '<div><div style="" draggable="true"><label class="cdi_syn_e">'.$cdi_syn_e.'</label></div></div>';
						$cdi_syn_e = [$cdi_syn_e];
					}
				}

=pod
				if(defined $query){
					$snippet_cdi_name = &snippet($snippet_cdi_name, \@QUERY, {'searchTarget' => $searchTarget, 'anyMatch' => $anyMatch, 'caseSensitive' => $caseSensitive} );
					$snippet_cdi_name_e = &snippet($snippet_cdi_name_e, \@QUERY, {'searchTarget' => $searchTarget, 'anyMatch' => $anyMatch, 'caseSensitive' => $caseSensitive} );
					$snippet_cdi_syn_e = &snippet($snippet_cdi_syn_e, \@QUERY, {'searchTarget' => $searchTarget, 'anyMatch' => $anyMatch, 'caseSensitive' => $caseSensitive} );

					my $line_height = 16;

					$snippet_cdi_name = '<div style="margin:2px;"><div style="line-height:'.$line_height.'px;"><label class="'.BITS::Config::ID_DATA_FIELD_ID.'">'.$snippet_cdi_name.'</label></div></div>';
					$snippet_cdi_name_e = '<div style="margin:2px;"><div style="line-height:'.$line_height.'px;"><label class="'.BITS::Config::NAME_DATA_FIELD_ID.'">'.$snippet_cdi_name_e.'</label></div></div>';

					if(defined $snippet_cdi_syn_e){
						if($snippet_cdi_syn_e =~ /;/){
							$snippet_cdi_syn_e = '<div style="margin:2px;"><div style="line-height:'.$line_height.'px;"><label class="'.BITS::Config::SYNONYM_DATA_FIELD_ID.'">'.join('</label></div><div style="margin-top:4px;line-height:'.$line_height.'px;"><label class="'.BITS::Config::SYNONYM_DATA_FIELD_ID.'">',split(/;/,$snippet_cdi_syn_e)).'</label></div></div>';
						}else{
							$snippet_cdi_syn_e = '<div style="margin:2px;"><div style="line-height:'.$line_height.'px;"><label class="'.BITS::Config::SYNONYM_DATA_FIELD_ID.'">'.$snippet_cdi_syn_e.'</label></div></div>';
						}
					}
				}else{
#					$snippet_cdi_name = undef;
#					$snippet_cdi_name_e = undef;
#					$snippet_cdi_syn_e = undef;
				}
=cut
				my $node_cdi_name_e;
				my $node_cdi_syn_e;
				if(defined $cdi_name_e && length $cdi_name_e){
#					$node_cdi_name_e = [];
#					for(my $node = $mecab->parse($cdi_name_e);$node;$node = $node->next){
#						my $surface = $node->surface;
#						next unless(defined $surface);
#						push(@$node_cdi_name_e, $surface);
#						$DATAS->{'words'}->{lc($surface)}->{$cdi_name} = undef;
#					}
					$node_cdi_name_e = &mecab($cdi_name_e);
					if(defined $node_cdi_name_e && ref $node_cdi_name_e eq 'ARRAY'){
						foreach my $surface (@$node_cdi_name_e){
							$DATAS->{'words'}->{lc($surface)}->{$cdi_name} = undef;
						}
					}
				}
				if(defined $cdi_syn_e){
					$node_cdi_syn_e = [];
					foreach my $str (@$cdi_syn_e){
#						my $arr = [];
#						for(my $node = $mecab->parse($str);$node;$node = $node->next){
#							my $surface = $node->surface;
#							next unless(defined $surface);
#							push(@$arr, $surface);
#							$DATAS->{'words'}->{lc($surface)}->{$cdi_name} = undef;
#						}
						my $arr = &mecab($str);
						if(defined $arr && ref $arr eq 'ARRAY'){
							foreach my $surface (@$arr){
								$DATAS->{'words'}->{lc($surface)}->{$cdi_name} = undef;
							}
						}
						push(@$node_cdi_syn_e, $arr);
					}
				}

				my $relation;

				$buildup_tree_sth->execute($cdi_id) or die $dbh->errstr;
				$column_number = 0;
				$buildup_tree_sth->bind_col(++$column_number, \$cdi_pname,   undef);
				$buildup_tree_sth->bind_col(++$column_number, \$cdi_pname_e,   undef);
				$buildup_tree_sth->bind_col(++$column_number, \$bul_name,   undef);
				while($buildup_tree_sth->fetch){
					my $hash  = {};
					$hash->{BITS::Config::ID_DATA_FIELD_ID} = $cdi_pname;
					$hash->{BITS::Config::NAME_DATA_FIELD_ID} = $cdi_pname_e;
					my $node_cdi_pname_e;
					if(defined $cdi_pname_e && length $cdi_pname_e){
#						$node_cdi_pname_e = [];
#						for(my $node = $mecab->parse($cdi_pname_e);$node;$node = $node->next){
#							my $surface = $node->surface;
#							next unless(defined $surface);
#							push(@$node_cdi_pname_e, $surface);
#							$DATAS->{'words'}->{lc($surface)}->{$cdi_name} = undef;
#						}
						$node_cdi_pname_e = &mecab($cdi_pname_e);
						if(defined $node_cdi_pname_e && ref $node_cdi_pname_e eq 'ARRAY'){
							foreach my $surface (@$node_cdi_pname_e){
								$DATAS->{'words'}->{lc($surface)}->{$cdi_name} = undef;
							}
						}


					}
					$hash->{'node'} = $node_cdi_pname_e;

					push(@{$relation->{$bul_name}}, $hash);

				}
				$buildup_tree_sth->finish;




				my $HASH = {};
				$HASH->{BITS::Config::MODEL_DATA_FIELD_ID}           = $md_id-0;
				$HASH->{BITS::Config::MODEL_VERSION_DATA_FIELD_ID}   = $mv_id-0;
				$HASH->{BITS::Config::MODEL_REVISION_DATA_FIELD_ID}  = $mr_id-0;
				$HASH->{BITS::Config::CONCEPT_INFO_DATA_FIELD_ID}    = $ci_id-0;
				$HASH->{BITS::Config::CONCEPT_BUILD_DATA_FIELD_ID}   = $cb_id-0;
				$HASH->{BITS::Config::ID_DATA_FIELD_ID}              = $cdi_name;
				$HASH->{BITS::Config::NAME_DATA_FIELD_ID}            = $cdi_name_e;
				$HASH->{BITS::Config::SYNONYM_DATA_FIELD_ID}         = $cdi_syn_e;
				$HASH->{BITS::Config::DEFINITION_DATA_FIELD_ID}      = $cdi_def_e;

=pod
#				if(defined $query){
				$HASH->{BITS::Config::SNIPPET_ID_DATA_FIELD_ID}      = $snippet_cdi_name;
				$HASH->{BITS::Config::SNIPPET_NAME_DATA_FIELD_ID}    = $snippet_cdi_name_e;
				$HASH->{BITS::Config::SNIPPET_SYNONYM_DATA_FIELD_ID} = $snippet_cdi_syn_e;
#				}
=cut

				if(defined $ELEMENT2ART_IDS && ref $ELEMENT2ART_IDS eq 'HASH' && exists $ELEMENT2ART_IDS->{$cdi_id} && defined $ELEMENT2ART_IDS->{$cdi_id} && ref $ELEMENT2ART_IDS->{$cdi_id} eq 'HASH'){
					$HASH->{BITS::Config::CONCEPT_DATA_INFO_DATA_FIELD_ID}    = $cdi_id-0;
					$HASH->{$_} = $ELEMENT2ART_IDS->{$cdi_id}->{$_} for(keys(%{$ELEMENT2ART_IDS->{$cdi_id}}));
				}

				$HASH->{'node_cdi_name_e'} = $node_cdi_name_e;
				$HASH->{'node_cdi_syn_e'}  = $node_cdi_syn_e;
				$HASH->{'relation'}        = $relation;


				push(@{$DATAS->{'datas'}},$HASH);

				$USE_IDS->{$cdi_id} = undef;
			}
			undef $buildup_tree_sth;
		}
		$sth->finish;
		undef $sth;

		if(exists $DATAS->{'words'} && defined $DATAS->{'words'} && ref $DATAS->{'words'} eq 'HASH'){
			foreach my $word (keys(%{$DATAS->{'words'}})){
				if(exists $DATAS->{'words'}->{$word} && defined $DATAS->{'words'}->{$word} && ref $DATAS->{'words'}->{$word} eq 'HASH'){
					my $cdi_names = [sort keys(%{$DATAS->{'words'}->{$word}})];
					$DATAS->{'words'}->{$word} = $cdi_names;
				}
				else{
					delete $DATAS->{'words'}->{$word};
				}
			}
		}



		&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

		if(defined $USE_IDS && defined $USE_ELEMENTS){
			my $ART_FILE_INFO;
			my $ART_FILE_INFO_FILE = &catdir($FindBin::Bin,'renderer_file','art_file_info.json');
			$ART_FILE_INFO = &cgi_lib::common::readFileJSON($ART_FILE_INFO_FILE) if(-e $ART_FILE_INFO_FILE && -f $ART_FILE_INFO_FILE && -s $ART_FILE_INFO_FILE);
			if(defined $ART_FILE_INFO && ref $ART_FILE_INFO eq 'HASH'){

				my $sql_fmt;
				if(&existsTable('buildup_tree_info')){
					if(&existsTableColumn('buildup_tree_info','md_id')){
						$sql_fmt = qq|
select but_cids from buildup_tree_info where md_id=$md_id AND mv_id=$mv_id AND mr_id=$mr_id AND ci_id=$ci_id AND cb_id=$cb_id AND bul_id=$crl_id AND but_delcause is null AND but_pids is not null AND cdi_id in (%s)
|;
					}else{
						$sql_fmt = qq|
select but_cids from buildup_tree_info where ci_id=$ci_id AND cb_id=$cb_id AND bul_id=$crl_id AND but_delcause is null AND but_pids is not null AND cdi_id in (%s)
|;
					}
				}else{
					$sql_fmt = qq|
select cti_cids from concept_tree_info where ci_id=$ci_id AND cb_id=$cb_id AND crl_id=$crl_id AND cti_delcause is null AND cti_pids is not null AND cdi_id in (%s)
|;
				}

				&cgi_lib::common::message(sprintf($sql_fmt,join(',',map {'?'} keys(%$USE_IDS))), $LOG) if(defined $LOG);

				my $sth = $dbh->prepare(sprintf($sql_fmt,join(',',map {'?'} keys(%$USE_IDS)))) or die $dbh->errstr;
				$sth->execute(keys(%$USE_IDS)) or die $dbh->errstr;
				my $HASH_IDS = {};
				if($sth->rows()>0){
					my $column_number = 0;
					my $cti_cids;
					$sth->bind_col(++$column_number, \$cti_cids,   undef);
					while($sth->fetch){
						next unless(defined $cti_cids);
						$cti_cids = &cgi_lib::common::decodeJSON($cti_cids);
						next unless(defined $cti_cids && ref $cti_cids eq 'ARRAY' && scalar @$cti_cids);
						$USE_IDS->{$_} = undef for(@$cti_cids);
					}
				}
				$sth->finish;
				undef $sth;

				my $ELEMENTS_HASH;
				$ELEMENTS_HASH->{$_->{&BITS::Config::CONCEPT_DATA_INFO_DATA_FIELD_ID()}} = $_ for(@$USE_ELEMENTS);
				my $ART_IDS_HASH;
				my $CDI_NAMES_HASH;
				if(defined $ELEMENTS_HASH && ref $ELEMENTS_HASH eq 'HASH' && scalar keys(%$ELEMENTS_HASH)){
					foreach my $cdi_id (keys(%$USE_IDS)){
						next unless(exists $ELEMENTS_HASH->{$cdi_id} && defined $ELEMENTS_HASH->{$cdi_id} && ref $ELEMENTS_HASH->{$cdi_id} eq 'HASH');
						my $art_id = $ELEMENTS_HASH->{$cdi_id}->{&BITS::Config::OBJ_ID_DATA_FIELD_ID()};
						next unless(exists $ART_FILE_INFO->{$art_id} && defined $ART_FILE_INFO->{$art_id} && ref $ART_FILE_INFO->{$art_id} eq 'HASH');

						my $cdi_name = $ELEMENTS_HASH->{$cdi_id}->{&BITS::Config::ID_DATA_FIELD_ID()};

						$ART_IDS_HASH->{$art_id} = $ART_FILE_INFO->{$art_id}->{&BITS::Config::OBJ_POLYS_FIELD_ID()};
						$CDI_NAMES_HASH->{$cdi_name} = undef;
					}
				}

				$DATAS->{'#elements'} = 0;
				$DATAS->{'elements'} = [];
				$DATAS->{'#objs'} = 0;
				$DATAS->{'objs'} = [];

				if(defined $CDI_NAMES_HASH && ref $CDI_NAMES_HASH eq 'HASH'){
					$DATAS->{'#elements'} = scalar keys(%$CDI_NAMES_HASH);
					push($DATAS->{'elements'}, sort keys(%$CDI_NAMES_HASH));
				}

				my $art_polys = 0;
				if(defined $ART_IDS_HASH && ref $ART_IDS_HASH eq 'HASH' && scalar keys(%$ART_IDS_HASH)){
					foreach my $art_id (keys(%$ART_IDS_HASH)){
						$art_polys += $ART_IDS_HASH->{$art_id};
					}
					$DATAS->{'#objs'} = scalar keys(%$ART_IDS_HASH);
					push(@{$DATAS->{'objs'}},keys(%$ART_IDS_HASH));
				}
				$DATAS->{'#polygons'} = $art_polys;
			}

		}

		$DATAS->{'success'} = JSON::XS::true;
	};
	if($@){
		$DATAS->{'msg'} = &cgi_lib::common::decodeUTF8($@);
		&cgi_lib::common::message($DATAS->{'msg'}, $LOG) if(defined $LOG);
		$DATAS->{'msg'} =~ s/\s+at\s+\/.+$//g;
		$DATAS->{'success'} = JSON::XS::false;
	}

	&gzip_json($DATAS);

	&cgi_lib::common::message(&Time::HiRes::tv_interval($t0), $LOG) if(defined $LOG);

	close($LOG) if(defined $LOG);
}

exit;

sub snippet {
	my $column = shift;
	my $querys = shift;
	my $options = shift;
	$options = $options || {};

	my $searchTarget  = exists $options->{'searchTarget'} && defined $options->{'searchTarget'} ? $options->{'searchTarget'} : 1;
	my $anyMatch      = exists $options->{'anyMatch'} && defined $options->{'anyMatch'} ? $options->{'anyMatch'} : 1;
	my $caseSensitive = exists $options->{'caseSensitive'} && defined $options->{'caseSensitive'} ? $options->{'caseSensitive'} : 0;

#	&cgi_lib::common::message($querys, $LOG) if(defined $LOG);
	if(defined $column && length $column && defined $querys && ref $querys eq 'ARRAY' && scalar @$querys){
		my $num = scalar @$querys;
		my $all_num = $num;
		my %match_pos;
		foreach (@$querys){
			my $query = quotemeta($_);
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
		if($all_num>$num){

			%match_pos = ();
#		say STDERR __LINE__.':['.$num.']['.$column.']';

			foreach (@$querys){
				my $query = quotemeta($_);
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
			foreach (@match_keys){
				my $query = quotemeta($_);
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

sub get_elements {
	my $dbh = shift;
	my $md_id = shift;
	my $mv_id = shift;
	my $cdi_ids = shift;

	my $ART_FILE_INFO;
#	my $ART_FILE_INFO_FILE = &catdir($FindBin::Bin,'renderer_file','art_file_info.json');
#	if(-e $ART_FILE_INFO_FILE && -f $ART_FILE_INFO_FILE && -s $ART_FILE_INFO_FILE){
#		$ART_FILE_INFO = &cgi_lib::common::readFileJSON($ART_FILE_INFO_FILE);
#	}

	my @bind_values;
	my $WHERE = '';
	my $cdi_ids_hash;
	if(defined $cdi_ids && ref $cdi_ids eq 'ARRAY' && scalar @$cdi_ids){
#		$WHERE = sprintf(' AND cm.cdi_id IN (%s)',join(',',map {'?'} @$cdi_ids));
#		push(@bind_values, @$cdi_ids);

		$cdi_ids_hash ={map {$_=>undef} @$cdi_ids};
	}
	&cgi_lib::common::message($cdi_ids_hash, $LOG);

	my $IDS;
	my $sql = qq|
select
 cm.cdi_id,
 cm.art_id,
 cdi.cdi_name
from (
 select ci_id,cdi_id,art_id from concept_art_map as cm
 where
  (cm.md_id,cm.mv_id,cm.mr_id,cm.cdi_id) in (select md_id,mv_id,max(mr_id),cdi_id from concept_art_map where md_id=$md_id AND mv_id=$mv_id group by md_id,mv_id,cdi_id)
  AND cm_use
  AND cm_delcause is null
  $WHERE
) as cm
left join (
 select
  ci_id,
  cdi_id,
  cdi_name
 from
  concept_data_info
) as cdi on cdi.ci_id=cm.ci_id and cdi.cdi_id=cm.cdi_id
group by
 cm.cdi_id,
 cm.art_id,
 cdi.cdi_name
order by
 cm.art_id,
 cdi.cdi_name
|;
	&cgi_lib::common::message($sql, $LOG);
	&cgi_lib::common::message(\@bind_values, $LOG);
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	if(scalar @bind_values){
		$sth->execute(@bind_values) or die $dbh->errstr;
	}else{
		$sth->execute() or die $dbh->errstr;
	}
	if($sth->rows()>0){
		&cgi_lib::common::message($sth->rows(), $LOG);
		my $column_number = 0;
		my $cdi_id;
		my $art_id;
		my $cdi_name;
		$sth->bind_col(++$column_number, \$cdi_id,   undef);
		$sth->bind_col(++$column_number, \$art_id,   undef);
		$sth->bind_col(++$column_number, \$cdi_name,   undef);
		while($sth->fetch){

			next if(defined $cdi_ids_hash && !exists $cdi_ids_hash->{$cdi_id});

			my $hash;
			if(defined $ART_FILE_INFO && ref $ART_FILE_INFO eq 'HASH' && exists $ART_FILE_INFO->{$art_id} && defined $ART_FILE_INFO->{$art_id} && ref $ART_FILE_INFO->{$art_id} eq 'HASH'){
				$hash->{$_} = $ART_FILE_INFO->{$art_id}->{$_} for(keys(%{$ART_FILE_INFO->{$art_id}}));
			}
			$hash->{&BITS::Config::CONCEPT_DATA_INFO_DATA_FIELD_ID()} = $cdi_id;
			$hash->{&BITS::Config::OBJ_ID_DATA_FIELD_ID()} = $art_id;
			$hash->{&BITS::Config::ID_DATA_FIELD_ID()} = $cdi_name;
			push(@$IDS, $hash);
		}
	}
	$sth->finish;
	undef $sth;
	&cgi_lib::common::message(scalar @{$IDS}, $LOG);
	return $IDS;
}

sub get_element_cdi_ids {
	my $dbh = shift;
	my $md_id = shift;
	my $mv_id = shift;
	my $cdi_ids = shift;

	my @bind_values;
	my $WHERE = '';
	my $cdi_ids_hash;
	if(defined $cdi_ids && ref $cdi_ids eq 'ARRAY' && scalar @$cdi_ids){
#		$WHERE = sprintf(' AND cdi_id IN (%s)',join(',',map {'?'} @$cdi_ids));
#		push(@bind_values, @$cdi_ids);
		$cdi_ids_hash ={map {$_=>undef} @$cdi_ids};
	}

	my $IDS;
	my $sql = qq|
select
 cdi_id
from
 concept_art_map
where
 (md_id,mv_id,mr_id,cdi_id) in (select md_id,mv_id,max(mr_id),cdi_id from concept_art_map where md_id=$md_id AND mv_id=$mv_id group by md_id,mv_id,cdi_id)
 AND cm_use
 AND cm_delcause is null
 $WHERE
group by
 cdi_id
|;
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	if(scalar @bind_values){
		$sth->execute(@bind_values) or die $dbh->errstr;
	}else{
		$sth->execute() or die $dbh->errstr;
	}
	if($sth->rows()>0){
		my $column_number = 0;
		my $cdi_id;
		$sth->bind_col(++$column_number, \$cdi_id,   undef);
		while($sth->fetch){
			next unless(defined $cdi_id);
			next if(defined $cdi_ids_hash && !exists $cdi_ids_hash->{$cdi_id});
			push(@$IDS, $cdi_id);
		}
	}
	$sth->finish;
	undef $sth;
	return $IDS;
}

sub get_element_art_ids {
	my $dbh = shift;
	my $md_id = shift;
	my $mv_id = shift;

	my $ID2COLOR;
	my $convert_coloring_table_file = &catfile(&File::Basename::dirname($0),'..','tools','convert_coloring_table.txt');
	if(-e $convert_coloring_table_file && -f $convert_coloring_table_file && -s $convert_coloring_table_file){
		open(my $IN, $convert_coloring_table_file) or die "$! [$convert_coloring_table_file]";
		while(<$IN>){
			chomp;
			my($cdi_name,$cdi_id,$color_group,$color) = split(/\t/);
			$ID2COLOR->{$cdi_id} = $color;
		}
	}

	my $sth_data = $dbh->prepare(qq|select art_data from art_file where art_id=? limit 1|) or die $dbh->errstr;

	my $IDS;
	my $sql = qq{
select
 cm.cdi_id,
 cm.art_id,
 COALESCE(cd.seg_color,bd.seg_color),
 afi.art_name || afi.art_ext as art_filename,
 EXTRACT(EPOCH FROM afi.art_timestamp) as art_timestamp
from
 concept_art_map cm

LEFT JOIN (
 select
  cd.ci_id,
  cd.cb_id,
  cd.cdi_id,
  cd.seg_id,
  cs.seg_color
 from
  concept_data as cd
 LEFT JOIN (
  select * from concept_segment
 ) as cs on cs.seg_id=cd.seg_id
) as cd on cd.ci_id=cm.ci_id AND cd.cb_id=cm.cb_id AND cd.cdi_id=cm.cdi_id

LEFT JOIN (
 select
  cd.md_id,
  cd.mv_id,
  cd.mr_id,
  cd.cdi_id,
  cd.seg_id,
  cs.seg_color
 from
  buildup_data as cd
 LEFT JOIN (
  select * from concept_segment
 ) as cs on cs.seg_id=cd.seg_id
) as bd on bd.md_id=cm.md_id AND bd.mv_id=cm.mv_id AND bd.mr_id=cm.mr_id AND bd.cdi_id=cm.cdi_id


LEFT JOIN (
 select * from art_file_info
) as afi on afi.art_id=cm.art_id

where
 (cm.md_id,cm.mv_id,cm.mr_id,cm.cdi_id) in (select md_id,mv_id,max(mr_id),cdi_id from concept_art_map where md_id=$md_id AND mv_id=$mv_id group by md_id,mv_id,cdi_id)
 AND cm.cm_use
 AND cm.cm_delcause is null
group by
 cm.cdi_id,
 cm.art_id,
 COALESCE(cd.seg_color,bd.seg_color),
 art_filename,
 art_timestamp
};
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;

	my $convert_obj_three = &catfile($FindBin::Bin,,'static','js','three','utils','converters','obj','convert_obj_three.py');
	my $old_umask = umask(0);

#	&cgi_lib::common::message($sth->rows(), $LOG) if(defined $LOG);

#	my $art_file_path = $BITS::Config::ART_FILE_PATH;
	my $art_file_path = &catfile($FindBin::Bin,'art_file');

	if($sth->rows()>0){
		my $column_number = 0;
		my $cdi_id;
		my $art_id;
		my $seg_color;
		my $art_filename;
		my $art_timestamp;
		$sth->bind_col(++$column_number, \$cdi_id,   undef);
		$sth->bind_col(++$column_number, \$art_id,   undef);
		$sth->bind_col(++$column_number, \$seg_color,   undef);
		$sth->bind_col(++$column_number, \$art_filename,   undef);
		$sth->bind_col(++$column_number, \$art_timestamp,   undef);
		while($sth->fetch){
			next unless(defined $cdi_id && defined $art_id && defined $art_filename && defined $art_timestamp);
			my $art_path = &catfile($art_file_path, "$art_id.obj");
			my $art_js_path = &catfile($art_file_path, "$art_id.js");
			my $art_bin_path = &catfile($art_file_path, "$art_id.bin");
			my $art_json_path = &catfile($art_file_path, "$art_id.json");
#			my $art_gz_path = &catfile($art_file_path, "$art_id.obj.gz");
			my $art_gz_path = &catfile($art_file_path, "$art_id.ogz");
#			&cgi_lib::common::message($art_path, $LOG) if(defined $LOG);
#			&cgi_lib::common::message($art_js_path, $LOG) if(defined $LOG);
#			&cgi_lib::common::message($art_bin_path, $LOG) if(defined $LOG);
			unless(-e $art_path && -s $art_path){
				my $art_data;
				$sth_data->execute($art_id) or die $dbh->errstr;
				$sth_data->bind_col(1, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
				$sth_data->fetch;
				$sth_data->finish;
				if(defined $art_data && open(my $OBJ,"> $art_path")){
					flock($OBJ,2);
					binmode($OBJ,':utf8');
					print $OBJ $art_data;
					close($OBJ);
					undef $OBJ;
					utime $art_timestamp,$art_timestamp,$art_path;
				}
				undef $art_data;
			}
=pod
			unless(-e $art_js_path && -s $art_js_path && -e $art_bin_path && -s $art_bin_path){
				if(-e $art_path && -s $art_path){
					system(qq|python $convert_obj_three -i $art_path -o $art_js_path -t binary 1>/dev/null 2>&1|);
					utime $art_timestamp,$art_timestamp,$art_js_path if(-e $art_js_path && -s $art_js_path);
					utime $art_timestamp,$art_timestamp,$art_bin_path if(-e $art_bin_path && -s $art_bin_path);
				}
			}
			unless(-e $art_json_path && -s $art_json_path){
				if(-e $art_path && -s $art_path){
					system(qq|python $convert_obj_three -i $art_path -o $art_json_path 1>/dev/null 2>&1|);
					utime $art_timestamp,$art_timestamp,$art_json_path if(-e $art_json_path && -s $art_json_path);
				}
			}
=cut

#ここでは、圧縮しない
#			unless(-e $art_gz_path && -s $art_gz_path){
#				if(-e $art_path && -s $art_path){
#					system(qq|/bin/gzip -c -9 $art_path > $art_gz_path|);
#					utime $art_timestamp,$art_timestamp,$art_gz_path if(-e $art_gz_path && -s $art_gz_path);
#				}
#			}

#			my ($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,$atime,$mtime,$ctime,$blksize,$blocks) = stat($art_path);
			$IDS->{$cdi_id}->{BITS::Config::OBJ_ID_DATA_FIELD_ID} = $art_id;

#			$IDS->{$cdi_id}->{BITS::Config::OBJ_URL_DATA_FIELD_ID} = &abs2rel($art_path,$BITS::Config::HTDOCS_PATH);
#			$IDS->{$cdi_id}->{BITS::Config::OBJ_URL_DATA_FIELD_ID} = &abs2rel($art_js_path,$BITS::Config::HTDOCS_PATH);

			$IDS->{$cdi_id}->{BITS::Config::OBJ_URL_DATA_FIELD_ID} = &abs2rel($art_path,$FindBin::Bin);
#			$IDS->{$cdi_id}->{BITS::Config::OBJ_URL_DATA_FIELD_ID} = &abs2rel($art_js_path,$FindBin::Bin);
#			$IDS->{$cdi_id}->{BITS::Config::OBJ_URL_DATA_FIELD_ID} = &abs2rel($art_json_path,$FindBin::Bin);

			if(-e $art_gz_path && -f $art_gz_path && -s $art_gz_path){
				$IDS->{$cdi_id}->{BITS::Config::OBJ_URL_DATA_FIELD_ID} = &abs2rel($art_gz_path,$FindBin::Bin);
			}else{
			}


#			$IDS->{$cdi_id}->{BITS::Config::OBJ_TIMESTAMP_DATA_FIELD_ID} = $mtime;
			$IDS->{$cdi_id}->{BITS::Config::OBJ_TIMESTAMP_DATA_FIELD_ID} = $art_timestamp - 0;
			$IDS->{$cdi_id}->{BITS::Config::OBJ_FILENAME_FIELD_ID} = $art_filename;
			if(defined $ID2COLOR && ref $ID2COLOR eq 'HASH'){
				if(exists $ID2COLOR->{$cdi_id}){
					$IDS->{$cdi_id}->{BITS::Config::CONCEPT_DATA_COLOR_DATA_FIELD_ID} = $ID2COLOR->{$cdi_id};
				}else{
					$IDS->{$cdi_id}->{BITS::Config::CONCEPT_DATA_COLOR_DATA_FIELD_ID} = defined $seg_color ? $seg_color : '#F0D2A0';
				}
			}else{
				$IDS->{$cdi_id}->{BITS::Config::CONCEPT_DATA_COLOR_DATA_FIELD_ID} = $seg_color;
			}
		}
	}
	umask($old_umask);
	$sth->finish;
	undef $sth;
	return $IDS;
}

sub mecab {
	my $str = shift;
	my $arr;
	if(defined $str && length $str){
		$str =~ s/([^a-z0-9\s]+)/ $1 /ig;
		$str =~ s/^\s+//g;
		$str =~ s/\s+$//g;
		$arr = [split(/\s+/,$str)];
	}
	return $arr
}
