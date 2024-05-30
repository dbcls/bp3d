Ext.define('Ag.ExtJS', {
	override: 'Ag.Main',
	initExtJS : function(){
		var self = this;
		Ext.QuickTips.init();
	//		Ext.state.Manager.setProvider(new Ext.state.CookieProvider()); //ソート順とかをCookieに登録する為に必要らしい
		Ext.state.Manager.setProvider(new Ext.state.LocalStorageProvider({
			prefix: self.DEF_LOCALDB_PROVIDER_PREFIX,
			listeners: {
				statechange: function(provider, key, value, eOpts){
				}
			}
		}));
	}
});
