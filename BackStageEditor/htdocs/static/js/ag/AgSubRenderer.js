function AgSubRenderer(){
	var self = this;

	var rate = 3/2;
	var rate = 2;

	self._loadObjUrls = [];

	self.SCREEN_HEIGHT = 96;
	self.SCREEN_WIDTH = self.SCREEN_HEIGHT / rate;
//	self.SCREEN_HEIGHT = 60;

	self.$_domElement = $('<div style="width:'+(self.SCREEN_WIDTH+4)+'px;height:'+(self.SCREEN_HEIGHT+4)+'px;background-color:#f0f0f0;border:2px solid #dddddd;position:relative;">');
	self.domElement = self.$_domElement.get(0);

	self.$_domElement.click(function(e){
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

	self._camera = new THREE.OrthographicCamera((1800 / rate)/-2, (1800 / rate)/2, 1800/2, 1800/-2, 0.1, 10000 );
	self._camera.position.set(0,-900,0);
	self._camera.up.set(0,0,1);
	self._camera.lookAt( self._target );

//	self._cameraPerspectiveHelper = new THREE.CameraHelper( self._camera );
//	self._camera.add( self._cameraPerspectiveHelper );

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
//	self._group = new THREE.Camera();
//	self._group.lookAt( self._target );

	self._scene.add(self._group);



	if(!Detector.webgl) Detector.addGetWebGLMessage();

	if(Detector.webgl){
		self._renderer = new THREE.WebGLRenderer({antialias:true,maxLights:6,preserveDrawingBuffer:true});
	}else{
		self._renderer = new THREE.CanvasRenderer({antialias:true,maxLights:6,preserveDrawingBuffer:true});
	}
	self._renderer.setSize( self.SCREEN_WIDTH, self.SCREEN_HEIGHT );
	self._renderer.setClearColor(Number('0xf0f0f0'));

//	self._renderer.domElement.style.position = "relative";

	self.domElement.appendChild( self._renderer.domElement );

//	$(self._renderer.domElement).click(function(e){
//		e.preventDefault();
//		e.stopPropagation();
//		return false;
//	});

	self._loadingManager = {};
	if(THREE.LoadingManager) self._loadingManager = new THREE.LoadingManager();
	self._loadingManager.onLoad = function(event){
//		console.log(arguments);
//		console.log(event);
		var color = '#F0D2A0';
		if(color.substr(0,1) == '#') color = color.substr(1);
		color = Number('0x'+color);

		var mesh = (event.content ? event.content : event).children.shift();
//		mesh.material.ambient.setHex( color );
		mesh.material.blending = THREE.AdditiveAlphaBlending;
		mesh.material.color.setHex( color );
		mesh.material.opacity = 1;
		mesh.material.transparent = false;
		mesh.material.wireframe = false;
		mesh.visible = true;
		mesh.doubleSided = true;


//		console.log(event);
//		console.log(mesh);




//		var center = THREE.GeometryUtils.center(mesh.geometry);
//		console.log(center);

		self._group.add( mesh );

		if(self._group.children.length<self._loadObjUrls.length) return;

//return;

		var max = new THREE.Vector3();
		var min = new THREE.Vector3();
		max.set(null,null,null);
		min.set(null,null,null);

		for(var i=0;i<self._group.children.length;i++){
			var mesh = self._group.children[i];
			mesh.geometry.computeBoundingBox();
			var bb = mesh.geometry.boundingBox;
			if(Ext.isEmpty(min.x) || bb.min.x < min.x) min.x = bb.min.x;
			if(Ext.isEmpty(min.y) || bb.min.y < min.y) min.y = bb.min.y;
			if(Ext.isEmpty(min.z) || bb.min.z < min.z) min.z = bb.min.z;

			if(Ext.isEmpty(max.x) || bb.max.x > max.x) max.x = bb.max.x;
			if(Ext.isEmpty(max.y) || bb.max.y > max.y) max.y = bb.max.y;
			if(Ext.isEmpty(max.z) || bb.max.z > max.z) max.z = bb.max.z;
		}

		var offset = new THREE.Vector3();
		offset.addVectors( max, min );
		offset.multiplyScalar( -0.5 );
//		console.log(offset);

//		self._dump(offset.distanceTo(self._group.position));

//		self._group.position.copy(offset);
//		self._group.translateZ(offset);

		for(var i=0;i<self._group.children.length;i++){
			var mesh = self._group.children[i];
			mesh.geometry.applyMatrix( new THREE.Matrix4().makeTranslation( offset.x, offset.y, offset.z ) );
			mesh.geometry.computeBoundingBox();
		}

		self.render();

	};

	self._objLoader = new THREE.OBJLoader();

	if(self._objLoader.addEventListener) self._objLoader.addEventListener('load',self._loadingManager.onLoad);

/*
	self._objLoader.addEventListener('load',function(event){
		var color = '#F0D2A0';
		if(color.substr(0,1) == '#') color = color.substr(1);
		color = Number('0x'+color);

		var mesh = event.content.children.shift();
		mesh.material.ambient.setHex( color );
		mesh.material.blending = THREE.AdditiveAlphaBlending;
		mesh.material.color.setHex( color );
		mesh.material.opacity = 1;
		mesh.material.transparent = false;
		mesh.material.wireframe = false;
		mesh.visible = true;
		mesh.doubleSided = true;


//		console.log(event);
//		console.log(mesh);




//		var center = THREE.GeometryUtils.center(mesh.geometry);
//		console.log(center);

		self._group.add( mesh );

		if(self._group.children.length<self._loadObjUrls.length) return;

//return;

		var max = new THREE.Vector3();
		var min = new THREE.Vector3();
		max.set(null,null,null);
		min.set(null,null,null);

		for(var i=0;i<self._group.children.length;i++){
			var mesh = self._group.children[i];
			mesh.geometry.computeBoundingBox();
			var bb = mesh.geometry.boundingBox;
			if(Ext.isEmpty(min.x) || bb.min.x < min.x) min.x = bb.min.x;
			if(Ext.isEmpty(min.y) || bb.min.y < min.y) min.y = bb.min.y;
			if(Ext.isEmpty(min.z) || bb.min.z < min.z) min.z = bb.min.z;

			if(Ext.isEmpty(max.x) || bb.max.x > max.x) max.x = bb.max.x;
			if(Ext.isEmpty(max.y) || bb.max.y > max.y) max.y = bb.max.y;
			if(Ext.isEmpty(max.z) || bb.max.z > max.z) max.z = bb.max.z;
		}

		var offset = new THREE.Vector3();
		offset.addVectors( max, min );
		offset.multiplyScalar( -0.5 );
//		console.log(offset);

//		self._dump(offset.distanceTo(self._group.position));

//		self._group.position.copy(offset);
//		self._group.translateZ(offset);

		for(var i=0;i<self._group.children.length;i++){
			var mesh = self._group.children[i];
			mesh.geometry.applyMatrix( new THREE.Matrix4().makeTranslation( offset.x, offset.y, offset.z ) );
			mesh.geometry.computeBoundingBox();
		}

		self.render();

	});
*/

//	self._objLoader.addEventListener('progress',function(event){
//		self._dump("progress():["+event.loaded+"]["+event.total+"]");
//	});

//	self.animate();
		self.render();
};

AgSubRenderer.prototype = {
//	get domElement(){
//		return this.$_domElement.get(0);
//	},

	animate : function(){
		var self = this;

		requestAnimationFrame( Ext.bind(self.animate,self) );
		self.render();
	},

	render : function(){
		var self = this;

//		self._camera.lookAt( self._target );

//		//ライトの位置もカメラの座標に更新
//		self._directionalLight.position.copy(self._camera.position);
//		self._directionalLight.target.position.copy(self._target);

		self._renderer.render( self._scene, self._camera );

	},

	loadObj : function(urls){
		var self = this;
		self._loadObjUrls = urls;
		Ext.iterate(urls,function(url,i,a){
			if(self._objLoader.addEventListener){
				self._objLoader.load(url);
			}else{
				self._objLoader.load(url,self._loadingManager.onLoad);
			}
		},self);
	},

	agDeg2Rad : function(deg){
		return deg * Math.PI / 180;
	},

	agRad2Deg : function(rad){
		return rad * 180 / Math.PI;
	},

	addLongitude : function(d){
		var self = this;
		self._group.rotation.addSelf(new THREE.Vector3(0, 0, self.agDeg2Rad(-d)));
		self._group.rotation.z = agDeg2Rad(Math.round(self.agRad2Deg(self._group.rotation.z)));//誤差修正
		self.render();
		return self;
	},

	setLongitude : function(d){
		var self = this;
		if(self._group.rotation.setZ){
			self._group.rotation.setZ(self.agDeg2Rad(-d));
		}else{
			self._group.rotation.z = self.agDeg2Rad(-d);
		}
		self.render();

//console.log(self.convertCoordinateScreenTo3D(new THREE.Vector2(0,0)));

		return self;
	},

	addLatitude : function(d){
		var self = this;
		self._group.rotation.addSelf(new THREE.Vector3(self.agDeg2Rad(d), 0, 0));
		self._group.rotation.x = agDeg2Rad(Math.round(self.agRad2Deg(self._group.rotation.x)));//誤差修正
		self.render();
		return self;
	},

	setLatitude : function(d){
		var self = this;
		if(self._group.rotation.setX){
			self._group.rotation.setX(self.agDeg2Rad(d));
		}else{
			self._group.rotation.x = self.agDeg2Rad(d);
		}
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
		if(window.dump) window.dump("AgSubRenderer.js:"+aStr+"\n");
		try{if(console && console.log) console.log("AgSubRenderer.js:"+aStr);}catch(e){}
	}

};
