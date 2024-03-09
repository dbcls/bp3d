window.ag_extensions = window.ag_extensions || {};
ag_extensions.toJSON = ag_extensions.toJSON || {};
ag_extensions.toJSON.defaults = ag_extensions.toJSON.defaults || {};

ag_extensions.toJSON.defaults.Common = function(){
	return {
		"Model":"bp3d",                 //  モデル（文字列）
		"Version":"4.0",                //  バージョン（文字列／"2.0"、"3.0"、"4.0"。未指定の場合最新バージョンとなります）
		"AnatomogramVersion":"20110318",//  アナトモグラムのバージョン（文字列）
		"ScalarMaximum":null,           //  Scalar最大値（整数）
		"ScalarMinimum":null,           //  Scalar最小値（整数）
		"ColorbarFlag":false,           //  カラーバーの描画フラグ（Boolean）
		"ScalarColorFlag":false,        //  Valueを利用した臓器描画フラグ（Boolean）
		"TreeName":"isa",               //  利用するTree名（文字列／"isa"、"partof"のいずれかを指定します）
		"DateTime":null,                //  描画時刻（文字列、yyyymmddhhmmss）
		"CoordinateSystemName":"bp3d",  //  描画座標系（文字列）
		"CopyrightType":null,           //  コピーライト画像サイズ（文字列／未指定、large、medium、small）
		"PinNumberDrawFlag": true,      //  PinのID描画フラグ（Boolean）
		"PinDescriptionDrawFlag":false, //  true：description表示、false：description非表示（Boolean）
		"PinIndicationLineDrawFlag":0   //  ピンからPin Descriptionへの線描画指定（整数／0:描画なし、1:ピン先端から描画、2:ピン終端から描画）
	};
};
ag_extensions.toJSON.defaults.Window = function(){
	return {
		"ImageWidth":500,           //  画像幅px数（整数）
		"ImageHeight":500,          //  画像高さpx数（正数）
		"BackgroundColor":"FFFFFF", //  背景色RGB（文字列、16進数6桁）
		"BackgroundOpacity":100,    //  背景の不透明度（整数、0～100）
		"GridFlag":false,           //  Gridの描画有無（Boolean）
		"GridTickInterval":100,     //  Gridの描画単位（整数、mm指定）
		"GridColor":"FFFFFF"        //  Gridの描画色RGB（文字列、16進数6桁）
	};
};
ag_extensions.toJSON.defaults.Camera = function(){
	return {
		"CameraMode":null,        // カメラ位置のモード（文字列、camera、front、back、left、right、top、bottom）
		"CameraX":null,           // カメラのX座標（Double）
		"CameraY":null,           // カメラのY座標（Double）
		"CameraZ":null,           // カメラのZ座標（Double）
		"TargetX":null,           // 中心点のX座標（Double）
		"TargetY":null,           // 中心点のY座標（Double）
		"TargetZ":null,           // 中心点のZ座標（Double）
		"CameraUpVectorX":null,   // カメラの上方ベクトルのX要素（Double）
		"CameraUpVectorY":null,   // カメラの上方ベクトルのY要素（Double）
		"CameraUpVectorZ":null,   // カメラの上方ベクトルのZ要素（Double）
		"Zoom":null,              // ズーム値（Double、0～19.8）
		"AddLatitudeDegree":null, // 緯度方向への追加回転角度（Double、0～360度）
		"AddLongitudeDegree":null // 経度方向への追加回転角度（Double、0～360度）
	};
};
ag_extensions.toJSON.defaults.Part = function(){
	return {
		"PartID":null,                   // 臓器ID（文字列、名称より優先されます）
		"PartName":null,                 // 臓器名（文字列）
		"PartColor":"FFFFFF",          // 臓器色RGB（文字列、16進数6桁）
		"PartScalar":null,              // 臓器スカラー値（Double）
		"ScalarColorFlag":false,       // 臓器をスカラー値で描画するフラグ（Boolean）
		"PartOpacity":1,               // 臓器不透明度（Double、0～1）
		"PartRepresentation":"surface",// 臓器描画方法（文字列、surface、wireframe、point）
		"UseForBoundingBoxFlag":true,  // 臓器をBoundingBoxに含めるか否かのフラグ（Boolean、Focus時にはBoudingBoxに含まれる臓器群が収まるように拡大率が返されます）
		"PartDeleteFlag":false         // 臓器の削除フラグ（Boolean）
	};
};
ag_extensions.toJSON.defaults.Legend = function(){
	return {
		"DrawLegendFlag":false, // Legendの描画有無フラグ（Boolean）
		"LegendPosition":"UL",  // Legendの描画位置（文字列、ULのみ）
		"LegendColor":"646464", // Legendの描画色RGB（文字列、16進数6桁）
		"LegendTitle":null,     // Legendのタイトル（文字列）
		"Legend":null,          // Legend（文字列）
		"LegendAuthor":null     // Legend Author（文字列）
	};
};
ag_extensions.toJSON.defaults.Pin = function(){
	return {
		"PinID":null,                        //  PinID（文字列）
		"PinX":null,                          //  Pinの3次元空間上X座標（Double）
		"PinY":null,                          //  Pinの3次元空間上Y座標（Double）
		"PinZ":null,                          //  Pinの3次元空間上Z座標（Double）
		"PinArrowVectorX":null,               //  PinベクトルのX要素（Double）
		"PinArrowVectorY":null,               //  PinベクトルのY要素（Double）
		"PinArrowVectorZ":null,               //  PinベクトルのZ要素（Double）
		"PinUpVectorX":null,                  //  Pinの上方ベクトルのX要素（Double）
		"PinUpVectorY":null,                  //  Pinの上方ベクトルのY要素（Double）
		"PinUpVectorZ":null,                  //  Pinの上方ベクトルのZ要素（Double）
		"PinScreenX":null,                    //  Pinの画像上のX座標（Double）
		"PinScreenY":null,                    //  Pinの画像上のY座標（Double）
		"PinDescriptionDrawFlag":false,    //  PinのDescription描画フラグ（Boolean）
		"PinDescriptionColor":"0000FF",    //  PinのDescription描画色RGB（文字列、16進数6桁）
		"PinColor":"0000FF",               //  Pinの描画色RGB（文字列、16進数6桁）
		"PinShape":null,                     //  Pin形状（文字列、16進数6桁）
		"PinSize":10.0,                    //  Pinサイズ（Double）
		"PinCoordinateSystemName":"bp3d",  //  Pin作成時の座標系（文字列）
		"PinPartID":null,                    //  Pinが打たれているパーツのID（文字列）
		"PinPartName":null,                  //  Pinが打たれているパーツの名称（文字列）
		"PinDescription":null,               //  PinのDescription（文字列）
		"PinNumberDrawFlag": true,         //  PinのID描画フラグ（Boolean）
		"PinValue":null                      //  Pinの値（文字列）
	};
};

