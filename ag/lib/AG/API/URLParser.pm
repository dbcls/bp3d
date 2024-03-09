package AG::API::URLParser;

use strict;
use JSON::XS;
use Encode;
use Encode::Guess;
use SetEnv;
#use common;
use cgi_lib::common;
use AG::ComDB::Shorturl;

sub new (){
	my $pkg = shift;
	my $urlstr = shift;
	bless {
		url => $urlstr,
		jsonObj => undef,
	}, $pkg;
}

sub decodeForm($$) {
	my $self = shift;
	my $formdata = shift;
	my $FORM;
	if(defined $formdata){
		my @pairs = split(/&/,$formdata);
		foreach my $pair (@pairs){
			my($name, $value) = split(/=/, $pair);
			next if($value eq '');
			$value = &cgi_lib::common::url_decode($value);
			unless(&Encode::is_utf8($value)){
				# UTF8フラグ がない場合、decode して、UTF8フラグつきにする
				my $guessed_obj = &Encode::Guess::guess_encoding($value, qw/euc-jp shift-jis/);
				$value = $guessed_obj->decode($value) if(ref $guessed_obj);
			}
#		$value = Encode::encode('utf8', $value) if(utf8::is_utf8($value));
#			&utf8::decode($value) unless(&utf8::is_utf8($value));
			$value = &cgi_lib::common::decodeUTF8($value);
			$FORM = {} unless(defined $FORM);
			$FORM->{$name} .= "\0" if(exists($FORM->{$name}));
			$FORM->{$name} .= $value;
		}
	}
	return $FORM;
}

sub parseCommon($$) {
	my $self = shift;
	my $param = shift;
#	my $Common;
	my $Common = {                               # 共通項目	レンダリング、座標計算等において、BodyParts3Dサーバが動作する上で共通に必要な項目
		Model => "bp3d",                           # モデル	文字列	
		Version => undef,                          # バージョン	文字列	
		AnatomogramVersion => "20110318",          # アナトモグラム形式のバージョン	文字列	
		ScalarMaximum => 65535,                    # Scalar Maximum	整数	
		ScalarMinimum => -65535,                   # Scalar Minimum	整数	
		ColorbarFlag => JSON::XS::false,           # カラーバーの描画フラグ	Boolean	
		ScalarColorFlag => JSON::XS::false,        # 臓器描画にScalarColorを利用するフラグ	Boolean	
		TreeName => "isa",                         # 利用するTree名	文字列	
		DateTime => "",                            # "yyyymmddhhmmss"	現在時刻	文字列	
		CoordinateSystemName => "bp3d",            # 描画座標系	文字列	
		CopyrightType => "",                       # コピーライト画像のサイズ（未指定、large、medium、small）	文字列	
		PinDescriptionDrawFlag => JSON::XS::false, # true：description表示、false：description非表示（Boolean）
		PinIndicationLineDrawFlag => 0             # ピンからPin Descriptionへの線描画指定（整数／0:描画なし、1:ピン先端から描画、2:ピン終端から描画）
	};

	foreach my $c_key (keys(%$param)){
		my $c_val = $param->{$c_key};
		if($c_key eq "av"){
			delete $param->{$c_key};
		}elsif($c_key eq "sx"){
			$Common->{ScalarMaximum} = int($c_val + 0);
			delete $param->{$c_key};
		}elsif($c_key eq "sn"){
			$Common->{ScalarMinimum} = int($c_val + 0);
			delete $param->{$c_key};
		}elsif($c_key eq "cf"){
			if($c_val eq '0' || $c_val eq 'false'){
				$Common->{ColorbarFlag} = JSON::XS::false;
#				$Common->{ScalarColorFlag} = JSON::XS::false;
			}else{
				$Common->{ColorbarFlag} = JSON::XS::true;
#				$Common->{ScalarColorFlag} = JSON::XS::true;
			}
			delete $param->{$c_key};
		}elsif($c_key eq "hf"){
			if($c_val eq '0' || $c_val eq 'false'){
				$Common->{ScalarColorFlag} = JSON::XS::false;
			}else{
				$Common->{ScalarColorFlag} = JSON::XS::true;
			}
			delete $param->{$c_key};
		}elsif($c_key eq "tn"){
			if($c_val eq "isa"){
				$Common->{TreeName} = $c_val;
			}elsif($c_val eq "partof"){
				$Common->{TreeName} = $c_val;
			}
			delete $param->{$c_key};
		}elsif($c_key eq "model"){
			$Common->{Model} = $c_val;
			delete $param->{$c_key};
		}elsif($c_key eq "bv"){
			$Common->{Version} = $c_val;
			delete $param->{$c_key};
		}elsif($c_key eq "dt"){
			$Common->{DateTime} = $c_val;
			delete $param->{$c_key};
		}elsif($c_key eq "crd"){
			$Common->{CoordinateSystemName} = $c_val;
			delete $param->{$c_key};
		}elsif($c_key eq "cprt"){
			$Common->{CopyrightType} = $c_val;
			delete $param->{$c_key};
		}elsif($c_key eq "np"){
			$Common->{PinNumberDrawFlag} = JSON::XS::false if($param->{np} eq '0' || $param->{np} eq 'false');
			delete $param->{$c_key};
		}elsif($c_key eq "dp"){
			$Common->{PinDescriptionDrawFlag} = JSON::XS::true if($param->{dp} ne '0' && $param->{dp} ne 'false');
			delete $param->{$c_key};
		}elsif($c_key eq "dpl"){
			$Common->{PinIndicationLineDrawFlag} = $c_val + 0;
			delete $param->{$c_key};
		}elsif($c_key eq "dpod"){
#			$Common->{PointDescriptionDrawFlag} = JSON::XS::true if($param->{dpod} ne '0' && $param->{dpod} ne 'false');
			delete $param->{$c_key};
		}elsif($c_key eq "dpol"){
#			$Common->{PointIndicationLineDrawFlag} = $c_val + 0;
			delete $param->{$c_key};
		}
	}

	unless(defined $Common->{Version} && length $Common->{Version}){
		use AG::DB;
		use AG::DB::Version;
		my $db = new AG::DB();
#		my $dbh = $db->get_dbh();
#		$Common->{Version} = &common::getLatestVersion($dbh,$Common->{Model});
		$Common->{Version} = $db->latestDataVersion($Common->{Model});
#		undef $dbh;
		undef $db;
	}

	return $Common;
}

