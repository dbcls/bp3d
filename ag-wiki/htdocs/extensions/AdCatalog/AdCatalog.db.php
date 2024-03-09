<?php
#ＤＢ
class AdCatalogDB {

	private static function getDB(){
		global $wgAdCatalogDBserver,$wgAdCatalogDBport,$wgAdCatalogDBname,$wgAdCatalogDBuser,$wgAdCatalogDBpassword;
		return pg_connect("host=$wgAdCatalogDBserver port=$wgAdCatalogDBport dbname=$wgAdCatalogDBname user=$wgAdCatalogDBuser password=$wgAdCatalogDBpassword");
	}

	private static function getCTID($dbconn,$title){
		if($title->getNamespace()!=NS_MAIN) return false;
		$rtn_array = array();
		$result = pg_query_params($dbconn, 'SELECT * FROM content WHERE ct_name_j = $1', array($title->mTextform));
		if($result){
			while($row = pg_fetch_array($result, NULL, PGSQL_ASSOC)){
				$rtn = array(
					'ct_id' => null,
					'lang'  => 'ja',
					'row'   => $row
				);
				$rtn['ct_id'] = $row['ct_id'];
				$rtn_array[] = $rtn;
			}
			pg_free_result($result);
		}
		if(count($rtn_array) == 0){
			$result = pg_query_params($dbconn, 'SELECT * FROM content WHERE ct_name_e = $1', array($title->mTextform));
			if($result){
				while($row = pg_fetch_array($result, NULL, PGSQL_ASSOC)){
					$rtn = array(
						'ct_id' => null,
						'lang'  => 'en',
						'row'   => $row
					);
					$rtn['ct_id'] = $row['ct_id'];
					$rtn_array[] = $rtn;
				}
				pg_free_result($result);
			}
		}
		return $rtn_array;
	}

	private static function getMemoir($dbconn,$ct_id){
		$memoir = array();
		if(!is_null($ct_id)){
wfDebug("getMemoir()=[".gettype($ct_id)."][".$ct_id."]\n");
			$result_memoir = pg_query_params($dbconn, 'SELECT * FROM memoir WHERE ct_id = $1 order by me_id', array($ct_id));
			if($result_memoir){
				while($row_memoir = pg_fetch_array($result_memoir, NULL, PGSQL_ASSOC)){
					$row_memoir['memoirsite'] = array();
					$result_memoirsite = pg_query_params($dbconn, 'SELECT * FROM memoirsite WHERE ct_id = $1 and me_id=$2 order by ms_id', array($ct_id,$row_memoir['me_id']));
					if($result_memoirsite){
						while($row_memoirsite = pg_fetch_array($result_memoirsite, NULL, PGSQL_ASSOC)){
							$row_memoir['memoirsite'][] = $row_memoirsite;
						}
					}
					$memoir[] = $row_memoir;
				}
			}
		}
		return $memoir;
	}

