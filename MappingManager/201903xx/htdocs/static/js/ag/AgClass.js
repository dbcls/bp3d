///////////////////////////////////////////////////////////////////////////////
window.AG = window.AG || {};
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
AG.BaseDef = function(){};
AG.BaseDef.prototype = Object.create({
	AG_X : 'x',		/** 座標 */
	AG_Y : 'y',
	AG_Z : 'z',
	AG_W : 3,		/** 同時座標のｗ */
	AG_WHW : 0,		/** 横幅 同次座標のWでないので注意 */
	AG_H : 1,
	AG_WH : 2,
	AG_U : 0,		/** テクスチャUV */
	AG_V : 1,
	AG_R : 0,		/** 色 */
	AG_G : 1,
	AG_B : 2,
	AG_A : 3,
	AG_RGB : 3,
	AG_RGBA : 4,
	AG_PI : Math.PI,
	AG_EPSILON : 0.0000001,

	AG3DATTRIB_REP : {
		AG3DATTRIB_REP_NONE      : 0,
		AG3DATTRIB_REP_WIREFRAME : 1,	//ワイヤーフレーム
		AG3DATTRIB_REP_POINTS    : 2,	//頂点描画
		AG3DATTRIB_REP_SURFACE   : 3,	//面描画
		AG3DATTRIB_REP_UNKNOWN   : 4
	}
});
AG.BaseDef.prototype.constructor = AG.BaseDef;
AG.BaseDef.prototype.AG_DEG2RAD = function(x){
	return ((x)*this.AG_PI/(180.0));
}
AG.BaseDef.prototype.AG_RAD2DEG = function(x){
	return ((x)*(180.0)/this.AG_PI);
}
AG.BaseDef.prototype.AG_ABS = function(x){
	return (((x) > 0) ? (x) : (-(x)));
}
AG.BaseDef.prototype.AG_IS_ZERO = function(x){
	return ((((x)<this.AG_EPSILON) && ((x)>(-this.AG_EPSILON))) ? 1 : 0);
}
AG.BaseDef.prototype.AG_IS_DIFFER = function(x,y){
	return ( ( ((x)-(y)<0) ? ((y)-(x)) : ((x)-(y)) ) > this.AG_EPSILON );
}
AG.BaseDef.prototype.AG_IS_EQUAL = function(x,y){
	return ( ( ((x)-(y)<0) ? ((y)-(x)) : ((x)-(y)) ) <= this.AG_EPSILON );
}
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
AG.MathUtil = function(){};
AG.MathUtil.prototype = Object.create(AG.BaseDef.prototype);
AG.MathUtil.prototype.constructor = AG.MathUtil;
/**
 * ベクトルをスカラー倍する
 */
AG.MathUtil.prototype.MultD3 = function(
	v0,		/** [i ] double[XYZ] の配列 */
	a )		/** [i ] スカラー倍 */
{
	v0[this.AG_X] = a*v0[this.AG_X];
	v0[this.AG_Y] = a*v0[this.AG_Y];
	v0[this.AG_Z] = a*v0[this.AG_Z];
}

/**
 * ベクトル反転設定
 */
AG.MathUtil.prototype.AGFlipD3 = function(
	v0 )	/** [i ] double[XYZ] の配列 */
{
	v0[this.AG_X] = -v0[this.AG_X];
	v0[this.AG_Y] = -v0[this.AG_Y];
	v0[this.AG_Z] = -v0[this.AG_Z];
}

/**
 * コピー OUT = v0
 */
AG.MathUtil.prototype.AGCopyD3 = function(
	v0,		/** [i ] double[XYZ] の配列 */
	out )	/** [ o] double[XYZ] の配列 */
{
	out[this.AG_X] = v0[this.AG_X];
	out[this.AG_Y] = v0[this.AG_Y];
	out[this.AG_Z] = v0[this.AG_Z];
}

/**
 * 和 V0+V1
 */
