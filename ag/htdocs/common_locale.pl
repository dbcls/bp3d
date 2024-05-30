use strict;

sub getLocale {
	my $lng = shift;
	my %LOCALE = ();

	$LOCALE{BP3D_TITLE} = qq|BodyParts3D/Anatomography|;
	$LOCALE{BP3D_DESCRIPTION} = qq|Select parts and Make Embeddable Model of Your Own.|;

	$LOCALE{DOCUMENT_TITLE}     = qq|$LOCALE{BP3D_TITLE} : $LOCALE{BP3D_DESCRIPTION}|;

	$LOCALE{FMA_DESCRIPTION_URL} = qq|http://sig.biostr.washington.edu/projects/fm/AboutFM.html|;
	$LOCALE{FMA_DESCRIPTION_HTML} = qq|<div style="padding:4px;font-weight:bold;vertical-align:bottom;"><a href="$LOCALE{FMA_DESCRIPTION_URL}" target="_blank" style="color:#0000ee;background: url(css/external.png) no-repeat scroll right bottom;padding-right:14px;">FMA is anatomical ontology by University of Washington School of Medicine</a></div>|;

	$LOCALE{VERSION_COMMENT_STYLE} = qq|display:none;font-size:12px;color:#000000;margin-left:2px;padding:4px;|;

#	$LOCALE{NOT_LATEST_VERSION} = qq|Data is not the latest version !|;
	$LOCALE{NOT_LATEST_VERSION} = qq||;
	$LOCALE{NOT_LATEST_VERSION_STYLE} = qq|display:none;font-size:12px;font-weight:bold;text-decoration:underline;color:#ff0000;margin-left:2px;padding:4px;|;
#	$LOCALE{NOT_LATEST_VERSION_STYLE} = qq|display:none;font-size:12px;font-weight:bold;text-decoration:underline;color:#ff3333;margin-left:2px;padding:4px;background-color:#fff;|;
#	$LOCALE{NOT_LATEST_VERSION_STYLE} = qq|display:none;font-size:12px;font-weight:bold;text-decoration:underline;color:#444;margin-left:2px;padding:4px;background-color:#ff6666;|;

	$LOCALE{VERSION_INFORMATION} = qq|" i " at the end of the data version (ex. 4.3i) denotes FMA data were augmented by ourselves to improve aggregation of smaller into larger parts. see <a href="http://rgm22.nig.ac.jp/mediawiki-ogareport/index.php/Site_information#Whats_new" target="_blank">http://rgm22.nig.ac.jp/mediawiki-ogareport/index.php/Site_information#Whats_new</a>|;
	$LOCALE{VERSION_INFORMATION_STYLE} = qq|font-size:10px;color:#000000;margin-left:2px;padding:4px;|;

	$LOCALE{DATA_VERSION} = 'Data Version';
	$LOCALE{OBJECTS_SET} = 'Objects set';
	$LOCALE{TREE_VERSION} = 'Tree version';
	$LOCALE{PART_OF_RELATION} = 'part of relations given as attributes in fma';
	$LOCALE{PART_OF_RELATION_BP3D} = 'part of relations added for BodyParts3D';
	$LOCALE{PART_OF_RELATION_BP3D_MESSAGE} = 'inference: "left-part" is part of "left-whole" when "part" is part of "whole".';

	$LOCALE{TITLE_HOME}     = "Home";
	$LOCALE{TABTIP_HOME}     = "Home";

#	$LOCALE{TITLE_BP3D}     = "BP3D Viewer";
	$LOCALE{TITLE_BP3D}     = " ";
	$LOCALE{TABTIP_BP3D}     = "BP3D Viewer";

#	$LOCALE{TITLE_AG}     = "Anatomography";
	$LOCALE{TITLE_AG}     = " ";
	$LOCALE{TABTIP_AG}     = "Anatomography";

	$LOCALE{BP3D_MODEL_ICON_LABEL} = "Share this body icon you made.";

	$LOCALE{TITLE_REVIEWS}     = "Reviews";
	$LOCALE{TABTIP_REVIEWS}     = "Reviews";

#	$LOCALE{TITLE_INFORMATION}  = "Information";
	$LOCALE{TITLE_INFORMATION}  = " ";
	$LOCALE{TABTIP_INFORMATION} = "Information";
	$LOCALE{BUTTON_INFORMATION}  = "Information";
	$LOCALE{BUTTON_ERROR_REPORT}  = "Error Report";

#	$LOCALE{BUTTON_OBJFILE_LIST}  = "list of obj files";
	$LOCALE{BUTTON_OBJFILE_LIST}  = "obj2FMA";
	$LOCALE{BUTTON_FMA2OBJFILE_LIST}  = "FMA2obj";

#	$LOCALE{GOTO_AG} = qq|<div class="goto-ag-base"><div class="goto-ag-btn"><a class="goto-ag-btn" href="#"><img src="css/goto_ag.png"></a></div></div>|;
#	$LOCALE{GOTO_AG_WIDTH} = 150;
	$LOCALE{GOTO_AG_WIDTH} = 200;


#	$LOCALE{GOTO_AG_WIDTH} = 200;


	$LOCALE{REPRESENTATION} = qq|Representation|;
	$LOCALE{REP_ID} = qq|Representation|;
	$LOCALE{REP_DENSITY} = qq|Model / Concept density|;
	$LOCALE{REP_PRIMITIVE} = qq|Representation method|;
	$LOCALE{CDI_NAME} = qq|Represented concept|;
	$LOCALE{ART_NAME} = qq|Model component|;

	$LOCALE{ELEMENT} = qq|ELEMENT|;
	$LOCALE{ELEMENT_COMPOUND} = qq|ELEMENT and complete COMPOUND|;
	$LOCALE{COMPLETE_COMPOUND} = qq|Complete COMPOUND|;
	$LOCALE{INCOMPLETE_COMPOUND} = qq|Incomplete COMPOUND|;

	$LOCALE{ELEMENT_PRIMARY} = qq|ELEMENT/PRIMARY|;
	$LOCALE{COMPOUND_SECONDARY} = qq|COMPOUND/SECONDARY|;
	$LOCALE{DETAIL_TITLE_TAB_INFORMATION} = "BodyParts3D";
	$LOCALE{DETAIL_TITLE_TAB_TWEET}       = "Comment";
	$LOCALE{DETAIL_TITLE_TAB_CONCEPT}     = "Concept(FMA)";

	$LOCALE{BUILD_UP}       = "Build-up";
	$LOCALE{TREE_TYPE}      = "$LOCALE{BUILD_UP} logic";

	$LOCALE{LINK_TAB_INFORMATION} = qq|<a href="#" onclick="return click_information_button({hash:\\'#BuildUp\\'});"><img src="css/information.png" width=12 height=12></a>|;
	$LOCALE{FMA_INFORMATION} = qq|<a href="#" onclick="return click_information_button({hash:\\'#FMA\\'});"><img src="css/information.png" width=12 height=12></a>|;

	$LOCALE{TREE_TYPE_HTML} = qq|<label style="font-size:14px;font-weight:bold;vertical-align:bottom;">$LOCALE{TREE_TYPE}$LOCALE{LINK_TAB_INFORMATION}&nbsp;</label>|;

#	$LOCALE{TREE_TYPE_NORTH_HTML} = qq|<table cellpadding=0 cellspacing=0><tr>|;
#	$LOCALE{TREE_TYPE_NORTH_HTML}.= qq|<td><img src="css/1.png" align=center width=44 height=44></td>|;
#	$LOCALE{TREE_TYPE_NORTH_HTML}.= qq|<td style="padding-left:1em;"><label style="white-space:nowrap;">$LOCALE{BUILD_UP} by&nbsp;</label><label id="navigate-north-buildup" style="white-space:nowrap;"></label></td>|;
#	$LOCALE{TREE_TYPE_NORTH_HTML}.= qq|</tr></table>|;

	$LOCALE{SEE_HOW_TO_URL} = "https://www.youtube.com/watch?v=CJLH1PqH_hg";

#	$LOCALE{NEIGHBOR_PARTS_GRID_EMPTY_MESSAGE} = "Initiate search by picking origin on screen.";
	$LOCALE{NEIGHBOR_PARTS_GRID_EMPTY_MESSAGE} = "Pick one point to gather neighboring elements of it.";

	$LOCALE{CLICK_IMAGE_GRID_EMPTY_MESSAGE} = "Click on the Image";

	if(!defined $lng || $lng eq "ja" || $lng eq ""){
		$LOCALE{SEE_WHAT_YOU_CAN_GET} = "できること";
		$LOCALE{SEE_WHAT_YOU_CAN_GET_URL} = "info/userGuide/application/index.html";
		$LOCALE{SEE_HOW_TO} = "使い方";

		$LOCALE{INFORMATION_URL} = "info/index.html";
		$LOCALE{LICENSE_URL} = "info/license/index.html";

		$LOCALE{TOP_TITLE}          = "トップページ";
		$LOCALE{TOP_WHATSNEW_TITLE} = "新着情報";

		$LOCALE{TABTIP_BP3D}     = "人体各部位のインデックス";
		$LOCALE{TABTIP_AG}     = "人体モデル図編集ツール";

		$LOCALE{BP3D_MODEL_ICON_LABEL} = "モデルアイコンを再現";

		$LOCALE{TOP_EDIT_TITLE}  = "編集";

		$LOCALE{TREE_TYPE_1}       = "便宜的";
		$LOCALE{TREE_TYPE_2}       = "is_a";
		$LOCALE{TREE_TYPE_3}       = "is_a";
		$LOCALE{TREE_TYPE_4}       = "PartOf";

		$LOCALE{OR_MODE} = "以上";

		$LOCALE{IMAGE_POSITION}       = "方向";
		$LOCALE{IMAGE_POSITION_ROTATE} = "回転";
		$LOCALE{IMAGE_POSITION_FRONT} = "前";
		$LOCALE{IMAGE_POSITION_BACK}  = "後";
		$LOCALE{IMAGE_POSITION_LEFT}  = "左";
		$LOCALE{IMAGE_POSITION_RIGHT} = "右";
		$LOCALE{IMAGE_POSITION_WIDTH} = 50;
		$LOCALE{IMAGE_POSITION_LIST_WIDTH} = 40;

		$LOCALE{IMAGE_TREE_DEPTH}       = "深さ";
		$LOCALE{IMAGE_TREE_DEPTH_WIDTH} = 35;
		$LOCALE{IMAGE_TREE_DEPTH_LIST_WIDTH} = 20;

		$LOCALE{ICON_REG_MSG}    = "登録済み";
		$LOCALE{ICON_UNREG_MSG}  = "未登録";
		$LOCALE{TREE_TITLE}      = "分類";
		$LOCALE{TREE_ROOT_TITLE} = "ホーム";
		$LOCALE{LOCALE_TITLE}    = "English";
		$LOCALE{CONTENT_TITLE}   = "画像を選択してください";
		$LOCALE{FILTER_TITLE}    = "フィルター";
		$LOCALE{SEARCH_GRID_FILTER_YES} = "有り";
		$LOCALE{SEARCH_GRID_FILTER_NO} = "無し";

		$LOCALE{DISPTYPE_TITLE}  = "表示形式";
		$LOCALE{DISPTYPE_THUMB}  = "サムネイル";
		$LOCALE{DISPTYPE_LIST}   = "リスト";
		$LOCALE{DISPTYPE_TREE}   = "ツリー";
		$LOCALE{DISPTYPE_WIDTH} = 80;
		$LOCALE{DISPTYPE_LIST_WIDTH} = 70;

		$LOCALE{SORT_TITLE}        = "ソート";
		$LOCALE{SORT_TITLE_NONE}   = "無し";
		$LOCALE{SORT_TITLE_NAME_J} = "名称(和名)";
		$LOCALE{SORT_TITLE_NAME_K} = "名称(かな)";
		$LOCALE{SORT_TITLE_NAME_E} = "名称(英名)";
		$LOCALE{SORT_TITLE_NAME_L} = "名称(ラテン名)";
		$LOCALE{SORT_TITLE_VOLUME} = "体積";
		$LOCALE{SORT_TITLE_LAST}   = "更新日時";
		$LOCALE{SORT_WIDTH}        = 100;
		$LOCALE{SORT_LIST_WIDTH}   = 90;

		$LOCALE{DETAIL_TITLE}    = "詳細";
		$LOCALE{DETAIL_TITLE_NAME}   = "名称";
		$LOCALE{DETAIL_TITLE_BNAME}  = "学名";
		$LOCALE{DETAIL_TITLE_SIZE}   = "ファイルサイズ";
		$LOCALE{DETAIL_TITLE_LAST}   = "更新日時";
		$LOCALE{DETAIL_TITLE_DETAIL} = "詳細";
		$LOCALE{DETAIL_TITLE_ICON_URL} = "アイコンURL";
		$LOCALE{DETAIL_TITLE_NAME_K} = "かな";
		$LOCALE{DETAIL_TITLE_NAME_J} = "和名";
		$LOCALE{DETAIL_TITLE_NAME_E} = "英名";
		$LOCALE{DETAIL_TITLE_NAME_L} = "ラテン語";
		$LOCALE{DETAIL_TITLE_ORGAN_SYSTEM_J} = "臓器系・器官系(日本語)";
		$LOCALE{DETAIL_TITLE_ORGAN_SYSTEM_E} = "臓器系・器官系(英語)";
		$LOCALE{DETAIL_TITLE_SYNONYM_J} = "シノニム(日本語)";
#		$LOCALE{DETAIL_TITLE_SYNONYM_E} = "シノニム(英語)";
		$LOCALE{DETAIL_TITLE_SYNONYM_E} = "シノニム";
		$LOCALE{DETAIL_TITLE_DEFINITION_E} = "定義";
		$LOCALE{DETAIL_TITLE_XMIN} = "Xmin";
		$LOCALE{DETAIL_TITLE_XMAX} = "Xmax";
		$LOCALE{DETAIL_TITLE_YMIN} = "Ymin";
		$LOCALE{DETAIL_TITLE_YMAX} = "Ymax";
		$LOCALE{DETAIL_TITLE_ZMIN} = "Zmin";
		$LOCALE{DETAIL_TITLE_ZMAX} = "Zmax";
		$LOCALE{DETAIL_TITLE_VOLUME} = "体積";
		$LOCALE{DETAIL_TITLE_POINT_PARENT} = "親FMAID";
		$LOCALE{DETAIL_TITLE_POINT_PARENT_ID} = "親FMAID";
		$LOCALE{DETAIL_TITLE_POINT_PARENT_NAME} = "親解剖構造名";
		$LOCALE{DETAIL_TITLE_POINT_CHILDREN} = "点構造要素";

		$LOCALE{COMMENT_TITLE}         = "コメント";
		$LOCALE{COMMENT_TITLE_REFRESH} = "コメント更新";
		$LOCALE{COMMENT_TITLE_PLUS}    = "コメント追加";
		$LOCALE{COMMENT_TITLE_REPLY}   = "返信";
		$LOCALE{COMMENT_TITLE_REPLY_SEL} = "選択コメント返信";
		$LOCALE{COMMENT_TITLE_DELETE_SEL} = "選択コメント削除";
		$LOCALE{COMMENT_TITLE_DELETE}  = "削除";
		$LOCALE{COMMENT_TITLE_DELETE_MSG} = "コメントを削除してよろしいですか？";
		$LOCALE{COMMENT_TITLE_DELETE_ERRMSG} = "コメントの削除に失敗しました";
		$LOCALE{COMMENT_TITLE_EDIT}  = "編集";
		$LOCALE{COMMENT_WIN_TITLE}    = "コメントを入力してください";
		$LOCALE{COMMENT_WIN_WAITMSG}  = "コメントを登録しています";
		$LOCALE{COMMENT_WIN_TITLE_SEND} = "登録";
		$LOCALE{COMMENT_WIN_TITLE_CANCEL} = "中止";
		$LOCALE{COMMENT_WIN_ADDMSG}  = "コメントを登録しました";
		$LOCALE{COMMENT_WIN_ERRMSG}  = "コメントの登録に失敗しました";

		$LOCALE{FEEDBACK_TITLE_DELETE_MSG} = "[ \%s ] を削除してよろしいですか？";


		$LOCALE{PAGING_REFRESH}   = "コメント更新";
		$LOCALE{PAGING_FIRST}     = "最初のページへ";
		$LOCALE{PAGING_LAST}      = "最後のページへ";
		$LOCALE{PAGING_NEXT}      = "次のページへ";
		$LOCALE{PAGING_PREV}      = "前のページへ";
		$LOCALE{PAGING_DISP_MSG}  = "表示中のコメント";
		$LOCALE{PAGING_EMPTY_MSG} = "表示するはコメントありません";

		$LOCALE{GRID_TITLE_NAME_J} = $LOCALE{DETAIL_TITLE_NAME_J};
		$LOCALE{GRID_TITLE_NAME_E} = $LOCALE{DETAIL_TITLE_NAME_E};
		$LOCALE{GRID_TITLE_NAME_K} = "かな";
		$LOCALE{GRID_TITLE_PHASE} = "フェーズ";
		$LOCALE{GRID_TITLE_MODIFIED} = "更新日";
		$LOCALE{GRID_TITLE_VOLUME} = "体積";
		$LOCALE{GRID_TITLE_ORGANSYS} = "器官系";

#		$LOCALE{GRID_EMPTY_MESSAGE} = "ここに臓器アイコンをドラッグして、Anatomographyタブをクリックして下さい。\\n\\n異なるデータセット・Treeのパーツは同時に描画できません。";
#		$LOCALE{GRID_EMPTY_MESSAGE} = "ここに臓器アイコンをドラッグして、Anatomographyタブをクリックして下さい。\\n\\n異なるデータセットのパーツは同時に描画できません。";
		$LOCALE{GRID_EMPTY_MESSAGE} = "ここに臓器アイコンをドラッグして、Anatomographyタブをクリックして下さい。<br><br>異なるデータセットのパーツは同時に描画できません。";

		$LOCALE{SORTNAME_LENGTH} = 12;

#		$LOCALE{LICENSES} = qq|<table><tbody><tr><td valign="top"><a href="https://creativecommons.org/licenses/by-sa/2.1/jp/" rel="license"><img src="https://i.creativecommons.org/l/by-sa/2.1/jp/88x31.png" alt="Creative Commons License" align="left" style="padding-right:2px;"></a>アナトモグラフィーで作成した画像（アナトモグラム）ならびにアナトモグラフィーWeb APIは、 <a href="https://creativecommons.org/licenses/by-sa/2.1/jp/" rel="license">クリエイティブ・コモンズ・ライセンス</a>の下でライセンスされています。原著者ならびに許諾者は、<a title="external-link" href="http://lifesciencedb.mext.go.jp/">文部科学省委託研究開発事業「統合データベースプロジェクト」</a>です。</td></tr></tbody></table>|;
#		$LOCALE{LICENSES_WIDTH} = 214;

		$LOCALE{LICENSES} = qq|<table><tbody><tr><td valign="top"><a href="https://creativecommons.org/licenses/by-sa/2.1/jp/" rel="license"><img src="//i.creativecommons.org/l/by-sa/2.1/jp/80x15.png" alt="Creative Commons License" align="left" style="padding-right:2px;"></a>本サイトのコンテンツの標準利用許諾は、"<b>クリエイティブ・コモンズ　表示-継承2.1　日本</b>"です。<a href="info/userGuide/faq/credit.html">&gt;&gt;詳細</a></td></tr></tbody></table>|;
		$LOCALE{LICENSES_WIDTH} = 100;
		$LOCALE{LICENSES_HEIGHT} = 80;

		$LOCALE{LICENSE_EMBED} = qq|BodyParts3D &copy; ライフサイエンス統合データベースセンター licensed under <a href="https://creativecommons.org/licenses/by-sa/2.1/jp/" target="_blank">CC表示 継承2.1 日本</a>|;

		$LOCALE{LICENSE_AG} = qq|<div class="licenses-base"><div class="licenses-img"><a href="https://creativecommons.org/licenses/by-sa/2.1/jp/" rel="license"><img src="//i.creativecommons.org/l/by-sa/2.1/jp/80x15.png" alt="Creative Commons License" align="left" style="padding-right:2px;"></a></div><br><div class="licenses-msg">BodyParts3D, &copy; ライフサイエンス統合データベースセンター licensed under CC表示 継承2.1 日本</div></div>|;
		$LOCALE{GOTO_AG} = qq|<div class="goto-ag-base"><div class="goto-ag-btn"><a class="goto-ag-btn" href="#"><img src="css/goto_ag.png?1"></a></div></div>$LOCALE{LICENSE_AG}|;


		$LOCALE{MSG_NOT_DATA} = "データは存在しません";
		$LOCALE{MSG_NOT_REVIEW} = "レビューは存在しません";
		$LOCALE{MSG_LOADING_DATA} = "データ読込中 ...";

		$LOCALE{MSG_NOT_ICON} = "アイコンは存在しません";

		$LOCALE{GOTO_ICON_LIST} = "アイコンリストへ";

		$LOCALE{PASTE_TITLE} = "Paste";
		$LOCALE{PASTE_DESC_TAB} = qq|<p style="margin:0;text-align:left;font-size:12px;">最初の行にデータの項目名<br/>２行目以降にデータを入力して下さい。<br>各項目（データ）の区切りはタブを使用して下さい。</p>|;
		$LOCALE{PASTE_DESC_CSV} = qq|<p style="margin:0;text-align:left;font-size:12px;">最初の行にデータの項目名<br/>２行目以降にデータを入力して下さい。<br>各項目（データ）の区切りはカンマを使用して下さい。</p>|;
		$LOCALE{COPY_TITLE} = "Copy";

		$LOCALE{ADMIN_MENU_TITLE} = "管理";
		$LOCALE{ADMIN_MENU_ADD_TITLE} = "追加";
		$LOCALE{ADMIN_MENU_UPDATE_TITLE} = "編集";
		$LOCALE{ADMIN_MENU_DELETE_TITLE} = "削除";
		$LOCALE{ADMIN_FORM_ADD_TITLE} = "追加";
		$LOCALE{ADMIN_FORM_UPDATE_TITLE} = "編集";
		$LOCALE{ADMIN_FORM_DELETE_TITLE} = "削除";
		$LOCALE{ADMIN_FORM_DELETE_CAUSE_TITLE} = "削除理由";
		$LOCALE{ADMIN_FORM_NAME_B_TITLE} = "学名";
		$LOCALE{ADMIN_FORM_NAME_J_TITLE} = "和名";
		$LOCALE{ADMIN_FORM_NAME_E_TITLE} = "英名";
		$LOCALE{ADMIN_FORM_DETAIL_J_TITLE} = "詳細情報(日本語)";
		$LOCALE{ADMIN_FORM_DETAIL_E_TITLE} = "詳細情報(英語)";
		$LOCALE{ADMIN_FORM_SYNONYM_J_TITLE} = "シノニム(日本語)";
		$LOCALE{ADMIN_FORM_SYNONYM_E_TITLE} = "シノニム(英語)";
		$LOCALE{ADMIN_FORM_CLASSLABEL_TITLE} = "分類ラベル";
		$LOCALE{ADMIN_FORM_NAME_TITLE} = "名称";
		$LOCALE{ADMIN_FORM_KANA_TITLE} = "かな";
		$LOCALE{ADMIN_FORM_LATINA_TITLE} = "ラテン語";
		$LOCALE{ADMIN_FORM_JPN_TITLE} = "日本語";
		$LOCALE{ADMIN_FORM_ENG_TITLE} = "英語";
		$LOCALE{ADMIN_FORM_ORGAN_SYSTEM_TITLE} = "臓器系・器官系";
		$LOCALE{ADMIN_FORM_ORGAN_SYSTEM_J_TITLE} = "臓器系・器官系(日本語)";
		$LOCALE{ADMIN_FORM_ORGAN_SYSTEM_E_TITLE} = "臓器系・器官系(英語)";
		$LOCALE{ADMIN_FORM_DETAIL_TITLE} = "詳細";
		$LOCALE{ADMIN_FORM_VOLUME_TITLE} = "体積";
		$LOCALE{ADMIN_FORM_ICON_TITLE} = "アイコン";
		$LOCALE{ADMIN_FORM_REG_WAITMSG}  = "登録しています";
		$LOCALE{ADMIN_FORM_REG_OKMSG} = "登録しました";
		$LOCALE{ADMIN_FORM_REG_ERRMSG} = "登録に失敗しました";
	}else{
		$LOCALE{SEE_WHAT_YOU_CAN_GET} = "See What You can get";
		$LOCALE{SEE_WHAT_YOU_CAN_GET_URL} = "info_en/userGuide/application/index.html";
		$LOCALE{SEE_HOW_TO} = "See How to";

		$LOCALE{INFORMATION_URL} = "info_en/index.html";
		$LOCALE{LICENSE_URL} = "info_en/license/index.html";

		$LOCALE{TOP_TITLE}          = "Top Page";
		$LOCALE{TOP_WHATSNEW_TITLE} = "What\\'s New";
		$LOCALE{TREE_TYPE_1}        = "Conventional";
		$LOCALE{TREE_TYPE_2}        = "is_a";
		$LOCALE{TREE_TYPE_3}        = "is_a";
		$LOCALE{TREE_TYPE_4}        = "PartOf";

		$LOCALE{OR_MODE} = " or more";

		$LOCALE{IMAGE_POSITION}       = "Position";
		$LOCALE{IMAGE_POSITION_ROTATE} = "Rotate";
		$LOCALE{IMAGE_POSITION_FRONT} = "Front";
		$LOCALE{IMAGE_POSITION_BACK}  = "Back";
		$LOCALE{IMAGE_POSITION_LEFT}  = "Left";
		$LOCALE{IMAGE_POSITION_RIGHT} = "Right";
		$LOCALE{IMAGE_POSITION_WIDTH} = 60;
		$LOCALE{IMAGE_POSITION_LIST_WIDTH} = 60;

		$LOCALE{IMAGE_TREE_DEPTH}       = "Depth";
		$LOCALE{IMAGE_TREE_DEPTH_WIDTH} = 50;
		$LOCALE{IMAGE_TREE_DEPTH_LIST_WIDTH} = 35;

		$LOCALE{ICON_REG_MSG}    = "Registered";
		$LOCALE{ICON_UNREG_MSG}  = "Unregistered";
		$LOCALE{TREE_TITLE}      = "Taxis";
		$LOCALE{TREE_ROOT_TITLE} = "Home";
		$LOCALE{LOCALE_TITLE}    = "Japanese";
		$LOCALE{CONTENT_TITLE}   = "Choose an Image";
		$LOCALE{FILTER_TITLE}    = "Filter";
		$LOCALE{SEARCH_GRID_FILTER_YES} = "Yes";
		$LOCALE{SEARCH_GRID_FILTER_NO} = "No";

		$LOCALE{DISPTYPE_TITLE}  = "Display format";
		$LOCALE{DISPTYPE_THUMB}  = "Thumbnail";
		$LOCALE{DISPTYPE_LIST}  = "List";
		$LOCALE{DISPTYPE_TREE}   = "Tree";
		$LOCALE{DISPTYPE_WIDTH} = 75;
		$LOCALE{DISPTYPE_LIST_WIDTH} = 75;

		$LOCALE{SORT_TITLE}        = "Sort by";
		$LOCALE{SORT_TITLE_NONE}   = "None";
		$LOCALE{SORT_TITLE_NAME_J} = "Name(Jpn)";
		$LOCALE{SORT_TITLE_NAME_K} = "Name(Kana)";
		$LOCALE{SORT_TITLE_NAME_E} = "Name";
		$LOCALE{SORT_TITLE_NAME_L} = "Name(Latina)";
		$LOCALE{SORT_TITLE_VOLUME} = "Volume";
		$LOCALE{SORT_TITLE_LAST}   = "Last Modified";
		$LOCALE{SORT_WIDTH}  = 90;
		$LOCALE{SORT_LIST_WIDTH}  = 90;
		$LOCALE{DETAIL_TITLE}        = "Detail";
		$LOCALE{DETAIL_TITLE_NAME}   = "Name";
		$LOCALE{DETAIL_TITLE_BNAME}  = "Binomial name";
		$LOCALE{DETAIL_TITLE_SIZE}   = "File Size";
		$LOCALE{DETAIL_TITLE_LAST}   = "Last Modified";
		$LOCALE{DETAIL_TITLE_DETAIL} = "Detail";

		$LOCALE{DETAIL_TITLE_ICON_URL} = "Icon URL";
		$LOCALE{DETAIL_TITLE_NAME_K} = "Kana";
		$LOCALE{DETAIL_TITLE_NAME_J} = "Japanese";
		$LOCALE{DETAIL_TITLE_NAME_E} = "Name";
		$LOCALE{DETAIL_TITLE_NAME_L} = "Latina";
		$LOCALE{DETAIL_TITLE_ORGAN_SYSTEM_J} = "Organ System(Jpn)";
		$LOCALE{DETAIL_TITLE_ORGAN_SYSTEM_E} = "Organ System";
		$LOCALE{DETAIL_TITLE_SYNONYM_J} = "Synonym (Jpn)";
		$LOCALE{DETAIL_TITLE_SYNONYM_E} = "Synonym";
		$LOCALE{DETAIL_TITLE_DEFINITION_E} = "Definition";
		$LOCALE{DETAIL_TITLE_XMIN} = "Xmin";
		$LOCALE{DETAIL_TITLE_XMAX} = "Xmax";
		$LOCALE{DETAIL_TITLE_YMIN} = "Ymin";
		$LOCALE{DETAIL_TITLE_YMAX} = "Ymax";
		$LOCALE{DETAIL_TITLE_ZMIN} = "Zmin";
		$LOCALE{DETAIL_TITLE_ZMAX} = "Zmax";
		$LOCALE{DETAIL_TITLE_VOLUME} = "Volume";
		$LOCALE{DETAIL_TITLE_POINT_PARENT} = "Parent FMAID";
		$LOCALE{DETAIL_TITLE_POINT_PARENT_ID} = "Parent FMAID";
		$LOCALE{DETAIL_TITLE_POINT_PARENT_NAME} = "Parent name";
		$LOCALE{DETAIL_TITLE_POINT_CHILDREN} = "Point Element";

		$LOCALE{COMMENT_TITLE}         = "Comment";
		$LOCALE{COMMENT_TITLE_REFRESH} = "Refresh comment";
		$LOCALE{COMMENT_TITLE_PLUS}    = "Add comment";
		$LOCALE{COMMENT_TITLE_REPLY}   = "Reply";
		$LOCALE{COMMENT_TITLE_DELETE_SEL}  = "Selected comment deletion";
		$LOCALE{COMMENT_TITLE_DELETE}  = "Delete";
		$LOCALE{COMMENT_TITLE_DELETE_MSG}  = "May I delete selected comment?";
		$LOCALE{COMMENT_TITLE_DELETE_ERRMSG} = "Failed in deletion of the comment";
		$LOCALE{COMMENT_TITLE_EDIT}  = "Edit";
		$LOCALE{COMMENT_WIN_TITLE}    = "Please input comment";
		$LOCALE{COMMENT_WIN_WAITMSG}  = "Register comment";
		$LOCALE{COMMENT_WIN_TITLE_SEND}  = "Register";
		$LOCALE{COMMENT_WIN_TITLE_CANCEL} = "Cancel";
		$LOCALE{COMMENT_WIN_ADDMSG}  = "Registered comment";
		$LOCALE{COMMENT_WIN_ERRMSG}  = "Failed in registration of the comment";

		$LOCALE{FEEDBACK_TITLE_DELETE_MSG} = "May I delete [ \%s ] ?";

		$LOCALE{PAGING_REFRESH}   = "Refresh comment";
		$LOCALE{PAGING_FIRST}     = "First Page";
		$LOCALE{PAGING_LAST}      = "Last Page";
		$LOCALE{PAGING_NEXT}      = "Next Page";
		$LOCALE{PAGING_PREV}      = "Previous Page";
		$LOCALE{PAGING_DISP_MSG}  = "Displaying comment";
		$LOCALE{PAGING_EMPTY_MSG} = "No comment to display";

		$LOCALE{GRID_TITLE_NAME_J} = "Kanji";
		$LOCALE{GRID_TITLE_NAME_E} = $LOCALE{DETAIL_TITLE_NAME_E};
		$LOCALE{GRID_TITLE_NAME_K} = "Kana";
		$LOCALE{GRID_TITLE_PHASE} = "Phase";
		$LOCALE{GRID_TITLE_MODIFIED} = "Last Modified";
		$LOCALE{GRID_TITLE_VOLUME} = "Volume";
		$LOCALE{GRID_TITLE_ORGANSYS} = "Organ System";

#		$LOCALE{GRID_EMPTY_MESSAGE} = "Drag the parts above and drop in this frame. This frame is a paint pallet for anatomography.\\n\\nParts from Different Data set or Tree may not be rendered together.";
#		$LOCALE{GRID_EMPTY_MESSAGE} = "Drag the parts above and drop in this frame. This frame is a paint pallet for anatomography.\\n\\nParts from Different Data set may not be rendered together.";
		$LOCALE{GRID_EMPTY_MESSAGE} = "Drag the parts above and drop in this frame. This frame is a paint pallet for anatomography.<br><br>Parts from Different Data set may not be rendered together.";

		$LOCALE{SORTNAME_LENGTH} = 23;

#		$LOCALE{LICENSES} = qq|<table><tbody><tr><td valign="top"><a href="https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en" rel="license"><img src="https://i.creativecommons.org/l/by-sa/2.1/jp/88x31.png" alt="Creative Commons License" align="left" style="padding-right:2px;"></a>Anatomical charts that you generate (Anatomogram) and Anatomography Web API are licensed under  <a href="https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en_US" rel="license">Creative Commons Attribution-Share Alike 2.1 Japan License.</a>.The author and licenser of the contents is <a title="external-link" href="http://lifesciencedb.mext.go.jp/en/index.html">Ministry of Education, Culture, Sports, and Technology(MEXT) Integreated Database Project</a>.</td></tr></tbody></table>|,
#		$LOCALE{LICENSES_WIDTH} = 240;
		$LOCALE{LICENSES} = qq|<table><tbody><tr><td valign="top"><a href="https://creativecommons.org/licenses/by-sa/2.1/jp/" rel="license"><img src="https://i.creativecommons.org/l/by-sa/2.1/jp/80x15.png" alt="Creative Commons License" align="left" style="padding-right:2px;"></a>The Standard License for these contents is the license specified in "<b>the Creative Commons Attribution-Share Alike 2.1 Japan.<b>"<a href="https://dbarchive.lifesciencedb.jp/en/bodyparts3d/lic.html">&gt;&gt;For details</a></td></tr></tbody></table>|;
		$LOCALE{LICENSES_WIDTH} = 166;
		$LOCALE{LICENSES_HEIGHT} = 94;

		$LOCALE{LICENSE_EMBED} = qq|BodyParts3D &copy; The Database Center for Life Science licensed under <a href="https://creativecommons.org/licenses/by-sa/2.1/jp/" target="_blank">CC Attribution-Share Alike 2.1 Japan</a>|;

		$LOCALE{LICENSE_AG} = qq|<div class="licenses-base"><div class="licenses-img"><a href="https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en_US" rel="license"><img src="https://i.creativecommons.org/l/by-sa/2.1/jp/80x15.png" alt="Creative Commons License" align="left" style="padding-right:2px;"></a></div><br><div class="licenses-msg">BodyParts3D, &copy; The Database Center for Life Science licensed under CC Attribution-Share Alike 2.1 Japan</div></div>|;

		$LOCALE{GOTO_AG} = qq|<div class="goto-ag-base"><div class="goto-ag-btn"><a class="goto-ag-btn" href="#"><img src="css/goto_ag.png?1"></a></div></div>$LOCALE{LICENSE_AG}|;


		$LOCALE{MSG_NOT_DATA} = "There is no data";
		$LOCALE{MSG_NOT_REVIEW} = "There is no review";
		$LOCALE{MSG_LOADING_DATA} = "Loading data ...";

		$LOCALE{MSG_NOT_ICON} = "There is not the icon";

		$LOCALE{GOTO_ICON_LIST} = "To a list of icons";

		$LOCALE{PASTE_TITLE} = "Paste";

		$LOCALE{PASTE_DESC_TAB} = qq|<p style="margin:0;text-align:left;font-size:12px;">The first row of data item names<br/>Please enter the data after the second line.<br>Each item (data) breaks, please use the tabs.</p>|;
		$LOCALE{PASTE_DESC_CSV} = qq|<p style="margin:0;text-align:left;font-size:12px;">The first row of data item names<br/>Please enter the data after the second line.<br>Each item (data) breaks, please use a comma.</p>|;
		$LOCALE{COPY_TITLE} = "Copy";

		$LOCALE{ADMIN_MENU_TITLE} = "Admin";
		$LOCALE{ADMIN_MENU_ADD_TITLE} = "Add";
		$LOCALE{ADMIN_MENU_UPDATE_TITLE} = "Edit";
		$LOCALE{ADMIN_MENU_DELETE_TITLE} = "Delete";
		$LOCALE{ADMIN_FORM_ADD_TITLE} = "Add";
		$LOCALE{ADMIN_FORM_UPDATE_TITLE} = "Edit";
		$LOCALE{ADMIN_FORM_DELETE_TITLE} = "Delete";
		$LOCALE{ADMIN_FORM_DELETE_CAUSE_TITLE} = "Deletion reason";
		$LOCALE{ADMIN_FORM_NAME_B_TITLE} = "Scientific name";
		$LOCALE{ADMIN_FORM_NAME_J_TITLE} = "Japanese name";
		$LOCALE{ADMIN_FORM_NAME_E_TITLE} = "English name";
		$LOCALE{ADMIN_FORM_DETAIL_J_TITLE} = "Detailed information (Japanese)";
		$LOCALE{ADMIN_FORM_DETAIL_E_TITLE} = "Detailed information (English)";
		$LOCALE{ADMIN_FORM_SYNONYM_J_TITLE} = "Synonym (Japanese)";
		$LOCALE{ADMIN_FORM_SYNONYM_E_TITLE} = "Synonym (English)";
		$LOCALE{ADMIN_FORM_CLASSLABEL_TITLE} = "Classification label";
		$LOCALE{ADMIN_FORM_NAME_TITLE} = "Name";
		$LOCALE{ADMIN_FORM_KANA_TITLE} = "Kana";
		$LOCALE{ADMIN_FORM_LATINA_TITLE} = "Latina";
		$LOCALE{ADMIN_FORM_JPN_TITLE} = "Japanese";
		$LOCALE{ADMIN_FORM_ENG_TITLE} = "English";
		$LOCALE{ADMIN_FORM_ORGAN_SYSTEM_TITLE} = "Organ System";
		$LOCALE{ADMIN_FORM_ORGAN_SYSTEM_J_TITLE} = "Organ System (Japanese)";
		$LOCALE{ADMIN_FORM_ORGAN_SYSTEM_E_TITLE} = "Organ System (English)";
		$LOCALE{ADMIN_FORM_DETAIL_TITLE} = "Detail";
		$LOCALE{ADMIN_FORM_VOLUME_TITLE} = "Volume";
		$LOCALE{ADMIN_FORM_ICON_TITLE} = "Icon";
		$LOCALE{ADMIN_FORM_REG_WAITMSG} = "Register";
		$LOCALE{ADMIN_FORM_REG_OKMSG} = "Registered";
		$LOCALE{ADMIN_FORM_REG_ERRMSG} = "Failed in registration";
	}

	$LOCALE{BP3D_TITLE_HTML} = qq|<div style="position:relative;width:auto;overflow:hidden;background:#dfe8f6;padding:2px;">|;
	$LOCALE{BP3D_TITLE_HTML}.= qq|<div style="float:left;margin-right:1em;"><label style="line-height:30px;color:#15428b;font:bold 16px tahoma,arial,helvetica,sans-serif;">$LOCALE{BP3D_TITLE}</label><label style="line-height:30px;color:black;font:normal 11px tahoma,arial,helvetica,sans-serif;"> : $LOCALE{BP3D_DESCRIPTION}</label></div>|;
	$LOCALE{BP3D_TITLE_HTML}.= qq|<table border="0" cellpadding="0" cellspacing="0" class="x-btn-wrap x-btn " style="float:left;width: auto;margin-left:1em;"><tbody><tr><td class="x-btn-left"><i>&nbsp;</i></td><td class="x-btn-center"><em unselectable="on"><button class="x-btn-text" type="button" onclick="click_information_button({url:\\'$LOCALE{SEE_WHAT_YOU_CAN_GET_URL}\\'})">$LOCALE{SEE_WHAT_YOU_CAN_GET}</button></em></td><td class="x-btn-right"><i>&nbsp;</i></td></tr></tbody></table>|;
	$LOCALE{BP3D_TITLE_HTML}.= qq|<table border="0" cellpadding="0" cellspacing="0" class="x-btn-wrap x-btn " style="float:left;width: auto;margin-left:1em;"><tbody><tr><td class="x-btn-left"><i>&nbsp;</i></td><td class="x-btn-center"><em unselectable="on"><button class="x-btn-text" type="button" onclick="click_information_button({url:\\'$LOCALE{SEE_HOW_TO_URL}\\'})">$LOCALE{SEE_HOW_TO}</button></em></td><td class="x-btn-right"><i>&nbsp;</i></td></tr></tbody></table>|;
	$LOCALE{BP3D_TITLE_HTML}.= qq|</div>|;

	return %LOCALE;
}

1;