	public static function articleSaveComplete(&$article, &$user, $text, $summary, $isMinor, &$isWatch, $section, &$flags, $revision, $baseRevId){

		error_reporting(E_ALL);

		wfDebug("\n\n");
		wfDebug("AdCatalogDB: articleSaveComplete()\n");
#		try{
#			wfDebug("\$article->mRevision->mText=[".strcmp($article->mContent,$article->mRevision->mText)."]\n");
#		}catch(Exception $e){}


		$openid = AdCatalogHooks::getUserUrl( $user );

#DEBUG
if(is_null($openid)){
	global $wgAdCatalogDefOpenID;
	$openid = $wgAdCatalogDefOpenID;
}


		if(is_null($openid)){
			return false;
		}

//		if(!is_null($openid) && strlen($openid)>0 && strcmp($article->mContent,$article->mRevision->mText) != 0){ //前のリビジョンとに違いがある場合
			$content_arr = explode("\n",$article->mContent);
#			wfDebug("\$article->mContent=[".$article->mContent."]\n");
#			wfDebug("\$article->mContent.count()=[".count($content_arr)."]\n");
#			wfDebug("\$article->mTitle->mTextform=[".$article->mTitle->mTextform."]\n");
#			wfDebug("json_encode(\$article)=[".json_encode($article)."]\n");


			$dbconn = AdCatalogDB::getDB();
			if($dbconn){
				$c_info_arr = AdCatalogDB::getCTID($dbconn,$article->mTitle);
				foreach($c_info_arr as $c_info){
					$ct_id = $c_info['ct_id'];
					$lang  = $c_info['lang'];
					$row_content=$c_info['row'];

					$func_args = array(
						'openid'       => $openid,
						'dbconn'       => $dbconn,
						'lang'         => $lang,
						'db_content'   => array('content'=>array($row_content)),
						'db_count'     => array(
							'content'    => 0,
							'contact'    => 0,
							'freesite'   => 0,
							'paysite'    => 0,
							'memoir'     => 0,
							'memoirsite' => array()
						),
						'wiki_content' => array()
					);

					$func_args['db_content']['contact'] = array();
					$result_contact = pg_prepare($dbconn, 'contact', 'SELECT * FROM contact WHERE ct_id = $1 order by co_id');
					if($result_contact) $result_contact = pg_execute($dbconn, 'contact', array($ct_id));
					if($result_contact){
						while($row_contact = pg_fetch_array($result_contact, NULL, PGSQL_ASSOC)){
							$func_args['db_content']['contact'][] = $row_contact;
						}
					}

					$func_args['db_content']['freesite'] = array();
					$result_freesite = pg_prepare($dbconn, 'freesite', 'SELECT * FROM freesite WHERE ct_id = $1 order by fs_id');
					if($result_freesite) $result_freesite = pg_execute($dbconn, 'freesite', array($ct_id));
					if($result_freesite){
						while($row_freesite = pg_fetch_array($result_freesite, NULL, PGSQL_ASSOC)){
							$func_args['db_content']['freesite'][] = $row_freesite;
						}
					}

					$func_args['db_content']['paysite'] = array();
					$result_paysite = pg_prepare($dbconn, 'paysite', 'SELECT * FROM paysite WHERE ct_id = $1 order by ps_id');
					if($result_paysite) $result_paysite = pg_execute($dbconn, 'paysite', array($ct_id));
					if($result_paysite){
						while($row_paysite = pg_fetch_array($result_paysite, NULL, PGSQL_ASSOC)){
							$func_args['db_content']['paysite'][] = $row_paysite;
						}
					}

					$func_args['db_content']['memoir'] = AdCatalogDB::getMemoir($dbconn,$ct_id);

					pg_query($dbconn,"BEGIN");

					$func = null;

					for($i=0;$i<count($content_arr);$i++){
						if(strcmp("{{Adcatalog/detail/about journal/$lang",$content_arr[$i]) == 0){
							$func = 'saveAboutJournal';
							$func_args['db_count']['content']++;
						}elseif(strcmp("{{Adcatalog/detail/contact information/$lang",$content_arr[$i]) == 0){
							$func = 'saveContactInformation';
							$func_args['db_count']['contact']++;
						}elseif(strcmp("{{Adcatalog/detail/free public website/$lang",$content_arr[$i]) == 0){
							$func = 'saveFreePublicWebsite';
							$func_args['db_count']['freesite']++;
						}elseif(strcmp("{{Adcatalog/detail/paid public website/$lang",$content_arr[$i]) == 0){
							$func = 'savePaidPublicWebsite';
							$func_args['db_count']['paysite']++;
						}elseif(strcmp("{{Adcatalog/detail/journal/$lang",$content_arr[$i]) == 0){
							$func = 'saveJournal';
							$func_args['db_count']['memoir']++;
							$func_args['db_count']['memoirsite'][] = 0;
						}elseif(strcmp("{{Adcatalog/detail/journal of public sites/$lang",$content_arr[$i]) == 0){
							$func = 'saveJournalOfPublicSites';
							$func_args['db_count']['memoirsite'][$func_args['db_count']['memoir']-1]++;
						}elseif(strcmp("}}",$content_arr[$i]) == 0){
							$retval = call_user_func( array('AdCatalogDB',$func), $func_args );
							wfDebug("\$retval=[$retval]\n");
							if(!$retval){
								pg_query($dbconn,"ROLLBACK");
								return false;
							}

							$func = null;
							unset($func_args['wiki_content']);
							$func_args['wiki_content'] = array();
						}else{
							$pos1 = strpos($content_arr[$i],"|");
							$pos2 = strpos($content_arr[$i],"=");
							if($pos1 !== false && $pos1 == 0 && $pos2 !== false && $pos2 >= 2){
								$key = substr($content_arr[$i],1,$pos2-1);
								$val = substr($content_arr[$i],$pos2+1);
								$val = preg_replace("/<br\s*\/*>/","\n",$val);
								$func_args['wiki_content'][$key] = $val;
							}
						}
					}
					if(count($func_args['db_content']['content'])>$func_args['db_count']['content']){
						wfDebug("\tDELETE content??\n");
						for($i=$func_args['db_count']['content'];$i<count($func_args['db_content']['content']);$i++){
							$tmp_content = array_merge($func_args['db_content']['content'][$i]);
							$tmp_content["ct_m_openid"] = $openid;
							$tmp_content["ct_modified"] = "'now()'";
							$tmp_content["ct_delcause"] = "delete from wiki";
							$fields = array();
							$params = array();
							$j = 0;
							foreach($tmp_content as $key => $val){
								if(strcmp($key,'ct_id') == 0) continue;
								$j++;
								$fields[] = "$key=$".$j;
								$params[] = $val;
							}
							$params[] = $tmp_content["ct_id"];
							$sql = 'update content set '.implode(',',$fields).' where ct_id=$'.(++$j);
							$query_res = pg_query_params($dbconn, $sql, $params);
							if($query_res===false){
								wfDebug("\tpg_last_error()=[".pg_last_error($dbconn)."]\n");
								pg_query($dbconn,"ROLLBACK");
								return false;
							}
						}
					}
					if(count($func_args['db_content']['contact'])>$func_args['db_count']['contact']){
						wfDebug("\tDELETE contact??\n");
						for($i=$func_args['db_count']['contact'];$i<count($func_args['db_content']['contact']);$i++){
							$tmp_contact = array_merge($func_args['db_content']['contact'][$i]);
							$tmp_contact["co_m_openid"] = $openid;
							$tmp_contact["co_modified"] = "'now()'";
							$tmp_contact["co_delcause"] = "delete from wiki";
							$fields = array();
							$params = array();
							$j = 0;
							foreach($tmp_contact as $key => $val){
								if(strcmp($key,'ct_id') == 0) continue;
								if(strcmp($key,'co_id') == 0) continue;
								$j++;
								$fields[] = "$key=$".$j;
								$params[] = $val;
							}
							$params[] = $tmp_contact["co_id"];
							$params[] = $tmp_contact["ct_id"];
							$sql = 'update contact set '.implode(',',$fields).' where co_id=$'.(++$j).' and ct_id=$'.(++$j);
							$query_res = pg_query_params($dbconn, $sql, $params);
							if($query_res===false){
								wfDebug("\tpg_last_error()=[".pg_last_error($dbconn)."]\n");
								pg_query($dbconn,"ROLLBACK");
								return false;
							}
						}
					}
					if(count($func_args['db_content']['freesite'])>$func_args['db_count']['freesite']){
						wfDebug("\tDELETE freesite??\n");
						for($i=$func_args['db_count']['freesite'];$i<count($func_args['db_content']['freesite']);$i++){
							$tmp_freesite = array_merge($func_args['db_content']['freesite'][$i]);
							$tmp_freesite["fs_m_openid"] = $openid;
							$tmp_freesite["fs_modified"] = "'now()'";
							$tmp_freesite["fs_delcause"] = "delete from wiki";
							$fields = array();
							$params = array();
							$j = 0;
							foreach($tmp_freesite as $key => $val){
								if(strcmp($key,'ct_id') == 0) continue;
								if(strcmp($key,'fs_id') == 0) continue;
								$j++;
								$fields[] = "$key=$".$j;
								$params[] = $val;
							}
							$params[] = $tmp_freesite["fs_id"];
							$params[] = $tmp_freesite["ct_id"];
							$sql = 'update freesite set '.implode(',',$fields).' where fs_id=$'.(++$j).' and ct_id=$'.(++$j);
							$query_res = pg_query_params($dbconn, $sql, $params);
							if($query_res===false){
								wfDebug("\tpg_last_error()=[".pg_last_error($dbconn)."]\n");
								pg_query($dbconn,"ROLLBACK");
								return false;
							}
						}
					}
					if(count($func_args['db_content']['paysite'])>$func_args['db_count']['paysite']){
						wfDebug("\tDELETE paysite??\n");
						for($i=$func_args['db_count']['paysite'];$i<count($func_args['db_content']['paysite']);$i++){
							$tmp_paysite = array_merge($func_args['db_content']['paysite'][$i]);
							$tmp_paysite["ps_m_openid"] = $openid;
							$tmp_paysite["ps_modified"] = "'now()'";
							$tmp_paysite["ps_delcause"] = "delete from wiki";
							$fields = array();
							$params = array();
							$j = 0;
							foreach($tmp_paysite as $key => $val){
								if(strcmp($key,'ct_id') == 0) continue;
								if(strcmp($key,'ps_id') == 0) continue;
								$j++;
								$fields[] = "$key=$".$j;
								$params[] = $val;
							}
							$params[] = $tmp_paysite["ps_id"];
							$params[] = $tmp_paysite["ct_id"];
							$sql = 'update paysite set '.implode(',',$fields).' where ps_id=$'.(++$j).' and ct_id=$'.(++$j);
							$query_res = pg_query_params($dbconn, $sql, $params);
							if($query_res===false){
								wfDebug("\tpg_last_error()=[".pg_last_error($dbconn)."]\n");
								pg_query($dbconn,"ROLLBACK");
								return false;
							}
						}
					}
					if(count($func_args['db_content']['memoir'])>$func_args['db_count']['memoir']){
						wfDebug("\tDELETE memoir??\n");
						for($i=$func_args['db_count']['memoir'];$i<count($func_args['db_content']['memoir']);$i++){
							$tmp_memoir = array_merge($func_args['db_content']['memoir'][$i]);
							$tmp_memoir["ps_m_openid"] = $openid;
							$tmp_memoir["ps_modified"] = "'now()'";
							$tmp_memoir["ps_delcause"] = "delete from wiki";
							$fields = array();
							$params = array();
							$j = 0;
							foreach($tmp_memoir as $key => $val){
								if(strcmp($key,'ct_id') == 0) continue;
								if(strcmp($key,'me_id') == 0) continue;
								$j++;
								$fields[] = "$key=$".$j;
								$params[] = $val;
							}
							$params[] = $tmp_memoir["me_id"];
							$params[] = $tmp_memoir["ct_id"];
							$sql = 'update memoir set '.implode(',',$fields).' where me_id=$'.(++$j).' and ct_id=$'.(++$j);
							$query_res = pg_query_params($dbconn, $sql, $params);
							if($query_res===false){
								wfDebug("\tpg_last_error()=[".pg_last_error($dbconn)."]\n");
								pg_query($dbconn,"ROLLBACK");
								return false;
							}
						}

						unset($func_args['db_content']['memoir']);
						$func_args['db_content']['memoir'] = AdCatalogDB::getMemoir($dbconn,$ct_id);
					}
					for($k=0;$k<count($func_args['db_content']['memoir']);$k++){
						$memoir = $func_args['db_content']['memoir'][$k];
						if(count($memoir['memoirsite'])>$func_args['db_count']['memoirsite'][$k]){
							wfDebug("\tDELETE memoirsite??\n");

							for($i=$func_args['db_count']['memoirsite'][$k];$i<count($memoir['memoirsite']);$i++){
								$tmp_memoirsite = array_merge($memoir['memoirsite'][$i]);
								$tmp_memoirsite["ms_m_openid"] = $openid;
								$tmp_memoirsite["ms_modified"] = "'now()'";
								$tmp_memoirsite["ms_delcause"] = "delete from wiki";
								$fields = array();
								$params = array();
								$j = 0;
								foreach($tmp_memoirsite as $key => $val){
									if(strcmp($key,'ct_id') == 0) continue;
									if(strcmp($key,'me_id') == 0) continue;
									if(strcmp($key,'ms_id') == 0) continue;
									$j++;
									$fields[] = "$key=$".$j;
									$params[] = $val;
								}
								$params[] = $tmp_memoirsite["ms_id"];
								$params[] = $tmp_memoirsite["me_id"];
								$params[] = $tmp_memoirsite["ct_id"];
								$sql = 'update memoirsite set '.implode(',',$fields).' where ms_id=$'.(++$j).' and  me_id=$'.(++$j).' and ct_id=$'.(++$j);
								$query_res = pg_query_params($dbconn, $sql, $params);
								if($query_res===false){
									wfDebug("\tpg_last_error()=[".pg_last_error($dbconn)."]\n");
									pg_query($dbconn,"ROLLBACK");
									return false;
								}
							}
						}
					}

					$query_res = pg_query($dbconn,"COMMIT");
					if($query_res===false) wfDebug("\tpg_last_error(COMMIT)=[".pg_last_error($dbconn)."]\n");
				}
				pg_close($dbconn);
			}
//		}
		wfDebug("\n\n");
		return true;
	}

