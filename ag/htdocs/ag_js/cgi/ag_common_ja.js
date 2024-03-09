// /bp3d/ag-in-service/htdocs/ag_common_js.cgiより自動生成
var gCOMMON_TPAP;
var gSelNode = null;

var model2tg;
var tg2model;
var version2tg;
var latestversion;
var cgipath = {"calcRotAxis":"API/calcRotAxis","focusClip":"API/focusClip","globalPin":{"pin":{"auth":"API/globalpin/pin/auth","search":"API/globalpin/pin/search","adding":"API/globalpin/pin/post","get":"API/globalpin/pin/get","delete":"API/globalpin/pin/remove","update":"API/globalpin/pin/update","getlist":"API/globalpin/pin/getlist"},"group":{"link":"API/globalpin/group/link","getattr":"API/globalpin/group/getattr","search":"API/globalpin/group/search","getlist":"API/globalpin/group/getlist","auth":"API/globalpin/group/auth","unlink":"API/globalpin/group/unlink","adding":"API/globalpin/group/post","delete":"API/globalpin/group/remove","get":"API/globalpin/group/get","update":"API/globalpin/group/update"}},"pick":"API/pick","focus":"API/focus","print":"API/print","image":"API/image","pointSearch":"API/pointSearch","map":"API/map","clip":"API/clip","point":"API/point","animation":"API/animation"};
var glb_us_state = {};
var glb_us_keymap = [];
//glb_us_keymap.length = 0;
if(glb_us_keymap.length==0){
	glb_us_keymap = [
	{
		'order': 2,
		'key'  : 'F9',
		'code' : Ext.EventObject.F9,
		'stop' : true,
		'cmd'  : 'ag-command-menu-image-move-focus-center'
	},{
		'order': 3,
		'key'  : 'F10',
		'code' : Ext.EventObject.F10,
		'stop' : true,
		'cmd'  : 'ag-command-menu-image-move-focus-zoom'
	},{
		'order': 4,
		'key'  : 'UP',
		'code' : Ext.EventObject.UP,
		'shift': true,
		'stop' : true,
		'cmd'  : 'ag-command-menu-image-move-up'
	},{
		'order': 5,
		'key'  : 'DOWN',
		'code' : Ext.EventObject.DOWN,
		'shift': true,
		'stop' : true,
		'cmd'  : 'ag-command-menu-image-move-down'
	},{
		'order': 6,
		'key'  : 'LEFT',
		'code' : Ext.EventObject.LEFT,
		'shift': true,
		'stop' : true,
		'cmd'  : 'ag-command-menu-image-move-left'
	},{
		'order': 7,
		'key'  : 'RIGHT',
		'code' : Ext.EventObject.RIGHT,
		'shift': true,
		'stop' : true,
		'cmd'  : 'ag-command-menu-image-move-right'
	},{
		'order': 8,
		'key'  : 'UP',
		'code' : Ext.EventObject.UP,
		'ctrl' : true,
		'stop' : true,
		'cmd'  : 'ag-command-menu-image-rotation-up'
	},{
		'order': 9,
		'key'  : 'DOWN',
		'code' : Ext.EventObject.DOWN,
		'ctrl' : true,
		'stop' : true,
		'cmd'  : 'ag-command-menu-image-rotation-down'
	},{
		'order': 10,
		'key'  : 'LEFT',
		'code' : Ext.EventObject.LEFT,
		'ctrl' : true,
		'stop' : true,
		'cmd'  : 'ag-command-menu-image-rotation-left'
	},{
		'order': 11,
		'key'  : 'RIGHT',
		'code' : Ext.EventObject.RIGHT,
		'ctrl' : true,
		'stop' : true,
		'cmd'  : 'ag-command-menu-image-rotation-right'
	},{
		'order': 12,
		'key'  : 'UP',
		'code' : Ext.EventObject.UP,
		'alt'  : true,
		'stop' : true,
		'cmd'  : 'ag-command-menu-image-zoom-up'
	},{
		'order': 13,
		'key'  : 'DOWN',
		'code' : Ext.EventObject.DOWN,
		'alt'  : true,
		'stop' : true,
		'cmd'  : 'ag-command-menu-image-zoom-down'
	}];
	for(var i=0;i<glb_us_keymap.length;i++){
		glb_us_keymap[i].order = i+1;
	}
}

var ag_parts_store;
var ag_param_store_fields = ['version', 'method', 'viewpoint', 'rotate_h', 'rotate_v', 'image_w', 'image_h', 'bg_rgb', 'bg_transparent', 'autoscalar_f', 'scalar_max', 'scalar_min', 'colorbar_f', 'heatmap_f', 'drawsort_f', 'mov_len', 'mov_fps', 'zoom', 'move_x', 'move_y', 'move_z', 'clip_type', 'clip_depth', 'clip_paramA', 'clip_paramB', 'clip_paramC', 'clip_paramD', 'clip_method', 'clipped_cameraX', 'clipped_cameraY', 'clipped_cameraZ', 'clipped_targetX', 'clipped_targetY', 'clipped_targetZ', 'clipped_upVecX', 'clipped_upVecY', 'clipped_upVecZ', 'grid', 'grid_len', 'grid_color', 'color_rgb', 'coord', 'point_color_rgb', 'point_label', 'point_desc', 'point_pin_line', 'point_point_line', 'point_sphere'];
var ag_param_store_data = [
	'09011601',	// version
	'I',				// method
	'C',				// viewpoint
	0,					// rotate_h
	0,					// rotate_v
	400,				// image_w
	400,				// image_h
	'FFFFFF',		// bg_rgb
	NaN,				// bg_transparent
	'1',				// autoscalar_f
	NaN,				// scalar_max
	NaN,				// scalar_min
	'0',				// colorbar_f
	'0',				// heatmap_f
	'0',				// drawsort_f
	60,					// mov_len
	60,					// mov_fps
	0,					// zoom
	0,					// move_x
	0,					// move_y
	0,					// move_z
	'N',				// clip_type
	NaN,				// clip_depth
	NaN,				// clip_paramA
	NaN,				// clip_paramB
	NaN,				// clip_paramC
	NaN,				// clip_paramD
	'NS',				// clip_method
	0,					// clipped_cameraX
	0,					// clipped_cameraY
	0,					// clipped_cameraZ
	0,					// clipped_targetX
	0,					// clipped_targetY
	0,					// clipped_targetZ
	0,					// clipped_upVecX
	0,					// clipped_upVecY
	0,					// clipped_upVecZ
	'0',				// grid
	10,					// grid_len
	'008000',		// grid_color
	'f0d2a0',		// color_rgb
	'bp3d',			// coordinate_system
	'0000ff',		// point_color_rgb
	'FMA',			// point_label
	1,					// point_desc
	0,					// point_pin_line
	0,					// point_point_line
	'SM'				//point_sphere
];
var ag_param_store = new Ext.data.SimpleStore ({
	fields : ag_param_store_fields,
	data : [ag_param_store_data]
});
var anatomoImgDrag = false;
var anatomoImgDragStartX = 0;
var anatomoImgDragStartY = 0;
var anatomoPickMode = false;
var anatomoPointMode = false;
var anatomoImgEvent = false;
var anatomoMoveMode = false;
var anatomoClipDepthMode = false;
var anatomoDragModeMove = false;
var anatomoUpdateZoomValue = false;
var anatomoUpdateClipValue = false;

var DEF_ZOOM_MAX = 100;

var YRangeFromServer = null;
var glb_rotateH = 0;
var glb_rotateV = 0;
var glb_zoom_slider = 1;
var glb_zoom_timer = null;
var glb_zoom_xy = null;
var glb_zoom_delta = 0;
var glb_mousedown_timer = null;
var glb_mousedown_toggle = false;

//Pick時にパーツのＩＤを設定される
var glb_point_f_id = null;
var glb_point_color = 'FF0000';
var glb_point_pallet_index = null;
var glb_point_transactionId = null;

function remove_point_f_id(store,record,index){
//	if(record.get('f_id')==glb_point_f_id || store.getCount()==0) clear_point_f_id();
	clear_point_f_id();
}
function set_point_f_id(f_id){
	if(Ext.isEmpty(f_id)){
		clear_point_f_id();
	}else{
		glb_point_f_id = f_id;
		ag_parts_gridpanel.getStore().on('update',remove_point_f_id);
		ag_parts_gridpanel.getStore().on('remove',remove_point_f_id);
	}
}
function get_point_f_id(){
	return glb_point_f_id;
}
function clear_point_f_id(){
	if(glb_point_f_id){
		glb_point_f_id = null;
		_loadAnatomo(makeAnatomoPrm(),true);
	}
	ag_parts_gridpanel.getStore().un('update',remove_point_f_id);
	ag_parts_gridpanel.getStore().un('remove',remove_point_f_id);
}


function set_point_color(color){
	glb_point_color = color;
}
function get_point_color(){
	return glb_point_color;
}

var init_bp3d_params = {};
//var init_bp3d_md_id;
//var init_bp3d_mv_id;
//var init_bp3d_mr_id;

var init_tree_group;
var init_bp3d_version;

//PIN関連の初期値
var init_anatomo_pin_number_draw = true;
//var init_anatomo_pin_description_draw = false;
var init_anatomo_pin_description_draw = true;
var init_anatomo_pin_description_line = 0;
//var init_anatomo_pin_shape = 'SC';
var init_anatomo_pin_shape = 'PL';

var init_anatomography_image_comment_draw = false;
var init_anatomography_image_comment_title = '';
var init_anatomography_image_comment_legend = '';
var init_anatomography_image_comment_author = '';

//_dump("init_tree_group=["+init_tree_group+"]");
//_dump("init_bp3d_version=["+init_bp3d_version+"]");

var _glb_no_clip = false;

var glb_anatomo_image_url = '';
var glb_anatomo_image_still = '';
var glb_anatomo_image_rotate = '';
var glb_anatomo_editor_url = '';
//var glb_anatomo_embedded_url = '';

var glb_transactionId = null;
var glb_time = null;

var m_ag = {
	initCameraPos: new AGVec3d(2.7979888916016167, -998.4280435445771, 809.7306805551052),
	cameraPos: new AGVec3d(2.7979888916016167, -998.4280435445771, 809.7306805551052),
	initTargetPos: new AGVec3d(2.7979888916015625, -110.37168800830841, 809.7306805551052),
	targetPos: new AGVec3d(2.7979888916015625, -110.37168800830841, 809.7306805551052),
	initUpVec: new AGVec3d(0, 0, 1),
	upVec: new AGVec3d(0, 0, 1),
	initDistance: 0,
	distance: 0,
	initLongitude: 0,
	longitude: 0,
	initLatitude: 0,
	latitude: 0,
	orthoYRange: 1800,
	initOrthoYRange: 1800,
	nearClip: 1,
	farClip: 10000,
	epsilon: 0.0000001,
	PI: 3.141592653589793238462643383279,
	Camera_YRange_Min: 1.0
};


var  timeoutAnatomoID = null;
function stopUpdateAnatomo(){
	if(timeoutAnatomoID) clearTimeout(timeoutAnatomoID);
	timeoutAnatomoID=null;
}

function updateAnatomo () {
//	console.log("updateAnatomo()");
	if(Ext.isEmpty(gParams.tp_md) || gParams.tp_md != 1){
		var contentsPanel = Ext.getCmp("contents-tab-panel");
		if (!contentsPanel) {
			return;
		}
		var activePanel;
		if(contentsPanel.getXType()=='tabpanel'){
			activePanel = contentsPanel.getActiveTab();
		}else if(contentsPanel.getXType()=='panel'){
			activePanel = contentsPanel.getLayout().activeItem;
		}
		if (!activePanel || !activePanel.id || (activePanel.id != "contents-tab-anatomography-panel")) {
			return;
		}
	}
	stopUpdateAnatomo();
	timeoutAnatomoID = setTimeout(function(){ _updateAnatomo();stopUpdateAnatomo(); },100);
}

var  _timeoutAnatomoID = null;

function _loadAnatomo (params,loadMask) {
//	console.log("_loadAnatomo()");
	if(loadMask){
		try{
			var comp = Ext.getCmp('anatomography-image');
			if(Ext.isEmpty(comp.loadMask)) comp.loadMask = new Ext.LoadMask(comp.body,{removeMask:false,  msg:'REDRAWING...'});
			comp.loadMask.show();
		}catch(e){_dump(e);}
	}

	var jsonStr = null;
	try{
		jsonStr = ag_extensions.toJSON.URI2JSON(params,{
			toString:true,
			mapPin:false,
			callback:undefined
		});
	}catch(e){jsonStr = null;}

	glb_time = (new Date()).getTime();

	var img = Ext.getDom('ag_img');

	var href = '';
	if(location.href.match(/^(.+\/)/)){
		href = RegExp.$1;
	}
	href += cgipath.image + "?" + (jsonStr ? encodeURIComponent(jsonStr) : params);
	if(href.length<=2083){
		img.src = cgipath.image+"?" + (jsonStr ? encodeURIComponent(jsonStr) : params);
	}else{
		var params_obj = Ext.urlDecode(params);
		if(!Ext.isEmpty(glb_transactionId)){
//			console.log("_loadAnatomo():abort()");
//			console.log(glb_transactionId);
//			console.log("Ext.Ajax.abort():["+Ext.Ajax.isLoading(glb_transactionId)+"]");
			if(Ext.Ajax.isLoading(glb_transactionId)) Ext.Ajax.abort(glb_transactionId);
		}
		glb_transactionId = Ext.Ajax.request({
			url     : cgipath.image,
			method  : 'POST',
			params  : jsonStr ? jsonStr : params,
			success : function(conn,response,options){
				glb_transactionId = null;
				try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
				try{
					var src;
					if(results && results.data){
						if(params_obj.dt != results.dt) return;
						src = results.data;
					}else{
						src = conn.responseText;
					}
					if(src && src != img.src){
						img.src = src;
					}else{
						load_ag_img();
					}
				}catch(e){
					alert(e);
				}
//				console.log("_loadAnatomo():success()");
			},
			failure : function(conn,response,options){
				glb_transactionId = null;
				try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
				var msg = '[';
				if(results && results.msg){
					msg += results.msg+' ]';
				}else{
					msg += conn.status+" "+conn.statusText+' ]';
				}
				var rotateAuto = false;
				try{rotateAuto = Ext.getCmp('ag-command-image-controls-rotateAuto').getValue();}catch(e){}
				if(conn.status==400) img.src = Ext.BLANK_IMAGE_URL;
//				console.log("_loadAnatomo():failure():"+msg);
//				console.log(conn);
//				console.log(response);
//				console.log(options);
				Ext.Msg.show({
					title:' ',
					buttons: Ext.Msg.OK,
					closable: false,
					icon: Ext.Msg.ERROR,
					modal : true,
					msg : msg
				});
			},
			callback : function(options,success,response){
//				console.log("_loadAnatomo():callback()");
//				console.log(options);
//				console.log(success);
//				console.log(response);
			}
		});
//		console.log("_loadAnatomo():exec()");
//		console.log(glb_transactionId);
	}
}

