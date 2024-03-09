#!/bp3d/local/perl/bin/perl

use strict;
use warnings;
use utf8;

use OAuth::Lite::Consumer;
use Encode;
use CGI;
use CGI::Carp qw/fatalsToBrowser/;
use URI;
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

*OAuth::Lite::Util::encode_param = sub {
	my $param = shift;
	URI::Escape::uri_escape_utf8($param, '^\w.~-');
};

my $consumer = OAuth::Lite::Consumer->new(
	consumer_key       => 'dTgqJPVGCiDI6gR7wy1jsg',
	consumer_secret    => 'AnjqUJdRX2cLZqVQSsRMqrG2jpEEXSe5R6A41Tu9zo',
	site               => 'http://twitter.com/',
	request_token_path => 'https://api.twitter.com/oauth/request_token',
	access_token_path  => 'https://api.twitter.com/oauth/access_token',
	authorize_path     => 'https://api.twitter.com/oauth/authorize',
);

my $param_oauth_token    = $q->param('oauth_token');
my $param_oauth_verifier = $q->param('oauth_verifier');

my $access_token = $consumer->get_access_token(
	token    => $param_oauth_token,
	verifier => $param_oauth_verifier,
);

my $res = $consumer->request(
	method => 'POST',
	url    => q{http://twitter.com/statuses/update.xml},
	token  => $access_token,
	params => {
		status => scalar localtime,
		token => $access_token,
	},
);

if ($res->is_success) {
	use XML::Simple;
	my $status = XMLin($res->decoded_content);
	print $q->redirect(
        "http://twitter.com/"
        . $status->{user}->{screen_name}
        . '/status/'
        . $status->{id}
	);
}
else {
	print $q->redirect('http://twitter.com');
}

exit;
