window.AgApp = window.AgApp || function(config){};
window.AgApp.prototype.openMappingMngWin = function(aOpt){
	var self = this;
	aOpt = Ext.apply({},aOpt||{},{
		iconCls: 'gear-btn',
		title: AgLang.mapping_mng,
	});
	aOpt.id = aOpt.id || Ext.id();

	var idPrefix = aOpt.id+'-';

	var itemIdMirrorPrefix = 'mirror-';
	var idMirrorPrefix = aOpt.id+'-'+itemIdMirrorPrefix;

	var attributeStoreId = idPrefix+'attributeStore';
	var existingAttributeStoreId = idPrefix+'existingAttributeStore';
	var parentAttributeStoreId = idPrefix+'parentAttributeStore';
	var attributeGridId = idPrefix+'attribute-gridpanel';

	var mirrorAttributeStoreId = idMirrorPrefix+'attributeStore';
	var mirrorExistingAttributeStoreId = idMirrorPrefix+'existingAttributeStore';
	var mirrorParentAttributeStoreId = idMirrorPrefix+'parentAttributeStore';
	var mirrorAttributeGridId = idMirrorPrefix+'attribute-gridpanel';

	var itemIdAllPrefix = 'all-';
	var idAllPrefix = aOpt.id+'-'+itemIdAllPrefix;
	var allExistingAttributeStoreId = idAllPrefix+'existingAttributeStore';

	self.syncMappingMngStore = function(records,loadPage){
		if(Ext.isEmpty(records)) records = [];
		if(Ext.isEmpty(loadPage)) loadPage = true;
		if(!Ext.isBoolean(loadPage)) loadPage = loadPage ? true : false;
		Ext.each([attributeStoreId,mirrorAttributeStoreId],function(storeId){
			var store = Ext.data.StoreManager.lookup(storeId);
			store.suspendEvents(false);
			Ext.each(records,function(r,i,a){
				var record = store.findRecord('art_id',r.get('art_id'),0,false,false,true);
				if(Ext.isEmpty(record)) return true;
				var fieldNames = ['cdi_name','cdi_name_e','cmp_id','cm_use','never_current'];
				record.beginEdit();
				Ext.each(fieldNames,function(fieldName){
					record.set(fieldName,r.get(fieldName));
				});
				record.commit(false,fieldNames);
				record.endEdit(false,fieldNames);
			});
			store.resumeEvents();
		});
		Ext.getCmp(attributeGridId).getView().refresh();
		Ext.getCmp(mirrorAttributeGridId).getView().refresh();
		if(loadPage){
			Ext.data.StoreManager.lookup(existingAttributeStoreId).loadPage(1);
			Ext.data.StoreManager.lookup(parentAttributeStoreId).loadPage(1);
			var panel = Ext.getCmp(aOpt.id);
			var mirror_checkboxfield = panel.down('checkboxfield#mirror');
			if(mirror_checkboxfield && mirror_checkboxfield.getValue() && !mirror_checkboxfield.isDisabled()){
				Ext.data.StoreManager.lookup(mirrorExistingAttributeStoreId).loadPage(1);
				Ext.data.StoreManager.lookup(mirrorParentAttributeStoreId).loadPage(1);
			}
		}
	};

	var lastRecord;
	var getLastRecord = function(){
		return lastRecord || Ext.create('CONCEPT_TERM',{});
	};
	var setLastRecord = function(record){
		if(Ext.isEmpty(record)){
			lastRecord = Ext.create('CONCEPT_TERM',{});
		}else{
			lastRecord = record;
		}
		var attributeStore = Ext.data.StoreManager.lookup(attributeStoreId);
		if(attributeStore) attributeStore.fireEvent('datachanged',attributeStore);
	};

	var lastMirrorRecord;
	var getLastMirrorRecord = function(){
		return lastMirrorRecord || Ext.create('CONCEPT_TERM',{});
	};
	var setLastMirrorRecord = function(record){
		if(Ext.isEmpty(record)){
			lastMirrorRecord = Ext.create('CONCEPT_TERM',{});
		}else{
			if(getLastRecord().get('cdi_name')===record.get('cdi_name') && getLastRecord().get('cmp_id')===record.get('cmp_id')){
				lastMirrorRecord = Ext.create('CONCEPT_TERM',{});

				Ext.Msg.show({
					title: AgLang.subject,
					msg: '同じFMAIDは指定できません',
					buttons: Ext.Msg.OK,
					icon: Ext.Msg.ERROR,
					fn: function(buttonId,text,opt){
					}
				});

			}else{
				lastMirrorRecord = record;
			}
		}
		var mirrorAttributeStore = Ext.data.StoreManager.lookup(mirrorAttributeStoreId);
		if(mirrorAttributeStore) mirrorAttributeStore.fireEvent('datachanged',mirrorAttributeStore);
	};

	var getExistingGridColumnRenderer = function(value,metaData,record,rowIndex,colIndex,store,view){
		if(metaData.column.xtype){
			if(metaData.column.xtype == 'booleancolumn'){
				if(Ext.isBoolean(value) && metaData.column.trueText && metaData.column.falseText){
					if(value){
						value = metaData.column.trueText;
					}else{
						value = metaData.column.falseText;
					}
				}
			}
			else if(metaData.column.xtype == 'agfilesizecolumn'){
				if(Ext.isNumber(value)) value = Ext.util.Format.fileSize(value);
			}
			else if(metaData.column.xtype == 'agnumbercolumn'){
				if(Ext.isNumber(value) && metaData.column.format) value = Ext.util.Format.number(value,metaData.column.format);
			}
			else if(metaData.column.xtype == 'datecolumn'){
				if(Ext.isDate(value) && metaData.column.format) value = Ext.util.Format.date(value,metaData.column.format);
			}
		}
/*
		var tdCls = [];
		if(Ext.isBoolean(record.get('is_virtual')) && record.get('is_virtual')){
			if(
				Ext.isEmpty(record.get('virtual_cm_use')) &&
				Ext.isEmpty(record.get('virtual_current_use')) &&
				Ext.isEmpty(record.get('virtual_current_use_reason')) &&
				Ext.isEmpty(record.get('virtual_never_current')) &&
				Ext.isEmpty(record.get('virtual_cdi_name'))
			){
				tdCls.push('gridcolumn_is_virtual');
			}else{
				var dataIndex = metaData.column.dataIndex ? metaData.column.dataIndex : view.up('gridpanel').columns[colIndex].dataIndex;
				if(dataIndex == 'current_use'){
					if(Ext.isBoolean(record.get('virtual_current_use')) && record.get('virtual_current_use') !== record.get('current_use')) tdCls.push('gridcolumn_is_virtual');
				}
				else if(dataIndex == 'never_current'){
					if(Ext.isBoolean(record.get('virtual_never_current')) && record.get('virtual_never_current') !== record.get('never_current')) tdCls.push('gridcolumn_is_virtual');
				}
				else if(dataIndex == 'cdi_name' || dataIndex == 'cdi_name_e'){
					if(Ext.isString(record.get('virtual_cdi_name')) && record.get('virtual_cdi_name') !== record.get('cdi_name')) tdCls.push('gridcolumn_is_virtual');
				}
			}
		}
		if(tdCls.length){
			if(Ext.isString(metaData.tdCls) && metaData.tdCls.length){
				metaData.tdCls += ' ' + tdCls.join(' ');
			}else{
				metaData.tdCls = tdCls.join(' ');
			}
		}
*/
		return value;
	};
	var getExistingGridColumns = function(){
		return [
			{
				text: AgLang.new,      dataIndex: 'is_virtual',       stateId: 'is_virtual',        width: 34, minWidth: 34, hidden: false, hideable: false, sortable: false, draggable: false, resizable: false, align: 'center'
				,renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
					var tdCls = [];
					if(value){
						tdCls.push('gridcolumn_current_use');
					}else{
//						tdCls.push('gridcolumn_current_none_use');
					}

					if(Ext.isString(metaData.tdCls) && metaData.tdCls.length){
						metaData.tdCls += ' ' + tdCls.join(' ');
					}else{
						metaData.tdCls = tdCls.join(' ');
					}
					return getExistingGridColumnRenderer('',metaData,record,rowIndex,colIndex,store,view);
				}
			},
			{
				text: AgLang.current,      dataIndex: 'current_use',       stateId: 'current_use',        width: 46, minWidth: 46, hidden: false, hideable: false, sortable: false, draggable: false, resizable: false
				,renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
					var tdCls = [];
					if(value){
						tdCls.push('gridcolumn_current_use');
					}
					else if(Ext.isEmpty(record.get('cdi_name'))){
						metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(self.TOOLTIP_FMAID_NOT_SUPPORTED) + '"';
					}
					else{
						tdCls.push('gridcolumn_current_none_use');
						if(Ext.isString(record.get('current_use_reason'))) metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(record.get('current_use_reason')) + '"';
					}

					if(Ext.isString(metaData.tdCls) && metaData.tdCls.length){
						metaData.tdCls += ' ' + tdCls.join(' ');
					}else{
						metaData.tdCls = tdCls.join(' ');
					}
					return getExistingGridColumnRenderer('',metaData,record,rowIndex,colIndex,store,view);
				}
			},
			{
				text: AgLang.edited,      dataIndex: 'cm_edited',       stateId: 'cm_edited',        width: 46, minWidth: 46, hidden: self.getHiddenEditedGridColumn(), hideable: false, sortable: true, draggable: false, resizable: false
				,renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
					var tdCls = [];
					if(value){
						tdCls.push('gridcolumn_current_use');
					}else{
						tdCls.push('gridcolumn_current_none_use');
					}
					if(Ext.isString(metaData.tdCls) && metaData.tdCls.length){
						metaData.tdCls += ' ' + tdCls.join(' ');
					}else{
						metaData.tdCls = tdCls.join(' ');
					}
					return getExistingGridColumnRenderer('',metaData,record,rowIndex,colIndex,store,view);
				}
			},
			{
				text: '&#160;',            dataIndex: 'art_tmb_path',     stateId: 'art_tmb_path',      width: 24, minWidth: 24, hidden: false, hideable: false, sortable: false, draggable: false, resizable: false
				,renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
					if(Ext.isString(metaData.innerCls) && metaData.innerCls.length){
						metaData.innerCls += ' art_tmb_path';
					}else{
						metaData.innerCls = 'art_tmb_path';
					}
					return getExistingGridColumnRenderer(value,metaData,record,rowIndex,colIndex,store,view);
				}
			},
			{
				text: 'Never Current',     dataIndex: 'never_current',stateId: 'never_current', width: 80, minWidth: 80, hidden: false, hideable: false, resizable: false, sortable: false, xtype : 'booleancolumn', trueText: 'Yes', falseText: 'No', align: 'center'
				,renderer: getExistingGridColumnRenderer
			},
//			{
//				text: AgLang.art_id,       dataIndex: 'art_id',       stateId: 'art_id',        width: 54, minWidth: 54, hidden: false, hideable: false
//				,renderer: getExistingGridColumnRenderer
//			},
			{
				text: AgLang.cdi_name,     dataIndex: 'cdi_name',     stateId: 'cdi_name',      width: 70, minWidth: 70, hidden: false,  hideable: false, xtype: 'agcolumncdiname'
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.cmp_abbr,     dataIndex: 'cmp_id',       stateId: 'cmp_id',        width: 40, minWidth: 40, hidden: false,  hideable: false, xtype: 'agcolumnconceptartmappart'
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.cdi_name_e,   dataIndex: 'cdi_name_e',   stateId: 'cdi_name_e',    flex: 2.0, minWidth: 80, hidden: true, hideable: true, xtype: 'agcolumncdinamee'
//				,renderer: getExistingGridColumnRenderer
			},
			{text: 'System',            dataIndex: 'seg_name',     stateId: 'seg_name',      flex: 1.0, minWidth: 50, hidden: true,  hideable: true,  xtype: 'agsystemcolumn'},
			{
				text: AgLang.art_id,       dataIndex: 'art_id',       stateId: 'art_id',        width: 54, minWidth: 54, hidden: false, hideable: false
				,renderer: getExistingGridColumnRenderer
			},
/*
			{text: AgLang.category,     dataIndex: 'arta_category',stateId: 'arta_category', flex: 1.0, minWidth: 50, hidden: true, hideable: true},
			{text: AgLang.class_name,   dataIndex: 'arta_class',   stateId: 'arta_class',    width: 36, minWidth: 36, hidden: true, hideable: true},
			{text: AgLang.comment,      dataIndex: 'arta_comment', stateId: 'arta_comment',  flex: 2.0, minWidth: 80, hidden: true, hideable: true},
			{text: AgLang.judge,        dataIndex: 'arta_judge',   stateId: 'arta_judge',    flex: 1.0, minWidth: 50, hidden: true, hideable: true},

			{text: AgLang.arto_id,      dataIndex: 'arto_id',      stateId: 'arto_id',       width: 60, minWidth: 60, hidden: true, hideable: true, sortable: false},
			{text: AgLang.arto_filename,dataIndex: 'arto_filename',stateId: 'arto_filename', flex: 2.0, minWidth: 80, hidden: true, hideable: true, sortable: false},
			{text: AgLang.arto_comment, dataIndex: 'arto_comment', stateId: 'arto_comment',  flex: 2.0, minWidth: 80, hidden: true, hideable: true, sortable: false},
*/
			{
				text: AgLang.file_name,    dataIndex: 'art_filename', stateId: 'art_filename',  flex: 2.0, minWidth: 80, hidden: true, hideable: true
				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.file_size,    dataIndex: 'art_data_size',stateId: 'art_data_size', width: 59,  hidden: true, hideable: true, xtype: 'agfilesizecolumn'
//				,renderer: getExistingGridColumnRenderer
			},

			{
				text: AgLang.xmax,         dataIndex: 'art_xmax',     stateId: 'art_xmax',      width: 63,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.xmin,         dataIndex: 'art_xmin',     stateId: 'art_xmin',      width: 63,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.xcenter,      dataIndex: 'art_xcenter',  stateId: 'art_xcenter',   width: 76,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.ymax,         dataIndex: 'art_ymax',     stateId: 'art_ymax',      width: 63,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.ymin,         dataIndex: 'art_ymin',     stateId: 'art_ymin',      width: 63,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.ycenter,      dataIndex: 'art_ycenter',  stateId: 'art_ycenter',   width: 76,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.zmax,         dataIndex: 'art_zmax',     stateId: 'art_zmax',      width: 63,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.zmin,         dataIndex: 'art_zmin',     stateId: 'art_zmin',      width: 63,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.zcenter,      dataIndex: 'art_zcenter',  stateId: 'art_zcenter',   width: 76,  hidden: false, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.volume,       dataIndex: 'art_volume',   stateId: 'art_volume',    width: 76,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},

			{
				text: AgLang.timestamp,    dataIndex: 'art_timestamp',stateId: 'art_timestamp', width: self.ART_TIMESTAMP_WIDTH, hidden: false,  hideable: true, xtype: 'datecolumn',     format: self.ART_TIMESTAMP_FORMAT
//				,renderer: getExistingGridColumnRenderer
			},
//				{text: AgLang.upload_modified, dataIndex: 'art_upload_modified',stateId: 'art_upload_modified', width: 112,  hidden: true, hideable: true, xtype: 'datecolumn', format: self.FORMAT_DATE_TIME },
			{
				text: AgLang.cm_entry,     dataIndex: 'cm_entry',     stateId: 'cm_entry',      width: 67, hidden: true, hideable: true, xtype: 'datecolumn',     format: self.FORMAT_DATE
//				,renderer: getExistingGridColumnRenderer
			}
		];
	};

	var getParentGridColumns = function(){
		return [
			{
				text: 'depth',  dataIndex: 'depth',     stateId: 'depth',      width: 30, minWidth: 30, hidden: true,  hideable: false, align: 'right'
			},
			{
				text: AgLang.new,      dataIndex: 'is_virtual',       stateId: 'is_virtual',        width: 34, minWidth: 34, hidden: false, hideable: false, sortable: false, draggable: false, resizable: false, align: 'center'
				,renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
					var tdCls = [];
					if(value){
						tdCls.push('gridcolumn_current_use');
					}else{
//						tdCls.push('gridcolumn_current_none_use');
					}

					if(Ext.isString(metaData.tdCls) && metaData.tdCls.length){
						metaData.tdCls += ' ' + tdCls.join(' ');
					}else{
						metaData.tdCls = tdCls.join(' ');
					}
					return getExistingGridColumnRenderer('',metaData,record,rowIndex,colIndex,store,view);
				}
			},
			{
				text: AgLang.current,      dataIndex: 'current_use',       stateId: 'current_use',        width: 46, minWidth: 46, hidden: false, hideable: false, sortable: false, draggable: false, resizable: false,
				renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
					var tdCls = [];
					if(value){
						tdCls.push('gridcolumn_current_use');
					}
					else if(Ext.isEmpty(record.get('cdi_name'))){
						metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(self.TOOLTIP_FMAID_NOT_SUPPORTED) + '"';
					}
					else{
						tdCls.push('gridcolumn_current_none_use');
						if(Ext.isString(record.get('current_use_reason'))) metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(record.get('current_use_reason')) + '"';
					}

					if(Ext.isString(metaData.tdCls) && metaData.tdCls.length){
						metaData.tdCls += ' ' + tdCls.join(' ');
					}else{
						metaData.tdCls = tdCls.join(' ');
					}
					return getExistingGridColumnRenderer('',metaData,record,rowIndex,colIndex,store,view);
				}
			},
			{
				text: AgLang.edited,      dataIndex: 'cm_edited',       stateId: 'cm_edited',        width: 46, minWidth: 46, hidden: self.getHiddenEditedGridColumn(), hideable: false, sortable: true, draggable: false, resizable: false
				,renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
					var tdCls = [];
					if(value){
						tdCls.push('gridcolumn_current_use');
					}else{
						tdCls.push('gridcolumn_current_none_use');
					}
					if(Ext.isString(metaData.tdCls) && metaData.tdCls.length){
						metaData.tdCls += ' ' + tdCls.join(' ');
					}else{
						metaData.tdCls = tdCls.join(' ');
					}
					return getExistingGridColumnRenderer('',metaData,record,rowIndex,colIndex,store,view);
				}
			},
			{
				text: '&#160;',            dataIndex: 'art_tmb_path',     stateId: 'art_tmb_path',      width: 24, minWidth: 24, hidden: false, hideable: false, sortable: false, draggable: false, resizable: false,
				renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
					if(Ext.isString(metaData.innerCls) && metaData.innerCls.length){
						metaData.innerCls += ' art_tmb_path';
					}else{
						metaData.innerCls = 'art_tmb_path';
					}
					return getExistingGridColumnRenderer(value,metaData,record,rowIndex,colIndex,store,view);
				}
			},
			{
				text: 'Never Current',     dataIndex: 'never_current',stateId: 'never_current', width: 80, minWidth: 80, hidden: false, hideable: false, resizable: false, sortable: false, xtype : 'booleancolumn', trueText: 'Yes', falseText: 'No', align: 'center'
				,renderer: getExistingGridColumnRenderer
			},
