/////////////////////////////////////////////////////////////////////////////////////////////////////
// ag_common_js.cgiから移植（ここから）
/////////////////////////////////////////////////////////////////////////////////////////////////////
Ext.BLANK_IMAGE_URL = "resources/images/default/s.gif";

var _dump = function(aStr){
//	if(window.dump) window.dump("main.cgi:"+aStr+"\n")
//	try{if(console && console.log) console.log(aStr);}catch(e){}
};

captureEvents = function(observable) {
	Ext.util.Observable.capture(
		observable,
		function(eventName) {
			_dump(eventName);
		},
		this
	);
};

var Cookies = {};
Cookies.set = function(aKey, aVal, aExpires){
//	if(aKey=="ag_annotation.images.type"){
//		_dump("Cookies.set():["+aKey+"]["+aVal+"]["+aExpires+"]");
//	}
	if(aExpires == undefined) aExpires = true;
	if(aExpires){
		var xDay = new Date;
		xDay.setDate(xDay.getDate() + 30); //30 Days after
		xDay = xDay.toGMTString(); //GMT format
		document.cookie = aKey + '=' + escape(aVal) + '; expires=' + xDay + ';';
	}else{
		document.cookie = aKey + '=' + escape(aVal) + ';';
	}
}

Cookies.get = function(name,defvalue){
	if(defvalue == undefined) defvalue = null;
	var arg = name + "=";
	var alen = arg.length;
	var clen = document.cookie.length;
	var i = 0;
	var j = 0;
	while(i < clen){
		j = i + alen;
		if (document.cookie.substring(i, j) == arg){
			var rtnval = Cookies.getCookieVal(j);
//			if(name=="ag_annotation.images.type"){
//				_dump("Cookies.set():["+name+"]["+defvalue+"]["+rtnval+"]");
//			}
			if(rtnval == "") rtnval = defvalue;
			return rtnval;
		}
		i = document.cookie.indexOf(" ", i) + 1;
		if(i == 0)
			break;
	}
//	if(name=="ag_annotation.images.type"){
//		_dump("Cookies.set():["+name+"]["+defvalue+"]");
//	}
	return defvalue;
};

Cookies.clear = function(name) {
//	_dump("Cookies.clear():["+name+"]");
	if(Cookies.get(name)){
		document.cookie = name + "=" +
			"; expires=Thu, 01-Jan-70 00:00:01 GMT";
	}
};

Cookies.getCookieVal = function(offset){
	var endstr = document.cookie.indexOf(";", offset);
	if(endstr == -1){
		endstr = document.cookie.length;
	}
	return unescape(document.cookie.substring(offset, endstr));
};

/////////////////////////////////////////////////////////////////////////////////////////////////////

function anatomo_fixlen_format (num, len) {
	var retStr = num + "";
	while(retStr.length < len) {
		retStr = "0" + retStr;
	}
	return retStr;
}

function anatomo_float_format (num) {
	var scalar = num.toString();
	if (scalar == "NaN") {
		return "NANANANANANA";
	}
	if (scalar.indexOf("e-", 0) >= 0) {
		scalar = "0.0";
	}
	var nums = new Array();
	if (scalar.indexOf(".", 0) >= 0) {
		nums = scalar.split(".");
	} else {
		nums[0] = scalar;
		nums[1] = "";
	}
	var fMinus = false;
	if (nums[0].indexOf("-", 0) >= 0) {
		fMinus = true;
		nums[0] = nums[0].replace("-", "");
	}
	if (nums[0] > 65535) {
		nums[0] = 65535;
	}
	while (nums[0].length < 5) {
		nums[0] = "0" + nums[0];
	}
	while (nums[1].length < 5) {
		nums[1] = nums[1] + "0";
	}
	if (nums[1].length > 5) {
		nums[1] = nums[1].substr(0, 5);
	}
	if (fMinus) {
		return "M" + nums[0] + "." + nums[1];
	} else {
		return "P" + nums[0] + "." + nums[1];
	}
}

function AGVec3d (x, y, z) {
	this.x = x;
	this.y = y;
	this.z = z;
}


function agDifferenceD3 (v0, v1, out) {
	out.x = parseFloat(v0.x) - parseFloat(v1.x);
	out.y = parseFloat(v0.y) - parseFloat(v1.y);
	out.z = parseFloat(v0.z) - parseFloat(v1.z);
}

function agInnerProductD3 (v0, v1) {
	return parseFloat(v0.x * v1.x) + parseFloat(v0.y * v1.y) + parseFloat(v0.z * v1.z);
}

function agOuterProductD3 (v0, v1, out) {
	out.x = parseFloat(v0.y * v1.z) - parseFloat(v1.y * v0.z);
	out.y = parseFloat(v0.z * v1.x) - parseFloat(v1.z * v0.x);
	out.z = parseFloat(v0.x * v1.y) - parseFloat(v1.x * v0.y);
}

function agNormalizeD3 (v0, out) {
	var len;
	len = parseFloat(v0.x * v0.x) + parseFloat(v0.y * v0.y) + parseFloat(v0.z * v0.z);
	len = Math.sqrt(len);
	if (len == 0) {
		return false;
	}
	out.x = v0.x / len;
	out.y = v0.y / len;
	out.z = v0.z / len;
	return true;
}

function agCopyD3 (v0, out) {
	out.x = v0.x;
	out.y = v0.y;
	out.z = v0.z;
}

function agIsZero (x) {
	return (((parseFloat(x)<parseFloat(m_ag.epsilon)) && (parseFloat(x)>(-parseFloat(m_ag.epsilon)))) ? true : false);
}

function agDeg2Rad (deg) {
	return deg * m_ag.PI / 180;
}

function agRad2Deg (rad) {
	return rad * 180 / m_ag.PI;
}




function getCameraPos () {
	return m_ag.cameraPos;
}

function getTargetPos () {
	return m_ag.targetPos;
}

function getYRange () {
	return m_ag.orthoYRange;
}

function getYRangeFromServer(aCB) {
	var img = document.getElementById("clipImg");
	var urlStr = img.src;
	urlStr = urlStr.replace(/^[^?]+/,"getYRange.cgi");

	var yRange = "";
	Ext.Ajax.request({
		url: urlStr,
		success : function (response, options) {
			yRange = response.responseText;

			YRangeFromServer = parseFloat(yRange);
			if(aCB) (aCB)(YRangeFromServer);
		},
		failure : function (response, options) {
		}
	});
}

function getNear () {
	return m_ag.nearClip;
}

function getFar () {
	return m_ag.farClip;
}

function calcRotateDeg () {
	var CTx = m_ag.targetPos.x - m_ag.cameraPos.x;
	var CTy = m_ag.targetPos.y - m_ag.cameraPos.y;
	var CTz = m_ag.targetPos.z - m_ag.cameraPos.z;

	// Calculate Rotate H
	var radH = Math.acos(CTy / Math.sqrt(CTx*CTx + CTy * CTy));
	var degH = radH / Math.PI * 180;
	if (CTx > 0) degH = 360 - degH;
	while (degH >= 360) {
		degH = degH - 360;
	}
	if (m_ag.upVec.z < 0) {
		degH = degH + 180;
		while (degH >= 360) {
			degH = degH - 360;
		}
	}

	// Calculate Rotate V
	var UnitX = -1 * Math.sin(degH / 180 * Math.PI);
	var UnitY = Math.cos(degH / 180 * Math.PI);
	var UnitZ = 0;
	var radV = Math.acos((CTx * UnitX + CTy * UnitY + CTz * UnitZ) / Math.sqrt((CTx * CTx + CTy * CTy + CTz * CTz) * (UnitX * UnitX + UnitY * UnitY + UnitZ * UnitZ)));
	if(isNaN(radV)) radV = 0;
	var degV = radV / Math.PI * 180;
	if (CTz > 0) degV = 360 - degV;
	while (degV >= 360) {
		degV = degV - 360;
	}

	degH = Math.round(degH);
	degV = Math.round(degV);

	while (degH >= 360) {
		degH = degH - 360;
	}
	while (degV >= 360) {
		degV = degV - 360;
	}

//	if(degV%15) degV += (degV%15)>=8?(15-(degV%15)):(degV%15)-15;
//	if(degH%15) degH += (degH%15)>=8?(15-(degH%15)):(degH%15)-15;

//	while (degH >= 360) {
//		degH = degH - 360;
//	}
//	while (degV >= 360) {
//		degV = degV - 360;
//	}

	return {H:degH,V:degV};
}

function calcCameraPos () {
	var eyeLongitudeRadian = agDeg2Rad(m_ag.longitude);
	var eyeLatitudeRadian = agDeg2Rad(m_ag.latitude);
	var eyeTargetDistance = m_ag.distance;

	var target = m_ag.targetPos;
	var eye = m_ag.cameraPos;
	var yAxis = m_ag.upVec;

	var zAxis = new AGVec3d(null, null, null);
	var xAxis = new AGVec3d(null, null, null);
	var tmp0 = new AGVec3d(null, null, null);
	var remind;

	var cEyeLongitude = Math.cos(eyeLongitudeRadian);
	var sEyeLongitude = Math.sin(eyeLongitudeRadian);
	var cEyeLatitude = Math.cos(eyeLatitudeRadian);
	var sEyeLatitude = Math.sin(eyeLatitudeRadian);

	zAxis.x = cEyeLatitude * cEyeLongitude;
	zAxis.y = cEyeLatitude * sEyeLongitude;
	zAxis.z = sEyeLatitude;

	tmp0.x = cEyeLongitude;
	tmp0.y = sEyeLongitude;
	tmp0.z = 0;

	if(parseFloat(zAxis.z) >= parseFloat(m_ag.epsilon)){
		agOuterProductD3( zAxis, tmp0, xAxis );
		agNormalizeD3( xAxis, xAxis );
		agOuterProductD3( zAxis, xAxis, yAxis );
		agNormalizeD3( yAxis, yAxis );
	}
	else if(parseFloat(zAxis.z) < -parseFloat(m_ag.epsilon)){
		agOuterProductD3(tmp0, zAxis, xAxis);
		agNormalizeD3(xAxis, xAxis);
		agOuterProductD3(zAxis, xAxis, yAxis);
		agNormalizeD3(yAxis, yAxis);
	}
	else{ // zAxis.z == 0
		remind =  Math.round(m_ag.latitude) % 360;
		remind = remind < 0 ? -remind : remind;

		if( remind > 175 && remind < 185 ){
			yAxis.x = 0;
			yAxis.y = 0;
			yAxis.z = -1;
		}else{
			yAxis.x = 0;
			yAxis.y = 0;
			yAxis.z = 1;
		}
	}

	eye.x = parseFloat(zAxis.x) * parseFloat(eyeTargetDistance) + parseFloat(target.x);
	eye.y = parseFloat(zAxis.y) * parseFloat(eyeTargetDistance) + parseFloat(target.y);
	eye.z = parseFloat(zAxis.z) * parseFloat(eyeTargetDistance) + parseFloat(target.z);

	var posDif = parseFloat(888.056);
	var tmpDeg = calcRotateDeg();
	if (tmpDeg.H == 0 && tmpDeg.V == 0) {
		m_ag.cameraPos.x = m_ag.targetPos.x;
		m_ag.cameraPos.y = m_ag.targetPos.y - posDif;
		m_ag.cameraPos.z = m_ag.targetPos.z;
	} else if (tmpDeg.H == 90 && tmpDeg.V == 0) {
		m_ag.cameraPos.x = m_ag.targetPos.x + posDif;
		m_ag.cameraPos.y = m_ag.targetPos.y;
		m_ag.cameraPos.z = m_ag.targetPos.z;
	} else if (tmpDeg.H == 180 && tmpDeg.V == 0) {
		m_ag.cameraPos.x = m_ag.targetPos.x;
		m_ag.cameraPos.y = m_ag.targetPos.y + posDif;
		m_ag.cameraPos.z = m_ag.targetPos.z;
	} else if (tmpDeg.H == 270 && tmpDeg.V == 0) {
		m_ag.cameraPos.x = m_ag.targetPos.x - posDif;
		m_ag.cameraPos.y = m_ag.targetPos.y;
		m_ag.cameraPos.z = m_ag.targetPos.z;
	}
}

function setCameraAndTarget (cam, tar, upVec, isInitData) {
	var tc = new AGVec3d(null, null, null);	// camera  -> target
	agDifferenceD3(cam, tar, tc);
	var tc_len = agInnerProductD3(tc, tc);
	tc_len = Math.sqrt(tc_len);
	if (agIsZero(tc_len)) {
		return false;
	}

	var ntc = new AGVec3d(null, null, null);	// |camera  -> target|
	var inv_tc_len = 1 / tc_len;
	ntc.x = tc.x * inv_tc_len;
	ntc.y = tc.y * inv_tc_len;
	ntc.z = tc.z * inv_tc_len;

	var vz = new AGVec3d(0, 0, 1); // zaxis

	// calc latitude
	var latitude = 90;
	if (upVec.z >= 0) {
		latitude = 90 - agRad2Deg(Math.acos(agInnerProductD3(ntc, vz)));
	} else {
		latitude = 90 + agRad2Deg(Math.acos(agInnerProductD3(ntc, vz)));
	}

	// calc longitude
	var longitude = 0;
	var ntc_xy = new AGVec3d(tc.x, tc.y, 0);

	if (agNormalizeD3(ntc_xy, ntc_xy)) {
		var vx = new AGVec3d(1, 0, 0);
		if (upVec.z >= 0) {
		} else {
			ntc_xy.x = -ntc_xy.x;
			ntc_xy.y = -ntc_xy.y;
			ntc_xy.z = 0;
		}
		var tmp = agRad2Deg(Math.acos(agInnerProductD3(ntc_xy, vx)));
		if (ntc_xy.y >= 0) {
			longitude = tmp;
		} else {
			longitude = -tmp;
		}
	} else {
		var vx = new AGVec3d(1, 0, 0);
		var nup_xy = new AGVec3d(null, null, null);
		if (ntc.z >= 0) {
			nup_xy.x = -upVec.x;
			nup_xy.y = -upVec.y;
			nup_xy.z = 0;
		} else {
			nup_xy.x = upVec.x;
			nup_xy.y = upVec.y;
			nup_xy.z = 0;
		}
		if (!agNormalizeD3(nup_xy, nup_xy)) {
		}
		var tmp = agRad2Deg(Math.acos(agInnerProductD3(nup_xy, vx)));
		if (nup_xy.y >= 0) {
			longitude = tmp;
		} else {
			longitude = -tmp;
		}
	}

	m_ag.targetPos.x = tar.x;
	m_ag.targetPos.y = tar.y;
	m_ag.targetPos.z = tar.z;
	m_ag.distance = tc_len;

	m_ag.longitude = longitude;
	m_ag.latitude = latitude;

	calcCameraPos();

	if (isInitData) {
		agCopyD3 (m_ag.targetPos, m_ag.initTargetPos);
		m_ag.initLongitude = m_ag.longitude;
		m_ag.initLatitude = m_ag.latitude;
		m_ag.initDistance = m_ag.distance;
	}
	return true;
}

function setYRange (yRange, isInitData) {
	if (yRange > m_ag.Camera_YRange_Min) {
		m_ag.orthoYRange = yRange;
		if (isInitData) {
			m_ag.initOrthoYRange = yRange;
		}
		return true;
	} else {
		return false;
	}
}

function changeYRange (d, base) {
	var ratio = 1.0;
	if (d > 0) {
		ratio = Math.pow(base, d);
	} else if (d < 0) {
		ratio = Math.pow(base, d);
	}
	var tmp = m_ag.orthoYRange * ratio;
	if (tmp < m_ag.Camera_YRange_Min) {
		tmp = m_ag.Camera_YRange_Min;
	}
	m_ag.orthoYRange = tmp;
}

function setNear (nearClip) {
	m_ag.nearClip = nearClip;
	return true;
}

function setFar (farClip) {
	m_ag.farClip = farClip;
	return false;
}

function addLongitude (d) {
	m_ag.longitude = m_ag.longitude + d;
	calcCameraPos();
}

function addLatitude (d) {
	m_ag.latitude = m_ag.latitude + d;
	calcCameraPos();
}

function moveTargetByMouseForOrtho (winHeight, dx, dy) {
	var rx = -dx * m_ag.orthoYRange / winHeight;
	var ry = dy * m_ag.orthoYRange / winHeight;

	// latitude
	eyeLongitudeRadian = agDeg2Rad(m_ag.longitude);

	// logitude
	eyeLatitudeRadian = agDeg2Rad(m_ag.latitude);

	var cEyeLongitude = Math.cos(eyeLongitudeRadian);
	var sEyeLongitude = Math.sin(eyeLongitudeRadian);
	var cEyeLatitude = Math.cos(eyeLatitudeRadian);
	var sEyeLatitude = Math.sin(eyeLatitudeRadian);

	var zAxis = new AGVec3d(null, null, null);
	var xAxis = new AGVec3d(null, null, null);
	var yAxis = new AGVec3d(null, null, null);
	var tmp0 = new AGVec3d(null, null, null);
	var remind;

	yAxis.x = cEyeLatitude * cEyeLongitude;
	yAxis.y = cEyeLatitude * sEyeLongitude;
	yAxis.z = sEyeLatitude;

	tmp0.x = cEyeLongitude;
	tmp0.y = sEyeLongitude;
	tmp0.z = 0.0;

	if(yAxis.z >= parseFloat(m_ag.epsilon)){
		agOuterProductD3(yAxis, tmp0, xAxis);
		agOuterProductD3(yAxis, xAxis, zAxis);
	}
	else if(yAxis.z < -parseFloat(m_ag.epsilon)){
		agOuterProductD3(tmp0, yAxis, xAxis);
		agOuterProductD3(yAxis, xAxis, zAxis);
	} else {	// yAxis.z == 0
		remind = Math.round(m_ag.latitude) % 360;
		remind = remind < 0 ? -remind : remind;

		if(remind > 175 && remind < 185){
			zAxis.x = 0.0;
			zAxis.y = 0.0;
			zAxis.z = -1.0;
		}else{
			zAxis.x = 0.0;
			zAxis.y = 0.0;
			zAxis.z = 1.0;
		}
		agOuterProductD3(zAxis, yAxis, xAxis);
	}

	var norm = new AGVec3d(null, null, null);
	if(agNormalizeD3(xAxis, norm)) {
		agCopyD3(norm, xAxis);
	}
	if(agNormalizeD3(zAxis, norm)) {
		agCopyD3(norm, zAxis);
	}

	m_ag.targetPos.x = parseFloat(m_ag.targetPos.x) + parseFloat(xAxis.x * rx) + parseFloat(zAxis.x * ry);
	m_ag.targetPos.y = parseFloat(m_ag.targetPos.y) + parseFloat(xAxis.y * rx) + parseFloat(zAxis.y * ry);
	m_ag.targetPos.z = parseFloat(m_ag.targetPos.z) + parseFloat(xAxis.z * rx) + parseFloat(zAxis.z * ry);

	calcCameraPos();
}

function changeYRange (d, base) {
	var ratio = 1.0;
	if (d > 0) {
		ratio = Math.pow(base, d);
	} else if (d < 0) {
		ratio = Math.pow(base, d);
	}
	var tmp = m_ag.orthoYRange * ratio;
	if (tmp < m_ag.Camera_YRange_Min) {
		tmp = m_ag.Camera_YRange_Min;
	}
	m_ag.orthoYRange = tmp;
}

function calcRotateAxisDeg (upVec) {

	var V = [upVec.x,upVec.y,upVec.z];

	var X = [1.0,0.0,0.0];// Ｘ軸方向ベクトル
	var Y = [0.0,1.0,0.0];// Ｙ軸方向ベクトル
	var Z = [0.0,0.0,1.0];// Ｚ軸方向ベクトル
	var XV,YV,ZV,VV; //_内積
	var VL;          //_|V|
	var k;           //_x,y,zインデクス
	var pi;          //_円周率
	var rx,ry,rz;    //_ラヂアン
	var dx,dy,dz;    //_度

	//_内積の計算
	XV = YV = ZV = VV = 0;
	for(k=0;k<3;k++){
		XV += X[k]*V[k];
		YV += Y[k]*V[k];
		ZV += Z[k]*V[k];
		VV += V[k]*V[k];
	}
	//_角度の計算
	VL = Math.sqrt(VV);
	rx = Math.acos(XV/VL);
	ry = Math.acos(YV/VL);
	rz = Math.acos(ZV/VL);
	//_ラヂアン→度換算
	pi = Math.PI;
	dx = 180*rx/pi;
	dy = 180*ry/pi;
	dz = 180*rz/pi;
	//_表示
//	_dump("X=["+rx+"]["+dx+"]");
//	_dump("Y=["+ry+"]["+dy+"]");
//	_dump("Z=["+rz+"]["+dz+"]");


	var degH = 0;
	var degV = 0;

	var CTx = upVec.x;
	var CTy = upVec.y;
	var CTz = upVec.z;

//	_dump("CTx=["+CTx+"]");
//	_dump("CTy=["+CTy+"]");
//	_dump("CTz=["+CTz+"]");

	// Calculate Rotate H
	var radH = Math.acos(CTy / Math.sqrt(CTx*CTx + CTy * CTy));
//	_dump("radH=["+radH+"]");
	if(isNaN(radH)) radH = 0;
	var degH = radH / Math.PI * 180;

	// Calculate Rotate V
	var UnitX = -1 * Math.sin(degH / 180 * Math.PI);
	var UnitY = Math.cos(degH / 180 * Math.PI);
	var UnitZ = 0;
	var radV = Math.acos((CTx * UnitX + CTy * UnitY + CTz * UnitZ) / Math.sqrt((CTx * CTx + CTy * CTy + CTz * CTz) * (UnitX * UnitX + UnitY * UnitY + UnitZ * UnitZ)));
	if(isNaN(radV)) radV = 0;
	var degV = radV / Math.PI * 180;

//	_dump("deg=["+degH+"]["+degV+"]");


	return {H:degH,V:degV};
}

/////////////////////////////////////////////////////////////////////////////////////////////////////
function load_ag_img(e) {
	try{Ext.getCmp('anatomography-image').loadMask.hide();}catch(e){}
	var date = new Date();
//_dump("_updateAnatomo():time2=["+glb_time+"]["+date.getTime()+"]");
	var time = date.getTime() - glb_time;
	date.setTime(time);
	var s = date.getSeconds();
	var ms = date.getMilliseconds();
//_dump("_updateAnatomo():img=[load]:"+s+"."+ms);

//_dump("_updateAnatomo():img=[load]:"+params);
	setImageTransform('scale(1) translate(0px,0px)');
	var elemImg = Ext.get('ag_img');
	glbImgXY = elemImg.getXY();

	ag_put_usersession_task.delay(1000);
}
function _updateAnatomo (loadMask) {
	if(Ext.isEmpty(loadMask)) loadMask = true;
	glb_anatomo_image_url='';
	glb_anatomo_editor_url='';

	glb_anatomo_image_still = '';
	glb_anatomo_image_rotate = '';

//	glb_anatomo_embedded_url='';

//	try{Ext.getCmp('anatomography-image').loadMask.show();}catch(e){}
	try{
		var img = Ext.getDom('ag_img');
		if(img && img.src){
			var params = makeAnatomoPrm();
//_dump("_updateAnatomo():anatomoImgEvent=["+anatomoImgEvent+"]");
			if(!anatomoImgEvent){
				var elem = Ext.get('ag_img');
				if(elem){

					if(Ext.isGecko){
						var base_div = Ext.get('anatomography-image-contentEl');
						Ext.EventManager.on(base_div,"mousedown", function(e,t) {anatomoImgMouseDown(e,t);});
						Ext.EventManager.on(base_div,"mousemove", function(e,t) {anatomoImgMouseMove(e,t);});
						Ext.EventManager.on(base_div,"mouseup",   function(e,t) {anatomoImgMouseUp(e,t);});
						Ext.EventManager.on(base_div,"mouseout",  function(e,t) {anatomoImgMouseOut(e,t);});
						Ext.EventManager.on(base_div,"mousewheel",function(e,t) {anatomoImgMouseWheel(e,t);});
						Ext.EventManager.on(base_div,"dblclick",  function(e,t) {anatomoImgDblClick(e,t);});
					}else{
						elem.on("mousedown", function(e,t) {anatomoImgMouseDown(e,t);});
						elem.on("mousemove", function(e,t) {anatomoImgMouseMove(e,t);});
						elem.on("mouseup",   function(e,t) {anatomoImgMouseUp(e,t);});
						elem.on("mouseout",  function(e,t) {anatomoImgMouseOut(e,t);});
						elem.on("mousewheel",function(e,t) {anatomoImgMouseWheel(e,t);});
						elem.on("dblclick",  function(e,t) {anatomoImgDblClick(e,t);});
					}

					elem.on("abort", function(e) {
//_dump("_updateAnatomo():ag_img:abort()");
						try{Ext.getCmp('anatomography-image').loadMask.hide();}catch(e){}
						var img = Ext.getDom('ag_img');
						if(img){
							img.src = "resources/images/default/s.gif";
							setImageTransform('scale(1) translate(0px,0px)');
						}
						Ext.Msg.show({
							title: get_ag_lang('TITLE_AG'),
							buttons: Ext.Msg.OK,
							closable: false,
							icon: Ext.Msg.ERROR,
							modal : true,
							msg : 'Image loading aborted.'
						});
					});
					elem.on("error", function(e){
//_dump("_updateAnatomo():ag_img:error()");
						try{Ext.getCmp('anatomography-image').loadMask.hide();}catch(e){}
						var img = Ext.getDom('ag_img');
						if(img){
							img.src = "resources/images/default/s.gif";
							setImageTransform('scale(1) translate(0px,0px)');
						}
						var error_params = makeAnatomoPrm();
						var params = Ext.urlDecode(error_params,true);
						if(Ext.isEmpty(params.oid001)) return;//部品未指定時のエラーは何もしない
						Ext.Ajax.request({
							url:cgipath.image,
							params: Ext.urlDecode(error_params, true),
							method: 'POST',
							callback: function(options,success,response){
//_dump("success=["+success+"]");
								if(success) return;

								var msg = 'Failed to load the image.';
								if(!success){
									msg += ' [' + response.status + ':' + response.statusText + ']';
									Ext.Msg.show({
										title:' ',
										buttons: Ext.Msg.OK,
										closable: false,
										icon: Ext.Msg.ERROR,
										modal : true,
										msg : msg
									});
								}
							}
						});
					});
					elem.on("load", load_ag_img);
				}
				anatomoImgEvent = true;
			}

			_loadAnatomo(params,loadMask);
		}

//		glb_anatomo_image_url = img.src;
		try{
//			var editURL = img.src;
			var editURL = getEditUrl();
			editURL += cgipath.image;

//			editURL = editURL.replace(/#.*/, "");
//			editURL = editURL.replace(/\?.*/, "");

			glb_anatomo_image_still = glb_anatomo_image_rotate = makeAnatomoPrm();

			glb_anatomo_image_url = editURL + "?" + glb_anatomo_image_still;

//_dump("glb_anatomo_image_url=["+glb_anatomo_image_url+"]");
//			_dump("_updateAnatomo():1334");
//			img.src = "css/loading.gif";
		}catch(e){}
	}catch(e){
		if(e.name && e.message){
//			alert("_updateAnatomo():"+e.name+":"+e.message);
//			_dump("_updateAnatomo():"+e.name+":"+e.message);
		}else{
//			alert("_updateAnatomo():"+e);
//			_dump("_updateAnatomo():"+e);
		}
		try{img.src = "resources/images/default/s.gif";}catch(e){}
//		_dump("_updateAnatomo():1344");
	}
	try{
		var editURL = getEditUrl();
		editURL += "?tp_ap=" + encodeURIComponent(makeAnatomoPrm(1));
		glb_anatomo_editor_url = editURL;
//		glb_anatomo_embedded_url = getEmbedIFrameUrl(editURL);
	}catch(e){}

//	try{Ext.getCmp('anatomography-image').loadMask.hide();}catch(e){}
}

