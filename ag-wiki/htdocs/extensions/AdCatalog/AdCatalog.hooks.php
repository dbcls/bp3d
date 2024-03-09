<?php

class AdCatalogHooks {

	#SpecialOpenID::getUserUrlの仕様が1.15対応の時と違う為、この関数で吸収する
	static function getUserUrl($user) {
		$openid_url = null;
		$openid_urls = SpecialOpenID::getUserUrl( $user );
		if(!is_null($openid_urls) && is_array($openid_urls) && count($openid_urls) && strlen($openid_urls[0]) != 0){
			$openid_url = $openid_urls[0];
		}elseif(!is_null($openid_urls) && !is_array($openid_urls) && strlen($openid_urls) != 0){
			$openid_url = $openid_urls;
		}
		return $openid_url;
	}
	static function authOpenID($openid) {
		return $openid;

		if(!is_null($openid) && strlen($openid)>0){
			global $wgAdCatalogAuthOpenID;
			$ch = curl_init();
			curl_setopt($ch, CURLOPT_URL, $wgAdCatalogAuthOpenID.$openid);
			curl_setopt($ch, CURLOPT_HEADER, 0);
			curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
			$result = curl_exec($ch);
			curl_close($ch);
			if(!is_null($result) && strlen($result)>0){
				$arr = explode("\t",$result);
				if(!$arr || strcmp($arr[0],$openid) || strcmp($arr[1],"1")) $openid = null;
			}else{
				$openid = null;
			}
		}
		return $openid;
	}

	#マジックワード関連
	public static function onMagicWordMagicWords(&$magicWords){
		foreach($GLOBALS['wgCustomVariables'] as $var) $magicWords[] = "MAG_$var";
		return true;
	}
	public static function onMagicWordwgVariableIDs(&$variables){
		foreach($GLOBALS['wgCustomVariables'] as $var) $variables[] = constant("MAG_$var");
		return true;
	}
	public static function onLanguageGetMagic(&$langMagic, $langCode = 0){
		foreach($GLOBALS['wgCustomVariables'] as $var) {
			$magic = "MAG_$var";
			$langMagic[defined($magic) ? constant($magic) : $magic] = array(0,$var);
		}
		return true;
	}
	public static function onParserGetVariableValueSwitch(&$parser,&$cache,&$index,&$ret){
		switch ($index) {
 		case MAG_USER_LANGUAGE:
			global $wgLang;
			$parser->disableCache();
			$ret = $wgLang->getCode();
			break;
		}
		return true;
	}
 
	#ユーザがログインを成功した後に動作します
	public static function onUserLoginComplete(&$user, &$inject_html){
		$openid = AdCatalogHooks::getUserUrl( $user );

#DEBUG
if(is_null($openid)){
	global $wgAdCatalogDefOpenID;
	$openid = $wgAdCatalogDefOpenID;
}
		$openid = AdCatalogHooks::authOpenID($openid);
		return $openid!==null;
	}

	#一つのタイトルからページを別のものへの移動を中断することを可能にする
	public static function onAbortMove($oldtitle, $newtitle, $user, &$error, $reason){
		wfDebug("AdCatalogHooks: onAbortMove()\n");
		wfDebug("\$oldtitle=[".gettype($oldtitle)."]\n");
		wfDebug("\$newtitle=[".gettype($newtitle)."]\n");
		wfDebug("\$user=[".gettype($user)."]\n");
		wfDebug("\$error=[".gettype($error)."]\n");
		wfDebug("\$reason=[".gettype($reason)."]\n");
		wfDebug("\n");
		return true;
	}

	#記事を移動させるリクエストが完了したときはいつも動作します
	public static function onTitleMoveComplete(&$title, &$newtitle, &$user, $oldid, $newid){
		wfDebug("AdCatalogHooks: onTitleMoveComplete()\n");
		wfDebug("\$title=[".gettype($title)."]\n");
		wfDebug("\$newtitle=[".gettype($newtitle)."]\n");
		wfDebug("\$user=[".gettype($user)."]\n");
		wfDebug("\$oldid=[".gettype($oldid)."]\n");
		wfDebug("\$newid=[".gettype($newid)."]\n");
		wfDebug("\n");

		try{
//			AdCatalogDB::titleMoveComplete($title, $newtitle, $user, $oldid, $newid);
		}catch(Exception $e){
		}

		return true;
	}

