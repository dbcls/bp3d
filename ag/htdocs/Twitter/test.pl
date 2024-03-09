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

#my @search_terms = qw|#bp3d #anagra|;
my @search_terms = qw|@tyamamot0328|;
my $search_term = join(" OR ",@search_terms);
my $results;

unless(DEBUG){
	use File::Basename;
	my @extlist = qw|.cgi|;
	my($cgi_name,$cgi_dir,$cgi_ext) = fileparse($0,@extlist);
	my $LOG;
	open($LOG,"> $FindBin::Bin/logs/$cgi_name.".time.".txt");
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
		traits   => [qw/API::RESTv1_1/],
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


	for(my $args = { q => $search_term, count => 100 }, my $n = 0; $n < 1000; ) {
		my $r = $nt->search({ %$args });
		print $LOG __LINE__,":",Dumper($r);
		last unless @{$r->{statuses}};

		push(@$results,@{$r->{'statuses'}});

		$args->{max_id} = $r->{statuses}[-1]{id} - 1;
		$n += @{$r->{statuses}};
	}
	close($LOG);
}
exit;


if(DEBUG){
	my $r = {
          'search_metadata' => {
                                 'since_id_str' => '0',
                                 'count' => 100,
                                 'query' => '%23bp3d+OR+%23anagra',
                                 'completed_in' => '0.015',
                                 'refresh_url' => '?since_id=318265453178933248&q=%23bp3d%20OR%20%23anagra&include_entities=1',
                                 'max_id' => '318265453178933248',
                                 'max_id_str' => '318265453178933248',
                                 'since_id' => 0
                               },
          'statuses' => [
                          {
                            'retweeted' => bless( do{\(my $o = 0)}, 'JSON::XS::Boolean' ),
                            'source' => '<a href="http://twitter.com/tweetbutton" rel="nofollow">Tweet Button</a>',
#                            'favorited' => $VAR1->{'statuses'}[0]{'retweeted'},
                            'coordinates' => undef,
                            'place' => undef,
                            'retweet_count' => 0,
                            'entities' => {
                                            'user_mentions' => [],
                                            'hashtags' => [
                                                            {
                                                              'text' => 'bp3d',
                                                              'indices' => [
                                                                             80,
                                                                             85
                                                                           ]
                                                            }
                                                          ],
                                            'urls' => []
                                          },
#                            'truncated' => $VAR1->{'statuses'}[0]{'retweeted'},
                            'created_at' => 'Sun Mar 31 07:36:11 +0000 2013',
                            'in_reply_to_status_id_str' => undef,
                            'contributors' => undef,
                            'text' => "BP2798 \x{80f8}\x{817a}\x{306e}\x{8449} http://221.186.138.155/bp3d-38321/?shorten=LrK5Pnjae05vqm0TTvHT9Tz8 #bp3d \x{548c}\x{540d}\x{304a}\x{3088}\x{3073}\x{304b}\x{306a}\x{3000}\x{304c}\x{9593}\x{9055}\x{3063}\x{3066}\x{308b}",
                            'user' => {
                                        'friends_count' => 7,
                                        'follow_request_sent' => undef,
                                        'profile_sidebar_fill_color' => '99CC33',
                                        'profile_image_url' => 'http://a0.twimg.com/profile_images/349094426/Homo_sapiens_L_normal.png',
                                        'profile_background_image_url_https' => 'https://si0.twimg.com/images/themes/theme5/bg.gif',
                                        'entities' => {
                                                        'description' => {
                                                                           'urls' => []
                                                                         }
                                                      },
                                        'profile_background_color' => '352726',
                                        'notifications' => undef,
                                        'url' => undef,
                                        'id' => 63055388,
                                        'following' => undef,
#                                        'is_translator' => $VAR1->{'statuses'}[0]{'retweeted'},
                                        'screen_name' => 'okbksk',
                                        'lang' => 'ja',
                                        'location' => '',
                                        'followers_count' => 53,
                                        'statuses_count' => 205,
                                        'name' => "\x{304a}\x{304a}\x{304f}\x{307c}",
                                        'description' => '',
                                        'favourites_count' => 0,
#                                        'profile_background_tile' => $VAR1->{'statuses'}[0]{'retweeted'},
                                        'listed_count' => 0,
#                                        'contributors_enabled' => $VAR1->{'statuses'}[0]{'retweeted'},
                                        'profile_link_color' => 'D02B55',
                                        'profile_image_url_https' => 'https://si0.twimg.com/profile_images/349094426/Homo_sapiens_L_normal.png',
                                        'profile_sidebar_border_color' => '829D5E',
                                        'created_at' => 'Wed Aug 05 06:38:00 +0000 2009',
                                        'utc_offset' => 32400,
#                                        'verified' => $VAR1->{'statuses'}[0]{'retweeted'},
                                        'profile_background_image_url' => 'http://a0.twimg.com/images/themes/theme5/bg.gif',
#                                        'default_profile' => $VAR1->{'statuses'}[0]{'retweeted'},
#                                        'protected' => $VAR1->{'statuses'}[0]{'retweeted'},
                                        'id_str' => '63055388',
                                        'profile_text_color' => '3E4415',
#                                        'default_profile_image' => $VAR1->{'statuses'}[0]{'retweeted'},
                                        'time_zone' => 'Tokyo',
                                        'geo_enabled' => bless( do{\(my $o = 1)}, 'JSON::XS::Boolean' ),
#                                        'profile_use_background_image' => $VAR1->{'statuses'}[0]{'user'}{'geo_enabled'}
                                      },
                            'in_reply_to_user_id' => undef,
                            'metadata' => {
                                            'result_type' => 'recent',
                                            'iso_language_code' => 'ja'
                                          },
                            'id' => '318265453178933248',
                            'in_reply_to_status_id' => undef,
                            'lang' => 'ja',
                            'geo' => undef,
                            'in_reply_to_user_id_str' => undef,
                            'id_str' => '318265453178933248',
                            'favorite_count' => 0,
                            'in_reply_to_screen_name' => undef
                          },
                          {
#                            'retweeted' => $VAR1->{'statuses'}[0]{'retweeted'},
                            'source' => '<a href="http://twitter.com/tweetbutton" rel="nofollow">Tweet Button</a>',
#                            'favorited' => $VAR1->{'statuses'}[0]{'retweeted'},
                            'coordinates' => undef,
                            'place' => undef,
                            'retweet_count' => 0,
                            'entities' => {
                                            'user_mentions' => [],
                                            'hashtags' => [
                                                            {
                                                              'text' => 'bp3d',
                                                              'indices' => [
                                                                             78,
                                                                             83
                                                                           ]
                                                            }
                                                          ],
                                            'urls' => []
                                          },
#                            'truncated' => $VAR1->{'statuses'}[0]{'retweeted'},
                            'created_at' => 'Fri Mar 29 10:30:06 +0000 2013',
                            'in_reply_to_status_id_str' => undef,
                            'contributors' => undef,
                            'text' => "BP3137 \x{7be9}\x{9aa8} http://221.186.138.155/bp3d-38321/?shorten=uKDSzyHvq09HK5LniOTHPjmW #bp3d Parpendicular plate is missing. Needs",
                            'user' => {
                                        'friends_count' => 7,
                                        'follow_request_sent' => undef,
                                        'profile_sidebar_fill_color' => '99CC33',
                                        'profile_image_url' => 'http://a0.twimg.com/profile_images/349094426/Homo_sapiens_L_normal.png',
                                        'profile_background_image_url_https' => 'https://si0.twimg.com/images/themes/theme5/bg.gif',
                                        'entities' => {
                                                        'description' => {
                                                                           'urls' => []
                                                                         }
                                                      },
                                        'profile_background_color' => '352726',
                                        'notifications' => undef,
                                        'url' => undef,
                                        'id' => 63055388,
                                        'following' => undef,
#                                        'is_translator' => $VAR1->{'statuses'}[0]{'retweeted'},
                                        'screen_name' => 'okbksk',
                                        'lang' => 'ja',
                                        'location' => '',
                                        'followers_count' => 53,
                                        'statuses_count' => 205,
                                        'name' => "\x{304a}\x{304a}\x{304f}\x{307c}",
                                        'description' => '',
                                        'favourites_count' => 0,
#                                        'profile_background_tile' => $VAR1->{'statuses'}[0]{'retweeted'},
                                        'listed_count' => 0,
#                                        'contributors_enabled' => $VAR1->{'statuses'}[0]{'retweeted'},
                                        'profile_link_color' => 'D02B55',
                                        'profile_image_url_https' => 'https://si0.twimg.com/profile_images/349094426/Homo_sapiens_L_normal.png',
                                        'profile_sidebar_border_color' => '829D5E',
                                        'created_at' => 'Wed Aug 05 06:38:00 +0000 2009',
                                        'utc_offset' => 32400,
#                                        'verified' => $VAR1->{'statuses'}[0]{'retweeted'},
                                        'profile_background_image_url' => 'http://a0.twimg.com/images/themes/theme5/bg.gif',
#                                        'default_profile' => $VAR1->{'statuses'}[0]{'retweeted'},
#                                        'protected' => $VAR1->{'statuses'}[0]{'retweeted'},
                                        'id_str' => '63055388',
                                        'profile_text_color' => '3E4415',
#                                        'default_profile_image' => $VAR1->{'statuses'}[0]{'retweeted'},
                                        'time_zone' => 'Tokyo',
#                                        'geo_enabled' => $VAR1->{'statuses'}[0]{'user'}{'geo_enabled'},
#                                        'profile_use_background_image' => $VAR1->{'statuses'}[0]{'user'}{'geo_enabled'}
                                      },
                            'in_reply_to_user_id' => undef,
                            'metadata' => {
                                            'result_type' => 'recent',
                                            'iso_language_code' => 'ja'
                                          },
                            'id' => '317584442908614656',
                            'in_reply_to_status_id' => undef,
                            'lang' => 'ja',
                            'geo' => undef,
                            'in_reply_to_user_id_str' => undef,
                            'id_str' => '317584442908614656',
                            'favorite_count' => 0,
                            'in_reply_to_screen_name' => undef
                          },
                          {
#                            'retweeted' => $VAR1->{'statuses'}[0]{'retweeted'},
                            'source' => '<a href="http://twitter.com/tweetbutton" rel="nofollow">Tweet Button</a>',
#                            'favorited' => $VAR1->{'statuses'}[0]{'retweeted'},
                            'coordinates' => undef,
                            'place' => undef,
                            'retweet_count' => 0,
                            'entities' => {
                                            'user_mentions' => [],
                                            'hashtags' => [
                                                            {
                                                              'text' => 'bp3d',
                                                              'indices' => [
                                                                             78,
                                                                             83
                                                                           ]
                                                            }
                                                          ],
                                            'urls' => []
                                          },
#                            'truncated' => $VAR1->{'statuses'}[0]{'retweeted'},
                            'created_at' => 'Fri Mar 29 09:26:44 +0000 2013',
                            'in_reply_to_status_id_str' => undef,
                            'contributors' => undef,
                            'text' => "BP3129 \x{92e4}\x{9aa8} http://221.186.138.155/bp3d-38321/?shorten=emy8Hj8fO111r4bumCeKfamS #bp3d Position is wrong. Check articulation with ETH+MAX.",
                            'user' => {
                                        'friends_count' => 7,
                                        'follow_request_sent' => undef,
                                        'profile_sidebar_fill_color' => '99CC33',
                                        'profile_image_url' => 'http://a0.twimg.com/profile_images/349094426/Homo_sapiens_L_normal.png',
                                        'profile_background_image_url_https' => 'https://si0.twimg.com/images/themes/theme5/bg.gif',
                                        'entities' => {
                                                        'description' => {
                                                                           'urls' => []
                                                                         }
                                                      },
                                        'profile_background_color' => '352726',
                                        'notifications' => undef,
                                        'url' => undef,
                                        'id' => 63055388,
                                        'following' => undef,
#                                        'is_translator' => $VAR1->{'statuses'}[0]{'retweeted'},
                                        'screen_name' => 'okbksk',
                                        'lang' => 'ja',
                                        'location' => '',
                                        'followers_count' => 53,
                                        'statuses_count' => 205,
                                        'name' => "\x{304a}\x{304a}\x{304f}\x{307c}",
                                        'description' => '',
                                        'favourites_count' => 0,
#                                        'profile_background_tile' => $VAR1->{'statuses'}[0]{'retweeted'},
                                        'listed_count' => 0,
#                                        'contributors_enabled' => $VAR1->{'statuses'}[0]{'retweeted'},
                                        'profile_link_color' => 'D02B55',
                                        'profile_image_url_https' => 'https://si0.twimg.com/profile_images/349094426/Homo_sapiens_L_normal.png',
                                        'profile_sidebar_border_color' => '829D5E',
                                        'created_at' => 'Wed Aug 05 06:38:00 +0000 2009',
                                        'utc_offset' => 32400,
#                                        'verified' => $VAR1->{'statuses'}[0]{'retweeted'},
                                        'profile_background_image_url' => 'http://a0.twimg.com/images/themes/theme5/bg.gif',
#                                        'default_profile' => $VAR1->{'statuses'}[0]{'retweeted'},
#                                        'protected' => $VAR1->{'statuses'}[0]{'retweeted'},
                                        'id_str' => '63055388',
                                        'profile_text_color' => '3E4415',
#                                        'default_profile_image' => $VAR1->{'statuses'}[0]{'retweeted'},
                                        'time_zone' => 'Tokyo',
#                                        'geo_enabled' => $VAR1->{'statuses'}[0]{'user'}{'geo_enabled'},
#                                        'profile_use_background_image' => $VAR1->{'statuses'}[0]{'user'}{'geo_enabled'}
                                      },
                            'in_reply_to_user_id' => undef,
                            'metadata' => {
                                            'result_type' => 'recent',
                                            'iso_language_code' => 'ja'
                                          },
                            'id' => '317568497184026625',
                            'in_reply_to_status_id' => undef,
                            'lang' => 'ja',
                            'geo' => undef,
                            'in_reply_to_user_id_str' => undef,
                            'id_str' => '317568497184026625',
                            'favorite_count' => 0,
                            'in_reply_to_screen_name' => undef
                          }
                        ]
        };
	push(@$results,@{$r->{'statuses'}});
}
if(defined $results){
	my $dbh = &get_dbh();

#	use CGI;
#	my $q = CGI->new();


#	print Dumper($results);
	foreach my $result (@$results){

		next unless(defined $result->{'id'});

		my $created_at;
		my $tw_created;
		my $tw_timezone;
		if(defined $result->{'created_at'}){
			my $t = $result->{'created_at'};
			if($t =~ /\s([\+\-][0-9]{4})\s/){
				$tw_timezone = $1;
				$t =~ s/\s[\+\-][0-9]{4}//g;
			}
			$tw_created = &HTTP::Date::str2time($t);
			my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($tw_created);
			$created_at = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
#			print $created_at,"\n";
#			print $tw_timezone,"\n";
		}
		my $hashtags;
		my $tw_hashtags;
		if(defined $result->{'entities'} && defined $result->{'entities'}->{'hashtags'} && ref $result->{'entities'}->{'hashtags'} eq 'ARRAY'){
			foreach my $hashtag (@{$result->{'entities'}->{'hashtags'}}){
				if(ref $hashtag eq 'HASH' && defined $hashtag->{'text'} && length($hashtag->{'text'})){
					push(@$hashtags,$hashtag->{'text'});
				}elsif(ref $hashtag eq '' && length($hashtag)){
					push(@$hashtags,$hashtag);
				}
			}
			$tw_hashtags = &JSON::XS::encode_json($hashtags) if(defined $hashtags);
		}


		my $sql = qq|select tw_id from twitter_search where tw_id=?|;
		my $sth = $dbh->prepare($sql);
		$sth->execute($result->{'id'});
		my $rows = $sth->rows();
		$sth->finish;
		undef $sth;
		next if($rows>=1);#登録済みの場合

		my $sql =<<SQL;
insert into twitter_search (
tw_id,
tw_hashtags,
tw_text,
tw_created,
tw_timezone,
tw_lang,
tw_user_scname,
tw_user_name,
tw_user_piuhs,
tw_raw_data,
tw_entry,
tw_openid
) values (
?,
?,
?,
?,
?,
?,
?,
?,
?,
?,
'now()',
'system'
)
SQL
		my $sth = $dbh->prepare($sql);

		my $tw_raw_data = &JSON::XS::encode_json($result);
		my $param_num = 0;
		$sth->bind_param(++$param_num, $result->{'id'});
		$sth->bind_param(++$param_num, $tw_hashtags);
		$sth->bind_param(++$param_num, $result->{'text'});
		$sth->bind_param(++$param_num, $tw_created);
		$sth->bind_param(++$param_num, $tw_timezone);
		$sth->bind_param(++$param_num, $result->{'lang'});
		$sth->bind_param(++$param_num, $result->{'user'}->{'screen_name'});
		$sth->bind_param(++$param_num, $result->{'user'}->{'name'});
		$sth->bind_param(++$param_num, $result->{'user'}->{'profile_image_url_https'});
		$sth->bind_param(++$param_num, $tw_raw_data);
		$sth->execute() or die $dbh->errstr;
		my $rows = $sth->rows();
		$sth->finish();
		undef $sth;

		my $shorten;
		my $sp_original;
		if(defined $result->{'text'} && length($result->{'text'}) && $result->{'text'} =~ /\?shorten=([A-Za-z0-9]+)/){
			$shorten = $1;
#			print $shorten,"\n";

			my $sql = qq|select sp_original from shorten_param where sp_shorten=?|;
			my $sth = $dbh->prepare($sql);
			$sth->execute($shorten);
			my $column_number = 0;
			$sth->bind_col(++$column_number, \$sp_original, undef);
			$sth->fetch;
			$sth->finish;
			undef $sth;
#			if(defined $sp_original){
#				print $sp_original,"\n";
#			}
		}
		if(defined $sp_original){#対応レコードが無い場合は、ここのサイトから投稿されたデータでは無い
			my $sql =<<SQL;
insert into representation_twitter (
rep_id,
tw_id,
rtw_entry,
rtw_openid
) values (
?,
?,
'now()',
'system'
)
SQL
			my $sth = $dbh->prepare($sql);
			if($sp_original =~ /i=([A-Z]+[0-9]+)/){
				my $rep_id = $1;
				$sth->execute($rep_id,$result->{'id'});
				$sth->finish;
			}
			undef $sth;
		}




#		print $result->{'text'},"\n";


#		print $result->{'text'},"\n";
#		print $result->{'from_user_name'},"\n";
#		print '@',$result->{'from_user'},"\n";
		print "\n";
	}
}
