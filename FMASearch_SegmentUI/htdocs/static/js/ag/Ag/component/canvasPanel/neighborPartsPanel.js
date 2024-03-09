Ext.define('Ag.Component.Canvas.NeighborParts', {
	override: 'Ag.Main',

	_createCanvasNeighborPartsPanel : function(config){
		var self = this;

		var canvas_pallet_store = Ext.data.StoreManager.lookup('canvas-pallet-store');
		var canvas_neighbor_parts_store = Ext.data.StoreManager.lookup('canvas-neighbor-parts-store');

		var canvas_neighbor_parts_store_task = new Ext.util.DelayedTask(function(){

			canvas_neighbor_parts_store.suspendEvents(false);
			try{
				canvas_neighbor_parts_store.each(function(record){
					var canvas_pallet_record = canvas_pallet_store.findRecord(Ag.Def.OBJ_ID_DATA_FIELD_ID, record.get(Ag.Def.OBJ_ID_DATA_FIELD_ID), 0, false, false, true);

					if(Ext.isEmpty(canvas_pallet_record)){
						if(!record.get(Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID)) return;

						record.beginEdit();
						record.set(Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID, false);
						record.commit(false,[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID]);
						record.endEdit(false,[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID]);
					}
					else{
//						if(record.get(Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID)) return;

						record.beginEdit();
						var data = canvas_pallet_record.getData();
						var keys = Ext.Object.getKeys(data);
						Ext.Array.each(keys, function(key){
							record.set(key, data[key]);
						});
						record.set(Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID, true);
						record.commit(false,keys);
						record.endEdit(false,keys);
					}
				});
			}catch(e){
				console.error(e);
			}
			canvas_neighbor_parts_store.resumeEvents();

			var canvasPanel = self._getCanvasPanel();
			var canvas_neighbor_parts_gridpanel = canvasPanel.down('gridpanel#canvas-neighbor-parts-gridpanel');
			canvas_neighbor_parts_gridpanel.getView().refresh();

		});

		canvas_neighbor_parts_store.on({
			load: function(store,records,successful,eOpts){
				console.log(store.storeId, 'load',successful);
				if(!successful) return;
				store.sort();
				canvas_neighbor_parts_store_task.delay(0);
			},
			update: function(store,record,operation){
				console.log(store.storeId, 'update', operation);
				if(operation!==Ext.data.Model.COMMIT) return;

				Ext.defer(function(){
					canvas_pallet_store.suspendEvents(false);
					try{
						var canvas_pallet_record = canvas_pallet_store.findRecord(Ag.Def.OBJ_ID_DATA_FIELD_ID, record.get(Ag.Def.OBJ_ID_DATA_FIELD_ID), 0, false, false, true);
						if(record.get(Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID)){
							var data = record.getData();
							data[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID] = false;
							if(Ext.isEmpty(canvas_pallet_record)){
								canvas_pallet_store.add(data);

								self.getCanvasRenderer().loadObj(self.getCanvasObjData(),{hitfma:canvas_pallet_store.getCount()});



							}
							else{
								canvas_pallet_record.beginEdit();
								var keys = Ext.Object.getKeys(canvas_pallet_record.getData());
								Ext.Array.each(keys, function(key){
									canvas_pallet_record.set(key, data[key]);
								});
								canvas_pallet_record.commit(false, keys);
								canvas_pallet_record.endEdit(false, keys);

								self.getCanvasRenderer().setObjProperties( self.getCanvasObjData() );

							}
						}
						else{
							if(Ext.isEmpty(canvas_pallet_record)) return;

							var datas = [canvas_pallet_record].map(function(record){var data = record.getData();data[Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID]=false;return data;});
							self.getCanvasRenderer().setObjProperties(datas);

							canvas_pallet_store.remove(canvas_pallet_record);

						}
					}catch(e){
						console.error(e);
					}
					canvas_pallet_store.resumeEvents();

					var canvasPanel = self._getCanvasPanel();
					var canvas_pallet_gridpanel = canvasPanel.down('gridpanel#canvas-pallet-gridpanel');
					canvas_pallet_gridpanel.getView().refresh();

				},0);
			}
		});


		canvas_pallet_store.on({
			add: function( store, records, index, eOpts ){
				canvas_neighbor_parts_store_task.cancel();
				canvas_neighbor_parts_store_task.delay(100);
			},
			bulkremove: function( store, records, indexes, isMove, eOpts ){
				canvas_neighbor_parts_store_task.cancel();
				canvas_neighbor_parts_store_task.delay(0);
			},
			update: function( store, record, operation ){
				if(operation!==Ext.data.Model.COMMIT) return;
				canvas_neighbor_parts_store_task.cancel();
				canvas_neighbor_parts_store_task.delay(0);
			}
		});





		return Ext.create('Ext.panel.Panel', Ext.apply({
			title: 'Neighbor Parts',
			itemId: 'canvas-neighbor-parts-panel',
			border: false,
			layout: {
				type: 'vbox',
				align: 'stretch'
			},
			items: [{
				height: 60,
				layout: {
					type: 'vbox',
					align: 'stretch',
					pack: 'center'
				},
				defaultType: 'fieldcontainer',
				defaults: {
					labelWidth: 76,
					labelAlign: 'right',
					layout: {
						type: 'hbox',
						align: 'middle',
						pack: 'start'
					}
				},
				items: [{
					flex: 1,
					fieldLabel: 'Origin(mm)',
					defaultType: 'displayfield',
					defaults: {
						labelWidth: 18,
						labelAlign: 'right',
						width: 88,
					},
					items: [{
						itemId: 'x',
						fieldLabel: 'X',
					},{
						itemId: 'y',
						fieldLabel: 'Y',
					},{
						itemId: 'z',
						fieldLabel: 'Z',
					}]
				},{
					fieldLabel: 'Radius(mm)',
					items: [{
						xtype: 'numberfield',
						itemId: Ag.Def.VOXEL_RANGE_FIELD_ID,
						width: 70,
						value: 10,
						maxValue: 50,
						minValue: 5,
						step: 5,
						checkChangeBuffer: 100,
						listeners: {
							change: function(field, value) {
								field.next('button#search').setDisabled(false);
							}
						}
					},{
						xtype: 'button',
						text: 'Search',
						itemId: 'search',
						disabled: true,
						handler: function(b){
							b.setDisabled(true);

							var voxel_range = b.prev('numberfield#'+Ag.Def.VOXEL_RANGE_FIELD_ID).getValue();
							voxel_range = parseInt(voxel_range, 10);

							var canvas_neighbor_parts_store = Ext.data.StoreManager.lookup('canvas-neighbor-parts-store');
							var p = canvas_neighbor_parts_store.getProxy();
							var extraParams = Ext.Object.merge({},p.extraParams || {});
							extraParams[Ag.Def.VOXEL_RANGE_FIELD_ID] = voxel_range;
							p.extraParams = extraParams;
							canvas_neighbor_parts_store.loadPage(1, {
								callback: function(records, operation, success){
									b.setDisabled(success);
								}
							});

						}
					}]
				}]
			},{
				flex: 1,
				xtype: 'gridpanel',


				itemId: 'canvas-neighbor-parts-gridpanel',
				store: canvas_neighbor_parts_store,
				viewConfig: self.getViewConfig(),
				columnLines: true,
				selModel: {
					mode: 'SIMPLE'
				},
				columns: [
					{
						text: self.DEF_PALLET_LABEL,
						dataIndex: Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID,
						width: self.DEF_REMOVE_COLUMN_WIDTH,
						hideable: false,
						hidden: false,
						hideable: true,
						xtype: 'agselectedcheckcolumn'
					},
					{
						text: Ag.Def.ID_DATA_FIELD_ID,
						dataIndex: Ag.Def.ID_DATA_FIELD_ID,
						width: 100
					},
					{ text: Ag.Def.NAME_DATA_FIELD_ID, dataIndex: Ag.Def.NAME_DATA_FIELD_ID, flex: 1 },
					{ text: Ag.Def.SYNONYM_DATA_FIELD_ID, dataIndex: Ag.Def.SYNONYM_DATA_FIELD_ID, flex: 1, hidden: true },
					{
						text: self.DEF_COLOR_LABEL,
						dataIndex: Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID,
						width: self.DEF_COLOR_COLUMN_WIDTH + 22,
						minWidth: self.DEF_COLOR_COLUMN_WIDTH + 22,
						hidden: false,
						hideable: true,
						xtype: 'agcolorcolumn'
					},
					{
						text: self.DEF_OPACITY_LABEL,
						dataIndex: Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID,
						width: self.DEF_OPACITY_COLUMN_WIDTH,
						hideable: false,
						hidden: false,
						hideable: true,
						xtype: 'agopacitycolumn'
					},
					{
						text: self.DEF_REMOVE_LABEL,
						dataIndex: Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID,
						width: self.DEF_REMOVE_COLUMN_WIDTH,
						hideable: false,
						hidden: false,
						hideable: true,
						xtype: 'agremovecolumn'
					},
					{
						text: self.DEF_DISTANCE_LABEL,
						dataIndex: Ag.Def.DISTANCE_FIELD_ID,
						width: 60,
						xtype: 'numbercolumn',
						format:'0.0000'
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
							}
						}
					}),
					self.getBufferedRenderer({pluginId: 'canvas-neighbor-parts-gridpanel-plugin'})
				],
				listeners: {
					afterrender: function( panel, eOpts ){
						panel.getView().on({
							itemkeydown: function(view, record, item, index, e, eOpts){
								if(e.getKey()===e.C && (e.ctrlKey || e.metaKey)){
									self.copyGridColumnsText(view);
								}
							}
						});
					}
				}

			}]
		},config||{}));
	},

	_searchCanvasNeighborPartsFromPick : function(renderer, intersects){
		var self = this;
		console.log('_searchCanvasNeighborPartsFromPick', renderer, intersects);

		var canvasPanel = self._getCanvasPanel();
		var canvas_neighbor_parts_panel = canvasPanel.down('panel#canvas-neighbor-parts-panel');
		var voxel_range = canvas_neighbor_parts_panel.down('numberfield#'+Ag.Def.VOXEL_RANGE_FIELD_ID).getValue();
		voxel_range = parseInt(voxel_range, 10);


		var canvas_pallet_store = Ext.data.StoreManager.lookup('canvas-pallet-store');

		var canvas_neighbor_parts_store = Ext.data.StoreManager.lookup('canvas-neighbor-parts-store');

		var filter_items_panel = self._getFilterPanel();
		var version_combobox = filter_items_panel.down('combobox#version-combobox');
		var version_record = version_combobox.findRecordByValue(version_combobox.getValue());
		var version_data = {};
		version_data[Ag.Def.LOCATION_HASH_MDID_KEY] = version_record.get(Ag.Def.LOCATION_HASH_MDID_KEY);
		version_data[Ag.Def.LOCATION_HASH_MVID_KEY] = version_record.get(Ag.Def.LOCATION_HASH_MVID_KEY);
		version_data[Ag.Def.LOCATION_HASH_MRID_KEY] = version_record.get(Ag.Def.LOCATION_HASH_MRID_KEY);
		version_data[Ag.Def.LOCATION_HASH_CIID_KEY] = version_record.get(Ag.Def.LOCATION_HASH_CIID_KEY);
		version_data[Ag.Def.LOCATION_HASH_CBID_KEY] = version_record.get(Ag.Def.LOCATION_HASH_CBID_KEY);

		var p = canvas_neighbor_parts_store.getProxy();
		var extraParams = Ext.Object.merge({},p.extraParams || {});
		extraParams = Ext.Object.merge(extraParams, version_data);
		extraParams[Ag.Def.VOXEL_RANGE_FIELD_ID] = voxel_range;
		extraParams[Ag.Def.OBJ_POINT_FIELD_ID] = Ext.JSON.encode(intersects[0].point);
		extraParams[Ag.Def.CONDITIONS_FIELD_ID] = Ext.JSON.encode({parts_map:true});
		extraParams[Ag.Def.OBJ_ID_DATA_FIELD_ID] = intersects[0].object[Ag.Def.OBJ_ID_DATA_FIELD_ID];

		if(Ext.Object.equals(p.extraParams || {},extraParams)){
//			segment_conditions_gridpanel.setLoading(false);
//			return;
		}
		p.extraParams = extraParams;

		canvas_neighbor_parts_store.loadPage(1);


		Ext.Array.each(['x','y','z'], function(key){
			var value = Ext.isNumber(intersects[0].point[key]) ? Ext.util.Format.number(parseFloat(intersects[0].point[key]),'0.0000') : '';
			canvas_neighbor_parts_panel.down('displayfield#'+key).setValue(value);
		});
	}
});
