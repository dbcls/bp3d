Ext.Msg.textField.on({
	keydown: function(field,e,eOpts){
		e.stopPropagation();
	},
	keypress: function(field,e,eOpts){
		e.stopPropagation();
	},
	keyup: function(field,e,eOpts){
		e.stopPropagation();
	}
});
Ext.Msg.textArea.on({
	keydown: function(field,e,eOpts){
		e.stopPropagation();
	},
	keypress: function(field,e,eOpts){
		e.stopPropagation();
	},
	keyup: function(field,e,eOpts){
		e.stopPropagation();
	}
});

Ext.apply(Ext.data.SortTypes, {
	asFJID: function(art_id){
		if(art_id.match(/^([A-Z]+)([0-9]+)(M*)$/)){
			var art_prefix = RegExp.$1;
			var art_serial = Ext.String.leftPad(RegExp.$2, 10, '0');
			var art_mirror = RegExp.$3;
			return art_prefix+art_serial+art_mirror;
		}else{
			return art_id;
		}
	}
});

Ext.define('My.ag.GridView', {
	override: 'Ext.grid.View',
	refresh: function() {
		var me = this,
		hasFocus = me.el && me.el.isAncestor(Ext.Element.getActiveElement()),
		scrollLeft = 0,
		scrollTop = 0;
		if(me.el){
			scrollLeft = me.el.dom.scrollLeft;
			scrollTop = me.el.dom.scrollTop;
		}

		me.callParent(arguments);
		me.headerCt.setSortState();

		// Create horizontal stretcher element if no records in view and there is overflow of the header container.
		// Element will be transient and destroyed by the next refresh.
		if (me.el && !me.all.getCount() && me.headerCt && me.headerCt.tooNarrow) {
			me.el.createChild({style:'position:absolute;height:1px;width:1px;left:' + (me.headerCt.getFullWidth() - 1) + 'px'});
		}

		if (hasFocus) {
			me.selModel.onLastFocusChanged(null, me.selModel.lastFocused);
		}
		if(me.el){
			me.el.dom.scrollLeft = scrollLeft;
			me.el.dom.scrollTop = scrollTop;
		}
	}
});

var filenameTest = /^[a-z0-9_\-]+$/i;
Ext.apply(Ext.form.field.VTypes, {
	filename: function(val, field) {
		return filenameTest.test(val);
	},
	filenameText: 'Not a valid filename.',
	filenameMask: /[a-z0-9_\-]/i,
	filenameReplaceMask: /[^a-z0-9_\-]/ig
});

Ext.define('Ext.ag.FilenamePrompt', {
	extend: 'Ext.window.MessageBox',
	alias: 'widget.agfilenameprompt',

	initComponent: function() {
		var me = this;
		var baseId = me.id;
		me.callParent();

		var id = me.textField.getId();
		var index = me.promptContainer.items.indexOf(me.textField);
		me.promptContainer.remove(me.textField,true);
		delete me.textField;

		me.textField = new Ext.form.field.Text({
			id: id,
			anchor: '100%',
			allowBlank: false,
			allowOnlyWhitespace: false,
			selectOnFocus: true,
			vtype: 'filename',
			enableKeyEvents: true,
			listeners: {
				validitychange: function( textfield, isValid, eOpts ){
					me.bottomTb.getComponent('ok').setDisabled(!isValid);
					me.bottomTb.getComponent('yes').setDisabled(!isValid);
				},
				afterrender: function( textfield, eOpts ){
				},
				keydown: function(field,e,eOpts){
					me.onPromptKey(field,e,eOpts);
					e.stopPropagation();
				},
				keypress: function(field,e,eOpts){
					e.stopPropagation();
				},
				keyup: function(field,e,eOpts){
					e.stopPropagation();
				},
				scope: me
			}
		});
		me.promptContainer.insert(index,me.textField);
		me.defaultFocus = me.textField;
	}
}, function() {
	Ext.FilenamePrompt = new this();
});

Ext.define('Ext.ag.ComboBox', {
	extend       : 'Ext.form.field.ComboBox',
	alias        : 'widget.agcombobox',
	allowBlank   : false,
	typeAhead    : false,
	editable     : false,
	triggerAction: 'all',
	lazyRender   : true,
	queryMode    : 'local',
	valueField   : 'value',
	displayField : 'display',
	tpl: '<ul class="x-list-plain"><tpl for="."><li class="x-boundlist-item<tpl if="disabled"> ag-disabled</tpl><tpl if="hidden"> x-hidden</tpl>">{display}</li></tpl></ul>',
	onBeforeSelect: function(list, record) {
		var me = this;
		if(record.data.disabled) return false;
		return me.callParent(arguments);
	}
});

Ext.define('Ext.ag.OpacityComboBox', {
	extend: 'Ext.form.field.ComboBox',
	alias: 'widget.agopacitycombobox',
	typeAhead: true,
	triggerAction: 'all',
	lazyRender:true,
	queryMode: 'local',
	selectOnTab: true,
	store: Ext.create('Ext.data.ArrayStore',{
		fields: ['myId','displayText'],
		data: [
			[1.0, 1.0],
			[0.8, 0.8],
			[0.6, 0.6],
			[0.4, 0.4],
			[0.3, 0.3],
			[0.2, 0.2],
			[0.1, 0.1],
			[0.05, 0.05],
			[0.0, 0.0]
		]
	}),
	valueField: 'myId',
	displayField: 'displayText'
});

Ext.define('Ext.ag.Column', {
	extend: 'Ext.grid.column.Column',
	alias: 'widget.agcolumn',
	renderer: function(value,metaData,record,rowIndex,colIndex,store){
		if(Ext.isObject(metaData) && Ext.isString(metaData.tdCls)){
			var p = store.getProxy();
			p.extraParams = p.extraParams || {};
			if(Ext.isDefined(p.extraParams) && Ext.isDefined(p.extraParams._pickIndex) && p.extraParams._pickIndex==rowIndex){
				metaData.tdCls += ' bp3d-pick-index';
			}else if(Ext.isBoolean(record.data.target_record) && record.data.target_record){
				metaData.tdCls += ' bp3d-pick-index';
			}
		}
		return value;
	},
});

