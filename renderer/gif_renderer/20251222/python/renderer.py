# coding: utf-8

import sys
import os
#import platform
#import pathlib
import json
#import inspect
import math
import time
#import glob
#import base64
#import shutil
#import io
#import copy
#import signal
import re
#import subprocess
#import psutil
#from PIL import Image
#import gzip
import tempfile
import gc

#from vtk import (vtkSphereSource, vtkPolyDataMapper, vtkActor, vtkRenderer, vtkCoordinate,
#                 vtkRenderWindow, vtkWindowToImageFilter, vtkPNGWriter, vtkOBJReader, vtkDataEncoder,
#                 vtkAppendPolyData, vtkPolyData, vtkLookupTable, vtkScalarBarActor, vtkTransform, vtkTextActor, vtkPropPicker,vtkCellPicker, vtkArrowSource, vtkGlyph3D)

#from bottle import static_file
import numpy as np
import vtk
#import imageio
import pyvista as pv
#from pyvista.plotting.helpers import view_vectors
#from multiprocessing import Pool, cpu_count
import multiprocessing as mp
#mp.set_start_method('fork')

import logging

from paramclass import Payload,Focus,Camera, CameraJson, Pick, PinJson, PickList, Pin, Map, MapList

#from pathlib import Path
#from typing import Optional

#from concurrent.futures import ThreadPoolExecutor

#pv.global_theme.allow_empty_mesh = True
#pv.global_theme.allow_empty_mesh = False

#from concurrent.futures import ThreadPoolExecutor, as_completed
#from tqdm import tqdm


def is_num(s):
	try:
		float(s)
	except ValueError:
		return False
	else:
		return True

def is_str(v):
	return type(v) is str

def float32_array(mesh):
	if mesh is None:
		return

	float32_array = vtk.vtkFloatArray()
	float32_array.SetNumberOfComponents(3)
	float32_array.SetNumberOfTuples(mesh.GetNumberOfPoints())
	for i in range(mesh.GetNumberOfPoints()):
		p = mesh.GetPoint(i)
		float32_array.SetTuple3(i, *p)
	mesh.GetPoints().SetData(float32_array)

	mesh.GetPointData().Initialize()
	mesh.GetCellData().Initialize()

	return mesh

def is_gltf_or_glb(path: str) -> bool:
	"""拡張子が .gltf もしくは .glb かどうかを判定する"""
	# os.path.splitext は (basename, ext) を返す
	# ext には先頭の「.」が含まれる
	_, ext = os.path.splitext(path)
	return ext.lower() in {'.gltf', '.glb'}

def load_polydata_from_npz(fname: str) -> pv.PolyData:
	arr = np.load(fname, allow_pickle=True)  # allow_pickle=True で dict も読み込める

	points = arr['points']
	faces  = arr['faces']

	poly = pv.PolyData(points, faces)

	# 属性を戻す
	poly.point_data.update(arr['point_data'].item())
	poly.cell_data.update(arr['cell_data'].item())
	poly.field_data.update(arr['field_data'].item())

	return poly


def pick_world_from_screen(plotter, x, y):
	"""
	画面座標 (x, y) を渡すと、その位置にあるセル（ここでは線分）の
	世界座標を返します。返り値は (世界座標, セル ID) です。
	"""
	picker = vtk.vtkCellPicker()           # セルを拾うピッカー
	picker.Pick(x, y, 0, plotter.renderer)         # 3rd arg は Z 方向のオフセット
	if picker.GetCellId() == -1:
		return None, None, None                  # 何も拾われなければ None
	pos = picker.GetPickPosition()   # 3D 空間の座標
	normal = picker.GetPickNormal()   # 正規ベクトル（numpy array）
	#print(picker)
	#print(picker.GetDataSet())
	#print(picker.GetMapper())
	#print(picker.GetPath())
	#print(picker.GetActor())
	#print(picker.GetActor().GetProperty())
	#print(picker.GetActor().name)
	return pos, normal, picker.GetActor().name #, picker.GetCellId()

def world_to_screen(plotter, world_point):
	"""
	3D 世界座標を画面座標（ピクセル）に変換する
	:param plotter: pv.Plotter か pv.Renderer
	:param world_point: (x, y, z) のタプルまたはリスト
	:return: (x_pixel, y_pixel)
	"""
	renderer = plotter.renderer

	# ① 世界座標を設定
	renderer.SetWorldPoint(world_point[0], world_point[1], world_point[2], 1.0)

	# ② 変換実行
	renderer.WorldToDisplay()

	# ③ 画面座標を取得
	display_point = renderer.GetDisplayPoint()  # (x, y, z, w)
	x_disp, y_disp = display_point[0], display_point[1]

	# ④ 画面座標を「ピクセル座標」に合わせる（左下原点）
	#    ここではウィンドウサイズを取得
	win_size = renderer.GetRenderWindow().GetSize()
	width, height = win_size[0], win_size[1]
	# もし左上原点で扱いたい場合は y = height - y_disp など

	return x_disp, y_disp, width, height



class Renderer():
	def __init__(self, obj_path, json_path, images_path, size = [512,512], version = None, load_mesh = True, reduction = .0, debug = False):

		self._log = logging.getLogger(self.__class__.__name__)
		self._log.debug("START:")

		start_time = time.perf_counter()

		if bool(int(os.getenv('AG_FMA_RENDERER_USE_GPU', '0'))):
			pv.set_jupyter_backend('server')
		#pv.start_xvfb()
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
		self._actor_dict = {}
		self._prop_dict = {}
		self._bounds_dict = {}
		self._pick_dict = {}

		self._DEF_HEIGHT = 1800

		#self._file_extensions = '.obj'
		#self._file_extensions = '.gltf'
		#self._file_extensions = '.glb'
		#self._file_extensions = '.vtp'
		#self._file_extensions = '.vtk'
		self._file_extensions = '.ply'
		#self._reduction = 0

		#total_file_size = 0
		versions_json = None

		versions_file_path = os.path.join(json_path,'versions_file.json')
		if os.path.isfile(versions_file_path):
			self._log.debug(versions_file_path)
			#total_file_size += os.path.getsize(versions_file_path)
			json_open = open(versions_file_path, encoding='utf-8')
			versions_json = json.load(json_open)
			json_load_keys = list(versions_json.keys())

			#self._versions = sorted([*json_load_keys], key=lambda x: json_load[x]['order'], reverse=True)

			if self._debug:
				self._versions = sorted(filter(lambda x: isinstance(versions_json[x], dict),json_load_keys), key=lambda x:versions_json[x]['order'], reverse=True)
			else:
				self._versions = sorted(filter(lambda x: isinstance(versions_json[x], dict) and versions_json[x]['mv_publish'],json_load_keys), key=lambda x:versions_json[x]['order'], reverse=True)

			#self._versions = sorted(json_load.keys(), reverse=True)
			#print(versions)
		self._log.debug(self._versions)
		self._log.debug(self._reduction)

