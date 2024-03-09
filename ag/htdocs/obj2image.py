#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import vtk
import os
import sys
#import os.path
#import glob
import time
import tempfile
#import PythonMagick
import subprocess
import shlex
import inspect
import shutil
import copy

class obj2image:

	def __init__(self,size = (500,500)):

#		print "__init__():START:"+str(inspect.currentframe().f_lineno)

		self.def_position = [2.7979888916016167, -998.4280435445771, 809.7306805551052]
		self.def_focalpoint = [2.7979888916015625, -110.37168800830841, 809.7306805551052]
		self.def_viewup = [0,0,1]
		self.def_cliprange = [0.01,1800]
		self.def_height = 1684.3185
		self.def_scale = 900

		self.def_color = (0.94,0.82,0.62)
		self.def_bkcolor = (1,1,1)
		self.def_opacity = 0.05
		self.def_opacity = 0

		self.def_focus_color = (1,0,0)
		self.def_focus_opacity = 1.0

#		self.def_size = (500,500)
		self.def_size = size

		self.objects = {}
		self.actors = {}

#		print "__init__():END:"+str(inspect.currentframe().f_lineno)


	def objDeleteAll(self):
		for k in self.objects.keys():
			del self.objects[k]

	def setSize(self,size = (500,500)):
		if isinstance(size[0],int)==False:
			size[0] = int(size[0])
		if isinstance(size[1],int)==False:
			size[1] = int(size[1])
		self.def_size = size

	def setColor(self,color = (1,0,0)):
		if isinstance(color[0],float)==False:
			color[0] = float(color[0])
		if isinstance(color[1],float)==False:
			color[1] = float(color[1])
		if isinstance(color[2],float)==False:
			color[2] = float(color[2])
		self.def_focus_color = color

	def objReader(self,filename):

#		print "objReader():START:"+str(inspect.currentframe().f_lineno)

		if self.objects.has_key(filename) != True:
			self.objects[filename] = vtk.vtkOBJReader()
			self.objects[filename].SetFileName(filename)

#		print "objReader():END:"+str(inspect.currentframe().f_lineno)

		return self.objects[filename];

	def obj2actor(self,filename,color,opacity=1.0):

#		print "obj2actor():START:"+str(inspect.currentframe().f_lineno)

		if self.actors.has_key(filename) != True:
			object = self.objReader(filename)

			mapper = vtk.vtkPolyDataMapper()
			mapper.SetInputConnection(object.GetOutputPort())

			self.actors[filename] = vtk.vtkActor()
			self.actors[filename].SetMapper(mapper)

		self.actors[filename].GetProperty().SetColor(color)
		self.actors[filename].GetProperty().SetOpacity(opacity)

#		print "obj2actor():END:"+str(inspect.currentframe().f_lineno)

		return self.actors[filename]

	def get_camera(self,camera,fontBounds,backBounds,yRange):

#		print "get_camera():START:"+str(inspect.currentframe().f_lineno)

#		fmax = 0
#		if max_flag:
#			fmax = max(abs(fontBounds[0]-fontBounds[1]),abs(fontBounds[2]-fontBounds[3]),abs(fontBounds[4]-fontBounds[5]))
#		else:
#			fmax = abs(fontBounds[4]-fontBounds[5])*1.2
#		bmax = max(abs(backBounds[0]-backBounds[1]),abs(backBounds[2]-backBounds[3]),abs(backBounds[4]-backBounds[5]))

#		scale = fmax*self.def_scale/bmax
		scale = yRange/2
#		print "get_camera():scale=["+str(scale)+"]:"+str(inspect.currentframe().f_lineno)
		focalpoint = ((fontBounds[0]+fontBounds[1])/2,(fontBounds[2]+fontBounds[3])/2,(fontBounds[4]+fontBounds[5])/2)
		position = (focalpoint[0],focalpoint[1]-(self.def_focalpoint[1]-self.def_position[1]),focalpoint[2])

		camera.SetParallelProjection(1);
		camera.SetParallelScale(scale);
		camera.SetPosition(position)
		camera.SetFocalPoint(focalpoint)
		camera.SetViewUp(self.def_viewup)
		camera.SetClippingRange(self.def_cliprange)

#		print "get_camera():END:"+str(inspect.currentframe().f_lineno)

		return camera



	def get_image(self,camera,renWin,azimuth,fontBounds,backBounds,yRange,image_file,largerbbox,largerbboxYRange):

#		print "get_image():START:"+str(inspect.currentframe().f_lineno)

		renWin.SetSize(self.def_size)

		self.get_camera(camera,fontBounds,backBounds,yRange)
		camera.Azimuth( azimuth )		#Z軸回転

		win2if = vtk.vtkWindowToImageFilter()
		win2if.SetInput(renWin)
#			win2if.SetInputBufferTypeToRGBA()	#背景を透過にする
		win2if.Update()

		target_file = os.path.join("/tmp",str(os.getpid())+"-target.png")
		larger_file = None

		writer = vtk.vtkPNGWriter()
		writer.SetFileName(target_file)
		writer.SetInputConnection(win2if.GetOutputPort())
		writer.Write()

		if largerbbox:
			larger_size = int(self.def_size[0]*0.4);
			renWin.SetSize([larger_size,larger_size])

			self.get_camera(camera,largerbbox,backBounds,largerbboxYRange)
			camera.Azimuth( azimuth )		#Z軸回転

			win2if = vtk.vtkWindowToImageFilter()
			win2if.SetInput(renWin)