AG.MathUtil.prototype.AGSumD3 = function(
	v0,		/** [i ] double[XYZ] の配列 */
	v1,		/** [i ] double[XYZ] の配列 */
	out )	/** [ o] double[XYZ] の配列 */
{
	out[this.AG_X] = v0[this.AG_X] + v1[this.AG_X];
	out[this.AG_Y] = v0[this.AG_Y] + v1[this.AG_Y];
	out[this.AG_Z] = v0[this.AG_Z] + v1[this.AG_Z];
}

/**
 * 差 V0-V1
 */
AG.MathUtil.prototype.AGDifferenceD3 = function(
	v0,		/** [i ] double[XYZ] の配列 */
	v1,		/** [i ] double[XYZ] の配列 */
	out )	/** [i ] double[XYZ] の配列 */
{
	out[this.AG_X] = v0[this.AG_X] - v1[this.AG_X];
	out[this.AG_Y] = v0[this.AG_Y] - v1[this.AG_Y];
	out[this.AG_Z] = v0[this.AG_Z] - v1[this.AG_Z];
}

/**
 * 中点 (V0+V1)/2
 */
AG.MathUtil.prototype.AGMiddleD3 = function(
	v0,		/** [i ] double[XYZ] の配列 */
	v1,		/** [i ] double[XYZ] の配列 */
	out )	/** [i ] double[XYZ] の配列 */
{
	out[this.AG_X] = (v0[this.AG_X] + v1[this.AG_X])/2.;
	out[this.AG_Y] = (v0[this.AG_Y] + v1[this.AG_Y])/2.;
	out[this.AG_Z] = (v0[this.AG_Z] + v1[this.AG_Z])/2.;
}

/**
 * 和 V0 + k(nrm)
 */
AG.MathUtil.prototype.AGMoveD3 = function(
	v0,		/** [i ] double[XYZ] の配列 */
	nrm,	/** [i ] double[XYZ] の法線ベクトル */
	k,		/** [i ] doubleの係数 */
	out )	/** [ o] double[XYZ] の配列 */
{
	out[this.AG_X] = v0[this.AG_X] + (k * nrm[this.AG_X]);
	out[this.AG_Y] = v0[this.AG_Y] + (k * nrm[this.AG_Y]);
	out[this.AG_Z] = v0[this.AG_Z] + (k * nrm[this.AG_Z]);
}

/**
 * 内積計算 V0・V1
 */
AG.MathUtil.prototype.AGInnerProductD3 = function(
	v0,		/** [i ] double[XYZ] の配列 */
	v1 )	/** [i ] double[XYZ] の配列 */
{
	return v0[this.AG_X]*v1[this.AG_X] + v0[this.AG_Y]*v1[this.AG_Y] + v0[this.AG_Z]*v1[this.AG_Z];
}

/**
 * 外積計算 V0×V1
 */
AG.MathUtil.prototype.AGOuterProductD3 = function(
	v0,		/** [i ] double[XYZ] の配列 */
	v1,		/** [i ] double[XYZ] の配列 */
	out )	/** [ o] double[XYZ] の配列 */
{
	out[this.AG_X] = v0[this.AG_Y]*v1[this.AG_Z] - v1[this.AG_Y]*v0[this.AG_Z];
	out[this.AG_Y] = v0[this.AG_Z]*v1[this.AG_X] - v1[this.AG_Z]*v0[this.AG_X];
	out[this.AG_Z] = v0[this.AG_X]*v1[this.AG_Y] - v1[this.AG_X]*v0[this.AG_Y];
}

/**
 * 法線化 V0 -> nV0
 */
AG.MathUtil.prototype.AGNormalizeD3 = function(
	v0,		/** [i ] double[XYZ] の配列 */
	out )	/** [ o] double[XYZ] の配列 */
{
	var len;
	len = v0[this.AG_X]*v0[this.AG_X] + v0[this.AG_Y]*v0[this.AG_Y] + v0[this.AG_Z]*v0[this.AG_Z];
	len = Math.sqrt( len );
	if( 0 == len ){
		return false;
	}
	out[this.AG_X] = v0[this.AG_X] / len;
	out[this.AG_Y] = v0[this.AG_Y] / len;
	out[this.AG_Z] = v0[this.AG_Z] / len;
	return	true;
}

