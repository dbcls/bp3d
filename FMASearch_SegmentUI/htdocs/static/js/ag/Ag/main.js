var EventSource = window.EventSource || window.MozEventSource;
var useEventSource = false;
//if(EventSource) useEventSource = true;

var openAgRender = function(urlHashStr){
	return false;
};
//var Ag = Ag || {};

Ext.define('Ag.Main', {
	mixins: {
		observable: 'Ext.util.Observable'
	},
	config: {
	},
	constructor: function (config) {
		var self = this;
		self.__config = config || {};

		self.mixins.observable.constructor.call(self, self._config);
/*
		self.addEvents(
			'init',
//			'rotate',
//			'zoom'
		);
*/

		self.__IS_ELECTRON = (window.navigator.appVersion && window.navigator.appVersion.match(/\sElectron\//) ? true : false);

//		Ag.LocalStorage = new Ag.LocalStorage();

		self._init_defined();

	if(Ag.LocalStorage.exists(self.DEF_LOCALDB_RENDERER_OPTIONS_KEY)){
		self.loadRendererOptions();
	}else{
		self.saveRendererOptions();
	}

		self._init_override();
	},

	_init_defined : function(){
		var self = this;

		self.DEF_LOCALDB_PROVIDER_PREFIX = Ag.Def.LOCALDB_PREFIX+'bp3d-mng-';
		self.DEF_LOCALDB_RENDERER_OPTIONS_KEY = Ag.Def.LOCALDB_PREFIX+'fma-search-renderer-options';

		self.FORMAT_FORM_FIELD_ID = '{0}-{1}';

		self.DEF_VIEW_DOCITEMS_HIDDEN = self.__IS_ELECTRON;

		self.DEF_CONCEPT_INFO_TERM = Ag.Def.DEF_CONCEPT_INFO_TERM;	//'FMA';

		self.DEF_ID_LABEL = Ag.Def.LOCATION_HASH_ID_KEY;
		self.DEF_NAME_LABEL = Ag.Def.LOCATION_HASH_NAME_KEY;
		self.DEF_SYNONYM_LABEL = 'synonym';
		self.DEF_DEFINITION_LABEL = 'definition';


		self.DEF_CONCEPT_LABEL = 'Concept';
		self.DEF_CONCEPT_FORM_LABEL_WIDTH = 48;
		self.DEF_CONCEPT_INFO_FORM_FIELD_WIDTH = 74;
		self.DEF_CONCEPT_INFO_FORM_FIELD_XTYPE = 'combobox';
		self.DEF_CONCEPT_INFO_FORM_FIELD_ID = Ext.util.Format.format(self.FORMAT_FORM_FIELD_ID,self.DEF_CONCEPT_INFO_FORM_FIELD_XTYPE,'concept-info');

		self.DEF_CONCEPT_BUILD_FORM_FIELD_WIDTH = 256;
		self.DEF_CONCEPT_BUILD_FORM_FIELD_XTYPE = 'combobox';
		self.DEF_CONCEPT_BUILD_FORM_FIELD_ID = Ext.util.Format.format(self.FORMAT_FORM_FIELD_ID,self.DEF_CONCEPT_BUILD_FORM_FIELD_XTYPE,'concept-build');

		self.DEF_COLOR_LABEL = 'color';
		self.DEF_COLOR_COLUMN_WIDTH = Ag.Def.COLOR_COLUMN_WIDTH - 0;

		self.DEF_OPACITY_LABEL = 'opacity';
		self.DEF_OPACITY_COLUMN_WIDTH = 52;

		self.DEF_REMOVE_LABEL = 'remove';
		self.DEF_REMOVE_COLUMN_WIDTH = 52;

		self.DEF_PALLET_LABEL = 'pallet';
		self.DEF_DISTANCE_LABEL = 'distance(mm)';


		//segment renderer
		self.DEF_SELECTION_SEGMENT_RENDERER_PICKED_COLOR = '#FF0000';


		//temp renderer
		self.DEF_SELECTION_RENDERER_PICKED_COLOR = '#FF00FF';
		self.DEF_SELECTION_RENDERER_PICKED_COLOR_FACTOR = 0.5;
		self.DEF_SELECTION_RENDERER_PICKED_OTHER_OPACITY = 0.5;
		self.DEF_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR = -0.8;

		self.DEF_SELECTION_RENDERER_PICKED_FIRST_COLOR = '#FF00FF';	//第１選択色
		self.DEF_SELECTION_RENDERER_PICKED_FIRST_COLOR_FACTOR = 0.5;
		self.USE_SELECTION_RENDERER_PICKED_FIRST_COLOR = true;
		self.USE_SELECTION_RENDERER_PICKED_FIRST_COLOR_FACTOR = false;
		self.USE_SELECTION_RENDERER_PICKED_FIRST_COLOR_WIREFRAME = true;

		self.DEF_SELECTION_RENDERER_PICKED_SECOND_COLOR = '#FF9900';	//第２選択色
		self.DEF_SELECTION_RENDERER_PICKED_SECOND_COLOR_FACTOR = 0.5;
		self.USE_SELECTION_RENDERER_PICKED_SECOND_COLOR = true;
		self.USE_SELECTION_RENDERER_PICKED_SECOND_COLOR_FACTOR = false;
		self.USE_SELECTION_RENDERER_PICKED_SECOND_COLOR_WIREFRAME = true;

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

		self.DEF_RENDERER_GRID_USE = false;
		self.DEF_RENDERER_GRID_COLOR = '#00FF00';
		self.DEF_RENDERER_GRID_DIVISIONS = 10;
		self.DEF_RENDERER_GRID_SIZE = 1800;

		self.DEF_DOUBLE_CLICK_INTERVAL = 250;



		self.DEF_MATCH_LIST_DRAW = true;
		self.DEF_PALLET_DRAW = false;
		self.DEF_NEIGHBOR_SEARCH_PICK = false;
		self.DEF_SEGMENT_FILTER = 'SEG2ART_INSIDE';


		self.DEF_SELECTED_TAGS_KEEP_LIST_ADD = true;	//selected tags へのレコード追加時の動作。true:追加、false:置換
		self.DEF_SELECTED_TAGS_KEEP_LIST_REPLACE = false;	//selected tags へのレコード追加時の動作。true:追加、false:置換
		self.DEF_SELECTED_TAGS_KEEP_LIST = self.DEF_SELECTED_TAGS_KEEP_LIST_ADD;	//selected tags へのレコード追加時の動作。true:追加、false:置換

	},

	_init_override : function(){
		var self = this;
		Ext.each([
			'initBind',
			'initExtJS',
			'initStore',
			'initDelayedTask',
			'initTemplate',
			'initComponent',
			'initContextmenu',
		],function(func){
			if(Ext.isFunction(self[func])) self[func].apply(self);
		});
	},

	isEmpty : function(value){
		if(Ext.isEmpty(value) || (Ext.isString(value) && (value=='none' || value.length==0))){
			return true;
		}else{
			return false;
		}
	},

	getLocationHash : function(){
		var self = this;
		var hash = Ext.Object.fromQueryString(window.location.hash.substr(1)) || {};
/*
		if(hash.ci_id && !hash[Ag.Def.LOCATION_HASH_CIID_KEY]) hash[Ag.Def.LOCATION_HASH_CIID_KEY] = hash.ci_id;
		if(hash.cb_id && !hash[Ag.Def.LOCATION_HASH_CBID_KEY]) hash[Ag.Def.LOCATION_HASH_CBID_KEY] = hash.cb_id;
		if(hash.search && !hash[Ag.Def.LOCATION_HASH_NAME_KEY]) hash[Ag.Def.LOCATION_HASH_NAME_KEY] = hash.search;
		delete hash.ci_id;
		delete hash.cb_id;
		delete hash.search;
*/
		return hash;
	},

	getExtraParams : function(params){
		var self = this;

		params = params || {};

		var hash = {};

		if(self.DEF_MODEL_VERSION_RECORD && self.DEF_MODEL_VERSION_RECORD instanceof Ext.data.Model){
			hash[Ag.Def.LOCATION_HASH_MDID_KEY] = self.DEF_MODEL_VERSION_RECORD.get(Ag.Def.LOCATION_HASH_MDID_KEY);
			hash[Ag.Def.LOCATION_HASH_MVID_KEY] = self.DEF_MODEL_VERSION_RECORD.get(Ag.Def.LOCATION_HASH_MVID_KEY);
			hash[Ag.Def.LOCATION_HASH_MRID_KEY] = self.DEF_MODEL_VERSION_RECORD.get(Ag.Def.LOCATION_HASH_MRID_KEY);
			hash[Ag.Def.LOCATION_HASH_CIID_KEY] = self.DEF_MODEL_VERSION_RECORD.get(Ag.Def.LOCATION_HASH_CIID_KEY);
			hash[Ag.Def.LOCATION_HASH_CBID_KEY] = self.DEF_MODEL_VERSION_RECORD.get(Ag.Def.LOCATION_HASH_CBID_KEY);
			hash[Ag.Def.VERSION_STRING_FIELD_ID] = self.DEF_MODEL_VERSION_RECORD.get(Ag.Def.VERSION_STRING_FIELD_ID);
		}
		else{
			//
			//指定されているバージョンが使用不可の時、とりあえず、最初のレコードを使用する
			//
			var modelVersionStore = Ext.data.StoreManager.lookup('version-store');
			var record = modelVersionStore.getAt(0);
			if(record && record instanceof Ext.data.Model){
				hash[Ag.Def.LOCATION_HASH_MDID_KEY] = record.get(Ag.Def.LOCATION_HASH_MDID_KEY);
				hash[Ag.Def.LOCATION_HASH_MVID_KEY] = record.get(Ag.Def.LOCATION_HASH_MVID_KEY);
				hash[Ag.Def.LOCATION_HASH_MRID_KEY] = record.get(Ag.Def.LOCATION_HASH_MRID_KEY);
				hash[Ag.Def.LOCATION_HASH_CIID_KEY] = record.get(Ag.Def.LOCATION_HASH_CIID_KEY);
				hash[Ag.Def.LOCATION_HASH_CBID_KEY] = record.get(Ag.Def.LOCATION_HASH_CBID_KEY);
				hash[Ag.Def.VERSION_STRING_FIELD_ID] = record.get(Ag.Def.VERSION_STRING_FIELD_ID);

				self.DEF_MODEL_VERSION_RECORD = record;
				self.DEF_MODEL_VERSION_VALUE = Ext.util.Format.format(Ag.Def.FORMAT_MODEL_VERSION_VALUE, record.get(Ag.Def.LOCATION_HASH_MDID_KEY), record.get(Ag.Def.LOCATION_HASH_MVID_KEY));
				self.DEF_CONCEPT_BUILD_VALUE = Ext.util.Format.format(Ag.Def.FORMAT_CONCEPT_VALUE, record.get(Ag.Def.LOCATION_HASH_CIID_KEY), record.get(Ag.Def.LOCATION_HASH_CBID_KEY));
			}
		}

		if(self.DEF_MODEL_SEGMENT_RECORD && self.DEF_MODEL_SEGMENT_RECORD instanceof Ext.data.Model){
			hash['cities_ids'] = self.DEF_MODEL_SEGMENT_RECORD.get('cities_ids');
		}
		else{
			var segment_store = Ext.data.StoreManager.lookup('segment-list-store');
			var record = segment_store.getRootNode();
			if(record && record instanceof Ext.data.Model){
				hash['cities_ids'] = record.get('cities_ids');
			}
		}

		if(self.DEF_SEARCH_TARGET && Ext.isNumeric(self.DEF_SEARCH_TARGET)){
			hash['searchTarget'] = self.DEF_SEARCH_TARGET;
		}
		else{
			hash['searchTarget'] =  (Ext.getCmp('main-viewport').down('radiogroup#search-target').getValue()||{})['searchTarget'] || '2';
		}

		if(self.DEF_SEGMENT_FILTER && Ext.isNumeric(self.DEF_SEGMENT_FILTER)){
			hash['SEG2ART'] = self.DEF_SEGMENT_FILTER;
		}
		else{
			hash['SEG2ART'] =  Ext.getCmp('main-viewport').down('combobox#segment-filtering-combobox').getValue() || 'SEG2ART_INSIDE';
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

	loadRendererOptions : function(){
		var self = this;
		if(Ag.LocalStorage.exists(self.DEF_LOCALDB_RENDERER_OPTIONS_KEY)){
			var renderer_options = {};
			try{renderer_options = Ext.decode(Ag.LocalStorage.load(self.DEF_LOCALDB_RENDERER_OPTIONS_KEY))}catch(e){};
			Ext.Object.each(renderer_options, function(key, value){
				self[key] = value;
			});
		}
	},

	saveRendererOptions : function(){
		var self = this;
			var renderer_options = {};
			Ext.each([
				'DEF_SELECTION_RENDERER_PICKED_COLOR',
				'DEF_SELECTION_RENDERER_PICKED_COLOR_FACTOR',
				'DEF_SELECTION_RENDERER_PICKED_OTHER_OPACITY',
				'DEF_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR',

				'USE_SELECTION_RENDERER_PICKED_COLOR',
				'USE_SELECTION_RENDERER_PICKED_COLOR_FACTOR',
				'USE_SELECTION_RENDERER_PICKED_OTHER_OPACITY',
				'USE_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR',


				'DEF_SELECTION_RENDERER_PICKED_FIRST_COLOR',
				'DEF_SELECTION_RENDERER_PICKED_FIRST_COLOR_FACTOR',
				'USE_SELECTION_RENDERER_PICKED_FIRST_COLOR',
				'USE_SELECTION_RENDERER_PICKED_FIRST_COLOR_FACTOR',
				'USE_SELECTION_RENDERER_PICKED_FIRST_COLOR_WIREFRAME',


				'DEF_SELECTION_RENDERER_PICKED_SECOND_COLOR',
				'DEF_SELECTION_RENDERER_PICKED_SECOND_COLOR_FACTOR',
				'USE_SELECTION_RENDERER_PICKED_SECOND_COLOR',
				'USE_SELECTION_RENDERER_PICKED_SECOND_COLOR_FACTOR',
				'USE_SELECTION_RENDERER_PICKED_SECOND_COLOR_WIREFRAME',

				'DEF_RENDERER_BACKGROUND_COLOR',
				'USE_SELECTION_RENDERER_BACKGROUND_COLOR_FACTOR',
				'DEF_SELECTION_RENDERER_BACKGROUND_COLOR_FACTOR',
				'DEF_SELECTION_RENDERER_BACKGROUND_COLOR',

				'DEF_RENDERER_GRID_USE',
				'DEF_RENDERER_GRID_COLOR',
				'DEF_RENDERER_GRID_DIVISIONS',
				'DEF_RENDERER_GRID_SIZE',

//				'DEF_SELECTED_TAGS_KEEP_LIST',
			],function(key){
				renderer_options[key] = self[key];
			});
			Ag.LocalStorage.save(self.DEF_LOCALDB_RENDERER_OPTIONS_KEY,Ext.encode(renderer_options));
	}

});
