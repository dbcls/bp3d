# coding: utf-8
# --- 旧JSON形式で受け取り用class定義 ---（ここから）

from typing import Literal, List, Optional
from pydantic import BaseModel, Field

#バージョン、ツリーなどのリクエスト全体に共通のconfiguration parameter群を設定します。
class Common(BaseModel):
	model: Optional[str] = Field(default="bp3d", alias="Model", description="キット（3Dモデル）名")
	version: Optional[str] = Field(default="latest", alias="Version", description="3Dデータのバージョン。未指定の場合には最新版が自動選択されます。")
	anatomogram_version: Optional[str] = Field(default="20110318", alias="AnatomogramVersion", description="パラメータ記載文法のバージョン")
	scalar_maximum: Optional[int] = Field(default=65535, alias="ScalarMaximum", description="Choropleth Mapの最大値")
	scalar_minimum: Optional[int] = Field(default=-65535, alias="ScalarMinimum", description="Choropleth Mapの最小値")
	colorbar_flag: Optional[bool] = Field(default=False, alias="ColorbarFlag", description="Choropleth Mapのカラーチャートバーの表示有無")
	scalar_color_flag: Optional[bool] = Field(default=False, alias="ScalarColorFlag", description="フラグをtrueにしたパーツをChoropleth Map表示")
	tree_name: Optional[Literal["all", "isa", "partof"]] = Field(default="all", alias="TreeName", description="パーツデータ組合せに利用するFMAツリーを指定します")
	date_time: Optional[str] = Field(None, alias="DateTime", description="configuration作成時のタイムスタンプ(YYYYMMDDhhmmss)")
	coordinate_system_name: Optional[str] = Field(default="bp3d", alias="CoordinateSystemName", description="3Dモデル空間名")
	copyright_type: Optional[Literal["large", "medium", "small"]] = Field(None, alias="CopyrightType", description="DBCLSのコピーライトを画像中に描画するサイズ（未指定の場合には描画しません）")
	pin_description_draw_flag: Optional[bool] = Field(default=False, alias="PinDescriptionDrawFlag", description="画像へのピン説明の描画有無")
	pin_indication_line_draw_flag: Optional[Literal[0, 1, 2]] = Field(default=0, alias="PinIndicationLineDrawFlag", description="ピンとピン説明の間に描画する線の設定（1:ピン先端、2：ピン終端、0：線無し）")

#画像サイズ、背景色など、描画画像に関するconfiguration parameter群を設定します。
class Window(BaseModel):
	image_width: Optional[int] = Field(default=512, ge=16, le=1024, alias="ImageWidth", description="生成画像の横幅ピクセル数")
	image_height: Optional[int] = Field(default=512, ge=16, le=1024, alias="ImageHeight", description="生成画像の高さピクセル数")
	background_color: Optional[str] = Field(default="FFFFFF", pattern=r"^[0-9a-fA-F]{6}$", alias="BackgroundColor", description="16進数表記の背景色")
	background_opacity: Optional[int] = Field(default=100, ge=0, le=100, alias="BackgroundOpacity", description="背景の不透明度")
	grid_flag: Optional[bool] = Field(default=False, alias="GridFlag", description="画像上に一定間隔の格子を描画するかどうかを指定")
	grid_tick_interval: Optional[int] = Field(default=100, alias="GridTickInterval", description="格子の描画単位（mm）")
	grid_color: Optional[str] = Field(default="FFFFFF", pattern=r"^[0-9a-fA-F]{6}$", alias="GridColor", description="16進数表記の格子の色")

#カメラ位置、ズーム、カメラの回転角度など、描画時のカメラ（視点）に関するconfiguration parameter群を設定します。
class Camera(BaseModel):
	camera_mode: Optional[Literal["camera", "front", "back", "left", "right", "top", "bottom"]] = Field(default="front", alias="CameraMode", description="カメラ位置を指定", exclude=True)
	camera_x: Optional[float] = Field(default=0, alias="CameraX", description="カメラのX座標（Modeがcameraの時）")
	camera_y: Optional[float] = Field(default=0, alias="CameraY", description="カメラのY座標（Modeがcameraの時）")
	camera_z: Optional[float] = Field(default=0, alias="CameraZ", description="カメラのZ座標（Modeがcameraの時）")
	target_x: Optional[float] = Field(default=0, alias="TargetX", description="カメラの視線が向かう点（Target）のX座標")
	target_y: Optional[float] = Field(default=0, alias="TargetY", description="カメラの視線が向かう点（Target）のY座標")
	target_z: Optional[float] = Field(default=0, alias="TargetZ", description="カメラの視線が向かう点（Target）のZ座標")
	camera_up_vector_x: Optional[float] = Field(default=0, alias="CameraUpVectorX", description="カメラの上方ベクトル（上方向を定義）のX要素")
	camera_up_vector_y: Optional[float] = Field(default=0, alias="CameraUpVectorY", description="カメラの上方ベクトル（上方向を定義）のY要素")
	camera_up_vector_z: Optional[float] = Field(default=0, alias="CameraUpVectorZ", description="カメラの上方ベクトル（上方向を定義）のZ要素")
	zoom: Optional[float] = Field(None, ge=0, le=19.8, alias="Zoom", description="ズーム値")
	add_latitude_degree: Optional[int] = Field(default=0, ge=0, le=360, alias="AddLatitudeDegree", description="緯度方向への追加回転角度", exclude=True)
	add_longitude_degree: Optional[int] = Field(default=0, ge=0, le=360, alias="AddLongitudeDegree", description="経度方向への追加回転角度", exclude=True)

