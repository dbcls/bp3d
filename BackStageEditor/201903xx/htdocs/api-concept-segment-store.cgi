#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;

use JSON::XS;
use DBD::Pg;
use File::Basename;
use File::Copy;
use File::Spec;
use File::Spec::Functions qw(abs2rel catdir catfile splitdir);
use Digest::MD5;
use Time::HiRes;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
require "webgl_common.pl";

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);

my($logfile,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);

$logfile .= qq|.$FORM{cmd}| if(exists $FORM{cmd});

open(LOG,"> $logfile");
select(LOG);
$| = 1;
select(STDOUT);
flock(LOG,2);
print LOG "\n[$logtime]:$0\n";
foreach my $key (sort keys(%ENV)){
	print LOG __LINE__,":\$ENV{$key}=[",$ENV{$key},"]\n";
}
foreach my $key (sort keys(%FORM)){
	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
}
#print LOG "\n";
#&setDefParams(\%FORM,\%COOKIE);
#foreach my $key (sort keys(%FORM)){
#	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}
#print LOG "\n";
#&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
#foreach my $key (sort keys(%FORM)){
#	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}
#print LOG "\n";
#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $where;
my @bind_values = ();
if(exists $FORM{'filter'}){
	my $filter;
	eval{$filter=&JSON::XS::decode_json($FORM{'filter'});};
	if(defined $filter){
		my @W;
		foreach my $f (@$filter){
			next unless(exists $f->{'property'} && defined $f->{'property'} && exists $f->{'value'} && defined $f->{'value'});
			push(@W,qq|$f->{property}=?|);
			push(@bind_values,$f->{value});
		}
		$where = qq|where |.join(" and ",@W) if(scalar @W > 0);
	}
}

my $orderby;
if(exists $FORM{'sort'}){
	my $order;
	eval{$order=&JSON::XS::decode_json($FORM{'sort'});};
	if(defined $order){
		my @O;
		foreach my $o (@$order){
			next unless(exists $o->{'property'} && defined $o->{'property'} && exists $o->{'direction'} && defined $o->{'direction'});
			push(@O,qq|$o->{'property'} $o->{'direction'}|);
		}
		$orderby = qq|order by |.join(',',@O) if(scalar @O > 0);
	}
}
#29:$FORM{'filter'}=[[{"property":"md_id","value":1}]]

$FORM{'cmd'} = 'read' unless(exists $FORM{'cmd'} && defined $FORM{'cmd'});

my $DATASET = {
	datas => [],
	total => 0,
	success => JSON::XS::false
};

