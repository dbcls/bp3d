window.ag_extensions = window.ag_extensions || {};
ag_extensions.import_parts_pins = ag_extensions.import_parts_pins || {};

ag_extensions.import_parts_pins.openWindow = function(aOpts){
	aOpts = Ext.apply({},aOpts||{},{
		title    : 'Import',
		width    : 500,
		height   : 324,
		plain    : true,
		modal    : true,
		resizable: false,
		animateTarget: null
	});

	var bp3d_version_combo = Ext.getCmp('bp3d-version-combo');
	var bp3d_version_store = bp3d_version_combo.getStore();
	var bp3d_version_idx = bp3d_version_store.find('tgi_version',new RegExp('^'+bp3d_version_combo.getValue()+'$'));
	var bp3d_version_rec;
	var bp3d_version_disp_value;
	if(bp3d_version_idx>=0) bp3d_version_rec = bp3d_version_store.getAt(bp3d_version_idx);
	if(bp3d_version_rec) bp3d_version_disp_value = bp3d_version_rec.get('tgi_name');

	var bp3d_tree_combo = Ext.getCmp('bp3d-tree-type-combo');
	var bp3d_tree_store = bp3d_tree_combo.getStore();
	var bp3d_tree_idx = bp3d_tree_store.find('t_type',new RegExp('^'+bp3d_tree_combo.getValue()+'$'));
	var bp3d_tree_rec;
	var bp3d_tree_disp_value;
	if(bp3d_tree_idx>=0) bp3d_tree_rec = bp3d_tree_store.getAt(bp3d_tree_idx);
	if(bp3d_tree_rec) bp3d_tree_disp_value = bp3d_tree_rec.get('bul_abbr');

	var convOpts = {
		target: {
			common: false,
			camera: false,
			clip: false,
			parts: true,
			point_parts: false,
			legendinfo: false,
			pins: true
		}
	};

	function add_text(text,aOpt){
		aOpt = aOpt || {};
		var aCB = aOpt.callback;
		var value="";
		var arr = text.replace(/0x0d0x0a|0x0d|0x0a|\r\n/g,"\n").split("\n");
		var url_arr = [];
		var text_arr = [];
		var addPartsRecs = [];
		for(var i=0;i<arr.length;i++){
			var trim_str = arr[i].trim();
			if(trim_str.length==0) continue;
			if(trim_str.indexOf('http')==0){
				url_arr.push(arr[i]);
			}else if(trim_str.search(/[\?&]*pno[0-9]{3}=/)>=0){
				url_arr.push(arr[i]);
			}else{
				text_arr.push(arr[i]);
			}
		}
		if(window.ag_extensions && ag_extensions.toJSON && ag_extensions.toJSON.JSONStr2URI){
			if(url_arr.length>0){
				for(var i=0;i<url_arr.length;i++){
					var trim_str = url_arr[i].trim();
					if(trim_str.length==0) continue;
					if(trim_str.search(/\?([\[\{].+)$/)>=0){
						var urlObj = Ext.urlDecode(RegExp.$1);
						var jsonStr;
						for(var key in urlObj){
							if(key.search(/^[\[\{]/)>=0){
								jsonStr = key;
								break;
							}
						}
						if(jsonStr){
							var rtn_url = ag_extensions.toJSON.JSONStr2URI(jsonStr);
							var rtn_text;
							if(rtn_url) rtn_text = URI2Text(rtn_url);
							if(rtn_text) url_arr[i] = Text2URI(rtn_text,convOpts);
						}
					}
					else if(trim_str.search(/\?(%7B|%5B)(.+)$/)>=0){
						var urlObj = Ext.urlDecode(RegExp.$1+RegExp.$2);
						var jsonStr;
						for(var key in urlObj){
							if(key.search(/^[\[\{]/)>=0){
								jsonStr = key;
								break;
							}
						}
						if(jsonStr){
							var rtn_url = ag_extensions.toJSON.JSONStr2URI(jsonStr);
							var rtn_text;
							if(rtn_url) rtn_text = URI2Text(rtn_url);
							if(rtn_text) url_arr[i] = Text2URI(rtn_text,convOpts);
						}
					}
				}
			}
		}
		if(text_arr.length>0){
			if(window.ag_extensions && ag_extensions.toJSON && ag_extensions.toJSON.JSONStr2URI){
				var rtn_url = ag_extensions.toJSON.JSONStr2URI(text_arr.join(""));
				var rtn_text;
				if(rtn_url) rtn_text = URI2Text('?'+rtn_url);
				if(rtn_text) text_arr = [rtn_text];
			}
			url_arr.push(Text2URI(text_arr.join("\n"),convOpts));
		}

		function add_items(params){
			if(Ext.isEmpty(params)) return addrecs;
			if(!params.tp_ap) params.tp_ap = Ext.urlEncode(params);
			if(convOpts.target.parts) addPartsRecs = addPartsRecs.concat(add_bp3d_parts_store_parts_from_TPAP(params.tp_ap));
			if(convOpts.target.pins) add_comment_store_pins_from_TPAP(params.tp_ap);
		}

		function add_store(arr,idx){
			if(Ext.isEmpty(idx)) idx = 0;

			for(;idx<arr.length;idx++){
				var url = arr[idx].trim();
//				if(url.indexOf('http')!=0) continue;

//				if(window.ag_extensions && ag_extensions.toJSON && ag_extensions.toJSON.URI2JSON){
//					var search = url;
//					if(url.indexOf("?")>=0) search = url.replace(/^.*\?(.*)$/g,"$1");
//					var urlObj = Ext.urlDecode(search);
//					if(urlObj.tp_ap) search = urlObj.tp_ap;
//					if(search){
//						console.log(search);
//						var jsonObj = ag_extensions.toJSON.URI2JSON(search,true);
//						if(jsonObj) console.log(Ext.util.JSON.encode(jsonObj));
//					}
//				}

				var search = "";
				if(url.indexOf("?")>=0){
					search = url.replace(/^.+\?(.*)$/g,"$1");
				}else if(url.search(/[\?&]*pno[0-9]{3}=/)>=0){
					search = url;
				}
				if(Ext.isEmpty(search)) continue;
				var params = Ext.urlDecode(search);
				if(params.shorten){

					var window_title = aOpts.title;
					Ext.Ajax.request({
						url     : 'get-convert-url.cgi',
						method  : 'POST',
						params  : Ext.urlEncode({url:url}),
						success : function(conn,response,options){
							try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
							if(Ext.isEmpty(results) || Ext.isEmpty(results.status_code) || results.status_code!=200){
								var msg = 'URL変換エラー';
								if(results && results.status_code) msg += ' [ '+ results.status_code +' ]';
								for(var key in results){
									_dump("1:["+key+"]=["+results[key]+"]");
								}
								if(aCB) (aCB)(false,addPartsRecs);
								Ext.MessageBox.show({
									title   : window_title,
									msg     : msg,
									buttons : Ext.MessageBox.OK,
									icon    : Ext.MessageBox.ERROR
								});
								return;
							}
							if(Ext.isEmpty(results.data)){
								if(aCB) (aCB)(false,addPartsRecs);
								var msg = 'URL変換エラー';
								if(results && results.status_code) msg += ' [ no data ]';
								Ext.MessageBox.show({
									title   : window_title,
									msg     : msg,
									buttons : Ext.MessageBox.OK,
									icon    : Ext.MessageBox.ERROR
								});
								return;
							}
							if(!Ext.isEmpty(results.data.url)){//shortURLに変換
								return;
							}
							if(!Ext.isEmpty(results.data.expand)){//longURLに変換
								var search;
								if(Ext.isArray(results.data.expand)){
									search = results.data.expand[0].long_url;
								}else{
									search = results.data.expand.long_url;
								}
								if(search){
									if(search.indexOf("?")>=0){
										search = search.replace(/^.+\?(.*)$/g,"$1");
									}else if(search.search(/[&]*pno[0-9]{3}=/)>=0){
									}else{
										search = undefined;
									}
								}
								if(search){
									if(search.search(/^([\[\{].+)$/)>=0){
										var urlObj = Ext.urlDecode(RegExp.$1);
										var jsonStr;
										for(var key in urlObj){
											if(key.search(/^[\[\{]/)>=0){
												jsonStr = key;
												break;
											}
										}
										if(jsonStr){
											var rtn_url = ag_extensions.toJSON.JSONStr2URI(jsonStr,{toString:false});
											if(rtn_url) search = Ext.urlEncode(rtn_url);
										}
									}
									else if(search.search(/^(%7B|%5B)(.+)$/)>=0){
										var urlObj = Ext.urlDecode(RegExp.$1+RegExp.$2);
										var jsonStr;
										for(var key in urlObj){
											if(key.search(/^[\[\{]/)>=0){
												jsonStr = key;
												break;
											}
										}
										if(jsonStr){
											var rtn_url = ag_extensions.toJSON.JSONStr2URI(jsonStr,{toString:false});
											if(rtn_url) search = Ext.urlEncode(rtn_url);
										}
									}
									add_items(Ext.urlDecode(search));
								}
								add_store(arr,++idx);
								return;
							}
						},
						failure : function(conn,response,options){
							if(aCB) (aCB)(false,addPartsRecs);
							Ext.MessageBox.show({
								title   : window_title,
								msg     : 'URL変換エラー',
								buttons : Ext.MessageBox.OK,
								icon    : Ext.MessageBox.ERROR
							});
						}
					});

					return;
				}else{
					add_items(params);
				}
			}
			if(aCB) (aCB)(true,addPartsRecs);
			return;
		}

		if(aOpt.clear){
			if(convOpts.target.parts) bp3d_parts_store.removeAll();
			if(convOpts.target.pins) ag_comment_store.removeAll();
		}

		add_store(url_arr);

		return;
	}

	function change_checked(field,checked){
		convOpts.target[field.name] = checked;
	}

	var ag_import_textarea_id = Ext.id();
	var win = new Ext.Window({
		title       : aOpts.title,
		animateTarget: aOpts.animateTarget,
		width       : aOpts.width,
		height      : aOpts.height,
		plain       : aOpts.plain,
		bodyStyle   : 'padding:5px;',
		buttonAlign : 'right',
		modal       : aOpts.modal,
		resizable   : aOpts.resizable,
		items: [{
			anchor: '100%',
			border: false,
			bodyStyle: 'background:transparent;',
			layout: 'table',
			layoutConfig: {
				columns: 3
			},
			items:[{
				xtype: 'label',
				width: 160,
				style: 'font:bold 11px tahoma,arial,helvetica,sans-serif;color:#15428b;',
				html: 'Paste http request or Table&nbsp;&nbsp;'
			},{
				xtype: 'checkbox',
				boxLabel: 'Parts',
				name: 'parts',
				checked: convOpts.target.parts,
				width: 60,
				listeners: {
					check: change_checked
				}
			},{
				xtype: 'checkbox',
				boxLabel: 'Pins',
				name: 'pins',
				checked: convOpts.target.pins,
				width: 60,
				listeners: {
					check: change_checked
				}
			}]
		},{
			xtype: 'textarea',
			id: ag_import_textarea_id,
			style: 'font-family:Courier;monospace;',
			selectOnFocus: true,
			allowBlank : false,
			hideLabel: true,
			emptyText: '',
			width: 474,
			height: 220
		}],
		buttons : [{
			text: 'Add to present pallet',
			handler: function(){
				var b = this;
				var ag_import_textarea = Ext.getCmp(ag_import_textarea_id);
				if(ag_import_textarea.validate()){
					if(convOpts.target.parts || convOpts.target.pins){
						b.setDisabled(true);
						win.loadMask.show();
						setTimeout(function(){
							var text = ag_import_textarea.getValue();
							add_text(text,{
								clear: false,
								callback: function(success,addPartsRecs){
									if(success){
										if(addPartsRecs.length) getConvertIdList(addPartsRecs,bp3d_parts_store);
										win.close();
									}else{
										win.loadMask.hide();
										b.setDisabled(false);
									}
								}
							});
						},100);
					}else{
						win.loadMask.hide();
					}
				}else{
					ag_import_textarea.focus();
				}
			}
		},{
			text: 'Replace with present pallet',
			handler: function(){
				var b = this;
				var ag_import_textarea = Ext.getCmp(ag_import_textarea_id);
				if(ag_import_textarea.validate()){
					if(convOpts.target.parts || convOpts.target.pins){
						b.setDisabled(true);
						win.loadMask.show();
						setTimeout(function(){
							var text = ag_import_textarea.getValue();
							add_text(text,{
								clear: true,
								callback: function(success,addPartsRecs){
									if(success){
										if(addPartsRecs.length) getConvertIdList(addPartsRecs,bp3d_parts_store);
										win.close();
									}else{
										win.loadMask.hide();
										b.setDisabled(false);
									}
								}
							});
						},100);
					}else{
						win.loadMask.hide();
					}
				}else{
					ag_import_textarea.focus();
				}
			}
		},{
			text: 'Cancel',
			handler: function(){
				win.close();
			}
		}],
		listeners : {
			render: function(comp){
				comp.loadMask = new Ext.LoadMask(comp.body,{removeMask:false});
			}
		}
	});
	win.show();
};