function setImageTransformOrigin(aOrigin){
//_dump("setImageTransformOrigin():["+aOrigin+"]");
	if(Ext.isGecko){

		var img_org = Ext.getDom('ag_img');
		var img = Ext.getDom('ag_img_dummy');
		if(!img && img_org){
			img = img_org.ownerDocument.createElement('img');
			img.setAttribute('id','ag_img_dummy');
			img.style.position = 'absolute';
			img.style.display = 'none';
			img_org.parentNode.appendChild(img);
		}

		if(img){
			img.style.left = '0px';
			img.style.top = '0px';
			img.style.width = img_org.offsetWidth + 'px';
			img.style.height = img_org.offsetHeight + 'px';
			img.src = img_org.src;
			img.style.opacity = '1.0';

			img.style.MozTransformOrigin = aOrigin;
			img.style.webkitTransformOrigin = aOrigin;
			img.style.transformOrigin = aOrigin;

		}

	}else if(Ext.isChrome || Ext.isSafari){
		var img = Ext.getDom('ag_img');
		if(img){
			img.style.webkitTransformOrigin = aOrigin;
			img.style.transformOrigin = aOrigin;
		}
	}
}

function setImageTransform(aTransform,aDisplay){
//_dump("setImageTransform():["+aTransform+"]["+aDisplay+"]");
	if(Ext.isGecko){

		if(!aDisplay) aDisplay = false;
		var img_org = Ext.getDom('ag_img');
		var img = Ext.getDom('ag_img_dummy');
		if(!img && img_org){
			img = img_org.ownerDocument.createElement('img');
			img.setAttribute('id','ag_img_dummy');
			img.style.position = 'absolute';
			img_org.parentNode.appendChild(img);
		}

		if(img){
			img.style.left = '0px';
			img.style.top = '0px';
			img.style.width = img_org.offsetWidth + 'px';
			img.style.height = img_org.offsetHeight + 'px';
			img.src = img_org.src;
			img.style.opacity = '1.0';
			img.style.display = aDisplay ? '' : 'none';

			img.style.MozTransform = aTransform;
			img.style.webkitTransform = aTransform;
			img.style.transform = aTransform;

			if(img_org){
				if(aDisplay){
					img_org.style.opacity = '0.0';
				}else{
					img_org.style.opacity = '1.0';
				}
			}
		}

	}else if(Ext.isChrome || Ext.isSafari){
		var img = Ext.getDom('ag_img');
		if(img){
			img.style.webkitTransform = aTransform;
			img.style.transform = aTransform;
		}
	}
}

function anatomoImgMouseWheel(e,t) {
//_dump("anatomoImgMouseWheel():"+t.id);
	if(!t || (t.id!='ag_img' && t.id!='ag_img_dummy')) return;
	try {
		e.stopPropagation();
		e.preventDefault();
	} catch (ex) {
		e.returnValue = false;
		e.cancelBubble = true;
	}


	try{
		var delta = e.getWheelDelta();
		if(delta){
			if(anatomoClipDepthMode){
				var slider = Ext.getCmp('anatomo-clip-slider');
				if(slider && slider.rendered) slider.setValue(slider.getValue() + delta);
			}else{
				var slider = Ext.getCmp('zoom-slider');
				if(slider && slider.rendered){
					glb_zoom_delta += delta;
					if(Math.abs(Math.round(glb_zoom_delta))>=1){

						var slider_value = slider.getValue();
						if(slider_value+glb_zoom_delta>=0 && slider_value+glb_zoom_delta<DEF_ZOOM_MAX){
							var val;
							if(Ext.isGecko){
								val = (Math.round(glb_zoom_delta) / 10);
								if(val>=0){
									val += (val*0.5);
								}else{
									val += (val*0.3);
								}
								val += 1;
							}else if(Ext.isChrome || Ext.isSafari){
								val = (Math.round(glb_zoom_delta) / 10);
								val += 1;
//_dump("anatomoImgMouseWheel():val=["+val+"]");
							}
							var elemImg = Ext.get('ag_img');
							var xyImg = elemImg.getXY();
							var sizeImg = elemImg.getSize();
							var mouseX = e.xy[0] - glbImgXY[0];
							var mouseY = e.xy[1] - glbImgXY[1];

//_dump("anatomoImgMouseWheel():e.xy=["+e.xy[0]+"]["+e.xy[1]+"]["+xyImg[0]+"]["+xyImg[1]+"]["+elemImg.getLeft()+"]["+elemImg.getLeft(true)+"]["+sizeImg.width+"]["+sizeImg.height+"]");

							setImageTransformOrigin(mouseX+'px '+mouseY+'px');
							setImageTransform('scale('+val+')',true);

//_dump("anatomoImgMouseWheel():slider.getValue()=["+slider.getValue()+"]");
							if(glb_zoom_timer) clearTimeout(glb_zoom_timer);
							glb_zoom_timer = setTimeout(function(){
								glb_zoom_xy = [];
								glb_zoom_xy[0] = e.xy[0];
								glb_zoom_xy[1] = e.xy[1];
								slider.setValue(slider.getValue() + glb_zoom_delta);
								glb_zoom_delta = 0;
								glb_zoom_timer = null;
							},500);
						}
					}
				}else{
					if(Math.round(glb_zoom_slider + glb_zoom_delta + delta)>=0){
						glb_zoom_delta += delta;
						glb_zoom_slider = glb_zoom_slider + glb_zoom_delta;

						glb_zoom_xy = [];
						glb_zoom_xy[0] = e.xy[0];
						glb_zoom_xy[1] = e.xy[1];

						if(glb_zoom_xy){
							var elemImg = Ext.get('ag_img');
							var xyImg = elemImg.getXY();

							var mouseX = glb_zoom_xy[0] - xyImg[0];
							var mouseY = glb_zoom_xy[1] - xyImg[1];

							var centerX = parseInt((ag_param_store.getAt(0).data.image_w /2) -  mouseX);
							var centerY = parseInt((ag_param_store.getAt(0).data.image_h /2) -  mouseY);

							setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);
							moveTargetByMouseForOrtho(ag_param_store.getAt(0).data.image_h, centerX / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)), centerY / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)));
						}

						var prm_record = ag_param_store.getAt(0);
						prm_record.beginEdit();
						prm_record.set('zoom', glb_zoom_slider / 5);
						prm_record.endEdit();
						prm_record.commit();

						if(glb_zoom_xy){

							var elemImg = Ext.get('ag_img');
							var xyImg = elemImg.getXY();

							var mouseX = glb_zoom_xy[0] - xyImg[0];
							var mouseY = glb_zoom_xy[1] - xyImg[1];

							var moveX = parseInt(mouseX - (ag_param_store.getAt(0).data.image_w /2));
							var moveY = parseInt(mouseY - (ag_param_store.getAt(0).data.image_h /2));

							setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);
							moveTargetByMouseForOrtho(ag_param_store.getAt(0).data.image_h, moveX / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)), moveY / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)));

						}
						updateAnatomo();
						updateClipImage();

						if(glb_zoom_xy) glb_zoom_xy = null;
						glb_zoom_delta = 0;
					}
				}
			}
		}
		e.stopEvent();
	}catch(e){
		_dump("anatomoImgMouseWheel():"+e);
	}
}

function anatomoIsPickMode () {
	return anatomoPickMode;
}

function anatomoIsPointMode () {
	return anatomoPointMode;
}

function anatomoImgMouseOut(e) {
}

function anatomoImgMouseDown(e,t) {
//_dump("anatomoImgMouseDown():"+t.id);
_dump("anatomoImgMouseDown():e.button=["+e.button+"]:e.which=["+e.which+"]:e.ctrlKey=["+e.ctrlKey+"]");
	if(!t || t.id!='ag_img') return;
//	if(e.button == 2) return;
	if(e.button != 0) return;
	try {
		e.stopPropagation();
		e.preventDefault();
	} catch (ex) {
		e.returnValue = false;
		e.cancelBubble = true;
	}
	anatomoImgDrag = true;
	anatomoImgDragStartX = e.xy[0];
	anatomoImgDragStartY = e.xy[1];
	if(e.ctrlKey || e.button == 1){
		anatomoMoveMode = true;
	} else {
		anatomoMoveMode = false;
	}
_dump("anatomoImgMouseDown():anatomoImgDrag=["+anatomoImgDrag+"]:anatomoMoveMode=["+anatomoMoveMode+"]");

	if(anatomoImgDrag){
		var rotateAuto = false;
		try{rotateAuto = Ext.getCmp('ag-command-image-controls-rotateAuto').getValue();}catch(e){}
		if(rotateAuto){
		}
	}

	if(anatomoDragModeMove){
		document.body.style.cursor = 'move';
	}else{
		document.body.style.cursor = 'default';
	}
	if(glb_mousedown_timer) clearTimeout(glb_mousedown_timer);
	if(e.button == 0){
		glb_mousedown_timer = setTimeout(function(){
			glb_mousedown_timer = null;

			if(anatomoDragModeMove){
				document.body.style.cursor = 'move';
			}else{
				document.body.style.cursor = 'default';
			}
			glb_mousedown_toggle = true;

			var target = (anatomoDragModeMove?Ext.get('ag-command-btn-rotate'):Ext.get('ag-command-btn-move'));
			if(!target) return;
			ag_command_toggle_exec(target);
//		},400);
		},1000); //2011-09-07
	}
}

function anatomoImgMouseMove(e) {

	if(glb_mousedown_timer){
		clearTimeout(glb_mousedown_timer);
		glb_mousedown_timer = null;
	}

	if (anatomoImgDrag) {
		try {
			e.stopPropagation();
			e.preventDefault();
		} catch (ex) {
			e.returnValue = false;
			e.cancelBubble = true;
		}
		var rotateAuto = false;
		try{rotateAuto = Ext.getCmp('ag-command-image-controls-rotateAuto').getValue();}catch(e){}
		if(rotateAuto) return;
		var dX = e.xy[0] - anatomoImgDragStartX;
		var dY = e.xy[1] - anatomoImgDragStartY;
		if(anatomoMoveMode || anatomoDragModeMove) {
			document.body.style.cursor = 'move';
			var rotImgDiv = Ext.getDom("rotImgDiv");
			rotImgDiv.style.visibility = "hidden";

			setImageTransform('scale(1) translate(' + dX + 'px, ' + dY + 'px)',true);

		}else{

			var prm_record = ag_param_store.getAt(0);
			deg = (isNaN(prm_record.data.rotate_h))?0:prm_record.data.rotate_h;


			document.body.style.cursor = 'default';
			// rotateH
			var degH = Math.round(getRotateHorizontalValue()/15)*15;
			degH = degH - 15 * Math.floor(dX / 20);
			while (degH >= 360) {
				degH = degH - 360;
			}
			while (degH < 0) {
				degH = degH + 360;
			}
			// rotateV
			var degV = Math.round(getRotateVerticalValue()/15)*15;
			degV = degV + 15 * Math.floor(dY / 20);
			while (degV >= 360) {
				degV = degV - 360;
			}
			while (degV < 0) {
				degV = degV + 360;
			}

			degH = degH.toString();
			degV = degV.toString();

			var rotateHSpan = Ext.getDom("rotImgDivRotateH");
			if(rotateHSpan){
				rotateHSpan.innerHTML = "H:"+degH;
			}

			var rotateVSpan = Ext.getDom("rotImgDivRotateV");
			if(rotateVSpan){
				rotateVSpan.innerHTML = "V:"+degV;
			}

			var rotImgDiv = Ext.getDom("rotImgDiv");
			rotImgDiv.style.visibility = "visible";
			rotImgDiv.style.left = (parseInt(e.xy[0]) + 10) + "px";
			rotImgDiv.style.top = (parseInt(e.xy[1]) + 10) + "px";
			rotImgDiv.style.backgroundPosition = degH /15 * (-80) + "px " + degV / 15 * (-80) + "px";
		}
	}
}