/**
 * nrm 軸の周りに angle 角度回転させる
 * nrm の進む方向で右ねじの方向が正
 */
AG.MathUtil.prototype.AGRotationAroundNorm= function(
	nrm,	/** [i ] 回転軸 */
	degree,	/** [i ] 回転角度 [deg.] */
	org,	/** [i ] オリジナルの頂点 */
	calc )	/** [ o] 計算された頂点 */
{
	var rad  = -degree * this.AG_PI/180.0;	// 右ねじの方向を正にするために変更
	var sina = Math.sin( rad );
	var cosa = Math.cos( rad );

	var in_org_nrm = this.AGInnerProductD3( org, nrm );
	var in_org_nrm_Nrm = new THREE.Vector3();
	in_org_nrm_Nrm[this.AG_X] = in_org_nrm * nrm[this.AG_X];
	in_org_nrm_Nrm[this.AG_Y] = in_org_nrm * nrm[this.AG_Y];
	in_org_nrm_Nrm[this.AG_Z] = in_org_nrm * nrm[this.AG_Z];
	org_in_org_nrm_Nrm = new THREE.Vector3();
	org_in_org_nrm_Nrm[this.AG_X] = org[this.AG_X] - in_org_nrm_Nrm[this.AG_X];
	org_in_org_nrm_Nrm[this.AG_Y] = org[this.AG_Y] - in_org_nrm_Nrm[this.AG_Y];
	org_in_org_nrm_Nrm[this.AG_Z] = org[this.AG_Z] - in_org_nrm_Nrm[this.AG_Z];
	var out_org_in_org_nrm_Nrm_Nrm = new THREE.Vector3();
	this.AGOuterProductD3( org_in_org_nrm_Nrm, nrm, out_org_in_org_nrm_Nrm_Nrm );

	calc[this.AG_X] = cosa*org[this.AG_X] + (1-cosa)*in_org_nrm_Nrm[this.AG_X] + sina*out_org_in_org_nrm_Nrm_Nrm[this.AG_X];
	calc[this.AG_Y] = cosa*org[this.AG_Y] + (1-cosa)*in_org_nrm_Nrm[this.AG_Y] + sina*out_org_in_org_nrm_Nrm_Nrm[this.AG_Y];
	calc[this.AG_Z] = cosa*org[this.AG_Z] + (1-cosa)*in_org_nrm_Nrm[this.AG_Z] + sina*out_org_in_org_nrm_Nrm_Nrm[this.AG_Z];
}
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
AG.CAg3DData = function(){
	this.m_filePath = "";
	this.m_id = "";

	this.m_pVertices = null;
	this.m_numVertices = 0;
	this.m_pNormals = null;
	this.m_numNormals = 0;
	this.m_pIndices = null;
	this.m_numIndices = 0;

	this.m_box3 = new THREE.Box3(new THREE.Vector3(0.0,0.0,0.0),new THREE.Vector3(0.0,0.0,0.0));

	this.m_isDrawable = true;
	this.m_isSelectable = true;
}
AG.CAg3DData.prototype = Object.create(AG.MathUtil.prototype);
AG.CAg3DData.prototype.constructor = AG.CAg3DData;

AG.CAg3DData.prototype.createData = function(numVerts,numNorms,numIndices){
	var self = this;
	self.clearData();
	if (numVerts != numNorms) {
		console.error( "[CAg3DData::createData()] Error!: numVerts and numNorms must be same!" );
		return false;
	}
	var i;
	self.m_pVertices = new Array(numVerts);
	self.m_numVertices = numVerts;
	for(i=0;i<numVerts;i++){
		self.m_pVertices[i] = new THREE.Vector3();
	}
	self.m_pNormals = new Array(numNorms);
	self.m_numNormals = numNorms;
	for(i=0;i<numNorms;i++){
		self.m_pNormals[i] = new THREE.Vector3();
	}
	self.m_pIndices = new Array(numIndices);
	self.m_numIndices = numIndices;
	for(i=0;i<numIndices;i++){
		self.m_pIndices[i] = new THREE.Vector3();
	}

	return true;
}

