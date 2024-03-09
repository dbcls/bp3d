#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import vtk
import os
import signal
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
import math

#import numpy

#import PythonMagick
#import wand.image

class OBJ2IMAGE:

	def __init__(self,OBJS,useRenderer=1,size = (500,500),maxAzimuth=72):

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
#		self.def_opacity = 0

		self.def_focus_color = (1,0,0)
		self.def_focus_opacity = 1.0

#		self.def_size = (500,500)
		self.def_size = size
#		print "__init__():START:"+str(self.def_size)

		self.def_max_azimuth = maxAzimuth

		self.color = copy.copy(self.def_color)
		self.bkcolor = copy.copy(self.def_bkcolor)
		self.focus_color = copy.copy(self.def_focus_color)
		self.size = copy.copy(self.def_size)


		self.actors = {}
		self.OBJS = OBJS;

#		self.vtkOffScreenRendering = 1;

		if useRenderer:

#			if self.vtkOffScreenRendering:
#				self.vtkGraphicsFactory = vtk.vtkGraphicsFactory()
#				self.vtkGraphicsFactory.SetOffScreenOnlyMode(1)
#				self.vtkGraphicsFactory.SetUseMesaClasses(1)

#				self.vtkImagingFactory = vtk.vtkImagingFactory()
#				self.vtkImagingFactory.SetUseMesaClasses(1)

			self.vtkRenderer = vtk.vtkRenderer()
			self.vtkRenderWindow = vtk.vtkRenderWindow()
#			if self.vtkOffScreenRendering:
#				self.vtkRenderWindow.SetOffScreenRendering(1)
			self.vtkRenderWindow.SetAlphaBitPlanes(1)
			self.vtkRenderWindow.AddRenderer(self.vtkRenderer)
			self.vtkRenderer.SetBackground(self.def_bkcolor)

			self.vtkCamera = vtk.vtkCamera()
			self.vtkRenderer.SetActiveCamera(self.vtkCamera)

			self.vtkPNGWriter = vtk.vtkPNGWriter()
#			self.vtkPNGWriter.SetCompressionLevel(0)

#		signal.signal(signal.SIGHUP,  self.signal_handler)
		signal.signal(signal.SIGINT,  self.signal_handler)
#		signal.signal(signal.SIGQUIT, self.signal_handler)
#		signal.signal(signal.SIGILL,  self.signal_handler)
#		signal.signal(signal.SIGTRAP, self.signal_handler)
#		signal.signal(signal.SIGABRT, self.signal_handler)
#		signal.signal(signal.SIGBUS,  self.signal_handler)
#		signal.signal(signal.SIGFPE,  self.signal_handler)
#		signal.signal(signal.SIGKILL, self.signal_handler)
#		signal.signal(signal.SIGTERM, self.signal_handler)
#		signal.signal(signal.SIGUSR1, self.signal_handler)
#		signal.signal(signal.SIGUSR2, self.signal_handler)
#		signal.signal(signal.SIGSEGV, self.signal_handler)

#		print "__init__():END:"+str(inspect.currentframe().f_lineno)

	def signal_handler(self,signal,frame):
		sys.exit(0)

	def objDeleteAll(self):
		self.OBJS.objDeleteAll();

	def setSize(self,size = (500,500)):
		if isinstance(size[0],int)==False:
			size[0] = int(size[0])
		if isinstance(size[1],int)==False:
			size[1] = int(size[1])
		self.def_size = size

	def setFocusColor(self,color = (1,0,0)):
		if isinstance(color[0],float)==False:
			color[0] = float(color[0])
		if isinstance(color[1],float)==False:
			color[1] = float(color[1])
		if isinstance(color[2],float)==False:
			color[2] = float(color[2])
		self.focus_color = color

	def resetFocusColor(self):
		self.focus_color = copy.copy(self.def_focus_color)

	def setColor(self,color = (1,0,0)):
		if isinstance(color[0],float)==False:
			color[0] = float(color[0])
		if isinstance(color[1],float)==False:
			color[1] = float(color[1])
		if isinstance(color[2],float)==False:
			color[2] = float(color[2])
		self.color = color

	def resetColor(self):
		self.color = copy.copy(self.def_color)

	def getMaxAzimuth(self):
		return self.def_max_azimuth

	def getSize(self):
