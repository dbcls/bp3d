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
	my $public_objs_base_path = &catdir($objs_base_path,'public');
	my $local_objs_base_path = &catdir($objs_base_path,'local');

	if(-e $version_file_path){
		my $versions_hash = &cgi_lib::common::readFileJSON($version_file_path);
		if(defined $versions_hash && ref $versions_hash eq 'HASH'){
			foreach my $version (sort keys(%{$versions_hash})){
				next unless(exists $versions_hash->{$version} && defined $versions_hash->{$version} && ref $versions_hash->{$version} eq 'HASH');

				my $zip_filename = qq|$version.zip|;

				my $public_objs_dir = &catfile($public_objs_base_path,$version);
				my $public_objs_file = &catfile($public_objs_base_path,$zip_filename);

				my $version_dir = &catdir($local_objs_base_path,$version);
				my $zip_filepath = &catfile($local_objs_base_path,$zip_filename);

				unless(-e $version_dir && -e $zip_filepath){
					my $renderer_file_path = &catdir($renderer_file_base_path,qq|$version.json|);
					if(-e $renderer_file_path && -s $renderer_file_path && -r $renderer_file_path){
						my $renderer_hash = &cgi_lib::common::readFileJSON($renderer_file_path);
						if(defined $renderer_hash && ref $renderer_hash eq 'HASH'){

							my $zip = Archive::Zip->new();

							my $art_ids = $renderer_hash->{$version}->{'art_ids'};

							chdir $FindBin::Bin;
							mkdir $version_dir or die "$version_dir を作成することができません。 : $!" unless(-e $version_dir);
							say $version_dir;
							chdir $version_dir;

							foreach my $art_id (sort keys(%{$art_ids})){
								#&cgi_lib::common::message($art_ids->{$art_id});
								#die __LINE__;
								my $artc_id = exists $art_ids->{$art_id}->{'artc_id'} && defined $art_ids->{$art_id}->{'artc_id'} ? $art_ids->{$art_id}->{'artc_id'} : $art_id;
								my $obj_filename = qq|$art_id.obj|;
								my $org_path = &catfile('..','..','..','art_file',$obj_filename);
								my $new_path = $obj_filename;
								next unless(-e $org_path);
								symlink($org_path, $new_path) unless(-e $new_path);

								$zip->addFile(&cgi_lib::common::encodeUTF8($org_path),&cgi_lib::common::encodeUTF8($new_path));
							}
							die 'write error' unless($zip->writeToFileNamed($zip_filepath) == AZ_OK);

							chdir $FindBin::Bin;
						}
					}
				}
				if(
							exists	$versions_hash->{$version}->{'mv_publish'}
					&&	defined	$versions_hash->{$version}->{'mv_publish'}
					&&					$versions_hash->{$version}->{'mv_publish'}
				){
					chdir $public_objs_base_path;
					my $local_path = &catdir('..','local');
					symlink( &catdir($local_path,$version), $version) unless(-e $public_objs_dir);
					symlink( &catfile($local_path,$zip_filename), $zip_filename) unless(-e $public_objs_file);
				}
				else{
					unlink($public_objs_dir) if(-e $public_objs_dir);
					unlink($public_objs_file) if(-e $public_objs_file);
				}
				chdir $FindBin::Bin;
			}
		}
	}
}

&main();