//			{
//				text: AgLang.art_id,       dataIndex: 'art_id',       stateId: 'art_id',        width: 54, minWidth: 54, hidden: false, hideable: false
//				,renderer: getExistingGridColumnRenderer
//			},
			{
				text: AgLang.cdi_name,     dataIndex: 'cdi_name',     stateId: 'cdi_name',      width: 70, minWidth: 70, hidden: false,  hideable: false, xtype: 'agcolumncdiname'
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.cmp_abbr,     dataIndex: 'cmp_id',       stateId: 'cmp_id',        width: 40, minWidth: 40, hidden: true,  hideable: false, xtype: 'agcolumnconceptartmappart'
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.cdi_name_e,   dataIndex: 'cdi_name_e',   stateId: 'cdi_name_e',    flex: 2.0, minWidth: 80, hidden: false, hideable: true, xtype: 'agcolumncdinamee'
//				,renderer: getExistingGridColumnRenderer
			},
			{text: 'System',            dataIndex: 'seg_name',     stateId: 'seg_name',      flex: 1.0, minWidth: 50, hidden: true,  hideable: true,  xtype: 'agsystemcolumn'},
			{
				text: AgLang.art_id,       dataIndex: 'art_id',       stateId: 'art_id',        width: 54, minWidth: 54, hidden: false, hideable: false
				,renderer: getExistingGridColumnRenderer
			},
/*
			{text: AgLang.category,     dataIndex: 'arta_category',stateId: 'arta_category', flex: 1.0, minWidth: 50, hidden: true, hideable: true},
			{text: AgLang.class_name,   dataIndex: 'arta_class',   stateId: 'arta_class',    width: 36, minWidth: 36, hidden: true, hideable: true},
			{text: AgLang.comment,      dataIndex: 'arta_comment', stateId: 'arta_comment',  flex: 2.0, minWidth: 80, hidden: true, hideable: true},
			{text: AgLang.judge,        dataIndex: 'arta_judge',   stateId: 'arta_judge',    flex: 1.0, minWidth: 50, hidden: true, hideable: true},

			{text: AgLang.arto_id,      dataIndex: 'arto_id',      stateId: 'arto_id',       width: 60, minWidth: 60, hidden: true, hideable: true, sortable: false},
			{text: AgLang.arto_filename,dataIndex: 'arto_filename',stateId: 'arto_filename', flex: 2.0, minWidth: 80, hidden: true, hideable: true, sortable: false},
			{text: AgLang.arto_comment, dataIndex: 'arto_comment', stateId: 'arto_comment',  flex: 2.0, minWidth: 80, hidden: true, hideable: true, sortable: false},
*/
			{
				text: AgLang.file_name,    dataIndex: 'art_filename', stateId: 'art_filename',  flex: 2.0, minWidth: 80, hidden: true, hideable: true
				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.file_size,    dataIndex: 'art_data_size',stateId: 'art_data_size', width: 59,  hidden: true, hideable: true, xtype: 'agfilesizecolumn'
//				,renderer: getExistingGridColumnRenderer
			},

			{
				text: AgLang.xmax,         dataIndex: 'art_xmax',     stateId: 'art_xmax',      width: 63,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.xmin,         dataIndex: 'art_xmin',     stateId: 'art_xmin',      width: 63,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.xcenter,      dataIndex: 'art_xcenter',  stateId: 'art_xcenter',   width: 76,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.ymax,         dataIndex: 'art_ymax',     stateId: 'art_ymax',      width: 63,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.ymin,         dataIndex: 'art_ymin',     stateId: 'art_ymin',      width: 63,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.ycenter,      dataIndex: 'art_ycenter',  stateId: 'art_ycenter',   width: 76,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.zmax,         dataIndex: 'art_zmax',     stateId: 'art_zmax',      width: 63,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.zmin,         dataIndex: 'art_zmin',     stateId: 'art_zmin',      width: 63,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.zcenter,      dataIndex: 'art_zcenter',  stateId: 'art_zcenter',   width: 76,  hidden: false, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},
			{
				text: AgLang.volume,       dataIndex: 'art_volume',   stateId: 'art_volume',    width: 76,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER
//				,renderer: getExistingGridColumnRenderer
			},

			{
				text: AgLang.timestamp,    dataIndex: 'art_timestamp',stateId: 'art_timestamp', width: self.ART_TIMESTAMP_WIDTH, hidden: false,  hideable: true, xtype: 'datecolumn',     format: self.ART_TIMESTAMP_FORMAT
//				,renderer: getExistingGridColumnRenderer
			},
