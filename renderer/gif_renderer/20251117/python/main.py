#!/usr/bin/env python3
# coding: utf-8

#import sys
import tempfile
import logging
import os
#import inspect
#import trace

os.environ["AG_FMA_RENDERER_VERSION"] = os.getenv('AG_FMA_RENDERER_VERSION', "20250216il500")
#os.environ["AG_FMA_RENDERER_VERSION"] = os.getenv('AG_FMA_RENDERER_VERSION', "2.0i")
#os.environ["AG_FMA_RENDERER_VERSION"] = "4.3i"
os.environ["AG_FMA_RENDERER_WORKER"] = os.getenv('AG_FMA_RENDERER_WORKER', "1")
#os.environ["AG_FMA_RENDERER_REDUCTION"] = os.getenv('AG_FMA_RENDERER_REDUCTION', "0.0")
#os.environ["AG_FMA_RENDERER_REDUCTION"] = os.getenv('AG_FMA_RENDERER_REDUCTION', "0.8")
#os.environ["AG_FMA_RENDERER_REDUCTION"] = os.getenv('AG_FMA_RENDERER_REDUCTION', "0.5")
#os.environ["AG_FMA_RENDERER_REDUCTION"] = os.getenv('AG_FMA_RENDERER_REDUCTION', "0.1")
os.environ["AG_FMA_RENDERER_USE_GPU"] = os.getenv('AG_FMA_RENDERER_USE_GPU', "1")
os.environ["AG_FMA_RENDERER_DEBUG"] = os.getenv('AG_FMA_RENDERER_DEBUG', "1")

# --- ログ設定 ------------------------------------------------------------
if bool(int(os.getenv('AG_FMA_RENDERER_DEBUG', '0'))):
	logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(name)s: %(funcName)s: %(lineno)d: %(message)s')
else:
	logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


'''
def trace_func(frame, event, arg):
	code = frame.f_code
	func_name = code.co_name
	#filename = code.co_filename
	#lineno = frame.f_lineno
	if event == 'call' and func_name == 'mkdtemp':
		caller = frame.f_back
		if caller:
			print(f"CALL {frame.f_code.co_name} "
						f"from {caller.f_code.co_name} "
						f"in {caller.f_code.co_filename}:{caller.f_lineno}")
		else:
			print(f"CALL {frame.f_code.co_name} (top level)")

		#args, varargs, varkw, locals_ = inspect.getargvalues(frame)
		#logging.debug(f"{filename}:{lineno} CALL  {func_name} args={locals_}")
	#elif event == 'return' and func_name == 'mkdtemp':
	#	logging.debug(f"{filename}:{lineno} RETURN {func_name} -> {arg}")

	return trace_func

sys.settrace(trace_func)
'''


'''
# 既存の関数を保持
_orig_mkdtemp = tempfile.mkdtemp

def _mkdtemp_wrapper(*args, **kwargs):

	caller_frame = inspect.stack()[0]   # 0: wrapper, 1: caller
	caller_name   = caller_frame.function
	caller_file   = caller_frame.filename
	caller_lineno = caller_frame.lineno

	print(f"tempfile.mkdtemp was called from {caller_name} "
				f"in {caller_file}:{caller_lineno}")

	# ここで呼び出し前に何かしたいならその処理
	logging.debug(f"tempfile.mkdtemp called with args={args}, kwargs={kwargs}")

	# 実際にディレクトリを作る
	path = _orig_mkdtemp(*args, **kwargs)

	# 作成後にログ・トレース・データベースへ書き込む等
	logging.debug(f"created temp dir: {path}")

	return path

# 置き換え
tempfile.mkdtemp = _mkdtemp_wrapper
'''


# --- 旧JSON形式で受け取り用class定義 ---（ここから）
from paramclass import Payload, set_payload_default #, Common, Window, Camera
from fastapi import Request

