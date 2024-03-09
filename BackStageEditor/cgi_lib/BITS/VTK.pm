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

import vtk

def vtkOBJReader(file):
	#.obj形式の読み込み
	object = vtk.vtkOBJReader()
	object.SetFileName(file)
	object.Update()
	return object;

def getProperties(file):
	object = vtkOBJReader(file);

	polyData = vtk.vtkPolyData()
	polyData.ShallowCopy(object.GetOutput())

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

	return {
		"volume"  : mass.GetVolume(),
		"points"  : polyData.GetNumberOfPoints(),
		"polys"   : polyData.GetNumberOfPolys(),
		"bounds"  : polyData.GetBounds(),
		"centers" : polyData.GetCenter()
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
	object = vtkOBJReader(file);

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

	polyData = vtk.vtkPolyData()
	polyData.ShallowCopy(reverse.GetOutput())

	#推定体積、面積、三角形メッシュの形状指数
	mass = vtk.vtkMassProperties()
	mass.SetInputConnection(reverse.GetOutputPort())
	mass.Update()

	return {
		"volume"  : mass.GetVolume(),
		"points"  : polyData.GetNumberOfPoints(),
		"polys"   : polyData.GetNumberOfPolys(),
		"bounds"  : polyData.GetBounds(),
		"centers" : polyData.GetCenter()
	}
