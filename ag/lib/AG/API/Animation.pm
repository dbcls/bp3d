package AG::API::Animation;

use strict;
use warnings;
use feature ':5.10';

#use AG::API::JSONParser;
use base qw/AG::API::JSONParser/;
use File::Basename;
use Image::Magick;
use AG::API::Log;

sub parse {
	my $parser = shift;
#	my $json = shift;
#	my $img = shift;
	my $json = $parser->{json};
	my $LOG = $parser->{'__LOG__'};

	my $ag_log = new AG::API::Log($json);

#	my $img;
	my $ContentType = qq|image/gif|;
	my $Status;
	my $Code = '503';
#	my @extlist = qw|.cgi|;
	my($name,$dir,$ext) = &File::Basename::fileparse($0,qr/\..*$/);

#	my $parser = new AgJSONParser($json);

	my $img = &cgi_lib::common::get_cache();
	if(defined $img){
		$Code = '200';
		my $im = Image::Magick->new();
		$im->BlobToImage($img);
		undef $img unless($ContentType eq $im->Get('mime'));
		undef $im;
	}
	if(!defined $img && defined $parser){
		if(
			exists $parser->{'jsonObj'} &&
			defined $parser->{'jsonObj'} &&
			ref $parser->{'jsonObj'} eq 'HASH'
		){
			unless(
				exists $parser->{'jsonObj'}->{'Camera'} &&
				defined $parser->{'jsonObj'}->{'Camera'} &&
				ref $parser->{'jsonObj'}->{'Camera'} eq 'HASH'
			){
				unless(
					exists $parser->{'jsonObj'}->{'Part'} &&
					defined $parser->{'jsonObj'}->{'Part'} &&
					ref $parser->{'jsonObj'}->{'Part'} eq 'ARRAY'
				){
					if(
						exists $parser->{'jsonObj'}->{'Pin'} &&
						defined $parser->{'jsonObj'}->{'Pin'} &&
						ref $parser->{'jsonObj'}->{'Pin'} eq 'ARRAY'
					){

=pod
						$parser->{'jsonObj'}->{'Part'} = [map {
							{
								"PartColor" => "F0D2A0",
								"PartDeleteFlag" => JSON::XS::false,
								"PartID" => $_->{'PinPartID'},
								"PartOpacity" => 0,
								"PartRepresentation" => "S",
								"ScalarColorFlag" => JSON::XS::false,
								"UseForBoundingBoxFlag" => JSON::XS::true
							}
						} @{$parser->{'jsonObj'}->{'Pin'}}];
						$parser->{json} = &cgi_lib::common::encodeJSON($parser->{jsonObj});

						$parser->{jsonObj}->{Camera} //= {};
						$parser->{jsonObj}->{Camera}->{CameraMode} = "front";
						$parser->{jsonObj}->{Camera}->{Zoom} = 0;
						$parser->{json} = &cgi_lib::common::encodeJSON($parser->{jsonObj});
						&cgi_lib::common::dumper($parser->{'jsonObj'},$LOG);

						my $content = $parser->getMethodContent('focus');
						$content = $parser->getContent() unless(defined $content);
						my $Status = $parser->getContentStatus();
						my $Code = $parser->getContentCode();
						my $ContentType = $parser->getContentType();
						&cgi_lib::common::message($content,$LOG);
						&cgi_lib::common::message($Status,$LOG);
						&cgi_lib::common::message($Code,$LOG);
						&cgi_lib::common::message($ContentType,$LOG);

						delete $parser->{jsonObj}->{Camera};
						delete $parser->{jsonObj}->{Part};
=cut
						my $Code = 200;
						if($Code == 200){
#							my $Camera_temp = &cgi_lib::common::decodeJSON($content);
#							my $Camera = $Camera_temp->{Camera};
							my $Camera = {
								TargetX => 0,
								TargetY => 0,
								TargetZ => 0,
							};
							map {
								$Camera->{TargetX} += $_->{PinX};
								$Camera->{TargetY} += $_->{PinY};
								$Camera->{TargetZ} += $_->{PinZ};
							} @{$parser->{'jsonObj'}->{'Pin'}};
							$Camera->{TargetX} /= scalar @{$parser->{'jsonObj'}->{'Pin'}};
							$Camera->{TargetY} /= scalar @{$parser->{'jsonObj'}->{'Pin'}};
							$Camera->{TargetZ} /= scalar @{$parser->{'jsonObj'}->{'Pin'}};

							$parser->{json} = &cgi_lib::common::encodeJSON($parser->{jsonObj});


							$parser->{jsonObj}->{Camera} //= {
								"CameraMode" => "camera",
								"CameraUpVectorX" => 0,
								"CameraUpVectorY" => 0,
								"CameraUpVectorZ" => 1,
								"CameraX" => 2.7979888916016167,
								"CameraY" => -998.4280435445771,
								"CameraZ" => 809.7306805551052,
								"TargetX" => 2.7979888916015625,
								"TargetY" => -110.37168800830841,
								"TargetZ" => 809.7306805551052
							};

							$parser->{jsonObj}->{Camera}->{CameraX} = $parser->{jsonObj}->{Camera}->{CameraX} + $Camera->{TargetX} - $parser->{jsonObj}->{Camera}->{TargetX};
							$parser->{jsonObj}->{Camera}->{CameraY} = $parser->{jsonObj}->{Camera}->{CameraY} + $Camera->{TargetY} - $parser->{jsonObj}->{Camera}->{TargetY};
							$parser->{jsonObj}->{Camera}->{CameraZ} = $parser->{jsonObj}->{Camera}->{CameraZ} + $Camera->{TargetZ} - $parser->{jsonObj}->{Camera}->{TargetZ};

							$parser->{jsonObj}->{Camera}->{TargetX} = $Camera->{TargetX};
							$parser->{jsonObj}->{Camera}->{TargetY} = $Camera->{TargetY};
							$parser->{jsonObj}->{Camera}->{TargetZ} = $Camera->{TargetZ};
							$parser->{jsonObj}->{Camera}->{Zoom} = 0;

							use AG::API::calc;
							my $cam = new AG::API::calc::AGVec3d($parser->{jsonObj}->{Camera}->{CameraX}, $parser->{jsonObj}->{Camera}->{CameraY}, $parser->{jsonObj}->{Camera}->{CameraZ});
							my $tar = new AG::API::calc::AGVec3d($parser->{jsonObj}->{Camera}->{TargetX}, $parser->{jsonObj}->{Camera}->{TargetY}, $parser->{jsonObj}->{Camera}->{TargetZ});
							my $upVec = new AG::API::calc::AGVec3d($parser->{jsonObj}->{Camera}->{CameraUpVectorX}, $parser->{jsonObj}->{Camera}->{CameraUpVectorY}, $parser->{jsonObj}->{Camera}->{CameraUpVectorZ});
							my $rtn = &AG::API::calc::setCameraAndTarget($cam,$tar,$upVec);
							&cgi_lib::common::dumper($rtn,$LOG);
							if(defined $rtn){
								$parser->{jsonObj}->{Camera}->{CameraX} = $rtn->{cameraPos}->x();
								$parser->{jsonObj}->{Camera}->{CameraY} = $rtn->{cameraPos}->y();
								$parser->{jsonObj}->{Camera}->{CameraZ} = $rtn->{cameraPos}->z();
								$parser->{jsonObj}->{Camera}->{TargetX} = $rtn->{targetPos}->x();
								$parser->{jsonObj}->{Camera}->{TargetY} = $rtn->{targetPos}->y();
								$parser->{jsonObj}->{Camera}->{TargetZ} = $rtn->{targetPos}->z();
								$parser->{jsonObj}->{Camera}->{CameraUpVectorX} = $rtn->{upVec}->x();
								$parser->{jsonObj}->{Camera}->{CameraUpVectorY} = $rtn->{upVec}->y();
								$parser->{jsonObj}->{Camera}->{CameraUpVectorZ} = $rtn->{upVec}->z();
							}else{
								delete $parser->{jsonObj}->{Camera};
							}
							$parser->{json} = &cgi_lib::common::encodeJSON($parser->{jsonObj});
							&cgi_lib::common::dumper($parser->{'jsonObj'},$LOG);
						}
					}
				}
			}
		}

		$img = $parser->getMethodPicture($name);
		$Status = $parser->getContentStatus();
		$Code = $parser->getContentCode();
		$ContentType = $parser->getContentType();

		&cgi_lib::common::set_cache($img) if(defined $Code && $Code eq '200' && defined $img);
	}

	print "Status:$Status\n" if(defined $Status);
	if(defined $Code && $Code eq '200'){
		print "Content-Type:$ContentType\n\n";
		binmode(STDOUT);
		print $img;
	}else{
		my $content = $parser->getContent() if(defined $parser);
		&cgi_lib::common::printContent($content,$ContentType);
	}
	$ag_log->print(defined $parser ? $parser->{'jsonObj'} : undef,undef,defined $parser ? $parser->getBalancerInformation() : undef);
}

1;