	private static function saveAboutJournal(&$func_args){
		wfDebug("AdCatalogDB: saveAboutJournal():".$func_args['db_count']['content']."\n");
		if(is_null($func_args['openid'])){
			wfDebug("AdCatalogDB: saveAboutJournal(1):\$func_args['openid']=[".gettype($func_args['openid'])."]\n");
			return false;
		}
			wfDebug("AdCatalogDB: saveAboutJournal(2):\$func_args['openid']=[".gettype($func_args['openid'])."]\n");

		$dbconn = $func_args['dbconn'];
		$lang = '_' . (strcmp($func_args['lang'],'ja') == 0 ? 'j' : 'e');
		$wiki_content = $func_args['wiki_content'];

		$content_pos = $func_args['db_count']['content']-1;
		$content = $func_args['db_content']['content'][$content_pos];

		$tmp_content = array_merge($content);
		$tmp_content['ct_url'] = $wiki_content['url'] ? $wiki_content['url'] : null;
		$tmp_content["ct_abbr$lang"] = $wiki_content['abbreviation'] ? $wiki_content['abbreviation'] : null;
		$tmp_content["ct_member$lang"] = $wiki_content['member'] ? $wiki_content['member'] : null;
		$tmp_content["ct_fee$lang"] = $wiki_content['fee'] ? $wiki_content['fee'] : null;
		$tmp_content["ct_remarks$lang"] = $wiki_content['remarks'] ? $wiki_content['remarks'] : null;
		$tmp_content["ct_posses$lang"] = $wiki_content['posses'] ? $wiki_content['posses'] : null;
		$tmp_content["ct_annual_remarks$lang"] = $wiki_content['annual_remarks'] ? $wiki_content['annual_remarks'] : null;

		$tmp_content["ct_m_openid"] = $func_args['openid'];
		$tmp_content["ct_modified"] = "'now()'";

		$fields = array();
		$params = array();
		$i = 0;
		foreach($tmp_content as $key => $val){
			if(strcmp($key,'ct_id') == 0) continue;
			$i++;
			$fields[] = "$key=$".$i;
			$params[] = $val;
		}
		$params[] = $tmp_content["ct_id"];
		$sql = 'update content set ' . implode(',',$fields) . ' where ct_id=$' . (++$i);

		$query_res = pg_query_params($dbconn, $sql, $params);
		if($query_res===false) wfDebug("\tpg_last_error()=[".pg_last_error($dbconn)."]\n");

		return $query_res!==false;
	}

