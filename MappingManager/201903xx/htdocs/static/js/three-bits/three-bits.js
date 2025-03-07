THREE.Vector3.prototype.isZero = function ( v ) {
	return this.lengthSq() < ( v !== undefined ? v : 0.0001 );
};
THREE.Vector3.prototype.addSelf = function ( v ) {
	this.x += v.x;
	this.y += v.y;
	this.z += v.z;
	return this;
};
THREE.Vector3.prototype.subSelf = function ( v ) {
		this.x -= v.x;
		this.y -= v.y;
		this.z -= v.z;
	return this;
};
/*
	clone: function () {

		return new THREE.Vector3( this.x, this.y, this.z );

	}
*/
THREE.PinHelper = function( dir, origin, length, color, headLength, headWidth, headColor ) {
	THREE.Object3D.call( this );

	if ( color === undefined ) color = 0x0000ff;
	if ( length === undefined ) length = 1;
	if ( headLength === undefined ) headLength = 0.089 * length;
	if ( headWidth === undefined ) headWidth = 0.089 * length;
	if ( headColor === undefined ) headColor = 0xb3b3b3;

	var lineGeometry = new THREE.CylinderBufferGeometry( 3, 0.1, 1, 5, 1 );
	lineGeometry.translate( 0, 0.5, 0 );

	var coneGeometry = new THREE.SphereBufferGeometry( 0.5 );
	coneGeometry.translate( 0, - 0.5, 0 );

	this.length = length;
	this.headLength = headLength;
	this.headWidth = headWidth;

	this.position.copy( origin );

	this.line = new THREE.Mesh( lineGeometry, new THREE.MeshStandardMaterial( { color: headColor } ) );
	this.line.matrixAutoUpdate = false;
	this.add( this.line );

	this.cone = new THREE.Mesh( coneGeometry, new THREE.MeshStandardMaterial( { color: color } ) );
	this.cone.matrixAutoUpdate = false;
	this.add( this.cone );

	this.setDirection( dir );
	this.setLength( length, headLength, headWidth );
};

THREE.PinHelper.prototype = Object.create( THREE.Object3D.prototype );
THREE.PinHelper.prototype.constructor = THREE.PinHelper;
THREE.PinHelper.prototype.setDirection = ( function () {
	var axis = new THREE.Vector3();
	var radians;
	return function setDirection( dir ) {
		if ( dir.y > 0.99999 ) {
			this.quaternion.set( 0, 0, 0, 1 );
		} else if ( dir.y < - 0.99999 ) {
			this.quaternion.set( 1, 0, 0, 0 );
		} else {
			axis.set( dir.z, 0, - dir.x ).normalize();
			radians = Math.acos( dir.y );
			this.quaternion.setFromAxisAngle( axis, radians );
		}
	};
}() );

THREE.PinHelper.prototype.setLength = function ( length, headLength, headWidth, scale ) {
	if ( headLength === undefined ) headLength = 0.089 * length;
	if ( headWidth === undefined ) headWidth = 0.089 * length;
	if ( scale === undefined ) scale = 1;
	this.line.scale.set( scale, Math.max( 0, length - headLength ), scale );
	this.line.updateMatrix();
	this.cone.scale.set( headWidth, headLength, headWidth );
	this.cone.position.y = length;
	this.cone.updateMatrix();
};

THREE.PinHelper.prototype.setScale = function ( scale ) {
	if ( scale === undefined ) scale = 1;
	this.setLength( this.length * scale, this.headLength * scale, this.headWidth * scale, scale );
};

THREE.PinHelper.prototype.setColor = function ( color ) {
//	this.line.material.color.copy( color );
	this.cone.material.color.copy( color );
};


//Super-Small
//Small
//Midium
//Large
THREE.LargePinHelper = function(dir, origin, color){
	this.length = 112.5 * 2;
	this.headLength = 20 * 2;
	this.headWidth = 20 * 2;
	THREE.PinHelper.call( this, dir, origin, this.length, color, this.headLength, this.headWidth );
};

THREE.LargePinHelper.prototype = Object.assign( Object.create( THREE.PinHelper.prototype ), {
	constructor: THREE.PinHelper
});

