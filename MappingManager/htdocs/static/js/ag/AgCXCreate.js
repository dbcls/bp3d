window.AgApp = window.AgApp || function(config){};
window.AgApp.prototype.getCXCreateButton = function(){
	var self = this;
	return {
		itemId: 'cx_create',
		xtype: 'button',
		tooltip: AgLang.cx_create,
		text: 'CX',
//		iconCls: 'pallet_join',
		iconCls: 'cx-create-btn',
		disabled: false,
		listeners: {
			click: function(b){
				self.openCXCreateMngWin({
					title: b.tooltip,
					iconCls: b.iconCls,
					animateTarget: b.el
				});
			}
		}
	};
};
window.AgApp.prototype.openCXCreateMngWin = function(aOpt){
	var self = this;
	aOpt = Ext.apply({},aOpt||{},{
		iconCls: 'pallet_join',
		title: AgLang.cx_create,
	});
	aOpt.id = aOpt.id || Ext.id();
	var idPrefix = aOpt.id+'-';
	var idCreateButton = idPrefix+'create-button';

	var getGridColumns = function(){
		return [

		{
			text: '&#160;',            dataIndex: 'art_tmb_path',     stateId: 'art_tmb_path',      width: 24, minWidth: 24, hidden: false, hideable: false, sortable: false, draggable: false, resizable: false,
			renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
				if(record.data.seg_color){
//								metaData.style = 'background:'+record.data.seg_color+';';
				}
				metaData.innerCls = 'art_tmb_path';
				return value;
			}
		},
		{text: AgLang.art_id,       dataIndex: 'art_id',       stateId: 'art_id',        width: 54, minWidth: 54, hidden: false, hideable: true},
		{text: AgLang.cdi_name,     dataIndex: 'cdi_name',     stateId: 'cdi_name',      width: 80, minWidth: 80, hidden: true, hideable: false, xtype: 'agcolumncdiname' },
		{text: AgLang.cmp_abbr,     dataIndex: 'cmp_id',       stateId: 'cmp_id',        width: 40, minWidth: 40, hidden: true, hideable: false, xtype: 'agcolumnconceptartmappart' },
		{text: AgLang.cdi_name_e,   dataIndex: 'cdi_name_e',   stateId: 'cdi_name_e',    flex: 2, minWidth: 80, hidden: true, hideable: false, xtype: 'agcolumncdinamee' },
		{text: AgLang.category,     dataIndex: 'arta_category',stateId: 'arta_category', flex: 1, minWidth: 50, hidden: true, hideable: true},
		{text: AgLang.class_name,   dataIndex: 'arta_class',   stateId: 'arta_class',    width: 36, minWidth: 36, hidden: true, hideable: true},
		{text: AgLang.comment,      dataIndex: 'arta_comment', stateId: 'arta_comment',  flex: 2, minWidth: 80, hidden: true, hideable: true},
		{text: AgLang.judge,        dataIndex: 'arta_judge',   stateId: 'arta_judge',    flex: 1, minWidth: 50, hidden: true, hideable: true},

		{text: AgLang.arto_id,      dataIndex: 'arto_id',      stateId: 'arto_id',       width: 60, minWidth: 60, hidden: true, hideable: true, sortable: false},
		{text: AgLang.arto_filename,dataIndex: 'arto_filename',stateId: 'arto_filename', flex: 2, minWidth: 80, hidden: true, hideable: true, sortable: false},
		{text: AgLang.arto_comment, dataIndex: 'arto_comment', stateId: 'arto_comment',  flex: 2, minWidth: 80, hidden: true, hideable: true, sortable: false},


		{text: AgLang.file_name,    dataIndex: 'art_filename', stateId: 'art_filename',  flex: 2, minWidth: 80, hidden: false, hideable: true},
		{text: 'Path',              dataIndex: 'art_path',     stateId: 'art_path',      flex: 1, minWidth: 50, hidden: true,  hideable: false},
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

		{text: AgLang.timestamp,    dataIndex: 'art_timestamp',stateId: 'art_timestamp', width: 67, hidden: false,  hideable: true, xtype: 'datecolumn',     format: self.FORMAT_DATE },
//					{text: AgLang.upload_modified, dataIndex: 'art_upload_modified',stateId: 'art_upload_modified', width: 112,  hidden: true, hideable: true, xtype: 'datecolumn', format: self.FORMAT_DATE_TIME },
		{text: AgLang.cm_entry,     dataIndex: 'cm_entry',     stateId: 'cm_entry',      width: 67, hidden: true, hideable: false, xtype: 'datecolumn',     format: self.FORMAT_DATE }

		];
	};

	var uploadFolderTreePanelStore = Ext.data.StoreManager.lookup('uploadFolderTreePanelStore');
	var uploadFolderTreeRecord = uploadFolderTreePanelStore.getRootNode().findChild('artf_comment','Combine Same FMA same dated obj files as new obj With prefix cx.',true);
	var uploadFolderTreeRecordInternalId = null;
	if(uploadFolderTreeRecord) uploadFolderTreeRecordInternalId = uploadFolderTreeRecord.internalId;