def get_payload(request: Request) -> Payload:
	raw_query = unquote(request.url.query)
	if not raw_query:
		raise HTTPException(status_code=400, detail="クエリ文字列がありません")
	try:
		payload_json = json.loads(raw_query)
		logger.debug(payload_json)
		payload = Payload(**payload_json)
	except json.JSONDecodeError:
		raise HTTPException(status_code=400, detail="JSON 解析失敗")
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))
	return payload

def set_query_params_dict(payload: Payload, methods: str = None):
	set_payload_default(payload)

	id = []
	focusid = []
	rgb = []
	opacity = []
	if isinstance(payload.part, list):
		for part in payload.part:
			if part.part_id is None:
				continue
			id.append(part.part_id)
			rgb.append(part.part_color)
			opacity.append(part.part_opacity)

			if part.use_for_bounding_box_flag:
				focusid.append(part.part_id)

	#logger.debug(id)
	#logger.debug(focusid)
	#logger.debug(rgb)
	#logger.debug(opacity)
	logger.debug(methods)

	query_params_dict = {
		"methods":   methods,
		"version":   payload.common.version,
		"size":      "%dx%d" % (payload.window.image_width, payload.window.image_height),
		"reduction": None,
		"zoom":      round( payload.camera.zoom * 5 - 0.5 ) + 1 if isinstance(payload.camera.zoom, float) else None,
		"ha":        payload.camera.add_latitude_degree,
		"va":        payload.camera.add_longitude_degree,
		"expansion": payload.common.tree_name,
		"id":        id if len(id)>0 else None,
		"focusid":   focusid if len(focusid)>0 else None,
		"rgb":       rgb if len(rgb)>0 else None,
		"opacity":   map(str,opacity) if len(opacity)>0 else None,
		"payload":   payload
	}
	param_list = list(query_params_dict.keys());
	for key in param_list:
		if query_params_dict[key] is None:
			del query_params_dict[key]

	return query_params_dict
# --- 旧JSON形式で受け取り用class定義 ---（ここまで）



import argparse
import multiprocessing
#import platform
import shutil

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List, Optional
import uvicorn
#from typing import AsyncGenerator
import json
from urllib.parse import unquote
import base64

from renderer import Renderer

renderer = None
app_path = os.getenv('AG_FMA_RENDERER_APP_PATH', os.path.abspath(os.path.dirname(__file__)))
base_path = os.getenv('AG_FMA_RENDERER_BASE_PATH', os.path.abspath(os.path.join(app_path, '..')))
htdocs_path = os.getenv('AG_FMA_RENDERER_HTDOCS_PATH', os.path.join(base_path, 'htdocs'))


# --- ライフサイクルイベント --------------------------------------------
async def lifespan(app: FastAPI):
	"""起動時に実行される処理"""
	logger.info("Application startup")
	#logger.debug(app.state.version)
	#logger.debug(app.state.reduction)

	logger.debug(__name__)

	app.state.version = os.getenv('AG_FMA_RENDERER_VERSION', 'latest')
	app.state.reduction = float(os.getenv('AG_FMA_RENDERER_REDUCTION', '0.0'))
	app.state.debug = bool(int(os.getenv('AG_FMA_RENDERER_DEBUG', '0')))

	logger.debug(app.state.version)
	logger.debug(app.state.reduction)
	logger.debug(app.state.debug)

	#images_path = tempfile.mkdtemp()
	images_path = tempfile.gettempdir()
	logs_path = os.path.join(app_path, 'logs')
	os.makedirs(logs_path, exist_ok=True)
	'''
	'''
	obj_path = os.getenv('AG_FMA_RENDERER_OBJS_PATH', os.path.join(base_path, 'objs'))
	if not os.path.isdir(obj_path):
		raise ValueError("Directory for obj files does not exist! [%s]" % obj_path)
	json_path = os.getenv('AG_FMA_RENDERER_JSON_PATH', os.path.join(base_path, 'renderer_file'))
	if not os.path.isdir(json_path):
		raise ValueError("Directory for JSON files does not exist! [%s]" % json_path)

	renderer = Renderer(
		obj_path,
		json_path,
		images_path,
		version=app.state.version,
		load_mesh=True,
		reduction=app.state.reduction,
		debug=app.state.debug
	)
	app.state.renderer = renderer
	logger.debug(images_path)
	'''
	'''

	yield
	logger.debug(images_path)
	tempdir = tempfile.gettempdir()
	if os.path.isdir(images_path) and images_path != tempdir and images_path in tempdir:
		shutil.rmtree(images_path)
	logger.info("Application shutdown")

