window.AgApp = window.AgApp || function(config){};
window.AgApp.prototype.initStore = function(){
	var self = this;
	var timeout = 300000;

	Ext.create('Ext.data.Store', {
		storeId: AgDef.CONCEPT_TERM_SEARCH_STORE_ID,
		model: 'CONCEPT_TERM',
		pageSize: AgDef.CONCEPT_TERM_SEARCH_GRID_PAGE_SIZE,
		remoteSort: true,
		sorters: [{
			property: 'name',
			direction: 'ASC'
		}],
		proxy: {
			type: 'ajax',
			url: 'get-fma-list.cgi',
			timeout: timeout,
//			pageParam: undefined,
//			startParam: undefined,
//			limitParam: undefined,
//			groupParam: undefined,
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
						if(response.status == '-1') return;
						Ext.Msg.show({
							title: 'Reader',
							msg: response.statusText + ' [ ' + (response.timedout ? 'timeout' : response.status) + ' ]',
							buttons: Ext.Msg.OK,
							icon: Ext.Msg.ERROR
						});
					}
				}
			},
			listeners: {
				exception : function(proxy,response,operation,eOpts){
					if(response.status == '-1') return;
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
		},
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
		storeId: AgDef.CONCEPT_TERM_STORE_ID,
		model: 'CONCEPT_TERM',
		pageSize: AgDef.CONCEPT_TERM_SEARCH_GRID_PAGE_SIZE,
		remoteSort: true,
		sorters: [{
			property: 'name',
			direction: 'ASC'
		}],
		proxy: {
			type: 'ajax',
//			url: 'get-fma-list.cgi',
			timeout: timeout,
			api: {
				create  : 'api-fma-list.cgi?cmd=create',
				read    : 'api-fma-list.cgi?cmd=read',
				update  : 'api-fma-list.cgi?cmd=update',
				destroy : 'api-fma-list.cgi?cmd=destroy'
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
					exception : function(reader,response,error,eOpts){
						if(response.status == '-1') return;
						Ext.Msg.show({
							title: 'Reader',
							msg: response.statusText + ' [ ' + (response.timedout ? 'timeout' : response.status) + ' ]',
							buttons: Ext.Msg.OK,
							icon: Ext.Msg.ERROR
						});
					}
				}
			},
			listeners: {
				exception : function(proxy,response,operation,eOpts){
					if(response.status == '-1') return;
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
		},
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

	Ext.create('Ext.ag.Store', {
		autoLoad: Ext.isArray(Ext.ag.Data.concept_info) && Ext.ag.Data.concept_info.length ? false : true,
		storeId: 'conceptInfoStore',
		model: 'CONCEPT_INFO',
		remoteSort: false,
		sorters: [{
			property: 'cb_order',
			direction: 'ASC'
		}],
		data: Ext.isArray(Ext.ag.Data.concept_info) && Ext.ag.Data.concept_info.length ? Ext.ag.Data.concept_info : null
	});

	Ext.create('Ext.ag.Store', {
		autoLoad: Ext.isArray(Ext.ag.Data.concept_build) && Ext.ag.Data.concept_build.length ? false : true,
		storeId: 'conceptBuildStore',
		model: 'CONCEPT_BUILD',
		remoteSort: false,
		sorters: [{
			property: 'cb_order',
			direction: 'ASC'
		}],
		data: Ext.isArray(Ext.ag.Data.concept_build) && Ext.ag.Data.concept_build.length ? Ext.ag.Data.concept_build : null
	});

	var upload_object_store = Ext.create('Ext.data.Store', {
		storeId: 'uploadObjectStore',
		model: 'PARTS',
		sorters    : [{
			property: 'art_name',
			direction: 'ASC'
		}],

		pageSize: self.DEF_UPLOAD_FILE_PAGE_SIZE,
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
			startParam: null,
			limitParam: null,
			pageParam: null,
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
				if(palletPartsStore && palletPartsStore.getCount()){
					var selected_art_ids = {};
					palletPartsStore.each(function(record){
						selected_art_ids[record.get('art_id')] = 1;//record.getData();
					});
					p.extraParams.selected_art_ids = Ext.encode(selected_art_ids);
				}

			},
			datachanged : function(store,options){
//				datachangedStore(store,Ext.getCmp('upload-object-grid'));
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
						upload_object_grid.setLoading(false);
					},0);
				}
//console.timeEnd(store.storeId);
			}
		}
	});
/*
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
*/
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
};

