var EventSource = window.EventSource || window.MozEventSource;
var useEventSource = false;
//if(EventSource) useEventSource = true;

var openAgRender = function(urlHashStr){
	return false;
};

var AgApp = function(config){
	var self = this;
	self._config = config || {};

	self.DEF_UPLOAD_FILE_PAGE_SIZE = 25;

	self.DEF_LOCALDB_HASH_KEY = AgDef.LOCALDB_PREFIX+'bp3d-pallet-parts';
	self.DEF_LOCALDB_TREE_INFO = AgDef.LOCALDB_PREFIX+'bp3d-tree-info';
	self.DEF_LOCALDB_FOLDER_INFO = AgDef.LOCALDB_PREFIX+'art-folder-info';

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

	self.ART_TIMESTAMP_FORMAT = USE_OBJ_TIMESTAMP_COMPARISON_UNIT===USE_OBJ_TIMESTAMP_COMPARISON_UNIT_DATE ? self.FORMAT_DATE : self.FORMAT_DATE_TIME;
	self.ART_TIMESTAMP_WIDTH = USE_OBJ_TIMESTAMP_COMPARISON_UNIT===USE_OBJ_TIMESTAMP_COMPARISON_UNIT_DATE ? 67 : 112;

	self.DEF_RELATION = ['is_a','regional_part_of','constitutional_part_of','branch_of','tributary_of','member_of','systemic_part_of','lexicalsuper'/*,'tributary_of'*/];
	self.DEF_DIRECTION = ['up','down'];
	self.DEF_RELATION_HIDDEN = {
		'regional_part_of'      : false,
		'constitutional_part_of': false,
		'branch_of'             : true,
		'tributary_of'          : true,
		'member_of'             : true,
		'systemic_part_of'      : true,
		'lexicalsuper'          : false
		/*,'tributary_of'          : true*/
	};
	self.FORMAT_RELATIONS_PANEL_ID = '{0}_{1}';
	self.FORMAT_FORM_FIELD_ID = '{0}-{1}';
//	AgDef.FORMAT_CONCEPT_VALUE = '{0}-{1}';

	self.DEF_CONCEPT_INFO_TERM = 'FMA';
//	self.DEF_CONCEPT_BUILD_TERM = '3.2.1-inference';
	self.DEF_CONCEPT_BUILD_TERM = null;

	self.DEF_CONCEPT_INFO_VALUE = null;
	self.DEF_CONCEPT_BUILD_VALUE = null;

//	AgDef.LOCATION_HASH_SEARCH_KEY = 'query';
//	AgDef.LOCATION_HASH_NAME_KEY = 'name';
//	AgDef.LOCATION_HASH_ID_KEY = 'id';
//	AgDef.LOCATION_HASH_CIID_KEY = 'ci';
//	AgDef.LOCATION_HASH_CBID_KEY = 'cb';
	self.DEF_LOCATION_HASH_EXTENDHIERARCHY_KEY = 'extendHierarchy';

//	self.DEF_ID_LABEL = 'FMAID';
//	self.DEF_ID_FORM_LABEL_WIDTH = 44;
	self.DEF_ID_LABEL = AgDef.LOCATION_HASH_ID_KEY;
	self.DEF_ID_FORM_LABEL_WIDTH = 10;
	self.DEF_ID_FORM_FIELD_WIDTH = 97;
	self.DEF_ID_FORM_FIELD_XTYPE = 'textfield';
	self.DEF_ID_FORM_FIELD_VTYPE = 'fmaid';
	self.DEF_ID_FORM_FIELD_ID = Ext.util.Format.format(self.FORMAT_FORM_FIELD_ID,self.DEF_ID_FORM_FIELD_XTYPE,self.DEF_ID_LABEL);
//	AgDef.ID_DATA_FIELD_ID = AgDef.LOCATION_HASH_ID_KEY;

	self.DEF_NAME_LABEL = AgDef.LOCATION_HASH_NAME_KEY;
	self.DEF_NAME_FORM_LABEL_WIDTH = 32;
	self.DEF_NAME_FORM_FIELD_WIDTH = 228;
	self.DEF_NAME_FORM_FIELD_XTYPE = 'textfield';
	self.DEF_NAME_FORM_FIELD_VTYPE = 'fmaname';
	self.DEF_NAME_FORM_FIELD_ID = Ext.util.Format.format(self.FORMAT_FORM_FIELD_ID,self.DEF_NAME_FORM_FIELD_XTYPE,self.DEF_NAME_LABEL);
//	AgDef.NAME_DATA_FIELD_ID = AgDef.LOCATION_HASH_NAME_KEY;

	self.DEF_SYNONYM_LABEL = 'synonym';
//	AgDef.SYNONYM_DATA_FIELD_ID = self.DEF_SYNONYM_LABEL;

	self.DEF_DEFINITION_LABEL = 'definition';
//	AgDef.DEFINITION_DATA_FIELD_ID = self.DEF_DEFINITION_LABEL;

	self.DEF_CONCEPT_LABEL = 'Concept';
	self.DEF_CONCEPT_FORM_LABEL_WIDTH = 48;
	self.DEF_CONCEPT_INFO_FORM_FIELD_WIDTH = 74;
	self.DEF_CONCEPT_INFO_FORM_FIELD_XTYPE = 'combobox';
	self.DEF_CONCEPT_INFO_FORM_FIELD_ID = Ext.util.Format.format(self.FORMAT_FORM_FIELD_ID,self.DEF_CONCEPT_INFO_FORM_FIELD_XTYPE,'concept-info');
//	AgDef.CONCEPT_INFO_DATA_FIELD_ID = 'ci_id';

	self.DEF_CONCEPT_BUILD_FORM_FIELD_WIDTH = 256;
	self.DEF_CONCEPT_BUILD_FORM_FIELD_XTYPE = 'combobox';
	self.DEF_CONCEPT_BUILD_FORM_FIELD_ID = Ext.util.Format.format(self.FORMAT_FORM_FIELD_ID,self.DEF_CONCEPT_BUILD_FORM_FIELD_XTYPE,'concept-build');
//	AgDef.CONCEPT_BUILD_DATA_FIELD_ID = 'cb_id';

	self.DEF_SEARCH_LABEL = 'Search (AND)';
	self.DEF_SEARCH_FORM_FIELD_XTYPE = 'combobox';
	self.DEF_SEARCH_FORM_FIELD_VTYPE = 'fmaname';
	self.DEF_SEARCH_FORM_FIELD_ID = Ext.util.Format.format(self.FORMAT_FORM_FIELD_ID,self.DEF_SEARCH_FORM_FIELD_XTYPE,AgDef.LOCATION_HASH_SEARCH_KEY);

	self.DEF_SEARCH_ANY_MATCH_LABEL = 'partialMatch';
//	AgDef.SEARCH_ANY_MATCH_NAME = 'anyMatch';
	self.DEF_SEARCH_CASE_SENSITIVE_LABEL = 'caseSensitive';
//	AgDef.SEARCH_CASE_SENSITIVE_NAME = 'caseSensitive';

//	AgDef.TERM_ID_DATA_FIELD_ID = 'term_id';
//	AgDef.TERM_NAME_DATA_FIELD_ID = 'term_name';
//	AgDef.RELATION_TYPE_NAME = 'type';

//	AgDef.SNIPPET_ID_DATA_FIELD_ID = 'snippet_id';
//	AgDef.SNIPPET_NAME_DATA_FIELD_ID = 'snippet_name';
//	AgDef.SNIPPET_SYNONYM_DATA_FIELD_ID = 'snippet_synonym';

//	AgDef.CONCEPT_TERM_STORE_ID = 'conceptStore';
//	AgDef.CONCEPT_TERM_SEARCH_STORE_ID = 'conceptSearchStore';

	self.TITLE_UPLOAD_OBJECT = 'obj files';

	self.downloadObjectsTask = new Ext.util.DelayedTask();

	self.init();

};
window.AgApp.prototype.constructor = AgApp;

window.AgApp.prototype.getHiddenEditedGridColumn = function(aOpt){
	return true;
};

window.AgApp.prototype.getLocationHash = function(){
	var self = this;
	var hash = Ext.Object.fromQueryString(window.location.hash.substr(1)) || {};

	if(hash.ci_id && !hash[AgDef.LOCATION_HASH_CIID_KEY]) hash[AgDef.LOCATION_HASH_CIID_KEY] = hash.ci_id;
	if(hash.cb_id && !hash[AgDef.LOCATION_HASH_CBID_KEY]) hash[AgDef.LOCATION_HASH_CBID_KEY] = hash.cb_id;
	if(hash.search && !hash[AgDef.LOCATION_HASH_NAME_KEY]) hash[AgDef.LOCATION_HASH_NAME_KEY] = hash.search;
	delete hash.ci_id;
	delete hash.cb_id;
	delete hash.search;

	return hash;
};

window.AgApp.prototype.setLocationHash = function(hashObject){
	var self = this;
	var hash = Ext.apply(self.getLocationHash(),hashObject || {});
	Ext.Object.each(hash,function(key,value){
		if(Ext.isEmpty(value)) delete hash[key];
	});

	var combobox = Ext.getCmp(self.DEF_CONCEPT_BUILD_FORM_FIELD_ID);
	var record = combobox.findRecordByValue(combobox.getValue());
	if(record){
		hash[AgDef.LOCATION_HASH_CIID_KEY] = record.get(AgDef.CONCEPT_INFO_DATA_FIELD_ID);
		hash[AgDef.LOCATION_HASH_CBID_KEY] = record.get(AgDef.CONCEPT_BUILD_DATA_FIELD_ID);
	}

	window.location.hash = Ext.Object.toQueryString(hash);
//	Ext.getCmp(self.DEF_NAME_FORM_FIELD_ID).setValue(hash[AgDef.LOCATION_HASH_NAME_KEY ]);
};

window.AgApp.prototype.getLocationHashName = function(hash){
	var self = this;
	hash = hash || self.getLocationHash();
	return hash[AgDef.LOCATION_HASH_NAME_KEY];
};

window.AgApp.prototype.setLocationHashName = function(value){
	var self = this;
	var hash = {};
	hash[AgDef.LOCATION_HASH_SEARCH_KEY] = '';
	hash[AgDef.LOCATION_HASH_NAME_KEY] = '';
	hash[AgDef.LOCATION_HASH_ID_KEY] = '';
	hash[AgDef.LOCATION_HASH_NAME_KEY] = (value||'').trim();
	self.setLocationHash(hash);
};

window.AgApp.prototype.getLocationHashID = function(hash){
	var self = this;
	hash = hash || self.getLocationHash();
	return hash[AgDef.LOCATION_HASH_ID_KEY];
};

window.AgApp.prototype.setLocationHashID = function(value){
	var self = this;
	var hash = {};
	hash[AgDef.LOCATION_HASH_SEARCH_KEY] = '';
	hash[AgDef.LOCATION_HASH_NAME_KEY] = '';
	hash[AgDef.LOCATION_HASH_ID_KEY] = (value||'').trim();
	self.setLocationHash(hash);
};

window.AgApp.prototype.getLocationHashExtendHierarchy = function(hash){
	var self = this;
	hash = hash || self.getLocationHash();
	return hash[self.DEF_LOCATION_HASH_EXTENDHIERARCHY_KEY]==='true';
};

window.AgApp.prototype.setLocationHashExtendHierarchy = function(value){
	var self = this;
	var hash = {};
	if(Ext.isEmpty(value)){
		value = '';
	}else{
		if(Ext.isString(value)) value = value==='true';
		if(Ext.isNumber(value)) value = value ? true : false;
		if(!value) value = '';
	}
	hash[self.DEF_LOCATION_HASH_EXTENDHIERARCHY_KEY] = value;
	self.setLocationHash(hash);
};

window.AgApp.prototype.getEmptyRecord = function(){
	var self = this;
	return Ext.create(Ext.data.StoreManager.lookup(AgDef.CONCEPT_TERM_STORE_ID).model.getName(),{});
};

window.AgApp.prototype.setLastRecord = function(record){
	var self = this;
	self.__lastRecord = record && record.copy ? record.copy() : self.getEmptyRecord();
//	$(window).trigger('updatelastrecord',[self.__lastRecord.getData()]);
//	if(window.postMessage) window.postMessage(self.__lastRecord.getData(),window.location.origin);
//	if(window.postMessage) window.postMessage({type:'updatelastrecord',data:self.__lastRecord.getData()},'http://tokyogw.bits.cc/');
	if(window.postMessage) window.postMessage({type:'updatelastrecord',data:self.__lastRecord.getData()},window.location.origin);
};

window.AgApp.prototype.getLastRecord = function(){
	var self = this;
	return self.__lastRecord || self.getEmptyRecord();
};

window.AgApp.prototype.loadRecord = function(id){
	var self = this;

	Ext.getCmp('window-panel').setLoading(true);
	Ext.Ajax.abortAll();
	var store = Ext.data.StoreManager.lookup(AgDef.CONCEPT_TERM_STORE_ID);
	store.loadPage(1,{
		params: {
			id: id
		},
		callback: function(records,operation,success){
			Ext.getCmp('window-panel').setLoading(false);
			if(!success) return;
			if(records.length>1){
			}else{
				var record = records.shift() || self.getEmptyRecord();
				Ext.getCmp(self.DEF_NAME_FORM_FIELD_ID).setValue(record.get(AgDef.NAME_DATA_FIELD_ID));
				self.setLastRecord(record);
//											field.setValue(record.get(AgDef.ID_DATA_FIELD_ID));
				self.initSubStatusPanel(record);
				self._updateFiled(record);
				if(Ext.isEmpty(record.get(AgDef.ID_DATA_FIELD_ID))){
					Ext.Msg.show({
						title: Ext.util.Format.format('{0}',AgLang.title),
						msg: Ext.util.Format.format('Unknown id [{0}]',id),
						buttons: Ext.Msg.OK,
						icon: Ext.Msg.ERROR,
						fn: function(buttonId,text,opt){
						}
					});
				}
			}
		}
	});
};

window.AgApp.prototype.isEmpty = function(value){
	if(Ext.isEmpty(value) || (Ext.isString(value) && (value=='none' || value.length==0))){
		return true;
	}else{
		return false;
	}
};

