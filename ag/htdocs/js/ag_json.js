var bitsAnatomoJSON = {

//“Common”:{			ハッシュ	
// “Model”:	“bp3d”	モデル	文字列	
// “Version”:	“”	バージョン	文字列	
// “AnatomogramVersion”:	“20110318”	アナトモグラム形式のバージョン	文字列	
// “ScalarMaximum”:	65535	Scalar Maximum	整数	
// “ScalarMinimum”:	-65535	Scalar Minimum	整数	
// “ColorbarFlag”:	false	カラーバーの描画フラグ	Boolean	
// “ScalarColorFlag”:	false	臓器描画にScalarColorを利用するフラグ	Boolean	
// “TreeName”:	“bp3d”	利用するTree名	文字列	
// “DateTime”:	“yyyymmddhhmmss”	現在時刻	文字列	
// “CoordinateSystemName”:	“bp3d”	描画座標系	文字列	
// “CopyrightType”:	“”	コピーライト画像のサイズ（未指定、large、midium、small）	文字列	
_convAgPrmURL2JSONCommon : function (aParamObj){
	var rtnObj = {
		'Model' : 'bp3d',
		'AnatomogramVersion' : '20110318',
		'Version' : 'latest'
	};
	if(aParamObj.av){
//		prm.Common.AnatomogramVersion = paramObj.av;
		delete aParamObj.av;
	}

//アナトモグラム形式のバージョン
	if(aParamObj.av){
//		prm.Common.AnatomogramVersion = paramObj.av;
		delete aParamObj.av;
	}

	return rtnObj;
},

convAgPrmURL2JSON : function (aParam){
try{
	var paramObj = Ext.urlDecode(aParam);

	var prm = {
		Common : {
			'Model' : 'bp3d',
			'AnatomogramVersion' : '20110318'
		},
		Window : {},
		Camera : {}
	};


// Common Parameters
	if(paramObj.av){
//		prm.Common.AnatomogramVersion = paramObj.av;
		delete paramObj.av;
	}

//	prm = prm + "&iw=" + prm_record.data.image_w;
	if(paramObj.iw){
//		prm.Common.AnatomogramVersion = paramObj.av;
		delete paramObj.iw;
	}
	prm = prm + "&ih=" + prm_record.data.image_h;
	prm = prm + "&bcl=" + prm_record.data.bg_rgb;
	if(!isNaN(prm_record.data.bg_transparent)) prm = prm + "&bga=0";

	if (isNaN(prm_record.data.scalar_max)) {
	} else {
		prm = prm + "&sx=" + prm_record.data.scalar_max;
	}
	if (isNaN(prm_record.data.scalar_min)) {
	} else {
		prm = prm + "&sn=" + prm_record.data.scalar_min;
	}
	if (prm_record.data.colorbar_f) {
		prm = prm + "&cf=" + prm_record.data.colorbar_f;
	}
	// Bodyparts Version
	var bp3d_tree_group_value = init_tree_group;
	var bp3d_tree_group = Ext.getCmp('anatomo-tree-group-combo');
	if(bp3d_tree_group && bp3d_tree_group.rendered){
		bp3d_tree_group_value = bp3d_tree_group.getValue();
	}

	var bp3d_version_value = init_bp3d_version;
	var bp3d_version = Ext.getCmp('anatomo-version-combo');
	if(bp3d_version && bp3d_version.rendered){
		bp3d_version_value = bp3d_version.getValue();
	}
//_dump("makeAnatomoPrm():bp3d_version_value=["+bp3d_version_value+"]");
	prm = prm + "&bv=" + bp3d_version_value;
//_dump("makeAnatomoPrm():bp3d_tree_group_value=["+bp3d_tree_group_value+"]");

	var bp3d_type_value = '0';
	var bp3d_type = Ext.getCmp('bp3d-tree-type-combo');
	if(bp3d_type && bp3d_type.rendered){
		bp3d_type_value = bp3d_type.getValue();
	}
//_dump("makeAnatomoPrm():bp3d_type_value=["+bp3d_type_value+"]");
	if(bp3d_type_value=='3' || bp3d_type_value=='is_a'){
		bp3d_type_value = 'isa';
	}else if(bp3d_type_value=='4' || bp3d_type_value=='part_of'){
		bp3d_type_value = 'partof';
	}else{
		bp3d_type_value = 'conventional';
	}
	prm = prm + "&tn=" + bp3d_type_value;
//_dump("makeAnatomoPrm():tn=["+bp3d_type_value+"]");

	// Date
	prm = prm + "&dt=" + getDateString();

	// Draw Legend Flag
	var drawCheck = Ext.getCmp('anatomography_image_comment_draw_check');
	if(drawCheck && drawCheck.rendered && drawCheck.getValue()){
		prm = prm + "&dl=1";
	}
	// Draw Pin Description Flag
	var drawCheck = Ext.getCmp('anatomo_pin_description_draw_check');
	if(drawCheck && drawCheck.rendered && drawCheck.getValue()){
		prm = prm + "&dp=1";
	}

	// Camera Parameters

	prm = prm + "&cx=" + roundPrm(m_ag_cameraPos.x);
	prm = prm + "&cy=" + truncationPrm(m_ag_cameraPos.y);
	prm = prm + "&cz=" + roundPrm(m_ag_cameraPos.z);
	prm = prm + "&tx=" + roundPrm(m_ag_targetPos.x);
	prm = prm + "&ty=" + truncationPrm(m_ag_targetPos.y);
	prm = prm + "&tz=" + roundPrm(m_ag_targetPos.z);
	prm = prm + "&ux=" + roundPrm(m_ag_upVec.x);
	prm = prm + "&uy=" + roundPrm(m_ag_upVec.y);
	prm = prm + "&uz=" + roundPrm(m_ag_upVec.z);
	prm = prm + "&zm=" + prm_record.data.zoom;

	var rotateAuto = false;
	try{rotateAuto = Ext.getCmp('ag-command-image-controls-rotateAuto').getValue();}catch(e){}
	if(rotateAuto){
		prm = prm + "&orax=" + roundPrm(agRotateAuto.rotAxis.x);
		prm = prm + "&oray=" + roundPrm(agRotateAuto.rotAxis.y);
		prm = prm + "&oraz=" + roundPrm(agRotateAuto.rotAxis.z);
		prm = prm + "&orcx=" + roundPrm(m_ag_targetPos.x);
		prm = prm + "&orcy=" + truncationPrm(m_ag_targetPos.y);
		prm = prm + "&orcz=" + roundPrm(m_ag_targetPos.z);
		prm = prm + "&ordg=" + agRotateAuto.angle;
		prm = prm + "&autorotate=" + agRotateAuto.dt_time;
	}

	if(!_glb_no_clip){
		// Clip Parameters
		prm = prm + "&cm=" + prm_record.data.clip_type;
		if(prm_record.data.clip_type == 'N'){
		}else{

			var clip;
			try{clip = Ext.getCmp('anatomo-clip-predifined-plane').getValue();}catch(e){clip = undefined;}
			if(clip && clip == 'FREE'){
				prm = prm + "&cd="  + (isNaN(prm_record.data.clip_depth)?'NaN':prm_record.data.clip_depth);
				prm = prm + "&cpa=" + (isNaN(prm_record.data.clip_paramA)?'NaN':roundPrm(prm_record.data.clip_paramA));
				prm = prm + "&cpb=" + (isNaN(prm_record.data.clip_paramB)?'NaN':roundPrm(prm_record.data.clip_paramB));
				prm = prm + "&cpc=" + (isNaN(prm_record.data.clip_paramC)?'NaN':roundPrm(prm_record.data.clip_paramC));
				prm = prm + "&cpd=" + (isNaN(prm_record.data.clip_paramD)?'NaN':roundPrm(prm_record.data.clip_paramD));
				prm = prm + "&ct=" + prm_record.data.clip_method;
			}else{
				prm = prm + "&cd=0";
				prm = prm + "&cpa=" + (isNaN(prm_record.data.clip_paramA)?'NaN':roundPrm(prm_record.data.clip_paramA));
				prm = prm + "&cpb=" + (isNaN(prm_record.data.clip_paramB)?'NaN':roundPrm(prm_record.data.clip_paramB));
				prm = prm + "&cpc=" + (isNaN(prm_record.data.clip_paramC)?'NaN':roundPrm(prm_record.data.clip_paramC));
				prm = prm + "&cpd=" + (isNaN(prm_record.data.clip_depth)?'NaN':prm_record.data.clip_depth);
				prm = prm + "&ct=" + prm_record.data.clip_method;
			}
		}
	}

	// Organ Parameters
	if (ag_parts_store && ag_parts_store.getCount() > 0) {

		var onum = 1;
		var pnum = 1;
		var num;

		for (var i = 0; i < ag_parts_store.getCount(); i++) {
			var record = ag_parts_store.getAt(i);
			if (!record || !record.data || (!record.data.f_id && !record.data.name_e)) return;

			if(!Ext.isEmpty(aOpacity) && !isNaN(parseFloat(aOpacity)) && parseFloat(aOpacity) > record.data.opacity) continue; //指定されたaOpacityより小さい値は除外

			if(!Ext.isEmpty(aMode) && aMode == 2){	//保存モード

				if(isPointDataRecord(record)){
					if(!record.data.f_id) continue;
					num = makeAnatomoOrganNumber(pnum);
					prm = prm + "&poid" + num + "=" + record.data.f_id;
					prm = prm + makeAnatomoOrganPointPrm(num,record);
					prm = prm + "&polb" + num + "=" + record.data.point_label;
					pnum++;
					continue;
				}else{
					num = makeAnatomoOrganNumber(onum);
					if(record.data.f_id){
						prm = prm + "&oid" + num + "=" + record.data.f_id;
					}else if(record.data.name_e){
						prm = prm + "&onm" + num + "=" + record.data.name_e;
					}else{
						continue;
					}
					if(record.data.version) prm = prm + "&ov" + num + "=" + record.data.version;
					prm = prm + makeAnatomoOrganPrm(num,record);
					onum++;
					continue;
				}
			}

			if(record.data.tg_id == bp3d_tree_group_value){
				if(isPointDataRecord(record)){
					if(!record.data.f_id) continue;
					if(!Ext.isEmpty(prm_record.data.point_label) && record.data.point_label != prm_record.data.point_label) continue;
					num = makeAnatomoOrganNumber(pnum);
					prm = prm + "&poid" + num + "=" + record.data.f_id;
					prm = prm + makeAnatomoOrganPointPrm(num,record);
					pnum++;
					continue;
				}else{
					num = makeAnatomoOrganNumber(onum);
					if(record.data.f_id){
						prm = prm + "&oid" + num + "=" + record.data.f_id;
					}else if(record.data.name_e){
						prm = prm + "&onm" + num + "=" + record.data.name_e;
					}else{
						continue;
					}
					prm = prm + makeAnatomoOrganPrm(num,record);
					onum++;
					continue;
				}
			}else{
				if(Ext.isEmpty(aMode)){	//通常モード
					if(record.data.conv_id){
						var id_arr = record.data.conv_id.split(",");
						for(var ocnt=0;ocnt<id_arr.length;ocnt++){
							if(isPointDataRecord(record)){
								if(!Ext.isEmpty(prm_record.data.point_label) && record.data.point_label != prm_record.data.point_label) continue;
								num = makeAnatomoOrganNumber(pnum);
								prm = prm + "&poid" + num + "=" + id_arr[ocnt];
								prm = prm + makeAnatomoOrganPointPrm(num,record);
								pnum++;
							}else{
								num = makeAnatomoOrganNumber(onum);
								prm = prm + "&oid" + num + "=" + id_arr[ocnt];
								prm = prm + makeAnatomoOrganPrm(num,record);
								onum++;
							}
						}
					}else{
						if(isPointDataRecord(record)){
							if(!Ext.isEmpty(prm_record.data.point_label) && record.data.point_label != prm_record.data.point_label) continue;
							num = makeAnatomoOrganNumber(pnum);
							prm = prm + "&poid" + num + "=" + record.data.f_id;
							prm = prm + makeAnatomoOrganPointPrm(num,record);
							pnum++;
						}else{
							num = makeAnatomoOrganNumber(onum);
							prm = prm + "&onm" + num + "=" + record.data.name_e;
							prm = prm + makeAnatomoOrganPrm(num,record);
							onum++;
						}
					}
				}else{	//Linkモード
					if(isPointDataRecord(record)){
						if(!Ext.isEmpty(prm_record.data.point_label) && record.data.point_label != prm_record.data.point_label) continue;
						num = makeAnatomoOrganNumber(pnum);
						prm = prm + "&poid" + num + "=" + record.data.f_id;
						prm = prm + makeAnatomoOrganPointPrm(num,record);
						pnum++;
					}else{
						num = makeAnatomoOrganNumber(onum);
						prm = prm + "&oid" + num + "=" + record.data.f_id;
						if(record.data.version) prm = prm + "&ov" + num + "=" + record.data.version;
						prm = prm + makeAnatomoOrganPrm(num,record);
						onum++;
					}
				}
			}
		}

		//Palletに存在しないパーツがピックされた場合
		if(glb_point_f_id){
			var num = makeAnatomoOrganNumber(onum);
			prm = prm + "&oid" + num + "=" + glb_point_f_id;
			prm = prm + "&ocl" + num + "=" + glb_point_color;
			glb_point_f_id = null;
			onum++;
		}

		if(onum>1){
//dpl	0,1,2	ピンからPin Descriptionへの線描画指定(0：ピンからDescriptionへの線描画無し、1：ピンの先端からDescriptionへの線描画、2：ピンの終端からDescriptionへの線描画）。Descriptionが描画されていないと線も描画しない。
//dpod	0,1	点構造のDescription
//dpol	0,1,2	点からPoint Descriptionへの線描画指定(0：点からDescriptionへの線描画無し、1：点の先端からDescriptionへの線描画、2：点の終端からDescriptionへの線描画）。Descriptionが描画されていないと線も描画しない。
			prm = prm + "&dpl="+prm_record.data.point_pin_line;
			prm = prm + "&dpod="+prm_record.data.point_desc;
			prm = prm + "&dpol="+prm_record.data.point_point_line;
		}
	}

	// Legend Parameters
	var drawCheck = Ext.getCmp('anatomography_image_comment_draw_check');
	if (drawCheck && drawCheck.rendered && drawCheck.getValue()) {
		prm = prm + "&lp=UL";
		prm = prm + "&lc=646464";
	}

//	prm = prm + "&lt=" + encodeURIComponent(Ext.getCmp("anatomography_image_comment_title").getValue());
	var cmp = Ext.getCmp("anatomography_image_comment_title");
	if(cmp && cmp.rendered){
		var value = encodeURIComponent(cmp.getValue());
		if(value != '') prm = prm + "&lt=" + value;
	}

//	prm = prm + "&le=" + encodeURIComponent(Ext.getCmp("anatomography_image_comment_legend").getValue());
	var cmp = Ext.getCmp("anatomography_image_comment_legend");
	if(cmp && cmp.rendered){
		var value = encodeURIComponent(cmp.getValue());
		if(value != '') prm = prm + "&le=" + value;
	}

//	prm = prm + "&la=" + encodeURIComponent(Ext.getCmp("anatomography_image_comment_author").getValue());
	var cmp = Ext.getCmp("anatomography_image_comment_author");
	if(cmp && cmp.rendered){
		var value = encodeURIComponent(cmp.getValue());
		if(value != '') prm = prm + "&la=" + value;
	}

	//Grid
	if (prm_record.data.grid && prm_record.data.grid=='1') {
		prm = prm + "&gdr=true";
		prm = prm + "&gcl="+prm_record.data.grid_color;
		prm = prm + "&gtc="+prm_record.data.grid_len;
	}

	var anatomo_pin_shape_combo_value;
	try{
		anatomo_pin_shape_combo_value = Ext.getCmp("anatomo_pin_shape_combo").getValue();
	}catch(e){
		anatomo_pin_shape_combo_value = init_anatomo_pin_shape;
	}

	// color_rgb (Default parts color)
	if(!Ext.isEmpty(aMode) && aMode == 2){	//保存モード
		prm = prm + "&fcl="+prm_record.data.color_rgb;
	}

	//coordinate_system
	var coordinate_system;
	try{
		coordinate_system = Ext.getCmp("ag-coordinate-system-combo").getValue();
	}catch(e){
		coordinate_system = prm_record.data.coord;
	}
	prm = prm + "&crd="+coordinate_system;

	// Pin Parameters
	if (ag_comment_store && ag_comment_store.getCount() > 0) {
		for (var i = 0; i < ag_comment_store.getCount(); i++) {
			var record = ag_comment_store.getAt(i);
			if (!record || !record.data) return;
			var num = i+1;
			while ((num+"").length < 3) {
				num = "0" + num;
			}
			// No
			prm = prm + "&pno" + num + "=" + parseInt(record.data.no).toString();
			// 3Dx
			prm = prm + "&px" + num + "=" + roundPrm(record.data.x3d);
			// 3Dy
			prm = prm + "&py" + num + "=" + roundPrm(record.data.y3d);
			// 3Dz
			prm = prm + "&pz" + num + "=" + roundPrm(record.data.z3d);
			// ArrVec3Dx
			prm = prm + "&pax" + num + "=" + roundPrm(record.data.avx3d);
			// ArrVec3Dy
			prm = prm + "&pay" + num + "=" + roundPrm(record.data.avy3d);
			// ArrVec3Dz
			prm = prm + "&paz" + num + "=" + roundPrm(record.data.avz3d);
			// UpVec3Dx
			prm = prm + "&pux" + num + "=" + roundPrm(record.data.uvx3d);
			// UpVec3Dy
			prm = prm + "&puy" + num + "=" + roundPrm(record.data.uvy3d);
			// UpVec3Dz
			prm = prm + "&puz" + num + "=" + roundPrm(record.data.uvz3d);
			// Draw Pin Description
			var drawCheck = Ext.getCmp('anatomo_pin_description_draw_check');
			if (drawCheck && drawCheck.rendered && drawCheck.getValue()) {
				prm = prm + "&pdd" + num + "=1";
				prm = prm + "&pdc" + num + "=" + record.data.color;
			}
			// Point Shape
			prm = prm + "&ps" + num + "=" + anatomo_pin_shape_combo_value;
			// ForeRGB
			prm = prm + "&pcl" + num + "=" + record.data.color;
			// OrganID
			prm = prm + "&poi" + num + "=" + encodeURIComponent(record.data.oid);
			// OrganName
			prm = prm + "&pon" + num + "=" + encodeURIComponent(record.data.organ);
			// Comment
			prm = prm + "&pd" + num + "=" + encodeURIComponent(record.data.comment);

			//coordinate_system
			if(!Ext.isEmpty(record.data.coord)) prm = prm + "&pcd" + num + "=" + encodeURIComponent(record.data.coord);
		}
	}

	return prm;
	}catch(e){
		_dump("makeAnatomoPrm():"+e);
	}
}

};
