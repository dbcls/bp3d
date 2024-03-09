#!/bp3d/local/perl/bin/perl

use strict;
use JSON::XS;

#use lib '/ext1/project/ag/ag-common/lib','/ext1/project/ag/ag1/htdocs_131011','/ext1/project/ag/ag1/htdocs_131011/IM';
use AG::ComDB::Shorturl;

require "common.pl";
#require "common_shorturl.pl";

my %FORM = ();
&decodeForm(\%FORM);
delete $FORM{_formdata} if(exists($FORM{_formdata}));

print qq|Content-type: text/javascript; charset=UTF-8\n\n|;
#unless(exists($FORM{'url'})){
#	print "\n";
#	exit;
#}
#print &convert_url($FORM{'url'});

my $shorturl = new AG::ComDB::Shorturl;
if(exists $FORM{'url'} && defined $FORM{'url'}){
	if(exists($FORM{'callback'})){
		my $jsonStr = &JSON::XS::encode_json($shorturl->convert_url($FORM{'url'},encode=>0));
		$jsonStr = $FORM{'callback'}."(".$jsonStr.")";
		print $jsonStr;
	}else{
		print $shorturl->convert_url($FORM{'url'});
	}
}elsif(exists $FORM{'urls'} && defined $FORM{'urls'}){
	my $json;
	eval{$json = &JSON::XS::decode_json($FORM{'urls'});};
	if(defined $json){
		if(ref $json eq 'HASH'){
			foreach my $key (keys(%$json)){
				if(ref $json->{$key} eq 'HASH' && exists $json->{$key}->{'url'} && defined $json->{$key}->{'url'}){
					$json->{$key}->{'result'} = $shorturl->convert_url($json->{$key}->{'url'}, encode=>0);
				}elsif(ref $json->{$key} eq 'ARRAY'){
					foreach my $data (@{$json->{$key}}){
						$data->{'result'} = $shorturl->convert_url($data->{'url'}, encode=>0) if(ref $data eq 'HASH' && exists $data->{'url'} && defined $data->{'url'});
					}
				}
			}
			$json->{status_code} = 200;
		}elsif(ref $json eq 'ARRAY'){
			foreach my $data (@$json){
				$data->{'result'} = $shorturl->convert_url($data->{'url'}, encode=>0) if(ref $data eq 'HASH' && exists $data->{'url'} && defined $data->{'url'});
			}
		}else{
			undef $json;
		}
	}
	if(defined $json){
		my $jsonStr = &JSON::XS::encode_json($json);
		$jsonStr = $FORM{'callback'}."(".$jsonStr.")" if(exists($FORM{'callback'}));
		print $jsonStr;
	}else{
		print "\n";
	}
}else{
	print "\n";
}
#exit;
