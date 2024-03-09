package AG::API::CalcRotAxis;

use strict;
use warnings;
use feature ':5.10';

#use AG::API::JSONParser;
use base qw/AG::API::JSONParser/;
use File::Basename;
use JSON::XS;
use AG::API::Log;
use cgi_lib::common;

sub parse {
	my $parser = shift;
#	my $json = shift;
	my $func = shift;
	my $json = $parser->{json};

	my $ag_log = new AG::API::Log($json);

	my $content;
	my $ContentType = qq|application/json|;
	my $Status;
	my $Code = '503';
#	my $parser ;
#	my @extlist = qw|.cgi|;
	my($name,$dir,$ext) = &File::Basename::fileparse($0,qr/\..*$/);

#	open OUT,">./tmp_image/$name.txt";
#	select(OUT);
#	$| = 1;
#	select(STDOUT);
	my $OUT = &cgi_lib::common::getLogFH(undef,undef,&AG::API::JSONParser::get_log_file_basename(),&AG::API::JSONParser::get_log_dir_basename($name));

	if(defined $json){
#		$parser = new AgJSONParser($json);
		if(defined $parser){
			print $OUT __LINE__,":[$json]\n";
			print $OUT __LINE__,":[$parser->{json}]\n";

			my $pickX1 = $parser->{jsonObj}->{Pick}->{ScreenPosX1};# $query->param('px1');
			my $pickY1 = $parser->{jsonObj}->{Pick}->{ScreenPosY1};# $query->param('py1');
			my $pickX2 = $parser->{jsonObj}->{Pick}->{ScreenPosX2};# $query->param('px2');
			my $pickY2 = $parser->{jsonObj}->{Pick}->{ScreenPosY2};# $query->param('py2');

			# Calc target 3D -> 2D by mapping ?
			my $center3dX = $parser->{jsonObj}->{Camera}->{TargetX};# $query->param('tx');
			my $center3dY = $parser->{jsonObj}->{Camera}->{TargetY};# $query->param('ty');
			my $center3dZ = $parser->{jsonObj}->{Camera}->{TargetZ};# $query->param('tz');
			# Calc target 3D -> 2D as center of image
			my $centerX = $parser->{jsonObj}->{Window}->{ImageWidth} / 2;# $query->param('iw') / 2;
			my $centerY = $parser->{jsonObj}->{Window}->{ImageHeight} / 2;# $query->param('ih') / 2;


			$pickX2 = $pickX1 + 1 if($pickX1 == $pickX2);
			$pickY2 = $pickY1 + 1 if($pickY1 == $pickY2);


			# Calc y = Ax + B
			my $paramA = -1 / (($pickY2 - $pickY1) / ($pickX2 - $pickX1));
			my $paramB = $centerY - $paramA * $centerX;

			my $new3dX = undef;
			my $new3dY = undef;
			my $new3dZ = undef;

			$parser->{jsonObj}->{Pick}->{ClipType} = 4;            # $agprm->{AgSOAP}->{AgPick}->{clipType} = 4;
			$parser->{jsonObj}->{Clip}->{ClipMode} = 'depth';      # $agprm->{AgSOAP}->{AgClipPlane}->{clip0Mode} = "depth";
			$parser->{jsonObj}->{Clip}->{ClipDepth} = 0;           # $agprm->{AgSOAP}->{AgClipPlane}->{depthClip0} = 0;
			$parser->{jsonObj}->{ObjectRotate}->{RotateDegree} = 0;# $agprm->{AgSOAP}->{AgProp}->{rotDeg} = 0;

			my $diff = 0;
			my $newX = 0;
			my $newY = 0;
			for ($diff = 5; $diff <= 100; $diff+=5) {
				# Calc new point (X,Y)
				$newX = $centerX + $diff;
				$newY = $paramA * $newX + $paramB;

				# Pick new point
				$parser->{jsonObj}->{Pick}->{ScreenPosX} = int($newX); #$agprm->{AgSOAP}->{AgPick}->{screenPosX} = int($newX);
				$parser->{jsonObj}->{Pick}->{ScreenPosY} = int($newY); #$agprm->{AgSOAP}->{AgPick}->{screenPosY} = int($newY);
				$parser->{json} = encode_json($parser->{jsonObj});
				$content = $parser->getMethodContent('pick');
				unless(defined $content){
					$content = $parser->getContent() unless(defined $content);
					$Status = $parser->getContentStatus();
					$Code = $parser->getContentCode();
					$ContentType = $parser->getContentType();
					last;
				}
				eval{
					my $obj = decode_json($content);
					if(defined $obj && scalar @{$obj->{Pin}} > 0){
						my $item = shift(@{$obj->{Pin}});
						$new3dX = $item->{PinX};
						$new3dY = $item->{PinY};
						$new3dZ = $item->{PinZ};
						my $json = {
							rotAxisX => $item->{PinX} - $center3dX,
							rotAxisY => $item->{PinY} - $center3dY,
							rotAxisZ => $item->{PinZ} - $center3dZ
						};
						$content = encode_json($json);
						last;
					}
				};
			}
		}
	}
	close($OUT);

#	print "Content-Type: text/html\n\n";
#	print $content;

	print "Status:$Status\n" if(defined $Status);
	if($Code eq '200'){
		if(defined $parser && exists $parser->{jsonObj}->{callback}){
			say qq|Content-Type:application/javascript|;
		}else{
			say qq|Content-Type:$ContentType|;
		}
		&cgi_lib::common::_printContentJSON($content,defined $parser ? $parser->{'jsonObj'} : undef);
	}else{
		&cgi_lib::common::printContent($content,$ContentType);
	}

	$ag_log->print(defined $parser ? $parser->{'jsonObj'} : undef,$content,defined $parser ? $parser->getBalancerInformation() : undef);
}

1;
