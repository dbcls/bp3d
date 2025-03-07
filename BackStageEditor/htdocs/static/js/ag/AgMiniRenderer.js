window.requestAnimationFrame = window.requestAnimationFrame ||
  window.webkitRequestAnimationFrame ||
  window.mozRequestAnimationFrame ||
  window.msRequestAnimationFrame;
window.cancelAnimationFrame = window.cancelAnimationFrame ||
  window.mozCancelAnimationFrame ||
  window.webkitCancelAnimationFrame ||
  window.msCancelAnimationFrame;

function AgMiniRenderer(config){
	var self = this;

	self._config = config || {};
	self._config.height = self._config.height || 96;
	self._config.rate   = self._config.rate   || 2;
	self._config.width  = self._config.width  || self._config.height/self._config.rate;

//	var rate = 3/2;
	var rate = self._config.rate;

	self.SCREEN_HEIGHT = self._config.height;
	self.SCREEN_WIDTH  = self._config.width;
//	self.SCREEN_HEIGHT = 60;

	self.$_domElement = $('<div style="width:'+(self.SCREEN_WIDTH)+'px;height:'+(self.SCREEN_HEIGHT)+'px;background-color:#f0f0f0;border:1px solid #b5b8c8;position:relative;">');
	self.domElement = self.$_domElement.get(0);
	self.SCREEN_HEIGHT -= 2;
	self.SCREEN_WIDTH  -= 2;

//	self._loadObjParams = [];

	self.$_domElement.click(function(e){
		if(Ext.isEmpty(self._animate)){
			self.startAnimate();
		}else{
			self.stopAnimate();
		}

		return false;
	}).mousedown(function(e){
		return false;
	}).mousemove(function(e){
		return false;
	}).mouseup(function(e){
		return false;
	}).bind('mousewheel',function(e){
		return false;
	});

	self._target = new THREE.Vector3(0,0,0);

	self._MAX_HEIGHT = 1800;
	self._camera = new THREE.OrthographicCamera((self._MAX_HEIGHT / rate)/-2, (self._MAX_HEIGHT / rate)/2, self._MAX_HEIGHT/2, self._MAX_HEIGHT/-2, 0.1, 10000 );
	self._camera.position.set(0,-900,0);
	self._camera.up.set(0,0,1);
	self._camera.lookAt( self._target );

	self._scene = new THREE.Scene();

	self._scene.add( self._camera );

	// LIGHTS
	self._ambientLight = new THREE.AmbientLight( 0x221d16 );
	self._scene.add( self._ambientLight );

	self._directionalLight = new THREE.DirectionalLight( 0xffffff);

	self._directionalLight.position.copy(self._camera.position);
	self._directionalLight.target.position.copy(self._target);
	self._scene.add( self._directionalLight );
	self._scene.add( self._directionalLight.target );

	self._group = new THREE.Group();
	self._rotateGroup = new THREE.Group();
	self._rotateGroup.add(self._group);

//	self._group = new THREE.Camera();
//	self._group.lookAt( self._target );

//	self._scene.add(self._group);
	self._scene.add(self._rotateGroup);



	if(!Detector.webgl) Detector.addGetWebGLMessage();

	if(Detector.webgl){
		self._renderer = new THREE.WebGLRenderer({antialias:true,maxLights:6,preserveDrawingBuffer:true});
	}else{
		self._renderer = new THREE.CanvasRenderer({antialias:true,maxLights:6,preserveDrawingBuffer:true});
	}
	self._renderer.setSize( self.SCREEN_WIDTH, self.SCREEN_HEIGHT );
	self._renderer.setClearColor(Number('0xffffff'));

//	self._renderer.domElement.style.position = "relative";

	self.domElement.appendChild( self._renderer.domElement );

//	$(self._renderer.domElement).click(function(e){
//		e.preventDefault();
//		e.stopPropagation();
//		return false;
//	});

	self._loadingManager = {};
	if(THREE.LoadingManager) self._loadingManager = new THREE.LoadingManager();
	self._loadingManager.onLoad = function(event, param){
		var color = param.color || '#F0D2A0';
		if(color.substr(0,1) == '#') color = color.substr(1);
		color = Number('0x'+color);

		var mesh = (event.content ? event.content : event).children.shift();
		mesh.url = param.url;
//		mesh.material.blending = THREE.AdditiveAlphaBlending;
		mesh.material.color.setHex( color );
		mesh.material.opacity = param.opacity;
//		mesh.material.transparent = false;
		mesh.material.wireframe = false;
		mesh.visible = param.visible;
		mesh.doubleSided = true;

		mesh.material.blending = THREE.NormalBlending;
		if(mesh.material.opacity>=1){
			mesh.material.depthWrite = true;
			mesh.material.transparent = false;
			mesh.doubleSided = false;
			mesh.material.side = THREE.FrontSide;
		}
		else{
			mesh.material.depthWrite = false;
			mesh.material.transparent = true;
			mesh.doubleSided = true;
			mesh.material.side = THREE.DoubleSide;
		}

		mesh.geometry.computeBoundingBox();

		self._group.add( mesh );

//		if(self._group.children.length<self._loadObjParams.length) return;

	};

	self._objLoader = new THREE.OBJLoader();

	if(self._objLoader.addEventListener) self._objLoader.addEventListener('load',self._loadingManager.onLoad);

	self.startAnimate();
//	self.render();
};

