#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import vtk
import inspect
#import cmath

class obj2deci:

	def __init__(self):
		self.objects = {}

	def objDeleteAll(self):
		for k in self.objects.keys():
			del self.objects[k]

	def objReader(self,file):
		if self.objects.has_key(file) != True:
			self.objects[file] = vtk.vtkOBJReader()
			self.objects[file].SetFileName(file)
			self.objects[file].Update()

		return self.objects[file]

	def getPolyDataNormals(self,object):
		#ラプラシアンスムージングを使用して点の座標を調整するフィルタ
		smoother = vtk.vtkSmoothPolyDataFilter()
		smoother.SetInputConnection(object.GetOutputPort())
		smoother.FeatureEdgeSmoothingOn()
		smoother.Update()

		#ポリゴンメッシュの法線を計算する
		normals = vtk.vtkPolyDataNormals()
		normals.SetInputConnection(smoother.GetOutputPort())
		normals.ComputePointNormalsOn()
		normals.Update()

		return normals

	def file2object(self,files):
		object = None
		if isinstance(files,list):
			object = vtk.vtkAppendPolyData()
			for file in files:
				if isinstance(file,str) or isinstance(file,unicode):
					object.AddInputConnection(self.objReader(file).GetOutputPort())
					object.Update()
				elif isinstance(file,dict) and file.has_key('path') and (isinstance(file['path'],str) or isinstance(file['path'],unicode)):
					object.AddInputConnection(self.objReader(file['path']).GetOutputPort())
					object.Update()
			polyData = self.polyData(object)
		else:
			object = self.objReader(files)
		return object

	def polyData(self,object):
		polyData = vtk.vtkPolyData()
		polyData.ShallowCopy(object.GetOutput())
		return polyData

	def getProperties(self,files):
		if files == None:
			return None

		object = self.file2object(files)
		polyData = self.polyData(object)

		#ポリゴンメッシュの法線を計算する
		#normals = self.getPolyDataNormals(object)

		#入力ポリゴンと三角形ストリップから三角形のポリゴンを作成する
		normals = self.triangleFilter(self.getPolyDataNormals(object))

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

	def getRenderer(self):
		return vtk.vtkRenderer()

	def getRenderWindow(self,renderer):
		renderWindow = vtk.vtkRenderWindow()
		renderWindow.SetSize(500,500)
		renderWindow.AddRenderer(renderer)
		return renderWindow

	def OBJExporter(self,prefix,object):
		#ポリゴンメッシュの法線を計算する
		normals = self.getPolyDataNormals(object)

		mapper = vtk.vtkPolyDataMapper()
		mapper.SetInputConnection(normals.GetOutputPort())

		actor = vtk.vtkActor()
		actor.SetMapper(mapper)

		renderer = self.getRenderer()
		renderWindow = self.getRenderWindow(renderer)
		renderer.AddActor(actor)

		objExporter = vtk.vtkOBJExporter()
		objExporter.SetRenderWindow(renderWindow)
		objExporter.SetFilePrefix(prefix)
		objExporter.Write()

		renderer.RemoveActor(actor)

	def normals(self,files,prefix):
		if files == None:
			return
		object = self.file2object(files)
		self.OBJExporter(prefix,object)
		return

	def triangleFilter(self,object):
		#入力ポリゴンと三角形ストリップから三角形のポリゴンを作成する
		triangleFilter = vtk.vtkTriangleFilter()
		triangleFilter.SetInputConnection(object.GetOutputPort())
		triangleFilter.Update()
		return triangleFilter

	#ポリゴンを削減(vtkQuadricDecimation)
	def quadricDecimation(self,files,prefix,reduction=.9):
		if files == None:
			return
		object = self.file2object(files)

		#入力ポリゴンと三角形ストリップから三角形のポリゴンを作成する
		triangleFilter = self.triangleFilter(self.getPolyDataNormals(object))

		#ポリゴンを削減
		mesh = vtk.vtkQuadricDecimation()
		mesh.SetInputConnection(triangleFilter.GetOutputPort())
		mesh.SetTargetReduction(reduction)
		#mesh.AttributeErrorMetricOn()
		mesh.Update()

		self.OBJExporter(prefix,mesh)
		return

	#ポリゴンを削減(vtkDecimatePro)
	def decimatePro(self,files,prefix,reduction=.9):
		if files == None:
			return
		object = self.file2object(files)

		#入力ポリゴンと三角形ストリップから三角形のポリゴンを作成する
		triangleFilter = self.triangleFilter(self.getPolyDataNormals(object))

		#ポリゴンを削減
		mesh = vtk.vtkDecimatePro()
		mesh.SetInputConnection(triangleFilter.GetOutputPort())
		mesh.SetTargetReduction(reduction)
		mesh.SplittingOff()
		mesh.BoundaryVertexDeletionOff()
		mesh.Update()

		self.OBJExporter(prefix,mesh)

		return

	#ポリゴンを削減(vtkQuadricClustering)
	def quadricClustering(self,files,prefix):
		if files == None:
			return
		object = self.file2object(files)

		#入力ポリゴンと三角形ストリップから三角形のポリゴンを作成する
		triangleFilter = self.triangleFilter(self.getPolyDataNormals(object))

		#ポリゴンを削減
		polyData = self.polyData(triangleFilter)
		bounds = polyData.GetBounds()
		xd = abs(int(bounds[1]-bounds[0]))
		yd = abs(int(bounds[3]-bounds[2]))
		zd = abs(int(bounds[5]-bounds[4]))

		qc = vtk.vtkQuadricClustering()
		qc.SetInputConnection(triangleFilter.GetOutputPort())
		qc.SetNumberOfXDivisions(xd)
		qc.SetNumberOfYDivisions(yd)
		qc.SetNumberOfZDivisions(zd)
		qc.AutoAdjustNumberOfDivisionsOn()
		qc.UseFeatureEdgesOn()
		qc.UseFeaturePointsOn()
		qc.UseInternalTrianglesOn()
		qc.UseInputPointsOn()
		qc.Update()

		self.OBJExporter(prefix,qc)

		return

	#BooleanOperationPolyDataFilter
	def booleanOperationRate(self,files1,files2,prefix=None):
		if files1 == None or files2 == None:
			return
		object1 = self.file2object(files1)
		object2 = self.file2object(files2)

		#入力ポリゴンと三角形ストリップから三角形のポリゴンを作成する
		normals1 = self.triangleFilter(self.getPolyDataNormals(object1))
		normals2 = self.triangleFilter(self.getPolyDataNormals(object2))