#		print "getSize():"+str(inspect.currentframe().f_lineno)+":"+str(self.def_size)
		return self.def_size

	def objReader(self,filename):
		return self.OBJS.objReader(filename);

	def obj2actor(self,file,color,opacity=1.0):

#		print "obj2actor():START:"+str(inspect.currentframe().f_lineno)

		filename = None
		actor_color = copy.copy(color)
		actor_opacity = opacity

		if isinstance(file,str) or isinstance(file,unicode):
			filename = file
		elif isinstance(file,dict):
			if file.has_key('path') and (isinstance(file['path'],str) or isinstance(file['path'],unicode)):
				filename = file['path']
			if file.has_key('color') and (isinstance(file['color'],tuple) or isinstance(file['color'],list)):
				actor_color = copy.copy(file['color'])
#			else:
#				print "obj2actor()::"+str(inspect.currentframe().f_lineno)+"::"+str(type(file['color']))+"::"+str(file['color'])
#				pass

			if file.has_key('opacity') and (isinstance(file['opacity'],int) or isinstance(file['opacity'],float)):
				actor_opacity = float(file['opacity'])
			pass

		if filename == None:
			return None


		if self.actors.has_key(filename) != True:
			object = self.objReader(filename)

			mapper = vtk.vtkPolyDataMapper()
			mapper.SetInputConnection(object.GetOutputPort())

			self.actors[filename] = vtk.vtkActor()
			self.actors[filename].SetMapper(mapper)

		self.actors[filename].GetProperty().SetColor(actor_color)
		self.actors[filename].GetProperty().SetOpacity(actor_opacity)

#		print "obj2actor():END:"+str(inspect.currentframe().f_lineno)

		return self.actors[filename]


	def objs2actor(self,files,color,opacity=1.0):

		#複数のポリゴンを一つに纏める
		appendPolyData = vtk.vtkAppendPolyData()

		for file in files:
			object = self.objReader(file)
			appendPolyData.AddInputConnection(object.GetOutputPort())

		appendPolyData.Update()

		#ポイントを複製マージ、および/または未使用のポイント/を削除するか、または細胞を退化削除
		cleanPolyData = vtk.vtkCleanPolyData()
		cleanPolyData.SetInputConnection(appendPolyData.GetOutputPort())
		cleanPolyData.Update()

		cleanPolyDataNormals = vtk.vtkPolyDataNormals()
		cleanPolyDataNormals.SetInputConnection(cleanPolyData.GetOutputPort())
		cleanPolyDataNormals.ComputePointNormalsOn()
		cleanPolyDataNormals.Update()

		smoother = vtk.vtkSmoothPolyDataFilter()
		smoother.SetInputConnection(cleanPolyData.GetOutputPort())
		smoother.FeatureEdgeSmoothingOn()
		smoother.Update()

		smootherNormals = vtk.vtkPolyDataNormals()
		smootherNormals.SetInputConnection(smoother.GetOutputPort())
		smootherNormals.ComputePointNormalsOn()
		smootherNormals.Update()

		objectMapper = vtk.vtkPolyDataMapper()
		objectMapper.SetInputConnection(smootherNormals.GetOutputPort())

		actor = vtk.vtkActor()
		actor.SetMapper(objectMapper)

		actor.GetProperty().SetColor(color)
		actor.GetProperty().SetOpacity(opacity)

		return actor


	def removeActors(self):
		for k in self.actors.keys():
			self.vtkRenderer.RemoveActor(self.actors[k])

	def get_camera(self,fontBounds,backBounds,yRange):
		camera = self.vtkCamera
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



	def get_image(self,azimuth,fontBounds,backBounds,yRange,prefix,largerbbox,largerbboxYRange):

#		print "get_image():START:"+str(inspect.currentframe().f_lineno)

		self.vtkRenderWindow.SetSize(self.def_size)

		self.get_camera(fontBounds,backBounds,yRange)
		self.vtkCamera.Azimuth( azimuth )		#Z軸回転

#		print "get_image()::"+str(inspect.currentframe().f_lineno)


		renderLargeImg = vtk.vtkRenderLargeImage()
		renderLargeImg.SetInput(self.vtkRenderer)
		renderLargeImg.SetMagnification(1)

#		print "get_image()::"+str(inspect.currentframe().f_lineno)

#		target_file = os.path.join("/tmp",str(os.getpid())+"-target.png")
#		larger_file = os.path.join("/tmp",str(os.getpid())+"-larger.png")

		target_file = prefix+"-target.png"
		larger_file = prefix+"-larger.png"

