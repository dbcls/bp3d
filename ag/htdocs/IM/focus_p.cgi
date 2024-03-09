#!/bp3d/local/perl/bin/perl

$| = 1 unless(defined $ENV{MOD_PERL});

use AG::API::Focus;

sub main {
	my $json = "";;
	my $callback = "";
	if($ENV{'REQUEST_METHOD'} eq 'POST'){
		read(STDIN, $json, $ENV{'CONTENT_LENGTH'});
	}else{
		$json = $ENV{'QUERY_STRING'};
	}
	if ($json =~ /&callback=([^&]+)/) {
		$callback = $1;
	}
	$json =~ s/&callback=.+//;

	&AG::API::Focus::parse($json, $callback);
}

&main();