function getEmbedIFrameUrl(editURL){
	return '<iframe width="425" height="350" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="'+editURL+'"></iframe><br />'+get_ag_lang('LICENSE_EMBED')+'<br /><small><a href="'+editURL+'" target="_blank" style="color:#0000FF;text-align:left">'+get_ag_lang('ANATOMO_OPEN')+'</a></small>';
}
function getEmbedImgUrl(editURL){
	return '<img src="'+editURL+'"><br />'+get_ag_lang('LICENSE_EMBED');
}
function getEmbedAUrl(editURL){
	return '<a href="'+editURL+'">BodyParts3D</a>';
}

function getEditUrl(){
	var editURL = document.URL;
	return editURL.replace(/#.*/, "").replace(/\?.*/, "").replace(/[^\/]+$/, "");
}

function setRotateHorizontalValue(value) {
	value = (isNaN(value))?0:parseInt(value);

//	var span = document.getElementById("rotateH");
//	span.setAttribute("value", value);
//	span.innerHTML = value;

	var prm_record = ag_param_store.getAt(0);
	prm_record.beginEdit();
	prm_record.set('rotate_h', value);
	prm_record.endEdit();
	prm_record.commit();

	try{Ext.getCmp("rotateH").setValue(value);}catch(e){}
}

function setRotateVerticalValue(value) {
	value = (isNaN(value))?0:parseInt(value);

//	var span = document.getElementById("rotateV");
//	span.setAttribute("value", value);
//	span.innerHTML = value;

	var prm_record = ag_param_store.getAt(0);
	prm_record.beginEdit();
	prm_record.set('rotate_v', value);
	prm_record.endEdit();
	prm_record.commit();

	try{Ext.getCmp("rotateV").setValue(value);}catch(e){}
}

function getRotateHorizontalValue() {
//	var span = document.getElementById("rotateH");
//	span.setAttribute("value", deg);
//	span.innerHTML = deg;
	try{
		return parseInt(Ext.getCmp("rotateH").getValue());
	}catch(e){
		var prm_record = ag_param_store.getAt(0);
		return prm_record.data.rotate_h;
	}
}

function getRotateVerticalValue() {
//	var span = document.getElementById("rotateV");
//	span.setAttribute("value", deg);
//	span.innerHTML = deg;
	try{
		return parseInt(Ext.getCmp("rotateV").getValue());
	}catch(e){
		var prm_record = ag_param_store.getAt(0);
		return prm_record.data.rotate_v;
	}
}

function makeRotImgDiv () {
	return;
	rotImgDiv = document.createElement("div");
	rotImgDiv.setAttribute("id", "rotImgDiv");
	rotImgDiv.setAttribute("align", "center");
	rotImgDiv.style.position = 'absolute';
	rotImgDiv.style.border = '1px solid #3c3c3c';
	rotImgDiv.style.background = '#f0f0f0';
	rotImgDiv.style.MozOpacity = 0.75;
	rotImgDiv.style.opacity = 0.75;
	rotImgDiv.style.filter = "alpha(opacity='75')";
	rotImgDiv.style.width = "80px";
	rotImgDiv.style.height = "80px";
	rotImgDiv.style.backgroundImage = "url('img/rotImg.png')";
	rotImgDiv.style.backgroundRepeat = "no-repeat";
	rotImgDiv.style.visibility = "hidden";
	rotImgDiv.style.left = "-100px";
	rotImgDiv.style.top = "-100px";
	document.body.appendChild(rotImgDiv);
}

function anatomoImgMoveCenter(x,y){
	var centerX = parseInt((ag_param_store.getAt(0).data.image_w /2) -  x);
	var centerY = parseInt((ag_param_store.getAt(0).data.image_h /2) -  y);
	var image_h = ag_param_store.getAt(0).data.image_h;
	var zoom = ag_param_store.getAt(0).data.zoom;
	moveTargetByMouseForOrtho(image_h, centerX / parseFloat(Math.pow(2, zoom)), centerY / parseFloat(Math.pow(2, zoom)));
	setImageTransform('scale(1) translate(' + centerX + 'px, ' + centerY + 'px)',true);
	stopUpdateAnatomo();
	_updateAnatomo();
}
function anatomoImgDblClick(e,t){
//_dump("anatomoImgDblClick():"+t.id);
	if(!t || t.id!='ag_img') return;
	try {
		e.stopPropagation();
		e.preventDefault();
	} catch (ex) {
		e.returnValue = false;
		e.cancelBubble = true;
	}

	var elemImg = Ext.get('ag_img');
	var xyImg = elemImg.getXY();
	var mouseX = e.xy[0] - xyImg[0];
	var mouseY = e.xy[1] - xyImg[1];
	anatomoImgMoveCenter(mouseX,mouseY);
//	var centerX = parseInt((ag_param_store.getAt(0).data.image_w /2) -  mouseX);
//	var centerY = parseInt((ag_param_store.getAt(0).data.image_h /2) -  mouseY);
//	moveTargetByMouseForOrtho(ag_param_store.getAt(0).data.image_h, centerX / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)), centerY / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)));
//	setImageTransform('scale(1) translate(' + centerX + 'px, ' + centerY + 'px)',true);
//	stopUpdateAnatomo();
//	_updateAnatomo();
}

function getFMAID_CSVstr () {
	var retStr = "";
	if (ag_parts_store && ag_parts_store.getCount() > 0) {
		for (var i = 0; i < ag_parts_store.getCount(); i++) {
			if (i > 0) {
				retStr = retStr + ",";
			}
			var record = ag_parts_store.getAt(i);
			retStr = retStr + record.data.f_id;
		}
	}
	return retStr;
}

function makeAnatomoOrganNumber(aNum){
	var num = aNum;
	while ((num+"").length < 3) {
		num = "0" + num;
	}
	return num;
}

function makeAnatomoOrganPointPrm(num,record){
	var prm = "";

	// Point Color
	var colorstr = record.data.color.substr(1, 6);
	if(colorstr.length == 6) prm = prm + "&pocl" + num + "=" + colorstr;

	// Point Remove
	prm = prm + "&porm" + num + "=";
	if (record.data.exclude) {
		prm = prm + "1";
	}else{
		prm = prm + "0";
	}

	// Point Opacity
	prm = prm + "&poop" + num + "=";
//	if(record.data.opacity==0.1){
//		prm = prm + "0.05";
//	}else{
		prm = prm + record.data.opacity;
//	}

	// Point Representation
	if (record.data.representation == "surface") {
		prm = prm + "&pore" + num + "=S";
	} else if (record.data.representation == "wireframe") {
		prm = prm + "&pore" + num + "=W";
	} else if (record.data.representation == "points") {
		prm = prm + "&pore" + num + "=P";
	}

	// Point Sphere
	var prm_record = ag_param_store.getAt(0);
	prm = prm + "&posh" + num + "=" + prm_record.data.point_sphere;

	return prm;
}

function isNumber(v){
	return((typeof v)==='number' && isFinite(v));
}

function roundPrm(value){
	try{if(!isNumber(value)) value = Number(value);}catch(e){}
	return Math.round(value*10000)/10000;
}

function truncationPrm(value){
	try{if(!isNumber(value)) value = Number(value);}catch(e){}
	return parseInt(value*10000)/10000;
}

function makeAnatomoPrm_Pin(record,anatomo_pin_shape_combo_value,coordinate_system,properties){

	if(window.ag_extensions && ag_extensions.global_pin && ag_extensions.global_pin.makeAnatomoPrm){
		return ag_extensions.global_pin.makeAnatomoPrm(arguments);
	}

	if(Ext.isEmpty(record) || Ext.isEmpty(record.data)) return undefined;

	properties = properties || {};
	var data = Ext.apply({},properties,record.data);

	if(Ext.isEmpty(anatomo_pin_shape_combo_value)){
		try{
			anatomo_pin_shape_combo_value = Ext.getCmp("anatomo_pin_shape_combo").getValue();
		}catch(e){
			anatomo_pin_shape_combo_value = init_anatomo_pin_shape;
		}
	}

	//coordinate_system
	if(Ext.isEmpty(coordinate_system)){
		try{
			coordinate_system = Ext.getCmp("ag-coordinate-system-combo").getValue();
		}catch(e){
			coordinate_system = prm_record.data.coord;
		}
	}
	var prm = '';
	try{
		var no = parseInt(data.no);
		var num = makeAnatomoOrganNumber(no);
		// No
		prm = prm + "pno" + num + "=" + no.toString();
		// 3Dx
		prm = prm + "&px" + num + "=" + roundPrm(data.x3d);
		// 3Dy
		prm = prm + "&py" + num + "=" + roundPrm(data.y3d);
		// 3Dz
		prm = prm + "&pz" + num + "=" + roundPrm(data.z3d);
		// ArrVec3Dx
		prm = prm + "&pax" + num + "=" + roundPrm(data.avx3d);
		// ArrVec3Dy
		prm = prm + "&pay" + num + "=" + roundPrm(data.avy3d);
		// ArrVec3Dz
		prm = prm + "&paz" + num + "=" + roundPrm(data.avz3d);
		// UpVec3Dx
		prm = prm + "&pux" + num + "=" + roundPrm(data.uvx3d);
		// UpVec3Dy
		prm = prm + "&puy" + num + "=" + roundPrm(data.uvy3d);
		// UpVec3Dz
		prm = prm + "&puz" + num + "=" + roundPrm(data.uvz3d);

		var pdc=0;
		// Draw Pin Description
		var drawCheck = Ext.getCmp('anatomo_pin_description_draw_check');
		if(drawCheck && drawCheck.rendered){
			if(drawCheck.getValue()){
				prm = prm + "&pdd" + num + "=1";
				prm = prm + "&pdc" + num + "=" + data.color;
				pdc=1;
			}else{
			}
		}else if(init_anatomo_pin_description_draw){
			prm = prm + "&pdd" + num + "=1";
			prm = prm + "&pdc" + num + "=" + data.color;
			pdc=1;
		}

		// Draw Pin Number
		var drawCheck = Ext.getCmp('anatomo_pin_number_draw_check');
		if(drawCheck && drawCheck.rendered){
			if(drawCheck.getValue()){
				prm = prm + "&pnd" + num + "=1";
				if(!pdc) prm = prm + "&pdc" + num + "=" + data.color;
			}else{
			}
		}else if(init_anatomo_pin_number_draw){
			prm = prm + "&pnd" + num + "=1";
			if(!pdc) prm = prm + "&pdc" + num + "=" + data.color;
		}


		// Point Shape
		prm = prm + "&ps" + num + "=" + anatomo_pin_shape_combo_value;
		// ForeRGB
		prm = prm + "&pcl" + num + "=" + data.color;
		// OrganID
		prm = prm + "&poi" + num + "=" + encodeURIComponent(data.oid);
		// OrganName
		prm = prm + "&pon" + num + "=" + encodeURIComponent(data.organ);
		// Comment
		prm = prm + "&pd" + num + "=" + (Ext.isEmpty(data.comment) ? '' : encodeURIComponent(data.comment));

		//coordinate_system
		if(!Ext.isEmpty(data.coord)){
			prm = prm + "&pcd" + num + "=" + encodeURIComponent(data.coord);
		}else if(!Ext.isEmpty(coordinate_system)){
			prm = prm + "&pcd" + num + "=" + encodeURIComponent(coordinate_system);
		}
	}catch(e){
		_dump(e);
		prm = undefined;
	}
//	console.log("prm=["+prm+"]");
	return prm;
}

function getDateString () {
	var now = new Date();
	var year = now.getFullYear();
	var mon = now.getMonth() + 1;
	var day = now.getDate();
	var hour = now.getHours();
	var min = now.getMinutes();
	var sec = now.getSeconds();
	if(mon < 10) mon = "0" + mon;
	if(day < 10) day = "0" + day;
	if(hour< 10) hour = "0" + hour;
	if(min < 10) min = "0" + min;
	if(sec < 10) sec = "0" + sec;
	return "" + year + mon + day + hour + min + sec;
}

setImageWindowSize = function(){
	var checkcmp = Ext.getCmp('anatomo-windowsize-autosize-check');
	if(checkcmp && checkcmp.rendered && !checkcmp.getValue()) return;
	var comp = Ext.getCmp('anatomography-image');
	if(!comp || !comp.rendered) return;
	var size = comp.getSize();
	try{
		var w = parseInt(size.width);
//		var w = parseInt((size.width-10)/10)*10;
//		w = (w<100?100:(w>900?900:w));
		w = (w<100?100:w);
		var h = parseInt(size.height);
//		var h = parseInt((size.height-10)/10)*10;
//		h = (h<100?100:(h>900?900:h));
		h = (h<100?100:h);
		var wc = Ext.getCmp('anatomo-width-combo');
		var hc = Ext.getCmp('anatomo-height-combo');
		if(wc && wc.rendered && hc && hc.rendered){
			wc.setValue(w);
			hc.setValue(h);
		}
		var prm_record = ag_param_store.getAt(0);
		prm_record.beginEdit();
		prm_record.set('image_w', w);
		prm_record.set('image_h', h);
		prm_record.endEdit();
		prm_record.commit();
		updateAnatomo();

	}catch(e){
		_dump("setImageWindowSize():"+e);
	}
};

var glb_ConvertIdList_transactionId = null;
getConvertIdList = function(records,store,callback){
//_dump("getConvertIdList():records=["+records.length+"]");
	var recs = [];
	for(var i=0;i<records.length;i++){
		var rec = {
			id      : records[i].id,
			tg_id   : records[i].get('tg_id'),
			tgi_id  : records[i].get('tgi_id'),
			version : records[i].get('version'),
			f_id    : records[i].get('f_id'),
			name_e  : records[i].get('name_e'),

			ci_id   : records[i].get('ci_id'),
			cb_id   : records[i].get('cb_id'),
			bul_id  : records[i].get('bul_id'),
			md_id   : records[i].get('md_id'),
			mv_id   : records[i].get('mv_id'),
			mr_id   : records[i].get('mr_id')
		};
		recs.push(rec);
	}
	var params = {
		parent  : (Ext.isEmpty(gParams.parent)?'':gParams.parent),
		lng     : gParams.lng,
		records : Ext.util.JSON.encode(recs)
	}
	try{
		params.version = Ext.getCmp('bp3d-version-combo').getValue();
//		_dump("getConvertIdList():params.version=["+params.version+"]");
	}catch(e){}
	if(Ext.isEmpty(params.version)) params.version=init_bp3d_version;

	try{
		var bp3d_version_combo = Ext.getCmp('bp3d-version-combo');
		var bp3d_version_store = bp3d_version_combo.getStore();
		var bp3d_version_idx = bp3d_version_store.find('tgi_version',new RegExp('^'+bp3d_version_combo.getValue()+'$'));
		var bp3d_version_rec;
		var bp3d_version_disp_value;
		if(bp3d_version_idx>=0) bp3d_version_rec = bp3d_version_store.getAt(bp3d_version_idx);
		if(bp3d_version_rec){
			params.md_id = bp3d_version_rec.get('md_id');
			params.mv_id = bp3d_version_rec.get('mv_id');
			params.mr_id = bp3d_version_rec.get('mr_id');
		}
	}catch(e){
		if(window.console) console.error(e);
	}
	try{
		var bp3d_tree_combo = Ext.getCmp('bp3d-tree-type-combo');
		var bp3d_tree_store = bp3d_tree_combo.getStore();
		var bp3d_tree_idx = bp3d_tree_store.find('t_type',new RegExp('^'+bp3d_tree_combo.getValue()+'$'));
		var bp3d_tree_rec;
		var bp3d_tree_disp_value;
		if(bp3d_tree_idx>=0) bp3d_tree_rec = bp3d_tree_store.getAt(bp3d_tree_idx);
		if(bp3d_tree_rec){
			params.bul_id = bp3d_tree_rec.get('bul_id');
			params.ci_id = bp3d_tree_rec.get('ci_id');
			params.cb_id = bp3d_tree_rec.get('cb_id');
		}
	}catch(e){
		if(window.console) console.error(e);
	}


	var params = Ext.urlEncode(params)
//_dump("getConvertIdList():params=["+params+"]");

	hideConvIDColumn();

	var window_title = "";
	if(glb_ConvertIdList_transactionId){
		Ext.Ajax.abort(glb_ConvertIdList_transactionId);
	}
	glb_ConvertIdList_transactionId = Ext.Ajax.request({
		url     : 'get-convert-id-list.cgi',
		method  : 'POST',
		params  : params,
		callback: function(options,success,response){
			glb_ConvertIdList_transactionId = null;
			try{
				if(callback) (callback)(success);
			}catch(e){
				_dump("getConvertIdList():callback():"+e);
			}
		},
		success : function(conn,response,options){
			try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
			if(!results || results.success == false){
				var msg = '';
				if(results && results.msg) msg += ' ['+results.msg+' ]';
				Ext.MessageBox.show({
					title   : window_title,
					msg     : msg,
					buttons : Ext.MessageBox.OK,
					icon    : Ext.MessageBox.ERROR
				});
				return;
			}
			try{
				if(results.records){
					try{var tg_id = Ext.getCmp('bp3d-tree-group-combo').getValue();}catch(e){tg_id=init_tree_group;}
					var i;
					for(i=0;i<results.records.length;i++){
						var record = store.getById(results.records[i].id);
						if(Ext.isEmpty(record)){
							var idx = store.find('b_id',new RegExp("^"+results.records[i].b_id+"$"));
							if(idx<0) idx = store.find('f_id',new RegExp("^"+results.records[i].f_id+"$"));
							if(idx<0) continue;
							record = store.getAt(idx);
						}
						record.beginEdit();
						if(results.records[i].conv_id && results.records[i].conv_id instanceof Array){
							record.set('conv_id',results.records[i].conv_id.join(","));
						}else{
							record.set('conv_id',results.records[i].conv_id);
						}
						for(var key in results.records[i]){
							if(key == 'conv_id') continue;
							record.set(key,results.records[i][key]);
						}
						record.commit(true);
						record.endEdit();
					}
					var records = store.getRange();
					store.removeAll();
					store.add(records);
					showConvIDColumn();
				}
				_updateAnatomo();
			}catch(e){
				_dump(e);
			}
		},
		failure : function(conn,response,options){
			try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
			var msg = '[';
			if(results && results.msg){
				msg += results.msg+' ]';
			}else{
				msg += conn.status+" "+conn.statusText+' ]';
			}
			Ext.MessageBox.show({
				title   : window_title,
				msg     : msg,
				buttons : Ext.MessageBox.OK,
				icon    : Ext.MessageBox.ERROR
			});
		}
	});
};

load_bp3d_contents_store = function(self,records,options){
_dump("load_bp3d_contents_store():records=["+records.length+"]");
_dump("load_bp3d_contents_store():["+Ext.isEmpty(gParams.tp_ap)+"]");
	try{reset_func();}catch(e){}
//	try{
		if(!Ext.isEmpty(gParams.tp_ap)){
			var tp_ap = gParams.tp_ap;
//						delete gParams.tp_ap;

			var tpap_param = analyzeTPAP(tp_ap);
			if(!tpap_param) return;
//_dump("bp3d_contents_store.load():tpap_param.parts=["+(tpap_param.parts?tpap_param.parts.length:0)+"]");

			var contents_tabs = Ext.getCmp('contents-tab-panel');

//2011-09-28 コメントアウト
//2011-09-30 各設定が正しく定義されない為、とりあえずタブをカレントにする
			if(((tpap_param.parts && tpap_param.parts.length>0 && records.length>0) || (tpap_param.pins && tpap_param.pins.length>0)) && contents_tabs){
				if(contents_tabs.getXType()=='tabpanel'){
					contents_tabs.setActiveTab('contents-tab-anatomography-panel');
				}else if(contents_tabs.getXType()=='panel'){
					contents_tabs.getLayout().setActiveItem('contents-tab-anatomography-panel');
				}
			}


			var fma_rec = {};
			for(var i=0,len=records.length;i<len;i++){
				var record = records[i].copy();
				var f_id = record.get('f_id');
				fma_rec[f_id] = record;
//_dump("bp3d_contents_store.load():record=["+i+"]["+record.data.f_id+"]["+record.data.name_e+"]");
			}

			try{var prm_record = (ag_param_store?ag_param_store.getAt(0):undefined);}catch(e){}

//_dump("bp3d_contents_store.load():prm_record.data.clip_depth=["+prm_record.data.clip_depth+"]");

			if(tpap_param.common != null && prm_record != undefined && prm_record != null){
				prm_record.beginEdit();
				if(!Ext.isEmpty(tpap_param.common.method)) prm_record.set('method',tpap_param.common.method);
				if(!Ext.isEmpty(tpap_param.common.viewpoint)) prm_record.set('viewpoint',tpap_param.common.viewpoint);
				if(gParams.tp_md){
					if(!Ext.isEmpty(tpap_param.common.image_w)) prm_record.set('image_w',tpap_param.common.image_w);
					if(!Ext.isEmpty(tpap_param.common.image_h)) prm_record.set('image_h',tpap_param.common.image_h);
				}
				if(!Ext.isEmpty(tpap_param.common.bg_rgb)) prm_record.set('bg_rgb',tpap_param.common.bg_rgb);
				prm_record.set('bg_transparent',Ext.isEmpty(tpap_param.common.bg_transparent)?NaN:0);
				if(!Ext.isEmpty(tpap_param.common.autoscalar_f)) prm_record.set('autoscalar_f',tpap_param.common.autoscalar_f);
				if(!Ext.isEmpty(tpap_param.common.colorbar_f)) prm_record.set('colorbar_f',tpap_param.common.colorbar_f);
				if(!Ext.isEmpty(tpap_param.common.heatmap_f)) prm_record.set('heatmap_f',tpap_param.common.heatmap_f);
				if(!Ext.isEmpty(tpap_param.common.drawsort_f)) prm_record.set('drawsort_f',tpap_param.common.drawsort_f);
				if(!Ext.isEmpty(tpap_param.common.mov_len)) prm_record.set('mov_len',tpap_param.common.mov_len);
				if(!Ext.isEmpty(tpap_param.common.mov_fps)) prm_record.set('mov_fps',tpap_param.common.mov_fps);

				if(gParams.tp_md){
					if(!Ext.isEmpty(tpap_param.common.image_w)){
						var elemW = Ext.getCmp('anatomo-width-combo');
						if(elemW && elemW.rendered) elemW.setValue(tpap_param.common.image_w);
					}
					if(!Ext.isEmpty(tpap_param.common.image_h)){
						var elemH = Ext.getCmp('anatomo-height-combo');
						if(elemH && elemH.rendered) elemH.setValue(tpap_param.common.image_h);
					}
					if(!Ext.isEmpty(tpap_param.common.image_w) || !Ext.isEmpty(tpap_param.common.image_h)){
						var elemC = Ext.getCmp('anatomo-windowsize-autosize-check');
						if(elemC && elemC.rendered) elemC.setValue(false);
					}
				}

				var elemBGCOLOR = Ext.getCmp('anatomo-bgcp');
				if(elemBGCOLOR && elemBGCOLOR.rendered) elemBGCOLOR.setValue('#'+tpap_param.common.bg_rgb);

				var elemBGTransparent = Ext.getCmp('anatomo-bgcolor-transparent-check');
				if(elemBGTransparent && elemBGTransparent.rendered) elemBGTransparent.setValue(Ext.isEmpty(tpap_param.common.bg_transparent)?false:true);

				if(!Ext.isEmpty(tpap_param.common.rotate_h) && !Ext.isEmpty(tpap_param.common.rotate_v)){
					setRotateHorizontalValue(tpap_param.common.rotate_h);
					setRotateVerticalValue(tpap_param.common.rotate_v);
					if(Ext.isEmpty(gParams.tp_md) || gParams.tp_md != 1){
						if(updateRotateImg) updateRotateImg();
					}
				}

				if(!Ext.isEmpty(tpap_param.common.scalar_max)){
					prm_record.set('scalar_max',tpap_param.common.scalar_max);
					var elem = Ext.getCmp('scalar-max-textfield');
					if(elem && elem.rendered) elem.setValue(tpap_param.common.scalar_max);
				}
				if(!Ext.isEmpty(tpap_param.common.scalar_min)){
					prm_record.set('scalar_min',tpap_param.common.scalar_min);
					var elem = Ext.getCmp('scalar-min-textfield');
					if(elem && elem.rendered) elem.setValue(tpap_param.common.scalar_min);
				}
				if(!Ext.isEmpty(tpap_param.common.colorbar_f) && parseInt(tpap_param.common.colorbar_f)>0){
					var elem = Ext.getCmp('show-colorbar-check');
					if(elem && elem.rendered) elem.setValue(true);
				}
				if(!Ext.isEmpty(tpap_param.common.heatmap_f) && parseInt(tpap_param.common.heatmap_f)>0){
					var elem = Ext.getCmp('show-heatmap-check');
					if(elem && elem.rendered) elem.setValue(true);
				}

//_dump("bp3d_contents_store.load():tpap_param.common.zoom=["+tpap_param.common.zoom+"]");
				if(!Ext.isEmpty(tpap_param.common.zoom)){
					prm_record.set('zoom',parseFloat(tpap_param.common.zoom));
					glb_zoom_slider = prm_record.data.zoom*5+1;
//_dump("bp3d_contents_store.load():glb_zoom_slider=["+glb_zoom_slider+"]");
//								var cmp = Ext.getCmp('zoom-value-text');
//								if(cmp && cmp.rendered) cmp.setValue(glb_zoom_slider+1);
					var cmp = Ext.getCmp('zoom-slider');
					if(cmp && cmp.rendered){
						cmp.setValue(glb_zoom_slider-1);
						ag_command_zoom_menu_slider_syncThumb_task.delay(1000);
					}
				}
				if(!Ext.isEmpty(tpap_param.common.move_x)) prm_record.set('move_x',tpap_param.common.move_x);
				if(!Ext.isEmpty(tpap_param.common.move_y)) prm_record.set('move_y',tpap_param.common.move_y);
				if(!Ext.isEmpty(tpap_param.common.move_z)) prm_record.set('move_z',tpap_param.common.move_z);
				if(!Ext.isEmpty(tpap_param.common.clip_depth)) prm_record.set('clip_depth',tpap_param.common.clip_depth);
				if(!Ext.isEmpty(tpap_param.common.clip_method)) prm_record.set('clip_method',tpap_param.common.clip_method);

				if(!Ext.isEmpty(tpap_param.common.bp3d_version)){
					init_bp3d_version = tpap_param.common.bp3d_version;
//_dump("bp3d_contents_store.load():init_bp3d_version=["+init_bp3d_version+"]");
					if(tpap_param.common.tg_id){
						init_tree_group = tpap_param.common.tg_id;
					}else if(tpap_param.common.model && model2tg[tpap_param.common.model]){
						init_tree_group = model2tg[tpap_param.common.model].tg_id;
					}else if(version2tg[init_bp3d_version] && version2tg[init_bp3d_version].tg_id){
						init_tree_group = version2tg[init_bp3d_version].tg_id;
					}
					if(version2tg[init_bp3d_version].tgi_delcause){
						if(Ext.isEmpty(latestversion[init_tree_group])) return;
						init_bp3d_version = latestversion[init_tree_group];
					}
//_dump("bp3d_contents_store.load():init_bp3d_version=["+init_bp3d_version+"]");

					var cmp = Ext.getCmp('bp3d-version-combo');
					if(cmp && cmp.rendered) cmp.setValue(init_bp3d_version);
					var cmp = Ext.getCmp('anatomo-version-combo');
					if(cmp && cmp.rendered) cmp.setValue(init_bp3d_version);
				}

				if(!Ext.isEmpty(tpap_param.common.grid)){
					prm_record.set('grid',tpap_param.common.grid);
					var elem = Ext.getCmp('ag-command-grid-show-check');
					if(elem && elem.rendered) elem.setValue(tpap_param.common.grid=='1'?true:false);
				}
				if(!Ext.isEmpty(tpap_param.common.grid_color)){
					var elem = Ext.getCmp('ag-command-grid-color-field');
					if(elem && elem.rendered) elem.setValue('#'+tpap_param.common.grid_color);
					prm_record.set('grid_color', tpap_param.common.grid_color);
				}
				if(!Ext.isEmpty(tpap_param.common.grid_len)){
					var elem = Ext.getCmp('ag-command-grid-len-combobox');
					if(elem && elem.rendered) elem.setValue(tpap_param.common.grid_len);
					prm_record.set('grid_len', tpap_param.common.grid_len);
				}

				if(Ext.isEmpty(tpap_param.common.coord)) tpap_param.common.coord = 'bp3d';
//_dump("bp3d_contents_store.load():tpap_param.common.coord=["+tpap_param.common.coord+"]");
				var elem = Ext.getCmp('ag-coordinate-system-combo');
				if(elem && elem.rendered){
					elem.setValue(tpap_param.common.coord);
//_dump("bp3d_contents_store.load():elem.getValue=["+elem.getValue()+"]");
				}
				prm_record.set('coord',tpap_param.common.coord);


				if(Ext.isEmpty(tpap_param.common.color_rgb)) tpap_param.common.color_rgb = 'f0d2a0';
				var elem = Ext.getCmp('anatomo-default-parts-color');
				if(elem && elem.rendered) elem.setValue(tpap_param.common.color_rgb);
				prm_record.set('color_rgb',tpap_param.common.color_rgb);

				if(Ext.isEmpty(tpap_param.common.point_color_rgb)) tpap_param.common.point_color_rgb = '0000ff';
				var elem = Ext.getCmp('anatomo-default-point-parts-color');
				if(elem && elem.rendered) elem.setValue(tpap_param.common.point_color_rgb);
				prm_record.set('point_color_rgb',tpap_param.common.point_color_rgb);

				if(!Ext.isEmpty(tpap_param.common.point_desc)){
					prm_record.set('point_desc',tpap_param.common.point_desc);
					var elem = Ext.getCmp('ag-command-point-description-check');
					if(elem && elem.rendered) elem.setValue(tpap_param.common.point_desc);
				}
				if(!Ext.isEmpty(tpap_param.common.point_pin_line)){
					init_anatomo_pin_description_line = tpap_param.common.point_pin_line;
					prm_record.set('point_pin_line',tpap_param.common.point_pin_line);
					var elem = Ext.getCmp('anatomo_pin_description_draw_pin_indication_line_combo');
					if(elem && elem.rendered) elem.setValue(tpap_param.common.point_pin_line);
				}
				if(!Ext.isEmpty(tpap_param.common.point_point_line)){
					prm_record.set('point_point_line',tpap_param.common.point_point_line);
					var elem = Ext.getCmp('ag-command-point-description-draw-point-indication-line-combo');
					if(elem && elem.rendered) elem.setValue(tpap_param.common.point_point_line);
				}
				if(!Ext.isEmpty(tpap_param.common.point_sphere)){
					prm_record.set('point_sphere',tpap_param.common.point_sphere);
					var elem = Ext.getCmp('ag-command-point-sphere-combo');
					if(elem && elem.rendered) elem.setValue(tpap_param.common.point_sphere);
				}


				//PIN関連
				if(!Ext.isEmpty(tpap_param.common.pin)){
					init_anatomo_pin_description_draw = tpap_param.common.pin ? true : false;
					var elem = Ext.getCmp('anatomo_pin_description_draw_check');
					if(elem && elem.rendered) elem.setValue(init_anatomo_pin_description_draw);
				}
				if(!Ext.isEmpty(tpap_param.common.pinno)){
					init_anatomo_pin_number_draw = tpap_param.common.pinno ? true : false;
					var elem = Ext.getCmp('anatomo_pin_number_draw_check');
					if(elem && elem.rendered) elem.setValue(init_anatomo_pin_number_draw);
				}


				if(!Ext.isEmpty(tpap_param.camera)){
					if(!Ext.isEmpty(tpap_param.camera.cameraPos)){
						m_ag.cameraPos.x = tpap_param.camera.cameraPos.x;
						m_ag.cameraPos.y = tpap_param.camera.cameraPos.y;
						m_ag.cameraPos.z = tpap_param.camera.cameraPos.z;
					}
					if(!Ext.isEmpty(tpap_param.camera.targetPos)){
						m_ag.targetPos.x = tpap_param.camera.targetPos.x;
						m_ag.targetPos.y = tpap_param.camera.targetPos.y;
						m_ag.targetPos.z = tpap_param.camera.targetPos.z;
					}
					if(!Ext.isEmpty(tpap_param.camera.upVec)){
						m_ag.upVec.x = tpap_param.camera.upVec.x;
						m_ag.upVec.y = tpap_param.camera.upVec.y;
						m_ag.upVec.z = tpap_param.camera.upVec.z;
					}
//_dump("m_ag.targetPos.x=["+(typeof m_ag.targetPos.x)+"]["+m_ag.targetPos.x+"]");
//_dump("m_ag.cameraPos=["+m_ag.cameraPos.x+"]["+m_ag.cameraPos.y+"]["+m_ag.cameraPos.z+"]");
//_dump("m_ag.targetPos=["+m_ag.targetPos.x+"]["+m_ag.targetPos.y+"]["+m_ag.targetPos.z+"]");
//_dump("m_ag.upVec=["+m_ag.upVec.x+"]["+m_ag.upVec.y+"]["+m_ag.upVec.z+"]");

					if(!Ext.isEmpty(tpap_param.camera.cameraPos) && !Ext.isEmpty(tpap_param.camera.targetPos) && !Ext.isEmpty(tpap_param.camera.upVec)){
						setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);

						var deg = calcRotateDeg();
						tpap_param.common.rotate_h = deg.H;
						tpap_param.common.rotate_v = deg.V;
						setRotateHorizontalValue(deg.H);
						setRotateVerticalValue(deg.V);

						if(Ext.isEmpty(gParams.tp_md) || gParams.tp_md != 1){
							if(updateRotateImg) updateRotateImg();
						}
					}
				}

				if(!Ext.isEmpty(tpap_param.clip) && !Ext.isEmpty(tpap_param.clip.type) && tpap_param.clip.type != 'N'){
					if(!Ext.isEmpty(tpap_param.clip.type))   prm_record.set('clip_type',tpap_param.clip.type);
					if(!Ext.isEmpty(tpap_param.clip.depth))  prm_record.set('clip_depth',parseFloat(tpap_param.clip.depth));
					if(!Ext.isEmpty(tpap_param.clip.method)) prm_record.set('clip_method',tpap_param.clip.method);
					if(!Ext.isEmpty(tpap_param.clip.paramA)) prm_record.set('clip_paramA',parseFloat(tpap_param.clip.paramA));
					if(!Ext.isEmpty(tpap_param.clip.paramB)) prm_record.set('clip_paramB',parseFloat(tpap_param.clip.paramB));
					if(!Ext.isEmpty(tpap_param.clip.paramC)) prm_record.set('clip_paramC',parseFloat(tpap_param.clip.paramC));
					if(!Ext.isEmpty(tpap_param.clip.paramD)) prm_record.set('clip_paramD',parseFloat(tpap_param.clip.paramD));

					if(prm_record.data.clip_paramA != 0 && prm_record.data.clip_paramB != 0 && prm_record.data.clip_paramB != 0){
					}else{
						if(prm_record.data.clip_paramB){
							prm_record.set('clip_depth', (tpap_param.clip.paramD*prm_record.data.clip_paramB));
						}else if(prm_record.data.clip_paramA){
							prm_record.set('clip_depth', (tpap_param.clip.paramD*prm_record.data.clip_paramA));
						}else if(prm_record.data.clip_paramC){
							prm_record.set('clip_depth', (tpap_param.clip.paramD*prm_record.data.clip_paramC));
						}
						prm_record.set('clip_depth', tpap_param.clip.paramD);
					}

					var anatomo_clip_check = Ext.getCmp('anatomo-clip-check');
					var anatomo_clip_method_combo = Ext.getCmp('anatomo-clip-method-combo');
					var anatomo_clip_predifined_plane = Ext.getCmp('anatomo-clip-predifined-plane');
					var anatomo_clip_fix_check = Ext.getCmp('anatomo-clip-fix-check');
					var anatomo_clip_reverse_check = Ext.getCmp('anatomo-clip-reverse-check');
					var anatomo_clip_slider = Ext.getCmp('anatomo-clip-slider');
					var anatomo_clip_value_text = Ext.getCmp('anatomo-clip-value-text');

					var anatomo_clip_slider_up_button = Ext.get('anatomo-clip-slider-up-button');
					var anatomo_clip_slider_down_button = Ext.get('anatomo-clip-slider-down-button');
					var anatomo_clip_text_up_button = Ext.get('anatomo-clip-text-up-button');
					var anatomo_clip_text_down_button = Ext.get('anatomo-clip-text-down-button');
					var anatomo_clip_unit_label = Ext.get('anatomo-clip-unit-label');
					var clipImgDiv = Ext.get('clipImgDiv');

					if(anatomo_clip_check) anatomo_clip_check.un('check',oncheck_anatomo_clip_check);
					if(anatomo_clip_method_combo) anatomo_clip_method_combo.un('select',onselect_anatomo_clip_method_combo);
					if(anatomo_clip_predifined_plane) anatomo_clip_predifined_plane.un('select',onselect_anatomo_clip_predifined_plane);
					if(anatomo_clip_fix_check) anatomo_clip_fix_check.un('check',oncheck_anatomo_clip_fix_check);
					if(anatomo_clip_reverse_check) anatomo_clip_reverse_check.un('check',oncheck_anatomo_clip_reverse_check);
					if(anatomo_clip_slider) anatomo_clip_slider.un('change',onchange_anatomo_clip_slider);
					if(anatomo_clip_value_text) anatomo_clip_value_text.un('change',onchange_anatomo_clip_value_text);

					if(anatomo_clip_check && anatomo_clip_check.rendered) anatomo_clip_check.setValue(true);

					var clip = 'FREE';
					var clip_param = 1;
					var clip_depth = 0;
//_dump("anatomo_clip_predifined_plane=["+anatomo_clip_predifined_plane+"]");
					if(anatomo_clip_predifined_plane && anatomo_clip_predifined_plane.rendered){
						if(prm_record.data.clip_paramA != 0 && prm_record.data.clip_paramB != 0 && prm_record.data.clip_paramB != 0){
							clip_param = prm_record.data.clip_paramD;
							clip_depth = Math.round(parseFloat(tpap_param.clip.depth));
							if(anatomo_clip_fix_check && anatomo_clip_fix_check.rendered) anatomo_clip_fix_check.setValue(true);
						}else{
							if(prm_record.data.clip_paramA != 0){
								clip = 'RL';
								clip_param = prm_record.data.clip_paramA;
							}else if(prm_record.data.clip_paramB != 0){
								clip = 'FB';
								clip_param = prm_record.data.clip_paramB;
							}else if(prm_record.data.clip_paramC != 0){
								clip = 'TB';
								clip_param = prm_record.data.clip_paramC;
							}
							anatomo_clip_predifined_plane.setValue(clip);
							clip_depth = Math.round(parseFloat(tpap_param.clip.paramD*clip_param*-1));
						}
					}
					if(clip_param<0 && anatomo_clip_reverse_check && anatomo_clip_reverse_check.rendered) anatomo_clip_reverse_check.setValue(true);

					if(anatomo_clip_slider && anatomo_clip_slider.rendered) anatomo_clip_slider.setValue(clip_depth);
					if(anatomo_clip_value_text && anatomo_clip_value_text.rendered) anatomo_clip_value_text.setValue(clip_depth);

					if(anatomo_clip_method_combo && anatomo_clip_method_combo.rendered) anatomo_clip_method_combo.setValue(tpap_param.clip.method);

					if(anatomo_clip_method_combo && anatomo_clip_method_combo.rendered) anatomo_clip_method_combo.show();
					if(anatomo_clip_predifined_plane && anatomo_clip_predifined_plane.rendered) anatomo_clip_predifined_plane.show();
					if(anatomo_clip_fix_check && anatomo_clip_fix_check.rendered && clip=='FREE') anatomo_clip_fix_check.show();
					if(anatomo_clip_reverse_check && anatomo_clip_reverse_check.rendered) anatomo_clip_reverse_check.show();
					if(anatomo_clip_slider && anatomo_clip_slider.rendered) anatomo_clip_slider.show();
					if(anatomo_clip_value_text && anatomo_clip_value_text.rendered) anatomo_clip_value_text.show();

					if(anatomo_clip_slider_up_button) anatomo_clip_slider_up_button.show();
					if(anatomo_clip_slider_down_button) anatomo_clip_slider_down_button.show();
					if(anatomo_clip_text_up_button) anatomo_clip_text_up_button.show();
					if(anatomo_clip_text_down_button) anatomo_clip_text_down_button.show();
					if(anatomo_clip_unit_label) anatomo_clip_unit_label.show();
					if(clip!='FREE' && clipImgDiv) clipImgDiv.show();

					if(anatomo_clip_predifined_plane && anatomo_clip_predifined_plane.rendered){
						if(anatomo_clip_predifined_plane.getValue() == "FB") {
							setClipImage(90,0,setClipLine);
						}else{
							setClipImage(0,0,setClipLine);
						}
					}

					if(anatomo_clip_check) anatomo_clip_check.on('check',oncheck_anatomo_clip_check);
					if(anatomo_clip_method_combo) anatomo_clip_method_combo.on('select',onselect_anatomo_clip_method_combo);
					if(anatomo_clip_predifined_plane) anatomo_clip_predifined_plane.on('select',onselect_anatomo_clip_predifined_plane);
					if(anatomo_clip_fix_check) anatomo_clip_fix_check.on('check',oncheck_anatomo_clip_fix_check);
					if(anatomo_clip_reverse_check) anatomo_clip_reverse_check.on('check',oncheck_anatomo_clip_reverse_check);
					if(anatomo_clip_slider) anatomo_clip_slider.on('change',onchange_anatomo_clip_slider);
					if(anatomo_clip_value_text) anatomo_clip_value_text.on('change',onchange_anatomo_clip_value_text);
				}
				prm_record.commit();
				prm_record.endEdit();
			}

			var new_recs = [];
//_dump("tpap_param.parts=["+tpap_param.parts.length+"]");
			if(tpap_param.parts && tpap_param.parts.length>0){
				for(var i=0,len=tpap_param.parts.length;i<len;i++){
					var part = tpap_param.parts[i];
					var f_id = part.id;
					if(!f_id && part.f_id) f_id = part.f_id;
//_dump("f_id=["+i+"]["+f_id+"]");
					if(Ext.isEmpty(fma_rec[f_id])) continue;
					var record = fma_rec[f_id];
					record.beginEdit();

//_dump("part.color=["+part.color+"]");
					if(!Ext.isEmpty(part.show)){
						record.set('color',(part.color=="NANANA"?"":"#"+part.color));
						record.set('value',(part.value=="NANANANANANA"?"":parseFloat((part.value.substr(0,1)=="M"?"-":"")+part.value.substr(1))));
						record.set('zoom', (part.show=="Z"?true:false));
						record.set('opacity',(parseFloat(part.opacity)/100));
					}else{
						record.set('color',  (!Ext.isEmpty(part.color)?('#'+part.color):'#'+prm_record.data.color_rgb));
						record.set('value',  part.value);
						record.set('zoom',   false);
						record.set('exclude',part.exclude);
						record.set('opacity',part.opacity);
						record.set('point',  part.point);
					}
					record.set('representation',(part.representation=="S"?"surface":(part.representation=="W"?"wireframe":(part.representation=="P"?"points":""))));

//_dump("record.data.color=["+record.data.color+"]");

					record.commit(true);
					record.endEdit();
					new_recs.push(record);
//_dump("record.data.tg_id=["+record.data.tg_id+"]");
				}
			}
//_dump("new_recs=["+new_recs.length+"]");


			if(tpap_param.point_parts && tpap_param.point_parts.length>0){
				for(var i=0,len=tpap_param.point_parts.length;i<len;i++){
					var part = tpap_param.point_parts[i];
					var f_id = part.id;
					if(!f_id && part.f_id) f_id = part.f_id;
//_dump("f_id=["+i+"]["+f_id+"]");
					if(Ext.isEmpty(fma_rec[f_id])) continue;
					var record = fma_rec[f_id];
					record.beginEdit();
					record.set('color',  (!Ext.isEmpty(part.color)?('#'+part.color):'#'+prm_record.data.point_color_rgb));
					record.set('value',  part.value);
					record.set('zoom',   false);
					record.set('exclude',part.exclude);
					record.set('opacity',part.opacity);
					record.set('point',  false);
					record.set('representation',(part.representation=="S"?"surface":(part.representation=="W"?"wireframe":(part.representation=="P"?"points":""))));

//_dump("record.data.color=["+record.data.color+"]");

					record.commit(true);
					record.endEdit();
					new_recs.push(record);
//_dump("record.data.tg_id=["+record.data.tg_id+"]");
				}
			}


			var ag_parts_gridpanel = Ext.getCmp('ag-parts-gridpanel');
			if(ag_parts_gridpanel){
				var store = ag_parts_gridpanel.getStore();
				store.add(new_recs);
				getConvertIdList(new_recs,store);
			}

			var anatomo_comment_store = null;
			var ag_pin_grid_panel = Ext.getCmp('anatomography-pin-grid-panel');
			if(ag_pin_grid_panel) anatomo_comment_store = ag_pin_grid_panel.getStore();

			if(anatomo_comment_store){
				anatomo_comment_store.removeAll();
				if(tpap_param.comments && tpap_param.comments.length>0){
					for (var i = 0, len = tpap_param.comments.length; i < len; i++) {
						var comment = tpap_param.comments[i];
						anatomo_comment_store.loadData([[parseIntTPAP(comment.no), comment.id, comment.name, parseFloatTPAP(comment.c3d.x), parseFloatTPAP(comment.c3d.y), parseFloatTPAP(comment.c3d.z), comment.point.rgb, comment.comment]], true);
					}
				}else if(tpap_param.pins && tpap_param.pins.length>0 && ag_comment_store_fields){
					var newRecord = Ext.data.Record.create(ag_comment_store_fields);
					var addrecs = [];
					for(var i=0,len=tpap_param.pins.length;i<len;i++){
						var pin = tpap_param.pins[i];
						var addrec = new newRecord({
							no: pin.no,
							x3d: pin.x3d,
							y3d: pin.y3d,
							z3d: pin.z3d,
							avx3d: pin.avx3d,
							avy3d: pin.avy3d,
							avz3d: pin.avz3d,
							uvx3d: pin.uvx3d,
							uvy3d: pin.uvy3d,
							uvz3d: pin.uvz3d,
							color: pin.color,
							oid: pin.organid,
							organ: pin.organname,
							comment: (pin.comment?pin.comment:""),
							coord: pin.coord
						});

						if(window.ag_extensions && ag_extensions.global_pin){
							addrec.beginEdit();
							if(!Ext.isEmpty(pin.PinID)) addrec.set("PinID",pin.PinID);
							if(!Ext.isEmpty(pin.PinGroupID)) addrec.set("PinGroupID",pin.PinGroupID);
							addrec.commit(true);
							addrec.endEdit();
						}
						addrecs.push(addrec);

						if(Ext.isEmpty(init_anatomo_pin_number_draw)) init_anatomo_pin_number_draw = pin.drawnm ? true : false;
						if(Ext.isEmpty(init_anatomo_pin_description_draw)) init_anatomo_pin_description_draw = pin.draw ? true : false;
						if(Ext.isEmpty(init_anatomo_pin_shape)) init_anatomo_pin_shape = pin.shape;

					}
					anatomo_comment_store.add(addrecs);

					var cmp = Ext.getCmp('anatomo_pin_number_draw_check');
					if(cmp && cmp.rendered) cmp.setValue(init_anatomo_pin_number_draw);

					var cmp = Ext.getCmp('anatomo_pin_description_draw_check');
					if(cmp && cmp.rendered) cmp.setValue(init_anatomo_pin_description_draw);

					var cmp = Ext.getCmp('anatomo_pin_description_draw_pin_indication_line_combo');
					if(cmp && cmp.rendered){
						if(init_anatomo_pin_description_draw){
							cmp.enable();
						}else{
							cmp.disable();
						}
					}
					var cmp = Ext.getCmp('anatomo_pin_shape_combo');
					if(cmp && cmp.rendered) cmp.setValue(init_anatomo_pin_shape);

				}
			}

			init_anatomography_image_comment_title = '';
			init_anatomography_image_comment_legend = '';
			init_anatomography_image_comment_author = '';

			if(!Ext.isEmpty(tpap_param.legendinfo)){
				if(!Ext.isEmpty(tpap_param.legendinfo.title)) init_anatomography_image_comment_title = tpap_param.legendinfo.title;
				if(!Ext.isEmpty(tpap_param.legendinfo.legend)) init_anatomography_image_comment_legend = tpap_param.legendinfo.legend;
				if(!Ext.isEmpty(tpap_param.legendinfo.author)) init_anatomography_image_comment_author = tpap_param.legendinfo.author;
				if(!Ext.isEmpty(tpap_param.legendinfo.position) && !Ext.isEmpty(tpap_param.legendinfo.color)){
					init_anatomography_image_comment_draw = true;
				}else{
					init_anatomography_image_comment_draw = false;
				}
			}

			var cmp = Ext.getCmp("anatomography_image_comment_title");
			if(cmp && cmp.rendered) cmp.setValue(init_anatomography_image_comment_title);

			var cmp = Ext.getCmp("anatomography_image_comment_legend");
			if(cmp && cmp.rendered) cmp.setValue(init_anatomography_image_comment_legend);

			var cmp = Ext.getCmp("anatomography_image_comment_author");
			if(cmp && cmp.rendered) cmp.setValue(init_anatomography_image_comment_author);

			var cmp = Ext.getCmp('anatomography_image_comment_draw_check');
			if(cmp && cmp.rendered) cmp.setValue(init_anatomography_image_comment_draw);


//2011-09-28 コメントアウト
//			if(tpap_param.parts && tpap_param.parts.length>0 && records.length>0 && contents_tabs) contents_tabs.setActiveTab('contents-tab-anatomography-panel');
//

			if(!Ext.isEmpty(gParams.tp_md) && gParams.tp_md == 1){
//_dump("CALL updateAnatomo()");
				setImageWindowSize();
			}

		}
//_dump("bp3d_contents_store.load():prm_record.data.clip_depth=["+prm_record.data.clip_depth+"]");
//	}catch(e){
//		_dump("bp3d_contents_store.load():"+e);
//	}

	if(Ext.Ajax.isLoading()){
		var runner = new Ext.util.TaskRunner();
		var task = {
			run: function(){
//				console.log("BEFORE CALL updateAnatomo()");
				if(Ext.Ajax.isLoading()) return;
				runner.stop(task);
//				console.log("CALL updateAnatomo()");
//				console.log("Ext.Ajax.isLoading():["+Ext.Ajax.isLoading()+"]");
				updateAnatomo();
			},
			interval: 1000 //1 second
		}
		runner.start(task);

	}else{
//		console.log("CALL updateAnatomo()");
//		console.log("Ext.Ajax.isLoading():["+Ext.Ajax.isLoading()+"]");
		updateAnatomo();
	}
};

