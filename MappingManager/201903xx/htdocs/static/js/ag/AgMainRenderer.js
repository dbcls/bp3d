//Ext.onReady(function() {
function AgMainRenderer(){
	var self = this;

	var DEBUG = (window.top===window);

	var subRenderer = null;
	var testRenderer = null;

	var css2DRenderer = null;
	var css3DRenderer = null;

	var SCREEN_WIDTH = window.innerWidth;
	var SCREEN_HEIGHT = window.innerHeight;
	var FLOOR = -250;
	var aspectRatio = SCREEN_WIDTH / SCREEN_HEIGHT;

	var container,
		stats,
		gui,cameraConfig={
			near: 0.1,
			far: 1685*2
		};

	var directionalLight,ambientLight;
	var camera, scene, projector,cameraPerspectiveHelper;
	var axisHelper;
	var agGrid,colorHeatMap;
	var renderer;

	var mesh, geometry;
	var mouse, INTERSECTED;
//	var group_objects = new THREE.Object3D();
//	var group_pins = new THREE.Object3D();
	var group_objects = new THREE.Group();
	var group_pins = new THREE.Group();
	var group_legend = new THREE.Group();

	var group_labels  = [];
	var voxelPosition = new THREE.Vector3(), tmpVec = new THREE.Vector3();

	var canvas_contextmenu;
	var _bp3d_image_window;


	var isUserInteracting = false,
	isShiftKey = false,
	minFov = 0.05,
	onMouseDownMouseX = 0,
	onMouseDownMouseY = 0,
	lon = 90, onMouseDownLon = 0,
	lat = 0, onMouseDownLat = 0,
	phi = 0, theta = 0,
	distance = -10000,
	initMax = new THREE.Vector3(),
	initMin = new THREE.Vector3(),
	initCenter = new THREE.Vector3(),
	initPosition = new THREE.Vector3(),
	initTarget = new THREE.Vector3(),
	initUp = new THREE.Vector3(),
	target = new THREE.Vector3();

	target.x = -0.622;
	target.y = -960.5107;
	target.z = 828.6308;

	target.x = 0;
	target.y = 0;
	target.z = 828.6308;

	var path2meshs = {};
	var zoom = 0;

	self.getMesh = function(path){
		return path2meshs[path];
	}
	self.setMesh = function(path,mesh){
		return path2meshs[path] = mesh;
	}
	self.isEmptyMesh = function(path){
		return Ext.isEmpty(self.getMesh(path));
	}

	function setMeshVisible(path,visible){
		if(self.isEmptyMesh(path)) return;
		self.getMesh(path).visible = visible;
	}

	//var jsonLoader = new THREE.JSONLoader(true);
	var objLoader = new THREE.OBJLoader();
//	var vtkLoader = new THREE.VTKLoader();

	var objLoaderCB = null;
	if(Number(THREE.REVISION)>=51){
	}

	function getOrthoParam(SCREEN_SIZE){
		var m_bBoxLeft = SCREEN_SIZE / -2;
		var m_bBoxRight = SCREEN_SIZE / 2;
		var m_bBoxTop = SCREEN_SIZE / 2;
		var m_bBoxBottom = SCREEN_SIZE / -2;


		var wi = m_bBoxRight - m_bBoxLeft;
		var hi = m_bBoxTop - m_bBoxBottom;
		if ((wi <= 0) || (hi <= 0)) {
			return undefined;
		}
		var le = -wi/2;
		var ri =  wi/2;
		var bo = -hi/2;
		var to =  hi/2;
		var baspect = wi / hi;
		if ( baspect > aspectRatio ) {
			bo = -((wi/2) / aspectRatio);
			to =  ((wi/2) / aspectRatio);
		}else{
			le = -((hi/2) * aspectRatio);
			ri =  ((hi/2) * aspectRatio);
		}
		var totalRatio = 1;

		var ne = m_persNear;
		var fa = m_persFar;

		return {
			left   : le * totalRatio,
			right  : ri * totalRatio,
			bottom : bo * totalRatio,
			top    : to * totalRatio,
	//		near   : 0.1,
	//		far    : 10000
			near   : cameraConfig.near,
			far    : cameraConfig.far
		};
	}

	function chengeZoom(){
		var yrange = getZoomYRange(zoom);
		var param = getOrthoParam(yrange);

		if(
			camera.left   != param.left ||
			camera.right  != param.right ||
			camera.top    != param.top ||
			camera.bottom != param.bottom ||
			camera.near   != param.near ||
			camera.far    != param.far
		){
			camera.left = param.left;
			camera.right = param.right;
			camera.top = param.top;
			camera.bottom = param.bottom;
			camera.near = param.near;
			camera.far = param.far;

			cameraUpdate();

			Ext.getCmp('zoom-value-text').setValue(Math.round(zoom*5-0.5)+1);
		}
	}

	function cameraUpdate(){
	//	console.log("cameraUpdate():["+SCREEN_WIDTH+"]["+SCREEN_HEIGHT+"]");
		camera.updateProjectionMatrix();
		if(cameraPerspectiveHelper) cameraPerspectiveHelper.update(camera);
		if(agGrid) agGrid.update(SCREEN_WIDTH,SCREEN_HEIGHT);
		if(colorHeatMap) colorHeatMap.update();
		camera.lookAt( target );
//		directionalLight.position.copy(camera.position);
//		directionalLight.target.position.copy(target);
		renderer.render( scene, camera );
	}

	function init(containerElem) {
		if(Ext.isEmpty(containerElem)){
			container = document.createElement( 'div' );
			document.body.appendChild( container );
		}else{
			container = containerElem;
		}
		SCREEN_WIDTH = container.offsetWidth;
		SCREEN_HEIGHT = container.offsetHeight;
		aspectRatio = SCREEN_WIDTH / SCREEN_HEIGHT;
//	console.log("["+SCREEN_WIDTH+"]["+SCREEN_HEIGHT+"]["+aspectRatio+"]");




		var param = getOrthoParam(1800);

//	var dist = 800;
//	var dist = 7900;
//	var fov = 2 * Math.atan( 1800 / ( 2 * dist ) ) * ( 180 / Math.PI );
//	console.log("fov=["+fov+"]");
//	camera = new THREE.CombinedCamera( 1800, 1800, fov, param.near, param.far, param.near, param.far );
//	camera.toOrthographic();

		camera = new THREE.OrthographicCamera(param.left, param.right, param.top, param.bottom, param.near, param.far );

		setCameraAndTarget(m_ag_initCameraPos,m_ag_initTargetPos,m_ag_initUpVec,true);

		camera.position.copy(m_ag_cameraPos);
		camera.up.copy(m_ag_upVec);
		target.copy(m_ag_targetPos);
		camera.lookAt( target );
		camera.updateProjectionMatrix();


//	cameraPerspectiveHelper = new THREE.CameraHelper( camera );
//	camera.add( cameraPerspectiveHelper );

		agGrid = new AgGrid( camera );
		colorHeatMap = new AgColorHeatMap( camera );

		scene = new THREE.Scene();

		scene.add( camera );

//	axisHelper = new THREE.AxisHelper();
//	scene.add( axisHelper );


		// LIGHTS
		ambientLight = new THREE.AmbientLight( 0x221d16 );
		scene.add( ambientLight );

		directionalLight = new THREE.DirectionalLight( 0xffffff);

		directionalLight.position.copy(camera.position);
		directionalLight.target.position.copy(target);
//		camera.add( directionalLight );
		scene.add( directionalLight );
		scene.add( directionalLight.target );

//	group_objects = new THREE.Object3D();
		scene.add(group_objects);
		scene.add(group_pins);
//		scene.add(group_legend);

//	scene.add(group_labels);



//		projector = new THREE.Projector();

//	geometry = new THREE.Geometry();
//	geometry.vertices.push( new THREE.Vector3( target ) );

//	var line = new THREE.Line( geometry, new THREE.LineBasicMaterial( { color: 0xff0000, opacity: 0.8 } ) );
//	scene.add( line );



		// RENDERER

		if ( ! Detector.webgl ) Detector.addGetWebGLMessage();

		var rendererParam = {
			antialias: true,
			maxLights: 6,
			clearAlpha: 1,
			preserveDrawingBuffer: true,
//			logarithmicDepthBuffer: true
		};

		if(Detector.webgl){
			renderer = new THREE.WebGLRenderer(rendererParam);
		}else{
			renderer = new THREE.CanvasRenderer(rendererParam);
		}
		renderer.setSize( SCREEN_WIDTH, SCREEN_HEIGHT );

		renderer.domElement.style.position = 'absolute';
		renderer.domElement.style.left = '0px';
		renderer.domElement.style.top = '0px';
		container.appendChild( renderer.domElement );
/*
		css2DRenderer = new THREE.CSS2DRenderer();
		css2DRenderer.setSize( SCREEN_WIDTH, SCREEN_HEIGHT );
		css2DRenderer.domElement.style.position = 'absolute';
		css2DRenderer.domElement.style.left = '0px';
		css2DRenderer.domElement.style.top = '0px';
		css2DRenderer.domElement.style.pointerEvents = 'none';
		container.appendChild( css2DRenderer.domElement );

		css3DRenderer = new THREE.CSS3DRenderer();
		css3DRenderer.setSize( SCREEN_WIDTH, SCREEN_HEIGHT );
		css3DRenderer.domElement.style.position = 'absolute';
		css3DRenderer.domElement.style.left = '0px';
		css3DRenderer.domElement.style.top = '0px';
		css3DRenderer.domElement.style.pointerEvents = 'none';
		container.appendChild( css3DRenderer.domElement );
*/

//	stats = new Stats();
//	stats.domElement.style.position = 'absolute';
//	stats.domElement.style.top = '0px';
//	stats.domElement.style.right = '0px';
//	stats.domElement.style.zIndex = 100;
//	container.appendChild( stats.domElement );
//	Ext.get(stats.domElement).setVisibilityMode(Ext.dom.Element.OFFSETS);
//	if(!Ext.getCmp('options-stats').checked) Ext.get(stats.domElement).setVisible(false);


//	gui = new DAT.GUI();
//	gui.add( cameraConfig, 'near', 0.1, 10000, 0.1 ).onChange( function() {
//		camera.near = cameraConfig.near;
//		camera.far = cameraConfig.far;
//		cameraUpdate();
//	});
//	gui.add( cameraConfig, 'far', 0.1, 10000, 0.1 ).onChange( function() {
//		camera.near = cameraConfig.near;
//		camera.far = cameraConfig.far;
//		cameraUpdate();
//	});
//	gui.close();


		container.addEventListener( 'mousedown', onDocumentMouseDown, false );
		container.addEventListener( 'dblclick', onDocumentDblClick, false );
		container.addEventListener( 'touchstart', onDocumentTouchStart, false );

		if(Ext.isGecko){
			container.addEventListener( 'DOMMouseScroll', onDocumentMouseWheel, false );
		}else{
			container.addEventListener( 'mousewheel', onDocumentMouseWheel, false );
		}

//		$(container).bind( 'mousemove', onObjectMouseMove);

//	document.addEventListener( 'mousemove', onObjectMouseMove. false);
		$(container).bind( 'contextmenu', onObjectContextMenu);


		document.addEventListener( 'touchmove', onDocumentTouchMove, false );
//	document.addEventListener( 'keydown', onDocumentKeyDown, false );
//	document.addEventListener( 'keyup', onDocumentKeyUp, false );

		if(window.parent != window){
			$(document).bind('keydown', function(e,o){onDocumentKeyDown(o||e);});
			$(document).bind('keyup',   function(e,o){onDocumentKeyUp(o||e);});
		}else{
			document.addEventListener( 'keydown', onDocumentKeyDown, false );
			document.addEventListener( 'keyup', onDocumentKeyUp, false );
		}

//	var field = Ext.getCmp('camera-near');
//	if(field) $(window).trigger('changeCameraNear',[field.value]);
//	var field = Ext.getCmp('camera-far');
//	if(field) $(window).trigger('changeCameraFar',[field.value]);

		hashChangeAddEventListenerTask.delay(0);
	}


	function onDocumentKeyDown( event ){
	//	console.log("onDocumentKeyDown():["+event.keyCode?event.keyCode:'???'+"]");
		if(!event || !event.keyCode || Ext.isEmpty(event.keyCode)) return;

	//				event.preventDefault();
		isAltKey = event.altKey;
		isShiftKey = event.shiftKey;
		isControlKey = event.ctrlKey;
		var isUpdate = false;
		switch (event.keyCode){
			case 37 : //Left
	//			setCameraAndTarget(camera.position, target, camera.up, true);
				addLongitude(5);
				isUpdate = true;
				break;
			case 38 : //Up
	//			setCameraAndTarget(camera.position, target, camera.up, true);
				addLatitude(-5);
				isUpdate = true;
				break;
			case 39 : //Right
	//			setCameraAndTarget(camera.position, target, camera.up, true);
				addLongitude(-5);
				isUpdate = true;
				break;
			case 40 : //Down
	//			setCameraAndTarget(camera.position, target, camera.up, true);
				addLatitude(5);
				isUpdate = true;
				break;
		}
		if(isUpdate){
			event.preventDefault();
			camera.position.copy(m_ag_cameraPos);
			camera.up.copy(m_ag_upVec);
			target.copy(m_ag_targetPos);
			updateCameraHash();

	/*
		var dir = camera.up.clone();
		var self = new THREE.Object3D();
		var axis = new THREE.Vector3( 0, 1, 0 ).crossSelf( dir );
		var radians = Math.acos( new THREE.Vector3( 0, 1, 0 ).dot( dir.clone().normalize() ) );
		self.matrix = new THREE.Matrix4().makeRotationAxis( axis.normalize(), radians );
		self.rotation.setEulerFromRotationMatrix( self.matrix, self.eulerOrder );
	//	console.log(self);
	//	console.log(camera.position);
	//	console.log(camera.up);
	//	console.log(target);
		var rad = self.rotation.y;
		var deg = rad * 180 / Math.PI;
	//	console.log(deg);
	*/
	/*
		var dummy = new THREE.Object3D();
		scene.add(dummy);
		dummy.rotation.setEulerFromRotationMatrix( camera.matrix, dummy.eulerOrder );

		console.log(camera.rotation);
		console.log("x=["+(camera.rotation.x * 180 / Math.PI)+"]["+Math.round(camera.rotation.x * 180 / Math.PI)+"]");
		console.log("y=["+(camera.rotation.y * 180 / Math.PI)+"]["+Math.round(camera.rotation.y * 180 / Math.PI)+"]");
		console.log("z=["+(camera.rotation.z * 180 / Math.PI)+"]["+Math.round(camera.rotation.z * 180 / Math.PI)+"]");

		console.log(dummy.rotation);
		console.log("x=["+(dummy.rotation.x * 180 / Math.PI)+"]["+Math.round(dummy.rotation.x * 180 / Math.PI)+"]");
		console.log("y=["+(dummy.rotation.y * 180 / Math.PI)+"]["+Math.round(dummy.rotation.y * 180 / Math.PI)+"]");
		console.log("z=["+(dummy.rotation.z * 180 / Math.PI)+"]["+Math.round(dummy.rotation.z * 180 / Math.PI)+"]");

		scene.remove(dummy);
	*/



		}
		return false;
	}

	function onDocumentKeyUp( event ){
	//				console.log("onDocumentKeyUp()");
		isAltKey = false;
		isShiftKey = false;
		isControlKey = false;

		var isUpdate = false;
		switch (event.keyCode){
			case 37 : //Left
				isUpdate = true;
				break;
			case 38 : //Up
				isUpdate = true;
				break;
			case 39 : //Right
				isUpdate = true;
				break;
			case 40 : //Down
				isUpdate = true;
				break;
		}
		if(isUpdate){
			event.preventDefault();
		}
	}

	function getMouseXY(event){
		var xy = Ext.get(renderer.domElement).getXY();
		return new THREE.Vector2(event.clientX-xy[0],event.clientY-xy[1]);
	}

	function onDocumentMouseDown( event ) {
		if(event.button == 0 || event.which == 1){
			event.preventDefault();

			isUserInteracting = false;
			isShiftKey = event.shiftKey;
		//	console.log("["+isShiftKey+"]");

			var mouseXY = getMouseXY(event);
			onPointerDownPointerX = mouseXY.x;
			onPointerDownPointerY = mouseXY.y;

			var tmpDeg = calcRotateDeg();
			onPointerDownH = tmpDeg.H;
			onPointerDownV = tmpDeg.V;

//			console.log('addEventListener(mousemove)');
			document.addEventListener( 'mousemove', onDocumentMouseMove, false );
			document.addEventListener( 'mouseup', onDocumentMouseUp, false );
		}
	}

	var intersect_target_objects = [];
	var intersect_target_objects_all = [];

	function getIntersectObjects(mouseXY,all){
		console.log('getIntersectObjects()',mouseXY);
		console.log('getIntersectObjects()',[SCREEN_WIDTH,SCREEN_HEIGHT]);

//		var mouseVec = new THREE.Vector3(
		var mouseVec = new THREE.Vector2(
			(   mouseXY.x / SCREEN_WIDTH  ) * 2 - 1,
			- ( mouseXY.y / SCREEN_HEIGHT ) * 2 + 1
		);

		console.log('getIntersectObjects()',mouseVec);
		console.log('getIntersectObjects()',camera.position,camera.up);

		var raycaster = new THREE.Raycaster();
		raycaster.setFromCamera( mouseVec, camera );

		var target_objects;
		if(all){
			target_objects = intersect_target_objects_all;
		}else{
			target_objects = intersect_target_objects;
		}

		jQuery.each(target_objects,function(){
			this.material.side = THREE.DoubleSide;
		});

		var intersects = raycaster.intersectObjects( target_objects );

		jQuery.each(target_objects,function(){
			this.material.side = THREE.FrontSide;
		});

		var intersects_arr = [];
		jQuery.each(intersects,function(){


			var AG_MARKER_MANAGER_ARROW_RATIO = 0.01;

			var arw = new AGVec3d();
			var tarPos = this.point.clone();
			AGDifferenceD3( tarPos, m_ag_cameraPos, arw );
			var arwlen = arw[AG_X]*arw[AG_X] + arw[AG_Y]*arw[AG_Y] + arw[AG_Z]*arw[AG_Z];
			arwlen = Math.sqrt( arwlen ) * AG_MARKER_MANAGER_ARROW_RATIO;
			AGNormalizeD3( arw, arw );
			AGMultD3( arw, arwlen );

			var ratio = 0.5;
			var numVerts = 10;
			var upVec = m_ag_upVec.clone();
			var cone = new AG.CAg3DCone( 'id' ).createData(
				tarPos,
				arw,
				upVec,
				ratio,
				numVerts
			);

			this.AGPin = {
				Pin: tarPos.clone(),
				PinArrowVector: arw.clone(),
				PinUpVector: upVec.clone()
			};
//			console.log(this);

			intersects_arr.push(this);
		});
		return intersects_arr.length>0 ? intersects_arr : undefined;
	}

	function convertCoordinateScreenTo3D(screenXY){
		var vec2 = new THREE.Vector2(
			  ( screenXY.x / SCREEN_WIDTH  ) * 2 - 1,
			- ( screenXY.y / SCREEN_HEIGHT ) * 2 + 1
		);
		var s_vec3 = new THREE.Vector3( vec2.x, vec2.y, -1.0 );
		var e_vec3 = new THREE.Vector3( vec2.x, vec2.y, 1.0 );
//		s_vec3 = projector.unprojectVector( s_vec3, camera );
		s_vec3.unproject( camera );
//		e_vec3 = projector.unprojectVector( e_vec3, camera );
		e_vec3.unproject( camera );
		e_vec3.subSelf( s_vec3 ).normalize();
		return e_vec3.multiplyScalar(s_vec3.y / - ( e_vec3.y )).addSelf(s_vec3);
	}

	function convertCoordinate3DToScreen(position) {
		var xy = Ext.get(renderer.domElement).getXY();
		var pos = position.clone();
		var projScreenMat = new THREE.Matrix4();

		projScreenMat.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse);
		pos.applyProjection(projScreenMat);

		return new THREE.Vector2(
			(  pos.x + 1) * SCREEN_WIDTH  / 2 + xy[0],
			(- pos.y + 1) * SCREEN_HEIGHT / 2 + xy[1]
		);
	}

	var tipTask = new Ext.util.DelayedTask();
	var objTip = null;
	var prevMouseXY = null;
	function onObjectMouseMove(event){
		var mouseXY = getMouseXY(event);
		if(Ext.isEmpty(prevMouseXY)) prevMouseXY = mouseXY.clone();
		tipTask.delay(250,function(event){
			if(!Ext.getCmp('options-tooltip').checked) return;
			var intersects = getIntersectObjects(mouseXY);
			if(Ext.isEmpty(intersects)){
				if(!objTip.isHidden()) objTip.hide();
			}else{
				var xy = [event.clientX,event.clientY];
				var text = '';
				if(!Ext.isEmpty(intersects[0].object.record.get('art_id'))) text += '<h3>['+intersects[0].object.record.get('art_id')+']</h3>';
				text += intersects[0].object.record.get('art_name');
	/*
				if(!Ext.isEmpty(intersects[0].object.geometry.boundingBox)){
					var num_fmt = '0.000';
					var func = Ext.util.Format.number;
					var bb = intersects[0].object.geometry.boundingBox;
					var st = 'style="text-align:right;padding:0 4px;"';
					text += '<hr>';
					text += '<table><tbody>';
					text += '<tr><td></td><td align="center">Max</td><td align="center">Min</td></tr>';
					text += '<tr><td>X:</td><td '+st+'>'+ func(bb.max.x, num_fmt) +'</td><td '+st+'>'+ func(bb.min.x, num_fmt) +'</td></tr>';
					text += '<tr><td>Y:</td><td '+st+'>'+ func(bb.max.y, num_fmt) +'</td><td '+st+'>'+ func(bb.min.y, num_fmt) +'</td></tr>';
					text += '<tr><td>Z:</td><td '+st+'>'+ func(bb.max.z, num_fmt) +'</td><td '+st+'>'+ func(bb.min.z, num_fmt) +'</td></tr>';
					text += '</tbody></table>';
				}
	*/
				objTip.update(text,false,function(){
					xy[0]+=4;
					xy[1]-=(objTip.getHeight()+4);
					objTip.showAt(xy);
				});
			}
		},this,[event]);
		if(!objTip.isHidden() && prevMouseXY.distanceTo(mouseXY)>0) objTip.hide();
		prevMouseXY = mouseXY.clone();
	}

	var objectContextMenuCB = function(type){
		var eve = new jQuery.Event(type);
		var data = Ext.apply({},INTERSECTED.object.record.data);
		$(window).trigger(eve,[data]);
		if(!Ext.isEmpty(INTERSECTED) && !Ext.isEmpty(eve.result) && eve.result!==false){
			INTERSECTED.object.material.color.setHex( Ext.isNumber(eve.result) ? eve.result : 0xdd0000 );
			INTERSECTED.result = eve.result;
			INTERSECTED = null;
		}
	};
	var objectContextMenu = Ext.create('Ext.menu.Menu', {
		width: 100,
		plain: true,
		renderTo: Ext.getBody(),  // usually rendered by it's containing component
		items: [{
			iconCls: 'minus-btn',
			text: 'hide parts',
			handler: function(i,e){
				objectContextMenuCB('hideParts');
			}
		},{
			iconCls: 'plus-btn',
			text: 'add pallet',
			id: 'add-pallet-menu',
			handler: function(i,e){
				objectContextMenuCB('addPalletParts');
			}
		}]
	});

	function onObjectContextMenu(event){
		//動作が複雑になる為、とりあえず非表示
		event.preventDefault();
		event.stopPropagation();
		return false;


	//	if(Ext.isEmpty(INTERSECTED) || INTERSECTED.result===true ) return true;
		if(Ext.isEmpty(INTERSECTED)) return true;

		Ext.getCmp('add-pallet-menu').show();
		if(INTERSECTED.result===true ) Ext.getCmp('add-pallet-menu').hide();

		objectContextMenu.showAt([event.clientX+2,event.clientY+2]);

		event.preventDefault();
		event.stopPropagation();
		return false;

	}

	function onDocumentMouseMove(event){
		var mouseXY = getMouseXY(event);
		var dX = mouseXY.x - onPointerDownPointerX;
		var dY = mouseXY.y - onPointerDownPointerY;
		if(dX || dY){	//Windows7以降では、mousemoveイベントが発生する為

			isUserInteracting = true;
			isShiftKey = event.shiftKey;

			if(isShiftKey){
				var degH = Math.round(onPointerDownH/15)*15;
				degH = degH - 15 * Math.floor(dX / 20);
				while (degH >= 360) {
					degH = degH - 360;
				}
				while (degH < 0) {
					degH = degH + 360;
				}
				// rotateV
				var degV = Math.round(onPointerDownV/15)*15;
				degV = degV + 15 * Math.floor(dY / 20);
				while (degV >= 360) {
					degV = degV - 360;
				}
				while (degV < 0) {
					degV = degV + 360;
				}

				if(onPointerDownH != degH || onPointerDownV != degV){
					if(onPointerDownH != degH){
						m_ag_longitude += (-5 * Math.floor(dX / 20));
						onPointerDownPointerX = mouseXY.x;
					}
					if(onPointerDownV != degV){
						m_ag_latitude  += (5 * Math.floor(dY / 20));
						onPointerDownPointerY = mouseXY.y;
					}
					m_ag_longitude = Math.round(m_ag_longitude/5)*5;
					m_ag_latitude = Math.round(m_ag_latitude/5)*5;

					calcCameraPos();

					camera.position.copy(m_ag_cameraPos);
					camera.up.copy(m_ag_upVec);
					target.copy(m_ag_targetPos);

					onPointerDownH = degH;
					onPointerDownV = degV;


				}

			}else{

				moveTargetByMouseForOrtho(dX,dY);

				camera.position.copy(m_ag_cameraPos);
				camera.up.copy(m_ag_upVec);
				target.copy(m_ag_targetPos);

				onPointerDownPointerX = mouseXY.x;
				onPointerDownPointerY = mouseXY.y;

			}

			render();
		}
	}

	function onDocumentMouseUp( event ) {
		if(!isUserInteracting){
			event.preventDefault();

			var mouseXY = getMouseXY(event);
			mouse = mouseXY;

			Ext.defer(function(){

				initINTERSECTED();

				var intersects = getIntersectObjects(mouse,event.ctrlKey);
				var clickmode = Ext.getCmp('click-mode-menu').getActiveItem().value;
				if(clickmode == 'clickmode.pick'){
					var p_route = [];
					if(!Ext.isEmpty(intersects) && intersects[0].distance<Math.abs(camera.far-camera.near)){
						INTERSECTED = intersects[0];
						var record = INTERSECTED.object.record;
						if(record){

							function makePickRecord(record){
								var param = {};
								for(var key in record.data){
									if(
										Ext.isBoolean(record.data[key]) ||
										Ext.isDate(record.data[key]) ||
										Ext.isNumber(record.data[key]) ||
										Ext.isString(record.data[key])
									){
										param[key] = record.data[key];
									}
								}
								param.selected = false;
								param.color = DEF_COLOR;
								param.opacity = 1.0;
								param.remove = false;
								param.representation = 'surface';
								param.scalar = null;
								param.scalar_flag = false;
								return Ext.create('RENDERER',param);
							}

							var jsonObj = getLocaleHashObj();
							var p_tree = jsonObj.Common.TreeName;
							var p_record = makePickRecord(record);
							p_route.push([p_record]);

						}
					}
					var e = new jQuery.Event('pickObject');
					$(window).trigger(e,[INTERSECTED,p_route]);
					if(!Ext.isEmpty(INTERSECTED) && !Ext.isEmpty(e.result) && e.result!==false){
						INTERSECTED.object.currentHex = INTERSECTED.object.material.color.getHex();
						INTERSECTED.object.material.color.setHex( Ext.isNumber(e.result) ? e.result : 0xdd0000 );
						INTERSECTED.result = e.result;
					}
					render();
				}else if(clickmode == 'clickmode.pin'){
					var e = new jQuery.Event('pinObject');
					$(window).trigger(e,[intersects]);
					if(!Ext.isEmpty(intersects) && !Ext.isEmpty(e.result) && e.result!==false){
	//					console.log("pinObject!!!");
	//					console.log(e);
	//					console.log(e.isDefaultPrevented());
	//					console.log(e.isImmediatePropagationStopped());
	//					console.log(e.isPropagationStopped());
					}
				}
				mouse = undefined;

			},0);

		}else{
			mouse = undefined;
		}

		isUserInteracting = false;
		isShiftKey = false;
	//				render();

//		console.log('removeEventListener(mousemove)');
		document.removeEventListener( 'mousemove', onDocumentMouseMove, false );
		document.removeEventListener( 'mouseup', onDocumentMouseUp, false );

		updateCameraHash();
	}

	function initINTERSECTED(){
		if(INTERSECTED){
			if(INTERSECTED.object.record){
				var color = INTERSECTED.object.record.get('color');
				if(color.substr(0,1) == '#') color = color.substr(1);
				color = Number('0x'+color);
				INTERSECTED.object.material.color.setHex( color );
			}else{
				INTERSECTED.object.material.color.setHex( INTERSECTED.object.currentHex );
			}
		}
		INTERSECTED = null;
	};

	function onDocumentDblClick( event ) {
	//	console.log("onDocumentDblClick()");

		initINTERSECTED();

		mouse = undefined;

	//	setCameraAndTarget(camera.position, target, camera.up, true);

		var mouseXY = getMouseXY(event);
		anatomoImgMoveCenter(mouseXY.x,mouseXY.y);

	}

	function onDocumentMouseWheel( event ) {
//	console.log("onDocumentMouseWheel()");

//		console.log({
//			wheelDeltaY: event.wheelDeltaY,
//			wheelDelta: event.wheelDelta,
//			detail: event.detail
//		});

		var mouseXY = getMouseXY(event);
		var mouseX = mouseXY.x;
		var mouseY = mouseXY.y;

		var centerX = parseInt((SCREEN_WIDTH /2) -  mouseX);
		var centerY = parseInt((SCREEN_HEIGHT /2) - mouseY);
		var moveX = parseInt(mouseX - (SCREEN_WIDTH /2));
		var moveY = parseInt(mouseY - (SCREEN_HEIGHT /2));
//	setCameraAndTarget(camera.position, target, camera.up, true);
		moveTargetByMouseForOrtho(centerX, centerY);
		camera.position.copy(m_ag_cameraPos);
		camera.up.copy(m_ag_upVec);
		target.copy(m_ag_targetPos);

		if(event.wheelDeltaY != undefined){
			zoom += event.wheelDeltaY>0 ? 0.2 : -0.2;
		}else if(event.wheelDelta != undefined){
			zoom += event.wheelDelta>0 ? 0.2 : -0.2;
		}else if(event.detail != undefined){// IEにもevent.detailが存在する為、最後に判定する
			zoom += event.detail>0 ? -0.2 : 0.2;
		}
		if(zoom>19.8) zoom = 19.8;
		if(zoom<0)   zoom = 0;

		chengeZoom();

		moveTargetByMouseForOrtho(moveX, moveY);
		camera.position.copy(m_ag_cameraPos);
		camera.up.copy(m_ag_upVec);
		target.copy(m_ag_targetPos);

		camera.updateProjectionMatrix();

		updateCameraHash();
	}

	function onDocumentTouchStart( event ) {

		if ( event.touches.length == 1 ) {

			event.preventDefault();

			onPointerDownPointerX = event.touches[ 0 ].pageX;
			onPointerDownPointerY = event.touches[ 0 ].pageY;

			onPointerDownLon = lon;
			onPointerDownLat = lat;

		}

	}

	function onDocumentTouchMove( event ) {

		if ( event.touches.length == 1 ) {

			event.preventDefault();

			lon = ( onPointerDownPointerX - event.touches[0].pageX ) * 0.1 + onPointerDownLon;
			lat = ( event.touches[0].pageY - onPointerDownPointerY ) * 0.1 + onPointerDownLat;

	//					render();

		}

	}


	function animate() {

		requestAnimationFrame( animate );

		render();
		if(stats) stats.update();
	}

	//var t=0;
	function render(param) {
		param = param || {};

	//	if(INTERSECTED) console.log('render():0x'+INTERSECTED.object.material.color.getHex().toString(16));

	//				console.log("render_def()");

	//t++;
	//camera.position.set( 400*Math.cos(t/100), 400*Math.sin(t/200) - 900, 50*Math.cos(t/50));
	//camera.position.setX( 400*Math.cos(t/100) );
	//camera.position.setZ(  50*Math.cos(t/50)  );

		camera.lookAt( target );

		//ライトの位置もカメラの座標に更新
		directionalLight.position.copy(camera.position);
		directionalLight.target.position.copy(target);


	//				renderer.clear();
	//				renderer.setViewport(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT );
		renderer.render( scene, camera );
		if(css2DRenderer) css2DRenderer.render( scene, camera );
		if(css3DRenderer) css3DRenderer.render( scene, camera );


		var $canvas2D = $('#canvas2D');
		var canvas2D = $canvas2D.get(0);
		var ctx = canvas2D && canvas2D.getContext ? canvas2D.getContext('2d') : undefined;
		if(ctx){
			var font = $canvas2D.css('font');
			var fontSize = Number($canvas2D.css('font-size').replace(/[^0-9]+/,""));
	//		console.log(font);

			ctx.clearRect(0,0,$canvas2D.width(),$canvas2D.height());
			ctx.font = font;
			ctx.textAlign = 'left';
			ctx.textBaseline = 'top';
			ctx.fillStyle = '#000000';
			ctx.globalAlpha = 1;

			if(param.DrawLegendFlag!==false){
				$('#legend-draw-area').show();
				$('#legend-draw-area>div>span').each(function(){
					var $span = $(this);
					var org_css = {};
					jQuery.each(['color','font-style','font-weight'],function(){
						var key;
						if(typeof this == 'object'){
							key = this.toString();
						}else if(typeof this == 'string'){
							key = this;
						}
						if(!key) return true;
						org_css[key] = $span.css(key);
					});
					$span.css({
						'font':font,
						'white-space':'nowrap'
					});
					jQuery.each(org_css,function(key,val){
						$span.css(key,val);
					});

					var offset = $span.offset();
					var width = $span.width();
	//				var height = $(this).height();
	//				console.log(ctx.measureText($(this).text()).width);
	//				console.log(offset);
	//				console.log("width=["+width+"]");
	//				console.log("height=["+height+"]");

	//				console.log('#'+$span.attr('LegendColor'));
	//				console.log($span.css('font'));
	//				console.log($span.css('color'));

					ctx.save();
					ctx.font = $span.css('font');
	//				ctx.fillStyle = '#'+$span.attr('LegendColor');
					ctx.fillStyle = $span.css('color');
					ctx.globalAlpha = 1;
					ctx.fillText($span.text(), offset.left, offset.top, width);
					ctx.restore();

				});
			}else{
				$('#legend-draw-area').hide();
			}

	//		jQuery.each(group_pins.children,function(){
	//			if(!this || !this.children) return true;
	//			jQuery.each(this.children,function(){
	//				this.visible = false;
	//			});
	//		});

	//		THREE.SceneUtils.showHierarchy(group_pins,false);
			group_pins.traverse(function(obj){ obj.visible = false; });

			var zoomRate = getZoomYRange(zoom)/1800;
			//console.log("zoomRate=["+zoomRate+"]");

			var labelFont = $canvas2D.css('font-style') + ' ' + $canvas2D.css('font-variant') + ' bold ' + ' ' + $canvas2D.css('font-size') + '/' + $canvas2D.css('line-height') + ' ' + $canvas2D.css('font-family');

	//		var tmpVec = new THREE.Vector3();
			var endPosition = new THREE.Vector3();

			$('#pin-draw-area>div>span').each(function(){
				$(this).css({
					'font':font,
					'white-space':'nowrap'
				});

				var PinVectorX = Number($(this).attr('PinX'));
				var PinVectorY = Number($(this).attr('PinY'));
				var PinVectorZ = Number($(this).attr('PinZ'));
				if(isNaN(PinVectorX) || isNaN(PinVectorY) || isNaN(PinVectorZ)){
					if(isNaN(PinVectorX)) console.warn("PinVectorX is NaN");
					if(isNaN(PinVectorY)) console.warn("PinVectorY is NaN");
					if(isNaN(PinVectorZ)) console.warn("PinVectorZ is NaN");
					return true;
				}
				var PinVector = new THREE.Vector3(PinVectorX,PinVectorY,PinVectorZ);

				var PinArrowVectorX = Number($(this).attr('PinArrowVectorX'));
				var PinArrowVectorY = Number($(this).attr('PinArrowVectorY'));
				var PinArrowVectorZ = Number($(this).attr('PinArrowVectorZ'));
				if(isNaN(PinArrowVectorX) || isNaN(PinArrowVectorY) || isNaN(PinArrowVectorZ)){
					if(isNaN(PinArrowVectorX)) console.warn("PinArrowVectorX is NaN");
					if(isNaN(PinArrowVectorY)) console.warn("PinArrowVectorY is NaN");
					if(isNaN(PinArrowVectorZ)) console.warn("PinArrowVectorZ is NaN");
					return true;
				}
				var PinArrowVector = new THREE.Vector3(PinArrowVectorX,PinArrowVectorY,PinArrowVectorZ);

				var PinUpVectorX = Number($(this).attr('PinUpVectorX'));
				var PinUpVectorY = Number($(this).attr('PinUpVectorY'));
				var PinUpVectorZ = Number($(this).attr('PinUpVectorZ'));
				if(isNaN(PinUpVectorX) || isNaN(PinUpVectorY) || isNaN(PinUpVectorZ)){
					if(isNaN(PinUpVectorX)) console.warn("PinUpVectorX is NaN");
					if(isNaN(PinUpVectorY)) console.warn("PinUpVectorY is NaN");
					if(isNaN(PinUpVectorZ)) console.warn("PinUpVectorZ is NaN");
					return true;
				}
				var PinUpVector = new THREE.Vector3(PinUpVectorX,PinUpVectorY,PinUpVectorZ);

				var PinIndicationLineDrawFlag = Number($(this).attr('PinIndicationLineDrawFlag'));
				if(isNaN(PinIndicationLineDrawFlag)){
					if(isNaN(PinIndicationLineDrawFlag)) console.warn("PinIndicationLineDrawFlag is NaN");
					return true;
				}

				var PinID = $(this).attr('PinID');
				if(Ext.isEmpty(PinID)){
					console.warn("PinID is Empty");
					return true;
				}
				var PinPartID = $(this).attr('PinPartID');
				if(Ext.isEmpty(PinPartID)){
					console.warn("PinPartID is Empty");
					return true;
				}

				var hexPinColor = Number('0x'+$(this).attr('PinColor'));
				var PinShape = $(this).attr('PinShape') || 'CIRCLE';
				var PinVector2 = convertCoordinate3DToScreen(PinVector);
				if(PinIndicationLineDrawFlag==2) endPosition.copy(PinVector);

				ctx.save();
				ctx.font = labelFont;
				ctx.fillStyle = '#'+$(this).attr('PinColor');
				ctx.fillText(PinID, PinVector2.x+5, PinVector2.y+5);
				if(PinShape=='CIRCLE'){
					ctx.strokeStyle = '#'+$(this).attr('PinColor');
					ctx.beginPath();
					ctx.arc(PinVector2.x, PinVector2.y, 5, 0, (360 * Math.PI / 180), false);
					ctx.fill();
					ctx.stroke();
				}
				ctx.restore();

				if(PinShape!='CIRCLE'){
					var lineRate = AgPin.LENGTH_C;
					if(PinShape.match(/^PIN_(.+)$/i)){
						var sizeStr = RegExp.$1;
						if(sizeStr=='LONG'){
							lineRate = AgPin.LENGTH_L;
						}else if(sizeStr=='MIDIUM'){
							lineRate = AgPin.LENGTH_M;
						}else{
							lineRate = AgPin.LENGTH_S;
						}
					}

					var objName = PinPartID+'_agpin';
					var pinObj = group_pins.getObjectByName(objName);
					if(!pinObj){
						pinObj = new AgPin(PinArrowVector,PinVector,hexPinColor);
						pinObj.name = objName;
						group_pins.add(pinObj);
					}else{
						pinObj.position.copy(PinVector);
						pinObj.setDirection(PinArrowVector);
					}
					pinObj.setVisibled(PinShape);
					pinObj.setScale(zoomRate);

					if(PinIndicationLineDrawFlag==2) endPosition.copy(pinObj.getEndPosition(PinArrowVector));
				}

				var PinDescriptionDrawFlag = $(this).attr('PinDescriptionDrawFlag');

				if(PinDescriptionDrawFlag == 'true' && param.PinDescriptionDrawFlag!==false){

					var offset = $(this).offset();
					ctx.save();
					ctx.fillStyle = '#'+$(this).attr('PinDescriptionColor');
					ctx.globalAlpha = 1;
					ctx.fillText($(this).text(), offset.left, offset.top);
					ctx.restore();

					if(PinIndicationLineDrawFlag>0 && param.PinIndicationLineDrawFlag!==0){

						var width = $(this).width();
						var height = $(this).height();

						var x = offset.left+width+fontSize;
						var y = offset.top+height/2;


						var scrVec2 = new THREE.Vector2(
							(   x / SCREEN_WIDTH  ) * 2 - 1,
							- ( y / SCREEN_HEIGHT ) * 2 + 1
						);

						var scrVec3 = new THREE.Vector3( scrVec2.x, scrVec2.y, -1 );
//						projector.unprojectVector( scrVec3, camera );
						scrVec3.unproject( camera );

						var objName = PinPartID+'_agpin_line';
						var pinObj = group_pins.getObjectByName(objName);
						if(!pinObj){
							pinObj = new THREE.Object3D();
							pinObj.name = objName;
							group_pins.add(pinObj);
						}

						var lineKey = PinPartID+'_desc_line';
//						var line = pinObj.getObjectByName(lineKey);
						var line = group_pins.getObjectByName(lineKey);
						if(!line){
							var lineGeo = new THREE.Geometry();
							lineGeo.vertices.push( scrVec3 );
							if(PinIndicationLineDrawFlag==2){
								lineGeo.vertices.push( endPosition.clone() );
							}else{
								lineGeo.vertices.push( PinVector.clone() );
							}
							line = new THREE.Line( lineGeo, new THREE.LineBasicMaterial( { color: 0x000000, opacity: 1, linewidth: 2 } ) );
							line.name = lineKey;
//							pinObj.add( line );
							group_pins.add(line);
						}else{
							line.geometry.vertices[0].copy(scrVec3);
							if(PinIndicationLineDrawFlag==2){
								line.geometry.vertices[1].copy(endPosition);
							}else{
								line.geometry.vertices[1].copy(PinVector);
							}
						}

						line.geometry.dynamic = true;
						line.geometry.computeFaceNormals();
						line.geometry.computeVertexNormals();
						line.geometry.normalsNeedUpdate = true;
						line.geometry.verticesNeedUpdate = true;


	//					console.log("line.geometry.vertices[0]=["+line.geometry.vertices[0].x+"]["+line.geometry.vertices[0].y+"]["+line.geometry.vertices[0].z+"]");
	//					console.log("line.geometry.vertices[1]=["+line.geometry.vertices[1].x+"]["+line.geometry.vertices[1].y+"]["+line.geometry.vertices[1].z+"]");

						line.visible = true;


	/*
						ctx.save();
						ctx.strokeStyle = '#000000';
						ctx.globalAlpha = 0.5;
						ctx.lineWidth = 2;
						ctx.beginPath();
						ctx.moveTo(x, y);
						ctx.lineTo(vec2.x, vec2.y);
						ctx.stroke();
						ctx.restore();
	*/
					}
				}


	/**/
			});

	//pinLine.afterUpdate();

			renderer.render( scene, camera );
		}

	}

	function resize(adjWidth,adjHeight) {
	//	console.log('resize('+adjWidth+','+adjHeight+')');
		if(Ext.isEmpty(renderer)) return;
		SCREEN_WIDTH = adjWidth;
		SCREEN_HEIGHT = adjHeight;
		aspectRatio = SCREEN_WIDTH / SCREEN_HEIGHT;
	//				camera.aspect = adjWidth/adjHeight;

		chengeZoom();

		renderer.setSize( SCREEN_WIDTH, SCREEN_HEIGHT );
		if(css2DRenderer) css2DRenderer.setSize( SCREEN_WIDTH, SCREEN_HEIGHT );
		if(css3DRenderer) css3DRenderer.setSize( SCREEN_WIDTH, SCREEN_HEIGHT );

		$('#canvas2D').attr({
			width  : SCREEN_WIDTH,
			height : SCREEN_HEIGHT
		});

		createLocaleHashStrTask.delay(250);
	}








	var BP3D_C2P_TREE;

	var jsonLoader = {
		_geometry : {},
		load : function(url,CB){
			if(Ext.isEmpty(jsonLoader._geometry[url])){
				Ext.Ajax.request({
					url     : url,
					method  : 'GET',
					disableCaching : true,
					success : function(conn,response,options){
						try{
							var json;
							try{json = Ext.JSON.decode(conn.responseText);}catch(e){console.log(e);}
							if(json){
								var geom = new THREE.Geometry();//形状の設定
								if(
									json.vertices && json.vertices.length &&
									json.indices  && json.indices.length &&
									json.vn  && json.vn.length
								){
									var vertexes = json.vertices,
											indices  = json.indices,
											vn       = json.vn;
									var i,j=0,l=indices.length;
									for(i=0;i<l;i+=3){
										var gvl = geom.vertices.length;
										var face = new THREE.Face3(gvl,gvl+1,gvl+2,new THREE.Vector3());
										for(j=0;j<3;j++){
											var ind = indices[i+j]*3;
	//										geom.vertices.push(new THREE.Vertex(new THREE.Vector3(vertexes[ind+0], vertexes[ind+1], vertexes[ind+2])));
											geom.vertices.push(new THREE.Vector3(vertexes[ind+0], vertexes[ind+1], vertexes[ind+2]));
											face.vertexNormals.push(new THREE.Vector3(vn[ind+0],vn[ind+1],vn[ind+2]));//頂点法線
										}
										geom.faces.push( face );

									}
								}
								geom.mergeVertices();
								geom.computeCentroids();

	//							geom.computeFaceNormals();//面法線未定義の場合、計算する
	//							geom.computeVertexNormals();//頂点法線未定義の場合、計算する

								geom.computeBoundingBox();
								json = undefined;
								jsonLoader._geometry[url] = geom;
								if(CB) (CB)(true,geom);
							}else{
	//							console.log("LOAD:ERR!!");
								if(CB) (CB)(false,conn,response,options);
							}
						}catch(e){
	//						console.log("LOAD:ERR!!:["+e+"]");
							if(CB) (CB)(false,conn,response,options);
						}
					},
					failure : function(conn,response,options){
	//					console.log("LOAD:NG!!");
						if(CB) (CB)(false,conn,response,options);
					}
				});
			}else if(CB){
				setTimeout(function(){ (CB)(true,jsonLoader._geometry[url]); },0);
			}
		}
	};



	var extension_parts_store = Ext.create('Ext.data.ArrayStore', {
		autoDestroy: true,
		model: 'RENDERER',
		storeId: 'extensionPartsStore',
		listeners : {
			add: function(store,records,index,eOpts){
				self.loadBp3dParts.task.delay(250);
			},
			update: function(store,record,operation){
				if(operation==Ext.data.Record.EDIT){
				}else if(operation==Ext.data.Record.COMMIT){
					var path = self.getRecordPath(record);
					if(self.isEmptyMesh(path)){
						if(record.get('selected')) self.loadBp3dParts.task.delay(250);
					}else{
						self.loadBp3dParts.setMeshProp(self.getMesh(path),record);
						self.loadBp3dParts.close();
					}
				}
			}
		}
	});

	var bp3d_parts_store = Ext.create('Ext.data.Store', {
		storeId: 'bp3dPartsStore',
		autoDestroy: true,
		autoLoad: false,
		isLoaded: false,
		model: 'RENDERER',
		sorters: [{
			property: 'art_data_size',
			direction: 'ASC'
		}],
		proxy: {
			type: 'ajax',
			url: 'AgRender-conv-art-id.cgi',
			limitParam : undefined,
			pageParam  : undefined,
			startParam : undefined,
			actionMethods : {
				create : "POST",
				read   : "POST",
				update : "POST",
				destroy: "POST"
			},
			reader: {
				type: 'json',
				root: 'datas',
				totalProperty:'total',
				listeners : {
					exception : function(){
					}
				}
			},
			listeners : {
				metachange : function(){
				}
			}
		},
		listeners : {
			add : function(){
			},
			beforeprefetch : function(){
			},
			beforesync : function(){
			},
			clear : function(){
			},
			datachanged : function(){
			},
			groupchange : function(){
			},
			metachange : function(){
			},
			prefetch : function(){
			},
			refresh : function(){
			},
			remove : function(){
			},
			write : function(){
			},
			beforeload : function(store,operation,eOpts){
				store.isLoaded = false;
				var p = store.getProxy();
				if(p.extraParams){
					if(Ext.isEmpty(window.DEF_VERSION_DATAS)){
						p.extraParams.model = DEF_MODEL;
						p.extraParams.version = DEF_VERSION;
						p.extraParams.ag_data = DEF_AG_DATA;
						p.extraParams.tree = DEF_TREE;
					}else{
						p.extraParams.version_datas = Ext.JSON.encode(DEF_VERSION_DATAS.datas);
					}
				}
			},
			load : function(store,records,options){
				store.isLoaded = true;
				var win = (window.parent ? window.parent : window);
				if(win==window && location.hash.substr(1).length>0) createLocaleHashStrTask.delay(250);

			},
			update  : function(store,record,operation){
				if(operation==Ext.data.Record.EDIT){
				}else if(operation==Ext.data.Record.COMMIT){

					var jsonObj = getLocaleHashObj();
					var p_tree = jsonObj.Common.TreeName;

					var path = self.getRecordPath(record);
					if(record.data.c_num && record.data.c_num[p_tree] && record.data.c_num[p_tree]>0){
						var updateFieldNames = ['selected','color','opacity','remove','focused','representation','scalar','scalar_flag'];

						store.suspendEvents(false);
						for(var i=0;i<record.data.c_num[p_tree];i++){
							var b_id = record.data.children[p_tree][i];
							var r = store.findRecord('b_id',b_id,0,false,true,true);
							if(Ext.isEmpty(r)) continue;
							var path = self.getRecordPath(r);
							var modifiedFieldNames = [];
							r.beginEdit();
							for(var j in updateFieldNames){
								var key = updateFieldNames[j];
								if(r.data[key] !== undefined && record.data[key] !== undefined && record.data[key] !== r.data[key]){
									r.set(key,record.data[key]);
									modifiedFieldNames.push(key);
								}
							}
							if(modifiedFieldNames.length>0){
								r.commit(false);
								r.endEdit(false,modifiedFieldNames);
							}else{
								r.cancelEdit();
							}

							if(!self.isEmptyMesh(path)){
								self.loadBp3dParts.setMeshProp(self.getMesh(path),r);
							}
						}
						store.resumeEvents();

						self.loadBp3dParts.task.delay(250);
						self.loadBp3dParts.addMesh();
						self.loadBp3dParts.close();


					}else{
						if(self.isEmptyMesh(path)){
							if(record.get('selected')) self.loadBp3dParts.task.delay(250);
						}else{
							self.loadBp3dParts.setMeshProp(self.getMesh(path),record);

							self.loadBp3dParts.addMesh();
							self.loadBp3dParts.close();
						}
					}
				}
			}
		}
	});
