#!/bp3d/local/perl/bin/perl

use strict;
use warnings;
use utf8;

use OAuth::Lite::Consumer;
use URI;
use CGI;
use CGI::Carp qw/fatalsToBrowser/;
use FindBin;
use lib qq|$FindBin::Bin/..|,qq|$FindBin::Bin/../IM|;

use File::Basename;
my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = fileparse($0,@extlist);
my $LOG;
open($LOG,">> $FindBin::Bin/$cgi_name.txt");
foreach my $key (sort keys(%ENV)){
	print $LOG __LINE__,":\$ENV{$key}=[",$ENV{$key},"]\n";
}
close($LOG);

my $q = CGI->new();

my $consumer = OAuth::Lite::Consumer->new(
	consumer_key       => 'dTgqJPVGCiDI6gR7wy1jsg',
	consumer_secret    => 'AnjqUJdRX2cLZqVQSsRMqrG2jpEEXSe5R6A41Tu9zo',
	callback_url       => 'http://221.186.138.155/bp3d-38321/Twitter/callback.cgi', 
	site               => 'http://twitter.com/',
	request_token_path => 'https://api.twitter.com/oauth/request_token',
	access_token_path  => 'https://api.twitter.com/oauth/access_token',
	authorize_path     => 'https://api.twitter.com/oauth/authorize',
);

my $request_token = $consumer->get_request_token();

my $uri = URI->new($consumer->{authorize_path});

$uri->query(
	$consumer->gen_auth_query("GET", 'http://twitter.com', $request_token)
);

print $q->redirect($uri->as_string);

exit;