window.AgApp.prototype.initTemplate = function(){
	var self = this;
	self.__relationsTpl = new Ext.XTemplate(
		'<table class="relations"><tbody>',
		'<tpl for=".">',
			'<tr class="term">',
				'<td class="'+AgDef.ID_DATA_FIELD_ID+'" valign="top"><label class="'+AgDef.ID_DATA_FIELD_ID+
				'<tpl if="values.'+AgDef.IS_SHAPE_FIELD_ID+' == true">',
					' is_shape',
				'</tpl>',
				'<tpl if="values.'+AgDef.IS_MAPED_FIELD_ID+' == true">',
					' is_maped',
				'</tpl>',
				'<tpl if="values.'+AgDef.IS_CURRENT_FIELD_ID+' == true">',
					' is_current',
				'</tpl>',
				'">{'+AgDef.ID_DATA_FIELD_ID+'}</label></td>',
				'<td class="separator" valign="top"><label class="separator" unselectable="on">:</label></td>',
				'<td class="'+AgDef.NAME_DATA_FIELD_ID+'" valign="top"><a class="search '+AgDef.NAME_DATA_FIELD_ID+'" href="#" data-'+AgDef.ID_DATA_FIELD_ID+'="{'+AgDef.ID_DATA_FIELD_ID+'}">{'+AgDef.NAME_DATA_FIELD_ID+'}</a></td>',
			'</tr>',
		'</tpl>',
		'</tbody></table>'
	);
/*
	self.__hierarchyCenterTpl = new Ext.XTemplate(
		'<table width=100% height=100% class="hierarchy-center draggable" draggable="true"><tbody><tr><td align=center valign=center>',
			'<table class="draggable-data"><tbody>',
			'<tpl if="this.isEmpty(values.'+AgDef.ID_DATA_FIELD_ID+') == false">',
				'<tr>',
					'<th align="left" valign=top class="'+AgDef.ID_DATA_FIELD_ID+'"><label class="'+AgDef.ID_DATA_FIELD_ID+'">'+self.DEF_ID_LABEL+'</label></th>',
					'<td valign=top class="separator"><label class="separator" unselectable="on">:</label></td>',
					'<td class="'+AgDef.ID_DATA_FIELD_ID+'"><label class="'+AgDef.ID_DATA_FIELD_ID+
					'<tpl if="values.'+AgDef.IS_SHAPE_FIELD_ID+' == true">',
						' is_shape',
					'</tpl>',
					'<tpl if="values.'+AgDef.IS_MAPED_FIELD_ID+' == true">',
						' is_maped',
					'</tpl>',
					'<tpl if="values.'+AgDef.IS_CURRENT_FIELD_ID+' == true">',
						' is_current',
					'</tpl>',
					'">{'+AgDef.ID_DATA_FIELD_ID+'}</label></td>',
				'</tr>',
			'</tpl>',
			'<tpl if="this.isEmpty(values.'+AgDef.NAME_DATA_FIELD_ID+') == false">',
				'<tr>',
					'<th align="left" valign=top class="'+AgDef.NAME_DATA_FIELD_ID+'"><label class="'+AgDef.NAME_DATA_FIELD_ID+'">'+self.DEF_NAME_LABEL+'</label></th>',
					'<td valign=top class="separator"><label class="separator" unselectable="on">:</label></td>',
					'<td class="'+AgDef.NAME_DATA_FIELD_ID+'"><label class="'+AgDef.NAME_DATA_FIELD_ID+'">{'+AgDef.NAME_DATA_FIELD_ID+'}</label></td>',
				'</tr>',
			'</tpl>',
			'<tpl if="this.isEmpty(values.'+AgDef.SYNONYM_DATA_FIELD_ID+') == false">',
				'<tr>',
					'<th align="left" valign=top class="'+AgDef.SYNONYM_DATA_FIELD_ID+'"><label class="'+AgDef.SYNONYM_DATA_FIELD_ID+'">'+self.DEF_SYNONYM_LABEL+'</label></th>',
					'<td valign=top class="separator"><label class="separator" unselectable="on">:</label></td>',
					'<td class="'+AgDef.SYNONYM_DATA_FIELD_ID+'">',
						'<tpl for="values.'+AgDef.SYNONYM_DATA_FIELD_ID+'">',
							'<div style="margin-top:1px;margin-bottom:2px;"><label class="'+AgDef.SYNONYM_DATA_FIELD_ID+'">{.}</label></div>',
						'</tpl>',
					'</td>',
				'</tr>',
			'</tpl>',
			'<tpl if="this.isEmpty(values.'+AgDef.DEFINITION_DATA_FIELD_ID+') == false">',
				'<tr>',
					'<th align="left" valign=top class="'+AgDef.DEFINITION_DATA_FIELD_ID+'"><label class="'+AgDef.DEFINITION_DATA_FIELD_ID+'">'+self.DEF_DEFINITION_LABEL+'</label></th>',
					'<td valign=top class="separator"><label class="separator" unselectable="on">:</label></td>',
					'<td class="'+AgDef.DEFINITION_DATA_FIELD_ID+'"><label class="'+AgDef.DEFINITION_DATA_FIELD_ID+'">{'+AgDef.DEFINITION_DATA_FIELD_ID+'}</label></td>',
				'</tr>',
			'</tpl>',
			'</tbody></table>',
		'</td></tr></tbody></table>',
		{
			isEmpty : function(val){
				return Ext.isEmpty(val);
			}
		}
	);
*/
	self.__hierarchyCenterTpl = new Ext.XTemplate(
		'<table width=100% height=100% class="hierarchy-center draggable" draggable="true"><tbody><tr><td align=center valign=center>',
			'<table class="draggable-data"><tbody>',
			'<tpl if="this.isEmpty(values.'+AgDef.ID_DATA_FIELD_ID+') == false">',
				'<tr>',
					'<th align="left" valign=top class="'+AgDef.ID_DATA_FIELD_ID+'"><label class="'+AgDef.ID_DATA_FIELD_ID+'">'+self.DEF_ID_LABEL+'</label></th>',
					'<td valign=top class="separator"><label class="separator" unselectable="on">:</label></td>',
					'<td class="'+AgDef.ID_DATA_FIELD_ID+'"><label class="'+AgDef.ID_DATA_FIELD_ID,
					'<tpl if="values.'+AgDef.IS_SHAPE_FIELD_ID+' == true">',
						' is_shape',
					'</tpl>',
					'<tpl if="values.'+AgDef.IS_MAPED_FIELD_ID+' == true">',
						' is_maped',
					'</tpl>',
					'<tpl if="values.'+AgDef.IS_CURRENT_FIELD_ID+' == true">',
						' is_current',
					'</tpl>',
					'">{'+AgDef.ID_DATA_FIELD_ID+'}</label></td>',
				'</tr>',
			'</tpl>',
			'<tpl if="this.isEmpty(values.'+AgDef.NAME_DATA_FIELD_ID+') == false">',
				'<tr>',
					'<th align="left" valign=top class="'+AgDef.NAME_DATA_FIELD_ID+'"><label class="'+AgDef.NAME_DATA_FIELD_ID+'">'+self.DEF_NAME_LABEL+'</label></th>',
					'<td valign=top class="separator"><label class="separator" unselectable="on">:</label></td>',
					'<td class="'+AgDef.NAME_DATA_FIELD_ID+'"><label class="'+AgDef.NAME_DATA_FIELD_ID+'">{'+AgDef.NAME_DATA_FIELD_ID+'}</label></td>',
				'</tr>',
			'</tpl>',
			'<tpl if="this.isEmpty(values.'+AgDef.CDS_DATA_FIELD_ID+') == false">',
				'<tr>',
					'<th align="left" valign=top class="'+AgDef.SYNONYM_DATA_FIELD_ID+'"><label class="'+AgDef.SYNONYM_DATA_FIELD_ID+'">'+self.DEF_SYNONYM_LABEL+'</label></th>',
					'<td valign=top class="separator"><label class="separator" unselectable="on">:</label></td>',
					'<td class="'+AgDef.SYNONYM_DATA_FIELD_ID+'">',
						'<tpl for="values.'+AgDef.CDS_DATA_FIELD_ID+'">',
							'<div style="margin-top:1px;margin-bottom:2px;"><label class="'+AgDef.SYNONYM_DATA_FIELD_ID,
							'<tpl if="values.'+AgDef.CDS_ADDED_AUTO_DATA_FIELD_ID+' == true &amp;&amp; values.'+AgDef.CDS_ADDED_DATA_FIELD_ID+' == true">',
								' is_added_auto',
							'</tpl>',
							'<tpl if="values.'+AgDef.CDS_ADDED_AUTO_DATA_FIELD_ID+' == false &amp;&amp; values.'+AgDef.CDS_ADDED_DATA_FIELD_ID+' == true">',
								' is_added',
							'</tpl>',
							'">{'+AgDef.CS_NAME_DATA_FIELD_ID+'}</label></div>',
						'</tpl>',
					'</td>',
				'</tr>',
			'</tpl>',
			'<tpl if="this.isEmpty(values.'+AgDef.DEFINITION_DATA_FIELD_ID+') == false">',
				'<tr>',
					'<th align="left" valign=top class="'+AgDef.DEFINITION_DATA_FIELD_ID+'"><label class="'+AgDef.DEFINITION_DATA_FIELD_ID+'">'+self.DEF_DEFINITION_LABEL+'</label></th>',
					'<td valign=top class="separator"><label class="separator" unselectable="on">:</label></td>',
					'<td class="'+AgDef.DEFINITION_DATA_FIELD_ID+'"><label class="'+AgDef.DEFINITION_DATA_FIELD_ID+'">{'+AgDef.DEFINITION_DATA_FIELD_ID+'}</label></td>',
				'</tr>',
			'</tpl>',
			'</tbody></table>',
		'</td></tr></tbody></table>',
		{
			isEmpty : function(val){
				return Ext.isEmpty(val);
			}
		}
	);
};

window.AgApp.prototype.initSubStatusPanel = function(record){
	var self = this;
	record = record || self.getEmptyRecord();
	var id = record.get(AgDef.ID_DATA_FIELD_ID);
	const re = new RegExp(/^FMA:*([0-9]+)\-[A-Z]$/);
	var disable = false;
	if(Ext.isString(id) && re.test(id)){
		disable = true;
	}
	var panel = Ext.getCmp('sub_status_panel');
	if(panel){
//		var b = panel.down('button[toggleGroup="sub"][pressed=true]');
		if(Ext.isArray(Ext.ag.Data.concept_art_map_part)){
			Ext.Array.each(Ext.ag.Data.concept_art_map_part, function(p){
				if(Ext.isString(p['crl_name']) && p['crl_name'].length>0){
					var b = panel.down('button#sub-'+p['cmp_abbr']);
					if(b){
						b.setDisabled(disable);
						if(b.pressed){
							b.suspendEvents(false);
							b.toggle(false,true);
							b.resumeEvents();
						}
					}
				}
			});
		}
		var textfield = panel.down('textfield#sub'+AgDef.NAME_DATA_FIELD_ID);
		if(textfield){
			textfield.setDisabled(true);
			textfield.suspendEvents(false);
			textfield.setValue('');
			textfield.resumeEvents();
		}
		var button = panel.down('button#submit');
		if(button){
			button.setDisabled(true);
		}
	}
}

window.AgApp.prototype._updateFiledData = function(id,record){
	var self = this;
	record = record || self.getEmptyRecord();
//	var data = record.raw || {};
	var data = record.getData() || {};

	var panel = Ext.getCmp(id);
	if(panel){
//				console.log(id);
		if(panel.items.length){
			if(!self.getLocationHashExtendHierarchy()){
				var c_panel = panel.items.getAt(0);
//						console.log(c_panel.id);
				panel.getLayout().setActiveItem(c_panel);
				self.__relationsTpl.overwrite(c_panel.body, data[id] || []);
				c_panel.updateLayout();
				if(Ext.isEmpty(data[id])){
					c_panel.body.setStyle({overflow:'hidden'});
				}else{
					c_panel.body.setStyle({overflow:'auto'});
				}
			}else{
				var c_panel = panel.items.getAt(1);
//						console.log(c_panel.id);
				panel.getLayout().setActiveItem(c_panel);
				var c_store = c_panel.getStore();
				if(!c_store.isLoading()){
//							var c_proxy = c_store.getProxy();
//							c_proxy.extraParams = c_proxy.extraParams || {};
					c_store.load({
						params: {
							id: data.id
						},
						callback: function(records,operation,success){
							if(Ext.isEmpty(records)){
								var c_panel = panel.items.getAt(0);
								panel.getLayout().setActiveItem(c_panel);
								c_panel.body.update();
								c_panel.body.setStyle({overflow:'hidden'});
								c_panel.updateLayout();
							}else{
								panel.getLayout().setActiveItem(panel.items.getAt(1));
							}
							panel.updateLayout();
//								console.log(panel.getLayout().getActiveItem().id,records);
						}
					});
				}
			}
		}else{
			self.__relationsTpl.overwrite(panel.body, data[id] || []);
		}
		panel.updateLayout();
	}
};

window.AgApp.prototype._updateFiled = function(record){
	var self = this;

	record = record || self.getEmptyRecord();
	var data = record.raw || {};

	var id = record.get(AgDef.ID_DATA_FIELD_ID);
	var name = record.get(AgDef.NAME_DATA_FIELD_ID);
	if(id && name){
		document.title = Ext.util.Format.format('{0} [{1}] {2}',AgLang.title,id,name);
	}else{
		document.title = Ext.util.Format.format('{0}',AgLang.title);
	}

//	var hash = self.getLocationHash();

	self.DEF_RELATION.forEach(function(relation){
		self.DEF_DIRECTION.forEach(function(direction){
			var id = Ext.util.Format.format(self.FORMAT_RELATIONS_PANEL_ID,relation,direction);
			self._updateFiledData(id,record);
/*
			var panel = Ext.getCmp(id);
			if(panel){
//				console.log(id);
				if(panel.items.length){
					if(!self.getLocationHashExtendHierarchy()){
						var c_panel = panel.items.getAt(0);
//						console.log(c_panel.id);
						panel.getLayout().setActiveItem(c_panel);
						self.__relationsTpl.overwrite(c_panel.body, data[id] || []);
						c_panel.updateLayout();
						if(Ext.isEmpty(data[id])){
							c_panel.body.setStyle({overflow:'hidden'});
						}else{
							c_panel.body.setStyle({overflow:'auto'});
						}
					}else{
						var c_panel = panel.items.getAt(1);
//						console.log(c_panel.id);
						panel.getLayout().setActiveItem(c_panel);
						var c_store = c_panel.getStore();
						if(!c_store.isLoading()){
//							var c_proxy = c_store.getProxy();
//							c_proxy.extraParams = c_proxy.extraParams || {};
							c_store.load({
								params: {
									id: data.id
								},
								callback: function(records,operation,success){
									if(Ext.isEmpty(records)){
										var c_panel = panel.items.getAt(0);
										panel.getLayout().setActiveItem(c_panel);
										c_panel.body.update();
										c_panel.body.setStyle({overflow:'hidden'});
										c_panel.updateLayout();
									}else{
										panel.getLayout().setActiveItem(panel.items.getAt(1));
									}
									panel.updateLayout();
	//								console.log(panel.getLayout().getActiveItem().id,records);
								}
							});
						}
					}
				}else{
					self.__relationsTpl.overwrite(panel.body, data[id] || []);
				}
				panel.updateLayout();
			}
*/
		});
	});

	var panel = Ext.getCmp('hierarchy_center');
	self.__hierarchyCenterTpl.overwrite(panel.body, data);

	Ext.query('table.relations label.separator').forEach(function(elem){
		Ext.get(elem).unselectable();
	});
	Ext.query('table.hierarchy-center label.separator').forEach(function(elem){
		Ext.get(elem).unselectable();
	});

	panel.updateLayout();
};

window.AgApp.prototype.initBind = function(){
	var self = this;

	self._hashChange = Ext.bind(function(e){
//		console.log('hashchange',window.location.hash.substr(1));
		var self = this;
		Ext.defer(function(){
//			var update_content = false;
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
//						update_content = true;
					}
				}
			}

			var tbbutton_single = Ext.getCmp('hierarchy-display-options-single');
			var tbbutton_extended = Ext.getCmp('hierarchy-display-options-extended');
			if(tbbutton_single && tbbutton_extended){
				if(self.getLocationHashExtendHierarchy()){
//					if(!tbbutton_extended.pressed){
						tbbutton_extended.toggle(true,false);
//					}
				}else{
//					if(!tbbutton_single.pressed){
						tbbutton_single.toggle(true,false);
//					}
				}
			}

			var hashId     = self.isEmpty(hash[AgDef.LOCATION_HASH_ID_KEY])     ? null : Ext.String.trim(hash[AgDef.LOCATION_HASH_ID_KEY]);
			var hashName   = self.isEmpty(hash[AgDef.LOCATION_HASH_NAME_KEY])   ? null : Ext.String.trim(hash[AgDef.LOCATION_HASH_NAME_KEY]);
			var hashSearch = self.isEmpty(hash[AgDef.LOCATION_HASH_SEARCH_KEY]) ? null : Ext.String.trim(hash[AgDef.LOCATION_HASH_SEARCH_KEY]);
			var field;
			if(hashSearch){
				field = Ext.getCmp(self.DEF_SEARCH_FORM_FIELD_ID);
				if(hashSearch == field.getValue()){
//					field = undefined;
				}else{
					field.setValue(hashSearch);
				}
			}
			if(hashName){
				field = Ext.getCmp(self.DEF_NAME_FORM_FIELD_ID);
				if(hashName == field.getValue()){
//					field = undefined;
				}else{
					field.setValue(hashName);
				}
			}
			if(hashId){
				field = Ext.getCmp(self.DEF_ID_FORM_FIELD_ID);
				if(hashId == field.getValue()){
//					field = undefined;
				}else{
					field.setValue(hashId);
				}
			}
//			console.log(field,update_content);
//			if(!field && update_content){
//				field = Ext.getCmp(self.DEF_ID_FORM_FIELD_ID);
//			}
			if(field){
				field.specialkeyENTER();
			}
		},250);
	},self);

	$(window).on('hashchange',self._hashChange);

	$(document).on('click','a.search',function(e){
//		console.log($(this).text());
//		self.setLocationHashName($(this).text());

//		var id_text = $(this).closest('tr.term').find('label.id').text();
		var id_text = $(this).attr('data-'+AgDef.ID_DATA_FIELD_ID);
		if(Ext.isString(id_text)) id_text = id_text.trim();
		if(Ext.isEmpty(id_text)){
			self.setLocationHashName($(this).text());
		}else{
			self.setLocationHashID(id_text);
/*
			var field = Ext.getCmp(self.DEF_ID_FORM_FIELD_ID);
			field.setValue(id_text);
			var e = new Ext.EventObjectImpl();
			e.keyCode = e.ENTER
			field.fireEvent('specialkey',field,e);
*/
		}
		return false;
	});

//	$(document).on('dragstart','table.draggable',function(e){
	$(document).on('dragstart','*[draggable]',function(e){
		e.originalEvent.dataTransfer.effectAllowed = 'copy';
		if(Ext.getCmp('dragtype-url').getValue()){
			e.originalEvent.dataTransfer.setData('text/plain', window.location.href);
		}
		else{
//			console.log(this.nodeName);
			var all_text_datas = [];
			if(this.nodeName=='TABLE'){
/*
				$(this).find('table>tbody>tr').each(function(){
					var text_datas = [];
					$(this).find('th,td').each(function(){
						$(this).find('label').each(function(){
							text_datas.push($(this).text());
						});
					});
					all_text_datas.push(text_datas.join("\t"));
				});
*/
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
				});
				all_text_datas.push(text_datas.join("\t"));
				e.originalEvent.dataTransfer.setData('text/plain', all_text_datas.join("\n"));
			}
			else{
				all_text_datas.push($(this).text());
				e.originalEvent.dataTransfer.setData('text/plain', all_text_datas.join("\n"));
			}
//			e.originalEvent.dataTransfer.setData('text/plain', all_text_datas.join("\n"));
		}
//		e.preventDefault();
		e.stopPropagation();
	});

	$(document).on('mouseover','*[draggable]',function(e){	//mouseenter
//		$('.draggable-hover').removeClass('draggable-hover');
		$(this).addClass('draggable-hover');
		e.preventDefault();
		e.stopPropagation();
	});
	$(document).on('mouseout','*[draggable]',function(e){	//mouseleave
//		$('.draggable-hover').removeClass('draggable-hover');
		$(this).removeClass('draggable-hover');
		e.preventDefault();
		e.stopPropagation();
	});
};

window.AgApp.prototype.initDelayedTask = function(){
	var self = this;
};

window.AgApp.prototype.initExtJS = function(){
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
};

window.AgApp.prototype.getExtraParams = function(params){
	var self = this;

	params = params || {};
//	if(Ext.isEmpty(params.current_datas)) params.current_datas = 1;

	var ci_id;
	var cb_id;

	var field = Ext.getCmp(self.DEF_CONCEPT_BUILD_FORM_FIELD_ID);
	if(field && field.rendered){
		try{
			var record = field.findRecordByValue(field.getValue());
			if(record){
				ci_id = record.get(AgDef.CONCEPT_INFO_DATA_FIELD_ID);
				cb_id = record.get(AgDef.CONCEPT_BUILD_DATA_FIELD_ID);
			}else{
				return undefined;
			}
		}catch(e){
			if(!field.isHidden()){
				console.error(e);
				return undefined;
			}
		}
	}else{
		return undefined;
	}

	var hash = {};
	hash[AgDef.LOCATION_HASH_CIID_KEY] = ci_id;
	hash[AgDef.LOCATION_HASH_CBID_KEY] = cb_id;
	return hash;
};

window.AgApp.prototype.beforeloadStore = function(store){
	var self = this;

	var extraParams = self.getExtraParams() || {};
//	var extraParams = self.getExtraParams();
	if(Ext.isEmpty(extraParams)) return false;

	var p = store.getProxy();
	p.extraParams = p.extraParams || {};
	p.extraParams = Ext.apply({},extraParams,p.extraParams);

	return true;
};

window.AgApp.prototype.getBufferedRenderer = function(args){
	var self = this;
	args = Ext.apply({},args||{},{
		pluginId: 'bufferedrenderer',
		trailingBufferZone: 20,
		leadingBufferZone: 50
	});
	return Ext.create('Ext.grid.plugin.BufferedRenderer', args);
};