#		polyData1 = self.polyData(object1)
#		polyData2 = self.polyData(object2)
#		print "booleanOperationRate(1)::"+str(inspect.currentframe().f_lineno)+"::"+str(polyData1.GetNumberOfPoints())+"::"+str(polyData1.GetNumberOfPolys())
#		print "booleanOperationRate(2)::"+str(inspect.currentframe().f_lineno)+"::"+str(polyData2.GetNumberOfPoints())+"::"+str(polyData2.GetNumberOfPolys())

		#重なっている位置？を取得
		intersection = vtk.vtkIntersectionPolyDataFilter()
		intersection.SetInputConnection(0,normals1.GetOutputPort())
		intersection.SetInputConnection(1,normals2.GetOutputPort())
		intersection.Update()
		intersectionPolyData = self.polyData(intersection)
#		print "booleanOperationRate(3)::"+str(inspect.currentframe().f_lineno)+"::"+str(intersectionPolyData.GetNumberOfPoints())+"::"+str(intersectionPolyData.GetNumberOfPolys())

		volume1 = 0.0
		volume2 = 0.0

		if intersectionPolyData.GetNumberOfPoints()>0:
			#重なっている領域を取得
			booleanOperation = vtk.vtkBooleanOperationPolyDataFilter()
#			booleanOperation.SetOperationToUnion()
			booleanOperation.SetOperationToIntersection()