	#action=editが呼び出される時はいつでも起動します
	public static function onAlternateEdit(&$editpage){
#		return true;

		wfDebug("\nAdCatalogHooks: onAlternateEdit():START\n");
		wfDebug("\$editpage=[".gettype($editpage)."]\n");
		if(is_object($editpage)){
			foreach($editpage as $key => $val){
				wfDebug("[".$key."]=[".gettype($val)."]");
				if(!is_object($val)){
					wfDebug("[".($val)."]");
					wfDebug("\n");
				}else{
					wfDebug("\n");
					foreach($val as $key2 => $val2){
						wfDebug("\t[".$key2."]=[".gettype($val2)."]");
						if(!is_object($val2)){
							wfDebug("[".($val2)."]");
						}else{
						}
						wfDebug("\n");
					}
				}
			}
		}
		wfDebug("\n");
		global $wgUser, $wgOut, $wgRequest;

		$is_sysop = false;
		$groups = $wgUser->getGroups();
		if(is_array($groups)){
			foreach($groups as $i => $val){
				if(is_string($val) && !strcmp($val,"sysop")){
					$is_sysop = true;
					break;
				}
			}
		}
		wfDebug("\$wgUser=[" .isset($wgUser) . "]\n");
		wfDebug("\$groups=[" .is_array($groups) . "]\n");
		wfDebug("\$is_sysop=[" . $is_sysop . "]\n");

		$openid = null;
		if($is_sysop){
#			wfDebug("\$wgUser=[" .$wgUser."]\n");
			$openid = AdCatalogHooks::getUserUrl( $wgUser );
			wfDebug("\$openid=[" .$openid."][" .is_null($openid)."]\n");
#DEBUG
if(is_null($openid)){
	global $wgAdCatalogDefOpenID;
	$openid = $wgAdCatalogDefOpenID;
}
			wfDebug("\$openid=[" .$openid."]\n");
			$openid = AdCatalogHooks::authOpenID($openid);
		}

		if($is_sysop && $openid!==null && strcmp($wgRequest->getText('action'),'edit') == 0 && !$wgRequest->getText('preload')){
#			$wgRequest->getRequestURL() . "&preload=Template:Adcatalog/detail/ja";

			global $wgServer, $wgArticlePath, $wgScript;
			wfDebug("\$wgServer\$wgArticlePath=[". $wgServer . $wgArticlePath . "]\n");
			wfDebug("\$wgServer\$wgScript=[". $wgServer . $wgScript . "]\n");

			$title = $wgRequest->getVal('title');

			wfDebug("\$title=[". gettype($title) . "]");
			if(is_string($title)){
				wfDebug("[". $title . "]");
			}elseif(is_object($title)){
				wfDebug("[". $title->getUrlform() . "]");
			}
			wfDebug("\n");

			$title = Title::newFromText( $title );

			wfDebug("\$title=[". gettype($title) . "]");
			if(is_string($title)){
				wfDebug("[". $title . "]");
			}elseif(is_object($title)){
				wfDebug("[". $title->{"mUrlform"} . "]");
			}
			wfDebug("\n");

			wfDebug("\$title=[". $title->getArticleID() . "]\n");
			if(isset($title) && $title->getArticleID() == 0 && $title->getNamespace()==NS_MAIN){
#				$query = "action=edit"."&preload=Template:Adcatalog/detail/ja"; //."&title=".$title->{"mUrlform"};
#				$wgOut->redirect($title->getFullURL( $query ), '301');
			}
		}
		wfDebug("AdCatalogHooks: onAlternateEdit():END\n\n");
		return $is_sysop && $openid!==null;
	}

	#MediaWikiが一つの記事を削除する一つのリクエストを受け取るときはいつも起動します
	public static function onArticleDelete(&$article, &$user, &$reason, &$error){
		wfDebug("AdCatalogHooks: onArticleDelete()\n");
		return true;
	}

	#記事削除のリクエストが終了した後で動作します
	public static function onArticleDeleteComplete(&$article, &$user, $reason, $id){
		wfDebug("AdCatalogHooks: onArticleDeleteComplete()\n");
		try{
//			AdCatalogDB::articleDeleteComplete($article, $user, $reason, $id);
		}catch(Exception $e){
		}
		return true;
	}

