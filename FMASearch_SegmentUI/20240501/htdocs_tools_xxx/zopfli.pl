#!/opt/services/ag/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use Cwd;
use File::Basename;
use File::Copy;
use Sys::CPU;
use Math::Round;
use Parallel::ForkManager;
use Getopt::Long qw(:config posix_default no_ignore_case gnu_compat);

my $jobs = round(Sys::CPU::cpu_count() / 2);
$jobs = 1 if($jobs<1);
#say $jobs;
#exit;

my $config = {
	jobs => $jobs
};
&Getopt::Long::GetOptions($config,qw/
	jobs|j=i
/) or exit 1;

my $zopfli = '/opt/services/ag/local/zopfli/zopfli';
exit unless(-e $zopfli && -f $zopfli && -x $zopfli);

my $exec_file = &Cwd::abs_path($0);
#say $exec_file;
my($exec_name,$exec_dir,$exec_ext) = &File::Basename::fileparse($exec_file, '.pl');
#exit;

#say scalar @ARGV;

$config->{'jobs'} = scalar @ARGV if($config->{'jobs'} > scalar @ARGV);
my $pm = new Parallel::ForkManager($config->{'jobs'});

foreach my $file (@ARGV){

	chdir $exec_dir;
#	print qq|[$exec_dir][$file]|;
	unless(-e $file && -f $file && -s $file && -r $file){
#		say '';
		next;
	}
	my($name,$dir,$ext) = &File::Basename::fileparse($file, qw/.json .obj/);
	unless(defined $ext && length $ext){
#		say '';
		next;
	}
	if($ext eq '.json' && defined $name && length $name && $name =~ /_ext$/){
#		say '';
		next;
	}
	chdir $dir;

	my $org_file = qq|${name}${ext}|;
	#print qq|[$org_file]|;
	my $gz_file;
	if($ext eq '.json'){
		$gz_file = qq|${name}.jgz|;
	}
	elsif($ext eq '.obj'){
		$gz_file = qq|${name}.ogz|;
	}
	unless(defined $gz_file && length $gz_file){
		#say '';
		next;
	}
	#print qq|[$gz_file]|;

	$pm->start and next;

	my $zopfli_file = qq|${name}${ext}.gz|;
	my $zopfli_file_mtime = 0;
	$zopfli_file_mtime = (stat($zopfli_file))[9] if(-e $zopfli_file && -f $zopfli_file && -s $zopfli_file && -r $zopfli_file);
	system(qq|$zopfli $org_file|) if($zopfli_file_mtime<(stat($org_file))[9]);
	if(-e $zopfli_file && -f $zopfli_file && -r $zopfli_file && -s $zopfli_file){
		$zopfli_file_mtime = (stat($zopfli_file))[9];
		unlink $gz_file if(-e $gz_file && -f $gz_file && -l $gz_file);
		unlink $gz_file if(-e $gz_file && -f $gz_file && -s $gz_file > -s $zopfli_file);
		&File::Copy::copy($zopfli_file, $gz_file) unless(-e $gz_file);
	}
	utime($zopfli_file_mtime, $zopfli_file_mtime, $gz_file) if(-e $gz_file);
	say qq|[$zopfli_file]|;

	$pm->finish;
}
$pm->wait_all_children;