THREE.MidiumPinHelper = function(dir, origin, color){
	this.length = 112.5;
	this.headLength = 20;
	this.headWidth = 20;
	THREE.PinHelper.call( this, dir, origin, this.length, color, this.headLength, this.headWidth );
};

THREE.MidiumPinHelper.prototype = Object.assign( Object.create( THREE.PinHelper.prototype ), {
	constructor: THREE.PinHelper
});

THREE.SmallPinHelper = function(dir, origin, color){
	this.length = 75;
	this.headLength = 20;
	this.headWidth = 20;
	THREE.PinHelper.call( this, dir, origin, this.length, color, this.headLength, this.headWidth );
};

THREE.SmallPinHelper.prototype = Object.assign( Object.create( THREE.PinHelper.prototype ), {
	constructor: THREE.PinHelper
});

THREE.SuperSmallPinHelper = function(dir, origin, color){
	this.length = 37.5;
	this.headLength = 20;
	this.headWidth = 20;
	THREE.PinHelper.call( this, dir, origin, this.length, color, this.headLength, this.headWidth );
};

THREE.SuperSmallPinHelper.prototype = Object.assign( Object.create( THREE.PinHelper.prototype ), {
	constructor: THREE.PinHelper
});


/*
//OpenGLレンダラーは、dir * -1 の値（座標系が違うので注意）
THREE.ConeHelper = function( dir, origin, up, length, color, headLength, headWidth ){
	THREE.Object3D.call( this );
	if ( color === undefined ) color = 0x0000ff;
//	var coneGeometry = new THREE.CylinderBufferGeometry( 0, 0.5, 1, 5, 1 );

	var coneHeight = 25;//height — Height of the cone. Default is 100.
	var coneRadius = coneHeight/2; //radius — Radius of the cone base. Default is 20.
	var coneRadiusSegments = 18;//radiusSegments — Number of segmented faces around the circumference of the cone. Default is 8
	var coneHeightSegments = 1;//heightSegments — Number of rows of faces along the height of the cone. Default is 1.
	var coneOpenEnded = false;//openEnded — A Boolean indicating whether the base of the cone is open or capped. Default is false, meaning capped.
	var coneThetaStart = 0;//thetaStart — Start angle for first segment, default = 0 (three o'clock position).
	var coneThetaLength = undefined;//thetaLength — The central angle, often called theta, of the circular sector. The default is 2*Pi, which makes for a complete cone.

	var coneGeometry = new THREE.ConeBufferGeometry( coneRadius, coneHeight, coneRadiusSegments, coneHeightSegments, coneOpenEnded, coneThetaStart, coneThetaLength );
	coneGeometry.translate( 0, -coneHeight/2, 0 );
//	var coneMaterial = new THREE.MeshBasicMaterial( { color: color } );
	var coneMaterial = new THREE.MeshPhongMaterial( {
		color: 0x156289,
		emissive: 0x072534,
		side: THREE.DoubleSide,
		shading: THREE.FlatShading
	});

	this.position.copy( origin );

	var sphereGeometry = new THREE.SphereBufferGeometry(coneRadius);//, coneHeight/2, coneHeight/2);
	sphereGeometry.translate( 0, -coneHeight, 0 );

	var sphereMaterial = new THREE.MeshPhongMaterial( {
		color: 0x156289,
//		emissive: 0x072534,
		opacity: 0.5,
		transparent: true,
		side: THREE.DoubleSide,
		shading: THREE.FlatShading
	});

	this.sphere = new THREE.Mesh( sphereGeometry, sphereMaterial );
	this.add( this.sphere );


	this.cone = new THREE.Mesh( coneGeometry, coneMaterial );
	this.cone.matrixAutoUpdate = false;
	this.add( this.cone );

	this.setDirection( dir, up );
	this.setLength( length, headLength, headWidth );

console.log(this);
};


THREE.ConeHelper.prototype = Object.create( THREE.Object3D.prototype );
THREE.ConeHelper.prototype.constructor = THREE.ConeHelper;
THREE.ConeHelper.prototype.setDirection = ( function () {
	var axis = new THREE.Vector3();
	var radians;
	return function setDirection( dir, up ) {
		if ( dir.y > 0.99999 ) {
			this.quaternion.set( 0, 0, 0, 1 );
		} else if ( dir.y < - 0.99999 ) {
			this.quaternion.set( 1, 0, 0, 0 );
		} else {
			if(up.z){
				axis.set( dir.z, 0, - dir.x ).normalize();
				radians = Math.acos( dir.y );
			}else if(up.y){
				axis.set( - dir.z, 0, dir.x ).normalize();
				radians = Math.acos( - dir.y );
			}
			this.quaternion.setFromAxisAngle( axis, radians );
		}
	};
}() );

THREE.ConeHelper.prototype.setLength = function ( length, headLength, headWidth ) {
		if ( headLength === undefined ) headLength = 0.2 * length;
		if ( headWidth === undefined ) headWidth = 0.2 * headLength;
//		this.line.scale.set( 1, Math.max( 0, length - headLength ), 1 );
//		this.line.updateMatrix();
//		this.cone.scale.set( headWidth, headLength, headWidth );
//		this.cone.position.y = length;
		this.cone.updateMatrix();
};

THREE.ConeHelper.prototype.setColor = function ( color ) {
//	this.line.material.color.copy( color );
	this.cone.material.color.copy( color );
};
*/
THREE.ConeHelper = function( dir, origin, color, length, headLength, headWidth, headColor ) {
	THREE.Object3D.call( this );

	if ( color === undefined ) color = 0x0000ff;
	if ( length === undefined ) length = 10;
	if ( headLength === undefined ) headLength = 0.5 * length;
	if ( headWidth === undefined ) headWidth = 0.5 * length;
	if ( headColor === undefined ) headColor = color;

	var lineGeometry = new THREE.CylinderBufferGeometry( 25, 0.1, 1, 72, 1 );
	lineGeometry.translate( 0, 0.5, 0 );

	var coneGeometry = new THREE.SphereBufferGeometry( 0.5 );
	coneGeometry.translate( 0, - 0.5, 0 );

	this.length = length;
	this.headLength = headLength;
	this.headWidth = headWidth;

	this.length = 20 * 4;
	this.headLength = 20 * 2;
	this.headWidth = 20 * 2;


	this.position.copy( origin );

	this.line = new THREE.Mesh( lineGeometry, new THREE.MeshLambertMaterial( { color: headColor } ) );
	this.line.matrixAutoUpdate = false;
	this.add( this.line );

	this.cone = new THREE.Mesh( coneGeometry, new THREE.MeshLambertMaterial( { color: color } ) );
	this.cone.matrixAutoUpdate = false;
	this.add( this.cone );

	this.setDirection( dir );
	this.setLength( length, headLength, headWidth );
};

