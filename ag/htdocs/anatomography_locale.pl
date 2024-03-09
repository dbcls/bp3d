use strict;

sub getLocale {
	my $lng = shift;
	my %LOCALE = ();

	$LOCALE{TOOLTIP_FOCUS_CENTER} = "Focus(Centering) Selected";
	$LOCALE{TOOLTIP_FOCUS} = "Focus(Centering & Zoom) Selected";
	$LOCALE{TOOLTIP_AUTO_ROTATION} = "Auto rotation";

#	$LOCALE{ANATOMO_REP_LABEL} = "Representation";
	$LOCALE{ANATOMO_REP_LABEL} = "Draw Type";

	if (!defined $lng || $lng eq "ja" || $lng eq "") {
		$LOCALE{COMMAND_LABEL} = "コマンド";
		$LOCALE{COMMAND_TITLE_ROTATE} = "回転";
		$LOCALE{COMMAND_TITLE_MOVE} = "移動";
		$LOCALE{COMMAND_TITLE_ZOOM} = "拡大縮小";
		$LOCALE{ANATOMO_ANATOMOGRAM_LABEL} = "アナトモグラム";
#		$LOCALE{ANATOMO_EDITOR_LABEL} = "エディタURL";
		$LOCALE{ANATOMO_EDITOR_LABEL} = "現在のサイト状態を再現";
#		$LOCALE{ANATOMO_IMAGE_LABEL} = "画像URL";
		$LOCALE{ANATOMO_IMAGE_LABEL} = "モデルイメージを再現";

		$LOCALE{ANATOMO_EDITOR_LABEL_A} = "hyperlink to the present status of this site";
		$LOCALE{ANATOMO_IMAGE_LABEL_IMG} = "Embed as an image";
		$LOCALE{ANATOMO_EMBEDDED_LABEL} = "モデルを操作可能イメージとして埋め込み";

		$LOCALE{ANATOMO_OPEN} = "大きなイメージで見る";
		$LOCALE{ANATOMO_COMMENT} = "絵に説明を付ける";
		$LOCALE{COORDINATE_SYSTEM} = "描画座標系";
		$LOCALE{CONVERT_URL_ERRMSG} = "URL変換エラー";


		$LOCALE{TOOLTIP_ROTATE} = "回転";
		$LOCALE{TOOLTIP_MOVE} = "移動";

		$LOCALE{HEATMAP_SET_MAX_VALUE} = "HeatMapの最大値に設定";
		$LOCALE{HEATMAP_SET_MIN_VALUE} = "HeatMapの最小値に設定";

	} else {
		$LOCALE{COMMAND_LABEL} = "Command";
		$LOCALE{COMMAND_TITLE_ROTATE} = "Rotate";
		$LOCALE{COMMAND_TITLE_MOVE} = "Move";
		$LOCALE{COMMAND_TITLE_ZOOM} = "Zoom";
		$LOCALE{ANATOMO_ANATOMOGRAM_LABEL} = "Anatomogram";
#		$LOCALE{ANATOMO_EDITOR_LABEL} = "Editor URL";
#		$LOCALE{ANATOMO_EDITOR_LABEL} = "Paste link to this page in email";
#		$LOCALE{ANATOMO_EDITOR_LABEL} = "Share the present status of this site.";
		$LOCALE{ANATOMO_EDITOR_LABEL} = "URL for this site with map";
#		$LOCALE{ANATOMO_IMAGE_LABEL} = "Image URL";
#		$LOCALE{ANATOMO_IMAGE_LABEL} = "Paste link to this Image in email";
#		$LOCALE{ANATOMO_IMAGE_LABEL} = "Share this body image you made.";
		$LOCALE{ANATOMO_IMAGE_LABEL} = "URL for this map image";
#		$LOCALE{ANATOMO_EMBEDDED_LABEL} = "Paste HTML to embed in website";
#		$LOCALE{ANATOMO_EMBEDDED_LABEL} = "Embed this body model as interactive image.";

		$LOCALE{ANATOMO_EDITOR_LABEL_A} = "hyperlink to the present status of this site";
		$LOCALE{ANATOMO_IMAGE_LABEL_IMG} = "Embed as an image";
		$LOCALE{ANATOMO_EMBEDDED_LABEL} = "Embed as an interactive window";

		$LOCALE{ANATOMO_OPEN} = "View Larger Image";
		$LOCALE{ANATOMO_COMMENT} = "Put a legend to anatomogram";
		$LOCALE{COORDINATE_SYSTEM} = "Coordinate system";
		$LOCALE{CONVERT_URL_ERRMSG} = "URL translation errors";

		$LOCALE{TOOLTIP_ROTATE} = "Rotate";
		$LOCALE{TOOLTIP_MOVE} = "Move";

		$LOCALE{HEATMAP_SET_MAX_VALUE} = "Set this value as the maximum.";
		$LOCALE{HEATMAP_SET_MIN_VALUE} = "Set this value as the minimum.";
	}
	return %LOCALE;
}
1;
