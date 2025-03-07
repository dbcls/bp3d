var AgPalletUtils = {
	makeCopyListText : function(copy_type,records){
		try{
			var copy_type_obj;
			if(copy_type=='csv'){
				copy_type_obj = AgUtils.CSVData;
			}else if(copy_type=='tab'){
				copy_type_obj = AgUtils.TabData;
			}

			var copyText = "";
			if(copy_type_obj){
				var column = [];
				column = [];
				Ext.iterate(records[0].data,function(key,i2,data){
					column.push(copy_type_obj.escape(key));
				});
				copyText += column.join(copy_type_obj.colDelimiter)+"\n";

				Ext.iterate(records,function(record,i1,a1){
					column = [];
					Ext.iterate(record.data,function(key,i2,data){
						if(Ext.isDate(data[key])){
							column.push(copy_type_obj.escape(data[key].getTime()));
						}else{
							column.push(copy_type_obj.escape(data[key]));
						}
					});
					copyText += column.join(copy_type_obj.colDelimiter)+"\n";
				});

			}
			return copyText;
		}catch(e){
			AgPalletUtils._error("makeCopyListText():"+e);
		}
	},

	copyListRecords : null,
	copyListWindow : null,
	copyListTextareafield : null,
	copyListCB : function(records,title){
		AgPalletUtils.copyListRecords = records;
		if(!AgPalletUtils.copyListWindow){
			if(!title) title = 'Copy';
			AgPalletUtils.copyListWindow = Ext.create('Ext.window.Window', {
				title       : title,
				width       : 600,
				height      : 300,
//				layout      : 'form',
//				plain       : true,
				bodyStyle   : 'padding:5px;text-align:right;',
				buttonAlign : 'center',
				modal       : true,
				resizable   : true,
				closeAction : 'hide',
				layout      : 'anchor',
				items       : [{
					xtype      : 'radiogroup',
					fieldLabel : 'Copy Type',
					labelWidth  : 68,
					columns    : 2,
					height     : 22,
					anchor     : '100%',
					defaults   : {
						name:'copy-list-type'
					},
					items      : [{
						boxLabel   : 'Tab-Separated Values',
						inputValue : 'tab',
						checked    : true
					},{
						boxLabel   : 'Comma-Separated Values',
						inputValue : 'csv'
					}],
					listeners  : {
						change : function(field,newValue,oldValue,eOpts){
							AgPalletUtils.copyListTextareafield.setValue(AgPalletUtils.makeCopyListText(newValue['copy-list-type'],AgPalletUtils.copyListRecords));
//							AgPalletUtils._dump(newValue);
						}
					}
				},{
					xtype         : 'textareafield',
					hideLabel     : true,
					anchor        : '100% -25',
					selectOnFocus : true,
					disabled      : false,
					value         : "",
					listeners  : {
						specialkey : function(f, e){
							e.stopPropagation();
						}
					}
				}],
				buttons : [{
					text    : 'OK',
					handler : function(){
						AgPalletUtils.copyListWindow.hide();
					}
				}],
				listeners : {
					beforeshow : function(win,eOpts){
						try{
							var textareafield;
							var radiofield;
							var num1 = win.items.getCount();
							for(var i=0;i<num1;i++){
								var item1 = win.items.getAt(i);
								if(item1.getXType()=='radiogroup'){
									var num2 = item1.items.getCount();
									for(var j=0;j<num2;j++){
										var item2 = item1.items.getAt(j);
										if(item2.getXType()=='radiofield'){
											if(item2.getValue()){
//												AgPalletUtils._dump("item2.getValue()=["+item2.getValue()+"]");
//												AgPalletUtils._dump("item2.getRawValue()=["+item2.getRawValue()+"]");
												radiofield = item2;
												break;
											}
										}
									}
								}else if(item1.getXType()=='textareafield'){
									textareafield = item1;
								}
							}
							if(radiofield && textareafield){
								textareafield.setValue(AgPalletUtils.makeCopyListText(radiofield.inputValue,AgPalletUtils.copyListRecords));
								AgPalletUtils.copyListTextareafield = textareafield;
							}
						}catch(e){
							AgPalletUtils._error(e);
						}
					}
				}
			});
		}
		Ext.defer(function(){
			try{
				AgPalletUtils.copyListWindow.show();
			}catch(e){
				AgPalletUtils._error(e);
			}
		},250);
	},






	pasteTextareaSpecialkeyCB : function(textarea, e){
		if(e.getKey() == e.TAB){
			e.stopEvent();
			var elem = textarea.el.dom;
			var value = (new String(elem.value)).replace(/0x0d0x0a|0x0d|0x0a|\r\n/g,"\n");
			var selectionStart = -1;
			var selectionEnd = -1;
			if(elem.selectionStart != undefined && elem.selectionEnd != undefined){
				selectionStart = elem.selectionStart;
				selectionEnd = elem.selectionEnd;
			}else if(Ext.isIE){
				elem.focus();
				var r = document.selection.createRange();
				var len = r.text.replace(/\r/g, "").length;
				var br = document.body.createTextRange();
				br.moveToElementText(elem);
				var all_len = br.text.replace(/\r/g, "").length;
				br.setEndPoint("StartToStart",r);
				selectionStart = all_len - br.text.replace(/\r/g, "").length;
				selectionEnd = selectionStart + len;
			}
			if(selectionStart<0 || selectionEnd<0) return;
			var l = value.substr(0,selectionStart)+"\t";
			var c = value.substr(selectionStart,selectionEnd-selectionStart);
			var r = value.substr(selectionEnd);
			textarea.setRawValue(l+r);
			if(elem.selectionStart != undefined && elem.selectionEnd != undefined){
				elem.selectionStart = elem.selectionEnd = l.length;
			}else if(Ext.isIE){
				var range = elem.createTextRange();
				range.move("character",l.length);
				range.select();
			}
		}else{
			e.stopPropagation();
		}
	},

	pasteListWindow         : null,
	pasteListTextareafield  : null,
	pasteListRadiogroup     : null,
	pasteListRadiogroupName : 'paste-list-type',

	pasteListRadioTabInputValue : 'tab',
	pasteListRadioCSVInputValue : 'csv',

	pasteListOkButton       : null,
	pasteListCancelButton   : null,

	pasteListStore          : null,
	pasteListCB             : null,

	pasteList : function(app,pasteStore,callBack){
		AgPalletUtils.pasteListStore = pasteStore;
		AgPalletUtils.pasteListCB = callBack;

		var title = 'Paste';

		if(!AgPalletUtils.pasteListWindow){
			AgPalletUtils.pasteListWindow = Ext.create('Ext.window.Window', {

				id          : 'bp3d-pallet-paste-window',
				title       : title,
				width       : 600,
				height      : 450,
//				layout      : 'form',
//				plain       : true,
				bodyStyle   : 'padding:5px;text-align:right;',
				buttonAlign : 'center',
				modal       : true,
				resizable   : true,
				closeAction : 'hide',
				labelWidth  : 68,
				layout      : 'anchor',
				items       : [{
					xtype           : 'textareafield',
					id              : 'bp3d-pallet-paste-textarea',
					hideLabel       : true,
					anchor          : '100% -25',
					selectOnFocus   : true,
					allowBlank      : false,
					enableKeyEvents : Ext.isChrome,
					listeners       : {
						keydown        : AgPalletUtils.pasteTextareaSpecialkeyCB,
						specialkey     : AgPalletUtils.pasteTextareaSpecialkeyCB,
						validitychange : function(textarea,isValid,eOpts){
							if(AgPalletUtils.pasteListOkButton) AgPalletUtils.pasteListOkButton.setDisabled(isValid!==true);
						},
						render         : function(textareafield,eOpts){
//							AgPalletUtils._dump("textareafield.render()");
							AgPalletUtils.pasteListTextareafield = textareafield;
						},
						scope: this
					}
				},{
					xtype      : 'radiogroup',
					fieldLabel : 'Paste Type',
					labelWidth : 68,
					columns    : 2,
					height     : 22,
					anchor     : '100%',
					defaults   : {
						name:AgPalletUtils.pasteListRadiogroupName
					},
					items      : [{
						boxLabel   :'Tab-Separated Values',
						hideLabel  : true,
						inputValue : AgPalletUtils.pasteListRadioTabInputValue
					},{
						boxLabel   : 'Comma-Separated Values',
						hideLabel  : true,
						inputValue : AgPalletUtils.pasteListRadioCSVInputValue
					}],
					listeners  : {
						render         : function(radiogroup,eOpts){
//							AgPalletUtils._dump("radiogroup.render():"+radiogroup.getValue());
							AgPalletUtils.pasteListRadiogroup = radiogroup;
						}
					}
				}],
				buttons : [{
					text      : 'OK',
					listeners : {
						render : function(button,eOpts){
//							AgPalletUtils._dump("OK.render()");
							AgPalletUtils.pasteListOkButton = button;
						},
						click  : function(button,e,eOpts){
							var textarea = AgPalletUtils.pasteListTextareafield;
							if(!textarea.validate()) return;

							AgPalletUtils.pasteListWindow.setLoading(true);

							AgPalletUtils.pasteListOkButton.disable();
							AgPalletUtils.pasteListCancelButton.disable();
							var pasteText = textarea.getValue();
							textarea.disable();
							Ext.defer(function(){
								try{
									if(pasteText){
										var paste_type = 'tab';
										try{
											var value = AgPalletUtils.pasteListRadiogroup.getValue();
											paste_type = value[AgPalletUtils.pasteListRadiogroupName];
										}catch(e){}

										var cvs_arr = AgUtils.CSVData.parse(pasteText);
										var cvs_title_arr = cvs_arr.shift() || [];
										var tab_arr = AgUtils.TabData.parse(pasteText);
										var tab_title_arr = tab_arr.shift() || [];
										if(paste_type=='csv' && cvs_title_arr.length<tab_title_arr.length){
											Ext.Msg.show({
												title:'Paste Type?',
												msg: 'Is this a Comma-Separated Values ?',
												buttons: Ext.Msg.YESNO,
												fn: function(buttonId){
													if(buttonId=='no'){
														pasteCancel();
													}else{
														pasteCB(pasteText);
													}
												},
												icon: Ext.MessageBox.QUESTION
											});
										}else if(paste_type=='tab' && cvs_title_arr.length>tab_title_arr.length){
											Ext.Msg.show({
												title:'Paste Type?',
												msg: 'Is this a Tab-Separated Values ?',
												buttons: Ext.Msg.YESNO,
												fn: function(buttonId){
													if(buttonId=='no'){
														pasteCancel();
													}else{
														pasteCB(pasteText);
													}
												},
												icon: Ext.MessageBox.QUESTION
											});
										}else{
											pasteCB(pasteText);
										}
									}else{
										pasteCancel();
									}
								}catch(e){
									AgPalletUtils._error(e);
									pasteCancel();
								}
							},0);
						}
					}
				},{
					text      : 'Cancel',
					listeners : {
						render : function(button,eOpts){
//							AgPalletUtils._dump("Cancel.render()");
							AgPalletUtils.pasteListCancelButton = button;
						},
						click  : function(button,e,eOpts){
							AgPalletUtils.pasteListWindow.hide();
							if(AgPalletUtils.pasteListCB) AgPalletUtils.pasteListCB([]);
						}
					}
				}],
				listeners : {
					'beforerender': function(comp){
//						AgPalletUtils._dump("pasteListWindow.beforerender()");
					},
					'beforeshow': function(comp){
//						AgPalletUtils._dump("pasteListWindow.beforeshow()");
					},
					'render': function(comp){
//						AgPalletUtils._dump("pasteListWindow.render()");
					},
					'close': function(comp){
//						AgPalletUtils._dump("pasteListWindow.close()");
					},
					'hide': function(comp){
//						AgPalletUtils._dump("pasteListWindow.hide()");
					},
					'show': function(comp){
//						AgPalletUtils._dump("pasteListWindow.show()");
						if(AgPalletUtils.pasteListTextareafield){
							AgPalletUtils.pasteListTextareafield.setValue('');
							AgPalletUtils.pasteListTextareafield.validate();
							AgPalletUtils.pasteListTextareafield.focus(true,250);
						}
						if(AgPalletUtils.pasteListRadiogroup){
							var value = {};
							value[AgPalletUtils.pasteListRadiogroupName] = AgPalletUtils.pasteListRadioTabInputValue;
							AgPalletUtils.pasteListRadiogroup.setValue(value);
						}
					},
					scope: this
				}
			});
		}
		Ext.defer(function(){
			try{
				AgPalletUtils.pasteListWindow.show();
			}catch(e){
				AgPalletUtils._error(e);
			}
		},250);


		var pasteCancel = function(){
			try{
				AgPalletUtils.pasteListWindow.setLoading(false);
				AgPalletUtils.pasteListTextareafield.enable();
				AgPalletUtils.pasteListOkButton.enable();
				AgPalletUtils.pasteListCancelButton.enable();
			}catch(e){
				AgPalletUtils._error(e);
			}
		};

		var pasteCB = function(pasteText){
			try{
				var arr = [];
				if(pasteText){
					var paste_type = 'tab';
					try{
						var value = AgPalletUtils.pasteListRadiogroup.getValue();
						paste_type = value[AgPalletUtils.pasteListRadiogroupName];
					}catch(e){}

					if(paste_type=='csv'){
						arr = AgUtils.CSVData.parse(pasteText);
					}else{
						arr = AgUtils.TabData.parse(pasteText);
					}
				}
				if(pasteText && arr.length>1){

					var addrecs = [];
					var title_arr = arr.shift();

					AgPalletUtils.pasteListStore.suspendEvents(true);
					try{
						var setRecordValue = function(record,key,value){
							var name = key;

							if(record.get(name)===undefined){
								name = null;
								for(var field in record.fields.map){
									if(!record.fields.map[field].mapping) continue;
									if(record.fields.map[field].mapping != key) continue;
									name = record.fields.map[field].name;
									break;
								}
							}
							if(name){
								record.set(name,value);
							}
						};
						var findRecordFieldName = function(record,key){
							var name = key;
							if(record.get(name)===undefined){
								name = null;
								for(var field in record.fields.map){
									if(!record.fields.map[field].mapping) continue;
									if(record.fields.map[field].mapping != key) continue;
									name = record.fields.map[field].name;
									break;
								}
							}
							return name;
						};
						Ext.iterate(arr,function(line,lineIdx,allLines){
							var modifiedFieldNames = [];
							var n_record = Ext.create(AgPalletUtils.pasteListStore.model.modelName,{});
							n_record.beginEdit();
							Ext.iterate(title_arr,function(title,titleIdx,allTitles){
//								title = title.trim().toLowerCase();
								title = findRecordFieldName(n_record,title.trim());
								if(Ext.isEmpty(title)) return true;
								if(Ext.isDate(n_record.data[title]) || (n_record.fields.map[title] && n_record.fields.map[title].type.type=='date')){
									var date = new Date();
									date.setTime(Number(line[titleIdx]));
									setRecordValue(n_record,title,date);
								}else if(Ext.isBoolean(n_record.data[title])){
									setRecordValue(n_record,title,Boolean(line[titleIdx]==="true"));
								}else if(Ext.isNumeric(n_record.data[title])){
									setRecordValue(n_record,title,Number(line[titleIdx]));
								}else{
									setRecordValue(n_record,title,line[titleIdx]);
								}
								modifiedFieldNames.push(title);
							});

							Ext.each(n_record.fields.items,function(item,i,a){
								try{
									if(item.convert){
										n_record.set(item.name,item.convert(n_record.get(item.name),n_record));
									}
								}catch(e){
									AgPalletUtils._error("482:"+e);
								}
							});
							n_record.commit(false);
							n_record.endEdit(false,modifiedFieldNames);

							var f_record = AgPalletUtils.findPasteListStore(n_record);
							if(f_record){
								AgPalletUtils.pasteListStore.remove(f_record);
								f_record = null;
							}

							if(f_record){
								var modifiedFieldNames = [];
								f_record.beginEdit();
//								Ext.iterate(f_record.data,function(key,idx,keys){
								Ext.each(title_arr,function(title){
									var key = findRecordFieldName(n_record,title.trim());
									if(Ext.isEmpty(key)){
										console.log(title,key);
										return true;
									}
									f_record.set(key,n_record.get(key));
									modifiedFieldNames.push(key);
								});
								f_record.commit(false);
								f_record.endEdit(false,modifiedFieldNames);
							}else{
								addrecs.push(n_record);
							}
						});

						if(addrecs.length>0){
//							AgPalletUtils.pasteListStore.add(addrecs);
//							if(AgPalletUtils.pasteListCB) AgPalletUtils.pasteListCB(addrecs);
						}
					}catch(e){
						AgPalletUtils._error("472:"+e);
						pasteCancel();
					}
					AgPalletUtils.pasteListStore.resumeEvents();

					if(addrecs.length>0){
						var art_ids = [];
						var art_id_hash = {};
						var cdi_names = [];
						var cdi_name_hash = {};
						Ext.each(addrecs,function(r,i,a){
							var art_id = r.get('art_id');
							var cdi_name = r.get('cdi_name');
							if(!Ext.isEmpty(art_id)){
								if(Ext.isEmpty(art_id_hash[art_id])){
									art_id_hash[art_id] = art_id;
									art_ids.push({
										art_id:   art_id,
										selected: r.get('selected'),
										color:    r.get('color'),
										opacity:  r.get('opacity'),
										remove:   r.get('remove'),
										scalar:   r.get('scalar')
									});
								}
							}
							else if(!Ext.isEmpty(cdi_name)){
								if(Ext.isEmpty(cdi_name_hash[cdi_name])){
									cdi_name_hash[cdi_name] = cdi_name;
									cdi_names.push({
										cdi_name: cdi_name,
										selected: r.get('selected'),
										color:    r.get('color'),
										opacity:  r.get('opacity'),
										remove:   r.get('remove'),
										scalar:   r.get('scalar')
									});
								}
							}
						});

						if(art_ids.length || cdi_names.length){
							var params = {};
							if(art_ids.length){
								params.art_ids = Ext.encode(art_ids);
							}
							else if(cdi_names.length){
								params.cdi_names = Ext.encode(cdi_names);
							}
							else if(cm_use_keys.length){
								params.cm_use_keys = Ext.encode(cm_use_keys);
							}
							app.getUploadObjInfo(params,{
								store: AgPalletUtils.pasteListStore,
								emptyMsg: {
									title: 'WARNING',
									msg: 'ペーストされたテキストに対応するデータが存在しません',
									buttons: Ext.Msg.OK,
									icon: Ext.Msg.WARNING
								},
								empty: function(){
									AgPalletUtils.pasteListStore.remove(addrecs);
									if(AgPalletUtils.pasteListCB) AgPalletUtils.pasteListCB(addrecs,[]);
								},
								success: function(records){
									if(AgPalletUtils.pasteListCB) AgPalletUtils.pasteListCB(addrecs,records);
								},
								failure: function(){
									if(AgPalletUtils.pasteListCB) AgPalletUtils.pasteListCB(addrecs);
								}
							});
						}
						else{
							AgPalletUtils.updateRecordStatus(addrecs);
							if(AgPalletUtils.pasteListCB) AgPalletUtils.pasteListCB(addrecs);
						}
					}
					else{
						if(AgPalletUtils.pasteListCB) AgPalletUtils.pasteListCB([]);
					}
				}else if(pasteText && arr.length==1){	//ペーストされたデータが１行のみの場合
					Ext.Msg.show({
						title: 'WARNING',
						msg: 'ペーストされたテキストを解析できません',
						buttons: Ext.Msg.OK,
						icon: Ext.Msg.WARNING
					});
					pasteCancel();
					return;
				}
				pasteCancel();
				AgPalletUtils.pasteListWindow.hide();
			}catch(e){
				AgPalletUtils._error("802:"+e);
				pasteCancel();
			}
		};
	},

	findPasteListStore : function(record){
		var e_record = null;
		Ext.each(AgPalletUtils.pasteListStore.getRange(),function(r,i,a){
			if(r.get('art_id') != record.get('art_id')) return true;
			e_record = r;
			return false;
		});
		return e_record;
	},

	updateRecordStatus : function(addrecs){
		AgPalletUtils.pasteListStore.suspendEvents(true);
		try{
			var uploadObjectAllStore = Ext.data.StoreManager.lookup('uploadObjectAllStore');
			try{
				uploadObjectAllStore.suspendEvents(false);
				Ext.each(addrecs,function(addrec,i,a){
//					var r = uploadObjectAllStore.findRecord('art_id',addrec.get('art_id'),0,false,true,true);

					var idx = uploadObjectAllStore.findBy(function(record,id){
						if(addrec.get('art_id')==record.get('art_id') && addrec.get('artg_name')==record.get('artg_name')) return true;
					});
					if(idx<0) return true;
					var r = uploadObjectAllStore.getAt(idx);

//				if(r) console.log(Ext.apply({},r.data));
					if(Ext.isEmpty(r)) return true;

					if(!r.get('selected')){
						r.beginEdit();
						r.set('selected',true)
						r.commit(true);
						r.endEdit(true,['selected']);
					}

					var modifiedFieldNames = [];
					addrec.beginEdit();
					Ext.each(addrec.fields.items,function(item,i,a){
						if(Ext.isEmpty(addrec.get(item.name)) && !Ext.isEmpty(r.get(item.name))){
							addrec.set(item.name,r.get(item.name));
							modifiedFieldNames.push(item.name);
						}
						else if(item.name == 'cm_use'){
							addrec.set(item.name,r.get(item.name));
							modifiedFieldNames.push(item.name);
						}
					});
					if(modifiedFieldNames.length){
						addrec.commit(false);
						addrec.endEdit(false,modifiedFieldNames);
					}else{
						addrec.cancelEdit();
					}
				});
			}catch(e){
				console.error(e);
			}
			uploadObjectAllStore.resumeEvents();

		}catch(e){
			AgPalletUtils._error("610:"+e);
		}
		AgPalletUtils.pasteListStore.resumeEvents();
	},

	_dump : function(aStr){
		if(window.dump) window.dump("AgPalletUtils.js:"+aStr+"\n");
		try{if(console && console.log) console.log("AgPalletUtils.js:"+aStr);}catch(e){}
	},
	_error : function(aStr){
		if(window.dump) window.dump("AgPalletUtils.js:"+aStr+"\n");
		try{if(console && console.error) console.error("AgPalletUtils.js:"+aStr);}catch(e){}
	}

};
