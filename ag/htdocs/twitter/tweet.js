Ext.onReady(function() {
	Ext.create('Ext.container.Viewport', {
		layout: 'fit',
		items: [{
			listeners: {
				afterrender: function(comp,eOpts){
					comp.setLoading(true);
					goto_twitter();
				},
				show: function(comp,eOpts){
				}
			}
		}]
	});

});

function goto_twitter(){
	var tweet_url = 'https://twitter.com/intent/tweet?';
	var o = Ext.Object.fromQueryString(window.location.search.substr(1),true) || {};
	o.url = o.url || getLinkURL();
	o.url = o.url || 'http://lifesciencedb.jp/bp3d/';

	var s = []

	s.push('hashtags='+encodeURIComponent(o.hashtags?o.hashtags:'bp3d'));
	s.push('original_referer='+encodeURIComponent(document.referrer));
	s.push('text='+encodeURIComponent(o.text?o.text:'BodyParts3D'));
	s.push('tw_p='+encodeURIComponent('tweetbutton'));

	var window_title = 'TWeet'
	Ext.Ajax.request({
		url     : '../get-convert-url.cgi',
		method  : 'POST',
		params  : Ext.urlEncode({url:o.url}),
		success : function(conn,response,options){
			try{var results = Ext.decode(conn.responseText);}catch(e){}
			if(Ext.isEmpty(results) || Ext.isEmpty(results.status_code) || results.status_code!=200){
				var msg = 'URL translation errors';
				if(results && results.status_code) msg += ' [ '+ results.status_code +' ]';
				Ext.MessageBox.show({
					title   : window_title,
					msg     : msg,
					buttons : Ext.MessageBox.OK,
					icon    : Ext.MessageBox.ERROR
				});
				return;
			}
			if(Ext.isEmpty(results.data)){
				var msg = 'URL translation errors';
				if(results && results.status_code) msg += ' [ no data ]';
				Ext.MessageBox.show({
					title   : window_title,
					msg     : msg,
					buttons : Ext.MessageBox.OK,
					icon    : Ext.MessageBox.ERROR
				});
				return;
			}

			delete o.url;
			if(!Ext.isEmpty(results.data.url)){//shortURLに変換
				o.url = results.data.url;
			}
			if(!Ext.isEmpty(results.data.expand)){//longURLに変換
				if(Ext.isArray(results.data.expand)){
					o.url = results.data.expand[0].long_url;
				}else{
					o.url = results.data.expand.long_url;
				}
			}
			s.push('url='+encodeURIComponent(o.url?o.url:'http://lifesciencedb.jp/bp3d/'));
			open_url = tweet_url+s.join('&');
			window.location.href = open_url;
		},
		failure : function(conn,response,options){
			anatomo_link_window.loadMask.hide();
			Ext.MessageBox.show({
				title   : window_title,
				msg     : 'URL translation errors',
				buttons : Ext.MessageBox.OK,
				icon    : Ext.MessageBox.ERROR
			});
		}
	});
}
