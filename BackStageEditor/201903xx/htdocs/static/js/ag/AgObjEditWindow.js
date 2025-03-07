window.AgApp = window.AgApp || function(config){};

//2016-03-31用 START
window.AgApp.prototype.regexpCdiNameLR = new RegExp("^([A-Z]+[0-9]+?)\-*([LR])$", "i");
//2016-03-31用 END

window.AgApp.prototype.openObjEditWindow = function(config){
	var self = this;

	config = config || {};
	config.records = config.records || [];
	var aCB = config.callback;
	config.title = config.title || AgLang.file_info;
	config.iconCls = config.iconCls || 'pallet_edit';
	config.height = config.height || 727;
	config.width = config.width || 667;
	config.modal = config.modal || true;

	var maxHeight = $(document.body).height();
	var maxWidth = $(document.body).width();

	var mirror_prefix = 'mirror_';

	if(config.height>maxHeight) config.height = maxHeight;
	if(config.width>maxWidth) config.width = maxWidth;

	if(Ext.isEmpty(config.records)){
		if(aCB) (aCB)();
		return;
	}

	var window_id = Ext.id();
//	console.log(window_id);
	var setDisabledSaveButton = function(){
		var win = Ext.getCmp(window_id);
		if(!win) return;
		var gridpanel = win.down('gridpanel');
		var store = gridpanel.getStore();
		var num = 0;
		num += store.getModifiedRecords().length;
		num += store.getNewRecords().length;
		num += store.getRemovedRecords().length;
		num += store.getUpdatedRecords().length;
		var formPanel = win.down('form');
		var disable = !formPanel.getForm().isValid();
		if(!disable) disable = num===0;

		if(!disable){
			var versionCombobox = Ext.getCmp('version-combobox');
			var r = versionCombobox.findRecordByValue(versionCombobox.getValue());
			disable = r.data.mv_frozen;
		}

		var toolbar = win.getDockedItems('toolbar[dock="bottom"]')[0];
		toolbar.getComponent('save').setDisabled(disable);
//		toolbar.getComponent('reset').setDisabled(disable);
		toolbar.getComponent('reset').setDisabled(num===0);
	};
	var setFieldValue = function(field,value){
		field.suspendEvents(false);
		field.setValue(value);
		field.resumeEvents();
		if(field.clearInvalid) field.clearInvalid();
	};
	var updateField = function(fields){
		if(Ext.isEmpty(fields)) return;
		var gridpanel = (Ext.isArray(fields) ? fields[0] : fields).up('window').down('gridpanel');
		if(!gridpanel) return;

		var name2value = [];
		Ext.each(fields,function(field){
			var name = field.getName();
			if(Ext.isEmpty(name)) return true;
			var value = field.getValue();
			if(Ext.isString(value)) value = Ext.String.trim(value);
			if(Ext.isEmpty(value)) value = null;
			name2value[name] = value;
		});
		var modifiedFieldNames = Ext.Object.getKeys(name2value);
		if(Ext.isEmpty(modifiedFieldNames)) return;

		gridpanel.setLoading({msg:"Please wait..."});

		var store = gridpanel.getStore();
		store.suspendEvents(true);
		var select_recs = gridpanel.getSelectionModel().getSelection();
		Ext.each(gridpanel.getSelectionModel().getSelection(),function(rec){
			modifiedFieldNames = [];
			rec.beginEdit();
			Ext.Object.each(name2value,function(name,value){
				if(rec.get(name)===undefined || rec.get(name)===value) return true;
				rec.set(name,value);
				modifiedFieldNames.push(name);
			});
			rec.endEdit(false, modifiedFieldNames);
		});
		store.resumeEvents();

		setDisabledSaveButton();
		gridpanel.setLoading(false);
	};

	var getSelectedData = function(){
		var win = Ext.getCmp(window_id);
		if(!win) return undefined;
		var gridpanel = win.down('gridpanel');
		var selModel = gridpanel.getSelectionModel();
		var selected = selModel.getSelection();
		var store = gridpanel.getStore();
		var form = selModel.view.up('window').down('form');
		var basicForm = form.getForm();

		var data = null;
		if(selected.length>1){
			var arr = {
				mv_name_e: [],
				cdi_name: [],
				cdi_name_e: [],
				cm_comment: [],
				cm_use: [],
				cmp_id: [],
				art_category: [],
				art_class: [],
				art_comment: [],
				art_judge: [],
				mirror: [],
				mirror_same_concept: [],
				mirror_cdi_name: [],
				mirror_cdi_name_e: []
			};
			Ext.each(selected,function(record){
				for(var key in arr){
					arr[key].push(record.data[key]);
				}
			});
			for(var key in arr){
				arr[key] = Ext.Array.unique(arr[key]);
			}

			data = {};
			for(var key in arr){
				if(arr[key].length==1){
					data[key] = arr[key][0];
				}else{
					data[key] = null;
				}
			}
		}
		else if(selected.length==1){
			data = Ext.apply({},selected[0].data);
		}
		return data;
	};

	var loadSelectedRecords = function(){
		var data = getSelectedData();
		if(Ext.isEmpty(data)) return;

		var win = Ext.getCmp(window_id);
		if(!win) return;
		var gridpanel = win.down('gridpanel');
		var store = gridpanel.getStore();
		var selModel = gridpanel.getSelectionModel();
		var form = selModel.view.up('window').down('form');
		var basicForm = form.getForm();

		n_record = Ext.create(store.model.modelName,data);
		if(Ext.isEmpty(n_record)) n_record = Ext.create(store.model.modelName,{});

		var fields = basicForm.getFields();
		fields.each(function(field,index,len){
			field.suspendEvents(false);
		});
		try{
			basicForm.loadRecord(n_record);
		}catch(e){console.error(e);}
		fields.each(function(field,index,len){
			var name = field.getName();
			if(Ext.isString(name) && name.length && Ext.isFunction(field.renderer)){
				field.setValue(field.getValue());
			}
			field.resumeEvents();
			try{field.validate();}catch(e){console.error(e);}
		});

		var cdi_name_field = basicForm.findField('cdi_name');
		var cdi_name_edit_field = cdi_name_field.nextSibling('textfield');
		setFieldValue(cdi_name_edit_field, cdi_name_field.renderer(cdi_name_field.getValue(),cdi_name_field));

		var mirror_cdi_name_field = basicForm.findField(mirror_prefix+'cdi_name');
		var mirror_cdi_name_edit_field = mirror_cdi_name_field.nextSibling('textfield');
		setFieldValue(mirror_cdi_name_edit_field, mirror_cdi_name_field.renderer(mirror_cdi_name_field.getValue(),mirror_cdi_name_field));
	};

	var cdiName = {
		validator: function( value ){
			var field = this;
			if(Ext.isString(value)){
				if(Ext.isEmpty(Ext.String.trim(value))) return true;
			}else{
				if(Ext.isEmpty(s)) return true;
			}
			var displayfield = field.up('fieldset').getComponent('cdi_name_e');
			if(Ext.isEmpty(displayfield.getValue())) return AgLang.error_cdi_name;
			return true;
		},

		focus: function( field, e, eOpts ){
			if(field.getXType()!=='combobox') return;
			var value = field.getValue();
			if(Ext.isString(value)) value = Ext.String.trim(value);
			if(Ext.isEmpty(value)) return;
			field.doQuery(value);
		},

		change: function(field,newValue,oldValue,prefix){

			var basicForm = field.up('form').getForm();
			if(Ext.isEmpty(prefix)) prefix = '';

			if(Ext.isString(newValue)) newValue = Ext.String.trim(newValue);
//			field.clearInvalid();
			//2016-03-31用 START
			var cmp_id = 0;
			var cmp_id_field = basicForm.findField(prefix+'cmp_id');
			var cdi_name_field = basicForm.findField(prefix+'cdi_name');
			//2016-03-31用 END
			var cdi_name_e_field = basicForm.findField(prefix+'cdi_name_e');
			if(Ext.isEmpty(newValue)){
				cdiName.delete(field,prefix);
//				setFieldValue(cmp_id_field, 0);	//2016-03-31用
//				setFieldValue(cdi_name_field, null);	//2016-03-31用
//				setFieldValue(cdi_name_e_field, null);
//				updateField([cmp_id_field,cdi_name_field,cdi_name_e_field]);
			}else{

				//2016-03-31用 START
				if(Ext.isString(newValue)){
					var m = self.regexpCdiNameLR.exec(newValue);
					if(Ext.isArray(m) && m.length){
						var tmp_cdi_name = m[1];
						var cmp_abbr = m[2].toUpperCase();
						var conceptArtMapPartStore = Ext.data.StoreManager.lookup('conceptArtMapPartStore');
						cmp_record = conceptArtMapPartStore.findRecord('cmp_abbr', cmp_abbr, 0, false, false, true );
						if(cmp_record){
							cmp_id = cmp_record.get('cmp_id');
							newValue = tmp_cdi_name;
						}
					}
				}
				field.doQuery(newValue);
				cmp_id_field.setValue(cmp_id);
				cdi_name_field.setValue(newValue);
				//2016-03-31用 END

				var fmaAllStore = Ext.data.StoreManager.lookup('fmaAllStore');
				if(fmaAllStore.isLoading()){
					var params = self.getExtraParams() || {};
					params.cmd = 'read';
					params.cdi_name = newValue;
					displayfield.setLoading(true);
					Ext.Ajax.request({
						url: 'get-fma-list.cgi',
						autoAbort: true,
						method: 'POST',
						params: params,
						callback: function(options,success,response){
							displayfield.setLoading(false);
							var json;
							try{json = Ext.decode(response.responseText)}catch(e){};
							if(!success || Ext.isEmpty(json) || Ext.isEmpty(json.success) || !json.success || Ext.isEmpty(json.datas)){
								if(Ext.isString(newValue) && newValue.length){
									setFieldValue(cmp_id_field, 0);	//2016-03-31用
									setFieldValue(cdi_name_field, null);	//2016-03-31用
									setFieldValue(cdi_name_e_field, null);
								}else{
									cdiName.delete(field,prefix);
								}
							}
							else{
								var data = json.datas[0];
								setFieldValue(cdi_name_field ,data.cdi_name);	//2016-03-31用
								setFieldValue(cdi_name_e_field, data.cdi_name_e);
								cdiName.selectPart(field,prefix);
							}
							field.validate();

							updateField([cmp_id_field,cdi_name_field,cdi_name_e_field]);
						}
					});
				}else{
					var record = fmaAllStore.findRecord('cdi_name', newValue, 0, false, false, true );
					if(Ext.isEmpty(record)){
						if(Ext.isString(newValue) && newValue.length){
							setFieldValue(cmp_id_field, 0);	//2016-03-31用
							setFieldValue(cdi_name_field, null);	//2016-03-31用
							setFieldValue(cdi_name_e_field, null);
						}else{
							cdiName.delete(field,prefix);
						}
					}else{
						setFieldValue(cdi_name_field, record.get('cdi_name'));	//2016-03-31用
						setFieldValue(cdi_name_e_field, record.get('cdi_name_e'));
						cdiName.selectPart(field,prefix);
					}
					field.validate();

					updateField([cmp_id_field,cdi_name_field,cdi_name_e_field]);
				}
			}
		},

		beforeQuery: function( queryPlan, eOpts ){
			var field = queryPlan.combo;
			if(field.getXType()!=='combobox') return;
			var value = '';
			if(Ext.isString(queryPlan.query)) value = Ext.String.trim(queryPlan.query);
			queryPlan.cancel = (value.length<4);
			if(queryPlan.cancel){
				var displayfield = field.up('fieldset').getComponent('cdi_name_e');
				displayfield.setValue(null);
				updateField([field,displayfield]);
				if(field.isExpanded) field.collapse();
			}
		},

		delete: function(b, prefix){
			if(b.getXType()==='button'){
				if(b.disabled) return;
				b.setDisabled(true);
			}
			Ext.defer(function(){
				var basicForm = b.up('form').getForm();

				var same_concept = false;
				if(Ext.isEmpty(prefix)){
					var mirroring = false;
					var mirror_fieldset = basicForm.findField('mirror');
					if(mirror_fieldset && mirror_fieldset.getValue()) mirroring = true;

					if(mirroring){
						var same_concept_checkbox = basicForm.findField(mirror_prefix+'same_concept');
						if(same_concept_checkbox) same_concept = same_concept_checkbox.getValue();
					}
					prefix = '';
				}

				var fields = [];
				var cdi_name_field = basicForm.findField(prefix+'cdi_name');
				if(cdi_name_field){
					setFieldValue(cdi_name_field ,null);
					fields.push(cdi_name_field);

					var cdi_name_edit_field = cdi_name_field.nextSibling('combobox');
					if(cdi_name_edit_field){
						setFieldValue(cdi_name_edit_field, null);
					}
				}
				var cdi_name_e_field = basicForm.findField(prefix+'cdi_name_e');
				if(cdi_name_e_field){
					setFieldValue(cdi_name_e_field, null);
					fields.push(cdi_name_e_field);
				}
				var cmp_id_field = basicForm.findField(prefix+'cmp_id');
				if(cmp_id_field){
					setFieldValue(cmp_id_field, 0);
					fields.push(cmp_id_field);
				}

				if(same_concept){

					var mirror_cdi_name_field = basicForm.findField(mirror_prefix+'cdi_name');
					if(mirror_cdi_name_field){
						setFieldValue(mirror_cdi_name_field ,null);
						fields.push(mirror_cdi_name_field);

						var mirror_cdi_name_edit_field = mirror_cdi_name_field.nextSibling('combobox')
						if(mirror_cdi_name_edit_field){
							setFieldValue(mirror_cdi_name_edit_field, null);
						}
					}
					var mirror_cdi_name_e_field = basicForm.findField(mirror_prefix+'cdi_name_e');
					if(mirror_cdi_name_e_field){
						setFieldValue(mirror_cdi_name_e_field, null);
						fields.push(mirror_cdi_name_e_field);
					}
					var mirror_cmp_id_field = basicForm.findField(mirror_prefix+'cmp_id');
					if(mirror_cmp_id_field){
						setFieldValue(mirror_cmp_id_field, 0);
						fields.push(mirror_cmp_id_field);
					}

				}

				updateField(fields);

				cdi_name_edit_field.focus();
				if(b.getXType()==='button'){
					b.setDisabled(false);
				}
			},100);
		},

		selectPart: function(field, prefix){
			var basicForm = field.up('form').getForm();

			var same_concept = false;
			if(Ext.isEmpty(prefix)){
				var mirroring = false;
				var mirror_fieldset = basicForm.findField('mirror');
				if(mirror_fieldset && mirror_fieldset.getValue()) mirroring = true;

				if(mirroring){
					var same_concept_checkbox = basicForm.findField(mirror_prefix+'same_concept');
					if(same_concept_checkbox) same_concept = same_concept_checkbox.getValue();
				}
				prefix = '';
			}

			var fields = [];
			var cmp_id_field = basicForm.findField(prefix+'cmp_id');
			if(Ext.isEmpty(cmp_id_field.getValue())){
				setFieldValue(cmp_id_field, 0);
				fields.push(cmp_id_field);
			}
			var cdi_name_field = basicForm.findField(prefix+'cdi_name');
			var cdi_name_edit_field = cdi_name_field.nextSibling('combobox')
			setFieldValue(cdi_name_edit_field, cdi_name_field.renderer(cdi_name_field.getValue(),cdi_name_field));
			setFieldValue(cdi_name_field, cdi_name_field.getValue());
			fields.push(cdi_name_field);

			var cdi_name_e_field = basicForm.findField(prefix+'cdi_name_e');
			setFieldValue(cdi_name_e_field, cdi_name_e_field.getValue());
			fields.push(cdi_name_e_field);

			if(same_concept){
				var mirror_cmp_id_field = basicForm.findField(mirror_prefix+'cmp_id');
				setFieldValue(mirror_cmp_id_field, cmp_id_field.getValue());
				fields.push(mirror_cmp_id_field);

				var mirror_cdi_name_field = basicForm.findField(mirror_prefix+'cdi_name');
				var mirror_cdi_name_edit_field = mirror_cdi_name_field.nextSibling('combobox')
				setFieldValue(mirror_cdi_name_edit_field, mirror_cdi_name_field.renderer(cdi_name_field.getValue(),mirror_cdi_name_field));
				setFieldValue(mirror_cdi_name_field, cdi_name_field.getValue());
				fields.push(mirror_cdi_name_field);

				var mirror_cdi_name_e_field = basicForm.findField(mirror_prefix+'cdi_name_e');
				setFieldValue(mirror_cdi_name_e_field, cdi_name_e_field.getValue());
				fields.push(mirror_cdi_name_e_field);
			}

			updateField(fields);
		}
	};

	var fmaSearch = {
		query: function(b){
			var value = b.prev('textfield').getValue();
			if(Ext.isString(value)) value = Ext.String.trim(value);

			//2016-03-31用 START
			if(Ext.isString(value)){
				var m = self.regexpCdiNameLR.exec(value);
				if(Ext.isArray(m) && m.length) value = m[1];
			}
			//2016-03-31用 END

			return value;
		},

		callback: function(record, b, prefix){
			if(Ext.isEmpty(record)) return;
			var basicForm = b.up('form').getForm();
			Ext.each(['cdi_name','cdi_name_e'],function(name,index,arr){
				var field = basicForm.findField(name);
				if(Ext.isEmpty(field)) return true;
				setFieldValue(field, record.get(name));
			});
			cdiName.selectPart(b, prefix);
		}
	};

	var historyMappingStore = Ext.data.StoreManager.lookup('historyMappingStore');
	if(Ext.isEmpty(historyMappingStore)){
		historyMappingStore = Ext.create('Ext.data.Store', {
			storeId: 'historyMappingStore',
			model: 'HISTORY_MAPPING',
			proxy: {
				type: 'ajax',
				url: 'get-info.cgi?cmd=history-mapping',
				pageParam: undefined,
				startParam: undefined,
				limitParam: undefined,
				noCache: false,
				actionMethods : {
					create : 'POST',
					read   : 'POST',
					update : 'POST',
					destroy: 'POST'
				},
				reader: {
					type: 'json',
					root: 'datas'
				}
			},
			listeners: {
				beforeload: function(store,operation,eOpts){
					if(store.loading && store.getLastRequestOptions()) {
						var requests = Ext.Ajax.requests;
						var id;
						for(id in requests){
							if(requests.hasOwnProperty(id) && requests[id].options == store.getLastRequestOptions()){
								Ext.Ajax.abort(requests[id]);
//								console.log("historyMappingStore.beforeload():Ext.Ajax.abort()");
							}
						}
					}
					var beforerequest = function(conn,options,eOpts){
						store.setLastRequestOptions(options);
					};
					Ext.Ajax.on({
						beforerequest: beforerequest,
						single: true,
						scope: self
					});
				},
				add: function(store,records,index,eOpts){
				},
				remove: function(store,record,index,eOpts){
				},
				update: function(store,record,operation){
				}
			}
		});
		historyMappingStore.setLastRequestOptions = function(options){
			historyMappingStore._LastRequestOptions = options;
		};
		historyMappingStore.getLastRequestOptions = function(){
			return historyMappingStore._LastRequestOptions;
		};
	}

	var objEditStore = Ext.data.StoreManager.lookup('objEditStore');
	if(Ext.isEmpty(objEditStore)){
		objEditStore = Ext.create('Ext.data.Store', {
			storeId: 'objEditStore',
			model: 'OBJ_EDIT',
			autoLoad: false,
			autoSync: false,
			remoteFilter: false,
			remoteSort: false,
			filterOnLoad : false,
			sortOnFilter: false,
			sortOnLoad: false,
			proxy: {
				type: 'ajax',
				api: {
					create  : 'api-upload-file-list.cgi?cmd=create',
					read    : 'api-upload-file-list.cgi?cmd=read',
					update  : 'api-upload-file-list.cgi?cmd=update_ver2',
					destroy : 'api-upload-file-list.cgi?cmd=destroy',
				},
				timeout: 300000,
				pageParam: undefined,
				startParam: undefined,
				limitParam: undefined,
				sortParam: undefined,
				groupParam: undefined,
				filterParam: undefined,
				actionMethods : {
					create : 'POST',
					read   : 'POST',
					update : 'POST',
					destroy: 'POST'
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
				}
			},
			listeners: {
				add: function(store,records,index,eOpts){
//					console.log("objEditStore.add()");
				},
				remove: function(store,record,index,eOpts){
//					console.log("objEditStore.remove()");
				},
				update: function(store,record,operation){
//					console.log("objEditStore.update():"+operation);
//					console.log(record);
					setDisabledSaveButton();
				},
				beforeload: function(store, operation, eOpts){
//					console.log("objEditStore.beforeload()");
				},
				load: function(store, operation, eOpts){
//					console.log("objEditStore.load()");
				},
				beforesync: function(options, eOpts){
//					console.log("objEditStore.beforesync()");
					return self.beforeloadStore(this);
				},
				write: function(store, operation, eOpts){
//					console.log("objEditStore.write()");
				}
			}
		});
	}

	var loadRecords = [];
	Ext.each(config.records,function(r,i,a){
//		loadRecords.push(Ext.create(objEditStore.model.modelName,r.data));
		loadRecords.push(r.getData());
	});

//	objEditStore.loadRecords(loadRecords);
	objEditStore.loadData(loadRecords);
	objEditStore.commitChanges();
	var record = config.records[0];

	var versionCombobox = Ext.getCmp('version-combobox');
	var r = versionCombobox.findRecordByValue(versionCombobox.getValue());
	var mv_frozen = r.data.mv_frozen;

	var obj_edit_window = Ext.create('Ext.window.Window', {
		id: window_id,
		title: config.title,
		iconCls: config.iconCls,
		modal: config.modal,
		height: config.height,
		width: config.width,
		animateTarget: config.animateTarget,
		autoShow: true,
		buttons: [{
			itemId: 'reset',
			text: AgLang.reset,
			disabled: true,//mv_frozen,
			listeners: {
				click: function(b,e,eOpts){
					var win = Ext.getCmp(window_id);
					var gridpanel = win.down('gridpanel');
					var store = gridpanel.getStore();
					store.rejectChanges();
					loadSelectedRecords();
					setDisabledSaveButton();

					var form = win.down('form');
					var record = form.getForm().getRecord();
					if(record.get('mirror')){
						form.getComponent('mirror').expand();
					}else{
						form.getComponent('mirror').collapse();
					}
				}
			}
		},'->',{
			itemId: 'save',
			text: AgLang.save,
			disabled: true,//mv_frozen,
			listeners: {
				click: function(b,e,eOpts){
					if(b.isDisabled()) return;
					b.setDisabled(true);

					var versionCombobox = Ext.getCmp('version-combobox');
					var r = versionCombobox.findRecordByValue(versionCombobox.getValue());
					if(r.data.mv_frozen){
						Ext.Msg.show({
							title: b.text,
							iconCls: b.iconCls,
							msg: '['+AgLang.not_editable_state+']です',
							buttons: Ext.Msg.OK,
							icon: Ext.Msg.ERROR,
							fn: function(buttonId,text,opt){
							}
						});
						return;
					}

					var win = b.up('window');
					if(win) win.setLoading(true);
					try{
						var gridpanel = win.down('gridpanel');
						var store = gridpanel.getStore();
						var modifiedRecords = store.getModifiedRecords();
						var cloneModifiedRecords = [];
						var is_mirror = false;
						if(Ext.isArray(modifiedRecords) && modifiedRecords.length){
							Ext.each(modifiedRecords,function(record){
								var c_record = record.copy();
								if(Ext.isObject(record.modified)){
									Ext.Object.each(record.modified,function(key, value){
										c_record.modified[key] = value;
										if(key=='mirror') is_mirror = true;
									});
								}
								cloneModifiedRecords.push(c_record);
							});
						}
//						console.log(cloneModifiedRecords);

						store.sync({
							callback: function(batch,options){
//								setDisabledSaveButton();
//								if(win) win.setLoading(false);
							},
							success: function(batch,options){

								var proxy = this;
								var reader = proxy.getReader();
								if(reader && reader.rawData && reader.rawData.success && Ext.isArray(reader.rawData.datas) && reader.rawData.datas.length){

									var selected = gridpanel.getSelectionModel().getSelection();
									if(selected.length==1){
										var record = selected[0];
										var historyMappingStore = Ext.data.StoreManager.lookup('historyMappingStore');
										if(historyMappingStore){
											historyMappingStore.loadPage(1,{
												params: {
													art_id: record.data.art_id
												},
												sorters: [{
													property: 'hist_timestamp',
													direction: 'DESC'
												}]
											});
										}
									}


//									console.log(reader.rawData);
									var datas = reader.rawData.datas;
									var uploadGroupStore = Ext.data.StoreManager.lookup('uploadGroupStore');
									if(uploadGroupStore.autoLoad) uploadGroupStore.suspendAutoSync();
									var filters = uploadGroupStore._getFilters();
									Ext.each(datas,function(data){
										uploadGroupStore._setFilters([{
											property: 'artg_delcause',
											value: null
										},{
											property: 'artg_id',
											value: data.artg_id
										}]);
										var record = uploadGroupStore.findRecord('artg_id',data.artg_id,0,false,false,true);
										if(record){
											record.beginEdit();
											record.set('art_count',data.art_count);
											record.set('nochk_count',data.nochk_count);
											record.set('nomap_count',data.nomap_count);
											record.set('use_map_count',data.use_map_count);
											record.set('all_cm_map_versions',data.all_cm_map_versions);
											record.endEdit(false,['art_count','nochk_count','nomap_count','use_map_count','all_cm_map_versions']);
											record.commit(false,['art_count','nochk_count','nomap_count','use_map_count','all_cm_map_versions']);
										}
									});
									uploadGroupStore._setFilters(filters);
									if(uploadGroupStore.autoLoad) uploadGroupStore.resumeAutoSync();

									var is_groupdisp = false;
									Ext.each(datas,function(data){
										var record = uploadGroupStore.findRecord('artg_id',data.artg_id,0,false,false,true);
										if(record && record.get('selected')){
											is_groupdisp = true;
											return false;
										}
									});

									if(is_mirror && is_groupdisp){

										var selected_art_ids = self.getSelectedArtIds();
										var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
										uploadObjectStore.on({
											load: function(store,records,successful,eOpts){

												var art_ids = [];
												var art_id_hash = {};
												objEditStore.each(function(r){
													var art_id = r.get('art_id');
													if(Ext.isEmpty(art_id)) return true;
													if(Ext.isEmpty(art_id_hash[art_id])){
														art_id_hash[art_id] = art_id;
														art_ids.push({
															art_id:         art_id,
															color:          r.get('color'),
															opacity:        r.get('opacity'),
															remove:         r.get('remove'),
															representation: r.get('representation'),
															scalar:         r.get('scalar'),
															scalar_flag:    r.get('scalar_flag'),
															selected:       r.get('selected')
														});
													}
												});

												self.updateArtInfo(function(){
													setDisabledSaveButton();
													if(win) win.setLoading(false);
												},null,art_ids);
											},
											single: true
										});
										uploadObjectStore.setLoadUploadObjectAllStoreFlag();
										uploadObjectStore.loadPage(1,{
											params: { selected_art_ids: Ext.encode(selected_art_ids) },
											sorters: uploadObjectStore.getUploadObjectLastSorters()
										});

									}else{
										Ext.each([Ext.data.StoreManager.lookup('uploadObjectStore'),Ext.data.StoreManager.lookup('palletPartsStore')],function(store){
											Ext.each(cloneModifiedRecords,function(c_record){
												var record = store.findRecord('art_id',c_record.get('art_id'),0,false,false,true);
												if(Ext.isEmpty(record)) return true;
												var data = c_record.getData();
												var modifiedFieldNames = [];
												record.beginEdit();
												Ext.Object.each(data,function(c_key,c_value){
													var value = record.get(c_key);
													if(value===undefined) return true;
													if(value===c_value) return true;
													record.set(c_key,c_value);
													modifiedFieldNames.push(c_key);
												});
												if(modifiedFieldNames.length){
													record.endEdit(false,modifiedFieldNames);
													record.commit(false,modifiedFieldNames);
												}else{
													record.cancelEdit();
												}
											});
										});
										setDisabledSaveButton();
										if(win) win.setLoading(false);
									}
									return;
								}

								Ext.data.StoreManager.lookup('uploadGroupStore').loadPage(1,{
									callback: function(records, operation, success) {
										var selected_art_ids = self.getSelectedArtIds();
										var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
										uploadObjectStore.on({
											load: function(store,records,successful,eOpts){

												var art_ids = [];
												var art_id_hash = {};
												objEditStore.each(function(r){
													var art_id = r.get('art_id');
													if(Ext.isEmpty(art_id)) return true;
													if(Ext.isEmpty(art_id_hash[art_id])){
														art_id_hash[art_id] = art_id;
														art_ids.push({
															art_id:         art_id,
															color:          r.get('color'),
															opacity:        r.get('opacity'),
															remove:         r.get('remove'),
															representation: r.get('representation'),
															scalar:         r.get('scalar'),
															scalar_flag:    r.get('scalar_flag'),
															selected:       r.get('selected')
														});
													}
												});

												self.updateArtInfo(function(){
													setDisabledSaveButton();
													if(win) win.setLoading(false);
												},null,art_ids);
											},
											single: true
										});
										uploadObjectStore.setLoadUploadObjectAllStoreFlag();
										uploadObjectStore.loadPage(1,{
											params: { selected_art_ids: Ext.encode(selected_art_ids) },
											sorters: uploadObjectStore.getUploadObjectLastSorters()
										});
									}
								});
							},
							failure: function(batch,options){
								var msg = AgLang.error_save;
								var proxy = this;
								var reader = proxy.getReader();
								if(reader && reader.rawData && reader.rawData.msg){
									msg += ' ['+reader.rawData.msg+']';
								}
								Ext.Msg.show({
									title: b.text,
									iconCls: b.iconCls,
									msg: msg,
									buttons: Ext.Msg.OK,
									icon: Ext.Msg.ERROR,
									fn: function(buttonId,text,opt){
									}
								});
								setDisabledSaveButton();
								if(win) win.setLoading(false);
							}
						});
					}catch(e){
						alert(e);
						setDisabledSaveButton();
						if(win) win.setLoading(false);
					}
				}
			}
		},{
			text: AgLang.close,
			listeners: {
				click: function(b,e,eOpts){
					if(aCB) (aCB)();
					b.up('window').close();
				}
			}
		}],
		layout: 'border',
		items: [{
			region: 'north',
			split: true,
			height: 100,
			xtype: 'gridpanel',
			columnLines: true,
			store: 'objEditStore',
			plugins: [self.getBufferedRenderer()],
			columns: [
				{xtype: 'rownumberer'},
				{text: '&#160;',         dataIndex: 'selected', width:30, minWidth:30, hidden:true,  hideable:false, xtype:'agselectedcheckcolumn'},
				{text: AgLang.art_id,    dataIndex: 'art_id',   width:60, minWidth:60, hidden:false, hideable:false},
				{text: AgLang.group,     dataIndex: 'group',    flex:1,   minWidth:80, hidden:false, hideable:false},
				{text: AgLang.file_name, dataIndex: 'filename', flex:1,   minWidth:80, hidden:false, hideable:false},
				{text: AgLang.cdi_name,  dataIndex: 'cdi_name', width:80, minWidth:80, hidden:false, hideable:false, xtype:'agcolumncdiname'},
				{text: AgLang.use,       dataIndex: 'cm_use',   width:34, minWidth:34, hidden:false, hideable:false, xtype:'agbooleancolumn', disabled:mv_frozen},


				{text: 'mirror', dataIndex: 'mirror',              width:30, minWidth:30, hidden:true, hideable:false, xtype: 'booleancolumn', trueText: 'Yes', falseText: 'No'},
				{text: 'same',   dataIndex: 'mirror_same_concept', width:30, minWidth:30, hidden:true, hideable:false, xtype: 'booleancolumn', trueText: 'Yes', falseText: 'No'},
				{text: 'id',     dataIndex: 'mirror_cdi_name',     width:80, minWidth:80, hidden:true, hideable:false, xtype: 'agcolumncdiname'},
				{text: 'name',   dataIndex: 'mirror_cdi_name_e',   flex: 1,  minWidth:80, hidden:true, hideable:false, xtype: 'agcolumncdinamee'},
				{text: 'cmp',    dataIndex: 'mirror_cmp_id',       width:24, minWidth:24, hidden:true, hideable:false},
			],
			selType: 'rowmodel',
			selModel: {
//				mode:'SINGLE'
					mode:'MULTI'
			},
			dockedItems: [{
				hidden: true,
				dock: 'top',
				xtype: 'toolbar',
				items: ['->','-',{
					hidden: true,
					disabled: true,
					itemId: 'find',
					text: AgLang.volume_find,
					iconCls: 'pallet_find',
					listeners: {
						click: function(b){

							b.setDisabled(true);

							var gridpanel = b.up('gridpanel');
							var selModel = gridpanel.getSelectionModel();
							var rec = selModel.getLastSelected();
							if(Ext.isEmpty(rec)){
								b.setDisabled(false);
								return;
							}
							selModel.deselectAll();
							selModel.select(rec);
							b.setDisabled(true);
//									console.log(rec);

							self.openFindObjectTask.delay(10,self.openFindObject,self,[{
								record: rec,
								title: b.text,
								iconCls: b.iconCls,
								modal: true,
								useValue: true,
								callback: function(record){
									b.setDisabled(false);
									if(Ext.isEmpty(record)) return;

									var basicForm = selModel.view.up('form').getForm();
									record.fields.each(function(item,index,len){
										var field = basicForm.findField(item.name);
										if(Ext.isEmpty(field)) return true;
										field.setValue(record.get(item.name));
									});

								}
							}]);

						}
					}
				}]
			}],
			listeners: {
				afterrender: function(comp){
					return;
				},
				selectionchange: function(selModel,selected,eOpts){
//					console.log("selectionchange()");
					var grid = this;
					var toolbar = grid.getDockedItems('toolbar[dock="top"]')[0];
					var disabled = Ext.isEmpty(selected);
					toolbar.getComponent('find').setDisabled(disabled);

					var record = selected[0];
//					if(Ext.isEmpty(record)) return;

					var form = selModel.view.up('window').down('form');
					var basicForm = form.getForm();
					var fields = basicForm.getFields();
					loadSelectedRecords();

					var historyMappingStore = Ext.data.StoreManager.lookup('historyMappingStore');
					if(historyMappingStore){
						if(selected.length==1){
							historyMappingStore.loadPage(1,{
								params: {
									art_id: record.data.art_id
								},
								sorters: [{
									property: 'hist_timestamp',
									direction: 'DESC'
								}]
							});
						}else{
							historyMappingStore.removeAll();
						}
					}

					if(!mv_frozen){
						var field_disabled = selected.length ? false : true;
						fields.each(function(field,index,len){
							field.setDisabled(field_disabled);
						});
						var button = form.down('button');
						while(button){
							button.setDisabled(field_disabled);
							button = button.next('button');
						}

						field_disabled = selected.length==1 ? false : true;
						var gridpanel = form.down('gridpanel');
						while(gridpanel){
							gridpanel.setDisabled(field_disabled);
							gridpanel = gridpanel.next('gridpanel');
						}
					}

					if(!mv_frozen && selected.length){
						var mirrorfield = basicForm.findField('mirror');
						if(mirrorfield){
							var mirrorDisabled = (selected.length==0?true:false);
							if(!mirrorDisabled){
								Ext.each(selected,function(r){
									mirrorDisabled = ((r.data.art_id.match(/M$/))?true:false);
									if(mirrorDisabled) return false;
								});
							}
							mirrorfield.setDisabled(mirrorDisabled);
							if(mirrorfield.isDisabled() && mirrorfield.getValue()) mirrorfield.setValue(false);
							var fieldset = mirrorfield.up('fieldset');
							if(fieldset){
								if(mirrorfield.getValue()){
									fieldset.expand();
								}else{
									fieldset.collapse();
								}
							}
						}
					}

				}
			}
		},{
			region: 'center',
			xtype: 'form',
			url: 'api-upload-file-list.cgi?cmd=update',
			method: 'POST',
			autoScroll: true,
			border: false,
			bodyStyle: 'background:transparent;padding:10px 10px 0px 10px;',
			defaults: {
				labelAlign: 'right',
				labelWidth: 56,
				anchor: '100%'
			},
			items: [
			{
				xtype:'fieldset',
				title: 'Concept',
				itemId: 'concept',
//					checkboxToggle: true,
//					collapsed: false,
//					checkboxName: 'map_concept',
				defaults: {
					labelAlign: 'right',
					labelWidth: 56,
					anchor: '100%'
				},
				items: [{
					xtype: 'displayfield',
					fieldLabel: AgLang.version,
					name: 'mv_name_e'
				},{
					itemId: 'cdi_name',
					xtype: 'fieldcontainer',
					fieldLabel: AgLang.cdi_name,
					bodyStyle: 'background:transparent;',
					border: false,
					layout: {
						type: 'hbox',
						pack: 'start'
					},
					items: [
					//2016-03-31用 START
					{
						xtype: 'agcdinamedisplayfield',
						name: 'cdi_name',
						itemId: 'cdi_name',
//						margin: '0 4 0 0',
						minWidth: 88,
						listeners: {
							change: function(field,newValue,oldValue,eOpts){
//								console.log('change()');
								updateField(field);
							}
						}
					},
					//2016-03-31用 END
					{
						disabled: mv_frozen,
//						width: 155,
						width: 88,
//						xtype: 'textfield',

						xtype: 'combobox',
						store: 'fmaAllStore',
						queryMode: 'local',
						displayField: 'cdi_name',
						valueField: 'cdi_name',
						hideTrigger: true,
						anyMatch: true,

//						itemId: 'cdi_name',			//2016-03-31用 COMMENT OUT
//						name: 'cdi_name',				//2016-03-31用 COMMENT OUT
						itemId: 'cdi_name_edit',	//2016-03-31用 ADD

						selectOnFocus: true,
						enableKeyEvents: true,
						validator: cdiName.validator,
						listeners: {
							focus: cdiName.focus,
							change: function(field,newValue,oldValue,eOpts){
								cdiName.change(field,newValue,oldValue);
							},
							beforequery: cdiName.beforeQuery,
							select: function( field, records, eOpts ){
								return;
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
							afterrender: function(field,eOpts){
								var el = field.getEl();
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
										if(dropData != field.getValue()) field.setValue(dropData);
									}
								});
							}
						}
					},{
						disabled: mv_frozen,
						width: 100,
						xtype: 'button',
						iconCls: 'pallet_find',
						text: 'FMA Search',
						listeners: {
							click: function(b,e,eOpts){
								self.openFMASearch({
									title: b.text,
									iconCls: b.iconCls,
									animateTarget: b.getEl(),
									query: fmaSearch.query(b),
									callback: function(record){
										if(Ext.isEmpty(record)) return;
										fmaSearch.callback(record,b);
									}
								});
							}
						}
					},{
						disabled: mv_frozen,
						width: 110,
						xtype: 'button',
						iconCls: 'pallet_table_list',
						text: AgLang.all_fma_list,
						listeners: {
							click: function(b,e,eOpts){
								var btn = Ext.getCmp('all-fma-list-button');
								if(btn) btn.fireEvent('click',btn);
							}
						}
					},{
						disabled: mv_frozen,
						width: 22,
						xtype: 'button',
						iconCls: 'pallet_delete',
						listeners: {
							click : function(b,e,eOpts){
								cdiName.delete(b);
							}
						}
					}]
				},{
					hidden: true,
					disabled: mv_frozen,
					width: 130,
					anchor: null,
					editable: false,
					xtype: 'combobox',
					fieldLabel: 'Part',
					name: 'cmp_id',
					itemId: 'cmp_id',
					store: 'conceptArtMapPartStore',
					queryMode: 'local',
					displayField: 'cmp_title',
					valueField: 'cmp_id',
					listeners: {
						change: function(field,newValue,oldValue,eOpts){
//							console.log('change()');
							updateField(field);
						},
						select: function( field, records, eOpts ){
							cdiName.selectPart(field);
						}
					}
				},{
					xtype: 'agcdinameedisplayfield',
					fieldLabel: AgLang.cdi_name_e,
					name: 'cdi_name_e',
					itemId: 'cdi_name_e',
					listeners: {
						change: function(field,newValue,oldValue,eOpts){
							updateField(field);
						}
					}
				},{
					disabled: mv_frozen,
					xtype: 'textfield',
					fieldLabel: AgLang.comment,
					name: 'cm_comment',
					listeners: {
						change: function(field,newValue,oldValue,eOpts){
							updateField(field);
						}
					}
				},{
					xtype: 'fieldcontainer',
					bodyStyle: 'background:transparent;',
					border: false,
					layout: {
						type: 'hbox',
						pack: 'start'
					},
					defaults: {
						labelAlign: 'right',
						labelWidth: 62
					},
					items: [{
						disabled: mv_frozen,
						xtype: 'checkboxfield',
						fieldLabel: AgLang.use,
						inputValue: 'true',
						name: 'cm_use',
						listeners: {
							change: function(field,newValue,oldValue,eOpts){
								updateField(field);
								if(!field.up('form').getForm().getFieldValues()['set_same_use_setting_mirror_part']) return;
								var checkboxfield = field.next('checkboxfield');
								checkboxfield.fireEvent('change',checkboxfield,true);
							},
							buffer: 100
						}
					},{
						hidden: false,
						disabled: mv_frozen,
						xtype: 'checkboxfield',
						hideLabel: true,
						boxLabel: 'Set same use / no-use setting to mirror part.',
						inputValue: 'true',
						margin: '0 0 0 30',
						name: 'set_same_use_setting_mirror_part',
						checked: false,
						listeners: {
							change: function(field,newValue,oldValue,eOpts){
								updateField(field);
								if(!newValue) return;
								var data = getSelectedData();
								if(Ext.isEmpty(data['cm_use'])) return;
								var cm_use = data['cm_use'];
								var gridpanel = field.up('window').down('grid');
								var records = gridpanel.getSelectionModel().getSelection();
								var store = gridpanel.getStore();
								Ext.each(records,function(r){
									var art_id = r.get('art_id');
									var art_mirror_id = null;
									if(art_id.match(/^([A-Z]+[0-9]+)(M*)$/)){
										art_mirror_id = RegExp.$1;
										if(Ext.isEmpty(RegExp.$2)) art_mirror_id += 'M';
									}
									if(Ext.isEmpty(art_mirror_id)) return true;
									var mirror_r = store.findRecord('art_id',art_mirror_id,0,false,false,true);
									if(Ext.isEmpty(mirror_r) || mirror_r.get('cm_use')==cm_use) return true;
									mirror_r.beginEdit();
									mirror_r.set('cm_use',cm_use);
									mirror_r.endEdit(false,['cm_use']);
								});

							},
							buffer: 100
						}
					}]
				},{
					height: 100,
					xtype: 'gridpanel',
					fieldLabel: AgLang.history,

					columnLines: true,
					store: 'historyMappingStore',
					plugins: [self.getBufferedRenderer()],
					columns: [
						{xtype: 'rownumberer'},
						{text: AgLang.hist_event, dataIndex: 'he_name',        width: 50, minWidth: 50, hidden:false, hideable:false},
						{text: AgLang.version,    dataIndex: 'mv_name_e',      width: 40, minWidth: 40, hidden:false, hideable:false},
						{text: AgLang.cdi_name,   dataIndex: 'cdi_name',       width: 80, minWidth: 80, hidden:false, hideable:false, xtype:'agcolumncdiname'},
						{text: AgLang.cdi_name_e, dataIndex: 'cdi_name_e',     flex: 1,   minWidth: 80, hidden:false, hideable:false, xtype:'agcolumncdinamee'},

						{text: AgLang.cdi_name_j, dataIndex: 'cdi_name_j',     flex:1,    minWidth: 80, hidden:true,  hideable:false, xtype:'agcolumncdi'},
						{text: AgLang.cdi_name_k, dataIndex: 'cdi_name_k',     flex:1,    minWidth: 80, hidden:true,  hideable:false, xtype:'agcolumncdi'},
						{text: AgLang.cdi_name_l, dataIndex: 'cdi_name_l',     flex:1,    minWidth: 80, hidden:true,  hideable:false, xtype:'agcolumncdi'},

						{text: AgLang.comment,    dataIndex: 'cm_comment',     flex: 1,   minWidth: 80, hidden:false, hideable:false},
						{text: AgLang.use,        dataIndex: 'cm_use',         width:32,  minWidth:32,  hidden:false, hideable:false, xtype:'agbooleancolumn'},
						{text: AgLang.user,       dataIndex: 'cm_openid',      width:112, minWidth:112, hidden:true,  hideable:false},
						{text: AgLang.timestamp,  dataIndex: 'hist_timestamp', width:112, minWidth:112, hidden:false, hideable:false, xtype:'datecolumn', format:self.FORMAT_DATE_TIME}
					],
					selType: 'rowmodel',
					selModel: {
						mode:'SINGLE'
					}

				}]
			},{
				xtype:'fieldset',
				title: 'Obj',
				style: {
					padding: '0px 5px 5px 5px'
				},
				layout: {
					type: 'hbox',
					align: 'stretch'
				},
				items: [{
					xtype:'fieldcontainer',
					flex: 1,
					layout: 'form',
					defaults: {
						labelAlign: 'right',
						labelWidth: 56,
						anchor: '100%'
					},
					items: [{
						fieldLabel: AgLang.category,
						xtype: 'textfield',
						name: 'art_category',
						selectOnFocus: true,
						enableKeyEvents: true,
						listeners: {
							change: function(field,newValue,oldValue,eOpts){
								updateField(field);
							},
							keydown: function(field,e,eOpts){
								e.stopPropagation();
							},
							keypress: function(field,e,eOpts){
								e.stopPropagation();
							},
							keyup: function(field,e,eOpts){
								e.stopPropagation();
							}
						}
					},{
						fieldLabel: AgLang.class_name,
						xtype: 'textfield',
						name: 'art_class',
						selectOnFocus: true,
						enableKeyEvents: true,
						listeners: {
							change: function(field,newValue,oldValue,eOpts){
								updateField(field);
							},
							keydown: function(field,e,eOpts){
								e.stopPropagation();
							},
							keypress: function(field,e,eOpts){
								e.stopPropagation();
							},
							keyup: function(field,e,eOpts){
								e.stopPropagation();
							}
						}
					},{
						fieldLabel: AgLang.comment,
						xtype: 'textfield',
						name: 'art_comment',
						selectOnFocus: true,
						enableKeyEvents: true,
						listeners: {
							change: function(field,newValue,oldValue,eOpts){
								updateField(field);
							},
							keydown: function(field,e,eOpts){
								e.stopPropagation();
							},
							keypress: function(field,e,eOpts){
								e.stopPropagation();
							},
							keyup: function(field,e,eOpts){
								e.stopPropagation();
							}
						}
					},{
						fieldLabel: AgLang.judge,
						xtype: 'textfield',
						name: 'art_judge',
						selectOnFocus: true,
						enableKeyEvents: true,
						listeners: {
							change: function(field,newValue,oldValue,eOpts){
								updateField(field);
							},
							keydown: function(field,e,eOpts){
								e.stopPropagation();
							},
							keypress: function(field,e,eOpts){
								e.stopPropagation();
							},
							keyup: function(field,e,eOpts){
								e.stopPropagation();
							}
						}
					}]
				},{
					hidden: false,
					xtype:'fieldcontainer',
					width: 113,
					height: 108,
					style: {
						margin: '0 0 0 5px'
					},
					listeners: {
						afterrender: function( field, eOpts ){
							if(field.hidden) return;

							if(Ext.isEmpty(self.objEditMiniRenderer)){
								self.objEditMiniRenderer = new AgMiniRenderer({width:108,height:108,rate:1});
							}else{
								self.objEditMiniRenderer.domElement.style.display = '';
							}
							field.layout.innerCt.dom.appendChild( self.objEditMiniRenderer.domElement );

							var params = [];
							objEditStore.each(function(record){
								params.push({
									url: Ext.String.format('{0}/{1}?{2}',record.get('grouppath'),record.get('path'),record.get('mtime').getTime()),
									color: record.get('color'),
									opacity: record.get('opacity'),
									visible: record.get('remove') ? false : true
								});
							});
							self.objEditMiniRenderer.loadObj(params, function(){
								var gridpanel = field.up('window').down('gridpanel');
								var selModel = gridpanel.getSelectionModel();
								selModel.on('selectionchange', function(selModel,selected,eOpts){
									if(Ext.isEmpty(selected)) selected = objEditStore.getRange();
									var urls = [];
									Ext.each(selected,function(record){
										if(record.get('remove') || record.get('opacity')<=0) return true;
										urls.push(Ext.String.format('{0}/{1}?{2}',record.get('grouppath'),record.get('path'),record.get('mtime').getTime()));
									});
									self.objEditMiniRenderer.showObj(urls);
								});
								selModel.fireEvent('selectionchange', selModel, selModel.getSelection());
							});
						}
					}
				}]
			},{
				xtype:'fieldset',
				title: 'Mirroring',
				itemId: 'mirror',
				checkboxName: 'mirror',
				checkboxToggle: true,
				collapsed: true,
				style: {
					marginBottom: '0px',
					padding: '0px 10px 0px 10px'
				},
				listeners: {
					collapse: function(field, eOpts){
						var f = field.child('fieldset');
						if(f) f.collapse();
					},
					expand: function(field, eOpts){
						var f = field.child('fieldset');
						if(f) f.expand();
					},
					afterrender: {
						fn: function(field, eOpts){
							if(field.collapsed){
								field.fireEvent('collapse',field);
							}
							field.checkboxCmp.on({
								change: function(field,newValue,oldValue,eOpts){
									updateField(field);
								}
							});
						},
						single: true,
						buffer:100
					}
				},
				items: [{
					xtype:'fieldset',
					title: 'Concept',
					itemId: 'concept',
//						checkboxToggle: true,
//						collapsed: false,
//						checkboxName: 'mirror_map_concept',
					style: {
						padding: '0px 5px 5px 5px'
					},
					defaults: {
						labelAlign: 'right',
						labelWidth: 56
					},
					listeners: {
						collapse: function(field, eOpts){
							if(mv_frozen) return;
							var f = field.child('checkboxfield');
							if(f){
								f.setDisabled(true);
								f = f.nextSibling('fieldcontainer');
								if(f){
									f.setDisabled(true);
									f = field.nextSibling('displayfield');
									if(f) f.setDisabled(true);
								}
							}
						},
						expand: function(field, eOpts){
							if(mv_frozen) return;
							var f = field.child('checkboxfield');
							if(f){
								f.setDisabled(false);
								f.fireEvent('change',f,f.getValue());
							}

							var form = field.up('form').getForm();
							var mirror_cdi_name_field = form.findField(mirror_prefix+'cdi_name');
							var mirror_cdi_name_e_field = form.findField(mirror_prefix+'cdi_name_e');
							var mirror_cdi_name_edit_field = mirror_cdi_name_field.nextSibling('textfield');

							var art_ids = [];
							var gridpanel = field.up('window').down('grid');
							var records = gridpanel.getSelectionModel().getSelection();
							var store = gridpanel.getStore();
							Ext.each(records,function(r){
								var art_id = r.get('art_id');
								if(Ext.isEmpty(art_id)) return true;
								var art_mirror_id = null;
								if(art_id.match(/^([A-Z]+[0-9]+)(M*)$/)){
									art_mirror_id = RegExp.$1;
									if(Ext.isEmpty(RegExp.$2)) art_mirror_id += 'M';
								}
								if(Ext.isEmpty(art_mirror_id)) return true;
								art_ids.push({art_id:art_mirror_id});
							});
							if(Ext.isEmpty(art_ids)){
								if(mirror_cdi_name_field) setFieldValue(mirror_cdi_name_field, null);
								if(mirror_cdi_name_e_field) setFieldValue(mirror_cdi_name_e_field, null);
								if(mirror_cdi_name_edit_field) setFieldValue(mirror_cdi_name_edit_field, null);
								return;
							}

							//未設定の時のみ
							if(Ext.isEmpty(mirror_cdi_name_field.getValue()) || Ext.isEmpty(mirror_cdi_name_e_field.getValue()) || Ext.isEmpty(mirror_cdi_name_edit_field.getValue())){
								var params = self.getExtraParams() || {};
								delete params.model;
								delete params.version;
								delete params.ag_data;
								delete params.tree;
								delete params.current_datas;
								params.art_ids = Ext.encode(art_ids);

								Ext.Ajax.request({
									url: 'get-upload-obj-info.cgi',
									method: 'POST',
									params: params,
									callback: function(options, success, response){
									},
									success: function(response, options){
										var json;
										var records;
										try{json = Ext.decode(response.responseText)}catch(e){};
										if(Ext.isEmpty(json)){
											Ext.Msg.show({
												title: 'WARNING',
												msg: 'データの取得に失敗しました',
												buttons: Ext.Msg.OK,
												icon: Ext.Msg.WARNING
											});
											return;
										}
										if(Ext.isEmpty(json.datas)) return;
										if(json.datas[0]['cdi_name'] && mirror_cdi_name_field){
											setFieldValue(mirror_cdi_name_field, json.datas[0]['cdi_name']);
											if(mirror_cdi_name_edit_field) setFieldValue(mirror_cdi_name_edit_field, json.datas[0]['cdi_name']);
										}
										if(json.datas[0]['cdi_name_e'] && mirror_cdi_name_e_field) setFieldValue(mirror_cdi_name_e_field, json.datas[0]['cdi_name_e']);
									}
								});
							}
						}
					},
					items: [{
						disabled: mv_frozen,
						xtype: 'checkboxfield',
						fieldLabel: 'Concept',
						boxLabel: 'Same Concept',
						name: mirror_prefix+'same_concept',
						listeners: {
							change: function(field, newValue, oldValue, eOpts){
								var fields = [field];
								var f = field.nextSibling('fieldcontainer');
								if(f){
									f.setDisabled(newValue);
									f = field.nextSibling('displayfield');
									if(f) f.setDisabled(newValue);
									f = field.nextSibling('combobox');
									if(f) f.setDisabled(newValue);
								}
								if(newValue){
									var scrollTop = field.up('panel').body.dom.scrollTop;
									var basicForm = field.up('form').getForm();
									Ext.each(['cmp_id','cdi_name','cdi_name_e'],function(name,index,arr){
										var field = basicForm.findField(name);
										var mirror_field = basicForm.findField(mirror_prefix+name);
										if(Ext.isEmpty(field) || Ext.isEmpty(mirror_field)) return true;
										setFieldValue(mirror_field, field.getValue());
										fields.push(mirror_field);
									});

									var name = 'cdi_name';
									var field = basicForm.findField(name).nextSibling('combobox');
									var mirror_field = basicForm.findField(mirror_prefix+name).nextSibling('combobox');
									setFieldValue(mirror_field, field.getValue());

									if(scrollTop) field.up('panel').body.dom.scrollTop = scrollTop;
								}
								updateField(fields);
							}
						}
					},{
						xtype: 'fieldcontainer',
						fieldLabel: AgLang.cdi_name,
						itemId: 'cdi_name',
						bodyStyle: 'background:transparent;',
						border: false,
						anchor: '100%',
						layout: {
							type: 'hbox',
							pack: 'start'
						},
						defaults: {
							labelAlign: 'right',
							labelWidth: 62
						},
						listeners: {
							disable: function(field,eOpts){
								var cfield = field.child('textfield');
								while(cfield){
									cfield.setDisabled(true);
									cfield = cfield.nextSibling('button');
								}
							},
							enable: function(field,eOpts){
								var cfield = field.child('textfield');
								while(cfield){
									cfield.setDisabled(false);
									cfield = cfield.nextSibling('button');
								}
							}
						},
						items: [
						//2016-03-31用 START
						{
							xtype: 'agcdinamedisplayfield',
							name: mirror_prefix+'cdi_name',
							itemId: 'cdi_name',
							minWidth: 88,
							listeners: {
								change: function(field,newValue,oldValue,eOpts){
									updateField(field);
								}
							}
						},
						//2016-03-31用 END
						{
							disabled: mv_frozen,
//							width: 155,
							width: 88,
//							fieldLabel: AgLang.cdi_name,
//							xtype: 'textfield',

							xtype: 'combobox',
							store: 'fmaMirrorAllStore',
							queryMode: 'local',
							displayField: 'cdi_name',
							valueField: 'cdi_name',
							hideTrigger: true,
							anyMatch: true,

//							itemId: mirror_prefix+'cdi_name',		//2016-03-31用 COMMENT OUT
//							name: mirror_prefix+'cdi_name',			//2016-03-31用 COMMENT OUT
							itemId: 'cdi_name_edit',	//2016-03-31用 ADD

							selectOnFocus: true,
							enableKeyEvents: true,
							validator: cdiName.validator,
							listeners: {
								focus: cdiName.focus,
								change: function(field,newValue,oldValue,eOpts){
									cdiName.change(field,newValue,oldValue,mirror_prefix);
								},
								beforequery: cdiName.beforeQuery,
								select: function( field, records, eOpts ){
									return;
								},
								keydown: function(field,e,eOpts){
									e.stopPropagation();
								},
								keypress: function(field,e,eOpts){
									e.stopPropagation();
								},
								keyup: function(field,e,eOpts){
									e.stopPropagation();
								}
							}
						},{
							disabled: mv_frozen,
							width: 60,
							xtype: 'button',
							text: 'Mirror ID',
							listeners: {
								click: function(b,e,eOpts){

									var basicForm = b.up('form').getForm();
									var cmp_id_field = basicForm.findField('cmp_id');
									var cmp_record = cmp_id_field.findRecordByValue(cmp_id_field.getValue());
									if(cmp_record && (cmp_record.get('cmp_abbr')==='L' || cmp_record.get('cmp_abbr')==='R')){
										var fields = [];
										var mirror_cmp_record = cmp_id_field.findRecord('cmp_abbr', cmp_record.get('cmp_abbr')!=='L' ? 'L' : 'R');
										var mirror_cmp_id_field = basicForm.findField(mirror_prefix+'cmp_id');
										setFieldValue(mirror_cmp_id_field, mirror_cmp_record.get('cmp_id'));
										fields.push(mirror_cmp_id_field);

										var cdi_name_field = basicForm.findField('cdi_name');
										var cdi_name_edit_field = cdi_name_field.nextSibling('combobox')
										var cdi_name_e_field = basicForm.findField('cdi_name_e');

										var mirror_cdi_name_field = basicForm.findField(mirror_prefix+'cdi_name');
										var mirror_cdi_name_edit_field = mirror_cdi_name_field.nextSibling('combobox')
										setFieldValue(mirror_cdi_name_edit_field, mirror_cdi_name_field.renderer(cdi_name_field.getValue(),mirror_cdi_name_field));
										setFieldValue(mirror_cdi_name_field, cdi_name_field.getValue());
										fields.push(mirror_cdi_name_field);

										var mirror_cdi_name_e_field = basicForm.findField(mirror_prefix+'cdi_name_e');
										setFieldValue(mirror_cdi_name_e_field, cdi_name_e_field.getValue());
										fields.push(mirror_cdi_name_e_field);

										updateField(fields);

									}
									else{
										var field = basicForm.findField('cdi_name_e');
										if(Ext.isEmpty(field)) return;
										var value = field.getValue();
										if(Ext.isEmpty(value)) return;
										var cdi_name_e = '';
										if(value.match(/left/i)){
											cdi_name_e = value.replace(/left/i,'right');
										}else if(value.match(/right/i)){
											cdi_name_e = value.replace(/right/i,'left');
										}
										if(Ext.isEmpty(cdi_name_e)){
											Ext.Msg.alert(b.text, 'None Data');
											return;
										}

										b.setDisabled(true);
										b.up('fieldset').setLoading(true);

										var fmaSearchStore = Ext.data.StoreManager.lookup('fmaSearchStore');
										fmaSearchStore.clearFilter(true);
										fmaSearchStore.load({
											params: {
												cdi_name_e: cdi_name_e
											},
											callback: function(records,operation,success){
												b.setDisabled(false);
												b.up('fieldset').setLoading(false);
												if(!success || Ext.isEmpty(records)){
													Ext.Msg.alert(b.text, 'None Data');
													return;
												}
												var record = records[0];
												var basicForm = b.up('form').getForm();
												Ext.each(['cdi_name','cdi_name_e'],function(name,index,arr){
													var field = basicForm.findField(mirror_prefix+name);
													if(Ext.isEmpty(field)) return true;
													setFieldValue(field, record.get(name));
												});
												cdiName.selectPart(b, mirror_prefix);
											}
										});
									}
								}
							}
						},{
							disabled: mv_frozen,
							width: 100,
							xtype: 'button',
							iconCls: 'pallet_find',
							text: 'FMA Search',
							listeners: {
								click: function(b,e,eOpts){
									self.openFMASearch({
										title: b.text,
										iconCls: b.iconCls,
										animateTarget: b.getEl(),
										query: fmaSearch.query(b, mirror_prefix),
										callback: function(record){
											if(Ext.isEmpty(record)) return;
											fmaSearch.callback(record, b, mirror_prefix);
										}
									});
								}
							}
						},{
							disabled: mv_frozen,
							width: 22,
							xtype: 'button',
							iconCls: 'pallet_delete',
							listeners: {
								click : function(b,e,eOpts){
									cdiName.delete(b, mirror_prefix);
								}
							}
						}]
					},{
						hidden: true,
						disabled: mv_frozen,
						width: 130,
						anchor: null,
						editable: false,
						xtype: 'combobox',
						fieldLabel: 'Part',
						name: mirror_prefix+'cmp_id',
						itemId: 'cmp_id',
						store: 'conceptArtMapPartStore',
						queryMode: 'local',
						displayField: 'cmp_title',
						valueField: 'cmp_id',
						listeners: {
							change: function(field,newValue,oldValue,eOpts){
	//							console.log('change()');
								updateField(field);
							},
							select: function( field, records, eOpts ){
								cdiName.selectPart(field, mirror_prefix);
							}
						}
					},{
						xtype: 'agcdinameedisplayfield',
						fieldLabel: AgLang.cdi_name_e,
						name: mirror_prefix+'cdi_name_e',
						itemId: 'cdi_name_e',
						listeners: {
							change: function(field,newValue,oldValue,eOpts){
								updateField(field);
							}
						}
					}]
				}]
			}],
			listeners: {
				afterrender: function(comp){
					var form = comp.getForm();
					form.getFields().each(function(field){
						var xtype = field.getXType();
						if(xtype == 'combobox' && field.editable){
						}else if(xtype == 'textfield'){
						}else if(xtype == 'textareafield'){
						}else{
							return true;
						}
						var el = field.getEl();
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
								if(dropData != field.getValue()) field.setValue(dropData);
							}
						});
					});
				}
			}
		}],
		listeners: {
			afterrender: function(comp){
				return;
				var gridpanel = comp.down('gridpanel');
				var selModel = gridpanel.getSelectionModel();
				if(selModel.getSelectionMode() == 'MULTI'){
					selModel.selectAll();
				}else{
					selModel.select(comp.getStore().getAt(0));
				}
			},
			destroy: function(){
			},
			hide: function(comp){
				if(self.objEditMiniRenderer){
					self.objEditMiniRenderer.stopAnimate();
					self.objEditMiniRenderer.domElement.style.display = 'none';
					Ext.getBody().dom.appendChild( self.objEditMiniRenderer.domElement );
				}
			},
			beforeclose: function( comp, eOpts ){
//				console.log('beforeclose()');
			},
			beforedestroy: function( comp, eOpts ){
//				console.log('beforedestroy()');
			},
			beforehide: function( comp, eOpts ){
//				console.log('beforehide()');
				var rtn = Ext.isEmpty(objEditStore.getModifiedRecords());
				if(!rtn){
					Ext.Msg.show({
						buttons: Ext.Msg.YESNO,
						closable: false,
						title: comp.title,
						icon: Ext.Msg.QUESTION,
						iconCls: comp.iconCls,
						msg: '変更内容が保存されていません。破棄しますか？',
						defaultFocus: 'no',
						fn: function(buttonId){
							if(buttonId!=='yes') return;
							objEditStore.rejectChanges();
							comp.close();
						}
					});
				}
				return rtn;
			},
			show: function( comp ){
				if(mv_frozen){
					var gridpanel = comp.down('gridpanel');
					var selModel = gridpanel.getSelectionModel();
					if(selModel.getSelectionMode() == 'MULTI'){
						selModel.selectAll();
					}else{
						selModel.select(comp.getStore().getAt(0));
					}
				}else{
					var fmaAllStore = Ext.data.StoreManager.lookup('fmaAllStore');
					if(fmaAllStore && (fmaAllStore.isLoading() || fmaAllStore.getTotalCount()==0)){
						fmaAllStore.on({
							load: function(){
								comp.setLoading(false);

								var gridpanel = comp.down('gridpanel');
								var selModel = gridpanel.getSelectionModel();
								if(selModel.getSelectionMode() == 'MULTI'){
									selModel.selectAll();
								}else{
									selModel.select(comp.getStore().getAt(0));
								}

							},
							single: true
						});
						comp.setLoading(true);
					}else{
						var gridpanel = comp.down('gridpanel');
						var selModel = gridpanel.getSelectionModel();
						if(selModel.getSelectionMode() == 'MULTI'){
							selModel.selectAll();
						}else{
							selModel.select(comp.getStore().getAt(0));
						}
					}
				}
			}
		}
	});
};
