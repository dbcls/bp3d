///////////////////////////////////////////////////////////////////////////////
//ピック機能のレスポンス向上
///////////////////////////////////////////////////////////////////////////////
window.ag_extensions = window.ag_extensions || {};
ag_extensions.pallet_element = ag_extensions.pallet_element || {};
///////////////////////////////////////////////////////////////////////////////
//初期化
///////////////////////////////////////////////////////////////////////////////
ag_extensions.pallet_element._init = function(){
	var self = this;
//	console.log('ag_extensions.pallet_element._init()');

	self.__MIN_PAGE_SIZE = 100;
	self.__MAX_PAGE_SIZE = 3000;
	self.__STEP_PAGE_SIZE = 100;
	self.__COOKIE_LIMIT_KEY = 'ag_extensions.pallet_element.pagesize';

	self.__Panel_id = 'ag-parts-element-panel';
	self.__GridPanel_id = 'ag-parts-element-gridpanel';
	self.__PagingBar_id = 'ag-parts-element-paging-toolbar';

	self.__palletGridPanel_id = 'ag-parts-gridpanel';
	self.__parentTabPanel_id = 'ag-comment-tabpanel';

	self.__contentsTabPanel_id = 'contents-tab-panel';
	self.__contentsAnatomographyPanel_id = 'contents-tab-anatomography-panel';

	self.__Panel = null;
	self.__GridStore = null;
	self.__GridPanel = null;
	self.__PagingBar = null;
	self.__palletGridPanel = null;
	self.__palletGridStore = null;
	self.__contentsTabPanel = null;

	self.__parentTabPanel = Ext.getCmp(self.__parentTabPanel_id);

	self._loadStoreDelayedTask = new Ext.util.DelayedTask(self._loadStore, self);

	if(self.__parentTabPanel){
		if(self.__parentTabPanel.rendered){
			self._initUI();
		}else{
			self.__parentTabPanel.on({
				render: function(){
					self._initUI();
				},
				buffer: 100,
				single: true
			});
		}
	}else{
		self.__initTask = {
			run: function(){
				self.__parentTabPanel = Ext.getCmp(self.__parentTabPanel_id);
				if(!self.__parentTabPanel) return;
				self.__initTaskRunner.stop(self.__initTask);
				if(self.__parentTabPanel.rendered){
					self._initUI();
				}else{
					self.__parentTabPanel.on({
						render: function(){
							self._initUI();
						},
						buffer: 100,
						single: true
					});
				}
			},
			interval: 1000
		}
		self.__initTaskRunner = new Ext.util.TaskRunner();
		self.__initTaskRunner.start(self.__initTask);
	}
};
///////////////////////////////////////////////////////////////////////////////
//Store初期化
///////////////////////////////////////////////////////////////////////////////
ag_extensions.pallet_element._initStore = function(){
	var self = this;
//	console.log('ag_extensions.pallet_element._initStore()');

	var store_fields = [
		{name:'partslist'},
		{name:'common_id'},
		{name:'b_id'},
		{name:'f_id',type:'string',convert:function(v,r){
			if(Ext.isEmpty(v)){
				return r.cdi_name;
			}else{
				return v;
			}
		}},
		{name:'name_j'},
		{name:'name_e',type:'string',convert:function(v,r){
			if(Ext.isEmpty(v)){
				return r.cdi_name_e;
			}else{
				return v;
			}
		}},
		{name:'name_k'},
		{name:'name_l'},
		{name:'phase'},
		'version',
//		'tg_id',
//		'tgi_id',
		{name:'tg_id',type:'int',convert:function(v,r){
			if(Ext.isEmpty(v)){
				return r.md_id;
			}else{
				return v;
			}
		}},
		{name:'tgi_id',type:'int',convert:function(v,r){
			if(Ext.isEmpty(v)){
				return r.mv_id;
			}else{
				return v;
			}
		}},

		'segment',
		'seg_color',
		'seg_thum_bgcolor',
		'seg_thum_bocolor',

		{name:'entry',   type:'date', dateFormat: 'timestamp',convert:function(v,r){
			if(Ext.isEmpty(v)){
				return r.rep_entry;
			}else{
				return v;
			}
		}},
		{name:'xmin',    type:'float',convert:function(v,r){
			if(Ext.isEmpty(v)){
				return r.rep_xmin;
			}else{
				return v;
			}
		}},
		{name:'xmax',    type:'float',convert:function(v,r){
			if(Ext.isEmpty(v)){
				return r.rep_xmax;
			}else{
				return v;
			}
		}},
		{name:'ymin',    type:'float',convert:function(v,r){
			if(Ext.isEmpty(v)){
				return r.rep_ymin;
			}else{
				return v;
			}
		}},
		{name:'ymax',    type:'float',convert:function(v,r){
			if(Ext.isEmpty(v)){
				return r.rep_ymax;
			}else{
				return v;
			}
		}},
		{name:'zmin',    type:'float',convert:function(v,r){
			if(Ext.isEmpty(v)){
				return r.rep_zmin;
			}else{
				return v;
			}
		}},
		{name:'zmax',    type:'float',convert:function(v,r){
			if(Ext.isEmpty(v)){
				return r.rep_zmax;
			}else{
				return v;
			}
		}},
		{name:'volume',  type:'float',convert:function(v,r){
			if(Ext.isEmpty(v)){
				return r.rep_volume;
			}else{
				return v;
			}
		}},
		{name:'organsys'},
		{name:'color'},
		{name:'value',defaultValue:''},
		{name:'zoom',type:'boolean',defaultValue:true},
		{name:'exclude',type:'boolean',defaultValue:false},
		{name:'opacity',type:'float',defaultValue:'1.0'},
		{name:'representation',defaultValue:'surface'},
		{name:'point',type:'boolean',defaultValue:false},
		{name:'elem_type'},
		{name:'def_color'},
		{name:'bul_id',type:'int'},
		{name:'cb_id',type:'int'},
		{name:'ci_id',type:'int'},
		{name:'md_id',type:'int'},
		{name:'mv_id',type:'int'},
		{name:'mr_id',type:'int'},
		{name:'cdi_name',type:'string'},
		{name:'cdi_name_e',type:'string'},
		{name:'rep_id',type:'string'},
		{name:'rep_xmin', type:'float'},
		{name:'rep_xmax', type:'float'},
		{name:'rep_ymin', type:'float'},
		{name:'rep_ymax', type:'float'},
		{name:'rep_zmin', type:'float'},
		{name:'rep_zmax', type:'float'},
		{name:'rep_volume', type:'float'},
		{name:'rep_entry',type:'date', dateFormat: 'timestamp'},
		{name:'rep_depth',type:'int'}
	];


	self.__GridStore = new Ext.data.JsonStore({
		url: 'get-pallet-element.cgi',
		autoLoad: false,
		root: 'datas',
		fields: store_fields,
		sortInfo: {
			field: 'rep_depth',
			direction: 'DESC'
		},
		listeners: {
			beforeload: function(store,options){
//				console.log('ag_extensions.pallet_element.__Store.beforeload()');
			},
			load: function(store,records,options){
//				console.log('ag_extensions.pallet_element.__Store.load()');
				var gridView = self.__GridPanel.getView();
				if(store.reader.jsonData.msg){
					gridView.emptyText = '<div class="bp3d-pallet-empty-message">'+store.reader.jsonData.msg+'</div>';
//            this.mainBody.update('<div class="x-grid-empty">' + this.emptyText + '</div>');
					self._clearStore(false);
				}else{
//					gridView.emptyText = '<div class="bp3d-pallet-empty-message">'+get_ag_lang('CLICK_IMAGE_GRID_EMPTY_MESSAGE')+'</div>';
					gridView.emptyText = '&nbsp;';
				}
				gridView.applyEmptyText();

				try{
					var toolbar = self.__PagingBar;
					var count = toolbar.items.getCount();
					if(count>0){
						var item = toolbar.items.get(1);
						item.el.innerHTML='<label>'+store.reader.jsonData.total+'&nbsp;Objects</label>';
					}
				}catch(e){
					_dump("load():"+e);
				}

//				console.log('ag_extensions.pallet_element.__Store.load():'+records.length);

				self._updateRecordsStatus(records);

				var storeLastOptionsParams = self._getStoreLastOptionsParams();
				Cookies.set(self.__COOKIE_LIMIT_KEY,storeLastOptionsParams.limit);
			},
			loadexception: function(){
				var store = this;
				var msg = store.reader && store.reader.jsonData && store.reader.jsonData.msg ? store.reader.jsonData.msg : 'Unknown Error!!';
				Ext.Msg.show({
					title: 'Error',
					msg: msg,
					buttons: Ext.Msg.OK,
					icon: Ext.MessageBox.ERROR
				});
				self._clearStore();
			}
		}
	});
};
///////////////////////////////////////////////////////////////////////////////
//UI初期化
///////////////////////////////////////////////////////////////////////////////
ag_extensions.pallet_element._initUI = function(){
	var self = this;
//	console.log('ag_extensions.pallet_element._initUI()');

	var insert_index = self.__parentTabPanel.items.findIndex('id',self.__palletGridPanel_id,0,false,true);
	if(insert_index<0) insert_index = 0;

	self._initStore();

	self.__PagingSizeData = [];
	for(var i=self.__MIN_PAGE_SIZE;i<=self.__MAX_PAGE_SIZE;i+=self.__STEP_PAGE_SIZE){
		self.__PagingSizeData.push([i,i]);
	}
	self.__PagingSizeComboBox = new Ext.form.ComboBox({
		ctCls         : 'x-small-editor',
		editable      : false,
		mode          : 'local',
		lazyInit      : false,
		displayField  : 'disp',
		valueField    : 'value',
		width         : 55,
		listWidth     : 55,
		triggerAction : 'all',
		value         : Cookies.get(self.__COOKIE_LIMIT_KEY) || self.__PagingSizeData[0][0],
		regex         : new RegExp("^[\-0-9]+$"),
		allowBlank    : false,
		selectOnFocus : true,
		validator     : function(value){
			value = Number(value);
			if(isNaN(value)) return '';
			return true;
		},
		store : new Ext.data.SimpleStore({
			fields: ['disp', 'value'],
			data: self.__PagingSizeData
		}),
		listeners: {
//			change: function(){
//				console.log('change()');
//				self._loadStoreDelayedTask.delay(250);
//			},
			select: function(){
//				console.log('select()');
				self._loadStoreDelayedTask.delay(250);
			}
		}
	});

////	self.__PagingBar = new Ext.PagingToolbar({
//	self.__PagingBar = new Ext.Toolbar({
//		id: self.__PagingBar_id,
//		pageSize: 100,
//		store: self.__GridStore,
//		displayInfo: false,
//		displayMsg: '',
//		emptyMsg: '',
//		hideMode: 'offsets',
//		hideParent: true,
//		items: [self.__PagingSizeComboBox]
//	});

	self.__PagingBar =  new Ext.Toolbar([
		'->',
		{xtype: 'tbtext', text: '<label>0&nbsp;Objects</label>'},
		'-',
		self.__PagingSizeComboBox
	]);

	var _grid_renderer = function(value,metadata,record,rowIndex,colIndex,store){
		var dataIndex = _grid_columns[colIndex].dataIndex;
		var item;
		for(var i=0;i<record.fields.length;i++){
			if(record.fields.keys[i] != dataIndex) continue;
			item = record.fields.items[i];
			break;
		}
		if(item){
			if(item.type == 'date'){
				if(dataIndex == 'entry' && value) value = new Date(value).format(bp3d.defaults.DATE_FORMAT);
				if(dataIndex == 'lastmod' && value) value = new Date(value).format(bp3d.defaults.TIME_FORMAT);
			}
		}
		if(isNoneDataRecord(record)){
			metadata.css += ' ag_point_none_data';
		}
		if(self.__PointId == record.data.f_id) metadata.css += ' ag_point_data';
		return value;
	}

	var _grid_partslist_checkbox_renderer = function(value,metadata,record,rowIndex,colIndex,store){
		var id = self.__GridPanel.getColumnModel().getColumnId(colIndex);
		metadata.css += ' x-grid3-check-col-td';
		if(isNoneDataRecord(record)) metadata.css += ' ag_point_none_data';
		if(self.__PointId == record.data.f_id) metadata.css += ' ag_point_data';
		if(record.data.seg_color) metadata.attr = 'style="background:'+record.data.seg_color+';"'
		if(isAdditionPartsList()){
			return '<div class="x-grid3-check-col'+(value?'-on':'')+' x-grid3-cc-'+id+'">&#160;</div>';
		}else{
			return '<div class="ag_grid_checkbox'+(value?'-on':'')+'-dis x-grid3-cc-'+id+'">&#160;</div>';
		}
	};

	var _grid_checkbox_renderer = function(value,metadata,record,rowIndex,colIndex,store){
		var id = self.__GridPanel.getColumnModel().getColumnId(colIndex);
		metadata.css += ' x-grid3-check-col-td';
		if(isNoneDataRecord(record)){
			metadata.css += ' ag_point_none_data';
		}else{
			if(record.data.partslist){
			}else{
				metadata.css += ' ag_point_none_pallet_data';
			}
		}
		if(self.__PointId == record.data.f_id) metadata.css += ' ag_point_data';
		return '<div class="x-grid3-check-col'+(value?'-on':'')+' x-grid3-cc-'+id+'">&#160;</div>';
	};

	var _grid_color_cell_style = function (value,metadata,record,rowIndex,colIndex,store) {
		if(self.__PointId == record.data.f_id) metadata.css += ' ag_point_data';
		if(isNoneDataRecord(record)){
			metadata.css += ' ag_point_none_data';
			return '';
		}else{
			if(record.data.partslist && value){
				return '<span style="background-color:' + value + '">&nbsp;&nbsp;&nbsp;&nbsp;</span>';
			}else{
				return '';
			}
		}
		return value;
	};

	var _grid_combobox_renderer = function(value,metadata,record,rowIndex,colIndex,store){
		if(isNoneDataRecord(record)){
			metadata.css += ' ag_point_none_data';
			value = "";
		}else{
			if(record.data.partslist){
			}else{
				value = "";
			}
		}
		if(self.__PointId == record.data.f_id) metadata.css += ' ag_point_data';
		return value;
	};

	var _grid_col_opacity_arr = [
		['1.0', '1.0'],
		['0.8', '0.8'],
		['0.6', '0.6'],
		['0.4', '0.4'],
		['0.3', '0.3'],
		['0.2', '0.2'],
		['0.1', '0.1'],
		['0.05', '0.05'],
		['0.0', '0.0']
	];

	var _grid_col_representation_arr = [
		['surface', 'surface'],
		['wireframe', 'wireframe'],
		['points', 'points']
	];

	var _grid_partslist_checkColumn = new Ext.grid.CheckColumn({
		header    : 'Pallet',
		dataIndex : 'partslist',
		width     : 40,
		fixed     : true,
		renderer  : _grid_partslist_checkbox_renderer
	});
	var _grid_zoom_checkColumn = new Ext.grid.CheckColumn({
		header    : "Zoom",
		dataIndex : 'zoom',
		hidden    : true,
		width     : 40,
		resizable : false,
		renderer  : _grid_checkbox_renderer
	});
	var _grid_exclude_checkColumn = new Ext.grid.CheckColumn({
		header    : "Remove",
		dataIndex : 'exclude',
		width     : 50,
		resizable : false,
		renderer  : _grid_checkbox_renderer
	});

	var _grid_col_version = {
		dataIndex:'version',
		header:'Version',
		id:'version',
		sortable: false,
		renderer: _grid_renderer,
		hidden:true
	};
	var _grid_col_rep_id = {
		dataIndex:'b_id',
		header: get_ag_lang('REP_ID'),
		renderer: _grid_renderer,
		sortable: true,
		id:'b_id'
	};
	var _grid_col_cdi_name = {
		dataIndex:'f_id',
		header: get_ag_lang('CDI_NAME'),
		renderer: _grid_renderer,
		sortable: true,
		id:'f_id'
	};

	var _grid_col_color = {
		dataIndex : 'color',
		header    : 'Color',
		id        : 'color',
		width     : 40,
		resizable : false,
		renderer  : _grid_color_cell_style,
/*
		editor    : new Ext.ux.ColorPickerField({
			menuListeners : {
				select: function(e, c){
					this.setValue(c);
					try{var record = self.__GridPanel._edit.record;}catch(e){_dump("color:"+e);}
					if(record){
						record.beginEdit();
						record.set('color',"#"+c);
						record.commit();
						record.endEdit();

						var grid = Ext.getCmp('ag-parts-gridpanel');
						var store = grid.getStore();
						var f_id = record.get('f_id');
						var record = null;
						var regexp = new RegExp('^'+f_id+'$');
						var index = store.find('f_id',regexp);
						if(index<0) index = store.find('conv_id',regexp);
						if(index>=0) record = store.getAt(index);
						if(record){
							record.set('color',"#"+c);
							record.commit();
						}
					}
				},
				show : function(){ // retain focus styling
					this.onFocus();
				},
				hide : function(){
					this.focus.defer(10, this);
				},
				beforeshow : function(menu) {
					try {
						if (this.value != "") {
							menu.palette.select(this.value);
						} else {
							this.setValue("");
							var el = menu.palette.el;
							if(menu.palette.value){
								try{el.child("a.color-"+menu.palette.value).removeClass("x-color-palette-sel");}catch(e){}
								menu.palette.value = null;
							}
						}
					}catch(ex){}
				}
			}
		})
*/
		editor    : new Ext.ux.ColorField({
			listeners: {
				select: function(e, c){
					try{var record = self.__GridPanel._edit.record;}catch(e){_dump("color:"+e);}
					if(record){
						record.beginEdit();
						record.set('color',"#"+c);
						record.commit();
						record.endEdit();

						var grid = Ext.getCmp('ag-parts-gridpanel');
						var store = grid.getStore();
						var f_id = record.get('f_id');
						var record = null;
						var regexp = new RegExp("^"+f_id+"\$");
						var index = store.find('f_id',regexp);
						if(index<0) index = store.find('conv_id',regexp);
						if(index>=0) record = store.getAt(index);
						if(record){
							record.set('color',"#"+c);
							record.commit();
						}

					}
				}
			}
		})
	};

	var _grid_col_opacity = {
		dataIndex : 'opacity',
		header    : 'Opacity',
		id        : 'opacity',
		width     : 50,
		resizable : false,
		align     : 'right',
		renderer: _grid_combobox_renderer,
		editor    : new Ext.form.ComboBox({
			typeAhead     : true,
			triggerAction : 'all',
			store         : _grid_col_opacity_arr,
			lazyRender    : true,
			listClass     : 'x-combo-list-small',
			listeners     : {
				'select' : function(combo,record,index){
					try{var record = self.__GridPanel._edit.record;}catch(e){_dump("opacity:"+e);}
					if(record){
						record.beginEdit();
						record.set('opacity',combo.getValue());
						record.commit();
						record.endEdit();

						var store = Ext.getCmp('ag-parts-gridpanel').getStore();
						var f_id = record.get('f_id');
						var record = null;
						var regexp = new RegExp("^"+f_id+"$");
						var index = store.find('f_id',regexp);
						if(index<0) index = store.find('conv_id',regexp);
						if(index>=0) record = store.getAt(index);
						if(record){
							record.set('opacity',combo.getValue());
							record.commit();
						}
					}
				},
				scope : this
			}
		})
	};

	var _grid_col_representation = {
		dataIndex : 'representation',
		header    : get_ag_lang('ANATOMO_REP_LABEL'),
		id        : 'representation',
		width     : 40,
		resizable : false,
		renderer  : _grid_combobox_renderer,
		hidden    : true,
		hideable  : true,
		sortable  : true,
		editor    : new Ext.form.ComboBox({
			typeAhead     : true,
			triggerAction : 'all',
			store         : _grid_col_representation_arr,
			lazyRender    : true,
			listClass     : 'x-combo-list-small',
			listeners     : {
				'select' : function(combo,record,index){
					try{var record = self.__GridPanel._edit.record;}catch(e){_dump("representation:"+e);}
					if(record){
						record.beginEdit();
						record.set('representation',combo.getValue());
						record.commit();
						record.endEdit();

						var store = Ext.getCmp('ag-parts-gridpanel').getStore();
						var f_id = record.get('f_id');
						var record = null;
						var regexp = new RegExp("^"+f_id+"$");
						var index = store.find('f_id',regexp);
						if(index<0) index = store.find('conv_id',regexp);
						if(index>=0) record = store.getAt(index);
						if(record){
							record.set('representation',combo.getValue());
							record.commit();
						}
					}
				},scope : this
			}
		})
	};

	var _grid_col_value = {
		dataIndex : 'value',
		header    : 'Value',
		id        : 'value',
		width     : 40,
		resizable : false,
		renderer  : _grid_renderer,
		hidden    : true,
		editor    : new Ext.form.TextField({
			allowBlank : true
		})
	};

	var _grid_columns = [
		_grid_partslist_checkColumn,
		{dataIndex:'name_e', header: get_ag_lang('DETAIL_TITLE_NAME_E'),                    renderer: _grid_renderer, id:'name_e'},
		_grid_col_color,
		_grid_col_opacity,
		_grid_exclude_checkColumn,
		_grid_col_value,
		_grid_col_representation,
		_grid_col_rep_id,
		_grid_col_cdi_name,
		{dataIndex:'xmin',  header:'Xmin(mm)',                        renderer: _grid_renderer, id:'xmin',     hidden:true},
		{dataIndex:'xmax',  header:'Xmax(mm)',                        renderer: _grid_renderer, id:'xmax',     hidden:true},
		{dataIndex:'ymin',  header:'Ymin(mm)',                        renderer: _grid_renderer, id:'ymin',     hidden:true},
		{dataIndex:'ymax',  header:'Ymax(mm)',                        renderer: _grid_renderer, id:'ymax',     hidden:true},
		{dataIndex:'zmin',  header:'Zmin(mm)',                        renderer: _grid_renderer, id:'zmin',     hidden:true},
		{dataIndex:'zmax',  header:'Zmax(mm)',                        renderer: _grid_renderer, id:'zmax',     hidden:true},
		{dataIndex:'volume',header: get_ag_lang('GRID_TITLE_VOLUME')+'(cm3)', renderer: _grid_renderer, id:'volume',   hidden:true},
		anatomography_point_grid_col_version,
		anatomography_point_grid_col_entry
	];


	self.__GridPanel = new Ext.grid.EditorGridPanel({
		id: self.__GridPanel_id,
		header: false,
		region: 'center',
		border: false,
		stripeRows: true,
		columnLines: true,
		maskDisabled: true,
		plugins: [
			_grid_partslist_checkColumn,
			_grid_zoom_checkColumn,
			_grid_exclude_checkColumn
		],
		clicksToEdit: 1,
		trackMouseOver: true,
		selModel: new Ext.grid.RowSelectionModel({singleSelect:true}),
		store: self.__GridStore,
		columns: _grid_columns,
		enableColLock: false,
		loadMask: true,
		viewConfig: {
			deferEmptyText: false,
//			emptyText: '<div class="bp3d-pallet-empty-message">'+get_ag_lang('CLICK_IMAGE_GRID_EMPTY_MESSAGE')+'</div>'
			emptyText: '&nbsp;'
		},

		listeners : {
			beforeedit: function(e){
				if(e.field == 'partslist'){
					e.cancel = (isNoneDataRecord(e.record)||(!isAdditionPartsList())?true:false);
				}else{
					e.cancel = !e.record.get('partslist');
				}
				if(!e.cancel) e.grid._edit = e;
			},
			afteredit: function(e){
				e.record.commit();

//				console.log('afteredit()');
				self._unBind();
				if(e.field == 'partslist'){
					if(e.value){
						self.__palletGridStore.add(e.record.copy());
					}else{
						var record = null;
						var index = self.__palletGridStore.find('f_id',new RegExp("^"+e.record.get('f_id')+"$"));
						if(index>=0) record = self.__palletGridStore.getAt(index);
						if(record) self.__palletGridStore.remove(record);
					}
				}else{
					var record = null;
					var regexp = new RegExp("^"+e.record.get('f_id')+"$");
					var index = self.__palletGridStore.find('f_id',regexp);
					if(index<0) index = self.__palletGridStore.find('conv_id',regexp);
					if(index>=0) record = self.__palletGridStore.getAt(index);
					if(record){
						record.set(e.field,e.record.get(e.field));
						record.commit();
					}
				}
				self._onBind();
			},
			complete: function(comp,row,col){
				comp.view.focusRow(row);
			},
			resize: function(grid){
				resizeGridPanelColumns(grid);
			},
			render: function(grid){
				restoreHiddenGridPanelColumns(grid);
			},
			scope : this
		}
	});
	self.__GridPanel.getColumnModel().on({
		'hiddenchange' : function(column,columnIndex,hidden){
			var editorgrid = self.__GridPanel;
			resizeGridPanelColumns(editorgrid);
			saveHiddenGridPanelColumns(editorgrid);
		},
		scope: this,
		delay: 100
	});

	self.__Panel = new Ext.Panel({
		id: self.__Panel_id,
		title: 'Element',
		layout: 'border',
//		border: true,
//		bodyStyle: 'border:0 0 1px 0;',

		items: [self.__GridPanel],

//		bbar: [{xtype: 'tbfill'},self.__PagingSizeComboBox],
		tbar : self.__PagingBar,

		listeners: {
			render: {
				fn: function(comp){
//					$(comp.body.dom).css({border:'0 0 1px 0'});
					self.__palletGridPanel = Ext.getCmp(self.__palletGridPanel_id);
					if(self.__parentTabPanel){
						if(self.__palletGridPanel.rendered){
							self._initBind();
						}else{
							self.__palletGridPanel.on({
								render: function(){
									self._initBind();
								},
								buffer: 100,
								single: true
							});
						}
					}else{
						self.__initTask = {
							run: function(){
								self.__palletGridPanel = Ext.getCmp(self.__palletGridPanel_id);
								if(!self.__palletGridPanel) return;
								self.__initTaskRunner.stop(self.__initTask);
								if(self.__palletGridPanel.rendered){
									self._initBind();
								}else{
									self.__palletGridPanel.on({
										render: function(){
											self._initBind();
										},
										buffer: 100,
										single: true
									});
								}
							},
							interval: 1000
						}
						if(!self.__initTaskRunner) self.__initTaskRunner = new Ext.util.TaskRunner();
						self.__initTaskRunner.start(self.__initTask);
					}
				},
				buffer: 100,
				single: true
			}
		}
	});
	self.__parentTabPanel.insert(++insert_index,self.__Panel);
};
///////////////////////////////////////////////////////////////////////////////
//イベント処理初期化
///////////////////////////////////////////////////////////////////////////////
ag_extensions.pallet_element._bindPalletStore = function(){
	var self = this;
//	console.log('ag_extensions.pallet_element._bindPalletStore()');
	self._loadStoreDelayedTask.delay(250);
};
ag_extensions.pallet_element._updatePalletStore = function(store,record,operation){
	var self = this;
//	console.log('ag_extensions.pallet_element._updatePalletStore():'+operation);
	if(operation!=Ext.data.Record.COMMIT) return;


	var update_record;
	var regexp = new RegExp("^"+record.get('f_id')+"$");
	var index = self.__GridStore.find('f_id',regexp);
	if(index<0) index = self.__GridStore.find('conv_id',regexp);
	if(index>=0) update_record = self.__GridStore.getAt(index);
//	console.log('ag_extensions.pallet_element._updatePalletStore():'+index);
	if(update_record){
		var updateNum = 0;
		var updateFieldNames = ['color','value','zoom','exclude','opacity','representation','point'];
		Ext.each(updateFieldNames,function(fieldName){
			if(update_record.get(fieldName)==record.get(fieldName)) return true;
			update_record.set(fieldName,record.get(fieldName));
			updateNum++;
		});
		if(updateNum) update_record.commit();
	}

//	self._loadStoreDelayedTask.delay(250);
};
ag_extensions.pallet_element._onBind = function(){
	var self = this;
//	console.log('ag_extensions.pallet_element._onBind()');
	self.__palletGridStore.on('add',self._bindPalletStore,self);
	self.__palletGridStore.on('clear',self._bindPalletStore,self);
	self.__palletGridStore.on('remove',self._bindPalletStore,self);
	self.__palletGridStore.on('update',self._bindPalletStore,self);
};
ag_extensions.pallet_element._unBind = function(){
	var self = this;
//	console.log('ag_extensions.pallet_element._unBind()');
	self.__palletGridStore.un('add',self._bindPalletStore,self);
	self.__palletGridStore.un('clear',self._bindPalletStore,self);
	self.__palletGridStore.un('remove',self._bindPalletStore,self);
	self.__palletGridStore.un('update',self._bindPalletStore,self);
};
ag_extensions.pallet_element._initBind = function(){
	var self = this;
//	console.log('ag_extensions.pallet_element._initBind()');
	self.__palletGridStore = self.__palletGridPanel.getStore();
	self._onBind();
	self.__palletGridStore.on('update',self._updatePalletStore,self,{buffer:250});
	self._bindPalletStore();
};
ag_extensions.pallet_element._loadStore = function(){
	var self = this;
//	console.log('ag_extensions.pallet_element._loadStore()');
	var datas = [];
	var store = self.__palletGridStore;
	if(store){
		Ext.each(store.getRange(),function(record){
			if(record.get('exclude') || record.get('opacity')<1) return true;
			datas.push({
				b_id: record.get('b_id'),
				f_id: record.get('f_id'),
				cb_id: record.get('cb_id'),
				ci_id: record.get('ci_id'),
				md_id: record.get('md_id'),
				mr_id: record.get('mr_id'),
				mv_id: record.get('mv_id'),
				bul_id: record.get('bul_id')
			});
		});
	}
	if(datas.length){
		datas = datas.sort(function(a,b){return a.f_id-b.f_id;});
	}
//	console.log(Ext.util.JSON.encode(datas));
//	console.log(datas);
//	console.log('ag_extensions.pallet_element._loadStore():'+datas.length);
	if(datas.length==0){
		self._clearStore();
		return;
	}
	var storeLastOptionsParams = self._getStoreLastOptionsParams();
	var params = {
		datas: Ext.util.JSON.encode(datas),
		limit: self.__PagingSizeComboBox.getValue()
	};
	if(storeLastOptionsParams.datas != params.datas || storeLastOptionsParams.limit != params.limit){
		self.__GridStore.load({
			params: params
		});
	}else{
		self._updateRecordsStatus(self.__GridStore.getRange());
	}
};
ag_extensions.pallet_element._initStoreLastOptionsParams = function(){
	var self = this;
	var params = {
		datas: Ext.util.JSON.encode([]),
		limit: Cookies.get(self.__COOKIE_LIMIT_KEY) || self.__MIN_PAGE_SIZE
	};
	return params;
}
ag_extensions.pallet_element._clearStore = function(clearParams){
	var self = this;
	if(Ext.isEmpty(clearParams)) clearParams = true;
	self.__GridStore.removeAll();
	if(clearParams && self.__GridStore.lastOptions){
		self.__GridStore.lastOptions.params = self._initStoreLastOptionsParams();
	}
	if(clearParams && self.__GridStore.reader){
		delete self.__GridStore.reader.jsonData;
	}
};
ag_extensions.pallet_element._getStoreLastOptionsParams = function(){
	var self = this;
	var params = self._initStoreLastOptionsParams();
	if(self.__GridStore.lastOptions && self.__GridStore.lastOptions.params) params = self.__GridStore.lastOptions.params;
	return params;
};
ag_extensions.pallet_element._updateRecordsStatus = function(records){
	var self = this;
	var prm_record = ag_param_store.getAt(0);
	var bp3d_parts_store = self.__palletGridStore;
	for(var i=0;i<records.length;i++){
		var partslist = false;
		var zoom = false;
		var exclude = false;
		var color = null;
		var opacity = "1.0";
		var representation = "surface";
		var value = "";
		var point = false;
		var elem_type = records[i].get('elem_type');
		var regexp = new RegExp("^"+records[i].get('f_id')+"$");
		var index = bp3d_parts_store.find('f_id',regexp);
		if(index<0) index = bp3d_parts_store.find('conv_id',regexp);
//					console.log('ag_extensions.pallet_element.__Store.load():'+records[i].get('f_id')+':'+index);
		if(index>=0){
			partslist = true;
			var record = bp3d_parts_store.getAt(index);
			exclude = record.get('exclude');
			color = record.get('color');
			opacity = record.get('opacity');
			representation = record.get('representation');
			value = record.get('value');
			point = record.get('point');
		}else{
			if(!Ext.isEmpty(records[i].get('def_color'))) color = records[i].get('def_color');
		}
		records[i].beginEdit();
		records[i].set('partslist',partslist);
		records[i].set('zoom',zoom);
		records[i].set('exclude',exclude);
		records[i].set('color',color?color:'#'+ (elem_type=='bp3d_point'? prm_record.data.point_color_rgb:prm_record.data.color_rgb));
		records[i].set('opacity',opacity);
		records[i].set('representation',representation);
		records[i].set('value',value);
		records[i].set('conv_id',records[i].get('f_id'));
		records[i].set('point',point);
		records[i].commit(true);
		records[i].endEdit();
	}
	self.__GridPanel.getView().refresh();
	if(records.length){
		self.selectPointElement(self.__PointId ? self.__PointId : null);
	}
};

