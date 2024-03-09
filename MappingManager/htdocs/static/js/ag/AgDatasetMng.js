window.AgApp = window.AgApp || function(config){};
window.AgApp.prototype.openDatasetMngWin = function(aOpt){
	var self = this;
	aOpt = Ext.apply({},aOpt||{},{
		iconCls: 'gear-btn',
		title: AgLang.dataset_mng,
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
		formPanel.getDockedItems('toolbar[dock="bottom"]')[0].down('button').setDisabled(disable);
	};

							var dataset_mng_win = Ext.create('Ext.window.Window', {
								animateTarget: aOpt.animateTarget,
								iconCls: aOpt.iconCls,
								title: aOpt.title,
								modal: aOpt.modal,
								width: aOpt.width,
								height: aOpt.height,
								autoShow: true,
								border: false,
								maximizable: true,
								closeAction: 'destroy',
								layout: 'border',
								items: [{
									region: 'center',
									xtype: 'aggridpanel',
									store: 'datasetMngStore',
									columns: [
										{
											text: AgLang.model,
											dataIndex: 'md_name_e',
											flex:1,
											minWidth: 80,
											hidden:true,
											hideable:false,
											filter:{type: 'string'}
										},
										{
											text: AgLang.version_signage,
											dataIndex: 'version',
											width: 72,
											minWidth: 72,
											hidden:false,
											hideable:true
										},
//										{text: AgLang.timestamp, dataIndex: 'mr_entry', width:112, minWidth:112, hidden:false, hideable:true,  xtype:'datecolumn',     format:self.FORMAT_DATE_TIME, filter:{type: 'date'}},
										{
											text: AgLang.objects_set_signage,
											dataIndex: 'mv_objects_set',
											width: 86,
											minWidth: 86,
											hidden:false,
											hideable:true
										},
										{
											text: 'FMA',
											dataIndex: 'ci_name',
											width: 36,
											minWidth: 36,
											hidden:false,
											hideable:true
										},
										{
											text: 'Build',
											dataIndex: 'cb_name',
											width: 86,
											minWidth: 86,
											hidden:false,
											hideable:true
										},
										{
											text: 'FMA Updated Date',
											dataIndex: 'cb_release',
											width: 70,
											minWidth: 70,
											hidden:false,
											hideable:true,
											xtype:'datecolumn',
											format:self.FORMAT_DATE
										},
										{
											text: 'Concept',
											dataIndex: 'cb_comment',
											flex: 2,
											minWidth: 60,
											hidden:false,
											hideable:true
										},
										{
											text: AgLang.comment,
											dataIndex: 'mv_comment',
											flex: 1,
											minWidth: 60,
											hidden:false,
											hideable:true
										},
										{
											text: AgLang.order,
											dataIndex: 'mv_order',
											width: 40,
											minWidth: 40,
											hidden: false,
											hideable: false,
											sortable: true,
											align: 'right'
										},
										{
											text: AgLang.use,
											dataIndex: 'mv_use',
											width: 30,
											minWidth: 30,
											hidden: true,
											hideable: true,
											sortable: true,
											renderer: function(value){
												if(value){
													return 'Yes';
												}else{
													return '<b style="color:red;">No</b>';
												}
											}
										},
										{
											text: AgLang.edit,
											dataIndex: 'mv_frozen',
											width: 60,
											minWidth: 60,
											hidden: false,
											hideable: false,
											sortable: true,
											renderer: function(value){
												if(value){
													return AgLang.not_editable_state;
												}else{
													return AgLang.editable;
												}
											}
										},
										{
											text: AgLang.publish,
											dataIndex: 'mv_publish',
											width: 50,
											minWidth: 50,
											hidden: false,
											hideable: false,
											sortable: true,
											renderer: function(value){
												if(value){
													return AgLang.publish_state;
												}else{
													return AgLang['private'];
												}
											}
										},
										{
											text: AgLang.renderer_version,
											dataIndex: 'mr_version',
											width: 93,
											minWidth: 93,
											hidden: true,
											hideable: true,
											sortable: true,
											renderer: function(value,metaData,record){
												return Ext.isEmpty(value) ? record.get('version_version')+'.'+record.get('version_revision')+'.'+Ext.Date.format(value,'ymdHi') : value;
											}
										},
										{
											text: AgLang.port,
											dataIndex: 'mv_port',
											width: 37,
											minWidth: 37,
											hidden: false,
											hideable: true,
											sortable: true,
											align: 'right'
										},
										{
											text: 'cb_id',
											dataIndex: 'cb_id',
											width: 37,
											minWidth: 37,
											hidden: true,
											hideable: true,
											sortable: true,
											align: 'right'
										},
										{
											text: 'mv_id',
											dataIndex: 'mv_id',
											width: 37,
											minWidth: 37,
											hidden: true,
											hideable: true,
											sortable: true,
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
									tbar: [{
										text: AgLang.add,
										iconCls: 'pallet_plus',
										listeners: {
											click: function(b){
												var gridpanel = b.up('gridpanel');
												var store = gridpanel.getStore();
												var max_version = store.max('fmt_version');
												var rec;
												if(max_version){
													rec = store.findRecord('fmt_version',max_version,0,false,false,true);
												}else{
													max_version = store.max('version');
													if(max_version) rec = store.findRecord('version',max_version,0,false,false,true);
												}
												if(rec){
//													var n = rec.copy();
//													Ext.data.Model.id(n);
//													n.beginEdit();
//													n.set('version',(n.data.version-0)+0.1);
//													n.set('mv_id',n.data.mv_id+1);
//													n.set('mr_id',1);
//													n.set('mv_publish',false);
//													n.endEdit(false,['version','mv_id','mr_id','mv_publish']);
//													store.insert(0,n);
													var ns = store.insert(0,[{}]);

													var max_mv_id = store.max('mv_id');

													var version = rec.get('version_version');
													var revision = rec.get('version_revision')+1;// ((rec.data.version.split('.',2))[1]-0)+1;
													var n = ns[0];//store.getAt(0);
													n.beginEdit();
													n.set('version.version',version);
													n.set('version.revision',revision);
													n.set('version',version+'.'+revision);
													n.set('mv_objects_set',version+'.'+revision);
													n.set('md_id',rec.data.md_id);
													n.set('mv_id',max_mv_id+1);
													n.set('prev_mv_id',rec.data.mv_id);
													n.set('mr_id',1);
													n.set('mv_frozen',false);
													n.set('mv_publish',false);
													n.set('mv_order',1);
													n.set('mv_port',0);
													n.set('mv_use',true);

													n.set('ci_id',rec.data.ci_id);
													n.set('ci_name',rec.data.ci_name);
													n.set('cb_id',rec.data.cb_id);
													n.set('cb_name',rec.data.cb_name);
													n.set('cb_comment',rec.data.cb_comment);
													n.set('cb_release',rec.data.cb_release);
													n.set('concept',rec.data.ci_id+'-'+rec.data.cb_id);

													n.set('info_takeover',true);

													n.set('version_version',version);
													n.set('version_revision',revision);
													n.set('fmt_version',Ext.String.leftPad(version+'',10,'0')+Ext.String.leftPad(revision+'',10,'0'));

													n.endEdit(false,['version','version.version','version.revision','md_id','mv_id','prev_mv_id','mr_id','mv_frozen','mv_publish','mv_order','mv_port','ci_id','ci_name','cb_id','cb_name','cb_comment','cb_release','concept','info_takeover','version_version','version_revision','fmt_version','mv_objects_set']);

//													Ext.each(store.getRange(1),function(r,i){
//														r.beginEdit();
//														r.set('mv_order',i+2);
//														r.endEdit(false,['mv_order']);
//													});

													gridpanel.getSelectionModel().select(0);

													b.setDisabled(true);
												}
											}
										},
									},'-','->',
									'-',{
										disabled: true,
										text: AgLang.thumbnail_background_part,
										tooltip: AgLang.thumbnail_background_part,
										iconCls: 'thumbnail_background_part',
										itemId: 'thumbnail-background-part',
										listeners: {
											click: function(b){
												var gridpanel = b.up('gridpanel');
												var store = gridpanel.getStore();
												var records = gridpanel.getSelectionModel().getSelection();
												if(records[0]){
													self.openThumbnailBackgroundPartSettingWindow({
														iconCls: b.iconCls,
														title: b.tooltip,
														animateTarget: b.el,
														record: records[0].copy()
													});
												}else{
													b.setDisabled(true);
												}
											}
										}
									},
									'-',{
										text: AgLang.segment_color,
										tooltip: AgLang.segment_color_mng,
										iconCls: 'color_pallet',
										listeners: {
											click: function(b){
												self.openSegmentColorSettingWindow({
													iconCls: b.iconCls,
													title: b.tooltip,
													animateTarget: b.el
												});
											}
										}
									},
									'-',{
										text: AgLang.renderer,
										tooltip: AgLang.renderer_mng,
										iconCls: 'gear-btn',
										listeners: {
											click: function(b){
												self.openRendererHostsMngWin({
													iconCls: b.iconCls,
													title: b.tooltip,
													animateTarget: b.el
												});
											}
										}
									}],
									listeners: {
										afterrender: function(grid,eOpts){
//											grid.getView().refresh();
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

											formPanel.up('window').getDockedItems('toolbar[dock="bottom"]')[0].down('button').setDisabled(records[0]?false:true);

											this.getDockedItems('toolbar[dock="top"]')[0].getComponent('thumbnail-background-part').setDisabled(records[0]?false:true);

											if(records[0]){
												var store = this.getStore();

												var version = form.findField('version.version');
//												version.setMinValue(parseInt(records[0].data.version));
												version.setMinValue(1);

												var revision = form.findField('version.revision');
												revision.setMinValue(0);

												form.loadRecord(records[0]);

												var readOnly = true;
												Ext.each(store.getNewRecords(),function(r,i,a){
													if(r.id != records[0].id) return true;
													readOnly = false;
													return false;
												});

												form.getFields().each(function(field,index,len){
													field.setDisabled(false);
													field.setReadOnly(readOnly);
												});

												form.findField('mv_use').setReadOnly(false);
												form.findField('mv_use').setDisabled(!readOnly);

												form.findField('mv_frozen').setReadOnly(false);
												form.findField('mv_frozen').setDisabled(!readOnly);

												form.findField('mv_publish').setReadOnly(false);
												form.findField('mv_publish').setDisabled(!readOnly);

												form.findField('mv_port').setReadOnly(false || form.findField('mv_publish').getValue());
												form.findField('mv_port').setDisabled(!readOnly);

												form.findField('version').setReadOnly(false || form.findField('mv_publish').getValue());
												form.findField('version').setDisabled(!readOnly);

												form.findField('mv_objects_set').setReadOnly(false || form.findField('mv_publish').getValue());
												form.findField('mv_objects_set').setDisabled(!readOnly);

												form.findField('mv_comment').setReadOnly(false || form.findField('mv_publish').getValue());
												form.findField('mv_comment').setDisabled(!readOnly);

//												form.findField('mv_order').setReadOnly(false || form.findField('mv_publish').getValue());
//												form.findField('mv_order').setDisabled(!readOnly);
												form.findField('mv_order').setReadOnly(false);
												form.findField('mv_order').setDisabled(false);

												if(!readOnly){
													formPanel.getDockedItems('toolbar[dock="bottom"]')[0].down('button').setDisabled(false);

												}
												formPanel.up('window').getDockedItems('toolbar[dock="bottom"]')[0].down('button').setDisabled(!readOnly || !form.findField('mv_frozen').getValue());

												form.findField('info_takeover').setDisabled(readOnly);
												form.findField('prev_mv_id').setDisabled(readOnly);
												if(!readOnly){
													var store = records[0].store;
													var md_id = records[0].data.md_id;
													var mv_id = records[0].data.prev_mv_id;
													var idx = store.findBy(function(r,id){
														if(r.data.md_id==md_id && r.data.mv_id==mv_id) return true;
														return false;
													});
													if(idx>=0){
														r = store.getAt(idx);
														if(r) form.findField('prev_mv_id').setValue(r.data.value);
													}
												}

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
									height: 266,
									xtype: 'form',
									bodyPadding: 10,
									defaults: {
										labelAlign: 'right',
										labelWidth: 60
									},
									items: [{
										hidden: true,
										xtype: 'button',
										text: '新規追加'
									},{
										hidden: true,
										xtype: 'displayfield',
										fieldLabel: AgLang.model,
										name: 'md_name_e'
									},{
										xtype: 'fieldcontainer',
										layout: {
											type: 'hbox',
											align: 'top',
											pack: 'start',
											defaultMargins: {top: 0, right: 4, bottom: 0, left: 0}
										},
										defaults: {
											labelAlign: 'right',
											labelWidth: 50
										},
										items: [{
											disabled: true,
											xtype: 'numberfield',
											fieldLabel: AgLang.version,
											name: 'version.version',
											allowBlank: false,
											allowDecimals: false,
											selectOnFocus: true,
											width: 100,
											listeners: {
												change: function(field,newValue,oldValue,eOpts){
													var gridpanel = field.up('window').down('gridpanel');
													var rec = gridpanel.getSelectionModel().getLastSelected();
													var name = field.getName();
													rec.beginEdit();
													rec.set(name,newValue);
													var version = newValue+'.'+rec.get('version.revision');
													rec.set('version',version);
													rec.set('mv_objects_set',version);
													rec.endEdit(false,[name,'version','mv_objects_set']);

													var formPanel = field.up('form');
													var form = formPanel.getForm();
													form.findField('version').setValue(version);
													form.findField('mv_objects_set').setValue(version);

													setDisabledSaveButton(field);
												},
												specialkey: function(field, e, eOpts){
													e.stopPropagation();
												}
											}
										},{
											disabled: true,
											xtype: 'numberfield',
											fieldLabel: AgLang.revision,
											name: 'version.revision',
											allowBlank: false,
											allowDecimals: false,
											selectOnFocus: true,
											width: 100,
											validator: function(v){
												return true;
												var field = this;
												var gridpanel = field.up('window').down('gridpanel');
												var rec = gridpanel.getSelectionModel().getLastSelected();
												if(Ext.isEmpty(rec.data.prev_mv_id)) return true;

												var store = gridpanel.getStore();
												var prev_rec = store.findRecord('mv_id',rec.data.prev_mv_id,0,false,false,true);
												if(Ext.isEmpty(prev_rec)) return true;

												var prev_version = parseInt(prev_rec.data.version);
												var prev_revision = (prev_rec.data.version.split('.',2))[1]-0;

												if(prev_version==rec.get('version.version') && prev_revision>=v) return false;

												return true;
											},
											listeners: {
												change: function(field,newValue,oldValue,eOpts){
													var gridpanel = field.up('window').down('gridpanel');
													var rec = gridpanel.getSelectionModel().getLastSelected();
													var name = field.getName();
													rec.beginEdit();
													rec.set(name,newValue);
													var version = rec.get('version.version')+'.'+newValue;
													rec.set('version',version);
													rec.set('mv_objects_set',version);
													rec.endEdit(false,[name,'version','mv_objects_set']);

													var formPanel = field.up('form');
													var form = formPanel.getForm();
													form.findField('version').setValue(version);
													form.findField('mv_objects_set').setValue(version);

													setDisabledSaveButton(field);
												},
												specialkey: function(field, e, eOpts){
													e.stopPropagation();
												}
											}
										},{
											disabled: true,
											xtype: 'textfield',
											fieldLabel: AgLang.version_signage,
											labelWidth: 74,
											name: 'version',
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
													rec.set('mv_objects_set',newValue);
													rec.endEdit(false,[name,'mv_objects_set']);

													var formPanel = field.up('form');
													var form = formPanel.getForm();
													form.findField('mv_objects_set').setValue(newValue);

													setDisabledSaveButton(field);
												},
												specialkey: function(field, e, eOpts){
													e.stopPropagation();
												}
											}
										},{
											disabled: true,
											xtype: 'textfield',
											fieldLabel: AgLang.objects_set_signage,
											labelWidth: 87,
											name: 'mv_objects_set',
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
											name: 'mv_order',
											allowBlank: false,
											selectOnFocus: true,
											width: 100,
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
										}]
									},{
										disabled: true,
										fieldLabel: 'Concept',
										name: 'concept',
										anchor: '100%',
										xtype: 'combobox',
										editable: true,
										selectOnFocus: true,
										matchFieldWidth: true,
										queryMode: 'local',
										displayField: 'display',
										valueField: 'value',
										store: 'conceptStore',
										listeners: {
											afterrender: function(field, eOpt){
												field.setEditable(false);
											},
											select: function(field, records, eOpts){
												var record = records[0];
												var gridpanel = field.up('window').down('gridpanel');
												var rec = gridpanel.getSelectionModel().getLastSelected();
												var name = field.getName();
												rec.beginEdit();
												rec.set(name,record.data.ci_id+'-'+record.data.cb_id);
												rec.set('ci_id',record.data.ci_id);
												rec.set('ci_name',record.data.ci_name);
												rec.set('cb_id',record.data.cb_id);
												rec.set('cb_name',record.data.cb_name);
												rec.set('cb_comment',record.data.cb_comment);
												rec.set('cb_release',record.data.cb_release);
												rec.endEdit(false,[name,'ci_id','ci_name','cb_id','cb_name','cb_comment','cb_release']);

												setDisabledSaveButton(field);
											}
										}
									},{
										disabled: true,
										xtype: 'checkboxfield',
										fieldLabel: AgLang.use,
										boxLabel: 'Yes',
										name: 'mv_use',
										listeners: {
											change: function(field,newValue,oldValue,eOpts){
												var gridpanel = field.up('window').down('gridpanel');
												var rec = gridpanel.getSelectionModel().getLastSelected();
												var name = field.getName();
												rec.beginEdit();
												rec.set(name,newValue);
												rec.endEdit(false,[name]);
/*
												var formPanel = field.up('form');
												if(!newValue){
													var form = formPanel.getForm();
													if(form.findField('mv_publish').getValue()){
														form.findField('mv_publish').setValue(false);
													}
												}
*/

												setDisabledSaveButton(field);
											}
										}
									},{
										disabled: true,
										xtype: 'checkboxfield',
										fieldLabel: AgLang.edit,
										boxLabel: AgLang.not_editable_label,
										name: 'mv_frozen',
										listeners: {
											change: function(field,newValue,oldValue,eOpts){
												var gridpanel = field.up('window').down('gridpanel');
												var rec = gridpanel.getSelectionModel().getLastSelected();
												var name = field.getName();
												rec.beginEdit();
												rec.set(name,newValue);
												rec.endEdit(false,[name]);

												var formPanel = field.up('form');
												if(!newValue){
													var form = formPanel.getForm();
													if(form.findField('mv_publish').getValue()){
														form.findField('mv_publish').setValue(false);
													}
												}
//												formPanel.up('window').getDockedItems('toolbar[dock="bottom"]')[0].down('button').setDisabled(!newValue);

												setDisabledSaveButton(field);
											}
										}
									},{
										disabled: true,
										xtype: 'checkboxfield',
										fieldLabel: AgLang.publish,
										boxLabel: AgLang.publish_label,
										name: 'mv_publish',
										listeners: {
											change: function(field,newValue,oldValue,eOpts){
												var gridpanel = field.up('window').down('gridpanel');
												var rec = gridpanel.getSelectionModel().getLastSelected();
												var name = field.getName();
												rec.beginEdit();
												rec.set(name,newValue);
												rec.endEdit(false,[name]);

												var formPanel = field.up('form');
												var form = formPanel.getForm();
												form.findField('mv_port').setReadOnly(newValue);
												form.findField('version').setReadOnly(newValue);
												form.findField('mv_objects_set').setReadOnly(newValue);
												form.findField('mv_comment').setReadOnly(newValue);

												if(newValue){
													if(!form.findField('mv_frozen').getValue()){
														form.findField('mv_frozen').setValue(true);
													}
												}

												setDisabledSaveButton(field);
											}
										}
									},{
										disabled: true,
										xtype: 'numberfield',
										fieldLabel: AgLang.port,
										name: 'mv_port',
										allowDecimals: false,
										minValue: 1,
										maxValue: 65535,
										maxLength: 5,
										selectOnFocus: true,
										width: 120,
										validator: function(v){
											if(Ext.isEmpty(v)){
												var field = this;
												var formPanel = field.up('form');
												var form = formPanel.getForm();
												if(form.findField('mv_publish').getValue()) return AgLang.error_port;
											}
											return true;
										},
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
										xtype: 'textfield',
										fieldLabel: AgLang.comment,
										name: 'mv_comment',
										selectOnFocus: true,
										anchor: '100%',
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
										xtype: 'label',
										html: '<hr size=1 />'
									},{
										xtype: 'fieldcontainer',
										layout: {
											type: 'hbox',
											align: 'top',
											pack: 'start',
											defaultMargins: {top: 0, right: 4, bottom: 0, left: 0}
										},
										defaults: {
											labelAlign: 'right',
											labelWidth: 50
										},
										items: [{
											disabled: true,
											xtype: 'checkboxfield',
											boxLabel: '対応情報を引継ぐ',
											name: 'info_takeover',
											listeners: {
												change: function(field,newValue,oldValue,eOpts){
													var formPanel = field.up('form');
													formPanel.getDockedItems('toolbar[dock="bottom"]')[0].down('button').setDisabled(!formPanel.getForm().isValid());

													var gridpanel = field.up('window').down('gridpanel');
													var rec = gridpanel.getSelectionModel().getLastSelected();
													var name = field.getName();
													rec.beginEdit();
													rec.set(name,newValue);
													rec.endEdit(false,[name]);
												}
											}
										},{
											disabled: true,
											hiddenLabel: true,
											name: 'prev_mv_id',
//											width: 184,
											width: 250,
											xtype: 'combobox',
											editable: false,
											matchFieldWidth: false,
											listConfig: {
//												minWidth: 167,
//												width: 167
												width: 199
											},
											queryMode: 'local',
											displayField: 'display',
											valueField: 'value',
											store: 'datasetMngStore',
											listeners: {
												afterrender: function(field, eOpt){
													field.setEditable(false);
												},
												select: function(field, records, eOpts){
													var record = records[0];
													var gridpanel = field.up('window').down('gridpanel');
													var rec = gridpanel.getSelectionModel().getLastSelected();
													var name = field.getName();
													rec.beginEdit();
													rec.set(name,record.data.mv_id);
													rec.endEdit(false,[name]);

													setDisabledSaveButton(field);
												}
											}
										}]
									}],
									buttons: [{
										disabled: true,
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
															var versionCombobox = Ext.getCmp('version-combobox');
															var value = versionCombobox.getValue();
															versionCombobox.getStore().loadPage(1,{
																callback: function(){
																}
															});
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

												var btn = gridpanel.getDockedItems('toolbar[dock="top"]')[0].down('button');
												if(btn.isDisabled() && newRecords.length>0) btn.setDisabled(false);
											}
										}
									}]
								}],
								buttons: [{
									disabled: true,
									text: AgLang['export']+' ('+AgLang.renderer+' files)',
									itemId: 'export',
									listeners: {
										click: function(b){

											b.setDisabled(true);

											var p = self.getExtraParams({current_datas:0});

											var gridpanel = b.up('window').down('gridpanel');
											var rec = gridpanel.getSelectionModel().getLastSelected();

											p = Ext.apply({},rec.data,p);
//											console.log(p);
//											return;


											p.cmd = 'export-tree-all';
//											window.location.href = "get-info.cgi?"+ Ext.Object.toQueryString(p);

											Ext.Ajax.abort();
											Ext.Ajax.request({
												url: 'get-info.cgi',
												method: 'POST',
												params: p,
												callback: function(options,success,response){
													if(!success){
														b.setDisabled(false);
														return;
													}
													try{json = Ext.decode(response.responseText)}catch(e){};
													if(Ext.isEmpty(json) || Ext.isEmpty(json.success) || json.success==false){
														b.setDisabled(false);
														return;
													}

													var _progress = Ext.Msg.show({
														closable : false,
														modal    : true,
														msg      : json.progress && json.progress.msg ? json.progress.msg : b.text+'...',
														progress : true,
														title    : b.text+'...'
													});

													if(Ext.isEmpty(self._TaskRunner)) self._TaskRunner = new Ext.util.TaskRunner();
													var task = self._TaskRunner.newTask({
														run: function () {
															task.stop();
															p.cmd = 'export-tree-all-progress';
															p.sessionID = json.sessionID;
															Ext.Ajax.abort();
															Ext.Ajax.request({
																url: 'get-info.cgi',
																method: 'POST',
																params: p,
																callback: function(options,success,response){
																	try{json = Ext.decode(response.responseText)}catch(e){};
																	if(Ext.isEmpty(json) || Ext.isEmpty(json.success) || json.success==false){
																		b.setDisabled(false);
																		_progress.close();
//																		console.log("_progress.close()")
																		task.stop();
																		return;
																	}
																	if(json.progress && Ext.isString(json.progress.msg) && json.progress.msg.toLowerCase()=='end'){
																		b.setDisabled(false);
																		task.stop();
																		_progress.close();
//																		console.log("_progress.close()")

																		p.cmd = 'export-tree-all-download';
																		p.sessionID = json.sessionID;
																		window.location.href = "get-info.cgi?"+ Ext.Object.toQueryString(p);

																	}else if(json.progress && Ext.isString(json.progress.msg) && json.progress.msg.toLowerCase().indexOf('error')==0){
																		b.setDisabled(false);
																		task.stop();
																		_progress.close();
//																		console.log("_progress.close()")

																		p.cmd = 'export-tree-all-cancel';
																		p.sessionID = json.sessionID;
																		Ext.Ajax.abort();
																		Ext.Ajax.request({
																			url: 'get-info.cgi',
																			method: 'POST',
																			params: p
																		});

																		Ext.defer(function(){
																			Ext.Msg.show({
																				title: b.text,
																				msg: json.progress.msg,
																				buttons: Ext.Msg.OK,
																				icon: Ext.Msg.ERROR
																			});
																		},100);

																		return;

																	}else{
//																		_progress.updateProgress(json.progress.value,json.progress.value,json.progress.msg);
																		_progress.updateProgress(json.progress.value,Math.floor(json.progress.value*100)+'%',json.progress.msg);
//																		console.log("["+json.progress.value+"]["+json.progress.msg+"]")
																		task.start();
																	}
																}
															});
														},
														interval: 3000
													});
													task.start();


												}
											});
										}
									}
								},'->',{
									text: AgLang.close,
									listeners: {
										click: function(b){
											b.up('window').close();
										}
									}
								}],
								listeners: {
									show: function(comp){
										comp.down('gridpanel').getStore().loadPage(1);
									},
									beforeclose: function(comp,eOpts){
										comp.down('gridpanel').getStore().loadPage(1);
									}
								}
							});



};
