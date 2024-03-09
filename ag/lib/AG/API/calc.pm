package AG::API::calc::AGVec3d;

use strict;
use warnings;
use feature ':5.10';

sub new {
	my $class = shift;
	my @args = @_;
	my $self = {};
	$self->{'x'} = $args[0];
	$self->{'y'} = $args[1];
	$self->{'z'} = $args[2];

	bless $self, $class;
}
sub x {
	my $self = shift;
	my $val = shift;
	$self->{'x'} = $val if(defined $val);
	return $self->{'x'};
}

sub y {
	my $self = shift;
	my $val = shift;
	$self->{'y'} = $val if(defined $val);
	return $self->{'y'};
}

sub z {
	my $self = shift;
	my $val = shift;
	$self->{'z'} = $val if(defined $val);
	return $self->{'z'};
}


package AG::API::calc;

use strict;
use warnings;
use feature ':5.10';
use Math::Trig;
use Math::Round;

use constant {
	epsilon => 0.0000001,
	true => 1,
	false => 0,
	null => undef,
};

sub agDifferenceD3 {
	my $v0 = shift;
	my $v1 = shift;
	my $out = shift;
	$out->x($v0->x() - $v1->x());
	$out->y($v0->y() - $v1->y());
	$out->z($v0->z() - $v1->z());
}

sub agInnerProductD3 {
	my $v0 = shift;
	my $v1 = shift;
	return $v0->x() * $v1->x() + $v0->y() * $v1->y() + $v0->z() * $v1->z();
}

sub agOuterProductD3 {
	my $v0 = shift;
	my $v1 = shift;
	my $out = shift;
	$out->x( (v0->y() * v1->z()) - (v1->y() * v0->z()) );
	$out->y( (v0->z() * v1->x()) - (v1->z() * v0->x()) );
	$out->z( (v0->x() * v1->y()) - (v1->x() * v0->y()) );
}

sub agIsZero {
	my $x = shift;
	return ((($x<epsilon)) && ($x>(- epsilon)) ? 1 : 0);
}

sub agNormalizeD3 {
	my $v0 = shift;
	my $out = shift;
	my $len;
	$len = $v0->x() * $v0->x() + $v0->y() * $v0->y() + $v0->z() * $v0->z();
	$len = sqrt($len);
	if ($len == 0) {
		return false;
	}
	$out->x($v0->x() / $len);
	$out->y($v0->y() / $len);
	$out->z($v0->z() / $len);
	return true;
}

sub agDeg2Rad {
	my $deg = shift;
	return $deg * pi / 180;
}

sub agRad2Deg {
	my $rad = shift;
	return $rad * 180 / pi;
}

sub isNaN { ! defined( $_[0] <=> 9**9**9 ) }

sub calcRotateDeg {
	my $m_ag = shift;

	my $CTx = $m_ag->{targetPos}->x() - $m_ag->{cameraPos}->x();
	my $CTy = $m_ag->{targetPos}->y() - $m_ag->{cameraPos}->y;
	my $CTz = $m_ag->{targetPos}->z() - $m_ag->{cameraPos}->z();

	#// Calculate Rotate H
	my $radH = acos($CTy / sqrt($CTx*$CTx + $CTy * $CTy));
	my $degH = $radH / pi * 180;
	$degH = 360 - $degH if ($CTx > 0);
	while ($degH >= 360) {
		$degH = $degH - 360;
	}
	if ($m_ag->{upVec}->z() < 0) {
		$degH = $degH + 180;
		while ($degH >= 360) {
			$degH = $degH - 360;
		}
	}

	#// Calculate Rotate V
	my $UnitX = -1 * sin($degH / 180 * pi);
	my $UnitY = cos($degH / 180 * pi);
	my $UnitZ = 0;
	my $radV = acos(($CTx * $UnitX + $CTy * $UnitY + $CTz * $UnitZ) / sqrt(($CTx * $CTx + $CTy * $CTy + $CTz * $CTz) * ($UnitX * $UnitX + $UnitY * $UnitY + $UnitZ * $UnitZ)));
	$radV = 0 if(&isNaN($radV ));
	my $degV = $radV / pi * 180;
	$degV = 360 - $degV if ($CTz > 0);
	while ($degV >= 360) {
		$degV = $degV - 360;
	}

	$degH = round($degH);
	$degV = round($degV);

	while ($degH >= 360) {
		$degH = $degH - 360;
	}
	while ($degV >= 360) {
		$degV = $degV - 360;
	}

#//	if(degV%15) degV += (degV%15)>=8?(15-(degV%15)):(degV%15)-15;
#//	if(degH%15) degH += (degH%15)>=8?(15-(degH%15)):(degH%15)-15;

#//	while (degH >= 360) {
#//		degH = degH - 360;
#//	}
#//	while (degV >= 360) {
#//		degV = degV - 360;
#//	}

	return {H=>$degH,V=>$degV};
}

