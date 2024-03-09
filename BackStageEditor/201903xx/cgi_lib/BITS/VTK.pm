package BITS::VTK;

#use strict;
#use warnings;
#use feature ':5.10';

#use parent 'Exporter';

#our @ISA = (Exporter);
#@EXPORT_OK = qw(extract find);
#@EXPORT_FAIL = qw(move_file);

use Inline Python;

1;

__DATA__
__Python__
#0
import vtk
import math

def vtkOBJReader(file):
	#.obj形式の読み込み
	object = vtk.vtkOBJReader()
	object.SetFileName(file)
	object.Update()
	return object;

def file2object(files):
	object = None
	if isinstance(files,list):
		object = vtk.vtkAppendPolyData()
		for file in files:
			if isinstance(file,basestring):
				o = vtkOBJReader(file)
				port = o.GetOutputPort()
				object.AddInputConnection(port)
				object.Update()
			elif isinstance(file,dict) and file.has_key('path') and isinstance(file['path'],basestring):
				object.AddInputConnection(vtkOBJReader(file['path']).GetOutputPort())
				object.Update()
	else:
		object = vtkOBJReader(files)
	return object

def getProperties(file):
	object = file2object(file);

	#polyData = vtk.vtkPolyData()
	#polyData.ShallowCopy(object.GetOutput())
	polyData = object.GetOutput()

	#入力ポリゴンと三角形ストリップから三角形のポリゴンを作成する
	triangleFilter = vtk.vtkTriangleFilter()
	triangleFilter.SetInputConnection(object.GetOutputPort())
	triangleFilter.Update()

	#重複しているものを削除
	cleanPolyData = vtk.vtkCleanPolyData()
	cleanPolyData.SetInputConnection(triangleFilter.GetOutputPort())

	#ラプラシアンスムージングを使用して点の座標を調整するフィルタ
	smoother = vtk.vtkSmoothPolyDataFilter()
#	smoother.SetInputConnection(object.GetOutputPort())
	smoother.SetInputConnection(cleanPolyData.GetOutputPort())
	smoother.FeatureEdgeSmoothingOn()
	smoother.Update()

	#ポリゴンメッシュの法線を計算する
	normals = vtk.vtkPolyDataNormals()
	normals.SetInputConnection(smoother.GetOutputPort())
	normals.ComputePointNormalsOn()
	normals.Update()

	#推定体積、面積、三角形メッシュの形状指数
	mass = vtk.vtkMassProperties()
	mass.SetInputConnection(normals.GetOutputPort())
	mass.Update()

	#重心
	centerOfMass = vtk.vtkCenterOfMass()
	centerOfMass.SetInputConnection(normals.GetOutputPort())
	centerOfMass.SetUseScalarsAsWeights(0);
	centerOfMass.Update()

	return {
		"volume"  : mass.GetVolume(),
		"points"  : polyData.GetNumberOfPoints(),
		"polys"   : polyData.GetNumberOfPolys(),
		"bounds"  : polyData.GetBounds(),
		"centers" : polyData.GetCenter(),
		"centerOfMass" : centerOfMass.GetCenter()
	}

def _getProperties(file):
	object = file2object(file);

	#polyData = vtk.vtkPolyData()
	#polyData.ShallowCopy(object.GetOutput())
	polyData = object.GetOutput()

	#重心
	centerOfMass = vtk.vtkCenterOfMass()
	centerOfMass.SetInputConnection(object.GetOutputPort())
	centerOfMass.SetUseScalarsAsWeights(0);
	centerOfMass.Update()

	return {
		"points"  : polyData.GetNumberOfPoints(),
		"polys"   : polyData.GetNumberOfPolys(),
		"bounds"  : polyData.GetBounds(),
		"centers" : polyData.GetCenter(),
		"centerOfMass" : centerOfMass.GetCenter()
	}