# --- アプリケーション -----------------------------------------------
app = FastAPI(lifespan=lifespan)

# CORS (必要に応じて調整)
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# ---- ユーティリティ関数 --------------------------------------------
def _generate_image_response(file_path: str) -> StreamingResponse:
	if not file_path or not os.path.exists(file_path):
		raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Image not found")
	media_type = _get_file_content_type(file_path)
	return StreamingResponse(
		_file_content_iterator(file_path),
		media_type=media_type,
		background=FileDeleteBackground(file_path)  # ファイル削除を遅延実行
	)

def _generate_url_json_response(
	request:  Request,
	base_url: str
) -> JSONResponse:
	path = request.url.path
	if 'dev' in path:
		base_url += '/dev'
	else:
		base_url += '/v1'
	return {"image_location": f"{base_url}?{request.query_params}"}

def _generate_base64_response(file_path: str) -> JSONResponse:
	with open(file_path, 'rb') as f:
		data = f.read()
	#logger.debug(os.path.getsize(file_path))
	#logger.debug(len(data))
	content_type = _get_file_content_type(file_path)
	os.remove(file_path)
	encoded_bytes = base64.b64encode(data)
	#logger.debug(len(encoded_bytes))
	#logger.debug(len(encoded_bytes.decode("utf-8")))
	#logger.debug(encoded_bytes.decode("utf-8"))
	return {"data":"data:"+content_type+";base64,"+encoded_bytes.decode("utf-8")}

def _get_file_content_type(f: str) -> str:
	ext = os.path.splitext(f)[1].lower()
	if ext == '.png':
		return 'image/png'
	elif ext == '.gif':
		return 'image/gif'
	elif ext == '.json':
		return 'application/json'
	else:
		return 'text/plain'

def _file_content_iterator(f: str):
	bufsize = 65536  # 64KB
	with open(f, 'rb') as fh:
		while True:
			buf = fh.read(bufsize)
			if not buf:
				break
			yield buf

# ファイル削除用の background task
class FileDeleteBackground:
	def __init__(self, path: str):
		self.path = path
	async def __call__(self):
		try:
			if os.path.isfile(self.path):
				os.remove(self.path)
		except Exception:
			pass

# ---- ルーティング ----------------------------------------------------
#@app.get("/message")
#async def message(tags: Optional[List[str]] = Query(None)):
#	print(tags)
#	return {"message": "Hello World"}

@app.middleware("http")
async def add_my_headers(request: Request, call_next):
	response = await call_next(request)
	response.headers["Cache-Control"] = "no-cache, no-store"
	return response

@app.get("/FMARenderer")
@app.get("/FMARenderer/")
@app.get("/FMARenderer/dev")
@app.get("/FMARenderer/v1")
async def fmarenderer(
	version:   str = None,
	size:      str = None,
	reduction: str = None,
	zoom:      str = None,
	ha:        str = None,
	va:        str = None,
	expansion: str = None,
	id:        Optional[List[str]] = Query(None),
	focusid:   Optional[List[str]] = Query(None),
	rgb:       Optional[List[str]] = Query(None),
	opacity:   Optional[List[str]] = Query(None),
):
	query_params_dict = {
		"version":   version,
		"size":      size,
		"reduction": reduction,
		"zoom":      zoom,
		"ha":        ha,
		"va":        va,
		"expansion": expansion,
		"id":        id,
		"focusid":   focusid,
		"rgb":       rgb,
		"opacity":   opacity,
	}
	param_list = list(query_params_dict.keys());
	for key in param_list:
		if query_params_dict[key] is None:
			del query_params_dict[key]

	f = app.state.renderer.animation(query_params_dict)
	return _generate_image_response(f)

