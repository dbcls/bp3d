#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use Data::Dumper;
$Data::Dumper::Indent = 1;
$Data::Dumper::Sortkeys = 1;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
use BITS::ReCalc;
require "webgl_common.pl";
use cgi_lib::common;

$SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit";
sub sigexit {
	my($date) = `date`;
	$date =~ s/\s*$//g;
	print STDERR "[$date] KILL THIS CGI!![$ENV{SCRIPT_NAME}]\n";
	exit(1);
}

#my $disEnv = &getDispEnv();
#my $dispTreeChildPartsNum = $disEnv->{dispTreeChildPartsNum};
my $dispTreeChildPartsNum = 'false';# unless(defined $dispTreeChildPartsNum);

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);
my($logfile,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

$FORM{'cmd'} = 'read' unless(defined $FORM{'cmd'});
$logfile .= '.'.$FORM{'cmd'};

#my @extlist = qw|.cgi .pl|;
#my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);
#my $logfile = qq|$FindBin::Bin/logs/$FORM{'cdi_name'}.$cgi_name.txt|;
#$logfile .= '.'.$FORM{'cdi_name'} if(exists $FORM{'cdi_name'} && defined $FORM{'cdi_name'});

=pod
$FORM{ag_data}=qq|obj/bp3d/4.0|;
$FORM{'cdi_name'}=qq|root|;
$FORM{model}=qq|bp3d|;
$FORM{'node'}=qq|root|;
$FORM{tree}=qq|isa|;
$FORM{version}=qq|4.0|;
=cut

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
#$logfile .= '.'.sprintf("%04d%02d%02d%02d",$year+1900,$mon+1,$mday,$hour);
$logfile .=  sprintf(".%02d%02d%02d.%05d",$hour,$min,$sec,$$);

my $LOG;
open($LOG,">> $logfile");
flock($LOG,2);
print $LOG "\n[$logtime]:$0\n";
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);


&setDefParams(\%FORM,\%COOKIE);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%FORM, 1), $LOG);

my $TREE = [];
#$TREE = {};
#$TREE->{'datas'} = [];
#$TREE->{'success'} = JSON::XS::false;
#$TREE->{'msg'} = undef;

#unless(defined $FORM{'version'}){
#	print qq|Content-type: text/html; charset=UTF-8\n\n|;
#	exit;
#}

#my $lsdb_OpenID;
#my $lsdb_Auth;
#my $parentURL = $FORM{'parent'} if(exists($FORM{'parent'}));
#my $parent_text;
#if(defined $parentURL){
#	($lsdb_OpenID,$lsdb_Auth) = &openidAuth($parentURL);
#}



$FORM{'cmd'} = 'read' unless(defined $FORM{'cmd'});

my $sql;

