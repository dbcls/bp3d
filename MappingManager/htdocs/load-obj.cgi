#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use File::Spec::Functions qw(abs2rel rel2abs catdir catfile splitdir);
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use FindBin;

use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|,'/bp3d/ag-common/lib';
use cgi_lib::common;

my $query = CGI->new;

my %FORM = ();
#my %COOKIE = ();
#&getParams($query,\%FORM,\%COOKIE);

my @params = $query->param();
foreach my $param (@params){
	if(defined $query->param($param)){
		$FORM{$param} = $query->param($param);
	}else{
		$FORM{$param} = undef;
	}
}

if(exists $FORM{'path'} && defined $FORM{'path'} && exists $FORM{'_dc'} && defined $FORM{'_dc'}){
	$FORM{'path'} =~ s/^[\/\.]+//g;
	my $path = &catfile($FindBin::Bin,$FORM{'path'});
	if(-e $path){
		print $query->redirect($FORM{'path'});
		exit;
	}else{
		my $dir = &File::Basename::dirname($path);
		unless(-e $dir && -d $dir){
			&cgi_lib::common::printNotFound();
			exit;
		}
	}
	unless(-e $path && -f $path && -s $path){
		my $art_timestamp;
		if(open(my $OBJ,"> $path")){
			if(flock($OBJ,6)){
				binmode($OBJ,':utf8');
				my($art_id,$dir,$ext) = &File::Basename::fileparse($path,qw/.obj/);
				use DBD::Pg;
				require "webgl_common.pl";
				my $dbh = &get_dbh();
				my $sth_data = $dbh->prepare(qq|select art_data,EXTRACT(EPOCH FROM art_timestamp) as art_timestamp from art_file where art_id=? order by art_serial desc NULLS FIRST limit 1|) or die $dbh->errstr;
				my $art_data;
				$sth_data->execute($art_id) or die $dbh->errstr;
				$sth_data->bind_col(1, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
				$sth_data->bind_col(2, \$art_timestamp, undef);
				$sth_data->fetch;
				$sth_data->finish;
				undef $sth_data;
				print $OBJ $art_data if(defined $art_data && defined $art_timestamp && length $art_timestamp);
				close($OBJ);
				utime $art_timestamp,$art_timestamp,$path if(defined $art_timestamp && -e $path && -f $path && -s $path);
			}else{
				close($OBJ);
			}
		}
	}

	my $max = 60;
	my $cnt = 0;
	while($cnt<$max){
		last if(-e $path && -f $path && -s $path);
		sleep(1);
		$cnt++;
	}
	if(-e $path && -f $path && -s $path){
		print $query->redirect($FORM{'path'});
	}else{
		&cgi_lib::common::printRequestTimeout();
	}
}else{
	&cgi_lib::common::printNotFound();
}
