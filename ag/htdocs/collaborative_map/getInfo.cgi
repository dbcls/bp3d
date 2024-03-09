#!/bp3d/local/perl/bin/perl

use strict;
use CGI;
use JSON;
$| = 1;

my $q = CGI->new;
my $projectNo = $q->param("projectNo");
unless ($projectNo) {
	$projectNo = 1;
}
my $pinFile = "pin_".$projectNo.".txt";
my $callback = $q->param("callback");

unless (-f $pinFile) {
	open OUT, ">".$pinFile;
	close OUT;
	system ("chmod", "777", $pinFile);
}

open IN,$pinFile;
my @pinInfos = ();
my %pinIDCnt = ();
while (<IN>) {
	chomp;
	if ($_) {
		push @pinInfos, $_;
	}
	if (/\"PinPartID\":\"([^\"]+)\"/) {
		$pinIDCnt{$1}++;
	}
}
close IN;

my $maxPinCnt = 20;
my $pinInfo = "";
my $startIndex = 0;
if (eval(@pinInfos) - $maxPinCnt >= 0) {
	$startIndex = eval(@pinInfos) - $maxPinCnt;
}
for (my $i = $startIndex; $i < @pinInfos; $i++) {
	if ($pinInfo) {
		$pinInfo .= ",";
	}
	$pinInfo .= $pinInfos[$i];
}

my $maxPartCnt = 40;
my $partHist = "";
my $partCnt = 0;
foreach my $partID (sort {$pinIDCnt{$b} <=> $pinIDCnt{$a}} keys %pinIDCnt) {
	if ($partHist) {
		$partHist .= ",";
	}
	$partHist .= "{'partID':'$partID', 'partCount':$pinIDCnt{$partID}}";
	$partCnt++;
	if ($partCnt >= $maxPartCnt) {
		last;
	}
}

my $json = "";
$json .= "{'publicPinJson':[".$pinInfo."],'publicPinStartIndex':$startIndex, 'publicPinPartFreq':[".$partHist."]}";

print "Content-Type:text/plain\n\n";
if ($callback) {
	print $callback."(".$json.")";
} else {
	print $json;
}
