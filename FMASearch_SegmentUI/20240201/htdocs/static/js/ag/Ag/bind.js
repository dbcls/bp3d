Ext.define('Ag.Store', {
	override: 'Ag.Main',
	initBind : function(){

		var self = this;

		self._hashChange = Ext.bind(function(e){
	//		console.log('hashchange',window.location.hash.substr(1));
			var self = this;
			Ext.defer(function(){
	//			var update_content = false;
				var combobox = Ext.getCmp(self.DEF_CONCEPT_BUILD_FORM_FIELD_ID);
				var hash = self.getLocationHash();
				if(Ext.isNumeric(hash[Ag.Def.LOCATION_HASH_CIID_KEY]) && Ext.isNumeric(hash[Ag.Def.LOCATION_HASH_CBID_KEY])){
					var value = Ext.util.Format.format(Ag.Def.FORMAT_CONCEPT_VALUE, hash[Ag.Def.LOCATION_HASH_CIID_KEY],hash[Ag.Def.LOCATION_HASH_CBID_KEY]);
					if(value != combobox.getValue()){
						var record = combobox.findRecordByValue(value);
						if(record){
							combobox.suspendEvent('select');
							combobox.setValue(value);
							combobox.resumeEvent('select');
	//						update_content = true;
						}
					}
				}

				var tbbutton_single = Ext.getCmp('hierarchy-display-options-single');
				var tbbutton_extended = Ext.getCmp('hierarchy-display-options-extended');
				if(tbbutton_single && tbbutton_extended){
					if(self.getLocationHashExtendHierarchy()){
	//					if(!tbbutton_extended.pressed){
							tbbutton_extended.toggle(true,false);
	//					}
					}else{
	//					if(!tbbutton_single.pressed){
							tbbutton_single.toggle(true,false);
	//					}
					}
				}

				var hashId     = self.isEmpty(hash[Ag.Def.LOCATION_HASH_ID_KEY])     ? null : Ext.String.trim(hash[Ag.Def.LOCATION_HASH_ID_KEY]);
				var hashName   = self.isEmpty(hash[Ag.Def.LOCATION_HASH_NAME_KEY])   ? null : Ext.String.trim(hash[Ag.Def.LOCATION_HASH_NAME_KEY]);
				var hashSearch = self.isEmpty(hash[Ag.Def.LOCATION_HASH_SEARCH_KEY]) ? null : Ext.String.trim(hash[Ag.Def.LOCATION_HASH_SEARCH_KEY]);
				var field;
				if(hashSearch){
					field = Ext.getCmp(self.DEF_SEARCH_FORM_FIELD_ID);
					if(hashSearch == field.getValue()){
	//					field = undefined;
					}else{
						field.setValue(hashSearch);
					}
				}
				if(hashName){
					field = Ext.getCmp(self.DEF_NAME_FORM_FIELD_ID);
					if(hashName == field.getValue()){
	//					field = undefined;
					}else{
						field.setValue(hashName);
					}
				}
				if(hashId){
					field = Ext.getCmp(self.DEF_ID_FORM_FIELD_ID);
					if(hashId == field.getValue()){
	//					field = undefined;
					}else{
						field.setValue(hashId);
					}
				}
	//			console.log(field,update_content);
	//			if(!field && update_content){
	//				field = Ext.getCmp(self.DEF_ID_FORM_FIELD_ID);
	//			}
				if(field){
					field.specialkeyENTER();
				}
			},250);
		},self);

		$(window).on('hashchange',self._hashChange);

		$(document).on('click','a.search',function(e){
	//		console.log($(this).text());
	//		self.setLocationHashName($(this).text());

	//		var id_text = $(this).closest('tr.term').find('label.id').text();
			var id_text = $(this).attr('data-'+Ag.Def.ID_DATA_FIELD_ID);
			if(Ext.isString(id_text)) id_text = id_text.trim();
			if(Ext.isEmpty(id_text)){
				self.setLocationHashName($(this).text());
			}else{
				self.setLocationHashID(id_text);
	/*
				var field = Ext.getCmp(self.DEF_ID_FORM_FIELD_ID);
				field.setValue(id_text);
				var e = new Ext.EventObjectImpl();
				e.keyCode = e.ENTER
				field.fireEvent('specialkey',field,e);
	*/
			}
			return false;
		});

	//	$(document).on('dragstart','table.draggable',function(e){
		$(document).on('dragstart','*[draggable]',function(e){
			e.originalEvent.dataTransfer.effectAllowed = 'copy';
			if(false && Ext.getCmp('dragtype-url').getValue()){
				e.originalEvent.dataTransfer.setData('text/plain', window.location.href);
			}
			else{
	//			console.log(this.nodeName);
				var all_text_datas = [];

				var datas = [];
				if(this.nodeName=='TR' && $(this).attr('data-boundview')){
					try{
						var view_id = $(this).attr('data-boundview');
						datas = Ext.Array.map(Ext.getCmp(view_id).panel.getSelectionModel().getSelection(),function(record){
/*
							var hash = {};
							hash[self.DEF_ID_LABEL] = record.get(Ag.Def.ID_DATA_FIELD_ID);
							hash[self.DEF_NAME_LABEL] = record.get(Ag.Def.NAME_DATA_FIELD_ID);
							hash[self.DEF_SYNONYM_LABEL] = record.get(Ag.Def.SYNONYM_DATA_FIELD_ID);
//
//							hash[Ag.Def.LOCATION_HASH_CIID_KEY] = record.get(Ag.Def.CONCEPT_INFO_DATA_FIELD_ID);
//							hash[Ag.Def.LOCATION_HASH_CBID_KEY] = record.get(Ag.Def.CONCEPT_BUILD_DATA_FIELD_ID);
//							hash[Ag.Def.LOCATION_HASH_MDID_KEY] = record.get(Ag.Def.MODEL_DATA_FIELD_ID);
//							hash[Ag.Def.LOCATION_HASH_MVID_KEY] = record.get(Ag.Def.MODEL_VERSION_DATA_FIELD_ID);
//
							hash[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = record.get(Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID);
//							return hash;
*/

//							return record.getData();

							var hash = record.getData();
							Ext.Object.each(hash,function(key,value){
								if(Ext.isDate(hash[key])) hash[key] = hash[key].getTime()/1000;
							});
//							hash['__view_id'] = view_id;
							return hash;
						});
					}catch(e){
						console.error(e);
					}
				}
				if(datas.length){
					if(false && self.DEF_MODEL_VERSION_RECORD){
						var hash = {};
						hash['model'] = self.DEF_MODEL_VERSION_RECORD.get('md_name');
						hash['version'] = self.DEF_MODEL_VERSION_RECORD.get('mv_name');
						hash['concept'] = self.DEF_MODEL_VERSION_RECORD.get('ci_name');
						hash['build'] = self.DEF_MODEL_VERSION_RECORD.get('cb_name');
						hash['datas'] = datas;
						e.originalEvent.dataTransfer.setData('text/plain', Ext.encode(hash));
					}
					else{
						e.originalEvent.dataTransfer.setData('text/plain', Ext.encode(datas));
					}
				}else if(this.nodeName=='TABLE'){
					var lastRecord = self.getLastRecord();
					var hash = {};
					hash[self.DEF_ID_LABEL] = lastRecord.get(Ag.Def.ID_DATA_FIELD_ID);
					hash[self.DEF_NAME_LABEL] = lastRecord.get(Ag.Def.NAME_DATA_FIELD_ID);
					hash[self.DEF_SYNONYM_LABEL] = lastRecord.get(Ag.Def.SYNONYM_DATA_FIELD_ID);
					hash[self.DEF_DEFINITION_LABEL] = lastRecord.get(Ag.Def.DEFINITION_DATA_FIELD_ID);
					e.originalEvent.dataTransfer.setData('text/plain', Ext.encode(hash));
				}
				else if(this.nodeName=='TR'){
					var text_datas = [];
					$(this).find('th,td').each(function(){
						$(this).find('label').each(function(){
							text_datas.push($(this).text());
						});
						$(this).find('div').each(function(){
							text_datas.push($(this).text());
						});
					});
					all_text_datas.push(text_datas.join("\t"));
					e.originalEvent.dataTransfer.setData('text/plain', all_text_datas.join("\n"));
				}
				else{
					all_text_datas.push($(this).text());
					e.originalEvent.dataTransfer.setData('text/plain', all_text_datas.join("\n"));
				}
	//			e.originalEvent.dataTransfer.setData('text/plain', all_text_datas.join("\n"));
			}
	//		e.preventDefault();
			e.stopPropagation();
		});

		$(document).on('mouseover','*[draggable]',function(e){	//mouseenter
	//		$('.draggable-hover').removeClass('draggable-hover');
			$(this).addClass('draggable-hover');
			e.preventDefault();
			e.stopPropagation();
		});
		$(document).on('mouseout','*[draggable]',function(e){	//mouseleave
	//		$('.draggable-hover').removeClass('draggable-hover');
			$(this).removeClass('draggable-hover');
			e.preventDefault();
			e.stopPropagation();
		});
	},

	copyGridColumnsText : function(view,grid_columns){
		var self = this;

		if(Ext.isEmpty(grid_columns)) grid_columns = view.getGridColumns();
		var rows = [];
		var cols = [];
		Ext.each(grid_columns, function(grid_column){
			cols.push(grid_column.text);
		});
		rows.push('#'+cols.join("\t"));


		Ext.Array.each(view.getSelectionModel().getSelection(), function(record){
			var cols = [];
			Ext.each(grid_columns, function(grid_column){
				cols.push(record.get(grid_column.dataIndex));
			});
			rows.push(cols.join("\t"));
		})

		var text = rows.join("\n");
		var ta = document.createElement('textarea');
		ta.value = text;
		document.body.appendChild(ta);
		ta.select();
		document.execCommand('copy');
		ta.parentElement.removeChild(ta);
	},

	getViewConfig : function(){
		var self = this;
		return {
			listeners: {
				itemkeydown: function( view, record, item, index, e, eOpts ){
					if(e.ctrlKey && e.getKey() == e.A){
						var gridpanel = this.up('panel');
						e.stopEvent();
						var button = gridpanel.down('button#select_all');
						if(button){
							button.fireEvent('click',button);
						}
						else{
							view.getSelectionModel().selectAll();
						}
					}
				}
			}
		};
	},

	getDropViewConfig : function(){
		var self = this;
		return Ext.apply(self.getViewConfig(),{
			rowTpl: [
				'{%',
					'var dataRowCls = values.recordIndex === -1 ? "" : " ' + Ext.baseCSSPrefix + 'grid-data-row";',
				'%}',
				'<tr role="row" {[values.rowId ? ("id=\\"" + values.rowId + "\\"") : ""]} ',
					'data-boundView="{view.id}" ',
					'data-recordId="{record.internalId}" ',
					'data-recordIndex="{recordIndex}" ',
					'class="{[values.itemClasses.join(" ")]} {[values.rowClasses.join(" ")]}{[dataRowCls]}" ',
					'draggable="true"',
					'{rowAttr:attributes} tabIndex="-1">',
					'<tpl for="columns">',
						'{%',
							'parent.view.renderCell(values, parent.record, parent.recordIndex, xindex - 1, out, parent)',
						'%}',
					'</tpl>',
				'</tr>',
				{
					priority: 0
				}
			]
		});
	},

	bindDrop : function(panel){
		var self = this;
		var store = panel.getStore();
		var view = panel.getView();
		var el = panel.getEl();
		el.on({
			dragenter: function(event){
				if(event && event.stopEvent) event.stopEvent();
				return false;
			},
			dragover: function(event){
				if(event && event.stopEvent) event.stopEvent();
				return false;
			},
			drop: function(event){
				if(event && event.stopEvent) event.stopEvent();
				var dataTransfer;
				if(Ext.isObject(event)){
					if(event.browserEvent && event.browserEvent.dataTransfer){
						dataTransfer = event.browserEvent.dataTransfer;
					}else if(event.dataTransfer){
						dataTransfer = event.dataTransfer;
					}
				}
				var dropData = null;
				if(dataTransfer && dataTransfer.getData){
					try{dropData = Ext.decode(dataTransfer.getData('text/plain'));}catch(e){}
				}
				if(dropData){
					if(!Ext.isArray(dropData)) dropData = [dropData];
					var add_records = [];
					var exists_records = [];
					Ext.each(dropData,function(data){
						var record = store.createModel(data||{});
						if(Ext.isEmpty(record.get(Ag.Def.ID_DATA_FIELD_ID))) return true;
						var find_record = store.findRecord( Ag.Def.ID_DATA_FIELD_ID, record.get(Ag.Def.ID_DATA_FIELD_ID), 0, false, false, true );
						if(Ext.isEmpty(find_record)){
							add_records.push(record);
						}else{
							exists_records.push(find_record);
						}
					});
					self.addRecords(view,add_records);
/*
					if(add_records.length){
						var sorters = store.sorters.getRange();
						if(sorters.length){
							store.sorters.clear();
							view.headerCt.clearOtherSortStates();
						}
						store.add(add_records);
						if(sorters.length){
							store.sorters.addAll(sorters);
							store.sort();
						}
					}
*/
				}
			}
		});
	},

	bindCellclick: function(panel){
		panel.on('cellclick', function( view, td, cellIndex, record, tr, rowIndex, e, eOpts ){
			var gridpanel = this;
			var selModel = gridpanel.getSelectionModel();
			var start = selModel.selectionStart;
			if(e.shiftKey && start){
				selModel.selectRange(start, record, e.ctrlKey);
			}
		},panel);
	}

});
