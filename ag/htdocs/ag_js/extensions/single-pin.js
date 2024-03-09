window.ag_extensions = window.ag_extensions || {};
ag_extensions.single_pin = ag_extensions.single_pin || {};

ag_extensions.single_pin._init = function(){
	var self = this;

//id="ag-comment-tabpanel"
	self.__parentPanel_id = 'anatomography-pin-grid-panel';
	self.__parentPanel = Ext.getCmp(self.__parentPanel_id);
//	console.log("ag_extensions.single_pin._init():"+self.__parentPanel);
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

ag_extensions.single_pin._initUI = function(){
	var self = this;
	try{
//		console.log("ag_extensions.single_pin._initUI():"+self.__parentPanel);
//		console.log("ag_extensions.single_pin._initUI():"+self.__parentPanel.getXType());
//		console.log("ag_extensions.single_pin._initUI():"+self.__parentPanel.getTopToolbar());
//		self.__panel = new Ext.Panel({
//			xtype: 'panel',
//			title: 'Global Pin Mng',
//		});
//		self.__parentPanel.add(self.__panel);

		var ttbar = self.__parentPanel.getTopToolbar();
		if(ttbar){
			ttbar.addSeparator();
			self.__tbBtn = ttbar.addButton({
				tooltip: 'Copy SINGLE-PIN URL',
				iconCls: 'pin_copy',
				listeners: {
					click: function(button, e) {
						self.openCopyWindow({
							animEl: button.el,
							iconCls: button.iconCls,
							title: button.tooltip
						});
					}
				}
			});

			self.__parentPanel.getSelectionModel().on({
				selectionchange: function(selModel){
					self.__tbBtn.setDisabled(selModel.getCount()<=0);
				},
				scope: self
			});

			self.bind();
		}
	}catch(e){
		console.error(e);
	}
};

ag_extensions.single_pin.bind = function(){
	var self = this;
	self.__parentPanel.on({
		cellclick: function(gridCmp,rowIndex,colIndex,e){
			try{
				if(gridCmp.getColumnModel().getIndexById('spu')!=colIndex) return;

				var selModel = gridCmp.getSelectionModel();
				selModel.clearSelections();
				selModel.selectRow(rowIndex);

				var animEl = Ext.get(gridCmp.getView().getCell(rowIndex,colIndex));

				var b = self.__tbBtn;
//				b.fireEvent('click',b);

				self.openCopyWindow({
					animEl: animEl,
					iconCls: b.iconCls,
					title: b.tooltip
				});

				e.stopEvent();
			}catch(e){
				if(window.console.error) window.console.error(e);
			}
		}
	});
};

ag_extensions.single_pin.gridColumn = function(){
	return {
		dataIndex: 'no',
		header: 'SINGLE-PIN URL',
		id: 'spu',
		renderer: ag_extensions.single_pin.rendererGrid
	};
};

ag_extensions.single_pin.rendererGrid = function(value,metadata,record,rowIndex,colIndex,store){
	var self = ag_extensions.single_pin;
	metadata.attr = metadata.cellAttr = 'style="-moz-user-select:none;-khtml-user-select:none;-webkit-user-select:none;user-select:none;cursor:pointer;text-align:center;"'
	try{
//		return '<a target="_blank" href='+self.createSinglePinSegmentUrl([record])+'><img src="css/icon_link_mini_off.png" width=15 height=14></a>';

//		return '<a href="#" onclick="return ag_extensions.single_pin.clickSPCol(this);"><img src="css/icon_link_mini_off.png" width=15 height=14></a>';
		return '<img src="css/icon_link_mini_off.png" width=15 height=14>';
	}catch(e){
		if(window.console.error) window.console.error(e);
		return '';
	}
};

ag_extensions.single_pin.clickSPCol = function(dom){
	var self = this;
	var records;
	try{
		var gridCmp = self.__parentPanel;
		var selModel = gridCmp.getSelectionModel();
		selModel.clearSelections();
		var idx = gridCmp.getView().findRowIndex(Ext.get(dom.parentNode));
	}catch(e){
		if(window.console.error) window.console.error(e);
	}
//	var b = Ext.getCmp('anatomo_comment_pick_sp_url_copy');
	return false;
};

//SINGLE-PIN URL (Pin alone)用
ag_extensions.single_pin.createSinglePinAloneUrl = function(records,asString){
	if(Ext.isEmpty(asString)) asString = true;
	var anatomo_pin_shape_combo_value;
	var coordinate_system;

	try{
		anatomo_pin_shape_combo_value = Ext.getCmp("anatomo_pin_shape_combo").getValue();
	}catch(e){
		anatomo_pin_shape_combo_value = undefined;
	}
	try{
		coordinate_system = Ext.getCmp("ag-coordinate-system-combo").getValue();
	}catch(e){
		coordinate_system = undefined;
	}

	var editURL = getEditUrl();
	var prmPins = [];
	Ext.each(records,function(r,i,a){
		var prmPin = makeAnatomoPrm_Pin(r,anatomo_pin_shape_combo_value,coordinate_system,{no:1});
		if(Ext.isEmpty(prmPin)) return true;

		var jsonStr = prmPin;
		try{
			jsonStr = ag_extensions.toJSON.URI2JSON(jsonStr,{
				toString:true,
				mapPin:false,
				callback:undefined
			});
			jsonStr = encodeURIComponent(jsonStr);
			prmPins.push(editURL + cgipath.animation + '?' + jsonStr);
		}catch(e){
			prmPins.push(editURL + cgipath.animation + '?' + prmPin);
		}
	});
	if(asString){
		var sp_alone_url;
		if(prmPins.length) sp_alone_url = prmPins.join("\n");
		return sp_alone_url;
	}else{
		return prmPins.length ? prmPins : undefined;
	}
};

//SINGLE-PIN URL (Pin on a segment)用
ag_extensions.single_pin.createSinglePinSegmentUrl = function(records,asString){
	if(Ext.isEmpty(asString)) asString = true;
	var anatomo_pin_shape_combo_value;
	var coordinate_system;

	try{
		anatomo_pin_shape_combo_value = Ext.getCmp("anatomo_pin_shape_combo").getValue();
	}catch(e){
		anatomo_pin_shape_combo_value = undefined;
	}
	try{
		coordinate_system = Ext.getCmp("ag-coordinate-system-combo").getValue();
	}catch(e){
		coordinate_system = undefined;
	}

	var cur_url = Text2URI(URI2Text(glb_anatomo_editor_url,{target:{parts:false,pins:false}}),{target:{parts:false,pins:false}});
	var cur_search = "";
	if(cur_url.indexOf("?")>=0) cur_search = cur_url.replace(/^.+\?(.*)$/g,"$1");
	var cur_params = {};
	if(cur_search){
		var params = Ext.urlDecode(cur_search);
		if(!params.tp_ap) params.tp_ap = cur_search;
		cur_params = Ext.urlDecode(params.tp_ap);
	}

	var newRecord = Ext.data.Record.create(bp3d_parts_store_fields);
	var numRec = makeAnatomoOrganNumber(1);
	var prm_record = ag_param_store.getAt(0);

	var editURL = getEditUrl();
	var prmPins = [];
	Ext.each(records,function(r,i,a){

		var parts_record = new newRecord({
			'f_id'          : r.data.oid,
			'exclude'       : false,
			'color'         : '#'+prm_record.data.color_rgb,
			'value'         : '',
			'zoom'          : false,
			'opacity'       : '1.0',
			'representation': 'surface',
			'point'         : false
		});

		var prmParts = "oid" + numRec + "=" + r.data.oid;
		prmParts += makeAnatomoOrganPrm(numRec,parts_record,null,null);

		var prmPin = makeAnatomoPrm_Pin(r,anatomo_pin_shape_combo_value,coordinate_system,{no:1});
		if(Ext.isEmpty(prmPin)) return true;

		var params = Ext.apply({},Ext.urlDecode(prmParts),cur_params);
		params = Ext.apply({},Ext.urlDecode(prmPin),params);

		var jsonStr = Ext.urlEncode(params);
		try{
			jsonStr = ag_extensions.toJSON.URI2JSON(jsonStr,{
				toString:true,
				mapPin:false,
				callback:undefined
			});
			jsonStr = encodeURIComponent(jsonStr);
			prmPins.push(editURL + cgipath.animation + '?' + jsonStr);
		}catch(e){
			prmPins.push(editURL + cgipath.animation + '?' + Ext.urlEncode(params));
		}
	});
	if(asString){
		var sp_segment_url;
		if(prmPins.length) sp_segment_url = prmPins.join("\n");
		return sp_segment_url;
	}else{
		return prmPins.length ? prmPins : undefined;
	}
};

//SINGLE-PIN URL (Pin on a whole model)用
ag_extensions.single_pin.createSinglePinWholeModelUrl = function(records,asString){
	if(Ext.isEmpty(asString)) asString = true;
	var anatomo_pin_shape_combo_value;
	var coordinate_system;

	try{
		anatomo_pin_shape_combo_value = Ext.getCmp("anatomo_pin_shape_combo").getValue();
	}catch(e){
		anatomo_pin_shape_combo_value = undefined;
	}
	try{
		coordinate_system = Ext.getCmp("ag-coordinate-system-combo").getValue();
	}catch(e){
		coordinate_system = undefined;
	}

	var cur_url = Text2URI(URI2Text(glb_anatomo_editor_url,{target:{pins:false}}),{target:{pins:false}});
	var cur_search = "";
	if(cur_url.indexOf("?")>=0){
		cur_search = cur_url.replace(/^.+\?(.*)$/g,"$1");
	}else if(cur_url.search(/[&]*pno[0-9]{3}=/)>=0){
		cur_search = cur_url;
	}
	var cur_params = {};
	if(cur_search){
		var params = Ext.urlDecode(cur_search);
		if(!params.tp_ap) params.tp_ap = cur_search;
		cur_params = Ext.urlDecode(params.tp_ap);
	}
	var editURL = getEditUrl();
	var prmPins = [];
	Ext.each(records,function(r,i,a){
		var prmPin = makeAnatomoPrm_Pin(r,anatomo_pin_shape_combo_value,coordinate_system,{no:1});
		if(Ext.isEmpty(prmPin)) return true;
		var params = Ext.apply({},Ext.urlDecode(prmPin),cur_params);
		var jsonStr = Ext.urlEncode(params);
		try{
			jsonStr = ag_extensions.toJSON.URI2JSON(jsonStr,{
				toString:true,
				mapPin:false,
				callback:undefined
			});
			jsonStr = encodeURIComponent(jsonStr);
			prmPins.push(editURL + cgipath.animation + '?' + jsonStr);
		}catch(e){
			prmPins.push(editURL + cgipath.animation + '?' + Ext.urlEncode(params));
		}
	});
	if(asString){
		var sp_whole_url;
		if(prmPins.length) sp_whole_url = prmPins.join("\n");
		return sp_whole_url;
	}else{
		return prmPins.length ? prmPins : undefined;
	}
};

ag_extensions.single_pin.openCopyWindow = function(aOpts){
	var self = this;
	aOpts = aOpts || {};

	var records;
	try{
		records = Ext.getCmp('anatomography-pin-grid-panel').getSelectionModel().getSelections();
	}catch(e){
		if(window.console.error) window.console.error(e);
	}
	if(Ext.isEmpty(records) || Ext.isEmpty(glb_anatomo_editor_url)) return;

//SINGLE-PIN URL (Pin alone)用
	self.__sp_alone_url = ag_extensions.single_pin.createSinglePinAloneUrl(records,false);
	if(Ext.isEmpty(self.__sp_alone_url)) return;

//SINGLE-PIN URL (Pin on a segment)用
	self.__sp_segment_url = ag_extensions.single_pin.createSinglePinSegmentUrl(records,false);
	if(Ext.isEmpty(self.__sp_segment_url)) return;

//SINGLE-PIN URL (Pin on a whole model)用
	self.__sp_whole_url = ag_extensions.single_pin.createSinglePinWholeModelUrl(records,false);
	if(Ext.isEmpty(self.__sp_whole_url)) return;

	self.__urls = {
		sp_alone_url : [],
		sp_segment_url : [],
		sp_whole_url : []
	};
	Ext.each(self.__sp_alone_url,function(url,i,a){
		self.__urls.sp_alone_url.push({url:url});
	});
	Ext.each(self.__sp_segment_url,function(url,i,a){
		self.__urls.sp_segment_url.push({url:url});
	});
	Ext.each(self.__sp_whole_url,function(url,i,a){
		self.__urls.sp_whole_url.push({url:url});
	});
	var sp_alone_url = "";
	var sp_segment_url = "";
	var sp_whole_url = "";

	var transaction_id = Ext.Ajax.request({
		url     : 'get-convert-url.cgi',
		method  : 'POST',
		params  : Ext.urlEncode({urls:Ext.util.JSON.encode(self.__urls)}),
		success : function(conn,response,options){

			try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
			if(Ext.isEmpty(results) || Ext.isEmpty(results.status_code) || results.status_code!=200){
				var msg = get_ag_lang('CONVERT_URL_ERRMSG');
				if(results && results.status_code) msg += ' [ '+ results.status_code +' ]';
				Ext.MessageBox.show({
					title   : aOpts.title,
					msg     : msg,
					buttons : Ext.MessageBox.OK,
					icon    : Ext.MessageBox.ERROR
				});
				return;
			}
			if(Ext.isEmpty(results.sp_alone_url) || Ext.isEmpty(results.sp_segment_url) || Ext.isEmpty(results.sp_whole_url)){
				var msg = get_ag_lang('CONVERT_URL_ERRMSG');
				if(results && results.status_code) msg += ' [ no data ]';
				Ext.MessageBox.show({
					title   : aOpts.title,
					msg     : msg,
					buttons : Ext.MessageBox.OK,
					icon    : Ext.MessageBox.ERROR
				});
				return;
			}

			self.__urls_shoft = {
				sp_alone_url : [],
				sp_segment_url : [],
				sp_whole_url : []
			};
			Ext.each(results.sp_alone_url,function(r,i,a){
				if(Ext.isEmpty(r) || Ext.isEmpty(r.result) || Ext.isEmpty(r.result.status_code) || r.result.status_code != 200 || Ext.isEmpty(r.result.data) || Ext.isEmpty(r.result.data.url)) return true;
				self.__urls_shoft.sp_alone_url.push(r.result.data.url);
			});
			Ext.each(results.sp_segment_url,function(r,i,a){
				if(Ext.isEmpty(r) || Ext.isEmpty(r.result) || Ext.isEmpty(r.result.status_code) || r.result.status_code != 200 || Ext.isEmpty(r.result.data) || Ext.isEmpty(r.result.data.url)) return true;
				self.__urls_shoft.sp_segment_url.push(r.result.data.url);
			});
			Ext.each(results.sp_whole_url,function(r,i,a){
				if(Ext.isEmpty(r) || Ext.isEmpty(r.result) || Ext.isEmpty(r.result.status_code) || r.result.status_code != 200 || Ext.isEmpty(r.result.data) || Ext.isEmpty(r.result.data.url)) return true;
				self.__urls_shoft.sp_whole_url.push(r.result.data.url);
			});
			Ext.getCmp('ag-sp-alone-url-textarea').setValue(self.__urls_shoft.sp_alone_url.join("\n"));
			Ext.getCmp('ag-sp-segment-url-textarea').setValue(self.__urls_shoft.sp_segment_url.join("\n"));
			Ext.getCmp('ag-sp-whole-url-textarea').setValue(self.__urls_shoft.sp_whole_url.join("\n"));
		},
		failure : function(conn,response,options){
			Ext.MessageBox.show({
				title   : aOpts.title,
				msg     : get_ag_lang('CONVERT_URL_ERRMSG'),
				buttons : Ext.MessageBox.OK,
				icon    : Ext.MessageBox.ERROR
			});
		}
	});

	var copyWindow = new Ext.Window({
		animateTarget: aOpts.animEl || aOpts.animateTarget,
		iconCls     : aOpts.iconCls,
		title       : aOpts.title,
		width       : 400,
		height      : 532,
		minWidth    : 400,
		minHeight   : 532,
		plain       : true,
		buttonAlign :'center',
		modal       : true,
		bodyStyle   : 'background:transparent;',
		layout      : 'fit',
		items       : [{
			layout: 'form',
			border: false,
			bodyStyle   :'background:transparent;padding:5px;',
			labelAlign: 'top',
			defaultType: 'textarea',
			defaults: {
				width: 374,
				height: 116,
				selectOnFocus: true
			},
			items: [{
				id: 'ag-sp-alone-url-textarea',
				fieldLabel: 'SINGLE-PIN URL (Pin alone)',
				value: sp_alone_url
			},{
				id: 'ag-sp-segment-url-textarea',
				fieldLabel: 'SINGLE-PIN URL (Pin on a segment)',
				value: sp_segment_url
			},{
				id: 'ag-sp-whole-url-textarea',
				fieldLabel: 'SINGLE-PIN URL (Pin on a whole model)',
				value: sp_whole_url
			},{
				hideLabel: true,
				xtype: 'checkbox',
				height: null,
				checked: false,
				boxLabel : 'Elongate URL to original configuration for parsing.',
				listeners : {
					check: function(checkbox,checked){
						_dump("check():["+checkbox.id+"]["+checked+"]");
						if(!checked){
							Ext.getCmp('ag-sp-alone-url-textarea').setValue(self.__urls_shoft.sp_alone_url.join("\n"));
							Ext.getCmp('ag-sp-segment-url-textarea').setValue(self.__urls_shoft.sp_segment_url.join("\n"));
							Ext.getCmp('ag-sp-whole-url-textarea').setValue(self.__urls_shoft.sp_whole_url.join("\n"));
						}else{
							Ext.getCmp('ag-sp-alone-url-textarea').setValue(self.__sp_alone_url.join("\n"));
							Ext.getCmp('ag-sp-segment-url-textarea').setValue(self.__sp_segment_url.join("\n"));
							Ext.getCmp('ag-sp-whole-url-textarea').setValue(self.__sp_whole_url.join("\n"));
						}
					}
				}
			}]
		}],
		buttons: [{
			text: 'OK',
			handler: function(){
				copyWindow.close();
			}
		}]
	});
	copyWindow.show();

};

Ext.onReady(function(){
	ag_extensions.single_pin._init();
});