Ext.define('Ext.ag.ColumnCDI', {
	extend: 'Ext.grid.column.Column',
	alias: 'widget.agcolumncdi',
	renderer: function(value,metaData,record,rowIndex,colIndex,store){
		if(Ext.isObject(metaData) && Ext.isString(metaData.tdCls)){
			var p = store.getProxy();
			p.extraParams = p.extraParams || {};
			if(Ext.isDefined(p.extraParams) && Ext.isDefined(p.extraParams._pickIndex) && p.extraParams._pickIndex==rowIndex){
				metaData.tdCls += ' bp3d-pick-index';
			}else if(Ext.isBoolean(record.data.target_record) && record.data.target_record){
				metaData.tdCls += ' bp3d-pick-index';
			}
			if(record.data.art_id && !record.data.cm_use){
				metaData.style += 'color:red;';
			}
		}
		return value;
	},
});

Ext.define('Ext.ag.FileSizeColumn', {
	extend: 'Ext.grid.column.Number',
	alias: 'widget.agfilesizecolumn',
	align:'right',
	renderer: function(value,metaData,record,rowIndex,colIndex,store){
		if(Ext.isObject(metaData) && Ext.isString(metaData.tdCls)){
			var p = store.getProxy();
			p.extraParams = p.extraParams || {};
			if(Ext.isDefined(p.extraParams) && Ext.isDefined(p.extraParams._pickIndex) && p.extraParams._pickIndex==rowIndex){
				metaData.tdCls += ' bp3d-pick-index';
			}else if(Ext.isBoolean(record.data.target_record) && record.data.target_record){
				metaData.tdCls += ' bp3d-pick-index';
			}
		}
		return Ext.util.Format.fileSize(value);
	},
});

Ext.define('Ext.ag.NumberColumn', {
	extend: 'Ext.grid.column.Number',
	alias: 'widget.agnumbercolumn',
	align:'right',
	renderer: function(value,metaData,record,rowIndex,colIndex,store){
		if(Ext.isObject(metaData) && Ext.isString(metaData.tdCls)){
			var p = store.getProxy();
			p.extraParams = p.extraParams || {};
			if(Ext.isDefined(p.extraParams) && Ext.isDefined(p.extraParams._pickIndex) && p.extraParams._pickIndex==rowIndex){
				metaData.tdCls += ' bp3d-pick-index';
			}else if(Ext.isBoolean(record.data.target_record) && record.data.target_record){
				metaData.tdCls += ' bp3d-pick-index';
			}
		}
		if(Ext.isObject(metaData) && metaData.column.format){
			return Ext.util.Format.number(value,metaData.column.format);
		}else{
			return value;
		}
	},
});

Ext.define('Ext.ag.OpacityColumn', {
	extend: 'Ext.ag.NumberColumn',
	alias: 'widget.agopacitycolumn',
	format:'0.00',
	field:{
		xtype:'agopacitycombobox',
		allowBlank:false
	},
	processEvent: function(type, view, cell, recordIndex, cellIndex, e,  record, row) {
		var me = this;
		if(type == 'mousedown'){
			return false;
		}
		if(type=='click'){
			me.view = view;
			me.record = record ? record : view.panel.store.getAt(recordIndex);
			me.recordIndex = recordIndex;
			if(me.getEditor){
				var ed = me.getEditor(me.record,me);
				if(ed.hasListener('select')) ed.un('select',me.select,me);
				ed.on('select',me.select,me);
			}
		}
		return me.callParent(arguments);
	},
	renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
		if(Ext.isObject(metaData) && Ext.isString(metaData.tdCls)){
			var p = store.getProxy();
			p.extraParams = p.extraParams || {};
			if(Ext.isDefined(p.extraParams) && Ext.isDefined(p.extraParams._pickIndex) && p.extraParams._pickIndex==rowIndex){
				metaData.tdCls += ' bp3d-pick-index';
			}else if(Ext.isBoolean(record.data.target_record) && record.data.target_record){
				metaData.tdCls += ' bp3d-pick-index';
			}
		}
		if(Ext.isObject(metaData) && Ext.isObject(metaData.column) && Ext.isString(metaData.column.format)){
			return Ext.util.Format.number(value,metaData.column.format);
		}else{
			return Ext.util.Format.number(value,this.format || '0.00');
		}
	},
	select : function(combo,record,index){
		var me = this;
		if(me.record){
			me.record.set(me.dataIndex,combo.getValue());
			if(me.record.isModified(me.dataIndex)){
				me.record.commit();
				me.view.fireEvent('opacitychange',me.record,combo.getValue(),{});
				me.view.refresh();
				me.view.focusRow(me.recordIndex);
			}
		}
	}
});

Ext.define('Ext.ag.CheckBaseColumn', {
	extend: 'Ext.grid.column.CheckColumn',
	alias: 'widget.agcheckbasecolumn',
	align:'center',
	resizable:false,
	renderer: function(value,metaData,record,rowIndex,colIndex,store){
		if(Ext.isObject(metaData) && Ext.isString(metaData.tdCls)){
			var p = store.getProxy();
			p.extraParams = p.extraParams || {};
			if(Ext.isDefined(p.extraParams) && Ext.isDefined(p.extraParams._pickIndex) && p.extraParams._pickIndex==rowIndex){
				metaData.tdCls += ' bp3d-pick-index';
			}else if(Ext.isBoolean(record.data.target_record) && record.data.target_record){
				metaData.tdCls += ' bp3d-pick-index';
			}
			var cssPrefix = Ext.baseCSSPrefix,
					cls = [cssPrefix + 'grid-checkheader'];
			if(value){
				cls.push(cssPrefix + 'grid-checkheader-checked');
			}
			if(record.data.disabled || record.data[this.dataIndex+'_disabled']){
				metaData.tdCls += ' '+ cssPrefix + 'item-disabled';
				cls.push(cssPrefix + 'form-field');
			}
			return '<div class="' + cls.join(' ') + '">&#160;</div>';
		}else{
			return value;
		}
	},
	processEvent: function(type, view, cell, recordIndex, cellIndex, e,  record, row) {
		var me = this;
		if(type == 'mousedown' || type=='click'){
			me.view = view;
			me.record = record ? record : view.panel.store.getAt(recordIndex);
			if(me.record && (me.record.data.disabled || me.record.data[this.dataIndex+'_disabled'])){
				return false;
			}
		}
		return me.callParent(arguments);
	},
});

