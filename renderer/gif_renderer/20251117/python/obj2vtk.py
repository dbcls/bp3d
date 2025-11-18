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


# ------------------------------------------------------------------ #
# Worker ------------------------------------------------------------- #
# ------------------------------------------------------------------ #
def convert_obj_to_vtp(obj_path: str, reduction: float = .0) -> None:
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

    vtp_path = base_path + ".vtp"
    vtk_path = base_path + ".vtk"

    if os.path.isfile(vtp_path) and os.path.isfile(vtk_path):          # output already exists → skip
        print(f"🗒  {obj_path} → {vtp_path}  (既に存在しています)")
        print(f"🗒  {obj_path} → {vtk_path}  (既に存在しています)")
        return

    # ------------------------------------------------------------------
    # 2️⃣  OBJ を読み込む
    # ------------------------------------------------------------------
    reader = vtk.vtkOBJReader()
    reader.SetFileName(obj_path)
    reader.Update()

    polydata = reader.GetOutput()

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

    # ------------------------------------------------------------------
    # 3️⃣  VTP へ書き出す（バイナリ XML）
    # ------------------------------------------------------------------
    if not os.path.isfile(vtp_path):
        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetFileName(vtp_path)
        writer.SetInputData(polydata)
        writer.SetDataModeToBinary()      # バイナリ XML
        writer.Write()
        print(f"✓ {obj_path} → {vtp_path}")

    if not os.path.isfile(vtk_path):
        writer = vtk.vtkPolyDataWriter()
        writer.SetFileName(vtk_path)
        writer.SetInputData(polydata)
        writer.SetFileTypeToBinary()      # バイナリ XML
        writer.Write()
        print(f"✓ {obj_path} → {vtk_path}")


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
        convert_func = partial(convert_obj_to_vtp, reduction=args.reduction)
        # `pool.map` では例外がそのまま投げられますので、
        # 失敗時に詳細を表示するために `pool.imap_unordered` を使う
        for _ in pool.imap_unordered(convert_func, existing_files):
            # ここでは何もしません – すべての出力は
            # convert_obj_to_vtp の内部でプリントされます
            pass


if __name__ == "__main__":
    main()
