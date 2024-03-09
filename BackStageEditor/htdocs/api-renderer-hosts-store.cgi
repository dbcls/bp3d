#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;

use JSON::XS;
use DBD::Pg;
use File::Copy;
use File::Spec;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
require "webgl_common.pl";
use make_httpd_conf;

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

&setDefParams(\%FORM,\%COOKIE);
foreach my $key (sort keys(%FORM)){
	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
}

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
foreach my $key (sort keys(%FORM)){
	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
}
#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $where;
my @bind_values = ();
if(exists $FORM{filter}){
	my $filter;
	eval{$filter=&JSON::XS::decode_json($FORM{filter});};
	if(defined $filter){
		my @W;
		foreach my $f (@$filter){
			push(@W,qq|$f->{property}=?|);
			push(@bind_values,$f->{value});
		}
		$where = qq|where |.join(" and ",@W) if(scalar @W > 0);
	}
}
#29:$FORM{filter}=[[{"property":"md_id","value":1}]]

$FORM{'cmd'} = 'read' unless(exists $FORM{'cmd'} && defined $FORM{'cmd'});

my $HOSTS = {
	datas => [],
	total => 0,
	success => JSON::XS::false
};

if($FORM{'cmd'} eq 'read'){
	eval{
		my $sql=<<SQL;
select
 rh_id,
 rh_ip,
 rh_use,
 rh_comment,
 EXTRACT(EPOCH FROM rh_entry)
from
 renderer_hosts
where
 rh_delcause is null
order by
 rh_ip
SQL

		print LOG __LINE__,":\$sql=[",$sql,"]\n";
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		if(scalar @bind_values > 0){
			$sth->execute(@bind_values) or die $dbh->errstr;
		}else{
			$sth->execute() or die $dbh->errstr;
		}

		my($rh_id,$rh_ip,$rh_use,$rh_comment,$rh_entry);

		my $column_number = 0;
		$sth->bind_col(++$column_number, \$rh_id, undef);
		$sth->bind_col(++$column_number, \$rh_ip, undef);
		$sth->bind_col(++$column_number, \$rh_use, undef);
		$sth->bind_col(++$column_number, \$rh_comment, undef);
		$sth->bind_col(++$column_number, \$rh_entry, undef);

		while($sth->fetch){
			my $HASH = {
				rh_id => $rh_id,
				rh_ip => $rh_ip,
				rh_use => $rh_use ? JSON::XS::true : JSON::XS::false,
				rh_comment => $rh_comment,
				rh_entry => $rh_entry,
			};
			push(@{$HOSTS->{'datas'}},$HASH);
		}
		$sth->finish;
		undef $sth;

		$HOSTS->{'total'} = scalar @{$HOSTS->{'datas'}};
		$HOSTS->{'success'} = JSON::XS::true;
	};
	if($@){
		$HOSTS->{'msg'} = $@;
		print LOG __LINE__,":",$@,"\n";
	}

}elsif(exists $FORM{'datas'} && defined $FORM{'datas'}){
	my $datas;
	eval{$datas = &JSON::XS::decode_json($FORM{'datas'});};
	if(defined $datas && ref $datas eq 'ARRAY'){
		if($FORM{'cmd'} eq 'create'){

#$dbh->do(qq|ALTER TABLE concept_art_map DISABLE TRIGGER USER;|) or die $dbh->errstr;
#$dbh->do(qq|ALTER TABLE history_concept_art_map DISABLE TRIGGER USER;|) or die $dbh->errstr;

			$dbh->{'AutoCommit'} = 0;
			$dbh->{'RaiseError'} = 1;
			eval{
				my $sth_ins = $dbh->prepare(qq|insert into renderer_hosts (rh_ip,rh_use,rh_comment,rh_entry,rh_openid) values (?,?,?,now(),'system')|) or die $dbh->errstr;
				foreach my $data (@$datas){
					$data->{'rh_ip'} = undef if(exists $data->{'rh_ip'} && defined $data->{'rh_ip'} && length($data->{'rh_ip'})==0);
					$data->{'rh_comment'} = undef if(exists $data->{'rh_comment'} && defined $data->{'rh_comment'} && length($data->{'rh_comment'})==0);
					$sth_ins->execute($data->{'rh_ip'},$data->{'rh_use'},$data->{'rh_comment'}) or die $dbh->errstr;
					$sth_ins->finish;
				}
				undef $sth_ins;
				$dbh->commit();
				$HOSTS->{'success'} = JSON::XS::true;
			};
			if($@){
				$HOSTS->{'msg'} = $@;
				print LOG __LINE__,":",$@,"\n";
				$dbh->rollback;
			}
			$dbh->{'AutoCommit'} = 1;
			$dbh->{'RaiseError'} = 0;

#$dbh->do(qq|ALTER TABLE concept_art_map ENABLE TRIGGER USER;|) or die $dbh->errstr;
#$dbh->do(qq|ALTER TABLE history_concept_art_map ENABLE TRIGGER USER;|) or die $dbh->errstr;

		}
		elsif($FORM{'cmd'} eq 'update'){
			$dbh->{'AutoCommit'} = 0;
			$dbh->{'RaiseError'} = 1;
			eval{
				my $sth = $dbh->prepare(qq|update renderer_hosts set rh_ip=?,rh_use=?,rh_comment=?,rh_entry=now() where rh_id=?|) or die $dbh->errstr;
				foreach my $data (@$datas){
					my $rows = $sth->execute($data->{'rh_ip'},$data->{'rh_use'},$data->{'rh_comment'},$data->{'rh_id'}) or die $dbh->errstr;
					$HOSTS->{total} += $rows if($rows>0);
					$sth->finish;
				}
				undef $sth;
				$dbh->commit();

				$HOSTS->{'success'} = JSON::XS::true;
			};
			if($@){
				$HOSTS->{'msg'} = $@;
				print LOG __LINE__,":",$@,"\n";
				$dbh->rollback;
			}
			$dbh->{'AutoCommit'} = 1;
			$dbh->{'RaiseError'} = 0;

		}
		elsif($FORM{'cmd'} eq 'destroy'){
			$dbh->{'AutoCommit'} = 0;
			$dbh->{'RaiseError'} = 1;
			eval{
				my $sth = $dbh->prepare(qq|delete from renderer_hosts where rh_id=?|) or die $dbh->errstr;
				foreach my $data (@$datas){
					my $rows = $sth->execute($data->{'rh_id'}) or die $dbh->errstr;
					$HOSTS->{total} += $rows if($rows>0);
					$sth->finish;
				}
				undef $sth;
				$dbh->commit();

				$HOSTS->{'success'} = JSON::XS::true;
			};
			if($@){
				$HOSTS->{'msg'} = $@;
				print LOG __LINE__,":",$@,"\n";
				$dbh->rollback;
			}
			$dbh->{'AutoCommit'} = 1;
			$dbh->{'RaiseError'} = 0;
		}
		if($HOSTS->{'success'} == JSON::XS::true){
			&make_httpd_conf::make_renderer_conf($dbh);
		}
	}
}

#my $json = &JSON::XS::encode_json($HOSTS);
#print $json;
&gzip_json($HOSTS);
