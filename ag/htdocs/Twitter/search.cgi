#!/bp3d/local/perl/bin/perl

use strict;

use Net::Twitter;
use Data::Dumper;
use HTTP::Date;

use FindBin;
use lib qq|$FindBin::Bin/..|,qq|$FindBin::Bin/../IM|;
require "common.pl";
require "common_db.pl";

use constant DEBUG => 0;

my @search_terms = qw|#bp3d #anagra|;
my $search_term = join(" OR ",@search_terms);
my $results;

unless(DEBUG){
	use File::Basename;
	my @extlist = qw|.cgi|;
	my($cgi_name,$cgi_dir,$cgi_ext) = fileparse($0,@extlist);
	my $LOG;
	open($LOG,"> $FindBin::Bin/$cgi_name.c.txt");
	foreach my $key (sort keys(%ENV)){
		print $LOG __LINE__,":\$ENV{$key}=[",$ENV{$key},"]\n";
	}

	my $consumer_key = qq|dTgqJPVGCiDI6gR7wy1jsg|;
	my $consumer_secret = qq|AnjqUJdRX2cLZqVQSsRMqrG2jpEEXSe5R6A41Tu9zo|;
	my $token = qq|1133726719-VLswXSRZTFTs2R4myV8imdFCbRSLwpsfmQxFHnA|;
	my $token_secret = qq|bL5Ev7fMha51NHF8pLEcQRHDQRNkujCPNtfno3jjjw|;

	# When no authentication is required:
	#my $nt = Net::Twitter->new(legacy => 0);

	# As of 13-Aug-2010, Twitter requires OAuth for authenticated requests
	my $nt = Net::Twitter->new(
		traits   => [qw/OAuth API::REST API::Search/],
		consumer_key        => $consumer_key,
		consumer_secret     => $consumer_secret,
		access_token        => $token,
		access_token_secret => $token_secret,
	);
	if(defined $nt){
	#	print $LOG __LINE__,":",Dumper($nt);
	}else{
		die "aaa";
	}

	my $r = $nt->search({q=>$search_term,src=>'hash'});
	if(defined $r){
		print $LOG __LINE__,":",Dumper($r);
		push(@$results,@{$r->{'results'}});
		if(exists $r->{'page'} && defined $r->{'page'} && exists $r->{'next_page'} && defined $r->{'next_page'}){
			my $page = $r->{'page'};
			my $results_per_page = $r->{'results_per_page'};
			for(my $page = $page+1;$page<=$results_per_page;$page++){
				$r = $nt->search({
					page => $page,
					max_id => $r->{'max_id'},
					q => $search_term,
					rpp => 100
				});
				push(@$results,@{$r->{'results'}});
				print $LOG __LINE__,":",Dumper($r);
			}
		}
	}
	close($LOG);
}
if(DEBUG){
	my $r = {
          'since_id_str' => '0',
          'page' => 1,
          'query' => '%23bp3d+OR+%23anagra',
          'completed_in' => '0.022',
          'refresh_url' => '?since_id=318265453178933248&q=%23bp3d%20OR%20%23anagra',
          'results_per_page' => 15,
          'max_id' => '318265453178933248',
          'max_id_str' => '318265453178933248',
          'results' => [
                         {
                           'source' => '&lt;a href=&quot;http://twitter.com/tweetbutton&quot;&gt;Tweet Button&lt;/a&gt;',
                           'geo' => undef,
                           'profile_image_url' => 'http://a0.twimg.com/profile_images/349094426/Homo_sapiens_L_normal.png',
                           'id_str' => '318265453178933248',
                           'from_user_id' => 63055388,
                           'profile_image_url_https' => 'https://si0.twimg.com/profile_images/349094426/Homo_sapiens_L_normal.png',
                           'iso_language_code' => 'ja',
                           'created_at' => 'Sun, 31 Mar 2013 07:36:11 +0000',
                           'text' => "BP2798 \x{80f8}\x{817a}\x{306e}\x{8449} http://221.186.138.155/bp3d-38321/?shorten=LrK5Pnjae05vqm0TTvHT9Tz8 #bp3d \x{548c}\x{540d}\x{304a}\x{3088}\x{3073}\x{304b}\x{306a}\x{3000}\x{304c}\x{9593}\x{9055}\x{3063}\x{3066}\x{308b}",
                           'metadata' => {
                                           'result_type' => 'recent'
                                         },
                           'from_user_name' => "\x{304a}\x{304a}\x{304f}\x{307c}",
                           'id' => '318265453178933248',
                           'from_user_id_str' => '63055388',
                           'from_user' => 'okbksk'
                         },
                         {
                           'source' => '&lt;a href=&quot;http://twitter.com/tweetbutton&quot;&gt;Tweet Button&lt;/a&gt;',
                           'geo' => undef,
                           'profile_image_url' => 'http://a0.twimg.com/profile_images/349094426/Homo_sapiens_L_normal.png',
                           'id_str' => '317584442908614656',
                           'from_user_id' => 63055388,
                           'profile_image_url_https' => 'https://si0.twimg.com/profile_images/349094426/Homo_sapiens_L_normal.png',
                           'iso_language_code' => 'ja',
                           'created_at' => 'Fri, 29 Mar 2013 10:30:06 +0000',
                           'text' => "BP3137 \x{7be9}\x{9aa8} http://221.186.138.155/bp3d-38321/?shorten=uKDSzyHvq09HK5LniOTHPjmW #bp3d Parpendicular plate is missing. Needs",
                           'metadata' => {
                                           'result_type' => 'recent'
                                         },
                           'from_user_name' => "\x{304a}\x{304a}\x{304f}\x{307c}",
                           'id' => '317584442908614656',
                           'from_user_id_str' => '63055388',
                           'from_user' => 'okbksk'
                         },
                         {
                           'source' => '&lt;a href=&quot;http://twitter.com/tweetbutton&quot;&gt;Tweet Button&lt;/a&gt;',
                           'geo' => undef,
                           'profile_image_url' => 'http://a0.twimg.com/profile_images/349094426/Homo_sapiens_L_normal.png',
                           'id_str' => '317568497184026625',
                           'from_user_id' => 63055388,
                           'profile_image_url_https' => 'https://si0.twimg.com/profile_images/349094426/Homo_sapiens_L_normal.png',
                           'iso_language_code' => 'ja',
                           'created_at' => 'Fri, 29 Mar 2013 09:26:44 +0000',
                           'text' => "BP3129 \x{92e4}\x{9aa8} http://221.186.138.155/bp3d-38321/?shorten=emy8Hj8fO111r4bumCeKfamS #bp3d Position is wrong. Check articulation with ETH+MAX.",
                           'metadata' => {
                                           'result_type' => 'recent'
                                         },
                           'from_user_name' => "\x{304a}\x{304a}\x{304f}\x{307c}",
                           'id' => '317568497184026625',
                           'from_user_id_str' => '63055388',
                           'from_user' => 'okbksk'
                         }
                       ],
          'since_id' => 0
        };
	push(@$results,@{$r->{'results'}});
}
if(defined $results){
	my $dbh = &get_dbh();

	use CGI;
#	my $q = CGI->new();

#	print Dumper($results);
	foreach my $result (@$results){
		my $time = &HTTP::Date::str2time($result->{'created_at'});
		my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($time);
		my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
		print $logtime,"\n";

		print $result->{'source'},"\n";
		my $source = $result->{'source'};


		print CGI::unescapeHTML($result->{'source'}),"\n";

		$source =~ s/&lt;/</g;
		$source =~ s/&gt;/>/g;
		$source =~ s/&quot;/"/g;
		print $source,"\n";

		print $result->{'text'},"\n";
		print $result->{'from_user_name'},"\n";
		print '@',$result->{'from_user'},"\n";
		print "\n";
	}
}