function anatomoImgMouseUp(e) {
	if(glb_mousedown_timer){
		clearTimeout(glb_mousedown_timer);
		glb_mousedown_timer = null;
	}

	document.body.style.cursor = 'default';

	var dX = e.xy[0] - anatomoImgDragStartX;
	var dY = e.xy[1] - anatomoImgDragStartY;

	var bp3d_home_group_btn_disabled = true;
	try{bp3d_home_group_btn_disabled = Ext.getCmp('bp3d-home-group-btn').disabled;}catch(e){}

	if(bp3d_home_group_btn_disabled && anatomoIsPickMode() && !dX && !dY){
		var imgX = 0;
		var imgY = 0;
		if (e.browserEvent.offsetX) {
			// IE
			imgX = e.browserEvent.offsetX;
			imgY = e.browserEvent.offsetY;
		} else {
			// FF
			var img = Ext.getDom('ag_img');
			imgX = e.browserEvent.layerX - img.offsetLeft;
			imgY = e.browserEvent.layerY - img.offsetTop;
		}
		try {
			Ext.getCmp('anatomography-pin-grid-panel').loadMask.show();
			var params = Ext.urlDecode(makeAnatomoPrm(null,1),true);
			params.px = imgX;
			params.py = imgY;

			var jsonStr = null;
			try{
				jsonStr = ag_extensions.toJSON.URI2JSON(params,{
					toString:true,
					mapPin:false,
					callback:undefined
				});
			}catch(e){jsonStr = null;}

			var urlStr = cgipath.pick;
			Ext.Ajax.request({
				url     : urlStr,
				method  : 'POST',
				params  : jsonStr ? jsonStr : params,
				success : function (response, options) {
					try{
						var pickDataAry = [];
						var obj = Ext.util.JSON.decode(response.responseText);
//_dump(cgipath.pick+":success():obj=["+(typeof obj)+"]");
						pickDataAry = obj.Pin;
//_dump(cgipath.pick+":success():pickDataAry=["+(typeof pickDataAry)+"]");
						var pickDepth = parseInt(Ext.getCmp('anatomo_comment_pick_depth').getValue());
						var pin_no = ag_comment_store.getCount();
						var newRecord = Ext.data.Record.create(ag_comment_store_fields);
						var addrecs = [];
						for (var i=0;i<pickDataAry.length;i++){
							if(i == pickDepth) break;
							var pickData = pickDataAry[i];
//_dump(cgipath.pick+":success():pickData.PinPartID=["+(typeof pickData.PinPartID)+"]["+(pickData.PinPartID)+"]");
							if(pickData.PinPartID.match(/^clipPlaneRect_(.+)$/)) pickData.PinPartID = RegExp.$1;
							var addrec = new newRecord({
								no:   ++pin_no,
								oid:   pickData.PinPartID,
								organ: pickData.PinPartName,
								x3d:   pickData.PinX,
								y3d:   pickData.PinY,
								z3d:   pickData.PinZ,
								avx3d: pickData.PinArrowVectorX,
								avy3d: pickData.PinArrowVectorY,
								avz3d: pickData.PinArrowVectorZ,
								uvx3d: pickData.PinUpVectorX,
								uvy3d: pickData.PinUpVectorY,
								uvz3d: pickData.PinUpVectorZ,
								color: '0000FF',
								comment:'',
								coord: pickData.PinCoordinateSystemName
							});
/*
							addrec.beginEdit();
							addrec.set("no",   ++pin_no);
							addrec.set("oid",   pickData.PinPartID);
							addrec.set("organ", '');
							addrec.set("x3d",   pickData.PinX);
							addrec.set("y3d",   pickData.PinY);
							addrec.set("z3d",   pickData.PinZ);
							addrec.set("avx3d", pickData.PinArrowVectorX);
							addrec.set("avy3d", pickData.PinArrowVectorY);
							addrec.set("avz3d", pickData.PinArrowVectorZ);
							addrec.set("uvx3d", pickData.PinUpVectorX);
							addrec.set("uvy3d", pickData.PinUpVectorY);
							addrec.set("uvz3d", pickData.PinUpVectorZ);
							addrec.set("color", '0000FF');
							addrec.set("comment",'');
							addrec.set("coord", pickData.PinCoordinateSystemName);
							addrec.commit(true);
							addrec.endEdit();
*/
							addrecs.push(addrec);

						}
						if(addrecs.length>0){
							ag_comment_store.add(addrecs);
						}else{
							if(window.ag_extensions && window.ag_extensions.pick_point) window.ag_extensions.pick_point.hide();
						}

					}catch(e){_dump(e);}
					Ext.getCmp('anatomography-pin-grid-panel').loadMask.hide();
				},
				failure: function (response, options) {
					alert(cgipath.pick+":failure():"+response.statusText);
					Ext.getCmp('anatomography-pin-grid-panel').loadMask.hide();
				}
			});
		} catch (ex) {
			alert(ex.toString());
		}
	}

	//Pick or Pallet タブがアクティブの場合
	if(
		!anatomoIsPickMode() && !dX && !dY && Ext.getCmp('anatomo_comment_point_button') &&
		ag_comment_tabpanel && ag_comment_tabpanel.rendered &&

		(
			(
				window.ag_extensions &&
				window.ag_extensions.pallet_element &&
				(ag_comment_tabpanel.getActiveTab().id == window.ag_extensions.pallet_element.getId() || ag_comment_tabpanel.getActiveTab().id == 'anatomography-point-grid-panel' || ag_comment_tabpanel.getActiveTab().id == 'ag-parts-gridpanel')
			)
			||
			(
				(!window.ag_extensions || !window.ag_extensions.pallet_element) &&
				(ag_comment_tabpanel.getActiveTab().id == 'anatomography-point-grid-panel' || ag_comment_tabpanel.getActiveTab().id == 'ag-parts-gridpanel')
			)
		)
	) {


		if(ag_comment_tabpanel.getActiveTab().id == 'ag-parts-gridpanel'){
			if(window.ag_extensions && window.ag_extensions.pallet_element){
				window.ag_extensions.pallet_element.setActiveTab();
			}else{
				ag_comment_tabpanel.setActiveTab('anatomography-point-grid-panel');
			}
		}
		Ext.getCmp('anatomo_comment_point_button').toggle(false);
		Ext.getCmp('anatomo_comment_point_button').disable();
		var imgX = 0;
		var imgY = 0;
		if (e.browserEvent.offsetX) {
			// IE
			imgX = e.browserEvent.offsetX;
			imgY = e.browserEvent.offsetY;
		} else {
			// FF
			var img = Ext.getDom('ag_img');
			imgX = e.browserEvent.layerX - img.offsetLeft;
			imgY = e.browserEvent.layerY - img.offsetTop;
		}
		try {
			if(window.ag_extensions && window.ag_extensions.pallet_element){
				if(ag_comment_tabpanel.getActiveTab().id == window.ag_extensions.pallet_element.getId()) window.ag_extensions.pallet_element.showLoadMask();
			}
			if(ag_comment_tabpanel.getActiveTab().id == 'anatomography-point-grid-panel') Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.show();

			Ext.getCmp('ag-parts-gridpanel').loadMask.show();
			var urlStr = cgipath.point;
			var params = Ext.urlDecode(makeAnatomoPrm(null,1),true);
			params.px = imgX;
			params.py = imgY;

			var jsonStr = null;
			try{
				jsonStr = ag_extensions.toJSON.URI2JSON(params,{
					toString:true,
					mapPin:false,
					callback:undefined
				});
			}catch(e){jsonStr = null;}

			if(glb_point_transactionId){
				Ext.Ajax.abort(glb_point_transactionId);
			}

			glb_point_transactionId = Ext.Ajax.request({
				url    : urlStr,
				method : 'POST',
				params : jsonStr ? jsonStr : params,
				callback: function(options,success,response){
					glb_point_transactionId = null;
				},
				success: function (response, options) {
//					_dump(cgipath.point+":success():"+response.responseText);
//					_dump(cgipath.point+":success():"+ag_comment_tabpanel.getActiveTab().id);
					try{var pointData = Ext.util.JSON.decode(response.responseText);}catch(e){_dump(e);}
					if(Ext.isEmpty(pointData) || Ext.isEmpty(pointData.id)){
						Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.hide();
						Ext.getCmp('ag-parts-gridpanel').loadMask.hide();
						clear_point_f_id();
						var loader = Ext.getCmp('anatomography-point-editorgrid-panel').getStore();
						loader.removeAll();
						loader.baseParams = {};
						var elem = Ext.getDom('ag-point-grid-content-route');
						if(elem) elem.innerHTML = '&nbsp;';

						if(window.ag_extensions){
							if(window.ag_extensions.pallet_element){
								window.ag_extensions.pallet_element.hideLoadMask();
								window.ag_extensions.pallet_element.selectPointElement(null);
							}
							if(window.ag_extensions.pick_point) window.ag_extensions.pick_point.hide();
						}
						return;
					}

					var f_id = pointData.id;
					try{
						var tx = parseInt(parseFloat(pointData.worldPosX)*1000)/1000;
						var ty = parseInt(parseFloat(pointData.worldPosY)*1000)/1000;
						var tz = parseInt(parseFloat(pointData.worldPosZ)*1000)/1000;

						var txCmp = Ext.getCmp('anatomography-point-grid-bbar-tx-text');
						var tyCmp = Ext.getCmp('anatomography-point-grid-bbar-ty-text');
						var tzCmp = Ext.getCmp('anatomography-point-grid-bbar-tz-text');
						var dxCmp = Ext.getCmp('ag-point-grid-footer-content-distance-x-text');
						var dyCmp = Ext.getCmp('ag-point-grid-footer-content-distance-y-text');
						var dzCmp = Ext.getCmp('ag-point-grid-footer-content-distance-z-text');
						var distanceCmp = Ext.getCmp('anatomography-point-grid-bbar-distance-text');

						var txP = txCmp.getValue();txP=(txP==''?'':parseFloat(txP));
						var tyP = tyCmp.getValue();tyP=(tyP==''?0:parseFloat(tyP));
						var tzP = tzCmp.getValue();tzP=(txP==''?0:parseFloat(tzP));

						if(!isNaN(tx)){
							txCmp.setValue(tx);
							tyCmp.setValue(ty);
							tzCmp.setValue(tz);
						}

						if(!isNaN(tx) && txP != ''){
							dxCmp.setValue(parseInt(parseFloat(txP-tx)*1000)/1000);
							dyCmp.setValue(parseInt(parseFloat(tyP-ty)*1000)/1000);
							dzCmp.setValue(parseInt(parseFloat(tzP-tz)*1000)/1000);

							var distance = parseInt(Math.sqrt(Math.pow(tx-txP,2)+Math.pow(ty-tyP,2)+Math.pow(tz-tzP,2))*1000)/1000;
							distanceCmp.setValue(distance);
						}else{
							dxCmp.setValue('');
							dyCmp.setValue('');
							dzCmp.setValue('');
							distanceCmp.setValue('');
						}

					}catch(e){}

					if(f_id.match(/^clipPlaneRect_(.+)$/)){
						f_id = RegExp.$1;
					}else if(f_id != ""){

					}else{
						Ext.getCmp('anatomo_comment_point_button').enable();

						var loader = Ext.getCmp('anatomography-point-editorgrid-panel').getStore();
						loader.removeAll();
						loader.baseParams = {};
						var elem = Ext.getDom('ag-point-grid-content-route');
						if(elem) elem.innerHTML = '&nbsp;';
						Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.hide();
						Ext.getCmp('ag-parts-gridpanel').loadMask.hide();
						if(window.ag_extensions){
							if(window.ag_extensions.pallet_element){
								window.ag_extensions.pallet_element.hideLoadMask();
								window.ag_extensions.pallet_element.selectPointElement(null);
							}
							if(window.ag_extensions.pick_point) window.ag_extensions.pick_point.hide();
						}
						return;
					}

					if(window.ag_extensions && window.ag_extensions.pallet_element) window.ag_extensions.pallet_element.selectPointElement(f_id);
					if(get_point_f_id() == f_id){
						Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.hide();
						Ext.getCmp('ag-parts-gridpanel').loadMask.hide();
						if(window.ag_extensions){
							if(window.ag_extensions.pallet_element) window.ag_extensions.pallet_element.hideLoadMask();
							if(window.ag_extensions.pick_point) window.ag_extensions.pick_point.hide();
						}
						return;
					}
					var loader = Ext.getCmp('anatomography-point-editorgrid-panel').getStore();
					loader.removeAll();
					loader.baseParams = {};
					var elem = Ext.getDom('ag-point-grid-content-route');
					if(elem) elem.innerHTML = '&nbsp;';


					if(get_point_f_id() != f_id){
						set_point_f_id(f_id);
						var params = makeAnatomoPrm();
						_loadAnatomo(params,true);
					}
					if(ag_comment_tabpanel.getActiveTab().id == 'anatomography-point-grid-panel'){

						var point_loader = null;
						var pallet_loader = null;

						point_loader = anatomography_point_conventional_root_store;
						var toggle_partof = Ext.getCmp('anatomo_comment_point_toggle_partof');
						if(toggle_partof && toggle_partof.rendered) toggle_partof.toggle(true);

						var cmp = Ext.getCmp('anatomo-tree-type-combo');
						if(cmp && cmp.rendered){
							var type = cmp.getValue();
							if(toggle_partof.pressed){
								if(type == '4'){
									point_loader = anatomography_point_partof_store;
								}else if(type == '3'){
									point_loader = anatomography_point_isa_store;
								}else if(type == '1'){
									point_loader = anatomography_point_conventional_root_store;
								}
							}else if(Ext.getCmp('anatomo_comment_point_toggle_haspart').pressed){
								if(type == '4'){
									point_loader = anatomography_point_haspart_store;
								}else if(type == '3'){
									point_loader = anatomography_point_hasmember_store;
								}else if(type == '1'){
									point_loader = anatomography_point_conventional_child_store;
								}
							}
						}
						pallet_loader = anatomography_pallet_point_conventional_root_store;
						var cmp = Ext.getCmp('bp3d-tree-type-combo-ag');
						if(cmp && cmp.rendered){
							var type = cmp.getValue();
							if(type == '4'){
								pallet_loader = anatomography_pallet_point_partof_store;
							}else if(type == '3'){
								pallet_loader = anatomography_pallet_point_isa_store;
							}else if(type == '1'){
								pallet_loader = anatomography_pallet_point_conventional_root_store;
							}
						}
						if(point_loader || pallet_loader){
							if(point_loader){
								point_loader.baseParams = point_loader.baseParams || {};
								point_loader.baseParams.f_id = f_id;
								point_loader.load();
							}
							if(pallet_loader){
								pallet_loader.baseParams = pallet_loader.baseParams || {};
								pallet_loader.baseParams.f_id = f_id;
								pallet_loader.load();
							}
						}else{
							var loader = Ext.getCmp('anatomography-point-editorgrid-panel').getStore();
							loader.removeAll();
							loader.baseParams = {};
							var elem = Ext.getDom('ag-point-grid-content-route');
							if(elem) elem.innerHTML = '&nbsp;';
							Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.hide();
							Ext.getCmp('ag-parts-gridpanel').loadMask.hide();
							if(window.ag_extensions){
								if(window.ag_extensions.pallet_element) window.ag_extensions.pallet_element.hideLoadMask();
								if(window.ag_extensions.pick_point) window.ag_extensions.pick_point.hide();
							}
						}
					}else{
						Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.hide();
						Ext.getCmp('ag-parts-gridpanel').loadMask.hide();
						if(window.ag_extensions){
							if(window.ag_extensions.pallet_element) window.ag_extensions.pallet_element.hideLoadMask();
							if(window.ag_extensions.pick_point) window.ag_extensions.pick_point.hide();
						}
					}
					Ext.getCmp('anatomo_comment_point_button').enable();
				},
				failure: function (response, options) {
					try{alert(cgipath.point+":failure():"+response.status+":"+response.statusText);}catch(e){}
					Ext.getCmp('anatomo_comment_point_button').enable();
					Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.hide();
					Ext.getCmp('ag-parts-gridpanel').loadMask.hide();
					if(window.ag_extensions){
						if(window.ag_extensions.pallet_element) window.ag_extensions.pallet_element.hideLoadMask();
						if(window.ag_extensions.pick_point) window.ag_extensions.pick_point.hide();
					}
				}
			});
		} catch (ex) {
			alert(ex.toString());
			Ext.getCmp('anatomo_comment_point_button').enable();
		}
	}


	//Point Search タブがアクティブの場合
	if(
		!anatomoIsPickMode() && !dX && !dY && Ext.getCmp('anatomo_comment_point_button') &&
		ag_comment_tabpanel && ag_comment_tabpanel.rendered &&
		(ag_comment_tabpanel.getActiveTab().id == 'anatomography-point-search-panel')
	) {
		var imgX = 0;
		var imgY = 0;
		if (e.browserEvent.offsetX) {
			// IE
			imgX = e.browserEvent.offsetX;
			imgY = e.browserEvent.offsetY;
		} else {
			// FF
			var img = Ext.getDom('ag_img');
			imgX = e.browserEvent.layerX - img.offsetLeft;
			imgY = e.browserEvent.layerY - img.offsetTop;
		}
		point_search(imgX,imgY);
	}


//	_dump("anatomoImgMouseUp():anatomoImgDrag=["+anatomoImgDrag+"]");

	if(anatomoImgDrag){
		try {
			e.stopPropagation();
			e.preventDefault();
		} catch (ex) {
			e.returnValue = false;
			e.cancelBubble = true;
		}
		var rotImgDiv = Ext.getDom("rotImgDiv");
		rotImgDiv.style.visibility = "hidden";
		anatomoImgDrag = false;

//		_dump("anatomoImgMouseUp():dX=["+dX+"]");
//		_dump("anatomoImgMouseUp():dY=["+dY+"]");

		if(dX || dY){

//			_dump("anatomoImgMouseUp():anatomoMoveMode=["+anatomoMoveMode+"]");
//			_dump("anatomoImgMouseUp():anatomoDragModeMove=["+anatomoDragModeMove+"]");

			if(anatomoMoveMode || anatomoDragModeMove){

				// calc camera target
				setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);
				moveTargetByMouseForOrtho(ag_param_store.getAt(0).data.image_h, dX / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)), dY / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)));

			} else {


				var rotateAuto = false;
				try{rotateAuto = Ext.getCmp('ag-command-image-controls-rotateAuto').getValue();}catch(e){}
//				_dump("anatomoImgMouseUp():rotateAuto=["+rotateAuto+"]");
				if(rotateAuto){
				}else{

					// rotateH
					var deg = getRotateHorizontalValue();
					deg = deg - 15 * Math.floor(dX / 20);
					while (deg >= 360) {
						deg = deg - 360;
					}
					while (deg < 0) {
						deg = deg + 360;
					}
					setRotateHorizontalValue(deg);

					// rotateV
					var deg = getRotateVerticalValue();
					deg = deg + 15 * Math.floor(dY / 20);
					while (deg >= 360) {
						deg = deg - 360;
					}
					while (deg < 0) {
						deg = deg + 360;
					}
					setRotateVerticalValue(deg);

					if(Ext.isEmpty(gParams.tp_md) || gParams.tp_md != 1){
						if(updateRotateImg) updateRotateImg();
					}

					// calc camera target
					setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);
					addLongitude(-15 * Math.floor(dX / 20));
					addLatitude(15 * Math.floor(dY / 20));

				}

			}
			updateAnatomo();
		}
	}

	if(glb_mousedown_toggle){
		if(anatomoDragModeMove){
			ag_command_toggle_exec(Ext.get('ag-command-btn-rotate'));
		}else{
			ag_command_toggle_exec(Ext.get('ag-command-btn-move'));
		}
		document.body.style.cursor = 'default';
		glb_mousedown_toggle = false;
	}
	anatomoMoveMode = false;
}


