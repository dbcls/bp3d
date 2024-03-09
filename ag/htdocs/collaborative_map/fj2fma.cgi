#!/usr/bin/env perl
use strict;
use CGI;
use JSON;
$| = 1;

# get parameters
my $q = CGI->new;
my $version = $q->param("version");
my $tree = $q->param("tree");
my $fj = $q->param("fj");
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

# construct JSON
my $fmaID = $fj2fma{$fj};
my $fmaName = $fj2name{$fj};
my %data;
if ($fj) {
	$data{"jfid"} = $fj;
}
if ($fmaID) {
	$data{"fmaid"} = $fmaID;
}
if ($fmaName) {
	$data{"fmaname"} = $fmaName;
}
my $retJSON = encode_json(\%data);

if ($callback) {
	print "Content-Type:application/javascript\n\n";
	print $callback."(".$retJSON.")";
} else {
	print "Content-Type:application/json\n\n";
	print $retJSON;
}
