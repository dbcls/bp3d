#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

#use Proc::ProcessTable;
#use Sys::Statistics::Linux;
#use JSON::XS;
#use Time::HiRes;

use FindBin;
use lib $FindBin::Bin,'/bp3d/ag-test/htdocs','/bp3d/ag-test/lib','/bp3d/ag-common/lib';

require "common.pl";
require "common_db.pl";
#use cgi_lib::common;
my $dbh = &get_dbh();

#$dbh->do("LISTEN model_version");

#my $JSONXS = JSON::XS->new->utf8->indent(0)->canonical(1);
#my $JSONXS = JSON::XS->new->utf8->indent(1)->canonical(1)->relaxed(1);


print "Content-Type: text/event-stream;\n\n";
print "event: start\n";
print "data: $$\n\n";
eval{
	$dbh->do("LISTEN model_version");
	$dbh->do("LISTEN art_folder");
	$dbh->do("LISTEN art_group");
	$dbh->do("LISTEN art_file");
	$dbh->do("LISTEN concept_art_map");
	LISTENLOOP: {
		my $p = 0;
		while (my $notify = $dbh->pg_notifies) {
			my ($name, $pid, $payload) = @$notify;
			print qq{event: $name\n};
			print qq{data: $pid\n};
			$p = 1;
		}
		print "\n";
		unless($p){
			$dbh->ping() or die qq{Ping failed!};
			print "\n";
			sleep(1);
		}
		redo;
	}
};
if($@){
	print "data: $@\n\n";
}