sub parseWindow($$) {
	my $self = shift;
	my $param = shift;
#	my $Window;
	my $Window = {                 # ウィンドウ項目	Window（描画画像全体）に関する項目
		ImageWidth => 500,           # 画像サイズ（width）	整数
		ImageHeight => 500,          # 画像サイズ（height）	整数
		BackgroundColor => "FFFFFF", # 背景色RGB（16進数6桁）	文字列
		BackgroundOpacity => 100,    # 背景の不透明度（0～100）	整数
		GridFlag => JSON::XS::false, # Gridの描画有無	Boolean
		GridTickInterval => 100,     # グリッドの描画単位（mm）	整数
		GridColor => "FFFFFF"        # グリッドの描画色RGB（16進数6桁）	文字列
	};
	foreach my $c_key (keys(%$param)){
		my $c_val = $param->{$c_key};
		if($c_key eq "iw"){
			$Window->{ImageWidth} = $c_val + 0;
			delete $param->{$c_key};
		}elsif($c_key eq "ih"){
			$Window->{ImageHeight} = $c_val + 0;
			delete $param->{$c_key};
		}elsif($c_key eq "bcl"){
			$Window->{BackgroundColor} = uc($c_val);
			delete $param->{$c_key};
		}elsif($c_key eq "bga"){
			$Window->{BackgroundOpacity} = $c_val + 0;
			delete $param->{$c_key};
		}elsif($c_key eq "gdr"){
			if($c_val eq '0' || $c_val eq 'false'){
				$Window->{GridFlag} = JSON::XS::false;
			}else{
				$Window->{GridFlag} = JSON::XS::true;
			}
			delete $param->{$c_key};
		}elsif($c_key eq "gtc"){
			$Window->{GridTickInterval} = $c_val + 0;
			delete $param->{$c_key};
		}elsif($c_key eq "gcl"){
			$Window->{GridColor} = uc($c_val);
			delete $param->{$c_key};
		}
	}
	return $Window;
}

