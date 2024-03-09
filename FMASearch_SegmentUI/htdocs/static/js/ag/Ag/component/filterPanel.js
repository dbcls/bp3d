Ext.define('Ag.Component.Filter', {
	override: 'Ag.Main',

	__SEGMENT_LIST_CLICK_TO_RENDER : true,

	__DO_NOT_DISPLAY_THE_RECORDS_IN_THE_UNDO_LIST_IN_THE_TEMPPALLET : true,	//アンドゥリストにあるレコードはテンプパレットに表示しない（2017-09-14）

	_getFilterObjDataFromRecord : function(record,is_selected,options){
		var self = this;
//		console.log('_getFilterObjDataFromRecord()',is_selected,options);
		record = record || {};
		var hash = record.getData ? record.getData() : record;

		if(Ext.isBoolean(hash[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID])){

			if(hash[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID]){
				var picked_color = hash[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID];
				var use_picked_color = false;
				if(Ext.isObject(options) && Ext.isObject(options.picked) && Ext.isDefined(options.picked.color)){
					picked_color = options.picked.color;
					use_picked_color = true;
				}
//				else if(self.USE_SELECTION_RENDERER_PICKED_COLOR){
//					picked_color = self.DEF_SELECTION_RENDERER_PICKED_COLOR;
//					use_picked_color = true;
//				}
				var factor;
				if(Ext.isObject(options) && Ext.isObject(options.picked) && Ext.isDefined(options.picked.factor)){
					factor = options.picked.factor;
				}
//				else if(self.USE_SELECTION_RENDERER_PICKED_COLOR_FACTOR){
//					factor = self.DEF_SELECTION_RENDERER_PICKED_COLOR_FACTOR;
//				}
				if(Ext.isDefined(factor)){

					var rgb = d3.rgb( picked_color );
					var grayscale = rgb.r * 0.3 + rgb.g * 0.59 + rgb.b * 0.11;
					var k = grayscale>127.5 ? true : false;

//					if(self.DEF_SELECTION_RENDERER_PICKED_COLOR_FACTOR>0){
					if(factor>0){
//						var factor = self.DEF_SELECTION_RENDERER_PICKED_COLOR_FACTOR;
//						if(!self.USE_SELECTION_RENDERER_PICKED_COLOR) factor += k ? 0 : 0.1;
						if(!use_picked_color) factor += k ? 0 : 0.1;
						picked_color = rgb.brighter(factor).toString();
					}
//					else if(self.DEF_SELECTION_RENDERER_PICKED_COLOR_FACTOR<0){
					else if(factor<0){
//						var factor = self.DEF_SELECTION_RENDERER_PICKED_COLOR_FACTOR * -1;
						factor *= -1;
//						if(!self.USE_SELECTION_RENDERER_PICKED_COLOR) factor += k ? 0 : 0.1;
						if(!use_picked_color) factor += k ? 0 : 0.1;
						picked_color = rgb.darker(factor).toString();
					}
				}

				hash[Ag.Def.PART_REPRESENTATION] = 'surface';
				if(Ext.isObject(options) && Ext.isObject(options.picked) && Ext.isBoolean(options.picked.wireframe) && options.picked.wireframe){
					hash[Ag.Def.PART_REPRESENTATION] = 'wireframe';
					if(Ext.isObject(options) && Ext.isObject(options.picked) && Ext.isDefined(options.picked.color)){
						hash[Ag.Def.PART_WIREFRAME_COLOR] = picked_color;
					}
					else{
						hash[Ag.Def.PART_WIREFRAME_COLOR] = '#000000';
					}
				}
				else{
					hash[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = picked_color;
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

	getTemporaryRenderer : function(){
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
		var store = Ext.data.StoreManager.lookup('version-store');
		var record = null;
		if(Ag.Def.DEF_MODEL_VERSION_TERM) record = store.findRecord('display',Ag.Def.DEF_MODEL_VERSION_TERM,0,false,false,true);
		var value = null;
		if(record){
			value = record.get('value');
			self.DEF_MODEL_VERSION_RECORD = record;
		}else{
			value = store.last().get('value');
			self.DEF_MODEL_VERSION_RECORD = store.last();
		}

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
				store: store,
				queryMode: 'local',
				displayField: 'display',
				valueField: 'value',
				editable: false,
				value: value,
				listeners: {
					afterrender: function(field, eOpts){
//						console.log(field.getStore().getRange());
					},
					select: function( field, records, eOpts ){
						if(Ext.isArray(records) && records.length) self.DEF_MODEL_VERSION_RECORD = record;
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
			itemId: 'segment-list-gridpanel',
			columnLines: true,
			store: Ext.data.StoreManager.lookup('segment-list-store'),
			viewConfig: self.getViewConfig(),
			selModel:{
				selection: 'rowmodel',
				mode: 'SIMPLE'
			},
		}));
	},

	_old_createSegmentListPanel : function(config){
		var self = this;
		return Ext.create('Ext.grid.Panel', Ext.apply({
			itemId: 'segment-list-gridpanel',
			columnLines: true,
			store: Ext.data.StoreManager.lookup('segment-list-store'),
			viewConfig: self.getViewConfig(),
			selModel:{
				selection: 'rowmodel',
				mode: 'SIMPLE'
			},

			hideHeaders: true,
			columns: [{
				xtype: 'numbercolumn',
				format:'0',
				align: 'right',
				width: 25,
				sortable: false,
				dataIndex: Ag.Def.SEGMENT_ID_DATA_FIELD_ID,
				renderer: function(value,metaData,record){
					metaData.style += 'padding:5px 5px 4px;';
					return value;
				}
			},{
				flex: 1,
				dataIndex: 'text',
				renderer: function(value,metaData,record){
					metaData.style += 'padding:5px 5px 4px;';
					return value;
				}
			}],

			dockedItems: [{
				hidden: true,
				xtype: 'toolbar',
				dock: 'top',
				itemId: 'top',
				items: [{xtype:'tbtext',text:'Segment',style:{'font-size':'1.2em','font-weight':'bold','cursor':'default','user-select':'none'}},{
					width: 100,
					editable: false,
					itemId: 'segment-filtering-combobox',
					xtype: 'combobox',
					store: Ext.create('Ext.data.Store', {
						fields: ['value', 'display'],
						data : [
							{"value":"SEG2ART", "display":"All Polygon"},
							{"value":"SEG2ART_INSIDE", "display":"Centroid"}
						]
					}),
					queryMode: 'local',
					displayField: 'display',
					valueField: 'value',
					value: 'SEG2ART',
					listeners: {
						change: function( field, newValue, oldValue, eOpts ){
//							console.log('change()');
						},
						select: function( field, records, eOpts ){
							var filter_top_panel = self._getFilterPanel();
							var segment_list_gridpanel = filter_top_panel.down('gridpanel#segment-list-gridpanel');
							var selModel = segment_list_gridpanel.getSelectionModel();
							var records = selModel.getSelection();
							if(records.length) segment_list_gridpanel.fireEvent('selectionchange',selModel,records,{});
						}
					}
				},'->',{
					itemId: 'select_all',
					iconCls:'pallet_select',
					listeners: {
						click: function(button,e){
							var panel = button.up('treepanel');
							var selModel = panel.getSelectionModel();
							var datas = [];
							selModel.selectAll(true);
/*
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

					if(panel.isXType('gridpanel')){
						var store = panel.getStore();
//						console.log(store.getCount());
						if(store.getCount()){
							panel.fireEvent('load', store, {}, store.getRange(), true);
						}
						else{
							store.on('load',function(store, records, successful, eOpts){
								panel.fireEvent('load', store, {}, records, successful);
							},{single:true});
						}
					}
					if(panel.collapsible) panel.collapse(Ext.Component.DIRECTION_LEFT,false);
				},
				load: function( store, node, records, successful, eOpts ){
					var panel = this;
					var datas = [];
					if(panel.isXType('treepanel')){
						node.cascadeBy(function(node){
							if(Ext.isEmpty(node.get(Ag.Def.OBJ_URL_DATA_FIELD_ID))) return;
							var data = node.getData();
							if(node.getDepth()!==1) data[Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID] = false;
							datas.push(data);
						});
					}
					else if(panel.isXType('gridpanel')){
						panel.getStore().each(function(node){
							if(Ext.isEmpty(node.get(Ag.Def.OBJ_URL_DATA_FIELD_ID))) return;
							datas.push(node.getData());
						});
					}
					if(datas.length){
						var parentPanel = panel.up('panel#segment-items-panel');
						if(parentPanel.rendered){
							parentPanel.__webglMainRenderer.loadObj(datas);
						}else{
							parentPanel.on('afterrender',function(){
								parentPanel.__webglMainRenderer.loadObj(datas);
							},self,{single:true});
						}
					}
				},
				beforeitemcollapse: function(){
					return false;
				},
				deselect: function( selModel, node, index, eOpts ){
					var panel = this;
					var datas = [];

					if(panel.isXType('treepanel')){
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
					}
					else if(panel.isXType('gridpanel')){
						datas.push(node.getData());
					}
					if(datas.length){
						var parentPanel = panel.up('panel#segment-items-panel');
						parentPanel.__webglMainRenderer.setObjProperties(datas);
					}
				},
				select: function( selModel, node, index, eOpts ){
					var panel = this;
					var datas = [];

					if(panel.isXType('treepanel')){

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
					}
					else if(panel.isXType('gridpanel')){
						var data = node.getData();
						data[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID] = true;
						data[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = self.DEF_SELECTION_SEGMENT_RENDERER_PICKED_COLOR;
						datas.push(data);
					}
					if(datas.length){
						var parentPanel = panel.up('panel#segment-items-panel');
						parentPanel.__webglMainRenderer.setObjProperties(datas);
					}
				},
			}
		},config||{}));
	},

	_createSegmentRenderPanel : function(config){
		var self = this;
		return Ext.create('Ext.panel.Panel', Ext.apply({
			itemId: 'segment-render-panel',
			layout: 'fit',
			listeners: {
				afterrender: function(panel, eOpts){
				},
				resize: function( panel, width, height, oldWidth, oldHeight, eOpts){
					var filter_top_panel = self._getFilterPanel();
					var parentPanel = filter_top_panel.down('panel#segment-items-panel');
					if(parentPanel){
						parentPanel.__webglMainRenderer._setSize(10,10);
//						var $dom = $(panel.layout.innerCt.dom);
						var $dom = $(panel.body.dom);
						width = $dom.width();
						height = $dom.height();
						parentPanel.__webglMainRenderer.setSize(width,height);
					}
				}
			}
		},config||{}));
	},

	_createSegmentTabPanel : function(config){
		var self = this;
		return Ext.create('Ext.panel.Panel', Ext.apply({
			itemId: 'segment-tab-panel',
			border: false,
			layout: 'border',
			items: [
				self._createSegmentListPanel({
					title: 'Segment List',
					region: 'west',
					width: 200,
					collapseDirection: 'left',
//					collapsed: true,
					collapsible: true
				}),
				self._createSegmentRenderPanel({region: 'center'}),
			],
			dockedItems: [{
				hidden: false,
				xtype: 'toolbar',
				dock: 'top',
				itemId: 'top',
				items: [{xtype:'tbtext',text:'Segment',style:{'font-size':'1.2em','font-weight':'bold','cursor':'default','user-select':'none'}},{
					width: 100,
					editable: false,
					itemId: 'segment-filtering-combobox',
					xtype: 'combobox',
					store: Ext.create('Ext.data.Store', {
						fields: ['value', 'display'],
						data : [
							{"value":"SEG2ART", "display":"All Polygon"},
							{"value":"SEG2ART_INSIDE", "display":"Centroid"}
						]
					}),
					queryMode: 'local',
					displayField: 'display',
					valueField: 'value',
					value: 'SEG2ART',
					listeners: {
						change: function( field, newValue, oldValue, eOpts ){
//							console.log('change()');
						},
						select: function( field, records, eOpts ){
							var filter_top_panel = self._getFilterPanel();
							var segment_list_gridpanel = filter_top_panel.down('gridpanel#segment-list-gridpanel');
							var selModel = segment_list_gridpanel.getSelectionModel();
							var records = selModel.getSelection();
							if(records.length) segment_list_gridpanel.fireEvent('selectionchange',selModel,records,{});
						}
					}
				},'->',{
					itemId: 'select_all',
					iconCls:'pallet_select',
					listeners: {
						click: function(button,e){
							var filter_top_panel = self._getFilterPanel();
							var panel = filter_top_panel.down('gridpanel#segment-list-gridpanel');
							var selModel = panel.getSelectionModel();
							var datas = [];
							selModel.selectAll(true);
/*
							panel.getRootNode().cascadeBy(function(node){
								var data = node.getData();
								if(node.getDepth()===1) data[Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID] = false;
								data[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID] = true;
								data[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = self.DEF_SELECTION_SEGMENT_RENDERER_PICKED_COLOR;
								datas.push(data);
							});
*/

							var records = [];
							if(panel.isXType('treepanel')){
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
							}
							else if(panel.isXType('gridpanel')){
								panel.getStore().each(function(node){
									records.push(node);
									var data = node.getData();
									data[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID] = true;
									data[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = self.DEF_SELECTION_SEGMENT_RENDERER_PICKED_COLOR;
									datas.push(data);
								});
							}
							if(records.length){
								selModel.select(records,false,true);

								var parentPanel = panel.up('panel#segment-items-panel');
								parentPanel.__webglMainRenderer.setObjProperties(datas);
								panel.fireEvent('selectionchange', selModel, selModel.getSelection(), {});
							}
						}
					}
				},{
					itemId: 'deselect_all',
					iconCls:'pallet_unselect',
					handler: function(button,e){
						var filter_top_panel = self._getFilterPanel();
						var panel = filter_top_panel.down('gridpanel#segment-list-gridpanel');
						var selModel = panel.getSelectionModel();
						selModel.deselectAll(true);
						var datas = [];
						if(panel.isXType('treepanel')){
							panel.getRootNode().cascadeBy(function(node){
								var data = node.getData();
								if(node.getDepth()!==1) data[Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID] = false;
								datas.push(data);
							});
						}
						else if(panel.isXType('gridpanel')){
							panel.getStore().each(function(node){
								datas.push(node.getData());
							});
						}
						if(datas.length){
							var parentPanel = panel.up('panel#segment-items-panel');
							parentPanel.__webglMainRenderer.setObjProperties(datas);
							panel.fireEvent('selectionchange', selModel, selModel.getSelection(), {});
						}
					}
				}]
			}],
			listeners: {
				afterrender: function(panel, eOpts){
				},
				resize: function( panel, width, height, oldWidth, oldHeight, eOpts){
				}
			}
		},config||{}));
	},

	_createSegmentItemsPanel : function(config){
		var self = this;

		var segment_items_dockedItems = [self._createRenderTopDocked({hidden:true})];

//		segment_items_dockedItems[0].items.forEach(function(item){
//			item.hidden = true;
//		});

		segment_items_dockedItems[0].items.unshift('->');
/*
		segment_items_dockedItems[0].items.unshift('-');
		segment_items_dockedItems[0].items.unshift({
			xtype: 'checkbox',
			itemId: 'automatic-rendering-checkbox',
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
					var panel = button.up('panel#segment-items-panel').down('gridpanel#segment-list-gridpanel');
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
					var panel = button.up('panel#segment-items-panel').down('gridpanel#segment-list-gridpanel');
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
//			layout: 'fit',
			border: 0,
			dockedItems: segment_items_dockedItems,
			layout: {
				type: 'hbox',
				align: 'stretch',
				pack: 'start'
			},
			items: [
				self._createSegmentTabPanel({flex: 1}),
//				self._createSegmentListPanel({flex: 0.62}),
//				self._createSegmentRenderPanel({flex: 1}),

//				self._createSegmentListPanel({flex: 1}),
//				self._createSegmentListPanel({flex: 1, hidden: true}),
//				self._createSystemColorPanel({flex: 1})
				self._createSystemColorPanel({width: 132})
			],
			listeners: {
				afterrender: function(panel, eOpts){

					var segment_list_gridpanel = panel.down('gridpanel#segment-list-gridpanel');
					var selModel = segment_list_gridpanel.getSelectionModel();
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
//							console.log(view);
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

									var childPanel = panel.down('gridpanel#segment-list-gridpanel');
									var childPanelView = childPanel.getView();

									var urlBASAL_STEM = {};

									if(childPanel.isXType('treepanel')){
										var current_date = new Date();
										if(Ext.isDate(panel.__lastPickDate)){
											var dt = Ext.Date.add(panel.__lastPickDate, Ext.Date.MILLI, self.DEF_DOUBLE_CLICK_INTERVAL);
											is_dblclick = Ext.Date.between(current_date,panel.__lastPickDate, dt);
										}
										panel.__lastPickDate = current_date;


										childPanel.getRootNode().cascadeBy(function(node){
											var text = node.get('text').toUpperCase().replace(/^[0-9_]+/g,'');
											if(text==='BASAL' || text==='STEM'){
												urlBASAL_STEM[node.get(Ag.Def.OBJ_URL_DATA_FIELD_ID)] = node;
											}
										});
									}
									else if(childPanel.isXType('gridpanel')){
										childPanel.getStore().each(function(node){
											var text = node.get('text').toUpperCase().replace(/^[0-9_]+/g,'');
											if(text==='BASAL' || text==='STEM'){
												urlBASAL_STEM[node.get(Ag.Def.OBJ_URL_DATA_FIELD_ID)] = node;
											}
										});
										is_dblclick = false;
									}


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

//										var childPanel = panel.down('gridpanel#segment-list-gridpanel');
//										var childPanelView = childPanel.getView();
//										var rootNode = childPanel.getRootNode();

										var childNodes = [];
										if(childPanel.isXType('treepanel')){
											var rootNode = childPanel.getRootNode();
											Ext.each(meshs,function(mesh){
												var childNode = rootNode.findChild(Ag.Def.OBJ_ID_DATA_FIELD_ID, mesh[Ag.Def.OBJ_ID_DATA_FIELD_ID], true);
												if(childNode) childNodes.push(childNode);
											});
										}
										else if(childPanel.isXType('gridpanel')){
											var store = childPanel.getStore();
											Ext.each(meshs,function(mesh){
												var childNode = store.findRecord(Ag.Def.OBJ_ID_DATA_FIELD_ID, mesh[Ag.Def.OBJ_ID_DATA_FIELD_ID], 0, false, false, true);
//												console.log('childNode',childNode);
												if(childNode) childNodes.push(childNode);
											});
										}
//										console.log(is_dblclick, childNodes);
//										Ext.each(childNodes,function(childNode){
//											console.log(childNode.get('text'));
//										});

										if(childNodes.length){
											if(childPanel.isXType('treepanel')){
												if(is_dblclick){
													pickDelayedTask.cancel();
													dblclickFunc.apply(self,[childNodes,childPanelView,e]);
												}else{
													pickDelayedTask.delay(self.DEF_DOUBLE_CLICK_INTERVAL,null,null,[childNodes,childPanelView,e]);
												}
											}
											else if(childPanel.isXType('gridpanel')){
												pickDelayedTask.delay(0,null,null,[childNodes,childPanelView,e]);
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

//					var childPanel = panel.down('panel#segment-render-panel');
					var childPanel = filter_top_panel.down('panel#segment-render-panel');
					if(childPanel.rendered){
//						childPanel.layout.innerCt.dom.appendChild( panel.__webglMainRenderer.domElement() );
						childPanel.body.dom.appendChild( panel.__webglMainRenderer.domElement() );
					}else{
						childPanel.on('afterrender',function(){
//							childPanel.layout.innerCt.dom.appendChild( panel.__webglMainRenderer.domElement() );
							childPanel.body.dom.appendChild( panel.__webglMainRenderer.domElement() );
						},self,{single:true});
					}





/*
					segment_render_longitude_field.on('change',function(field,value){
						console.log(value);
					});
					segment_render_latitude_field.on('change',function(field,value){
						console.log(value);
					});
*/

				}
			}
		},config||{}));
	},

	_createSystemColorPanel_old : function(config){
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
						var segment_list_gridpanel = filter_top_panel.down('gridpanel#segment-list-gridpanel');
						var version_combobox = filter_top_panel.down('combobox#version-combobox');
						var segment_panel = filter_top_panel.down('panel#segment-panel');

						var system_color_view = view;
						var system_color_view_selmodel = system_color_view.getSelectionModel();
						var system_color_view_store = system_color_view.getStore();

						if(
							Ext.isEmpty(segment_list_gridpanel) ||
							Ext.isEmpty(version_combobox)       ||
							Ext.isEmpty(segment_panel)          ||
							Ext.isEmpty(system_color_view_store) ||
							Ext.isEmpty(system_color_view_selmodel)
						) return;

						version_combobox.on({
							select: function( combobox, records, eOpts ){
								var selModel = segment_list_gridpanel.getSelectionModel();
								segment_list_gridpanel.fireEvent('selectionchange',selModel,selModel.getSelection(),{});
							},
							buffer:10
						});

						var end_func = function(){
							segment_panel.setLoading(false);
//							console.timeEnd( 'segment_list_gridpanel.selectionchange' );
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
//							console.time( 'segment_list_gridpanel.selectionchange' );

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

								var segment_list_gridview = segment_list_gridpanel.getView();
								Ext.each(segment_list_gridpanel.getRootNode().childNodes,function(childNode){
									var isSelected = false;
									Ext.each(childNode.childNodes,function(grandChildNode){
										if(!segment_list_gridview.isSelected(grandChildNode)) return true;
										isSelected = true;
										var segment_arr = grandChildNode.get('segment').split('/');
										if(Ag.data.SEG2ART[segment_arr[0]][segment_arr[1]]){
											segments = segments || {};
											Ext.Object.merge(segments,Ag.data.SEG2ART[segment_arr[0]][segment_arr[1]]);
										}
									});
									if(isSelected) return true;
									if(!segment_list_gridview.isSelected(childNode)) return true;

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
								var segment_list_store = Ext.data.StoreManager.lookup('segment-list-store');
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

						segment_list_gridpanel.on('selectionchange',function(selModel,selected, eOpts){
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
						},segment_list_gridpanel)


//					},
//					selectionchange: function(selModel, selected){
//						console.log(selModel, selected);
					}
				}
			})
		},config||{}));
	},

	_createSystemColorPanel : function(config){
		var self = this;
		return Ext.create('Ext.grid.Panel', Ext.apply({
			itemId: 'system-color-gridpanel',

			store: Ext.data.StoreManager.lookup('system-list-store'),
			hideHeaders: true,
			columns: [
				{
					text: 'text',
					dataIndex: 'text',
					flex: 1,
					minWidth: 98,
					hideable: false,
					renderer: function(value,metaData,record){
////						console.log(record.get(Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID));
////						metaData.style += 'background-color:'+record.get(Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID)+';';
//						metaData.style += 'padding:5px 5px 4px;';

//						metaData.style += 'padding:1px 2px;margin:3px;';
						metaData.style += 'border:1px solid #ddd;padding:2px 2px;margin:1px 2px;';
						metaData.style += 'background-color:'+record.get(Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID)+';';
						if(Ext.draw.Color.fromString(record.get(Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID)).getGrayscale()<128) metaData.style += 'color:#FFFFFF;';

						return value;
					}
				},
				{
					text: self.DEF_COLOR_LABEL,
					dataIndex: Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID,
					width: self.DEF_COLOR_COLUMN_WIDTH,
					hidden: true,
					hideable: false,
					renderer: function(value){
						return Ext.String.format('<div style="border:1px solid gray;background:{0};width:{1}px;height:{2}px;"> </div>',value,self.DEF_COLOR_COLUMN_WIDTH-22,24-11);
					}
				},
				{
					text: 'element',
					dataIndex: 'element_count',
					xtype: 'numbercolumn',
					format:'0,000',
					align: 'right',
					width: 32,
					hideable: false,
					renderer: function(value,metaData,record){

//						metaData.style += 'border:1px solid black;padding:1px 2px;margin:2px;';
//						metaData.style += 'background-color:'+record.get(Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID)+';';
//						if(Ext.draw.Color.fromString(record.get(Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID)).getGrayscale()<128) metaData.style += 'color:#FFFFFF;';

						metaData.style += 'padding:1px 2px;margin:3px;';

						return value;
					}
				}
			],
			dockedItems: [{
				xtype: 'toolbar',
				dock: 'top',
				itemId: 'top',
				items: [{
					xtype:'tbtext',
					text:'System',
					style:{'font-size':'1.2em','font-weight':'bold','cursor':'default','user-select':'none'}
				},
//				'->',
				{
					itemId: 'select_all',
					tooltip: 'Select',
					iconCls: 'pallet_select',
					disabled: false,
					listeners: {
						click: function(button){
//							var system_color_view = button.up('panel#system-color-panel').down('dataview#system-color-view');
							var system_color_view = button.up('gridpanel#system-color-gridpanel');
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
//							var system_color_view = button.up('panel#system-color-panel').down('dataview#system-color-view');
							var system_color_view = button.up('gridpanel#system-color-gridpanel');
							var system_color_view_selmodel = system_color_view.getSelectionModel();
							system_color_view_selmodel.deselectAll();
						}
					}
				}]
			}],
			selModel: {
				mode: 'SIMPLE'
			},
			listeners: {
				afterrender: function(view, eOpts){
					var filter_top_panel = self._getFilterPanel();
					var segment_list_gridpanel = filter_top_panel.down('gridpanel#segment-list-gridpanel');
					var version_combobox = filter_top_panel.down('combobox#version-combobox');
					var segment_panel = filter_top_panel.down('panel#segment-panel');

					var system_color_view = view;
					var system_color_view_selmodel = system_color_view.getSelectionModel();
					var system_color_view_store = system_color_view.getStore();

					if(
						Ext.isEmpty(segment_list_gridpanel) ||
						Ext.isEmpty(version_combobox)       ||
						Ext.isEmpty(segment_panel)          ||
						Ext.isEmpty(system_color_view_store) ||
						Ext.isEmpty(system_color_view_selmodel)
					) return;

					version_combobox.on({
						select: function( combobox, records, eOpts ){
							var selModel = segment_list_gridpanel.getSelectionModel();
							segment_list_gridpanel.fireEvent('selectionchange',selModel,selModel.getSelection(),{});
						},
						buffer:10
					});

					var end_func = function(){
						segment_panel.setLoading(false);
//						console.timeEnd( 'segment_list_gridpanel.selectionchange' );
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
//						console.log('segment_list_gridpanel.selectionchange');
//						console.time( 'segment_list_gridpanel.selectionchange' );

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
							var filter_top_panel = self._getFilterPanel();
							var segment_filtering_combobox = filter_top_panel.down('combobox#segment-filtering-combobox');
							var SEG2ART = segment_filtering_combobox.getValue()==='SEG2ART' ? Ag.data.SEG2ART : Ag.data.SEG2ART_INSIDE;

							var segments;

							var segment_list_gridview = segment_list_gridpanel.getView();
/*
							Ext.each(segment_list_gridpanel.getRootNode().childNodes,function(childNode){
								var isSelected = false;
								Ext.each(childNode.childNodes,function(grandChildNode){
									if(!segment_list_gridview.isSelected(grandChildNode)) return true;
									isSelected = true;
									var segment_arr = grandChildNode.get('segment').split('/');
									if(SEG2ART[segment_arr[0]][segment_arr[1]]){
										segments = segments || {};
										Ext.Object.merge(segments,SEG2ART[segment_arr[0]][segment_arr[1]]);
									}
								});
								if(isSelected) return true;
								if(!segment_list_gridview.isSelected(childNode)) return true;

								var segment_arr = childNode.get('segment').split('/');
								if(SEG2ART[segment_arr[0]][segment_arr[1]]){
									segments = segments || {};
									Ext.Object.merge(segments,SEG2ART[segment_arr[0]][segment_arr[1]]);
								}
							});
*/
							segment_list_gridpanel.getStore().each(function(childNode){
								if(!segment_list_gridview.isSelected(childNode)) return true;
//								console.log('childNode',childNode);
								var segment_arr = childNode.get('segment').split('/');
								if(SEG2ART[segment_arr[0]][segment_arr[1]]){
									segments = segments || {};
									Ext.Object.merge(segments,SEG2ART[segment_arr[0]][segment_arr[1]]);
								}
							});
//							console.log('segments',segments);

							if(Ext.isEmpty(segments)){
								interrupt_func();
								return;
							}
//								console.log(segments);

/*
							var SEGMENT_LIST_NODES = {};
							var segment_list_store = Ext.data.StoreManager.lookup('segment-list-store');
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

					segment_list_gridpanel.on('selectionchange',function(selModel,selected, eOpts){
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
					},segment_list_gridpanel)


//					},
//					selectionchange: function(selModel, selected){
//						console.log(selModel, selected);
				}
			}
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
//				self._createSystemColorPanel({height:200})
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
				pack: 'center'
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
						var segment_conditions_selmodel = segment_conditions_gridpanel.getSelectionModel();
						segment_conditions_selmodel.deselectAll();

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
					{ text: Ag.Def.ID_DATA_FIELD_ID,  dataIndex: Ag.Def.SNIPPET_ID_DATA_FIELD_ID, width: Ag.Def.ID_DATA_FIELD_WIDTH },
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
//										self.getTemporaryRenderer().setObjProperties( self.getFilterObjData( target_hash ) );
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
//										self.getTemporaryRenderer().setObjProperties( self.getFilterObjData( target_hash ) );
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

						panel.getView().on({
							itemkeydown: function(view, record, item, index, e, eOpts){
								if(e.getKey()===e.C && (e.ctrlKey || e.metaKey)){
									var columns = [
										{ text: Ag.Def.ID_DATA_FIELD_ID,  dataIndex: Ag.Def.ID_DATA_FIELD_ID, width: Ag.Def.ID_DATA_FIELD_WIDTH },
										{ text: Ag.Def.NAME_DATA_FIELD_ID, dataIndex: Ag.Def.NAME_DATA_FIELD_ID, flex: 1 },
										{ text: Ag.Def.SYNONYM_DATA_FIELD_ID, dataIndex: Ag.Def.SYNONYM_DATA_FIELD_ID, flex: 1 }
									];
									self.copyGridColumnsText(view,columns);
								}
							}
						});
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

						temporary_pallet_selmodel.select(select_records,false,true);
						temporary_pallet_gridpanel.fireEvent('selectionchange',temporary_pallet_selmodel,select_records, {});

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

//		var temporary_pallet_undo_button = temporary_pallet_gridpanel.down('button#undo');


		self.__removeTemporaryPalletRecords = self.__removeTemporaryPalletRecords || [];
//		self.__removeTemporaryPalletRecords.push(records);
		var removeTemporaryPalletRecords = [];

		var hash = {};
		Ext.each(records,function(record){
			var id = record.get(Ag.Def.ID_DATA_FIELD_ID);
			hash[ id ] = record.getData();
			hash[ id ][ Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID ] = false;

			removeTemporaryPalletRecords.push(record.getData());
		});
		self.__removeTemporaryPalletRecords.push(removeTemporaryPalletRecords);
//		temporary_pallet_undo_button.setDisabled(self.__removeTemporaryPalletRecords.length ? false : true);
		self.fireEvent('addRemoveTemporaryPalletRecords');

		self.removeRecords(temporary_pallet_gridpanel.getView(),records);
		self.getTemporaryRenderer().setObjProperties( self.getFilterObjData( hash ) );
		self.refreshView(temporary_pallet_gridpanel.getView());
	},

	_createTemporaryPalletPanel : function(config){
		var self = this;

		var relation_column_renderer = function(value, metaData, record, rowIdx, colIdx, store) {
			if(Ext.isString(value) && value.length){
				value = Ext.util.Format.nl2br(value);
				metaData.tdAttr = 'data-qtip="' + value + '"';
			}
			return value;
		};

		var get_relation_column = function(dataIndex, hidden){
			return {
				text: dataIndex,
				tooltip: dataIndex,
				dataIndex: dataIndex,
				flex: 1,
				hidden: hidden,
				hideable: true,
				renderer: relation_column_renderer
			};
		};

		return Ext.create('Ext.panel.Panel', Ext.apply({
			itemId: 'temporary-pallet-panel',
			layout: {
				type: 'vbox',
				align: 'stretch',
				pack: 'center'
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
					{ text: Ag.Def.ID_DATA_FIELD_ID,  dataIndex: Ag.Def.ID_DATA_FIELD_ID, width: Ag.Def.ID_DATA_FIELD_WIDTH, renderer: relation_column_renderer },
					{ text: Ag.Def.NAME_DATA_FIELD_ID, dataIndex: Ag.Def.NAME_DATA_FIELD_ID, flex: 1, renderer: relation_column_renderer },
					{ text: Ag.Def.SYNONYM_DATA_FIELD_ID, dataIndex: Ag.Def.SYNONYM_DATA_FIELD_ID, flex: 1, hidden: true, renderer: relation_column_renderer },
					{
						text: self.DEF_COLOR_LABEL,
						dataIndex: Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID,
						width: self.DEF_COLOR_COLUMN_WIDTH,
						hideable: true,
						renderer: function(value,metaData){
							metaData.tdAttr = 'data-qtip="' + value + '"';
							return Ext.String.format('<div style="border:1px solid gray;background:{0};width:{1}px;height:{2}px;"> </div>',value,self.DEF_COLOR_COLUMN_WIDTH-22,24-11);
						}
					}
					,{ text: 'Prefecture',  dataIndex: Ag.Def.OBJ_PREFECTURES_FIELD_ID, width: 80, hidden: true, hideable: false }
					,{
//						text: 'City',
						text: 'Segment',
						dataIndex: Ag.Def.OBJ_CITIES_FIELD_ID,
						width: 80
					}
					,get_relation_column('is_a',false)
					,get_relation_column('regional_part_of',false)
					,get_relation_column('constitutional_part_of',false)
					,get_relation_column('branch_of',true)
					,get_relation_column('member_of',false)
					,get_relation_column('systemic_part_of',true)
					,get_relation_column('arterial_supply_of',true)
					,get_relation_column('tributary_of',true)
					,get_relation_column('lexicalsuper',false)

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
									var temporaryRenderer = self.getTemporaryRenderer();
									temporaryRenderer.cancelLoadObj(function(){
										var values = self.getFilterObjData();
										temporaryRenderer.loadObj( values,{ hitfma: values.length });
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

											self.getTemporaryRenderer().setObjProperties( self.getFilterObjData( hash ) );

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
						'-',
						{
							itemId: 'undo',
							tooltip: 'Undo',
							iconCls: 'pallet_undo',
							disabled: true,
							listeners: {
								afterrender: function( b, eOpts ){
									self.on({
										addRemoveTemporaryPalletRecords: function(){
											b.setDisabled(self.__removeTemporaryPalletRecords.length ? false : true);
										},
										removeRemoveTemporaryPalletRecords: function(){
											b.setDisabled(self.__removeTemporaryPalletRecords.length ? false : true);
										}
									});
								},
								click: function( button ){
									self.deselectAllSegmentConditionsGridpanel();
									var trash_datas = self.__removeTemporaryPalletRecords.pop();
									self.fireEvent('removeRemoveTemporaryPalletRecords');
									if(Ext.isEmpty(trash_datas)){
//										button.setDisabled( true );
										return;
									}
//									if(Ext.isEmpty(self.__removeTemporaryPalletRecords)) button.setDisabled( true );

									var filter_top_panel = self._getFilterPanel();

									var search_panel = filter_top_panel.down('panel#search-panel');
									search_panel.setLoading(true);

									var temporary_pallet_gridpanel = filter_top_panel.down('gridpanel#temporary-pallet-gridpanel');
									var temporary_pallet_selmodel = temporary_pallet_gridpanel.getSelectionModel();
									var temporary_pallet_store = temporary_pallet_gridpanel.getStore();


									self.addRecords(temporary_pallet_gridpanel.getView(),trash_datas);

									if(self._isFilterAutoRender()){
										var temporaryRenderer = self.getTemporaryRenderer();
										temporaryRenderer.cancelLoadObj(function(){
											var values = self.getFilterObjData();
											temporaryRenderer.setAutoFocus( false );
											temporaryRenderer.loadObj( values,{ hitfma: values.length });
											temporaryRenderer.on('load',function(self,successful){
												search_panel.setLoading(false);
												temporaryRenderer.setAutoFocus( true );
											},self,{single:true});
										});
									}else{
										search_panel.setLoading(false);
									}

								}
							}
						},
						{
							hidden: !self.__DO_NOT_DISPLAY_THE_RECORDS_IN_THE_UNDO_LIST_IN_THE_TEMPPALLET,
							itemId: 'undo_list',
							tooltip: 'Undo list',
							iconCls: 'pallet_undo_list',
							disabled: true,
							listeners: {
								afterrender: function( b, eOpts ){
//									return;
									self.on({
										addRemoveTemporaryPalletRecords: function(){
											b.setDisabled(self.__removeTemporaryPalletRecords.length ? false : true);
										},
										removeRemoveTemporaryPalletRecords: function(){
											b.setDisabled(self.__removeTemporaryPalletRecords.length ? false : true);
										}
									});
								},
								click: function( b ){
									var delete_button = b;//.prev('button#delete');
									if(Ext.isEmpty(b.__window)){
										b.__window = Ext.create('Ext.Window', {
											title: b.text || b.tooltip,
											iconCls: b.iconCls,
											animateTarget: null,//delete_button ? delete_button.el : null,
											constrain: true,
											constrainTo: self._getFilterPanel().body,
											itemId: 'undo-list',
											width: 530,
											height: 350,
											layout: 'fit',
											items: [{
												xtype: 'gridpanel',
												store: Ext.create('Ext.data.Store', {
													model: 'Ag.data.Model.CONCEPT_TERM_PALLET',
													remoteSort: false,
													sorters: [{
														property: Ag.Def.NAME_DATA_FIELD_ID,
														direction: 'ASC'
													}]
												}),
//												viewConfig: self.getDropViewConfig(),
												viewConfig: self.getViewConfig(),
												selModel: {
													mode: 'SIMPLE'
												},
												columns: [
													{ text: Ag.Def.ID_DATA_FIELD_ID,  dataIndex: Ag.Def.ID_DATA_FIELD_ID, width: Ag.Def.ID_DATA_FIELD_WIDTH },
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
													items: [{
														itemId: 'select_all',
														tooltip: 'Select',
														iconCls: 'pallet_select',
														disabled: false,
														hidden: false,
														listeners: {
															click: function( b ){
																var gridpanel = b.up('gridpanel');
																var store = gridpanel.getStore();
																var selmodel = gridpanel.getSelectionModel();
																gridpanel.getView().saveScrollState();
																selmodel.selectAll();
																gridpanel.getView().restoreScrollState();
															}
														}
													},{
														itemId: 'deselect_all',
														tooltip: 'Unselect',
														iconCls: 'pallet_unselect',
														disabled: false,
														hidden: false,
														listeners: {
															click: function( b ){
																var gridpanel = b.up('gridpanel');
																var store = gridpanel.getStore();
																var selmodel = gridpanel.getSelectionModel();
																gridpanel.getView().saveScrollState();
																selmodel.deselectAll();
																gridpanel.getView().restoreScrollState();
															}
														}
													},'->',{
														itemId: 'delete',
														tooltip: 'Delete',
														iconCls: 'pallet_delete',
														disabled: true,
														listeners: {
															afterrender: function( b ){
																var gridpanel = b.up('gridpanel');
																gridpanel.on('selectionchange',function(selModel,selected){
																	b.setDisabled(Ext.isEmpty(selected));
																});

																b._clearUndoList = function(b){

																	var gridpanel = b.up('gridpanel');
																	var selmodel = gridpanel.getSelectionModel();
																	var records = selmodel.getSelection();
																	if(Ext.isEmpty(records)) return;

																	var remove_ids = {};
																	Ext.Array.each(records,function(record,i){
																		remove_ids[record.get(Ag.Def.ID_DATA_FIELD_ID)] = record;
																	});

																	var removeTemporaryPalletRecords = self.__removeTemporaryPalletRecords.reverse();
																	self.__removeTemporaryPalletRecords = [];
																	Ext.Array.each(removeTemporaryPalletRecords, function(remove_datas,i){
																		var remove_index = [];
																		Ext.Array.each(remove_datas,function(remove_data,j){
																			if(Ext.isEmpty(remove_ids[remove_data[Ag.Def.ID_DATA_FIELD_ID]])) return true;
																			remove_index.push(j);
																		});
																		if(Ext.isEmpty(remove_index)){
																			self.__removeTemporaryPalletRecords.unshift(remove_datas);
																			return true;
																		}

																		Ext.Array.each(remove_index.reverse(),function(j){
																			Ext.Array.erase(remove_datas,j,1);
																		});
																		if(Ext.isEmpty(remove_datas)) return true;
																		self.__removeTemporaryPalletRecords.unshift(remove_datas);
																	});

																	var trash_datas = records.map(function(record){ return record.getData(); });

																	var store = gridpanel.getStore();
																	store.remove(records);

																	self.fireEvent('removeRemoveTemporaryPalletRecords');

																	return trash_datas;
																};
															},
															click: function( b ){
																b._clearUndoList(b);
															}
														}
													},{
														itemId: 'undo',
														tooltip: 'Undo',
														iconCls: 'pallet_undo',
														disabled: true,
														listeners: {
															afterrender: function( b, eOpts ){
																var gridpanel = b.up('gridpanel');
																gridpanel.on('selectionchange',function(selModel,selected){
																	b.setDisabled(Ext.isEmpty(selected));
																});
															},
															click: function( b ){
																var trash_datas = b.prev('button#delete')._clearUndoList(b);

																self.deselectAllSegmentConditionsGridpanel();

																var filter_top_panel = self._getFilterPanel();
																var temporary_pallet_gridpanel = filter_top_panel.down('gridpanel#temporary-pallet-gridpanel');
																var temporary_pallet_selmodel = temporary_pallet_gridpanel.getSelectionModel();
																var temporary_pallet_store = temporary_pallet_gridpanel.getStore();

																self.addRecords(temporary_pallet_gridpanel.getView(),trash_datas);

																if(self._isFilterAutoRender()){
																	var temporaryRenderer = self.getTemporaryRenderer();
																	temporaryRenderer.cancelLoadObj(function(){
																		var values = self.getFilterObjData();
																		temporaryRenderer.setAutoFocus( false );
																		temporaryRenderer.loadObj( values,{ hitfma: values.length });
																		temporaryRenderer.on('load',function(self,successful){
																			search_panel.setLoading(false);
																			temporaryRenderer.setAutoFocus( true );
																		},self,{single:true});
																	});
																}

															}
														}
													}]
												}]
											}],
											listeners: {
												afterrender: function( comp, eOpts ){
//													console.log('afterrender');
													comp._reload = function(){
														var gridpanel = comp.down('gridpanel');
														var store = gridpanel.getStore();
														if(Ext.isArray(self.__removeTemporaryPalletRecords) && self.__removeTemporaryPalletRecords.length){
															var remove_ids = {};
															Ext.Array.each(self.__removeTemporaryPalletRecords,function(remove_datas){
																Ext.Array.each(remove_datas,function(remove_data){
																	if(Ext.isEmpty(remove_ids[remove_data[Ag.Def.ID_DATA_FIELD_ID]])) remove_ids[remove_data[Ag.Def.ID_DATA_FIELD_ID]] = Ext.Object.merge({},remove_data);
																});
															});
															store.removeAll(true);
															self.addRecords(gridpanel.getView(),Ext.Object.getKeys(remove_ids).map(function(key){return remove_ids[key]}));
														}else{
															store.removeAll(false);
														}
														var elements_label = gridpanel.down('tbtext#elements');
														var polygons_label = gridpanel.down('tbtext#polygons');
														if(elements_label) elements_label.setText(Ext.String.format('# of elements:{0}',Ext.util.Format.number(store.getCount(),'0,000')));
														if(polygons_label) polygons_label.setText(Ext.String.format('# of polygons:{0}',Ext.util.Format.number(store.sum(Ag.Def.OBJ_POLYS_FIELD_ID),'0,000')));
													};
													self.on('addRemoveTemporaryPalletRecords', comp._reload);
													self.on('removeRemoveTemporaryPalletRecords', comp._reload);
													comp._reload();
												},
												beforeshow: function( comp, eOpts ){
//													console.log('beforeshow');
												},
												close: function( comp, eOpts ){
													self._getFilterPanel().remove(b.__window);
												},
												destroy: function( comp, eOpts ){
//													console.log('destroy');

													self.un('addRemoveTemporaryPalletRecords', comp._reload);
													self.un('removeRemoveTemporaryPalletRecords', comp._reload);

													delete comp._reload;
													delete b.__window;
												}
											}
										});
										self._getFilterPanel().add(b.__window);
									}
									if(delete_button){
										b.__window.showBy(delete_button,'tr-br?');
									}else{
										b.__window.show();
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

						view.on({
							itemkeydown: function(view, record, item, index, e, eOpts){
								if(e.getKey()===e.C && (e.ctrlKey || e.metaKey)){
									self.copyGridColumnsText(view);
								}
							}
						});

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
						self.getTemporaryRenderer().setObjProperties( datas );
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

		var temporary_render_dockedItems = [self._createRenderTopDocked({},Ext.bind(self.getFilterObjData,self),Ext.bind(self._getFilterPanel,self))];

		var constrainedWin = Ext.create('Ext.Window', {
//			title: 'Segment Window',
			header: false,
			resizable: true,
			resizeHandles: 's e se',
			width: 48 * 2,
			height: 96 * 2,
			minWidth: 48 * 2,
			minHeight: 96 * 2,

			x: 0,
			y: 0,
			constrain: true,
			closable: false,
			layout: 'fit',
//			items: self._createSegmentRenderPanel()
		});

		return Ext.create('Ext.panel.Panel', Ext.apply({
			itemId: 'temporary-render-panel',
			layout: 'fit',
			dockedItems: temporary_render_dockedItems,
//			items: constrainedWin,
			listeners: {
				afterrender: function(panel, eOpts){
//					constrainedWin.show();

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
//					panel.layout.innerCt.dom.appendChild( panel.__webglMainRenderer.domElement() );
					panel.body.dom.appendChild( panel.__webglMainRenderer.domElement() );

/*
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
*/


//					var filter_top_panel = self._getFilterPanel();

					var segment_list_gridpanel = filter_top_panel.down('gridpanel#segment-list-gridpanel');
					var segment_list_gridpanel_selmodel = segment_list_gridpanel.getSelectionModel();

					var segment_panel = filter_top_panel.down('panel#segment-panel');
					var temporary_pallet_gridpanel = filter_top_panel.down('gridpanel#temporary-pallet-gridpanel');
					var version_combobox = filter_top_panel.down('combobox#version-combobox');
					var search_panel = filter_top_panel.down('panel#search-panel');

//					var system_color_view = filter_top_panel.down('dataview#system-color-view');
					var system_color_view = filter_top_panel.down('gridpanel#system-color-gridpanel');
					var system_color_view_selmodel = system_color_view.getSelectionModel();
					var system_color_view_store = system_color_view.getStore();


					if(
						Ext.isEmpty(segment_list_gridpanel)     ||
						Ext.isEmpty(segment_list_gridpanel_selmodel)     ||
						Ext.isEmpty(segment_panel)              ||
						Ext.isEmpty(temporary_pallet_gridpanel) ||
						Ext.isEmpty(version_combobox)           ||
						Ext.isEmpty(search_panel)               ||
						Ext.isEmpty(system_color_view)          ||
						Ext.isEmpty(system_color_view_store)    ||
						Ext.isEmpty(system_color_view_selmodel)
					) return;


					if(segment_list_gridpanel){

/*
						if(version_combobox){
							version_combobox.on({
								select: function( combobox, records, eOpts ){
									var selModel = segment_list_gridpanel.getSelectionModel();
									segment_list_gridpanel.fireEvent('selectionchange',selModel,selModel.getSelection(),{});
								},
								buffer:10
							});
						}
*/
						var func = function(/*selModel,selected, eOpts*/){
							try{
//								console.time( 'segment_list_gridpanel.selectionchange' );


								var selected = segment_list_gridpanel_selmodel.getSelection();
								var system_selected = system_color_view_selmodel.getSelection();

								var temporary_pallet_selmodel = temporary_pallet_gridpanel.getSelectionModel();
								var temporary_pallet_store = temporary_pallet_gridpanel.getStore();

								var id_to_art_id = {};

								if(false && Ext.isEmpty(selected)){
									panel.__webglMainRenderer.hideAllObj();
									if(temporary_pallet_store.getCount()) temporary_pallet_store.removeAll();
									segment_panel.setLoading(false);
//									console.timeEnd( 'segment_list_gridpanel.selectionchange' );
									return;
								}

								if(Ext.isEmpty(Ag.data.SEG2ART) || Ext.isEmpty(Ag.data.renderer)){
									segment_panel.setLoading(false);
//									console.timeEnd( 'segment_list_gridpanel.selectionchange' );
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
//										console.timeEnd( 'segment_list_gridpanel.selectionchange' );
										return;
									}

									self.__id_to_art_id = self.__id_to_art_id || {};
									self.__id_to_art_id[version] = self.__id_to_art_id[version] || {};

									var ids = Ag.data.renderer[version][Ag.Def.IDS_DATA_FIELD_ID];
									var art_ids = Ag.data.renderer[version][Ag.Def.OBJ_IDS_DATA_FIELD_ID];

									var filter_top_panel = self._getFilterPanel();
									var segment_filtering_combobox = filter_top_panel.down('combobox#segment-filtering-combobox');
									var segment_filtering = segment_filtering_combobox.getValue();
									var SEG2ART = segment_filtering==='SEG2ART' ? Ag.data.SEG2ART : Ag.data.SEG2ART_INSIDE;

									self.__id_to_art_id[version][segment_filtering] = self.__id_to_art_id[version][segment_filtering] || {};

									var segments;

									var segment_list_gridview = segment_list_gridpanel.getView();
									if(segment_list_gridpanel.isXType('treepanel')){
										Ext.each(segment_list_gridpanel.getRootNode().childNodes,function(childNode){
											var isSelected = false;
											Ext.each(childNode.childNodes,function(grandChildNode){
												if(!segment_list_gridview.isSelected(grandChildNode)) return true;
												isSelected = true;
												var segment_arr = grandChildNode.get('segment').split('/');
												if(SEG2ART[segment_arr[0]][segment_arr[1]]){
													segments = segments || {};
													Ext.Object.merge(segments,SEG2ART[segment_arr[0]][segment_arr[1]]);
												}
											});
											if(isSelected) return true;
											if(!segment_list_gridview.isSelected(childNode)) return true;

											var segment_arr = childNode.get('segment').split('/');
											if(SEG2ART[segment_arr[0]][segment_arr[1]]){
												segments = segments || {};
												Ext.Object.merge(segments,SEG2ART[segment_arr[0]][segment_arr[1]]);
											}
										});
									}
									else if(segment_list_gridpanel.isXType('gridpanel')){
										segment_list_gridpanel.getStore().each(function(childNode){
											if(!segment_list_gridview.isSelected(childNode)) return true;
											var segment_arr = childNode.get('segment').split('/');
											if(SEG2ART[segment_arr[0]][segment_arr[1]]){
												segments = segments || {};
												Ext.Object.merge(segments,SEG2ART[segment_arr[0]][segment_arr[1]]);
											}
										});
									}

									if(Ext.isEmpty(segments)){
										segment_panel.setLoading(false);
//										console.timeEnd( 'segment_list_gridpanel.selectionchange' );
										return;
									}

									var SEGMENT_LIST_NODES = {};
									if(segment_list_gridpanel.isXType('treepanel')){
										var segment_list_store = Ext.data.StoreManager.lookup('segment-list-store');
										var segment_list_store_root_node = segment_list_store.getRootNode();
										segment_list_store_root_node.cascadeBy(function(node){
											SEGMENT_LIST_NODES[node.get('segment')] = node;
										});
									}
									else if(segment_list_gridpanel.isXType('gridpanel')){
										segment_list_gridpanel.getStore().each(function(node){
											SEGMENT_LIST_NODES[node.get('segment')] = node;
										});
									}


									Ext.Object.each(segments,function(art_id){
										if(Ext.isEmpty(art_ids[art_id])) return true;

										var id = art_ids[art_id][Ag.Def.ID_DATA_FIELD_ID];
										if(Ext.isEmpty(ids[id])) return true;
	//									if(id == 'FMA72976'){
	//										console.log(id,art_id,ids[id],art_ids[art_id]);
	//									}

										if(Ext.isEmpty(system_selected_hash[ids[id][Ag.Def.SYSTEM_ID_DATA_FIELD_ID]])) return true;


										if(Ext.isObject(self.__id_to_art_id[version][segment_filtering][ id ])){
											id_to_art_id[ id ] = Ext.apply({}, self.__id_to_art_id[version][segment_filtering][ id ]);
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
													if(segment_filtering!=='SEG2ART' && !value2.inside) return true;
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

										self.__id_to_art_id[version][segment_filtering][ id ] = Ext.apply({}, id_to_art_id[ id ]);

									});

	//								Ext.each(Ext.Object.getKeys(id_to_art_id).sort(),function(id){
	//									console.log(id);
	//								});

								}

								if(self.__DO_NOT_DISPLAY_THE_RECORDS_IN_THE_UNDO_LIST_IN_THE_TEMPPALLET){	//アンドゥリストにあるレコードはテンプパレットに表示しない（2017-09-14）
									if(Ext.Object.getKeys(id_to_art_id).length && Ext.isArray(self.__removeTemporaryPalletRecords) && self.__removeTemporaryPalletRecords.length){
										var remove_ids = {};
										Ext.Array.each(self.__removeTemporaryPalletRecords,function(remove_datas){
											Ext.Array.each(remove_datas,function(remove_data){
												remove_ids[remove_data[Ag.Def.ID_DATA_FIELD_ID]] = true;
											});
										});
										if(Ext.Object.getKeys(remove_ids).length){
											Ext.Object.each(id_to_art_id, function(key, value){
												if(remove_ids[key]) delete id_to_art_id[key];
											});
										}
									}
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
//								console.timeEnd( 'segment_list_gridpanel.selectionchange' );
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

						segment_list_gridpanel.on('selectionchange',function(selModel,selected, eOpts){
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
						},segment_list_gridpanel)

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

//					var $dom = $(panel.layout.innerCt.dom);
					var $dom = $(panel.body.dom);
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

								self.getTemporaryRenderer().setObjProperties( self.getFilterObjData( hash ) );

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
						self.getTemporaryRenderer().setObjProperties( self.getFilterObjData() );
					}
				}
			}),
			selModel: {
				mode: 'SIMPLE'
			},
			columns: [
				{ text: Ag.Def.ID_DATA_FIELD_ID,  dataIndex: Ag.Def.ID_DATA_FIELD_ID, width: Ag.Def.ID_DATA_FIELD_WIDTH },
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
					var store = panel.getStore();
					store.view = panel.getView();
					self.bindDrop(panel);
					self.bindCellclick(panel);

					store.view.on({
						itemkeydown: function(view, record, item, index, e, eOpts){
							if(e.getKey()===e.C && (e.ctrlKey || e.metaKey)){
								self.copyGridColumnsText(view);
							}
						}
					});

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
					self.getTemporaryRenderer().setObjProperties( datas );


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
				{ text: Ag.Def.ID_DATA_FIELD_ID,  dataIndex: Ag.Def.ID_DATA_FIELD_ID, width: Ag.Def.ID_DATA_FIELD_WIDTH },
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


					self.getTemporaryRenderer().setObjProperties(self.getFilterObjDataFromRecord(temporary_render_store.getRange(), selModel, is_selected));
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
					var segment_list_gridpanel = panel.down('gridpanel#segment-list-gridpanel');
					if(segment_list_gridpanel) self.refreshView(segment_list_gridpanel.getView());

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