window.AgApp.prototype.initComponent = function(){
	var self = this;

	var idPrefix = Ext.id()+'-';
	var existingAttributeStoreId = idPrefix+'existingAttributeStore';
//	var attributeStoreId = idPrefix+'attributeStore';

	var conceptInfoStore = Ext.data.StoreManager.lookup('conceptInfoStore');
	var conceptInfoIdx = conceptInfoStore.findBy(function(record){
		return record.get('ci_name')===self.DEF_CONCEPT_INFO_TERM;
	});
	if(conceptInfoIdx>=0){
		var record = conceptInfoStore.getAt(conceptInfoIdx);
		if(record) self.DEF_CONCEPT_INFO_VALUE = record.get(AgDef.CONCEPT_INFO_DATA_FIELD_ID);
//		console.log(self.DEF_CONCEPT_INFO_VALUE);
	}

	var conceptBuildStore = Ext.data.StoreManager.lookup('conceptBuildStore');
	var conceptBuildIdx = conceptBuildStore.findBy(function(record){
		return record.get('ci_name')===self.DEF_CONCEPT_INFO_TERM && record.get('cb_name')===self.DEF_CONCEPT_BUILD_TERM;
	});
	if(conceptBuildIdx>=0){
		var record = conceptBuildStore.getAt(conceptBuildIdx);
		if(record) self.DEF_CONCEPT_BUILD_VALUE = Ext.util.Format.format(AgDef.FORMAT_CONCEPT_VALUE, record.get(AgDef.CONCEPT_INFO_DATA_FIELD_ID), record.get(AgDef.CONCEPT_BUILD_DATA_FIELD_ID));
//		console.log(self.DEF_CONCEPT_BUILD_VALUE);
	}

	var view_dockedItems = [{
		hidden: false,
		xtype: 'toolbar',
		dock: 'top',
		layout: {
			overflowHandler: 'Menu'
		},
		items:[{
//			hidden: conceptInfoStore.getCount()<=1 ? true : false,
			id: self.DEF_CONCEPT_INFO_FORM_FIELD_ID,
			fieldLabel: self.DEF_CONCEPT_LABEL,
			labelWidth: self.DEF_CONCEPT_FORM_LABEL_WIDTH,
			width: self.DEF_CONCEPT_FORM_LABEL_WIDTH+self.DEF_CONCEPT_INFO_FORM_FIELD_WIDTH,
			xtype: self.DEF_CONCEPT_INFO_FORM_FIELD_XTYPE,
			editable: false,
			queryMode: 'local',
			displayField: 'display',
			valueField: 'value',
//			value: Ext.isEmpty(self.DEF_CONCEPT_BUILD_VALUE) ? conceptBuildStore.getAt(0).get('value') : self.DEF_CONCEPT_BUILD_VALUE,
			store: conceptInfoStore,
			listeners: {
				afterrender: function(combobox, eOpts){
					var hash = self.getLocationHash();
					var value;
					if(Ext.isEmpty(hash[AgDef.LOCATION_HASH_CIID_KEY])){
						value = Ext.isEmpty(self.DEF_CONCEPT_INFO_VALUE) ? combobox.getStore().getAt(0).get('value') : self.DEF_CONCEPT_INFO_VALUE;
					}else{
						value = hash[AgDef.LOCATION_HASH_CIID_KEY];
					}
					var record = combobox.findRecordByValue(value-0);
					if(!record) record = combobox.getStore().getAt(0);
					if(record){
						combobox.suspendEvent('select');
						combobox.setValue(record.get('value'));
						combobox.resumeEvent('select');
						combobox.fireEvent('select',combobox);
					}
				},
				select: function(combobox){
//					self.setLocationHash();
					var ci_id = new RegExp('^'+combobox.getValue()+'$');
					conceptBuildStore.clearFilter(true);
					conceptBuildStore.filter(AgDef.CONCEPT_INFO_DATA_FIELD_ID,ci_id);

					var concept_build_combobox = Ext.getCmp(self.DEF_CONCEPT_BUILD_FORM_FIELD_ID)
					if(concept_build_combobox && concept_build_combobox.rendered){
						if(conceptBuildStore.getCount()){
							if(Ext.isEmpty(concept_build_combobox.getValue())){
								var record = concept_build_combobox.getStore().getAt(0);
								if(record){
									concept_build_combobox.setValue(record.get('value'));
									concept_build_combobox.fireEvent('select',concept_build_combobox);
								}
							}
						}else{
							concept_build_combobox.setValue(null);
						}
					}
				}
			}
		},{
//			hidden: conceptBuildStore.getCount()<=1 ? true : false,
			id: self.DEF_CONCEPT_BUILD_FORM_FIELD_ID,
//			fieldLabel: self.DEF_CONCEPT_LABEL,
//			labelWidth: self.DEF_CONCEPT_FORM_LABEL_WIDTH,
//			width: self.DEF_CONCEPT_FORM_LABEL_WIDTH+self.DEF_CONCEPT_BUILD_FORM_FIELD_WIDTH,
			hideLabel: true,
			width: self.DEF_CONCEPT_BUILD_FORM_FIELD_WIDTH,

			xtype: 'combobox',
			editable: false,
			queryMode: 'local',
			displayField: 'display',
			valueField: 'value',
//			value: Ext.isEmpty(self.DEF_CONCEPT_BUILD_VALUE) ? conceptBuildStore.getAt(0).get('value') : self.DEF_CONCEPT_BUILD_VALUE,
			store: conceptBuildStore,

//			matchFieldWidth: false,
			listConfig : {
//				plugins: 'bufferedrenderer',
//				resizable: true,
				tpl: new Ext.XTemplate(
					'<table class="concept-build-list" width=100%>',
					'<thead><tr><th>version</th><th>release</th></tr></thead>',
					'<tbody>',
					'<tpl for=".">',
						'<tr class="x-boundlist-item"><td>{cb_name}</td><td align="center">{release}</td></tr>',
					'</tpl>',
					'</tbody></table>'
				)
			},

			listeners: {
				afterrender: function(combobox, eOpts){
					var hash = self.getLocationHash();
					var value;
					var store = combobox.getStore();
					if(Ext.isEmpty(hash[AgDef.LOCATION_HASH_CIID_KEY]) || Ext.isEmpty(hash[AgDef.LOCATION_HASH_CBID_KEY])){
						value = Ext.isEmpty(self.DEF_CONCEPT_BUILD_VALUE) ? store.first().get('value') : self.DEF_CONCEPT_BUILD_VALUE;
					}else{
						value = Ext.util.Format.format(AgDef.FORMAT_CONCEPT_VALUE, hash[AgDef.LOCATION_HASH_CIID_KEY],hash[AgDef.LOCATION_HASH_CBID_KEY]);
					}
					var record = combobox.findRecordByValue(value);
					if(!record) record = store.getAt(0);
					if(record){
						combobox.suspendEvent('select');
						combobox.setValue(record.get('value'));
						combobox.resumeEvent('select');
					}
				},
				select: function(combobox){
					self.setLocationHash();

					var field = Ext.getCmp(self.DEF_ID_FORM_FIELD_ID);
					field.specialkeyENTER();

				}
			}
		},
		{
			xtype: 'tbseparator',
			hidden: false
		},

		'->',

		{
			xtype: 'tbseparator',
			hidden: false
		},
		{
			xtype: 'button',
			text: self.DEF_SEARCH_LABEL,
			menu: {
				defaultType: 'menucheckitem',
				items: [{
					itemId: 'search-anymatch-checkboxfield',
					text: self.DEF_SEARCH_ANY_MATCH_LABEL,
					name: AgDef.SEARCH_ANY_MATCH_NAME,
					inputValue: '1',
					checked: true,
					listeners: {
						checkchange: function( field, newValue, oldValue, eOpts ){
							var toolbar = field.up('toolbar');
							var combobox = toolbar.down('combobox#search-combobox');
							if(combobox){
								combobox.inputEl.focus();
								var value = combobox.inputEl.getValue().trim();
								if(value.length) combobox.doQuery(value);
							}
						}
					}
				},{
					itemId: 'search-casesensitive-checkboxfield',
					text: self.DEF_SEARCH_CASE_SENSITIVE_LABEL,
					name: AgDef.SEARCH_CASE_SENSITIVE_NAME,
					inputValue: '1',
					checked: false,
					listeners: {
						checkchange: function( field, newValue, oldValue, eOpts ){
							var toolbar = field.up('toolbar');
							var combobox = toolbar.down('combobox#search-combobox');
							if(combobox){
								combobox.inputEl.focus();
								var value = combobox.inputEl.getValue().trim();
								if(value.length) combobox.doQuery(value);
							}
						}
					}
				}]
			}
		},
		{
			hidden: false,
			id: self.DEF_SEARCH_FORM_FIELD_ID,
			itemId: self.DEF_SEARCH_FORM_FIELD_ID,
			name: AgDef.LOCATION_HASH_SEARCH_KEY,
			fieldLabel: self.DEF_SEARCH_LABEL,
			hideLabel: true,
//			labelWidth: 80,
//			width: 270,
			width: self.DEF_NAME_FORM_FIELD_WIDTH,
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

			pageSize: Ext.data.StoreManager.lookup(AgDef.CONCEPT_TERM_SEARCH_STORE_ID).pageSize,

			queryCaching: false,
			queryParam: AgDef.LOCATION_HASH_SEARCH_KEY,
//			queryParam: AgDef.NAME_DATA_FIELD_ID,	//とりあえず

			matchFieldWidth: false,
			listConfig : {
//				plugins: 'bufferedrenderer',
				resizable: true,
				tpl: new Ext.XTemplate(
					'<table class="term-search-list">',
					'<thead><tr><th>'+self.DEF_ID_LABEL+'</th><th>'+self.DEF_NAME_LABEL+'</th><th>'+self.DEF_SYNONYM_LABEL+'</th></tr></thead>',
					'<tbody>',
					'<tpl for=".">',
						'<tr class="x-boundlist-item"><td valign="top">{'+AgDef.SNIPPET_ID_DATA_FIELD_ID+'}</td><td valign="top">{'+AgDef.SNIPPET_NAME_DATA_FIELD_ID+'}</td><td valign="top">',
						'<tpl if="this.isEmpty(values.'+AgDef.SYNONYM_DATA_FIELD_ID+') == false">',
							'{'+AgDef.SNIPPET_SYNONYM_DATA_FIELD_ID+'}',
						'</tpl>',
						'<tpl if="this.isEmpty(values.'+AgDef.SYNONYM_DATA_FIELD_ID+') == true">',
							'&nbsp;',
						'</tpl>',
						'</td></tr>',
					'</tpl>',
					'</tbody></table>',
					{
						isEmpty : function(val){
							return Ext.isEmpty(val);
						}
					}
				)
			},

			specialkeyENTER: function(){
				var field = this;
				field.doQuery(field.inputEl.getValue());
			},

			listeners: {
				afterrender: function(field, eOpts){
					return;
					var hash = Ext.Object.fromQueryString(window.location.hash.substr(1));
					if(Ext.isEmpty(hash[AgDef.LOCATION_HASH_NAME_KEY ])) return;
					field.setValue(hash[AgDef.LOCATION_HASH_NAME_KEY ]);
					if(field.isVisible()) field.doQuery(hash[AgDef.LOCATION_HASH_NAME_KEY ]);
				},
				keydown: function(field,e,eOpts){
					e.stopPropagation();
				},
				keypress: function(field,e,eOpts){
					e.stopPropagation();
				},
				keyup: function(field,e,eOpts){
					e.stopPropagation();
				},
				beforequery: function( queryPlan, eOpts ){
					Ext.Ajax.abortAll();
					var store = queryPlan.combo.getStore();
					var p = store.getProxy();
					p.extraParams = p.extraParams || {};
/*
					var checkboxfield = queryPlan.combo.nextSibling('checkboxfield');
					while(checkboxfield){
						var name = checkboxfield.getName();
						delete p.extraParams[name];
						if(checkboxfield.getValue()) p.extraParams[name] = 1;
						checkboxfield = checkboxfield.nextSibling('checkboxfield');
					}
*/
					var toolbar = this.up('toolbar');
					Ext.each(['search-anymatch-checkboxfield','search-casesensitive-checkboxfield'],function(id){
						var checkboxfield = toolbar.down('menucheckitem#'+id);
						if(!checkboxfield) return true;
						var name = checkboxfield.name;
						delete p.extraParams[name];
						if(checkboxfield.checked) p.extraParams[name] = 1;
					});

				},
				beforeselect: function(field, record, index, eOpts ){
					var id = record.get(AgDef.ID_DATA_FIELD_ID);
					var name = record.get(AgDef.NAME_DATA_FIELD_ID);
					var lastRecord = self.getLastRecord();
					if(lastRecord.get(AgDef.ID_DATA_FIELD_ID) != id){

//						Ext.getCmp(self.DEF_ID_FORM_FIELD_ID).specialkeyENTER();
//						return false;

						self.setLastRecord(record);
						if(id) Ext.getCmp(self.DEF_ID_FORM_FIELD_ID).setValue(id);
						if(name) Ext.getCmp(self.DEF_NAME_FORM_FIELD_ID).setValue(name);

						$(window).off('hashchange',self._hashChange);
						$(window).one('hashchange',function(){
							$(window).on('hashchange',self._hashChange);

/////
							Ext.getCmp('window-panel').setLoading(true);
							Ext.Ajax.abortAll();
							var store = Ext.data.StoreManager.lookup(AgDef.CONCEPT_TERM_STORE_ID);
							store.loadPage(1,{
								params: {
									id: id
								},
								callback: function(records,operation,success){
									Ext.getCmp('window-panel').setLoading(false);

									if(!success) return;
									if(records.length>1){
									}else{
										var record = records.shift() || self.getEmptyRecord();
										Ext.getCmp(self.DEF_NAME_FORM_FIELD_ID).setValue(record.get(AgDef.NAME_DATA_FIELD_ID));
										self.setLastRecord(record);
										self.initSubStatusPanel(record);
										self._updateFiled(record);
										if(Ext.isEmpty(record.get(AgDef.ID_DATA_FIELD_ID))){
											Ext.Msg.show({
												title: Ext.util.Format.format('{0}',AgLang.title),
												msg: Ext.util.Format.format('Unknown id [{0}]',id),
												buttons: Ext.Msg.OK,
												icon: Ext.Msg.ERROR,
												fn: function(buttonId,text,opt){
												}
											});
										}
									}


								}
							});
/////
						});
//						var hash = {};
//						hash[AgDef.LOCATION_HASH_ID_KEY] = id;
//						hash[AgDef.LOCATION_HASH_NAME_KEY] = name;
//						self.setLocationHash(hash);
						self.setLocationHashID(id);
						self.initSubStatusPanel(record);
						self._updateFiled(record);
					}else{
						Ext.getCmp(self.DEF_NAME_FORM_FIELD_ID).setValue(name);
					}
					return false;
				},
				specialkey: function(field, e){
					if(field.inputEl.getValue().length && e.getKey() == e.ENTER){
////						Ext.Ajax.abortAll();
//						field.doQuery(field.inputEl.getValue());
						field.specialkeyENTER();
					}
				}
			}
		},
/*
		{
			id: 'search-anymatch-checkboxfield',
			xtype: 'checkboxfield',
			boxLabel: 'partialMatch',
			name: 'anyMatch',
			inputValue: '1',
			checked: true,
			listeners: {
				change: function( field, newValue, oldValue, eOpts ){
					var combobox = field.previousSibling('combobox');
					if(combobox){
						combobox.inputEl.focus();
						if(combobox.inputEl.getValue().length){
//							Ext.Ajax.abortAll();
							combobox.doQuery(combobox.inputEl.getValue());
						}
					}
				}
			}
		},
		{
			id: 'search-casesensitive-checkboxfield',
			xtype: 'checkboxfield',
			boxLabel: 'caseSensitive',
			name: 'caseSensitive',
			inputValue: '1',
			checked: false,
			listeners: {
				change: function( field, newValue, oldValue, eOpts ){
					var combobox = field.previousSibling('combobox');
					if(combobox){
						combobox.inputEl.focus();
						if(combobox.inputEl.getValue().length){
//							Ext.Ajax.abortAll();
							combobox.doQuery(combobox.inputEl.getValue());
						}
					}
				}
			}
		},
*/

		{
			xtype: 'tbseparator',
			hidden: false
		},
		{
			id: self.DEF_ID_FORM_FIELD_ID,
			fieldLabel: self.DEF_ID_LABEL,
			labelWidth: self.DEF_ID_FORM_LABEL_WIDTH,
			hidden: false,
			width: self.DEF_ID_FORM_LABEL_WIDTH+self.DEF_ID_FORM_FIELD_WIDTH,
			xtype: self.DEF_ID_FORM_FIELD_XTYPE,
			itemId: self.DEF_ID_FORM_FIELD_ID,
			name: AgDef.LOCATION_HASH_ID_KEY,
			vtype: self.DEF_ID_FORM_FIELD_VTYPE,
			selectOnFocus: true,
			enableKeyEvents: true,
			specialkeyENTER: function(){
				var field = this;
				var id = field.getValue().trim();
				if(self.getLocationHashID() != id){
					self.setLocationHashID(id);
				}else{
					var concept = Ext.getCmp(self.DEF_CONCEPT_BUILD_FORM_FIELD_ID);
					var conceptRecord = concept.findRecordByValue(concept.getValue());
					if(!conceptRecord) return;
					var lastRecord = self.getLastRecord();
					if(
						lastRecord.get(AgDef.ID_DATA_FIELD_ID) != id ||
						lastRecord.get(AgDef.CONCEPT_INFO_DATA_FIELD_ID) != conceptRecord.get(AgDef.CONCEPT_INFO_DATA_FIELD_ID) ||
						lastRecord.get(AgDef.CONCEPT_BUILD_DATA_FIELD_ID) != conceptRecord.get(AgDef.CONCEPT_BUILD_DATA_FIELD_ID)
					){
						self.loadRecord(id);
						return;
						Ext.getCmp('window-panel').setLoading(true);
						Ext.Ajax.abortAll();
						var store = Ext.data.StoreManager.lookup(AgDef.CONCEPT_TERM_STORE_ID);
						store.loadPage(1,{
							params: {
								id: id
							},
							callback: function(records,operation,success){
								Ext.getCmp('window-panel').setLoading(false);
								if(!success) return;
								if(records.length>1){
								}else{
									var record = records.shift() || self.getEmptyRecord();
									Ext.getCmp(self.DEF_NAME_FORM_FIELD_ID).setValue(record.get(AgDef.NAME_DATA_FIELD_ID));
									self.setLastRecord(record);
//											field.setValue(record.get(AgDef.ID_DATA_FIELD_ID));
									self.initSubStatusPanel(record);
									self._updateFiled(record);
									if(Ext.isEmpty(record.get(AgDef.ID_DATA_FIELD_ID))){
										Ext.Msg.show({
											title: Ext.util.Format.format('{0}',AgLang.title),
											msg: Ext.util.Format.format('Unknown id [{0}]',id),
											buttons: Ext.Msg.OK,
											icon: Ext.Msg.ERROR,
											fn: function(buttonId,text,opt){
											}
										});
									}
								}
							}
						});
					}
				}
			},
			listeners: {
				afterrender: function(field, eOpts){
					field.inputEl.set({
						autocomplete: 'on',
						spellcheck: 'false'
					});
/*
					var hashName = self.getLocationHashName();
					var hashId = self.getLocationHashID();
					if(self.isEmpty(hashName)){
						if(self.isEmpty(hashId)) return;
						field.setValue(hashId);
						var e = new Ext.EventObjectImpl();
						e.keyCode = e.ENTER
						field.fireEvent('specialkey',field,e);
					}
*/
				},
				keydown: function(field,e,eOpts){
					e.stopPropagation();
				},
				keypress: function(field,e,eOpts){
					e.stopPropagation();
				},
				keyup: function(field,e,eOpts){
					e.stopPropagation();
				},
				specialkey: function(field, e){
					if(field.getValue().length && e.getKey() == e.ENTER){
						field.specialkeyENTER();
					}
				}
			}
		},
		{
			xtype: 'tbseparator',
			hidden: false
		},
		{
			hidden: false,
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
				var field = this;
				var name = field.getValue().trim();
				if(self.getLocationHashName() != name){
					self.setLocationHashName(name);
				}else{
					var concept = Ext.getCmp(self.DEF_CONCEPT_BUILD_FORM_FIELD_ID);
					var conceptRecord = concept.findRecordByValue(concept.getValue());
					if(!conceptRecord) return;
					var lastRecord = self.getLastRecord();
					if(
						lastRecord.get(AgDef.NAME_DATA_FIELD_ID) != name ||
						lastRecord.get(AgDef.CONCEPT_INFO_DATA_FIELD_ID) != conceptRecord.get(AgDef.CONCEPT_INFO_DATA_FIELD_ID) ||
						lastRecord.get(AgDef.CONCEPT_BUILD_DATA_FIELD_ID) != conceptRecord.get(AgDef.CONCEPT_BUILD_DATA_FIELD_ID)
					){
						Ext.getCmp('window-panel').setLoading(true);
						Ext.Ajax.abortAll();
						var store = Ext.data.StoreManager.lookup(AgDef.CONCEPT_TERM_STORE_ID);
						store.loadPage(1,{
							params: {
								name: name
							},
							callback: function(records,operation,success){
								Ext.getCmp('window-panel').setLoading(false);
								if(!success) return;
								if(records.length>1){
								}else{
									var record = records.shift() || self.getEmptyRecord();
									Ext.getCmp(self.DEF_ID_FORM_FIELD_ID).setValue(record.get(AgDef.ID_DATA_FIELD_ID));
									self.setLastRecord(record);
//											field.setValue(record.get(AgDef.NAME_DATA_FIELD_ID));
									self.initSubStatusPanel(record);
									self._updateFiled(record);
									if(Ext.isEmpty(record.get(AgDef.NAME_DATA_FIELD_ID))){
										Ext.Msg.show({
											title: Ext.util.Format.format('{0}',AgLang.title),
											msg: Ext.util.Format.format('Unknown name [{0}]',name),
											buttons: Ext.Msg.OK,
											icon: Ext.Msg.ERROR,
											fn: function(buttonId,text,opt){
											}
										});
									}
								}
							}
						});
					}
				}
			},
			listeners: {
				afterrender: function(field, eOpts){
					field.inputEl.set({
						autocomplete: 'on',
						spellcheck: 'true'
					});
/*
					var value = self.getLocationHashName();
					if(self.isEmpty(value)) return;
					if(value.match(/^FMA:*([0-9]+)/i) || value.match(/^([0-9]+)/)){
						var fmaid = 'FMA'+RegExp.$1;
						field = Ext.getCmp(self.DEF_ID_FORM_FIELD_ID);
						field.setValue(fmaid);
						var e = new Ext.EventObjectImpl();
						e.keyCode = e.ENTER
						field.fireEvent('specialkey',field,e);
					}else{
						field.setValue(value);
						self.updateFiled(value);
					}
*/
				},
				keydown: function(field,e,eOpts){
					e.stopPropagation();
				},
				keypress: function(field,e,eOpts){
					e.stopPropagation();
				},
				keyup: function(field,e,eOpts){
					e.stopPropagation();
				},
				specialkey: function(field, e){
					if(field.getValue().length && e.getKey() == e.ENTER){
						field.specialkeyENTER();
					}
				}
			}
		},
		{
			hidden: true,
			xtype: 'tbseparator'
		},
		{
			hidden: true,
			labelWidth: 56,
			width: 140,
			xtype: 'combobox',
			fieldLabel: 'Order by',
			editable: false,
			store:  Ext.create('Ext.data.Store', {
				fields: ['value','display'],
				data : [
					{value:AgDef.NAME_DATA_FIELD_ID, display:self.DEF_NAME_LABEL},
					{value:AgDef.ID_DATA_FIELD_ID,   display:self.DEF_ID_LABEL},
				]
			}),
			queryMode: 'local',
			displayField: 'display',
			valueField: 'value',
			value: AgDef.NAME_DATA_FIELD_ID,
			listeners:{
				select: function(field, records, eOpts){
					Ext.Ajax.abortAll();
				}
			}
		},
		{
			hidden: true,
			width: 74,
			xtype: 'combobox',
			editable: false,
			store:  Ext.create('Ext.data.Store', {
				fields: ['value'],
				data : [
					{value:'ASC'},
					{value:'DESC'},
				]
			}),
			queryMode: 'local',
			displayField: 'value',
			valueField: 'value',
			value: 'ASC',
		}]
	},{
		hidden: false,
		xtype: 'toolbar',
		dock: 'bottom',
		layout: {
			overflowHandler: 'Menu'
		},
		items: [{
			xtype:'buttongroup',
			defaultType: 'button',
			defaults: {
				enableToggle: true,
				toggleGroup: 'hierarchy_display_options',
				listeners: {
					afterrender: function( button ){
						var extendHierarchy = self.getLocationHashExtendHierarchy();
						if(button.itemId=='single' && !extendHierarchy){
							button.toggle(true,true);
						}else if(button.itemId=='extended' && extendHierarchy){
							button.toggle(true,true);
						}
					},
					toggle: function(button, pressed){
						if(button.itemId=='extended'){
							self.setLocationHashExtendHierarchy(pressed);
							self._updateFiled(self.getLastRecord());
						}
					}
				}
			},
			items:[{
				id: 'hierarchy-display-options-single',
				itemId: 'single',
				text: 'Single-level hierarchies',
				tooltip: 'Show only a single level of the hierarchy for each relationship.'
			},{
				id: 'hierarchy-display-options-extended',
				itemId: 'extended',
				text: 'Extended hierarchies',
				tooltip: 'Show arrowheads for opening the hierarchy for each relationship.'
			}]
		},{
			xtype: 'tbfill',
			hidden: false
		},{
			xtype:'buttongroup',
			defaultType: 'button',
			defaults: {
				enableToggle: true,
				listeners: {
					afterrender: function( button ){
						if(button.getXType() != 'button') return;
						var hidden = self.DEF_RELATION_HIDDEN[button.itemId] || false;
						if(button.toggle){
							button.toggle(!hidden,false);
						}else{
						}
					},
					toggle: function(button, pressed){
						var relation = button.itemId;
						self.DEF_DIRECTION.forEach(function(direction){
							var id = Ext.util.Format.format(self.FORMAT_RELATIONS_PANEL_ID,relation,direction);
							var panel = Ext.getCmp(id);
							if(panel){
								if(pressed){
									panel.show(button.getEl());
								}else{
									panel.hide(button.getEl());
								}
							}
						});
					}
				}
			},
			items:[{
				xtype: 'tbseparator',
				hidden: false
			},{
				itemId: 'regional_part_of',
				text: 'regional_part'
			},{
				itemId: 'constitutional_part_of',
				text: 'constitutional_part'
			},{
				itemId: 'branch_of',
				text: 'branch'
			},{
				itemId: 'tributary_of',
				text: 'tributary'
			},{
				itemId: 'member_of',
				text: 'member'
			},{
				itemId: 'systemic_part_of',
				text: 'systemic_part'
			},{
				itemId: 'lexicalsuper',
				text: 'nominal_part'
			}
/*
			,{
				itemId: 'tributary_of',
				text: 'tributary'
			}
*/
			]
		}]
	}];


	var getCookiesPath = function(){
		return (window.location.pathname.split('/').splice(0,window.location.pathname.split('/').length).join('/'));
	};

	var getCookiesExpires = function(){
		var xDay = new Date;
		xDay.setTime(xDay.getTime() + (30 * 24 * 60 * 60 * 1000)); //30 Days after
		return xDay;
	};