#				win2if.SetInputBufferTypeToRGBA()	#背景を透過にする
			win2if.Update()

			writer = vtk.vtkPNGWriter()
			writer.SetFileName(larger_file)
			writer.SetInputConnection(win2if.GetOutputPort())
			writer.Write()

			cmd = 'mogrify -transparent white ' +  larger_file
			subprocess.call(cmd, shell=True)

			cmd = 'composite -gravity southeast '+ larger_file + ' ' + target_file + ' png8:' + image_file
			subprocess.call(cmd, shell=True)

		else:
			cmd = 'convert '+ target_file + ' png8:' + image_file
			subprocess.call(cmd, shell=True)

		if larger_file and os.path.exists(larger_file) and os.path.isfile(larger_file):
			os.remove(larger_file)

		if os.path.exists(target_file) and os.path.isfile(target_file):
			os.remove(target_file)

#		print "get_image():END:"+str(inspect.currentframe().f_lineno)




	def bound(self,obj_files):

#		print "bound():START:"+str(inspect.currentframe().f_lineno)

		if obj_files:
			appendPolyData = vtk.vtkAppendPolyData()
			for file in obj_files:
				appendPolyData.AddInputConnection(self.objReader(file).GetOutputPort())

			appendPolyData.Update()
			polyData = vtk.vtkPolyData()
			polyData.ShallowCopy(appendPolyData.GetOutput())

#			print "bound():END:"+str(inspect.currentframe().f_lineno)
			return polyData.GetBounds()

		else:
#			print "bound():END:"+str(inspect.currentframe().f_lineno)
			return None

	def animgif(self,obj_files1,obj_files2,dest_prefix,yRange,largerbbox,largerbboxYRange):

#		print "animgif():START:"+str(inspect.currentframe().f_lineno)

		renWin = vtk.vtkRenderWindow()
		renWin.SetSize(self.def_size)
		renWin.SetAlphaBitPlanes(1)
#		renWin.SetAAFrames(10)
#		print renWin.GetAAFrames()
#		print renWin.GetFDFrames()
#		print renWin.GetMultiSamples()

		renderer = vtk.vtkRenderer()
		renWin.AddRenderer(renderer)
		renderer.SetBackground(self.def_bkcolor)
#		renderer.SetUseDepthPeeling(1)

		#とりあえず、対象のオブジェクトを読み込む
		for file in obj_files1:
			renderer.AddActor(self.obj2actor(file,self.def_focus_color,self.def_focus_opacity))

		#その他のオブジェクトはフォーカス後に読み込む
		if obj_files2:
			for file in obj_files2:
				renderer.AddActor(self.obj2actor(file,self.def_color,self.def_opacity))

		fontBounds = self.bound(obj_files1)
		backBounds = self.bound(obj_files2)
		if backBounds==None:
			backBounds = copy.deepcopy(fontBounds)

		camera = vtk.vtkCamera()
		renderer.SetActiveCamera(camera)

		tmp_files = []

		for azimuth in range(0,72):
			angle = azimuth * 5
			file = dest_prefix+"-"+str(angle)+".png"
#			print angle
			self.get_image(camera,renWin,angle,fontBounds,backBounds,yRange,file,largerbbox,largerbboxYRange)
			tmp_files.append(file);

		renWin.RemoveRenderer(renderer);
		renWin.Finalize();

#		cmd = 'mogrify -transparent white ' + ' '.join(self.tmp_files)	#白を透過にする
#		cmd = 'mogrify -transparent white -depth 8 -colors 256 ' + ' '.join(self.tmp_files)	#白を透過にする
#		subprocess.call(cmd, shell=True)

		giffile = dest_prefix+".gif"
		cmd = 'convert -dispose Background -delay 0 -loop 0 ' + ' '.join(tmp_files) + ' ' + giffile
		subprocess.call(cmd, shell=True)

		if os.path.exists(giffile) and os.path.isfile(giffile):
			tmp_files.insert(0,giffile)

#		print inspect.currentframe().f_lineno

#		print "animgif():END:"+str(inspect.currentframe().f_lineno)

		return tmp_files



	def png(self,obj_files1,obj_files2,dest_prefix,angle,yRange,largerbbox,largerbboxYRange):

#		print "png():START:"+str(inspect.currentframe().f_lineno)

		renWin = vtk.vtkRenderWindow()
		renWin.SetSize(self.def_size)
		renWin.SetAlphaBitPlanes(1)
#		renWin.SetAAFrames(10)

		renderer = vtk.vtkRenderer()
		renWin.AddRenderer(renderer)
		renderer.SetBackground(self.def_bkcolor)
#		renderer.SetUseDepthPeeling(1)


		#とりあえず、対象のオブジェクトを読み込む
		for file in obj_files1:
			renderer.AddActor(self.obj2actor(file,self.def_focus_color,self.def_focus_opacity))

		#その他のオブジェクトはフォーカス後に読み込む
		if obj_files2:
			for file in obj_files2:
				renderer.AddActor(self.obj2actor(file,self.def_color,self.def_opacity))

		fontBounds = self.bound(obj_files1)
		backBounds = self.bound(obj_files2)
		if backBounds==None:
			backBounds = copy.deepcopy(fontBounds)

		camera = vtk.vtkCamera()
		renderer.SetActiveCamera(camera)

		file = dest_prefix+"-"+str(angle)+".png"
		self.get_image(camera,renWin,angle,fontBounds,backBounds,yRange,file,largerbbox,largerbboxYRange)

#		print "png():END:"+str(inspect.currentframe().f_lineno)

		return [file]

'''
if __name__ == "__main__":
#	version = vtk.vtkVersion()
#	print "VTK_VERSION:"+version.GetVTKVersion()

	op = obj2image((500,500));

	op.animgif(['../ag_data/obj_3.0.1/FMA7274.obj'],['../ag_data/obj_3.0.1/FMA7163.obj'])

'''