#パーツの回転角度、回転中心、回転軸など、パーツ群の回転に関するconfiguration parameter群を設定します。
class ObjectRotate(BaseModel):
	rotate_degree: Optional[float] = Field(default=0, alias="RotateDegree", description="回転角度")
	rotate_center_x: Optional[float] = Field(default=0, alias="RotateCenterX", description="回転中心のX座標")
	rotate_center_y: Optional[float] = Field(default=0, alias="RotateCenterY", description="回転中心のY座標")
	rotate_center_z: Optional[float] = Field(default=0, alias="RotateCenterZ", description="回転中心のZ座標")
	rotate_axis_vector_x: Optional[float] = Field(default=0, alias="RotateAxisVectorX", description="回転軸ベクトルのX要素")
	rotate_axis_vector_y: Optional[float] = Field(default=0, alias="RotateAxisVectorY", description="回転軸ベクトルのY要素")
	rotate_axis_vector_z: Optional[float] = Field(default=0, alias="RotateAxisVectorZ", description="回転軸ベクトルのZ要素")

#パーツパラメータを、カンマ区切りで繰り返し
class Part(BaseModel):
	part_id: Optional[str] = Field(None, alias="PartID", description="パーツのFMA ID（PartNameより優先されます）")
	part_name: Optional[str] = Field(None, alias="PartName", description="FMAのPreferred Name（PartID未指定時に有効）")
	part_color: Optional[str] = Field(default="FFFFFF", pattern=r"^[0-9a-fA-F]{6}$", alias="PartColor", description="16進数表記のパーツ描画色")
	part_scalar: Optional[float] = Field(default=0, alias="PartScalar", description="パーツに割り当てる数値（ScalarColorFlagをtrueにした際に利用）")
	scalar_color_flag: Optional[bool] = Field(default=False, alias="ScalarColorFlag", description="ヒートマップ表示に利用するかどうかを指定")
	part_opacity: Optional[float] = Field(default=1, ge=0, le=1, alias="PartOpacity", description="パーツの不透明度")
	part_representation: Optional[Literal["surface", "wireframe", "point"]] = Field(default="surface", alias="PartRepresentation", description="パーツの描画方法")
	use_for_bounding_box_flag: Optional[bool] = Field(default=True, alias="UseForBoundingBoxFlag", description="ズーム値算出時のバウンディングボックス計算に利用するかどうかを指定")
	part_delete_flag: Optional[bool] = Field(default=False, alias="PartDeleteFlag", description="パーツを描画しない場合にtrueを指定します")
	class Config:
		validate_by_name = True  # フィールド名でも入力可能

#説明文描画有無、説明文など、画像の説明文に関するconfiguration parameter群を設定します。
class Legend(BaseModel):
	draw_legend_flag: Optional[bool] = Field(default=False, alias="DrawLegendFlag", description="画像上に説明文を描画するかどうかを指定します")
	legend_position: Optional[Literal["UL"]] = Field(default="UL", alias="LegendPosition", description="説明文の描画位置")
	legend_color: Optional[str] = Field(default="FFFFFF", pattern=r"^[0-9a-fA-F]{6}$", alias="LegendColor", description="16進数表記の説明文描画色")
	legend_title: Optional[str] = Field(None, alias="LegendTitle", description="説明文のタイトル")
	legend: Optional[str] = Field(None, alias="Legend", description="説明文の内容")
	legend_author: Optional[str] = Field(None, alias="LegendAuthor", description="説明文のauthor")