AG.CAg3DData.prototype.clearData = function(){
	var self = this;
	if(self.m_pVertices){
		delete self.m_pVertices;
		self.m_pVertices = null;
		self.m_numVertices = 0;
	}
	if(self.m_pNormals){
		delete self.m_pNormals;
		self.m_pNormals = null;
		self.m_numNormals = 0;
	}
	if(self.m_pIndices){
		delete self.m_pIndices;
		self.m_pIndices = null;
		self.m_numIndices = 0;
	}	
}

AG.CAg3DData.prototype.setVerticesBBMinMax = function(minX,maxX,minY,maxY,minZ,maxZ){
	this.m_box3.set(new THREE.Vector3(minX,minY,minZ),new THREE.Vector3(maxX,maxY,maxZ));
	return true;
}

AG.CAg3DData.prototype.getVerticesBBMinMax = function(){
	return this.m_box3.clone();
}
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
AG.CAg3DCone = function(id){
	this.m_pointPos = new THREE.Vector3(0.0,0.0,0.0);
	this.m_arrowVec = new THREE.Vector3(0.0,0.0,0.0);
	this.m_upVec = new THREE.Vector3(0.0,1.0,0.0);
	this.m_coneRatio = 0.5;		//底面の円の半径のarrowの長さに対する比率
	this.m_coneNumVerts = 10;		//底面の円の頂点数

	this.m_isDrawable = true;
	this.m_isSelectable = false; //セレクト対象にはならない！

	//属性
	this.m_attrib = {};
	if (id) {
		this.m_attrib.m_id = id;
	}
	else {
		this.m_attrib.m_id = "";
	}
	this.m_attrib.m_rgb = new THREE.Color().setRGB(0.3,0.3,0.6);
	this.m_attrib.m_opacity = 1.0;
//	this.m_attrib.m_representation = this.AG3DATTRIB_REP.AG3DATTRIB_REP_SURFACE;
}
AG.CAg3DCone.prototype = Object.create(AG.CAg3DData.prototype);
AG.CAg3DCone.prototype.constructor = AG.CAg3DCone;