#		print "get_image()::"+str(inspect.currentframe().f_lineno)

		self.vtkPNGWriter.SetFileName(target_file)
		self.vtkPNGWriter.SetInputConnection(renderLargeImg.GetOutputPort())
		self.vtkPNGWriter.Write()

#		print "get_image()::"+str(inspect.currentframe().f_lineno)

		if largerbbox:
			larger_size = int(self.def_size[0]*0.4);
#			self.vtkRenderWindow.SetSize([larger_size,larger_size])

			self.get_camera(largerbbox,backBounds,largerbboxYRange)
			self.vtkCamera.Azimuth( azimuth )		#Z軸回転

#			print "get_image()::"+str(inspect.currentframe().f_lineno)

			renderLargeImg = vtk.vtkRenderLargeImage()
			renderLargeImg.SetInput(self.vtkRenderer)
			renderLargeImg.SetMagnification(1)

#			print "get_image()::"+str(inspect.currentframe().f_lineno)

			self.vtkPNGWriter.SetFileName(larger_file)
			self.vtkPNGWriter.SetInputConnection(renderLargeImg.GetOutputPort())
			self.vtkPNGWriter.Write()

#			print "get_image()::"+str(inspect.currentframe().f_lineno)

#			cmd = 'mogrify -transparent white ' +  larger_file
#			subprocess.call(cmd, shell=True)

			cmd = 'mogrify -transparent white -geometry ' + str(larger_size) + 'x' + str(larger_size) + ' -sharpen 0.7 ' + larger_file
			subprocess.call(cmd, shell=True)

			cmd = 'composite -gravity southeast '+ larger_file + ' ' + target_file + ' png8:' + prefix + '.png'
			subprocess.call(cmd, shell=True)

		else:
			cmd = 'convert '+ target_file + ' png8:' + prefix + '.png'
			subprocess.call(cmd, shell=True)

		if larger_file and os.path.exists(larger_file) and os.path.isfile(larger_file):
			os.remove(larger_file)

		if os.path.exists(target_file) and os.path.isfile(target_file):
			os.remove(target_file)

#		print "get_image():END:"+str(inspect.currentframe().f_lineno)


	def get_target_image(self,azimuth,fontBounds,backBounds,yRange,prefix):

#		print "get_target_image():START:"+str(inspect.currentframe().f_lineno)

		self.get_camera(fontBounds,backBounds,yRange)
		self.vtkCamera.Azimuth( azimuth )		#Z軸回転

#		print "get_target_image()::"+str(inspect.currentframe().f_lineno)

		target_file = None
		if prefix:
			target_file = prefix+"-target.png"

#		print "get_target_image()::"+str(inspect.currentframe().f_lineno)

		renderLargeImg = vtk.vtkRenderLargeImage()
		renderLargeImg.SetInput(self.vtkRenderer)
		renderLargeImg.SetMagnification(1)

		self.vtkPNGWriter.SetInputConnection(renderLargeImg.GetOutputPort())
		if target_file:
			self.vtkPNGWriter.SetFileName(target_file)
		else:
			self.vtkPNGWriter.WriteToMemoryOn()
		self.vtkPNGWriter.Write()
		if target_file==None:
			target_file = buffer(self.vtkPNGWriter.GetResult())

#		print "get_target_image():END:"+str(inspect.currentframe().f_lineno)

		return target_file


	def get_larger_image(self,azimuth,largerbbox,backBounds,largerbboxYRange,prefix):

#		print "get_image():START:"+str(inspect.currentframe().f_lineno)

		larger_file = None
		if prefix:
			larger_file = prefix+"-larger.png"

#		print "get_image()::"+str(inspect.currentframe().f_lineno)

		larger_size = int(self.def_size[0]*0.4);

		self.get_camera(largerbbox,backBounds,largerbboxYRange)
		self.vtkCamera.Azimuth( azimuth )		#Z軸回転

#			print "get_image()::"+str(inspect.currentframe().f_lineno)

		renderLargeImg = vtk.vtkRenderLargeImage()
		renderLargeImg.SetInput(self.vtkRenderer)
		renderLargeImg.SetMagnification(1)

		self.vtkPNGWriter.SetInputConnection(renderLargeImg.GetOutputPort())
		if larger_file:
			self.vtkPNGWriter.SetFileName(larger_file)
		else:
			self.vtkPNGWriter.WriteToMemoryOn()
		self.vtkPNGWriter.Write()
		if larger_file==None:
			larger_file = buffer(self.vtkPNGWriter.GetResult())