#ピンのxyz座標、色、サイズ、形状など、ピンに関するconfiguration parameter群を設定します。
class Pin(BaseModel):
	pin_id: Optional[str] = Field(None, alias="PinID", description="ピンのID", exclude=True)
	pin_x: Optional[float] = Field(default=0, alias="PinX", description="ピンのX座標")
	pin_y: Optional[float] = Field(default=0, alias="PinY", description="ピンのY座標")
	pin_z: Optional[float] = Field(default=0, alias="PinZ", description="ピンのZ座標")
	pin_arrow_vector_x: Optional[float] = Field(default=0, alias="PinArrowVectorX", description="ピンの方向ベクトルのX要素")
	pin_arrow_vector_y: Optional[float] = Field(default=0, alias="PinArrowVectorY", description="ピンの方向ベクトルのY要素")
	pin_arrow_vector_z: Optional[float] = Field(default=0, alias="PinArrowVectorZ", description="ピンの方向ベクトルのZ要素")
	pin_up_vector_x: Optional[float] = Field(default=0, alias="PinUpVectorX", description="ピンの上方ベクトルのX要素")
	pin_up_vector_y: Optional[float] = Field(default=0, alias="PinUpVectorY", description="ピンの上方ベクトルのY要素")
	pin_up_vector_z: Optional[float] = Field(default=1, alias="PinUpVectorZ", description="ピンの上方ベクトルのZ要素")
	pin_screen_x: Optional[float] = Field(default=0, alias="PinScreenX", description="画像上のピンのX座標", exclude=True)
	pin_screen_y: Optional[float] = Field(default=0, alias="PinScreenY", description="画像上のピンのY座標", exclude=True)
	pin_description_draw_flag: Optional[bool] = Field(default=False, alias="PinDescriptionDrawFlag", description="ピンの説明文を画像上に描画するかどうかを指定します", exclude=True)
	pin_description_color: Optional[str] = Field(default="FFFFFF", pattern=r"^[0-9a-fA-F]{6}$", alias="PinDescriptionColor", description="16進数のピン説明文描画色", exclude=True)
	pin_color: Optional[str] = Field(default="FFFFFF", pattern=r"^[0-9a-fA-F]{6}$", alias="PinColor", description="16進数のピン描画色", exclude=True)
	pin_shape: Optional[Literal["CONE", "PIN_LONG"]] = Field(default="CONE", alias="PinShape", description="ピン形状", exclude=True)
	pin_size: Optional[int] = Field(default=10, alias="PinSize", description="ピンのサイズ", exclude=True)
	pin_coordinate_system_name: Optional[Literal["bp3d"]] = Field(default="bp3d", alias="PinCoordinateSystemName", description="ピンの3D空間名")
	pin_part_id: Optional[str] = Field(None, alias="PinPartID", description="pickメソッドによって返される最小単位のパーツのID")
	pin_part_name: Optional[str] = Field(None, alias="PinPartName", description="pickしたパーツの名称", exclude=True)
	pin_description: Optional[str] = Field(None, alias="PinDescription", description="ピンの説明文", exclude=True)

#ピックする最大数、画像上のxy座標など、pick methodに関するconfiguration parameter群を設定します。
class Pick(BaseModel):
	max_number_of_picks: Optional[int] = Field(default=20, alias="MaxNumberOfPicks", description="指定数分")
	screen_pos_x: Optional[int] = Field(None, alias="ScreenPosX", description="画像上ピック位置のX座標")
	screen_pos_y: Optional[int] = Field(None, alias="ScreenPosY", description="画像上ピック位置のY座標")

#光源のxyz座標、光源種別など、光源に関するconfiguration parameter群を設定します。
class Light(BaseModel):
	light_pos_x: Optional[float] = Field(default=0, alias="LightPosX", description="光源のX座標")
	light_pos_y: Optional[float] = Field(default=0, alias="LightPosY", description="光源のY座標")
	light_pos_z: Optional[float] = Field(default=0, alias="LightPosZ", description="光源のZ座標")
	light_add_distance: Optional[int] = Field(default=0, alias="LightAddDistance", description="光源をターゲット座標から指定mm遠ざけます")
	light_add_latitude: Optional[int] = Field(default=0, ge=0, le=360, alias="LightAddLatitude", description="ターゲット座標を中心として、光源を緯度方向に指定角度回転させます")
	light_add_longitude: Optional[int] = Field(default=0, ge=0, le=360, alias="LightAddLongitude", description="ターゲット座標を中心として、光源を経度方向に指定角度回転させます")
	lightIs_auto: Optional[bool] = Field(default=False, alias="LightIsAuto", description="trueを指定するとカメラと同位置に光源を配置します")
	lightIs_parallel: Optional[bool] = Field(default=False, alias="LightIsParallel", description="trueを指定すると並行光源、falseを指定すると点光源になります")
	lightIs_spec: Optional[bool] = Field(default=False, alias="LightIsSpec", description="trueを指定すると反射光有り、falseを指定すると反射光無しになります")

