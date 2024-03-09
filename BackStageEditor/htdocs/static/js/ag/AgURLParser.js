var AgURLParser = {

	newCommon : function() {
		return {                            // 共通項目	レンダリング、座標計算等において、BodyParts3Dサーバが動作する上で共通に必要な項目
//			Model                : "bp3d",    // モデル	文字列	
			Model                : DEF_MODEL,    // モデル	文字列	
//			Version              : "3.0",     // バージョン	文字列	
			Version              : DEF_VERSION,     // バージョン	文字列	
			AnatomogramVersion   : "20110318",// アナトモグラム形式のバージョン	文字列	
			ScalarMaximum        :  65535,    // Scalar Maximum	整数	
			ScalarMinimum        : -65535,    // Scalar Minimum	整数	
			ColorbarFlag         : false,     // カラーバーの描画フラグ	Boolean	
			ScalarColorFlag      : false,     // 臓器描画にScalarColorを利用するフラグ	Boolean	
//			TreeName             : "bp3d",    // 利用するTree名	文字列	
			TreeName             : DEF_TREE,    // 利用するTree名	文字列	
			DateTime             : null,      // "yyyymmddhhmmss"	現在時刻	文字列	
			CoordinateSystemName : "bp3d",    // 描画座標系	文字列	
			CopyrightType        : null       // コピーライト画像のサイズ（未指定、large、midium、small）	文字列	
		};
	},

	parseCommon : function(param) {
		var Common;
		for(var c_key in param){
			if(!Common) Common = AgURLParser.newCommon();
			var c_val = param[c_key];
			if(c_key == "av"){
				delete param[c_key];
			}else if(c_key == "sx"){
				Common.ScalarMaximum = Number(c_val);
				delete param[c_key];
			}else if(c_key == "sn"){
				Common.ScalarMinimum = Number(c_val);
				delete param[c_key];
			}else if(c_key == "cf"){
				if(c_val == '0' || c_val == 'false'){
					Common.ColorbarFlag = false;
				}else{
					Common.ColorbarFlag = true;
				}
				delete param[c_key];
			}else if(c_key == "hf"){
				if(c_val == '0' || c_val == 'false'){
					Common.ScalarColorFlag = false;
				}else{
					Common.ScalarColorFlag = true;
				}
				delete param[c_key];
			}else if(c_key == "tn"){
				if(c_val == "isa"){
					Common.TreeName = c_val;
				}else if(c_val == "partof"){
					Common.TreeName = c_val;
				}
				delete param[c_key];
			}else if(c_key == "model"){
				Common.Model = c_val;
				delete param[c_key];
			}else if(c_key == "bv"){
				Common.Version = c_val;
				delete param[c_key];
			}else if(c_key == "dt"){
				Common.DateTime = c_val;
				delete param[c_key];
			}else if(c_key == "crd"){
				Common.CoordinateSystemName = c_val;
				delete param[c_key];
			}else if(c_key == "cprt"){
				Common.CopyrightType = c_val;
				delete param[c_key];
			}else if(c_key == "dp"){
				if(param.dp != '0' && param.dp != 'false') Common.PinDescriptionDrawFlag = true;
				delete param[c_key];
			}else if(c_key == "dpl"){
				Common.PinIndicationLineDrawFlag = Number(c_val);
				delete param[c_key];
			}else if(c_key == "dpod"){
				if(param.dpod != '0' && param.dpod != 'false') Common.PointDescriptionDrawFlag = true;
				delete param[c_key];
			}else if(c_key == "dpol"){
				Common.PointIndicationLineDrawFlag = Number(c_val);
				delete param[c_key];
			}
		}
		return Common;
	},

	newWindow : function() {
		return {                       // ウィンドウ項目	Window（描画画像全体）に関する項目
			ImageWidth        : 500,     // 画像サイズ（width）	整数
			ImageHeight       : 500,     // 画像サイズ（height）	整数
			BackgroundColor   : "FFFFFF",// 背景色RGB（16進数6桁）	文字列
			BackgroundOpacity : 100,     // 背景の不透明度（0～100）	整数
			GridFlag          : false,   // Gridの描画有無	Boolean
			GridTickInterval  : 100,     // グリッドの描画単位（mm）	整数
			GridColor         : "00FF00" // グリッドの描画色RGB（16進数6桁）	文字列
		};
	},

	parseWindow : function(param) {
		var Window;
		for(var c_key in param){
			if(!Window) Window = AgURLParser.newWindow();
			var c_val = param[c_key];
			if(c_key == "iw"){
				Window['ImageWidth'] = Number(c_val);
				delete param[c_key];
			}else if(c_key == "ih"){
				Window['ImageHeight'] = Number(c_val);
				delete param[c_key];
			}else if(c_key == "bcl"){
				Window['BackgroundColor'] = (new String(c_val)).toUpperCase();
				delete param[c_key];
			}else if(c_key == "bga"){
				Window['BackgroundOpacity'] = Number(c_val);
				delete param[c_key];
			}else if(c_key == "gdr"){
				if(c_val == '0' || c_val == 'false'){
					Window['GridFlag'] = false;
				}else{
					Window['GridFlag'] = true;
				}
				delete param[c_key];
			}else if(c_key == "gtc"){
				Window['GridTickInterval'] = Number(c_val);
				delete param[c_key];
			}else if(c_key == "gcl"){
				Window['GridColor'] = (new String(c_val)).toUpperCase();
				delete param[c_key];
			}
		}
		return Window;
	},

	newCamera : function() {
		return {
			CameraMode         : 'camera',             // カメラ位置のモード（camera,front,back,left,right,top,bottom）。"camera"の場合にのみカメラ、ターゲット、upベクトルの指定が有効。	文字列
			CameraX            :    2.7979888916016167,// カメラのx座標	Double
			CameraY            : -998.4280435445771,   // カメラのy座標	Double
			CameraZ            :  809.7306805551052,   // カメラのz座標	Double
			TargetX            :    2.7979888916015625,// ターゲット（カメラ視線の中心）のx座標	Double
			TargetY            : -110.37168800830841,  // ターゲットのy座標	Double
			TargetZ            :  809.7306805551052,   // ターゲットのz座標	Double
			CameraUpVectorX    : 0,                    // カメラupベクトルx要素	Double
			CameraUpVectorY    : 0,                    // カメラupベクトルy要素	Double
			CameraUpVectorZ    : 1,                    // カメラupベクトルz要素	Double
			Zoom               : 0,                    // ズーム値（0～19.8）	Double
			AddLatitudeDegree  : 0,                    // 緯度方向への追加回転角度（0～360）	Double
			AddLongitudeDegree : 0                     // 経度方向への追加回転角度（0～360）	Double
		};
	},

	parseCamera : function(param) {
		var Camera;
		for(var c_key in param){
			if(!Camera) Camera = AgURLParser.newCamera();
			var c_val = param[c_key];
			if(c_key == "cx"){
				Camera.CameraX = Number(c_val);
				delete param[c_key];
			}else if(c_key == "cy"){
				Camera.CameraY = Number(c_val);
				delete param[c_key];
			}else if(c_key == "cz"){
				Camera.CameraZ = Number(c_val);
				delete param[c_key];
			}else if(c_key == "tx"){
				Camera.TargetX = Number(c_val);
				delete param[c_key];
			}else if(c_key == "ty"){
				Camera.TargetY = Number(c_val);
				delete param[c_key];
			}else if(c_key == "tz"){
				Camera.TargetZ = Number(c_val);
				delete param[c_key];
			}else if(c_key == "ux"){
				Camera.CameraUpVectorX = Number(c_val);
				delete param[c_key];
			}else if(c_key == "uy"){
				Camera.CameraUpVectorY = Number(c_val);
				delete param[c_key];
			}else if(c_key == "uz"){
				Camera.CameraUpVectorZ = Number(c_val);
				delete param[c_key];
			}else if(c_key == "zm"){
				Camera.Zoom = Number(c_val)*5;
				delete param[c_key];
			}else if(c_key == "cameraMode"){
				Camera.CameraMode = c_val;
				delete param[c_key];
			}else if(c_key == "addLongitude"){
				Camera.AddLongitudeDegree = Number(c_val);
				delete param[c_key];
			}else if(c_key == "addLatitude"){
				Camera.AddLatitudeDegree = Number(c_val);
				delete param[c_key];
			}
		}
//		if(Camera && !Camera.CameraMode) Camera.CameraMode = 'camera';
		return Camera;
	},

	newPart : function() {
		return {                              // パーツ項目	Part（臓器）に関する項目	複数が前提のため、要素が1の場合であっても配列として記載
			PartModel             : null,       // 臓器モデル名	文字列
			PartVersion           : null,       // 臓器バージョン	文字列
			PartID                : null,       // 臓器ID（名称に優先される）	文字列
			PartName              : null,       // 臓器名	文字列
			PartColor             : "FFFFFF",   // 臓器色RGB（16進数6桁）	文字列
			PartScalar            : null,       // 臓器スカラー値	Double
			PartScalarFlag        : false,      // 臓器をスカラー値で描画するFlag	Boolean
			PartOpacity           : 1.0,        // 臓器不透明度	Double
			PartRepresentation    : "surface",  // 臓器描画方法（surface、wireframe、point）	文字列
			UseForBoundingBoxFlag : true,       // BoundingBox計算への利用有無	Boolean
			PartDeleteFlag        : false       // 臓器の削除フラグ（臓器引き算用）	Boolean
		};
	},

	parsePart : function(param) {
		var Part = [];
		var UseForBoundingBoxFlag;
		for(var i=1;;i++){
			var id = Ext.String.leftPad(i, 3, '0');

			if(!param["oid"+id] && !param["onm"+id]) break;

			var PartItem = AgURLParser.newPart();
			var keynum = 0;
			for(var c_key in param){
				var c_val = param[c_key];
				if(c_key == "oid"+id){
					PartItem["PartID"] = c_val;
					delete param[c_key];
					keynum++;
				}else if(c_key == "onm"+id){
					PartItem["PartName"] = c_val;
					delete param[c_key];
					keynum++;
				}else if(c_key == "ocl"+id){
					PartItem["PartColor"] = (new String(c_val)).toUpperCase();
					delete param[c_key];
					keynum++;
				}else if(c_key == "osc"+id){
					PartItem["PartScalar"] = Number(c_val);
					PartItem["PartScalarFlag"] = true;
					PartItem["ScalarColorFlag"] = true;
					delete param[c_key];
					keynum++;
				}else if(c_key == "osz"+id){
					if(c_val == 'H'){
						PartItem["PartDeleteFlag"] = true;
					}else if(c_val == 'Z'){
						PartItem["UseForBoundingBoxFlag"] = true;
						UseForBoundingBoxFlag = true;
					}
					delete param[c_key];
					keynum++;
				}else if(c_key == "oop"+id){
					PartItem["PartOpacity"] = Number(c_val);
					delete param[c_key];
					keynum++;
				}else if(c_key == "orp"+id){
					if(c_val == "W"){
						PartItem["PartRepresentation"] = "wireframe";
					}else if(c_val == "P"){
						PartItem["PartRepresentation"] = "points";
					}else{
						PartItem["PartRepresentation"] = "surface";
					}
					delete param[c_key];
					keynum++;
				}else if(c_key  == "odcp"+id){
					if(c_val != '0' && c_val != 'false') PartItem["PartDrawChildPoint"] = true;
					delete param[c_key];
					keynum++;
				}
			}
			if(keynum>0) Part.push(PartItem);
		}
		if(UseForBoundingBoxFlag){
			for(var i in Part){
				var PartItem = Part[i];
				if(!PartItem["UseForBoundingBoxFlag"]) PartItem["UseForBoundingBoxFlag"] = false;
			}
		}
		return (Part.length > 0 ? Part : undefined);
	},


	newLegend : function() {
		return {                      // Legend項目	Legendに関する項目
			DrawLegendFlag : false,     // Legendの描画有無フラグ	Boolean	
			LegendPosition : "UL",      // Legendの描画位置（UL:左上のみ）	文字列	
//			LegendColor    : "FFFFFF",  // Legendの描画色RGB（16進数6桁）	文字列	
			LegendColor    : "000000",  // Legendの描画色RGB（16進数6桁）	文字列	
			LegendTitle    : null,      // LegendのTitle	文字列	
			Legend         : null,      // Legend	文字列	
			LegendAuthor   : null       // Legendオーサー	文字列
		};
	},

	parseLegend : function(param) {
		var Legend = AgURLParser.newLegend();
		var keynum = 0;
		for(var c_key in param){
			var c_val = param[c_key];
			if(c_key == "dl"){
				if(c_val != '0' && c_val != 'false') Legend['DrawLegendFlag'] = true;
				delete param[c_key];
				keynum++;
			}else if(c_key == "lp"){
				Legend['LegendPosition'] = c_val;
				delete param[c_key];
				keynum++;
			}else if(c_key == "lc"){
				Legend['LegendColor'] = (new String(c_val)).toUpperCase();
				delete param[c_key];
				keynum++;
			}else if(c_key == "lt"){
				Legend['LegendTitle'] = c_val;
				delete param[c_key];
				keynum++;
			}else if(c_key == "le"){
				Legend['Legend'] = c_val;
				delete param[c_key];
				keynum++;
			}else if(c_key == "la"){
				Legend['LegendAuthor'] = c_val;
				delete param[c_key];
				keynum++;
			}
		}
		return keynum>0 ? Legend : undefined;
	},

	newPin : function() {
		return {                                // ピン項目	Pinに関する項目	要素が1の場合であっても配列として記載
			PinPartID                 : null,     // PinID	文字列	
			PinX                      : 0,        // Pinの3次元空間上x座標	Double	
			PinY                      : 0,        // Pinの3次元空間上y座標	Double	
			PinZ                      : 0,        // Pinの3次元空間上z座標	Double	
			PinArrowVectorX           : 0,        // Pinのベクトルx要素	Double	
			PinArrowVectorY           : 0,        // Pinのベクトルy要素	Double	
			PinArrowVectorZ           : 0,        // Pinのベクトルz要素	Double	
			PinUpVectorX              : 0,        // PinのUpベクトルx要素	Double	
			PinUpVectorY              : 0,        // PinのUpベクトルy要素	Double	
			PinUpVectorZ              : 0,        // PinのUpベクトルz要素	Double	
			PinDescription            : null,     // Pinのデスクリプション	文字列	
			PinDescriptionDrawFlag    : false,    // Pinのデスクリプション描画フラグ	Boolean	
			PinDescriptionColor       : "FFFFFF", // デスクリプション描画色RGB(16進6桁）	文字列	
			PinIndicationLineDrawFlag : 0,        // ピンからPin Descriptionへの線描画指定	int
			                                      // (0：ピンからDescriptionへの線描画無し、1：ピンの先端からDescriptionへの線描画、2：ピンの終端からDescriptionへの線描画）
			                                      // ※Descriptionが描画されていないと線も描画しない。
			PinColor                  : "FFFFFF", // Pinの描画色RGB(16進6桁)	文字列	
			PinShape                  : null,     // ピン形状	文字列	
			PinOrganID                : null,     // 	文字列	
			PinOrganName              : null,     // 	文字列	
			PinOrganGroup             : null,     // 	文字列	
			PinOrganGrouppath         : null,     // 	文字列	
			PinOrganPath              : null,     // 	文字列	
			PinCoordinateSystemName   : "bp3d"    // ピン作成時座標系	文字列	
		}
	},

	parsePin : function(param) {
		var Pin = [];

		for(var i=1;;i++){
			var id = Ext.String.leftPad(i, 3, '0');
			if(!param["pno"+id]) break;

			var PinItem = AgURLParser.newPin();
			var keynum = 0;
			for(var c_key in param){
				var c_val = param[c_key];

				if(c_key == "pno"+id) {
					PinItem['PinPartNo'] = c_val;
					PinItem['PinID'] = c_val;
					delete param[c_key];
					keynum++;
				}else if(c_key == "px"+id) {
					PinItem['PinX'] = Number(c_val);
					delete param[c_key];
					keynum++;
				}else if(c_key == "py"+id) {
					PinItem['PinY'] = Number(c_val);
					delete param[c_key];
					keynum++;
				}else if(c_key == "pz"+id) {
					PinItem['PinZ'] = Number(c_val);
					delete param[c_key];
					keynum++;
				}else if(c_key == "pax"+id) {
					PinItem['PinArrowVectorX'] = Number(c_val);
					delete param[c_key];
					keynum++;
				}else if(c_key == "pay"+id) {
					PinItem['PinArrowVectorY'] = Number(c_val);
					delete param[c_key];
					keynum++;
				}else if(c_key == "paz"+id) {
					PinItem['PinArrowVectorZ'] = Number(c_val);
					delete param[c_key];
					keynum++;
				}else if(c_key == "pux"+id) {
					PinItem['PinUpVectorX'] = Number(c_val);
					delete param[c_key];
					keynum++;
				}else if(c_key == "puy"+id) {
					PinItem['PinUpVectorY'] = Number(c_val);
					delete param[c_key];
					keynum++;
				}else if(c_key == "puz"+id) {
					PinItem['PinUpVectorZ'] = Number(c_val);
					delete param[c_key];
					keynum++;
				}else if(c_key == "pcl"+id) {
					PinItem['PinColor'] = (new String(c_val)).toUpperCase();
					delete param[c_key];
					keynum++;
				}else if(c_key == "pd"+id) {
					PinItem['PinDescription'] = c_val;
					delete param[c_key];
					keynum++;
				}else if(c_key == "pdc"+id) {
					PinItem['PinDescriptionColor'] = (new String(c_val)).toUpperCase();
					delete param[c_key];
					keynum++;
				}else if(c_key == "pdd"+id) {
					if(c_val != '0' && c_val != 'false') PinItem['PinDescriptionDrawFlag'] = true;
					delete param[c_key];
					keynum++;
				}else if(c_key == "poi"+id) {
					PinItem['PinOrganID'] = c_val;
					delete param[c_key];
					keynum++;
				}else if(c_key == "pon"+id) {
					PinItem['PinOrganName'] = c_val;
					delete param[c_key];
					keynum++;
				}else if(c_key == "ps"+id) {
					if(c_val == "CC"){
						PinItem['PinShape'] = "CONE";
					}else if(c_val == "PS"){
						PinItem['PinShape'] = "PIN";
						PinItem['PinSize'] = 10.0;
					}else if(c_val == "PM"){
						PinItem['PinShape'] = "PIN_MIDIUM";
						PinItem['PinSize'] = 15.0;
					}else if(c_val == "PL"){
						PinItem['PinShape'] = "PIN_LONG";
						PinItem['PinSize'] = 20.0;
					}else if(c_val == "SC"){
						PinItem['PinShape'] = "CIRCLE";
						PinItem['PinSize'] = 10.0;
					}
					delete param[c_key];
					keynum++;
				}else if(c_key == "pcd"+id) {
					PinItem['PinCoordinateSystemName'] = c_val;
					delete param[c_key];
					keynum++;
				}
			}
			if(keynum>0) Pin.push(PinItem);
		}
		return (Pin.length > 0 ? Pin : undefined);
	},

	newExtensionPartGroup : function() {
		return {                              //
			PartGroupId           : null,       // 臓器グループID	文字列
			PartGroupName         : null,       // 臓器グループ名	文字列
			PartGroupPath         : null,       // 臓器グループのパス	文字列
			PartGroupItems        : []          // 臓器グループの部品	配列
		};
	},
	newExtensionPart : function() {
		return {                              // パーツ項目	Part（臓器）に関する項目	複数が前提のため、要素が1の場合であっても配列として記載
			PartId                : null,       // 臓器ID	文字列
			PartName              : null,       // 臓器名	文字列
			PartColor             : "FFFFFF",   // 臓器色RGB（16進数6桁）	文字列
			PartScalar            : 0.0,        // 臓器スカラー値	Double
			PartScalarFlag        : false,      // 臓器をスカラー値で描画するFlag	Boolean
			PartOpacity           : 1.0,        // 臓器不透明度	Double
			PartRepresentation    : "surface",  // 臓器描画方法（surface、wireframe、point）	文字列
			UseForBoundingBoxFlag : true,       // BoundingBox計算への利用有無	Boolean
			PartDeleteFlag        : false,      // 臓器の削除フラグ（臓器引き算用）	Boolean
			PartPath              : null        // JSONへのパス	文字列
		};
	},

	parseURL : function(str){
		var jsonObj = null;
		var decode_str;
		try{
			decode_str = decodeURIComponent(str);
		}catch(e){
//			console.error(e);
//			console.log(str);
			decode_str = str;
//			return null;
		}
//		_dump('AgURLParser.parseURL():decode_str=['+decode_str+']');
		try{jsonObj = Ext.JSON.decode(decode_str,true);}catch(e){}
//		_dump('AgURLParser.parseURL():jsonObj=['+jsonObj+']');
//		console.log(jsonObj);
		if(!jsonObj){
			var urlObj = Ext.Object.fromQueryString(decode_str);
			if(urlObj){
				var Window = AgURLParser.parseWindow(urlObj);
				var Part = AgURLParser.parsePart(urlObj);
				if(Window || Part){

					var Common = AgURLParser.parseCommon(urlObj);
					var Camera = AgURLParser.parseCamera(urlObj);
					var Legend = AgURLParser.parseLegend(urlObj);
					var Pin = AgURLParser.parsePin(urlObj);

					jsonObj = {};
					if(Common) jsonObj['Common'] = Common;
					if(Window) jsonObj['Window'] = Window;
					if(Camera) jsonObj['Camera'] = Camera;
					if(Legend) jsonObj['Legend'] = Legend;
					if(Pin)    jsonObj['Pin'] = Pin;
					if(Part)   jsonObj['Part'] = Part;
				}
			}
		}
//		_dump('AgURLParser.parseURL():jsonObj=['+jsonObj+']');
		return jsonObj;
	}
};
