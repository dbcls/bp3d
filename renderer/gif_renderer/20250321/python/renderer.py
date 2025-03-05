# coding: utf-8

import sys
import os
#import platform
import pathlib
import json
import inspect
import math
import time
import glob
#import base64
import shutil
#import io
#import copy
#import signal
import re
#import subprocess
import psutil
from PIL import Image
#import gzip
import tempfile

#from vtk import (vtkSphereSource, vtkPolyDataMapper, vtkActor, vtkRenderer, vtkCoordinate,
#                 vtkRenderWindow, vtkWindowToImageFilter, vtkPNGWriter, vtkOBJReader, vtkDataEncoder,
#                 vtkAppendPolyData, vtkPolyData, vtkLookupTable, vtkScalarBarActor, vtkTransform, vtkTextActor, vtkPropPicker,vtkCellPicker, vtkArrowSource, vtkGlyph3D)

#from bottle import static_file
import numpy as np
import vtk
import imageio
import pyvista as pv
from pyvista.plotting.helpers import view_vectors
#from multiprocessing import Pool, cpu_count
import multiprocessing as mp

def is_num(s):
	try:
		float(s)
	except ValueError:
		return False
	else:
		return True

def is_str(v):
	return type(v) is str

class Renderer():
	def __init__(self, obj_path, json_path, images_path, size = [500,500], version = None, load_mesh = True, reduction = .0, debug = False):
		start_time = time.time()
		start = time.perf_counter()
		if debug:
			print("__init__():START:",inspect.currentframe().f_lineno, file=sys.stderr)

		pv.start_xvfb()
		self._plotter = None
		self._openPlotter(forced=True)


		#obj_file_path = pathlib.Path(obj_path)
		#obj_file_list = sorted(list(obj_file_path.glob('**/CX*.obj')))
		#print(l)

		self._debug = debug

		self._reduction = reduction

		self._obj_path = obj_path
		self._json_path = json_path
		self._images_path = images_path

		self._versions = []
		self._renderer_info_dict = {}
		self._mesh_dict = {}
		self._actor_dict = {}

		self._DEF_HEIGHT = 1800

		versions_file_path = os.path.join(json_path,'versions_file.json')
		if os.path.isfile(versions_file_path):
			if self._debug:
				print("__init__():EXEC:",inspect.currentframe().f_lineno, versions_file_path, file=sys.stderr)
			json_open = open(versions_file_path, encoding='utf-8')
			json_load = json.load(json_open)
			json_load_keys = list(json_load.keys())

			#self._versions = sorted([*json_load_keys], key=lambda x: json_load[x]['order'], reverse=True)

			if self._debug:
				self._versions = sorted(filter(lambda x: isinstance(json_load[x], dict),json_load_keys), key=lambda x:json_load[x]['order'], reverse=True)
			else:
				self._versions = sorted(filter(lambda x: isinstance(json_load[x], dict) and json_load[x]['mv_publish'],json_load_keys), key=lambda x:json_load[x]['order'], reverse=True)

			#self._versions = sorted(json_load.keys(), reverse=True)
			#print(versions)
		if self._debug:
			print("__init__():EXEC:",inspect.currentframe().f_lineno, self._versions, file=sys.stderr)
			print("__init__():EXEC:",inspect.currentframe().f_lineno, self._reduction, file=sys.stderr)