sub parseCamera($$) {
	my $self = shift;
	my $param = shift;
	my $Camera;
#	my $Camera = {            # カメラ項目	Cameraに関する項目
#		CameraMode => "front",  # カメラ位置のモード（camera,front,back,left,right,top,bottom）。”camera”の場合にのみカメラ、ターゲット、upベクトルの指定が有効。	文字列
#		CameraX => 0,           # カメラのx座標	Double
#		CameraY => 0,           # カメラのy座標	Double
#		CameraZ => 0,           # カメラのz座標	Double
#		TargetX => 0,           # ターゲット（カメラ視線の中心）のx座標	Double
#		TargetY => 0,           # ターゲットのy座標	Double
#		TargetZ => 0,           # ターゲットのz座標	Double
#		CameraUpVectorX => 0,   # カメラupベクトルx要素	Double
#		CameraUpVectorY => 0,   # カメラupベクトルy要素	Double
#		CameraUpVectorZ => 0,   # カメラupベクトルz要素	Double
#		Zoom => 0,              # ズーム値（0～19.8）	Double
#		AddLatitudeDegree => 0, # 緯度方向への追加回転角度（0～360）	Double
#		AddLongitudeDegree => 0 # 経度方向への追加回転角度（0～360）	Double
#	};
	foreach my $c_key (keys(%$param)){
		my $c_val = $param->{$c_key};
		if($c_key eq "cx"){
			$Camera->{CameraX} = $c_val + 0;
			delete $param->{$c_key};
		}elsif($c_key eq "cy"){
			$Camera->{CameraY} = $c_val + 0;
			delete $param->{$c_key};
		}elsif($c_key eq "cz"){
			$Camera->{CameraZ} = $c_val + 0;
			delete $param->{$c_key};
		}elsif($c_key eq "tx"){
			$Camera->{TargetX} = $c_val + 0;
			delete $param->{$c_key};
		}elsif($c_key eq "ty"){
			$Camera->{TargetY} = $c_val + 0;
			delete $param->{$c_key};
		}elsif($c_key eq "tz"){
			$Camera->{TargetZ} = $c_val + 0;
			delete $param->{$c_key};
		}elsif($c_key eq "ux"){
			$Camera->{CameraUpVectorX} = $c_val + 0;
			delete $param->{$c_key};
		}elsif($c_key eq "uy"){
			$Camera->{CameraUpVectorY} = $c_val + 0;
			delete $param->{$c_key};
		}elsif($c_key eq "uz"){
			$Camera->{CameraUpVectorZ} = $c_val + 0;
			delete $param->{$c_key};
		}elsif($c_key eq "zm"){
			$c_val = 0 unless($c_val =~ /^[0-9\.]+$/);
			$Camera->{Zoom} = ($c_val + 0)*5;
#			$Camera->{Zoom} = 0;
			delete $param->{$c_key};
		}elsif($c_key eq "cameraMode"){
			$Camera->{CameraMode} = $c_val;
			delete $param->{$c_key};
		}elsif($c_key eq "addLongitude"){
			$Camera->{AddLongitudeDegree} = $c_val + 0;
			delete $param->{$c_key};
		}elsif($c_key eq "addLatitude"){
			$Camera->{AddLatitudeDegree} = $c_val + 0;
			delete $param->{$c_key};
		}
	}
	$Camera->{CameraMode} = 'camera' unless(defined $Camera && defined $Camera->{CameraMode} && length $Camera->{CameraMode});
	return $Camera;
}