	#新しい記事が作成された後に動作します
	public static function onArticleInsertComplete(&$article, &$user, $text, $summary, $minoredit, &$watchthis, $sectionanchor, &$flags, $revision){
		wfDebug("AdCatalogHooks: onArticleInsertComplete()\n");
		return true;
	}

	#MediaWikiが記事を保護するリクエストを受け取る時に動作します
	public static function onArticleProtect(&$article, &$user, $protect, $reason, $moveonly){
		wfDebug("AdCatalogHooks: onArticleProtect()\n");
	}

	#MediaWikiが記事を保護するリクエストを受け取る時に動作します
	public static function onArticleProtectComplete(&$article, &$user, $protect, $reason, $moveonly){
		wfDebug("AdCatalogHooks: onArticleProtectComplete()\n");
	}

	#MediaWikiが記事を保存するリクエストを受け取るときに動作します
	public static function onArticleSave(&$article, &$user, &$text, &$summary, $isminor, &$iswatch, $section){
		wfDebug("AdCatalogHooks: onArticleSave():\$user=[".gettype($user)."]\n");
		if(!is_null($user)){
			foreach($user as $key => $val){
				wfDebug("\t\$user->[$key]=[".gettype($val)."]\n");
			}
		}
		wfDebug("AdCatalogHooks: onArticleSave():\$user->getId()=[". $user->getId() ."]\n");
		wfDebug("AdCatalogHooks: onArticleSave():\$user->getName()=[". $user->getName() ."]\n");
		wfDebug("AdCatalogHooks: onArticleSave():\$openid=[". AdCatalogHooks::getUserUrl( $user ) ."]\n");

		if(strcmp($user->getName(),'Bot')==0){
			return true;
		}

		$openid = AdCatalogHooks::getUserUrl( $user );
#DEBUG
if(is_null($openid)){
	global $wgAdCatalogDefOpenID;
	$openid = $wgAdCatalogDefOpenID;
}
		if(is_null($openid) || strlen($openid)==0) return false;
		return true;
	}

	#記事を保存するリクエストが処理された後に動作します
	public static function onArticleSaveComplete(&$article, &$user, $text, $summary, $isMinor, &$isWatch, $section, &$flags, $revision, $baseRevId){
		wfDebug("AdCatalogHooks: onArticleSaveComplete()\n");
		try{
//			AdCatalogDB::articleSaveComplete($article, $user, $text, $summary, $isMinor, $isWatch, $section, $flags, $revision, $baseRevId);
		}catch(Exception $e){
		}
		return true;
	}

	#デフォルトのタブリストが投入された後で呼び出されます(リンクは文脈依存です、すなわち"通常"の記事もしくは"特別ページ")。
	public static function onSkinTemplateContentActions(&$content_actions){
		global $wgRequest, $wgLanguageNames;
		$title = $wgRequest->getVal('title');
		$maintitle = Title::newFromText($title);
		if($maintitle->getNamespace()==NS_MAIN && isset($content_actions['edit']) && $maintitle->getArticleID() == 0){
#			wfLoadExtensionMessages('AdCatalog');//拡張機能で定義したメッセージをロード
#			unset($content_actions['edit']);	//これはアクションを削除するためのみ
#			$text = wfMsg('adcatalog-title').wfMsg('create');//.'['.$maintitle->getNamespace().']';
#			$main_action['edit-ja'] = array(
#				'class' => false or 'selected',									//タブがハイライトされる場合
#				'text'  => $text.'['.$wgLanguageNames['ja'].']',	//タブが表示するもの
#				'href'  => $maintitle->getFullURL("action=edit&preload=Template:Adcatalog/detail/ja"),   //リンクする場所
#			);
#			$main_action['edit-en'] = array(
#				'class' => false or 'selected',									//タブがハイライトされる場合
#				'text'  => $text.'['.$wgLanguageNames['en'].']',	//タブが表示するもの
#				'href'  => $maintitle->getFullURL("action=edit&preload=Template:Adcatalog/detail/en"),   //リンクする場所
#			);
#			$main_action['edit-adcatalog'] = array(
#				'class' => false or 'selected',									//タブがハイライトされる場合
#				'text'  => $text,	//タブが表示するもの
#				'href'  => $maintitle->getFullURL('#'),   //リンクする場所
#			);
#			$content_actions = array_merge( $main_action, $content_actions);	//新しいアクションを追加する


		}
		return true;
	}
#			$wgOut->setPageTitle( wfMsg( 'editing', $title ) );

