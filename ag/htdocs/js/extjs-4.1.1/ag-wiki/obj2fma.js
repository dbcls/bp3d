Ext.BLANK_IMAGE_URL = "js/extjs-4.1.1/resources/themes/images/default/tree/s.gif";
function agWiki(params){
	this.params = params;
	this.init();
}
agWiki.prototype.init = function(){
	var self = this;
	console.log(self.params);

	Ext.create('Ext.data.Store', {
		storeId:'simpsonsStore',
		fields:['name', 'email', 'phone'],
		data:{'items':[
			{ 'name': 'Lisa',  "email":"lisa@simpsons.com",  "phone":"555-111-1224"  },
			{ 'name': 'Bart',  "email":"bart@simpsons.com",  "phone":"555-222-1234" },
			{ 'name': 'Homer', "email":"home@simpsons.com",  "phone":"555-222-1244"  },
			{ 'name': 'Marge', "email":"marge@simpsons.com", "phone":"555-222-1254"  }
		]},
		proxy: {
			type: 'memory',
			reader: {
				type: 'json',
				root: 'items'
			}
		}
	});

	Ext.create('Ext.container.Viewport', {
		layout: 'border',
		items: [{
			region: 'center',
			xtype: 'gridpanel',
//			title: 'Simpsons',
			store: Ext.data.StoreManager.lookup('simpsonsStore'),
			columns: [
				{ text: 'Representation ID',  dataIndex: 'name' },
				{ text: 'Intended Concept ID', dataIndex: 'email' },
				{ text: 'Dataset', dataIndex: 'phone' },
				{ text: 'Tree', dataIndex: 'phone' },
				{ text: 'obj Files', dataIndex: 'phone', flex: 1 }
			],
			dockedItems: [{
				xtype: 'pagingtoolbar',
				store: Ext.data.StoreManager.lookup('simpsonsStore'),
				dock: 'bottom',
				displayInfo: true
			}]
		}]
	});
};

Ext.onReady(function(){
	var wiki = new agWiki(Ext.Object.fromQueryString(window.location.search.substring(1)));
});