function makeAnatomoOrganPrm(num,record,mode,aOpacity){
	var prm = "";

	if(get_point_f_id() && (Ext.isEmpty(mode) || mode!=2) && get_point_f_id() == record.data.f_id){
		prm = prm + "&ocl" + num + "=" + glb_point_color;
	}else{
		// color
		var colorstr = record.data.color.substr(1, 6);
		if(colorstr.length == 6) prm = prm + "&ocl" + num + "=" + colorstr;
	}

	// value
	if (isNaN(parseFloat(record.data.value))) {
	} else {
		prm = prm + "&osc" + num + "=" + parseFloat(record.data.value);
	}

	// Show
	if (record.data.exclude || (!Ext.isEmpty(aOpacity) && !isNaN(parseFloat(aOpacity)) && parseFloat(aOpacity) > record.data.opacity)) {
		prm = prm + "&osz" + num + "=H";
	}else if (record.data.zoom) {
		prm = prm + "&osz" + num + "=Z";
	}else{
		prm = prm + "&osz" + num + "=S";
	}
	// Opacity
//	if(record.data.opacity==0.1){
//		prm = prm + "&oop" + num + "=0.05";
//	}else{
		prm = prm + "&oop" + num + "=" + record.data.opacity;
//	}
	// representation
	if (record.data.representation == "surface") {
		prm = prm + "&orp" + num + "=S";
	} else if (record.data.representation == "wireframe") {
		prm = prm + "&orp" + num + "=W";
	} else if (record.data.representation == "points") {
		prm = prm + "&orp" + num + "=P";
	}

	//Organ Draw Child Point Flag
	prm = prm + "&odcp" + num + "=" + (record.data.point?1:0);

	return prm;
}



function makeAnatomoPrm(aMode,aOpacity){
	try{

	var prm = "";
	var prm_record = ag_param_store.getAt(0);

	// General Parameters
	var version = "09051901";
	prm = "av=" + version;
	if(!Ext.isEmpty(gParams.tp_md) && gParams.tp_md == 1){
		var size = Ext.getBody().getSize();
		prm = prm + "&iw=" + size.width;
		prm = prm + "&ih=" + size.height;
	}else{
		prm = prm + "&iw=" + prm_record.data.image_w;
		prm = prm + "&ih=" + prm_record.data.image_h;
	}
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
	if (prm_record.data.heatmap_f) {
		prm = prm + "&hf=" + prm_record.data.heatmap_f;
	}
	// Bodyparts Version
	var bp3d_tree_group_value = init_tree_group;
	var bp3d_tree_group = Ext.getCmp('anatomo-tree-group-combo');
	if(bp3d_tree_group && bp3d_tree_group.rendered) bp3d_tree_group_value = bp3d_tree_group.getValue();
	prm = prm + "&model=" + encodeURIComponent(tg2model[bp3d_tree_group_value].tg_model);

//	if(!Ext.isEmpty(gParams.tp_md) && gParams.tp_md == 1){
//		console.log(gCOMMON_TPAP);
//	}

	var bp3d_version_value;
	var bp3d_version = Ext.getCmp('anatomo-version-combo');
	if(bp3d_version && bp3d_version.rendered){
		bp3d_version_value = bp3d_version.getValue();
	}
//_dump("makeAnatomoPrm(1):bp3d_version_value=["+bp3d_version_value+"]");
	if(!Ext.isEmpty(gParams.tp_md) && gParams.tp_md == 1){
		if(Ext.isEmpty(bp3d_version_value) && gCOMMON_TPAP) bp3d_version_value = gCOMMON_TPAP.bv;
	}
//_dump("makeAnatomoPrm(2):bp3d_version_value=["+bp3d_version_value+"]");
	if(Ext.isEmpty(bp3d_version_value)) bp3d_version_value = init_bp3d_version;

	prm = prm + "&bv=" + bp3d_version_value;

//_dump("makeAnatomoPrm(3):bp3d_version_value=["+bp3d_version_value+"]");
//_dump("makeAnatomoPrm():bp3d_tree_group_value=["+bp3d_tree_group_value+"]");

	var bp3d_type_value;
	var bp3d_type = Ext.getCmp('bp3d-tree-type-combo');
	if(bp3d_type && bp3d_type.rendered){
		bp3d_type_value = bp3d_type.getValue();
		if(!Ext.isEmpty(bp3d_type_value)){
			if(bp3d_type_value=='3' || bp3d_type_value=='is_a'){
				bp3d_type_value = 'isa';
			}else if(bp3d_type_value=='4' || bp3d_type_value=='part_of'){
				bp3d_type_value = 'partof';
			}else{
//				bp3d_type_value = 'conventional';
			}
		}
	}
	if(!Ext.isEmpty(gParams.tp_md) && gParams.tp_md == 1){
		if(Ext.isEmpty(bp3d_type_value) && gCOMMON_TPAP) bp3d_type_value = gCOMMON_TPAP.tn;
	}
	if(Ext.isEmpty(bp3d_type_value)) bp3d_type_value = 'isa';

	prm = prm + "&tn=" + bp3d_type_value;

//_dump("makeAnatomoPrm():bp3d_type_value=["+bp3d_type_value+"]");
//_dump("makeAnatomoPrm():tn=["+bp3d_type_value+"]");

	// Date
	prm = prm + "&dt=" + getDateString();

	// Draw Legend Flag
	var drawCheck = Ext.getCmp('anatomography_image_comment_draw_check');
	if(drawCheck && drawCheck.rendered){
		if(drawCheck.getValue()) prm = prm + "&dl=1";
	}else if(init_anatomography_image_comment_draw){
		prm = prm + "&dl=1";
	}
	// Draw Pin Number Flag
	var drawCheck = Ext.getCmp('anatomo_pin_number_draw_check');
	if(drawCheck && drawCheck.rendered){
		if(!drawCheck.getValue()) prm = prm + "&np=0";
	}else if(!init_anatomo_pin_number_draw){
		prm = prm + "&np=0";
	}
	// Draw Pin Description Flag
	var drawCheck = Ext.getCmp('anatomo_pin_description_draw_check');
	if(drawCheck && drawCheck.rendered){
		if(drawCheck.getValue()) prm = prm + "&dp=1";
	}else if(init_anatomo_pin_description_draw){
		prm = prm + "&dp=1";
	}

	// Camera Parameters
	// 何れかの値が不正な場合
	if(isNaN(m_ag.cameraPos.x) || isNaN(m_ag.cameraPos.y) || isNaN(m_ag.cameraPos.z) ||
		 isNaN(m_ag.targetPos.x) || isNaN(m_ag.targetPos.y) || isNaN(m_ag.targetPos.z) ||
		 isNaN(m_ag.upVec.x) || isNaN(m_ag.upVec.y) || isNaN(m_ag.upVec.z)){
		if(isNaN(m_ag.cameraPos.x) || isNaN(m_ag.cameraPos.y) || isNaN(m_ag.cameraPos.z)) m_ag.cameraPos = new AGVec3d(2.7979888916016167, -998.4280435445771, 809.7306805551052);
		if(isNaN(m_ag.targetPos.x) || isNaN(m_ag.targetPos.y) || isNaN(m_ag.targetPos.z)) m_ag.targetPos = new AGVec3d(2.7979888916015625, -110.37168800830841, 809.7306805551052);
		if(isNaN(m_ag.upVec.x) || isNaN(m_ag.upVec.y) || isNaN(m_ag.upVec.z)) m_ag.upVec = new AGVec3d(0, 0, 1);
		setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);
		var deg = calcRotateDeg();
		setRotateHorizontalValue(deg.H);
		setRotateVerticalValue(deg.V);

		if(updateRotateImg) updateRotateImg();
	}

	prm = prm + "&cx=" + roundPrm(m_ag.cameraPos.x);
	prm = prm + "&cy=" + truncationPrm(m_ag.cameraPos.y);
	prm = prm + "&cz=" + roundPrm(m_ag.cameraPos.z);
	prm = prm + "&tx=" + roundPrm(m_ag.targetPos.x);
	prm = prm + "&ty=" + truncationPrm(m_ag.targetPos.y);
	prm = prm + "&tz=" + roundPrm(m_ag.targetPos.z);
	prm = prm + "&ux=" + roundPrm(m_ag.upVec.x);
	prm = prm + "&uy=" + roundPrm(m_ag.upVec.y);
	prm = prm + "&uz=" + roundPrm(m_ag.upVec.z);
	prm = prm + "&zm=" + prm_record.data.zoom;
//_dump("prm_record.data.zoom=["+prm_record.data.zoom+"]");
	var rotateAuto = false;
	try{rotateAuto = Ext.getCmp('ag-command-image-controls-rotateAuto').getValue();}catch(e){}
	if(rotateAuto){
		var orax = roundPrm(agRotateAuto.rotAxis.x);
		var oray = roundPrm(agRotateAuto.rotAxis.y);
		var oraz = roundPrm(agRotateAuto.rotAxis.z);
		var orcx = roundPrm(m_ag.targetPos.x);
		var orcy = truncationPrm(m_ag.targetPos.y);
		var orcz = roundPrm(m_ag.targetPos.z);
		if(isNaN(orax) || isNaN(oray) || isNaN(oraz) || isNaN(orcx) || isNaN(orcy) || isNaN(orcz)){
			try{Ext.getCmp('ag-command-image-controls-rotateAuto').setValue(false);}catch(e){}
			Ext.MessageBox.show({
				title   : 'Auto rotation',
				msg     : 'Value of the coordinate calculation is incorrect.',
				buttons : Ext.MessageBox.OK,
				icon    : Ext.MessageBox.ERROR
			});
		}else{
			prm = prm + "&orax=" + orax;
			prm = prm + "&oray=" + oray;
			prm = prm + "&oraz=" + oraz;
			prm = prm + "&orcx=" + orcx;
			prm = prm + "&orcy=" + orcy;
			prm = prm + "&orcz=" + orcz;
			prm = prm + "&ordg=" + agRotateAuto.angle;
			prm = prm + "&autorotate=" + agRotateAuto.dt_time;
		}
	}

	if(!_glb_no_clip){
		// Clip Parameters
		prm = prm + "&cm=" + prm_record.data.clip_type;
		if(prm_record.data.clip_type == 'N'){
		}else{

			var clip;
			try{clip = Ext.getCmp('anatomo-clip-predifined-plane').getValue();}catch(e){clip = undefined;}
//			if(!clip || clip == 'FREE'){
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

			if(!Ext.isEmpty(aMode) && aMode == 2){	//保存モード

				if(isPointDataRecord(record)){
					if(!record.data.f_id) continue;
					num = makeAnatomoOrganNumber(pnum);
					prm = prm + "&poid" + num + "=" + record.data.f_id;
					prm = prm + makeAnatomoOrganPointPrm(num,record);
					prm = prm + "&polb" + num + "=" + record.data.point_label;
					pnum++;
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
					prm = prm + makeAnatomoOrganPrm(num,record,aMode,aOpacity);
					onum++;
				}
				continue;
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
					prm = prm + makeAnatomoOrganPrm(num,record,undefined,aOpacity);
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
								prm = prm + makeAnatomoOrganPrm(num,record,undefined,aOpacity);
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
							prm = prm + makeAnatomoOrganPrm(num,record,undefined,aOpacity);
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
						prm = prm + makeAnatomoOrganPrm(num,record,undefined,aOpacity);
						onum++;
					}
				}
			}
		}

		if(get_point_f_id() && (Ext.isEmpty(aMode) || aMode != 2)){	//保存モード
			//Palletに存在しないパーツがピックされた場合
			var num = makeAnatomoOrganNumber(onum);
			prm = prm + "&oid" + num + "=" + get_point_f_id();
			prm = prm + "&ocl" + num + "=" + glb_point_color;
			onum++;
		}