sub parseClip($$) {
	my $self = shift;
	my $param = shift;
	my $Clip;
#	my $Clip => {                # クリップ項目	Clip（断面）に関する項目
#		ClipPlaneType => "normal", # クリップ面のタイプを指定。	文字列
#	                             #   normal：断面透明
#	                             #   section1_normal：背景+2D断面。色分け有
#	                             #   section2_normal：背景+2D断面。色分け無
#		ClipMode => "none",        # クリップ面指定方法	文字列
#	                             #   none：断面無し
#	                             #   depth：BoundingBoxの中央から視線ベクトル方向への奥行をClipDepthで指定
#	                             #   plane：AX+BY+CZ+D=0の断面を指定
#		ClipDepth => 0,            # クリップの奥行	Double
#		ClipPlaneA => 0,           # クリップ面パラメータA	Double
#		ClipPlaneB => 0,           # クリップ面パラメータB	Double
#		ClipPlaneC => 0,           # クリップ面パラメータC	Double
#		ClipPlaneD => 0            # クリップ面パラメータD	Double
#	};
	foreach my $c_key (keys(%$param)){
		my $c_val = $param->{$c_key};
		if($c_key eq "cm"){
#			if($c_val eq "N"){
#				$Clip->{ClipMode} = "none";
#			}elsif($c_val eq "D"){
			if($c_val eq "D"){
				$Clip->{ClipMode} = "depth";
			}elsif($c_val eq "P"){
				$Clip->{ClipMode} = "plane";
			}
			delete $param->{$c_key};
		}elsif($c_key eq "cd"){
			$Clip->{ClipDepth} = $c_val + 0;
			delete $param->{$c_key};
		}elsif($c_key eq "cpa"){
			$Clip->{ClipPlaneA} = $c_val + 0 if($c_val =~ /\-?[0-9\.]+$/);
			delete $param->{$c_key};
		}elsif($c_key eq "cpb"){
			$Clip->{ClipPlaneB} = $c_val + 0 if($c_val =~ /\-?[0-9\.]+$/);
			delete $param->{$c_key};
		}elsif($c_key eq "cpc"){
			$Clip->{ClipPlaneC} = $c_val + 0 if($c_val =~ /\-?[0-9\.]+$/);
			delete $param->{$c_key};
		}elsif($c_key eq "cpd"){
			$Clip->{ClipPlaneD} = $c_val + 0 if($c_val =~ /\-?[0-9\.]+$/);
			delete $param->{$c_key};
		}elsif($c_key eq "ct"){
			if($c_val eq "N"){
				$Clip->{ClipPlaneType} = "normal";
			}elsif($c_val eq "S"){
				$Clip->{ClipPlaneType} = "section1";
			}elsif($c_val eq "NS"){
				$Clip->{ClipPlaneType} = "section1_normal";
			}else{
				$Clip->{ClipPlaneType} = "section2_normal";
			}
			delete $param->{$c_key};
		}
	}
	return $Clip;
}

sub parsePart($$) {
	my $self = shift;
	my $param = shift;
	my @Part = ();
	my $UseForBoundingBoxFlag;
#	my %defPartItem = (                          # パーツ項目	Part（臓器）に関する項目	複数が前提のため、要素が1の場合であっても配列として記載
#		PartID => undef,                        # 臓器ID（名称に優先される）	文字列
#		PartName => undef,                      # 臓器名	文字列
#		PartColor => "FFFFFF",                  # 臓器色RGB（16進数6桁）	文字列
#		PartScalar => 0.0,                      # 臓器スカラー値	Double
#		PartScalarFlag => JSON::XS::false,      # 臓器をスカラー値で描画するFlag	Boolean
#		PartOpacity => 1,                       # 臓器不透明度	Double
#		PartRepresentation => "surface",        # 臓器描画方法（surface、wireframe、point）	文字列
#		UseForBoundingBoxFlag => JSON::XS::true, # BoundingBox計算への利用有無	Boolean
#		PartDeleteFlag => JSON::XS::false       # 臓器の削除フラグ（臓器引き算用）	Boolean
#	);
	for(my $i=1;;$i++){
		my $id = sprintf("%03d",$i);
		last if(!exists($param->{"oid$id"}) && !exists($param->{"onm$id"}));
		my %PartItem = ();
		foreach my $c_key (keys(%$param)){
			my $c_val = $param->{$c_key};
			if($c_key eq "oid$id"){
				$PartItem{PartID} = $c_val;
				delete $param->{$c_key};
			}elsif($c_key eq "onm$id"){
				$PartItem{PartName} = $c_val;
				delete $param->{$c_key};
			}elsif($c_key eq "ocl$id"){
				$PartItem{PartColor} = uc($c_val);
				delete $param->{$c_key};
			}elsif($c_key eq "osc$id"){
				$PartItem{PartScalar} = $c_val + 0;
				$PartItem{PartScalarFlag} = JSON::XS::true;
				$PartItem{ScalarColorFlag} = JSON::XS::true;
				delete $param->{$c_key};
			}elsif($c_key eq "osz$id"){
				if($c_val eq 'H'){
					$PartItem{PartDeleteFlag} = JSON::XS::true;
#					$PartItem{UseForBoundingBoxFlag} = JSON::XS::false;
				}elsif($c_val eq 'Z'){
					$PartItem{UseForBoundingBoxFlag} = JSON::XS::true;
					$UseForBoundingBoxFlag = JSON::XS::true;
				}
#				$organs[$1]{"organ_show_hide_zoom"} = $c_val;
				delete $param->{$c_key};
			}elsif($c_key eq "oop$id"){
				$PartItem{PartOpacity} = $c_val + 0;
				delete $param->{$c_key};
			}elsif($c_key eq "orp$id"){
				if($c_val eq "W"){
					$PartItem{PartRepresentation} = "wireframe";
				}elsif($c_val eq "P"){
					$PartItem{PartRepresentation} = "points";
				}
				delete $param->{$c_key};
			}elsif($c_key  eq "odcp$id"){
#				$organs[$1]{"organ_draw_child_point"} = $c_val;
				$PartItem{PartDrawChildPoint} = JSON::XS::true if($c_val ne '0' && $c_val ne 'false');
				delete $param->{$c_key};
			}
		}
		push(@Part,\%PartItem) if(scalar keys(%PartItem) > 0);
	}
	if(defined $UseForBoundingBoxFlag){
		foreach my $PartItem (@Part){
			$PartItem->{UseForBoundingBoxFlag} = JSON::XS::false unless(defined $PartItem->{UseForBoundingBoxFlag});
		}
	}
	return (scalar @Part > 0 ? (wantarray ? @Part : \@Part) : undef);
}