ag_extensions.toJSON.defaults.PinGroup = function(){
	return {
		"PinGroupID":null,                     //  PinGroupID（文字列）
		"PinGroupColor":"0000FF",            //  PinGroupの描画色RGB（文字列、16進数6桁）
		"PinGroupDescription":null,            //  PinGroupのDescription（文字列）
		"PinGroupDescriptionColor":"0000FF", //  PinGroupのDescription描画色RGB（文字列、16進数6桁）
		"PinGroupDescriptionDrawFlag":false, //  PinGroupのDescription描画フラグ（Boolean）
		"PinGroupNumberDrawFlag": true,      //  PinGroupのID描画フラグ（Boolean）
		"PinGroupShape":null,                  //  Pin形状（文字列、16進数6桁）
		"PinGroupSize":10.0,                 //  Pinサイズ（Double）
		"PinGroupValue":null,                  //  PinGroupの値（文字列）
		"PinGroupApiAdding": false,          //  PinGroupのAPIからのPin追加可フラグ（Boolean）
		"PinGroupApiExclusion": false,       //  PinGroupのAPIからのPin除外可フラグ（Boolean）
		"PinGroupApiReference": false,       //  PinGroupのAPIからのPin参照情報可フラグ（Boolean）
		"PinGroupSearch": false,             //  PinGroupの検索可フラグ（Boolean）
		"PinCount":null                         //  Pin数（整数）
	};
};

ag_extensions.toJSON.defaults.Pick = function(){
	return {
		"MaxNumberOfPicks":20, // 指定数分、パーツ表面を貫通して結果を返します
		"ScreenPosX":null,     // 画像上ピック位置のX座標
		"ScreenPosY":null,     // 画像上ピック位置のY座標
		"VoxelRadius":null     //
	};
};

ag_extensions.toJSON.defaults.ObjectRotate = function(){
	return {
		"DateTime":null,
		"RotateCenterX":null,
		"RotateCenterY":null,
		"RotateCenterZ":null,
		"RotateAxisVectorX":null,
		"RotateAxisVectorY":null,
		"RotateAxisVectorZ":null,
		"RotateDegree":null
	};
};

ag_extensions.toJSON.pinShapeAbbr2PinShape = function(pinShapeAbbr){
	if(pinShapeAbbr == 'CC'){
		return 'CONE';
	}else if(pinShapeAbbr == 'PSS'){
		return 'PIN_LONG';
	}else if(pinShapeAbbr == 'PS'){
		return 'PIN_LONG';
	}else if(pinShapeAbbr == 'PM'){
		return 'PIN_LONG';
	}else if(pinShapeAbbr == 'PL'){
		return 'PIN_LONG';
	}
	return "";
};
ag_extensions.toJSON.pinShapeAbbr2PinSize = function(pinShapeAbbr){
	if(pinShapeAbbr == 'CC'){
		return 25.0;
	}else if(pinShapeAbbr == 'PSS'){
		return 20.0;
	}else if(pinShapeAbbr == 'PS'){
		return 37.5;
	}else if(pinShapeAbbr == 'PM'){
		return 75.0;
	}else if(pinShapeAbbr == 'PL'){
		return 112.5;
	}
	return 10.0
};

//既存のレコードからJSON用のPinオブジェクトを生成する
ag_extensions.toJSON.fromRecordPin2HashPin = function(obj,clearEmpty){
	var self = this;
	if(Ext.isEmpty(clearEmpty)) clearEmpty = true;
	var hash = Ext.apply({},obj||{},self.defaults.Pin());
	if(Ext.isEmpty(hash.PinID)) hash.PinID = hash.no;
	hash.PinX = hash.x3d;
	hash.PinY = hash.y3d;
	hash.PinZ = hash.z3d;
	hash.PinArrowVectorX = hash.avx3d;
	hash.PinArrowVectorY = hash.avy3d;
	hash.PinArrowVectorZ = hash.avz3d;
	hash.PinUpVectorX = hash.uvx3d;
	hash.PinUpVectorY = hash.uvy3d;
	hash.PinUpVectorZ = hash.uvz3d;
	hash.PinColor = hash.color;
	hash.PinDescriptionColor = hash.color;
	hash.PinCoordinateSystemName = hash.coord;
	hash.PinPartID = hash.oid;
	hash.PinPartName = hash.organ;
	hash.PinDescription = hash.comment;
	hash.PinSize = self.pinShapeAbbr2PinSize(hash.PinShape);
	hash.PinShape = self.pinShapeAbbr2PinShape(hash.PinShape);
	delete hash.no;
	delete hash.x3d;
	delete hash.y3d;
	delete hash.z3d;
	delete hash.avx3d;
	delete hash.avy3d;
	delete hash.avz3d;
	delete hash.uvx3d;
	delete hash.uvy3d;
	delete hash.uvz3d;
	delete hash.color;
	delete hash.coord;
	delete hash.oid;
	delete hash.organ;
	delete hash.comment;

	if(clearEmpty){
		self._deletesEmptyProp(hash);
	}
	return hash;
};