//				{text: AgLang.upload_modified, dataIndex: 'art_upload_modified',stateId: 'art_upload_modified', width: 112,  hidden: true, hideable: true, xtype: 'datecolumn', format: self.FORMAT_DATE_TIME },
			{
				text: AgLang.cm_entry,     dataIndex: 'cm_entry',     stateId: 'cm_entry',      width: 67, hidden: true, hideable: true, xtype: 'datecolumn',     format: self.FORMAT_DATE
//				,renderer: getExistingGridColumnRenderer
			}
		];
	};

	var getStore = function(storeId){
		var store = Ext.data.StoreManager.lookup(storeId);
		if(!Ext.isEmpty(store)) return store;
		return Ext.create('Ext.data.Store', {
			storeId: storeId,
			model: 'PARTS',
			sorters    : [{
				property: 'depth',
				direction: 'DESC'
			}],
			proxy: Ext.create('Ext.data.proxy.Ajax',{
				type: 'ajax',
				timeout: 300000,
				pageParam: undefined,
				startParam: undefined,
				limitParam: undefined,
				sortParam: undefined,
				groupParam: undefined,
				filterParam: undefined,
				api: {
					create  : 'api-upload-file-list.cgi?cmd=create',
					read    : 'api-upload-file-list.cgi?cmd=read',
					update  : 'api-upload-file-list.cgi?cmd=update_concept_art_map',
					destroy : 'api-upload-file-list.cgi?cmd=destroy',
				},
				actionMethods : {
					create : 'POST',
					read   : 'POST',
					update : 'POST',
					destroy: 'POST'
				},
				extraParams: {
					hideChildrenTerm: 1,
					hideAncestorTerm: 1,
					hideParentTerm: 1,
					hideDescendantsTerm: 1,
					hidePairTerm: 1,
				},
				reader: {
					type: 'json',
					root: 'datas',
					totalProperty: 'total',
					listeners: {
						exception : function(){
						}
					}
				},
				writer: {
					type: 'json',
					root: 'datas',
					allowSingle: false,
					encode: true
				},
				doRequest: function(operation, callback, scope) {
					var writer  = this.getWriter();
					var request = this.buildRequest(operation);
					if(operation.allowWrite()){
						request = writer.write(request);
					}
					Ext.apply(request, {
						binary        : this.binary,
						headers       : this.headers,
						timeout       : this.timeout,
						scope         : this,
						callback      : this.createRequestCallback(request, operation, callback, scope),
						method        : this.getMethod(request),
						disableCaching: false
					});
					if(this.request_object){
						Ext.Ajax.abort(this.request_object);
						delete this.request_object;
					}
					this.request_object = Ext.Ajax.request(request);
					return request;
				}
			}),
			listeners: {
				beforeload: function(store,operation,eOpts){
					if(!self.beforeloadStore(store)) return false;
					var p = store.getProxy();
					p.extraParams = p.extraParams || {};
					delete p.extraParams.current_datas;
					delete p.extraParams._ExtVerMajor;
					delete p.extraParams._ExtVerMinor;
					delete p.extraParams._ExtVerPatch;
					delete p.extraParams._ExtVerBuild;
					delete p.extraParams._ExtVerRelease;
				}
			}
		});
	};

	var getHideParentTermCheckbox = function(){
		return {
			hidden: true,
			disabled: true,
			xtype: 'checkboxfield',
			boxLabel: 'hide parent term',
			checked: true,
			listeners: {
				afterrender: function(field){
					var gridpanel = field.up('gridpanel');
					var store = gridpanel.getStore();
					store.on({
						load: function(store, records, successful, eOpts){
							field.setDisabled(successful ? false : true);
						}
					});
					if(field.checked){
						var proxy = store.getProxy();
						proxy.extraParams = proxy.extraParams || {};
						proxy.extraParams.hideChildrenTerm=1;
						proxy.extraParams.hideAncestorTerm=1;
						proxy.extraParams.hideParentTerm=1;
						proxy.extraParams.hideDescendantsTerm=1;
						proxy.extraParams.hidePairTerm=1;
					}
				},
				change: function(field, checked){
					var gridpanel = field.up('gridpanel');
					var store = gridpanel.getStore();
					var proxy = store.getProxy();
					proxy.extraParams = proxy.extraParams || {};
					delete proxy.extraParams.hideParentTerm;
					if(checked) proxy.extraParams.hideParentTerm=1;
					store.reload({
						callback: function(){
							if(Ext.isChrome && gridpanel) gridpanel.columns.forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
						}
					})
				}
			}
		};
	};

	var getAttributeDeleteButton = function(){
		return {
			disabled: true,
			xtype: 'button',
			iconCls: 'pallet_delete',
			listeners: {
				afterrender: function(field){
					var gridpanel = field.up('gridpanel');
					gridpanel.on({
						selectionchange: function(selModel, selected, eOpts){
							var disabled = Ext.isEmpty(selected);
							field.setDisabled(disabled);
						}
					});
				},
				click: function(field){
					var gridpanel = field.up('gridpanel');
					var store = gridpanel.getStore();
					var selModel = gridpanel.getSelectionModel();
					store.remove(selModel.getSelection());
					loadAttributePage();
				}
			}
		};
	};

	var getNeverCurrentButton = function(){
		return {
			xtype: 'button',
			disabled: true,
			itemId: 'never_current',
			iconCls: 'gridcolumn_current_none_use',
			text: AgLang.never_current,
			listeners: {
				afterrender: function(field){
					var gridpanel = field.up('gridpanel');
					gridpanel.on('selectionchange',function(selModel,selected,eOpts){
						var disabled = true;
						if(Ext.isArray(selected)){
							Ext.each(selected,function(record){
								if(Ext.isBoolean(record.get('is_exists')) && record.get('is_exists')){
									disabled = false;
									return false;
								}
							});
						}
						field.setDisabled(disabled);
					});
				},
				click: function(field){
					var gridpanel = field.up('gridpanel');
					var store = gridpanel.getStore();
					var selModel = gridpanel.getSelectionModel();
					var records = selModel.getSelection();
					if(Ext.isArray(records) && records.length){
						records.forEach(function(record){
							record.beginEdit();
							if(Ext.isBoolean(record.get('is_virtual')) && record.get('is_virtual')){
								var virtual_cm_use = Ext.isBoolean(record.get('virtual_cm_use')) && record.get('virtual_cm_use') ? !record.get('virtual_cm_use') : true;
								var virtual_never_current = Ext.isBoolean(record.get('virtual_never_current')) && record.get('virtual_never_current') ? !record.get('virtual_never_current') : false;
								record.set('cm_use', virtual_cm_use);
								record.set('never_current', virtual_never_current);
								record.set('virtual_cm_use', virtual_cm_use);
								record.set('virtual_never_current', virtual_never_current);
								record.endEdit(false,['cm_use','never_current','virtual_cm_use','virtual_never_current']);
							}else{
								record.set('cm_use',!record.get('cm_use'));
								record.set('never_current',!record.get('never_current'));
								record.endEdit(false,['cm_use','never_current']);
							}
						});
						field.setDisabled(true);
						if(Ext.isEmpty(store.getUpdatedRecords())){
							return;
						}
						field.setIconCls('loading-btn');
						var gridpanel = field.up('gridpanel');
						if(gridpanel) gridpanel.setDisabled(true);


						self.syncMappingMngStore(records,false);
						if(self.syncUploadObjectStore) self.syncUploadObjectStore(records);
						if(self.syncPalletPartsStore) self.syncPalletPartsStore(records);
						if(self.syncPickSearchStore) self.syncPickSearchStore(records);

						field.setIconCls('loading-btn');
						var gridpanel = field.up('gridpanel');
						if(gridpanel) gridpanel.setDisabled(true);

						store.sync({
							callback: function(batch,options){
								field.setIconCls('gridcolumn_current_none_use');
								if(gridpanel) gridpanel.setDisabled(false);
								Ext.data.StoreManager.lookup(existingAttributeStoreId).loadPage(1);
								Ext.data.StoreManager.lookup(parentAttributeStoreId).loadPage(1);
								var panel = Ext.getCmp(aOpt.id);
								var mirror_checkboxfield = panel.down('checkboxfield#mirror');
								if(mirror_checkboxfield && mirror_checkboxfield.getValue() && !mirror_checkboxfield.isDisabled()){
									Ext.data.StoreManager.lookup(mirrorExistingAttributeStoreId).loadPage(1);
									Ext.data.StoreManager.lookup(mirrorParentAttributeStoreId).loadPage(1);
								}
								Ext.data.StoreManager.lookup(allExistingAttributeStoreId).loadPage(1);
							},
							success: function(batch,options){
								store.loadPage(1);
								var attributeStore = Ext.data.StoreManager.lookup(attributeStoreId);
								attributeStore.fireEvent('datachanged', attributeStore);
							},
							failure: function(batch,options){
								var msg = AgLang.error_submit;
								var proxy = this;
								var reader = proxy.getReader();
								if(reader && reader.rawData && reader.rawData.msg){
									msg += ' ['+reader.rawData.msg+']';
								}
								Ext.Msg.show({
									title: field.text || AgLang.never_current,
									iconCls: 'gridcolumn_current_none_use',
									msg: msg,
									buttons: Ext.Msg.OK,
									icon: Ext.Msg.ERROR,
									fn: function(buttonId,text,opt){
									}
								});
								field.setDisabled(false);
								Ext.each(records,function(r,i,a){
									r.reject();
								});
								self.syncMappingMngStore(records,false);
								if(self.syncUploadObjectStore) self.syncUploadObjectStore(records);
								if(self.syncPalletPartsStore) self.syncPalletPartsStore(records);
								if(self.syncPickSearchStore) self.syncPickSearchStore(records);
							}
						});

					}
				}
			}
		};
	};

	var getRemoveMappingButton = function(){
		return {
			xtype: 'button',
			disabled: true,
			itemId: 'delete',
//			iconCls: 'pallet_delete',
			text: AgLang.remove_from_current,
			listeners: {
				afterrender: function(field){
					var gridpanel = field.up('gridpanel');
					gridpanel.on('selectionchange',function(selModel,selected,eOpts){
						var disabled = true;
						if(Ext.isArray(selected)){
							Ext.each(selected,function(record){
								if(Ext.isBoolean(record.get('is_exists')) && record.get('is_exists')){
									disabled = false;
									return false;
								}
							});
						}
						field.setDisabled(disabled);
					});
				},
				click: function(field){

					Ext.Msg.show({
						title: field.text || AgLang.remove_from_current,
//						iconCls: field.iconCls || 'pallet_delete',
						buttons: Ext.Msg.YESNO,
						icon: Ext.Msg.QUESTION,
						defaultFocus: 'no',
						msg: 'マッピング情報を削除してよろしいですか？',
						fn: function(buttonId,text,opt){
							if(buttonId!='yes') return;

							var gridpanel = field.up('gridpanel');
							var store = gridpanel.getStore();
							var selModel = gridpanel.getSelectionModel();
							var records = selModel.getSelection();
							if(Ext.isArray(records) && records.length){
								records.forEach(function(record){
									record.beginEdit();
									record.set('cdi_name',null);
									record.set('cdi_name_e',null);
									record.set('cmp_id',0);
									record.endEdit(false,['cdi_name','cdi_name_e','cmp_id']);
								});
								field.setDisabled(true);
								if(Ext.isEmpty(store.getUpdatedRecords())){
									return;
								}
								field.setIconCls('loading-btn');
								var gridpanel = field.up('gridpanel');
								if(gridpanel) gridpanel.setDisabled(true);


								self.syncMappingMngStore(records,false);
								if(self.syncUploadObjectStore) self.syncUploadObjectStore(records);
								if(self.syncPalletPartsStore) self.syncPalletPartsStore(records);
								if(self.syncPickSearchStore) self.syncPickSearchStore(records);

								field.setIconCls('loading-btn');
								var gridpanel = field.up('gridpanel');
								if(gridpanel) gridpanel.setDisabled(true);

								store.sync({
									callback: function(batch,options){
										field.setIconCls('pallet_delete');
										if(gridpanel) gridpanel.setDisabled(false);
										Ext.data.StoreManager.lookup(existingAttributeStoreId).loadPage(1);
										Ext.data.StoreManager.lookup(parentAttributeStoreId).loadPage(1);
										var panel = Ext.getCmp(aOpt.id);
										var mirror_checkboxfield = panel.down('checkboxfield#mirror');
										if(mirror_checkboxfield && mirror_checkboxfield.getValue() && !mirror_checkboxfield.isDisabled()){
											Ext.data.StoreManager.lookup(mirrorExistingAttributeStoreId).loadPage(1);
											Ext.data.StoreManager.lookup(mirrorParentAttributeStoreId).loadPage(1);
										}
										Ext.data.StoreManager.lookup(allExistingAttributeStoreId).loadPage(1);
									},
									success: function(batch,options){
										store.loadPage(1);
										var attributeStore = Ext.data.StoreManager.lookup(attributeStoreId);
										attributeStore.fireEvent('datachanged', attributeStore);
									},
									failure: function(batch,options){
										var msg = AgLang.error_submit;
										var proxy = this;
										var reader = proxy.getReader();
										if(reader && reader.rawData && reader.rawData.msg){
											msg += ' ['+reader.rawData.msg+']';
										}
										Ext.Msg.show({
											title: field.text || AgLang.remove_from_current,
//											iconCls: 'pallet_delete',
											msg: msg,
											buttons: Ext.Msg.OK,
											icon: Ext.Msg.ERROR,
											fn: function(buttonId,text,opt){
											}
										});
										field.setDisabled(false);
										Ext.each(records,function(r,i,a){
											r.reject();
										});
										self.syncMappingMngStore(records,false);
										if(self.syncUploadObjectStore) self.syncUploadObjectStore(records);
										if(self.syncPalletPartsStore) self.syncPalletPartsStore(records);
										if(self.syncPickSearchStore) self.syncPickSearchStore(records);
									}
								});
							}
						}
					});
				}
			}
		};
	};

	var getFMABrowserButton = function(){
		return {
			xtype: 'button',
			disabled: true,
			itemId: 'send',
			iconCls: 'window_send',
			text: AgLang.FMABrowser,
			listeners: {
				afterrender: function(b){
					var gridpanel = b.up('gridpanel');
					gridpanel.on('selectionchange',function(selModel,selected,eOpts){
						b.setDisabled(Ext.isEmpty(selected));
					});
				},
				click: function(b){
					var gridpanel = b.up('gridpanel');
					var selModel = gridpanel.getSelectionModel();
					var record = selModel.getLastSelected();
					if(record){
						self.openFMABrowser(record.get('cdi_name'));
					}
				}
			}
		};
	};

	var _loadAttributePage = function(){
		var dropRecord = getLastRecord();
		var cdi_name = dropRecord.get('cdi_name');
		if(Ext.isEmpty(cdi_name)) return;

		var cmp_id = dropRecord.get('cmp_id');
		var conceptArtMapPartStore = Ext.data.StoreManager.lookup('conceptArtMapPartStore');
/*
		var cmp_record_L = conceptArtMapPartStore.findRecord('cmp_abbr', 'L', 0, false, false, true );
		var cmp_record_R = conceptArtMapPartStore.findRecord('cmp_abbr', 'R', 0, false, false, true );
		var cmp_record_P = conceptArtMapPartStore.findRecord('cmp_abbr', 'P', 0, false, false, true );
		if(cmp_record_L && cmp_record_L.get('cmp_id')===cmp_id){
			cdi_name = Ext.String.format('{0}-{1}',cdi_name,cmp_record_L.get('cmp_abbr'));
		}
		else if(cmp_record_R && cmp_record_R.get('cmp_id')===cmp_id){
			cdi_name = Ext.String.format('{0}-{1}',cdi_name,cmp_record_R.get('cmp_abbr'));
		}
		else if(cmp_record_P && cmp_record_P.get('cmp_id')===cmp_id){
			cdi_name = Ext.String.format('{0}-{1}',cdi_name,cmp_record_P.get('cmp_abbr'));
		}
*/
		var cmp_record = conceptArtMapPartStore.findRecord( 'cmp_id', cmp_id, 0, false, false, true ) ;
		if(cmp_record){
			var cmp_abbr = cmp_record.get('cmp_abbr');
			if(Ext.isString(cmp_abbr) && cmp_abbr.length) cdi_name = Ext.String.format('{0}-{1}',cdi_name,cmp_abbr);
		}

		var art_id;
		var attributeStore = Ext.data.StoreManager.lookup(attributeStoreId);
		if(attributeStore && attributeStore.getCount()){
			art_id = attributeStore.getAt(0).get('art_id');
		}

		var existingAttributeStore = Ext.data.StoreManager.lookup(existingAttributeStoreId);
		var existingAttributeProxy = existingAttributeStore.getProxy();
		existingAttributeProxy.extraParams = existingAttributeProxy.extraParams || {};
		existingAttributeProxy.extraParams.cdi_name = cdi_name;
		if(Ext.isEmpty(art_id)){
			delete existingAttributeProxy.extraParams.art_id;
		}else{
			existingAttributeProxy.extraParams.art_id = art_id;
		}
		existingAttributeStore.loadPage(1,{
			callback: function(records,operation,success){
				var store = this;
				if(!success && store.proxy.reader.rawData && store.proxy.reader.rawData.msg){
					Ext.Msg.show({
						title: 'Make SUB',
						msg: store.proxy.reader.rawData.msg,
						buttons: Ext.Msg.OK,
						icon: Ext.Msg.ERROR
					});
				}

			}
		});

		var parentAttributeStore = Ext.data.StoreManager.lookup(parentAttributeStoreId);
		var parentAttributeProxy = parentAttributeStore.getProxy();
		parentAttributeProxy.extraParams = parentAttributeProxy.extraParams || {};
		parentAttributeProxy.extraParams.cdi_cname = cdi_name;
		if(Ext.isEmpty(art_id)){
			delete parentAttributeProxy.extraParams.art_id;
		}else{
			parentAttributeProxy.extraParams.art_id = art_id;
		}

		parentAttributeProxy.extraParams.hideParentTerm = Ext.getCmp(idPrefix+'parent-attribute-display-type-parent').getValue() ? 0 : 1;
		parentAttributeProxy.extraParams.hideAncestorTerm = Ext.getCmp(idPrefix+'parent-attribute-display-type-ancestor').getValue() ? 0 : 1;
		parentAttributeStore.loadPage(1,{
			callback: function(records,operation,success){
			}
		});

		var mirror_checkboxfield = Ext.getCmp(aOpt.id).down('checkboxfield#mirror');
		if(mirror_checkboxfield && mirror_checkboxfield.getValue() && !mirror_checkboxfield.isDisabled()){
			var dropMirrorRecord = getLastMirrorRecord();
			var mirror_cdi_name = dropMirrorRecord.get('cdi_name');
			if(Ext.isEmpty(mirror_cdi_name)){
				var mirrorExistingAttributeStore = Ext.data.StoreManager.lookup(mirrorExistingAttributeStoreId);
				var mirrorParentAttributeStore = Ext.data.StoreManager.lookup(mirrorParentAttributeStoreId);
				mirrorExistingAttributeStore.removeAll();
				mirrorParentAttributeStore.removeAll();
			}else{
				mirror_checkboxfield.fireEvent('change', mirror_checkboxfield, true);
			}
		}

		Ext.data.StoreManager.lookup(allExistingAttributeStoreId).loadPage(1);
	};

	var loadAttributePage = function(){
		var dropRecord = getLastRecord();
		var cdi_name = dropRecord.get('cdi_name');
		if(Ext.isEmpty(cdi_name)) return;

		var cmp_id = dropRecord.get('cmp_id');
		var conceptArtMapPartStore = Ext.data.StoreManager.lookup('conceptArtMapPartStore');
		var cmp_record = conceptArtMapPartStore.findRecord('cmp_id', cmp_id, 0, false, false, true );
		if(cmp_record && (cmp_record.get('cmp_abbr')==='L' || cmp_record.get('cmp_abbr')==='R')){

			var params = self.getExtraParams() || {};
			delete params.current_datas;
			delete params._ExtVerMajor;
			delete params._ExtVerMinor;
			delete params._ExtVerPatch;
			delete params._ExtVerBuild;
			delete params._ExtVerRelease;
			params.cmd = 'read';
			params.cdi_name = Ext.String.format('{0}-{1}',dropRecord.get('cdi_name'),cmp_record.get('cmp_abbr'));
			params.cmp_id = cmp_id;

			Ext.Ajax.request({
				url: 'get-fma-list.cgi',
				autoAbort: true,
				method: 'POST',
				params: params,
				callback: function(options,success,response){
					var json;
					try{json = Ext.decode(response.responseText)}catch(e){};
					if(!success || Ext.isEmpty(json) || Ext.isEmpty(json.success) || !json.success || Ext.isEmpty(json.datas)){
						_loadAttributePage();
					}
					else{
						var data = json.datas.shift();
						if(data.cdi_name != params.cdi_name){
							Ext.Msg.show({
								title: 'WARNING',
								msg: Ext.String.format('FMAID:{0}を使用して下さい',data.cdi_name),
								buttons: Ext.Msg.OK,
								icon: Ext.Msg.WARNING,
								fn: function(){
									var dropRecord = Ext.create('CONCEPT_TERM',{
										id: data.cdi_name,
										name: data.cdi_name_e
									});
									var field = Ext.getCmp(idPrefix+'subject-panel');
									field.update(dropRecord.getData());
									setLastRecord(dropRecord);
									_loadAttributePage();
								}
							});
						}else{
							_loadAttributePage();
						}
					}
				}
			});
		}
		else{
			_loadAttributePage();
		}
	};

	var loadMirrorAttributePage = new Ext.util.DelayedTask(function(){
//		console.log('loadMirrorAttributePage();');
		var dropRecord = getLastRecord();
		var cdi_name = dropRecord.get('cdi_name');

		var mirrorDropRecord = getLastMirrorRecord();
		var mirror_cdi_name = mirrorDropRecord.get('cdi_name');

		var mirrorExistingAttributeStore = Ext.data.StoreManager.lookup(mirrorExistingAttributeStoreId);
		var mirrorParentAttributeStore = Ext.data.StoreManager.lookup(mirrorParentAttributeStoreId);

		if(Ext.isEmpty(cdi_name) || Ext.isEmpty(mirror_cdi_name)){
			mirrorExistingAttributeStore.removeAll();
			mirrorParentAttributeStore.removeAll();
			Ext.data.StoreManager.lookup(allExistingAttributeStoreId).loadPage(1);
			return;
		}

		var cmp_id = dropRecord.get('cmp_id');
		var mirror_cmp_id = mirrorDropRecord.get('cmp_id');
		var conceptArtMapPartStore = Ext.data.StoreManager.lookup('conceptArtMapPartStore');
/*
		var cmp_record_L = conceptArtMapPartStore.findRecord('cmp_abbr', 'L', 0, false, false, true );
		var cmp_record_R = conceptArtMapPartStore.findRecord('cmp_abbr', 'R', 0, false, false, true );
		var cmp_record_P = conceptArtMapPartStore.findRecord('cmp_abbr', 'P', 0, false, false, true );
		if(cmp_record_L && cmp_record_L.get('cmp_id')===cmp_id){
			cdi_name = Ext.String.format('{0}-{1}',cdi_name,cmp_record_L.get('cmp_abbr'));
		}
		else if(cmp_record_R && cmp_record_R.get('cmp_id')===cmp_id){
			cdi_name = Ext.String.format('{0}-{1}',cdi_name,cmp_record_R.get('cmp_abbr'));
		}
		else if(cmp_record_P && cmp_record_P.get('cmp_id')===cmp_id){
			cdi_name = Ext.String.format('{0}-{1}',cdi_name,cmp_record_P.get('cmp_abbr'));
		}
*/
		var cmp_record = conceptArtMapPartStore.findRecord( 'cmp_id', cmp_id, 0, false, false, true ) ;
		if(cmp_record){
			var cmp_abbr = cmp_record.get('cmp_abbr');
			if(Ext.isString(cmp_abbr) && cmp_abbr.length) cdi_name = Ext.String.format('{0}-{1}',cdi_name,cmp_abbr);
		}

/*
		if(cmp_record_L && cmp_record_L.get('cmp_id')===mirror_cmp_id){
			mirror_cdi_name = Ext.String.format('{0}-{1}',mirror_cdi_name,cmp_record_L.get('cmp_abbr'));
		}
		else if(cmp_record_R && cmp_record_R.get('cmp_id')===mirror_cmp_id){
			mirror_cdi_name = Ext.String.format('{0}-{1}',mirror_cdi_name,cmp_record_R.get('cmp_abbr'));
		}
		else if(cmp_record_P && cmp_record_P.get('cmp_id')===mirror_cmp_id){
			mirror_cdi_name = Ext.String.format('{0}-{1}',mirror_cdi_name,cmp_record_P.get('cmp_abbr'));
		}
*/
		cmp_record = conceptArtMapPartStore.findRecord( 'cmp_id', mirror_cmp_id, 0, false, false, true ) ;
		if(cmp_record){
			var cmp_abbr = cmp_record.get('cmp_abbr');
			if(Ext.isString(cmp_abbr) && cmp_abbr.length) mirror_cdi_name = Ext.String.format('{0}-{1}',mirror_cdi_name,cmp_abbr);
		}


		var art_id;
		var attributeStore = Ext.data.StoreManager.lookup(attributeStoreId);
		if(attributeStore && attributeStore.getCount()){
			art_id = attributeStore.getAt(0).get('art_id');
		}

		var mirror_art_id;
		var mirrorAttributeStore = Ext.data.StoreManager.lookup(mirrorAttributeStoreId);
		if(mirrorAttributeStore && mirrorAttributeStore.getCount()){
			mirror_art_id = mirrorAttributeStore.getAt(0).get('art_id');
		}

		var mirrorExistingAttributeProxy = mirrorExistingAttributeStore.getProxy();
		mirrorExistingAttributeProxy.extraParams = mirrorExistingAttributeProxy.extraParams || {};
//		mirrorExistingAttributeProxy.extraParams.cdi_name = cdi_name;
		mirrorExistingAttributeProxy.extraParams.cdi_name = mirror_cdi_name;

//		if(Ext.isEmpty(art_id)){
//			delete mirrorExistingAttributeProxy.extraParams.art_id;
//		}else{
//			mirrorExistingAttributeProxy.extraParams.art_id = art_id;
//		}
		if(Ext.isEmpty(mirror_art_id)){
			delete mirrorExistingAttributeProxy.extraParams.art_id;
		}else{
			mirrorExistingAttributeProxy.extraParams.art_id = mirror_art_id;
		}
		mirrorExistingAttributeStore.loadPage(1,{
			callback: function(records,operation,success){
			}
		});

		var mirrorParentAttributeProxy = mirrorParentAttributeStore.getProxy();
		mirrorParentAttributeProxy.extraParams = mirrorParentAttributeProxy.extraParams || {};
		mirrorParentAttributeProxy.extraParams.cdi_cname = cdi_name;
		mirrorParentAttributeProxy.extraParams.mirror_cdi_cname = mirror_cdi_name;
//		mirrorParentAttributeProxy.extraParams.cmp_id = cmp_id;
		if(Ext.isEmpty(art_id)){
			delete mirrorParentAttributeProxy.extraParams.art_id;
		}else{
			mirrorParentAttributeProxy.extraParams.art_id = art_id;
		}
		if(Ext.isEmpty(mirror_art_id)){
			delete mirrorParentAttributeProxy.extraParams.mirror_art_id;
		}else{
			mirrorParentAttributeProxy.extraParams.mirror_art_id = mirror_art_id;
		}

		mirrorParentAttributeProxy.extraParams.hideParentTerm = Ext.getCmp(idMirrorPrefix+'parent-attribute-display-type-parent').getValue() ? 0 : 1;
		mirrorParentAttributeProxy.extraParams.hideAncestorTerm = Ext.getCmp(idMirrorPrefix+'parent-attribute-display-type-ancestor').getValue() ? 0 : 1;

		mirrorParentAttributeStore.loadPage(1,{
			callback: function(records,operation,success){
			}
		});

		Ext.data.StoreManager.lookup(allExistingAttributeStoreId).loadPage(1);
	});

	var getFMAAllCombobox = function(){
		return {
			itemId: 'fmaAll',
			xtype: 'combobox',
			store: 'fmaAllStore',
			queryMode: 'local',
			displayField: 'cdi_name',
			valueField: 'cdi_name',
			hideTrigger: true,
			anyMatch: true,

			name: 'cdi_name',
			labelWidth: 40,
			fieldLabel: AgLang.cdi_name,
			anchor: '100%',
			selectOnFocus: true,
			enableKeyEvents: true,
			listeners: {
				afterrender: function(field,eOpts){
					var store = field.getStore();
					field.setDisabled(store.isLoading());
					store.on({
						beforeload: function(store, operation, eOpts){
							field.setDisabled(true);
						},
						load: function(store, records, successful, eOpts){
							if(successful) field.setDisabled(false);
						}
					});
				},
				beforeQuery: function( queryPlan, eOpts ){
					var field = queryPlan.combo;
					var value = '';
					if(Ext.isString(queryPlan.query)) value = Ext.String.trim(queryPlan.query);
					queryPlan.cancel = (value.match(/^[A-Z]+/) ? value.length<5 : value.length<3);
					if(queryPlan.cancel){
						if(field.isExpanded) field.collapse();
					}
				},
				select: function(field, records, eOpts){
					var record = records.shift();
					var dropRecord = Ext.create('CONCEPT_TERM',{
						id: record.get('cdi_name'),
						name: record.get('cdi_name_e')
					});
					field.up('form').next('panel').update(dropRecord.getData());
					setLastRecord(dropRecord);
					loadAttributePage();
				},
				specialkey: function(field,e,eOpts){
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
		};
	};

	var getMirrorFMAAllCombobox = function(){
		return {
			xtype: 'combobox',
			store: 'fmaMirrorAllStore',
			queryMode: 'local',
			displayField: 'cdi_name',
			valueField: 'cdi_name',
			hideTrigger: true,
			anyMatch: true,

			name: 'cdi_name',
			labelWidth: 40,
			fieldLabel: AgLang.cdi_name,
			anchor: '100%',
			selectOnFocus: true,
			enableKeyEvents: true,
			listeners: {
				afterrender: function(field,eOpts){
					var store = field.getStore();
					field.setDisabled(store.isLoading());
					store.on({
						beforeload: function(store, operation, eOpts){
							field.setDisabled(true);
						},
						load: function(store, records, successful, eOpts){
							if(successful) field.setDisabled(false);
						}
					});
				},
				beforeQuery: function( queryPlan, eOpts ){
					var field = queryPlan.combo;
					var value = '';
					if(Ext.isString(queryPlan.query)) value = Ext.String.trim(queryPlan.query);
					queryPlan.cancel = (value.match(/^[A-Z]+/) ? value.length<5 : value.length<3);
					if(queryPlan.cancel){
						if(field.isExpanded) field.collapse();
					}
				},
				select: function(field, records, eOpts){
//					console.log(records);
					var record = records.shift();
//					console.log(record);
					var dropRecord = Ext.create('CONCEPT_TERM',{
						id: record.get('cdi_name'),
						name: record.get('cdi_name_e')
					});
					setLastMirrorRecord(dropRecord);

					field.up('form').next('panel').update(getLastMirrorRecord().getData());
					loadMirrorAttributePage.delay(250);
				},
				specialkey: function(field,e,eOpts){
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
		};
	};

	var getFMATemplate = function(){
		return new Ext.XTemplate(
			'<tpl if="this.isEmpty(values.id) == true">',
				'<div unselectable="on" class="x-grid-empty">drag & drop FMA ID from '+AgLang.FMABrowser+'</div>',
			'</tpl>',
			'<tpl if="this.isEmpty(values.id) == false">',
				'<table width=100% height=100% class="hierarchy-center draggable"><tbody><tr><td align=center valign=center>',
					'<table class="draggable-data"><tbody>',
					'<tpl if="this.isEmpty(values.id) == false">',
						'<tr>',
							'<th align="left" valign=top class="id"><label class="id" unselectable="on">'+AgLang.cdi_name+'</label></th>',
							'<td valign=top class="separator"><label class="separator" unselectable="on">:</label></td>',
							'<td class="id"><label class="id unselectable="on"">{id}</label></td>',
						'</tr>',
					'</tpl>',
					'<tpl if="this.isEmpty(values.name) == false">',
						'<tr>',
							'<th align="left" valign=top class="name"><label class="name" unselectable="on">'+AgLang.cdi_name_e+'</label></th>',
							'<td valign=top class="separator"><label class="separator" unselectable="on">:</label></td>',
							'<td class="name"><label class="name" unselectable="on">{name}</label></td>',
						'</tr>',
					'</tpl>',
					'<tpl if="this.isEmpty(values.synonym) == false">',
						'<tr>',
							'<th align="left" valign=top class="synonym"><label class="synonym" unselectable="on">'+AgLang.cdi_syn_e+'</label></th>',
							'<td valign=top class="separator"><label class="separator" unselectable="on">:</label></td>',
							'<td class="synonym">',
								'<tpl for="values.synonym"><div style="white-space:nowrap;"><label class="synonym" unselectable="on">{.}</label></div></tpl>',
							'</td>',
						'</tr>',
					'</tpl>',
					'<tpl if="this.isEmpty(values.definition) == false">',
						'<tr>',
							'<td class="definition" colspan=3><label class="definition" unselectable="on" style="font-weight:bold;">'+AgLang.cdi_def_e+'</label><label class="separator" unselectable="on">&nbsp:&nbsp</label><label class="definition" unselectable="on">{definition}</label></td>',
						'</tr>',
					'</tpl>',
					'</tbody></table>',
				'</td></tr></tbody></table>',
			'</tpl>',
			{
				isEmpty : function(val){
					return Ext.isEmpty(val);
				}
			}
		);
	};

	var getSubjectAfterrender = function(field,eOpts){
		field.update({});
		var el = field.getEl();
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
				if(Ext.isArray(dropData) && dropData.length) dropData = dropData[0];
				var dropRecord = Ext.create('CONCEPT_TERM',dropData||{});
				field.update(dropRecord.getData());
				setLastRecord(dropRecord);
				loadAttributePage();
/*
				if(Ext.isString(dropData['data-boundview']) && dropData['data-boundview'].length){
					var gridview = Ext.getCmp(dropData['data-boundview']);
					var gridpanel = gridview ? gridview.up('gridpanel') : null;
					var button = gridpanel ? gridpanel.down('button#draggable') : null;
					if(button && button.pressed){
						Ext.Array.each(gridview.getNodes(), function(node, index){
							Ext.get(node).set({draggable:button.pressed},true);
							if(index==0){
							}
						});
					}
				}
*/
			}
		});
	};

	var getMirrorSubjectAfterrender = function(field,eOpts){
		field.update({});
		var el = field.getEl();
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
				if(Ext.isArray(dropData) && dropData.length) dropData = dropData[0];
				var dropRecord = Ext.create('CONCEPT_TERM',dropData||{});
				setLastMirrorRecord(dropRecord);
				field.update(getLastMirrorRecord().getData());
				loadMirrorAttributePage.delay(250);

				var attributeStore = Ext.data.StoreManager.lookup(attributeStoreId);
				attributeStore.fireEvent('datachanged', attributeStore);
			}
		});
	};

	var getAttributeStore = function(storeId){
		return Ext.create('Ext.data.Store', {
			storeId: storeId,
			model: 'PARTS',
//			model: 'OBJ_EDIT',
			sorters: [{
				property: 'art_name',
				direction: 'ASC'
			}],
			proxy: {
				type: 'ajax',
				timeout: 300000,
				pageParam: undefined,
				startParam: undefined,
				limitParam: undefined,
				sortParam: undefined,
				groupParam: undefined,
				filterParam: undefined,
				api: {
					create  : 'api-upload-file-list.cgi?cmd=update_concept_art_map',
					read    : 'api-upload-file-list.cgi?cmd=read',
					update  : 'api-upload-file-list.cgi?cmd=update_concept_art_map',
					destroy : 'api-upload-file-list.cgi?cmd=destroy',
				},
				actionMethods : {
					create : 'POST',
					read   : 'POST',
					update : 'POST',
					destroy: 'POST'
				},
				reader: {
					type: 'json',
					root: 'datas',
					totalProperty: 'total',
					listeners: {
						exception : function(){
						}
					}
				},
				writer: {
					type: 'json',
					root: 'datas',
					allowSingle: false,
					encode: true
				}
			},
			listeners: {
				beforeload: function(store,operation,eOpts){
					if(!self.beforeloadStore(store)) return false;
					var p = store.getProxy();
					p.extraParams = p.extraParams || {};
					delete p.extraParams.current_datas;
					delete p.extraParams._ExtVerMajor;
					delete p.extraParams._ExtVerMinor;
					delete p.extraParams._ExtVerPatch;
					delete p.extraParams._ExtVerBuild;
					delete p.extraParams._ExtVerRelease;
				},
				beforesync: function(options,eOpts){
					var store = this;
					if(!self.beforeloadStore(store)) return false;
					var p = store.getProxy();
					p.extraParams = p.extraParams || {};
					delete p.extraParams.current_datas;
					delete p.extraParams._ExtVerMajor;
					delete p.extraParams._ExtVerMinor;
					delete p.extraParams._ExtVerPatch;
					delete p.extraParams._ExtVerBuild;
					delete p.extraParams._ExtVerRelease;
				}
			}
		});
	};

	var getAttributeGridColumns = function(){
		return [
			{text: '&#160;',            dataIndex: 'selected',     stateId: 'selected',      width: 30, minWidth: 30, hidden: true, hideable: false, sortable: true, draggable: false, resizable: false, xtype: 'agselectedcheckcolumn'},
			{
				text: '&#160;',            dataIndex: 'art_tmb_path',     stateId: 'art_tmb_path',      width: 24, minWidth: 24, hidden: false, hideable: false, sortable: true, draggable: false, resizable: false,
				renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
					if(record.data.seg_color){
//								metaData.style = 'background:'+record.data.seg_color+';';
					}
					metaData.innerCls = 'art_tmb_path';
					return value;
				}
			},
			{text: AgLang.art_id,       dataIndex: 'art_id',       stateId: 'art_id',        width: 54, minWidth: 54, hidden: false, hideable: true},
			{text: AgLang.cdi_name,     dataIndex: 'cdi_name',     stateId: 'cdi_name',      width: 80, minWidth: 80, hidden: false, hideable: true, xtype: 'agcolumncdiname' },
			{text: AgLang.cmp_abbr,     dataIndex: 'cmp_id',       stateId: 'cmp_id',        width: 40, minWidth: 40, hidden: false, hideable: true, xtype: 'agcolumnconceptartmappart' },
			{text: AgLang.cdi_name_e,   dataIndex: 'cdi_name_e',   stateId: 'cdi_name_e',    flex: 2, minWidth: 80, hidden: true, hideable: true, xtype: 'agcolumncdinamee' },
			{text: 'System',            dataIndex: 'seg_name',     stateId: 'seg_name',      flex: 1.0, minWidth: 50, hidden: true,  hideable: true,  xtype: 'agsystemcolumn'},
			{text: AgLang.category,     dataIndex: 'arta_category',stateId: 'arta_category', flex: 1, minWidth: 50, hidden: true, hideable: true},
			{text: AgLang.class_name,   dataIndex: 'arta_class',   stateId: 'arta_class',    width: 36, minWidth: 36, hidden: true, hideable: true},
			{text: AgLang.comment,      dataIndex: 'arta_comment', stateId: 'arta_comment',  flex: 2, minWidth: 80, hidden: true, hideable: true},
			{text: AgLang.judge,        dataIndex: 'arta_judge',   stateId: 'arta_judge',    flex: 1, minWidth: 50, hidden: true, hideable: true},

			{text: AgLang.arto_id,      dataIndex: 'arto_id',      stateId: 'arto_id',       width: 60, minWidth: 60, hidden: true, hideable: true, sortable: false},
			{text: AgLang.arto_filename,dataIndex: 'arto_filename',stateId: 'arto_filename', flex: 2, minWidth: 80, hidden: true, hideable: true, sortable: false},
			{text: AgLang.arto_comment, dataIndex: 'arto_comment', stateId: 'arto_comment',  flex: 2, minWidth: 80, hidden: true, hideable: true, sortable: false},

			{text: 'Color',             dataIndex: 'color',        stateId: 'color',         width: 40, minWidth: 40, hidden: true,  hideable: false,  xtype: 'agcolorcolumn'},
			{text: 'Opacity',           dataIndex: 'opacity',      stateId: 'opacity',       width: 44, minWidth: 44, hidden: true,  hideable: false,  xtype: 'agopacitycolumn'},
			{text: 'Hide',              dataIndex: 'remove',       stateId: 'remove',        width: 40, minWidth: 40, hidden: true,  hideable: false,  xtype: 'agcheckcolumn'},
			{text: 'Scalar',            dataIndex: 'scalar',       stateId: 'scalar',        width: 40, minWidth: 40, hidden: true,  hideable: false,  xtype: 'agnumbercolumn', format: '0', editor: 'numberfield'},

			{text: AgLang.file_name,    dataIndex: 'art_filename', stateId: 'art_filename',  flex: 2, minWidth: 80, hidden: true, hideable: true},
			{text: 'Path',              dataIndex: 'art_path',     stateId: 'art_path',      flex: 1, minWidth: 50, hidden: true,  hideable: false},
			{text: AgLang.file_size,    dataIndex: 'art_data_size',stateId: 'art_data_size', width: 59,  hidden: true, hideable: true, xtype: 'agfilesizecolumn'},

			{text: AgLang.xmax,         dataIndex: 'art_xmax',     stateId: 'art_xmax',      width: 59,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.xmin,         dataIndex: 'art_xmin',     stateId: 'art_xmin',      width: 59,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.xcenter,      dataIndex: 'art_xcenter',  stateId: 'art_xcenter',   width: 59,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.ymax,         dataIndex: 'art_ymax',     stateId: 'art_ymax',      width: 59,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.ymin,         dataIndex: 'art_ymin',     stateId: 'art_ymin',      width: 59,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.ycenter,      dataIndex: 'art_ycenter',  stateId: 'art_ycenter',   width: 59,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.zmax,         dataIndex: 'art_zmax',     stateId: 'art_zmax',      width: 59,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.zmin,         dataIndex: 'art_zmin',     stateId: 'art_zmin',      width: 59,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.zcenter,      dataIndex: 'art_zcenter',  stateId: 'art_zcenter',   width: 59,  hidden: false, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.volume,       dataIndex: 'art_volume',   stateId: 'art_volume',    width: 59,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},

			{text: AgLang.timestamp,    dataIndex: 'art_timestamp',stateId: 'art_timestamp', width: self.ART_TIMESTAMP_WIDTH, hidden: false,  hideable: true, xtype: 'datecolumn',     format: self.ART_TIMESTAMP_FORMAT },
//					{text: AgLang.upload_modified, dataIndex: 'art_upload_modified',stateId: 'art_upload_modified', width: 112,  hidden: true, hideable: true, xtype: 'datecolumn', format: self.FORMAT_DATE_TIME },
			{text: AgLang.cm_entry,     dataIndex: 'cm_entry',     stateId: 'cm_entry',      width: 67, hidden: true, hideable: true, xtype: 'datecolumn',     format: self.FORMAT_DATE }
		];
	};

	var allExistingAttributeStore = getStore(allExistingAttributeStoreId).on({
		beforeload: function(store,operation,eOpts){
			var proxy = store.getProxy();
//			console.log(proxy);
			proxy.extraParams = proxy.extraParams || {};
			proxy.extraParams.hideChildrenTerm=1;
			proxy.extraParams.hideAncestorTerm=0;
			proxy.extraParams.hideParentTerm=1;
			proxy.extraParams.hideDescendantsTerm=0;
			proxy.extraParams.hidePairTerm=1;

			delete proxy.extraParams.cdi_name;
			delete proxy.extraParams.art_id;
			delete proxy.extraParams.mirror_cdi_name;
			delete proxy.extraParams.mirror_art_id;
			delete proxy.extraParams.exists_art_ids;

			if(store.getCount()){
				var exists_art_ids = [];
				store.each(function(record){
					exists_art_ids.push(record.get('art_id'));
				});
				proxy.extraParams.exists_art_ids = Ext.encode(exists_art_ids);
			}

			var conceptArtMapPartStore = Ext.data.StoreManager.lookup('conceptArtMapPartStore');
			var dropRecord = getLastRecord();
			var cdi_name = dropRecord.get('cdi_name');
			if(!Ext.isEmpty(cdi_name)){
				var cmp_id = dropRecord.get('cmp_id');
/*
				var cmp_record_L = conceptArtMapPartStore.findRecord('cmp_abbr', 'L', 0, false, false, true );
				var cmp_record_R = conceptArtMapPartStore.findRecord('cmp_abbr', 'R', 0, false, false, true );
				var cmp_record_P = conceptArtMapPartStore.findRecord('cmp_abbr', 'P', 0, false, false, true );
				if(cmp_record_L && cmp_record_L.get('cmp_id')===cmp_id){
					proxy.extraParams.cdi_name = Ext.String.format('{0}-{1}',cdi_name,cmp_record_L.get('cmp_abbr'));
				}
				else if(cmp_record_R && cmp_record_R.get('cmp_id')===cmp_id){
					proxy.extraParams.cdi_name = Ext.String.format('{0}-{1}',cdi_name,cmp_record_R.get('cmp_abbr'));
				}
				else if(cmp_record_P && cmp_record_P.get('cmp_id')===cmp_id){
					proxy.extraParams.cdi_name = Ext.String.format('{0}-{1}',cdi_name,cmp_record_P.get('cmp_abbr'));
				}
*/
				var cmp_record = conceptArtMapPartStore.findRecord( 'cmp_id', cmp_id, 0, false, false, true ) ;
				if(cmp_record){
					var cmp_abbr = cmp_record.get('cmp_abbr');
					if(Ext.isString(cmp_abbr) && cmp_abbr.length) proxy.extraParams.cdi_name = Ext.String.format('{0}-{1}',cdi_name,cmp_abbr);
				}
				else{
					proxy.extraParams.cdi_name = cdi_name;
				}
				var attributeStore = Ext.data.StoreManager.lookup(attributeStoreId);
				if(attributeStore && attributeStore.getCount()){
					proxy.extraParams.art_id = attributeStore.getAt(0).get('art_id');
				}

				var mirror_checkboxfield = Ext.getCmp(aOpt.id).down('checkboxfield#mirror');
				if(mirror_checkboxfield && mirror_checkboxfield.getValue() && !mirror_checkboxfield.isDisabled()){
					var mirrorDropRecord = getLastMirrorRecord();
					var mirror_cdi_name = mirrorDropRecord.get('cdi_name');
					if(!Ext.isEmpty(mirror_cdi_name)){
						var mirror_cmp_id = mirrorDropRecord.get('cmp_id');
/*
						if(cmp_record_L && cmp_record_L.get('cmp_id')===mirror_cmp_id){
							proxy.extraParams.mirror_cdi_name = Ext.String.format('{0}-{1}',mirror_cdi_name,cmp_record_L.get('cmp_abbr'));
						}
						else if(cmp_record_R && cmp_record_R.get('cmp_id')===mirror_cmp_id){
							proxy.extraParams.mirror_cdi_name = Ext.String.format('{0}-{1}',mirror_cdi_name,cmp_record_R.get('cmp_abbr'));
						}
						else if(cmp_record_P && cmp_record_P.get('cmp_id')===mirror_cmp_id){
							proxy.extraParams.mirror_cdi_name = Ext.String.format('{0}-{1}',mirror_cdi_name,cmp_record_P.get('cmp_abbr'));
						}
*/
						var cmp_record = conceptArtMapPartStore.findRecord( 'cmp_id', mirror_cmp_id, 0, false, false, true ) ;
						if(cmp_record){
							var cmp_abbr = cmp_record.get('cmp_abbr');
							if(Ext.isString(cmp_abbr) && cmp_abbr.length) proxy.extraParams.mirror_cdi_name = Ext.String.format('{0}-{1}',mirror_cdi_name,cmp_abbr);
						}
						else{
							proxy.extraParams.mirror_cdi_name = mirror_cdi_name;
						}
						var mirrorAttributeStore = Ext.data.StoreManager.lookup(mirrorAttributeStoreId);
						if(mirrorAttributeStore && mirrorAttributeStore.getCount()){
							proxy.extraParams.mirror_art_id = mirrorAttributeStore.getAt(0).get('art_id');
						}
					}
				}
			}
			if(Ext.isEmpty(proxy.extraParams.cdi_name) && Ext.isEmpty(proxy.extraParams.art_id) && Ext.isEmpty(proxy.extraParams.mirror_cdi_name) && Ext.isEmpty(proxy.extraParams.mirror_art_id) && Ext.isEmpty(proxy.extraParams.exists_art_ids)){
				return false;
			}else{
				return true;
			}
		},
		load: function(store,records,successful,eOpts){
			if(successful && Ext.isArray(records) && records.length){
				if(self.syncUploadObjectStore) self.syncUploadObjectStore(records);
				if(self.syncPalletPartsStore) self.syncPalletPartsStore(records);
				if(self.syncPickSearchStore) self.syncPickSearchStore(records);
			}
		}
	});
	var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
	var palletPartsStore = Ext.data.StoreManager.lookup('palletPartsStore');
	var pickSearchStore = Ext.data.StoreManager.lookup('pickSearchStore');
