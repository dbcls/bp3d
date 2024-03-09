
//システム共通のパレット色（※英字は大文字で定義すること）
//var palette_color = [
//	"000000", "993300", "333300", "003300", "003366", "000080",
//	"333399", "333333", "800000", "FF6600", "808000", "008000",
//	"008080", "0000FF", "666699", "808080", "FF0000", "FF9900",
//	"99CC00", "339966", "33CCCC", "3366FF", "800080", "969696",
//	"FF00FF", "FFCC00", "FFFF00", "00FF00", "00FFFF", "00CCFF",
//	"993366", "C0C0C0", "FF99CC", "FFCC99", "F0D2A0", "FFFF99",
//	"CCFFCC", "CCFFFF", "99CCFF", "CC99FF", "FFFFFF"
//];
var palette_color2 = [
	"000000", "993300", "333300", "003300", "003366", "000080",
	"333399", "333333", "800000", "FF6600", "808000", "008000",
	"008080", "0000FF", "666699", "808080", "FF0000", "FF9900",
	"99CC00", "339966", "33CCCC", "3366FF", "800080", "969696",
	"FF00FF", "FFCC00", "FFFF00", "00FF00", "00FFFF", "00CCFF",
	"993366", "C0C0C0", "FF99CC", "FFCC99", "F0D2A0", "FFFF99",
	"CCFFCC", "CCFFFF", "99CCFF", "CC99FF", "FFFFFF"
];

var palette_color = [
"FFFFFF","FFCCCC","FFE6CC","FFFFCC","E6FFCC","CCFFCC","CCFFE6","CCFFFF","CCE6FF","CCCCFF","E6CCFF","FFCCFF","FFCCE6",
"E6E6E6","FF9999","FFCC99","FFFF99","CCFF99","99FF99","99FFCC","99FFFF","99CCFF","9999FF","CC99FF","FF99FF","FF99CC",
"CCCCCC","FF6666","FFB366","FFFF66","B3FF66","66FF66","66FFB3","66FFFF","66B3FF","6666FF","B366FF","FF66FF","FF66B3",
"B3B3B3","FF3333","FF9933","FFFF33","99FF33","33FF33","33FF99","33FFFF","3399FF","3333FF","9933FF","FF33FF","FF3399",
"999999","FF0000","FF8000","FFFF00","80FF00","00FF00","00FF80","00FFFF","0080FF","0000FF","8000FF","FF00FF","FF0080",
"808080","CC0000","CC6600","CCCC00","66CC00","00CC00","00CC66","00CCCC","0066CC","0000CC","6600CC","CC00CC","CC0066",
"666666","990000","994D00","999900","4D9900","009900","00994D","009999","004D99","000099","4D0099","990099","99004D",
"4D4D4D","660000","663300","666600","336600","006600","006633","006666","003366","000066","330066","660066","660033",
"333333","330000","331A00","333300","1A3300","003300","00331A","003333","001A33","000033","1A0033","330033","33001A",
"000000","F0D2A0"
];

//Ext.onReady(function(){
//	Ext.Ajax.on({
//		beforerequest: function(conn,options){
//			console.log("Ext.Ajax.beforerequest():"+options.url);
////			console.log(conn);
////			console.log(options);
//		},
//		requestcomplete: function(conn,response,options){
//			console.log("Ext.Ajax.requestcomplete():"+options.url);
////			console.log(conn);
////			console.log(response);
////			console.log(options);
//		},
//		requestexception: function(conn,response,options){
//			console.log("Ext.Ajax.requestexception():"+options.url);
//			console.log(conn);
//			console.log(response);
//			console.log(options);
//		}
//	});
//});

Ext.EventManager.on(window,'load',function(){
//	Ext.state.Manager.setProvider(new Ext.state.CookieProvider()); //ソート順とかをCookieに登録する為に必要らしい

	Ext.QuickTips.init();
	ag_init();
	if(Ext.isEmpty(gParams.tp_md)){
		try{anatomography_render();}catch(e){_dump("anatomography_render():"+e);}
//		try{
			ag_ann_init();
//		}catch(e){
//			if(window.console) console.log(e);
//			_dump("ag_ann_init():"+e);
//		}
		try{anatomography_init();}catch(e){_dump("anatomography_init():"+e);}
	}

});