AG.CAg3DCone.prototype.createData = function(point,arrow,upVec,ratio,numVerts){
	var self = this;

	if(self.m_attrib.m_representation==undefined) self.m_attrib.m_representation = self.AG3DATTRIB_REP.AG3DATTRIB_REP_SURFACE;

	self.clearData();

	self.m_pointPos.copy(point);
	self.m_arrowVec.copy(arrow);
	self.m_upVec.copy(upVec);
	self.m_coneRatio = ratio;		//底面の円の半径のarrowの長さに対する比率
	self.m_coneNumVerts = numVerts;		//底面の円の頂点数

	var lenArrow = arrow.length();
	var lenR = lenArrow*ratio;

	var tmpVec = new THREE.Vector3().crossVectors(arrow, upVec);
	var up0Vec = new THREE.Vector3().crossVectors(arrow, tmpVec);
	up0Vec.normalize().multiplyScalar(lenR);

	//upベクトルがつぶれた場合
	if(up0Vec.x == 0 && up0Vec.y == 0 && up0Vec.z == 0){
		return undefined;
	}

	var narrowVec = arrow.clone().normalize();


	var cenPos = new THREE.Vector3().subVectors(point, arrow);

	var i;
	var basePos = new Array(numVerts);
	for(i=0;i<numVerts;i++){
		basePos[i] = new THREE.Vector3();
	}
	var baseVec = new Array(numVerts);
	for(i=0;i<numVerts;i++){
		baseVec[i] = new THREE.Vector3();
	}

	for(i=0;i<numVerts;i++) {
		if(basePos[i]==undefined) basePos[i] = new THREE.Vector3();
		self.AGRotationAroundNorm(
			narrowVec,			/** [i ] 回転軸 */
			i*360.0/numVerts,	/** [i ] 回転角度 [deg.] */
			up0Vec,				/** [i ] オリジナルの頂点 */
			tmpVec );			/** [ o] 計算された頂点 */
		self.AGSumD3(cenPos,tmpVec,basePos[i]);
	}

	//頂点の作成
	AG.CAg3DData.prototype.createData.call(this,
			numVerts + 2, //底面の頂点数 + 底面の中心 + 円錐の先
			numVerts + 2, //
			numVerts*2*3 //(底面の三角形数 + 円錐面の三角形数)*3
	);

	//円錐の先
	(self.m_pVertices[0])[this.AG_X] = point[this.AG_X];
	(self.m_pVertices[0])[this.AG_Y] = point[this.AG_Y];
	(self.m_pVertices[0])[this.AG_Z] = point[this.AG_Z];
	(self.m_pNormals[0])[this.AG_X] = narrowVec[this.AG_X];
	(self.m_pNormals[0])[this.AG_Y] = narrowVec[this.AG_Y];
	(self.m_pNormals[0])[this.AG_Z] = narrowVec[this.AG_Z];
	//底面の中心
	(self.m_pVertices[1])[this.AG_X] = cenPos[this.AG_X];
	(self.m_pVertices[1])[this.AG_Y] = cenPos[this.AG_Y];
	(self.m_pVertices[1])[this.AG_Z] = cenPos[this.AG_Z];
	self.AGFlipD3( narrowVec );
	(self.m_pNormals[1])[this.AG_X] = narrowVec[this.AG_X];
	(self.m_pNormals[1])[this.AG_Y] = narrowVec[this.AG_Y];
	(self.m_pNormals[1])[this.AG_Z] = narrowVec[this.AG_Z];
	for(i=2;i<self.m_numVertices;i++){
		(self.m_pVertices[i])[this.AG_X] = (basePos[i - 2])[this.AG_X];
		(self.m_pVertices[i])[this.AG_Y] = (basePos[i - 2])[this.AG_Y];
		(self.m_pVertices[i])[this.AG_Z] = (basePos[i - 2])[this.AG_Z];
		self.AGNormalizeD3( baseVec[i - 2], baseVec[i - 2] );
		(self.m_pNormals[i])[this.AG_X] = (baseVec[i - 2])[this.AG_X];
		(self.m_pNormals[i])[this.AG_Y] = (baseVec[i - 2])[this.AG_Y];
		(self.m_pNormals[i])[this.AG_Z] = (baseVec[i - 2])[this.AG_Z];
	}

	var idx = 0;
	for(i=0;i<numVerts-1;i++){
		self.m_pIndices[idx + 0] = 0;
		self.m_pIndices[idx + 1] = 2 + i;
		self.m_pIndices[idx + 2] = 3 + i;
		idx += 3;
	}
	self.m_pIndices[idx + 0] = 0;
	self.m_pIndices[idx + 1] = numVerts + 1;
	self.m_pIndices[idx + 2] = 2;
	idx += 3;
	for(i=0;i<numVerts-1;i++){
		self.m_pIndices[idx + 0] = 1;
		self.m_pIndices[idx + 1] = 2 + i;
		self.m_pIndices[idx + 2] = 3 + i;
		idx += 3;
	}
	self.m_pIndices[idx + 0] = 1;
	self.m_pIndices[idx + 1] = numVerts + 1;
	self.m_pIndices[idx + 2] = 2;

	return self;
}
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
function AGVec3d (x, y, z) {}
AGVec3d.prototype = Object.create(THREE.Vector3.prototype);
AGVec3d.prototype.constructor = AGVec3d;