Ext.define('Ext.ag.CheckColumn', {
	extend: 'Ext.ag.CheckBaseColumn',
	alias: 'widget.agcheckcolumn',
	listeners:{
		checkchange : function(column,recordIndex,checked,eOpts){
			column.ownerCt.view.panel.store.getAt(recordIndex).commit();
		}
	}
});

Ext.define('Ext.ag.SelectedCheckColumn', {
	extend: 'Ext.ag.CheckColumn',
	alias: 'widget.agselectedcheckcolumn',
	hideable: false,
	renderer: function(value,metaData,record,rowIndex,colIndex,store){
		if(Ext.isObject(metaData) && Ext.isString(metaData.tdCls)){
			var p = store.getProxy();
			p.extraParams = p.extraParams || {};
			if(Ext.isDefined(p.extraParams) && Ext.isDefined(p.extraParams._pickIndex) && p.extraParams._pickIndex==rowIndex){
				metaData.tdCls += ' bp3d-pick-index';
			}else if(Ext.isBoolean(record.data.target_record) && record.data.target_record){
				metaData.tdCls += ' bp3d-pick-index';
			}
			if(record.data.is_temporary || record.data.disabled){
				return '<div class="x-grid-cell-inner">&#160;</div>';
			}else{
				return Ext.util.Format.format('<div class="x-grid-checkheader{0}" style="cursor:default;">&#160;</div>',value?' x-grid-checkheader-checked':'');
			}
		}else{
			return value;
		}
	},
	processEvent: function(type, view, cell, recordIndex, cellIndex, e,  record, row) {
		var me = this;
		if(type == 'mousedown' || type=='click'){
			me.view = view;
			me.record = record ? record : view.panel.store.getAt(recordIndex);
			if(me.record && (me.record.data.is_temporary || me.record.data.disabled || me.record.data[this.dataIndex+'_disabled'])){
				return false;
			}
		}
		return me.callParent(arguments);
	},
});

Ext.define('Ext.ag.RecalcColumn', {
	extend: 'Ext.grid.column.Column',
	alias: 'widget.agrecalccolumn',
	renderer: function(value,metaData,record,rowIndex,colIndex,store){
		if(Ext.isObject(metaData) && Ext.isString(metaData.tdCls)){
			var p = store.getProxy();
			p.extraParams = p.extraParams || {};
			if(Ext.isDefined(p.extraParams) && Ext.isDefined(p.extraParams._pickIndex) && p.extraParams._pickIndex==rowIndex){
				metaData.tdCls += ' bp3d-pick-index';
			}else if(Ext.isBoolean(record.data.target_record) && record.data.target_record){
				metaData.tdCls += ' bp3d-pick-index';
			}
			if(record.get('style')){
				if(Ext.isEmpty(metaData.style)) metaData.style = '';
				metaData.style += record.get('style');
			}
		}
		return value;
	},
});

Ext.define('Ext.ag.ColorBaseColumn', {
	extend: 'Ext.grid.column.Column',
	alias: 'widget.agcolorbasecolumn',
	requires: ['Ext.ag.ColorPickerPalletField'],
	field:{
		xtype:'colorpickerpalletfield',
		allowBlank:false,
		allowOnlyWhitespace:false
	},
	align     : 'center',
	resizable : false,
	renderer  : function (value,metaData,record,rowIndex,colIndex,store) {
		if(Ext.isObject(metaData) && Ext.isString(metaData.tdCls)){
			var p = store.getProxy();
			p.extraParams = p.extraParams || {};
			if(Ext.isDefined(p.extraParams) && Ext.isDefined(p.extraParams._pickIndex) && p.extraParams._pickIndex==rowIndex){
				metaData.tdCls += ' bp3d-pick-index';
			}else if(Ext.isBoolean(record.data.target_record) && record.data.target_record){
				metaData.tdCls += ' bp3d-pick-index';
			}
			value = Ext.util.Format.format('<span style="border:1px solid #DDDDDD;background-color:{0};">&nbsp;&nbsp;&nbsp;&nbsp;</span>',value);
		}
		return value;
	},
	processEvent: function(type, view, cell, recordIndex, cellIndex, e,  record, row) {
		var me = this;
		if(type == 'mousedown'){
			return false;
		}
		if(type=='click'){
			me.view = view;
			me.record = record ? record : view.panel.store.getAt(recordIndex);
			if(me.getEditor){
				var ed = me.getEditor(me.record,me);
				if(ed.hasListener('select')) ed.un('select',me.select,me);
				ed.on('select',me.select,me);
			}
		}
		return me.callParent(arguments);
	},
	select : function(combo,record,index){
		var me = this;
		if(me.record){
			var value = combo.getValue();
			if(me.record.get(me.dataIndex) != value) me.record.set(me.dataIndex,value);
			if(me.record.isModified(me.dataIndex)){
				me.view.fireEvent('colorchange',me.record,value,{});
			}
		}
	}
});

Ext.define('Ext.ag.ColorColumn', {
	extend: 'Ext.ag.ColorBaseColumn',
	alias: 'widget.agcolorcolumn',
	select : function(combo,record,index){
		var me = this;
		if(me.record){
			var value = combo.getValue();
			if(me.record.get(me.dataIndex) != value) me.record.set(me.dataIndex,value);
			if(me.record.isModified(me.dataIndex)){
				me.record.commit();
				me.view.fireEvent('colorchange',me.record,value,{});
			}
		}
	}
});

Ext.define('Ext.ag.BooleanColumn', {
	extend: 'Ext.grid.column.Boolean',
	alias: 'widget.agbooleancolumn',
	align:'center'
});