@app.get("/FMARendererF")
@app.get("/FMARendererF/")
@app.get("/FMARendererF/dev")
@app.get("/FMARendererF/v1")
async def fmarendererf(
	version:   str = None,
	size:      str = None,
	reduction: str = None,
	zoom:      str = None,
	ha:        str = None,
	va:        str = None,
	expansion: str = None,
	id:        Optional[List[str]] = Query(None),
	focusid:   Optional[List[str]] = Query(None),
	rgb:       Optional[List[str]] = Query(None),
	opacity:   Optional[List[str]] = Query(None),
):
	query_params_dict = {
		"version":   version,
		"size":      size,
		"reduction": reduction,
		"zoom":      zoom,
		"ha":        ha,
		"va":        va,
		"expansion": expansion,
		"id":        id,
		"focusid":   focusid,
		"rgb":       rgb,
		"opacity":   opacity,
	}
	param_list = list(query_params_dict.keys());
	for key in param_list:
		if query_params_dict[key] is None:
			del query_params_dict[key]

	f = app.state.renderer.image(query_params_dict)
	return _generate_image_response(f)

@app.get("/RotatingModelURL")
@app.get("/RotatingModelURL/")
@app.get("/RotatingModelURL/dev")
@app.get("/RotatingModelURL/v1")
async def rotating_model_url(request: Request):
	base_url = os.getenv('AG_FMA_RENDERER_ROTATINGMODEL_URL', 'https://bp3d.dbcls.jp/FMARenderer')
	return _generate_url_json_response(request,base_url)

@app.get("/FrontModelURL")
@app.get("/FrontModelURL/")
@app.get("/FrontModelURL/dev")
@app.get("/FrontModelURL/v1")
async def front_model_url(request: Request):
	#print(request.url)
	#print(type(request.url))
	#print(request.url.path)
	#print(type(request.url.path))
	#print(request.query_params)
	#print(type(request.query_params))
	#print(request.query_params['id'])
	#print(type(request.query_params['id']))
	#return {"message": "Hello World"}
	base_url = os.getenv('AG_FMA_RENDERER_FRONTMODEL_URL', 'https://bp3d.dbcls.jp/FMARendererF')
	return _generate_url_json_response(request,base_url)

@app.get("/API/image")
async def image_get(request: Request):
	payload = get_payload(request)
	query_params_dict = set_query_params_dict(payload, 'image')
	f = app.state.renderer.image(query_params_dict)
	#return _generate_base64_response(f)
	return _generate_image_response(f)

@app.post("/API/image")
async def image_post(payload: Payload):
	query_params_dict = set_query_params_dict(payload, 'image')
	f = app.state.renderer.image(query_params_dict)
	return _generate_base64_response(f)

@app.get("/API/animation")
async def image_get(request: Request):
	payload = get_payload(request)
	query_params_dict = set_query_params_dict(payload, 'animation')
	f = app.state.renderer.animation(query_params_dict)
	return _generate_base64_response(f)

@app.post("/API/animation")
async def image_post(payload: Payload):
	query_params_dict = set_query_params_dict(payload, 'animation')
	f = app.state.renderer.animation(query_params_dict)
	return _generate_base64_response(f)

@app.get("/API/focus")
async def image_get(request: Request):
	payload = get_payload(request)
	query_params_dict = set_query_params_dict(payload, 'focus')
	f = app.state.renderer.image(query_params_dict)
	return _generate_image_response(f)

