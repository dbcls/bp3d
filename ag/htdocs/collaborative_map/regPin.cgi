#!/usr/bin/env perl
use strict;
use CGI;
use JSON;
$| = 1;

# get parameters
my $q = CGI->new;
my $projectNo = $q->param("projectNo");	# project no is used to separate pin information file
unless ($projectNo) {
	$projectNo = 1;			# default project no
}
$projectNo =~ s/[^a-zA-Z0-9]//g;	# only alphanumeric charaters are allowed for project no
my $version = $q->param("version");
my $tree = $q->param("tree");
my $pinJSON = $q->param("pinJSON");
my $pinData = decode_json($pinJSON);
my $pinFile = "pin_".$projectNo.".txt";
my $callback = $q->param("callback");

# read FJID and FMAID relation file
my %fj2fma = ();
my %fj2name = ();
my %fma2name = ();
open IN,"v".$version."_".$tree.".txt";	# assume file name as v[VERSION]_[TREE].txt
# read file contents
while (<IN>) {
	chomp;
	# skip comment line
	if (/^#/) {
		next;
	}
	# split and store FJID / FMAID related information
	my @data = split("\t", $_);
	$fj2fma{$data[0]} = $data[2];
	$fj2name{$data[0]} = $data[3];
	$fma2name{$data[2]} = $data[3];
}
close IN;

# get FJID/FMAID and FMA Preferred Name
my $fjID = "";
my $fmaID = "";
my $partID = $pinData->{"PinPartID"};
# judge ID type
if ($partID =~ /^FJ/) {
	$fjID = $partID;
} elsif ($partID =~ /^FMA/) {
	$fmaID = $partID;
}
$pinData->{"PinPartFJID"} = $fjID;
if ($fj2fma{$fjID}) {
	$fmaID = $fj2fma{$fjID};
}
if ($fmaID) {
	$pinData->{"PinPartID"} = $fmaID;
}
# get FMA Preferred Name
if ($fma2name{$fmaID}) {
	$pinData->{"PinPartName"} = $fma2name{$fmaID};
} elsif ($fj2name{$fjID}) {
	$pinData->{"PinPartName"} = $fj2name{$fjID};
}
my $pinJSON2 = encode_json($pinData);

# check pin file existence
unless (-f $pinFile) {
	open OUT,">".$pinFile;
	close OUT;
	system ("chmod", "777", $pinFile);
}

# append pin information to pin file
open OUT,">>".$pinFile;
print OUT $pinJSON2."\n";
close OUT;

# print message
print "Content-Type:text/plain\n\n";
print $callback."('pin successfully submitted')";