//既存のレコードからJSON用のPinGroupオブジェクトを生成する
ag_extensions.toJSON.fromRecordPin2HashPinGroup = function(obj,clearEmpty){
	var self = this;
	if(Ext.isEmpty(clearEmpty)) clearEmpty = true;
	var hash = Ext.apply({},obj||{},self.defaults.PinGroup());
	if(Ext.isEmpty(hash.PinGroupID)) hash.PinGroupID = hash.no;
	hash.PinGroupColor = hash.color;
	hash.PinGroupDescriptionColor = hash.color;
	hash.PinGroupDescription = hash.comment;
//	if(hash.PinGroupShape == 'CC'){
//		hash.PinGroupShape = 'CONE';
//		hash.PinGroupSize = 25.0;
//	}else if(hash.PinGroupShape == 'PSS'){
//		hash.PinGroupShape = 'PIN_LONG';
//		hash.PinGroupSize = 20.0;
//	}else if(hash.PinGroupShape == 'PS'){
//		hash.PinGroupShape = 'PIN_LONG';
//		hash.PinGroupSize = 37.5;
//	}else if(hash.PinGroupShape == 'PM'){
//		hash.PinGroupShape = 'PIN_LONG';
//		hash.PinGroupSize = 75.0;
//	}else if(hash.PinGroupShape == 'PL'){
//		hash.PinGroupShape = 'PIN_LONG';
//		hash.PinGroupSize = 112.5;
//	}
	hash.PinGroupSize = self.pinShapeAbbr2PinSize(hash.PinGroupShape);// 25.0;
	hash.PinGroupShape = self.pinShapeAbbr2PinShape(hash.PinGroupShape);// 'CONE';

	delete hash.no;
	delete hash.x3d;
	delete hash.y3d;
	delete hash.z3d;
	delete hash.avx3d;
	delete hash.avy3d;
	delete hash.avz3d;
	delete hash.uvx3d;
	delete hash.uvy3d;
	delete hash.uvz3d;
	delete hash.color;
	delete hash.coord;
	delete hash.oid;
	delete hash.organ;
	delete hash.comment;

	if(clearEmpty){
		self._deletesEmptyProp(hash);
	}
	return hash;
};