def _file2object(files):
	object = None
	if isinstance(files,list):
		object = vtk.vtkAppendPolyData()
		for file in files:
			if isinstance(file,basestring):
				o = vtkOBJReader(file)
				port = o.GetOutputPort()
				object.AddInputConnection(port)
				object.Update()
			elif isinstance(file,dict) and file.has_key('path') and isinstance(file['path'],basestring):
				object.AddInputConnection(vtkOBJReader(file['path']).GetOutputPort())
				object.Update()
	else:
		object = vtkOBJReader(files)
	return object

def _getPropertiesVolume(file):
	object = _file2object(file);

	#polyData = vtk.vtkPolyData()
	#polyData.ShallowCopy(object.GetOutput())
	polyData = object.GetOutput()

	triangleFilter = vtk.vtkTriangleFilter()
	triangleFilter.SetInputConnection(object.GetOutputPort())
	triangleFilter.Update()

	#重複しているものを削除
	cleanPolyData = vtk.vtkCleanPolyData()
	cleanPolyData.SetInputConnection(triangleFilter.GetOutputPort())
	cleanPolyData.Update()

	#ポリゴンメッシュの法線を計算する
	normals = vtk.vtkPolyDataNormals()
	normals.SetInputConnection(cleanPolyData.GetOutputPort())
	normals.ComputePointNormalsOn()
	normals.Update()

	#polyDataConnectivityFilter = vtk.vtkPolyDataConnectivityFilter()
	#polyDataConnectivityFilter.SetInputConnection(normals.GetOutputPort())
	#polyDataConnectivityFilter.SetExtractionModeToLargestRegion()
	#polyDataConnectivityFilter.Update()

	#推定体積、面積、三角形メッシュの形状指数
	mass = vtk.vtkMassProperties()
	mass.SetInputConnection(normals.GetOutputPort())
	mass.Update()

	#重心
	centerOfMass = vtk.vtkCenterOfMass()
	centerOfMass.SetInputConnection(object.GetOutputPort())
	centerOfMass.SetUseScalarsAsWeights(0);
	centerOfMass.Update()

	return {
		"volume"  : mass.GetVolume(),
		"points"  : polyData.GetNumberOfPoints(),
		"polys"   : polyData.GetNumberOfPolys(),
		"bounds"  : polyData.GetBounds(),
		"centers" : polyData.GetCenter(),
		"centerOfMass" : centerOfMass.GetCenter()
	}


def obj2normals(file,prefix):

	renderWindow = vtk.vtkRenderWindow()
	renderWindow.SetSize(500,500)

	renderer = vtk.vtkRenderer()
	renderWindow.AddRenderer(renderer)

	#.obj形式の読み込み
	object = vtkOBJReader(file);

	#入力ポリゴンと三角形ストリップから三角形のポリゴンを作成する
#	triangleFilter = vtk.vtkTriangleFilter()
#	triangleFilter.SetInputConnection(object.GetOutputPort())
#	triangleFilter.Update()

	#重複しているものを削除
#	cleanPolyData = vtk.vtkCleanPolyData()
#	cleanPolyData.SetInputConnection(triangleFilter.GetOutputPort())

	#ラプラシアンスムージングを使用して点の座標を調整するフィルタ
	smoother = vtk.vtkSmoothPolyDataFilter()
	smoother.SetInputConnection(object.GetOutputPort())
#	smoother.SetInputConnection(cleanPolyData.GetOutputPort())
	smoother.FeatureEdgeSmoothingOn()
	smoother.Update()

	#ポリゴンメッシュの法線を計算する
	normals = vtk.vtkPolyDataNormals()
	normals.SetInputConnection(smoother.GetOutputPort())
	normals.ComputePointNormalsOn()
	normals.Update()

	mapper = vtk.vtkPolyDataMapper()
	mapper.SetInputConnection(normals.GetOutputPort())

	actor = vtk.vtkActor()
	actor.SetMapper(mapper)

	renderer.AddActor(actor)

	objExporter = vtk.vtkOBJExporter()
	objExporter.SetRenderWindow(renderWindow)
	objExporter.SetFilePrefix(prefix)
	objExporter.Write()

	renderer.RemoveActor(actor)

	return