get_bp3d_buildup_logic = function(){
	var bul_id = init_bp3d_params['bul_id'] ? init_bp3d_params['bul_id'] : 3;
	try{
		bul_id = Ext.getCmp('bp3d-tree-type-combo').getValue();
	}catch(e){}
	return bul_id;
};

/////////////////////////////////////////////////////////////////////////////////////////////////////

afterLayout = function(panel){
	try{
		if(!Ext.isIE) return;
		if(!panel.rendered) return;
		if(panel.collapsed) panel.expand(false);
		var box = panel.getBox();
		if(box.x==0 && box.y==0) return;
		var width  = Ext.isEmpty(panel.initialConfig.minWidth) ?box.width :panel.initialConfig.minWidth;
		var height = Ext.isEmpty(panel.initialConfig.minHeight)?box.height:panel.initialConfig.minHeight;
		if((box.width<width && height > 0) || (width > 0 && box.height<height)){
			panel.setSize(width,height);
			panel.ownerCt.doLayout();
		}
	}catch(e){
		_dump("afterLayout():"+e);
	}
};


Ext.menu.RangeMenu.prototype.icons = {
	gt: 'css/greater_then.png',
	lt: 'css/less_then.png',
	eq: 'css/equals.png'
};
Ext.grid.filter.StringFilter.prototype.icon = 'css/find.png';