#		exit(1)

		#if self._debug:
		#	print("__init__():EXEC:",inspect.currentframe().f_lineno, version, file=sys.stderr)

		if version and version not in self._versions:
			version = self._versions[0]
		if version:
			self._versions = [version]

		if self._debug:
			print("__init__():EXEC:",inspect.currentframe().f_lineno, version, file=sys.stderr)
		#exit(1)

		if self._debug:
			print("__init__():EXEC:",inspect.currentframe().f_lineno, time.time() - start_time, file=sys.stderr)
		if load_mesh:
			for v in self._versions:
				file_path = os.path.join(json_path,'renderer_file',v+'.json')
				if self._debug:
					print("__init__():EXEC:",inspect.currentframe().f_lineno, file_path, file=sys.stderr)
				if not os.path.isfile(file_path):
					continue

				json_open = open(file_path, encoding='utf-8')
				json_load = json.load(json_open)
				self._renderer_info_dict[v] = json_load[v]

				if load_mesh and isinstance(json_load[v], dict) and 'ids' in json_load[v] and isinstance(json_load[v]['ids'], dict) and 'art_ids' in json_load[v] and isinstance(json_load[v]['art_ids'], dict):

					ids_dict = json_load[v]['ids']
					#objs_dict = json_load[v]['art_ids']

					if self._debug:
						#self._load_actor(self._plotter, id_list=['FMA52847'], ids_dict=ids_dict)
						#self._load_actor(self._plotter, id_list=['FMA5018'], ids_dict=ids_dict)
						#self._load_actor(self._plotter, id_list=['FMA7309','FMA7310'], ids_dict=ids_dict)
						#self._load_actor(self._plotter, id_list=['FMA52847','FMA7309','FMA7310'], ids_dict=ids_dict)
						self._load_actor(self._plotter, id_list=['FMA58241','FMA58295','FMA5823'], ids_dict=ids_dict)
					else:
						self._load_actor(self._plotter, id_list=sorted(ids_dict.keys()), ids_dict=ids_dict)


				#if version and version == v:
				#	break
				#elif self._debug:
				#	break

		if self._debug:
			print("__init__():END:",inspect.currentframe().f_lineno, time.time() - start_time, len(self._actor_dict.keys()), file=sys.stderr)


	def getZoomYRange(self,zoom):
		return max(1,round( math.exp(1) ** ((math.log(self._DEF_HEIGHT)/math.log(2)-zoom) * math.log(2)) ));

	def getYRangeZoom(self,yrange):
		return round((math.log(self._DEF_HEIGHT)/math.log(2) - math.log(yrange)/math.log(2)) * 10) / 10;

	def get_version_list(self):
		return self._versions

	def get_latest_version(self):
		return self._versions[0]

	def check_version(self,version=None):
		if not version or version not in self._versions:
			version = self.get_latest_version()
		return version

	def get_ids_list(self,version):
		ids_dict = self._renderer_info_dict[version]['ids']
		return list(ids_dict.keys())

	def animation(self, query, script_path=None):

		param_list = list(query.keys());
		if self._debug:
			print("animation():EXEC:",inspect.currentframe().f_lineno, param_list, file=sys.stderr)

		version = query.get('version') or 'latest'
		if self._debug:
			print("animation():EXEC:",inspect.currentframe().f_lineno, version, file=sys.stderr)

		size_list = (500, 500)
		size_str = query.get('size') or '500x500'
		if self._debug:
			print("animation():EXEC:",inspect.currentframe().f_lineno, size_str, file=sys.stderr)
		size_match_result = re.match('^([0-9]+)[^0-9]+([0-9]+)$', size_str)
		if size_match_result:
			size_list = (int(size_match_result.group(1)), int(size_match_result.group(2)))
		else:
			size_match_result = re.match('^([0-9]+)$', size_str)
			if size_match_result:
				size_list = (int(size_match_result.group(1)), int(size_match_result.group(1)))

		reduction = None
		reduction_str = query.get('reduction')
		if reduction_str:
			reduction_match_result = re.match('^([0-9]+)$', reduction_str)
			if reduction_match_result:
				reduction = float(reduction_match_result.group(1)) / 100
		if self._debug:
			print("animation():EXEC:",inspect.currentframe().f_lineno, reduction, file=sys.stderr)

		zoom = None
		zoom_str = query.get('zoom')
		if zoom_str and is_num(zoom_str):
			zoom = float(zoom_str)
		if self._debug:
			print("animation():EXEC:",inspect.currentframe().f_lineno, zoom, file=sys.stderr)

		id_list = []
		id_property_dict = {}
		if 'id' in param_list:
			#id_list = sorted(query.getall('id'))
			temp_id_list = query.getall('id')
			for id in temp_id_list:
				if ',' in id:
					id_list.extend(id.split(','))
				else:
					id_list.append(id)

			for id in id_list:
				id_property_dict[id] = {'color':None,'opacity':1.0}

			if self._debug:
				print("animation():EXEC:",inspect.currentframe().f_lineno, id_list, file=sys.stderr)
				print("animation():EXEC:",inspect.currentframe().f_lineno, id_property_dict, file=sys.stderr)

		focusid_list = None
		if 'focusid' in param_list:
			temp_id_list = query.getall('focusid')
			if isinstance(temp_id_list, list) and len(temp_id_list) > 0:
				focusid_list = []
				for id in temp_id_list:
					if not len(id) > 0:
						continue
					if ',' in id:
						focusid_list.extend(id.split(','))
					else:
						focusid_list.append(id)
		if self._debug:
			print("image():EXEC:",inspect.currentframe().f_lineno, focusid_list, file=sys.stderr)

		if 'rgb' in param_list:
			rgb_list = query.getall('rgb')
			rgb_cnt = 0
			for rgb in rgb_list:
				if ',' in rgb:
					for rgb1 in rgb.split(','):
						if len(rgb1) == 6:
							id_property_dict[id_list[rgb_cnt]]['color'] = '#'+rgb1
						rgb_cnt += 1
						if rgb_cnt >= len(id_list):
							break
				else:
					if len(rgb) == 6:
						id_property_dict[id_list[rgb_cnt]]['color'] = '#'+rgb
					rgb_cnt += 1
					if rgb_cnt >= len(id_list):
						break

			if self._debug:
				print("animation():EXEC:",inspect.currentframe().f_lineno, id_property_dict, file=sys.stderr)

		if 'opacity' in param_list:
			opacity_list = query.getall('opacity')
			if self._debug:
				print("animation():EXEC:",inspect.currentframe().f_lineno, opacity_list, file=sys.stderr)
			opacity_cnt = 0
			for opacity in opacity_list:
				if ',' in opacity:
					for opacity1 in opacity.split(','):
						if is_num(opacity1):
							#id_property_dict[id_list[opacity_cnt]]['opacity'] = 1.0 - float(opacity1)
							id_property_dict[id_list[opacity_cnt]]['opacity'] = float(opacity1)
						opacity_cnt += 1
						if opacity_cnt >= len(id_list):
							break
				else:
					if is_num(opacity):
						#id_property_dict[id_list[opacity_cnt]]['opacity'] = 1.0 - float(opacity)
						id_property_dict[id_list[opacity_cnt]]['opacity'] = float(opacity)
					opacity_cnt += 1
					if opacity_cnt >= len(id_list):
						break

		if self._debug:
			print("animation():EXEC:",inspect.currentframe().f_lineno, id_property_dict, file=sys.stderr)

		expansion = 'art_ids'
		if 'expansion' in param_list:
			expansion_list = query.getall('expansion')
			if isinstance(expansion_list, list) and len(expansion_list)>0 and is_str(expansion_list[0]) and len(expansion_list[0])>0 :
				expansion_str = expansion_list[0].lower()
				if expansion_str == 'is_a' or expansion_str == 'isa':
					expansion = 'art_ids_isa'
				elif expansion_str == 'part_of' or expansion_str == 'partof':
					expansion = 'art_ids_partof'
				elif expansion_str == 'none':
					expansion = 'art_ids_none'

		image_filepath = self._animation(
			size=size_list,
			version=version,
			id_list=id_list,
			id_property_dict=id_property_dict,
			focusid_list=focusid_list,
			expansion=expansion,
			script_path=script_path,
			reduction=reduction,
			zoom=zoom
		)
		return image_filepath


	def image(self, query, script_path=None):

		param_list = list(query.keys());
		if self._debug:
			print("image():EXEC:",inspect.currentframe().f_lineno, param_list, file=sys.stderr)

		version = query.get('version') or 'latest'
		if self._debug:
			print("image():EXEC:",inspect.currentframe().f_lineno, version, file=sys.stderr)

		size_list = [500, 500]
		size_str = query.get('size') or '500x500'
		if self._debug:
			print("image():EXEC:",inspect.currentframe().f_lineno, size_str, file=sys.stderr)
		size_match_result = re.match('^([0-9]+)[^0-9]+([0-9]+)$', size_str)
		if size_match_result:
			size_list = [int(size_match_result.group(1)), int(size_match_result.group(2))]
		else:
			size_match_result = re.match('^([0-9]+)$', size_str)
			if size_match_result:
				size_list = [int(size_match_result.group(1)), int(size_match_result.group(1))]

		reduction = None
		reduction_str = query.get('reduction')
		if reduction_str:
			reduction_match_result = re.match('^([0-9]+)$', reduction_str)
			if reduction_match_result:
				reduction = float(reduction_match_result.group(1)) / 100
		if self._debug:
			print("image():EXEC:",inspect.currentframe().f_lineno, reduction, file=sys.stderr)

		zoom = None
		zoom_str = query.get('zoom')
		if zoom_str and is_num(zoom_str):
			zoom = float(zoom_str)
		if self._debug:
			print("image():EXEC:",inspect.currentframe().f_lineno, zoom, file=sys.stderr)

		azimuth = 0
		elevation = 0

		ha_str = query.get('ha')
		if ha_str and is_num(ha_str):
			azimuth = int(ha_str)
		if self._debug:
			print("image():EXEC:",inspect.currentframe().f_lineno, azimuth, file=sys.stderr)

		va_str = query.get('va')
		if va_str and is_num(va_str):
			elevation = int(va_str)
		if self._debug:
			print("image():EXEC:",inspect.currentframe().f_lineno, azimuth, file=sys.stderr)

		id_list = []
		id_property_dict = {}
		if 'id' in param_list:
			#id_list = sorted(query.getall('id'))
			temp_id_list = query.getall('id')
			for id in temp_id_list:
				if ',' in id:
					id_list.extend(id.split(','))
				else:
					id_list.append(id)

			for id in id_list:
				id_property_dict[id] = {'color':None,'opacity':1.0}

			if self._debug:
				print("image():EXEC:",inspect.currentframe().f_lineno, id_list, file=sys.stderr)
				print("image():EXEC:",inspect.currentframe().f_lineno, id_property_dict, file=sys.stderr)

		focusid_list = None
		if 'focusid' in param_list:
			temp_id_list = query.getall('focusid')
			if isinstance(temp_id_list, list) and len(temp_id_list) > 0:
				focusid_list = []
				for id in temp_id_list:
					if not len(id) > 0:
						continue
					if ',' in id:
						focusid_list.extend(id.split(','))
					else:
						focusid_list.append(id)
		if self._debug:
			print("image():EXEC:",inspect.currentframe().f_lineno, focusid_list, file=sys.stderr)

		if 'rgb' in param_list:
			rgb_list = query.getall('rgb')
			rgb_cnt = 0
			for rgb in rgb_list:
				if ',' in rgb:
					for rgb1 in rgb.split(','):
						if len(rgb1) == 6:
							id_property_dict[id_list[rgb_cnt]]['color'] = '#'+rgb1
						rgb_cnt += 1
						if rgb_cnt >= len(id_list):
							break
				else:
					if len(rgb) == 6:
						id_property_dict[id_list[rgb_cnt]]['color'] = '#'+rgb
					rgb_cnt += 1
					if rgb_cnt >= len(id_list):
						break

			if self._debug:
				print("image():EXEC:",inspect.currentframe().f_lineno, id_property_dict, file=sys.stderr)

		if 'opacity' in param_list:
			opacity_list = query.getall('opacity')
			if self._debug:
				print("image():EXEC:",inspect.currentframe().f_lineno, opacity_list, file=sys.stderr)
			opacity_cnt = 0
			for opacity in opacity_list:
				if ',' in opacity:
					for opacity1 in opacity.split(','):
						if is_num(opacity1):
							#id_property_dict[id_list[opacity_cnt]]['opacity'] = 1.0 - float(opacity1)
							id_property_dict[id_list[opacity_cnt]]['opacity'] = float(opacity1)
						opacity_cnt += 1
						if opacity_cnt >= len(id_list):
							break
				else:
					if is_num(opacity):
						#id_property_dict[id_list[opacity_cnt]]['opacity'] = 1.0 - float(opacity)
						id_property_dict[id_list[opacity_cnt]]['opacity'] = float(opacity)
					opacity_cnt += 1
					if opacity_cnt >= len(id_list):
						break

		if self._debug:
			print("image():EXEC:",inspect.currentframe().f_lineno, id_property_dict, file=sys.stderr)

		expansion = 'art_ids';
		if 'expansion' in param_list:
			expansion_list = query.getall('expansion')
			if isinstance(expansion_list, list) and len(expansion_list)>0 and is_str(expansion_list[0]) and len(expansion_list[0])>0 :
				expansion_str = expansion_list[0].lower()
				if expansion_str == 'is_a' or expansion_str == 'isa':
					expansion = 'art_ids_isa'
				elif expansion_str == 'part_of' or expansion_str == 'partof':
					expansion = 'art_ids_partof'
				elif expansion_str == 'none':
					expansion = 'art_ids_none'

		image_filepath = self._image(
			size=size_list,
			version=version,
			id_list=id_list,
			id_property_dict=id_property_dict,
			focusid_list=focusid_list,
			expansion=expansion,
			script_path=script_path,
			reduction=reduction,
			azimuth=azimuth,
			elevation=elevation,
			zoom=zoom
		)
		return image_filepath


	def _read_mesh(self, art_id, reduction = None):
		if art_id not in self._mesh_dict:
			#continue
			file_path = os.path.join(self._obj_path,art_id+'.obj')
			if os.path.isfile(file_path):

				if reduction == None:
					reduction = self._reduction

				if reduction and reduction > .0:
					mesh = pv.read(file_path)
					decimate = vtk.vtkQuadricDecimation()
					decimate.SetInputData(mesh)
					decimate.SetTargetReduction(reduction)
					decimate.Update()
					decimated_polydata = decimate.GetOutput()
					mesh_decimated = pv.PolyData(decimated_polydata) 
					self._mesh_dict[art_id] = mesh_decimated
				else:
					self._mesh_dict[art_id] = pv.read(file_path)

			else:
				self._mesh_dict[art_id] = None

	def _load_mesh(self, id_list=[], id_property_dict={}, expansion='art_ids', ids_dict={}, objs_dict={}, default_color='#F0D2A0', plotter=None, reduction = 0.0):
		if self._debug:
			print("_load_mesh():START:",inspect.currentframe().f_lineno, file=sys.stderr)
		start_time = time.time()

		exists_actor_list = []
		if self._actor_dict and isinstance(self._actor_dict, dict) and len(self._actor_dict.keys())>0:
			exists_actor_list = set(self._actor_dict.keys())

			#if self._debug:
			#	print("_load_mesh():EXEC:",inspect.currentframe().f_lineno, exists_actor_list, file=sys.stderr)

		load_mesh_list = []	#読み込み対象リスト

		#id_set = set(id_list)
		id_set = sorted(set(id_list), key=lambda x: ids_dict[x]['depth'])
		ids_set = set(ids_dict.keys())
		objs_set = set(objs_dict.keys())

		obj_property_dict = {}

		for id in id_set:
			if id not in ids_set:
				continue
			id_dict = ids_dict[id]

			if not isinstance(id_dict, dict) or not (expansion in id_dict) or not isinstance(id_dict[expansion], list):
				continue

			if self._debug:
				print("_load_mesh():EXEC:",inspect.currentframe().f_lineno, id, file=sys.stderr)

			#load_mesh_list = set(list(load_mesh_list)+id_dict['art_ids'])
			load_mesh_list += id_dict[expansion]

			if id_property_dict[id] and isinstance(id_property_dict[id], dict):
				for art_id in id_dict[expansion]:
					obj_property_dict[art_id] = id_property_dict[id]
			else:
				for art_id in id_dict[expansion]:
					obj_property_dict[art_id] = {'color': None, 'opacity': 1.0}

		load_mesh_set = sorted(set(load_mesh_list))

		#max_bounds = 0
		#disp_bounds = [None,None,None,None,None,None]

		for art_id in exists_actor_list:
			if art_id in load_mesh_set:
				self._actor_dict[art_id].visibility = True
				if art_id in objs_set and objs_dict[art_id] and isinstance(objs_dict[art_id], dict):
					#self._actor_dict[art_id].prop.color = objs_dict[art_id]['color'] or default_color
					self._actor_dict[art_id].prop.color = obj_property_dict[art_id]['color'] or objs_dict[art_id]['color'] or default_color
					self._actor_dict[art_id].prop.opacity = obj_property_dict[art_id]['opacity'] #or default_opacity
				load_mesh_set.remove(art_id)	#読み込み済みの場合はリストから削除

				#Xmin,Xmax,Ymin,Ymax,Zmin,Zmax
				#bounds = self._actor_dict[art_id].GetBounds()
				#for i in (0,2,4):
				#	if disp_bounds[i]==None or disp_bounds[i]>bounds[i]:
				#		disp_bounds[i] = bounds[i]
				#	j = i + 1
				#	if disp_bounds[j]==None or disp_bounds[j]<bounds[j]:
				#		disp_bounds[j] = bounds[j]
				#if self._debug:
				#	print("_load_mesh():EXEC:",inspect.currentframe().f_lineno, bounds, disp_bounds, file=sys.stderr)

			else:
				self._actor_dict[art_id].visibility = False

		for art_id in load_mesh_set:
			if art_id in exists_actor_list:
				continue

			self._read_mesh(art_id)

			if self._debug:
				print("_load_mesh():EXEC:",inspect.currentframe().f_lineno, art_id, file=sys.stderr)
			#	print("_load_mesh():EXEC:",inspect.currentframe().f_lineno, self._mesh_dict[art_id], file=sys.stderr)
			#print("_load_mesh():EXEC:",inspect.currentframe().f_lineno, art_id, file=sys.stderr)

			if not plotter or not self._mesh_dict[art_id]:
				continue

			#if self._debug:
			#	print("_load_mesh():EXEC:",inspect.currentframe().f_lineno, art_id, file=sys.stderr)


			if reduction and reduction > .0:
				mesh = self._mesh_dict[art_id]
				decimate = vtk.vtkQuadricDecimation()
				decimate.SetInputData(mesh)
				decimate.SetTargetReduction(reduction)
				decimate.Update()
				decimated_polydata = decimate.GetOutput()
				mesh_decimated = pv.PolyData(decimated_polydata)
				if art_id in objs_set and objs_dict[art_id] and isinstance(objs_dict[art_id], dict):
					self._actor_dict[art_id] = plotter.add_mesh(mesh_decimated, color=objs_dict[art_id]['color'] or default_color)
				else:
					self._actor_dict[art_id] = plotter.add_mesh(mesh_decimated, color=default_color)
			elif art_id in objs_set and objs_dict[art_id] and isinstance(objs_dict[art_id], dict):
				self._actor_dict[art_id] = plotter.add_mesh(self._mesh_dict[art_id], color=objs_dict[art_id]['color'] or default_color)
			else:
				self._actor_dict[art_id] = plotter.add_mesh(self._mesh_dict[art_id], color=default_color)

			##Xmin,Xmax,Ymin,Ymax,Zmin,Zmax
			#bounds = self._actor_dict[art_id].GetBounds()
			#for i in (0,2,4):
			#	if disp_bounds[i]==None or disp_bounds[i]>bounds[i]:
			#		disp_bounds[i] = bounds[i]
			#	j = i + 1
			#	if disp_bounds[j]==None or disp_bounds[j]<bounds[j]:
			#		disp_bounds[j] = bounds[j]
			#if self._debug:
			#	print("_load_mesh():EXEC:",inspect.currentframe().f_lineno, bounds, disp_bounds, file=sys.stderr)

		#max_bounds = max(max_bounds, max(abs(disp_bounds[0] - disp_bounds[1]), abs(disp_bounds[2] - disp_bounds[3]), abs(disp_bounds[4] - disp_bounds[5])))
		#zoom_bounds = self.getYRangeZoom(max_bounds)
		#if zoom_bounds>0:
		#	zoom_bounds = zoom_bounds-0.1
		#y_range = self.getZoomYRange(zoom_bounds)

		#if self._debug:
		#	print("_load_mesh():EXEC:",inspect.currentframe().f_lineno, max_bounds, file=sys.stderr)
		#	print("_load_mesh():EXEC:",inspect.currentframe().f_lineno, zoom_bounds, file=sys.stderr)
		#	print("_load_mesh():EXEC:",inspect.currentframe().f_lineno, y_range, file=sys.stderr)

		if self._debug:
			print("_load_mesh():END:",inspect.currentframe().f_lineno, time.time() - start_time, file=sys.stderr)



	def _load_actor(self, plotter, id_list=[], ids_dict={}, default_color='#F0D2A0',visibility=True):
		if self._debug:
			#print("_load_actor():START:",inspect.currentframe().f_lineno, id_list, file=sys.stderr)
			print("_load_actor():START:",inspect.currentframe().f_lineno, file=sys.stderr)
		start_time = time.time()
		art_ids_list = []
		for id in id_list:
			if id not in ids_dict:
				continue
			id_dict = ids_dict[id]

			if not isinstance(id_dict, dict) or not isinstance(id_dict['art_ids'], list):
				continue

			#if self._debug:
			#	print("_load_actor():EXEC:",inspect.currentframe().f_lineno, id, file=sys.stderr)
			#print("_load_actor():EXEC:",inspect.currentframe().f_lineno, id, file=sys.stderr)

			art_ids_list += id_dict['art_ids']

		art_ids_set = sorted(set(art_ids_list))
		art_ids_len = len(art_ids_set)
		art_ids_count = 0

		for art_id in art_ids_set:
			art_ids_count+=1
			if art_id in self._actor_dict:
				continue

			if self._debug:
				print("_load_actor():EXEC:[%5d][%5d/%5d]:[%-10s]" % (inspect.currentframe().f_lineno,art_ids_count,art_ids_len,art_id), file=sys.stderr)

			self._read_mesh(art_id)

			#if self._debug:
			#	print("_load_actor():EXEC:",inspect.currentframe().f_lineno, art_id, file=sys.stderr)

			if not self._mesh_dict[art_id]:
				continue

			#if self._debug:
			#	print("_load_actor():EXEC:",inspect.currentframe().f_lineno, art_id, file=sys.stderr)
			#print("_load_actor():EXEC:",inspect.currentframe().f_lineno, art_id, file=sys.stderr)

			self._actor_dict[art_id] = plotter.add_mesh(self._mesh_dict[art_id], color=default_color)
			if not visibility:
				self._actor_dict[art_id].visibility = False

		if self._debug:
			print("_load_actor():END:",inspect.currentframe().f_lineno, time.time() - start_time, file=sys.stderr)


	def _get_bounds(self, id_list=[], expansion='art_ids', ids_dict={}, objs_dict={}, plotter=None, default_color='#F0D2A0'):
		if self._debug:
			print("_get_bounds():START:",inspect.currentframe().f_lineno, id_list, file=sys.stderr)
		start_time = time.time()

		exists_actor_list = []
		if self._actor_dict and isinstance(self._actor_dict, dict) and len(self._actor_dict.keys())>0:
			exists_actor_list = set(self._actor_dict.keys())

		if self._debug:
			print("_get_bounds():EXEC:",inspect.currentframe().f_lineno, exists_actor_list, file=sys.stderr)
			print("_get_bounds():EXEC:",inspect.currentframe().f_lineno, id_list, file=sys.stderr)

		load_mesh_list = []	#読み込み対象リスト

		#id_set = set(id_list)
		id_set = sorted(set(id_list), key=lambda x: ids_dict[x]['depth'])
		ids_set = set(ids_dict.keys())
		objs_set = set(objs_dict.keys())

		obj_property_dict = {}

		for id in id_set:
			if id not in ids_set:
				continue
			id_dict = ids_dict[id]

			if not isinstance(id_dict, dict) or not (expansion in id_dict) or not isinstance(id_dict[expansion], list):
				continue

			if self._debug:
				print("_get_bounds():EXEC:",inspect.currentframe().f_lineno, id, file=sys.stderr)

			#load_mesh_list = set(list(load_mesh_list)+id_dict['art_ids'])
			load_mesh_list += id_dict[expansion]


		load_mesh_set = sorted(set(load_mesh_list))

		#max_bounds = 0
		xmin = []
		xmax = []
		ymin = []
		ymax = []
		zmin = []
		zmax = []

		for art_id in exists_actor_list:
			if art_id in load_mesh_set:
				bounds = self._actor_dict[art_id].GetBounds()
				xmin.append(bounds[0])
				xmax.append(bounds[1])
				ymin.append(bounds[2])
				ymax.append(bounds[3])
				zmin.append(bounds[4])
				zmax.append(bounds[5])

				load_mesh_set.remove(art_id)	#読み込み済みの場合はリストから削除

		for art_id in load_mesh_set:
			if art_id in exists_actor_list:
				continue

			self._read_mesh(art_id)

			if self._debug:
				print("_get_bounds():EXEC:",inspect.currentframe().f_lineno, art_id, file=sys.stderr)
			#	print("_get_bounds():EXEC:",inspect.currentframe().f_lineno, self._mesh_dict[art_id], file=sys.stderr)
			#print("_get_bounds():EXEC:",inspect.currentframe().f_lineno, art_id, file=sys.stderr)

			if not plotter or not self._mesh_dict[art_id]:
				continue

			self._actor_dict[art_id] = plotter.add_mesh(self._mesh_dict[art_id], color=default_color)
			self._actor_dict[art_id].visibility = False

			bounds = self._actor_dict[art_id].GetBounds()
			xmin.append(bounds[0])
			xmax.append(bounds[1])
			ymin.append(bounds[2])
			ymax.append(bounds[3])
			zmin.append(bounds[4])
			zmax.append(bounds[5])

		return (min(xmin),max(xmax),min(ymin),max(ymax),min(zmin),max(zmax))


	def _openPlotter(self, size = [500,500], forced=False):

		#print("_openPlotter():START:",inspect.currentframe().f_lineno, size, forced, self._plotter, file=sys.stderr)

		if forced:
			self._plotter = pv.Plotter(off_screen=True, window_size=size)
			self._plotter.enable_parallel_projection()
			#self._plotter.add_bounding_box(line_width=5, color='black')

		if self._plotter:
			#print("_openPlotter():EXEC:",inspect.currentframe().f_lineno, self._plotter.window_size, type(self._plotter.window_size), type(size), file=sys.stderr)
			#if self._plotter.window_size != list(size):
			#	print("_openPlotter():EXEC:",inspect.currentframe().f_lineno, self._plotter.window_size, file=sys.stderr)
			#	self._plotter.window_size = list(size)
			self._plotter.window_size = list(size)
			#print("_openPlotter():EXEC:",inspect.currentframe().f_lineno, self._plotter.window_size, type(self._plotter.window_size), type(size), file=sys.stderr)
			return self._plotter
		else:
			plotter = pv.Plotter(off_screen=True, window_size=size)
			plotter.enable_parallel_projection()
			return plotter


	def _closePlotter(self, plotter):
		#print("_closePlotter():START:",inspect.currentframe().f_lineno, file=sys.stderr)
		if self._plotter:
			#print("_closePlotter():END:",inspect.currentframe().f_lineno, file=sys.stderr)
			pass
		else:
			plotter.clear()
			plotter.deep_clean()
			plotter.close()
			plotter = None
			#print("_closePlotter():END:",inspect.currentframe().f_lineno, file=sys.stderr)


	def _execMakeAnimation(self, size = [500,500], id_list=[], id_property_dict={}, focusid_list=None, expansion='art_ids', ids_dict={}, objs_dict={}, range_step=12, reduction=None, start_time=None, image_filepath=None, zoom=None):

		if self._debug:
			print("_execMakeAnimation():START:",inspect.currentframe().f_lineno, time.time() - start_time, file=sys.stderr)

		plotter = self._openPlotter(size=size)

		if self._debug:
			print("_execMakeAnimation():EXEC:",inspect.currentframe().f_lineno, time.time() - start_time, file=sys.stderr)
		self._load_mesh(id_list=id_list, id_property_dict=id_property_dict, expansion=expansion, ids_dict=ids_dict, objs_dict=objs_dict, plotter=plotter, reduction=reduction)
		if self._debug:
			print("_execMakeAnimation():EXEC:",inspect.currentframe().f_lineno, time.time() - start_time, file=sys.stderr)

		bounds = None
		if isinstance(focusid_list, list) and len(focusid_list) > 0:
			bounds = self._get_bounds(id_list=focusid_list, expansion=expansion, ids_dict=ids_dict, objs_dict=objs_dict, plotter=plotter)
			if self._debug:
				print("_execMakeAnimation():EXEC:",inspect.currentframe().f_lineno, bounds, file=sys.stderr)

		plotter.camera_position = 'xz'
		plotter.camera.azimuth = 0
		plotter.camera.elevation = 0
		#plotter.camera.zoom(zoom)
		plotter.camera.zoom(1.0)
		#plotter.camera.reset_clipping_range()
		plotter.renderer.reset_camera(render=True, bounds=bounds)

		y_range = None
		if zoom != None and is_num(zoom) and zoom >= 1.0 :
			y_range = self.getZoomYRange((zoom - 1.0) / 5.0)
			if self._debug:
				print("_execMakeAnimation():EXEC:",inspect.currentframe().f_lineno, y_range, file=sys.stderr)
			plotter.camera.SetParallelScale(y_range / 2.0)

		if self._debug:
			print("_execMakeAnimation():EXEC:",inspect.currentframe().f_lineno, time.time() - start_time, file=sys.stderr)

		#plotter.open_gif(tmp_filepath, fps = 5)	# default fps = 10
		plotter.open_gif(image_filepath, fps = 5)	# default fps = 10
		if self._debug:
			print("_execMakeAnimation():EXEC:",inspect.currentframe().f_lineno, time.time() - start_time, file=sys.stderr)
		for_start_time = time.time()
		for i in range(0,360,range_step):
			plotter.camera.azimuth = i
			#plotter.camera.reset_clipping_range()
			plotter.renderer.reset_camera(render=True, bounds=bounds)
			if zoom != None :
				plotter.camera.SetParallelScale(y_range / 2.0)
			plotter.write_frame()
			for_end_time = time.time()
			if self._debug:
				print("_execMakeAnimation():EXEC:",inspect.currentframe().f_lineno, i, for_end_time - start_time, for_end_time - for_start_time, file=sys.stderr)
			for_start_time = for_end_time
		#plotter.close()
		plotter.mwriter.close()

		if self._debug:
			print("_execMakeAnimation():EXEC:",inspect.currentframe().f_lineno, time.time() - start_time, time.time() - for_start_time, file=sys.stderr)

		#if os.path.isfile(image_filepath):
		#	os.remove(image_filepath)

		if self._debug:
			print("_execMakeAnimation():EXEC:",inspect.currentframe().f_lineno, time.time() - start_time, file=sys.stderr)

		#shutil.move(tmp_filepath, image_path)

		if self._debug:
			print("_execMakeAnimation():EXEC:",inspect.currentframe().f_lineno, time.time() - start_time, file=sys.stderr)

		self._closePlotter(plotter)

		shutil.rmtree(tmp_dir)
		if self._debug:
			print("_execMakeAnimation():END:",inspect.currentframe().f_lineno, time.time() - start_time, file=sys.stderr)


	def _execMakeImage(self, size = [500,500], id_list=[], id_property_dict={}, focusid_list=None, expansion='art_ids', ids_dict={}, objs_dict={}, reduction=None, start_time=None, image_filepath=None, azimuth=0, elevation=0, zoom=None):

		if self._debug:
			print("_execMakeImage():START:",inspect.currentframe().f_lineno, size, file=sys.stderr)

		plotter = self._openPlotter(size=size)

		if self._debug:
			print("_execMakeImage():EXEC:",inspect.currentframe().f_lineno, file=sys.stderr)
		self._load_mesh(id_list=id_list, id_property_dict=id_property_dict, expansion=expansion, ids_dict=ids_dict, objs_dict=objs_dict, plotter=plotter, reduction=reduction)
		if self._debug:
			print("_execMakeImage():EXEC:",inspect.currentframe().f_lineno, file=sys.stderr)

		bounds = None
		if isinstance(focusid_list, list) and len(focusid_list) > 0:
			bounds = self._get_bounds(id_list=focusid_list, expansion=expansion, ids_dict=ids_dict, objs_dict=objs_dict, plotter=plotter)
			if self._debug:
				print("_execMakeImage():EXEC:",inspect.currentframe().f_lineno, bounds, file=sys.stderr)

		plotter.camera_position = 'xz'
		plotter.camera.azimuth = azimuth
		plotter.camera.elevation = elevation
		#plotter.camera.zoom(zoom)
		plotter.camera.zoom(1.0)
		#plotter.camera.zoom('tight')
		#plotter.camera.tight(padding=0.05, view='xz', adjust_render_window=False)
		#plotter.camera.reset_clipping_range()
		plotter.renderer.reset_camera(render=True, bounds=bounds)

		#y_range = self._DEF_HEIGHT
		if zoom != None and is_num(zoom) and zoom >= 1.0 :
			y_range = self.getZoomYRange((zoom - 1.0) / 5.0)
			if self._debug:
				print("_execMakeImage():EXEC:",inspect.currentframe().f_lineno, y_range, file=sys.stderr)
			plotter.camera.SetParallelScale(y_range / 2.0)

		if self._debug:
			print("_execMakeImage():EXEC:",inspect.currentframe().f_lineno, plotter.camera.focal_point, file=sys.stderr)
			print("_execMakeImage():EXEC:",inspect.currentframe().f_lineno, plotter.camera.position, file=sys.stderr)
			print("_execMakeImage():EXEC:",inspect.currentframe().f_lineno, plotter.camera.distance, file=sys.stderr)
			print("_execMakeImage():EXEC:",inspect.currentframe().f_lineno, plotter.camera.clipping_range, file=sys.stderr)

		plotter.screenshot(image_filepath)

		if self._debug:
			print("_execMakeImage():EXEC:",inspect.currentframe().f_lineno, plotter.camera.GetParallelScale(), file=sys.stderr)
			x0, x1, y0, y1, z0, z1 = plotter.renderer.ComputeVisiblePropBounds()
			max_bounds = max(1, max(abs(x0 - x1), abs(y0 - y1), abs(z0 - z1)))
			zoom_bounds = self.getYRangeZoom(max_bounds)
			if zoom_bounds>0:
				zoom_bounds = zoom_bounds-0.1
			y_range = self.getZoomYRange(zoom_bounds)
			print("_execMakeImage():EXEC:",inspect.currentframe().f_lineno, x0, x1, y0, y1, z0, z1, file=sys.stderr)
			print("_execMakeImage():EXEC:",inspect.currentframe().f_lineno, max_bounds, file=sys.stderr)
			print("_execMakeImage():EXEC:",inspect.currentframe().f_lineno, zoom_bounds, file=sys.stderr)
			print("_execMakeImage():EXEC:",inspect.currentframe().f_lineno, y_range, file=sys.stderr)
			#print("_execMakeImage():EXEC:",inspect.currentframe().f_lineno, plotter.camera, file=sys.stderr)

		self._closePlotter(plotter)
		if self._debug:
			print("_execMakeImage():END:",inspect.currentframe().f_lineno, file=sys.stderr)

		return image_filepath


	def _execMakeNoneImage(self, size = [500,500], image_filepath=None):
		if self._debug:
			print("_execMakeNoneImage():START:",inspect.currentframe().f_lineno, size, file=sys.stderr)
		plotter = self._openPlotter(size=size)
		self._load_mesh(plotter=plotter)
		plotter.add_text("No Image", position="upper_edge", font_size=30, color="black")
		plotter.camera.reset_clipping_range()
		plotter.screenshot(image_filepath)
		self._closePlotter(plotter)
		if self._debug:
			print("_execMakeNoneImage():END:",inspect.currentframe().f_lineno, size, file=sys.stderr)
		return image_filepath


	def _makeAnimation(self, use_fork=True, use_multiprocessing=False, size = [500,500], id_list=[], id_property_dict={}, focusid_list=None, expansion='art_ids', ids_dict={}, objs_dict={}, range_step=12, reduction=None, start_time=None, image_filepath=None, zoom=None):

		if use_fork:
			try:
				pid = os.fork()

				if not pid:
					try:
						self._execMakeAnimation(
							size=size,
							id_list=id_list,
							id_property_dict=id_property_dict,
							focusid_list=focusid_list,
							expansion=expansion,
							ids_dict=ids_dict,
							objs_dict=objs_dict,
							range_step=range_step,
							reduction=reduction,
							start_time=start_time,
							image_filepath=image_filepath,
							zoom=zoom
						)

						os._exit(0)

					except OSError as e:
						print("exec():{}".format(e))
						sys.exit(1)

				else:
					try:
						status = os.waitpid(pid, 0)[1]
					except OSError as e:
						print("waitpid():{}".format(e))
						sys.exit(1)
					if os.WIFEXITED(status):
						if self._debug or status != 0:
							print("_makeAnimation():END:",inspect.currentframe().f_lineno, file=sys.stderr)
							print("child (PID={}) finished: ".format(pid), end="")
							print("exit, status={}".format(os.WEXITSTATUS(status)))
					elif os.WIFSIGNALED(status):
						print("_makeAnimation():END:",inspect.currentframe().f_lineno, file=sys.stderr)
						print("child (PID={}) finished: ".format(pid), end="")
						print("signal, sig={}".format(os.WTERMSIG(status)))
					else:
						print("_makeAnimation():END:",inspect.currentframe().f_lineno, file=sys.stderr)
						print("child (PID={}) finished: ".format(pid), end="")
						print("abnormal exit")

			except OSError as e:
				print("fork():{}".format(e))
				pass

		else:
			self._execMakeAnimation(
				size=size,
				id_list=id_list,
				id_property_dict=id_property_dict,
				focusid_list=focusid_list,
				expansion=expansion,
				ids_dict=ids_dict,
				objs_dict=objs_dict,
				range_step=range_step,
				reduction=reduction,
				start_time=start_time,
				image_filepath=image_filepath,
				zoom=zoom
			)


	def _makeImage(self, use_fork=True, size = [500,500], id_list=[], id_property_dict={}, focusid_list=None, expansion='art_ids', ids_dict={}, objs_dict={}, reduction=None, start_time=None, image_filepath=None, azimuth=0, elevation=0, zoom=None):

		if self._debug:
			print("_makeImage():START:",inspect.currentframe().f_lineno, use_fork, file=sys.stderr)

		if use_fork:
			try:
				pid = os.fork()

				if not pid:
					try:
						self._execMakeImage(
							size=size,
							id_list=id_list,
							id_property_dict=id_property_dict,
							focusid_list=focusid_list,
							expansion=expansion,
							ids_dict=ids_dict,
							objs_dict=objs_dict,
							reduction=reduction,
							start_time=start_time,
							image_filepath=image_filepath,
							azimuth=azimuth,
							elevation=elevation,
							zoom=zoom
						)

						os._exit(0)

					except OSError as e:
						print("exec():{}".format(e))
						sys.exit(1)

				else:
					try:
						status = os.waitpid(pid, 0)[1]
					except OSError as e:
						print("waitpid():{}".format(e))
						sys.exit(1)
					if os.WIFEXITED(status):
						if self._debug or status != 0:
							print("_makeImage():END:",inspect.currentframe().f_lineno, file=sys.stderr)
							print("child (PID={}) finished: ".format(pid), end="")
							print("exit, status={}".format(os.WEXITSTATUS(status)))
					elif os.WIFSIGNALED(status):
						print("_makeImage():END:",inspect.currentframe().f_lineno, file=sys.stderr)
						print("child (PID={}) finished: ".format(pid), end="")
						print("signal, sig={}".format(os.WTERMSIG(status)))
					else:
						print("_makeImage():END:",inspect.currentframe().f_lineno, file=sys.stderr)
						print("child (PID={}) finished: ".format(pid), end="")
						print("abnormal exit")

			except OSError as e:
				print("fork():{}".format(e))
				pass

		else:
			self._execMakeImage(
				size=size,
				id_list=id_list,
				id_property_dict=id_property_dict,
				focusid_list=focusid_list,
				expansion=expansion,
				ids_dict=ids_dict,
				objs_dict=objs_dict,
				reduction=reduction,
				start_time=start_time,
				image_filepath=image_filepath,
				azimuth=azimuth,
				elevation=elevation,
				zoom=zoom
			)

		if self._debug:
			print("_makeImage():END:",inspect.currentframe().f_lineno, use_fork, file=sys.stderr)



	def _makeNoneImage(self, use_fork=True, size = [500,500], image_filepath=None ):

		if self._debug:
			print("_makeNoneImage():START:",inspect.currentframe().f_lineno, use_fork, file=sys.stderr)

		if use_fork:
			try:
				pid = os.fork()

				if not pid:
					try:
						self._execMakeNoneImage(
							size=size,
							image_filepath=image_filepath
						)

						os._exit(0)

					except OSError as e:
						print("exec():{}".format(e))
						sys.exit(1)

				else:
					try:
						status = os.waitpid(pid, 0)[1]
					except OSError as e:
						print("waitpid():{}".format(e))
						sys.exit(1)
					if os.WIFEXITED(status):
						if self._debug or status != 0:
							print("_makeNoneImage():END:",inspect.currentframe().f_lineno, file=sys.stderr)
							print("child (PID={}) finished: ".format(pid), end="")
							print("exit, status={}".format(os.WEXITSTATUS(status)))
					elif os.WIFSIGNALED(status):
						print("_makeNoneImage():END:",inspect.currentframe().f_lineno, file=sys.stderr)
						print("child (PID={}) finished: ".format(pid), end="")
						print("signal, sig={}".format(os.WTERMSIG(status)))
					else:
						print("_makeNoneImage():END:",inspect.currentframe().f_lineno, file=sys.stderr)
						print("child (PID={}) finished: ".format(pid), end="")
						print("abnormal exit")

			except OSError as e:
				print("fork():{}".format(e))
				pass

		else:
			self._execMakeNoneImage(
				size=size,
				image_filepath=image_filepath
			)

		if self._debug:
			print("_makeNoneImage():END:",inspect.currentframe().f_lineno, use_fork, file=sys.stderr)


	def _lock(self, image_lockfilepath):
		rtn = False
		if not os.path.isdir(image_lockfilepath):
			try:
				os.makedirs(image_lockfilepath)

				pid_filepath = os.path.join( image_lockfilepath, str(os.getpid()) )
				p = pathlib.Path(pid_filepath)
				p.touch(mode=0o400, exist_ok=True)

				rtn = True
			except FileExistsError as e:
				print("makedirs():{}".format(e))
				pass

		if self._debug:
			print("_lock():END:",inspect.currentframe().f_lineno, rtn, file=sys.stderr)

		return rtn


	def _unlock(self, image_lockfilepath):
		rtn = False

		#ロックされている場合
		if os.path.isdir(image_lockfilepath):
			#ファイル一覧を取得
			files_file = [
				f for f in os.listdir(image_lockfilepath) if os.path.isfile(os.path.join(image_lockfilepath, f))
			]
			exists_pid = False
			if len(files_file)>0:
				#プロセス一覧を取得
				pids_dict = {
					str(p.info["pid"]): p.info["name"]
					for p in psutil.process_iter(attrs=["pid", "name"])
				}
				#自身のpidは削除
				self_pid = str(os.getpid())
				if self_pid in pids_dict:
					del pids_dict[self_pid]
				#プロセスの有無を確認
				for pid in files_file:
					if pid in pids_dict:
						exists_pid = True
						break
			#プロセスが無い場合
			if not exists_pid:
				shutil.rmtree(image_lockfilepath)

		if not os.path.isdir(image_lockfilepath):
			rtn = True

		if self._debug:
			print("_unlock():END:",inspect.currentframe().f_lineno, rtn, file=sys.stderr)

		return rtn


	def _animation(self, size = [500,500], version=None, id_list=[], id_property_dict={}, focusid_list=None, expansion='art_ids', is_forced=False, script_path=None, range_step=12, reduction=None, zoom=None):

		start_time = time.time()

		#print("_animation():EXEC:",inspect.currentframe().f_lineno, self._images_path, file=sys.stderr)

		if not reduction:
			reduction = self._reduction

		image_filepath = None

		ids_dict = {}
		objs_dict = {}

		version = self.check_version(version)

		if self._debug:
			print("_animation():EXEC:",inspect.currentframe().f_lineno, "version=[{}]".format(version), file=sys.stderr)
			print("_animation():EXEC:",inspect.currentframe().f_lineno, "reduction=[{}]".format(reduction), file=sys.stderr)

		if not self._renderer_info_dict or not isinstance(self._renderer_info_dict, dict) or version not in self._renderer_info_dict:
			file_path = os.path.join(self._json_path,'renderer_file',version+'.json')
			if self._debug:
				print("_animation():EXEC:",inspect.currentframe().f_lineno, file_path, file=sys.stderr)
			if os.path.isfile(file_path):
				json_open = open(file_path, encoding='utf-8')
				json_load = json.load(json_open)
				if json_load and isinstance(json_load, dict) and version in json_load:
					self._renderer_info_dict[version] = json_load[version]
				else:
					self._renderer_info_dict[version] = None

		if self._renderer_info_dict and isinstance(self._renderer_info_dict, dict) and version in self._renderer_info_dict:
			if 'ids' in self._renderer_info_dict[version]:
				ids_dict = self._renderer_info_dict[version]['ids']
			if 'art_ids' in self._renderer_info_dict[version]:
				objs_dict = self._renderer_info_dict[version]['art_ids']

		if self._debug:
			print("_animation():EXEC:",inspect.currentframe().f_lineno, "id_list=[{}]".format(id_list), file=sys.stderr)

		if len(id_list)>0 and isinstance(ids_dict, dict):
			id_list = sorted([id for id in id_list if id in ids_dict])

		if self._debug:
			print("_animation():EXEC:",inspect.currentframe().f_lineno, "id_list=[{}]".format(id_list), file=sys.stderr)

		if len(id_list)>0:
			fd, image_filepath = tempfile.mkstemp(dir=self._images_path, suffix='.gif')
			os.close(fd)

			self._makeAnimation(
				use_fork=True,
				size=size,
				id_list=id_list,
				id_property_dict=id_property_dict,
				focusid_list=focusid_list,
				expansion=expansion,
				ids_dict=ids_dict,
				objs_dict=objs_dict,
				range_step=range_step,
				reduction=reduction,
				start_time=start_time,
				image_filepath=image_filepath,
				zoom=zoom
			)

		else:
			if image_filepath and os.path.isfile(image_filepath):
				os.remove(image_filepath)

		if self._debug:
			print("_animation():EXEC:",inspect.currentframe().f_lineno, image_filepath, file=sys.stderr)

		if not image_filepath or not os.path.isfile(image_filepath) or os.path.getsize(image_filepath)==0:
			if image_filepath and os.path.isfile(image_filepath):
				os.remove(image_filepath)

			fd, image_filepath = tempfile.mkstemp(dir=self._images_path, suffix='.png')
			os.close(fd)

			if self._debug:
				print("_animation():EXEC:",inspect.currentframe().f_lineno, image_filepath, file=sys.stderr)
			self._makeNoneImage(
				use_fork=True,
				size=size,
				image_filepath=image_filepath
			)

		if self._debug:
			print("_animation():EXEC:",inspect.currentframe().f_lineno, image_filepath, file=sys.stderr)
			print("_animation():END:",inspect.currentframe().f_lineno, time.time() - start_time, file=sys.stderr)

		return image_filepath


	def _image(self, size = [500,500], version=None, id_list=[], id_property_dict={}, focusid_list=None, expansion='art_ids', is_forced=False, script_path=None, reduction=None, azimuth=0, elevation=0, zoom=None):

		if self._debug:
			print("_image():START:",inspect.currentframe().f_lineno, size, type(size), file=sys.stderr)

		start_time = time.time()

		#print("_animation():EXEC:",inspect.currentframe().f_lineno, self._images_path, file=sys.stderr)

		if not reduction:
			reduction = self._reduction

		image_filepath = None

		ids_dict = {}
		objs_dict = {}

		version = self.check_version(version)

		if self._debug:
			print("_image():EXEC:",inspect.currentframe().f_lineno, "version=[{}]".format(version), file=sys.stderr)
			print("_image():EXEC:",inspect.currentframe().f_lineno, "reduction=[{}]".format(reduction), file=sys.stderr)

		if not self._renderer_info_dict or not isinstance(self._renderer_info_dict, dict) or version not in self._renderer_info_dict:
			file_path = os.path.join(self._json_path,'renderer_file',version+'.json')
			if self._debug:
				print("_image():EXEC:",inspect.currentframe().f_lineno, file_path, file=sys.stderr)
			if os.path.isfile(file_path):
				json_open = open(file_path, encoding='utf-8')
				json_load = json.load(json_open)
				if json_load and isinstance(json_load, dict) and version in json_load:
					self._renderer_info_dict[version] = json_load[version]
				else:
					self._renderer_info_dict[version] = None

		if self._renderer_info_dict and isinstance(self._renderer_info_dict, dict) and version in self._renderer_info_dict:
			if 'ids' in self._renderer_info_dict[version]:
				ids_dict = self._renderer_info_dict[version]['ids']
			if 'art_ids' in self._renderer_info_dict[version]:
				objs_dict = self._renderer_info_dict[version]['art_ids']

		if self._debug:
			print("_image():EXEC:",inspect.currentframe().f_lineno, "id_list=[{}]".format(id_list), file=sys.stderr)

		if len(id_list)>0 and isinstance(ids_dict, dict):
			id_list = sorted([id for id in id_list if id in ids_dict])

		if self._debug:
			print("_image():EXEC:",inspect.currentframe().f_lineno, "id_list=[{}]".format(id_list), file=sys.stderr)

		if isinstance(focusid_list, list) and len(focusid_list)>0 and isinstance(ids_dict, dict):
			if self._debug:
				print("_image():EXEC:",inspect.currentframe().f_lineno, focusid_list, file=sys.stderr)
			focusid_list = sorted([id for id in focusid_list if id in ids_dict])
			if len(focusid_list) == 0:
				focusid_list = None
			if self._debug:
				print("_image():EXEC:",inspect.currentframe().f_lineno, focusid_list, file=sys.stderr)

		if len(id_list)>0:
			fd, image_filepath = tempfile.mkstemp(dir=self._images_path, suffix='.png')
			os.close(fd)

			self._makeImage(
				use_fork=True,
				size=size,
				id_list=id_list,
				id_property_dict=id_property_dict,
				focusid_list=focusid_list,
				expansion=expansion,
				ids_dict=ids_dict,
				objs_dict=objs_dict,
				reduction=reduction,
				start_time=start_time,
				image_filepath=image_filepath,
				azimuth=azimuth,
				elevation=elevation,
				zoom=zoom
			)

		if self._debug:
			print("_image():EXEC:",inspect.currentframe().f_lineno, image_filepath, file=sys.stderr)

		if not image_filepath or not os.path.isfile(image_filepath) or os.path.getsize(image_filepath)==0:
			if image_filepath and os.path.isfile(image_filepath):
				os.remove(image_filepath)

			fd, image_filepath = tempfile.mkstemp(dir=self._images_path, suffix='.png')
			os.close(fd)

			if self._debug:
				print("_image():EXEC:",inspect.currentframe().f_lineno, image_filepath, file=sys.stderr)
			self._makeNoneImage(
				use_fork=True,
				size=size,
				image_filepath=image_filepath
			)

		if self._debug:
			print("_image():EXEC:",inspect.currentframe().f_lineno, image_filepath, file=sys.stderr)
			print("_image():END:",inspect.currentframe().f_lineno, time.time() - start_time, file=sys.stderr)

		return image_filepath
