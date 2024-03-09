window.AgApp = window.AgApp || function(config){};
window.AgApp.prototype.getHiddenEditedGridColumn = function(aOpt){
	return true;
};
window.AgApp.prototype.openFreezeMappingMngWin = function(aOpt){
	var self = this;
	aOpt = Ext.apply({},aOpt||{},{
		iconCls: 'package-btn',
		title: AgLang.freeze_mapping,
	});
	aOpt.id = aOpt.id || Ext.id();
	aOpt.changeTargets = aOpt.changeTargets || [];

	var idPrefix = aOpt.id+'-';
	var storeId = idPrefix+'store';

	var pointLabel = AgLang.corrected_reference_point;
	var commentLabel = AgLang.comment;
	var timestampLabel = aOpt.title+' Time stamp';
	var statusLabel = 'status';

	var createLabel = 'Create ' + aOpt.title;
	var editLabel = 'Edit ' + aOpt.title+' attribute';
	var downloadLabel = 'Download ' + aOpt.title;
	var deleteLabel = 'Delete ' + aOpt.title;



	var editFreezeMapping = function(options){
		options = options || {};
		var title = options.title;
		var iconCls = options.iconCls;
		var animateTarget = options.animateTarget;
		var record = options.record;
		var store = Ext.data.StoreManager.lookup(storeId);
//		console.log(record.getData());

		Ext.create('Ext.window.Window', {
			title: title,
			iconCls: iconCls,
			animateTarget: animateTarget,
			height: 165,
			width: 500,
			modal: true,
			resizable: false,
			closable: false,
			layout: 'fit',
			items: {
				xtype: 'form',
				border: false,
				bodyPadding: 5,
				items: [{
					xtype: 'displayfield',
					fieldLabel: timestampLabel,
					labelWidth: 156,
					anchor: '100%',
					name: 'fm_timestamp_format',
				},{
					xtype: 'checkboxfield',
					boxLabel: pointLabel,
					name: 'fm_point',
					handler: function(field,value){
						var name = field.name;
						record.beginEdit();
						record.set(name,value);
						record.endEdit(false,[name]);
					}
				},{
					xtype: 'textfield',
					name: 'fm_comment',
					fieldLabel: commentLabel,
					labelAlign: 'top',
					allowBlank: true,
					anchor: '100%',
					listeners: {
						change: function( field, value, oldValue, eOpts ){
							var name = field.name;
							record.beginEdit();
							record.set(name,value);
							record.endEdit(false,[name]);
						}
					}
				}],
				buttons: [{
					xtype: 'button',
					text: 'Cancel',
					handler: function(b,e){
						var store = Ext.data.StoreManager.lookup(storeId);
						store.rejectChanges();
						b.up('window').close();
					}
				},'->',{
					xtype: 'button',
					text: 'Submit',
					handler: function(b,e){
						var store = Ext.data.StoreManager.lookup(storeId);
						if(Ext.isEmpty(store.getModifiedRecords())){
							store.loadPage(1);
							b.up('window').close();
						}else{
//							b.setDisabled(true);
//							b.prev('button').setDisabled(true);
							b.up('window').setLoading(record.get('fm_id') ? true : '２分程お待ち下さい…');
							store.sync({
								success: function(batch,options){
									store.loadPage(1);
									b.up('window').close();
									if(Ext.isArray(aOpt.changeTargets)){
										Ext.each(aOpt.changeTargets,function(changeTarget){
											changeTarget.fireEvent('change',changeTarget);
										});
									}
								},
								failure: function(batch,options){
									var msg = AgLang.error_submit;
									var proxy = this;
									var reader = proxy.getReader();
									if(reader && reader.rawData && reader.rawData.msg){
										msg += ' ['+reader.rawData.msg+']';
									}
									Ext.Msg.show({
										title: title,
										iconCls: iconCls,
										msg: msg,
										buttons: Ext.Msg.OK,
										icon: Ext.Msg.ERROR,
										fn: function(buttonId,text,opt){
										}
									});
//									b.setDisabled(false);
									b.up('window').setLoading(false);
								}
							});
						}
					}
				}],
				listeners: {
					afterrender: function(form){
						form.loadRecord(record);
					}
				}
			}
		}).show();
	};

	var toolbar_button_afterrender = function(b){
		var gridpanel = b.up('gridpanel');
		var selModel = gridpanel.getSelectionModel();
		selModel.on({
			deselect: function( selModel, record, index, eOpts ){
				b.setDisabled(true);
			},
			select: function( selModel, record, index, eOpts ){
				b.setDisabled(false);
			},
			selectionchange: function( selModel, selected, eOpts ){
				if(Ext.isEmpty(selected)){
					b.setDisabled(true);
				}else{
					b.setDisabled(false);
				}
			}
		});
	};

	Ext.create('Ext.window.Window', {
		title: aOpt.title,
		iconCls: aOpt.iconCls,
		animateTarget: aOpt.animateTarget,
		height: 400,
		width: 500,
		modal: true,
		layout: 'fit',
		buttons: [{
			xtype: 'button',
			text: 'Close',
			handler: function(b,e){
				b.up('window').close();
			}
		}],
		items: {
			xtype: 'gridpanel',
			border: false,
			columns: [
				{xtype: 'rownumberer'},
				{text: timestampLabel, dataIndex: 'fm_timestamp', stateId: 'fm_timestamp', width: 162, hidden: false, hideable: false, xtype: 'datecolumn', format: self.FORMAT_DATE_TIME },
				{text: pointLabel, dataIndex: 'fm_point',     stateId: 'fm_point',     width: 150, hidden: false, hideable: false,

//				xtype: 'checkcolumn'
					renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
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
						return '';
					}

				},
				{text: commentLabel,   dataIndex: 'fm_comment',   stateId: 'fm_comment',   flex: 1,    hidden: false, hideable: false, xtype: 'gridcolumn'},
				{text: statusLabel,    dataIndex: 'fm_status',    stateId: 'fm_status',    flex: 1,    hidden: false, hideable: false, xtype: 'gridcolumn'}
			],
			plugins: {
				ptype: 'bufferedrenderer',
				trailingBufferZone: 20,
				leadingBufferZone: 50
			},
			listeners: {
				beforeselect: function(selmodel, record, index, eOpts){
					return (record.get('fm_status') === 'finish' || record.get('fm_status') === 'error');
				}
			},
			store: Ext.create('Ext.data.Store', {
				storeId: storeId,
				fields:[
					{name: 'fm_id',        type: 'int'},
					{name: 'fm_point',     type: 'boolean', defaultValue: false, },
					{name: 'fm_timestamp', type: 'date', dateFormat: 'timestamp', serialize: function(v,rec){return Ext.Date.format(v,'Y-m-d H:i:s');} },
					{name: 'fm_timestamp_format', type: 'string', convert: function(v,rec){
//						if(Ext.isEmpty(v)){
							return Ext.Date.format(rec.get('fm_timestamp'),self.FORMAT_DATE_TIME);
//						}else{
//							return v;
//						}
					}, persist: false },
					{name: 'fm_comment',   type: 'string', defaultValue: null, useNull: true},
					{name: 'fm_status',    type: 'string', defaultValue: null, useNull: true},
				],
				sorters: [{
					property: 'fm_timestamp',
					direction: 'DESC'
				}],
				autoLoad: true,
				autoSync: false,
				remoteFilter: false,
				remoteSort: false,
				filterOnLoad : false,
				sortOnFilter: false,
				sortOnLoad: false,
				proxy: Ext.create('Ext.data.proxy.Ajax',{
					type: 'ajax',
					timeout: 300000 * 3,
					api: {
						create  : 'api-freeze-mapping-store.cgi?cmd=create',
						read    : 'api-freeze-mapping-store.cgi?cmd=read',
						update  : 'api-freeze-mapping-store.cgi?cmd=update',
						destroy : 'api-freeze-mapping-store.cgi?cmd=destroy',
					},
					actionMethods : {
						create : 'POST',
						read   : 'POST',
						update : 'POST',
						destroy: 'POST'
					},
					limitParam: undefined,
					pageParam: undefined,
					sortParam: undefined,
					startParam: undefined,
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
				}),
				listeners: {
					load: function(store){
						store.sort();
					}
				}
			}),
			dockedItems: [{
				xtype: 'toolbar',
				dock: 'top',
				items: [{
					xtype: 'button',
					iconCls: 'package_add-btn',
					text: createLabel,
					handler: function(b,e){
						var gridpanel = b.up('gridpanel');
						var store = gridpanel.getStore();
						var fm_timestamp = new Date();
						var records = store.add({
							fm_timestamp: fm_timestamp,
							fm_timestamp_format: Ext.Date.format(fm_timestamp,self.FORMAT_DATE_TIME)
						});
						var record = records[0];
						editFreezeMapping({
							title: b.text || b.tooltip,
							iconCls: b.iconCls,
							animateTarget: b.el,
							record: record
						});
					}
				},'-','->','-',{
					disabled: true,
					xtype: 'button',
					iconCls: 'package_edit-btn',
					tooltip: editLabel,
					handler: function(b,e){
						var gridpanel = b.up('gridpanel');
						var selModel = gridpanel.getSelectionModel();
						var records = selModel.getSelection();
						var record = records[0];
						editFreezeMapping({
							title: b.text || b.tooltip,
							iconCls: b.iconCls,
							animateTarget: b.el,
							record: record
						});
					},
					listeners: {
						afterrender: toolbar_button_afterrender
					}
				},'-',{
					disabled: true,
					xtype: 'button',
					iconCls: 'pallet_download',
					tooltip: downloadLabel,
					handler: function(b,e){
						var gridpanel = b.up('gridpanel');
						var store = gridpanel.getStore();
						var selModel = gridpanel.getSelectionModel();
						var records = selModel.getSelection();
						var record = records[0];
						var p = record.getData();
						p.cmd = 'download';
						window.location.href = 'api-freeze-mapping-store.cgi?'+ Ext.Object.toQueryString(p);
					},
					listeners: {
						afterrender: toolbar_button_afterrender
					}
				},'-',{
					disabled: true,
					xtype: 'button',
					iconCls: 'pallet_delete',
					tooltip: deleteLabel,
					handler: function(b,e){
						var gridpanel = b.up('gridpanel');
						var store = gridpanel.getStore();
						var selModel = gridpanel.getSelectionModel();
						var records = selModel.getSelection();
						var record = records[0];

						var msg = '選択されている情報を削除してよろしいですか？';

						Ext.Msg.show({
							title: deleteLabel,
							msg: msg,
							iconCls: 'pallet_delete',
							buttons: Ext.Msg.YESNO,
							defaultFocus: 'no',
							fn: function(btn){
								if(btn != 'yes'){
									b.setDisabled(false);
									b.setIconCls('pallet_delete');
									return;
								}

								store.remove(record);
								store.sync({
									success: function(batch,options){
										store.loadPage(1);
									},
									failure: function(batch,options){
										var msg = AgLang.error_submit;
										var proxy = this;
										var reader = proxy.getReader();
										if(reader && reader.rawData && reader.rawData.msg){
											msg += ' ['+reader.rawData.msg+']';
										}
										Ext.Msg.show({
											title: title,
											iconCls: iconCls,
											msg: msg,
											buttons: Ext.Msg.OK,
											icon: Ext.Msg.ERROR,
											fn: function(buttonId,text,opt){
											}
										});
										store.rejectChanges();
									}
								});
							}
						});


					},
					listeners: {
						afterrender: toolbar_button_afterrender
					}
				}]
			},{
				xtype: 'pagingtoolbar',
				store: storeId,   // same store GridPanel is using
				dock: 'bottom',
				displayInfo: true
			}]

		}
	}).show();

};
