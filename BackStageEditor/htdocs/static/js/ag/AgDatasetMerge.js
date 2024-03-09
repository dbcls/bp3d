window.AgApp = window.AgApp || function(config){};

window.AgApp.prototype.openDatasetMergeWindow = function(config){
	var self = this;

	config = config || {};
	var aCB = config.callback;
	config.title = config.title || AgLang.merge;
	config.iconCls = config.iconCls || 'pallet_merge';
	config.height = config.height || 600;
	config.width = config.width || 600;
	config.modal = config.modal || true;

	var maxHeight = $(document.body).height();
	var maxWidth = $(document.body).width();

	if(config.height>maxHeight) config.height = maxHeight;
	if(config.width>maxWidth) config.width = maxWidth;

	var window_id = Ext.id();

	var datasetMngStore = Ext.data.StoreManager.lookup('datasetMngStore');
	var conceptBuildStore = Ext.data.StoreManager.lookup('conceptBuildStore');
	if(Ext.isEmpty(config.concept_datas)) config.concept_datas = conceptBuildStore.getRange().map(function(r){return r.getData();});
	if(Ext.isEmpty(config.dataset_datas)) config.dataset_datas = datasetMngStore.getRange().map(function(r){return r.getData();});

/*
	config.concept_datas = config.concept_datas || [];
	config.concept_datas.unshift({value:'all',display:'ALL'});

	var filterConceptStore = Ext.create('Ext.data.Store', {
		autoDestroy: true,
		storeId: 'filterConceptStore',
		model: 'CONCEPT',
		sorters: [{
			property: 'cb_order',
			direction: 'ASC'
		}],
		data: config.concept_datas
	});

	var sourceDatasetStore = Ext.create('Ext.data.Store', {
		autoDestroy: true,
		storeId: 'sourceDatasetStore',
		model: 'VERSION',
		sorters: [{
			property: 'mv_order',
			direction: 'ASC'
		},{
			property: 'fmt_version',
			direction: 'DESC'
		}],
		data: config.dataset_datas || [],
		listeners: {
			add: {
				fn: function(store){
					store.filter();
					store.sort();
				},
				buffer: 100
			},
			filterchange: function( store, filters, eOpts ){
				store.sort();
			}
		}
	});

	var updateMergePriority = function(store){
		store.suspendEvent('update');
		try{
			store.each(function(record,idx){
				record.beginEdit();
				record.set('mv_priority',idx+1);
				record.commit(false,['mv_priority']);
				record.endEdit(false,['mv_priority']);
			});
		}catch(e){
			console.error(e);
		}
		store.resumeEvent('update');

		var win = Ext.getCmp(window_id);
		if(win){
			var grid = win.down('gridpanel#merge-destination-dataset-grid');
			if(grid) grid.getView().refresh();
		}
	};
*/
	var setDisabledSaveButton = function(store){
		var win = Ext.getCmp(window_id);
		if(!win) return;
//		var num = store.getCount();

		var num = 0;
		try{num = win.down('agselectdatasetfield').getCount();}catch(e){}

		var disable = false;
		if(!disable) disable = num===0;
		var toolbar = win.getDockedItems('toolbar[dock="bottom"]')[0];
		toolbar.getComponent('merge').setDisabled(disable);
		toolbar.getComponent('reset').setDisabled(disable);
	};

/*
	var destinationDatasetStore = Ext.create('Ext.data.Store', {
		autoDestroy: true,
		storeId: 'destinationDatasetStore',
		model: 'VERSION',
		sorters: [{
			property: 'mv_priority',
			direction: 'ASC'
		}],
		data: config.destination_dataset_datas || [],
		listeners: {
			add: {
				fn: function(store){
					updateMergePriority(store);
					setDisabledSaveButton(store);
				},
				buffer: 100
			},
			remove: {
				fn: function(store){
					updateMergePriority(store);
					setDisabledSaveButton(store);
				},
				buffer: 100
			}
		}
	});

	var filterSourceDatasetStore = function(){
		Ext.defer(function(){
			var win = Ext.getCmp(window_id);
			if(win){
				var concept = null;
				var mv_use = false;
				var mv_frozen = false;
				var mv_publish = false;
				var keyword = null;
				var filters = [];
				try{concept = win.down('combobox#concept-combobox').getValue();}catch(e){}
				try{mv_use = win.down('checkboxfield#mv_use-checkboxfield').getValue();}catch(e){}
				try{mv_frozen = win.down('checkboxfield#mv_frozen-checkboxfield').getValue();}catch(e){}
				try{mv_publish = win.down('checkboxfield#mv_publish-checkboxfield').getValue();}catch(e){}
				try{keyword = win.down('textfield#keyword-textfield').getValue();}catch(e){}

				if(Ext.isString(concept) && concept.trim().length && concept != 'all'){
					var concept_record;
					try{concept_record = win.down('combobox#concept-combobox').findRecordByValue(concept);}catch(e){}
					if(concept_record){
						filters.push({
							filterFn: function(record){
								return concept_record.get('ci_id') === record.get('ci_id') && concept_record.get('cb_id') === record.get('cb_id');
							}
						});
					}
				}

				if(mv_use) filters.push({property: 'mv_use', value: true});
				if(mv_frozen) filters.push({property: 'mv_frozen', value: true});
				if(mv_publish) filters.push({property: 'mv_publish', value: true});
				if(Ext.isString(keyword) && keyword.trim().length){
					var keywords = keyword.trim().replace(/\s{2,}/,' ').split(' ');
					keywords.forEach(function(keyword){
						keyword = new RegExp(Ext.String.escapeRegex(keyword.trim()),'i');
						filters.push({
							filterFn: function(record){
								return keyword.test(record.get('version')) || keyword.test(record.get('mv_objects_set'));
							}
						});
					});
				}

				sourceDatasetStore.clearFilter(filters.length>0?true:false);
				if(filters.length) sourceDatasetStore.filter(filters);

			}
		},100);

	};
*/

	var merge_window = Ext.create('Ext.window.Window', {
		id: window_id,
		title: config.title,
		iconCls: config.iconCls,
		modal: config.modal,
		height: config.height,
		width: config.width,
		minWidth: config.width,
		minHeight: config.height,
		animateTarget: config.animateTarget,
		buttons: [{
			hidden: true,
			itemId: 'reset',
			text: AgLang.reset,
			disabled: true,
			listeners: {
				click: function(b,e,eOpts){
					var win = Ext.getCmp(window_id);
					var gridpanel = win.down('gridpanel');
					var store = gridpanel.getStore();
					store.rejectChanges();
					setDisabledSaveButton();
				}
			}
		},'->',{
			itemId: 'merge',
			text: AgLang.merge,
			disabled: true,
			listeners: {
				click: function(b,e,eOpts){
					var win = b.up('window');
					if(!win) return;
					var formPanel = win.down('form');
					var basicForm = formPanel.getForm();
					if(!basicForm.isValid()) return;

					if(b.isDisabled()) return;
					b.setDisabled(true);
					try{
						var submitValues = Ext.apply({},basicForm.getValues(),self.getExtraParams() || {});
						delete submitValues.current_datas;
						delete submitValues._ExtVerBuild;
						delete submitValues._ExtVerMajor;
						delete submitValues._ExtVerMinor;
						delete submitValues._ExtVerPatch;
						delete submitValues._ExtVerRelease;
						delete submitValues.ag_data;
						delete submitValues.bul_id;
						delete submitValues.model;
						delete submitValues.tree;

						var datasetMngStore = Ext.data.StoreManager.lookup('datasetMngStore');
						var max_mv_id = datasetMngStore.max('mv_id');
						submitValues.mv_id = (max_mv_id ? max_mv_id : 0) + 1;

						submitValues.mv_publish = false;

						try{
							submitValues.merge_mv_ids = win.down('agselectdatasetfield').getValue();
						}catch(e){
							submitValues.merge_mv_ids = [];
						}

/*
						destinationDatasetStore.each(function(record){
							submitValues.merge_mv_ids.push({
								md_id: record.get('md_id'),
								mv_id: record.get('mv_id')
							});
						});
*/

						var concept_field = basicForm.findField('concept');
						var concept_record = concept_field.findRecordByValue(submitValues.concept);
						delete submitValues.concept;
						submitValues.ci_id = concept_record.get('ci_id');
						submitValues.cb_id = concept_record.get('cb_id');
						submitValues.mv_order -= 0;

//console.log(submitValues);
//return;
						win.setLoading(config.title+'...');

						var proxy = datasetMngStore.getProxy();
						Ext.Ajax.request({
							url: proxy.api.create,
							method: proxy.actionMethods.create,
//							timeout: 3000,
							timeout: proxy.timeout,
							params: {
								datas: Ext.encode([submitValues])
							},
							callback: function(options,success,response){
								setDisabledSaveButton();
								win.setLoading(false);
								var json;
								try{json = Ext.decode(response.responseText)}catch(e){};
								if(success==false || Ext.isEmpty(json) || Ext.isEmpty(json.success) || json.success==false){
									if(Ext.isEmpty(json) || Ext.isEmpty(json.msg)){
										console.error(options,success,response);
										if(response.statusText){
											var msg = response.statusText;
											if(response.timedout) msg += ' [Timeout]';
											Ext.Msg.show({
												title: config.title,
												msg: msg,
												buttons: Ext.Msg.OK,
												icon: Ext.Msg.ERROR
											});
										}
										return;
									}
									Ext.Msg.show({
										title: config.title,
										iconCls: config.iconCls,
										buttons: Ext.Msg.OK,
										icon: Ext.Msg.WARNING,
										value: json.msg,
										multiline: true,
										prompt: true,
										width: 600
									});
									return;
								}
								datasetMngStore.loadPage(1);
								win.close();
							}
						});
					}catch(e){
						alert(e);
						setDisabledSaveButton();
						win.setLoading(false);
					}
				}
			}
		},{
			text: AgLang.close,
			listeners: {
				click: function(b,e,eOpts){
					if(aCB) (aCB)();
					b.up('window').close();
				}
			}
		}],
		layout: {
			type: 'vbox',
			align: 'stretch',
		},
		items: [
/*
		{
			itemId: 'filter-fieldset',
			xtype: 'fieldset',
			title: 'filter',
			margin: '0 10 0 10',
			height: 74,
			layout: {
				type: 'vbox',
				align: 'stretch',
			},
			items: [{
				itemId: 'concept-combobox',
				fieldLabel: 'Concept',
				labelWidth: 49,
				name: 'concept',
				xtype: 'combobox',
				editable: false,
				matchFieldWidth: false,
				displayField: 'display',
				valueField: 'value',
				queryMode: 'local',
				store: filterConceptStore,
				value: 'all',
				listeners: {
					afterrender: function(field, eOpt){
					},
					select: function(field, records, eOpts){
						filterSourceDatasetStore();
					}
				}
			},{
				xtype: 'fieldcontainer',
				layout: {
					type: 'hbox',
					align: 'stretch',
				},
				defaults: {
					margin: '0 10 0 0',
				},
				items: [{
					itemId: 'mv_use-checkboxfield',
					xtype: 'checkboxfield',
					boxLabel: AgLang.use,
					name: 'mv_use',
					listeners: {
						afterrender: function(field){
							field.setValue(true);
						},
						change: function(field,newValue,oldValue,eOpts){
							filterSourceDatasetStore();
						}
					}
				},{
					itemId: 'mv_frozen-checkboxfield',
					xtype: 'checkboxfield',
					boxLabel: AgLang.not_editable,
					name: 'mv_frozen',
					listeners: {
						change: function(field,newValue,oldValue,eOpts){
							if(!newValue && field.nextSibling('checkboxfield#mv_publish-checkboxfield').getValue()){
								field.nextSibling('checkboxfield#mv_publish-checkboxfield').setValue(false);
							}else{
								filterSourceDatasetStore();
							}
						}
					}
				},{
					itemId: 'mv_publish-checkboxfield',
					xtype: 'checkboxfield',
					boxLabel: AgLang.publish,
					name: 'mv_publish',
					listeners: {
						change: function(field,newValue,oldValue,eOpts){
							if(newValue && !field.previousSibling('checkboxfield#mv_frozen-checkboxfield').getValue()){
								field.prev('checkboxfield#mv_frozen-checkboxfield').setValue(true)
							}else{
								filterSourceDatasetStore();
							}
						}
					}
				},{
					flex: 1,
					margin: '0 0 0 0',
					itemId: 'keyword-textfield',
					xtype: 'textfield',
					fieldLabel: 'keyword(AND)',
					labelWidth: 82,
					enableKeyEvents: true,
					listeners: {
						change: function(field,newValue,oldValue,eOpts){
							filterSourceDatasetStore();
						},
						keydown: function(field,e,eOpts){
							e.stopPropagation();
						},
						keypress: function(field,e,eOpts){
							e.stopPropagation();
						},
						keyup: function(field,e,eOpts){
							e.stopPropagation();
						}
					}
				}]
			}]
		},{
			xtype: 'fieldcontainer',
			margin: '6 10 2 10',
			layout: {
				type: 'hbox',
				align: 'bottom',
				pack: 'center',
			},
			items: [{
				xtype: 'label',
				text: 'Drag and Drop',
			}]
		},{

			flex: 1,
			xtype: 'fieldcontainer',
			layout: {
				type: 'hbox',
				align: 'stretch',
			},
			defaults: {
				border: true,
				margin: '0 10 6 10',
			},
			items: [{
				flex: 1,
				title: 'Source Dataset',
				xtype: 'aggridpanel',
				store: sourceDatasetStore,
				columns: [{
					text: AgLang.version_signage,
					dataIndex: 'version',
					flex: 1,
					minWidth: 72,
					draggable: false,
					hidden:false,
					hideable:false
				}],
				selType: 'rowmodel',
				selModel: {
					mode:'MULTI'
				},
				viewConfig: {
					stripeRows:true,
					plugins: {
						ptype: 'gridviewdragdrop',
						dragText: 'Drag and drop to reorganize'
					}
				},
				listeners: {
					afterrender: function(comp){
						if(comp) comp.columns.forEach(function(c){if(Ext.isEmpty(c.flex)) c.autoSize()});
					},
					selectionchange: function(selModel,selected,eOpts){
					}
				}
			},{
				hidden: true,
				width: 40,
				xtype: 'fieldcontainer',
				margin: 0,
				layout: {
					type: 'vbox',
					align: 'center',
					pack: 'center',
				},
				defaultType: 'button',
				defaults: {
					disabled: true,
					margin: 10,
				},
				items: [{
					iconCls: 'pallet_right'
				},{
					iconCls: 'pallet_left'
				}]
			},{
				itemId: 'merge-destination-dataset-grid',
				flex: 1,
				title: 'Destination Dataset',
				xtype: 'aggridpanel',
				store: destinationDatasetStore,
				columns: [{
					text: AgLang.version_signage,
					dataIndex: 'version',
					flex: 1,
					minWidth: 72,
					draggable: false,
					hidden:false,
					hideable:false,
					sortable: false,
					menuDisabled: false,
				},{
					text: 'Priority',
					dataIndex: 'mv_priority',
					width: 40,
					minWidth: 40,
					draggable: false,
					hidden: false,
					hideable: false,
					sortable: false,
					menuDisabled: false,
					align: 'right'
				}],
				selType: 'rowmodel',
				selModel: {
					mode:'MULTI'
				},
				viewConfig: {
					stripeRows:true,
					plugins: {
						ptype: 'gridviewdragdrop',
						dragText: 'Drag and drop to reorganize'
					}
				},
				listeners: {
					afterrender: function(comp){
						if(comp) comp.columns.forEach(function(c){if(Ext.isEmpty(c.flex)) c.autoSize()});
					},
					selectionchange: function(selModel,selected,eOpts){
					}
				}
			}]

		}
*/
		{
			xtype: 'agselectdatasetfield',
			margin: '0 10 10 10',
			flex: 1,
			concept_datas: config.concept_datas || [],
			dataset_datas: config.dataset_datas || [],
			listeners: {
				select: function(field, records){
					setDisabledSaveButton();
				}
			}
		}


		,{
			height:130,
			xtype: 'form',
			border: false,
			bodyStyle: {backgroundColor:'transparent'},
			layout: {
				type: 'vbox',
				align: 'stretch',
			},
			items: [{
				xtype: 'fieldcontainer',
				margin: '0 10 0 10',
				layout: {
					type: 'hbox',
					align: 'middle ',
					pack: 'start',
				},
				defaultType: 'numberfield',
				defaults: {
					labelAlign: 'right',
					labelWidth: 50,
					margin: '0 10 0 0',
					allowBlank: false,
					allowDecimals: false,
					selectOnFocus: true,
					width: 100,
					minValue: 0,
					listeners: {
						change: function(field,newValue,oldValue,eOpts){
							try{
								var formPanel = field.up('form');
								var basicForm = formPanel.getForm();

								var version_field = basicForm.findField('version');
								var mv_objects_set_field = basicForm.findField('mv_objects_set');

								var version = version_field.getValue();
								var mv_objects_set = mv_objects_set_field.getValue();

								var version_version = basicForm.findField('version.version').getValue();
								var version_revision = basicForm.findField('version.revision').getValue();

								if(version.match(/^[0-9]+\.[0-9]+\.([0-9]+)$/)){
									version_field.setValue(Ext.util.Format.format('{0}.{1}.{2}',version_version,version_revision,RegExp.$1));
								}
								if(mv_objects_set.match(/^[0-9]+\.[0-9]+\.([0-9]+)$/)){
									mv_objects_set_field.setValue(Ext.util.Format.format('{0}.{1}.{2}',version_version,version_revision,RegExp.$1));
								}

							}catch(e){
								console.warn(e);
							}
						}
					}
				},
				items: [{
					fieldLabel: AgLang.version,
					name: 'version.version'
				},{
					fieldLabel: AgLang.revision,
					name: 'version.revision',
				}]
			},{
				xtype: 'fieldcontainer',
				margin: '10 10 0 10',
				layout: {
					type: 'hbox',
					align: 'middle ',
					pack: 'start',
				},
				defaults: {
					labelAlign: 'right',
					margin: '0 10 0 0',
					allowBlank: false,
					selectOnFocus: true,
					enableKeyEvents: true,
				},
				items: [{
					xtype: 'textfield',
					fieldLabel: AgLang.version_signage,
					labelWidth: 74,
					name: 'version',
					width: 200,
					listeners: {
						keydown: function(field,e,eOpts){
							e.stopPropagation();
						},
						keypress: function(field,e,eOpts){
							e.stopPropagation();
						},
						keyup: function(field,e,eOpts){
							e.stopPropagation();
						}
					}
				},{
					xtype: 'textfield',
					fieldLabel: AgLang.objects_set_signage,
					labelWidth: 87,
					name: 'mv_objects_set',
					width: 213,
					listeners: {
						keydown: function(field,e,eOpts){
							e.stopPropagation();
						},
						keypress: function(field,e,eOpts){
							e.stopPropagation();
						},
						keyup: function(field,e,eOpts){
							e.stopPropagation();
						}
					}
				},{
					xtype: 'numberfield',
					fieldLabel: AgLang.order,
					labelWidth: 34,
					name: 'mv_order',
					allowDecimals: false,
					width: 100,
					minValue: 1,
					value: 1
				}]
			},{
				xtype: 'fieldcontainer',
				margin: '10 10 0 10',
				layout: 'anchor',
				items: [{
					fieldLabel: 'Concept',
					labelWidth: 56,
					labelAlign: 'right',
					name: 'concept',
					anchor: '100%',
					xtype: 'combobox',
					editable: false,
					matchFieldWidth: false,
					displayField: 'display',
					valueField: 'value',
					store: 'conceptBuildStore',
					listeners: {
						afterrender: function(field, eOpt){
							var store = field.getStore();
							if(store.getCount()){
								field.setValue(store.getAt(0).get(field.valueField));
							}else{
								store.on('load',function(){
									field.setValue(store.getAt(0).get(field.valueField));
								},store,{single:true});
							}
						},
						select: function(field, records, eOpts){
						}
					}
				}]
			},{
				xtype: 'fieldcontainer',
				height: 36,
				layout: 'anchor',
				items: [{
					xtype: 'textfield',
					margin: '6 10 0 10',
					fieldLabel: AgLang.comment,
					labelWidth: 56,
					labelAlign: 'right',
					name: 'mv_comment',
					selectOnFocus: true,
					enableKeyEvents: true,
					anchor: '100%',
					listeners: {
						keydown: function(field,e,eOpts){
							e.stopPropagation();
						},
						keypress: function(field,e,eOpts){
							e.stopPropagation();
						},
						keyup: function(field,e,eOpts){
							e.stopPropagation();
						}
					}
				}]

			}]
		}],
		listeners: {
			afterrender: function(comp){
//				console.log(comp);

				var store = Ext.data.StoreManager.lookup('datasetMngStore');
				var max_version = store.max('fmt_version');
				var rec;
				if(max_version){
					rec = store.findRecord('fmt_version',max_version,0,false,false,true);
				}else{
					max_version = store.max('version');
					if(max_version) rec = store.findRecord('version',max_version,0,false,false,true);
				}
				if(rec){
					var version = rec.get('version_version');
					var revision = rec.get('version_revision')+1;// ((rec.data.version.split('.',2))[1]-0)+1;
//					console.log(version,revision);

					var formPanel = comp.down('form');
					var basicForm = formPanel.getForm();
					var version_version_field = basicForm.findField('version.version');
					if(version_version_field) version_version_field.setValue(version);
					var version_revision_field = basicForm.findField('version.revision');
					if(version_revision_field) version_revision_field.setValue(revision);

					var v = [version,revision,Ext.Date.format(new Date(), 'ymdhi')].join('.');

					var version_field = basicForm.findField('version');
					if(version_field) version_field.setValue(v);

					var mv_objects_set_field = basicForm.findField('mv_objects_set');
					if(mv_objects_set_field) mv_objects_set_field.setValue(v);

				}

			}
		}
	}).show();
};