//		if(onum>1){
//dpl	0,1,2	ピンからPin Descriptionへの線描画指定(0：ピンからDescriptionへの線描画無し、1：ピンの先端からDescriptionへの線描画、2：ピンの終端からDescriptionへの線描画）。Descriptionが描画されていないと線も描画しない。
//dpod	0,1	点構造のDescription
//dpol	0,1,2	点からPoint Descriptionへの線描画指定(0：点からDescriptionへの線描画無し、1：点の先端からDescriptionへの線描画、2：点の終端からDescriptionへの線描画）。Descriptionが描画されていないと線も描画しない。
//			prm = prm + "&dpl="+prm_record.data.point_pin_line;
//			prm = prm + "&dpod="+prm_record.data.point_desc;
//			prm = prm + "&dpol="+prm_record.data.point_point_line;
//		}
	}
	//dpl	0,1,2	ピンからPin Descriptionへの線描画指定(0：ピンからDescriptionへの線描画無し、1：ピンの先端からDescriptionへの線描画、2：ピンの終端からDescriptionへの線描画）。Descriptionが描画されていないと線も描画しない。
	prm = prm + "&dpl="+prm_record.data.point_pin_line;

	// Legend Parameters
	var drawCheck = Ext.getCmp('anatomography_image_comment_draw_check');
	if(drawCheck && drawCheck.rendered){
		if(drawCheck.getValue()){
			prm = prm + "&lp=UL";
			prm = prm + "&lc=646464";
		}
	}else if(init_anatomography_image_comment_draw){
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
			var prmPin = makeAnatomoPrm_Pin(ag_comment_store.getAt(i),anatomo_pin_shape_combo_value,coordinate_system);
			if(Ext.isEmpty(prmPin)) continue;
			prm = prm + '&' + prmPin;
		}
	}

	return prm;
	}catch(e){
		_dump("makeAnatomoPrm():"+e);
	}
}

oncheck_anatomo_grid_check = function(checkbox, fChecked){
	var prm_record = ag_param_store.getAt(0);
	prm_record.beginEdit();
	if (fChecked) {
		prm_record.set('grid', '1');
	} else {
		prm_record.set('grid', '0');
	}
	prm_record.endEdit();
	prm_record.commit();

	if(fChecked){
		try{
			Ext.get('ag-command-grid-len-label').show(false);
			Ext.get('ag-command-grid-color-label').show(false);
		}catch(e){}
		try{
			Ext.get('ag-image-grid-box').setHeight(66,{
				callback:function(){
					try{
						Ext.getCmp('ag-command-grid-len-combobox').enable();
						Ext.getCmp('ag-command-grid-len-combobox').show(false);
					}catch(e){}
					Ext.getCmp('ag-command-grid-color-field').enable();
					Ext.getCmp('ag-command-grid-color-field').show(false);
				}
			});
		}catch(e){}
	}else{
		try{
			Ext.get('ag-command-grid-len-label').hide(false);
			Ext.get('ag-command-grid-color-label').hide(false);
		}catch(e){}
		try{
			Ext.get('ag-image-grid-box').setHeight(19,true);
		}catch(e){}

		try{
			Ext.getCmp('ag-command-grid-len-combobox').hide(false);
			Ext.getCmp('ag-command-grid-len-combobox').disable();
		}catch(e){}
		Ext.getCmp('ag-command-grid-color-field').hide(false);
		Ext.getCmp('ag-command-grid-color-field').disable();
	}
	updateAnatomo();
}

/* iPad用 */
var anatomoImgDragStart_dX = null;
var anatomoImgDragStart_dY = null;
var anatomoImgDragStart_degH = null;
var anatomoImgDragStart_degV = null;

var anatomoImgMoveStartX = null;
var anatomoImgMoveStartY = null;
var anatomoImgMoveStart_dX = null;
var anatomoImgMoveStart_dY = null;

var curScale = null;
var chgScale = null;
var curRotation = null;

is_iPad = function(){
	if(navigator.userAgent.match(/^Mozilla\/5\.0\s\(iPad;\s*U;\s(CPU\s*[^;]+);[^\)]+\)/)){
		return true;
	}else{
		return false;
	}
}

imgTouchStart = function(e){
	e.preventDefault();
//_dump("imgTouchStart()");

	if(!e.touches) e.touches = [];
	for(var key in e){
		if(typeof e[key] == "function"){
		}else{
//			_dump('touchstart():'+key+"=["+e[key]+"]");
		}
	}

	if(e.touches && e.touches.length>1){
		anatomoImgDragStartX = null;
		anatomoImgDragStartY = null;
		anatomoImgDragStart_dX = null;
		anatomoImgDragStart_dY = null;

		anatomoImgMoveStartX = e.targetTouches[0].pageX;
		anatomoImgMoveStartY = e.targetTouches[0].pageY;
		anatomoImgMoveStart_dX = 0;
		anatomoImgMoveStart_dY = 0;
		return;
	}else{
		if(e.targetTouches && e.targetTouches.length>0){
			anatomoImgDragStartX = e.targetTouches[0].pageX;
			anatomoImgDragStartY = e.targetTouches[0].pageY;
		}else{
			anatomoImgDragStartX = e.pageX;
			anatomoImgDragStartY = e.pageY;
		}
		anatomoImgDragStart_dX = null;
		anatomoImgDragStart_dY = null;

		anatomoImgMoveStartX = null;
		anatomoImgMoveStartY = null;
		anatomoImgMoveStart_dX = null;
		anatomoImgMoveStart_dY = null;
	}
};
imgTouchMove = function(e){
	e.preventDefault();
//_dump("imgTouchMove(2)");

//_dump('touchmove:'+e.touches.length+","+e.targetTouches[0].pageX+","+e.targetTouches[0].pageY+","+chgScale+","+chgScale);

	if(anatomoImgDragStartX == null || anatomoImgDragStartY == null){
		if(anatomoImgMoveStartX != null && anatomoImgMoveStartY != null){
			anatomoImgMoveStart_dX = e.targetTouches[0].pageX - anatomoImgMoveStartX;
			anatomoImgMoveStart_dY = e.targetTouches[0].pageY - anatomoImgMoveStartY;

			if(chgScale == null) e.target.style.webkitTransform = 'translate(' + anatomoImgMoveStart_dX + 'px, ' + anatomoImgMoveStart_dY + 'px)';

		}
		return;
	}


	var dX = e.targetTouches[0].pageX - anatomoImgDragStartX;
	var dY = e.targetTouches[0].pageY - anatomoImgDragStartY;

//_dump('touchmove:'+e.touches.length+","+e.targetTouches[0].pageX+","+e.targetTouches[0].pageY+","+dX+","+dY);

	anatomoImgDragStart_dX = dX;
	anatomoImgDragStart_dY = dY;

	if(e.touches.length>1){
		return;
	}

	var rotateHSpan = document.getElementById("rotateH");
	var rotateVSpan = document.getElementById("rotateV");

	var degH = getRotateHorizontalValue();
	degH = degH - 15 * Math.floor(dX / 20);
	while (degH >= 360) {
		degH = degH - 360;
	}
	while (degH < 0) {
		degH = degH + 360;
	}

	var degV = getRotateVerticalValue();
	degV = degV + 15 * Math.floor(dY / 20);
	while (degV >= 360) {
		degV = degV - 360;
	}
	while (degV < 0) {
		degV = degV + 360;
	}

	degH = degH.toString();
	degV = degV.toString();

	anatomoImgDragStart_degH = degH;
	anatomoImgDragStart_degV = degV;

	var rotateHSpan = document.getElementById("rotImgDivRotateH");
	if(rotateHSpan){
		rotateHSpan.innerHTML = "H:"+degH;
	}

	var rotateVSpan = document.getElementById("rotImgDivRotateV");
	if(rotateVSpan){
		rotateVSpan.innerHTML = "V:"+degV;
	}

	var rotImgDiv = document.getElementById("rotImgDiv");
	if(rotImgDiv){
		rotImgDiv.style.left = (parseInt(e.targetTouches[0].pageX) - 130) + "px";
		rotImgDiv.style.top  = (parseInt(e.targetTouches[0].pageY) + 0)   + "px";

		var posX = (degH / 15 * (-80));
		var posY = (degV / 15 * (-80));

		if(posX<=-960 && posY<=-960){
			posX += 960;
			posY += 960;
			rotImgDiv.style.backgroundImage = "url(iphone/img/rotImg_iphone_rb.png)";
		}else if(posX<=-960){
			posX += 960;
			rotImgDiv.style.backgroundImage = "url(iphone/img/rotImg_iphone_rt.png)";
		}else if(posY<=-960){
			posY += 960;
			rotImgDiv.style.backgroundImage = "url(iphone/img/rotImg_iphone_lb.png)";
		}else{
			rotImgDiv.style.backgroundImage = "url(iphone/img/rotImg_iphone_lt.png)";
		}
		rotImgDiv.style.backgroundPositionX = posX + "px";
		rotImgDiv.style.backgroundPositionY = posY + "px";

		rotImgDiv.style.visibility = "visible";
	}

//_dump("degH=["+degH+"],degV=["+degV+"]");
//_dump(rotImgDiv.style.backgroundPosition);
};
imgTouchEnd = function(e){
	e.preventDefault();
//_dump("imgTouchEnd()");

//_dump('touchend:'+anatomoImgDragStart_dX+","+anatomoImgDragStart_dY);

	var rotImgDiv = document.getElementById("rotImgDiv");
	if(rotImgDiv) rotImgDiv.style.visibility = "hidden";

	if(anatomoImgDragStartX == null || anatomoImgDragStartY == null || anatomoImgDragStart_dX == null || anatomoImgDragStart_dY == null){
		if(anatomoImgMoveStartX == null || anatomoImgMoveStartY == null || anatomoImgMoveStart_dX == null || anatomoImgMoveStart_dY == null){
			if(anatomoImgDragStartX == null || anatomoImgDragStartY == null){
			 element_selected(e);
			}else{
				try{
					var img = document.getElementById('ag_img');
					var imgX = anatomoImgDragStartX - img.x;
					var imgY = anatomoImgDragStartY - img.y;
//_dump('touchend():&px=' + img.x + '&py=' +img.y);
				}catch(ex){
					alert(ex);
					return;
				}

//_dump('touchend():&px=' + imgX + '&py=' +imgY);

//				var urlStr = cgipath.point+'?' + makeAnatomoPrm() + '&px=' + imgX + '&py=' +imgY;

				var params = Ext.urlDecode(makeAnatomoPrm());
				params.px = imgX;
				params.py = imgY;

				var jsonStr = null;
				try{
					jsonStr = ag_extensions.toJSON.URI2JSON(params,{
						toString:true,
						mapPin:false,
						callback:undefined
					});
				}catch(e){jsonStr = null;}

				Ext.Ajax.request({
					url     : cgipath.point,
					method  : 'POST',
					params  : jsonStr ? jsonStr : params,
					success : function (response, options) {

//						var f_id = response.responseText;
						var f_id;
						try{var pointData = Ext.util.JSON.decode(response.responseText);}catch(e){_dump(e);}
						if(pointData) f_id = pointData.id;



						if(!f_id || !f_id.match(/^(?:FMA|BP)\d+/)){
							return;
						}

						getPickList(f_id,'partof');

					},
					failure: function (response, options) {
						alert(cgipath.point+":failure():"+response.statusText);
					}
				});
			}
		}
		anatomoImgDragStart_dX = null;
		anatomoImgDragStartdY = null;
		return;
	}

	var dX = anatomoImgDragStart_dX;
	var dY = anatomoImgDragStart_dY;

	try{
		setRotateHorizontalValue(anatomoImgDragStart_degH);
		setRotateVerticalValue(anatomoImgDragStart_degV);

		setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);
		addLongitude(-15 * Math.floor(dX / 20));
		addLatitude(15 * Math.floor(dY / 20));

		updateAnatomo();

		anatomoImgDragStart_dX = null;
		anatomoImgDragStart_dY = null;

	}catch(ex){
		_dump(ex);
	}
};
imgGestureStart = function(e){
	e.preventDefault();
//_dump("imgGestureStart()");
	if(curScale == null) curScale = 1;
};
imgGestureChange = function(e){
	e.preventDefault();
//_dump("imgGestureChange()");

	chgScale = e.scale;
	chgScale *= curScale;
	if(chgScale<1) chgScale = 1;

//_dump("gesturechange:["+ e.scale + "]["+ curScale + "]["+ chgScale + "]");

	e.target.style.webkitTransform = 'scale(' + e.scale + ') translate(' + anatomoImgMoveStart_dX + 'px, ' + anatomoImgMoveStart_dY + 'px)';

	var value = chgScale - 1;
	if(value<0) value = 0;
	if(value>6) value = 6;

	var prm_record = ag_param_store.getAt(0);
	prm_record.beginEdit();
	prm_record.set('zoom', value);
	prm_record.endEdit();
	prm_record.commit();

	var rotImgDiv = document.getElementById("rotImgDiv");
	if(rotImgDiv) rotImgDiv.style.visibility = "hidden";
};
imgGestureEnd = function(e){
	e.preventDefault();
//_dump("imgGestureEnd()");

	var dX = anatomoImgMoveStart_dX;
	var dY = anatomoImgMoveStart_dY;

	setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);
	moveTargetByMouseForOrtho(ag_param_store.getAt(0).data.image_h, dX / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)), dY / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)));

	updateAnatomo();

	curScale = chgScale;
	chgScale = null;
};

ag_command_zoom_menu_slider_syncThumb_task = new Ext.util.DelayedTask(function(){
	var slider = Ext.getCmp('zoom-slider');
	if(!slider || !slider.rendered) return;
	slider.syncThumb();
});