if(!String.prototype.ellipse) {
	String.prototype.ellipse = function(maxLength){
//		if(this.length > maxLength){
//			return this.substr(0, maxLength-3) + '...';
//		}
		return this;
	};
}

if(!String.prototype.sprintf) {
	String.prototype.sprintf = function(args___) {
		var rv = [], i = 0, v, width, precision, sign, idx, argv = arguments, next = 0;
		var s = (this + "     ").split(""); // add dummy 5 chars.
		var unsign = function(val) { return (val >= 0) ? val : val % 0x100000000 + 0x100000000; };
		var getArg = function() { return argv[idx ? idx - 1 : next++]; };

		for(;i<s.length-5;++i){
			if(s[i] !== "%"){
				rv.push(s[i]);
				continue;
			}
			++i, idx = 0, precision = undefined;

			// arg-index-specifier
			if (!isNaN(parseInt(s[i])) && s[i + 1] === "$") { idx = parseInt(s[i]); i += 2; }
			// sign-specifier
			sign = (s[i] !== "#") ? false : ++i, true;
			// width-specifier
			width = (isNaN(parseInt(s[i]))) ? 0 : parseInt(s[i++]);
			// precision-specifier
			if (s[i] === "." && !isNaN(parseInt(s[i + 1]))) { precision = parseInt(s[i + 1]); i += 2; }

			switch(s[i]){
				case "d": v = parseInt(getArg()).toString(); break;
				case "u": v = parseInt(getArg()); if (!isNaN(v)) { v = unsign(v).toString(); } break;
				case "o": v = parseInt(getArg()); if (!isNaN(v)) { v = (sign ? "0"  : "") + unsign(v).toString(8); } break;
				case "x": v = parseInt(getArg()); if (!isNaN(v)) { v = (sign ? "0x" : "") + unsign(v).toString(16); } break;
				case "X": v = parseInt(getArg()); if (!isNaN(v)) { v = (sign ? "0X" : "") + unsign(v).toString(16).toUpperCase(); } break;
				case "f": v = parseFloat(getArg()).toFixed(precision); break;
				case "c": width = 0; v = getArg(); v = (typeof v === "number") ? String.fromCharCode(v) : NaN; break;
				case "s": width = 0; v = getArg().toString(); if (precision) { v = v.substring(0, precision); } break;
				case "%": width = 0; v = s[i]; break;
				default:  width = 0; v = "%" + ((width) ? width.toString() : "") + s[i].toString(); break;
			}
			if(isNaN(v)){ v = v.toString(); }
			(v.length < width) ? rv.push(" ".repeat(width - v.length), v) : rv.push(v);
		}
		return rv.join("");
	};
}
if(!String.prototype.repeat){
	String.prototype.repeat = function(n) {
		var rv = [], i = 0, sz = n || 1, s = this.toString();
		for (; i < sz; ++i) { rv.push(s); }
		return rv.join("");
	};
}

function parseFloatTPAP(str){
	try{
		return str=="NANANANANANA"?NaN:parseFloat((str.substr(0,1)=="M"?"-":"")+str.substr(1).replace(/^0+/,""));
	}catch(e){
		return NaN;
	}
}

function parseIntTPAP(str){
	try{
		return parseInt(str.replace(/^0+/,""));
	}catch(e){
		return NaN;
	}
}

function analyzeTPAP(tp_ap,aOpts){

	var defOpts = {
		pin: {
			url_prefix : null
		}
	};
	aOpts = aOpts||{};
	var convOpts = {};
	for(var key in defOpts){
		convOpts[key] = Ext.apply({},aOpts[key]||{},defOpts[key]);
	}

	var param = {};
	var param_arr = tp_ap.split("|");
	if(param_arr.length<1) return undefined;
	if(param_arr.length==1){

		//修正中（とりあえず、パーツの情報を受け取れるように修正）2009/09/09
		var tp_ap_obj = Ext.urlDecode(tp_ap,true);
		if(tp_ap_obj && Ext.isEmpty(tp_ap_obj.av)) tp_ap_obj.av = "09051901";

		if(tp_ap_obj && tp_ap_obj.av){
			if(tp_ap_obj.av == "09051901"){
				param.common = {};
				param.common.version = tp_ap_obj.av;
				param.common.pin = 0;
				param.common.pinno = 1;

				if(!Ext.isEmpty(tp_ap_obj.iw)) param.common.image_w = tp_ap_obj.iw;
				if(!Ext.isEmpty(tp_ap_obj.ih)) param.common.image_h = tp_ap_obj.ih;
				if(!Ext.isEmpty(tp_ap_obj.bcl)) param.common.bg_rgb = tp_ap_obj.bcl.toUpperCase();
				if(!Ext.isEmpty(tp_ap_obj.bga)) param.common.bg_transparent = tp_ap_obj.bga;
				if(!Ext.isEmpty(tp_ap_obj.sx)) param.common.scalar_max = tp_ap_obj.sx;
				if(!Ext.isEmpty(tp_ap_obj.sn)) param.common.scalar_min = tp_ap_obj.sn;
				if(!Ext.isEmpty(tp_ap_obj.cf)) param.common.colorbar_f = tp_ap_obj.cf;
				if(!Ext.isEmpty(tp_ap_obj.hf)) param.common.heatmap_f = tp_ap_obj.hf;
				if(!Ext.isEmpty(tp_ap_obj.model)) param.common.model = tp_ap_obj.model;
				if(!Ext.isEmpty(tp_ap_obj.bv)) param.common.bp3d_version = tp_ap_obj.bv;
				if(!Ext.isEmpty(tp_ap_obj.tn)) param.common.treename = tp_ap_obj.tn;
				if(!Ext.isEmpty(tp_ap_obj.dt)) param.common.date = tp_ap_obj.dt;
				if(!Ext.isEmpty(tp_ap_obj.dl)) param.common.legend = tp_ap_obj.dl;
				if(!Ext.isEmpty(tp_ap_obj.dp)) param.common.pin = tp_ap_obj.dp-0;
				if(!Ext.isEmpty(tp_ap_obj.zm)) param.common.zoom = tp_ap_obj.zm;
				if(!Ext.isEmpty(tp_ap_obj.crd)) param.common.coord = tp_ap_obj.crd;
				if(!Ext.isEmpty(tp_ap_obj.fcl)) param.common.color_rgb = tp_ap_obj.fcl;

				if(!Ext.isEmpty(tp_ap_obj.np)) param.common.pinno = tp_ap_obj.np-0;

				if(!Ext.isEmpty(tp_ap_obj.gdr)){
					param.common.grid = (tp_ap_obj.gdr=='true'?'1':'0');
				}else{
					param.common.grid = '0';
				}
				if(!Ext.isEmpty(tp_ap_obj.gcl)) param.common.grid_color = tp_ap_obj.gcl;
				if(!Ext.isEmpty(tp_ap_obj.gtc)) param.common.grid_len = tp_ap_obj.gtc;

				if(
					!Ext.isEmpty(tp_ap_obj.cx) || !Ext.isEmpty(tp_ap_obj.cy) || !Ext.isEmpty(tp_ap_obj.cz) ||
					!Ext.isEmpty(tp_ap_obj.tx) || !Ext.isEmpty(tp_ap_obj.ty) || !Ext.isEmpty(tp_ap_obj.tz) ||
					!Ext.isEmpty(tp_ap_obj.ux) || !Ext.isEmpty(tp_ap_obj.uy) || !Ext.isEmpty(tp_ap_obj.uz)
				){
					param.camera = {};
					if(!Ext.isEmpty(tp_ap_obj.cx) && !Ext.isEmpty(tp_ap_obj.cy) && !Ext.isEmpty(tp_ap_obj.cz) && !isNaN(tp_ap_obj.cx) && !isNaN(tp_ap_obj.cy) && !isNaN(tp_ap_obj.cz)){
						param.camera.cameraPos = {};
						if(!Ext.isEmpty(tp_ap_obj.cx)) param.camera.cameraPos.x = parseFloat(tp_ap_obj.cx);
						if(!Ext.isEmpty(tp_ap_obj.cy)) param.camera.cameraPos.y = parseFloat(tp_ap_obj.cy);
						if(!Ext.isEmpty(tp_ap_obj.cz)) param.camera.cameraPos.z = parseFloat(tp_ap_obj.cz);
					}
					if(!Ext.isEmpty(tp_ap_obj.tx) && !Ext.isEmpty(tp_ap_obj.ty) && !Ext.isEmpty(tp_ap_obj.tz) && !isNaN(tp_ap_obj.tx) && !isNaN(tp_ap_obj.ty) && !isNaN(tp_ap_obj.tz)){
						param.camera.targetPos = {};
						if(!Ext.isEmpty(tp_ap_obj.tx)) param.camera.targetPos.x = parseFloat(tp_ap_obj.tx);
						if(!Ext.isEmpty(tp_ap_obj.ty)) param.camera.targetPos.y = parseFloat(tp_ap_obj.ty);
						if(!Ext.isEmpty(tp_ap_obj.tz)) param.camera.targetPos.z = parseFloat(tp_ap_obj.tz);
					}
					if(!Ext.isEmpty(tp_ap_obj.ux) && !Ext.isEmpty(tp_ap_obj.uy) && !Ext.isEmpty(tp_ap_obj.uz) && !isNaN(tp_ap_obj.ux) && !isNaN(tp_ap_obj.uy) && !isNaN(tp_ap_obj.uz)){
						param.camera.upVec = {};
						if(!Ext.isEmpty(tp_ap_obj.ux)) param.camera.upVec.x = parseFloat(tp_ap_obj.ux);
						if(!Ext.isEmpty(tp_ap_obj.uy)) param.camera.upVec.y = parseFloat(tp_ap_obj.uy);
						if(!Ext.isEmpty(tp_ap_obj.uz)) param.camera.upVec.z = parseFloat(tp_ap_obj.uz);
					}
				}

				if(
					!Ext.isEmpty(tp_ap_obj.cm)  || !Ext.isEmpty(tp_ap_obj.cd)  || !Ext.isEmpty(tp_ap_obj.ct)  ||
					!Ext.isEmpty(tp_ap_obj.cpa) || !Ext.isEmpty(tp_ap_obj.cpb) || !Ext.isEmpty(tp_ap_obj.cpc) || !Ext.isEmpty(tp_ap_obj.cpd)
				){
					param.clip = {};
					if(!Ext.isEmpty(tp_ap_obj.cm)) param.clip.type = tp_ap_obj.cm;
					if(!Ext.isEmpty(tp_ap_obj.cd)) param.clip.depth = tp_ap_obj.cd;
					if(!Ext.isEmpty(tp_ap_obj.ct)) param.clip.method = tp_ap_obj.ct;
					if(!Ext.isEmpty(tp_ap_obj.cpa)) param.clip.paramA = parseFloat(tp_ap_obj.cpa);
					if(!Ext.isEmpty(tp_ap_obj.cpb)) param.clip.paramB = parseFloat(tp_ap_obj.cpb);
					if(!Ext.isEmpty(tp_ap_obj.cpc)) param.clip.paramC = parseFloat(tp_ap_obj.cpc);
					if(!Ext.isEmpty(tp_ap_obj.cpd)) param.clip.paramD = parseFloat(tp_ap_obj.cpd);
				}

				if(!Ext.isEmpty(tp_ap_obj.oid001) || !Ext.isEmpty(tp_ap_obj.onm001)){
					var prm_record = ag_param_store.getAt(0);
					param.parts = [];
					for(var i=0;;i++){
						var num = makeAnatomoOrganNumber(i+1);
						if(Ext.isEmpty(tp_ap_obj['oid'+num]) && Ext.isEmpty(tp_ap_obj['onm'+num])) break;
						var parts = {
							color   : prm_record.data.color_rgb,
							value   : '',
							exclude : false,
							zoom    : false,
							opacity : 1.0,
							representation : 'S',
							point   : false
						};
						if(!Ext.isEmpty(tp_ap_obj['oid'+num])) parts.f_id = tp_ap_obj['oid'+num];
						if(!Ext.isEmpty(tp_ap_obj['onm'+num])) parts.f_nm = tp_ap_obj['onm'+num];
						if(!Ext.isEmpty(tp_ap_obj['ocl'+num])) parts.color = tp_ap_obj['ocl'+num].toUpperCase();
						if(!Ext.isEmpty(tp_ap_obj['osc'+num])) parts.value = tp_ap_obj['osc'+num];
						if(!Ext.isEmpty(tp_ap_obj['osz'+num])){
							if(tp_ap_obj['osz'+num] == 'H'){
								parts.exclude = true;
							}else if(tp_ap_obj['osz'+num] == 'Z'){
								parts.zoom = true;
							}
						}
						if(!Ext.isEmpty(tp_ap_obj['oop'+num])) parts.opacity = tp_ap_obj['oop'+num];
						if(!Ext.isEmpty(tp_ap_obj['orp'+num])) parts.representation = tp_ap_obj['orp'+num];
						if(!Ext.isEmpty(tp_ap_obj['ov'+num])) parts.version = tp_ap_obj['ov'+num];
						if(!Ext.isEmpty(tp_ap_obj['odcp'+num])) parts.point = tp_ap_obj['odcp'+num]=='1'?true:false;
//_dump("parts.point=["+parts.point+"]");
						param.parts.push(parts);
					}
				}
				if(!Ext.isEmpty(tp_ap_obj.lp) || !Ext.isEmpty(tp_ap_obj.lc) || !Ext.isEmpty(tp_ap_obj.lt) || !Ext.isEmpty(tp_ap_obj.le) || !Ext.isEmpty(tp_ap_obj.la)){
					param.legendinfo = {};
					if(!Ext.isEmpty(tp_ap_obj.lp)) param.legendinfo.position = tp_ap_obj.lp;
					if(!Ext.isEmpty(tp_ap_obj.lc)) param.legendinfo.color = tp_ap_obj.lc.toUpperCase();
					if(!Ext.isEmpty(tp_ap_obj.lt)) param.legendinfo.title = tp_ap_obj.lt;
					if(!Ext.isEmpty(tp_ap_obj.le)) param.legendinfo.legend = tp_ap_obj.le;
					if(!Ext.isEmpty(tp_ap_obj.la)) param.legendinfo.author = tp_ap_obj.la;
				}
				if(!Ext.isEmpty(tp_ap_obj.pno001)){
					param.pins = [];

					var pinRecord = Ext.data.Record.create(ag_comment_store_fields);

					for(var i=0;;i++){
						var num = makeAnatomoOrganNumber(i+1);
						if(Ext.isEmpty(tp_ap_obj['pno'+num])) break;
						var pin = {};
						pin.no = i+1;
						if(!Ext.isEmpty(tp_ap_obj['px'+num]))  pin.x3d = tp_ap_obj['px'+num]-0;
						if(!Ext.isEmpty(tp_ap_obj['py'+num]))  pin.y3d = tp_ap_obj['py'+num]-0;
						if(!Ext.isEmpty(tp_ap_obj['pz'+num]))  pin.z3d = tp_ap_obj['pz'+num]-0;
						if(!Ext.isEmpty(tp_ap_obj['pax'+num])) pin.avx3d = tp_ap_obj['pax'+num]-0;
						if(!Ext.isEmpty(tp_ap_obj['pay'+num])) pin.avy3d = tp_ap_obj['pay'+num]-0;
						if(!Ext.isEmpty(tp_ap_obj['paz'+num])) pin.avz3d = tp_ap_obj['paz'+num]-0;
						if(!Ext.isEmpty(tp_ap_obj['pux'+num])) pin.uvx3d = tp_ap_obj['pux'+num]-0;
						if(!Ext.isEmpty(tp_ap_obj['puy'+num])) pin.uvy3d = tp_ap_obj['puy'+num]-0;
						if(!Ext.isEmpty(tp_ap_obj['puz'+num])) pin.uvz3d = tp_ap_obj['puz'+num]-0;
						if(!Ext.isEmpty(tp_ap_obj['pdd'+num])) pin.draw = tp_ap_obj['pdd'+num]-0;
						if(!Ext.isEmpty(tp_ap_obj['pnd'+num])) pin.drawnm = tp_ap_obj['pnd'+num]-0;
						if(!Ext.isEmpty(tp_ap_obj['pdc'+num])) pin.tcolor = tp_ap_obj['pdc'+num].toUpperCase();
						if(!Ext.isEmpty(tp_ap_obj['ps'+num]))  pin.shape = tp_ap_obj['ps'+num];
						if(!Ext.isEmpty(tp_ap_obj['pcl'+num])) pin.color = tp_ap_obj['pcl'+num].toUpperCase();
						if(!Ext.isEmpty(tp_ap_obj['poi'+num])){
							pin.oid = tp_ap_obj['poi'+num];
							pin.organid = tp_ap_obj['poi'+num];
						}
						if(!Ext.isEmpty(tp_ap_obj['pon'+num])){
							pin.organ = tp_ap_obj['pon'+num];
							pin.organname = tp_ap_obj['pon'+num];
						}
						if(!Ext.isEmpty(tp_ap_obj['pd'+num]))  pin.comment = tp_ap_obj['pd'+num];
						if(!Ext.isEmpty(tp_ap_obj['pcd'+num])) pin.coord = tp_ap_obj['pcd'+num];
						if(window.ag_extensions && ag_extensions.global_pin){
							if(!Ext.isEmpty(tp_ap_obj['pid'+num])) pin.PinID = tp_ap_obj['pid'+num];
							if(!Ext.isEmpty(tp_ap_obj['pgid'+num])) pin.PinGroupID = tp_ap_obj['pgid'+num];
						}

						if(convOpts.pin.url_prefix){
							var newPartsRecord = Ext.data.Record.create(bp3d_parts_store_fields);
							var numParts = makeAnatomoOrganNumber(1);
							var prm_record = ag_param_store.getAt(0);
							var parts_record = new newPartsRecord({
								'f_id'          : pin.oid,
								'exclude'       : false,
								'color'         : '#'+prm_record.data.color_rgb,
								'value'         : '',
								'zoom'          : false,
								'opacity'       : '1.0',
								'representation': 'surface',
								'point'         : false
							});
							var prmParts = "oid" + numParts + "=" + pin.oid;
							prmParts += makeAnatomoOrganPrm(numParts,parts_record,null,null);

							var newPinRecord = new pinRecord(pin);
							var pinPrm = makeAnatomoPrm_Pin(newPinRecord,undefined,undefined,{no:1});

							var params = Ext.urlDecode(prmParts);
							if(pinPrm) params = Ext.apply({},Ext.urlDecode(pinPrm),params);

							if(pinPrm) pin.url = convOpts.pin.url_prefix + encodeURIComponent(Ext.urlEncode(params));

							newPartsRecord = undefined;
							numParts = undefined;
							prm_record = undefined;
							parts_record = undefined;
							newPinRecord = undefined;
						}
						param.pins.push(pin);
					}
					pinRecord = undefined;
				}

				if(!Ext.isEmpty(tp_ap_obj.poid001)){
					var prm_record = ag_param_store.getAt(0);
					param.point_parts = [];
					for(var i=0;;i++){
						var num = makeAnatomoOrganNumber(i+1);
						if(Ext.isEmpty(tp_ap_obj['poid'+num])) break;
						var parts = {
							color   : prm_record.data.point_color_rgb,
							value   : '',
							exclude : false,
							zoom    : false,
							opacity : 1.0,
							representation : 'S',
							point   : false
						};
						if(!Ext.isEmpty(tp_ap_obj['poid'+num])) parts.f_id = tp_ap_obj['poid'+num];
						if(!Ext.isEmpty(tp_ap_obj['pocl'+num])) parts.color = tp_ap_obj['pocl'+num].toUpperCase();
						if(!Ext.isEmpty(tp_ap_obj['porm'+num])) parts.exclude = tp_ap_obj['porm'+num]=='1'?true:false;
						if(!Ext.isEmpty(tp_ap_obj['poop'+num])) parts.opacity = tp_ap_obj['poop'+num];
						if(!Ext.isEmpty(tp_ap_obj['pore'+num])) parts.representation = tp_ap_obj['pore'+num];
						if(!Ext.isEmpty(tp_ap_obj['posh'+num])){
							parts.point_sphere = tp_ap_obj['posh'+num];
							param.common.point_sphere = tp_ap_obj['posh'+num];
						}
						param.point_parts.push(parts);
					}
				}
				if(!Ext.isEmpty(tp_ap_obj.dpod)) param.common.point_desc = tp_ap_obj.dpod;
				if(!Ext.isEmpty(tp_ap_obj.dpl)) param.common.point_pin_line = tp_ap_obj.dpl;
				if(!Ext.isEmpty(tp_ap_obj.dpol)) param.common.point_point_line = tp_ap_obj.dpol;
				return param;
			}else{
				return undefined;
			}
		}else{
			return undefined;
		}
	}

	var prm_info = param_arr.shift();
	var p = prm_info.split(":");
	param.common = {};
	param.common.version = p[0];

	if(param.common.version == "08020601" || param.common.version == "08110101"){
		param.common.method = p[1].substr(0,1);
		param.common.viewpoint = p[1].substr(1,1);
		param.common.rotate_h = parseIntTPAP(p[1].substr(2,3));
		param.common.rotate_v = parseIntTPAP(p[1].substr(5,3));
		param.common.image_w = parseIntTPAP(p[1].substr(8,4));
		param.common.image_h = parseIntTPAP(p[1].substr(12,4));
		param.common.bg_rgb = p[1].substr(16,6);
		param.common.autoscalar_f = p[1].substr(22,1);
		param.common.scalar_max = parseFloatTPAP(p[1].substr(23,12));
		param.common.scalar_min = parseFloatTPAP(p[1].substr(35,12));
		param.common.colorbar_f = p[1].substr(47,1);
		param.common.drawsort_f = p[1].substr(48,1);
		param.common.mov_len = parseIntTPAP(p[1].substr(49,2));
		param.common.mov_fps = parseIntTPAP(p[1].substr(51,2));

	}else if(param.common.version == "09011601"){
		param.common.method = p[1].substr(0,1);
		param.common.viewpoint = p[1].substr(1,1);
		param.common.rotate_h = parseIntTPAP(p[1].substr(2,3));
		param.common.rotate_v = parseIntTPAP(p[1].substr(5,3));
		param.common.image_w = parseIntTPAP(p[1].substr(8,4));
		param.common.image_h = parseIntTPAP(p[1].substr(12,4));
		param.common.bg_rgb = p[1].substr(16,6);
		param.common.autoscalar_f = p[1].substr(22,1);
		param.common.scalar_max = parseFloatTPAP(p[1].substr(23,12));
		param.common.scalar_min = parseFloatTPAP(p[1].substr(35,12));
		param.common.colorbar_f = p[1].substr(47,1);
		param.common.drawsort_f = p[1].substr(48,1);
		param.common.mov_len = parseIntTPAP(p[1].substr(49,2));
		param.common.mov_fps = parseIntTPAP(p[1].substr(51,2));

		param.common.zoom = parseFloatTPAP(p[1].substr(53,12));
		param.common.move_x = parseFloatTPAP(p[1].substr(65,12));
		param.common.move_y = parseFloatTPAP(p[1].substr(77,12));
		param.common.move_z = parseFloatTPAP(p[1].substr(89,12));
		param.common.clip_depth = parseFloatTPAP(p[1].substr(101,12));
		param.common.clip_method = p[1].substr(113,1);
	}

	if(param_arr.length>0 && param.common.version == "08020601"){
		param.parts = [];
		for(var i=0,len=param_arr.length;i<len;i++){
			var p = param_arr[i].split(":");
			param.parts.push({
				id : p[0],
				color : (p.length<=2?p[1]:"").substr(0,6),
				value : (p.length<=2?p[1]:"").substr(6,12),
				show : (p.length<=2?p[1]:"").substr(18,1),
				opacity : (p.length<=2?p[1]:"").substr(19,3),
				representation : (p.length<=2?p[1]:"").substr(22,1)
			});
		}
	}else if(param_arr.length>0 && (param.common.version == "08110101" || param.common.version == "09011601")){
		param.parts = [];
		var parts_info = param_arr.shift();
		var parts_arr = parts_info.split("@");
		for(var i=0,len=parts_arr.length;i<len;i++){
			var p = parts_arr[i].split(":");
			param.parts.push({
				id : p[0],
				color : (p.length<=2?p[1]:"").substr(0,6),
				value : (p.length<=2?p[1]:"").substr(6,12),
				show : (p.length<=2?p[1]:"").substr(18,1),
				opacity : (p.length<=2?p[1]:"").substr(19,3),
				representation : (p.length<=2?p[1]:"").substr(22,1)
			});
		}
	}

	if(param_arr.length>0 && (param.common.version == "08110101" || param.common.version == "09011601")){
		param.comments = [];

		var comments_info = param_arr.shift();
		var comments_arr = comments_info.split("@");
		for(var i=0,len=comments_arr.length;i<len;i++){
			var p = comments_arr[i].split(":");
			param.comments.push({
				no : p[0].substr(0,3),
				c3d : {
					x : p[0].substr(3,12),
					y : p[0].substr(15,12),
					z : p[0].substr(27,12)
				},
				point : {
					shape : (p.length>=2?p[1]:"").substr(0,2),
					rotation : (p.length>=2?p[1]:"").substr(2,3),
					rgb : (p.length>=2?p[1]:"").substr(5,6),
					edge_rgb : (p.length>=2?p[1]:"").substr(11,6)
				},
				id : (p.length>=3?p[2]:""),
				name : (p.length>=4?p[3]:""),
				comment : (p.length>=5?p[4]:"")
			});
		}

	}
	return param;
}