sub calcCameraPos {
	my $m_ag = shift;

	my $eyeLongitudeRadian = &agDeg2Rad($m_ag->{longitude});
	my $eyeLatitudeRadian = &agDeg2Rad($m_ag->{latitude});
	my $eyeTargetDistance = $m_ag->{distance};

	my $target = $m_ag->{targetPos};
	my $eye = $m_ag->{cameraPos};
	my $yAxis = $m_ag->{upVec};

	my $zAxis = new AG::API::calc::AGVec3d(null, null, null);
	my $xAxis = new AG::API::calc::AGVec3d(null, null, null);
	my $tmp0 = new AG::API::calc::AGVec3d(null, null, null);
	my $remind;

	my $cEyeLongitude = cos($eyeLongitudeRadian);
	my $sEyeLongitude = sin($eyeLongitudeRadian);
	my $cEyeLatitude = cos($eyeLatitudeRadian);
	my $sEyeLatitude = sin($eyeLatitudeRadian);

	$zAxis->x($cEyeLatitude * $cEyeLongitude);
	$zAxis->y($cEyeLatitude * $sEyeLongitude);
	$zAxis->z($sEyeLatitude);

	$tmp0->x($cEyeLongitude);
	$tmp0->y($sEyeLongitude);
	$tmp0->z(0);

	if(($zAxis->z()) >= (epsilon)){
		&agOuterProductD3( $zAxis, $tmp0, $xAxis );
		&agNormalizeD3( $xAxis, $xAxis );
		&agOuterProductD3( $zAxis, $xAxis, $yAxis );
		&agNormalizeD3( $yAxis, $yAxis );
	}
	elsif(($zAxis->z()) < -(epsilon)){
		&agOuterProductD3($tmp0, $zAxis, $xAxis);
		&agNormalizeD3($xAxis, $xAxis);
		&agOuterProductD3($zAxis, $xAxis, $yAxis);
		&agNormalizeD3($yAxis, $yAxis);
	}
	else{ #// $zAxis->z() == 0
		$remind =  round($m_ag->{latitude}) % 360;
		$remind = $remind < 0 ? -$remind : $remind;

		if( $remind > 175 && $remind < 185 ){
			$yAxis->x(0);
			$yAxis->y(0);
			$yAxis->z(-1);
		}else{
			$yAxis->x(0);
			$yAxis->y(0);
			$yAxis->z(1);
		}
	}

	$eye->x( ($zAxis->x()) * ($eyeTargetDistance) + ($target->x()) );
	$eye->y( ($zAxis->y()) * ($eyeTargetDistance) + ($target->y()) );
	$eye->z( ($zAxis->z()) * ($eyeTargetDistance) + ($target->z()) );

	my $posDif = (888.056);
	my $tmpDeg = &calcRotateDeg($m_ag);
	if ($tmpDeg->{H} == 0 && $tmpDeg->{V} == 0) {
		$m_ag->{cameraPos}->x($m_ag->{targetPos}->x());
		$m_ag->{cameraPos}->y($m_ag->{targetPos}->y() - $posDif);
		$m_ag->{cameraPos}->z($m_ag->{targetPos}->z());
	} elsif ($tmpDeg->{H} == 90 && $tmpDeg->{V} == 0) {
		$m_ag->{cameraPos}->x($m_ag->{targetPos}->x() + $posDif);
		$m_ag->{cameraPos}->y($m_ag->{targetPos}->y());
		$m_ag->{cameraPos}->z($m_ag->{targetPos}->z());
	} elsif ($tmpDeg->{H} == 180 && $tmpDeg->{V} == 0) {
		$m_ag->{cameraPos}->x($m_ag->{targetPos}->x());
		$m_ag->{cameraPos}->y($m_ag->{targetPos}->y() + $posDif);
		$m_ag->{cameraPos}->z($m_ag->{targetPos}->z());
	} elsif ($tmpDeg->{H} == 270 && $tmpDeg->{V} == 0) {
		$m_ag->{cameraPos}->x($m_ag->{targetPos}->x() - $posDif);
		$m_ag->{cameraPos}->y($m_ag->{targetPos}->y());
		$m_ag->{cameraPos}->z($m_ag->{targetPos}->z());
	}
}