#ポリゴンを削減
def quadricDecimation(file,prefix,reduction=.9):
	renderWindow = vtk.vtkRenderWindow()
	renderWindow.SetSize(500,500)

	renderer = vtk.vtkRenderer()
	renderWindow.AddRenderer(renderer)

	#.obj形式の読み込み
	object = vtkOBJReader(file);

#	polyData = vtk.vtkPolyData()
#	polyData.ShallowCopy(object.GetOutput())
#	print "\tdecimation" + "------------"
#	print "\t\t" + str(polyData.GetNumberOfPoints()) + " points."
#	print "\t\t" + str(polyData.GetNumberOfPolys())  + " polygons."

	#入力ポリゴンと三角形ストリップから三角形のポリゴンを作成する
	triangleFilter = vtk.vtkTriangleFilter()
	triangleFilter.SetInputConnection(object.GetOutputPort())
	triangleFilter.Update()

	#重複しているものを削除
	cleanPolyData = vtk.vtkCleanPolyData()
	cleanPolyData.SetInputConnection(triangleFilter.GetOutputPort())

	#ラプラシアンスムージングを使用して点の座標を調整するフィルタ
	smoother = vtk.vtkSmoothPolyDataFilter()
	smoother.SetInputConnection(cleanPolyData.GetOutputPort())
	smoother.FeatureEdgeSmoothingOn()
	smoother.Update()

	#ポリゴンメッシュの法線を計算する
	normals = vtk.vtkPolyDataNormals()
	normals.SetInputConnection(smoother.GetOutputPort())
	normals.ComputePointNormalsOn()
	normals.Update()

	#入力ポリゴンと三角形ストリップから三角形のポリゴンを作成する
	triangleFilter = vtk.vtkTriangleFilter()
	triangleFilter.SetInputConnection(normals.GetOutputPort())
	triangleFilter.Update()

	mesh = vtk.vtkQuadricDecimation()
	mesh.SetInputConnection(triangleFilter.GetOutputPort())
	mesh.SetTargetReduction(reduction)
	mesh.Update()

	#ラプラシアンスムージングを使用して点の座標を調整するフィルタ
	smoother = vtk.vtkSmoothPolyDataFilter()
	smoother.SetInputConnection(mesh.GetOutputPort())
	smoother.FeatureEdgeSmoothingOn()
	smoother.Update()

	#ポリゴンメッシュの法線を計算する
	normals = vtk.vtkPolyDataNormals()
	normals.SetInputConnection(smoother.GetOutputPort())
	normals.ComputePointNormalsOn()
	normals.Update()

#	polyData = vtk.vtkPolyData()
#	polyData.ShallowCopy(mesh.GetOutput())
#	print "\tdecimation" + "------------"
#	print "\t\t" + str(polyData.GetNumberOfPoints()) + " points."
#	print "\t\t" + str(polyData.GetNumberOfPolys())  + " polygons."

	mapper = vtk.vtkPolyDataMapper()
	mapper.SetInputConnection(normals.GetOutputPort())

	actor = vtk.vtkActor()
	actor.SetMapper(mapper)

	renderer.AddActor(actor)

	objExporter = vtk.vtkOBJExporter()
	objExporter.SetRenderWindow(renderWindow)
	objExporter.SetFilePrefix(prefix)
	objExporter.Write()

	renderer.RemoveActor(actor)

	return

