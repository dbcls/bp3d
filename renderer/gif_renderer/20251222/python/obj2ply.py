#!/usr/bin/env python3
"""
Convert one or more OBJ files to binary VTP (XML PolyData) files
using multiprocessing.

Usage:
    python obj2vtp.py file1.obj file2.obj [..., fileN.obj]

Each OBJ is read, converted to a vtkPolyData, and written out as
`<original_name>.vtp`.  The output is binary XML for speed and size
reduction.

The script is safe to run on any VTK‑Python ≥ 8.x (the method names
below are available in those releases).  No VTK objects are shared
between processes – every worker creates its own reader/writer.
"""

import argparse
import os
import sys
import multiprocessing
from multiprocessing import Pool
from functools import partial

import vtk
import pyvista as pv

# ------------------------------------------------------------------ #
# Worker ------------------------------------------------------------- #
# ------------------------------------------------------------------ #
def convert_obj_to_ply(obj_path: str, reduction: float = .0, ascii: bool = False) -> None:
    """
    Read *obj_path*, write a binary VTP file `<obj_name>.vtp`.

    The function is intentionally *process‑local* – it never shares
    VTK objects with the parent process or other workers.
    """
    # ------------------------------------------------------------------
    # 1️⃣  Skip if the input file is missing or the output already exists
    # ------------------------------------------------------------------
    if not os.path.isfile(obj_path):
        # Parent already warned; return silently for this worker.
        return

    base_path = os.path.splitext(obj_path)[0]
    if reduction and reduction > .0:
        base_path += "_%03d" % (int(reduction * 100))

    ply_path = base_path + ".ply"

    if os.path.isfile(ply_path):          # output already exists → skip
        print(f"🗒  {obj_path} → {ply_path}  (既に存在しています)")
        return

    # ------------------------------------------------------------------
    # 2️⃣  OBJ を読み込む
    # ------------------------------------------------------------------
    #obj_reader = vtk.vtkOBJReader()
    #obj_reader.SetFileName(obj_path)
    #obj_reader.Update()
    #polydata = obj_reader.GetOutput()
    polydata = pv.read(obj_path)
    if polydata is None or polydata.GetNumberOfPoints() == 0:
        raise RuntimeError(f"OBJ ファイル '{obj_path}' の読み込みに失敗しました。")

    '''
    # ---------- 2. 必要なら法線を計算 ----------
    # OBJ には法線が無いことがあるので、ここで補完しておく
    normals_filter = vtk.vtkPolyDataNormals()
    normals_filter.SetInputData(polydata)
    normals_filter.ConsistencyOn()
    normals_filter.SplittingOff()
    normals_filter.Update()

    polydata = normals_filter.GetOutput()

    if reduction and reduction > .0:
        decimate = vtk.vtkQuadricDecimation()
        decimate.SetInputData(polydata)
        decimate.SetTargetReduction(reduction)
        decimate.Update()
        polydata = decimate.GetOutput()

    for data in (polydata.GetCellData(), polydata.GetPointData()):
        if data.HasArray("MaterialIds"):
            data.RemoveArray("MaterialIds")
        if data.HasArray("GroupIds"):
            data.RemoveArray("GroupIds")
    '''

    # ------------------------------------------------------------------
    # 3️⃣  PLY へ書き出す
    # ------------------------------------------------------------------
    #ply_writer = vtk.vtkPLYWriter()
    #ply_writer.SetFileName(ply_path)
    #ply_writer.SetInputData(polydata)

    #if ascii:
    #    ply_writer.SetFileTypeToASCII()
    #    print("SetFileTypeToASCII")
    #else:
    #    ply_writer.SetFileTypeToBinary()
    #    print("SetFileTypeToBinary")

    # ここで実際にファイルを書き出す
    #ply_writer.Write()
    polydata.save(ply_path)
    print(f"✓ {obj_path} → {ply_path}")


# ------------------------------------------------------------------ #
# Main --------------------------------------------------------------- #
# ------------------------------------------------------------------ #
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert OBJ files to binary VTP (XML PolyData)."
    )
    parser.add_argument(
        "obj_files",
	        nargs="+",
        help="Path(s) to one or more OBJ files to convert.",
    )
    parser.add_argument("--reduction", type=float, default=0.0,
                        help="削減率")
    #parser.add_argument('--ascii', action='store_true', help="PLYファイル形式（テキスト）")
    args = parser.parse_args()

    # ------------------------------------------------------------------
    # 1️⃣  Filter the input list – keep only existing files
    # ------------------------------------------------------------------
    existing_files = [
        f for f in args.obj_files if os.path.isfile(f)
    ]

    if not existing_files:
        print("⚠️  変換対象のOBJファイルがありません。", file=sys.stderr)
        sys.exit(1)

    # ------------------------------------------------------------------
    # 2️⃣  変換を並列化（CPUコア数分のプロセスを生成）
    # ------------------------------------------------------------------
    cpu_cnt = os.cpu_count() or 1
    with Pool(processes=cpu_cnt) as pool:
        #convert_func = partial(convert_obj_to_ply, reduction=args.reduction, ascii=args.ascii)
        convert_func = partial(convert_obj_to_ply, reduction=args.reduction)
        # `pool.map` では例外がそのまま投げられますので、
        # 失敗時に詳細を表示するために `pool.imap_unordered` を使う
        for _ in pool.imap_unordered(convert_func, existing_files):
            # ここでは何もしません – すべての出力は
            # convert_obj_to_ply の内部でプリントされます
            pass


if __name__ == "__main__":
    main()
