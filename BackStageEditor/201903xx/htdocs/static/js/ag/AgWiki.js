var AgWiki = {
	_iframe : null,
	_hashRenderStr : null,
	_url : "http://221.186.138.155/project/anatomo_wiki/en/index.php",
	_hash : "#fma_thumbnail=rotate",
	_id : "ag-wiki",
	_b_id : null,
	_init : false,

	init : function(param){
		AgWiki._dump("AgWiki.init()");
		AgWiki._param = param || {};
		if(AgWiki._param.dom){
			AgWiki._iframe = $('<iframe id="'+AgWiki._id+'" width="100%" height="100%" frameborder=0 src="'+AgWiki._url+'">').appendTo($(AgWiki._param.dom)).get(0);
		}
		AgWiki._init = true;
	},

	load : function(b_id,tree){
		if(!AgWiki._init) return;
		AgWiki._dump("AgWiki.load()");
		if(!tree) tree = 'bp3d';
//		if(tree=='bp3d'){
//			tree = 'conventional';
//		}else if(tree=='isa'){
//			tree = 'is_a';
//		}else if(tree=='partof'){
//			tree = 'part_of';
//		}
		if(AgWiki._b_id != b_id){
			$(AgWiki._iframe).attr('src',AgWiki._url+'/'+b_id+AgWiki._hash+'&thumbnail_tree='+tree).hide().one('load',function(){$(this).fadeIn(300)});
			AgWiki._b_id = b_id;
		}
		AgWiki.unload_task.cancel();
		if(AgWiki._param.panel) AgWiki._param.panel.expand();
		Ext.getCmp('ag-parts-fma-obj-link-button').setDisabled(false);
	},

	unload : function(){
		if(!AgWiki._init) return;
		AgWiki._dump("AgWiki.unload()");
		AgWiki.unload_task.delay(50);
	},

	unload_task : new Ext.util.DelayedTask(function(){
		if(!AgWiki._init) return;
		Ext.getCmp('ag-parts-fma-obj-link-button').setDisabled(true);
		AgWiki._param.panel.collapse(Ext.Component.DIRECTION_BOTTOM);
	}),

	_dump : function(aStr){
//		if(window.dump) window.dump("AgWiki.js:"+aStr+"\n");
//		try{if(console && console.log) console.log("AgWiki.js:"+aStr);}catch(e){}
	}

};
/*
http://192.168.1.237/anatomo_wiki/en/api.php?action=query&prop=revisions&format=jsonfm&titles=FMA20394&rvprop=timestamp|content

http://192.168.1.237/anatomo_wiki/en/api.php?action=query&list=allpages&apprefix=FMA&format=jsonfm&apfilterredir=nonredirects
http://192.168.1.237/anatomo_wiki/en/api.php?action=query&list=allpages&apprefix=FMA&format=jsonfm&apfrom=FMA10000/partof/brother




http://192.168.1.237/anatomo_wiki/en/api.php?action=login&lgname=gogo&lgpassword=togo

http://192.168.1.237/anatomo_wiki/en/api.php?action=parse&title=FMA20943&format=jsonfm&text={{Project:Sandbox}}


http://192.168.1.237/anatomo_wiki/en/api.php?action=parse&title=FMA20943&format=jsonfm&text={{Template:BodyParts3D\n|id=FMA20394\n|taid=\n|name_e=Human body\n|name_j=\u4eba\u4f53\n|name_k=\u3058\u3093\u305f\u3044\n|name_l=\n|organ_systems_e=others\n|organ_systems_j=\n|synonym_e=\n|synonym_j=\n|universal_id=FMA20394\n|lsdb_synonym_e=\n|lsdb_synonym_l=\n|lsdb_synonym_j=\n|lsdb_synonym_k=\n|lsdb_relative_e=\n|lsdb_relative_l=\n|lsdb_relative_j=\n|lsdb_relative_k=\n|lsdb_auto_e=\n|lsdb_auto_l=\n|lsdb_auto_j=\n|lsdb_auto_k=\n|thumbnail_rotate=\n|thumbnail_front=\n|thumbnail_left=\n|thumbnail_back=\n|thumbnail_right=\n}}\n----\n{{Template:BodyParts3D\/partof|FMA20394}}\n{{Template:BodyParts3D\/is a|FMA20394}}
*/