Ext.define('Ext.ag.GridPanel', {
	extend: 'Ext.grid.Panel',
	alias: 'widget.aggridpanel',
	columnLines: true,
	loadMask:true,
	viewConfig: {
		stripeRows: true,
		enableTextSelection: false,
		loadMask: false
	},
	selType: 'rowmodel',
	selModel: {
		mode:'MULTI'
	},
	afterRender: function() {
		var me = this;
		me.callParent();
		me.getView().on({
			beforeitemkeydown: function(view, record, item, index, e, eOpts){
				if((e.ctrlKey && e.getKey() == e.A) || e.getKey() == e.DELETE) return true;
				return false;
			},
			itemkeydown: function(view, record, item, index, e, eOpts){
				if(e.ctrlKey && e.getKey() == e.A){
					var viewDom = view.el.dom;
					var scX = viewDom.scrollLeft;
					var scY = viewDom.scrollTop;
					var selModel = view.getSelectionModel();
					selModel.selectAll(true);
					view.focusRow(index);
					view.refresh();
					view.scrollBy(scX,scY,false);
					e.stopEvent()
				}
			}
		});
	}
});



Ext.define('Ext.ag.ColorMenu', {
	extend: 'Ext.menu.Menu',
	alias: 'widget.agcolormenu',
	requires: ['Ext.ag.ColorPickerPallet'],
	hideOnClick : false,
	pickerId : null,
	initComponent : function(){
		var me = this,
			cfg = Ext.apply({}, me.initialConfig);
		delete cfg.listeners;
		Ext.apply(me, {
			plain: true,
			showSeparator: false,
			items: Ext.applyIf({
				cls: Ext.baseCSSPrefix + 'menu-color-item',
				id: me.pickerId,
				floating: false,
				header: false,
				xtype: 'colorpickerpallet'
			}, cfg)
		});
		me.callParent(arguments);
		me.picker = me.down('colorpickerpallet');
		me.relayEvents(me.picker, ['select']);
		if (me.hideOnClick) {
			me.on('select', me.hidePickerOnSelect, me);
		}
	},
	hidePickerOnSelect: function() {
		Ext.menu.Manager.hideAll();
	},
	getValue: function(){
		var me = this;
		return me.picker.getColor ? me.picker.getColor(true) : me.picker.value;
	},
	setValue: function(color){
		var me = this;
		me.picker.setColor(color);
	}
});
/*
Ext.define('Ext.ag.Store', {
	extend: 'Ext.data.Store',
	requires: ['Ext.util.MixedCollection'],
	alias: 'widget.agstore',
	findBufferRecord : function(property, value, start, anyMatch, caseSensitive, exactMatch){
		var me = this;
		if(me.buffered && me.pageMap){
			var records = me.pageMap.getRange(0,me.totalCount-1);
			var m = new Ext.util.MixedCollection();
			m.addAll(records);
			var fn=false;
			if(!Ext.isEmpty(value)){
				if(Ext.isBoolean(value) || Ext.isNumber(value)){
					fn = function(r){return value===r.data[property];};
				}else{
					value = m.createValueMatcher(value, anyMatch, caseSensitive, exactMatch);
					fn = function(r){return value.test(r.data[property]);};
				}
			}
			var index = fn ? m.findIndexBy(fn, null, start) : -1;
			return index !== -1 ? m.getAt(index) : null;
		}else{
			return me.findRecord.apply(me, arguments);
		}
	},
	getBufferRange : function(startIndex, endIndex){
		var me = this;
		if(me.buffered && me.pageMap){
			if(Ext.isEmpty(startIndex)) startIndex = 0;
			if(Ext.isEmpty(endIndex)) endIndex = me.totalCount-1;
			return me.pageMap.getRange.apply(me.pageMap, [startIndex, endIndex]);
		}else{
			return me.getRange.apply(me, arguments);
		}
	}
});
*/
Ext.define('Ext.ag.Store', {
	extend: 'Ext.data.Store',
	requires: ['Ext.util.MixedCollection'],
	alias: 'widget.agstore',
	_getFilters : function(){

		var me = this;
		var min = [],
				length = me.filters.length,
				i = 0;

		for (; i < length; i++) {
			var f = me.filters.getAt(i);
			if(f && f.serialize){
				min[i] = f.serialize();
			}else{
				min[i] = {
					property: f.getProperty ? f.getProperty() : f.property,
					value   : f.getValue ? f.getValue() : f.value,
					anyMatch: false,
					caseSensitive: false,
					exactMatch: true
				};
			}
		}
		return min;
	},
	_setFilters : function(filters){
		var me = this;
		filters = filters || me._getFilters();
		me.clearFilter(true);
		if(Ext.getVersion().major>=5){
			me.setFilters(filters);
		}else{
			me.filter(filters);
		}
	},
	_getGroupingCount : function(groupers){
		var me = this;
		var filters = me._getFilters();
		me._setFilters([{
			property: 'artg_delcause',
			value: null
		}]);
		me.group(groupers);
		var counts = me.count(true);
		me.clearGrouping();
		me._setFilters(filters);
		return counts;
	}
});

Ext.define('Ext.ag.PageSizeComboBox', {
	extend: 'Ext.form.field.ComboBox',
	alias: 'widget.agpagesizecombobox',
	selectOnFocus: true,
	typeAhead: true,
	triggerAction: 'all',
	lazyRender: true,
	queryMode: 'local',
	store: Ext.create('Ext.data.ArrayStore',{
		fields: ['value'],
		data: [
			[  25],
			[  50],
			[  75],
			[ 100],
			[ 250],
			[ 500]
//			[ 750],
//			[1000]
		]
	}),
	valueField: 'value',
	displayField: 'value',
	maskRe: /[0-9]/,
	value: 50,
//	width: 54,
	width: 46,
	listConfig: {
//		minWidth: 46
		minWidth: 54
	}
});