#リフレクション（ミラーリング）(vtkTransformPolyDataFilter)
def reflection(file,prefix):
	#.obj形式の読み込み
	object = file2object(file);

	trans = vtk.vtkTransform()
	trans.Scale(-1, 1, 1)

	transform = vtk.vtkTransformPolyDataFilter()
	transform.SetInputConnection(object.GetOutputPort())
	transform.SetTransform(trans)
	transform.Update()

	#入力ポリゴンと三角形ストリップから三角形のポリゴンを作成する
	triangleFilter = vtk.vtkTriangleFilter()
	triangleFilter.SetInputConnection(transform.GetOutputPort())
	triangleFilter.Update()

	#重複しているものを削除
	cleanPolyData = vtk.vtkCleanPolyData()
	cleanPolyData.SetInputConnection(triangleFilter.GetOutputPort())

	#ラプラシアンスムージングを使用して点の座標を調整するフィルタ
	smoother = vtk.vtkSmoothPolyDataFilter()
	smoother.SetInputConnection(cleanPolyData.GetOutputPort())
	smoother.FeatureEdgeSmoothingOn()
	smoother.Update()

	#ポリゴンメッシュの法線を計算する
	normals = vtk.vtkPolyDataNormals()
	normals.SetInputConnection(smoother.GetOutputPort())
	normals.ComputePointNormalsOn()
	normals.Update()

	reverse = vtk.vtkReverseSense();
	reverse.SetInputConnection(normals.GetOutputPort())
	reverse.ReverseCellsOn()
	reverse.ReverseNormalsOn()
	reverse.Update()

	renderWindow = vtk.vtkRenderWindow()
	renderWindow.SetSize(500,500)

	renderer = vtk.vtkRenderer()
	renderWindow.AddRenderer(renderer)

	mapper = vtk.vtkPolyDataMapper()
	mapper.SetInputConnection(reverse.GetOutputPort())

	actor = vtk.vtkActor()
	actor.SetMapper(mapper)

	renderer.AddActor(actor)

	objExporter = vtk.vtkOBJExporter()
	objExporter.SetRenderWindow(renderWindow)
	objExporter.SetFilePrefix(prefix)
	objExporter.Write()

	renderer.RemoveActor(actor)

	#polyData = vtk.vtkPolyData()
	#polyData.ShallowCopy(reverse.GetOutput())
	polyData = reverse.GetOutput()

	#推定体積、面積、三角形メッシュの形状指数
	mass = vtk.vtkMassProperties()
	mass.SetInputConnection(reverse.GetOutputPort())
	mass.Update()

	#重心
	centerOfMass = vtk.vtkCenterOfMass()
	centerOfMass.SetInputConnection(reverse.GetOutputPort())
	centerOfMass.SetUseScalarsAsWeights(0);
	centerOfMass.Update()

	return {
		"volume"  : mass.GetVolume(),
		"points"  : polyData.GetNumberOfPoints(),
		"polys"   : polyData.GetNumberOfPolys(),
		"bounds"  : polyData.GetBounds(),
		"centers" : polyData.GetCenter(),
		"centerOfMass" : centerOfMass.GetCenter()
	}

#リフレクション（ミラーリング）(vtkTransformPolyDataFilter)
def reflection_2(file,prefix):
	#.obj形式の読み込み
	object = file2object(file);

	trans = vtk.vtkTransform()
	trans.Scale(-1, 1, 1)

	transform = vtk.vtkTransformPolyDataFilter()
	transform.SetInputConnection(object.GetOutputPort())
	transform.SetTransform(trans)
	transform.Update()

	#入力ポリゴンと三角形ストリップから三角形のポリゴンを作成する
	triangleFilter = vtk.vtkTriangleFilter()
	triangleFilter.SetInputConnection(transform.GetOutputPort())
	triangleFilter.Update()

	#重複しているものを削除
	cleanPolyData = vtk.vtkCleanPolyData()
	cleanPolyData.SetInputConnection(triangleFilter.GetOutputPort())

	#ポリゴンメッシュの法線を計算する
	normals = vtk.vtkPolyDataNormals()
	normals.SetInputConnection(cleanPolyData.GetOutputPort())
	normals.ComputePointNormalsOn()
	normals.Update()

	reverse = vtk.vtkReverseSense();
	reverse.SetInputConnection(normals.GetOutputPort())
	reverse.ReverseCellsOn()
	reverse.ReverseNormalsOn()
	reverse.Update()

	renderWindow = vtk.vtkRenderWindow()
	renderWindow.SetSize(500,500)

	renderer = vtk.vtkRenderer()
	renderWindow.AddRenderer(renderer)

	mapper = vtk.vtkPolyDataMapper()
	mapper.SetInputConnection(reverse.GetOutputPort())

	actor = vtk.vtkActor()
	actor.SetMapper(mapper)

	renderer.AddActor(actor)

	objExporter = vtk.vtkOBJExporter()
	objExporter.SetRenderWindow(renderWindow)
	objExporter.SetFilePrefix(prefix)
	objExporter.Write()

	renderer.RemoveActor(actor)

	#polyData = vtk.vtkPolyData()
	#polyData.ShallowCopy(reverse.GetOutput())
	polyData = reverse.GetOutput()

	#推定体積、面積、三角形メッシュの形状指数
	mass = vtk.vtkMassProperties()
	mass.SetInputConnection(reverse.GetOutputPort())
	mass.Update()

	#重心
	centerOfMass = vtk.vtkCenterOfMass()
	centerOfMass.SetInputConnection(reverse.GetOutputPort())
	centerOfMass.SetUseScalarsAsWeights(0);
	centerOfMass.Update()

	return {
		"volume"  : mass.GetVolume(),
		"points"  : polyData.GetNumberOfPoints(),
		"polys"   : polyData.GetNumberOfPolys(),
		"bounds"  : polyData.GetBounds(),
		"centers" : polyData.GetCenter(),
		"centerOfMass" : centerOfMass.GetCenter()
	}