//	console.log(Ext.getBody().getSize());
//	console.log(Ext.getBody().getSize(true));

	var bodySize = Ext.getBody().getSize();
	var all_height = bodySize.height-27-10*2;
	var height = Math.floor((bodySize.height-27)/3)-10*2;
	var north_panel_height = 200;
	var south_panel_height = 100;
	var center_panel_height = 250;
	if(all_height>north_panel_height+south_panel_height+center_panel_height){
		south_panel_height = all_height - north_panel_height - center_panel_height;
	}

	var getPanelConfig = function(config){

		config = config || {id: Ext.id()};

		var extraParams = {};
		extraParams[AgDef.RELATION_TYPE_NAME] = config.id;

		var store = 	Ext.create('Ext.data.TreeStore', {
			autoLoad: false,
			storeId: config.id+'-treePanelStore',
			model: 'CONCEPT_TERM_TREE',
			sorters: [{
				property: 'term_name',
				direction: 'ASC'
			}],
			proxy: {
				type: 'ajax',
				url: 'get-fma-tree.cgi',
				actionMethods : {
					read   : 'POST',
				},
				extraParams: extraParams
			},
			root: {
				allowDrag: false,
				allowDrop: false,
				depth: 0,
	//				expandable: true,
				expanded: true,
//				expanded: false,
				iconCls: 'tree-folder',
				root: true,
				text: '/',
				name: 'root',
				term_id: 'root'
			},

			listeners: {
				beforeload: function(store, operation, eOpts){
					if(self.beforeloadStore(store)){
/**/
						var sel_node = operation.node ? operation.node : this.getSelectionModel().getLastSelected();
						var p = store.getProxy();
						p.extraParams = p.extraParams || {};
						if(sel_node){
							p.extraParams[AgDef.LOCATION_HASH_ID_KEY] = sel_node.get(AgDef.TERM_ID_DATA_FIELD_ID);
						}else{
							delete p.extraParams[AgDef.LOCATION_HASH_ID_KEY];
						}
/**/
					}else{
						return false;
					}
				},
				load: function(store, node, records, successful, eOpts){
				},
				update: function(store,record,operation,modifiedFieldNames,eOpts){
				},
				scope : self
			}
		});

		config.hidden = config.hidden || self.DEF_RELATION_HIDDEN[config.itemId] || false;

		return Ext.apply(config || {},{
//			header: false,
			defaults: {
				border: false,
			},
			layout: 'card',
			items: [{
//				title: config.title,
//				iconCls: 'view_text',
				id: config.id+'-panel',
				itemId: config.id+'-panel',
				bodyStyle: {overflow: 'auto'}
			},{
//				title: config.title,
//				iconCls: 'view_tree',
				id: config.id+'-treepanel',
				itemId: config.id+'-treepanel',
				xtype: 'treepanel',
				store: store,
				rootVisible: false,
				useArrows: true,
				listeners: {
					itemclick: function( view, record, item, index, e, eOpts ){
						self.setLocationHashID(record.get(AgDef.TERM_ID_DATA_FIELD_ID));
					}
				}
			}]
		});
	};

	var north_panel = {
		region: 'north',
		split: true,
		minHeight: 150,
		maxHeight: 200,
//		height: north_panel_height,
		flex: 0.7,
		margin: '20 50 1 50',
		layout: {
			type: 'hbox',
			align: 'stretch',
			pack: 'center'
		},
		defaultType: 'panel',
		defaults: {
			frame: true,
			margin: '0 10 0 10',
			autoScroll: false,
			bodyCls: 'aa'
		},
		items: [getPanelConfig({
			id: 'regional_part_of_up',
			itemId: 'regional_part_of',
			title: 'is regional part of',
			flex: 1,
		}),getPanelConfig({
			id: 'constitutional_part_of_up',
			itemId: 'constitutional_part_of',
			title: 'is constitutional part of',
			flex: 1,
		}),getPanelConfig({
//			hidden: true,
			id: 'branch_of_up',
			itemId: 'branch_of',
			title: 'is branch part of',
			flex: 1,
		}),getPanelConfig({
			id: 'tributary_of_up',
			itemId: 'tributary_of',
			title: 'is tributary of',
			flex: 1,
		}),getPanelConfig({
			id: 'member_of_up',
			itemId: 'member_of',
			title: 'is member of',
			flex: 1,
		}),getPanelConfig({
			id: 'systemic_part_of_up',
			itemId: 'systemic_part_of',
			title: 'is systemic part of',
			flex: 1,
		}),getPanelConfig({
			id: 'lexicalsuper_up',
			itemId: 'lexicalsuper',
			title: 'is nominal part of',
			flex: 1,
		})
/*
		,getPanelConfig({
//			hidden: true,
			id: 'tributary_of_up',
			itemId: 'tributary_of',
			title: 'is tributary of',
			flex: 1,
		})
*/
		],
		listeners: {
			resize: function(comp,adjWidth,adjHeight,rawWidth,rawHeight){
			}
		}
	};
	var south_panel = {
		region: 'south',
		split: true,
		minHeight: 150,
		flex: 0.7,
		margin: '1 50 20 50',
		layout: {
			type: 'hbox',
			align: 'stretch',
			pack: 'center'
		},
		defaultType: 'panel',
		defaults: {
			frame: true,
			margin: '0 10 0 10',
			autoScroll: false
		},
		items: [getPanelConfig({
			id: 'regional_part_of_down',
			itemId: 'regional_part_of',
			title: 'has regional part',
			flex: 1,
		}),getPanelConfig({
			id: 'constitutional_part_of_down',
			itemId: 'constitutional_part_of',
			title: 'has constitutional part',
			flex: 1,
		}),getPanelConfig({
//			hidden: true,
			id: 'branch_of_down',
			itemId: 'branch_of',
			title: 'has branch part',
			flex: 1,
		}),getPanelConfig({
			id: 'tributary_of_down',
			itemId: 'tributary_of',
			title: 'has tributary',
			flex: 1,
		}),getPanelConfig({
			id: 'member_of_down',
			itemId: 'member_of',
			title: 'has member',
			flex: 1,
		}),getPanelConfig({
			id: 'systemic_part_of_down',
			itemId: 'systemic_part_of',
			title: 'has systemic part',
			flex: 1,
		}),getPanelConfig({
			id: 'lexicalsuper_down',
			itemId: 'lexicalsuper',
			title: 'has nominal part',
			flex: 1,
		})
/*
		,getPanelConfig({
//			hidden: true,
			id: 'tributary_of_down',
			itemId: 'tributary_of',
			title: 'has tributary',
			flex: 1,
		})
*/
		],
		listeners: {
			resize: function(comp,adjWidth,adjHeight,rawWidth,rawHeight){
			}
		}
	};
	var subclass_items = [];
	var subpart_items = [];
	if(Ext.isArray(Ext.ag.Data.concept_art_map_part)){
//		console.log(Ext.ag.Data.concept_art_map_part);
		Ext.Array.each(Ext.ag.Data.concept_art_map_part, function(p){
			if(Ext.isString(p['crl_name']) && p['crl_name'].length>0){
				var config = {
					text:   p['cmp_abbr'],
					prefix: p['cmp_prefix'],
					itemId: 'sub-'+p['cmp_abbr']
				};
				if(p['crl_name']=='is_a'){
					subclass_items.push(config);
				}
				else if(p['crl_name']=='part_of'){
					subpart_items.push(config);
				}
			}
		});
	}

	var press_sub = {};

	var getExistingGridColumnRenderer = function(value,metaData,record,rowIndex,colIndex,store,view){
		if(metaData.column.xtype){
			if(metaData.column.xtype == 'booleancolumn'){
				if(Ext.isBoolean(value) && metaData.column.trueText && metaData.column.falseText){
					if(value){
						value = metaData.column.trueText;
					}else{
						value = metaData.column.falseText;
					}
				}
			}
			else if(metaData.column.xtype == 'agfilesizecolumn'){
				if(Ext.isNumber(value)) value = Ext.util.Format.fileSize(value);
			}
			else if(metaData.column.xtype == 'agnumbercolumn'){
				if(Ext.isNumber(value) && metaData.column.format) value = Ext.util.Format.number(value,metaData.column.format);
			}
			else if(metaData.column.xtype == 'datecolumn'){
				if(Ext.isDate(value) && metaData.column.format) value = Ext.util.Format.date(value,metaData.column.format);
			}
		}
		return value;
	};

	var getHideParentTermCheckbox = function(){
		return {
			hidden: true,
			disabled: true,
			xtype: 'checkboxfield',
			boxLabel: 'hide parent term',
			checked: true,
			listeners: {
				afterrender: function(field){
					var gridpanel = field.up('gridpanel');
					var store = gridpanel.getStore();
					store.on({
						load: function(store, records, successful, eOpts){
							field.setDisabled(successful ? false : true);
						}
					});
					if(field.checked){
						var proxy = store.getProxy();
						proxy.extraParams = proxy.extraParams || {};
						proxy.extraParams.hideChildrenTerm=1;
						proxy.extraParams.hideAncestorTerm=1;
						proxy.extraParams.hideParentTerm=1;
						proxy.extraParams.hideDescendantsTerm=1;
						proxy.extraParams.hidePairTerm=1;
					}
				},
				change: function(field, checked){
					var gridpanel = field.up('gridpanel');
					var store = gridpanel.getStore();
					var proxy = store.getProxy();
					proxy.extraParams = proxy.extraParams || {};
					delete proxy.extraParams.hideParentTerm;
					if(checked) proxy.extraParams.hideParentTerm=1;
					store.reload({
						callback: function(){
							if(Ext.isChrome && gridpanel) gridpanel.columns.forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
						}
					})
				}
			}
		};
	};

	var getNeverCurrentButton = function(){
		return {
			xtype: 'button',
			disabled: true,
			itemId: 'never_current',
			iconCls: 'gridcolumn_current_none_use',
			text: AgLang.never_current,
			listeners: {
				afterrender: function(field){
					var gridpanel = field.up('gridpanel');
					gridpanel.on('selectionchange',function(selModel,selected,eOpts){
						var disabled = true;
						if(Ext.isArray(selected)){
							Ext.each(selected,function(record){
								if(Ext.isBoolean(record.get('is_exists')) && record.get('is_exists')){
									disabled = false;
									return false;
								}
							});
						}
						field.setDisabled(disabled);
					});
				},
				click: function(field){
					var gridpanel = field.up('gridpanel');
					var store = gridpanel.getStore();
					var selModel = gridpanel.getSelectionModel();
					var records = selModel.getSelection();
					if(Ext.isArray(records) && records.length){
						records.forEach(function(record){
							record.beginEdit();
							if(Ext.isBoolean(record.get('is_virtual')) && record.get('is_virtual')){
								var virtual_cm_use = Ext.isBoolean(record.get('virtual_cm_use')) && record.get('virtual_cm_use') ? !record.get('virtual_cm_use') : true;
								var virtual_never_current = Ext.isBoolean(record.get('virtual_never_current')) && record.get('virtual_never_current') ? !record.get('virtual_never_current') : false;
								record.set('cm_use', virtual_cm_use);
								record.set('never_current', virtual_never_current);
								record.set('virtual_cm_use', virtual_cm_use);
								record.set('virtual_never_current', virtual_never_current);
								record.endEdit(false,['cm_use','never_current','virtual_cm_use','virtual_never_current']);
							}else{
								record.set('cm_use',!record.get('cm_use'));
								record.set('never_current',!record.get('never_current'));
								record.endEdit(false,['cm_use','never_current']);
							}
						});
						field.setDisabled(true);
						if(Ext.isEmpty(store.getUpdatedRecords())){
							return;
						}
						field.setIconCls('loading-btn');
						var gridpanel = field.up('gridpanel');
						if(gridpanel) gridpanel.setDisabled(true);

/*
						self.syncMappingMngStore(records,false);
						if(self.syncUploadObjectStore) self.syncUploadObjectStore(records);
						if(self.syncPalletPartsStore) self.syncPalletPartsStore(records);
						if(self.syncPickSearchStore) self.syncPickSearchStore(records);
*/
						field.setIconCls('loading-btn');
						var gridpanel = field.up('gridpanel');
						if(gridpanel) gridpanel.setDisabled(true);

						store.sync({
							callback: function(batch,options){
								field.setIconCls('gridcolumn_current_none_use');
								if(gridpanel) gridpanel.setDisabled(false);
								var hash = self.getLocationHash();
								var hashId     = self.isEmpty(hash[AgDef.LOCATION_HASH_ID_KEY])     ? null : Ext.String.trim(hash[AgDef.LOCATION_HASH_ID_KEY]);
								Ext.data.StoreManager.lookup(existingAttributeStoreId).loadPage(1,{params:{cdi_name:hashId}});
//								Ext.data.StoreManager.lookup(parentAttributeStoreId).loadPage(1);
//								var panel = Ext.getCmp(aOpt.id);
//								var mirror_checkboxfield = panel.down('checkboxfield#mirror');
//								if(mirror_checkboxfield && mirror_checkboxfield.getValue() && !mirror_checkboxfield.isDisabled()){
//									Ext.data.StoreManager.lookup(mirrorExistingAttributeStoreId).loadPage(1);
//									Ext.data.StoreManager.lookup(mirrorParentAttributeStoreId).loadPage(1);
//								}
//								Ext.data.StoreManager.lookup(allExistingAttributeStoreId).loadPage(1);
							},
							success: function(batch,options){
								store.loadPage(1);
//								var attributeStore = Ext.data.StoreManager.lookup(attributeStoreId);
//								attributeStore.fireEvent('datachanged', attributeStore);
							},
							failure: function(batch,options){
								var msg = AgLang.error_submit;
								var proxy = this;
								var reader = proxy.getReader();
								if(reader && reader.rawData && reader.rawData.msg){
									msg += ' ['+reader.rawData.msg+']';
								}
								Ext.Msg.show({
									title: field.text || AgLang.never_current,
									iconCls: 'gridcolumn_current_none_use',
									msg: msg,
									buttons: Ext.Msg.OK,
									icon: Ext.Msg.ERROR,
									fn: function(buttonId,text,opt){
									}
								});
								field.setDisabled(false);
								Ext.each(records,function(r,i,a){
									r.reject();
								});
/*
								self.syncMappingMngStore(records,false);
								if(self.syncUploadObjectStore) self.syncUploadObjectStore(records);
								if(self.syncPalletPartsStore) self.syncPalletPartsStore(records);
								if(self.syncPickSearchStore) self.syncPickSearchStore(records);
*/
							}
						});

					}
				}
			}
		};
	};

	var getRemoveMappingButton = function(){
		return {
			xtype: 'button',
			disabled: true,
			itemId: 'delete',
//			iconCls: 'pallet_delete',
			text: AgLang.remove_from_current,
			listeners: {
				afterrender: function(field){
					var gridpanel = field.up('gridpanel');
					gridpanel.on('selectionchange',function(selModel,selected,eOpts){
						var disabled = true;
						if(Ext.isArray(selected)){
							Ext.each(selected,function(record){
								if(Ext.isBoolean(record.get('is_exists')) && record.get('is_exists')){
									disabled = false;
									return false;
								}
							});
						}
						field.setDisabled(disabled);
					});
				},
				click: function(field){

					Ext.Msg.show({
						title: field.text || AgLang.remove_from_current,
//						iconCls: field.iconCls || 'pallet_delete',
						buttons: Ext.Msg.YESNO,
						icon: Ext.Msg.QUESTION,
						defaultFocus: 'no',
						msg: 'マッピング情報を削除してよろしいですか？',
						fn: function(buttonId,text,opt){
							if(buttonId!='yes') return;

							var gridpanel = field.up('gridpanel');
							var store = gridpanel.getStore();
							var selModel = gridpanel.getSelectionModel();
							var records = selModel.getSelection();
							if(Ext.isArray(records) && records.length){
								records.forEach(function(record){
									record.beginEdit();
									record.set('cdi_name',null);
									record.set('cdi_name_e',null);
									record.set('cmp_id',0);
									record.endEdit(false,['cdi_name','cdi_name_e','cmp_id']);
								});
								field.setDisabled(true);
								if(Ext.isEmpty(store.getUpdatedRecords())){
									return;
								}
								field.setIconCls('loading-btn');
								var gridpanel = field.up('gridpanel');
								if(gridpanel) gridpanel.setDisabled(true);

/*
								self.syncMappingMngStore(records,false);
								if(self.syncUploadObjectStore) self.syncUploadObjectStore(records);
								if(self.syncPalletPartsStore) self.syncPalletPartsStore(records);
								if(self.syncPickSearchStore) self.syncPickSearchStore(records);
*/
								field.setIconCls('loading-btn');
								var gridpanel = field.up('gridpanel');
								if(gridpanel) gridpanel.setDisabled(true);

								store.sync({
									callback: function(batch,options){
										field.setIconCls('pallet_delete');
										if(gridpanel) gridpanel.setDisabled(false);
										var hash = self.getLocationHash();
										var hashId     = self.isEmpty(hash[AgDef.LOCATION_HASH_ID_KEY])     ? null : Ext.String.trim(hash[AgDef.LOCATION_HASH_ID_KEY]);
										Ext.data.StoreManager.lookup(existingAttributeStoreId).loadPage(1,{params:{cdi_name:hashId}});
//										Ext.data.StoreManager.lookup(parentAttributeStoreId).loadPage(1);
//										var panel = Ext.getCmp(aOpt.id);
//										var mirror_checkboxfield = panel.down('checkboxfield#mirror');
//										if(mirror_checkboxfield && mirror_checkboxfield.getValue() && !mirror_checkboxfield.isDisabled()){
//											Ext.data.StoreManager.lookup(mirrorExistingAttributeStoreId).loadPage(1);
//											Ext.data.StoreManager.lookup(mirrorParentAttributeStoreId).loadPage(1);
//										}
//										Ext.data.StoreManager.lookup(allExistingAttributeStoreId).loadPage(1);
									},
									success: function(batch,options){
										store.loadPage(1);
//										var attributeStore = Ext.data.StoreManager.lookup(attributeStoreId);
//										attributeStore.fireEvent('datachanged', attributeStore);
									},
									failure: function(batch,options){
										var msg = AgLang.error_submit;
										var proxy = this;
										var reader = proxy.getReader();
										if(reader && reader.rawData && reader.rawData.msg){
											msg += ' ['+reader.rawData.msg+']';
										}
										Ext.Msg.show({
											title: field.text || AgLang.remove_from_current,
//											iconCls: 'pallet_delete',
											msg: msg,
											buttons: Ext.Msg.OK,
											icon: Ext.Msg.ERROR,
											fn: function(buttonId,text,opt){
											}
										});
										field.setDisabled(false);
										Ext.each(records,function(r,i,a){
											r.reject();
										});
/*
										self.syncMappingMngStore(records,false);
										if(self.syncUploadObjectStore) self.syncUploadObjectStore(records);
										if(self.syncPalletPartsStore) self.syncPalletPartsStore(records);
										if(self.syncPickSearchStore) self.syncPickSearchStore(records);
*/
									}
								});
							}
						}
					});
				}
			}
		};
	};

	var getFMABrowserButton = function(){
		return {
			xtype: 'button',
			disabled: true,
			itemId: 'send',
			iconCls: 'window_send',
			text: AgLang.FMABrowser,
			listeners: {
				afterrender: function(b){
					var gridpanel = b.up('gridpanel');
					gridpanel.on('selectionchange',function(selModel,selected,eOpts){
						b.setDisabled(Ext.isEmpty(selected));
					});
				},
				click: function(b){
					var gridpanel = b.up('gridpanel');
					var selModel = gridpanel.getSelectionModel();
					var record = selModel.getLastSelected();
					if(record){
						self.openFMABrowser(record.get('cdi_name'));
					}
				}
			}
		};
	};

	var getExistingGridColumns = function(){
		return [
			{
				text: AgLang.new,      dataIndex: 'is_virtual',       stateId: 'is_virtual',        width: 34, minWidth: 34, hidden: true, hideable: false, sortable: false, draggable: false, resizable: false, align: 'center'
				,renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
					var tdCls = [];
					if(value){
						tdCls.push('gridcolumn_current_use');
					}else{
//						tdCls.push('gridcolumn_current_none_use');
					}

					if(Ext.isString(metaData.tdCls) && metaData.tdCls.length){
						metaData.tdCls += ' ' + tdCls.join(' ');
					}else{
						metaData.tdCls = tdCls.join(' ');
					}
					return getExistingGridColumnRenderer('',metaData,record,rowIndex,colIndex,store,view);
				}
			},
			{
				text: AgLang.current,      dataIndex: 'current_use',       stateId: 'current_use',        width: 46, minWidth: 46, hidden: false, hideable: false, sortable: false, draggable: false, resizable: false
				,renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
					var tdCls = [];
					if(value){
						tdCls.push('gridcolumn_current_use');
					}
					else if(Ext.isEmpty(record.get('cdi_name'))){
						metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(self.TOOLTIP_FMAID_NOT_SUPPORTED) + '"';
					}
					else{
						tdCls.push('gridcolumn_current_none_use');
						if(Ext.isString(record.get('current_use_reason'))) metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(record.get('current_use_reason')) + '"';
					}

					if(Ext.isString(metaData.tdCls) && metaData.tdCls.length){
						metaData.tdCls += ' ' + tdCls.join(' ');
					}else{
						metaData.tdCls = tdCls.join(' ');
					}
					return getExistingGridColumnRenderer('',metaData,record,rowIndex,colIndex,store,view);
				}
			},
			{
				text: AgLang.edited,      dataIndex: 'cm_edited',       stateId: 'cm_edited',        width: 46, minWidth: 46, hidden: self.getHiddenEditedGridColumn(), hideable: false, sortable: true, draggable: false, resizable: false
				,renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
					var tdCls = [];
					if(value){
						tdCls.push('gridcolumn_current_use');
					}else{
						tdCls.push('gridcolumn_current_none_use');
					}
					if(Ext.isString(metaData.tdCls) && metaData.tdCls.length){
						metaData.tdCls += ' ' + tdCls.join(' ');
					}else{
						metaData.tdCls = tdCls.join(' ');
					}
					return getExistingGridColumnRenderer('',metaData,record,rowIndex,colIndex,store,view);
				}
			},
			{
				text: '&#160;',            dataIndex: 'art_tmb_path',     stateId: 'art_tmb_path',      width: 34, minWidth: 34, hidden: false, hideable: false, sortable: false, draggable: false, resizable: false
				,renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
					if(Ext.isString(metaData.innerCls) && metaData.innerCls.length){
						metaData.innerCls += ' art_tmb_path';
					}else{
						metaData.innerCls = 'art_tmb_path';
					}
					return getExistingGridColumnRenderer(value,metaData,record,rowIndex,colIndex,store,view);
				}
			},
			{
				text: 'Never Current',     dataIndex: 'never_current',stateId: 'never_current', width: 80, minWidth: 80, hidden: false, hideable: false, resizable: false, sortable: false, xtype : 'booleancolumn', trueText: 'Yes', falseText: 'No', align: 'center'
				,renderer: getExistingGridColumnRenderer
			},