sub parseLegend($$) {
	my $self = shift;
	my $param = shift;
	my $Legend;
#	my $Legend => {                      # Legend項目	Legendに関する項目
#		DrawLegendFlag => JSON::XS::false, # Legendの描画有無フラグ	Boolean	
#		LegendPosition => "UL",            # Legendの描画位置（UL:左上のみ）	文字列	
#		LegendColor => "FFFFFF",           # Legendの描画色RGB（16進数6桁）	文字列	
#		LegendTitle => undef,              # LegendのTitle	文字列	
#		Legend => undef,                   # Legend	文字列	
#		LegendAuthor => undef              # Legendオーサー	Double	
#	};
	foreach my $c_key (keys(%$param)){
		my $c_val = $param->{$c_key};
		if($c_key eq "dl"){
			$Legend->{DrawLegendFlag} = JSON::XS::true if($c_val ne '0' && $c_val ne 'false');
			delete $param->{$c_key};
		}elsif($c_key eq "lp"){
			$Legend->{LegendPosition} = $c_val;
			delete $param->{$c_key};
		}elsif($c_key eq "lc"){
			$Legend->{LegendColor} = uc($c_val);
			delete $param->{$c_key};
		}elsif($c_key eq "lt"){
			$Legend->{LegendTitle} = $c_val;
			delete $param->{$c_key};
		}elsif($c_key eq "le"){
			$Legend->{Legend} = $c_val;
			delete $param->{$c_key};
		}elsif($c_key eq "la"){
			$Legend->{LegendAuthor} = $c_val;
			delete $param->{$c_key};
		}
	}
	return $Legend;
}

