#!/usr/bin/env python3
# coding: utf-8

import os
import sys
import time
import json
import platform
import inspect
import traceback
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

import daemon
from bottledaemon import daemon_run
from bottle import route, run, template, abort, error, request, default_app, HTTPResponse
from bottle import TEMPLATE_PATH
from bottle import static_file

from renderer import Renderer
#import renderer

DEBUG = True

renderer = None
script_path = os.path.abspath(os.path.dirname(__file__));
base_path = os.path.abspath(os.path.join(script_path,'..'));
htdocs_path = os.path.join(base_path,'htdocs')
#images_path = os.path.join(htdocs_path,'images')
images_path = os.path.join(script_path,'images')

@route('/<filename:path>')
def server_static(filename=None):
	#def server_static(filename='index.html'):
	if filename:
		paths = filename.split('/')
		if DEBUG:
			print(paths, file=sys.stderr)

		file_path = os.path.join(*paths)
		exists_path = os.path.join(htdocs_path,file_path)
		if DEBUG:
			print(exists_path, file=sys.stderr)
			print("server_static():EXEC:",inspect.currentframe().f_lineno, exists_path, file=sys.stderr)
			print("server_static():EXEC:",inspect.currentframe().f_lineno, request.query.keys(), file=sys.stderr)
		if os.path.exists(exists_path):
			return static_file(file_path, root=htdocs_path)

	param_list = list(request.query.keys());
	if DEBUG:
		print("server_static():EXEC:",inspect.currentframe().f_lineno, filename, param_list, file=sys.stderr)

	#return static_file(renderer.animation(request.query, script_path=os.path.abspath(os.path.join(script_path,'makeimage'))), root='/')

	#return static_file(renderer.animation(request.query), root='/')

	r = None
	if 'RotatingModelURL' in request.url:
		base_url = os.getenv('AG_FMA_RENDERER_ROTATINGMODELURL','https://bp3d.dbcls.jp/FMARenderer')
		if 'v1' in request.urlparts.path:
			base_url = base_url + '/v1'
		body = {"image_location": base_url + '?' + request.query_string}

		r = HTTPResponse(status=200, body=body)
		r.set_header("Content-Type", "application/json")

	elif 'FrontModelURL' in request.url:
		base_url = os.getenv('AG_FMA_RENDERER_FRONTMODELURL','https://bp3d.dbcls.jp/FMARendererF')
		if 'v1' in request.urlparts.path:
			base_url = base_url + '/v1'
		body = {"image_location": base_url + '?' + request.query_string}

		r = HTTPResponse(status=200, body=body)
		r.set_header("Content-Type", "application/json")

	elif 'FMARendererF' in request.url:
		f = renderer.image(request.query)
		r = HTTPResponse(status=200)
		r.content_type = _get_file_content_type(f)
		r.body = _file_content_iterator(f)

	else:
		f = renderer.animation(request.query)
		r = HTTPResponse(status=200)
		r.content_type = _get_file_content_type(f)
		r.body = _file_content_iterator(f)

	if DEBUG:
		print("server_static():EXEC:",inspect.currentframe().f_lineno, r, file=sys.stderr)

	return r

@route('/')
def index():
	#return static_file('index.html', root=htdocs_path)
	#return server_static(filename=os.path.join('images','none.png'))
	return server_static(filename='none.png')

@error(404)
def error404(error):
	return "Not Found!"

def _get_file_content_type(f):
	root_ext_pair = os.path.splitext(f)
	if root_ext_pair[1] == '.png':
		return 'image/png'
	else:
		return 'image/gif'

def _file_content_iterator(f):
	if DEBUG:
		print("_file_content_iterator():START:",inspect.currentframe().f_lineno, f, file=sys.stderr)
	bufsize = 1024  # 1KB
	with open(f, 'rb') as fh:
		while True:
			buf = fh.read(bufsize)
			if len(buf) == 0:
				break  # EOF
			yield buf

	if f and os.path.isfile(f) and os.path.exists(f):
		os.remove(f)

	if DEBUG:
		print("_file_content_iterator():END:",inspect.currentframe().f_lineno, f, file=sys.stderr)