//	console.log(bp3d_parts_store);

	//z_h:1684.3158
	//y_c:-96.5112
	//var m_ag_initCameraPos = new THREE.Vector3(-0.622, -984.5667, 828.6308);
	var m_ag_initCameraPos = new THREE.Vector3(-1.244, -1780.827, 828.6308);
	var m_ag_cameraPos = new THREE.Vector3(2.7979888916016167, -998.4280435445771, 809.7306805551052);

	//var m_ag_initTargetPos = new THREE.Vector3(-0.622, -96.5107, 828.6308);
	var m_ag_initTargetPos = new THREE.Vector3(-1.244, -96.5112, 828.6308);
	var m_ag_targetPos = new THREE.Vector3(2.7979888916015625, -110.37168800830841, 809.7306805551052);

	var m_ag_initUpVec = new THREE.Vector3(0, 0, 1);
	var m_ag_upVec = new THREE.Vector3(0, 0, 1);
	var m_ag_initDistance = 0;
	var m_ag_distance = 0;
	var m_ag_initLongitude = 0;
	var m_ag_longitude = 0;
	var m_ag_initLatitude = 0;
	var m_ag_latitude = 0;
	var m_ag_orthoYRange = 1800;
	var m_ag_initOrthoYRange = 1800;
	var m_ag_nearClip = 1;
	var m_ag_farClip = 10000;
	var m_ag_epsilon = 0.0000001;
	var m_ag_PI = 3.141592653589793238462643383279;
	var m_ag_Camera_YRange_Min = 1.0;
	var m_ag_fovY = 30.0;
	var m_ag_posDif;

	var m_rotate_h = 0;
	var m_rotate_v = 0;

	//console.log(Math.round((Math.log(1800)/Math.log(2) - Math.log(m_ag_orthoYRange) / Math.log(2)) * 5 -0.5));

	function setRotateHorizontalValue(value) {
		m_rotate_h = (isNaN(value))?0:parseInt(value);
	}

	function setRotateVerticalValue(value) {
		m_rotate_v = (isNaN(value))?0:parseInt(value);
	}

	function getRotateHorizontalValue() {
		return m_rotate_h;
	}

	function getRotateVerticalValue() {
		return m_rotate_v;
	}

	function agDeg2Rad (deg) {
		return deg * Math.PI / 180;
	}

	function agRad2Deg (rad) {
		return rad * 180 / Math.PI;
	}

	function addLongitude (d) {
		m_ag_longitude = m_ag_longitude + d;
		m_ag_longitude = Math.round(m_ag_longitude/5)*5;
		calcCameraPos();
	}

	function setLongitude (d) {
		m_ag_longitude = d - 90;
		m_ag_longitude = Math.round(m_ag_longitude/5)*5;
		calcCameraPos();
	}

	function addLatitude (d) {
		m_ag_latitude = m_ag_latitude + d;
		m_ag_latitude = Math.round(m_ag_latitude/5)*5;
		calcCameraPos();
	}

	function setLatitude (d) {
		m_ag_latitude = d;
		m_ag_latitude = Math.round(m_ag_latitude/5)*5;
		calcCameraPos();
	}

	function calcRotateDeg () {

		var HV = getCameraAxis();
		if(!Ext.isEmpty(HV)){

			while (HV.H >= 360) {
				HV.H -= 360;
			}
			while (HV.H < 0) {
				HV.H += 360;
			}
			while (HV.V >= 360) {
				HV.V -= 360;
			}
			while (HV.V < 0) {
				HV.V += 360;
			}

			Ext.getCmp('rotateH').setValue(HV.H);
			Ext.getCmp('rotateV').setValue(HV.V);

			if(subRenderer){
				subRenderer.setLongitude(HV.H).setLatitude(HV.V);
			}
			if(testRenderer){
				testRenderer.setLongitude(HV.H).setLatitude(HV.V);
			}
			return {H:HV.H,V:HV.V};
		}


	//	var CTx = m_ag_targetPos.x - m_ag_cameraPos.x;
	//	var CTy = m_ag_targetPos.y - m_ag_cameraPos.y;
	//	var CTz = m_ag_targetPos.z - m_ag_cameraPos.z;

		var CT = new THREE.Vector3();
		CT.sub(m_ag_targetPos,m_ag_cameraPos);


		// Calculate Rotate H
		var radH = Math.acos(CT.y / Math.sqrt(CT.x * CT.x + CT.y * CT.y));

	//	console.log("calcRotateDeg()");
		var degH = radH / Math.PI * 180;
	//	console.log("calcRotateDeg():["+degH+"]");
		var degH = Math.round(radH / Math.PI * 180);
	//	console.log("calcRotateDeg():["+degH+"]");
		var degH = Math.round(Math.round(radH / Math.PI * 180 + 0.5)/5)*5;
	//	console.log("calcRotateDeg():["+degH+"]");

		if (CT.x > 0) degH = 360 - degH;
		while (degH >= 360) {
			degH = degH - 360;
		}
		if (m_ag_upVec.z < 0) {
			degH = degH + 180;
			while (degH >= 360) {
				degH = degH - 360;
			}
		}

		// Calculate Rotate V
	//	var UnitX = -1 * Math.sin(degH / 180 * Math.PI);
	//	var UnitY = Math.cos(degH / 180 * Math.PI);
	//	var UnitZ = 0;
		var Unit = new THREE.Vector3(-1 * Math.sin(degH / 180 * Math.PI),Math.cos(degH / 180 * Math.PI),0);

		var radV = Math.acos(CT.dot(Unit) / Math.sqrt(CT.lengthSq() * Unit.lengthSq()));
		if(isNaN(radV)) radV = 0;
		var degV = radV / Math.PI * 180;
		if (CT.z > 0) degV = 360 - degV;
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

		Ext.getCmp('rotateH').setValue(degH);
		Ext.getCmp('rotateV').setValue(degV);

		if(subRenderer){
			subRenderer.setLongitude(degH).setLatitude(degV);
	//		subRenderer.setLatitude(degV);
		}
		if(testRenderer){
			testRenderer.setLongitude(degH).setLatitude(degV);
		}

		return {H:degH,V:degV};
	}


	function calcCameraPos () {


		var eyeLongitudeRadian = agDeg2Rad(m_ag_longitude);
		var eyeLatitudeRadian = agDeg2Rad(m_ag_latitude);
		var eyeTargetDistance = m_ag_distance;

		var target = m_ag_targetPos;
		var eye = m_ag_cameraPos;
		var yAxis = m_ag_upVec;

		var zAxis = new THREE.Vector3();
		var xAxis = new THREE.Vector3();
		var tmp0 = new THREE.Vector3();
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

		if(parseFloat(zAxis.z) >= parseFloat(m_ag_epsilon)){
			xAxis.crossVectors(zAxis, tmp0);
			xAxis.normalize();
			yAxis.crossVectors(zAxis, xAxis);
			yAxis.normalize();
		}
		else if(parseFloat(zAxis.z) < -parseFloat(m_ag_epsilon)){
			xAxis.crossVectors(tmp0, zAxis);
			xAxis.normalize();
			yAxis.crossVectors(zAxis, xAxis);
			yAxis.normalize();
		}
		else{ // zAxis.z == 0
			remind =  Math.round(m_ag_latitude) % 360;
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

	//	var posDif = parseFloat(888.056);
		var posDif = m_ag_posDif;
		var tmpDeg = calcRotateDeg();
	//	console.log("calcCameraPos():tmpDeg:["+tmpDeg.H+"]["+tmpDeg.V+"]");
	//	console.log("calcCameraPos():eyeTargetDistance:["+eyeTargetDistance+"]");
	//	console.log("calcCameraPos():m_ag_posDif=["+m_ag_posDif+"]");

		if (tmpDeg.H == 0 && tmpDeg.V == 0) {
			m_ag_cameraPos.x = m_ag_targetPos.x;
			m_ag_cameraPos.y = m_ag_targetPos.y - posDif;
			m_ag_cameraPos.z = m_ag_targetPos.z;
		} else if (tmpDeg.H == 90 && tmpDeg.V == 0) {
			m_ag_cameraPos.x = m_ag_targetPos.x + posDif;
			m_ag_cameraPos.y = m_ag_targetPos.y;
			m_ag_cameraPos.z = m_ag_targetPos.z;
		} else if (tmpDeg.H == 180 && tmpDeg.V == 0) {
			m_ag_cameraPos.x = m_ag_targetPos.x;
			m_ag_cameraPos.y = m_ag_targetPos.y + posDif;
			m_ag_cameraPos.z = m_ag_targetPos.z;
		} else if (tmpDeg.H == 270 && tmpDeg.V == 0) {
			m_ag_cameraPos.x = m_ag_targetPos.x - posDif;
			m_ag_cameraPos.y = m_ag_targetPos.y;
			m_ag_cameraPos.z = m_ag_targetPos.z;
		}
	//	console.log(m_ag_cameraPos);
	//	console.log(m_ag_targetPos);
	//	console.log(m_ag_upVec);
	}


	function getCameraAxis(){

		return {
			H : Math.round(m_ag_longitude/5)*5 + 90,
			V : Math.round(m_ag_latitude/5)*5
		};

		var
			cam = camera.position.clone(),
			tar = target.clone(),
			upVec = camera.up.clone();

	//	console.log("setCameraAndTarget():m_ag_cameraPos:["+m_ag_cameraPos.x+"]["+m_ag_cameraPos.y+"]["+m_ag_cameraPos.z+"]");
	//	console.log("setCameraAndTarget():m_ag_targetPos:["+m_ag_targetPos.x+"]["+m_ag_targetPos.y+"]["+m_ag_targetPos.z+"]");

		cam.copy(m_ag_cameraPos);
		tar.copy(m_ag_targetPos);
		upVec.copy(m_ag_upVec);

	//	console.log("getCameraAxis()");

		var tc = new THREE.Vector3();	// camera  -> target
		tc.sub(cam, tar);
		if(tc.isZero()) return undefined;
		var tc_len = tc.length();

		var ntc = tc.clone();	// |camera  -> target|
		var inv_tc_len = 1 / tc_len;
		ntc.multiplyScalar(inv_tc_len);

		var vz = new THREE.Vector3(0, 0, 1); // zaxis

	//	console.log(agRad2Deg(Math.acos(ntc.dot(vz))));

		// calc latitude
		var latitude = 90;
		if (upVec.z >= 0) {
			latitude = 90 - agRad2Deg(Math.acos(ntc.dot(vz)));
		} else {
			latitude = 90 + agRad2Deg(Math.acos(ntc.dot(vz)));
		}

		// calc longitude
		var longitude = 0;
		var ntc_xy = new THREE.Vector3(tc.x, tc.y, 0);

		if (!ntc_xy.normalize().isZero()) {
			var vx = new THREE.Vector3(1, 0, 0);
			if (upVec.z >= 0) {
			} else {
				ntc_xy.x = -ntc_xy.x;
				ntc_xy.y = -ntc_xy.y;
				ntc_xy.z = 0;
			}
			var tmp = agRad2Deg(Math.acos(ntc_xy.dot(vx)));
			if (ntc_xy.y >= 0) {
				longitude = tmp;
			} else {
				longitude = -tmp;
			}
		} else {
			var vx = new THREE.Vector3(1, 0, 0);
			var nup_xy = new THREE.Vector3();
			if (ntc.z >= 0) {
				nup_xy.x = -upVec.x;
				nup_xy.y = -upVec.y;
				nup_xy.z = 0;
			} else {
				nup_xy.x = upVec.x;
				nup_xy.y = upVec.y;
				nup_xy.z = 0;
			}
			nup_xy.normalize();
			var tmp = agRad2Deg(Math.acos(nup_xy.dot(vx)));
			if (nup_xy.y >= 0) {
				longitude = tmp;
			} else {
				longitude = -tmp;
			}
		}
	//	console.log(tc_len);
	//	console.log(Math.round(longitude/5)*5 + 90);
	//	console.log(Math.round(latitude/5)*5);

		cam.copy(m_ag_cameraPos);
		tar.copy(m_ag_targetPos);
		upVec.copy(m_ag_upVec);
		setCameraAndTarget_old(cam, tar, upVec);

		return undefined;

		return {
			H : Math.round(longitude/5)*5 + 90,
			V : Math.round(latitude/5)*5
		};
	}

	function AGDifferenceD3 (v0, v1, out) {
		out.x = parseFloat(v0.x) - parseFloat(v1.x);
		out.y = parseFloat(v0.y) - parseFloat(v1.y);
		out.z = parseFloat(v0.z) - parseFloat(v1.z);
	}
	function AGInnerProductD3 (v0, v1) {
		return parseFloat(v0.x * v1.x) + parseFloat(v0.y * v1.y) + parseFloat(v0.z * v1.z);
	}
	function AGOuterProductD3 (v0, v1, out) {
		out.x = parseFloat(v0.y * v1.z) - parseFloat(v1.y * v0.z);
		out.y = parseFloat(v0.z * v1.x) - parseFloat(v1.z * v0.x);
		out.z = parseFloat(v0.x * v1.y) - parseFloat(v1.x * v0.y);
	}
	function AGIsZero (x) {
		return (((parseFloat(x)<parseFloat(m_ag_epsilon)) && (parseFloat(x)>(-parseFloat(m_ag_epsilon)))) ? true : false);
	}

	function AGNormalizeD3 (v0, out) {
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
	function AGMultD3(v0,a){
		v0[AG_X] = a*v0[AG_X];
		v0[AG_Y] = a*v0[AG_Y];
		v0[AG_Z] = a*v0[AG_Z];
	}

	function setCameraAndTarget_old (cam, tar, upVec) {
		var tc = new AGVec3d(null, null, null);	// camera  -> target
		AGDifferenceD3(cam, tar, tc);
		var tc_len = AGInnerProductD3(tc, tc);
		tc_len = Math.sqrt(tc_len);
		if (AGIsZero(tc_len)) {
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
			latitude = 90 - agRad2Deg(Math.acos(AGInnerProductD3(ntc, vz)));
		} else {
			latitude = 90 + agRad2Deg(Math.acos(AGInnerProductD3(ntc, vz)));
		}

		// calc longitude
		var longitude = 0;
		var ntc_xy = new AGVec3d(tc.x, tc.y, 0);

		if (AGNormalizeD3(ntc_xy, ntc_xy)) {
			var vx = new AGVec3d(1, 0, 0);
			if (upVec.z >= 0) {
			} else {
				ntc_xy.x = -ntc_xy.x;
				ntc_xy.y = -ntc_xy.y;
				ntc_xy.z = 0;
			}
			var tmp = agRad2Deg(Math.acos(AGInnerProductD3(ntc_xy, vx)));
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
			if (!AGNormalizeD3(nup_xy, nup_xy)) {
			}
			var tmp = agRad2Deg(Math.acos(AGInnerProductD3(nup_xy, vx)));
			if (nup_xy.y >= 0) {
				longitude = tmp;
			} else {
				longitude = -tmp;
			}
		}
	//	console.log(Math.round(longitude/5)*5 + 90);
	//	console.log(Math.round(latitude/5)*5);
	}

	function setCameraAndTarget (cam, tar, upVec, isInitData) {
		isInitData = false;

		var tc = new THREE.Vector3();	// camera  -> target
		tc.subVectors(cam, tar);
		if(tc.isZero()) return false;
		var tc_len = tc.length();

		var ntc = tc.clone();	// |camera  -> target|
		var inv_tc_len = 1 / tc_len;
		ntc.multiplyScalar(inv_tc_len);

		var vz = new THREE.Vector3(0, 0, 1); // zaxis

		// calc latitude
		var latitude = 90;
		if (upVec.z >= 0) {
			latitude = 90 - agRad2Deg(Math.acos(ntc.dot(vz)));
		} else {
			latitude = 90 + agRad2Deg(Math.acos(ntc.dot(vz)));
		}

		// calc longitude
		var longitude = 0;
		var ntc_xy = new THREE.Vector3(tc.x, tc.y, 0);

		if (!ntc_xy.normalize().isZero()) {
			var vx = new THREE.Vector3(1, 0, 0);
			if (upVec.z >= 0) {
			} else {
				ntc_xy.x = -ntc_xy.x;
				ntc_xy.y = -ntc_xy.y;
				ntc_xy.z = 0;
			}
			var tmp = agRad2Deg(Math.acos(ntc_xy.dot(vx)));
			if (ntc_xy.y >= 0) {
				longitude = tmp;
			} else {
				longitude = -tmp;
			}
		} else {
			var vx = new THREE.Vector3(1, 0, 0);
			var nup_xy = new THREE.Vector3();
			if (ntc.z >= 0) {
				nup_xy.x = -upVec.x;
				nup_xy.y = -upVec.y;
				nup_xy.z = 0;
			} else {
				nup_xy.x = upVec.x;
				nup_xy.y = upVec.y;
				nup_xy.z = 0;
			}
			nup_xy.normalize();
			var tmp = agRad2Deg(Math.acos(nup_xy.dot(vx)));
			if (nup_xy.y >= 0) {
				longitude = tmp;
			} else {
				longitude = -tmp;
			}
		}

		m_ag_targetPos.copy(tar);
		m_ag_distance = tc_len;
		if(Ext.isEmpty(m_ag_posDif)) m_ag_posDif = m_ag_distance;

		m_ag_longitude = longitude;
		m_ag_latitude = latitude;

		m_ag_longitude = Math.round(m_ag_longitude/5)*5;
		m_ag_latitude = Math.round(m_ag_latitude/5)*5;

		calcCameraPos();

		if (isInitData) {
			m_ag_initTargetPos.copy(m_ag_targetPos);
			m_ag_initLongitude = m_ag_longitude;
			m_ag_initLatitude = m_ag_latitude;
			m_ag_initDistance = m_ag_distance;
		}

	//	console.log("setCameraAndTarget():m_ag_cameraPos:["+m_ag_cameraPos.x+"]["+m_ag_cameraPos.y+"]["+m_ag_cameraPos.z+"]");
	//	console.log("setCameraAndTarget():m_ag_targetPos:["+m_ag_targetPos.x+"]["+m_ag_targetPos.y+"]["+m_ag_targetPos.z+"]");
	//	console.log("setCameraAndTarget():m_ag_distance:["+m_ag_distance+"]");
	//	console.log("setCameraAndTarget():m_ag_posDif:["+m_ag_posDif+"]");
	//	console.log("setCameraAndTarget():m_ag_orthoYRange:["+m_ag_orthoYRange+"]");
	//	console.log("setCameraAndTarget():m_ag_longitude:["+m_ag_longitude+"]");
	//	console.log("setCameraAndTarget():m_ag_latitude:["+m_ag_latitude+"]");

		return true;
	}

	var d_yrange = 1567;
	var d_yrange = 115.4656;
	//console.log("Math.E=["+Math.E+"]");																						// 2.718281828459045
	//console.log("Math.log(2)=["+Math.log(2)+"]");																	// 0.6931471805599453
	//console.log("Math.log(1800)=["+Math.log(1800)+"]");														// 7.495541943884256 // 1800 = 2.718281828459045 ^ 7.495541943884256
	//console.log("Math.log(1800)/Math.log(2)=["+Math.log(1800)/Math.log(2)+"]");		//10.813781191217037

	//console.log("Math.log("+d_yrange+")=["+Math.log(d_yrange)+"]");
	//console.log(Math.log(1800)/Math.log(2) - Math.log(d_yrange) / Math.log(2));
	//console.log((Math.log(1800)/Math.log(2) - Math.log(d_yrange) / Math.log(2))*5);
	//console.log((Math.log(1800)/Math.log(2) - Math.log(d_yrange) / Math.log(2))*5 -0.5);
	//console.log(Math.round((Math.log(1800)/Math.log(2) - Math.log(d_yrange) / Math.log(2))*5 -0.5));


	//1800/2 - 1500/2 = 900 - 750 = 150;
	//1800/2 - x/2    = 900 - x/2 = 150;
	//900-150 = 750*2 = 1500;

	//10.813781191217037-0.2 = 10.613781191217037
	//10.613781191217037 * 0.6931471805599453 = 7.3569125077722668577560411480761
	//2.718281828459045 ^ 7.3569125077722668577560411480761 = 1566.991013933022231958271264821

	//10.813781191217037-6 = 4.813781191217037
	//4.813781191217037 * 0.6931471805599453 = 3.3366588605245841177560411480761
	//2.718281828459045 ^ 3.3366588605245841177560411480761 = 28.124999999999989456324316090796

	var ZOOM = 6;
	var ZOOM = 5.8;
	var ZOOM = 4;
	var ZOOM = 19.8;
	//console.log("ZOOM:["+ZOOM+"]=["+Math.pow(Math.E,(Math.log(1800)/Math.log(2)-ZOOM) * Math.log(2))+"]");
	//console.log("ZOOM:["+ZOOM+"]=["+Math.round(Math.pow(Math.E,(Math.log(1800)/Math.log(2)-ZOOM) * Math.log(2)))+"]");
	//console.log("ZOOM:["+ZOOM+"]=["+getZoomYRange(ZOOM)+"]");

	function getZoomYRange(zoom){
		return Math.max(1,Math.round(Math.pow(Math.E,(Math.log(1800)/Math.log(2)-zoom) * Math.log(2))));
	}
	function getYRangeZoom(yrange){
		return Math.round((Math.log(1800)/Math.log(2) - Math.log(yrange)/Math.log(2)) * 10) / 10;
	}

	//console.log("");


	//console.log((Math.log(1800)/Math.log(2) - Math.log(d_yrange) / Math.log(2))*5);
	//console.log((Math.log(1800)/Math.log(2) - Math.log(d_yrange) / Math.log(2))*5 -0.5);
	//console.log(Math.round((Math.log(1800)/Math.log(2) - Math.log(d_yrange) / Math.log(2))*5 -0.5));
	//Math.round((Math.log(1800)/Math.log(2) - Math.log(ret.getCamera().getYrange()) / Math.log(2)) * 5 -0.5)
	/*
	0～19.8

	783.4955069665117252226430157324
	682.07245492967913705626691058823
	*/

	function anatomoImgMoveCenter(x,y){
		var centerX = parseInt((SCREEN_WIDTH /2) -  x);
		var centerY = parseInt((SCREEN_HEIGHT /2) -  y);
	//	var image_h = SCREEN_HEIGHT;
	//	var zoom = 0;


	//	moveTargetByMouseForOrtho(m_ag_orthoYRange, centerX / parseFloat(Math.pow(2, zoom)), centerY / parseFloat(Math.pow(2, zoom)));


	//	moveTargetByMouseForOrtho(centerX / parseFloat(Math.pow(2, zoom)), centerY / parseFloat(Math.pow(2, zoom)));
		moveTargetByMouseForOrtho(centerX,centerY);

	//	moveTargetByMouseForOrtho(centerX, centerY);
		camera.position.copy(m_ag_cameraPos);
		camera.up.copy(m_ag_upVec);
		target.copy(m_ag_targetPos);
	}

	function moveTargetByMouseForOrtho (dx, dy) {
	//	m_ag_orthoYRange = 1800;
	//	var rx = -dx * m_ag_orthoYRange / winHeight;
	//	var ry = dy * m_ag_orthoYRange / winHeight;

//		console.log(m_ag_orthoYRange*dx/SCREEN_HEIGHT,m_ag_orthoYRange*dy/SCREEN_HEIGHT);

	//	console.log("moveTargetByMouseForOrtho():SCREEN=["+SCREEN_WIDTH+"]["+SCREEN_HEIGHT+"]");
	//	console.log("moveTargetByMouseForOrtho():xy=["+dx+"]["+dy+"]");
//		console.log("moveTargetByMouseForOrtho():zoom=["+zoom+"]");

		var h = m_ag_orthoYRange/ Math.pow(2, zoom);
//		console.log(h*dx/SCREEN_HEIGHT,h*dy/SCREEN_HEIGHT);
//		console.log(m_ag_cameraPos);

		moveTarget (h*dx/SCREEN_HEIGHT,h*dy/SCREEN_HEIGHT);
//		console.log(m_ag_cameraPos);

/*


	//	dx /= parseFloat(Math.pow(2, zoom));
	//	dy /= parseFloat(Math.pow(2, zoom));

		dx /= parseFloat(Math.pow(2, zoom));
		dy /= parseFloat(Math.pow(2, zoom));

		m_ag_orthoYRange = 1800;
		dx *= (m_ag_orthoYRange / SCREEN_HEIGHT);
		dy *= (m_ag_orthoYRange / SCREEN_HEIGHT);

//		console.log("moveTargetByMouseForOrtho():xy=["+dx+"]["+dy+"]");

		moveTarget (dx, dy);
*/
	}

	function moveTarget (dx, dy) {

		var rx = -dx;
		var ry = dy;

	//console.log("moveTargetByMouseForOrtho():["+dx+"]["+dy+"]["+rx+"]["+ry+"]["+m_ag_orthoYRange+"]["+winHeight+"]["+(m_ag_orthoYRange / winHeight)+"]");

		// latitude
		var eyeLongitudeRadian = agDeg2Rad(m_ag_longitude);
	//console.log("moveTarget():m_ag_longitude=["+m_ag_longitude+"]["+eyeLongitudeRadian+"]");

		// logitude
		var eyeLatitudeRadian = agDeg2Rad(m_ag_latitude);
	//console.log("moveTarget():m_ag_latitude=["+m_ag_latitude+"]["+eyeLatitudeRadian+"]");

		var cEyeLongitude = Math.cos(eyeLongitudeRadian);
		var sEyeLongitude = Math.sin(eyeLongitudeRadian);
		var cEyeLatitude = Math.cos(eyeLatitudeRadian);
		var sEyeLatitude = Math.sin(eyeLatitudeRadian);

		var zAxis = new THREE.Vector3();
		var xAxis = new THREE.Vector3();
		var yAxis = new THREE.Vector3();
		var tmp0 = new THREE.Vector3();
		var remind;

		yAxis.set(cEyeLatitude * cEyeLongitude, cEyeLatitude * sEyeLongitude, sEyeLatitude);
		tmp0.set(cEyeLongitude, sEyeLongitude, 0);

		if(yAxis.z >= parseFloat(m_ag_epsilon)){
			xAxis.crossVectors(yAxis, tmp0);
			zAxis.crossVectors(yAxis, xAxis);
		}
		else if(yAxis.z < -parseFloat(m_ag_epsilon)){
			xAxis.crossVectors(tmp0, yAxis);
			zAxis.crossVectors(yAxis, xAxis);
		} else {	// yAxis.z == 0
			remind = Math.round(m_ag_latitude) % 360;
			remind = remind < 0 ? -remind : remind;

			if(remind > 175 && remind < 185){
				zAxis.set(0, 0, -1);
			}else{
				zAxis.set(0, 0, 1);
			}
			xAxis.crossVectors(zAxis, yAxis);
		}

		var norm = new THREE.Vector3();
		if(AGNormalizeD3(xAxis, norm)) norm.copy(xAxis);
		if(AGNormalizeD3(zAxis, norm)) norm.copy(zAxis);

		m_ag_targetPos.x = parseFloat(m_ag_targetPos.x) + parseFloat(xAxis.x * rx) + parseFloat(zAxis.x * ry);
		m_ag_targetPos.y = parseFloat(m_ag_targetPos.y) + parseFloat(xAxis.y * rx) + parseFloat(zAxis.y * ry);
		m_ag_targetPos.z = parseFloat(m_ag_targetPos.z) + parseFloat(xAxis.z * rx) + parseFloat(zAxis.z * ry);

		calcCameraPos();
	}

	function calcTarget (dx, dy) {

		var rx = -dx;
		var ry = dy;

	//console.log("calcTarget():["+dx+"]["+dy+"]["+rx+"]["+ry+"]["+m_ag_orthoYRange+"]["+winHeight+"]["+(m_ag_orthoYRange / winHeight)+"]");

		// latitude
		var eyeLongitudeRadian = agDeg2Rad(m_ag_longitude);
	//console.log("calcTarget():m_ag_longitude=["+m_ag_longitude+"]["+eyeLongitudeRadian+"]");

		// logitude
		var eyeLatitudeRadian = agDeg2Rad(m_ag_latitude);
	//console.log("calcTarget():m_ag_latitude=["+m_ag_latitude+"]["+eyeLatitudeRadian+"]");

		var cEyeLongitude = Math.cos(eyeLongitudeRadian);
		var sEyeLongitude = Math.sin(eyeLongitudeRadian);
		var cEyeLatitude = Math.cos(eyeLatitudeRadian);
		var sEyeLatitude = Math.sin(eyeLatitudeRadian);

		var zAxis = new THREE.Vector3();
		var xAxis = new THREE.Vector3();
		var yAxis = new THREE.Vector3();
		var tmp0 = new THREE.Vector3();
		var remind;

		yAxis.set(cEyeLatitude * cEyeLongitude, cEyeLatitude * sEyeLongitude, sEyeLatitude);
		tmp0.set(cEyeLongitude, sEyeLongitude, 0);

		if(yAxis.z >= parseFloat(m_ag_epsilon)){
			xAxis.crossVectors(yAxis, tmp0);
			zAxis.crossVectors(yAxis, xAxis);
		}
		else if(yAxis.z < -parseFloat(m_ag_epsilon)){
			xAxis.crossVectors(tmp0, yAxis);
			zAxis.crossVectors(yAxis, xAxis);
		} else {	// yAxis.z == 0
			remind = Math.round(m_ag_latitude) % 360;
			remind = remind < 0 ? -remind : remind;

			if(remind > 175 && remind < 185){
				zAxis.set(0, 0, -1);
			}else{
				zAxis.set(0, 0, 1);
			}
			xAxis.crossVectors(zAxis, yAxis);
		}

		var norm = new THREE.Vector3();
		if(AGNormalizeD3(xAxis, norm)) norm.copy(xAxis);
		if(AGNormalizeD3(zAxis, norm)) norm.copy(zAxis);

		return new THREE.Vector3(
			parseFloat(m_ag_targetPos.x) + parseFloat(xAxis.x * rx) + parseFloat(zAxis.x * ry),
			parseFloat(m_ag_targetPos.y) + parseFloat(xAxis.y * rx) + parseFloat(zAxis.y * ry),
			parseFloat(m_ag_targetPos.z) + parseFloat(xAxis.z * rx) + parseFloat(zAxis.z * ry)
		);
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
	//	console.log("X=["+rx+"]["+dx+"]");
	//	console.log("Y=["+ry+"]["+dy+"]");
	//	console.log("Z=["+rz+"]["+dz+"]");


		var degH = 0;
		var degV = 0;

		var CTx = upVec.x;
		var CTy = upVec.y;
		var CTz = upVec.z;

	//	console.log("CTx=["+CTx+"]");
	//	console.log("CTy=["+CTy+"]");
	//	console.log("CTz=["+CTz+"]");

		// Calculate Rotate H
		var radH = Math.acos(CTy / Math.sqrt(CTx*CTx + CTy * CTy));
	//	console.log("radH=["+radH+"]");
		if(isNaN(radH)) radH = 0;
		var degH = radH / Math.PI * 180;

		// Calculate Rotate V
		var UnitX = -1 * Math.sin(degH / 180 * Math.PI);
		var UnitY = Math.cos(degH / 180 * Math.PI);
		var UnitZ = 0;
		var radV = Math.acos((CTx * UnitX + CTy * UnitY + CTz * UnitZ) / Math.sqrt((CTx * CTx + CTy * CTy + CTz * CTz) * (UnitX * UnitX + UnitY * UnitY + UnitZ * UnitZ)));
		if(isNaN(radV)) radV = 0;
		var degV = radV / Math.PI * 180;

	//	console.log("deg=["+degH+"]["+degV+"]");


		return {H:degH,V:degV};
	}



	/*!
	 * バウンディングボックスから自動的にカメラを設定
	 */
	var AG_PERSWIN_DISTANCE_MIN = 1.0;
	var AG_PERSWIN_DISTANCE_MAX = 100000.0;
	var AG_PERSWIN_FOVY_MIN = 1.0;
	var AG_PERSWIN_FOVY_MAX = 90.0;
	var AG_PERSWIN_AUTO_CAMERA_ELONG = 1.1;
	var AG_PERSWIN_AUTO_CAMERA_FAR_ELONG = 2.0;
	var AG_PERSWIN_AUTO_CAMERA_NEAR_ENSHORT = 0.9;
	var AG_PERSWIN_AUTO_CAMERA_FOVY = 30.0;

	var AG_X = 'x';
	var AG_Y = 'y';
	var AG_Z = 'z';
	function setAutoCameraPos(param){
		var minX = param.xmin,
				maxX = param.xmax,
				minY = param.ymin,
				maxY = param.ymax,
				minZ = param.zmin,
				maxZ = param.zmax;
		var ret = true;

		var newcam = new THREE.Vector3();		/* 新しいカメラの位置 */
		var newtar = new THREE.Vector3();		/* 新しいターゲットの位置 */
		var newfar;		/* m_persFar */
		var newnear;		/* m_parsNear */

		var bc_pos = new THREE.Vector3();		/* バウンディングボックスの中心点 */
		var bfc_pos = new THREE.Vector3();	/* バウンディングボックス正面の中心点 */
		var bbc_pos = new THREE.Vector3();	/* バウンディングボックス背面の中心点 */
		var bf_w;		/* バウンディングボックス正面のwidth */
		var bf_h;		/* バウンディングボックス正面のheight */
		var bf_d;		/* バウンディングボックスのdepth */
		var ntc = new THREE.Vector3();		/* 新しい|target->camera| */

		bc_pos.x = (maxX + minX)/2;
		bc_pos.y = (maxY + minY)/2;
		bc_pos.z = (maxZ + minZ)/2;

		bfc_pos.x = bbc_pos.x = bc_pos.x;
		bfc_pos.y = bbc_pos.y = bc_pos.y;
		bfc_pos.z = bbc_pos.z = bc_pos.z;

		bf_w = maxX - minX;
		bf_h = maxZ - minZ;
		bf_d = maxY - minY;

		bfc_pos.y = minY;
		bbc_pos.y = maxY;
		ntc.x =  0.0;
		ntc.y = -1.0;
		ntc.z =  0.0;

	/*
		m_bBoxLeft		= minX;
		m_bBoxRight		= maxX;
		m_bBoxBottom	= minZ;
		m_bBoxTop		= maxZ;
		m_bBoxFront		= minY;
		m_bBoxBack		= maxY;
	*/


		var cam_bfc_len; /* bfcと新カメラとの距離 */
		var newfovy = AG_PERSWIN_AUTO_CAMERA_FOVY; /* 新しい縦画角 */
		var diag_len = Math.sqrt(bf_w*bf_w + bf_h*bf_h + bf_d*bf_d); /* バウンディングボックスの対角線距離 */

		if((bf_h * aspectRatio) < bf_w){
			cam_bfc_len = ((bf_w / aspectRatio) / 2) / Math.tan( agDeg2Rad(newfovy / 2) );
		}else{
			cam_bfc_len = (bf_h / 2) / Math.tan( agDeg2Rad(newfovy / 2) );
		}
		cam_bfc_len = cam_bfc_len * AG_PERSWIN_AUTO_CAMERA_ELONG;

		newtar[AG_X] = bc_pos[AG_X];
		newtar[AG_Y] = bc_pos[AG_Y];
		newtar[AG_Z] = bc_pos[AG_Z];
		newcam[AG_X] = bfc_pos[AG_X] + (cam_bfc_len * ntc[AG_X]);
		newcam[AG_Y] = bfc_pos[AG_Y] + (cam_bfc_len * ntc[AG_Y]);
		newcam[AG_Z] = bfc_pos[AG_Z] + (cam_bfc_len * ntc[AG_Z]);
		newfar = (cam_bfc_len + bf_d) * AG_PERSWIN_AUTO_CAMERA_FAR_ELONG;
		newnear = (cam_bfc_len + bf_d/2 - diag_len/2) * AG_PERSWIN_AUTO_CAMERA_NEAR_ENSHORT;
		if (newnear < 0) newnear = 0.1;

	//	setFovy(newfovy);
		m_persFar = newfar;
		m_persNear = newnear;
		setCameraAndTarget(newcam,newtar,new THREE.Vector3(0,0,1));
	}

	var m_persNear = 0.00001;
	var m_persNear = 0.1;
	var m_persFar = 10000;
	var m_persFovy = m_initPersFovy = AG_PERSWIN_AUTO_CAMERA_FOVY;

	var m_persFar;
	var m_persNear;
	var m_persFovy = AG_PERSWIN_AUTO_CAMERA_FOVY;
	function setFovy(
		fovy		/*! [i ] 縦画角 [deg] */,
		isInitData	/*! [i ] 初期化データか否か */ )
	{
		if( fovy <= 120 && fovy > 0 ){
			m_persFovy = fovy;
			if( isInitData ) m_initPersFovy = fovy;
			return true;
		}else{
			return false;
		}
	}

	$(window).bind('changeGuide',function(e,checked){
	//	console.log("changeGuide():EVENT!!");
		try{
			Ext.getCmp('options-guide').setChecked(checked);
			render();
		}catch(e){
			console.error(e);
		}
	});
	$(window).bind('changeToolTip',function(e,checked){
	//	console.log("changeToolTip():EVENT!!");
		try{
			var options_tooltip = Ext.getCmp('options-tooltip');
			options_tooltip.setChecked(checked);
		}catch(e){
			console.error(e);
		}
	});
	$(window).bind('changeStats',function(e,checked){
	//	console.log("changeStats():EVENT!!");
		try{
			Ext.getCmp('options-stats').setChecked(checked);
		}catch(e){
			console.error(e);
		}
	});
	$(window).bind('changeClickMode',function(e,clickmode){
	//	console.log("changeClickMode():EVENT!!");
		try{
			var menuBtn = Ext.getCmp('click-mode-menu');
			menuBtn.menu.items.each(function(menuitem,i,l){
				if(menuitem.value != clickmode) return true;
				menuBtn.setActiveItem(menuitem,true);
				return false;
			});
		}catch(e){
			console.error(e);
		}
	});
	$(window).bind('changeLongitudeDegree',function(e,newValue,oldValue){
	//	console.log("changeLongitudeDegree():EVENT!!");
		try{
			var field = Ext.getCmp('rotateH');
			if(field.value!=newValue){
				field.suspendEvents(false);
				try{
					setLongitude(newValue);
					camera.position.copy(m_ag_cameraPos);
					camera.up.copy(m_ag_upVec);
					target.copy(m_ag_targetPos);
					updateCameraHash();
				}catch(e){
					console.error(e);
				}
				field.resumeEvents();
			}
		}catch(e){
			console.error(e);
		}
	});
	$(window).bind('changeLatitudeDegree',function(e,newValue,oldValue){
	//	console.log("changeLatitudeDegree():EVENT!!");
		try{
			var field = Ext.getCmp('rotateV');
			if(field.value!=newValue){
				field.suspendEvents(false);
				try{
					setLatitude(newValue);
					camera.position.copy(m_ag_cameraPos);
					camera.up.copy(m_ag_upVec);
					target.copy(m_ag_targetPos);
					updateCameraHash();
				}catch(e){
					console.error(e);
				}
				field.resumeEvents();
			}
		}catch(e){
			console.error(e);
		}
	});
	$(window).bind('changeZoom',function(e,newValue,oldValue){
	//	console.log("changeZoom():EVENT!!");
		try{
			var field = Ext.getCmp('zoom-value-text');
			if(field.value!=newValue){
				field.suspendEvents(false);
				try{
					zoom = (newValue-1)/5;
					chengeZoom();
					updateCameraHash();
				}catch(e){
					console.error(e);
				}
				field.resumeEvents();
			}
		}catch(e){
			console.error(e);
		}
	});
	$(window).bind('changeCameraNear',function(e,newValue,oldValue){
	//	console.log("changeCameraNear():EVENT!!");
		try{
			var field = Ext.getCmp('camera-near');
			if(field.value!=newValue){
				field.suspendEvents(false);
				try{
					field.setValue(newValue);
					cameraConfig.near = newValue;
					camera.near = newValue;
					cameraUpdate();
				}catch(e){
					console.error(e);
				}
				field.resumeEvents();
			}
		}catch(e){
			console.error(e);
		}
	});
	$(window).bind('changeCameraFar',function(e,newValue,oldValue){
	//	console.log("changeCameraFar():EVENT!!");
		try{
			var field = Ext.getCmp('camera-far');
			if(field.value!=newValue){
				field.suspendEvents(false);
				try{
					field.setValue(newValue);
					cameraConfig.far = newValue;
					camera.far = newValue;
					cameraUpdate();
				}catch(e){
					console.error(e);
				}
				field.resumeEvents();
			}
		}catch(e){
			console.error(e);
		}
	});
	$(window).bind('printImage',function(e){
	//	console.log("printImage():EVENT!!");
		self.loadBp3dParts.showLoading();
		Ext.defer(function(){
			var chg = false;
			var visible = subRenderer ? Ext.get(subRenderer.domElement).isVisible() : false;
			if(visible) Ext.get(subRenderer.domElement).setVisible(false);
			try{
				if(cameraPerspectiveHelper && cameraPerspectiveHelper.visible){
					cameraPerspectiveHelper.visible = false;
					render();
					chg = true;
				}

				var imageDatas = [];
				render();
				imageDatas.push({
					'3D': renderer.domElement.toDataURL('image/png'),
					'2D': canvas2D.toDataURL('image/png')
				});
				Ext.Ajax.request({
					url: 'make-rotating-image.cgi',
					timeout: 300000,
					params  : {
						images : Ext.encode(imageDatas),
						cmd    : 'base64'
					},
					success : function(conn,response,options){
	//					console.log("LOAD:OK!!");
						try{
							var json;
							try{json = Ext.JSON.decode(conn.responseText);}catch(e){console.error(e);}
							if(json && json.success){
								if(_bp3d_image_window && !_bp3d_image_window.closed) _bp3d_image_window.close();
								var dataURL = json.data;
								_bp3d_image_window = window.open('about:blank',"_bp3d_image_window","width="+SCREEN_WIDTH+",height="+SCREEN_HEIGHT);
								var image = _bp3d_image_window.document.createElement( 'img' );
								_bp3d_image_window.document.body.appendChild( image );
								image.onabort=image.onerror=function(){
									self.loadBp3dParts.hideLoading();
								};
								image.onload=function(){
									self.loadBp3dParts.hideLoading();
								};
								image.src = dataURL;
								_bp3d_image_window.focus();
							}
						}catch(e){
	//						console.log("LOAD:ERR!!:["+e+"]");
							console.error(e);
							self.loadBp3dParts.hideLoading();
						}
					},
					failure : function(conn,response,options){
	//					console.log("LOAD:NG!!");
						self.loadBp3dParts.hideLoading();
					}
				});
				imageDatas.length = 0;
				imageDatas = undefined;

			}catch(e){
				console.error(e);
			}
			if(chg) cameraPerspectiveHelper.visible = true;
			if(visible && subRenderer) Ext.get(subRenderer.domElement).setVisible(true);
			render();
		},250);
	});
	$(window).bind('printRotatingImage',function(e,w,h){
	//	console.log("printRotatingImage():EVENT!!");
		if(Ext.isEmpty(w) && Ext.isEmpty(h)) w = h = 120;
		if(Ext.isEmpty(w)) w = h;
		if(Ext.isEmpty(h)) h = w;

		self.loadBp3dParts.showLoading();

		Ext.defer(function(){
			var $canvas2D = $('#canvas2D');
			var canvas2D = $canvas2D.get(0);
	//		var org_font = $canvas2D.css('font-style') + ' ' + $canvas2D.css('font-variant') + ' ' + $canvas2D.css('font-weight') + ' ' + $canvas2D.css('font-size') + '/' + $canvas2D.css('line-height') + ' ' + $canvas2D.css('font-family');
			var org_font = $canvas2D.css('font');
			$canvas2D.css('font-size','9px');

			var visible = subRenderer ? Ext.get(subRenderer.domElement).isVisible() : false;
			if(visible) Ext.get(subRenderer.domElement).setVisible(false);

			try{
				var chg = false;

				if(cameraPerspectiveHelper && cameraPerspectiveHelper.visible){
					cameraPerspectiveHelper.visible = false;
					render();
					chg = true;
				}

				var _SCREEN_WIDTH = SCREEN_WIDTH;
				var _SCREEN_HEIGHT = SCREEN_HEIGHT;

				var tmpDeg = calcRotateDeg();
				var _H = tmpDeg.H;

				resize(w,h);
				createLocaleHashStrTask.cancel();


				var imageDatas = [];
				do{
					addLongitude(5);
					camera.position.copy(m_ag_cameraPos);
					camera.up.copy(m_ag_upVec);
					target.copy(m_ag_targetPos);
					if(w < 640){
						render({
							DrawLegendFlag: false,
							PinDescriptionDrawFlag: false,
							PinIndicationLineDrawFlag: 0
						});
					}else{
						render();
					}
					imageDatas.push({
						'3D': renderer.domElement.toDataURL('image/png'),
						'2D': canvas2D.toDataURL('image/png')
					});

					tmpDeg = calcRotateDeg();
	//				console.log("["+_H+"]["+tmpDeg.H+"]");

				}while(_H != tmpDeg.H);

				resize(_SCREEN_WIDTH,_SCREEN_HEIGHT);
				createLocaleHashStrTask.cancel();

				Ext.Ajax.request({
					url: 'make-rotating-image.cgi',
					timeout: 300000,
					params  : {
						images : Ext.encode(imageDatas),
						cmd    : 'base64'
					},
					success : function(conn,response,options){
	//					console.log("LOAD:OK!!");
						try{
							var json;
							try{json = Ext.JSON.decode(conn.responseText);}catch(e){console.log(e);}
							if(json && json.success){
								if(_bp3d_image_window && !_bp3d_image_window.closed) _bp3d_image_window.close();
								var dataURL = json.data;
								_bp3d_image_window = window.open('about:blank',"_bp3d_image_window","width="+(w+25)+",height="+(h+20));
								var image = _bp3d_image_window.document.createElement( 'img' );
								_bp3d_image_window.document.body.appendChild( image );
								image.onabort=image.onerror=function(){
									self.loadBp3dParts.hideLoading();
								};
								image.onload=function(){
									self.loadBp3dParts.hideLoading();
								};
								image.src = dataURL;
								_bp3d_image_window.focus();
							}
						}catch(e){
	//						console.log("LOAD:ERR!!:["+e+"]");
							self.loadBp3dParts.hideLoading();
						}
					},
					failure : function(conn,response,options){
	//					console.log("LOAD:NG!!");
						self.loadBp3dParts.hideLoading();
					}
				});
				imageDatas.length = 0;
				imageDatas = undefined;

			}catch(e){
				console.error(e);
				self.loadBp3dParts.hideLoading();
			}
			if(chg) cameraPerspectiveHelper.visible = true;

			if(visible && subRenderer) Ext.get(subRenderer.domElement).setVisible(true);
			$canvas2D.css('font',org_font);
			render();

		},250);

	});

	$(window).bind('changeLocaleHashStr',function(e,hashStr){
	//	console.log("changeLocaleHashStr():EVENT!!");
		self.loadBp3dParts.showLoading();
		setTimeout(function(){
			createLocaleHashStr(hashStr);
		},250);
	});

	var glb_hashStr;

	var getLocaleHashStr = function(){
		var hashStr = glb_hashStr;
		if(Ext.isEmpty(hashStr)) hashStr = (window.parent ? window.parent : window).location.hash.substr(1);
		return hashStr;
	};
	var getLocaleHashObj = function(){
		var hashStr = getLocaleHashStr();
		return AgURLParser.parseURL(hashStr);
	};

	var getDateTime = function(){
		return Ext.util.Format.date(new Date(),'YmdGis');
	};

	var createLocaleHashStr = function(hashStr){

	//console.log("createLocaleHashStr():START");

	//	console.log("createLocaleHashStr():START");
	//	console.log("createLocaleHashStr():hashStr=["+hashStr+"]["+Ext.isEmpty(hashStr)+"]["+Ext.isString(hashStr)+"]");
		if((Ext.isEmpty(hashStr) && !Ext.isString(hashStr)) || Ext.isObject(hashStr)) hashStr = getLocaleHashStr();
		if(!Ext.isString(hashStr)) hashStr = getLocaleHashStr();

		var jsonObj = AgURLParser.parseURL(hashStr);
		jsonObj = jsonObj || {};
	//	console.log(jsonObj);

		//Common
	//	jsonObj.Common = jsonObj.Common || AgURLParser.newCommon();
		if(!jsonObj.Common) {
			jsonObj.Common = AgURLParser.newCommon();
	//		jsonObj.Common.Version = null;
		}
		if(!jsonObj.Common.DateTime) jsonObj.Common.DateTime = getDateTime();
		if(!jsonObj.Common.TreeName) jsonObj.Common.TreeName = DEF_TREE;
	//	console.log(jsonObj);

		var p_tree = jsonObj.Common.TreeName;

	/**/
		if(bp3d_parts_store && bp3d_parts_store.sorters.getAt(0).property != 'c_num_'+p_tree){
			bp3d_parts_store.suspendEvents(true);
			bp3d_parts_store.sort([{
				property: 'c_num_'+p_tree,
				direction: 'DESC'
			},{
				property: 'depth_'+p_tree,
				direction: 'ASC'
			},{
				property: 'filesize',
				direction: 'ASC'
			}]);
			bp3d_parts_store.resumeEvents();
		}
	/**/

		//ColorHeatMap
		if(Ext.isBoolean(jsonObj.Common.ColorbarFlag)){
			colorHeatMap.setVisibled(jsonObj.Common.ColorbarFlag);
			if(Ext.isNumber(jsonObj.Common.ScalarMaximum)) colorHeatMap.setScalarMaximum(jsonObj.Common.ScalarMaximum);
			if(Ext.isNumber(jsonObj.Common.ScalarMinimum)) colorHeatMap.setScalarMinimum(jsonObj.Common.ScalarMinimum);
			colorHeatMap.update();
		}else{
			agGrid.setVisibled(false);
		}


		//Window
		jsonObj.Window = jsonObj.Window || AgURLParser.newWindow();

		//Background

		//BackgroundOpacity
		var BackgroundOpacity = 100;
		if(!Ext.isEmpty(jsonObj.Window.BackgroundOpacity)) BackgroundOpacity = (Ext.isNumber(jsonObj.Window.BackgroundOpacity) ? jsonObj.Window.BackgroundOpacity : Number(jsonObj.Window.BackgroundOpacity));
		BackgroundOpacity /= 100;

		//BackgroundColor
		var BackgroundColor = jsonObj.Window.BackgroundColor;
		if(Ext.isString(BackgroundColor)){
			if(BackgroundColor.substr(0,1) == '#') BackgroundColor = BackgroundColor.substr(1);
			BackgroundColor = Number('0x'+BackgroundColor);
		}
		if(renderer) renderer.setClearColor(BackgroundColor,BackgroundOpacity);

		//Grid
		if(Ext.isNumber(jsonObj.Window.GridTickInterval)) agGrid.setGridSpacing(jsonObj.Window.GridTickInterval,true);
		if(Ext.isString(jsonObj.Window.GridColor) && jsonObj.Window.GridColor.length==6){
			var value = Number('0x'+jsonObj.Window.GridColor);
			if(!isNaN(value)) agGrid.setGridColor(value,true);
		}
		if(Ext.isBoolean(jsonObj.Window.GridFlag)) agGrid.setVisibled(jsonObj.Window.GridFlag);


		jsonObj.Window.ImageWidth = SCREEN_WIDTH;
		jsonObj.Window.ImageHeight = SCREEN_HEIGHT;







		//Camera
		jsonObj.Camera = jsonObj.Camera || AgURLParser.newCamera();
		if(
			Ext.isNumber(jsonObj.Camera.CameraX) &&
			Ext.isNumber(jsonObj.Camera.CameraY) &&
			Ext.isNumber(jsonObj.Camera.CameraZ)
		){
			m_ag_cameraPos.x = jsonObj.Camera.CameraX;
			m_ag_cameraPos.y = jsonObj.Camera.CameraY;
			m_ag_cameraPos.z = jsonObj.Camera.CameraZ;
			if(camera) camera.position.copy(m_ag_cameraPos);
		}

		if(
			Ext.isNumber(jsonObj.Camera.CameraUpVectorX) &&
			Ext.isNumber(jsonObj.Camera.CameraUpVectorY) &&
			Ext.isNumber(jsonObj.Camera.CameraUpVectorZ)
		){
			m_ag_upVec.x = jsonObj.Camera.CameraUpVectorX;
			m_ag_upVec.y = jsonObj.Camera.CameraUpVectorY;
			m_ag_upVec.z = jsonObj.Camera.CameraUpVectorZ;
			if(camera) camera.up.copy(m_ag_upVec);
		}

		if(
			Ext.isNumber(jsonObj.Camera.TargetX) &&
			Ext.isNumber(jsonObj.Camera.TargetY) &&
			Ext.isNumber(jsonObj.Camera.TargetZ)
		){
			m_ag_targetPos.x = jsonObj.Camera.TargetX;
			m_ag_targetPos.y = jsonObj.Camera.TargetY;
			m_ag_targetPos.z = jsonObj.Camera.TargetZ;
			if(target) target.copy(m_ag_targetPos);
		}

		if(Ext.isNumber(jsonObj.Camera.Zoom)){
	//		console.log("jsonObj.Camera.Zoom=["+jsonObj.Camera.Zoom+"]");
	//		zoom = jsonObj.Camera.Zoom/5;
			zoom = Math.round(jsonObj.Camera.Zoom*10)/10;
			chengeZoom();
		}
		if(camera){
			camera.updateProjectionMatrix();
			setCameraAndTarget(camera.position, target, camera.up, true);
			calcCameraPos();
		}

		//Legend
		$('#legend-draw-area').html('');
		gLegend = null;
		if(Ext.isObject(jsonObj.Legend) && jsonObj.Legend.DrawLegendFlag){
			gLegend = jsonObj.Legend;
			var text = '';
			if(Ext.isDefined(jsonObj.Legend.LegendTitle)){
				var def_style = 'font-weight:bold;';
				if(Ext.isString(jsonObj.Legend.LegendTitle)){
					if(Ext.String.trim(jsonObj.Legend.LegendTitle).length){
						text += '<span style="'+def_style+'">' + Ext.String.trim(jsonObj.Legend.LegendTitle) + '</span><br/>';
					}
				}else if(Ext.isObject(jsonObj.Legend.LegendTitle)){
					if(Ext.isString(Ext.String.trim(jsonObj.Legend.LegendTitle.text)) && Ext.String.trim(jsonObj.Legend.LegendTitle.text).length){
						var style = def_style;
						if(Ext.isString(jsonObj.Legend.LegendTitle.style) && Ext.String.trim(jsonObj.Legend.LegendTitle.style).length) style = Ext.String.trim(jsonObj.Legend.LegendTitle.style);
						text += '<span style="'+style+'">' + Ext.String.trim(jsonObj.Legend.LegendTitle.text) + '</span><br/>';
					}
				}
			}

			if(Ext.isDefined(jsonObj.Legend.Legend)){
				if(Ext.isString(jsonObj.Legend.Legend)){
					text += '<span>' + Ext.util.Format.nl2br(jsonObj.Legend.Legend).replace(/<br\/>/g,'</span><br/><span>') + '</span><br/>';
				}else if(Ext.isArray(jsonObj.Legend.Legend)){
					var l = [];
					Ext.each(jsonObj.Legend.Legend,function(item,i,a){
						if(Ext.isString(item)){
							l.push('<span>'+item+'</span>');
						}else if(Ext.isObject(item)){
							var style = '';
							if(Ext.isString(item.style) && Ext.String.trim(item.style).length) style = Ext.String.trim(item.style);
							l.push('<span style="'+style+'">' + item.text + '</span>');
						}
					});
					text += l.join('<br/>');
				}
			}

	//		if(!Ext.isEmpty(jsonObj.Legend.LegendAuthor) && !Ext.isEmpty(Ext.String.trim(jsonObj.Legend.LegendAuthor))) text += '<span>' + Ext.String.trim(jsonObj.Legend.LegendAuthor) + '</span><br/>';
			if(Ext.isDefined(jsonObj.Legend.LegendAuthor)){
				var def_style = 'font-style:italic;';
				if(Ext.isString(jsonObj.Legend.LegendAuthor)){
					if(Ext.String.trim(jsonObj.Legend.LegendAuthor).length){
						text += '<span style="'+def_style+'">' + Ext.String.trim(jsonObj.Legend.LegendAuthor) + '</span><br/>';
					}
				}else if(Ext.isObject(jsonObj.Legend.LegendAuthor)){
					if(Ext.isString(jsonObj.Legend.LegendAuthor.text) && Ext.String.trim(jsonObj.Legend.LegendAuthor.text).length){
						var style = def_style;
						if(Ext.isString(jsonObj.Legend.LegendAuthor.style) && Ext.String.trim(jsonObj.Legend.LegendAuthor.style).length) style = Ext.String.trim(jsonObj.Legend.LegendAuthor.style);
						text += '<span style="'+style+'">' + Ext.String.trim(jsonObj.Legend.LegendAuthor.text) + '</span><br/>';
					}
				}
			}

			if(Ext.isString(text) && Ext.String.trim(text).length) $('#legend-draw-area').html('<div>'+Ext.String.trim(text)+'</div>');
		}

		//Pin
		$('#pin-draw-area').html('');
		if(Ext.isArray(jsonObj.Pin)){
			var text = '';
			Ext.each(jsonObj.Pin,function(pin,i,a){
				console.log(pin);
				if(Ext.isEmpty(pin.PinIndicationLineDrawFlag) && Ext.isDefined(jsonObj.Common.PinIndicationLineDrawFlag)) pin.PinIndicationLineDrawFlag = jsonObj.Common.PinIndicationLineDrawFlag;
				var pinText = '';

				if(Ext.isDefined(pin.PinID)){
					var PinID = pin.PinID;
					if(Ext.isNumber(PinID)) PinID += "";
					if(Ext.isString(PinID) && Ext.String.trim(PinID).length) pinText += '<label>' + Ext.String.trim(PinID) + ' : </label>';
				}else if(Ext.isDefined(pin.PinPartID)){
					var PinPartID = pin.PinPartID;
					if(Ext.isNumber(PinPartID)) PinPartID += "";
					if(Ext.isString(PinPartID) && Ext.String.trim(PinPartID).length) pinText += '<label>' + Ext.String.trim(PinPartID) + ' : </label>';
				}
				if(Ext.isString(pin.PinPartName) && Ext.String.trim(pin.PinPartName).length){
					pinText += '<label>' + Ext.String.trim(pin.PinPartName) + ' : </label>';
				}

				if(Ext.isString(pin.PinOrganName) && Ext.String.trim(pin.PinOrganName).length){
					pinText += '<label>' + Ext.String.trim(pin.PinOrganName) + ' : </label>';
				}else if(Ext.isString(pin.PinOrganID) && Ext.String.trim(pin.PinOrganID).length){
					pinText += '<label>' + Ext.String.trim(pin.PinOrganID) + ' : </label>';
				}
				if(Ext.isString(pin.PinDescription) && Ext.String.trim(pin.PinDescription).length) pinText += '<label>' + Ext.String.trim(pin.PinDescription) + ' : </label>';
				if(Ext.isString(pinText) && Ext.String.trim(pinText).length){
					text += '<div><span pinno="'+(i+1)+'"';
					if(Ext.isString(pin.PinDescriptionColor) && Ext.String.trim(pin.PinDescriptionColor).length) text += ' style="color:#'+Ext.String.trim(pin.PinDescriptionColor)+';"';
					for(var key in pin){
						if(Ext.isDefined(pin[key])){
							if(Ext.isString(pin[key])){
								if(Ext.String.trim(pin[key]).length) text += ' '+key+'="'+Ext.String.trim(pin[key])+'"';
							}else if(Ext.isNumber(pin[key]) || Ext.isBoolean(pin[key])){
								text += ' '+key+'="'+pin[key]+'"';
							}
						}
					}
					text += '>'+Ext.String.trim(pinText)+'</span></div>';
				}
			});
			if(Ext.isString(text) && text.length) $('#pin-draw-area').html(text);
		}

		if(bp3d_parts_store) bp3d_parts_store.suspendEvents(false);


		jQuery.each(group_objects.children,function(){
			if(this.visible) this.visible = false;
		});

		self.loadBp3dParts.close();
		self.loadBp3dParts.showLoading();


		//初期化
		for(var path in path2meshs){
			self.loadBp3dParts.hiddenMesh(path);
		}
		if(bp3d_parts_store){
			bp3d_parts_store.each(function(r){
				r.beginEdit();
				r.set('selected',false);
				r.endEdit(true,['selected']);
			});
		}


		if(Ext.isArray(jsonObj.Part) && jsonObj.Part.length && bp3d_parts_store){

			bp3d_parts_store.load({
				params : {keywords:Ext.encode(jsonObj)},
				callback: function(records, operation, success) {
	//				console.log("bp3d_parts_store.load():CALLBACK()");
	//				console.log(records);

					var use_paths = {};
					//対象のメッシュが有る場合、属性を変更する
					Ext.each(records,function(record,i,a){
						var path = self.getRecordPath(record);
						if(self.isEmptyMesh(path)) return true;
						self.loadBp3dParts.setMeshProp(self.getMesh(path),record);
						use_paths[path]=record;
					});

					//対象外のメッシュを非表示
					for(var path in path2meshs){
//					if(Ext.isEmpty(use_paths[path])) loadBp3dParts.hiddenMesh(path2meshs[path]);
						if(Ext.isEmpty(use_paths[path])) self.loadBp3dParts.hiddenMesh(path);
					}

					self.loadBp3dParts.setLoading(false);

					self.loadBp3dParts.task.delay(250);
					self.loadBp3dParts.addMesh();
					self.loadBp3dParts.close();

					extension_parts_store.suspendEvents(true);

					//初期化
					var records = extension_parts_store.getRange();
					for(var i in records){
						var record = records[i];
						var fields = record.fields;
						var modifiedFieldNames = [];
						record.beginEdit();
						for(var j in fields.items){
							if(Ext.isEmpty(fields.items[j].defaultValue)) continue;
							if(record.get(fields.items[j].name) == fields.items[j].defaultValue) continue;
							record.set(fields.items[j].name,fields.items[j].defaultValue);
							modifiedFieldNames.push(fields.items[j].name);
						}
						if(modifiedFieldNames.length>0){
							record.commit(false);
							record.endEdit(false,modifiedFieldNames);
						}else{
							record.cancelEdit();
						}
					}

					if(!Ext.isEmpty(jsonObj.ExtensionPartGroup)){

						for(var i in jsonObj.ExtensionPartGroup){

							var PartGroupName = jsonObj.ExtensionPartGroup[i].PartGroupName;
							var PartGroupPath = jsonObj.ExtensionPartGroup[i].PartGroupPath;

							for(var j in jsonObj.ExtensionPartGroup[i].PartGroupItems){
								var obj = jsonObj.ExtensionPartGroup[i].PartGroupItems[j];
								var path = obj.PartPath;
								if(path.match(/^(.+)\.json$/)){
									path = RegExp.$1+'.obj';
								}

								var isAdd = false;
	//							var record = extension_parts_store.findRecord('path',path,0,false,true,true);
								var idx = extension_parts_store.findBy(function(r,id){
									if(r.get('art_path')==path) return true;
									return false;
								});
								var record = extension_parts_store.getAt(idx);
								if(!record){
									record = Ext.create(extension_parts_store.model.modelName,{});
									isAdd = true;
								}

								var modifiedFieldNames = [];
								record.beginEdit();
								if(record.get('selected') != true){
									record.set('selected',true);
									modifiedFieldNames.push('selected');
								}
								if(!Ext.isEmpty(obj.PartId) && record.get('art_id') != obj.PartId){
									record.set('art_id',obj.PartId);
									modifiedFieldNames.push('art_id');
								}
								if(!Ext.isEmpty(obj.PartName) && record.get('art_name') != obj.PartName){
									record.set('art_name',obj.PartName);
									modifiedFieldNames.push('art_name');
								}
								if(!Ext.isEmpty(obj.PartColor) && record.get('color') != '#'+obj.PartColor){
									record.set('color','#'+obj.PartColor);
									modifiedFieldNames.push('color');
								}
								if(!Ext.isEmpty(obj.PartOpacity) && record.get('opacity') != obj.PartOpacity){
									record.set('opacity',obj.PartOpacity);
									modifiedFieldNames.push('opacity');
								}
								if(!Ext.isEmpty(obj.PartDeleteFlag) && record.get('remove') != obj.PartDeleteFlag){
									record.set('remove',obj.PartDeleteFlag);
									modifiedFieldNames.push('remove');
								}
								if(!Ext.isEmpty(obj.UseForBoundingBoxFlag) && record.get('focused') != obj.UseForBoundingBoxFlag){
									record.set('focused',obj.UseForBoundingBoxFlag);
									modifiedFieldNames.push('focused');
								}
								if(!Ext.isEmpty(obj.PartRepresentation) && record.get('representation') != obj.PartRepresentation){
									record.set('representation',obj.PartRepresentation);
									modifiedFieldNames.push('representation');
								}

								if(Ext.isNumber(obj.PartScalar)){
									if(record.get('scalar') != obj.PartScalar){
										record.set('scalar',obj.PartScalar);
										modifiedFieldNames.push('scalar');
									}
								}else{
									record.set('scalar',null);
									modifiedFieldNames.push('scalar');
								}
								if(Ext.isBoolean(obj.PartScalarFlag)){
									if(record.get('scalar_flag') != obj.PartScalarFlag){
										record.set('scalar_flag',obj.PartScalarFlag);
										modifiedFieldNames.push('scalar_flag');
									}
								}else{
									record.set('scalar_flag',false);
									modifiedFieldNames.push('scalar_flag');
								}

								if(record.get('art_path') != path){
									record.set('art_path',path);
									modifiedFieldNames.push('art_path');
								}
								if(!Ext.isEmpty(obj.PartMTime) && record.get('art_timestamp') != obj.PartMTime){
									record.set('art_timestamp',obj.PartMTime);
									modifiedFieldNames.push('art_timestamp');
								}
								if(modifiedFieldNames.length>0){
									record.commit(false);
									record.endEdit(false,modifiedFieldNames);
								}else{
									record.cancelEdit();
								}
								if(isAdd){
									extension_parts_store.add(record);
								}
							}
						}
					}

					bp3d_parts_store.resumeEvents();
					extension_parts_store.resumeEvents();

					self.loadBp3dParts.addMesh();

					setHash(Ext.JSON.encode(jsonObj));

					self.loadBp3dParts.hideLoadingTask.delay(250);

					render();//描画されない場合がある為、ここで描画をコールしておく
				}
			});
			return;


		}else{
			self.loadBp3dParts.setLoading(false);

			self.loadBp3dParts.task.delay(250);
			self.loadBp3dParts.addMesh();
			self.loadBp3dParts.close();
		}

	//	self.loadBp3dParts.task.delay(250);
	//	self.loadBp3dParts.addMesh();
	//	self.loadBp3dParts.close();

	//	console.log("createLocaleHashStr():extension_parts_store");

		extension_parts_store.suspendEvents(true);

		//初期化
		var records = extension_parts_store.getRange();
		for(var i in records){
			var record = records[i];
			var fields = record.fields;
			var modifiedFieldNames = [];
			record.beginEdit();
			for(var j in fields.items){
				if(Ext.isEmpty(fields.items[j].defaultValue)) continue;
				if(record.get(fields.items[j].name) == fields.items[j].defaultValue) continue;
				record.set(fields.items[j].name,fields.items[j].defaultValue);
				modifiedFieldNames.push(fields.items[j].name);
			}
			if(modifiedFieldNames.length>0){
				record.commit(false);
				record.endEdit(false,modifiedFieldNames);
			}else{
				record.cancelEdit();
			}
		}

		if(!Ext.isEmpty(jsonObj.ExtensionPartGroup)){

			for(var i in jsonObj.ExtensionPartGroup){

				var PartGroupName = jsonObj.ExtensionPartGroup[i].PartGroupName;
				var PartGroupPath = jsonObj.ExtensionPartGroup[i].PartGroupPath;

				for(var j in jsonObj.ExtensionPartGroup[i].PartGroupItems){
					var obj = jsonObj.ExtensionPartGroup[i].PartGroupItems[j];
	//				var path = PartGroupPath+'/'+obj.PartPath;
					var path = obj.PartPath;
					if(Ext.isString(path) && path.match(/^(.+)\.json$/)){
						path = RegExp.$1+'.obj';
					}

					var isAdd = false;
	//				var record = extension_parts_store.findRecord('path',path,0,false,true,true);
					var idx = extension_parts_store.findBy(function(r,id){
						if(r.get('art_path')==path) return true;
						return false;
					});
					var record = extension_parts_store.getAt(idx);
					if(!record){
						record = Ext.create(extension_parts_store.model.modelName,{});
						isAdd = true;
					}

					var modifiedFieldNames = [];
					record.beginEdit();
					if(record.get('selected') != true){
						record.set('selected',true);
						modifiedFieldNames.push('selected');
					}
					if(!Ext.isEmpty(obj.PartId) && record.get('art_id') != obj.PartId){
						record.set('art_id',obj.PartId);
						modifiedFieldNames.push('art_id');
					}
					if(!Ext.isEmpty(obj.PartName) && record.get('art_name') != obj.PartName){
						record.set('art_name',obj.PartName);
						modifiedFieldNames.push('art_name');
					}
					if(!Ext.isEmpty(obj.PartColor) && record.get('color') != '#'+obj.PartColor){
						record.set('color','#'+obj.PartColor);
						modifiedFieldNames.push('color');
					}
					if(!Ext.isEmpty(obj.PartOpacity) && record.get('opacity') != obj.PartOpacity){
						record.set('opacity',obj.PartOpacity);
						modifiedFieldNames.push('opacity');
					}
					if(!Ext.isEmpty(obj.PartDeleteFlag) && record.get('remove') != obj.PartDeleteFlag){
						record.set('remove',obj.PartDeleteFlag);
						modifiedFieldNames.push('remove');
					}
					if(!Ext.isEmpty(obj.UseForBoundingBoxFlag) && record.get('focused') != obj.UseForBoundingBoxFlag){
						record.set('focused',obj.UseForBoundingBoxFlag);
						modifiedFieldNames.push('focused');
					}
					if(!Ext.isEmpty(obj.PartRepresentation) && record.get('representation') != obj.PartRepresentation){
						record.set('representation',obj.PartRepresentation);
						modifiedFieldNames.push('representation');
					}

					if(Ext.isNumber(obj.PartScalar)){
						if(record.get('scalar') != obj.PartScalar){
							record.set('scalar',obj.PartScalar);
							modifiedFieldNames.push('scalar');
						}
					}else{
						record.set('scalar',null);
						modifiedFieldNames.push('scalar');
					}
					if(Ext.isBoolean(obj.PartScalarFlag)){
						if(record.get('scalar_flag') != obj.PartScalarFlag){
							record.set('scalar_flag',obj.PartScalarFlag);
							modifiedFieldNames.push('scalar_flag');
						}
					}else{
						record.set('scalar_flag',false);
						modifiedFieldNames.push('scalar_flag');
					}

					if(record.get('art_path') != path){
						record.set('art_path',path);
						modifiedFieldNames.push('art_path');
					}
					if(!Ext.isEmpty(obj.PartMTime) && record.get('art_timestamp') != obj.PartMTime){
						record.set('art_timestamp',obj.PartMTime);
						modifiedFieldNames.push('art_timestamp');
					}
					if(modifiedFieldNames.length>0){
						record.commit(false);
						record.endEdit(false,modifiedFieldNames);
					}else{
						record.cancelEdit();
					}
					if(isAdd){
						extension_parts_store.add(record);
					}
				}
			}
		}



		if(bp3d_parts_store) bp3d_parts_store.resumeEvents();
		extension_parts_store.resumeEvents();

		self.loadBp3dParts.addMesh();

		setHash(Ext.JSON.encode(jsonObj));

		self.loadBp3dParts.hideLoadingTask.delay(250);

		render();//描画されない場合がある為、ここで描画をコールしておく
	};


	var hashChange = function(e){
		createLocaleHashStr(window.location.hash.substr(1));
	};
	var hashChangeAddEventListenerTask = new Ext.util.DelayedTask(function(){
		window.addEventListener( 'hashchange', hashChange, false );
	});

	var setHash = function(hashStr){
		if(glb_hashStr == hashStr){
			return;
		}

	//	console.log("setHash()");
	//	console.log(getLocaleHashObj());
		glb_hashStr = hashStr;
	//	console.log(getLocaleHashObj());


		hashChangeAddEventListenerTask.cancel();
		window.removeEventListener( 'hashchange', hashChange, false );
		Ext.defer(function(){
			if(window.parent && window.parent == window){
	//			hashStr = encodeURIComponent(hashStr);
	//			window.location.hash = hashStr;
			}else{
	//			$(window).trigger('createLocaleHashStr',[{hash:glb_hashStr}]);
			}

				$(window).trigger('createLocaleHashStr',[{hash:glb_hashStr}]);

			hashChangeAddEventListenerTask.delay(0);
		},250);

		render();
	};
	var updateCameraHash = function(){
		var jsonObj = getLocaleHashObj();
		jsonObj = jsonObj || {};
		jsonObj.Camera = jsonObj.Camera || AgURLParser.newCamera();

		jsonObj.Camera.CameraX = m_ag_cameraPos.x;
		jsonObj.Camera.CameraY = m_ag_cameraPos.y;
		jsonObj.Camera.CameraZ = m_ag_cameraPos.z;

		jsonObj.Camera.CameraUpVectorX = m_ag_upVec.x;
		jsonObj.Camera.CameraUpVectorY = m_ag_upVec.y;
		jsonObj.Camera.CameraUpVectorZ = m_ag_upVec.z;

		jsonObj.Camera.TargetX = m_ag_targetPos.x;
		jsonObj.Camera.TargetY = m_ag_targetPos.y;
		jsonObj.Camera.TargetZ = m_ag_targetPos.z;

	//	jsonObj.Camera.Zoom = Math.round(zoom*5);
		jsonObj.Camera.Zoom = Math.round(zoom*10)/10;

		if(!Ext.isEmpty(jsonObj.Part)){
			for(var i in jsonObj.Part){
				var obj = jsonObj.Part[i];
				if(!Ext.isEmpty(obj.UseForBoundingBoxFlag)) obj.UseForBoundingBoxFlag = null;
			}
		}

		if(!Ext.isEmpty(jsonObj.ExtensionPartGroup)){
			for(var i in jsonObj.ExtensionPartGroup){
				for(var j in jsonObj.ExtensionPartGroup[i].PartGroupItems){
					var obj = jsonObj.ExtensionPartGroup[i].PartGroupItems[j];
					if(!Ext.isEmpty(obj.UseForBoundingBoxFlag)) obj.UseForBoundingBoxFlag = null;
				}
			}
		}

		setHash(Ext.JSON.encode(jsonObj));
	};



	//var xm;
	//var xm = new THREE.MeshBasicMaterial( { map: new THREE.Texture( x, new THREE.UVMapping(), THREE.RepeatWrapping, THREE.RepeatWrapping ) } );
	//xm.map.needsUpdate = true;
	//xm.map.repeat.set( 10, 10 );

	self.getRecordPath = function(record){
		if(Ext.isEmpty(record.get('art_path'))){
			console.warn('art_path=null',record.getData());
			return null;
		}
		var path = '';
		path += record.get('art_path');
		var paths = path.split('/');
		Ext.each(paths,function(p,i,a){
			paths[i] = encodeURIComponent(p);
		});
		path = paths.join('/');
		return path;
	};

	self.loadBp3dParts = {
		_records : [],
		_cnt : 0,
		_num : 0,
		_progress : null,
		_loadMask : null,

		setLoading : function(load,targetEl){
			var me = Ext.getCmp('center-panel'),config;
			if(me && me.rendered){
				if(load !== false && !me.collapsed){
					if(Ext.isEmpty(me.loadMask)){
						if(Ext.isObject(load)){
							config = Ext.apply({}, load);
						}else if(Ext.isString(load)){
							config = {msg: load};
						}else{
							config = {};
						}
						if(targetEl){
							Ext.applyIf(config, {useTargetEl: true});
						}
//						me.loadMask = new Ext.LoadMask(me, config);
						config.target = me;
						me.loadMask = new Ext.LoadMask(config);

						$(window).trigger('showLoading');
	//					console.log("trigger('showLoading')");

						me.loadMask.show();
					}
				}else{
					if(!Ext.isEmpty(me.loadMask)){
						Ext.destroy(me.loadMask);
						me.loadMask = null;
						$(window).trigger('hideLoading');
	//					console.log("trigger('hideLoading')");
					}
				}
			}
		},

		showLoading : function(){
			self.loadBp3dParts.hideLoadingTask.cancel();
			self.loadBp3dParts.setLoading('Please wait...');
		},

		hideLoading : function(){
			self.loadBp3dParts.hideLoadingTask.cancel();
			if(bp3d_parts_store && (!bp3d_parts_store.isLoaded || bp3d_parts_store.isLoading())){//初期化時
				self.loadBp3dParts.hideLoadingTask.delay(250);
			}else{
				self.loadBp3dParts.setLoading(false);
			}
		},

		hideLoadingTask : new Ext.util.DelayedTask(function(){
			self.loadBp3dParts.hideLoading();
		}),

		mask : function(msg){
			if(Ext.isEmpty(msg)) msg = '';

			self.loadBp3dParts.hideLoading();

			if(Ext.isEmpty(self.loadBp3dParts._progress)){
				self.loadBp3dParts._progress = Ext.Msg.show({
					closable : false,
					modal    : true,
					msg      : msg,
					progress : true,
					title    : 'Loading...'
				});
			}
			self.loadBp3dParts._cnt++;
			self.loadBp3dParts._progress.updateProgress(self.loadBp3dParts._cnt/(self.loadBp3dParts._num+1),self.loadBp3dParts._cnt+'/'+self.loadBp3dParts._num,msg).center();
		},

		unmask : function(){
			if(self.loadBp3dParts._cnt>=self.loadBp3dParts._num){
				if(self.loadBp3dParts._progress) self.loadBp3dParts._progress.updateProgress(self.loadBp3dParts._cnt/self.loadBp3dParts._num,self.loadBp3dParts._cnt+'/'+self.loadBp3dParts._num).center();
				self.loadBp3dParts.closeTask.delay(750);
			}
		},

		close : function(){
			self.loadBp3dParts._records.length = 0;
			if(self.loadBp3dParts._progress && self.loadBp3dParts._progress.close) self.loadBp3dParts._progress.close();
			self.loadBp3dParts._progress = null;
		},

		closeTask : new Ext.util.DelayedTask(function(){
			self.loadBp3dParts.close();
		}),

		createMesh : function( param ) {
			if(Ext.isEmpty(param)) param = {};



			var material;
			material = new THREE.MeshLambertMaterial({
	//		material = new THREE.MeshBasicMaterial({
				ambient     : Ext.isEmpty(param.color) ? DEF_COLOR_HEX : param.color,
				color       : Ext.isEmpty(param.color) ? DEF_COLOR_HEX : param.color,

	//				blending:THREE.NoBlending,
	//				blending:THREE.NormalBlending,
	//				blending:THREE.AdditiveBlending,
	//				blending:THREE.SubtractiveBlending,
	//				blending:THREE.MultiplyBlending,
				blending:THREE.AdditiveAlphaBlending,

				opacity     : Ext.isEmpty(param.opacity) ? 1: param.opacity,
				transparent : false,
				shading     : THREE.SmoothShading,
				wireframe   : Ext.isEmpty(param.representation) ? false : param.representation == 'wireframe' ? true : false
			})

			var mesh = new THREE.Mesh(
				param.geometry,
				material
			);
			mesh.position.set( param.position.x, param.position.y, param.position.z );
	//		mesh.doubleSided = true;
			mesh.visible = Ext.isEmpty(param.visible) ? false : param.visible;


	//		mesh.overdraw = true;

		//	console.log("createMesh():mesh.visible=["+mesh.visible+"]");

			return mesh;
		},

		addMesh : function(mesh){
			if(!Ext.isEmpty(mesh)){
				group_objects.add(mesh);
/*
				console.log(mesh);
				var text = document.createElement( 'div' );
				text.className = 'pin_label';
				text.style.color = '#0000ff';
				text.textContent = mesh.id;
				console.log($(text).height());

				var label = new THREE.CSS2DObject( text );
				label.position.copy( mesh.geometry.boundingBox.max );
//				label.position.copy( convertCoordinateScreenTo3D(0,0) );
				group_pins.add( label );
//				console.log($(text).height());
//				console.log($(label.element).height());

//				console.log(convertCoordinateScreenTo3D(0,0));
//				console.log(label);
*/
			}
			intersect_target_objects.length = 0;
			intersect_target_objects_all.length = 0;
			jQuery.each(group_objects.children,function(){
//				this.renderDepth = this.material.opacity;
				this.renderOrder = this.material.opacity;
	//			console.log("addMesh():opacity=["+this.visible+"]["+this.material.opacity+"]["+this.name+"]")
				if(this.visible){
					if(this.material.opacity==1) intersect_target_objects.push(this);
					if(this.material.opacity>0) intersect_target_objects_all.push(this);
				}
			});
			render();
		},

	//	hiddenMesh : function(mesh){
		hiddenMesh : function(path){
	//		mesh.visible = false;
			setMeshVisible(path,false);
		},

		setMeshProp : function(mesh,record){
	//		mesh.visible = record.get('remove') ? false : record.get('selected');
			setMeshVisible(mesh.name,record.get('remove') ? false : record.get('selected'));
			if(!mesh.visible) return;

			if(mesh.visible){
				var color;
				if(colorHeatMap.isVisibled() && record.get('scalar_flag') && Ext.isNumber(record.get('scalar'))){
					color = colorHeatMap.calcColorValue(record.get('scalar'));
				}else{
					color = record.get('color');
					if(color.substr(0,1) == '#') color = color.substr(1);
					color = Number('0x'+color);
				}

	//			if(mesh.material instanceof THREE.MeshLambertMaterial){
	//				mesh.material = new THREE.ShaderMaterial({
	//					fragmentShader: THREE.ShaderUtils.lib.normal.fragmentShader,
	//					vertexShader: THREE.ShaderUtils.lib.normal.vertexShader,
	//					uniforms: THREE.ShaderUtils.lib.normal.uniforms
	//				});
	//				if(mesh.material.ambient === undefined) mesh.material.ambient = new THREE.Color();
	//				if(mesh.material.color === undefined) mesh.material.color = new THREE.Color();
	//			}

//				mesh.material.ambient.setHex( color );
				mesh.material.color.setHex( color );
				mesh.material.opacity = record.get('opacity');
				mesh.material.wireframe = Ext.isEmpty(record.get('representation')) ? false : record.get('representation') == 'wireframe' ? true : false;


				mesh.material.blending = THREE.NormalBlending;
				mesh.material.side = THREE.FrontSide;
				mesh.doubleSided = false;
				mesh.material.depthWrite = true;
				mesh.material.transparent = false;

				if(record.get('opacity')<1){
					mesh.material.depthWrite = false;
					mesh.material.transparent = true;
					mesh.doubleSided = true;
					mesh.material.side = THREE.DoubleSide;
				}
			}
		},

		setMeshParam : function(mesh,record){
			var path = self.getRecordPath(record);

			if(mesh && mesh.geometry && !mesh.geometry.boundingBox) mesh.geometry.computeBoundingBox();

			self.setMesh(path,mesh);
			self.getMesh(path).record = record;
			self.getMesh(path).name = path;

	//		var mesh1 = new THREE.Mesh(
	//			mesh.geometry,
	//			mesh.material.clone()
	//		);
	//		mesh1.material.side = THREE.FrontSide;

	//		var mesh2 = new THREE.Mesh(
	//			mesh.geometry,
	//			mesh.material.clone()
	//		);
	//		mesh2.material.side = THREE.BackSide;

			self.loadBp3dParts.setMeshProp(mesh,record);

			if(Ext.isBoolean(record.get('focused'))){
				if(record.get('focused')){
					self.loadBp3dParts._focused.zoom.push(mesh);
				}else{
					self.loadBp3dParts._focused.center.push(mesh);
				}
				record.store.suspendEvents(false);
				record.set('focused',null);
				record.commit(false);
				record.endEdit(false,['focused']);
				record.store.resumeEvents();
			}

			self.loadBp3dParts.addMesh(mesh);
	//		self.loadBp3dParts.addMesh(mesh1);
	//		self.loadBp3dParts.addMesh(mesh2);

			self.loadBp3dParts.unmask();
			self.loadBp3dParts.exec();
		},

		exec : function(){
			var records = self.loadBp3dParts._records;
			while(!Ext.isEmpty(records)){

				var record = records.shift();

				var path = self.getRecordPath(record);
				if(Ext.isEmpty(path)) continue;

				if(record.get('selected')){

					if(!self.isEmptyMesh(path)){
						setMeshVisible(path,record.get('remove') ? false : record.get('selected'));

						if(Ext.isBoolean(record.get('focused'))){
							if(record.get('focused')){
								self.loadBp3dParts._focused.zoom.push(self.getMesh(path));
							}else{
								self.loadBp3dParts._focused.center.push(self.getMesh(path));
							}
							record.store.suspendEvents(false);
							record.set('focused',null);
							record.commit(false);
							record.endEdit(false,['focused']);
							record.store.resumeEvents();
						}
						continue;
					}

					if(record.get('remove')){
						continue;
					}

					var name = record.get('art_name');
					if(record.get('cdi_name') && record.get('art_id')){
						name = record.get('cdi_name') + ' - ' + record.get('art_id');
					}else if(record.get('cdi_name')){
						name = record.get('cdi_name');
					}else if(record.get('art_id')){
						name = Ext.util.Format.format('[ {0} ] {1}', record.get('art_id'), name);
					}
					self.loadBp3dParts.mask(name +  (Ext.isEmpty(record.get('art_data_size')) || record.get('art_data_size') == 0 ? '' : ' ['+ Ext.util.Format.fileSize(record.get('art_data_size')) + ']'));


					var url = path;
					try{
						url+='?_dc='+Math.floor(record.get('art_timestamp').getTime()/1000);
					}catch(e){
						console.error(e);
					}
					Ext.Ajax.request({
						url: url,
						method: 'HEAD',
						callback: function(options,success,response){
							if(response.status != 200){
								url = 'load-obj.cgi?path=' + encodeURIComponent(path);
								try{
									url+='&_dc='+Math.floor(record.get('art_timestamp').getTime()/1000);
								}catch(e){
									console.error(e);
								}
							}
							objLoader.load(url,function(event){
								var object = event.content ? event.content : event;
								var mesh = object.children.shift();
								mesh.name = path;
								self.loadBp3dParts.setMeshParam(mesh,record);
							});
						}
					});

					break;
//					return;

				}else if(!self.isEmptyMesh(path)){
//				path2meshs[path].visible = false;
					setMeshVisible(path,false);
				}
			}
			if(records.length==0){
	//			console.log("loadBp3dParts.exec(zoom)["+loadBp3dParts._focused.zoom.length+"]");
	//			console.log("loadBp3dParts.exec(center)["+loadBp3dParts._focused.center.length+"]");
				if(self.loadBp3dParts._focused.zoom.length>0){
					var max;
					var min;
					var all_max;
					var all_min;
					Ext.each(self.loadBp3dParts._focused.zoom,function(mesh,i,a){
						mesh.geometry.computeBoundingBox();
						var bb = mesh.geometry.boundingBox;
						if(mesh.visible){
							if(Ext.isEmpty(min)) min = bb.min.clone();
							if(Ext.isEmpty(max)) max = bb.max.clone();

							min.x = Math.min(min.x,bb.min.x);
							min.y = Math.min(min.y,bb.min.y);
							min.z = Math.min(min.z,bb.min.z);

							max.x = Math.max(max.x,bb.max.x);
							max.y = Math.max(max.y,bb.max.y);
							max.z = Math.max(max.z,bb.max.z);
						}

						if(Ext.isEmpty(all_min)) all_min = bb.min.clone();
						if(Ext.isEmpty(all_max)) all_max = bb.max.clone();

						all_min.x = Math.min(all_min.x,bb.min.x);
						all_min.y = Math.min(all_min.y,bb.min.y);
						all_min.z = Math.min(all_min.z,bb.min.z);

						all_max.x = Math.max(all_max.x,bb.max.x);
						all_max.y = Math.max(all_max.y,bb.max.y);
						all_max.z = Math.max(all_max.z,bb.max.z);

					});
					var offset = new THREE.Vector3();
					var size = new THREE.Vector3();
					if(max && min){
						offset.addVectors( max, min );
						size.subVectors( max, min );
					}else{
						offset.addVectors( all_max, all_min );
						size.subVectors( all_max, all_min );
					}
					offset.multiplyScalar( 0.5 );

	//				var distance = Math.sqrt(Math.pow(max.x-min.x,2)+Math.pow(max.y-min.y,2)+Math.pow(max.z-min.z,2));
	//				console.log("distance=["+distance+"]");
	//				console.log("distance=["+getYRangeZoom(distance)+"]");


	//console.log(offset);
	//console.log(size);
	//console.log(max);
	//console.log(min);

					var yrange = Math.max(size.x,size.y,size.z);
//					var yrange = Math.max(size.x,size.y,size.z,Math.pow(size.x*size.x + size.y*size.y + size.z*size.z, 0.46));
	//		console.log("yrange=["+yrange+"]");
					zoom = getYRangeZoom(yrange);
	//		console.log("zoom=["+zoom+"]");
					zoom = Math.floor(zoom/0.2) * 0.2;
	//		console.log("zoom=["+zoom+"]");
	//		yrange = getZoomYRange(zoom);
	//		console.log("yrange=["+yrange+"]");
					chengeZoom();

	//		console.log("yrange=["+yrange+"]");
	//		console.log("yrange=["+getYRangeZoom(yrange)+"]");

	//if(size.x > size.y && size.x > size.z){
	//	console.log("x=["+getYRangeZoom(size.x)+"]");
	//}else if(size.y > size.x && size.y > size.z){
	//	console.log("y=["+getYRangeZoom(size.y)+"]");
	//}else if(size.z > size.x && size.z > size.y){
	//	console.log("z=["+getYRangeZoom(size.z)+"]");
	//}
					m_ag_targetPos.copy(offset);
					moveTarget(0,0);

				}else if(self.loadBp3dParts._focused.center.length>0){

					var max;
					var min;
					var all_max;
					var all_min;
					Ext.each(self.loadBp3dParts._focused.center,function(mesh,i,a){
						mesh.geometry.computeBoundingBox();
						var bb = mesh.geometry.boundingBox;
						if(mesh.visible){
							if(Ext.isEmpty(min)) min = bb.min.clone();
							if(Ext.isEmpty(max)) max = bb.max.clone();

							min.x = Math.min(min.x,bb.min.x);
							min.y = Math.min(min.y,bb.min.y);
							min.z = Math.min(min.z,bb.min.z);

							max.x = Math.max(max.x,bb.max.x);
							max.y = Math.max(max.y,bb.max.y);
							max.z = Math.max(max.z,bb.max.z);
						}

						if(Ext.isEmpty(all_min)) all_min = bb.min.clone();
						if(Ext.isEmpty(all_max)) all_max = bb.max.clone();

						all_min.x = Math.min(all_min.x,bb.min.x);
						all_min.y = Math.min(all_min.y,bb.min.y);
						all_min.z = Math.min(all_min.z,bb.min.z);

						all_max.x = Math.max(all_max.x,bb.max.x);
						all_max.y = Math.max(all_max.y,bb.max.y);
						all_max.z = Math.max(all_max.z,bb.max.z);
					});
					var offset = new THREE.Vector3();
					if(max && min){
						offset.addVectors( max, min );
					}else{
						offset.addVectors( all_max, all_min );
					}
					offset.multiplyScalar( 0.5 );

					m_ag_targetPos.copy(offset);
					moveTarget(0,0);


				}


				camera.position.copy(m_ag_cameraPos);
				camera.up.copy(m_ag_upVec);
				target.copy(m_ag_targetPos);


				if(bp3d_parts_store){
					bp3d_parts_store.suspendEvents(false);
					Ext.each(bp3d_parts_store.getRange(),function(record,i,a){
						if(!Ext.isBoolean(record.get('focused'))) return true;
						record.beginEdit();
						record.set('focused',null);
						record.commit(false);
						record.endEdit(false,['focused']);
					});
					bp3d_parts_store.resumeEvents();
				}

				extension_parts_store.suspendEvents(false);
				Ext.each(extension_parts_store.getRange(),function(record,i,a){
					if(!Ext.isBoolean(record.get('focused'))) return true;
					record.beginEdit();
					record.set('focused',null);
					record.commit(false);
					record.endEdit(false,['focused']);
				});
				extension_parts_store.resumeEvents();

				updateCameraHash();
			}

		},
		task : new Ext.util.DelayedTask(function(){

			if(bp3d_parts_store) bp3d_parts_store.suspendEvents(false);
			extension_parts_store.suspendEvents(false);

			if(bp3d_parts_store) bp3d_parts_store.clearFilter();
			extension_parts_store.clearFilter();

			if(bp3d_parts_store){
				bp3d_parts_store.filterBy(function(record,id){
					if(!record.get('selected')) return false;
					if(record.get('remove')) return false;
					var path = self.getRecordPath(record);
					if(Ext.isEmpty(path)) return false;
					if(!self.isEmptyMesh(path)) return false;
					return true;
				});
			}
			extension_parts_store.filterBy(function(record,id){
				if(!record.get('selected')) return false;
				if(record.get('remove')) return false;
				var path = self.getRecordPath(record);
				if(Ext.isEmpty(path)) return false;
				if(!self.isEmptyMesh(path)) return false;
				return record.get('selected');
			});
			self.loadBp3dParts._cnt = 0;
			self.loadBp3dParts._num = bp3d_parts_store ? bp3d_parts_store.getRange().length : 0;
			self.loadBp3dParts._num += extension_parts_store.getRange().length;

			self.loadBp3dParts._focused = {
				'zoom' : [],
				'center' : []
			};

			if(bp3d_parts_store) bp3d_parts_store.clearFilter();
			extension_parts_store.clearFilter();

			if(bp3d_parts_store) bp3d_parts_store.resumeEvents();
			extension_parts_store.resumeEvents();

			self.loadBp3dParts._records = bp3d_parts_store ? bp3d_parts_store.getRange().concat(extension_parts_store.getRange()) : [];
			self.loadBp3dParts.exec();

		})
	};

	var createLocaleHashStrTask = new Ext.util.DelayedTask(function(){
		if(bp3d_parts_store && bp3d_parts_store.isLoading()) return;
	//	console.log("createLocaleHashStrTask()");
		createLocaleHashStr();
	});



























	Ext.QuickTips.init();
	//	Ext.state.Manager.setProvider(new Ext.state.CookieProvider()); //ソート順とかをCookieに登録する為に必要らしい

	var viewport = Ext.create('Ext.container.Viewport', {
		layout: 'border',
		items: [{
			id:'center-panel',
			region: 'center',
			border:false,
			listeners : {
				afterrender : function(panel){
//						console.log('center.afterrender');
//						panel.loadMask = new Ext.LoadMask(panel.body);


						panel.tip = Ext.create('Ext.tip.ToolTip', {
							hideMode: 'visibility',
							renderTo: Ext.getBody()
						});
						objTip = panel.tip;


				},
				resize : function(panel,adjWidth,adjHeight,rawWidth,rawHeight){
//						console.log('center.resize');
					resize(adjWidth,adjHeight);
				}
			}
		},{
			hidden: DEBUG ? false : (Ext.isEmpty(window.opener)?true:false),
			id:'north-panel',
			region: 'north',
			border:false,
			height:25,
			tbar : [{
				xtype:'label',
				text:'H:'
			},{
				xtype:'numberfield',
				id:'rotateH',
				width:54,
				value:0,
				readOnly:true,
				allowBlank:false,
				listeners : {
					change: function(field, newValue, oldValue, eOpts){
						$(window).trigger('changeLongitudeDegree',[newValue, oldValue]);
					}
				}
			},{
				xtype:'tbspacer',
				width:5
			},{
				xtype:'label',
				text:'V:'
			},{
				xtype:'numberfield',
				id:'rotateV',
				width:54,
				value:0,
				readOnly:true,
				allowBlank:false,
				listeners : {
					change: function(field, newValue, oldValue, eOpts){
						$(window).trigger('changeLatitudeDegree',[newValue, oldValue]);
					}
				}
			},{
				xtype:'tbspacer',
				width:5
			},{
				xtype:'label',
				text:'Zoom:'
			},{
				xtype:'numberfield',
				id:'zoom-value-text',
				width:44,
				value:1,
				readOnly:true,
				allowBlank:false,
				listeners : {
					change: function(field, newValue, oldValue, eOpts){
						$(window).trigger('changeZoom',[newValue, oldValue]);
					}
				}
			},'-',{
				hidden: DEBUG ? false : true,
				xtype:'numberfield',
				id:'camera-near',
				width:54,
				value:cameraConfig.near,
				readOnly:true,
				allowBlank:false,
				listeners : {
					afterrender: function(field, eOpts){
						$(window).trigger('changeCameraNear',[field.value]);
					},
					change: function(field, newValue, oldValue, eOpts){
						$(window).trigger('changeCameraNear',[newValue, oldValue]);
					}
				}
			},{
				hidden: DEBUG ? false : true,
				xtype:'numberfield',
				id:'camera-far',
				width:54,
				value:cameraConfig.far,
				readOnly:true,
				allowBlank:false,
				listeners : {
					afterrender: function(field, eOpts){
						$(window).trigger('changeCameraFar',[field.value]);
					},
					change: function(field, newValue, oldValue, eOpts){
						$(window).trigger('changeCameraFar',[newValue, oldValue]);
					}
				}
			},'->','-',{
				hidden: DEBUG ? false : true,
				id: 'click-mode-menu',
				xtype:'cycle',
				iconCls:'plus-btn',
				showText: true,
				tooltip: 'Click mode',
				menu: {
					width: 100,
					items: [{
						id: 'click-mode-menu-pick',
						text: 'Pick',
						iconCls: 'cursor-btn',
						checked: true,
						value: 'clickmode.pick'
					},{
						id: 'click-mode-menu-pin',
						text: 'Pin',
						iconCls: 'pin-btn',
						value: 'clickmode.pin'
					}]
				},
				changeHandler: function(cycleBtn, activeItem) {
//						Ext.Msg.alert('Change View', activeItem.value);
//						console.log(activeItem.value);
				}
			},{
				xtype: 'tbseparator',
				hidden: DEBUG ? false : true,
			},{
				tooltip: 'Options',
				iconCls: 'gear-btn',
				menu: new Ext.menu.Menu({
					items: [{
						xtype:'menuitem',
						text: 'Display',
						menu: {

							defaultType: 'menucheckitem',
							defaults: {
								hideOnClick: true,
								clickHideDelay: 250
							},
							items: [{
								id: 'options-guide',
								text: 'Guide',
								checked: true,
								listeners : {
									checkchange: function(menuItem, checked, eOpts){
//											console.log("checkchange():["+menuItem.id+"]");
										if(subRenderer) Ext.get(subRenderer.domElement).setVisible(checked);
									}
								}
							},{
								id: 'options-tooltip',
								text: 'ToolTip',
								checked: false,
								listeners : {
									checkchange: function(menuItem, checked, eOpts){
										if(checked){
//											console.log('addEventListener(mousemove)');
											$(container).bind( 'mousemove', onObjectMouseMove);
										}else{
//											console.log('removeEventListener(mousemove)');
											$(container).unbind( 'mousemove', onObjectMouseMove);
										}
									}
								}
							},{xtype: 'menuseparator'},{
								id: 'options-stats',
								text: 'Stats',
								checked: true,
								listeners : {
									checkchange: function(menuItem, checked, eOpts){
										if(stats) Ext.get(stats.domElement).setVisible(checked);
									}
								}
							}]
						}
					}]
				})
			}]
		}],
		listeners : {
			afterrender : function(viewport){
//					console.log('viewport.afterrender');


				self.loadBp3dParts.showLoading();

//					var body = Ext.getCmp('center-panel').body;
				var id = 'center-panel';
				var body = Ext.get(id+'-innerCt');
				if(Ext.isEmpty(body)) body = Ext.getCmp(id).body;

/**/
				init(body.dom);
				$('<canvas id="canvas2D" width='+body.getWidth()+' height='+body.getHeight()+'>')
				.appendTo($(body.dom))
				.css({
					position : 'absolute',
					left     : '0px',
					top      : '0px',
					zIndex   : 99
				});
/**/




				subRenderer = new AgSubRenderer();
//					subRenderer.domElement.style.position = 'absolute';
				subRenderer.domElement.style.position = 'relative';
				subRenderer.domElement.style.left = '0px';
				subRenderer.domElement.style.top = '0px';
//					subRenderer.domElement.style.right = '0px';
				subRenderer.domElement.style.zIndex = 100;
				subRenderer.domElement.style.marginRight = '4px';
				subRenderer.domElement.style.marginBottom = '0px';
				subRenderer.domElement.style.styleFloat = 'left';
				body.dom.appendChild( subRenderer.domElement );
				Ext.get(subRenderer.domElement).setVisibilityMode(Ext.dom.Element.OFFSETS);
				if(!Ext.getCmp('options-guide').checked) Ext.get(subRenderer.domElement).setVisible(false);

				Ext.get(subRenderer.domElement).on({
					click: function(e, t, eOpts){
						e.stopEvent();

						var elem = Ext.get(t);
						var domXY = elem.getXY();
						var domSize = elem.getSize();
						var clickXY = e.getXY();
						var mouseXY = new THREE.Vector2(clickXY[0]-domXY[0],clickXY[1]-domXY[1]);


						mouseXY.x = domSize.width/2-mouseXY.x;
						mouseXY.y = domSize.height/2-mouseXY.y;


						m_ag_orthoYRange = 1800;
						mouseXY.x *= (m_ag_orthoYRange / domSize.height);
						mouseXY.y *= (m_ag_orthoYRange / domSize.height);

						m_ag_targetPos.copy(m_ag_initTargetPos);
						moveTarget(mouseXY.x,mouseXY.y);

						camera.position.copy(m_ag_cameraPos);
						camera.up.copy(m_ag_upVec);
						target.copy(m_ag_targetPos);

						updateCameraHash();

					},
					mousewheel: function(e, t, eOpts){
						e.stopEvent();
//							console.log("mousewheel!!:["+e.getWheelDeltas().y+"]");
//							console.log(e);
//							return true;

						var elem = Ext.get(t);
						var domXY = elem.getXY();
						var domSize = elem.getSize();
						var clickXY = e.getXY();
						var mouseXY = new THREE.Vector2(clickXY[0]-domXY[0],clickXY[1]-domXY[1]);

						mouseXY.x = domSize.width/2-mouseXY.x;
						mouseXY.y = domSize.height/2-mouseXY.y;

						m_ag_orthoYRange = 1800;
						mouseXY.x *= (m_ag_orthoYRange / domSize.height);
						mouseXY.y *= (m_ag_orthoYRange / domSize.height);

						m_ag_targetPos.copy(m_ag_initTargetPos);
						moveTarget(mouseXY.x,mouseXY.y);

						zoom += e.getWheelDeltas().y>0 ? 0.2 : -0.2;
						if(zoom>19.8) zoom = 19.8;
						if(zoom<0)   zoom = 0;
						chengeZoom();

//							mouseXY.multiplyScalar(-1);
//							moveTarget(mouseXY.x,mouseXY.y);

						camera.position.copy(m_ag_cameraPos);
						camera.up.copy(m_ag_upVec);
						target.copy(m_ag_targetPos);

						updateCameraHash();

					}
				});

				var paths = ['static/obj/body.obj'];
				if(paths.length>0){
					if(subRenderer) subRenderer.loadObj(paths);
					if(testRenderer) testRenderer.loadObj(paths);
				}


/**/
//					testRenderer = new AgTestRenderer();
//					testRenderer.domElement.style.position = 'absolute';
//					testRenderer.domElement.style.bottom = '0px';
//					testRenderer.domElement.style.left = '0px';
//					testRenderer.domElement.style.zIndex = 100;
//					body.dom.appendChild( testRenderer.domElement );
/**/

				$('<div id="legend-draw-area" style="position:relative;z-index:100;background:transparent;color:black;margin-top:4px;margin-left:4px;visibility:hidden;"></div>').appendTo($(body.dom));
				$('<div id="pin-draw-area" style="position:relative;z-index:100;background:transparent;color:black;margin-top:4px;margin-left:4px;visibility:hidden;"></div>').appendTo($(body.dom));

				$('<div style="clear:left;">').appendTo($(body.dom));

//					init(body.dom);
//					$('<canvas id="canvas2D" width='+body.getWidth()+' height='+body.getHeight()+'>')
//					.appendTo($(body.dom))
//					.css({
//						position : 'absolute',
//						left     : '0px',
//						top      : '0px',
//						zIndex   : 99
//					});

//					self.loadBp3dParts.hideLoadingTask.delay(5000);//わざと遅めに設定



//					animate();
//					render();
			},
			render : function(viewport){
//					console.log('viewport.render');
			},
			resize : function(viewport,adjWidth,adjHeight,rawWidth,rawHeight){
//					console.log('viewport.resize');
			}
		}
	});
}

var agMainRenderer;
Ext.onReady(function() {
	agMainRenderer = new AgMainRenderer();
});

//未完成
function Drop(event) {
	if(event && event.preventDefault) event.preventDefault();
//	return false;

//	console.log("Drop()");
	if(event && event.dataTransfer){
		if(event.dataTransfer.files.length>0){
			for(var i=0;i<event.dataTransfer.files.length;i++){
				var reader = new FileReader();
				reader._file = event.dataTransfer.files[i];
//				console.log(reader._file);

				reader.onload = function(e) {
//					console.log(e.target.result);
//					console.log(e.target._file);

					var objLoader = new THREE.OBJLoader();
					var object = objLoader.parse(e.target.result);
					var mesh = object.children.shift();
//					console.log(mesh);
					if(Ext.isEmpty(mesh) || mesh.geometry.vertices.length==0){
						alert('Parse Error!!['+e.target._file.name+']');
						return;
					}

					var path = e.target._file.name;

					var extension_parts_store = Ext.data.StoreManager.lookup('extensionPartsStore');
					extension_parts_store.suspendEvents(false);

					var isAdd = false;
					var record = extension_parts_store.findRecord('path',path,0,false,true,true);
					if(!record){
						record = Ext.create(extension_parts_store.model.modelName,{});
						isAdd = true;
					}


					var modifiedFieldNames = [];
					record.beginEdit();
					if(record.get('selected') != true){
						record.set('selected',true);
						modifiedFieldNames.push('selected');
					}
					if(record.get('art_name') != path){
						record.set('art_name',path);
						modifiedFieldNames.push('art_name');
					}
					if(record.get('art_path') != path){
						record.set('art_path',path);
						modifiedFieldNames.push('art_path');
					}
//					if(!Ext.isEmpty(obj.PartMTime) && record.get('modified') != obj.PartMTime){
//						record.set('modified',obj.PartMTime);
//						modifiedFieldNames.push('modified');
//					}

					if(record.get('art_data_size') != e.target._file.size){
						record.set('art_data_size',e.target._file.size);
						modifiedFieldNames.push('art_data_size');
					}
					if(record.get('art_timestamp') != e.target._file.lastModifiedDate){
						record.set('art_timestamp',e.target._file.lastModifiedDate);
						modifiedFieldNames.push('art_timestamp');
					}

					mesh.geometry.computeBoundingBox();
					var bb = mesh.geometry.boundingBox;

					if(record.get('art_xmin') != bb.min.x){
						record.set('art_xmin',bb.min.x);
						modifiedFieldNames.push('art_xmin');
					}
					if(record.get('art_ymin') != bb.min.y){
						record.set('art_ymin',bb.min.y);
						modifiedFieldNames.push('art_ymin');
					}
					if(record.get('art_zmin') != bb.min.z){
						record.set('art_zmin',bb.min.z);
						modifiedFieldNames.push('art_zmin');
					}

					if(record.get('art_xmax') != bb.max.x){
						record.set('art_xmax',bb.max.x);
						modifiedFieldNames.push('art_xmax');
					}
					if(record.get('art_ymax') != bb.max.y){
						record.set('art_ymax',bb.max.y);
						modifiedFieldNames.push('art_ymax');
					}
					if(record.get('art_zmax') != bb.max.z){
						record.set('art_zmax',bb.max.z);
						modifiedFieldNames.push('art_zmax');
					}

					var center = new THREE.Vector3();
					center.addVectors( bb.max, bb.min );
					center.multiplyScalar( 0.5 );
					if(record.get('art_xcenter') != center.x){
						record.set('art_xcenter',center.x);
						modifiedFieldNames.push('art_xcenter');
					}
					if(record.get('art_ycenter') != center.y){
						record.set('art_ycenter',center.y);
						modifiedFieldNames.push('art_ycenter');
					}
					if(record.get('art_zcenter') != center.z){
						record.set('art_zcenter',center.z);
						modifiedFieldNames.push('art_zcenter');
					}

					var group = 'DropObject';
					var grouppath = '__'+group;
					if(record.get('group') != group){
						record.set('group',group);
						modifiedFieldNames.push('group');
					}
					if(record.get('grouppath') != grouppath){
						record.set('grouppath',grouppath);
						modifiedFieldNames.push('grouppath');
					}

					if(record.get('dropobject') != true){
						record.set('dropobject',true);
						modifiedFieldNames.push('dropobject');
					}

					if(modifiedFieldNames.length>0){
						record.commit(false);
						record.endEdit(false,modifiedFieldNames);
					}else{
						record.cancelEdit();
					}
					if(isAdd){
						extension_parts_store.add(record);
						Ext.defer(function(){ $(window).trigger('dropObject',[record]); },250);
					}

					extension_parts_store.resumeEvents();

					var path2 = agMainRenderer.getRecordPath(record);
					agMainRenderer.setMesh(path2,mesh);
					agMainRenderer.loadBp3dParts.setMeshProp(mesh,record);

					agMainRenderer.loadBp3dParts.addMesh(mesh);
					agMainRenderer.loadBp3dParts.unmask();
					agMainRenderer.loadBp3dParts.exec();


				};
				reader.readAsText(event.dataTransfer.files[i]);
			}
		}else if(event.dataTransfer.items.length>0){
			var text = "";
			for(var i=0;i<event.dataTransfer.items.length;i++){
				text += event.dataTransfer.getData(event.dataTransfer.items[i].type);
			}
//			console.log(text.length);
		}
	}
	if(event && event.preventDefault) event.preventDefault();
	return false;
}

function cancel(event) {
	if(event && event.preventDefault) event.preventDefault();
	return false;
}