sub parsePin($$) {
	my $self = shift;
	my $param = shift;
	my @Pin = ();
#	my $Pin => {                                 # ピン項目	Pinに関する項目	要素が1の場合であっても配列として記載
#		PinPartID => undef,                        # PinID	文字列	
#		PinX => 0,                                 # Pinの3次元空間上x座標	Double	
#		PinY => 0,                                 # Pinの3次元空間上y座標	Double	
#		PinZ => 0,                                 # Pinの3次元空間上z座標	Double	
#		PinArrowVectorX => 0,                      # Pinのベクトルx要素	Double	
#		PinArrowVectorY => 0,                      # Pinのベクトルy要素	Double	
#		PinArrowVectorZ => 0,                      # Pinのベクトルz要素	Double	
#		PinUpVectorX => 0,                         # PinのUpベクトルx要素	Double	
#		PinUpVectorY => 0,                         # PinのUpベクトルy要素	Double	
#		PinUpVectorZ => 0,                         # PinのUpベクトルz要素	Double	
#		PinDescriptionDrawFlag => JSON::XS::false, # Pinのデスクリプション描画フラグ	Boolean	
#		PinDescriptionColor => "FFFFFF",           # デスクリプション描画色RGB(16進6桁）	文字列	
#		PinColor => "FFFFFF",                      # Pinの描画色RGB(16進6桁)	文字列	
#		PinShape => undef,                         # ピン形状	文字列	
#		PinCoordinateSystemName => "bp3d"          # ピン作成時座標系	文字列	
#	};

	for(my $i=1;;$i++){
		my $id = sprintf("%03d",$i);
		last if(!exists($param->{"pno$id"}));
		my %PinItem = ();
		foreach my $c_key (keys(%$param)){
			my $c_val = $param->{$c_key};

			if($c_key eq "pno$id") {
				$PinItem{PinPartNo} = $c_val;
				$PinItem{PinID} = $c_val unless(defined $PinItem{PinID} && length $PinItem{PinID});
				delete $param->{$c_key};
			}elsif($c_key eq "pid$id") {
				$PinItem{PinID} = $c_val;
				delete $param->{$c_key};
			}elsif($c_key eq "pgid$id") {
				$PinItem{PinGroupID} = $c_val;
				delete $param->{$c_key};
			}elsif($c_key eq "px$id") {
				$PinItem{PinX} = $c_val;
				delete $param->{$c_key};
			}elsif($c_key eq "py$id") {
				$PinItem{PinY} = $c_val;
				delete $param->{$c_key};
			}elsif($c_key eq "pz$id") {
				$PinItem{PinZ} = $c_val;
				delete $param->{$c_key};
			}elsif($c_key eq "pax$id") {
				$PinItem{PinArrowVectorX} = $c_val;
				delete $param->{$c_key};
			}elsif($c_key eq "pay$id") {
				$PinItem{PinArrowVectorY} = $c_val;
				delete $param->{$c_key};
			}elsif($c_key eq "paz$id") {
				$PinItem{PinArrowVectorZ} = $c_val;
				delete $param->{$c_key};
			}elsif($c_key eq "pux$id") {
				$PinItem{PinUpVectorX} = $c_val;
				delete $param->{$c_key};
			}elsif($c_key eq "puy$id") {
				$PinItem{PinUpVectorY} = $c_val;
				delete $param->{$c_key};
			}elsif($c_key eq "puz$id") {
				$PinItem{PinUpVectorZ} = $c_val;
				delete $param->{$c_key};
			}elsif($c_key eq "pcl$id") {
				$PinItem{PinColor} = uc($c_val);
				delete $param->{$c_key};
			}elsif($c_key eq "pdc$id") {
				$PinItem{PinDescriptionColor} = uc($c_val);
				delete $param->{$c_key};
			}elsif($c_key eq "pnd$id") {
				$PinItem{PinNumberDrawFlag} = JSON::XS::true if($c_val ne '0' && $c_val ne 'false');
				delete $param->{$c_key};
			}elsif($c_key eq "pdd$id") {
				$PinItem{PinDescriptionDrawFlag} = JSON::XS::true if($c_val ne '0' && $c_val ne 'false');
				delete $param->{$c_key};
			}elsif($c_key eq "poi$id") {
				$PinItem{PinPartID} = $c_val;
				delete $param->{$c_key};
			}elsif($c_key eq "pon$id") {
				$PinItem{PinPartName} = $c_val;
				delete $param->{$c_key};
			}elsif($c_key eq "pd$id") {
				$PinItem{PinDescription} = $c_val;
				delete $param->{$c_key};
			}elsif($c_key eq "ps$id") {
				if($c_val eq "CC"){
#					$PinItem{PinShape} = "coneshape_0.5_10";
					$PinItem{PinShape} = "CONE";
					$PinItem{PinSize} = 25.0;
				}elsif($c_val eq "PSS"){
#					$PinItem{PinShape} = "pin20090721_02";
					$PinItem{PinShape} = "PIN_LONG";
					$PinItem{PinSize} = 20.0;
				}elsif($c_val eq "PS"){
#					$PinItem{PinShape} = "pin20090721_02";
					$PinItem{PinShape} = "PIN_LONG";
					$PinItem{PinSize} = 37.5;
				}elsif($c_val eq "PM"){
#					$PinItem{PinShape} = "pin20090721_02";
					$PinItem{PinShape} = "PIN_LONG";
					$PinItem{PinSize} = 75.0;
				}elsif($c_val eq "PL"){
#					$PinItem{PinShape} = "pin20090721_03";
					$PinItem{PinShape} = "PIN_LONG";
					$PinItem{PinSize} = 112.5;
				}elsif($c_val eq "SC"){
					$PinItem{PinShape} = $c_val;
				}
				delete $param->{$c_key};
			}elsif($c_key eq "pcd$id") {
				$PinItem{PinCoordinateSystemName} = $c_val;
				delete $param->{$c_key};
			}
		}
		push(@Pin,\%PinItem) if(scalar keys(%PinItem) > 0);
	}
	return (scalar @Pin > 0 ? (wantarray ? @Pin : \@Pin) : undef);
}