//			{
//				text: AgLang.art_id,       dataIndex: 'art_id',       stateId: 'art_id',        width: 54, minWidth: 54, hidden: false, hideable: false
//				,renderer: getExistingGridColumnRenderer
//			},
			{
				text: AgLang.cdi_name,     dataIndex: 'cdi_name',     stateId: 'cdi_name',      width: 70, minWidth: 70, hidden: true,  hideable: false, xtype: 'agcolumncdiname'
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.cmp_abbr,     dataIndex: 'cmp_id',       stateId: 'cmp_id',        width: 30, minWidth: 30, hidden: true,  hideable: false, xtype: 'agcolumnconceptartmappart'
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.cdi_name_e,   dataIndex: 'cdi_name_e',   stateId: 'cdi_name_e',    flex: 2.0, minWidth: 80, hidden: true, hideable: true, xtype: 'agcolumncdinamee'
//				,renderer: getExistingGridColumnRenderer
			},
			{text: 'System',            dataIndex: 'seg_name',     stateId: 'seg_name',      flex: 1.0, minWidth: 50, hidden: true,  hideable: true,  xtype: 'agsystemcolumn'},
			{
				text: AgLang.art_id,       dataIndex: 'art_id',       stateId: 'art_id',        width: 54, minWidth: 54, hidden: false, hideable: false
				,renderer: getExistingGridColumnRenderer
			},
/*
			{text: AgLang.category,     dataIndex: 'arta_category',stateId: 'arta_category', flex: 1.0, minWidth: 50, hidden: true, hideable: true},
			{text: AgLang.class_name,   dataIndex: 'arta_class',   stateId: 'arta_class',    width: 36, minWidth: 36, hidden: true, hideable: true},
			{text: AgLang.comment,      dataIndex: 'arta_comment', stateId: 'arta_comment',  flex: 2.0, minWidth: 80, hidden: true, hideable: true},
			{text: AgLang.judge,        dataIndex: 'arta_judge',   stateId: 'arta_judge',    flex: 1.0, minWidth: 50, hidden: true, hideable: true},

			{text: AgLang.arto_id,      dataIndex: 'arto_id',      stateId: 'arto_id',       width: 60, minWidth: 60, hidden: true, hideable: true, sortable: false},
			{text: AgLang.arto_filename,dataIndex: 'arto_filename',stateId: 'arto_filename', flex: 2.0, minWidth: 80, hidden: true, hideable: true, sortable: false},
			{text: AgLang.arto_comment, dataIndex: 'arto_comment', stateId: 'arto_comment',  flex: 2.0, minWidth: 80, hidden: true, hideable: true, sortable: false},
*/
			{
				text: AgLang.file_name,    dataIndex: 'art_filename', stateId: 'art_filename',  flex: 2.0, minWidth: 80, hidden: true, hideable: true
				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.file_size,    dataIndex: 'art_data_size',stateId: 'art_data_size', width: 59,  hidden: true, hideable: true, xtype: 'agfilesizecolumn'
//				,renderer: getExistingGridColumnRenderer
			},

			{
				text: AgLang.xmax,         dataIndex: 'art_xmax',     stateId: 'art_xmax',      width: 63,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.xmin,         dataIndex: 'art_xmin',     stateId: 'art_xmin',      width: 63,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.xcenter,      dataIndex: 'art_xcenter',  stateId: 'art_xcenter',   width: 76,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.ymax,         dataIndex: 'art_ymax',     stateId: 'art_ymax',      width: 63,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.ymin,         dataIndex: 'art_ymin',     stateId: 'art_ymin',      width: 63,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.ycenter,      dataIndex: 'art_ycenter',  stateId: 'art_ycenter',   width: 76,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.zmax,         dataIndex: 'art_zmax',     stateId: 'art_zmax',      width: 63,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.zmin,         dataIndex: 'art_zmin',     stateId: 'art_zmin',      width: 63,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.zcenter,      dataIndex: 'art_zcenter',  stateId: 'art_zcenter',   width: 76,  hidden: false, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.volume,       dataIndex: 'art_volume',   stateId: 'art_volume',    width: 76,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},

			{
				text: AgLang.timestamp,    dataIndex: 'art_timestamp',stateId: 'art_timestamp', minWidth: self.ART_TIMESTAMP_WIDTH, flex: 1, hidden: false,  hideable: true, xtype: 'datecolumn',     format: self.ART_TIMESTAMP_FORMAT
//				,renderer: getExistingGridColumnRenderer
			},