THREE.ConeHelper.prototype = Object.create( THREE.Object3D.prototype );
THREE.ConeHelper.prototype.constructor = THREE.ConeHelper;
THREE.ConeHelper.prototype.setDirection = ( function () {
	var axis = new THREE.Vector3();
	var radians;
	return function setDirection( dir ) {
		if ( dir.y > 0.99999 ) {
			this.quaternion.set( 0, 0, 0, 1 );
		} else if ( dir.y < - 0.99999 ) {
			this.quaternion.set( 1, 0, 0, 0 );
		} else {
			axis.set( dir.z, 0, - dir.x ).normalize();
			radians = Math.acos( dir.y );
			this.quaternion.setFromAxisAngle( axis, radians );
		}
	};
}() );

THREE.ConeHelper.prototype.setLength = function ( length, headLength, headWidth, scale ) {
	if ( headLength === undefined ) headLength = 0.5 * length;
	if ( headWidth === undefined ) headWidth = 0.5 * length;
	if ( scale === undefined ) scale = 1;
	this.line.scale.set( scale, Math.max( 0, length - headLength ), scale );
	this.line.updateMatrix();
	this.cone.scale.set( headWidth, headLength, headWidth );
	this.cone.position.y = length;
	this.cone.updateMatrix();
};

THREE.ConeHelper.prototype.setScale = function ( scale ) {
	if ( scale === undefined ) scale = 1;
	this.setLength( this.length * scale, this.headLength * scale, this.headWidth * scale, scale );
};

THREE.ConeHelper.prototype.setColor = function ( color ) {
//	this.line.material.color.copy( color );
	this.cone.material.color.copy( color );
};
