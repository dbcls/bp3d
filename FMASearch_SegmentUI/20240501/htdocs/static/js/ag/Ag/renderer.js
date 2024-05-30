var EventSource = window.EventSource || window.MozEventSource;
var useEventSource = false;
//if(EventSource) useEventSource = true;

var openAgRender = function(urlHashStr){
	return false;
};

Ext.define('AgApp', {
	mixins: {
		observable: 'Ext.util.Observable'
	},
	constructor: function (config) {


		var self = this;
		self._config = config || {};

		self.IS_ELECTRON = (window.navigator.appVersion && window.navigator.appVersion.match(/\sElectron\//) ? true : false)  || true;

		self.DEF_LOCALDB_RENDERER_OPTIONS_KEY = AgDef.LOCALDB_PREFIX+'fma-search-renderer-options';

		self.DEF_LOCALDB_PROVIDER_PREFIX = AgDef.LOCALDB_PREFIX+'bp3d-mng-';

		self.event_namespace = '.main';
		self.AgLocalStorage = new AgLocalStorage();

		self.FORMAT_FULL_FLOAT_NUMBER = '0,0.0000';
		self.FORMAT_FLOAT_NUMBER = '0,0.00';
		self.FORMAT_INT_NUMBER = '0,0';
		self.FORMAT_RATE_NUMBER = '0.00';
		self.FORMAT_DATE = 'Y/m/d';
		self.FORMAT_TIME = 'H:i:s';
		self.FORMAT_DATE_TIME = self.FORMAT_DATE+' '+self.FORMAT_TIME;
		self.FORMAT_ID_NUMBER = '0';

		self.FORMAT_RELATIONS_PANEL_ID = '{0}_{1}';
		self.FORMAT_FORM_FIELD_ID = '{0}-{1}';

		self.DEF_MODEL_TERM = AgDef.DEF_MODEL_TERM;	//'BodyParts3D';
		self.DEF_MODEL_VERSION_TERM = AgDef.DEF_MODEL_VERSION_TERM;	//'20161017i4';
		self.DEF_MODEL_VERSION_RECORD = null;
		self.DEF_MODEL_VERSION_VALUE = null;

		self.DEF_CONCEPT_INFO_TERM = AgDef.DEF_CONCEPT_INFO_TERM;	//'FMA';
		self.DEF_CONCEPT_BUILD_TERM = AgDef.DEF_CONCEPT_BUILD_TERM;	//'4.3.0-inference';

		self.DEF_CONCEPT_INFO_VALUE = null;
		self.DEF_CONCEPT_BUILD_VALUE = null;

		self.DEF_LOCATION_HASH_EXTENDHIERARCHY_KEY = 'extendHierarchy';

		self.DEF_ID_LABEL = AgDef.LOCATION_HASH_ID_KEY;
		self.DEF_ID_FORM_LABEL_WIDTH = 10;
		self.DEF_ID_FORM_FIELD_WIDTH = 92;
		self.DEF_ID_FORM_FIELD_XTYPE = 'textfield';
		self.DEF_ID_FORM_FIELD_VTYPE = 'fmaid';
		self.DEF_ID_FORM_FIELD_ID = Ext.util.Format.format(self.FORMAT_FORM_FIELD_ID,self.DEF_ID_FORM_FIELD_XTYPE,self.DEF_ID_LABEL);
		self.DEF_ID_COLUMN_WIDTH = 95;

		self.DEF_NAME_LABEL = AgDef.LOCATION_HASH_NAME_KEY;
		self.DEF_NAME_FORM_LABEL_WIDTH = 32;
		self.DEF_NAME_FORM_FIELD_WIDTH = 228;
		self.DEF_NAME_FORM_FIELD_XTYPE = 'textfield';
		self.DEF_NAME_FORM_FIELD_VTYPE = 'fmaname';
		self.DEF_NAME_FORM_FIELD_ID = Ext.util.Format.format(self.FORMAT_FORM_FIELD_ID,self.DEF_NAME_FORM_FIELD_XTYPE,self.DEF_NAME_LABEL);

		self.DEF_SYNONYM_LABEL = 'synonym';

		self.DEF_DEFINITION_LABEL = 'definition';

		self.DEF_COLOR_LABEL = 'color';
		self.DEF_COLOR_COLUMN_WIDTH = 52;

		self.DEF_VIEW_DOCITEMS_HIDDEN = self.IS_ELECTRON;

		self.DEF_FILENAME_LABEL = 'filename';

		self.DEF_CONCEPT_LABEL = 'Concept';
		self.DEF_CONCEPT_FORM_LABEL_WIDTH = 48;
		self.DEF_CONCEPT_INFO_FORM_FIELD_WIDTH = 74;
		self.DEF_CONCEPT_INFO_FORM_FIELD_XTYPE = 'combobox';
		self.DEF_CONCEPT_INFO_FORM_FIELD_ID = Ext.util.Format.format(self.FORMAT_FORM_FIELD_ID,self.DEF_CONCEPT_INFO_FORM_FIELD_XTYPE,'concept-info');

		self.DEF_CONCEPT_BUILD_FORM_FIELD_WIDTH = 256;
		self.DEF_CONCEPT_BUILD_FORM_FIELD_XTYPE = 'combobox';
		self.DEF_CONCEPT_BUILD_FORM_FIELD_ID = Ext.util.Format.format(self.FORMAT_FORM_FIELD_ID,self.DEF_CONCEPT_BUILD_FORM_FIELD_XTYPE,'concept-build');

		self.DEF_SEARCH_LABEL = 'Search';
		self.DEF_SEARCH_FORM_FIELD_XTYPE = 'combobox';
		self.DEF_SEARCH_FORM_FIELD_VTYPE = 'fmasearch';
		self.DEF_SEARCH_FORM_FIELD_ID = Ext.util.Format.format(self.FORMAT_FORM_FIELD_ID,self.DEF_SEARCH_FORM_FIELD_XTYPE,AgDef.LOCATION_HASH_SEARCH_KEY);
		self.DEF_SEARCH_FORM_FIELD_WIDTH = 310;
		self.DEF_SEARCH_FORM_FIELD_LIST_WIDTH = 310;

		self.DEF_SEARCH_EXCLUDE_LABEL = 'Not (OR)';
		self.DEF_SEARCH_EXCLUDE_FORM_FIELD_XTYPE = 'textfield';
		self.DEF_SEARCH_EXCLUDE_FORM_FIELD_ID = Ext.util.Format.format(self.FORMAT_FORM_FIELD_ID,self.DEF_SEARCH_EXCLUDE_FORM_FIELD_XTYPE,AgDef.LOCATION_HASH_SEARCH_EXCLUDE_KEY);

		self.DEF_SEARCH_TARGET_ELEMENT_XTYPE = 'button';
		self.DEF_SEARCH_TARGET_ELEMENT_ID = Ext.util.Format.format(self.FORMAT_FORM_FIELD_ID,self.DEF_SEARCH_TARGET_ELEMENT_XTYPE,'element');
		self.DEF_SEARCH_TARGET_ELEMENT_LABEL = 'Element';

		self.DEF_SEARCH_TARGET_WHOLE_XTYPE = 'button';
		self.DEF_SEARCH_TARGET_WHOLE_ID = Ext.util.Format.format(self.FORMAT_FORM_FIELD_ID,self.DEF_SEARCH_TARGET_WHOLE_XTYPE,'whole');
		self.DEF_SEARCH_TARGET_WHOLE_LABEL = 'Whole';

		self.DEF_SEARCH_TARGET_CHECKED_ID = self.DEF_SEARCH_TARGET_WHOLE_ID;


		self.DEF_SEARCH_ANY_MATCH_ID = 'search-anymatch-checkboxfield';
		self.DEF_SEARCH_ANY_MATCH_LABEL = 'partialMatch';

		self.DEF_SEARCH_CASE_SENSITIVE_ID = 'search-casesensitive-checkboxfield';
		self.DEF_SEARCH_CASE_SENSITIVE_LABEL = 'caseSensitive';

		self.DEF_SEARCH_RESULT_LIST_LABEL = '検索結果（リスト）';
		self.DEF_SEARCH_RESULT_LIST_ID = 'search-result-list-gridpanel';
		self.DEF_SEARCH_RESULT_LIST_PLUGIN_ID = self.DEF_SEARCH_RESULT_LIST_ID+'-bufferedrenderer';
		self.DEF_SEARCH_RESULT_LIST_HIDDEN = self.IS_ELECTRON;

		self.DEF_SEARCH_RESULT_RENDERING_IMAGE_LABEL = '検索結果（レンダリングイメージ）';
		self.DEF_SEARCH_RESULT_RENDERING_IMAGE_ID = 'search-result-rendering-image-panel';
		self.DEF_SEARCH_RESULT_RENDERING_IMAGE_SHOW_HEADER = self.IS_ELECTRON ? false : true;

		self.DEF_SEARCH_RESULT_RENDERING_OPTION_BUTTIN_HIDDEN = self.IS_ELECTRON;


		self.DEF_SELECTION_RENDERER_PICKED_COLOR = '#FF00FF';
		self.DEF_SELECTION_RENDERER_PICKED_COLOR_FACTOR = 0.5;
		self.DEF_SELECTION_RENDERER_PICKED_OTHER_OPACITY = 0.5;
		self.DEF_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR = -0.8;

		self.USE_SELECTION_RENDERER_PICKED_COLOR = false;
		self.USE_SELECTION_RENDERER_PICKED_COLOR_FACTOR = false;
		self.USE_SELECTION_RENDERER_PICKED_OTHER_OPACITY = true;
		self.USE_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR = false;

		self.DEF_RENDERER_BACKGROUND_COLOR = '#FFFFFF';
		self.USE_SELECTION_RENDERER_BACKGROUND_COLOR_FACTOR = false;
		self.DEF_SELECTION_RENDERER_BACKGROUND_COLOR_FACTOR = -0.1;
		self.DEF_SELECTION_RENDERER_BACKGROUND_COLOR = self.DEF_RENDERER_BACKGROUND_COLOR;

		if(self.DEF_SELECTION_RENDERER_BACKGROUND_COLOR_FACTOR>0){
			var rgb = d3.rgb( self.DEF_RENDERER_BACKGROUND_COLOR );
			self.DEF_SELECTION_RENDERER_BACKGROUND_COLOR = rgb.brighter(self.DEF_SELECTION_RENDERER_BACKGROUND_COLOR_FACTOR).toString();
		}
		else if(self.DEF_SELECTION_RENDERER_BACKGROUND_COLOR_FACTOR<0){
			var rgb = d3.rgb( self.DEF_RENDERER_BACKGROUND_COLOR );
			self.DEF_SELECTION_RENDERER_BACKGROUND_COLOR = rgb.darker(self.DEF_SELECTION_RENDERER_BACKGROUND_COLOR_FACTOR*-1).toString();
		}

		self.DEF_DOUBLE_CLICK_INTERVAL = 250;

		self.init();
	},

	getLocationHash : function(){
		var self = this;
//		var hash = Ext.Object.fromQueryString(window.location.hash.substr(1)) || {};
		var hash = Ext.JSON.decode( window.decodeURIComponent( window.location.hash.substr(1)) || '{}');
		console.log(hash);

//		console.log(ag_extensions.toJSON.defaults.Common());

		var merge_hash = {};
		merge_hash.Common = Ext.apply({},hash.Common || {},ag_extensions.toJSON.defaults.Common());
		merge_hash.Window = Ext.apply({},hash.Window || {},ag_extensions.toJSON.defaults.Window());
		merge_hash.Camera = Ext.apply({},hash.Camera || {},ag_extensions.toJSON.defaults.Camera());
		merge_hash.Legend = Ext.apply({},hash.Legend || {},ag_extensions.toJSON.defaults.Legend());
/*
		if(Ext.isArray(hash.Part)){
			merge_hash.Part = [];
			Ext.each(hash.Part,function(Part){
				merge_hash.Part.push(Ext.apply({},Part || {},ag_extensions.toJSON.defaults.Part()));
			});
		}
*/
		if(Ext.isArray(hash.Pin)){
			merge_hash.Pin = [];
			Ext.each(hash.Pin,function(Pin){
				merge_hash.Pin.push(Ext.apply({},Pin || {},ag_extensions.toJSON.defaults.Pin()));
			});
		}
		console.log(merge_hash);

		console.log(merge_hash.Common.Version);


		if(Ext.isObject(Ag.data.renderer) && Ext.isObject(Ag.data.renderer[merge_hash.Common.Version])){
			var renderer_data = Ag.data.renderer[merge_hash.Common.Version];
			var fma_datas = renderer_data.datas;
			if(Ext.isArray(hash.Part)){
				var PartDatas = [];
				Ext.each(hash.Part,function(Part){
					var part = Ext.apply({},Part || {},ag_extensions.toJSON.defaults.Part());

					var PartData;
					if(Ext.isString(part.PartID) && part.PartID.length){
						PartData = Ext.apply({},fma_datas[Part.PartID],part);
					}
					else if(Ext.isString(part.PartName) && part.PartName.length){
						PartData = Ext.apply({},fma_datas[fma_datas[part.PartName.toLowerCase()]],part);
					}
					if(Ext.isObject(PartData)) PartDatas.push(PartData);
					console.log(Part,PartData);
				});
				if(PartDatas.length){
					if(PartDatas.length>1){
						PartDatas = PartDatas.sort(function(a,b){ return b[AgDef.BUILDUP_TREE_DEPTH_FIELD_ID] - a[AgDef.BUILDUP_TREE_DEPTH_FIELD_ID];});
					}
					var records = [];
					var art_datas = {};

					merge_hash.Part = [];

					var version_data = {};
					version_data[AgDef.MODEL_DATA_FIELD_ID] = renderer_data[AgDef.MODEL_DATA_FIELD_ID];
					version_data[AgDef.MODEL_VERSION_DATA_FIELD_ID] = renderer_data[AgDef.MODEL_VERSION_DATA_FIELD_ID];
					version_data[AgDef.CONCEPT_INFO_DATA_FIELD_ID] = renderer_data[AgDef.CONCEPT_INFO_DATA_FIELD_ID];
					version_data[AgDef.CONCEPT_BUILD_DATA_FIELD_ID] = renderer_data[AgDef.CONCEPT_BUILD_DATA_FIELD_ID];

					Ext.each(PartDatas,function(Part){
						var part_data = Ext.apply({},{},version_data);
						part_data[AgDef.CONCEPT_DATA_INFO_DATA_FIELD_ID] = Part[AgDef.CONCEPT_DATA_INFO_DATA_FIELD_ID];
						part_data[AgDef.ID_DATA_FIELD_ID] = Part[AgDef.ID_DATA_FIELD_ID];
						part_data[AgDef.NAME_DATA_FIELD_ID] = Part[AgDef.NAME_DATA_FIELD_ID];

						if(Ext.isNumber(merge_hash.Camera.Zoom)){
							part_data[AgDef.USE_FOR_BOUNDING_BOX_FIELD_ID] = false;
						}else{
							part_data[AgDef.USE_FOR_BOUNDING_BOX_FIELD_ID] = Part.UseForBoundingBoxFlag;
						}
//						part_data[AgDef.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = Ext.String.format('#{0}',Part.PartColor);
						part_data[AgDef.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = Part.PartColor;
						part_data[AgDef.CONCEPT_DATA_OPACITY_DATA_FIELD_ID] = Part.PartOpacity;
						part_data[AgDef.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID] = Part.PartDeleteFlag ? false : true;

						Ext.each(Part[AgDef.OBJ_IDS_DATA_FIELD_ID],function(art_id){
							if(Ext.isObject(art_datas[art_id])) return true;
							var art_data = Ext.apply({},{},part_data);
							art_data[AgDef.OBJ_ID_DATA_FIELD_ID] = art_id;
							art_data[AgDef.OBJ_FILENAME_FIELD_ID] = Ext.String.format('{0}{1}',art_id,AgDef.OBJ_EXT_NAME);
							art_data[AgDef.OBJ_URL_DATA_FIELD_ID] = Ext.String.format('{0}/{1}{2}',AgDef.OBJ_PATH_NAME,art_id,AgDef.OBJ_EXT_NAME);

//							console.log(art_data);
							art_datas[art_id] = art_data;

							records.push(Ext.create('CONCEPT_TERM_PALLET', art_data));
						});

					});

					self.__SearchResultRenderer.setAutoFocus(false);
					self.__SearchResultRenderer.setAutoRender(false);

					self.__SearchResultRenderer.hideAllObj();
					self.__SearchResultRenderer.loadObj(self.getObjDataFromRecords(records),function(){
					});

					if(Ext.isNumber(merge_hash.Camera.TargetX) && Ext.isNumber(merge_hash.Camera.TargetY) && Ext.isNumber(merge_hash.Camera.TargetZ)){
						self.__SearchResultRenderer.setTarget({
							x:merge_hash.Camera.TargetX,
							y:merge_hash.Camera.TargetY,
							z:merge_hash.Camera.TargetZ
						});
					}
					if(
						Ext.isNumber(merge_hash.Camera.CameraX) && Ext.isNumber(merge_hash.Camera.CameraY) && Ext.isNumber(merge_hash.Camera.CameraZ) &&
						Ext.isNumber(merge_hash.Camera.CameraUpVectorX) && Ext.isNumber(merge_hash.Camera.CameraUpVectorY) && Ext.isNumber(merge_hash.Camera.CameraUpVectorZ)
					){
						self.__SearchResultRenderer.setCameraPosition({
							x:merge_hash.Camera.CameraX,
							y:merge_hash.Camera.CameraY,
							z:merge_hash.Camera.CameraZ
						},{
							x:merge_hash.Camera.CameraUpVectorX,
							y:merge_hash.Camera.CameraUpVectorY,
							z:merge_hash.Camera.CameraUpVectorZ
						});
					}

						self.__SearchResultRenderer.setTarget({x: -0.6599998474121094, y: -54.58045148849487, z: 1513.875});
						self.__SearchResultRenderer.setCameraPosition({x: -0.6599998474121094, y: -1854.5804514884949, z: 1513.875},{x: 0, y: 0, z: 1});


					if(Ext.isNumber(merge_hash.Camera.Zoom)){
						console.log(merge_hash.Camera.Zoom);
						self.__SearchResultRenderer.setDispZoom(merge_hash.Camera.Zoom+1);
						self.__SearchResultRenderer.setAutoRender(true);
					}else{
						self.__SearchResultRenderer.setAutoFocus(true);
						self.__SearchResultRenderer.setAutoRender(true);
					}

					self.__SearchResultRenderer.setAutoFocus(true);

				}
				console.log(PartDatas);
			}
		}





		if(hash.ci_id && !hash[AgDef.LOCATION_HASH_CIID_KEY]) hash[AgDef.LOCATION_HASH_CIID_KEY] = hash.ci_id;
		if(hash.cb_id && !hash[AgDef.LOCATION_HASH_CBID_KEY]) hash[AgDef.LOCATION_HASH_CBID_KEY] = hash.cb_id;
		if(hash.search && !hash[AgDef.LOCATION_HASH_NAME_KEY]) hash[AgDef.LOCATION_HASH_NAME_KEY] = hash.search;
		delete hash.ci_id;
		delete hash.cb_id;
		delete hash.search;

		return hash;
	},

	setLocationHash : function(hashObject,silent){
		var self = this;
		var hash = Ext.apply(self.getLocationHash(),hashObject || {});
		Ext.Object.each(hash,function(key,value){
			if(Ext.isEmpty(value)) delete hash[key];
		});
		if(!Ext.isBoolean(silent)) silent = false;
		if(silent){
			$(window).off('hashchange',self._hashChange);
			window.location.hash = Ext.Object.toQueryString(hash);
			$(window).on('hashchange',self._hashChange);
		}else{
			window.location.hash = Ext.Object.toQueryString(hash);
		}
	},

	getEmptyRecord : function(){
		var self = this;
		return Ext.create(Ext.data.StoreManager.lookup(AgDef.CONCEPT_TERM_STORE_ID).model.getName(),{});
	},

	setLastRecord : function(record){
		var self = this;
		self.__lastRecord = record && record.copy ? record.copy() : self.getEmptyRecord();
		if(window.postMessage) window.postMessage({type:'updatelastrecord',data:self.__lastRecord.getData()},window.location.origin);
	},

	getLastRecord : function(){
		var self = this;
		return self.__lastRecord || self.getEmptyRecord();
	},

	isEmpty : function(value){
		if(Ext.isEmpty(value) || (Ext.isString(value) && (value=='none' || value.length==0))){
			return true;
		}else{
			return false;
		}
	},

	initTemplate : function(){
		var self = this;
	},

	initBind : function(){
		var self = this;

		self._hashChange = Ext.bind(function(e){
			var self = this;
			Ext.defer(function(){
				var combobox = Ext.getCmp(self.DEF_CONCEPT_BUILD_FORM_FIELD_ID);
				var hash = self.getLocationHash();
				if(Ext.isNumeric(hash[AgDef.LOCATION_HASH_CIID_KEY]) && Ext.isNumeric(hash[AgDef.LOCATION_HASH_CBID_KEY])){
					var value = Ext.util.Format.format(AgDef.FORMAT_CONCEPT_VALUE, hash[AgDef.LOCATION_HASH_CIID_KEY],hash[AgDef.LOCATION_HASH_CBID_KEY]);
					if(value != combobox.getValue()){
						var record = combobox.findRecordByValue(value);
						if(record){
							combobox.suspendEvent('select');
							combobox.setValue(value);
							combobox.resumeEvent('select');
						}
					}
				}


				var hashId     = self.isEmpty(hash[AgDef.LOCATION_HASH_ID_KEY])     ? null : Ext.String.trim(hash[AgDef.LOCATION_HASH_ID_KEY]);
				var hashName   = self.isEmpty(hash[AgDef.LOCATION_HASH_NAME_KEY])   ? null : Ext.String.trim(hash[AgDef.LOCATION_HASH_NAME_KEY]);
				var hashSearch = self.isEmpty(hash[AgDef.LOCATION_HASH_SEARCH_KEY]) ? null : Ext.String.trim(hash[AgDef.LOCATION_HASH_SEARCH_KEY]);
				var field;
				if(hashSearch){
					field = Ext.getCmp(self.DEF_SEARCH_FORM_FIELD_ID);
					if(hashSearch == field.getValue()){
					}else{
						field.setValue(hashSearch);
					}
				}
				if(hashName){
					field = Ext.getCmp(self.DEF_NAME_FORM_FIELD_ID);
					if(hashName == field.getValue()){
					}else{
						field.setValue(hashName);
					}
				}
				if(hashId){
					field = Ext.getCmp(self.DEF_ID_FORM_FIELD_ID);
					if(hashId == field.getValue()){
					}else{
						field.setValue(hashId);
					}
				}
				if(field){
					field.specialkeyENTER();
				}
			},250);
		},self);

		$(window).on('hashchange',self._hashChange);


		$(document).on('dragstart','*[draggable]',function(e){
			e.originalEvent.dataTransfer.effectAllowed = 'copy';
			if(false && Ext.getCmp('dragtype-url').getValue()){
				e.originalEvent.dataTransfer.setData('text/plain', window.location.href);
			}
			else{
				var all_text_datas = [];

				var datas = [];
				if(this.nodeName=='TR' && $(this).attr('data-boundview')){
					try{
						var view_id = $(this).attr('data-boundview');
						datas = Ext.Array.map(Ext.getCmp(view_id).panel.getSelectionModel().getSelection(),function(record){
							var hash = {};
							hash[self.DEF_ID_LABEL] = record.get(AgDef.ID_DATA_FIELD_ID);
							hash[self.DEF_NAME_LABEL] = record.get(AgDef.NAME_DATA_FIELD_ID);
							hash[self.DEF_SYNONYM_LABEL] = record.get(AgDef.SYNONYM_DATA_FIELD_ID);
							hash[AgDef.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = record.get(AgDef.CONCEPT_DATA_COLOR_DATA_FIELD_ID);
							return hash;
						});
					}catch(e){
						console.error(e);
					}
				}
				if(datas.length){
					if(false && self.DEF_MODEL_VERSION_RECORD){
						var hash = {};
						hash['model'] = self.DEF_MODEL_VERSION_RECORD.get('md_name');
						hash['version'] = self.DEF_MODEL_VERSION_RECORD.get('mv_name');
						hash['concept'] = self.DEF_MODEL_VERSION_RECORD.get('ci_name');
						hash['build'] = self.DEF_MODEL_VERSION_RECORD.get('cb_name');
						hash['datas'] = datas;
						e.originalEvent.dataTransfer.setData('text/plain', Ext.encode(hash));
					}
					else{
						e.originalEvent.dataTransfer.setData('text/plain', Ext.encode(datas));
					}
				}else if(this.nodeName=='TABLE'){
					var lastRecord = self.getLastRecord();
					var hash = {};
					hash[self.DEF_ID_LABEL] = lastRecord.get(AgDef.ID_DATA_FIELD_ID);
					hash[self.DEF_NAME_LABEL] = lastRecord.get(AgDef.NAME_DATA_FIELD_ID);
					hash[self.DEF_SYNONYM_LABEL] = lastRecord.get(AgDef.SYNONYM_DATA_FIELD_ID);
					hash[self.DEF_DEFINITION_LABEL] = lastRecord.get(AgDef.DEFINITION_DATA_FIELD_ID);
					e.originalEvent.dataTransfer.setData('text/plain', Ext.encode(hash));
				}
				else if(this.nodeName=='TR'){
					var text_datas = [];
					$(this).find('th,td').each(function(){
						$(this).find('label').each(function(){
							text_datas.push($(this).text());
						});
						$(this).find('div').each(function(){
							text_datas.push($(this).text());
						});
					});
					all_text_datas.push(text_datas.join("\t"));
					e.originalEvent.dataTransfer.setData('text/plain', all_text_datas.join("\n"));
				}
				else{
					all_text_datas.push($(this).text());
					e.originalEvent.dataTransfer.setData('text/plain', all_text_datas.join("\n"));
				}
			}
			e.stopPropagation();
		});

		$(document).on('mouseover','*[draggable]',function(e){	//mouseenter
			$(this).addClass('draggable-hover');
			e.preventDefault();
			e.stopPropagation();
		});
		$(document).on('mouseout','*[draggable]',function(e){	//mouseleave
			$(this).removeClass('draggable-hover');
			e.preventDefault();
			e.stopPropagation();
		});
	},

	initDelayedTask : function(){
		var self = this;
	},

	initExtJS : function(){
		var self = this;
		Ext.QuickTips.init();
	//		Ext.state.Manager.setProvider(new Ext.state.CookieProvider()); //ソート順とかをCookieに登録する為に必要らしい
		Ext.state.Manager.setProvider(new Ext.state.LocalStorageProvider({
			prefix: self.DEF_LOCALDB_PROVIDER_PREFIX,
			listeners: {
				statechange: function(provider, key, value, eOpts){
				}
			}
		}));
	},

	getExtraParams : function(params){
		var self = this;

		params = params || {};

		var hash = {};

		if(self.DEF_MODEL_VERSION_RECORD){
			hash[AgDef.LOCATION_HASH_MDID_KEY] = self.DEF_MODEL_VERSION_RECORD.get(AgDef.MODEL_DATA_FIELD_ID);
			hash[AgDef.LOCATION_HASH_MVID_KEY] = self.DEF_MODEL_VERSION_RECORD.get(AgDef.MODEL_VERSION_DATA_FIELD_ID);
	//		hash[AgDef.LOCATION_HASH_MRID_KEY] = self.DEF_MODEL_VERSION_RECORD.get(AgDef.MODEL_REVISION_DATA_FIELD_ID);
			hash[AgDef.LOCATION_HASH_CIID_KEY] = self.DEF_MODEL_VERSION_RECORD.get(AgDef.CONCEPT_INFO_DATA_FIELD_ID);
			hash[AgDef.LOCATION_HASH_CBID_KEY] = self.DEF_MODEL_VERSION_RECORD.get(AgDef.CONCEPT_BUILD_DATA_FIELD_ID);
		}
		else{
			//
			//指定されているバージョンが使用不可の時、とりあえず、最初のレコードを使用する
			//
			var modelVersionStore = Ext.data.StoreManager.lookup('modelVersionStore');
			var record = modelVersionStore.getAt(0);
			if(record){
				hash[AgDef.LOCATION_HASH_MDID_KEY] = record.get(AgDef.MODEL_DATA_FIELD_ID);
				hash[AgDef.LOCATION_HASH_MVID_KEY] = record.get(AgDef.MODEL_VERSION_DATA_FIELD_ID);
	//			hash[AgDef.LOCATION_HASH_MRID_KEY] = record.get(AgDef.MODEL_REVISION_DATA_FIELD_ID);
				hash[AgDef.LOCATION_HASH_CIID_KEY] = record.get(AgDef.CONCEPT_INFO_DATA_FIELD_ID);
				hash[AgDef.LOCATION_HASH_CBID_KEY] = record.get(AgDef.CONCEPT_BUILD_DATA_FIELD_ID);

				self.DEF_MODEL_VERSION_RECORD = record;
				self.DEF_MODEL_VERSION_VALUE = Ext.util.Format.format(AgDef.FORMAT_MODEL_VERSION_VALUE, record.get(AgDef.MODEL_DATA_FIELD_ID), record.get(AgDef.MODEL_VERSION_DATA_FIELD_ID));
				self.DEF_CONCEPT_BUILD_VALUE = Ext.util.Format.format(AgDef.FORMAT_CONCEPT_VALUE, record.get(AgDef.CONCEPT_INFO_DATA_FIELD_ID), record.get(AgDef.CONCEPT_BUILD_DATA_FIELD_ID));
			}
		}
		return hash;
	},

	beforeloadStore : function(store){
		var self = this;

		var extraParams = self.getExtraParams() || {};
		if(Ext.isEmpty(extraParams)) return false;

		var p = store.getProxy();
		p.extraParams = p.extraParams || {};
		p.extraParams = Ext.apply({},extraParams,p.extraParams);

		return true;
	},

	getBufferedRenderer : function(args){
		var self = this;
		args = Ext.apply({},args||{},{
			pluginId: 'bufferedrenderer',
			trailingBufferZone: 20,
			leadingBufferZone: 50
		});
		return Ext.create('Ext.grid.plugin.BufferedRenderer', args);
	},

	initComponent : function(){
		var self = this;

		var conceptInfoStore = Ext.data.StoreManager.lookup('conceptInfoStore');
		var conceptInfoIdx = conceptInfoStore.findBy(function(record){
			return record.get('ci_name')===self.DEF_CONCEPT_INFO_TERM;
		});
		if(conceptInfoIdx>=0){
			var record = conceptInfoStore.getAt(conceptInfoIdx);
			if(record) self.DEF_CONCEPT_INFO_VALUE = record.get(AgDef.CONCEPT_INFO_DATA_FIELD_ID);
		}

		var conceptBuildStore = Ext.data.StoreManager.lookup('conceptBuildStore');
		var conceptBuildIdx = conceptBuildStore.findBy(function(record){
			return record.get('ci_name')===self.DEF_CONCEPT_INFO_TERM && record.get('cb_name')===self.DEF_CONCEPT_BUILD_TERM;
		});
		if(conceptBuildIdx>=0){
			var record = conceptBuildStore.getAt(conceptBuildIdx);
			if(record) self.DEF_CONCEPT_BUILD_VALUE = Ext.util.Format.format(AgDef.FORMAT_CONCEPT_VALUE, record.get(AgDef.CONCEPT_INFO_DATA_FIELD_ID), record.get(AgDef.CONCEPT_BUILD_DATA_FIELD_ID));
		}

		var modelVersionStore = Ext.data.StoreManager.lookup('modelVersionStore');
		var modelVersionIdx = modelVersionStore.findBy(function(record){
			return record.get('md_name')===self.DEF_MODEL_TERM && record.get('mv_name')===self.DEF_MODEL_VERSION_TERM;
		});
		if(modelVersionIdx>=0){
			var record = modelVersionStore.getAt(modelVersionIdx);
			if(record){
				self.DEF_MODEL_VERSION_RECORD = record;
				self.DEF_MODEL_VERSION_VALUE = Ext.util.Format.format(AgDef.FORMAT_MODEL_VERSION_VALUE, record.get(AgDef.MODEL_DATA_FIELD_ID), record.get(AgDef.MODEL_VERSION_DATA_FIELD_ID));
				self.DEF_CONCEPT_BUILD_VALUE = Ext.util.Format.format(AgDef.FORMAT_CONCEPT_VALUE, record.get(AgDef.CONCEPT_INFO_DATA_FIELD_ID), record.get(AgDef.CONCEPT_BUILD_DATA_FIELD_ID));
			}
		}

		var searchOptionCheckHandler = function(field,checked){
			var toolbar = field.up('toolbar');
			var combobox = toolbar.down('combobox#'+self.DEF_SEARCH_FORM_FIELD_ID);
			if(combobox){
				combobox.inputEl.focus();
				var value = combobox.inputEl.getValue().trim();
				if(value.length) combobox.doQuery(value);
			}
		};

		var view_dockedItems = [{
			hidden: self.DEF_VIEW_DOCITEMS_HIDDEN,
			xtype: 'toolbar',
			dock: 'top',
			layout: {
				overflowHandler: 'Menu'
			},
			items:[{
				hidden: true,
				id: self.DEF_CONCEPT_INFO_FORM_FIELD_ID,
				fieldLabel: self.DEF_CONCEPT_LABEL,
				labelWidth: self.DEF_CONCEPT_FORM_LABEL_WIDTH,
				width: self.DEF_CONCEPT_FORM_LABEL_WIDTH+self.DEF_CONCEPT_INFO_FORM_FIELD_WIDTH,
				xtype: self.DEF_CONCEPT_INFO_FORM_FIELD_XTYPE,
				editable: false,
				queryMode: 'local',
				displayField: 'display',
				valueField: 'value',
				store: conceptInfoStore,
				listeners: {
					afterrender: function(combobox, eOpts){
					},
					select: function(combobox){
					}
				}
			},{
				hidden: true,
				id: self.DEF_CONCEPT_BUILD_FORM_FIELD_ID,
				hideLabel: true,
				width: self.DEF_CONCEPT_BUILD_FORM_FIELD_WIDTH,

				xtype: 'combobox',
				editable: false,
				queryMode: 'local',
				displayField: 'display',
				valueField: 'value',
				store: conceptBuildStore,
				listeners: {
					afterrender: function(combobox, eOpts){
					},
					select: function(combobox){
					}
				}
			},
			{
				xtype: 'tbseparator',
				hidden: true
			},

			'->',

			{
				xtype: 'tbseparator',
				hidden: true
			},

			{
				xtype: 'button',
				text: self.DEF_SEARCH_LABEL,
				menu: {
					defaultType: 'menucheckitem',
					items: [
					{
						itemId: self.DEF_SEARCH_ANY_MATCH_ID,
						text: self.DEF_SEARCH_ANY_MATCH_LABEL,
						name: AgDef.SEARCH_ANY_MATCH_NAME,
						inputValue: '1',
						checked: true,
						checkHandler: searchOptionCheckHandler
					},{
						itemId: self.DEF_SEARCH_CASE_SENSITIVE_ID,
						text: self.DEF_SEARCH_CASE_SENSITIVE_LABEL,
						name: AgDef.SEARCH_CASE_SENSITIVE_NAME,
						inputValue: '1',
						checked: false,
						checkHandler: searchOptionCheckHandler
					}]
				}
			},

			{
				xtype: self.DEF_SEARCH_TARGET_ELEMENT_XTYPE,
				itemId: self.DEF_SEARCH_TARGET_ELEMENT_ID,
				text: self.DEF_SEARCH_TARGET_ELEMENT_LABEL,
				pressed: self.DEF_SEARCH_TARGET_CHECKED_ID === self.DEF_SEARCH_TARGET_ELEMENT_ID,
				inputValue: AgDef.SEARCH_TARGET_ELEMENT_VALUE,
				enableToggle: true,
				toggleGroup: AgDef.SEARCH_TARGET_NAME,
				toggleHandler: searchOptionCheckHandler
			},{
				xtype: self.DEF_SEARCH_TARGET_WHOLE_XTYPE,
				itemId: self.DEF_SEARCH_TARGET_WHOLE_ID,
				text: self.DEF_SEARCH_TARGET_WHOLE_LABEL,
				pressed: self.DEF_SEARCH_TARGET_CHECKED_ID === self.DEF_SEARCH_TARGET_WHOLE_ID,
				inputValue: AgDef.SEARCH_TARGET_WHOLE_VALUE,
				enableToggle: true,
				toggleGroup: AgDef.SEARCH_TARGET_NAME,
				toggleHandler: searchOptionCheckHandler
			},

			{
				hidden: false,
				id: self.DEF_SEARCH_FORM_FIELD_ID,
				itemId: self.DEF_SEARCH_FORM_FIELD_ID,
				name: AgDef.LOCATION_HASH_SEARCH_KEY,
				fieldLabel: self.DEF_SEARCH_LABEL,
				hideLabel: true,
				emptyText: self.DEF_SEARCH_LABEL,
				width: self.DEF_SEARCH_FORM_FIELD_WIDTH,
				xtype: self.DEF_SEARCH_FORM_FIELD_XTYPE,
				selectOnFocus: true,
				store: AgDef.CONCEPT_TERM_SEARCH_STORE_ID,
				queryMode: 'remote',
				displayField: AgDef.NAME_DATA_FIELD_ID,
				valueField: AgDef.ID_DATA_FIELD_ID,
				hideTrigger: true,
				enableKeyEvents: true,
				allowBlank: true,
				allowOnlyWhitespace: true,
				anyMatch: true,
				caseSensitive: false,
				enableRegEx: true,
				vtype: self.DEF_SEARCH_FORM_FIELD_VTYPE,
				pageSize: AgDef.CONCEPT_TERM_SEARCH_GRID_PAGE_SIZE,
				queryCaching: false,
				queryParam: AgDef.LOCATION_HASH_SEARCH_KEY,
				matchFieldWidth: false,
				specialkeyENTER: function(){
				},
				listeners: {
				}
			},

			{
				hidden: true,
				id: self.DEF_SEARCH_EXCLUDE_FORM_FIELD_ID,
				itemId: self.DEF_SEARCH_EXCLUDE_FORM_FIELD_ID,
				name: AgDef.LOCATION_HASH_SEARCH_EXCLUDE_KEY,
				fieldLabel: self.DEF_SEARCH_EXCLUDE_LABEL,
				hideLabel: true,
				emptyText: self.DEF_SEARCH_EXCLUDE_LABEL,
				width: self.DEF_NAME_FORM_FIELD_WIDTH,
				xtype: self.DEF_SEARCH_EXCLUDE_FORM_FIELD_XTYPE,
				selectOnFocus: false,
				enableKeyEvents: true,
				listeners: {
				}
			},
			{
				xtype: 'tbseparator',
				hidden: true
			},
			{
				id: self.DEF_ID_FORM_FIELD_ID,
				fieldLabel: self.DEF_ID_LABEL,
				labelWidth: self.DEF_ID_FORM_LABEL_WIDTH,
				hidden: true,
				width: self.DEF_ID_FORM_LABEL_WIDTH+self.DEF_ID_FORM_FIELD_WIDTH,
				xtype: self.DEF_ID_FORM_FIELD_XTYPE,
				itemId: self.DEF_ID_FORM_FIELD_ID,
				name: AgDef.LOCATION_HASH_ID_KEY,
				vtype: self.DEF_ID_FORM_FIELD_VTYPE,
				selectOnFocus: true,
				enableKeyEvents: true,
				specialkeyENTER: function(){
				},
				listeners: {
				}
			},
			{
				xtype: 'tbseparator',
				hidden: true
			},
			{
				hidden: true,
				id: self.DEF_NAME_FORM_FIELD_ID,
				fieldLabel: self.DEF_NAME_LABEL,
				labelWidth: self.DEF_NAME_FORM_LABEL_WIDTH,
				width: self.DEF_NAME_FORM_LABEL_WIDTH+self.DEF_NAME_FORM_FIELD_WIDTH,
				xtype: self.DEF_NAME_FORM_FIELD_XTYPE,
				itemId: self.DEF_NAME_FORM_FIELD_ID,
				name: AgDef.LOCATION_HASH_NAME_KEY,
				selectOnFocus: true,
				enableKeyEvents: true,
				vtype: self.DEF_NAME_FORM_FIELD_VTYPE,
				specialkeyENTER: function(){
				},
				listeners: {
				}
			}]
		}];

		var bodySize = Ext.getBody().getSize();
		var height = Math.floor((bodySize.height-27)/3)-10*2;

		var _getObjDataFromRecord = function(record,selModel,is_selected){
			var hash = record.getData();
			if(Ext.isDate(hash[AgDef.OBJ_TIMESTAMP_DATA_FIELD_ID])){
				hash[AgDef.OBJ_URL_DATA_FIELD_ID] += '?'+hash[AgDef.OBJ_TIMESTAMP_DATA_FIELD_ID].getTime();
			}
			delete hash[AgDef.OBJ_TIMESTAMP_DATA_FIELD_ID];

			hash[AgDef.CONCEPT_DATA_SELECTED_DATA_FIELD_ID] = null;
			if(selModel){
				if(selModel.isSelected(record)){

					if(self.USE_SELECTION_RENDERER_PICKED_COLOR){
						hash[AgDef.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = self.DEF_SELECTION_RENDERER_PICKED_COLOR;
					}
					if(self.USE_SELECTION_RENDERER_PICKED_COLOR_FACTOR){

						var rgb = d3.rgb( hash[AgDef.CONCEPT_DATA_COLOR_DATA_FIELD_ID] );
						var grayscale = rgb.r * 0.3 + rgb.g * 0.59 + rgb.b * 0.11;
						var k = grayscale>127.5 ? true : false;
						if(self.DEF_SELECTION_RENDERER_PICKED_COLOR_FACTOR>0){
							var factor = self.DEF_SELECTION_RENDERER_PICKED_COLOR_FACTOR;
							if(!self.USE_SELECTION_RENDERER_PICKED_COLOR) factor += k ? 0 : 0.1;
							hash[AgDef.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = rgb.brighter(factor).toString();
						}
						else if(self.DEF_SELECTION_RENDERER_PICKED_COLOR_FACTOR<0){
							var factor = self.DEF_SELECTION_RENDERER_PICKED_COLOR_FACTOR * -1;
							if(!self.USE_SELECTION_RENDERER_PICKED_COLOR) factor += k ? 0 : 0.1;
							hash[AgDef.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = rgb.darker(factor).toString();
						}

					}
					hash[AgDef.CONCEPT_DATA_SELECTED_DATA_FIELD_ID] = true;
				}
				else if(Ext.isBoolean(is_selected) && is_selected){
					if(hash[AgDef.CONCEPT_DATA_OPACITY_DATA_FIELD_ID]>=1.0) hash[AgDef.CONCEPT_DATA_SELECTED_DATA_FIELD_ID] = false;

					if(self.USE_SELECTION_RENDERER_PICKED_OTHER_OPACITY || self.USE_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR){
						var rgb = d3.rgb( hash[AgDef.CONCEPT_DATA_COLOR_DATA_FIELD_ID] );
						var grayscale = rgb.r * 0.3 + rgb.g * 0.59 + rgb.b * 0.11;
						var k = grayscale>127.5 ? true : false;

						if(self.USE_SELECTION_RENDERER_PICKED_OTHER_OPACITY){
							hash[AgDef.CONCEPT_DATA_OPACITY_DATA_FIELD_ID] = self.DEF_SELECTION_RENDERER_PICKED_OTHER_OPACITY;
						}

						if(self.USE_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR){
							if(self.DEF_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR>0){
								hash[AgDef.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = rgb.brighter(self.DEF_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR).toString();
							}
							else if(self.DEF_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR<0){
								hash[AgDef.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = rgb.darker(self.DEF_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR*-1).toString();
							}
						}
					}
				}
			}
			return hash;
		};

		var getObjDataFromRecords;
		self.getObjDataFromRecords = getObjDataFromRecords = function(records,selModel,is_selected){
			return records.map(Ext.bind(_getObjDataFromRecord,self,[selModel,is_selected],1));
		};

		var center_panel = {
			region: 'center',
			id: self.DEF_SEARCH_RESULT_RENDERING_IMAGE_ID,
			title: self.DEF_SEARCH_RESULT_RENDERING_IMAGE_LABEL,
			header: self.DEF_SEARCH_RESULT_RENDERING_IMAGE_SHOW_HEADER,

			dockedItems: [{
				xtype: 'toolbar',
				dock: 'top',
				itemId: 'top',
				items: [{
					xtype: 'numberfield',
					labelWidth: 10,
					width: 72,
					name: 'longitude',
					itemId: 'longitude',
					fieldLabel: 'H',
					allowBlank:false,
					allowDecimals: false,
					keyNavEnabled: false,
					mouseWheelEnabled: false,
					selectOnFocus: false,
					step: 1,
					value: 0,
					maxValue: 359,
					minValue: 0,
					validator: function(){
						var value = Math.round(this.value/this.step)*this.step;
						if(value > this.maxValue) value -= (this.maxValue+this.step);
						if(value < this.minValue) value += (this.maxValue+this.step);
						if(value != this.value) Ext.defer(function(){ this.setValue(value); },50,this);
						return true;
					},
					listeners: {
						change: function( field, newValue, oldValue, eOpts ){
							if(self.__SearchResultRenderer){
								self.__SearchResultRenderer.setHorizontal(newValue);
								if(self.__AgSubRenderer) self.__AgSubRenderer.setHorizontal(newValue);
							}
						},
						afterrender: function(field, eOpts){
							field.spinDownEl.on('mousedown',function(e,t,o){
								if(field.value==field.minValue) Ext.defer(function(){ this.setValue(field.maxValue); },50,field);
							});
							field.spinUpEl.on('mousedown',function(e,t,o){
								if(field.value==field.maxValue) Ext.defer(function(){ this.setValue(field.minValue); },50,field);
							});
						},
						specialkey: function(field, e, eOpts){
							if(e.getKey()==e.DOWN && field.value==field.minValue){
								Ext.defer(function(){ this.setValue(field.maxValue); },50,field);
							}else if(e.getKey()==e.UP && field.value==field.maxValue){
								Ext.defer(function(){ this.setValue(field.minValue); },50,field);
							}
							e.stopPropagation();
						}
					}
				},{
					xtype: 'numberfield',
					labelWidth: 10,
					width: 72,
					name: 'latitude',
					itemId: 'latitude',
					fieldLabel: 'V',
					allowBlank:false,
					allowDecimals: false,
					keyNavEnabled: false,
					mouseWheelEnabled: false,
					selectOnFocus: false,
					step: 1,
					value: 0,
					maxValue: 359,
					minValue: 0,
					validator: function(){
						var value = Math.round(this.value/this.step)*this.step;
						if(value > this.maxValue) value -= (this.maxValue+this.step);
						if(value < this.minValue) value += (this.maxValue+this.step);
						if(value != this.value) Ext.defer(function(){ this.setValue(value); },50,this);
						return true;
					},
					listeners: {
						change: function( field, newValue, oldValue, eOpts ){
							if(self.__SearchResultRenderer){
								self.__SearchResultRenderer.setVertical(newValue);
								if(self.__AgSubRenderer) self.__AgSubRenderer.setVertical(newValue);
							}
						},
						afterrender: function(field, eOpts){
							field.spinDownEl.on('mousedown',function(e,t,o){
								if(field.value==field.minValue) Ext.defer(function(){ this.setValue(field.maxValue); },50,field);
							});
							field.spinUpEl.on('mousedown',function(e,t,o){
								if(field.value==field.maxValue) Ext.defer(function(){ this.setValue(field.minValue); },50,field);
							});
						},
						specialkey: function(field, e, eOpts){
							if(e.getKey()==e.DOWN && field.value==field.minValue){
								Ext.defer(function(){ this.setValue(field.maxValue); },50,field);
							}else if(e.getKey()==e.UP && field.value==field.maxValue){
								Ext.defer(function(){ this.setValue(field.minValue); },50,field);
							}
							e.stopPropagation();
						}
					}
				},{
					xtype: 'numberfield',
					labelWidth: 34,
					width: 98,
					name: 'zoom',
					itemId: 'zoom',
					fieldLabel: 'Zoom',
					allowBlank:false,
					allowDecimals: false,
					keyNavEnabled: false,
					mouseWheelEnabled: false,
					selectOnFocus: false,
					value: 1,
					maxValue: 100,
					minValue: 1,
					validator: function(){
						var value = Math.round(this.value);
						if(value > this.maxValue) value = this.maxValue;
						if(value < this.minValue) value = this.minValue;
						if(value != this.value) Ext.defer(function(){ this.setValue(value); },50,this);
						return true;
					},
					listeners: {
						change: function( field, newValue, oldValue, eOpts ){
							if(self.__SearchResultRenderer){
								console.log('change',newValue);
								self.__SearchResultRenderer.setDispZoom(newValue);
							}
						},
						specialkey: function(field, e, eOpts){
							e.stopPropagation();
						}
					}
				},'->',{
					hidden: self.DEF_SEARCH_RESULT_RENDERING_OPTION_BUTTIN_HIDDEN,
					xtype: 'button',
					iconCls: 'gear-btn',
					tooltip: 'Options [ Renderer ]',
					handler: function(button,e){
					},
					listeners: {
						afterrender: function( comp, eOpts ){
						}
					}
				}]
			}],
			listeners: {
				afterrender: function(panel, eOpts){
					if(Ext.isEmpty(self.__SearchResultRenderer)){
						var pickDelayedTask =  new Ext.util.DelayedTask(function(record){
							var gridpanel = Ext.getCmp(self.DEF_SEARCH_RESULT_LIST_ID);
							var selModel = gridpanel.getSelectionModel();
							selModel.deselect([record]);
						});

						var dblclickFunc =  function(record,e){
							var conceptParentStore = Ext.data.StoreManager.lookup(AgDef.CONCEPT_PARENT_TERM_STORE_ID);
							var params = {};
							params[AgDef.LOCATION_HASH_CID_KEY] = record.get(AgDef.LOCATION_HASH_ID_KEY);
							Ext.Ajax.abortAll();
							conceptParentStore.loadPage(1,{
								params: params,
								callback: function(records,operation,success){
								}
							});
						}

						var zoom_field = panel.down('toolbar#top').down('numberfield#zoom');
						self.__SearchResultRenderer = new AgMainRenderer({
							width:108,
							height:108,
							rate:1,
							minZoom: zoom_field.minValue,
							maxZoom: zoom_field.maxValue,
							backgroundColor: self.DEF_RENDERER_BACKGROUND_COLOR,
							listeners: {
								pick: function(ren,intersects,e){
									var is_dblclick = false;
									if(e.ctrlKey){
										if(Ext.isDate(self.__lastPickDate)) delete self.__lastPickDate;
									}else{
										var current_date = new Date();
										if(Ext.isDate(self.__lastPickDate)){
											var dt = Ext.Date.add(self.__lastPickDate, Ext.Date.MILLI, self.DEF_DOUBLE_CLICK_INTERVAL);
											is_dblclick = Ext.Date.between(current_date,self.__lastPickDate, dt);
										}
										self.__lastPickDate = current_date;
									}

									console.log('pick',ren,intersects,e);
									if(Ext.isArray(intersects) && intersects.length){
										var mesh = intersects[0].object;

										var gridpanel = Ext.getCmp(self.DEF_SEARCH_RESULT_LIST_ID);
										var store = gridpanel.getStore();
										var selModel = gridpanel.getSelectionModel();
										var recordIdx = store.find( AgDef.OBJ_ID_DATA_FIELD_ID, mesh[AgDef.OBJ_ID_DATA_FIELD_ID], 0, false, false, true );
										if(recordIdx>=0){
											var record = store.getAt(recordIdx);
											if(selModel.isSelected(record)){
												if(is_dblclick){
													pickDelayedTask.cancel();
													dblclickFunc(record,e);
												}else{
													if(e.ctrlKey){
														selModel.deselect([record]);
													}else{
														pickDelayedTask.delay(self.DEF_DOUBLE_CLICK_INTERVAL,null,null,[record]);
													}
												}
											}else{
												var plugin = gridpanel.getPlugin(self.DEF_SEARCH_RESULT_LIST_PLUGIN_ID);
												plugin.scrollTo( recordIdx, false, function(recordIdx,record){
													selModel.select([record],e.ctrlKey);
												}, self );
											}
										}
									}
								},
								rotate: function(ren,value){
									var longitude_field = panel.down('toolbar#top').down('numberfield#longitude');
									var latitude_field = panel.down('toolbar#top').down('numberfield#latitude');
									if(longitude_field){
										if(longitude_field.getValue() !== value.H){
											longitude_field.suspendEvent('change');
											try{
												longitude_field.setValue(value.H);
											}catch(e){
												console.error(e);
											}
											longitude_field.resumeEvent('change');
											if(self.__AgSubRenderer) self.__AgSubRenderer.setHorizontal(value.H);
										}
									}
									if(latitude_field){
										if(latitude_field.getValue() !== value.V){
											latitude_field.suspendEvent('change');
											try{
												latitude_field.setValue(value.V);
											}catch(e){
												console.error(e);
											}
											latitude_field.resumeEvent('change');
											if(self.__AgSubRenderer) self.__AgSubRenderer.setVertical(value.V);
										}
									}
								},
								zoom: function(ren,value){
									var zoom_field = panel.down('toolbar#top').down('numberfield#zoom');
									if(zoom_field){
										if(zoom_field.getValue() !== value){
											zoom_field.suspendEvent('change');
											try{
												zoom_field.setValue(value);
											}catch(e){
												console.error(e);
											}
											zoom_field.resumeEvent('change');
										}
									}
								}
							}
						});
					}else{
						self.__SearchResultRenderer.domElement.style.display = '';
						self.__SearchResultRenderer.hideAllObj();
					}
					panel.layout.innerCt.dom.appendChild( self.__SearchResultRenderer.domElement );


					if(Ext.isEmpty(self.__AgSubRenderer)){
						self.__AgSubRenderer = new AgSubRenderer();
						self.__AgSubRenderer.domElement.style.position = 'absolute';
						self.__AgSubRenderer.domElement.style.left = '0px';
						self.__AgSubRenderer.domElement.style.top = '0px';
						self.__AgSubRenderer.domElement.style.zIndex = 100;
						self.__AgSubRenderer.domElement.style.marginRight = '4px';
						self.__AgSubRenderer.domElement.style.marginBottom = '0px';
						self.__AgSubRenderer.domElement.style.styleFloat = 'left';
						panel.layout.innerCt.dom.appendChild( self.__AgSubRenderer.domElement );
						var paths = ['static/obj/body.obj'];
						if(paths.length>0){
							if(self.__AgSubRenderer) self.__AgSubRenderer.loadObj(paths);
						}
					}
				},
				resize: function( panel, width, height, oldWidth, oldHeight, eOpts){

					self.__SearchResultRenderer._setSize(10,10);

					var $dom = $(panel.layout.innerCt.dom);
					width = $dom.width();
					height = $dom.height();
					self.__SearchResultRenderer.setSize(width,height);
				}
			}
		};

		var east_panel = {
			hidden: self.DEF_SEARCH_RESULT_LIST_HIDDEN,
			region: 'east',
			title: self.DEF_SEARCH_RESULT_LIST_LABEL,
			width: 350,
			minWidth: 350,
			collapsed: false,
			collapsible: false,
			hideCollapseTool: true,
			headerPosition: 'top',
			columnLines: true,
			split: true,
			xtype: 'gridpanel',
			id: self.DEF_SEARCH_RESULT_LIST_ID,
			store: Ext.data.StoreManager.lookup(AgDef.CONCEPT_TERM_STORE_ID),
			plugins: self.getBufferedRenderer({pluginId: self.DEF_SEARCH_RESULT_LIST_PLUGIN_ID}),
			viewConfig: {
				rowTpl: [
					'{%',
						'var dataRowCls = values.recordIndex === -1 ? "" : " ' + Ext.baseCSSPrefix + 'grid-data-row";',
					'%}',
					'<tr role="row" {[values.rowId ? ("id=\\"" + values.rowId + "\\"") : ""]} ',
						'data-boundView="{view.id}" ',
						'data-recordId="{record.internalId}" ',
						'data-recordIndex="{recordIndex}" ',
						'class="{[values.itemClasses.join(" ")]} {[values.rowClasses.join(" ")]}{[dataRowCls]}" ',
						'draggable="true"',
						'{rowAttr:attributes} tabIndex="-1">',
						'<tpl for="columns">',
							'{%',
								'parent.view.renderCell(values, parent.record, parent.recordIndex, xindex - 1, out, parent)',
							'%}',
						'</tpl>',
					'</tr>',
					{
						priority: 0
					}
				]
			},
			selModel: {
				mode: 'MULTI',
				listeners: {
				}
			},
			columns: [
				{ text: self.DEF_ID_LABEL,       dataIndex: AgDef.ID_DATA_FIELD_ID,      width: self.DEF_ID_COLUMN_WIDTH, hideable: false },
				{ text: self.DEF_NAME_LABEL,     dataIndex: AgDef.NAME_DATA_FIELD_ID,    flex: 1, hideable: false },
				{ text: self.DEF_SYNONYM_LABEL,  dataIndex: AgDef.SYNONYM_DATA_FIELD_ID, flex: 1, hideable: false, hidden: true  },
				{ text: self.DEF_FILENAME_LABEL, dataIndex: AgDef.OBJ_FILENAME_FIELD_ID, flex: 2, hideable: true },
				{
					text: self.DEF_COLOR_LABEL,
					dataIndex: AgDef.CONCEPT_DATA_COLOR_DATA_FIELD_ID,
					width: self.DEF_COLOR_COLUMN_WIDTH,
					hideable: false,
					renderer: function(value){
						return Ext.String.format('<div style="border:1px solid gray;background:{0};width:{1}px;height:{2}px;"> </div>',value,self.DEF_COLOR_COLUMN_WIDTH-22,24-11);
					}
				}
			],
			dockedItems: [{
				hidden: false,
				xtype: 'toolbar',
				dock: 'top',
				itemId: 'top',
				layout: {
					overflowHandler: 'Menu'
				},
				items:['->',{
					disabled: true,
					xtype: 'button',
					itemId: 'delete',
					iconCls: 'pallet_delete',
					handler: function(button,e){
						var gridpanel = button.up('gridpanel');
						var selModel = gridpanel.getSelectionModel();
						var records = selModel.getSelection();
						if(Ext.isEmpty(records)) return;
						var store = gridpanel.getStore();
						records.map(function(record){
							record.beginEdit();
							record.set(AgDef.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID,false);
							record.endEdit(false,[AgDef.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID]);
						});
						if(self.__SearchResultRenderer){
							self.__SearchResultRenderer.setObjProperties(getObjDataFromRecords(records));
							if(self.USE_SELECTION_RENDERER_BACKGROUND_COLOR_FACTOR) self.__SearchResultRenderer.setBackgroundColor(self.DEF_RENDERER_BACKGROUND_COLOR);
						}
						store.remove(records);
					}
				}]
			}],
			listeners: {
				afterrender: function(gridpanel, eOpts){
					var conceptStore = Ext.data.StoreManager.lookup(AgDef.CONCEPT_TERM_STORE_ID);
					var conceptSearchStore = Ext.data.StoreManager.lookup(AgDef.CONCEPT_TERM_SEARCH_STORE_ID);
					if(conceptSearchStore){
						conceptSearchStore.on({
							beforeload: function(store, operation, eOpts){
								conceptStore.removeAll();
								self.__SearchResultRenderer.hideAllObj();
							},
							load: function(store, records, successful, eOpts){
								if(successful && Ext.isArray(records) && records.length){

									var hash = {};
									hash[AgDef.LOCATION_HASH_SEARCH_KEY] = store.lastOptions.params[AgDef.LOCATION_HASH_SEARCH_KEY]
									self.setLocationHash(hash,true);

									var p = store.getProxy();
									p.extraParams = p.extraParams || {};
									var ids = Ext.Array.map(records,function(record){
										return record.get(AgDef.ID_DATA_FIELD_ID);;
									});
									var params = {};
									params[AgDef.LOCATION_HASH_IDS_KEY] = Ext.encode(ids);
									Ext.Ajax.abortAll();
									conceptStore.loadPage(1,{
										params: params,
										callback: function(records,operation,success){
											if(success){
												var selModel = gridpanel.getSelectionModel();
												self.__SearchResultRenderer.loadObj(getObjDataFromRecords(records,selModel),function(){
												});
											}else{
												var rawData = conceptStore.getProxy().getReader().rawData || {};
												if(rawData.success) return;
												console.log(rawData);
												var msg = 'An error occurred for some reason.';
												if(Ext.isString(rawData.msg) && rawData.msg.length) msg = rawData.msg;
												Ext.Msg.show({
													title: 'Search',
													msg: msg,
													buttons: Ext.Msg.OK,
													icon: Ext.Msg.ERROR
												});
											}
										}
									});
								}
								else if(!successful){
									var rawData = conceptSearchStore.getProxy().getReader().rawData;
									if(Ext.isObject(rawData)){
										if(rawData.success) return;
										console.log(rawData);
										var msg = 'An error occurred for some reason.';
										if(Ext.isString(rawData.msg) && rawData.msg.length) msg = rawData.msg;
										Ext.Msg.show({
											title: 'Search',
											msg: msg,
											buttons: Ext.Msg.OK,
											icon: Ext.Msg.ERROR
										});
									}

								}
							}
						});
					}
				},
				selectionchange: function( selModel, selected, eOpts ){

					var delete_button = this.down('toolbar#top').down('button#delete');
					delete_button.setDisabled(Ext.isEmpty(selected));

					if(Ext.isEmpty(self.__SearchResultRenderer)) return;

					var is_selected = false;
					if(Ext.isArray(selected) && selected.length) is_selected = true;
					self.__SearchResultRenderer.setObjProperties(getObjDataFromRecords(selModel.getStore().getRange(),selModel,is_selected));

					if(self.USE_SELECTION_RENDERER_BACKGROUND_COLOR_FACTOR){
						self.__SearchResultRenderer.setBackgroundColor(is_selected ? self.DEF_SELECTION_RENDERER_BACKGROUND_COLOR : self.DEF_RENDERER_BACKGROUND_COLOR);
					}else{
						self.__SearchResultRenderer.setBackgroundColor(self.DEF_RENDERER_BACKGROUND_COLOR);
					}
				}
			}
		};

		//layout:window
		var viewport_items = [{
			id: 'window-panel',
			bodyStyle: 'background:#aaa;',
			minHeight: 360,
			layout: 'border',
			dockedItems: view_dockedItems,
			defaultType: 'panel',
			items: [center_panel,east_panel],
			listeners: {
				afterrender: function(comp){

				},
				render: function(comp){
				},
				resize: function(comp,adjWidth,adjHeight,rawWidth,rawHeight){
				}
			}
		}];


		var viewport = Ext.create('Ext.container.Viewport', {
			id: 'main-viewport',
			layout: 'fit',
			items: viewport_items,
			listeners: {
				afterrender: function(viewport){
					var el = viewport.getEl();
					el.on({
						dragenter: function(event){
							if(event && event.stopEvent) event.stopEvent();
							return false;
						},
						dragover: function(event){
							if(event && event.stopEvent) event.stopEvent();
							return false;
						},
						drop: function(event){
							if(event && event.stopEvent) event.stopEvent();
							var dataTransfer;
							if(Ext.isObject(event)){
								if(event.browserEvent && event.browserEvent.dataTransfer){
									dataTransfer = event.browserEvent.dataTransfer;
								}else if(event.dataTransfer){
									dataTransfer = event.dataTransfer;
								}
							}
							var dropData = '';
							if(dataTransfer && dataTransfer.getData){
								dropData = dataTransfer.getData('text/plain');
							}
							if(Ext.isEmpty(dropData)) return;
							if(Ext.isString(dropData)){
								if(dropData.match(/^[\[\{].+[\]\}]$/)){
									try{dropData = Ext.decode(dropData);}catch(e){}
								}
							}else{
								return;
							}
							var field;
							if(Ext.isString(dropData)){
								field = Ext.getCmp(self.DEF_SEARCH_FORM_FIELD_ID);
								field.setValue(dropData);
							}else if(Ext.isObject(dropData)){
								if(dropData.id){
									field = Ext.getCmp(self.DEF_ID_FORM_FIELD_ID);
									field.setValue(dropData.id);
								}
								else if(dropData.name){
									field = Ext.getCmp(self.DEF_NAME_FORM_FIELD_ID);
									field.setValue(dropData.name);
								}
							}
							if(field){
								Ext.defer(function(){
									field.specialkeyENTER();
								},250);
							}
						}
					});

					var hash = self.getLocationHash();
					var hashId     = self.isEmpty(hash[AgDef.LOCATION_HASH_ID_KEY])     ? null : Ext.String.trim(hash[AgDef.LOCATION_HASH_ID_KEY]);
					var hashName   = self.isEmpty(hash[AgDef.LOCATION_HASH_NAME_KEY])   ? null : Ext.String.trim(hash[AgDef.LOCATION_HASH_NAME_KEY]);
					var hashSearch = self.isEmpty(hash[AgDef.LOCATION_HASH_SEARCH_KEY]) ? null : Ext.String.trim(hash[AgDef.LOCATION_HASH_SEARCH_KEY]);
					var field;
					if(hashSearch){
						field = Ext.getCmp(self.DEF_SEARCH_FORM_FIELD_ID);
						field.setValue(hashSearch);
					}
					if(hashName){
						field = Ext.getCmp(self.DEF_NAME_FORM_FIELD_ID);
						field.setValue(hashName);
					}
					if(hashId){
						field = Ext.getCmp(self.DEF_ID_FORM_FIELD_ID);
						field.setValue(hashId);
					}
					if(field){
						var e = new Ext.EventObjectImpl();
						e.keyCode = e.ENTER
						field.fireEvent('specialkey',field,e);
					}


				},
				beforedestroy: function(viewport){
				},
				destroy: function(viewport){
				},
				render: function(viewport){
				},
				resize: function(viewport,adjWidth,adjHeight,rawWidth,rawHeight){


				}
			}
		});
	},

	initContextmenu : function(){
		var self = this;
	},

	init : function(){
		var self = this;

		self.initBind();
		self.initExtJS();
		self.initStore();
		self.initDelayedTask();
		self.initTemplate();
		self.initComponent();
		self.initContextmenu();
	}
});