//				{text: AgLang.upload_modified, dataIndex: 'art_upload_modified',stateId: 'art_upload_modified', width: 112,  hidden: true, hideable: true, xtype: 'datecolumn', format: self.FORMAT_DATE_TIME },
			{
				text: AgLang.cm_entry,     dataIndex: 'cm_entry',     stateId: 'cm_entry',      minWidth: self.ART_TIMESTAMP_WIDTH, flex: 1, hidden: true, hideable: true, xtype: 'datecolumn',     format: self.FORMAT_DATE
//				,renderer: getExistingGridColumnRenderer
			}
		];
	};

	var getStore = function(storeId){
		var store = Ext.data.StoreManager.lookup(storeId);
		if(!Ext.isEmpty(store)) return store;
		return Ext.create('Ext.data.Store', {
			storeId: storeId,
			model: 'PARTS',
			sorters    : [{
				property: 'depth',
				direction: 'DESC'
			}],
			proxy: Ext.create('Ext.data.proxy.Ajax',{
				type: 'ajax',
				timeout: 300000,
				pageParam: undefined,
				startParam: undefined,
				limitParam: undefined,
				sortParam: undefined,
				groupParam: undefined,
				filterParam: undefined,
				api: {
					create  : 'api-upload-file-list.cgi?cmd=create',
//					create  : 'api-upload-file-list.cgi?cmd=read',
					read    : 'api-upload-file-list.cgi?cmd=read',
					update  : 'api-upload-file-list.cgi?cmd=update_concept_art_map',
//					update  : 'api-upload-file-list.cgi?cmd=read',
					destroy : 'api-upload-file-list.cgi?cmd=destroy'
//					destroy  : 'api-upload-file-list.cgi?cmd=read'
				},
				actionMethods : {
					create : 'POST',
					read   : 'POST',
					update : 'POST',
					destroy: 'POST'
				},
				extraParams: {
					hideChildrenTerm: 1,
					hideAncestorTerm: 1,
					hideParentTerm: 1,
					hideDescendantsTerm: 1,
					hidePairTerm: 1,
				},
				reader: {
					type: 'json',
					root: 'datas',
					totalProperty: 'total',
					listeners: {
						exception : function(){
						}
					}
				},
				writer: {
					type: 'json',
					root: 'datas',
					allowSingle: false,
					encode: true
				},
				doRequest: function(operation, callback, scope) {
					var writer  = this.getWriter();
					var request = this.buildRequest(operation);
					if(operation.allowWrite()){
						request = writer.write(request);
					}
					Ext.apply(request, {
						binary        : this.binary,
						headers       : this.headers,
						timeout       : this.timeout,
						scope         : this,
						callback      : this.createRequestCallback(request, operation, callback, scope),
						method        : this.getMethod(request),
						disableCaching: false
					});
					if(this.request_object){
						Ext.Ajax.abort(this.request_object);
						delete this.request_object;
					}
					this.request_object = Ext.Ajax.request(request);
					return request;
				}
			}),
			listeners: {
				beforeload: function(store,operation,eOpts){
					if(!self.beforeloadStore(store)) return false;
					var p = store.getProxy();
					p.extraParams = p.extraParams || {};
					delete p.extraParams.current_datas;
					delete p.extraParams._ExtVerMajor;
					delete p.extraParams._ExtVerMinor;
					delete p.extraParams._ExtVerPatch;
					delete p.extraParams._ExtVerBuild;
					delete p.extraParams._ExtVerRelease;
				}
			}
		});
	};

	var func_subtoggle = function( button, pressed, eOpts, subname ){
//		console.log('func_subtoggle', button, pressed, eOpts, subname);
		var lastRecord = self.getLastRecord() || [];
		var subdata = lastRecord.get(subname);
		if(pressed){
			press_sub[button.text] = {
				prefix: button.prefix,
				subname: subname
			};
		}
		else{
			delete press_sub[button.text];
		}
//		console.log(button.text, pressed, press_sub);
//		console.log(Ext.getCmp('is_a_down'));
//		console.log(Ext.getCmp('regional_part_of_down'));
//		console.log(self.getLastRecord());
		var id = lastRecord.get(AgDef.ID_DATA_FIELD_ID);
		var name = lastRecord.get(AgDef.NAME_DATA_FIELD_ID);

		var panel = button.up('panel#sub_status_panel');
		var submit_button = panel ? panel.down('button#submit') : null;
		var sub_textfield = panel ? panel.down('textfield#sub') : null;
		var subid_textfield = panel ? panel.down('textfield#sub'+AgDef.ID_DATA_FIELD_ID) : null;
		var subname_textfield = panel ? panel.down('textfield#sub'+AgDef.NAME_DATA_FIELD_ID) : null;
		if(subname_textfield){
			if(pressed){
				var new_id = id+'-'+button.text;
				var new_name = button.prefix + ' ' + Ext.String.trim(name).toLowerCase();

				var subdatas = lastRecord.get(subname) || [];
				var subdata = Ext.Array.findBy(subdatas, function(item,index){
					if(item[AgDef.ID_DATA_FIELD_ID]==new_id) return true;
					return false;
				});
				if(Ext.isEmpty(subdata)){
/*
					var new_data = {};
					new_data[AgDef.ID_DATA_FIELD_ID] = new_id;
					new_data[AgDef.NAME_DATA_FIELD_ID] = new_name;
					subdatas.push(new_data);
					lastRecord.beginEdit();
					lastRecord.set(subname,subdatas);
					lastRecord.commit(false,[subname]);
					self._updateFiledData(subname,lastRecord);
*/
				}
				else{
					new_name = subdata[AgDef.NAME_DATA_FIELD_ID];
				}
				if(sub_textfield){
					sub_textfield.setValue(subname);
					sub_textfield.initValue();
				}
				if(subid_textfield){
					subid_textfield.setValue(new_id);
					subid_textfield.initValue();
				}
				subname_textfield.setDisabled(false);
				subname_textfield.suspendEvents(false);
				subname_textfield.setValue(new_name);
				subname_textfield.initValue();
				subname_textfield.resumeEvents();
				if(submit_button) submit_button.setDisabled(false);
			}
			else if(Ext.Object.getKeys(press_sub).length==0){
				if(sub_textfield){
					sub_textfield.setValue('');
					sub_textfield.initValue();
				}
				if(subid_textfield){
					subid_textfield.setValue('');
					subid_textfield.initValue();
				}
				subname_textfield.setDisabled(true);
				subname_textfield.suspendEvents(false);
				subname_textfield.setValue('');
				subname_textfield.initValue();
				subname_textfield.resumeEvents();
				if(submit_button) submit_button.setDisabled(true);
			}
		}

//							self._updateFiled(self.getLastRecord());
	};

	var func_subchange = function(textfield, newValue, oldValue, eOpts){
		var panel = textfield.up('panel#sub_status_panel');
//		console.log(panel,newValue,oldValue);
		var button = panel ? panel.down('button[toggleGroup="sub"][pressed=true]') : null;
		if(button){
		}
	}

	var center_center_panel = {
		region: 'center',
//		minWidth: 100,
		minHeight: 150,
//		maxHeight: 200,
//		height: center_panel_height,
		flex: 1,
		margin: '0 10 0 10',
		layout: {
			type: 'hbox',
			align: 'stretch',
			pack: 'center'
		},
		defaultType: 'panel',
		defaults: {
			frame: true,
			autoScroll: true
		},
		items: [getPanelConfig({
			id: 'is_a_up',
			title: 'has superclass (is a)',
			flex: 0.6
		}),{
			layout: 'border',
			flex: 1.8,
			margin: '0 1 0 1',
			border: false,
			items :[{
				border: false,
//				region: 'center',
				region: 'west',
				width: 374,
				layout: 'border',
				items: [{
					border: false,
					region: 'center',
					id: 'hierarchy_center',
//					title: 'aaa',
					autoScroll: true,
					bodyStyle: {
						textAlign: 'center',
						verticalAlign: 'middle'
					},
					dockedItems: [{
						hidden: false,
						xtype: 'toolbar',
						dock: 'top',
						items: ['->',{
							xtype: 'button',
							text: 'Synonym',
							iconCls: 'synonym_editing',
							tooltip: 'Synonym editing',
							disabled: true,
							listeners: {
								afterrender: function(button){
									var store = Ext.data.StoreManager.lookup(AgDef.CONCEPT_TERM_STORE_ID);
									var records = store.getRange();
//									console.log(records,records.length);
									store.on({
										load: {
											fn: function(store, records, successful, eOpts){
//												console.log(records, successful);
												if(successful && records.length==1){
													button.setDisabled(false);
												}
												else{
													button.setDisabled(true);
												}
											},
											buffer: 0
										}
									});
								},
								click: function(button, e, eOpts){
									var records = Ext.data.StoreManager.lookup(AgDef.CONCEPT_TERM_STORE_ID).getRange();
									if(records.length!=1){
										button.setDisabled(true);
										return;
									}

									var filterFn = function(record) {
										try{
											return record.get(AgDef.CDS_DELETED_DATA_FIELD_ID) === false;
										}catch(e){
											console.error(e);
											return false;
										}
									};
									var storeId = 'synonymStore';
									var synonym_store = Ext.data.StoreManager.lookup(storeId);
									if(Ext.isEmpty(synonym_store)){
										synonym_store = Ext.create('Ext.data.Store', {
											storeId: storeId,
											fields: [
												{
													name:AgDef.SYNONYM_DATA_FIELD_ID,
													type:'string',
													convert: function(v,record){
														if(Ext.isEmpty(v)){
															return record.get(AgDef.CS_NAME_DATA_FIELD_ID);
														}
														else{
															return v;
														}
													}
												},
												{
													name:AgDef.CDS_EDITED_DATA_FIELD_ID,
													type:'boolean',
													defaultValue: false
												},
												{
													name:AgDef.CDS_DELETED_DATA_FIELD_ID,
													type:'boolean',
													defaultValue: false
												},
												{
													name:AgDef.CDS_ADDED_DATA_FIELD_ID,
													type:'boolean',
													defaultValue: false
												},
												{
													name:AgDef.CDS_ADDED_AUTO_DATA_FIELD_ID,
													type:'boolean',
													defaultValue: false
												},
												{
													name:AgDef.CDS_ORDER_DATA_FIELD_ID,
													type:'int',
													defaultValue: 0
												},
												{
													name:AgDef.CS_NAME_DATA_FIELD_ID,
													type:'string',
													useNull: true,
													defaultValue: null
												},
												{
													name:AgDef.CS_ID_DATA_FIELD_ID,
													type:'int',
													useNull: true,
													defaultValue: null
												},
												{
													name:AgDef.CDS_ID_DATA_FIELD_ID,
													type:'int',
													useNull: true,
													defaultValue: null
												},
												{
													name:AgDef.CDS_BID_DATA_FIELD_ID,
													type:'int',
													useNull: true,
													defaultValue: null
												}
											],
											filters: [filterFn]
										});
									}
//									console.log(records[0].get('synonym')||[]);
									var loadRecords = [];
									if(Ext.isEmpty(records[0].get(AgDef.CDS_DATA_FIELD_ID))){
										loadRecords = Ext.Array.map(records[0].get(AgDef.SYNONYM_DATA_FIELD_ID)||[],function(synonym){
											var hash = {};
											hash[AgDef.CS_NAME_DATA_FIELD_ID] = synonym;
											return hash;
										});
									}
									else if(Ext.isArray(records[0].get(AgDef.CDS_DATA_FIELD_ID))){
										loadRecords = Ext.Array.clone(records[0].get(AgDef.CDS_DATA_FIELD_ID));
									}
//									console.log(loadRecords);
//									synonym_store.loadRecords( loadRecords );
									if(loadRecords.length>0){
										synonym_store.removeAll(true);
										synonym_store.add( loadRecords );
									}
									else{
										synonym_store.removeAll(false);
									}
//									console.log(synonym_store.getRange());

									Ext.create('Ext.window.Window', {
										title: button.tooltip,
										iconCls: button.iconCls,
										animateTarget: button.el,
										modal:true,
										height: parseInt(($(window).height()/5*3)),
										width: parseInt(($(window).width()/5*3)),
										minHeight: 300,
										minWidth: 500,
										layout: 'fit',
										items: [{
											xtype: 'gridpanel',
											border: true,
											columnLines: true,
											viewConfig: {
												stripeRows: true
											},
											columns: [{
												xtype: 'rownumberer'
											},{
												header: 'Synonym',
												dataIndex: AgDef.SYNONYM_DATA_FIELD_ID,
												draggable: false,
												hideable: false,
												resizable: false,
												sortable: true,
												flex: 1,
												editor: {
													xtype: 'textfield',
													allowBlank: false
												}
											},{
												xtype: 'checkcolumn',
												header: 'added',
												dataIndex: AgDef.CDS_ADDED_DATA_FIELD_ID,
												draggable: false,
												hideable: false,
												resizable: false,
												sortable: false,
												width: 50,
												listeners: {
													beforecheckchange: function(){
														return false;
													}
												}
											},{
												xtype: 'checkcolumn',
												header: 'auto',
												dataIndex: AgDef.CDS_ADDED_AUTO_DATA_FIELD_ID,
												draggable: false,
												hideable: false,
												resizable: false,
												sortable: false,
												width: 50,
												listeners: {
													beforecheckchange: function(){
														return false;
													}
												}
											}],
											store: synonym_store,
											selType: 'rowmodel',
											selModel: {
												mode: 'MULTI'
											},
											plugins: [
												Ext.create('Ext.grid.plugin.CellEditing', {
													clicksToEdit: 2
												})
											],
											listeners: {
												edit: function(editor, e, eOpts){
													var value = Ext.String.trim(e.value);
//													value = value.substr(0,1).toUpperCase() + value.substr(1).toLowerCase();
													e.record.set(AgDef.SYNONYM_DATA_FIELD_ID, value);
													if(value != e.record.get(AgDef.CS_NAME_DATA_FIELD_ID)){
														e.record.set(AgDef.CDS_EDITED_DATA_FIELD_ID, true);
													}else{
														e.record.set(AgDef.CDS_EDITED_DATA_FIELD_ID, false);
													}
													e.record.commit();
//													console.log(e.record.getData());
												}
											}
										}],
										dockedItems: [{
											xtype: 'toolbar',
											dock: 'top',
											defaults: {minWidth: 50},
											items: [{
												text: 'Add',
												itemId: 'add',
												listeners: {
													click: function(button){
														try{
															Ext.Msg.show({
																title:'Synonym',
																msg: 'Please enter the synonym to add',
																animateTarget: button.el,
																buttons: Ext.Msg.OKCANCEL,
																defaultFocus: 'cancel',
																icon: Ext.Msg.QUESTION,
																minWidth: 500,
																modal: true,
																prompt: true,
																fn: function(buttonId,text){
																	if (buttonId == 'ok' && Ext.isString(text) && Ext.String.trim(text).length>0){
																		var data = {};
																		text = Ext.String.trim(text);
//																		text = text.substr(0,1).toUpperCase() + text.substr(1).toLowerCase();
																		data[AgDef.SYNONYM_DATA_FIELD_ID] = text;
																		data[AgDef.CDS_ADDED_DATA_FIELD_ID] = true;
																		data[AgDef.CDS_EDITED_DATA_FIELD_ID] = true;
																		synonym_store.add(data);
																	}
																}
															});
														}catch(e){
														}
													}
												}
											},'->',{
												disabled: true,
												text: 'Delete',
												itemId: 'delete',
												listeners: {
													afterrender: function(button){
														var gridpanel = button.up('window').down('gridpanel');
														var selmodel = gridpanel.getSelectionModel();
														selmodel.on({
															selectionchange: function( selmodel, selected, eOpts ){
																button.setDisabled(selected.length>0 ? false : true);
															}
														});
													},
													click: function(button){
														try{
															var gridpanel = button.up('window').down('gridpanel');
															var store = gridpanel.getStore();
															var selmodel = gridpanel.getSelectionModel();
															var remove_records = [];
															Ext.Array.each(selmodel.getSelection(), function(record){
																if(Ext.isEmpty(record.get(AgDef.CS_NAME_DATA_FIELD_ID))){
																	remove_records.push(record);
																}
																else{
																	record.beginEdit();
																	record.set(AgDef.CDS_DELETED_DATA_FIELD_ID,true);
																	record.commit(true,[AgDef.CDS_DELETED_DATA_FIELD_ID]);
																	record.endEdit(true,[AgDef.CDS_DELETED_DATA_FIELD_ID]);
//																	console.log(record.getData());
																}
															});
															if(remove_records.length>0){
																store.remove(remove_records);
															}
															store.filter();
														}catch(e){
														}
													}
												}
											}]
										},{
											xtype: 'toolbar',
											dock: 'bottom',
											ui: 'footer',
											defaults: {minWidth: 60},
											items: ['->',{
												text: 'Save',
												itemId: 'save',
												listeners: {
													click: function(button){
														try{
															var win = button.up('window');
															var chg_synonym_arr = Ext.Array.map(synonym_store.getRange(), function(record){ return record.get('synonym'); });
//															console.log(chg_synonym_arr);
//															return;
															var store = Ext.data.StoreManager.lookup(AgDef.CONCEPT_TERM_STORE_ID);
															var record = store.getRange()[0];
															var org_synonym_arr = record.get('synonym')||[];
															if(Ext.Array.equals(org_synonym_arr,chg_synonym_arr)){
																button.up('window').close();
																return;
															}

															var params = {};
															params[AgDef.LOCATION_HASH_CIID_KEY] = record.get(AgDef.CONCEPT_INFO_DATA_FIELD_ID);
															params[AgDef.LOCATION_HASH_CBID_KEY] = record.get(AgDef.CONCEPT_BUILD_DATA_FIELD_ID);
															params[AgDef.ID_DATA_FIELD_ID] = record.get(AgDef.ID_DATA_FIELD_ID);
//															params[AgDef.SYNONYM_DATA_FIELD_ID] = Ext.JSON.encode(chg_synonym_arr);
															synonym_store.clearFilter(true);
//															console.log(synonym_store.filters);
															params[AgDef.SYNONYM_DATA_FIELD_ID] = Ext.JSON.encode(Ext.Array.map(synonym_store.getRange(), function(record){
																return record.getData();
															}));
															synonym_store.filter({filterFn:filterFn});

															win.setLoading(true);

															Ext.Ajax.request({
																url: 'api-fma-list.cgi?cmd=update_synonym',
																timeout: 300000,
																params: params,
																success: function(response){
																	win.setLoading(false);
																	var rtn = Ext.decode(response.responseText);
																	if(Ext.isObject(rtn)){
																		if(rtn.success){
																			win.close();
																			self.loadRecord(record.get(AgDef.ID_DATA_FIELD_ID));
																		}
																		else if(Ext.isString(rtn.msg) && rtn.msg.length){
																			Ext.Msg.show({
																				title: button.text,
																				msg: rtn.msg,
																				buttons: Ext.Msg.OK,
																				icon: Ext.Msg.ERROR,
																				fn: function(buttonId,text,opt){
																				}
																			});
																		}
																		else{
																			Ext.Msg.show({
																				title: button.text,
																				msg: 'Unknown error',
																				buttons: Ext.Msg.OK,
																				icon: Ext.Msg.ERROR,
																				fn: function(buttonId,text,opt){
																				}
																			});
																		}
																	}
																	else{
																		Ext.Msg.show({
																			title: button.text,
																			msg: 'Unknown error',
																			buttons: Ext.Msg.OK,
																			icon: Ext.Msg.ERROR,
																			fn: function(buttonId,text,opt){
																			}
																		});
																	}
																},
																failure: function(response, opts) {
																	win.setLoading(false);
																	Ext.Msg.show({
																		title: button.text,
																		msg: 'server-side failure with status code ' + response.status,
																		buttons: Ext.Msg.OK,
																		icon: Ext.Msg.ERROR,
																		fn: function(buttonId,text,opt){
																		}
																	});
																}
															});

														}catch(e){
															console.error(e);
														}
													}
												}
											},{
												text: 'Cancel',
												itemId: 'cancel',
												listeners: {
													click: function(button){
														try{
//															synonym_store.rejectChanges();
															button.up('window').close();
														}catch(e){
														}
													}
												}
											}]
										}]
									}).show();


								}
							}
						}]
					},{
						hidden: true,
						xtype: 'toolbar',
						dock: 'bottom',
						items: ['->',{
							xtype: 'tbtext',
							style: 'cursor:default;font-size:2em',
							text: 'drag:'
						},{
							xtype: 'buttongroup',
							defaultType: 'radiofield',
							items: [{
								id: 'dragtype-url',
								boxLabel: 'URL',
								name: 'dragtype',
								inputValue: 'url'
							},{
								boxLabel: 'TEXT',
								name: 'dragtype',
								inputValue: 'text',
								checked: true
							}]
						}]
					}]
				},{
					id: 'sub_status_panel',
					itemId: 'sub_status_panel',
					region: 'south',
					height: 92,
					bodyPadding: '2 2 0 2',
					layout: {
						type: 'vbox',
						align: 'stretch',
						pack: 'center'
					},
					defaults: {
						flex: 1,
						labelAlign: 'right'
					},
					items: [{
						xtype: 'fieldcontainer',
						fieldLabel: 'Make subclass',
						labelWidth: 91,
						layout: {
							type: 'hbox',
							align: 'middle',
							pack: 'start'
						},
						defaultType: 'button',
						defaults: {
							enableToggle: true,
							toggleGroup: 'sub',
							listeners: {
								toggle: Ext.bind(func_subtoggle, self, ['is_a_down'], true)
							}
						},
						items: subclass_items
					},{
						xtype: 'fieldcontainer',
						fieldLabel: 'Make subpart(reginal po)',
						labelWidth: 150,
						layout: {
							type: 'hbox',
							align: 'middle',
							pack: 'start'
						},
						defaultType: 'button',
						defaults: {
							enableToggle: true,
							toggleGroup: 'sub',
							listeners: {
								toggle: Ext.bind(func_subtoggle, self, ['regional_part_of_down'], true)
							}
						},
						items: subpart_items
					},{
						xtype: 'fieldcontainer',
						layout: {
							type: 'hbox',
							align: 'stretch',
							pack: 'center'
						},
						items: [{
							hidden: true,
							flex: 1,
							xtype: 'textfield',
							itemId: 'sub'
						},{
							hidden: true,
							flex: 1,
							xtype: 'textfield',
							itemId: 'sub'+AgDef.ID_DATA_FIELD_ID
						},{
							flex: 1,
							xtype: 'textfield',
							itemId: 'sub'+AgDef.NAME_DATA_FIELD_ID,
							emptyText: 'Change name to',
							listeners: {
								change: Ext.bind(func_subchange, self)
							}
						},{
							itemId: 'submit',
							xtype: 'button',
							disabled: true,
							text: 'ok',
							listeners: {
								click: function(button){
									var panel = button.up('panel#sub_status_panel');
									var sub_textfield = panel ? panel.down('textfield#sub') : null;
									var subid_textfield = panel ? panel.down('textfield#sub'+AgDef.ID_DATA_FIELD_ID) : null;
									var subname_textfield = panel ? panel.down('textfield#sub'+AgDef.NAME_DATA_FIELD_ID) : null;
									if(sub_textfield && subid_textfield && subname_textfield){
										var subname = sub_textfield.getValue();
										var new_id = subid_textfield.getValue();
										var new_name = subname_textfield.getValue();
										var lastRecord = self.getLastRecord() || [];
										var subdatas = lastRecord.get(subname) || [];
										var subdata = Ext.Array.findBy(subdatas, function(item,index){
											if(item[AgDef.ID_DATA_FIELD_ID]==new_id) return true;
											return false;
										});
										if(Ext.isEmpty(subdata)){
											var new_data = {};
											new_data[AgDef.ID_DATA_FIELD_ID] = new_id;
											new_data[AgDef.NAME_DATA_FIELD_ID] = new_name;
											subdatas.push(new_data);
										}
										else{
											subdata[AgDef.NAME_DATA_FIELD_ID] = new_name;
										}
										lastRecord.beginEdit();
										lastRecord.set(subname,subdatas);
										lastRecord.commit(false,[subname]);
										self._updateFiledData(subname,lastRecord);

										var params = self.getExtraParams() || {};
										params[AgDef.ID_DATA_FIELD_ID] = new_id;
										params[AgDef.NAME_DATA_FIELD_ID] = new_name;

										Ext.Ajax.request({
											url: 'api-fma.cgi',
											method: 'POST',
											timeout: 300000,
											params: params,
											callback: function(options,success,response){

												var json;
												try{json = Ext.decode(response.responseText)}catch(e){};
												if(success==false || Ext.isEmpty(json) || Ext.isEmpty(json.success) || json.success==false){
													if(Ext.isEmpty(json) || Ext.isEmpty(json.msg)) return;
													Ext.Msg.show({
														title: 'Error',
														msg: json.msg,
														buttons: Ext.Msg.OK,
														icon: Ext.Msg.ERROR
													});
													return;
												}

											}
										});

									}
								}
							}
						}]
					}]
				}]
			},{
//				region: 'east',
//				width: 232,
				region: 'center',



				xtype: 'gridpanel',
				itemId: 'existing-attribute-gridpanel',
				id: idPrefix+'existing-attribute-gridpanel',
				stateId: idPrefix+'existing-attribute-gridpanel',
				store: getStore(existingAttributeStoreId),
				columnLines: true,
				columns: getExistingGridColumns(),
/*
				viewConfig: {
					stripeRows:true,
//					allowCopy: true,
					plugins: {
						ptype: 'gridviewdragdrop',
						ddGroup: 'dd-upload_folder_tree',
						enableDrag: false,
						enableDrop: true
					},
					listeners: {
						beforedrop: function(node, data, overModel, dropPosition, dropHandlers) {
							var view = this;
							dropHandlers.cancelDrop();
//							console.log(node, data, overModel, dropPosition, dropHandlers);
							if(Ext.isObject(data) && Ext.isArray(data.records) && data.records.length>0){
							}
							return false;
						}
					}
				},
*/
				plugins: [self.getBufferedRenderer()],
				selType: 'rowmodel',
				selModel: {
					mode:'MULTI'
				},
				dockedItems: [{
					xtype: 'toolbar',
					dock: 'top',
					items: [{
						hidden: true,
						xtype: 'tbtext',
						text: '<b>'+AgLang.existing_attribute+'</b>',
					},{
						hidden: true,
						xtype: 'tbseparator'
					},getHideParentTermCheckbox(),{
						hidden: true,
						xtype: 'tbseparator'
					},getNeverCurrentButton(),{
						hidden: false,
						xtype: 'tbseparator'
					},getRemoveMappingButton(),{
						hidden: false,
						xtype: 'tbseparator'
					},'->',{
						hidden: true,
						xtype: 'tbseparator'
					},{
						hidden: false,
						xtype: 'button',
						disabled: true,
						tooltip: 'Download_Selected',
						iconCls: 'pallet_download',
						listeners: {
							afterrender: function(button){
								var gridpanel = button.up('gridpanel');
								gridpanel.on('selectionchange',function(selModel,selected,eOpts){
									var disabled = true;
									if(Ext.isArray(selected) && selected.length){
										disabled = false;
									}
									button.setDisabled(disabled);
								});
							},
							click: function(button){

								button.setDisabled(true);

								var gridpanel = button.up('gridpanel');
								var selModel = gridpanel.getSelectionModel();
								var recs = selModel.getSelection();
								if(Ext.isEmpty(recs)){
									button.setDisabled(false);
									return;
								}
								selModel.deselectAll();
								selModel.select(recs);
								button.setDisabled(true);

								self.downloadObjectsTask.delay(10,self.downloadObjects,self,[{
									type: 'objects',
									records: recs,
									callback: function(){
										button.setDisabled(false);
									}
								}]);

							}
						}
					},{
						hidden: true,
						xtype: 'tbseparator'
					},{
						hidden: true,
						text: 'Submit'
					}]
				}],
				listeners: {
					afterrender: function(gridpanel){
						if(Ext.isChrome){
							gridpanel.columns.forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
							var store = gridpanel.getStore();
							store.on({
								load: {
									fn: function(){
										gridpanel.columns.forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
									},
									buffer: 0
								}
							});
						}


						var el = gridpanel.getView().getEl();
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
								var dropData = null;
								if(dataTransfer && dataTransfer.getData){
									try{dropData = Ext.decode(dataTransfer.getData('text/plain'));}catch(e){}
								}
								if(Ext.isArray(dropData) && dropData.length) dropData = dropData[0];
//								console.log(dropData.cdi_name);
								var lastRecord = self.getLastRecord();
//								console.log(lastRecord.get('id'));
								var dropRecord = Ext.create('PARTS',Ext.Object.merge({},dropData||{},{cdi_name:lastRecord.get('id'), cmp_id:0, current_use: false}));
//								var dropRecord = Ext.create('PARTS',Ext.Object.merge({},dropData||{}));
//								console.log(dropRecord.get('cdi_name'));

								var store = gridpanel.getStore();
								var add_records = store.add(dropRecord.getData());

//								console.log(store.getNewRecords(),store.getModifiedRecords(),store.getUpdatedRecords(),store.getRemovedRecords());
								if(store.getNewRecords().lenth>0 || store.getModifiedRecords().length>0 || store.getUpdatedRecords().length>0 || store.getRemovedRecords().length>0){
									store.sync({
										callback: function(batch,options){
//											console.log('callback');
/*
											store.loadPage(1,{
												params: {
													cdi_name: lastRecord.get('id')
												}
											});
*/
										},
										success: function(batch,options){
//											console.log('success');
											store.reload();
										},
										failure: function(batch,options){
//											console.log('failure');
											store.rejectChanges();

											var msg = AgLang.error_submit;
											var proxy = this;
											var reader = proxy.getReader();
											if(reader && reader.rawData && reader.rawData.msg){
												msg += ' ['+reader.rawData.msg+']';
											}
											Ext.Msg.show({
												title: 'Draggable',
												iconCls: 'gridcolumn_current_none_use',
												msg: msg,
												buttons: Ext.Msg.OK,
												icon: Ext.Msg.ERROR,
												fn: function(buttonId,text,opt){
												}
											});

										}
									});
								}

/*
								field.update(dropRecord.getData());
								setLastRecord(dropRecord);
								loadAttributePage();
*/
							}
						});


					},
					columnhide: function(ct, column, eOpts){
						if(Ext.isChrome) ct.getGridColumns().forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
					},
					columnshow: function(ct, column, eOpts){
						if(Ext.isChrome) ct.getGridColumns().forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
					}
				}


















			}],
		},getPanelConfig({
			id: 'is_a_down',
			title: 'has subclass',
			flex: 0.6,
		})],
		listeners: {
			resize: function(comp,adjWidth,adjHeight,rawWidth,rawHeight){
			}
		}
	};


	var center_panel = {
		itemId: 'has-class',
		region: 'center',
		autoScroll: true,
		layout: {
			type: 'vbox',
			align: 'stretch',
			pack: 'center'
		},
		defaultType: 'panel',
		defaults: {
			border: false,
		},
		items: [north_panel,center_center_panel,south_panel],
	};

	var west_panel = {
		hidden: true,
		region: 'west',
		title: 'Upper classes',
		width: 600,
		collapsed: true,
		collapsible: true,
		hideCollapseTool: true,
		headerPosition: 'right',
	};