#			booleanOperation.SetOperationToDifference()
			booleanOperation.ReorientDifferenceCellsOff()
			booleanOperation.SetInputConnection(0,normals1.GetOutputPort())
			booleanOperation.SetInputConnection(1,normals2.GetOutputPort())
			booleanOperation.Update()

			#推定体積
			mass1 = vtk.vtkMassProperties()
			mass1.SetInputConnection(normals1.GetOutputPort())
			mass1.Update()
			volume1 = mass1.GetVolume();
#			if __name__ == "__main__":
#				print "booleanOperationRate()::"+str(inspect.currentframe().f_lineno)+"::volume1::GetVolume()::"+str(mass1.GetVolume())
#				print "booleanOperationRate()::"+str(inspect.currentframe().f_lineno)+"::volume1::GetVolumeProjected()::"+str(mass1.GetVolumeProjected())
#				print "booleanOperationRate()::"+str(inspect.currentframe().f_lineno)+"::volume1::GetNormalizedShapeIndex()::"+str(mass1.GetNormalizedShapeIndex())

			#推定体積
			mass2 = vtk.vtkMassProperties()
			mass2.SetInputConnection(normals2.GetOutputPort())
			mass2.Update()
			volume2 = mass2.GetVolume();
#			if __name__ == "__main__":
#				print "booleanOperationRate()::"+str(inspect.currentframe().f_lineno)+"::volume2::GetVolume()::"+str(mass2.GetVolume())
#				print "booleanOperationRate()::"+str(inspect.currentframe().f_lineno)+"::volume2::GetVolumeProjected()::"+str(mass2.GetVolumeProjected())
#				print "booleanOperationRate()::"+str(inspect.currentframe().f_lineno)+"::volume2::GetNormalizedShapeIndex()::"+str(mass2.GetNormalizedShapeIndex())

			#推定体積
			'''
			filler = vtk.vtkTriangleFilter()
			filler.SetInputConnection(booleanOperation.GetOutputPort())
			cleaner = vtk.vtkCleanPolyData()
			cleaner.SetInputConnection(filler.GetOutputPort())
			apdNormals = vtk.vtkPolyDataNormals()
			apdNormals.SetInputConnection(cleaner.GetOutputPort())
			reverse = vtk.vtkReverseSense();
			reverse.SetInputConnection(apdNormals.GetOutputPort())
			reverse.ReverseCellsOn()
			reverse.ReverseNormalsOn()
			triangle = vtk.vtkTriangleFilter()
			triangle.SetInputConnection(reverse.GetOutputPort())
			'''

			triangleFilter = self.triangleFilter(booleanOperation)

			'''
			appendFilter = vtk.vtkAppendPolyData()
			appendFilter.AddInputConnection(normals1.GetOutputPort())
			appendFilter.AddInputConnection(normals2.GetOutputPort())
			appendFilter.Update()
			cleaner = vtk.vtkCleanPolyData()
			cleaner.SetInputConnection(appendFilter.GetOutputPort())
			triangleFilter = self.triangleFilter(cleaner)
			'''

			mass3 = vtk.vtkMassProperties()
			mass3.SetInputConnection(triangleFilter.GetOutputPort())
			mass3.Update()
			volume3 = mass3.GetVolume();

			rtn = {
				"volume": mass3.GetVolume(),
				"volumeProjected": mass3.GetVolumeProjected(),
				"normalizedShapeIndex": mass3.GetNormalizedShapeIndex()
			}