#ポイントがOBJ内に存在するか(vtkDelaunay3D, vtkPolyData::FindCell)
def pointInsideObject(file,point):
	#.obj形式の読み込み
	object = file2object(file)
	#print str(object)
	#print str(object.GetOutput())

	objectPolyData = object.GetOutput()
	#objectPolyData.ShallowCopy(object.GetOutput())
	#print str(objectPolyData)

	points = vtk.vtkPoints()
	points.InsertNextPoint(point)

	pointsPolydata = vtk.vtkPolyData()
	pointsPolydata.SetPoints(points)
	#print ""
	#print str(point)
	#print str(pointsPolydata)
	#print str(objectPolyData)

	selectEnclosedPoints = vtk.vtkSelectEnclosedPoints()
	selectEnclosedPoints.SetTolerance(0.0)
	selectEnclosedPoints.SetInput(pointsPolydata);

	selectEnclosedPoints.SetSurface(objectPolyData);
	selectEnclosedPoints.Update()

	#print str(selectEnclosedPoints)
	#print str(selectEnclosedPoints.IsInside(0))
	return selectEnclosedPoints.IsInside(0)

def pointsOutsideObject(file,point):
	#print str(isinstance(point,list))
	#.obj形式の読み込み
	object = file2object(file)
	#print str(object)
	#print str(object.GetOutput())

	objectPolyData = object.GetOutput()
	#objectPolyData.ShallowCopy(object.GetOutput())
	#print str(objectPolyData)

	points = vtk.vtkPoints()
	if isinstance(point,list):
		for p in point:
			points.InsertNextPoint(p)
	else:
		points.InsertNextPoint(point)

	pointsPolydata = vtk.vtkPolyData()
	pointsPolydata.SetPoints(points)
	#print ""
	#print str(point)
	#print str(pointsPolydata)
	#print str(objectPolyData)

	selectEnclosedPoints = vtk.vtkSelectEnclosedPoints()
	selectEnclosedPoints.InsideOutOn()
	selectEnclosedPoints.SetTolerance(0.0)
	selectEnclosedPoints.SetInput(pointsPolydata);

	selectEnclosedPoints.SetSurface(objectPolyData);
	selectEnclosedPoints.Update()

	incount = 0
	outcount = 0
	inpoints = []
	for i in range(0, pointsPolydata.GetNumberOfPoints()):
		if selectEnclosedPoints.IsInside(i):
			outcount += 1
		else:
			incount += 1
			inpoints.append(pointsPolydata.GetPoint(i))

	#print str(selectEnclosedPoints)
	#print str(selectEnclosedPoints.IsInside(0))
	return inpoints


