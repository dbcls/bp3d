//未完成

Ext.ux.NoLabelsLayout = function( config ){
	Ext.ux.NoLabelsLayout.superclass.constructor.call( this, config );
	var template = new Ext.Template(
		'<div class="x-form-item x-menu-form-item {5}">',
		'<div class="x-form-element" id="x-form-el-{0}">',
		'</div>',
		'</div><div class="x-form-clear-left"></div>'
	);
	template.disableFormats = true;
	template.compile();
	Ext.ux.NoLabelsLayout.prototype.fieldTpl = template;
};
Ext.extend( Ext.ux.NoLabelsLayout, Ext.layout.FormLayout );

Ext.ux.TextFieldItem = function( config ){
	Ext.ux.TextFieldItem.superclass.constructor.call( this, config );
	this.defaultSize = 20;
	this.el = new Ext.form.TextField({
		cls: 'x-menu-field',
		id: this.id,
		fieldLabel: this.initialConfig.fieldLabel,
		labelStyle : 'font-family:tahoma,arial,sans-serif;font-size:11px;',
		autoCreate: {
			tag: "input",
			type: "text",
			size: this.initialConfig.size || this.defaultSize,
			autocomplete: "off",
			allowBlank: true
		}
	});
};

Ext.extend( Ext.ux.TextFieldItem, Ext.menu.Item, {
	onClick : function(e){
		e.stopEvent();
	},
	onRender: function( container, position ){
		var form = new Ext.form.FormPanel({
			baseCls : 'x-plain',
			border  : false,
			labelWidth :20
		});
		form.add( this.el );
		form.render( container );
		var textFieldDiv = Ext.get( 'x-form-el-' + this.id );
		textFieldDiv.removeClass( 'x-form-element' );
		textFieldDiv.addClass( 'x-menu-item' );
		textFieldDiv.insertFirst({
			tag: "img",
			src: this.initialConfig.icon || Ext.BLANK_IMAGE_URL,
			cls: 'x-menu-item-icon'
		});
	},
	getTextField: function(){
		return this.el;
	}
});