@app.post("/API/focus")
async def image_post(payload: Payload):
	query_params_dict = set_query_params_dict(payload, 'focus')
	f = app.state.renderer.image(query_params_dict)
	return _generate_image_response(f)

@app.get("/API/pick")
async def image_get(request: Request):
	payload = get_payload(request)
	query_params_dict = set_query_params_dict(payload, 'pick')
	f = app.state.renderer.image(query_params_dict)
	return _generate_image_response(f)

@app.post("/API/pick")
async def image_post(payload: Payload):
	query_params_dict = set_query_params_dict(payload, 'pick')
	f = app.state.renderer.image(query_params_dict)
	return _generate_image_response(f)

@app.get("/API/map")
async def image_get(request: Request):
	payload = get_payload(request)
	query_params_dict = set_query_params_dict(payload, 'map')
	f = app.state.renderer.image(query_params_dict)
	return _generate_image_response(f)

@app.post("/API/map")
async def image_post(payload: Payload):
	query_params_dict = set_query_params_dict(payload, 'map')
	f = app.state.renderer.image(query_params_dict)
	return _generate_image_response(f)

app.mount("/", StaticFiles(directory=htdocs_path, html=True), name="static")

# --- uvicorn 起動 ------------------------------------------------------
if __name__ == "__main__":
	logger.info("Application start")

	cpu_count = int(max(1, multiprocessing.cpu_count() // 3))
	#cpu_count = 1

	host = os.getenv('AG_FMA_RENDERER_HOST', '0.0.0.0')
	port = int(os.getenv('AG_FMA_RENDERER_PORT', '3000'))
	workers = int(os.getenv('AG_FMA_RENDERER_WORKER', cpu_count))
	debug = bool(int(os.getenv('AG_FMA_RENDERER_DEBUG', '0')))

	log_level = 'debug' if debug else 'warning'

	uvicorn.run(
		"main:app",
		host=host,
		port=port,
		reload=False,   # 開発時にコード変更を自動リロード
		workers=workers,	 # 本番環境では適宜増やす
		log_level=log_level,
	)
else:
	pass

## AG_FMA_RENDERER_VERSION=2.0i AG_FMA_RENDERER_DEBUG=1 gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:3000
# AG_FMA_RENDERER_VERSION=2.0i AG_FMA_RENDERER_DEBUG=1 uvicorn main:app --host=0.0.0.0 --port=3000 --workers 2 --log-level=debug
# AG_FMA_RENDERER_BASE_PATH=/home/tyamamot/ag/renderer/gif_renderer/python_egl_fastapi/datas/2.0i AG_FMA_RENDERER_VERSION=2.0i AG_FMA_RENDERER_DEBUG=1 uvicorn main:app --host=0.0.0.0 --port=3000 --workers 2 --log-level=debug

#AG_FMA_RENDERER_APP_PATH=/home/tyamamot/ag/renderer/gif_renderer/python_egl_fastapi AG_FMA_RENDERER_VERSION=2.0i AG_FMA_RENDERER_DEBUG=1 python main.py
#AG_FMA_RENDERER_APP_PATH=/home/tyamamot/ag/renderer/gif_renderer/python_egl_fastapi AG_FMA_RENDERER_VERSION=20251101il500 AG_FMA_RENDERER_DEBUG=1 python main.py
#AG_FMA_RENDERER_BASE_PATH=/home/tyamamot/ag/renderer/gif_renderer/python_egl_fastapi/datas/2.0i AG_FMA_RENDERER_VERSION=2.0i AG_FMA_RENDERER_DEBUG=1 python main.py
#AG_FMA_RENDERER_BASE_PATH=/home/tyamamot/ag/renderer/gif_renderer/python_egl_fastapi/datas/20251101il500 AG_FMA_RENDERER_VERSION=20251101il500 AG_FMA_RENDERER_DEBUG=1 python main.py
