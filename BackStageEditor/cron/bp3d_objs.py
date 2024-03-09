#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import vtk

class BP3D_OBJS:
	def __init__(self):
		self.objects = {}

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

	def triangleFilter(self,object):
		#入力ポリゴンと三角形ストリップから三角形のポリゴンを作成する
		triangleFilter = vtk.vtkTriangleFilter()
		triangleFilter.SetInputConnection(object.GetOutputPort())
		triangleFilter.Update()
		return triangleFilter

	#ポリゴンを削減(vtkQuadricDecimation)
	def quadricDecimation(self,object,reduction=.9):
		return object
		if reduction == 1.0:
			return object

		#入力ポリゴンと三角形ストリップから三角形のポリゴンを作成する
		triangleFilter = self.triangleFilter(self.getPolyDataNormals(object))

		#ポリゴンを削減
		mesh = vtk.vtkQuadricDecimation()
		mesh.SetInputConnection(triangleFilter.GetOutputPort())
		mesh.SetTargetReduction(reduction)
		#mesh.AttributeErrorMetricOn()
		mesh.Update()

		return mesh

	def objReader(self,filename,reduction=.9):
		if self.objects.has_key(filename) != True:
			object = vtk.vtkOBJReader()
			object.SetFileName(filename)
			self.objects[filename] = self.quadricDecimation(object,reduction)
		return self.objects[filename];

	def objDeleteAll(self):
		for k in self.objects.keys():
			del self.objects[k]
