window.requestAnimationFrame = window.requestAnimationFrame ||
  window.webkitRequestAnimationFrame ||
  window.mozRequestAnimationFrame ||
  window.msRequestAnimationFrame;
window.cancelAnimationFrame = window.cancelAnimationFrame ||
  window.mozCancelAnimationFrame ||
  window.webkitCancelAnimationFrame ||
  window.msCancelAnimationFrame;

Ext.define('Ag.MainRenderer', {
	mixins: {
		observable: 'Ext.util.Observable'
	},
	constructor: function (config) {
		var self = this;


		self.__config = config || {};
		self.__config.height = self.__config.height || 96;
		self.__config.rate   = self.__config.rate   || 2;
		self.__config.width  = self.__config.width  || self.__config.height/self.__config.rate;

		self.__config.minZoom = self.__config.minZoom || 1;
		self.__config.maxZoom = self.__config.maxZoom || 44;
//		console.log(self.__config);

		self.__config.usePan = Ext.isEmpty(self.__config.usePan) ? true : (Ext.isBoolean(self.__config.usePan) ? self.__config.usePan : (self.__config.usePan ? true : false));

		self.__config.usePromise = Ext.isEmpty(self.__config.usePromise) ? true : (Ext.isBoolean(self.__config.usePromise) ? self.__config.usePromise : (self.__config.usePromise ? true : false));

		self.__config.backgroundColor = self.__config.backgroundColor || '#FFFFFF';

		self.mixins.observable.constructor.call(self, self.__config);
		self.addEvents(
			'load',
			'pick',
			'rotate',
			'zoom'
		);

		self.__cameraPersNear = 0.1;
		self.__cameraPersFar = 10000;

	//	var rate = 3/2;
		var rate = self.__config.rate;

		self.__SCREEN_HEIGHT = self.__config.height;
		self.__SCREEN_WIDTH  = self.__config.width;
	//	self.__SCREEN_HEIGHT = 60;
		self.__aspectRatio = self.__SCREEN_WIDTH / self.__SCREEN_HEIGHT;

		self.__BORDER_WIDTH = 0;
		self.$_domElement = $('<div>').css({
			width: self.__SCREEN_WIDTH,
			height: self.__SCREEN_HEIGHT,
			backgroundColor: '#f0f0f0',
			border: self.__BORDER_WIDTH+'px solid #b5b8c8',
			textAlign: 'center',
//			position: 'relative',
			position: 'absolute',
		});
		self.__domElement = self.$_domElement.get(0);


		self.__SCREEN_HEIGHT -= (self.__BORDER_WIDTH*2);
		self.__SCREEN_WIDTH  -= (self.__BORDER_WIDTH*2);

	//	self._loadObjParams = [];

		var mousewheelevent = 'onwheel' in document ? 'wheel' : 'onmousewheel' in document ? 'mousewheel' : 'DOMMouseScroll';
		var d3_document = document;
		var d3_behavior_zoomDelta;
		var d3_behavior_zoomWheel = "onwheel" in d3_document ? (d3_behavior_zoomDelta = function() {
			return -d3.event.deltaY * (d3.event.deltaMode ? 120 : 1);
		}, "wheel") : "onmousewheel" in d3_document ? (d3_behavior_zoomDelta = function() {
			return d3.event.wheelDelta;
		}, "mousewheel") : (d3_behavior_zoomDelta = function() {
			return -d3.event.detail;
		}, "MozMousePixelScroll");


		self.__target = new THREE.Vector3(0,0,0);

		self.__MAX_HEIGHT = 1800;
	//	self.__MAX_HEIGHT = 900;
		self.__camFactor = 2;
//		self.__camera = new THREE.OrthographicCamera((self.__MAX_HEIGHT / rate)/-2, (self.__MAX_HEIGHT / rate)/2, self.__MAX_HEIGHT/2, self.__MAX_HEIGHT/-2, 0.1, 10000 );
//		self.__camera = new THREE.OrthographicCamera(self.__MAX_HEIGHT / 2 * -1, self.__MAX_HEIGHT / 2, self.__MAX_HEIGHT / 2, self.__MAX_HEIGHT / 2 * -1, 0, self.__MAX_HEIGHT );
//		self.__camera = new THREE.OrthographicCamera(0, self.__MAX_HEIGHT, 0, self.__MAX_HEIGHT * -1, 0, self.__MAX_HEIGHT);

		self.__camera = new THREE.OrthographicCamera(0, self.__MAX_HEIGHT, 0, self.__MAX_HEIGHT * -1, 0.0001, self.__MAX_HEIGHT * 2);
//		self.__camera = new THREE.CombinedCamera(self.__MAX_HEIGHT, self.__MAX_HEIGHT, 45, 0.0001, self.__MAX_HEIGHT * 2,0.0001, self.__MAX_HEIGHT * 2);
//		self.__camera.toOrthographic();

		self.__camera.position.set(0,-self.__MAX_HEIGHT,0);
//		self.__camera.position.set(0,-900,0);
//		self.__camera.position.set(0,0,0);


	//	self.__camera.rotation.order = 'XZY';
	//	self.__camera.rotation.y = - Math.PI / 4;
	//	self.__camera.rotation.x = Math.atan( - 1 / Math.sqrt( 2 ) );


		self.__camera.up.set(0,0,1);
		self.__camera.lookAt( self.__target );


//		self.__grid = new THREE.GridHelper( self.__MAX_HEIGHT, 10, 0x0000ff, 0x808080 );
//		if(self.__grid.visible) self.__grid.visible = false;
//		if(self.__grid && self.__grid.visible) self.__grid.position.copy(self.__camera.position);

//		self.__grid.position.y = - 150;
//		self.__grid.position.x = - 150;
//		self.__camera.add( self.__grid );




		self.__scene = new THREE.Scene();

//		self.__scene.add( self.__grid );
//		self.setGrid({visible:false});

//		console.log(self.__scene);
//		console.log(self.__grid);


//		self.__scene.add( self.__camera );

		// LIGHTS
		self.__ambientLight = new THREE.AmbientLight( 0x221d16 );
		self.__scene.add( self.__ambientLight );

/**/
//		self.__directionalLight = new THREE.DirectionalLight( 0xffffff );
		self.__directionalLight = new THREE.DirectionalLight( 0xffffff, 1 );
		self.__directionalLight.position.copy(self.__camera.position);
		self.__directionalLight.target.position.copy(self.__target);
		self.__scene.add( self.__directionalLight );
		self.__scene.add( self.__directionalLight.target );


/**/
		self.__group = new THREE.Group();
		self.__rotateGroup = new THREE.Group();
		self.__rotateGroup.add(self.__group);

	//	self.__group = new THREE.Camera();
	//	self.__group.lookAt( self.__target );

	//	self.__scene.add(self.__group);
		self.__scene.add(self.__rotateGroup);
//		console.log(self.__rotateGroup);

//OBJを動かす場合（cameraを動かす場合は、コメントにする）
//		self._offset = new THREE.Vector3();


		self.__pinGroup = new THREE.Group();
//		self._rotatePinGroup = new THREE.Group();
//		self._rotatePinGroup.add(self.__pinGroup);
		self.__scene.add(self.__pinGroup);
/*
		self.on('zoom', function(s,zoom){
			var zoomScale = self.getZoomScale();
			var yrange = self.getZoomYRange(zoomScale);
			var yrate = yrange / self.__MAX_HEIGHT;
			for(var i=0;i<self.__pinGroup.children.length;i++){
				var voxel = self.__pinGroup.children[i];
				voxel.setScale(yrate);
			}
		});
*/

		self.__pinDescriptionLineGroup = new THREE.Group();
		self.__scene.add(self.__pinDescriptionLineGroup);

//		var gridHelper = new THREE.GridHelper( 400, 40, 0x0000ff, 0x808080 );
//		self.__scene.add( gridHelper );

//		var polarGridHelper = new THREE.PolarGridHelper( 200, 16, 8, 64, 0x0000ff, 0x808080 );
//		self.__scene.add( polarGridHelper );



		if(!Detector.webgl) Detector.addGetWebGLMessage();

		if(Detector.webgl){
			self.__renderer = new THREE.WebGLRenderer({alpha: true,antialias:true,maxLights:6,preserveDrawingBuffer:true});
		}else{
			self.__renderer = new THREE.CanvasRenderer({antialias:true,maxLights:6,preserveDrawingBuffer:true});
		}
		self.__renderer.setSize( self.__SCREEN_WIDTH, self.__SCREEN_HEIGHT );
//		self.__renderer.setClearColor(Number('0xffffff'));
//		self.__renderer.setClearColor(Number('0xf0f0f0'));
//		self.__renderer.setClearColor(Number('0x999999'));
		self.__renderer.setClearColor(self.__config.backgroundColor);


		//空間のクリッピング
//		var plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), -900);
//		self.__renderer.clippingPlanes.push(plane);


	//	self.__renderer.domElement.style.position = "relative";
		$(self.__renderer.domElement).css({
			position: 'absolute',
			left: 0,
			top: 0,
		});
		self.__domElement.appendChild( self.__renderer.domElement );

		$('<div>').addClass('legend-text-label').appendTo($(self.__domElement));

//////////////////////////
// Rotate (START)
//////////////////////////
		self.__longitude = -90;
		self.__latitude = 0;
		var m_ag_distance = self.__MAX_HEIGHT;
		var m_ag_cameraPos = new THREE.Vector3();
		var m_ag_upVec = new THREE.Vector3();
		var m_ag_targetPos = new THREE.Vector3();
		var m_ag_posDif = m_ag_distance;
		var m_ag_epsilon = 0.0000001;

		var getCameraAxis = function(){
			return {
//				H : Math.round(self.__longitude/5)*5 + 90,
//				V : Math.round(self.__latitude/5)*5
				H : Math.round(self.__longitude) + 90,
				V : Math.round(self.__latitude)
			};
		};

		self._calcRotateDeg = function(){
			var HV = getCameraAxis();
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
			return HV;
		}

		self._calcCameraPos = function(){

//			console.log('self._calcCameraPos');

			var eyeLongitudeRadian = self.agDeg2Rad(self.__longitude);
			var eyeLatitudeRadian = self.agDeg2Rad(self.__latitude);
			var eyeTargetDistance = m_ag_distance;

			var target = m_ag_targetPos.copy(self.__target);
			var eye = m_ag_cameraPos.copy(self.__camera.position);
			var yAxis = m_ag_upVec.copy(self.__camera.up);

			var zAxis = new THREE.Vector3();
			var xAxis = new THREE.Vector3();
			var tmp0 = new THREE.Vector3();

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
				var remind = Math.abs(Math.round(self.__latitude) % 360);
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

			var posDif = m_ag_posDif;
			var tmpDeg = self._calcRotateDeg();

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

			self.__camera.position.copy(m_ag_cameraPos);
			self.__camera.up.copy(m_ag_upVec);
			self.__target.copy(m_ag_targetPos);

		};

		var mouseDownVec2 = null;
		var mouseMoveVec2 = null;
		var mouseDownDeg = null;
		var mouseDownTranslate = null;
		var documentMouseMove = function(e){
//			console.log('documentMouseMove');
			if(Ext.isEmpty(mouseDownVec2) || (self.__config.usePan && !e.shiftKey)) return;
			mouseMoveVec2 = new THREE.Vector2(e.offsetX, e.offsetY);
			if(mouseMoveVec2.equals(mouseDownVec2)){
//				console.log('equals mouseDownVec2 mouseMoveVec2');
				mouseMoveVec2 = null;
				return;
			}
//			mouseMoveVec2.sub(mouseDownVec2);

			var mouseSubVec2 = new THREE.Vector2();
			mouseSubVec2.subVectors(mouseMoveVec2, mouseDownVec2);
//				console.log(mouseSubVec2);
//				if(Math.abs(mouseSubVec2.x) < 5 && Math.abs(mouseSubVec2.y) < 5) return;

//			console.log(mouseSubVec2);
//			var multiplyValue = 0.05;
//			mouseSubVec2.multiplyScalar(multiplyValue);
//			console.log(mouseSubVec2);
//			if(Math.abs(mouseSubVec2.x) < multiplyValue && Math.abs(mouseSubVec2.y) < multiplyValue) return;


//			var moveRate = 1;
			var moveRate = 100;
			var rotateAngle = 1;

//			var degH = Math.round(mouseDownDeg.H/rotateAngle)*rotateAngle;
			var degH = mouseDownDeg.H;
			if(mouseSubVec2.x>0){
				degH += -rotateAngle * Math.ceil(mouseSubVec2.x / moveRate);
			}else{
				degH += -rotateAngle * Math.floor(mouseSubVec2.x / moveRate);
			}
			while (degH >= 360) {
				degH = degH - 360;
			}
			while (degH < 0) {
				degH = degH + 360;
			}
			// rotateV
//			var degV = Math.round(mouseDownDeg.V/rotateAngle)*rotateAngle;
			var degV = mouseDownDeg.V;
			if(mouseSubVec2.y>0){
				degV +=  rotateAngle * Math.ceil(mouseSubVec2.y / moveRate);
			}else{
				degV +=  rotateAngle * Math.floor(mouseSubVec2.y / moveRate);
			}
			while (degV >= 360) {
				degV = degV - 360;
			}
			while (degV < 0) {
				degV = degV + 360;
			}

			if(mouseDownDeg.H != degH || mouseDownDeg.V != degV){
				if(mouseDownDeg.H != degH){
					if(mouseSubVec2.x>0){
						self.__longitude += (-rotateAngle * Math.ceil(mouseSubVec2.x / moveRate));
					}else{
						self.__longitude += (-rotateAngle * Math.floor(mouseSubVec2.x / moveRate));
					}
					mouseDownVec2.x = mouseMoveVec2.x;
				}
				if(mouseDownDeg.V != degV){
					if(mouseSubVec2.y>0){
						self.__latitude  += (rotateAngle * Math.ceil(mouseSubVec2.y / moveRate));
					}else{
						self.__latitude  += (rotateAngle * Math.floor(mouseSubVec2.y / moveRate));
					}
					mouseDownVec2.y = mouseMoveVec2.y;
				}
				self.__longitude = Math.round(self.__longitude/rotateAngle)*rotateAngle;
				self.__latitude = Math.round(self.__latitude/rotateAngle)*rotateAngle;

				self._calcCameraPos();

//				self.__camera.position.copy(m_ag_cameraPos);
//				self.__camera.up.copy(m_ag_upVec);
//				self.__target.copy(m_ag_targetPos);

				mouseDownDeg.H = degH;
				mouseDownDeg.V = degV;

//					console.log(mouseSubVec2,self.__longitude,self.__latitude);
//					console.log(self._calcRotateDeg());
				self.fireEvent('rotate', self, self._calcRotateDeg());

//				self.zoomCB();
				self.render();

			}
			else{
//				console.log(mouseDownDeg.H,degH,mouseDownDeg.V,degV);
			}
//			console.log('not equals mouseDownVec2 mouseMoveVec2');
//			mouseMoveVec2 = null;
		};
		var documentMouseUp = function(e){
//			console.log('documentMouseUp');

			if(Ext.isArray(mouseDownTranslate)) self.__zoom.translate(mouseDownTranslate);

			mouseDownVec2 = null;
			mouseMoveVec2 = null;
			mouseDownDeg = null;
			mouseDownTranslate = null;
			$(document).unbind('mousemove',documentMouseMove);
			$(document).unbind('mouseup',documentMouseUp);
		};
//////////////////////////
// Rotate (END)
//////////////////////////

		$(self.__renderer.domElement).click(function(e){
//			return false;
		}).mousedown(function(e){
//			console.log('mousedown');
			mouseDownVec2 = new THREE.Vector2(e.offsetX, e.offsetY);
			if(e.shiftKey || !self.__config.usePan){
				mouseDownDeg = self._calcRotateDeg();
				mouseDownTranslate = self.__zoom.translate();
//				console.log(mouseDownDeg);
				$(document).bind('mousemove',documentMouseMove);
				$(document).bind('mouseup',documentMouseUp);
			}
		}).mousemove(function(e){
//			return false;
		}).mouseup(function(e){
//			console.log('mouseup');
			var mouseUpVec2 = null;
			if(!self.__config.usePan && mouseDownVec2 && !mouseMoveVec2){
				mouseUpVec2 = new THREE.Vector2(e.offsetX, e.offsetY);
			}


			if((self.__config.usePan && mouseDownVec2 && !mouseDownDeg) || (!self.__config.usePan && mouseDownVec2 && mouseUpVec2 && mouseUpVec2.equals(mouseDownVec2)) ){
//				var mouseUpVec2 = new THREE.Vector2(e.offsetX, e.offsetY);
				mouseUpVec2 = mouseUpVec2 || new THREE.Vector2(e.offsetX, e.offsetY);
				if(mouseUpVec2.equals(mouseDownVec2)){
					var intersects = self.getIntersectObjects(mouseDownVec2);
					self.fireEvent('pick', self, intersects, e);
/*
					var intersect = intersects[0];
					var zoomScale = self.getZoomScale();
					var yrange = self.getZoomYRange(zoomScale);
					var yrate = yrange / self.__MAX_HEIGHT;
					var voxel = new THREE.ConeHelper( intersect.face.normal, intersect.point, 0x0000ff );
					voxel.setScale(yrate);
					self.__pinGroup.add( voxel );
					console.log( intersect.point, intersect.face.normal, intersect.object.up );
*/
				}
				else{
//					console.log(mouseDownVec2.distanceTo(mouseUpVec2));
				}
				mouseDownVec2 = null;
			}

//			return false;
		}).bind(mousewheelevent,function(e){
//			return false;
		});


		var state = {
			x: 0,
			y: 0,
			scale: self.__MAX_HEIGHT / 2
		};

//D3.jsを使用して、zoomとpanを制御
		self._view = d3.select(self.__renderer.domElement);
		self.__zoom = d3.behavior.zoom().scaleExtent([self.__config.minZoom, self.__config.maxZoom])
		self.__zoom.on('zoom', function(e){
			if(d3.event.sourceEvent.shiftKey || !self.__config.usePan){
				return false;
			}else{
				self.zoomCB();
			}
		});
		self._view.call(self.__zoom).on('dblclick.zoom', null);

		self.zoomCB = function() {
			var self = this;
//			if(mouseDownVec2 && mouseDownDeg) return;
//			console.log('zoomCB()');//

			var DZOOM = self.__MAX_HEIGHT / 2;
			var aspect = self.__aspectRatio;
			var x, y, z, _ref;
			z = self.__zoom.scale();
			_ref = self.__zoom.translate(), x = _ref[0], y = _ref[1];
			self.fireEvent('zoom',self, self.getDispZoom());
			return window.requestAnimationFrame(function() {
				var width = self.__SCREEN_WIDTH;
				var height = self.__SCREEN_HEIGHT;
				x = x - width / 2;
				y = y - height / 2;

				self.__camera.left = -DZOOM / z * aspect - x / width * DZOOM / z * 2 * aspect;
				self.__camera.right = DZOOM / z * aspect - x / width * DZOOM / z * 2 * aspect;
				self.__camera.top = DZOOM / z + y / height * DZOOM / z * 2;
				self.__camera.bottom = -DZOOM / z + y / height * DZOOM / z * 2;
				self.__camera.updateProjectionMatrix();

//				self._calcCameraPos();
				self.render();
			});
		};



		self._loadingManager = {};
		if(THREE.LoadingManager) self._loadingManager = new THREE.LoadingManager();
		self._loadingManager.onLoad = function(event, param){
			try{
				var group = (event.content ? event.content : event);
				if(group instanceof THREE.Group){
					var children = group.children;
					var mesh;
					var i
					for(i=0;i<children.length;i++){
						mesh = children[i];
						mesh[Ag.Def.OBJ_URL_DATA_FIELD_ID] = param[Ag.Def.OBJ_URL_DATA_FIELD_ID];
						mesh[Ag.Def.OBJ_ID_DATA_FIELD_ID] = param[Ag.Def.OBJ_ID_DATA_FIELD_ID];
						self.setMeshProperties(mesh,param);
						mesh.geometry.computeBoundingBox();
					}
					group[Ag.Def.OBJ_URL_DATA_FIELD_ID] = param[Ag.Def.OBJ_URL_DATA_FIELD_ID];
					group.name = group[Ag.Def.OBJ_ID_DATA_FIELD_ID] = param[Ag.Def.OBJ_ID_DATA_FIELD_ID];
					self.__group.add( group );
				}
				else if(group instanceof THREE.Mesh){
					group[Ag.Def.OBJ_URL_DATA_FIELD_ID] = param[Ag.Def.OBJ_URL_DATA_FIELD_ID];
					group[Ag.Def.OBJ_ID_DATA_FIELD_ID] = param[Ag.Def.OBJ_ID_DATA_FIELD_ID];
					self.setMeshProperties(group,param);
					group.geometry.computeBoundingBox();
					group.name = group[Ag.Def.OBJ_ID_DATA_FIELD_ID] = param[Ag.Def.OBJ_ID_DATA_FIELD_ID];
					self.__group.add( group );
				}else{
					console.error('Unknown data type!!');
					console.error(event);
				}
			}catch(e){
				console.error(e);
			}
		};

		self._objLoader = new THREE.OBJLoader();

//		if(self._objLoader.addEventListener) self._objLoader.addEventListener('load',self._loadingManager.onLoad);

	//	self.startAnimate();
		self._calcCameraPos();
		self.render();
	},

	domElement : function(mesh,param) {
		var self = this;
		return self.__domElement;
	},

	_setMeshProperties : function(mesh,param) {
		var self = this;
		var color = param[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] || '#F0D2A0';
		if(color.substr(0,1) == '#') color = color.substr(1);
		color = Number('0x'+color);
		mesh.material.color.setHex( color );
		mesh.material.opacity = param[Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID];
		mesh.material.wireframe = false;
//		mesh.material.wireframe = param[Ag.Def.PART_REPRESENTATION]==='wireframe' ;//false;
		mesh.visible = param[Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID] && mesh.material.opacity>0 ? true : false;

//		if(mesh.visible && Ext.isBoolean(param[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID])){
		if(mesh.visible || Ext.isBoolean(param[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID])){
			mesh[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID] = param[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID];
		}else{
			delete mesh[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID];
		}

		mesh[Ag.Def.USE_FOR_BOUNDING_BOX_FIELD_ID] = param[Ag.Def.USE_FOR_BOUNDING_BOX_FIELD_ID];

		mesh.material.blending = THREE.NormalBlending;
		if(mesh.material.opacity>=1){
			mesh.material.transparent = false;
		}
		else{
			mesh.material.transparent = true;
		}
		mesh.material.depthWrite = true;
		mesh.doubleSided = true;
		mesh.material.side = THREE.DoubleSide;

		//選択状態をwireframeで表現する
		while(mesh.children.length){
			mesh.remove(mesh.children[0]);
		}
		if(param[Ag.Def.PART_REPRESENTATION]==='wireframe'){
			var geo = new THREE.EdgesGeometry( mesh.geometry ); // or WireframeGeometry
			var mat = new THREE.LineBasicMaterial( { color: param[Ag.Def.PART_WIREFRAME_COLOR], linewidth: 2 } );
			var wireframe = new THREE.LineSegments( geo, mat );
			mesh.add( wireframe );
		}

	},

	setMeshProperties : function(mesh,param) {
		var self = this;
		if(mesh instanceof THREE.Mesh){
			self._setMeshProperties(mesh,param);
		}
		else if(mesh instanceof THREE.Group){
			for(var i=0;i<mesh.children.length;i++){
				self._setMeshProperties(mesh.children[i],param);
			}
		}
	},

	setSize : function(width,height){
		var self = this;
		self.stopAnimate();
		self._setSize(width,height);
		self.autoFocus();
	},

	_setSize : function(width,height){
		var self = this;

		self.__SCREEN_WIDTH = width;
		self.__SCREEN_HEIGHT = height;
		self.__aspectRatio = self.__SCREEN_WIDTH / self.__SCREEN_HEIGHT;
//		console.log('self.__aspectRatio',self.__aspectRatio);

		self.$_domElement.width(self.__SCREEN_WIDTH).height(self.__SCREEN_HEIGHT);
		self.__SCREEN_HEIGHT -= (self.__BORDER_WIDTH*2);
		self.__SCREEN_WIDTH  -= (self.__BORDER_WIDTH*2);

		if(Ext.isFunction(self.__camera.setZoom)){
			if(self.__SCREEN_WIDTH < self.__SCREEN_HEIGHT){
				self.__renderer.setSize( self.__SCREEN_WIDTH, self.__SCREEN_WIDTH );
			}else{
				self.__renderer.setSize( self.__SCREEN_HEIGHT, self.__SCREEN_HEIGHT );
			}
		}else{
			self.__renderer.setSize( self.__SCREEN_WIDTH, self.__SCREEN_HEIGHT );
		}
	},

	stopAnimate : function(){
		var self = this;
		if(Ext.isEmpty(self.__animate)) return false;
		cancelAnimationFrame( self.__animate );
		delete self.__animate;
		return true;
	},

	startAnimate : function(){
		var self = this;
		self.stopAnimate();
		self.__animate = requestAnimationFrame( Ext.bind(self.startAnimate,self) );
//		self.addLongitude(0.5);
////		self.addLatitude(0.5);


//		var timer = new Date().getTime() * 0.0005;
//		self.__camera.position.y = Math.floor(Math.cos( timer ) * 200);
//		self.__camera.position.z = Math.floor(Math.sin( timer ) * 200);
//		console.log(self.__camera.position);

		self._render();
	},

	render : function(){
		var self = this;
		if(self.getAutoRender()){
//			console.log( self.__target.clone(), self.__camera.position.clone(), self.__camera.up.clone() );
//			console.trace();
			window.requestAnimationFrame(function() {
				return self._render();
			});
		}
	},

	_render : function(){
		var self = this;
		self.__camera.lookAt( self.__target );
		if(self.__directionalLight){
			self.__directionalLight.position.copy( self.__camera.position );
			self.__directionalLight.target.position.copy( self.__target );
		}
		if(self.__grid && self.__grid.visible) self.__grid.position.copy( self.__camera.position );

		if(
			self.__pinGroup.children.length ||
			($.isArray(self.__pintextlabels) && self.__pintextlabels.length) ||
			($.isArray(self.__pindescriptionlabels) && self.__pindescriptionlabels.length)
		){
			self.__scene.updateMatrixWorld();
			self.__camera.updateMatrixWorld();

			var zoomScale = self.getZoomScale();
			var yrange = self.getZoomYRange(zoomScale);
			var yrate = yrange / self.__MAX_HEIGHT;
			self.__pinGroup.children.forEach(function(child){
				child.setScale(yrate);
			});

			if($.isArray(self.__pintextlabels) && self.__pintextlabels.length){
				self.__pintextlabels.forEach(function(pintextlabel){
					pintextlabel.updatePosition();
				});
			}

			if($.isArray(self.__pindescriptionlabels) && self.__pindescriptionlabels.length){

				var po = $(self.__domElement).offset();
				self.__pindescriptionlabels.forEach(function(description){
					if(description.parent && description.line){
						var voxel = description.parent;
						var dline = description.line;

						var co = description.offset();

			//			var position = description.position();
						var position = {};
						position.top = (co.top-po.top);
						position.left = (co.left-po.left);

						position.top += description.height()/2;
						position.left += description.width();
						var description_vector = self.convertCoordinateScreenTo3D(new THREE.Vector2(position.left,position.top));

	//					voxel.updateMatrixWorld();
	//					var vector = new THREE.Vector3();
	//					vector.setFromMatrixPosition( voxel.line.matrixWorld );
						var i = 0;
						dline.geometry.attributes.position.array[ i++ ] = description_vector.x;
						dline.geometry.attributes.position.array[ i++ ] = description_vector.y;
						dline.geometry.attributes.position.array[ i++ ] = description_vector.z;
						dline.geometry.attributes.position.needsUpdate = true;

	//					dline.geometry.vertices[ 0 ].x = description_vector.x;
	//					dline.geometry.vertices[ 0 ].z = description_vector.z;
	//					dline.geometry.verticesNeedUpdate = true;

					}
				});
			}
		}

		self.__renderer.render( self.__scene, self.__camera );
	},

	getZoomYRange : function(zoomScale){
		var self = this;
		var height = self.__MAX_HEIGHT;
//		var height = self.__MAX_HEIGHT * (self.__aspectRatio<1 ?  self.__aspectRatio : 1);
		return Math.max(1,Math.round(Math.pow(Math.E,(Math.log(height)/Math.log(2)-zoomScale) * Math.log(2))));
	},

	getYRangeZoom : function(yrange){
		var self = this;
		var height = self.__MAX_HEIGHT;
//		var height = self.__MAX_HEIGHT * (self.__aspectRatio<1 ?  self.__aspectRatio : 1);
		return Math.round((Math.log(height)/Math.log(2) - Math.log(yrange)/Math.log(2)) * 10) / 10;
	},

	getZoomScale : function(){
		var self = this;
		return Math.round(Math.log(self.__zoom.scale()) / Math.log(2) * 10) / 10;
	},

	getDispZoom : function(){
		var self = this;
//		console.log( self.getZoomYRange( Math.log(self.__zoom.scale() || 1) / Math.log(2) ));
		var scale = self.getZoomScale();
//		var yrange = self.getZoomYRange(scale);
//		console.log( scale, yrange, self.__MAX_HEIGHT / yrange, yrange / self.__MAX_HEIGHT );
		var zoom = Math.round( scale * 5 - 0.5 ) + 1;
		return zoom;
	},

	setDispZoom : function(zoom,render){
		var self = this;
		if(zoom<1) zoom = 1;

//		console.log(self.__zoom.translate());
		self.__zoom.scale(Math.pow(2, Math.round(((zoom-1)/5) * 10)/10));
//		console.log(self.__zoom.translate());

		var width = self.__SCREEN_WIDTH;
		var height = self.__SCREEN_HEIGHT;
//		self.__zoom.translate([width/2, height/2]);

//		console.log('setDispZoom',zoom);

//		var yRange = self.getZoomYRange((zoom-1)/5);
//		self.setYRange(yRange, render);

//		self.DISP_ZOOM = Math.round(zoom);
//		self.__zoom.scale(Math.round(zoom));
		self.zoomCB();
	},

	setYRange : function(yRange,render){
		var self = this;
/*
		self.__camera.left   = yRange/-2;
		self.__camera.right  = yRange/2;
		self.__camera.bottom = yRange/-2;
		self.__camera.top    = yRange/2;
		self.__camera.updateProjectionMatrix();

		if(render) self.render();
*/

		self.YRANGE = yRange;
		self.ZOOM = self.getYRangeZoom(yRange);
//		self.DISP_ZOOM = Math.round(self.ZOOM*5-0.5)+1;

//		self.DISP_ZOOM = self.__MAX_HEIGHT/yRange;
//		self.DISP_ZOOM = Math.round(self.__MAX_HEIGHT/yRange);

//		console.log(self.DISP_ZOOM, self.getYRangeZoom(yRange));
//		self.__zoom.scale(self.DISP_ZOOM);

//		console.log('setYRange',yRange,self.getYRangeZoom(yRange));
		self.__zoom.scale(Math.pow(2, self.getYRangeZoom(yRange)));
//		console.log(self.__zoom.scale());

//		var width = $(self.__renderer.domElement).width();
//		var height = $(self.__renderer.domElement).height();
//		self.__zoom.translate([width/2, height/2]);

		self.zoomCB();

	},

	focus : function(zoom){
		var self = this;
//		if(self.__group.children.length<self._loadObjParams.length) return;

		if(Ext.isEmpty(zoom)) zoom = true;
		if(!Ext.isBoolean(zoom)) zoom = zoom ? true : false;

		var max = new THREE.Vector3();
		var min = new THREE.Vector3();
		max.set(null,null,null);
		min.set(null,null,null);
		var arr = [];

		for(var i=0;i<self.__group.children.length;i++){
			if(self.__group.children[i] instanceof THREE.Mesh){
				var mesh = self.__group.children[i];
	//			if(mesh.visible && mesh.material.opacity>=1){
				if(mesh.visible && mesh[Ag.Def.USE_FOR_BOUNDING_BOX_FIELD_ID]){
					var bb = mesh.geometry.boundingBox;
					if(Ext.isEmpty(min.x) || bb.min.x < min.x) min.x = bb.min.x;
					if(Ext.isEmpty(min.y) || bb.min.y < min.y) min.y = bb.min.y;
					if(Ext.isEmpty(min.z) || bb.min.z < min.z) min.z = bb.min.z;

					if(Ext.isEmpty(max.x) || bb.max.x > max.x) max.x = bb.max.x;
					if(Ext.isEmpty(max.y) || bb.max.y > max.y) max.y = bb.max.y;
					if(Ext.isEmpty(max.z) || bb.max.z > max.z) max.z = bb.max.z;

					Ext.Array.push(arr,Ext.Object.getValues(bb.max));
					Ext.Array.push(arr,Ext.Object.getValues(bb.min));
				}
			}
			else if(self.__group.children[i] instanceof THREE.Group){
				for(var j=0;j<self.__group.children[i].children.length;j++){
					var mesh = self.__group.children[i].children[j];
					if(mesh.visible && mesh[Ag.Def.USE_FOR_BOUNDING_BOX_FIELD_ID]){
						var bb = mesh.geometry.boundingBox;
						if(Ext.isEmpty(min.x) || bb.min.x < min.x) min.x = bb.min.x;
						if(Ext.isEmpty(min.y) || bb.min.y < min.y) min.y = bb.min.y;
						if(Ext.isEmpty(min.z) || bb.min.z < min.z) min.z = bb.min.z;

						if(Ext.isEmpty(max.x) || bb.max.x > max.x) max.x = bb.max.x;
						if(Ext.isEmpty(max.y) || bb.max.y > max.y) max.y = bb.max.y;
						if(Ext.isEmpty(max.z) || bb.max.z > max.z) max.z = bb.max.z;

						Ext.Array.push(arr,Ext.Object.getValues(bb.max));
						Ext.Array.push(arr,Ext.Object.getValues(bb.min));
					}
				}
			}
		}
		if(arr.length==0){
			for(var i=0;i<self.__group.children.length;i++){
				if(self.__group.children[i] instanceof THREE.Mesh){
					var mesh = self.__group.children[i];
					if(mesh.visible){
						var bb = mesh.geometry.boundingBox;
						if(Ext.isEmpty(min.x) || bb.min.x < min.x) min.x = bb.min.x;
						if(Ext.isEmpty(min.y) || bb.min.y < min.y) min.y = bb.min.y;
						if(Ext.isEmpty(min.z) || bb.min.z < min.z) min.z = bb.min.z;

						if(Ext.isEmpty(max.x) || bb.max.x > max.x) max.x = bb.max.x;
						if(Ext.isEmpty(max.y) || bb.max.y > max.y) max.y = bb.max.y;
						if(Ext.isEmpty(max.z) || bb.max.z > max.z) max.z = bb.max.z;

						Ext.Array.push(arr,Ext.Object.getValues(bb.max));
						Ext.Array.push(arr,Ext.Object.getValues(bb.min));
					}
				}
				else if(self.__group.children[i] instanceof THREE.Group){
					for(var j=0;j<self.__group.children[i].children.length;j++){
						var mesh = self.__group.children[i].children[j];
						if(mesh.visible){
							var bb = mesh.geometry.boundingBox;
							if(Ext.isEmpty(min.x) || bb.min.x < min.x) min.x = bb.min.x;
							if(Ext.isEmpty(min.y) || bb.min.y < min.y) min.y = bb.min.y;
							if(Ext.isEmpty(min.z) || bb.min.z < min.z) min.z = bb.min.z;

							if(Ext.isEmpty(max.x) || bb.max.x > max.x) max.x = bb.max.x;
							if(Ext.isEmpty(max.y) || bb.max.y > max.y) max.y = bb.max.y;
							if(Ext.isEmpty(max.z) || bb.max.z > max.z) max.z = bb.max.z;

							Ext.Array.push(arr,Ext.Object.getValues(bb.max));
							Ext.Array.push(arr,Ext.Object.getValues(bb.min));
						}
					}
				}
			}
		}

		if(arr.length){
			var offset = new THREE.Vector3();
			offset.addVectors( max, min );

//OBJを動かす場合
			if(Ext.isDefined(self._offset)){
				offset.multiplyScalar( -0.5 );
//				console.log(min);
//				console.log(max);
//				console.log(offset);
				self.__group.matrix.identity();
				self.__group.applyMatrix( new THREE.Matrix4().makeTranslation( offset.x, offset.y, offset.z ) );

				if(Ext.isEmpty(self._offset)) self._offset = new THREE.Vector3();
				self._offset.copy(offset);

			}
//cameraを動かす場合
			else{
				offset.multiplyScalar( 0.5 );
				self.__camera.position.setX(offset.x);
				self.__camera.position.setZ(offset.z);
				self.__target.copy(offset);
			}

			if(!zoom) return;

			var width = self.__SCREEN_WIDTH;
			var height = self.__SCREEN_HEIGHT;
			self.__zoom.translate([width/2, height/2]);

//最長を計算する
			var valArr = [max.x-min.x,max.y-min.y,max.z-min.z];
/**/
			valArr.push(Math.pow(valArr[0]*valArr[0] + valArr[1]*valArr[1], 0.5));
			valArr.push(Math.pow(valArr[1]*valArr[1] + valArr[2]*valArr[2], 0.5));
			valArr.push(Math.pow(valArr[0]*valArr[0] + valArr[2]*valArr[2], 0.5));
/**/
			var maxVal = Ext.Array.max(valArr);
			self.setYRange(maxVal);

//			self.ZOOM = self.getYRangeZoom(maxVal);
//			self.DISP_ZOOM =  Math.round(self.ZOOM*5-0.5)+1;
//			console.log(self.ZOOM,self.DISP_ZOOM,(self.DISP_ZOOM-1)/5);

//			var val = maxVal;
//			self.__camera.left = self.__camera.bottom = val/-2;
//			self.__camera.right = self.__camera.top = val/2;
//			self.__camera.updateProjectionMatrix();


//			self.startAnimate();
		}
	},

	_findMesh : function(param){
		var self = this;
		var __findMesh = null;
		for(var i=0;i<self.__group.children.length;i++){
			var mesh = self.__group.children[i];
			if(mesh[Ag.Def.OBJ_URL_DATA_FIELD_ID] !== param[Ag.Def.OBJ_URL_DATA_FIELD_ID]) continue;
			__findMesh = mesh;
			break;
		}
		return __findMesh;
	},

	setObjProperties : function(params){
		var self = this;
		self.__tempObjParams = Ext.isArray(params) ? Ext.Array.clone(params) : [Ext.Object.merge({},params)] ;
		if(self.__config.usePromise && Ext.isFunction(window.Promise)){
			var promises = [];
			Ext.each(self.__tempObjParams,function(param){
				promises.push(self._setObjPropertiesPromise(param));
			});
			Promise.all(promises).then(function(){
				self._calcCameraPos();
				self.render();
			});
		}else{
			self._setObjProperties();
		}
		return;
	},

	_setObjPropertiesPromise : function(param){
		var self = this;
		return new Promise(function(resolve, reject){
			if(!Ext.isBoolean(param[Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID])) param[Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID] = true;
			if(!Ext.isNumber(param[Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID])) param[Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID] = 1;
			var mesh = self._findMesh(param);
			if(mesh) self.setMeshProperties(mesh,param);
			resolve();
		});
	},

	_setObjProperties : function(){
		var self = this;
		var param = self.__tempObjParams.shift();
		if(param){
			if(!Ext.isBoolean(param[Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID])) param[Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID] = true;
			if(!Ext.isNumber(param[Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID])) param[Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID] = 1;
			var mesh = self._findMesh(param);
			if(mesh) self.setMeshProperties(mesh,param);
			if(window.setImmediate){
				window.setImmediate(Ext.bind(self._setObjProperties,self));
			}else{
				self._setObjProperties();
			}
		}else{
			self._calcCameraPos();
			self.render();
		}
	},

	cancelLoadObj : function(callback){
		var self = this;
		if(self.__isLoadingObj){
			self.__cancelLoadingObj = true;
			if(Ext.isFunction(callback)){
				self.on('load',function(self,successful){
					callback();
				},self,{single:true});
			}
		}
		else if(Ext.isFunction(callback)){
			callback();
		}
	},

	loadObj : function(params, options){
		var self = this;

		if(self.__isLoadingObj){
			self.on('load',function(self,successful){
				self.loadObj(params, options);
			},self,{single:true});
		}

//		if(Ext.isObject(options) && Ext.isBoolean(options.hideAllObj)){
//			if(options.hideAllObj) self.hideAllObj();
//		}else{
		self.hideAllObj();
//		}

		self.__cancelLoadingObj = false;
		self.__isLoadingObj = true;

//		if(Ext.isEmpty(self._loadMask)) self._loadMask = new Ext.LoadMask(myPanel, {msg:"Please wait..."});
		Ext.get(self.__domElement).mask('Please wait...');

//		self.stopAnimate();

		self.__onLoadCallback = null;
		self.__onLoadOptions = null;
		if(Ext.isFunction(options)){
			self.__onLoadCallback = options;
		}else if(Ext.isObject(options)){
			if(Ext.isFunction(options.callback)) self.__onLoadCallback = options.callback;
			self.__onLoadOptions = Ext.Object.merge({},options);
		}

		self.__tempObjParams = Ext.isArray(params) ? Ext.Array.clone(params) : [Ext.Object.merge({},params)] ;
		self.__tempObjParamsCount = 0;
		self.__tempObjParamsTotal = 0;
		if(Ext.isArray(self.__tempObjParams)) self.__tempObjParamsTotal = self.__tempObjParams.length;

		if(self.__tempObjParamsTotal){
			if(Ext.isObject(self.__onLoadOptions) && Ext.isNumeric(self.__onLoadOptions.hitfma)){
				Ext.get(self.__domElement).mask(Ext.String.format('Hit {0} FMA: {1} obj files: Loading {2}/{3}',self.__onLoadOptions.hitfma,self.__tempObjParamsTotal,0,self.__tempObjParamsTotal));
			}
			else{
				Ext.get(self.__domElement).mask(Ext.String.format('{0} obj files: Loading {1}/{2}',self.__tempObjParamsTotal,0,self.__tempObjParamsTotal));
//				Ext.get(self.__domElement).mask(Ext.String.format('Please wait... [{0}%]',0));
			}
		}


		if(self.__config.usePromise && Ext.isFunction(window.Promise)){
			self.__loadingObjRequests = {};
			var promises = [];
			Ext.each(self.__tempObjParams,function(param){
				promises.push(self._loadObjPromise(param));
			});
			Promise.all(promises).then(function(){
				self.autoFocus();
				if(Ext.isFunction(self.__onLoadCallback)) self.__onLoadCallback();
				Ext.get(self.__domElement).unmask();
				var successful = !self.__cancelLoadingObj;
				delete self.__loadingObjRequests;
				self.__cancelLoadingObj = false;
				self.__isLoadingObj = false;
				self.fireEvent('load',self,successful);
			}).catch(function (e) {
//				console.error('error');
//				console.error(e);
				Ext.get(self.__domElement).unmask();
				delete self.__loadingObjRequests;
				self.__cancelLoadingObj = false;
				self.__isLoadingObj = false;
				self.fireEvent('load',self,false);
			});
		}else{
			self._loadObj();
		}
		return;

	},

	_loadObjPromise : function(param){
		var self = this;

		return new Promise(function(resolve, reject){
			var func = function(){

//				console.log('self.__cancelLoadingObj',self.__cancelLoadingObj);
//				if(self.__cancelLoadingObj){
//					reject('cancel');
//					return;
//				}

				var countUp = function(){
					if(self.__cancelLoadingObj){
						Ext.get(self.__domElement).mask('Cancel...');
					}
					else if(self.__tempObjParamsTotal){
						self.__tempObjParamsCount++;

						if(Ext.isObject(self.__onLoadOptions) && Ext.isNumeric(self.__onLoadOptions.hitfma)){
							Ext.get(self.__domElement).mask(Ext.String.format('Hit {0} FMA: {1} obj files: Loading {2}/{3}',self.__onLoadOptions.hitfma,self.__tempObjParamsTotal,self.__tempObjParamsCount,self.__tempObjParamsTotal));
						}
						else{
							Ext.get(self.__domElement).mask(Ext.String.format('{0} obj files: Loading {1}/{2}',self.__tempObjParamsTotal,self.__tempObjParamsCount,self.__tempObjParamsTotal));
	//						Ext.get(self.__domElement).mask(Ext.String.format('Please wait... [{0}%]', Math.floor((self.__tempObjParamsCount/self.__tempObjParamsTotal)*100) ));
						}
					}
					resolve();
	//				reject();
				}

				if(!Ext.isBoolean(param[Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID])) param[Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID] = true;
				if(!Ext.isNumber(param[Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID])) param[Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID] = 1;
				var mesh = self._findMesh(param);
				if(mesh){
					self.setMeshProperties(mesh,param);
					countUp();
				}else if(param[Ag.Def.OBJ_URL_DATA_FIELD_ID]){
	//				console.log('self.__cancelLoadingObj',self.__cancelLoadingObj);
					self.__loadingObjRequests[param[Ag.Def.OBJ_URL_DATA_FIELD_ID]] = self._objLoader.load(param[Ag.Def.OBJ_URL_DATA_FIELD_ID], function(container){
//						console.log('self.__cancelLoadingObj',self.__cancelLoadingObj);
						delete self.__loadingObjRequests[param[Ag.Def.OBJ_URL_DATA_FIELD_ID]];
						if(self.__cancelLoadingObj){
							Object.keys(self.__loadingObjRequests).forEach(function(url){
								if(self.__loadingObjRequests[url] && self.__loadingObjRequests[url].abort) self.__loadingObjRequests[url].abort();
								delete self.__loadingObjRequests[url];
							});
							reject('cancel');
							return;
						}else{
							self._loadingManager.onLoad(container,param);
						}
						countUp();
					});
//					console.log(request);
				}else{
					countUp();
				}
			};
			func();
//			setTimeout(func,250);
		});
	},

	_loadObj : function(){
		var self = this;

		if(self.__tempObjParamsTotal){
			self.__tempObjParamsCount++;
			if(Ext.isObject(self.__onLoadOptions) && Ext.isNumeric(self.__onLoadOptions.hitfma)){
				Ext.get(self.__domElement).mask(Ext.String.format('Hit {0} FMA: {1} obj files: Loading {2}/{3}',self.__onLoadOptions.hitfma,self.__tempObjParamsTotal,self.__tempObjParamsCount,self.__tempObjParamsTotal));
			}
			else{
				Ext.get(self.__domElement).mask(Ext.String.format('{0} obj files: Loading {1}/{2}',self.__tempObjParamsTotal,self.__tempObjParamsCount,self.__tempObjParamsTotal));
//				Ext.get(self.__domElement).mask(Ext.String.format('Please wait... [{0}%]', Math.floor((self.__tempObjParamsCount/self.__tempObjParamsTotal)*100) ));
			}
		}

		var param = self.__tempObjParams.shift();
		if(param && !self.__cancelLoadingObj){
			if(!Ext.isBoolean(param[Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID])) param[Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID] = true;
			if(!Ext.isNumber(param[Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID])) param[Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID] = 1;
			var mesh = self._findMesh(param);
			if(mesh){
				self.setMeshProperties(mesh,param);
				if(window.setImmediate){
					window.setImmediate(Ext.bind(self._loadObj,self));
				}else{
					self._loadObj();
				}
			}else{
				self._objLoader.load(param[Ag.Def.OBJ_URL_DATA_FIELD_ID], function(container){
					self._loadingManager.onLoad(container,param);
					if(window.setImmediate){
						window.setImmediate(Ext.bind(self._loadObj,self));
					}else{
						self._loadObj();
					}
				});
			}
		}else{
			self.autoFocus();
			if(Ext.isFunction(self.__onLoadCallback)) self.__onLoadCallback();
			Ext.get(self.__domElement).unmask();
			var successful = !self.__cancelLoadingObj;
			self.__cancelLoadingObj = false;
			self.__isLoadingObj = false;
			self.fireEvent('load',self,successful);
		}
	},

	getIntersectObjects : function(mouseXY,all){
		var self = this;

		var target_objects = [];
		for(var i=0;i<self.__group.children.length;i++){
			if(self.__group.children[i] instanceof THREE.Mesh){
				var mesh = self.__group.children[i];
				if(mesh.visible || Ext.isBoolean(mesh[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID])){
					if(all){
						target_objects.push(mesh);
					}
	//				else if(mesh.material.opacity>=1){
					else if(mesh.material.opacity>=1 || Ext.isBoolean(mesh[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID])){
						target_objects.push(mesh);
					}
				}
			}
			else if(self.__group.children[i] instanceof THREE.Group){
				for(var j=0;j<self.__group.children[i].children.length;j++){
					var mesh = self.__group.children[i].children[j];
					if(mesh.visible){
//					if(mesh.visible || Ext.isBoolean(mesh[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID])){
						if(all){
							target_objects.push(mesh);
						}
		//				else if(mesh.material.opacity>=1){
						else if(mesh.material.opacity>=1 || Ext.isBoolean(mesh[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID])){
							target_objects.push(mesh);
						}
					}
				}
			}
		}

/*
		//対象は「mesh.visible == true」の為、とりあえず、mesh.visible を true にする
		target_objects.forEach(function(mesh){
			if(!mesh.visible && Ext.isBoolean(mesh[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID])){
				mesh.__visible = mesh.visible;
				mesh.visible = true;
			}
		});
*/

//		var mouseVec = new THREE.Vector3(
		var mouseVec = new THREE.Vector2(
			(   mouseXY.x / self.__SCREEN_WIDTH   ) * 2 - 1,
			- ( mouseXY.y / self.__SCREEN_HEIGHT  ) * 2 + 1
		);

		var raycaster = new THREE.Raycaster();
		raycaster.setFromCamera( mouseVec, self.__camera );

//		jQuery.each(target_objects,function(){
//			if(this.material.opacity>=1){
//				this.material.side = THREE.DoubleSide;
//			}
//		});

		var intersects = raycaster.intersectObjects( target_objects );

//		jQuery.each(target_objects,function(){
//			if(this.material.opacity>=1){
//				this.material.side = THREE.FrontSide;
//			}
//		});

/*
		//「mesh.__visible」が存在する場合、値を mesh.visible に戻して、mesh.__visible を削除
		target_objects.forEach(function(mesh){
			if(Ext.isBoolean(mesh.__visible) && Ext.isBoolean(mesh[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID])){
				mesh.visible = mesh.__visible;
				delete mesh.__visible;
			}
		});
*/

		if(Ext.isDefined(self._offset)){
		}


		//Clip時
		if(intersects.length>0 && self.__renderer.clippingPlanes.length > 0){
			intersects = intersects.filter(function(elem){
				return self.__renderer.clippingPlanes.every(function(elem2){
					return elem2.distanceToPoint(elem.point) > 0;
				});
			});
		}

		return intersects;
	},

	hideAllObj : function(){
		var self = this;

		if(self.__isLoadingObj){
			self.__cancelLoadingObj = true;
			self.on('load',function(self,successful){
//				console.log(successful);
				self.hideAllObj();
			},self,{single:true});
		}


		for(var i=0;i<self.__group.children.length;i++){
			var mesh = self.__group.children[i];
			if(mesh instanceof THREE.Mesh){
				mesh.visible = false;
			}
			else if(mesh instanceof THREE.Group){
				for(var j=0;j<mesh.children.length;j++){
					mesh.children[j].visible = false;
				}
			}
		}
		self.render();
	},

	showObj : function(urls){
		var self = this;
		self.stopAnimate();

		self.hideAllObj();

		Ext.iterate(urls,function(url,i,a){
			for(var i=0;i<self.__group.children.length;i++){
				var mesh = self.__group.children[i];
				if(mesh[Ag.Def.OBJ_URL_DATA_FIELD_ID]===url){
					if(mesh instanceof THREE.Mesh){
						mesh.visible = true;
					}
					else if(mesh instanceof THREE.Group){
						for(var j=0;j<mesh.children.length;j++){
							mesh.children[j].visible = false;
						}
					}
				}
			}
		},self);
		self.autoFocus();
	},

	exportObjs : function(){
		var self = this;
		var exporter = new THREE.OBJMergeExporter();
		return exporter.parse(self.__group);
	},

	agDeg2Rad : function(deg){
		return deg * Math.PI / 180;
	},

	agRad2Deg : function(rad){
		return rad * 180 / Math.PI;
	},

	addLongitude : function(d){
		var self = this;
		self.__rotateGroup.rotateZ(self.agDeg2Rad(Math.round(-d*10)/10));
		self.render();
		return self;
	},

	addLatitude : function(d){
		var self = this;
		self.__rotateGroup.rotateX(self.agDeg2Rad(Math.round(d*10)/10));
		self.render();
		return self;
	},

	setHorizontal : function(angle){
		var self = this;
		while (angle >= 360) {
			angle = angle - 360;
		}
		while (angle < 0) {
			angle = angle + 360;
		}
		self.__longitude = angle-90;
		self._calcCameraPos();
		self.fireEvent('rotate', self, self._calcRotateDeg());
//		self.zoomCB();
		self.render();
		return self;
	},

	setVertical : function(angle){
		var self = this;
		while (angle >= 360) {
			angle = angle - 360;
		}
		while (angle < 0) {
			angle = angle + 360;
		}
		self.__latitude = angle;
		self._calcCameraPos();
		self.fireEvent('rotate', self, self._calcRotateDeg());
//		self.zoomCB();
		self.render();
		return self;
	},

	toImage : function(){
		try{
			var self = this;
			window.open(self.__renderer.domElement.toDataURL('image/png'), '_toImage' );
		}catch(e){
			console.error(e);
		}
	},

	setBackgroundColor : function(color){
		var self = this;
		self.__renderer.setClearColor(color);
		self._calcCameraPos();
		self.render();
	},

	old_convertCoordinateScreenTo3D : function(screenXY){
		var self = this;
		var vec2 = new THREE.Vector2(
			  ( screenXY.x / self.__SCREEN_WIDTH  ) * 2 - 1,
			- ( screenXY.y / self.__SCREEN_HEIGHT ) * 2 + 1
		);
		var s_vec3 = new THREE.Vector3( vec2.x, vec2.y, -1.0 );
		var e_vec3 = new THREE.Vector3( vec2.x, vec2.y, 1.0 );
		s_vec3.unproject( self.__camera );
		console.log('s_vec3',s_vec3);
		e_vec3.unproject( self.__camera );
		e_vec3.sub( s_vec3 ).normalize();
		return e_vec3.multiplyScalar(s_vec3.y / - ( e_vec3.y )).add(s_vec3);
	},

	convertCoordinateScreenTo3D : function(screenXY){
		var self = this;
		var vec2 = new THREE.Vector2(
			  ( screenXY.x / self.__SCREEN_WIDTH  ) * 2 - 1,
			- ( screenXY.y / self.__SCREEN_HEIGHT ) * 2 + 1
		);
		var s_vec3 = new THREE.Vector3( vec2.x, vec2.y, -1.0 );
		s_vec3.unproject( self.__camera );
		return s_vec3;
	},

	convertCoordinate3DToScreen : function(obj) {
		var self = this;
/*
		var width = self.__SCREEN_WIDTH;
		var height = self.__SCREEN_HEIGHT;

		var pos = position.clone();
		var projScreenMat = new THREE.Matrix4();
		projScreenMat.multiplyMatrices(self.__camera.projectionMatrix, self.__camera.matrixWorldInverse);
		pos.applyMatrix4(projScreenMat);
		return new THREE.Vector2(
			(  pos.x + 1) * width  / 2, // + xy[0],
			(- pos.y + 1) * height / 2 //+ xy[1]
		);
*/

		var vector = new THREE.Vector3();
		var width = self.__SCREEN_WIDTH / 2;
		var height = self.__SCREEN_HEIGHT / 2;
		obj.updateMatrixWorld();

		vector.setFromMatrixPosition(obj.matrixWorld);
		vector.project(self.__camera);

		vector.x = ( vector.x * width ) + width;
		vector.y = - ( vector.y * height ) + height;

		return new THREE.Vector2(vector.x, vector.y);

	},

	setAutoFocus : function(onoff){
		var self = this;
		self.__autofocus = Ext.isBoolean(onoff) ? onoff : (onoff ? true : false);
/*
		if(self.__autofocus){
			self.focus();
			self._calcCameraPos();
			self.render();
		}
*/
		return self.__autofocus;
	},
	getAutoFocus : function(){
		var self = this;
		return Ext.isBoolean(self.__autofocus) ? self.__autofocus : true;
	},
	autoFocus : function(){
		var self = this;
		if(self.getAutoFocus()){
			self.focus();
			self._calcCameraPos();
		}
		self.render();
	},

	setAutoRender : function(onoff){
		var self = this;
		self.__autorender = Ext.isBoolean(onoff) ? onoff : (onoff ? true : false);
/*
		if(self.__autorender){
			self.render();
		}
*/
		return self.__autofocus;
	},
	getAutoRender : function(){
		var self = this;
		return Ext.isBoolean(self.__autorender) ? self.__autorender : true;
	},

	setTarget : function(vector3){
		var self = this;
		self.__target.copy(vector3);
//		console.log(self.__target);
	},
	getTarget : function(){
		var self = this;
		return self.__target.clone();
	},

	setCameraPosition : function(position,up){
		var self = this;
		self.__camera.position.copy(position);
		if(up) self.__camera.up.copy(up);
//		console.log(self.__camera.position);
		self.__camera.updateProjectionMatrix();
	},
	getCameraPosition : function(){
		var self = this;
		return self.__camera.position.clone();
	},

	setCameraUp : function(vector3){
		var self = this;
		self.__camera.up.copy(vector3);
//		console.log(self.__camera.up);
		self.__camera.updateProjectionMatrix();
	},
	getCameraUp : function(){
		var self = this;
		return self.__camera.up.clone();
	},

	_createPinTextLabel : function(){
		var self = this;
		var div = document.createElement('div');
		$(div).addClass('pin-text-label');
		$('<label>').appendTo($(div));
		return {
			element: div,
			parent: false,
			position: new THREE.Vector3(0,0,0),
			setHTML: function(html) {
				$(this.element).children('label').html(html);
			},
			setParent: function(threejsobj) {
				this.parent = threejsobj;
			},
			setColor: function(color) {
				$(this.element).css({
					color : color
				});
			},
			updatePosition: function() {
				var coords2d = this.parent ? self.convertCoordinate3DToScreen(this.parent) : {x:0,y:0};
				$(this.element).css({
					left : coords2d.x,
					top  : coords2d.y
				});
			}
		};
	},

	_createPinDescriptionLabel : function(){
		var self = this;
		var div = document.createElement('div');
		$(div).addClass('pin-description-label');
		$('<label>').appendTo($(div));
		return {
			element: div,
			parent: false,
			line: false,
			position: new THREE.Vector3(0,0,0),
			setHTML: function(html) {
				$(this.element).children('label').html(html);
			},
			setParent: function(threejsobj) {
				this.parent = threejsobj;
			},
			setLine: function(threejsobj) {
				this.line = threejsobj;
			},
			setColor: function(color) {
				$(this.element).css({
					color : color
				});
			},
			offset: function(){
				return $(this.element).children('label').offset();
			},
			position: function(){
				return $(this.element).children('label').position();
			},
			height: function(){
				return $(this.element).children('label').height();
			},
			width: function(){
				return $(this.element).children('label').width();
			}
		};
	},

	createPin : function(dir, origin, options){
		var self = this;
		options = options || {};
		options.color = options.color || 0x0000ff;
		options.text = options.text || '';
//		options.description = options.description || '';

		options.shape = options.shape || 'PIN_LONG';
		options.size = options.size || 112.5;
		options.line = options.line || 0;

//		console.log(options);

		var zoomScale = self.getZoomScale();
		var yrange = self.getZoomYRange(zoomScale);
		var yrate = yrange / self.__MAX_HEIGHT;

		var voxel = null;
/*
		if(self.__pinGroup && $.isArray(self.__pinGroup.children) && self.__pinGroup.children.length){
			for(var i = 0, l = self.__pinGroup.children.length; i < l; i ++ ){
				var child = self.__pinGroup.children[ i ];
				if(child.visible) continue;
				if(options.shape === 'PIN_LONG' && child instanceof THREE.LargePinHelper){
					voxel = child;
					break;
				}
				else if(options.shape === 'CONE' && child instanceof THREE.ConeHelper){
					voxel = child;
					break;
				}
				else if(options.shape === 'CIRCLE' && child instanceof THREE.CircleHelper){
					voxel = child;
					break;
				}
			}
		}
*/

		if(voxel === null){
			if(options.shape === 'PIN_LONG'){
				voxel = new THREE.LargePinHelper( dir, origin, options.color, options.size );
			}
			else if(options.shape === 'CONE'){
				voxel = new THREE.ConeHelper( dir, origin, options.color, options.size );
			}
			else{
				voxel = new THREE.CircleHelper( dir, origin, options.color, options.size );
			}
			self.__pinGroup.add( voxel );
		}
		else{
			voxel.visible = true;
			voxel.setSize( options.size );
			voxel.setColor( options.color );
			voxel.position.copy( origin );
			voxel.setDirection( dir );
		}

		voxel.setScale(yrate);

		if(options.text){
			var text = self._createPinTextLabel();
			text.setHTML(options.text);
			text.setColor(options.color);
			text.setParent(voxel);
			voxel.__text = text;

			self.__pintextlabels = self.__pintextlabels || [];
			self.__pintextlabels.push(text);
			self.__domElement.appendChild(text.element);
		}

		if(options.description){
			var description = self._createPinDescriptionLabel();
			description.setHTML(options.description);
			description.setColor(options.color);
			description.setParent(voxel);
			voxel.__description = description;

			self.__pindescriptionlabels = self.__pindescriptionlabels || [];
			self.__pindescriptionlabels.push(description);
			self.__domElement.appendChild(description.element);

			if(options.line){
//			console.log( intersect.face.normal, intersect.point, options.color );
//			console.log(voxel);

//			console.log($(self.__domElement).offset(),$(self.__domElement).position());
//			console.log(description.offset(),description.position(),description.width(),description.height());

				var po = $(self.__domElement).offset();
				var co = description.offset();

	//			var position = description.position();
				var position = {};
				position.top = (co.top-po.top);
				position.left = (co.left-po.left);
	//			console.log(position);

				position.top += description.height()/2;
				position.left += description.width();// + 6;
	//			console.log(position);

				self.__scene.updateMatrixWorld();
				self.__camera.updateMatrixWorld();

				var description_vector = self.convertCoordinateScreenTo3D(new THREE.Vector2(position.left,position.top));
	//			console.log(description_vector);
	//			description_vector.y = -self.__MAX_HEIGHT;


				voxel.updateMatrixWorld();
				var vector = new THREE.Vector3();
				if(options.line === 1){
					vector.setFromMatrixPosition( voxel.line ? voxel.line.matrixWorld : voxel.cone.matrixWorld );
				}else if(options.line === 2){
					vector.setFromMatrixPosition( voxel.cone ? voxel.cone.matrixWorld : voxel.line.matrixWorld );
				}

				var dline = null;
/*
				if(self.__pinDescriptionLineGroup && $.isArray(self.__pinDescriptionLineGroup.children) && self.__pinDescriptionLineGroup.children.length){
					for(var i = 0, l = self.__pinDescriptionLineGroup.children.length; i < l; i ++ ){
						var child = self.__pinGroup.children[ i ];
						if(child.visible) continue;
						dline = child;
					}
				}
*/
				if(dline === null){
					var geometry = new THREE.BufferGeometry();
					var vertices = new Float32Array( [
						description_vector.x, description_vector.y,  description_vector.z,
						vector.x,  vector.y,  vector.z,
					]);
					geometry.addAttribute( 'position', new THREE.BufferAttribute( vertices, 3 ) );
					geometry.computeBoundingSphere();

					var material = new THREE.LineBasicMaterial( {
						color: options.color,
						linewidth: 2,
						linecap: 'round',
						linejoin: 'round'
					});
					dline = new THREE.Line( geometry, material );

					self.__pinDescriptionLineGroup.add(dline);
				}
				else{
					dline.visible = true;
					var i = 0;
					dline.geometry.attributes.position.array[ i++ ] = description_vector.x;
					dline.geometry.attributes.position.array[ i++ ] = description_vector.y;
					dline.geometry.attributes.position.array[ i++ ] = description_vector.z;
					dline.geometry.attributes.position.array[ i++ ] = vector.x;
					dline.geometry.attributes.position.array[ i++ ] = vector.y;
					dline.geometry.attributes.position.array[ i++ ] = vector.z;
					dline.geometry.attributes.position.needsUpdate = true;
				}


				description.setLine(dline);
			}
		}

		return voxel;
	},

	removeAllPin : function(){
		var self = this;
		if(self.__pinGroup && $.isArray(self.__pinGroup.children) && self.__pinGroup.children.length){
//			for(var i = 0, l = self.__pinGroup.children.length; i < l; i ++ ){
			for(var i = self.__pinGroup.children.length - 1; i >= 0; i -- ){
				var child = self.__pinGroup.children[ i ];
				if(child.visible){
					var voxel = child;

					voxel.visible = false;
					if(voxel.__text){
						$(voxel.__text.element).remove();
						delete voxel.__text;
					}
					if(voxel.__description){
						if(voxel.__description.line){
							voxel.__description.line.visible = false;
							self.__pinDescriptionLineGroup.remove(voxel.__description.line);
							delete voxel.__description.line;
						}
						$(voxel.__description.element).remove();
						delete voxel.__description;
					}
				}
				self.__pinGroup.remove(child);
			}
		}
	},

	addLegend : function(legend){
		var self = this;
		legend = legend || {};
		self.removeLegend();
//		var $base = $('div.legend-text-label');
		var $base = self.$_domElement.find('div.legend-text-label');
		if(legend.title){
			$('<div>').text(legend.title).appendTo($base);
		}
		if(legend.legend){
			if($.isArray(legend.legend) && legend.legend.length){
				legend.legend.forEach(function(text){
					if(text){
						$('<div>').text(text).appendTo($base);
					}else{
						$('<div>').html('&nbsp;').appendTo($base);
					}
				});
			}else{
				$('<div>').text(legend.legend).appendTo($base);
			}
		}
		if(legend.author){
			$('<div>').text(legend.author).appendTo($base);
		}
	},

	removeLegend : function(){
		var self = this;
//		$('div.legend-text-label').empty();
		self.$_domElement.find('div.legend-text-label').empty();
	},


	setClip : function(planes){
		var self = this;
		planes = planes || [];
		planes.forEach(function(p,i){
			if(self.__renderer.clippingPlanes[i]){
				var plane = self.__renderer.clippingPlanes[i];
				plane.setComponents(p.x, p.y, p.z, p.constant);
			}else{
				var plane = new THREE.Plane();
				plane.setComponents(p.x, p.y, p.z, p.constant);
				self.__renderer.clippingPlanes.push(plane);
			}
		});
		self.__renderer.clippingPlanes.length = planes.length;
		self.render();
	},

	clearClip : function(){
		var self = this;
		self.__renderer.clippingPlanes.length = 0;
		self.render();
	},

	calcClip : function(h,v){
		var self = this;

		var longitude = h-90;
		var latitude  = v-0;
		var m_ag_epsilon = 0.0000001;

		var eyeLongitudeRadian = self.agDeg2Rad(longitude);
		var eyeLatitudeRadian = self.agDeg2Rad(latitude);

		console.log(eyeLongitudeRadian,eyeLatitudeRadian);


		var yAxis = new THREE.Vector3();

		var zAxis = new THREE.Vector3();
		var xAxis = new THREE.Vector3();
		var tmp0 = new THREE.Vector3();

		var cEyeLongitude = Math.cos(eyeLongitudeRadian);
		var sEyeLongitude = Math.sin(eyeLongitudeRadian);
		var cEyeLatitude = Math.cos(eyeLatitudeRadian);
		var sEyeLatitude = Math.sin(eyeLatitudeRadian);

		zAxis.x = cEyeLatitude * cEyeLongitude;
		zAxis.y = cEyeLatitude * sEyeLongitude;
		zAxis.z = sEyeLatitude;

		console.log(zAxis);

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
			var remind = Math.abs(Math.round(latitude) % 360);
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
		console.log(yAxis);
		return yAxis;
	},

	setGrid : function(params){
		var self = this;

		if(self.__grid) self.__scene.remove(self.__grid);

		params = Ext.apply({},params||{},{
			size: self.__MAX_HEIGHT,
			divisions: 10,
			color1: 0x00ff00,
			color2: 0x00ff00,
			visible: true
		});
//		console.log(params);
		self.__grid = new THREE.GridHelper( params.size, params.divisions, params.color1, params.color2 );
		if(self.__grid){
			self.__grid.visible = params.visible;
			self.__scene.add( self.__grid );
		}

		self.render();
	},

	clearGrid : function(){
		var self = this;
		if(self.__grid) self.__grid.visible = false;
		self.render();
	},

	_dump : function(aStr){
		if(window.dump) window.dump("AgMainRenderer.js:"+aStr+"\n");
		try{if(console && console.log) console.log("AgMainRenderer.js:"+aStr);}catch(e){}
	}

});
