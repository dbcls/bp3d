/*
 * Ext JS Library 2.2
 * Copyright(c) 2006-2008, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */

Ext.app.SearchField = Ext.extend(Ext.form.TwinTriggerField, {
	initComponent : function(){
		Ext.app.SearchField.superclass.initComponent.call(this);
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
	paramName : 'query',
	keyword   : '',

	onTrigger1Click : function(){
		_dump("Ext.app.SearchField.onTrigger1Click()");
		try{
			if(this.hasSearch){
				this.el.dom.value = '';
				this.keyword = '';

//				var treeCmp = Ext.getCmp('navigate-tree-panel');
//				var search_node = treeCmp.getNodeById('search');
//				if(!Ext.isEmpty(search_node)) search_node.remove();

				this.triggers[0].hide();
				this.hasSearch = false;
			}
		}catch(e){
			_dump("Ext.app.SearchField.onTrigger1Click():"+e);
		}
	},

	onTrigger2Click : function(){
		_dump("Ext.app.SearchField.onTrigger2Click()");
		try{
			var v = this.getRawValue();
			_dump("Ext.app.SearchField.onTrigger2Click():v.length=["+v.length+"]");
			if(v.length < 1){
				this.onTrigger1Click();
				return;
			}
			this.keyword = v;

			var urlOBj = Ext.urlDecode(_location.location.search.substr(1));
			urlOBj.node = 'search';
			urlOBj[this.paramName] = v;
			_location.location.search = Ext.urlEncode(urlOBj);

			this.hasSearch = true;
			this.triggers[0].show();
		}catch(e){
			_dump("Ext.app.SearchField.onTrigger2Click():"+e);
		}
	}
});