#			print "get_image()::"+str(inspect.currentframe().f_lineno)

#		cmd = 'mogrify -transparent white -geometry ' + str(larger_size) + 'x' + str(larger_size) + ' -sharpen 0.7 ' + larger_file
#		subprocess.call(cmd, shell=True)

#		print "get_image():END:"+str(inspect.currentframe().f_lineno)

		return larger_file


	def bound(self,obj_files):

#		print "bound():START:"+str(inspect.currentframe().f_lineno)

		if obj_files:
			appendPolyData = vtk.vtkAppendPolyData()
			for file in obj_files:
				if isinstance(file,str) or isinstance(file,unicode):
					appendPolyData.AddInputConnection(self.objReader(file).GetOutputPort())
				elif isinstance(file,dict) and file.has_key('path') and (isinstance(file['path'],str) or isinstance(file['path'],unicode)):
					appendPolyData.AddInputConnection(self.objReader(file['path']).GetOutputPort())
				else:
					if sys.version_info.major == 3:
						print("bound():PROC:"+str(inspect.currentframe().f_lineno)+":"+str(isinstance(file,str)))
						print("bound():PROC:"+str(inspect.currentframe().f_lineno)+":"+str(isinstance(file,dict)))
						print("bound():PROC:"+str(inspect.currentframe().f_lineno)+":"+str(isinstance(file,tuple)))
						print("bound():PROC:"+str(inspect.currentframe().f_lineno)+":"+str(isinstance(file,list)))
						if isinstance(file,dict):
							print("bound():PROC:"+str(inspect.currentframe().f_lineno)+":"+str(file.has_key('path')))
							print("bound():PROC:"+str(inspect.currentframe().f_lineno)+":"+str(isinstance(file['path'],unicode)))
							print("bound():PROC:"+str(inspect.currentframe().f_lineno)+":"+str(file['path']))
					elif sys.version_info.major == 2:
						print "bound():PROC:"+str(inspect.currentframe().f_lineno)+":"+str(isinstance(file,str))
						print "bound():PROC:"+str(inspect.currentframe().f_lineno)+":"+str(isinstance(file,dict))
						print "bound():PROC:"+str(inspect.currentframe().f_lineno)+":"+str(isinstance(file,tuple))
						print "bound():PROC:"+str(inspect.currentframe().f_lineno)+":"+str(isinstance(file,list))
						if isinstance(file,dict):
							print "bound():PROC:"+str(inspect.currentframe().f_lineno)+":"+str(file.has_key('path'))
							print "bound():PROC:"+str(inspect.currentframe().f_lineno)+":"+str(isinstance(file['path'],unicode))
							print "bound():PROC:"+str(inspect.currentframe().f_lineno)+":"+str(file['path'])

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

		#対象のオブジェクトを読み込む
		for file in obj_files1:
			self.vtkRenderer.AddActor(self.obj2actor(file,self.focus_color,self.def_focus_opacity))
#		self.vtkRenderer.AddActor(self.objs2actor(obj_files1,self.focus_color,self.def_focus_opacity))

#		print "animgif()::"+str(inspect.currentframe().f_lineno)

		if obj_files2:
			for file in obj_files2:
				self.vtkRenderer.AddActor(self.obj2actor(file,self.color,self.def_opacity))
#			self.vtkRenderer.AddActor(self.objs2actor(obj_files2,self.color,self.def_opacity))

#		print "animgif()::"+str(inspect.currentframe().f_lineno)

		fontBounds = self.bound(obj_files1)
		backBounds = self.bound(obj_files2)
		if backBounds==None:
			backBounds = copy.deepcopy(fontBounds)

#		print "animgif()::"+str(inspect.currentframe().f_lineno)

		png_files = []
		target_png_files = []
		larger_png_files = []

#		print "animgif()::"+str(inspect.currentframe().f_lineno)

		self.vtkRenderWindow.SetSize(self.def_size)

		for azimuth in range(0,self.def_max_azimuth):
			angle = azimuth * (360/self.def_max_azimuth) #5
			prefix = None
			if dest_prefix:
				prefix = dest_prefix+"-"+str(angle)
			target_file = self.get_target_image(angle,fontBounds,backBounds,yRange,prefix)
			target_png_files.append(target_file)