	#出力ページへの最後の小さな変更、例えば、CSSもしくは拡張機能によるJavaScriptの追加などを許可します。
	public static function onBeforePageDisplay(&$out, &$sk){
		wfDebug("AdCatalogHooks: onBeforePageDisplay()\n");
		global $wgRequest,$wgScriptPath,$wgLanguageNames;
		$css_path = "${wgScriptPath}/extensions/AdCatalog/css/";
		$js_path = "${wgScriptPath}/extensions/AdCatalog/js/";
		$title = $wgRequest->getVal('title');
		$action = $wgRequest->getVal('action');
		$preload = $wgRequest->getVal('preload');
		$maintitle = Title::newFromText($title);

		wfLoadExtensionMessages('AdCatalog');//拡張機能で定義したメッセージをロード
		$default_title = wfMsg('create');

		$bodyparts3d_title = 'FMA Template';

		$en = $wgLanguageNames['en'];
		$ja = $wgLanguageNames['ja'];
		$default_href = $maintitle->getFullURL("action=edit");


		$bodyparts3d_href = $maintitle->getFullURL("action=edit&preload=Template:BodyParts3D/Create");

		global $wgLang;
		$code = $wgLang->getCode();

		$editmode = 'false';
		if($maintitle->getNamespace()==NS_MAIN && $maintitle->getArticleID() == 0){
			$editmode = 'true';
			//ページ内のタイトルを修正
			if(!is_null($action) && $action=='edit' && !is_null($preload)){
				if(strpos($preload, 'Template:BodyParts3D')!==false){
					$out->setPageTitle( wfMsg( 'editing', $title ) . ' - ' . ($code=='ja'?'「':'[ ') . $bodyparts3d_title . ($code=='ja'?'」':' ]'));
				}
			}
		}

		$script = <<<END
<link rel="stylesheet" href="${css_path}style.css" media="screen" charset="UTF-8" />
<script type="text/javascript" src="${js_path}jquery.min.js"></script>
<script type="text/javascript">
var bitsAdCatalog = {
	init : function(e){
		bitsAdCatalog.hideControl(e);
		if($editmode) bitsAdCatalog.createCatalogMenu(e);
	},

	hideControl : function(){
		var \$img = $('table.fma_thumbnail>tbody>tr>td:eq(1)>p img');
		\$img.eq(0).attr('alt','Rotate');
		\$img.eq(1).attr('alt','Front');
		\$img.eq(2).attr('alt','Left');
		\$img.eq(3).attr('alt','Back');
		\$img.eq(4).attr('alt','Right');
		\$img.css({
			width: '120px',
			height: '120px',
		});

		if(window==window.top) return;

		\$img.bind('abort',function(){
//			console.log('abort!!['+this.src+']');
		}).bind('error',function(){
//			console.log('error!!['+this.src+']');
			$(this).css({
				width: 'auto',
				height: 'auto',
			});
		});


		$('globalWrapper').hide();

		$('#content').css({
			'margin-left':'0.4em',
			'margin-top' :'20px',
			'font-size' :'0.8em'
		});
		$('#p-logo').hide();
		$('#p-personal').hide();
		$('#p-navigation').hide();
		$('#p-tb').hide();
		$('#p-search').hide();
		$('#p-lang').hide();
		$('#p-cactions').css({
			'left':'0px',
			'top' :'0px'
		});
		$('#p-cactions').find('ul').css({'margin-left':'0px'});
		$('#ca-nstab-main').hide();
		$('#ca-nstab-image').hide();
		$('#ca-talk').hide();
		$('#ca-viewsource').hide();
		$('#ca-history').hide();
		$('#footer').hide();
		$('#pt-anonuserpage').hide();
		$('#pt-anontalk').hide();

		setTimeout(function(){

			/*サムネイルの表示設定*/
			var hash = window.location.hash.substr(1);
			var fma_thumbnail;
			var thumbnail_tree;
			var thumbnail_version;
			if(hash.match(/fma_thumbnail=([A-Za-z0\|]+)/)) fma_thumbnail = RegExp.\$1;
			if(hash.match(/thumbnail_tree=(conventional|bp3d|is_a|isa|part_of|partof)/)) thumbnail_tree = RegExp.\$1;
			if(hash.match(/thumbnail_version=([0-9][0-9\.]+[0-9])/)) thumbnail_version = RegExp.\$1;
			if(thumbnail_version) thumbnail_version = encodeURIComponent(thumbnail_version);
			if(fma_thumbnail || thumbnail_tree || thumbnail_version){
				if(!thumbnail_version) thumbnail_version = '';

				\$img.hide();
//				console.log("$title");
//				console.log(fma_thumbnail);
//				console.log(thumbnail_tree);
//				console.log(\$img.length);
				setTimeout(function(){
					if(fma_thumbnail){
						\$img.hide().each(function(){
							if(thumbnail_tree){
								$(this).attr('src',$(this).attr('src').replace(/(t=)(conventional|bp3d|is_a|isa|part_of|partof:?)/,"$1"+thumbnail_tree+'&v='+thumbnail_version));
							}else{
								return false;
							}
						});
						if(fma_thumbnail.match(/Rotate/i)){
							\$img.eq(0).show();
						}
						if(fma_thumbnail.match(/Front/i)){
							\$img.eq(1).show();
						}
						if(fma_thumbnail.match(/Left/i)){
							\$img.eq(2).show();
						}
						if(fma_thumbnail.match(/Back/i)){
							\$img.eq(3).show();
						}
						if(fma_thumbnail.match(/Right/i)){
							\$img.eq(4).show();
						}
					}else{
						\$img.each(function(){
							if(thumbnail_tree){
								$(this).attr('src',$(this).attr('src').replace(/(t=)(conventional|bp3d|is_a|isa|part_of|partof:?)/,"$1"+thumbnail_tree+'&v='+thumbnail_version));
							}else{
								return false;
							}
						}).show();
					}
				},250);
			}


			$('globalWrapper').show();
		},250);
	},

	createCatalogMenu : function(e){
		var elem = $('li#ca-edit');
		if(elem.length==0) return;
		var a = elem.children('a');
		if(a.length==0) return;
		elem.css({'position':'relative'});
		a.css({'background':'transparent url("${js_path}btn-arrow.gif") no-repeat scroll right 0pt'});
		var ul = elem.find('ul');
		if(ul.length==0){
			ul = $('<ul>');
			ul.addClass('ca-edit-child');
			ul.css({
				'display':'none',
				'position':'absolute',
				'margin':'0px',
				'z-index':'60000'
			});
			elem.append(ul);
		}
		a.bind('click mouseover',function(e){
			var target = $(e.target);
			var position = target.position();
			var height = target.height();
			var ul = $('ul.ca-edit-child');
			ul.css({
				left : position.left + 'px',
				top  : (position.top+height) + 'px'
			});
			ul.show();
			e.stopPropagation();
			return false;
		});
		$(window).bind('click',function(e){
			if(e.button!=0) return;
			$('ul.ca-edit-child').hide();
			$('ul.ca-edit-child ul').hide();
		});

		this.createCatalogSubMenu(e,{parent:ul,href:"${default_href}",text:"${default_title}",children:null});

		this.createCatalogSubMenu(e,{parent:ul,href:"${bodyparts3d_href}",text:"${bodyparts3d_title}",children:null});

	},

	createCatalogSubMenu : function(e,param){
		var ul = param.parent;
		if(!ul || ul.length==0) return;
		var li = $('<li>');
		li.addClass('ca-edit-child-li');
		li.css({
			'display':'block',
			'font-weight':'normal'
		});
		ul.append(li);

		var a = $('<a>');
		a.attr({'href':param.href?param.href:'#'});
		a.css({'text-transform':'none'});
		if(param.text) a.text(param.text);
		li.append(a);
		if(a.attr('href')=='#'){
			a.css({
				'background':'transparent url("${js_path}more.gif") no-repeat scroll right 0pt'
			});
			a.bind('click mouseover',function(e){
				$('ul.ca-edit-child ul').hide();
				var parent = $(this).parent();
				var ul = parent.children('ul');
				var position = parent.position();
				var width = parent.width();
				ul.css({
					left : (position.left+width) + 'px',
					top  : (position.top) + 'px'
				});
				ul.show();
				e.stopPropagation();
				return false;
			});
		}

		if(!param.children) return;
		var ul = li.children('ul');
		if(ul.length==0){
			ul = $('<ul>');
			ul.css({
				'display':'none',
				'position':'absolute',
				'margin':'0px',
				'z-index':'60000'
			});
			li.append(ul);
		}
		var children;
		if(param.children instanceof Array){
			children = param.children;
		}else{
			children = [param.children];
		}
		for(var i=0;i<children.length;i++){
			this.createCatalogSubMenu(e,{
				parent   : ul,
				href     : children[i].href,
				text     : children[i].text,
				children : children[i].children
			});
		}
	}
};
$(document).ready(function(e){
	bitsAdCatalog.init(e);
});
</script>
END;
		$out->addScript($script);
		return true;
	}

