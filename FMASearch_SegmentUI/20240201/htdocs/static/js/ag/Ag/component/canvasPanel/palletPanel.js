Ext.define('Ag.Component.Canvas.Pallet', {
	override: 'Ag.Main',

	getCanvasPalletGridPanel : function(){
		var self = this;
		return self._getCanvasPanel().down('gridpanel#canvas-pallet-gridpanel');
	},

	getCanvasObjData : function(){
		var self = this;

		var gridpanel = self.getCanvasPalletGridPanel();
		var store = gridpanel.getStore();
		var selModel = gridpanel.getSelectionModel();

		var is_selected = false;
		var selected = selModel.getSelection();
		if(Ext.isArray(selected) && selected.length) is_selected = true;

		return self.getObjDataFromRecords(store.getRange(), selModel, is_selected);
	},

	_createCanvasPalletPanel : function(config){
		var self = this;

		config = config || {};
		var itemId = config.itemId || 'canvas-pallet-panel';
		delete config.itemId;

		return Ext.create('Ext.panel.Panel', Ext.apply({
			title: 'Pallet',
			xtype: 'panel',
			itemId: itemId,
			layout: 'fit',
			dockedItems: [{
				xtype: 'toolbar',
				dock: 'bottom',
				itemId: 'bottom',
				items: [{
					itemId: 'select_all',
					tooltip: 'Select',
					iconCls: 'pallet_select',
					disabled: false,
					listeners: {
						click: function(button){
							var gridpanel = self.getCanvasPalletGridPanel();
							gridpanel.getSelectionModel().selectAll();
						}
					}
				},{
					xtype: 'tbspacer',
					height: 3,
				},{
					itemId: 'deselect_all',
					tooltip: 'Unselect',
					iconCls: 'pallet_unselect',
					disabled: false,
					listeners: {
						click: function(button){
							var gridpanel = self.getCanvasPalletGridPanel();
							gridpanel.getSelectionModel().deselectAll();
						}
					}
				},{
					xtype: 'tbspacer',
					height: 12,
				},{
					itemId: 'copy',
					tooltip: 'Copy',
					iconCls: 'pallet_copy',
					disabled: true,
				},{
					xtype: 'tbspacer',
					height: 3,
				},{
					itemId: 'paste',
					tooltip: 'Paste',
					iconCls: 'pallet_paste',
					disabled: true,
				},{
					xtype: 'tbspacer',
					height: 12,
				},{
					itemId: 'delete',
					tooltip: 'Delete',
					iconCls: 'pallet_delete',
					disabled: true,
					listeners: {
						afterrender: function( button, eOpts ){
							var gridpanel = self.getCanvasPalletGridPanel();
							gridpanel.on('selectionchange',function(selModel,selected){
								button.setDisabled(Ext.isEmpty(selected));
							});
						},
						click: function(button){
							var gridpanel = self.getCanvasPalletGridPanel();
							var records = gridpanel.getSelectionModel().getSelection();
							gridpanel.getStore().remove(records);

							var datas = records.map(function(record){var data = record.getData();data[Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID]=false;return data;});

							self.getCanvasRenderer().setObjProperties(datas);

						}
					}
				}]
			}],
			items: [{

				xtype: 'gridpanel',
				itemId: 'canvas-pallet-gridpanel',
				store: Ext.data.StoreManager.lookup('canvas-pallet-store'),
				viewConfig: self.getDropViewConfig(),
				columnLines: true,
				border: false,
				selModel: {
					mode: 'SIMPLE'
				},
				columns: [
					{ text: Ag.Def.ID_DATA_FIELD_ID,  dataIndex: Ag.Def.ID_DATA_FIELD_ID, width: 80 },
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
					}
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
					self.getBufferedRenderer({pluginId: 'canvas-pallet-gridpanel-plugin'})
				],
				listeners: {
					afterrender: function( panel, eOpts ){
						var store = panel.getStore();
						store.view = panel.getView();
						self.bindDrop(panel);
						self.bindCellclick(panel);

						store.view.on({
							itemkeydown: function(view, record, item, index, e, eOpts){
								if(e.getKey()===e.C && (e.ctrlKey || e.metaKey)){
									self.copyGridColumnsText(view);
								}
							},
							colorchange: function(record,value){
								var view = this;
								self.getCanvasRenderer().setObjProperties( self.getCanvasObjData() );
							},
							opacitychange: function(record,value){
								var view = this;
								self.getCanvasRenderer().setObjProperties( self.getCanvasObjData() );
							},
							removechange: function(record,value){
								var view = this;
								self.getCanvasRenderer().setObjProperties( self.getCanvasObjData() );
							}
						});

					},
					selectionchange: function( selModel, selected, eOpts ){
						self.getCanvasRenderer().setObjProperties(self.getCanvasObjData());
					}
				}
			}]
		},config||{}));
	}
});