	private static function saveContactInformation(&$func_args){
		wfDebug("AdCatalogDB: saveContactInformation():".$func_args['db_count']['contact']."\n");

		$dbconn = $func_args['dbconn'];
		$lang = '_' . (strcmp($func_args['lang'],'ja') == 0 ? 'j' : 'e');
		$wiki_content = $func_args['wiki_content'];

		$contact_pos = $func_args['db_count']['contact']-1;
		$contact = null;
		$contact_add = false;
		if(isset($func_args['db_content']['contact'][$contact_pos])){
			$contact = $func_args['db_content']['contact'][$contact_pos];
		}else{
			$contact_add = true;

			$content_pos = $func_args['db_count']['content']-1;
			$content = $func_args['db_content']['content'][$content_pos];

			$contact = array(
				'ct_id'       => $content["ct_id"],
				'co_e_openid' => $func_args['openid'],
				'co_entry'    => "'now()'"
			);
		}

		$tmp_contact = array_merge($contact);
		$tmp_contact["co_zip$lang"] = $wiki_content['zip'] ? $wiki_content['zip'] : null;
		$tmp_contact["co_addr$lang"] = $wiki_content['addr'] ? $wiki_content['addr'] : null;
		$tmp_contact["co_tel$lang"] = $wiki_content['tel'] ? $wiki_content['tel'] : null;
		$tmp_contact["co_fax$lang"] = $wiki_content['fax'] ? $wiki_content['fax'] : null;
		$tmp_contact['co_email'] = $wiki_content['email'] ? $wiki_content['email'] : null;
		$tmp_contact["co_m_openid"] = $func_args['openid'];
		$tmp_contact["co_modified"] = "'now()'";

		if(!isset(
			$tmp_contact["co_zip_j"],
			$tmp_contact["co_addr_j"],
			$tmp_contact["co_tel_j"],
			$tmp_contact["co_fax_j"],
			$tmp_contact["co_zip_e"],
			$tmp_contact["co_addr_e"],
			$tmp_contact["co_tel_e"],
			$tmp_contact["co_fax_e"],
			$tmp_contact['co_email']
		)){
			if($contact_add) return true;
			$tmp_contact["co_delcause"] = "delete from wiki";
		}else{
			$tmp_contact["co_delcause"] = null;
		}

		$fields = array();
		$values = array();
		$params = array();
		$i = 0;
		foreach($tmp_contact as $key => $val){
			if(strcmp($key,'ct_id') == 0) continue;
			if(strcmp($key,'co_id') == 0) continue;
			$i++;
			if($contact_add){
				$fields[] = $key;
				$values[] = "$".$i;
			}else{
				$fields[] = "$key=$".$i;
			}
			$params[] = $val;
		}
		$sql = '';
		if($contact_add){
			$fields[] = 'ct_id';
			$values[] = "$".(++$i);
			$sql = 'insert into contact ('.implode(',',$fields).') values ('.implode(',',$values).')';
		}else{
			$sql = 'update contact set '.implode(',',$fields).' where co_id=$'.(++$i).' and ct_id=$'.(++$i);
			$params[] = $tmp_contact['co_id'];
		}
		$params[] = $tmp_contact['ct_id'];

		$query_res = pg_query_params($dbconn, $sql, $params);
		if($query_res===false) wfDebug("\tpg_last_error()=[".pg_last_error($dbconn)."]\n");

		return $query_res!==false;
	}

