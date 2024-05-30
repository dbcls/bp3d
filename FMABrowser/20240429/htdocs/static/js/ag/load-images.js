// /opt/services/ag/FMABrowser/20240407/htdocs/load-images.cgiより自動生成
var AgImages = {
	lis : []
};
Ext.onReady(function(){
	if(!Ext.isEmpty(AgImages.lis)){
		var img = new Image();
		img.onload = img.onabort = img.onerror = function(){
			if(Ext.isEmpty(AgImages.lis)){
				img = undefined;
				return;
			}
			img.src = AgImages.lis.shift();
		};
		img.src = AgImages.lis.shift();
	}
});
