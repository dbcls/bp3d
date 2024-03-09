package yahoo;

use strict;
use vars qw($VERSION);
$VERSION = "0.01";

$ENV{'TZ'} = "JST-9";

use HTTP::Date;
use Web::Scraper;
use LWP::UserAgent;
use URI;
use MIME::Base64;
use Data::Dumper;
use File::Path;
use FindBin;

#my $ua = new LWP::UserAgent( agent => 'Mozilla/5.0 (Windows NT 5.1; rv:22.0) Gecko/20100101 Firefox/22.0' );
my $ua = new LWP::UserAgent();

sub _get_head {
	my $url = shift;
	my $res;
	if(wantarray){
		$res = $ua->get($url);
	}else{
		$res = $ua->head($url);
	}
	if($res->is_success){
		$url = $res->request->uri->as_string;
	}else{
	}
	return wantarray ? ($url,$res) : $url;
}

sub get {
	my $scraper = scraper {
		#2013/07/17時点でのformat
		process 'div.cnt.cf', "statuses[]" => scraper {

			process '[data-time]', 'created_at' => sub {
				my $html = shift;
				my $text = $html->attr('data-time');
				$text = time unless(defined $text && length($text));
				&HTTP::Date::time2str($text)
			};#ツイート日時

			process 'h2', 'text' => 'TEXT';#ツイート内容

			process 'h2', "entities" => scraper {

				process 'a.url[target]', 'urls[]' =>  sub {
					my $html = shift;
					my $text = $html->attr('href');
					my $url;
					if(defined $text && length($text)){
						$url = {'url' => $text};
						my $expanded_url = &_get_head($text);
						$url->{'expanded_url'} = $expanded_url if($expanded_url ne $text);
					}
					$url;
				};

				process 'a.url>em', 'hashtags[]' => sub {
					my $html = shift;
					my $text = $html->as_text();
					my $hashtag;
					$hashtag = {'text' => $text} if(defined $text && length($text));
					$hashtag;
				};#ハッシュタグ

				result 'hashtags','urls'
			};

			process '*', "user" => scraper {
				process 'p.img>a[target]>img', 'profile_image_url_https' => sub {
					my $html = shift;
					my $src = $html->attr('src');
					my($r_src,$res) = &_get_head($src);
					my $content = $res->content;
					if(defined $content){
#						warn __LINE__,":",length($content),"\n";
						my $base64 = &MIME::Base64::encode_base64($content, '');
						my $mime_type = $res->headers->{'content-type'};
#						warn __LINE__,":$mime_type\n";
#						warn __LINE__,":$base64\n";
						$src = qq|data:$mime_type;base64,$base64|;
					}
					$src;
				};#ユーザイメージ
				process 'div.inf.cf>p.lt>a.nam[target]', 'screen_name' => 'TEXT';#スクリーン名
				process 'div.inf.cf>p.lt>span.s_2', 'name' => sub {
					my $html = shift;
					my $text = $html->right();
					$text;
				};#ユーザ名
			};

			process 'div.inf.cf>p.lt>a[title][target]', 'id' => sub {
				my $html = shift;
				my $href = $html->attr('href');
				my $id;
				$id = $1 if($href =~ /([0-9]+)$/);
				$id;
			};#ID

			result 'text','created_at','id','entities','user'
		};

	};
#	$scraper->user_agent($ua);#わざとUserAgentをデフォルトで使用する。リンクに余計な情報が含まれないため

	my $results;

	my @URLS = qw|http://realtime.search.yahoo.co.jp/search?tt=c&ei=UTF-8&fr=sfp_as&aq=-1&oq=&p=%23bp3d&meta=vc%3D http://realtime.search.yahoo.co.jp/search?tt=c&ei=UTF-8&fr=sfp_as&aq=-1&oq=&p=%23anagra&meta=vc%3D|;
#	my @URLS = qw|file:///ext1/project/ag/ag1/htdocs/db/04_Yahoo/test.html|;

#	my $uri = URI->new(qq|http://realtime.search.yahoo.co.jp/search?tt=c&ei=UTF-8&fr=sfp_as&aq=-1&oq=&p=%23bp3d&meta=vc%3D|);
#	my $uri = URI->new(qq|file:///ext1/project/ag/ag1/htdocs/db/04_Yahoo/test.html|);

	foreach my $url (@URLS){
		my $uri = URI->new($url);
		my $s = $scraper->scrape($uri);
		if(defined $s && defined $s->{'statuses'} && ref $s->{'statuses'} eq 'ARRAY'){
			push(@$results,@{$s->{'statuses'}}) if(scalar @{$s->{'statuses'}} > 0);
		}
	}
	return $results;
}

1;