#			if __name__ == "__main__":
#				print "booleanOperationRate()::"+str(inspect.currentframe().f_lineno)+"::volume3::GetVolume()::"+str(mass3.GetVolume())
#				print "booleanOperationRate()::"+str(inspect.currentframe().f_lineno)+"::volume3::GetVolumeProjected()::"+str(mass3.GetVolumeProjected())
#				print "booleanOperationRate()::"+str(inspect.currentframe().f_lineno)+"::volume3::GetNormalizedShapeIndex()::"+str(mass3.GetNormalizedShapeIndex())
#			print "booleanOperationRate()::"+str(inspect.currentframe().f_lineno)+"::volume3::GetVolumeX()::"+str(mass3.GetVolumeX())
#			print "booleanOperationRate()::"+str(inspect.currentframe().f_lineno)+"::volume3::GetVolumeY()::"+str(mass3.GetVolumeY())
#			print "booleanOperationRate()::"+str(inspect.currentframe().f_lineno)+"::volume3::GetVolumeZ()::"+str(mass3.GetVolumeZ())
#			print "booleanOperationRate()::"+str(inspect.currentframe().f_lineno)+"::volume3::GetKx()::"+str(mass3.GetKx())
#			print "booleanOperationRate()::"+str(inspect.currentframe().f_lineno)+"::volume3::GetKy()::"+str(mass3.GetKy())
#			print "booleanOperationRate()::"+str(inspect.currentframe().f_lineno)+"::volume3::GetKz()::"+str(mass3.GetKz())
#			print "booleanOperationRate()::"+str(inspect.currentframe().f_lineno)+"::volume3::GetSurfaceArea()::"+str(mass3.GetSurfaceArea())
#			print "booleanOperationRate()::"+str(inspect.currentframe().f_lineno)+"::volume3::GetMinCellArea()::"+str(mass3.GetMinCellArea())
#			print "booleanOperationRate()::"+str(inspect.currentframe().f_lineno)+"::volume3::GetMaxCellArea()::"+str(mass3.GetMaxCellArea())
#			print "booleanOperationRate()::"+str(inspect.currentframe().f_lineno)+"::volume3::GetNormalizedShapeIndex()::"+str(mass3.GetNormalizedShapeIndex())

			if prefix != None:
				self.OBJExporter(prefix,triangleFilter)

#			if __name__ == "__main__":
#				self.OBJExporter('test',triangleFilter)

			return rtn

			if mass3.GetNormalizedShapeIndex() >= 1.0:
				val = volume3/volume1
				if val<0.0001:
					val = 0.0001
				return val
			else:
				return 0.0001