#			if largerbbox:
#				target_png_files.append(target_file)
#			else:
#				file = prefix+".png"
#				cmd = 'convert '+ target_file + ' png8:' + file
#				subprocess.call(cmd, shell=True)
#				if os.path.exists(file) and os.path.isfile(file):
#					png_files.append(file)
#					os.remove(target_file)

		if largerbbox:
			idx=0
			for azimuth in range(0,self.def_max_azimuth):
				angle = azimuth * (360/self.def_max_azimuth) #5
				prefix = None
				if dest_prefix:
					prefix = dest_prefix+"-"+str(angle)
				larger_file = self.get_larger_image(angle,largerbbox,backBounds,largerbboxYRange,prefix)
				larger_png_files.append(larger_file)
#				if larger_file and os.path.exists(larger_file) and os.path.isfile(larger_file) and target_png_files[idx] and os.path.exists(target_png_files[idx]) and os.path.isfile(target_png_files[idx]):
#					file = prefix+".png"
#					cmd = 'composite -gravity southeast '+ larger_file + ' ' + target_png_files[idx] + ' png8:' + file
#					subprocess.call(cmd, shell=True)
#					if os.path.exists(file) and os.path.isfile(file):
#						png_files.append(file)
#						os.remove(larger_file)
#						os.remove(target_png_files[idx])
#				idx += 1

#		print "animgif()::"+str(inspect.currentframe().f_lineno)

		self.removeActors()

#		print "animgif()::"+str(inspect.currentframe().f_lineno)

#		gif_file = dest_prefix+".gif"
#		cmd = 'convert -dispose Background -delay 0 -loop 0 ' + ' '.join(png_files) + ' ' + gif_file
#		subprocess.call(cmd, shell=True)

#		print "animgif()::"+str(inspect.currentframe().f_lineno)

#		if os.path.exists(gif_file) and os.path.isfile(gif_file):
#			png_files.insert(0,gif_file)

#		print "animgif():END:"+str(inspect.currentframe().f_lineno)

		png_files.append(target_png_files)
		png_files.append(larger_png_files)

		return png_files



	def png(self,obj_files1,obj_files2,dest_prefix,angle,yRange,largerbbox,largerbboxYRange):

#		print "png():START:"+str(inspect.currentframe().f_lineno)

		#対象のオブジェクトを読み込む
		for file in obj_files1:
			self.vtkRenderer.AddActor(self.obj2actor(file,self.focus_color,self.def_focus_opacity))

#		print "png()::"+str(inspect.currentframe().f_lineno)

		#その他のオブジェクトはフォーカス後に読み込む
		if obj_files2:
			for file in obj_files2:
				self.vtkRenderer.AddActor(self.obj2actor(file,self.color,self.def_opacity))

#		print "png()::"+str(inspect.currentframe().f_lineno)

		fontBounds = self.bound(obj_files1)
		backBounds = self.bound(obj_files2)
		if backBounds==None:
			backBounds = copy.deepcopy(fontBounds)

#		print "png()::"+str(inspect.currentframe().f_lineno)

		prefix = None
		if dest_prefix:
			prefix = dest_prefix+"-"+str(angle)
#		file = prefix+".png"
#		self.get_image(angle,fontBounds,backBounds,yRange,prefix,largerbbox,largerbboxYRange)

		png_files = []
		self.vtkRenderWindow.SetSize(self.def_size)

		target_file = self.get_target_image(angle,fontBounds,backBounds,yRange,prefix)
		if target_file:
#		if os.path.exists(target_file) and os.path.isfile(target_file):
			png_files.append(target_file)

		if largerbbox:
			larger_file = self.get_larger_image(angle,largerbbox,backBounds,largerbboxYRange,prefix)
			if os.path.exists(larger_file) and os.path.isfile(larger_file):
				png_files.append(larger_file)


#		print "png()::"+str(inspect.currentframe().f_lineno)

		self.removeActors()

#		print "png():END:"+str(inspect.currentframe().f_lineno)

		return png_files

	def obj2animgif(self,size,obj_files1,obj_files2,dest_prefix,yRange,largerbbox,largerbboxYRange):
#		print "obj2animgif():START:"+str(inspect.currentframe().f_lineno)
		self.setSize(size)
		rtn = self.animgif(obj_files1,obj_files2,dest_prefix,yRange,largerbbox,largerbboxYRange)