Ext.define('Ext.ag.PagingToolbar', {
	extend: 'Ext.toolbar.Paging',
	requires: ['Ext.ag.PageSizeComboBox'],
	alias: 'widget.agpagingtoolbar',
	displayInfo: true,
	displayMsg: '{0} - {1} / {2}',
	emptyMsg: "No data to display",
	getPagingItems: function(){
		var me = this;
		return [{
			itemId: 'first',
			tooltip: me.firstText,
			overflowText: me.firstText,
			iconCls: Ext.baseCSSPrefix + 'tbar-page-first',
			disabled: true,
			handler: me.moveFirst,
			scope: me
		},{
			itemId: 'prev',
			tooltip: me.prevText,
			overflowText: me.prevText,
			iconCls: Ext.baseCSSPrefix + 'tbar-page-prev',
			disabled: true,
			handler: me.movePrevious,
			scope: me
		},
		'-',
//		me.beforePageText,
		{
			xtype: 'numberfield',
			itemId: 'inputItem',
			name: 'inputItem',
			cls: Ext.baseCSSPrefix + 'tbar-page-number',
			allowDecimals: false,
			minValue: 1,
			hideTrigger: true,
			enableKeyEvents: true,
			keyNavEnabled: false,
			selectOnFocus: true,
			submitValue: false,
			isFormField: false,
			width: me.inputItemWidth,
			margins: '-1 2 3 2',
			listeners: {
				scope: me,
				keydown: me.onPagingKeyDown,
				blur: me.onPagingBlur
			}
		},{
			xtype: 'tbtext',
			itemId: 'afterTextItem',
			text: Ext.String.format(me.afterPageText, 1)
		},
		'-',
		{
			itemId: 'next',
			tooltip: me.nextText,
			overflowText: me.nextText,
			iconCls: Ext.baseCSSPrefix + 'tbar-page-next',
			disabled: true,
			handler: me.moveNext,
			scope: me
		},{
			itemId: 'last',
			tooltip: me.lastText,
			overflowText: me.lastText,
			iconCls: Ext.baseCSSPrefix + 'tbar-page-last',
			disabled: true,
			handler: me.moveLast,
			scope: me
		},
		'-',
		{
			hidden: false,
			itemId: 'refresh',
			tooltip: me.refreshText,
			overflowText: me.refreshText,
			iconCls: Ext.baseCSSPrefix + 'tbar-loading',
			handler: me.doRefresh,
			scope: me
		},'-',{
			xtype:'agpagesizecombobox',
			listeners : {
				afterrender : function(combobox){
					var toolbar = combobox.up('agpagingtoolbar');
					if(toolbar){
						combobox.suspendEvents(false);
						combobox.setValue(toolbar.getStore().pageSize);
						combobox.resumeEvents();
					}
				},
				select : function(combobox, newValue, oldValue, eOpts){
					var toolbar = combobox.up('agpagingtoolbar');
					if(toolbar){
						var store = toolbar.getStore();
						store.pageSize = combobox.getValue();
						store.loadPage(1);
					}
				},
				specialkey: function(combobox, e){
					if(e.getKey() == e.ENTER){
						var toolbar = combobox.up('agpagingtoolbar');
						if(toolbar){
							var store = toolbar.getStore();
							store.pageSize = combobox.getValue();
							store.loadPage(1);
							e.stopEvent();
						}
					}
				}
			}
		},'-'];
	}
});

Ext.define('Ext.ag.ColorDisplay', {
	extend: 'Ext.form.field.Display',
	alias: 'widget.agcolordisplayfield',
	renderer  : function (value,field) {
		if(Ext.isEmpty(value)){
			return value;
		}else{
			return '<div style="text-align:center;cursor:default;padding:0 0 0 2px;"><span style="cursor:default;margin:0 2px 0 4px;border:1px solid #DDDDDD;background-color:' + value + ';">&nbsp;&nbsp;&nbsp;&nbsp;</span>'+value+'</div>';
		}
	}
});

