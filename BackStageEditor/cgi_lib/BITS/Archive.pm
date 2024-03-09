package BITS::Archive;

use Exporter;

@ISA = (Exporter);
@EXPORT_OK = qw(extract find);
@EXPORT_FAIL = qw(move_file);

use strict;
use warnings;
use feature ':5.10';
use Archive::Extract;
use File::Basename;
use File::Path;
use File::Spec;
use File::Copy;
#use Encode::Guess qw/shift-jis euc-jp 7bit-jis/;
use Encode;

our $dir;
our @FILES;
our @ExtList = qw(.obj .tar .tar.gz .tgz .gz .Z .zip .bz2 .tar.bz2 .tbz .lzma .xz .tar.xz .txz);
our $from_char_charset;
our $to_char_set = 'utf8';

sub extract($;$$) {
	my $file = shift;
	my $prefix = shift;
	my $encode = shift;
	return undef unless(-e $file);

	if(defined $prefix){
		$dir = $prefix;
	}else{
		$dir = &File::Basename::basename($file,@ExtList);
	}
	&File::Path::rmtree($dir) if(-e $dir);
	&File::Path::mkpath($dir,{mode=>0777}) unless(-e $dir);
	chmod 0777,$dir;

	$encode = 'utf8' unless(defined $encode);
	$from_char_charset = $encode;

	my $ae;
	eval{
		$Archive::Extract::WARN = 0;
		$ae = Archive::Extract->new(archive => $file) if(-e $file);
	};
	if(defined $ae){
		my $to_path = File::Spec->catdir(File::Spec->tmpdir(),&File::Basename::basename($dir).qq|_$$|);
		&File::Path::rmtree($to_path) if(-e $to_path);
		&File::Path::mkpath($to_path,{mode=>0777}) unless(-e $to_path);
		chmod 0777,$to_path;
		$ae->extract( to => $to_path);
		&find(\&move_file, $to_path);
		&File::Path::rmtree($to_path) if(-e $to_path);
	}else{
		my $to = File::Spec->catfile($dir,&File::Basename::basename($file));
#		my $decoder = Encode::Guess->guess($to);
#		$to = $decoder->decode($to) if(defined $decoder && ref $decoder ne '');
		&File::Copy::move($file,$to);
		push(@FILES,$to) if(-e $to);
#		push(@FILES,$file) if(-e $file);
	}
	return wantarray ? @FILES : \@FILES;
}


sub move_file($$) {
	my $d = shift;
	my $f = shift;
	my $fr = File::Spec->catfile($d,$f);
	return unless(-f $fr && $f =~ /\.obj$/);
	my $to = File::Spec->catfile($dir,$f);
#	my $decoder = Encode::Guess->guess($to);
#	$to = $decoder->decode($to) if(defined $decoder && ref $decoder ne '');

#	&Encode::from_to($to,$from_char_charset,$to_char_set) if($from_char_charset ne $to_char_set);

	&File::Copy::move($fr,$to);
	push(@FILES,$to) if(-e $to);
}

sub find($$) {
	my $c = shift;
	my $d = shift;
	return unless(-d $d);
	my $D;
	opendir($D,$d) || die "Can't open dir. $!\n";
	my @F = sort readdir($D);closedir($D);
	my $ca;
	foreach my $f (@F){
		next if($f eq "." || $f eq "..");
		{ $c->($d,$f); };
		my $ca = File::Spec->catfile($d,$f);
		next if(-f $ca);
		&find($c,$ca);
	}
}

1;
