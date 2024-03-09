window.AgApp = window.AgApp || function(config){};
window.AgApp.prototype.openConceptMngWin = function(aOpt){
	var self = this;
	aOpt = Ext.apply({},aOpt||{},{
		iconCls: 'gear-btn',
		title: AgLang.concept_mng,
		modal: true,
		width: 800,
//		height: 435
		height: 500
	});

	if(aOpt.width  > Ext.getBody().getWidth())  aOpt.width  = Ext.getBody().getWidth();
	if(aOpt.height > Ext.getBody().getHeight()) aOpt.height = Ext.getBody().getHeight();

	var setDisabledSaveButton = function(field){
		var gridpanel = field.up('window').down('gridpanel');
		var store = gridpanel.getStore();
		var num = 0;
		num += store.getModifiedRecords().length;
		num += store.getNewRecords().length;
		num += store.getRemovedRecords().length;
		num += store.getUpdatedRecords().length;
		var formPanel = field.up('form');
		var disable = !formPanel.getForm().isValid();
		if(!disable) disable = num===0;
		formPanel.getDockedItems('toolbar[dock="bottom"]')[0].down('#save').setDisabled(disable);
	};

	var concept_mng_win = Ext.create('Ext.window.Window', {
		animateTarget: aOpt.animateTarget,
		iconCls: aOpt.iconCls,
		title: aOpt.title,
		modal: aOpt.modal,
		width: aOpt.width,
		height: aOpt.height,
		autoShow: true,
		border: false,
		maximizable: true,
		minHeight: 300,
		closeAction: 'destroy',
		stateful: true,
		stateId: 'concept-mng-window',
		layout: 'fit',
		items: [{
			xtype: 'tabpanel',
			activeTab: 'concept-build-panel',
			bodyStyle: {
				backgroundColor: 'transparent'
			},
			defaults: {
				border: false,
				bodyStyle: {
					backgroundColor: 'transparent'
				}
			},
			items: [{
				title: 'Concept info',
				itemId: 'concept-info-panel',
				layout: {
					type: 'vbox',
					align: 'stretch'
				},
			},{
				title: 'Concept build',
				itemId: 'concept-build-panel',
				layout: {
					type: 'vbox',
					align: 'stretch'
				},
				defaults: {
					minHeight: 100,
				},
				items: [{
					region: 'center',
					flex: 1,
					xtype: 'aggridpanel',
					store: 'conceptBuildStore',
					stateful: true,
					itemId: 'concept-build-gridpanel',
					stateId: 'concept-build-gridpanel',
					columns: [
						{
							text: 'Concept',
							dataIndex: 'ci_name',
							stateId: 'ci_name',
							width: 36,
							minWidth: 36,
							draggable: false,
							hidden:false,
							hideable:false
						},
						{
							text: 'Build',
							dataIndex: 'cb_name',
							stateId: 'cb_name',
							width: 86,
							minWidth: 86,
							draggable: false,
							hidden:false,
							hideable:false
						},
						{
							text: 'Updated Date',
							dataIndex: 'cb_release',
							stateId: 'cb_release',
							width: 70,
							minWidth: 70,
							draggable: false,
							hidden:false,
							hideable:false,
							xtype:'datecolumn',
							format:self.FORMAT_DATE
						},
						{
							text: AgLang.comment,
							dataIndex: 'cb_comment',
							stateId: 'cb_comment',
							flex: 2,
							minWidth: 60,
							draggable: false,
							hidden:false,
							hideable:false
						},
						{
							text: AgLang.order,
							dataIndex: 'cb_order',
							stateId: 'cb_order',
							width: 40,
							minWidth: 40,
							draggable: false,
							hidden: false,
							hideable: false,
							align: 'right'
						},
						{
							text: AgLang.use,
							align: 'center',
							xtype: 'booleancolumn',
							dataIndex: 'cb_use',
							stateId: 'cb_use',
							width: 30,
							minWidth: 30,
							draggable: false,
							hidden: false,
							hideable: true,
							trueText: 'Yes',
							falseText: '<b style="color:red;">No</b>'
//							renderer: function(value){
//								if(value){
//									return 'Yes';
//								}else{
//									return '<b style="color:red;">No</b>';
//								}
//							}
						},
						{
							text: 'cb_id',
							dataIndex: 'cb_id',
							stateId: 'cb_id',
							width: 37,
							minWidth: 37,
							draggable: false,
							hidden: true,
							hideable: true,
							align: 'right'
						}
					],
					viewConfig: {
						autoScroll: true,
						overflowX: 'hidden',
						overflowY: 'scroll',
						stripeRows:true,
						enableTextSelection:false,
						loadMask:true
					},
					selType: 'rowmodel',
					selModel: {
						mode:'SINGLE'
					},
					listeners: {
						afterrender: function(gridpanel,eOpts){

							try{
								var columns = gridpanel.view.getGridColumns();
								columns.forEach(function(column){
									if(column.getXType()=='rownumberer'){
										gridpanel.view.autoSizeColumn(column);
									}else if(Ext.isEmpty(column.flex) && column.isVisible() && column.resizable){
										gridpanel.view.autoSizeColumn(column);
									}
								});
							}catch(e){
								console.error(e);
							}
							var store = gridpanel.getStore();
							store.on('load',function(store, records, successful, eOpts){
								try{
									if(successful && records.length>0){
										var columns;
										try{columns = gridpanel.view.getGridColumns();}catch(e){}
										if(Ext.isEmpty(columns)) return;
										columns.forEach(function(column){
											if(column.getXType()=='rownumberer'){
												gridpanel.view.autoSizeColumn(column);
											}else if(Ext.isEmpty(column.flex) && column.isVisible() && column.resizable){
												gridpanel.view.autoSizeColumn(column);
											}
										});
									}
								}catch(e){
									console.error(e);
								}
							},store,{
								buffer: 100
							});

						},
						render: function(grid,eOpts){
		//											grid.getView().on({
		//												beforeitemkeydown: function(view, record, item, index, e, eOpts){
		//													e.stopPropagation();
		//													return false;
		//												}
		//											});
						},
						selectionchange: function(selModel,records){
							var formPanel = this.nextSibling('form');
							var form = formPanel.getForm();
							form.getFields().each(function(field,index,len){
								field.suspendEvents(false);
								field.reset();
								field.setDisabled(true);
								field.setReadOnly(true);
							});

							if(records[0]){
								form.loadRecord(records[0]);
								form.getFields().each(function(field,index,len){
									field.setDisabled(false);
									field.setReadOnly(false);
								});
							}

							form.getFields().each(function(field,index,len){
								field.resumeEvents();
							});

						}
					}
				},{
					region: 'south',
		//									height: 176,
		//									height: 240,
					height: 100,
					xtype: 'form',
					bodyPadding: 10,
					defaults: {
						labelAlign: 'right',
						labelWidth: 60
					},
					items: [{
						xtype: 'fieldcontainer',
						layout: {
							type: 'hbox',
							align: 'top',
							pack: 'start',
							defaultMargins: {top: 0, right: 4, bottom: 0, left: 0}
						},
						defaults: {
							labelAlign: 'right',
							labelWidth: 60
						},
						items: [{
							disabled: true,
							xtype: 'textfield',
							fieldLabel: AgLang.build_signage,
							name: 'cb_name',
							allowBlank: false,
							selectOnFocus: true,
							width: 200,
							listeners: {
								change: function(field,newValue,oldValue,eOpts){
									var gridpanel = field.up('window').down('gridpanel');
									var rec = gridpanel.getSelectionModel().getLastSelected();
									var name = field.getName();
									rec.beginEdit();
									rec.set(name,newValue);
									var display;
									var cb_comment = rec.get('cb_comment');
									if(Ext.isString(cb_comment)) cb_comment = cb_comment.trim();
									if(Ext.isEmpty(cb_comment)){
										rec.set('display',Ext.util.Format.format('{0} {1}',rec.get('ci_name'),newValue));
									}else{
										rec.set('display',Ext.util.Format.format('{0} {1} [{2}]',rec.get('ci_name'),newValue,cb_comment));
									}
									rec.endEdit(false,[name,'display']);
									setDisabledSaveButton(field);
								},
								specialkey: function(field, e, eOpts){
									e.stopPropagation();
								}
							}
						},{
							disabled: true,
							xtype: 'datefield',
							fieldLabel: 'Updated Date',
							name: 'cb_release',
							allowBlank: false,
							selectOnFocus: true,
							labelWidth: 90,
							width: 200,
							maxValue: new Date(),
							format: 'Y/m/d',
							listeners: {
								change: function(field,newValue,oldValue,eOpts){
									var gridpanel = field.up('window').down('gridpanel');
									var rec = gridpanel.getSelectionModel().getLastSelected();
									var name = field.getName();
									rec.beginEdit();
									rec.set(name,newValue);
									rec.endEdit(false,[name]);
									setDisabledSaveButton(field);
								},
								specialkey: function(field, e, eOpts){
									e.stopPropagation();
								}
							}
						},{
							disabled: true,
							xtype: 'numberfield',
							fieldLabel: AgLang.order,
							name: 'cb_order',
							allowBlank: false,
							selectOnFocus: true,
							width: 120,
							minValue: 1,
							listeners: {
								change: function(field,newValue,oldValue,eOpts){
									var gridpanel = field.up('window').down('gridpanel');
									var rec = gridpanel.getSelectionModel().getLastSelected();
									var name = field.getName();
									rec.beginEdit();
									rec.set(name,newValue);
									rec.endEdit(false,[name]);
									setDisabledSaveButton(field);
								},
								specialkey: function(field, e, eOpts){
									e.stopPropagation();
								}
							}

						},{
							disabled: true,
							xtype: 'checkboxfield',
							fieldLabel: AgLang.use,
							boxLabel: 'Yes',
							name: 'cb_use',
							listeners: {
								change: function(field,newValue,oldValue,eOpts){
									var gridpanel = field.up('window').down('gridpanel');
									var rec = gridpanel.getSelectionModel().getLastSelected();
									var name = field.getName();
									rec.beginEdit();
									rec.set(name,newValue);
									rec.endEdit(false,[name]);
									setDisabledSaveButton(field);
								}
							}


						}]
					},{
						disabled: true,
						xtype: 'textfield',
						fieldLabel: AgLang.comment,
						name: 'cb_comment',
						selectOnFocus: true,
						anchor: '100%',
						listeners: {
							change: function(field,newValue,oldValue,eOpts){
								var gridpanel = field.up('window').down('gridpanel');
								var rec = gridpanel.getSelectionModel().getLastSelected();
								var name = field.getName();
								rec.beginEdit();
								rec.set(name,newValue);

								var display;
								var cb_comment = newValue;
								if(Ext.isString(cb_comment)) cb_comment = cb_comment.trim();
								if(Ext.isEmpty(cb_comment)){
									rec.set('display',Ext.util.Format.format('{0} {1}',rec.get('ci_name'),rec.get('cb_name')));
								}else{
									rec.set('display',Ext.util.Format.format('{0} {1} [{2}]',rec.get('ci_name'),rec.get('cb_name'),cb_comment));
								}
								rec.endEdit(false,[name,'display']);

								setDisabledSaveButton(field);
							},
							specialkey: function(field, e, eOpts){
								e.stopPropagation();
							}
						}
					}],
					buttons: [{
						disabled: true,
						itemId: 'export',
						text: AgLang.export,
						iconCls: 'pallet_download',
						menu: {
							defaults: {
								iconCls: 'pallet_download'
							},
							items: [{
								itemId: 'all_data',
								text: 'Cencept all data',
							},{
								itemId: 'only_data',
								text: 'Only concepts that are used in this build',
							}],
							listeners: {
								click: function( menu, item, e, eOpts ){
									var b = item.up('button');
									var win = item.up('window');
									var gridpanel = win.down('gridpanel');
									var selModel = gridpanel.getSelectionModel();
									var record = selModel.getLastSelected();
									var config = {
										cmd: 'export-concept',
										format: 'zip',
										title:  Ext.util.Format.format('{0} [ {1} - {2} ]',aOpt.title, b.text, item.text),
										iconCls: item.iconCls,
										ci_id: record.get('ci_id'),
										cb_id: record.get('cb_id'),
										filename: Ext.util.Format.format(
											'concept_{0}_{1}_{2}_{3}',
											record.get('ci_name'),
											record.get('cb_name').replace(Ext.form.field.VTypes.filenameReplaceMask,'_'),
											Ext.util.Format.date(record.get('cb_release'),'Ymd'),
											Ext.util.Format.date(new Date(),'YmdHis')
										)
									};
									config[item.itemId] = 1;
									self.export(config);
								}
							}
						},
						listeners: {
							afterrender: function(b,eOpts){
								var win = b.up('window');
								var gridpanel = win.down('gridpanel');
								gridpanel.on('selectionchange',function( selModel, selected, eOpts ){
									b.setDisabled(Ext.isEmpty(selected));
								});
							},
							click: function(b){
								return;
								var win = b.up('window');
								var gridpanel = win.down('gridpanel');
								var selModel = gridpanel.getSelectionModel();
								var record = selModel.getLastSelected();
								self.export({
									cmd: 'export-concept',
									format: 'zip',
									title: aOpt.title + ' [ ' + b.text +' ]',
									iconCls: b.iconCls,
									ci_id: record.get('ci_id'),
									cb_id: record.get('cb_id'),
									filename: Ext.util.Format.format(
										'concept_{0}_{1}_{2}_{3}',
										record.get('ci_name'),
										record.get('cb_name').replace(Ext.form.field.VTypes.filenameReplaceMask,'_'),
										Ext.util.Format.date(record.get('cb_release'),'Ymd'),
										Ext.util.Format.date(new Date(),'YmdHis')
									)
								});
							}
						}
					},'->',{
						disabled: true,
						itemId: 'save',
						text: AgLang.save,
						listeners: {
							click: {
								fn: function(b){
									var win = b.up('window');
									var gridpanel = win.down('gridpanel');
									win.setLoading(true);
									var store = gridpanel.getStore();
									store.sync({
										callback: function(batch,options){
		//															console.log('callback()');
											gridpanel.getSelectionModel().deselectAll();
											win.setLoading(false);
										},
										success: function(batch,options){
		//															console.log('success()');

											var proxy = this;
											var reader = proxy.getReader();
											if(reader && reader.rawData && reader.rawData.msg && Ext.isString(reader.rawData.msg)){
		//																var msg = Ext.util.Format.nl2br(reader.rawData.msg);

												Ext.Msg.show({
													title: b.text,
													iconCls: b.iconCls,
		//																	msg: msg,
													buttons: Ext.Msg.OK,
													icon: Ext.Msg.WARNING,
													value: reader.rawData.msg,
													multiline: true,
													prompt: true,
													width: 600
												});

											}


											b.setDisabled(true);
//											var versionCombobox = Ext.getCmp('version-combobox');
//											var value = versionCombobox.getValue();
//											versionCombobox.getStore().loadPage(1,{
//												callback: function(){
//												}
//											});
										},
										failure: function(batch,options){
		//															console.log('failure()');
											var msg = AgLang.error_save;
											var value = '';
											var proxy = this;
											var reader = proxy.getReader();
											if(reader && reader.rawData && reader.rawData.msg){
												value = reader.rawData.msg;
											}
											Ext.Msg.show({
												title: b.text,
												iconCls: b.iconCls,
												msg: msg,
												buttons: Ext.Msg.OK,
												icon: Ext.Msg.ERROR,
												value: value,
												multiline: true,
												prompt: true,
												width: 600
											});
										}
									});
								},
								buffer: 100
							}
						}
					},{
						text: AgLang.cancel,
						listeners: {
							click: function(b){
								var gridpanel = b.up('window').down('gridpanel');
								gridpanel.getSelectionModel().deselectAll();
								var store = gridpanel.getStore();
								var newRecords = store.getNewRecords();
								store.rejectChanges();
								b.previousSibling('button').setDisabled(true);
							}
						}
					}]
				}],
			}],
		}],
		buttons: ['->',{
			text: AgLang.close,
			listeners: {
				click: function(b){
					b.up('window').close();
				}
			}
		}],
		listeners: {
			show: function(comp){
				var store = comp.down('gridpanel').getStore();
				store.loadPage(1,{
					callback: function(records,operation,success){
						store.clearFilter();
					}
				});
			},
			beforeclose: function(comp,eOpts){
				var store = comp.down('gridpanel').getStore();
				store.loadPage(1,{
					callback: function(records,operation,success){
						store.clearFilter(false);
						store.filter('cb_use',true);
					}
				});
			}
		}
	});



};