	private static function saveFreePublicWebsite(&$func_args){
		wfDebug("AdCatalogDB: saveFreePublicWebsite():".$func_args['db_count']['freesite']."\n");

		$dbconn = $func_args['dbconn'];
		$lang = '_' . (strcmp($func_args['lang'],'ja') == 0 ? 'j' : 'e');
		$wiki_content = $func_args['wiki_content'];

		$freesite_pos = $func_args['db_count']['freesite']-1;
		$freesite = null;
		$freesite_add = false;
		if(isset($func_args['db_content']['freesite'][$freesite_pos])){
			$freesite = $func_args['db_content']['freesite'][$freesite_pos];
		}else{
			$freesite_add = true;

			$content_pos = $func_args['db_count']['content']-1;
			$content = $func_args['db_content']['content'][$content_pos];

			$freesite = array(
				'ct_id'       => $content["ct_id"],
				'fs_e_openid' => $func_args['openid'],
				'fs_entry'    => "'now()'"
			);
		}

		$tmp_freesite = array_merge($freesite);
		$tmp_freesite['fs_url'] = $wiki_content['url'] ? $wiki_content['url'] : null;
		$tmp_freesite["fs_remarks$lang"] = $wiki_content['remarks'] ? $wiki_content['remarks'] : null;
		$tmp_freesite["fs_m_openid"] = $func_args['openid'];
		$tmp_freesite["fs_modified"] = "'now()'";

		if(!isset(
			$tmp_freesite["fs_url"],
			$tmp_freesite["fs_remarks_j"],
			$tmp_freesite["fs_remarks_e"]
		)){
			if($freesite_add) return true;
			$tmp_freesite["fs_delcause"] = "delete from wiki";
		}else{
			$tmp_freesite["fs_delcause"] = null;
		}

		$fields = array();
		$values = array();
		$params = array();
		$i = 0;
		foreach($tmp_freesite as $key => $val){
			if(strcmp($key,'ct_id') == 0) continue;
			if(strcmp($key,'fs_id') == 0) continue;
			$i++;
			if($freesite_add){
				$fields[] = $key;
				$values[] = "$".$i;
			}else{
				$fields[] = "$key=$".$i;
			}
			$params[] = $val;
		}
		$sql = '';
		if($freesite_add){
			$fields[] = 'ct_id';
			$values[] = "$".(++$i);
			$sql = 'insert into freesite ('.implode(',',$fields).') values ('.implode(',',$values).')';
		}else{
			$sql = 'update freesite set '.implode(',',$fields).' where fs_id=$'.(++$i).' and ct_id=$'.(++$i);
			$params[] = $tmp_freesite['fs_id'];
		}
		$params[] = $tmp_freesite['ct_id'];

		$query_res = pg_query_params($dbconn, $sql, $params);
		if($query_res===false) wfDebug("\tpg_last_error()=[".pg_last_error($dbconn)."]\n");

		return $query_res!==false;
	}

