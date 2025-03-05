#!/opt/services/ag/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use File::Spec::Functions qw(abs2rel rel2abs catdir catfile splitdir);
use File::Path;
use Archive::Zip qw( :ERROR_CODES );

use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'..','cgi_lib');
use BITS::Config;
require "webgl_common.pl";
use cgi_lib::common;

sub main {
	my $base_path = &catdir($FindBin::Bin,'renderer_file');
	my $version_file_path = &catdir($base_path,'versions_file.json');
	my $renderer_file_base_path = &catdir($base_path,'renderer_file');

	my $objs_base_path = &catdir($FindBin::Bin,'objs');
	my $public_base_path = &catdir($objs_base_path,'public');
	my $local_base_path = &catdir($objs_base_path,'local');

	if(-e $version_file_path){
		my $versions_hash = &cgi_lib::common::readFileJSON($version_file_path);
		if(defined $versions_hash && ref $versions_hash eq 'HASH'){
			foreach my $version (sort keys(%{$versions_hash})){
				next unless(exists $versions_hash->{$version} && defined $versions_hash->{$version} && ref $versions_hash->{$version} eq 'HASH');

				my $tsv_filename = qq|$version.tsv|;
				my $zip_filename = qq|$tsv_filename.zip|;

				my $public_zip_file = &catfile($public_base_path,$zip_filename);

				my $version_dir = &catdir($local_base_path,$version);
				my $tsv_filepath = &catfile($local_base_path,$tsv_filename);
				my $zip_filepath = &catfile($local_base_path,$zip_filename);

				unless(-e $tsv_filepath && -r $tsv_filepath && -s $tsv_filepath){
					my $renderer_file_path = &catdir($renderer_file_base_path,qq|$version.json|);
					if(-e $renderer_file_path && -s $renderer_file_path && -r $renderer_file_path){

						my $renderer_hash = &cgi_lib::common::readFileJSON($renderer_file_path);
						if(defined $renderer_hash && ref $renderer_hash eq 'HASH'){

							my $art_ids = $renderer_hash->{$version}->{'art_ids'};
							my $ids = $renderer_hash->{$version}->{'ids'};
							if(defined $art_ids && ref $art_ids eq 'HASH' && defined $ids && ref $ids eq 'HASH'){
								say STDERR qq|[$tsv_filepath]|;
								open(my $OUT, '>', $tsv_filepath) or die "$!";
								say $OUT qq|#FMAID\texpansion\tobjid|;
								foreach my $id (sort keys(%{$ids})){
									next unless($id =~ /^FMA[0-9]+$/);
									my $id_hash = $ids->{$id};
#									say STDERR qq|\t[$id]|;
									foreach my $expansion_key (qw/art_ids art_ids_isa art_ids_partof/){
										my $expansion = 'all';
										if($expansion_key eq 'art_ids_isa'){
											$expansion = 'is_a';
										}
										elsif($expansion_key eq 'art_ids_partof'){
											$expansion = 'part_of';
										}
#										say STDERR qq|\t\t[$expansion]|;
										next unless(
											exists	$id_hash->{$expansion_key} &&
											defined	$id_hash->{$expansion_key} &&
											ref			$id_hash->{$expansion_key} eq 'ARRAY' &&
											scalar	@{$id_hash->{$expansion_key}}
										);
										my $obj_ids_hash = {};
										foreach my $obj_id (@{$id_hash->{$expansion_key}}){
#											say STDERR qq|\t\t\t[$obj_id]|;
											if(
												exists	$art_ids->{$obj_id} &&
												defined	$art_ids->{$obj_id} &&
												ref			$art_ids->{$obj_id} eq 'HASH' &&
												exists	$art_ids->{$obj_id}->{'artc_id'} &&
												defined	$art_ids->{$obj_id}->{'artc_id'} &&
												length	$art_ids->{$obj_id}->{'artc_id'}
											){
												$obj_ids_hash->{ $art_ids->{$obj_id}->{'artc_id'} } = undef;
											}
											else{
												$obj_ids_hash->{$obj_id} = undef;
											}
										}
										say $OUT sprintf("%s\t%s\t%s",$id,$expansion,join(',',sort keys(%{$obj_ids_hash})));
									}
								}
								close($OUT);
							}
						}
					}
				}

				unless(-e $zip_filepath && -r $zip_filepath && -s $zip_filepath){
					if(-e $tsv_filepath && -r $tsv_filepath && -s $tsv_filepath){
						my $zip = Archive::Zip->new();
						$zip->addFile(&cgi_lib::common::encodeUTF8($tsv_filepath),&cgi_lib::common::encodeUTF8($tsv_filename));
						die 'write error' unless($zip->writeToFileNamed($zip_filepath) == AZ_OK);
					}
				}

				if(
							exists	$versions_hash->{$version}->{'mv_publish'}
					&&	defined	$versions_hash->{$version}->{'mv_publish'}
					&&					$versions_hash->{$version}->{'mv_publish'}
				){
					chdir $public_base_path;
					my $local_path = &catdir('..','local');
					symlink( &catfile($local_path,$zip_filename), $zip_filename) unless(-e $public_zip_file);
				}
				else{
					unlink($public_zip_file) if(-e $public_zip_file);
				}
				chdir $FindBin::Bin;
			}
		}
	}
}

&main();