#			if volume1>volume2:
#				return volume3/volume1
#			else:
#				return volume3/volume2
		else:
			return

	#リフレクション（ミラーリング）(vtkReflectionFilter) #未完成
	def reflection(self,files,prefix):
		if files == None:
			return
		object = self.file2object(files)

		trans = vtk.vtkTransform()
		trans.Scale(-1, 1, 1)

		transform = vtk.vtkTransformPolyDataFilter()
		transform.SetInputConnection(object.GetOutputPort())
		transform.SetTransform(trans)
		transform.Update()

		filler = vtk.vtkTriangleFilter()
		filler.SetInputConnection(transform.GetOutputPort())
		filler.Update()

		cleaner = vtk.vtkCleanPolyData()
		cleaner.SetInputConnection(filler.GetOutputPort())
		cleaner.Update()

		apdNormals = vtk.vtkPolyDataNormals()
		apdNormals.SetInputConnection(cleaner.GetOutputPort())
		apdNormals.Update()

		reverse = vtk.vtkReverseSense();
		reverse.SetInputConnection(apdNormals.GetOutputPort())
		reverse.ReverseCellsOn()
		reverse.ReverseNormalsOn()
		reverse.Update()

		self.OBJExporter(prefix,reverse)


		'''
		#リフレクション（ミラーリング）
		refl = vtk.vtkReflectionFilter()
		refl.SetInputConnection(triangleFilter.GetOutputPort())
		refl.CopyInputOff()
		refl.SetPlane(6)
		refl.Update()

		polyData1 = self.polyData(refl)
		print "booleanOperationRate(1)::"+str(inspect.currentframe().f_lineno)+"::"+str(polyData1.GetNumberOfPoints())+"::"+str(polyData1.GetNumberOfPolys())

		reverse = vtk.vtkReverseSense();
		reverse.SetInputConnection(refl.GetOutputPort())
		reverse.ReverseCellsOn()
		reverse.ReverseNormalsOn()

		polyData1 = self.polyData(reverse)
		print "booleanOperationRate(1)::"+str(inspect.currentframe().f_lineno)+"::"+str(polyData1.GetNumberOfPoints())+"::"+str(polyData1.GetNumberOfPolys())

		filler = vtk.vtkTriangleFilter()
		filler.SetInputConnection(refl.GetOutputPort())

		cleaner = vtk.vtkCleanPolyData()
		cleaner.SetInputConnection(filler.GetOutputPort())

		apdNormals = vtk.vtkPolyDataNormals()
		apdNormals.SetInputConnection(cleaner.GetOutputPort())

		reverse = vtk.vtkReverseSense();
		reverse.SetInputConnection(apdNormals.GetOutputPort())
		reverse.ReverseCellsOn()
		reverse.ReverseNormalsOn()

		polyData1 = self.polyData(reverse)
		print "booleanOperationRate(1)::"+str(inspect.currentframe().f_lineno)+"::"+str(polyData1.GetNumberOfPoints())+"::"+str(polyData1.GetNumberOfPolys())

		if __name__ == "__main__":
			print "reflection()::"+str(inspect.currentframe().f_lineno)+"::"

		self.OBJExporter(prefix,apdNormals)
		'''

		return


	def cleanPolyData(self,files,prefix):
		if files == None:
			return
		object = self.file2object(files)

		filler = vtk.vtkTriangleFilter()
		filler.SetInputConnection(object.GetOutputPort())

		cleaner = vtk.vtkCleanPolyData()
		cleaner.SetInputConnection(filler.GetOutputPort())

		apdNormals = vtk.vtkPolyDataNormals()
		apdNormals.SetInputConnection(cleaner.GetOutputPort())

		reverse = vtk.vtkReverseSense();
		reverse.SetInputConnection(apdNormals.GetOutputPort())
		reverse.ReverseCellsOff()
		reverse.ReverseNormalsOff()

		mass1 = vtk.vtkMassProperties()
		mass1.SetInputConnection(reverse.GetOutputPort())
		mass1.Update()
		volume1 = mass1.GetVolume();
#		if __name__ == "__main__":
#			print "booleanOperationRate()::"+str(inspect.currentframe().f_lineno)+"::volume1::GetVolume()::"+str(mass1.GetVolume())
#			print "booleanOperationRate()::"+str(inspect.currentframe().f_lineno)+"::volume1::GetVolumeProjected()::"+str(mass1.GetVolumeProjected())
#			print "booleanOperationRate()::"+str(inspect.currentframe().f_lineno)+"::volume1::GetNormalizedShapeIndex()::"+str(mass1.GetNormalizedShapeIndex())

		self.OBJExporter(prefix,apdNormals)
		return

	def massProperties(self,files):
		if files == None:
			return
		object = self.file2object(files)

		filler = vtk.vtkTriangleFilter()
		filler.SetInputConnection(object.GetOutputPort())

		cleaner = vtk.vtkCleanPolyData()
		cleaner.SetInputConnection(filler.GetOutputPort())

		apdNormals = vtk.vtkPolyDataNormals()
		apdNormals.SetInputConnection(cleaner.GetOutputPort())

		mass1 = vtk.vtkMassProperties()
		mass1.SetInputConnection(apdNormals.GetOutputPort())
		mass1.Update()
		volume1 = mass1.GetVolume();
