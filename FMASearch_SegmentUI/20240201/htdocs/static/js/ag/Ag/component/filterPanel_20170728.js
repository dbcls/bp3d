Ext.define('Ag.Component.Filter', {
	override: 'Ag.Main',

	__SEGMENT_LIST_CLICK_TO_RENDER : true,

	_getFilterObjDataFromRecord : function(record,is_selected){
		var self = this;
		record = record || {};
		var hash = record.getData ? record.getData() : record;

		if(Ext.isBoolean(hash[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID])){

			if(hash[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID]){

				if(self.USE_SELECTION_RENDERER_PICKED_COLOR){
					hash[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = self.DEF_SELECTION_RENDERER_PICKED_COLOR;
				}
				if(self.USE_SELECTION_RENDERER_PICKED_COLOR_FACTOR){

					var rgb = d3.rgb( hash[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] );
					var grayscale = rgb.r * 0.3 + rgb.g * 0.59 + rgb.b * 0.11;
					var k = grayscale>127.5 ? true : false;

					if(self.DEF_SELECTION_RENDERER_PICKED_COLOR_FACTOR>0){
						var factor = self.DEF_SELECTION_RENDERER_PICKED_COLOR_FACTOR;
						if(!self.USE_SELECTION_RENDERER_PICKED_COLOR) factor += k ? 0 : 0.1;
						hash[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = rgb.brighter(factor).toString();
					}
					else if(self.DEF_SELECTION_RENDERER_PICKED_COLOR_FACTOR<0){
						var factor = self.DEF_SELECTION_RENDERER_PICKED_COLOR_FACTOR * -1;
						if(!self.USE_SELECTION_RENDERER_PICKED_COLOR) factor += k ? 0 : 0.1;
						hash[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = rgb.darker(factor).toString();
					}

				}
				hash[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID] = true;
			}
			else if(Ext.isBoolean(is_selected) && is_selected){
				if(hash[Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID]>=1.0) hash[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID] = false;

				if(self.USE_SELECTION_RENDERER_PICKED_OTHER_OPACITY || self.USE_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR){
					var rgb = d3.rgb( hash[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] );
					var grayscale = rgb.r * 0.3 + rgb.g * 0.59 + rgb.b * 0.11;
					var k = grayscale>127.5 ? true : false;

					if(self.USE_SELECTION_RENDERER_PICKED_OTHER_OPACITY){

						hash[Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID] = self.DEF_SELECTION_RENDERER_PICKED_OTHER_OPACITY;
					}

					if(self.USE_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR){

						if(self.DEF_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR>0){
							hash[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = rgb.brighter(self.DEF_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR).toString();
						}
						else if(self.DEF_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR<0){
							hash[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = rgb.darker(self.DEF_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR*-1).toString();
						}
					}
				}
			}
		}
		return hash;
	},

	getFilterObjDataFromRecord : function(records,is_selected){
		var self = this;
		return records.map(Ext.bind(self._getFilterObjDataFromRecord,self,[is_selected],1));
	},

	getFilterObjDataHash : function(hash){
		var self = this;
		hash = hash || {};
		var filter_top_panel = self._getFilterPanel();
		var temporary_pallet_gridpanel  = filter_top_panel.down('gridpanel#temporary-pallet-gridpanel');
		var temporary_pallet_selmodel   = temporary_pallet_gridpanel.getSelectionModel();
		var temporary_pallet_store      = temporary_pallet_gridpanel.getStore();
		var persistent_pallet_gridpanel = filter_top_panel.down('gridpanel#persistent-pallet-gridpanel');
		var persistent_pallet_selmodel  = persistent_pallet_gridpanel.getSelectionModel();
		var persistent_pallet_store     = persistent_pallet_gridpanel.getStore();

		var is_selected = false;
		temporary_pallet_store.each(function(record){
			var id = record.get(Ag.Def.ID_DATA_FIELD_ID);
			hash[ id ] = record.getData();
			hash[ id ][ Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID ] = temporary_pallet_selmodel.isSelected(record);
			if(is_selected) return true;
			if(hash[ id ][ Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID ]) is_selected = true;
		});
		persistent_pallet_store.each(function(record){
			var id = record.get(Ag.Def.ID_DATA_FIELD_ID);
			hash[ id ] = record.getData();
			hash[ id ][ Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID ] = persistent_pallet_selmodel.isSelected(record);
			if(is_selected) return true;
			if(hash[ id ][ Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID ]) is_selected = true;
		});
		return is_selected;
	},

	getFilterObjData : function(hash){
		var self = this;
		hash = hash || {};
		var is_selected = self.getFilterObjDataHash(hash);
		return self.getFilterObjDataFromRecord( Ext.Object.getValues( hash ), is_selected );
	},

	getFilterRenderer : function(){
		var self = this;
		var filter_top_panel = self._getFilterPanel();
		var panel = filter_top_panel.down('panel#temporary-render-panel');
		return panel.__webglMainRenderer;
	},

	_filterGridpanelSelectionchange : function(gridpanel,target_gridpanel){
		var self = this;

		var selmodel  = gridpanel.getSelectionModel();
		var store = gridpanel.getStore();
		var selectKeepExisting = true;

		var target_selmodel  = target_gridpanel.getSelectionModel();
		var target_store     = target_gridpanel.getStore();
		var target_selected_records   = [];
		var target_deselected_records = [];
		store.each(function(record){
			var target_record = target_store.findRecord(Ag.Def.ID_DATA_FIELD_ID, record.get(Ag.Def.ID_DATA_FIELD_ID), 0, false, false, true);
			if(target_record) selmodel.isSelected(record) ? target_selected_records.push(target_record) : target_deselected_records.push(target_record);
		});
		if(target_deselected_records.length) target_selmodel.deselect(target_deselected_records, true);
		if(target_selected_records.length) target_selmodel.select(target_selected_records, selectKeepExisting, true);
	},

	_filterDeselectAll : function( suppressEvent ){
		var self = this;
		var filter_top_panel = self._getFilterPanel();
		var temporary_pallet_gridpanel  = filter_top_panel.down('gridpanel#temporary-pallet-gridpanel');
		var temporary_pallet_selmodel   = temporary_pallet_gridpanel.getSelectionModel();
		var temporary_pallet_store      = temporary_pallet_gridpanel.getStore();
		var persistent_pallet_gridpanel = filter_top_panel.down('gridpanel#persistent-pallet-gridpanel');
		var persistent_pallet_selmodel  = persistent_pallet_gridpanel.getSelectionModel();
		var persistent_pallet_store     = persistent_pallet_gridpanel.getStore();

		suppressEvent = Ext.isEmpty(suppressEvent) ? false : (Ext.isBoolean(suppressEvent) ? suppressEvent : (suppressEvent ? true : false));

		temporary_pallet_selmodel.deselectAll(true);
		persistent_pallet_selmodel.deselectAll(true);
		if(!suppressEvent) persistent_pallet_gridpanel.fireEvent('selectionchange', persistent_pallet_selmodel, [], {});
	},

	_createVersionPanel : function(config){
		var self = this;
		return Ext.create('Ext.panel.Panel', Ext.apply({
			itemId: 'version-panel',
//			xtype: 'toolbar',
			border: 1,
			bodyPadding: '0 5',
			layout: {
				type: 'hbox',
				align: 'middle',
				pack: 'start'
			},
			items: [{
				itemId: 'version-combobox',
				width: 180,
				xtype: 'combobox',
				labelWidth: 50,
				labelAlign: 'right',
				fieldLabel: 'version',
				store: Ext.data.StoreManager.lookup('version-store'),
				queryMode: 'local',
				displayField: 'display',
				valueField: 'value',
				editable: false,
				value: Ext.data.StoreManager.lookup('version-store').last().get('value'),
				listeners: {
					afterrender: function(field, eOpts){
//						console.log(field.getStore().getRange());
					}
				}
			},{
				padding: '0 0 0 10',
				xtype: 'checkbox',
				itemId: 'automatic-rendering-checkbox',
				tooltip: 'Automatic rendering',
				boxLabel: 'Automatic rendering',
				checked: true

			}]
		},config||{}));
	},

	_isFilterAutoRender : function(){
		var self = this;
		var filter_top_panel = self._getFilterPanel();
		var checkbox = filter_top_panel.down('checkbox#automatic-rendering-checkbox');
		return checkbox ? checkbox.getValue() : false;
	},

	_createSegmentListPanel : function(config){
		var self = this;
		return Ext.create('Ext.tree.Panel', Ext.apply({
			itemId: 'segment-list-treepanel',
			rootVisible: false,
			store: Ext.data.StoreManager.lookup('segment-list-treestore'),
			viewConfig: self.getViewConfig(),
			selModel:{
				selection: 'treemodel',
				mode: 'SIMPLE'
			},
/*
			hideHeaders: true,
			columns: [{
				xtype: 'treecolumn',
				text: 'segment',
//				flex: 1,
				width: 240,
				sortable: false,
				dataIndex: 'text',
//				autoScroll: true,
//				locked: true
			},{
				xtype: 'numbercolumn',
				text: 'element_count',
//				flex: 1,
				width: 100,
				sortable: false,
				dataIndex: 'element_count'
			}],
/**/
			dockedItems: [{
				hidden: true,
				xtype: 'toolbar',
				dock: 'top',
				itemId: 'top',
				items: [{
					itemId: 'select_all',
					iconCls:'pallet_select',
					listeners: {
						click: function(button,e){
							var panel = button.up('treepanel');
							var selModel = panel.getSelectionModel();
							selModel.selectAll(true);
							var datas = [];
							panel.getRootNode().cascadeBy(function(node){
								var data = node.getData();
								if(node.getDepth()===1) data[Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID] = false;
								data[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID] = true;
								data[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = self.DEF_SELECTION_SEGMENT_RENDERER_PICKED_COLOR;
								datas.push(data);
							});
							var parentPanel = panel.up('panel#segment-items-panel');
							parentPanel.__webglMainRenderer.setObjProperties(datas);
							panel.fireEvent('selectionchange', selModel, selModel.getSelection(), {});
						}
					}
				},{
					itemId: 'deselect_all',
					iconCls:'pallet_unselect',
					handler: function(button,e){
						var panel = button.up('treepanel');
						var selModel = panel.getSelectionModel();
						selModel.deselectAll(true);
						var datas = [];
						panel.getRootNode().cascadeBy(function(node){
							var data = node.getData();
							if(node.getDepth()!==1) data[Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID] = false;
							datas.push(data);
						});
						var parentPanel = panel.up('panel#segment-items-panel');
						parentPanel.__webglMainRenderer.setObjProperties(datas);
						panel.fireEvent('selectionchange', selModel, selModel.getSelection(), {});
					}
				}]
			}],
			listeners: {
				afterrender: function( panel, eOpts ){
					self.bindCellclick(panel);
				},
				load: function( store, node, records, successful, eOpts ){
					var panel = this;
					var datas = [];
					node.cascadeBy(function(node){
						if(Ext.isEmpty(node.get(Ag.Def.OBJ_URL_DATA_FIELD_ID))) return;
						var data = node.getData();
						if(node.getDepth()!==1) data[Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID] = false;
						datas.push(data);
					});

					var parentPanel = panel.up('panel#segment-items-panel');
					if(parentPanel.rendered){
						parentPanel.__webglMainRenderer.loadObj(datas);
					}else{
						parentPanel.on('afterrender',function(){
							parentPanel.__webglMainRenderer.loadObj(datas);
						},self,{single:true});
					}
				},
				beforeitemcollapse: function(){
					return false;
				},
				deselect: function( selModel, node, index, eOpts ){
					var panel = this;
					var datas = [];

					if(node.getDepth()===1){
						var data = node.getData();
						datas.push(data);

						var childrenNodes = [];
						node.eachChild(function(childrenNode){
							if(selModel.isSelected(childrenNode)) childrenNodes.push(childrenNode);
							var data = childrenNode.getData();
							data[Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID] = false;
							datas.push(data);
						});
						if(childrenNodes.length) selModel.deselect(childrenNodes, true);

					}
					else{
						var childrenNodes = [];
						var parentNode = node.parentNode;

						parentNode.eachChild(function(childrenNode){
							if(selModel.isSelected(childrenNode)) childrenNodes.push(childrenNode);
						});

						var data = parentNode.getData();
						if(childrenNodes.length) data[Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID] = false;
						datas.push(data);

						parentNode.eachChild(function(childrenNode){
							var data = childrenNode.getData();
							if(childrenNodes.length){
								if(selModel.isSelected(childrenNode)){
									data[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID] = true;
									data[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = self.DEF_SELECTION_SEGMENT_RENDERER_PICKED_COLOR;
								}
							}
							else{
								data[Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID] = false;
							}
							datas.push(data);
						});

					}

					var parentPanel = panel.up('panel#segment-items-panel');
					parentPanel.__webglMainRenderer.setObjProperties(datas);
				},
				select: function( selModel, node, index, eOpts ){
					var panel = this;
					var datas = [];

					if(node.getDepth()===1){

						var data = node.getData();
						data[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID] = true;
						data[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = self.DEF_SELECTION_SEGMENT_RENDERER_PICKED_COLOR;
						datas.push(data);

						var childrenNodes = [];
						node.eachChild(function(childrenNode){
							if(selModel.isSelected(childrenNode)) childrenNodes.push(childrenNode);
							var data = childrenNode.getData();
							data[Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID] = false;
							datas.push(data);
						});
						if(childrenNodes.length) selModel.deselect(childrenNodes, true);
					}
					else{
						var parentNode = node.parentNode;
						if(selModel.isSelected(parentNode)) selModel.deselect([parentNode], true);
						var parentData = parentNode.getData();
						parentData[Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID] = false;
						datas.push(parentData);

						parentNode.eachChild(function(childrenNode){
							var data = childrenNode.getData();
							if(selModel.isSelected(childrenNode)){
								data[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID] = true;
								data[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = self.DEF_SELECTION_SEGMENT_RENDERER_PICKED_COLOR;
							}
							datas.push(data);
						});
					}


					var parentPanel = panel.up('panel#segment-items-panel');
					parentPanel.__webglMainRenderer.setObjProperties(datas);
				},
			}
		},config||{}));
	},

	_createSegmentRenderPanel : function(config){
		var self = this;
		return Ext.create('Ext.panel.Panel', Ext.apply({
			itemId: 'segment-render-panel',
			listeners: {
				afterrender: function(panel, eOpts){
				},
				resize: function( panel, width, height, oldWidth, oldHeight, eOpts){
					var parentPanel = panel.up('panel#segment-items-panel');
					parentPanel.__webglMainRenderer._setSize(10,10);
					var $dom = $(panel.layout.innerCt.dom);
					width = $dom.width();
					height = $dom.height();
					parentPanel.__webglMainRenderer.setSize(width,height);
				}
			}
		},config||{}));
	},

	_createSegmentItemsPanel : function(config){
		var self = this;

		var segment_items_dockedItems = [self._createRenderTopDocked()];

//		segment_items_dockedItems[0].items.forEach(function(item){
//			item.hidden = true;
//		});

		segment_items_dockedItems[0].items.unshift('->');
/*
		segment_items_dockedItems[0].items.unshift('-');
		segment_items_dockedItems[0].items.unshift({
			xtype: 'checkbox',
			itemId: 'automatic-rendering-checkbox',
//			tooltip: 'Automatic rendering',
			boxLabel: 'Automatic rendering',
			checked: true
		});
		segment_items_dockedItems[0].items.unshift('-');
		segment_items_dockedItems[0].items.unshift(' ');
*/
		segment_items_dockedItems[0].items.unshift({xtype:'tbtext',text:'Segment',style:{'font-size':'1.2em','font-weight':'bold','cursor':'default','user-select':'none'}});
		segment_items_dockedItems[0].items.pop();
		segment_items_dockedItems[0].items.pop();

		segment_items_dockedItems[0].items.push({
			itemId: 'select_all',
			iconCls:'pallet_select',
			listeners: {
				click: function(button,e){
					var panel = button.up('panel#segment-items-panel').down('treepanel#segment-list-treepanel');
					var selModel = panel.getSelectionModel();
					var datas = [];
/*
					selModel.selectAll(true);
					panel.getRootNode().cascadeBy(function(node){
						var data = node.getData();
						if(node.getDepth()===1) data[Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID] = false;
						data[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID] = true;
						data[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = self.DEF_SELECTION_SEGMENT_RENDERER_PICKED_COLOR;
						datas.push(data);
					});
*/
					var records = [];
					panel.getRootNode().cascadeBy(function(node){
						var data = node.getData();
						if(node.getDepth()===1){
							records.push(node);
						}else{
							data[Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID] = false;
						}
						data[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID] = true;
						data[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = self.DEF_SELECTION_SEGMENT_RENDERER_PICKED_COLOR;
						datas.push(data);
					});
					selModel.select(records,false,true);


					var parentPanel = panel.up('panel#segment-items-panel');
					parentPanel.__webglMainRenderer.setObjProperties(datas);
					panel.fireEvent('selectionchange', selModel, selModel.getSelection(), {});
				}
			}
		},{
			itemId: 'deselect_all',
			iconCls:'pallet_unselect',
			listeners: {
				click: function(button,e){
					var panel = button.up('panel#segment-items-panel').down('treepanel#segment-list-treepanel');
					var selModel = panel.getSelectionModel();
					selModel.deselectAll(true);
					var datas = [];
					panel.getRootNode().cascadeBy(function(node){
						var data = node.getData();
						if(node.getDepth()!==1) data[Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID] = false;
						datas.push(data);
					});
					var parentPanel = panel.up('panel#segment-items-panel');
					parentPanel.__webglMainRenderer.setObjProperties(datas);
					panel.fireEvent('selectionchange', selModel, selModel.getSelection(), {});
				}
			}
		});


		return Ext.create('Ext.panel.Panel', Ext.apply({
			itemId: 'segment-items-panel',
			border: 0,
			dockedItems: segment_items_dockedItems,
			layout: {
				type: 'hbox',
				align: 'stretch',
				pack: 'start'
			},
			items: [
				self._createSegmentListPanel({flex: 0.62}),
				self._createSegmentRenderPanel({flex: 1})
			],
			listeners: {
				afterrender: function(panel, eOpts){

					var segment_list_treepanel = panel.down('treepanel#segment-list-treepanel');
					var selModel = segment_list_treepanel.getSelectionModel();
					var selectKeepExisting = selModel.getSelectionMode()==='SIMPLE' ? true : e.ctrlKey;
					var selectSuppressEvent = false;

					var filter_top_panel = self._getFilterPanel();
					var temporary_render_panel  = filter_top_panel.down('panel#temporary-render-panel');
					var temporary_render_top_toolbar     = temporary_render_panel.down('toolbar#top');
					var temporary_render_longitude_field = temporary_render_top_toolbar.down('numberfield#longitude');
					var temporary_render_latitude_field  = temporary_render_top_toolbar.down('numberfield#latitude');

					var segment_items_panel = panel;
					var segment_items_top_toolbar = panel.down('toolbar#top');
					var segment_render_longitude_field = segment_items_top_toolbar.down('numberfield#longitude');
					var segment_render_latitude_field  = segment_items_top_toolbar.down('numberfield#latitude');
					var segment_render_zoom_field      = segment_items_top_toolbar.down('numberfield#zoom');
					segment_render_longitude_field.hide();
					segment_render_latitude_field.hide();
					segment_render_zoom_field.hide();

					if(Ext.isEmpty(panel.__webglMainRenderer)){

						var pickDelayedTask =  new Ext.util.DelayedTask(function(nodes,view,e){
							console.log(view);
							var selModel = view.getSelectionModel();
							var selectKeepExisting = selModel.getSelectionMode()==='SIMPLE' ? true : e.ctrlKey;
							var selectSuppressEvent = true;

							var datas = [];
							var last_node;
							Ext.each(nodes,function(node){
								var data = node.getData();
								if(view.isSelected(node)){
									view.deselect(node,selectSuppressEvent);
								}else{
									view.select(node,selectKeepExisting,selectSuppressEvent);
									last_node = node;

									data[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID] = true;
									data[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = self.DEF_SELECTION_SEGMENT_RENDERER_PICKED_COLOR;
								}
								datas.push(data);
							});
							if(last_node){
								view.focusNode(last_node);
								view.getEl().setScrollLeft(0);
							}
							if(datas.length) panel.__webglMainRenderer.setObjProperties(datas);
							view.panel.fireEvent('selectionchange', selModel, selModel.getSelection(), {});
						});

						var dblclickFunc =  function(nodes,view,e){
							var selModel = view.getSelectionModel();
							var selectKeepExisting = selModel.getSelectionMode()==='SIMPLE' ? true : e.ctrlKey;
							var selectSuppressEvent = true;

							var datas = [];
							var select_nodes = [];
							var deselect_nodes = [];
							Ext.each(nodes,function(node){
								var selected = view.isSelected(node);

								if(node.getDepth()===1){
									var data = node.getData();
									data[Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID] = false;
									datas.push(data);
									deselect_nodes.push(node);


									node.eachChild(function(childNode){
										var data = childNode.getData();
										if(selected){
											data[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = self.DEF_SELECTION_SEGMENT_RENDERER_PICKED_COLOR;
											select_nodes.push(childNode);
										}else{
											deselect_nodes.push(childNode);
										}
										datas.push(data);
									});
								}
								else if(node.getDepth()===2){
									var data = node.parentNode.getData();
									if(selected){
										data[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = self.DEF_SELECTION_SEGMENT_RENDERER_PICKED_COLOR;
										select_nodes.push(node.parentNode);
									}else{
										deselect_nodes.push(node.parentNode);
									}
									datas.push(data);
									node.parentNode.eachChild(function(childNode){
										var data = childNode.getData();
										data[Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID] = false;
										deselect_nodes.push(childNode);
										datas.push(data);
									});
								}
							});
							if(datas.length) panel.__webglMainRenderer.setObjProperties(datas);
							if(select_nodes.length) view.select(select_nodes,selectKeepExisting,true);
							if(deselect_nodes.length) view.deselect(deselect_nodes,true);
							view.panel.fireEvent('selectionchange', selModel, selModel.getSelection(), {});
						}

						panel.__webglMainRenderer = new Ag.MainRenderer({
							width:108,
							height:108,
							rate:1,
//							minZoom: zoom_field.minValue,
//							maxZoom: zoom_field.maxValue,
							minZoom: 1,
							maxZoom: 1,
							usePan: false,
							backgroundColor: self.DEF_RENDERER_BACKGROUND_COLOR,
							listeners: {
								pick: function(ren,intersects,e){
//									console.log('pick',ren,intersects,e);

									var is_dblclick = false;
									var current_date = new Date();
									if(Ext.isDate(panel.__lastPickDate)){
										var dt = Ext.Date.add(panel.__lastPickDate, Ext.Date.MILLI, self.DEF_DOUBLE_CLICK_INTERVAL);
										is_dblclick = Ext.Date.between(current_date,panel.__lastPickDate, dt);
									}
									panel.__lastPickDate = current_date;


									var childPanel = panel.down('treepanel#segment-list-treepanel');
									var childPanelView = childPanel.getView();
									var rootNode = childPanel.getRootNode();

									var urlBASAL_STEM = {};
									rootNode.cascadeBy(function(node){
										var text = node.get('text').toUpperCase().replace(/^[0-9_]+/g,'');
//										console.log(node.get('text'),text);
										if(text==='BASAL' || text==='STEM'){
											urlBASAL_STEM[node.get(Ag.Def.OBJ_URL_DATA_FIELD_ID)] = node;
										}
									});
//									console.log(urlBASAL_STEM);


									var meshs = [];

									if(Ext.isArray(intersects) && intersects.length){

//										console.log(is_dblclick, intersects);
//										intersects.forEach(function(intersect){
//											console.log(intersect.object[Ag.Def.OBJ_URL_DATA_FIELD_ID]);
//										});

										var temp_meshs = [];
										var exists_mesh = {};
										Ext.each(intersects,function(intersect){
											var mesh = intersect.object;
											if(Ext.isEmpty(mesh[Ag.Def.OBJ_ID_DATA_FIELD_ID])) return true;
											if(Ext.isEmpty(exists_mesh[mesh[Ag.Def.OBJ_ID_DATA_FIELD_ID]])){
												exists_mesh[mesh[Ag.Def.OBJ_ID_DATA_FIELD_ID]] = mesh;
												temp_meshs.push(mesh);

												if(Ext.isEmpty(urlBASAL_STEM[mesh[Ag.Def.OBJ_URL_DATA_FIELD_ID]])) return true;
												meshs.push(mesh);
											}
										});
										if(temp_meshs.length && meshs.length === 0) meshs.push(temp_meshs[0]);
									}

									if(Ext.isArray(meshs) && meshs.length){
//										console.log(is_dblclick, meshs);

//										var childPanel = panel.down('treepanel#segment-list-treepanel');
//										var childPanelView = childPanel.getView();
//										var rootNode = childPanel.getRootNode();

										var childNodes = [];
										Ext.each(meshs,function(mesh){
											var childNode = rootNode.findChild(Ag.Def.OBJ_ID_DATA_FIELD_ID, mesh[Ag.Def.OBJ_ID_DATA_FIELD_ID], true);
											if(childNode) childNodes.push(childNode);
										});
//										console.log(is_dblclick, childNodes);
//										Ext.each(childNodes,function(childNode){
//											console.log(childNode.get('text'));
//										});

										if(childNodes.length){
											if(is_dblclick){
												pickDelayedTask.cancel();
												dblclickFunc.apply(self,[childNodes,childPanelView,e]);
											}else{
												pickDelayedTask.delay(self.DEF_DOUBLE_CLICK_INTERVAL,null,null,[childNodes,childPanelView,e]);
											}
										}
									}

								},
								rotate: function(ren,value){
									if(segment_render_longitude_field){
										if(segment_render_longitude_field.getValue() !== value.H){
											segment_render_longitude_field.suspendEvent('change');
											try{
												segment_render_longitude_field.setValue(value.H);
											}catch(e){
												console.error(e);
											}
											segment_render_longitude_field.resumeEvent('change');
											if(segment_items_panel.__webglSubRenderer) segment_items_panel.__webglSubRenderer.setHorizontal(value.H);
										}
									}
									if(segment_render_latitude_field){
										if(segment_render_latitude_field.getValue() !== value.V){
											segment_render_latitude_field.suspendEvent('change');
											try{
												segment_render_latitude_field.setValue(value.V);
											}catch(e){
												console.error(e);
											}
											segment_render_latitude_field.resumeEvent('change');
											if(segment_items_panel.__webglSubRenderer) segment_items_panel.__webglSubRenderer.setVertical(value.V);
										}
									}


									if(temporary_render_longitude_field){
										if(temporary_render_longitude_field.getValue() !== value.H){
											temporary_render_longitude_field.suspendEvent('change');
											try{
												temporary_render_longitude_field.setValue(value.H);
											}catch(e){
												console.error(e);
											}
											temporary_render_longitude_field.resumeEvent('change');
											if(temporary_render_panel.__webglMainRenderer) temporary_render_panel.__webglMainRenderer.setHorizontal(value.H);
											if(temporary_render_panel.__webglSubRenderer) temporary_render_panel.__webglSubRenderer.setHorizontal(value.H);
										}
									}
									if(temporary_render_latitude_field){
										if(temporary_render_latitude_field.getValue() !== value.V){
											temporary_render_latitude_field.suspendEvent('change');
											try{
												temporary_render_latitude_field.setValue(value.V);
											}catch(e){
												console.error(e);
											}
											temporary_render_latitude_field.resumeEvent('change');
											if(temporary_render_panel.__webglMainRenderer) temporary_render_panel.__webglMainRenderer.setVertical(value.V);
											if(temporary_render_panel.__webglSubRenderer) temporary_render_panel.__webglSubRenderer.setVertical(value.V);
										}
									}


								},
								zoom: function(ren,value){
									//未使用
								}
							}
						});
					}
					else{
						panel.__webglMainRenderer.domElement().style.display = '';
						panel.__webglMainRenderer.hideAllObj();
					}

					var childPanel = panel.down('panel#segment-render-panel');
					childPanel.layout.innerCt.dom.appendChild( panel.__webglMainRenderer.domElement() );



					segment_render_longitude_field.on('change',function(field,value){
						console.log(value);
					});
					segment_render_latitude_field.on('change',function(field,value){
						console.log(value);
					});


				}
			}
		},config||{}));
	},

	_createSystemColorPanel : function(config){
		var self = this;
		return Ext.create('Ext.panel.Panel', Ext.apply({
			itemId: 'system-color-panel',
			dockedItems: [{
				xtype: 'toolbar',
				dock: 'top',
				itemId: 'top',
				items: [{
					xtype:'tbtext',
					text:'System',
					style:{'font-size':'1.2em','font-weight':'bold','cursor':'default','user-select':'none'}
				},'->',{
					itemId: 'select_all',
					tooltip: 'Select',
					iconCls: 'pallet_select',
					disabled: false,
					listeners: {
						click: function(button){
							var system_color_view = button.up('panel#system-color-panel').down('dataview#system-color-view');
							var system_color_view_selmodel = system_color_view.getSelectionModel();
							system_color_view_selmodel.selectAll();
						}
					}
				},{
					itemId: 'deselect_all',
					tooltip: 'Unselect',
					iconCls: 'pallet_unselect',
					disabled: false,
					listeners: {
						click: function(button){
							var system_color_view = button.up('panel#system-color-panel').down('dataview#system-color-view');
							var system_color_view_selmodel = system_color_view.getSelectionModel();
							system_color_view_selmodel.deselectAll();
						}
					}
				}]
			}],
			layout: 'fit',
			items: Ext.create('Ext.view.View', {
				itemId: 'system-color-view',
				store: Ext.data.StoreManager.lookup('system-list-store'),
				autoScroll: true,
				tpl: [
					'<tpl for=".">',
						'<div class="system-list-wrap" data-id="{'+Ag.Def.SYSTEM_ID_DATA_FIELD_ID+':htmlEncode}">',
							'<div class="system-list-item" style="background:{'+Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID+'};color:{[ this.getColor(values.'+Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID+') ]}">{text}&nbsp;({[ this.getStr(values.element_count) ]})</div>',
						'</div>',
					'</tpl>',
					'<div class="x-clear"></div>',
					{
						getColor: function(value){
							var rgb = d3.rgb( value );
							var grayscale = rgb.r * 0.3 + rgb.g * 0.59 + rgb.b * 0.11;
							var k = grayscale>127.5 ? 'black' : 'white';
							return k;
						},
						getStr: function(value){
							if(Ext.isEmpty(value)) return '-';
							return value;
						}
					}
				],
				selModel: {
					mode: 'SIMPLE'
				},
				trackOver: true,
				overItemCls: 'x-item-over',
				itemSelector: 'div.system-list-wrap',
				emptyText: 'No images to display',
				prepareData: function(data) {
/*
					Ext.apply(data, {
						shortName: Ext.util.Format.ellipsis(data.name, 15),
						sizeString: Ext.util.Format.fileSize(data.size),
						dateString: Ext.util.Format.date(data.lastmod, "m/d/Y g:i a")
					});
*/
					return data;
				},
				listeners: {
					afterrender: function(view, eOpts){
						var filter_top_panel = self._getFilterPanel();
						var segment_list_treepanel = filter_top_panel.down('treepanel#segment-list-treepanel');
						var version_combobox = filter_top_panel.down('combobox#version-combobox');
						var segment_panel = filter_top_panel.down('panel#segment-panel');

						var system_color_view = view;
						var system_color_view_selmodel = system_color_view.getSelectionModel();
						var system_color_view_store = system_color_view.getStore();

						if(
							Ext.isEmpty(segment_list_treepanel) ||
							Ext.isEmpty(version_combobox)       ||
							Ext.isEmpty(segment_panel)          ||
							Ext.isEmpty(system_color_view_store) ||
							Ext.isEmpty(system_color_view_selmodel)
						) return;

						version_combobox.on({
							select: function( combobox, records, eOpts ){
								var selModel = segment_list_treepanel.getSelectionModel();
								segment_list_treepanel.fireEvent('selectionchange',selModel,selModel.getSelection(),{});
							},
							buffer:10
						});

						var end_func = function(){
							segment_panel.setLoading(false);
							console.timeEnd( 'segment_list_treepanel.selectionchange' );
						};
						var interrupt_func = function(){
							system_color_view_store.suspendEvents( true );
							system_color_view_store.each(function(record){
								if(Ext.isEmpty(record.get('element_count'))) return true;
								record.beginEdit();
								record.set('element_count',null);
								record.commit(false,['element_count']);
								record.endEdit(false,['element_count']);
							});
							system_color_view_store.resumeEvents();

							end_func();
						};
						var func = function(selModel,selected, eOpts){
							console.time( 'segment_list_treepanel.selectionchange' );

							if(
								Ext.isEmpty(Ag.data.SEG2ART)  ||
								Ext.isEmpty(Ag.data.renderer) ||
								Ext.isEmpty(selected)
							){
								interrupt_func();
								return;
							}

							var version_record = version_combobox.findRecordByValue(version_combobox.getValue());
							var version = version_record.get(Ag.Def.VERSION_STRING_FIELD_ID);
							if(Ext.isEmpty(Ag.data.renderer[version])){
								interrupt_func();
								return;
							}

							var ids = Ag.data.renderer[version][Ag.Def.IDS_DATA_FIELD_ID];
							var art_ids = Ag.data.renderer[version][Ag.Def.OBJ_IDS_DATA_FIELD_ID];
							if(Ext.isEmpty(ids) || Ext.isEmpty(art_ids)){
								interrupt_func();
								return;
							}

							try{

								var segments;

								var segment_list_treeview = segment_list_treepanel.getView();
								Ext.each(segment_list_treepanel.getRootNode().childNodes,function(childNode){
									var isSelected = false;
									Ext.each(childNode.childNodes,function(grandChildNode){
										if(!segment_list_treeview.isSelected(grandChildNode)) return true;
										isSelected = true;
										var segment_arr = grandChildNode.get('segment').split('/');
										if(Ag.data.SEG2ART[segment_arr[0]][segment_arr[1]]){
											segments = segments || {};
											Ext.Object.merge(segments,Ag.data.SEG2ART[segment_arr[0]][segment_arr[1]]);
										}
									});
									if(isSelected) return true;
									if(!segment_list_treeview.isSelected(childNode)) return true;

									var segment_arr = childNode.get('segment').split('/');
									if(Ag.data.SEG2ART[segment_arr[0]][segment_arr[1]]){
										segments = segments || {};
										Ext.Object.merge(segments,Ag.data.SEG2ART[segment_arr[0]][segment_arr[1]]);
									}
								});
								if(Ext.isEmpty(segments)){
									interrupt_func();
									return;
								}
//								console.log(segments);

/*
								var SEGMENT_LIST_NODES = {};
								var segment_list_store = Ext.data.StoreManager.lookup('segment-list-treestore');
								var segment_list_store_root_node = segment_list_store.getRootNode();
								segment_list_store_root_node.cascadeBy(function(node){
									SEGMENT_LIST_NODES[node.get('segment')] = node;
								});
*/

								var element_count = {};
								var use_ids = {};

								Ext.Object.each(segments,function(art_id){
									if(Ext.isEmpty(art_ids[art_id])) return true;

									var id = art_ids[art_id][Ag.Def.ID_DATA_FIELD_ID];
									if(Ext.isEmpty(ids[id])) return true;

									use_ids[id] = null;
								});
								Ext.Object.each(use_ids,function(id){
									element_count[ids[id][Ag.Def.SYSTEM_ID_DATA_FIELD_ID]] = element_count[ids[id][Ag.Def.SYSTEM_ID_DATA_FIELD_ID]] || 0;
									element_count[ids[id][Ag.Def.SYSTEM_ID_DATA_FIELD_ID]]++;
								});

//								console.log(element_count);


								system_color_view_store.suspendEvents( true );
								system_color_view_store.each(function(record){
									var system_id = record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID);
									record.beginEdit();
									record.set('element_count',element_count[system_id] || 0);
									record.commit(false,['element_count']);
									record.endEdit(false,['element_count']);
								});
								system_color_view_store.resumeEvents();

								segment_panel.setLoading(false);
							}catch(e){
								console.error(e);
							}
							end_func();
						};

						segment_list_treepanel.on('selectionchange',function(selModel,selected, eOpts){
							segment_panel.setLoading(true);

							if(window.setImmediate){
								window.setImmediate(function(){
									func(selModel,selected, eOpts);
								});
							}else{
								Ext.defer(function(){
									func(selModel,selected, eOpts);
								},10);
							}
						},segment_list_treepanel)


//					},
//					selectionchange: function(selModel, selected){
//						console.log(selModel, selected);
					}
				}
			})
		},config||{}));
	},

	_createSegmentPanel : function(config){
		var self = this;

		return Ext.create('Ext.panel.Panel', Ext.apply({
			itemId: 'segment-panel',
			layout: {
				type: 'vbox',
				align: 'stretch',
				pack: 'start'
			},
			items: [
				self._createVersionPanel({height: 36}),
				self._createSegmentItemsPanel({flex: 1}),
				self._createSystemColorPanel({height:200})
			]
		},config||{}));
	},

	_createSearchConditionsPanel : function(config){
		var self = this;

		return Ext.create('Ext.panel.Panel', Ext.apply({
			itemId: 'segment-conditions-panel',
			layout: {
				type: 'vbox',
				align: 'stretch',
				pack: 'cenrer'
			},
//			bodyPadding: '5 5 0',
			items: [{
				xtype: 'label',
				style: 'font-weight:bold;background-color:#add2ed;padding:2px;',
				text: 'Semantic Refinement'.toUpperCase()
			},{
				xtype: 'label',
				style: 'padding:4px 0 2px 5px;',
				text: 'Concepts keyword search (AND)'
			},{
				style: 'margin:0 5px 5px 5px;',
				xtype: 'radiogroup',
				itemId: 'search_target',
				columns: [77,149],
				items: [{
					boxLabel:   'Element',
					name:       'searchTarget',
					inputValue: '1'
				},{
					boxLabel:   'Include HYPERNYM',
					name:       'searchTarget',
					inputValue: '2',
					checked:    true
				}]
			},{
				style: 'margin:0 5px 5px 5px;',
				xtype: 'checkboxgroup',
				itemId: 'search_options',
				columns: [105,116],
				items: [{
					boxLabel:   'Partial Match',
					cls: 'ag-form-cb-label',
					name:       'anyMatch',
					inputValue: '1',
					checked:    true
				},{
					boxLabel:   'Case Sensitive',
					cls: 'ag-form-cb-label',
					fieldStyle: 'white-space: nowrap;',
					name:       'caseSensitive',
					inputValue: '1'
				}]
			},{
				style: 'margin:0 5px 5px 5px;',
				xtype: 'textfield',
				itemId: Ag.Def.LOCATION_HASH_SEARCH_KEY,
				emptyText: 'Search',
				listeners: {
					afterrender: function(field, eOpts){

						var filter_items_panel = field.up('panel#filter-items-panel');

						var segment_conditions_panel = field.up('panel#segment-conditions-panel');

						var segment_conditions_radiogroup = segment_conditions_panel.down('radiogroup#search_target');
						segment_conditions_radiogroup.on('change',function(radiogroup){
							field.fireEvent('change',field);
						});

						var segment_conditions_checkboxgroup = segment_conditions_panel.down('checkboxgroup#search_options');
						segment_conditions_checkboxgroup.on('change',function(checkboxgroup){
							field.fireEvent('change',field);
						});

						var temporary_pallet_gridpanel = filter_items_panel.down('gridpanel#temporary-pallet-gridpanel');
						var temporary_pallet_store = temporary_pallet_gridpanel.getStore();
						temporary_pallet_store.on({
							add: function(store){
								field.fireEvent('change',field);
							},
							clear: function(store){
								field.fireEvent('change',field);
							},
							bulkremove: function(store){
								field.fireEvent('change',field);
							}
						});


					},
					change: function( field, newValue, oldValue, eOpts ){
						var segment_conditions_gridpanel = field.next('gridpanel#segment-conditions-gridpanel');
						var temporary_pallet_gridpanel = field.up('panel#search-panel').down('gridpanel#temporary-pallet-gridpanel');

						var hits_label     = segment_conditions_gridpanel.down('tbtext#hits');
						var elements_label = segment_conditions_gridpanel.down('tbtext#elements');
						var polygons_label = segment_conditions_gridpanel.down('tbtext#polygons');
						var segment_conditions_store = segment_conditions_gridpanel.getStore();

						var clearLabel = function(){
							if(hits_label)     hits_label.setText(Ext.String.format('# of hits:{0}','-'));
							if(elements_label) elements_label.setText(Ext.String.format('# of elements:{0}','-'));
							if(polygons_label) polygons_label.setText(Ext.String.format('# of polygons:{0}','-'));
						};

						var value = field.getValue();

						segment_conditions_gridpanel.setLoading(true);

						var filter_items_panel = field.up('panel#filter-items-panel');


						var temp_cdi_cids = [];
						var cdi_ids = {};
						cdi_ids[Ag.Def.LOCATION_HASH_CIDS_KEY] = Ext.JSON.encode(temp_cdi_cids);
						var temporary_pallet_store = temporary_pallet_gridpanel.getStore();
						if(temporary_pallet_store && temporary_pallet_store.getCount()){
							temporary_pallet_store.each(function(record){
								temp_cdi_cids.push(record.get(Ag.Def.CONCEPT_DATA_INFO_DATA_FIELD_ID));
							});
							cdi_ids[Ag.Def.LOCATION_HASH_CIDS_KEY] = Ext.JSON.encode(temp_cdi_cids.sort());
						}

						var p = segment_conditions_store.getProxy();

						if((!value || value.length < 3) || temp_cdi_cids.length == 0){
							segment_conditions_store.removeAll(false);
							segment_conditions_gridpanel.setLoading(false);
							clearLabel();
							p.extraParams = {};
							return;
						}


						var version_combobox = filter_items_panel.down('combobox#version-combobox');
						var version_record = version_combobox.findRecordByValue(version_combobox.getValue());
						var version_data = {};
						version_data[Ag.Def.LOCATION_HASH_MDID_KEY] = version_record.get(Ag.Def.LOCATION_HASH_MDID_KEY);
						version_data[Ag.Def.LOCATION_HASH_MVID_KEY] = version_record.get(Ag.Def.LOCATION_HASH_MVID_KEY);
						version_data[Ag.Def.LOCATION_HASH_MRID_KEY] = version_record.get(Ag.Def.LOCATION_HASH_MRID_KEY);
						version_data[Ag.Def.LOCATION_HASH_CIID_KEY] = version_record.get(Ag.Def.LOCATION_HASH_CIID_KEY);
						version_data[Ag.Def.LOCATION_HASH_CBID_KEY] = version_record.get(Ag.Def.LOCATION_HASH_CBID_KEY);

						var extraParams = Ext.Object.merge({},p.extraParams || {});
						delete extraParams.anyMatch;
						delete extraParams.caseSensitive;
						extraParams = Ext.Object.merge(extraParams, field.prev('checkboxgroup').getValue(), field.prev('radiogroup').getValue(),version_data, cdi_ids );
						extraParams[Ag.Def.LOCATION_HASH_SEARCH_KEY] = value;
						if(Ext.Object.equals(p.extraParams || {},extraParams)){
							segment_conditions_gridpanel.setLoading(false);
							return;
						}
						p.extraParams = extraParams;

						clearLabel();

						segment_conditions_store.loadPage(1,{
							callback: function(records, operation, success){
								if(!success) return;

								var rawData = segment_conditions_store.getProxy().getReader().rawData || {};

								if(hits_label)                                            hits_label.setText(Ext.String.format('# of hits:{0}',Ext.util.Format.number(records.length,'0,000')));
								if(elements_label && Ext.isNumeric(rawData['#elements'])) elements_label.setText(Ext.String.format('# of elements:{0}',Ext.util.Format.number(rawData['#elements'],'0,000')));
								if(polygons_label && Ext.isNumeric(rawData['#polygons'])) polygons_label.setText(Ext.String.format('# of polygons:{0}',Ext.util.Format.number(rawData['#polygons'],'0,000')));

								segment_conditions_gridpanel.setLoading(false);
							}
						});
					}
				}
			},{
				style: 'margin:0 5px 5px 5px;',
				flex: 1,
				xtype: 'gridpanel',
				itemId: 'segment-conditions-gridpanel',
				store: Ext.data.StoreManager.lookup(Ag.Def.CONCEPT_TERM_SEARCH_STORE_ID),
				viewConfig: Ext.apply({
					rowTpl: [
						'{%',
							'var dataRowCls = values.recordIndex === -1 ? "" : " ' + Ext.baseCSSPrefix + 'grid-data-row";',
						'%}',
						'<tr role="row" {[values.rowId ? ("id=\\"" + values.rowId + "\\"") : ""]} ',
							'data-boundView="{view.id}" ',
							'data-recordId="{record.internalId}" ',
							'data-recordIndex="{recordIndex}" ',
							'class="{[values.itemClasses.join(" ")]} {[values.rowClasses.join(" ")]}{[dataRowCls]} term-search-list" ',
							'{rowAttr:attributes} tabIndex="-1">',
							'<tpl for="columns">',
								'{%',
									'parent.view.renderCell(values, parent.record, parent.recordIndex, xindex - 1, out, parent)',
								'%}',
							'</tpl>',
						'</tr>',
						{
							priority: 0
						}
					]
				}, self.getViewConfig()),
				selModel: {
					mode: 'MULTI'
				},
				columns: [
					{ text: Ag.Def.ID_DATA_FIELD_ID,  dataIndex: Ag.Def.SNIPPET_ID_DATA_FIELD_ID, width: 80 },
					{ text: Ag.Def.NAME_DATA_FIELD_ID, dataIndex: Ag.Def.SNIPPET_NAME_DATA_FIELD_ID, flex: 1 },
					{ text: Ag.Def.SYNONYM_DATA_FIELD_ID, dataIndex: Ag.Def.SNIPPET_SYNONYM_DATA_FIELD_ID, flex: 1 }
				],
				plugins: self.getBufferedRenderer({pluginId: 'segment-conditions-gridpanel-plugin'}),
				dockedItems: [{
					xtype: 'toolbar',
					dock: 'top',
					itemId: 'top',
					items: [
						{ xtype: 'tbfill' },
						{ xtype: 'tbseparator'},
						{ xtype: 'tbtext', itemId: 'hits', text: '# of hits:-' },
						{ xtype: 'tbseparator'},
						{ xtype: 'tbtext', itemId: 'elements', text: '# of elements:-' },
						{ xtype: 'tbseparator' },
						{ xtype: 'tbtext', itemId: 'polygons', text: '# of polygons:-' },
						{ xtype: 'tbseparator', hidden: true }
					]
				},{
					xtype: 'toolbar',
					dock: 'bottom',
					itemId: 'bottom',
//					layout: { pack: 'center'},
					defaultType: 'button',
					items: [{
						itemId: 'select_all',
						tooltip: 'Select',
						iconCls: 'pallet_select',
						disabled: false,
						hidden: false,
						listeners: {
							click: function( button ){
								var segment_conditions_gridpanel = button.up('gridpanel#segment-conditions-gridpanel');
								segment_conditions_gridpanel.getSelectionModel().selectAll();
							}
						}
					},{
						itemId: 'deselect_all',
						tooltip: 'Unselect',
						iconCls: 'pallet_unselect',
						disabled: false,
						hidden: false,
						listeners: {
							click: function( button ){
								var segment_conditions_gridpanel = button.up('gridpanel#segment-conditions-gridpanel');
								segment_conditions_gridpanel.getSelectionModel().deselectAll();
							}
						}
					},{
						xtype: 'tbseparator',
						hidden: false
					},{
						xtype: 'tbfill',
						hidden: false
					},{
						xtype: 'tbseparator',
						hidden: false
					},{
						disabled: true,
						tooltip: 'Delete match',
						itemId: 'delete-match',
						iconCls: 'pallet_delete',
						text: 'Match',
						listeners: {
							afterrender: function( button, eOpts ){
								var segment_conditions_gridpanel = button.up('gridpanel#segment-conditions-gridpanel');
/*
								var segment_conditions_store = segment_conditions_gridpanel.getStore();
								segment_conditions_store.on({
									load: function(store){
										button.setDisabled(store.getCount()===0);
									},
									add: function(store){
										button.setDisabled(store.getCount()===0);
									},
									clear: function(store){
										button.setDisabled(store.getCount()===0);
									},
									bulkremove: function(store){
										button.setDisabled(store.getCount()===0);
									},
								});
*/
								var segment_conditions_selmodel = segment_conditions_gridpanel.getSelectionModel();
								segment_conditions_selmodel.on({
									selectionchange: function( selModel, selected, eOpts ){
										button.setDisabled(Ext.isEmpty(selected));
									}
								});


							},
							click: function( button ){
								var search_panel = button.up('panel#search-panel');
								search_panel.setLoading(true);
								var func = function(){
									try{
										var filter_top_panel = button.up('panel#filter-top-panel');

										var segment_conditions_gridpanel = filter_top_panel.down('gridpanel#segment-conditions-gridpanel');
										var segment_conditions_selmodel = segment_conditions_gridpanel.getSelectionModel();
										var segment_conditions_store = segment_conditions_gridpanel.getStore();
										var records = segment_conditions_selmodel.getSelection();
										if(records.length===0){
											button.setDisabled(true);
											search_panel.setLoading(false);
											return;
										}
//										var records = [];
//										if(records.length===0) records = segment_conditions_store.getRange();



										var version_combobox = filter_top_panel.down('combobox#version-combobox');
										var version_record = version_combobox.findRecordByValue(version_combobox.getValue());
										var version = version_record.get(Ag.Def.VERSION_STRING_FIELD_ID);
										if(Ext.isEmpty(Ag.data.renderer[version])) return;

										var ids = Ag.data.renderer[version][Ag.Def.IDS_DATA_FIELD_ID];
										var art_ids = Ag.data.renderer[version][Ag.Def.OBJ_IDS_DATA_FIELD_ID];

										var temporary_pallet_gridpanel = filter_top_panel.down('gridpanel#temporary-pallet-gridpanel');
										var temporary_pallet_selmodel = temporary_pallet_gridpanel.getSelectionModel();
										var temporary_pallet_store = temporary_pallet_gridpanel.getStore();

										var target_ids = {};
										Ext.each(records,function(record){
											var id = record.get(Ag.Def.ID_DATA_FIELD_ID);
											if(Ext.isEmpty(ids[id])) return true;
											if(Ext.isEmpty(ids[id][Ag.Def.OBJ_IDS_DATA_FIELD_ID])) return true;
											Ext.each(ids[id][Ag.Def.OBJ_IDS_DATA_FIELD_ID],function(art_id){
												if(Ext.isEmpty(art_ids[art_id])) return true;
												target_ids[art_ids[art_id][Ag.Def.ID_DATA_FIELD_ID]] = art_id;
											});
										});
										var target_hash = {};
										var target_records = [];
										temporary_pallet_store.each(function(record){
											if(Ext.isEmpty(target_ids[record.get(Ag.Def.ID_DATA_FIELD_ID)])) return true;
											target_records.push(record);

											var id = record.get(Ag.Def.ID_DATA_FIELD_ID);
											target_hash[ id ] = record.getData();
											target_hash[ id ][Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID] = false;

										});

//										self.removeRecords(temporary_pallet_gridpanel.getView(),target_records);
//										self.getFilterRenderer().setObjProperties( self.getFilterObjData( target_hash ) );
//										self.refreshView(temporary_pallet_gridpanel.getView());
										self._removeTemporaryPalletRecords(target_records);

									}catch(e){
										console.error(e);
									}
									search_panel.setLoading(false);
								};
								if(window.setImmediate){
									window.setImmediate(func);
								}else{
									Ext.defer(func,10);
								}

							}
						}
					},{
						xtype: 'tbseparator',
						hidden: false
					},{
						disabled: true,
						tooltip: 'Delete unmatch',
						itemId: 'delete-unmatch',
						iconCls: 'pallet_delete',
						text: 'Unmatch',
						listeners: {
							afterrender: function( button, eOpts ){
								var segment_conditions_gridpanel = button.up('gridpanel#segment-conditions-gridpanel');
/*
								var segment_conditions_store = segment_conditions_gridpanel.getStore();
								segment_conditions_store.on({
									load: function(store){
										button.setDisabled(store.getCount()===0);
									},
									add: function(store){
										button.setDisabled(store.getCount()===0);
									},
									clear: function(store){
										button.setDisabled(store.getCount()===0);
									},
									bulkremove: function(store){
										button.setDisabled(store.getCount()===0);
									},
								});
*/
								var segment_conditions_selmodel = segment_conditions_gridpanel.getSelectionModel();
								segment_conditions_selmodel.on({
									selectionchange: function( selModel, selected, eOpts ){
										button.setDisabled(Ext.isEmpty(selected));
									}
								});
							},
							click: function( button ){
								var search_panel = button.up('panel#search-panel');
								search_panel.setLoading(true);
								var func = function(){
									try{
										var filter_top_panel = button.up('panel#filter-top-panel');
										var segment_conditions_gridpanel = filter_top_panel.down('gridpanel#segment-conditions-gridpanel');
										var segment_conditions_selmodel = segment_conditions_gridpanel.getSelectionModel();
										var segment_conditions_store = segment_conditions_gridpanel.getStore();
										var records = segment_conditions_selmodel.getSelection();
										if(records.length===0){
											button.setDisabled(true);
											search_panel.setLoading(false);
											return;
										}
//										var records = [];
//										if(records.length===0) records = segment_conditions_store.getRange();

										var version_combobox = filter_top_panel.down('combobox#version-combobox');
										var version_record = version_combobox.findRecordByValue(version_combobox.getValue());
										var version = version_record.get(Ag.Def.VERSION_STRING_FIELD_ID);
										if(Ext.isEmpty(Ag.data.renderer[version])) return;

										var ids = Ag.data.renderer[version][Ag.Def.IDS_DATA_FIELD_ID];
										var art_ids = Ag.data.renderer[version][Ag.Def.OBJ_IDS_DATA_FIELD_ID];

										var temporary_pallet_gridpanel = filter_top_panel.down('gridpanel#temporary-pallet-gridpanel');
										var temporary_pallet_selmodel = temporary_pallet_gridpanel.getSelectionModel();
										var temporary_pallet_store = temporary_pallet_gridpanel.getStore();

										var target_ids = {};
										Ext.each(records,function(record){
											var id = record.get(Ag.Def.ID_DATA_FIELD_ID);
											if(Ext.isEmpty(ids[id])) return true;
											if(Ext.isEmpty(ids[id][Ag.Def.OBJ_IDS_DATA_FIELD_ID])) return true;
											Ext.each(ids[id][Ag.Def.OBJ_IDS_DATA_FIELD_ID],function(art_id){
												if(Ext.isEmpty(art_ids[art_id])) return true;
												target_ids[art_ids[art_id][Ag.Def.ID_DATA_FIELD_ID]] = art_id;
											});
										});
										var target_hash = {};
										var target_records = [];
										temporary_pallet_store.each(function(record){
											if(!Ext.isEmpty(target_ids[record.get(Ag.Def.ID_DATA_FIELD_ID)])) return true;
											target_records.push(record);

											var id = record.get(Ag.Def.ID_DATA_FIELD_ID);
											target_hash[ id ] = record.getData();
											target_hash[ id ][Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID] = false;

										});

//										self.removeRecords(temporary_pallet_gridpanel.getView(),target_records);
//										self.getFilterRenderer().setObjProperties( self.getFilterObjData( target_hash ) );
//										self.refreshView(temporary_pallet_gridpanel.getView());

										self._removeTemporaryPalletRecords(target_records);

									}catch(e){
										console.error(e);
									}
									search_panel.setLoading(false);
								};
								if(window.setImmediate){
									window.setImmediate(func);
								}else{
									Ext.defer(func,10);
								}
							}
						}

					}]
				}],
				listeners: {
					afterrender: function( panel, eOpts ){
//						self.bindCellclick(panel);

						var segment_conditions_gridpanel = panel;
						var segment_conditions_selmodel = segment_conditions_gridpanel.getSelectionModel();
						if(segment_conditions_selmodel.getSelectionMode()==='SIMPLE') self.bindCellclick(segment_conditions_selmodel);

					},
					selectionchange: function( selModel, selected, eOpts ){
						var segment_conditions_gridpanel = this;
						var segment_conditions_store = segment_conditions_gridpanel.getStore();
						var filter_items_panel = segment_conditions_gridpanel.up('panel#filter-items-panel');

						var filter_top_panel = self._getFilterPanel();

						var temporary_pallet_gridpanel = filter_top_panel.down('gridpanel#temporary-pallet-gridpanel');
						var temporary_pallet_selmodel = temporary_pallet_gridpanel.getSelectionModel();
						var temporary_pallet_store = temporary_pallet_gridpanel.getStore();
						if(Ext.isEmpty(selected)){
							temporary_pallet_selmodel.deselectAll(false);
							return;
						}


						var version_combobox = filter_top_panel.down('combobox#version-combobox');
						var version_record = version_combobox.findRecordByValue(version_combobox.getValue());
						var version = version_record.get(Ag.Def.VERSION_STRING_FIELD_ID);
						if(Ext.isEmpty(Ag.data.renderer) || Ext.isEmpty(Ag.data.renderer[version])) return;

						var ids = Ag.data.renderer[version][Ag.Def.IDS_DATA_FIELD_ID];
						var art_ids = Ag.data.renderer[version][Ag.Def.OBJ_IDS_DATA_FIELD_ID];
						var use_art_ids = {};
						Ext.each(selected, function(record){
							var id = record.get(Ag.Def.ID_DATA_FIELD_ID);
							if(Ext.isEmpty(ids[id]) || Ext.isEmpty(ids[id][ Ag.Def.OBJ_IDS_DATA_FIELD_ID ])) return;
							Ext.each(ids[id][ Ag.Def.OBJ_IDS_DATA_FIELD_ID ],function(art_id){
								use_art_ids[art_id] = null;
							});
						});

						var select_records = [];
						Ext.Object.each(use_art_ids, function(art_id){
							var record = temporary_pallet_store.findRecord( Ag.Def.OBJ_ID_DATA_FIELD_ID, art_id, 0, false, false, true );
							if(Ext.isEmpty(record)) return true;
							select_records.push(record);
						});

						temporary_pallet_selmodel.select(select_records);

					}
				}
			}]
		},config||{}));
	},

	_removeTemporaryPalletRecords : function(records){
		var self = this;
		var filter_top_panel = self._getFilterPanel();
		var temporary_pallet_gridpanel = filter_top_panel.down('gridpanel#temporary-pallet-gridpanel');
		var temporary_pallet_selmodel = temporary_pallet_gridpanel.getSelectionModel();
		var temporary_pallet_store = temporary_pallet_gridpanel.getStore();

		var temporary_pallet_undo_button = temporary_pallet_gridpanel.down('button#undo');


		self.__removeTemporaryPalletRecords = self.__removeTemporaryPalletRecords || [];
//		self.__removeTemporaryPalletRecords.push(records);
		var __removeTemporaryPalletRecords = [];

		var hash = {};
		Ext.each(records,function(record){
			var id = record.get(Ag.Def.ID_DATA_FIELD_ID);
			hash[ id ] = record.getData();
			hash[ id ][ Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID ] = false;

			__removeTemporaryPalletRecords.push(record.getData());
		});
		self.__removeTemporaryPalletRecords.push(__removeTemporaryPalletRecords);
		temporary_pallet_undo_button.setDisabled(self.__removeTemporaryPalletRecords.length ? false : true);

		self.removeRecords(temporary_pallet_gridpanel.getView(),records);
		self.getFilterRenderer().setObjProperties( self.getFilterObjData( hash ) );
		self.refreshView(temporary_pallet_gridpanel.getView());
	},

	_createTemporaryPalletPanel : function(config){
		var self = this;

		return Ext.create('Ext.panel.Panel', Ext.apply({
			itemId: 'temporary-pallet-panel',
			layout: {
				type: 'vbox',
				align: 'stretch',
				pack: 'cenrer'
			},
//			bodyPadding: '5',
			items: [{
//				height: 20,
				xtype: 'label',
				style: 'font-weight:bold;background-color:#add2ed;padding:2px;',
				text: 'physically selected elements'.toUpperCase()
			},{
//				height: 20,
				xtype: 'label',
				style: 'padding:4px 0 2px 5px;',
				text: 'BP3D Element that overlaps with both specified "segments and concepts".'
			},{
				style: 'margin:5px;',
				flex: 1,
				xtype: 'gridpanel',
				itemId: 'temporary-pallet-gridpanel',
				store: Ext.data.StoreManager.lookup(Ag.Def.CONCEPT_TERM_STORE_ID),
				viewConfig: self.getDropViewConfig(),
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
						width: self.DEF_COLOR_COLUMN_WIDTH,
						hideable: false,
						renderer: function(value){
							return Ext.String.format('<div style="border:1px solid gray;background:{0};width:{1}px;height:{2}px;"> </div>',value,self.DEF_COLOR_COLUMN_WIDTH-22,24-11);
						}
					}
					,{ text: 'Prefecture',  dataIndex: Ag.Def.OBJ_PREFECTURES_FIELD_ID, width: 80 }
					,{ text: 'City',  dataIndex: Ag.Def.OBJ_CITIES_FIELD_ID, width: 80 }
				],
				plugins: self.getBufferedRenderer({pluginId: 'temporary-pallet-gridpanel-plugin'}),
				dockedItems: [{
					xtype: 'toolbar',
					dock: 'top',
					itemId: 'top',
					items: [
						{ xtype: 'tbfill' },
						{ xtype: 'tbseparator'},
						{ xtype: 'tbtext', itemId: 'elements', text: '# of elements:-' },
						{ xtype: 'tbseparator' },
						{ xtype: 'tbtext', itemId: 'polygons', text: '# of polygons:-' },
						{ xtype: 'tbseparator', hidden: true }
					]
				},{
					xtype: 'toolbar',
					dock: 'bottom',
					itemId: 'bottom',
					items: [
						{
							xtype: 'button',
							itemId: 'render',
							text: 'render',
							disabled: true,
							hidden: false,
							listeners: {
								afterrender: function( button, eOpts ){
									var temporary_pallet_store = button.up('gridpanel#temporary-pallet-gridpanel').getStore();
									temporary_pallet_store.on({
										datachanged: function(store, eOpts){
											button.setDisabled(store.getCount()===0);
										}
									});
								},
								click: function( button ){
									var filterRenderer = self.getFilterRenderer();
									filterRenderer.cancelLoadObj(function(){
										var values = self.getFilterObjData();
										filterRenderer.loadObj( values,{ hitfma: values.length });
									});

								}
							}
						},
						{
							xtype: 'tbseparator',
							hidden: false
						},
						{
							itemId: 'select_all',
							tooltip: 'Select',
							iconCls: 'pallet_select',
							disabled: false,
							hidden: false,
							listeners: {
								click: function( button ){
									self.deselectAllSegmentConditionsGridpanel();
									var filter_top_panel = button.up('panel#filter-top-panel');
									var temporary_pallet_gridpanel = filter_top_panel.down('gridpanel#temporary-pallet-gridpanel');
									var temporary_pallet_store = temporary_pallet_gridpanel.getStore();
									var temporary_pallet_selmodel = temporary_pallet_gridpanel.getSelectionModel();
									var selectKeepExisting = temporary_pallet_selmodel.getSelectionMode()==='SIMPLE' ? true : e.ctrlKey;
									temporary_pallet_selmodel.selectAll();
								}
							}
						},{
							itemId: 'deselect_all',
							tooltip: 'Unselect',
							iconCls: 'pallet_unselect',
							disabled: false,
							hidden: false,
							listeners: {
								click: function( button ){
									self.deselectAllSegmentConditionsGridpanel();
									var filter_top_panel = button.up('panel#filter-top-panel');
									var temporary_pallet_gridpanel = filter_top_panel.down('gridpanel#temporary-pallet-gridpanel');
									var temporary_pallet_store = temporary_pallet_gridpanel.getStore();
									var temporary_pallet_selmodel = temporary_pallet_gridpanel.getSelectionModel();
									var selectKeepExisting = temporary_pallet_selmodel.getSelectionMode()==='SIMPLE' ? true : e.ctrlKey;
									temporary_pallet_selmodel.deselectAll();
								}
							}
						},{
							xtype: 'tbseparator',
							hidden: true
						},{
							itemId: 'copy',
							tooltip: 'Copy',
							iconCls: 'pallet_copy',
							disabled: false,
							hidden: true
						},{
							itemId: 'paste',
							tooltip: 'Paste',
							iconCls: 'pallet_paste',
							disabled: false,
							hidden: true
						},{
							xtype: 'tbseparator',
							hidden: false
						},

						{ xtype: 'tbfill' },
						{
							xtype: 'tbseparator',
							hidden: false
						},
						{
							itemId: 'delete',
							tooltip: 'Delete',
							iconCls: 'pallet_delete',
							disabled: true,
							listeners: {
								afterrender: function( button, eOpts ){
									var temporary_pallet_gridpanel = button.up('gridpanel#temporary-pallet-gridpanel');
									temporary_pallet_gridpanel.on('selectionchange',function(selModel,selected){
										button.setDisabled(Ext.isEmpty(selected));
									});
								},
								click: function( button ){
									self.deselectAllSegmentConditionsGridpanel();
									var temporary_pallet_panel = button.up('panel#temporary-pallet-panel');
									temporary_pallet_panel.setLoading(true);
									var func = function(){
										try{
											var filter_top_panel = button.up('panel#filter-top-panel');

											var temporary_pallet_gridpanel = filter_top_panel.down('gridpanel#temporary-pallet-gridpanel');
											var temporary_pallet_selmodel = temporary_pallet_gridpanel.getSelectionModel();
											var records = temporary_pallet_selmodel.getSelection();
											if(Ext.isEmpty(records)) return;
/*
											var hash = {};
											Ext.each(records,function(record){
												var id = record.get(Ag.Def.ID_DATA_FIELD_ID);
												hash[ id ] = record.getData();
												hash[ id ][ Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID ] = false;
											});

											self.removeRecords(temporary_pallet_gridpanel.getView(),records);

											self.getFilterRenderer().setObjProperties( self.getFilterObjData( hash ) );

											self.refreshView(temporary_pallet_gridpanel.getView());
*/
											self._removeTemporaryPalletRecords(records);
										}catch(e){
											console.error(e);
										}
										temporary_pallet_panel.setLoading(false);
									};
									if(window.setImmediate){
										window.setImmediate(func);
									}else{
										Ext.defer(func,10);
									}

								}
							}
						},
						{
							itemId: 'undo',
							tooltip: 'Undo',
							iconCls: 'pallet_undo',
							disabled: true,
							listeners: {
								click: function( button ){
									self.deselectAllSegmentConditionsGridpanel();
									var trash_datas = self.__removeTemporaryPalletRecords.pop();
									if(Ext.isEmpty(trash_datas)){
										button.setDisabled( true );
										return;
									}
									if(Ext.isEmpty(self.__removeTemporaryPalletRecords)) button.setDisabled( true );

									var filter_top_panel = self._getFilterPanel();

									var search_panel = filter_top_panel.down('panel#search-panel');
									search_panel.setLoading(true);

									var temporary_pallet_gridpanel = filter_top_panel.down('gridpanel#temporary-pallet-gridpanel');
									var temporary_pallet_selmodel = temporary_pallet_gridpanel.getSelectionModel();
									var temporary_pallet_store = temporary_pallet_gridpanel.getStore();


									self.addRecords(temporary_pallet_gridpanel.getView(),trash_datas);

									if(self._isFilterAutoRender()){
										var filterRenderer = self.getFilterRenderer();
										filterRenderer.cancelLoadObj(function(){
											var values = self.getFilterObjData();
											filterRenderer.loadObj( values,{ hitfma: values.length });
											filterRenderer.on('load',function(self,successful){
												search_panel.setLoading(false);
											},self,{single:true});
										});
									}else{
										search_panel.setLoading(false);
									}

								}
							}
						},
						{
							xtype: 'tbseparator',
							hidden: true
						},
						{
							xtype: 'tbfill',
							hidden: true
						}
					]
				}],
				listeners: {
					afterrender: function( panel, eOpts ){
						self.bindDrop(panel);
						self.bindCellclick(panel);

						var store = panel.getStore();
						var view = panel.getView();

						var elements_label = panel.down('tbtext#elements');
						var polygons_label = panel.down('tbtext#polygons');
						if(elements_label || elements_label){
							var updateLabel = function(){
								if(elements_label) elements_label.setText(Ext.String.format('# of elements:{0}',Ext.util.Format.number(store.getCount(),'0,000')));
								if(polygons_label) polygons_label.setText(Ext.String.format('# of polygons:{0}',Ext.util.Format.number(store.sum(Ag.Def.OBJ_POLYS_FIELD_ID),'0,000')));
							};
							store.on({
								add: updateLabel,
								clear: updateLabel,
								bulkremove: updateLabel
							});
						}

					},
					selectionchange: function( selModel, selected, eOpts ){
						var gridpanel = this;
						var store = gridpanel.getStore();
						if(store.getCount()){
							var filter_top_panel = self._getFilterPanel();
							var target_gridpanel = filter_top_panel.down('gridpanel#persistent-pallet-gridpanel');
							self._filterGridpanelSelectionchange(gridpanel,target_gridpanel);
						}

						var datas = self.getFilterObjData();
						self.getFilterRenderer().setObjProperties( datas );
					},
					itemclick: function( view, record, item, index, e, eOpts ){
						var gridpanel = this;
						self.deselectAllSegmentConditionsGridpanel();
					}
				}
			}]
		},config||{}));
	},

	deselectAllSegmentConditionsGridpanel : function(){
		var self = this;
		var filter_top_panel = self._getFilterPanel();
		var segment_conditions_gridpanel = filter_top_panel.down('gridpanel#segment-conditions-gridpanel');
		var segment_conditions_selmodel = segment_conditions_gridpanel.getSelectionModel();
		segment_conditions_selmodel.deselectAll(true);
		segment_conditions_gridpanel.down('button#delete-match').setDisabled(true);
		segment_conditions_gridpanel.down('button#delete-unmatch').setDisabled(true);
	},

	_createSearchPanel : function(config){
		var self = this;

		return Ext.create('Ext.panel.Panel', Ext.apply({
			itemId: 'search-panel',
			layout: {
				type: 'vbox',
				align: 'stretch',
				pack: 'start'
			},
			items: [
				self._createTemporaryPalletPanel({flex: 1}),
				self._createSearchConditionsPanel({flex: 1}),

				self._createPersistentPalettePanel({
//					flex: 1
					heigth: 170,
					minHeight: 170,
					maxHeight: 170
				}),

			]
		},config||{}));
	},

	_createTemporaryRenderPanel : function(config){
		var self = this;

		var temporary_render_dockedItems = [self._createRenderTopDocked(Ext.bind(self.getFilterObjData,self))];

		return Ext.create('Ext.panel.Panel', Ext.apply({
			itemId: 'temporary-render-panel',
			dockedItems: temporary_render_dockedItems,
			listeners: {
				afterrender: function(panel, eOpts){

					if(Ext.isEmpty(panel.__webglMainRenderer)){
						var filter_top_panel = self._getFilterPanel();

						var segment_items_panel            = filter_top_panel.down('panel#segment-items-panel');
						var segment_items_top_toolbar      = segment_items_panel.down('toolbar#top');
						var segment_render_longitude_field = segment_items_top_toolbar.down('numberfield#longitude');
						var segment_render_latitude_field  = segment_items_top_toolbar.down('numberfield#latitude');

						var temporary_render_panel           = panel;
						var temporary_render_top_toolbar     = panel.down('toolbar#top');
						var temporary_render_longitude_field = temporary_render_top_toolbar.down('numberfield#longitude');
						var temporary_render_latitude_field  = temporary_render_top_toolbar.down('numberfield#latitude');
						var temporary_render_zoom_field      = temporary_render_top_toolbar.down('numberfield#zoom');
						panel.__webglMainRenderer = new Ag.MainRenderer({
							width:108,
							height:108,
							rate:1,
							minZoom: temporary_render_zoom_field.minValue,
							maxZoom: temporary_render_zoom_field.maxValue,
							backgroundColor: self.DEF_RENDERER_BACKGROUND_COLOR,

							listeners: {
								pick: function(ren,intersects,e){
//									console.log('pick',ren,intersects,e);

//									var filter_top_panel = self._getFilterPanel();
									var temporary_pallet_gridpanel  = filter_top_panel.down('gridpanel#temporary-pallet-gridpanel');
									var temporary_pallet_selmodel   = temporary_pallet_gridpanel.getSelectionModel();
									var temporary_pallet_store      = temporary_pallet_gridpanel.getStore();
									var temporary_pallet_plugin     = temporary_pallet_gridpanel.getPlugin(temporary_pallet_gridpanel.getItemId()+'-plugin');

									var persistent_pallet_gridpanel = filter_top_panel.down('gridpanel#persistent-pallet-gridpanel');
									var persistent_pallet_selmodel  = persistent_pallet_gridpanel.getSelectionModel();
									var persistent_pallet_store     = persistent_pallet_gridpanel.getStore();
									var persistent_pallet_plugin    = persistent_pallet_gridpanel.getPlugin(persistent_pallet_gridpanel.getItemId()+'-plugin');

									var selectKeepExisting = temporary_pallet_selmodel.getSelectionMode()==='SIMPLE' ? true : e.ctrlKey;

									if(Ext.isArray(intersects) && intersects.length){
										var mesh = intersects[0].object;

										var temporary_pallet_record = temporary_pallet_store.findRecord(Ag.Def.OBJ_ID_DATA_FIELD_ID, mesh[ Ag.Def.OBJ_ID_DATA_FIELD_ID ], 0, false, false, true);
										var persistent_pallet_record = persistent_pallet_store.findRecord(Ag.Def.OBJ_ID_DATA_FIELD_ID, mesh[ Ag.Def.OBJ_ID_DATA_FIELD_ID ], 0, false, false, true);
										if(temporary_pallet_record && persistent_pallet_record){
											if(temporary_pallet_selmodel.isSelected(temporary_pallet_record)){
												temporary_pallet_selmodel.deselect(temporary_pallet_record,true);
												persistent_pallet_selmodel.deselect(persistent_pallet_record);
											}
											else if(temporary_pallet_plugin){
												temporary_pallet_plugin.scrollTo( temporary_pallet_store.indexOf(temporary_pallet_record), false, function(){
													temporary_pallet_selmodel.select(temporary_pallet_record,selectKeepExisting,true);
													if(persistent_pallet_plugin){
														persistent_pallet_plugin.scrollTo( persistent_pallet_store.indexOf(persistent_pallet_record), false, function(){
															persistent_pallet_selmodel.select(persistent_pallet_record,selectKeepExisting);
														});
													}else{
														persistent_pallet_selmodel.select(persistent_pallet_record,selectKeepExisting);
													}
												});

											}
											else if(persistent_pallet_plugin){
												temporary_pallet_selmodel.select(temporary_pallet_record,selectKeepExisting,true);
												persistent_pallet_plugin.scrollTo( persistent_pallet_store.indexOf(persistent_pallet_record), false, function(){
													persistent_pallet_selmodel.select(persistent_pallet_record,selectKeepExisting);
												});
											}
											else{
												temporary_pallet_selmodel.select(temporary_pallet_record,selectKeepExisting,true);
												persistent_pallet_selmodel.select(persistent_pallet_record,selectKeepExisting);
											}
										}
										else if(temporary_pallet_record){
											if(temporary_pallet_selmodel.isSelected(temporary_pallet_record)){
												temporary_pallet_selmodel.deselect(temporary_pallet_record);
											}
											else if(temporary_pallet_plugin){
												temporary_pallet_plugin.scrollTo( temporary_pallet_store.indexOf(temporary_pallet_record), false, function(){
													temporary_pallet_selmodel.select(temporary_pallet_record,selectKeepExisting);
												});
											}
											else{
												temporary_pallet_selmodel.select(temporary_pallet_record,selectKeepExisting);
											}
										}
										else if(persistent_pallet_record){
											if(persistent_pallet_selmodel.isSelected(persistent_pallet_record)){
												persistent_pallet_selmodel.deselect(persistent_pallet_record);
											}
											else if(persistent_pallet_plugin){
												persistent_pallet_plugin.scrollTo( persistent_pallet_store.indexOf(persistent_pallet_record), false, function(){
													persistent_pallet_selmodel.select(persistent_pallet_record,selectKeepExisting);
												});
											}
											else{
												persistent_pallet_selmodel.select(persistent_pallet_record,selectKeepExisting);
											}
										}
									}
									else{
										self._filterDeselectAll();
									}
									self.deselectAllSegmentConditionsGridpanel();
								},
								rotate: function(ren,value){
									if(temporary_render_longitude_field){
										if(temporary_render_longitude_field.getValue() !== value.H){
											temporary_render_longitude_field.suspendEvent('change');
											try{
												temporary_render_longitude_field.setValue(value.H);
											}catch(e){
												console.error(e);
											}
											temporary_render_longitude_field.resumeEvent('change');
											if(temporary_render_panel.__webglSubRenderer) temporary_render_panel.__webglSubRenderer.setHorizontal(value.H);
										}
									}
									if(temporary_render_latitude_field){
										if(temporary_render_latitude_field.getValue() !== value.V){
											temporary_render_latitude_field.suspendEvent('change');
											try{
												temporary_render_latitude_field.setValue(value.V);
											}catch(e){
												console.error(e);
											}
											temporary_render_latitude_field.resumeEvent('change');
											if(temporary_render_panel.__webglSubRenderer) temporary_render_panel.__webglSubRenderer.setVertical(value.V);
										}
									}


									if(segment_render_longitude_field){
										if(segment_render_longitude_field.getValue() !== value.H){
											segment_render_longitude_field.suspendEvent('change');
											try{
												segment_render_longitude_field.setValue(value.H);
											}catch(e){
												console.error(e);
											}
											segment_render_longitude_field.resumeEvent('change');
											if(segment_items_panel.__webglMainRenderer) segment_items_panel.__webglMainRenderer.setHorizontal(value.H);
											if(segment_items_panel.__webglSubRenderer) segment_items_panel.__webglSubRenderer.setHorizontal(value.H);
										}
									}
									if(segment_render_latitude_field){
										if(segment_render_latitude_field.getValue() !== value.V){
											segment_render_latitude_field.suspendEvent('change');
											try{
												segment_render_latitude_field.setValue(value.V);
											}catch(e){
												console.error(e);
											}
											segment_render_latitude_field.resumeEvent('change');
											if(segment_items_panel.__webglMainRenderer) segment_items_panel.__webglMainRenderer.setVertical(value.V);
											if(segment_items_panel.__webglSubRenderer) segment_items_panel.__webglSubRenderer.setVertical(value.V);
										}
									}

								},
								zoom: function(ren,value){
									if(temporary_render_zoom_field){
										if(temporary_render_zoom_field.getValue() !== value){
											temporary_render_zoom_field.suspendEvent('change');
											try{
												temporary_render_zoom_field.setValue(value);
											}catch(e){
												console.error(e);
											}
											temporary_render_zoom_field.resumeEvent('change');
										}
									}
								}
							}

						});
					}
					else{
						panel.__webglMainRenderer.domElement().style.display = '';
						panel.__webglMainRenderer.hideAllObj();
					}
					panel.layout.innerCt.dom.appendChild( panel.__webglMainRenderer.domElement() );

					if(Ext.isEmpty(panel.__webglSubRenderer)){
						panel.__webglSubRenderer = new Ag.SubRenderer();
						panel.__webglSubRenderer.domElement.style.position = 'absolute';
						panel.__webglSubRenderer.domElement.style.left = '0px';
						panel.__webglSubRenderer.domElement.style.top = '0px';
						panel.__webglSubRenderer.domElement.style.zIndex = 100;
						panel.__webglSubRenderer.domElement.style.marginRight = '4px';
						panel.__webglSubRenderer.domElement.style.marginBottom = '0px';
						panel.__webglSubRenderer.domElement.style.styleFloat = 'left';
						panel.layout.innerCt.dom.appendChild( panel.__webglSubRenderer.domElement );
						var paths = ['static/obj/body.obj'];
						if(paths.length>0){
							if(panel.__webglSubRenderer) panel.__webglSubRenderer.loadObj(paths);
						}
					}



//					var filter_top_panel = self._getFilterPanel();

					var segment_list_treepanel = filter_top_panel.down('treepanel#segment-list-treepanel');
					var segment_list_treepanel_selmodel = segment_list_treepanel.getSelectionModel();

					var segment_panel = filter_top_panel.down('panel#segment-panel');
					var temporary_pallet_gridpanel = filter_top_panel.down('gridpanel#temporary-pallet-gridpanel');
					var version_combobox = filter_top_panel.down('combobox#version-combobox');
					var search_panel = filter_top_panel.down('panel#search-panel');

					var system_color_view = filter_top_panel.down('dataview#system-color-view');
					var system_color_view_selmodel = system_color_view.getSelectionModel();
					var system_color_view_store = system_color_view.getStore();


					if(
						Ext.isEmpty(segment_list_treepanel)     ||
						Ext.isEmpty(segment_list_treepanel_selmodel)     ||
						Ext.isEmpty(segment_panel)              ||
						Ext.isEmpty(temporary_pallet_gridpanel) ||
						Ext.isEmpty(version_combobox)           ||
						Ext.isEmpty(search_panel)               ||
						Ext.isEmpty(system_color_view)          ||
						Ext.isEmpty(system_color_view_store)    ||
						Ext.isEmpty(system_color_view_selmodel)
					) return;


					if(segment_list_treepanel){

/*
						if(version_combobox){
							version_combobox.on({
								select: function( combobox, records, eOpts ){
									var selModel = segment_list_treepanel.getSelectionModel();
									segment_list_treepanel.fireEvent('selectionchange',selModel,selModel.getSelection(),{});
								},
								buffer:10
							});
						}
*/
						var func = function(/*selModel,selected, eOpts*/){
							try{
								console.time( 'segment_list_treepanel.selectionchange' );


								var selected = segment_list_treepanel_selmodel.getSelection();
								var system_selected = system_color_view_selmodel.getSelection();

								var temporary_pallet_selmodel = temporary_pallet_gridpanel.getSelectionModel();
								var temporary_pallet_store = temporary_pallet_gridpanel.getStore();

								var id_to_art_id = {};

								if(false && Ext.isEmpty(selected)){
									panel.__webglMainRenderer.hideAllObj();
									if(temporary_pallet_store.getCount()) temporary_pallet_store.removeAll();
									segment_panel.setLoading(false);
									console.timeEnd( 'segment_list_treepanel.selectionchange' );
									return;
								}

								if(Ext.isEmpty(Ag.data.SEG2ART) || Ext.isEmpty(Ag.data.renderer)){
									segment_panel.setLoading(false);
									console.timeEnd( 'segment_list_treepanel.selectionchange' );
									return;
								}

								if(
									Ext.isArray(selected) &&
									selected.length &&
									Ext.isArray(system_selected) &&
									system_selected.length
								){


									var system_selected_hash = {};
									Ext.each(system_selected,function(record){
										system_selected_hash[record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID)] = record.getData();
									});
//									console.log(system_selected_hash);


									var version_record = version_combobox.findRecordByValue(version_combobox.getValue());
									var version = version_record.get(Ag.Def.VERSION_STRING_FIELD_ID);
									if(Ext.isEmpty(Ag.data.renderer[version])){
										segment_panel.setLoading(false);
										console.timeEnd( 'segment_list_treepanel.selectionchange' );
										return;
									}

									self.__id_to_art_id = self.__id_to_art_id || {};
									self.__id_to_art_id[version] = self.__id_to_art_id[version] || {};

									var ids = Ag.data.renderer[version][Ag.Def.IDS_DATA_FIELD_ID];
									var art_ids = Ag.data.renderer[version][Ag.Def.OBJ_IDS_DATA_FIELD_ID];

									var segments;

									var segment_list_treeview = segment_list_treepanel.getView();
									Ext.each(segment_list_treepanel.getRootNode().childNodes,function(childNode){
										var isSelected = false;
										Ext.each(childNode.childNodes,function(grandChildNode){
											if(!segment_list_treeview.isSelected(grandChildNode)) return true;
											isSelected = true;
											var segment_arr = grandChildNode.get('segment').split('/');
											if(Ag.data.SEG2ART[segment_arr[0]][segment_arr[1]]){
												segments = segments || {};
												Ext.Object.merge(segments,Ag.data.SEG2ART[segment_arr[0]][segment_arr[1]]);
											}
										});
										if(isSelected) return true;
										if(!segment_list_treeview.isSelected(childNode)) return true;

										var segment_arr = childNode.get('segment').split('/');
										if(Ag.data.SEG2ART[segment_arr[0]][segment_arr[1]]){
											segments = segments || {};
											Ext.Object.merge(segments,Ag.data.SEG2ART[segment_arr[0]][segment_arr[1]]);
										}
									});
									if(Ext.isEmpty(segments)){
										segment_panel.setLoading(false);
										console.timeEnd( 'segment_list_treepanel.selectionchange' );
										return;
									}

									var SEGMENT_LIST_NODES = {};
									var segment_list_store = Ext.data.StoreManager.lookup('segment-list-treestore');
									var segment_list_store_root_node = segment_list_store.getRootNode();
									segment_list_store_root_node.cascadeBy(function(node){
										SEGMENT_LIST_NODES[node.get('segment')] = node;
									});


									Ext.Object.each(segments,function(art_id){
										if(Ext.isEmpty(art_ids[art_id])) return true;

										var id = art_ids[art_id][Ag.Def.ID_DATA_FIELD_ID];
										if(Ext.isEmpty(ids[id])) return true;
	//									if(id == 'FMA72976'){
	//										console.log(id,art_id,ids[id],art_ids[art_id]);
	//									}

										if(Ext.isEmpty(system_selected_hash[ids[id][Ag.Def.SYSTEM_ID_DATA_FIELD_ID]])) return true;


										if(Ext.isObject(self.__id_to_art_id[version][ id ])){
											id_to_art_id[ id ] = Ext.apply({}, self.__id_to_art_id[version][ id ]);
											return true;
										}


										id_to_art_id[ id ] = Ext.apply({},ids[id],art_ids[art_id]);
										delete id_to_art_id[ id ][ Ag.Def.OBJ_IDS_DATA_FIELD_ID ];

										id_to_art_id[ id ][Ag.Def.OBJ_ID_DATA_FIELD_ID] = art_id;

										id_to_art_id[ id ][Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID] = false;

										id_to_art_id[ id ][Ag.Def.CONCEPT_INFO_DATA_FIELD_ID]   = version_record.get( Ag.Def.LOCATION_HASH_CIID_KEY );
										id_to_art_id[ id ][Ag.Def.CONCEPT_BUILD_DATA_FIELD_ID]  = version_record.get( Ag.Def.LOCATION_HASH_CBID_KEY );
										id_to_art_id[ id ][Ag.Def.MODEL_DATA_FIELD_ID]          = version_record.get( Ag.Def.LOCATION_HASH_MDID_KEY );
										id_to_art_id[ id ][Ag.Def.MODEL_VERSION_DATA_FIELD_ID]  = version_record.get( Ag.Def.LOCATION_HASH_MVID_KEY );
										id_to_art_id[ id ][Ag.Def.MODEL_REVISION_DATA_FIELD_ID] = version_record.get( Ag.Def.LOCATION_HASH_MRID_KEY );

										if(Ext.isObject(Ag.data.art_file_info) && Ext.isObject(Ag.data.art_file_info[art_id])){

											id_to_art_id[ id ][Ag.Def.OBJ_FILENAME_FIELD_ID] = Ag.data.art_file_info[art_id][Ag.Def.OBJ_FILENAME_FIELD_ID];
											id_to_art_id[ id ][Ag.Def.OBJ_TIMESTAMP_DATA_FIELD_ID] = Ag.data.art_file_info[art_id][Ag.Def.OBJ_TIMESTAMP_DATA_FIELD_ID];

											id_to_art_id[ id ][Ag.Def.OBJ_X_MIN_FIELD_ID] = Ag.data.art_file_info[art_id][Ag.Def.OBJ_X_MIN_FIELD_ID];
											id_to_art_id[ id ][Ag.Def.OBJ_X_MAX_FIELD_ID] = Ag.data.art_file_info[art_id][Ag.Def.OBJ_X_MAX_FIELD_ID];
											id_to_art_id[ id ][Ag.Def.OBJ_Y_MIN_FIELD_ID] = Ag.data.art_file_info[art_id][Ag.Def.OBJ_Y_MIN_FIELD_ID];
											id_to_art_id[ id ][Ag.Def.OBJ_Y_MAX_FIELD_ID] = Ag.data.art_file_info[art_id][Ag.Def.OBJ_Y_MAX_FIELD_ID];
											id_to_art_id[ id ][Ag.Def.OBJ_Z_MIN_FIELD_ID] = Ag.data.art_file_info[art_id][Ag.Def.OBJ_Z_MIN_FIELD_ID];
											id_to_art_id[ id ][Ag.Def.OBJ_Z_MAX_FIELD_ID] = Ag.data.art_file_info[art_id][Ag.Def.OBJ_Z_MAX_FIELD_ID];
											id_to_art_id[ id ][Ag.Def.OBJ_POLYS_FIELD_ID] = Ag.data.art_file_info[art_id][Ag.Def.OBJ_POLYS_FIELD_ID];
										}

										if(Ext.isObject(Ag.data.MENU_SEGMENTS_in_art_file) && Ext.isObject(Ag.data.MENU_SEGMENTS_in_art_file[art_id])){

											var PREFECTURES = {};
											var CITIES = {};

											Ext.Object.each(Ag.data.MENU_SEGMENTS_in_art_file[art_id],function(key1,value1){
												Ext.Object.each(value1,function(key2,value2){
													var key = [key1,key2].join('/');
													if(Ext.isEmpty(SEGMENT_LIST_NODES[key])) return true;
													var node = SEGMENT_LIST_NODES[key];
													if(key1 == 'PREFECTURES'){
														PREFECTURES[node.get(Ag.Def.SEGMENT_ID_DATA_FIELD_ID)] = node;
													}else if(key1 == 'CITIES'){
														CITIES[node.get(Ag.Def.SEGMENT_ID_DATA_FIELD_ID)] = node;
													}
												});
											});

											id_to_art_id[ id ][Ag.Def.OBJ_PREFECTURES_FIELD_ID] = Object.keys(PREFECTURES).sort().join(',');
											id_to_art_id[ id ][Ag.Def.OBJ_CITIES_FIELD_ID] = Object.keys(CITIES).sort().join(',');

										}

										self.__id_to_art_id[version][ id ] = Ext.apply({}, id_to_art_id[ id ]);

									});

	//								Ext.each(Ext.Object.getKeys(id_to_art_id).sort(),function(id){
	//									console.log(id);
	//								});

								}






								search_panel.setLoading(true);

								var datas = Ext.Object.getValues(id_to_art_id);
								var add_recors;
								if(datas.length){
									temporary_pallet_store.removeAll(true);
									add_recors = self.addRecords(temporary_pallet_gridpanel.getView(),datas);
								}else{
									temporary_pallet_store.removeAll();
									add_recors = [];
								}

								segment_panel.setLoading(false);
								console.timeEnd( 'segment_list_treepanel.selectionchange' );
//								return;

								if(self._isFilterAutoRender()){
									panel.__webglMainRenderer.cancelLoadObj(function(){
										var values = self.getFilterObjData();
										panel.__webglMainRenderer.loadObj( values,{ hitfma: values.length });
										panel.__webglMainRenderer.on('load',function(self,successful){
											search_panel.setLoading(false);
										},self,{single:true});
									});
								}else{
									search_panel.setLoading(false);
								}
							}catch(e){
								console.error(e);
								segment_panel.setLoading(false);
								search_panel.setLoading(false);
							}

						};

						segment_list_treepanel.on('selectionchange',function(selModel,selected, eOpts){
							segment_panel.setLoading(true);
							if(window.setImmediate){
								window.setImmediate(function(){
									func(selModel,selected, eOpts);
								});
							}else{
								Ext.defer(function(){
									func(selModel,selected, eOpts);
								},10);
							}
						},segment_list_treepanel)

						system_color_view.on('selectionchange',function(selModel,selected, eOpts){
							segment_panel.setLoading(true);
							if(window.setImmediate){
								window.setImmediate(function(){
									func(selModel,selected, eOpts);
								});
							}else{
								Ext.defer(function(){
									func(selModel,selected, eOpts);
								},10);
							}
						},system_color_view)



					}
				},
				resize: function( panel, width, height, oldWidth, oldHeight, eOpts){
					panel.__webglMainRenderer._setSize(10,10);

					var $dom = $(panel.layout.innerCt.dom);
					width = $dom.width();
					height = $dom.height();
					panel.__webglMainRenderer.setSize(width,height);
				}
			}
		},config||{}));
	},

	_createDetailedInformationPanel : function(config){
		var self = this;

		return Ext.create('Ext.tab.Panel', Ext.apply({
			itemId: 'detailed-information-panel',
			tabBar : {
				layout: {
					pack : 'end'
				}
			},
			items: [{
				itemId: 'bodyparts3d',
				title: 'BodyParts3D',
				bodyPadding: 5,
				tpl: new Ext.XTemplate(
					'<table>',
					'<tr><td>id</td><td>:</td><td>{id}</td></tr>',
					'<tr><td>name</td><td>:</td><td>{name}</td></tr>',
					'<tr><td>synonym</td><td>:</td><td>{synonym}</td></tr>',
					'<tr><td>definition</td><td>:</td><td>{definition}</td></tr>',
					'</table>',

					'<table>',
					'<tr><td>Prefectures</td><td>:</td><td>{art_prefectures}</td></tr>',
					'<tr><td>City</td><td>:</td><td>{art_cities}</td></tr>',
					'</table>',

					'<table>',
					'<tr><td>Xmin</td><td>:</td><td>{art_xmin}</td></tr>',
					'<tr><td>Xmax</td><td>:</td><td>{art_xmax}</td></tr>',
					'<tr><td>Ymin</td><td>:</td><td>{art_ymin}</td></tr>',
					'<tr><td>Ymax</td><td>:</td><td>{art_ymax}</td></tr>',
					'<tr><td>Zmin</td><td>:</td><td>{art_zmin}</td></tr>',
					'<tr><td>Zmax</td><td>:</td><td>{art_zmax}</td></tr>',
					'<tr><td>LastUpdate</td><td>:</td><td>{[ this.getDate(values.art_timestamp) ]}</td></tr>',
					'</table>',

					{
						getDate: function(value){
							var date = '';
							if(Ext.isDate(value)){
								date = Ext.Date.format(value, 'Y-m-d');
							}
							return date;
						}
					}
				),
				listeners: {
					afterrender: function(panel, eOpts){
						var temporary_pallet_gridpanel = panel.up('panel#filter-items-panel').down('gridpanel#temporary-pallet-gridpanel');
						if(temporary_pallet_gridpanel){
//							console.log(temporary_pallet_gridpanel);
							temporary_pallet_gridpanel.on('selectionchange', function( selModel, selected, eOpts ){
								var gridpanel = this;
								var store = gridpanel.getStore();
								var lastSelected = selModel.getLastSelected();
								if(lastSelected){
//									console.log(lastSelected);
									panel.update(lastSelected.getData());
								}else{
									panel.update({});
								}
							},temporary_pallet_gridpanel);
						}
					}
				}
			},{
				itemId: 'concept_fma',
				title: 'Concept(FMA)'
			}]
		},config||{}));
	},

	_createFilterItemsPanel : function(config){
		var self = this;

		return Ext.create('Ext.panel.Panel', Ext.apply({
			itemId: 'filter-items-panel',
			minHeight: 200,
			layout: {
				type: 'hbox',
				align: 'stretch',
				pack: 'start'
			},
			items: [
				self._createSegmentPanel({flex: 1}),
				self._createTemporaryRenderPanel({flex: 1}),
				self._createSearchPanel({flex: 1}),
//				self._createDetailedInformationPanel({flex: 0.6}),
			],
			listeners: {
			}
		},config||{}));
	},

	_createPersistentPaletteToolbar : function(config){
		var self = this;
		return Ext.create('Ext.toolbar.Toolbar', Ext.apply({
			itemId: 'persistent-palette-toolbar',
			xtype: 'toolbar',
			layout: {
				type: 'vbox',
				align: 'left',
				pack: 'start'
			},

			defaultType: 'button',
			items: [{
				itemId: 'select_all',
				tooltip: 'Select',
				iconCls: 'pallet_select',
				disabled: false,
				listeners: {
					click: function(button){
						var filter_top_panel = button.up('panel#filter-top-panel');
						var persistent_pallet_gridpanel = filter_top_panel.down('gridpanel#persistent-pallet-gridpanel');
						var persistent_pallet_selmodel = persistent_pallet_gridpanel.getSelectionModel();
						persistent_pallet_selmodel.selectAll();
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
						var filter_top_panel = button.up('panel#filter-top-panel');
						var persistent_pallet_gridpanel = filter_top_panel.down('gridpanel#persistent-pallet-gridpanel');
						var persistent_pallet_selmodel = persistent_pallet_gridpanel.getSelectionModel();
						persistent_pallet_selmodel.deselectAll();
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
				hidden: true,
			},{
				xtype: 'tbspacer',
				height: 3,
			},{
				itemId: 'paste',
				tooltip: 'Paste',
				iconCls: 'pallet_paste',
				disabled: true,
				hidden: true,
			},{
				xtype: 'tbfill'
			},{
				itemId: 'delete',
				tooltip: 'Delete',
				iconCls: 'pallet_delete',
				disabled: true,
				listeners: {
					afterrender: function( button, eOpts ){
						var filter_top_panel = button.up('panel#filter-top-panel');
						var persistent_pallet_gridpanel = filter_top_panel.down('gridpanel#persistent-pallet-gridpanel');
						persistent_pallet_gridpanel.on('selectionchange',function(selModel,selected){
							button.setDisabled(Ext.isEmpty(selected));
						});
					},
					click: function(button){
						var persistent_palette_panel = button.up('panel#persistent-palette-panel');
						persistent_palette_panel.setLoading(true);
						var func = function(){
							try{
								var filter_top_panel = button.up('panel#filter-top-panel');

								var persistent_pallet_gridpanel = filter_top_panel.down('gridpanel#persistent-pallet-gridpanel');
								var persistent_pallet_selmodel = persistent_pallet_gridpanel.getSelectionModel();
								var records = persistent_pallet_selmodel.getSelection();
								if(Ext.isEmpty(records)) return;


								var hash = {};
								Ext.each(records,function(record){
									var id = record.get(Ag.Def.ID_DATA_FIELD_ID);
									hash[ id ] = record.getData();
									hash[ id ][ Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID ] = false;
								});

								self.removeRecords(persistent_pallet_gridpanel.getView(),records);

								self.getFilterRenderer().setObjProperties( self.getFilterObjData( hash ) );

								self.refreshView(persistent_pallet_gridpanel.getView());


							}catch(e){
								console.error(e);
							}
							persistent_palette_panel.setLoading(false);
						};
						if(window.setImmediate){
							window.setImmediate(func);
						}else{
							Ext.defer(func,10);
						}
					}
				}
			}]

		},config || {}));
	},

	_createPersistentPaletteGridPanel : function(config){
		var self = this;
		return Ext.create('Ext.grid.Panel', Ext.apply({
			flex: 1,
			xtype: 'gridpanel',
			itemId: 'persistent-pallet-gridpanel',
			store: Ext.data.StoreManager.lookup('persistent-pallet-store'),
			viewConfig: Ext.apply(self.getDropViewConfig(),{
				listeners: {
					colorchange: function(record,value){
						var view = this;
						self.getFilterRenderer().setObjProperties( self.getFilterObjData() );
					}
				}
			}),
			selModel: {
				mode: 'SIMPLE'
			},
			columns: [
				{ text: Ag.Def.ID_DATA_FIELD_ID,  dataIndex: Ag.Def.ID_DATA_FIELD_ID, width: 80 },
				{ text: Ag.Def.NAME_DATA_FIELD_ID, dataIndex: Ag.Def.NAME_DATA_FIELD_ID, flex: 1 },
				{ text: Ag.Def.SYNONYM_DATA_FIELD_ID, dataIndex: Ag.Def.SYNONYM_DATA_FIELD_ID, flex: 1, hidden: true },
/*
				{
					text: self.DEF_COLOR_LABEL,
					dataIndex: Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID,
					width: self.DEF_COLOR_COLUMN_WIDTH,
					hideable: false,
					renderer: function(value){
						return Ext.String.format('<div style="border:1px solid gray;background:{0};width:{1}px;height:{2}px;"> </div>',value,Ag.Def.COLOR_COLUMN_WIDTH-22,24-11);
					}
				}
*/
				{
					text: self.DEF_COLOR_LABEL,
					dataIndex: Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID,
					width: self.DEF_COLOR_COLUMN_WIDTH + 22,
					minWidth: self.DEF_COLOR_COLUMN_WIDTH + 22,
					hidden: false,
					hideable: true,
					xtype: 'agcolorcolumn'
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
				self.getBufferedRenderer({pluginId: 'persistent-pallet-gridpanel-plugin'})
			],
			listeners: {
				afterrender: function( panel, eOpts ){
					self.bindDrop(panel);
					self.bindCellclick(panel);
				},
				selectionchange: function( selModel, selected, eOpts ){

					var gridpanel = this;
					var store = gridpanel.getStore();

					if(store.getCount()){
						var filter_top_panel = self._getFilterPanel();
						var target_gridpanel = filter_top_panel.down('gridpanel#temporary-pallet-gridpanel');
						self._filterGridpanelSelectionchange(gridpanel,target_gridpanel);
					}

					var datas = self.getFilterObjData();
//					console.log(self.getObjDataSelection(datas), datas.length, datas);
					self.getFilterRenderer().setObjProperties( datas );


				}
			}
		},config||{}));
	},

	_createPersistentPalettePanel : function(config){
		var self = this;

//		console.log(config);

		config = Ext.apply({
			itemId: 'persistent-palette-panel',
			minHeight: 200,
			maxHeight: 200,
			height: 200,
//			resizable: true,
//			resizeHandles: 'n',
			layout: {
				type: 'hbox',
				align: 'stretch'
			},
			items: [
				self._createPersistentPaletteToolbar({width: 40}),
				self._createPersistentPaletteGridPanel({flex: 1}),

			{
				width: 100,
//				bodyPadding: 5,
				bodyPadding: '0 0 30 0',
				layout: {
					type: 'vbox',
					align: 'stretch',
					pack: 'start'
				},
				defaults: {
					margin: '30 10 0 10',
				},
				items: [{
					flex: 1,
					xtype: 'button',
					text: 'Download',
					itemId: 'download',
					disabled: true,
					listeners: {
						afterrender: function( button, eOpts ){
							var filter_top_panel = self._getFilterPanel();
							var target_gridpanel = filter_top_panel.down('gridpanel#persistent-pallet-gridpanel');
							if(target_gridpanel){
								target_gridpanel.on('selectionchange', function(selModel, selected, eOpts){
									button.setDisabled(Ext.isEmpty(selected));
								});
							}
						},
						click: function(button){
							var filter_top_panel = self._getFilterPanel();
							var target_gridpanel = filter_top_panel.down('gridpanel#persistent-pallet-gridpanel');
							var target_selmodel = target_gridpanel.getSelectionModel();
							var target_store = target_gridpanel.getStore()
							var records = target_selmodel.getSelection();
							if(Ext.isEmpty(records)){
								button.setDisabled(true);
								return;
							}
							var ids = {};
							Ext.each(records,function(record){
								var id = record.get(Ag.Def.ID_DATA_FIELD_ID);
								ids[ id ] = null;
							});

							var version_combobox = filter_top_panel.down('combobox#version-combobox');
							var version_record = version_combobox.findRecordByValue(version_combobox.getValue());

							var post_data = {};
							post_data[Ag.Def.LOCATION_HASH_MDID_KEY] = version_record.get(Ag.Def.LOCATION_HASH_MDID_KEY);
							post_data[Ag.Def.LOCATION_HASH_MVID_KEY] = version_record.get(Ag.Def.LOCATION_HASH_MVID_KEY);
							post_data[Ag.Def.LOCATION_HASH_MRID_KEY] = version_record.get(Ag.Def.LOCATION_HASH_MRID_KEY);
							post_data[Ag.Def.LOCATION_HASH_CIID_KEY] = version_record.get(Ag.Def.LOCATION_HASH_CIID_KEY);
							post_data[Ag.Def.LOCATION_HASH_CBID_KEY] = version_record.get(Ag.Def.LOCATION_HASH_CBID_KEY);

							post_data[Ag.Def.LOCATION_HASH_IDS_KEY] = Ext.JSON.encode(Ext.Object.getKeys(ids));

							console.log(post_data);

							var $form = $('<form>').attr({
								'action':'download.cgi',
								'method':'POST'
							}).appendTo($(document.body));
							Ext.Object.each(post_data, function(key, value, myself) {
								$('<input>').attr({
									'type':'hidden',
									'name':key
								}).val(value).appendTo($form);
							});
							$form.submit(function(){
								$(this).remove();
							}).get(0).submit();


						}
					}
				},{
					flex: 1,
					xtype: 'button',
					text: 'Map URL',
					itemId: 'map_url',
					disabled: true,
					hidden: true
				}],
				listeners: {
					afterrender: function( panel, eOpts ){
//						console.log(panel.down('toolbar#top'));
//						console.log(panel.down('button#select'));
					}
				}
			}],
			listeners: {
				boxready: {
					fn: function() {
//						delete this.flex;
					},
					single: true
				}
			}
		},config||{});

//		console.log(config);

		return Ext.create('Ext.panel.Panel', config);

	},

	_createTemporaryRenderGridpanel : function(config){
		var self = this;
		config = Ext.apply({
			itemId: 'temporary-render-gridpanel',
			store: Ext.data.StoreManager.lookup('temporary-render-store'),
			viewConfig: self.getDropViewConfig(),
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
					width: self.DEF_COLOR_COLUMN_WIDTH,
					hideable: false,
					renderer: function(value){
						return Ext.String.format('<div style="border:1px solid gray;background:{0};width:{1}px;height:{2}px;"> </div>',value,self.DEF_COLOR_COLUMN_WIDTH-22,24-11);
					}
				}
			],
			plugins: self.getBufferedRenderer({pluginId: 'temporary-render-gridpanel-plugin'}),
			listeners: {
				afterrender: function( panel, eOpts ){
					self.bindDrop(panel);
					self.bindCellclick(panel);
				},
				selectionchange: function( selModel, selected, eOpts ){
					eOpts = eOpts || {};
					if(Ext.isEmpty(eOpts.focusNode)) eOpts.focusNode = true;

					var temporary_render_gridpanel = this;
					var temporary_render_store = temporary_render_gridpanel.getStore();
					var temporary_render_selModel = temporary_render_gridpanel.getSelectionModel();
					var selectKeepExisting = temporary_render_selModel.getSelectionMode()==='SIMPLE' ? true : e.ctrlKey;

					var filter_top_panel = temporary_render_gridpanel.up('panel#filter-top-panel');

					var temporary_pallet_gridpanel = filter_top_panel.down('gridpanel#temporary-pallet-gridpanel');
					var temporary_pallet_store = temporary_pallet_gridpanel.getStore();
					var temporary_pallet_selmodel = temporary_pallet_gridpanel.getSelectionModel();

					var persistent_pallet_gridpanel = filter_top_panel.down('gridpanel#persistent-pallet-gridpanel');
					var persistent_pallet_store = persistent_pallet_gridpanel.getStore();
					var persistent_pallet_selmodel = persistent_pallet_gridpanel.getSelectionModel();

					var temporary_pallet_select_records = [];
					var temporary_pallet_deselect_records = [];

					var persistent_pallet_select_records = [];
					var persistent_pallet_deselect_records = [];

					temporary_render_store.each(function(record){
						var temporary_pallet_record = temporary_pallet_store.findRecord(Ag.Def.ID_DATA_FIELD_ID, record.get(Ag.Def.ID_DATA_FIELD_ID), 0, false, false, true);
						var persistent_pallet_record = persistent_pallet_store.findRecord(Ag.Def.ID_DATA_FIELD_ID, record.get(Ag.Def.ID_DATA_FIELD_ID), 0, false, false, true);
						if(temporary_render_selModel.isSelected(record)){
							if(temporary_pallet_record  && !temporary_pallet_selmodel.isSelected(temporary_pallet_record))   temporary_pallet_select_records.push(temporary_pallet_record);
							if(persistent_pallet_record && !persistent_pallet_selmodel.isSelected(persistent_pallet_record)) persistent_pallet_select_records.push(persistent_pallet_record);
						}
						else{
							if(temporary_pallet_record  && temporary_pallet_selmodel.isSelected(temporary_pallet_record))   temporary_pallet_deselect_records.push(temporary_pallet_record);
							if(persistent_pallet_record && persistent_pallet_selmodel.isSelected(persistent_pallet_record)) persistent_pallet_deselect_records.push(persistent_pallet_record);
						}
					});

					if(temporary_pallet_deselect_records.length || temporary_pallet_select_records.length){
						if(temporary_pallet_deselect_records.length) temporary_pallet_selmodel.deselect(temporary_pallet_deselect_records, true);
						if(temporary_pallet_select_records.length)   temporary_pallet_selmodel.select(temporary_pallet_select_records, selectKeepExisting, true);
						self.refreshView(temporary_pallet_gridpanel.getView());
						if(eOpts.focusNode && temporary_pallet_select_records.length){
							var last_record = temporary_pallet_select_records[temporary_pallet_select_records.length-1];
							var plugin = temporary_pallet_gridpanel.getPlugin('temporary-pallet-gridpanel-plugin');
							if(plugin){
								plugin.scrollTo( temporary_pallet_store.indexOf(last_record) );
							}else{
								temporary_pallet_gridpanel.getView().focusNode( last_record );
							}
						}
						if(window.setImmediate){
							window.setImmediate(function(){
								temporary_pallet_gridpanel.fireEvent('selectionchange', temporary_pallet_selmodel, temporary_pallet_selmodel.getSelection(), {});
							});
						}else{
							Ext.defer(function(){
								temporary_pallet_gridpanel.fireEvent('selectionchange', temporary_pallet_selmodel, temporary_pallet_selmodel.getSelection(), {});
							},10);
						}
					}

					if(persistent_pallet_deselect_records.length || persistent_pallet_select_records.length){
						if(persistent_pallet_deselect_records.length) persistent_pallet_selmodel.deselect(persistent_pallet_deselect_records, true);
						if(persistent_pallet_select_records.length) persistent_pallet_selmodel.select(persistent_pallet_select_records, selectKeepExisting, true);
						self.refreshView(persistent_pallet_gridpanel.getView());
						if(eOpts.focusNode && persistent_pallet_select_records.length){
							var last_record = persistent_pallet_select_records[persistent_pallet_select_records.length-1];
							var plugin = persistent_pallet_gridpanel.getPlugin('persistent-pallet-gridpanel-plugin');
							if(plugin){
								plugin.scrollTo( persistent_pallet_store.indexOf(last_record) );
							}else{
								persistent_pallet_gridpanel.getView().focusNode( last_record );
							}
						}
						if(window.setImmediate){
							window.setImmediate(function(){
								persistent_pallet_gridpanel.fireEvent('selectionchange', persistent_pallet_selmodel, persistent_pallet_selmodel.getSelection(), {});
							});
						}else{
							Ext.defer(function(){
								persistent_pallet_gridpanel.fireEvent('selectionchange', persistent_pallet_selmodel, persistent_pallet_selmodel.getSelection(), {});
							},10);
						}
					}


					var is_selected = false;
					if(Ext.isArray(selected) && selected.length) is_selected = true;

					var panel = temporary_render_gridpanel.up('panel#filter-top-panel').down('panel#temporary-render-panel');
					panel.__webglMainRenderer.setObjProperties(self.getFilterObjDataFromRecord(temporary_render_store.getRange(), selModel, is_selected));

/*
						var lastSelected = selModel.getLastSelected();
						if(lastSelected){
							var bodyparts3d_panel = gridpanel.up('panel#filter-items-panel').down('panel#bodyparts3d');
							var concept_fma_panel = gridpanel.up('panel#filter-items-panel').down('panel#concept_fma');
//							console.log(bodyparts3d_panel,concept_fma_panel);
						}
*/
				}
			}
		},config||{});
		return Ext.create('Ext.grid.Panel', config);
	},

	_createFilterPanel : function(config){
		var self = this;

		var filter_top_panel = Ext.create('Ext.panel.Panel', Ext.apply({
			itemId: 'filter-top-panel',
			title: 'PHYSICAL/SEMANTIC FILTER',
			tabConfig: {
				cls: 'ag-tab-filter'
			},
			defaultType: 'panel',
			layout: {
				type: 'vbox',
				align: 'stretch',
				pack: 'start'
			},
			items: [
				self._createFilterItemsPanel({flex: 1}),
/*
				self._createPersistentPalettePanel({
//					flex: 1
					heigth: 170,
					minHeight: 170,
					maxHeight: 170
				}),
*/
/*
				self._createTemporaryRenderGridpanel({
					hidden: true,
					heigth: 170,
					minHeight: 170,
					maxHeight: 170
				})
*/
			],
			listeners: {
				activate: function( panel, eOpts ){
					var segment_list_treepanel = panel.down('treepanel#segment-list-treepanel');
					if(segment_list_treepanel) self.refreshView(segment_list_treepanel.getView());

					var temporary_pallet_gridpanel = panel.down('gridpanel#temporary-pallet-gridpanel');
					if(temporary_pallet_gridpanel) self.refreshView(temporary_pallet_gridpanel.getView());

					var persistent_pallet_gridpanel = panel.down('gridpanel#persistent-pallet-gridpanel');
					if(persistent_pallet_gridpanel) self.refreshView(persistent_pallet_gridpanel.getView());
				}
			}
		},config||{}));
		return filter_top_panel;
	},

	_getFilterPanel : function(){
		var self = this;
		return self.getViewport().down('panel#filter-top-panel');
	}
});
