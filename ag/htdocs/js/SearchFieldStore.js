/*
 * Ext JS Library 2.2
 * Copyright(c) 2006-2008, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */

Ext.app.SearchFieldStore = Ext.extend(Ext.form.TwinTriggerField, {
	initComponent : function(){
		Ext.app.SearchField.superclass.initComponent.call(this);
		this.on('specialkey', function(f, e){
			if(e.getKey() == e.ENTER){
				this.onTrigger2Click();
			}
		}, this);
	},

	validationEvent:false,
	validateOnBlur:false,
	trigger1Class:'x-form-clear-trigger',
	trigger2Class:'x-form-search-trigger',
	hideTrigger1:true,
	width:180,
	hasSearch : false,
	paramName : 'query',
	pageSize : 20,

	onTrigger1Click : function(){
		_dump("Ext.app.SearchFieldStore.onTrigger1Click()");
		try{
			if(this.hasSearch){
				this.el.dom.value = '';
				var o = {start: 0};
				this.store.baseParams = this.store.baseParams || {};
				this.store.baseParams[this.paramName] = '';
				this.store.reload({params:o});
				this.triggers[0].hide();
				this.hasSearch = false;
			}
		}catch(e){
			_dump("Ext.app.SearchFieldStore.onTrigger1Click():"+e);
		}
	},

	onTrigger2Click : function(){
		_dump("Ext.app.SearchFieldStore.onTrigger2Click()");
		try{
			var v = this.getRawValue();
			_dump("Ext.app.SearchFieldStore.onTrigger2Click():v.length=["+v.length+"]");
			if(v.length < 1){
				this.onTrigger1Click();
				return;
			}
			var o = {start:0,limit:this.pageSize};
			this.store.baseParams = this.store.baseParams || {};
			this.store.baseParams[this.paramName] = v;
			this.store.reload({params:o});
			this.hasSearch = true;
			this.triggers[0].show();
		}catch(e){
			_dump("Ext.app.SearchFieldStore.onTrigger2Click():"+e);
		}
	}
});