//JSON文字列からURI文字を生成する
ag_extensions.toJSON.JSONStr2URI = function(jsonStr,aOpts){
	var self = this;
	var uri = {};
	var jsonObj;
	if(!Ext.isEmpty(jsonStr)){
		if(typeof jsonStr == 'string'){
			try{jsonObj = Ext.util.JSON.decode(jsonStr);}catch(e){if(window.console && console.log) console.log(e);}
		}else if(typeof jsonStr == 'object'){
			jsonObj = jsonStr;
		}
	}
	if(Ext.isEmpty(jsonObj)) return null;

	aOpts = Ext.apply({},aOpts||{},{
		toString: true,
		clearEmpty: true
	});
	var toStringOpts = aOpts.toString;
	var clearEmpty = aOpts.clearEmpty;

	var prm_record = ag_param_store.getAt(0);

	if(Ext.isEmpty(jsonObj.Common)){
		jsonObj.Common = Ext.apply({},{
			Version:bp3d.defaults.bp3d_version,
			PinDescriptionDrawFlag: Ext.getCmp('anatomo_pin_description_draw_check').getValue(),
			PinIndicationLineDrawFlag: Ext.getCmp('anatomo_pin_description_draw_pin_indication_line_combo').getValue(),
			PinNumberDrawFlag: Ext.getCmp('anatomo_pin_number_draw_check').getValue()
		},self.defaults.Common());
	}
	jsonObj.Common = Ext.apply({},{AnatomogramVersion: '09051901'},jsonObj.Common);
	var h = jsonObj.Common;
	if(!Ext.isEmpty(h.Model)) uri.model = h.Model;
	if(!Ext.isEmpty(h.Version)) uri.bv = h.Version;
	if(!Ext.isEmpty(h.AnatomogramVersion)) uri.av = h.AnatomogramVersion;
	if(!Ext.isEmpty(h.ScalarMaximum) && (h.ScalarMaximum-0) != 65535) uri.sx = h.ScalarMaximum;
	if(!Ext.isEmpty(h.ScalarMinimum) && (h.ScalarMinimum-0) != -65535) uri.sn = h.ScalarMinimum;
	if(!Ext.isEmpty(h.ColorbarFlag) && h.ColorbarFlag) uri.cf = h.ColorbarFlag ? 1 : 0;
	if(!Ext.isEmpty(h.ScalarColorFlag) && h.ScalarColorFlag) uri.hf = h.ScalarColorFlag ? 1 : 0;
	if(!Ext.isEmpty(h.TreeName)) uri.tn = h.TreeName;
	if(!Ext.isEmpty(h.DateTime)) uri.dt = h.DateTime;
	if(!Ext.isEmpty(h.CoordinateSystemName)) uri.crd = h.CoordinateSystemName;
	if(!Ext.isEmpty(h.PinDescriptionDrawFlag) && h.PinDescriptionDrawFlag) uri.dp = h.PinDescriptionDrawFlag ? 1 : 0;
	if(!Ext.isEmpty(h.PinIndicationLineDrawFlag) && h.PinIndicationLineDrawFlag) uri.dpl = h.PinIndicationLineDrawFlag;
	if(!Ext.isEmpty(h.PinNumberDrawFlag) && h.PinNumberDrawFlag) uri.np = h.PinNumberDrawFlag ? 1 : 0;

	if(Ext.isEmpty(jsonObj.Window)) jsonObj.Window = self.defaults.Window();
	var h = jsonObj.Window;
	if(!Ext.isEmpty(h.ImageWidth)) uri.iw = h.ImageWidth;
	if(!Ext.isEmpty(h.ImageHeight)) uri.ih = h.ImageHeight;
	if(!Ext.isEmpty(h.BackgroundColor)) uri.bcl = h.BackgroundColor;
	if(!Ext.isEmpty(h.BackgroundOpacity)) uri.bga = h.BackgroundOpacity;
	if(!Ext.isEmpty(h.GridFlag) && h.GridFlag){
		uri.gdr = h.GridFlag ? 1 : 0;
		if(!Ext.isEmpty(h.GridTickInterval)) uri.gtc = h.GridTickInterval;
		if(!Ext.isEmpty(h.GridColor)) uri.gcl = h.GridColor;
	}
	if(!Ext.isEmpty(jsonObj.Camera)){
		jsonObj.Camera = Ext.apply({},jsonObj.Camera,self.defaults.Camera());
		var h = jsonObj.Camera;
		uri.cx = h.CameraX;
		uri.cy = h.CameraY;
		uri.cz = h.CameraZ;
		uri.tx = h.TargetX;
		uri.ty = h.TargetY;
		uri.tz = h.TargetZ;
		uri.ux = h.CameraUpVectorX;
		uri.uy = h.CameraUpVectorY;
		uri.uz = h.CameraUpVectorZ;
		uri.zm = h.Zoom;
	}
	if(!Ext.isEmpty(jsonObj.Legend)){
		jsonObj.Legend = Ext.apply({},jsonObj.Legend,self.defaults.Legend());
		var h = Ext.apply({},jsonObj.Legend,self.defaults.Legend());
		uri.dl = h.DrawLegendFlag?1:0;
		if(!Ext.isEmpty(h.LegendPosition)) uri.lp = h.LegendPosition.toUpperCase();
		if(!Ext.isEmpty(h.LegendColor)) uri.lc = h.LegendColor.toUpperCase();
		uri.lt = h.LegendTitle;
		uri.le = h.Legend;
		uri.la = h.LegendAuthor;
	}
	if(jsonObj.Part && jsonObj.Part.length>0){
		var no = 0;
		var def_color = Ext.getCmp('anatomo-default-parts-color').getValue();
		if(def_color.indexOf("#")>=0) def_color = def_color.substr(def_color.indexOf("#")+1);
		Ext.each(jsonObj.Part,function(h,i,a){
			if(Ext.isEmpty(h.PartID) && Ext.isEmpty(h.PartName)) return true;

			h = Ext.apply({},h,Ext.apply({},{PartColor:def_color,UseForBoundingBoxFlag:false},self.defaults.Part()));

			var num = makeAnatomoOrganNumber(++no);

			if(!Ext.isEmpty(h.PartID)) uri['oid'+num] = h.PartID;
			if(!Ext.isEmpty(h.PartName)) uri['onm'+num] = h.PartName;
			if(!Ext.isEmpty(h.PartColor)) uri['ocl'+num] = h.PartColor;
			if(!Ext.isEmpty(h.PartScalar)) uri['osc'+num] = h.PartScalar;
			uri['osz'+num] = 'S';
			if(!Ext.isEmpty(h.PartDeleteFlag) && h.PartDeleteFlag){
				uri['osz'+num] = 'H';
			}else if(!Ext.isEmpty(h.UseForBoundingBoxFlag) && h.UseForBoundingBoxFlag){
				uri['osz'+num] = 'Z';
			}
			if(!Ext.isEmpty(h.PartOpacity)) uri['oop'+num] = h.PartOpacity-0;
			if(!Ext.isEmpty(h.PartRepresentation)) uri['orp'+num] = h.PartRepresentation;
			if(!Ext.isEmpty(h.Version)) uri['ov'+num] = h.Version;
		});
	}
	if(jsonObj.Pin && jsonObj.Pin.length>0){
		Ext.each(jsonObj.Pin,function(h,i,a){
			h = Ext.apply({},h,Ext.apply({},{PinShape:Ext.getCmp('anatomo_pin_shape_combo').getValue()},self.defaults.Pin()));
			var num = makeAnatomoOrganNumber(i+1);
			uri['pno'+num] = i+1;
			if(!Ext.isEmpty(h.PinX)) uri['px'+num] = h.PinX-0;
			if(!Ext.isEmpty(h.PinY)) uri['py'+num] = h.PinY-0;
			if(!Ext.isEmpty(h.PinZ)) uri['pz'+num] = h.PinZ-0;
			if(!Ext.isEmpty(h.PinArrowVectorX)) uri['pax'+num] = h.PinArrowVectorX-0;
			if(!Ext.isEmpty(h.PinArrowVectorY)) uri['pay'+num] = h.PinArrowVectorY-0;
			if(!Ext.isEmpty(h.PinArrowVectorZ)) uri['paz'+num] = h.PinArrowVectorZ-0;
			if(!Ext.isEmpty(h.PinUpVectorX)) uri['pux'+num] = h.PinUpVectorX-0;
			if(!Ext.isEmpty(h.PinUpVectorY)) uri['puy'+num] = h.PinUpVectorY-0;
			if(!Ext.isEmpty(h.PinUpVectorZ)) uri['puz'+num] = h.PinUpVectorZ-0;
			if(!Ext.isEmpty(h.PinDescriptionDrawFlag)) uri['pdd'+num] = h.PinDescriptionDrawFlag ? 1: 0;
			if(!Ext.isEmpty(h.PinDescriptionColor)) uri['pdc'+num] = h.PinDescriptionColor.toUpperCase();
			if(!Ext.isEmpty(h.PinNumberDrawFlag)) uri['pnd'+num] = h.PinNumberDrawFlag ? 1: 0;
			if(!Ext.isEmpty(h.PinColor)) uri['pcl'+num] = h.PinColor.toUpperCase();
			if(!Ext.isEmpty(h.PinShape)){
				uri['ps'+num] = h.PinShape.toUpperCase();
				if(uri['ps'+num]=='CONE'){
					uri['ps'+num]='CC';
				}else if(uri['ps'+num]=='PIN_LONG'){
					if(Ext.isEmpty(h.PinSize) || (h.PinSize-0)==self.pinShapeAbbr2PinSize('PL')){
						uri['ps'+num]='PL';
					}else if((h.PinSize-0)==self.pinShapeAbbr2PinSize('PM')){
						uri['ps'+num]='PM';
					}else if((h.PinSize-0)==self.pinShapeAbbr2PinSize('PS')){
						uri['ps'+num]='PS';
					}else if((h.PinSize-0)==self.pinShapeAbbr2PinSize('PSS')){
						uri['ps'+num]='PSS';
					}
				}else{
					uri['ps'+num] = "";
				}
			}
			if(!Ext.isEmpty(h.PinPartID)) uri['poi'+num] = h.PinPartID;
			if(!Ext.isEmpty(h.PinPartName)) uri['pon'+num] = h.PinPartName;
			if(!Ext.isEmpty(h.PinDescription)) uri['pd'+num] = h.PinDescription;
			if(!Ext.isEmpty(h.PinCoordinateSystemName)) uri['pcd'+num] = h.PinCoordinateSystemName;
			if(window.ag_extensions && ag_extensions.global_pin){
				if(!Ext.isEmpty(h.PinID)) uri['pid'+num] = h.PinID;
				if(!Ext.isEmpty(h.PinGroupID)) uri['pgid'+num] = h.PinGroupID;
			}
		});
	}

	if(!Ext.isEmpty(jsonObj.Pick)){
		var h = Ext.apply({},jsonObj.Pick,self.defaults.Pick());
		if(!Ext.isEmpty(h.ScreenPosX)) uri.px = h.ScreenPosX;
		if(!Ext.isEmpty(h.ScreenPosY)) uri.py = h.ScreenPosY;
		if(!Ext.isEmpty(h.VoxelRadius)) uri.vr = h.VoxelRadius;
	}

	if(!Ext.isEmpty(jsonObj.ObjectRotate)){
		var h = Ext.apply({},jsonObj.ObjectRotate,self.defaults.ObjectRotate());
		if(!Ext.isEmpty(h.ObjectRotate)) uri.autorotate = h.ObjectRotate;
		if(!Ext.isEmpty(h.RotateCenterX)) uri.orcx = h.RotateCenterX;
		if(!Ext.isEmpty(h.RotateCenterY)) uri.orcy = h.RotateCenterY;
		if(!Ext.isEmpty(h.RotateCenterZ)) uri.orcz = h.RotateCenterZ;
		if(!Ext.isEmpty(h.RotateAxisVectorX)) uri.orax = h.RotateAxisVectorX;
		if(!Ext.isEmpty(h.RotateAxisVectorY)) uri.oray = h.RotateAxisVectorY;
		if(!Ext.isEmpty(h.RotateAxisVectorZ)) uri.oraz = h.RotateAxisVectorZ;
		if(!Ext.isEmpty(h.RotateDegree)) uri.ordg = h.RotateDegree;
	}

	if(clearEmpty) self._deletesEmptyProp(uri);
	if(toStringOpts){
		var editURL = getEditUrl() + "?tp_ap=" + encodeURIComponent(Ext.urlEncode(uri));
		return editURL;
	}else{
		return uri;
	}
};