//2016-03-31用 START
Ext.define('Ext.ag.ColumnCDIName', {
	extend: 'Ext.grid.column.Column',
	alias: 'widget.agcolumncdiname',
	width: 80,
	minWidth: 80,
	renderer: function(value,metaData,record,rowIndex,colIndex,store){
		if(Ext.isObject(metaData) && Ext.isString(metaData.tdCls)){
			var p = store.getProxy();
			p.extraParams = p.extraParams || {};
			if(Ext.isDefined(p.extraParams) && Ext.isDefined(p.extraParams._pickIndex) && p.extraParams._pickIndex==rowIndex){
				metaData.tdCls += ' bp3d-pick-index';
			}else if(Ext.isBoolean(record.data.target_record) && record.data.target_record){
				metaData.tdCls += ' bp3d-pick-index';
			}
			if(record.data.art_id && !record.data.cm_use){
				metaData.style += 'color:red;';
			}
		}
/*
		var cmp_id = record.get('cmp_id');
//		cmp_id = 1;
		if(cmp_id){
			var cdi_name = record.get('cdi_name');
			var m = null;
			if(Ext.isString(cdi_name)) m = cdi_name.match(/^(.+?)\-*([LR])$/i);
			if(Ext.isArray(m) && m.length) cdi_name = m[1];
			if(Ext.isString(cdi_name) && cdi_name.length){
				var conceptArtMapPartStore = Ext.data.StoreManager.lookup('conceptArtMapPartStore');
				var cmp_record = conceptArtMapPartStore.findRecord('cmp_id', cmp_id, 0, false, false, true );
				if(cmp_record) value = Ext.String.format('{0}-{1}', cdi_name, cmp_record.get('cmp_abbr'));
			}
		}
*/
		return value;
	},
});
Ext.define('Ext.ag.ColumnCDINameE', {
	extend: 'Ext.grid.column.Column',
	alias: 'widget.agcolumncdinamee',
	innerCls: 'ag-grid-cell-inner-cdiname-e',
	renderer: function(value,metaData,record,rowIndex,colIndex,store){
		if(Ext.isObject(metaData) && Ext.isString(metaData.tdCls)){
			var p = store.getProxy();
			p.extraParams = p.extraParams || {};
			if(Ext.isDefined(p.extraParams) && Ext.isDefined(p.extraParams._pickIndex) && p.extraParams._pickIndex==rowIndex){
				metaData.tdCls += ' bp3d-pick-index';
			}else if(Ext.isBoolean(record.data.target_record) && record.data.target_record){
				metaData.tdCls += ' bp3d-pick-index';
			}
			if(record.data.art_id && !record.data.cm_use){
				metaData.style += 'color:red;';
			}
		}
/*
		var cmp_id = record.get('cmp_id');
//		cmp_id = 1;
		if(cmp_id){
			var cdi_name_e = record.get('cdi_name_e');
			if(Ext.isString(cdi_name_e) && cdi_name_e.length){
				var conceptArtMapPartStore = Ext.data.StoreManager.lookup('conceptArtMapPartStore');
				var cmp_record = conceptArtMapPartStore.findRecord('cmp_id', cmp_id, 0, false, false, true );
				if(cmp_record){
					if(Ext.isObject(metaData) && Ext.isString(metaData.tdCls)){
						value = Ext.String.format('<span class="ag-grid-cell-inner-cdiname-e-{0}">[{0}]</span> {1}', cmp_record.get('cmp_abbr'), cdi_name_e);
					}else{
						value = Ext.String.format('[{0}] {1}', cmp_record.get('cmp_abbr'), cdi_name_e);
					}
				}
			}
		}
*/
		return value;
	},
});
Ext.define('Ext.ag.ColumnConceptArtMapPart', {
	extend: 'Ext.grid.column.Column',
	alias: 'widget.agcolumnconceptartmappart',
	width:50,
	minWidth:50,
	renderer: function(value,metaData,record,rowIndex,colIndex,store){
		if(Ext.isObject(metaData) && Ext.isString(metaData.tdCls)){
			var p = store.getProxy();
			p.extraParams = p.extraParams || {};
			if(Ext.isDefined(p.extraParams) && Ext.isDefined(p.extraParams._pickIndex) && p.extraParams._pickIndex==rowIndex){
				metaData.tdCls += ' bp3d-pick-index';
			}else if(Ext.isBoolean(record.data.target_record) && record.data.target_record){
				metaData.tdCls += ' bp3d-pick-index';
			}
			if(record.data.art_id && !record.data.cm_use){
				metaData.style += 'color:red;';
			}
		}
		var cmp_id = record.get('cmp_id');
		var cdi_name = record.get('cdi_name');
		if(Ext.isString(cdi_name) && cdi_name.length){
			var conceptArtMapPartStore = Ext.data.StoreManager.lookup('conceptArtMapPartStore');
			var cmp_record = conceptArtMapPartStore.findRecord('cmp_id', cmp_id, 0, false, false, true );
			if(cmp_record) value = cmp_record.get('cmp_title');
		}else{
			value = '';
		}
		return value;
	},
});
Ext.define('Ext.ag.CDINameDisplay', {
	extend: 'Ext.form.field.Display',
	alias: 'widget.agcdinamedisplayfield',
	renderer: function (value,field) {
//		console.log('renderer()');
		if(Ext.isEmpty(value)) return value;
		var record = field.up('form').getRecord();
		var cmp_id = 0;
		if(0 && record){
			cmp_id = record.get('cmp_id');
		}else{
			var cmp_id_field = field.up('fieldset').getComponent('cmp_id');
			cmp_id = cmp_id_field ? cmp_id_field.getValue() : 0;
		}
//		cmp_id = 1;
		if(cmp_id){
			var conceptArtMapPartStore = Ext.data.StoreManager.lookup('conceptArtMapPartStore');
			var cmp_record = conceptArtMapPartStore.findRecord('cmp_id', cmp_id, 0, false, false, true );
			if(cmp_record) value = Ext.String.format('{0}-{1}', value, cmp_record.get('cmp_abbr'));
		}
		return value;
	}
});
Ext.define('Ext.ag.CDINameEDisplay', {
	extend: 'Ext.form.field.Display',
	alias: 'widget.agcdinameedisplayfield',
	renderer: function (value,field) {
		if(Ext.isEmpty(value)) return value;
		var record = field.up('form').getRecord();
		var cmp_id = 0;
		if(0 && record){
			cmp_id = record.get('cmp_id');
		}else{
			var cmp_id_field = field.up('fieldset').getComponent('cmp_id');
			cmp_id = cmp_id_field ? cmp_id_field.getValue() : 0;
		}
//		cmp_id = 1;
		if(cmp_id){
			var conceptArtMapPartStore = Ext.data.StoreManager.lookup('conceptArtMapPartStore');
			var cmp_record = conceptArtMapPartStore.findRecord('cmp_id', cmp_id, 0, false, false, true );
			if(cmp_record) value = Ext.String.format('[{0}] {1}', cmp_record.get('cmp_abbr'), value);
		}
		return value;
	}
});
//2016-03-31用 END


