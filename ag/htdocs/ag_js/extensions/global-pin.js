///////////////////////////////////////////////////////////////////////////////
//
///////////////////////////////////////////////////////////////////////////////
window.ag_extensions = window.ag_extensions || {};
ag_extensions.global_pin = ag_extensions.global_pin || {};
///////////////////////////////////////////////////////////////////////////////
//初期化
///////////////////////////////////////////////////////////////////////////////
ag_extensions.global_pin._init = function(){
	var self = this;

//id="ag-comment-tabpanel"
	self.__parentPanel_id = 'anatomography-pin-grid-panel';
	self.__parentPanel = Ext.getCmp(self.__parentPanel_id);
//	console.log("ag_extensions.global_pin._init():"+self.__parentPanel);
	if(self.__parentPanel){
		if(self.__parentPanel.rendered){
			self._initUI();
		}else{
			self.__parentPanel.on({
				'render': function(){
					self._initUI();
				},
				buffer: 100,
				single: true
			});
		}
	}else{
		self.__initTask = {
			run: function(){
				self.__parentPanel = Ext.getCmp(self.__parentPanel_id);
				if(!self.__parentPanel) return;
				self.__initTaskRunner.stop(self.__initTask);
				if(self.__parentPanel.rendered){
					self._initUI();
				}else{
					self.__parentPanel.on({
						'render': function(){
							self._initUI();
						},
						buffer: 100,
						single: true
					});
				}
			},
			interval: 1000
		}
		self.__initTaskRunner = new Ext.util.TaskRunner();
		self.__initTaskRunner.start(self.__initTask);
	}
};
///////////////////////////////////////////////////////////////////////////////
//UI初期化
///////////////////////////////////////////////////////////////////////////////
ag_extensions.global_pin._initUI = function(){
	var self = this;
	try{
//		console.log("ag_extensions.global_pin._initUI():"+self.__parentPanel);
//		console.log("ag_extensions.global_pin._initUI():"+self.__parentPanel.getXType());
//		console.log("ag_extensions.global_pin._initUI():"+self.__parentPanel.getTopToolbar());
//		self.__panel = new Ext.Panel({
//			xtype: 'panel',
//			title: 'Global Pin Mng',
//		});
//		self.__parentPanel.add(self.__panel);

		var ttbar = self.__parentPanel.getTopToolbar();
		if(ttbar){

			self.__convertMenuItem = new Ext.menu.Item({
				text: 'to Global ID',
				tooltip: 'convert to Global Pin',
				iconCls: 'convert-pin-item',
				disabled: true,
				handler: function(){
					var b = this;
					self.convLocalPin2GlobalPin({
						title: b.tooltip,
						iconCls: b.iconCls,
						animateTarget: b.el
					});
				}
			});
			self.__findGroupItem = new Ext.menu.Item({
				text: 'Find Pin Group',
				iconCls: 'find-group-item',
				handler: function(){
					var b = this;
					self.findPinGroup({
						title: b.text,
						iconCls: b.iconCls,
						animateTarget: b.el
					},function(records){
						if(Ext.isEmpty(records) || records.length == 0) return;
						var no = ag_comment_store.getCount();
						var pinRecord = Ext.data.Record.create(ag_comment_store_fields);
						var arr = [];
						Ext.each(records,function(r,i,a){
							var rec = new pinRecord(Ext.apply({},r.data));
							rec.beginEdit();
							rec.set('no',++no);
							rec.set('color',r.get('PinGroupPinColor'));
							rec.set('comment',r.get('PinGroupDescription'));
							rec.commit(true);
							rec.endEdit();
							arr.push(rec);
						});
						if(arr.length>0){
							ag_comment_store.add(arr);
							self.__parentPanel.getView().refresh();
							updateAnatomo();
						}
					});
				}
			});
			self.__addGroupMenuItem = new Ext.menu.Item({
				text: 'Create Pin Group',
				iconCls: 'add-group-item',
				disabled: true,
				handler: function(){
					var b = this;
					self.addPinGroup({
						title: b.text,
						iconCls: b.iconCls,
						animateTarget: b.el
					});
				}
			});
			self.__addPinMenuItem = new Ext.menu.Item({
				text: 'Find Pin',
				iconCls: 'find-pin-item',
				disabled: false,
				handler: function(){
					var b = this;
					self.findPin({
						title: b.text,
						iconCls: b.iconCls,
						animateTarget: b.el
					},function(records){
						if(Ext.isEmpty(records) || records.length == 0) return;
						var no = ag_comment_store.getCount();
						var pinRecord = Ext.data.Record.create(ag_comment_store_fields);
						var arr = [];
						Ext.each(records,function(r,i,a){
							var rec = new pinRecord(Ext.apply({},r.data));
							rec.beginEdit();
							rec.set('no',++no);
							rec.set('oid',r.get('PinPartID'));
							rec.set('organ',r.get('PinPartName'));
							rec.set('x3d',r.get('PinX'));
							rec.set('y3d',r.get('PinY'));
							rec.set('z3d',r.get('PinZ'));
							rec.set('avx3d',r.get('PinArrowVectorX'));
							rec.set('avy3d',r.get('PinArrowVectorY'));
							rec.set('avz3d',r.get('PinArrowVectorZ'));
							rec.set('uvx3d',r.get('PinUpVectorX'));
							rec.set('uvy3d',r.get('PinUpVectorY'));
							rec.set('uvz3d',r.get('PinUpVectorZ'));
							rec.set('color',r.get('PinColor'));
							rec.set('comment',r.get('PinDescription'));
							rec.set('coord',r.get('PinCoordinateSystemName'));
							rec.commit(true);
							rec.endEdit();
							arr.push(rec);
						});
						if(arr.length>0){
							ag_comment_store.add(arr);
							self.__parentPanel.getView().refresh();
							updateAnatomo();
						}
					});
				}
			});

			self.__parentPanel.getSelectionModel().on({
				selectionchange: function(selModel){
					self.__convertMenuItem.setDisabled(true);
					if(selModel.getCount()==0) return;
					Ext.each(selModel.getSelections(),function(r,i,a){
						var no = r.get('no');
						if(Ext.isEmpty(no)) return true;
						var PinID = r.get('PinID');
						var PinGroupID = r.get('PinGroupID');
						if(Ext.isEmpty(PinID) && Ext.isEmpty(PinGroupID)){
							self.__convertMenuItem.setDisabled(false);
							return false;
						}else{
							return true;
						}
					});
				},
				scope: self
			});

			self.__parentPanel.on({
				rowdblclick: function(e){
//					console.log('dblclick()');
					var selModel = self.__parentPanel.getSelectionModel();
					if(selModel.getCount()!=1) return;
					var record = selModel.getSelected();
					if(Ext.isEmpty(record)) return;
					if(self._isGlobalPin(record)){
						self._editGlobalPin({},record);
					}else if(self._isGlobalPinGroup(record)){
						self._editGlobalPinGroup({},record);
					}
				},
				scope: self
			});

			self.__tbCheckbox = new Ext.form.Checkbox({
				checked: true,
				inputValue: true,
				listeners: {
					check: function(filed,checked){
						self.__tbBtn.setDisabled(!checked);
					},
					scope: self
				}
			});

			self.__parentPanel.getStore().on({
				add: function(store,recs,index){
					if(!self.__tbCheckbox.getValue()) return;
//					console.log("add():["+recs.length+"]");
					var records = [];
					Ext.each(recs,function(r,i,a){
						var no = r.get('no');
						if(Ext.isEmpty(no)) return true;
						var PinID = r.get('PinID');
						var PinGroupID = r.get('PinGroupID');
						if(Ext.isEmpty(PinID) && Ext.isEmpty(PinGroupID)) records.push(r);
					});
					if(Ext.isEmpty(records)) return;
					ag_extensions.global_pin._convLocalPin2GlobalPin({},records);
				},
				update: function(store,record,operation){
//					console.log("update():["+operation+"]");
//					console.log(Ext.apply({},record.data));
//					if(operation!=Ext.data.Record.COMMIT) return;
					return;
//					console.log(record);
					if(self._isGlobalPin(record)){
						if(record.data.color!=record.data.PinColor || record.data.comment!=record.data.PinDescription){
							record.beginEdit();
							record.set('PinColor',record.data.color);
							record.set('PinDescription',record.data.comment);
							record.commit(false);
						}
					}else if(self._isGlobalPinGroup(record)){
						if(record.data.color!=record.data.PinGroupPinColor || record.data.comment!=record.data.PinGroupDescription){
							record.beginEdit();
							record.set('PinGroupPinColor',record.data.color);
							record.set('PinGroupDescription',record.data.comment);
							record.commit(false);
						}
					}
				}
			});

			ttbar.addSeparator();
			ttbar.add(self.__tbCheckbox);
			self.__tbBtn = ttbar.addButton({
				text: 'Global Pin',
				menu: {
					items: [
						self.__convertMenuItem,
						self.__addPinMenuItem,
						'-',
						self.__findGroupItem,
						'-',
						self.__addGroupMenuItem
					]
				}
			});
			ag_extensions.auth.auth(function(auth){
				self.__auth = auth;
				self.__addGroupMenuItem.setDisabled(!auth);
			});
		}
	}catch(e){
		console.error(e);
	}
};
///////////////////////////////////////////////////////////////////////////////
// ピン用ストアのフィールド定義
///////////////////////////////////////////////////////////////////////////////
ag_extensions.global_pin.store_field_pin = function(){
	return [
		{name:'PinID', type:'string'},
		{name:'PinX', type:'float'},
		{name:'PinY', type:'float'},
		{name:'PinZ', type:'float'},
		{name:'PinArrowVectorX', type:'float'},
		{name:'PinArrowVectorY', type:'float'},
		{name:'PinArrowVectorZ', type:'float'},
		{name:'PinUpVectorX', type:'float'},
		{name:'PinUpVectorY', type:'float'},
		{name:'PinUpVectorZ', type:'float'},
		{name:'PinColor', type:'string'},
		{name:'PinDescriptionColor', type:'string'},
		{name:'PinNumberDrawFlag', type:'boolean'},
		{name:'PinDescriptionDrawFlag', type:'boolean'},
		{name:'PinShape', type:'string'},
		{name:'PinSize', type:'float'},
		{name:'PinCoordinateSystemName', type:'string'},
		{name:'PinPartID', type:'string'},
		{name:'PinPartName', type:'string'},
		{name:'PinDescription', type:'string'},
		{name:'Version', type:'string'},
		{name:'PinValue', type:'string'},
		{name:'PinRadius', type:'float'}
	];
};
///////////////////////////////////////////////////////////////////////////////
// ピングループ用ストアのフィールド定義
///////////////////////////////////////////////////////////////////////////////
ag_extensions.global_pin.store_field_pin_group = function(){
	return [
		{name:'PinGroupID', type:'string'},
		{name:'PinGroupPinColor', type:'string'},
		{name:'PinGroupDescription', type:'string'},
		{name:'PinGroupPinDescriptionColor', type:'string'},
		{name:'PinGroupPinDescriptionDrawFlag', type:'boolean'},
		{name:'PinGroupPinNumberDrawFlag', type:'boolean'},
		{name:'PinGroupPinShape', type:'string'},
		{name:'PinGroupPinSize', type:'float'},
		{name:'PinGroupValue', type:'string'},
		{name:'PinGroupApiAdding', type:'boolean'},
		{name:'PinGroupApiExclusion', type:'boolean'},
		{name:'PinGroupApiReference', type:'boolean'},
		{name:'PinGroupSearch', type:'boolean'},
		{name:'PinCount', type:'int'}
	];
};
///////////////////////////////////////////////////////////////////////////////
// ピン用グリッドのカラム定義
///////////////////////////////////////////////////////////////////////////////
ag_extensions.global_pin._grid_columns_pin_renderer = function(value,metadata,record,rowIndex,colIndex,store){
	metadata.attr = 'style="white-space:normal;"';
	return Ext.util.Format.nl2br(value);
};
///////////////////////////////////////////////////////////////////////////////
// ピン用グリッドのカラム定義
///////////////////////////////////////////////////////////////////////////////
ag_extensions.global_pin.grid_columns_pin = function(){
	var self = this;
	var width = 96;
	return [
		{dataIndex:'PinID',header:'PinID',width:60},
		{dataIndex:'PinPartID',header:'PartID',width:68},
		{dataIndex:'PinPartName',header:'PartName',width:width,renderer:self._grid_columns_pin_renderer},
		{dataIndex:'PinDescription',header:'Description',width:width,renderer:self._grid_columns_pin_renderer},
		{dataIndex:'PinValue',header:'Value',width:width,renderer:self._grid_columns_pin_renderer}
	];
};
///////////////////////////////////////////////////////////////////////////////
// ピングループ用グリッドのカラム定義
///////////////////////////////////////////////////////////////////////////////
ag_extensions.global_pin.grid_columns_pin_group = function(){
	var self = this;
	var width = 158;
	return [
		{dataIndex:'PinGroupID',header:'PinGroupID',width:60},
		{dataIndex:'PinGroupDescription',header:'Description',width:width,renderer:self._grid_columns_pin_renderer},
		{dataIndex:'PinGroupValue',header:'Value',width:width,renderer:self._grid_columns_pin_renderer},
		{dataIndex:'PinCount',header:'#',width:40,align:'right'}
	];
};
///////////////////////////////////////////////////////////////////////////////
// 既存のピンをグローバルピンに変換する関数
///////////////////////////////////////////////////////////////////////////////
ag_extensions.global_pin.convLocalPin2GlobalPin = function(config){
	var self = this;
	config = Ext.apply({},config||{},{
		title: 'convert'
	});
//	console.log('ag_extensions.global_pin.convLocalPin2GlobalPin()');

	var records = [];
	Ext.each(self.__parentPanel.getSelectionModel().getSelections(),function(r,i,a){
		var no = r.get('no');
		if(Ext.isEmpty(no)) return true;
		var PinID = r.get('PinID');
		var PinGroupID = r.get('PinGroupID');
		if(Ext.isEmpty(PinID) && Ext.isEmpty(PinGroupID)) records.push(r);
	});
	if(Ext.isEmpty(records)) return;

	if(!self.__auth){
		Ext.Msg.show({
			title: config.title,
			msg: 'Because you are not logged in, you can not change the attributes of the pin after the conversion. Would you like?',
			buttons: Ext.Msg.OKCANCEL,
			animEl: config.animateTarget,
			icon: Ext.MessageBox.QUESTION,
			fn: function(buttonId){
				if(buttonId!='ok') return;
				self._convLocalPin2GlobalPin(config,records);
			}
		});
	}else{
		self._convLocalPin2GlobalPin.defer(100,self,[config,records]);
	}
};
///////////////////////////////////////////////////////////////////////////////
// 既存のピンをグローバルピンに変換する関数
///////////////////////////////////////////////////////////////////////////////
ag_extensions.global_pin._convLocalPin2GlobalPin = function(config,records){
	var self = this;
	try{
		var url = cgipath.globalPin.pin.adding;
		var arr = [];
		var def = {
			PinNumberDrawFlag : Ext.getCmp('anatomo_pin_number_draw_check').getValue(),
			PinDescriptionDrawFlag : Ext.getCmp('anatomo_pin_description_draw_check').getValue(),
			PinShape : Ext.getCmp('anatomo_pin_shape_combo').getValue(),
			Version : Ext.getCmp('bp3d-version-combo').getValue(),
			PinValue : null //この時点では、未設定
		};
		Ext.each(records,function(r,i,a){
			var obj = Ext.apply({},r.data,def);
			var hash = ag_extensions.toJSON.fromRecordPin2HashPin(obj,true);
			arr.push(hash);
		});
		if(Ext.isEmpty(arr)) return;
		Ext.Ajax.request({
			url: url,
			method: 'POST',
			params: {json: Ext.util.JSON.encode(arr)},
			callback: function(options,success,response){
				if(success){
					var json = Ext.util.JSON.decode(response.responseText);
					if(json && json.success){
						if(json.Pin.length == records.length){
							Ext.each(json.Pin,function(pin,i,a){
								var r = records[i];
								r.beginEdit();
								for(var key in pin){
									r.set(key,pin[key]);
								}
								r.commit(true);
								r.endEdit();
							});
							self.__parentPanel.getView().refresh();
							updateAnatomo();
						}
					}
				}
			}
		});
	}catch(e){
		if(window.console) window.console.error(e);
	}
};
///////////////////////////////////////////////////////////////////////////////
// ピン情報更新関数
///////////////////////////////////////////////////////////////////////////////
ag_extensions.global_pin._updateGlobalPin = function(record){
	var self = this;
//	console.log('ag_extensions.global_pin._updateGlobalPin()');
	var url = cgipath.globalPin.pin.update;
	var arr = [Ext.apply({},record.data)];
//	console.log(arr);
	if(Ext.isEmpty(arr)) return;

	Ext.Ajax.request({
		url: url,
		method: 'POST',
		params: {json: Ext.util.JSON.encode(arr)},
		callback: function(options,success,response){
//			console.log(success);
			if(success){
//				console.log(response);
				var json = Ext.util.JSON.decode(response.responseText);
				if(json && json.success){
					if(json.Pin.length==1){
//						console.log(json.Pin);
						Ext.each(json.Pin,function(pin,i,a){
							var r = record;
							r.beginEdit();
							for(var key in pin){
								r.set(key,pin[key]);
							}
							r.commit(true);
							r.endEdit();
						});
						self.__parentPanel.getView().refresh();
						updateAnatomo();
					}
				}
			}
		}
	});
};
///////////////////////////////////////////////////////////////////////////////
// グリッド画面用ツールバー
///////////////////////////////////////////////////////////////////////////////
ag_extensions.global_pin._PagingToolbar = function(config){
	var self = this;
	config = Ext.apply({},config||{},{
		pageSize    : 20,
		displayInfo : false,
		displayMsg  : '',
		emptyMsg    : '',
		hideMode    : 'offsets',
		hideParent  : true
	});
	return new Ext.PagingToolbar({
		pageSize: config.pageSize,
		store: config.store,
		displayInfo: config.displayInfo,
		displayMsg: config.displayMsg,
		emptyMsg: config.emptyMsg,
		hideMode: config.hideMode,
		hideParent: config.hideParent,
		listeners: {
			render: function(comp){
//				return;
				comp.addFill();
				comp.addSeparator();
				comp.add(
					new Ext.form.ComboBox({
						allowBlank: false,
						width: 50,
						disableKeyFilter: true,
						displayField: 'value',
						valueTextArea: 'value',
						forceSelection: false,
						editable: true,
						hideLabel: true,
						mode: 'local',
						selectOnFocus: true,
						triggerAction: 'all',
						value: comp.pageSize,
						store: new Ext.data.SimpleStore({
							fields:['value'],
							data:[
								[10],
								[20],
								[30],
								[50],
								[80],
								[100],
								[150],
								[200]
							]
						}),
						listeners: {
							change: function(field,newValue,oldValue){
								if(Ext.isEmpty(newValue)) return;
								comp.pageSize = newValue-0;
								comp.changePage(1);
							},
							select: function(field,record,index){
								field.fireEvent('change',field,field.getValue());
							},
							specialkey: function(field,e){
								if(e.getKey()==e.ENTER){
									field.fireEvent('change',field,field.getValue());
								}
							}
						}
					})
				);
			}
		}
	});
};
///////////////////////////////////////////////////////////////////////////////
// ピンの検索画面
///////////////////////////////////////////////////////////////////////////////
ag_extensions.global_pin.findPin = function(config,aCB){
	var self = this;
	config = Ext.apply({},config||{},{
		title: 'find Pin',
		iconCls: 'find-item',
		modal: true,
		width: 650,
		height: 400,
		plain: false,
		resizable: false
	});

	var pinGridPanelStore = new Ext.data.JsonStore({
		url: cgipath.globalPin.pin.search,
		id: 'PinID',
		root: 'Pin',
		successProperty: 'success',
		totalProperty: 'total',
		remoteSort: true,
		sortInfo: {field: 'gp_entry', direction: 'ASC'},
		fields: self.store_field_pin()
	});

	var pinGridPanelBBar = self._PagingToolbar({pageSize:20,store:pinGridPanelStore});

	var pinGridPanel = new Ext.grid.GridPanel({
		region: 'center',
//		title: 'Pin',
//		iconCls: 'pin-item',
		store: pinGridPanelStore,
		columns: self.grid_columns_pin(),
		stripeRows: true,
		columnLines: true,
		selModel: new Ext.grid.RowSelectionModel({
			listeners: {
				selectionchange: function(selModel){
				}
			}
		}),
		bbar: pinGridPanelBBar
	});

//	console.log(Ext.getCmp('bp3d-version-combo'));
	var dataVersionCombo = Ext.getCmp('bp3d-version-combo');
	var comboSize = dataVersionCombo.getSize();
	comboSize.width += 73;

	var version_datas = [['All','']];
	Ext.each(dataVersionCombo.getStore().getRange(),function(r,i,a){
		version_datas.push([r.get(dataVersionCombo.displayField),r.get(dataVersionCombo.valueField)]);
	});

	var pinFormPanel = new Ext.form.FormPanel({
		region: 'west',
		width: 300,
		bodyStyle: 'padding:5px;',
		labelAlign: 'right',
		labelWidth: 32,
		defaultType: 'fieldset',
		items: [{
			xtype: 'textfield',
			name: 'PinID',
			fieldLabel: 'PinID',
			anchor: '100%'
		},{
			title: 'Keyword',
			autoHeight: true,
			defaultType: 'textfield',
			labelWidth: 64,
			items: [{
				name: 'PinPartID',
				fieldLabel: 'PartID',
				anchor: '100%'
			},{
				name: 'PinPartName',
				fieldLabel: 'PartName',
				anchor: '100%'
			},{
				name: 'PinDescription',
				fieldLabel: 'Description',
				anchor: '100%'
			}]
		}
/**/
		,{
			title: 'Filter',
			autoHeight: true,
			labelWidth: 74,
			style: 'padding: 10px 5px;',
			items: [{
				xtype: 'panel',
				border: false,
				anchor: '100%',
				layout:'column',
				labelWidth: 74,
				labelAlign: 'right',
				defaultType: 'panel',
				items: [{
					columnWidth: .25,
					xtype: 'label',
					fieldLabel: 'Origin(mm)',
					html: '<label style="width:74px;font-size:12px;line-height:19px;" class="x-form-item-label">Origin(mm):</label>'
				},{
					columnWidth: .25,
					border: false,
					layout: 'form',
					bodyStyle: 'padding-left:5px;',
					anchor: '100%',
					labelWidth: 10,
					labelAlign: 'right',
					items: {
						xtype: 'numberfield',
						name: 'PinX',
						fieldLabel: 'X',
						labelSeparator: '>',
						anchor: '100%'
					}
				},{
					columnWidth: .25,
					border: false,
					layout: 'form',
					bodyStyle: 'padding-left:5px;',
					anchor: '100%',
					labelWidth: 10,
					labelAlign: 'right',
					items: {
						xtype: 'numberfield',
						name: 'PinY',
						fieldLabel: 'Y',
						labelSeparator: '>',
						anchor: '100%'
					}
				},{
					columnWidth: .25,
					border: false,
					layout: 'form',
					bodyStyle: 'padding-left:5px;',
					anchor: '100%',
					labelWidth: 10,
					labelAlign: 'right',
					items: {
						xtype: 'numberfield',
						name: 'PinZ',
						fieldLabel: 'Z',
						labelSeparator: '>',
						anchor: '100%'
					}
				}]
			},{
				xtype: 'panel',
				border: false,
				anchor: '100%',
				layout:'column',
				labelWidth: 74,
				labelAlign: 'right',
				defaultType: 'panel',
				items: [{
					columnWidth: .25,
					xtype: 'label',
					html: '&nbsp;'
				},{
					columnWidth: .25,
					border: false,
					layout: 'form',
					bodyStyle: 'padding-left:5px;',
					anchor: '100%',
					labelWidth: 10,
					labelAlign: 'right',
					items: {
						xtype: 'numberfield',
						name: 'PinX2',
						fieldLabel: 'X',
						labelSeparator: '<',
						anchor: '100%'
					}
				},{
					columnWidth: .25,
					border: false,
					layout: 'form',
					bodyStyle: 'padding-left:5px;',
					anchor: '100%',
					labelWidth: 10,
					labelAlign: 'right',
					items: {
						xtype: 'numberfield',
						name: 'PinY2',
						fieldLabel: 'Y',
						labelSeparator: '<',
						anchor: '100%'
					}
				},{
					columnWidth: .25,
					border: false,
					layout: 'form',
					bodyStyle: 'padding-left:5px;',
					anchor: '100%',
					labelWidth: 10,
					labelAlign: 'right',
					items: {
						xtype: 'numberfield',
						name: 'PinZ2',
						fieldLabel: 'Z',
						labelSeparator: '<',
						anchor: '100%'
					}
				}]
//			},{
//				xtype: 'numberfield',
//				name: 'PinRadius',
//				fieldLabel: 'Radius(mm)',
//				width: 40
			},{
				xtype: 'combo',
				name: 'Version',
				fieldLabel: 'Data Version',
				width: comboSize.width,
				editable: false,
				store: new Ext.data.SimpleStore({
					fields:[
						dataVersionCombo.displayField,
						dataVersionCombo.valueField
					],
					data: version_datas
				}),
				mode: 'local',
				triggerAction: dataVersionCombo.triggerAction,
				displayField: dataVersionCombo.displayField,
				valueField: dataVersionCombo.valueField,
				value: '',
				listeners: {
					render: function(field){
					}
				}
			}]
		}
/**/
		],
		bbar: ['->','-',{
			text: 'Search',
			iconCls: 'find-item',
			handler: function(){
				var b = this;
				var value = {};
				$(pinFormPanel.getForm().el.dom).find("[name]").each(function(){
					var $this = $(this);
					var name = $this.attr("name");
					var comp = Ext.getCmp($this.attr("id"));
					if($this.attr("type")=='checkbox'){
						value[name] = $this.attr("checked");
					}else if(comp.getXType()=='numberfield'){
						var val = $this.val();
						if(!Ext.isEmpty(val)) value[name] = val-0;
					}else if(comp.getXType()=='combo'){
						value[name] = comp.getValue();
					}else{
						value[name] = $this.val();
					}
					if(Ext.isEmpty(value[name])) delete value[name];
				});
				pinGridPanelStore.baseParams.json = Ext.util.JSON.encode(value);
				pinGridPanelBBar.changePage(1);
			}
		}]
	});

	var win = new Ext.Window({
		title: config.title,
		iconCls: config.iconCls,
		animateTarget: config.animateTarget,
		modal: config.modal,
		width: config.width,
		height: config.height,
		plain: config.plain,
		resizable: config.resizable,
		closeAction: 'close',
		layout: 'border',
		buttonAlign: 'right',
		buttons: [{
			disabled: true,
			text: 'OK',
			listeners: {
				render: function(b){
					pinGridPanel.getSelectionModel().on({
						selectionchange: function(selModel){
							b.setDisabled(selModel.getCount()===0);
						}
					});
				},
				click: function(b){
					if(aCB) (aCB)(pinGridPanel.getSelectionModel().getSelections())
					win.close();
				}
			}
		},{
			text: 'Cancel',
			handler: function(){
				win.close();
			}
		}],
		items: [
			pinFormPanel,
			pinGridPanel
		]
	});
	win.show();
	pinGridPanelBBar.changePage(1);
};
///////////////////////////////////////////////////////////////////////////////
// ピングループの検索画面
///////////////////////////////////////////////////////////////////////////////
ag_extensions.global_pin.findPinGroup = function(config,aCB){
	var self = this;
	config = Ext.apply({},config||{},{
		title: 'find Pin Group',
		iconCls: 'find-item',
		modal: true,
		width: 450,
		height: 500,
		plain: false,
		resizable: false
	});

	var groupGridPanelStore = new Ext.data.JsonStore({
		url: cgipath.globalPin.group.search,
		id: 'PinGroupID',
		root: 'PinGroup',
		successProperty: 'success',
		totalProperty: 'total',
		remoteSort: true,
		sortInfo: {field: 'gpg_entry', direction: 'ASC'},
		fields: self.store_field_pin_group()
	});

	var groupGridPanelBBar = self._PagingToolbar({pageSize:20,store:groupGridPanelStore});

	var groupGridPanel = new Ext.grid.GridPanel({
		region: 'center',
		store: groupGridPanelStore,
		columns: self.grid_columns_pin_group(),
		stripeRows: true,
		columnLines: true,
		selModel: new Ext.grid.RowSelectionModel({
			listeners: {
				selectionchange: function(selModel){
				}
			}
		}),
		bbar: groupGridPanelBBar
	});

	var groupFormPanel = new Ext.form.FormPanel({
		region: 'north',
		height: 60,
		bodyStyle: 'padding:5px;',
		labelAlign: 'right',
		labelWidth: 64,
		defaultType: 'textfield',
		items: [{
			name: 'PinGroupDescription',
			fieldLabel: 'Description',
			anchor: '100%'
		}],
		bbar: ['->','-',{
			text: 'Search',
			iconCls: 'find-item',
			handler: function(){
				var b = this;
				var value = {};
				$(groupFormPanel.getForm().el.dom).find("[name]").each(function(){
					var $this = $(this);
					var name = $this.attr("name");
					if($this.attr("type")=='checkbox'){
						value[name] = $this.attr("checked");
					}else{
						value[name] = $this.val();
					}
				});
				groupGridPanelStore.baseParams.json = Ext.util.JSON.encode(value);
				groupGridPanelBBar.changePage(1);
			}
		}]
	});

	var win = new Ext.Window({
		title: config.title,
		iconCls: config.iconCls,
		animateTarget: config.animateTarget,
		modal: config.modal,
		width: config.width,
		height: config.height,
		plain: config.plain,
		resizable: config.resizable,
		closeAction: 'close',
		layout: 'border',
		buttonAlign: 'right',
		buttons: [{
			disabled: true,
			text: 'OK',
			listeners: {
				render: function(b){
					groupGridPanel.getSelectionModel().on({
						selectionchange: function(selModel){
							b.setDisabled(selModel.getCount()===0);
						}
					});
				},
				click: function(b){
					if(aCB) (aCB)(groupGridPanel.getSelectionModel().getSelections())
					win.close();
				}
			}
		},{
			text: 'Cancel',
			handler: function(){
				win.close();
			}
		}],
		items: [
			groupFormPanel,
			groupGridPanel
		]
	});
	win.show();
	groupGridPanelBBar.changePage(1);
};
///////////////////////////////////////////////////////////////////////////////
// ピングループの追加関数
///////////////////////////////////////////////////////////////////////////////
ag_extensions.global_pin.addPinGroup = function(config){
	var self = this;
	if(!self.__auth) return;//ログインしていない場合
	config = Ext.apply({},config||{},{
		title: 'add Pin Group'
	});

	//空のレコードを生成
	var pinRecord = Ext.data.Record.create(ag_comment_store_fields);
	var def = {
		PinGroupPinNumberDrawFlag: Ext.getCmp('anatomo_pin_number_draw_check').getValue(),
		PinGroupPinDescriptionDrawFlag: Ext.getCmp('anatomo_pin_description_draw_check').getValue(),
		PinGroupPinShape: Ext.getCmp('anatomo_pin_shape_combo').getValue(),
		PinGroupPinColor: '0000FF'
	};
	def.PinGroupPinSize = ag_extensions.toJSON.pinShapeAbbr2PinSize(def.PinGroupPinShape);
	def.PinGroupPinShape = ag_extensions.toJSON.pinShapeAbbr2PinShape(def.PinGroupPinShape);
	var record = new pinRecord(Ext.apply({},def,ag_extensions.toJSON.defaults.PinGroup()));

	//編集画面を開く
	self._editGlobalPinGroup(config,record,function(r){
//		console.log(r);
		var url = cgipath.globalPin.group.adding;
		Ext.Ajax.request({
			url: url,
			method: 'POST',
			params: {json: Ext.util.JSON.encode(r.data)},
			callback: function(options,success,response){
//				console.log(success);
				if(success){
//					console.log(response);
					var json = Ext.util.JSON.decode(response.responseText);
					if(json && json.success){
					}
				}
			}
		});
	});
};
///////////////////////////////////////////////////////////////////////////////
// ピングループの編集画面
///////////////////////////////////////////////////////////////////////////////
ag_extensions.global_pin._editGlobalPinGroup = function(config,record,aCB){
	var self = this;
	config = Ext.apply({},config||{},{
		title: 'add Pin Group',
		modal: true,
//		width: 450,
//		height: 500,

//		width: 600,
		width: 666,
		height: 390,

		plain: false,
		resizable: false
	});
//	console.log('ag_extensions.global_pin.addPinGroup()');

// ピングループの属性フィールド
	var idTextField = new Ext.form.TextField({
		disabled: true,
		name: 'PinGroupID',
		fieldLabel: 'ID',
		anchor: '100%'
	});
	var descTextArea = new Ext.form.TextArea({
		name: 'PinGroupDescription',
		fieldLabel: 'Description',
		anchor: '100%'
	});
	var colorField = new Ext.ux.ColorField({
		name: 'PinGroupPinColor',
		allowBlank: false,
		fieldLabel: 'Color',
		ctCls : 'x-small-editor',
//		id:'anatomo-edit-color-palette',
		width: 80
	});

	var apiAddingCheckbox = new Ext.form.Checkbox({
		name: 'PinGroupApiAdding',
		boxLabel: 'Adding',
		inputValue: true,
		autoWidth: true
	});
	var apiExclusionCheckbox = new Ext.form.Checkbox({
		name: 'PinGroupApiExclusion',
		boxLabel: 'Exclusion',
		inputValue: true,
		autoWidth: true
	});
	var apiReferenceCheckbox = new Ext.form.Checkbox({
		name: 'PinGroupApiReference',
		boxLabel: 'Reference',
		inputValue: true,
		autoWidth: true
	});
	var apiCheckboxGroup = new Ext.form.CheckboxGroup({
		fieldLabel: 'API',
		anchor: '100%',
		columns: [80,80,80],
		items: [
			apiAddingCheckbox,
			apiExclusionCheckbox,
			apiReferenceCheckbox
		]
	});

	var searchCheckbox = new Ext.form.Checkbox({
		name: 'PinGroupSearch',
		fieldLabel: 'Search',
		boxLabel: 'Permit',
		inputValue: true,
		anchor: '100%'
	});
	var valueTextArea = new Ext.form.TextArea({
		name: 'PinGroupValue',
		fieldLabel: 'Value',
		anchor: '100%'
	});

	var pinGridPanelStore = new Ext.data.JsonStore({
		url: cgipath.globalPin.pin.getlist,
		root: 'Pin',
		totalProperty: 'total',
		autoLoad: false,
//		baseParams: {
//			json: Ext.util.JSON.encode({PinGroupID: record.data.PinGroupID})
//		},
		remoteSort: true,
		sortInfo: {field: 'gp_entry', direction: 'ASC'},
		fields: self.store_field_pin()
	});

	var groupAttrFormPanel = new Ext.form.FormPanel({
		region: 'center',
//		title: 'Group Attribute',
		bodyStyle: 'padding:5px;',
		labelAlign: 'right',
		labelWidth: 64,
		defaultType: 'textfield',
//		defaults: {
//			anchor: '100%'
//		},
		items: [
			idTextField,
			colorField,
			descTextArea,
			apiCheckboxGroup,
			searchCheckbox,
			valueTextArea
		],
		tbar: ['<label style="font-size:11px;font-weight:bold;color:#15428b;line-height:21px;">Group Attribute</label>'],
		buttonAlign: 'right',
		buttons: [{
			text: 'Reset',
			handler: function(){
				var form = groupAttrFormPanel.getForm();
				form.loadRecord(record);
				apiAddingCheckbox.setValue(record.get('PinGroupApiAdding'));
				apiExclusionCheckbox.setValue(record.get('PinGroupApiExclusion'));
				apiReferenceCheckbox.setValue(record.get('PinGroupApiReference'));
			}
		},{
			text: 'Save',
			formBind: true,
			handler: function(){
//				var values = groupAttrFormPanel.getForm().getValues();
				var values = {};
				$(groupAttrFormPanel.getForm().el.dom).find("[name]").each(function(){
					var $this = $(this);
					var name = $this.attr("name");
					if($this.attr("type")=='checkbox'){
						values[name] = $this.attr("checked");
					}else{
						values[name] = $this.val();
					}
				});

//				console.log(record);
//				console.log(values);
				record.beginEdit();
				var value;
				for(var key in values){
					value = values[key];
					if(key == 'PinGroupPinColor'){
						if(value.substr(0,1)=="#") value = value.substr(1);
						record.set('PinGroupPinDescriptionColor',value);
					}
					else if(value == 'true' || value == 'false'){
						if(value=='true'){
							value = true;
						}else{
							value = false;
						}
					}
					record.set(key,value);
				}
				record.set('color',record.get('PinGroupPinColor'));
				record.set('comment',record.get('PinGroupDescription'));
				record.commit(true);
				record.endEdit();
				self.__parentPanel.getView().refresh();
				updateAnatomo();

				var url;
				if(Ext.isEmpty(record.get('PinGroupID'))){
					url = cgipath.globalPin.group.adding;
				}else{
					url = cgipath.globalPin.group.update;
				}
//				if(aCB) (aCB)(record);
				Ext.Ajax.request({
					url: url,
					method: 'POST',
					params: {json: Ext.util.JSON.encode(record.data)},
					callback: function(options,success,response){
//						console.log(success);
						if(success){
//							console.log(response);
							var json = Ext.util.JSON.decode(response.responseText);
							if(json && json.success && json.PinGroup && json.PinGroup.length==1){
								record.beginEdit();
								for(var key in json.PinGroup[0]){
									record.set(key,json.PinGroup[0][key]);
								}
								record.set('color',record.get('PinGroupPinColor'));
								record.set('comment',record.get('PinGroupDescription'));
								record.commit(true);
								record.endEdit();
								self.__parentPanel.getView().refresh();
								updateAnatomo();

								var form = groupAttrFormPanel.getForm();
								form.loadRecord(record);
								apiAddingCheckbox.setValue(record.get('PinGroupApiAdding'));
								apiExclusionCheckbox.setValue(record.get('PinGroupApiExclusion'));
								apiReferenceCheckbox.setValue(record.get('PinGroupApiReference'));
								pinGridPanel.setDisabled(Ext.isEmpty(record.get('PinGroupID')));

								pinGridPanelStore.baseParams.json = Ext.util.JSON.encode({PinGroupID: record.data.PinGroupID});
							}
						}
					}
				});
			}
		}]
	});

	var pinGridPanelBBar = self._PagingToolbar({pageSize:20,store:pinGridPanelStore});

	var pinAddTBBtn = new Ext.Toolbar.Button({
		text: 'Add',
		iconCls: 'add-link-item',
		handler: function(){
			var b = this;
			self.findPin({
				title: 'Select Pin',
				iconCls: b.iconCls,
				animateTarget: b.el
			},function(records){
				var PinGroupID = record.get('PinGroupID');
				if(Ext.isEmpty(PinGroupID)) return;
				var arr = [];
				Ext.each(records,function(r,i,a){
					arr.push({
						PinGroupID: PinGroupID,
						PinID: r.get('PinID')
					});
				});
				if(arr.length>0){
					var url = cgipath.globalPin.group.link;
					Ext.Ajax.request({
						url: url,
						method: 'POST',
						params: {json: Ext.util.JSON.encode(arr)},
						callback: function(options,success,response){
//							console.log(success);
							if(success){
//								console.log(response);
								var json = Ext.util.JSON.decode(response.responseText);
								if(json && json.success){
									pinGridPanelBBar.changePage(1);
									updateAnatomo();
								}
							}
						}
					});
				}
			});
		}
	});
	var pinEditTBBtn = new Ext.Toolbar.Button({
		text: 'Edit',
		iconCls: 'edit-pin-item',
		disabled: true,
		handler: function(){
			var b = this;
		}
	});
	var pinDelTBBtn = new Ext.Toolbar.Button({
		text: 'Del',
		iconCls: 'del-link-item',
		disabled: true,
		handler: function(){
			var b = this;
			var records = pinGridPanel.getSelectionModel().getSelections();
			if(records.length==0) return;

			var PinGroupID = record.get('PinGroupID');
			if(Ext.isEmpty(PinGroupID)) return;
			var arr = [];
			Ext.each(records,function(r,i,a){
				arr.push({
					PinGroupID: PinGroupID,
					PinID: r.get('PinID')
				});
			});
			if(arr.length>0){
				var url = cgipath.globalPin.group.unlink;
				Ext.Ajax.request({
					url: url,
					method: 'POST',
					params: {json: Ext.util.JSON.encode(arr)},
					callback: function(options,success,response){
//						console.log(success);
						if(success){
//							console.log(response);
							var json = Ext.util.JSON.decode(response.responseText);
							if(json && json.success){
								pinGridPanelBBar.changePage(1);
								updateAnatomo();
							}
						}
					}
				});
			}
		}
	});

	var pinGridPanel = new Ext.grid.GridPanel({
		disabled: Ext.isEmpty(record.get('PinGroupID')),
		region: 'east',
		width: 330,
//		title: 'Pin',
//		iconCls: 'pin-item',
		stripeRows: true,
		columnLines: true,
		store: pinGridPanelStore,
		columns: self.grid_columns_pin(),
		selModel: new Ext.grid.RowSelectionModel({
			listeners: {
				selectionchange: function(selModel){
					pinEditTBBtn.setDisabled(selModel.getCount()!==1);
					pinDelTBBtn.setDisabled(selModel.getCount()===0);
				}
			}
		}),
		tbar: ['<label style="font-size:11px;font-weight:bold;color:#15428b;line-height:21px;">Pin</label>','->'],
		bbar: pinGridPanelBBar
	});

	var win = new Ext.Window({
		title: config.title,
		iconCls: config.iconCls,
		animateTarget: config.animateTarget,
		modal: config.modal,
		width: config.width,
		height: config.height,
		plain: config.plain,
		resizable: config.resizable,
		closeAction: 'close',
		layout: 'border',
		buttonAlign: 'right',
		buttons: [{
			text: 'Close',
			handler: function(){
				win.close();
			}
		}],
		items: [
			pinGridPanel,
			groupAttrFormPanel
		]
	});
	win.show();

	descTextArea.setDisabled(true);
	apiCheckboxGroup.setDisabled(true);
	searchCheckbox.setDisabled(true);
	valueTextArea.setDisabled(true);
	pinGridPanel.setDisabled(true);

	if(!Ext.isEmpty(record.get('PinGroupID'))){
		self._authGlobalPinGroup(record,function(success,json){
			if(json && json.PinGroup && json.PinGroup.length==1){
				record.beginEdit();
				for(var key in json.PinGroup[0]){
					record.set(key,json.PinGroup[0][key]);
				}
				if(record.get('color') != record.get('PinGroupPinColor')) record.set('PinGroupPinColor',record.get('color'))
				record.set('comment',record.get('PinGroupDescription'));
				record.commit(true);
				record.endEdit();
				self.__parentPanel.getView().refresh();
				updateAnatomo();

				var form = groupAttrFormPanel.getForm();
				form.loadRecord(record);
				apiAddingCheckbox.setValue(record.get('PinGroupApiAdding'));
				apiExclusionCheckbox.setValue(record.get('PinGroupApiExclusion'));
				apiReferenceCheckbox.setValue(record.get('PinGroupApiReference'));
				if(success || record.get('PinGroupApiReference')){
					pinGridPanel.setDisabled(Ext.isEmpty(record.get('PinGroupID')));
					pinGridPanelStore.baseParams.json = Ext.util.JSON.encode({PinGroupID: record.data.PinGroupID});
					pinGridPanelBBar.changePage(1);
				}
			}
			if(success){
				descTextArea.setDisabled(false);
				apiCheckboxGroup.setDisabled(false);
				searchCheckbox.setDisabled(false);
				valueTextArea.setDisabled(false);
//				pinGridPanel.setDisabled(false);

				var topTBar = pinGridPanel.getTopToolbar();
				topTBar.addSeparator();
				topTBar.addButton(pinAddTBBtn);
//				topTBar.addSeparator();
//				topTBar.addButton(pinEditTBBtn);
				topTBar.addSeparator();
				topTBar.addButton(pinDelTBBtn);
			}else{
			}
		});
	}else if(self.__auth){
		descTextArea.setDisabled(false);
		apiCheckboxGroup.setDisabled(false);
		searchCheckbox.setDisabled(false);
		valueTextArea.setDisabled(false);
		var form = groupAttrFormPanel.getForm();
		form.loadRecord(record);
	}
};
///////////////////////////////////////////////////////////////////////////////
// 既存のパラメータ生成関数の置き換え
///////////////////////////////////////////////////////////////////////////////
ag_extensions.global_pin.makeAnatomoPrm = function(params){
	var idx=0;
	var record = params[idx++];
	var anatomo_pin_shape_combo_value = params[idx++];
	var coordinate_system = params[idx++];
	var properties = params[idx++];
//	console.log("makeAnatomoPrm()");
//	console.log(record);
//	console.log(anatomo_pin_shape_combo_value);
//	console.log(coordinate_system);
//	console.log(properties);

	if(Ext.isEmpty(record) || Ext.isEmpty(record.data)) return undefined;

	properties = properties || {};
	var data = Ext.apply({},properties,record.data);

	if(Ext.isEmpty(anatomo_pin_shape_combo_value)){
		try{
			anatomo_pin_shape_combo_value = Ext.getCmp("anatomo_pin_shape_combo").getValue();
		}catch(e){
			anatomo_pin_shape_combo_value = init_anatomo_pin_shape;
		}
	}

	//coordinate_system
	if(Ext.isEmpty(coordinate_system)){
		try{
			coordinate_system = Ext.getCmp("ag-coordinate-system-combo").getValue();
		}catch(e){
			coordinate_system = prm_record.data.coord;
		}
	}
	var prm = '';
	try{
		var no = parseInt(data.no);
		var num = makeAnatomoOrganNumber(no);
		// No
		prm = prm + "pno" + num + "=" + no.toString();

		if(!Ext.isEmpty(data.PinID) || !Ext.isEmpty(data.PinGroupID)){
			// ID
			if(!Ext.isEmpty(data.PinID)) prm = prm + "&pid" + num + "=" + data.PinID;
			if(!Ext.isEmpty(data.PinGroupID)) prm = prm + "&pgid" + num + "=" + data.PinGroupID;
		}else{
		}

		// 3Dx
		if(!Ext.isEmpty(data.x3d) && !isNaN(data.x3d)) prm = prm + "&px" + num + "=" + roundPrm(data.x3d);
		// 3Dy
		if(!Ext.isEmpty(data.y3d) && !isNaN(data.y3d)) prm = prm + "&py" + num + "=" + roundPrm(data.y3d);
		// 3Dz
		if(!Ext.isEmpty(data.z3d) && !isNaN(data.z3d)) prm = prm + "&pz" + num + "=" + roundPrm(data.z3d);
		// ArrVec3Dx
		if(!Ext.isEmpty(data.avx3d) && !isNaN(data.avx3d)) prm = prm + "&pax" + num + "=" + roundPrm(data.avx3d);
		// ArrVec3Dy
		if(!Ext.isEmpty(data.avy3d) && !isNaN(data.avy3d)) prm = prm + "&pay" + num + "=" + roundPrm(data.avy3d);
		// ArrVec3Dz
		if(!Ext.isEmpty(data.avz3d) && !isNaN(data.avz3d)) prm = prm + "&paz" + num + "=" + roundPrm(data.avz3d);
		// UpVec3Dx
		if(!Ext.isEmpty(data.uvx3d) && !isNaN(data.uvx3d)) prm = prm + "&pux" + num + "=" + roundPrm(data.uvx3d);
		// UpVec3Dy
		if(!Ext.isEmpty(data.uvy3d) && !isNaN(data.uvy3d)) prm = prm + "&puy" + num + "=" + roundPrm(data.uvy3d);
		// UpVec3Dz
		if(!Ext.isEmpty(data.uvz3d) && !isNaN(data.uvz3d)) prm = prm + "&puz" + num + "=" + roundPrm(data.uvz3d);


		var pdc=0;
		// Draw Pin Description
		var drawCheck = Ext.getCmp('anatomo_pin_description_draw_check');
		if(drawCheck && drawCheck.rendered){
			if(drawCheck.getValue()){
				prm = prm + "&pdd" + num + "=1";
				prm = prm + "&pdc" + num + "=" + data.color;
				pdc=1;
			}else{
			}
		}else if(init_anatomo_pin_description_draw){
			prm = prm + "&pdd" + num + "=1";
			prm = prm + "&pdc" + num + "=" + data.color;
			pdc=1;
		}

		// Draw Pin Number
		var drawCheck = Ext.getCmp('anatomo_pin_number_draw_check');
		if(drawCheck && drawCheck.rendered){
			if(drawCheck.getValue()){
				prm = prm + "&pnd" + num + "=1";
				if(!pdc) prm = prm + "&pdc" + num + "=" + data.color;	//pdcが未設定の場合
			}else{
			}
		}else if(init_anatomo_pin_number_draw){
			prm = prm + "&pnd" + num + "=1";
			if(!pdc) prm = prm + "&pdc" + num + "=" + data.color;	//pdcが未設定の場合
		}

		// Point Shape
		prm = prm + "&ps" + num + "=" + anatomo_pin_shape_combo_value;
		// ForeRGB
		prm = prm + "&pcl" + num + "=" + data.color;
		// OrganID
		if(!Ext.isEmpty(data.oid)) prm = prm + "&poi" + num + "=" + encodeURIComponent(data.oid);
		// OrganName
		if(!Ext.isEmpty(data.oid)) prm = prm + "&pon" + num + "=" + encodeURIComponent(data.organ);
		// Comment
		prm = prm + "&pd" + num + "=" + (Ext.isEmpty(data.comment) ? '' : encodeURIComponent(data.comment));

		//coordinate_system
		if(!Ext.isEmpty(data.coord)){
			prm = prm + "&pcd" + num + "=" + encodeURIComponent(data.coord);
		}else if(!Ext.isEmpty(coordinate_system)){
			prm = prm + "&pcd" + num + "=" + encodeURIComponent(coordinate_system);
		}

	}catch(e){
		_dump(e);
		prm = undefined;
	}
//	console.log("prm=["+prm+"]");
	return prm;
};
///////////////////////////////////////////////////////////////////////////////
// 既存のグリッド用のレンダラーの置き換え
///////////////////////////////////////////////////////////////////////////////
ag_extensions.global_pin.grid_renderer = function(params){
//	console.log("ag_extensions.global_pin.grid_renderer()");
	var idx=0;
	var value = params[idx++];
	var metadata = params[idx++];
	var record = params[idx++];
	var rowIndex = params[idx++];
	var colIndex = params[idx++];
	var store = params[idx++];

	var dataIndex = ag_pin_grid_panel_cols[colIndex].dataIndex;
	if(dataIndex=='no'){
		Ext.each(['PinID','PinGroupID'],function(f,i,a){
			if(!Ext.isEmpty(record.data[f]) && typeof record.data[f] == 'string' && record.data[f].match(/^[0-9]+$/)) return true;

			if(!Ext.isEmpty(record.data[f])){
				value = record.data[f];
				dataIndex = f;
				metadata.attr = 'style="text-align:left;"';
				return false;
			}
		});
	}else if(dataIndex=='color'){
		Ext.each(['PinColor','PinGroupPinColor'],function(f,i,a){
			if(!Ext.isEmpty(record.data[f])){
				value = record.data[f];
				dataIndex = f;
				metadata.attr = 'style="text-align:left;"';
				return false;
			}
		});
	}else if(dataIndex=='comment'){
		Ext.each(['PinDescription','PinGroupDescription'],function(f,i,a){
			if(!Ext.isEmpty(record.data[f])){
				value = record.data[f];
				dataIndex = f;
				metadata.attr = 'style="text-align:left;"';
				return false;
			}
		});
	}
	var item;
	for(var i=0;i<record.fields.length;i++){
		if(record.fields.keys[i] != dataIndex) continue;
		item = record.fields.items[i];
		break;
	}

	if(item){
		if(item.type == 'date'){
			if(dataIndex == 'entry' && value) value = new Date(value).format(bp3d.defaults.DATE_FORMAT);
			if(dataIndex == 'lastmod' && value) value = new Date(value).format(bp3d.defaults.TIME_FORMAT);
		}
	}

	return value;
};
///////////////////////////////////////////////////////////////////////////////
//レコードがピンか判定する
///////////////////////////////////////////////////////////////////////////////
ag_extensions.global_pin._isGlobalPin = function(record){
	var self = this;
	if(record && !Ext.isEmpty(record.data.PinID) && typeof record.data.PinID == 'string' && record.data.PinID.match(/^[0-9]+$/)) return false;
	if(record && !Ext.isEmpty(record.data.PinID)) return true;
	return false;
};
///////////////////////////////////////////////////////////////////////////////
//レコードがグループか判定する
///////////////////////////////////////////////////////////////////////////////
ag_extensions.global_pin._isGlobalPinGroup = function(record){
	var self = this;
	if(record && !Ext.isEmpty(record.data.PinGroupID) && typeof record.data.PinGroupID == 'string' && record.data.PinGroupID.match(/^[0-9]+$/)) return false;
	if(record && !Ext.isEmpty(record.data.PinGroupID)) return true;
	return false;
};
///////////////////////////////////////////////////////////////////////////////
//レコードがピンまたはグループか判定する
///////////////////////////////////////////////////////////////////////////////
ag_extensions.global_pin.isGlobalPin = function(record){
	var self = this;
	if(record && (self._isGlobalPin(record) || self._isGlobalPinGroup(record))) return true;
	return false;
};
///////////////////////////////////////////////////////////////////////////////
//編集可かサーバに問い合わせする
///////////////////////////////////////////////////////////////////////////////
ag_extensions.global_pin._auth = function(aURL,aOBJ,aCB){
	var self = this;
	if(Ext.isEmpty(aURL) || Ext.isEmpty(aOBJ)){
		if(aCB) (aCB)(false);
		return;
	}
	Ext.Ajax.request({
		url: aURL,
		method: 'POST',
		params: {json: Ext.util.JSON.encode(aOBJ)},
		callback: function(options,success,response){
			var json;
			var rtn = false;
			if(success){
				json = Ext.util.JSON.decode(response.responseText);
				if(json && json.success) rtn = json.success;
			}
			if(aCB) (aCB)(rtn,json);
		}
	});
};
///////////////////////////////////////////////////////////////////////////////
//ピンが編集可か判定する
///////////////////////////////////////////////////////////////////////////////
ag_extensions.global_pin._authGlobalPin = function(record,aCB){
	var self = this;
	if(Ext.isEmpty(record) || Ext.isEmpty(record.data.PinID)){
		if(aCB) (aCB)(false);
		return;
	}
	var url = cgipath.globalPin.pin.auth;
	self._auth(url,{PinID:record.data.PinID},aCB);
};
///////////////////////////////////////////////////////////////////////////////
//グループが編集可か判定する
///////////////////////////////////////////////////////////////////////////////
ag_extensions.global_pin._authGlobalPinGroup = function(record,aCB){
	var self = this;
	if(Ext.isEmpty(record) || Ext.isEmpty(record.data.PinGroupID)){
		if(aCB) (aCB)(false);
		return;
	}
	var url = cgipath.globalPin.group.auth;
	self._auth(url,{PinGroupID:record.data.PinGroupID},aCB);
};
///////////////////////////////////////////////////////////////////////////////
//ピン属性編集画面(現行を引き継いだ場合)
///////////////////////////////////////////////////////////////////////////////
ag_extensions.global_pin._editGlobalPin_old = function(config,record){
	var self = this;
	if(Ext.isEmpty(record)) return;

	var descTextArea = new Ext.form.TextArea({
		disabled: true,
		hideLabel: true,
		style: 'margin:4px 0 0 4px;',
		anchor: '-8 -8',
		value: record.data.PinDescription
	});

	var colorField = new Ext.ux.ColorField({
		ctCls : 'x-small-editor',
		width: 80,
		style: 'margin:0 0 0 4px;',
		hideLabel: true,
		value: record.data.PinColor
	});

	var fmasearchGridCellCopyBtn = new Ext.Toolbar.Button({
		text: 'Paste',
		iuconCls: '',
		disabled: true,
		handler: function(e){
			var grid = fmasearchGrid;
			var sel = grid.getSelectionModel();
			if(!sel || !sel.hasSelection()) return;
			var cellArr = sel.getSelectedCell();
			grid.fireEvent('celldblclick',grid,cellArr[0],cellArr[1],e);
		},
		scope: this
	});

	var fmasearchGrid = new Ext.grid.GridPanel({
		disabled: true,
//		xtype: 'grid',
//		id:'anatomo-edit-fmasearch-grid',
		columns: [
			{dataIndex:'f_id',   header:get_ag_lang('CDI_NAME'),          width:70, resizable:true, fixed:true},
			{dataIndex:'name_e', header:get_ag_lang('DETAIL_TITLE_NAME_E')
		],
		selModel: new Ext.grid.CellSelectionModel(),
		store: fma_search_store,
		loadMask: true,
		maskDisabled: true,
		height: 234,
		stripeRows: true,
		columnLines: true,
		tbar: [
			new Ext.app.SearchFMAStore({
				hideLabel: true,
				pageSize: 20,
				store: fma_search_store
			}),'->',fmasearchGridCellCopyBtn
		],
		bbar: new Ext.PagingToolbar({
			pageSize: 20,
			store: fma_search_store,
			displayInfo: false,
			displayMsg: '',
			emptyMsg: '',
			hideMode: 'offsets',
			hideParent: true
		}),
		listeners: {
			'render': function(grid){
				grid.getColumnModel().on({
					'hiddenchange' : function(column,columnIndex,hidden){
						resizeGridPanelColumns(fmasearchGrid);
					},
					scope: this,
					delay: 100
				});
			},
			'resize': function(grid){
				resizeGridPanelColumns(grid);
			},
			'cellclick': function(grid,rowIndex,columnIndex,e){
				if(rowIndex>=0 && rowIndex>=0) fmasearchGridCellCopyBtn.enable();
			},
			'celldblclick': function(grid,rowIndex,columnIndex,e){
//_dump('celldblclick');
				try{
					var record = grid.getStore().getAt(rowIndex);
					var fieldName = grid.getColumnModel().getDataIndex(columnIndex);
					var text = descTextArea;
					if(text){
						var dom = text.el.dom;
						if(dom.selectionStart != undefined){
							var st = dom.selectionStart>0?dom.value.slice(0,dom.selectionStart):"";
							var et = dom.value.slice(dom.selectionEnd);
							text.setValue(st+record.get(fieldName)+et);
						}else{
							text.focus();
							var selection = dom.ownerDocument.selection.createRange();
							selection.text = record.get(fieldName) + selection.text;
						}
					}
				}catch(e){
					for(var key in e){
						_dump(e[key]);
					}
				}
			},
			scope:this
		}
	});

	var win = new Ext.Window({
		title:'Edit Attribute Dialog',
		modal:true,
		width:450,
		height:500,
		closeAction:'close',
		plain:true,
		resizable: false,
		items: [{
			layout: 'anchor',
			items: [{
				height: 152,
				border: false,
				anchor: '100%',
				layout:'column',
				items: [{
					xtype: 'fieldset',
					title: 'Description',
					columnWidth: 1,
					height: 162,
					bodyStyle: 'padding:0px;',
					style: 'margin:0 0 4px 4px;',
					layout: 'anchor',
					items: descTextArea
				},{
					xtype: 'fieldset',
					title: 'Color',
					width: 130,
					height: 60,
					style: 'margin:0 4px 4px 4px;',
					items: colorField
				}]
			},{
				xtype: 'fieldset',
				title: 'FMAID',
				style: 'margin:0 0 4px 4px;',
				anchor: '-8 -38',
				items: fmasearchGrid
			}]
		}],
		buttons: [{
			text:'OK',
			handler : function() {
				var color = colorField.getValue();
				if(color.substr(0,1)=="#") color = color.substr(1);
				record.beginEdit();
				record.set('comment', descTextArea.getValue());
				record.set('PinDescription', descTextArea.getValue());
				record.set('color', color);
				record.set('PinColor', color);
				record.set('PinDescriptionColor', color);
				record.commit(true);
				record.endEdit();
				self.__parentPanel.getView().refresh();
				self._updateGlobalPin(record);
				win.close();
				updateAnatomo();
			}
		},{
			text:'Cancel',
			handler : function() {
				win.close();
			}
		}],
		listeners: {
			'render': function(win){
			},
			scope:this
		}

	});
	win.show();

	if(self.__auth){
		self._authGlobalPin(record,function(success,json){
			if(success){
				descTextArea.setDisabled(false);
				fmasearchGrid.setDisabled(false);
			}
			if(json && json.Pin && json.Pin.length==1){
				descTextArea.setValue(json.Pin[0].PinDescription);
				colorField.setValue(json.Pin[0].PinColor);
				record.beginEdit();
				for(var key in json.Pin[0]){
					record.set(key, json.Pin[0][key]);
				}
				record.commit(true);
				record.endEdit();
				self.__parentPanel.getView().refresh();
				updateAnatomo();
			}
		});
	}
};
///////////////////////////////////////////////////////////////////////////////
//ピン属性編集画面(新規)
///////////////////////////////////////////////////////////////////////////////
ag_extensions.global_pin._editGlobalPin = function(config,record){
	var self = this;
	if(Ext.isEmpty(record)) return;

	config = Ext.apply({},config||{},{
		title: 'Edit Pin Attr',
		modal: true,
//		width: 450,
//		height: 500,

//		width: 600,
		width: 666,
		height: 390,

		plain: false,
		resizable: false
	});

	var idTextField = new Ext.form.TextField({
		disabled: true,
		name: 'PinID',
		fieldLabel: 'ID',
		anchor: '100%'
	});
	var descTextArea = new Ext.form.TextArea({
		disabled: true,
		fieldLabel: 'Description',
		anchor: '100%',
		height: 94,
		name: 'PinDescription'
	});
	var colorField = new Ext.ux.ColorField({
		width: 80,
		fieldLabel: 'Color',
		name: 'PinColor'
	});
	var valueTextArea = new Ext.form.TextArea({
		disabled: true,
		fieldLabel: 'Value',
		anchor: '100%',
		height: 94,
		name: 'PinValue'
	});

	var groupGridPanelStore = new Ext.data.JsonStore({
		url: cgipath.globalPin.group.getlist,
		root: 'PinGroup',
		totalProperty: 'total',
		autoLoad: false,
		remoteSort: true,
		sortInfo: {field: 'gpg_entry', direction: 'ASC'},
		fields: self.store_field_pin_group()
	});

	var pinAttrFormPanel = new Ext.form.FormPanel({
		region: 'center',
		bodyStyle: 'padding:5px;',
		labelAlign: 'right',
		labelWidth: 64,
		defaultType: 'textfield',
		items: [
			idTextField,
			colorField,
			descTextArea,
			valueTextArea
		],
		tbar: ['<label style="font-size:11px;font-weight:bold;color:#15428b;line-height:21px;">Pin Attribute</label>'],
		buttonAlign: 'right',
		buttons: [{
			text: 'Reset',
			handler: function(){
				var form = groupAttrFormPanel.getForm();
				form.loadRecord(record);
			}
		},{
			text: 'Save',
			formBind: true,
			handler: function(){
				var values = {};
				$(pinAttrFormPanel.getForm().el.dom).find("[name]").each(function(){
					var $this = $(this);
					var name = $this.attr("name");
					if($this.attr("type")=='checkbox'){
						values[name] = $this.attr("checked");
					}else{
						values[name] = $this.val();
					}
				});
				record.beginEdit();
				var value;
				for(var key in values){
					value = values[key];
					if(key == 'PinColor'){
						if(value.substr(0,1)=="#") value = value.substr(1);
						record.set('PinDescriptionColor',value);
					}
					else if(value == 'true' || value == 'false'){
						if(value=='true'){
							value = true;
						}else{
							value = false;
						}
					}
					record.set(key,value);
				}
				record.set('color',record.get('PinColor'));
				record.set('comment',record.get('PinDescription'));
				record.commit(true);
				record.endEdit();
				self.__parentPanel.getView().refresh();
				updateAnatomo();

				var url;
				if(Ext.isEmpty(record.get('PinID'))){
					url = cgipath.globalPin.pin.adding;
				}else{
					url = cgipath.globalPin.pin.update;
				}
//				if(aCB) (aCB)(record);
				Ext.Ajax.request({
					url: url,
					method: 'POST',
					params: {json: Ext.util.JSON.encode(record.data)},
					callback: function(options,success,response){
//						console.log(success);
						if(success){
//							console.log(response);
							var json = Ext.util.JSON.decode(response.responseText);
							if(json && json.success && json.Pin && json.Pin.length==1){
								record.beginEdit();
								for(var key in json.Pin[0]){
									record.set(key,json.Pin[0][key]);
								}
								record.set('color',record.get('PinColor'));
								record.set('comment',record.get('PinDescription'));
								record.commit(true);
								record.endEdit();
								self.__parentPanel.getView().refresh();
								updateAnatomo();

								var form = pinAttrFormPanel.getForm();
								form.loadRecord(record);

								groupGridPanelStore.baseParams.json = Ext.util.JSON.encode({PinID: record.data.PinID});
							}
						}
					}
				});
			}
		}]
	});

	var groupGridPanelBBar = self._PagingToolbar({pageSize:20,store:groupGridPanelStore});

	var groupAddTBBtn = new Ext.Toolbar.Button({
		text: 'Add',
		iconCls: 'add-link-item',
		handler: function(){
			var b = this;
			self.findPinGroup({
				title: 'Select Pin Group',
				iconCls: b.iconCls,
				animateTarget: b.el
			},function(records){
				var PinID = record.get('PinID');
				if(Ext.isEmpty(PinID)) return;
				var arr = [];
				Ext.each(records,function(r,i,a){
					arr.push({
						PinGroupID: r.get('PinGroupID'),
						PinID: PinID
					});
				});
				if(arr.length>0){
					var url = cgipath.globalPin.group.link;
					Ext.Ajax.request({
						url: url,
						method: 'POST',
						params: {json: Ext.util.JSON.encode(arr)},
						callback: function(options,success,response){
//							console.log(success);
							if(success){
//								console.log(response);
								var json = Ext.util.JSON.decode(response.responseText);
								if(json && json.success){
									groupGridPanelBBar.changePage(1);
									updateAnatomo();
								}
							}
						}
					});
				}
			});
		}
	});
	var groupEditTBBtn = new Ext.Toolbar.Button({
		text: 'Edit',
		iconCls: 'edit-link-item',
		disabled: true,
		handler: function(){
			var b = this;
		}
	});
	var groupDelTBBtn = new Ext.Toolbar.Button({
		text: 'Del',
		iconCls: 'del-link-item',
		disabled: true,
		handler: function(){
			var b = this;
			var records = groupGridPanel.getSelectionModel().getSelections();
			if(records.length==0) return;

			var PinID = record.get('PinID');
			if(Ext.isEmpty(PinID)) return;
			var arr = [];
			Ext.each(records,function(r,i,a){
				arr.push({
					PinGroupID: r.get('PinGroupID'),
					PinID: PinID
				});
			});
			if(arr.length>0){
				var url = cgipath.globalPin.group.unlink;
				Ext.Ajax.request({
					url: url,
					method: 'POST',
					params: {json: Ext.util.JSON.encode(arr)},
					callback: function(options,success,response){
//						console.log(success);
						if(success){
//							console.log(response);
							var json = Ext.util.JSON.decode(response.responseText);
							if(json && json.success){
								groupGridPanelBBar.changePage(1);
								updateAnatomo();
							}
						}
					}
				});
			}
		}
	});

	var groupGridPanel = new Ext.grid.GridPanel({
		disabled: Ext.isEmpty(record.get('PinID')),
		region: 'east',
		width: 330,
		stripeRows: true,
		columnLines: true,
		store: groupGridPanelStore,
		columns: self.grid_columns_pin_group(),
		selModel: new Ext.grid.RowSelectionModel({
			listeners: {
				selectionchange: function(selModel){
					groupEditTBBtn.setDisabled(selModel.getCount()!==1);
					groupDelTBBtn.setDisabled(selModel.getCount()===0);
				}
			}
		}),
		tbar: ['<label style="font-size:11px;font-weight:bold;color:#15428b;line-height:21px;">Group</label>','->'],
		bbar: groupGridPanelBBar
	});

	var win = new Ext.Window({
		title: config.title,
		iconCls: config.iconCls,
		animateTarget: config.animateTarget,
		modal: config.modal,
		width: config.width,
		height: config.height,
		plain: config.plain,
		resizable: config.resizable,
		closeAction: 'close',
		layout: 'border',
		buttonAlign: 'right',
		buttons: [{
			text: 'Close',
			handler: function(){
				win.close();
			}
		}],
		items: [
			groupGridPanel,
			pinAttrFormPanel
		]
	});
	win.show();

	descTextArea.setDisabled(true);
	valueTextArea.setDisabled(true);
	groupGridPanel.setDisabled(true);

	if(!Ext.isEmpty(record.get('PinID'))){
		self._authGlobalPin(record,function(success,json){
			if(json && json.Pin && json.Pin.length==1){
				record.beginEdit();
				for(var key in json.Pin[0]){
					record.set(key,json.Pin[0][key]);
				}
				if(record.get('color') != record.get('PinColor')) record.set('PinColor',record.get('color'))
				record.set('comment',record.get('PinDescription'));
				record.commit(true);
				record.endEdit();
				self.__parentPanel.getView().refresh();
				updateAnatomo();

				var form = pinAttrFormPanel.getForm();
				form.loadRecord(record);
				if(success){
					groupGridPanel.setDisabled(Ext.isEmpty(record.get('PinID')));
					groupGridPanelStore.baseParams.json = Ext.util.JSON.encode({PinID: record.get('PinID')});
					groupGridPanelBBar.changePage(1);
				}
			}
			if(success){
				descTextArea.setDisabled(false);
				valueTextArea.setDisabled(false);
				groupGridPanel.setDisabled(false);

				var topTBar = groupGridPanel.getTopToolbar();
				topTBar.addSeparator();
				topTBar.addButton(groupAddTBBtn);
//				topTBar.addSeparator();
//				topTBar.addButton(groupEditTBBtn);
				topTBar.addSeparator();
				topTBar.addButton(groupDelTBBtn);
			}
		});
	}
};


Ext.onReady(function(){
	if(Ext.isEmpty(ag_extensions.auth)) return;
	ag_extensions.global_pin._init();
});
