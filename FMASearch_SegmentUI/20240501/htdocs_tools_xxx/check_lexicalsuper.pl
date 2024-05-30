#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use File::Spec::Functions qw(abs2rel rel2abs catdir catfile splitdir);
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'..','cgi_lib');
use BITS::Config;
require "webgl_common.pl";
use cgi_lib::common;

my $path = &catfile($FindBin::Bin,'..','htdocs','renderer_file','renderer_file.json');
my $json = &cgi_lib::common::readFileJSON($path);
if(defined $json && ref $json eq 'HASH'){
	foreach my $version (sort keys(%{$json})){
		next unless(
					defined	$json->{$version}
			&&	ref			$json->{$version} eq 'HASH'
			&&	exists	$json->{$version}->{'ids'}
			&&	defined	$json->{$version}->{'ids'}
			&&	ref			$json->{$version}->{'ids'} eq 'HASH'
		);
		my $ids = $json->{$version}->{'ids'};
		foreach my $cdi_name (sort keys(%{$ids})){
			if($cdi_name =~ /^(FMA[0-9]+)[A-Z]*\-[LRU]$/){
				my $cdi_rname = $1;
				my $cdi = $ids->{$cdi_name};
				my $cdi_r = $ids->{$cdi_rname};
				next unless(
							defined	$cdi_r
					&&	ref			$cdi_r eq 'HASH'
					&&	exists	$cdi_r->{'relation'}
					&&	defined	$cdi_r->{'relation'}
					&&	ref			$cdi_r->{'relation'} eq 'HASH'
					&&	exists	$cdi_r->{'relation'}->{'lexicalsuper'}
					&&	defined	$cdi_r->{'relation'}->{'lexicalsuper'}
					&&	ref			$cdi_r->{'relation'}->{'lexicalsuper'} eq 'HASH'
				);
				my $lexicalsuper = $cdi_r->{'relation'}->{'lexicalsuper'};
				foreach my $cdi_pname (keys(%{$lexicalsuper})){
					say $version."\t".$cdi->{'id'}."\t".$cdi->{'name'}."\t".$cdi_r->{'id'}."\t".$cdi_r->{'name'}."\t".$cdi_pname."\t".$lexicalsuper->{$cdi_pname};
				}
			}
			else{
				my $cdi = $ids->{$cdi_name};
				next unless(
							defined	$cdi
					&&	ref			$cdi eq 'HASH'
					&&	exists	$cdi->{'relation'}
					&&	defined	$cdi->{'relation'}
					&&	ref			$cdi->{'relation'} eq 'HASH'
					&&	exists	$cdi->{'relation'}->{'lexicalsuper'}
					&&	defined	$cdi->{'relation'}->{'lexicalsuper'}
					&&	ref			$cdi->{'relation'}->{'lexicalsuper'} eq 'HASH'
				);
				my $lexicalsuper = $cdi->{'relation'}->{'lexicalsuper'};
				foreach my $cdi_pname (keys(%{$lexicalsuper})){
					say $version."\t"."\t"."\t".$cdi->{'id'}."\t".$cdi->{'name'}."\t".$cdi_pname."\t".$lexicalsuper->{$cdi_pname};
				}
			}
		}
	}
}