//	console.log(uploadFolderTreeRecord);
//	console.log(uploadFolderTreeRecordInternalId);

	if(Ext.isEmpty(self.__CXCreateMngWin)){
		var getCXRecord = function(){
			var create_gridpanel = self.__CXCreateMngWin.down('gridpanel#create-gridpanel');
			var create_store = create_gridpanel.getStore();

			var org_gridpanel = self.__CXCreateMngWin.down('gridpanel#org-gridpanel');
			var org_store = org_gridpanel.getStore();

			var create_button = Ext.getCmp(idCreateButton);

			create_store.removeAll();

			if(org_store.getCount()>1){
				var proxy = create_store.getProxy();
				proxy.extraParams = proxy.extraParams || {};
				proxy.extraParams.datas = Ext.JSON.encode(org_store.getRange().map(function(record){ return {art_id:record.get('art_id')}; }));
				create_store.loadPage(1,{
					callback: function(records, operation, success){
						if(success && records.length){
							create_gridpanel.setDisabled(false);
							create_button.setDisabled(true);
						}else{
							create_gridpanel.setDisabled(true);
							create_button.setDisabled(false);
						}
					}
				});
			}else{
				create_gridpanel.setDisabled(true);
				create_button.setDisabled(true);
			}
		};
		var uploadObjectStoreRemove = function(store, record, index, isMove, eOpts){
			store.on('write',function(){
				getCXRecord();
			},this,{
				single: true
			});
		};

		var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
		uploadObjectStore.on('remove', uploadObjectStoreRemove, self);

		self.__CXCreateMngWin = Ext.create('Ext.window.Window', {
			title: aOpt.title,
			iconCls: aOpt.iconCls,
			animateTarget: aOpt.animateTarget,
			height: 400,
			width: 460,
			resizable: true,
			layout: 'fit',
			items: {
				xtype: 'form',
				border: false,
				layout: {
					type: 'vbox',
					align: 'stretch',
					pack: 'center'
				},
				items: [{
					xtype: 'hiddenfield',
					itemId: 'folder_path',
					name: 'folder_path'
				},{
					xtype: 'hiddenfield',
					itemId: 'artf_id',
					name: 'artf_id'
				},{
					xtype:'fieldcontainer',
					flex: 1,
					layout: {
						type: 'hbox',
						align: 'stretch'
					},
					items: [{
						flex: 1,
						xtype: 'gridpanel',
						itemId: 'org-gridpanel',
						emptyText: 'drag & drop obj file(s)',
						columns: getGridColumns(),
						columnLines: true,
						store: Ext.create('Ext.data.Store', {
							model: 'PARTS',
							listeners: {
								add: function( store, records, index, eOpts ){
									getCXRecord();
								},
								remove: function( store, record, index, isMove, eOpts ){
									getCXRecord();
								}
							}
						}),
						selType: 'rowmodel',
						selModel: {
							mode:'MULTI',
						},
						plugins: {
							ptype: 'bufferedrenderer',
							trailingBufferZone: 20,  // Keep 20 rows rendered in the table behind scroll
							leadingBufferZone: 50   // Keep 50 rows rendered in the table ahead of scroll
						},
						viewConfig: {
							stripeRows: true,
							plugins: {
								ddGroup: 'dd-upload_folder_tree',
								ptype: 'gridviewdragdrop',
								enableDrag: false
							},
							listeners: {
								beforedrop: function( node, data, overModel, dropPosition, dropHandlers, eOpts ){
									var view = this;
									var grid = view.up('gridpanel');
									var store = view.getStore();
									if(data.records[0] && (Ext.getClassName(data.records[0])=='PARTS' || Ext.getClassName(data.records[0])=='PALLETPARTS' || Ext.getClassName(data.records[0])=='PICK_SEARCH' || Ext.getClassName(data.records[0])=='HISTORY_MAPPING')){
										var datas = [];
										data.records.forEach(function(r){
											var record = store.findRecord('art_id',r.get('art_id'),0,false,false,true);
											if(Ext.isEmpty(record)) datas.push(Ext.Object.merge({},r.getData(),{selected:true}));
										});
										if(datas.length){
											var sorters = store.sorters.getRange();
											if(sorters.length){
												store.sorters.clear();
												view.headerCt.clearOtherSortStates()
											}
											view.getSelectionModel().select(store.add(datas));
											if(sorters.length){
												store.sorters.addAll(sorters);
												store.sort();
											}
										}
										dropHandlers.cancelDrop();
									}else{
										dropHandlers.cancelDrop();
										return false;
									}
								},
								drop: function( node, data, overModel, dropPosition, eOpts ){
								}
							}
						},
						dockedItems: [{
							xtype: 'toolbar',
							dock: 'top',
							defaultType: 'button',
							items:[{
								xtype: 'tbtext',
								text: '<b>'+self.TITLE_UPLOAD_OBJECT+'</b>'
							},'->','-',{
								disabled: true,
//								iconCls: 'pallet_delete',
								text: 'remove selected obj file(s) from list',
								listeners: {
									afterrender: function(field){
										var gridpanel = field.up('gridpanel');
										gridpanel.on({
											selectionchange: function(selModel, selected, eOpts){
												var disabled = Ext.isEmpty(selected);
												field.setDisabled(disabled);
											}
										});
									},
									click: function(field){
										var gridpanel = field.up('gridpanel');
										var store = gridpanel.getStore();
										store.remove(gridpanel.getSelectionModel().getSelection());
									}
								}
							}]
						}],
						listeners: {
							afterrender: function(gridpanel){
								gridpanel.getStore().removeAll();
							}
						}
					},{
						hidden: false,
						xtype:'fieldcontainer',
						layout: {
							type: 'vbox',
							align: 'stretch',
							pack: 'start'
						},
						items: [{
							hidden: false,
							xtype:'fieldcontainer',
							width: 113,
							height: 108,
							style: {
								margin: '5px 0 5px 5px'
							},
							listeners: {
								afterrender: function( field, eOpts ){
									if(field.hidden) return;
									var formPanel = field.up('form');
									var gridpanel = formPanel.down('gridpanel#org-gridpanel');
									var store = gridpanel.getStore();
									var selModel = gridpanel.getSelectionModel();

									if(Ext.isEmpty(self.__CXCreateMiniRenderer)){
										self.__CXCreateMiniRenderer = new AgMiniRenderer({width:108,height:108,rate:1});
									}else{
										self.__CXCreateMiniRenderer.domElement.style.display = '';
										self.__CXCreateMiniRenderer.hideAllObj();
									}
									field.layout.innerCt.dom.appendChild( self.__CXCreateMiniRenderer.domElement );

									var loadObj = function(){
										var params = [];
										store.each(function(record){
											params.push({
												url: Ext.String.format('{0}?{1}',record.get('art_path'),record.get('art_timestamp').getTime()),
												color: record.get('color'),
												opacity: record.get('opacity'),
												visible: record.get('remove') ? false : true
											});
										});
										self.__CXCreateMiniRenderer.loadObj(params, function(){
											selModel.on('selectionchange', function(selModel,selected,eOpts){
												if(Ext.isEmpty(selected)) selected = store.getRange();
												var urls = [];
												Ext.each(selected,function(record){
													if(record.get('remove') || record.get('opacity')<=0) return true;
													urls.push(Ext.String.format('{0}?{1}',record.get('art_path'),record.get('art_timestamp').getTime()));
												});
												self.__CXCreateMiniRenderer.showObj(urls);
											});
											selModel.fireEvent('selectionchange', selModel, selModel.getSelection());
										});
									};
									store.on({
										add: function(){
											loadObj();
										},
										remove: function(){
											loadObj();
										}
									});
								}
							}
						},{
							hidden: true,
							xtype:'fieldcontainer',
							width: 113,
							height: 108,
							layout: {
								type: 'vbox',
								align: 'center',
								pack: 'start'
							},
							items: [{
								xtype: 'button',
								text: 'Export',
								handler: function(){
									if(Ext.isEmpty(self.__CXCreateMiniRenderer)) return;
									var exportObj = self.__CXCreateMiniRenderer.exportObjs();
									console.log(exportObj);
								}
							}]
						}]
					}]
				},{
					height: 22,
					padding: '5 5 0 5',
					xtype: 'textfield',
					itemId: 'file_name',
					name: 'file_name',
					fieldLabel: AgLang.file_name,
					labelAlign: 'right',
					labelWidth: 51,
					emptyText: 'Enter when you want to specify a file name',
					anchor: '100%',
					enableKeyEvents: true,
					listeners: {
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
					height: 22,
					padding: '0 5 0 5',

					xtype: 'treepicker',
					name: 'treepicker',
					fieldLabel: AgLang.cx_create_folder,
					labelAlign: 'right',
					labelWidth: AgLang.cx_create_folder_labelWidth,
					store: Ext.data.StoreManager.lookup('uploadFolderTreePanelStore'),
					displayField: 'text',
					valueField: 'artf_id',
					editable: false,
					anchor: '100%',
	//				value: uploadFolderTreeRecordInternalId,//artf_id,
					listeners: {
						afterrender: function(field){
							if(Ext.isEmpty(uploadFolderTreeRecordInternalId)) return;
							field.setValue(uploadFolderTreeRecordInternalId);
							field.fireEvent('select',field,uploadFolderTreeRecord);
						},
						select: function(field,record){
							var formPanel = field.up('form');
							if(record.get('artf_id')){
								formPanel.getComponent('folder_path').setValue(record.getPath('text').replace('//',''));
							}else{
								formPanel.getComponent('folder_path').setValue('/');
							}
							formPanel.getComponent('artf_id').setValue(record.get('artf_id'));
						}
					}
				},{
					xtype: 'panel',
					height: 28,
					buttons: [{
						disabled: true,
						id: idCreateButton,
						text: 'Create',
						handler: function(b) {
							var formPanel = b.up('form');
							var org_gridpanel = formPanel.down('gridpanel#org-gridpanel');
							org_gridpanel.getSelectionModel().selectAll();
							Ext.Msg.confirm(b.text, 'データを作成して宜しいですか？', function(btn){
								if(btn != 'yes') return;

								var create_gridpanel = formPanel.down('gridpanel#create-gridpanel');
								var create_store = create_gridpanel.getStore();
								create_store.removeAll();

								var org_store = org_gridpanel.getStore();
								var file_name = formPanel.getComponent('file_name').getValue().trim();
								var artf_id = formPanel.getComponent('artf_id').getValue() - 0;
								var extraParams = {
	//								folder_path: formPanel.getComponent('folder_path').getValue(),
									artf_id: artf_id,
									file_name: Ext.isEmpty(file_name) ? null : file_name,
									datas : Ext.JSON.encode(org_store.getRange().map(function(record){ return {art_id:record.get('art_id')}; })),
	//								geometry: self.__CXCreateMiniRenderer.exportObjs()
								};
	//							console.log(extraParams);
								var win = b.up('window');
								win.setLoading(true);

								var title = b.text;
								Ext.Ajax.request({
									url: 'api-cx-object-store.cgi?cmd=create',
									method: 'POST',
									params: extraParams,
									timeout: 300000,
									callback: function(options,success,response){
										win.setLoading(false);
										if(!success){
											Ext.Msg.show({
												title: title,
												msg: '['+response.status+'] '+response.statusText,
												iconCls: 'pallet_link',
												icon: Ext.Msg.ERROR,
												buttons: Ext.Msg.OK
											});
											return;
										}

										var json;
										try{json = Ext.decode(response.responseText)}catch(e){};
										if(Ext.isEmpty(json) || !json.success){
											var msg = 'Unknown error!!';
											if(Ext.isObject(json) && json.msg) msg = json.msg;
											Ext.Msg.show({
												title: title,
												msg: msg,
												icon: Ext.Msg.ERROR,
												buttons: Ext.Msg.OK
											});
											return;
										}
										getCXRecord();

										var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
										var proxy = uploadObjectStore.getProxy();
										var params = proxy.extraParams || {};
										if(artf_id===params.artf_id){
											uploadObjectStore.reload();
										}

									}
								});
							});
						}
					}]
				},{
					height: 64,
					disabled: true,
					xtype: 'gridpanel',
					itemId: 'create-gridpanel',
					columns: getGridColumns(),
					columnLines: true,
					store: Ext.create('Ext.data.Store', {
						model: 'PARTS',
						proxy: Ext.create('Ext.data.proxy.Ajax',{
							timeout: 300000,
							pageParam: undefined,
							startParam: undefined,
							limitParam: undefined,
							sortParam: undefined,
							groupParam: undefined,
							filterParam: undefined,
							api: {
								read: 'api-cx-object-store.cgi?cmd=read'
							},
							actionMethods : {
								read: 'POST'
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
								encode: false
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
						})
					}),
					viewConfig: {
						stripeRows: true,
						plugins: {
							ddGroup: 'dd-upload_folder_tree',
							ptype: 'gridviewdragdrop',
							enableDrop: false
						}
					},
					listeners: {
						afterrender: function(gridpanel){
							gridpanel.getStore().removeAll();
						}
					}
				}]
			},
			buttons: [{
				text: 'Close',
				handler: function(b) {
					b.up('window').close();
				}
			}],
			listeners: {
				destroy: function( win, eOpts ){
					delete self.__CXCreateMngWin;
					uploadObjectStore.un('remove', uploadObjectStoreRemove, self);
				}
			}
		});
	}
	self.__CXCreateMngWin.show();
};
