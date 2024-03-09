window.ag_extensions = window.ag_extensions || {};
ag_extensions.auth = ag_extensions.auth || {};

ag_extensions.auth._init = function(){
	var self = this;
//	console.log("ag_extensions.auth._init():"+Ext.getCmp('anatomography_comment'));
	self.__parentPanel_id = 'header-panel';
	self.__parentPanel = Ext.getCmp(self.__parentPanel_id);
	if(self.__parentPanel){
		if(self.__parentPanel.rendered){
			self._initUI();
		}else{
			self.__parentPanel.on({
				'render': function(){
					self._initUI();
				},
				buffer: 100,
				single: true
			});
		}
	}else{
		self.__initTask = {
			run: function(){
				self.__parentPanel = Ext.getCmp(self.__parentPanel_id);
				if(!self.__parentPanel) return;
				self.__initTaskRunner.stop(self.__initTask);
				if(self.__parentPanel.rendered){
					self._initUI();
				}else{
					self.__parentPanel.on({
						'render': function(){
							self._initUI();
						},
						buffer: 100,
						single: true
					});
				}
			},
			interval: 1000
		}
		self.__initTaskRunner = new Ext.util.TaskRunner();
		self.__initTaskRunner.start(self.__initTask);
	}
};

ag_extensions.auth._initUI = function(){
	var self = this;
//	console.log("ag_extensions.auth._initUI():"+self.__parentPanel);
//	console.log(self.__parentPanel);
	self.__parentPanel.items.each(function(item,index,length){
		if(item.getXType()!='panel') return true;
		var btbar = item.getBottomToolbar();
		if(Ext.isEmpty(btbar)) return true;
		btbar.add('-',window.gAuthTBButton)
	});
};

ag_extensions.auth.logout = function(b,e){
	Ext.Ajax.request({
		url       : 'ag_login_exit.cgi',
		method    : 'GET',
		params    : {
			_time      : (new Date()).getTime()
		},
		success   : function(conn,response,options,aParam){
			try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
			if(!results || results.success == false){
				var msg = 'OpenID:[' + Cookies.get('openid_url') + '] does not exist.';
				alert("Failure:"+msg);
				return;
			}
			Cookies.clear('openid_session');
			location.href = location.href;
		},
		failure : function(conn,response,options){
			var msg = 'OpenID:[' + Cookies.get('openid_url') + '] Unknown Error.';
			alert("Failure:"+msg);
		}
	});
};
ag_extensions.auth.checkAuth = function(openid_url,aCB){
		Ext.Ajax.request({
			url       : 'ag_login_check.cgi',
			method    : 'GET',
			params    : {
				openid_url : openid_url,
				_time      : (new Date()).getTime()
			},
			success   : function(conn,response,options,aParam){
				try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
				if(!results || results.success == false){
					var msg = 'OpenID:[' + openid_url + '] does not exist.';
					alert("Failure:"+msg);
					if(aCB) (aCB)(undefined);
					return;
				}
				if(results.session){
					if(aCB) (aCB)(results.session);
				}else{
					alert("Undefined sessionID!!");
					if(aCB) (aCB)(undefined);
				}
			},
			failure : function(conn,response,options){
				if(aCB) (aCB)(undefined);
			}
		});
};
ag_extensions.auth.auth = function(aCB){
		Ext.Ajax.request({
			url       : 'auth.cgi',
			method    : 'GET',
			params    : {
				_time      : (new Date()).getTime()
			},
			success   : function(conn,response,options,aParam){
				try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
				if(Ext.isEmpty(results)) results = {success:false};
				if(Ext.isEmpty(results.success)) results.success = false;
				if(aCB) (aCB)(results.success);
			},
			failure : function(conn,response,options){
				if(aCB) (aCB)(false);
			}
		});
};

ag_extensions.auth.login = function(b,e){
	var self = this;
	var openid_url = Cookies.get('openid_url');
	var emptyText = 'http://openid.dbcls.jp/user/[username]';
	var openid_win = new Ext.Window({
		id:'bp3d-openid-login-window',
		layout:'fit',
		width:350,
		height:120,
		closeAction:'hide',
		plain: true,
		frame:true,
		modal: true,
		closable : false,
		resizable : false,
		title: 'Login',
		iconCls: 'openid-icon',
		items : {
			xtype : 'form',
			id:'bp3d-openid-login-form',
			frame:false,
			plain: true,
			border:false,
			bodyStyle :{'padding':'4px'},
			labelWidth : 45,
			defaultType: 'textfield',
			items : [{
				fieldLabel: 'OpenID',
				id:'bp3d-openid-login-url',
				cls: 'openid',
				name: 'openid_url',
				value : openid_url,
				emptyText : emptyText,
				anchor : '100%',
				allowBlank:false,
				selectOnFocus:true,
				autoCreate : true,
				autoEl : {
					tag: "input",
					type: "text",
					size: "20",
					autocomplete: "on",
					name: "openid_url"
				},
				listeners: {
					specialkey: function(field, e){
						if(e.getKey() != e.ENTER) return;
						var button = Ext.getCmp('bp3d-openid-login-button');
						if(button) button.fireEvent('click',button,e);
					}
				}
			},{
				xtype : 'label',
				text : '( For example: ' + emptyText + ' )'
			}]
		},
		buttonAlign : 'center',
		defaultButton : 'bp3d-openid-login-button',
		buttons: [{
			text:'Login',
			id:'bp3d-openid-login-button',
			listeners: {
				click: function(b,e){
					var form = Ext.getCmp('bp3d-openid-login-form');
					if(form && form.getForm().isValid()){
						b.disable();
						var openid_url = Ext.getCmp('bp3d-openid-login-url').getValue();

						self.checkAuth(openid_url,function(sessionID){
							if(sessionID){
								Cookies.set('openid_url',openid_url);
								var search = Ext.urlDecode(location.search.substr(1),true);
								search.openid_url = openid_url
								search.session = sessionID;
								location.search = Ext.urlEncode(search);
							}else{
								b.enable();
							}
						});
					}
				}
			}
		},{
			text: 'Cancel',
			handler: function(){
				openid_win.close();
			}
		}]
	});
	openid_win.show();
};

//Ext.EventManager.on(window,'load',function(){
Ext.onReady(function(){
	if(Ext.isEmpty(window.gAuthTBButton)) return;
	ag_extensions.auth._init();
});