//URI文字からJSON文字列を生成する
ag_extensions.toJSON.URI2JSON = function(URIStr,aOpts){
	var self = this;
	var uriObj;
	if(!Ext.isEmpty(URIStr)){
		if(typeof URIStr == 'string'){
			if(URIStr.indexOf("?")>=0) URIStr = URIStr.substr(URIStr.indexOf("?")+1);
			try{uriObj = Ext.urlDecode(URIStr,false);}catch(e){if(window.console && console.error) console.error(e);}
			if(uriObj && uriObj.tp_ap) uriObj = Ext.urlDecode(uriObj.tp_ap);
		}else if(typeof URIStr == 'object'){
			uriObj = URIStr;
		}
	}
	if(Ext.isEmpty(uriObj)) return null;

	aOpts = Ext.apply({},aOpts||{},{
		callback: function(value){
//			console.log("callback()");
//			console.log(value);
		},
		mapPin: true,
		toString: false,
		clearEmpty: true
	});
	var toStringOpts = aOpts.toString;
	var clearEmpty = aOpts.clearEmpty;

	var jsonObj = {
		Common: Ext.apply({},{Version:bp3d.defaults.bp3d_version},self.defaults.Common()),
		Window: self.defaults.Window()
	};
	if(!Ext.isEmpty(uriObj.model)) jsonObj.Common.Model = uriObj.model;
	if(!Ext.isEmpty(uriObj.bv)) jsonObj.Common.Version = uriObj.bv;
	if(!Ext.isEmpty(uriObj.av)) jsonObj.Common.AnatomogramVersion = uriObj.av;
	if(!Ext.isEmpty(uriObj.sx)) jsonObj.Common.ScalarMaximum = uriObj.sx-0;
	if(!Ext.isEmpty(uriObj.sn)) jsonObj.Common.ScalarMinimum = uriObj.sn-0;
	if(!Ext.isEmpty(uriObj.cf)) jsonObj.Common.ColorbarFlag = uriObj.cf-0?true:false;
	if(!Ext.isEmpty(uriObj.hf)) jsonObj.Common.ScalarColorFlag = uriObj.hf-0?true:false;
	if(!Ext.isEmpty(uriObj.tn)) jsonObj.Common.TreeName = uriObj.tn;
	if(!Ext.isEmpty(uriObj.dt)) jsonObj.Common.DateTime = uriObj.dt;
	if(!Ext.isEmpty(uriObj.crd)) jsonObj.Common.CoordinateSystemName = uriObj.crd;
	if(!Ext.isEmpty(uriObj.np)) jsonObj.Common.PinNumberDrawFlag = uriObj.np-0?true:false;
	if(!Ext.isEmpty(uriObj.dp)) jsonObj.Common.PinDescriptionDrawFlag = uriObj.dp-0?true:false;
	if(!Ext.isEmpty(uriObj.dpl)) jsonObj.Common.PinIndicationLineDrawFlag = uriObj.dpl-0;
	if(clearEmpty) self._deletesEmptyProp(jsonObj.Common);

	if(!Ext.isEmpty(uriObj.iw)) jsonObj.Window.ImageWidth = uriObj.iw-0;
	if(!Ext.isEmpty(uriObj.ih)) jsonObj.Window.ImageHeight = uriObj.ih-0;
	if(!Ext.isEmpty(uriObj.bcl)) jsonObj.Window.BackgroundColor = uriObj.bcl;
	if(!Ext.isEmpty(uriObj.bga)) jsonObj.Window.BackgroundOpacity = uriObj.bga-0;
//	if(!Ext.isEmpty(uriObj.gdr)) jsonObj.Window.GridFlag = uriObj.gdr-0?true:false;
	if(!Ext.isEmpty(uriObj.gdr)) jsonObj.Window.GridFlag = (uriObj.gdr==="true");
	if(!Ext.isEmpty(uriObj.gtc)) jsonObj.Window.GridTickInterval = uriObj.gtc-0;
	if(!Ext.isEmpty(uriObj.gcl)) jsonObj.Window.GridColor = uriObj.gcl;
	if(clearEmpty)self._deletesEmptyProp(jsonObj.Window);

	if(
		!Ext.isEmpty(uriObj.cx) && !Ext.isEmpty(uriObj.cy) && !Ext.isEmpty(uriObj.cz) && !isNaN(Number(uriObj.cx)) && !isNaN(Number(uriObj.cy)) && !isNaN(Number(uriObj.cz)) &&
		!Ext.isEmpty(uriObj.tx) && !Ext.isEmpty(uriObj.ty) && !Ext.isEmpty(uriObj.tz) && !isNaN(Number(uriObj.tx)) && !isNaN(Number(uriObj.ty)) && !isNaN(Number(uriObj.tz)) &&
		!Ext.isEmpty(uriObj.ux) && !Ext.isEmpty(uriObj.uy) && !Ext.isEmpty(uriObj.uz) && !isNaN(Number(uriObj.ux)) && !isNaN(Number(uriObj.uy)) && !isNaN(Number(uriObj.uz))
	){
		jsonObj.Camera = Ext.apply({},{
			CameraMode:"camera",
			CameraX: parseFloat(uriObj.cx),
			CameraY: parseFloat(uriObj.cy),
			CameraZ: parseFloat(uriObj.cz),
			TargetX: parseFloat(uriObj.tx),
			TargetY: parseFloat(uriObj.ty),
			TargetZ: parseFloat(uriObj.tz),
			CameraUpVectorX: parseFloat(uriObj.ux),
			CameraUpVectorY: parseFloat(uriObj.uy),
			CameraUpVectorZ: parseFloat(uriObj.uz)
		},self.defaults.Camera());
	}
	if(!Ext.isEmpty(uriObj.zm) && !isNaN(Number(uriObj.zm))){
		if(Ext.isEmpty(jsonObj.Camera)) jsonObj.Camera = Ext.apply({},{CameraMode:"front"},self.defaults.Camera());
		jsonObj.Camera.Zoom = parseFloat(uriObj.zm)*5;
	}
	if(clearEmpty && jsonObj.Camera) self._deletesEmptyProp(jsonObj.Camera);

	if(!Ext.isEmpty(uriObj.lp) || !Ext.isEmpty(uriObj.lc) || !Ext.isEmpty(uriObj.lt) || !Ext.isEmpty(uriObj.le) || !Ext.isEmpty(uriObj.la)){
		jsonObj.Legend = self.defaults.Legend();
		if(!Ext.isEmpty(uriObj.dl)) jsonObj.Legend.DrawLegendFlag = uriObj.dl-0?true:false;
		if(!Ext.isEmpty(uriObj.lp)) jsonObj.Legend.LegendPosition = uriObj.lp;
		if(!Ext.isEmpty(uriObj.lc)) jsonObj.Legend.LegendColor = uriObj.lc.toUpperCase();
		if(!Ext.isEmpty(uriObj.lt)) jsonObj.Legend.LegendTitle = uriObj.lt;
		if(!Ext.isEmpty(uriObj.le)) jsonObj.Legend.Legend = uriObj.le;
		if(!Ext.isEmpty(uriObj.la)) jsonObj.Legend.LegendAuthor = uriObj.la;
	}
	if(clearEmpty && jsonObj.Legend) self._deletesEmptyProp(jsonObj.Legend);

	if(!Ext.isEmpty(uriObj.oid001) || !Ext.isEmpty(uriObj.onm001)){
		var defValue = self.defaults.Part();
		jsonObj.Part = [];
		var UseForBoundingBoxFlag = false;
		for(var i=0;;i++){
			var num = makeAnatomoOrganNumber(i+1);
			if(Ext.isEmpty(uriObj['oid'+num]) && Ext.isEmpty(uriObj['onm'+num])) break;
			var Part = self.defaults.Part();
			Part.PartDeleteFlag = false;
			Part.UseForBoundingBoxFlag = false;

			if(!Ext.isEmpty(uriObj['oid'+num])) Part.PartID = uriObj['oid'+num];
			if(!Ext.isEmpty(uriObj['onm'+num])) Part.PartName = uriObj['onm'+num];
			if(!Ext.isEmpty(uriObj['ocl'+num])) Part.PartColor = uriObj['ocl'+num];
			if(!Ext.isEmpty(uriObj['osc'+num])){
				Part.PartScalar = uriObj['osc'+num]-0;
				Part.ScalarColorFlag = true;
			}
			if(!Ext.isEmpty(uriObj['oop'+num])) Part.PartOpacity = uriObj['oop'+num]-0;
			if(!Ext.isEmpty(uriObj['orp'+num])) Part.PartRepresentation = uriObj['orp'+num];
			if(!Ext.isEmpty(uriObj['osz'+num])){
				if(uriObj['osz'+num]=='H'){
					Part.PartDeleteFlag = true;
				}else if(uriObj['osz'+num]=='Z'){
					Part.UseForBoundingBoxFlag = UseForBoundingBoxFlag = true;
				}
			}
			if(clearEmpty) self._deletesEmptyProp(Part);
			jsonObj.Part.push(Part);
		}
		if(jsonObj.Part){
			if(jsonObj.Part.length <= 0){
				delete jsonObj.Part;
			}else if(!UseForBoundingBoxFlag){
				Ext.each(jsonObj.Part,function(Part){
					Part.UseForBoundingBoxFlag = true;
				});
			}
		}
	}
	if(!Ext.isEmpty(uriObj.pno001)){
		var defValue = self.defaults.Pin();
		jsonObj.Pin = [];
		for(var i=0;;i++){
			var num = makeAnatomoOrganNumber(i+1);
			if(Ext.isEmpty(uriObj['pno'+num])) break;
			var Pin = self.defaults.Pin();
			if(!Ext.isEmpty(uriObj['px'+num]))  Pin.PinX = uriObj['px'+num]-0;
			if(!Ext.isEmpty(uriObj['py'+num]))  Pin.PinY = uriObj['py'+num]-0;
			if(!Ext.isEmpty(uriObj['pz'+num]))  Pin.PinZ = uriObj['pz'+num]-0;
			if(!Ext.isEmpty(uriObj['pax'+num])) Pin.PinArrowVectorX = uriObj['pax'+num]-0;
			if(!Ext.isEmpty(uriObj['pay'+num])) Pin.PinArrowVectorY = uriObj['pay'+num]-0;
			if(!Ext.isEmpty(uriObj['paz'+num])) Pin.PinArrowVectorZ = uriObj['paz'+num]-0;
			if(!Ext.isEmpty(uriObj['pux'+num])) Pin.PinUpVectorX = uriObj['pux'+num]-0;
			if(!Ext.isEmpty(uriObj['puy'+num])) Pin.PinUpVectorY = uriObj['puy'+num]-0;
			if(!Ext.isEmpty(uriObj['puz'+num])) Pin.PinUpVectorZ = uriObj['puz'+num]-0;
			if(!Ext.isEmpty(uriObj['pdd'+num])) Pin.PinDescriptionDrawFlag = uriObj['pdd'+num]-0?true:false;
			if(!Ext.isEmpty(uriObj['pnd'+num])) Pin.PinNumberDrawFlag = uriObj['pnd'+num]-0?true:false;
			if(!Ext.isEmpty(uriObj['pdc'+num])) Pin.PinDescriptionColor = uriObj['pdc'+num].toUpperCase();
			if(!Ext.isEmpty(uriObj['ps'+num])){
				Pin.PinShape = self.pinShapeAbbr2PinShape(uriObj['ps'+num]);
				Pin.PinSize = self.pinShapeAbbr2PinSize(uriObj['ps'+num]);
			}
			if(!Ext.isEmpty(uriObj['pcl'+num])) Pin.PinColor = uriObj['pcl'+num].toUpperCase();
			if(!Ext.isEmpty(uriObj['poi'+num])) Pin.PinPartID = uriObj['poi'+num];
			if(!Ext.isEmpty(uriObj['pon'+num])) Pin.PinPartName = uriObj['pon'+num];
			if(!Ext.isEmpty(uriObj['pd'+num]))  Pin.PinDescription = uriObj['pd'+num];
			if(!Ext.isEmpty(uriObj['pcd'+num])) Pin.PinCoordinateSystemName = uriObj['pcd'+num];
			if(window.ag_extensions && ag_extensions.global_pin){
				if(!Ext.isEmpty(uriObj['pid'+num])) Pin.PinID = uriObj['pid'+num];
				if(!Ext.isEmpty(uriObj['pgid'+num])) Pin.PinGroupID = uriObj['pgid'+num];
			}
			if(Ext.isEmpty(Pin.PinID)) Pin.PinID = i+1;
			jsonObj.Pin.push(Pin);
		}
		if(jsonObj.Pin && jsonObj.Pin.length ==0) delete jsonObj.Pin;
	}

	if(jsonObj.Pin && jsonObj.Pin.length){
		if(aOpts.mapPin){
			if(aOpts.callback){
				self._getMapPin(jsonObj,function(rtnJsonMapStr){
					if(!Ext.isEmpty(rtnJsonMapStr)){
						self._mergeMapPin(jsonObj.Pin,rtnJsonMapStr,aOpts);
					}else if(clearEmpty){
						Ext.each(jsonObj.Pin,function(pin,i,a){
							self._deletesEmptyProp(pin);
						});
					}
					var rtn;
					if(toStringOpts){
						var jsonStr = Ext.util.JSON.encode(jsonObj);
						if(typeof toStringOpts == 'object') jsonStr = self._formatJSONStr(jsonStr,toStringOpts);
						rtn = jsonStr;
					}else{
						rtn = jsonObj;
					}
					(aOpts.callback)(rtn);
				});
				var rtn;
				if(toStringOpts){
					var jsonStr = Ext.util.JSON.encode(jsonObj);
					if(typeof toStringOpts == 'object') jsonStr = self._formatJSONStr(jsonStr,toStringOpts);
					rtn = jsonStr;
				}else{
					rtn = jsonObj;
				}
				return rtn;
			}else{
				var rtnJsonMapStr = self._getMapPin(jsonObj);
				if(!Ext.isEmpty(rtnJsonMapStr)){
					self._mergeMapPin(jsonObj.Pin,rtnJsonMapStr,aOpts);
				}else if(clearEmpty){
					Ext.each(jsonObj.Pin,function(pin,i,a){
						self._deletesEmptyProp(pin);
					});
				}
			}
		}else if(clearEmpty){
			Ext.each(jsonObj.Pin,function(pin,i,a){
				self._deletesEmptyProp(pin);
			});
		}
	}

	if(!Ext.isEmpty(uriObj['px']) && !Ext.isEmpty(uriObj['py'])){
		jsonObj.Pick = self.defaults.Pick();
		jsonObj.Pick.ScreenPosX = uriObj['px']-0;
		jsonObj.Pick.ScreenPosY = uriObj['py']-0;
		if(!Ext.isEmpty(uriObj['vr'])) jsonObj.Pick.VoxelRadius = uriObj['vr']-0;
		if(clearEmpty) self._deletesEmptyProp(jsonObj.Pick);
	}

	if(
		!Ext.isEmpty(uriObj['autorotate']) &&
		!Ext.isEmpty(uriObj['orcx']) &&
		!Ext.isEmpty(uriObj['orcy']) &&
		!Ext.isEmpty(uriObj['orcz']) &&
		!Ext.isEmpty(uriObj['orax']) &&
		!Ext.isEmpty(uriObj['oray']) &&
		!Ext.isEmpty(uriObj['oraz']) &&
		!Ext.isEmpty(uriObj['ordg'])
	){
		jsonObj.ObjectRotate = self.defaults.ObjectRotate();
		jsonObj.ObjectRotate.DateTime = uriObj['autorotate'];
		jsonObj.ObjectRotate.RotateCenterX = uriObj['orcx']-0;
		jsonObj.ObjectRotate.RotateCenterY = uriObj['orcy']-0;
		jsonObj.ObjectRotate.RotateCenterZ = uriObj['orcz']-0;
		jsonObj.ObjectRotate.RotateAxisVectorX = uriObj['orax']-0;
		jsonObj.ObjectRotate.RotateAxisVectorY = uriObj['oray']-0;
		jsonObj.ObjectRotate.RotateAxisVectorZ = uriObj['oraz']-0;
		jsonObj.ObjectRotate.RotateDegree = uriObj['ordg']-0;
		if(clearEmpty) self._deletesEmptyProp(jsonObj.ObjectRotate);
	}

	var rtn;
	if(toStringOpts){
		var jsonStr = Ext.util.JSON.encode(jsonObj);
		if(typeof toStringOpts == 'object') jsonStr = self._formatJSONStr(jsonStr,toStringOpts);
		rtn = jsonStr;
	}else{
		rtn = jsonObj;
	}
	if(aOpts.callback) (aOpts.callback)(rtn);
	return rtn;
};