if($FORM{'cmd'} eq 'read'){
	eval{
		my $sql=<<SQL;
select * from (
select
 seg_id,
 seg_name,
 upper(seg_color) as seg_color,
 upper(seg_thum_bgcolor) as seg_thum_bgcolor,
 upper(seg_thum_bocolor) as seg_thum_bocolor,
 upper(seg_thum_fgcolor) as seg_thum_fgcolor,
 cdi_ids,
 seg_delcause,
 EXTRACT(EPOCH FROM seg_entry) as seg_entry
from
 concept_segment as cs
) as a
$where
$orderby
SQL

		print LOG __LINE__,":\$sql=[",$sql,"]\n";
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		if(scalar @bind_values > 0){
			$DATASET->{total} = $sth->execute(@bind_values) or die $dbh->errstr;
		}else{
			$DATASET->{total} = $sth->execute() or die $dbh->errstr;
		}

		my($seg_id,$seg_name,$seg_color,$seg_thum_bgcolor,$seg_thum_bocolor,$seg_thum_fgcolor,$seg_delcause,$seg_entry,$cdi_ids);

		my $column_number = 0;
		$sth->bind_col(++$column_number, \$seg_id, undef);
		$sth->bind_col(++$column_number, \$seg_name, undef);
		$sth->bind_col(++$column_number, \$seg_color, undef);
		$sth->bind_col(++$column_number, \$seg_thum_bgcolor, undef);
		$sth->bind_col(++$column_number, \$seg_thum_bocolor, undef);
		$sth->bind_col(++$column_number, \$seg_thum_fgcolor, undef);
		$sth->bind_col(++$column_number, \$cdi_ids, undef);
		$sth->bind_col(++$column_number, \$seg_delcause, undef);
		$sth->bind_col(++$column_number, \$seg_entry, undef);


		my $sth_cdi = $dbh->prepare(qq|select cdi_name from concept_data_info where cdi_delcause is null and ci_id=$FORM{ci_id} and cdi_id=?|) or die $dbh->errstr;

		while($sth->fetch){

			$cdi_ids = &cgi_lib::common::decodeJSON($cdi_ids) if(defined $cdi_ids);
			$cdi_ids = undef if(defined $cdi_ids && ref $cdi_ids eq 'ARRAY' && scalar @$cdi_ids == 0);
			if(defined $cdi_ids && ref $cdi_ids eq 'ARRAY' && scalar @$cdi_ids){
				foreach my $cdi_id (@$cdi_ids){
					$sth_cdi->execute($cdi_id) or die $dbh->errstr;
					my $column_number = 0;
					$sth_cdi->bind_col(++$column_number, \$cdi_id, undef);
					$sth_cdi->fetch;
					$sth_cdi->finish;
				}
				$cdi_ids = [sort {$a cmp $b} grep {defined $_} @$cdi_ids];
				if(scalar @$cdi_ids){
					$cdi_ids = join(',',@$cdi_ids);
				}else{
					$cdi_ids = undef;
				}
			}

			my $HASH = {
				seg_id => $seg_id+0,

				seg_name => $seg_name,
				seg_color => $seg_color,
				seg_thum_bgcolor => $seg_thum_bgcolor,
				seg_thum_bocolor => $seg_thum_bocolor,
				seg_thum_fgcolor => $seg_thum_fgcolor,
				seg_delcause => $seg_delcause,

				cdi_names => $cdi_ids,

				seg_entry => $seg_entry+0,


			};
			push(@{$DATASET->{'datas'}},$HASH);
		}
		$sth->finish;
		undef $sth;

		undef $sth_cdi;

		$DATASET->{'total'} = scalar @{$DATASET->{'datas'}};
		$DATASET->{'success'} = JSON::XS::true;
	};
	if($@){
		$DATASET->{'msg'} = $@;
		print LOG __LINE__,":",$@,"\n";
	}

}
elsif(exists $FORM{'datas'} && defined $FORM{'datas'}){
	my $datas;
	eval{$datas = &JSON::XS::decode_json($FORM{'datas'});};
	if(defined $datas && ref $datas eq 'ARRAY' && scalar @$datas){
		if($FORM{'cmd'} eq 'create'){

#$dbh->do(qq|ALTER TABLE concept_art_map DISABLE TRIGGER USER;|) or die $dbh->errstr;
#$dbh->do(qq|ALTER TABLE history_concept_art_map DISABLE TRIGGER USER;|) or die $dbh->errstr;

			$dbh->{'AutoCommit'} = 0;
			$dbh->{'RaiseError'} = 1;
			eval{
				my $sql_ins=<<SQL;
insert into concept_segment (
 seg_name,
 seg_color,
 seg_thum_bgcolor,
 seg_thum_bocolor,
 seg_thum_fgcolor,
 cdi_ids,
 seg_delcause,
 seg_entry,
 seg_openid
) values (
 ?,
 upper(?),
 upper(?),
 upper(?),
 upper(?),
 ?,
 ?,
 now(),
 'system'
)
RETURNING seg_id
SQL
				my $sth_ins = $dbh->prepare($sql_ins) or die $dbh->errstr;

				my $sth_cdi = $dbh->prepare(qq|select cdi_id from concept_data_info where cdi_delcause is null and ci_id=$FORM{ci_id} and cdi_name=?|) or die $dbh->errstr;

				foreach my $data (@$datas){
					next unless(
						defined $data->{'seg_name'}         && $data->{'seg_name'} &&
						defined $data->{'seg_color'}        && $data->{'seg_color'} &&
						defined $data->{'seg_thum_bgcolor'} && $data->{'seg_thum_bgcolor'} &&
						defined $data->{'seg_thum_fgcolor'} && $data->{'seg_thum_fgcolor'} &&
						defined $data->{'seg_use'}
					);
#muscle
#FMA5022,FMA10474,FMA32558,FMA85453

					my $cdi_ids;
					if(defined $data->{'cdi_names'} && length $data->{'cdi_names'}){
						$cdi_ids = [split(/[^A-Za-z0-9]+/,$data->{'cdi_names'})];
						if(defined $cdi_ids && ref $cdi_ids eq 'ARRAY' && scalar @$cdi_ids){
							foreach my $cdi_id (@$cdi_ids){
								$sth_cdi->execute($cdi_id) or die $dbh->errstr;
								my $column_number = 0;
								$sth_cdi->bind_col(++$column_number, \$cdi_id, undef);
								$sth_cdi->fetch;
								$sth_cdi->finish;
							}
							$cdi_ids = [sort {$a <=> $b} grep {defined $_} @$cdi_ids];
							if(scalar @$cdi_ids){
								$cdi_ids = &cgi_lib::common::encodeJSON($cdi_ids);
							}else{
								$cdi_ids = undef;
							}
						}
					}

					my $seg_id;
					my $seg_delcause;
					$seg_delcause = 'no use' if($data->{'seg_use'} == JSON::XS::false);
					my $param_num=0;
					$sth_ins->bind_param(++$param_num, $data->{'seg_name'}, undef);
					$sth_ins->bind_param(++$param_num, $data->{'seg_color'}, undef);
					$sth_ins->bind_param(++$param_num, $data->{'seg_thum_bgcolor'}, undef);
					$sth_ins->bind_param(++$param_num, $data->{'seg_thum_bocolor'}, undef);
					$sth_ins->bind_param(++$param_num, $data->{'seg_thum_fgcolor'}, undef);
					$sth_ins->bind_param(++$param_num, $cdi_ids, undef);
					$sth_ins->bind_param(++$param_num, $seg_delcause, undef);
					$sth_ins->execute() or die $dbh->errstr;
					$DATASET->{'total'} += $sth_ins->rows();
					$sth_ins->bind_col(1, \$seg_id, undef);
					$sth_ins->fetch;
					$sth_ins->finish;

					undef $seg_id;
					undef $seg_delcause;
					undef $param_num;
				}
				undef $sth_ins;

				$dbh->commit();

				$DATASET->{'success'} = JSON::XS::true;
			};
			if($@){
				$DATASET->{'msg'} = $@;
				print LOG __LINE__,":",$@,"\n";
				$dbh->rollback;
			}
			$dbh->{'AutoCommit'} = 1;
			$dbh->{'RaiseError'} = 0;
		}
		elsif($FORM{'cmd'} eq 'update'){
			$dbh->{'AutoCommit'} = 0;
			$dbh->{'RaiseError'} = 1;
			eval{
				my $ci_id = $FORM{'ci_id'};
				my $cb_id = $FORM{'cb_id'};

				my $sql_sel=<<SQL;
select
 seg_name,
 upper(seg_color) as seg_color,
 upper(seg_thum_bgcolor) as seg_thum_bgcolor,
 upper(seg_thum_bocolor) as seg_thum_bocolor,
 upper(seg_thum_fgcolor) as seg_thum_fgcolor,
 cdi_ids,
 seg_delcause
from
 concept_segment
where
 seg_id=?
SQL

				my $sql_upd1=<<SQL;
update concept_segment set
 seg_name=?,
 seg_color=upper(?),
 seg_thum_bgcolor=upper(?),
 seg_thum_bocolor=upper(?),
 seg_thum_fgcolor=upper(?),
 cdi_ids=?,
 seg_delcause=?,
 seg_entry=now()
where
 seg_id=?
SQL

				my $sql_upd2=<<SQL;
update concept_segment set
 seg_name=?,
 seg_color=upper(?),
 seg_thum_bgcolor=upper(?),
 seg_thum_bocolor=upper(?),
 seg_thum_fgcolor=upper(?),
 cdi_ids=?,
 seg_delcause=?
where
 seg_id=?
SQL
				my $sth_sel = $dbh->prepare($sql_sel) or die $dbh->errstr;
				my $sth_upd1 = $dbh->prepare($sql_upd1) or die $dbh->errstr;
				my $sth_upd2 = $dbh->prepare($sql_upd2) or die $dbh->errstr;

				my $sth_cdi = $dbh->prepare(qq|select cdi_id from concept_data_info where cdi_delcause is null and ci_id=$FORM{ci_id} and cdi_name=?|) or die $dbh->errstr;

				my @update_seg_ids;
				foreach my $data (@$datas){
					next unless(
						defined $data->{'seg_name'}         && $data->{'seg_name'} &&
						defined $data->{'seg_color'}        && $data->{'seg_color'} &&
						defined $data->{'seg_thum_bgcolor'} && $data->{'seg_thum_bgcolor'} &&
						defined $data->{'seg_thum_fgcolor'} && $data->{'seg_thum_fgcolor'} &&
						defined $data->{'seg_use'}
					);

					my $seg_name;
					my $seg_color;
					my $seg_thum_bgcolor;
					my $seg_thum_bocolor;
					my $seg_thum_fgcolor;
					my $cdi_ids;
					my $seg_delcause;
					my $seg_use;

					$sth_sel->execute($data->{'seg_id'}) or die $dbh->errstr;
					my $col_num=0;
					$sth_sel->bind_col(++$col_num, \$seg_name, undef);
					$sth_sel->bind_col(++$col_num, \$seg_color, undef);
					$sth_sel->bind_col(++$col_num, \$seg_thum_bgcolor, undef);
					$sth_sel->bind_col(++$col_num, \$seg_thum_bocolor, undef);
					$sth_sel->bind_col(++$col_num, \$seg_thum_fgcolor, undef);
					$sth_sel->bind_col(++$col_num, \$cdi_ids, undef);
					$sth_sel->bind_col(++$col_num, \$seg_delcause, undef);
					$sth_sel->fetch;
					$sth_sel->finish;

					$seg_use = defined $seg_delcause ? JSON::XS::false : JSON::XS::true;
					print LOG '$seg_use=['.$seg_use."]\n";

					next if(
						$seg_name         eq $data->{'seg_name'} &&
						$seg_color        eq $data->{'seg_color'} &&
						$seg_thum_bgcolor eq $data->{'seg_thum_bgcolor'} &&
						$seg_thum_fgcolor eq $data->{'seg_thum_fgcolor'} &&
						defined $cdi_ids && $data->{'cdi_ids'} && $cdi_ids eq $data->{'cdi_ids'} &&
						$seg_use          == $data->{'seg_use'}
					);

					$seg_delcause = undef;
					$seg_delcause = 'no use' if($data->{'seg_use'} == JSON::XS::false);
					print LOG '$seg_delcause=['.$seg_delcause."]\n";

					my $sth_upd;
					if(
						$seg_color        eq $data->{'seg_color'} &&
						$seg_thum_bgcolor eq $data->{'seg_thum_bgcolor'} &&
						$seg_thum_fgcolor eq $data->{'seg_thum_fgcolor'} &&
						defined $cdi_ids && $data->{'cdi_ids'} && $cdi_ids eq $data->{'cdi_ids'} &&
						$seg_use          == $data->{'seg_use'}
					){
						$sth_upd = $sth_upd2;
					}else{
						$sth_upd = $sth_upd1;
						push(@update_seg_ids,$data->{'seg_id'});
					}

					$cdi_ids = undef;
					if(defined $data->{'cdi_names'} && length $data->{'cdi_names'}){
						$cdi_ids = [split(/[^A-Za-z0-9]+/,$data->{'cdi_names'})];
						if(defined $cdi_ids && ref $cdi_ids eq 'ARRAY' && scalar @$cdi_ids){
							foreach my $cdi_id (@$cdi_ids){
								$sth_cdi->execute($cdi_id) or die $dbh->errstr;
								my $column_number = 0;
								$sth_cdi->bind_col(++$column_number, \$cdi_id, undef);
								$sth_cdi->fetch;
								$sth_cdi->finish;
							}
							$cdi_ids = [sort {$a <=> $b} grep {defined $_} @$cdi_ids];
							if(scalar @$cdi_ids){
								$cdi_ids = &cgi_lib::common::encodeJSON($cdi_ids);
							}else{
								$cdi_ids = undef;
							}
						}
					}

					my $param_num=0;
					$sth_upd->bind_param(++$param_num, $data->{'seg_name'}, undef);
					$sth_upd->bind_param(++$param_num, $data->{'seg_color'}, undef);
					$sth_upd->bind_param(++$param_num, $data->{'seg_thum_bgcolor'}, undef);
					$sth_upd->bind_param(++$param_num, $data->{'seg_thum_bocolor'}, undef);
					$sth_upd->bind_param(++$param_num, $data->{'seg_thum_fgcolor'}, undef);
					$sth_upd->bind_param(++$param_num, $cdi_ids, undef);
					$sth_upd->bind_param(++$param_num, $seg_delcause, undef);
					$sth_upd->bind_param(++$param_num, $data->{'seg_id'}, undef);
					$sth_upd->execute() or die $dbh->errstr;
					$DATASET->{'total'} += $sth_upd->rows();
					$sth_upd->finish;
				}
				undef $sth_sel;
				undef $sth_upd1;
				undef $sth_upd2;
				$dbh->commit();

				$DATASET->{'success'} = JSON::XS::true;

				print LOG '@update_seg_ids=['.(scalar @update_seg_ids)."]\n";

				if(scalar @update_seg_ids){
					my $cmd = qq|find /bp3d/cache_fma/*/common -name "*.json" -exec rm -fr {} \\; 2> /dev/null|;
					system($cmd);

=pod
					my @cdi_names;
					my $sth_sel = $dbh->prepare(qq|select distinct cdi_name from view_concept_data where cd_delcause is null and seg_id=?|) or die $dbh->errstr;
					foreach my $seg_id (@update_seg_ids){
						$sth_sel->execute($seg_id) or die $dbh->errstr;
						my $cdi_name;
						my $col_num=0;
						$sth_sel->bind_col(++$col_num, \$cdi_name, undef);
						while($sth_sel->fetch){
							push(@cdi_names,$cdi_name);
						}
						$sth_sel->finish;
					}
					undef $sth_sel;
					if(scalar @cdi_names){
=cut

#					$cmd = qq|find /bp3d/cache_fma/*/common -type d -empty -exec rm -fr {} \\; 2> /dev/null|;
#					system($cmd);
				}

			};
			if($@){
				$DATASET->{'msg'} = $@;
				print LOG __LINE__,":",$@,"\n";
				$dbh->rollback;
				$DATASET->{'success'} = JSON::XS::false;
			}
			$dbh->{'AutoCommit'} = 1;
			$dbh->{'RaiseError'} = 0;
		}
		elsif($FORM{'cmd'} eq 'destroy'){
			$dbh->{'AutoCommit'} = 0;
			$dbh->{'RaiseError'} = 1;
			eval{
				my $sth = $dbh->prepare('delete from concept_segment where seg_id=?') or die $dbh->errstr;;
				foreach my $data (@$datas){
					next unless(exists $data->{'seg_id'} && defined $data->{'seg_id'});
					$sth->execute($data->{'seg_id'}) or die $dbh->errstr;
					$sth->finish;
				}
				undef $sth;
				$DATASET->{'success'} = JSON::XS::true;
			};
			if($@){
				$DATASET->{'msg'} = $@;
				print LOG __LINE__,":",$@,"\n";
				$dbh->rollback;
				$DATASET->{'success'} = JSON::XS::false;
			}
			$dbh->{'AutoCommit'} = 1;
			$dbh->{'RaiseError'} = 0;
		}
	}
}
elsif($FORM{'cmd'} eq 'update_concept'){

	$dbh->{'AutoCommit'} = 0;
	$dbh->{'RaiseError'} = 1;
	eval{

		my $sql_seg = qq|select seg_id from concept_segment where seg_id=?|;
		my $sth_seg = $dbh->prepare($sql_seg) or die $dbh->errstr;;
		my $seg_id = $FORM{'seg_id'};
		$sth_seg->execute($seg_id);
		my $seg_rows = $sth_seg->rows();
		$sth_seg->finish;
		undef $sth_seg;

		my $md_id = $FORM{'md_id'};
		my $mv_id = $FORM{'mv_id'};
		my $mr_id = $FORM{'mr_id'};
		my $ci_id = $FORM{'ci_id'};
		my $cb_id = $FORM{'cb_id'};
		my $cdi_name = $FORM{'cdi_name'};

		my $sql_but = qq|select cdi_id,cti_cids from concept_tree_info where ci_id=? and cb_id=? and cdi_name=?|;
		my $sth_but = $dbh->prepare($sql_but) or die $dbh->errstr;
		$sth_but->execute($ci_id,$cb_id,$cdi_name);
		my $but_rows = $sth_but->rows();

		my $ART_IDS;
		my $cd_rows = 0;
		if($seg_rows>0 && $but_rows>0){
			my $sql_cm_fmt = qq|select art_id from concept_art_map where cm_use and cm_delcause is null and ci_id=? and cb_id=? and cdi_id in (%s)|;

			my $sql_cd_fmt = qq|update concept_data set seg_id=?,cd_entry=now() where ci_id=? and cb_id=? and cdi_id in (%s) and seg_id<>?|;


			my $cdi_id;
			my $but_cids;
			$sth_but->bind_col(1, \$cdi_id, undef);
			$sth_but->bind_col(2, \$but_cids, undef);
			while($sth_but->fetch){
				next unless(defined $cdi_id);
				undef $but_cids unless(defined $FORM{'set_segment_recursively'});
				$but_cids = &JSON::XS::decode_json($but_cids) if(defined $but_cids);
				push(@$but_cids,$cdi_id);

				my $sth_cd = $dbh->prepare(sprintf($sql_cd_fmt,join(",",@$but_cids))) or die $dbh->errstr;;
				$sth_cd->execute($seg_id,$ci_id,$cb_id,$seg_id);
				my $rows = $sth_cd->rows();
				$sth_cd->finish;
				undef $sth_cd;

				if($rows>0){
					$cd_rows += $rows;

					my $art_id;
					my $sth_cm = $dbh->prepare(sprintf($sql_cm_fmt,join(",",@$but_cids))) or die $dbh->errstr;;
					$sth_cm->execute($ci_id,$cb_id);
					my $rows = $sth_cm->rows();
					$sth_cm->bind_col(1, \$art_id, undef);
					while($sth_cm->fetch){
						$ART_IDS->{$art_id} = undef;
					}
					$sth_cm->finish;
					undef $sth_cm;
				}

			}

		}
		$sth_but->finish;
		undef $sth_but;

		$dbh->commit();
		$DATASET->{'success'} = JSON::XS::true;

		if($cd_rows){
			my $cmd = qq|find /bp3d/cache_fma/*/common -name "*.json" -exec rm -fr {} \\; 2> /dev/null|;
			system($cmd);
		}
		if(defined $ART_IDS){
			my @IDS = map { { art_id => $_ } } sort keys(%$ART_IDS);
			&make_art_images(\@IDS);
		}
	};
	if($@){
		$DATASET->{'msg'} = $@;
		print LOG __LINE__,":",$@,"\n";
		$dbh->rollback;
		$DATASET->{'success'} = JSON::XS::false;
	}
	$dbh->{'AutoCommit'} = 1;
	$dbh->{'RaiseError'} = 0;



}

&gzip_json($DATASET);
exit;


sub make_art_images {
	my $LIST = shift;
	my $sessionID;

	return unless(defined $LIST && ref $LIST eq 'ARRAY' && scalar @$LIST > 0);

	my $prog_basename = qq|make_art_image|;
	my $prog = &catfile($FindBin::Bin,'..','cron',qq|$prog_basename.pl|);
	return unless(-e $prog && -X $prog);

	my $sessionID = &Digest::MD5::md5_hex(&Time::HiRes::time());
	my $out_path = &catdir($FindBin::Bin,'temp');
	my $params_file = &catfile($out_path,qq|$sessionID.json|);
	open(OUT,"> $params_file") or die $!;
	flock(OUT,2);
	print OUT &JSON::XS::encode_json($LIST);
	close(OUT);
	chmod 0666,$params_file;

	my $pid = fork;
	if(defined $pid){
		if($pid == 0){
			my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
			$year = sprintf("%04d",$year+1900);
			$mon  = sprintf("%02d",$mon+1);
			$mday = sprintf("%02d",$mday);
			my $d = &catdir($FindBin::Bin,'logs',$year,$mon,$mday);
			&File::Path::make_path($d) unless(-e $d);
			my $f1 = &catfile($d,qq|$prog_basename.log|);
			my $f2 = &catfile($d,qq|$prog_basename.err|);
			close(STDOUT);
			close(STDERR);
			open STDOUT, ">> $f1" || die "[$f1] $!\n";
			open STDERR, ">> $f2" || die "[$f2] $!\n";
			close(STDIN);
			exec(qq|nice -n 19 $prog $params_file|);
			exit(1);
		}
	}else{
		die("Can't execute program");
	}
}

sub make_cm_images {
	my $prog_basename = qq|make_cm_image|;
	my $prog = &catfile($FindBin::Bin,'..','cron',qq|$prog_basename.pl|);
	return unless (-e $prog && -X $prog);

	my $pid = fork;
	if(defined $pid){
		if($pid == 0){
			my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
			$year = sprintf("%04d",$year+1900);
			$mon  = sprintf("%02d",$mon+1);
			$mday = sprintf("%02d",$mday);
			my $d = &catdir($FindBin::Bin,'logs',$year,$mon,$mday);
			&File::Path::make_path($d) unless(-e $d);
			my $f1 = &catfile($d,qq|$prog_basename.log|);
			my $f2 = &catfile($d,qq|$prog_basename.err|);
			close(STDOUT);
			close(STDERR);
			open STDOUT, ">> $f1" || die "[$f1] $!\n";
			open STDERR, ">> $f2" || die "[$f2] $!\n";
			close(STDIN);
			exec(qq|nice -n 19 $prog|);
			exit(1);
		}
	}else{
		die("Can't execute program");
	}
}
