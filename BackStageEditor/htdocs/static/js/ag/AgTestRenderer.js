function AgTestRenderer(){
	var self = this;

	var rate = 3/2;
	var rate = 2;

	self._loadObjUrls = [];

	self.SCREEN_HEIGHT = 250;
	self.SCREEN_WIDTH = self.SCREEN_HEIGHT / rate;
//	self.SCREEN_HEIGHT = 60;

	self.$_domElement = $('<div style="width:'+(self.SCREEN_WIDTH+4)+'px;height:'+(self.SCREEN_HEIGHT+4)+'px;background-color:#f0f0f0;border:2px solid #dddddd;">');
	self.domElement = self.$_domElement.get(0);

	self.$_domElement.click(function(){
		return false;
	});

	//カメラ位置角度
	self._cameraPos3 = new THREE.Vector3();
	//カメラ移動先の位置角度
	self._cameraTarget3 = new THREE.Vector3();
	//カメラ距離
	self._distance = 10000;


	self._target = new THREE.Vector3(0,0,0);

//	self._camera = new THREE.OrthographicCamera((1800 / rate)/-2, (1800 / rate)/2, 1800/2, 1800/-2, 0.1, self._distance );


//THREE.PerspectiveCamera = function ( fov, aspect, near, far ) {
//	this.fov = fov !== undefined ? fov : 50;
//	this.aspect = aspect !== undefined ? aspect : 1;
//	this.near = near !== undefined ? near : 0.1;
//	this.far = far !== undefined ? far : 2000;

//THREE.OrthographicCamera = function ( left, right, top, bottom, near, far ) {
//	this.near = ( near !== undefined ) ? near : 0.1;
//	this.far = ( far !== undefined ) ? far : 2000;

//THREE.CombinedCamera = function ( width, height, fov, near, far, orthoNear, orthoFar ) {

	self._camera = new THREE.CombinedCamera(1800,1800,30,1,self._distance,0.1,self._distance);
	self._camera.toOrthographic();

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

	self._group = new THREE.Object3D();
	self._scene.add(self._group);

	if(!Detector.webgl) Detector.addGetWebGLMessage();

	if(Detector.webgl){
		self._renderer = new THREE.WebGLRenderer({antialias:true,maxLights:6});
	}else{
		self._renderer = new THREE.CanvasRenderer({antialias:true,maxLights:6});
	}
	self._renderer.setSize( self.SCREEN_WIDTH, self.SCREEN_HEIGHT );

	self._renderer.domElement.style.position = "relative";
	self.domElement.appendChild( self._renderer.domElement );

	self._trackball = new THREE.TrackballControls( self._camera, self._renderer.domElement );

	self._objLoader = new THREE.OBJLoader();
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
		offset.add( max, min );
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
//	self._objLoader.addEventListener('progress',function(event){
//		self._dump("progress():["+event.loaded+"]["+event.total+"]");
//	});

	self.animate();
//		self.render();
};

AgTestRenderer.prototype = {
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


//		self._cameraPos3.x += (self._cameraTarget3.x - self._cameraPos3.x) * 0.2;
//		self._cameraPos3.y += (self._cameraTarget3.y - self._cameraPos3.y) * 0.2;
//		self._cameraPos3.z += (self._cameraTarget3.z - self._cameraPos3.z) * 0.2;

//		self._camera.position.x = self._distance * Math.sin( self._cameraPos3.x * Math.PI / 180 );
//		self._camera.position.y = self._distance * Math.tan( self._cameraPos3.y * Math.PI / 180 );
//		self._camera.position.z = self._distance * Math.cos( self._cameraPos3.z * Math.PI / 180 );


		self._trackball.update();
		self._renderer.render( self._scene, self._camera );

	},

	loadObj : function(urls){
		var self = this;
		self._loadObjUrls = urls;
		Ext.iterate(urls,function(url,i,a){
			self._objLoader.load(url);
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
		self._camera.rotation.addSelf(new THREE.Vector3(0, 0, self.agDeg2Rad(-d)));
		self._camera.rotation.z = agDeg2Rad(Math.round(self.agRad2Deg(self._camera.rotation.z)));//誤差修正
//		self.render();
		return self;
	},

	setLongitude : function(d){
		var self = this;
//		self._camera.position.setZ(self.agDeg2Rad(-d));

//		self._cameraTarget3.x -= d;
//		self._cameraTarget3.y -= d;
 
//		self.render();
		return self;
	},

	addLatitude : function(d){
		var self = this;
		self._camera.rotation.addSelf(new THREE.Vector3(self.agDeg2Rad(d), 0, 0));
		self._camera.rotation.x = agDeg2Rad(Math.round(self.agRad2Deg(self._camera.rotation.x)));//誤差修正
//		self.render();
		return self;
	},

	setLatitude : function(d){
		var self = this;
//		self._camera.position.setX(self.agDeg2Rad(d));

//		self._cameraTarget3.z += d;
//		self._cameraTarget3.y -= d;

//		self.render();
		return self;
	},

	_dump : function(aStr){
		if(window.dump) window.dump("AgTestRenderer.js:"+aStr+"\n");
		try{if(console && console.log) console.log("AgTestRenderer.js:"+aStr);}catch(e){}
	}

};
