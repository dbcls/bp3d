#!/bp3d/local/perl/bin/perl

$| = 1 unless(defined $ENV{MOD_PERL});

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI::Cookie;
use JSON::XS;

use AG::API::GlobalPin;

use constant {
	DEBUG => AG::ComDB::GlobalPin::DEBUG
#	DEBUG => 0
};

sub main {
	my $RTN = {
		success => JSON::XS::false,
		message => undef
	};
	my $PARAMS = {};
	my $COOKIE = {};

	my $query = CGI->new;

	my @params = $query->param();
	foreach my $param (@params){
		next if(exists $PARAMS->{$param} && defined $PARAMS->{$param});
		$PARAMS->{$param} = defined $query->param($param) ? $query->param($param) : undef;
		$PARAMS->{$param} = undef if(defined $PARAMS->{$param} && length($PARAMS->{$param})==0);
	}
	my @url_params = $query->url_param();
	foreach my $url_param (sort @url_params){
		next if(exists $PARAMS->{$url_param} && defined $PARAMS->{$url_param});
		$PARAMS->{$url_param} = defined $query->url_param($url_param) ? $query->url_param($url_param) : undef;
		$PARAMS->{$url_param} = undef if(defined $PARAMS->{$url_param} && length($PARAMS->{$url_param})==0);
	}
	my @cookie_params = $query->cookie();
	foreach my $cookie_param (sort @cookie_params){
		$COOKIE->{$cookie_param} = defined $query->cookie($cookie_param) ? $query->cookie($cookie_param) : undef;
	}
	unless(exists $PARAMS->{'json'}){
		foreach my $key (keys(%$PARAMS)){
			if($key =~ /^[\[\{].+[\]\}]$/){
				$PARAMS->{'json'} = $key;
				delete $PARAMS->{$key};
			}
			last if(exists $PARAMS->{'json'});
		}
	}

	print "Content-Type:text/html\n\n" if(DEBUG);

	$RTN = AG::API::GlobalPin::parse(
		cmd =>$PARAMS->{'cmd'},
		type=>$PARAMS->{'type'},
		json=>$PARAMS->{'json'},
		start=>$PARAMS->{'start'},
		limit=>$PARAMS->{'limit'},
		'sort'=>$PARAMS->{'sort'},
		'dir'=>$PARAMS->{'dir'},
		cookie=>$COOKIE
	);

	unless(DEBUG){
		$RTN->{'message'} =~ s/\n//g if(defined $RTN->{'message'} && $RTN->{'message'} =~ /\n/);
		while(defined $RTN->{'message'} && $RTN->{'message'} =~ /\s+at\s+\/.+$/){
			$RTN->{'message'} =~ s/\s+at\s+\/.+$//g;
		}
	}
	$RTN->{'message'} =~ s/\s*$//g if(defined $RTN->{'message'});


	my $content = &JSON::XS::encode_json($RTN);
	if(exists $PARAMS->{'callback'} && defined $PARAMS->{'callback'}){
		print "Content-Type:text/javascript\n\n" unless(DEBUG);
		print $PARAMS->{'callback'}."(".$content.")";
	}else{
		print "Content-Type:text/plain\n\n" unless(DEBUG);
		print $content;
	}
#=pod
	if(DEBUG){
		unless(exists $ENV{HTTP_REFERER}){
			print '<br><br><hr size=1>';
			print $json.'<br>';
			foreach my $key (sort keys(%$PARAMS)){
				print qq|\$PARAMS->{$key}=[$PARAMS->{$key}]<br>|;
			}
			foreach my $key (sort keys(%$COOKIE)){
				print qq|\$COOKIE->{$key}=[$COOKIE->{$key}]<br>|;
			}
			foreach my $key (sort keys(%ENV)){
				print qq|\$ENV{$key}=[$ENV{$key}]<br>|;
			}
		}
	}
#=cut
}
&main();
