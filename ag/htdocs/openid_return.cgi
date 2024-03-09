#!/bp3d/local/perl/bin/perl

use strict;

use Data::Dumper;
use File::Spec;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/IM|,qq|$FindBin::Bin/../../ag-common/lib|;
require "common.pl";
require "common_db.pl";

use CGI;
use LWP::UserAgent;
use Cache::File;
use Net::OpenID::Consumer;

my $cgi = CGI->new;
$cgi->charset('utf-8');

#my $required_root = qq|http://192.168.1.237/|;
my $required_root = qq|http://192.168.1.237/bp3d-38321/|;
my $claimed_url = qq|http://openid.dbcls.jp/user/tyamamot|;

my $csr = Net::OpenID::Consumer->new(
	ua    => LWP::UserAgent->new,
	cache => Cache::File->new( cache_root => '/tmp/mycache' ),
	args  => $cgi,
	consumer_secret => sub { $_[0] },
	required_root => $required_root,
	assoc_options => [
		max_encrypt => 1,
		session_no_encrypt_https => 1,
	],
);

print $cgi->header();

# Once you redirect the user to $check_url, the provider should
# eventually redirect back, at which point you need some kind of
# handler at openid-check.app to deal with that response.

# You can either use the callback-based API (recommended)...
#
$csr->handle_server_response(
    not_openid => sub {
        print __LINE__.":Not an OpenID message"."<br>\n";
    },
    setup_needed => sub {
        if ($csr->message->protocol_version >= 2) {
            # (OpenID 2) retry request in checkid_setup mode (above)
	        print __LINE__.":(OpenID 2) retry request in checkid_setup mode (above)"."<br>\n";
        }
        else {
            # (OpenID 1) redirect user to $csr->user_setup_url
	        print __LINE__.":(OpenID 1) redirect user to \$csr->user_setup_url"."<br>\n";
        }
    },
    cancelled => sub {
        # User hit cancel; restore application state prior to check_url
        print __LINE__.":User hit cancel; restore application state prior to check_url"."<br>\n";
    },
    verified => sub {
        my ($vident) = @_;
        my $verified_url = $vident->url;
        print __LINE__.":You are $verified_url !"."<br>\n";
    },
    error => sub {
        my ($errcode,$errtext) = @_;
        print __LINE__.":Error validating identity: $errcode: $errtext"."<br>\n";
    },
);

# ... or handle the various cases yourself
#
unless ($csr->is_server_response) {
    print __LINE__.":Not an OpenID message"."<br>\n";
} elsif ($csr->setup_needed) {
     # (OpenID 2) retry request in checkid_setup mode
     # (OpenID 1) redirect/link/popup user to $csr->user_setup_url
    print __LINE__.":"."<br>\n";
} elsif ($csr->user_cancel) {
     # User hit cancel; restore application state prior to check_url
} elsif (my $vident = $csr->verified_identity) {
     my $verified_url = $vident->url;
     print __LINE__.":You are $verified_url !"."<br>\n";
} else {
     print __LINE__.":Error validating identity: " . $csr->err."<br>\n";
}