sub parsePick($$) {
	my $self = shift;
	my $param = shift;
	my $Pick;
#	my $Pick => {             # Pick項目	Pickに関する項目
#		MaxNumberOfPicks => 20, # ピックする最大数	整数	
#		ScreenPosX => 0,        # 画像上のピック座標X	整数	
#		ScreenPosY => 0,        # 画像上のピック座標Y	整数	
#		ClipType => 2           # クリップタイプ
#                            #  0：クリップ平面上ピック無、全結果を返す
#                            #  1：クリップ平面上ピック無、クリップアウトマーカーを返さない
#                            #  2：クリップ平面上をピック、全結果を返す
#                            #  3：クリップ平面上をピック、クリップアウトマーカーを返さない
#                            #  4：クリップ平面上をピック、その他を全て消す	整数	
#	};
	foreach my $c_key (keys(%$param)){
		my $c_val = $param->{$c_key};
		if($c_key eq "px"){
			$Pick->{ScreenPosX} = $c_val + 0;
			delete $param->{$c_key};
		}elsif($c_key eq "py"){
			$Pick->{ScreenPosY} = $c_val + 0;
			delete $param->{$c_key};
		}elsif($c_key eq "px1"){
			$Pick->{ScreenPosX1} = $c_val + 0;
			delete $param->{$c_key};
		}elsif($c_key eq "py1"){
			$Pick->{ScreenPosY1} = $c_val + 0;
			delete $param->{$c_key};
		}elsif($c_key eq "px2"){
			$Pick->{ScreenPosX2} = $c_val + 0;
			delete $param->{$c_key};
		}elsif($c_key eq "py2"){
			$Pick->{ScreenPosY2} = $c_val + 0;
			delete $param->{$c_key};

		#VoxelPick用に追加
		}elsif($c_key eq "vr"){
#			$Pick->{VoxelRange} = $c_val + 0;
			$Pick->{VoxelRadius} = $c_val + 0;
			delete $param->{$c_key};

		}
	}
	return $Pick;
}

sub parsePoint($$) {
	my $self = shift;
	my $param = shift;
	my @Point = ();

	for(my $i=1;;$i++){
		my $id = sprintf("%03d",$i);
		last if(!exists($param->{"poid$id"}));
		my %PointItem = ();
		foreach my $c_key (keys(%$param)){
			my $c_val = $param->{$c_key};

			if($c_key eq "poid$id") {
				$PointItem{PointID} = $c_val;
				delete $param->{$c_key};
			}elsif($c_key eq "porm$id") {
				$PointItem{PointRemove} = JSON::XS::true if($c_val ne '0' && $c_val ne 'false');
				delete $param->{$c_key};
			}elsif($c_key eq "pocl$id") {
				$PointItem{PointColor} = uc($c_val);
				delete $param->{$c_key};
			}elsif($c_key eq "poop$id") {
				$PointItem{PointOpacity} = $c_val + 0;
				delete $param->{$c_key};
			}elsif($c_key eq "pore$id") {
				$PointItem{PointRepresentation} = $c_val;
				delete $param->{$c_key};
			}elsif($c_key eq "posh$id") {
#				if($c_val eq "SS"){
#					$PointItem{PinShape} = "PIN";
#					$PointItem{PinSize} = 10.0;
#				}elsif($c_val eq "SM"){
#					$PointItem{PinShape} = "PIN";
#					$PointItem{PinSize} = 15.0;
#				}elsif($c_val eq "SL"){
#					$PointItem{PinShape} = "PIN_LONG";
#					$PointItem{PinSize} = 20.0;
#				}
				$PointItem{PointShape} = $c_val;
				delete $param->{$c_key};
			}
		}
		push(@Point,\%PointItem) if(scalar keys(%PointItem) > 0);
	}
	return (scalar @Point > 0 ? (wantarray ? @Point : \@Point) : undef);
}