def start(version = None, load_mesh = True, reduction = .0, debug = False):
	global renderer
	global DEBUG
	DEBUG = debug
	#traceback.print_stack()
	if debug:
		print("start():START:",inspect.currentframe().f_lineno, file=sys.stderr)
	#base_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'));
	obj_path = None
	json_path = None
	if(platform.system()=="Windows"):
		obj_path = os.path.join(base_path,'my-vtkjs-app','dist')
		json_path = os.path.join(base_path,'my-vtkjs-app','dist')
	else:
		obj_path = base_path
		json_path = base_path

	obj_path = os.path.join(obj_path,'objs')
	json_path = os.path.join(json_path,'renderer_file')

	if debug:
		print("start():EXEC:",inspect.currentframe().f_lineno, obj_path, file=sys.stderr)
		print("start():EXEC:",inspect.currentframe().f_lineno, json_path, file=sys.stderr)
		print("start():EXEC:",inspect.currentframe().f_lineno, images_path, file=sys.stderr)
	renderer = Renderer(obj_path, json_path, images_path, version = version, load_mesh = load_mesh, reduction = reduction, debug = debug)
	if debug:
		print("start():END:",inspect.currentframe().f_lineno, file=sys.stderr)

#traceback.print_stack()
#start()
if __name__ == "__main__":

	script_basename = os.path.basename(__file__)
	if script_basename == 'makeimage':

		parser = argparse.ArgumentParser(description='FMAレンダラー')  # parserを定義
		parser.add_argument('--version', help='Version', default='latest')
		parser.add_argument('--id', help='FMA ID (--mode makeimage only)', action='append')
		args = parser.parse_args()  # 引数を解析

		#start()

		start(version = args.version, load_mesh = False, debug = True)

		ids_list = []
		if args.id and isinstance(args.id, list):
			ids_list = args.id

			version = None
			if args.version:
				version = args.version

				version_list = renderer.get_version_list()
				if version_list and isinstance(version_list, list) and version in version_list:
					None
				else:
					version = renderer.get_latest_version()

			else:
				version = renderer.get_latest_version()

			renderer._animation(version=version, id_list=ids_list, is_forced=True, script_path=os.path.abspath(os.path.join(script_path,'makeimage')))
		else:

			version_list = renderer.get_version_list()
			versions = None
			if args.version:
				if version_list and isinstance(version_list, list) and args.version in version_list:
					versions = [args.version]
				else:
					versions = [renderer.get_latest_version()]
			else:
				versions = version_list

			for v in versions:
				ids_list = renderer.get_ids_list(v)
				for id in ids_list:
					renderer._animation(version=v, id_list=[id], is_forced=True, script_path=os.path.abspath(os.path.join(script_path,'makeimage')))


	elif script_basename == 'development':
		parser = argparse.ArgumentParser(description='FMAレンダラー')  # parserを定義
		parser.add_argument('--host', default='0.0.0.0', help='host addr')
		parser.add_argument('--port', type=int, default=3000, help='port number')
		#parser.add_argument('--version', help='Version', default='latest')
		parser.add_argument('--version', help='Version')
		parser.add_argument('--reduction', help='reduction', type=float, default=0.0)
		args = parser.parse_args()  # 引数を解析

		start(version = args.version, load_mesh = True, reduction = args.reduction, debug = True)
		run(host=args.host, port=args.port, reloader=False, debug=DEBUG)

		#elif args.mode == 'production':
		#	start(version = args.version, load_mesh = False, debug = True)
		#	daemon_run(host=args.host, port=args.port)

	elif script_basename == 'production':

		version = os.getenv('AG_FMA_RENDERER_VERSION',None)
		reduction = float(os.getenv('AG_FMA_RENDERER_REDUCTION','0.8'))
		debug = int(os.getenv('AG_FMA_RENDERER_DEBUG','0'))
		port = os.getenv('AG_FMA_RENDERER_PORT','38341')

		if sys.argv and len(sys.argv) > 1 and sys.argv[1] and sys.argv[1]=='start':
			#start(version = 'latest', load_mesh = False)
			start(version = version, load_mesh = True, reduction = reduction, debug = debug)


		pidfile = os.path.abspath(os.path.join(script_path,'bottle_'+port+'.pid'))
		logfile = os.path.abspath(os.path.join(script_path,'bottle_'+port+'.log'))

		daemon_run(host='0.0.0.0', port=int(port), pidfile=pidfile, logfile=logfile)

	#run(host='10.0.2.15', port=8080, reloader=False, debug=True)
	#run(host='0.0.0.0', port=8080, reloader=True, debug=DEBUG)
	#daemon_run(host='0.0.0.0', port=8080, reloader=False, debug=DEBUG)
	#start()
else:
	version = os.getenv('AG_FMA_RENDERER_VERSION',None)
	reduction = float(os.getenv('AG_FMA_RENDERER_REDUCTION','0.8'))
	debug = int(os.getenv('AG_FMA_RENDERER_DEBUG','0'))
	start(load_mesh = True, version = version, reduction = reduction, debug = debug)
	application = default_app()