sub setCameraAndTarget {
	my $cam = shift;
	my $tar = shift;
	my $upVec = shift;
	
	my $tc = new AG::API::calc::AGVec3d(undef, undef, undef);#	// camera  -> target
	&agDifferenceD3($cam, $tar, $tc);
	my $tc_len = &agInnerProductD3($tc, $tc);
	$tc_len = sqrt($tc_len);
	if (&agIsZero($tc_len)) {
		return undef;
	}

	my $ntc = new AG::API::calc::AGVec3d(null, null, null);#	// |camera  -> target|
	my $inv_tc_len = 1 / $tc_len;
	$ntc->x($tc->x() * $inv_tc_len);
	$ntc->y($tc->y() * $inv_tc_len);
	$ntc->z($tc->z() * $inv_tc_len);

	my $vz = new AG::API::calc::AGVec3d(0, 0, 1);# // zaxis

	#// calc latitude
	my $latitude = 90;
	if ($upVec->z() >= 0) {
		$latitude = 90 - &agRad2Deg(acos(agInnerProductD3($ntc, $vz)));
	} else {
		$latitude = 90 + &agRad2Deg(acos(agInnerProductD3($ntc, $vz)));
	}

	#// calc longitude
	my $longitude = 0;
	my $ntc_xy = new AG::API::calc::AGVec3d($tc->x(), $tc->y(), 0);

	if (&agNormalizeD3($ntc_xy, $ntc_xy)) {
		my $vx = new AG::API::calc::AGVec3d(1, 0, 0);
		if ($upVec->z() >= 0) {
		} else {
			$ntc_xy->x(-$ntc_xy->x());
			$ntc_xy->y(-$ntc_xy->y());
			$ntc_xy->z(0);
		}
		my $tmp = &agRad2Deg(acos(agInnerProductD3($ntc_xy, $vx)));
		if ($ntc_xy->y() >= 0) {
			$longitude = $tmp;
		} else {
			$longitude = -$tmp;
		}
	} else {
		my $vx = new AG::API::calc::AGVec3d(1, 0, 0);
		my $nup_xy = new AG::API::calc::AGVec3d(null, null, null);
		if ($ntc->z() >= 0) {
			$nup_xy->x(-$upVec->x());
			$nup_xy->y(-$upVec->y());
			$nup_xy->z(0);
		} else {
			$nup_xy->x($upVec->x());
			$nup_xy->y($upVec->y());
			$nup_xy->z(0);
		}
		if (!&agNormalizeD3($nup_xy, $nup_xy)) {
		}
		my $tmp = &agRad2Deg(acos(agInnerProductD3($nup_xy, $vx)));
		if ($nup_xy->y() >= 0) {
			$longitude = $tmp;
		} else {
			$longitude = -$tmp;
		}
	}

	my $m_ag = {};
	$m_ag->{cameraPos} = new AG::API::calc::AGVec3d(2.7979888916016167, -998.4280435445771, 809.7306805551052);
	$m_ag->{upVec} = new AG::API::calc::AGVec3d(0, 0, 1);
	$m_ag->{targetPos} = new AG::API::calc::AGVec3d($tar->x(), $tar->y(), $tar->z());
	$m_ag->{distance} = $tc_len;

	$m_ag->{longitude} = $longitude;
	$m_ag->{latitude} = $latitude;

	&calcCameraPos($m_ag);

	return $m_ag;
}


1;
