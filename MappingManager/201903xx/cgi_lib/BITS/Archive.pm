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
use File::Spec::Functions qw(abs2rel rel2abs catdir catfile splitdir tmpdir);
use File::Copy;
#use Encode::Guess qw/shift-jis euc-jp 7bit-jis/;
use Encode;

our $dir;
our @FILES;
our @ExtList = qw/.obj .tar .tar.gz .tgz .gz .Z .zip .bz2 .tar.bz2 .tbz .lzma .xz .tar.xz .txz/;
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

	$encode = 'utf8' unless(defined $encode);
	$from_char_charset = $encode;

	my $ae;
	eval{
		$Archive::Extract::WARN = 0;
		$ae = Archive::Extract->new(archive => $file) if(-e $file);
	};
	if(defined $ae){
		unless(-e $dir){
			my $old_mask = umask(0);
			&File::Path::mkpath($dir,{mode=>0777});
			umask($old_mask);
		}
		$ae->extract( to => $dir);
		&find(\&move_file, $dir);
#		die __LINE__;
#		my $to_path = &catdir(&tmpdir(),&File::Basename::basename($dir).qq|_$$|);
#		&File::Path::rmtree($to_path) if(-e $to_path);
#		&File::Path::mkpath($to_path,{mode=>0777}) unless(-e $to_path);
#		chmod 0777,$to_path;
#		$ae->extract( to => $to_path);
#		&find(\&move_file, $to_path);
#		&File::Path::rmtree($to_path) if(-e $to_path);
	}else{
		push(@FILES,$file) if(-e $file);
#		my $to = &catfile($dir,&File::Basename::basename($file));
##		my $decoder = Encode::Guess->guess($to);
##		$to = $decoder->decode($to) if(defined $decoder && ref $decoder ne '');
#		&File::Copy::move($file,$to);
#		push(@FILES,$to) if(-e $to);
##		push(@FILES,$file) if(-e $file);
	}
	return wantarray ? @FILES : \@FILES;
}


sub move_file_old($$) {
	my $d = shift;
	my $f = shift;
	my $fr = &catfile($d,$f);
	return unless(-f $fr && $f =~ /\.obj$/);
	my $to = &catfile($dir,$f);
#	my $decoder = Encode::Guess->guess($to);
#	$to = $decoder->decode($to) if(defined $decoder && ref $decoder ne '');

#	&Encode::from_to($to,$from_char_charset,$to_char_set) if($from_char_charset ne $to_char_set);

	&File::Copy::move($fr,$to);
	push(@FILES,$to) if(-e $to);
}

sub move_file($$) {
	my $d = shift;
	my $f = shift;
	my $fr = &catfile($d,$f);
	return unless(-e $fr && -f $fr && -s $fr && $f =~ /\.obj$/);
	push(@FILES,$fr);
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
		my $ca = &catfile($d,$f);
		next if(-f $ca);
		&find($c,$ca);
	}
}

1;