/*
	var upload_object_grid = Ext.create('Ext.grid.Panel',{
//		title: self.TITLE_UPLOAD_OBJECT,
		id: 'upload-object-grid',
		region: 'center',
//		region: 'south',
//		split: true,
//		height: self.panelHeight-100,
//		height: 250,
		flex: 2,
		minHeight: 150,
		columnLines: true,
		store: 'uploadObjectStore',
		stateful: true,
		stateId: 'upload-object-grid',
//		plugins: [self.getCellEditing(),self.getBufferedRenderer()],
		plugins: [self.getBufferedRenderer()],
		columns: [
			{text: '&#160;',            dataIndex: 'selected',     stateId: 'selected',      width: 40, minWidth: 40, hidden: true, hideable: false, sortable: true, draggable: false, resizable: false, xtype: 'agselectedcheckcolumn'},

			{
				text: AgLang.current,      dataIndex: 'current_use',       stateId: 'current_use',        width: 46, minWidth: 46, hidden: false, hideable: false, sortable: false, draggable: false, resizable: false,
				renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
					var tdCls = [];
					if(value){
						tdCls.push('gridcolumn_current_use');
					}
					else if(Ext.isEmpty(record.get('cdi_name'))){
						metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(self.TOOLTIP_FMAID_NOT_SUPPORTED) + '"';
					}
					else{
						tdCls.push('gridcolumn_current_none_use');
						if(Ext.isString(record.get('current_use_reason'))) metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(record.get('current_use_reason')) + '"';
					}
					if(Ext.isString(metaData.tdCls) && metaData.tdCls.length){
						metaData.tdCls += ' ' + tdCls.join(' ');
					}else{
						metaData.tdCls = tdCls.join(' ');
					}
					return '';
				}
			},

			{
				text: '&#160;',            dataIndex: 'art_tmb_path',     stateId: 'art_tmb_path',      width: 34, minWidth: 34, hidden: false, hideable: false, sortable: false, draggable: false, resizable: false,
				renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
					if(record.data.seg_color){
//						metaData.style = 'background:'+record.data.seg_color+';';
					}
					metaData.innerCls = 'art_tmb_path';
					return value;
				}
			},

			{text: AgLang.art_id,       dataIndex: 'art_id',       stateId: 'art_id',        width: 60, minWidth: 60, hidden: false, hideable: true},
			{text: AgLang.cdi_name,     dataIndex: 'cdi_name',     stateId: 'cdi_name',      width: 80, minWidth: 80, hidden: true,  hideable: true, xtype: 'agcolumncdiname' },
			{text: AgLang.cmp_abbr,     dataIndex: 'cmp_id',       stateId: 'cmp_id',        width: 40, minWidth: 40, hidden: true,  hideable: true, xtype: 'agcolumnconceptartmappart' },
			{text: AgLang.cdi_name_e,   dataIndex: 'cdi_name_e',   stateId: 'cdi_name_e',    flex: 2.0, minWidth: 80, hidden: true,  hideable: true, xtype: 'agcolumncdinamee' },

			{text: 'System',            dataIndex: 'seg_name',     stateId: 'seg_name',      flex: 1.0, minWidth: 50, hidden: true,  hideable: true,  xtype: 'agsystemcolumn'},

			{text: AgLang.category,     dataIndex: 'arta_category',stateId: 'arta_category', flex: 1.0, minWidth: 50, hidden: false, hideable: true},
			{text: AgLang.class_name,   dataIndex: 'arta_class',   stateId: 'arta_class',    width: 36, minWidth: 36, hidden: false, hideable: true},
			{text: AgLang.comment,      dataIndex: 'arta_comment', stateId: 'arta_comment',  flex: 2.0, minWidth: 80, hidden: false, hideable: true},
			{text: AgLang.judge,        dataIndex: 'arta_judge',   stateId: 'arta_judge',    flex: 1.0, minWidth: 50, hidden: false, hideable: true},

			{text: AgLang.arto_id,      dataIndex: 'arto_id',      stateId: 'arto_id',       width: 60, minWidth: 60, hidden: true, hideable: true, sortable: false},
			{text: AgLang.arto_filename,dataIndex: 'arto_filename',stateId: 'arto_filename', flex: 2.0, minWidth: 80, hidden: true, hideable: true, sortable: false},
			{text: AgLang.arto_comment, dataIndex: 'arto_comment', stateId: 'arto_comment',  flex: 2.0, minWidth: 80, hidden: true, hideable: true, sortable: false},

			{text: 'Color',             dataIndex: 'color',        stateId: 'color',         width: 40, minWidth: 40, hidden: true,  hideable: false,  xtype: 'agcolorcolumn'},
			{text: 'Opacity',           dataIndex: 'opacity',      stateId: 'opacity',       width: 44, minWidth: 44, hidden: true,  hideable: false,  xtype: 'agopacitycolumn'},
			{text: 'Hide',              dataIndex: 'remove',       stateId: 'remove',        width: 40, minWidth: 40, hidden: true,  hideable: false,  xtype: 'agcheckcolumn'},
			{text: 'Scalar',            dataIndex: 'scalar',       stateId: 'scalar',        width: 40, minWidth: 40, hidden: true,  hideable: false,  xtype: 'agnumbercolumn', format: '0', editor: 'numberfield'},

			{text: AgLang.file_name,    dataIndex: 'art_filename', stateId: 'art_filename',  flex: 2.0, minWidth: 80, hidden: false, hideable: true},
			{text: 'Path',              dataIndex: 'art_path',     stateId: 'art_path',      flex: 1.0, minWidth: 50, hidden: true,  hideable: false},
			{text: AgLang.file_size,    dataIndex: 'art_data_size',stateId: 'art_data_size', width: 59,  hidden: true, hideable: true, xtype: 'agfilesizecolumn'},

			{text: AgLang.xmax,         dataIndex: 'art_xmax',     stateId: 'art_xmax',      width: 59,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.xmin,         dataIndex: 'art_xmin',     stateId: 'art_xmin',      width: 59,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.xcenter,      dataIndex: 'art_xcenter',  stateId: 'art_xcenter',   width: 59,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.ymax,         dataIndex: 'art_ymax',     stateId: 'art_ymax',      width: 59,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.ymin,         dataIndex: 'art_ymin',     stateId: 'art_ymin',      width: 59,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.ycenter,      dataIndex: 'art_ycenter',  stateId: 'art_ycenter',   width: 59,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.zmax,         dataIndex: 'art_zmax',     stateId: 'art_zmax',      width: 59,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.zmin,         dataIndex: 'art_zmin',     stateId: 'art_zmin',      width: 59,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.zcenter,      dataIndex: 'art_zcenter',  stateId: 'art_zcenter',   width: 59,  hidden: false, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.volume,       dataIndex: 'art_volume',   stateId: 'art_volume',    width: 59,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},

			{text: AgLang.timestamp,    dataIndex: 'art_timestamp',stateId: 'art_timestamp', width: self.ART_TIMESTAMP_WIDTH,  hidden: false, hideable: true, xtype: 'datecolumn',     format: self.ART_TIMESTAMP_FORMAT },
			{text: AgLang.upload_modified, dataIndex: 'art_upload_modified',stateId: 'art_upload_modified', width: 112,  hidden: false, hideable: true, xtype: 'datecolumn',     format: self.FORMAT_DATE_TIME }
		],

		viewConfig: {
			stripeRows:true,
			enableTextSelection:false,
			loadMask:true,
			allowCopy: true,
			plugins: [{
				ddGroup: 'dd-upload_folder_tree',
				ptype: 'gridviewdragdrop',
				enableDrag: true,
				enableDrop: false
			}]
		},
		selType: 'rowmodel',
		selModel: {
			mode:'MULTI'
		},

		dockedItems: [{
			xtype: 'toolbar',
			dock: 'top',
//			layout: {
//				overflowHandler: 'Menu'
//			},
			items:[{
				xtype: 'tbtext',
				text: '<b>'+self.TITLE_UPLOAD_OBJECT+'</b>'
			},'-',

			'->','-',{
				itemId: 'download',
				xtype: 'button',
				tooltip: 'Download Selected',
				iconCls: 'pallet_download',
				disabled:true,
				listeners: {
					click: function(b){
						b.setDisabled(true);

						var gridpanel = b.up('gridpanel');
						var selModel = gridpanel.getSelectionModel();
						var recs = selModel.getSelection();
						if(Ext.isEmpty(recs)){
							b.setDisabled(false);
							return;
						}
						selModel.deselectAll();
						selModel.select(recs);
						b.setDisabled(true);

						self.downloadObjectsTask.delay(10,self.downloadObjects,self,[{
							type: 'objects',
							records: recs,
							callback: function(){
								b.setDisabled(false);
							}
						}]);
					}
				}
			},'-',{
				itemId: 'reload',
				xtype: 'button',
				iconCls: 'x-tbar-loading',
				listeners: {
					click: function(b){
						var gridpanel = b.up('gridpanel');
						var view = gridpanel.getView();
						view.saveScrollState();
						var store = gridpanel.getStore();
						store.loadPage(1,{callback: function(records,operation,success){
							view.restoreScrollState();
						}});
					}
				}
			}
			]
		}],
		listeners: {
			selectionchange: function(selModel,selected,eOpts){
				var gridpanel = this;
				var toolbar = selModel.view.up('gridpanel').getDockedItems('toolbar[dock="top"]')[0];
				var disabled = Ext.isEmpty(selected);
				toolbar.getComponent('download').setDisabled(disabled);
			},
			afterrender: function(gridpanel){
				if(Ext.isChrome){
					gridpanel.columns.forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
					gridpanel.getStore().on('load',function(){
						gridpanel.columns.forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
					});
				}
			},
			containercontextmenu : function(view,e,eOpts){
				e.stopEvent();
				return false;
			},
			beforeitemcontextmenu: function( view, record, item, index, e, eOpts ){
				e.stopEvent();
				return false;
			},
			itemcontextmenu: {
				fn: self.showPalletItemContextmenu,
				scope: self
			}
		}
	});
/*
/*
	var upload_folder_tree = Ext.create('Ext.tree.Panel', {
		title: self.TITLE_UPLOAD_FOLDER,
		id: 'upload-folder-tree',
		region: 'north',
		flex: 1,
		minHeight: 150,
		stateId: 'upload-folder-tree',
		stateEvents: ['resize'],
		stateful: false,
		split: true,
		store: 'uploadFolderTreePanelStore',

		hideHeaders: true,
		columns: [{
			xtype: 'treecolumn',
			stateId: 'artf_name',
			flex: 1,
			hidden: false,
			hideable: false,
			sortable: false,
			resizable: false,
			dataIndex: 'text'
		},{
			xtype: 'agnumbercolumn',
			stateId: 'art_count',
			width: 40,
			hidden: false,
			hideable: false,
			sortable: false,
			resizable: false,
			format: '0',
			align: 'right',
			dataIndex: 'art_count'
		}],
		selModel: {
			mode:'SINGLE',
			listeners: {
				selectionchange : function(selModel,selected,eOpts){
					var treepanel = selModel.view.panel;
					var toolbar = treepanel.getDockedItems('toolbar[dock="top"]')[0];
					toolbar.getComponent('download').disable();
					if(selModel.getCount()>0){
						toolbar.getComponent('download').enable();
					}
				}
			}
		},
		dockedItems: [{
			dock: 'top',
			xtype: 'toolbar',
			layout: {
				overflowHandler: 'Menu'
			},
			items: [
				,self.getObjSearchButton(),'-',
				,'->',
				'-',{
					itemId: 'download',
					xtype: 'button',
					tooltip: 'Download Selected',
					iconCls: 'pallet_download',
					disabled:true,
					listeners: {
						click: function(b){
							b.setDisabled(true);

							var treepanel = b.up('treepanel');
							var selModel = treepanel.getSelectionModel();
							var recs = selModel.getSelection();
							if(Ext.isEmpty(recs)){
								b.setDisabled(false);
								return;
							}
							selModel.deselectAll();
							selModel.select(recs);
							b.setDisabled(true);

							var filename = (recs.length===1 ? recs[0].get('artf_name') + '_objects_'+Ext.util.Format.date(new Date(),'YmdHis') : null);
							if(Ext.isDefined(filename)) filename = filename.replace(/[^A-Za-z0-9]/g,'_');

							self.downloadObjectsTask.delay(10,self.downloadObjects,self,[{
								type: 'folder',
								records: recs,
								filename: filename,
								callback: function(){
									b.setDisabled(false);
								}
							}]);
						}
					}
				},'-',' '


			,'-',{
				itemId: 'reload',
				xtype: 'button',
				iconCls: 'x-tbar-loading',
				listeners: {
					click: function(b){
						var treepanel = b.up('treepanel');
						var store = treepanel.getStore();
						var selModel = treepanel ? treepanel.getSelectionModel() : null;
						var node = selModel ? selModel.getSelection()[0] : null;
						if(node){
							if(node.isRoot()){
								store.load({node:node});
							}else{
								store.load({
									node:node,
									callback: function(records,operation,success){
										if(success){
											Ext.data.StoreManager.lookup('uploadObjectStore').loadPage(1);
										}
									}
								});
							}
						}else{
							store.load();
						}
					}
				}
			}]
		}],
		listeners: {
			afterrender: function( panel, eOpts ){
			},
			beforeload: function( store, operation, eOpts ){
				var sel_node = operation.node ? operation.node : this.getSelectionModel().getLastSelected();
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				if(sel_node){
					p.extraParams.artf_pid = sel_node.get('artf_id');
				}else{
					delete p.extraParams.artf_pid;
				}
			},
			load: function(){
				var store, records, successful, operation, node, eOpts, i=0;
				if(Ext.getVersion().major>=5){
					store = arguments[i++];
					records = arguments[i++];
					successful = arguments[i++];
					operation = arguments[i++];
					node = arguments[i++];
					eOpts = arguments[i++];
				}else{
					store = arguments[i++];
					node = arguments[i++];
					records = arguments[i++];
					successful = arguments[i++];
					eOpts = arguments[i++];
				}
				if(successful && node.isRoot()){
					var treepanel = this;
					var path = node.getPath('artf_name');
					upload_folder_tree.getSelectionModel().deselectAll();
					upload_folder_tree.selectPath(path,'artf_name',null,function(bSuccess, oLastNode){
						if(bSuccess){
							var proxy = store.getProxy();

							Ext.Ajax.request({
								url: proxy.api.read+'_art_count',
								method: proxy.actionMethods.read,
								timeout: proxy.timeout,
								params: {
									artf_id: node.get('artf_id')
								},
								callback: function(options,success,response){
									var json;
									try{json = Ext.decode(response.responseText)}catch(e){};
									if(success==false || Ext.isEmpty(json) || Ext.isEmpty(json.success) || json.success==false){
										if(Ext.isEmpty(json) || Ext.isEmpty(json.msg)) return;
										Ext.Msg.show({
											title: title,
											msg: json.msg,
											buttons: Ext.Msg.OK,
											icon: Ext.Msg.ERROR
										});
										return;
									}
									store.suspendAutoSync();
									try{
										node.beginEdit();
										node.set('art_count',json.art_count);
										node.endEdit(false,['art_count']);
										node.commit(false,['art_count']);
									}catch(e){
										console.warn(e);
									}
									store.resumeAutoSync();
									var selModel = treepanel.getSelectionModel();
									selModel.fireEvent('selectionchange',selModel,selModel.getSelection());
								}
							});
						}else{
							console.warn('upload_folder_tree.selectPath():['+path+']:['+bSuccess+']');
						}
					});
				}

				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.artf_pid;
			},
			selectionchange: function( selModel, selected, eOpts ){
			},
			deselect: function( selModel, record, eOpts ){
				var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
				var p = uploadObjectStore.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.select_all;
				delete p.extraParams.artf_id;
			},
			select: function( selModel, record, index, eOpts ){

				var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
				var p = uploadObjectStore.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.select_all;
				p.extraParams.artf_id = record.get('artf_id');
				uploadObjectStore.loadPage(1);
				var obj = {};
				if(self.AgLocalStorage.exists(self.DEF_LOCALDB_FOLDER_INFO)) obj = Ext.decode(self.AgLocalStorage.load(self.DEF_LOCALDB_FOLDER_INFO));
				obj['selected'] = record.getPath('artf_name');
				self.AgLocalStorage.save(self.DEF_LOCALDB_FOLDER_INFO,Ext.encode(obj));
			},


			itemappend: function(node,newNode,index,eOpts){
				if(!newNode.isExpanded()){
					var obj = {};
					if(self.AgLocalStorage.exists(self.DEF_LOCALDB_FOLDER_INFO)) obj = Ext.decode(self.AgLocalStorage.load(self.DEF_LOCALDB_FOLDER_INFO));
					obj['expand'] = obj['expand'] || {};
					var artf_id = newNode.get('artf_id');
					if(obj['expand'][artf_id]){// || node.internalId=='root'){
						newNode.expand();
					}
				}
			},
			itemcollapse: function(node,eOpts){
				var tree_panel = this;
				var obj = {};
				if(self.AgLocalStorage.exists(self.DEF_LOCALDB_FOLDER_INFO)) obj = Ext.decode(self.AgLocalStorage.load(self.DEF_LOCALDB_FOLDER_INFO));
				obj['expand'] = obj['expand'] || {};
				var artf_id = node.get('artf_id');
				delete obj['expand'][artf_id];
				self.AgLocalStorage.save(self.DEF_LOCALDB_FOLDER_INFO,Ext.encode(obj));

				Ext.defer(function(){
					node.collapseChildren(true);
				},100);

				var sel_node = tree_panel.getSelectionModel().getLastSelected();
				if(sel_node && sel_node!=node){
					var child_node = node.findChild( 'artf_id', sel_node.get('artf_id'), true );
//					if(child_node) tree_panel.getSelectionModel().deselect([sel_node]);
					if(child_node) tree_panel.getSelectionModel().select([node]);
				}
			},
			itemexpand: function(node,eOpts){
				var obj = {};
				if(self.AgLocalStorage.exists(self.DEF_LOCALDB_FOLDER_INFO)) obj = Ext.decode(self.AgLocalStorage.load(self.DEF_LOCALDB_FOLDER_INFO));
				obj['expand'] = obj['expand'] || {};
				var artf_id = node.get('artf_id');
				obj['expand'][artf_id] = true;
				self.AgLocalStorage.save(self.DEF_LOCALDB_FOLDER_INFO,Ext.encode(obj));
			},
			itemcontextmenu: function(treepanel, record, item, index, e, eOpts){
				e.stopEvent();
				var xy = e.getXY();
				xy[0] += 2;
				xy[1] += 2;
				if(self.contextMenu && self.contextMenu.upload_folder) self.contextMenu.upload_folder.showAt(xy);
			}
		}
	});
*/
	var east_panel = {
		hidden: true,
		region: 'east',
		title: 'Semantic category of obj lineage',
		width: 350,
		collapsed: false,
		collapsible: true,
		hideCollapseTool: false,
		split: true,
		headerPosition: 'left',
/*
		layout: 'border',
		items:[
			upload_folder_tree,
			upload_object_grid
		]
*/
	};

	//layout:window
	var viewport_items = [{
		id: 'window-panel',
		bodyStyle: 'background:#aaa;',
		minHeight: 360,
		layout: 'border',
		dockedItems: view_dockedItems,
		defaultType: 'panel',
		items: [center_panel,west_panel,east_panel],
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
//				Ext.data.StoreManager.lookup('uploadFolderTreePanelStore').load();

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

//								Ext.data.StoreManager.lookup(existingAttributeStoreId).loadPage(1,{params:{cdi_name:hashId}});
				}
				if(field){
/**/
					var store = Ext.data.StoreManager.lookup(AgDef.CONCEPT_TERM_STORE_ID);
					if(store){
/*
						store.on({
							load: function(){
								Ext.data.StoreManager.lookup('uploadFolderTreePanelStore').load();
							},
							single: true
						});
*/
						store.on({
							load: function(){
								var hash = self.getLocationHash();
								var hashId     = self.isEmpty(hash[AgDef.LOCATION_HASH_ID_KEY])     ? null : Ext.String.trim(hash[AgDef.LOCATION_HASH_ID_KEY]);
								Ext.data.StoreManager.lookup(existingAttributeStoreId).loadPage(1,{params:{cdi_name:hashId}});
							}
						});
					}
/**/
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

				self.DEF_RELATION.forEach(function(relation){
					self.DEF_DIRECTION.forEach(function(direction){
						var id = Ext.util.Format.format(self.FORMAT_RELATIONS_PANEL_ID,relation,direction);
						var panel = Ext.getCmp(id);
						if(panel){
							panel.updateLayout();
						}
					});
				});

			}
		}
	});
};