def pointDistanceObject(file,point):
	#.obj形式の読み込み
	object = file2object(file)
	objectPolyData = object.GetOutput()
	dist_arr = []
	for i in range(1, objectPolyData.GetNumberOfPoints()):
		distSquared = vtk.vtkMath.Distance2BetweenPoints(point,objectPolyData.GetPoint(i))
		dist = math.sqrt(distSquared)
		dist_arr.append(dist)
	return min(dist_arr)


#file2がfile1内に存在するか
def objectInsideObject(file1,file2):
	#.obj形式の読み込み
	object1 = file2object(file1)
	object2 = file2object(file2)

	objectPolyData1 = object1.GetOutput()
	objectPolyData2 = object2.GetOutput()

	#points = vtk.vtkPoints()
	#for i in range(0, objectPolyData2.GetNumberOfPoints()):
	#	point = objectPolyData2.GetPoint(i);
	#	points.InsertNextPoint(point)

	#pointsPolydata = vtk.vtkPolyData()
	#pointsPolydata.SetPoints(points)

	selectEnclosedPoints = vtk.vtkSelectEnclosedPoints()
	selectEnclosedPoints.SetInput(objectPolyData2);
	selectEnclosedPoints.SetTolerance(0.0)
	selectEnclosedPoints.SetSurface(objectPolyData1);
	selectEnclosedPoints.Update()
	#print "selectEnclosedPoints.GetInsideOut()="+str(selectEnclosedPoints.GetInsideOut())

	incount = 0
	outcount = 0
	for i in range(0, objectPolyData2.GetNumberOfPoints()):
		if selectEnclosedPoints.IsInside(i):
			incount += 1
		else:
			outcount += 1

	return {
		"incount" :incount,
		"outcount" :outcount,
		"all": objectPolyData2.GetNumberOfPoints() - 0
	}

#file2がfile1内に存在するか
def objectOutsideObject(file1,file2):
	#.obj形式の読み込み
	object1 = file2object(file1)
	object2 = file2object(file2)

	objectPolyData1 = object1.GetOutput()
	objectPolyData2 = object2.GetOutput()

	#points = vtk.vtkPoints()
	#for i in range(0, objectPolyData2.GetNumberOfPoints()):
	#	point = objectPolyData2.GetPoint(i);
	#	points.InsertNextPoint(point)

	#pointsPolydata = vtk.vtkPolyData()
	#pointsPolydata.SetPoints(points)

	selectEnclosedPoints = vtk.vtkSelectEnclosedPoints()
	selectEnclosedPoints.SetInput(objectPolyData2);
	selectEnclosedPoints.InsideOutOn()
	selectEnclosedPoints.SetTolerance(0.0)
	selectEnclosedPoints.SetSurface(objectPolyData1);
	selectEnclosedPoints.Update()
	#print "selectEnclosedPoints.GetInsideOut()="+str(selectEnclosedPoints.GetInsideOut())

	incount = 0
	outcount = 0
	for i in range(0, objectPolyData2.GetNumberOfPoints()):
		if selectEnclosedPoints.IsInside(i):
			outcount += 1
		else:
			incount += 1

	return {
		"incount" :incount,
		"outcount" :outcount,
		"all": objectPolyData2.GetNumberOfPoints() - 0
	}