ag_extensions.toJSON._formatJSONStr = function(jsonStr,aOpts){
	aOpts = Ext.apply({},aOpts||{},{indent:2});
	var indent = aOpts.indent;
	var idx=0;
	var l = '';
	var m = '';
	var r = jsonStr;
	do {
		if(r.match(/[\{\[\]\},]/)){
			l += RegExp.leftContext;
			m = RegExp.lastMatch;
			r = RegExp.rightContext;
			if(m=='{' || m=='['){
				idx+=indent;
				l+=m+"\n"+String.leftPad('',idx);
			}else if(m==','){
				l+=m+"\n"+String.leftPad('',idx);
			}else if(m=='}' || m==']'){
				idx-=indent;
				l += "\n"+String.leftPad('',idx)+m;
			}
		}else{
			l+=r;
			break;
		}
	}while(1);
	return l;
};

ag_extensions.toJSON._deletesEmptyProp = function(Obj){
	for(var key in Obj){
		if(Ext.isEmpty(Obj[key])) delete Obj[key];
	}
};

ag_extensions.toJSON._mergeMapPin = function(PinArray,rtnJsonMapStr,aOpts){
	var self = this;
	if(!Ext.isEmpty(rtnJsonMapStr)){
		var rtnJson;
		try{rtnJson = Ext.util.JSON.decode(rtnJsonMapStr);}catch(e){}
		if(rtnJson && rtnJson.Map && rtnJson.Map.length){
			var mapColl = new Ext.util.MixedCollection(true,function(item){return item.PinID;});
			mapColl.addAll(rtnJson.Map);
			Ext.each(PinArray,function(pin,i,a){
				var map = mapColl.get(pin.PinID);
				if(!Ext.isEmpty(map)) Ext.apply(pin,map,pin);
				if(aOpts.clearEmpty) self._deletesEmptyProp(pin);
			});
		}
	}
};

ag_extensions.toJSON._getMapPin = function(jsonObj,aCallback){
	var self = this;
	var config = {
		type: 'POST',
		url: cgipath.map,
		data: Ext.util.JSON.encode(jsonObj)
	};
	if(aCallback){
		config.async = true;
		config.complete = function(XMLHttpRequest,textStatus){
			if(textStatus=='success'){
				(aCallback)(XMLHttpRequest.responseText);
			}else{
				(aCallback)();
			}
		};
		$.ajax(config);
		return;
	}else{
		config.async = false;
		var rtnJsonMapStr = $.ajax(config).responseText;
		return rtnJsonMapStr;
	}
};
