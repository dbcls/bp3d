Ext.define('Ext.ux.form.LocalSearchField', {
	extend: 'Ext.form.field.Trigger',
	alias: 'widget.localsearchfield',
	trigger1Cls: Ext.baseCSSPrefix + 'form-clear-trigger',
	trigger2Cls: Ext.baseCSSPrefix + 'form-search-trigger',
	hasSearch : false,
//	paramName : 'query',
	paramName : 'name',
	config: {
		store: null
	},
	initComponent: function() {
		var me = this;
		me.callParent(arguments);
		me.on('specialkey', function(f, e){
			if (e.getKey() == e.ENTER) {
				me.onTrigger2Click();
			}
		});
		if(Ext.isEmpty(me.store)) return;
		if(Ext.isString(me.store)) me.store = Ext.data.StoreManager.lookup(me.store);
/*
		me.store.remoteFilter = true;
		if (!me.store.proxy.hasOwnProperty('filterParam')) {
			me.store.proxy.filterParam = me.paramName;
		}
		me.store.proxy.encodeFilters = function(filters) {
			return filters[0].value;
		}
*/
	},
	afterRender: function(){
		this.callParent();
		this.triggerCell.item(0).setDisplayed(false);
	},
	onTrigger1Click : function(){
		var me = this;
		if (me.hasSearch) {
			me.setValue('');

//			me.store.clearFilter();
			me.store.clearFilter(true);
			me.store.removeAll();


			me.hasSearch = false;
			me.triggerCell.item(0).setDisplayed(false);
			me.updateLayout();
		}
	},
	onTrigger2Click : function(){
		var me = this,
			value = me.getValue();
		if (value.length > 0) {
			me.store.filter({
				id: me.paramName,
				property: me.paramName,
				value: value
			});
			me.hasSearch = true;
			me.triggerCell.item(0).setDisplayed(true);
			me.updateLayout();
		}
	}
});