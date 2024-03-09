/**
 * Parameters:
 *  dir - Vector3
 *  position - Vector3
 *  hex - color in hex value
 */

AgPin = function ( dir, position, hex, lineHex ) {

	THREE.Object3D.call( this );
	var self = this;

	if ( hex === undefined ) hex = 0x0000ff;
	if ( lineHex === undefined ) lineHex = 0x808080;
	if ( length === undefined ) length = 20;

	self._scale = 1;
	self._type = null;

	var segmentsWidth = 50;
	var segmentsHeight = 50;
	var segmentsRadius = 50;
	var linewidth = 4;

	self._line_material = new THREE.LineBasicMaterial( { color: lineHex, linewidth: linewidth } );
	self._mesh_material = new THREE.MeshLambertMaterial({
		color: hex,
//		ambient: hex,
//		shading: THREE.SmoothShading
	});

	var geometry;

	geometry = new THREE.Geometry();
	geometry.vertices.push( new THREE.Vector3( 0, 0, 0 ) );
	geometry.vertices.push( new THREE.Vector3( 0, AgPin.LENGTH_S, 0 ) );
	self.lineS = new THREE.Line( geometry, self._line_material );
	self.lineS.visible = false;
	self.add( self.lineS );

	geometry = new THREE.SphereGeometry(AgPin.RADIUS_S, segmentsWidth, segmentsHeight);
	self.sphereS = new THREE.Mesh( geometry, self._mesh_material );
	self.sphereS.position.set( 0, AgPin.LENGTH_S-AgPin.RADIUS_S, 0 );
	self.sphereS.visible = false;
	self.add( self.sphereS );


	geometry = new THREE.Geometry();
	geometry.vertices.push( new THREE.Vector3( 0, 0, 0 ) );
	geometry.vertices.push( new THREE.Vector3( 0, AgPin.LENGTH_M, 0 ) );
	self.lineM = new THREE.Line( geometry, self._line_material );
	self.lineM.visible = false;
	self.add( self.lineM );

	geometry = new THREE.SphereGeometry(AgPin.RADIUS_M, segmentsWidth, segmentsHeight);
	self.sphereM = new THREE.Mesh( geometry, self._mesh_material );
	self.sphereM.position.set( 0, AgPin.LENGTH_M-AgPin.RADIUS_M, 0 );
	self.sphereM.visible = false;
	self.add( self.sphereM );


	geometry = new THREE.Geometry();
	geometry.vertices.push( new THREE.Vector3( 0, 0, 0 ) );
	geometry.vertices.push( new THREE.Vector3( 0, AgPin.LENGTH_L, 0 ) );
	self.lineL = new THREE.Line( geometry, self._line_material );
	self.lineL.visible = false;
	self.add( self.lineL );

	geometry = new THREE.SphereGeometry(AgPin.RADIUS_L, segmentsWidth, segmentsHeight);
	self.sphereL = new THREE.Mesh( geometry, self._mesh_material );
	self.sphereL.position.set( 0, AgPin.LENGTH_L-AgPin.RADIUS_L, 0 );
	self.sphereL.visible = false;
	self.add( self.sphereL );


	geometry = new THREE.CylinderGeometry( AgPin.RADIUS_C, 0, AgPin.LENGTH_C, segmentsRadius, segmentsHeight );
	self.cone = new THREE.Mesh( geometry, self._mesh_material );
	self.cone.position.set( 0, AgPin.LENGTH_C/2, 0 );
	self.cone.visible = false;
	self.add( self.cone );

	if ( position instanceof THREE.Vector3 ) self.position = position;

	self.setDirection( dir );
};

AgPin.prototype = Object.create( THREE.Object3D.prototype );

AgPin.prototype.setDirection = function ( dir ) {
	var self = this;
	var axis = new THREE.Vector3( 0, 1, 0 ).cross( dir );
	var radians = Math.acos( new THREE.Vector3( 0, 1, 0 ).dot( dir.clone().normalize() ) );
	self.matrix = new THREE.Matrix4().makeRotationAxis( axis.normalize(), radians );
	self.rotation.setFromRotationMatrix( self.matrix, self.rotation.order );
};

AgPin.prototype.setColor = function ( hex, lineHex ) {
	var self = this;

	if(lineHex === undefined) lineHex = hex;

	self._line_material.color.setHex( lineHex );
	self._mesh_material.color.setHex( hex );
	self._mesh_material.ambient.setHex( hex );
};

AgPin.prototype.setScale = function ( scale ) {
	var self = this;
	if(Math.abs(self._scale-scale)<0.0001) return;
	self.scale.set( scale, scale, scale );
	self._scale=scale;


};

AgPin.prototype.setVisibled = function( type ){
	var self = this;

	if(type) type = type.toUpperCase();

//	if(self._type===type) return;
	self._type = type;

	self.lineS.visible = false;
	self.sphereS.visible = false;
	self.lineM.visible = false;
	self.sphereM.visible = false;
	self.lineL.visible = false;
	self.sphereL.visible = false;
	self.cone.visible = false;

	if(type == 'CONE'){
		self.cone.visible = true;
	}else if(type == 'PIN_SHORT'){
		self.lineS.visible = true;
		self.sphereS.visible = true;
	}else if(type == 'PIN_MIDIUM'){
		self.lineM.visible = true;
		self.sphereM.visible = true;
	}else if(type == 'PIN_LONG'){
		self.lineL.visible = true;
		self.sphereL.visible = true;
	}
};

AgPin.prototype.getEndPosition = function( vec3 ){
	var self = this;

	var lineRate = 1;
	if(self._type == 'CONE'){
		lineRate = AgPin.LENGTH_C;
	}else if(self._type == 'PIN_SHORT'){
		lineRate = AgPin.LENGTH_S;
	}else if(self._type == 'PIN_MIDIUM'){
		lineRate = AgPin.LENGTH_M;
	}else if(self._type == 'PIN_LONG'){
		lineRate = AgPin.LENGTH_L;
	}

	var tmpVec = new THREE.Vector3();
	var endVec = new THREE.Vector3();
	tmpVec.copy(vec3).multiplyScalar(lineRate*self._scale);
	endVec.add( self.position, self.matrixRotationWorld.multiplyVector3( tmpVec ) );

	return endVec;
};

AgPin.RADIUS_C = AgPin.RADIUS_S = AgPin.RADIUS_M = AgPin.RADIUS_L = 10;
AgPin.LENGTH_C = AgPin.LENGTH_S = 40;

AgPin.RADIUS_C = 40;
AgPin.LENGTH_C = 80;

AgPin.RADIUS_S = 20;
AgPin.LENGTH_S = 100;

AgPin.RADIUS_M = 40;
AgPin.LENGTH_M = 300;

AgPin.RADIUS_L = 60;
AgPin.LENGTH_L = 500;
