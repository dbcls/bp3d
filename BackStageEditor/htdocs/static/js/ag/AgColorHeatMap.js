AgColorHeatMap = function ( camera ) {

	THREE.Object3D.call( this );

	var self = this;

	self.scalarMin = 0.0;		//スカラー値の最小値
	self.scalarMax = 100.0;	//スカラー値の最大値

	self.ratioRange = {
		min : new THREE.Vector2(0.90,-0.95),
		max : new THREE.Vector2(0.95, 0.95)
	};

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

	self.update();

//	THREE.SceneUtils.showHierarchy( self, false);
	self.traverse(function(obj){ obj.visible = false; });

};

AgColorHeatMap.prototype = Object.create( THREE.Object3D.prototype );


/**
 * スカラー値から色値を計算する。
 * 正規分布を利用
 */
AgColorHeatMap.prototype.calcColorValueByNormalDist = function( scalar ) { //float scalar,	//-1.0 - 1.0
	var val = 3.0*scalar;
	var colG = Math.exp( -val*val/4.0 );
	var colB = Math.exp( -(val + 2.1)*(val + 2.1)/4.0 );
	var colR = Math.exp( -(val - 2.1)*(val - 2.1)/4.0 );
	return (new THREE.Color()).setRGB(colR,colG,colB).getHex();
}

/**
 * スカラー値から色値を計算する。
 * 正規分布を利用
 */
AgColorHeatMap.prototype.calcColorValue = function( scalar ) {
	var self = this;
	if (scalar < self.scalarMin) {
		scalar = self.scalarMin;
	}else if (scalar > self.scalarMax) {
		scalar = self.scalarMax;
	}
	var zeroPos = (self.scalarMin + self.scalarMax)/2;
	var width = (self.scalarMax - self.scalarMin)/2;
	var val = (scalar - zeroPos) / width;
	return self.calcColorValueByNormalDist( val );
}


AgColorHeatMap.prototype.update = function(gridSpacing, gridColor) {
	var self = this;
//	var x = 1, y = 1, z = 1;

//self._dump("AgColorHeatMap.update():["+self.visible+"]");

	if(!self.visible) return;

	self.__c.projectionMatrix.copy( self._camera.projectionMatrix );

	self.__v.set( self.ratioRange.min.x, self.ratioRange.min.y, -1 );
//	self.__projector.unprojectVector( self.__v, self.__c );
	self.__v.unproject( self.__c );
	self._min.copy(self.__v);

	self.__v.set( self.ratioRange.max.x, self.ratioRange.max.y, 1 );
//	self.__projector.unprojectVector( self.__v, self.__c );
	self.__v.unproject( self.__c );
	self._max.copy(self.__v);

	self.__v.set( self.ratioRange.max.x, self.ratioRange.max.y, 0 );
//	self.__projector.unprojectVector( self.__v, self.__c );
	self.__v.unproject(  self.__c );
	self._center.copy(self.__v);

self._dump("update():x:["+self._min.x+"]["+self._max.x+"]");
self._dump("update():y:["+self._min.y+"]["+self._max.y+"]");
self._dump("update():z:["+self._min.z+"]["+self._max.z+"]");

	self._min.z = Math.round(Math.max(self._min.z,self._max.z) * 100)/100;
	self._min.z -= 0.9;

//	var c;
//	for(c = self.children.length-1;c>=0;c--){
//		self.remove(self.children[c]);
//	}

	var nCells	= 48;	//凡例のカラーセルの数
	var nCells_2 = nCells/2;

	var cellW = Math.abs(self._max.x-self._min.x); //カラーセルの幅
	var cellH = Math.abs(self._max.y-self._min.y); //カラーセルの高さ

self._dump("update():cell:["+cellW+"]["+cellH+"]["+(cellH/nCells)+"]");

	if(self.children.length==0){
		for (var y = -nCells_2; y < nCells_2; y++ ) {
			var color = self.calcColorValueByNormalDist(y/nCells_2);
//			var geometry = new THREE.PlaneGeometry(2,1);
			var geometry = new THREE.PlaneBufferGeometry(2,1);
			var material = new THREE.MeshLambertMaterial({color: color});
			var mesh = new THREE.Mesh(geometry,material);
			mesh.position.set(0,y,0);
			self.add(mesh);
		}
	}
	var scale = cellH/(nCells+3);
	self.scale.set(scale,scale,1);
//	self.position.set(min.x - (cellW*1.5),0,0);
	self.position.set(self._min.x,0,self._min.z);
//	self.position.set(0,0,0);

};

AgColorHeatMap.prototype.isVisibled = function(){
	var self = this;
	return self.visible;
};
AgColorHeatMap.prototype.setVisibled = function( visibled, Suspended ){
	var self = this;
//	self.visible = visibled;
//	THREE.SceneUtils.showHierarchy( self, visibled);
	self.traverse(function(obj){ obj.visible = visibled; });
	if(Suspended!==true) self.update();
};
AgColorHeatMap.prototype.setScalarMaximum = function( scalarMax, Suspended ){
	var self = this;
	self.scalarMax = scalarMax;
};
AgColorHeatMap.prototype.setScalarMinimum = function( scalarMin, Suspended ){
	var self = this;
	self.scalarMin = scalarMin;
};
AgColorHeatMap.prototype._dump = function(aStr){
//	if(window.dump) window.dump("AgColorHeatMap.js:"+aStr+"\n");
//	try{if(console && console.log) console.log("AgColorHeatMap.js:"+aStr);}catch(e){}
};
