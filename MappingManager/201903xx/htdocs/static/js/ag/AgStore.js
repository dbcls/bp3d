window.AgApp = window.AgApp || function(config){};
window.AgApp.prototype.initStore = function(){
	var self = this;

	Ext.Ajax.timeout = 300000;

	var datachangedStore = function(store,grid){
		var palletPartsStore = Ext.data.StoreManager.lookup('palletPartsStore');
		store.suspendEvents(false);
		try{
			store.each(function(record){
				var selected = false;
				var r = palletPartsStore.findRecord('art_id',record.get('art_id'),0,false,false,true);
				if(r) selected = true;
				if(record.get('selected')===selected) return true;
				record.beginEdit();
				record.set('selected',selected);
				record.endEdit(true,['selected']);
				record.commit(true,['selected']);
			});
		}catch(e){
			console.warn(e);
		}
		store.resumeEvents();
		grid.getView().refresh();
	};

	var syncStore = function(store,grid,records,queueSuspended){
		if(Ext.isEmpty(queueSuspended)) queueSuspended = false;
		if(!Ext.isBoolean(queueSuspended)) queueSuspended = queueSuspended ? true : false;
		store.suspendEvents(queueSuspended);
		Ext.each(records,function(r,i,a){
			var record = store.findRecord('art_id',r.get('art_id'),0,false,false,true);
			if(Ext.isEmpty(record)) return true;
//			var fieldNames = ['cdi_name','cdi_name_e','cmp_id','current_use','cm_edited'];
			var fieldNames = ['cdi_name','cdi_name_e','cmp_id','cp_id','cl_id','current_use','cm_edited'];
			record.beginEdit();
			Ext.each(fieldNames,function(fieldName){
				record.set(fieldName,r.get(fieldName));
			});
			record.commit(false,fieldNames);
			record.endEdit(false,fieldNames);
		});
		store.resumeEvents();
		grid.getView().refresh();
	};

	self.syncUploadObjectStore = function(records){
		syncStore(Ext.data.StoreManager.lookup('uploadObjectStore'),Ext.getCmp('upload-object-grid'),records);
	};
	self.syncPalletPartsStore = function(records){
		syncStore(Ext.data.StoreManager.lookup('palletPartsStore'),Ext.getCmp('pallet-grid'),records,true);
	};
	self.syncPickSearchStore = function(records){
		syncStore(Ext.data.StoreManager.lookup('pickSearchStore'),Ext.getCmp('pick-search-grid'),records);
	};

	self.reloadUploadObjectStore = function(){
		Ext.data.StoreManager.lookup('uploadObjectStore').reload();
	};

	var upload_object_store = Ext.create('Ext.data.Store', {
		storeId: 'uploadObjectStore',
		model: 'PARTS',
		sorters    : [{
			property: 'art_name',
			direction: 'ASC'
		}],

		pageSize: DEF_UPLOAD_FILE_PAGE_SIZE,
		autoLoad: false,
		autoSync: false,
		remoteFilter: false,

//		remoteSort: false,
		remoteSort: true,

		filterOnLoad : false,
		sortOnFilter: false,
		sortOnLoad: false,
		proxy: Ext.create('Ext.data.proxy.Ajax',{
			type: 'ajax',
			timeout: 300000,
			api: {
				create  : 'api-upload-file-list.cgi?cmd=create',
				read    : 'api-upload-file-list.cgi?cmd=read',
				update  : 'api-upload-file-list.cgi?cmd=update',
				destroy : 'api-upload-file-list.cgi?cmd=destroy',
			},
			actionMethods : {
				create : 'POST',
				read   : 'POST',
				update : 'POST',
				destroy: 'POST'
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
				encode: true
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
		}),
		listeners: {
			beforeload: function(store,operation,eOpts){
//				debugger;
				if(!self.beforeloadStore(store)) return false;
//console.time(store.storeId);
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;

				delete p.extraParams.selected_art_ids;
				var palletPartsStore = Ext.data.StoreManager.lookup('palletPartsStore');
				if(palletPartsStore.getCount()){
					var selected_art_ids = {};
					palletPartsStore.each(function(record){
						selected_art_ids[record.get('art_id')] = 1;//record.getData();
					});
					p.extraParams.selected_art_ids = Ext.encode(selected_art_ids);
				}

			},
			datachanged : function(store,options){
				datachangedStore(store,Ext.getCmp('upload-object-grid'));
			},
			load: function(store,records,successful,eOpts){
//				console.log('uploadObjectStore.load()',successful,store.getTotalCount());
				if(successful){
					Ext.defer(function(){
						var upload_object_grid = Ext.getCmp('upload-object-grid');
						if(!store.isLoading()) upload_object_grid.setLoading(true);

						var p = store.getProxy();
						p.extraParams = p.extraParams || {};
						if(Ext.isNumber(p.extraParams.artf_id)){
							var uploadFolderTreePanelStore = Ext.data.StoreManager.lookup('uploadFolderTreePanelStore');
							uploadFolderTreePanelStore.suspendAutoSync();
							try{
								var rootNode = uploadFolderTreePanelStore.getRootNode();
								var node;
								if(p.extraParams.artf_id){
									node = rootNode.findChild( 'artf_id', p.extraParams.artf_id, true );
								}else{
									node = rootNode;
								}
								if(node){
									node.set('art_count',store.getTotalCount())
									node.commit(false,['art_count']);
								}
							}catch(e){
								console.error(e);
							}
							uploadFolderTreePanelStore.resumeAutoSync();

							var treepanel = Ext.getCmp('upload-folder-tree');
							var selModel = treepanel.getSelectionModel();
							selModel.fireEvent('selectionchange', selModel,selModel.getSelection());

						}

						var palletPartsStore = Ext.data.StoreManager.lookup('palletPartsStore');
						if(palletPartsStore.getCount()){
							palletPartsStore.suspendEvents(false);
							try{
								Ext.each(records.filter(function(record){return record.get('selected')}),function(r){
									var record = palletPartsStore.findRecord('art_id',r.get('art_id'),0,false,false,true);
									if(Ext.isEmpty(record)) return true;
									var data = r.getData();
									var modifiedFieldNames = [];
									var t_key = new RegExp(/^(art|cdi|cmp|current_use:?)/);
									record.beginEdit();
									Ext.Object.each(data,function(c_key,c_value){
										if(!t_key.test(c_key)) return true;
										var value = record.get(c_key);
										if(value===undefined) return true;
										if(value===c_value) return true;
										record.set(c_key,c_value);
										modifiedFieldNames.push(c_key);
									});
									if(modifiedFieldNames.length){
										record.endEdit(false,modifiedFieldNames);
										record.commit(false,modifiedFieldNames);
									}else{
										record.cancelEdit();
									}
								});
							}catch(e){
								console.error(e);
							}
							palletPartsStore.resumeEvents();
							var pallet_gridpanel = Ext.getCmp('pallet-grid');
							if(pallet_gridpanel && pallet_gridpanel.rendered) pallet_gridpanel.getView().refresh();
						}
						upload_object_grid.setLoading(false);
					},0);
				}
//console.timeEnd(store.storeId);
			},
			update: function(store,record,operation){
				if(operation==Ext.data.Record.EDIT){
				}else if(operation==Ext.data.Record.COMMIT){
					Ext.defer(function(){
						var palletPartsStore = Ext.data.StoreManager.lookup('palletPartsStore');
						var r = palletPartsStore.findRecord('art_id',record.get('art_id'),0,false,false,true);
						if(record.get('selected')){
							if(r) return;
							var add_records = palletPartsStore.add([record.getData()]);
							var pallet_gridpanel = Ext.getCmp('pallet-grid');
							if(pallet_gridpanel && pallet_gridpanel.rendered) pallet_gridpanel.getSelectionModel().select(add_records);
						}else{
							if(Ext.isBoolean(r) && !r) return;
							palletPartsStore.remove([r]);
						}
					},0);
				}
			},
			add: function(store){
//				console.log("uploadObjectStore.add()");
			},
			beforeprefetch: function(store){
//				console.log("uploadObjectStore.beforeprefetch()");
			},
			beforesync: function(store){
//				console.log("uploadObjectStore.beforesync()");
			},
			bulkremove: function(store){
//				console.log("uploadObjectStore.bulkremove()");
			},
			clear: function(store){
//				console.log("uploadObjectStore.clear()");
			},
			filterchange: function(store){
//				console.log("uploadObjectStore.filterchange()");
			},
			groupchange: function(store){
//				console.log("uploadObjectStore.groupchange()");
			},
			metachange: function(store){
//				console.log("uploadObjectStore.metachange()");
			},
			prefetch: function(store){
//				console.log("uploadObjectStore.prefetch()");
			},
			refresh: function(store){
//				console.log("uploadObjectStore.refresh()");
			},
			remove: function(store){
//					console.log('uploadObjectStore.remove()');
			},
			write: function(store){
//				console.log("uploadObjectStore.write()");
			}
		}
	});

	Ext.create('Ext.data.Store', {
		storeId: 'bp3dSearchStore',
		model: 'FMA',
		pageSize: DEF_FMA_SEARCH_GRID_PAGE_SIZE,
		remoteSort: true,
		sorters: [{
			property: 'art_num',
			direction: 'DESC'
		},{
			property: 'cdi_name_e',
			direction: 'ASC'
		}],
		proxy: Ext.create('Ext.data.proxy.Ajax',{
			type: 'ajax',
			url: 'get-fma-list.cgi',
			timeout: 300000,
			actionMethods : {
				create : 'POST',
				read   : 'POST',
				update : 'POST',
				destroy: 'POST'
			},
			reader: {
				type: 'json',
				root: 'datas',
				totalProperty: 'total',
				listeners: {
					exception : function(reader,response,error,eOpts){
						Ext.Msg.show({
							title: 'Reader',
							msg: response.statusText + ' [ ' + (response.timedout ? 'timeout' : response.status) + ' ]',
							buttons: Ext.Msg.OK,
							icon: Ext.Msg.ERROR
						});
					}
				}
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
			},
			listeners: {
				exception : function(proxy,response,operation,eOpts){
					Ext.Msg.show({
						title: 'Proxy',
						msg: response.statusText + ' [ ' + (response.timedout ? 'timeout' : response.status) + ' ]',
						buttons: Ext.Msg.OK,
						icon: Ext.Msg.ERROR
					});
				},
				metachange : function(proxy,meta,eOpts){
				}
			}
		}),
		listeners: {
			beforeload: function(store,operation,eOpts){
				if(!self.beforeloadStore(store)) return false;
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;

				//ここでハイライト用の正規表現を生成
				self.bp3d_search_grid_renderer_params.searchValue = (Ext.isEmpty(store.lastOptions.filters) || Ext.isEmpty(store.lastOptions.filters[0].value)) ? null : store.lastOptions.filters[0].value;
				if(self.bp3d_search_grid_renderer_params.searchValue !== null){
					self.bp3d_search_grid_renderer_params.searchRegExp = new RegExp(self.bp3d_search_grid_renderer_params.searchValue, 'g' + (self.bp3d_search_grid_renderer_params.caseSensitive ? '' : 'i'));
				}else{
					self.bp3d_search_grid_renderer_params.searchRegExp = null;
				}
//				if(Ext.isEmpty(self.bp3d_search_grid_renderer_params.searchValue)) return false;

//				var bp3d_search_grid = Ext.getCmp('bp3d-search-grid');
//				bp3d_search_grid.setLoading(true);
			},
			datachanged : function(store,options){
//				var bp3d_search_grid = Ext.getCmp('bp3d-search-grid');
//				self.load_pallet_store_records(store.getRange(),store,bp3d_search_grid);
			},
			load: function(store,records,successful,eOpts){
//				var bp3d_search_grid = Ext.getCmp('bp3d-search-grid');
//				bp3d_search_grid.setLoading(false);
			},
			update: function(store,record,operation){
				if(operation==Ext.data.Record.EDIT){
				}else if(operation==Ext.data.Record.COMMIT){

//					Ext.defer(function(){
//						self.checkedUploadGroup([record]);
//					},100);

				}
			}
		}
	});

	Ext.create('Ext.data.Store', {
		storeId: 'prefixStore',
		autoLoad: true,
		model: 'PREFIX',
		data : DEF_PREFIX_DATAS,
		proxy: {
			type: 'memory',
			reader: {
				type: 'json',
				root: 'datas'
			}
		}
	});

	Ext.create('Ext.data.Store', {
		autoLoad: false,
		storeId: 'conceptBuildStore',
		model: 'CONCEPT_BUILD',
		sorters: [{
			property: 'cb_order',
			direction: 'ASC'
		}],
		filters: [{
			property: 'cb_use',
			value: true
		}],
		proxy: Ext.create('Ext.data.proxy.Ajax',{
			timeout: 300000,
			type: 'ajax',
			api: {
				create  : 'api-concept-build-store.cgi?cmd=create',
				read    : 'api-concept-build-store.cgi?cmd=read',
				update  : 'api-concept-build-store.cgi?cmd=update',
				destroy : 'api-concept-build-store.cgi?cmd=destroy',
			},
			limitParam: undefined,
			pageParam: undefined,
			startParam: undefined,
			sortParam: undefined,
			filterParam: undefined,
			actionMethods : {
				create : 'POST',
				read   : 'POST',
				update : 'POST',
				destroy: 'POST'
			},
			reader: {
				type: 'json',
				root: 'datas',
				listeners: {
					exception: function(reader,response,error,eOpts){
//						console.log('exception()');
//						console.log(reader);
//						console.log(response);
//						console.log(error);
//						console.log(eOpts);
					}
				}
			},
			writer: {
				allowSingle: false,
				encode: true,
				type: 'json',
				root: 'datas',
				writeAllFields: true
			},
/*
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
*/
		}),
		listeners: {
			load: function( store, records, successful, eOpts ){
//				console.log('conceptBuildStore.load():'+successful);
			}
		}
	});

	var modelVersionStore = Ext.create('Ext.data.Store', {
		autoLoad: false,
		storeId: 'modelVersionStore',
		model: 'VERSION',
		proxy: {
			timeout: 300000,
			type: 'ajax',
			api: {
//				create  : 'api-dataset-store.cgi?cmd=create',
				read    : 'api-dataset-store.cgi?cmd=read',
				update  : 'api-dataset-store.cgi?cmd=update',
//				destroy : 'api-dataset-store.cgi?cmd=destroy',
			},
			limitParam: undefined,
			pageParam: undefined,
			sortParam: undefined,
			startParam: undefined,
			actionMethods : {
				create : 'POST',
				read   : 'POST',
				update : 'POST',
				destroy: 'POST'
			},
			reader: {
				type: 'json',
				root: 'datas',
				listeners: {
					exception: function(reader,response,error,eOpts){
						console.log('modelVersionStore.exception()');
						console.log(reader);
						console.log(response);
						console.log(error);
						console.log(eOpts);
					}
				}
			},
			writer: {
				allowSingle: false,
				encode: true,
				type: 'json',
				root: 'datas',
				writeAllFields: true
			}
		},
		listeners: {
			load: function( store, records, successful, eOpts ){
//				console.log('modelVersionStore.load():'+successful);
			}
		}
	});


	var pallet_store = Ext.create('Ext.data.ArrayStore', {
		storeId: 'palletPartsStore',
		autoDestroy: true,
		model: 'PALLETPARTS',
		listeners: {
			add: function(store,records,index,eOpts){
//				console.log('palletPartsStore.add()',records.length);
				self.setHashTask.delay(0);
				self.update_localdb_pallet();
			},
			remove: function(store,record,index,eOpts){
//				console.log('palletPartsStore.remove()');
				self.setHashTask.delay(0);
//				self.update_localdb_pallet();
				self.updateLocalDBPalletTask.delay(0);
			},
			update: function(store,record,operation){
				if(operation==Ext.data.Record.EDIT){
//					console.log(record.getChanges());
				}else if(operation==Ext.data.Record.COMMIT){
//					console.log('palletPartsStore.update()');
					self.setHashTask.delay(0);
//					self.update_localdb_pallet();
					self.updateLocalDBPalletTask.delay(0);
				}
			}
		}
	});

	Ext.create('Ext.data.Store', {
		storeId: 'fmaSearchStore',
		model: 'FMA',
		pageSize: DEF_FMA_SEARCH_GRID_PAGE_SIZE,
		remoteSort: false,
		sorters: [{
			property: 'cdi_name_e',
			direction: 'ASC'
		}],
		proxy: Ext.create('Ext.data.proxy.Ajax',{
			type: 'ajax',
			url: 'get-fma-list.cgi',
			timeout: 300000,
			actionMethods : {
				create : 'POST',
				read   : 'POST',
				update : 'POST',
				destroy: 'POST'
			},
			reader: {
				type: 'json',
				root: 'datas',
				totalProperty: 'total',
				listeners: {
					exception : function(reader,response,error,eOpts){
						Ext.Msg.show({
							title: 'Reader',
							msg: response.statusText + ' [ ' + (response.timedout ? 'timeout' : response.status) + ' ]',
							buttons: Ext.Msg.OK,
							icon: Ext.Msg.ERROR
						});
					}
				}
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
			},
			listeners: {
				exception : function(proxy,response,operation,eOpts){
					Ext.Msg.show({
						title: 'Proxy',
						msg: response.statusText + ' [ ' + (response.timedout ? 'timeout' : response.status) + ' ]',
						buttons: Ext.Msg.OK,
						icon: Ext.Msg.ERROR
					});
				},
				metachange : function(proxy,meta,eOpts){
				}
			}
		}),
		listeners: {
			beforeload: function(store,operation,eOpts){
				if(!self.beforeloadStore(store)) return false;
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;
			},
			datachanged : function(store,options){
			},
			load: function(store,records,successful,eOpts){
			},
			update: function(store,record,operation){
			}
		}
	});

	Ext.create('Ext.data.Store', {
		storeId: 'pickSearchStore',
		model: 'PICK_SEARCH',
		pageSize: 50,
		autoLoad: false,
		autoSync: false,
		remoteFilter: false,
		remoteSort: false,
		filterOnLoad : false,
		sortOnFilter: false,
		sortOnLoad: false,
		proxy: Ext.create('Ext.data.proxy.Ajax',{
			type: 'ajax',
			timeout: 30000*2*5,//30sec * 2 * 10
			pageParam: undefined,
			startParam: undefined,
			limitParam: undefined,
			sortParam: undefined,
			groupParam: undefined,
			filterParam: undefined,
			url: 'get-pick-search.cgi',
			actionMethods : {
				create : 'POST',
				read   : 'POST',
				update : 'POST',
				destroy: 'POST'
			},
			reader: {
				type: 'json',
				root: 'datas',
				totalProperty: 'total',
				listeners: {
					exception : function(){
					}
				}
//			},
//			writer: {
//				type: 'json',
//				root: 'datas',
//				allowSingle: false,
//				encode: false
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
		}),
		sorters: [{
			property: 'distance_voxel',
			direction: 'ASC'
		}],

		listeners: {
			beforeload: function(store,operation,eOpts){
				if(!self.beforeloadStore(store)) return false;
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;

				var view = Ext.getCmp('pick-search-grid').getView();
				var sorters = store.sorters.getRange();
				if(sorters.length){
					store.sorters.clear();
					view.headerCt.clearOtherSortStates()
				}
				store.sorters.add(new Ext.util.Sorter({
					property : 'distance_voxel',
					direction: 'ASC'
				}));
				store.sort();
			},
			datachanged : function(store,options){
				datachangedStore(store,Ext.getCmp('pick-search-grid'));
			},
			update: function(store,record,operation){
				if(operation==Ext.data.Record.EDIT){
				}else if(operation==Ext.data.Record.COMMIT){
					Ext.defer(function(){
						var palletPartsStore = Ext.data.StoreManager.lookup('palletPartsStore');
						var r = palletPartsStore.findRecord('art_id',record.get('art_id'),0,false,false,true);
						if(record.get('selected')){
							if(r) return;
							var add_records = palletPartsStore.add([record.getData()]);
							var pallet_gridpanel = Ext.getCmp('pallet-grid');
							if(pallet_gridpanel && pallet_gridpanel.rendered) pallet_gridpanel.getSelectionModel().select(add_records);
						}else{
							if(Ext.isBoolean(r) && !r) return;
							palletPartsStore.remove([r]);
						}
					},0);
				}
			}
		}
	});

	Ext.create('Ext.data.TreeStore', {
		autoLoad: false,
		autoSync: false,
		storeId: 'uploadFolderTreePanelStore',
		model: 'UPLOAD_FOLDER_TREE',
		proxy: Ext.create('Ext.data.proxy.Ajax',{
			type: 'ajax',
			timeout: 300000,
			api: {
				create  : 'api-upload-folder-tree.cgi?cmd=create',
				read    : 'api-upload-folder-tree.cgi?cmd=read',
				update  : 'api-upload-folder-tree.cgi?cmd=update',
				destroy : 'api-upload-folder-tree.cgi?cmd=destroy',
			},
			actionMethods : {
				create : 'POST',
				read   : 'POST',
				update : 'POST',
				destroy: 'POST'
			},
			reader: {
				type: 'json',
				root: 'datas',
				totalProperty:'total',
				listeners: {
					exception : function(){
					}
				}
			},
			writer: {
				type: 'json',
				root: 'datas',
				allowSingle: false,
				writeAllFields: true,
				writeRecordId: false,
				encode: true
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
		}),
		root: {
			allowDrag: true,
			allowDrop: true,
			depth: 0,
//				expandable: true,
			expanded: true,
			iconCls: 'tfolder',
			root: true,
			text: '/',
			name: 'root',
			artf_id: 0,
			artf_name: 'root'
		},
//		folderSort: true,

		sorters: [{
			property: 'artf_name',
			direction: 'ASC'
		}],

		listeners: {
			beforeload: function(store,operation,eOpts){
				if(!self.beforeloadStore(store)) return false;
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;
			},
			beforesync: function(options,eOpts){
				var store = this;
				if(!self.beforeloadStore(store)) return false;
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;
			}
		}
	});

	var fmaAllStore = Ext.create('Ext.data.Store', {
		storeId: 'fmaAllStore',
		autoSync: false,
		autoLoad: false,
		model: 'FMA_LIST',
//		pageSize: DEF_PARTS_GRID_PAGE_SIZE,
		remoteSort: false,	//trueにしないとソートできない
		sorters: [{
			property: 'cdi_name',
			direction: 'ASC'
		}],
/*
		sorters: [{
			sorterFn: function(o1, o2){
				var cdi_name_1 = o1.get('cdi_name');
				var cdi_name_2 = o2.get('cdi_name');
				var index_1 = cdi_name_1.indexOf('FMA');
				var index_2 = cdi_name_2.indexOf('FMA');
				if(index_1 === index_2){
					var value_1 = parseInt(cdi_name_1.substring(3));
					var value_2 = parseInt(cdi_name_2.substring(3));
					return value_1 - value_2;
				}else if(cdi_name_1 === cdi_name_2){
					return 0;
				}else{
					return cdi_name_1 < cdi_name_2 ? -1 : 1;
				}
			}
		}],
*/
		proxy: Ext.create('Ext.data.proxy.Ajax',{
			type: 'ajax',
			timeout: 300000,
			api: {
//				create  : 'api-fma-list.cgi?cmd=create',
				read    : 'api-fma-list.cgi?cmd=read',
//				update  : 'api-fma-list.cgi?cmd=update',
//				destroy : 'api-fma-list.cgi?cmd=destroy',
			},
			actionMethods : {
//				create : 'POST',
				read   : 'POST',
//				update : 'POST',
//				destroy: 'POST'
			},
			pageParam: undefined,
			startParam: undefined,
			limitParam: undefined,
//			sortParam: undefined,
			groupParam: undefined,
			filterParam: undefined,
			reader: {
				type: 'json',
				root: 'datas',
				totalProperty:'total',
				listeners: {
					exception : function(){
					}
				}
			},
//			writer: {
//				allowSingle: false,
//				encode: true,
//				type: 'json',
//				root: 'datas',
//				writeAllFields: true
//			},
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
			},
			listeners: {
				metachange : function(){
				}
			}
		}),
		listeners: {
			beforeload: function(store,operation,eOpts){

				var button = Ext.getCmp('ag-pallet-fma-obj-link-button');
				if(button) button.setDisabled(true);

				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				var ci_id = p.extraParams.ci_id;

				if(!self.beforeloadStore(store)) return false;
				delete p.extraParams.current_datas;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;

				if(Ext.isEmpty(p.extraParams.ci_id)) return false;

				//読み込み済みのデータと条件が同じ場合は中止する
				if(store.getCount()>0 && ci_id === p.extraParams.ci_id){
					if(button) button.setDisabled(false);
					return false;
				}

				if(button) button.setIconCls('loading-btn');
			},
			datachanged : function(store,options){
			},
			load: function(store,records,successful,eOpts){
				var button = Ext.getCmp('ag-pallet-fma-obj-link-button');
				if(button){

					var mv_frozen = false;
					button.setDisabled(!successful || mv_frozen);
					button.setIconCls('pallet_link');
				}
			},
			update : function(store,record,operation){
			}
		}
	});

	Ext.create('Ext.data.Store', {
		storeId: 'fmaMirrorAllStore',
		model: 'FMA_LIST',
		sorters: [{
			property: 'cdi_name',
			direction: 'ASC'
		}],
/*
		sorters: [{
			sorterFn: function(o1, o2){
				var cdi_name_1 = o1.get('cdi_name');
				var cdi_name_2 = o2.get('cdi_name');
				var index_1 = cdi_name_1.indexOf('FMA');
				var index_2 = cdi_name_2.indexOf('FMA');
				if(index_1 === index_2){
					var value_1 = parseInt(cdi_name_1.substring(3));
					var value_2 = parseInt(cdi_name_2.substring(3));
					return value_1 - value_2;
				}else if(cdi_name_1 === cdi_name_2){
					return 0;
				}else{
					return cdi_name_1 < cdi_name_2 ? -1 : 1;
				}
			}
		}],
*/
		proxy: {
			type: 'memory',
		}
	});
	if(fmaAllStore){
		fmaAllStore.on({
			load: function(store, records, successful, eOpts){
				var fmaMirrorAllStore = Ext.data.StoreManager.lookup('fmaMirrorAllStore');
				if(successful){
					fmaMirrorAllStore.loadRecords(records);
				}else{
					fmaMirrorAllStore.removeAll();
				}
			},
			single: true
		});
	}

	Ext.create('Ext.ag.Store', {
		storeId: 'conflictListStore',
		model: 'CONFILICT_LIST',
//		groupField: 'cdi_name',
		remoteSort: false,	//trueにしないとソートできない
		sorters: [{
			property: 'cdi_name_e',
			direction: 'ASC'
		}],
		filters: [{
			filterFn: function(record){
				return record.get('mapped_obj') > 1;
			}
		}],
		proxy: Ext.create('Ext.data.proxy.Ajax',{
			type: 'ajax',
			api: {
				read    : 'get-conflict-list.cgi?cmd=read',
			},
			actionMethods : {
				read   : 'POST',
			},
			timeout: 300000,
			pageParam: undefined,
			startParam: undefined,
			limitParam: undefined,
			sortParam: undefined,
			groupParam: undefined,
			filterParam: undefined,
			reader: {
				type: 'json',
				root: 'datas',
				totalProperty:'total',
				listeners: {
					exception : function(){
					}
				}
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
		}),
		listeners: {
			beforeload: function(store,operation,eOpts){
				if(!self.beforeloadStore(store)) return false;
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;
			}
		}
	});

	Ext.create('Ext.ag.Store', {
		storeId: 'mapListStore',
		model: 'CONFILICT_LIST',
		remoteSort: false,	//trueにしないとソートできない
		sorters: [{
			property: 'cdi_name',
			direction: 'ASC'
		}],
/*
		sorters: [{
			sorterFn: function(o1, o2){
				var cdi_name_1 = o1.get('cdi_name');
				var cdi_name_2 = o2.get('cdi_name');
				var index_1 = cdi_name_1.indexOf('FMA');
				var index_2 = cdi_name_2.indexOf('FMA');
				if(index_1 === index_2){
					var value_1 = parseInt(cdi_name_1.substring(3));
					var value_2 = parseInt(cdi_name_2.substring(3));
					return value_1 - value_2;
				}else if(cdi_name_1 === cdi_name_2){
					return 0;
				}else{
					return cdi_name_1 < cdi_name_2 ? -1 : 1;
				}
			}
		}],
*/
		filters: [{
			filterFn: function(record){
				return record.get('mapped_obj') > 0;
			}
		}],
		proxy: Ext.create('Ext.data.proxy.Ajax',{
			type: 'ajax',
			api: {
				read    : 'get-conflict-list.cgi?cmd=read',
			},
			actionMethods : {
				read   : 'POST',
			},
			timeout: 300000,
			pageParam: undefined,
			startParam: undefined,
			limitParam: undefined,
			sortParam: undefined,
			groupParam: undefined,
			filterParam: undefined,
			reader: {
				type: 'json',
				root: 'datas',
				totalProperty:'total',
				listeners: {
					exception : function(){
					}
				}
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
		}),
		listeners: {
			beforeload: function(store,operation,eOpts){
				if(!self.beforeloadStore(store)) return false;
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;

				var panel = Ext.getCmp('conflict-panel');
				if(panel && panel.rendered) panel.setLoading(true);
//				Ext.data.StoreManager.lookup('conflictListStore').removeAll();
			},
			load: function(store,records, successful, eOpts){
				var add_records = [];
				Ext.each(records,function(record){
					add_records.push(Ext.apply({},record.data));
				});
				Ext.data.StoreManager.lookup('conflictListStore').loadData(add_records);
				var panel = Ext.getCmp('conflict-panel');
				if(panel && panel.rendered) panel.setLoading(false);
			}
		}
	});

	//2016-03-31 START
	Ext.create('Ext.ag.Store', {
//		autoLoad: true,
		autoLoad: Ext.isArray(Ext.ag.Data.concept_art_map_part) && Ext.ag.Data.concept_art_map_part.length ? false : true,
		storeId: 'conceptArtMapPartStore',
		model: 'CONCEPT_ART_MAP_PART',
		remoteSort: false,	//trueにしないとソートできない
		sorters: [{
			property: 'cmp_order',
			direction: 'ASC'
		},{
			property: 'cmp_id',
			direction: 'ASC'
		}],
		data: Ext.isArray(Ext.ag.Data.concept_art_map_part) && Ext.ag.Data.concept_art_map_part.length ? Ext.ag.Data.concept_art_map_part : null,
		proxy: Ext.create('Ext.data.proxy.Ajax',{
			type: 'ajax',
			api: {
				create  : 'api-concept-art-map-part.cgi?cmd=create',
				read    : 'api-concept-art-map-part.cgi?cmd=read',
				update  : 'api-concept-art-map-part.cgi?cmd=update',
				destroy : 'api-concept-art-map-part.cgi?cmd=destroy',
			},
			actionMethods : {
				read : 'POST',
			},
			timeout: 300000,
			pageParam: undefined,
			startParam: undefined,
			limitParam: undefined,
			sortParam: undefined,
			groupParam: undefined,
			filterParam: undefined,
			reader: {
				type: 'json',
				root: 'datas',
				totalProperty:'total',
				listeners: {
					exception : function(){
					}
				}
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
		}),
		listeners: {
			beforeload: function(store,operation,eOpts){
				if(!self.beforeloadStore(store)) return false;
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;
			},
			load: function(store,records, successful, eOpts){
			}
		}
	});

	Ext.create('Ext.ag.Store', {
//		autoLoad: true,
		autoLoad: Ext.isArray(Ext.ag.Data.concept_art_map_part_select) && Ext.ag.Data.concept_art_map_part_select.length ? false : true,
		storeId: 'conceptArtMapPartSelectStore',
		model: 'CONCEPT_ART_MAP_PART',
		remoteSort: false,	//trueにしないとソートできない
		sorters: [{
			property: 'cmp_order',
			direction: 'ASC'
		},{
			property: 'cmp_id',
			direction: 'ASC'
		}],
		data: Ext.isArray(Ext.ag.Data.concept_art_map_part_select) && Ext.ag.Data.concept_art_map_part_select.length ? Ext.ag.Data.concept_art_map_part_select : null,
		proxy: Ext.create('Ext.data.proxy.Ajax',{
			type: 'ajax',
			api: {
				create  : 'api-concept-art-map-part.cgi?cmd=create',
				read    : 'api-concept-art-map-part.cgi?cmd=read',
				update  : 'api-concept-art-map-part.cgi?cmd=update',
				destroy : 'api-concept-art-map-part.cgi?cmd=destroy',
			},
			actionMethods : {
				read : 'POST',
			},
			timeout: 300000,
			pageParam: undefined,
			startParam: undefined,
			limitParam: undefined,
			sortParam: undefined,
			groupParam: undefined,
			filterParam: undefined,
			reader: {
				type: 'json',
				root: 'datas',
				totalProperty:'total',
				listeners: {
					exception : function(){
					}
				}
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
		}),
		listeners: {
			beforeload: function(store,operation,eOpts){
				if(!self.beforeloadStore(store)) return false;
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;
			},
			load: function(store,records, successful, eOpts){
				console.log(store.itemId,'load',successful,Ext.isArray(records) ? records.length : 0);
			}
		}
	});
	if(Ext.isArray(Ext.ag.Data.concept_art_map_part_select) && Ext.ag.Data.concept_art_map_part_select.length){
		var conceptArtMapPartSelectStore = Ext.data.StoreManager.lookup('conceptArtMapPartSelectStore');
		conceptArtMapPartSelectStore.clearFilter(true);
//		console.log(conceptArtMapPartSelectStore.getCount());
		conceptArtMapPartSelectStore.filter([
			{filterFn: function(item) { return item.get('cmp_id') > 0; }}
		]);
//		console.log(conceptArtMapPartSelectStore.getCount());
	}

	//2016-03-31 END


	Ext.create('Ext.ag.Store', {
//		autoLoad: true,
		autoLoad: Ext.isArray(Ext.ag.Data.concept_info) && Ext.ag.Data.concept_info.length ? false : true,
		storeId: 'conceptInfoStore',
		model: 'CONCEPT_INFO',
		remoteSort: false,	//trueにしないとソートできない
		sorters: [{
			property: 'ci_id',
			direction: 'ASC'
		}],
		data: Ext.isArray(Ext.ag.Data.concept_info) && Ext.ag.Data.concept_info.length ? Ext.ag.Data.concept_info : null,
		proxy: Ext.create('Ext.data.proxy.Ajax',{
			type: 'ajax',
			api: {
				read : 'api-concept-info-store.cgi?cmd=read',
			},
			actionMethods : {
				read : 'POST',
			},
			timeout: 300000,
			pageParam: undefined,
			startParam: undefined,
			limitParam: undefined,
			sortParam: undefined,
			groupParam: undefined,
			filterParam: undefined,
			reader: {
				type: 'json',
				root: 'datas',
				totalProperty:'total',
				listeners: {
					exception : function(){
					}
				}
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
		}),
		listeners: {
			beforeload: function(store,operation,eOpts){
				if(!self.beforeloadStore(store)) return false;
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;
			},
			load: function(store,records, successful, eOpts){
			}
		}
	});

	Ext.create('Ext.data.Store', {
		storeId: 'uploadFolderFileStore',
		model: 'UPLOAD_FOLDER_FILE',

		pageSize: undefined,
		autoLoad: false,
		autoSync: false,
		remoteFilter: false,
		remoteSort: false,
		filterOnLoad : false,
		sortOnFilter: false,
		sortOnLoad: false,
		proxy: Ext.create('Ext.data.proxy.Ajax',{
			type: 'ajax',
			api: {
				create  : 'api-upload-folder-file.cgi?cmd=create',
				read    : 'api-upload-folder-file.cgi?cmd=read',
				update  : 'api-upload-folder-file.cgi?cmd=update',
				destroy : 'api-upload-folder-file.cgi?cmd=destroy',
			},
			timeout: 300000,
			actionMethods : {
				create : 'POST',
				read   : 'POST',
				update : 'POST',
				destroy: 'POST'
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
				encode: true
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
		}),
		listeners: {
			beforeload: function(store,operation,eOpts){
				if(!self.beforeloadStore(store)) return false;
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;
			},
			beforesync: function(options,eOpts){
				var store = this;
				if(!self.beforeloadStore(store)) return false;
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;
			}
		}
	});





	Ext.create('Ext.ag.Store', {
//		autoLoad: true,
		autoLoad: Ext.isArray(Ext.ag.Data.concept_part) && Ext.ag.Data.concept_part.length ? false : true,
		storeId: 'conceptPartStore',
		model: 'CONCEPT_PART',
		remoteSort: false,	//trueにしないとソートできない
		sorters: [{
			property: 'cp_order',
			direction: 'ASC'
		},{
			property: 'cp_id',
			direction: 'ASC'
		}],
		data: Ext.isArray(Ext.ag.Data.concept_part) && Ext.ag.Data.concept_part.length ? Ext.ag.Data.concept_part : null,
		proxy: Ext.create('Ext.data.proxy.Ajax',{
			type: 'ajax',
			api: {
				create  : 'api-concept-part.cgi?cmd=create',
				read    : 'api-concept-part.cgi?cmd=read',
				update  : 'api-concept-part.cgi?cmd=update',
				destroy : 'api-concept-part.cgi?cmd=destroy',
			},
			actionMethods : {
				read : 'POST',
			},
			timeout: 300000,
			pageParam: undefined,
			startParam: undefined,
			limitParam: undefined,
			sortParam: undefined,
			groupParam: undefined,
			filterParam: undefined,
			reader: {
				type: 'json',
				root: 'datas',
				totalProperty:'total',
				listeners: {
					exception : function(){
					}
				}
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
		}),
		listeners: {
			beforeload: function(store,operation,eOpts){
				if(!self.beforeloadStore(store)) return false;
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;
			},
			add: function(store, records, successful, eOpts){
				window.AgHashMap = window.AgHashMap || {};
				window.AgHashMap.conceptPart = new Ext.util.HashMap();
				Ext.Array.each(records, function(record){
					window.AgHashMap.conceptPart.add(record.get('cp_id'),record.getData());
					window.AgHashMap.conceptPart.add(record.get('cp_abbr'),record.getData());
				});
			},
			load: function(store, records, successful, eOpts){
				window.AgHashMap = window.AgHashMap || {};
				window.AgHashMap.conceptPart = new Ext.util.HashMap();
				Ext.Array.each(records, function(record){
					window.AgHashMap.conceptPart.add(record.get('cp_id'),record.getData());
					window.AgHashMap.conceptPart.add(record.get('cp_abbr'),record.getData());
				});
			}
		}
	});

	Ext.create('Ext.ag.Store', {
//		autoLoad: true,
		autoLoad: Ext.isArray(Ext.ag.Data.concept_part_select) && Ext.ag.Data.concept_part_select.length ? false : true,
		storeId: 'conceptPartSelectStore',
		model: 'CONCEPT_PART',
		remoteSort: false,	//trueにしないとソートできない
		sorters: [{
			property: 'cp_order',
			direction: 'ASC'
		},{
			property: 'cp_id',
			direction: 'ASC'
		}],
		data: Ext.isArray(Ext.ag.Data.concept_part_select) && Ext.ag.Data.concept_part_select.length ? Ext.ag.Data.concept_part_select : null,
		proxy: Ext.create('Ext.data.proxy.Ajax',{
			type: 'ajax',
			api: {
				create  : 'api-concept-part.cgi?cmd=create',
				read    : 'api-concept-part.cgi?cmd=read',
				update  : 'api-concept-part.cgi?cmd=update',
				destroy : 'api-concept-part.cgi?cmd=destroy',
			},
			actionMethods : {
				read : 'POST',
			},
			timeout: 300000,
			pageParam: undefined,
			startParam: undefined,
			limitParam: undefined,
			sortParam: undefined,
			groupParam: undefined,
			filterParam: undefined,
			reader: {
				type: 'json',
				root: 'datas',
				totalProperty:'total',
				listeners: {
					exception : function(){
					}
				}
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
		}),
		listeners: {
			beforeload: function(store,operation,eOpts){
				if(!self.beforeloadStore(store)) return false;
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;
			},
			load: function(store,records, successful, eOpts){
				console.log(store.itemId,'load',successful,Ext.isArray(records) ? records.length : 0);
			}
		}
	});
	if(Ext.isArray(Ext.ag.Data.concept_part_select) && Ext.ag.Data.concept_part_select.length){
		var conceptPartSelectStore = Ext.data.StoreManager.lookup('conceptPartSelectStore');
		conceptPartSelectStore.clearFilter(true);
		conceptPartSelectStore.filter([
			{filterFn: function(item) { return item.get('cp_id') > 0; }}
		]);
	}





	Ext.create('Ext.ag.Store', {
//		autoLoad: true,
		autoLoad: Ext.isArray(Ext.ag.Data.concept_laterality) && Ext.ag.Data.concept_laterality.length ? false : true,
		storeId: 'conceptLateralityStore',
		model: 'CONCEPT_LATERALITY',
		remoteSort: false,	//trueにしないとソートできない
		sorters: [{
			property: 'cl_order',
			direction: 'ASC'
		},{
			property: 'cl_id',
			direction: 'ASC'
		}],
		data: Ext.isArray(Ext.ag.Data.concept_laterality) && Ext.ag.Data.concept_laterality.length ? Ext.ag.Data.concept_laterality : null,
		proxy: Ext.create('Ext.data.proxy.Ajax',{
			type: 'ajax',
			api: {
				create  : 'api-concept-laterality.cgi?cmd=create',
				read    : 'api-concept-laterality.cgi?cmd=read',
				update  : 'api-concept-laterality.cgi?cmd=update',
				destroy : 'api-concept-laterality.cgi?cmd=destroy',
			},
			actionMethods : {
				read : 'POST',
			},
			timeout: 300000,
			pageParam: undefined,
			startParam: undefined,
			limitParam: undefined,
			sortParam: undefined,
			groupParam: undefined,
			filterParam: undefined,
			reader: {
				type: 'json',
				root: 'datas',
				totalProperty:'total',
				listeners: {
					exception : function(){
					}
				}
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
		}),
		listeners: {
			beforeload: function(store,operation,eOpts){
				if(!self.beforeloadStore(store)) return false;
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;
			},
			add: function(store,records, successful, eOpts){
				window.AgHashMap = window.AgHashMap || {};
				window.AgHashMap.cconceptLaterality = new Ext.util.HashMap();
				Ext.Array.each(records, function(record){
					window.AgHashMap.cconceptLaterality.add(record.get('cl_id'),record.getData());
					window.AgHashMap.cconceptLaterality.add(record.get('cl_abbr'),record.getData());
				});
			},
			load: function(store,records, successful, eOpts){
				window.AgHashMap = window.AgHashMap || {};
				window.AgHashMap.cconceptLaterality = new Ext.util.HashMap();
				Ext.Array.each(records, function(record){
					window.AgHashMap.cconceptLaterality.add(record.get('cl_id'),record.getData());
					window.AgHashMap.cconceptLaterality.add(record.get('cl_abbr'),record.getData());
				});
			}
		}
	});

	Ext.create('Ext.ag.Store', {
//		autoLoad: true,
		autoLoad: Ext.isArray(Ext.ag.Data.concept_laterality_select) && Ext.ag.Data.concept_laterality_select.length ? false : true,
		storeId: 'conceptLateralitySelectStore',
		model: 'CONCEPT_LATERALITY',
		remoteSort: false,	//trueにしないとソートできない
		sorters: [{
			property: 'cl_order',
			direction: 'ASC'
		},{
			property: 'cl_id',
			direction: 'ASC'
		}],
		data: Ext.isArray(Ext.ag.Data.concept_laterality_select) && Ext.ag.Data.concept_laterality_select.length ? Ext.ag.Data.concept_laterality_select : null,
		proxy: Ext.create('Ext.data.proxy.Ajax',{
			type: 'ajax',
			api: {
				create  : 'api-concept-laterality.cgi?cmd=create',
				read    : 'api-concept-laterality.cgi?cmd=read',
				update  : 'api-concept-laterality.cgi?cmd=update',
				destroy : 'api-concept-laterality.cgi?cmd=destroy',
			},
			actionMethods : {
				read : 'POST',
			},
			timeout: 300000,
			pageParam: undefined,
			startParam: undefined,
			limitParam: undefined,
			sortParam: undefined,
			groupParam: undefined,
			filterParam: undefined,
			reader: {
				type: 'json',
				root: 'datas',
				totalProperty:'total',
				listeners: {
					exception : function(){
					}
				}
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
		}),
		listeners: {
			beforeload: function(store,operation,eOpts){
				if(!self.beforeloadStore(store)) return false;
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;
			},
			load: function(store,records, successful, eOpts){
				console.log(store.itemId,'load',successful,Ext.isArray(records) ? records.length : 0);
			}
		}
	});
	if(Ext.isArray(Ext.ag.Data.concept_laterality_select) && Ext.ag.Data.concept_laterality_select.length){
		var conceptLateralitySelectStore = Ext.data.StoreManager.lookup('conceptLateralitySelectStore');
		conceptLateralitySelectStore.clearFilter(true);
		conceptLateralitySelectStore.filter([
			{filterFn: function(item) { return item.get('cl_id') > 0; }}
		]);
	}

	Ext.create('Ext.ag.Store', {
//		autoLoad: true,
		autoLoad: Ext.isArray(Ext.ag.Data.concept_relation_logic) && Ext.ag.Data.concept_relation_logic.length ? false : true,
		storeId: 'conceptRelationLogicStore',
		model: 'CONCEPT_RELATION_LOGIC',
		remoteSort: false,	//trueにしないとソートできない
		sorters: [{
			property: 'crl_order',
			direction: 'ASC'
		},{
			property: 'crl_id',
			direction: 'ASC'
		}],
		data: Ext.isArray(Ext.ag.Data.concept_relation_logic) && Ext.ag.Data.concept_relation_logic.length ? Ext.ag.Data.concept_relation_logic : null,
		proxy: Ext.create('Ext.data.proxy.Ajax',{
			type: 'ajax',
			api: {
				create  : 'api-concept-relation-logic.cgi?cmd=create',
				read    : 'api-concept-relation-logic.cgi?cmd=read',
				update  : 'api-concept-relation-logic.cgi?cmd=update',
				destroy : 'api-concept-relation-logic.cgi?cmd=destroy',
			},
			actionMethods : {
				read : 'POST',
			},
			timeout: 300000,
			pageParam: undefined,
			startParam: undefined,
			limitParam: undefined,
			sortParam: undefined,
			groupParam: undefined,
			filterParam: undefined,
			reader: {
				type: 'json',
				root: 'datas',
				totalProperty:'total',
				listeners: {
					exception : function(){
					}
				}
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
		}),
		listeners: {
			beforeload: function(store,operation,eOpts){
				if(!self.beforeloadStore(store)) return false;
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;
			},
			load: function(store,records, successful, eOpts){
//				console.log(store.storeId,'load',successful,Ext.isArray(records) ? records.length : 0);
			}
		}
	});

	Ext.create('Ext.ag.Store', {
		storeId: 'conceptDataInfoUserDataStore',
		model: 'CONCEPT_DATA_INFO_USER_DATA',
		remoteSort: false,	//trueにしないとソートできない
		sorters: [{
			property: 'cdi_name',
			direction: 'ASC'
		}],
		proxy: Ext.create('Ext.data.proxy.Ajax',{
			type: 'ajax',
			api: {
				create  : 'api-concept-data-info-user-data.cgi?cmd=create',
				read    : 'api-concept-data-info-user-data.cgi?cmd=read',
				update  : 'api-concept-data-info-user-data.cgi?cmd=update',
				destroy : 'api-concept-data-info-user-data.cgi?cmd=destroy',
			},
			actionMethods : {
				create : 'POST',
				read   : 'POST',
				update : 'POST',
				destroy: 'POST'
			},
			timeout: 300000,
			pageParam: undefined,
			startParam: undefined,
			limitParam: undefined,
			sortParam: undefined,
			groupParam: undefined,
			filterParam: undefined,
			reader: {
				type: 'json',
				root: 'datas',
				totalProperty:'total',
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
		}),
		listeners: {
			beforeload: function(store,operation,eOpts){
				if(!self.beforeloadStore(store)) return false;
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;
			},
			load: function(store,records, successful, eOpts){
//				console.log(store.storeId,'load',successful,Ext.isArray(records) ? records.length : 0);
			}
		}
	});

};

