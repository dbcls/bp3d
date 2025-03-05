Ext.define('Ag.Component.Canvas.Pin', {
	override: 'Ag.Main',

	getCanvasPinPanel : function(){
		var self = this;
		var canvas_top_panel = self._getCanvasPanel();
		return canvas_top_panel.down('panel#canvas-pin-panel');
	},

	getCanvasPinGridPanel : function(){
		var self = this;
		var canvas_top_panel = self._getCanvasPanel();
		return canvas_top_panel.down('gridpanel#canvas-pin-gridpanel');
	},

	_createCanvasPinPanel : function(config){
		var self = this;

		config = config || {};
		var itemId = config.itemId || 'canvas-pin-panel';
		delete config.itemId;

		var depth_datas = [];
		for(var i=1;i<=16;i++){
			depth_datas.push([i]);
		}
		return Ext.create('Ext.panel.Panel', Ext.apply({
			title: 'Pin',
			itemId: itemId,
			layout: 'fit',
			dockedItems: [{
				xtype: 'toolbar',
				dock: 'top',
				itemId: 'top',
				items: [{
					hidden: true,
					xtype: 'combobox',
					itemId: 'depth',
					fieldLabel: 'Depth',
					labelWidth: 40,
					width: 96,
					editable: false,
					listConfig: {
						minWidth: 51
					},
					queryMode: 'local',
					displayField: 'value',
					valueField: 'value',
					value: depth_datas[0][0],
					store: Ext.create('Ext.data.ArrayStore', {
						fields: [{name: 'value', type: 'int'}],
						data : depth_datas
					})
				},{
					hidden: false,
					xtype: 'numberfield',
					itemId: 'depth',
					fieldLabel: 'Depth',
					labelWidth: 40,
					width: 96,
					value: 1,
					minValue: 1,
					maxValue: 16,
					allowBlank: false,
					allowDecimals: false,
					allowExponential: false,
					allowOnlyWhitespace: false,
					listeners: {
						validitychange: function( file, isValid, eOpts ){
							if(isValid) return;
							file.setValue(1);
						}
					}
				},'-',{
					disabled: true,
					itemId: 'pin_up',
					iconCls: 'pin_up',
					tooltip: 'Up'
				},{
					disabled: true,
					itemId: 'pin_down',
					iconCls: 'pin_down',
					tooltip: 'Down'
				},'-',{
					disabled: true,
					itemId: 'delete',
					iconCls: 'pallet_delete',
					tooltip: 'Delete',
					listeners: {
						afterrender: function( b, eOpts ){
							var canvas_pin_gridpanel = self.getCanvasPinGridPanel();
							canvas_pin_gridpanel.on('selectionchange',function(selmodel, selected, eOpts){
								b.setDisabled(Ext.isEmpty(selected));
							});
						},
						click: function(b){
							var canvas_pin_gridpanel = self.getCanvasPinGridPanel();
							var canvas_pin_selmodel = canvas_pin_gridpanel.getSelectionModel();
							var records = canvas_pin_selmodel.getSelection();
							if(Ext.isEmpty(records)) return;
							self.removeRecords(canvas_pin_gridpanel.getView(),records);
							self._reAddCanvasPinDataFromStore();
						}
					}
				},'-',{
					disabled: true,
					itemId: 'delete_all',
					iconCls: 'pallet_delete',
					tooltip: 'Delete ALL',
					text: 'ALL',
					listeners: {
						afterrender: function( b, eOpts ){
							var canvas_pin_gridpanel = self.getCanvasPinGridPanel();
							var canvas_pin_store = canvas_pin_gridpanel.getStore();
							var func = function(){
								b.setDisabled(canvas_pin_store.getCount()===0);
							};
							canvas_pin_store.on('add',func);
							canvas_pin_store.on('bulkremove',func);
							canvas_pin_store.on('clear',func);
						},
						click: function(b){
							var canvas_pin_gridpanel = self.getCanvasPinGridPanel();
							var canvas_pin_store = canvas_pin_gridpanel.getStore();
							canvas_pin_store.removeAll();
							var renderer = self.getCanvasRenderer();
							renderer.removeAllPin();
							renderer.render();
						}
					}
				},'-']
			},{
				xtype: 'toolbar',
				dock: 'bottom',
				itemId: 'bottom',
				items: [{
					xtype: 'checkboxfield',
					itemId: 'number',
					boxLabel: 'Number',
					checked: true,
					listeners: {
						change: function( field, newValue, oldValue, eOpts ){
							self._reAddCanvasPinDataFromStore();
						}
					}
				},{
					xtype: 'checkboxfield',
					itemId: 'description',
					boxLabel: 'Description',
					checked: true,
					listeners: {
						afterrender: function( field, eOpts ){
							if(field.getValue()) return;
							field.next('combobox#line').setDisabled(true);
						},
						change: function( field, newValue, oldValue, eOpts ){
							field.next('combobox#line').setDisabled(oldValue);
							self._reAddCanvasPinDataFromStore();
						}
					}
				},{
					xtype: 'combobox',
					itemId: 'line',
					fieldLabel: 'Line',
					labelWidth: 30,
					width: 103,
					editable: false,
					queryMode: 'local',
					displayField: 'display',
					valueField: 'value',
					value: 0,
					store: Ext.create('Ext.data.ArrayStore', {
						fields: [
							{name: 'value',   type: 'int'},
							{name: 'display', type: 'string'}
						],
						data: [
							[0,'None'],
							[1,'Tip'],
							[2,'End']
						]
					}),
					listeners: {
						change: function( field, newValue, oldValue, eOpts ){
							self._reAddCanvasPinDataFromStore();
						}
					}
				},{
					xtype: 'combobox',
					itemId: 'shape',
					fieldLabel: 'Shape',
					labelWidth: 40,
					width: 120,
					editable: false,
					queryMode: 'local',
					displayField: 'display',
					valueField: 'value',
					value: 'PL',
					store: Ext.create('Ext.data.ArrayStore', {
						fields: [
							{name: 'display', type: 'string'},
							{name: 'value',   type: 'string'},
							{name: 'shape',   type: 'string'},
							{name: 'size',    type: 'float'}
						],
						data: [
							['Circle', 'SC',  'CIRCLE',    25.0],
							['Corn',   'CC',  'CONE',      25.0],
							['Pin L',  'PL',  'PIN_LONG', 112.5],
							['Pin M',  'PM',  'PIN_LONG',  75.0],
							['Pin S',  'PS',  'PIN_LONG',  37.5],
							['Pin SS', 'PSS', 'PIN_LONG',  20.0]
						]
					}),
					listeners: {
						change: function( field, newValue, oldValue, eOpts ){
							self._reAddCanvasPinDataFromStore();
						}
					}
				}]
			}],
			items: [{
				xtype: 'gridpanel',

				itemId: 'canvas-pin-gridpanel',

				store: Ext.data.StoreManager.lookup('canvas-pin-store'),

	//			viewConfig: self.getDropViewConfig(),
				viewConfig: Ext.apply(self.getDropViewConfig(),{
					listeners: {
						colorchange: function(record,value){
							var view = this;
							self._reAddCanvasPinDataFromStore();
						},
						descriptionchange: function(record,value){
							var view = this;
							self._reAddCanvasPinDataFromStore();
						}
					}
				}),
				columnLines: true,
				selModel: {
					mode: 'SIMPLE'
				},

				columns: [
					{ text: Ag.Def.PIN_NO_FIELD_ID,  dataIndex: Ag.Def.PIN_NO_FIELD_ID, width: 40 },
					{ text: Ag.Def.PIN_PART_ID_FIELD_ID,  dataIndex: Ag.Def.PIN_PART_ID_FIELD_ID, width: 80 },
					{ text: Ag.Def.PIN_PART_NAME_FIELD_ID,  dataIndex: Ag.Def.PIN_PART_NAME_FIELD_ID, flex: 1 },
					{
						text: self.DEF_COLOR_LABEL,
						dataIndex: Ag.Def.PIN_COLOR_FIELD_ID,
						width: self.DEF_COLOR_COLUMN_WIDTH + 22,
						minWidth: self.DEF_COLOR_COLUMN_WIDTH + 22,
						hidden: false,
						hideable: true,
						xtype: 'agcolorcolumn'
					},
					{
						text: Ag.Def.PIN_DESCRIPTION_FIELD_ID,
						dataIndex: Ag.Def.PIN_DESCRIPTION_FIELD_ID,
						flex: 1,
						editor: {
							xtype: 'textfield'
						}
					},
				],

				plugins: [
					Ext.create('Ext.grid.plugin.CellEditing', {
						clicksToEdit: 1,
						listeners: {
							beforeedit: function(editor,e,eOpts){
							},
							edit: function(editor,e,eOpts){
								console.log(e);
								e.record.commit();
								if(e.field === Ag.Def.PIN_DESCRIPTION_FIELD_ID){
									e.view.fireEvent('descriptionchange', e.record, e.value);
								}
							}
						}
					}),
					self.getBufferedRenderer({pluginId: 'canvas-pin-gridpanel-plugin'})
				],


				listeners: {
					afterrender: function( panel, eOpts ){
	//					var store = panel.getStore();
	//					store.view = panel.getView();
						self.bindDrop(panel);
						self.bindCellclick(panel);
					},
					selectionchange: function( selModel, selected, eOpts ){
	//					self.getCanvasRenderer().setObjProperties(self.getCanvasObjData());
					}
				}
			}]

		},config||{}));
	},

	_addCanvasPinDataFromPick : function(renderer, intersects){
		var self = this;
		intersects = intersects || [];
		var panel = self.getCanvasPinPanel();
		var depth = panel.down('numberfield#depth').getValue();

		var number_flag = panel.down('checkboxfield#number').getValue();
		var description_flag = panel.down('checkboxfield#description').getValue();

		var line_combobox = panel.down('combobox#line');
		var line = line_combobox.getValue();

		var shape_combobox = panel.down('combobox#shape');
		var shape_record = shape_combobox.findRecordByValue(shape_combobox.getValue());
		var shape = shape_record.get('shape');
		var size = shape_record.get('size');

		var canvas_pin_store = Ext.data.StoreManager.lookup('canvas-pin-store');
		var canvas_pallet_store = Ext.data.StoreManager.lookup('canvas-pallet-store');

//		console.log(depth);

		var pinDatas = [];
//		var pinMeshs = [];

		var no = canvas_pin_store.max(Ag.Def.PIN_NO_FIELD_ID) || 0;

		for(var i=0;i<intersects.length && i<depth;i++){
			var intersect = intersects[i];
//			console.log(i+1,intersect.face.normal, intersect.point, intersect.object);

			var mesh = intersect.object;

			var canvas_pallet_idx = canvas_pallet_store.find( Ag.Def.OBJ_ID_DATA_FIELD_ID, mesh[Ag.Def.OBJ_ID_DATA_FIELD_ID], 0, false, false, true );
			if(canvas_pallet_idx<0) continue;

			var canvas_pallet_record = canvas_pallet_store.getAt(canvas_pallet_idx);

			no++;

			var data = {};
			data[Ag.Def.PIN_NO_FIELD_ID] = no;

			data[Ag.Def.PIN_COORDINATE_X_FIELD_ID] = intersect.point.x;
			data[Ag.Def.PIN_COORDINATE_Y_FIELD_ID] = intersect.point.y;
			data[Ag.Def.PIN_COORDINATE_Z_FIELD_ID] = intersect.point.z;

			data[Ag.Def.PIN_VECTOR_X_FIELD_ID] = intersect.face.normal.x;
			data[Ag.Def.PIN_VECTOR_Y_FIELD_ID] = intersect.face.normal.y;
			data[Ag.Def.PIN_VECTOR_Z_FIELD_ID] = intersect.face.normal.z;

			data[Ag.Def.PIN_DESCRIPTION_DRAW_FLAG_FIELD_ID] = description_flag;

			data[Ag.Def.PIN_SHAPE_FIELD_ID] = shape;
			data[Ag.Def.PIN_SIZE_FIELD_ID] = size;

			data[Ag.Def.PIN_PART_ID_FIELD_ID] = canvas_pallet_record.get(Ag.Def.ID_DATA_FIELD_ID);
			data[Ag.Def.PIN_PART_NAME_FIELD_ID] = canvas_pallet_record.get(Ag.Def.NAME_DATA_FIELD_ID);

			var record = canvas_pin_store.createModel(data);
			data = record.getData();

			var pinMesh = renderer.createPin(intersect.face.normal, intersect.point, {
				shape: shape,
				size: size,
				line: description_flag ? line : null,
				color: data[Ag.Def.PIN_COLOR_FIELD_ID],
				text: number_flag ? data[Ag.Def.PIN_NO_FIELD_ID] : null,
				description: description_flag ? Ext.String.format('{0}&nbsp;:&nbsp;{1}&nbsp;:&nbsp;{2}', data[Ag.Def.PIN_NO_FIELD_ID], data[Ag.Def.PIN_PART_NAME_FIELD_ID], data[Ag.Def.PIN_DESCRIPTION_FIELD_ID] ? data[Ag.Def.PIN_DESCRIPTION_FIELD_ID] : '') : null
			});
//			console.log(pinMesh);
//			pinMeshs.push(pinMesh);

			data[Ag.Def.PIN_ID_FIELD_ID] = pinMesh.uuid;


			pinDatas.push(data);
		}

		var gridpanel = self.getCanvasPinGridPanel();
		if(gridpanel.rendered){
				self.addRecords(gridpanel.getView(),pinDatas);
		}else{
			canvas_pin_store.add(pinDatas);
		}

		renderer.render();
	},

	_reAddCanvasPinDataFromStore : function(){
		var self = this;

		var renderer = self.getCanvasRenderer();
		renderer.removeAllPin();

		var panel = self.getCanvasPinPanel();

		var number_flag = panel.down('checkboxfield#number').getValue();
		var description_flag = panel.down('checkboxfield#description').getValue();

		var line_combobox = panel.down('combobox#line');
		var line = line_combobox.getValue();

		var shape_combobox = panel.down('combobox#shape');
		var shape_record = shape_combobox.findRecordByValue(shape_combobox.getValue());
		var shape = shape_record.get('shape');
		var size = shape_record.get('size');

		var canvas_pin_store = Ext.data.StoreManager.lookup('canvas-pin-store');
		canvas_pin_store.suspendEvents( true );
		try{
			canvas_pin_store.each(function(record,idx){
				var no = idx+1;
				if(
					record.get(Ag.Def.PIN_NO_FIELD_ID) !== no ||
					record.get(Ag.Def.PIN_DESCRIPTION_DRAW_FLAG_FIELD_ID) !== description_flag ||
					record.get(Ag.Def.PIN_SHAPE_FIELD_ID) !== shape ||
					record.get(Ag.Def.PIN_SIZE_FIELD_ID) !== size
				){
					record.beginEdit();
					record.set(Ag.Def.PIN_NO_FIELD_ID, no);
					record.set(Ag.Def.PIN_DESCRIPTION_DRAW_FLAG_FIELD_ID, description_flag);
					record.set(Ag.Def.PIN_SHAPE_FIELD_ID, shape);
					record.set(Ag.Def.PIN_SIZE_FIELD_ID, size);
					record.commit(false,[Ag.Def.PIN_NO_FIELD_ID,Ag.Def.PIN_DESCRIPTION_DRAW_FLAG_FIELD_ID,Ag.Def.PIN_SHAPE_FIELD_ID,Ag.Def.PIN_SIZE_FIELD_ID]);
					record.endEdit(false,[Ag.Def.PIN_NO_FIELD_ID,Ag.Def.PIN_DESCRIPTION_DRAW_FLAG_FIELD_ID,Ag.Def.PIN_SHAPE_FIELD_ID,Ag.Def.PIN_SIZE_FIELD_ID]);
				}
				var data = record.getData();
				var dir = new THREE.Vector3(data[Ag.Def.PIN_VECTOR_X_FIELD_ID],data[Ag.Def.PIN_VECTOR_Y_FIELD_ID],data[Ag.Def.PIN_VECTOR_Z_FIELD_ID]);
				var origin = new THREE.Vector3(data[Ag.Def.PIN_COORDINATE_X_FIELD_ID],data[Ag.Def.PIN_COORDINATE_Y_FIELD_ID],data[Ag.Def.PIN_COORDINATE_Z_FIELD_ID]);

				var pinMesh = renderer.createPin(dir, origin, {
					shape: shape,
					size: size,
					line: description_flag ? line : null,
					color: data[Ag.Def.PIN_COLOR_FIELD_ID],
					text: number_flag ? data[Ag.Def.PIN_NO_FIELD_ID] : null,
					description: description_flag ? Ext.String.format('{0}&nbsp;:&nbsp;{1}&nbsp;:&nbsp;{2}', data[Ag.Def.PIN_NO_FIELD_ID], data[Ag.Def.PIN_PART_NAME_FIELD_ID], data[Ag.Def.PIN_DESCRIPTION_FIELD_ID] ? data[Ag.Def.PIN_DESCRIPTION_FIELD_ID] : '') : null
				});

			});
		}catch(e){
			console.error(e);
		}
		canvas_pin_store.resumeEvents();

		renderer.render();
	}

});
