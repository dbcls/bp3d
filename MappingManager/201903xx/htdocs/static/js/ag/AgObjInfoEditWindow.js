Ext.define('Ext.ag.ObjInfoEditWindow', {
	extend: 'Ext.window.Window',

	width: 300,
	height: 300,

	minWidth: 300,
	minHeight: 250,

	constructor: function (config) {
		var me = this;
		me.callParent(arguments);
	},

	initComponent: function() {
		var me = this;
		var baseId = me.id;

//		console.log(me);
/*
		me.store = Ext.create('Ext.data.Store', {
			model: 'PARTS',
			proxy: {
				type: 'memory',
			},
			listeners: {
				add: function(store,records,index,eOpts){
//					console.log("me.store.add()");
				},
				remove: function(store,record,index,eOpts){
//					console.log("me.store.remove()");
				},
				update: function(store,record,operation){
//					console.log("me.store.update():"+operation);
//					console.log(record);
				},
				beforeload: function(store, operation, eOpts){
//					console.log("me.store.beforeload()");
				},
				load: function(store, operation, eOpts){
//					console.log("me.store.load()");
				},
				beforesync: function(options, eOpts){
//					console.log("me.store.beforesync()");
				},
				write: function(store, operation, eOpts){
//					console.log("me.store.write()");
				}
			}
		});
		me.store.loadData(me.initialConfig.records);
		console.log(me.store.getRange());
*/

		me.closable = false;
		me.layout = 'fit';
		me.items = [{
			xtype: 'fieldcontainer',
			layout: {
				type: 'hbox',
				align: 'stretch',
				pack: 'center'
			},
//			defaultType: 'panel',
			items: [{
				hidden: false,
				xtype:'fieldcontainer',
				minWidth: 112,
				minHeight: 108,
				flex: 1,
				style: {
					margin: '4px 0 0 4px'
				},
				listeners: {
					afterrender: function( field, eOpts ){
//						console.log('afterrender');
						if(field.hidden) return;

						if(Ext.isEmpty(self.webglRenderer)){
							self.webglRenderer = new AgMiniRenderer({width:108,height:108,rate:1});
						}else{
							self.webglRenderer.domElement.style.display = '';
						}
						field.layout.innerCt.dom.appendChild( self.webglRenderer.domElement );

						var params = [];
						Ext.Array.each(me.initialConfig.records || [], function(record){
							params.push({
								url: Ext.String.format('{0}?{1}',record.get('art_path'),record.get('art_timestamp').getTime()),
								color: record.get('color'),
								opacity: record.get('opacity'),
								visible: record.get('remove') ? false : true
							});
						});
						self.webglRenderer.loadObj(params, function(){});
					},
					resize: function( field, width, height, oldWidth, oldHeight, eOpts ){
//						console.log('resize', width, height);
						self.webglRenderer.setSize(width-4, height-4);
					}
				}
			},{
//				title: 'b',
				flex: 1.5,
				xtype: 'form',
				trackResetOnLoad: true,
				frame: true,
				border: false,
//				bodyPadding: '0 5 0 0',
				defaultType: 'textfield',
				defaults: {
					labelAlign: 'top',
					anchor: '100%',
					selectOnFocus: true,
					enableKeyEvents: true,
					listeners: {
						change: {
							fn: function(field,newValue,oldValue,eOpts){
//								console.log('change',field,newValue,oldValue,eOpts);

								Ext.Array.each(me.initialConfig.records || [], function(record){
									var key = field.name;
									var value = newValue;//record.get(key);
									if(Ext.isString(value) && Ext.isEmpty(Ext.String.trim(value))) value = null;
									if(record.get(key) === value) return true;

									record.beginEdit();
									record.set(key, value);
									record.endEdit(false, [key]);

//									console.log(record.getData());
								});
							},
							buffer: 250

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
				},

				items: [{
					fieldLabel: AgLang.category,
					name: 'arta_category',
				},{
					fieldLabel: AgLang.class_name,
					name: 'arta_class',
				},{
					fieldLabel: AgLang.comment,
					name: 'arta_comment',
				},{
					fieldLabel: AgLang.judge,
					name: 'arta_judge',
				}],

				listeners: {
					afterrender: function( field, eOpts ){
						if(field.hidden) return;

						var values = {};
						Ext.Array.each(me.initialConfig.records || [], function(record){
							Ext.Object.each(record.getData(), function(key,value){
								if(Ext.isDefined(values[key])){
									if(values[key] !== value) values[key] = null;
								}
								else{
									values[key] = value;
								}
							});
						});
						field.getForm().setValues(values);

					}
				}



			}]
		}];

		me.buttons = [{
			text: 'reset',
			handler : function(b){
				var store;
				var modifiedRecords;
				if(Ext.isArray(me.initialConfig.records) && me.initialConfig.records.length>0){
					store = me.initialConfig.records[0].store;
					modifiedRecords = store.getModifiedRecords();
				}
				if(Ext.isArray(modifiedRecords) && modifiedRecords.length>0){
					b.up('window').down('form').getForm().reset();
					store.rejectChanges();
				}
			}
		},'->',{
			text: 'submit',
			handler : function(b){
//				var values = b.up('window').down('form').getForm().getValues();
//				console.log(values);

				var win = b.up('window');
				win.setLoading(true);

				var store;
				var modifiedRecords;
				if(Ext.isArray(me.initialConfig.records) && me.initialConfig.records.length>0){
					store = me.initialConfig.records[0].store;
					modifiedRecords = store.getModifiedRecords();
				}
				if(Ext.isArray(modifiedRecords) && modifiedRecords.length>0){
					store.sync({
						callback: function(batch,options){
							win.setLoading(false);
						},
						success: function(batch,options){
							b.up('window').close();
						},
						failure: function(batch,options){
							console.log(this);
							var proxy = this;
							var reader = proxy.getReader();
							var jsonData = reader.jsonData;
							var msg = '';
							if(Ext.isObject(jsonData) && Ext.isString(jsonData.msg) && jsonData.msg.length){
								msg = jsonData.msg;
							}
							else{
								if(batch.hasException){
									for(var i = 0; i < batch.exceptions.length; i ++ ){
										switch(batch.exceptions[i].action){
											case "destroy" :
												msg = msg + batch.exceptions[i].records.length + " Delete, ";
												break;
											case "update" :
												msg = msg + batch.exceptions[i].records.length + " Update, ";
												break;
											case "create" :
												msg = msg + batch.exceptions[i].records.length + " Create, ";
												break;
										}
									}
								}
								else{
									msg = 'Changes failed.';
								}
							}
							Ext.MessageBox.show({
								title: 'Error',
								msg: msg,
								icon: Ext.MessageBox.ERROR,
								buttons: Ext.MessageBox.OK
							});
						}
					});
				}
				else{
					b.up('window').close();
				}
			}
		},{
			text: 'close',
			handler : function(b){
				var win = b.up('window');
				var store;
				var modifiedRecords;
				if(Ext.isArray(me.initialConfig.records) && me.initialConfig.records.length>0){
					store = me.initialConfig.records[0].store;
					modifiedRecords = store.getModifiedRecords();
				}
				if(Ext.isArray(modifiedRecords) && modifiedRecords.length>0){
					win.down('form').getForm().reset();
					store.rejectChanges();
				}
				win.close();
			}
		}];

		me.callParent();
	}

});
