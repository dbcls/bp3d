window.AgApp = window.AgApp || function(config){};
window.AgApp.prototype.initStore = function(){
	var self = this;

	var upload_group_store = Ext.create('Ext.ag.Store', {
		storeId: 'uploadGroupStore',
		autoLoad: false,
		autoSync: false,
		model: 'EXTENSIONPARTS',
		proxy: {
			type: 'ajax',
			timeout: 300000,
			api: {
				create  : 'api-upload-group-list.cgi?cmd=create',
				read    : 'api-upload-group-list.cgi?cmd=read',
				update  : 'api-upload-group-list.cgi?cmd=update',
				destroy : 'api-upload-group-list.cgi?cmd=destroy',
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
				encode: true
			},
			listeners: {
				metachange : function(){
				}
			}
		},
		filters: [{
			property: 'artg_delcause',
			value: null
		}],
		sorters: [{
			property: 'artg_name',
			direction: 'ASC'
		}],
		listeners: {
			beforesync: function( options, eOpts ){
//				console.log("uploadGroupStore.beforesync()");
				var store = this;
				if(!self.beforeloadStore(store)) return false;
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams.model;
				delete p.extraParams.version;
				delete p.extraParams.ag_data;
				delete p.extraParams.tree;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;
			},
			beforeload: function(store,operation,eOpts){
//				console.log("uploadGroupStore.beforeload()");
				self.groupname2grouppath = {};
				try{Ext.getCmp('upload-group-grid').setLoading(true);}catch(e){}

				if(!self.beforeloadStore(store)) return false;

				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.selected_artg_ids;
				delete p.extraParams.current_datas;
				delete p.extraParams.model;
				delete p.extraParams.version;
				delete p.extraParams.ag_data;
				delete p.extraParams.tree;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;

				var filters = store._getFilters();
				store._setFilters([{
					property: 'artg_delcause',
					value: null
				},{
					property: 'selected',
					value: true
				}]);

				var selected_artg_ids = [];
				store.each(function(r){
					selected_artg_ids.push(r.get('artg_id'));
				});
				if(!Ext.isEmpty(selected_artg_ids)) p.extraParams.selected_artg_ids = Ext.encode(selected_artg_ids);

				store._setFilters(filters);

			},
			load: function(store,records,successful,eOpts){
//				console.log("uploadGroupStore.load()");
				Ext.each(records,function(record,i,a){
					var name = record.get('name');
					if(self.groupname2grouppath[name]) return true;
					self.groupname2grouppath[name] = AgURLParser.newExtensionPartGroup();
					self.groupname2grouppath[name].PartGroupName = name;
					self.groupname2grouppath[name].PartGroupPath = record.get('path');
				});
				try{Ext.getCmp('upload-group-grid').setLoading(false);}catch(e){}
/*
				var filters = store._getFilters();
				store._setFilters([{
					property: 'artg_delcause',
					value: null
				}]);
				store.group('artf_id');
				var counts = store.count(true);
				store.clearGrouping();
				store._setFilters(filters);
*/
				var groupingCount = store._getGroupingCount('artf_id');
				if(Ext.isObject(groupingCount)){
//					console.log(groupingCount);
					var store = Ext.data.StoreManager.lookup('uploadFolderTreePanelStore');
					store.suspendAutoSync();
					var rootNode = store.getRootNode();
					Ext.Object.each(groupingCount, function(key, value, myself) {
						var node = rootNode;
						key-=0;
						if(key){
							node = rootNode.findChild( 'artf_id', key, true );
						}
//						console.log(node);
						if(!node) return true;
						node.set('artg_count',value);
						node.commit(false,['artg_count']);
					});
					store.resumeAutoSync();
				}
			},
			filterchange: {
				fn: function( store, filters, eOpts ){
//					console.log("uploadGroupStore.filterchange()");
//					console.log(filters);

					var selected_art_ids = self.getSelectedArtIds();
					var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
					uploadObjectStore.setLoadUploadObjectAllStoreFlag();
					uploadObjectStore.loadPage(1,{
						params: { selected_art_ids: Ext.encode(selected_art_ids) },
						sorters: uploadObjectStore.getUploadObjectLastSorters()
					});

				},
				buffer: 250
			},
			add: function(store,records,index,eOpts){
			},
			remove: function(store,record,index,eOpts){
//				console.log("uploadGroupStore.remove()");
			},
			update: function(store,record,operation,modifiedFieldNames,eOpts){

//				console.log('uploadGroupStore.update(1)');
//				console.log(operation);
//				console.log(record.modified);

				if(operation==Ext.data.Record.EDIT){
					if(!Ext.isEmpty(record.modified.selected)){
						upload_object_grid.setLoading(true);
						store.on({
							update : function(store,record,operation,modifiedFieldNames,eOpts){
								if(operation!=Ext.data.Record.COMMIT){
									upload_object_grid.setLoading(false);
									return;
								}

//								var filters = [];
//								var hideNoUse = Ext.getCmp('hide-no-use-checkbox').getValue();
//								if(hideNoUse) filters.push({property: 'cm_use',value: true});

								var selected_art_ids = self.getSelectedArtIds();
								var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
								uploadObjectStore.setLoadUploadObjectAllStoreFlag();
								uploadObjectStore.loadPage(1,{
									params: { selected_art_ids: Ext.encode(selected_art_ids) },
									sorters: uploadObjectStore.getUploadObjectLastSorters()
								});
							},
							buffer : 250,
							single : true
						});
					}else if(record.data.selected && (!Ext.isEmpty(record.modified.color) || !Ext.isEmpty(record.modified.opacity))){
						store.on({
							update : function(store,record,operation,modifiedFieldNames,eOpts){
								if(operation!=Ext.data.Record.COMMIT) return;

								var extension_parts_store = Ext.data.StoreManager.lookup('extensionPartsStore');

								var isCommit = false;
								Ext.iterate([upload_object_store,extension_parts_store],function(rs,is,as){
									rs.suspendEvents(true);
									Ext.iterate(self.store_find_group(rs,record.get('name')),function(r,i,a){
										if(self.record_update(['color','opacity'],record,r)) isCommit = true;
									});
									rs.resumeEvents();
								});
								if(isCommit){
//									upload_object_grid.getView().refresh();
									var scrollTop = upload_object_grid.body.dom.scrollTop;
									upload_object_grid.getView().refresh();
									upload_object_grid.body.dom.scrollTop = scrollTop;
								}
							},
							buffer : 10,
							single : true
						});

					}
/*
					else if(!Ext.isEmpty(record.modified.artf_id)){
						store.on(
							'update',
							function(store,record,operation,modifiedFieldNames,eOpts){
								if(operation!=Ext.data.Record.COMMIT) return;

								var groupingCount = store._getGroupingCount('artf_id');
								if(Ext.isObject(groupingCount)){

									var store = Ext.data.StoreManager.lookup('uploadFolderTreePanelStore');
									store.suspendAutoSync();
									var rootNode = store.getRootNode();

									if(Ext.isNumber(eOpts.artf_id)){
										if(Ext.isEmpty(groupingCount[eOpts.artf_id])){
											var node = rootNode;
											if(eOpts.artf_id){
												node = rootNode.findChild( 'artf_id', eOpts.artf_id, true );
											}
											if(node){
												node.set('artg_count',0)
												node.commit(false,['artg_count']);
											}
										}
									}

									Ext.Object.each(groupingCount, function(key, value, myself) {
										var node = rootNode;
										key-=0;
										if(key){
											node = rootNode.findChild( 'artf_id', key, true );
										}
										if(!node) return true;
										node.set('artg_count',value);
										node.commit(false,['artg_count']);
									});
									store.resumeAutoSync();
								}

							},
							this,
							{
								buffer : 10,
								single : true,
								artf_id: record.modified.artf_id
							}
						);
					}
*/
				}else if(operation==Ext.data.Record.COMMIT){
					return;
				}
			}
		}
	});
	upload_group_store.on('load',function(store,records,options){

		var func = Ext.bind(self.upload_group_store_hashchange,self);

		$(window).unbind('hashchange', func);
		self.upload_group_store_load(store,records);
		if(store.findExact('selected',true)>=0){
			if(true || self.getPressedLinkedUploadPartsButton()){
				var cb1 = function(){
					var selected_art_ids = {};
					pallet_store.each(function(r){
						if(!r.get('selected')) return true;
						var artg_id = r.get('artg_id');
						selected_art_ids[artg_id] = selected_art_ids[artg_id] || {};
						selected_art_ids[artg_id][r.get('art_id')] = null;
					});
					upload_object_store.setLoadUploadObjectAllStoreFlag();
					upload_object_store.loadPage(1,{
						params: {
							selected_art_ids: Ext.encode(selected_art_ids)
						},
						sorters: self.getSelectedSorters()
					});
				};
				var cb2 = function(){
					var combo = Ext.getCmp('tree-combobox');
					if(combo){
						if(Ext.isEmpty(combo.getValue())){
							combo.on({
								select: {
									fn: cb1,
									scope: self,
									single: true
								}
							});
						}else{
							cb1();
						}
					}
				};
				var treeStore = Ext.data.StoreManager.lookup('treeStore');
				if(treeStore.getCount()>0){
					cb2();
				}else{
					treeStore.on({
						load: {
							fn: cb2,
							scope: self,
							single: true
						}
					});
				}

			}else{
				upload_object_store.on('load',function(store,records,options){
					self.upload_group_store_load(store,records);
				},this,{
					single:true,
					buffer:500
				});
				upload_object_store.loadPage(1);
			}
		}
		Ext.defer(function(){
			$(window).bind('hashchange', func);
		},1000);
	},this,{
		single:true,
		buffer:500
	});


	var upload_object_store = Ext.create('Ext.data.Store', {
		storeId: 'uploadObjectStore',
		model: 'EXTENSIONPARTS',
		sorters    : [{
			property: 'artg_name',
			direction: 'ASC'
		},{
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
		proxy: {
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
			}
		},

		listeners: {
			beforeload: function(store,operation,eOpts){
//				console.log("uploadObjectStore.beforeload():["+store.getLoadUploadObjectAllStoreFlag()+"]");
//				console.log(operation);

				store.setUploadObjectLastSorters(Ext.Array.clone(operation.sorters || []));

				var extension_parts_store = Ext.data.StoreManager.lookup('extensionPartsStore');

				if(true || self.getPressedLinkedUploadPartsButton()){
					Ext.defer(function(){
						var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
						var uploadObjectAllStore = Ext.data.StoreManager.lookup('uploadObjectAllStore');

//						var autoAbort = Ext.Ajax.autoAbort;
//						Ext.Ajax.autoAbort = true;


//						uploadObjectAllStore.clearFilter();
//						if(operation.filters.length>0) uploadObjectAllStore.filter(operation.filters);
//						if(operation.sorters.length>0) uploadObjectAllStore.sort(operation.sorters);

						var params = null;
						var filters = null;
						var sorters = null;
						if(operation.params) params = operation.params;
						if(operation.filters && operation.filters.length>0) filters = operation.filters;
						if(operation.sorters && operation.sorters.length>0) sorters = operation.sorters;

						var cb = function(rs, op, success){
							var loadRecords = [];
							var loadDatas = [];
							Ext.each(uploadObjectAllStore.getRange(operation.start,operation.start+operation.limit-1),function(r,i,a){
								var rec = r.copy();
								Ext.data.Model.id(rec);
								loadRecords.push(rec);
								loadDatas.push({
									art_id: rec.data.art_id,
									artg_id: rec.data.artg_id
								});
							});


							uploadObjectStore.loadRecords(loadRecords);
							self.updateArtInfo(function(){
								uploadObjectStore.fireEvent('load', uploadObjectStore, uploadObjectStore.getRange(), true);
								upload_object_grid.setLoading(false);
							},uploadObjectStore);
							return;


//							if(!self.beforeloadStore(uploadObjectStore)){
//								uploadObjectStore.loadRecords(loadRecords,operation);
//								uploadObjectStore.fireEvent('load', uploadObjectStore, uploadObjectStore.getRange(), true);
//								return false;
//							}
//							var p = store.getProxy();
//							var extraParams = Ext.Object.merge(params||{},p.extraParams||{});
//							extraParams = Ext.Object.merge({art_datas:Ext.encode(loadDatas)},extraParams);
//							if(operation.sorters && operation.sorters.length){
//								var sorters = [];
//								Ext.each(operation.sorters,function(o){
//									sorters.push({
//										property: o.property,
//										direction: o.direction
//									});
//								});
//								if(sorters.length) extraParams.sort = Ext.encode(sorters);
//							}
//							upload_object_grid.setLoading(true);
//							console.log('Ext.Ajax.request():api-upload-file-list.cgi?cmd=read');
//							Ext.Ajax.request({
//								url: 'api-upload-file-list.cgi?cmd=read',
//								method: 'POST',
//								params: Ext.Object.toQueryString(extraParams,true),
//								callback: function(options,success,response){
//									uploadObjectStore.fireEvent('load', uploadObjectStore, uploadObjectStore.getRange(), true);
//								},
//								success: function(response,options){
//									var json;
//									var records;
//									try{json = Ext.decode(response.responseText)}catch(e){};
//									if(Ext.isEmpty(json) || Ext.isEmpty(json.datas) || json.success==false){
//										uploadObjectStore.loadRecords(loadRecords,operation);
//										return;
//									}
//									uploadObjectStore.removeAll(false);
//
//									var addrecs = [];
//									Ext.iterate(json.datas,function(data){
//										addrecs.push(Ext.create(uploadObjectStore.model.modelName,data));
//									});
//									uploadObjectStore.add(addrecs);
//								},
//								failure: function(response,options){
//									console.log(response);
//								}
//							});
						};

//						upload_object_grid.setLoading(true);
						if(uploadObjectStore.getLoadUploadObjectAllStoreFlag()){
							uploadObjectAllStore.loadPage(1,{
								params: params,
								filters: filters,
								sorters: sorters,
								callback: function(rs, op, success){
									uploadObjectStore.totalCount = uploadObjectAllStore.getCount();
									cb();
								}
							});
						}
						else{
							cb();
						}
						uploadObjectStore.setLoadUploadObjectAllStoreFlag(false);
					},100);
					upload_object_grid.setLoading(true);
					return false;
				}
//				console.log("upload_object_store.beforeload()");

				if(!self.beforeloadStore(store)) return false;


				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams.model;
				delete p.extraParams.version;
				delete p.extraParams.ag_data;
				delete p.extraParams.tree;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;

				var groups = [];
				var artg_ids = [];
				extension_parts_store.suspendEvents(true);
//				var filter = upload_group_store._getFilters();
//				upload_group_store._setFilters([{
//					property: 'artg_delcause',
//					value: null
//				},{
//					property: 'selected',
//					value: true
//				}]);
				upload_group_store.each(function(r,i,a){
					if(r.get('selected')){
						groups.push(r.get('name'));
						artg_ids.push(r.get('artg_id'));
					}else{
						self.extension_parts_store_remove_group(r.get('artg_name'));
					}
				});
//				upload_group_store._setFilters(filter);
				extension_parts_store.resumeEvents();

//				console.log(Ext.data.StoreManager.lookup('extensionPartsStore').getRange());

				p.extraParams.groups = Ext.encode(groups);
				p.extraParams.artg_ids = Ext.encode(artg_ids);

				delete p.extraParams.selected;
				var records = [];
				extension_parts_store.each(function(r,i,a){
					records.push({
						art_id   : r.get('art_id'),
						artg_id  : r.get('artg_id'),

						group    : r.get('group'),
						name     : r.get('name'),
						color    : r.get('color'),
						opacity  : r.get('opacity'),
						selected : r.get('selected')
					});
				});
				p.extraParams.selected = Ext.encode(records);
			},
			datachanged : function(store,options){
//				console.log("uploadObjectStore.datachanged()");
				self.load_pallet_store_records(store.getRange(),store,upload_object_grid);
			},
			load: function(store,records,successful,eOpts){
//				console.log("uploadObjectStore.load()");
				upload_object_grid.setLoading(false);
			},
			update: function(store,record,operation){
//				console.log("uploadObjectStore.update()");
				if(operation==Ext.data.Record.EDIT){
				}else if(operation==Ext.data.Record.COMMIT){
					Ext.defer(function(){
						var uploadObjectAllStore = Ext.data.StoreManager.lookup('uploadObjectAllStore');
						var upd_rec = uploadObjectAllStore.findRecord('art_id',record.data.art_id,0,false,false,true);
						if(!Ext.isEmpty(upd_rec)){
							var keys = [];
							for(var key in record.data){
								keys.push(key);
							}
							uploadObjectAllStore.suspendEvents(false);
							self.record_update(keys,record,upd_rec);
							uploadObjectAllStore.resumeEvents();
						}
						self.extension_parts_store_update(record,true,false);
					},100);
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
//				console.log("uploadObjectStore.remove()");
			},
			write: function(store){
//				console.log("uploadObjectStore.write()");
			}
		}
	});
	upload_object_store.setLoadUploadObjectAllStoreFlag = function(flag){
		if(Ext.isEmpty(flag)) flag = true;
		upload_object_store._load_uploadObjectAllStore = flag;
	};
	upload_object_store.getLoadUploadObjectAllStoreFlag = function(){
		return upload_object_store._load_uploadObjectAllStore;
	};

	upload_object_store.setUploadObjectLastSorters = function(sorters){
		if(Ext.isEmpty(sorters)) sorters = [];
		upload_object_store._lastSorters = sorters;
	};
	upload_object_store.getUploadObjectLastSorters = function(){
		return upload_object_store._lastSorters;
	};

	upload_object_store.filters.on({
		add: function(index, o, key, eOpts){
			upload_object_store.setLoadUploadObjectAllStoreFlag();
		},
		clear: function(index, o, key, eOpts){
			upload_object_store.setLoadUploadObjectAllStoreFlag();
		},
		remove: function(index, o, key, eOpts){
			upload_object_store.setLoadUploadObjectAllStoreFlag();
		},
		replace: function(index, o, key, eOpts){
			upload_object_store.setLoadUploadObjectAllStoreFlag();
		},
		scope: upload_object_store
	});
	upload_object_store.sorters.on({
		add: function(index, o, key, eOpts){
			upload_object_store.setLoadUploadObjectAllStoreFlag();
		},
		clear: function(index, o, key, eOpts){
			upload_object_store.setLoadUploadObjectAllStoreFlag();
		},
		remove: function(index, o, key, eOpts){
			upload_object_store.setLoadUploadObjectAllStoreFlag();
		},
		replace: function(index, o, key, eOpts){
			upload_object_store.setLoadUploadObjectAllStoreFlag();
		},
		scope: upload_object_store
	});

	var upload_object_all_store = Ext.create('Ext.data.Store', {
		storeId: 'uploadObjectAllStore',
		model: 'EXTENSIONPARTS',
		sorters    : [{
			property: 'artg_name',
			direction: 'ASC'
		},{
			property: 'art_name',
			direction: 'ASC'
		}],
		autoLoad: false,
		autoSync: false,

//		remoteFilter: false,
//		remoteSort: false,
//		filterOnLoad : false,
//		sortOnFilter: false,
//		sortOnLoad: false,

		remoteFilter: false,
		remoteSort: false,
		filterOnLoad : false,
		sortOnFilter: false,
		sortOnLoad: false,

		proxy: {
			type: 'ajax',
			timeout: 300000,
			pageParam: undefined,
			startParam: undefined,
			limitParam: undefined,
//			sortParam: undefined,
			groupParam: undefined,
//			filterParam: undefined,
			api: {
				create  : 'api-upload-file-list.cgi?cmd=create',
				read    : 'api-upload-file-list.cgi?cmd=read',
				update  : 'api-upload-file-list.cgi?cmd=update',
				destroy : 'api-upload-file-list.cgi?cmd=destroy',
			},
			noCache: false,
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
			}
		},
		listeners: {
			beforeload: function(store,operation,eOpts){

				if(!self.beforeloadStore(store)) return false;
//				console.log("uploadObjectAllStore.beforeload():["+store.loading+"]");

				if (store.loading && store.getLastRequestOptions()) {
					var requests = Ext.Ajax.requests;
					var id;
					for(id in requests){
						if(requests.hasOwnProperty(id) && requests[id].options == store.getLastRequestOptions()){
							Ext.Ajax.abort(requests[id]);
//							console.log("uploadObjectAllStore.beforeload():Ext.Ajax.abort()");
						}
					}
				}
/*
    doRequest: function(operation, callback, scope) {
        var writer  = this.getWriter(),
            request = this.buildRequest(operation);

        if (operation.allowWrite()) {
            request = writer.write(request);
        }

        Ext.apply(request, {
            binary        : this.binary,
            headers       : this.headers,
            timeout       : this.timeout,
            scope         : this,
            callback      : this.createRequestCallback(request, operation, callback, scope),
            method        : this.getMethod(request),
            disableCaching: false // explicitly set it to false, ServerProxy handles caching
        });

        Ext.Ajax.request(request);

        return request;
    },
*/

				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams.model;
				delete p.extraParams.version;
				delete p.extraParams.ag_data;
				delete p.extraParams.tree;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;

				var groups = [];
				var artg_ids = [];

//				var filter = upload_group_store._getFilters();
//				upload_group_store._setFilters([{
//					property: 'artg_delcause',
//					value: null
//				},{
//					property: 'selected',
//					value: true
//				}]);
				upload_group_store.each(function(r){
					if(r.get('selected')){
						groups.push(r.get('artg_name'));
						artg_ids.push(r.get('artg_id'));
					}
				});
//				upload_group_store._setFilters(filter);

				var selected_art_ids = {};

				store.each(function(r){
					if(!r.get('selected')) return true;
					var artg_id = r.get('artg_id');
					selected_art_ids[artg_id] = selected_art_ids[artg_id] || {};
					selected_art_ids[artg_id][r.get('art_id')] = null;
				});

				p.extraParams.groups = Ext.encode(groups);
				p.extraParams.artg_ids = Ext.encode(artg_ids);
				p.extraParams.selected_art_ids = Ext.encode(selected_art_ids);

				delete p.extraParams.selected;
				delete p.extraParams.current_datas;
				delete p.extraParams.model;
				delete p.extraParams.version;
				delete p.extraParams.ag_data;
				delete p.extraParams.tree;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;

				upload_object_grid.setLoading(true);
//				console.log("beforeload()");

//				console.log("uploadObjectAllStore.beforeload()");


				var beforerequest = function(conn,options,eOpts){
					store.setLastRequestOptions(options);
				};
				Ext.Ajax.on({
					beforerequest: beforerequest,
					single: true,
					scope: self
				});


			},
			datachanged : function(store,options){
			},
			load: function(store,records,successful,eOpts){
				upload_object_grid.setLoading(false);
//				console.log("load()");
			},
			update: function(store,record,operation,eOpts){
//				console.log("update()");
			},
			write: function(store,operation,eOpts){
//				console.log("write()");
			}
		}
	});
	upload_object_all_store.setLastRequestOptions = function(options){
		upload_object_all_store._LastRequestOptions = options;
	};
	upload_object_all_store.getLastRequestOptions = function(){
		return upload_object_all_store._LastRequestOptions;
	};


	var extension_parts_store = Ext.create('Ext.data.ArrayStore', {
		model: 'EXTENSIONPARTS',
		storeId : 'extensionPartsStore',
		listeners: {
			add: function(store,records,index,eOpts){
//				console.log("extension_parts_store.add():["+records.length+"]");
//				self.setHashTask.delay(0);
				self.update_pallet_store(records);
			},
			remove: function(store,record,index,eOpts){
//				console.log("extension_parts_store.remove()");
//				self.setHashTask.delay(0);
			},
			update: function(store,record,operation){
				if(operation==Ext.data.Record.EDIT){
				}else if(operation==Ext.data.Record.COMMIT){
//					console.log("extension_parts_store.update():["+operation+"]");
					self.update_pallet_store([record]);

				}
			}
		}
	});

	Ext.create('Ext.data.TreeStore', {
		autoLoad: false,
		storeId: 'treePanelStore',
		model: 'BP3D_TREE',
//		lazyFill: true,
		proxy: {
			type: 'ajax',
//				url: 'get-bp3d-tree.cgi',
			timeout: 300000,
			api: {
				create  : 'api-bp3d-tree.cgi?cmd=create',
				read    : 'api-bp3d-tree.cgi?cmd=read',
				update  : 'api-bp3d-tree.cgi?cmd=update',
				destroy : 'api-bp3d-tree.cgi?cmd=destroy',
			},
			actionMethods : {
				create : 'POST',
				read   : 'POST',
				update : 'POST',
				destroy: 'POST'
			}
		},
		root: {
			allowDrag: false,
			allowDrop: false,
			depth: 0,
//				expandable: true,
//			expanded: true,
			expanded: false,
			iconCls: 'tree-folder',
			root: true,
			text: '/',
			name: 'root',
			cdi_name: 'root'
		},

		listeners: {
			beforeload: function(store, operation, eOpts){
				if(operation.node.isRoot()){
//					console.log('treePanelStore.beforeload()');
//					console.log(operation);
//					console.log(eOpts);
//					console.log(store.isLoading());
//					console.trace();
					if(store.isLoading()) return false;
				}
				if(self.beforeloadStore(store)){
//					console.log("treePanelStore.beforeload():["+operation.node.data.cdi_name+"]");
					var p = store.getProxy();
					p.extraParams = p.extraParams || {};
					p.extraParams.cdi_name = operation.node.data.cdi_name;
					p.extraParams.use_checkbox = (self.getPressedLinkedUploadPartsButton()!==true);
					p.extraParams.path = operation.node.getPath('cdi_name','/');
//					console.log(p.extraParams);

					delete p.extraParams.current_datas;
					delete p.extraParams.model;
					delete p.extraParams.version;
					delete p.extraParams.ag_data;
					delete p.extraParams.tree;
					delete p.extraParams._ExtVerMajor;
					delete p.extraParams._ExtVerMinor;
					delete p.extraParams._ExtVerPatch;
					delete p.extraParams._ExtVerBuild;
					delete p.extraParams._ExtVerRelease;
				}else{
					return false;
				}
			},
			datachanged : function(store,options){
//					console.log("treePanelStore.datachanged()");
			},
			load: function(store, node, records, successful, eOpts){
				if(node.isRoot()){
//					console.log('treePanelStore.load():['+successful+']');
//					console.log(node);
//					console.log(records);
//					console.log(eOpts);
					node.expand();
				}
				if(successful){
					var parts_tree_panel = Ext.getCmp('parts-tree-panel');
					self.load_pallet_store_records(records,store,parts_tree_panel);
				}
//					console.log("load()");
//					console.log(records);
//					console.log(successful);
			},
			update: function(store,record,operation,modifiedFieldNames,eOpts){
//					console.log("treePanelStore.record():["+operation+"]");
			},
			scope : self
		}
	});

	var parts_grid_store = Ext.create('Ext.data.Store', {
		storeId: 'partsGridStore',
		autoDestroy: true,
		autoLoad: false,
		model: 'BP3D',
		pageSize: DEF_PARTS_GRID_PAGE_SIZE,
		remoteSort:true,	//trueにしないとソートできない
		sorters: [{
			property: 'cdi_name_e',
			direction: 'ASC'
		}],
		proxy: {
			type: 'ajax',
			timeout: 300000,
			api: {
				create  : 'api-bp3d-list.cgi?cmd=create',
				read    : 'api-bp3d-list.cgi?cmd=read',
				update  : 'api-bp3d-list.cgi?cmd=update',
				destroy : 'api-bp3d-list.cgi?cmd=destroy',
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
			listeners: {
				metachange : function(){
				}
			}
		},
		listeners: {
			beforeload: function(store,operation,eOpts){
				if(!self.beforeloadStore(store)) return false;

				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.selected;
				delete p.extraParams.current_datas;
				delete p.extraParams.model;
				delete p.extraParams.version;
				delete p.extraParams.ag_data;
				delete p.extraParams.tree;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;

				var records = [];
				pallet_store.each(function(r){
					if(r.get('version')!=p.extraParams.version) return true;
					records.push({
						rep_id   : r.get('rep_id'),
						cdi_name : r.get('cdi_name'),
						color    : r.get('color'),
						opacity  : r.get('opacity'),
						remove   : r.get('remove'),
						selected : r.get('selected')
					});
				});
				p.extraParams.selected = Ext.encode(records);

				var parts_grid = Ext.getCmp('parts-grid');
				parts_grid.setLoading(true);
//				if(Ext.getCmp('parts-tab-panel').getActiveTab()==parts_grid) parts_grid.setLoading(true);

//				Ext.getCmp('parts-tab-panel').setLoading(true);
			},
			datachanged : function(store,options){
//				console.log("parts_grid_store.datachanged():["+store.getCount()+"]");
				var parts_grid = Ext.getCmp('parts-grid');
				self.load_pallet_store_records(store.getRange(),store,parts_grid);
			},
			load: function(store,records,successful,eOpts){
//				console.log("parts_grid_store.load():["+(records?records.length:0)+"]");
//				console.log(records);
//				if(successful){
//					self.load_pallet_store_records(records,store,parts_grid);
//				}

				var parts_grid = Ext.getCmp('parts-grid');
				parts_grid.setLoading(false);
//				Ext.getCmp('parts-tab-panel').setLoading(bp3d_search_store.isLoading());
			},
			update : function(store,record,operation){
//				console.log("parts_grid_store():["+operation+"]");
				if(operation==Ext.data.Record.EDIT){
				}else if(operation==Ext.data.Record.COMMIT){

//					Ext.defer(self.update_pallet_store,1,this,[[record]]);

					Ext.defer(function(){
						if(self.getPressedLinkedUploadPartsButton()){
							self.checkedUploadGroup([record]);
						}else{
							self.update_pallet_store([record]);
//							self.checkedUploadGroup([record],true);
						}
					},100);


				}
			}
		}
	});

	var bp3d_search_store = Ext.create('Ext.data.Store', {
		storeId: 'bp3dSearchStore',
//		model: 'FMA',
		model: 'BP3D',
		pageSize: DEF_FMA_SEARCH_GRID_PAGE_SIZE,
		remoteSort: true,
		sorters: [{
			property: 'cdi_name_e',
			direction: 'ASC'
		}],
		proxy: {
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
		},
		listeners: {
			beforeload: function(store,operation,eOpts){
				if(!self.beforeloadStore(store)) return false;

				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams.model;
				delete p.extraParams.version;
				delete p.extraParams.ag_data;
				delete p.extraParams.tree;
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
				if(Ext.isEmpty(self.bp3d_search_grid_renderer_params.searchValue)) return false;

				var bp3d_search_grid = Ext.getCmp('bp3d-search-grid');
				bp3d_search_grid.setLoading(true);
			},
			datachanged : function(store,options){
				var bp3d_search_grid = Ext.getCmp('bp3d-search-grid');
				self.load_pallet_store_records(store.getRange(),store,bp3d_search_grid);
			},
			load: function(store,records,successful,eOpts){
				var bp3d_search_grid = Ext.getCmp('bp3d-search-grid');
				bp3d_search_grid.setLoading(false);
			},
			update: function(store,record,operation){
				if(operation==Ext.data.Record.EDIT){
				}else if(operation==Ext.data.Record.COMMIT){

					Ext.defer(function(){
						if(self.getPressedLinkedUploadPartsButton()){
							self.checkedUploadGroup([record]);
						}else{
							self.update_pallet_store([record]);
							var parts_grid = Ext.getCmp('parts-grid');
							self.updata_grid_store_record(record,parts_grid_store,parts_grid);
//							self.checkedUploadGroup([record],true);
						}
					},100);

				}
			}
		}
	});

	Ext.create('Ext.data.Store', {
		storeId: 'fmaGridStore',
		autoSync: true,
		autoLoad: false,
		model: 'FMA',
		pageSize: DEF_PARTS_GRID_PAGE_SIZE,
		remoteSort: true,	//trueにしないとソートできない
		sorters: [{
			property: 'cdi_name_e',
			direction: 'ASC'
		}],
		proxy: {
			type: 'ajax',
			timeout: 300000,
			api: {
				create  : 'api-fma-list.cgi?cmd=create',
				read    : 'api-fma-list.cgi?cmd=read',
				update  : 'api-fma-list.cgi?cmd=update',
				destroy : 'api-fma-list.cgi?cmd=destroy',
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
				allowSingle: false,
				encode: true,
				type: 'json',
				root: 'datas',
				writeAllFields: true
			},
			listeners: {
				metachange : function(){
				}
			}
		},
		listeners: {
			beforeload: function(store,operation,eOpts){
				if(!self.beforeloadStore(store)) return false;
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams.model;
				delete p.extraParams.version;
				delete p.extraParams.ag_data;
				delete p.extraParams.tree;
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
			update : function(store,record,operation){
			}
		}
	});

	Ext.create('Ext.data.Store', {
		storeId: 'modelStore',
		autoLoad: true,
		model: 'MODEL',
		data : DEF_MODEL_DATAS,
		proxy: {
			type: 'memory',
			reader: {
				type: 'json',
				root: 'datas'
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
		storeId: 'datasetStore',
		model: 'VERSION',
		proxy: {
			type: 'ajax',
			url : 'api-dataset-store.cgi',
			timeout: 300000,
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
				root: 'datas'
			},
			writer: {
				allowSingle: false,
				encode: true,
				type: 'json',
				root: 'datas',
				writeAllFields: true
			}
		}
	});

	Ext.create('Ext.data.Store', {
		autoLoad: false,
		storeId: 'rendererHostsMngStore',
		fields: [
			{name: 'rh_id',      type: 'int'},
			{name: 'rh_ip',      type: 'string'},
			{name: 'rh_use',     type: 'boolean', defaultValue: false},
			{name: 'rh_comment', type: 'string'},
			{name: 'rh_entry', type: 'date', dateFormat: 'timestamp'}
		],
		proxy: {
			timeout: 300000,
			type: 'ajax',
			api: {
				create  : 'api-renderer-hosts-store.cgi?cmd=create',
				read    : 'api-renderer-hosts-store.cgi?cmd=read',
				update  : 'api-renderer-hosts-store.cgi?cmd=update',
				destroy : 'api-renderer-hosts-store.cgi?cmd=destroy',
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
			}
		}
	});

	var datasetMngStore = Ext.create('Ext.data.Store', {
		autoLoad: false,
		storeId: 'datasetMngStore',
		model: 'VERSION',
		sorters: [{
			property: 'mv_order',
			direction: 'ASC'
		},{
			property: 'fmt_version',
			direction: 'DESC'
		}],
		proxy: {
			timeout: 300000,
			type: 'ajax',
			api: {
				create  : 'api-dataset-store.cgi?cmd=create',
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
			}
		}
	});

	Ext.create('Ext.data.Store', {
		storeId: 'treeStore',
		autoLoad: false,
		model: 'TREE',
		proxy: {
			type: 'ajax',
			url : 'buildup_tree-store.cgi',
			timeout: 300000,
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
				root: 'datas'
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
			beforeload: function(store,operation,eOpts){
//				var md_id;
//				var mv_id;
//				var mr_id;
				var ci_id;
				var cb_id;

				var field = Ext.getCmp('version-combobox');
				if(field && field.rendered){
					try{
						var record = field.findRecordByValue(field.getValue());
						if(record){
//							model = record.get('model');
//							version = record.get('version');
//							ag_data = record.get('data');
//							md_id = record.get('md_id');
//							mv_id = record.get('mv_id');
//							mr_id = record.get('mr_id');
							ci_id = record.get('ci_id');
							cb_id = record.get('cb_id');
						}else{
							return false;
						}
					}catch(e){
						if(!field.isHidden()){
							console.error(e);
							return false;
						}
					}
				}else{
					return false;
				}
				var p = store.getProxy();
//				p.extraParams.model = model;
//				p.extraParams.version = version;
//				p.extraParams.ag_data = ag_data;
//				p.extraParams.md_id = md_id;
//				p.extraParams.mv_id = mv_id;
//				p.extraParams.mr_id = mr_id;
				p.extraParams.ci_id = ci_id;
				p.extraParams.cb_id = cb_id;
			}
		}
	});

	Ext.create('Ext.data.Store', {
		autoLoad: true,
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
		proxy: {
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
			}
		}
	});

	var pallet_store = Ext.create('Ext.data.ArrayStore', {
		storeId: 'palletPartsStore',
		autoDestroy: true,
		model: 'PALLETPARTS',
		listeners: {
			add: function(store,records,index,eOpts){
				self.setHashTask.delay(0);
				self.update_localdb_pallet();
			},
			remove: function(store,record,index,eOpts){
				self.setHashTask.delay(0);
				self.update_localdb_pallet();
			},
			update: function(store,record,operation){
				if(operation==Ext.data.Record.EDIT){
//					console.log(record.getChanges());
				}else if(operation==Ext.data.Record.COMMIT){
					self.setHashTask.delay(0);
					self.update_localdb_pallet();
				}
			}
		}
	});

	Ext.create('Ext.data.Store', {
		storeId: 'pickStore',
		model: 'PALLETPARTS',
		listeners: {
			datachanged: function(store, eOpts){
//					console.log("pickStore.datachanged():["+store.getCount()+"]");
				if(store.getCount()<=0) return;
				self.load_pallet_store_records(store.getRange(),store,pick_panel);
			},
			load: function(store, records, successful, eOpts){
//					console.log("pickStore.load():["+store.getCount()+"]");
			},
			refresh: function(store, eOpts){
//					console.log("pickStore.refresh():["+store.getCount()+"]");
			},
			add: function(store, records, index, eOpts){
//					console.log("pickStore.add():["+store.getCount()+"]");
//					self.setHashTask.delay(250);
			},
			remove: function(store, record, index, eOpts){
//					console.log("pickStore.remove():["+store.getCount()+"]");
//					self.setHashTask.delay(250);
			},
			update: function(store, record, operation, modifiedFieldNames, eOpts){
//					console.log("pickStore.update():["+store.getCount()+"]");
				if(operation==Ext.data.Record.EDIT){
				}else if(operation==Ext.data.Record.COMMIT){
//						self.setHashTask.delay(250);
					self.update_pallet_store([record],true,true);
				}
			}
		}
	});

	Ext.create('Ext.data.ArrayStore', {
		storeId: 'pickPageStore',
		fields: [{
			name: 'display',
			type: 'string'
		},{
			name: 'value',
			type: 'int'
		},{
			name: 'records'
		}],
		listeners: {
			datachanged: function(store, eOpts){
//							console.log("pickPageStore.datachanged():["+store.getCount()+"]");
				var count = store.getCount();
				var pickPageCombo = Ext.getCmp('pick-page-combobox');
//							console.log("pickPageStore.datachanged():["+pickPageCombo+"]");
				if(pickPageCombo){
					pickPageCombo.setValue(0);
					pickPageCombo.setValue(count==0?0:1);
					pickPageCombo.setDisabled(count==0);
				}
			},
			load: function(store, records, successful, eOpts){
//							console.log("pickPageStore.load():["+store.getCount()+"]");
			},
			refresh: function(store, eOpts){
//							console.log("pickPageStore.refresh():["+store.getCount()+"]");
			}
		}
	});

	Ext.create('Ext.data.ArrayStore', {
		storeId: 'pickPageStore',
		fields: [{
			name: 'display',
			type: 'string'
		},{
			name: 'value',
			type: 'int'
		},{
			name: 'records'
		}],
		listeners: {
			datachanged: function(store, eOpts){
//							console.log("pickPageStore.datachanged():["+store.getCount()+"]");
				var count = store.getCount();
				var pickPageCombo = Ext.getCmp('pick-page-combobox');
//							console.log("pickPageStore.datachanged():["+pickPageCombo+"]");
				if(pickPageCombo){
					pickPageCombo.setValue(0);
					pickPageCombo.setValue(count==0?0:1);
					pickPageCombo.setDisabled(count==0);
				}
			},
			load: function(store, records, successful, eOpts){
//							console.log("pickPageStore.load():["+store.getCount()+"]");
			},
			refresh: function(store, eOpts){
//							console.log("pickPageStore.refresh():["+store.getCount()+"]");
			}
		}
	});


	Ext.create('Ext.data.Store', {
		storeId: 'pinStore',
		model: 'PIN',
		listeners: {
			add: function(store, records, index, eOpts){
				self.setHashTask.delay(250);
			},
			remove: function(store, record, index, eOpts){
				self.setHashTask.delay(250);
			},
			update: function(store, record, operation, modifiedFieldNames, eOpts){
				if(operation==Ext.data.Record.EDIT){
				}else if(operation==Ext.data.Record.COMMIT){
					self.setHashTask.delay(250);
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
		proxy: {
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
		},
		listeners: {
			beforeload: function(store,operation,eOpts){
				if(!self.beforeloadStore(store)) return false;
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams.model;
				delete p.extraParams.version;
				delete p.extraParams.ag_data;
				delete p.extraParams.tree;
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
		storeId: 'errorTwitterStore',
		model: 'ERROR_TWITTER',
		pageSize: DEF_ERROR_TWITTER_GRID_PAGE_SIZE,
		autoLoad: false,
		remoteFilter: true,
		remoteSort: true,
		filterOnLoad: true,
		sortOnFilter: true,
		sortOnLoad: true,
		sorters: [{
			property: 'tw_date',
			direction: 'DESC'
		},{
			property: 'rep_id',
			direction: 'ASC'
		}],
		proxy: {
			type: 'ajax',
			timeout: 300000,
			api: {
				create  : 'api-error-twitter-store.cgi?cmd=create',
				read    : 'api-error-twitter-store.cgi?cmd=read',
				update  : 'api-error-twitter-store.cgi?cmd=update',
				destroy : 'api-error-twitter-store.cgi?cmd=destroy',
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
				allowSingle: false,
				encode: true,
				type: 'json',
				root: 'datas',
				writeAllFields: true
			},
			listeners: {
				metachange : function(){
				}
			}
		},
		listeners: {
			beforeload: function(store,operation,eOpts){
				if(!self.beforeloadStore(store)) return false;
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams.model;
				delete p.extraParams.version;
				delete p.extraParams.ag_data;
				delete p.extraParams.tree;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;
			}
		}
	});

	Ext.create('Ext.data.Store', {
		storeId: 'findObjectStore',
		model: 'EXTENSIONPARTS',
		pageSize: DEF_FIND_FILE_PAGE_SIZE,
		autoLoad: false,
		autoSync: false,
		remoteFilter: true,
		remoteSort: true,
		filterOnLoad : false,
		sortOnFilter: false,
		sortOnLoad: false,
//		sorters: [{
//			property: 'diff_volume',
//			direction: 'ASC'
//		}],
		proxy: {
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
			}
		},

		listeners: {
			beforeload: function(store,operation,eOpts){
//				if(!self.beforeloadStore(store)) return false;

				var findObjectStore = Ext.data.StoreManager.lookup('findObjectStore');
				var findObjectAllStore = Ext.data.StoreManager.lookup('findObjectAllStore');

				Ext.defer(function(){
					if(operation.filters.length>0){
						findObjectAllStore.filter(operation.filters);
					}else{
						findObjectAllStore.clearFilter();
					}
					if(operation.sorters.length>0){
						findObjectAllStore.sort(operation.sorters);
					}
//					findObjectStore.totalCount = findObjectAllStore.getTotalCount();
					findObjectStore.totalCount = findObjectAllStore.getCount();

					var loadRecords = [];
					Ext.each(findObjectAllStore.getRange(operation.start,operation.start+operation.limit-1),function(r,i,a){
						var rec = r.copy();
						Ext.data.Model.id(rec);
						loadRecords.push(rec);
					});
					findObjectStore.loadRecords(loadRecords,operation);

					findObjectStore.fireEvent('load', findObjectStore, findObjectStore.getRange(), true);
				},10);
				return false;

			},
			datachanged : function(store,options){
//				self.load_pallet_store_records(store.getRange(),store,upload_object_grid);
			},
			load: function(store,records,successful,eOpts){
//				upload_object_grid.setLoading(false);
			},
			update: function(store,record,operation){
//				if(operation==Ext.data.Record.EDIT){
//				}else if(operation==Ext.data.Record.COMMIT){
//					self.extension_parts_store_update(record,true,false);
//				}
			}
		}
	});

	Ext.create('Ext.data.Store', {
		storeId: 'findObjectAllStore',
		model: 'EXTENSIONPARTS',
		pageSize: 50,
		autoLoad: false,
		autoSync: false,
		remoteFilter: false,
		remoteSort: false,
		filterOnLoad : false,
		sortOnFilter: false,
		sortOnLoad: false,
		proxy: {
			type: 'ajax',
			timeout: 30000*2*5,//30sec * 2 * 10
			pageParam: undefined,
//			startParam: undefined,
//			limitParam: undefined,
			sortParam: undefined,
			groupParam: undefined,
			filterParam: undefined,
			api: {
				create  : 'get-upload-file-search.cgi?cmd=create',
				read    : 'get-upload-file-search.cgi?cmd=read',
				update  : 'get-upload-file-search.cgi?cmd=update',
				destroy : 'get-upload-file-search.cgi?cmd=destroy',
			},
//			url: 'get-upload-file-search.cgi',
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
			}
		},

		listeners: {
			beforeload: function(store,operation,eOpts){
				if(!self.beforeloadStore(store)) return false;
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams.model;
				delete p.extraParams.version;
				delete p.extraParams.ag_data;
				delete p.extraParams.tree;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;
			},
			datachanged: function(store,options){
			},
			load: function(store,records,successful,eOpts){
			},
			update: function(store,record,operation){
			}
		}
	});


	Ext.create('Ext.data.Store', {
		storeId: 'pickSearchStore',
		model: 'EXTENSIONPARTS',
//		pageSize: DEF_FIND_FILE_PAGE_SIZE,
		pageSize: 1000,
		autoLoad: false,
		autoSync: false,
		remoteFilter: true,
		remoteSort: true,
		filterOnLoad : false,
		sortOnFilter: false,
		sortOnLoad: false,
//		sorters: [{
//			property: 'diff_volume',
//			direction: 'ASC'
//		}],
		proxy: {
			type: 'ajax',
			timeout: 300000,
			api: {
				create  : 'api-upload-file-list.cgi?cmd=create',
				read    : 'api-upload-file-list.cgi?cmd=read',
				update  : 'api-upload-file-list.cgi?cmd=update',
				destroy : 'api-upload-file-list.cgi?cmd=destroy',
			},
			pageParam: undefined,
			startParam: undefined,
			limitParam: undefined,
			sortParam: undefined,
			groupParam: undefined,
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
			}
		},

		listeners: {
			beforeload: function(store,operation,eOpts){
//				if(!self.beforeloadStore(store)) return false;

				var pickSearchStore = Ext.data.StoreManager.lookup('pickSearchStore');
				var pickSearchAllStore = Ext.data.StoreManager.lookup('pickSearchAllStore');

				Ext.defer(function(){
					if(operation.filters.length>0){
						pickSearchAllStore.filter(operation.filters);
					}else{
						pickSearchAllStore.clearFilter();
					}
					if(operation.sorters.length>0){
						pickSearchAllStore.sort(operation.sorters);
					}
//					findObjectStore.totalCount = findObjectAllStore.getTotalCount();
					pickSearchStore.totalCount = pickSearchAllStore.getCount();

					var start = operation.start || 0;
					var limit = operation.limit || pickSearchAllStore.getCount();

					var loadRecords = [];
					Ext.each(pickSearchAllStore.getRange(start,start+limit-1),function(r,i,a){
						var rec = r.copy();
						Ext.data.Model.id(rec);
						loadRecords.push(rec);
					});
					pickSearchStore.loadRecords(loadRecords,operation);

					pickSearchStore.fireEvent('load', pickSearchStore, pickSearchStore.getRange(), true);
				},10);
				return false;

			},
			datachanged : function(store,options){
//				self.load_pallet_store_records(store.getRange(),store,upload_object_grid);
			},
			load: function(store,records,successful,eOpts){
//				upload_object_grid.setLoading(false);
			},
			update: function(store,record,operation){
//				if(operation==Ext.data.Record.EDIT){
//				}else if(operation==Ext.data.Record.COMMIT){
//					self.extension_parts_store_update(record,true,false);
//				}
			}
		}
	});

	Ext.create('Ext.data.Store', {
		storeId: 'pickSearchAllStore',
		model: 'EXTENSIONPARTS',
//		pageSize: 10,
		autoLoad: false,
		autoSync: false,
		remoteFilter: false,
		remoteSort: false,
		filterOnLoad : false,
		sortOnFilter: false,
		sortOnLoad: false,
		proxy: {
			type: 'ajax',
			timeout: 30000*2*5,//30sec * 2 * 10
			pageParam: undefined,
//			startParam: undefined,
//			limitParam: undefined,
			sortParam: undefined,
			groupParam: undefined,
			filterParam: undefined,
//			api: {
//				create  : 'api-upload-file-list.cgi?cmd=create',
//				read    : 'api-upload-file-list.cgi?cmd=read',
//				update  : 'api-upload-file-list.cgi?cmd=update',
//				destroy : 'api-upload-file-list.cgi?cmd=destroy',
//			},
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
			}
		},

		listeners: {
			beforeload: function(store,operation,eOpts){
				if(!self.beforeloadStore(store)) return false;
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams.model;
				delete p.extraParams.version;
				delete p.extraParams.ag_data;
				delete p.extraParams.tree;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;
			}
		}
	});

	Ext.create('Ext.data.Store', {
		storeId: 'recalcStore',
		autoSync: false,
		autoLoad: false,
		model: 'RECALC',
		remoteSort: false,
		sorters: [{
			property: 'bul_id',
			direction: 'ASC'
		},{
			property: 'but_depth',
			direction: 'DESC'
		}],
		proxy: {
			type: 'ajax',
			timeout: 30000*2*5*2,//30sec * 2 * 10
			api: {
//				create  : 'api-recalculation.cgi?cmd=create',
				read    : 'api-recalculation.cgi?cmd=read',
//				update  : 'api-recalculation.cgi?cmd=update',
//				destroy : 'api-recalculation.cgi?cmd=destroy',
			},
			pageParam: undefined,
			startParam: undefined,
			limitParam: undefined,
			sortParam: undefined,
			groupParam: undefined,
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
				totalProperty:'total',
				listeners: {
					exception : function(){
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
			listeners: {
				metachange : function(){
				}
			}
		},
		listeners: {
			beforeload: function(store,operation,eOpts){
				if(!self.beforeloadStore(store)) return false;
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams.model;
				delete p.extraParams.version;
				delete p.extraParams.ag_data;
				delete p.extraParams.tree;
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
			update : function(store,record,operation){
			}
		}
	});

	Ext.create('Ext.data.TreeStore', {
		autoLoad: false,
		autoSync: true,
		storeId: 'uploadFolderTreePanelStore',
		model: 'UPLOAD_FOLDER_TREE',
		proxy: {
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
			}
		},
		root: {
			allowDrag: false,
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
			beforesync: function(store,eOpts){
//				console.log('beforesync()');
			},
			write: function(store,operation,eOpts){
//				console.log('write()');
			},
			beforeload: function(store,operation,eOpts){
			},
			datachanged : function(store,options){
			},
			load: function(/*store,node,records,successful*/){


				var store, records, successful, operation, node, eOpts, i=0;
				if(Ext.getVersion().major>=5){
					store = arguments[i++];
					records = arguments[i++];
					successful = arguments[i++];
					operation = arguments[i++];
					node = arguments[i++];
					eOpts = arguments[i++];
				}else{
					store = arguments[i++];
					node = arguments[i++];
					records = arguments[i++];
					successful = arguments[i++];
					eOpts = arguments[i++];
				}

//				console.log('uploadFolderTreePanelStore:load():'+successful);
//				console.log(node);
//				console.log(records);
				if(successful){
					store.suspendAutoSync();
					store.suspendEvents(true);

					var uploadGroupStore = Ext.data.StoreManager.lookup('uploadGroupStore');
					var filter = uploadGroupStore._getFilters();
					uploadGroupStore._setFilters([{
						property: 'artg_delcause',
						value: null
					},{
						property: 'artf_id',
						value: node.get('artf_id')
					}]);
					node.set('artg_count', uploadGroupStore.getCount());
					node.commit();
					Ext.each(records,function(record){

						uploadGroupStore._setFilters([{
							property: 'artg_delcause',
							value: null
						},{
							property: 'artf_id',
							value: record.get('artf_id')
						}]);
						record.set('artg_count', uploadGroupStore.getCount());
						record.commit();

					});

					uploadGroupStore._setFilters(filter);
					store.resumeEvents();
					store.resumeAutoSync();
					return;
				}
				var proxy = store.getProxy();
				var rawData = proxy.getReader().rawData;
				if(Ext.isObject(rawData) && rawData.msg){
					Ext.Msg.show({
						title: 'Error ['+proxy.api.read+']',
						iconCls: 'tfolder',
						msg: rawData.msg,
						buttons: Ext.Msg.OK,
						icon: Ext.Msg.ERROR,
						fn: function(buttonId,text,opt){
						}
					});
				}
			},
			append: function(store, node, index, eOpts){
//				console.log(node);
			},
			update: function(store,record,operation,modifiedFieldNames,eOpts){
			},
			scope : self
		}
	});

	var fmaAllStore = Ext.create('Ext.data.Store', {
		storeId: 'fmaAllStore',
		autoSync: false,
		autoLoad: false,
		model: 'FMA_LIST',
//		pageSize: DEF_PARTS_GRID_PAGE_SIZE,
		remoteSort: false,	//trueにしないとソートできない
//		sorters: [{
//			property: 'cdi_name_e',
//			direction: 'ASC'
//		}],
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
		proxy: {
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
			listeners: {
				metachange : function(){
				}
			}
		},
		listeners: {
			beforeload: function(store,operation,eOpts){

				var button = Ext.getCmp('ag-pallet-fma-obj-link-button');
				if(button) button.setDisabled(true);

				var versionCombobox = Ext.getCmp('version-combobox');
				var r = versionCombobox.findRecordByValue(versionCombobox.getValue());
				if(Ext.isBoolean(r) && !r) return false;

				var mv_frozen = r.data.mv_frozen;
				if(mv_frozen) return false;

				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				var ci_id = p.extraParams.ci_id;
				var cb_id = p.extraParams.cb_id;

				if(!self.beforeloadStore(store)) return false;
				delete p.extraParams.current_datas;
				delete p.extraParams.model;
				delete p.extraParams.version;
				delete p.extraParams.ag_data;
				delete p.extraParams.tree;
				delete p.extraParams._ExtVerMajor;
				delete p.extraParams._ExtVerMinor;
				delete p.extraParams._ExtVerPatch;
				delete p.extraParams._ExtVerBuild;
				delete p.extraParams._ExtVerRelease;

				if(Ext.isEmpty(p.extraParams.ci_id) || Ext.isEmpty(p.extraParams.cb_id)) return false;

				//読み込み済みのデータと条件が同じ場合は中止する
				if(store.getCount()>0 && ci_id === p.extraParams.ci_id && cb_id === p.extraParams.cb_id){
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
					var versionCombobox = Ext.getCmp('version-combobox');
					var r = versionCombobox.findRecordByValue(versionCombobox.getValue());
					if(r) mv_frozen = r.get('mv_frozen');

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
		proxy: {
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
		},
		listeners: {
			beforeload: function(store,operation,eOpts){
				if(!self.beforeloadStore(store)) return false;
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams.model;
				delete p.extraParams.version;
				delete p.extraParams.ag_data;
				delete p.extraParams.tree;
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
//			property: 'cdi_name',
//			direction: 'ASC',
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
		filters: [{
			filterFn: function(record){
				return record.get('mapped_obj') > 0;
			}
		}],
		proxy: {
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
		},
		listeners: {
			beforeload: function(store,operation,eOpts){
				if(!self.beforeloadStore(store)) return false;
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams.model;
				delete p.extraParams.version;
				delete p.extraParams.ag_data;
				delete p.extraParams.tree;
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
			property: 'cmp_id',
			direction: 'ASC'
		}],
		data: Ext.isArray(Ext.ag.Data.concept_art_map_part) && Ext.ag.Data.concept_art_map_part.length ? Ext.ag.Data.concept_art_map_part : null,
		proxy: {
			type: 'ajax',
			api: {
				read : 'get-concept-art-map-part.cgi?cmd=read',
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
		},
		listeners: {
			beforeload: function(store,operation,eOpts){
				if(!self.beforeloadStore(store)) return false;
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.current_datas;
				delete p.extraParams.model;
				delete p.extraParams.version;
				delete p.extraParams.ag_data;
				delete p.extraParams.tree;
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
	//2016-03-31 END
};

