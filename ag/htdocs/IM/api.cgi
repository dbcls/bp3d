#!/bp3d/local/perl/bin/perl

$| = 1 unless(defined $ENV{MOD_PERL});

use strict;
use warnings;
use feature ':5.10';

use File::Basename;

#use AG::API::Point;
use cgi_lib::common;

sub main {
	my $json = "";

	if(exists $ENV{'REQUEST_METHOD'} && defined $ENV{'REQUEST_METHOD'}){
		if($ENV{'REQUEST_METHOD'} eq 'POST'){
			read(STDIN, $json, $ENV{'CONTENT_LENGTH'});
		}elsif(exists $ENV{'QUERY_STRING'} && defined $ENV{'QUERY_STRING'}){
			$json = $ENV{'QUERY_STRING'};
		}
	}else{
#		$json = &cgi_lib::common::url_encode(qq|{"Common":{"Model":"bp3d","Version":"4.0","AnatomogramVersion":"09051901","ColorbarFlag":false,"ScalarColorFlag":false,"TreeName":"isa","DateTime":"20150206150316","CoordinateSystemName":"bp3d","PinNumberDrawFlag":true,"PinDescriptionDrawFlag":true,"PinIndicationLineDrawFlag":0},"Window":{"ImageWidth":1076,"ImageHeight":1048,"BackgroundColor":"FFFFFF","BackgroundOpacity":100,"GridFlag":false,"GridTickInterval":100,"GridColor":"FFFFFF"},"Camera":{"CameraMode":"camera","CameraX":-66.8638,"CameraY":-1013.482,"CameraZ":1107.6296,"TargetX":-66.8638,"TargetY":-125.426,"TargetZ":1107.6296,"CameraUpVectorX":0,"CameraUpVectorY":0,"CameraUpVectorZ":1,"Zoom":18},"Part":[{"PartID":"FMA7197","PartColor":"F0D2A0","ScalarColorFlag":false,"PartOpacity":1,"PartRepresentation":"S","UseForBoundingBoxFlag":true,"PartDeleteFlag":false},{"PartID":"FMA15743","PartColor":"F0D2A0","ScalarColorFlag":false,"PartOpacity":1,"PartRepresentation":"S","UseForBoundingBoxFlag":true,"PartDeleteFlag":true},{"PartID":"FMA15742","PartColor":"FF0000","ScalarColorFlag":false,"PartOpacity":1,"PartRepresentation":"surface","UseForBoundingBoxFlag":true,"PartDeleteFlag":false}],"Pin":[{"PinID":1,"PinX":-59.2149,"PinY":-190.6797,"PinZ":1133.1259,"PinArrowVectorX":0.6256,"PinArrowVectorY":1.2385,"PinArrowVectorZ":-0.2849,"PinUpVectorX":0,"PinUpVectorY":0,"PinUpVectorZ":1,"PinDescriptionDrawFlag":true,"PinDescriptionColor":"0000FF","PinColor":"0000FF","PinShape":"PIN_LONG","PinSize":112.5,"PinCoordinateSystemName":"bp3d","PinPartID":"FMA15746","PinPartName":"Hepatovenous segment VIII","PinNumberDrawFlag":true}],"Pick":{"MaxNumberOfPicks":20,"ScreenPosX":433,"ScreenPosY":463}}|);

#		$json = &cgi_lib::common::url_encode(qq|{"Common":{"Model":"bp3d","Version":"4.0","AnatomogramVersion":"09051901","ColorbarFlag":false,"ScalarColorFlag":false,"TreeName":"isa","DateTime":"20150206170121","CoordinateSystemName":"bp3d","PinNumberDrawFlag":true,"PinDescriptionDrawFlag":true,"PinIndicationLineDrawFlag":0},"Window":{"ImageWidth":1076,"ImageHeight":1048,"BackgroundColor":"FFFFFF","BackgroundOpacity":100,"GridFlag":false,"GridTickInterval":100,"GridColor":"FFFFFF"},"Camera":{"CameraMode":"camera","CameraX":-66.8638,"CameraY":-1013.482,"CameraZ":1107.6296,"TargetX":-66.8638,"TargetY":-125.426,"TargetZ":1107.6296,"CameraUpVectorX":0,"CameraUpVectorY":0,"CameraUpVectorZ":1,"Zoom":18},"Part":[{"PartID":"FMA7197","PartColor":"F0D2A0","ScalarColorFlag":false,"PartOpacity":1,"PartRepresentation":"S","UseForBoundingBoxFlag":true,"PartDeleteFlag":false},{"PartID":"FMA15743","PartColor":"F0D2A0","ScalarColorFlag":false,"PartOpacity":1,"PartRepresentation":"S","UseForBoundingBoxFlag":true,"PartDeleteFlag":true},{"PartID":"FMA15745","PartColor":"FF0000","ScalarColorFlag":false,"PartOpacity":1,"PartRepresentation":"surface","UseForBoundingBoxFlag":true,"PartDeleteFlag":false}],"Pin":[{"PinID":1,"PinX":-59.2149,"PinY":-190.6797,"PinZ":1133.1259,"PinArrowVectorX":0.6256,"PinArrowVectorY":1.2385,"PinArrowVectorZ":-0.2849,"PinUpVectorX":0,"PinUpVectorY":0,"PinUpVectorZ":1,"PinDescriptionDrawFlag":true,"PinDescriptionColor":"0000FF","PinColor":"0000FF","PinShape":"PIN_LONG","PinSize":112.5,"PinCoordinateSystemName":"bp3d","PinPartID":"FMA15746","PinPartName":"Hepatovenous segment VIII","PinNumberDrawFlag":true}],"Pick":{"MaxNumberOfPicks":20,"ScreenPosX":861,"ScreenPosY":274}}|).qq|&callback=func|;

		$json = qq|%7B"Common"%3A%7B"Model"%3A"bp3d"%2C"Version"%3A"4.2.1310071531"%2C"AnatomogramVersion"%3A"09051901"%2C"ColorbarFlag"%3Afalse%2C"ScalarColorFlag"%3Afalse%2C"TreeName"%3A"isa"%2C"DateTime"%3A"20140906170000"%2C"CoordinateSystemName"%3A"bp3d"%2C"PinNumberDrawFlag"%3Atrue%2C"PinDescriptionDrawFlag"%3Atrue%2C"PinIndicationLineDrawFlag"%3A0%7D%2C"Window"%3A%7B"ImageWidth"%3A400%2C"ImageHeight"%3A400%2C"BackgroundColor"%3A"FFFFFF"%2C"BackgroundOpacity"%3A100%2C"GridFlag"%3Afalse%2C"GridTickInterval"%3A100%2C"GridColor"%3A"FFFFFF"%7D%2C"Camera"%3A%7B"CameraMode"%3A"camera"%2C"CameraX"%3A2.798%2C"CameraY"%3A-998.428%2C"CameraZ"%3A809.7307%2C"TargetX"%3A2.798%2C"TargetY"%3A-110.3716%2C"TargetZ"%3A809.7307%2C"CameraUpVectorX"%3A0%2C"CameraUpVectorY"%3A0%2C"CameraUpVectorZ"%3A1%2C"Zoom"%3A0%7D%7D|;

	}
#	&cgi_lib::common::message($json);

#	my($name,$dir,$ext) = &File::Basename::fileparse($0,qr/\.[^\.]*$/);

	&cgi_lib::common::printNotFound() unless($json);

	my($name,$dir,$ext) = &File::Basename::fileparse($0,qr/\..*$/);
	$name = ucfirst($name);
	my $m = qq|AG::API::$name|;
	eval "use $m";
	if($@){
		&cgi_lib::common::message($@);
		&cgi_lib::common::printNotFound();
	}else{
#		eval qq|${m}::parse('|.$json.qq|')|;
#		if($@){
#			&cgi_lib::common::message($@);
#			&cgi_lib::common::printNotFound();
#		}
		eval{
			my $o = eval qq|new ${m}('|.$json.qq|')|;
			if($@){
				&cgi_lib::common::message($@);
				&cgi_lib::common::printNotFound();
			}
			else{
				$o->parse();
			}
		};
		if($@){
			&cgi_lib::common::message($@);
			&cgi_lib::common::printNotFound();
		}
	}


#	&AG::API::Point::parse($json);
}

&main();