anatomography_image_render = function(comp,aOptions,aCB){
//	try{
		if(Ext.isEmpty(gParams.tp_md)){
			gParams.tp_ct = 1;
			gParams.tp_bt = 1;
			gParams.tp_ro = 1;
			gParams.tp_gr = 1;
			gParams.tp_zo = 1;
		}

		if(window.top != window && is_iPad()){
			delete gParams.tp_ct;
			delete gParams.tp_bt;
			delete gParams.tp_ro;
			delete gParams.tp_gr;
			delete gParams.tp_zo;
		}

		if(is_iPad()){
			var imageElem = document.getElementById('ag_img');
			if(imageElem){
				imageElem.addEventListener('touchstart',imgTouchStart,false);
				imageElem.addEventListener('touchmove', imgTouchMove, false);
				imageElem.addEventListener('touchend',  imgTouchEnd,  false);

				imageElem.addEventListener('gesturestart', imgGestureStart,  false);
				imageElem.addEventListener('gesturechange',imgGestureChange, false);
				imageElem.addEventListener('gestureend',   imgGestureEnd,    false);

				imageElem.addEventListener('load',function(e){
					e.target.style.webkitTransform = 'scale(1) translate(0px, 0px)';
					e.target.style.webkitTransformStyle = 'flat';
					e.target.style.left = '0px';
					e.target.style.top  = '0px';
				},false);
			}
			Ext.getDom('ag-image-command-box').style.opacity = '1';
			if(false){
				Ext.get('ag-command-ipad').removeClass('x-hide-display');
			}
		}

		comp.on("resize", function(comp,adjWidth,adjHeight,rawWidth,rawHeight){
			setImageWindowSize();
		});

		var ag_img = Ext.get('ag_img');
		if(ag_img){
			ag_img.on("load", function(e){
				var ag_img_frame = Ext.get("ag_img_frame");
				if(ag_img_frame){
					var load_image = e.getTarget();
					ag_img_frame.dom.style.width = load_image.width + 'px';
					ag_img_frame.dom.style.height = load_image.height + 'px';
				}
				var cmp = Ext.getCmp('anatomography-image');
				if(cmp && cmp.rendered && cmp.loadMask) cmp.loadMask.hide();
			});
			ag_img.on("contextmenu", function(e){
//				_dump("contextmenu");
//				e.stopEvent();
			});
		}



		if(Ext.isEmpty(gParams.tp_ct)){
			Ext.get('ag-image-command-box').setVisibilityMode(Ext.Element.DISPLAY);
			Ext.get('ag-image-command-box').hide();
		}

		Ext.get('ag-image-rotate-box').removeClass('x-hide-display');

		if(Ext.isEmpty(gParams.tp_bt)){
			Ext.get('ag-image-button-box').setVisibilityMode(Ext.Element.DISPLAY);
			Ext.get('ag-image-button-box').hide();
		}

		if(is_iPad()){
			Ext.get('ag-image-zoom-text-box').setVisibilityMode(Ext.Element.DISPLAY);
			Ext.get('ag-image-zoom-text-box').hide();
		}

		var prm_record = ag_param_store.getAt(0);

		setTimeout(function(){
			if(Ext.isEmpty(gParams.tp_zo)){
				Ext.get('ag-image-zoom-box').setVisibilityMode(Ext.Element.DISPLAY);
				Ext.get('ag-image-zoom-box').hide();
			}else if(Ext.isIE){
/* IEで表示しなので修正の必要あり
				var elem = Ext.getDom('ag-command-zoom-btn-down');
				if(elem){
					var parentNode = elem.parentNode;
					parentNode.removeChild(elem);
					elem = parentNode.ownerDocument.createElement('a');
					elem.setAttribute('id','ag-command-zoom-btn-down');
					parentNode.appendChild(elem);
				}
*/
			}
			var d_height = 190;
			if(Ext.isEmpty(gParams.tp_ro) && Ext.isEmpty(gParams.tp_gr)){
				d_height -= 90;
			}else if(Ext.isEmpty(gParams.tp_ro)){
				d_height -= 26;
			}else if(Ext.isEmpty(gParams.tp_gr)){
				d_height -= 74;
			}
			if(is_iPad()) d_height -= 24;

			var size = comp.getSize();
			var slider_height = size.height-d_height;
			if(slider_height<20) slider_height = 20;
			if(slider_height>100) slider_height = 100;
			Ext.get('ag-command-zoom-slider-render').setHeight(slider_height);
			new Ext.Slider({
				renderTo: 'ag-command-zoom-slider-render',
				id: 'zoom-slider',
				value : prm_record.data.zoom,
				height: slider_height,
				vertical: true,
				hidden : Ext.isEmpty(gParams.tp_zo),
				minValue: 0,
				maxValue: DEF_ZOOM_MAX-1,
				increment: 1,
				plugins: new Ext.ux.SliderTip(),
				listeners: {
					'change' : {
						fn : function (slider, value) {
//_dump("zoom-slider.change():value=["+value+"]");
							if(glb_zoom_xy){
								var elemImg = Ext.get('ag_img');
//								var xyImg = elemImg.getXY();
								var xyImg = glbImgXY;
								var mouseX = glb_zoom_xy[0] - xyImg[0];
								var mouseY = glb_zoom_xy[1] - xyImg[1];
								var centerX = parseInt((ag_param_store.getAt(0).data.image_w /2) -  mouseX);
								var centerY = parseInt((ag_param_store.getAt(0).data.image_h /2) -  mouseY);
								setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);
								moveTargetByMouseForOrtho(ag_param_store.getAt(0).data.image_h, centerX / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)), centerY / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)));
							}
							var prm_record = ag_param_store.getAt(0);
							prm_record.beginEdit();
							prm_record.set('zoom', value / 5);
							prm_record.endEdit();
							prm_record.commit();
							anatomoUpdateZoomValueText(value + 1);
							if(glb_zoom_xy){
								var elemImg = Ext.get('ag_img');
//								var xyImg = elemImg.getXY();
								var xyImg = glbImgXY;
								var mouseX = glb_zoom_xy[0] - xyImg[0];
								var mouseY = glb_zoom_xy[1] - xyImg[1];
								var moveX = parseInt(mouseX - (ag_param_store.getAt(0).data.image_w /2));
								var moveY = parseInt(mouseY - (ag_param_store.getAt(0).data.image_h /2));
								setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);
								moveTargetByMouseForOrtho(ag_param_store.getAt(0).data.image_h, moveX / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)), moveY / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)));
							}
							updateAnatomo();
							updateClipImage();
							if(glb_zoom_xy) glb_zoom_xy = null;
						},
						scope  : this
					},
					'render' : {
						fn : function(slider){
							if(glb_zoom_slider){
								var textField = Ext.getCmp('zoom-value-text');
								var slider = Ext.getCmp('zoom-slider');
								if(slider && slider.rendered && textField && textField.rendered){
//_dump("zoom-slider.render():glb_zoom_slider=["+glb_zoom_slider+"]");
									slider.setValue(glb_zoom_slider-1);
									glb_zoom_slider = null;
									ag_command_zoom_menu_slider_syncThumb_task.delay(1000);
								}
							}
						},
						scope:this
					}
				}
			});
		},100);

		new Ext.form.NumberField ({
			ctCls : 'x-small-editor',
			renderTo: 'ag-command-zoom-text-render',
			id: 'zoom-value-text',
			width: 28,
			value : prm_record.data.zoom+1,
			allowBlank : false,
			allowDecimals : false,
			allowNegative : false,
			selectOnFocus : true,
			hidden : Ext.isEmpty(gParams.tp_zo),
			maxValue : DEF_ZOOM_MAX,
			minValue : 1,
			listeners: {
				'change': {
					fn : function(textField,newValue,oldValue){
						if (anatomoUpdateZoomValue) {
							return;
						}
						var value = isNaN(parseInt(newValue, 10))?oldValue:parseInt(newValue, 10);
						if (value < 1) {
							value = 1;
						}
						if (value > DEF_ZOOM_MAX) {
							value = DEF_ZOOM_MAX
						}
						textField.setValue(value);
						var slider = Ext.getCmp('zoom-slider');
						if(slider && slider.rendered){
//_dump("zoom-value-text.change():["+value+"]");
							slider.setValue(value - 1);
							ag_command_zoom_menu_slider_syncThumb_task.delay(1000);
						}
					},
					scope:this
				},
				'valid': {
					fn : function(textField){
						var value = textField.getValue();
						var slider = Ext.getCmp('zoom-slider');
						if(slider && slider.rendered){
//_dump("zoom-value-text.valid():["+value+"]");
							slider.setValue(value - 1);
							ag_command_zoom_menu_slider_syncThumb_task.delay(1000);
						}
					},
					scope:this
				},
				'render': {
					fn : function(textField){
						if(glb_zoom_slider){
							var slider = Ext.getCmp('zoom-slider');
							if(slider && slider.rendered){
//_dump("zoom-value-text.render():glb_zoom_slider=["+glb_zoom_slider+"]");
								slider.setValue(glb_zoom_slider-1);
								glb_zoom_slider = null;
								ag_command_zoom_menu_slider_syncThumb_task.delay(1000);
							}
						}
					},
					scope:this
				}
			}
		});

		var ag_command_rotate_menu_hide_task = new Ext.util.DelayedTask(function(){
			var button = Ext.getCmp('ag-command-rotate-button');
			if(!button || !button.rendered) return;
			if(button.hasVisibleMenu()) button.hideMenu();
		});
		new Ext.Button({
			ctCls : 'x-small-editor',
			renderTo: 'ag-command-rotate-button-render',
			id: 'ag-command-rotate-button',
			width: 30,
			text:'Rotate',
			hidden : Ext.isEmpty(gParams.tp_ro),
			menu: {
				id: 'ag-command-rotate-menu',
				cls : 'ag-command-rotate-menu',
				items : [{
					text   : 'H:0,V:0',
					icon   : "img_angle/000_000.png",
					itemCls: 'x-menu-item ag-command-rotate-menu-item',
					handler: function(){ setRotate(0,0); }
				},{
					text   : 'H:45,V:0',
					icon   : "img_angle/045_000.png",
					itemCls: 'x-menu-item ag-command-rotate-menu-item',
					handler: function(){ setRotate(45,0); }
				},{
					text   : 'H:90,V:0',
					icon   : "img_angle/090_000.png",
					itemCls: 'x-menu-item ag-command-rotate-menu-item',
					handler: function(){ setRotate(90,0); }
				},{
					text   : 'H:180,V:0',
					icon   : "img_angle/180_000.png",
					itemCls: 'x-menu-item ag-command-rotate-menu-item',
					handler: function(){ setRotate(180,0); }
				},{
					text   : 'H:270,V:0',
					icon   : "img_angle/270_000.png",
					itemCls: 'x-menu-item ag-command-rotate-menu-item',
					handler: function(){ setRotate(270,0); }
				},{
					text   : 'H:315,V:0',
					icon   : "img_angle/315_000.png",
					itemCls: 'x-menu-item ag-command-rotate-menu-item',
					handler: function(){ setRotate(315,0); }
				},{
					text   : 'H:180,V:90',
					icon   : "img_angle/180_090.png",
					itemCls: 'x-menu-item ag-command-rotate-menu-item',
					handler: function(){ setRotate(180,90); }
				},{
					text   : 'H:0,V:270',
					icon   : "img_angle/000_270.png",
					itemCls: 'x-menu-item ag-command-rotate-menu-item',
					handler: function(){ setRotate(0,270); }
				}]
			}
		});


		Ext.QuickTips.register({
			target: 'ag-command-btn-rotate',
			text: get_ag_lang('TOOLTIP_ROTATE')
		});
		Ext.QuickTips.register({
			target: 'ag-command-btn-move',
			text: get_ag_lang('TOOLTIP_MOVE')
		});
		Ext.QuickTips.register({
			target: 'ag-command-focus-center-button',
			text: get_ag_lang('TOOLTIP_FOCUS_CENTER')
		});
		Ext.QuickTips.register({
			target: 'ag-command-focus-button',
			text: get_ag_lang('TOOLTIP_FOCUS')
		});

		new Ext.form.Checkbox({
			ctCls    : 'x-small-editor',
			id       : 'ag-command-autorotate-chechbox',
			checked  : false,
			listeners: {
				'check': function(checkbox,checked){
					Ext.getCmp('ag-command-image-controls-rotateAuto').setValue(checked);
				},
				scope:this
			}
		}).render('ag-command-autorotate-chechbox-render','ag-command-autorotate-chechbox-label');
		if(gDispAnatomographyPanel){
			var elem = Ext.get('ag-command-autorotate-chechbox-render');
			if(elem){
				elem.setVisibilityMode(Ext.Element.DISPLAY);
				elem.hide();
			}
			Ext.get('ag-command-autorotate-chechbox-label').hide();
		}

		if(Ext.isEmpty(gParams.tp_gr)){
			try{
				Ext.get('ag-image-grid-box').setVisibilityMode(Ext.Element.DISPLAY);
				Ext.get('ag-image-grid-box').hide();
			}catch(e){}
		}

		new Ext.form.Checkbox ({
			ctCls : 'x-small-editor',
			renderTo: 'ag-command-grid-render',
			id: 'ag-command-grid-show-check',
			width: 45,
			checked: (prm_record.data.grid=='1')?true:false,
			hidden : Ext.isEmpty(gParams.tp_gr),
			listeners: {
				'render': function(checkbox){
					checkbox.on('check',oncheck_anatomo_grid_check);
					if(checkbox.checked){
						try{Ext.get('ag-image-grid-box').setHeight(66);}catch(e){}
						try{Ext.getCmp('ag-command-grid-len-combobox').show();}catch(e){}
					}else{
						try{Ext.getCmp('ag-command-grid-len-combobox').hide();}catch(e){}
						try{Ext.get('ag-image-grid-box').setHeight(19);}catch(e){}
					}
				},
				scope:this
			}
		});

		new Ext.ux.ColorField({
			ctCls : 'x-small-editor',
			width: 54,
			renderTo:'ag-command-grid-color-render',
			id:'ag-command-grid-color-field',
			value:prm_record.data.grid_color,
			disabled: (prm_record.data.grid=='1')?false:true,
			hidden: (prm_record.data.grid=='1')?false:true,
			editable: false,
			hideTrigger : is_iPad(),
			colors: palette_color2,
			colorsItemCls: 'x-color-palette x-color-palette-grid',
			colorsOptionMenu: false,
			listeners: {
				select: function (e, color) {
					var prm_record = ag_param_store.getAt(0);
					prm_record.beginEdit();
					prm_record.set('grid_color', color);
					prm_record.endEdit();
					prm_record.commit();
					updateAnatomo();
				},
				render: function(checkbox){
					try{
						if(prm_record.data.grid=='1'){
							Ext.get('ag-command-grid-color-label').show(false);
						}else{
							Ext.get('ag-command-grid-color-label').hide(false);
						}
					}catch(e){}
				},
				scope:this
			}
		});

		new Ext.form.ComboBox({
			ctCls : 'x-small-editor',
			renderTo:'ag-command-grid-len-render',
			id: 'ag-command-grid-len-combobox',
			editable: false,
			mode: 'local',
			lazyInit: false,
			displayField: 'disp',
			valueField: 'value',
			width: 54,
			value: (isNaN(prm_record.data.grid_len))?'':prm_record.data.grid_len,
			disabled: (prm_record.data.grid=='1')?false:true,
			hidden: (prm_record.data.grid=='1')?false:true,
			hideTrigger : is_iPad(),
			triggerAction: 'all',
			store: new Ext.data.SimpleStore({
				fields: ['disp', 'value'],
				data : [
					['1mm', 1],
					['5mm', 5],
					['10mm', 10],
					['50mm', 50],
					['100mm', 100]
				]
			}),
			listeners: {
				'render': function(combo){
					try{
						if(prm_record.data.grid=='1'){
							Ext.get('ag-command-grid-len-label').show(false);
						}else{
							Ext.get('ag-command-grid-len-label').hide(false);
						}
					}catch(e){}
				},
				'select' : function(combo, record, index) {
					var prm_record = ag_param_store.getAt(0);
					prm_record.beginEdit();
					prm_record.set('grid_len', record.data.value);
					prm_record.endEdit();
					prm_record.commit();
					updateAnatomo();
				},
				scope:this
			}
		});

		if(aCB) (aCB)();