if($FORM{'cmd'} eq 'read'){
	$sql=<<SQL;
select
  artf.artf_id,
  artf.artf_pid,
  artf_name,
  artf_use,
  artf_comment,
  artf_delcause,
  EXTRACT(EPOCH FROM artf_timestamp) as artf_timestamp,
  EXTRACT(EPOCH FROM artf_entry) as artf_entry,
  child_count
--  ,artg_count
from 
  art_folder as artf

left join (
  select
   artf_pid,
   count(artf_pid) as child_count
  from
   art_folder
  group by
   artf_pid
) as c on (c.artf_pid=artf.artf_id)

--left join (
--  select
--   artf_id,
--   count(artf_id) as artg_count
--  from
--   art_group
--  group by
--   artf_id
--) as g on (g.artf_id=artf.artf_id)

where
  artf_delcause is null
SQL

	$FORM{'node'} = $FORM{'artf_pid'} if(!defined $FORM{'node'} && exists $FORM{'artf_pid'} && defined $FORM{'artf_pid'});
	unless(exists($FORM{'node'})){
#		my $json = &JSON::XS::encode_json(\@TREE);
#		print $json;
		&gzip_json($TREE);
#		print LOG __LINE__,":",$json,"\n";
		close($LOG);
		exit;
	}elsif($FORM{'node'} eq 'root'){
		$sql .= qq|and artf.artf_pid is null|;
	}elsif(exists($FORM{'artf_pid'})){
		$sql .= qq|and artf.artf_pid=?|;
	}
#$sql .= qq| order by tree.t_order|;
#$sql .= qq| order by tree.t_cnum desc|;
#	$sql .= qq| order by bu_cnum desc,f.cdi_name_e|;
	$sql .= qq| order by artf_name|;

	print $LOG __LINE__,":sql=[$sql]\n";
	eval{
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;

		my $expanded = JSON::XS::false;

		if($FORM{'node'} eq 'root'){
			$sth->execute() or die $dbh->errstr;
	#		$expanded = JSON::XS::true;
		}elsif(exists($FORM{'artf_pid'})){
			$sth->execute($FORM{'artf_pid'}) or die $dbh->errstr;
		}else{
			$sth->execute() or die $dbh->errstr;
		}
		print $LOG __LINE__,":rows=[",$sth->rows(),"]\n";

		my $artf_id;
		my $artf_pid;
		my $artf_name;
		my $artf_use;
		my $artf_comment;
		my $artf_delcause;
		my $artf_timestamp;
		my $artf_entry;
		my $child_count;
#		my $artg_count;

		my $column_number = 0;
		$sth->bind_col(++$column_number, \$artf_id,   undef);
		$sth->bind_col(++$column_number, \$artf_pid,    undef);
		$sth->bind_col(++$column_number, \$artf_name,   undef);
		$sth->bind_col(++$column_number, \$artf_use,   undef);
		$sth->bind_col(++$column_number, \$artf_comment, undef);
		$sth->bind_col(++$column_number, \$artf_delcause,     undef);
		$sth->bind_col(++$column_number, \$artf_timestamp,   undef);
		$sth->bind_col(++$column_number, \$artf_entry,    undef);
		$sth->bind_col(++$column_number, \$child_count,    undef);
#		$sth->bind_col(++$column_number, \$artg_count,    undef);

		while($sth->fetch){

			my $HASH = {
				text    => $artf_name,
				leaf    => JSON::XS::false,#$child_count ? JSON::XS::false : JSON::XS::true,
				iconCls => 'tfolder',

				artf_id => $artf_id,
				artf_pid => $artf_pid,
				artf_name => $artf_name,
				artf_use => $artf_use ? JSON::XS::true : JSON::XS::false,
				artf_comment => $artf_comment,
				artf_delcause => $artf_delcause,

				artf_timestamp => defined $artf_timestamp ? $artf_timestamp+0 : undef,
				artf_entry => defined $artf_entry ? $artf_entry+0 : undef,

#				artg_count => defined $artg_count ? $artg_count+0 : undef,
			};

			push(@$TREE,$HASH);
	#		undef $text;
		}
		$sth->finish;
		undef $sth;
	};
	if($@){
		print $LOG __LINE__,":",$@,"\n";
		$TREE = {};
		$TREE->{'success'} = JSON::XS::false;
		$TREE->{'msg'} = $@;
	}
}
if($FORM{'cmd'} eq 'read_artg_count'){
	$TREE = {};
	$sql=<<SQL;
select
 count(artg_id) as artg_count
from
 art_group
where
 atrg_use and
 artg_delcause is null
SQL
	if(exists($FORM{'artf_id'})){
		$FORM{'artf_id'} = undef unless($FORM{'artf_id'});
		if(defined $FORM{'artf_id'}){
			$sql .= qq|and artf_id=?|;
		}else{
			$sql .= qq|and artf_id is null|;
		}
	}else{
		$sql .= qq|and artf_id is null|;
	}
	eval{
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		if(exists($FORM{'artf_id'})){
			if(defined $FORM{'artf_id'}){
				$sth->execute($FORM{'artf_id'}) or die $dbh->errstr;
			}else{
				$sth->execute() or die $dbh->errstr;
			}
		}else{
			$sth->execute() or die $dbh->errstr;
		}
		my $artg_count;
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$artg_count,   undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;

		if(defined $artg_count){
			$TREE->{'success'} = JSON::XS::true;
			$TREE->{'artg_count'} = $artg_count - 0;
		}
	};
	if($@){
		print $LOG __LINE__,":",$@,"\n";
		$TREE = {};
		$TREE->{'success'} = JSON::XS::false;
		$TREE->{'msg'} = $@;
	}

}
elsif($FORM{'cmd'} eq 'create'){
	$TREE = {};
	$TREE->{'success'} = JSON::XS::false;
	my $datas;
	if(exists $FORM{'datas'} && defined $FORM{'datas'}){
		eval{ $datas = &JSON::XS::decode_json($FORM{'datas'}); };
	}
	if(defined $datas && ref $datas eq 'ARRAY'){
		$dbh->{AutoCommit} = 0;
		$dbh->{RaiseError} = 1;
		eval{
			my $sth_sel      = $dbh->prepare(qq|select artf_id from art_folder where artf_pid=?       and artf_name=?|) or die $dbh->errstr;
			my $sth_sel_null = $dbh->prepare(qq|select artf_id from art_folder where artf_pid is null and artf_name=?|) or die $dbh->errstr;
			my $sth_sel_delcause = $dbh->prepare(qq|select artf_id from art_folder where artf_delcause is not null order by artf_id limit 1|) or die $dbh->errstr;

			my $sth_upd = $dbh->prepare(qq|update art_folder set artf_use=true,artf_delcause=null,artf_timestamp=now(),artf_pid=?,artf_name=? where artf_id=? RETURNING artf_id,artf_pid,artf_name,artf_use,artf_comment,artf_delcause,EXTRACT(EPOCH FROM artf_timestamp),EXTRACT(EPOCH FROM artf_entry)|) or die $dbh->errstr;
			my $sth_ins = $dbh->prepare(qq|insert into art_folder (artf_pid,artf_name,artf_timestamp,artf_entry,artf_use) values (?,?,now(),now(),true) RETURNING artf_id,artf_pid,artf_name,artf_use,artf_comment,artf_delcause,EXTRACT(EPOCH FROM artf_timestamp),EXTRACT(EPOCH FROM artf_entry)|) or die $dbh->errstr;

			foreach my $data (@$datas){
				$data->{'artf_pid'} = undef unless($data->{'artf_pid'});
				my $rows;
				my $artf_id;
				my $column_number = 0;
				$data->{'artf_pid'} = undef unless($data->{'artf_pid'});
				if(defined $data->{'artf_pid'}){
					$sth_sel->execute( $data->{'artf_pid'}, $data->{'artf_name'} ) or die $dbh->errstr;
					$rows = $sth_sel->rows();
					$sth_sel->bind_col(++$column_number, \$artf_id,   undef);
					$sth_sel->fetch;
					$sth_sel->finish;
				}else{
					$sth_sel_null->execute( $data->{'artf_name'} ) or die $dbh->errstr;
					$rows = $sth_sel_null->rows();
					$sth_sel_null->bind_col(++$column_number, \$artf_id,   undef);
					$sth_sel_null->fetch;
					$sth_sel_null->finish;
				}
				unless(defined $artf_id){
					$sth_sel_delcause->execute() or die $dbh->errstr;
					$rows = $sth_sel_delcause->rows();
					$column_number = 0;
					$sth_sel_delcause->bind_col(++$column_number, \$artf_id,   undef);
					$sth_sel_delcause->fetch;
					$sth_sel_delcause->finish;
				}
				if(defined $artf_id){
					$sth_upd->execute( $data->{'artf_pid'}, $data->{'artf_name'}, $artf_id ) or die $dbh->errstr;

					my $artf_id;
					my $artf_pid;
					my $artf_name;
					my $artf_use;
					my $artf_comment;
					my $artf_delcause;
					my $artf_timestamp;
					my $artf_entry;
					my $column_number = 0;
					$sth_upd->bind_col(++$column_number, \$artf_id,   undef);
					$sth_upd->bind_col(++$column_number, \$artf_pid,    undef);
					$sth_upd->bind_col(++$column_number, \$artf_name,   undef);
					$sth_upd->bind_col(++$column_number, \$artf_use,   undef);
					$sth_upd->bind_col(++$column_number, \$artf_comment, undef);
					$sth_upd->bind_col(++$column_number, \$artf_delcause,     undef);
					$sth_upd->bind_col(++$column_number, \$artf_timestamp,   undef);
					$sth_upd->bind_col(++$column_number, \$artf_entry,    undef);

					$sth_upd->fetch;

					my $HASH = {
						text    => $artf_name,
						leaf    => JSON::XS::false,#$child_count ? JSON::XS::false : JSON::XS::true,
						iconCls => 'tfolder',

						artf_id => $artf_id,
						artf_pid => $artf_pid,
						artf_name => $artf_name,
						artf_use => $artf_use ? JSON::XS::true : JSON::XS::false,
						artf_comment => $artf_comment,
						artf_delcause => $artf_delcause,

						artf_timestamp => defined $artf_timestamp ? $artf_timestamp+0 : undef,
						artf_entry => defined $artf_entry ? $artf_entry+0 : undef,
					};
					push(@{$TREE->{'datas'}},$HASH);

					$sth_upd->finish;
				}else{
					$sth_ins->execute( $data->{'artf_pid'}, $data->{'artf_name'} ) or die $dbh->errstr;

					my $artf_id;
					my $artf_pid;
					my $artf_name;
					my $artf_use;
					my $artf_comment;
					my $artf_delcause;
					my $artf_timestamp;
					my $artf_entry;
					my $column_number = 0;
					$sth_ins->bind_col(++$column_number, \$artf_id,   undef);
					$sth_ins->bind_col(++$column_number, \$artf_pid,    undef);
					$sth_ins->bind_col(++$column_number, \$artf_name,   undef);
					$sth_ins->bind_col(++$column_number, \$artf_use,   undef);
					$sth_ins->bind_col(++$column_number, \$artf_comment, undef);
					$sth_ins->bind_col(++$column_number, \$artf_delcause,     undef);
					$sth_ins->bind_col(++$column_number, \$artf_timestamp,   undef);
					$sth_ins->bind_col(++$column_number, \$artf_entry,    undef);

					$sth_ins->fetch;

					my $HASH = {
						text    => $artf_name,
						leaf    => JSON::XS::false,#$child_count ? JSON::XS::false : JSON::XS::true,
						iconCls => 'tfolder',

						artf_id => $artf_id,
						artf_pid => $artf_pid,
						artf_name => $artf_name,
						artf_use => $artf_use ? JSON::XS::true : JSON::XS::false,
						artf_comment => $artf_comment,
						artf_delcause => $artf_delcause,

						artf_timestamp => defined $artf_timestamp ? $artf_timestamp+0 : undef,
						artf_entry => defined $artf_entry ? $artf_entry+0 : undef,
					};
					push(@{$TREE->{'datas'}},$HASH);

					$sth_ins->finish;
				}
			}

			$dbh->commit();
			$dbh->do("NOTIFY art_folder");
			$TREE->{'success'} = JSON::XS::true;
		};
		if($@){
			print $LOG __LINE__,":",$@,"\n";
			$TREE->{'msg'} = $@;
			$dbh->rollback;
		}
		$dbh->{AutoCommit} = 1;
		$dbh->{RaiseError} = 0;
	}
}
elsif($FORM{'cmd'} eq 'update'){
	$TREE = {};
	$TREE->{'success'} = JSON::XS::false;
	my $datas;
	if(exists $FORM{'datas'} && defined $FORM{'datas'}){
		eval{ $datas = &JSON::XS::decode_json($FORM{'datas'}); };
	}
	if(defined $datas && ref $datas eq 'ARRAY'){
		$dbh->{AutoCommit} = 0;
		$dbh->{RaiseError} = 1;
		eval{
			my $sth_sel      = $dbh->prepare(qq|select artf_id from art_folder where artf_pid=?       and artf_name=? and artf_delcause is not null|) or die $dbh->errstr;
			my $sth_sel_null = $dbh->prepare(qq|select artf_id from art_folder where artf_pid is null and artf_name=? and artf_delcause is not null|) or die $dbh->errstr;
			my $sth_upd_pid  = $dbh->prepare(qq|update art_folder set artf_pid=?,artf_timestamp=now() where artf_pid=?|) or die $dbh->errstr;

			my $sth_del      = $dbh->prepare(qq|delete from art_folder where artf_pid=?       and artf_name=? and artf_delcause is not null|) or die $dbh->errstr;
			my $sth_del_null = $dbh->prepare(qq|delete from art_folder where artf_pid is null and artf_name=? and artf_delcause is not null|) or die $dbh->errstr;


			my $sth_upd = $dbh->prepare(qq|update art_folder set artf_pid=?,artf_name=?,artf_timestamp=now() where artf_id=? RETURNING artf_id,artf_pid,artf_name,artf_use,artf_comment,artf_delcause,EXTRACT(EPOCH FROM artf_timestamp),EXTRACT(EPOCH FROM artf_entry)|) or die $dbh->errstr;
			foreach my $data (@$datas){
				$data->{'artf_pid'} = undef unless($data->{'artf_pid'});
				my $artf_id;
				my $column_number = 0;
				if(defined $data->{'artf_pid'}){
					$sth_sel->execute( $data->{'artf_pid'}, $data->{'artf_name'} ) or die $dbh->errstr;
					$sth_sel->bind_col(++$column_number, \$artf_id,   undef);
					while($sth_sel->fetch){
						$sth_upd_pid->execute( $artf_id, $data->{'artf_pid'} ) or die $dbh->errstr;
						$sth_upd_pid->finish;
					}
					$sth_sel->finish;
					$sth_del->execute( $data->{'artf_pid'}, $data->{'artf_name'} ) or die $dbh->errstr;
					$sth_del->finish;
				}else{
					$sth_sel_null->execute( $data->{'artf_name'} ) or die $dbh->errstr;
					$sth_sel_null->bind_col(++$column_number, \$artf_id,   undef);
					while($sth_sel_null->fetch){
						$sth_upd_pid->execute( $artf_id, $data->{'artf_pid'} ) or die $dbh->errstr;
						$sth_upd_pid->finish;
					}
					$sth_sel_null->finish;
					$sth_del_null->execute( $data->{'artf_name'} ) or die $dbh->errstr;
					$sth_del_null->finish;
				}

				$sth_upd->execute( $data->{'artf_pid'}, $data->{'artf_name'}, $data->{'artf_id'} ) or die $dbh->errstr;

				#my $artf_id;
				my $artf_pid;
				my $artf_name;
				my $artf_use;
				my $artf_comment;
				my $artf_delcause;
				my $artf_timestamp;
				my $artf_entry;
				$column_number = 0;
				$sth_upd->bind_col(++$column_number, \$artf_id,   undef);
				$sth_upd->bind_col(++$column_number, \$artf_pid,    undef);
				$sth_upd->bind_col(++$column_number, \$artf_name,   undef);
				$sth_upd->bind_col(++$column_number, \$artf_use,   undef);
				$sth_upd->bind_col(++$column_number, \$artf_comment, undef);
				$sth_upd->bind_col(++$column_number, \$artf_delcause,     undef);
				$sth_upd->bind_col(++$column_number, \$artf_timestamp,   undef);
				$sth_upd->bind_col(++$column_number, \$artf_entry,    undef);

				$sth_upd->fetch;

				my $HASH = {
					text    => $artf_name,
					leaf    => JSON::XS::false,#$child_count ? JSON::XS::false : JSON::XS::true,
					iconCls => 'tfolder',

					artf_id => $artf_id,
					artf_pid => $artf_pid,
					artf_name => $artf_name,
					artf_use => $artf_use ? JSON::XS::true : JSON::XS::false,
					artf_comment => $artf_comment,
					artf_delcause => $artf_delcause,

					artf_timestamp => defined $artf_timestamp ? $artf_timestamp+0 : undef,
					artf_entry => defined $artf_entry ? $artf_entry+0 : undef,
				};
				push(@{$TREE->{'datas'}},$HASH);


				$sth_upd->finish;
			}

			$dbh->commit();
			$dbh->do("NOTIFY art_folder");
			$TREE->{'success'} = JSON::XS::true;
		};
		if($@){
			print $LOG __LINE__,":",$@,"\n";
			$TREE->{'msg'} = $@;
			$dbh->rollback;
		}
		$dbh->{AutoCommit} = 1;
		$dbh->{RaiseError} = 0;
	}
}
elsif($FORM{'cmd'} eq 'destroy'){
	$TREE = {};
	$TREE->{'success'} = JSON::XS::false;
	my $datas;
	if(exists $FORM{'datas'} && defined $FORM{'datas'}){
		eval{ $datas = &JSON::XS::decode_json($FORM{'datas'}); };
	}
	if(defined $datas && ref $datas eq 'ARRAY'){
		$dbh->{AutoCommit} = 0;
		$dbh->{RaiseError} = 1;
		eval{
			my $sth_upd = $dbh->prepare(qq|update art_folder set artf_delcause='DELETE',artf_use=false,artf_timestamp=now() where artf_id=?|) or die $dbh->errstr;
			my $sth_upd_group = $dbh->prepare(qq|update art_group set artf_id=null where artf_id=?|) or die $dbh->errstr;
			foreach my $data (@$datas){
				&cgi_lib::common::message(&cgi_lib::common::encodeJSON($data,1),$LOG) if(defined $LOG);
				$sth_upd_group->execute( $data->{'artf_id'} ) or die $dbh->errstr;
				$sth_upd_group->finish;

				$sth_upd->execute( $data->{'artf_id'} ) or die $dbh->errstr;
				$sth_upd->finish;
			}
			$dbh->do(qq|update art_group set artf_id=null where artf_id in (select artf_id from art_folder where artf_delcause is not null)|) or die $dbh->errstr;
			$dbh->commit();
			$dbh->do("NOTIFY art_folder");
			$TREE->{'success'} = JSON::XS::true;
		};
		if($@){
			print $LOG __LINE__,":",$@,"\n";
			$TREE->{'msg'} = $@;
			$dbh->rollback;
		}
		$dbh->{AutoCommit} = 1;
		$dbh->{RaiseError} = 0;
	}
}

#my $json = to_json(\@TREE);
#my $json = &JSON::XS::encode_json(\@TREE);
#print $json;
&gzip_json($TREE);
#print $LOG __LINE__,":",$json,"\n";

print $LOG __LINE__,":",&Data::Dumper::Dumper($TREE);

close($LOG);
exit;

=debug




=cut
