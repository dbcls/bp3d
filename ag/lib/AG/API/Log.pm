package AG::API::Log;

use strict;
use feature ':5.10';
use Time::HiRes;
use File::Basename;
use JSON::XS;
use File::Spec::Functions qw(catdir catfile);

sub new {
	my $class = shift;
	my $text = shift;
	my $self  = {};

	$self->{'TIME'} = [&Time::HiRes::gettimeofday()];
	$self->{'TEXT'} = &url_decode($text);

=pod

	$self->{AGE}    = undef;
	$self->{'FH'} = $OUT;
=cut

	bless ($self, $class);
	return $self;
}

sub print {
	my $self = shift;
	my $jsonObj = shift;
	my $content = shift;
	my $balancerInformation = shift;

	my($name, $dir, $ext) = &File::Basename::fileparse($0, qr/\..*$/);

	my($wtime,$msec) = @{$self->{'TIME'}};
	my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($wtime);
	my $cur_time = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
	$year = sprintf("%04d",$year+1900);
	$mon  = sprintf("%02d",$mon+1);
	$mday = sprintf("%02d",$mday);

	my $elapsed = &Time::HiRes::tv_interval($self->{'TIME'},[&Time::HiRes::gettimeofday()]);

	my $log_dir = &catdir($dir,'tmp_image',$year,$mon,$mday);
	&File::Path::make_path($log_dir) unless(-e $log_dir);
	my $log_file = &catfile($log_dir,qq|$name.txt|);

	my $json = JSON::XS->new->utf8->indent(0)->canonical(1);

	my @LOGS = ();
	push(@LOGS,$ENV{HTTP_X_FORWARDED_FOR} // $ENV{REMOTE_ADDR} );
	push(@LOGS,$ENV{REQUEST_METHOD});
	push(@LOGS,$name);
	push(@LOGS,$cur_time);
	push(@LOGS,$wtime);
	push(@LOGS,$elapsed);
	push(@LOGS,$self->{'TEXT'});
	push(@LOGS,$json->encode(\%ENV));
	if(defined $jsonObj){
		if(ref $jsonObj eq 'HASH' || ref $jsonObj eq 'ARRAY'){
			push(@LOGS,$json->encode($jsonObj));
		}else{
			push(@LOGS,$jsonObj);
		}
	}else{
		push(@LOGS,'');
	}
	push(@LOGS,$content // '');
	push(@LOGS,$balancerInformation // '');

	open my $OUT,">> $log_file";
	flock($OUT,2);
	select($OUT);
	$| = 1;
	select(STDOUT);
	print $OUT join("\t",@LOGS)."\n";
	close($OUT);
}

sub url_decode {
	my $str = shift;
	$str =~ tr/+/ /;
	$str =~ s/%([0-9A-Fa-f][0-9A-Fa-f])/pack('H2', $1)/eg;
	return $str;
}

1;
