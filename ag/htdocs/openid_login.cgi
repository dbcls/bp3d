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
#my $claimed_url = qq|http://openid.dbcls.jp/user/tyamamot|;
my $claimed_url = qq|https://me.yahoo.co.jp/a/DBAVt7JDYJDfEqdLLwxtmi4zfNCSXf.d|;

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

# Say a user enters "bradfitz.com" as his/her identity.  The first
# step is to perform discovery, i.e., fetch that page, parse it,
# find out the actual identity provider and other useful information,
# which gets encapsulated in a Net::OpenID::ClaimedIdentity object:

my $claimed_identity = $csr->claimed_identity($claimed_url);
unless ($claimed_identity) {
	die "not actually an openid?  " . $csr->err;
}

# We can then launch the actual authentication of this identity.
# The first step is to redirect the user to the appropriate URL at
# the identity provider.  This URL is constructed as follows:
#
my $check_url = $claimed_identity->check_url(
	return_to  => $required_root.qq|openid_return.cgi|,
	trust_root => $required_root,

  # to do a "checkid_setup mode" request, in which the user can
  # interact with the provider, e.g., so that the user can sign in
  # there if s/he has not done so already, you will need this,
	delayed_return => 1

  # otherwise, this will be a "check_immediate mode" request, the
  # provider will have to immediately return some kind of answer
  # without interaction
);
print $cgi->redirect($check_url);
