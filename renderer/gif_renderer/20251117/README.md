# bp3d/renderer/gif_renderer
BodyParts3D development by BITS

## システムのアップデータ及び追加インストール
sudo apt install -y \
  python3-pip \
  python3-venv \
  libgl1-mesa-glx \
  libgl1-mesa-dev \
  libosmesa6-dev \
  cmake \
  ninja-build

## 仮想環境の作成
python3 -m venv python/venv
source python/venv/bin/activate
python3 -m pip install --upgrade pip

## VTKビルド及びインストール
git clone -b v9.1.0 --depth 1 https://github.com/Kitware/VTK
rm -fr build_osmesa && mkdir build_osmesa && cd build_osmesa
cmake ../VTK \
  -GNinja \
  -DCMAKE_BUILD_TYPE=Release \
  -DVTK_BUILD_TESTING=OFF \
  -DVTK_BUILD_DOCUMENTATION=OFF \
  -DVTK_BUILD_EXAMPLES=OFF \
  -DVTK_MODULE_ENABLE_VTK_PythonInterpreter:STRING=NO \
  -DVTK_MODULE_ENABLE_VTK_WebCore:STRING=YES \
  -DVTK_MODULE_ENABLE_VTK_WebGLExporter:STRING=YES \
  -DVTK_MODULE_ENABLE_VTK_WebPython:STRING=YES \
  -DVTK_WHEEL_BUILD=ON \
  -DVTK_PYTHON_VERSION=3 \
  -DVTK_WRAP_PYTHON=ON \
  -DVTK_OPENGL_HAS_EGL=OFF \
  -DVTK_OPENGL_HAS_OSMESA=ON \
  -DVTK_USE_COCOA=FALSE \
  -DVTK_USE_X=FALSE \
  -DVTK_DEFAULT_RENDER_WINDOW_HEADLESS=True
nice -n 19 ninja -j $(nproc)
python3 -m pip install wheel
python3 setup.py bdist_wheel
pip install dist/vtk-*.whl
rsync -av build/lib.linux-x86_64-3.10/vtkmodules/libvtk*.so ../python/venv/lib/python3.10/site-packages/vtkmodules/

## Pythonモジュールインストール
pip install pyvista[all] fastapi[all] uvicorn[standard] pillow wheel
