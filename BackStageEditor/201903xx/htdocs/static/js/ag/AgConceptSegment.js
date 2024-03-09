window.AgApp = window.AgApp || function(config){};
window.AgApp.prototype.getConceptSegmentStore = function(){
	var self = this;
	var storeId = 'conceptSegmentStore';
	var store = Ext.data.StoreManager.lookup(storeId);
	if(Ext.isEmpty(store)){
		store = Ext.create('Ext.data.Store', {
			storeId: storeId,
			model: 'CONCEPT_SEGMENT',
			autoLoad: false,
			autoSync: false,
			remoteFilter: false,
			remoteSort: false,
			filterOnLoad : false,
			sortOnFilter: false,
			sortOnLoad: false,
			sorters: [{
				property: 'seg_name',
				direction: 'ASC'
			}],
			proxy: {
				type: 'ajax',
				api: {
					create  : 'api-concept-segment-store.cgi?cmd=create',
					read    : 'api-concept-segment-store.cgi?cmd=read',
					update  : 'api-concept-segment-store.cgi?cmd=update',
					destroy : 'api-concept-segment-store.cgi?cmd=destroy',
				},
				timeout: 300000,
				noCache: true,
				pageParam: undefined,
				startParam: undefined,
				limitParam: undefined,
//				sortParam: undefined,
				groupParam: undefined,
				filterParam: undefined,
				batchOrder: 'destroy,create,update',
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
//					console.log("conceptSegmentStore.add()");
				},
				remove: function(store,record,index,eOpts){
//					console.log("conceptSegmentStore.remove()");
				},
				update: {
					fn: function(store,record,operation){
						console.log('conceptSegmentStore.update():'+operation);
						if(Ext.isString(record.get('cdi_names'))){
							var cdi_names = [];
							record.get('cdi_names').split(/[^A-Za-z0-9]+/).forEach(function(cdi_name){
								if(Ext.isString(cdi_name)){
									cdi_name = cdi_name.trim();
									if(cdi_name.length) cdi_names.push(cdi_name);
								}
							});
							if(record.get('cdi_names') != (cdi_names.length ? cdi_names.join(',') : null)){
								record.beginEdit();
								record.set('cdi_names', cdi_names.length ? cdi_names.join(',') : null);
								record.endEdit(false,['cdi_names']);
							}
						}
					},
					buffer: 250
//					setDisabledSaveButton();
				},
				beforeload: function(store, operation, eOpts){
					if(!self.beforeloadStore(store)) return false;
					var p = store.getProxy();
					p.extraParams = p.extraParams || {};
					delete p.extraParams.selected_artg_ids;
					delete p.extraParams.current_datas;
					delete p.extraParams.model;
					delete p.extraParams.version;
					delete p.extraParams.ag_data;
					delete p.extraParams.tree;
					delete p.extraParams._ExtVerMajor;
					delete p.extraParams._ExtVerMinor;
					delete p.extraParams._ExtVerPatch;
					delete p.extraParams._ExtVerBuild;
					delete p.extraParams._ExtVerRelease;
				},
				beforesync: function(options, eOpts){
//					console.log("conceptSegmentStore.beforesync()");
					var store = this;
					if(!self.beforeloadStore(store)) return false;
					var p = store.getProxy();
					p.extraParams = p.extraParams || {};
					delete p.extraParams.selected_artg_ids;
					delete p.extraParams.current_datas;
					delete p.extraParams.model;
					delete p.extraParams.version;
					delete p.extraParams.ag_data;
					delete p.extraParams.tree;
					delete p.extraParams._ExtVerMajor;
					delete p.extraParams._ExtVerMinor;
					delete p.extraParams._ExtVerPatch;
					delete p.extraParams._ExtVerBuild;
					delete p.extraParams._ExtVerRelease;
				},
				write: function(store, operation, eOpts){
//					console.log("conceptSegmentStore.write()");
				}
			}
		});
	}
	return store;
};