//	console.log(uploadObjectStore);
//	console.log(palletPartsStore);
//	console.log(pickSearchStore);

	if(uploadObjectStore){
		uploadObjectStore.on({
			load: function(store,rs,successful,eOpts){
				var records = getStore(allExistingAttributeStoreId).getRange();
				if(Ext.isArray(records) && records.length){
					if(self.syncUploadObjectStore) self.syncUploadObjectStore(records);
					if(self.syncPalletPartsStore) self.syncPalletPartsStore(records);
				}
			}
		});
	}
	if(pickSearchStore){
		pickSearchStore.on({
			load: function(store,rs,successful,eOpts){
				var records = getStore(allExistingAttributeStoreId).getRange();
				if(Ext.isArray(records) && records.length){
					if(self.syncPickSearchStore) self.syncPickSearchStore(records);
					if(self.syncPalletPartsStore) self.syncPalletPartsStore(records);
				}
			}
		});
	}




//FMA52862
//FMA54699

	var mapping_mng_win = Ext.create('Ext.panel.Panel', {
		id: aOpt.id,
		itemId: aOpt.id,
		stateId: aOpt.id,
		iconCls: aOpt.iconCls,
		title: aOpt.title,
		header: false,
		region: 'west',
		split: true,
		collapsed: false,
		collapsible: true,
//		flex: 1,
		width: 500,
		minWidth: 500,
		minHeight: 300,
		autoScroll: true,
		border: true,
		closable: false,
		closeAction: 'hide',
		buttons: [{
			disabled: true,
			itemId: 'submit',
			text: 'submit',
			listeners: {
				afterrender: function(field){
					var attributeStore = Ext.data.StoreManager.lookup(attributeStoreId);
					var mirrorAttributeStore = Ext.data.StoreManager.lookup(mirrorAttributeStoreId);
					attributeStore.on({
						datachanged: function(store, eOpts){
							var cdi_name = getLastRecord().get('cdi_name');
							var cmp_id = getLastRecord().get('cmp_id');
							var disabled = Ext.isEmpty(cdi_name);
							if(!disabled){
								disabled = true;
								attributeStore.each(function(record){
									if(record.get('cdi_name')===cdi_name && record.get('cmp_id')===cmp_id && record.get('cm_use') && !record.get('never_current')) return true;
									disabled = false;
									return false;
								});
							}
							if(disabled){
								var mirror_cdi_name;
								var mirror_cmp_id;
								var mirror_checkboxfield = Ext.getCmp(aOpt.id).down('checkboxfield#mirror');
								if(mirror_checkboxfield && mirror_checkboxfield.getValue() && !mirror_checkboxfield.isDisabled()){
									mirror_cdi_name = getLastMirrorRecord().get('cdi_name');
									mirror_cmp_id = getLastMirrorRecord().get('cmp_id');
									disabled = Ext.isEmpty(mirror_cdi_name);
								}
								if(!disabled){
									disabled = true;
									mirrorAttributeStore.each(function(record){
										if(record.get('cdi_name')===mirror_cdi_name && record.get('cmp_id')===mirror_cmp_id && record.get('cm_use') && !record.get('never_current')) return true;
										disabled = false;
										return false;
									});
								}
							}
							field.setDisabled(disabled);
						},
						buffer:250
					});
				},
				click: function(field){
					var attributeStore = Ext.data.StoreManager.lookup(attributeStoreId);
					var mirrorAttributeStore = Ext.data.StoreManager.lookup(mirrorAttributeStoreId);
					var data = attributeStore.getAt(0).getData();
					data.cdi_name = getLastRecord().get('cdi_name');
					data.cdi_name_e = getLastRecord().get('cdi_name_e');
					data.cmp_id = 0;

					var cmp_id = getLastRecord().get('cmp_id');
					var conceptArtMapPartStore = Ext.data.StoreManager.lookup('conceptArtMapPartStore');
/*
					var cmp_record_L = conceptArtMapPartStore.findRecord('cmp_abbr', 'L', 0, false, false, true );
					var cmp_record_R = conceptArtMapPartStore.findRecord('cmp_abbr', 'R', 0, false, false, true );
					var cmp_record_P = conceptArtMapPartStore.findRecord('cmp_abbr', 'P', 0, false, false, true );
					if(cmp_record_L && cmp_record_L.get('cmp_id')===cmp_id){
						data.cdi_name = Ext.String.format('{0}-{1}',data.cdi_name,cmp_record_L.get('cmp_abbr'));
					}
					else if(cmp_record_R && cmp_record_R.get('cmp_id')===cmp_id){
						data.cdi_name = Ext.String.format('{0}-{1}',data.cdi_name,cmp_record_R.get('cmp_abbr'));
					}
					else if(cmp_record_P && cmp_record_P.get('cmp_id')===cmp_id){
						data.cdi_name = Ext.String.format('{0}-{1}',data.cdi_name,cmp_record_P.get('cmp_abbr'));
					}
*/
					var cmp_record = conceptArtMapPartStore.findRecord( 'cmp_id', cmp_id, 0, false, false, true ) ;
					if(cmp_record){
						var cmp_abbr = cmp_record.get('cmp_abbr');
						if(Ext.isString(cmp_abbr) && cmp_abbr.length) data.cdi_name = Ext.String.format('{0}-{1}',data.cdi_name,cmp_abbr);
					}


					var panel = Ext.getCmp(aOpt.id);
					var mirror_checkboxfield = panel.down('checkboxfield#mirror');
					if(mirror_checkboxfield && mirror_checkboxfield.getValue() && !mirror_checkboxfield.isDisabled()){
						data.mirror = true;
						data.mirror_art_id = mirrorAttributeStore.getAt(0).get('art_id');
						data.mirror_cdi_name = getLastMirrorRecord().get('cdi_name');
						data.mirror_cdi_name_e = getLastMirrorRecord().get('cdi_name_e');
						data.mirror_cmp_id = 0;

						var mirror_cmp_id = getLastMirrorRecord().get('cmp_id');
/*
						if(cmp_record_L && cmp_record_L.get('cmp_id')===mirror_cmp_id){
							data.mirror_cdi_name = Ext.String.format('{0}-{1}',data.mirror_cdi_name,cmp_record_L.get('cmp_abbr'));
						}
						else if(cmp_record_R && cmp_record_R.get('cmp_id')===mirror_cmp_id){
							data.mirror_cdi_name = Ext.String.format('{0}-{1}',data.mirror_cdi_name,cmp_record_R.get('cmp_abbr'));
						}
						else if(cmp_record_P && cmp_record_P.get('cmp_id')===mirror_cmp_id){
							data.mirror_cdi_name = Ext.String.format('{0}-{1}',data.mirror_cdi_name,cmp_record_P.get('cmp_abbr'));
						}
*/
						cmp_record = conceptArtMapPartStore.findRecord( 'cmp_id', mirror_cmp_id, 0, false, false, true ) ;
						if(cmp_record){
							var cmp_abbr = cmp_record.get('cmp_abbr');
							if(Ext.isString(cmp_abbr) && cmp_abbr.length) data.mirror_cdi_name = Ext.String.format('{0}-{1}',data.mirror_cdi_name,cmp_abbr);
						}

					}
					var record = Ext.create('OBJ_EDIT',data);
//					console.log(record.getData());

					var proxy = attributeStore.getProxy();
					var params = Ext.Object.merge({},self.getExtraParams() || {},{datas: Ext.encode([record.getData()])});
					delete params.current_datas;
					delete params._ExtVerMajor;
					delete params._ExtVerMinor;
					delete params._ExtVerPatch;
					delete params._ExtVerBuild;
					delete params._ExtVerRelease;

//					console.log(params);
					panel.setLoading(true);
//					return;
					Ext.Ajax.request({
						url: proxy.api.update,
						method: proxy.actionMethods.update,
						timeout: proxy.timeout,
						params: params,
						callback: function(options,success,response){
							var panel = Ext.getCmp(aOpt.id);
							panel.setLoading(false);
							var json;
							try{json = Ext.decode(response.responseText)}catch(e){};
							if(success==false || Ext.isEmpty(json) || Ext.isEmpty(json.success) || json.success==false){
								if(Ext.isEmpty(json) || Ext.isEmpty(json.msg)) return;
								Ext.Msg.show({
									title: field.text || AgLang.replace,
									msg: json.msg,
									buttons: Ext.Msg.OK,
									icon: Ext.Msg.ERROR
								});
							}
							else{
								var records = [];
								if(Ext.isArray(json.datas)){
									var attributeStore = Ext.data.StoreManager.lookup(attributeStoreId);
									var attributeModel = Ext.getClassName(attributeStore.model);
									json.datas.forEach(function(data){
										records.push(Ext.create(attributeModel,data));
									});
								}
//								if(records.length) self.syncMappingMngStore(records,false);
//								loadAttributePage();
//								var mirror_checkboxfield = panel.down('checkboxfield#mirror');
//								if(mirror_checkboxfield && mirror_checkboxfield.getValue() && !mirror_checkboxfield.isDisabled()){
//									loadMirrorAttributePage.delay(250);
//								}
//								var attributeStore = Ext.data.StoreManager.lookup(attributeStoreId);
//								attributeStore.fireEvent('datachanged', attributeStore);

								if(records.length){
									if(mirror_checkboxfield && mirror_checkboxfield.getValue() && !mirror_checkboxfield.isDisabled()){
										if(self.reloadUploadObjectStore) self.reloadUploadObjectStore();
									}else{
										if(self.syncUploadObjectStore) self.syncUploadObjectStore(records);
									}
									if(self.syncPalletPartsStore) self.syncPalletPartsStore(records);
									if(self.syncPickSearchStore) self.syncPickSearchStore(records);
								}

								if(mirror_checkboxfield && mirror_checkboxfield.getValue() && !mirror_checkboxfield.isDisabled()){
									mirror_checkboxfield.setValue(false);
								}
								attributeStore.removeAll();
								mirrorAttributeStore.removeAll();

								Ext.data.StoreManager.lookup(existingAttributeStoreId).removeAll();
								Ext.data.StoreManager.lookup(parentAttributeStoreId).removeAll();

								Ext.data.StoreManager.lookup(mirrorExistingAttributeStoreId).removeAll();
								Ext.data.StoreManager.lookup(mirrorParentAttributeStoreId).removeAll();

								Ext.data.StoreManager.lookup(allExistingAttributeStoreId).loadPage(1);

								setLastRecord();
								var panel = Ext.getCmp(idPrefix+'subject-panel');
								panel.update({});
								panel.prev('form').down('combobox').setValue('');

								setLastMirrorRecord();
								var mirror_panel = Ext.getCmp(idMirrorPrefix+'subject-panel');
								mirror_panel.update({});
								mirror_panel.prev('form').down('combobox').setValue('');
							}
						}
					});
				}
			}
		}],

		dockedItems: [{
			xtype: 'toolbar',
			dock: 'top',
			items: [{
				xtype: 'tbtext',
				text : '<b>'+aOpt.title+'</b>'
			},'->','-',{
				itemId: 'concept-build-combobox',
				id: idPrefix+'concept-build-combobox',
				width: 180,
				xtype: 'combobox',
				store: 'conceptBuildStore',
				queryMode: 'local',
				displayField: 'display',
				valueField: 'value',
				editable: false,
				disabled: true
			},'-',{
				text: AgLang.subclass_list,
				iconCls: 'pallet_download',
				handler: function(b,e){
					var href = './api-concept-data-info-user-data.cgi?cmd=download';
					window.location.href = href;
				}
			}]
		}],

		layout: {
			type: 'vbox',
			align: 'stretch'
		},
		defaults: {
			minHeight: 100,
			border: true
		},
		items: [{
			region: 'north',
//			flex:1,
//			height: 120,
			height: 147,
			layout: {
				type: 'hbox',
				align: 'stretch'
			},
			border: false,
			items: [{
//				title: 'aa',
				dockedItems: [{
					xtype: 'toolbar',
					dock: 'top',
					items: [{
						xtype: 'tbtext',
						text : '<b>'+AgLang.subject+'</b>'
					},'->','-',{
						xtype: 'button',
						iconCls: 'package_edit-btn',
						text: 'Syn',
						tooltip: 'Synonym editing',
						listeners: {
							afterrender: function(button){
								button.setDisabled(true);
								var combobox = button.up('panel').down('combobox#fmaAll');
								combobox.on({
									change: function(combobox,newValue,oldValue,eOpts){
										button.setDisabled(true);
									},
									select: function(combobox,records,eOpts){
//										console.log('select',records,combobox.getModelData(),combobox.findRecordByValue(combobox.getValue()));
										button.setDisabled(false);
									}
								});
							},
							click: function(button){
								button.setDisabled(true);
//								self.openFMABrowser(getLastRecord().get('id') || '');
								var extraParams = self.getExtraParams() || {};
//								console.log('click',extraParams);
								var combobox = button.up('panel').down('combobox#fmaAll');
								var record = combobox.findRecordByValue(combobox.getValue());
								var cdi_id = record.get('cdi_id');
								var cdi_name = record.get('cdi_name');
								var cdi_name_e = record.get('cdi_name_e');
								var params = {
									ci_id: extraParams.ci_id,
									cb_id: extraParams.cb_id,
									cdi_id: cdi_id
								};
								var title = Ext.util.Format.format('{0} [ {1} ] {2}',button.tooltip,cdi_name,cdi_name_e);

								Ext.Ajax.request({
									url: 'api-fma-list.cgi?cmd=read_synonym',
									autoAbort: true,
									method: 'POST',
									params: params,
									callback: function(options,success,response){
										button.setDisabled(false);
										var json;
										try{json = Ext.decode(response.responseText)}catch(e){};
										if(!success || Ext.isEmpty(json) || Ext.isEmpty(json.success) || !json.success){
//											_loadAttributePage();
											Ext.Msg.show({
												title: title,
												msg: 'シノニムの取得に失敗しました。',
												buttons: Ext.Msg.OK,
												icon: Ext.Msg.ERRIR
											});
											return;
										}

										var filterFn = function(record) {
											try{
												return record.get('is_deleted') === false;
											}catch(e){
												console.error(e);
												return false;
											}
										};
										var storeId = 'synonymStore';
										var synonym_store = Ext.data.StoreManager.lookup(storeId);
										if(Ext.isEmpty(synonym_store)){
											synonym_store = Ext.create('Ext.data.Store', {
												storeId: storeId,
												fields: [
													{
														name:'synonym',
														type:'string',
														convert: function(v,record){
															if(Ext.isEmpty(v)){
																return record.get('cs_name');
															}
															else{
																return v;
															}
														}
													},
													{
														name:'is_edited',
														type:'boolean',
														defaultValue: false
													},
													{
														name:'is_deleted',
														type:'boolean',
														defaultValue: false
													},
													{
														name:'cds_added',
														type:'boolean',
														defaultValue: false
													},
													{
														name:'cds_added_auto',
														type:'boolean',
														defaultValue: false
													},
													{
														name:'cds_order',
														type:'int',
														defaultValue: 0
													},
													{
														name:'cs_name',
														type:'string',
														useNull: true,
														defaultValue: null
													},
													{
														name:'cs_id',
														type:'int',
														useNull: true,
														defaultValue: null
													},
													{
														name:'cds_id',
														type:'int',
														useNull: true,
														defaultValue: null
													},
													{
														name:'cds_bid',
														type:'int',
														useNull: true,
														defaultValue: null
													}
												],
												filters: [filterFn]
											});
										}

										var org_synonym_arr = [];
										if(Ext.isArray(json.datas) && json.datas.length && Ext.isObject(json.datas[0])){
											var loadRecords = [];
											if(Ext.isEmpty(json.datas[0]['cds'])){
												loadRecords = Ext.Array.map(json.datas[0]['synonym']||[],function(synonym){
													org_synonym_arr.push(synonym);
													var hash = {};
													hash['cs_name'] = synonym;
													return hash;
												});
											}
											else if(Ext.isArray(json.datas[0].cd_syn)){
												loadRecords = Ext.Array.clone(json.datas[0]['cds']);
												org_synonym_arr = Ext.Array.map(loadRecords, function(data){ return data['cs_name']; });
											}
											if(loadRecords.length>0){
												synonym_store.removeAll(true);
												synonym_store.add( loadRecords );
											}
											else{
												synonym_store.removeAll(false);
											}
										}

										Ext.create('Ext.window.Window', {
											title: title,
											iconCls: button.iconCls,
											animateTarget: button.el,
											modal:true,
											height: parseInt(($(window).height()/5*3)),
											width: parseInt(($(window).width()/5*3)),
											minHeight: 300,
											minWidth: 500,
											layout: 'fit',
											items: [{
												xtype: 'gridpanel',
												border: true,
												columnLines: true,
												viewConfig: {
													stripeRows: true
												},
												columns: [{
													xtype: 'rownumberer'
												},{
													header: 'Synonym',
													dataIndex: 'synonym',
													flex: 1,
													editor: {
														xtype: 'textfield',
														allowBlank: false
													}
												},{
													xtype: 'checkcolumn',
													header: 'added',
													dataIndex: 'cds_added',
													draggable: false,
													hideable: false,
													resizable: false,
													sortable: false,
													width: 50,
													listeners: {
														beforecheckchange: function(){
															return false;
														}
													}
												},{
													xtype: 'checkcolumn',
													header: 'auto',
													dataIndex: 'cds_added_auto',
													draggable: false,
													hideable: false,
													resizable: false,
													sortable: false,
													width: 50,
													listeners: {
														beforecheckchange: function(){
															return false;
														}
													}
												}],
												store: synonym_store,
												selType: 'rowmodel',
												selModel: {
													mode: 'MULTI'
												},
												plugins: [
													Ext.create('Ext.grid.plugin.CellEditing', {
														clicksToEdit: 2
													})
												],
												listeners: {
													edit: function(editor, e, eOpts){
														var value = Ext.String.trim(e.value);
//														value = value.substr(0,1).toUpperCase() + value.substr(1).toLowerCase();
														e.record.set('synonym', value);
														if(value != e.record.get('cs_name')){
															e.record.set('is_edited', true);
														}else{
															e.record.set('is_edited', false);
														}
														e.record.commit();
	//													console.log(e.record.getData());
													}
												}
											}],
											dockedItems: [{
												xtype: 'toolbar',
												dock: 'top',
												defaults: {minWidth: 50},
												items: [{
													text: 'Add',
													itemId: 'add',
													listeners: {
														click: function(button){
															try{
																Ext.Msg.show({
																	title:'Synonym',
																	msg: 'Please enter the synonym to add',
																	animateTarget: button.el,
																	buttons: Ext.Msg.OKCANCEL,
																	defaultFocus: 'cancel',
																	icon: Ext.Msg.QUESTION,
																	minWidth: 500,
																	modal: true,
																	prompt: true,
																	fn: function(buttonId,text){
																		if (buttonId == 'ok' && Ext.isString(text) && Ext.String.trim(text).length>0){
																			var data = {};
																			text = Ext.String.trim(text);
//																			text = text.substr(0,1).toUpperCase() + text.substr(1).toLowerCase();
																			data['synonym'] = text;
																			data['cds_added'] = true;
																			data['is_edited'] = true;
																			synonym_store.add(data);
																		}
																	}
																});
															}catch(e){
															}
														}
													}
												},'->',{
													disabled: true,
													text: 'Delete',
													itemId: 'delete',
													listeners: {
														afterrender: function(button){
															var gridpanel = button.up('window').down('gridpanel');
															var selmodel = gridpanel.getSelectionModel();
															selmodel.on({
																selectionchange: function( selmodel, selected, eOpts ){
																	button.setDisabled(selected.length>0 ? false : true);
																}
															});
														},
														click: function(button){
															try{
																var gridpanel = button.up('window').down('gridpanel');
																var store = gridpanel.getStore();
																var selmodel = gridpanel.getSelectionModel();
																var remove_records = [];
																Ext.Array.each(selmodel.getSelection(), function(record){
																	if(Ext.isEmpty(record.get('cs_name'))){
																		remove_records.push(record);
																	}
																	else{
																		record.beginEdit();
																		record.set('is_deleted',true);
																		record.commit(true,['is_deleted']);
																		record.endEdit(true,['is_deleted']);
	//																	console.log(record.getData());
																	}
																});
																if(remove_records.length>0){
																	store.remove(remove_records);
																}
																store.filter();
															}catch(e){
															}
														}
													}
												}]
											},{
												xtype: 'toolbar',
												dock: 'bottom',
												ui: 'footer',
												defaults: {minWidth: 60},
												items: ['->',{
													text: 'Save',
													itemId: 'save',
													listeners: {
														click: function(button){
															try{
																var win = button.up('window');
																var chg_synonym_arr = Ext.Array.map(synonym_store.getRange(), function(record){ return record.get('synonym'); });
																if(Ext.Array.equals(org_synonym_arr,chg_synonym_arr)){
																	button.up('window').close();
																	return;
																}

																var params = {
																	ci_id: extraParams.ci_id,
																	cb_id: extraParams.cb_id,
																	cdi_id: cdi_id,
																	cdi_name: cdi_name
																};
																synonym_store.clearFilter(true);
																params['cd_syn'] = Ext.JSON.encode(Ext.Array.map(synonym_store.getRange(), function(record){
																	return record.getData();
																}));
																synonym_store.filter({filterFn:filterFn});

																win.setLoading(true);

																Ext.Ajax.request({
																	url: 'api-fma-list.cgi?cmd=update_synonym',
																	timeout: 300000,
																	params: params,
																	success: function(response){
																		win.setLoading(false);
																		var rtn = Ext.decode(response.responseText);
																		if(Ext.isObject(rtn)){
																			if(rtn.success){
																				win.close();
																				_loadAttributePage();
																			}
																			else if(Ext.isString(rtn.msg) && rtn.msg.length){
																				Ext.Msg.show({
																					title: title,
																					msg: rtn.msg,
																					buttons: Ext.Msg.OK,
																					icon: Ext.Msg.ERROR,
																					fn: function(buttonId,text,opt){
																					}
																				});
																			}
																			else{
																				Ext.Msg.show({
																					title: title,
																					msg: 'Unknown error',
																					buttons: Ext.Msg.OK,
																					icon: Ext.Msg.ERROR,
																					fn: function(buttonId,text,opt){
																					}
																				});
																			}
																		}
																		else{
																			Ext.Msg.show({
																				title: button.text,
																				msg: 'Unknown error',
																				buttons: Ext.Msg.OK,
																				icon: Ext.Msg.ERROR,
																				fn: function(buttonId,text,opt){
																				}
																			});
																		}
																	},
																	failure: function(response, opts) {
																		win.setLoading(false);
																		Ext.Msg.show({
																			title: title,
																			msg: 'server-side failure with status code ' + response.status,
																			buttons: Ext.Msg.OK,
																			icon: Ext.Msg.ERROR,
																			fn: function(buttonId,text,opt){
																			}
																		});
																	}
																});

															}catch(e){
																console.error(e);
															}
														}
													}
												},{
													text: 'Cancel',
													itemId: 'cancel',
													listeners: {
														click: function(button){
															try{
	//															synonym_store.rejectChanges();
																button.up('window').close();
															}catch(e){
															}
														}
													}
												}]
											}]
										}).show();

									}
								});

							}
						}
					},'-',{
						xtype: 'button',
						iconCls: 'window_send',
						text: AgLang.FMABrowser,
						listeners: {
							click: function(){
								self.openFMABrowser(getLastRecord().get('id') || '');
							}
						}
					}]
				}
/*
				,{
					hidden: true,
					xtype: 'toolbar',
					dock: 'bottom',
					defaultType: 'button',
//					layout: {
//						overflowHandler: 'Menu'
//					},
					listeners: {
						afterrender: function(toolbar){
//							console.log('toolbar.afterrender');
							var conceptArtMapPartSelectStore = Ext.data.StoreManager.lookup('conceptArtMapPartSelectStore');
//							console.log(toolbar.items);
							while(toolbar.items.getCount()>2){
								toolbar.remove(toolbar.items.getAt(toolbar.items.getCount()-1));
							}
							var buttons = {};
							var button_items = {};
							conceptArtMapPartSelectStore.each(function(record){
								var cmp_title = record.get('cmp_title');
								var cmp_abbr = record.get('cmp_abbr');
//								var text = '<b>'+cmp_title.substr(0,1).toUpperCase()+'</b>'+cmp_title.substr(1).toLowerCase();
								var text = cmp_abbr;
								var tooltip = cmp_title;//.substr(0,1).toUpperCase()+cmp_title.substr(1).toLowerCase();

								if(cmp_abbr.match(/^([A-Z])(1{0,1})$/)){
									var cmp_key = RegExp.$1;
									var cmp_key_number = RegExp.$2 || 0;
//									console.log(cmp_key,cmp_key_number);
//									var button_text = cmp_title.replace(/[0-9]+$/g,'');
//									button_text = '<b>'+button_text.substr(0,1).toUpperCase()+'</b>'+button_text.substr(1).toLowerCase();
									var button_text = Ext.String.format('<b>{0}</b>',text);
									var button_tooltip = tooltip;

									var listeners = null;
									if(!cmp_key_number){
										listeners = {
											afterrender: function(field){
												var attributeStore = Ext.data.StoreManager.lookup(attributeStoreId);
												if(attributeStore){
													attributeStore.on({
														datachanged: function(store){
															var conceptArtMapPartStore = Ext.data.StoreManager.lookup('conceptArtMapPartStore');
															var lastRecord = getLastRecord();
															var cmp_record = conceptArtMapPartStore.findRecord('cmp_abbr', field.itemId, 0, false, false, true );
															if(cmp_record && lastRecord.get('cmp_id')===cmp_record.get('cmp_id')){
																if(!field.pressed) field.toggle(true,true);
															}else{
																if(field.pressed) field.toggle(false,true);
															}
														}
													});
												}
											},
											click: function(field,e){
												var conceptArtMapPartStore = Ext.data.StoreManager.lookup('conceptArtMapPartStore');
												var lastRecord = getLastRecord();
												if(field.pressed){
													var cmp_record = conceptArtMapPartStore.findRecord('cmp_abbr', field.itemId, 0, false, false, true );
													if(cmp_record){
														lastRecord.set('cmp_id',cmp_record.get('cmp_id'));
													}else{
														lastRecord.set('cmp_id',0);
													}
												}else{
													var cmp_record = conceptArtMapPartStore.findRecord('cmp_title', 'itself', 0, false, false, true );
													if(cmp_record){
														lastRecord.set('cmp_id',cmp_record.get('cmp_id'));
													}else{
														lastRecord.set('cmp_id',0);
													}
													field.up('panel').focus();
												}
												setLastRecord(lastRecord);
												loadAttributePage();
											}
										};
									}

									buttons[cmp_key] = toolbar.add({
										itemId: cmp_key,
										text: button_text,
										tooltip: button_tooltip,
										enableToggle: true,
										toggleGroup: 'sub',
										listeners: listeners
									});
									toolbar.add('-');
								}
								if(cmp_abbr.match(/^([A-Z])[0-9]+$/)){
									var cmp_key = RegExp.$1;
									button_items[cmp_key] = button_items[cmp_key] || [];
									button_items[cmp_key].push(record)
								}
							});
							Ext.Object.each(button_items, function(cmp_key,records){
								if(Ext.isEmpty(buttons[cmp_key])) return true;
								if(Ext.isArray(records) && records.length){
//									console.log(records);
									var idx = toolbar.items.findIndex( 'itemId', cmp_key, 0, false, false );
//									console.log(idx);
									if(idx>=0){
										var item_datas = [];
										Ext.each(records, function(record){
											item_datas.push(record.getData());
										});
										var component_obj = {
											itemId: cmp_key+'_combobox',
											disabled: true,
											width: 50,
											xtype: 'combobox',
											store: Ext.create('Ext.data.Store', {
												model: 'CONCEPT_ART_MAP_PART',
												data : item_datas
											}),
											queryMode: 'local',
											editable: false,
											listConfig: {
												minWidth: 50
											},
											displayField: 'cmp_title',
											valueField: 'cmp_id',
											value: records[0].get('cmp_id'),
											listeners : {
												afterrender: function(combobox){

													var field = combobox.prev('button#'+cmp_key);
													field.on('toggle', function(field, pressed, eOpts){
														combobox.setDisabled(!pressed);
														if(pressed){
															combobox.fireEvent('change', combobox, combobox.getValue());
															field.up('panel').focus();
														}
													});
													field.on('click', function(field, eOpts){
														if(field.pressed) return;
														var lastRecord = getLastRecord();
														lastRecord.set('cmp_id',0);
														setLastRecord(lastRecord);
														loadAttributePage();
													});

													var attributeStore = Ext.data.StoreManager.lookup(attributeStoreId);
													if(attributeStore){
														attributeStore.on({
															datachanged: function(store){
																var lastRecord = getLastRecord();
																var cmp_record = combobox.findRecordByValue(lastRecord.get('cmp_id'));
																if(cmp_record){
																	if(!field.pressed) field.toggle(true,false);
																}else{
																	if(field.pressed) field.toggle(false,false);
																}
															}
														});
													}
												},
												change: function( combobox, newValue, oldValue, eOpts ){

													var field = combobox.prev('button#'+cmp_key);
													var lastRecord = getLastRecord();
													lastRecord.set('cmp_id', newValue);
													setLastRecord(lastRecord);
													loadAttributePage();

												}
											}
										};
										if(idx+1<toolbar.items.getCount()){
											toolbar.insert( idx+1, component_obj);
										}else{
											toolbar.add(component_obj);
										}
									}
								}
							});
						}
					},
					items: [{
						xtype: 'tbtext',
						text : AgLang.make_sub
					},'-'
					]
				}
*/
				],
				flex:1,
				layout: {
					type: 'vbox',
					align: 'stretch'
				},
				items: [{
					height: 32,
					border: true,
					xtype: 'form',
					bodyPadding: 4,
					layout: 'anchor',
					items: getFMAAllCombobox()
				},{
					flex:1,
					autoScroll: true,
					itemId: 'subject-panel',
					id: idPrefix+'subject-panel',
					stateId: idPrefix+'subject-panel',
					xtype: 'panel',
					border: true,
					bodyStyle: 'border-bottom-width:0;',
					tpl: getFMATemplate(),
					listeners: {
						afterrender: getSubjectAfterrender
					}
				}]
			},{
				width: 20,
				border: false,
				bodyStyle: 'border-width:0 1px;',
				layout: {
					type: 'vbox',
					align: 'center',
					pack: 'center'
				},
				items: [{
					xtype: 'label',
					text: '<-',
				}]
			},{
				border: true,
				bodyStyle: 'border-bottom-width:0;',
				flex:1,
				xtype: 'gridpanel',
				itemId: 'attribute-gridpanel',
				id: attributeGridId,
				stateId: attributeGridId,
//				title: 'attribute',
//				emptyText: self.TITLE_UPLOAD_OBJECT + ' drag &amp; drop',
				emptyText: 'drag & drop a obj file',
				store: getAttributeStore(attributeStoreId),
				columnLines: true,
				columns: getAttributeGridColumns(),
				plugins: [self.getBufferedRenderer()],
				selType: 'rowmodel',
				selModel: {
					mode:'MULTI'
				},
				viewConfig: {
					stripeRows:true,
					plugins: {
						ptype: 'gridviewdragdrop',
						ddGroup: 'dd-upload_folder_tree',
						enableDrag: true
					},
					listeners: {
						beforedrop: function(node, data, overModel, dropPosition, dropHandlers) {
							var view = this;
							dropHandlers.cancelDrop();

							var store = view.getStore();
							var datas = []
							Ext.each(data.records,function(record){
								if(store.find('art_id',record.get('art_id'),0,false,false,true)>=0) return true;
								datas.push(record.getData());
								return false;	//conceptに対応するobjは一つなので…
							});
							if(datas.length){

								var sorters = store.sorters.getRange();
								if(sorters.length){
									store.sorters.clear();
									view.headerCt.clearOtherSortStates()
								}

								var selModel = view.getSelectionModel();
								store.removeAll(true);	//conceptに対応するobjは一つなので…
								selModel.select(store.add(datas));

								if(sorters.length){
									store.sorters.addAll(sorters);
									store.sort();
								}

							}
							if(Ext.isChrome) view.up('gridpanel').columns.forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
							loadAttributePage();
						},
						itemkeydown : function(view,record,item,index,e,eOpts){
							if(e.getKey()==e.DELETE){
								e.stopEvent();
								var store = view.getStore();
								var selModel = view.getSelectionModel();
								store.remove(selModel.getSelection());
								if(Ext.isChrome) view.up('gridpanel').columns.forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
							}
						}
					}
				},
				dockedItems: [{
					xtype: 'toolbar',
					dock: 'top',
					items: [{
						xtype: 'tbtext',
						text : '<b>'+AgLang.attribute+'</b>'
					},'-','->','-',{
						disabled: true,
						xtype: 'button',
//						iconCls: 'pallet_delete',
						text: 'clear obj file',
						listeners: {
							afterrender: function(field){
								var gridpanel = field.up('gridpanel');
								gridpanel.on({
									selectionchange: function(selModel, selected, eOpts){
										var disabled = Ext.isEmpty(selected);
										field.setDisabled(disabled);
									}
								});
							},
							click: function(field){
								var gridpanel = field.up('gridpanel');
								var store = gridpanel.getStore();
//								var selModel = gridpanel.getSelectionModel();
//								store.remove(selModel.getSelection());

								var panel = Ext.getCmp(aOpt.id);
								var mirror_checkboxfield = panel.down('checkboxfield#mirror');
								if(mirror_checkboxfield && mirror_checkboxfield.getValue() && !mirror_checkboxfield.isDisabled()){
//									mirror_checkboxfield.fireEvent('change',mirror_checkboxfield,false);
//									mirror_checkboxfield.setDisabled(true);
									mirror_checkboxfield.setValue(false);
//									return;
									Ext.defer(function(){
										store.removeAll();
										loadAttributePage();
									},100);
								}else{
									store.removeAll();
									loadAttributePage();
								}
							}
						}
					},{
						hidden: true,
						xtype: 'tbseparator'
					},{
						hidden: true,
						disabled: true,
						xtype: 'checkboxfield',
						boxLabel: 'Mirroring',
						itemId: 'mirror_old',
						listeners: {
							afterrender: function(field){
								var gridpanel = field.up('gridpanel');
								var store = gridpanel.getStore();
								store.on({
									datachanged: function(store, eOpts){
										var cdi_name = getLastRecord().get('cdi_name');
										var disabled = Ext.isEmpty(cdi_name);
										if(!disabled){
											disabled = (store.getCount()===0);
										}
										field.setDisabled(disabled);
									}
								});
							}
						}
					},{
						hidden: true,
						xtype: 'tbseparator'
					},{
						hidden: true,
						disabled: true,
						xtype: 'button',
						iconCls: 'replace',
						text: AgLang.replace,
						listeners: {
							afterrender: function(field){
								var gridpanel = field.up('gridpanel');
								var store = gridpanel.getStore();
								store.on({
									datachanged: function(store, eOpts){
										var cdi_name = getLastRecord().get('cdi_name');
										var disabled = Ext.isEmpty(cdi_name);
										if(!disabled){
											disabled = (store.getCount()===0);
										}
										field.setDisabled(disabled);
									}
								});
							},
							click: function(field){
								var lastRecord = getLastRecord();
								var cdi_name = lastRecord.get('cdi_name');
								var cdi_name_e = lastRecord.get('cdi_name_e');
								if(Ext.isEmpty(cdi_name)){
									return;
								}
								var gridpanel = field.up('gridpanel');
								var store = gridpanel.getStore();
								var update_records = [];
								store.each(function(record){
									record.beginEdit();
									record.set('cdi_name',cdi_name);
									record.set('cdi_name_e',cdi_name_e);
									record.set('cmp_id',0);
									record.set('cm_use',true);
									record.set('never_current',false);
									record.endEdit(false,['cdi_name','cdi_name_e','cmp_id','cm_use','never_current']);
									update_records.push(record);
								});

								if(Ext.isEmpty(update_records)){
									return;
								}
								var mirror_field = field.prev('checkboxfield#mirror');
								field.setDisabled(true);
								mirror_field.setDisabled(true);
								field.setIconCls('loading-btn');

								var mirror_value = mirror_field.getValue();

								var gridpanel = field.up('gridpanel');
								if(gridpanel) gridpanel.setDisabled(true);

								var proxy = store.getProxy();
								proxy.extraParams = proxy.extraParams || {};
								proxy.extraParams.cmd_mode = 'replace';
//								console.log(update_records);
//								console.log(store.getUpdatedRecords());
								var update_datas = [];
								update_records.forEach(function(record){
									update_datas.push({
										art_id:        record.get('art_id'),
										cdi_name:      record.get('cdi_name'),
										cmp_id:        record.get('cmp_id'),
										cm_use:        record.get('cm_use'),
										never_current: record.get('never_current'),
										mirror:        mirror_value
									});
								});

								var params = Ext.Object.merge({},proxy.extraParams || {},{datas: Ext.encode(update_datas)});
								Ext.Ajax.request({
									url: proxy.api.update,
									method: proxy.actionMethods.update,
									timeout: proxy.timeout,
									params: params,
									callback: function(options,success,response){
										field.setIconCls('replace');
										field.setDisabled(false);
										mirror_field.setDisabled(false);
										if(gridpanel) gridpanel.setDisabled(false);

										var json;
										try{json = Ext.decode(response.responseText)}catch(e){};
										if(success==false || Ext.isEmpty(json) || Ext.isEmpty(json.success) || json.success==false){
											Ext.each(update_records,function(r,i,a){
												r.reject();
											});
											if(Ext.isEmpty(json) || Ext.isEmpty(json.msg)) return;
											Ext.Msg.show({
												title: field.text || AgLang.replace,
												msg: json.msg,
												buttons: Ext.Msg.OK,
												icon: Ext.Msg.ERROR
											});
										}else{
											if(Ext.isArray(json.datas)){
												var add_datas = [];
												json.datas.forEach(function(data){
													var f_record = store.findRecord('art_id', data.art_id, 0, false, false, true);
													if(Ext.isEmpty(f_record)) add_datas.push(data);
												});
												if(add_datas.length) store.add(add_datas);
											}

											/* existingAttributeStore から対応されていたOBJを取得 */
											var existingAttributeStore = Ext.data.StoreManager.lookup(existingAttributeStoreId);
											var old_map_records = [];
											existingAttributeStore.each(function(record){
												if(record.get('cdi_name')!==cdi_name) return true;
												var f_record = store.findRecord('art_id', record.get('art_id'), 0, false, false, true);
												if(Ext.isEmpty(f_record)){
													old_map_records.push(record.getData());
												}
											});
											if(old_map_records.length){
												store.add(old_map_records).forEach(function(record){
													record.beginEdit();
													record.set('cdi_name',null);
													record.set('cdi_name_e',null);
													record.set('cmp_id',0);
													record.commit(false,['cdi_name','cdi_name_e','cmp_id']);
												});
											}
											if(mirror_value){
												if(self.reloadUploadObjectStore) self.reloadUploadObjectStore();
											}else{
												if(self.syncUploadObjectStore) self.syncUploadObjectStore(store.getRange());
											}
											if(self.syncPalletPartsStore) self.syncPalletPartsStore(store.getRange());
											if(self.syncPickSearchStore) self.syncPickSearchStore(store.getRange());
											Ext.data.StoreManager.lookup(existingAttributeStoreId).loadPage(1);
											Ext.data.StoreManager.lookup(parentAttributeStoreId).loadPage(1);
											store.removeAll();
										}
									}
								});
/**/
							}
						}
					},{
						hidden: true,
						xtype: 'tbseparator'
					},{
						hidden: true,
						disabled: true,
						xtype: 'button',
						iconCls: 'append',
						text: AgLang.append,
						listeners: {
							afterrender: function(field){
								var gridpanel = field.up('gridpanel');
								var store = gridpanel.getStore();
								store.on({
									datachanged: function(store, eOpts){
										var cdi_name = getLastRecord().get('cdi_name');
										var disabled = Ext.isEmpty(cdi_name);
										if(!disabled){
											disabled = true;
											store.each(function(record){
												if(record.get('cdi_name')===cdi_name) return true;
												disabled = false;
												return false;
											});
										}
										field.setDisabled(disabled);
									}
								});
							},
							click: function(field){
								var lastRecord = getLastRecord();
								var cdi_name = lastRecord.get('cdi_name');
								var cdi_name_e = lastRecord.get('cdi_name_e');
								if(Ext.isEmpty(cdi_name)){
									field.setDisabled(true);
									return;
								}
								var gridpanel = field.up('gridpanel');
								var store = gridpanel.getStore();
								var update_records = [];
								store.each(function(record){
									record.beginEdit();
									record.set('cdi_name',cdi_name);
									record.set('cdi_name_e',cdi_name_e);
									record.set('cmp_id',0);
									record.set('cm_use',true);
									record.set('never_current',false);
									record.endEdit(false,['cdi_name','cdi_name_e','cmp_id','cm_use','never_current']);
									console.log('click', record.getChanges(), Ext.isEmpty(record.getChanges()['cdi_name']));
									if(!Ext.isEmpty(record.getChanges()['cdi_name'])) update_records.push(record);
								});

								field.setDisabled(true);
								if(Ext.isEmpty(update_records)){
									return;
								}
								field.setIconCls('loading-btn');
								var gridpanel = field.up('gridpanel');
								if(gridpanel) gridpanel.setDisabled(true);

								var proxy = store.getProxy();
								proxy.extraParams = proxy.extraParams || {};
								proxy.extraParams.cmd_mode = 'append';
								store.sync({
									callback: function(batch,options){
										field.setIconCls('append');
										if(gridpanel) gridpanel.setDisabled(false);
									},
									success: function(batch,options){
										if(self.syncUploadObjectStore) self.syncUploadObjectStore(store.getRange());
										if(self.syncPalletPartsStore) self.syncPalletPartsStore(store.getRange());
										if(self.syncPickSearchStore) self.syncPickSearchStore(store.getRange());
										Ext.data.StoreManager.lookup(existingAttributeStoreId).loadPage(1);
										Ext.data.StoreManager.lookup(parentAttributeStoreId).loadPage(1);
										store.removeAll();
									},
									failure: function(batch,options){
										var msg = AgLang.error_submit;
										var proxy = this;
										var reader = proxy.getReader();
										if(reader && reader.rawData && reader.rawData.msg){
											msg += ' ['+reader.rawData.msg+']';
										}
										Ext.Msg.show({
											title: field.text || AgLang.append,
											iconCls: 'append',
											msg: msg,
											buttons: Ext.Msg.OK,
											icon: Ext.Msg.ERROR,
											fn: function(buttonId,text,opt){
											}
										});
										field.setDisabled(false);
										Ext.each(update_records,function(r,i,a){
											r.reject();
										});
									}
								});
							}
						}
					}]
				}],
				listeners: {
					afterrender: function(gridpanel){
						gridpanel.getStore().removeAll();
						if(Ext.isChrome) gridpanel.columns.forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
					},
					columnhide: function(ct, column, eOpts){
						if(Ext.isChrome) ct.getGridColumns().forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
					},
					columnshow: function(ct, column, eOpts){
						if(Ext.isChrome) ct.getGridColumns().forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
					}
				}
			}],
			dockedItems: [{
				xtype: 'toolbar',
				dock: 'bottom',
				defaultType: 'button',
				listeners: {

						afterrender: function(toolbar){
//							console.log('toolbar.afterrender');
							var conceptArtMapPartSelectStore = Ext.data.StoreManager.lookup('conceptArtMapPartSelectStore');
//							console.log(toolbar.items);
							while(toolbar.items.getCount()>2){
								toolbar.remove(toolbar.items.getAt(toolbar.items.getCount()-1));
							}
							var buttons = {};
							var button_items = {};
							conceptArtMapPartSelectStore.each(function(record){
								var cmp_title = record.get('cmp_title');
								var cmp_abbr = record.get('cmp_abbr');
//								var text = '<b>'+cmp_title.substr(0,1).toUpperCase()+'</b>'+cmp_title.substr(1).toLowerCase();
								var text = cmp_abbr;
								var tooltip = cmp_title;//.substr(0,1).toUpperCase()+cmp_title.substr(1).toLowerCase();

								if(cmp_abbr.match(/^([A-Z])(1{0,1})$/)){
									var cmp_key = RegExp.$1;
									var cmp_key_number = RegExp.$2 || 0;
//									console.log(cmp_key,cmp_key_number);
//									var button_text = cmp_title.replace(/[0-9]+$/g,'');
//									button_text = '<b>'+button_text.substr(0,1).toUpperCase()+'</b>'+button_text.substr(1).toLowerCase();
									var button_text = Ext.String.format('<b>{0}</b>',text);
									var button_tooltip = tooltip;

									var listeners = null;
									if(!cmp_key_number){
										listeners = {
											afterrender: function(field){
												var attributeStore = Ext.data.StoreManager.lookup(attributeStoreId);
												if(attributeStore){
													attributeStore.on({
														datachanged: function(store){
															var conceptArtMapPartStore = Ext.data.StoreManager.lookup('conceptArtMapPartStore');
															var lastRecord = getLastRecord();
															var cmp_record = conceptArtMapPartStore.findRecord('cmp_abbr', field.itemId, 0, false, false, true );
															if(cmp_record && lastRecord.get('cmp_id')===cmp_record.get('cmp_id')){
																if(!field.pressed) field.toggle(true,true);
															}else{
																if(field.pressed) field.toggle(false,true);
															}
														}
													});
												}
											},
											click: function(field,e){
												var conceptArtMapPartStore = Ext.data.StoreManager.lookup('conceptArtMapPartStore');
												var lastRecord = getLastRecord();
												if(field.pressed){
													var cmp_record = conceptArtMapPartStore.findRecord('cmp_abbr', field.itemId, 0, false, false, true );
													if(cmp_record){
														lastRecord.set('cmp_id',cmp_record.get('cmp_id'));
													}else{
														lastRecord.set('cmp_id',0);
													}
												}else{
													var cmp_record = conceptArtMapPartStore.findRecord('cmp_title', 'itself', 0, false, false, true );
													if(cmp_record){
														lastRecord.set('cmp_id',cmp_record.get('cmp_id'));
													}else{
														lastRecord.set('cmp_id',0);
													}
													field.up('panel').focus();
												}
												setLastRecord(lastRecord);
												loadAttributePage();
											}
										};
									}

									buttons[cmp_key] = toolbar.add({
										itemId: cmp_key,
										text: button_text,
										tooltip: button_tooltip,
										enableToggle: true,
										toggleGroup: 'sub',
										listeners: listeners
									});
									toolbar.add('-');
								}
								if(cmp_abbr.match(/^([A-Z])[0-9]+$/)){
									var cmp_key = RegExp.$1;
									button_items[cmp_key] = button_items[cmp_key] || [];
									button_items[cmp_key].push(record)
								}
							});
							Ext.Object.each(button_items, function(cmp_key,records){
								if(Ext.isEmpty(buttons[cmp_key])) return true;
								if(Ext.isArray(records) && records.length){
//									console.log(records);
									var idx = toolbar.items.findIndex( 'itemId', cmp_key, 0, false, false );
//									console.log(idx);
									if(idx>=0){
										var item_datas = [];
										Ext.each(records, function(record){
											item_datas.push(record.getData());
										});
										var component_obj = {
											itemId: cmp_key+'_combobox',
											disabled: true,
											width: 50,
											xtype: 'combobox',
											store: Ext.create('Ext.data.Store', {
												model: 'CONCEPT_ART_MAP_PART',
												data : item_datas
											}),
											queryMode: 'local',
											editable: false,
											listConfig: {
												minWidth: 50
											},
											displayField: 'cmp_title',
											valueField: 'cmp_id',
											value: records[0].get('cmp_id'),
											listeners : {
												afterrender: function(combobox){

													var field = combobox.prev('button#'+cmp_key);
													field.on('toggle', function(field, pressed, eOpts){
														combobox.setDisabled(!pressed);
														if(pressed){
															combobox.fireEvent('change', combobox, combobox.getValue());
															field.up('panel').focus();
														}
													});
													field.on('click', function(field, eOpts){
														if(field.pressed) return;
														var lastRecord = getLastRecord();
														lastRecord.set('cmp_id',0);
														setLastRecord(lastRecord);
														loadAttributePage();
													});

													var attributeStore = Ext.data.StoreManager.lookup(attributeStoreId);
													if(attributeStore){
														attributeStore.on({
															datachanged: function(store){
																var lastRecord = getLastRecord();
																var cmp_record = combobox.findRecordByValue(lastRecord.get('cmp_id'));
																if(cmp_record){
																	if(!field.pressed) field.toggle(true,false);
																}else{
																	if(field.pressed) field.toggle(false,false);
																}
															}
														});
													}
												},
												change: function( combobox, newValue, oldValue, eOpts ){

													var field = combobox.prev('button#'+cmp_key);
													var lastRecord = getLastRecord();
													lastRecord.set('cmp_id', newValue);
													setLastRecord(lastRecord);
													loadAttributePage();

												}
											}
										};
										if(idx+1<toolbar.items.getCount()){
											toolbar.insert( idx+1, component_obj);
										}else{
											toolbar.add(component_obj);
										}
									}
								}
							});
						}




















				},
				items: [{
					xtype: 'tbtext',
					text : AgLang.make_sub
				},'-']
			}]
		},{
			flex: 1,
			xtype: 'gridpanel',
			itemId: 'existing-attribute-gridpanel',
			id: idPrefix+'existing-attribute-gridpanel',
			stateId: idPrefix+'existing-attribute-gridpanel',
			store: getStore(existingAttributeStoreId),
			columnLines: true,
			columns: getExistingGridColumns(),
			viewConfig: {
				stripeRows:true,
				plugins: {
					ptype: 'gridviewdragdrop',
					ddGroup: 'dd-upload_folder_tree',
					enableDrop: false
				},
			},
			plugins: [self.getBufferedRenderer()],
			selType: 'rowmodel',
			selModel: {
				mode:'MULTI'
			},
			dockedItems: [{
				xtype: 'toolbar',
				dock: 'top',
				items: [{
					xtype: 'tbtext',
					text: '<b>'+AgLang.existing_attribute+'</b>',
				},{
					hidden: true,
					xtype: 'tbseparator'
				},getHideParentTermCheckbox(),{
					hidden: false,
					xtype: 'tbseparator'
				},getNeverCurrentButton(),{
					hidden: false,
					xtype: 'tbseparator'
				},getRemoveMappingButton(),{
					hidden: false,
					xtype: 'tbseparator'
				},'->',{
					hidden: false,
					xtype: 'tbseparator'
				},getFMABrowserButton()]
			},{
				hidden: true,
				itemId: 'existing-attribute-gridpanel-agpagingtoolbar',
				id: idPrefix+'existing-attribute-gridpanel-agpagingtoolbar',
				stateId: idPrefix+'existing-attribute-gridpanel-agpagingtoolbar',
				xtype: 'agpagingtoolbar',
				store: existingAttributeStoreId,
				dock: 'bottom'
			}],
			listeners: {
				afterrender: function(gridpanel){
					if(Ext.isChrome){
						gridpanel.columns.forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
						var store = gridpanel.getStore();
						store.on({
							load: {
								fn: function(){
									gridpanel.columns.forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
								},
								buffer: 0
							}
						});
					}
				},
				columnhide: function(ct, column, eOpts){
					if(Ext.isChrome) ct.getGridColumns().forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
				},
				columnshow: function(ct, column, eOpts){
					if(Ext.isChrome) ct.getGridColumns().forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
				}
			}
		},{
			hidden: false,
			region: 'south',
			split: true,
			flex: 1,
			xtype: 'gridpanel',
			itemId: 'parent-attribute-gridpanel',
			id: idPrefix+'parent-attribute-gridpanel',
			stateId: idPrefix+'parent-attribute-gridpanel',
			store: getStore(parentAttributeStoreId),
			columnLines: true,
			columns: getParentGridColumns(),
			viewConfig: {
				stripeRows:true,
				plugins: {
					ptype: 'gridviewdragdrop',
					ddGroup: 'dd-upload_folder_tree',
					enableDrop: false
				},
			},
			plugins: [self.getBufferedRenderer()],
			selType: 'rowmodel',
			selModel: {
				mode:'MULTI'
			},
			dockedItems: [{
				hidden: false,
				xtype: 'toolbar',
				dock: 'top',
				items: [{
					xtype: 'tbtext',
					text: '<b>'+AgLang.parent_attribute+'</b>',
				},{
					hidden: false,
					xtype: 'tbseparator'
				},getNeverCurrentButton(),{
					hidden: false,
					xtype: 'tbseparator'
				},getRemoveMappingButton(),{
					hidden: false,
					xtype: 'tbseparator'
				},{
					xtype: 'radiofield',
					boxLabel: AgLang.parent_attribute_parent,
					name: idPrefix+'parent-attribute-display-type',
					id: idPrefix+'parent-attribute-display-type-parent',
					padding: '0 5 0 5',
					checked: true,
					handler: function(field,checked){
						if(!checked) loadAttributePage();
					}
				},{
					xtype: 'radiofield',
					boxLabel: AgLang.parent_attribute_ancestor,
					name: idPrefix+'parent-attribute-display-type',
					id: idPrefix+'parent-attribute-display-type-ancestor',
					padding: '0 5 0 0',
					handler: function(field,checked){
						if(!checked) loadAttributePage();
					}
				},{
					hidden: false,
					xtype: 'tbseparator'
				},'->',{
					hidden: false,
					xtype: 'tbseparator'
				},getFMABrowserButton()]
			},{
				hidden: true,
				itemId: 'parent-attribute-gridpanel-agpagingtoolbar',
				id: idPrefix+'parent-attribute-gridpanel-agpagingtoolbar',
				stateId: idPrefix+'parent-attribute-gridpanel-agpagingtoolbar',
				xtype: 'agpagingtoolbar',
				store: parentAttributeStoreId,
				dock: 'bottom'
			}],
			listeners: {
				afterrender: function(gridpanel){
					if(Ext.isChrome){
						gridpanel.columns.forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
						var store = gridpanel.getStore();
						store.on({
							load: {
								fn: function(){
									gridpanel.columns.forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
								},
								buffer: 0
							}
						});
					}
				},
				columnhide: function(ct, column, eOpts){
					if(Ext.isChrome) ct.getGridColumns().forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
				},
				columnshow: function(ct, column, eOpts){
					if(Ext.isChrome) ct.getGridColumns().forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
				}
			}
		},{
			height: 120+26,
			layout: {
				type: 'hbox',
				align: 'stretch'
			},
			border: false,
			dockedItems: [{
				xtype: 'toolbar',
				dock: 'top',
				items: [{
					xtype: 'checkboxfield',
					boxLabel : '<b>Mirror</b>',
					itemId: 'mirror',
					disabled: true,
					listeners: {
						afterrender: function(field){
							var store = Ext.data.StoreManager.lookup(attributeStoreId);
							store.on({
								datachanged: function(store, eOpts){
									var cdi_name = getLastRecord().get('cdi_name');
									var disabled = Ext.isEmpty(cdi_name);
									if(!disabled){
										disabled = store.getCount()>0 ? false : true;
									}
									field.setDisabled(disabled);
									if(disabled){
										if(field.getValue()) field.fireEvent('change', field, false);
									}
								}
							});
						},
						change: function(field,value){
							var button = field.next('button#set_to_default');
							button.setDisabled(!value);
							if(value) button.fireEvent('click', button);

							var panel = field.up('panel');
							panel.items.each(function(item){
								item.setDisabled(!value);
							});

							var gridpanel = panel.next('gridpanel');
							gridpanel.setDisabled(!value);

							gridpanel = gridpanel.next('gridpanel');
							gridpanel.setDisabled(!value);

							if(value) return;

							var mirrorAttributeStore = Ext.data.StoreManager.lookup(mirrorAttributeStoreId);
							mirrorAttributeStore.removeAll();

							setLastMirrorRecord();
							field.up('panel').down('panel').down('panel#subject-panel').update(getLastMirrorRecord().getData());
							loadMirrorAttributePage.delay(250);

							var attributeStore = Ext.data.StoreManager.lookup(attributeStoreId);
							attributeStore.fireEvent('datachanged', attributeStore);
						}
					}
				},'-',{
					disabled: true,
					xtype: 'button',
					text: 'set to default',
					itemId: 'set_to_default',
					listeners: {
						click: function(b){
							var value = getLastRecord().get('cdi_name_e');
							if(Ext.isEmpty(value)) return;

							var art_id;
							var art_mirroring;
							var art_record;
							var attributeStore = Ext.data.StoreManager.lookup(attributeStoreId);
							if(attributeStore && attributeStore.getCount()){
								art_record = attributeStore.getAt(0);
								art_id = art_record.get('art_id');
								if(art_id){
									if(art_id.match(/^(.+)M$/)){
										art_id = RegExp.$1;
										art_mirroring = false;
									}else{
										art_id += 'M';
										art_mirroring = true;
									}
								}
							}
							if(Ext.isEmpty(art_id)) return;
							if(art_id){
								var params = self.getExtraParams() || {};
								delete params.current_datas;
								delete params._ExtVerMajor;
								delete params._ExtVerMinor;
								delete params._ExtVerPatch;
								delete params._ExtVerBuild;
								delete params._ExtVerRelease;
								params.art_id = art_id;
								Ext.Ajax.request({
									url: 'get-upload-obj-info.cgi',
									method: 'POST',
									params: params,
									success: function(response, eOpts){
										var json;
										try{json = Ext.decode(response.responseText)}catch(e){};

										var mirrorAttributeStore = Ext.data.StoreManager.lookup(mirrorAttributeStoreId);
										var mirrorAttributeModel = Ext.getClassName(mirrorAttributeStore.model);
										var mirrorAttributeRecord;

										if(Ext.isEmpty(json) || Ext.isEmpty(json.datas)){
											var art_data = art_record.getData();
											art_data.art_id = art_id
											art_data.art_mirroring = art_mirroring
											art_data.art_xmin *= -1
											art_data.art_xmax *= -1
											delete art_data.art_tmb_path;
											delete art_data.cdi_id;
											delete art_data.cdi_name;
											delete art_data.cdi_name_e;
											mirrorAttributeRecord = Ext.create(mirrorAttributeModel, art_data);
										}else{
											mirrorAttributeRecord = Ext.create(mirrorAttributeModel, json.datas[0]);
										}
//										console.log(mirrorAttributeRecord);
										var mirrorAttributeGridView = Ext.getCmp(mirrorAttributeGridId).getView();
										mirrorAttributeStore.removeAll(true);
										mirrorAttributeStore

										var sorters = mirrorAttributeStore.sorters.getRange();
										if(sorters.length){
											mirrorAttributeStore.sorters.clear();
											mirrorAttributeGridView.headerCt.clearOtherSortStates()
										}

										var selModel = mirrorAttributeGridView.getSelectionModel();
										mirrorAttributeStore.removeAll(true);	//conceptに対応するobjは一つなので…
										selModel.select(mirrorAttributeStore.add([mirrorAttributeRecord]));

										if(sorters.length){
											mirrorAttributeStore.sorters.addAll(sorters);
											mirrorAttributeStore.sort();
										}

										if(Ext.isChrome) mirrorAttributeGridView.up('gridpanel').columns.forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
										loadMirrorAttributePage.delay(250);

										var attributeStore = Ext.data.StoreManager.lookup(attributeStoreId);
										attributeStore.fireEvent('datachanged', attributeStore);

									},
									failure: function(response,eOpts){
									}
								});
							}

							var cdi_name_e = '';
							var cmp_id = getLastRecord().get('cmp_id');
							if(cmp_id){

								var mirror_cmp_record;
								var conceptArtMapPartStore = Ext.data.StoreManager.lookup('conceptArtMapPartStore');
								var cmp_record_L = conceptArtMapPartStore.findRecord('cmp_abbr', 'L', 0, false, false, true );
								var cmp_record_R = conceptArtMapPartStore.findRecord('cmp_abbr', 'R', 0, false, false, true );
//								var cmp_record_P = conceptArtMapPartStore.findRecord('cmp_abbr', 'P', 0, false, false, true );

								if(cmp_record_L && cmp_record_L.get('cmp_id')===cmp_id){
									mirror_cmp_record = cmp_record_R;
								}
								if(Ext.isEmpty(mirror_cmp_record)){
									if(cmp_record_R && cmp_record_R.get('cmp_id')===cmp_id){
										mirror_cmp_record = cmp_record_L;
									}
								}
								if(Ext.isEmpty(mirror_cmp_record)){
//									if(cmp_record_P && cmp_record_P.get('cmp_id')===cmp_id){
									if(cmp_id){
										if(value.match(/\bleft\b/i)){
											cdi_name_e = value.replace(/\bleft\b/i,'right');
										}else if(value.match(/\bright\b/i)){
											cdi_name_e = value.replace(/\bright\b/i,'left');
										}
										if(cdi_name_e){
//											mirror_cmp_record = cmp_record_P;
											mirror_cmp_record = conceptArtMapPartStore.findRecord( 'cmp_id', cmp_id, 0, false, false, true ) ;
										}
									}
								}
								if(Ext.isEmpty(mirror_cmp_record)){
									setLastMirrorRecord();
								}else if(Ext.isEmpty(cdi_name_e)){
									var lastMirrorRecord = Ext.create('CONCEPT_TERM',{
										id: getLastRecord().get('cdi_name'),
										name: getLastRecord().get('cdi_name_e'),
									});
									lastMirrorRecord.set('cmp_id',mirror_cmp_record.get('cmp_id'));
									setLastMirrorRecord(lastMirrorRecord);
								}
								if(Ext.isEmpty(cdi_name_e)){
									b.up('panel').down('panel').down('panel#subject-panel').update(getLastMirrorRecord().getData());
									loadMirrorAttributePage.delay(250);

									return;
								}

							}

							if(Ext.isEmpty(cdi_name_e)){
								if(value.match(/left/i)){
									cdi_name_e = value.replace(/left/i,'right');
								}else if(value.match(/right/i)){
									cdi_name_e = value.replace(/right/i,'left');
								}
							}
							if(Ext.isEmpty(cdi_name_e)){
								setLastMirrorRecord();
								b.up('panel').down('panel').down('panel#subject-panel').update(getLastMirrorRecord().getData());
								loadMirrorAttributePage.delay(250);
								return
							}

							b.setDisabled(true);

							var fmaSearchStore = Ext.data.StoreManager.lookup('fmaSearchStore');
							fmaSearchStore.clearFilter(true);
							fmaSearchStore.load({
								params: {
									cdi_name_e: cdi_name_e
								},
								callback: function(records,operation,success){
									b.setDisabled(false);
									if(!success || Ext.isEmpty(records)){
										setLastMirrorRecord();
									}else{
										var record = records[0];
//										console.log(record);
										var lastMirrorRecord = Ext.create('CONCEPT_TERM',{
											id:record.get('cdi_name'),
											name:record.get('cdi_name_e'),
										});
										if(mirror_cmp_record) lastMirrorRecord.set('cmp_id',mirror_cmp_record.get('cmp_id'));
										setLastMirrorRecord(lastMirrorRecord);
									}
									b.up('panel').down('panel').down('panel#subject-panel').update(getLastMirrorRecord().getData());
									loadMirrorAttributePage.delay(250);
								}
							});

						}
					}
				},'-']
			}],
			defaults: {
				disabled: true
			},
			items: [{
				dockedItems: [{
					xtype: 'toolbar',
					dock: 'top',
					items: [{
						xtype: 'tbtext',
						text : '<b>Mirror '+AgLang.subject+'</b>'
					},'->','-',{
						xtype: 'button',
						iconCls: 'window_send',
						text: AgLang.FMABrowser,
						listeners: {
							click: function(){
								self.openFMABrowser(getLastMirrorRecord().get('id') || '');
							}
						}
					}]
				}],
				flex:1,
				layout: {
					type: 'vbox',
					align: 'stretch'
				},
				items: [{
					height: 32,
					border: true,
					xtype: 'form',
					bodyPadding: 4,
					layout: 'anchor',
					items: getMirrorFMAAllCombobox()
				},{
					flex:1,
					autoScroll: true,
					itemId: 'subject-panel',
					id: idMirrorPrefix+'subject-panel',
					stateId: idMirrorPrefix+'subject-panel',
					xtype: 'panel',
					border: true,
					bodyStyle: 'border-bottom-width:0;',
					tpl: getFMATemplate(),
					listeners: {
						afterrender: getMirrorSubjectAfterrender
					}
				}]
			},{
				width: 20,
				border: false,
				bodyStyle: 'border-width:0 1px;',
				layout: {
					type: 'vbox',
					align: 'center',
					pack: 'center'
				},
				items: [{
					xtype: 'label',
					text: '<-',
				}]
			},{
				border: true,
				bodyStyle: 'border-bottom-width:0;',
				flex:1,
				xtype: 'gridpanel',
				itemId: 'attribute-gridpanel',
				id: mirrorAttributeGridId,
				stateId: mirrorAttributeGridId,
//				title: 'attribute',
//				emptyText: self.TITLE_UPLOAD_OBJECT + ' drag &amp; drop',
				emptyText: 'drag & drop a obj file',
				store: getAttributeStore(mirrorAttributeStoreId),
				columnLines: true,
				columns: getAttributeGridColumns(),
				plugins: [self.getBufferedRenderer()],
				selType: 'rowmodel',
				selModel: {
					mode:'MULTI'
				},
				viewConfig: {
					stripeRows:true,
					plugins: {
						ptype: 'gridviewdragdrop',
						ddGroup: 'dd-upload_folder_tree',
						enableDrag: true
					},
					listeners: {
						beforedrop: function(node, data, overModel, dropPosition, dropHandlers) {
							var view = this;
							dropHandlers.cancelDrop();

							var store = view.getStore();
							var datas = []
							Ext.each(data.records,function(record){
								if(store.find('art_id',record.get('art_id'),0,false,false,true)>=0) return true;
								datas.push(record.getData());
								return false;	//conceptに対応するobjは一つなので…
							});
							if(datas.length){

								var sorters = store.sorters.getRange();
								if(sorters.length){
									store.sorters.clear();
									view.headerCt.clearOtherSortStates()
								}

								var selModel = view.getSelectionModel();
								store.removeAll(true);	//conceptに対応するobjは一つなので…
								selModel.select(store.add(datas));

								if(sorters.length){
									store.sorters.addAll(sorters);
									store.sort();
								}

							}
							if(Ext.isChrome) view.up('gridpanel').columns.forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
							loadMirrorAttributePage.delay(250);

							var attributeStore = Ext.data.StoreManager.lookup(attributeStoreId);
							attributeStore.fireEvent('datachanged', attributeStore);
						},
						itemkeydown : function(view,record,item,index,e,eOpts){
							if(e.getKey()==e.DELETE){
								e.stopEvent();
								var store = view.getStore();
								var selModel = view.getSelectionModel();
								store.remove(selModel.getSelection());
								if(Ext.isChrome) view.up('gridpanel').columns.forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
							}
						}
					}
				},
				dockedItems: [{
					xtype: 'toolbar',
					dock: 'top',
					items: [{
						xtype: 'tbtext',
						text : '<b>Mirror '+AgLang.attribute+'</b>'
					},'-','->','-',{
						disabled: true,
						xtype: 'button',
//						iconCls: 'pallet_delete',
						text: 'clear obj file',
						listeners: {
							afterrender: function(field){
								var gridpanel = field.up('gridpanel');
								gridpanel.on({
									selectionchange: function(selModel, selected, eOpts){
										var disabled = Ext.isEmpty(selected);
										field.setDisabled(disabled);
									}
								});
							},
							click: function(field){
								var gridpanel = field.up('gridpanel');
								var store = gridpanel.getStore();
//								var selModel = gridpanel.getSelectionModel();
//								store.remove(selModel.getSelection());
								store.removeAll();
								loadMirrorAttributePage.delay(250);

								var attributeStore = Ext.data.StoreManager.lookup(attributeStoreId);
								attributeStore.fireEvent('datachanged', attributeStore);
							}
						}
					}]
				}],
				listeners: {
					afterrender: function(gridpanel){
						gridpanel.getStore().removeAll();
						if(Ext.isChrome) gridpanel.columns.forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
					},
					columnhide: function(ct, column, eOpts){
						if(Ext.isChrome) ct.getGridColumns().forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
					},
					columnshow: function(ct, column, eOpts){
						if(Ext.isChrome) ct.getGridColumns().forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
					}
				}
			}]
		},{
			hidden: false,
			disabled: true,
			flex: 1,
			xtype: 'gridpanel',
			itemId: itemIdMirrorPrefix+'existing-attribute-gridpanel',
			id: idMirrorPrefix+'existing-attribute-gridpanel',
			stateId: idMirrorPrefix+'existing-attribute-gridpanel',
//			title: AgLang.existing_attribute,
			store: getStore(mirrorExistingAttributeStoreId),
			columnLines: true,
			columns: getExistingGridColumns(),
			viewConfig: {
				stripeRows:true,
				plugins: {
					ptype: 'gridviewdragdrop',
					ddGroup: 'dd-upload_folder_tree',
					enableDrop: false
				},
			},
//			plugins: [self.getCellEditing(),self.getBufferedRenderer()],
			plugins: [self.getBufferedRenderer()],
			selType: 'rowmodel',
			selModel: {
				mode:'MULTI'
			},
			dockedItems: [{
				xtype: 'toolbar',
				dock: 'top',
//				ui: 'footer',
				items: [{
					xtype: 'tbtext',
					text: '<b>Mirror '+AgLang.existing_attribute+'</b>',
				},{
					hidden: true,
					xtype: 'tbseparator'
				},getHideParentTermCheckbox(),{
					hidden: false,
					xtype: 'tbseparator'
				},getNeverCurrentButton(),{
					hidden: false,
					xtype: 'tbseparator'
				},getRemoveMappingButton(),{
					hidden: false,
					xtype: 'tbseparator'
				},'->',{
					hidden: false,
					xtype: 'tbseparator'
				},getFMABrowserButton()]
			},{
				hidden: true,
				itemId: 'existing-attribute-gridpanel-agpagingtoolbar',
				id: idMirrorPrefix+'existing-attribute-gridpanel-agpagingtoolbar',
				stateId: idMirrorPrefix+'existing-attribute-gridpanel-agpagingtoolbar',
				xtype: 'agpagingtoolbar',
				store: mirrorExistingAttributeStoreId,
				dock: 'bottom'
			}],
			listeners: {
				afterrender: function(gridpanel){
					if(Ext.isChrome){
						gridpanel.columns.forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
						var store = gridpanel.getStore();
						store.on({
							load: {
								fn: function(){
									gridpanel.columns.forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
								},
								buffer: 0
							}
						});
					}
				},
				columnhide: function(ct, column, eOpts){
					if(Ext.isChrome) ct.getGridColumns().forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
				},
				columnshow: function(ct, column, eOpts){
					if(Ext.isChrome) ct.getGridColumns().forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
				}
			}
		},{

			hidden: false,
			disabled: true,
			flex: 1,
			xtype: 'gridpanel',
			itemId: itemIdMirrorPrefix+'parent-attribute-gridpanel',
			id: idMirrorPrefix+'parent-attribute-gridpanel',
			stateId: idMirrorPrefix+'parent-attribute-gridpanel',
			store: getStore(mirrorParentAttributeStoreId),
			columnLines: true,
			columns: getParentGridColumns(),
			viewConfig: {
				stripeRows:true,
				plugins: {
					ptype: 'gridviewdragdrop',
					ddGroup: 'dd-upload_folder_tree',
					enableDrop: false
				},
			},
//			plugins: [self.getCellEditing(),self.getBufferedRenderer()],
			plugins: [self.getBufferedRenderer()],
			selType: 'rowmodel',
			selModel: {
				mode:'MULTI'
			},
			dockedItems: [{
				hidden: false,
				xtype: 'toolbar',
				dock: 'top',
//				ui: 'footer',
//				defaults: {minWidth: 75},
				items: [{
					xtype: 'tbtext',
					text: '<b>Mirror '+AgLang.parent_attribute+'</b>',
				},{
					hidden: false,
					xtype: 'tbseparator'
				},getNeverCurrentButton(),{
					hidden: false,
					xtype: 'tbseparator'
				},getRemoveMappingButton(),{
					hidden: false,
					xtype: 'tbseparator'
				},{
					xtype: 'radiofield',
					boxLabel: AgLang.parent_attribute_parent,
					name: idMirrorPrefix+'parent-attribute-display-type',
					id: idMirrorPrefix+'parent-attribute-display-type-parent',
					padding: '0 5 0 5',
					checked: true,
					handler: function(field,checked){
						if(!checked) loadMirrorAttributePage.delay(250);
					}
				},{
					xtype: 'radiofield',
					boxLabel: AgLang.parent_attribute_ancestor,
					name: idMirrorPrefix+'parent-attribute-display-type',
					id: idMirrorPrefix+'parent-attribute-display-type-ancestor',
					padding: '0 5 0 0',
					handler: function(field,checked){
						if(!checked) loadMirrorAttributePage.delay(250);
					}
				},{
					hidden: false,
					xtype: 'tbseparator'
				},'->',{
					hidden: false,
					xtype: 'tbseparator'
				},getFMABrowserButton()]
			},{
				hidden: true,
				itemId: 'parent-attribute-gridpanel-agpagingtoolbar',
				id: idMirrorPrefix+'parent-attribute-gridpanel-agpagingtoolbar',
				stateId: idMirrorPrefix+'parent-attribute-gridpanel-agpagingtoolbar',
				xtype: 'agpagingtoolbar',
				store: mirrorParentAttributeStoreId,
				dock: 'bottom'
			}],
			listeners: {
				afterrender: function(gridpanel){
					if(Ext.isChrome){
						gridpanel.columns.forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
						var store = gridpanel.getStore();
						store.on({
							load: {
								fn: function(){
									gridpanel.columns.forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
								},
								buffer: 0
							}
						});
					}
				},
				columnhide: function(ct, column, eOpts){
					if(Ext.isChrome) ct.getGridColumns().forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
				},
				columnshow: function(ct, column, eOpts){
					if(Ext.isChrome) ct.getGridColumns().forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
				}
			}

		}],
		listeners: {
			afterrender: function(win){
//				console.log('win.afterrender()');
//				return;
/*
				Ext.data.StoreManager.lookup('modelVersionStore').loadPage(1,{
					callback: function(records, operation, success){
						console.log('modelVersionStore.loadPage():'+success);
						console.log(records);
						console.log(operation);
						console.log(success);
					}
				});
*/

				var conceptBuildStore = Ext.data.StoreManager.lookup('conceptBuildStore');
				conceptBuildStore.loadPage(1,{
					callback: function(records, operation, success){
//						console.log('conceptBuildStore.loadPage():'+success);
//						console.log(records);
//						console.log(operation);
//						console.log(success);
						if(!success) return;
//						return;
						var modelVersionStore = Ext.data.StoreManager.lookup('modelVersionStore');
						modelVersionStore.loadPage(1,{
							callback: function(records, operation, success){
//								console.log('modelVersionStore.loadPage():'+success);
//								console.log(records);
//								console.log(operation);
//								console.log(success);
								if(!success) return;
								var mode_version_record = records.shift();
								var conceptBuildCombobox = Ext.getCmp(idPrefix+'concept-build-combobox');
								if(mode_version_record && conceptBuildCombobox){
									var idx = conceptBuildStore.findBy(function(record){
										if(record.get('ci_id')===mode_version_record.get('ci_id') && record.get('cb_id')===mode_version_record.get('cb_id')){
											return true;
										}else{
											return false;
										}
									});
									if(idx>=0){
										var record = conceptBuildStore.getAt(idx);
										conceptBuildCombobox.setValue(record.get('value'));
										conceptBuildCombobox.setDisabled(false);
										conceptBuildCombobox.on({
											change: function( combobox, newValue, oldValue, eOpts ){
												var record = combobox.findRecordByValue(newValue);
												if(record){
													var mode_version_record = modelVersionStore.getAt(0);
													mode_version_record.beginEdit();
													mode_version_record.set('cb_id',record.get('cb_id'));
													mode_version_record.endEdit(false,['cb_id']);
													modelVersionStore.sync({
														success: function(batch,options){
															loadAttributePage();
														},
														failure: function(batch,options){
															var msg = AgLang.error_submit;
															var proxy = this;
															var reader = proxy.getReader();
															if(reader && reader.rawData && reader.rawData.msg){
																msg += ' ['+reader.rawData.msg+']';
															}
															Ext.Msg.show({
																title: 'Error',
																msg: msg,
																buttons: Ext.Msg.OK,
																icon: Ext.Msg.ERROR,
																fn: function(buttonId,text,opt){
																}
															});
															mode_version_record.reject();
															combobox.setDisabled(true);
														}

													});
												}
											}
										});
									}
								}
							}
						});
					}
				});
			},
			change: function(comp){
				loadAttributePage();
			},
			show: function(comp){
//				comp.down('gridpanel').getStore().loadPage(1);
			},
			beforeclose: function(comp,eOpts){
//				comp.down('gridpanel').getStore().loadPage(1);
			}
		}
	});
	return mapping_mng_win;
};