#分割フレーム数、1フレーム秒数など、animation methodに関するconfiguration parameter群を設定します。
class Animation(BaseModel):
	mode: Optional[Literal["camera", "object"]] = Field(default="camera", alias="Mode", description="cameraを回転するか、object（パーツ群）を回転するかを指定")
	is_latitude: Optional[bool] = Field(default=False, alias="IsLatitude", description="回転方向を指定します。(true:緯度方向、false：経度方向）")
	center_x: Optional[float] = Field(default=0, alias="CenterX", description="object回転モードにおける回転中心X座標")
	center_y: Optional[float] = Field(default=0, alias="CenterY", description="object回転モードにおける回転中心Y座標")
	center_z: Optional[float] = Field(default=0, alias="CenterZ", description="object回転モードにおける回転中心Z座標")
	axis_vector_x: Optional[float] = Field(default=0, alias="AxisVectorX", description="objectモードにおける回転軸ベクトルのX要素")
	axis_vector_y: Optional[float] = Field(default=0, alias="AxisVectorY", description="objectモードにおける回転軸ベクトルのY要素")
	axis_vector_z: Optional[float] = Field(default=0, alias="AxisVectorZ", description="objectモードにおける回転軸ベクトルのZ要素")
	divide_number: Optional[int] = Field(default=60, alias="DivideNumber", description="1回転の分割フレーム数")
	delay_time: Optional[int] = Field(default=10, alias="DelayTime", description="1フレームの表示ミリ秒")
	exp_num_of_colors: Optional[int] = Field(default=8, alias="ExpNumOfColors", description="GIFカラーマップのべき乗数")
	quantize_mode: Optional[Literal[0, 1]] = Field(default=8, alias="QuantizeMode", description="GIFカラーの量子化モード(0:ノーマル、1:トータル）")

class Payload(BaseModel):
	part:          List[Part]             = Field(None, alias="Part")
	common:        Optional[Common]       = Field(None, alias="Common")
	window:        Optional[Window]       = Field(None, alias="Window")
	camera:        Optional[Camera]       = Field(None, alias="Camera")
	object_rotate: Optional[ObjectRotate] = Field(None, alias="ObjectRotate")
	legend:        Optional[Legend]       = Field(None, alias="Legend")
	pin:           Optional[List[Pin]]    = Field(None, alias="Pin")
	pick:          Optional[Pick]         = Field(None, alias="Pick")
	light:         Optional[Light]        = Field(None, alias="Light")
	animation:     Optional[Animation]    = Field(None, alias="Animation")

	class Config:
		validate_by_name = True  # フィールド名でも入力可能


#focus methodに対して適切なmap configuration parameterを与えることで、指定したconfigurationの表示を適切に行うためのcamera位置の情報をJSON形式で取得することができます。
class CameraJson(BaseModel):
	CameraX:         float
	CameraY:         float
	CameraZ:         float
	TargetX:         float
	TargetY:         float
	TargetZ:         float
	CameraUpVectorX: float
	CameraUpVectorY: float
	CameraUpVectorZ: float
	Zoom:            float

class Focus(BaseModel):
	Camera: CameraJson

#pick methodに対して適切なmap configuration parameterを与えることで、レンダリング画像上の点から視線方向に伸びる直線がパーツと交差する点の情報を得ることができます。
class PinJson(BaseModel):
	PinX:            float
	PinY:            float
	PinZ:            float
	PinArrowVectorX: float
	PinArrowVectorY: float
	PinArrowVectorZ: float
	PinUpVectorX:    float
	PinUpVectorY:    float
	PinUpVectorZ:    float
	PinPartID:       str
	PinCoordinateSystemName: str = "bp3d"

class PickList(BaseModel):
	Pin: List[PinJson]

#map methodに対して適切なmap configuration parameterを与えることで、レンダリング画像上の点から視線方向に伸びる直線がパーツと交差する点の情報を得ることができます。
class Map(BaseModel):
	PinX: float
	PinY: float
	PinZ: float
	PinScreenX: int
	PinScreenY: int

class MapList(BaseModel):
	Map: List[Map]


def set_payload_default(payload: Payload):
	if payload.common is None:
		payload.common = Common()
	if payload.window is None:
		payload.window = Window()
	if payload.camera is None:
		payload.camera = Camera()
