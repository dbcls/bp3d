#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
VTK だけで書く実装
OBJ を multiprocessing で並列読み込みし、MultiBlock (.vtm) に書き出す

使い方:
    python obj_to_vtm_multiproc_vtk.py /path/to/obj_dir output.vtm
"""

import os
import json
import pathlib
import argparse
import multiprocessing
from multiprocessing import Pool, cpu_count, set_start_method, Process
from functools import partial
import vtk
import pyvista as pv

# ----------------------------------------------------------------------
# 1. 1 つのプロセスで OBJ → XML PolyData (バイナリ文字列) へ変換
# ----------------------------------------------------------------------
def _obj_to_xml_str(path: pathlib.Path, reduction: float | None = None):

    if not os.path.isfile(str(path)):
        raise FileNotFoundError(f"%s に OBJ ファイルが見つかりませんでした。" % str(path))

    reader = vtk.vtkOBJReader()
    reader.SetFileName(str(path))
    reader.Update()

    polydata = reader.GetOutput()

    if reduction and reduction > .0:
        decimate = vtk.vtkQuadricDecimation()
        decimate.SetInputData(polydata)
        decimate.SetTargetReduction(reduction)
        decimate.Update()
        polydata = decimate.GetOutput()

    # ---------- ここから ----------
    # 1. 「MaterialIds」を CellData としても PointData としても除去
    for data in (polydata.GetCellData(), polydata.GetPointData()):
        if data.HasArray("MaterialIds"):
            data.RemoveArray("MaterialIds")
        if data.HasArray("GroupIds"):
            data.RemoveArray("GroupIds")
    # ---------- ここまで ----------

    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetInputData(polydata)
    writer.SetDataModeToBinary()
    writer.WriteToOutputStringOn()
    writer.Write()

    xml_str = writer.GetOutputString()
    return path.stem, xml_str

# ----------------------------------------------------------------------
# 2. メインプロセス: 文字列を PolyData として読み込み、MultiBlock を作成
# ----------------------------------------------------------------------
#def obj_files_to_vtm_multiproc_vtk(obj_dir: str | pathlib.Path,
#                                   output_vtm: str | pathlib.Path,
#                                   workers: int | None = None):
def obj_files_to_vtm_multiproc_vtk(
    objs_list: list[str] | list[pathlib.Path],
    obj_dir: str | pathlib.Path,
    output_vtm: str | pathlib.Path,
    reduction: float | None = None,
    workers: int | None = None,
):
    """
    複数 OBJ を並列に読み込み、MultiBlock (.vtm) へ保存

    Parameters
    ----------
    obj_dir : str or Path
        OBJ ファイルが置かれたディレクトリ
    output_vtm : str or Path
        出力する .vtm ファイル名
    workers : int or None
        並列プロセス数。None なら CPU コア数を自動判定
    """
    obj_dir = pathlib.Path(obj_dir)
    output_vtm = pathlib.Path(output_vtm)

    # 1. 対象ファイルを取得
    #obj_paths = sorted(obj_dir.glob("*.obj"))
    obj_paths = [pathlib.Path(os.path.join(obj_dir, f + '.obj')) for f in objs_list if os.path.isfile(os.path.join(obj_dir, f + '.obj'))]
    if not obj_paths:
        raise FileNotFoundError(f"{obj_dir} に OBJ ファイルが見つかりませんでした。")
    #print(obj_paths)
    if workers is None:
        workers = cpu_count()

    # 2. multiprocessing で読み込み (OBJ → XML PolyData 文字列)
    partial_func = partial(_obj_to_xml_str, reduction=reduction)
    with Pool(processes=workers) as pool:
        results = pool.map(partial_func, obj_paths)

    # 3. MultiBlock を作成
    mb = vtk.vtkMultiBlockDataSet()

    for idx, (name, xml_str) in enumerate(results):
        # 文字列 → PolyData
        xml_reader = vtk.vtkXMLPolyDataReader()
        xml_reader.ReadFromInputStringOn()
        xml_reader.SetInputString(xml_str)
        xml_reader.Update()
        polydata = xml_reader.GetOutput()

        mb.SetBlock(idx, polydata)
        mb.GetMetaData(idx).Set(vtk.vtkCompositeDataSet.NAME(), name)

    # 4. VTM へ書き込み
    writer = vtk.vtkXMLMultiBlockDataWriter()
    writer.SetFileName(str(output_vtm))
    writer.SetInputData(mb)
    writer.SetDataModeToBinary()
    writer.Write()

    print(f"MultiBlock written to: {output_vtm}")

def chunk_to_list(lst, size:int=100):
    return [lst[i:i + size] for i in range(0, len(lst), size)]

# ----------------------------------------------------------------------
# 5. 実行例
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Windows では spawn を強制
    try:
        set_start_method("spawn", force=True)
    except RuntimeError:
        # すでに開始済みの場合は無視
        pass

    parser = argparse.ArgumentParser(description="VTK + multiprocessing で OBJ → VTM")
    parser.add_argument("json_dir", help="JSON ファイルが入っているディレクトリ")
    parser.add_argument("obj_dir", help="OBJ ファイルが入っているディレクトリ")
    #parser.add_argument("output_vtm", help="出力する .vtm ファイル名")
    parser.add_argument("--version", type=str, default=None,
                        help="バージョン指定")
    parser.add_argument("--workers", type=int, default=None,
                        help="並列プロセス数 (省略で CPU コア数を自動選択)")
    parser.add_argument("--reduction", type=float, default=None,
                        help="削減割合")
    parser.add_argument("--size", type=int, default=100,
                        help="配列サイズ")
    args = parser.parse_args()

    versions = []
    renderer_info_dict = {}
    versions_file_path = os.path.join(args.json_dir,'versions_file.json')
    if os.path.isfile(versions_file_path):
      json_open = open(versions_file_path, encoding='utf-8')
      json_load = json.load(json_open)
      json_load_keys = list(json_load.keys())

      if args.version:
          versions = sorted(filter(lambda x: isinstance(json_load[x], dict),json_load_keys), key=lambda x:json_load[x]['order'], reverse=True)
      else:
          versions = sorted(filter(lambda x: isinstance(json_load[x], dict) and json_load[x]['mv_publish'],json_load_keys), key=lambda x:json_load[x]['order'], reverse=True)

      for v in versions:
        if args.version and args.version != v:
          continue

        print(v)

        #output_vtm = os.path.join(args.obj_dir,v+'.vtm')
        ##output_vtm = os.path.join('.',v+'.vtm')
        #if os.path.isfile(output_vtm):
        #  continue

        file_path = os.path.join(args.json_dir,'renderer_file',v+'.json')
        if not os.path.isfile(file_path):
          continue

        json_open = open(file_path, encoding='utf-8')
        json_load = json.load(json_open)
        renderer_info_dict[v] = json_load[v]

        if isinstance(json_load[v], dict) and 'ids' in json_load[v] and isinstance(json_load[v]['ids'], dict) and 'art_ids' in json_load[v] and isinstance(json_load[v]['art_ids'], dict):

          ids_dict = json_load[v]['ids']
          art_ids_dict = json_load[v]['art_ids']
          art_ids_list = sorted(set(art_ids_dict.keys()))

          #obj_files_to_vtm_multiproc_vtk(art_ids_list, args.obj_dir, output_vtm, workers=args.workers)

          art_ids_lists = chunk_to_list(art_ids_list,args.size)
          art_ids_lists_len = len(art_ids_lists)
          for i in range(art_ids_lists_len):

              output_vtm = os.path.join(args.obj_dir,v+"_%03d.vtm" % i)
              print("\t",output_vtm)

              process = Process(target=obj_files_to_vtm_multiproc_vtk, args=(art_ids_lists[i], args.obj_dir, output_vtm), kwargs={"workers": args.workers, 'reduction': args.reduction})
              process.start()
              process.join()

          #mb = pv.read(output_vtm)
          #print(mb)
          #print(mb[0])
          #print(mb['FJ108'])
          #print(mb.keys())

    #obj_files_to_vtm_multiproc_vtk(args.obj_dir, args.output_vtm, workers=args.workers)