#		if __name__ == "__main__":
#			print "booleanOperationRate()::"+str(inspect.currentframe().f_lineno)+"::volume1::GetVolume()::"+str(mass1.GetVolume())
#			print "booleanOperationRate()::"+str(inspect.currentframe().f_lineno)+"::volume1::GetVolumeProjected()::"+str(mass1.GetVolumeProjected())
#			print "booleanOperationRate()::"+str(inspect.currentframe().f_lineno)+"::volume1::GetNormalizedShapeIndex()::"+str(mass1.GetNormalizedShapeIndex())


		return


if __name__ == "__main__":
	od = obj2deci();
#	od.booleanOperationRate("ag_data/bp3d/FJ/FJ1052.obj","/ext1/project/ag/ag1/htdocs/ag-renderer/art_file/FJ3175-0.obj");
#	rtn = od.booleanOperationRate("ag_data/bp3d/FJ/FJ1052.obj","ag_data/bp3d/FJ/FJ1053.obj");
#	rtn = od.booleanOperationRate(["/ext1/project/ag/ag1/htdocs/ag-renderer/art_file/FJ3441-0.obj","/ext1/project/ag/ag1/htdocs/ag-renderer/art_file/FJ3659-0.obj"],["/ext1/project/ag/ag1/htdocs/ag-renderer/art_file/FJ1861-0.obj","/ext1/project/ag/ag1/htdocs/ag-renderer/art_file/FJ1862-0.obj"]);
#	rtn = od.booleanOperationRate(["/ext1/project/ag/ag1/htdocs/ag-renderer/art_file/FJ3441-0.obj","/ext1/project/ag/ag1/htdocs/ag-renderer/art_file/FJ3659-0.obj"],["/ext1/project/ag/ag1/htdocs/ag-renderer/art_file/FJ2810-0.obj"]);
#	rtn = od.booleanOperationRate("ag_data/bp3d/FJ/FJ1052.obj","ag_data/bp3d/FJ/FJ1052.obj");
#	rtn = od.booleanOperationRate(["/ext1/project/ag/ag1/htdocs/ag-renderer/art_file/FJ3157-0.obj"],["/ext1/project/ag/ag1/htdocs/ag-renderer/art_file/FJ3159-0.obj"]);
#	rtn = od.booleanOperationRate("art_file/DBCLS__FUJIEDA_120406_liver_divided01_obj/FJ1845.obj","art_file/DBCLS__FUJIEDA_120406_liver_divided01_obj/FJ1864.obj");
#	rtn = od.booleanOperationRate("art_file/DBCLS__FUJIEDA_120406_liver_divided01_obj/FJ1845.obj","art_file/DBCLS__FUJIEDA_120406_liver_divided01_obj/FJ1860.obj");
#	rtn = od.booleanOperationRate("art_file/DBCLS__FUJIEDA_120406_liver_divided01_obj/FJ1845.obj","art_file/DBCLS__FUJIEDA3.0/FJ192.obj");
#	rtn = od.booleanOperationRate("art_file/DBCLS__FUJIEDA_120406_liver_divided01_obj/FJ1845.obj","art_file/DBCLS__FUJIEDA_liver_obj_120301/FJ2403.obj");
#	rtn = od.booleanOperationRate("art_file/DBCLS__FUJIEDA_120628-skin-obj/FJ2814.obj","art_file/DBCLS__FUJIEDA3.0/FJ391.obj");

#	rtn = od.reflection("art_file/DBCLS__FUJIEDA_120914_blood vessels-Trunk_obj_renal vesels/FJ3472.obj","FJ3472M");

#	rtn = od.cleanPolyData("test/exporterasInch.obj","test/test");
#	rtn = od.cleanPolyData("test/test.obj","test/test2");
	rtn = od.cleanPolyData("test/aaa.obj","test/test2");

	rtn = od.massProperties("test/130820_thyroid gland_thyroid gland.obj");
#	rtn = od.massProperties("test/exporterasInch.obj");

#	print str(inspect.currentframe().f_lineno)+"::"+str(rtn)
