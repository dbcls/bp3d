AgGrid = function ( camera ) {

	THREE.Object3D.call( this );

	var self = this;

//	self.__projector = new THREE.Projector();
	self.__v = new THREE.Vector3();
	self.__c = new THREE.Camera();

	self._min = new THREE.Vector3();
	self._max = new THREE.Vector3();
	self._center = new THREE.Vector3();

	self._camera = camera;

//		self.matrixWorld = self._camera.matrixWorld;
//		self.matrixAutoUpdate = false;

	self._camera.add( self );

	var color = 0x00ff00;

	var size = 13000, step = 10;

	var geometry =  new THREE.Geometry();

	for(var i = -size; i <= size; i += step){
		geometry.vertices.push( new THREE.Vector3(-size, i, 0) );
		geometry.vertices.push( new THREE.Vector3( size, i, 0) );

		geometry.vertices.push( new THREE.Vector3( i, -size, 0) );
		geometry.vertices.push( new THREE.Vector3( i,  size, 0) );
	}

	self._material = new THREE.LineBasicMaterial({color: color, opacity: 0.5});
//	var mesh = new THREE.Line(geometry,self._material,THREE.LinePieces);
	var mesh = new THREE.Line(geometry,self._material,THREE.LineSegments);
//	mesh.scale.set(0.1,0.1,0.1);
//	mesh.scale.set(0.5,0.5,0.5);
//	mesh.scale.set(5,5,5);
	self.add(mesh);

	self.update();

//	THREE.SceneUtils.showHierarchy( self, false);
	self.traverse(function(obj){ obj.visible = false; });

	self.position.set(0,0,-1);

};

AgGrid.prototype = Object.create( THREE.Object3D.prototype );

AgGrid.prototype.update = function(gridSpacing, gridColor) {
	var self = this;
//	return;
//	var x = 1, y = 1, z = 1;

//self._dump("AgGrid.update():["+self.visible+"]");

	if(!self.visible) return;

//	self.matrixAutoUpdate = true;
//	self.updateMatrixWorld(true);
//	self.matrixAutoUpdate = false;

	self.__c.projectionMatrix.copy( self._camera.projectionMatrix );

	self.__v.set( -1, -1, -1 );
//	self.__projector.unprojectVector( self.__v, self.__c );
	self.__v.unproject( self.__c );
	self._min.copy(self.__v);

	self.__v.set( 1, 1, 1 );
//	self.__projector.unprojectVector( self.__v, self.__c );
	self.__v.unproject( self.__c );
	self._max.copy(self.__v);

	self.__v.set( 0, 0, 0 );
//	self.__projector.unprojectVector( self.__v, self.__c );
	self.__v.unproject( self.__c );
	self._center.copy(self.__v);

self._dump("update():x:["+self._min.x+"]["+self._max.x+"]");
self._dump("update():y:["+self._min.y+"]["+self._max.y+"]");
self._dump("update():z:["+self._min.z+"]["+self._max.z+"]");

	self._min.z = Math.round(Math.max(self._min.z,self._max.z) * 100)/100;
	self._min.z -= 1;

	self.position.set(0,0,self._min.z);

};

AgGrid.prototype.isVisibled = function(){
	var self = this;
	return self.visible;
};
AgGrid.prototype.setVisibled = function( visibled, Suspended ){
	var self = this;
//	THREE.SceneUtils.showHierarchy( self, visibled);
	self.traverse(function(obj){ obj.visible = visibled; });
};
AgGrid.prototype.setGridSpacing = function( gridSpacing, Suspended ){
	var self = this;
	var scale = gridSpacing/10;
	self.children[0].scale.set(scale,scale,scale);
};
AgGrid.prototype.setGridColor = function( gridColor, Suspended ){
	var self = this;
	self._material.color.setHex(gridColor);
};


AgGrid.prototype._dump = function(aStr){
//	if(window.dump) window.dump("AgGrid.js:"+aStr+"\n");
//	try{if(console && console.log) console.log("AgGrid.js:"+aStr);}catch(e){}
};
