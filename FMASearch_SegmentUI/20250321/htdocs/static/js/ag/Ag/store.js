Ext.define('Ag.Store', {
	override: 'Ag.Main',

	initStore : function(){
		var self = this;
		var timeout = 300000;

		Ext.Ajax.timeout = timeout;

		var make_ag_word = function(value,tooltip,className){
			if(Ext.isNumber(value)) value += '';
			if(Ext.isString(value) && value.length){
				if(Ext.isEmpty(tooltip)) tooltip = value;
				if(Ext.isEmpty(className)) className = 'bp3d-word';
				var replace_array_value = className==='bp3d-category' ? [value.trim()] : value.replace(/([^a-z0-9\s]+)/ig,' $1 ').trim().split(/\s+/);
				return Ext.util.Format.format(
					'<div class="bp3d-term" data-qtip="{0}">{1}</div>',Ext.String.htmlEncode(tooltip),
					Ext.Array.map(
						replace_array_value,
						function(str){
	//						if(str.length>2){
							if(Ext.isString(str) && str.length && str.match(/[a-z0-9]+/i)){
								return Ext.util.Format.format('<a href="#" class="bp3d-word-button {0}" data-value="{1}">{2}</a>',className,str.toLowerCase(),str);
							}
							else{
								return str;
							}
						}
					).join(' ')
				);
			}
			else{
				return value;
			}
		};

		var make_ag_words = function(value,className){
			if(Ext.isArray(value) && value.length){
				var rtn = [];
				Ext.Array.each(value, function(v,i){
					rtn.push(make_ag_word(value[i],value[i],className));
				});
				return rtn.join('');
			}
			else{
				return make_ag_word(value,value,className);
			}
		};

		var renderer_dataIndex_suffix = '';
//		var renderer_dataIndex_suffix = '_renderer';

		var _update_search_records = function(store,records,cities_ids,SEG2ART){
			console.time('_update_search_records');
			var add_datas = [];

			var p = store.getProxy();
			p.extraParams = p.extraParams || {};
			var version = p.extraParams['version'];
			if(Ext.isEmpty(version) && self.DEF_MODEL_VERSION_RECORD) version = self.DEF_MODEL_VERSION_RECORD.get(Ag.Def.VERSION_STRING_FIELD_ID);
			var ids;
			var art_ids;
			if(Ag.data.renderer && version){
				ids = Ag.data.renderer[version]['ids'];
				art_ids = Ag.data.renderer[version]['art_ids'];
			}
			if(Ext.isEmpty(art_ids)){
				Ext.Msg.alert('Error', 'Render file loading error!!');
				return add_datas;
			}

			var cities;
			var cities_store = Ext.data.StoreManager.lookup('cities-list-store');
			if(Ext.isArray(cities_ids) && cities_ids.length){
				cities = [];
				Ext.Array.each(cities_ids, function(cities_id){
//								cities.push(cities_store.getAt(cities_id-1).getData());	// unfound対応(2019/12/27)
					cities.push(cities_store.getAt(cities_id-0).getData());		// unfound対応(2019/12/27)
				});
			}
			else{
				cities = Ext.Array.map(cities_store.getRange(),function(record){ return record.getData(); });
			}
//						console.log(cities);
			var use_art_ids = {};
			var use_cdi_names = {};

			if(Ext.isArray(cities) && cities.length && SEG2ART && SEG2ART.CITIES){
				Ext.Array.each(cities, function(c){
					Ext.Object.each(SEG2ART.CITIES[c.name], function(art_id,value){
						if(art_ids[art_id]){
							if(Ext.isEmpty(use_art_ids[art_id])){
								use_art_ids[art_id] = {};
								use_art_ids[art_id][Ag.Def.ID_DATA_FIELD_ID] = art_ids[art_id][Ag.Def.ID_DATA_FIELD_ID];
								use_art_ids[art_id][Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID] = art_ids[art_id][Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID];
								use_art_ids[art_id]['cities_ids'] = [c['cities_id']];
							}
							else{
								use_art_ids[art_id]['cities_ids'].push(c['cities_id']);
							}

							if(Ext.isEmpty(use_cdi_names[art_ids[art_id][Ag.Def.ID_DATA_FIELD_ID]])){
								use_cdi_names[art_ids[art_id][Ag.Def.ID_DATA_FIELD_ID]] = {};
								use_cdi_names[art_ids[art_id][Ag.Def.ID_DATA_FIELD_ID]][Ag.Def.OBJ_ID_DATA_FIELD_ID] = art_id;
								use_cdi_names[art_ids[art_id][Ag.Def.ID_DATA_FIELD_ID]][Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID] = art_ids[art_id][Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID];
								use_cdi_names[art_ids[art_id][Ag.Def.ID_DATA_FIELD_ID]]['cities_ids'] = [c['cities_id']];
							}
							else{
								use_cdi_names[art_ids[art_id][Ag.Def.ID_DATA_FIELD_ID]]['cities_ids'].push(c['cities_id'])
							}
						}
					});
				});
			}
			else{
				Ext.Object.each(art_ids, function(art_id,value){
					use_art_ids[art_id] = value[Ag.Def.ID_DATA_FIELD_ID];
					use_cdi_names[value[Ag.Def.ID_DATA_FIELD_ID]] = art_id;
				});
			}
//						console.log(use_art_ids);
//						console.log(use_cdi_names);

			store.clearFilter(true);
			store.filterBy(function(record,id){
				return Ext.isDefined(use_cdi_names[record.get(Ag.Def.ID_DATA_FIELD_ID)]);
			});

//						var system_store = Ext.data.StoreManager.lookup('system-list-store');
//						var system_count = {};



			var use_system_ids;
/*
			var system_list_store = Ext.data.StoreManager.lookup('system-list-store');
			system_list_store.filter([{
				property: Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID,
				value: true
			}]);
			if(system_list_store.getCount()>0){
				use_system_ids = {};
				system_list_store.each(function(record){
					use_system_ids[record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID)] = record.getData();
				});
			}
			system_list_store.clearFilter();
*/

			store.suspendEvents(true);
			try{
				Ext.Array.each(records, function(record,idx,len){
					var cdi_name = record.get(Ag.Def.ID_DATA_FIELD_ID);
					if(Ext.isEmpty(cdi_name)){
						console.error(record.getData());
						return true;
					}
					var system_id = null;
					if(Ext.isObject(ids[cdi_name]) && Ext.isString(ids[cdi_name][Ag.Def.SYSTEM_ID_DATA_FIELD_ID])){
						system_id = ids[cdi_name][Ag.Def.SYSTEM_ID_DATA_FIELD_ID];
					}
					else{
						console.error(cdi_name);
					}

//								console.log(idx,len);
					record.beginEdit();

					var cdi_name_renderer = cdi_name;
					if(Ext.isString(cdi_name_renderer) && cdi_name_renderer.match(/^FMA([0-9]+)[A-Z]*\-[LRU]+$/)) cdi_name_renderer = RegExp.$1;
					if(Ext.isString(cdi_name_renderer) && cdi_name_renderer.match(/^FMA([0-9]+)\-.+$/)) cdi_name_renderer = RegExp.$1;
					if(Ext.isString(cdi_name_renderer) && cdi_name_renderer.match(/^FMA([0-9]+)$/)) cdi_name_renderer = RegExp.$1;
					record.set(Ag.Def.ID_DATA_FIELD_ID+'_renderer',cdi_name_renderer);


					var system10_id = null;
					var system10_name = null;
					if(Ext.isObject(ids[cdi_name])){
						if(Ext.isString(ids[cdi_name][Ag.Def.SYSTEM10_ID_DATA_FIELD_ID])) system10_id = ids[cdi_name][Ag.Def.SYSTEM10_ID_DATA_FIELD_ID];
						if(Ext.isString(ids[cdi_name][Ag.Def.SYSTEM10_NAME_DATA_FIELD_ID])) system10_name = ids[cdi_name][Ag.Def.SYSTEM10_NAME_DATA_FIELD_ID];
					}
//							if(Ext.isEmpty(system_count[system_id])) system_count[system_id] = 0;
//							system_count[system_id]++;

//					if(Ext.isObject(ids[cdi_name]) && Ext.isString(ids[cdi_name][Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID])){
					if(
						Ext.isEmpty(record.get(Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID)) &&
						Ext.isObject(ids[cdi_name]) &&
						Ext.isString(ids[cdi_name][Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID])
					){
						record.set(Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID, ids[cdi_name][Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID]);
					}

					record.set(Ag.Def.SYSTEM_ID_DATA_FIELD_ID, system_id);
					if(!Ext.isEmpty(renderer_dataIndex_suffix)){
						var system_id_renderer = system_id;
						if(Ext.isString(system_id_renderer) && system_id_renderer.length){
							if(system_id_renderer.match(/^[0-9]+(.+)$/)) system_id_renderer = RegExp.$1;
							if(system_id_renderer.match(/^_+(.+)$/)) system_id_renderer = RegExp.$1;
							record.set(Ag.Def.SYSTEM_ID_DATA_FIELD_ID+renderer_dataIndex_suffix, make_ag_words(system_id_renderer,'bp3d-system'));
						}
					}
					else{
						var system_id_renderer = system_id;
						if(Ext.isString(system_id_renderer) && system_id_renderer.length){
							if(system_id_renderer.match(/^[0-9]+(.+)$/)) system_id_renderer = RegExp.$1;
							if(system_id_renderer.match(/^_+(.+)$/)) system_id_renderer = RegExp.$1;
							record.set(Ag.Def.SYSTEM_ID_DATA_FIELD_ID+'_renderer', system_id_renderer);
						}
					}

					record.set(Ag.Def.SYSTEM10_ID_DATA_FIELD_ID, system10_id);
					record.set(Ag.Def.SYSTEM10_NAME_DATA_FIELD_ID, system10_name);
					if(!Ext.isEmpty(renderer_dataIndex_suffix)){
						record.set(Ag.Def.SYSTEM10_NAME_DATA_FIELD_ID+renderer_dataIndex_suffix, make_ag_words(system10_name,'bp3d-category'));
					}

					if(Ext.isObject(use_cdi_names[cdi_name])){
						record.set(Ag.Def.OBJ_CITIES_FIELD_ID, use_cdi_names[cdi_name]['cities_ids']);
						if(!Ext.isEmpty(renderer_dataIndex_suffix)){
							record.set(Ag.Def.OBJ_CITIES_FIELD_ID+renderer_dataIndex_suffix, make_ag_words(use_cdi_names[cdi_name]['cities_ids'],'bp3d-segment'));
						}
						if(Ext.isArray(use_cdi_names[cdi_name]['cities_ids']) && use_cdi_names[cdi_name]['cities_ids'].length){
							var segments = [];
							Ext.Array.each(use_cdi_names[cdi_name]['cities_ids'], function(cities_id){
								if(Ext.isString(Ag.data.citiesids2segment[cities_id]) && Ag.data.citiesids2segment[cities_id].length){
	//											record.set('segment', Ag.data.citiesids2segment[cities_id]);
									segments.push(Ag.data.citiesids2segment[cities_id]);
	//											console.log(cities_id, Ag.data.citiesids2segment[cities_id]);
									return false;
								}
							});
							if(segments.length) record.set('segment', segments);
						}
					}

					if(!Ext.isEmpty(renderer_dataIndex_suffix)){
						record.set('sub'+renderer_dataIndex_suffix, make_ag_words(record.get('sub'),'bp3d-sub'));

						record.set(Ag.Def.NAME_DATA_FIELD_ID+renderer_dataIndex_suffix, make_ag_words(record.get(Ag.Def.NAME_DATA_FIELD_ID),'bp3d-word'));
						record.set(Ag.Def.SYNONYM_DATA_FIELD_ID+renderer_dataIndex_suffix, make_ag_words(record.get(Ag.Def.SYNONYM_DATA_FIELD_ID),'bp3d-word'));

						var id_renderer = record.get(Ag.Def.ID_DATA_FIELD_ID);
						if(Ext.isString(id_renderer) && id_renderer.length){
							if(id_renderer.match(/^FMA([0-9]+)\-.+$/)) id_renderer = RegExp.$1;
							if(id_renderer.match(/^FMA([0-9]+)$/)) id_renderer = RegExp.$1;
							record.set(Ag.Def.ID_DATA_FIELD_ID+renderer_dataIndex_suffix, make_ag_words(id_renderer,'bp3d-fmaid'));
						}
					}

					if(Ext.isObject(use_cdi_names[cdi_name])){
						record.set(Ag.Def.OBJ_ID_DATA_FIELD_ID, use_cdi_names[cdi_name][Ag.Def.OBJ_ID_DATA_FIELD_ID]);
						if(!Ext.isEmpty(renderer_dataIndex_suffix)){
							var obj_renderer = use_cdi_names[cdi_name]['art_id'];
							if(Ext.isString(obj_renderer) && obj_renderer.length){
								record.set(Ag.Def.OBJ_ID_DATA_FIELD_ID+renderer_dataIndex_suffix, Ext.util.Format.format('<div data-qtip="{0}">{1}</div>',Ext.String.htmlEncode(obj_renderer.replace(/^([A-Z]+[0-9]+).*$/g,'$1')),obj_renderer));
							}
						}

						record.set(Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID, use_cdi_names[cdi_name][Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID]);
					}
					record.set(Ag.Def.OBJ_URL_DATA_FIELD_ID, null);

					record.set(Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID, false);
//							record.set(Ag.Def.USE_FOR_BOUNDING_BOX_FIELD_ID, false);


					if(Ext.isObject(ids[cdi_name])){
						if(Ext.isObject(ids[cdi_name][Ag.Def.CONCEPT_DATA_RELATION_DATA_FIELD_ID])){
							Ext.Object.each(ids[cdi_name][Ag.Def.CONCEPT_DATA_RELATION_DATA_FIELD_ID], function(relation,value){
								if(Ext.isObject(value)){
									Ext.Object.each(value, function(id,name){
										var v = record.get(relation);
										if(Ext.isEmpty(v)){
											v = [{id:id,name:name}];
										}
										else{
											v.push({id:id,name:name});
										}
										record.set(relation, v);

										if(relation == 'is_a' || relation == 'lexicalsuper') return true;
										v = record.get('part_of');
										if(Ext.isEmpty(v)){
											v = [{id:id,name:name}];
										}
										else{
											v.push({id:id,name:name});
										}
										record.set('part_of', v);
									});
								}
							});
						}
					}
					if(!Ext.isEmpty(renderer_dataIndex_suffix)){
						Ext.Array.each(['is_a','part_of'], function(relation){
							var value = record.get(relation);

							if(Ext.isString(value) && value.length){
								record.set(relation+renderer_dataIndex_suffix, make_ag_word(value,value,'bp3d-word'));
							}
							else if(Ext.isArray(value) && value.length){
								var rtn = [];
								Ext.Array.each(value, function(v,i){
									if(Ext.isString(v) && v.length){
										rtn.push(make_ag_word(v));
									}
									else if(Ext.isObject(v) && Ext.isString(v['name']) && v['name'].length){
										rtn.push(make_ag_word(v['name'],Ext.util.Format.format('{0} : {1}',v['id'],v['name'])));
									}
								});
								record.set(relation+renderer_dataIndex_suffix, rtn.join(''));
							}
						});
					}

					if(Ext.isObject(ids[cdi_name]) && Ext.isString(ids[cdi_name][Ag.Def.SYNONYM_DATA_FIELD_ID]) && ids[cdi_name][Ag.Def.SYNONYM_DATA_FIELD_ID].length){
						record.set(Ag.Def.SYNONYM_DATA_FIELD_ID, ids[cdi_name][Ag.Def.SYNONYM_DATA_FIELD_ID]);
					}
					else{
						record.set(Ag.Def.SYNONYM_DATA_FIELD_ID, null);
					}

					record.commit();
					record.endEdit();

					if(Ext.isObject(use_system_ids)){
						if(Ext.isEmpty(use_system_ids[system_id])) return true;
					}

					add_datas.push(record.getData());
				});
			}catch(e){
				console.error(e);
			}
			store.resumeEvents();

			console.timeEnd('_update_search_records');
			return add_datas;
		};

		var update_search_records = function(store,records){
			var p = store.getProxy();
			p.extraParams = p.extraParams || {};
			var version = p.extraParams['version'];
			if(Ext.isEmpty(version) && self.DEF_MODEL_VERSION_RECORD) version = self.DEF_MODEL_VERSION_RECORD.get(Ag.Def.VERSION_STRING_FIELD_ID);
			var cities_ids = p.extraParams['cities_ids'];
			var ids;
			var art_ids;
			if(Ag.data.renderer && version){
				ids = Ag.data.renderer[version]['ids'];
				art_ids = Ag.data.renderer[version]['art_ids'];
			}
			if(Ext.isEmpty(art_ids)){
				Ext.Msg.alert('Error', 'Render file loading error!!');
				return add_datas;
			}
			if(cities_ids) cities_ids = Ext.Array.map(cities_ids.split(/,/), function(v){ return v-0; });

			var SEG2ART = p.extraParams['SEG2ART']==='SEG2ART' ? Ag.data.SEG2ART : Ag.data.SEG2ART_INSIDE;

			var add_datas = _update_search_records(store,records,cities_ids,SEG2ART);


			var match_list_store = Ext.data.StoreManager.lookup(Ag.Def.CONCEPT_MATCH_LIST_STORE_ID);
//			match_list_store.removeAll();//add_datas.length?true:false);
			match_list_store.add(add_datas);
		};

		Ext.create('Ext.data.Store', {
			storeId: Ag.Def.CONCEPT_TERM_SEARCH_STORE_ID,
//			model: 'Ag.data.Model.CONCEPT_TERM',
			model: 'Ag.data.Model.CONCEPT_TERM_PALLET',
			pageSize: Ag.Def.CONCEPT_TERM_SEARCH_GRID_PAGE_SIZE,
			remoteSort: false,
			sorters: [{
				property: Ag.Def.NAME_DATA_FIELD_ID,
				direction: 'ASC'
			}],
			proxy: {
				type: 'ajax',
				url: 'get-fma-list.cgi',
				timeout: timeout,
				pageParam: Ag.Def.CONCEPT_TERM_SEARCH_GRID_PAGE_SIZE ? 'page' : undefined,
				startParam: Ag.Def.CONCEPT_TERM_SEARCH_GRID_PAGE_SIZE ? 'start' : undefined,
				limitParam: Ag.Def.CONCEPT_TERM_SEARCH_GRID_PAGE_SIZE ? 'limit' : undefined,
				sortParam: undefined,
				actionMethods: {
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
							if(response.statusText == 'OK' && response.status == 200) return;
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
						if(response.status == '-1') return;
						if(response.statusText == 'OK' && response.status == 200) return;
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
					if(self.beforeloadStore && !self.beforeloadStore(store)) return false;
					var p = store.getProxy();
					p.extraParams = p.extraParams || {};
					delete p.extraParams.current_datas;
					delete p.extraParams._ExtVerMajor;
					delete p.extraParams._ExtVerMinor;
					delete p.extraParams._ExtVerPatch;
					delete p.extraParams._ExtVerBuild;
					delete p.extraParams._ExtVerRelease;

					p.extraParams['anyMatch'] = 1;
					if(Ext.isEmpty(p.extraParams['searchTarget'])) p.extraParams['searchTarget'] = 1;

					delete p.extraParams['system_ids'];
					var use_system_ids;
					var system_list_store = Ext.data.StoreManager.lookup('system-list-store');
					system_list_store.filter([{
						property: Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID,
						value: true
					}]);
					if(system_list_store.getCount()>0){
						use_system_ids = {};
						system_list_store.each(function(record){
							use_system_ids[record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID)] = record.getData();
						});
					}
					system_list_store.clearFilter();
					if(Ext.isObject(use_system_ids)){
						p.extraParams['system_ids'] = Ext.JSON.encode(Ext.Object.getKeys(use_system_ids));
					}
				},
				datachanged : function(store,options){
				},
				load: function(store,records,successful,eOpts){
					if(successful){
						update_search_records(store,records);
					}
				},
				add: function( store, records, index, eOpts ){
					if(Ext.isEmpty(renderer_dataIndex_suffix)) return;
//					console.log('add()');
					update_search_records(store,records);
					update_system_element_count.delay(0,null,null,[store]);
				},
				update: {
					fn: function(store,record,operation){
						if(Ext.isEmpty(renderer_dataIndex_suffix)) return;
//						console.log('update()');
						update_system_element_count.delay(0,null,null,[store]);
					},
					buffer: 100
				},
				bulkremove: {
					fn: function( store, records, indexes, isMove, eOpts ){
						if(Ext.isEmpty(renderer_dataIndex_suffix)) return;
//						console.log('bulkremove()');
//						update_system_element_count.delay(250,null,null,[store]);
						update_system_element_count.delay(0,null,null,[store]);
					},
					buffer: 100
				},
				filterchange: function( store, filters, eOpts ){
//					console.log('filterchange', store, filters, eOpts);
				}
			}
		});

		var update_system_element_count = new Ext.util.DelayedTask(function(store){
//			console.log('START update_system_element_count()',store.storeId);
			if(Ext.isEmpty(store)) store = Ext.data.StoreManager.lookup(Ag.Def.CONCEPT_MATCH_LIST_STORE_ID);
			var stores = [Ext.data.StoreManager.lookup(Ag.Def.CONCEPT_MATCH_LIST_STORE_ID),Ext.data.StoreManager.lookup(Ag.Def.CONCEPT_TERM_STORE_ID)];
			var system_store = Ext.data.StoreManager.lookup('system-list-store');
			var element_count = {};
			var element = {};
			Ext.Array.each(stores,function(store){
				store.each(function(record,id){
	//				console.log(record.getData());
					var system_id = record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID);
					if(system_id.match(/^([0-9]+)(.+)$/)) system_id = parseInt(RegExp.$1);
					if(Ext.isEmpty(element_count[system_id])) element_count[system_id] = 0;
					if(Ext.isEmpty(element[system_id])) element[system_id] = [];
					element_count[system_id]++;
					element[system_id].push(record.getData());
				})
			});
//			console.log(element_count);
			system_store.suspendEvents(true);
			try{
				system_store.each(function(record){
					var system_id = record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID);
					if(system_id.match(/^([0-9]+)(.+)$/)) system_id = parseInt(RegExp.$1);

					record.beginEdit();
					if(Ext.isDefined(element_count[system_id])){
						record.set('element_count',element_count[system_id]);
					}
					else{
						record.set('element_count',0);
					}
					if(Ext.isDefined(element[system_id])){
						record.set('element',element[system_id]);
					}
					else{
						record.set('element',null);
					}
					record.commit(false,['element_count','element']);
				});
			}catch(e){}
			system_store.resumeEvents();
//			console.log('END update_system_element_count()');


			element_count = {};
			element = {};
			Ext.Array.each(stores,function(store){
				store.each(function(record,id){
//					var segment_id = record.get(Ag.Def.SEGMENT_DATA_FIELD_ID);

//					Ext.Array.each(Ext.Array.filter((record.get(Ag.Def.SEGMENT_DATA_FIELD_ID) || []), function(segment_id){ return Ext.isNumeric(segment_id); }), function(segment_id){
					Ext.Array.each(record.get(Ag.Def.SEGMENT_DATA_FIELD_ID) || [], function(segment_id){
						if(Ext.isEmpty(element_count[segment_id])) element_count[segment_id] = 0;
						if(Ext.isEmpty(element[segment_id])) element[segment_id] = [];
						element_count[segment_id]++;
						element[segment_id].push(record.getData());
					});
				})
			});
	//			console.log(element_count);
	//			console.log(element);

			var segment_store = Ext.data.StoreManager.lookup('segment-list-store');
			segment_store.suspendEvents(true);
			try{
				segment_store.getRootNode().cascadeBy(function(node){
					if(!node.isLeaf()) return true;
//					Ext.Array.each(Ext.Array.filter((node.get('cities_ids') || "").split(','), function(cities_id){ return Ext.isNumeric(cities_id); }), function(cities_id){
						node.beginEdit();
						node.set('element_count',0);
						node.set('element',null);
						node.commit(true,['element_count','element']);
//					});
				});
				segment_store.getRootNode().cascadeBy(function(node){
					if(!node.isLeaf()) return true;
//					Ext.Array.each(Ext.Array.filter((node.get('cities_ids') || "").split(','), function(cities_id){ return Ext.isNumeric(cities_id); }), function(cities_id){
						var cities_id = node.get(Ag.Def.SEGMENT_DATA_FIELD_ID);

						var cur_element_count = node.get('element_count');
						var cur_element = node.get('element');
						if(Ext.isEmpty(cur_element_count)) cur_element_count = 0;
						if(Ext.isNumber(element_count[cities_id])){
							cur_element_count += element_count[cities_id];
						}
						if(Ext.isArray(element[cities_id]) && element[cities_id].length){
							if(Ext.isEmpty(cur_element)) cur_element = [];
							cur_element = cur_element.concat(element[cities_id]);
						}
						if(Ext.isEmpty(cur_element)) cur_element = null;
						node.beginEdit();
						node.set('element_count',cur_element_count);
						node.set('element',cur_element);
						node.commit(false,['element_count','element']);

//					});
//					console.log(node.get('cities_ids'),node.get('element_count'));
				});
			}catch(e){}
			segment_store.resumeEvents();

		});

		Ext.create('Ext.data.Store', {
			storeId: Ag.Def.CONCEPT_MATCH_LIST_STORE_ID,
			model: 'Ag.data.Model.CONCEPT_TERM_PALLET',
			remoteSort: false,
			sorters: [{
				property: Ag.Def.NAME_DATA_FIELD_ID,
				direction: 'ASC'
			}],
			listeners: {
				add: function( store, records, index, eOpts ){
					if(records.length){
						update_system_element_count.cancel();
						update_system_element_count.delay(250,null,null,[store]);
					}
				},
				bulkremove: function( store, records, indexes, isMove, eOpts ){
					if(records.length){
						update_system_element_count.cancel();
						update_system_element_count.delay(250,null,null,[store]);
					}
				}
			}
		});
		if(window.agstorelocalforage){
			self.on('loadrenderer',function(){
				try{
					let match_list_store = Ext.data.StoreManager.lookup(Ag.Def.CONCEPT_MATCH_LIST_STORE_ID);
					if(match_list_store){

						agstorelocalforage.getItem(Ag.Def.CONCEPT_MATCH_LIST_STORE_ID).then(function(value) {

							let fmaids = [];
							let ids;
							let art_ids;
							let exists_fmaids = false;
							if(self.DEF_MODEL_VERSION_RECORD && self.DEF_MODEL_VERSION_RECORD instanceof Ext.data.Model){
								let version = self.DEF_MODEL_VERSION_RECORD.get('display');
								if(
									Ext.isString(version) &&
									version.length>0 &&
									Ext.isObject(Ag.data.renderer) &&
									Ext.isObject(Ag.data.renderer[version]) &&
									Ext.isObject(Ag.data.renderer[version]['ids']) &&
									Ext.isObject(Ag.data.renderer[version]['art_ids'])
								){
									ids = Ag.data.renderer[version]['ids'];
									art_ids = Ag.data.renderer[version]['art_ids'];
									let fmaid_arr = [];
									let fmaid_options = {};
									let fmaid_test = new RegExp(/^(FMA).*?([0-9]+.*)$/,'i');
									let urlparams_hash = {};
									let url = new URL(window.location.href);
									let searchParams = url.searchParams;
									if(searchParams.size>0){
										for(const [name, value] of searchParams.entries()){
											let lname = name.toLowerCase();
											if(Ext.isEmpty(urlparams_hash[lname])) urlparams_hash[lname] = [];
											urlparams_hash[lname].push(value);
//											console.log(lname,value);
										}
									}
									if(Ext.isArray(urlparams_hash['id']) && urlparams_hash['id'].length>0){
										urlparams_hash['id'].forEach(function(id){
//											console.log(id);
											if(Ext.isString(id) && id.length>0 && fmaid_test.test(id)){
												let fmaid = (RegExp.$1 + RegExp.$2).toUpperCase();
												fmaid.split(',').forEach(function(id){
													if(Ext.isString(id) && id.length>0 && fmaid_test.test(id)){
														fmaid_arr.push((RegExp.$1 + RegExp.$2).toUpperCase());
													}
												});
											}
										});
									}
									if(Ext.isArray(urlparams_hash['fmaid']) && urlparams_hash['fmaid'].length>0){
										urlparams_hash['fmaid'].forEach(function(id){
											if(Ext.isString(id) && id.length>0 && fmaid_test.test(id)){
												let fmaid = (RegExp.$1 + RegExp.$2).toUpperCase();
												fmaid.split(',').forEach(function(id){
													if(Ext.isString(id) && id.length>0 && fmaid_test.test(id)){
														fmaid_arr.push((RegExp.$1 + RegExp.$2).toUpperCase());
													}
												});
											}
										});
									}
									if(Ext.isArray(fmaid_arr) && fmaid_arr.length>0){
										const fmaid_len = fmaid_arr.length;
										let fmaid_cnt = 0;
										let hash_key = 'rgb';
										if(Ext.isArray(urlparams_hash[hash_key]) && urlparams_hash[hash_key].length>0){
											urlparams_hash[hash_key].forEach(function(color){
												if(fmaid_cnt>=fmaid_len) return;
												color.split(',').forEach(function(color){
													if(fmaid_cnt>=fmaid_len) return;
													if(Ext.isString(color) && (color.length==3 || color.length==6)){
														let ext_color = Ext.draw.Color.fromString('#'+color);
														if(Ext.isDefined(ext_color)){
															if(Ext.isEmpty(fmaid_options[fmaid_arr[fmaid_cnt]])) fmaid_options[fmaid_arr[fmaid_cnt]] = {};
															fmaid_options[fmaid_arr[fmaid_cnt]]['color'] = ext_color.toString().toUpperCase();
														}
													}
													fmaid_cnt++;
												});
											});
										}
										fmaid_cnt = 0;
										hash_key = 'opacity';
										if(Ext.isArray(urlparams_hash[hash_key]) && urlparams_hash[hash_key].length>0){
											urlparams_hash[hash_key].forEach(function(opacity){
												if(fmaid_cnt>=fmaid_len) return;
												opacity.split(',').forEach(function(opacity){
													if(fmaid_cnt>=fmaid_len) return;
													if(Ext.isNumeric(opacity)){
														if(Ext.isEmpty(fmaid_options[fmaid_arr[fmaid_cnt]])) fmaid_options[fmaid_arr[fmaid_cnt]] = {};
//														fmaid_options[fmaid_arr[fmaid_cnt]]['opacity'] = 1 - parseFloat(opacity);
														fmaid_options[fmaid_arr[fmaid_cnt]]['opacity'] = parseFloat(opacity)>1 ? 1 : parseFloat(opacity);
													}
													fmaid_cnt++;
												});
											});
										}
									}
//									console.log(fmaid_arr);
									if(Ext.isArray(fmaid_arr) && fmaid_arr.length>0){
										exists_fmaids = true;
										let key_art_ids = 'art_ids';
										if(Ext.isArray(urlparams_hash['expansion']) && urlparams_hash['expansion'].length>0 && Ext.isString(urlparams_hash['expansion'][0])){
											let params_expansion = urlparams_hash['expansion'][0].toLowerCase();
											if(params_expansion == 'is_a' || params_expansion == 'isa'){
												key_art_ids = 'art_ids_isa';
											}
											else if(params_expansion == 'part_of' || params_expansion == 'partof'){
												key_art_ids = 'art_ids_partof';
											}
											else if(params_expansion == 'none'){
												key_art_ids = 'art_ids_none';
											}
										}
//										console.log(key_art_ids);

										fmaid_arr.forEach(function(fmaid){
//											console.log(ids[fmaid]);
											if(Ext.isString(fmaid) && fmaid.length>0 && Ext.isObject(ids[fmaid])){
												if(ids[fmaid]['is_element']){
													let hash = {};
													hash[Ag.Def.ID_DATA_FIELD_ID] = ids[fmaid][Ag.Def.ID_DATA_FIELD_ID];
													hash[Ag.Def.NAME_DATA_FIELD_ID] = ids[fmaid][Ag.Def.NAME_DATA_FIELD_ID];
													if(Ext.isObject(fmaid_options[fmaid])){
														if(Ext.isString(fmaid_options[fmaid]['color']) && fmaid_options[fmaid]['color'].length>0){
															hash[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = fmaid_options[fmaid]['color'];
														}
														else{
															hash[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = null;
														}
														if(Ext.isNumber(fmaid_options[fmaid]['opacity'])){
															hash[Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID] = fmaid_options[fmaid]['opacity'];
														}
														else{
															hash[Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID] = 1;
														}
													}
													else{
														hash[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = null;
														hash[Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID] = 1;
													}
													fmaids.push(hash);
												}
												else if(Ext.isArray(ids[fmaid][key_art_ids])){
													ids[fmaid][key_art_ids].forEach(function(art_id, index, array){
														if(
															Ext.isObject(art_ids[art_id]) &&
															Ext.isString(art_ids[art_id][Ag.Def.ID_DATA_FIELD_ID]) &&
															art_ids[art_id][Ag.Def.ID_DATA_FIELD_ID].length>0 &&
															Ext.isObject(ids[art_ids[art_id][Ag.Def.ID_DATA_FIELD_ID]]) &&
															ids[art_ids[art_id][Ag.Def.ID_DATA_FIELD_ID]]['is_element']
														){
															let hash = {};
															hash[Ag.Def.ID_DATA_FIELD_ID] = ids[art_ids[art_id][Ag.Def.ID_DATA_FIELD_ID]][Ag.Def.ID_DATA_FIELD_ID];
															hash[Ag.Def.NAME_DATA_FIELD_ID] = ids[art_ids[art_id][Ag.Def.ID_DATA_FIELD_ID]][Ag.Def.NAME_DATA_FIELD_ID];
															if(Ext.isObject(fmaid_options[fmaid])){
																if(Ext.isString(fmaid_options[fmaid]['color']) && fmaid_options[fmaid]['color'].length>0){
																	hash[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = fmaid_options[fmaid]['color'];
																}
																else{
																	hash[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = null;
																}
																if(Ext.isNumber(fmaid_options[fmaid]['opacity'])){
																	hash[Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID] = fmaid_options[fmaid]['opacity'];
																}
																else{
																	hash[Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID] = 1;
																}
															}
															else{
																hash[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = null;
																hash[Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID] = 1;
															}
															fmaids.push(hash);
														}
													});
												}
											}
										});
									}
								}
							}
							if(exists_fmaids){
								if(Ext.isArray(fmaids) && fmaids.length>0){
									match_list_store.suspendEvents(true);
									let datas = [];
									fmaids.forEach(function(hash){
										datas.push(hash);
									});
									let records = match_list_store.add(datas);
									_update_search_records(match_list_store,records,null,Ag.data.SEG2ART);
									match_list_store.resumeEvents();
	//								Ext.defer(_update_search_records,100,this,[match_list_store,records,null,Ag.data.SEG2ART]);

									records = match_list_store.getRange();
									match_list_store.removeAll(true);
									match_list_store.add(records);

									let tabpanel = Ext.getCmp('main-viewport').down('tabpanel#east-tabpanel');
									let gridpanel = tabpanel.down('gridpanel#match-list-gridpanel');
									if(tabpanel && gridpanel){
										let setAct = function(){
											tabpanel.setActiveTab(gridpanel);
										};
										if(tabpanel && tabpanel.rendered && gridpanel && gridpanel.rendered){
											setAct();
										}
									}

									let renderpanel = Ext.getCmp('main-viewport').down('panel#main-render-panel');
									console.log(renderpanel);
									if(renderpanel && renderpanel.__webglMainRenderer && renderpanel.__webglMainRenderer instanceof Ag.MainRenderer){

										let url = new URL(window.location.href);
										let searchParams = url.searchParams;

										if(
												(
													searchParams.has('cx') && Ext.isNumeric(searchParams.get('cx')) &&
													searchParams.has('cy') && Ext.isNumeric(searchParams.get('cy')) &&
													searchParams.has('cz') && Ext.isNumeric(searchParams.get('cz'))
												) ||

												(searchParams.has('focusid') && Ext.isString(searchParams.get('focusid'))) ||
												(searchParams.has('ha')      && Ext.isNumeric(searchParams.get('ha')))     ||
												(searchParams.has('va')      && Ext.isNumeric(searchParams.get('va')))     ||
												(searchParams.has('zoom')    && Ext.isNumeric(searchParams.get('zoom')))
										){

											renderpanel.__webglMainRenderer.on('load',function(renderer,successful){
//												console.log('load',renderer,successful);
												if(successful){
//													console.log(renderer);
//													console.log(renderer.getTarget());
//													console.log(renderer.getCameraPosition());
//													console.log(renderer.getCameraUp());
//													console.log(renderer.getHorizontal());
//													console.log(renderer.getVertical());
//													console.log(renderer.getDispZoom());

													if(searchParams.has('focusid') && Ext.isString(searchParams.get('focusid'))){
//														console.log('focusid',searchParams.get('focusid'));
														try{

															let fmaid_test = new RegExp(/^(FMA).*?([0-9]+.*)$/,'i');
															let fmaid_arr = [];
															let focusid = searchParams.get('focusid');
															let params_expansion = searchParams.has('focusid') ? searchParams.get('expansion') : null;
															if(Ext.isEmpty(params_expansion)) params_expansion = 'art_ids';
															params_expansion = params_expansion.toLowerCase();
															if(focusid.length>0 && fmaid_test.test(focusid)){
																let fmaid = (RegExp.$1 + RegExp.$2).toUpperCase();
																fmaid.split(',').forEach(function(id){
																	if(Ext.isString(id) && id.length>0 && fmaid_test.test(id)){
																		fmaid_arr.push((RegExp.$1 + RegExp.$2).toUpperCase());
																	}
																});
															}
															if(Ext.isArray(fmaid_arr) && fmaid_arr.length>0){
																let art_file_info = Ag.data.art_file_info;
																let key_art_ids = 'art_ids';
																if(params_expansion == 'is_a' || params_expansion == 'isa'){
																	key_art_ids = 'art_ids_isa';
																}
																else if(params_expansion == 'part_of' || params_expansion == 'partof'){
																	key_art_ids = 'art_ids_partof';
																}
																else if(params_expansion == 'none'){
																	key_art_ids = 'art_ids_none';
																}

																let art_xmin = [];
																let art_xmax = [];
																let art_ymin = [];
																let art_ymax = [];
																let art_zmin = [];
																let art_zmax = [];
																fmaid_arr.forEach(function(fmaid){
																	if(ids[fmaid]['is_element']){
																		ids[fmaid]['art_ids'].forEach(function(art_id, index, array){
																			if(
																				Ext.isObject(art_file_info) &&
																				Ext.isObject(art_file_info[art_id]) &&
																				Ext.isNumber(art_file_info[art_id]['art_xmin']) &&
																				Ext.isNumber(art_file_info[art_id]['art_xmax']) &&
																				Ext.isNumber(art_file_info[art_id]['art_ymin']) &&
																				Ext.isNumber(art_file_info[art_id]['art_ymax']) &&
																				Ext.isNumber(art_file_info[art_id]['art_zmin']) &&
																				Ext.isNumber(art_file_info[art_id]['art_zmax'])
																			){
//																				console.log(art_file_info[art_id]);
																				art_xmin.push(art_file_info[art_id]['art_xmin']);
																				art_xmax.push(art_file_info[art_id]['art_xmax']);
																				art_ymin.push(art_file_info[art_id]['art_ymin']);
																				art_ymax.push(art_file_info[art_id]['art_ymax']);
																				art_zmin.push(art_file_info[art_id]['art_zmin']);
																				art_zmax.push(art_file_info[art_id]['art_zmax']);
																			}
																		});
																	}
																	else if(Ext.isArray(ids[fmaid][key_art_ids])){
																		ids[fmaid][key_art_ids].forEach(function(art_id, index, array){
																			if(
																				Ext.isObject(art_file_info) &&
																				Ext.isObject(art_file_info[art_id]) &&
																				Ext.isNumber(art_file_info[art_id]['art_xmin']) &&
																				Ext.isNumber(art_file_info[art_id]['art_xmax']) &&
																				Ext.isNumber(art_file_info[art_id]['art_ymin']) &&
																				Ext.isNumber(art_file_info[art_id]['art_ymax']) &&
																				Ext.isNumber(art_file_info[art_id]['art_zmin']) &&
																				Ext.isNumber(art_file_info[art_id]['art_zmax'])
																			){
//																				console.log(art_file_info[art_id]);
																				art_xmin.push(art_file_info[art_id]['art_xmin']);
																				art_xmax.push(art_file_info[art_id]['art_xmax']);
																				art_ymin.push(art_file_info[art_id]['art_ymin']);
																				art_ymax.push(art_file_info[art_id]['art_ymax']);
																				art_zmin.push(art_file_info[art_id]['art_zmin']);
																				art_zmax.push(art_file_info[art_id]['art_zmax']);
																			}
																		});
																	}
																});
																if(art_xmin.length){
																	let xmin = Math.min(...art_xmin);
																	let xmax = Math.max(...art_xmax);
																	let ymin = Math.min(...art_ymin);
																	let ymax = Math.max(...art_ymax);
																	let zmin = Math.min(...art_zmin);
																	let zmax = Math.max(...art_zmax);
//																	console.log(xmin,xmax,ymin,ymax,zmin,zmax);

																	let max = new THREE.Vector3(xmax,ymax,zmax);
																	let min = new THREE.Vector3(xmin,ymin,zmin);
																	let offset = new THREE.Vector3();
																	offset.addVectors( max, min );
																	offset.multiplyScalar( 0.5 );

																	let pos = renderer.getCameraPosition();
																	pos.x = offset.x;
																	pos.z = offset.z;
																	renderer.setCameraPosition(pos);
																	renderer.setTarget(offset);


			var width = renderer.__SCREEN_WIDTH;
			var height = renderer.__SCREEN_HEIGHT;
			renderer.__zoom.translate([width/2, height/2]);

//最長を計算する
			var valArr = [max.x-min.x,max.y-min.y,max.z-min.z];
/**/
			valArr.push(Math.pow(valArr[0]*valArr[0] + valArr[1]*valArr[1], 0.5));
			valArr.push(Math.pow(valArr[1]*valArr[1] + valArr[2]*valArr[2], 0.5));
			valArr.push(Math.pow(valArr[0]*valArr[0] + valArr[2]*valArr[2], 0.5));
/**/
			var maxVal = Ext.Array.max(valArr);
			renderer.setYRange(maxVal);

																}
															}
														}catch(e){
															console.error(e);
														}
													}
													if(searchParams.has('ha') && Ext.isNumeric(searchParams.get('ha'))){
//														console.log('ha',searchParams.get('ha'));
														renderer.setHorizontal(parseInt(searchParams.get('ha')));
													}
													if(searchParams.has('va') && Ext.isNumeric(searchParams.get('va'))){
//														console.log('va',searchParams.get('va'));
														renderer.setVertical(parseInt(searchParams.get('va')));
													}
													if(searchParams.has('zoom') && Ext.isNumeric(searchParams.get('zoom'))){
//														console.log('zoom',searchParams.get('zoom'));
														renderer.setDispZoom(parseInt(searchParams.get('zoom')));
													}

													if(
														searchParams.has('cx') && Ext.isNumeric(searchParams.get('cx')) &&
														searchParams.has('cy') && Ext.isNumeric(searchParams.get('cy')) &&
														searchParams.has('cz') && Ext.isNumeric(searchParams.get('cz'))
													){
														let pos = new THREE.Vector3();
														pos.set(
															parseFloat(searchParams.get('cx')),
															parseFloat(searchParams.get('cy')),
															parseFloat(searchParams.get('cz'))
														);
														renderer.setCameraPos(pos);
													}
													else{

														if(searchParams.has('ha') && Ext.isNumeric(searchParams.get('ha'))){
															renderer.setHorizontal(parseInt(searchParams.get('ha')));
														}
														if(searchParams.has('va') && Ext.isNumeric(searchParams.get('va'))){
															renderer.setVertical(parseInt(searchParams.get('va')));
														}
														if(searchParams.has('zoom') && Ext.isNumeric(searchParams.get('zoom'))){
															renderer.setDispZoom(parseInt(searchParams.get('zoom')));
														}

													}

												}
											},self,{single:true});
										}
										renderpanel.__webglMainRenderer.on('zoom',function(renderer,value){
											console.log('zoom');
//												console.log(renderer.getCameraPos());
//												console.log(renderer.getHorizontal());
//												console.log(renderer.getVertical());
//												console.log(renderer.getDispZoom());

											let pos  = renderer.getCameraPos();
											let ha   = renderer.getHorizontal();
											let va   = renderer.getVertical();
											let zoom = renderer.getDispZoom();

											let url = new URL(window.location.href);
											let searchParams = url.searchParams;

											searchParams.set('cx', Math.ceil(pos.x * 100000) / 100000 );
											searchParams.set('cy', Math.ceil(pos.y * 100000) / 100000 );
											searchParams.set('cz', Math.ceil(pos.z * 100000) / 100000 );
											searchParams.set('ha', ha );
											searchParams.set('va', va );
											searchParams.set('zoom', zoom );

											console.log(url.toString());

										});
										renderpanel.__webglMainRenderer.on('rotate',function(renderer,value){
											console.log('rotate',value);
//												console.log(renderer.getCameraPos());
//												console.log(renderer.getHorizontal());
//												console.log(renderer.getVertical());
//												console.log(renderer.getDispZoom());

											let pos  = renderer.getCameraPos();
											let ha   = renderer.getHorizontal();
											let va   = renderer.getVertical();
											let zoom = renderer.getDispZoom();

											let url = new URL(window.location.href);
											let searchParams = url.searchParams;

											searchParams.set('cx', Math.ceil(pos.x * 100000) / 100000 );
											searchParams.set('cy', Math.ceil(pos.y * 100000) / 100000 );
											searchParams.set('cz', Math.ceil(pos.z * 100000) / 100000 );
											searchParams.set('ha', ha );
											searchParams.set('va', va );
											searchParams.set('zoom', zoom );

											console.log(url.toString());
										});

									}

								}
								else{
									match_list_store.removeAll();
								}
							}
							else if(Ext.isArray(value) && value.length){
								match_list_store.suspendEvents(true);
								match_list_store.add(value);
								match_list_store.resumeEvents();
							}

							match_list_store.on({
								add: function( store, records, index, eOpts ){
									agstorelocalforage.setItem(Ag.Def.CONCEPT_MATCH_LIST_STORE_ID, Ext.Array.map(store.getRange(), function(record){ return record.getData(); }) ).then(function (value) {
									}).catch(function(err) {
										console.error(err);
									});
								},
								bulkremove: function( store, records, indexes, isMove, eOpts ){
									agstorelocalforage.setItem(Ag.Def.CONCEPT_MATCH_LIST_STORE_ID, Ext.Array.map(store.getRange(), function(record){ return record.getData(); }) ).then(function (value) {
									}).catch(function(err) {
										console.error(err);
									});
								},
								update: function( store, record, operation, modifiedFieldNames, eOpts ){
									if(operation == Ext.data.Model.COMMIT){
										agstorelocalforage.setItem(Ag.Def.CONCEPT_MATCH_LIST_STORE_ID, Ext.Array.map(store.getRange(), function(record){ return record.getData(); }) ).then(function (value) {
										}).catch(function(err) {
											console.error(err);
										});
									}
								}
							});

						}).catch(function(err) {
							console.error(err);
						});
					}
				}catch(e){
					console.error(e);
				}
			},self,{single:true});
		}

		Ext.create('Ext.data.Store', {
			storeId: Ag.Def.CONCEPT_TERM_STORE_ID,
			model: 'Ag.data.Model.CONCEPT_TERM_PALLET',
			remoteSort: false,
			sorters: [{
				property: Ag.Def.NAME_DATA_FIELD_ID,
				direction: 'ASC'
			}],
			listeners: {
				bulkremove: function( store, records, indexes, isMove, eOpts ){
					if(records.length){
						update_system_element_count.cancel();
						update_system_element_count.delay(250,null,null,[store]);
					}
				}
			}
		});

		Ext.create('Ext.data.Store', {
			storeId: Ag.Def.CONCEPT_SELECTED_ITEMS_STORE_ID,
			model: 'Ag.data.Model.CONCEPT_TERM_PALLET',
			remoteSort: false,
			sorters: [{
				property: Ag.Def.NAME_DATA_FIELD_ID,
				direction: 'ASC'
			}]
		});

		Ext.create('Ext.data.Store', {
			storeId: Ag.Def.CONCEPT_SELECTED_TAGS_STORE_ID,
			model: 'Ag.data.Model.CONCEPT_TERM_PALLET',
			remoteSort: false,
			sorters: [{
				property: Ag.Def.NAME_DATA_FIELD_ID,
				direction: 'ASC'
			}]
		});

/*
		Ext.create('Ext.data.Store', {
			storeId: Ag.Def.CONCEPT_PARENT_TERM_STORE_ID,
			model: 'Ag.data.Model.CONCEPT_TERM_PALLET',
			pageSize: Ag.Def.CONCEPT_TERM_SEARCH_GRID_PAGE_SIZE,
	//		remoteSort: true,
			remoteSort: false,
			sorters: [{
				property: Ag.Def.NAME_DATA_FIELD_ID,
				direction: 'ASC'
			}],
			proxy: {
				type: 'ajax',
				url: 'get-fma-list.cgi',
				timeout: timeout,
				pageParam: Ag.Def.CONCEPT_TERM_SEARCH_GRID_PAGE_SIZE ? 'page' : undefined,
				startParam: Ag.Def.CONCEPT_TERM_SEARCH_GRID_PAGE_SIZE ? 'start' : undefined,
				limitParam: Ag.Def.CONCEPT_TERM_SEARCH_GRID_PAGE_SIZE ? 'limit' : undefined,
				actionMethods: {
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
							if(response.statusText == 'OK' && response.status == 200) return;
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
						if(response.statusText == 'OK' && response.status == 200) return;
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
*/

		Ext.create('Ag.data.Store', {
			autoLoad: Ext.isArray(Ag.data.concept_info) && Ag.data.concept_info.length ? false : true,
			storeId: 'conceptInfoStore',
			model: 'Ag.data.Model.CONCEPT_INFO',
			remoteSort: false,
			sorters: [{
				property: 'cb_order',
				direction: 'ASC'
			}],
			data: Ext.isArray(Ag.data.concept_info) && Ag.data.concept_info.length ? Ag.data.concept_info : null
		});

		Ext.create('Ag.data.Store', {
			autoLoad: Ext.isArray(Ag.data.concept_build) && Ag.data.concept_build.length ? false : true,
			storeId: 'conceptBuildStore',
			model: 'Ag.data.Model.CONCEPT_BUILD',
			remoteSort: false,
			sorters: [{
				property: 'cb_order',
				direction: 'ASC'
			}],
			data: Ext.isArray(Ag.data.concept_build) && Ag.data.concept_build.length ? Ag.data.concept_build : null
		});

		Ext.create('Ag.data.Store', {
			autoLoad: Ext.isArray(Ag.data.model_version) && Ag.data.model_version.length ? false : true,
			storeId: 'version-store',
			model: 'Ag.data.Model.MODEL_VERSION',
			remoteSort: false,
			sorters: [{
				property: 'mv_order',
				direction: 'ASC'
			}],
			data: Ext.isArray(Ag.data.model_version) && Ag.data.model_version.length ? Ag.data.model_version : null
		});
/**/
		Ext.create('Ext.data.TreeStore', {
			autoLoad: true,
			autoSync: false,
			storeId: 'segment-list-store',
			model: 'Ag.data.Model.SEGMENT_LIST',
			remoteSort: false,
			proxy: Ext.create('Ext.data.proxy.Ajax',{
				type: 'ajax',
				noCache: Ext.isNumber(Ag.Def.DEF_FILE_MTIME['PREFECTURES2CITIES.jgz']) ? false : true,
				timeout: timeout,
				url: 'MENU_SEGMENTS/PREFECTURES2CITIES.jgz' + (Ext.isNumber(Ag.Def.DEF_FILE_MTIME['PREFECTURES2CITIES.jgz']) ? '?'+Ag.Def.DEF_FILE_MTIME['PREFECTURES2CITIES.jgz'] : ''),
				reader: {
					type: 'json',
//					root: 'children',
					listeners: {
						exception : function(){
						}
					}
				},
			}),
			root: {
				allowDrag: false,
				allowDrop: false,
				depth: 0,
	//				expandable: true,
				expanded: true,
	//			iconCls: 'tfolder',
				root: true,
				text: 'whole',
				name: 'root',
				segment: 'whole'
			},
			listeners: {
				beforeload: function( store, operation, eOpts ){
				},
				load: function( store, node, records, successful, eOpts ){
//					console.log('load',  store, node, records, successful, eOpts );

					Ag.data.citiesids2segment = {};
					store.getRootNode().cascadeBy(function(node){
						if(!node.isLeaf()) return true;
						Ext.Array.each(Ext.Array.filter((node.get('cities_ids') || "").split(','), function(cities_id){ return Ext.isNumeric(cities_id); }), function(cities_id){
							Ag.data.citiesids2segment[cities_id] = node.get('segment');
						});
//						console.log(node.getData());
					});
//					console.log(Ag.data.citiesids2segment);

					return;
					if(!successful) return;
					var ids = [];
					store.getRootNode().cascadeBy(function(node){
						var depth = node.getDepth();
						if(depth==0) return true;
						if(Ext.isEmpty(ids[depth])) ids[depth] = 0;
						node.beginEdit();
						if(false && depth==1){
							node.set(Ag.Def.SEGMENT_ID_DATA_FIELD_ID,Ext.String.leftPad( new String(++ids[depth]), 2, '0' ));
						}else{
							node.set(Ag.Def.SEGMENT_ID_DATA_FIELD_ID,new String(++ids[depth]));
						}
						node.set('text',Ext.String.format('{0}_{1}',node.get(Ag.Def.SEGMENT_ID_DATA_FIELD_ID),node.get('text')));
						node.commit(false,['text',Ag.Def.SEGMENT_ID_DATA_FIELD_ID]);
						node.endEdit(false,['text',Ag.Def.SEGMENT_ID_DATA_FIELD_ID]);
					});
				}
			}
		});
/**/
/*
		Ext.create('Ag.data.Store', {
			autoLoad: true,
			autoSync: false,
			storeId: 'segment-list-store',
			model: 'Ag.data.Model.SEGMENT_LIST',
			groupField: 'prefectures',
			remoteSort: false,
			proxy: Ext.create('Ext.data.proxy.Ajax',{
				type: 'ajax',
				timeout: timeout,
				url: 'MENU_SEGMENTS/PREFECTURES2CITIES.jgz',
				reader: {
					type: 'json',
					root: 'children',
					listeners: {
						exception : function(){
						}
					}
				},
			}),
			listeners: {
				load: function( store, records, successful, eOpts ){
					if(!successful) return;
					Ext.each(records, function(record, index){
						record.beginEdit();
						record.set(Ag.Def.SEGMENT_ID_DATA_FIELD_ID,new String(index+1));
						record.commit(false,[Ag.Def.SEGMENT_ID_DATA_FIELD_ID]);
						record.endEdit(false,[Ag.Def.SEGMENT_ID_DATA_FIELD_ID]);
					});
//					console.log(records);
				}
			}
		});
*/
		Ext.create('Ext.data.Store', {
			storeId: 'temporary-render-store',
			model: 'Ag.data.Model.CONCEPT_TERM_PALLET',
			remoteSort: false,
//			sorters: [{
//				property: Ag.Def.NAME_DATA_FIELD_ID,
//				direction: 'ASC'
//			}]
		});

		var createPalletStore = function(storeId,mirrorStoreId){
			return Ext.create('Ext.data.Store', {
				storeId: storeId,
				mirrorStoreId: mirrorStoreId,
				model: 'Ag.data.Model.CONCEPT_TERM_PALLET',
				remoteSort: false,
				sorters: [{
					property: Ag.Def.NAME_DATA_FIELD_ID,
					direction: 'ASC'
				}],
				listeners: {
					add: function(store, records, index, eOpts){
						var mirror_pallet_store = Ext.data.StoreManager.lookup(store.mirrorStoreId);
						var add_datas = [];
						records.forEach(function(record){
							var find_record = mirror_pallet_store.findRecord(Ag.Def.OBJ_ID_DATA_FIELD_ID, record.get(Ag.Def.OBJ_ID_DATA_FIELD_ID), 0, false, false, true);
							if(find_record) return true;
							add_datas.push(record.getData());
						});
//						if(add_datas.length) mirror_pallet_store.add(add_datas);
						if(add_datas.length){
							if(mirror_pallet_store.view){
								self.addRecords(mirror_pallet_store.view,add_datas);
							}else{
								mirror_pallet_store.add(add_datas);
							}
						}
					},
					clear: function(store, eOpts){
						var mirror_pallet_store = Ext.data.StoreManager.lookup(store.mirrorStoreId);
						if(mirror_pallet_store.getCount()) mirror_pallet_store.removeAll();
					},
					bulkremove: function(store, records, indexes, isMove, eOpts){
						var mirror_pallet_store = Ext.data.StoreManager.lookup(mirrorStoreId);
						var find_records = [];
						Ext.each(records,function(record){
							var find_record = mirror_pallet_store.findRecord(Ag.Def.OBJ_ID_DATA_FIELD_ID, record.get(Ag.Def.OBJ_ID_DATA_FIELD_ID), 0, false, false, true);
							if(find_record) find_records.push(find_record);
						});
//						if(find_records.length) mirror_pallet_store.remove(find_records);
						if(find_records.length){
							if(mirror_pallet_store.view){
								self.removeRecords(mirror_pallet_store.view,find_records);
							}else{
								mirror_pallet_store.remove(find_records);
							}
						}
					},
					update: function(store, record, operation, eOpts){
						var mirror_pallet_store = Ext.data.StoreManager.lookup(store.mirrorStoreId);
						if(operation == Ext.data.Model.COMMIT){
							var find_record = mirror_pallet_store.findRecord(Ag.Def.OBJ_ID_DATA_FIELD_ID, record.get(Ag.Def.OBJ_ID_DATA_FIELD_ID), 0, false, false, true);
							if(find_record){
								var modifiedFieldNames = [];
								find_record.beginEdit();
								Ext.Object.each(record.getData(),function(key,value){
									if(record.get(key)===find_record.get(key)) return true;
									find_record.set(key,record.get(key));
									modifiedFieldNames.push(key);
								});
								if(modifiedFieldNames.length){
									find_record.commit(false,modifiedFieldNames);
									find_record.endEdit(false,modifiedFieldNames);
								}else{
									find_record.cancelEdit();
								}
							}
						}
					}
				}
			});
		};
		createPalletStore('canvas-pallet-store','persistent-pallet-store');
		createPalletStore('persistent-pallet-store','canvas-pallet-store');

		Ext.create('Ext.data.Store', {
			storeId: 'canvas-pin-store',
			model: 'Ag.data.Model.PIN_PALLET'
		});

		Ext.create('Ext.data.Store', {
			storeId: 'canvas-neighbor-parts-store',
			model: 'Ag.data.Model.NEIGHBOR_PARTS',
			remoteSort: false,
			sorters: [{
				property: Ag.Def.DISTANCE_FIELD_ID,
				direction: 'ASC'
			}],
			proxy: {
				type: 'ajax',
				timeout: timeout,
				url: 'get-pick-search.cgi',
				sortParam: undefined,
				actionMethods: {
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
							if(response.statusText == 'OK' && response.status == 200) return;
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
						if(response.status == '-1') return;
						if(response.statusText == 'OK' && response.status == 200) return;
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
					console.time('canvas-neighbor-parts-store.load(1)');
				},
				datachanged : function(store,options){
				},
				load: function(store,records,successful,eOpts){
					if(successful && records.length){
//						var add_datas = _update_search_records(store,records,null,Ag.data.SEG2ART);
						Ext.defer(_update_search_records,100,this,[store,records,null,Ag.data.SEG2ART]);
//						var add_datas = _update_search_records(store,records,null,Ag.data.SEG2ART);
					}
					console.timeEnd('canvas-neighbor-parts-store.load(1)');
				},
				update: function(store,record,operation){
				}
			}
		});

		Ext.create('Ext.data.Store', {
			storeId: 'keyword-search-store',
			model: 'Ag.data.Model.KEYWORD_SEARCH',
			remoteSort: false,
			sorters: [{
				property: Ag.Def.NAME_DATA_FIELD_ID,
				direction: 'ASC'
			}],
			proxy: {
				type: 'ajax',
				timeout: timeout,
				url: 'get-fma-list.cgi',
				pageParam: Ag.Def.CONCEPT_TERM_SEARCH_GRID_PAGE_SIZE ? 'page' : undefined,
				startParam: Ag.Def.CONCEPT_TERM_SEARCH_GRID_PAGE_SIZE ? 'start' : undefined,
				limitParam: Ag.Def.CONCEPT_TERM_SEARCH_GRID_PAGE_SIZE ? 'limit' : undefined,
				sortParam: undefined,
				actionMethods: {
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
							if(response.statusText == 'OK' && response.status == 200) return;
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
						if(response.status == '-1') return;
						if(response.statusText == 'OK' && response.status == 200) return;
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

					p.extraParams['anyMatch'] = 1;
					if(Ext.isEmpty(p.extraParams['searchTarget'])) p.extraParams['searchTarget'] = 1;

					delete p.extraParams['system_ids'];
					var use_system_ids;
					var system_list_store = Ext.data.StoreManager.lookup('system-list-store');
					system_list_store.filter([{
						property: Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID,
						value: true
					}]);
					if(system_list_store.getCount()>0){
						use_system_ids = {};
						system_list_store.each(function(record){
							use_system_ids[record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID)] = record.getData();
						});
					}
					system_list_store.clearFilter();
					if(Ext.isObject(use_system_ids)){
						p.extraParams['system_ids'] = Ext.JSON.encode(Ext.Object.getKeys(use_system_ids));
					}

					console.time('keyword-search-store.load(1)');
				},
				load: function(store,records,successful,eOpts){
					if(successful && records.length){
//						var add_datas = _update_search_records(store,records,null,Ag.data.SEG2ART);
						Ext.defer(_update_search_records,100,this,[store,records,null,Ag.data.SEG2ART]);
//						var add_datas = _update_search_records(store,records,null,Ag.data.SEG2ART);
					}
					console.timeEnd('keyword-search-store.load(1)');
				}
			}
		});

		Ext.create('Ext.data.Store', {
			storeId: 'segment-grid-store',
			model: 'Ag.data.Model.SEGMENT_GRID',
			remoteSort: false,
			sorters: [{
				property: Ag.Def.NAME_DATA_FIELD_ID,
				direction: 'ASC'
			}],
		});

		if(1){
			let disableCaching = Ext.isNumber(Ag.Def.DEF_FILE_MTIME['SEG2ART.jgz']) ? false : true;
			let url = 'MENU_SEGMENTS/SEG2ART.jgz' + (Ext.isNumber(Ag.Def.DEF_FILE_MTIME['SEG2ART.jgz']) ? '?'+Ag.Def.DEF_FILE_MTIME['SEG2ART.jgz'] : '');
			if (disableCaching===false && window.aglocalforage) {
				aglocalforage.getItem(url).then(function(value) {
					if(value !== null){
						if(Ext.isObject(value)) Ag.data.SEG2ART = value;
					}
					else{

						Ext.Ajax.request({
							disableCaching: disableCaching,
							url: url,
							callback: function(options,success,response){
							},
							success: function(response){
								var hash = Ext.JSON.decode( response.responseText );
								if(Ext.isObject(hash)){
									aglocalforage.setItem(url, hash).then(function (value) {
										if(Ext.isObject(value)) Ag.data.SEG2ART = value;
									}).catch(function(err) {
										console.error(err);
									});
								}
							}
						});

					}
				}).catch(function(err) {
					console.error(err);
				});
			}
			else{
				Ext.Ajax.request({
					disableCaching: disableCaching,
					url: url,
					callback: function(options,success,response){
					},
					success: function(response){
						var hash = Ext.JSON.decode( response.responseText );
						if(Ext.isObject(hash)) Ag.data.SEG2ART = hash;
					}
				});
			}
		}

		if(1){
			let disableCaching = Ext.isNumber(Ag.Def.DEF_FILE_MTIME['SEG2ART_INSIDE.jgz']) ? false : true;
			let url = 'MENU_SEGMENTS/SEG2ART_INSIDE.jgz' + (Ext.isNumber(Ag.Def.DEF_FILE_MTIME['SEG2ART_INSIDE.jgz']) ? '?'+Ag.Def.DEF_FILE_MTIME['SEG2ART_INSIDE.jgz'] : '');
			if (disableCaching===false && window.aglocalforage) {
				aglocalforage.getItem(url).then(function(value) {
					if(value !== null){
						if(Ext.isObject(value)) Ag.data.SEG2ART_INSIDE = value;
					}
					else{

						Ext.Ajax.request({
							disableCaching: disableCaching,
							url: url,
							callback: function(options,success,response){
							},
							success: function(response){
								var hash = Ext.JSON.decode( response.responseText );
								if(Ext.isObject(hash)){
									aglocalforage.setItem(url, hash).then(function (value) {
										if(Ext.isObject(value)) Ag.data.SEG2ART_INSIDE = value;
									}).catch(function(err) {
										console.error(err);
									});
								}
							}
						});

					}
				}).catch(function(err) {
					console.error(err);
				});
			}
			else{
				Ext.Ajax.request({
					disableCaching: disableCaching,
					url: url,
					callback: function(options,success,response){
					},
					success: function(response){
						var hash = Ext.JSON.decode( response.responseText );
						if(Ext.isObject(hash)) Ag.data.SEG2ART_INSIDE = hash;
					}
				});
			}
		}

		if(1){
			let disableCaching = Ext.isNumber(Ag.Def.DEF_FILE_MTIME['MENU_SEGMENTS_in_art_file.jgz']) ? false : true;
			let url = 'MENU_SEGMENTS/MENU_SEGMENTS_in_art_file.jgz' + (Ext.isNumber(Ag.Def.DEF_FILE_MTIME['MENU_SEGMENTS_in_art_file.jgz']) ? '?'+Ag.Def.DEF_FILE_MTIME['MENU_SEGMENTS_in_art_file.jgz'] : '');

			if (disableCaching===false && window.aglocalforage) {
				aglocalforage.getItem(url).then(function(value) {
					if(value !== null){
						if(Ext.isObject(value)) Ag.data.MENU_SEGMENTS_in_art_file = value;
					}
					else{

						Ext.Ajax.request({
							disableCaching: disableCaching,
							url: url,
							callback: function(options,success,response){
							},
							success: function(response){
								var hash = Ext.JSON.decode( response.responseText );
								if(Ext.isObject(hash)){
									aglocalforage.setItem(url, hash).then(function (value) {
										if(Ext.isObject(value)) Ag.data.MENU_SEGMENTS_in_art_file = value;
									}).catch(function(err) {
										console.error(err);
									});
								}
							}
						});

					}
				}).catch(function(err) {
					console.error(err);
				});
			}
			else{
				Ext.Ajax.request({
					disableCaching: disableCaching,
					url: url,
					callback: function(options,success,response){
					},
					success: function(response){
						var hash = Ext.JSON.decode( response.responseText );
						if(hash) Ag.data.MENU_SEGMENTS_in_art_file = hash;
					}
				});
			}
		}
/*
		Ext.Ajax.request({
			url: 'MENU_SEGMENTS/CITIES.jgz',
			callback: function(options,success,response){
			},
			success: function(response){
				var hash = Ext.JSON.decode( response.responseText );
				if(hash) Ag.data.CITIES = hash;
			}
		});
*/
		Ext.create('Ag.data.Store', {
			autoLoad: true,
			autoSync: false,
			storeId: 'cities-list-store',
			model: 'Ag.data.Model.SEGMENT_LIST',
			groupField: 'prefectures',
			remoteSort: false,
			proxy: Ext.create('Ext.data.proxy.Ajax',{
				type: 'ajax',
				timeout: timeout,
				noCache: Ext.isNumber(Ag.Def.DEF_FILE_MTIME['CITIES.jgz']) ? false : true,
				url: 'MENU_SEGMENTS/CITIES.jgz' + (Ext.isNumber(Ag.Def.DEF_FILE_MTIME['CITIES.jgz']) ? '?'+Ag.Def.DEF_FILE_MTIME['CITIES.jgz'] : ''),
				pageParam: undefined,
				startParam: undefined,
				limitParam: undefined,
				groupParam: undefined,
				sortParam: undefined,
				reader: {
					type: 'json',
					root: 'children',
					listeners: {
						exception : function(){
						}
					}
				}
			}),
			listeners: {
				load: function( store, records, successful, eOpts ){
//					console.log(store.storeId,records,successful);
				}
			}
		});



		Ext.create('Ext.data.Store', {
			autoLoad: true,
			autoSync: false,
			storeId: 'system-list-store',
			model: 'Ag.data.Model.SYSTEM_LIST',
			remoteSort: false,
			proxy: Ext.create('Ext.data.proxy.Ajax',{
				type: 'ajax',
				timeout: timeout,
				noCache: Ext.isNumber(Ag.Def.DEF_FILE_MTIME['SYSTEM_COLOR.jgz']) ? false : true,
				url: 'MENU_SEGMENTS/SYSTEM_COLOR.jgz' + (Ext.isNumber(Ag.Def.DEF_FILE_MTIME['SYSTEM_COLOR.jgz']) ? '?'+Ag.Def.DEF_FILE_MTIME['SYSTEM_COLOR.jgz'] : ''),
				pageParam: undefined,
				startParam: undefined,
				limitParam: undefined,
				groupParam: undefined,
				sortParam: undefined,
				reader: {
					type: 'json',
					root: 'datas',
					listeners: {
						exception : function(){
						}
					}
				}
			}),
			listeners: {
				load: function( store, node, records, successful, eOpts ){
//					console.log(store.storeId,records,successful);
					if(!successful) return;
/*
					console.log(store.storeId,records);

					var fn = function(){
						var version;
						var ids;
						var art_ids;
						if(self.DEF_MODEL_VERSION_RECORD && self.DEF_MODEL_VERSION_RECORD instanceof Ext.data.Model){
							version = self.DEF_MODEL_VERSION_RECORD.get(Ag.Def.VERSION_STRING_FIELD_ID);
							Ag.data.isLoadingRenderer = Ag.data.isLoadingRenderer || {};
							if(Ag.data.isLoadingRenderer[version]) return;
						}
						else{
							Ext.defer(fn, 250);
							return;
						}
					};

					self.on('loadrenderer',fn,self);
*/
				}
			}
		});
/*
		Ext.Ajax.request({
			url: 'MENU_SEGMENTS/SYSTEM_ELEMENT_COLOR.jgz',
			callback: function(options,success,response){
			},
			success: function(response){
				var hash = Ext.JSON.decode( response.responseText );
				if(hash) Ag.data.SYSTEM_ELEMENT_COLOR = hash;
			}
		});
*/

		Ext.create('Ext.data.TreeStore', {
			storeId: 'system-tree-store',
			model: 'Ag.data.Model.SYSTEM_TREE',
			proxy: {
				type: 'memory'
			},
			root: {
				allowDrag: false,
				allowDrop: false,
				depth: 0,
				expanded: true,
				root: true,
				text: 'whole',
				name: 'root',
				system_id: 'whole'
			}
		});

		Ext.create('Ext.data.Store', {
			storeId: 'system-grid-store',
			model: 'Ag.data.Model.SYSTEM_GRID',
			remoteSort: false,
			sorters: [{
				property: Ag.Def.NAME_DATA_FIELD_ID,
				direction: 'ASC'
			}],
		});

		if(1){
			let disableCaching = Ext.isNumber(Ag.Def.DEF_FILE_MTIME['art_file_info.jgz']) ? false : true;
			let url = 'renderer_file/art_file_info.jgz' + (Ext.isNumber(Ag.Def.DEF_FILE_MTIME['art_file_info.jgz']) ? '?'+Ag.Def.DEF_FILE_MTIME['art_file_info.jgz'] : '');
			if (disableCaching===false && window.aglocalforage) {
				aglocalforage.getItem(url).then(function(value) {
					if(value !== null){
						if(Ext.isObject(value)) Ag.data.art_file_info = value;
					}
					else{

						Ext.Ajax.request({
							disableCaching: disableCaching,
							url: url,
							callback: function(options,success,response){
							},
							success: function(response){
								var hash = Ext.JSON.decode( response.responseText );
								if(Ext.isObject(hash)){
									aglocalforage.setItem(url, hash).then(function (value) {
										if(Ext.isObject(value)) Ag.data.art_file_info = value;
									}).catch(function(err) {
										console.error(err);
									});
								}
							}
						});

					}
				}).catch(function(err) {
					console.error(err);
				});
			}
			else{
				Ext.Ajax.request({
					disableCaching: disableCaching,
					url: url,
					callback: function(options,success,response){
					},
					success: function(response){
						var hash = Ext.JSON.decode( response.responseText );
						if(Ext.isObject(hash)) Ag.data.art_file_info = hash;
					}
				});
			}
		}
/*
		Ext.Ajax.request({
			url: 'renderer_file/renderer_file.jgz',
			callback: function(options,success,response){
//				console.log('callback()');
				try{
					Ext.getCmp('main-viewport').__loadMask.hide();
				}catch(e){
					console.error(e);
				}
			},
			success: function(response){
//				console.log('success()');
				var hash = Ext.JSON.decode( response.responseText );
				if(Ext.isObject(hash)) Ag.data.renderer = hash;
//				console.log(Ag.data.renderer);
			}
		});
*/
		Ext.create('Ext.data.Store', {
			storeId: 'canvas-upload-store',
			model: 'Ag.data.Model.CONCEPT_TERM_PALLET',
			listeners: {
				add: function( store, records, index, eOpts ){
					_update_search_records(store,records,null,Ag.data.SEG2ART);
				}
			}
		});
	},

	loadRendererFile : function(){
		let self = this;
/**/
//		console.log('loadRendererFile');
		self.fireEvent('beforeloadrenderer');

		if(self.DEF_MODEL_VERSION_RECORD && self.DEF_MODEL_VERSION_RECORD instanceof Ext.data.Model){
			let display = self.DEF_MODEL_VERSION_RECORD.get('display');
			let disableCaching = Ext.isNumber(Ag.Def.DEF_FILE_MTIME[display+'.jgz']) ? false : true;
			let url = 'renderer_file/renderer_file/'+display+'.jgz' + (disableCaching ? '' : '?'+Ag.Def.DEF_FILE_MTIME[display+'.jgz']);
			if(Ext.isObject(Ag.data.renderer) && (Ext.isObject(Ag.data.renderer[display]) || Ext.isString(Ag.data.renderer[display]))){
				self.fireEvent('loadrenderer',true);
				return;
			}
			if(Ext.isObject(Ag.data.isLoadingRenderer) && Ext.isBoolean(Ag.data.isLoadingRenderer[display]) && Ag.data.isLoadingRenderer[display]){
				return;
			}
			Ag.data.isLoadingRenderer = Ag.data.isLoadingRenderer || {};
			Ag.data.isLoadingRenderer[display] = true;

			try{
				Ext.getCmp('main-viewport').__loadMask.show();
			}catch(e){
//				console.log(e);
			}


			var success = function(hash){
//					console.log('success()');
				if(Ext.isObject(hash)){
					Ag.data.renderer = Ag.data.renderer || {};
					Ext.Object.each(hash, function(key, value, self) {
						Ag.data.renderer[key] = hash[key];
//					console.log(Ag.data.renderer);
					});

					let cities_store = Ext.data.StoreManager.lookup('cities-list-store');
					let system_list_store = Ext.data.StoreManager.lookup('system-list-store');
//						let keyword_search_store = Ext.data.StoreManager.lookup('keyword-search-store');

					let viewport = self.getViewport();
					let window_panel         = viewport.down('panel#window-panel');
					let segment_filtering_combobox = window_panel.down('combobox#segment-filtering-combobox');
					let segment_filtering_value = segment_filtering_combobox.getValue();

					let fn = function(){
						if(Ext.isEmpty(Ag.data.keyword_search)) Ag.data.keyword_search = {};
						if(Ext.isEmpty(Ag.data.keyword_search[display])){

							if(cities_store.isLoading()){
								cities_store.on({
									load: {
										fn: fn,
										single: true
									}
								});
								return;
							}
							if(system_list_store.isLoading()){
								system_list_store.on({
									load: {
										fn: fn,
										single: true
									}
								});
								return;
							}

							let SEG2ART = segment_filtering_value==='SEG2ART' ? Ag.data.SEG2ART : Ag.data.SEG2ART_INSIDE;
//							console.log('SEG2ART', SEG2ART);
							if(Ext.isEmpty(SEG2ART)){
								Ext.defer(fn, 250);
								return;
							}
							if(Ext.isEmpty(Ag.data.MENU_SEGMENTS_in_art_file)){
								Ext.defer(fn, 250);
								return;
							}
							if(Ext.isEmpty(Ag.data.citiesids2segment)){
								Ext.defer(fn, 250);
								return;
							}

//								console.log('Ag.data.MENU_SEGMENTS_in_art_file', Ag.data.MENU_SEGMENTS_in_art_file);
//								console.log('Ag.data.citiesids2segment', Ag.data.citiesids2segment);

//								console.log('display', display);
//								console.log('Ag.data.renderer', Ag.data.renderer[display]);

							let ids = Ag.data.renderer[display]['ids'];
							let art_ids = Ag.data.renderer[display]['art_ids'];
							if(Ext.isEmpty(ids) || Ext.isEmpty(art_ids)){
								if(Ext.isEmpty(ids)) console.warn('ids is empty!!');
								if(Ext.isEmpty(art_ids)) console.warn('art_ids is empty!!');
								return;
							}

							let name2cities = {};
							let cities = Ext.Array.map(cities_store.getRange(),function(record){
								let data = record.getData();
								name2cities[data['name']] = data;
								return data;
							});
//								console.log('name2cities', name2cities);

							let system_id2name = {};
							system_list_store.each(function(record){
								let system_id = (record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID).split('/'))[0];
								let system_name = record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID);
								if(system_name.match(/^[0-9]+(.+)$/)) system_name = RegExp.$1;
								if(system_name.match(/^_+(.+)$/)) system_name = RegExp.$1;
								system_id2name[system_id] = system_name;
							});
//								console.log('system_id2name', system_id2name);

							let seg2art = {};
							Ext.Object.each(SEG2ART['CITIES'], function(key,value){
								Ext.Array.map(Ext.Object.getKeys(value), function(art_id){ seg2art[art_id] = true; });
							});

							let use_ids;
							Ext.Object.each(art_ids, function(art_id, data, myself) {

								if(!Ext.isBoolean(seg2art[art_id]) || !seg2art[art_id]){
//										console.log(art_id);
									return true;
								}

								let id = data[Ag.Def.ID_DATA_FIELD_ID];
								let artc_id = data[Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID];
								if(Ext.isEmpty(id) || Ext.isEmpty(ids[id])) return true;
								if(!Ext.isBoolean(ids[id]['is_element']) || !ids[id]['is_element']) return true;

								if(Ext.isEmpty(use_ids)) use_ids = {};
								if(Ext.isEmpty(use_ids[id])){
									var tempobj = {};
									tempobj[Ag.Def.OBJ_ID_DATA_FIELD_ID] = art_id;
									tempobj[Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID] = artc_id;
									use_ids[id] = Ext.Object.merge(tempobj, ids[id]);
								}

								var system_id = ids[id][Ag.Def.SYSTEM_ID_DATA_FIELD_ID];
								if(Ext.isString(system_id) && system_id.length){
									use_ids[id]['system_name'] = system_id2name[system_id];
								}

								var synonym = ids[id]['synonym'];
								if(Ext.isString(synonym) && synonym.length){
									delete use_ids[id]['synonym'];
									use_ids[id]['synonym'] = Ext.Array.map(synonym.split(';'), function(str){ return Ext.String.trim(str); });
								}
								if(Ext.isObject(Ag.data.MENU_SEGMENTS_in_art_file[art_id])){
									Ext.Array.each(Ext.Object.getKeys(Ag.data.MENU_SEGMENTS_in_art_file[art_id]['CITIES'] || {}), function(cities_name){
										var cities_id = name2cities[cities_name]['cities_id'];
										if(Ext.isEmpty(use_ids[id][Ag.Def.OBJ_CITIES_FIELD_ID])){
											use_ids[id][Ag.Def.OBJ_CITIES_FIELD_ID] = [cities_id];
											if(Ext.isString(Ag.data.citiesids2segment[cities_id]) && Ag.data.citiesids2segment[cities_id].length) use_ids[id]['segment'] = [Ag.data.citiesids2segment[cities_id]];
										}
										else{
											use_ids[id][Ag.Def.OBJ_CITIES_FIELD_ID].push(cities_id);
//											if(Ext.isString(Ag.data.citiesids2segment[cities_id]) && Ag.data.citiesids2segment[cities_id].length) use_ids[id]['segment'].push(Ag.data.citiesids2segment[cities_id]);
											if(Ext.isString(Ag.data.citiesids2segment[cities_id]) && Ag.data.citiesids2segment[cities_id].length && Ext.Array.contains(use_ids[id]['segment'],Ag.data.citiesids2segment[cities_id])==false) use_ids[id]['segment'].push(Ag.data.citiesids2segment[cities_id]);
										}
									});
								}

								if(Ext.isObject(use_ids[id]['relation'])){
									Ext.Object.each(use_ids[id]['relation'], function(relation,value){
										if(Ext.isObject(value)){
											Ext.Object.each(value, function(rid,rname){
												var v = use_ids[id][relation];
												if(Ext.isEmpty(v)){
													v = [{id:rid,name:rname}];
												}
												else{
													v.push({id:rid,name:rname});
												}
												use_ids[id][relation] = v;

												if(relation == 'is_a' || relation == 'lexicalsuper') return true;
												v = use_ids[id]['part_of'];
												if(Ext.isEmpty(v)){
													v = [{id:rid,name:rname}];
												}
												else{
													v.push({id:rid,name:rname});
												}
												use_ids[id]['part_of'] = v;
											});
										}
									});
								}

							});
//								console.log(use_ids);
							Ag.data.keyword_search[display] = use_ids;
						}
//							keyword_search_store.clearFilter(true);
//							keyword_search_store.removeAll(true);
//							keyword_search_store.add(Ext.Object.getValues(Ag.data.keyword_search[display]));

					};

					Ext.defer(fn, 0);

				}
			};

			if (disableCaching===false && window.aglocalforage) {
				aglocalforage.getItem(url).then(function(value) {
					if(value !== null){
						success(value);
						Ag.data.isLoadingRenderer[display] = false;
						self.fireEvent('loadrenderer',true);
						try{
							Ext.getCmp('main-viewport').__loadMask.hide();
						}catch(e){
							console.error(e);
						}
					}
					else{

						Ext.Ajax.request({
							disableCaching: disableCaching,
							url: url,
/*
							callback: function(options,success,response){
								Ag.data.isLoadingRenderer[display] = false;
			//					console.log('loadrenderer',success);
								self.fireEvent('loadrenderer',success);
								try{
									Ext.getCmp('main-viewport').__loadMask.hide();
								}catch(e){
									console.log(e);
								}
							},
*/
							success: function(response){
			//					console.log('success()');
								let hash = Ext.JSON.decode( response.responseText );
								aglocalforage.setItem(url, hash).then(function (value) {
									success(value);

									Ag.data.isLoadingRenderer[display] = false;
									self.fireEvent('loadrenderer',true);
									try{
										Ext.getCmp('main-viewport').__loadMask.hide();
									}catch(e){
										console.error(e);
									}


								}).catch(function(err) {
									console.error(err);

									Ag.data.isLoadingRenderer[display] = false;
									self.fireEvent('loadrenderer',false);
									try{
										Ext.getCmp('main-viewport').__loadMask.hide();
									}catch(e){
										console.error(e);
									}

								});
							},
							failure: function(response, opts){
								Ag.data.isLoadingRenderer[display] = false;
								self.fireEvent('loadrenderer',false);
								try{
									Ext.getCmp('main-viewport').__loadMask.hide();
								}catch(e){
									console.error(e);
								}
							}
						});

					}
				}).catch(function(err) {
					console.error(err);
					Ag.data.isLoadingRenderer[display] = false;
					self.fireEvent('loadrenderer',false);
					try{
						Ext.getCmp('main-viewport').__loadMask.hide();
					}catch(e){
						console.error(e);
					}
				});
			}
			else{
				Ext.Ajax.request({
					disableCaching: disableCaching,
					url: url,
					callback: function(options,success,response){
						Ag.data.isLoadingRenderer[display] = false;
	//					console.log('loadrenderer',success);
						self.fireEvent('loadrenderer',success);
						try{
							Ext.getCmp('main-viewport').__loadMask.hide();
						}catch(e){
							console.log(e);
						}
					},
					success: function(response){
	//					console.log('success()');
						let hash = Ext.JSON.decode( response.responseText );
						success(hash);
					}
				});
			}
		}
/**/
	},

	addRecords : function(view,records){
		var self = this;
		if(Ext.isEmpty(view) || Ext.isEmpty(records)) return;
		var store = view.getStore ? view.getStore() : null;
		if(Ext.isEmpty(store)) return;

//		return self._addRecords(store,records);

		var add_recors = null;
		try{
			var sorters = store.sorters.getRange();
			if(sorters.length){
				store.sorters.clear();
				view.headerCt.clearOtherSortStates();
			}
			add_recors = store.add(records);
			if(sorters.length){
				store.sorters.addAll(sorters);
				store.sort();
			}
		}catch(e){
			console.error(e);
			try{
				if(view) self.refreshView(view);
			}catch(e){}
		}

		return add_recors;
	},

	removeRecords : function(view,records){
		var self = this;
		if(Ext.isEmpty(view) || Ext.isEmpty(records)) return;
		var store = view.getStore ? view.getStore() : null;
		if(Ext.isEmpty(store)) return;

		var sorters = store.sorters.getRange();
		if(sorters.length){
			store.sorters.clear();
			view.headerCt.clearOtherSortStates();
		}
		try{
			if(store.getCount()===records.length){
				store.removeAll();
			}else{
				if(view.stripeRows){
					view.stripeRows = false;
					store.remove(records);
					view.stripeRows = true;
				}else{
					store.remove(records);
				}
			}
		}catch(e){
			console.error(e);
		}
		if(sorters.length){
			store.sorters.addAll(sorters);
			store.sort();
		}
	}
});

