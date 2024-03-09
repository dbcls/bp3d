package make_httpd_conf;

use strict;
#use warnings;
use feature ':5.10';
use vars qw($VERSION);
$VERSION = "0.01";

use constant {
	PREFIX => 'cluster',
	SUFFIX => '.conf',
	BASENAME => 'ag-renderer-include'
};

use DBI;
use DBD::Pg;
use File::Basename;
use File::Spec;
use Cwd qw(abs_path);
use Carp;

use FindBin;
use lib $FindBin::Bin;

sub make_renderer_conf {
	my $dbh = shift;

	eval{

		my $sql=<<SQL;
select
 rh_ip
from
 renderer_hosts
where
 rh_delcause is null AND rh_use
order by
 rh_ip
SQL

		my $HOSTS;
		my $sth = $dbh->prepare($sql) or DBI->errstr();
		$sth->execute() or DBI->errstr();
		my($rh_id,$rh_ip,$rh_use,$rh_comment,$rh_entry);
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$rh_ip, undef);
		while($sth->fetch){
			push(@$HOSTS,$rh_ip) if(defined $rh_ip);
		}
		$sth->finish;
		undef $sth;

		my $sql=<<SQL;
select
 mr_version,
 mv_port,
 md_abbr
from
 model_version as mv
left join (
 select * from model where md_delcause is null
) as md on (md.md_id=mv.md_id)
left join (
 select * from model_revision where (md_id,mv_id,mr_id) in (select md_id,mv_id,max(mr_id) from model_revision where mr_delcause is null and mr_use group by md_id,mv_id)
) as mr on (
   mr.md_id=mv.md_id and
   mr.mv_id=mv.mv_id
 )
where
 mv_delcause is null AND
 mv_version is not null AND
 mv_port is not null AND
 mv_frozen
order by
 mv_port
SQL

		my $PORTS;
		my $sth = $dbh->prepare($sql) or DBI->errstr();
		$sth->execute() or DBI->errstr();
		my($mv_version,$mv_port,$md_abbr);
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$mv_version, undef);
		$sth->bind_col(++$column_number, \$mv_port, undef);
		$sth->bind_col(++$column_number, \$md_abbr, undef);
		while($sth->fetch){
			push(@$PORTS,{
				mv_version => $mv_version,
				mv_port => $mv_port,
				md_abbr => $md_abbr
			});
		}
		$sth->finish;
		undef $sth;

		if(defined $HOSTS && defined $PORTS){
			my $FILES;
			my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,qw/.cgi .pl/);
			my $conf_dir = &Cwd::abs_path(File::Spec->catdir($cgi_dir,'..','local','etc','httpd','renderer_conf'));
			unless(-e $conf_dir){
				my $old = umask(0);
				&File::Path::mkpath($conf_dir,0,0777);
				umask($old);
			}
			foreach my $port (@$PORTS){
				my $filename = $port->{'mv_version'};
				$filename =~ s/\.//g;
				$filename = PREFIX.$filename;

				my $path = File::Spec->catfile($conf_dir,$filename.SUFFIX);
				my $OUT;
				open($OUT,qq|> $path|) or die $!;
				flock($OUT,2);
				print $OUT <<CONF;
ProxyPassMatch ^/$port->{'md_abbr'}/$port->{'mv_version'}/(.*)\$ balancer://$filename/renderer/\$1
<Proxy balancer://$filename>
  ProxySet lbmethod=byrequests maxattempts=1 nofailover=Off timeout=300
CONF
				foreach my $host (@$HOSTS){
					print $OUT <<CONF
  BalancerMember http://$host:$port->{'mv_port'} connectiontimeout=1 retry=5 timeout=300 ttl=5
CONF
				}
				print $OUT <<CONF;
</Proxy>
CONF
				close($OUT);
				push(@$FILES,$path);
			}

			if(defined $FILES){
				my $path = File::Spec->catfile($conf_dir,BASENAME.SUFFIX);
				my $OUT;
				open($OUT,qq|> $path|) or die $!;
				flock($OUT,2);
=pod
				print $OUT <<CONF;
ProxyRequests Off
ProxyVia Off

<Location /balancer-manager>
  SetHandler balancer-manager
  Order Allow,Deny
  Allow from All
</Location>
<Proxy *>
  Order deny,allow
  Deny from all
  allow from localhost 127.0.0.1
#  allow from localhost 127.0.0.1 172.19.1
</Proxy>
<Proxy http://lifesciencedb.jp:32888/bp3d-38321/API/*>
  Order deny,allow
  Deny from all
  allow from localhost 127.0.0.1 172.19.1
</Proxy>
<Proxy http://lifesciencedb.jp/bp3d/API/*>
  Order deny,allow
  Deny from all
  allow from localhost 127.0.0.1 172.19.1
</Proxy>
CONF
=cut
				foreach my $file (@$FILES){
					print $OUT qq|Include $file\n|;
				}
				close($OUT);
			}
		}
	};
	if($@){
		&Carp::croak($@);
	}
}

1;
