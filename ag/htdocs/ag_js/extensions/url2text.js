window.ag_extensions = window.ag_extensions || {};
ag_extensions.url2text = ag_extensions.url2text || {};

ag_extensions.url2text.openWindow = function(aOpts){
	aOpts = aOpts || {};

	var cur_text = URI2Text(glb_anatomo_editor_url,{target:{pins:false}});
	var cur_url = Text2URI(cur_text,{target:{pins:false}});
	var convOpts = {
		pin: {
			url_prefix : cur_url+encodeURIComponent('&')
		}
	};

	var text_value = URI2Text(glb_anatomo_editor_url,convOpts);
	if(Ext.isEmpty(text_value)) return;

	var json_value;
	var json_hidden=true;
	var text_height=290;
	if(true && window.ag_extensions && ag_extensions.toJSON && ag_extensions.toJSON.URI2JSON){
		json_value = ag_extensions.toJSON.URI2JSON(glb_anatomo_editor_url,{toString:{},callback:function(value){
			json_value = value;
			var textCmp = Ext.getCmp('ag_json_editor');
			if(textCmp && textCmp.rendered){
				textCmp.setValue(json_value);
			}else{
				var runner = new Ext.util.TaskRunner();
				var task = {
					run: function(json_value){
						var textCmp = Ext.getCmp('ag_json_editor');
						if(textCmp && textCmp.rendered){
							textCmp.setValue(json_value);
							runner.stop(task);
						}
					},
					args: [json_value],
					interval: 1000 //1 second
				}
				runner.start(task);
			}
		}});
		json_hidden=false;
		text_height=119;
	}

	var anatomo_url_window = new Ext.Window({
		animateTarget: aOpts.animEl || aOpts.animateTarget,
		iconCls     : aOpts.iconCls,
		title       : aOpts.title,
		width       : 600,
		height      : 500,
		layout      : 'form',
		plain       : true,
		bodyStyle   : 'padding:5px;text-align:right;',
		buttonAlign : 'center',
		modal       : true,
		resizable   : false,
		labelAlign  : 'left',
		labelWidth  : 24,
		items       : [
		{
			xtype         : 'textarea',
			id            : 'ag_url_textarea',
			fieldLabel    : 'URL',
			anchor        : '100%',
//			height        : 100,
			height        : 50,
			selectOnFocus : false,
			value         : glb_anatomo_editor_url
		},
		{
			layout:'table',
			border: false,
			width: '100%',
			bodyStyle: 'background-color: transparent;',
			layoutConfig: {
				columns: 2
			},
			items:[{
				hidden: true,
				xtype: 'button',
				text: 'URL to Table',
				handler: function(){
//						var url_arr = Ext.getCmp('ag_url_textarea').getValue().replace(/0x0d0x0a|0x0d|0x0a|\r\n/g,"\n").replace(/\n$/g,"").split("\n");
//						for(var i=0;i<url_arr.length;i++){
//							var rtnstr = URI2Text(url_arr[i],convOpts);
//							if(Ext.isEmpty(rtnstr)) continue;
//							Ext.getCmp('ag_url_editor').setValue(rtnstr);
//							break;
//						}

					var url_arr = Ext.getCmp('ag_url_textarea').getValue().replace(/0x0d0x0a|0x0d|0x0a|\r\n/g,"\n").replace(/\n$/g,"").split("\n");
					for(var i=0;i<url_arr.length;i++){
						url_arr[i] = url_arr[i].trim();
						if(Ext.isEmpty(url_arr[i])) continue;
						var idx = url_arr[i].indexOf("?");
						if(idx<0) continue;
						var search = url_arr[i].substr(idx+1);
						if(Ext.isEmpty(search)) continue;
						var params = Ext.urlDecode(search);
						if(params.shorten){
							update_open_ShortURL2LongURL(url_arr[i],function(long_url){
								var rtnstr = URI2Text(long_url,convOpts);
								if(Ext.isEmpty(rtnstr)) return;
								Ext.getCmp('ag_url_editor').setValue(rtnstr);
							});
							break;
						}else{
							var rtnstr = URI2Text(url_arr[i],convOpts);
							if(Ext.isEmpty(rtnstr)) continue;
							Ext.getCmp('ag_url_editor').setValue(rtnstr);
							break;
						}
					}

				}
			},{
				xtype: 'button',
				text: 'Open this URL',
				handler: function(){
					var url_arr = Ext.getCmp('ag_url_textarea').getValue().replace(/0x0d0x0a|0x0d|0x0a|\r\n/g,"\n").replace(/\n$/g,"").split("\n");
					for(var i=0;i<url_arr.length;i++){
						var rtnstr = url_arr[i];
						rtnstr = rtnstr.replace(/\r|\n/g,"").trim();
						if(Ext.isEmpty(rtnstr)) continue;
						Ext.getDom('ag-open-url-form-url').value = rtnstr;
						Ext.getDom('ag-open-url-form').submit();
						break;
					}
				}
			}],
			listeners: {
				render: {
					fn: function(comp){
						_dump("render():["+comp.id+"]");
						var table = $(comp.body.dom).children('table.x-table-layout');
						_dump(table);
						table.css({width:'100%'}).find('td.x-table-layout-cell:eq(1)').attr({align:'right'});
					},
					buffer: 250
				}
			}
		},
		{
			border: true,
			bodyStyle: 'background-color: transparent;',
			tbar:['<label style="font-size:11px;font-weight:bold;color:#15428b;line-height:21px;">Table</label>','->'],
			bbar:[{
				text: 'URL to Table',
				handler: function(){
					var url_arr = Ext.getCmp('ag_url_textarea').getValue().replace(/0x0d0x0a|0x0d|0x0a|\r\n/g,"\n").replace(/\n$/g,"").split("\n");
					for(var i=0;i<url_arr.length;i++){
						url_arr[i] = url_arr[i].trim();
						if(Ext.isEmpty(url_arr[i])) continue;
						var idx = url_arr[i].indexOf("?");
						if(idx<0) continue;
						var search = url_arr[i].substr(idx+1);
						if(Ext.isEmpty(search)) continue;
						var params = Ext.urlDecode(search);
						if(params.shorten){
							update_open_ShortURL2LongURL(url_arr[i],function(long_url){
								var rtnstr = URI2Text(long_url,convOpts);
								if(Ext.isEmpty(rtnstr)) return;
								Ext.getCmp('ag_url_editor').setValue(rtnstr);
							});
							break;
						}else{
							var rtnstr = URI2Text(url_arr[i],convOpts);
							if(Ext.isEmpty(rtnstr)) continue;
							Ext.getCmp('ag_url_editor').setValue(rtnstr);
							break;
						}
					}
				}
			},'-','->','-',{
				text     : 'Table to URL',
				disabled : false,
				handler : function(){
					var rtnstr = Text2URI(Ext.getCmp('ag_url_editor').getValue());
					Ext.getCmp('ag_url_textarea').setValue(rtnstr);
					update_open_url2text(rtnstr,function(url){
						Ext.getCmp('ag_url_textarea').setValue(url);
					});
				}
			}],
			anchor    : '100%',
			layout: 'anchor',
			items:{
				xtype     : 'textarea',
				id        : 'ag_url_editor',
				style     : 'font-family:Courier;monospace;',
				hideLabel : true,
				value     : text_value,
				anchor    : '100%',
				height: text_height
			}
		},
		{
			hidden:true,
			xtype    : 'button',
			text     : 'Table to URL',
			disabled : false,
			handler : function(){
				var rtnstr = Text2URI(Ext.getCmp('ag_url_editor').getValue());
				Ext.getCmp('ag_url_textarea').setValue(rtnstr);
				update_open_url2text(rtnstr,function(url){
					Ext.getCmp('ag_url_textarea').setValue(url);
				});
			}
		},
		{
			hidden: json_hidden,
			border: true,
			bodyStyle: 'background-color: transparent;',
			tbar: ['<label style="font-size:11px;font-weight:bold;color:#15428b;line-height:21px;">JSON</label>','->'],
			bbar:[{
				text: 'URL to JSON',
				handler: function(){
					var url_arr = Ext.getCmp('ag_url_textarea').getValue().replace(/0x0d0x0a|0x0d|0x0a|\r\n/g,"\n").replace(/\n$/g,"").split("\n");
					for(var i=0;i<url_arr.length;i++){
						url_arr[i] = url_arr[i].trim();
						if(Ext.isEmpty(url_arr[i])) continue;
						var idx = url_arr[i].indexOf("?");
						if(idx<0) continue;
						var search = url_arr[i].substr(idx+1);
						if(Ext.isEmpty(search)) continue;
						var params = Ext.urlDecode(search);
						if(params.shorten){
							update_open_ShortURL2LongURL(url_arr[i],function(long_url){
								var rtnstr = ag_extensions.toJSON.URI2JSON(long_url,{toString:{},callback:function(value){
									Ext.getCmp('ag_json_editor').setValue(value);
								}});
								if(Ext.isEmpty(rtnstr)) return;
								Ext.getCmp('ag_json_editor').setValue(rtnstr);
							});
							break;
						}else{
							var rtnstr = ag_extensions.toJSON.URI2JSON(url_arr[i],{toString:{},callback:function(value){
								Ext.getCmp('ag_json_editor').setValue(value);
							}});
							if(Ext.isEmpty(rtnstr)) continue;
							Ext.getCmp('ag_json_editor').setValue(rtnstr);
							break;
						}
					}
				}
			},'-','->','-',{
				text     : 'JSON to URL',
				disabled : false,
				handler : function(){
					var rtnstr = ag_extensions.toJSON.JSONStr2URI(Ext.getCmp('ag_json_editor').getValue());
					Ext.getCmp('ag_url_textarea').setValue(rtnstr);
					update_open_url2text(rtnstr,function(url){
						Ext.getCmp('ag_url_textarea').setValue(url);
					});
				}
			}],
			anchor: '100%',
			layout: 'anchor',
			items:{
				xtype     : 'textarea',
				id        : 'ag_json_editor',
				style     : 'font-family:Courier;monospace;',
				hideLabel : true,
				value     : json_value,
				anchor    : '100%',
				height: text_height
			}
		}
		],
		buttons : [{
			text    : 'Close',
			handler : function(){
				anatomo_url_window.close();
			}
		}],
		listeners: {
			render: function(){
				var long_url = Ext.getCmp('ag_url_textarea').getValue();
				update_open_url2text(long_url,function(url){
					Ext.getCmp('ag_url_textarea').setValue(url);
				});
			}
		}
	});
	anatomo_url_window.show();
};