AgMiniRenderer.prototype = {
//	get domElement(){
//		return this.$_domElement.get(0);
//	},

	stopAnimate : function(){
		var self = this;
		if(Ext.isEmpty(self._animate)) return false;
		cancelAnimationFrame( self._animate );
		delete self._animate;
		return true;
	},

	startAnimate : function(){
		var self = this;
		self.stopAnimate();
		self._animate = requestAnimationFrame( Ext.bind(self.startAnimate,self) );
		self.addLongitude(0.5);
//		self.addLatitude(0.5);
		self.render();
	},

	render : function(){
		var self = this;
		self._renderer.render( self._scene, self._camera );
	},

	focus : function(){
		var self = this;
//		if(self._group.children.length<self._loadObjParams.length) return;

		var max = new THREE.Vector3();
		var min = new THREE.Vector3();
		max.set(null,null,null);
		min.set(null,null,null);
		var arr = [];

		for(var i=0;i<self._group.children.length;i++){
			var mesh = self._group.children[i];
			if(mesh.visible && mesh.material.opacity>=1){
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
		if(arr.length==0){
			for(var i=0;i<self._group.children.length;i++){
				var mesh = self._group.children[i];
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

		if(arr.length){
			var offset = new THREE.Vector3();
			offset.addVectors( max, min );
			offset.multiplyScalar( -0.5 );
//			console.log(min);
//			console.log(max);
//			console.log(offset);
			self._group.matrix.identity();
			self._group.applyMatrix( new THREE.Matrix4().makeTranslation( offset.x, offset.y, offset.z ) );

			var valArr = [max.x-min.x,max.y-min.y,max.z-min.z];
//			console.log(Ext.Array.max(valArr));

			valArr.push(Math.pow(valArr[0]*valArr[0] + valArr[1]*valArr[1], 0.5));
			valArr.push(Math.pow(valArr[1]*valArr[1] + valArr[2]*valArr[2], 0.5));
			valArr.push(Math.pow(valArr[0]*valArr[0] + valArr[2]*valArr[2], 0.5));

//			var minVal = Ext.Array.min(valArr);
			var maxVal = Ext.Array.max(valArr);
//			console.log(Ext.Array.max(valArr));

//			valArr.push(Math.pow(valArr[0]*valArr[0] + valArr[1]*valArr[1] + valArr[2]*valArr[2], 0.5));
//			 maxVal = Ext.Array.max(valArr);
//			console.log(maxVal);

			var val = maxVal;
			self._camera.left = self._camera.bottom = val/-2;
			self._camera.right = self._camera.top = val/2;
			self._camera.updateProjectionMatrix();
		}
	},

	loadObj : function(params, onLoad){
		var self = this;

//		if(Ext.isEmpty(self._loadMask)) self._loadMask = new Ext.LoadMask(myPanel, {msg:"Please wait..."});
		Ext.get(self.domElement).mask("Please wait...");

		self.stopAnimate();
		self._onLoad = onLoad;
//		self._loadObjParams = Ext.Array.clone(params);
		self._tempObjParams = Ext.Array.clone(params);

		self.hideAllObj();

		self._loadObj();
		return;

	},

	_loadObj : function(){
		var self = this;
		var param = self._tempObjParams.shift();
		if(param){
			var exists = false;
			if(!Ext.isBoolean(param.visible)) param.visible = true;
			if(!Ext.isNumber(param.opacity)) param.opacity = 1;
			for(var i=0;i<self._group.children.length;i++){
				var mesh = self._group.children[i];
				if(mesh.url !== param.url) continue;

				var color = param.color || '#F0D2A0';
				if(color.substr(0,1) == '#') color = color.substr(1);
				color = Number('0x'+color);
				mesh.material.color.setHex( color );
				mesh.material.opacity = param.opacity;
				mesh.visible = param.visible && mesh.material.opacity>0 ? true : false;

				if(mesh.visible){
					if(mesh.material.opacity>=1){
						mesh.material.depthWrite = true;
						mesh.material.transparent = false;
						mesh.doubleSided = false;
						mesh.material.side = THREE.FrontSide;
					}
					else{
						mesh.material.depthWrite = false;
						mesh.material.transparent = true;
						mesh.doubleSided = true;
						mesh.material.side = THREE.DoubleSide;
					}
				}

				exists = true;
				break;
			}
			if(exists){
				self._loadObj();
			}else{
				self._objLoader.load(param.url, function(container){
					self._loadingManager.onLoad(container,param);
					self._loadObj();
				});
			}
		}else{
			self.focus();
			self.startAnimate();
			if(Ext.isFunction(self._onLoad)) self._onLoad();
			Ext.get(self.domElement).unmask();
		}
	},

	hideAllObj : function(){
		var self = this;
		for(var i=0;i<self._group.children.length;i++){
			var mesh = self._group.children[i];
			mesh.visible = false;
		}
		self.render();
	},

	showObj : function(urls){
		var self = this;
		self.stopAnimate();
//		if(self._group.children.length<self._loadObjParams.length) return;
//		return;

		self.hideAllObj();

		Ext.iterate(urls,function(url,i,a){
			for(var i=0;i<self._group.children.length;i++){
				var mesh = self._group.children[i];
				if(mesh.url===url) mesh.visible = true;
			}
		},self);
		self.focus();
		self.startAnimate();
	},

	agDeg2Rad : function(deg){
		return deg * Math.PI / 180;
	},

	agRad2Deg : function(rad){
		return rad * 180 / Math.PI;
	},

	addLongitude : function(d){
		var self = this;
		self._rotateGroup.rotateZ(self.agDeg2Rad(Math.round(-d*10)/10));
		self.render();
		return self;
	},

	addLatitude : function(d){
		var self = this;
		self._rotateGroup.rotateX(self.agDeg2Rad(Math.round(d*10)/10));
		self.render();
		return self;
	},

	toImage : function(){
		try{
			var self = this;
			window.open(self._renderer.domElement.toDataURL('image/png'), '_toImage' );
		}catch(e){
			console.error(e);
		}
	},

	convertCoordinateScreenTo3D : function(screenXY){
		var self = this;
		var vec2 = new THREE.Vector2(
			  ( screenXY.x / self.SCREEN_WIDTH  ) * 2 - 1,
			- ( screenXY.y / self.SCREEN_HEIGHT ) * 2 + 1
		);
		var s_vec3 = new THREE.Vector3( vec2.x, vec2.y, -1.0 );
		var e_vec3 = new THREE.Vector3( vec2.x, vec2.y, 1.0 );
		var projector = new THREE.Projector();
		s_vec3 = projector.unprojectVector( s_vec3, self._camera );
		e_vec3 = projector.unprojectVector( e_vec3, self._camera );
		e_vec3.subSelf( s_vec3 ).normalize();
		return e_vec3.multiplyScalar(s_vec3.y / - ( e_vec3.y )).addSelf(s_vec3);
	},

	convertCoordinate3DToScreen : function(position) {
		var self = this;
		var xy = Ext.get(self._renderer.domElement).getXY();
		var pos = position.clone();
		var projScreenMat = new THREE.Matrix4();
		projScreenMat.multiply(self._camera.projectionMatrix, self._camera.matrixWorldInverse);
		projScreenMat.multiplyVector3( pos );
		return new THREE.Vector2(
			(  pos.x + 1) * self.SCREEN_WIDTH  / 2 + xy[0],
			(- pos.y + 1) * self.SCREEN_HEIGHT / 2 + xy[1]
		);
	},

	_dump : function(aStr){
		if(window.dump) window.dump("AgMiniRenderer.js:"+aStr+"\n");
		try{if(console && console.log) console.log("AgMiniRenderer.js:"+aStr);}catch(e){}
	}

};