Ext.define('Ext.ag.SelectDatasetField', {
	extend: 'Ext.container.Container',
	alias: 'widget.agselectdatasetfield',
	requires: [
		'Ext.grid.*',
		'Ext.layout.container.HBox',
		'Ext.layout.container.VBox',
//		'CONCEPT_BUILD',
//		'VERSION',
		'Ext.data.Store',
		'Ext.form.field.ComboBox',
		'Ext.form.field.Checkbox',
		'Ext.form.field.Text',
		'Ext.form.FieldSet',
		'Ext.form.FieldContainer'
	],
	layout: {
		type: 'vbox',
		align: 'stretch',
	},
	concept_datas: [],
	dataset_datas: [],
	destination_dataset_datas: [],

	priorityLabel : 'Priority',
	hidePriority : false,

	initComponent: function(){
		var me = this;

		me.concept_datas.unshift({value:'all',display:'ALL'});
		me.filterConceptStore = Ext.create('Ext.data.Store', {
			autoDestroy: true,
			model: 'CONCEPT_BUILD',
			sorters: [{
				property: 'cb_order',
				direction: 'ASC'
			}],
			data: me.concept_datas
		});

		me.sourceDatasetStore = Ext.create('Ext.data.Store', {
			autoDestroy: true,
			model: 'VERSION',
			sorters: [{
				property: 'mv_order',
				direction: 'ASC'
			},{
				property: 'fmt_version',
				direction: 'DESC'
			}],
			data: me.dataset_datas || [],
			listeners: {
				add: {
					fn: function(store){
						store.filter();
						store.sort();
					},
					buffer: 100
				},
				filterchange: function( store, filters, eOpts ){
					store.sort();
				}
			}
		});

		me.destinationDatasetStore = Ext.create('Ext.data.Store', {
			autoDestroy: true,
			model: 'VERSION',
			sorters: [{
				property: 'mv_priority',
				direction: 'ASC'
			}],
			data: me.destination_dataset_datas || [],
			listeners: {
				add: {
					fn: function(store){
						me.updateMergePriority();
						me.fireEvent('select',me,me.destinationDatasetStore.getRange());
					},
					buffer: 100
				},
				remove: {
					fn: function(store){
						me.updateMergePriority();
						me.fireEvent('select',me,me.destinationDatasetStore.getRange());
					},
					buffer: 100
				}
			}
		});

		me.items = [{

			itemId: 'filter-fieldset',
			xtype: 'fieldset',
			title: 'filter',
//			margin: '0 10 0 10',
			margin: '0 0 0 0',
			height: 74,
			layout: {
				type: 'vbox',
				align: 'stretch',
			},
			items: [{
				itemId: 'concept-combobox',
				fieldLabel: 'Concept',
				labelWidth: 49,
				name: 'concept',
				xtype: 'combobox',
				editable: false,
				matchFieldWidth: false,
				displayField: 'display',
				valueField: 'value',
				queryMode: 'local',
				store: me.filterConceptStore,
				value: 'all',
				listeners: {
					afterrender: function(field, eOpt){
					},
					select: function(field, records, eOpts){
						me.filterSourceDatasetStore();
					}
				}
			},{
				xtype: 'fieldcontainer',
				layout: {
					type: 'hbox',
					align: 'stretch',
				},
				defaults: {
					margin: '0 10 0 0',
				},
				items: [{
					itemId: 'mv_use-checkboxfield',
					xtype: 'checkboxfield',
					boxLabel: AgLang.use,
					name: 'mv_use',
					listeners: {
						afterrender: function(field){
							field.setValue(true);
						},
						change: function(field,newValue,oldValue,eOpts){
							me.filterSourceDatasetStore();
						}
					}
				},{
					itemId: 'mv_frozen-checkboxfield',
					xtype: 'checkboxfield',
					boxLabel: AgLang.not_editable,
					name: 'mv_frozen',
					listeners: {
						change: function(field,newValue,oldValue,eOpts){
							if(!newValue && field.nextSibling('checkboxfield#mv_publish-checkboxfield').getValue()){
								field.nextSibling('checkboxfield#mv_publish-checkboxfield').setValue(false);
							}else{
								me.filterSourceDatasetStore();
							}
						}
					}
				},{
					itemId: 'mv_publish-checkboxfield',
					xtype: 'checkboxfield',
					boxLabel: AgLang.publish,
					name: 'mv_publish',
					listeners: {
						change: function(field,newValue,oldValue,eOpts){
							if(newValue && !field.previousSibling('checkboxfield#mv_frozen-checkboxfield').getValue()){
								field.prev('checkboxfield#mv_frozen-checkboxfield').setValue(true)
							}else{
								me.filterSourceDatasetStore();
							}
						}
					}
				},{
					flex: 1,
					margin: '0 0 0 0',
					itemId: 'keyword-textfield',
					xtype: 'textfield',
					fieldLabel: 'keyword(AND)',
					labelWidth: 82,
					enableKeyEvents: true,
					listeners: {
						change: function(field,newValue,oldValue,eOpts){
							me.filterSourceDatasetStore();
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
				}]
			}]
		},{
			xtype: 'fieldcontainer',
			margin: '6 0 2 0',
			layout: {
				type: 'hbox',
				align: 'bottom',
				pack: 'center',
			},
			items: [{
				xtype: 'label',
				text: 'Drag and Drop',
			}]
		},{

			flex: 1,
			xtype: 'fieldcontainer',
			margin: '0 0 0 0',
			layout: {
				type: 'hbox',
				align: 'stretch',
			},
			defaults: {
				border: true,
			},
			items: [{
				flex: 1,
				title: 'Source Dataset',
				xtype: 'aggridpanel',
				margin: '0 3 0 0',
				store: me.sourceDatasetStore,
				columns: [{
					text: AgLang.version_signage,
					dataIndex: 'version',
					flex: 1,
					minWidth: 72,
					draggable: false,
					hidden:false,
					hideable:false
				}],
				selType: 'rowmodel',
				selModel: {
					mode:'MULTI'
				},
				viewConfig: {
					stripeRows:true,
					plugins: {
						ptype: 'gridviewdragdrop',
						dragText: 'Drag and drop to reorganize'
					}
				},
				listeners: {
					afterrender: function(comp){
						if(comp) comp.columns.forEach(function(c){if(Ext.isEmpty(c.flex)) c.autoSize()});
					},
					selectionchange: function(selModel,selected,eOpts){
					}
				}
			},{
				itemId: 'merge-destination-dataset-grid',
				flex: 1,
				title: 'Destination Dataset',
				xtype: 'aggridpanel',
				margin: '0 0 0 3',
				store: me.destinationDatasetStore,
				columns: [{
					text: AgLang.version_signage,
					dataIndex: 'version',
					flex: 1,
					minWidth: 72,
					draggable: false,
					hidden:false,
					hideable:false,
					sortable: false,
					menuDisabled: false,
				},{
					text: me.priorityLabel,
					hidden: me.hidePriority,
					dataIndex: 'mv_priority',
					width: 40,
					minWidth: 40,
					draggable: false,
					hidden: false,
					hideable: false,
					sortable: false,
					menuDisabled: false,
					align: 'right'
				}],
				selType: 'rowmodel',
				selModel: {
					mode:'MULTI'
				},
				viewConfig: {
					stripeRows:true,
					plugins: {
						ptype: 'gridviewdragdrop',
						dragText: 'Drag and drop to reorganize'
					}
				},
				listeners: {
					afterrender: function(comp){
						if(comp) comp.columns.forEach(function(c){if(Ext.isEmpty(c.flex)) c.autoSize()});
					},
					selectionchange: function(selModel,selected,eOpts){
					}
				}
			}]
		}];
		me.callParent();
	},

	getCount: function(){
		var me = this;
		return me.destinationDatasetStore.getCount();
	},

	getValue: function(){
		var me = this;
		var values = [];
		me.destinationDatasetStore.each(function(record){
			values.push({
				md_id: record.get('md_id'),
				mv_id: record.get('mv_id')
			});
		});
		return values;
	},

	updateMergePriority: function(){
		var me = this;
		me.destinationDatasetStore.suspendEvent('update');
		try{
			me.destinationDatasetStore.each(function(record,idx){
				record.beginEdit();
				record.set('mv_priority',idx+1);
				record.commit(false,['mv_priority']);
				record.endEdit(false,['mv_priority']);
			});
		}catch(e){
			console.error(e);
		}
		me.destinationDatasetStore.resumeEvent('update');

		var grid = me.down('gridpanel#merge-destination-dataset-grid');
		if(grid) grid.getView().refresh();
	},

	filterSourceDatasetStore: function(){
		var me = this;
		Ext.defer(function(){
			var concept = null;
			var mv_use = false;
			var mv_frozen = false;
			var mv_publish = false;
			var keyword = null;
			var filters = [];
			try{concept = me.down('combobox#concept-combobox').getValue();}catch(e){}
			try{mv_use = me.down('checkboxfield#mv_use-checkboxfield').getValue();}catch(e){}
			try{mv_frozen = me.down('checkboxfield#mv_frozen-checkboxfield').getValue();}catch(e){}
			try{mv_publish = me.down('checkboxfield#mv_publish-checkboxfield').getValue();}catch(e){}
			try{keyword = me.down('textfield#keyword-textfield').getValue();}catch(e){}

			if(Ext.isString(concept) && concept.trim().length && concept != 'all'){
				var concept_record;
				try{concept_record = me.down('combobox#concept-combobox').findRecordByValue(concept);}catch(e){}
				if(concept_record){
					filters.push({
						filterFn: function(record){
							return concept_record.get('ci_id') === record.get('ci_id') && concept_record.get('cb_id') === record.get('cb_id');
						}
					});
				}
			}

			if(mv_use) filters.push({property: 'mv_use', value: true});
			if(mv_frozen) filters.push({property: 'mv_frozen', value: true});
			if(mv_publish) filters.push({property: 'mv_publish', value: true});
			if(Ext.isString(keyword) && keyword.trim().length){
				var keywords = keyword.trim().replace(/\s{2,}/,' ').split(' ');
				keywords.forEach(function(keyword){
					keyword = new RegExp(Ext.String.escapeRegex(keyword.trim()),'i');
					filters.push({
						filterFn: function(record){
							return keyword.test(record.get('version')) || keyword.test(record.get('mv_objects_set'));
						}
					});
				});
			}

			me.sourceDatasetStore.clearFilter(filters.length>0?true:false);
			if(filters.length) me.sourceDatasetStore.filter(filters);

		},100);

	}

});

Ext.define('Ext.ag.SelectDatasetWindow', {
	extend: 'Ext.window.Window',
	alias: 'widget.agselectdatasetwindow',
	layout: {
		type: 'vbox',
		align: 'stretch',
	},
	minButtonWidth: 75,
	priorityLabel: 'Order',
	initComponent: function(){
		var me = this;
		me.callParent();

		me.agselectdatasetfield = Ext.create('Ext.ag.SelectDatasetField',{
			margin: '0 10 6 10',
			flex: 1,
			concept_datas: me.concept_datas || [],
			dataset_datas: me.dataset_datas || [],
			priorityLabel: me.priorityLabel,
			listeners: {
				select: function(field, records){
					me.setDisabledSaveButton();
					me.params = me.params || {};
					me.params.mv_ids = [];
					try{me.params.mv_ids = field.getValue();}catch(e){}
					me.params.mv_ids = Ext.encode(me.params.mv_ids);
				}
			}
		});

		me.ok_button = Ext.create('Ext.button.Button',{
			itemId: 'ok',
			text: Ext.MessageBox.buttonText.ok,
			disabled: true,
			listeners: {
				click: function(b,e,eOpts){
					if(b.isDisabled()) return;
					b.setDisabled(true);
					try{
						if(Ext.isFunction(me.callback)){
							me.callback(me.params || {});
						}
						me.close();
					}catch(e){
						console.error(e);
					}
				}
			}
		});

		me.insert(0,me.agselectdatasetfield);

		me.addDocked([{
			xtype: 'toolbar',
			dock: 'bottom',
			ui: 'footer',
			defaults: {minWidth: me.minButtonWidth},
			items: ['->',me.ok_button]
		}]);
	},

	setDisabledSaveButton: function(){
		var me = this;
		var num = me.agselectdatasetfield.getCount();
		var disable = false;
		if(!disable) disable = num===0;
		me.ok_button.setDisabled(disable);
	}
});


Ext.define('Ext.ag.ExportSelectDatasetWindow', {
	extend: 'Ext.ag.SelectDatasetWindow',
	alias: 'widget.agexportselectdatasetwindow',

	filenameLabel: 'Please enter download file name',
	filenameLabelAlign: 'top',
	filenameLabelWidth: 100,
	priorityLabel: 'Priority',

	initComponent: function(){
		var me = this;
		me.callParent();

		me.params = me.params || {};
		if(Ext.isEmpty(me.params.filename)) me.params.filename = '';

		me.textfield = new Ext.form.field.Text({
			margin: '0 10 6 10',
			itemId: 'filename',
			fieldLabel: me.filenameLabel,
			labelAlign: me.filenameLabelAlign,
			labelWidth: me.filenameLabelWidth,
			anchor: '100%',
			allowBlank: false,
			allowOnlyWhitespace: false,
			selectOnFocus: true,
			vtype: 'filename',
			enableKeyEvents: true,
			value: me.params.filename,
			listeners: {
				change: function(field, newValue, oldValue, eOpts){
					me.setDisabledSaveButton();
					me.params = me.params || {};
					me.params.filename = field.getValue();
				},
				keydown: function(field,e,eOpts){
					e.stopPropagation();
				},
				keypress: function(field,e,eOpts){
					e.stopPropagation();
				},
				keyup: function(field,e,eOpts){
					e.stopPropagation();
				},
				scope: me
			}
		});
		me.insert(1,me.textfield);
	},
	setDisabledSaveButton: function(){
		var me = this;
		var num = me.agselectdatasetfield.getCount();
		var disable = false;
		if(!disable) disable = num===0;
		if(!disable) disable = !me.textfield.validate();
		me.ok_button.setDisabled(disable);
		return disable;
	}
});