#		exit(1)

		#if self._debug:
		#	print("__init__():EXEC:",inspect.currentframe().f_lineno, version, file=sys.stderr)

		if version and version not in self._versions:
			version = self._versions[0]
		if version:
			self._versions = [version]

		self._log.debug(version)
		#exit(1)

		self._log.debug(time.perf_counter() - start_time if debug else None)
		if load_mesh:
			for v in self._versions:
				file_path = os.path.join(json_path,'renderer_file',v+'.json')
				self._log.debug(file_path)
				if not os.path.isfile(file_path):
					continue
				#total_file_size += os.path.getsize(file_path)

				#i = 0
				#vtm_file_base_path = os.path.join(obj_path,v)
				#vtm_file_path = vtm_file_base_path+"_%03d.vtm" % i
				vtm_file_path = None
				if vtm_file_path and os.path.isfile(vtm_file_path):
					while vtm_file_path and os.path.isfile(vtm_file_path):
						self._log.debug(vtm_file_path)
						mb = pv.read(vtm_file_path)
						for art_id in mb.keys():
							self._actor_dict[art_id] = self._plotter.add_mesh(mb[art_id], color='#F0D2A0', name=art_id)
							self._prop_dict[art_id] = self._actor_dict[art_id].prop
							self._bounds_dict[art_id] = self._actor_dict[art_id].bounds

						i += 1
						vtm_file_path = vtm_file_base_path+"_%03d.vtm" % i

				else:
					self._log.debug(time.perf_counter() - start_time if debug else None)

					json_open = open(file_path, encoding='utf-8')
					json_load = json.load(json_open)
					self._renderer_info_dict[v] = json_load[v]

					if load_mesh and isinstance(json_load[v], dict) and 'ids' in json_load[v] and isinstance(json_load[v]['ids'], dict) and 'art_ids' in json_load[v] and isinstance(json_load[v]['art_ids'], dict):

						ids_dict = json_load[v]['ids']
						objs_dict = json_load[v]['art_ids']

						if bool(int(os.getenv('AG_FMA_RENDERER_SAVE_DATAS', '0'))):
							#'''
							import shutil
							app_path = os.getenv('AG_FMA_RENDERER_APP_PATH', os.path.abspath(os.path.dirname(__file__)))
							base_path = os.getenv('AG_FMA_RENDERER_BASE_PATH', os.path.abspath(os.path.join(app_path, '..')))
							htdocs_path = os.getenv('AG_FMA_RENDERER_HTDOCS_PATH', os.path.join(base_path, 'htdocs'))
							#self._log.debug(__file__)
							#self._log.debug(app_path)

							datas_copy_base_path = os.path.abspath(os.path.join(app_path, 'datas', v))
							if not os.path.isdir(datas_copy_base_path):
								os.makedirs(datas_copy_base_path, exist_ok=True)

							datas_copy_htdocs_path = os.path.abspath(os.path.join(datas_copy_base_path, 'htdocs'))
							if not os.path.isdir(datas_copy_htdocs_path):
								shutil.copytree(htdocs_path, datas_copy_htdocs_path)

							datas_copy_obj_path = os.path.abspath(os.path.join(datas_copy_base_path, 'objs'))
							if not os.path.isdir(datas_copy_obj_path):
								os.makedirs(datas_copy_obj_path, exist_ok=True)

							datas_copy_json_path = os.path.abspath(os.path.join(datas_copy_base_path, 'renderer_file'))
							if not os.path.isdir(datas_copy_json_path):
								os.makedirs(datas_copy_json_path, exist_ok=True)

							shutil.copy2(versions_file_path, datas_copy_json_path)

							file_copy_path = os.path.join(datas_copy_json_path,'versions_file.json')
							d = {v: versions_json[v]}
							d[v]['mv_publish'] = True
							with open(file_copy_path, 'w') as f:
								json.dump(d, f, indent=2)

							datas_json_copy_path = os.path.abspath(os.path.join(datas_copy_json_path,'renderer_file'))
							if not os.path.isdir(datas_json_copy_path):
								os.makedirs(datas_json_copy_path, exist_ok=True)
							shutil.copy2(file_path, datas_json_copy_path)

							for art_id in objs_dict:
								file_path = os.path.join(self._obj_path,art_id+self._file_extensions)
								if not os.path.isfile(file_path):
									continue
								#total_file_size += os.path.getsize(file_path)
								file_copy_path = os.path.join(datas_copy_obj_path,art_id+self._file_extensions)
								if os.path.isfile(file_copy_path):
									continue
								#self._log.debug(file_path)
								shutil.copy2(file_path, datas_copy_obj_path)

							#self._log.debug(total_file_size)

							self._json_path = datas_copy_json_path
							self._obj_path = datas_copy_obj_path

							#total_file_size = None
							#'''

						if self._debug:
							#self._load_actor(self._plotter, id_list=['FMA52847'], ids_dict=ids_dict)
							#self._load_actor(self._plotter, id_list=['FMA5018'], ids_dict=ids_dict)
							#self._load_actor(self._plotter, id_list=['FMA7309','FMA7310'], ids_dict=ids_dict)
							#self._load_actor(self._plotter, id_list=['FMA52847','FMA7309','FMA7310'], ids_dict=ids_dict)
							#self._load_actor(self._plotter, id_list=['FMA58241','FMA58295','FMA5823'], ids_dict=ids_dict)
							self._load_actor(self._plotter, id_list=sorted(ids_dict.keys()), ids_dict=ids_dict, objs_dict=objs_dict)
						else:
							self._load_actor(self._plotter, id_list=sorted(ids_dict.keys()), ids_dict=ids_dict, objs_dict=objs_dict)

					self._log.debug(time.perf_counter() - start_time if debug else None)
					del ids_dict, objs_dict
					gc.collect()

				del json_open, json_load
				gc.collect()

				#if version and version == v:
				#	break
				#elif self._debug:
				#	break

		del versions_json
		gc.collect()

		#self._log.debug(time.perf_counter() - start_time if debug else None)
		#self._log.debug("END")
		self._log.info("elapsed: %f", time.perf_counter() - start_time)


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

	def expand_hex_color(self, code: str) -> str:
		# 先頭の # を無視して 3 桁か 6 桁か判定
		stripped = code.lstrip('#')
		if len(stripped) == 3:
			# 3 桁なら各文字を 2 回繰り返す
			return '#' + ''.join(ch * 2 for ch in stripped)
		elif len(stripped) == 6:
			# すでに 6 桁ならそのまま
			return '#' + stripped
		else:
			raise ValueError(f"Unexpected hex color format: {code}")

	def animation(self, query, script_path=None, payload:Payload=None):

		param_list = list(query.keys());
		self._log.debug(param_list)

		version = query.get('version') or 'latest'
		self._log.debug(version)

		size_list = (512, 512)
		size_str = query.get('size') or '512x512'
		self._log.debug(size_str)
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
		self._log.debug(reduction)

		zoom = None
		zoom_str = query.get('zoom')
		if zoom_str and is_num(zoom_str):
			zoom = float(zoom_str)
		self._log.debug(zoom)

		id_list = []
		id_property_dict = {}
		if 'id' in param_list:
			#id_list = sorted(query.getall('id'))
			#temp_id_list = query.getall('id')
			#temp_id_list = query.get('id')
			temp_id_list = query.getall('id') if hasattr(query, 'getall') else query.get('id')
			if isinstance(temp_id_list, str) and len(temp_id_list)>0:
				temp_id_list = [temp_id_list]
			for id in temp_id_list:
				if ',' in id:
					id_list.extend(id.split(','))
				else:
					id_list.append(id)

			for id in id_list:
				id_property_dict[id] = {'color':None,'opacity':1.0}

			self._log.debug(id_list)
			self._log.debug(id_property_dict)

		focusid_list = None
		if 'focusid' in param_list:
			#temp_id_list = query.getall('focusid')
			#temp_id_list = query.get('focusid')
			temp_id_list = query.getall('focusid') if hasattr(query, 'getall') else query.get('focusid')
			if isinstance(temp_id_list, str) and len(temp_id_list)>0:
				temp_id_list = [temp_id_list]
			if isinstance(temp_id_list, list) and len(temp_id_list) > 0:
				focusid_list = []
				for id in temp_id_list:
					if not len(id) > 0:
						continue
					if ',' in id:
						focusid_list.extend(id.split(','))
					else:
						focusid_list.append(id)
		self._log.debug(focusid_list)

		if 'rgb' in param_list:
			#rgb_list = query.getall('rgb')
			#rgb_list = query.get('rgb')
			rgb_list = query.getall('rgb') if hasattr(query, 'getall') else query.get('rgb')
			if isinstance(rgb_list, str) and len(rgb_list)>0:
				rgb_list = [rgb_list]
			rgb_cnt = 0
			for rgb in rgb_list:
				if ',' in rgb:
					for rgb1 in rgb.split(','):
						if len(rgb1) == 3 or len(rgb1) == 6:
							id_property_dict[id_list[rgb_cnt]]['color'] = self.expand_hex_color(rgb1)
						rgb_cnt += 1
						if rgb_cnt >= len(id_list):
							break
				else:
					if len(rgb) == 3 or len(rgb) == 6:
						id_property_dict[id_list[rgb_cnt]]['color'] = self.expand_hex_color(rgb)
					rgb_cnt += 1
					if rgb_cnt >= len(id_list):
						break

			self._log.debug(id_property_dict)

		if 'opacity' in param_list:
			#opacity_list = query.getall('opacity')
			#opacity_list = query.get('opacity')
			opacity_list = query.getall('opacity') if hasattr(query, 'getall') else query.get('opacity')
			self._log.debug(opacity_list)
			if isinstance(opacity_list, str) and len(opacity_list)>0:
				opacity_list = [opacity_list]
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

		self._log.debug(id_property_dict)

		expansion = 'art_ids'
		if 'expansion' in param_list:
			#expansion_list = query.getall('expansion')
			#expansion_list = query.get('expansion')
			expansion_list = query.getall('expansion') if hasattr(query, 'getall') else query.get('expansion')
			if isinstance(expansion_list, str) and len(expansion_list)>0:
				expansion_list = [expansion_list]
			if isinstance(expansion_list, list) and len(expansion_list)>0 and is_str(expansion_list[0]) and len(expansion_list[0])>0 :
				expansion_str = expansion_list[0].lower()
				if expansion_str == 'is_a' or expansion_str == 'isa':
					expansion = 'art_ids_isa'
				elif expansion_str == 'part_of' or expansion_str == 'partof':
					expansion = 'art_ids_partof'
				elif expansion_str == 'none':
					expansion = 'art_ids_none'

		if payload is None:
			payload = query.get('payload') or None
		self._log.debug(payload)

		methods = query.get('methods') or None
		self._log.debug(methods)

		image_filepath = self._animation(
			size=size_list,
			version=version,
			id_list=id_list,
			id_property_dict=id_property_dict,
			focusid_list=focusid_list,
			expansion=expansion,
			script_path=script_path,
			reduction=reduction,
			zoom=zoom,
			payload=payload,
			methods=methods
		)
		return image_filepath


	def image(self, query, script_path=None, payload:Payload=None):

		param_list = list(query.keys());
		self._log.debug(param_list)

		version = query.get('version') or 'latest'
		self._log.debug(version)

		size_list = [512, 512]
		size_str = query.get('size') or '512x512'
		self._log.debug(size_str)
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
		self._log.debug(reduction)

		zoom = None
		zoom_str = query.get('zoom')
		if zoom_str and is_num(zoom_str):
			zoom = float(zoom_str)
		self._log.debug(zoom)

		azimuth = 0
		elevation = 0

		ha_str = query.get('ha')
		if ha_str and is_num(ha_str):
			azimuth = int(ha_str)
		self._log.debug(azimuth)

		va_str = query.get('va')
		if va_str and is_num(va_str):
			elevation = int(va_str)
		self._log.debug(elevation)

		id_list = []
		id_property_dict = {}
		if 'id' in param_list:
			#id_list = sorted(query.getall('id'))
			#temp_id_list = query.getall('id')
			#temp_id_list = query.get('id')
			temp_id_list = query.getall('id') if hasattr(query, 'getall') else query.get('id')
			if isinstance(temp_id_list, str) and len(temp_id_list)>0:
				temp_id_list = [temp_id_list]
			for id in temp_id_list:
				if ',' in id:
					id_list.extend(id.split(','))
				else:
					id_list.append(id)

			for id in id_list:
				id_property_dict[id] = {'color':None,'opacity':1.0}

			self._log.debug(id_list)
			self._log.debug(id_property_dict)

		focusid_list = None
		if 'focusid' in param_list:
			#temp_id_list = query.getall('focusid')
			#temp_id_list = query.get('focusid')
			temp_id_list = query.getall('focusid') if hasattr(query, 'getall') else query.get('focusid')
			if isinstance(temp_id_list, str) and len(temp_id_list)>0:
				temp_id_list = [temp_id_list]
			if isinstance(temp_id_list, list) and len(temp_id_list) > 0:
				focusid_list = []
				for id in temp_id_list:
					if not len(id) > 0:
						continue
					if ',' in id:
						focusid_list.extend(id.split(','))
					else:
						focusid_list.append(id)
		self._log.debug(focusid_list)

		if 'rgb' in param_list:
			#rgb_list = query.getall('rgb')
			#rgb_list = query.get('rgb')
			rgb_list = query.getall('rgb') if hasattr(query, 'getall') else query.get('rgb')
			if isinstance(rgb_list, str) and len(rgb_list)>0:
				rgb_list = [rgb_list]
			rgb_cnt = 0
			for rgb in rgb_list:
				if ',' in rgb:
					for rgb1 in rgb.split(','):
						if len(rgb1) == 3 or len(rgb1) == 6:
							id_property_dict[id_list[rgb_cnt]]['color'] = self.expand_hex_color(rgb1)
						rgb_cnt += 1
						if rgb_cnt >= len(id_list):
							break
				else:
					if len(rgb) == 3 or len(rgb) == 6:
						id_property_dict[id_list[rgb_cnt]]['color'] = self.expand_hex_color(rgb)
					rgb_cnt += 1
					if rgb_cnt >= len(id_list):
						break

			self._log.debug(id_property_dict)

		if 'opacity' in param_list:
			#opacity_list = query.getall('opacity')
			#opacity_list = query.get('opacity')
			opacity_list = query.getall('opacity') if hasattr(query, 'getall') else query.get('opacity')
			self._log.debug(opacity_list)
			if isinstance(opacity_list, str) and len(opacity_list)>0:
				opacity_list = [opacity_list]
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

		self._log.debug(id_property_dict)

		expansion = 'art_ids';
		if 'expansion' in param_list:
			#expansion_list = query.getall('expansion')
			#expansion_list = query.get('expansion')
			expansion_list = query.getall('expansion') if hasattr(query, 'getall') else query.get('expansion')
			self._log.debug(expansion_list)
			if isinstance(expansion_list, str) and len(expansion_list)>0:
				expansion_list = [expansion_list]
			if isinstance(expansion_list, list) and len(expansion_list)>0 and is_str(expansion_list[0]) and len(expansion_list[0])>0 :
				expansion_str = expansion_list[0].lower()
				if expansion_str == 'is_a' or expansion_str == 'isa':
					expansion = 'art_ids_isa'
				elif expansion_str == 'part_of' or expansion_str == 'partof':
					expansion = 'art_ids_partof'
				elif expansion_str == 'none':
					expansion = 'art_ids_none'
		self._log.debug(expansion)

		if payload is None:
			payload = query.get('payload') or None
		self._log.debug(payload)

		methods = query.get('methods') or None
		self._log.debug(methods)

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
			zoom=zoom,
			payload=payload,
			methods=methods
		)
		return image_filepath


	def _read_mesh_file(self, file_path):
		if is_gltf_or_glb(file_path):
			block = pv.read(file_path)
			return block[0][0][0][0]
		else:
			return pv.read(file_path)


	def _read_mesh_data(self, art_id, reduction = None):

		#self._log.debug("art_id: %s", art_id)
		mesh = None

		if reduction is None:
			reduction = self._reduction

		file_path = os.path.join(self._obj_path,art_id+self._file_extensions)
		if os.path.isfile(file_path):
			#self._log.debug("exists: %s", file_path)
			if reduction and reduction > .0:
				file_reduction_path = os.path.join(self._obj_path,art_id + ("_%03d" % (int(reduction * 100))) + self._file_extensions)
				if os.path.isfile(file_reduction_path):
					#self._log.debug("exists: %s", file_reduction_path)
					#return self._read_mesh_file(file_reduction_path)
					mesh = self._read_mesh_file(file_reduction_path)
					#mesh = mesh.smooth(n_iter=100, relaxation_factor=0.02)
					#return pv.PolyData(mesh)

				else:
					mesh = self._read_mesh_file(file_path)

					decimate = vtk.vtkQuadricDecimation()
					decimate.SetInputData(mesh)
					decimate.SetTargetReduction(reduction)
					decimate.Update()

					#decimate = vtk.vtkDecimatePro()
					#decimate.SetInputData(mesh)
					#decimate.SetTargetReduction(reduction)
					#decimate.PreserveTopologyOn()
					#decimate.Update()

					mesh = decimate.GetOutput()
					#mesh = float32_array(mesh)

					del decimate
					gc.collect()

					#return pv.PolyData(decimate.GetOutput())
					#return mesh
			else:
				#return self._read_mesh_file(file_path)
				mesh = self._read_mesh_file(file_path)
				#return mesh

		return float32_array(mesh)

		#else:
		#	#self._log.debug("none: %s",file_path)
		#	return None
		#return mesh




	def _load_mesh(self,
								id_list=None,
								id_property_dict=None,
								expansion='art_ids',
								ids_dict=None,
								objs_dict=None,
								default_color='#F0D2A0',
								plotter=None,
								reduction=0.0):
		# 1. 変数をローカルにキャッシュ
		actor_dict   = self._actor_dict
		prop_dict    = self._prop_dict
		bounds_dict  = self._bounds_dict
		pick_dict    = self._pick_dict
		debug        = self._debug
		start_time = time.perf_counter() if debug else None

		self._log.debug("expansion=[{}]".format(expansion))

		# 2. 速い集合/リスト変換
		exists_actor_set = set(actor_dict.keys()) if actor_dict else set()
		objs_set        = set(objs_dict.keys()) if objs_dict else set()

		# 3. id_set の作成（depth がキー）
		ids_dict = ids_dict or {}
		id_set   = sorted(set(id_list or []), key=lambda x: ids_dict[x]['depth'])
		id_set   = [id_ for id_ in id_set if id_ in ids_dict]  # 先にフィルタ

		# 4. アート ID とプロパティを一括取得
		#    （重複を避けつつ、obj_property_dict を一度に構築）
		art_id_list = []
		obj_property_dict = {}
		for id_ in id_set:
			id_dict = ids_dict.get(id_, {})
			arts = id_dict.get(expansion, [])
			if not isinstance(arts, list):          # ここで一度だけチェック
				continue

			art_id_list.extend(arts)

			# id_property_dict が dict であればそれを使い、無ければデフォルト
			prop = id_property_dict.get(id_, None)
			if not isinstance(prop, dict):
				prop = {'color': None, 'opacity': 1.0}

			for art_id in arts:
				obj_property_dict[art_id] = prop

		self._log.debug("built art_id_list, props: %d", len(art_id_list))
		self._log.debug("elapsed: %f", time.perf_counter() - start_time if debug else None)

		# 5. 一度だけで済む集合
		load_mesh_set = set(art_id_list)
		#load_mesh_list = list(set(load_mesh_set) & set(exists_actor_set))
		load_mesh_list = [x for x in exists_actor_set if x in load_mesh_set]
		unload_mesh_set = [x for x in exists_actor_set if x not in load_mesh_set]
		self._log.debug("exists_actor_set, props: %d", len(exists_actor_set))
		self._log.debug("load_mesh_set, props: %d", len(load_mesh_set))
		self._log.debug("load_mesh_list, props: %d", len(load_mesh_list))
		self._log.debug("unload_mesh_set, props: %d", len(unload_mesh_set))
		self._log.debug("elapsed: %f", time.perf_counter() - start_time if debug else None)

		bbox = vtk.vtkBoundingBox()

		# 6. 既存アクターの更新
		for art_id in load_mesh_list:
			actor = actor_dict[art_id]

			if not actor.visibility:
				actor.visibility = True
				#self._log.debug("visibility %s", actor.visibility)

			if art_id in objs_set and isinstance(objs_dict[art_id], dict):
				col = (obj_property_dict[art_id]['color'] or objs_dict[art_id]['color'] or default_color).lower()
				opa = obj_property_dict[art_id]['opacity']

				prop = prop_dict[art_id]
				if prop.color != col:
					prop.color   = col
					#self._log.debug("color %s", prop.color)
				if prop.opacity != opa:
					prop.opacity = opa
					#self._log.debug("opacity %f", prop.opacity)

			bbox.AddBounds(bounds_dict[art_id])

			load_mesh_set.discard(art_id)          # O(1) 削除

		self._log.debug("updated existing actors: elapsed: %f", time.perf_counter() - start_time if debug else None)

		for art_id in unload_mesh_set:
			actor = actor_dict[art_id]
			actor.visibility = False
			#self._log.debug("visibility %s", actor.visibility)

		self._log.debug("updated existing actors: elapsed %f", time.perf_counter() - start_time if debug else None)

		# 7. 読み込みが必要なアート ID だけ処理
		self._log.debug("len(load_mesh_set): %d", len(load_mesh_set))
		for art_id in load_mesh_set:
			# 既にアクターが存在している場合は読み込む必要なし
			if art_id in exists_actor_set:
				continue

			# ここが I/O の重い部分
			self._read_mesh(art_id, reduction=reduction)

			# さらに Plotter へ追加
			if not plotter or not actor_dict.get(art_id):
				continue

			mesh = self._read_mesh_data(art_id)

			if art_id in objs_set and isinstance(objs_dict[art_id], dict):
				actor_dict[art_id] = plotter.add_mesh(mesh, color=objs_dict[art_id].get('color', default_color), show_edges=False, smooth_shading=True, name=art_id)
			else:
				actor_dict[art_id] = plotter.add_mesh(mesh, color=default_color, show_edges=False, smooth_shading=True, name=art_id)

			prop_dict[art_id] = actor_dict[art_id].prop
			bounds_dict[art_id] = actor_dict[art_id].bounds
			pick_dict[actor_dict[art_id].name] = art_id

			bbox.AddBounds(bounds_dict[art_id])

		self._log.debug("finished")
		self._log.debug("elapsed %f", time.perf_counter() - start_time if debug else None)

		bounds = [0,0,0,0,0,0]
		bbox.GetBounds(bounds)
		del bbox
		return bounds

	def _load_actor(self, plotter, id_list=[], ids_dict={}, objs_dict={}, default_color='#F0D2A0',visibility=True):

		actor_dict  = self._actor_dict
		prop_dict   = self._prop_dict
		bounds_dict = self._bounds_dict
		pick_dict   = self._pick_dict
		debug       = self._debug
		start_time = time.perf_counter() if debug else None
		self._log.debug("START")

		art_ids_list = [
			aid
			for id_ in id_list
			if (id_dict := ids_dict.get(id_))
			and isinstance(id_dict, dict)
			and isinstance((art_ids := id_dict.get('art_ids')), list)
			for aid in art_ids
		]

		art_ids_set = sorted(set(art_ids_list))
		art_ids_len = len(art_ids_set)
		art_ids_count = 0
		self._log.debug("art_ids_len: %d", art_ids_len)

		step_start_time = time.perf_counter() if debug else None

		for art_id in art_ids_set:
			art_ids_count+=1
			print("\r[%5d/%5d]:[%-10s]" % (art_ids_count,art_ids_len,art_id), end="", file=sys.stderr) if debug else None
			color = objs_dict[art_id]['color'] if isinstance(objs_dict[art_id], dict) and isinstance(objs_dict[art_id]['color'], str) and len(objs_dict[art_id]['color'])>0 else default_color
			mesh = self._read_mesh_data(art_id)
			actor_dict.update({art_id: plotter.add_mesh(
				mesh,
				color=color,
				show_edges=False,
				smooth_shading=True,
				#name=art_id,
				render=False,
				reset_camera=False,
				pickable=True
			)})
			#print(":[%f]" % (time.perf_counter() - step_start_time), end="", file=sys.stderr) if debug else None
			prop_dict[art_id] = actor_dict[art_id].prop
			#print(":[%f]" % (time.perf_counter() - step_start_time), end="", file=sys.stderr) if debug else None
			bounds_dict[art_id] = actor_dict[art_id].bounds
			#print(":[%f]" % (time.perf_counter() - step_start_time), end="", file=sys.stderr) if debug else None
			pick_dict[actor_dict[art_id].name] = art_id
		print("", file=sys.stderr)
		self._log.debug("END: elapsed: %f", time.perf_counter() - start_time if debug else None)


	def _get_bounds(self, id_list=[], expansion='art_ids', ids_dict={}, objs_dict={}, plotter=None, default_color='#F0D2A0'):
		actor_dict  = self._actor_dict
		prop_dict   = self._prop_dict
		bounds_dict = self._bounds_dict
		debug  = self._debug
		self._log.debug(id_list)
		start_time = time.perf_counter() if debug else None

		exists_actor_list = []
		if actor_dict and isinstance(actor_dict, dict) and len(actor_dict.keys())>0:
			exists_actor_list = set(actor_dict.keys())

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

			self._log.debug(id)

			load_mesh_list.extend(id_dict[expansion])


		load_mesh_set = sorted(set(load_mesh_list))

		bbox = vtk.vtkBoundingBox()

		for art_id in exists_actor_list:
			if art_id in load_mesh_set:
				bbox.AddBounds(bounds_dict[art_id])

				load_mesh_set.remove(art_id)	#読み込み済みの場合はリストから削除

		for art_id in load_mesh_set:
			if art_id in exists_actor_list:
				continue

			self._read_mesh(art_id)

			self._log.debug(art_id)

			if not plotter:
				continue

			mesh = self._read_mesh_data(art_id)
			actor_dict[art_id] = plotter.add_mesh(mesh, color=default_color, show_edges=False, smooth_shading=True, name=art_id)
			actor_dict[art_id].visibility = False
			prop_dict[art_id] = actor_dict[art_id].prop
			bounds_dict[art_id] = actor_dict[art_id].bounds
			bbox.AddBounds(bounds_dict[art_id])

		bounds = [0,0,0,0,0,0]
		bbox.GetBounds(bounds)
		del bbox
		return bounds


	def _openPlotter(self, size = [512,512], forced=False):

		#print("_openPlotter():START:",inspect.currentframe().f_lineno, size, forced, self._plotter, file=sys.stderr)

		if forced:
			self._plotter = pv.Plotter(off_screen=True, window_size=size)
			self._plotter.enable_parallel_projection()
			#self._plotter.disable_anti_aliasing()
			#self._log.debug(pv.global_theme.multi_samples)
			#self._plotter.add_bounding_box(line_width=5, color='black')
			self._plotter.camera_position = 'xz'

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
			#plotter.disable_anti_aliasing()
			plotter.camera_position = 'xz'
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


	def _execMakeAnimation(self, size = [512,512], id_list=[], id_property_dict={}, focusid_list=None, expansion='art_ids', ids_dict={}, objs_dict={}, range_step=12, reduction=None, start_time=None, image_filepath=None, zoom=None, payload:Payload=None, methods:str=None):

		debug        = self._debug
		start_time = time.perf_counter() if debug else None
		self._log.debug("START: %f",time.perf_counter() - start_time if debug else None)

		plotter = self._openPlotter(size=size)

		self._log.debug("EXEC: %f",time.perf_counter() - start_time if debug else None)
		bounds = self._load_mesh(id_list=id_list, id_property_dict=id_property_dict, expansion=expansion, ids_dict=ids_dict, objs_dict=objs_dict, plotter=plotter, reduction=reduction)
		self._log.debug("EXEC: %f",time.perf_counter() - start_time if debug else None)

		#bounds = None
		if isinstance(focusid_list, list) and len(focusid_list) > 0:
			bounds = self._get_bounds(id_list=focusid_list, expansion=expansion, ids_dict=ids_dict, objs_dict=objs_dict, plotter=plotter)
			self._log.debug(bounds)

		#plotter.camera_position = 'xz'
		plotter.camera.azimuth = 0
		plotter.camera.elevation = 0
		#plotter.camera.zoom(zoom)
		plotter.camera.zoom(1.0)
		#plotter.camera.reset_clipping_range()
		plotter.renderer.reset_camera(render=True, bounds=bounds)

		y_range = None
		if zoom != None and is_num(zoom) and zoom >= 1.0 :
			y_range = self.getZoomYRange((zoom - 1.0) / 5.0)
			self._log.debug(y_range)
			plotter.camera.SetParallelScale(y_range / 2.0)

		self._log.debug("EXEC: %f",time.perf_counter() - start_time if debug else None)

		#plotter.open_gif(tmp_filepath, fps = 5)	# default fps = 10
		plotter.open_gif(image_filepath, fps = 5)	# default fps = 10
		self._log.debug("EXEC: %f",time.perf_counter() - start_time if debug else None)
		for_start_time = time.perf_counter() if debug else None
		for i in range(0,360,range_step):
			plotter.camera.azimuth = i
			#plotter.camera.reset_clipping_range()
			plotter.renderer.reset_camera(render=False, bounds=bounds)
			if zoom != None :
				plotter.camera.SetParallelScale(y_range / 2.0)
			plotter.write_frame()
			if debug:
				for_end_time = time.perf_counter()
				self._log.debug("EXEC:%d %f %f", i, for_end_time - start_time, for_end_time - for_start_time)
				for_start_time = for_end_time
		#plotter.close()
		plotter.mwriter.close()

		if debug:
			self._log.debug("EXEC: %f %f", time.perf_counter() - start_time, time.perf_counter() - for_start_time)

		#if os.path.isfile(image_filepath):
		#	os.remove(image_filepath)

		self._log.debug("EXEC: %f",time.perf_counter() - start_time if debug else None)

		#shutil.move(tmp_filepath, image_path)

		self._log.debug("EXEC: %f",time.perf_counter() - start_time if debug else None)

		self._closePlotter(plotter)

		self._log.debug("EXEC: %f",time.perf_counter() - start_time if debug else None)


	def _execMakeImage(self, size = [512,512], id_list=[], id_property_dict={}, focusid_list=None, expansion='art_ids', ids_dict={}, objs_dict={}, reduction=None, start_time=None, image_filepath=None, azimuth=0, elevation=0, zoom=None, payload:Payload=None, methods:str=None):

		debug        = self._debug
		start_time = time.perf_counter() if debug else None

		self._log.debug("START")
		self._log.debug(size)

		plotter = self._openPlotter(size=size)

		bounds = self._load_mesh(id_list=id_list, id_property_dict=id_property_dict, expansion=expansion, ids_dict=ids_dict, objs_dict=objs_dict, plotter=plotter, reduction=reduction)
		self._log.debug(time.perf_counter() - start_time if debug else None)

		#bounds = None
		if isinstance(focusid_list, list) and len(focusid_list) > 0:
			bounds = self._get_bounds(id_list=focusid_list, expansion=expansion, ids_dict=ids_dict, objs_dict=objs_dict, plotter=plotter)
			self._log.debug(bounds)
		self._log.debug(bounds)

		self._log.debug(time.perf_counter() - start_time if debug else None)

		#plotter.camera_position = 'xz'
		self._log.debug(time.perf_counter() - start_time if debug else None)
		camera = plotter.camera
		self._log.debug(time.perf_counter() - start_time if debug else None)
		camera.azimuth = azimuth
		self._log.debug(time.perf_counter() - start_time if debug else None)
		camera.elevation = elevation
		self._log.debug(time.perf_counter() - start_time if debug else None)
		#plotter.camera.zoom(zoom)
		camera.zoom(1.0)
		self._log.debug(time.perf_counter() - start_time if debug else None)
		#plotter.camera.zoom('tight')
		#plotter.camera.tight(padding=0.05, view='xz', adjust_render_window=False)
		#plotter.camera.reset_clipping_range()

		self._log.debug(time.perf_counter() - start_time if debug else None)

		plotter.renderer.reset_camera(render=False, bounds=bounds)

		#self._log.debug(camera)
		#self._log.debug(camera.__dict__)
		#self._log.debug(camera.position)
		#self._log.debug(camera.focal_point)
		#self._log.debug(camera.up)
		#self._log.debug(plotter.camera_position)
		self._log.debug(time.perf_counter() - start_time if debug else None)

		#y_range = self._DEF_HEIGHT
		if zoom != None and is_num(zoom) and zoom >= 1.0 :
			y_range = self.getZoomYRange((zoom - 1.0) / 5.0)
			self._log.debug(y_range)
			camera.SetParallelScale(y_range / 2.0)

		self._log.debug(time.perf_counter() - start_time if debug else None)

		#self._log.debug(payload)
		#if isinstance(payload, Payload):
		#	self._log.debug(payload.methods)
		#if isinstance(methods, str):
		#	self._log.debug(methods)
		#	self._log.debug(image_filepath)

		#z = self.getYRangeZoom(camera.GetParallelScale()*2.0)
		#self._log.debug(z)

		if isinstance(methods, str) and (methods == 'focus' or methods == 'pick' or methods == 'map'):
			self._log.debug(methods)
			d = "{}"
			if methods == 'focus':
				cp = plotter.camera_position
				#self._log.debug(cp)
				#self._log.debug(cp[0][0])
				#self._log.debug(type(cp[0][0]))
				z = self.getYRangeZoom(camera.GetParallelScale()*2.0)
				#self._log.debug(z)
				camera = CameraJson(
					CameraX=cp[0][0],
					CameraY=cp[0][1],
					CameraZ=cp[0][2],
					TargetX=cp[1][0],
					TargetY=cp[1][1],
					TargetZ=cp[1][2],
					CameraUpVectorX=cp[2][0],
					CameraUpVectorY=cp[2][1],
					CameraUpVectorZ=cp[2][2],
					Zoom=z
				)
				#self._log.debug(camera)

				d = Focus(Camera=camera).json()
				#self._log.debug(d)
				#dj = d.json()
				#self._log.debug(dj)
				#self._log.debug(d.json(indent=2))


				#self._log.debug(d.json(indent=2))

			elif methods == 'pick':
				if isinstance(payload, Payload) and isinstance(payload.pick, Pick) and isinstance(payload.pick.screen_pos_x, int) and isinstance(payload.pick.screen_pos_y, int):
					pick = payload.pick
					self._log.debug(pick.json())
					pick_pos, pick_normal, pick_name = pick_world_from_screen(plotter, pick.screen_pos_x, pick.screen_pos_y)
					self._log.debug(pick_pos)
					self._log.debug(type(pick_pos))
					self._log.debug(pick_normal)
					self._log.debug(type(pick_normal))
					self._log.debug(pick_name)
					self._log.debug(self._pick_dict[pick_name])

					if isinstance(pick_pos, tuple) and isinstance(pick_normal, tuple):
						up = camera.up

						pin = PinJson(
							PinX=pick_pos[0],
							PinY=pick_pos[1],
							PinZ=pick_pos[2],
							PinArrowVectorX=pick_normal[0],
							PinArrowVectorY=pick_normal[1],
							PinArrowVectorZ=pick_normal[2],
							PinUpVectorX=up[0],
							PinUpVectorY=up[1],
							PinUpVectorZ=up[2],
							PinPartID=self._pick_dict[pick_name]
						)
						d = PickList(Pin=[pin]).json()
						#self._log.debug(picklist)
						#self._log.debug(picklist.json())

					else:
						d = PickList(Pin=[]).json()

					pass
				else:

					d = PickList(Pin=[]).json()

					pass

			elif methods == 'map':
				if isinstance(payload, Payload) and isinstance(payload.pin, list) and isinstance(payload.pin[0], Pin):
					self._log.debug(payload.pin)
					maplist = []
					for pin in payload.pin:
						screen_x, screen_y, win_w, win_h = world_to_screen(plotter, (pin.pin_x, pin.pin_y, pin.pin_z))
						self._log.debug(f"{screen_x}, {screen_y}")
						maplist.append( Map(PinX=pin.pin_x, PinY=pin.pin_y, PinZ=pin.pin_z, PinScreenX=int(screen_x), PinScreenY=int(screen_y)) )
					d = MapList(Map=maplist).json()

				else:
					d = MapList(Map=[]).json()
				pass

			with open(image_filepath, "w", encoding="utf-8") as f:
				f.write(d)

		else:
			'''
			#zoomに関係なくpinのサイズを一定にする必要あり
			if isinstance(methods, str) and methods == 'image' and isinstance(payload, Payload):

				if isinstance(payload.pin, list) and len(payload.pin) > 0 and isinstance(payload.pin[0], Pin):
					pinlist = payload.pin
					for pin in pinlist:
						self._log.debug(pin.json())

						pin_shape = pin.pin_shape.upper() if isinstance(pin.pin_shape, str) and len(pin.pin_shape)>0 else 'CONE'
						pin_color = self.expand_hex_color(pin.pin_color)

						cam_pos = np.array(plotter.camera.position)
						dist = np.linalg.norm(cam_pos - (pin.pin_x,pin.pin_y,pin.pin_z))
						desired_length_pixels = pin.pin_size * 500 # 20.0
						scale_factor = desired_length_pixels / dist
						#scale_factor = 25.0
						self._log.debug(f"dist : {dist}")
						self._log.debug(f"desired_length_pixels : {desired_length_pixels}")
						self._log.debug(f"scale_factor : {scale_factor}")

						self._log.debug(dist)
						self._log.debug(scale_factor)

						start_point  = np.array([pin.pin_x,pin.pin_y,pin.pin_z])
						normal = np.array([pin.pin_arrow_vector_x,pin.pin_arrow_vector_y,pin.pin_arrow_vector_z])

						#end_point = start_point + (normal / np.linalg.norm(normal)) * scale_factor
						#pin_mesh = pv.Arrow(start=end_point, direction=-normal, scale=scale_factor)
						#self._log.debug(f"Start : {start_point}")
						#self._log.debug(f"End   : {end_point}")

						if pin_shape == 'PIN_LONG':
							scale_factor = scale_factor * 2
							start_point = start_point + (normal / np.linalg.norm(normal)) * (scale_factor / 2)
							end_point = start_point + (normal / np.linalg.norm(normal)) * (scale_factor / 2)
							pin_mesh = pv.Cone(center=start_point, direction=-normal, height=scale_factor, radius=scale_factor/32, resolution=12)
							self._log.debug(f"Start : {start_point}")
							self._log.debug(f"End   : {end_point}")
							plotter.add_mesh(pin_mesh, color="#C0C0C0", pickable=False)
							#plotter.add_mesh(pin_mesh, color="#FF0000", pickable=False)

							sphere_mesh = pv.Sphere(radius=scale_factor/8, center=end_point, direction=-normal)
							plotter.add_mesh(sphere_mesh, color=pin_color, pickable=False)

						#if pin_shape == 'CONE':
						else:
							start_point = start_point + (normal / np.linalg.norm(normal)) * (scale_factor / 2)
							end_point = start_point + (normal / np.linalg.norm(normal)) * (scale_factor / 2)
							pin_mesh = pv.Cone(center=start_point, direction=-normal, height=scale_factor, radius=scale_factor/2, resolution=12)
							self._log.debug(f"Start : {start_point}")
							self._log.debug(f"End   : {end_point}")
							plotter.add_mesh(pin_mesh, color=pin_color, pickable=False)


					#plotter.render()
				pass
			#self._log.debug(methods)
			'''

			plotter.screenshot(image_filepath)

		self._log.debug(time.perf_counter() - start_time if debug else None)

		'''
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
		'''

		self._closePlotter(plotter)
		self._log.debug("END")

		return image_filepath


	def _execMakeNoneImage(self, size = [512,512], image_filepath=None, payload:Payload=None, methods:str=None):
		self._log.debug("START")
		if isinstance(methods, str) and (methods == 'focus' or methods == 'pick' or methods == 'map'):
			self._log.debug(methods)
			d = "{}"
			if methods == 'focus':
				d = Focus(Camera={}).json()
			elif methods == 'pick':
				d = PickList(Pin=[]).json()
			elif methods == 'map':
				d = MapList(Map=[]).json()
			with open(image_filepath, "w", encoding="utf-8") as f:
				f.write(d)

		else:
			self._log.debug(size)
			plotter = self._openPlotter(size=size)
			self._load_mesh(plotter=plotter)
			if not (isinstance(methods, str) and methods == 'image'):
				plotter.add_text("No Image", position="upper_edge", font_size=30, color="black")
			plotter.camera.reset_clipping_range()
			plotter.screenshot(image_filepath)
			self._closePlotter(plotter)
		self._log.debug("END")
		return image_filepath


	def _makeAnimation(self, use_fork=True, use_multiprocessing=False, size = [512,512], id_list=[], id_property_dict={}, focusid_list=None, expansion='art_ids', ids_dict={}, objs_dict={}, range_step=12, reduction=None, start_time=None, image_filepath=None, zoom=None, payload:Payload=None, methods:str=None):

		use_fork = hasattr(os, 'fork')
		debug    = self._debug
		self._log.debug("START")

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
							zoom=zoom,
							payload=payload,
							methods=methods
						)

						os._exit(0)

					except OSError as e:
						self._log.debug("exec():{}".format(e))
						sys.exit(1)

				else:
					try:
						status = os.waitpid(pid, 0)[1]
					except OSError as e:
						self._log.debug("waitpid():{}".format(e))
						sys.exit(1)
					if os.WIFEXITED(status):
						if debug or status != 0:
							self._log.debug("END")
							self._log.debug("child (PID={}) finished: ".format(pid))
							self._log.debug("exit, status={}".format(os.WEXITSTATUS(status)))
					elif os.WIFSIGNALED(status):
						self._log.debug("END")
						self._log.debug("child (PID={}) finished: ".format(pid))
						self._log.debug("signal, sig={}".format(os.WTERMSIG(status)))
					else:
						self._log.debug("END")
						self._log.debug("child (PID={}) finished: ".format(pid))
						self._log.debug("abnormal exit")

			except OSError as e:
				self._log.debug("fork():{}".format(e))
				pass

		elif use_multiprocessing:

			kwargs = {
				'size': size,
				'id_list': id_list,
				'id_property_dict': id_property_dict,
				'focusid_list': focusid_list,
				'expansion': expansion,
				'ids_dict': ids_dict,
				'objs_dict': objs_dict,
				'range_step': range_step,
				'reduction': reduction,
				'start_time': start_time,
				'image_filepath': image_filepath,
				'zoom': zoom,
			}
			process = mp.Process(target=self._execMakeAnimation, kwargs=kwargs)
			process.start()
			process.join()

			if self._debug or process.exitcode != 0:
				self._log.debug("END")
				self._log.debug(f"child (PID={process.pid}) finished: ")

				if process.exitcode >= 0:
					self._log.debug(f"exit, status={process.exitcode}")
				else:
					self._log.debug(f"signal, sig={-process.exitcode}")

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
				zoom=zoom,
				payload=payload,
				methods=methods
			)


	def _makeImage(self, use_fork=True, use_multiprocessing=False, size = [512,512], id_list=[], id_property_dict={}, focusid_list=None, expansion='art_ids', ids_dict={}, objs_dict={}, reduction=None, start_time=None, image_filepath=None, azimuth=0, elevation=0, zoom=None, payload:Payload=None, methods:str=None):

		use_fork = hasattr(os, 'fork')
		debug    = self._debug
		self._log.debug("START")

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
							zoom=zoom,
							payload=payload,
							methods=methods
						)

						os._exit(0)

					except OSError as e:
						self._log.debug("exec():{}".format(e))
						sys.exit(1)

				else:
					try:
						status = os.waitpid(pid, 0)[1]
					except OSError as e:
						self._log.debug("waitpid():{}".format(e))
						sys.exit(1)
					if os.WIFEXITED(status):
						if self._debug or status != 0:
							self._log.debug("END")
							self._log.debug("child (PID={}) finished: ".format(pid))
							self._log.debug("exit, status={}".format(os.WEXITSTATUS(status)))
					elif os.WIFSIGNALED(status):
						self._log.debug("END")
						self._log.debug("child (PID={}) finished: ".format(pid))
						self._log.debug("signal, sig={}".format(os.WTERMSIG(status)))
					else:
						self._log.debug("END")
						self._log.debug("child (PID={}) finished: ".format(pid))
						self._log.debug("abnormal exit")

			except OSError as e:
				self._log.debug("fork():{}".format(e))
				pass

		elif use_multiprocessing:

			kwargs = {
				'size': size,
				'id_list': id_list,
				'id_property_dict': id_property_dict,
				'focusid_list': focusid_list,
				'expansion': expansion,
				'ids_dict': ids_dict,
				'objs_dict': objs_dict,
				'reduction': reduction,
				'start_time': start_time,
				'image_filepath': image_filepath,
				'azimuth': azimuth,
				'elevation': elevation,
				'zoom': zoom,
			}
			process = mp.Process(target=self._execMakeImage, kwargs=kwargs)
			process.start()
			process.join()

			if debug or process.exitcode != 0:
				self._log.debug("_makeAnimation():END")
				self._log.debug(f"child (PID={process.pid}) finished")

				if process.exitcode >= 0:
					self._log.debug(f"exit, status={process.exitcode}")
				else:
					self._log.debug(f"signal, sig={-process.exitcode}")

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
				zoom=zoom,
				payload=payload,
				methods=methods
			)

		self._log.debug("END")



	def _makeNoneImage(self, use_fork=True, use_multiprocessing=False, size = [512,512], image_filepath=None, payload:Payload=None, methods:str=None ):

		use_fork = hasattr(os, 'fork')
		debug    = self._debug
		self._log.debug("START")

		if use_fork:
			try:
				pid = os.fork()

				if not pid:
					try:
						self._execMakeNoneImage(
							size=size,
							image_filepath=image_filepath,
							payload=payload,
							methods=methods
						)

						os._exit(0)

					except OSError as e:
						self._log.debug("exec():{}".format(e))
						sys.exit(1)

				else:
					try:
						status = os.waitpid(pid, 0)[1]
					except OSError as e:
						self._log.debug("waitpid():{}".format(e))
						sys.exit(1)
					if os.WIFEXITED(status):
						if self._debug or status != 0:
							self._log.debug("END")
							self._log.debug("child (PID={}) finished: ".format(pid))
							self._log.debug("exit, status={}".format(os.WEXITSTATUS(status)))
					elif os.WIFSIGNALED(status):
						self._log.debug("END")
						self._log.debug("child (PID={}) finished: ".format(pid))
						self._log.debug("signal, sig={}".format(os.WTERMSIG(status)))
					else:
						self._log.debug("END")
						self._log.debug("child (PID={}) finished: ".format(pid))
						self._log.debug("abnormal exit")

			except OSError as e:
				self._log.debug("fork():{}".format(e))
				pass

		elif use_multiprocessing:

			kwargs = {
				'size': size,
				'image_filepath': image_filepath,
			}
			process = mp.Process(target=self._execMakeNoneImage, kwargs=kwargs)
			process.start()
			process.join()

			if debug or process.exitcode != 0:
				self._log.debug("END")
				self._log.debug(f"child (PID={process.pid}) finished: ")

				if process.exitcode >= 0:
					self._log.debug(f"exit, status={process.exitcode}")
				else:
					self._log.debug(f"signal, sig={-process.exitcode}")

		else:
			self._execMakeNoneImage(
				size=size,
				image_filepath=image_filepath,
				payload=payload,
				methods=methods
			)

		self._log.debug(use_fork)


	def _animation(self, size = [512,512], version=None, id_list=[], id_property_dict={}, focusid_list=None, expansion='art_ids', is_forced=False, script_path=None, range_step=12, reduction=None, zoom=None, payload:Payload=None, methods:str=None):

		debug        = self._debug
		start_time = time.perf_counter() if debug else None

		if reduction is None:
			reduction = self._reduction

		image_filepath = None

		ids_dict = {}
		objs_dict = {}

		version = self.check_version(version)

		self._log.debug("version=[{}]".format(version))
		self._log.debug("reduction=[{}]".format(reduction))

		if not self._renderer_info_dict or not isinstance(self._renderer_info_dict, dict) or version not in self._renderer_info_dict:
			file_path = os.path.join(self._json_path,'renderer_file',version+'.json')
			self._log.debug(file_path)
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

		self._log.debug("id_list=[{}]".format(id_list))

		if len(id_list)>0 and isinstance(ids_dict, dict):
			id_list = sorted([id for id in id_list if id in ids_dict])

		self._log.debug("id_list=[{}]".format(id_list))

		if len(id_list)>0:
			fd, image_filepath = tempfile.mkstemp(dir=self._images_path, suffix='.gif')
			os.close(fd)

			self._makeAnimation(
				#use_fork=True,
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
				zoom=zoom,
				payload=payload,
				methods=methods
			)

		else:
			if image_filepath and os.path.isfile(image_filepath):
				os.remove(image_filepath)

		self._log.debug(image_filepath)

		if not image_filepath or not os.path.isfile(image_filepath) or os.path.getsize(image_filepath)==0:
			if image_filepath and os.path.isfile(image_filepath):
				os.remove(image_filepath)

			fd, image_filepath = tempfile.mkstemp(dir=self._images_path, suffix='.png')
			os.close(fd)

			self._log.debug(image_filepath)
			self._makeNoneImage(
				#use_fork=True,
				size=size,
				image_filepath=image_filepath,
				payload=payload,
				methods=methods
			)

		self._log.debug(image_filepath)
		self._log.debug("elapsed: %f", time.perf_counter() - start_time if debug else None)

		return image_filepath


	def _image(self, size = [512,512], version=None, id_list=[], id_property_dict={}, focusid_list=None, expansion='art_ids', is_forced=False, script_path=None, reduction=None, azimuth=0, elevation=0, zoom=None, payload:Payload=None, methods:str=None):

		debug        = self._debug
		start_time = time.perf_counter() if debug else None
		self._log.debug("START")

		if reduction is None:
			reduction = self._reduction

		image_filepath = None

		ids_dict = {}
		objs_dict = {}

		version = self.check_version(version)

		self._log.debug("version=[{}]".format(version))
		self._log.debug("reduction=[{}]".format(reduction))
		self._log.debug("expansion=[{}]".format(expansion))

		if not self._renderer_info_dict or not isinstance(self._renderer_info_dict, dict) or version not in self._renderer_info_dict:
			file_path = os.path.join(self._json_path,'renderer_file',version+'.json')
			self._log.debug(file_path)
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

		self._log.debug("id_list=[{}]".format(id_list))

		if len(id_list)>0 and isinstance(ids_dict, dict):
			id_list = sorted([id for id in id_list if id in ids_dict])

		self._log.debug("id_list=[{}]".format(id_list))

		if isinstance(focusid_list, list) and len(focusid_list)>0 and isinstance(ids_dict, dict):
			self._log.debug(focusid_list)
			focusid_list = sorted([id for id in focusid_list if id in ids_dict])
			if len(focusid_list) == 0:
				focusid_list = None
			self._log.debug(focusid_list)

		if len(id_list)>0:
			self._log.debug(payload)
			suffix='.png'
			if isinstance(methods, str):
				if methods == 'focus' or methods == 'pick' or methods == 'map':
					suffix='.json'
			fd, image_filepath = tempfile.mkstemp(dir=self._images_path, suffix=suffix)
			os.close(fd)

			self._makeImage(
				#use_fork=True,
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
				zoom=zoom,
				payload=payload,
				methods=methods
			)

		self._log.debug(image_filepath)

		if not image_filepath or not os.path.isfile(image_filepath) or os.path.getsize(image_filepath)==0:
			if image_filepath and os.path.isfile(image_filepath):
				os.remove(image_filepath)

			suffix='.png'
			if isinstance(methods, str):
				if methods == 'focus' or methods == 'pick' or methods == 'map':
					suffix='.json'

			fd, image_filepath = tempfile.mkstemp(dir=self._images_path, suffix=suffix)
			os.close(fd)

			self._log.debug(image_filepath)
			self._makeNoneImage(
				#use_fork=True,
				size=size,
				image_filepath=image_filepath,
				payload=payload,
				methods=methods
			)

		self._log.debug(image_filepath)
		self._log.debug("elapsed: %f", time.perf_counter() - start_time if debug else None)

		return image_filepath