window.AgApp.prototype.openSegmentColorSettingWindow = function(config){
	var self = this;

	config = config || {};
	var aCB = config.callback;
	config.title = config.title || AgLang.segment_color_mng;
	config.iconCls = config.iconCls || 'color_pallet';
	config.height = config.height || 350;
	config.width = config.width || 600;
	config.modal = config.modal || true;

	var maxHeight = $(document.body).height();
	var maxWidth = $(document.body).width();

	if(config.height>maxHeight) config.height = maxHeight;
	if(config.width>maxWidth) config.width = maxWidth;

	var conceptSegmentStore = self.getConceptSegmentStore();
	conceptSegmentStore.loadPage(1);

	var window_id = Ext.id();

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
		var disable = false;
		if(!disable) disable = num===0;
		var toolbar = win.getDockedItems('toolbar[dock="bottom"]')[0];
		toolbar.getComponent('save').setDisabled(disable);
		toolbar.getComponent('reset').setDisabled(disable);
	};

	var setting_window = Ext.create('Ext.window.Window', {
		id: window_id,
		title: config.title,
		iconCls: config.iconCls,
		modal: config.modal,
		height: config.height,
		width: config.width,
		animateTarget: config.animateTarget,
		buttons: [{
			itemId: 'reset',
			text: AgLang.reset,
			disabled: true,
			listeners: {
				click: function(b,e,eOpts){
					var win = Ext.getCmp(window_id);
					var gridpanel = win.down('gridpanel');
					var store = gridpanel.getStore();
					store.rejectChanges();
					setDisabledSaveButton();
				}
			}
		},'->',{
			itemId: 'save',
			text: AgLang.save,
			disabled: true,
			listeners: {
				click: function(b,e,eOpts){
					if(b.isDisabled()) return;
					b.setDisabled(true);
					var win = b.up('window');
					if(win) win.setLoading(true);
					try{
						var gridpanel = win.down('gridpanel');
						var store = gridpanel.getStore();
						store.sync({
							callback: function(batch,options){
//								setDisabledSaveButton();
//								if(win) win.setLoading(false);
							},
							success: function(batch,options){
								setDisabledSaveButton();
								if(win) win.setLoading(false);
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
		layout: 'fit',
		items: [{
			xtype: 'aggridpanel',
			border: false,
			store: conceptSegmentStore,
			plugins: [
				Ext.create('Ext.grid.plugin.CellEditing', {
					clicksToEdit: 1,
					listeners: {
						beforeedit: function(editor,context,eOpts){
//							console.log('beforeedit',context);
							context.cancel = ((context.field==='seg_name' || context.field==='cdi_names') && context.record.get('seg_id')===0);
							return !context.cancel;
						},
						canceledit: function(editor,context,eOpts){
//							console.log('canceledit');
						},
						edit: function(editor,context,eOpts){
//							console.log('edit');
							if(Ext.String.trim(context.value).length != context.value.length){
								context.value = Ext.String.trim(context.value);
							}
						},
						validateedit: function(editor,context,eOpts){
//							console.log('validateedit');
							if(Ext.String.trim(context.value).length == 0){
								context.cancel = true;
//								context.record.data[context.field] = context.originalValue;
							}
						}
					}
				})
			],
			columns: [{
				text: AgLang.seg_name,
				dataIndex: 'seg_name',
				flex: 1,
				hidden:false,
				hideable:false,
				minWidth:60,
				editor: {
					xtype: 'textfield',
					allowBlank: true,
					selectOnFocus: true,
					listeners: {
						specialkey: function(field, e, eOpts){
							e.stopPropagation();
						}
					}
				}
			},{
				text: AgLang.seg_color_full,
				dataIndex: 'seg_color',
				width: 60,
				hidden:false,
				hideable:false,
				resizable: true,
				xtype:'agcolorbasecolumn'
			},{
				text: AgLang.seg_thum_bgcolor_full,
				dataIndex: 'seg_thum_bgcolor',
				width: 140,
				hidden:false,
				hideable:false,
				resizable: true,
				xtype:'agcolorbasecolumn'
			},{
				text: AgLang.seg_thum_fgcolor_full,
				dataIndex: 'seg_thum_fgcolor',
				width: 120,
				hidden:false,
				hideable:false,
				resizable: true,
				xtype:'agcolorbasecolumn'
			},{
				text: AgLang.cdi_names,
				dataIndex: 'cdi_names',
				flex: 1,
				hidden:false,
				hideable:false,
				minWidth:60,
				renderer: function(value,metaData,record,rowIndex,colIndex,store){
					var rtn;
					if(Ext.isString(value)){
						var cdi_names = [];
						value.split(/[^A-Za-z0-9]+/).forEach(function(cdi_name){
							if(Ext.isString(cdi_name)){
								cdi_name = cdi_name.trim();
								if(cdi_name.length) cdi_names.push(cdi_name);
							}
						});
						rtn = cdi_names.join(', ');
						metaData.style='white-space:normal;';
					}else{
						rtn = value;
					}
					return rtn;
				},
				editor: {
					xtype: 'textfield',
					allowBlank: true,
					selectOnFocus: true,
					listeners: {
						specialkey: function(field, e, eOpts){
							e.stopPropagation();
						}
					}
				}
			},{
				text: AgLang.use,
				dataIndex: 'seg_use',
				width: 34,
				hidden:false,
				hideable:false,
				resizable: true,
				xtype:'agcheckbasecolumn'
			}],
			selType: 'rowmodel',
			selModel: {
				mode:'SINGLE'
			},
			viewConfig: {
				stripeRows:true,
				enableTextSelection:false,
				loadMask:true
			},
			dockedItems: [{
				dock: 'top',
				xtype: 'toolbar',
				items: [{
					text: AgLang.add,
					iconCls: 'pallet_plus',
					listeners: {
						click: function(b){
							var gridpanel = b.up('gridpanel');
							var store = gridpanel.getStore();
							var rec = store.add([{seg_name:'new segment'}]);
							gridpanel.getSelectionModel().select(rec);
						}
					}
				},'-','->','-',{
					disabled: true,
					text: AgLang.remove,
					itemId: 'remove',
					iconCls: 'pallet_delete',
					listeners: {
						click: function(b){
							var gridpanel = b.up('gridpanel');
							var selModel = gridpanel.getSelectionModel();
							var rec = selModel.getLastSelected();
							var store = gridpanel.getStore();
							store.remove(rec);
							selModel.deselectAll();
						}
					}

				}]
			}],
			listeners: {
				afterrender: function(comp){
					comp.columns.forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
				},
				selectionchange: function(selModel,selected,eOpts){
					var grid = this;
					var toolbar = grid.getDockedItems('toolbar[dock="top"]')[0];
					var disabled = Ext.isEmpty(selected) || selected[0].data.seg_id===0;
					toolbar.getComponent('remove').setDisabled(disabled);
				}
			}
		}],
		listeners: {
			afterrender: function(comp){
				conceptSegmentStore.on({
					add: setDisabledSaveButton,
					remove: setDisabledSaveButton,
					update: setDisabledSaveButton
				});
			},
			destroy: function(comp){
				conceptSegmentStore.un({
					add: setDisabledSaveButton,
					remove: setDisabledSaveButton,
					update: setDisabledSaveButton
				});
			}
		}
	}).show();
};
window.AgApp.prototype.openConceptColorSettingWindow = function(config){
	var self = this;

//	console.log(config);
	config = config || {};
	config.records = config.records || [];
	var aCB = config.callback;
	config.title = config.title || AgLang.properties;
	config.iconCls = config.iconCls || 'color_pallet';
	config.height = config.height || 146;
	config.width = config.width || 600;
	config.modal = config.modal || true;

	var maxHeight = $(document.body).height();
	var maxWidth = $(document.body).width();

	if(config.height>maxHeight) config.height = maxHeight;
	if(config.width>maxWidth) config.width = maxWidth;

	if(Ext.isEmpty(config.records)){
		if(aCB) (aCB)();
		return;
	}

	config.record = Ext.create('BP3D_PROPERTY',config.records[0].data);
	config.title += ' ['+config.record.data.cdi_name+'] '+config.record.data.cdi_name_e;

	var conceptSegmentStore = self.getConceptSegmentStore();
	conceptSegmentStore.loadPage(1);

	var window_id = Ext.id();

	var setDisabledSaveButton = function(){
		try{
			var win = Ext.getCmp(window_id);
			var form = win.down('form');
			var baseForm = form.getForm();
			var rec = baseForm.getRecord();
			var dirty = baseForm.isDirty();
			var disable = !dirty;
			var toolbar = win.getDockedItems('toolbar[dock="bottom"]')[0];
			toolbar.getComponent('save').setDisabled(disable);
			toolbar.getComponent('reset').setDisabled(disable);
//			baseForm.findField('set_segment_recursively').setDisabled(disable);
		}catch(e){
			console.error(e);
		}
	};

	var setting_window = Ext.create('Ext.window.Window', {
		id: window_id,
		title: config.title,
		iconCls: config.iconCls,
		modal: config.modal,
		height: config.height,
		width: config.width,
		animateTarget: config.animateTarget,
		buttons: [{
			itemId: 'reset',
			text: AgLang.reset,
			disabled: true,
			listeners: {
				click: function(b,e,eOpts){
					var win = Ext.getCmp(window_id);
					win.down('form').getForm().reset();
					setDisabledSaveButton();
				}
			}
		},'->',{
			itemId: 'save',
			text: AgLang.save,
			disabled: true,
			listeners: {
				click: function(b,e,eOpts){
					if(b.isDisabled()) return;
					b.setDisabled(true);
					var win = b.up('window');
					if(win) win.setLoading(true);
					try{
						var baseForm = win.down('form').getForm();
						if(baseForm.isValid()){
							baseForm.submit({
								success: function(form, action) {
									if(win) win.setLoading(false);
									form.setValues(form.getValues());
									setDisabledSaveButton();
									Ext.data.StoreManager.lookup('treePanelStore').load();
									Ext.data.StoreManager.lookup('partsGridStore').loadPage(1);
									Ext.data.StoreManager.lookup('bp3dSearchStore').loadPage(1);
								},
								failure: function(form, action) {
									Ext.Msg.alert('Failed', action.result ? action.result.msg : 'No response');
									if(win) win.setLoading(false);
									setDisabledSaveButton();
								}
							});
						}
						else{
							setDisabledSaveButton();
						}
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
		layout: 'fit',
		items: [{
			xtype: 'form',
			border: false,

			url: 'api-concept-segment-store.cgi?cmd=update_concept',
			baseParams: self.getExtraParams(),
			jsonSubmit: false,
			method: 'POST',
			standardSubmit: false,
			timeout: 300,
			trackResetOnLoad: true,


			bodyPadding: 5,
			layout: 'anchor',
			defaults: {
				anchor: '100%'
			},
			fieldDefaults: {
				labelAlign: 'top',
				labelWidth: 100
			},
			items: [{
				xtype: 'fieldset',
//				padding: '0 10 5 10',
				items: [{
					xtype: 'fieldcontainer',
//					padding: '0 10 5 10',
					layout: 'column',
					defaultType: 'agcolordisplayfield',
					items: [{
						columnWidth: 0.20,
						fieldLabel: AgLang.seg_name,
						name: 'seg_id',
						xtype: 'combobox',
						store: conceptSegmentStore,
						queryMode: 'local',
						displayField: 'seg_name',
						valueField: 'seg_id',
						editable: false,
						allowBlank: false,
						allowOnlyWhitespace: false,
						listeners: {
							change: function( comp, newValue, oldValue, eOpts ){
//								console.log('change():'+comp.id);
							},
							select: function( comp, records, eOpts ){
//								console.log('select():'+comp.id);
								var next = comp.nextSibling();
								while(next){
									next.setValue(records[0].get(next.name));
									next = next.nextSibling();
								}
							}
						}
					},{
						columnWidth: 0.15,
						fieldLabel: AgLang.seg_color_full,
						name: 'seg_color'
					},{
						columnWidth: 0.35,
						fieldLabel: AgLang.seg_thum_bgcolor_full,
						name: 'seg_thum_bgcolor'
					},{
						columnWidth: 0.30,
						fieldLabel: AgLang.seg_thum_fgcolor_full,
						name: 'seg_thum_fgcolor'
					}]
				},{
					disabled: false,
					xtype: 'checkboxfield',
					boxLabel: AgLang.set_segment_recursively,
					name: 'set_segment_recursively',
					inputValue: 'true'
				},{
					disabled: false,
					xtype: 'hiddenfield',
					name: 'cdi_name'
				}]
			}],
			listeners: {
				afterrender: function(comp){
//					console.log('afterrender():'+comp.id);
				},
				dirtychange: function(comp){
//					console.log('dirtychange():'+comp.id);
					setDisabledSaveButton();
				},
				validitychange: function(comp){
//					console.log('validitychange():'+comp.id);
				}
			}
		}],
		listeners: {
			afterrender: function(comp){
				comp.down('form').getForm().loadRecord(config.record);
			},
			destroy: function(comp){
			}
		}
	}).show();
};
