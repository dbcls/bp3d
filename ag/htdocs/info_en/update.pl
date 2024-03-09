#!/bp3d/local/perl/bin/perl
#!/usr/bin/perl
use strict;
use LWP::UserAgent;

my $serverBaseURL = "http://lifesciencedb.jp/bp3d/info_en/";
open SITEMAP, "sitemap.txt";
my @siteinfos = ();
while (<SITEMAP>) {
	if (/^#/) {
		next;
	}
	chomp;
	if ($_) {
		push @siteinfos, $_;
	}
}
close SITEMAP;

foreach my $siteinfo (@siteinfos) {
	my @siteinfoAry = split("\t", $siteinfo);
	my $targetURL = $siteinfoAry[0];
	my $templateFile = $siteinfoAry[1];
	my $targetFile = $siteinfoAry[2];
	my $baseURL = $siteinfoAry[3];
	my $wikiDir = $siteinfoAry[4];

	my $request = HTTP::Request->new(GET => $targetURL);
	my $ua = LWP::UserAgent->new;
	my $response = $ua->request($request);
	if ($response->is_success) {
		my $content = $response->content;
		open IN,$templateFile;
		open OUT,">".$targetFile;
		while (<IN>) {
			if (/^REPLACESTRING/) {
				my @contents = split("\n", $content);
				my $fInContent = 0;
				foreach my $line (@contents) {
					$line =~ s/\"\/$wikiDir/\"$baseURL\/$wikiDir/g;
					for my $siteInfoTmp (@siteinfos) {
						my @siteInfoTmpAry = split("\t", $siteInfoTmp);
						my $urlFrom = $siteInfoTmpAry[0];
						my $urlTo = $siteInfoTmpAry[2];
						$line =~ s/$urlFrom/$serverBaseURL$urlTo/g;
					}
					if ($line =~ /\<\!-- start content --\>/) {
						$fInContent = 1;
					} elsif ($line =~ /\<\!-- end content --\>/) {
						print OUT $line."\n";
						$fInContent = 0;
					}
					if ($fInContent) {
						print OUT $line."\n";
					}
				}
			} else {
				print OUT;
			}
		}
		close IN;
		close OUT;
	}
}