	private static function savePaidPublicWebsite(&$func_args){
		wfDebug("AdCatalogDB: savePaidPublicWebsite():".$func_args['db_count']['paysite']."\n");

		$dbconn = $func_args['dbconn'];
		$lang = '_' . (strcmp($func_args['lang'],'ja') == 0 ? 'j' : 'e');
		$wiki_content = $func_args['wiki_content'];

		$paysite_pos = $func_args['db_count']['paysite']-1;
		$paysite = null;
		$paysite_add = false;
		if(isset($func_args['db_content']['paysite'][$paysite_pos])){
			$paysite = $func_args['db_content']['paysite'][$paysite_pos];
		}else{
			$paysite_add = true;

			$content_pos = $func_args['db_count']['content']-1;
			$content = $func_args['db_content']['content'][$content_pos];

			$paysite = array(
				'ct_id'       => $content["ct_id"],
				'ps_e_openid' => $func_args['openid'],
				'ps_entry'    => "'now()'"
			);
		}

		$tmp_paysite = array_merge($paysite);
		$tmp_paysite['ps_url'] = $wiki_content['url'] ? $wiki_content['url'] : null;
		$tmp_paysite["ps_remarks$lang"] = $wiki_content['remarks'] ? $wiki_content['remarks'] : null;
		$tmp_paysite["ps_m_openid"] = $func_args['openid'];
		$tmp_paysite["ps_modified"] = "'now()'";

		if(!isset(
			$tmp_paysite["ps_url"],
			$tmp_paysite["ps_remarks_j"],
			$tmp_paysite["ps_remarks_e"]
		)){
			if($paysite_add) return true;
			$tmp_paysite["ps_delcause"] = "delete from wiki";
		}else{
			$tmp_paysite["ps_delcause"] = null;
		}

		$fields = array();
		$values = array();
		$params = array();
		$i = 0;
		foreach($tmp_paysite as $key => $val){
			if(strcmp($key,'ct_id') == 0) continue;
			if(strcmp($key,'ps_id') == 0) continue;
			$i++;
			if($paysite_add){
				$fields[] = $key;
				$values[] = "$".$i;
			}else{
				$fields[] = "$key=$".$i;
			}
			$params[] = $val;
		}
		$sql = '';
		if($paysite_add){
			$fields[] = 'ct_id';
			$values[] = "$".(++$i);
			$sql = 'insert into paysite ('.implode(',',$fields).') values ('.implode(',',$values).')';

			$paysite_ins = @pg_prepare($dbconn, $stmtname, $sql);
			if($paysite_ins===false) wfDebug("\tpg_last_error()=[".pg_last_error($dbconn)."]\n");

		}else{
			$sql = 'update paysite set '.implode(',',$fields).' where ps_id=$'.(++$i).' and ct_id=$'.(++$i);

			$paysite_upd = @pg_prepare($dbconn, $stmtname, $sql);
			if($paysite_upd===false) wfDebug("\tpg_last_error()=[".pg_last_error($dbconn)."]\n");

			$params[] = $tmp_paysite['ps_id'];
		}
		$params[] = $tmp_paysite['ct_id'];

		$query_res = pg_query_params($dbconn, $sql, $params);
		if($query_res===false) wfDebug("\tpg_last_error()=[".pg_last_error($dbconn)."]\n");

		return $query_res!==false;
	}

	private static function saveJournal(&$func_args){
		wfDebug("AdCatalogDB: saveJournal():".$func_args['db_count']['memoir']."\n");

		$dbconn = $func_args['dbconn'];
		$lang = '_' . (strcmp($func_args['lang'],'ja') == 0 ? 'j' : 'e');
		$wiki_content = $func_args['wiki_content'];

		$memoir_pos = $func_args['db_count']['memoir']-1;
		$memoir = null;
		$memoir_add = false;
		if(isset($func_args['db_content']['memoir'][$memoir_pos])){
			$memoir = $func_args['db_content']['memoir'][$memoir_pos];
		}else{
			$memoir_add = true;

			$content_pos = $func_args['db_count']['content']-1;
			$content = $func_args['db_content']['content'][$content_pos];

			$memoir = array(
				'ct_id'       => $content["ct_id"],
				'me_e_openid' => $func_args['openid'],
				'me_entry'    => "'now()'"
			);
		}
		wfDebug("\t\$memoir_add=[$memoir_add]\n");

		$tmp_memoir = array_merge($memoir);
		$tmp_memoir["me_name$lang"] = $wiki_content['name'] ? $wiki_content['name'] : null;
		$tmp_memoir['me_b_lang'] = $wiki_content['body_language'] ? $wiki_content['body_language'] : null;
		$tmp_memoir['me_a_lang'] = $wiki_content['abstract_language'] ? $wiki_content['abstract_language'] : null;
		$tmp_memoir["me_issueof$lang"] = $wiki_content['issueof'] ? $wiki_content['issueof'] : null;
		$tmp_memoir['me_url'] = $wiki_content['url'] ? $wiki_content['url'] : null;
		$tmp_memoir['me_print_issn'] = $wiki_content['print_issn'] ? $wiki_content['print_issn'] : null;
		$tmp_memoir['me_online_issn'] = $wiki_content['online_issn'] ? $wiki_content['online_issn'] : null;
		$tmp_memoir['me_periodof'] = $wiki_content['periodof'] ? $wiki_content['periodof'] : null;

		$tmp_memoir["me_m_openid"] = $func_args['openid'];
		$tmp_memoir["me_modified"] = "'now()'";

		if(!isset(
			$tmp_memoir["me_name_j"],
			$tmp_memoir["me_name_e"],
			$tmp_memoir["me_b_lang"],
			$tmp_memoir["me_a_lang"],
			$tmp_memoir["me_issueof_j"],
			$tmp_memoir["me_issueof_e"],
			$tmp_memoir["me_url"],
			$tmp_memoir["me_print_issn"],
			$tmp_memoir["me_online_issn"],
			$tmp_memoir["me_periodof"]
		)){
			if($memoir_add) return true;
			$tmp_memoir["me_delcause"] = "delete from wiki";
		}else{
			$tmp_memoir["me_delcause"] = null;
		}

		$fields = array();
		$values = array();
		$params = array();
		$i = 0;
		foreach($tmp_memoir as $key => $val){
			if(strcmp($key,'ct_id') == 0) continue;
			if(strcmp($key,'me_id') == 0) continue;
			if(strcmp($key,'memoirsite') == 0) continue;
			$i++;
			if($memoir_add){
				$fields[] = $key;
				$values[] = "$".$i;
			}else{
				$fields[] = "$key=$".$i;
			}
			$params[] = $val;
		}
		$sql = '';
		if($memoir_add){
			$fields[] = 'ct_id';
			$values[] = "$".(++$i);
			$sql = 'insert into memoir ('.implode(',',$fields).') values ('.implode(',',$values).')';
		}else{
			$sql = 'update memoir set '.implode(',',$fields).' where me_id=$'.(++$i).' and ct_id=$'.(++$i);
			$params[] = $tmp_memoir['me_id'];
		}
		$params[] = $tmp_memoir['ct_id'];

		$query_res = pg_query_params($dbconn, $sql, $params);
		if($query_res!==false && $memoir_add){
			unset($func_args['db_content']['memoir']);
			$func_args['db_content']['memoir'] = AdCatalogDB::getMemoir($dbconn,$tmp_memoir['ct_id']);
		}
		if($query_res===false) wfDebug("\tpg_last_error()=[".pg_last_error($dbconn)."]\n");

		return $query_res!==false;
	}