///////////////////////////////////////////////////////////////////////////////
//
///////////////////////////////////////////////////////////////////////////////
ag_extensions.pallet_element.getId = function(){
	var self = this;
//	console.log('ag_extensions.pallet_element.getId()');
	return self.__Panel_id;
};
///////////////////////////////////////////////////////////////////////////////
//
///////////////////////////////////////////////////////////////////////////////
ag_extensions.pallet_element.selectPointElement = function(pointId){
	var self = this;
//	console.log('ag_extensions.pallet_element.selectPointElement():'+pointId);
	var idx = -1;
	if(pointId){
		self.__PointId = pointId;
		idx = self.__GridStore.findBy(function(record,id){
			if(record.get('f_id')==self.__PointId){
				return true;
			}else{
				return false;
			}
		});
	}
	var view = self.__GridPanel.getView();
	if(idx<0 && view.hasRows()){
		delete self.__PointId;
	}
	view.refresh();
	if(idx<0) idx = 0;
//	console.log('ag_extensions.pallet_element.selectPointElement():'+view.hasRows());
//	console.log('ag_extensions.pallet_element.selectPointElement():'+idx);
	if(view.hasRows()){
		if(!self.__contentsTabPanel) self.__contentsTabPanel = Ext.getCmp(self.__contentsTabPanel_id);
		if(self.__contentsTabPanel.getActiveTab().id == self.__contentsAnatomographyPanel_id){
			view.focusRow(idx);
		}else{
			self.__contentsTabPanel.on({
				tabchange: function(tabPanel,tab){
					view.focusRow(idx);
//					console.log('ag_extensions.pallet_element.selectPointElement():'+idx);
				},
				single: true
			});
		}
	}
};
///////////////////////////////////////////////////////////////////////////////
//
///////////////////////////////////////////////////////////////////////////////
ag_extensions.pallet_element.setActiveTab = function(){
	var self = this;
//	console.log('ag_extensions.pallet_element.setActiveTab()');
	self.__parentTabPanel.setActiveTab(self.__Panel);
};
ag_extensions.pallet_element.showLoadMask = function(){
	var self = this;
//	console.log('ag_extensions.pallet_element.showLoadMask()');
	try{
		self.__Panel.loadMask.show();
	}catch(e){
	}
};
ag_extensions.pallet_element.hideLoadMask = function(){
	var self = this;
//	console.log('ag_extensions.pallet_element.hideLoadMask()');
	try{
		self.__Panel.loadMask.hide();
	}catch(e){
	}
};
///////////////////////////////////////////////////////////////////////////////
//初期化処理コール
///////////////////////////////////////////////////////////////////////////////
Ext.onReady(function(){
	ag_extensions.pallet_element._init();
});