#		print "obj2animgif():END:"+str(inspect.currentframe().f_lineno)

#		print "obj2animgif()::"+str(inspect.currentframe().f_lineno)+'::rtn='+str(len(rtn))

#		if rtn and isinstance(rtn,list) and len(rtn)==2 and isinstance(rtn[0],list) and len(rtn[0])>0 and isinstance(rtn[0][0],str)==False:
#			for i in range(len(rtn)):
#				for j in range(len(rtn[i])):
#					pngs = []
#					for k in range(rtn[i][j].GetNumberOfTuples()):
#						pngs.append(chr(int(rtn[i][j].GetComponent(j,k))))
#					rtn[i][j] = ''.join(pngs)
		return rtn

	def obj2png(self,size,obj_files1,obj_files2,dest_prefix,angle,yRange,largerbbox,largerbboxYRange):
#		print "obj2png():START:"+str(inspect.currentframe().f_lineno)
		self.setSize(size)
		rtn = self.png(obj_files1,obj_files2,dest_prefix,angle,yRange,largerbbox,largerbboxYRange)
#		print "obj2png():END:"+str(inspect.currentframe().f_lineno)

#		if rtn and isinstance(rtn,list) and len(rtn)==1 and isinstance(rtn[0],str)==False:
#			pngs = [];
#			for i in range(rtn[0].GetNumberOfTuples()):
#				pngs.append(chr(int(rtn[0].GetComponent(0,i))));
#			rtn = None;
#			rtn = ''.join(pngs)

		return rtn



#'''
if __name__ == "__main__":
#	version = vtk.vtkVersion()
#	print "VTK_VERSION:"+version.GetVTKVersion()

#	test_dict_1 = {'YEAR':'2010','MONTH':'1','DAY':'20'}
#	if isinstance(test_dict_1,dict):
#		print "main()::"+str(inspect.currentframe().f_lineno)+'::test_dict_1='+str(type(test_dict_1))

#	def_size = (500,500)
#	print "main()::"+str(inspect.currentframe().f_lineno)+'::def_size='+str(type(def_size))


	from bp3d_objs import BP3D_OBJS
	import glob

	DEF_HEIGHT = 1800
	def getZoomYRange(zoom):
		return max(1,round( math.exp(1) ** ((math.log(DEF_HEIGHT)/math.log(2)-zoom) * math.log(2)) ))

	def getYRangeZoom(yrange):
		return round((math.log(DEF_HEIGHT)/math.log(2) - math.log(yrange)/math.log(2)) * 10) / 10

	bo = BP3D_OBJS()
	files = glob.glob('../art_file/*.obj')
	for file in files:
#		print file
		bo.objReader(file)


	obj_files1 = [{'path':'../art_file/FJ1451.obj'},{'path':'../art_file/FJ1451M.obj'}]

	oi = OBJ2IMAGE(bo,1);

	
#	print "main()::"+str(inspect.currentframe().f_lineno)+'::focus_color='+str(copy.copy(oi.def_focus_color))
#	exit



	b1 = oi.bound(obj_files1);
	if sys.version_info.major == 3:
		print("main()::"+str(inspect.currentframe().f_lineno)+'::b1='+str(b1))
	elif sys.version_info.major == 2:
		print "main()::"+str(inspect.currentframe().f_lineno)+'::b1='+str(b1)

	b1max = max(abs(b1[0]-b1[1]),abs(b1[2]-b1[3]),abs(b1[4]-b1[5]));
	if sys.version_info.major == 3:
		print("main()::"+str(inspect.currentframe().f_lineno)+'::b1max='+str(b1max))
	elif sys.version_info.major == 2:
		print "main()::"+str(inspect.currentframe().f_lineno)+'::b1max='+str(b1max)

	b1zoom = getYRangeZoom(b1max);
	if sys.version_info.major == 3:
		print("main()::"+str(inspect.currentframe().f_lineno)+'::b1zoom='+str(b1zoom))
	elif sys.version_info.major == 2:
		print "main()::"+str(inspect.currentframe().f_lineno)+'::b1zoom='+str(b1zoom)

	if b1zoom>0:
		b1zoom1 =  b1zoom-0.1
	else:
		b1zoom1 =  b1zoom

	if sys.version_info.major == 3:
		print("main()::"+str(inspect.currentframe().f_lineno)+'::b1zoom1='+str(b1zoom1))
	elif sys.version_info.major == 2:
		print "main()::"+str(inspect.currentframe().f_lineno)+'::b1zoom1='+str(b1zoom1)

	b1YRange = getZoomYRange(b1zoom1);
	if sys.version_info.major == 3:
		print("main()::"+str(inspect.currentframe().f_lineno)+'::b1YRange='+str(b1YRange))
	elif sys.version_info.major == 2:
		print "main()::"+str(inspect.currentframe().f_lineno)+'::b1YRange='+str(b1YRange)