	private static function saveJournalOfPublicSites(&$func_args){

		$memoir_pos = $func_args['db_count']['memoir']-1;

		wfDebug("AdCatalogDB: saveJournalOfPublicSites():".$func_args['db_count']['memoirsite'][$memoir_pos]."\n");

		$dbconn = $func_args['dbconn'];
		$lang = '_' . (strcmp($func_args['lang'],'ja') == 0 ? 'j' : 'e');
		$wiki_content = $func_args['wiki_content'];

		$memoirsite_pos = $func_args['db_count']['memoirsite'][$memoir_pos]-1;

		wfDebug("\t\$memoirsite_pos=[$memoirsite_pos]\n");

		$memoir = $func_args['db_content']['memoir'][$memoir_pos];

		$memoirsite = null;
		$memoirsite_add = false;
		if(isset($memoir['memoirsite'][$memoirsite_pos])){
			$memoirsite = $memoir['memoirsite'][$memoirsite_pos];
		}else{
			$memoirsite_add = true;

			$content_pos = $func_args['db_count']['content']-1;
			$content = $func_args['db_content']['content'][$content_pos];

			$memoirsite = array(
				'ct_id'       => $content["ct_id"],
				'me_id'       => $memoir["me_id"],
				'ms_e_openid' => $func_args['openid'],
				'ms_entry'    => "'now()'"
			);
		}
		wfDebug("\t\$memoirsite_add=[$memoirsite_add]\n");

		$tmp_memoirsite = array_merge($memoirsite);
		$tmp_memoirsite['ms_url'] = $wiki_content['ms_url'] ? $wiki_content['ms_url'] : null;
		$tmp_memoirsite["ms_range$lang"] = $wiki_content['range'] ? $wiki_content['range'] : null;
		$tmp_memoirsite["ms_content$lang"] = $wiki_content['content'] ? $wiki_content['content'] : null;
		$tmp_memoirsite["ms_platform$lang"] = $wiki_content['platform'] ? $wiki_content['platform'] : null;
		$tmp_memoirsite["ms_licensed$lang"] = $wiki_content['licensed'] ? $wiki_content['licensed'] : null;
		$tmp_memoirsite["ms_remarks$lang"] = $wiki_content['remarks'] ? $wiki_content['remarks'] : null;

		$tmp_memoirsite["ms_m_openid"] = $func_args['openid'];
		$tmp_memoirsite["ms_modified"] = "'now()'";

		if(!isset(
			$tmp_memoir["ms_url"],
			$tmp_memoir["ms_range_j"],
			$tmp_memoir["ms_range_e"],
			$tmp_memoir["ms_content_j"],
			$tmp_memoir["ms_content_e"],
			$tmp_memoir["ms_platform_j"],
			$tmp_memoir["ms_platform_e"],
			$tmp_memoir["ms_licensed_j"],
			$tmp_memoir["ms_licensed_e"],
			$tmp_memoir["ms_remarks_j"],
			$tmp_memoir["ms_remarks_e"]
		)){
			if($memoirsite_add) return true;
			$tmp_memoirsite["ms_delcause"] = "delete from wiki";
		}else{
			$tmp_memoirsite["ms_delcause"] = null;
		}

		$fields = array();
		$values = array();
		$params = array();
		$i = 0;
		foreach($tmp_memoirsite as $key => $val){
			if(strcmp($key,'ct_id') == 0) continue;
			if(strcmp($key,'me_id') == 0) continue;
			if(strcmp($key,'ms_id') == 0) continue;
			$i++;
			if($memoirsite_add){
				$fields[] = $key;
				$values[] = "$".$i;
			}else{
				$fields[] = "$key=$".$i;
			}
			$params[] = $val;
		}
		$sql = '';
		if($memoirsite_add){
			$fields[] = 'me_id';
			$values[] = "$".(++$i);
			$fields[] = 'ct_id';
			$values[] = "$".(++$i);
			$sql = 'insert into memoirsite ('.implode(',',$fields).') values ('.implode(',',$values).')';
		}else{
			$sql = 'update memoirsite set '.implode(',',$fields).' where ms_id=$'.(++$i).' and me_id=$'.(++$i).' and ct_id=$'.(++$i);
			$params[] = $tmp_memoirsite['ms_id'];
		}
		$params[] = $tmp_memoirsite['me_id'];
		$params[] = $tmp_memoirsite['ct_id'];

		$query_res = pg_query_params($dbconn, $sql, $params);
		if($query_res===false) wfDebug("\tpg_last_error()=[".pg_last_error($dbconn)."]\n");

		return $query_res!==false;
	}


