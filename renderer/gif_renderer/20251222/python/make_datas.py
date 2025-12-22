#!/usr/bin/env python3
# coding: utf-8

import os
import json
import shutil
import logging
import pyvista as pv
import numpy as np
import gc
import vtk

def vtk2gltf(file,gltf_file):

	renderWindow = vtk.vtkRenderWindow()
	renderWindow.SetSize(500,500)

	renderer = vtk.vtkRenderer()
	renderWindow.AddRenderer(renderer)

	reader = vtk.vtkPolyDataReader()   # 例：Legacy PolyData
	# structured grid なら vtkStructuredGridReader() を使う
	reader.SetFileName(file)
	reader.Update()
	polydata = reader.GetOutput()

	mapper = vtk.vtkPolyDataMapper()
	mapper.SetInputData(polydata)

	actor = vtk.vtkActor()
	actor.SetMapper(mapper)

	renderer.AddActor(actor)

	exporter = vtk.vtkGLTFExporter()
	exporter.SetRenderWindow(renderWindow)
	exporter.SetFileName(gltf_file)
	exporter.SetInlineData(True)
	exporter.SetSaveNormal(True)
	exporter.Update()

	renderer.RemoveActor(actor)
	renderWindow.RemoveRenderer(renderer)

	exporter = None
	actor = None
	mapper = None
	object = None
	renderer = None
	renderWindow = None

	return

# 1. PolyData を npz に保存
def save_polydata_to_npz(polydata: pv.PolyData, fname: str):
	# --- 主要データ ---------------------------------------------
	points = polydata.points            # (N, 3)
	faces  = polydata.faces             # (M, ...) 1‑D array

	# --- 属性データ ---------------------------------------------
	# point_data, cell_data, field_data は dict 形
	point_data = {k: v.copy() for k, v in polydata.point_data.items()}
	cell_data  = {k: v.copy() for k, v in polydata.cell_data.items()}
	field_data = {k: v.copy() for k, v in polydata.field_data.items()}

	# --- npz で保存 --------------------------------------------
	np.savez_compressed(
		fname,
		points=points,
		faces=faces,
		point_data=point_data,
		cell_data=cell_data,
		field_data=field_data
	)

# 2. npz から PolyData を復元
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

def main():
	logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(name)s: %(funcName)s: %(lineno)d: %(message)s')
	logger = logging.getLogger(__name__)

	app_path = os.getenv('AG_FMA_RENDERER_APP_PATH', os.path.abspath(os.path.dirname(__file__)))
	base_path = os.getenv('AG_FMA_RENDERER_BASE_PATH', os.path.abspath(os.path.join(app_path, '..')))

	htdocs_path = os.getenv('AG_FMA_RENDERER_HTDOCS_PATH', os.path.join(base_path, 'htdocs'))
	if not os.path.isdir(htdocs_path):
		raise ValueError("Directory for obj files does not exist! [%s]" % htdocs_path)

	obj_path = os.getenv('AG_FMA_RENDERER_OBJS_PATH', os.path.join(base_path, 'objs'))
	if not os.path.isdir(obj_path):
		raise ValueError("Directory for obj files does not exist! [%s]" % obj_path)

	json_path = os.getenv('AG_FMA_RENDERER_JSON_PATH', os.path.join(base_path, 'renderer_file'))
	if not os.path.isdir(json_path):
		raise ValueError("Directory for JSON files does not exist! [%s]" % json_path)

	versions_file_path = os.path.join(json_path,'versions_file.json')
	if not os.path.isfile(versions_file_path):
		raise ValueError("JSON files does not exist! [%s]" % versions_file_path)

	#file_extension = '.vtk'
	file_extension = '.obj'

	logger.debug(versions_file_path)

	json_open = open(versions_file_path, encoding='utf-8')
	versions_json = json.load(json_open)
	json_load_keys = list(versions_json.keys())
	versions = sorted(filter(lambda x: isinstance(versions_json[x], dict),json_load_keys), key=lambda x:versions_json[x]['order'], reverse=True)
	#versions = ['2.0i','4.3i']
	versions = ['20250216il500']
	#versions = ['20251101il500']
	for v in versions:
		file_path = os.path.join(json_path,'renderer_file',v+'.json')
		if not os.path.isfile(file_path):
			logger.debug("JSON files does not exist! [%s]" % file_path)
			continue
		logger.debug(file_path)

		json_open = open(file_path, encoding='utf-8')
		json_load = json.load(json_open)

		ids_dict = json_load[v]['ids']
		objs_dict = json_load[v]['art_ids']

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
			file_path = os.path.join(obj_path,art_id+file_extension)
			if not os.path.isfile(file_path):
				continue

			file_copy_base_path = os.path.join(datas_copy_obj_path,art_id)
			#logger.debug(file_copy_base_path)

			file_copy_path = file_copy_base_path+file_extension
			if os.path.isfile(file_copy_path):
				os.remove(file_copy_path)
			#if not os.path.isfile(file_copy_path):
			#	shutil.copy2(file_path, datas_copy_obj_path)

			#npz_file_path = file_copy_path+'.npz'
			#if not os.path.isfile(npz_file_path):
			#	save_polydata_to_npz(pv.read(file_path), npz_file_path)

			#poly = load_polydata_from_npz(npz_file_path)
			#poly.save(npz_file_path+'.vtk')

			gltf_file_path = file_copy_base_path+'.gltf'
			glb_file_path = file_copy_base_path+'.glb'
			#poly = load_polydata_from_npz(npz_file_path)
			#poly.save(glb_file_path)

			#vtk2gltf(file_path, gltf_file_path)
			#vtk2gltf(file_path, glb_file_path)

			if os.path.isfile(gltf_file_path):
				os.remove(gltf_file_path)

			if os.path.isfile(glb_file_path):
				os.remove(glb_file_path)

			#vtk2gltf(file_path, gltf_file_path)

			polydata = pv.read(file_path)
			for ext in ['.ply', '.vtp', '.stl','.geo', '.obj', '.iv', '.pkl', '.pickle']:
				file_path = file_copy_base_path+ext
				if os.path.isfile(file_path):
					os.remove(file_path)
				#polydata.save(file_path)

			ply_file_path = file_copy_base_path+'.ply'
			polydata.save(ply_file_path)




if __name__ == "__main__":
	main()