//	}catch(e){
//		_dump("anatomography_image_render():"+e);
//	}
};


function ag_init(){
//_dump("ag_init():["+Ext.isEmpty(gParams.tp_ap)+"]");

	if(!Ext.isEmpty(gParams.tp_md) && gParams.tp_md == 1){
		gDispAnatomographyPanel = true;
		var anatomography_image = new Ext.Panel({
			contentEl  : 'anatomography-image-contentEl',
			id         : 'anatomography-image',
			region     : 'center',
			autoScroll : false,
			border     : false,
			bodyStyle  : 'background-color:#f8f8f8;overflow:hidden;',
			listeners : {
				"render": function(comp){
					comp.loadMask = new Ext.LoadMask(comp.body,{removeMask:false});
					setTimeout(function(){ comp.loadMask.show(); },0);
					anatomography_image_render(comp,undefined,function(){
						anatomography_init();
						setImageWindowSize();
						comp.loadMask.hide();
					});
				},
				scope:this
			}
		});

		var viewport = new Ext.Viewport({
			layout:'border',
			monitorResize:true,
			items:anatomography_image,
			listeners : {
				'resize' : function(){
				},scope:this
			}
		});
		makeRotImgDiv();

		Ext.get('ag-copyright').removeClass('x-hide-display');
		Ext.getDom('ag-copyright-link').setAttribute("href",location.pathname+"?tp_ap="+encodeURIComponent(gParams.tp_ap));
	}

	if(gParams && !Ext.isEmpty(gParams.tp_ap)){
		try{var position = Ext.getCmp('positionSelect').getValue();}catch(e){}
		var f_ids = [];
		var t_type = '3';
		var tpap_param = analyzeTPAP(gParams.tp_ap);
		if(tpap_param && ((tpap_param.parts && tpap_param.parts.length>0) || (tpap_param.point_parts && tpap_param.point_parts.length>0) || (tpap_param.pins && tpap_param.pins.length>0))){

			var tgi_version = null;
			if(tpap_param.common && tpap_param.common.bp3d_version){
//_dump("ag_init():tpap_param.common.bp3d_version=["+tpap_param.common.bp3d_version+"]");
				tgi_version = tpap_param.common.bp3d_version;
				var tg_id = tpap_param.common.tg_id ? tpap_param.common.tg_id : undefined;
				if(tg_id==undefined && tpap_param.common.model && model2tg[tpap_param.common.model]) tg_id = model2tg[tpap_param.common.model].tg_id;
				if(tg_id==undefined && version2tg[tgi_version]) tg_id = version2tg[tgi_version].tg_id;
				if(tg_id && (!version2tg[tgi_version] || version2tg[tgi_version].tgi_delcause)){
					if(Ext.isEmpty(latestversion[tg_id])) return;
					tgi_version = latestversion[tg_id];
				}

//_dump("ag_init():tgi_version=["+tgi_version+"]");

				var cmp = Ext.getCmp('bp3d-version-combo');
				if(cmp && cmp.rendered) cmp.setValue(tgi_version);
				var cmp = Ext.getCmp('anatomo-version-combo');
				if(cmp && cmp.rendered) cmp.setValue(tgi_version);
			}

			if(tpap_param.common && tpap_param.common.treename){
				if(tpap_param.common.treename=='isa'){
					t_type = '3';
				}else if(tpap_param.common.treename=='partof'){
					t_type = '4';
				}
				var cmp = Ext.getCmp('bp3d-tree-type-combo');
				if(cmp && cmp.rendered) cmp.setValue(t_type);
				var cmp = Ext.getCmp('bp3d-tree-type-combo-ag');
				if(cmp && cmp.rendered) cmp.setValue(t_type);
			}

			if(tpap_param.parts && tpap_param.parts.length>0){
//_dump("ag_init():tpap_param.parts.length=["+tpap_param.parts.length+"]");
				for(var i=0,len=tpap_param.parts.length;i<len;i++){
//_dump("ag_init():["+i+"]:id=["+tpap_param.parts[i].id+"]");
//_dump("ag_init():["+i+"]:f_id=["+tpap_param.parts[i].f_id+"]");
					if(tpap_param.parts[i].id){
						if(Ext.isEmpty(tpap_param.parts[i].version)){
							f_ids.push({f_id:tpap_param.parts[i].id});
						}else{
							f_ids.push({f_id:tpap_param.parts[i].id,version:tpap_param.parts[i].version});
						}
					}else if(tpap_param.parts[i].f_id){
						if(Ext.isEmpty(tpap_param.parts[i].version)){
							f_ids.push({f_id:tpap_param.parts[i].f_id});
						}else{
							f_ids.push({f_id:tpap_param.parts[i].f_id,version:tpap_param.parts[i].version});
						}
					}
				}
			}
//_dump("ag_init():f_ids.length=["+f_ids.length+"]");

			if(tpap_param.point_parts && tpap_param.point_parts.length>0){
				for(var i=0,len=tpap_param.point_parts.length;i<len;i++){
					if(tpap_param.point_parts[i].id){
						if(Ext.isEmpty(tpap_param.point_parts[i].version)){
							f_ids.push({f_id:tpap_param.point_parts[i].id});
						}else{
							f_ids.push({f_id:tpap_param.point_parts[i].id,version:tpap_param.point_parts[i].version});
						}
					}else if(tpap_param.point_parts[i].f_id){
						if(Ext.isEmpty(tpap_param.point_parts[i].version)){
							f_ids.push({f_id:tpap_param.point_parts[i].f_id});
						}else{
							f_ids.push({f_id:tpap_param.point_parts[i].f_id,version:tpap_param.point_parts[i].version});
						}
					}
				}
			}
//_dump("ag_init():f_ids.length=["+f_ids.length+"]");
			if(f_ids.length>0){
				var params = {
					objs : Ext.util.JSON.encode(f_ids)
				};
//_dump("ag_init():params.objs=["+params.objs+"]");
				if(!Ext.isEmpty(position)) params.position = position;
				if(tgi_version){
					params.version = tgi_version;
				}
//_dump("ag_init():params.version=["+params.version+"]");
				if(tpap_param.common && tpap_param.common.model){
					params.model = tpap_param.common.model;
				}

				params.t_type = t_type;
//				bp3d_contents_store.on('load',load_bp3d_contents_store,this,{single:true});
//				bp3d_contents_store.load({params:params});

				bp3d_contents_load_store.on('load',load_bp3d_contents_store,this,{single:true});
				bp3d_contents_load_store.load({params:params});

			}else{

				var runner = new Ext.util.TaskRunner();
				var task = {
					run: function(){
						var contents_tabs = Ext.getCmp('contents-tab-panel');
						if(contents_tabs){
							runner. stop(this);
							load_bp3d_contents_store(bp3d_contents_load_store,[],{});
						}
					},
					interval: 1000 //1 second
				}
				runner.start(task);

//				setTimeout(function(){
//					load_bp3d_contents_store(bp3d_contents_load_store,[],{});
//				},5000);
			}
		}
	}
}



function get_bp3d_contents_store_fields(){
	return [
		'id',
		'pid',
		't_type',
		'name',
		'src',
		'srcstr',
		'f_id',
		'b_id',
		'common_id',
		'name_j',
		'name_e',
		'name_k',
		'name_l',
		'syn_j',
		'syn_e',
		'def_e',
		'organsys_j',
		'organsys_e',
		'organsys',
		'phase',
		{name:'xmin',   type:'float'},
		{name:'xmax',   type:'float'},
		{name:'ymin',   type:'float'},
		{name:'ymax',   type:'float'},
		{name:'zmin',   type:'float'},
		{name:'zmax',   type:'float'},
		{name:'volume', type:'float'},
		{name:'density', type:'float'},
		'used_parts',
		{name:'used_parts_num',type:'int'},
		'density_icon',
		'density_ends',
		{name:'density_ends_num',type:'int'},
		{name:'primitive',type:'boolean'},
		'taid',
		'physical',
		{name:'phy_id',type:'int'},
		'segment',
		'seg_color',
		'seg_thum_bgcolor',
		'seg_thum_bocolor',
		{name:'seg_id',type:'int'},
		'lsdb_term',
		'version',
		{name:'tg_id',type:'int',convert:function(v,r){
			if(Ext.isEmpty(v)){
				return r.md_id;
			}else{
				return v;
			}
		}},
		{name:'tgi_id',type:'int',convert:function(v,r){
			if(Ext.isEmpty(v)){
				return r.mv_id;
			}else{
				return v;
			}
		}},
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
		'mca_id',

		'model',
		'model_version',
		'concept_info',
		'concept_build',
		'buildup_logic',
		{name:'bu_revision',type:'int'},

		'state',
		'def_color',
		{name:'point',type:'boolean'},
		'elem_type',
		'point_label',
		'point_parent',
		'point_children',
		{name:'entry', type:'date', dateFormat:'timestamp'},
		{name:'lastmod', type:'date', dateFormat:'timestamp'},
		'search_c_path',
		'c_path',
		'u_path',
		'is_a',
		'part_of',
		'has_part',
		'is_a_path2root',
		'is_a_brother',
		'is_a_children',
		'partof_path2root',
		'partof_path2root_circular',
		'partof_brother',
		'partof_children'
	];
}