sub parseObjectRotate($$) {
	my $self = shift;
	my $param = shift;
	my $ObjectRotate;
#	my $ObjectRotate => {  #
#		DateTime => undef, #
#	};

	foreach my $c_key (keys(%$param)){
		my $c_val = $param->{$c_key};
		if($c_key eq "autorotate"){
			$ObjectRotate->{DateTime} = $c_val + 0;
			delete $param->{$c_key};
		}elsif($c_key eq "orcx"){
			$ObjectRotate->{RotateCenterX} = $c_val + 0;
			delete $param->{$c_key};
		}elsif($c_key eq "orcy"){
			$ObjectRotate->{RotateCenterY} = $c_val + 0;
			delete $param->{$c_key};
		}elsif($c_key eq "orcz"){
			$ObjectRotate->{RotateCenterZ} = $c_val + 0;
			delete $param->{$c_key};
		}elsif($c_key eq "orax"){
			$ObjectRotate->{RotateAxisVectorX} = $c_val + 0;
			delete $param->{$c_key};
		}elsif($c_key eq "oray"){
			$ObjectRotate->{RotateAxisVectorY} = $c_val + 0;
			delete $param->{$c_key};
		}elsif($c_key eq "oraz"){
			$ObjectRotate->{RotateAxisVectorZ} = $c_val + 0;
			delete $param->{$c_key};
		}elsif($c_key eq "ordg"){
			$ObjectRotate->{RotateDegree} = $c_val + 0;
			delete $param->{$c_key};
		}
	}
	return $ObjectRotate;
}

sub parseURL($$) {
	my $self = shift;
	my $formdata = shift;
	my $form = $self->decodeForm($formdata);
	if(exists($form->{shorten})){
=pod
		use common_db;
		my $dbh = &common_db::get_dbh();
		my $sth = $dbh->prepare(qq|select sp_original from shorten_param where sp_shorten=?|);
		$sth->execute($form->{shorten});
		my $column_number = 0;
		my $sp_original;
		$sth->bind_col(++$column_number, \$sp_original, undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;
		undef $dbh;
=cut
		my $shorturl = new AG::ComDB::Shorturl;
		my $sp_original = $shorturl->get_long_url($form->{shorten});

		$form = $self->decodeForm($sp_original) if(defined $sp_original);
		undef $sp_original;
		undef $shorturl;
	}
	my $Window = $self->parseWindow($form);
	my $Part = $self->parsePart($form);
	my $Pin = $self->parsePin($form);
	if(defined $Window || defined $Part || defined $Pin){
		my $Common = $self->parseCommon($form);
		my $Camera = $self->parseCamera($form);
		my $Clip = $self->parseClip($form);
		my $Pick = $self->parsePick($form);
		my $Legend = $self->parseLegend($form);
		my $Point = $self->parsePoint($form);
		my $ObjectRotate = $self->parseObjectRotate($form);

		$self->{jsonObj} = {};
		$self->{jsonObj}->{Common} = $Common if(defined $Common);
		$self->{jsonObj}->{Window} = $Window if(defined $Window);
		$self->{jsonObj}->{Camera} = $Camera if(defined $Camera);
		$self->{jsonObj}->{Clip} = $Clip if(defined $Clip);
		$self->{jsonObj}->{Part} = $Part if(defined $Part);
		$self->{jsonObj}->{Pick} = $Pick if(defined $Pick);
		$self->{jsonObj}->{Pin} = $Pin if(defined $Pin);
		$self->{jsonObj}->{Legend} = $Legend if(defined $Legend);
		$self->{jsonObj}->{Point} = $Point if(defined $Point);
		$self->{jsonObj}->{ObjectRotate} = $ObjectRotate if(defined $ObjectRotate);

		if(exists($form->{callback})){
			$self->{jsonObj}->{callback} = $form->{callback};
			delete $form->{callback};
		}

		delete $form->{_dc} if(exists($form->{_dc}));

		if(scalar keys(%$form) > 0){
			my $env = SetEnv->new;
			my $log_file = $env->{basePath}."tmp_image/AgURLParser.txt";

			open OUT,">> $log_file";
			foreach my $key (sort keys(%$form)){
				print OUT qq|$key=[$form->{$key}]\n|;
			}
			print OUT qq|\n|;
			close(OUT);
		}
	}
}

1;