function URI2Text(aURIString,aOpts){
	if(Ext.isEmpty(aURIString)) return undefined;

	var defOpts = {
		target: {
			common: true,
			camera: true,
			clip: true,
			parts: true,
			point_parts: true,
			legendinfo: true,
			pins: true
		},
		pin: {
			url_prefix : null
		}
	};
	aOpts = aOpts||{};
	var convOpts = {};
	for(var key in defOpts){
		convOpts[key] = Ext.apply({},aOpts[key]||{},defOpts[key]);
	}

	var tpap_param;
	if(typeof aURIString == 'string'){
		var search = "";
		if(aURIString.indexOf("?")>=0){
//			search = aURIString.replace(/^.+\?(.*)$/g,"$1");
			search = aURIString.replace(/^.*\?(.*)$/g,"$1");
		}else{
			return undefined;
		}
		var params = Ext.urlDecode(search);
		if(Ext.isEmpty(params.tp_ap)) params.tp_ap = search;
		tpap_param = analyzeTPAP(params.tp_ap,convOpts);
	}else if(typeof aURIString == 'object'){
		tpap_param = aURIString;
	}
	if(Ext.isEmpty(tpap_param)) return undefined;

	var key_len = 9;
	var text_value = "";
	var key_value;
	if(convOpts.target.common && !Ext.isEmpty(tpap_param.common)){

		//Version of script
		if(!Ext.isEmpty(tpap_param.common.version)){
			key_value = 'VERSION';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + tpap_param.common.version + "\n";
		}

		//Screen size
		if(!Ext.isEmpty(tpap_param.common.image_w) && !Ext.isEmpty(tpap_param.common.image_h)){
			key_value = 'SIZE';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - W:" + tpap_param.common.image_w + ';H:' + tpap_param.common.image_h + "\n";
		}

		//back ground color
		if(!Ext.isEmpty(tpap_param.common.bg_rgb)){
			key_value = 'BGCOLOR';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + tpap_param.common.bg_rgb + "\n";
		}
		if(!Ext.isEmpty(tpap_param.common.bg_transparent)){
			key_value = 'BGTRANS';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + "1\n";
		}

		//max and min for scholor color system、with ot w/o color bars
		if(!Ext.isEmpty(tpap_param.common.scalar_max) && !Ext.isEmpty(tpap_param.common.scalar_min)){
			key_value = 'SCCOLOR';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - MAX:" + tpap_param.common.scalar_max + ';MIN:' + tpap_param.common.scalar_min + "\n";
		}
		if(!Ext.isEmpty(tpap_param.common.colorbar_f)){
			key_value = 'COLORBAR';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + tpap_param.common.colorbar_f + "\n";
		}
		if(!Ext.isEmpty(tpap_param.common.heatmap_f)){
			key_value = 'HEATMAP';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + tpap_param.common.heatmap_f + "\n";
		}

		//BodyParts3Dのバージョン
		if(!Ext.isEmpty(tpap_param.common.bp3d_version)){
			key_value = 'BP3DVER';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + tpap_param.common.bp3d_version + "\n";
		}

		//Tree Name
		if(!Ext.isEmpty(tpap_param.common.treename)){
			key_value = 'TREENAME';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + tpap_param.common.treename + "\n";
		}

		//作成日付
		if(!Ext.isEmpty(tpap_param.common.date)){
			key_value = 'DATE';
			while(key_value.length<key_len) key_value += ' ';
			var date_str = tpap_param.common.date;
			if(date_str.match(/^([0-9]{4})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})$/)){
				var date = new Date(RegExp.$1, RegExp.$2, RegExp.$3, RegExp.$4, RegExp.$5, RegExp.$6);
				date_str = date.toString();
				date_str = date_str.replace(/\(.+$/,"").replace(/\s+$/,"");
			}
			text_value += key_value + " - " + date_str + "\n";
		}

		//Legend描画フラグ
		if(!Ext.isEmpty(tpap_param.common.legend)){
			key_value = 'DRAWNOTE';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + tpap_param.common.legend + "\n";
		}

		//Pin描画フラグ
		if(!Ext.isEmpty(tpap_param.common.pin)){
			key_value = 'DRAWPIN';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + tpap_param.common.pin + "\n";
		}
		if(!Ext.isEmpty(tpap_param.common.pinno)){
			key_value = 'DRAWPINNO';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + tpap_param.common.pinno + "\n";
		}
		if(!Ext.isEmpty(tpap_param.common.point_pin_line)){
			key_value = 'DRAWPINLI';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + tpap_param.common.point_pin_line + "\n";
		}

		//Zoom
		if(!Ext.isEmpty(tpap_param.common.zoom)){
			key_value = 'ZOOM';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + ((tpap_param.common.zoom*5)+1) + "\n";
		}

		//Grid
		if(!Ext.isEmpty(tpap_param.common.grid)){
			key_value = 'GRID';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + tpap_param.common.grid + "\n";
			if(!Ext.isEmpty(tpap_param.common.grid_color)){
				key_value = '  COLOR';
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + tpap_param.common.grid_color + "\n";
			}
			if(!Ext.isEmpty(tpap_param.common.grid_len)){
				key_value = '  INTER';
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + tpap_param.common.grid_len + "\n";
			}
		}

		//coordinate_system
		if(!Ext.isEmpty(tpap_param.common.coord)){
			key_value = 'COORD';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - " + tpap_param.common.coord + "\n";
		}

//		//Point
//		if(!Ext.isEmpty(tpap_param.common.point_desc) && tpap_param.common.point_desc){
//			key_value = 'POINTDESC';
//			text_value += key_value + "\n";
//			key_value = '  SHOW';
//			while(key_value.length<key_len) key_value += ' ';
//			text_value += key_value + " - " + tpap_param.common.point_desc + "\n";
//
//			if(!Ext.isEmpty(tpap_param.common.point_pin_line)){
//				key_value = '  PIN';
//				while(key_value.length<key_len) key_value += ' ';
//				text_value += key_value + " - " + tpap_param.common.point_pin_line + "\n";
//			}
//
//			if(!Ext.isEmpty(tpap_param.common.point_point_line)){
//				key_value = '  POINT';
//				while(key_value.length<key_len) key_value += ' ';
//				text_value += key_value + " - " + tpap_param.common.point_point_line + "\n";
//			}
//
//			if(!Ext.isEmpty(tpap_param.common.point_sphere)){
//				key_value = '  SPHERE';
//				while(key_value.length<key_len) key_value += ' ';
//				text_value += key_value + " - " + (tpap_param.common.point_sphere=='SL'?'Large':tpap_param.common.point_sphere=='SM'?'Medium':'Small') + "\n";
//			}
//
//		}
	}

	if(convOpts.target.camera && !Ext.isEmpty(tpap_param.camera)){
		key_value = 'CAMERA';
//		while(key_value.length<key_len) key_value += ' ';
		text_value += key_value + "\n";

		if(!Ext.isEmpty(tpap_param.camera.cameraPos)){
			key_value = '  COORD';	//coordination of camera and object(x,y,z)
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - X:" + tpap_param.camera.cameraPos.x + ';Y:' + tpap_param.camera.cameraPos.y + ';Z:' + tpap_param.camera.cameraPos.z + "\n";
		}
		if(!Ext.isEmpty(tpap_param.camera.targetPos)){
			key_value = '  VECTOR';	//direction of camera(x,y,z)
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - X:" + tpap_param.camera.targetPos.x + ';Y:' + tpap_param.camera.targetPos.y + ';Z:' + tpap_param.camera.targetPos.z + "\n";
		}
		if(!Ext.isEmpty(tpap_param.camera.upVec)){
			key_value = '  UP';	//magnify
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - X:" + tpap_param.camera.upVec.x + ';Y:' + tpap_param.camera.upVec.y + ';Z:' + tpap_param.camera.upVec.z + "\n";
		}
	}




	if(convOpts.target.parts && !Ext.isEmpty(tpap_param.parts) && tpap_param.parts.length>0){
		key_value = 'PARTS';
		text_value += key_value + "\n";

		for(var p=0,len=tpap_param.parts.length;p<len;p++){
			var part = tpap_param.parts[p];

			if(!Ext.isEmpty(part.f_id)){
				key_value = '  ID';	//臓器ID(FMAID)
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + part.f_id + "\n";
			}
			if(!Ext.isEmpty(part.f_nm)){
				key_value = '  NAME';	//臓器NAME
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + part.f_nm + "\n";
			}
			if(!Ext.isEmpty(part.version)){
				key_value = '  VERSION';	//バージョン
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + part.version + "\n";
			}
			if(!Ext.isEmpty(part.color)){
				key_value = '  COLOR';	//臓器色(RGB)
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + part.color + "\n";
			}
			if(!Ext.isEmpty(part.value)){
				key_value = '  SCALAR';	//スカラー値
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + part.value + "\n";
			}
			if(!Ext.isEmpty(part.opacity)){
				key_value = '  OPACITY';	//不透明度
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + part.opacity + "\n";
			}
			if(!Ext.isEmpty(part.representation)){
				key_value = '  REPRE';	//表現方法
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + (part.representation=='P'?'points':(part.representation=='W'?'wireframe':'surface')) + "\n";
			}
			if(!Ext.isEmpty(part.exclude) || !Ext.isEmpty(part.zoom)){
				key_value = '  STATE';	//状態フラグ
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + (part.exclude?'delete':(part.zoom?'focus':'show')) + "\n";
			}
//			if(!Ext.isEmpty(part.point)){
//				key_value = '  POINT';	//POINT表示フラグ
//				while(key_value.length<key_len) key_value += ' ';
//				text_value += key_value + " - " + (part.point?1:0) + "\n";
//			}
		}
	}


//	if(convOpts.target.point_parts && !Ext.isEmpty(tpap_param.point_parts) && tpap_param.point_parts.length>0){
//		key_value = 'POINTPARTS';
//		text_value += key_value + "\n";
//
//		for(var p=0,len=tpap_param.point_parts.length;p<len;p++){
//			var part = tpap_param.point_parts[p];
//
//			if(!Ext.isEmpty(part.f_id)){
//				key_value = '  ID';	//臓器ID(FMAID)
//				while(key_value.length<key_len) key_value += ' ';
//				text_value += key_value + " - " + part.f_id + "\n";
//			}
//			if(!Ext.isEmpty(part.f_nm)){
//				key_value = '  NAME';	//臓器NAME
//				while(key_value.length<key_len) key_value += ' ';
//				text_value += key_value + " - " + part.f_nm + "\n";
//			}
//			if(!Ext.isEmpty(part.version)){
//				key_value = '  VERSION';	//バージョン
//				while(key_value.length<key_len) key_value += ' ';
//				text_value += key_value + " - " + part.version + "\n";
//			}
//			if(!Ext.isEmpty(part.color)){
//				key_value = '  COLOR';	//臓器色(RGB)
//				while(key_value.length<key_len) key_value += ' ';
//				text_value += key_value + " - " + part.color + "\n";
//			}
//			if(!Ext.isEmpty(part.value)){
//				key_value = '  SCALAR';	//スカラー値
//				while(key_value.length<key_len) key_value += ' ';
//				text_value += key_value + " - " + part.value + "\n";
//			}
//			if(!Ext.isEmpty(part.opacity)){
//				key_value = '  OPACITY';	//不透明度
//				while(key_value.length<key_len) key_value += ' ';
//				text_value += key_value + " - " + part.opacity + "\n";
//			}
//			if(!Ext.isEmpty(part.representation)){
//				key_value = '  REPRE';	//表現方法
//				while(key_value.length<key_len) key_value += ' ';
//				text_value += key_value + " - " + (part.representation=='P'?'points':(part.representation=='W'?'wireframe':'surface')) + "\n";
//			}
//			if(!Ext.isEmpty(part.exclude) || !Ext.isEmpty(part.zoom)){
//				key_value = '  STATE';	//状態フラグ
//				while(key_value.length<key_len) key_value += ' ';
//				text_value += key_value + " - " + (part.exclude?'delete':(part.zoom?'focus':'show')) + "\n";
//			}
//		}
//	}


	if(convOpts.target.legendinfo && !Ext.isEmpty(tpap_param.legendinfo)){
		key_value = 'NOTE';
//		while(key_value.length<key_len) key_value += ' ';
		text_value += key_value + "\n";

		if(!Ext.isEmpty(tpap_param.legendinfo.title)){
			key_value = '  TITLE';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - ";
			text_value += tpap_param.legendinfo.title;
			text_value += "\n";
		}

		if(!Ext.isEmpty(tpap_param.legendinfo.legend)){
			key_value = '  LEGEND';
			while(key_value.length<key_len) key_value += ' ';
			var text_arr = tpap_param.legendinfo.legend.replace(/0x0d0x0a|0x0d|0x0a|\r\n/g,"\n").replace(/\n$/g,"").split("\n");
			text_value += key_value + " - " + text_arr[0] + "\n";
			if(text_arr.length>1){
				key_value = '';
				while(key_value.length<key_len) key_value += ' ';
				for(var text_cnt=1;text_cnt<text_arr.length;text_cnt++){
					text_value += key_value + "   " + text_arr[text_cnt] + "\n";
				}
			}
		}

		if(!Ext.isEmpty(tpap_param.legendinfo.author)){
			key_value = '  AUTHOR';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - ";
			text_value += tpap_param.legendinfo.author;
			text_value += "\n";
		}

		if(!Ext.isEmpty(tpap_param.legendinfo.position)){
			key_value = '  DISP';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - ";
			text_value += tpap_param.legendinfo.position;
			text_value += "\n";
		}

		if(!Ext.isEmpty(tpap_param.legendinfo.color)){
			key_value = '  COLOR';
			while(key_value.length<key_len) key_value += ' ';
			text_value += key_value + " - ";
			text_value += tpap_param.legendinfo.color;
			text_value += "\n";
		}
	}

	if(convOpts.target.pins && !Ext.isEmpty(tpap_param.pins) && tpap_param.pins.length>0){
		key_value = 'PIN';
//		while(key_value.length<key_len) key_value += ' ';
		text_value += key_value + "\n";

		for(var p=0,len=tpap_param.pins.length;p<len;p++){
			var pin = tpap_param.pins[p];

			if(!Ext.isEmpty(pin.no)){
				key_value = '  NO';	//ピン番号
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + pin.no + "\n";
			}

			if(!Ext.isEmpty(pin.organid)){
				key_value = '  ID';	//臓器ID (FMAID)
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + pin.organid + "\n";
			}

			if(!Ext.isEmpty(pin.organname)){
				key_value = '  ORGAN';	//臓器名
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + pin.organname + "\n";
			}

			if(!Ext.isEmpty(pin.comment)){
				key_value = '  DESC';	//PINの説明
				while(key_value.length<key_len) key_value += ' ';
				var text_arr = pin.comment.replace(/0x0d0x0a|0x0d|0x0a|\r\n/g,"\n").replace(/\n$/g,"").split("\n");
				text_value += key_value + " - " + text_arr[0] + "\n";
				if(text_arr.length>1){
					key_value = '';
					while(key_value.length<key_len) key_value += ' ';
					for(var text_cnt=1;text_cnt<text_arr.length;text_cnt++){
						text_value += key_value + "   " + text_arr[text_cnt] + "\n";
					}
				}
			}

			if(!Ext.isEmpty(pin.shape)){
				key_value = '  SHAPE';	//PINの形状
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + (pin.shape=='PSS'?'Pin SS':(pin.shape=='PS'?'Pin S':(pin.shape=='PM'?'Pin M':(pin.shape=='PL'?'Pin L':(pin.shape=='CC'?'Corn':'Circle'))))) + "\n";
			}

			if(!Ext.isEmpty(pin.color)){
				key_value = '  PCOLOR';	//PINの色
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + pin.color + "\n";
			}

			if(!Ext.isEmpty(pin.tcolor)){
				key_value = '  TCOLOR';	//説明の色
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + pin.tcolor + "\n";
			}

			if(!Ext.isEmpty(pin.draw)){
				key_value = '  DRAW';	//PINの説明表示・非表示
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + pin.draw + "\n";
			}

			if(!Ext.isEmpty(pin.drawnm)){
				key_value = '  DRAWNO';	//PINの説明表示・非表示
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + pin.drawnm + "\n";
			}

			if(!Ext.isEmpty(pin.x3d) && !Ext.isEmpty(pin.y3d) && !Ext.isEmpty(pin.z3d)){
				key_value = '  COORD';	//ピン座標
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - X:" + pin.x3d + ";Y:" + pin.y3d + ";Z:" + pin.z3d + "\n";
			}

			if(!Ext.isEmpty(pin.avx3d) && !Ext.isEmpty(pin.avy3d) && !Ext.isEmpty(pin.avz3d)){
				key_value = '  VECTOR';	//法線ベクトル
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - X:" + pin.avx3d + ";Y:" + pin.avy3d + ";Z:" + pin.avz3d + "\n";
			}

			if(!Ext.isEmpty(pin.uvx3d) && !Ext.isEmpty(pin.uvy3d) && !Ext.isEmpty(pin.uvz3d)){
				key_value = '  UP';	//上方向を示す座標
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - X:" + pin.uvx3d + ";Y:" + pin.uvy3d + ";Z:" + pin.uvz3d + "\n";
			}

			if(!Ext.isEmpty(pin.coord)){
				key_value = '  SCOORD';	//描画座標系
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + pin.coord + "\n";
			}

			if(window.ag_extensions && ag_extensions.global_pin){
				if(!Ext.isEmpty(pin.PinID)){
					key_value = '  PID';
					while(key_value.length<key_len) key_value += ' ';
					text_value += key_value + " - " + pin.PinID + "\n";
				}
				if(!Ext.isEmpty(pin.PinGroupID)){
					key_value = '  PGID';
					while(key_value.length<key_len) key_value += ' ';
					text_value += key_value + " - " + pin.PinGroupID + "\n";
				}
			}

			if(!Ext.isEmpty(pin.url)){
				key_value = '  URL';	//描画座標系
				while(key_value.length<key_len) key_value += ' ';
				text_value += key_value + " - " + pin.url + "\n";
			}
		}
	}

	if(text_value == "") return undefined;
	return text_value + '//\n\n';
}