#file2がfile1内に存在するか（テスト）
def objectInsideObject2(file1,file2,prefix):
	#.obj形式の読み込み
	object1 = file2object(file1)
	object2 = file2object(file2)

	objectPolyData1 = object1.GetOutput()
	objectPolyData2 = object2.GetOutput()

	#print "objectPolyData1.GetNumberOfCells()="+str(objectPolyData1.GetNumberOfCells())
	#print "objectPolyData1.GetNumberOfPolys()="+str(objectPolyData1.GetNumberOfPolys())
	#return

	selectEnclosedPoints1 = vtk.vtkSelectEnclosedPoints()

	#print str(selectEnclosedPoints1.GetInsideOut())
	#print str(selectEnclosedPoints1.GetCheckSurface())
	#print str(selectEnclosedPoints1.GetTolerance())

	#selectEnclosedPoints1.InsideOutOn()
	#selectEnclosedPoints1.CheckSurfaceOn()
	selectEnclosedPoints1.InsideOutOff()
	selectEnclosedPoints1.CheckSurfaceOff()
	selectEnclosedPoints1.SetTolerance(0.0)

	#print str(selectEnclosedPoints1.GetInsideOut())
	#print str(selectEnclosedPoints1.GetCheckSurface())
	#print str(selectEnclosedPoints1.GetTolerance())


	selectEnclosedPoints1.SetInput(objectPolyData2);
	selectEnclosedPoints1.SetSurface(objectPolyData1);
	selectEnclosedPoints1.Update()

	selectEnclosedPoints2 = vtk.vtkSelectEnclosedPoints()
	selectEnclosedPoints2.SetInput(objectPolyData1);
	selectEnclosedPoints2.SetTolerance(0.0)
	selectEnclosedPoints2.SetSurface(objectPolyData2);
	selectEnclosedPoints2.Update()


	'''
	outsizePoints = vtk.vtkPoints()
	outsizeCellArray = vtk.vtkCellArray()
	outsizePolyData = vtk.vtkPolyData()
	outsizeId = 0
	incount = 0

	dict1 = {}
	dict2 = {}

	for i in range(0, objectPolyData2.GetNumberOfPoints()):
		if selectEnclosedPoints1.IsInside(i):
			incount += 1
		else:
			point = objectPolyData2.GetPoint(i)
			idList = vtk.vtkIdList()
			objectPolyData2.GetPointCells(objectPolyData2.FindPoint(point),idList)
			for j in range(0, idList.GetNumberOfIds()):
				cellId = idList.GetId(j)

				if cellId not in dict2:
					dict2[cellId] = 1
					outsizePoints.InsertNextPoint(point)
					cell = objectPolyData2.GetCell(cellId)
					cellPoints = cell.GetPoints()
					outsizeCellArray.InsertNextCell(cellPoints.GetNumberOfPoints())
					for j in range(0, cellPoints.GetNumberOfPoints()):
						outsizePoints.InsertPoint(outsizeId, cellPoints.GetPoint(j))
						outsizeCellArray.InsertCellPoint(outsizeId)
						outsizeId += 1

	for i in range(0, objectPolyData1.GetNumberOfPoints()):
		point = objectPolyData1.GetPoint(i)
		cellIdList = vtk.vtkIdList()
		objectPolyData1.GetPointCells(objectPolyData1.FindPoint(point),cellIdList)
		for j in range(0, cellIdList.GetNumberOfIds()):
			cellId = cellIdList.GetId(j)

			if cellId in dict1:
				continue

			dict1[cellId] = 1
			outsizePoints.InsertNextPoint(point)
			cell = objectPolyData1.GetCell(cellId)
			cellPoints = cell.GetPoints()
			outsizeCellArray.InsertNextCell(cellPoints.GetNumberOfPoints())
			for j in range(0, cellPoints.GetNumberOfPoints()):
				outsizePoints.InsertPoint(outsizeId, cellPoints.GetPoint(j))
				outsizeCellArray.InsertCellPoint(outsizeId)
				outsizeId += 1

	outsizePolyData.SetPoints(outsizePoints)
	outsizePolyData.SetPolys(outsizeCellArray)
	'''

	#print "objectPolyData1.GetNumberOfCells()="+str(objectPolyData1.GetNumberOfCells())
	#print "objectPolyData1.GetNumberOfPolys()="+str(objectPolyData1.GetNumberOfPolys())
	#return


	outsizePoints = objectPolyData1.GetPoints()
	outsizeCellArray = objectPolyData1.GetPolys()
	outsizePolyData = vtk.vtkPolyData()
	incount = 0
	pointId = objectPolyData1.GetNumberOfPoints()


	for i in range(0, objectPolyData2.GetNumberOfPoints()):
		if selectEnclosedPoints1.IsInside(i):
			incount += 1
		else:
			point = objectPolyData2.GetPoint(i)
			cellIdList = vtk.vtkIdList()
			objectPolyData2.GetPointCells(objectPolyData2.FindPoint(point),cellIdList)
			for j in range(0, cellIdList.GetNumberOfIds()):
				cellId = cellIdList.GetId(j)
				#print "cellId="+str(cellId)

				cell = objectPolyData2.GetCell(cellId)
				cellPoints = cell.GetPoints()
				outsizeCellArray.InsertNextCell(cellPoints.GetNumberOfPoints())
				for j in range(0, cellPoints.GetNumberOfPoints()):
					outsizePoints.InsertPoint(pointId, cellPoints.GetPoint(j))
					outsizeCellArray.InsertCellPoint(pointId)
					pointId += 1





	outsizePolyData.SetPoints(outsizePoints)
	outsizePolyData.SetPolys(outsizeCellArray)


	#outsizePolyData = objectPolyData1
	#print str(outsizePolyData)

	#return

	#入力ポリゴンと三角形ストリップから三角形のポリゴンを作成する
	triangleFilter = vtk.vtkTriangleFilter()
	triangleFilter.SetInputConnection(outsizePolyData.GetProducerPort())
	triangleFilter.Update()

	#重複しているものを削除
	cleanPolyData = vtk.vtkCleanPolyData()
	cleanPolyData.SetInputConnection(triangleFilter.GetOutputPort())

	#ラプラシアンスムージングを使用して点の座標を調整するフィルタ
	smoother = vtk.vtkSmoothPolyDataFilter()
	smoother.SetInputConnection(cleanPolyData.GetOutputPort())
	#smoother.FeatureEdgeSmoothingOn()
	smoother.SetNumberOfIterations(15)
	smoother.SetRelaxationFactor(0.1)
	smoother.FeatureEdgeSmoothingOff()
	smoother.BoundarySmoothingOn()
	smoother.Update()

	#ポリゴンメッシュの法線を計算する
	normals = vtk.vtkPolyDataNormals()
	normals.SetInputConnection(cleanPolyData.GetOutputPort())
	normals.ComputePointNormalsOn()
	normals.ComputeCellNormalsOn()
	normals.Update()

	#推定体積、面積、三角形メッシュの形状指数
	mass = vtk.vtkMassProperties()
	mass.SetInputConnection(normals.GetOutputPort())
	mass.Update()
	#print str(mass.GetVolume())

	#重心
	centerOfMass = vtk.vtkCenterOfMass()
	centerOfMass.SetInputConnection(normals.GetOutputPort())
	centerOfMass.SetUseScalarsAsWeights(0);
	centerOfMass.Update()

	'''
	#	"volume"  : mass.GetVolume(),
	#	"points"  : outsizePolyData.GetNumberOfPoints(),
	#	"polys"   : outsizePolyData.GetNumberOfPolys(),
	#	"bounds"  : outsizePolyData.GetBounds(),
	#	"centers" : outsizePolyData.GetCenter(),
	#	"centerOfMass" : centerOfMass.GetCenter()
	'''

	renderWindow = vtk.vtkRenderWindow()
	renderWindow.SetSize(500,500)

	renderer = vtk.vtkRenderer()
	renderWindow.AddRenderer(renderer)

	mapper = vtk.vtkPolyDataMapper()
	mapper.SetInputConnection(normals.GetOutputPort())

	actor = vtk.vtkActor()
	actor.SetMapper(mapper)

	renderer.AddActor(actor)

	objExporter = vtk.vtkOBJExporter()
	objExporter.SetRenderWindow(renderWindow)
	objExporter.SetFilePrefix(prefix)
	objExporter.Write()

	renderer.RemoveActor(actor)

	return

	return {
		"incount" :incount,
		"all": objectPolyData2.GetNumberOfPoints() - 0,

	}