window.AgApp.prototype.downloadObjects = function(config){
	var self = this;
	config = config || {};
	config.title = config.title || 'Download';
	config.iconCls = config.iconCls || 'pallet_download';
	config.msg = config.msg || 'Please enter download file name:';
	config.filename = config.filename || 'objects_'+Ext.util.Format.date(new Date(),'YmdHis');
	config.records = config.records || [];

	var records = [];
	Ext.each(config.records,function(r,i,a){
		if(Ext.isEmpty(r.get('art_id')) && Ext.isEmpty(r.get('artf_id'))) return true;
		records.push({
			art_id: r.get('art_id'),
			artf_id: r.get('artf_id')
		});
	});
	if(Ext.isEmpty(records)){
		if(config.callback) (config.callback)(config.records)
		return;
	}

	Ext.FilenamePrompt.show({
		title: config.title,
		msg: config.msg,
		iconCls: config.iconCls,
		buttons: Ext.Msg.OKCANCEL,
		prompt: true,
		value: config.filename,
		animateTarget: config.animateTarget,
		closable: false,
		icon: Ext.MessageBox.QUESTION,
		defaultFocus: 'cancel',
		modal: true,
		width: 300,
		fn: function(btn, filename){
			if(btn == 'ok'){
				var form_name = 'form_download';
				if(!document.forms[form_name]){
					var form = $('<form>').attr({
						action: 'download.cgi',
						method: 'POST',
						name:   form_name,
						id:     form_name,
						style:  "display:none;"
					}).appendTo($(document.body));
					var input = $('<input type="hidden" name="type">').appendTo(form);
					var input = $('<input type="hidden" name="records">').appendTo(form);
					var input = $('<input type="hidden" name="filename">').appendTo(form);
				}
				document.forms[form_name].type.value = config.type;
				document.forms[form_name].records.value = Ext.encode(records);
				document.forms[form_name].filename.value = filename;
				document.forms[form_name].submit();
			}
			if(config.callback) (config.callback)(config.records)
		}
	});
};

window.AgApp.prototype.initContextmenu = function(){
	var self = this;
};

window.AgApp.prototype.init = function(){
	var self = this;

	self.initBind();
	self.initExtJS();
	self.initStore();
	self.initDelayedTask();
	self.initTemplate();
	self.initComponent();
	self.initContextmenu();
};
