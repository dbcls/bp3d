Ext.define('THUMBNAIL_BACKGROUND_PART', {
	extend: 'Ext.data.Model',
	fields: [{
		name: 'md_id',
		type: 'int'
	},{
		name: 'mv_id',
		type: 'int'
//	},{
//		name: 'ci_id',
//		type: 'int'
	},{
		name: 'cdi_name',
		type: 'string'
	},{
		name: 'cdi_name_org',
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.get('cdi_name');
			return v;
		}
	},{
		name: 'cdi_name_e',
		type: 'string'
	},{
		name: 'tbp_use',
		type: 'boolean',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = Ext.isEmpty(r.data.seg_delcause);
			return v;
		}
	},{
		name: 'tbp_delcause',
		useNull: true,
		defaultValue: null,
		type: 'string'
	}]
});


window.AgApp = window.AgApp || function(config){};
window.AgApp.prototype.getThumbnailBackgroundPartStore = function(){
	var self = this;
	var storeId = 'thumbnailBackgroundPartStore';
	var store = Ext.data.StoreManager.lookup(storeId);
	if(Ext.isEmpty(store)){
		store = Ext.create('Ext.data.Store', {
			storeId: storeId,
			model: 'THUMBNAIL_BACKGROUND_PART',
			autoLoad: false,
			autoSync: false,
			remoteFilter: false,
			remoteSort: false,
			filterOnLoad : false,
			sortOnFilter: false,
			sortOnLoad: false,
			sorters: [{
				property: 'cdi_name',
				direction: 'ASC'
			}],
			proxy: {
				type: 'ajax',
				api: {
					create  : 'api-thumbnail-background-part-store.cgi?cmd=create',
					read    : 'api-thumbnail-background-part-store.cgi?cmd=read',
					update  : 'api-thumbnail-background-part-store.cgi?cmd=update',
					destroy : 'api-thumbnail-background-part-store.cgi?cmd=destroy',
				},
				timeout: 300000,
				noCache: true,
				pageParam: undefined,
				startParam: undefined,
				limitParam: undefined,
//				sortParam: undefined,
				groupParam: undefined,
//				filterParam: undefined,
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
//					console.log("thumbnailBackgroundPartStore.add()");
				},
				remove: function(store,record,index,eOpts){
//					console.log("thumbnailBackgroundPartStore.remove()");
				},
				update: function(store,record,operation){
//					console.log("thumbnailBackgroundPartStore.update():"+operation);
//					setDisabledSaveButton();
				},
				beforeload: function(store, operation, eOpts){
//					console.log("thumbnailBackgroundPartStore.beforeload()");
				},
				beforesync: function(options, eOpts){
//					console.log("thumbnailBackgroundPartStore.beforesync()");
					return self.beforeloadStore(this);
				},
				write: function(store, operation, eOpts){
//					console.log("thumbnailBackgroundPartStore.write()");
				}
			}
		});
	}
	return store;
};

window.AgApp.prototype.openThumbnailBackgroundPartSettingWindow = function(config){
	var self = this;

	config = config || {};
	var aCB = config.callback;
	config.title = config.title || AgLang.thumbnail_background_part;
	config.iconCls = config.iconCls || 'thumbnail_background_part';
	config.height = config.height || 300;
//	config.height = config.height || 600;
//	config.width = config.width || 600;
	config.width = config.width || 350;
	config.modal = config.modal || true;

	var maxHeight = $(document.body).height();
	var maxWidth = $(document.body).width();

	if(config.height>maxHeight) config.height = maxHeight;
	if(config.width>maxWidth) config.width = maxWidth;

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

	var thumbnailBackgroundPartStore = self.getThumbnailBackgroundPartStore();
	thumbnailBackgroundPartStore.loadPage(1,{
		filters:[{
			property: 'md_id',
			value: config.record.get('md_id')
		},{
			property: 'mv_id',
			value: config.record.get('mv_id')
		}],
		callback: function(records, operation, success) {
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
									},
									success: function(batch,options){
										setDisabledSaveButton();
										if(win) win.setLoading(false);
										thumbnailBackgroundPartStore.loadPage(1,{
											filters:[{
												property: 'md_id',
												value: config.record.get('md_id')
											},{
												property: 'mv_id',
												value: config.record.get('mv_id')
											}]
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
				layout: 'fit',
				items: [{
					xtype: 'aggridpanel',
					border: false,
					store: thumbnailBackgroundPartStore,
					plugins: [
						Ext.create('Ext.grid.plugin.CellEditing', {
							clicksToEdit: 1,
							listeners: {
								beforeedit: function(editor,context,eOpts){
								},
								canceledit: function(editor,context,eOpts){
								},
								edit: function(editor,context,eOpts){
									if(Ext.String.trim(context.value).length != context.value.length){
										context.value = Ext.String.trim(context.value);
									}
								},
								validateedit: function(editor,context,eOpts){
									if(Ext.String.trim(context.value).length == 0){
										context.cancel = true;
									}
								}
							}
						})
					],
					columns: [{
						text: AgLang.cdi_name,
						dataIndex: 'cdi_name',
						hidden:false,
						hideable:false,
						width:80,
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
						text: AgLang.cdi_name_e,
						dataIndex: 'cdi_name_e',
						flex:1,
						minWidth:70,
						hidden:false,
						hideable:false
					},{
						text: AgLang.use,
						dataIndex: 'tbp_use',
						width: 34,
						hidden:false,
						hideable:false,
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
									var rec = store.add([{
										md_id:config.record.get('md_id'),
										mv_id:config.record.get('mv_id')
									}]);
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
						thumbnailBackgroundPartStore.on({
							add: setDisabledSaveButton,
							remove: setDisabledSaveButton,
							update: setDisabledSaveButton
						});
					},
					destroy: function(comp){
						thumbnailBackgroundPartStore.un({
							add: setDisabledSaveButton,
							remove: setDisabledSaveButton,
							update: setDisabledSaveButton
						});
					}
				}
			}).show(config.animateTarget,function(){
				if(Ext.isArray(config.records) && config.records.length){
					var gridpanel = this.down('gridpanel');
					var store = gridpanel.getStore();
					var records = [];
					Ext.each(config.records,function(record){
						var fr = store.findRecord( 'cdi_name', record.get('cdi_name'), 0, false, false, true );
						if(Ext.isEmpty(fr)){
							var recs = store.add({md_id:record.get('md_id'),mv_id:record.get('mv_id')});
							records.push(recs[0]);
							recs[0].set('cdi_name', record.get('cdi_name'));
							recs[0].set('cdi_name_org', record.get('cdi_name'));
							recs[0].set('cdi_name_e', record.get('cdi_name_e'));
						}
					});
					if(records.length) gridpanel.getSelectionModel().select(records[0]);
				}
			});
		},
		scope: self
	});
};