bp3d_contents_store = new Ext.data.JsonStore({
	url: 'get-contents.cgi',
	pruneModifiedRecords : true,
	root: 'images',
	fields: get_bp3d_contents_store_fields(),
	listeners: {
		'beforeload' : {
			fn:function(self,options){
//				_dump("bp3d_contents_store.beforeload()");
				try{
					self.baseParams = self.baseParams || {};
					delete gParams.parent;
					if(!Ext.isEmpty(gParams.parent)) self.baseParams.parent = gParams.parent;
					self.baseParams.lng = gParams.lng;

					delete self.baseParams.t_type;
					try{var treeType = Ext.getCmp('bp3d-tree-type-combo').getValue();}catch(e){treeType=undefined;}
					if(!Ext.isEmpty(treeType)) self.baseParams.t_type = treeType;

					try{var position = Ext.getCmp('positionSelect').getValue();}catch(e){position=undefined;}
					if(!Ext.isEmpty(position)) self.baseParams.position = position;

					self.baseParams.sorttype = '';
					try{var bp3d_sorttype = Ext.getCmp('sortSelect').getValue();}catch(e){_dump("bp3d_contents_store.beforeload():e=["+e+"]");bp3d_sorttype=undefined;}
					if(!Ext.isEmpty(bp3d_sorttype)) self.baseParams.sorttype = bp3d_sorttype;


					delete self.baseParams.version;
					if(options.params && options.params.version){
						self.baseParams.version = options.params.version;
						init_bp3d_version = options.params.version;
					}else{
						try{
							self.baseParams.version = Ext.getCmp('bp3d-version-combo').getValue();
						}catch(e){
							_dump("bp3d_contents_store.beforeload():e=["+e+"]");
						}
					}
					if(Ext.isEmpty(self.baseParams.version)) self.baseParams.version = init_bp3d_version;

					try{var detailEl = Ext.getCmp('img-detail-panel').body;}catch(e){}
					try{var commentDetailEl = Ext.getCmp('comment-detail-panel').body;}catch(e){}

					if(detailEl) detailEl.update('<div style="padding:10px;font-size:11px;"><img src="ext-2.2.1/resources/images/default/tree/loading.gif">データ読込中 ...</div>');
					if(commentDetailEl) commentDetailEl.update('<div style="padding:10px;font-size:11px;"><img src="ext-2.2.1/resources/images/default/tree/loading.gif">データ読込中 ...</div>');

					var bp3d_contents_detail_annotation_panel = Ext.getCmp('bp3d-contents-detail-annotation-panel');
					if(bp3d_contents_detail_annotation_panel){
						bp3d_contents_detail_annotation_panel.disable();
						if(bp3d_contents_detail_annotation_panel.bottomToolbar) bp3d_contents_detail_annotation_panel.bottomToolbar.disable();
					}
//					for(var key in self.baseParams){
//						_dump("bp3d_contents_store.beforeload():["+key+"]=["+self.baseParams[key]+"]");
//					}

					for(var key in init_bp3d_params){
						if(key.match(/_id$/)) self.baseParams[key] = init_bp3d_params[key];
					}

					try{var treeType = Ext.getCmp('bp3d-tree-type-combo').getValue();}catch(e){treeType=undefined;}
					if(!Ext.isEmpty(treeType)) self.baseParams.bul_id = treeType;

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


					self.baseParams.degenerate_same_shape_icons = false;
					if($("input#bp3d-content-panel-header-content-degenerate-same-shape-icons:checked").val()) self.baseParams.degenerate_same_shape_icons = true;
//					console.log("self.baseParams.degenerate_same_shape_icons=["+self.baseParams.degenerate_same_shape_icons+"]");

				}catch(e){
					_dump("bp3d_contents_store.beforeload():"+e);
				}
			},
			scope:this
		},
		'datachanged':{
			fn:function(self){
//				_dump("bp3d_contents_store.datachanged()");
				try{
//					var bp3d_contents_dataview = Ext.getCmp('bp3d-contents-dataview');
					var bp3d_contents_dataview = getViewImages();
					if(bp3d_contents_dataview){
						setTimeout(function(){
							try{
								bp3d_contents_dataview.show();
								var num = -1;
								var id = null;
								var fmaid = Cookies.get('ag_annotation.images.fmaid');
//								_dump("bp3d_contents_store.datachanged():fmaid=["+fmaid+"]");
								if(fmaid){
									num = self.find("f_id",fmaid);
									if(num<0){
//										Cookies.set('ag_annotation.images.fmaid','');
									}else{
//										var record = self.getAt(num);
//										if(record) id = record.data.id;
									}
								}
//								_dump("bp3d_contents_store.datachanged():fmaid=["+fmaid+"]["+num+"]");
								if(num<0){
									num = 0;
								}
								if(num>=0){
									bp3d_contents_dataview.select(num);
/*
									var element = bp3d_contents_dataview.getEl();
									if(element){
										element.dom.scrollTop = 0;
										var dom = Ext.getDom("contents_"+id);
										if(id && dom){
											element.dom.parentNode.scrollTop = dom.offsetTop - 4;
										}else{
											element.dom.parentNode.scrollTop = 0;
										}
									}
*/
									var element = bp3d_contents_dataview.getEl();
									if(element){
										element.dom.scrollTop = 0;
										var nodes = bp3d_contents_dataview.getSelectedNodes();
										if(nodes && nodes.length){
											var dom = nodes[0];
											if(dom){
												element.dom.parentNode.scrollTop = dom.offsetTop - 4;
											}else{
												element.dom.parentNode.scrollTop = 0;
											}
										}
									}

								}else{
									showDetails();
								}
								var chooserCmp = Ext.getCmp('img-chooser-view');
								var detailCmp = Ext.getCmp('img-detail-panel');
								var chooserEl = chooserCmp.body;
								var filterCmp = Ext.getCmp('filter');
								var sortCmp = Ext.getCmp('sortSelect');
								var positionCmp = Ext.getCmp('positionSelect');
								var disptypeCmp = Ext.getCmp('disptypeSelect');
								var addcommentCmp = Ext.getCmp('btn-add-comment');

								if(bp3d_contents_dataview.store.getRange().length>0){
									if(chooserCmp) chooserCmp.show();
									if(detailCmp) detailCmp.show();
									if(chooserEl) chooserEl.show();
									if(filterCmp) filterCmp.enable();
									if(sortCmp) sortCmp.enable();
									if(positionCmp) positionCmp.enable();
									if(disptypeCmp) disptypeCmp.enable();
									if(addcommentCmp) addcommentCmp.enable();
								}else{
									if(addcommentCmp) addcommentCmp.disable();
								}

							}catch(e){alert(e)}
						},250);
					}
				}catch(e){
					_dump("bp3d_contents_store.datachanged():"+e);
				}
			},scope:this},
		'load': {
			fn: function(store,records){

//				_dump("bp3d_contents_store.load("+records.length+")");
				if(store.reader.jsonData){
//					_dump(store.reader.jsonData);
					for(var key in store.reader.jsonData){
						if(
							typeof store.reader.jsonData[key] != 'number' &&
							typeof store.reader.jsonData[key] != 'string' &&
							typeof store.reader.jsonData[key] != 'boolean'
						) continue;
						init_bp3d_params[key] = store.reader.jsonData[key];
//						_dump("bp3d_contents_store.load():["+key+"]=["+init_bp3d_params[key]+"]["+(typeof init_bp3d_params[key])+"]");
					}
				}
				var buildup_logic = ' Tree of ';
				var ci_name = 'FMA';
				var cb_name = '3.0';
				if(store.reader.jsonData.ci_name) ci_name = store.reader.jsonData.ci_name;
				if(store.reader.jsonData.cb_name) cb_name = store.reader.jsonData.cb_name;
				Ext.get('bp3d-buildup-logic-contents-label').update((init_bp3d_params.bul_id==3 ? 'IS-A' : 'HAS-PART')+buildup_logic+ci_name+cb_name);

				Ext.get('bp3d-concept-info-label').update(ci_name);
				Ext.get('bp3d-concept-build-label').update(cb_name);

				try{filter_func();}catch(e){}
			},scope:this
		},
		'loadexception': {
			fn:function(){

Ext.get('bp3d-buildup-logic-contents-label').update('');

				_dump("bp3d_contents_store.loadexception()");
				try{
					var viewport = Ext.getCmp('viewport');
					if(viewport && viewport.loadMask){
						viewport.loadMask.hide();
						delete viewport.loadMask;
						var contents_tabs = Ext.getCmp('contents-tab-panel');
						if(contents_tabs) contents_tabs.setActiveTab('contents-tab-bodyparts-panel');
					}
				}catch(e){}
				try{
//					var bp3d_contents_dataview = Ext.getCmp('bp3d-contents-dataview');
					var bp3d_contents_dataview = getViewImages();
					if(bp3d_contents_dataview) bp3d_contents_dataview.hide();

					var chooserEl = Ext.getCmp('img-chooser-view').body;
					if(chooserEl) chooserEl.hide();
					try{
						var detailEl = Ext.getCmp('img-detail-panel').body;
						if(detailEl) detailEl.update('');
					}catch(e){}

					var filterCmp = Ext.getCmp('filter');
					if(filterCmp) filterCmp.disable();

					var sortCmp = Ext.getCmp('sortSelect');
					if(sortCmp) sortCmp.disable();

					var positionCmp = Ext.getCmp('positionSelect');
					if(positionCmp) positionCmp.disable();

					var disptypeCmp = Ext.getCmp('disptypeSelect');
					if(disptypeCmp) disptypeCmp.disable();


					var addcommentCmp = Ext.getCmp('btn-add-comment');
					if(addcommentCmp) addcommentCmp.disable();
				}catch(e){
					_dump("bp3d_contents_store.loadexception():"+e);
				}
			},scope:this
		}
	}
});

bp3d_contents_load_store = new Ext.data.JsonStore({
	url: 'get-contents.cgi',
	pruneModifiedRecords : true,
	root: 'images',
	fields: get_bp3d_contents_store_fields(),
	listeners: {
		'beforeload' : {
			fn:function(self,options){
				_dump("bp3d_contents_load_store.beforeload()");
				_dump(options);
				try{
					self.baseParams = self.baseParams || {};
					delete gParams.parent;
					if(!Ext.isEmpty(gParams.parent)) self.baseParams.parent = gParams.parent;
					self.baseParams.lng = gParams.lng;

					delete self.baseParams.t_type;
					try{var treeType = Ext.getCmp('bp3d-tree-type-combo').getValue();}catch(e){treeType=undefined;}
					if(!Ext.isEmpty(treeType)) self.baseParams.t_type = treeType;

					try{var position = Ext.getCmp('positionSelect').getValue();}catch(e){position=undefined;}
					if(!Ext.isEmpty(position)) self.baseParams.position = position;

					self.baseParams.sorttype = '';
					try{var bp3d_sorttype = Ext.getCmp('sortSelect').getValue();}catch(e){_dump("bp3d_contents_store.beforeload():e=["+e+"]");bp3d_sorttype=undefined;}
					if(!Ext.isEmpty(bp3d_sorttype)) self.baseParams.sorttype = bp3d_sorttype;

					delete self.baseParams.version;
					if(options.params && options.params.version){
						self.baseParams.version = options.params.version;
						init_bp3d_version = options.params.version;
						try{
							var store = Ext.getCmp('bp3d-version-combo').getStore();
						}catch(e){
							_dump("bp3d_contents_load_store.beforeload():e=["+e+"]");
						}
					}else{
						try{
							self.baseParams.version = Ext.getCmp('bp3d-version-combo').getValue();
						}catch(e){
							_dump("bp3d_contents_load_store.beforeload():e=["+e+"]");
						}
					}
					if(Ext.isEmpty(self.baseParams.version)) self.baseParams.version = init_bp3d_version;

					_dump(self.baseParams);

				}catch(e){
					_dump("bp3d_contents_load_store.beforeload():"+e);
				}
			},
			scope:this
		},
		'datachanged' : {
			fn:function(self,options){
				_dump("bp3d_contents_load_store.datachanged()");
			}
		},
		load: {
			fn:function(store,records){
				_dump("bp3d_contents_load_store.load("+records.length+")");
				if(store.reader.jsonData){
					_dump(store.reader.jsonData);
					for(var key in store.reader.jsonData){
						if(
							typeof store.reader.jsonData[key] != 'number' &&
							typeof store.reader.jsonData[key] != 'string'
						) continue;
						init_bp3d_params[key] = store.reader.jsonData[key];
//						_dump("bp3d_contents_load_store.load():["+key+"]=["+init_bp3d_params[key]+"]["+(typeof init_bp3d_params[key])+"]");
					}
				}
			}
		},
		' loadexception' : {
			fn:function(self,records){
				_dump("bp3d_contents_load_store.loadexception()");
			}
		}
	}
});





var ag_put_usersession_task = new Ext.util.DelayedTask(function(){
//_dump("ag_put_usersession_task():["+makeAnatomoPrm()+"]");
//_dump("ag_put_usersession_task():["+makeAnatomoPrm(2)+"]");
	Ext.Ajax.request({
		url       : 'put-usersession.cgi',
		method    : 'POST',
		params    : {
			info  : makeAnatomoPrm(2),
			state : Ext.util.JSON.encode(glb_us_state),
			keymap : Ext.util.JSON.encode(glb_us_keymap)
		},
		success   : function(conn,response,options,aParam){
//			_dump("ag_put_usersession_task():put-usersession.cgi:success");
		},
		failure : function(conn,response,options){
//			_dump("ag_put_usersession_task():put-usersession.cgi:failure");
		}
	});
});

var ag_keymap_fields = [
	{name : 'order', type : 'int'},
	{name : 'key',   type : 'string'},
	{name : 'code',  type : 'int'},
	{name : 'shift', type : 'boolean', defaultValue : false},
	{name : 'ctrl',  type : 'boolean', defaultValue : false},
	{name : 'alt',   type : 'boolean', defaultValue : false},
	{name : 'stop',  type : 'boolean', defaultValue : true},
	{name : 'cmd',   type : 'string'}
];

var ag_keymap_store = new Ext.data.JsonStore({
	root   : 'keymaps',
	fields : ag_keymap_fields,
	sortInfo : {
		field     : 'order',
		direction : 'ASC'
	},
	totalProperty : glb_us_keymap.length,
	data : {
		keymaps : glb_us_keymap
	},
	listeners : {
		'add' : function(store,records,index){
//			_dump("ag_keymap_store:add()");
		},
		'remove' : function(store,record,index){
//			_dump("ag_keymap_store:remove()");
		},
		'update' : function(store,record,operation){
//			_dump("ag_keymap_store:update()");
		}
	}
});
//_dump("ag_keymap_store=["+ag_keymap_store.getCount()+"]");



function agKeyMapCB(k,e){
	var contents_tabs = Ext.getCmp('contents-tab-panel');
	if(contents_tabs.getActiveTab().id != 'contents-tab-anatomography-panel') return;
	var shiftKey = e.shiftKey?true:false;
	var ctrlKey = e.ctrlKey?true:false;
	var altKey = e.altKey?true:false;
	var index = ag_keymap_store.findBy(function(record,id){
		var key = record.get('key');
		var code = Ext.EventObject[key];
		var shift = record.get('shift');
		var ctrl = record.get('ctrl');
		var alt = record.get('alt');
		return (k==code && shift==shiftKey && ctrl==ctrlKey && alt==altKey)?true:false;
	});
//	_dump("agKeyMapCB():index=["+index+"]");
	if(index<0) return;
	var record = ag_keymap_store.getAt(index);
	var cmd = record.get('cmd');
	var stop = record.get('stop');
	var cmp = cmd?Ext.getCmp(cmd):undefined;
	if(!cmp) return;
	if(cmp.xtype=='checkbox'){
		cmp.show();
		cmp.setChecked(cmp.checked?false:true)
		cmp.hide();
		if(stop) e.stopEvent();
	}else{
		if(cmp.fireEvent('click',cmp) && stop) e.stopEvent();
	}
}
var agKeyMapNames = [];
var agKeyMapNameToCode = {};
var agKeyMapCodeToName = {};
for(var key in Ext.EventObject){
	if(typeof Ext.EventObject[key] != 'number') continue;
	switch (key){
		case 'button':
		case 'A':
		case 'B':
		case 'C':
		case 'D':
		case 'E':
		case 'F':
		case 'G':
		case 'H':
		case 'I':
		case 'J':
		case 'K':
		case 'L':
		case 'M':
		case 'N':
		case 'O':
		case 'P':
		case 'Q':
		case 'R':
		case 'S':
		case 'T':
		case 'U':
		case 'V':
		case 'W':
		case 'X':
		case 'Y':
		case 'Z':
		case 'ZERO':
		case 'ONE':
		case 'TWO':
		case 'THREE':
		case 'FOUR':
		case 'FIVE':
		case 'SIX':
		case 'SEVEN':
		case 'EIGHT':
		case 'NINE':
		case 'NUM_ZERO':
		case 'NUM_ONE':
		case 'NUM_TWO':
		case 'NUM_THREE':
		case 'NUM_FOUR':
		case 'NUM_FIVE':
		case 'NUM_SIX':
		case 'NUM_SEVEN':
		case 'NUM_EIGHT':
		case 'NUM_NINE':
		case 'ALT':
		case 'CONTROL':
		case 'SHIFT':
			continue
	}
	agKeyMapNames.push(key);
	agKeyMapCodeToName[Ext.EventObject[key]] = key;
	agKeyMapNameToCode[key] = {
		code : Ext.EventObject[key]
	};
}
agKeyMapNames.sort();

var agKeyMap;
function agKeyMapExec(){
	if(window.agKeyMap){
		window.agKeyMap.disable();
		window.agKeyMap = undefined;
		delete window.agKeyMap;
	}
	var hash = {};
	var hash_key;
	var KeyMapConfig = [];
	var len = ag_keymap_store.getCount();
	var i;
	for(i=0;i<len;i++){
		var record = ag_keymap_store.getAt(i);
		var key = record.get('key');
		var code = Ext.EventObject[key];
		var shift = record.get('shift');
		var ctrl = record.get('ctrl');
		var alt = record.get('alt');
		var stop = record.get('stop');
//		_dump("["+i+"]:["+key+"]["+code+"]["+shift+"]["+ctrl+"]["+alt+"]["+stop+"]");
		hash_key = code;
		hash_key += '	'+shift;
		hash_key += '	'+ctrl;
		hash_key += '	'+alt;
		hash_key += '	'+stop;
		if(hash[hash_key]) continue;
		KeyMapConfig.push({
			key       : code,
			shift     : shift,
			ctrl      : ctrl,
			alt       : alt,
			fn        : agKeyMapCB,
			scope     : this,
			stopEvent : stop
		});
		hash[hash_key] = true;
	}
	window.agKeyMap = new Ext.KeyMap(document, KeyMapConfig);
	KeyMapConfig = undefined;
}
agKeyMapExec();
