window.ag_extensions = window.ag_extensions || {};
ag_extensions.dataDrop = ag_extensions.dataDrop || {};

ag_extensions.dataDrop.init = function(){
		//FMASearchからのDrag&Dropに対応
		var el = Ext.getBody();
		el.on({
			dragenter: function(event){
				if(event && event.stopEvent) event.stopEvent();
				return false;
			},
			dragover: function(event){
				if(event && event.stopEvent) event.stopEvent();
				return false;
			},
			drop: function(event){
				if(event && event.stopEvent) event.stopEvent();
				var dataTransfer;
				if(Ext.isObject(event)){
					if(event.browserEvent && event.browserEvent.dataTransfer){
						dataTransfer = event.browserEvent.dataTransfer;
					}else if(event.dataTransfer){
						dataTransfer = event.dataTransfer;
					}
				}
				var dropData = null;
				if(dataTransfer && dataTransfer.getData){
					dropData = dataTransfer.getData('text/plain');
				}
				if(Ext.isEmpty(dropData)) return;
				if(Ext.isString(dropData)){
					if(dropData.match(/^[\[\{].+[\]\}]$/)){
						try{dropData = Ext.decode(dropData);}catch(e){}
					}
				}else{
					return;
				}
				try{
					if(Ext.isArray(dropData) || Ext.isObject(dropData)){
						var params = {};
						try{
							params.version = Ext.getCmp('bp3d-version-combo').getValue();
						}catch(e){}
						if(Ext.isEmpty(params.version)) params.version=init_bp3d_version;

						try{
							var bp3d_version_combo = Ext.getCmp('bp3d-version-combo');
							var bp3d_version_store = bp3d_version_combo.getStore();
							var bp3d_version_idx = bp3d_version_store.find('tgi_version',new RegExp('^'+bp3d_version_combo.getValue()+'$'));
							var bp3d_version_rec;
							var bp3d_version_disp_value;
							if(bp3d_version_idx>=0) bp3d_version_rec = bp3d_version_store.getAt(bp3d_version_idx);
							if(bp3d_version_rec){
								params.md_id = bp3d_version_rec.get('md_id');
								params.mv_id = bp3d_version_rec.get('mv_id');
								params.mr_id = bp3d_version_rec.get('mr_id');
							}
						}catch(e){
							if(window.console) console.error(e);
						}
						try{
							var bp3d_tree_combo = Ext.getCmp('bp3d-tree-type-combo');
							var bp3d_tree_store = bp3d_tree_combo.getStore();
							var bp3d_tree_idx = bp3d_tree_store.find('t_type',new RegExp('^'+bp3d_tree_combo.getValue()+'$'));
							var bp3d_tree_rec;
							var bp3d_tree_disp_value;
							if(bp3d_tree_idx>=0) bp3d_tree_rec = bp3d_tree_store.getAt(bp3d_tree_idx);
							if(bp3d_tree_rec){
								params.bul_id = bp3d_tree_rec.get('bul_id');
								params.ci_id = bp3d_tree_rec.get('ci_id');
								params.cb_id = bp3d_tree_rec.get('cb_id');
							}
						}catch(e){
							if(window.console) console.error(e);
						}
//						console.log(params);

						var newRecord = Ext.data.Record.create(bp3d_parts_store_fields);
						var prm_record = ag_param_store.getAt(0);
						var data2record = function(data){
							var addrec = new newRecord(Ext.apply({},{
								'exclude'       : false,
								'color'         : '#'+prm_record.data.color_rgb,
								'value'         : '',
								'zoom'          : false,
								'exclude'       : false,
								'opacity'       : '1.0',
								'representation': 'surface',
								'point'         : false
							},params));

							addrec.beginEdit();
							for(var fcnt=0;fcnt<addrec.fields.items.length;fcnt++){
								var fname = addrec.fields.items[fcnt].name;
								var fdefaultValue = addrec.fields.items[fcnt].defaultValue;
								if(Ext.isEmpty(addrec.get(fname))) addrec.set(fname,fdefaultValue);
							}

							if(data.id) addrec.set('f_id',data.id);
							if(data.name) addrec.set('name_e',data.name);
							if(data.color) addrec.set('color',data.color);
//							console.log(addrec.data.f_id,addrec.data.color);

							addrec.commit(false);
							addrec.endEdit();
							return addrec;
						};

						var partslist = Ext.getCmp('control-tab-partslist-panel');
						var store = partslist.getStore();

						var addrecs = [];
						var adddatas = {};

						var find_property = 'f_id';
						if(Ext.isArray(dropData)){
							Ext.each(dropData,function(data){
								var record = data2record(data);
								var idx = store.find(find_property, record.get(find_property), 0, false, true);
								if(idx<0) addrecs.push(record);
							});
						}
						else if(Ext.isObject(dropData)){
							var record = data2record(dropData);
							var idx = store.find(find_property, record.get(find_property), 0, false, true);
							if(idx<0) addrecs.push(record);
						}
						if(addrecs.length){
							Ext.each(addrecs,function(r){
								adddatas[r.get('f_id')]= Ext.apply({},r.data);
							});

							store.add(addrecs);
							clearConvertIdList(addrecs);
							getConvertIdList(addrecs,store,function(success){
								if(success){
									Ext.each(addrecs,function(addrec){
										var f_id = addrec.get('f_id');
										if(adddatas[f_id] && adddatas[f_id].color != addrec.get('color')){
											addrec.beginEdit();
											addrec.set('color',adddatas[f_id].color);
											addrec.commit(false);
											addrec.endEdit();
										}
									});
								}
							});
						}


					}

				}catch(e){
					console.error(e);
				}



			}
		});
};

Ext.onReady(function(){
	ag_extensions.dataDrop.init();
});

if(Ext.isEmpty(Ext.isObject)){
	var toString = Object.prototype.toString;
	Ext.isObject = (toString.call(null) === '[object Object]') ?
		function(value) {
			return value !== null && value !== undefined && toString.call(value) === '[object Object]' && value.ownerDocument === undefined;
		} :
		function(value) {
			return toString.call(value) === '[object Object]';
		}
	;
}
if(Ext.isEmpty(Ext.isString)){
	Ext.isString = function(value) {
		return typeof value === 'string';
	};
}
