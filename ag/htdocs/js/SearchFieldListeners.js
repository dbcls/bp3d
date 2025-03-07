/*
 * Ext JS Library 2.2
 * Copyright(c) 2006-2008, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */

Ext.app.SearchFieldListeners = Ext.extend(Ext.form.TwinTriggerField, {
	initComponent : function(){
		Ext.app.SearchFieldListeners.superclass.initComponent.call(this);
		this.on('specialkey', function(f, e){
			if(e.getKey() == e.ENTER) this.onTrigger2Click();
		}, this);
	},

	validationEvent:false,
	validateOnBlur:false,
	trigger1Class:'x-form-clear-trigger',
	trigger2Class:'x-form-search-trigger',
	hideTrigger1:true,
	width:180,
	hasSearch : false,
	keyword   : '',

	onTrigger1Click : function(){
		if(this.hasSearch){
			this.el.dom.value = '';
			this.keyword = '';
			this.triggers[0].hide();
			this.hasSearch = false;
			this.fireEvent('clear',this);
		}
	},

	onTrigger2Click : function(){
		var v = this.getRawValue();
		if(v.length < 1){
			this.onTrigger1Click();
			return;
		}
		this.keyword = v;
		this.hasSearch = true;
		this.triggers[0].show();
		this.fireEvent('search',this,this.keyword);
	}
});