function Text2URI(aFlatTextString,aOpts){
	if(!aFlatTextString) return "";

	var defOpts = {
		target: {
			common: true,
			camera: true,
			clip: true,
			parts: true,
			point_parts: true,
			legendinfo: true,
			pins: true
		}
	};
	aOpts = aOpts||{};
	var convOpts = {};
	for(var key in defOpts){
		convOpts[key] = Ext.apply({},aOpts[key]||{},defOpts[key]);
	}

	var text_arr = aFlatTextString.replace(/0x0d0x0a|0x0d|0x0a|\r\n/g,"\n").replace(/\n$/g,"").split("\n");
	var param = {};
	var camera = 0;
	var clip = 0;
	var parts = 0;
	var point_parts = 0;
	var note = 0;
	var pin = 0;
	var grid = 0;
	var point_desc = 0;
	var parts_no = "";
	var pin_no = "";
	for(var i=0,len=text_arr.length;i<len;i++){
		next_line:
		if(convOpts.target.common && text_arr[i].match(/^VERSION\s+-\s+([0-9]{8})$/)){
			param.av = RegExp.$1;
		}else if(convOpts.target.common && text_arr[i].match(/^SIZE\s+-\s+W:([0-9]+);H:([0-9]+)$/)){
			param.iw = RegExp.$1;
			param.ih = RegExp.$2;
		}else if(convOpts.target.common && text_arr[i].match(/^BGCOLOR\s+-\s+([0-9A-Fa-f]{6})$/)){
			param.bcl = RegExp.$1;
		}else if(convOpts.target.common && text_arr[i].match(/^BGTRANS\s+-\s+([0-9]+)$/)){
			param.bga = "0";
		}else if(convOpts.target.common && text_arr[i].match(/^SCCOLOR\s+-\s+MAX:([0-9]+);MIN:([0-9]+)$/)){
			param.sx = RegExp.$1;
			param.sn = RegExp.$2;
		}else if(convOpts.target.common && text_arr[i].match(/^COLORBAR\s+-\s+([0-9]+)$/)){
			param.cf = RegExp.$1;
		}else if(convOpts.target.common && text_arr[i].match(/^HEATMAP\s+-\s+([0-9]+)$/)){
			param.hf = RegExp.$1;
		}else if(convOpts.target.common && text_arr[i].match(/^BP3DVER\s+-\s+([0-9\.]+)$/)){
			param.bv = RegExp.$1;
		}else if(convOpts.target.common && text_arr[i].match(/^TREENAME\s+-\s+([A-Za-z]+)$/)){
			param.tn = RegExp.$1;
		}else if(convOpts.target.common && text_arr[i].match(/^DATE\s+-\s+(\S.+)$/)){
			param.dt = RegExp.$1;
			if(param.dt.match(/[^0-9]+/)){
				var date = new Date(param.dt);
				var yy = date.getYear();
				var mm = date.getMonth();
				var dd = date.getDate();
				var h = date.getHours();
				var m = date.getMinutes();
				var s = date.getSeconds();
				if(yy < 2000) { yy += 1900; }
				if(mm < 10) { mm = "0" + mm; }
				if(dd < 10) { dd = "0" + dd; }
				param.dt = "" + yy + mm + dd + h + m + s;
			}
		}else if(convOpts.target.common && text_arr[i].match(/^DRAWNOTE\s+-\s+([0-9]+)$/)){
			param.dl = RegExp.$1;
		}else if(convOpts.target.common && text_arr[i].match(/^DRAWPIN\s+-\s+([0-9]+)$/)){
			param.dp = RegExp.$1;
		}else if(convOpts.target.common && text_arr[i].match(/^DRAWPINNO\s+-\s+([01]+)$/)){
			param.np = RegExp.$1;
		}else if(convOpts.target.common && text_arr[i].match(/^DRAWPINLI\s+-\s+([01]+)$/)){
			param.dpl = RegExp.$1;
		}else if(convOpts.target.common && text_arr[i].match(/^ZOOM\s+-\s+([0-9]+)$/)){
			param.zm = RegExp.$1;
			param.zm = (param.zm-1)/5;
		}else if(convOpts.target.common && (text_arr[i].match(/^GRID\s+-\s+([01]+)$/) || grid)){
			if(!grid){
				param.gdr = RegExp.$1;
				param.gdr = param.gdr=='1'?'true':'false';
				grid = 1;
			}else if(text_arr[i].match(/^\s+COLOR\s+-\s+([0-9A-Fa-f]{6})$/)){
				param.gcl = RegExp.$1;
			}else if(text_arr[i].match(/^\s+INTER\s+-\s+([0-9]+)$/)){
				param.gtc = RegExp.$1;
			}else{
				grid = 0;
				i--;
				continue;
			}

		}else if(convOpts.target.common && (text_arr[i].match(/^POINTDESC\s*$/) || point_desc)){
			if(!point_desc){
				point_desc = 1;
				param.dpod = 1;
			}else if(text_arr[i].match(/^PIN\s+-\s+([012]+)$/)){
				param.dpl = RegExp.$1;
			}else if(text_arr[i].match(/^POINT\s+-\s+([012]+)$/)){
				param.dpol = RegExp.$1;
			}else{
				point_desc = 0;
				i--;
				continue;
			}

		}else if(convOpts.target.common && text_arr[i].match(/^COORD\s+-\s+([A-Za-z0-9]+)$/)){
			param.crd = RegExp.$1;
		}else if(convOpts.target.camera && (text_arr[i].match(/^CAMERA\s*$/) || camera)){
			if(!camera){
				camera = 1;
			}else if(text_arr[i].match(/^\s+COORD\s+-\s+X:([0-9\.\-]+);Y:([0-9\.\-]+);Z:([0-9\.\-]+)$/)){
				param.cx = RegExp.$1;
				param.cy = RegExp.$2;
				param.cz = RegExp.$3;
			}else if(text_arr[i].match(/^\s+VECTOR\s+-\s+X:([0-9\.\-]+);Y:([0-9\.\-]+);Z:([0-9\.\-]+)$/)){
				param.tx = RegExp.$1;
				param.ty = RegExp.$2;
				param.tz = RegExp.$3;
			}else if(text_arr[i].match(/^\s+UP\s+-\s+X:([0-9\.\-]+);Y:([0-9\.\-]+);Z:([0-9\.\-]+)$/)){
				param.ux = RegExp.$1;
				param.uy = RegExp.$2;
				param.uz = RegExp.$3;
			}else{
				camera = 0;
				i--;
				continue;
			}
		}else if(convOpts.target.clip && (text_arr[i].match(/^CLIP\s*$/) || clip)){
			if(!clip){
				clip = 1;
			}else if(text_arr[i].match(/^\s+TYPE\s+-\s+(\S+)$/)){
				param.cm = RegExp.$1;
				if(param.cm == 'depth'){
					param.cm = 'D';
				}else if(param.cm == 'plane'){
					param.cm = 'P';
				}else{
					param.cm = 'N';
				}
			}else if(text_arr[i].match(/^\s+DEPTH\s+-\s+(\S+)$/)){
				param.cd = RegExp.$1;
			}else if(text_arr[i].match(/^\s+METHOD\s+-\s+(\S+)$/)){
				param.ct = RegExp.$1;
				if(param.ct == 'section1'){
					param.ct = 'S';
				}else if(param.ct == 'section1_normal'){
					param.ct = 'NS';
				}else{
					param.ct = 'N';
				}
			}else if(text_arr[i].match(/^\s+PARAM\s+-\s+A:([0-9\.\-]+);B:([0-9\.\-]+);C:([0-9\.\-]+);D:([0-9\.\-]+)$/)){
				param.cpa = RegExp.$1;
				param.cpb = RegExp.$2;
				param.cpc = RegExp.$3;
				param.cpd = RegExp.$4;
			}else{
				clip = 0;
				i--;
				continue;
			}
		}else if(convOpts.target.parts && (text_arr[i].match(/^PARTS\s*$/) || parts)){
			if(!parts){
				parts = 1;
			}else if(text_arr[i].match(/^\s+ID\s+-\s+(\S+)$/)){
				var val = RegExp.$1;
				parts++;
//				parts_no = (parts-1)+"";
//				while (parts_no.length < 3) parts_no = "0" + parts_no;
				parts_no = makeAnatomoOrganNumber(parts-1);
				param["oid"+parts_no] = val;
			}else if(text_arr[i].match(/^\s+NAME\s+-\s+(.+)$/)){
				var val = RegExp.$1;
				parts++;
//				parts_no = (parts-1)+"";
//				while (parts_no.length < 3) parts_no = "0" + parts_no;
				parts_no = makeAnatomoOrganNumber(parts-1);
				param["onm"+parts_no] = val;
			}else if(text_arr[i].match(/^\s+VERSION\s+-\s+([0-9\.]+)$/)){
				param["ov"+parts_no] = RegExp.$1;
			}else if(text_arr[i].match(/^\s+COLOR\s+-\s+#*([0-9A-Fa-f]{6})$/)){
				param["ocl"+parts_no] = RegExp.$1;
			}else if(text_arr[i].match(/^\s+SCALAR\s+-\s+(\S+)$/)){
				param["osc"+parts_no] = RegExp.$1;
			}else if(text_arr[i].match(/^\s+OPACITY\s+-\s+([0-9\.]+)$/)){
				param["oop"+parts_no] = RegExp.$1;
			}else if(text_arr[i].match(/^\s+REPRE\s+-\s+(\S+)$/)){
				param["orp"+parts_no] = RegExp.$1;
				if(param["orp"+parts_no] == 'surface'){
					param["orp"+parts_no] = 'S';
				}else if(param["orp"+parts_no] == 'wireframe'){
					param["orp"+parts_no] = 'W';
				}else if(param["orp"+parts_no] == 'points'){
					param["orp"+parts_no] = 'P';
				}
			}else if(text_arr[i].match(/^\s+STATE\s+-\s+(\S+)$/)){
				param["osz"+parts_no] = RegExp.$1;
				if(param["osz"+parts_no] == 'show'){
					param["osz"+parts_no] = 'S';
				}else if(param["osz"+parts_no] == 'focus'){
					param["osz"+parts_no] = 'Z';
				}else if(param["osz"+parts_no] == 'delete'){
					param["osz"+parts_no] = 'H';
				}
			}else if(text_arr[i].match(/^\s+POINT\s+-\s+(\S+)$/)){
				param["odcp"+parts_no] = RegExp.$1;
			}else{
				parts = 0;
				i--;
				continue;
			}
		}else if(convOpts.target.point_parts && (text_arr[i].match(/^POINTPARTS\s*$/) || point_parts)){
			if(!point_parts){
				point_parts = 1;
			}else if(text_arr[i].match(/^\s+ID\s+-\s+(\S+)$/)){
				var val = RegExp.$1;
				parts++;
//				parts_no = (parts-1)+"";
//				while (parts_no.length < 3) parts_no = "0" + parts_no;
				parts_no = makeAnatomoOrganNumber(parts-1);
				param["oid"+parts_no] = val;
			}else if(text_arr[i].match(/^\s+NAME\s+-\s+(.+)$/)){
				var val = RegExp.$1;
				parts++;
//				parts_no = (parts-1)+"";
//				while (parts_no.length < 3) parts_no = "0" + parts_no;
				parts_no = makeAnatomoOrganNumber(parts-1);
				param["onm"+parts_no] = val;
			}else if(text_arr[i].match(/^\s+VERSION\s+-\s+([0-9\.]+)$/)){
				param["ov"+parts_no] = RegExp.$1;
			}else if(text_arr[i].match(/^\s+COLOR\s+-\s+#*([0-9A-Fa-f]{6})$/)){
				param["ocl"+parts_no] = RegExp.$1;
			}else if(text_arr[i].match(/^\s+SCALAR\s+-\s+(\S+)$/)){
				param["osc"+parts_no] = RegExp.$1;
			}else if(text_arr[i].match(/^\s+OPACITY\s+-\s+([0-9\.]+)$/)){
				param["oop"+parts_no] = RegExp.$1;
			}else if(text_arr[i].match(/^\s+REPRE\s+-\s+(\S+)$/)){
				param["orp"+parts_no] = RegExp.$1;
				if(param["orp"+parts_no] == 'surface'){
					param["orp"+parts_no] = 'S';
				}else if(param["orp"+parts_no] == 'wireframe'){
					param["orp"+parts_no] = 'W';
				}else if(param["orp"+parts_no] == 'points'){
					param["orp"+parts_no] = 'P';
				}
			}else if(text_arr[i].match(/^\s+STATE\s+-\s+(\S+)$/)){
				param["osz"+parts_no] = RegExp.$1;
				if(param["osz"+parts_no] == 'show'){
					param["osz"+parts_no] = 'S';
				}else if(param["osz"+parts_no] == 'focus'){
					param["osz"+parts_no] = 'Z';
				}else if(param["osz"+parts_no] == 'delete'){
					param["osz"+parts_no] = 'H';
				}
			}else{
				point_parts = 0;
				i--;
				continue;
			}
		}else if(convOpts.target.legendinfo && (text_arr[i].match(/^NOTE\s*$/) || note)){
			if(!note){
				note = 1;
			}else if(text_arr[i].match(/^\s+TITLE\s+-\s+(\S.*)$/)){
				param.lt = RegExp.$1;
			}else if(text_arr[i].match(/^\s+LEGEND\s+-\s+(\S.*)$/) || text_arr[i].match(/^\s{9,}(\S.*)$/)){
				if(text_arr[i].match(/^\s+LEGEND\s+-\s+(\S.*)$/)){
					param.le = RegExp.$1;
				}else if(text_arr[i].match(/^\s{9,}(\S.*)$/)){
					param.le += ' ' + RegExp.$1;
				}
			}else if(text_arr[i].match(/^\s+AUTHOR\s+-\s+(\S.*)$/)){
				param.la = RegExp.$1;
			}else if(text_arr[i].match(/^\s+DISP\s+-\s+(\S.*)$/)){
				param.lp = RegExp.$1;
			}else if(text_arr[i].match(/^\s+COLOR\s+-\s+#*([0-9A-Fa-f]{6})$/)){
				param.lc = RegExp.$1;
			}else{
				note = 0;
				i--;
				continue;
			}
		}else if(convOpts.target.pins && (text_arr[i].match(/^PIN\s*$/) || pin)){
			if(!pin){
				pin = 1;
			}else if(text_arr[i].match(/^\s+NO\s+-\s+([0-9]+)$/)){
				var val = RegExp.$1;
//				pin_no = val+"";
//				while (pin_no.length < 3) pin_no = "0" + pin_no;
				pin_no = makeAnatomoOrganNumber(val-0);
				param["pno"+pin_no] = val;
			}else if(text_arr[i].match(/^\s+ID\s+-\s+(\S.*)$/)){
				param["poi"+pin_no] = RegExp.$1;
			}else if(text_arr[i].match(/^\s+ORGAN\s+-\s+(\S.*)$/)){
				param["pon"+pin_no] = RegExp.$1;
			}else if(text_arr[i].match(/^\s+DESC\s+-\s+(\S.*)$/) || text_arr[i].match(/^\s{9,}(\S.*)$/)){
				param["pd"+pin_no] = RegExp.$1;
			}else if(text_arr[i].match(/^\s+SHAPE\s+-\s+(\S.*)$/)){
				param["ps"+pin_no] = RegExp.$1;
				if(param["ps"+pin_no] == 'Corn'){
					param["ps"+pin_no] = 'CC';
				}else if(param["ps"+pin_no] == 'Pin L'){
					param["ps"+pin_no] = 'PL';
				}else if(param["ps"+pin_no] == 'Pin M'){
					param["ps"+pin_no] = 'PM';
				}else if(param["ps"+pin_no] == 'Pin S'){
					param["ps"+pin_no] = 'PS';
				}else if(param["ps"+pin_no] == 'Pin SS'){
					param["ps"+pin_no] = 'PSS';
				}else{
					param["ps"+pin_no] = 'SC';
				}
			}else if(text_arr[i].match(/^\s+PCOLOR\s+-\s+#*([0-9A-Fa-f]{6})$/)){
				param["pcl"+pin_no] = RegExp.$1;
			}else if(text_arr[i].match(/^\s+TCOLOR\s+-\s+#*([0-9A-Fa-f]{6})$/)){
				param["pdc"+pin_no] = RegExp.$1;
			}else if(text_arr[i].match(/^\s+DRAW\s+-\s+(\S.*)$/)){
				param["pdd"+pin_no] = RegExp.$1;
			}else if(text_arr[i].match(/^\s+DRAWNO\s+-\s+(\S.*)$/)){
				param["pnd"+pin_no] = RegExp.$1;
			}else if(text_arr[i].match(/^\s+COORD\s+-\s+X:([0-9\.\-]+);Y:([0-9\.\-]+);Z:([0-9\.\-]+)$/)){
				param["px"+pin_no] = RegExp.$1;
				param["py"+pin_no] = RegExp.$2;
				param["pz"+pin_no] = RegExp.$3;
			}else if(text_arr[i].match(/^\s+VECTOR\s+-\s+X:([0-9\.\-]+);Y:([0-9\.\-]+);Z:([0-9\.\-]+)$/)){
				param["pax"+pin_no] = RegExp.$1;
				param["pay"+pin_no] = RegExp.$2;
				param["paz"+pin_no] = RegExp.$3;
			}else if(text_arr[i].match(/^\s+UP\s+-\s+X:([0-9\.\-]+);Y:([0-9\.\-]+);Z:([0-9\.\-]+)$/)){
				param["pux"+pin_no] = RegExp.$1;
				param["puy"+pin_no] = RegExp.$2;
				param["puz"+pin_no] = RegExp.$3;
			}else if(text_arr[i].match(/^\s+SCOORD\s+-\s+(\S.*)$/)){
				param["coord"+pin_no] = RegExp.$1;
			}else if(text_arr[i].match(/^\s+URL\s+-\s+(\S.*)$/)){
			}else if(text_arr[i].match(/^\s+PID\s+-\s+(\S.*)$/)){
				if(window.ag_extensions && ag_extensions.global_pin) param["pid"+pin_no] = RegExp.$1;
			}else if(text_arr[i].match(/^\s+PGID\s+-\s+(\S.*)$/)){
				if(window.ag_extensions && ag_extensions.global_pin) param["pgid"+pin_no] = RegExp.$1;
			}else{
				pin = 0;
				i--;
				continue;
			}
		}
	}


	var search = Ext.urlEncode(param);
	var editURL = getEditUrl();
	editURL = editURL + "?tp_ap=" + encodeURIComponent(search);
	return editURL;
}


var bp3d_parts_store_fields = [
	{name:'f_id'},
	{name:'b_id'},
	{name:'name_j'},
	{name:'name_e'},
	{name:'name_k'},
	{name:'name_l'},
	{name:'phase'},
	{name:'version'},
	{name:'tg_id',convert:function(v,r){
		if(Ext.isEmpty(v)){
			return r.md_id;
		}else{
			return v;
		}
	}},
	{name:'tgi_id',convert:function(v,r){
		if(Ext.isEmpty(v)){
			return r.mv_id;
		}else{
			return v;
		}
	}},
	{name:'entry',type: 'date', dateFormat: 'timestamp'},
	{name:'xmin',type:'float'},
	{name:'xmax',type:'float'},
	{name:'ymin',type:'float'},
	{name:'ymax',type:'float'},
	{name:'zmin',type:'float'},
	{name:'zmax',type:'float'},
	{name:'volume',type:'float'},
	'taid',
	{name:'organsys'},
	{name:'color'},
	{name:'value'},
	{name:'zoom',type:'boolean'},
	{name:'exclude',type:'boolean'},
	{name:'opacity',type:'float'},
	{name:'representation'},
	{name:'def_color'},
	{name:'conv_id'},
	{name:'common_id'},
	{name:'point',type:'boolean'},
	{name:'elem_type'},
	{name:'point_label'},
	{name:'bul_id',type:'int'},
	{name:'cb_id',type:'int'},
	{name:'ci_id',type:'int'},
	{name:'md_id',type:'int'},
	{name:'mv_id',type:'int'},
	{name:'mr_id',type:'int'},
	{name:'but_cnum',type:'int'},
	{name:'icon',type:'string'},

	{name:'tweet_num',type:'int',defaultValue:0},
	{name:'tweets',type:'auto'},

	'segment',
	'seg_color',
	'seg_thum_bgcolor',
	'seg_thum_bocolor',

	'model',
	'model_version',
	'concept_info',
	'concept_build',
	'buildup_logic',
	{name:'bu_revision',type:'int'}
];

bp3d_parts_store = new Ext.data.SimpleStore({
	fields : bp3d_parts_store_fields,
	root   : 'records',
	listeners : {
		"add" : function(store,records,index){
			addPartslistGrid(store,records,index);
		},
		"remove" : function(store,record,index){
			removePartslistGrid(store,record,index);
		},
		"update" : function(store,record,operation){
			updatePartslistGrid(store,record,operation);
		},
		"clear" : function(store){
		}
	}
})
bp3d_parts_store.loadData([]);

var ag_comment_store_fields = [
	{name:'no', type:'int'},
	{name:'oid', type:'string'},
	{name:'organ', type:'string'},
	{name:'x3d', type:'float'},
	{name:'y3d', type:'float'},
	{name:'z3d', type:'float'},
	{name:'avx3d', type:'float'},
	{name:'avy3d', type:'float'},
	{name:'avz3d', type:'float'},
	{name:'uvx3d', type:'float'},
	{name:'uvy3d', type:'float'},
	{name:'uvz3d', type:'float'},
	{name:'color', type:'string'},
	{name:'comment', type:'string'},
	{name:'name_j', type:'string'},
	{name:'name_k', type:'string'},
	{name:'name_l', type:'string'},
	{name:'coord', type:'string'}
];
if(window.ag_extensions && ag_extensions.global_pin){
	if(ag_extensions.global_pin.store_field_pin) ag_comment_store_fields = ag_comment_store_fields.concat(ag_extensions.global_pin.store_field_pin());
	if(ag_extensions.global_pin.store_field_pin_group) ag_comment_store_fields = ag_comment_store_fields.concat(ag_extensions.global_pin.store_field_pin_group());
}

var ag_comment_store = new Ext.data.SimpleStore({
	fields : ag_comment_store_fields,
	root : 'records',
	listeners : {
		'add' : function(store,records,index){
			if(Ext.isEmpty(records) || records.length==0 || index<0) return;

			var grid = Ext.getCmp('anatomography-pin-grid-panel');
			if(grid && grid.rendered){
				setTimeout(function(){try{
					grid.getView().focusRow(index);
					grid.getSelectionModel().selectRow(index);
				}catch(e){}},100);
			}

			var pick_data = {f_ids:[]};
			for(var i=0;i<records.length;i++){
				if(Ext.isEmpty(records[i].data.organ)) pick_data.f_ids.push(records[i].data.oid);
			}
			if(pick_data.f_ids.length>0){
				pick_data.f_ids = Ext.util.JSON.encode(pick_data.f_ids);
				try{pick_data.version = Ext.getCmp('bp3d-version-combo').getValue();}catch(e){pick_data.version=init_bp3d_version;}

				if(init_bp3d_params.version) pick_data.version = init_bp3d_params.version;
				if(init_bp3d_params.t_type) pick_data.t_type = init_bp3d_params.t_type;
				if(init_bp3d_params.tgi_id) pick_data.tgi_id = init_bp3d_params.tgi_id;
				if(init_bp3d_params.md_id) pick_data.md_id = init_bp3d_params.md_id;
				if(init_bp3d_params.mv_id) pick_data.mv_id = init_bp3d_params.mv_id;
				if(init_bp3d_params.mr_id) pick_data.mr_id = init_bp3d_params.mr_id;
				if(init_bp3d_params.bul_id) pick_data.bul_id = init_bp3d_params.bul_id;
				if(init_bp3d_params.cb_id) pick_data.cb_id = init_bp3d_params.cb_id;
				if(init_bp3d_params.ci_id) pick_data.ci_id = init_bp3d_params.ci_id;

				Ext.Ajax.request({
					url     : 'get-contents.cgi',
					method  : 'POST',
					params  : Ext.urlEncode(pick_data),
					success : function(conn,response,options){
						try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
						if(results && results.images && results.images.length>0){
							for(var i=0;i<results.images.length;i++){
								var startIndex = 0;
								while(1){
									var rtnIndex = ag_comment_store.find('oid',new RegExp("^"+results.images[i].f_id+"$"),startIndex,true,true);
									if(rtnIndex>=startIndex){
										var rec = ag_comment_store.getAt(rtnIndex);
										if(rec){
											rec.beginEdit();
											rec.set("organ", results.images[i].name_e);
											rec.set("name_j",results.images[i].name_j);
											rec.set("name_k",results.images[i].name_k);
											rec.set("name_l",results.images[i].name_l);
											rec.commit();
											rec.endEdit();
										}
										startIndex = rtnIndex +1;
									}else{
										break;
									}
								}
							}
						}
						updateAnatomo();
					},
					failure : function(conn,response,options){
						updateAnatomo();
					}
				});
			}else{
				updateAnatomo();
			}
		},
		'remove' : function(store,record,index){
		},
		'update' : function(store,record,operation){
		},
		'clear' : function(store){
		}
	}
});

fma_search_store = new Ext.data.JsonStore({
	url: 'get-fma.cgi',
	pruneModifiedRecords : true,
	totalProperty : 'total',
	root: 'records',
//	remoteSort: true,
//	sortInfo: {field: 'volume', direction: 'DESC'},
	fields: [
		'f_id',
		'b_id',
		'name_j',
		'name_e',
		'name_k',
		'name_l',
		'syn_j',
		'syn_e',
		'def_e',
		'organsys_j',
		'organsys_e',
		'text',
		'name',
		'organsys',
		'phase',
		{name:'xmin',   type:'float'},
		{name:'xmax',   type:'float'},
		{name:'ymin',   type:'float'},
		{name:'ymax',   type:'float'},
		{name:'zmin',   type:'float'},
		{name:'zmax',   type:'float'},
		{name:'volume', type:'float'},
		'taid',
		'physical',
		{name:'phy_id',type:'int'},
		'segment',
		'seg_color',
		'seg_thum_bgcolor',
		'seg_thum_bocolor',
		{name:'seg_id',type:'int'},
		'version',
		'tg_id',
		'tgi_id',
		{name:'md_id',type:'int'},
		{name:'mv_id',type:'int'},
		{name:'mr_id',type:'int'},
		{name:'ci_id',type:'int'},
		{name:'cb_id',type:'int'},
		{name:'bul_id',type:'int'},

		{name:'tweet_num',type:'int',defaultValue:0},
		{name:'tweets',type:'auto'},

		'model',
		'model_version',
		'concept_info',
		'concept_build',
		'buildup_logic',
		{name:'icon',type:'string'},
		{name:'bu_revision',type:'int'},
		'state',
		'def_color',
		{name:'entry', type:'date', dateFormat:'timestamp'},
		{name:'lastmod', type:'date', dateFormat:'timestamp'}
	],
	listeners: {
		'beforeload' : {
			fn:function(self,options){
				try{
					self.baseParams = self.baseParams || {};
					delete gParams.parent;
					if(!Ext.isEmpty(gParams.parent)) self.baseParams.parent = gParams.parent;
					self.baseParams.lng = gParams.lng;
					try{var bp3d_version = Ext.getCmp('bp3d-version-combo').getValue();}catch(e){_dump("fma_search_store.beforeload():e=["+e+"]");bp3d_version='4.1';}
					if(!Ext.isEmpty(bp3d_version)) self.baseParams.version = bp3d_version;
				}catch(e){
					_dump("fma_search_store.beforeload():"+e);
				}
				for(var key in init_bp3d_params){
					if(key.match(/_id$/)) self.baseParams[key] = init_bp3d_params[key];
				}

				try{
					var store = Ext.getCmp('bp3d-version-combo').getStore();
					var idx = store.findBy(function(record,id){
						if(record.data.tgi_version==self.baseParams.version) return true;
					});
					if(idx>=0){
						var record = store.getAt(idx);
						if(record){
							self.baseParams.md_id = record.data.md_id;
							self.baseParams.mv_id = record.data.mv_id;
							self.baseParams.mr_id = record.data.mr_id;
							self.baseParams.ci_id = record.data.ci_id;
							self.baseParams.cb_id = record.data.cb_id;
						}
					}
				}catch(e){}
			},
			scope:this
		},
		'load': {
			fn:function(self,records,options){
			},
			scope:this,
			single:true
		},
		'datachanged':{
			fn:function(self){
			},scope:this
		},
		'loadexception': {
			fn:function(){
			},scope:this
		}
	}
});

var addPartslistGrid_timer = null;
function addPartslistGrid(store,records,index){
	var zoom = false;
//_dump("addPartslistGrid():gDispAnatomographyPanel=["+gDispAnatomographyPanel+"]");
	if(!gDispAnatomographyPanel){
		zoom = true;
		for(var i=store.getCount()-1;i>=0;i--){
			try{
				var record = store.getAt(i);
				if(record) record.set('zoom',true);
			}catch(e){}
		}
	}

	ag_parts_store = store;
	if(zoom){
		if(addPartslistGrid_timer) clearTimeout(addPartslistGrid_timer);
		addPartslistGrid_timer = setTimeout(function(){
			addPartslistGrid_timer = null;
			ag_focus(true);
		},500);
	}else{
		if(!updateClipImage()) updateAnatomo();
	}
	update_anatomography_point_grid(records);
	try{update_ag_fma_search_grid(records);}catch(e){}

	setTimeout(function(){
		try{
			var sel = ag_parts_gridpanel.getSelectionModel();
			try{sel.clearSelections();}catch(e){}
			var g_store = ag_parts_gridpanel.getStore();
			var g_count = g_store.getCount();
			for(var i=0;i<g_count;i++){
				var record = g_store.getAt(i);
				if(record.get('zoom') && !sel.isSelected(i)) sel.selectRow(i,true);
			}
		}catch(e){}
	},0);
	setEmptyGridText();
}

function removePartslistGrid(store,record,index){
	if(store.getCount()==0){
		var cmp = Ext.getCmp('contents-tab-panel');
		if(cmp && cmp.getActiveTab().id == 'contents-tab-bodyparts-panel'){
			gDispAnatomographyPanel = false;
		}
		Ext.getCmp('bp3d-home-group-btn').disable();
		try{
			var bp3d_grid = Ext.getCmp('control-tab-partslist-panel');
			if(bp3d_grid){
				var cmodel = bp3d_grid.getColumnModel();
				var index = cmodel.getIndexById('conv_id');
				cmodel.setHidden(index,true);
			}else{
				bp3d_grid = undefined;
			}
		}catch(e){}
		try{
			var ag_grid = Ext.getCmp('ag-parts-gridpanel');
			if(ag_grid){
				var cmodel = ag_grid.getColumnModel();
				var index = cmodel.getIndexById('conv_id');
				cmodel.setHidden(index,true);
			}else{
				ag_grid = undefined;
			}
		}catch(e){}
	}

	ag_parts_store = store;
	if(!updateClipImage()) updateAnatomo();
	update_anatomography_point_grid(record);
	try{update_ag_fma_search_grid(record);}catch(e){}

	setTimeout(function(){
		try{
			var sel = ag_parts_gridpanel.getSelectionModel();
			try{sel.clearSelections();}catch(e){}
			var g_store = ag_parts_gridpanel.getStore();
			var g_count = g_store.getCount();
			for(var i=0;i<g_count;i++){
				var record = g_store.getAt(i);
				if(record.get('zoom') && !sel.isSelected(i)) sel.selectRow(i,true);
			}
		}catch(e){
			_dump("removePartslistGrid():"+e);
		}
	},0);
	setEmptyGridText();
}

function updatePartslistGrid(store,record,operation){
	ag_parts_store = store;
	if(!updateClipImage()) updateAnatomo();
	update_anatomography_point_grid(record);
	try{update_ag_fma_search_grid(record);}catch(e){}
}

var resizeGridPanelColumns = function(grid){
	try{
		var column = grid.getColumnModel();
		var innerWidth = grid.getInnerWidth();
		var totalWidth = column.getTotalWidth(false);
		var columnCount = column.getColumnCount();
		var columnNum = 0;
		for(var i=0;i<columnCount;i++){
			if(column.isHidden(i)){
				continue;
			}
			if(column.isHidden(i) || column.isFixed(i) || !column.isResizable(i) || column.config[i].resizable){
				innerWidth -= column.getColumnWidth(i);
				continue;
			}
			if(column.isResizable(i)) columnNum++;
		}
		if(columnNum==0) return;
		var columnWidth = parseInt((innerWidth-21)/columnNum);
		for(var i=0;i<columnCount;i++){
			if(column.isHidden(i) || column.isFixed(i) || !column.isResizable(i) || column.config[i].resizable) continue;
			if(column.isResizable(i)) column.setColumnWidth(i,columnWidth);
		}
	}catch(e){
		for(var ekey in e){
			_dump('resizeGridPanelColumns():'+ekey+'=['+e[ekey]+']');
		}
	}
};

var saveHiddenGridPanelColumns = function(grid,id){
	if(Ext.isEmpty(id)) id = grid.getId();
	var columnModel = grid.getColumnModel();
	var count = columnModel.getColumnCount();
	var hash = {};
	for(var i=0;i<count;i++){
		if(columnModel.isFixed(i)) continue;
		hash[columnModel.getColumnId(i)] = columnModel.isHidden(i);
	}
	glb_us_state[id+'-columns-hidden'] = hash;

	ag_put_usersession_task.delay(1000);

//	var json = Ext.util.JSON.encode(hash);
//	Cookies.set(id+'-columns-hidden',json);
Cookies.clear(id+'-columns-hidden');
//_dump("saveHiddenGridPanelColumns():"+json);
};

var isPointDataRecord = function(record){
	if(record.data.elem_type=='bp3d_point') return true;
	return false;
};
var isNoneDataRecord = function(record){
	if(!Ext.isEmpty(record.data.zmax)) return false;
	if(!Ext.isEmpty(record.data.elem_type) && isPointDataRecord(record)) return false;
	return true;
};

var restoreHiddenGridPanelColumns = function(grid,id){
	if(Ext.isEmpty(id)) id = grid.getId();
	if(Ext.isEmpty(glb_us_state[id+'-columns-hidden'])) return;
	var hash = glb_us_state[id+'-columns-hidden'];

//	var json = Cookies.get(id+'-columns-hidden');
//_dump("restoreHiddenGridPanelColumns():"+json);
//	if(!json) return;
	var columnModel = grid.getColumnModel();
//	var hash = Ext.util.JSON.decode(json);
	for(var key in hash){
		var index = columnModel.getIndexById(key);
		if(index<0) continue;
		if(columnModel.isFixed(index)) continue;
		columnModel.setHidden(index,hash[key]);
	}
};

setEmptyGridText = function(){
	return;
};

var point_search = function(imgX,imgY,voxelRadius){
	if(Ext.isEmpty(voxelRadius) || (voxelRadius-0)<5) voxelRadius = 5;
	try{
		ag_comment_tabpanel.getActiveTab().loadMask.show();

		$(Ext.getCmp('ag-point-search-editorgrid-panel').getBottomToolbar().items.last().el).text('- / -')

		Ext.getCmp('ag-point-search-header-content-more-button').setDisabled(true);

		clear_point_f_id();
//		var params = makeAnatomoPrm();
//		_loadAnatomo(params,true);

		var store = Ext.getCmp('ag-point-search-editorgrid-panel').getStore();
		store.removeAll();
		delete store.baseParams.f_id;

		Ext.getCmp('ag-point-search-header-content-screen-x-text').setValue(imgX);
		Ext.getCmp('ag-point-search-header-content-screen-y-text').setValue(imgY);
		var cr = Ext.getCmp('ag-point-search-header-content-voxel-range-text');
		if(cr){
			cr.setValue(voxelRadius);
			cr.fireEvent('change',cr,voxelRadius);
		}

		var cx = Ext.getCmp('ag-point-search-header-content-coordinate-x-text');
		if(cx){
			cx.setValue('');
			cx.fireEvent('change',cx,'');
		}
		var cy = Ext.getCmp('ag-point-search-header-content-coordinate-y-text');
		if(cy){
			cy.setValue('');
			cy.fireEvent('change',cy,'');
		}
		var cz = Ext.getCmp('ag-point-search-header-content-coordinate-z-text');
		if(cz){
			cz.setValue('');
			cz.fireEvent('change',cz,'');
		}

		var urlStr = cgipath.pointSearch;
		var params = Ext.urlDecode(makeAnatomoPrm(null,1),true);
		params.px = imgX;
		params.py = imgY;
		params.vr = voxelRadius;

		var jsonStr = null;
		try{
			jsonStr = ag_extensions.toJSON.URI2JSON(params,{
				toString:true,
				mapPin:false,
				callback:undefined
			});
		}catch(e){jsonStr = null;}

		Ext.Ajax.request({
			url    : urlStr,
			method : 'POST',
			params : jsonStr ? jsonStr : params,
			success: function (response, options) {
				try{var pointData = Ext.util.JSON.decode(response.responseText);}catch(e){_dump(e);}
				if(Ext.isEmpty(pointData) || Ext.isEmpty(pointData.id)){
					ag_comment_tabpanel.getActiveTab().loadMask.hide();
					if(ag_extensions && ag_extensions.pick_point && ag_extensions.pick_point.hide) ag_extensions.pick_point.hide();
					return;
				}

				Ext.getCmp('ag-point-search-header-content-more-button').setDisabled(false);

				var tx = parseInt(parseFloat(pointData.worldPosX)*1000)/1000;
				var ty = parseInt(parseFloat(pointData.worldPosY)*1000)/1000;
				var tz = parseInt(parseFloat(pointData.worldPosZ)*1000)/1000;

				var cx = Ext.getCmp('ag-point-search-header-content-coordinate-x-text');
				if(cx){
					cx.setValue(tx);
					cx.fireEvent('change',cx,tx);
				}
				var cy = Ext.getCmp('ag-point-search-header-content-coordinate-y-text');
				if(cy){
					cy.setValue(ty);
					cy.fireEvent('change',cy,ty);
				}
				var cz = Ext.getCmp('ag-point-search-header-content-coordinate-z-text');
				if(cz){
					cz.setValue(tz);
					cz.fireEvent('change',cz,tz);
				}

				var store = Ext.getCmp('ag-point-search-editorgrid-panel').getStore();
				store.baseParams.f_id = pointData.id;
				var newRecord = Ext.data.Record.create(ag_point_search_fields);
				var recs = [];
				Ext.each(pointData.ids,function(o,i,a){
					recs.push(new newRecord(o));
				});
				store.add(recs)

				$(Ext.getCmp('ag-point-search-editorgrid-panel').getBottomToolbar().items.last().el).text(pointData.ids.length + ' / ' + pointData.total)

				Ext.getCmp('ag-point-search-header-content-more-button').setDisabled(pointData.ids.length<pointData.total?true:false);

				set_point_f_id(pointData.id);
				var params = makeAnatomoPrm();
				_loadAnatomo(params,true);
				ag_comment_tabpanel.getActiveTab().loadMask.hide();
				if(ag_extensions && ag_extensions.pick_point && ag_extensions.pick_point.hide) ag_extensions.pick_point.hide();
			},
			failure: function (response, options) {
				try{alert(cgipath.pointSearch+":failure():"+response.status+":"+response.statusText);}catch(e){}
				ag_comment_tabpanel.getActiveTab().loadMask.hide();
				if(ag_extensions && ag_extensions.pick_point && ag_extensions.pick_point.hide) ag_extensions.pick_point.hide();
			}
		});
	}catch(e){
		try{
			ag_comment_tabpanel.getActiveTab().loadMask.hide();
		}catch(e){}
	}
};



function add_bp3d_parts_store_parts_from_TPAP(tp_ap,aCB){
	var tpap_param = analyzeTPAP(tp_ap);
	if(Ext.isEmpty(tpap_param)) return;
	var newRecord = Ext.data.Record.create(bp3d_parts_store_fields);
	var addrecs = [];

	if(tpap_param.parts && tpap_param.parts.length>0 && bp3d_parts_store_fields){
		var prm_record = ag_param_store.getAt(0);
//		console.log(tpap_param.parts);
		for(var j=0,len=tpap_param.parts.length;j<len;j++){
			var parts = tpap_param.parts[j];

			var idx=-1;
			if(!Ext.isEmpty(parts.f_id)){
				idx = bp3d_parts_store.find('f_id',new RegExp('^'+parts.f_id+'$'));
			}else if(!Ext.isEmpty(parts.b_id)){
				idx = bp3d_parts_store.find('b_id',new RegExp('^'+parts.b_id+'$'));
			}
			if(idx>=0) continue;

			var addrec = new newRecord({});
			addrec.beginEdit();
			for(var fcnt=0;fcnt<addrec.fields.items.length;fcnt++){
				var fname = addrec.fields.items[fcnt].name;
				var fdefaultValue = addrec.fields.items[fcnt].defaultValue;
				addrec.set(fname,fdefaultValue);
			}

			if(!Ext.isEmpty(parts.f_id)) addrec.set("f_id",parts.f_id);
			if(!Ext.isEmpty(parts.f_nm)) addrec.set("name_e",parts.f_nm);
			if(!Ext.isEmpty(parts.color)) addrec.set("color",'#'+parts.color);
			if(!Ext.isEmpty(parts.value)) addrec.set("value",parts.value);
			if(!Ext.isEmpty(parts.exclude)) addrec.set("exclude",parts.exclude);
			if(!Ext.isEmpty(parts.zoom)) addrec.set("zoom",parts.zoom);
			if(!Ext.isEmpty(parts.opacity)) addrec.set("opacity",parts.opacity);
			if(!Ext.isEmpty(parts.representation)) addrec.set("representation",parts.representation);
			if(!Ext.isEmpty(parts.point)) addrec.set("point",parts.point);
			if(!Ext.isEmpty(parts.b_id)){
				addrec.set("b_id",parts.b_id);
				if(!Ext.isEmpty(parts.conv_id)){
					addrec.set("conv_id",parts.conv_id);
				}else{
					addrec.set("conv_id",parts.b_id);
				}
			}

			addrec.commit(true);
			addrec.endEdit();
			addrecs.push(addrec);
		}
	}
	if(addrecs.length>0) bp3d_parts_store.add(addrecs);
	return addrecs;
}

function add_comment_store_pins_from_TPAP(tp_ap){
	var tpap_param = analyzeTPAP(tp_ap);
	if(Ext.isEmpty(tpap_param)) return;

	var newRecord = Ext.data.Record.create(ag_comment_store_fields);
	var addrecs = [];
	var pin_no = ag_comment_store.getCount();

	if(tpap_param.comments && tpap_param.comments.length>0){
		for (var i = 0, len = tpap_param.comments.length; i < len; i++) {
			var comment = tpap_param.comments[i];
			var addrec = new newRecord({});
			addrec.beginEdit();
			for(var fcnt=0;fcnt<addrec.fields.items.length;fcnt++){
				var fname = addrec.fields.items[fcnt].name;
				var fdefaultValue = addrec.fields.items[fcnt].defaultValue;
				addrec.set(fname,fdefaultValue);
			}
			addrec.set("no",   ++pin_no);
			addrec.set("x3d",    parseFloatTPAP(comment.c3d.x));
			addrec.set("y3d",    parseFloatTPAP(comment.c3d.y));
			addrec.set("z3d",    parseFloatTPAP(comment.c3d.z));
			addrec.set("avx3d",  "");
			addrec.set("avy3d",  "");
			addrec.set("avz3d",  "");
			addrec.set("uvx3d",  "");
			addrec.set("uvy3d",  "");
			addrec.set("uvz3d",  "");
			addrec.set("color",  comment.point.rgb);
			addrec.set("oid",    comment.id);
			addrec.set("organ",  comment.name);
			addrec.set("comment",(comment.comment?comment.comment:""));
			addrec.set("coord",  "");
			addrec.commit(true);
			addrec.endEdit();
			addrecs.push(addrec);
		}
	}else if(tpap_param.pins && tpap_param.pins.length>0 && ag_comment_store_fields){
		for(var j=0,len=tpap_param.pins.length;j<len;j++){
			var pin = tpap_param.pins[j];
			var addrec = new newRecord({});
			addrec.beginEdit();
			for(var fcnt=0;fcnt<addrec.fields.items.length;fcnt++){
				var fname = addrec.fields.items[fcnt].name;
				var fdefaultValue = addrec.fields.items[fcnt].defaultValue;
				addrec.set(fname,fdefaultValue);
			}
			addrec.set("no",++pin_no);
			addrec.set("x3d",pin.x3d);
			addrec.set("y3d",pin.y3d);
			addrec.set("z3d",pin.z3d);
			addrec.set("avx3d",pin.avx3d);
			addrec.set("avy3d",pin.avy3d);
			addrec.set("avz3d",pin.avz3d);
			addrec.set("uvx3d",pin.uvx3d);
			addrec.set("uvy3d",pin.uvy3d);
			addrec.set("uvz3d",pin.uvz3d);
			addrec.set("color",pin.color);
			addrec.set("oid",pin.organid);
			addrec.set("organ",pin.organname);
			addrec.set("comment",(pin.comment?pin.comment:""));
			addrec.set("coord",  pin.coord);
			if(window.ag_extensions && ag_extensions.global_pin){
				if(!Ext.isEmpty(pin.PinID)) addrec.set("PinID", pin.PinID);
				if(!Ext.isEmpty(pin.PinGroupID)) addrec.set("PinGroupID", pin.PinGroupID);
			}
			addrec.commit(true);
			addrec.endEdit();
			addrecs.push(addrec);
		}
	}
	if(addrecs.length>0) ag_comment_store.add(addrecs);
}


function export_parts_pins(aOpts){

	aOpts = Ext.apply({},aOpts||{},{
		title    : 'Export',
		width    : 500,
		height   : 500,
		plain    : true,
		modal    : true,
		resizable: true,
		animateTarget: null
	});

	var cur_text = URI2Text(glb_anatomo_editor_url,{target:{pins:false}});
	var cur_url = Text2URI(cur_text,{target:{pins:false}});

	var convOpts = {
		target: {
			common: false,
			camera: false,
			clip: false,
			parts: true,
			point_parts: false,
			legendinfo: false,
			pins: true
		},
		pin: {
			url_prefix : cur_url+encodeURIComponent('&')
		}
	};


	function get_text(){
		var value = URI2Text(glb_anatomo_editor_url,convOpts);
		return value;
	}
	var text_value = get_text();
	if(Ext.isEmpty(text_value)) return;

	var url_short_value = "";
	var url_long_value = Text2URI(text_value,convOpts);
	if(Ext.isEmpty(url_long_value)) return;

	function change_checked(field,checked){
		convOpts.target[field.name] = checked;
		text_value = get_text();
		url_short_value = "";
		url_long_value = "";
		if(text_value != ""){
			url_long_value = Text2URI(text_value,convOpts);
			if(url_long_value != ""){
				update_open_url2text(url_long_value,function(url){
					url_short_value = url;
					Ext.getCmp('ag_export_short_url_textfield').setValue(url_short_value);
				});
			}
		}
		Ext.getCmp('ag_export_table_textarea').setValue(text_value);
		Ext.getCmp('ag_export_long_url_textfield').setValue(url_long_value);
		Ext.getCmp('ag_export_short_url_textfield').setValue(url_short_value);
	}

	var win = new Ext.Window({
		title       : aOpts.title,
		animateTarget: aOpts.animateTarget,
		width       : aOpts.width,
		height      : aOpts.height,
		plain       : aOpts.plain,
		bodyStyle   : 'padding:5px;',
		buttonAlign : 'right',
		modal       : aOpts.modal,
		resizable   : aOpts.resizable,
		items       : [{
			xtype:'fieldset',
			title: 'Export',
			autoHeight: true,
			layout: 'table',
			layoutConfig: {
				columns: 2
			},
			items:[{
				xtype: 'checkbox',
				boxLabel: 'Parts',
				name: 'parts',
				checked: convOpts.target.parts,
				width: 100,
				listeners: {
					check: change_checked
				}
			},{
				xtype: 'checkbox',
				boxLabel: 'Pins',
				name: 'pins',
				checked: convOpts.target.pins,
				width: 100,
				listeners: {
					check: change_checked
				}
			}]
		},{
			xtype:'fieldset',
			title: 'Message URL',
			autoHeight: true,
			labelAlign: 'right',
			labelWidth: 40,
			items:[{
				xtype         : 'textfield',
				id            : 'ag_export_short_url_textfield',
				fieldLabel    : 'Short',
				anchor        : '100%',
				readOnly      : true,
				selectOnFocus : true,
				value         : url_short_value,
				listeners: {
					render: function(comp){
						update_open_url2text(url_long_value,function(url){
							comp.setValue(url);
						});
					}
				}
			},{
				xtype         : 'textfield',
				id            : 'ag_export_long_url_textfield',
				fieldLabel    : 'Long',
				anchor        : '100%',
				readOnly      : true,
				selectOnFocus : true,
				value         : url_long_value
			}]
		},{
			xtype:'fieldset',
			title: 'Table',
			autoHeight: true,
			layout: 'fit',
			items: [{
				xtype: 'textarea',
				id: 'ag_export_table_textarea',
				style: 'font-family:Courier;monospace;',
				readOnly: true,
				selectOnFocus: true,
				value: text_value,
				anchor: '100%',
				height: 220
			}]
		}],
		buttons : [{
			text: 'Close',
			handler: function(){
				win.close();
			}
		}]
	});
	win.show();
}
/////////////////////////////////////////////////////////////////////////////////////////////////////
// ag_common_js.cgiから移植（ここまで）
/////////////////////////////////////////////////////////////////////////////////////////////////////

/////////////////////////////////////////////////////////////////////////////////////////////////////
// anatomography_js.cgiから移植（ここから）
/////////////////////////////////////////////////////////////////////////////////////////////////////
Ext.ux.SliderTip = Ext.extend(Ext.Tip, {
	minWidth: 10,
	offsets : [20, 20],
	init : function(slider){
		slider.on('dragstart', this.onSlide, this);
		slider.on('drag', this.onSlide, this);
		slider.on('dragend', this.hide, this);
		slider.on('destroy', this.destroy, this);
	},
	onSlide : function(slider){
		this.show();
		this.body.update(this.getText(slider));
		this.doAutoWidth();
		this.el.alignTo(slider.thumb, 'b-t?', this.offsets);
	},
	getText : function(slider){
		return slider.getValue() + 1;
	}
});

var tip = new Ext.ux.SliderTip ({
	getText: function(slider) {
//		return String.format('<b>{0}</b>', parseInt(slider.getValue()) -1000);
		return String.format('<b>{0}</b>', parseInt(slider.getValue()));
	}
});

var tip_depth = new Ext.ux.SliderTip ({
	getText: function(slider) {
//		return String.format('<b>{0}</b>', parseInt(slider.getValue()) -1000);
		return String.format('<b>{0}</b>', parseInt(slider.getValue()));
	}
});

var ag_parts_gridpanel_col_opacity_arr = [
	['1.0',  '1.0'],
	['0.8',  '0.8'],
	['0.6',  '0.6'],
	['0.4',  '0.4'],
	['0.3',  '0.3'],
	['0.2',  '0.2'],
	['0.1',  '0.1'],
	['0.05', '0.05'],
	['0.0',  '0.0']
];

var ag_parts_gridpanel_col_representation_arr = [
	['surface', 'surface'],
	['wireframe', 'wireframe'],
	['points', 'points']
];

var ag_parts_gridpanel_color_cell_style = function (val) {
	return '<span style="background-color:' + val + '">&nbsp;&nbsp;&nbsp;&nbsp;</span>';
};

function tabChange(tabPanel,tab){
	//タブが変更された時にコールされる
	updateAnatomo();
}

function ag_focus(aClearZoom,aCenteringOnly) {
//_dump('focus()');
	if(Ext.isEmpty(aClearZoom)) aClearZoom = false;
	if(Ext.isEmpty(aCenteringOnly)) aCenteringOnly = false;

//	var urlStr = cgipath.focus+'?' + makeAnatomoPrm();

	var params = Ext.urlDecode(makeAnatomoPrm());
	var jsonStr = null;
	try{
		jsonStr = ag_extensions.toJSON.URI2JSON(params,{
			toString:true,
			mapPin:false,
			callback:undefined
		});
	}catch(e){jsonStr = null;}

	var urlStr = cgipath.focus;
	Ext.Ajax.request({
		url     : urlStr,
		method  : 'POST',
		params  : jsonStr ? jsonStr : params,
		success : function (response, options) {
			try{
				var targetXYZYRange = Ext.util.JSON.decode(response.responseText);
			}catch(e){
				_dump(e);
				return;
			}
			if(targetXYZYRange.Camera){
				m_ag.cameraPos.x = parseFloat(m_ag.cameraPos.x) + parseFloat(targetXYZYRange.Camera.TargetX) - parseFloat(m_ag.targetPos.x);
				m_ag.cameraPos.y = parseFloat(m_ag.cameraPos.y) + parseFloat(targetXYZYRange.Camera.TargetY) - parseFloat(m_ag.targetPos.y);
				m_ag.cameraPos.z = parseFloat(m_ag.cameraPos.z) + parseFloat(targetXYZYRange.Camera.TargetZ) - parseFloat(m_ag.targetPos.z);
				m_ag.targetPos.x = parseFloat(targetXYZYRange.Camera.TargetX);
				m_ag.targetPos.y = parseFloat(targetXYZYRange.Camera.TargetY);
				m_ag.targetPos.z = parseFloat(targetXYZYRange.Camera.TargetZ);

//				m_ag.cameraPos.x = parseFloat(targetXYZYRange.Camera.CameraX);
//				m_ag.cameraPos.y = parseFloat(targetXYZYRange.Camera.CameraY);
//				m_ag.cameraPos.z = parseFloat(targetXYZYRange.Camera.CameraZ);
//				m_ag.targetPos.x = parseFloat(targetXYZYRange.Camera.TargetX);
//				m_ag.targetPos.y = parseFloat(targetXYZYRange.Camera.TargetY);
//				m_ag.targetPos.z = parseFloat(targetXYZYRange.Camera.TargetZ);
//				m_ag.upVec.x = parseFloat(targetXYZYRange.Camera.CameraUpVectorX);
//				m_ag.upVec.y = parseFloat(targetXYZYRange.Camera.CameraUpVectorY);
//				m_ag.upVec.z = parseFloat(targetXYZYRange.Camera.CameraUpVectorZ);

			}else{
				m_ag.cameraPos.x = parseFloat(m_ag.cameraPos.x) + parseFloat(targetXYZYRange.targetPosX) - parseFloat(m_ag.targetPos.x);
				m_ag.cameraPos.y = parseFloat(m_ag.cameraPos.y) + parseFloat(targetXYZYRange.targetPosY) - parseFloat(m_ag.targetPos.y);
				m_ag.cameraPos.z = parseFloat(m_ag.cameraPos.z) + parseFloat(targetXYZYRange.targetPosZ) - parseFloat(m_ag.targetPos.z);
				m_ag.targetPos.x = parseFloat(targetXYZYRange.targetPosX);
				m_ag.targetPos.y = parseFloat(targetXYZYRange.targetPosY);
				m_ag.targetPos.z = parseFloat(targetXYZYRange.targetPosZ);
			}

			setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);

			if(!aCenteringOnly){
				var slider = Ext.getCmp('zoom-slider');
				var sliderValue = 0;
				if(targetXYZYRange.Camera){
					sliderValue = targetXYZYRange.Camera.Zoom;
				}else{
					sliderValue = Math.round((parseFloat(Math.log(1800) / Math.LN2) - parseFloat(Math.log(targetXYZYRange.yrange) / Math.LN2)) * 5 - 0.5);
				}
				glb_zoom_slider = sliderValue+1;
				if(slider && slider.rendered){
					slider.setValue(sliderValue);
				}else{
					var prm_record =ag_param_store.getAt(0);
					prm_record.beginEdit();
					prm_record.set('zoom', glb_zoom_slider / 5);
					prm_record.endEdit();
					prm_record.commit();
				}
			}
			updateAnatomo();

			if(aClearZoom){
				var grid = Ext.getCmp('ag-parts-gridpanel');
				try{grid.getSelectionModel().clearSelections();}catch(e){}
				var store = grid.getStore();
				var records = store.getRange();
				for(var i=records.length-1;i>=0;i--){
					var record = records[i];
					if(record){
						record.beginEdit();
						record.set('zoom',false);
						record.commit(true);
						record.endEdit();
					}
				}
			}
		}
	});
}

function oncheck_anatomo_clip_check(checkbox, fChecked){
	try{
		var prm_record =ag_param_store.getAt(0);
		var method = Ext.getCmp('anatomo-clip-method-combo');
		var plane = Ext.getCmp('anatomo-clip-predifined-plane');
		var fix = Ext.getCmp('anatomo-clip-fix-check');
		var reverse = Ext.getCmp('anatomo-clip-reverse-check');
		var slider = Ext.getCmp('anatomo-clip-slider');
		var buttonUp = document.getElementById('anatomo-clip-up-button');
		var buttonDown = document.getElementById('anatomo-clip-down-button');
		var textField = Ext.getCmp('anatomo-clip-value-text');
		var clipImgDiv = document.getElementById('clipImgDiv');

		var buttonSliderUp = Ext.get('anatomo-clip-slider-up-button');
		var buttonSliderDown = Ext.get('anatomo-clip-slider-down-button');
		var buttonTextUp = Ext.get('anatomo-clip-text-up-button');
		var buttonTextDown = Ext.get('anatomo-clip-text-down-button');
		var labelClipUnit = Ext.get('anatomo-clip-unit-label');
		var clipImgDiv = Ext.get('clipImgDiv');

		prm_record.beginEdit();
		if (fChecked) {
			method.show();
			plane.show();
			fix.show();
			reverse.show();
			slider.show();
			textField.show();

			if(buttonSliderUp) buttonSliderUp.show();
			if(buttonSliderDown) buttonSliderDown.show();
			if(buttonTextUp) buttonTextUp.show();
			if(buttonTextDown) buttonTextDown.show();
			if(labelClipUnit) labelClipUnit.show();
			if(clipImgDiv) clipImgDiv.show();

			prm_record.set('clip_type', 'D');
			prm_record.set('clip_depth', slider.getValue());
			prm_record.set('clipped_cameraX', m_ag.cameraPos.x);
			prm_record.set('clipped_cameraY', m_ag.cameraPos.y);
			prm_record.set('clipped_cameraZ', m_ag.cameraPos.z);
			prm_record.set('clipped_targetX', m_ag.targetPos.x);
			prm_record.set('clipped_targetY', m_ag.targetPos.y);
			prm_record.set('clipped_targetZ', m_ag.targetPos.z);
			prm_record.set('clipped_upVecX', m_ag.upVec.x);
			prm_record.set('clipped_upVecY', m_ag.upVec.y);
			prm_record.set('clipped_upVecZ', m_ag.upVec.z);
			anatomoClipDepthMode = true;
//			var urlStr = cgipath.clip+'?' + makeAnatomoPrm();
			var urlStr = cgipath.clip;
//			_dump("oncheck_anatomo_clip_check():urlStr=["+urlStr+"]");

			var params = Ext.urlDecode(makeAnatomoPrm());
			var jsonStr = null;
			try{
				jsonStr = ag_extensions.toJSON.URI2JSON(params,{
					toString:true,
					mapPin:false,
					callback:undefined
				});
			}catch(e){jsonStr = null;}

			Ext.Ajax.request({
				url     : urlStr,
				method  : 'POST',
				params  : jsonStr ? jsonStr : params,
				success : function (response, options) {
					try{
//						_dump("oncheck_anatomo_clip_check():"+cgipath.clip+":success():response.responseText=["+response.responseText+"]");
						var responseObj = Ext.util.JSON.decode(response.responseText);
						var prm_record = ag_param_store.getAt(0);
						prm_record.beginEdit();
						prm_record.set('clip_paramA', parseFloat(responseObj.Clip.ClipPlaneA));
						prm_record.set('clip_paramB', parseFloat(responseObj.Clip.ClipPlaneB));
						prm_record.set('clip_paramC', parseFloat(responseObj.Clip.ClipPlaneC));
						prm_record.set('clip_paramD', parseFloat(responseObj.Clip.ClipPlaneD));

						prm_record.set('clip_type', 'P');
						prm_record.endEdit();
						prm_record.commit();
						anatomoClipDepthMode = false;
						updateAnatomo();
						plane.fireEvent('select',plane);
					}catch(e){
						_dump("oncheck_anatomo_clip_check():"+cgipath.clip+":success():"+e);
					}
				},
				failure : function (response, options) {
					_dump("oncheck_anatomo_clip_check():"+cgipath.clip+":failure():response.responseText=["+response.responseText+"]");
				}
			});
		} else {
			method.hide();
			plane.hide();
			fix.hide();
			reverse.hide();
			slider.hide();
			textField.hide();

			if(buttonSliderUp) buttonSliderUp.hide();
			if(buttonSliderDown) buttonSliderDown.hide();
			if(buttonTextUp) buttonTextUp.hide();
			if(buttonTextDown) buttonTextDown.hide();
			if(labelClipUnit) labelClipUnit.hide();
			if(clipImgDiv) clipImgDiv.hide();

			prm_record.set('clip_type', 'N');
			prm_record.set('clip_depth', NaN);
			anatomoClipDepthMode = false;
		}
		prm_record.endEdit();
		prm_record.commit();
		updateAnatomo();
	}catch(e){
		_dump("oncheck_anatomo_clip_check():"+e);
	}
}
function oncheck_anatomo_clip_fix_check(checkbox, fChecked){
	if(fChecked){
		Ext.getCmp('anatomo-clip-reverse-check').enable();
	}else{
		Ext.getCmp('anatomo-clip-reverse-check').setValue(false);
		Ext.getCmp('anatomo-clip-reverse-check').disable();
	}
	onload_ag_img();
}
function oncheck_anatomo_clip_reverse_check(checkbox, fChecked){
	var prm_record = ag_param_store.getAt(0);
	prm_record.beginEdit();
	prm_record.set('clip_paramA', prm_record.get('clip_paramA')*-1);
	prm_record.set('clip_paramB', prm_record.get('clip_paramB')*-1);
	prm_record.set('clip_paramC', prm_record.get('clip_paramC')*-1);
	prm_record.set('clip_paramD', prm_record.get('clip_paramD')*-1);
	prm_record.set('clip_depth',  prm_record.get('clip_depth') *-1);
	prm_record.endEdit();
	prm_record.commit();
	stopUpdateAnatomo();
	_updateAnatomo();
}
function onselect_anatomo_clip_method_combo(combo, record, index){
	var prm_record = ag_param_store.getAt(0);
	prm_record.beginEdit();
	prm_record.set('clip_method', record.data.value);
	prm_record.endEdit();
	prm_record.commit();
	updateAnatomo();
}
function onselect_anatomo_clip_predifined_plane(combo, record, index){
	var value = combo.getValue();
	var reverse = Ext.getCmp('anatomo-clip-reverse-check').getValue();

	var clip_slider = Ext.getCmp('anatomo-clip-slider');
	var clip_text = Ext.getCmp('anatomo-clip-value-text');
	if(clip_slider && clip_text){
		if(value == "FREE"){
			clip_slider.minValue = -1000;
			clip_slider.maxValue = 1000;
		}else{
			clip_slider.minValue = -350;
			clip_slider.maxValue = 1800;
		}
	}

	if(value == "FB"){
		if(reverse){
			setClipImageHV(90,0,180,0);
		}else{
			setClipImageHV(90,0,0,0);
		}
	}else if(value == "RL"){
		if(reverse){
			setClipImageHV(0,0,90,0);
		}else{
			setClipImageHV(0,0,270,0);
		}
	}else if(value == "TB"){
		if(reverse){
			setClipImageHV(0,0,180,90);
		}else{
			setClipImageHV(0,0,0,270);
		}
	}else if(value == "FREE"){
		Ext.getCmp('anatomo-clip-fix-check').setValue(false);
		Ext.getCmp('anatomo-clip-reverse-check').setValue(false);
		Ext.getCmp('anatomo-clip-reverse-check').disable();
		setClipImageHV(0,0,0,0);
	}
}
function onchange_anatomo_clip_slider(slider, value){
	var clip;
	try{clip = Ext.getCmp('anatomo-clip-predifined-plane').getValue();}catch(e){clip = undefined;}

	var prm_record = ag_param_store.getAt(0);
	prm_record.beginEdit();
	if(clip == 'FB'){
		prm_record.set('clip_depth', (value*-1*prm_record.data.clip_paramB));
	}else if(clip == 'RL'){
		prm_record.set('clip_depth', (value*-1*prm_record.data.clip_paramA));
	}else if(clip == 'TB'){
		prm_record.set('clip_depth', (value*-1*prm_record.data.clip_paramC));
	}else if(clip == 'FREE'){
		prm_record.set('clip_depth', value);
	}
	prm_record.endEdit();
	prm_record.commit();

	anatomoUpdateClipValueText(value);
	updateClipPlane();

	var textCmp = Ext.getCmp('anatomo-clip-value-text');
	if(textCmp) textCmp.fireEvent('change',textCmp,value);
}
function onchange_anatomo_clip_value_text(textField, newValue, oldValue){
//_dump("onchange_anatomo_clip_value_text():"+anatomoUpdateClipValue);
	try{

	if (anatomoUpdateClipValue) {
		return;
	}
	var value = isNaN(parseInt(newValue, 10))?oldValue:Math.round(newValue);

	var clip;
	try{clip = Ext.getCmp('anatomo-clip-predifined-plane').getValue();}catch(e){clip = undefined;}
	var clip_slider = Ext.getCmp('anatomo-clip-slider');

	if(clip == 'FB' || clip == 'RL' || clip == 'TB'){
		if (value < clip_slider.minValue) {
			value = clip_slider.minValue;
		}
		if (value > clip_slider.maxValue) {
			value = clip_slider.maxValue
		}
		textField.setValue(value);
		clip_slider.setValue(value);
	}else{
		if (value < -1000) {
			value = -1000;
		}
		if (value > 1000) {
			value = 1000
		}
		textField.setValue(value);
//		clip_slider.setValue(value + 1000);
		clip_slider.setValue(value);
	}

	setClipLine();

	}catch(e){
		_dump("onchange_anatomo_clip_value_text():"+e);
	}
}

function onload_image_sample(){
	var elem = Ext.get("clipImg");
	elem.un("load", onload_image_sample);

	Ext.getCmp("anatomo-clip-check").on('check',oncheck_anatomo_clip_check);
	Ext.getCmp("anatomo-clip-method-combo").on('select',onselect_anatomo_clip_method_combo);
	Ext.getCmp("anatomo-clip-predifined-plane").on('select',onselect_anatomo_clip_predifined_plane);
	Ext.getCmp("anatomo-clip-reverse-check").on('check',oncheck_anatomo_clip_reverse_check);
	Ext.getCmp("anatomo-clip-slider").on('change',onchange_anatomo_clip_slider);
	Ext.getCmp("anatomo-clip-value-text").on('change',onchange_anatomo_clip_value_text);
}

function loadSaveData(record,latestVersion){
	if(latestVersion == undefined) latestVersion = false;
	var partslist = Ext.getCmp('control-tab-partslist-panel');
	var store = partslist.getStore();

	partslist.stopEditing();

	if(record && record.data){

		var prm_record = ag_param_store.getAt(0);
		prm_record.beginEdit();
		for(var i=0;i<ag_param_store_fields.length;i++){
			prm_record.set(ag_param_store_fields[i],ag_param_store_data[i]);
		}
		prm_record.commit();
		prm_record.endEdit();

		m_ag.cameraPos = new AGVec3d(2.7979888916016167, -998.4280435445771, 809.7306805551052);
		m_ag.targetPos = new AGVec3d(2.7979888916015625, -110.37168800830841, 809.7306805551052);
		m_ag.upVec = new AGVec3d(0, 0, 1);
		m_ag.longitude = 0;
		m_ag.latitude = 0;
		m_ag.distance = 0;

		setRotateHorizontalValue(0);
		setRotateVerticalValue(0);

		Ext.getCmp("anatomo-clip-check").setValue(false);
		Ext.getCmp("zoom-value-text").setValue(1);
		Ext.getCmp("anatomo-width-combo").setValue(400);
		Ext.getCmp("anatomo-height-combo").setValue(400);
		Ext.getCmp("anatomo-bgcp").setValue('#FFFFFF');
		Ext.getCmp("anatomo-bgcolor-transparent-check").setValue(false);
		Ext.getCmp("scalar-max-textfield").setValue('');
		Ext.getCmp("scalar-min-textfield").setValue('');
		Ext.getCmp("show-colorbar-check").setValue(false);

		Ext.getCmp("ag-command-grid-show-check").setValue(false);
		Ext.getCmp("ag-command-grid-color-field").setValue('#008000');
		Ext.getCmp("ag-command-grid-len-combobox").setValue(10);

		Ext.getCmp("ag-coordinate-system-combo").setValue('bp3d');

		var tg_id = '$tg_id';
		var tgi_version = '$tgi_version';

		Ext.getCmp("bp3d-tree-group-combo").setValue('$tg_id');
		Ext.getCmp("bp3d-version-combo").setValue('$tgi_version');
		Ext.getCmp("bp3d-tree-type-combo").setValue('$bul_id');

		Ext.getCmp("anatomo-tree-group-combo").setValue('$tg_id');
		Ext.getCmp("anatomo-version-combo").setValue('$tgi_version');
		Ext.getCmp("bp3d-tree-type-combo-ag").setValue('$bul_id');

		if(record.data.baseparam){
			prm_record.beginEdit();
			for(var reckey in record.data.baseparam){
				if(typeof record.data.baseparam[reckey] == "function") continue;
				prm_record.set(reckey,Ext.isEmpty(record.data.baseparam[reckey])?NaN:record.data.baseparam[reckey]);
			}
			prm_record.commit();
			prm_record.endEdit();

			if(record.data.baseparam.bg_rgb){
				Ext.getCmp("anatomo-bgcp").setValue('#'+record.data.baseparam.bg_rgb);
			}
			if(!Ext.isEmpty(record.data.baseparam.bg_transparent)){
				Ext.getCmp("anatomo-bgcolor-transparent-check").setValue(true);
			}

			if(record.data.baseparam.grid){
				Ext.getCmp("ag-command-grid-show-check").setValue(record.data.baseparam.grid);
			}
//_dump("loadSaveData():record.data.baseparam.grid_len=["+record.data.baseparam.grid_len+"]");
			if(record.data.baseparam.grid_len){
				Ext.getCmp("ag-command-grid-len-combobox").setValue(record.data.baseparam.grid_len);
			}
			if(record.data.baseparam.grid_color){
				Ext.getCmp("ag-command-grid-color-field").setValue('#'+record.data.baseparam.grid_color);
			}

			if(record.data.baseparam.coord){
				Ext.getCmp("ag-coordinate-system-combo").setValue(record.data.baseparam.coord);
			}

			if(record.data.cameraprm){
				setCameraAndTarget(record.data.cameraprm.m_ag.cameraPos, record.data.cameraprm.m_ag.targetPos, record.data.cameraprm.m_ag.upVec, true);
			}
			if(record.data.environment){
				if(record.data.environment.rotate){
					setRotateHorizontalValue(record.data.environment.rotate.H);
					setRotateVerticalValue(record.data.environment.rotate.V);
				}
				if(record.data.environment.zoom){
					Ext.getCmp("zoom-value-text").setValue(record.data.environment.zoom);
				}

//_dump("loadSaveData():record.data.environment.bp3dversion=["+record.data.environment.bp3dversion+"]");
				if(record.data.environment.bp3dversion){
					if(record.data.environment.tg_id){
						tg_id = record.data.environment.tg_id;
					}else if(record.data.environment.model){
						tg_id = model2tg[record.data.environment.model].tg_id;
					}else{
						tg_id = version2tg[record.data.environment.bp3dversion].tg_id;
					}
//_dump("loadSaveData():tg_id=["+tg_id+"]");
//_dump("loadSaveData():tgi_version=["+tgi_version+"]");
					if(latestVersion){
						tgi_version = latestversion[tg_id];
					}else{
						if(version2tg[record.data.environment.bp3dversion].tgi_delcause){
							if(Ext.isEmpty(latestversion[tg_id])) return;
							tgi_version = latestversion[tg_id];
						}else{
							tgi_version = record.data.environment.bp3dversion;
						}
					}
//_dump("loadSaveData():tgi_version=["+tgi_version+"]");

					Ext.getCmp("anatomo-version-combo").setValue(tgi_version);
					Ext.getCmp("bp3d-version-combo").setValue(tgi_version);

					Ext.getCmp("anatomo-tree-group-combo").setValue(tg_id);
					Ext.getCmp("bp3d-tree-group-combo").setValue(tg_id);

					if(record.data.environment.treename){
_dump("loadSaveData():record.data.environment.treename=["+record.data.environment.treename+"]");
						Ext.getCmp("bp3d-tree-type-combo").setValue(record.data.environment.treename);
						Ext.getCmp("bp3d-tree-type-combo-ag").setValue(record.data.environment.treename);
					}

					Ext.getCmp("bp3d-version-combo").getStore().reload({
						callback : function(records,options,success){
							Ext.getCmp("anatomo-version-combo").setValue(tgi_version);
							Ext.getCmp("bp3d-version-combo").setValue(tgi_version);
							if(record.data.environment.treename){
								Ext.getCmp("bp3d-tree-type-combo").setValue(record.data.environment.treename);
								Ext.getCmp("bp3d-tree-type-combo-ag").setValue(record.data.environment.treename);
								Ext.getCmp("bp3d-tree-type-combo").getStore().reload({
									callback : function(records,options,success){
										Ext.getCmp("bp3d-tree-type-combo").setValue(record.data.environment.treename);
										Ext.getCmp("bp3d-tree-type-combo-ag").setValue(record.data.environment.treename);
									}
								});
							}else{
								Ext.getCmp("bp3d-tree-type-combo").getStore().reload({
									callback : function(records,options,success){
										Ext.getCmp("bp3d-tree-type-combo").setValue('1');
										Ext.getCmp("bp3d-tree-type-combo-ag").setValue('1');
									}
								});
							}
							try{Ext.getCmp("anatomo-tree-type-combo").getStore().reload();}catch(e){}
						}
					});

				}
				if(record.data.environment.size){
					Ext.getCmp("anatomo-width-combo").setValue(record.data.environment.size.width);
					Ext.getCmp("anatomo-height-combo").setValue(record.data.environment.size.height);
				}
				if(record.data.environment.colormap){
					Ext.getCmp("scalar-max-textfield").setValue(record.data.environment.colormap.max);
					Ext.getCmp("scalar-min-textfield").setValue(record.data.environment.colormap.min);
					Ext.getCmp("show-colorbar-check").setValue(record.data.environment.colormap.bar);
				}
				if(record.data.environment.clip){
					Ext.getCmp("anatomo-clip-check").un('check',oncheck_anatomo_clip_check);
					Ext.getCmp("anatomo-clip-method-combo").un('select',onselect_anatomo_clip_method_combo);
					Ext.getCmp("anatomo-clip-predifined-plane").un('select',onselect_anatomo_clip_predifined_plane);
					Ext.getCmp("anatomo-clip-reverse-check").un('check',oncheck_anatomo_clip_reverse_check);
					Ext.getCmp("anatomo-clip-slider").un('change',onchange_anatomo_clip_slider);
					Ext.getCmp("anatomo-clip-value-text").un('change',onchange_anatomo_clip_value_text);

					Ext.getCmp("anatomo-clip-check").setValue(true);
					Ext.getCmp("anatomo-clip-method-combo").setValue(record.data.environment.clip.method);
					Ext.getCmp("anatomo-clip-predifined-plane").setValue(record.data.environment.clip.predifined);
					Ext.getCmp("anatomo-clip-fix-check").setValue(record.data.environment.clip.fix);
					Ext.getCmp("anatomo-clip-reverse-check").setValue(record.data.environment.clip.reverse);
					Ext.getCmp("anatomo-clip-slider").setValue(record.data.environment.clip.value);
					Ext.getCmp("anatomo-clip-value-text").setValue(record.data.environment.clip.value);

					var method = Ext.getCmp('anatomo-clip-method-combo');
					var plane = Ext.getCmp('anatomo-clip-predifined-plane');
					var fix = Ext.getCmp('anatomo-clip-fix-check');
					var reverse = Ext.getCmp('anatomo-clip-reverse-check');
					var slider = Ext.getCmp('anatomo-clip-slider');
					var buttonUp = document.getElementById('anatomo-clip-up-button');
					var buttonDown = document.getElementById('anatomo-clip-down-button');
					var textField = Ext.getCmp('anatomo-clip-value-text');
					var clipImgDiv = document.getElementById('clipImgDiv');
					var buttonSliderUp = Ext.get('anatomo-clip-slider-up-button');
					var buttonSliderDown = Ext.get('anatomo-clip-slider-down-button');
					var buttonTextUp = Ext.get('anatomo-clip-text-up-button');
					var buttonTextDown = Ext.get('anatomo-clip-text-down-button');
					var labelClipUnit = Ext.get('anatomo-clip-unit-label');
					var clipImgDiv = Ext.get('clipImgDiv');
					var comboboxPanel = Ext.getCmp('anatomography-control-clip-combobox-panel');

					method.show();
					plane.show();
					fix.show();
					reverse.show();
					slider.show();
					if(comboboxPanel) comboboxPanel.show();
					textField.show();

					if(buttonSliderUp) buttonSliderUp.show();
					if(buttonSliderDown) buttonSliderDown.show();
					if(buttonTextUp) buttonTextUp.show();
					if(buttonTextDown) buttonTextDown.show();
					if(labelClipUnit) labelClipUnit.show();
					if(clipImgDiv) clipImgDiv.show();


					if(record.data.environment.clip.clipprm){

						var elem = Ext.get("clipImg");
						elem.on("load", onload_image_sample);
						var value = plane.getValue();
						if(value == "FB") {
							setClipImage(90,0,setClipLine);
						} else if (value == "RL") {
							setClipImage(0,0,setClipLine);
						} else if (value == "TB") {
							setClipImage(0,0,setClipLine);
						}


					}else{
						onload_image_sample();
					}
				}
			}
		}
		updateRotateImg();
		setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);

		var cmp = Ext.getCmp('bp3d_dataview');
		if(cmp && cmp.rendered) cmp.store.reload();


		var cmp = Ext.getCmp('anatomography_image_comment_draw_check');
		if(cmp && cmp.rendered) cmp.setValue(false);
		var cmp = Ext.getCmp("anatomography_image_comment_title");
		if(cmp && cmp.rendered) cmp.setValue("");
		var cmp = Ext.getCmp("anatomography_image_comment_legend");
		if(cmp && cmp.rendered) cmp.setValue("");
		var cmp = Ext.getCmp("anatomography_image_comment_author");
		if(cmp && cmp.rendered) cmp.setValue("");
		var cmp = Ext.getCmp('anatomo_pin_description_draw_check');
		if(cmp && cmp.rendered) cmp.setValue(false);
		var cmp = Ext.getCmp('anatomo_pin_shape_combo');
		if(cmp && cmp.rendered){
			try{var value = cmp.initialConfig.store.getAt(0).get(cmp.initialConfig.valueField);}catch(e){value='SC';}
			cmp.setValue(value);
		}
		ag_comment_store.removeAll();

		if(record.data.anatomoprm){
			// Legend Parameters
			var cmp = Ext.getCmp('anatomography_image_comment_draw_check');
			if(cmp && cmp.rendered) cmp.setValue(record.data.anatomoprm.lp?true:false);

			var cmp = Ext.getCmp("anatomography_image_comment_title");
			if(cmp && cmp.rendered) cmp.setValue(record.data.anatomoprm.lt);

			var cmp = Ext.getCmp("anatomography_image_comment_legend");
			if(cmp && cmp.rendered) cmp.setValue(record.data.anatomoprm.le);

			var cmp = Ext.getCmp("anatomography_image_comment_author");
			if(cmp && cmp.rendered) cmp.setValue(record.data.anatomoprm.la);

			var newRecord = Ext.data.Record.create(ag_comment_store_fields);
			var addrecs = [];
			var f_ids = {};
			for(var i=0;;i++){
				var num = i+1;
				while ((num+"").length < 3) {
					num = "0" + num;
				}
				if(!record.data.anatomoprm["pno"+num]) break;
				var addrec = new newRecord({});
				addrec.beginEdit();
				addrec.set("no",     record.data.anatomoprm["pno"+num]);
				addrec.set("x3d",    record.data.anatomoprm["px"+num]);
				addrec.set("y3d",    record.data.anatomoprm["py"+num]);
				addrec.set("z3d",    record.data.anatomoprm["pz"+num]);
				addrec.set("avx3d",  record.data.anatomoprm["pax"+num]);
				addrec.set("avy3d",  record.data.anatomoprm["pay"+num]);
				addrec.set("avz3d",  record.data.anatomoprm["paz"+num]);
				addrec.set("uvx3d",  record.data.anatomoprm["pux"+num]);
				addrec.set("uvy3d",  record.data.anatomoprm["puy"+num]);
				addrec.set("uvz3d",  record.data.anatomoprm["puz"+num]);
				addrec.set("color",  record.data.anatomoprm["pcl"+num]);
				addrec.set("oid",    record.data.anatomoprm["poi"+num]);
				addrec.set("organ",  record.data.anatomoprm["pon"+num]);
				addrec.set("comment",record.data.anatomoprm["pd"+num]);
				addrec.set("coord",  record.data.anatomoprm["pcd"+num]);
				if(window.ag_extensions && ag_extensions.global_pin){
					if(!Ext.isEmpty(record.data.anatomoprm["pid"+num])) addrec.set("PinID",  record.data.anatomoprm["pid"+num]);
					if(!Ext.isEmpty(record.data.anatomoprm["pgid"+num])) addrec.set("PinGroupID",  record.data.anatomoprm["pgid"+num]);
				}
				addrec.commit();
				addrec.endEdit();
				addrecs.push(addrec);

				f_ids[record.data.anatomoprm["poi"+num]] = record.data.anatomoprm["pno"+num];

				var cmp = Ext.getCmp('anatomo_pin_number_draw_check');
				if(cmp && cmp.rendered) cmp.setValue(record.data.anatomoprm["pnd"+num]);

				var cmp = Ext.getCmp('anatomo_pin_description_draw_check');
				if(cmp && cmp.rendered) cmp.setValue(record.data.anatomoprm["pdd"+num]);

				var cmp = Ext.getCmp('anatomo_pin_shape_combo');
				if(cmp && cmp.rendered) cmp.setValue(record.data.anatomoprm["ps"+num]);

			}
			ag_comment_store.add(addrecs);
		}

		if(record.data.partslist){
			var conv_flag = false;

			var records = store.getRange();
			while(records.length){
				store.remove(records[records.length-1]);
				records = store.getRange();
			}

			var newRecord = Ext.data.Record.create(bp3d_parts_store_fields);
			try{
				var prm_record = ag_param_store.getAt(0);
				var addrecs = [];
				for(var i=0;i<record.data.partslist.length;i++){
					var addrec = new newRecord({
						'exclude'       : false,
						'color'         : '#'+prm_record.data.color_rgb,
						'value'         : '',
						'zoom'          : false,
						'exclude'       : false,
						'opacity'       : '1.0',
						'representation': 'surface',
						'point'         : false
					});
					addrec.beginEdit();
					for(var fcnt=0;fcnt<addrec.fields.items.length;fcnt++){
						var fname = addrec.fields.items[fcnt].name;
						var fdefaultValue = addrec.fields.items[fcnt].defaultValue;
						if(Ext.isEmpty(record.data.partslist[i][fname])){
							addrec.set(fname,fdefaultValue);
						}else{
							addrec.set(fname,record.data.partslist[i][fname]);
						}
					}
					if((!addrec.data.b_id || addrec.data.b_id == "") && record.data.partslist[i].f_id) addrec.data.b_id = record.data.partslist[i].f_id;
					if((!addrec.data.entry || addrec.data.entry == "") && record.data.partslist[i].lastmod) addrec.data.entry = record.data.partslist[i].lastmod;
					if(addrec.data.entry.match(/^[0-9]+$/)){
						addrec.data.entry = Date.parseDate(parseInt(addrec.data.entry), "U");
					}else if(addrec.data.entry.match(/^[0-9]{4}\-[0-9]{2}\-[0-9]{2}T/)){
						if(addrec.data.entry.match(/^[0-9]{4}\-[0-9]{2}\-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}$/)) addrec.data.entry+='Z';
						addrec.data.entry = Date.parseDate(addrec.data.entry, "c");
					}
					addrec.set('zoom',false);
					if(!addrec.get('color')) addrec.set('color','#'+prm_record.data.color_rgb);

					if(!addrec.data.tg_id || addrec.data.tg_id == ""){
						addrec.set('tg_id',tg_id);
					}else if(addrec.data.tg_id != tg_id){
						conv_flag = true;
					}
					if(!addrec.data.version || addrec.data.version == "") addrec.set('version',tgi_version);

					addrec.commit(true);
					addrec.endEdit();
					addrecs.push(addrec);
				}
				store.add(addrecs);
				clearConvertIdList(addrecs);
				getConvertIdList(addrecs,store);

				if(conv_flag){

					var btn = Ext.getCmp('bp3d-home-group-btn');
					if(btn && btn.rendered){
						if(store.getCount()>0 && store.find('tg_id', new RegExp('^'+tg_id+'$')) == -1){
							btn.enable();
							btn.el.dom.setAttribute('tg_id',addrecs[0].data.tg_id);
						}else{
							btn.disable();
						}
					}

				}

			}catch(e){
				_dump("ag_sample_dataview():"+e);
			}
		}
		setImageWindowSize();
	}

}

/////////////////////////////////////////////////////////////////////////////////////////////////////
// anatomography_js.cgiから移植（ここまで）
/////////////////////////////////////////////////////////////////////////////////////////////////////

/////////////////////////////////////////////////////////////////////////////////////////////////////
// ag_annotation_js.cgiから移植（ここから）
/////////////////////////////////////////////////////////////////////////////////////////////////////

function click_locale(){
	if(gParams.lng == "ja"){
		gParams.lng = "en";
	}else{
		gParams.lng = "ja";
	}
	Cookies.set('ag_annotation.locale',gParams.lng);
//	location.reload(true);
	try{
		var params = Ext.urlDecode(window.location.search.substring(1));
	}catch(e){alert("3:"+e);}
	params.lng = gParams.lng;
	location.search = Ext.urlEncode(params);
}

function getActivePartsList(){
	var partslist = null;
	var contents_tabs = Ext.getCmp('contents-tab-panel');
	if(contents_tabs){
		if(contents_tabs.getActiveTab().id == 'contents-tab-bodyparts-panel'){
			partslist = Ext.getCmp('control-tab-partslist-panel');
		}else if(contents_tabs.getActiveTab().id == 'contents-tab-anatomography-panel'){
			partslist = Ext.getCmp('ag-parts-gridpanel');
		}
	}
	return partslist;
};

/////////////////////////////////////////////////////////////////////////////////////////////////////
// ag_annotation_js.cgiから移植（ここまで）
/////////////////////////////////////////////////////////////////////////////////////////////////////


var versionListTpl = new Ext.XTemplate(
	'<table style="width:100%;border-spacing: 2px 0;">',
	'<thead style="background:#f0f0f0;"><tr>',
	'<th nowrap style="font-weight:bold;padding-right:10px;">'+ag_lang.DATA_VERSION+'</th>',
	'<th nowrap style="font-weight:bold;padding-right:10px;">'+ag_lang.OBJECTS_SET+'</th>',
	'<th nowrap style="font-weight:bold;padding-right:10px;">'+ag_lang.TREE_VERSION+'</th>',
	'<th nowrap style="font-weight:bold;padding-right:10px;">'+ag_lang.PART_OF_RELATION+'</th>',
	'<th nowrap style="font-weight:bold;">'+ag_lang.PART_OF_RELATION_BP3D+'</th>',
	'</tr></thead>',
	'<tbody>',
	'<tpl for="."><tr class="x-combo-list-item">',
		'<td style="padding-right:10px;">{tgi_name}</td>',
		'<td style="padding-right:10px;">{tgi_objects_set}</td>',
		'<td style="padding-right:10px;">{tgi_tree_version}</td>',
		'<td style="padding-right:10px;">{tgi_part_of_relation}</td>',
		'<td style="">{tgi_part_of_relation_bp3d}</td>',
	'</tr></tpl>',
	'</tbody>',
	'</table>'
//	,'<div style="background:#f0f0f0;border-top:1px solid #ddd;margin-top:2px;padding:0 2px;">',
//	'<label id="bp3-version-information" style="font-size:10px;color:#000000;">'+ag_lang.VERSION_INFORMATION+'</label>',
//	'</div>'
);


