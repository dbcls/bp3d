Ext.define('Ag.Component.Canvas.Renderer', {
	override: 'Ag.Main',

	getCanvasRenderer : function(){
		var self = this;
		var canvas_top_panel = self._getCanvasPanel();
		var panel = canvas_top_panel.down('panel#canvas-renderer-panel');
		return panel.__webglMainRenderer;
	},

	_createCanvasRendererPanel : function(config){
		var self = this;
		var dockedItems = [self._createRenderTopDocked({},Ext.bind(self.getCanvasObjData,self),Ext.bind(self._getCanvasPanel,self))];
		return Ext.create('Ext.panel.Panel', Ext.apply({
//			flex: 1,
//			title: 'Renderer',
			layout: {
				type: 'vbox',
				align: 'stretch',
				pack: 'start'
			},
			items: [{
				flex: 1,
				itemId: 'canvas-renderer-panel',
				layout: 'fit',
				dockedItems: dockedItems,
				listeners: {
					afterrender: function(panel, eOpts){
//						return;

						var cenvas_panel = self._getCanvasPanel();
						var pallet_gridpanel = cenvas_panel.down('gridpanel#canvas-pallet-gridpanel');

						if(Ext.isEmpty(panel.__webglMainRenderer)){

							var pickDelayedTask =  new Ext.util.DelayedTask(function(record){
								var gridpanel = pallet_gridpanel;
								var selModel = gridpanel.getSelectionModel();
								selModel.deselect([record]);
							});

							var dblclickFunc =  function(record,e){
								return;
								var conceptParentStore = Ext.data.StoreManager.lookup(AgDef.CONCEPT_PARENT_TERM_STORE_ID);
								var params = {};
								params[AgDef.LOCATION_HASH_CID_KEY] = record.get(AgDef.LOCATION_HASH_ID_KEY);
								Ext.Ajax.abortAll();
								conceptParentStore.loadPage(1,{
									params: params,
									callback: function(records,operation,success){
		//								console.log(this);
		//								console.log(success,operation,records);
									}
								});
							}

							var zoom_field = panel.down('toolbar#top').down('numberfield#zoom');
							panel.__webglMainRenderer = new Ag.MainRenderer({
								width:108,
								height:108,
								rate:1,
								minZoom: zoom_field.minValue,
								maxZoom: zoom_field.maxValue,
								backgroundColor: self.DEF_RENDERER_BACKGROUND_COLOR,

								listeners: {
									pick: function(ren,intersects,e){
	//									console.log('pick',ren,intersects,e);

										if(self._isCanvasInformationActiveTabPinPanel()){
//											console.log('pick',ren,intersects,e);
											if(Ext.isArray(intersects) && intersects.length){
												self._addCanvasPinDataFromPick(ren,intersects);
											}
											return;
										}
										if(self._isCanvasInformationActiveTabNeighborPartsPanel()){
//											console.log('pick',ren,intersects,e);
											if(Ext.isArray(intersects) && intersects.length){
												self._searchCanvasNeighborPartsFromPick(ren,intersects);
											}
//											return;
										}
										else{
											if(!self._isCanvasInformationActiveTabPalletPanel()){
												self._setCanvasInformationActiveTabPalletPanel();
											}
										}

										var gridpanel = pallet_gridpanel;
										var store = gridpanel.getStore();
										var selModel = gridpanel.getSelectionModel();
										var selectKeepExisting = selModel.getSelectionMode()==='SIMPLE' ? true : e.ctrlKey;

										var is_dblclick = false;
										if(selModel){
											if(Ext.isDate(self.__lastPickDate)) delete self.__lastPickDate;
										}else{
											var current_date = new Date();
											if(Ext.isDate(self.__lastPickDate)){
												var dt = Ext.Date.add(self.__lastPickDate, Ext.Date.MILLI, self.DEF_DOUBLE_CLICK_INTERVAL);
												is_dblclick = Ext.Date.between(current_date,self.__lastPickDate, dt);
											}
											self.__lastPickDate = current_date;
										}

										if(Ext.isArray(intersects) && intersects.length){
											var mesh = intersects[0].object;

											var recordIdx = store.find( Ag.Def.OBJ_ID_DATA_FIELD_ID, mesh[Ag.Def.OBJ_ID_DATA_FIELD_ID], 0, false, false, true );
											if(recordIdx>=0){
												var record = store.getAt(recordIdx);
												if(selModel.isSelected(record)){
													if(is_dblclick){
														pickDelayedTask.cancel();
		//												console.log(e);
														dblclickFunc(record,e);
													}else{
														if(selectKeepExisting){
															selModel.deselect([record]);
														}else{
															pickDelayedTask.delay(self.DEF_DOUBLE_CLICK_INTERVAL,null,null,[record]);
		//												selModel.deselect([record]);
														}
													}
												}else{
													var plugin = null;
													if(self._isCanvasInformationActiveTabPalletPanel()) plugin = gridpanel.getPlugin(gridpanel.itemId+'-plugin');
													if(plugin){
														try{
															plugin.scrollTo( recordIdx, false, function(recordIdx,record){
																selModel.select([record],selectKeepExisting);
															}, self );
														}catch(e){
															console.error(e);
															selModel.select([record],selectKeepExisting);
														}
													}else{
														selModel.select([record],selectKeepExisting);
													}
												}
											}
										}
										else{
											selModel.deselectAll();
										}
									},
									rotate: function(ren,value){
		//								console.log('rotate',value);
										var longitude_field = panel.down('toolbar#top').down('numberfield#longitude');
										var latitude_field = panel.down('toolbar#top').down('numberfield#latitude');
		//								console.log('rotate',value,longitude_field.getValue(),latitude_field.getValue());
										if(longitude_field){
											if(longitude_field.getValue() !== value.H){
												longitude_field.suspendEvent('change');
												try{
													longitude_field.setValue(value.H);
		//											console.log('rotate',longitude_field.getValue());
												}catch(e){
													console.error(e);
												}
												longitude_field.resumeEvent('change');
												if(panel.__webglSubRenderer) panel.__webglSubRenderer.setHorizontal(value.H);
											}
										}
										if(latitude_field){
											if(latitude_field.getValue() !== value.V){
												latitude_field.suspendEvent('change');
												try{
													latitude_field.setValue(value.V);
		//											console.log('rotate',latitude_field.getValue());
												}catch(e){
													console.error(e);
												}
												latitude_field.resumeEvent('change');
												if(panel.__webglSubRenderer) panel.__webglSubRenderer.setVertical(value.V);
											}
										}
									},
									zoom: function(ren,value){
		//								console.log('zoom',value);
										var zoom_field = panel.down('toolbar#top').down('numberfield#zoom');
										if(zoom_field){
											if(zoom_field.getValue() !== value){
												zoom_field.suspendEvent('change');
												try{
													zoom_field.setValue(value);
		//											console.log('zoom',zoom_field.getValue());
												}catch(e){
													console.error(e);
												}
												zoom_field.resumeEvent('change');
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
//						panel.layout.innerCt.dom.appendChild( panel.__webglMainRenderer.domElement() );
						panel.body.dom.appendChild( panel.__webglMainRenderer.domElement() );

						if(Ext.isEmpty(panel.__webglSubRenderer)){
							panel.__webglSubRenderer = new Ag.SubRenderer();
							$(panel.__webglSubRenderer.domElement).css({
//								position: 'absolute',
								position: 'relative',
								left: 0,
								top: 0,
								zIndex: 100,
								marginRight: 4,
								marginBottom: 0,
								'float': 'left'
							});
//							panel.layout.innerCt.dom.appendChild( panel.__webglSubRenderer.domElement );
//							panel.body.dom.appendChild( panel.__webglSubRenderer.domElement );

//							panel.__webglMainRenderer.domElement().appendChild( panel.__webglSubRenderer.domElement );

							$(panel.__webglMainRenderer.domElement()).children('canvas').after($(panel.__webglSubRenderer.domElement));


							var paths = ['static/obj/body.obj'];
							if(paths.length>0){
								if(panel.__webglSubRenderer) panel.__webglSubRenderer.loadObj(paths);
							}
						}

						var pallet_store = pallet_gridpanel && pallet_gridpanel.getStore ? pallet_gridpanel.getStore() : null;
						if(pallet_store){
							pallet_store.on({
								load: function(store, records, successful, eOpts){
	//								console.log('load', records, successful, eOpts);
								},
								add: function(store, records, index, eOpts){
	//								console.log('add', records, index, eOpts);
									panel.__webglMainRenderer.loadObj(self.getObjDataFromRecords(store.getRange(),pallet_gridpanel.getSelectionModel()),{hitfma:store.getCount()});
								},
								clear: function(store, eOpts){
	//								console.log('clear', eOpts);
									panel.__webglMainRenderer.hideAllObj();
								},
								bulkremove: function(store, records, indexes, isMove, eOpts){
									var datas = records.map(function(record){var data = record.getData();data[Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID]=false;return data;});
									panel.__webglMainRenderer.setObjProperties(datas);
								},
								update: function(store, record, operation, eOpts){
	//								console.log('update', record, operation, eOpts);
	//								panel.__webglMainRenderer.setObjProperties(self.getObjDataFromRecords([record],pallet_gridpanel.getSelectionModel()));
								}
							});
							if(pallet_store.getCount && pallet_store.getCount()) pallet_store.fireEvent('add',pallet_store,pallet_store.getRange(),0,{});
						}

					},
					resize: function( panel, width, height, oldWidth, oldHeight, eOpts){
//						console.log(width,height);
						panel.__webglMainRenderer._setSize(10,10);

//						var $dom = $(panel.layout.innerCt.dom);
						var $dom = $(panel.body.dom);
						width = $dom.width();
						height = $dom.height();
						panel.__webglMainRenderer.setSize(width,height);
					}
				}
			}]
		},config||{}));
	},
});
