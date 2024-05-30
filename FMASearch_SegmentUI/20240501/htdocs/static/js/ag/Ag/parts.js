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

Ext.define('Ag.view.BoundList', {
	override: 'Ext.view.BoundList',
	createPagingToolbar: function() {
		return Ext.widget('pagingtoolbar', {
			id: this.id + '-paging-toolbar',
			pageSize: this.pageSize,
			store: this.dataSource,
			border: false,
			displayInfo: true,
			displayMsg: '{0} - {1} of {2}',
			ownerCt: this,
			ownerLayout: this.getComponentLayout()
		});
	}
});

/*
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
*/

var fmaidTest = /^[FMA0-9:]+$/;
Ext.apply(Ext.form.field.VTypes, {
	fmaid: function(val, field) {
		return fmaidTest.test(val);
	},
	fmaidText: 'Not a valid FMAID.',
	fmaidMask: /[AFM0-9:]/
});

var fmanameTest = /^[A-Za-z0-9 ]+$/;
Ext.apply(Ext.form.field.VTypes, {
	fmaname: function(val, field) {
		return fmanameTest.test(val);
	},
	fmanameText: 'Not a valid Name.',
	fmanameMask: /[A-Za-z0-9 ]/
});

var fmasearchTest = /^[A-Za-z0-9\"\(\)\- ]+$/;
Ext.apply(Ext.form.field.VTypes, {
	fmasearch: function(val, field) {
		return fmasearchTest.test(val);
	},
	fmasearchText: 'Not a valid keyword.',
	fmasearchMask: /[A-Za-z0-9\"\(\)\- ]/
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

Ext.define('Ag.window.FilenamePrompt', {
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

Ext.define('Ag.form.field.ComboBox', {
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

Ext.define('Ag.form.field.OpacityComboBox', {
	extend: 'Ext.form.field.ComboBox',
	alias: 'widget.agopacitycombobox',
	typeAhead: true,
	triggerAction: 'all',
	lazyRender:true,
	queryMode: 'local',
	selectOnTab: true,
	enableKeyEvents: true,
	store: Ext.create('Ext.data.ArrayStore',{
		fields: ['value','display'],
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
	valueField: 'value',
	displayField: 'display',
	onKeyDown: function(e) {
		var me = this;
		e.stopPropagation();
		me.callParent(arguments);
	},
	onKeyUp: function(e) {
		var me = this;
		e.stopPropagation();
		me.callParent(arguments);
	},
	onKeyPress: function(e) {
		var me = this;
		e.stopPropagation();
		me.callParent(arguments);
	}
});

Ext.define('Ag.button.OpacityButton', {
	extend: 'Ext.button.Button',
	alias: 'widget.agopacitybutton',
	text: 'Opacity',
	menu: {
		items:[{
			text: '1.0'
		},{
			text: '0.8'
		},{
			text: '0.6'
		},{
			text: '0.4'
		},{
			text: '0.3'
		},{
			text: '0.2'
		},{
			text: '0.1'
		},{
			text: '0.05'
		},{
			text: '0.0'
		}]
	},
	initComponent: function() {
		var me = this;
		me.callParent();
		me.menu.on({
			click: function(menu, item, e, eOpts){
				var opacity = parseFloat(item.text);
				me.fireEvent('opacitychange',me,opacity,{});
			}
		});
	}
});

Ext.define('Ag.grid.column.Column', {
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

Ext.define('Ext.grid.column.CDI', {
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
//			if(record.data.art_id && !record.data.cm_use){
//				metaData.style += 'color:red;';
//			}
		}
		return value;
	},
});

Ext.define('Ag.grid.column.FileSize', {
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

Ext.define('Ag.grid.column.Number', {
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

Ext.define('Ag.grid.column.Opacity', {
	extend: 'Ag.grid.column.Number',
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
		var rtn = value;
		if(Ext.isObject(metaData) && Ext.isString(metaData.tdCls)){
			metaData.tdCls += ' bp3d-grid-cell-opacity';
			var p = store.getProxy();
			p.extraParams = p.extraParams || {};
			if(Ext.isDefined(p.extraParams) && Ext.isDefined(p.extraParams._pickIndex) && p.extraParams._pickIndex==rowIndex){
				metaData.tdCls += ' bp3d-pick-index';
			}else if(Ext.isBoolean(record.data.target_record) && record.data.target_record){
				metaData.tdCls += ' bp3d-pick-index';
			}
		}
		if(Ext.isObject(metaData) && Ext.isObject(metaData.column) && Ext.isString(metaData.column.format)){
			rtn = Ext.util.Format.number(value,metaData.column.format);
		}else{
			rtn = Ext.util.Format.number(value,this.format || '0.00');
		}
		rtn = Ext.String.format('<div data-value="{0}">{1}</div>',rtn,rtn);
		return rtn;
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

Ext.define('Ag.grid.column.CheckBase', {
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

Ext.define('Ag.grid.column.Check', {
	extend: 'Ag.grid.column.CheckBase',
	alias: 'widget.agcheckcolumn',
	listeners:{
		checkchange : function(column,recordIndex,checked,eOpts){
			column.ownerCt.view.panel.store.getAt(recordIndex).commit();
		}
	}
});

Ext.define('Ag.grid.column.Remove', {
	extend: 'Ag.grid.column.Check',
	alias: 'widget.agremovecolumn',
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
			if(!value){
				cls.push(cssPrefix + 'grid-checkheader-checked');
			}
			if(record.data.disabled || record.data[this.dataIndex+'_disabled']){
				metaData.tdCls += ' '+ cssPrefix + 'item-disabled';
				cls.push(cssPrefix + 'form-field');
			}
			return '<div class="' + cls.join(' ') + '">&#160;</div>';
		}else{
			return !value;
		}
	},
	listeners:{
		checkchange : function(column,recordIndex,checked,eOpts){
			var record = column.ownerCt.view.panel.store.getAt(recordIndex);
			record.commit();
//			console.log(column,recordIndex,checked,record.getData());
			column.view.fireEvent('removechange',record,checked,eOpts);
		}
	}
});

Ext.define('Ag.grid.column.SelectedCheck', {
	extend: 'Ag.grid.column.Check',
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

Ext.define('Ag.grid.column.Recalc', {
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

Ext.define('Ag.grid.column.ColorBase', {
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
	renderer  : function (value,metaData,record,rowIndex,colIndex,store,view) {
		var gridpanel = this;
		var rtn = value;
//		var column = gridpanel.columns[metaData.columnIndex];
//		console.log(this,value,metaData,record,rowIndex,colIndex,store,view );
//		console.log( gridpanel.headerCt );
//		console.log( gridpanel.headerCt.getHeaderAtIndex(colIndex) );
		var column = gridpanel.headerCt.getHeaderAtIndex(colIndex);
		if(Ext.isObject(metaData) && Ext.isString(metaData.tdCls)){
			metaData.tdCls += ' bp3d-grid-cell-color';
			var p = store.getProxy();
			p.extraParams = p.extraParams || {};
			if(Ext.isDefined(p.extraParams) && Ext.isDefined(p.extraParams._pickIndex) && p.extraParams._pickIndex==rowIndex){
				metaData.tdCls += ' bp3d-pick-index';
			}else if(Ext.isBoolean(record.data.target_record) && record.data.target_record){
				metaData.tdCls += ' bp3d-pick-index';
			}
//			value = Ext.util.Format.format('<span style="border:1px solid #DDDDDD;background-color:{0};">&nbsp;&nbsp;&nbsp;&nbsp;</span>',value);
//			value = Ext.String.format('<div style="border:1px solid gray;background:{0};width:{1}px;height:{2}px;"> </div>',value,Ag.Def.COLOR_COLUMN_WIDTH-22,24-11);
			rtn = Ext.String.format('<div style="border:1px solid gray;background:{0};min-width:32px;width:{1}px;height:{2}px;display:inline-block;" data-value="{3}"> </div>',value,column.getWidth()-22,24-11,value);
		}
		return rtn;
	},
	processEvent: function(type, view, cell, recordIndex, cellIndex, e,  record, row) {
		var me = this;
		if(type == 'mousedown'){
			return false;
		}
		else if(type=='click'){
			me.view = view;
			me.record = record ? record : view.panel.store.getAt(recordIndex);
			if(me.getEditor){
				var ed = me.getEditor(me.record,me);
				if(ed.hasListener('select')) ed.un('select',me.select,me);
				ed.on('select',me.select,me);
			}
		}
		else{
//			console.log(type);
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

Ext.define('Ag.grid.column.Color', {
	extend: 'Ag.grid.column.ColorBase',
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

Ext.define('Ag.grid.column.Boolean', {
	extend: 'Ext.grid.column.Boolean',
	alias: 'widget.agbooleancolumn',
	align:'center'
});

Ext.define('Ag.grid.panel', {
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
			itemkeydown: function(view, record, item, index, e, eOpts){
				e.stopEvent();
				if(e.ctrlKey && e.getKey() == e.A){
					var viewDom = view.el.dom;
					var scX = viewDom.scrollLeft;
					var scY = viewDom.scrollTop;
					var selModel = view.getSelectionModel();
					selModel.deselectAll(true);
					selModel.selectAll();
					view.focusRow(index);
					view.scrollBy(scX,scY,false);
					e.stopEvent()
				}else if(e.getKey() == e.DELETE){
					var toolbar = view.up('gridpanel').getDockedItems('toolbar[dock="top"]')[0];
					var button = toolbar.getComponent('delete');
					if(button && !button.isDisabled() && !button.isHidden()) button.fireEvent('click',button);
				}
			}
		});
	}
});

Ext.define('Ag.tree.Panel', {
	extend: 'Ext.tree.Panel',
	alias: 'widget.agtreepanel',
	afterRender: function() {
		var me = this;
		me.callParent();
		me.getView().on({
			itemkeydown: function(view, record, item, index, e, eOpts){
				if(e.getKey() == e.DELETE){
					var toolbar = view.up('treepanel').getDockedItems('toolbar[dock="top"]')[0];
					var button = toolbar.getComponent('delete');
					if(button && !button.isDisabled() && !button.isHidden()) button.fireEvent('click',button);
				}
			}
		});
	}
});

Ext.define('Ag.menu.ColorMenu', {
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
			plain: false,
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

var DEF_COLOR = '#F0D2A0';

Ext.define('Ag.button.ColorButton', {
	extend: 'Ext.button.Button',
	alias: 'widget.agcolorbutton',
	requires: ['Ag.menu.ColorMenu'],
	text: 'Color',
	menu: {
		xtype: 'agcolormenu',
		value: DEF_COLOR
	},
	initComponent: function() {
		var me = this;
		me.callParent();
		me.menu.on({
			select: function(picker, color, eOpts){
				me.fireEvent('colorchange',me,color,{});
			}
		});
	}
});

/*
Ext.define('Ag.data.Store', {
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
Ext.define('Ag.data.Store', {
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

Ext.define('Ag.form.field.PageSizeComboBox', {
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
			[ 500],
			[ 750],
			[1000]
		]
	}),
	valueField: 'value',
	displayField: 'value',
	maskRe: /[0-9]/,
	value: 50,
	width: 70,
	enableKeyEvents: true,
	onKeyDown: function(e) {
		var me = this;
		e.stopPropagation();
		me.callParent(arguments);
	},
	onKeyUp: function(e) {
		var me = this;
		e.stopPropagation();
		me.callParent(arguments);
	},
	onKeyPress: function(e) {
		var me = this;
		e.stopPropagation();
		me.callParent(arguments);
	}
});




Ext.define('Ag.toolbar.Paging', {
	extend: 'Ext.toolbar.Paging',
	requires: ['Ag.form.field.PageSizeComboBox'],
	alias: 'widget.agpagingtoolbar',
	displayInfo: true,
	displayMsg: '{0} - {1} / {2}',
	emptyMsg: "No data to display",
	inputItemWidth: 44,
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
				blur: me.onPagingBlur,
				keydown: function(field,e,eOpts){
					e.stopPropagation();
					me.onPagingKeyDown(field,e,eOpts);
				},
				keypress: function(field,e,eOpts){
					e.stopPropagation();
				},
				keyup: function(field,e,eOpts){
					e.stopPropagation();
				}
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
		},
		'-',
		{
			xtype:'agpagesizecombobox',
			itemId: me.id+'-agpagesizecombobox',
			stateful: true,
			stateId: me.id+'-agpagesizecombobox',
			listeners : {
				afterrender : function(combobox){
					var toolbar = combobox.up('agpagingtoolbar');
					if(toolbar){
						var pageSize = toolbar.getStore().pageSize;
						var state = combobox.getState() || {value:pageSize};
						state.value = state.value || pageSize;
						if(state.value!=pageSize){
							combobox.setValue(state.value);
							combobox.fireEvent('select',combobox);
						}else{
							combobox.suspendEvents(false);
							combobox.setValue(state.value);
							combobox.resumeEvents();
						}
					}
					if(combobox.editable && combobox.stateful){
						combobox.on('beforestatesave',function(stateful, state, eOpts){
							if(Ext.isEmpty(state.value)) state.value = combobox.getValue()-0;
						});
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

Ext.define('Ag.form.field.ColorDisplay', {
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
Ext.define('Ag.grid.column.CDIName', {
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
//			if(record.data.art_id && !record.data.cm_use){
//				metaData.style += 'color:red;';
//			}
		}
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
		return value;
	},
});
Ext.define('Ag.grid.column.CDINameE', {
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
//			if(record.data.art_id && !record.data.cm_use){
//				metaData.style += 'color:red;';
//			}
		}
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
		return value;
	},
});
Ext.define('Ag.grid.column.ConceptArtMapPart', {
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
//			if(record.data.art_id && !record.data.cm_use){
//				metaData.style += 'color:red;';
//			}
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
Ext.define('Ag.form.field.CDINameDisplay', {
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
Ext.define('Ag.form.field.CDINameEDisplay', {
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