	#ページがレンダーされた後でHTMLが表示される前に呼び出されます。(編集時にはコールされない？)
	public static function onOutputPageBeforeHTML(&$out, &$text){
		wfDebug("AdCatalogHooks: onOutputPageBeforeHTML()\n");
//		if(!is_null($out)){
//			foreach($out as $key => $val){
//				wfDebug("\t\$out->[$key]=[".gettype($val)."][".$val."]\n");
//			}
//		}
//		if(!is_null($text)){
//			foreach($text as $key => $val){
//				wfDebug("\t\$text->[$key]=[".gettype($val)."][".$val."]\n");
//			}
//		}



		return true;
	}

	public static function onArticleAfterFetchContent(&$article, &$content){
		wfDebug("AdCatalogHooks: onArticleAfterFetchContent()\n");
		return true;
	}
	public static function onArticleEditUpdateNewTalk(&$article){
		wfDebug("AdCatalogHooks: onArticleEditUpdateNewTalk()\n");
		return true;
	}
	public static function onArticleEditUpdates(&$article, &$editInfo, $changed){
		wfDebug("AdCatalogHooks: onArticleEditUpdates()\n");
		return true;
	}
	#復帰の時にコールされる？
	public static function onArticleEditUpdatesDeleteFromRecentchanges(&$article){
		wfDebug("\n");
		wfDebug("AdCatalogHooks: onArticleEditUpdatesDeleteFromRecentchanges()\n");

		global $wgRequest,$wgUser;
		$title = $wgRequest->getVal('title');
		$action = $wgRequest->getVal('action');

		wfDebug("\$title=[".gettype($title)."][".($title)."]\n");
		wfDebug("\$action=[".gettype($action)."][".($action)."]\n");

		$maintitle = Title::newFromText($title);
		if(!is_null($maintitle)){
			if($maintitle->getNamespace()==NS_SPECIAL && strcmp($maintitle->getDBkey(),'Undelete')==0){
				wfDebug("getNamespace()=[".$maintitle->getNamespace()."]\n");
				wfDebug("getDBkey()=[".$maintitle->getDBkey()."]\n");
				wfDebug("\$article->mTitle->mTextform=[".$article->mTitle->mTextform."]\n");

				try{
//					AdCatalogDB::articleUndeleteComplete($article,$wgUser);
				}catch(Exception $e){
				}
			}
		}

		wfDebug("\n");
		wfDebug("\n");

		return true;
	}
	#記事がDBから読み取る前にコールされる（DBのフィールドの変更）
	public static function onArticlePageDataBefore(&$article, &$fields){
#		wfDebug("AdCatalogHooks: onArticlePageDataBefore()\n");
		return true;
	}
	#記事をDBから読み込んだ後にコールされる
	public static function onArticlePageDataAfter(&$article, &$row){
		wfDebug("AdCatalogHooks: onArticlePageDataAfter()\n");

		if(is_object($row) || is_array($row)){
			foreach($row as $key => $val){
				wfDebug("[".$key."]=[".gettype($val)."]");
				if(!is_object($val) && !is_array($val)){
					wfDebug("[".($val)."]");
					wfDebug("\n");
				}else{
					wfDebug("\n");
					foreach($val as $key2 => $val2){
						wfDebug("\t[".$key2."]=[".gettype($val2)."]");
						if(!is_object($val2)){
							wfDebug("[".($val2)."]");
						}else{
						}
						wfDebug("\n");
					}
				}
			}
		}

		return true;
	}
	public static function onArticlePurge(&$article){
		wfDebug("AdCatalogHooks: onArticlePurge()\n");
		return true;
	}
	public static function onArticleRollbackComplete(&$article, $user, $target, $current){
		wfDebug("AdCatalogHooks: onArticleRollbackComplete()\n");
		return true;
	}
	public static function onArticleUpdateBeforeRedirect(&$article, &$sectionanchor, &$extraQuery){
		wfDebug("AdCatalogHooks: onArticleUpdateBeforeRedirect()\n");
		return true;
	}
	public static function onArticleViewRedirect(&$article){
		wfDebug("AdCatalogHooks: onArticleViewRedirect()\n");
		return true;
	}
	#記事のヘッダが表示された後に呼び出されます
	public static function onArticleViewHeader(&$article, &$outputDone, &$pcache){
		wfDebug("AdCatalogHooks: onArticleViewHeader()\n");

		wfDebug("\$outputDone\n");
		if(is_object($outputDone) || is_array($outputDone)){
			foreach($outputDone as $key => $val){
				wfDebug("[".$key."]=[".gettype($val)."]");
				if(!is_object($val) && !is_array($val)){
					wfDebug("[".($val)."]");
					wfDebug("\n");
				}else{
					wfDebug("\n");
					foreach($val as $key2 => $val2){
						wfDebug("\t[".$key2."]=[".gettype($val2)."]");
						if(!is_object($val2)){
							wfDebug("[".($val2)."]");
						}else{
						}
						wfDebug("\n");
					}
				}
			}
		}else{
			wfDebug("\t[$outputDone]\n");
		}
		wfDebug("\n");

		wfDebug("\$pcache\n");
		if(is_object($pcache) || is_array($pcache)){
			foreach($pcache as $key => $val){
				wfDebug("[".$key."]=[".gettype($val)."]");
				if(!is_object($val) && !is_array($val)){
					wfDebug("[".($val)."]");
					wfDebug("\n");
				}else{
					wfDebug("\n");
					foreach($val as $key2 => $val2){
						wfDebug("\t[".$key2."]=[".gettype($val2)."]");
						if(!is_object($val2)){
							wfDebug("[".($val2)."]");
						}else{
						}
						wfDebug("\n");
					}
				}
			}
		}else{
			wfDebug("\t[$pcache]\n");
		}
		wfDebug("\n");

		wfDebug("\$article\n");
		if(is_object($article) || is_array($article)){
			foreach($article as $key => $val){
				wfDebug("[".$key."]=[".gettype($val)."]");
				if(!is_object($val) && !is_array($val)){
					wfDebug("[".($val)."]");
					wfDebug("\n");
				}else{
					wfDebug("\n");
					foreach($val as $key2 => $val2){
						wfDebug("\t[".$key2."]=[".gettype($val2)."]");
						if(!is_object($val2)){
							wfDebug("[".($val2)."]");
						}else{
						}
						wfDebug("\n");
					}
				}
			}
		}else{
			wfDebug("\t[$article]\n");
		}
		wfDebug("\n");

		return true;
	}
	public static function onDisplayOldSubtitle(&$article, &$oldid){
		wfDebug("AdCatalogHooks: onDisplayOldSubtitle()\n");
		return true;
	}
	public static function onIsFileCacheable(&$article){
		wfDebug("AdCatalogHooks: onIsFileCacheable()\n");
		return true;
	}
	public static function onNewRevisionFromEditComplete(&$article, $revision, $bool, $user){
		wfDebug("AdCatalogHooks: onNewRevisionFromEditComplete()\n");
		return true;
	}
	public static function onShowRawCssJs($content, $title, $out){
		wfDebug("AdCatalogHooks: onShowRawCssJs()\n");
		return true;
	}
	public static function onUnwatchArticle(&$user, &$article){
		wfDebug("AdCatalogHooks: onUnwatchArticle()\n");
		return true;
	}
	public static function onUnwatchArticleComplete(&$user, &$article){
		wfDebug("AdCatalogHooks: onUnwatchArticleComplete()\n");
		return true;
	}
	public static function onWatchArticle(&$user, &$article){
		wfDebug("AdCatalogHooks: onWatchArticle()\n");
		return true;
	}
	public static function onWatchArticleComplete(&$user, &$article){
		wfDebug("AdCatalogHooks: onWatchArticleComplete()\n");
		return true;
	}

}