	public static function articleDeleteComplete(&$article, &$user, $reason, $id){
		$rtn = false;

		error_reporting(E_ALL);

		wfDebug("\n\n");
		wfDebug("AdCatalogDB: articleDeleteComplete()\n");
		wfDebug("\$article->mRevision->mText=[".strcmp($article->mContent,$article->mRevision->mText)."]\n");

		$openid = AdCatalogHooks::getUserUrl( $user );
#DEBUG
if(is_null($openid)){
	global $wgAdCatalogDefOpenID;
	$openid = $wgAdCatalogDefOpenID;
}

		if(!is_null($openid) && strlen($openid)>0){

			$dbconn = AdCatalogDB::getDB();
			if($dbconn){
				$c_info_arr = AdCatalogDB::getCTID($dbconn,$article->mTitle);
				foreach($c_info_arr as $c_info){
					$tmp_content = array();
					$tmp_content["ct_delcause"] = "delete from wiki";
					$tmp_content["ct_m_openid"] = $openid;
					$tmp_content["ct_modified"] = "'now()'";
					$fields = array();
					$params = array();
					$i = 0;
					foreach($tmp_content as $key => $val){
						if(strcmp($key,'ct_id') == 0) continue;
						$i++;
						$fields[] = "$key=$".$i;
						$params[] = $val;
					}
					$params[] = $c_info["ct_id"];
					$sql = 'update content set ' . implode(',',$fields) . ' where ct_id=$' . (++$i);
					$query_res = pg_query_params($dbconn, $sql, $params);
					if($query_res===false) wfDebug("\tpg_last_error()=[".pg_last_error($dbconn)."]\n");
					$rtn = $query_res!==false;
				}
				pg_close($dbconn);
			}
		}
		return $rtn;
	}

	public static function articleUndeleteComplete(&$article, &$user){
		$rtn = false;

		error_reporting(E_ALL);

		wfDebug("\n\n");
		wfDebug("AdCatalogDB: articleUndeleteComplete()\n");
		wfDebug("\$article->mRevision->mText=[".strcmp($article->mContent,$article->mRevision->mText)."]\n");

		$openid = AdCatalogHooks::getUserUrl( $user );
#DEBUG
if(is_null($openid)){
	global $wgAdCatalogDefOpenID;
	$openid = $wgAdCatalogDefOpenID;
}
		if(!is_null($openid) && strlen($openid)>0){

			$dbconn = AdCatalogDB::getDB();
			if($dbconn){
				$c_info_arr = AdCatalogDB::getCTID($dbconn,$article->mTitle);
				foreach($c_info_arr as $c_info){
					$tmp_content = array();
					$tmp_content["ct_delcause"] = null;
					$tmp_content["ct_m_openid"] = $openid;
					$tmp_content["ct_modified"] = "'now()'";
					$fields = array();
					$params = array();
					$i = 0;
					foreach($tmp_content as $key => $val){
						if(strcmp($key,'ct_id') == 0) continue;
						$i++;
						$fields[] = "$key=$".$i;
						$params[] = $val;
					}
					$params[] = $c_info["ct_id"];
					$sql = 'update content set ' . implode(',',$fields) . ' where ct_id=$' . (++$i);
					$query_res = pg_query_params($dbconn, $sql, $params);
					if($query_res===false) wfDebug("\tpg_last_error()=[".pg_last_error($dbconn)."]\n");
					$rtn = $query_res!==false;
				}
				pg_close($dbconn);
			}
		}
		return $rtn;
	}

	public static function titleMoveComplete(&$title, &$newtitle, &$user, $oldid, $newid){
		$rtn = false;
		error_reporting(E_ALL);

		wfDebug("\n\n");
		wfDebug("AdCatalogDB: titleMoveComplete()\n");
		wfDebug("\$title->mTextform=[".$title->mTextform."]\n");

		$openid = AdCatalogHooks::getUserUrl( $user );
#DEBUG
if(is_null($openid)){
	global $wgAdCatalogDefOpenID;
	$openid = $wgAdCatalogDefOpenID;
}
		if(!is_null($openid) && strlen($openid)>0){
			$dbconn = AdCatalogDB::getDB();
			if($dbconn){
				$c_info_arr = AdCatalogDB::getCTID($dbconn,$title);
				foreach($c_info_arr as $c_info){
					$lang = '_' . (strcmp($c_info['lang'],'ja') == 0 ? 'j' : 'e');
					$tmp_content = array();
					$tmp_content["ct_name$lang"] = $newtitle->mTextform;
					$tmp_content["ct_m_openid"] = $openid;
					$tmp_content["ct_modified"] = "'now()'";
					$fields = array();
					$params = array();
					$i = 0;
					foreach($tmp_content as $key => $val){
						if(strcmp($key,'ct_id') == 0) continue;
						$i++;
						$fields[] = "$key=$".$i;
						$params[] = $val;
					}
					$params[] = $c_info["ct_id"];
					$sql = 'update content set ' . implode(',',$fields) . ' where ct_id=$' . (++$i);
					$query_res = pg_query_params($dbconn, $sql, $params);
					if($query_res===false) wfDebug("\tpg_last_error()=[".pg_last_error($dbconn)."]\n");
					$rtn = $query_res!==false;
				}
				pg_close($dbconn);
			}
		}
		return $rtn;
	}
}
