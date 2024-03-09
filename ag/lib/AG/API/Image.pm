package AG::API::Image;

use strict;
use warnings;
use feature ':5.10';

use base qw/AG::API::JSONParser/;

use File::Basename;
use MIME::Base64;
use JSON::XS;
use Time::HiRes;
#use File::Spec;
use File::Spec::Functions qw(catdir catfile);
use File::Path;
use Digest::MD5 qw(md5_hex);
use Clone qw(clone);
use GD;
use Image::Magick;
use AG::API::Log;
use cgi_lib::common;

sub parse {
	my $parser = shift;
#	my $json = shift;
	my $func = shift;
	my $json = $parser->{json};
	my $LOG = $parser->{'__LOG__'};

	my $png;
	my $content;
	my $imgurl;
	my $ContentType = qq|image/png|;
	my $Status;
	my $Code = '503';

	my $ag_log = new AG::API::Log($json);

#	my $parser = new AgJSONParser($json);

	my($name,$dir,$ext) = &File::Basename::fileparse($0,qr/\..*$/);
	my $ag_images_path = &catdir($dir,'ag_images');

	my $autorotate;
	if(defined $parser){
		my $HASH = $parser && $parser->{jsonObj} ? $parser->{jsonObj} : {};
		my $dt = $HASH->{ObjectRotate}->{DateTime} if(defined $HASH->{ObjectRotate} && exists $HASH->{ObjectRotate} && defined $HASH->{ObjectRotate}->{DateTime} && exists $HASH->{ObjectRotate}->{DateTime});
		if(defined $dt){
			$autorotate = "$ag_images_path/$dt";
			unless(-e $autorotate){
				mkdir $autorotate;
				chmod 0777,$autorotate;
			}
			my %TEMP = %{clone($HASH)};
			delete $TEMP{Common}->{DateTime} if(defined $TEMP{Common} && exists $TEMP{Common} && defined $TEMP{Common}->{DateTime} && exists $TEMP{Common}->{DateTime});
			my $hash = &Digest::MD5::md5_hex(&cgi_lib::common::encodeJSON(\%TEMP)."bits.cc");
			$autorotate .= qq|/$hash|;
		}
		if(defined $autorotate && -e $autorotate){
			GD::Image->trueColor(1);
			my $image = GD::Image->new($autorotate);
			if($ENV{'REQUEST_METHOD'} eq 'GET'){
				print "Content-Type: image/png\n\n";
				binmode(STDOUT);
				print $image->png;
			}elsif($ENV{'REQUEST_METHOD'} eq 'POST'){
				$HASH->{dt} = $HASH->{Common}->{DateTime} if(defined $HASH->{Common} && exists $HASH->{Common} && defined $HASH->{Common}->{DateTime} && exists $HASH->{Common}->{DateTime});
				if($ENV{HTTP_USER_AGENT} =~ /\s+MSIE\s+(\d+)\.(\d+)/ && $1 <= 8){
					my @tmpfiles = ();
					my $dirname = $ag_images_path;
					if(-e $dirname){
						opendir(DIR, $dirname) or die;
						@tmpfiles = sort grep { -f "$dirname/$_"} readdir(DIR);
						closedir(DIR);
					}
					my $now = time - (7*24*60*60);#1week
					foreach my $file (@tmpfiles){
						my $filename = &catfile($dirname,$file);
						my $mtile = (stat($filename))[9];
						unlink $filename if($mtile<$now);
					}
					if(exists $HASH->{Common} && defined $HASH->{Common} && exists $HASH->{Common}->{DateTime} && defined $HASH->{Common}->{DateTime}){
						my $filename = $dirname."/".$HASH->{Common}->{DateTime}."_".$$.".png";
						open my $IMGOUT, "> $filename";
						binmode($IMGOUT);
						print $IMGOUT $image->png;
						close $IMGOUT;
						$filename =~ s/$ENV{DOCUMENT_ROOT}//g;
						$filename =~ s/^\/+//g;
						$HASH->{data} = $filename;
					}
				}else{
					$HASH->{data} = qq|data:image/png;base64,|.&MIME::Base64::encode_base64($image->png,'');
				}
#				print qq|Content-type: text/html\n\n|;
#				my $json = &cgi_lib::common::encodeJSON($HASH);
#				print $json;
				&cgi_lib::common::printContentJSON($HASH);
			}
			undef $image;
			$ag_log->print(defined $parser ? $parser->{'jsonObj'} : undef,undef,defined $parser ? $parser->getBalancerInformation() : undef);
			exit;
		}
	}

	if(defined $parser){
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
		$png = $parser->getMethodPicture($name);
		$content = $parser->getContent() unless(defined $png);
		$Status = $parser->getContentStatus();
		$Code = $parser->getContentCode();
		$ContentType = $parser->getContentType();
	}

	my $extension;
	if(defined $png){
		my $im = Image::Magick->new();
		$im->BlobToImage($png);
		$ContentType = $im->Get('mime');
		$extension = lc($im->Get('magick'));
		undef $im;
	}

	if($ENV{'REQUEST_METHOD'} eq 'GET' || $Code ne '200'){
		print "Status:$Status\n" if(defined $Status);
		print "Content-Type:$ContentType\n";
		if(defined $png){
			print "\n";
			binmode(STDOUT);
			print $png;
			if(defined $autorotate){
				open(my $OUT,"> $autorotate");
				binmode($OUT);
				print $OUT $png;
				close($OUT);
				chmod 0666,$autorotate;
			}
		}elsif(defined $content){
#			print $content;
			&cgi_lib::common::_printContent($content);
		}
	}elsif($ENV{'REQUEST_METHOD'} eq 'POST'){
		my $HASH = $parser && $parser->{jsonObj} ? $parser->{jsonObj} : {};
		if(defined $png){
			if(exists $ENV{HTTP_USER_AGENT} && $ENV{HTTP_USER_AGENT} =~ /\s+MSIE\s+(\d+)\.(\d+)/ && $1 <= 8){
				my @tmpfiles = ();
				my $dirname = $ag_images_path;
				if(-e $dirname){
					opendir(DIR, $dirname) or die;
					@tmpfiles = sort grep { -f "$dirname/$_"} readdir(DIR);
					closedir(DIR);
				}
				my $now = time - (7*24*60*60);#1week
				foreach my $file (@tmpfiles){
					my $filename = "$dirname/$file";
					my $mtile = (stat($filename))[9];
					unlink $filename if($mtile<$now);
				}
				if(defined $HASH->{Common} && exists $HASH->{Common} && defined $HASH->{Common}->{DateTime} && exists $HASH->{Common}->{DateTime}){
					my $filename = $dirname."/".$HASH->{Common}->{DateTime}."_".$$.".$extension";
					open IMGOUT, ">".$filename;
					binmode(IMGOUT);
					print IMGOUT $png;
					close IMGOUT;
					$filename =~ s/$ENV{DOCUMENT_ROOT}//g;
					$filename =~ s/^\/+//g;
					$HASH->{data} = $filename;
				}
			}else{
				$HASH->{data} = qq|data:$ContentType;base64,|.&MIME::Base64::encode_base64($png,'');
			}
			$HASH->{dt} = $HASH->{Common}->{DateTime} if(defined $HASH->{Common} && exists $HASH->{Common} && defined $HASH->{Common}->{DateTime} && exists $HASH->{Common}->{DateTime});
			if(defined $autorotate){
				open(my $OUT,"> $autorotate");
				binmode($OUT);
				print $OUT $png;
				close($OUT);
				chmod 0666,$autorotate;
			}
		}
#		my $ContentType = qq|text/html|;
#		print "Content-Type:$ContentType\n\n";
#		my $json = &cgi_lib::common::encodeJSON($HASH);
#		print $json;
		&cgi_lib::common::printContentJSON($HASH);
	}
	$ag_log->print(defined $parser ? $parser->{'jsonObj'} : undef,undef,defined $parser ? $parser->getBalancerInformation() : undef);
}

1;