#	dest_prefix = '/bp3d/ag-renderer/htdocs/tmp/FJ1451'
	dest_prefix = None
	size = [640,640]

	imgs =oi.obj2png(size,obj_files1,None,dest_prefix,0,b1YRange,None,None)
	if sys.version_info.major == 3:
		print(imgs)
	elif sys.version_info.major == 2:
		print imgs

#	imgs = oi.obj2animgif(size,obj_files1,None,dest_prefix,b1YRange,None,None)
#	print "main()::"+str(inspect.currentframe().f_lineno)+'::imgs='+str(imgs)
#	print "main()::"+str(inspect.currentframe().f_lineno)+'::imgs='+str(type(imgs))
#	print imgs

#	if isinstance(imgs,list):
	

#	if imgs and isinstance(imgs,list) and len(imgs)==1 and isinstance(imgs[0],str)==False:
#		print "main()::"+str(inspect.currentframe().f_lineno)+'::imgs='+str(len(imgs))
#		print "main()::"+str(inspect.currentframe().f_lineno)+'::imgs='+str(imgs[0])

#		print "main()::"+str(inspect.currentframe().f_lineno)+'::imgs='+str(type(imgs[0]))
#		print "main()::"+str(inspect.currentframe().f_lineno)+'::GetSize='+str(imgs[0].GetSize())
#		print "main()::"+str(inspect.currentframe().f_lineno)+'::GetDataSize='+str(imgs[0].GetDataSize())
#		print "main()::"+str(inspect.currentframe().f_lineno)+'::GetDataType='+str(imgs[0].GetDataType())
#		print "main()::"+str(inspect.currentframe().f_lineno)+'::GetArrayType='+str(imgs[0].GetArrayType())
#		print "main()::"+str(inspect.currentframe().f_lineno)+'::GetRange='+str(imgs[0].GetRange())
#		print "main()::"+str(inspect.currentframe().f_lineno)+'::GetDataTypeValueMin='+str(imgs[0].GetDataTypeValueMin())
#		print "main()::"+str(inspect.currentframe().f_lineno)+'::GetDataTypeValueMax='+str(imgs[0].GetDataTypeValueMax())
#		print "main()::"+str(inspect.currentframe().f_lineno)+'::GetDataTypeMin='+str(imgs[0].GetDataTypeMin())
#		print "main()::"+str(inspect.currentframe().f_lineno)+'::GetDataTypeMax='+str(imgs[0].GetDataTypeMax())
#		print "main()::"+str(inspect.currentframe().f_lineno)+'::GetNumberOfTuples='+str(imgs[0].GetNumberOfTuples())
#		print "main()::"+str(inspect.currentframe().f_lineno)+'::GetNumberOfComponents='+str(imgs[0].GetNumberOfComponents())
#		print "main()::"+str(inspect.currentframe().f_lineno)+'::GetComponent='+str(imgs[0].GetComponent(0,0))
#		print "main()::"+str(inspect.currentframe().f_lineno)+'::GetTuple='+str(imgs[0].GetTuple(0))

#		pngs = [];
#		for i in range(0,imgs[0].GetNumberOfTuples()):
#			print "main()::"+str(inspect.currentframe().f_lineno)+'::GetTuple('+str(i)+')='+str(imgs[0].GetTuple(i))
#			print "main()::"+str(inspect.currentframe().f_lineno)+'::GetComponent('+str(i)+')='+str(imgs[0].GetComponent(0,i))
#			print "main()::"+str(inspect.currentframe().f_lineno)+'::GetTuple='+str(len(imgs[0].GetTuple(i)))
#			print "main()::"+str(inspect.currentframe().f_lineno)+'::GetTuple='+str(chr(int(imgs[0].GetTuple(i)[0])))
#			pngs.append(chr(int(imgs[0].GetTuple(i)[0])));
#			pngs.append(chr(int(imgs[0].GetComponent(0,i))));

#		print ''.join(pngs)


#'''
