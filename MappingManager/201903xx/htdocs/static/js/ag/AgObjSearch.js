window.AgApp = window.AgApp || function(config){};
window.AgApp.prototype.getObjSearchButton = function(){
	var self = this;
	return {
		itemId: 'obj_search',

		xtype: 'button',
		tooltip: AgLang.obj_search,
		text: 'OBJ',
		iconCls: 'obj-search-btn',
		disabled: false,
		listeners: {
			click: function(b){
				self.openObjSearchMngWin({
					title: b.tooltip,
					iconCls: b.iconCls,
					animateTarget: b.el
				});
			}
		}


/*
							afterrender: {
								fn: function(){
									console.log(toolbar.getWidth());
								},
								scope: self,
								single:true
							},
							resize: {
								fn: function( toolbar, width, height, oldWidth, oldHeight, eOpts){
									var searchfield_width = width-290;
									console.log(toolbar.getWidth(),searchfield_width);
									searchfield.setWidth(searchfield_width);
									while(!searchfield.getWidth()){
										console.log(searchfield.getWidth());
										searchfield.setWidth(searchfield_width);
									}
								},
								scope: self
							}
						});
					},
					specialkey: function(field, e, eOpts){
						e.stopPropagation();
					}
				}
*/

	};
};
window.AgApp.prototype.openObjSearchMngWin = function(aOpt){
	var self = this;
	aOpt = Ext.apply({},aOpt||{},{
		iconCls: 'obj-search-btn',
		title: AgLang.obj_search,
	});
	aOpt.id = aOpt.id || Ext.id();
	var idPrefix = aOpt.id+'-';


	var getGridColumns = function(){
		return [
		{
			text: AgLang.current,      dataIndex: 'current_use',       stateId: 'current_use',        width: 46, minWidth: 46, hidden: false, hideable: false, sortable: false, draggable: false, resizable: false,
			renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
				var tdCls = [];
				if(value){
					tdCls.push('gridcolumn_current_use');
				}else{
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
			text: '&#160;',            dataIndex: 'art_tmb_path',     stateId: 'art_tmb_path',      width: 24, minWidth: 24, hidden: false, hideable: false, sortable: false, draggable: false, resizable: false,
			renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
				if(record.data.seg_color){
//								metaData.style = 'background:'+record.data.seg_color+';';
				}
				metaData.innerCls = 'art_tmb_path';
				return value;
			}
		},
		{text: AgLang.art_id,       dataIndex: 'art_id',       stateId: 'art_id',        width: 54, minWidth: 54, hidden: true, hideable: false},
		{text: AgLang.art_id,       dataIndex: 'artc_id',      stateId: 'artc_id',       width: 54, minWidth: 54, hidden: false, hideable: true},
		{text: AgLang.cdi_name,     dataIndex: 'cdi_name',     stateId: 'cdi_name',      width: 80, minWidth: 80, hidden: true, hideable: false, xtype: 'agcolumncdiname' },
		{text: AgLang.cmp_abbr,     dataIndex: 'cmp_id',       stateId: 'cmp_id',        width: 40, minWidth: 40, hidden: true, hideable: false, xtype: 'agcolumnconceptartmappart' },
		{text: AgLang.cp_abbr,      dataIndex: 'cp_id',        stateId: 'cp_id',         width: 40, minWidth: 40, hidden: true, hideable: false, xtype: 'agcolumnconceptpart' },
		{text: AgLang.cl_abbr,      dataIndex: 'cl_id',        stateId: 'cl_id',         width: 40, minWidth: 40, hidden: true, hideable: false, xtype: 'agcolumnconceptlaterality' },

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


		{text: AgLang.artf_names,   dataIndex: 'artf_names',   stateId: 'artf_names',    flex: 2, minWidth: 80, hidden: false, hideable: false, xtype: 'agcolumnartfolder' },

//					{text: AgLang.upload_modified, dataIndex: 'art_upload_modified',stateId: 'art_upload_modified', width: 112,  hidden: true, hideable: true, xtype: 'datecolumn', format: self.FORMAT_DATE_TIME },
		{text: AgLang.cm_entry,     dataIndex: 'cm_entry',     stateId: 'cm_entry',      width: 67, hidden: true, hideable: false, xtype: 'datecolumn',     format: self.FORMAT_DATE }

		];
	};


	if(Ext.isEmpty(self.__ObjSearchMngWin)){

		var searchObjDStore = Ext.create('Ext.data.Store', {
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
					read: 'api-upload-file-list.cgi?cmd=read'
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
		});

		var searchObjRecord = function(){
			var search_gridpanel = self.__ObjSearchMngWin.down('gridpanel#search-gridpanel');
			var search_store = search_gridpanel.getStore();
			search_store.removeAll();

			var proxy = search_store.getProxy();
			proxy.extraParams = proxy.extraParams || {};
			proxy.extraParams.datas = Ext.JSON.encode(org_store.getRange().map(function(record){ return {art_id:record.get('art_id')}; }));
			search_store.loadPage(1,{
				callback: function(records, operation, success){
					if(success && records.length){
						search_gridpanel.setDisabled(false);
					}else{
						search_gridpanel.setDisabled(true);
					}
				}
			});
		};
		var uploadObjectStoreRemove = function(store, record, index, isMove, eOpts){
			store.on('write',function(){
				searchObjRecord();
			},this,{
				single: true
			});
		};

		var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
		uploadObjectStore.on('remove', uploadObjectStoreRemove, self);

		self.__ObjSearchMngWin = Ext.create('Ext.window.Window', {
			title: aOpt.title,
			iconCls: aOpt.iconCls,
			animateTarget: aOpt.animateTarget,
			height: 560,
			width: 560,
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
					margin: '5 5 0 5',
					emptyText: AgLang.obj_search_empty_text,
					fieldLabel: AgLang.obj_search,
					labelWidth: 30,
					hideLabel: true,
					xtype: 'searchfield',
					selectOnFocus: true,
					enableKeyEvents: true,
					store: searchObjDStore,
					listeners: {
						beforerender: function(searchfield, eOpt){
						},
						afterrender: function(searchfield, eOpt){
							searchfield.inputEl.set({autocomplete: 'on'});
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
					xtype:'fieldcontainer',
					flex: 1,
					style: {
						margin: '5px 0 5px 5px'
					},
					listeners: {
						afterrender: function( field, eOpts ){
							if(field.hidden) return;
							var formPanel = field.up('form');
							var gridpanel = formPanel.down('gridpanel#search-gridpanel');
							var store = gridpanel.getStore();
							var selModel = gridpanel.getSelectionModel();

							if(Ext.isEmpty(self.__ObjSearchMiniRenderer)){
								self.__ObjSearchMiniRenderer = new AgMiniRenderer({width:108,height:108,rate:1});
							}else{
								self.__ObjSearchMiniRenderer.domElement.style.display = '';
								self.__ObjSearchMiniRenderer.hideAllObj();
							}
							field.layout.innerCt.dom.appendChild( self.__ObjSearchMiniRenderer.domElement );

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
								self.__ObjSearchMiniRenderer.loadObj(params, function(){
									selModel.on('selectionchange', function(selModel,selected,eOpts){
										if(Ext.isEmpty(selected)) selected = store.getRange();
										var urls = [];
										Ext.each(selected,function(record){
											if(record.get('remove') || record.get('opacity')<=0) return true;
											urls.push(Ext.String.format('{0}?{1}',record.get('art_path'),record.get('art_timestamp').getTime()));
										});
										self.__ObjSearchMiniRenderer.showObj(urls);
									});
									selModel.fireEvent('selectionchange', selModel, selModel.getSelection());
								});
							};
							store.on({
								beforeload( store, operation, eOpts ){
									self.__ObjSearchMiniRenderer.hideAllObj();
								},
								load: function(store, records, successful, eOpts){
									if(successful) loadObj();
								}
							});
						},
						resize: function( field, width, height, oldWidth, oldHeight, eOpts){
//							console.log(width, height);
							self.__ObjSearchMiniRenderer.setSize(width-6,height-2);
						}
					}
				},{
					flex: 1,
					disabled: false,
					border: false,
					xtype: 'gridpanel',
					itemId: 'search-gridpanel',
					columns: getGridColumns(),
					columnLines: true,
					store: searchObjDStore,
					selType: 'rowmodel',
					selModel: {
						mode:'MULTI',
					},
					plugins: {
						ptype: 'bufferedrenderer',
						trailingBufferZone: 20,
						leadingBufferZone: 50
					},
					viewConfig: {
						stripeRows: true,
						plugins: {
							ddGroup: 'dd-upload_folder_tree',
							ptype: 'gridviewdragdrop',
							enableDrop: false
						},
						listeners: {
							itemkeydown: function(view, record, item, index, e, eOpts){
								e.stopEvent();
								if(e.ctrlKey && e.getKey() == e.A){
									var viewDom = view.el.dom;
									var scX = viewDom.scrollLeft;
									var scY = viewDom.scrollTop;
									var selModel = view.getSelectionModel();
									selModel.deselectAll(true);
									selModel.selectAll();
									view.focusRow(index);
									view.scrollBy(scX,scY,false);
									e.stopEvent()
								}
							}
						}
					},
					dockedItems: [{
						xtype: 'toolbar',
						dock: 'bottom',
						itemId: 'toolbar-bottom',
						items:['->','-',{
							xtype: 'tbtext',
							itemId: 'num',
							minWidth: 26,
							style: 'text-align:right;',
							text: '<label>0 Objects</label>'
						}]
					}],
					listeners: {
						afterrender: function(gridpanel){
							var store = gridpanel.getStore();
							store.removeAll();
							store.on({
								datachanged: function(store,eOpts){
									gridpanel.getDockedComponent('toolbar-bottom').getComponent('num').setText('<label>'+store.getCount()+' Objects</label>');
								}
							});
							gridpanel.getDockedComponent('toolbar-bottom').getComponent('num').setText('<label>'+store.getCount()+' Objects</label>');
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
					delete self.__ObjSearchMngWin;
					uploadObjectStore.un('remove', uploadObjectStoreRemove, self);
				}
			}
		});
	}
	self.__ObjSearchMngWin.show();
};
