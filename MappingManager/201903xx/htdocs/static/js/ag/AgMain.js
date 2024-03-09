var EventSource = window.EventSource || window.MozEventSource;
var useEventSource = false;
//if(EventSource) useEventSource = true;

var openAgRender = function(urlHashStr){
	var win = window.open("AgRender.cgi#"+urlHashStr,"_blank","width=800,height=600,dependent=yes,directories=no,menubar=no,resizable=yes,status=no,toolbar=no");
	$(win).bind('load',function(){
		var $win = this.$(this);
/*
		$win.bind('showLoading',function(){
			console.log('showLoading');
		});
		$win.bind('hideLoading',function(){
			console.log('hideLoading');
		});

		$win.bind('changeLongitudeDegree',function(){
			console.log('changeLongitudeDegree');
		});
		$win.bind('changeLatitudeDegree',function(){
			console.log('changeLatitudeDegree');
		});
		$win.bind('changeZoom',function(){
			console.log('changeZoom');
		});
		$win.bind('changeCameraNear',function(){
			console.log('changeCameraNear');
		});
		$win.bind('changeCameraFar',function(){
			console.log('changeCameraFar');
		});
		$win.bind('dropObject',function(){
			console.log('dropObject');
		});
		$win.bind('pickObject',function(){
			console.log('pickObject');
		});
		$win.bind('pinObject',function(){
			console.log('pinObject');
		});
		$win.bind('addPalletParts',function(){
			console.log('addPalletParts');
		});
		$win.bind('hideParts',function(){
			console.log('hideParts');
		});
		$win.bind('hashchange',function(){
			console.log('hashchange');
		});
*/
		var createLocaleHashStrTask = new Ext.util.DelayedTask();
		var createLocaleHashStrFunc = function(){
			$win.unbind('createLocaleHashStr');
//			console.log(arguments);
			var hash;
			try{
				hash = Ext.decode(arguments[arguments.length-1].hash);
			}catch(e){
			}
			if(Ext.isEmpty(hash)) return;

			Ext.each(hash.ExtensionPartGroup,function(PartGroup,i,a){
				Ext.each(PartGroup.PartGroupItems,function(item,i,a){
					item.UseForBoundingBoxFlag = true;
				});
			});
			var hashStr = Ext.encode(hash);
			$win.trigger('changeLocaleHashStr',[hashStr]);
		};
		$win.bind('createLocaleHashStr',function(){
//			console.log('createLocaleHashStr');
			createLocaleHashStrTask.delay(250,createLocaleHashStrFunc,this,arguments);
		});

	});



	return false;
};

var AgApp = function(config){
	var self = this;
	self._config = config || {};

	self.hidden_paenl = {
		'pin': true
	};


	self.DEF_LAYOUT_WINDOW = 'window';
	self.DEF_LAYOUT = self.DEF_LAYOUT_WINDOW;

	self.glb_localdb_init = false;

	self.DEF_LOCALDB_HASH_KEY = AgDef.LOCALDB_PREFIX+'bp3d-pallet-parts';
	self.DEF_LOCALDB_TREE_INFO = AgDef.LOCALDB_PREFIX+'bp3d-tree-info';
	self.DEF_LOCALDB_FOLDER_INFO = AgDef.LOCALDB_PREFIX+'art-folder-info';

	self.DEF_LOCALDB_PROVIDER_PREFIX = AgDef.LOCALDB_PREFIX+'bp3d-mng-';

	self.event_namespace = '.main';
	self.AgRender = new AgRender({namespace: self.event_namespace.substring(1)});
	self.AgLocalStorage = new AgLocalStorage();

//	self.AgLocalStorage.remove(self.DEF_LOCALDB_HASH_KEY);

	self.FORMAT_FULL_FLOAT_NUMBER = '0,0.0000';
	self.FORMAT_FLOAT_NUMBER = '0,0.00';
	self.FORMAT_INT_NUMBER = '0,0';
	self.FORMAT_RATE_NUMBER = '0.00';
	self.FORMAT_DATE = 'Y/m/d';
	self.FORMAT_TIME = 'H:i:s';
	self.FORMAT_TIME_M = 'H:i:s.u';
	self.FORMAT_DATE_TIME = self.FORMAT_DATE+' '+self.FORMAT_TIME;
	self.FORMAT_DATE_TIME_M = self.FORMAT_DATE+' '+self.FORMAT_TIME_M;
	self.FORMAT_ID_NUMBER = '0';

	self.PALLET_WINDOW_HIDDEN = false;
	self.PALLET_PANEL_HIDDEN = false;

	self.ART_TIMESTAMP_FORMAT = USE_OBJ_TIMESTAMP_COMPARISON_UNIT===USE_OBJ_TIMESTAMP_COMPARISON_UNIT_DATE ? self.FORMAT_DATE : self.FORMAT_DATE_TIME;
	self.ART_TIMESTAMP_WIDTH = USE_OBJ_TIMESTAMP_COMPARISON_UNIT===USE_OBJ_TIMESTAMP_COMPARISON_UNIT_DATE ? 67 : 112;

//	self.USE_CLICK_TO_GROUOP_SELECTED = false;	//フォルダクリック時にグループを自動的にチェック（選択状態にする）。その後、オブジェクトをリストに表示する

//	self.USE_FMA_OBJ_LINK = true;	//FMA対応変更モード
	self.USE_FMA_OBJ_LINK = false;	//FMA対応変更モード

//	self.USE_FMA_MAPPING = true;	//FMAマッピング
	self.USE_FMA_MAPPING = false;	//FMAマッピング

//	self.USE_CONFLICT_LIST = true;	//conflictリスト
	self.USE_CONFLICT_LIST = false;	//conflictリスト
	self.USE_CONFLICT_LIST_TYPE = 'window';	//conflictリスト

//	self.TITLE_UPLOAD_FOLDER = 'semantic group of obj';
//	self.TITLE_UPLOAD_GROUP = 'physical group of obj (small modification)';
//	self.TITLE_UPLOAD_OBJECT = 'specified obj';
	self.TITLE_UPLOAD_FOLDER = 'Semantic category of obj lineage';
	self.TITLE_UPLOAD_GROUP = 'correction lineage';
	self.TITLE_UPLOAD_OBJECT = 'obj files';

	self.TOOLTIP_FMAID_NOT_SUPPORTED = 'FMAID not supported';

	self.MAPPING_MNG_ID = 'mapping-mng';

	self.MAINTAIN_UPLOAD_DIRECTORY_STRUCTURE_HIDDEN = false;
	self.MAINTAIN_UPLOAD_DIRECTORY_STRUCTURE_CHECKED = (!self.MAINTAIN_UPLOAD_DIRECTORY_STRUCTURE_HIDDEN ? MAINTAIN_UPLOAD_DIRECTORY_STRUCTURE : false);

	try{self.glb_hashStr = (window.parent ? window.parent : window).location.hash.substr(1);}catch(e){console.error(e);}
	if(Ext.isEmpty(self.glb_hashStr)){
		self.glb_hashStr = self.AgRender.getLocationHash();
	}else{
		self.AgLocalStorage.remove(self.DEF_LOCALDB_HASH_KEY);
		self.glb_localdb_init = true;
	}

	self.groupname2grouppath = {};
	self.bp3d_search_grid_renderer_params = {
		searchValue : null,
		matchCls : 'x-livesearch-match',
		caseSensitive : false,
		searchRegExp : null
	};

	self.panelWidth = Math.floor(window.screen.width/4);
	self.eastPanelWidth = Math.floor(window.screen.width/3);
	self.panelHeight = Math.floor(window.screen.height/3);

	self.init();

};
window.AgApp.prototype = Object.create(AG.MathUtil.prototype);
window.AgApp.prototype.constructor = AgApp;

window.AgApp.prototype.getLocaleHashStr = function(){
	var self = this;

	var hashStr = self.glb_hashStr;
	return hashStr;
};
window.AgApp.prototype.getLocaleHashObj = function(hashStr){
	var self = this;

	hashStr = hashStr || self.getLocaleHashStr();
	return AgURLParser.parseURL(hashStr);
};

window.AgApp.prototype.updateUIValue = function(){
	var self = this;

	var jsonObj = self.getLocaleHashObj();
	self.setHash2Legend(jsonObj);
	self.setHash2Pin(jsonObj);
	self.setHash2Grid(jsonObj);
	self.setHash2BackgroundColor(jsonObj);
	self.setHash2Common(jsonObj);
};

window.AgApp.prototype.setHash2Legend = function(jsonObj){
	var self = this;

	if(Ext.isEmpty(jsonObj) || Ext.isEmpty(jsonObj.Legend)) return;

	var titleCmp = Ext.getCmp('legend-title-textfield');
	var legendCmp = Ext.getCmp('legend-legend-textareafield');
	var authorCmp = Ext.getCmp('legend-author-textfield');
	var drawCmp = Ext.getCmp('legend-draw-checkbox');

	var Legend = jsonObj.Legend;
	var value = '';

	if(titleCmp){
		titleCmp.suspendEvents(false);
		value = '';
		if(!Ext.isEmpty(Legend.LegendTitle)) value = Legend.LegendTitle;
		if(titleCmp.getValue()!=value) titleCmp.setValue(value);
		titleCmp.resumeEvents();
	}
	if(legendCmp){
		legendCmp.suspendEvents(false);
		value = '';
		if(!Ext.isEmpty(Legend.Legend)) value = Legend.Legend;
		if(legendCmp.getValue()!=value) legendCmp.setValue(value);
		legendCmp.resumeEvents();
	}
	if(authorCmp){
		authorCmp.suspendEvents(false);
		value = '';
		if(!Ext.isEmpty(Legend.LegendAuthor)) value = Legend.LegendAuthor;
		if(authorCmp.getValue()!=value) authorCmp.setValue(value);
		authorCmp.resumeEvents();
	}
	if(drawCmp){
		drawCmp.suspendEvents(false);
		value = false;
		if(!Ext.isEmpty(Legend.DrawLegendFlag)) value = Legend.DrawLegendFlag;
		if(drawCmp.getValue()!=value) drawCmp.setValue(value);
		drawCmp.resumeEvents();
	}
};

window.AgApp.prototype.setHash2Pin = function(jsonObj){
	var self = this;

	if(Ext.isEmpty(jsonObj) || Ext.isEmpty(jsonObj.Pin)) return;

	var PinDescriptionDrawFlag = false;
	var PinIndicationLineDrawFlag = 0;
	var PinShape = null;
	if(!Ext.isEmpty(jsonObj.Common) && Ext.isBoolean(jsonObj.Common.PinDescriptionDrawFlag)) PinDescriptionDrawFlag = jsonObj.Common.PinDescriptionDrawFlag;
	if(!Ext.isEmpty(jsonObj.Common) && Ext.isNumber(jsonObj.Common.PinIndicationLineDrawFlag)) PinIndicationLineDrawFlag = jsonObj.Common.PinIndicationLineDrawFlag;

	var store = Ext.data.StoreManager.lookup('pinStore');
	var gridCmp = Ext.getCmp('pin-panel');
	var descriptionCmp = Ext.getCmp('pin-description-checkbox');
	var lineCmp = Ext.getCmp('pin-line-combobox');
	var shapeCmp = Ext.getCmp('pin-shape-combobox');

	var Pin = jsonObj.Pin;

	store.suspendEvents(false);
	store.removeAll(true);
	var records = [];
	Ext.each(Pin,function(pin,i,a){
		var record = Ext.create(Ext.getClassName(store.model),{});
		var modifiedFieldNames = [];

		record.beginEdit();
		for(var key in pin){
			if(record.data[key]===undefined) continue;
			if(key.indexOf('Color')>=0 && pin[key].indexOf('#')!=0){
				record.set(key,'#'+pin[key]);
			}else{
				record.set(key,pin[key]);
			}
			modifiedFieldNames.push(key);
		}
		if(modifiedFieldNames.length>0){
			record.commit(false);
			record.endEdit(false,modifiedFieldNames);
			records.push(record);

			if(Ext.isEmpty(PinShape)) PinShape = record.data.PinShape;
		}else{
			record.cancelEdit();
		}
	});
	if(records.length>0) store.add(records);

	store.resumeEvents();

	if(Ext.isEmpty(PinShape)) PinShape = 'CIRCLE';

	if(descriptionCmp){
		descriptionCmp.suspendEvents(false);
		if(descriptionCmp.getValue()!=PinDescriptionDrawFlag) descriptionCmp.setValue(PinDescriptionDrawFlag);
		descriptionCmp.resumeEvents();
	}
	if(lineCmp){
		lineCmp.suspendEvents(false);
		value = '';
		if(lineCmp.getValue()!=PinIndicationLineDrawFlag) lineCmp.setValue(PinIndicationLineDrawFlag);
		lineCmp.setDisabled(!PinDescriptionDrawFlag);
		lineCmp.resumeEvents();
	}
	if(shapeCmp){
		shapeCmp.suspendEvents(false);
		if(shapeCmp.getValue()!=PinShape) shapeCmp.setValue(PinShape);
		shapeCmp.resumeEvents();
	}

	if(gridCmp) gridCmp.getView().refresh();
};

window.AgApp.prototype.setHash2Grid = function(jsonObj){
	var self = this;

	if(Ext.isEmpty(jsonObj) || Ext.isEmpty(jsonObj.Window)) return;

	var gridCmp = Ext.getCmp('options-grid');
	var spacingCmp = Ext.getCmp('options-grid-spacing');
	var colorCmp = Ext.getCmp('options-grid-color');

	var Window = jsonObj.Window;

	if(gridCmp){
		gridCmp.suspendEvents(false);
		if(Ext.isBoolean(Window.GridFlag) && gridCmp.checked != Window.GridFlag){
//			console.log("setHash2Grid():GridFlag=["+gridCmp.checked+"]->["+Window.GridFlag+"]");
			gridCmp.checked = Window.GridFlag;
		}
		gridCmp.resumeEvents();
	}
	if(spacingCmp){
		spacingCmp.suspendEvents(false);
		if(!Ext.isEmpty(Window.GridTickInterval) && Ext.isNumber(Window.GridTickInterval) && spacingCmp.getValue()!=Window.GridTickInterval){
//			console.log("setHash2Grid():GridTickInterval=["+spacingCmp.getValue()+"]->["+Window.GridTickInterval+"]");
			spacingCmp.setValue(Window.GridTickInterval);
		}
		spacingCmp.resumeEvents();
	}
	if(colorCmp){
		colorCmp.suspendEvents(false);
		try{
			if(!Ext.isEmpty(Window.GridColor) && Ext.isString(Window.GridColor) && Window.GridColor.length==6){
				var GridColor = Window.GridColor.toUpperCase();
				if(colorCmp.getValue() != GridColor){
//					console.log("setHash2Grid():GridColor=["+colorCmp.getValue()+"]->["+GridColor+"]");
					colorCmp.setValue(GridColor);
				}
			}
		}catch(e){
			console.error(e);
		}
		colorCmp.resumeEvents();
	}
};

window.AgApp.prototype.setHash2Common = function(jsonObj){
	var self = this;

	if(Ext.isEmpty(jsonObj) || Ext.isEmpty(jsonObj.Common)) return;

	var colorheatmapCmp = Ext.getCmp('options-colorheatmap');
	var maxCmp = Ext.getCmp('options-colorheatmap-max');
	var minCmp = Ext.getCmp('options-colorheatmap-min');

	var Common = jsonObj.Common;

//	console.log("setHash2Common()");
//	console.log(Common);

	var Model = DEF_MODEL;
	var ConceptInfo = DEF_CONCEPT_INFO;
	var ConceptBuild = DEF_CONCEPT_BUILD;

	var updModel = false;
	var updVersion = false;
	var updTree = false;



	if(colorheatmapCmp){
		colorheatmapCmp.suspendEvents(false);
		try{
			if(Ext.isBoolean(Common.ColorbarFlag) && colorheatmapCmp.checked != Common.ColorbarFlag){
//				console.log("setHash2Common():ColorbarFlag=["+colorheatmapCmp.checked+"]->["+Common.ColorbarFlag+"]");
				colorheatmapCmp.checked = Common.ColorbarFlag;
			}
			var pallet_grid = Ext.getCmp('pallet-grid');
			Ext.each(pallet_grid.getView().getGridColumns(),function(c,i,a){
				if(c.dataIndex!=='scalar') return true;
				c.setVisible(colorheatmapCmp.checked);
				return false;
			});
		}catch(e){
			console.error(e);
		}
		colorheatmapCmp.resumeEvents();
	}
	if(maxCmp){
		maxCmp.suspendEvents(false);
		try{
			var ScalarMaximum = 65535;
			if(Ext.isNumber(Common.ScalarMaximum) && Common.ScalarMaximum < ScalarMaximum) ScalarMaximum = Common.ScalarMaximum;
			if(maxCmp.getValue() != ScalarMaximum){
//				console.log("setHash2Common():ScalarMaximum=["+maxCmp.getValue()+"]->["+ScalarMaximum+"]");
				maxCmp.setValue(ScalarMaximum);
			}
		}catch(e){
			console.error(e);
		}
		maxCmp.resumeEvents();
	}
	if(minCmp){
		minCmp.suspendEvents(false);
		try{
			var ScalarMinimum = -65535;
			if(Ext.isNumber(Common.ScalarMinimum) && Common.ScalarMinimum > ScalarMinimum) ScalarMinimum = Common.ScalarMinimum;
			if(minCmp.getValue() != ScalarMinimum){
//				console.log("setHash2Common():ScalarMinimum=["+minCmp.getValue()+"]->["+ScalarMinimum+"]");
				minCmp.setValue(ScalarMinimum);
			}
		}catch(e){
			console.error(e);
		}
		minCmp.resumeEvents();
	}

};

window.AgApp.prototype.setHash2BackgroundColor = function(jsonObj){
	var self = this;

	if(Ext.isEmpty(jsonObj) || Ext.isEmpty(jsonObj.Window)) return;

	var colorCmp = Ext.getCmp('options-background-color');
	var opacityCmp = Ext.getCmp('options-background-opacity');

	var Window = jsonObj.Window;

//	console.log("setHash2BackgroundColor()");
//	console.log(Window);

	if(colorCmp){
		colorCmp.suspendEvents(false);
		try{
			if(!Ext.isEmpty(Window.BackgroundColor) && Ext.isString(Window.BackgroundColor) && Window.GridColor.length==6){
				var BackgroundColor = Window.BackgroundColor.toUpperCase();
				if(colorCmp.getValue() != BackgroundColor){
//					console.log("setHash2BackgroundColor():BackgroundColor=["+colorCmp.getValue()+"]->["+BackgroundColor+"]");
					colorCmp.setValue(BackgroundColor);
				}
			}
		}catch(e){
			console.error(e);
		}
		colorCmp.resumeEvents();
	}
	if(opacityCmp){
		opacityCmp.suspendEvents(false);
		try{
			var BackgroundOpacity = false;
			if(!Ext.isEmpty(Window.BackgroundOpacity)){
				if(Ext.isNumber(Window.BackgroundOpacity) && Window.BackgroundOpacity>=0 && Window.BackgroundOpacity<=100) BackgroundOpacity = Window.BackgroundOpacity < 100 ? true : false;
				if(Ext.isBoolean(Window.BackgroundOpacity)) BackgroundOpacity = Window.BackgroundOpacity;
				if(opacityCmp.checked != BackgroundOpacity){
//					console.log("setHash2BackgroundColor():BackgroundOpacity=["+opacityCmp.checked+"]->["+BackgroundOpacity+"]");
					opacityCmp.checked = BackgroundOpacity;
				}
			}
		}catch(e){
			console.error(e);
		}
		opacityCmp.resumeEvents();
	}
};

window.AgApp.prototype.initBind = function(){
	var self = this;

	$(window).bind('agrender_hashchange'+self.event_namespace,function(e,hash){
		self.glb_hashStr = hash;
		self.updateUIValueTask.delay(250);
	});

	$(window).bind('agrender_load'+self.event_namespace,function(e,hash){
		self.glb_hashStr = hash;
		self.updateUIValue();
		self.AgRender.changeGuide(Ext.getCmp('options-guide').checked);
		self.AgRender.changeToolTip(Ext.getCmp('options-tooltip').checked);
		self.AgRender.changeStats(Ext.getCmp('options-stats').checked);
	});

	$(window).bind('agrender_showLoading'+self.event_namespace,function(){
		Ext.getCmp('render-panel').setLoading(false);
		Ext.getCmp('render-panel').getDockedComponent('render-panel-toolbar').setDisabled(true);
		try{
			var parts_panel = Ext.getCmp('parts-panel');
			parts_panel.body.mask();
			parts_panel.getHeader().setDisabled(true);
		}catch(e){}
	});

	$(window).bind('agrender_hideLoading'+self.event_namespace,function(){
		Ext.getCmp('render-panel').getDockedComponent('render-panel-toolbar').setDisabled(false);
		try{
			var parts_panel = Ext.getCmp('parts-panel');
			parts_panel.body.unmask();
			parts_panel.getHeader().setDisabled(false);
		}catch(e){}
	});

	$(window).bind('dropObject'+self.event_namespace,function(e,r){
		var palletPartsStore = Ext.data.StoreManager.lookup('palletPartsStore');
		var record = Ext.create(Ext.getClassName(palletPartsStore.model),{});
		var modifiedFieldNames = [];
		record.beginEdit();

		for(var key in r.data){
			if(record.get(key)==undefined) continue;
			if(record.get(key) != r.data[key]){
				record.set(key,r.data[key]);
				modifiedFieldNames.push(key);
			}
		}

		if(modifiedFieldNames.length>0){
			record.commit(false);
			record.endEdit(false,modifiedFieldNames);
			palletPartsStore.add(record);
		}else{
			record.cancelEdit();
		}
	});

	$(window).bind('pickObject'+self.event_namespace,function(e,o,route){

		var b = Ext.getCmp('pick-search-conditions-button');
		if(b) b.setDisabled(true);
		var b = Ext.getCmp('pick-search-more-button');
		if(b) b.setDisabled(true);

		var pallet_grid = Ext.getCmp('pallet-grid');
		var store = pallet_grid.getStore();
		var p = store.getProxy();
		p.extraParams = p.extraParams || {};
		delete p.extraParams._pickIndex;

		var pickSearchStore = Ext.data.StoreManager.lookup('pickSearchStore');

		if(Ext.isEmpty(o) || Ext.isEmpty(route)){
			pickSearchStore.removeAll();

			store.suspendEvents(false);
			store.each(function(record){
				if(record.get('target_record')){
					record.set('target_record', false);
					record.commit();
				}
			});
			store.resumeEvents();
			pallet_grid.getView().refresh();
			return false;
		}

		var selMode = pallet_grid.getSelectionModel();
		selMode.deselectAll();

		var eastTabPanel = Ext.getCmp('east-tab-panel');
		var pickSearchPanel = Ext.getCmp('pick-search-panel');

		if(pickSearchPanel && pickSearchPanel.rendered && !pickSearchPanel.isDisabled()){
			if(eastTabPanel.getActiveTab().id==pickSearchPanel.id){
				var p = pickSearchStore.getProxy();
				p.extraParams = p.extraParams || {};
				p.extraParams.art_point = Ext.encode({
					x : o.point.x,
					y : o.point.y,
					z : o.point.z
				});
				p.extraParams.voxel_range = 10;
				delete p.extraParams.art_id;
				if(!Ext.isEmpty(o.object.record.data.art_id)){
					p.extraParams.art_id = o.object.record.data.art_id;
				}else if(!Ext.isEmpty(o.object.record.data.c_art_id)){
					p.extraParams.art_id = o.object.record.data.c_art_id;
				}else{
					var store = pallet_grid.getStore();
					var idx = store.findBy(function(record,id){
						if(record.get('art_id')==o.object.record.data.art_id) return true;
					});
					if(idx>=0){
						var record = store.getAt(idx);
						p.extraParams.art_id = record.get('art_id');
					}
				}
				if(!Ext.isEmpty(p.extraParams.art_id)){
					var b = Ext.getCmp('pick-search-conditions-button');
					if(b) b.fireEvent('click',b);
				}
			}
		}

		//Pallet上のオブジェクトを選択
		var store = pallet_grid.getStore();
		var p = store.getProxy();
		p.extraParams = p.extraParams || {};
		delete p.extraParams._pickIndex;

		var idx = store.findBy(function(record,id){
			if(record.get('art_id')==o.object.record.data.art_id) return true;
		});
		var rtn;
		store.suspendEvents(false);
		store.each(function(record){
			record.set('target_record', false);
			record.commit();
		});
		if(idx>=0){
//			p.extraParams._pickIndex = idx;
			var record = store.getAt(idx);
			record.set('target_record', true);
			record.commit();

			var view = pallet_grid.getView();
			view.refresh();
			view.select(record);
			view.focusRow(idx);
			if(Ext.isEmpty(view.getNode(record))){
				var plugin = pallet_grid.getPlugin('bufferedrenderer');
				if(plugin) plugin.scrollTo(idx,true);
			}
			rtn = true;
		}else{
			rtn = 0x990000;
		}
		store.resumeEvents();
		return rtn;
	});

	$(window).bind('pinObject'+self.event_namespace,function(e,o){
		if(Ext.isEmpty(o)) return false;

		var panel = Ext.getCmp('east-tab-panel');
		var tabid = 'pin-panel';
		if(panel.getActiveTab().id!=tabid) panel.setActiveTab(Ext.getCmp(tabid));

		var PinUpVectorX=0,PinUpVectorY=0,PinUpVectorZ=1;
		var jsonObj = self.getLocaleHashObj();
		if(!Ext.isEmpty(jsonObj) && !Ext.isEmpty(jsonObj.Camera)){
			if(Ext.isNumber(jsonObj.Camera.CameraUpVectorX)) PinUpVectorX = jsonObj.Camera.CameraUpVectorX;
			if(Ext.isNumber(jsonObj.Camera.CameraUpVectorY)) PinUpVectorY = jsonObj.Camera.CameraUpVectorY;
			if(Ext.isNumber(jsonObj.Camera.CameraUpVectorZ)) PinUpVectorZ = jsonObj.Camera.CameraUpVectorZ;
		}
		var depth = Ext.getCmp('pin-depth-combobox').getValue();
		var store = Ext.data.StoreManager.lookup('pinStore');
		var count = store.getCount();

		var records = [];
		Ext.each(o,function(obj,i,a){
			if(depth<=i) return false;
//			console.log(i);

			var record = Ext.create(Ext.getClassName(store.model),{});
			var modifiedFieldNames = [];
			var skey,dkey;
			record.beginEdit();

			skey='cdi_name';
			if(!Ext.isEmpty(obj.object.record.data[skey])){
				dkey='PinOrganID';
				record.set(dkey,obj.object.record.data[skey]);
				modifiedFieldNames.push(dkey);
			}
			skey='name';
			if(!Ext.isEmpty(obj.object.record.data[skey])){
				dkey='PinOrganName';
				record.set(dkey,obj.object.record.data[skey]);
				modifiedFieldNames.push(dkey);
			}
			skey='group';
			if(!Ext.isEmpty(obj.object.record.data[skey])){
				dkey='PinOrganGroup';
				record.set(dkey,obj.object.record.data[skey]);
				modifiedFieldNames.push(dkey);
			}
			skey='grouppath';
			if(!Ext.isEmpty(obj.object.record.data[skey])){
				dkey='PinOrganGrouppath';
				record.set(dkey,obj.object.record.data[skey]);
				modifiedFieldNames.push(dkey);
			}
			skey='path';
			if(!Ext.isEmpty(obj.object.record.data[skey])){
				dkey='PinOrganPath';
				record.set(dkey,obj.object.record.data[skey]);
				modifiedFieldNames.push(dkey);
			}
			skey='version';
			if(!Ext.isEmpty(obj.object.record.data[skey])){
				dkey='PinOrganVersion';
				record.set(dkey,obj.object.record.data[skey]);
				modifiedFieldNames.push(dkey);

				dkey='PinOrganGroup';
				record.set(dkey,obj.object.record.data[skey]);
				modifiedFieldNames.push(dkey);
			}

			if(!Ext.isEmpty(obj.point)){
				Ext.each(['x','y','z'],function(skey,i,a){
					if(Ext.isNumber(obj.point[skey])){
						dkey='Pin'+skey.toUpperCase();
						record.set(dkey,obj.point[skey]);
						modifiedFieldNames.push(dkey);
					}
				});
			}
			if(!Ext.isEmpty(obj.face) && !Ext.isEmpty(obj.face.normal)){
				Ext.each(['x','y','z'],function(skey,i,a){
					if(Ext.isNumber(obj.face.normal[skey])){
						dkey='PinArrowVector'+skey.toUpperCase();
						record.set(dkey,obj.face.normal[skey]);
						modifiedFieldNames.push(dkey);
					}
				});
			}


			if(modifiedFieldNames.length>0){
				dkey='PinPartID';
				record.set(dkey,++count);
				modifiedFieldNames.push(dkey);

				dkey='PinUpVectorX';
				record.set(dkey,PinUpVectorX);
				modifiedFieldNames.push(dkey);
				dkey='PinUpVectorY';
				record.set(dkey,PinUpVectorY);
				modifiedFieldNames.push(dkey);
				dkey='PinUpVectorZ';
				record.set(dkey,PinUpVectorZ);
				modifiedFieldNames.push(dkey);

				record.commit(false);
				record.endEdit(false,modifiedFieldNames);
				records.push(record);

//				console.log(record.data);

			}else{
				record.cancelEdit();
			}


		});
		if(records.length){
			store.suspendEvents(true);
			store.add(records);
			store.resumeEvents();
		}
		return true;
	});

	$(window).bind('addPalletParts'+self.event_namespace,function(e,o){
		return true;	// 2013/09/05 何もしない

		var palletPartsStore = Ext.data.StoreManager.lookup('palletPartsStore');
		var record = Ext.create(Ext.getClassName(palletPartsStore.model),o);
		self.update_palletPartsStore([record],true,true);
		return true;
	});

	$(window).bind('hideParts'+self.event_namespace,function(e,o){
		return true;	// 2013/09/05 何もしない

		var palletPartsStore = Ext.data.StoreManager.lookup('palletPartsStore');
		var record = Ext.create(Ext.getClassName(palletPartsStore.model),o);
		var modifiedFieldNames = [];
		record.beginEdit();
		record.set('remove',true);
		modifiedFieldNames.push('remove');

		if(modifiedFieldNames.length>0){
			record.commit(false);
			record.endEdit(false,modifiedFieldNames);
		}else{
			record.cancelEdit();
		}

//		self.update_palletPartsStore([record],true,true);
		var recs = self.find_palletPartsStore([record]);
		if(!Ext.isEmpty(recs)){
//			console.log(recs);
		}
		return true;
	});

	$(window).bind('changeLongitudeDegree'+self.event_namespace,function(e,newValue,oldValue){
		var field = Ext.getCmp('rotateH');
		if(field.value!=newValue){
			field.suspendEvents(false);
			field.setValue(newValue);
			field.resumeEvents();
		}
		return true;
	});
	$(window).bind('changeLatitudeDegree'+self.event_namespace,function(e,newValue,oldValue){
		var field = Ext.getCmp('rotateV');
		if(field.value!=newValue){
			field.suspendEvents(false);
			field.setValue(newValue);
			field.resumeEvents();
		}
		return true;
	});
	$(window).bind('changeZoom'+self.event_namespace,function(e,newValue,oldValue){
		var field = Ext.getCmp('zoom-value-text');
		if(field.value!=newValue){
			field.suspendEvents(false);
			field.setValue(newValue);
			field.resumeEvents();
		}
		return true;
	});

	self.glbCameraNear = undefined;
	self.glbCameraFar = undefined;
	$(window).bind('changeCameraNear'+self.event_namespace,function(e,newValue,oldValue){
		var field = Ext.getCmp('camera-near');
		if(field.value!=newValue){
			field.suspendEvents(false);
			field.setValue(newValue);
			field.resumeEvents();
		}
		if(self.glbCameraNear===undefined) self.glbCameraNear = newValue;
		return true;
	});
	$(window).bind('changeCameraFar'+self.event_namespace,function(e,newValue,oldValue){
		var field = Ext.getCmp('camera-far');
		if(field.value!=newValue){
			field.suspendEvents(false);
			field.setValue(newValue);
			field.resumeEvents();
		}
		if(self.glbCameraFar===undefined) self.glbCameraFar = newValue;
		return true;
	});

};

window.AgApp.prototype.initDelayedTask = function(){
	var self = this;

	self.updateLocalDBPalletTask = new Ext.util.DelayedTask(function(){
		self.update_localdb_pallet();
	});

	self.updateUIValueTask = new Ext.util.DelayedTask(function(){
		self.updateUIValue();
	});

	self.setHashTask = new Ext.util.DelayedTask(function(render,store,records,callback){
//		console.log('self.setHashTask()');
//		return;

		var palletPartsStore = store || Ext.data.StoreManager.lookup('palletPartsStore');
		var pallet_records = records || palletPartsStore.getRange();

		var hashStr = null;
		if(render && Ext.isFunction(render.getLocationHash)) hashStr = render.getLocationHash()

		var agRender = render || self.AgRender;
		var palletPartsStore = store || Ext.data.StoreManager.lookup('palletPartsStore');
		var pallet_records = records || palletPartsStore.getRange();

		var jsonObj = self.getLocaleHashObj(hashStr);
		jsonObj = jsonObj || {};
//		console.log(jsonObj.Camera);

		//Common
		jsonObj.Common = jsonObj.Common || AgURLParser.newCommon();

		jsonObj.Common.Model = DEF_MODEL;

		jsonObj.Common.Version = DEF_VERSION;

		jsonObj.Common.TreeName = DEF_TREE;


		//ColorHeatMap
		jsonObj.Common.ColorbarFlag = jsonObj.Common.ScalarColorFlag = Ext.getCmp('options-colorheatmap').checked;
		jsonObj.Common.ScalarMaximum = Ext.getCmp('options-colorheatmap-max').getValue();
		jsonObj.Common.ScalarMinimum = Ext.getCmp('options-colorheatmap-min').getValue();



		//Window
		jsonObj.Window = jsonObj.Window || AgURLParser.newWindow();

		// Grid
		jsonObj.Window.GridFlag = Ext.getCmp('options-grid').checked;
		jsonObj.Window.GridTickInterval = Ext.getCmp('options-grid-spacing').getValue();
		jsonObj.Window.GridColor = Ext.getCmp('options-grid-color').getValue();

		// BackgroundColor
		jsonObj.Window.BackgroundColor = Ext.getCmp('options-background-color').getValue();
		var BackgroundOpacity = Ext.getCmp('options-background-opacity').checked;
		if(!Ext.isEmpty(BackgroundOpacity)) jsonObj.Window.BackgroundOpacity = BackgroundOpacity ? 0 : 100;

		//Parts
		var parts = [];

		var ext_parts_hash = {};
		var ext_parts = [];
		{
			Ext.each(pallet_records,function(record,i,a){
				if(!record.get('selected')) return true;

//				var groupid = record.get('artf_id');
				var groupid = '.';
				var groupname = '.';
				var grouppath = '.';
				if(Ext.isEmpty(groupid) || Ext.isEmpty(groupname) || Ext.isEmpty(grouppath)) return true;

				if(Ext.isEmpty(ext_parts_hash[groupid])){
					ext_parts_hash[groupid] = AgURLParser.newExtensionPartGroup();
					ext_parts_hash[groupid].PartGroupId = groupid;
					ext_parts_hash[groupid].PartGroupName = groupname;
					ext_parts_hash[groupid].PartGroupPath = grouppath;
				}

				var part = AgURLParser.newExtensionPart();
				var color = record.get('color');
				if(color.substr(0,1) == '#') color = color.substr(1);
				part.PartColor = color;

				part.PartId = record.get('art_id');
				part.PartName = record.get('art_filename');
				part.PartOpacity = record.get('opacity');
				part.UseForBoundingBoxFlag = record.get('focused');
				part.PartDeleteFlag = record.get('remove');
				part.PartRepresentation = record.get('representation');

				part.PartScalarFlag = false;
				if(Ext.isNumber(record.get('scalar'))){
					part.PartScalar = record.get('scalar');
					part.PartScalarFlag = jsonObj.Common.ColorbarFlag;
				}

				part.PartPath = record.get('art_path');
				part.PartMTime = (new Date(record.get('art_timestamp'))).getTime();

				ext_parts_hash[groupid].PartGroupItems.push(part);
			});
			for(var groupid in ext_parts_hash){
				ext_parts.push(ext_parts_hash[groupid]);
			}
		}
//		console.log("ext_parts=["+ext_parts.length+"]");

		{/*Focus情報をクリア*/
			palletPartsStore.suspendEvents(false);
			palletPartsStore.clearFilter();
			palletPartsStore.filterBy(function(record,id){
				if(Ext.isEmpty(record.data.focused)) return false;
				return true;
			});
			palletPartsStore.each(function(record,i,a){
				record.beginEdit();
				record.set('focused',null);
				record.commit(false);
				record.endEdit(false,['focused']);
			});
			palletPartsStore.clearFilter();
			palletPartsStore.resumeEvents();
		}

		var legend = AgURLParser.newLegend();
		try{
			legend.LegendTitle    = Ext.getCmp('legend-title-textfield').getValue();
			legend.Legend         = Ext.getCmp('legend-legend-textareafield').getValue();
			legend.LegendAuthor   = Ext.getCmp('legend-author-textfield').getValue();
			legend.DrawLegendFlag = Ext.getCmp('legend-draw-checkbox').getValue();
		}catch(e){
		}

		var PinDescriptionDrawFlag = false;//Ext.getCmp('pin-description-checkbox').getValue();
		var PinIndicationLineDrawFlag = 0;//Ext.getCmp('pin-line-combobox').getValue();
		var PinShape = 'PIN_LONG';//Ext.getCmp('pin-shape-combobox').getValue();
		var pins = [];
		var pinStore = Ext.data.StoreManager.lookup('pinStore');
		if(pinStore){
			pinStore.each(function(record,i,a){
	//		console.log(record.data);
				var pin = AgURLParser.newPin();
				for(var key in record.data){
					if(key.indexOf('Color')>=0 && record.data[key].indexOf('#')==0){
						pin[key] = record.data[key].substr(1);
					}else{
						pin[key] = record.data[key];
					}
				}
				pin.PinDescriptionDrawFlag = PinDescriptionDrawFlag;
				pin.PinIndicationLineDrawFlag = PinIndicationLineDrawFlag;
				pin.PinShape = PinShape;
				pins.push(pin);
			});
		}

		// Pin
		jsonObj.Common.PinDescriptionDrawFlag = PinDescriptionDrawFlag;
		jsonObj.Common.PinIndicationLineDrawFlag = PinIndicationLineDrawFlag;


		jsonObj.Part = parts;
		jsonObj.Legend = legend;
		jsonObj.Pin = pins;
		jsonObj.ExtensionPartGroup = ext_parts;

//	console.log("setHashTask()");
//	console.log(jsonObj);
//	console.log(ext_parts);

		agRender.setHash(Ext.JSON.encode(jsonObj));
		if(Ext.isFunction(callback)) callback.apply(self);
	});

	self.setDisabled_pallet_grid_button_Task = new Ext.util.DelayedTask(function(){
		var buttons = [];
		buttons.push(Ext.getCmp('ag-pallet-copy-button'));
		buttons.push(Ext.getCmp('ag-pallet-delete-button'));
		buttons.push(Ext.getCmp('ag-pallet-download-button'));
		buttons.push(Ext.getCmp('ag-pallet-def-color-button'));
		buttons.push(Ext.getCmp('ag-pallet-none-color-button'));
		buttons.push(Ext.getCmp('ag-pallet-color-pallet-button'));
		buttons.push(Ext.getCmp('ag-pallet-opacity-pallet-button'));
		buttons.push(Ext.getCmp('ag-pallet-remove-pallet-button'));
		var pallet_grid = Ext.getCmp('pallet-grid');
		var selModel = pallet_grid.getSelectionModel();
		var selCount = selModel.getCount();
		Ext.iterate(buttons,function(button,index,allItems){
			if(button && button.setDisabled) button.setDisabled(selCount===0);
		});

		var button = Ext.getCmp('ag-pallet-edit-button');
		button.setDisabled(true);
		if(selCount>=1){
			var idx=-1;
			Ext.each(selModel.getSelection(),function(r,i,a){
				if(Ext.isEmpty(r.get('art_id'))) return true;
				idx = i;
				return false;
			});
			button.setDisabled(idx<0?true:false);
		}
	});

	self.downloadObjectsTask = new Ext.util.DelayedTask();
	self.searchArtMirroringIdTask = new Ext.util.DelayedTask();
};

window.AgApp.prototype.initExtJS = function(){
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
};

window.AgApp.prototype.getExtraParams = function(params){
	var self = this;

	params = params || {};
	if(Ext.isEmpty(params.current_datas)) params.current_datas = 1;

	var ci_id;
	var cb_id;

	try{
		var field = Ext.getCmp(self.MAPPING_MNG_ID).down('#concept-build-combobox');
		if(field && field.rendered){
			var record = field.findRecordByValue(field.getValue());
			if(record){
				ci_id = record.get('ci_id');
				cb_id = record.get('cb_id');
			}else{
				return undefined;
			}
		}
	}catch(e){
//		console.error(e);
	}

	if(Ext.isEmpty(ci_id)){
		var field = Ext.getCmp('concept-info-combobox');
		if(field && field.rendered){
			try{
				var record = field.findRecordByValue(field.getValue());
				if(record){
					ci_id = record.get('ci_id');
				}else{
					return undefined;
				}
			}catch(e){
				if(!field.isHidden()){
					console.error(e);
					return undefined;
				}
			}
		}else{
			return undefined;
		}
	}



	var ExtVersion = Ext.getVersion()

	var current_datas = null;
	if(params.current_datas) current_datas = self.getCurrentDatas();

	return {
		ci_id: ci_id,
		cb_id: cb_id,
		current_datas: current_datas,
		_ExtVerMajor: ExtVersion.getMajor(),
		_ExtVerMinor: ExtVersion.getMinor(),
		_ExtVerPatch: ExtVersion.getPatch(),
		_ExtVerBuild: ExtVersion.getBuild(),
		_ExtVerRelease: ExtVersion.getRelease(),
	};
};

window.AgApp.prototype.beforeloadStore = function(store){
	var self = this;

	var extraParams = self.getExtraParams() || {};

	var p = store.getProxy();
	p.extraParams = p.extraParams || {};
/*
	p.extraParams.model = model;
	p.extraParams.version = version;
	p.extraParams.ag_data = ag_data;
	p.extraParams.tree = tree;

	p.extraParams.md_id = md_id;
	p.extraParams.mv_id = mv_id;
	p.extraParams.mr_id = mr_id;
	p.extraParams.ci_id = ci_id;
	p.extraParams.cb_id = cb_id;
	p.extraParams.bul_id = bul_id;
*/

	p.extraParams = Ext.apply({},extraParams,p.extraParams);

	return true;
};

window.AgApp.prototype.reloadUploadObjectStore_updatePalletPartsStore = function(page){
/*
	var self = this;
	var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
	if(Ext.isEmpty(page)) page = uploadObjectStore.currentPage;

	uploadObjectStore.on({
		load: {
			fn: function(store,records,successful,eOpts){
				var uploadObjectAllStore = Ext.data.StoreManager.lookup('uploadObjectAllStore');
				var palletPartsStore = Ext.data.StoreManager.lookup('palletPartsStore');
				palletPartsStore.suspendEvents(true);
				palletPartsStore.each(function(r){
					if(Ext.isEmpty(r.data.art_id)) return true;
					var rec = uploadObjectAllStore.findRecord('art_id',r.data.art_id,0,false,false,true);
					if(Ext.isEmpty(rec)) return true;
					var keys = [];
					for(var key in r.data){
						if(
							key=='selected' ||
							key=='color' ||
							key=='opacity' ||
							key=='remove' ||
							key=='representation' ||
							key=='scalar' ||
							key=='scalar_flag'
						) continue;
						keys.push(key);
					}
					self.record_update(keys,rec,r);
				});
				palletPartsStore.resumeEvents();
				self.setHashTask.delay(250);
			},
			single: true,
			scope: self
		}
	});
	uploadObjectStore.loadPage(page);
*/
};

//他のstoreのrecordに、palletPartsStoreの内容を反映
window.AgApp.prototype.load_palletPartsRecords = function(records,grid_store,grid){
/*
	var self = this;

	var isCommit = false;
	var palletPartsStore = Ext.data.StoreManager.lookup('palletPartsStore');
	grid_store.suspendEvents(false);
	Ext.iterate(records,function(record,index,allItems){
		if(record && record.get){
			var art_id = record.get('art_id');
			var rep_id = record.get('rep_id');
			var f_id = record.get('f_id');
			var version = record.get('version');
			var name = record.get('name');
			var group = record.get('group');
			var idx = -1;
			if(art_id !== undefined && art_id){
				idx = palletPartsStore.findBy(function(r,id){
					if(art_id == r.get('art_id')) return true;
					return false;
				});
			}else if(rep_id !== undefined && rep_id){
				idx = palletPartsStore.findBy(function(r,id){
					if(rep_id == r.get('rep_id')) return true;
					return false;
				});
			}else{
				if(idx<0 && f_id && version){
					idx = palletPartsStore.findBy(function(r,id){
						if(f_id == r.get('f_id') && version == r.get('version')) return true;
						return false;
					});
				}
				if(idx<0 && name && group){
					idx = palletPartsStore.findBy(function(r,id){
						if(name == r.get('name') && group == r.get('group')) return true;
						return false;
					});
				}
			}
			var r=null;
			if(idx>=0) r = palletPartsStore.getAt(idx);
			if(!Ext.isEmpty(r)){

				var key = 'selected';
				if(Ext.isBoolean(record.get(key)) && !record.get(key)){
					record.beginEdit();
					record.set(key,true);
					record.commit(false);
					record.endEdit(false,[key]);
					isCommit = true;
				}
				if(record.modelName=='BP3D_TREE'){
					var key = 'checked';
					if(Ext.isBoolean(record.get(key)) && !record.get(key)){
						record.beginEdit();
						record.set(key,true);
						record.commit(false);
						record.endEdit(false,[key]);
						isCommit = true;
					}
				}
			}else{
				var key = 'selected';
				if(Ext.isBoolean(record.get(key)) && record.get(key)){
					record.beginEdit();
					record.set(key,false);
					record.commit(false);
					record.endEdit(false,[key]);
					isCommit = true;
				}
				if(record.modelName=='BP3D_TREE'){
					var key = 'checked';
					if(Ext.isBoolean(record.get(key)) && record.get(key)){
						record.beginEdit();
						record.set(key,false);
						record.commit(false);
						record.endEdit(false,[key]);
						isCommit = true;
					}
				}
			}
		}
		return;
	});
	grid_store.resumeEvents();
	if(isCommit && grid){
		grid.getView().refresh();
	}
*/
};

window.AgApp.prototype.find_palletPartsStore = function(records){
	var self = this;

	var palletPartsStore = Ext.data.StoreManager.lookup('palletPartsStore');


	var hash_records = {};
	var rtn_records = [];

	Ext.each(records,function(record,index,allItems){

		var selected = record.get('selected')!==undefined ? record.get('selected') : record.get('checked');

		var art_id = record.get('art_id');
		var rep_id = record.get('rep_id');

		var group = record.get('group');
		if(Ext.isEmpty(group)) group = record.get('version');
		if(Ext.isEmpty(group)) group = '';

		var name = record.get('name');
		if(Ext.isEmpty(name)) name = '';

		palletPartsStore.each(function(r,i,a){
			if(!Ext.isEmpty(r.get('art_id')) && !Ext.isEmpty(art_id)){
				if(r.get('art_id') != art_id) return true;
			}else if(!Ext.isEmpty(r.get('rep_id')) && !Ext.isEmpty(rep_id)){
				if(r.get('rep_id') != rep_id) return true;
			}else{
				if(r.get('group') != group || r.get('name') != name) return true;
			}
			hash_records[r.getId()] = r;
		});
	});

	Ext.each(hash_records,function(key, value, myself){
		rtn_records.push(value);
	});
	return rtn_records;
};

//他のstoreのrecordを使用して、palletPartsStoreの内容を更新
window.AgApp.prototype.update_palletPartsStore = function(records,queueSuspended,after_selected){
	var self = this;

	var palletPartsStore = Ext.data.StoreManager.lookup('palletPartsStore');

	if(Ext.isEmpty(queueSuspended)) queueSuspended = true;
	if(Ext.isEmpty(after_selected)) after_selected = false;


	var add_records = [];
	var palletPartsStore_add_records = [];
	var palletPartsStore_del_records = [];
	Ext.iterate(records,function(record,index,allItems){

		var selected = record.get('selected')!==undefined ? record.get('selected') : record.get('checked');

		var art_id = record.get('art_id');
		var rep_id = record.get('rep_id');

		var group = record.get('group');
		if(Ext.isEmpty(group)) group = record.get('version');
		if(Ext.isEmpty(group)) group = '';

		var name = record.get('name');
		if(Ext.isEmpty(name)) name = '';

		var isAdd = false;
		var n_records = [];
		palletPartsStore.each(function(r,i,a){
/*
			if(r.get('art_id')!==undefined && art_id!==undefined){
				if(r.get('art_id') != art_id) return true;
			}else if(r.get('rep_id')!==undefined && rep_id!==undefined){
				if(r.get('rep_id') != rep_id) return true;
			}else{
				if(r.get('group') != group || r.get('name') != name) return true;
			}
*/
			if(!Ext.isEmpty(r.get('art_id')) && !Ext.isEmpty(art_id)){
				if(r.get('art_id') != art_id) return true;
			}else if(!Ext.isEmpty(r.get('rep_id')) && !Ext.isEmpty(rep_id)){
				if(r.get('rep_id') != rep_id) return true;
			}else{
				if(r.get('group') != group || r.get('name') != name) return true;
			}

			n_records.push(r);
//			return false;
		});
		if(selected && Ext.isEmpty(n_records)){
			isAdd = true;
			n_records.push(Ext.create(Ext.getClassName(palletPartsStore.model),Ext.apply({}, record.data)));
		}
		if(!Ext.isEmpty(n_records)){
			if(selected){
				Ext.each(n_records,function(n_record){
					var modifiedFieldNames = [];
					n_record.beginEdit();
					for(var key in record.data){
						if(n_record.get(key) !== undefined && record.get(key) !== n_record.get(key)){
							n_record.set(key,record.get(key));
							modifiedFieldNames.push(key);
						}
					}
					if(n_record.get('selected') !== selected){
						var key = 'selected';
						n_record.set(key,selected);
						modifiedFieldNames.push(key);
					}

					if(record.get('group')===undefined && record.get('version')!==undefined){
						var key = 'group';
						n_record.set(key,record.get('version'));
						modifiedFieldNames.push(key);
					}

					if(!Ext.isEmpty(group) && !Ext.isEmpty(self.groupname2grouppath[group]) && n_record.get('grouppath') != self.groupname2grouppath[group].PartGroupPath){
						n_record.set('grouppath',self.groupname2grouppath[group].PartGroupPath);
						modifiedFieldNames.push('grouppath');
					}

					if(modifiedFieldNames.length>0){
						n_record.commit(false);
						n_record.endEdit(false,modifiedFieldNames);
						isCommit = true;
					}else{
						record.cancelEdit();
					}
					if(isAdd){
						palletPartsStore_add_records.push(n_record);
					}
					add_records.push(n_record);
				});
			}else{
				palletPartsStore_del_records = palletPartsStore_del_records.concat(n_records);
			}
		}
	});

	if(palletPartsStore_add_records.length){
		try{
			palletPartsStore.suspendEvents(queueSuspended);
			palletPartsStore.add(palletPartsStore_add_records);
			palletPartsStore.resumeEvents();
		}catch(e){
			console.error(e);
		}
	}
	if(palletPartsStore_del_records.length){
		try{
			palletPartsStore.suspendEvents(queueSuspended);
			palletPartsStore.remove(palletPartsStore_del_records);
			palletPartsStore.resumeEvents();
		}catch(e){
			console.error(e);
		}
	}


	if(after_selected){
		var pallet_grid = Ext.getCmp('pallet-grid');
		var selMode = pallet_grid.getSelectionModel();
		selMode.select(add_records);
	}

	self.update_other_palletPartsStore();

};

window.AgApp.prototype.updata_grid_store_record = function(record,grid_store,grid){
/*
	var self = this;
	var r = grid_store.findRecord('rep_id',record.get('rep_id'),false,true,true);
	if(!Ext.isEmpty(r)){
		grid_store.suspendEvents(!Ext.isEmpty(grid));
		var modifiedFieldNames = [];
		r.beginEdit();
		for(var key in record.data){
			if(
				Ext.isString(record.data[key]) ||
				Ext.isNumber(record.data[key]) ||
				Ext.isBoolean(record.data[key])){
				if(r.data[key] !== undefined && record.data[key] !== undefined && record.get(key) !== r.get(key)){
					r.set(key,record.get(key));
					modifiedFieldNames.push(key);
				}
			}
		}
		if(modifiedFieldNames.length>0){
			r.commit(false);
			r.endEdit(false,modifiedFieldNames);
		}else{
			r.cancelEdit();
		}
		grid_store.resumeEvents();
		if(modifiedFieldNames.length>0 && !Ext.isEmpty(grid)){
			grid.getView().refresh();
		}
	}
*/
};

window.AgApp.prototype.store_find_group = function(store,group){
/*
	var self = this;

	var records = [];
	store.each(function(r,i,a){
		if(r.get('artg_name') != group) return;
		records.push(r);
	});
	return records;
*/
};

window.AgApp.prototype.record_update = function(keys,s_record,d_record){
/*
	var self = this;

	var isCommit = false;
	var modifiedFieldNames = [];
	d_record.beginEdit();
	Ext.iterate(keys,function(key,i,a){
		var field = s_record.fields.getByKey('name');
		if(Ext.isEmpty(field)) return true;
		if(
//			Ext.isString(s_record.data[key]) ||
//			Ext.isNumber(s_record.data[key]) ||
//			Ext.isBoolean(s_record.data[key])||
//			Ext.isDate(s_record.data[key])

			field.type.type == 'string'  ||
			field.type.type == 'int'     ||
			field.type.type == 'float'   ||
			field.type.type == 'boolean' ||
			field.type.type == 'date'

		){
			if(s_record.get(key) != d_record.get(key)){
				d_record.set(key,s_record.get(key));
				modifiedFieldNames.push(key);
			}
		}
	});
	if(modifiedFieldNames.length>0){
		d_record.commit(false);
		d_record.endEdit(false,modifiedFieldNames);
		isCommit = true;
	}else{
		d_record.cancelEdit();
	}
	return isCommit;
*/
};

window.AgApp.prototype.extension_parts_store_update = function(record,addRec,queueSuspended){
/*
	var self = this;

	var records = Ext.isArray(record) ? record : [record];
	if(Ext.isEmpty(queueSuspended)) queueSuspended = true;
	var add_records = [];
	var upd_records = [];

	var org_add_records = [];
	var org_upd_records = [];

	var extension_parts_store = Ext.data.StoreManager.lookup('extensionPartsStore');

	Ext.each(records,function(record,i,a){
		var e_record = self.store_find(extension_parts_store,record,false);
		if(addRec && !e_record){
			add_records.push(Ext.create(Ext.getClassName(extension_parts_store.model),{}));
			org_add_records.push(record);
		}else if(e_record){
			upd_records.push(e_record);
			org_upd_records.push(record);
		}else{
			return false;
		}
	});
	if(add_records.length + upd_records.length != records.length) return;

	extension_parts_store.suspendEvents(queueSuspended);
	try{
		var data;
		if(records[0]) data = records[0].getData();
		if(Ext.isObject(data)){
			var keys = Ext.Array.filter(Ext.Object.getKeys(data),function(key){
				if(
					key=='color' ||
					key=='opacity' ||
					key=='remove' ||
					key=='representation' ||
					key=='scalar' ||
					key=='scalar_flag'
				) return false;
				return true;
			});
			Ext.each(org_upd_records,function(record,i,a){
				self.record_update(keys,org_upd_records[i],upd_records[i]);
			});

			keys = Ext.Object.getKeys(data);
			Ext.each(org_add_records,function(record,i,a){
				self.record_update(keys,org_add_records[i],add_records[i]);
			});
		}
		if(add_records.length) extension_parts_store.add(add_records);
	}catch(e){
		console.error(e);
	}
	extension_parts_store.resumeEvents();

	if(!queueSuspended) self.update_palletPartsStore(upd_records.concat(add_records));
*/
};

window.AgApp.prototype.store_find = function(store,records,createNewRecord){
/*
	var self = this;

	if(Ext.isEmpty(createNewRecord)) createNewRecord = false;//対象レコードが無い場合に、新規にレコードを作成するか？

	var local_find = function(record){
		var e_record = null;
		store.each(function(r,i,a){
			if(r.get('art_id')!==undefined && record.get('art_id')!==undefined){
				if(r.get('art_id') != record.get('art_id')) return true;
//			}else if(r.get('rep_id')!==undefined && record.get('rep_id')!==undefined){
//				if(r.get('rep_id') != record.get('rep_id')) return true;
			}else{
				if(r.get('group') != record.get('group') || r.get('name') != record.get('name')) return true;
			}
			e_record = r;
			return false;
		});
		return e_record;
	};

	if(Ext.isArray(records)){
		var upd_records = null;
		records = Ext.isArray(records) ? records : [records];
		Ext.each(records,function(record,i,a){
			var e_record = local_find(record);
			if(createNewRecord && Ext.isEmpty(e_record)) e_record = Ext.create(Ext.getClassName(store.model),{});
			if(Ext.isEmpty(e_record)) return true;
			upd_records = upd_records ||[];
			upd_records.push(e_record);
		});
		return upd_records;
	}else{
		var e_record = local_find(records);
		if(createNewRecord && Ext.isEmpty(e_record)) e_record = Ext.create(Ext.getClassName(store.model),{});
		return e_record;
	}
*/
};

//palletPartsStoreの内容をlocalStorageに保存
window.AgApp.prototype.update_localdb_pallet = function(){
	var self = this;

	var saveRecords = [];
	Ext.data.StoreManager.lookup('palletPartsStore').each(function(r,i,a){
		if(r.get('dropobject')) return true;
		var record = {};
		Ext.Object.each(r.getData(),function(key,val){
			if(Ext.isDate(val)){
				record[key] = val.getTime();
			}else{
				record[key] = val;
			}
		});
		delete record.target_record;
		saveRecords.push(record);
	});
	self.AgLocalStorage.save(self.DEF_LOCALDB_HASH_KEY,Ext.encode(saveRecords));
};

window.AgApp.prototype.upload_group_store_hashchange = function(e){
/*
	var self = this;
	window.location.reload(true);
*/
};

window.AgApp.prototype.upload_group_store_load = function(store,records){
/*
	var self = this;

	var extension_parts_store = Ext.data.StoreManager.lookup('extensionPartsStore');
	var upload_group_store = Ext.data.StoreManager.lookup('uploadGroupStore');
	var upload_object_store = Ext.data.StoreManager.lookup('uploadObjectStore');
	var uploadObjectAllStore = Ext.data.StoreManager.lookup('uploadObjectAllStore');

	var jsonObj = self.getLocaleHashObj();
	if(jsonObj){

		var d_store = upload_group_store;
		var d_filters = d_store._getFilters();
		d_store._setFilters([{
			anyMatch: false,
			caseSensitive: false,
			exactMatch: true,
			property: 'artg_delcause',
			value: null
		}]);
		var d_records = d_store.getRange();

		var o_store;
		o_store = uploadObjectAllStore;
		var o_records = o_store.getRange();

//		console.log("upload_group_store_load():["+d_records.length+"]["+o_records.length+"]");

		if(jsonObj.ExtensionPartGroup && jsonObj.ExtensionPartGroup.length>0 && d_records.length>0){

			d_store.suspendEvents(true);

			o_store.suspendEvents(false);
			extension_parts_store.suspendEvents(false);

			var partGroups = {};
			for(var i in jsonObj.ExtensionPartGroup){
				var ExtensionPartGroup = jsonObj.ExtensionPartGroup[i];
				if(Ext.isEmpty(ExtensionPartGroup.PartGroupId)){
					var d_record = d_store.findRecord('name',ExtensionPartGroup.PartGroupName,0,false,false,true);
					if(d_record){
						ExtensionPartGroup.PartGroupId = d_record.get('artg_id');
						ExtensionPartGroup.PartGroupName = d_record.get('artg_name');
						ExtensionPartGroup.PartGroupPath = d_record.get('path');
					}
				}
				if(!Ext.isEmpty(ExtensionPartGroup.PartGroupId)){
					partGroups[ExtensionPartGroup.PartGroupId] = ExtensionPartGroup;
				}else{
					partGroups[ExtensionPartGroup.PartGroupName] = ExtensionPartGroup;
				}
//				console.log("upload_group_store_load(1):ExtensionPartGroup.PartGroupName=["+ExtensionPartGroup.PartGroupName+"]["+partGroups[ExtensionPartGroup.PartGroupName]+"]");
			}

			var upd_records = [];
			var add_records = [];

			for(var i in d_records){
				var d_record = d_records[i];
				var PartGroupId = d_record.get('artg_id');
				var PartGroupName = d_record.get('artg_name');
//				console.log("upload_group_store_load(1.1):PartGroupName=["+PartGroupName+"]["+partGroups[PartGroupName]+"]");
				if(Ext.isEmpty(partGroups[PartGroupId]) && Ext.isEmpty(partGroups[PartGroupName])) continue;
//				console.log("upload_group_store_load(2):PartGroupName=["+PartGroupName+"]");

				var fieldName = 'selected';
				if(d_record.get(fieldName) != true){

					d_record.beginEdit();
					d_record.set(fieldName,true);
					d_record.commit(false);
					d_record.endEdit(false,[fieldName]);

//					console.log("upload_group_store_load(3):PartGroupName=["+PartGroupName+"]");
				}else{
//					d_record.cancelEdit();
//					console.log("upload_group_store_load(4):PartGroupName=["+PartGroupName+"]["+partGroups[PartGroupName].PartGroupItems.length+"]");
//					continue;

					var PartGroupItems = null;
					if(partGroups[PartGroupId].PartGroupItems && partGroups[PartGroupId].PartGroupItems.length>0){
						PartGroupItems = partGroups[PartGroupId].PartGroupItems;
					}else if(partGroups[PartGroupName].PartGroupItems && partGroups[PartGroupName].PartGroupItems.length>0){
						PartGroupItems = partGroups[PartGroupName].PartGroupItems;
					}
					if(PartGroupItems && PartGroupItems.length>0){

						var parts = {};
						for(var i in PartGroupItems){
							var part = PartGroupItems[i];
//							parts[part.PartName] = part;
							parts[part.PartPath] = part;
//							console.log("upload_group_store_load(5):part.PartName=["+part.PartName+"]["+o_records.length+"]");
						}
						for(var i in o_records){
							var record = o_records[i];
//							var PartName = record.get('name');
							var PartName = record.get('path');
							if(Ext.isEmpty(parts[PartName])) continue;
//							console.log("upload_group_store_load(6):PartName=["+PartName+"]");

							var obj = parts[PartName];

							var modifiedFieldNames = [];
							record.beginEdit();
							if(record.get('selected') != true){
								record.set('selected',true);
								modifiedFieldNames.push('selected');
							}
							if(!Ext.isEmpty(obj.PartColor) && record.get('color') != '#'+obj.PartColor){
								record.set('color','#'+obj.PartColor);
								modifiedFieldNames.push('color');
							}
							if(!Ext.isEmpty(obj.PartOpacity) && record.get('opacity') != obj.PartOpacity){
								record.set('opacity',obj.PartOpacity);
								modifiedFieldNames.push('opacity');
							}
							if(!Ext.isEmpty(obj.PartDeleteFlag) && record.get('remove') != obj.PartDeleteFlag){
								record.set('remove',obj.PartDeleteFlag);
								modifiedFieldNames.push('remove');
							}
							if(!Ext.isEmpty(obj.UseForBoundingBoxFlag) && record.get('focused') != obj.UseForBoundingBoxFlag){
								record.set('focused',obj.UseForBoundingBoxFlag);
								modifiedFieldNames.push('focused');
							}
							if(modifiedFieldNames.length>0){
								record.commit(true);
								record.endEdit(true,modifiedFieldNames);
							}else{
								record.cancelEdit();
							}

//							self.extension_parts_store_update(record,true);
//							if(self.glb_localdb_init) self.update_palletPartsStore([record],false);
							upd_records.push(record);

							delete parts[PartName];
						}

//						o_store.resumeEvents();
//						pallet_grid.getView().refresh();


						for(var PartName in parts){
//							console.log("upload_group_store_load(7):PartName=["+PartName+"]");
//							console.log("upload_group_store_load(7):PartGroupName=["+PartGroupName+"]");

							var record = Ext.create(Ext.getClassName(extension_parts_store.model),{});

							var obj = parts[PartName];

							var modifiedFieldNames = [];
							record.beginEdit();
							if(record.get('selected') != true){
								record.set('selected',true);
								modifiedFieldNames.push('selected');
							}
							if(!Ext.isEmpty(obj.PartName) && record.get('name') != obj.PartName){
								record.set('name',obj.PartName);
								modifiedFieldNames.push('name');
							}
							if(!Ext.isEmpty(obj.PartColor) && record.get('color') != '#'+obj.PartColor){
								record.set('color','#'+obj.PartColor);
								modifiedFieldNames.push('color');
							}
							if(!Ext.isEmpty(obj.PartOpacity) && record.get('opacity') != obj.PartOpacity){
								record.set('opacity',obj.PartOpacity);
								modifiedFieldNames.push('opacity');
							}
							if(!Ext.isEmpty(obj.PartDeleteFlag) && record.get('remove') != obj.PartDeleteFlag){
								record.set('remove',obj.PartDeleteFlag);
								modifiedFieldNames.push('remove');
							}
							if(!Ext.isEmpty(obj.UseForBoundingBoxFlag) && record.get('focused') != obj.UseForBoundingBoxFlag){
								record.set('focused',obj.UseForBoundingBoxFlag);
								modifiedFieldNames.push('focused');
							}
							if(!Ext.isEmpty(obj.PartPath) && record.get('path') != obj.PartPath){
								record.set('path',obj.PartPath);
								modifiedFieldNames.push('path');
							}
							if(!Ext.isEmpty(PartGroupName) && record.get('group') != PartGroupName){
								record.set('group',PartGroupName);
								modifiedFieldNames.push('group');
							}
							if(modifiedFieldNames.length>0){
								record.commit(true);
								record.endEdit(true,modifiedFieldNames);
							}else{
								record.cancelEdit();
							}

//							self.extension_parts_store_update(record,true);
//							if(self.glb_localdb_init) self.update_palletPartsStore([record],false);
							upd_records.push(record);

						}

//						extension_parts_store.resumeEvents();

					}
				}
			}

			self.extension_parts_store_update(upd_records,true);
			if(self.glb_localdb_init) self.update_palletPartsStore(upd_records,false);

			o_store.resumeEvents();
			extension_parts_store.resumeEvents();

			d_store.resumeEvents();
		}
		d_store._setFilters(d_filters);
	}

	Ext.getCmp('upload-group-grid').getView().refresh();
	Ext.getCmp('upload-object-grid').getView().refresh();

	if(self.glb_localdb_init){
		var pallet_grid = Ext.getCmp('pallet-grid');
		pallet_grid.getView().refresh();
		self.update_localdb_pallet();
	}
*/
};

window.AgApp.prototype.initRecoreds = function(records){
	var self = this;

	for(var i in records){
		var record = records[i];
		var fields = record.fields;
		var modifiedFieldNames = [];
		record.beginEdit();
		for(var j in fields.items){
			if(Ext.isEmpty(fields.items[j].defaultValue)) continue;
			if(record.get(fields.items[j].name) == fields.items[j].defaultValue) continue;
			record.set(fields.items[j].name,fields.items[j].defaultValue);
			modifiedFieldNames.push(fields.items[j].name);
		}
		if(modifiedFieldNames.length>0){
			record.commit(false);
			record.endEdit(false,modifiedFieldNames);
		}else{
			record.cancelEdit();
		}
	}
};

window.AgApp.prototype.extension_parts_store_remove_group = function(group){
/*
	var self = this;

	var extension_parts_store = Ext.data.StoreManager.lookup('extensionPartsStore');
	var records = self.store_find_group(extension_parts_store,group);
	if(records.length>0) extension_parts_store.remove(records);
*/
};

window.AgApp.prototype.getCellEditing = function(){
	var self = this;
	return Ext.create('Ext.grid.plugin.CellEditing', {
		pluginId: 'cellediting',
		clicksToEdit: 1,
		listeners: {
			edit : function(editor,e,eOpts){
				var isCommit = false;
				Ext.Object.each(e.record.getChanges(),function(key,value,object){
					isCommit = true;
					return false;
				});
				if(isCommit) e.record.commit();
			}
		}
	});
};

window.AgApp.prototype.getBufferedRenderer = function(args){
	var self = this;
	args = Ext.apply({},args||{},{
		pluginId: 'bufferedrenderer',
		trailingBufferZone: 20,
		leadingBufferZone: 50
	});
	return Ext.create('Ext.grid.plugin.BufferedRenderer', args);
};

//選択されているrecordsを削除
window.AgApp.prototype.remove_select_records_palletPartsStore = function(queueSuspended){
	var self = this;

	var palletPartsStore = Ext.data.StoreManager.lookup('palletPartsStore');

	if(Ext.isEmpty(queueSuspended)) queueSuspended = true;
	var pallet_grid = Ext.getCmp('pallet-grid');
	var selMode = pallet_grid.getSelectionModel();
	var selCount = selMode.getCount();
	if(selCount>0){
		pallet_grid.setLoading(true);
		Ext.defer(function(){

			var records = selMode.getSelection().reverse();
			selMode.deselect(records);

			palletPartsStore.suspendEvents(false);
			palletPartsStore.remove(records);
			palletPartsStore.resumeEvents();
			pallet_grid.getView().refresh();

			palletPartsStore.fireEvent('datachanged',palletPartsStore);

			self.setHashTask.delay(0);
			self.update_localdb_pallet();

			var store;

			self.update_other_palletPartsStore();

			pallet_grid.setLoading(false);
		},100);
	}
	return selCount;
};

//palletPartsStoreの内容を他のstoreに反映
window.AgApp.prototype.update_other_palletPartsStore = function(){
	var self = this;
	var store;
	store = Ext.data.StoreManager.lookup('uploadObjectStore');
	store.fireEvent('datachanged',store);
	store = Ext.data.StoreManager.lookup('bp3dSearchStore');
	store.fireEvent('datachanged',store);
	store = Ext.data.StoreManager.lookup('pickSearchStore');
	store.fireEvent('datachanged',store);
};

window.AgApp.prototype.getSelectedSorters = function(){
	return [{
		property: 'selected',
		direction: 'DESC'
	},{
		property: 'art_name',
		direction: 'ASC'
	}];
}

window.AgApp.prototype.getSelectedArtIds = function(store){
	var self = this;
	if(Ext.isEmpty(store)) store = Ext.data.StoreManager.lookup('palletPartsStore');
	var selected_art_ids = {};
	store.each(function(r){
		if(!r.get('selected')) return true;
		var artg_id = r.get('artg_id');
		if(Ext.isEmpty(artg_id)) return true;
		selected_art_ids[artg_id] = selected_art_ids[artg_id] || {};
		selected_art_ids[artg_id][r.get('art_id')] = null;
	});
	return selected_art_ids;
};

//DEBUG用関数
window.AgApp.prototype.getCurrentDatas = function(){
	var pallet_datas = [];
	var object_datas = [];
	try{
		Ext.data.StoreManager.lookup('palletPartsStore').each(function(r){
			pallet_datas.push(Ext.apply({},r.data));
		});
	}catch(e){}
	try{
		Ext.data.StoreManager.lookup('uploadObjectStore').each(function(r){
			object_datas.push({
				art_id:r.get('art_id'),
				selected:r.get('selected')
			});
		});
	}catch(e){}
	return Ext.encode({
		pallet_datas:pallet_datas,
		object_datas:object_datas
	});
};

window.AgApp.prototype.updateArtInfo = function(callback,store,art_ids){
	var self = this;

	if(Ext.isEmpty(store)) store = Ext.data.StoreManager.lookup('palletPartsStore');
	if(Ext.isEmpty(art_ids)){
		art_ids = [];
		var art_id_hash = {};
		store.each(function(r){
			var art_id = r.get('art_id');
			if(Ext.isEmpty(art_id)) return true;
			if(Ext.isEmpty(art_id_hash[art_id])){
				art_id_hash[art_id] = art_id;
				art_ids.push({
					art_id:         art_id,
					color:          r.get('color'),
					opacity:        r.get('opacity'),
					remove:         r.get('remove'),
					representation: r.get('representation'),
					scalar:         r.get('scalar'),
					scalar_flag:    r.get('scalar_flag'),
					selected:       r.get('selected')
				});
			}
		});
	}
	if(Ext.isEmpty(art_ids)){
		if(callback) callback();
		return;
	}

	var exists_art_ids = [];
	Ext.each(art_ids,function(item){
		exists_art_ids.push(item.art_id);
	});

	var params = self.getExtraParams() || {};
	delete params.current_datas;
//	params.art_ids = Ext.encode(art_ids);
	params.exists_art_ids = Ext.encode(exists_art_ids);

	Ext.Ajax.request({
//		url: 'get-upload-obj-info.cgi',
		url: 'api-upload-file-list.cgi',
		method: 'POST',
		params: params,
		callback: function(eOpts, success, response){
			if(callback) callback();
		},
		success: function(response, eOpts){
			var json;
			try{json = Ext.decode(response.responseText)}catch(e){};
			if(Ext.isEmpty(json) || Ext.isEmpty(json.datas)){
				return;
			}
			store.suspendEvents(true);
			try{
				Ext.iterate(json.datas,function(data){
					var idx = -1;
					do{
						idx = store.find('art_id',data.art_id,idx+1,false,false,true);
						if(idx>=0){
							var n_record = store.getAt(idx);
							if(n_record){
								var modifiedFieldNames = [];
								n_record.beginEdit();
								for(var key in data){
									if(n_record.get(key)==data[key]) continue;
									n_record.set(key,data[key]);
									modifiedFieldNames.push(key);
								}
								Ext.each(n_record.fields.items,function(item,i,a){
									try{
										if(item.convert){
											n_record.set(item.name,item.convert(n_record.get(item.name),n_record));
											modifiedFieldNames.push(item.name);
										}
									}catch(e){console.error(e);}
								});
								n_record.commit(false);
								n_record.endEdit(false,modifiedFieldNames);

							}
						}
					}while(idx>=0);
				});
			}catch(e){console.error(r);}
			store.resumeEvents();
		},
		failure: function(response,eOpts){
		}
	});
};

window.AgApp.prototype.getUploadObjInfo = function(params,options){
	var self = this;

//	var hideNoUse = Ext.getCmp('hide-no-use-checkbox').getValue();
//	if(hideNoUse) params.cm_use = true;

	options = options || {};
//	options.emptyMsg = options.emptyMsg || {
//		title: 'Failure',
//		msg: '対応するデータは、存在しません',
//		buttons: Ext.Msg.OK,
//		icon: Ext.Msg.ERROR
//	};
	if(Ext.isEmpty(options.store)) options.store = Ext.data.StoreManager.lookup('palletPartsStore');

	params = Ext.apply({},self.getExtraParams(),params);
	delete params.current_datas;

	Ext.Ajax.request({
		url: 'get-upload-obj-info.cgi',
		method: 'POST',
		params: params,
		timeout: 300000,
		callback: function(eOpts, success, response){
		},
		success: function(response, eOpts){
			var json;
			var records;
			try{json = Ext.decode(response.responseText)}catch(e){};
			if(Ext.isEmpty(json) || Ext.isEmpty(json.datas)){
				if(json.success){
					if(options.emptyMsg) Ext.Msg.show(options.emptyMsg);
					if(options.empty) options.empty();
				}else if(Ext.isString(json.msg) && json.msg.length){
					Ext.Msg.show({
						title: 'ERROR',
//						iconCls: b.iconCls,
						msg: json.msg,
						buttons: Ext.Msg.OK,
						icon: Ext.Msg.ERROR
					});
					if(options.failure) options.failure();
				}else{
					Ext.Msg.show({
						title: 'ERROR',
						msg: '何らかのエラーが発生しました。',
						buttons: Ext.Msg.OK,
						icon: Ext.Msg.ERROR
					});
					if(options.failure) options.failure();
				}
				return;
			}

			var palletPartsStore = options.store;
			var addrecs = [];
			var success_records = [];
			Ext.iterate(json.datas,function(data){
				var n_record = palletPartsStore.findRecord('art_id',data.art_id,0,false,false,true);
				if(Ext.isEmpty(n_record)){
					var modifiedFieldNames = [];
					n_record = Ext.create(Ext.getClassName(palletPartsStore.model),data);
					n_record.beginEdit();
					if(!Ext.isBoolean(n_record.get('selected')) || !n_record.get('selected')){
						n_record.set('selected',true);
						modifiedFieldNames.push('selected');
					}
					Ext.each(n_record.fields.items,function(item,i,a){
						try{
							if(item.convert){
								n_record.set(item.name,item.convert(n_record.get(item.name),n_record));
								modifiedFieldNames.push(item.name);
							}
						}catch(e){console.error(e);}
					});
					n_record.commit(false);
					n_record.endEdit(false,modifiedFieldNames);

					addrecs.push(n_record);
				}
				success_records.push(n_record);
			});
			if(addrecs.length){
				var sorters = palletPartsStore.sorters.getRange();
				if(sorters.length) palletPartsStore.sorters.clear();
				addrecs = palletPartsStore.add(addrecs);
				if(sorters.length){
					palletPartsStore.sorters.addAll(sorters);
					palletPartsStore.sort();
				}
				if(options.success) options.success(addrecs);
			}else if(success_records.length){
				if(options.success) options.success(success_records);
			}else{
				if(options.emptyMsg) Ext.Msg.show(options.emptyMsg);
				if(options.empty) options.empty();
			}
		},
		failure: function(response,eOpts){
			Ext.Msg.show({
				title: 'ERROR',
				msg: response.statusText + ' ['+ response.status + ']',
				buttons: Ext.Msg.OK,
				icon: Ext.Msg.ERROR
			});
			if(options.failure) options.failure();
		}
	});
};

window.AgApp.prototype.initComponent = function(){
	var self = this;

	var get_grid_filters = function(){
		return {
			ftype: 'filters',
			encode: true, // json encode the filter query
			local: false,   // defaults to false (remote filtering)
		};
	};

	var bp3d_search_grid_renderer = function(value,metaData,record,rowIndex,colIndex,store){
		if(Ext.isObject(metaData) && Ext.isString(metaData.tdCls)){
			if(self.bp3d_search_grid_renderer_params.searchRegExp !== null && Ext.isString(value)){
				value = value.replace(self.bp3d_search_grid_renderer_params.searchRegExp, function(m){
					return '<span class="' + self.bp3d_search_grid_renderer_params.matchCls + '">' + m + '</span>';
				});
			}
		}
		return value;
	};

	var bp3d_search_grid = Ext.create('Ext.ag.GridPanel',{
		id: 'bp3d-search-grid',
		title: 'Filtered List',
		columnLines: true,
		border: false,
		stripeRows: true,
		store: 'bp3dSearchStore',
		stateful: true,
		stateId: 'bp3d-search-grid',
		plugins: [self.getBufferedRenderer()],
		loadMask: false,
		columns: [
			{text: AgLang.cdi_name,    dataIndex: 'cdi_name',    stateId: 'cdi_name',   width:70, minWidth:70, hidden:false, hideable:true, sortable:true, renderer:bp3d_search_grid_renderer},
			{text: AgLang.cdi_name_e,  dataIndex: 'cdi_name_e',  stateId: 'cdi_name_e', flex:1,   minWidth:70, hidden:false, hideable:true, sortable:true, renderer:bp3d_search_grid_renderer },
			{text: AgLang.cdi_name_j,  dataIndex: 'cdi_name_j',  stateId: 'cdi_name_j', flex:1,   minWidth:70, hidden:false, hideable:true, sortable:true, renderer:bp3d_search_grid_renderer },
			{text: AgLang.cdi_name_k,  dataIndex: 'cdi_name_k',  stateId: 'cdi_name_k', flex:1,   minWidth:70, hidden:false, hideable:true, sortable:true, renderer:bp3d_search_grid_renderer },
			{text: AgLang.cdi_name_l,  dataIndex: 'cdi_name_l',  stateId: 'cdi_name_l', flex:1,   minWidth:70, hidden:false, hideable:true, sortable:true, renderer:bp3d_search_grid_renderer },
//			{text: '#'+AgLang.art_ids, dataIndex: 'art_num',     width:50, minWidth:30, hidden:false, hideable:true, sortable:true, align:'right'},
//			{text: AgLang.art_ids,     dataIndex: 'art_ids',     flex:1,   minWidth:70, hidden:false, hideable:true, sortable:true, renderer:bp3d_search_grid_renderer },
		],


		viewConfig: {
			stripeRows: true,
			enableTextSelection: false,
			loadMask: true
		},

		selType: 'rowmodel',
		selModel: {
			mode:'MULTI',
			listeners: {
				beforedeselect : function(rowModel,record,index,eOpts){
				},
				beforeselect : function(rowModel,record,index,eOpts){
				},
				selectionchange : function(selModel,records,eOpts){
				}
			}
		},

		dockedItems: [{
			dock: 'top',
			xtype: 'toolbar',
			items: {
				width: self.panelWidth-14,
				fieldLabel: AgLang.filter,
				labelWidth: 30,
				xtype: 'searchfield',
				selectOnFocus: true,
				store: 'bp3dSearchStore',
				stateful: true,
				stateId: 'bp3d-search-searchfield',
				listeners: {
					beforerender: function(searchfield, eOpt){
					},
					afterrender: function(searchfield, eOpt){
						searchfield.inputEl.set({autocomplete:'on'});
						if(Ext.isEmpty(searchfield.getValue())) return;
						searchfield.onTrigger2Click();
					},
					specialkey: function(field, e, eOpts){
						e.stopPropagation();
					}
				}
			},
			listeners: {
				resize: function(toolbar,width,height,oldWidth,oldHeight,eOpts){
					try{
						var searchfield = toolbar.down('searchfield');
						searchfield.setWidth(toolbar.getWidth()-6);
					}catch(e){
						console.error(e);
					}
				}
			}
		},{
			id: 'bp3d-search-grid-agpagingtoolbar',
			stateId: 'bp3d-search-grid-agpagingtoolbar',
			xtype: 'agpagingtoolbar',
			store: 'bp3dSearchStore',
			dock: 'bottom'
		}],

		listeners: {
			itemclick: {
				fn: function(view,record,item,index,e,eOpts){
				},
				buffer:100
			},
			activate: function(comp,eOpts){
				//render時に定義するactivateイベントがrenderイベント後に発生しない為、空でも定義する
			},
			afterrender: function(field,eOpts){
//				console.log('afterrender():['+field.id+']');
			},
			containercontextmenu : function(view,e,eOpts){
				e.stopEvent();
				return false;
			},
			itemcontextmenu : {
				fn: self.showBp3dItemContextmenu,
				scope: self
			}
		}
	});

	var conceptInfoStore = Ext.data.StoreManager.lookup('conceptInfoStore');
	var conceptInfoRecord = conceptInfoStore.getAt(0);
	var conceptInfoValue = conceptInfoRecord ? conceptInfoRecord.get('ci_id') : null;

	var north_panel_dockedItems = [{
		hidden: false,
		xtype: 'toolbar',
		dock: 'top',
		layout: {
			overflowHandler: 'Menu'
		},
		items:[{
			hidden: conceptInfoStore.getCount()<=1 ? true : false,
			id: 'concept-info-combobox',
			fieldLabel: 'Concept',
			labelWidth: 40,
			width: 100,
			xtype: 'combobox',
			editable: false,
			queryMode: 'local',
			displayField: 'ci_name',
			valueField: 'ci_id',
			value: conceptInfoValue,
			store: conceptInfoStore,
			listeners: {
				afterrender: function(field, eOpts){
//						console.log('afterrender():['+field.id+']');

					if(bp3d_search_grid.rendered){
						bp3d_search_grid.getStore().loadPage(1);
					}else{
						bp3d_search_grid.on('afterrender',function(){bp3d_search_grid.getStore().loadPage(1);},this,{single:true});
					}
					Ext.defer(function(){
						if(self.USE_FMA_OBJ_LINK){
							Ext.data.StoreManager.lookup('fmaAllStore').loadPage(1,{
								callback: function(records,operation,success){
									if(!success) return;
									Ext.getCmp('fma-list-tbbutton').setDisabled(false);
									Ext.getCmp('ag-conflict-button').setDisabled(false);
									Ext.getCmp('all-upload-parts-list-menu').setDisabled(false);
								}
							});
						}else{
							Ext.data.StoreManager.lookup('fmaAllStore').loadPage(1);
							Ext.getCmp('fma-list-tbbutton').setDisabled(false);
							Ext.getCmp('ag-conflict-button').setDisabled(false);
							Ext.getCmp('all-upload-parts-list-menu').setDisabled(false);
						}
					},0);
				},
			}
		},{
			hidden: true,
			disabled:true,
//			id: 'fma-list-tbbutton',
			text: AgLang.all_fma_list,
			iconCls: 'pallet_table',
			menu: [{
//				id: 'all-fma-list-button',
				iconCls: 'pallet_table_list',
				text: AgLang.format_html,
				listeners: {
					click: function(b){
						var w = $(window).width() - 20;
						var h = $(window).height() - 0;
						var p = self.getExtraParams({current_datas:0});
						p.cmd = 'fma-all-list';
						p.title = AgLang.all_fma_list;
						var win = window.open('get-info.cgi?'+ Ext.Object.toQueryString(p),"_blank","width="+w+",height="+h+",dependent=yes,directories=no,menubar=no,resizable=yes,status=no,toolbar=no");
					}
				}
			},{
				hidden: true,
				xtype: 'tbseparator'
			},{
				text: 'Export',
				iconCls: 'pallet_download',
				menu: [{
					text: AgLang.format_excel_xlsx,
					iconCls: 'pallet_xls',
					handler: function(b,e){
						self.export({
							cmd: 'export-fma-all-list',
							format: 'xlsx',
							title: AgLang.all_fma_list + ' [ ' + b.text +' ]',
							iconCls: b.iconCls,
							filename: Ext.util.Format.format('{0}_{1}',AgLang.all_fma_list.replace(Ext.form.field.VTypes.filenameReplaceMask,'_'),Ext.util.Format.date(new Date(),'YmdHis'))
						});
					}
				},{
					text: AgLang.format_excel,
					iconCls: 'pallet_xls',
					handler: function(b,e){
						self.export({
							cmd: 'export-fma-all-list',
							format: 'xls',
							title: AgLang.all_fma_list + ' [ ' + b.text +' ]',
							iconCls: b.iconCls,
							filename: Ext.util.Format.format('{0}_{1}',AgLang.all_fma_list.replace(Ext.form.field.VTypes.filenameReplaceMask,'_'),Ext.util.Format.date(new Date(),'YmdHis'))
						});
					}
				},{
					text: AgLang.format_tsv,
					iconCls: 'pallet_txt',
					handler: function(b,e){
						self.export({
							cmd: 'export-fma-all-list',
							format: 'txt',
							title: AgLang.all_fma_list + ' [ ' + b.text +' ]',
							iconCls: b.iconCls,
							filename: Ext.util.Format.format('{0}_{1}',AgLang.all_fma_list.replace(Ext.form.field.VTypes.filenameReplaceMask,'_'),Ext.util.Format.date(new Date(),'YmdHis'))
						});
					}
				}]
			},{
				disabled:true,
				text: AgLang['import'],
				itemId: 'import',
				iconCls: 'pallet_upload',
				handler: function(b,e){
					var p = self.getExtraParams({current_datas:0});
					delete p.current_datas;
					delete p._ExtVerMajor;
					delete p._ExtVerMinor;
					delete p._ExtVerPatch;
					delete p._ExtVerBuild;
					delete p._ExtVerRelease;
					p.cmd = 'import-fma-all-list';
					self.openImportWindow({
						title: b.text + ' ('+ b.up('button').text +')',
						iconCls: b.iconCls,
						params: p
					});
				}
			}],
			listeners: {
				afterrender: function(b){
				},
				menushow: function(b,menu,eOpts){
					var import_menu = menu.getComponent('import');
					import_menu.setDisabled(false);
				}
			}
		},{
			hidden: true,
			xtype: 'tbseparator'
		},
		{
			hidden: true,
			id: self.MAPPING_MNG_ID+'-btn',
			iconCls: 'gear-btn',
			text: AgLang.mapping_mng,
			enableToggle: true,
			pressed: false,
			listeners: {
				afterrender: function(b){
					var viewport = Ext.getCmp('main-viewport');
					viewport.on('resize',function(){
						var panel = Ext.getCmp('window-panel');
						b.on('toggle', function(b, pressed){
							var window_id = self.MAPPING_MNG_ID;
							var win = Ext.getCmp(window_id);
							if(pressed){
								if(Ext.isEmpty(win)){
									win = self.openMappingMngWin({
										id: window_id,
	//									animateTarget: b.el,
										iconCls: b.iconCls,
										title: b.text,
										constrainHeader: true,
										width: Math.floor(panel.body.getWidth()/3),
										height: panel.body.getHeight()
									});
									panel.add(win);
									win.on('hide', function(){
										if(b.pressed) b.toggle(false);
									});
								}
								win.showAt(0,0);
							}else{
								win.hide();
							}
						});
						if(b.pressed){
							b.fireEvent('toggle',b,true);
						}else{
						}


					},self,{
						single: true,
						delay: 1000
					});
				}
			}
		},{
			hidden: true,
			xtype: 'tbseparator'
		},
		'->',

		{
			hidden: true,
			xtype: 'tbseparator'
		},{
			hidden: true,
			text: AgLang.window,
			iconCls: 'window_alignment',
			listeners: {
				afterrender: function(tbitem){
					var menuitem = Ext.getCmp('menuitem-fma-window');
					if(menuitem.getXType()=='menucheckitem'){
						if(menuitem.checked){
							Ext.defer(function(){
								Ext.getCmp('fma-window').show();
							},1000);
						}
					}else{
//							console.log(Ext.getCmp('fma-window').hidden);
					}
				}
			},
			menu: Ext.create('Ext.menu.Menu', {
				listeners: {
					show: function( menu, eOpts ){
						var menuitem = Ext.getCmp('menuitem-fma-window');
						if(menuitem.getXType() == 'menucheckitem'){
							menuitem.setChecked(Ext.getCmp('fma-window').isVisible(),false);
						}
					}
				},
				items: [{
//						xtype: 'menucheckitem',
					xtype: 'menuitem',
					iconCls: 'pallet_table',
					text: AgLang.fma_window,
					itemId: 'fma-window',
					id: 'menuitem-fma-window',
//						stateful: true,
//						stateId: 'menuitem-fma-window',
//						stateEvents: ['checkchange'],
					listeners: {
						afterrender: function(menuitem){
							if(menuitem.getXType() == 'menucheckitem' && menuitem.stateful){
								menuitem.on('beforestatesave', function(stateful,state,eOpts){
									state.checked = menuitem.checked;
								});
							}
						},
						checkchange: function( menuitem, checked, eOpts ){
							if(menuitem.getXType() != 'menucheckitem') return;
							var fma_window = Ext.getCmp('fma-window');
							var el = menuitem.getEl();
							if(checked){
								fma_window.show(el);
							}else{
								fma_window.hide(el);
							}
						},
						click: function(menuitem){
							if(menuitem.getXType() == 'menucheckitem') return;
							Ext.getCmp('fma-window').show();
						}
					}
				},'-',{
					text: AgLang.window_alignment,
					iconCls: 'window_alignment',
					listeners: {
						click: function(b){
							if(b.isDisabled()) return;
							b.setDisabled(true);
							Ext.getCmp('main-viewport').items.each(function(item,index,len){
								item.setLoading(true);
							});
							Ext.defer(function(){
								arrange_windows(true);
								b.setDisabled(false);
								Ext.getCmp('main-viewport').items.each(function(item,index,len){
									item.setLoading(false);
								});
							},100)
						}
					}
				}]
			})
		}
		]
	}];

	var fma_tab_panel = Ext.create('Ext.tab.Panel',{
		id: 'parts-tab-panel',
		region: 'center',
		border: false,
		items: [
			bp3d_search_grid
		]
	});

	var getCookiesPath = function(){
		return (window.location.pathname.split('/').splice(0,window.location.pathname.split('/').length).join('/'));
	};

	var getCookiesExpires = function(){
		var xDay = new Date;
		xDay.setTime(xDay.getTime() + (30 * 24 * 60 * 60 * 1000)); //30 Days after
		return xDay;
	};

	var all_upload_parts_list_menu = {
		id: 'all-upload-parts-list-menu',
		disabled: true,
		xtype: 'button',
		iconCls: 'pallet_table',
		text: AgLang.all_upload_parts_list,
		tooltip: AgLang.all_upload_parts_list,
		menu: [{
			iconCls: 'pallet_table_list',
			text: AgLang.format_html,
			listeners: {
				click: function(b){
					var w = $(window).width() - 10;
					var h = $(window).height() - 10;
					var p = self.getExtraParams({current_datas:0});
					p.cmd = 'upload-all-list';
					p.title = AgLang.all_upload_parts_list;
					var win = window.open('get-info.cgi?'+ Ext.Object.toQueryString(p),'_blank','width='+w+',height='+h+',dependent=yes,directories=no,menubar=no,resizable=yes,status=no,toolbar=no');
				}
			}
		},'-',{
			text: 'Export',
			iconCls: 'pallet_download',
			menu: [{
				text: AgLang.format_excel_xlsx,
				iconCls: 'pallet_xls',
				handler: function(b,e){
					self.export({
						cmd: 'export-upload-all-list',
						format: 'xlsx',
						title: AgLang.all_upload_parts_list + ' [ ' + b.text +' ]',
						iconCls: b.iconCls,
						filename: Ext.util.Format.format('{0}_{1}',AgLang.all_upload_parts_list.replace(Ext.form.field.VTypes.filenameReplaceMask,'_'),Ext.util.Format.date(new Date(),'YmdHis'))
					});
				}
			},{
				text: AgLang.format_excel,
				iconCls: 'pallet_xls',
				handler: function(b,e){
					self.export({
						cmd: 'export-upload-all-list',
						format: 'xls',
						title: AgLang.all_upload_parts_list + ' [ ' + b.text +' ]',
						iconCls: b.iconCls,
						filename: Ext.util.Format.format('{0}_{1}',AgLang.all_upload_parts_list.replace(Ext.form.field.VTypes.filenameReplaceMask,'_'),Ext.util.Format.date(new Date(),'YmdHis'))
					});
				}
			},{
				text: AgLang.format_tsv,
				iconCls: 'pallet_txt',
				handler: function(b,e){
					self.export({
						cmd: 'export-upload-all-list',
						format: 'txt',
						title: AgLang.all_upload_parts_list + ' [ ' + b.text +' ]',
						iconCls: b.iconCls,
						filename: Ext.util.Format.format('{0}_{1}',AgLang.all_upload_parts_list.replace(Ext.form.field.VTypes.filenameReplaceMask,'_'),Ext.util.Format.date(new Date(),'YmdHis'))
					});
				}
			},'-',{
				text: AgLang.format_zip,
				iconCls: 'pallet_zip',
				handler: function(b,e){
					self.export({
						cmd: 'export-concept-art-map',
						format: 'zip',
						title: b.text,
						iconCls: b.iconCls,
						filename: Ext.util.Format.format('{0}_{1}','mapping',Ext.util.Format.date(new Date(),'YmdHis'))
					});
				}
			}]
		},{
			disabled:true,
			text: AgLang['import'],
			itemId: 'import',
			iconCls: 'pallet_upload',
			menu: [{
				text: AgLang.all_upload_parts_list,
				iconCls: 'pallet_table',
				handler: function(b,e){
					var p = self.getExtraParams({current_datas:0});
					delete p.current_datas;
					delete p._ExtVerMajor;
					delete p._ExtVerMinor;
					delete p._ExtVerPatch;
					delete p._ExtVerBuild;
					delete p._ExtVerRelease;
					p.cmd = 'import-upload-all-list';
					self.openImportWindow({
						title: AgLang['import'] + ' ('+ b.text +')',
						iconCls: b.iconCls,
						params: p
					});
				}
			},'-',{
				text: AgLang.format_zip,
				iconCls: 'pallet_zip',
				handler: function(b,e){
					var p = self.getExtraParams({current_datas:0});
					delete p.current_datas;
					delete p._ExtVerMajor;
					delete p._ExtVerMinor;
					delete p._ExtVerPatch;
					delete p._ExtVerBuild;
					delete p._ExtVerRelease;
					p.cmd = 'import-concept-art-map';
					self.openImportWindow({
						title: AgLang['import'] + ' ('+ b.text +')',
						iconCls: b.iconCls,
						params: p
					});
				}
			}]
		}],
		listeners: {
			render: function(b){
			},
			menushow: function(b,menu,eOpts){
				var import_menu = menu.getComponent('import');
				import_menu.setDisabled(false);
			}
		}
	};

	var update_object_button = {
		disabled: false,
		itemId: 'upload',
		xtype: 'button',
		iconCls: 'pallet_upload',
		text: 'Upload',
		listeners: {
			click: function(b){
				if(!self._uploadWin){

					var originalObjectStore = Ext.data.StoreManager.lookup('originalObjectStore');
					if(Ext.isEmpty(originalObjectStore)){
						originalObjectStore = Ext.create('Ext.data.Store', {
							storeId: 'originalObjectStore',
							model: 'ORIGINAL_OBJECT'
						});
					}

					var dropFileStore = Ext.data.StoreManager.lookup('dropFileStore');
					if(Ext.isEmpty(dropFileStore)){
						dropFileStore = Ext.create('Ext.data.Store', {
							storeId: 'dropFileStore',
							model: 'DROP_FILE',
							proxy: {
								type: 'memory',
								reader: {
									type: 'array'
								}
							}
						});
					}

					self._uploadWin = Ext.create('Ext.window.Window', {
						title: b.text,
						iconCls: b.iconCls,
						closable: true,
//						closeAction: 'hide',
						closeAction: 'destroy',
						modal:true,
//								resizable:false,
						resizable:true,
//								width: 400,
//								minWidth: 350,
//							height: 240,
//								height: 425,
						width: 455,
						minWidth: 455,
						height: 533,
						minHeight: 533,
						layout: 'fit',
						border: false,
						items:[{
							xtype:'form',
							bodyPadding: 5,
							defaults: {
								hideLabel: false,
								labelAlign: 'right',
								labelStyle: 'font-weight:bold;',
								labelWidth: 70
							},
							items: [{
								xtype: 'combobox',
								name: 'prefix_id',
								itemId: 'prefix_id',
								fieldLabel: AgLang.prefix,
								store: 'prefixStore',
								queryMode: 'local',
								displayField: 'display',
								valueField: 'prefix_id',
								value: DEF_PREFIX_ID,
								editable: false
							},{
//								xtype: 'treecombo',
								xtype: 'treepicker',
								name: 'treepicker',
								fieldLabel: 'Folder',
//								store: 'uploadFolderTreePanelStore',
								store: Ext.data.StoreManager.lookup('uploadFolderTreePanelStore'),
								displayField: 'text',
								valueField: 'artf_id',
								editable: false,
								anchor: '100%',
								listeners: {
									select: function(treecombo,record){//,item,index,e,eOpts,records,ids){
//										treecombo.setValue(record.get('artf_id'));
										var formPanel = treecombo.up('form');
										if(record.get('artf_id')){
											formPanel.getComponent('folder_path').setValue(record.getPath('text').replace('//',''));
										}else{
											formPanel.getComponent('folder_path').setValue('/');
										}
										formPanel.getComponent('artf_id').setValue(record.get('artf_id'));
									}
								}
							},{
								xtype: 'hidden',
								name: 'artf_id',
								itemId: 'artf_id'
							},{
								xtype: 'displayfield',
								fieldLabel: 'Folder(full)',
								itemId: 'folder_path'
							},{
								anchor: '100% -70',
								xtype: 'fieldcontainer',
								layout: {
									type: 'vbox',
									align: 'stretch'
								},
								items: [{

									xtype: 'fieldset',
									itemId: 'file_fieldset',
									title: 'Upload Object file',
									minHeight: 100,
									flex: 1,
									layout: {
										type: 'vbox',
										align: 'stretch'
									},
									defaults: {
										hideLabel: false,
										labelAlign: 'right',
										labelStyle: 'font-weight:bold;',
										labelWidth: 70
									},
									listeners: {
										afterrender: function( fieldset, eOpts ){
											var el = fieldset.getEl();
											el.on({
												dragenter: function(event){
													self.fileDragenter(event);
													return false;
												},
												dragover: function(event){
													self.fileDragover(event);
													return false;
												},
												drop: function(event){
													var fieldset = this;
													self.fileDrop(event,{
														callback: Ext.bind(function(files,folders){
	//														console.log(files);
	//														console.log(folders);

															var formPanel = this.up('form');
															var submit_btn = formPanel.getDockedItems('toolbar[dock="bottom"]')[0].getComponent('submit');
															var fieldset = formPanel.down('fieldset#file_fieldset');
															fieldset.getComponent('file_name').setValue('').hide();
															fieldset.getComponent('file_size').setValue('').hide();
															fieldset.getComponent('file_last').setValue('').hide();
															fieldset.getComponent('file_error').hide();
															var file_gridpanel = fieldset.getComponent('file_gridpanel');
															file_gridpanel.hide();

															var file_gridpanel_store = file_gridpanel.getStore();
															var records = [];
															var file_size = 0;
															Ext.each(files,function(file){
																records.push([file.name,file.size,file.lastModifiedDate,file]);
																file_size += file.size;
															});
															file_gridpanel_store.loadRawData(records);
															if(files.length>1){
																file_gridpanel.show();

																var art_org_info_fieldset = formPanel.down('fieldset#art_org_info');
																art_org_info_fieldset.collapse();
																art_org_info_fieldset.hide();

															}else{
																var file = files[0];
																fieldset.getComponent('file_name').setValue(file.name).show();
																fieldset.getComponent('file_size').setValue(Ext.util.Format.fileSize(file.size)).show();
																fieldset.getComponent('file_last').setValue(Ext.util.Format.date(file.lastModifiedDate,self.FORMAT_DATE_TIME)).show();

																formPanel.down('fieldset#art_org_info').show();
															}

															var error = false;
															var error_msg = '';
															if(file_size>DEF_UPLOAD_FILE_MAX_SIZE){
																error = true;
																fieldset.getComponent('file_error').setValue(Ext.String.format(AgLang.error_file_size,Ext.util.Format.fileSize(DEF_UPLOAD_FILE_MAX_SIZE)));
															}
															if(error){
																fieldset.getComponent('file_error').show();
															}else{
																fieldset.getComponent('file_error').hide();
															}
															submit_btn.setDisabled(error);

														},fieldset)
													});
													return false;
												},
												scope: fieldset
											});
										}
									},
									items: [{
										xtype: 'fieldcontainer',
										layout: {
											type: 'hbox',
											align: 'middle'
										},
										items: [{
										xtype: 'filefield',
											name: 'file',
											hideLabel:true,
											buttonOnly: true,
											buttonText: 'Select File...',
											listeners: {
												afterrender: function(field,eOpts){
													if(field.fileInputEl){
														field.fileInputEl.set({'multiple':'multiple'});
													}
												},
												change: function(field,value,eOpts){
													var formPanel = field.up('form');
													var submit_btn = formPanel.getDockedItems('toolbar[dock="bottom"]')[0].getComponent('submit');
													var fieldset = formPanel.down('fieldset#file_fieldset');

													var file_gridpanel = fieldset.getComponent('file_gridpanel');
													var file_gridpanel_store = file_gridpanel.getStore();
													file_gridpanel.hide();
													file_gridpanel_store.removeAll();

													if(field.fileInputEl.dom.files && field.fileInputEl.dom.files.length){
														var file_size = 0;
														var files = field.fileInputEl.dom.files;
														var records = [];
														Ext.each(files,function(file){
															records.push([file.name,file.size,file.lastModifiedDate,file]);
														});
														file_gridpanel_store.loadRawData(records);

														if(files.length>1){
															fieldset.getComponent('file_name').setValue('').hide();
															fieldset.getComponent('file_size').setValue('').hide();
															fieldset.getComponent('file_last').setValue('').hide();
															fieldset.getComponent('file_error').hide();
															file_gridpanel.show();

															var art_org_info_fieldset = formPanel.down('fieldset#art_org_info');
															art_org_info_fieldset.collapse();
															art_org_info_fieldset.hide();
														}
														else{
															var file = files[0];
															fieldset.getComponent('file_name').setValue(file.name).show();
															fieldset.getComponent('file_size').setValue(Ext.util.Format.fileSize(file.size)).show();
															fieldset.getComponent('file_last').setValue(Ext.util.Format.date(file.lastModifiedDate,self.FORMAT_DATE_TIME)).show();

															formPanel.down('fieldset#art_org_info').show();
														}

														var error = false;
														var error_msg = '';
														if(file_size>DEF_UPLOAD_FILE_MAX_SIZE){
															error = true;
															fieldset.getComponent('file_error').setValue(Ext.String.format(AgLang.error_file_size,Ext.util.Format.fileSize(DEF_UPLOAD_FILE_MAX_SIZE)));
														}
														if(error){
															fieldset.getComponent('file_error').show();
														}else{
															fieldset.getComponent('file_error').hide();
														}
														submit_btn.setDisabled(error);
													}else{
														fieldset.getComponent('file_name').setValue('').hide();
														fieldset.getComponent('file_size').setValue('').hide();
														fieldset.getComponent('file_last').setValue('').hide();
														fieldset.getComponent('file_error').hide();
														submit_btn.setDisabled(true);
													}
												}
											}
										},{
											hidden: false,
											xtype: 'label',
											text: 'または、ここにファイル(複数可)'+(Ext.isChrome?'、フォルダ':'')+'をドロップしてください',
											margin: '0 0 0 10'
										}]
									},{
										xtype: 'displayfield',
										fieldLabel: AgLang.file_name,
										itemId: 'file_name'
									},{
										xtype: 'displayfield',
										fieldLabel: AgLang.file_size,
										itemId: 'file_size'
									},{
										hidden: true,
										xtype: 'displayfield',
										fieldLabel: 'ERROR',
										itemId: 'file_error',
										labelStyle: 'font-weight:bold;color:red;',
										fieldStyle: 'color:red;'
									},{
										xtype: 'displayfield',
										fieldLabel: AgLang.timestamp,
										itemId: 'file_last'
									},{
										xtype: 'gridpanel',
										itemId: 'file_gridpanel',
										store: 'dropFileStore',
										flex: 1,
										margin: '0 0 10 0',
										columnLines: true,
										columns: [
											{ xtype: 'rownumberer' },
											{ text: AgLang.file_name, dataIndex: 'name', flex: 1 },
											{ text: AgLang.file_size, dataIndex: 'size', xtype:'agfilesizecolumn', width: 60},
											{ text: AgLang.timestamp, dataIndex: 'lastModified', width:114, xtype:'datecolumn', format: self.FORMAT_DATE_TIME }
										]
									}]
								},{
									xtype: 'fieldset',
									itemId: 'art_org_info',
									title: 'Original Object file Information',
									checkboxToggle: true,
									checkboxName: 'art_org_info',
									collapsed: true,
									collapsible: true,
									height: 244,
									anchor: '100%',
									listeners: {
										collapse: function(fieldset,eOpts){
											fieldset.getComponent('arto_id').setDisabled(true);
											fieldset.getComponent('arto_comment').setDisabled(true);
										},
										expand: function(fieldset,eOpts){
											fieldset.getComponent('arto_id').setDisabled(false);
											fieldset.getComponent('arto_comment').setDisabled(false);
										}
									},
									defaults: {
										labelAlign: 'right',
										labelWidth: 56,
										enableKeyEvents: true,
										selectOnFocus: true
									},
									items: [{
										disabled:true,
										xtype: 'textfield',
										fieldLabel: AgLang.art_ids,
										itemId: 'arto_id',
										name: 'arto_id',
										anchor: '100%',
										emptyText: '複数のIDを指定する場合は、英数字以外の文字で区切ってください。',
										validator: function(value){
											var field = this;
											var fieldset = field.up('fieldset');
											var isExpand = fieldset.checkboxCmp.getValue();
											if(!isExpand){
												return true;
											}
											var rtn = AgLang.error_arto_id;
											if(Ext.isString(value) && value.length){
												var s = Ext.String.trim(value);
												if(Ext.isEmpty(s)){
													return rtn;
												}
											}else if(Ext.isEmpty(value)){
												return true;
											}

											return true;
										},
										listeners: {
											change: function(field,newValue,oldValue,eOpts){

												var fieldset = field.up('fieldset');

												var arto_comment = fieldset.getComponent('arto_comment');
												var gridpanel = field.next('gridpanel');

												var art_id = Ext.String.trim(newValue);
												if(Ext.isEmpty(art_id)){
													originalObjectStore.removeAll();
													field.focus(false);
													return;
												}

												gridpanel.setLoading(true);

												var params = Ext.apply({},self.getExtraParams());
												delete params.current_datas;
												params.cmd = 'read';
												params.art_id = Ext.String.trim(newValue);

												Ext.Ajax.request({
													url: 'get-upload-obj-info.cgi',
													autoAbort: true,
													method: 'POST',
													params: params,
													callback: function(options,success,response){
														gridpanel.setLoading(false);
	//														if(!success) return;
														var json;
														try{json = Ext.decode(response.responseText)}catch(e){};
														if(!success || Ext.isEmpty(json) || Ext.isEmpty(json.success) || !json.success || Ext.isEmpty(json.datas)){
															originalObjectStore.removeAll();
															field.focus(false);
															return;
														}
														var data = json.datas[0];
														originalObjectStore.loadData(json.datas);
														field.validate();
	//														if(field.validate()) arto_comment.focus(false);
														field.focus(false);
													}
												});
											},
											keydown: function(field,e,eOpts){
												e.stopPropagation();
											},
											keypress: function(field,e,eOpts){
												e.stopPropagation();
											},
											keyup: function(field,e,eOpts){
												e.stopPropagation();
											}
										}
									},{
										xtype: 'gridpanel',
										store: Ext.data.StoreManager.lookup('originalObjectStore'),
										columns: [
											{text: AgLang.art_id,    dataIndex: 'art_id',       width:60},
											{text: AgLang.file_name, dataIndex: 'art_filename', flex:1 }
										],
										height: 120,
										anchor: '100%'
									},{
										xtype: 'textareafield',
										fieldLabel: AgLang.comment,
										itemId: 'arto_comment',
										name: 'arto_comment',
										height: 60,
										anchor: '100%',
										margin: '5 0 0 0',
										listeners: {
											keydown: function(field,e,eOpts){
												e.stopPropagation();
											},
											keypress: function(field,e,eOpts){
												e.stopPropagation();
											},
											keyup: function(field,e,eOpts){
												e.stopPropagation();
											}
										}
									}]
								}]
							}],


							buttons: [{
								disabled: true,
								iconCls: 'pallet_upload',
								text: 'Upload',
								itemId: 'submit',
								handler: function() {
									var b = this;
									var form = b.up('form').getForm();
									if(true || form.isValid()){
										b.setDisabled(true);

										var fd = new FormData();
										var values = form.getValues();
										console.log(values);
										fd.append('prefix_id',values.prefix_id);
										fd.append('artf_id',values.artf_id);

										if(Ext.isDefined(values.art_org_info)){
											fd.append('art_org_info',values.art_org_info);
											if(Ext.isString(values.arto_id) && values.arto_id.length) fd.append('arto_id',values.arto_id);
											if(Ext.isString(values.arto_comment) && values.arto_comment.length) fd.append('arto_comment',values.arto_comment);
										}

										var dropFileStore = Ext.data.StoreManager.lookup('dropFileStore');
										if(dropFileStore.getCount()==1){
											fd.append('file',dropFileStore.getAt(0).get('file'));
										}else{
											dropFileStore.each(function(record,i){
												fd.append('file'+(i+1),record.get('file'));
											});
										}
										var file_info = [];
										dropFileStore.each(function(record,i){
										var file = record.get('file');
											file_info.push({
												name: file.name,
												size: file.size,
												last: file.lastModifiedDate.getTime()/1000,
												path: file.__directoryEntry ? file.__directoryEntry.fullPath : null
											});
										});
										fd.append('files',Ext.encode(file_info));

										var _upload_progress = Ext.Msg.show({
											closable : false,
											modal    : true,
											msg      : 'Upload...',
											progress : true,
											title    : 'Upload...'
										});

										$.ajax({
											url: 'upload-object.cgi',
											type: 'POST',
											timeout: 300000,
											data: fd,
											processData: false,
											contentType: false,
											dataType: 'json',
											xhr : function(){
												var XHR = $.ajaxSettings.xhr();
												if(XHR.upload){
													XHR.upload.addEventListener('progress',function(e){
														var value = e.loaded/e.total;
														_upload_progress.updateProgress(value,Math.floor(value*100)+'%','Upload...');
													});
												}
												return XHR;
											}
										})
										.done(function( data, textStatus, jqXHR ){
											_upload_progress.close();
											if(!data.success){
												Ext.Msg.show({
													title: 'Failure',
													msg: data.msg,
													buttons: Ext.Msg.OK,
													icon: Ext.Msg.ERROR
												});
												return;
											}

											var _progress = Ext.Msg.show({
												closable : false,
												modal    : true,
												msg      : 'Uncompress...',
												progress : true,
												title    : 'Upload...',
												autoShow : true
											});
											_progress.center();
											var url = 'upload-object.cgi?'+Ext.Object.toQueryString({sessionID: data.sessionID, mtime: data.mtime, mfmt: data.mfmt});
											var cb = function(json,callback){
												if(Ext.isEmpty(json)) return;
												if(Ext.isObject(json) && Ext.isObject(json.progress) && Ext.isNumber(json.progress.value)){
													var value = json.progress.value;
													if(Ext.isString(value)) value = parseFloat(value);
													_progress.updateProgress(value,Math.floor(value*100)+'%',json.progress.msg);
												}
												var close_progress_title = null;
												var close_progress_icon = null;
												var close_progress_msg = null;
												if(json.progress && Ext.isString(json.progress.msg) && json.progress.msg.toLowerCase()=='end'){
													close_progress_title = 'Success';
													close_progress_icon = Ext.Msg.INFO;
													close_progress_msg = json.file ? 'Your data "' + json.file + '" has been uploaded.' : 'Your data uploaded.';
												}else if(json.progress && Ext.isString(json.progress.msg) && json.progress.msg.toLowerCase().indexOf('error')==0){
													close_progress_title = 'Error';
													close_progress_icon = Ext.Msg.ERROR;
													close_progress_msg = json.progress.msg;
												}else if(Ext.isBoolean(json.success) && !json.success && Ext.isString(json.msg) && json.msg.length){
													close_progress_title = 'Error';
													close_progress_icon = Ext.Msg.ERROR;
													close_progress_msg = json.msg;
												}
												if(callback) (callback)(close_progress_msg?true:false);
												if(close_progress_msg){
													_progress.close();
													Ext.Msg.show({
														title: close_progress_title,
														msg: close_progress_msg,
														buttons: Ext.Msg.OK,
														icon: close_progress_icon
													});
													if(json.file || json.files){
														var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
														uploadObjectStore.loadPage(1);
													}
												}
											};

											if(useEventSource && EventSource){
												var evtSource = new EventSource(url);
												evtSource.onmessage = function(event){
													var json;
													try{json = Ext.decode(event.data)}catch(e){};
													if(json){
														cb(json,function(isEndOrError){if(isEndOrError) event.target.close();});
													}
												};
											}
											else{
												if(Ext.isEmpty(self._TaskRunner)) self._TaskRunner = new Ext.util.TaskRunner();
												var task = self._TaskRunner.newTask({
													run: function () {
														task.stop();
														Ext.Ajax.abort();
														Ext.Ajax.request({
															url: url,
															method: 'GET',
															callback: function(options,success,response){
																task.stop();
																try{json = Ext.decode(response.responseText)}catch(e){};
																if(json){
																	cb(json,function(isEndOrError){if(!isEndOrError) task.start();});
																}
															}
														});
													},
													interval: 1000
												});
												task.start();
											}

										})
										.fail(function( jqXHR, textStatus, errorThrown ){
											console.log(jqXHR);
											console.log(textStatus);
											console.log(errorThrown);
										});

















										return;
										form.submit({
											clientValidation: true,
											url: 'upload-object.cgi',
											waitMsg: 'Uploading your data...',
											success: function(fp, o) {
												if(!o.result.success){
													Ext.Msg.show({
														title: 'Failure',
														msg: o.result.msg,
														buttons: Ext.Msg.OK,
														icon: Ext.Msg.ERROR
													});
													return;
												}
												var _progress = Ext.Msg.show({
													closable : false,
													modal    : true,
													msg      : b.text+'...',
													progress : true,
													title    : b.text+'...'
												});
												var url = 'upload-object.cgi?sessionID='+window.encodeURIComponent(o.result.sessionID);
												var cb = function(json,callback){
													if(Ext.isEmpty(json)) return;

													if(Ext.isObject(json) && Ext.isObject(json.progress) && Ext.isNumeric(json.progress.value)) _progress.updateProgress(json.progress.value,Math.floor(json.progress.value*100)+'%',json.progress.msg);
													_progress.center();
													var close_progress_title = null;
													var close_progress_icon = null;
													var close_progress_msg = null;
													if(json.progress && Ext.isString(json.progress.msg) && json.progress.msg.toLowerCase()=='end'){
														close_progress_title = 'Success';
														close_progress_icon = Ext.Msg.INFO;
														close_progress_msg = 'Your data "' + json.file + '" has been uploaded.';
													}else if(json.progress && Ext.isString(json.progress.msg) && json.progress.msg.toLowerCase().indexOf('error')==0){
														close_progress_title = 'Error';
														close_progress_icon = Ext.Msg.ERROR;
														close_progress_msg = json.progress.msg;
													}else if(Ext.isBoolean(json.success) && !json.success && Ext.isString(json.msg) && json.msg.length){
														close_progress_title = 'Error';
														close_progress_icon = Ext.Msg.ERROR;
														close_progress_msg = json.msg;
													}
													if(callback) (callback)(close_progress_msg?true:false);
													if(close_progress_msg){
														_progress.close();
//														Ext.Msg.alert(close_progress_title, close_progress_msg);
														Ext.Msg.show({
															title: close_progress_title,
															msg: close_progress_msg,
															buttons: Ext.Msg.OK,
															icon: close_progress_icon
														});
														if(json.file){
															var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
															uploadObjectStore.loadPage(1);
														}
														self._uploadWin.hide();
													}
												};

												if(useEventSource && EventSource){
													var evtSource = new EventSource(url);
													evtSource.onmessage = function(event){
														var json;
														try{json = Ext.decode(event.data)}catch(e){};
														if(json){
															cb(json,function(isEndOrError){if(isEndOrError) event.target.close();});
														}
													};
												}
												else{
													if(Ext.isEmpty(self._TaskRunner)) self._TaskRunner = new Ext.util.TaskRunner();
													var task = self._TaskRunner.newTask({
														run: function () {
															task.stop();
															Ext.Ajax.abort();
															Ext.Ajax.request({
																url: url,
																method: 'GET',
																callback: function(options,success,response){
																	task.stop();
																	try{json = Ext.decode(response.responseText)}catch(e){};
																	if(json){
																		cb(json,function(isEndOrError){if(!isEndOrError) task.start();});
																	}
																}
															});
														},
														interval: 1000
													});
													task.start();
												}
											},
											failure: function(form, action) {
//													self._uploadWin.hide();
												b.setDisabled(false);
												switch (action.failureType) {
													case Ext.form.action.Action.CLIENT_INVALID:
														Ext.Msg.show({
															title: 'Failure',
															msg: 'Form fields may not be submitted with invalid values',
															buttons: Ext.Msg.OK,
															icon: Ext.Msg.ERROR
														});
														break;
													case Ext.form.action.Action.CONNECT_FAILURE:
														Ext.Msg.show({
															title: 'Failure',
															msg: 'Ajax communication failed',
															buttons: Ext.Msg.OK,
															icon: Ext.Msg.ERROR
														});
														break;
													case Ext.form.action.Action.SERVER_INVALID:
														Ext.Msg.show({
															title: 'Failure',
															msg: action.result.msg,
															buttons: Ext.Msg.OK,
															icon: Ext.Msg.ERROR
														});
												}
											}
										});
									}
								}
							}],
							listeners: {
								show: function(comp){
								}
							}
						}],
						listeners: {
							show: function(comp){
								var folder_tree = Ext.getCmp('upload-folder-tree');
								var node = folder_tree.getSelectionModel().getSelection()[0] || folder_tree.getRootNode();
//								var treecombo = comp.down('treecombo');
								var treecombo = comp.down('treepicker');
								if(treecombo){
									treecombo.setValue(node.getId());
									treecombo.fireEvent('select',treecombo,node);
//									var formPanel = treecombo.up('form');
//									if(node.get('artf_id')){
//										formPanel.getComponent('folder_path').setValue(node.getPath('text').replace('//',''));
//									}else{
//										formPanel.getComponent('folder_path').setValue('/');
//									}
								}
								var formPanel = comp.down('form');
								formPanel.getComponent('prefix_id').setValue(DEF_PREFIX_ID);

								var fieldset = formPanel.down('fieldset#file_fieldset');
								fieldset.getComponent('file_name').hide();
								fieldset.getComponent('file_size').hide();
								fieldset.getComponent('file_last').hide();


								fieldset.getComponent('file_gridpanel').hide();
							},
							hide: function(comp){
								var formPanel = comp.down('form');
								formPanel.getForm().reset();
								formPanel.getDockedItems('toolbar[dock="bottom"]')[0].getComponent('submit').setDisabled(true);

								var fieldset = formPanel.down('fieldset#file_fieldset');
								fieldset.getComponent('file_error').hide();
							},
							destroy: function(comp){
								delete self._uploadWin;
							}
						}
					});
				}
				self._uploadWin.show();
			}
		}
	};

	upload_object_grid = Ext.create('Ext.ag.GridPanel',{
//		title: self.TITLE_UPLOAD_OBJECT,
		id: 'upload-object-grid',
		region: 'center',
//		region: 'south',
//		split: true,
//		height: self.panelHeight-100,
//		height: 250,
		flex: 2,
		minHeight: 150,
		columnLines: true,
		store: 'uploadObjectStore',
		stateful: true,
		stateId: 'upload-object-grid',
		plugins: [self.getCellEditing(),self.getBufferedRenderer()],
		columns: [
			{text: '&#160;',            dataIndex: 'selected',     stateId: 'selected',      width: 30, minWidth: 30, hidden: false, hideable: false, sortable: true, draggable: false, resizable: false, xtype: 'agselectedcheckcolumn'},

			{
				text: AgLang.current,      dataIndex: 'current_use',       stateId: 'current_use',        width: 46, minWidth: 46, hidden: false, hideable: false, sortable: false, draggable: false, resizable: false,
				renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
					var tdCls = [];
					if(value){
						tdCls.push('gridcolumn_current_use');
					}
					else if(Ext.isEmpty(record.get('cdi_name'))){
						metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(self.TOOLTIP_FMAID_NOT_SUPPORTED) + '"';
					}
					else{
						tdCls.push('gridcolumn_current_none_use');
						if(Ext.isString(record.get('current_use_reason'))) metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(record.get('current_use_reason')) + '"';
					}
					if(Ext.isString(metaData.tdCls) && metaData.tdCls.length){
						metaData.tdCls += ' ' + tdCls.join(' ');
					}else{
						metaData.tdCls = tdCls.join(' ');
					}
					return '';
				}
			},

			{
				text: '&#160;',            dataIndex: 'art_tmb_path',     stateId: 'art_tmb_path',      width: 24, minWidth: 24, hidden: false, hideable: false, sortable: false, draggable: false, resizable: false,
				renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
					if(record.data.seg_color){
//						metaData.style = 'background:'+record.data.seg_color+';';
					}
					metaData.innerCls = 'art_tmb_path';
					return value;
				}
			},

			{text: AgLang.art_id,       dataIndex: 'art_id',       stateId: 'art_id',        width: 60, minWidth: 60, hidden: true, hideable: false},
			{text: AgLang.art_id,       dataIndex: 'artc_id',      stateId: 'artc_id',       width: 60, minWidth: 60, hidden: false, hideable: true},
			{text: AgLang.cdi_name,     dataIndex: 'cdi_name',     stateId: 'cdi_name',      width: 80, minWidth: 80, hidden: true,  hideable: true, xtype: 'agcolumncdiname' },

			{text: AgLang.cmp_abbr,     dataIndex: 'cmp_id',       stateId: 'cmp_id',        width: 40, minWidth: 40, hidden: true,  hideable: false, xtype: 'agcolumnconceptartmappart' },
			{text: AgLang.cp_abbr,      dataIndex: 'cp_id',        stateId: 'cp_id',         width: 40, minWidth: 40, hidden: true,  hideable: true, xtype: 'agcolumnconceptpart' },
			{text: AgLang.cl_abbr,      dataIndex: 'cl_id',        stateId: 'cl_id',         width: 40, minWidth: 40, hidden: true,  hideable: true, xtype: 'agcolumnconceptlaterality' },

			{text: AgLang.cdi_name_e,   dataIndex: 'cdi_name_e',   stateId: 'cdi_name_e',    flex: 2.0, minWidth: 80, hidden: true,  hideable: true, xtype: 'agcolumncdinamee' },

			{text: 'System',            dataIndex: 'seg_name',     stateId: 'seg_name',      flex: 1.0, minWidth: 50, hidden: true,  hideable: true,  xtype: 'agsystemcolumn'},

			{text: AgLang.category,     dataIndex: 'arta_category',stateId: 'arta_category', flex: 1.0, minWidth: 50, hidden: false, hideable: true},
			{text: AgLang.class_name,   dataIndex: 'arta_class',   stateId: 'arta_class',    width: 36, minWidth: 36, hidden: false, hideable: true},
			{text: AgLang.comment,      dataIndex: 'arta_comment', stateId: 'arta_comment',  flex: 2.0, minWidth: 80, hidden: false, hideable: true},
			{text: AgLang.judge,        dataIndex: 'arta_judge',   stateId: 'arta_judge',    flex: 1.0, minWidth: 50, hidden: false, hideable: true},

			{text: AgLang.arto_id,      dataIndex: 'arto_id',      stateId: 'arto_id',       width: 60, minWidth: 60, hidden: true, hideable: true, sortable: false},
			{text: AgLang.arto_filename,dataIndex: 'arto_filename',stateId: 'arto_filename', flex: 2.0, minWidth: 80, hidden: true, hideable: true, sortable: false},
			{text: AgLang.arto_comment, dataIndex: 'arto_comment', stateId: 'arto_comment',  flex: 2.0, minWidth: 80, hidden: true, hideable: true, sortable: false},

			{text: 'Color',             dataIndex: 'color',        stateId: 'color',         width: 40, minWidth: 40, hidden: true,  hideable: false,  xtype: 'agcolorcolumn'},
			{text: 'Opacity',           dataIndex: 'opacity',      stateId: 'opacity',       width: 44, minWidth: 44, hidden: true,  hideable: false,  xtype: 'agopacitycolumn'},
			{text: 'Hide',              dataIndex: 'remove',       stateId: 'remove',        width: 40, minWidth: 40, hidden: true,  hideable: false,  xtype: 'agcheckcolumn'},
			{text: 'Scalar',            dataIndex: 'scalar',       stateId: 'scalar',        width: 40, minWidth: 40, hidden: true,  hideable: false,  xtype: 'agnumbercolumn', format: '0', editor: 'numberfield'},

			{text: AgLang.file_name,    dataIndex: 'art_filename', stateId: 'art_filename',  flex: 2.0, minWidth: 80, hidden: false, hideable: true},
			{text: 'Path',              dataIndex: 'art_path',     stateId: 'art_path',      flex: 1.0, minWidth: 50, hidden: true,  hideable: false},
			{text: AgLang.file_size,    dataIndex: 'art_data_size',stateId: 'art_data_size', width: 59,  hidden: true, hideable: true, xtype: 'agfilesizecolumn'},

			{text: AgLang.xmax,         dataIndex: 'art_xmax',     stateId: 'art_xmax',      width: 59,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.xmin,         dataIndex: 'art_xmin',     stateId: 'art_xmin',      width: 59,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.xcenter,      dataIndex: 'art_xcenter',  stateId: 'art_xcenter',   width: 59,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.ymax,         dataIndex: 'art_ymax',     stateId: 'art_ymax',      width: 59,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.ymin,         dataIndex: 'art_ymin',     stateId: 'art_ymin',      width: 59,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.ycenter,      dataIndex: 'art_ycenter',  stateId: 'art_ycenter',   width: 59,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.zmax,         dataIndex: 'art_zmax',     stateId: 'art_zmax',      width: 59,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.zmin,         dataIndex: 'art_zmin',     stateId: 'art_zmin',      width: 59,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.zcenter,      dataIndex: 'art_zcenter',  stateId: 'art_zcenter',   width: 59,  hidden: false, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.volume,       dataIndex: 'art_volume',   stateId: 'art_volume',    width: 59,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},

			{text: AgLang.timestamp,    dataIndex: 'art_timestamp',stateId: 'art_timestamp', width: self.ART_TIMESTAMP_WIDTH,  hidden: false, hideable: true, xtype: 'datecolumn',     format: self.ART_TIMESTAMP_FORMAT },
			{text: AgLang.upload_modified, dataIndex: 'art_upload_modified',stateId: 'art_upload_modified', width: 112,  hidden: false, hideable: true, xtype: 'datecolumn',     format: self.FORMAT_DATE_TIME }
		],

		viewConfig: {
			stripeRows:true,
			enableTextSelection:false,
			loadMask:true,
			allowCopy: true,
			plugins: [{
				ddGroup: 'dd-upload_folder_tree',
				ptype: 'gridviewdragdrop',
				enableDrop: false
			}]
		},
		selType: 'rowmodel',
		selModel: {
			mode:'MULTI'
		},

		dockedItems: [{
			xtype: 'toolbar',
			dock: 'top',
			layout: {
				overflowHandler: 'Menu'
			},
			items:[{
				xtype: 'tbtext',
				text: '<b>'+self.TITLE_UPLOAD_OBJECT+'</b>'
			},'-',{
				xtype: 'button',
				iconCls: 'pallet_checked',
				text: 'check all',
				listeners: {
					click: function(b){
						upload_object_grid.setLoading(true);
						pallet_grid.setLoading(true);
						b.setDisabled(true);
						Ext.defer(function(){
							try{
								var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
								var proxy = uploadObjectStore.getProxy();
								var params = Ext.Object.merge({},proxy.extraParams || {},{select_all: true});

								Ext.Ajax.request({
									url: proxy.api.read,
									method: proxy.actionMethods.read,
									timeout: proxy.timeout,
									params: params,
									callback: function(options,success,response){
										var json;
										try{json = Ext.decode(response.responseText)}catch(e){};
										if(success==false || Ext.isEmpty(json) || Ext.isEmpty(json.success) || json.success==false || Ext.isEmpty(json.datas) || !Ext.isArray(json.datas)){
											if(Ext.isEmpty(json) || Ext.isEmpty(json.msg)) return;
											Ext.Msg.show({
												title: title,
												msg: json.msg,
												buttons: Ext.Msg.OK,
												icon: Ext.Msg.ERROR
											});
										}else{
											var palletPartsStore = Ext.data.StoreManager.lookup('palletPartsStore');
											var records = [];
											Ext.each(json.datas,function(data){
												if(palletPartsStore.findRecord('art_id',data.art_id,0,false,false,true)!==null) return true;
												records.push(data);
											});
											var view = Ext.getCmp('pallet-grid').getView();
											var sorters = palletPartsStore.sorters.getRange();
											if(sorters.length){
												palletPartsStore.sorters.clear();
												view.headerCt.clearOtherSortStates()
											}
											view.getSelectionModel().select(palletPartsStore.add(records));
											if(sorters.length){
												palletPartsStore.sorters.addAll(sorters);
												palletPartsStore.sort();
											}

										}
										upload_object_grid.setLoading(false);
										pallet_grid.setLoading(false);
										b.setDisabled(false);
									}
								});

								uploadObjectStore.suspendEvents(false);
								try{
									uploadObjectStore.each(function(r,i,a){
										if(r.get('selected')) return true;
										r.beginEdit();
										r.set('selected',true)
										r.commit(true);
										r.endEdit(true,['selected']);
									});
								}catch(e){console.error(e);}
								uploadObjectStore.resumeEvents();
								upload_object_grid.getView().refresh();

							}catch(e){
								console.error(e);
								upload_object_grid.setLoading(false);
								pallet_grid.setLoading(false);
								b.setDisabled(false);
							}
						},10);
					}
				}
			},'-',{
				xtype: 'button',
				iconCls: 'pallet_unchecked',
				text: 'uncheck all',
				listeners: {
					click: function(b){
						upload_object_grid.setLoading(true);
						pallet_grid.setLoading(true);
						b.setDisabled(true);
						Ext.defer(function(){
							try{
								var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
								var proxy = uploadObjectStore.getProxy();
								var params = Ext.Object.merge({},proxy.extraParams || {});

								Ext.Ajax.request({
									url: proxy.api.read,
									method: proxy.actionMethods.read,
									timeout: proxy.timeout,
									params: params,
									callback: function(options,success,response){
										var json;
										try{json = Ext.decode(response.responseText)}catch(e){};
										if(success==false || Ext.isEmpty(json) || Ext.isEmpty(json.success) || json.success==false || Ext.isEmpty(json.datas) || !Ext.isArray(json.datas)){
											if(Ext.isEmpty(json) || Ext.isEmpty(json.msg)) return;
											Ext.Msg.show({
												title: title,
												msg: json.msg,
												buttons: Ext.Msg.OK,
												icon: Ext.Msg.ERROR
											});
										}else{
//											console.log(json.total);
											var palletPartsStore = Ext.data.StoreManager.lookup('palletPartsStore');
											var records = [];
											Ext.each(json.datas,function(data){
												var record = palletPartsStore.findRecord('art_id',data.art_id,0,false,false,true);
												if(Ext.isObject(record)) records.push(record);
											});
											palletPartsStore.remove(records);
										}
										upload_object_grid.setLoading(false);
										pallet_grid.setLoading(false);
										b.setDisabled(false);
									}
								});

								uploadObjectStore.suspendEvents(false);
								try{
									uploadObjectStore.each(function(r,i,a){
										if(!r.get('selected')) return true;
										r.beginEdit();
										r.set('selected',false)
										r.commit(true);
										r.endEdit(true,['selected']);
									});
								}catch(e){console.error(e);}
								uploadObjectStore.resumeEvents();
								upload_object_grid.getView().refresh();

							}catch(e){
								upload_object_grid.setLoading(false);
								pallet_grid.setLoading(false);
								b.setDisabled(false);
							}
						},100);
					}
				}
			},

			{
				hidden: true,
				xtype: 'tbseparator',
			},{
				hidden: true,
				disabled: true,
				xtype: 'tbtext',
				text: 'Move Selected Obj(s) To'
			},{
				hidden: true,
				disabled: true,
				id: 'moveFolderCombo',
				itemId: 'moveFolder',
				iconCls: 'tfolder_property',
				xtype: 'treepicker',
				store: Ext.data.StoreManager.lookup('uploadFolderTreePanelStore'),
				editable: false,
				displayField: 'text',
				valueField: 'artf_id',
				width: 100,
				listeners: {
					select: function(treecombo,record){
						var grid = treecombo.up('grid');
						var records = grid ? grid.getSelectionModel().getSelection() : [];
						if(Ext.isEmpty(records)) return;
						changeUploadFolder(record,records);
					}
				}
			},

			'-',' ','-',{
				itemId: 'download',
				xtype: 'button',
				tooltip: 'Download Selected',
				iconCls: 'pallet_download',
				disabled:true,
				listeners: {
					click: function(b){
						b.setDisabled(true);

						var gridpanel = b.up('gridpanel');
						var selModel = gridpanel.getSelectionModel();
						var recs = selModel.getSelection();
						if(Ext.isEmpty(recs)){
							b.setDisabled(false);
							return;
						}
						selModel.deselectAll();
						selModel.select(recs);
						b.setDisabled(true);

						self.downloadObjectsTask.delay(10,self.downloadObjects,self,[{
							type: 'objects',
							records: recs,
							callback: function(){
								b.setDisabled(false);
							}
						}]);
					}
				}
			},

			'-',' ','-',{
				itemId: 'edit',
				xtype: 'button',
				tooltip: 'Edit',
				iconCls: 'package_edit-btn',
				disabled:true,
				listeners: {
					click: function(b){
						b.setDisabled(true);

						var gridpanel = b.up('gridpanel');
						var selModel = gridpanel.getSelectionModel();
						var records = selModel.getSelection();
						if(Ext.isEmpty(selModel)){
//							b.setDisabled(true);
							return;
						}
						selModel.deselectAll();
						selModel.select(records);
						b.setDisabled(true);

/*
						self.downloadObjectsTask.delay(10,self.downloadObjects,self,[{
							type: 'objects',
							records: records,
							callback: function(){
								b.setDisabled(false);
							}
						}]);
*/

						var nodes = gridpanel.getView().getSelectedNodes();
//						console.log(nodes);

						var animateTarget = Ext.get(nodes[0]);
						Ext.create('Ext.ag.ObjInfoEditWindow', {
							animateTarget: animateTarget,
							iconCls: b.iconCls,
							title: b.tooltip,
							modal: true,
							records: records,
						}).show(
							animateTarget,
							function(){
								b.setDisabled(false);
							}
						);


					}
				}
			},

			'-','->','-',{
				itemId: 'delete',
				xtype: 'button',
				tooltip: 'Delete Selected',
				iconCls: 'pallet_delete',
				disabled:true,
				listeners: {
					click: function(b){
						b.setDisabled(true);

						var gridpanel = b.up('gridpanel');
						var store = gridpanel.getStore();
						var selModel = gridpanel.getSelectionModel();
						var records = selModel.getSelection();
						if(Ext.isEmpty(records)){
							b.setDisabled(false);
							return;
						}

						var remove_records = records;
						selModel.deselectAll();

						var delete_cdi_names = remove_records.filter(function(record,index,array){
							return Ext.isEmpty(record.get('cdi_name')) ? false : true;
						});

						selModel.select(remove_records);

						var msg = '';
						if(delete_cdi_names.length){
							msg += 'FMAIDに対応済みのデータが含まれています。<br>';
							var t = ['<div style="max-height:10em;overflow:auto;margin:0.5em 0em;padding-left:1em;background:white;"><table>'];
							delete_cdi_names.forEach(function(r){
								t.push('<tr>');
								var tr = [];
								['art_id','cdi_name'].forEach(function(v){
									tr.push('<td>'+r.get(v)+'</td>');
								});
								t.push(tr.join('<td>:</td>'));
								t.push('</tr>');
							});
							t.push('</table></div>');
							msg += t.join('');
						}
						msg += '選択されているアップロードデータを削除してよろしいですか？';

						Ext.Msg.show({
							title: b.text || 'Delete',
							iconCls: b.iconCls,
							msg: msg,
							animateTarget: b.el,
							buttons: Ext.Msg.YESNO,
							icon: Ext.Msg.QUESTION,
							defaultFocus: 'no',
							fn: function(buttonId,text,opt){
								if(buttonId != 'yes'){
									b.setDisabled(false);
									return;
								}

								if(!self.beforeloadStore(store)) return;
								var p = store.getProxy();
								p.extraParams = p.extraParams || {};
								delete p.extraParams.current_datas;
								delete p.extraParams.model;
								delete p.extraParams.version;
								delete p.extraParams.ag_data;
								delete p.extraParams.tree;
								delete p.extraParams._ExtVerMajor;
								delete p.extraParams._ExtVerMinor;
								delete p.extraParams._ExtVerPatch;
								delete p.extraParams._ExtVerBuild;
								delete p.extraParams._ExtVerRelease;

								store.remove(remove_records);
								store.sync({
									callback: function(batch,options){
										b.setDisabled(false);
									},
									success: function(batch,options){
										var palletPartsStore = Ext.data.StoreManager.lookup('palletPartsStore');
										palletPartsStore.suspendEvents(true);
										var find_recs = [];
										Ext.each(remove_records,function(r,i,a){
											var find_idx = palletPartsStore.findBy(function(record){
											 return record.get('art_id')===r.get('art_id') && record.get('artf_id')===r.get('artf_id');
											});
											if(find_idx<0) return true;
											var find_rec = palletPartsStore.getAt(find_idx);
											if(find_rec) find_recs.push(find_rec);
										});
										if(find_recs.length) palletPartsStore.remove(find_recs);
										palletPartsStore.resumeEvents();
										Ext.getCmp('pallet-grid').getView().refresh();

										var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
										uploadObjectStore.loadPage(1);
										if(self.syncMappingMngStore) self.syncMappingMngStore();
									},
									failure: function(batch,options){
										var msg = AgLang.error_delete;
										var proxy = this;
										var reader = proxy.getReader();
										if(reader && reader.rawData && reader.rawData.msg){
											msg += ' ['+reader.rawData.msg+']';
										}
										Ext.Msg.show({
											title: b.text || 'Delete',
											iconCls: b.iconCls,
											msg: msg,
											buttons: Ext.Msg.OK,
											icon: Ext.Msg.ERROR,
											fn: function(buttonId,text,opt){
											}
										});
										store.rejectChanges();
										selModel.select(remove_records);
									}
								});
							}
						});

					}
				}
			}


			]
		},{
			id: 'upload-object-grid-agpagingtoolbar',
			stateId: 'upload-object-grid-agpagingtoolbar',
			xtype: 'agpagingtoolbar',
			store: 'uploadObjectStore',
			dock: 'bottom'
		}],
		listeners: {
			selectionchange: function(selModel,selected,eOpts){
				var grid = this;
				var toolbar = selModel.view.up('gridpanel').getDockedItems('toolbar[dock="top"]')[0];
				var disabled = Ext.isEmpty(selected);
				toolbar.getComponent('download').setDisabled(disabled);
				toolbar.getComponent('edit').setDisabled(disabled);
				toolbar.getComponent('delete').setDisabled(disabled);
				toolbar.getComponent('moveFolder').setDisabled(disabled);
			},
			afterrender: function(gridpanel){
				if(Ext.isChrome){
					gridpanel.columns.forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
					gridpanel.getStore().on('load',function(){
						gridpanel.columns.forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
					});
				}
			},
			containercontextmenu : function(view,e,eOpts){
				e.stopEvent();
				return false;
			},
			itemcontextmenu: {
				fn: self.showPalletItemContextmenu,
				scope: self
			}
		}
	});

	//palletPartsStoreをlocalStorageの内容で初期化
	if(self.AgLocalStorage.exists(self.DEF_LOCALDB_HASH_KEY)){
		var records = [];
		try{records = Ext.decode(self.AgLocalStorage.load(self.DEF_LOCALDB_HASH_KEY))}catch(e){};

		var palletPartsStore = Ext.data.StoreManager.lookup('palletPartsStore');
		var add_records = [];

		Ext.iterate(records,function(record,index,allItems){
			var n_record = Ext.create(Ext.getClassName(palletPartsStore.model),{});
			var modifiedFieldNames = [];
			n_record.beginEdit();
			for(var key in n_record.data){
				if(Ext.isDate(n_record.data[key]) || n_record.fields.map[key].type.type=='date'){
					var date = new Date();
					date.setTime(record[key]);
					n_record.set(key,date);
				}else{
					n_record.set(key,record[key]);
				}
				modifiedFieldNames.push(key);
			}
			n_record.commit(false);
			n_record.endEdit(false,modifiedFieldNames);
			add_records.push(n_record);
		});
		if(add_records.length){
			palletPartsStore.suspendEvents(false);
			try{palletPartsStore.add(add_records);}catch(e){console.error(e);}
			palletPartsStore.resumeEvents();
			palletPartsStore.fireEvent('datachanged',palletPartsStore);
			self.updateArtInfo();
		}
	}

	var pallet_grid = Ext.create('Ext.ag.GridPanel',{
		hidden: self.PALLET_PANEL_HIDDEN,
		id: 'pallet-grid',
		region: 'south',
		title: 'Pallet',
		split: true,
//		height: self.panelHeight,
		height: 250,
		minHeight: 250,
//		flex: 1,
		columnLines: true,
		store: 'palletPartsStore',
		stateful: true,
		stateId: 'pallet-grid',
		plugins: [Ext.create('Ext.grid.plugin.CellEditing', {
			clicksToEdit: 1,
			listeners: {
				beforeedit: function(editor,e,eOpts){
					if(e.field=='cdi_name' || e.field=='cmp_id'){
						var button = Ext.getCmp('ag-pallet-fma-obj-link-button');
						if(!button || !button.rendered || button.disabled || !button.pressed) e.cancel = true;
					}
				},
				edit: function(editor,e,eOpts){
					var gridpanel = this.grid;
					var selModel = gridpanel.getSelectionModel();
					var isCommit = false;
					if(e.field=='cdi_name'){
						if(Ext.isString(e.record.getChanges()['cdi_name'])){
							var cdi_name = Ext.String.trim(e.record.getChanges()['cdi_name'] || e.record.get('cdi_name') || '');
							var cdi_name_e = null;
							var cmp_id = e.record.getChanges()['cmp_id'] || e.record.get('cmp_id') || 0;
							if(cdi_name.length){

								var m = self.regexpIsSubclassCdiName.exec(cdi_name);
								if(Ext.isArray(m) && m.length){
									var tmp_cdi_name = m[1];
									var cmp_abbr = m[2].toUpperCase();
									cdi_name = tmp_cdi_name;
									var conceptArtMapPartStore = Ext.data.StoreManager.lookup('conceptArtMapPartStore');
									var cmp_record = conceptArtMapPartStore.findRecord('cmp_abbr', cmp_abbr, 0, false, false, true );
									if(cmp_record) cmp_id = cmp_record.get('cmp_id');
								}

								var fmaAllStore = Ext.data.StoreManager.lookup('fmaAllStore');
								var record = fmaAllStore.findRecord('cdi_name', cdi_name, 0, false, false, true );
								if(Ext.isEmpty(record)){
									e.record.reject();
									Ext.Msg.show({
										title: 'Error',
										msg: 'Unknown FMAID ['+ cdi_name +']',
										buttons: Ext.Msg.OK,
										icon: Ext.Msg.ERROR
									});
									return false;
								}else{
									cdi_name = record.get('cdi_name');
									cdi_name_e = record.get('cdi_name_e');
								}
							}else{
								cdi_name = null;
								if(cdi_name) cdi_name_e = e.record.get('cdi_name_e');
							}
							e.record.set('cmp_id', cmp_id);

							//サーバに更新を反映するし、成功したら下の処理を実行
							var extraParams = self.getExtraParams();
							delete extraParams.ag_data;
							delete extraParams.current_datas;
							delete extraParams.model;
							delete extraParams.tree;
							delete extraParams.version;

							var art_id = e.record.get('art_id');

							extraParams.datas = Ext.encode([{
								art_id: art_id,
								cdi_name: cdi_name,
								cmp_id: cmp_id,
								cm_use: !Ext.isEmpty(cdi_name)
							}]);
							extraParams.comment = AgLang.fma_corresponding_change;

							Ext.Ajax.request({
								url: 'api-upload-file-list.cgi?cmd=update_concept_art_map',
								method: 'POST',
								params: extraParams,
								callback: function(options,success,response){
									if(!success){
										Ext.Msg.show({
											title: AgLang.fma_corresponding_change,
											msg: '['+response.status+'] '+response.statusText,
											iconCls: 'pallet_link',
											icon: Ext.Msg.ERROR,
											buttons: Ext.Msg.OK
										});
										e.record.reject();
										selModel.fireEvent('selectionchange', selModel,selModel.getSelection());
										return;
									}

									var json;
									try{json = Ext.decode(response.responseText)}catch(e){};
									if(Ext.isEmpty(json) || !json.success){
										var msg = 'Unknown error!!';
										if(Ext.isObject(json) && json.msg) msg = json.msg;
										Ext.Msg.show({
											title: AgLang.fma_corresponding_change,
											msg: msg,
											iconCls: 'pallet_link',
											icon: Ext.Msg.ERROR,
											buttons: Ext.Msg.OK
										});
										e.record.reject();
										selModel.fireEvent('selectionchange', selModel,selModel.getSelection());
										return;
									}

									e.record.beginEdit();
									e.record.set('cdi_name', cdi_name);
									e.record.set('cdi_name_e', cdi_name_e);
									e.record.set('cmp_id', cmp_id);
									e.record.endEdit(false,['cdi_name','cdi_name_e','cmp_id']);
									e.record.commit(false,['cdi_name','cdi_name_e','cmp_id']);

									if(self.syncMappingMngStore) self.syncMappingMngStore([e.record]);
									if(self.syncUploadObjectStore) self.syncUploadObjectStore([e.record]);
									if(self.syncPickSearchStore) self.syncPickSearchStore([e.record]);

									Ext.getCmp('pallet-grid').getView().refresh();
									selModel.fireEvent('selectionchange', selModel,selModel.getSelection());
								}
							});
							return;

						}
					}else{
						Ext.Object.each(e.record.getChanges(),function(key,value,object){
							isCommit = true;
							return false;
						});
					}
					if(isCommit) e.record.commit();
				}
			}
		}),self.getBufferedRenderer()],
		columns: [

			{
				text: AgLang.current,      dataIndex: 'current_use',       stateId: 'current_use',        width: 46, minWidth: 46, hidden: false, hideable: false, sortable: false, draggable: false, resizable: false,
				renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
					var tdCls = [];
//					console.log(value,record.get('current_use_reason'));
					if(value){
						tdCls.push('gridcolumn_current_use');
					}
					else if(Ext.isEmpty(record.get('cdi_name'))){
						metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(self.TOOLTIP_FMAID_NOT_SUPPORTED) + '"';
					}
					else{
						tdCls.push('gridcolumn_current_none_use');
						if(Ext.isString(record.get('current_use_reason'))) metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(record.get('current_use_reason')) + '"';
					}
					if(Ext.isString(metaData.tdCls) && metaData.tdCls.length){
						metaData.tdCls += ' ' + tdCls.join(' ');
					}else{
						metaData.tdCls = tdCls.join(' ');
					}
					return '';
				}
			},
			{
				text: AgLang.edited,      dataIndex: 'cm_edited',       stateId: 'cm_edited',        width: 46, minWidth: 46, hidden: self.getHiddenEditedGridColumn(), hideable: false, sortable: true, draggable: false, resizable: false
				,renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
					var tdCls = [];
					if(value){
						tdCls.push('gridcolumn_current_use');
					}else{
						tdCls.push('gridcolumn_current_none_use');
					}
					if(Ext.isString(metaData.tdCls) && metaData.tdCls.length){
						metaData.tdCls += ' ' + tdCls.join(' ');
					}else{
						metaData.tdCls = tdCls.join(' ');
					}
					return '';
				}
			},


			{
				text: '&#160;',            dataIndex: 'art_tmb_path',     stateId: 'art_tmb_path',      width: 24, minWidth: 24, hidden: false, hideable: false, sortable: false, draggable: false, resizable: false,
				renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
					if(record.data.seg_color){
//						metaData.style = 'background:'+record.data.seg_color+';';
					}
					metaData.innerCls = 'art_tmb_path';
					return value;
				}
			},
			{text: AgLang.art_id,     dataIndex: 'art_id',  stateId: 'art_id',  width: 60, minWidth: 60, hidden: true, hideable: false, xtype: 'agcolumn'},
			{text: AgLang.art_id,     dataIndex: 'artc_id', stateId: 'artc_id', width: 60, minWidth: 60, hidden: false, hideable: true, xtype: 'agcolumn'},
			{
				text: AgLang.cdi_name,
				dataIndex: 'cdi_name',
				stateId: 'cdi_name',
//				xtype:'agcolumncdi',
//				width:70,
//				minWidth:70,
				//2016-03-31用 START
				xtype: 'agcolumncdiname',
				width: 80,
				minWidth: 80,
				//2016-03-31用 END
				hidden: false,
				hideable: true,
				editor: {
					xtype: 'textfield',
					allowBlank: true,
					allowOnlyWhitespace: false,
					selectOnFocus: true,
					enableKeyEvents: true,
					vtype: 'fmaid',
					listeners: {
						keydown: function(field,e,eOpts){
							e.stopPropagation();
						},
						keypress: function(field,e,eOpts){
							e.stopPropagation();
						},
						keyup: function(field,e,eOpts){
							e.stopPropagation();
						}
					}
/*
					xtype: 'combobox',
					store: 'fmaAllStore',
					queryMode: 'local',
					displayField: 'cdi_name',
					valueField: 'cdi_name',
					pageSize: 10
http://192.168.1.237/ExtJS/ext-4.2.1/examples/form/forum-search.js
*/
				}
			},

			{
				text: AgLang.cmp_abbr,
				dataIndex: 'cmp_id',
				stateId: 'cmp_id',
				xtype: 'agcolumnconceptartmappart',
				width: 40,
				minWidth: 40,
				hidden: true,
				hideable: false,
				editor: {
					allowBlank: true,
					allowOnlyWhitespace: false,
					editable: false,
					xtype: 'combobox',
					store: 'conceptArtMapPartStore',
					queryMode: 'local',
					displayField: 'cmp_title',
					valueField: 'cmp_id',
					matchFieldWidth: false,
					enableKeyEvents: true,
					listeners: {
						keydown: function(field,e,eOpts){
							e.stopPropagation();
						},
						keypress: function(field,e,eOpts){
							e.stopPropagation();
						},
						keyup: function(field,e,eOpts){
							e.stopPropagation();
						}
					}
				}
			},
			{
				text: AgLang.cp_abbr,
				dataIndex: 'cp_id',
				stateId: 'cp_id',
				xtype: 'agcolumnconceptpart',
				width: 40,
				minWidth: 40,
				hidden: false,
				hideable: true,
				editor: {
					allowBlank: true,
					allowOnlyWhitespace: false,
					editable: false,
					xtype: 'combobox',
					store: 'conceptPartStore',
					queryMode: 'local',
					displayField: 'cp_title',
					valueField: 'cp_id',
					matchFieldWidth: false,
					enableKeyEvents: true,
					listeners: {
						keydown: function(field,e,eOpts){
							e.stopPropagation();
						},
						keypress: function(field,e,eOpts){
							e.stopPropagation();
						},
						keyup: function(field,e,eOpts){
							e.stopPropagation();
						}
					}
				}
			},
			{
				text: AgLang.cl_abbr,
				dataIndex: 'cl_id',
				stateId: 'cl_id',
				xtype: 'agcolumnconceptlaterality',
				width: 40,
				minWidth: 40,
				hidden: false,
				hideable: true,
				editor: {
					allowBlank: true,
					allowOnlyWhitespace: false,
					editable: false,
					xtype: 'combobox',
					store: 'conceptLateralityStore',
					queryMode: 'local',
					displayField: 'cl_title',
					valueField: 'cl_id',
					matchFieldWidth: false,
					enableKeyEvents: true,
					listeners: {
						keydown: function(field,e,eOpts){
							e.stopPropagation();
						},
						keypress: function(field,e,eOpts){
							e.stopPropagation();
						},
						keyup: function(field,e,eOpts){
							e.stopPropagation();
						}
					}
				}
			},

			{
				text: AgLang.cdi_name_e,
				dataIndex: 'cdi_name_e',
				stateId: 'cdi_name_e',
				flex: 2.0,
				minWidth: 80,
//				xtype:'agcolumncdi',
				xtype: 'agcolumncdinamee',	//2016-03-31用
				//2016-03-31用 END
				hidden: false,
				hideable: true
			},

			{text: 'System',             dataIndex: 'seg_name',      stateId: 'seg_name',      flex: 1.0, minWidth: 50, hidden: true, hideable: true,  xtype: 'agsystemcolumn'},

			{text: AgLang.art_category,  dataIndex: 'arta_category', stateId: 'arta_category', flex: 1.0, minWidth: 50, hidden: false, hideable: true, xtype: 'agcolumn'},
			{text: AgLang.art_class,     dataIndex: 'arta_class',    stateId: 'arta_class',    width: 36, minWidth: 36, hidden: false, hideable: true, xtype: 'agcolumn'},
			{text: AgLang.art_comment,   dataIndex: 'arta_comment',  stateId: 'arta_comment',  flex: 2.0, minWidth: 80, hidden: false, hideable: true, xtype: 'agcolumn'},
			{text: AgLang.art_judge,     dataIndex: 'arta_judge',    stateId: 'arta_judge',    flex: 1.0, minWidth: 50, hidden: false, hideable: true, xtype: 'agcolumn'},

			{text: AgLang.art_filename,  dataIndex: 'art_filename',  stateId: 'art_filename',  flex: 2.0,  minWidth: 80, hidden: false, hideable: true, xtype: 'agcolumn'},
//			{text: AgLang.art_folder,    dataIndex: 'artf_name',     stateId: 'artf_name',     flex:1,    minWidth:80, hidden:true, hideable:false, xtype:'agcolumn'},
//			{text: AgLang.art_folder,    dataIndex: 'artf_id',       stateId: 'artf_id',       width:36,    minWidth:36, hidden:false, hideable:false, xtype:'agcolumn'},


			{text: AgLang.art_data_size, dataIndex: 'art_data_size', stateId: 'art_data_size', width: 60, hidden: true,  hideable: true, xtype: 'agfilesizecolumn'},

			{text: AgLang.art_xmax,      dataIndex: 'art_xmax',      stateId: 'art_xmax',      width: 60, hidden: true, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER },
			{text: AgLang.art_xmin,      dataIndex: 'art_xmin',      stateId: 'art_xmin',      width: 60, hidden: true, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER },
			{text: AgLang.art_xcenter,   dataIndex: 'art_xcenter',   stateId: 'art_xcenter',   width: 59, hidden: true, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER },
			{text: AgLang.art_ymax,      dataIndex: 'art_ymax',      stateId: 'art_ymax',      width: 60, hidden: true, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER },
			{text: AgLang.art_ymin,      dataIndex: 'art_ymin',      stateId: 'art_ymin',      width: 60, hidden: true, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER },
			{text: AgLang.art_ycenter,   dataIndex: 'art_ycenter',   stateId: 'art_ycenter',   width: 59, hidden: true, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER },
			{text: AgLang.art_zmax,      dataIndex: 'art_zmax',      stateId: 'art_zmax',      width: 55, hidden: true, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER },
			{text: AgLang.art_zmin,      dataIndex: 'art_zmin',      stateId: 'art_zmin',      width: 55, hidden: true, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER },
			{text: AgLang.art_zcenter,   dataIndex: 'art_zcenter',   stateId: 'art_zcenter',   width: 59, hidden: true, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER },
			{text: AgLang.volume,        dataIndex: 'art_volume',    stateId: 'art_volume',    width: 59, hidden: true, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},

			{text: AgLang.timestamp,     dataIndex: 'art_timestamp', stateId: 'art_timestamp', width: self.ART_TIMESTAMP_WIDTH, hidden: true, hideable: true, xtype: 'datecolumn',     format: self.ART_TIMESTAMP_FORMAT },
			{text: AgLang.upload_modified, dataIndex: 'art_upload_modified',stateId: 'art_upload_modified', width: 112,  hidden: true, hideable: true, xtype: 'datecolumn', format: self.FORMAT_DATE_TIME },

			{text: 'Color',              dataIndex: 'color',         stateId: 'color',         width: 40, hidden: false, hideable: false, xtype: 'agcolorcolumn'},
			{text: 'Opacity',            dataIndex: 'opacity',       stateId: 'opacity',       width: 44, hidden: false, hideable: false, xtype: 'agopacitycolumn'},
			{text: 'Hide',               dataIndex: 'remove',        stateId: 'remove',        width: 40, hidden: false, hideable: false, xtype: 'agcheckcolumn'},
			{text: 'Scalar',             dataIndex: 'scalar',        stateId: 'scalar',        width: 40, hidden: true,  hideable: false, xtype: 'agnumbercolumn', format: '0', editor: 'numberfield'}
		],

		viewConfig: {
			stripeRows:true,
			enableTextSelection:false,
			loadMask:true,
			allowCopy: true,
			plugins: {
				ptype: 'gridviewdragdrop',
				ddGroup: 'dd-upload_folder_tree'
			},
			listeners: {
				beforedrop: function( node, data, overModel, dropPosition, dropHandlers, eOpts ){
					var view = this;
					var grid = view.up('gridpanel');
					var store = view.getStore();
					if(data.records[0] && (Ext.getClassName(data.records[0])=='PARTS' || Ext.getClassName(data.records[0])=='PICK_SEARCH' || Ext.getClassName(data.records[0])=='HISTORY_MAPPING')){
						var datas = [];
						data.records.forEach(function(r){
							var record = store.findRecord('art_id',r.get('art_id'),0,false,false,true);
							if(Ext.isEmpty(record)) datas.push(Ext.Object.merge({},r.getData(),{selected:true}));
						});
						if(datas.length){
							var sorters = store.sorters.getRange();
							if(sorters.length){
								store.sorters.clear();
								view.headerCt.clearOtherSortStates()
							}
							view.getSelectionModel().select(store.add(datas));
							if(sorters.length){
								store.sorters.addAll(sorters);
								store.sort();
							}
							self.update_other_palletPartsStore();
						}
						dropHandlers.cancelDrop();
					}
					else if(data.records[0] && Ext.getClassName(data.records[0])=='UPLOAD_FOLDER_TREE'){
						grid.setLoading(true);

						var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
						var proxy = uploadObjectStore.getProxy();
						var params = Ext.Object.merge({},proxy.extraParams || {},{artf_id: data.records[0].get('artf_id'), recursive: data.copy ? true : false});
						Ext.Ajax.request({
							url: proxy.api.read,
							method: proxy.actionMethods.read,
							timeout: proxy.timeout,
							params: params,
							callback: function(options,success,response){
								var json;
								try{json = Ext.decode(response.responseText)}catch(e){};
								if(success==false || Ext.isEmpty(json) || Ext.isEmpty(json.success) || json.success==false || Ext.isEmpty(json.datas) || !Ext.isArray(json.datas)){
									grid.setLoading(false);
									if(Ext.isEmpty(json) || Ext.isEmpty(json.msg)) return;
									Ext.Msg.show({
										title: 'DROP',
										msg: json.msg,
										buttons: Ext.Msg.OK,
										icon: Ext.Msg.ERROR
									});
								}else{
									var datas = [];
									Ext.each(json.datas,function(data){
										var record = store.findRecord('art_id',data.art_id,0,false,false,true);
										if(Ext.isEmpty(record)) datas.push(Ext.Object.merge({},data,{selected:true}));
									});
									if(datas.length){
										var sorters = store.sorters.getRange();
										if(sorters.length){
											store.sorters.clear();
											view.headerCt.clearOtherSortStates()
										}
										view.getSelectionModel().select(store.add(datas));
										if(sorters.length){
											store.sorters.addAll(sorters);
											store.sort();
										}
										self.update_other_palletPartsStore();
									}
									grid.setLoading(false);
								}
							}
						});
						dropHandlers.cancelDrop();
					}else{
						dropHandlers.cancelDrop();
						return false;
					}
				},
				drop: function( node, data, overModel, dropPosition, eOpts ){
				}
			}
		},
		selType: 'rowmodel',
		selModel: {
			mode:'MULTI',
			listeners: {
				selectionchange : function(selModel,selected,eOpts){
					self.setDisabled_pallet_grid_button_Task.delay(250);
				}
			}
		},
		dockedItems: [{
			xtype: 'toolbar',
			dock: 'top',
			itemId: 'toolbar-top',
			layout: {
				overflowHandler: 'Menu'
			},
			items:[{
				tooltip : 'Select All',
				iconCls  : 'pallet_select',
				listeners: {
					click: function(b,e,eOpts){
						var grid = b.up('gridpanel');
						var view = grid.getView();
						var viewDom = view.el.dom;
						var scX = viewDom.scrollLeft;
						var scY = viewDom.scrollTop;
						var selMode = grid.getSelectionModel();
						selMode.deselectAll(true);
						selMode.selectAll();
						grid.focus();
						view.scrollBy(scX-viewDom.scrollLeft,scY-viewDom.scrollTop,false);
//						self.setDisabled_pallet_grid_button_Task.delay(0);
					}
				}
			},{
				tooltip : 'Unselect All',
				iconCls  : 'pallet_unselect',
				listeners: {
					click: function(b,e,eOpts){
						var grid = b.up('gridpanel');
						var view = grid.getView();
						var viewDom = view.el.dom;
						var scX = viewDom.scrollLeft;
						var scY = viewDom.scrollTop;
						var selMode = grid.getSelectionModel();
						selMode.deselectAll();
						grid.focus();
						view.scrollBy(scX-viewDom.scrollLeft,scY-viewDom.scrollTop,false);
					}
				}
			},'-',{
				tooltip : 'Focus(Centering)',
				iconCls: 'pallet_focus_center',
				listeners: {
					click: function (b, e) {
						var grid = b.up('gridpanel');
						var view = grid.getView();
						var viewDom = view.el.dom;
						var scX = viewDom.scrollLeft;
						var scY = viewDom.scrollTop;
						var store = grid.getStore();
						var records = [];
						var selMode = grid.getSelectionModel();
						if(selMode.getCount()>0){
							records = selMode.getSelection();
						}else{
							records = store.getRange();
						}
						store.suspendEvents(false);
//						Ext.each(store.getRange(),function(record,i,a){
//							record.beginEdit();
//							record.set('focused',null);
//							record.commit(false);
//							record.endEdit(false,['focused']);
//						});
						Ext.each(records,function(record,i,a){
							record.beginEdit();
							record.set('focused',false);
							record.commit(false);
							record.endEdit(false,['focused']);
						});
						store.resumeEvents();
						self.setHashTask.delay(0);
						grid.focus();
						view.scrollBy(scX-viewDom.scrollLeft,scY-viewDom.scrollTop,false);
					}
				}
			},{
				tooltip : 'Focus(Centering & Zoom)',
				iconCls: 'pallet_focus',
				listeners: {
					click: function (b, e) {
						var grid = b.up('gridpanel');
						var view = grid.getView();
						var viewDom = view.el.dom;
						var scX = viewDom.scrollLeft;
						var scY = viewDom.scrollTop;
						var store = grid.getStore();
						var records = [];
						var selMode = grid.getSelectionModel();
						if(selMode.getCount()>0){
							records = selMode.getSelection();
						}else{
							records = store.getRange();
						}
						store.suspendEvents(false);
//						Ext.each(store.getRange(),function(record,i,a){
//							record.beginEdit();
//							record.set('focused',null);
//							record.commit(false);
//							record.endEdit(false,['focused']);
//						});
						Ext.each(records,function(record,i,a){
							record.beginEdit();
							record.set('focused',true);
							record.commit(false);
							record.endEdit(false,['focused']);
						});
						store.resumeEvents();
						self.setHashTask.delay(0);
						grid.focus();
						view.scrollBy(scX-viewDom.scrollLeft,scY-viewDom.scrollTop,false);
					}
				}
			},'-',{
				id: 'ag-pallet-def-color-button',
				tooltip: 'Set distinct color to selected parts',
				iconCls: 'pallet_def_color',
				disabled: true,
				listeners: {
					click: function(b, e){
						var grid = b.up('gridpanel');
						if(!grid || !grid.rendered) return;
						var selModel = grid.getSelectionModel();
						var records = selModel.getSelection();
						if(records.length==0) return;

						var bg_rgb = 'FFFFFF';
						var colorCmp = Ext.getCmp('options-background-color');
						if(colorCmp) bg_rgb = colorCmp.getValue();
//						console.log("bg_rgb=["+bg_rgb+"]");

						var bg_r = parseInt(bg_rgb.substr(0,2),16);
						var bg_g = parseInt(bg_rgb.substr(2,2),16);
						var bg_b = parseInt(bg_rgb.substr(4,2),16);
						var bg_y = bg_r*0.299 + bg_g*0.587 + bg_b*0.114;
						if(bg_y<128){
							bg_y = 255;
						}else{
							bg_y = 200;
						}

						var getRandomColor2 = function(bc,y){
//							console.log("getRandomColor2=["+y+"]");
							var c;
							do{
//								c = Math.ceil(Math.random() * parseInt("FF", 16));
								c = Math.ceil(Math.random() * y);
							}while(Math.abs(c-bc)<=10);
							c = c.toString(16);
							while(c.length<2){ c = '0' + c; }
							return c;
						};
						var getRandomColor = function(){
							var r = getRandomColor2(bg_r,bg_y);
							var g = getRandomColor2(bg_g,bg_y);
							var b = getRandomColor2(bg_b,bg_y);
							return ('#'+r+g+b).toUpperCase();
						};
						var store = Ext.data.StoreManager.lookup('palletPartsStore');
						store.suspendEvents(true);
						Ext.each(records,function(record,i,a){
							record.beginEdit();
							record.set('color', getRandomColor());
							record.commit(false);
							record.endEdit(false,['color']);
						});
						store.resumeEvents();

						var view = grid.getView();
						var viewDom = view.el.dom;
						var scX = viewDom.scrollLeft;
						var scY = viewDom.scrollTop;
						selModel.deselectAll(true);
						view.refresh();
						view.scrollBy(scX-viewDom.scrollLeft,scY-viewDom.scrollTop,false);

						Ext.defer(function(){
							selModel.select(records);
							view.scrollBy(scX-viewDom.scrollLeft,scY-viewDom.scrollTop,false);
						},50);
					}
				}


			},{
				id: 'ag-pallet-none-color-button',
				tooltip: 'Set default color to selected parts',
				iconCls: 'pallet_none_color',
				disabled: true,
				listeners: {
					click: function(b, e){
						var grid = b.up('gridpanel');
						if(!grid || !grid.rendered) return;
						var selModel = grid.getSelectionModel();
						var records = selModel.getSelection();
						if(records.length==0) return;
						var store = Ext.data.StoreManager.lookup('palletPartsStore');
						store.suspendEvents(true);
						Ext.each(records,function(record,i,a){
							record.beginEdit();
							record.set('color', DEF_COLOR);
							record.commit(false);
							record.endEdit(false,['color']);
						});
						store.resumeEvents();

						var view = grid.getView();
						var viewDom = view.el.dom;
						var scX = viewDom.scrollLeft;
						var scY = viewDom.scrollTop;
						selModel.deselectAll(true);
						view.refresh();
						view.scrollBy(scX-viewDom.scrollLeft,scY-viewDom.scrollTop,false);

						Ext.defer(function(){
							selModel.select(records);
							view.scrollBy(scX-viewDom.scrollLeft,scY-viewDom.scrollTop,false);
						},50);
					},
					scope: this
				}
			},'-',{
				id: 'ag-pallet-color-pallet-button',
				tooltip: 'Set select color to selected parts',
				iconCls: 'color_pallet',
				text: 'Color',
				disabled: true,
				menu: {
					xtype: 'agcolormenu',
					value: DEF_COLOR,
					listeners: {
						select: function(picker, color, eOpts){
							var b = Ext.getCmp('ag-pallet-color-pallet-button');
							var grid = b.up('gridpanel');
							if(!grid || !grid.rendered) return;
							var selModel = grid.getSelectionModel();
							var records = selModel.getSelection();
							if(records.length==0) return;
							var store = Ext.data.StoreManager.lookup('palletPartsStore');
							store.suspendEvents(true);
							Ext.each(records,function(record,i,a){
								record.beginEdit();
								record.set('color', '#'+color);
								record.commit(false);
								record.endEdit(false,['color']);
							});
							store.resumeEvents();

							var view = grid.getView();
							var viewDom = view.el.dom;
							var scX = viewDom.scrollLeft;
							var scY = viewDom.scrollTop;
							selModel.deselectAll(true);
							view.refresh();
							view.scrollBy(scX-viewDom.scrollLeft,scY-viewDom.scrollTop,false);

							Ext.defer(function(){
								selModel.select(records);
								view.scrollBy(scX-viewDom.scrollLeft,scY-viewDom.scrollTop,false);
							},50);
						}
					}
				}
			},{
				id: 'ag-pallet-opacity-pallet-button',
				text: 'Opacity',
				disabled: true,
				menu: {
					items:[{
						text: '1.0'
					},{
						text: '0.8'
					},{
						text: '0.6'
					},{
						text: '0.4'
					},{
						text: '0.3'
					},{
						text: '0.2'
					},{
						text: '0.1'
					},{
						text: '0.05'
					},{
						text: '0.0'
					}],
					listeners: {
						click: function( menu, item, e, eOpts ){
							var opacity = parseFloat(item.text)

							var b = Ext.getCmp('ag-pallet-opacity-pallet-button');
							var gridpanel = b.up('gridpanel');
							if(!gridpanel || !gridpanel.rendered) return;
							var selModel = gridpanel.getSelectionModel();
							var records = selModel.getSelection();
							if(records.length==0) return;
							var store = gridpanel.getStore();
							store.suspendEvents(true);
							Ext.each(records,function(record,i,a){
								record.beginEdit();
								record.set('opacity', opacity);
								record.commit(false);
								record.endEdit(false,['opacity']);
							});
							store.resumeEvents();

							var view = gridpanel.getView();
							var viewDom = view.el.dom;
							var scX = viewDom.scrollLeft;
							var scY = viewDom.scrollTop;
							selModel.deselectAll(false);
							view.refresh();
							view.scrollBy(scX-viewDom.scrollLeft,scY-viewDom.scrollTop,false);

							Ext.defer(function(){
								selModel.select(records);
								view.scrollBy(scX-viewDom.scrollLeft,scY-viewDom.scrollTop,false);
							},50);
						}
					}
				}
			},{
				id: 'ag-pallet-remove-pallet-button',
				text: 'Hide',
				disabled: true,
				menu: {
					items:[{
						text: 'Show'
					},{
						text: 'Hide'
					}],
					listeners: {
						click: function( menu, item, e, eOpts ){
							var hide = item.text.toUpperCase()==='HIDE';

							var b = Ext.getCmp('ag-pallet-remove-pallet-button');
							var gridpanel = b.up('gridpanel');
							if(!gridpanel || !gridpanel.rendered) return;
							var selModel = gridpanel.getSelectionModel();
							var records = selModel.getSelection();
							if(records.length==0) return;
							var store = gridpanel.getStore();
							store.suspendEvents(true);
							Ext.each(records,function(record,i,a){
								record.beginEdit();
								record.set('remove', hide);
								record.commit(false);
								record.endEdit(false,['remove']);
							});
							store.resumeEvents();

							var view = gridpanel.getView();
							var viewDom = view.el.dom;
							var scX = viewDom.scrollLeft;
							var scY = viewDom.scrollTop;
							selModel.deselectAll(true);
							view.refresh();
							view.scrollBy(scX-viewDom.scrollLeft,scY-viewDom.scrollTop,false);

							Ext.defer(function(){
								selModel.select(records);
								view.scrollBy(scX-viewDom.scrollLeft,scY-viewDom.scrollTop,false);
							},50);
						}
					}
				}
			},
			'-',
			'->',
			{
				hidden: !self.USE_FMA_OBJ_LINK,
				xtype: 'tbseparator'
			},{
				hidden: !self.USE_FMA_OBJ_LINK,
				disabled: true,
				id: 'ag-pallet-fma-obj-link-button',
				text: AgLang.fma_corresponding_change_mode,
				iconCls: 'pallet_link',
				enableToggle: true
			},{
				hidden: !self.USE_FMA_OBJ_LINK,
				tooltip   : 'Paste',
				iconCls   : 'pallet_special_paste',
				listeners: {
					afterrender: function( b, eOpts ){
						var button = Ext.getCmp('ag-pallet-fma-obj-link-button');
						if(button){
							b.setDisabled(button.isDisabled() || (pressed ? false : true));
							button.on({
								disable: function(button, eOpts){
									b.setDisabled(true);
								},
								enable: function(button, eOpts){
									b.setDisabled(button.pressed ? false : true);
								},
								toggle: function( button, pressed, eOpts ){
									b.setDisabled(button.isDisabled() || (pressed ? false : true));
								}
							});
						}
					},
					click: function(b,e,eOpts){
						var gridpanel = b.up('gridpanel');
						if(gridpanel && gridpanel.rendered){
							Ext.Msg.show({
								title: AgLang.fma_corresponding_change,
								iconCls: b.iconCls,
								closable: false,
								msg: AgLang.fma_corresponding_change_dialog_message,
								width: 500,
								buttons: Ext.Msg.OKCANCEL,
								defaultFocus: 0,
								multiline: true,
								animateTarget: b.el,
								icon: Ext.window.MessageBox.INFO,
								fn: function(buttonId, text, opt){
									if(buttonId != 'ok') return;
//									console.log(text);
									gridpanel.setLoading(true);
									Ext.defer(function(){

										var paste_array = [];
										if(text.indexOf("\t")>=0){
											paste_array = AgUtils.TabData.parse(text);
										}else if(text.indexOf(",")>=0){
											paste_array = AgUtils.CSVData.parse(text);
										}else if(text.indexOf(" ")>=0 || text.indexOf("　")>=0){
											paste_array = AgUtils.TabData.parse(Ext.String.trim(text.replace(/　/g," ").replace(/[ ]{2,}/g," ").replace(/\s+$/g,"").replace(/^\s+/g,"")).replace(/[ ]/g,"\t"));
										}else{
											paste_array = AgUtils.TabData.parse(text);
										}


										if( Ext.isEmpty(paste_array) || (Ext.isArray(paste_array) && !Ext.isArray(paste_array[0])) || (Ext.isArray(paste_array) && Ext.isEmpty(paste_array[0])) ){
											Ext.Msg.show({
												title: AgLang.fma_corresponding_change,
												iconCls: b.iconCls,
												msg: AgLang.fma_corresponding_change_dialog_error_message,
												buttons: Ext.Msg.OK,
												icon: Ext.Msg.ERROR,
												fn: function(buttonId,text,opt){
												}
											});
											gridpanel.setLoading(false);
											return;
										}

										var palletPartsStore = Ext.data.StoreManager.lookup('palletPartsStore');
										var fmaAllStore = Ext.data.StoreManager.lookup('fmaAllStore');
										var n_record = Ext.create(Ext.getClassName(palletPartsStore.model),{});
										var c_record;
										var art_ids = [];
										var map_records = [];

										var prefixs = [];
										Ext.data.StoreManager.lookup('prefixStore').each(function(record){
											prefixs.push(record.get('prefix_char'));
										});
										var art_id_regexp = new RegExp('^('+prefixs.join('|')+':?)[0-9]+');
										var cdi_name_regexp = new RegExp('^[A-Z]{2,}[0-9]+');
										var conceptArtMapPartStore = Ext.data.StoreManager.lookup('conceptArtMapPartStore');
										Ext.each(paste_array,function(array,i,arr){
											Ext.each(array,function(text,i,arr){
												if(Ext.isString(arr[i])) arr[i] = Ext.String.trim(text);
												if(art_id_regexp.test(arr[i])){

													if(c_record && c_record.getChanges()){
														c_record.endEdit(false);
														c_record.commit(false);
														art_ids.push({
															art_id:     c_record.get('art_id'),
															cdi_name:   c_record.get('cdi_name'),
															cdi_name_e: c_record.get('cdi_name_e'),
															cmp_id:     c_record.get('cmp_id'),
															selected:   c_record.get('selected'),
															color:      c_record.get('color'),
															opacity:    c_record.get('opacity'),
															remove:     c_record.get('remove'),
															scalar:     c_record.get('scalar')
														});
														map_records.push(c_record.copy());
														c_record = null;
													}

													c_record = palletPartsStore.findRecord( 'art_id', arr[i], 0, false, false, true );
													if(Ext.isEmpty(c_record)){
														c_record = n_record.copy();
														Ext.data.Model.id(c_record);
														c_record.beginEdit();
														c_record.set('art_id',arr[i]);
													}else{
														c_record.beginEdit();
													}
												}
												else if(cdi_name_regexp.test(arr[i])){

													var cdi_name = arr[i];
													var cmp_id = 0;
													if(Ext.isString(arr[i]) && arr[i].length){
														var m = self.regexpIsSubclassCdiName.exec(cdi_name);
														if(Ext.isArray(m) && m.length){
															var tmp_cdi_name = m[1];
															var cmp_abbr = m[2].toUpperCase();
															cdi_name = tmp_cdi_name;
															var cmp_record = conceptArtMapPartStore.findRecord('cmp_abbr', cmp_abbr, 0, false, false, true );
															if(cmp_record) cmp_id = cmp_record.get('cmp_id');
														}
														var f_record = fmaAllStore.findRecord( 'cdi_name', cdi_name, 0, false, false, true );
														if(f_record){
															if(c_record.get('cmp_id')!==cmp_id) c_record.set('cmp_id', cmp_id);
															if(c_record.get('cdi_name')!==f_record.get('cdi_name')){
																c_record.set('cdi_name', f_record.get('cdi_name'));
															}
															if(c_record.get('cdi_name_e')!==f_record.get('cdi_name_e')) c_record.set('cdi_name_e', f_record.get('cdi_name_e'));
														}
													}

												}
											});
										});
										if(c_record && c_record.getChanges()){
											c_record.endEdit(false);
											c_record.commit(false);
											art_ids.push({
												art_id:     c_record.get('art_id'),
												cdi_name:   c_record.get('cdi_name'),
												cdi_name_e: c_record.get('cdi_name_e'),
												cmp_id:     c_record.get('cmp_id'),
												selected:   c_record.get('selected'),
												color:      c_record.get('color'),
												opacity:    c_record.get('opacity'),
												remove:     c_record.get('remove'),
												scalar:     c_record.get('scalar')
											});
											map_records.push(c_record.copy());
										}

										if( Ext.isEmpty(art_ids) ){
											Ext.Msg.show({
												title: AgLang.fma_corresponding_change,
												iconCls: b.iconCls,
												msg: AgLang.fma_corresponding_change_dialog_error_message,
												buttons: Ext.Msg.OK,
												icon: Ext.Msg.ERROR,
												fn: function(buttonId,text,opt){
												}
											});
											gridpanel.setLoading(false);
											return;
										}

										var params = {
											art_ids: Ext.encode(art_ids)
										};
										self.getUploadObjInfo(params,{
											store: palletPartsStore,
											emptyMsg: {
												title: 'WARNING',
												msg: 'Data that corresponds to the text that was pasted does not exist.',
												iconCls: b.iconCls,
												buttons: Ext.Msg.OK,
												icon: Ext.Msg.WARNING
											},
											empty: function(){
//												console.log('empty()');
												gridpanel.setLoading(false);
											},
											success: function(records){
//												console.log('success()');
//												console.log(records);
												if(Ext.isArray(records) && records.length){
													var extraParams = self.getExtraParams();
													delete extraParams.ag_data;
													delete extraParams.current_datas;
													delete extraParams.model;
													delete extraParams.tree;
													delete extraParams.version;
													var datas = [];
													Ext.each(map_records,function(record){
														var p_record = palletPartsStore.findRecord( 'art_id', record.get('art_id'), 0, false, false, true );
														if(Ext.isEmpty(p_record)) return true;
														datas.push({
															art_id:   record.get('art_id'),
															cdi_name: record.get('cdi_name'),
															cmp_id:   record.get('cmp_id'),
															cm_use:   !Ext.isEmpty(record.get('cdi_name'))
														});
													});

													extraParams.datas = Ext.encode(datas);
													extraParams.comment = AgLang.fma_corresponding_change;
//													console.log(extraParams);


													Ext.Ajax.request({
														url: 'api-upload-file-list.cgi?cmd=update_concept_art_map',
														method: 'POST',
														params: extraParams,
														callback: function(options,success,response){
															if(!success){
																Ext.Msg.show({
																	title: AgLang.fma_corresponding_change,
																	msg: '['+response.status+'] '+response.statusText,
																	iconCls: b.iconCls,
																	icon: Ext.Msg.ERROR,
																	buttons: Ext.Msg.OK
																});
																gridpanel.setLoading(false);
																self.updateArtInfo();
																return;
															}

															var json;
															try{json = Ext.decode(response.responseText)}catch(e){};
															if(Ext.isEmpty(json) || !json.success){
																var msg = 'Unknown error!!';
																if(Ext.isObject(json) && json.msg) msg = json.msg;
																Ext.Msg.show({
																	title: AgLang.fma_corresponding_change,
																	msg: msg,
																	iconCls: b.iconCls,
																	icon: Ext.Msg.ERROR,
																	buttons: Ext.Msg.OK
																});
																gridpanel.setLoading(false);
																self.updateArtInfo();
																return;
															}

//															self.updateArtInfo();

															if(self.syncMappingMngStore) self.syncMappingMngStore(map_records);
															if(self.syncUploadObjectStore) self.syncUploadObjectStore(map_records);
															if(self.syncPalletPartsStore) self.syncPalletPartsStore(map_records);
															if(self.syncPickSearchStore) self.syncPickSearchStore(map_records);

															gridpanel.setLoading(false);
															var selModel = gridpanel.getSelectionModel();
															selModel.fireEvent('selectionchange', selModel,selModel.getSelection());
														}
													});
												}
											},
											failure: function(){
												console.log('failure()');
												gridpanel.setLoading(false);
											}
										});

									},10);
								}
							});
						}
					}
				}
			},{
				hidden: !self.USE_FMA_OBJ_LINK,
				xtype: 'tbseparator'
			},{
				hidden: !self.USE_FMA_OBJ_LINK,
				text: AgLang.fma_corresponding_link_break,
				iconCls: 'pallet_link_break',
				disabled: true,
				handler: function(b,e){
					if(b.isDisabled()) return;
					b.setDisabled(true);

					var gridpanel = b.up('gridpanel');
					var selModel = gridpanel.getSelectionModel();
					var datas = [];
					var records = [];
					Ext.each(selModel.getSelection(),function(r,i,a){
						if(Ext.isEmpty(r.get('art_id')) || Ext.isEmpty(r.get('cdi_name'))) return true;
						datas.push({art_id:r.get('art_id'),artf_id:r.get('artf_id')});
						records.push(r);
					});
					if(Ext.isEmpty(datas)){
						selModel.fireEvent('selectionchange', selModel,selModel.getSelection());
						return;
					}

					Ext.Msg.show({
						title: b.text || AgLang.fma_corresponding_link_break,
						iconCls: b.iconCls,
						msg: '選択されているデータのFMA対応付けを削除してよろしいですか？',
						animateTarget: b.el,
						buttons: Ext.Msg.YESNO,
						icon: Ext.Msg.QUESTION,
						defaultFocus: 'no',
						fn: function(buttonId,text,opt){
							if(buttonId != 'yes'){
								selModel.fireEvent('selectionchange', selModel,selModel.getSelection());
								return;
							}

							var extraParams = self.getExtraParams();
							delete extraParams.current_datas;
							extraParams.datas = Ext.encode(datas);
							extraParams.comment = AgLang.fma_corresponding_link_break;

							b.setIconCls('loading-btn');

							Ext.Ajax.request({
								url: 'api-upload-file-list.cgi?cmd=update_concept_art_map',
								method: 'POST',
								params: extraParams,
								callback: function(options,success,response){
									if(!success){
										Ext.Msg.show({
											title: AgLang.fma_corresponding_change,
											msg: '['+response.status+'] '+response.statusText,
											iconCls: b.iconCls,
											icon: Ext.Msg.ERROR,
											buttons: Ext.Msg.OK
										});
										gridpanel.setLoading(false);
										selModel.fireEvent('selectionchange', selModel,selModel.getSelection());
										b.setIconCls('pallet_link_break');
										return;
									}

									var json;
									try{json = Ext.decode(response.responseText)}catch(e){};
									if(Ext.isEmpty(json) || !json.success){
										var msg = 'Unknown error!!';
										if(Ext.isObject(json) && json.msg) msg = json.msg;
										Ext.Msg.show({
											title: AgLang.fma_corresponding_change,
											msg: msg,
											iconCls: b.iconCls,
											icon: Ext.Msg.ERROR,
											buttons: Ext.Msg.OK
										});
										gridpanel.setLoading(false);
										selModel.fireEvent('selectionchange', selModel,selModel.getSelection());
										b.setIconCls('pallet_link_break');
										return;
									}

									var conceptArtMapPartStore = Ext.data.StoreManager.lookup('conceptArtMapPartStore');
									var cmp_id     = conceptArtMapPartStore.getAt(0).get('cmp_id');
									var cdi_name   = null;
									var cdi_name_e = null;
									Ext.each(records,function(record){
										record.beginEdit();
										record.set('cdi_name', cdi_name);
										record.set('cdi_name_e', cdi_name_e);
										record.set('cmp_id', cmp_id);
										record.endEdit(false,['cdi_name','cdi_name_e','cmp_id']);
										record.commit(false,['cdi_name','cdi_name_e','cmp_id']);
									});

									if(self.syncMappingMngStore) self.syncMappingMngStore(records);
									if(self.syncUploadObjectStore) self.syncUploadObjectStore(records);
									if(self.syncPalletPartsStore) self.syncPalletPartsStore(records);
									if(self.syncPickSearchStore) self.syncPickSearchStore(records);

									gridpanel.setLoading(false);
									selModel.fireEvent('selectionchange', selModel,selModel.getSelection());
									b.setIconCls('pallet_link_break');
								}
							});
						}
					});
				},
				listeners: {
					afterrender: function(b,eOpts){
						var gridpanel = b.up('gridpanel');
						var selModel = gridpanel.getSelectionModel();
						selModel.on('selectionchange', function(selModel,selected,eOpts){
							b.setDisabled(true);
							if(selected.length>=1){
								var idx=-1;
								Ext.each(selected,function(r,i,a){
									if(Ext.isEmpty(r.get('art_id')) || Ext.isEmpty(r.get('cdi_name'))) return true;
									idx = i;
									return false;
								});
								b.setDisabled(idx<0?true:false);
							}
						});
					}
				}
			},{
				hidden: !self.USE_FMA_OBJ_LINK,
				xtype: 'tbseparator'
			},
			{
				hidden: !self.USE_FMA_MAPPING,
				xtype: 'tbseparator'
			},
			{
				hidden: !self.USE_FMA_MAPPING,
				id: 'ag-pallet-edit-button',
				tooltip: 'Edit Selected',
				iconCls: 'pallet_edit',
				text: AgLang.file_info ,//+ '(New)',
				disabled: true,
				handler: function(b,e){
					if(b.isDisabled()) return;
					b.setDisabled(true);
					Ext.defer(function(){
						var grid = b.up('gridpanel');
						var selModel = grid.getSelectionModel();
						var records = [];
						Ext.each(selModel.getSelection(),function(r,i,a){
							if(Ext.isEmpty(r.get('art_id'))) return true;
							records.push(r);
						});
						if(Ext.isEmpty(records)){
							selModel.fireEvent('selectionchange', selModel,selModel.getSelection());
						}else{
							self.openObjEditWindow({
								title: b.text,
								iconCls: b.iconCls,
								records: records,
								callback: function(){
									selModel.fireEvent('selectionchange', selModel,selModel.getSelection());
								}
							});
							selModel.fireEvent('selectionchange', selModel,selModel.getSelection());
						}
					},100);
				},
				listeners: {
					afterrender: function(b,eOpts){
						var gridpanel = b.up('gridpanel');
						var selModel = gridpanel.getSelectionModel();
						selModel.on('selectionchange', function(selModel,selected,eOpts){
							b.setDisabled(true);
							if(selected.length>=1){
								var idx=-1;
								Ext.each(selected,function(r,i,a){
									if(Ext.isEmpty(r.get('art_id'))) return true;
									idx = i;
									return false;
								});
								b.setDisabled(idx<0?true:false);
							}
						});
					}
				}
			},'-',{
				hidden: false,
				id: 'ag-pallet-download-button',
				xtype: 'button',
				tooltip: 'Download Selected',
				iconCls: 'pallet_download',
				disabled:true,
				handler: function(b,e){
					b.setDisabled(true);

					var gridpanel = b.up('gridpanel');
					var selModel = gridpanel.getSelectionModel();
					var recs = selModel.getSelection();
					if(Ext.isEmpty(recs)){
						b.setDisabled(false);
						return;
					}
					selModel.deselectAll();
					selModel.select(recs);
					b.setDisabled(true);

					self.downloadObjectsTask.delay(10,self.downloadObjects,self,[{
						type: 'pallet',
						records: recs,
						callback: function(){
							b.setDisabled(false);
						}
					}]);
				}
			},

			'-',
			{
				id: 'ag-pallet-copy-button',
				tooltip: 'Copy Selected',
				iconCls: 'pallet_copy',
				disabled: true,
				handler: function(b,e){
					var grid = b.up('gridpanel');
					var selModel = grid.getSelectionModel();
//						var records = selModel.getSelection();
					var records = [];
					grid.getStore().each(function(r,i,a){
						if(selModel.isSelected(r)) records.push(r);
					});
					if(records.length>0){
						AgUtils.copyListCB(grid,records);
//							AgPalletUtils.copyListCB(records);
					}
				}
			},
			'-',
			{
				tooltip: 'Paste',
				iconCls: 'pallet_paste',
				handler: function(b,e){
					var gridpanel = b.up('gridpanel');
					if(gridpanel && gridpanel.rendered){
						var waitMask = new Ext.LoadMask({target:gridpanel,msg:'Please wait...'});
						waitMask.show();
						AgPalletUtils.pasteList(self,gridpanel.getStore(),function(addrecs,records){
							var scrollTop = gridpanel.body.dom.scrollTop;
							gridpanel.getView().refresh();
							gridpanel.body.dom.scrollTop = scrollTop;
							waitMask.hide();
							if(records && records.length>0){
								Ext.defer(function(){
									self.update_other_palletPartsStore();
								},250);
							}
						});
					}
				}
			},
			'-',
			{
				id: 'ag-pallet-delete-button',
				tooltip: 'Delete Selected',
				iconCls: 'pallet_delete',
				disabled: true,
				handler: function(b,e){
					self.remove_select_records_palletPartsStore();
				}
			},

			'-',
			{
				xtype: 'tbtext',
				itemId: 'num',
				minWidth: 26,
				style: 'text-align:right;',
				text: '<label>0 Objects</label>'
			}
			]
		}],
		listeners: {
			render: function(grid,eOpts){
				grid.getView().on({
					itemkeydown : function(view,record,item,index,e,eOpts){
						if(e.getKey()==e.DELETE){
							e.stopEvent();
							var b = Ext.getCmp('ag-pallet-delete-button');
							b.fireEvent('click',b);
						}
					}
				});
			},
			afterrender: function(grid,eOpts){
				var store = grid.getStore();
				store.on({
					datachanged: function(store,eOpts){
						grid.getDockedComponent('toolbar-top').getComponent('num').setText('<label>'+store.getCount()+' Objects</label>');
					}
				});
				grid.getDockedComponent('toolbar-top').getComponent('num').setText('<label>'+store.getCount()+' Objects</label>');
//				if(Ext.isChrome) grid.columns.forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});

				if(!self.PALLET_PANEL_HIDDEN){
					var viewport = Ext.getCmp('main-viewport');
					viewport.on('resize',function(viewport){
						var panel = Ext.getCmp('window-panel');
						var pallet_height = Math.floor(panel.body.getHeight()/4);
						grid.setHeight(pallet_height);
					},self,{
						single: true
					});
				}
			},
			itemcontextmenu: {
				fn: self.showPalletItemContextmenu,
				scope: self
			}
		}
	});

	self.getConflictPanel = function(config){
		config = Ext.apply({},config || {},{title: AgLang.conflict_list,iconCls: 'pallet_table'});
		var conflict_panel = Ext.create('Ext.panel.Panel',{
//		var conflict_panel = {
			hidden: !self.USE_CONFLICT_LIST,
			xtype: 'panel',
			id: 'conflict-panel',
			title: (self.USE_CONFLICT_LIST_TYPE == 'tab') ? config.title : null,
			iconCls: (self.USE_CONFLICT_LIST_TYPE == 'tab') ? config.iconCls : null,
			border: false,
//			autoHeight: true,
			layout: 'border',
			items: [{
				hidden: true,
				region: 'north',
				height: 24,
				xtype: 'form',
				border: true,
				items:[{
					fieldLabel: '検索対象',
					labelWidth: 60,
					labelAlign: 'right',
					xtype: 'radiogroup',
					columns: [67,140],
					vertical: false,
					items: [
						{
							boxLabel: 'conflict',
							name: 'conflict_type',
							inputValue: 'conflict',
							checked: true
						},
						{
							boxLabel: 'conflict incl. children',
							name: 'conflict_type',
							inputValue: 'children'
						}
					],
					listeners: {
						afterrender: function(radiogroup, eOpt){
//							console.log('afterrender():radiogroup');
						},
						change: function( radiogroup, newValue, oldValue, eOpts ){
//							console.log(newValue);
							var store = Ext.getCmp('conflict-panel').down('gridpanel').getStore();
							var p = store.getProxy();
							p.extraParams = p.extraParams || {};
							p.extraParams.conflict_type = newValue;
							store.loadPage(1);
						}
					}
				}]
			},{
				border: false,
				region: 'center',
				xtype: 'gridpanel',
//				store: Ext.data.StoreManager.lookup('conflictListStore'),
				store: 'conflictListStore',
//				features: [{ftype:'grouping'}],
//				autoScroll: true,
				columns: [
					{text: AgLang.cdi_name,   dataIndex: 'cdi_name',    width:80, minWidth:80, hidden:false, hideable:false, draggable: false, xtype:'agcolumncdiname'},

					{text: AgLang.cmp_abbr,   dataIndex: 'cmp_id',      width:40, minWidth:40, hidden:true, hideable:false, draggable: false, xtype: 'agcolumnconceptartmappart'},
					{text: AgLang.cp_abbr,    dataIndex: 'cp_id',       width:40, minWidth:40, hidden:false, hideable:false, draggable: false, xtype: 'agcolumnconceptpart' },
					{text: AgLang.cl_abbr,    dataIndex: 'cl_id',       width:40, minWidth:40, hidden:false, hideable:false, draggable: false, xtype: 'agcolumnconceptlaterality' },

					{text: AgLang.cdi_name_e, dataIndex: 'cdi_name_e',  flex:1,   minWidth:80, hidden:false, hideable:false, draggable: false, xtype:'agcolumncdinamee'},
					{text: 'mapped obj',      dataIndex: 'mapped_obj',  width:70, minWidth:70, hidden:false, hideable:false, draggable: false, xtype:'agnumbercolumn', format:'0'},
					{text: '&#160;',          dataIndex: 'cdi_name',    width:40, minWidth:40, hidden:false, hideable:false, draggable: false, xtype:'templatecolumn', align:'center', tpl: '<a href="#" onclick="return false;">show</a>', sortable: false},
				],
				dockedItems: [{
					xtype: 'toolbar',
					dock: 'bottom',
					items: [{
						xtype: 'button',
						iconCls: 'x-tbar-loading',
						listeners: {
							click: function(b){
								var store = Ext.data.StoreManager.lookup('mapListStore');
								store.loadPage(1);
							}
						}
					},'-','->','-',{
						xtype: 'tbtext',
						itemId: 'num',
						text: '- Objects',
						listeners: {
							afterrender: function(field, eOpt){
//								var gridpanel = field.up('gridpanel');
//								var store = gridpanel.getStore();
								var store = Ext.data.StoreManager.lookup('mapListStore');
								store.on('load',function(store,records,successful,eOpts){
									if(Ext.isArray(records) && records.length){
										field.setText(Ext.util.Format.format('{0} Objects',records.length));
									}else{
										field.setText('- Objects');
									}
								});
							}
						}
					}]
				}],
				listeners: {
					afterrender: function(gridpanel, eOpt){
//						console.log('afterrender():gridpanel');
//						gridpanel.getStore().loadPage(1);
					},
					cellclick: function(gridpanel, td, cellIndex, record, tr, rowIndex, e, eOpts ){
						if(e.target.nodeName=='A'){
//							console.log('cellclick():gridpanel');
//							console.log(td);
//							console.log(cellIndex);
//							console.log(record);
//							console.log(tr);
//							console.log(rowIndex);
//							console.log(e);


							var title = Ext.String.format('{0} : {1} : {2}', config.title, record.get('cdi_name'), record.get('cdi_name_e'));
							var animateTarget = Ext.get(td);
//							var objs = Ext.Array.clone(record.data.objs);

							var art_ids = [];
							Ext.each(record.data.objs,function(obj){
								art_ids.push({art_id: obj.art_id});
							});
							var params = self.getExtraParams() || {};
							delete params.current_datas;
							params.art_ids = Ext.encode(art_ids);
							params.cmd = 'read';
//							console.log(params);

							var ag_conflict_objs_window_id = 'ag-conflict-objs-window';
							Ext.Ajax.request({
								url: 'get-upload-obj-info.cgi',
								autoAbort: true,
								method: 'POST',
								params: params,
								callback: function(options,success,response){
									var json;
									try{json = Ext.decode(response.responseText)}catch(e){};
									if(!success || Ext.isEmpty(json) || Ext.isEmpty(json.success) || !json.success || Ext.isEmpty(json.datas)){
										return;
									}
									var win = Ext.getCmp(ag_conflict_objs_window_id);
									var gridpanel = win.down('gridpanel');
									var store = gridpanel.getStore();
									store.suspendEvents(true);
									Ext.each(json.datas,function(data){
										var record = store.findRecord('art_id',data.art_id,0,false,false,true);
										if(Ext.isEmpty(record)) return true;
										record.beginEdit();
										record.set('art_path',data.art_path);
										record.endEdit(false,['art_path']);
										record.commit(false,['art_path']);
									});
									store.resumeEvents();
//									store.loadData(json.datas);
								}
							});

							var win = Ext.getCmp(ag_conflict_objs_window_id);
							if(win){
								if(win.isHidden()){
									win.setTitle(title);
									var gridpanel = win.down('gridpanel');
									var store = gridpanel.getStore();
									store.loadData(record.data.objs);
									win.show(animateTarget);
								}else{
									win.hide(null,function(){
										win.setTitle(title);
										var gridpanel = win.down('gridpanel');
										var store = gridpanel.getStore();
										store.loadData(record.data.objs);
										win.show(animateTarget);
									});
								}
							}else{
								var uxiframe_namespace = '.uxiframe';
								Ext.create('Ext.window.Window', {
									id: ag_conflict_objs_window_id,
									title: title,
									iconCls: config.iconCls,
									height: 600,
									minHeight: 400,
									width: 600,
									minWidth: 400,
									layout: 'border',
//									animateTarget: animateTarget,
									autoDestroy: true,
									autoShow: false,
									maximizable: true,
									modal: true,
									closeAction: 'hide',
									items: [{
										region: 'center',
										xtype: 'uxiframe',
										src: 'AgRender.cgi',
										listeners: {
											afterrender: function(uxiframe,eOpts){
//												console.log('afterrender:uxiframe():'+uxiframe.id);
											},
											beforedestroy: function(uxiframe,eOpts){
//												console.log('beforedestroy:uxiframe():'+uxiframe.id);
											},
											load: function(uxiframe,eOpts){
//												console.log('load:uxiframe():'+uxiframe.id);
											}
										}
									},{
										region: 'south',
										height: 150,
										minHeight: 150,
										split: true,
										xtype: 'aggridpanel',
										store: Ext.create('Ext.data.Store', {
											model: 'CONFILICT_LIST_PALLET',
											proxy: {
												type: 'memory',
												reader: {
													type: 'json',
													root: 'objs'
												}
											}
										}),
										plugins: [self.getCellEditing()],
										columns: [
											{text: AgLang.use,        dataIndex: 'cm_use',       stateId: 'cm_use',       width:30, minWidth:30, hidden:false, hideable:false, sortable:false, xtype:'agselectedcheckcolumn'},
											{text: AgLang.art_id,     dataIndex: 'art_id',       stateId: 'art_id',       width:60, minWidth:60, hidden:true,  hideable:false, sortable:false, xtype:'agcolumn'},
											{text: AgLang.art_id,     dataIndex: 'artc_id',      stateId: 'artc_id',      width:60, minWidth:60, hidden:false, hideable:false, sortable:false, xtype:'agcolumn'},
											{text: AgLang.cdi_name,   dataIndex: 'cdi_name',     stateId: 'cdi_name',     width:80, minWidth:80, hidden:false, hideable:false, sortable:false, xtype:'agcolumncdiname'},
											{text: AgLang.cdi_name_e, dataIndex: 'cdi_name_e',   stateId: 'cdi_name_e',   flex:2,   minWidth:80, hidden:false, hideable:false, sortable:false, xtype:'agcolumncdinamee'},
											{text: AgLang.file_name,  dataIndex: 'art_filename', stateId: 'art_filename', flex :2,  minWidth:80, hidden:false, hideable:false, sortable:false, xtype:'agcolumn'},
											{text: AgLang.timestamp,  dataIndex: 'art_timestamp',stateId: 'art_timestamp',width:self.ART_TIMESTAMP_WIDTH, minWidth:67, hidden:false, hideable:false, sortable:true,  xtype:'datecolumn', format: self.ART_TIMESTAMP_FORMAT },
											{text: 'Color',           dataIndex: 'color',        stateId: 'color',        width:40, minWidth:40, hidden:false, hideable:false, sortable:false, xtype:'agcolorcolumn'},
											{text: 'Opacity',         dataIndex: 'opacity',      stateId: 'opacity',      width:44, minWidth:44, hidden:false, hideable:false, sortable:false, xtype:'agopacitycolumn'},
											{text: 'Hide',            dataIndex: 'remove',       stateId: 'remove',       width:40, minWidth:40, hidden:false, hideable:false, sortable:false, xtype:'agcheckcolumn'},
										],
										viewConfig: {
											stripeRows:true,
											enableTextSelection:false,
//											allowCopy: true,
//											plugins: {
//												ddGroup: 'dd-upload_folder_tree',
//												ptype: 'gridviewdragdrop',
//												enableDrop: false
//											}
										},
										selModel: {
											mode:'MULTI'
										},
										dockedItems: [{
											xtype: 'toolbar',
											dock: 'top',
											items:[{
												tooltip : 'Select All',
												iconCls  : 'pallet_select',
												listeners: {
													click: function(b,e,eOpts){
														var win = b.up('window');
														var gridpanel = win.down('gridpanel');
														var selMode = gridpanel.getSelectionModel();
														selMode.deselectAll();
														selMode.selectAll();
														gridpanel.getView().focus(false);
													}
												}
											},{
												tooltip : 'Unselect All',
												iconCls  : 'pallet_unselect',
												listeners: {
													click: function(b,e,eOpts){
														var win = b.up('window');
														var gridpanel = win.down('gridpanel');
														var selMode = gridpanel.getSelectionModel();
														selMode.deselectAll();
													}
												}
											},'-',{
												tooltip : 'Focus(Centering)',
												iconCls: 'pallet_focus_center',
												listeners: {
													click: function (b, e) {
														var win = b.up('window');
														var gridpanel = win.down('gridpanel');
														var store = gridpanel.getStore();
														var records = [];
														var selMode = gridpanel.getSelectionModel();
														if(selMode.getCount()>0){
															records = selMode.getSelection();
														}else{
															records = store.getRange();
														}
														store.suspendEvents(false);
														Ext.each(records,function(record,i,a){
															record.beginEdit();
															record.set('focused',false);
															record.commit(false);
															record.endEdit(false,['focused']);
														});
														store.resumeEvents();
														var uxiframe = win.down('uxiframe');
														self.setHashTask.delay(0,null,null,[uxiframe.AgRender,store,null,null]);
													}
												}
											},{
												tooltip : 'Focus(Centering & Zoom)',
												iconCls: 'pallet_focus',
												listeners: {
													click: function (b, e) {
														var win = b.up('window');
														var gridpanel = win.down('gridpanel');
														var store = gridpanel.getStore();
														var records = [];
														var selMode = gridpanel.getSelectionModel();
														if(selMode.getCount()>0){
															records = selMode.getSelection();
														}else{
															records = store.getRange();
														}
														store.suspendEvents(false);
														Ext.each(records,function(record,i,a){
															record.beginEdit();
															record.set('focused',true);
															record.commit(false);
															record.endEdit(false,['focused']);
														});
														store.resumeEvents();
														var uxiframe = win.down('uxiframe');
														self.setHashTask.delay(0,null,null,[uxiframe.AgRender,store,null,null]);
													}
												}
											},'-',{
												xtype: 'tbtext',
												text: AgLang.cdi_name
											},{
												id: 'ag-conflict-objs-window-add-combobox',
												xtype: 'combobox',
												store: 'mapListStore',
												queryMode: 'local',
												anyMatch: true,
												displayField: 'cdi_name',
												valueField: 'cdi_name',
												width: 72+17,
												enableKeyEvents: true,
												listeners: {
													change: function( combobox, newValue, oldValue, eOpts ){
														Ext.getCmp('ag-conflict-objs-window-add-button').setDisabled(true);
													},
													select: function( combobox, records, eOpts ){
														Ext.getCmp('ag-conflict-objs-window-add-button').setDisabled(Ext.isEmpty(records));
													},
													keydown: function(field,e,eOpts){
														e.stopPropagation();
													},
													keypress: function(field,e,eOpts){
														e.stopPropagation();
													},
													keyup: function(field,e,eOpts){
														e.stopPropagation();
													}
												}
											},{
												disabled:true,
												id: 'ag-conflict-objs-window-add-button',
												iconCls  : 'pallet_plus',
												listeners: {
													click : function(b,e,eOpts){
														var combobox = Ext.getCmp('ag-conflict-objs-window-add-combobox');
														var value = combobox.getValue();
														var record = combobox.getStore().findRecord( 'cdi_name', value, 0, false, true, true );
														if(record){
															var objs = Ext.Array.clone(record.data.objs);
															Ext.each(objs,function(obj){
																obj.is_temporary = true;
															});
															var win = b.up('window');
															var gridpanel = win.down('gridpanel');
															var store = gridpanel.getStore();
															store.loadData(objs, true);
															var uxiframe = win.down('uxiframe');
															self.setHashTask.delay(0,null,null,[uxiframe.AgRender,store,null,null]);
														}
													}
												}

											},{
												disabled:true,
												id: 'ag-conflict-objs-window-delete-button',
												iconCls  : 'pallet_delete',
												listeners: {
													click : function(b,e,eOpts){
														var win = b.up('window');
														var gridpanel = win.down('gridpanel');
														var selModel = gridpanel.getSelectionModel();
														var recs = selModel.getSelection();
														if(Ext.isEmpty(recs)){
															return;
														}
														var del_recs = [];
														Ext.each(recs,function(r){
															if(r.get('is_temporary')) del_recs.push(r);
														});
														if(Ext.isEmpty(del_recs)){
															return;
														}
														var store = gridpanel.getStore();
														store.remove(del_recs);
														var uxiframe = win.down('uxiframe');
														self.setHashTask.delay(0,null,null,[uxiframe.AgRender,store,null,null]);
													}
												}
											},'-','->','-',{
												disabled:true,
												id: 'ag-conflict-objs-window-download-button',
//												text: 'Download',
												tooltip: 'Download Selected',
												iconCls: 'pallet_download',
												listeners: {
													click: function(b){
														b.setDisabled(true);

														var win = b.up('window');
														var gridpanel = win.down('gridpanel');
														var selModel = gridpanel.getSelectionModel();
														var recs = selModel.getSelection();
														if(Ext.isEmpty(recs)){
															b.setDisabled(false);
															return;
														}

														self.downloadObjectsTask.delay(10,self.downloadObjects,self,[{
															type: 'objects',
															records: recs,
															callback: function(){
																b.setDisabled(false);
															}
														}]);
													}
												}
											}]
										}],
										listeners: {
											afterrender: function(gridpanel,eOpts){
//												gridpanel.getStore().loadData(record.data);
											},
											selectionchange: function( gridpanel, selected, eOpts ){
												Ext.getCmp('ag-conflict-objs-window-download-button').setDisabled(selected.length===0);

												var disabled = true;
												Ext.each(selected,function(record){
													if(record.get('is_temporary')){
														disabled = false;
														return false;
													}
												});
												Ext.getCmp('ag-conflict-objs-window-delete-button').setDisabled(disabled);
											}
										}
									}],
									buttons: [{
										text: 'add pallet',
										id: 'ag-conflict-objs-window-add-pallet-button',
										handler: function(b, e){
											var pallet_gridgridpanel = Ext.getCmp('pallet-grid');
											var palletPartsStore = pallet_gridgridpanel.getStore();

											var win = b.up('window');
											var gridpanel = win.down('gridpanel');
											var store = gridpanel.getStore();
											var art_ids = [];
											var datas = [];
											var cdi_name;

											var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
											uploadObjectStore.suspendEvents(false);
											try{
												store.each(function(record){
													var art_id = record.get('art_id');
													art_ids.push({art_id:art_id});

													var find_record = palletPartsStore.findRecord('art_id', art_id, 0, false, false, true);
//													if(Ext.isEmpty(find_record)) datas.push(record.getData());
													if(Ext.isEmpty(find_record)) datas.push(Ext.create(Ext.getClassName(palletPartsStore.model),record.getData()));

													Ext.each([uploadObjectStore],function(find_store){
														var startIdx = 0;
														while(find_record = find_store.findRecord('art_id', art_id, startIdx, false, false, true)){
															if(!find_record.get('selected')){
																find_record.beginEdit();
																find_record.set('selected',true)
																find_record.commit(true);
																find_record.endEdit(true,['selected']);
															}
															startIdx = find_store.indexOf(find_record);
															if(startIdx<0) break;
															startIdx++;
														}
													});
												});
											}catch(e){
												console.error(e);
											}


											uploadObjectStore.resumeEvents();
//											Ext.getCmp('upload-object-grid').getView().refresh();
											Ext.each(['upload-object-grid','pallet-grid'], function(id){
												var gridpanel = Ext.getCmp(id);
												gridpanel.getView().refresh();
											});

											if(datas.length){
//												palletPartsStore.loadData(datas, true);
												palletPartsStore.loadRecords(datas, {addRecords:true});
												self.update_localdb_pallet();
											}
											if(art_ids.length){
												var params = self.getExtraParams() || {};
												delete params.model;
												delete params.version;
												delete params.ag_data;
												delete params.tree;
												delete params.current_datas;
												params.art_ids = Ext.encode(art_ids);

												Ext.Ajax.request({
													url: 'get-upload-obj-info.cgi',
													method: 'POST',
													params: params,
													callback: function(options, success, response){
													},
													success: function(response, options){
														var json;
														var records;
														try{json = Ext.decode(response.responseText)}catch(e){};
														if(Ext.isEmpty(json)){
															Ext.Msg.show({
																title: 'WARNING',
																msg: 'データの取得に失敗しました',
																buttons: Ext.Msg.OK,
																icon: Ext.Msg.WARNING
															});
															return;
														}
														if(Ext.isEmpty(json.datas)) return;

														uploadObjectStore.suspendEvents(false);
														try{
															Ext.each(json.datas,function(data){
																var art_id = data.art_id;
																Ext.each([palletPartsStore,uploadObjectStore],function(find_store){
																	var startIdx = 0;
																	var find_record;
																	while(find_record = find_store.findRecord('art_id', art_id, startIdx, false, false, true)){
																		var modifiedFieldNames = [];
																		find_record.beginEdit();
																		Ext.Object.each(data,function(name,value){
//																			console.log(name,value,find_record.get(name));
																			if(find_record.get(name)===undefined || find_record.get(name)===value) return true;
																			find_record.set(name,value)
																			modifiedFieldNames.push(name);
																		});
																		if(modifiedFieldNames.length){
																			find_record.commit(true);
																			find_record.endEdit(true,modifiedFieldNames);
																		}else{
																			find_record.cancelEdit();
																		}
																		startIdx = find_store.indexOf(find_record);
																		if(startIdx<0) break;
																		startIdx++;
																	}
																});
															});
															self.update_localdb_pallet();
														}catch(e){
															console.error(e);
														}
														uploadObjectStore.resumeEvents();
														Ext.each(['upload-object-grid','pallet-grid'], function(id){
															var gridpanel = Ext.getCmp(id);
															gridpanel.getView().refresh();
														});
													}
												});
											}
										}
									},'->',{
										text: AgLang.save,
										disabled:true,
										id: 'ag-conflict-objs-window-save-button',
										handler: function(b, e){
											if(b.isDisabled()) return;
											b.setDisabled(true);
											b.setIconCls('loading-btn');

											var win = b.up('window');
											win.setDisabled(true);
											var gridpanel = win.down('gridpanel');

											var store = gridpanel.getStore();
											store.clearFilter(true);
											store.filter('cm_use', false);
											var datas = [];
											var cdi_name;
											store.each(function(record){
												datas.push({
													art_id: record.get('art_id'),
													cdi_name: record.get('cdi_name'),
													cmp_id: record.get('cmp_id'),
													cm_use: record.get('cm_use')
												});
												cdi_name = record.get('cdi_name');
											});
											store.clearFilter();
											if(datas.length){

												var wait_win = Ext.Msg.show({
													title: config.title,
													iconCls: config.iconCls,
													msg: 'しばらくお持ちください…',
//													animateTarget: b.el,
													closable: false,
													wait: true
												});

												var extraParams = self.getExtraParams() || {};
												delete extraParams.ag_data;
												delete extraParams.current_datas;
												delete extraParams.model;
												delete extraParams.tree;
												delete extraParams.version;
												extraParams.datas = Ext.encode(datas);
												extraParams.comment = config.title;
//												console.log(extraParams);


												Ext.Ajax.request({
													url: 'api-upload-file-list.cgi?cmd=update_concept_art_map',
													method: 'POST',
													params: extraParams,
													callback: function(options,success,response){
														wait_win.close();
					//									console.log(options);
					//									console.log(success);
					//									console.log(response);
														if(!success){
															Ext.Msg.show({
																title: config.title,
																iconCls: config.iconCls,
																msg: '['+response.status+'] '+response.statusText,
																icon: Ext.Msg.ERROR,
																buttons: Ext.Msg.OK,
																fn: function(){
																	b.setDisabled(false);
																	b.setIconCls(null);
																	win.setDisabled(false);
																}
															});
															return;
														}

														var json;
														try{json = Ext.decode(response.responseText)}catch(e){};
														if(Ext.isEmpty(json) || !json.success){
															var msg = 'Unknown error!!';
															if(Ext.isObject(json) && json.msg) msg = json.msg;
															Ext.Msg.show({
																title: config.title,
																iconCls: config.iconCls,
																msg: msg,
																icon: Ext.Msg.ERROR,
																buttons: Ext.Msg.OK,
																fn: function(){
																	b.setDisabled(false);
																	b.setIconCls(null);
																	win.setDisabled(false);
																}
															});
															return;
														}

														var conflictListStore = Ext.data.StoreManager.lookup('conflictListStore');
														var record = conflictListStore.findRecord( 'cdi_name', cdi_name, 0, false, false, true);
														if(record){
															var datas = [];
															store.each(function(record){
																if(!record.get('cm_use')) return true;
																datas.push({
																	cm_use:       record.get('cm_use'),
																	art_id:       record.get('art_id'),
																	art_filename: record.get('art_filename'),
																	artg_id:      record.get('artg_id'),
																	artg_name:    record.get('artg_name'),
																	art_entry:    (record.get('art_entry') ? record.get('art_entry') : new Date()).getTime(),
																	art_path:     record.get('art_path'),
																	cdi_name:     record.get('cdi_name'),
																});
															});
															record.beginEdit();
															record.set('mapped_obj',datas.length);
															record.set('objs', datas);
															record.endEdit(false,['mapped_obj','objs']);
															record.commit(false,['mapped_obj','objs']);
														}


														var mapListStore = Ext.data.StoreManager.lookup('mapListStore');
														var record = mapListStore.findRecord( 'cdi_name', cdi_name, 0, false, false, true);
														if(record){
															var datas = [];
															store.each(function(record){
																if(!record.get('cm_use')) return true;
																datas.push({
																	cm_use:       record.get('cm_use'),
																	art_id:       record.get('art_id'),
																	art_filename: record.get('art_filename'),
																	artg_id:      record.get('artg_id'),
																	artg_name:    record.get('artg_name'),
																	art_entry:    (record.get('art_entry') ? record.get('art_entry') : new Date()).getTime(),
																	art_path:     record.get('art_path'),
																	cdi_name:     record.get('cdi_name'),
																});
															});
															record.beginEdit();
															record.set('mapped_obj',datas.length);
															record.set('objs', datas);
															record.endEdit(false,['mapped_obj','objs']);
															record.commit(false,['mapped_obj','objs']);
														}

														win.close();
														self.updateArtInfo();
													}
												});

											}else{
												win.close();
											}
										}
									},{
										text: AgLang.close,
										handler: function(b, e){
											b.up('window').close();
										}
									}],
									listeners: {
										afterrender: function(win,eOpts){
//											console.log('afterrender:win():'+win.id);
											var uxiframe = win.down('uxiframe');
											var uxiframe_dom = uxiframe.el.dom;
											var uxiframe_iframe = uxiframe.iframeEl.dom;
											uxiframe.AgRender = new AgRender({namespace: uxiframe_namespace.substring(1), hash_key:'ag-render-uxiframe-hash', use_localstorage: true});
											uxiframe.AgRender.open({
												dom: uxiframe_dom,
												iframe: uxiframe_iframe,
												iframe_window: uxiframe.getWin(),
												iframe_document: uxiframe.getDoc(),
											});

											var gridpanel = win.down('gridpanel');
											var store = gridpanel.getStore();
											var p = store.getProxy();
											p.extraParams = p.extraParams || {};
											delete p.extraParams._pickIndex;

											$(window).bind('changeLongitudeDegree'+uxiframe_namespace,function(e,newValue,oldValue){
//												console.log('changeLongitudeDegree()');
												e.stopPropagation();
											});
											$(window).bind('changeLatitudeDegree'+uxiframe_namespace,function(e,newValue,oldValue){
//												console.log('changeLatitudeDegree()');
												e.stopPropagation();
											});
											$(window).bind('changeZoom'+uxiframe_namespace,function(e,newValue,oldValue){
//												console.log('changeZoom()');
												e.stopPropagation();
											});
											$(window).bind('pickObject'+uxiframe_namespace,function(e,o,route){
//												console.log('pickObject()');
//												e.stopPropagation();

												var p = store.getProxy();
												p.extraParams = p.extraParams || {};
//												if(Ext.isNumber(p.extraParams._pickIndex)){
//													var record = store.getAt(p.extraParams._pickIndex);
//													gridpanel.getView().deselect(record);
//												}
												delete p.extraParams._pickIndex;

												var idx = -1;
												if(Ext.isObject(o) && Ext.isObject(o.object)){
													idx = store.findBy(function(record,id){
														if(record.data.art_path==o.object.record.data.art_path) return true;
													});
												}

												store.suspendEvents(false);
												store.each(function(record){
													record.beginEdit();
													record.set('target_record', false);
													record.endEdit(false,['target_record']);
													record.commit(false,['target_record']);
												});

												if(idx>=0){
//													p.extraParams._pickIndex = idx;
													var record = store.getAt(idx);
													record.beginEdit();
													record.set('target_record', true);
													record.endEdit(false,['target_record']);
													record.commit(false,['target_record']);
												}
												store.resumeEvents();

												gridpanel.getView().refresh();
												if(idx>=0){
													var record = store.getAt(idx);
													gridpanel.getView().select(record);
													return true;
												}else{
													return 0x990000;
												}

											});


											$(window).bind('iframe_load'+uxiframe_namespace,function(e,newValue,oldValue){
//												console.log('iframe_load()');
												e.stopPropagation();
											});
											$(window).bind('agrender_load'+uxiframe_namespace,function(e,newValue,oldValue){
//												console.log('agrender_load()');
												e.stopPropagation();
												self.setHashTask.delay(0,null,null,[uxiframe.AgRender,store,null,null]);

												store.on({
													metachange: function( store, meta, eOpts ){
//														console.log('metachange:store():');
//														self.setHashTask.delay(0,null,null,[uxiframe.AgRender,store,null,null]);
													},
													update: function( store, record, operation, eOpts ){
//														console.log('update:store():'+operation);
														if(operation==Ext.data.Model.COMMIT){
															var count = 0;
															store.suspendEvents(false);
															store.each(function(record){
																var cm_use = record.get('cm_use');
																record.set('selected', cm_use);
																record.commit();
																if(!cm_use) count++;
															});
															store.resumeEvents();

															var mv_frozen = false;

															Ext.getCmp('ag-conflict-objs-window-save-button').setDisabled(mv_frozen || count===0);
															self.setHashTask.delay(0,null,null,[uxiframe.AgRender,store,null,null]);
														}
													}
												});
											});
											store.loadData(record.data.objs);
										},
										show: function(win,eOpts){
//											console.log('show:win():'+win.id);
											self.AgRender._cancel_keybind = true;
											var uxiframe = win.down('uxiframe');
											if(uxiframe.AgRender) uxiframe.AgRender._cancel_keybind = false;

											var button = Ext.getCmp('ag-conflict-objs-window-save-button');
											button.setDisabled(true);
											button.setIconCls(null);

											win.setDisabled(false);

											var gridpanel = win.down('gridpanel');
											gridpanel.setDisabled(true);
											var store = gridpanel.getStore();
//											self.setHashTask.delay(250,null,null,[uxiframe.AgRender,store,null,null]);
											self.setHashTask.delay(0,null,null,[uxiframe.AgRender,store,null,null]);

											$(window).one('agrender_hashchange'+uxiframe_namespace,function(e,newValue,oldValue){
//												console.log('agrender_hashchange()');
												e.stopPropagation();
												Ext.defer(function(){
													store.suspendEvents(false);
													store.each(function(record){
														record.set('focused', true);
														record.commit();
													});
													store.resumeEvents();
													self.setHashTask.delay(0,null,null,[uxiframe.AgRender,store,null,null]);
													gridpanel.setDisabled(false);
												},250);
											});
										},
										hide: function(win,eOpts){
//											console.log('hide:win():'+win.id);

											self.AgRender._cancel_keybind = false;
											var uxiframe = win.down('uxiframe');
											uxiframe.AgRender._cancel_keybind = true;

											var gridpanel = win.down('gridpanel');
											var store = gridpanel.getStore();
											store.removeAll();
											self.setHashTask.delay(0,null,null,[uxiframe.AgRender,store,null,function(){

												self.setHashTask.delay(0,null,null,[null,null,null,null]);

											}]);

											var p = store.getProxy();
											p.extraParams = p.extraParams || {};
											delete p.extraParams._pickIndex;


										}
									}
								}).show(animateTarget);
							}
						}
					}
				}
			}],
			listeners: {
				afterrender: function(panel, eOpt){
//					var store = panel.down('gridpanel').getStore();
					var store = Ext.data.StoreManager.lookup('mapListStore');

					var radiogroup = panel.down('radiogroup').getValue();
					var p = store.getProxy();
					p.extraParams = p.extraParams || {};
					p.extraParams.conflict_type = radiogroup.conflict_type;
					store.loadPage(1);
				},
				beforedestroy: function(panel, eOpt){
//					console.log('beforedestroy()');
				}
			}
		});
//		};
		return conflict_panel;
	};

	var changeUploadFolder = function(upload_folder_record,upload_obj_records,record_copy){
		if(Ext.isEmpty(record_copy)) record_copy = false;
		if(!Ext.isBoolean(record_copy)) record_copy = record_copy ? true : false;

		var drag_artf_ids = Ext.Array.unique(upload_obj_records.map(function(r){return r.get('artf_id')}));
		var drop_artf_id = upload_folder_record.get('artf_id');

		var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
		var p = uploadObjectStore.getProxy();
		p.extraParams = p.extraParams || {};

		var uploadFolderFileStore = Ext.data.StoreManager.lookup('uploadFolderFileStore');
		uploadFolderFileStore.loadPage(1,{
			params: {
				drag_artf_ids: Ext.encode(drag_artf_ids),
				drop_artf_id: upload_folder_record.get('artf_id'),
				drop_art_ids: Ext.encode(upload_obj_records.map(function(r){return r.get('art_id')}))
			},
			callback: function(records,operation,success){
				if(!success) return;
				var add_recs = upload_obj_records.filter(function(r){
					return uploadFolderFileStore.findBy(function(record,id){return record.get('art_id')===r.get('art_id') && record.get('artf_id')===upload_folder_record.get('artf_id')})===-1;
				});
				if(add_recs.length){
					var copy_datas = add_recs.map(function(r){
						var copy_data = r.getData();
						copy_data.artf_id = upload_folder_record.get('artf_id');
						return copy_data;
					});
					uploadFolderFileStore.add(copy_datas);
					var remove_recs = [];
					if(!record_copy){
						upload_obj_records.forEach(function(r){
							var remove_idx = uploadFolderFileStore.findBy(function(record,id){return record.get('art_id')===r.get('art_id') && record.get('artf_id')===r.get('artf_id')});
							if(remove_idx===-1) return true;
							remove_recs.push(uploadFolderFileStore.getAt(remove_idx));
						});
//						console.log(remove_recs);
						if(remove_recs.length){
							uploadFolderFileStore.remove(remove_recs);
						}
					}
					uploadFolderFileStore.sync({
						batch: Ext.create('Ext.data.Batch',{
							pauseOnException: true,
							listeners: {
								complete: function( batch, operation, eOpts ){
								},
								exception: function( batch, operation, eOpts ){
									batch.proxy.reader.rawData.msg
									Ext.Msg.show({
										title: record_copy ? 'Copy' : 'Move',
										msg: batch.proxy.reader.rawData.msg ? batch.proxy.reader.rawData.msg : '何らかのエラーが発生しました',
										iconCls: 'tfolder',
										icon: Ext.Msg.ERROR,
										buttons: Ext.Msg.OK
									});
									batch.destroy();
								},
								operationcomplete: function( batch, operation, eOpts ){
									var uploadFolderTreePanelStore = Ext.data.StoreManager.lookup('uploadFolderTreePanelStore');
									uploadFolderTreePanelStore.suspendAutoSync();
									try{
										var rootNode = uploadFolderTreePanelStore.getRootNode();
										batch.proxy.reader.rawData.datas.forEach(function(data){
											var node;
											if(data.artf_id){
												node = rootNode.findChild( 'artf_id', data.artf_id, true );
											}else{
												node = rootNode;
											}
											if(node){
												node.set('art_count',data.art_count)
												node.commit(false,['art_count']);
											}
										});
									}catch(e){
										console.error(e);
									}
									uploadFolderTreePanelStore.resumeAutoSync();
								}
							}
						}),
						callback: function(batch,options){
						},
						success: function(batch,options){
							if(remove_recs.length===0) return;

							var callback = function(){
								var palletPartsStore = Ext.data.StoreManager.lookup('palletPartsStore');
								if(palletPartsStore.getCount()){
									palletPartsStore.suspendEvents(true);
									try{
										upload_obj_records.forEach(function(upload_obj_record){
											var idx = palletPartsStore.findBy(function(record){
												return record.get('art_id')===upload_obj_record.get('art_id') && record.get('artf_id')===upload_obj_record.get('artf_id');
											});
											if(idx===-1) return true;
											var pallet_record = palletPartsStore.getAt(idx);
											if(pallet_record){
												pallet_record.beginEdit();
												pallet_record.set('artf_id',drop_artf_id);
												pallet_record.endEdit(false,['artf_id']);
												pallet_record.commit(false,['artf_id']);
											}
										});
									}catch(e){
										console.error(e);
									}
									palletPartsStore.resumeEvents();
								}
							};

							if(p.extraParams.artf_id == drop_artf_id || drag_artf_ids.filter(function(drag_artf_id){return p.extraParams.artf_id === drag_artf_id;}).length){
								var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
								var loadPage = 1;
								if(uploadObjectStore.currentPage * uploadObjectStore.pageSize < uploadObjectStore.getTotalCount()){
									loadPage = uploadObjectStore.currentPage;
								}else if(uploadObjectStore.currentPage * uploadObjectStore.pageSize > uploadObjectStore.getTotalCount()){
									loadPage = uploadObjectStore.currentPage-1;
								}
								if(loadPage<1) loadPage = 1;
								uploadObjectStore.loadPage(loadPage,{
									callback: function(records,operation,success){
										if(!success) return;
										callback();
									}
								});
							}else{
								callback();
							}
						},
						failure: function(batch,options){
						}
					});
				}
			}
		});
	};

//	var upload_folder_tree = Ext.create('Ext.tree.Panel', {
	var upload_folder_tree = Ext.create('Ext.ag.TreePanel', {
		title: self.TITLE_UPLOAD_FOLDER,
		id: 'upload-folder-tree',
		region: 'north',
		flex: 1,
		minHeight: 150,
		stateId: 'upload-folder-tree',
		stateEvents: ['resize'],
		stateful: false,
		split: true,
		store: 'uploadFolderTreePanelStore',

		hideHeaders: true,
		columns: [{
			xtype: 'treecolumn',
			stateId: 'artf_name',
			flex: 1,
			hidden: false,
			hideable: false,
			sortable: false,
			resizable: false,
			dataIndex: 'text'
		},{
			xtype: 'agnumbercolumn',
			stateId: 'art_count',
			width: 40,
			hidden: false,
			hideable: false,
			sortable: false,
			resizable: false,
			format: '0',
			align: 'right',
			dataIndex: 'art_count'
		}],
		viewConfig: {
			allowCopy: true,
			plugins: {
				ptype: 'treeviewdragdrop',
				appendOnly: true,
				containerScroll: true,
				ddGroup: 'dd-upload_folder_tree'
			},
			listeners: {
				beforedrop: function( node, data, overModel, dropPosition, dropHandlers, eOpts ){
//					console.log('treeviewdragdrop','beforedrop',data);
					var p = overModel.getProxy ? overModel.getProxy() : overModel.store.getProxy();
					p.extraParams = p.extraParams || {};
					delete p.extraParams.artf_pid;

					if(data.records[0] && (Ext.getClassName(data.records[0])=='PARTS' || Ext.getClassName(data.records[0])=='PALLETPARTS')){
						dropHandlers.wait = true;
						Ext.defer(function(){
							dropHandlers.cancelDrop();
							changeUploadFolder(overModel,data.records,data.copy);
						},0);

					}
					else if(data.records[0] && Ext.getClassName(data.records[0])=='UPLOAD_FOLDER_TREE'){
						dropHandlers.wait = true;
						Ext.defer(function(){
							var c;
							if(overModel.hasChildNodes()){
								Ext.each(data.records,function(r){
									c = overModel.findChild('artf_name', r.get('artf_name'));
									if(c) return false;
								});
							}
							if(c){
								Ext.Msg.show({
									title: 'Drag',
									msg: 'Already exist in the same folder.',
									iconCls: 'tfolder',
									icon: Ext.Msg.ERROR,
									buttons: Ext.Msg.OK
								});
								dropHandlers.cancelDrop();
							}else{
								dropHandlers.processDrop();
							}
						},0);
					}
					else{
						dropHandlers.wait = true;
						Ext.defer(function(){
							dropHandlers.cancelDrop();
						},0);
					}
				},
				drop: function( node, data, overModel, dropPosition, eOpts ){
					var artf_pid;
					if(dropPosition=='append'){
						artf_pid = overModel.get('artf_id');
					}else{
						artf_pid = overModel.get('artf_pid');
					}
					var artf_pids = {};
					artf_pids[artf_pid] = overModel.getDepth();
					var record;
					Ext.each(data.records,function(r){
						artf_pids[r.get('artf_pid')] = r.getDepth();
						r.beginEdit();
						r.set('artf_pid',artf_pid);
						r.endEdit(false,['artf_pid']);
						record = r;
					});

					var uploadFolderTreePanelStore = Ext.data.StoreManager.lookup('uploadFolderTreePanelStore');

					var reject = function(){
						var rootNode = uploadFolderTreePanelStore.getRootNode();
						var nodes = [];
						Ext.each(Ext.Object.getKeys(artf_pids).sort(function(a,b){return artf_pids[b]-artf_pids[a];}),function(artf_pid){
							var node = rootNode.findChild( 'artf_id', artf_pid, true );
							if(node) nodes.push(node);
						});
						var load_uploadFolderTreePanelStore = function(){
							var node = nodes.shift();
							if(node){
								uploadFolderTreePanelStore.load({
									node: node,
									callback: function(records,operation,success){
										if(!success) return;
										load_uploadFolderTreePanelStore();
									}
								});
							}
						};
						load_uploadFolderTreePanelStore();
					};
					var success = function(data){
						Ext.each(data.records,function(node){
							node.beginEdit();
							var field_names = ['artf_timestamp'];
							Ext.each(field_names,function(field_name){
								node.set(field_name,node.fields.map[field_name].convert(data[field_name],node));
							});
							node.endEdit(true,field_names);
							node.commit(true,field_names);
						});
					};

					if(uploadFolderTreePanelStore.isLoading()){
						uploadFolderTreePanelStore.on('load',{
							fn: function(){
								uploadFolderTreePanelStore.sync({
									success: function(batch,options){
										if(Ext.isArray(this.reader.rawData.datas) && this.reader.rawData.datas.length){
											success(this.reader.rawData.datas[0]);
										}
									},
									failure: function(batch,options){
										Ext.Msg.show({
											title: 'Drag',
											msg: this.reader.rawData.msg,
											iconCls: 'tfolder',
											icon: Ext.Msg.ERROR,
											buttons: Ext.Msg.OK
										});
										reject();
									}
								});
							},
							single: true
						});
					}else{
						uploadFolderTreePanelStore.sync({
							success: function(batch,options){
								if(Ext.isArray(this.reader.rawData.datas) && this.reader.rawData.datas.length){
									success(this.reader.rawData.datas[0]);
								}
							},
							failure: function(batch,options){
								Ext.Msg.show({
									title: 'Drag',
									msg: this.reader.rawData.msg,
									iconCls: 'tfolder',
									icon: Ext.Msg.ERROR,
									buttons: Ext.Msg.OK
								});
								reject();
							}
						});
					}

				},
				afterrender: function( treeview, eOpts ){
					var el = treeview.getEl();
					el.on({
						dragenter: function(event){
							self.fileDragenter(event);
							var tr = Ext.get(event.target).up('tr.x-grid-data-row',el) || Ext.get(treeview.getNode(treeview.panel.store.getRootNode()));

							var oldAutoAbort = Ext.Ajax.autoAbort;
							Ext.Ajax.autoAbort = true;
							treeview.panel.getSelectionModel().select(treeview.getRecord(tr));
							Ext.Ajax.autoAbort = oldAutoAbort;

							return false;
						},
						dragover: function(event){
							self.fileDragover(event);
							return false;
						},
						drop: function(event){
							var tr = Ext.get(event.target).up('tr.x-grid-data-row',el) || Ext.get(treeview.getNode(treeview.panel.store.getRootNode()));
							self.fileDrop(event,{
								callback: function(files,folders){
									var rec = treeview.panel.getSelectionModel().getSelection()[0] || treeview.panel.store.getRootNode();
									var fd = new FormData();
									fd.append('prefix_id',DEF_PREFIX_ID);
									fd.append('artf_id',rec.get('artf_id'));
									if(files.length==1){
										fd.append('file',files[0]);
									}else{
										Ext.each(files,function(file,i){
											fd.append('file'+(i+1),file);
										});
									}

									var file_info = [];
									Ext.each(files,function(file,i){
										file_info.push({
											name: file.name,
											size: file.size,
											last: file.lastModifiedDate.getTime()/1000,
											path: file.__directoryEntry ? file.__directoryEntry.fullPath : null
										});
									});
									fd.append('files',Ext.encode(file_info));
									fd.append('maintain_upload_directory_structure', self.MAINTAIN_UPLOAD_DIRECTORY_STRUCTURE_CHECKED ? 1 : 0);

									var _upload_progress = Ext.Msg.show({
										closable : false,
										modal    : true,
										msg      : 'Upload...',
										progress : true,
										title    : 'Upload...'
									});

									$.ajax({
										url: 'upload-object.cgi',
										type: 'POST',
										timeout: 300000,
										data: fd,
										processData: false,
										contentType: false,
										dataType: 'json',
										xhr : function(){
											var XHR = $.ajaxSettings.xhr();
											if(XHR.upload){
												XHR.upload.addEventListener('progress',function(e){
													var value = e.loaded/e.total;
													_upload_progress.updateProgress(value,Math.floor(value*100)+'%','Upload...');
												});
											}
											return XHR;
										}
									})
									.done(function( data, textStatus, jqXHR ){
										_upload_progress.close();
										if(!data.success){
											Ext.Msg.show({
												title: 'Failure',
												msg: data.msg,
												buttons: Ext.Msg.OK,
												icon: Ext.Msg.ERROR
											});
											return;
										}

										var _progress = Ext.Msg.show({
											closable : false,
											modal    : true,
											msg      : 'Uncompress...',
											progress : true,
											title    : 'Upload...',
											autoShow : true
										});
										_progress.center();
										var url = 'upload-object.cgi?'+Ext.Object.toQueryString({sessionID: data.sessionID, mtime: data.mtime, mfmt: data.mfmt});
										var cb = function(json,callback){
											if(Ext.isEmpty(json)) return;
											if(Ext.isObject(json) && Ext.isObject(json.progress) && Ext.isNumber(json.progress.value)){
												var value = json.progress.value;
												if(Ext.isString(value)) value = parseFloat(value);
												_progress.updateProgress(value,Math.floor(value*100)+'%',json.progress.msg);
											}
											var close_progress_title = null;
											var close_progress_icon = null;
											var close_progress_msg = null;
											if(json.progress && Ext.isString(json.progress.msg) && json.progress.msg.toLowerCase()=='end'){
												close_progress_title = 'Success';
												close_progress_icon = Ext.Msg.INFO;
												close_progress_msg = json.file ? 'Your data "' + json.file + '" has been uploaded.' : 'Your data uploaded.';
											}else if(json.progress && Ext.isString(json.progress.msg) && json.progress.msg.toLowerCase().indexOf('error')==0){
												close_progress_title = 'Error';
												close_progress_icon = Ext.Msg.ERROR;
												close_progress_msg = json.progress.msg;
											}else if(Ext.isBoolean(json.success) && !json.success && Ext.isString(json.msg) && json.msg.length){
												close_progress_title = 'Error';
												close_progress_icon = Ext.Msg.ERROR;
												close_progress_msg = json.msg;
											}
											if(callback) (callback)(close_progress_msg?true:false);
											if(close_progress_msg){
												_progress.close();
												Ext.Msg.show({
													title: close_progress_title,
													msg: close_progress_msg,
													buttons: Ext.Msg.OK,
													icon: close_progress_icon
												});
												if(json.file || json.files){
													if(self.MAINTAIN_UPLOAD_DIRECTORY_STRUCTURE_CHECKED){
														treeview.panel.getStore().load({node:rec});
													}else{
														Ext.data.StoreManager.lookup('uploadObjectStore').loadPage(1);
													}
												}
											}
										};

										if(useEventSource && EventSource){
											var evtSource = new EventSource(url);
											evtSource.onmessage = function(event){
												var json;
												try{json = Ext.decode(event.data)}catch(e){};
												if(json){
													cb(json,function(isEndOrError){if(isEndOrError) event.target.close();});
												}
											};
										}
										else{
											if(Ext.isEmpty(self._TaskRunner)) self._TaskRunner = new Ext.util.TaskRunner();
											var task = self._TaskRunner.newTask({
												run: function () {
													task.stop();
													Ext.Ajax.abort();
													Ext.Ajax.request({
														url: url,
														method: 'GET',
														callback: function(options,success,response){
															task.stop();
															try{json = Ext.decode(response.responseText)}catch(e){};
															if(json){
																cb(json,function(isEndOrError){if(!isEndOrError) task.start();});
															}
														}
													});
												},
												interval: 1000
											});
											task.start();
										}

									})
									.fail(function( jqXHR, textStatus, errorThrown ){
										console.log(jqXHR);
										console.log(textStatus);
										console.log(errorThrown);
									});
								}
							});

							return false;
						}
					});
				}
			}
		},
		selModel: {
			mode:'SINGLE',
			listeners: {
				selectionchange : function(selModel,selected,eOpts){
					var treepanel = selModel.view.panel;
					var toolbar = treepanel.getDockedItems('toolbar[dock="top"]')[0];

					toolbar.getComponent('rename').disable();
					toolbar.getComponent('delete').disable();
					toolbar.getComponent('download').disable();

					if(selModel.getCount()>0 && selected[0].getId()!='root'){
						toolbar.getComponent('rename').enable();
						toolbar.getComponent('delete').enable();
					}

					if(selModel.getCount()>0 && selected[0].getId()=='root' && selected[0].get('art_count')>0){
						toolbar.getComponent('delete').enable();
					}

//					if(selModel.getCount()>0 && selected[0].get('art_count')>0){
//						toolbar.getComponent('download').enable();
//					}
					if(selModel.getCount()>0){
						toolbar.getComponent('download').enable();
					}
				}
			}
		},
		dockedItems: [{
			dock: 'top',
			xtype: 'toolbar',
			layout: {
				overflowHandler: 'Menu'
			},
			items: [
				update_object_button,
				{
					disabled: false,
					xtype: 'button',
					iconCls: 'gear-btn',
					listeners: {
						click: {
							fn: function(b,e,o){

								Ext.create('Ext.window.Window', {
									title: 'Upload Default setting',
									iconCls: b.iconCls,
									closable: true,
									modal:true,
									resizable:false,
									width: 250,
									minWidth: 250,
									height: 120,
//									minHeight: 120,
									layout: 'fit',
									border: false,
									autoShow: true,
									items:[{
										xtype:'form',
										bodyPadding: 5,
										defaults: {
											hideLabel: false,
											labelAlign: 'right',
											labelStyle: 'font-weight:bold;',
											labelWidth: 40
										},
										items: [{
											xtype: 'combobox',
											name: 'prefix_id',
											itemId: 'prefix_id',
											fieldLabel: AgLang.prefix,
											store: 'prefixStore',
											queryMode: 'local',
											displayField: 'display',
											valueField: 'prefix_id',
											value: DEF_PREFIX_ID,
											editable: false
										},{
											itemId: 'maintain_upload_directory_structure',
											hidden: self.MAINTAIN_UPLOAD_DIRECTORY_STRUCTURE_HIDDEN,
											xtype: 'checkboxfield',
											boxLabel: MAINTAIN_UPLOAD_DIRECTORY_STRUCTURE_TEXT,
											checked: self.MAINTAIN_UPLOAD_DIRECTORY_STRUCTURE_CHECKED
										}]
									}],
									buttons: [{
										disabled: false,
										text: 'OK',
										handler: function(b,e) {
											var win = b.up('window');
											var formPanel = win.down('form');
											DEF_PREFIX_ID = formPanel.getComponent('prefix_id').getValue();
											if(Ext.isChrome) self.MAINTAIN_UPLOAD_DIRECTORY_STRUCTURE_CHECKED = formPanel.getComponent('maintain_upload_directory_structure').getValue();
											b.up('window').close();
										}
									},{
										text: 'Cancel',
										handler: function(b,e) {
											b.up('window').close();
										}
									}]

								});

							},
							buffer:0
						}
					}
				},'-',
/*
				{
					hidden: !self.USE_CONFLICT_LIST || self.USE_CONFLICT_LIST_TYPE == 'tab',
					disabled: true,
					id: 'ag-conflict-button',
					iconCls: 'pallet_table',
					text: AgLang.conflict_list,
					handler: function(b, e){
//						console.log(b);
						var win = Ext.getCmp('ag-conflict-window');
						if(win){
							win.show();
						}else{
							Ext.create('Ext.window.Window', {
								id: 'ag-conflict-window',
								title: b.text,
								iconCls: b.iconCls,
								height: 400,
								width: 400,
								layout: 'fit',
								animateTarget: b.el,
								autoDestroy: true,
								autoShow: true,
								closeAction: 'destroy',
								items: self.getConflictPanel({title: b.text,iconCls: b.iconCls}),
								buttons: [{
									text: AgLang.close,
									handler: function(b, e){
										b.up('window').close();
									}
								}]
							});
						}
					},
					listeners: {
						afterrender: function(b){
						}
					}
				},
				{
					hidden: !self.USE_CONFLICT_LIST || self.USE_CONFLICT_LIST_TYPE == 'tab',
					xtype: 'tbseparator'
				},
*/

				,self.getCXCreateButton(),'-',self.getCXSearchButton(),'-',self.getObjSearchButton(),'-',

				,'->',
//				'-',all_upload_parts_list_menu,'-'

//				'-',self.getCXCreateButton(),'-',{xtype: 'tbspacer', width: 20},

				'-',{
					itemId: 'download',
					xtype: 'button',
					tooltip: 'Download Selected',
					iconCls: 'pallet_download',
					disabled:true,
					listeners: {
						click: function(b){
							b.setDisabled(true);

							var treepanel = b.up('treepanel');
							var selModel = treepanel.getSelectionModel();
							var recs = selModel.getSelection();
							if(Ext.isEmpty(recs)){
								b.setDisabled(false);
								return;
							}
							selModel.deselectAll();
							selModel.select(recs);
							b.setDisabled(true);

							var filename = (recs.length===1 ? recs[0].get('artf_name') + '_objects_'+Ext.util.Format.date(new Date(),'YmdHis') : null);
							if(Ext.isDefined(filename)) filename = filename.replace(/[^A-Za-z0-9]/g,'_');

							self.downloadObjectsTask.delay(10,self.downloadObjects,self,[{
								type: 'folder',
								records: recs,
								filename: filename,
								callback: function(){
									b.setDisabled(false);
								}
							}]);
						}
					}
				},'-',' '


			,'-',{
				itemId: 'reload',
				xtype: 'button',
				iconCls: 'x-tbar-loading',
				listeners: {
					click: function(b){
						var treepanel = b.up('treepanel');
						var store = treepanel.getStore();
						var selModel = treepanel ? treepanel.getSelectionModel() : null;
						var node = selModel ? selModel.getSelection()[0] : null;
						if(node){
							if(node.isRoot()){
								store.load({node:node});
							}else{
								store.load({
									node:node,
									callback: function(records,operation,success){
										if(success){
											Ext.data.StoreManager.lookup('uploadObjectStore').loadPage(1);
										}
									}
								});
							}
						}else{
							store.load();
						}
					}
				}
			},

			,'-',{
				itemId: 'add',
				xtype: 'button',
				tooltip: 'Add folder',
				iconCls: 'tfolder_add',
				listeners: {
					click: function(b){
						var treepanel = b.up('treepanel');
						var selModel = treepanel ? treepanel.getSelectionModel() : null;
						var node = selModel ? selModel.getSelection()[0] : null;
						if(node){
							var title = b.text || 'Add';
							Ext.Msg.show({
								title: title,
								msg: 'Please enter new folder name:',
								iconCls: b.iconCls,
								buttons: Ext.Msg.OKCANCEL,
								prompt: true,
								fn: function(btn, text){
									if(btn != 'ok') return;
									var artf_name = Ext.String.trim(text);
									if(artf_name.length==0) return;
									node.expand(false,function(){
										if(node.hasChildNodes()){
											var c = node.findChild('artf_name', artf_name);
											if(c){
												Ext.Msg.show({
													title: title,
													msg: 'Already exist in the same folder.',
													iconCls: b.iconCls,
													icon: Ext.Msg.ERROR,
													buttons: Ext.Msg.OK
												});
												return ;
											}
										}
										try{
											var uploadFolderTreePanelStore = Ext.data.StoreManager.lookup('uploadFolderTreePanelStore');

											var append_node = node.appendChild({
												text: artf_name,
												leaf: false,
												iconCls: 'tfolder',
												artf_pid: node.get('artf_id'),
												artf_name: artf_name
											}, false, false );
//												console.log(append_node);

//												console.log('getNewRecords()     :'+uploadFolderTreePanelStore.getNewRecords().length);
//												console.log('getModifiedRecords():'+uploadFolderTreePanelStore.getModifiedRecords().length);
//												console.log('getRemovedRecords() :'+uploadFolderTreePanelStore.getRemovedRecords().length);
//												console.log('getUpdatedRecords() :'+uploadFolderTreePanelStore.getUpdatedRecords().length);

											uploadFolderTreePanelStore.sync({
												callback: function(batch,options){
												},
												success: function(batch,options){
													if(Ext.isArray(this.reader.rawData.datas) && this.reader.rawData.datas.length){
														var data = this.reader.rawData.datas[0];
														append_node.beginEdit();
														var field_names = ['artf_id','artf_entry','artf_timestamp'];
														Ext.each(field_names,function(field_name){
															append_node.set(field_name,append_node.fields.map[field_name].convert(data[field_name],append_node));
														});
														append_node.endEdit(true,field_names);
														append_node.commit(true,field_names);
													}
												},
												failure: function(batch,options){
													Ext.Msg.show({
														title: title,
														msg: this.reader.rawData.msg,
														iconCls: b.iconCls,
														icon: Ext.Msg.ERROR,
														buttons: Ext.Msg.OK
													});
													node.removeChild(append_node,true);
//														console.log('getNewRecords()     :'+uploadFolderTreePanelStore.getNewRecords().length);
//														console.log('getModifiedRecords():'+uploadFolderTreePanelStore.getModifiedRecords().length);
//														console.log('getRemovedRecords() :'+uploadFolderTreePanelStore.getRemovedRecords().length);
//														console.log('getUpdatedRecords() :'+uploadFolderTreePanelStore.getUpdatedRecords().length);
												}
											});

										}catch(e){
											console.error(e);
										}
									});
								}
							});

						}
					}
				}
			}
			,'-',{
				itemId: 'rename',
				xtype: 'button',
				tooltip: 'Rename Selected folder',
				iconCls: 'tfolder_rename',
				disabled:true,
				listeners: {
					click: function(b){
						var treepanel = b.up('treepanel');
						var selModel = treepanel ? treepanel.getSelectionModel() : null;
						var node = selModel ? selModel.getSelection()[0] : null;
						if(node){
							var title = b.text || 'Rename';
							var old_artf_name = node.get('artf_name');
							Ext.Msg.show({
								title: title,
								msg: 'Please enter new folder name:',
								iconCls: b.iconCls,
								buttons: Ext.Msg.OKCANCEL,
								prompt: true,
								value: old_artf_name,
								fn: function(btn, text){
									if(btn != 'ok') return;
									var artf_name = Ext.String.trim(text);
									if(artf_name.length==0) return;
									if(artf_name==old_artf_name) return;
									if(node.parentNode.hasChildNodes()){
										var c = node.parentNode.findChild('artf_name', artf_name);
										if(c && c != node){
											Ext.Msg.show({
												title: title,
												msg: 'Already exist in the same folder.',
												iconCls: b.iconCls,
												icon: Ext.Msg.ERROR,
												buttons: Ext.Msg.OK
											});
											return ;
										}
									}
									node.beginEdit();
									node.set('text',artf_name);
									node.set('artf_name',artf_name);
									node.endEdit(false,['text','artf_name']);

									var uploadFolderTreePanelStore = Ext.data.StoreManager.lookup('uploadFolderTreePanelStore');

									var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
									var proxy = uploadFolderTreePanelStore.getProxy();
									proxy.extraParams = proxy.extraParams || {};
									var artf_id = proxy.extraParams.artf_id;

									var record = artf_id ? uploadFolderTreePanelStore.findRecord( 'artf_id', artf_id, 0, false, false, false) : uploadFolderTreePanelStore.getRootNode();
									Ext.getCmp('moveFolderCombo').setValue(record ? record.getId() : undefined);


									uploadFolderTreePanelStore.sync({
										success: function(batch,options){
											if(Ext.isArray(this.reader.rawData.datas) && this.reader.rawData.datas.length){
												var data = this.reader.rawData.datas[0];
												node.beginEdit();
												var field_names = ['artf_timestamp'];
												Ext.each(field_names,function(field_name){
													node.set(field_name,node.fields.map[field_name].convert(data[field_name],node));
												});
												node.endEdit(true,field_names);
												node.commit(true,field_names);
											}
										},
										failure: function(batch,options){
											Ext.Msg.show({
												title: title,
												msg: this.reader.rawData.msg,
												iconCls: b.iconCls,
												icon: Ext.Msg.ERROR,
												buttons: Ext.Msg.OK
											});
											node.reject();
										}
									});
								}
							});
						}
					}
				}
			}
			,'-',{
				itemId: 'delete',
				xtype: 'button',
				tooltip: 'Delete Selected folder',
				iconCls: 'pallet_delete',
				disabled:true,
				listeners: {
					click: function(b){
						var treepanel = b.up('treepanel');
						var selModel = treepanel ? treepanel.getSelectionModel() : null;
						var node = selModel ? selModel.getSelection()[0] : null;
						if(!node) return;

						var title = b.text || 'Delete';
						var iconCls = b.iconCls;
						var msg;
//						if(node.isRoot()){
//							msg = '選択されているフォルダに関連しているオブジェクトを削除してよろしいですか？<input type="checkbox" id="remove_folder_and_object" checked style="display:none;"/>';
//						}else{
							msg = '選択されているフォルダを削除してよろしいですか？<br/><br/><input type="checkbox" id="remove_folder_and_object" /><label for="remove_folder_and_object">関連しているオブジェクトも削除する</label>';
//						}

						b.setDisabled(true);

						Ext.Msg.show({
							title: title,
							msg: msg,
							iconCls: iconCls,
							buttons: Ext.Msg.YESNO,
							defaultFocus: 'no',
							fn: function(btn){
								if(btn != 'yes'){
									b.setDisabled(false);
									b.setIconCls('pallet_delete');
									return;
								}
								b.setIconCls('loading-btn');
								treepanel.setLoading(true);

								var remove_folder_and_object = false;
								if(document.getElementById('remove_folder_and_object').checked){
									remove_folder_and_object = true;
								}
								var artf_id = node.get('artf_id');
								var isRoot = node.isRoot();
								var parentNode = isRoot ? node : node.parentNode;

								var uploadFolderTreePanelStore = Ext.data.StoreManager.lookup('uploadFolderTreePanelStore');
								var proxy = uploadFolderTreePanelStore.getProxy();
								proxy.extraParams = proxy.extraParams || {};
								proxy.extraParams.remove_folder_and_object = remove_folder_and_object;
								proxy.extraParams.remove_artf_id = artf_id;

								try{
									var childNodes = [];
									var findChildNodes = function(c){
										if(!c.isRoot()) childNodes.unshift(c);
										if(c.hasChildNodes()){
											c.eachChild(findChildNodes);
										}
									};
									findChildNodes(node);
									Ext.each(childNodes,function(c){
										c.remove();
									});


									selModel.deselectAll(true);
									selModel.select(parentNode);

									if(Ext.isEmpty(uploadFolderTreePanelStore.getRemovedRecords())){
										if(node.isRoot() && self.beforeloadStore(uploadFolderTreePanelStore)){
											delete proxy.extraParams.current_datas;
											Ext.Ajax.request({
												url: proxy.api.destroy,
												method: proxy.actionMethods.destroy,
												timeout: proxy.timeout,
												params: Ext.Object.merge({},proxy.extraParams,{datas: Ext.encode([{artf_id: node.get('artf_id')}])} ),
												callback: function(options,success,response){
													b.setDisabled(false);
													b.setIconCls('pallet_delete');
													treepanel.setLoading(false);
													treepanel.fireEvent('selectionchange',selModel,selModel.getSelection());
													if(self.syncMappingMngStore) self.syncMappingMngStore();
												}
											});
										}else{
											b.setDisabled(false);
											b.setIconCls('pallet_delete');
											treepanel.setLoading(false);
										}
									}else{
										uploadFolderTreePanelStore.sync({
											callback: function(batch,options){
												b.setDisabled(false);
												b.setIconCls('pallet_delete');
												treepanel.setLoading(false);
											},
											success: function(batch,options){
												if(isRoot) uploadFolderTreePanelStore.load({node:parentNode});
												if(self.syncMappingMngStore) self.syncMappingMngStore();
											},
											failure: function(batch,options){
												try{
													Ext.Msg.show({
														title: title,
														msg: this.reader.rawData.msg,
														iconCls: iconCls,
														icon: Ext.Msg.ERROR,
														buttons: Ext.Msg.OK
													});
													uploadFolderTreePanelStore.load({
														node: parentNode,
														callback: function(records,operation,success){
															if(!success) return;
															try{
																var rootNode = uploadFolderTreePanelStore.getRootNode();
																var node;
																if(artf_id){
																	node = rootNode.findChild( 'artf_id', artf_id, true );
																}else{
																	node = rootNode;
																}
																if(node){
																	selModel.select(node);
																}
															}catch(e){
																console.error(e);
															}
														}
													});
												}catch(e){
													console.error(e);
												}
											}
										});
									}
								}catch(e){
									console.error(e);
								}
							}
						});
					}
				}
			}]
		}],
		listeners: {
			afterrender: function( panel, eOpts ){
				var fmaAllStore = Ext.data.StoreManager.lookup('fmaAllStore');
				panel.setDisabled(fmaAllStore.isLoading());
				fmaAllStore.on({
					beforeload: function(store, operation, eOpts){
						panel.setDisabled(true);
					},
					load: function(store, records, successful, eOpts){
						if(successful) panel.setDisabled(false);
					}
				});
			},
			beforeload: function( store, operation, eOpts ){
				var sel_node = operation.node ? operation.node : this.getSelectionModel().getLastSelected();
				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				if(sel_node){
					p.extraParams.artf_pid = sel_node.get('artf_id');
				}else{
					delete p.extraParams.artf_pid;
				}
			},
			load: function(/* store, node, records, successful, eOpts */){
				var store, records, successful, operation, node, eOpts, i=0;
				if(Ext.getVersion().major>=5){
					store = arguments[i++];
					records = arguments[i++];
					successful = arguments[i++];
					operation = arguments[i++];
					node = arguments[i++];
					eOpts = arguments[i++];
				}else{
					store = arguments[i++];
					node = arguments[i++];
					records = arguments[i++];
					successful = arguments[i++];
					eOpts = arguments[i++];
				}
				if(successful && node.isRoot()){
					var treepanel = this;
					var path = node.getPath('artf_name');
					upload_folder_tree.getSelectionModel().deselectAll();
					upload_folder_tree.selectPath(path,'artf_name',null,function(bSuccess, oLastNode){
						if(bSuccess){
							var proxy = store.getProxy();

							Ext.Ajax.request({
								url: proxy.api.read+'_art_count',
								method: proxy.actionMethods.read,
								timeout: proxy.timeout,
								params: {
									artf_id: node.get('artf_id')
								},
								callback: function(options,success,response){
									var json;
									try{json = Ext.decode(response.responseText)}catch(e){};
									if(success==false || Ext.isEmpty(json) || Ext.isEmpty(json.success) || json.success==false){
										if(Ext.isEmpty(json) || Ext.isEmpty(json.msg)) return;
										Ext.Msg.show({
											title: title,
											msg: json.msg,
											buttons: Ext.Msg.OK,
											icon: Ext.Msg.ERROR
										});
										return;
									}
									store.suspendAutoSync();
									try{
										node.beginEdit();
										node.set('art_count',json.art_count);
										node.endEdit(false,['art_count']);
										node.commit(false,['art_count']);
									}catch(e){
										console.warn(e);
									}
									store.resumeAutoSync();
									var selModel = treepanel.getSelectionModel();
									selModel.fireEvent('selectionchange',selModel,selModel.getSelection());
								}
							});
						}else{
							console.warn('upload_folder_tree.selectPath():['+path+']:['+bSuccess+']');
						}
					});
				}

				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.artf_pid;
			},
			selectionchange: function( selModel, selected, eOpts ){
//				console.log('selectionchange()',selected);
/*
				var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
				var p = uploadObjectStore.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.select_all;
				if(Ext.isEmpty(selected)){
					delete p.extraParams.artf_id;
				}else{
					p.extraParams.artf_id = selected[0].get('artf_id');
				}
				uploadObjectStore.loadPage(1);
*/
			},
			deselect: function( selModel, record, eOpts ){
				var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
				var p = uploadObjectStore.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.select_all;
				delete p.extraParams.artf_id;
			},
			select: function( selModel, record, index, eOpts ){

				var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
				var p = uploadObjectStore.getProxy();
				p.extraParams = p.extraParams || {};
				delete p.extraParams.select_all;
				p.extraParams.artf_id = record.get('artf_id');
				uploadObjectStore.loadPage(1);
				var obj = {};
				if(self.AgLocalStorage.exists(self.DEF_LOCALDB_FOLDER_INFO)) obj = Ext.decode(self.AgLocalStorage.load(self.DEF_LOCALDB_FOLDER_INFO));
				obj['selected'] = record.getPath('artf_name');
				self.AgLocalStorage.save(self.DEF_LOCALDB_FOLDER_INFO,Ext.encode(obj));
			},


			itemappend: function(node,newNode,index,eOpts){
				if(!newNode.isExpanded()){
					var obj = {};
					if(self.AgLocalStorage.exists(self.DEF_LOCALDB_FOLDER_INFO)) obj = Ext.decode(self.AgLocalStorage.load(self.DEF_LOCALDB_FOLDER_INFO));
					obj['expand'] = obj['expand'] || {};
					var artf_id = newNode.get('artf_id');
					if(obj['expand'][artf_id]){// || node.internalId=='root'){
						newNode.expand();
					}
				}
			},
			itemcollapse: function(node,eOpts){
				var tree_panel = this;
				var obj = {};
				if(self.AgLocalStorage.exists(self.DEF_LOCALDB_FOLDER_INFO)) obj = Ext.decode(self.AgLocalStorage.load(self.DEF_LOCALDB_FOLDER_INFO));
				obj['expand'] = obj['expand'] || {};
				var artf_id = node.get('artf_id');
				delete obj['expand'][artf_id];
				self.AgLocalStorage.save(self.DEF_LOCALDB_FOLDER_INFO,Ext.encode(obj));

				Ext.defer(function(){
					node.collapseChildren(true);
				},100);

				var sel_node = tree_panel.getSelectionModel().getLastSelected();
				if(sel_node && sel_node!=node){
					var child_node = node.findChild( 'artf_id', sel_node.get('artf_id'), true );
//					if(child_node) tree_panel.getSelectionModel().deselect([sel_node]);
					if(child_node) tree_panel.getSelectionModel().select([node]);
				}
			},
			itemexpand: function(node,eOpts){
				var obj = {};
				if(self.AgLocalStorage.exists(self.DEF_LOCALDB_FOLDER_INFO)) obj = Ext.decode(self.AgLocalStorage.load(self.DEF_LOCALDB_FOLDER_INFO));
				obj['expand'] = obj['expand'] || {};
				var artf_id = node.get('artf_id');
				obj['expand'][artf_id] = true;
				self.AgLocalStorage.save(self.DEF_LOCALDB_FOLDER_INFO,Ext.encode(obj));
			},
			itemcontextmenu: function(treepanel, record, item, index, e, eOpts){
				e.stopEvent();
				var xy = e.getXY();
				xy[0] += 2;
				xy[1] += 2;
				self.contextMenu.upload_folder.showAt(xy);
			}
		}
	});



	var upload_panel = Ext.create('Ext.panel.Panel',{
		id: 'upload-panel',
		layout: 'border',
		title:'Upload Parts List',
		border:false,
//		autoScroll: true,
		items:[
			upload_folder_tree,
//			upload_group_grid,
			upload_object_grid
		]
	});

	var pick_search_panel = Ext.create('Ext.panel.Panel',{
		disabled: false,
		id: 'pick-search-panel',
		title: AgLang.pick_search,
		iconCls: 'tab_pick',
		layout: 'border',
		items: [{
			hidden: false,
			region: 'north',
			id: 'pick-search-conditions-panel',
			border: false,
//			height: 62,
//			height: 96,
//			height: 70,
			height: 95,
			frame: true,
			xtype: 'form',
			bodyPadding: '0 0 0 0',
			defaults: {
				labelAlign: 'left',
//				labelAlign: 'right',
//				labelWidth: 64,
				labelWidth: 70,
//				labelWidth: 120,
				labelStyle: 'font-weight:bold;'
			},
			items: [{
				xtype: 'radiogroup',
				fieldLabel: 'Parts Type',
				vertical: false,
//				width: 350,
				width: 300,
				items: [{
					boxLabel  : 'FMA対応済み',
					name      : 'parts_map',
					inputValue: true,
					checked   : true
				},{
					boxLabel  : '全て',
					name      : 'parts_map',
					inputValue: false
				}],
				listeners: {
					change: function(radiofield,newValue,oldValue,eOpts){
						var fieldset = this.nextSibling('fieldset');
						if(fieldset) fieldset.setDisabled(oldValue.parts_map);
						Ext.getCmp('pick-search-conditions-button').setDisabled(false);
					}
				}
			},{
				xtype: 'fieldcontainer',
				fieldLabel: 'Pick',
				hideLabel: true,
				itemId: 'pick',
				layout: {
					type: 'hbox',
					align: 'middle',
					pack: 'start',
//					defaultMargins: {top: 0, right: 4, bottom: 0, left: 8}
				},
				defaultType: 'displayfield',
				defaults: {
					labelWidth: 12,
					margin: '0 4 0 8'
				},
				items:[{
					xtype:'label',
					text:'Pick:',
					margin: '0 4 0 0',
					style: 'font-weight:bold;'
				},{
					fieldLabel: AgLang.art_id,
					labelWidth: 30,
					itemId: 'art_id'
				},{
					fieldLabel: 'X',
					itemId: 'x'
				},{
					fieldLabel: 'Y',
					itemId: 'y'
				},{
					fieldLabel: 'Z',
					itemId: 'z'
				},{
					flex: 1,
					xtype: 'fieldcontainer',
					layout: {
						type: 'hbox',
						align: 'middle',
						pack: 'end'
					},
					items: [{
						width: 70,
						xtype: 'button',
						disabled: true,
						id: 'pick-search-conditions-button',
						text: 'Search',
						listeners: {
							click: function(b){
								var formPanel = b.up('form');
								var form = formPanel.getForm();
								if(form.isValid()){
									b.setDisabled(true);

									var pickSearchPanel = Ext.getCmp('pick-search-panel').down('gridpanel');
									pickSearchPanel.setLoading(true);

									var pickSearchStore = Ext.data.StoreManager.lookup('pickSearchStore');

									var p = pickSearchStore.getProxy();
									p.extraParams = p.extraParams || {};
									delete p.extraParams.conditions;
									var values = form.getValues(false,false,false,false);

									//非表示時に現在の表示内容のパラメータを設定する
									p.extraParams.conditions = Ext.encode({
										parts_map: Ext.isEmpty(values.parts_map) ? true : values.parts_map,
									});

									var pick = formPanel.getComponent('pick');
									pick.getComponent('art_id').setValue(p.extraParams.art_id);

									var art_point = Ext.decode(p.extraParams.art_point);
									pick.getComponent('x').setValue(Ext.util.Format.number(art_point.x,self.FORMAT_FULL_FLOAT_NUMBER));
									pick.getComponent('y').setValue(Ext.util.Format.number(art_point.y,self.FORMAT_FULL_FLOAT_NUMBER));
									pick.getComponent('z').setValue(Ext.util.Format.number(art_point.z,self.FORMAT_FULL_FLOAT_NUMBER));

									var voxel_range = formPanel.getComponent('voxel_range');
									voxel_range.getComponent('value').setValue(Ext.util.Format.number(p.extraParams.voxel_range,self.FORMAT_INT_NUMBER));

									pickSearchStore.loadPage(1,{
										callback:function(rs, operation, success){
											var p = pickSearchStore.getProxy();
											var art_id = p.extraParams.art_id;
											if(success){
												var idx = pickSearchStore.findBy(function(record,id){
													if(record.get('art_id')==art_id) return true;
												});
												pickSearchStore.suspendEvents(false);
												pickSearchStore.each(function(record){
													if(record.get('target_record')){
														record.set('target_record', false);
														record.commit();
													}
												});
												if(idx>=0){
													var record = pickSearchStore.getAt(idx);
													record.set('target_record', true);
													record.commit();
												}
												pickSearchStore.resumeEvents();

												var p = pickSearchStore.getProxy();
												Ext.getCmp('pick-search-more-button').setDisabled(p.extraParams.voxel_range<DEF_PICK_SEAECH_MAX_RANGE?false:true);
											}
											pickSearchPanel.setLoading(false);
											pickSearchPanel.getView().refresh();
										}
									});
								}
							}
						}
					}]
				}]
			},{
				xtype: 'fieldcontainer',
				fieldLabel: AgLang.voxel_range,
				hideLabel: true,
				itemId: 'voxel_range',
				layout: {
					type: 'hbox',
					align: 'middle',
					pack: 'start',
//					defaultMargins: {top: 0, right: 4, bottom: 0, left: 8}
				},
				defaultType: 'displayfield',
				defaults: {
					margin: '0 4 0 8'
				},
				items:[{
					xtype:'label',
					html: AgLang.voxel_range+':',
					margin: '0 4 0 0',
					style: 'font-weight:bold;'
				},{
					itemId: 'value',
					value: 10
				},{
					width: 70,
					xtype: 'button',
					disabled: true,
					id: 'pick-search-more-button',
					text: 'More',
					listeners: {
						click: function(b){
							b.setDisabled(true);
							var pickSearchStore = Ext.data.StoreManager.lookup('pickSearchStore');
							var p = pickSearchStore.getProxy();
							p.extraParams = p.extraParams || {};
							p.extraParams.voxel_range += 10;
							var b = Ext.getCmp('pick-search-conditions-button');
							if(b) b.fireEvent('click',b);
						}
					}
				}]
			}],
			listeners: {
				render: function(comp,eOpts){
				}
			}
		},{
			id: 'pick-search-grid',
			region: 'center',
			border: true,
			xtype: 'aggridpanel',
			store: 'pickSearchStore',
			stateful: true,
			stateId: 'pick-search-grid',
			columns: [
				{text: '&#160;',           dataIndex: 'selected',     stateId: 'selected',      width: 30, hidden: false, hideable: false, sortable: true, draggable: false, xtype: 'agselectedcheckcolumn' },
				{
					text: AgLang.current,      dataIndex: 'current_use',       stateId: 'current_use',        width: 46, minWidth: 46, hidden: false, hideable: false, sortable: false, draggable: false, resizable: false,
					renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
						var tdCls = [];
						if(value){
							tdCls.push('gridcolumn_current_use');
						}
						else if(Ext.isEmpty(record.get('cdi_name'))){
							metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(self.TOOLTIP_FMAID_NOT_SUPPORTED) + '"';
						}
						else{
							tdCls.push('gridcolumn_current_none_use');
							if(Ext.isString(record.get('current_use_reason'))) metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(record.get('current_use_reason')) + '"';
						}
						if(Ext.isString(metaData.tdCls) && metaData.tdCls.length){
							metaData.tdCls += ' ' + tdCls.join(' ');
						}else{
							metaData.tdCls = tdCls.join(' ');
						}
						return '';
					}
				},
				{
					text: '&#160;',            dataIndex: 'art_tmb_path',     stateId: 'art_tmb_path',      width: 24, minWidth: 24, hidden: false, hideable: false, sortable: false, draggable: false, resizable: false,
					renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
						if(record.data.seg_color){
//							metaData.style = 'background:'+record.data.seg_color+';';
						}
						metaData.innerCls = 'art_tmb_path';
						return value;
					}
				},
				{text: AgLang.art_id,      dataIndex: 'art_id',       stateId: 'art_id',        width:60,  minWidth: 60, hidden: true, hideable: false, xtype: 'agcolumn'},
				{text: AgLang.art_id,      dataIndex: 'artc_id',      stateId: 'artc_id',       width:60,  minWidth: 60, hidden: false, hideable: true, xtype: 'agcolumn'},

				{text: AgLang.cdi_name,    dataIndex: 'cdi_name',     stateId: 'cdi_name',      width: 80, minWidth: 80, hidden: false, hideable: true, xtype: 'agcolumncdiname'},
				{text: AgLang.cdi_name_e,  dataIndex: 'cdi_name_e',   stateId: 'cdi_name_e',    flex: 2.0, minWidth: 80, hidden: false, hideable: true, xtype: 'agcolumncdinamee'},

				{text: AgLang.category,    dataIndex: 'arta_category',stateId: 'arta_category', flex: 1.0, minWidth: 50, hidden: true,  hideable: true, xtype: 'agcolumn'},
				{text: AgLang.class_name,  dataIndex: 'arta_class',   stateId: 'arta_class',    width: 36, minWidth: 36, hidden: true,  hideable: true, xtype: 'agcolumn'},
				{text: AgLang.comment,     dataIndex: 'arta_comment', stateId: 'arta_comment',  flex: 2.0, minWidth: 80, hidden: true,  hideable: true, xtype: 'agcolumn'},
				{text: AgLang.judge,       dataIndex: 'arta_judge',   stateId: 'arta_judge',    flex: 1.0, minWidth: 50, hidden: true,  hideable: true, xtype: 'agcolumn'},

				{text: AgLang.file_name,   dataIndex: 'art_filename', stateId: 'art_filename',  flex: 2.0, minWidth: 80, hidden: false, hideable: true, xtype: 'agcolumn'},
				{text: AgLang.art_data_size, dataIndex: 'art_data_size', stateId: 'art_data_size', width: 60, hidden: true,  hideable: true, xtype: 'agfilesizecolumn'},

				{text: AgLang.xmax,        dataIndex: 'art_xmax',     stateId: 'art_xmax',      width: 60,  hidden: true,  hideable: true, xtype:'agnumbercolumn', format:self.FORMAT_FLOAT_NUMBER },
				{text: AgLang.xmin,        dataIndex: 'art_xmin',     stateId: 'art_xmin',      width: 60,  hidden: true,  hideable: true, xtype:'agnumbercolumn', format:self.FORMAT_FLOAT_NUMBER },
				{text: AgLang.xcenter,     dataIndex: 'art_xcenter',  stateId: 'art_xcenter',   width: 59,  hidden: true,  hideable: true, xtype:'agnumbercolumn', format:self.FORMAT_FLOAT_NUMBER },
				{text: AgLang.ymax,        dataIndex: 'art_ymax',     stateId: 'art_ymax',      width: 60,  hidden: true,  hideable: true, xtype:'agnumbercolumn', format:self.FORMAT_FLOAT_NUMBER },
				{text: AgLang.ymin,        dataIndex: 'art_ymin',     stateId: 'art_ymin',      width: 60,  hidden: true,  hideable: true, xtype:'agnumbercolumn', format:self.FORMAT_FLOAT_NUMBER },
				{text: AgLang.ycenter,     dataIndex: 'art_ycenter',  stateId: 'art_ycenter',   width: 59,  hidden: true,  hideable: true, xtype:'agnumbercolumn', format:self.FORMAT_FLOAT_NUMBER },
				{text: AgLang.zmax,        dataIndex: 'art_zmax',     stateId: 'art_zmax',      width: 55,  hidden: true,  hideable: true, xtype:'agnumbercolumn', format:self.FORMAT_FLOAT_NUMBER },
				{text: AgLang.zmin,        dataIndex: 'art_zmin',     stateId: 'art_zmin',      width: 55,  hidden: true,  hideable: true, xtype:'agnumbercolumn', format:self.FORMAT_FLOAT_NUMBER },
				{text: AgLang.zcenter,     dataIndex: 'art_zcenter',  stateId: 'art_zcenter',   width: 59,  hidden: true,  hideable: true, xtype:'agnumbercolumn', format:self.FORMAT_FLOAT_NUMBER },
				{text: AgLang.volume,      dataIndex: 'art_volume',   stateId: 'art_volume',    width: 60,  hidden: true,  hideable: true, xtype:'agnumbercolumn', format:self.FORMAT_FLOAT_NUMBER },
				{text: AgLang.timestamp,   dataIndex: 'art_timestamp',stateId: 'art_timestamp', width: 112, hidden: true,  hideable: true, xtype:'datecolumn',     format:self.FORMAT_DATE_TIME },

				{
					text: AgLang.distance_voxel,
					dataIndex: 'distance_voxel',
					itemId: 'distance_voxel',
					stateId: 'distance_voxel',
					width:90,
					minWidth:90,
					hidden: false,
					hideable: false,
					sortable: true,
					align:'right',
					xtype:'agnumbercolumn',
					format:self.FORMAT_FULL_FLOAT_NUMBER
				}
			],
			plugins: [self.getCellEditing(),self.getBufferedRenderer()],
			viewConfig: {
				stripeRows:true,
				enableTextSelection:false,
				loadMask:true,
//				allowCopy: true,
				plugins: {
					ddGroup: 'dd-upload_folder_tree',
					ptype: 'gridviewdragdrop',
					enableDrop: false
				}
			},
			selType: 'rowmodel',
			selModel: {
				mode:'MULTI',
			},
			dockedItems: [{
				xtype: 'toolbar',
				dock: 'top',
				defaultType: 'button',
				items:[{
					iconCls: 'pallet_checked',
					text: 'check all',
					listeners: {
						click: function(b){
							b.setDisabled(true);
							Ext.defer(function(){
								var gridpanel = b.up('gridpanel');
								var store = gridpanel.getStore();
								store.suspendEvents(false);
								var palletPartsStore = Ext.data.StoreManager.lookup('palletPartsStore');
								try{
									var records = [];
									store.each(function(record){
										if(record.get('selected')) return true;
										var r = palletPartsStore.findRecord('art_id',record.get('art_id'),0,false,false,true);
										if(Ext.isEmpty(r)){
											record.set('selected',true);
											record.commit();
											records.push(Ext.Object.merge({},record.getData()));
										}
									});
									if(records.length){
										var view = Ext.getCmp('pallet-grid').getView();
										var sorters = palletPartsStore.sorters.getRange();
										if(sorters.length){
											palletPartsStore.sorters.clear();
											view.headerCt.clearOtherSortStates()
										}
										view.getSelectionModel().select(palletPartsStore.add(records));
										if(sorters.length){
											palletPartsStore.sorters.addAll(sorters);
											palletPartsStore.sort();
										}
									}
								}catch(e){
									console.error(e);
								}
								store.resumeEvents();
								gridpanel.getView().refresh();
								b.setDisabled(false);
							},10);
						}
					}
				},'-',{
					iconCls: 'pallet_unchecked',
					text: 'uncheck all',
					listeners: {
						click: function(b){
							b.setDisabled(true);
							Ext.defer(function(){
								var gridpanel = b.up('gridpanel');
								var store = gridpanel.getStore();
								store.suspendEvents(false);
								var palletPartsStore = Ext.data.StoreManager.lookup('palletPartsStore');
								try{
									var records = [];
									store.each(function(record){
										if(!record.get('selected')) return true;
										record.set('selected',false);
										record.commit();
										var r = palletPartsStore.findRecord('art_id',record.get('art_id'),0,false,false,true);
										if(r) records.push(r);
									});
									if(records.length){
										palletPartsStore.remove(records);
									}
								}catch(e){
									console.error(e);
								}
								store.resumeEvents();
								gridpanel.getView().refresh();
								b.setDisabled(false);
							},10);
						}
					}
				},'-','->','-',{
					itemId: 'download',
					tooltip: 'Download Selected',
					iconCls: 'pallet_download',
					disabled:true,
					listeners: {
						click: function(b){
							b.setDisabled(true);

							var gridpanel = b.up('gridpanel');
							var selModel = gridpanel.getSelectionModel();
							var recs = selModel.getSelection();
							if(Ext.isEmpty(recs)){
								b.setDisabled(false);
								return;
							}
							selModel.deselectAll();
							selModel.select(recs);
							b.setDisabled(true);

							self.downloadObjectsTask.delay(10,self.downloadObjects,self,[{
								type: 'objects',
								records: recs,
								callback: function(){
									b.setDisabled(false);
								}
							}]);
						}
					}
				}]
			},{
				xtype: 'toolbar',
				dock: 'bottom',
				items: ['->','-',{
					xtype: 'tbtext',
					itemId: 'num',
					minWidth: 26,
					style: 'text-align:right;',
					text: '<label>0 Objects</label>'
				}]
			}],
			listeners: {
				selectionchange: function(selModel,selected,eOpts){
					var grid = this;
					var toolbar = selModel.view.up('gridpanel').getDockedItems('toolbar[dock="top"]')[0];
					var disabled = Ext.isEmpty(selected);
					toolbar.getComponent('download').setDisabled(disabled);
				},
				render: function(grid,eOpts){
				},
				afterrender: function(grid,eOpts){
					var store = grid.getStore();
					store.on({
						datachanged: function(store,eOpts){
							grid.getDockedItems('toolbar[dock="bottom"]')[0].getComponent('num').setText('<label>'+store.getCount()+' Objects</label>');
						}
					});
					grid.getDockedItems('toolbar[dock="bottom"]')[0].getComponent('num').setText('<label>'+store.getCount()+' Objects</label>');
				},
				itemcontextmenu: {
					fn: self.showPalletItemContextmenu,
					scope: self
				}
			}
		}]
	});

	var east_tab_panel = Ext.create('Ext.tab.Panel',{
		flex: 1,
		minWidth: 400,
		id: 'east-tab-panel',
//		region: 'center',
		region: 'east',
		split: true,
//		collapsible: false,
//		bodyStyle: 'background:transparent;',
		border: false,
		autoScroll: true,
		items: [
			upload_panel,
			pick_search_panel,
			(self.USE_CONFLICT_LIST && self.USE_CONFLICT_LIST_TYPE == 'tab') ? self.getConflictPanel() : null
		],
		dockedItems: [{
			xtype: 'toolbar',
			dock: 'top',
			items: [{
				hidden: false,
				disabled:true,
				id: 'fma-list-tbbutton',
				text: AgLang.all_fma_list,
				iconCls: 'pallet_table',
				menu: [{
					id: 'all-fma-list-button',
					iconCls: 'pallet_table_list',
					text: AgLang.format_html,
					listeners: {
						click: function(b){
							var w = $(window).width() - 20;
							var h = $(window).height() - 0;
							var p = self.getExtraParams({current_datas:0});
							p.cmd = 'fma-all-list';
							p.title = AgLang.all_fma_list;
							var win = window.open('get-info.cgi?'+ Ext.Object.toQueryString(p),"_blank","width="+w+",height="+h+",dependent=yes,directories=no,menubar=no,resizable=yes,status=no,toolbar=no");
						}
					}
				},{
					hidden: true,
					xtype: 'tbseparator'
				},{
					text: 'Export',
					iconCls: 'pallet_download',
					menu: [{
						text: AgLang.format_excel_xlsx,
						iconCls: 'pallet_xls',
						handler: function(b,e){
							self.export({
								cmd: 'export-fma-all-list',
								format: 'xlsx',
								title: AgLang.all_fma_list + ' [ ' + b.text +' ]',
								iconCls: b.iconCls,
								filename: Ext.util.Format.format('{0}_{1}',AgLang.all_fma_list.replace(Ext.form.field.VTypes.filenameReplaceMask,'_'),Ext.util.Format.date(new Date(),'YmdHis'))
							});
						}
					},{
						text: AgLang.format_excel,
						iconCls: 'pallet_xls',
						handler: function(b,e){
							self.export({
								cmd: 'export-fma-all-list',
								format: 'xls',
								title: AgLang.all_fma_list + ' [ ' + b.text +' ]',
								iconCls: b.iconCls,
								filename: Ext.util.Format.format('{0}_{1}',AgLang.all_fma_list.replace(Ext.form.field.VTypes.filenameReplaceMask,'_'),Ext.util.Format.date(new Date(),'YmdHis'))
							});
						}
					},{
						text: AgLang.format_tsv,
						iconCls: 'pallet_txt',
						handler: function(b,e){
							self.export({
								cmd: 'export-fma-all-list',
								format: 'txt',
								title: AgLang.all_fma_list + ' [ ' + b.text +' ]',
								iconCls: b.iconCls,
								filename: Ext.util.Format.format('{0}_{1}',AgLang.all_fma_list.replace(Ext.form.field.VTypes.filenameReplaceMask,'_'),Ext.util.Format.date(new Date(),'YmdHis'))
							});
						}
					}]
				},{
					disabled:true,
					text: AgLang['import'],
					itemId: 'import',
					iconCls: 'pallet_upload',
					handler: function(b,e){
						var p = self.getExtraParams({current_datas:0});
						delete p.current_datas;
						delete p._ExtVerMajor;
						delete p._ExtVerMinor;
						delete p._ExtVerPatch;
						delete p._ExtVerBuild;
						delete p._ExtVerRelease;
						p.cmd = 'import-fma-all-list';
						self.openImportWindow({
							title: b.text + ' ('+ b.up('button').text +')',
							iconCls: b.iconCls,
							params: p
						});
					}
				}],
				listeners: {
					afterrender: function(b){
					},
					menushow: function(b,menu,eOpts){
						var import_menu = menu.getComponent('import');
						import_menu.setDisabled(false);
					}
				}
			},{
				hidden: false,
				xtype: 'tbseparator'
			},'->','-',{
				hidden: !self.USE_CONFLICT_LIST || self.USE_CONFLICT_LIST_TYPE == 'tab',
				disabled: true,
				id: 'ag-conflict-button',
				iconCls: 'pallet_table',
				text: AgLang.conflict_list,
				handler: function(b, e){
//						console.log(b);
					var win = Ext.getCmp('ag-conflict-window');
					if(win){
						win.show();
					}else{
						Ext.create('Ext.window.Window', {
							id: 'ag-conflict-window',
							title: b.text,
							iconCls: b.iconCls,
							height: 400,
							width: 400,
							layout: 'fit',
							animateTarget: b.el,
							autoDestroy: true,
							autoShow: true,
							closeAction: 'destroy',
							items: self.getConflictPanel({title: b.text,iconCls: b.iconCls}),
							buttons: [{
								text: AgLang.close,
								handler: function(b, e){
									b.up('window').close();
								}
							}]
						});
					}
				},
				listeners: {
					afterrender: function(b){
					}
				}
			},
			{
				hidden: !self.USE_CONFLICT_LIST || self.USE_CONFLICT_LIST_TYPE == 'tab',
				xtype: 'tbseparator'
			},all_upload_parts_list_menu]
		}],
		listeners: {
			afterrender: function(comp){
//				console.log("afterrender():["+comp.id+"]["+comp.getActiveTab().id+"]");
			},
			tabchange: function(comp, newCard, oldCard, eOpts){
//				console.log("tabchange():["+comp.id+"]["+newCard.id+"]["+comp.getActiveTab().id+"]");
				var menu = Ext.getCmp('click-mode-menu');
				var menuitem = menu.getActiveItem();
				var itemid = '';
				if(newCard.id=='pin-panel'){
					itemid = 'click-mode-pin-menuitem';
				}else{
					itemid = 'click-mode-pick-menuitem';
				}
				if(menuitem.id != itemid) menu.setActiveItem(Ext.getCmp(itemid));
			}
		}
	});

	var render_panel = Ext.create('Ext.panel.Panel',{
//		flex: 1,
		width: 200,
		minWidth: 200,
/*
		resizable: {
			minWidth: 200,
			handles: 'e',
			pinned: true,
			listeners: {
				beforeresize: function(resizer){
				},
				resizedrag: function(resizer){
				},
				resize: function(resizer, width, height, e, eOpts){
					console.log('resize', resizer, width, height, e, eOpts);
					delete resizer.target.flex;
					resizer.target.setWidth(width);
				}
			}
		},
*/
		id:'render-panel',
		region: 'center',
//		split: true,
		autoDestroy: false,
		listeners: {
			afterrender: function(panel){
				panel.setLoading(true);
				var body = Ext.get(panel.id+'-innerCt');
				if(Ext.isEmpty(body)) body = panel.body;

				self.AgRender.open({
					dom:body.dom,
					loadMask:false
				});

//				console.log('afterrender', panel.id);
				var viewport = Ext.getCmp('main-viewport');
				viewport.on('resize',function(viewport){
					var panel = Ext.getCmp('window-panel');
					var panel_width = Math.floor(panel.body.getWidth()/2);
					panel.setWidth(panel_width);
				},self,{
					single: true
				});
			}
		},
		dockedItems: [{
			id: 'render-panel-toolbar',
			xtype: 'toolbar',
			dock: 'top',
			layout: {
				overflowHandler: 'Menu'
			},
			items : [{
				xtype:'numberfield',
				id:'rotateH',
				fieldLabel: 'H',
				labelWidth: 10,
				allowBlank:false,
				allowDecimals: false,
				keyNavEnabled: false,
				mouseWheelEnabled: false,
//						readOnly:true,
//						width:30,
				maxValue: 355,
				minValue: 0,
				selectOnFocus: false,
				step: 5,
				width:64,
				value:0,
				validator: function(){
					var value = Math.round(this.value/this.step)*this.step;
					if(value > this.maxValue) value -= (this.maxValue+5);
					if(value < this.minValue) value += (this.maxValue+5);
					if(value != this.value) Ext.defer(function(){ this.setValue(value); },50,this);
					return true;
				},
				listeners: {
					change: {
						fn : function(field, newValue, oldValue, eOpts){
//									console.log("change():["+field.id+"]["+field.value+"]");
							self.AgRender.changeLongitudeDegree(newValue, oldValue);
						},
//								buffer: 250
					},
					afterrender: function(field, eOpts){
						field.spinDownEl.on('mousedown',function(e,t,o){
							if(field.value==field.minValue) Ext.defer(function(){ this.setValue(field.maxValue); },50,field);
						});
						field.spinUpEl.on('mousedown',function(e,t,o){
							if(field.value==field.maxValue) Ext.defer(function(){ this.setValue(field.minValue); },50,field);
						});
					},
					specialkey: function(field, e, eOpts){
						if(e.getKey()==e.DOWN && field.value==field.minValue){
							Ext.defer(function(){ this.setValue(field.maxValue); },50,field);
						}else if(e.getKey()==e.UP && field.value==field.maxValue){
							Ext.defer(function(){ this.setValue(field.minValue); },50,field);
						}
						e.stopPropagation();
					}
				}
			},{
				xtype:'numberfield',
				id:'rotateV',
				fieldLabel: 'V',
				labelWidth: 10,
				allowBlank:false,
				allowDecimals: false,
				keyNavEnabled: false,
				mouseWheelEnabled: false,
//						readOnly:true,
//						width:30,
				maxValue: 355,
				minValue: 0,
				selectOnFocus: false,
				step: 5,
				width:64,
				value:0,
				validator: function(){
					var value = Math.round(this.value/this.step)*this.step;
					if(value > this.maxValue) value -= (this.maxValue+5);
					if(value < this.minValue) value += (this.maxValue+5);
					if(value != this.value) Ext.defer(function(){ this.setValue(value); },50,this);
					return true;
				},
				listeners: {
					change: {
						fn : function(field, newValue, oldValue, eOpts){
							self.AgRender.changeLatitudeDegree(newValue, oldValue);
						},
//								buffer: 250
					},
					afterrender: function(field, eOpts){
						field.spinDownEl.on('mousedown',function(e,t,o){
							if(field.value==field.minValue) Ext.defer(function(){ this.setValue(field.maxValue); },50,field);
						});
						field.spinUpEl.on('mousedown',function(e,t,o){
							if(field.value==field.maxValue) Ext.defer(function(){ this.setValue(field.minValue); },50,field);
						});
					},
					specialkey: function(field, e, eOpts){
						if(e.getKey()==e.DOWN && field.value==field.minValue){
							Ext.defer(function(){ this.setValue(field.maxValue); },50,this);
						}else if(e.getKey()==e.UP && field.value==field.maxValue){
							Ext.defer(function(){ this.setValue(field.minValue); },50,this);
						}
						e.stopPropagation();
					}
				}
			},{
				xtype:'tbspacer',
				width:5,
				hidden: true
			},{
				xtype:'numberfield',
				id:'zoom-value-text',
				fieldLabel: 'Zoom',
				labelWidth: 30,
				allowBlank:false,
				allowDecimals: false,
				keyNavEnabled: false,
				mouseWheelEnabled: false,
//						readOnly:true,
//						width:24,
				width:74,
				maxValue: 44,
				minValue: 1,
				selectOnFocus: false,
				step: 1,
				value:1,
				validator: function(){
					var value = Math.round(this.value);
					if(value > this.maxValue) value = this.maxValue;
					if(value < this.minValue) value = this.minValue;
					if(value != this.value) Ext.defer(function(){ this.setValue(value); },50,this);
					return true;
				},
				listeners: {
					change: {
						fn : function(field, newValue, oldValue, eOpts){
							self.AgRender.changeZoom(newValue, oldValue);
						},
//								buffer: 250
					},
					specialkey: function(field, e, eOpts){
						e.stopPropagation();
					}
				}
			},'-',{
				hidden: true,
				xtype:'numberfield',
				id:'camera-near',
				fieldLabel: 'Near',
				labelWidth: 28,
				allowBlank:false,
				allowDecimals: true,
				keyNavEnabled: false,
				mouseWheelEnabled: false,
				maxValue: 10000,
				minValue: 0,
				selectOnFocus: false,
				step: 5,
				width: 98,
				value: 0.1,
				validator: function(){
					if(self.glbCameraNear===undefined || self.glbCameraFar===undefined) return true;
					var value = this.value!==null?this.value:self.glbCameraNear;
					if(value > self.glbCameraFar) value = self.glbCameraFar;
					if(value < self.glbCameraNear) value = self.glbCameraNear;
					if(value != this.value) Ext.defer(function(){ this.setValue(value); },50,this);
					return true;
				},
				listeners: {
					change: function(field, newValue, oldValue, eOpts){
						self.AgRender.changeCameraNear(newValue, oldValue);
					},
					specialkey: function(field, e, eOpts){
						e.stopPropagation();
					}
				}
			},{
				hidden: true,
				xtype:'numberfield',
				id:'camera-far',
				fieldLabel: 'Far',
				labelWidth: 20,
				allowBlank:false,
				allowDecimals: true,
				keyNavEnabled: false,
				mouseWheelEnabled: false,
				maxValue: 10000,
				minValue: 0,
				selectOnFocus: false,
				step: 5,
				width: 90,
				value: 1800.0,
				validator: function(){
					if(self.glbCameraNear===undefined || self.glbCameraFar===undefined) return true;
					var value = this.value!==null?this.value:self.glbCameraFar;
					if(value > self.glbCameraFar) value = self.glbCameraFar;
					if(value < self.glbCameraNear) value = self.glbCameraNear;
					if(value != this.value) Ext.defer(function(){ this.setValue(value); },50,this);
					return true;
				},
				listeners: {
					change: function(field, newValue, oldValue, eOpts){
						self.AgRender.changeCameraFar(newValue, oldValue);
					},
					show: function(field, e, eOpts){
//								console.log("show():["+field.id+"]["+field.getXTypes()+"]");
					},
					specialkey: function(field, e, eOpts){
						e.stopPropagation();
					}
				}
			},{
				xtype: 'tbseparator',
				hidden: true

			},'->',{
				xtype: 'tbseparator',
				hidden: true
			},{
				hidden: true,
				id: 'click-mode-menu',
				xtype:'cycle',
				iconCls:'plus-btn',
				showText: true,
				tooltip: 'Click mode',
				menu: {
					width: 100,
					items: [{
						id: 'click-mode-pick-menuitem',
						text: 'Pick',
						iconCls: 'cursor-btn',
						checked: true,
						value: 'clickmode.pick'
					},{
						id: 'click-mode-pin-menuitem',
						text: 'Pin',
						iconCls: 'pin-btn',
						hidden: false,
						disabled: false,
						value: 'clickmode.pin'
					}]
				},
				changeHandler: function(cycleBtn, activeItem) {
					if(activeItem.value=='clickmode.pin'){
						var panel = Ext.getCmp('east-tab-panel');
						var tabid = 'pin-panel';
						if(panel.getActiveTab().id!=tabid) panel.setActiveTab(Ext.getCmp(tabid));
					}
					self.AgRender.changeClickMode(activeItem.value);
				}
			},{
				xtype: 'tbseparator',
				hidden: false
			},{
				hidden: true,
				tooltip: 'Image for Print',
				iconCls: 'printer-btn',
				handler: function(menuItem, e, eOpts){
					self.AgRender.printImage();
				}
			},{
				xtype: 'tbseparator',
				hidden: true
			},{
				tooltip: 'Options',
				iconCls: 'gear-btn',
				menu: new Ext.menu.Menu({
					defaultType: 'menuitem',
					items: [{
						text: 'Information',
						menu: {
							defaultType: 'menucheckitem',
							defaults: {
								hideOnClick: true,
								clickHideDelay: 250
							},
							items: [{
								id: 'options-guide',
								text: 'Guide',
								checked: true,
								checkHandler: function(menuItem, checked, eOpts){
									self.AgRender.changeGuide(checked);
								}
							},{
								hidden: false,
								id: 'options-tooltip',
								text: 'ToolTip',
								checked: false,
								checkHandler: function(menuItem, checked, eOpts){
									self.AgRender.changeToolTip(checked);
								}
							},{
								xtype: 'menuseparator',
								hidden: true
							},{
								id: 'options-stats',
								text: 'Stats',
								hidden: true,
								checked: false,
								checkHandler: function(menuItem, checked, eOpts){
									self.AgRender.changeStats(checked);
								}
							}]
						}
					},{
						hidden: true,
						text: 'Window',
						menu: {
							items: [{
								id: 'options-grid',
								text: 'Grid',
								hideOnClick: false,
								hidden: false,
								checked: false,
								checkHandler: function(menuItem, checked, eOpts){
									self.setHashTask.delay(0);
								},
								menu: {
									items: [{
										xtype: 'combobox',
										id: 'options-grid-spacing',
										hideLabel: true,
										displayField: 'display',
										valueField: 'value',
										typeAhead: false,
										editable: false,
										queryMode: 'local',
										triggerAction: 'all',
										emptyText: 'Select a state...',
										selectOnFocus: false,
										width: 135,
										iconCls: 'no-icon',
										value: 5,
										store: Ext.create('Ext.data.ArrayStore', {
											fields: ['value', 'display'],
											data : [
												[1,'1mm'],
												[5,'5mm'],
												[10,'10mm'],
												[50,'50mm'],
												[100,'100mm']
											]
										}),
										listeners: {
											select: function(combobox, records, eOpts){
												self.setHashTask.delay(0);
											}
										}
									},{
										text: 'choose a color',
										iconCls: 'color_pallet',
										menu: {
											xtype: 'agcolormenu',
											id: 'options-grid-color',
											value: '00FF00',
											listeners: {
												select: function(picker, color, eOpts){
													self.setHashTask.delay(0);
												}
											}
										}
									}]
								}
							},{
								id: 'options-background',
								text: 'Background color',
								hideOnClick: false,
								hidden: false,
								xype: 'menuitem',
								menu: {
									items: [{
										text: 'choose a color',
										iconCls: 'color_pallet',
										menu: {
											xtype: 'agcolormenu',
											id: 'options-background-color',
											value: 'FFFFFF',
											listeners: {
												select: function(picker, color, eOpts){
													self.setHashTask.delay(0);
												}
											}
										}
									},{
										text: 'Transparent',
										id: 'options-background-opacity',
										checked: false,
										checkHandler: function(menuItem, checked, eOpts){
											self.setHashTask.delay(0);
										}
/*
										xtype: 'numberfield',
										maxValue: 100,
										minValue: 0,
										allowBlank: false,
										allowDecimals: false,
										value: 100,
										iconCls: 'no-icon',
										listeners: {
											afterrender: function(field, eOpts){
//												console.log("afterrender():["+field.id+"]["+field.getValue()+"]["+field.value+"]");
												if(Ext.isEmpty(field.getValue())){
													var jsonObj = self.getLocaleHashObj();
													jsonObj = jsonObj || {};
													jsonObj.Window = jsonObj.Window || AgURLParser.newWindow();
													field.setValue(jsonObj.Window.BackgroundOpacity);
//													console.log("afterrender():["+field.id+"]["+field.getValue()+"]["+field.value+"]");
												}
											},
											validitychange: function(field, isValid, eOpts){
												if(isValid) self.setHashTask.delay(0);
											}
										}
*/
									}]
								}
							},{
								id: 'options-colorheatmap',
								text: 'Heat map',
								hideOnClick: false,
								hidden: false,
								checked: false,
								checkHandler: function(menuItem, checked, eOpts){
									self.setHashTask.delay(0);
									Ext.each(pallet_grid.getView().getGridColumns(),function(c,i,a){
										if(c.dataIndex!=='scalar') return true;
										c.setVisible(checked);
										return false;
									});
								},
								menu: {
									defaults: {
										labelWidth:26
									},
									items: [{
										id: 'options-colorheatmap-max',
										xtype: 'numberfield',
										iconCls: 'heatmap_max',
										fieldLabel:'Max',
										maxValue: 65535,
										minValue: -65535,
										allowBlank: false,
										allowDecimals: false,
										listeners: {
											afterrender: function(field, eOpts){
//														console.log("afterrender():["+field.id+"]["+field.getValue()+"]["+field.value+"]");
												if(Ext.isEmpty(field.getValue())){
													var jsonObj = self.getLocaleHashObj();
													jsonObj = jsonObj || {};
													jsonObj.Common = jsonObj.Common || AgURLParser.newCommon();
													field.setValue(jsonObj.Common.ScalarMaximum);
//															console.log("afterrender():["+field.id+"]["+field.getValue()+"]["+field.value+"]");
												}
											},
											change: function(field){
												self.setHashTask.delay(250);
											},
											specialkey: function(field, e, eOpts){
												e.stopPropagation();
											}
										}
									},{
										id: 'options-colorheatmap-min',
										xtype: 'numberfield',
										iconCls: 'heatmap_min',
										fieldLabel:'Min',
										maxValue: 65535,
										minValue: -65535,
										allowBlank: false,
										allowDecimals: false,
										listeners: {
											afterrender: function(field, eOpts){
//														console.log("afterrender():["+field.id+"]["+field.getValue()+"]["+field.value+"]");
												if(Ext.isEmpty(field.getValue())){
													var jsonObj = self.getLocaleHashObj();
													jsonObj = jsonObj || {};
													jsonObj.Common = jsonObj.Common || AgURLParser.newCommon();
													field.setValue(jsonObj.Common.ScalarMinimum);
//															console.log("afterrender():["+field.id+"]["+field.getValue()+"]["+field.value+"]");
												}
											},
											change: function(field){
												self.setHashTask.delay(250);
											},
											specialkey: function(field, e, eOpts){
												e.stopPropagation();
											}
										}
									}]
								}
							}]
						}
					},{
						xtype: 'menuseparator',
						hidden: true
					},{
						hidden: true,
						text: 'Rotating Image',
						iconCls: 'image-btn',
						menu: {
							defaultType: 'menucheckitem',
							items : [{
								text: 'Small image [120x120]',
								handler: function(){
									self.AgRender.printRotatingImage(120,120);
								}
							},{
								text: 'Medium image [320x320]',
								handler: function(){
									self.AgRender.printRotatingImage(320,320);
								}
							},{
								text: 'Large image [640x640]',
								handler: function(){
									self.AgRender.printRotatingImage(640,640);
								}
							}]
						}
					},{
						hidden: true,
						text: 'Image for Print',
						iconCls: 'printer-btn',
						handler: function(menuItem, e, eOpts){
							self.AgRender.printImage();
						}
					}]
				})
			}]
		}]
	});

	var arrange_windows = function(force){
		if(Ext.isEmpty(force)) force = false;
//		console.log('arrange_windows()',force);

//		var size = Ext.getCmp('window-panel').getSize();
		var size = Ext.getCmp('window-panel').body.getSize();
		var xy = Ext.getCmp('window-panel').body.getXY();
		var adjWidth = size.width;
		var adjHeight = size.height;

		var left = 0;
		var top = xy[1];
		var width = Math.floor(adjWidth/4);
		var height = adjHeight;

		width = Math.floor(adjWidth/3)*2;
		if(pallet_window.isHidden()){
			height = adjHeight;
		}else{
			height = Math.floor(adjHeight/4)*3;
		}


		if(force || !render_window.stateful){
			if(force && render_window.maximized) render_window.restore();
			render_window.setPosition(left,top);
			render_window.setSize(width,height);
		}else if(render_window.stateful){
			var state = render_window.getState();
			if(Ext.isEmpty(state.width) || Ext.isEmpty(state.height)){
				render_window.setPosition(left,top);
				render_window.setSize(width,height);
			}else if(state.maximized){
				render_window.setSize(adjWidth,adjHeight);
			}
		}

		left+=width;
		width = adjWidth-left;
		height = adjHeight;

		if(force || !upload_window.stateful){
			if(force && upload_window.maximized) upload_window.restore();
			upload_window.setPosition(left,top);
			upload_window.setSize(width,height);
		}else if(upload_window.stateful){
			var state = upload_window.getState();
			if(Ext.isEmpty(state.width) || Ext.isEmpty(state.height)){
				upload_window.setPosition(left,top);
				upload_window.setSize(width,height);
			}else if(state.maximized){
				upload_window.setSize(adjWidth,adjHeight);
			}
		}

		left = 0;
		width = Math.floor(adjWidth/3)*2;
		top = Math.floor(adjHeight/4)*3+xy[1];
		height = adjHeight-top+xy[1];

		if(pallet_window.isVisible()){
			if(force || !pallet_window.stateful){
				if(force && pallet_window.maximized) pallet_window.restore();
				pallet_window.setPosition(left,top);
				pallet_window.setSize(width,height);
			}else if(pallet_window.stateful){
				var state = pallet_window.getState();
				if(Ext.isEmpty(state.width) || Ext.isEmpty(state.height)){
					pallet_window.setPosition(left,top);
					pallet_window.setSize(width,height);
				}else if(state.maximized){
					pallet_window.setSize(adjWidth,adjHeight);
				}
			}
		}

		if(fma_window.isVisible()) fma_window.show();
	};

/*
	var render_window = Ext.create('Ext.window.Window', {
		constrainHeader: true,
		title: 'Render',
		id: 'render-window',
		border: false,
		closable: false,
		maximizable: true,
		stateId: 'render-window',
		stateEvents: ['resize','move'],
		stateful: true,
		layout: 'fit',
		width: 250,
		height: 250,
		minWidth: 250,
		minHeight: 250,
		items: render_panel,
		listeners: {
			afterrender: function(comp){
			},
			render: function(comp){
			},
			beforestaterestore: function(stateful,state,eOpts){
			},
			beforestatesave: function(stateful,state,eOpts){
			},
			staterestore: function(stateful,state,eOpts){
			},
			statesave: function(stateful,state,eOpts){
			}
		}
	});
*/
	var fma_window = Ext.create('Ext.window.Window', {
		id: 'fma-window',
		title: AgLang.fma_window,
		border: false,
		closable: true,
		closeAction: 'hide',
		iconCls: 'pallet_table',
		maximizable: true,
		stateId: 'fma-window',
		stateEvents: ['resize','move','hide','show'],
		stateful: true,
		hidden: true,
		layout: 'fit',
		width: 300,
		height: 300,
		minWidth: 300,
		minHeight: 300,
		items: fma_tab_panel,
		listeners: {
			afterrender: function(comp){
//				console.log('afterrender',comp.id);
				fma_tab_panel.setBorder(0);
				if(comp.stateful){
					comp.on('beforestatesave', function(stateful,state,eOpts){
//						console.log('beforestatesave',comp.id);
//						console.log(state);
						state.size = state.size || {height:comp.minHeight,width:comp.minWidth};
						state.height = state.height || comp.minHeight;
						state.width = state.width   || comp.minWidth;
						state.maximized = state.maximized || comp.maximized;

						state.pos = state.pos || [0,0];
						if(state.pos[0]<0) state.pos[0] = 0;
						if(state.pos[1]<0) state.pos[1] = 0;

						state.hidden = comp.isHidden();
						delete state.hidden;

						if(!state.maximized){
//							console.log(state);
							var size = Ext.getCmp('main-viewport').getSize();
//							console.log(size);

							if(state.pos[0] > size.width -100) state.pos[0] = size.width -100;
							if(state.pos[1] > size.height-100) state.pos[1] = size.height-100;
						}

					});
					comp.on('staterestore', function(stateful,state,eOpts){
						console.log('staterestore',comp.id,state);
					});
				}
			},
			show: function(comp){
				var state = comp.getState();
				state.size = state.size || {height:comp.minHeight,width:comp.minWidth};
				state.height = state.height || comp.minHeight;
				state.width = state.width   || comp.minWidth;
				state.maximized = state.maximized || comp.maximized;

				if(!state.maximized){
					state.pos = state.pos || [0,0];
					var size = Ext.getCmp('main-viewport').getSize();
					if(state.pos[0] > size.width -100) state.pos[0] = size.width -100;
					if(state.pos[1] > size.height-100) state.pos[1] = size.height-100;
					if(state.pos[0]<0) state.pos[0] = 0;
					if(state.pos[1]<0) state.pos[1] = 0;
					comp.setXY(state.pos,false);
				}

			},
			hide: function(comp){
				var menuitem = Ext.getCmp('menuitem-fma-window');
				if(menuitem.getXType()=='menucheckitem' && menuitem.checked) menuitem.setChecked(false);
			}
		}
	});

/*
	var upload_window = Ext.create('Ext.window.Window', {
		constrainHeader: true,
		id: 'upload-window',
		border: false,
		closable: false,
		maximizable: true,
		stateId: 'upload-window',
		stateEvents: ['resize','move'],
		stateful: true,
		layout: 'fit',
		width: 300,
		height: 300,
		minWidth: 300,
		minHeight: 300,
		items: east_tab_panel,
		listeners: {
			afterrender: function(comp){
			},
			beforestatesave: function(stateful,state,eOpts){
			},
			render: function(comp){
			},
			resize: function(comp,adjWidth,adjHeight,rawWidth,rawHeight){
			},
			move: function(comp){
			},
			beforestaterestore: function(comp){
			},
			staterestore: function(comp){
			},
			statesave: function(comp){
			}
		}
	});
*/
/*
	var pallet_window = Ext.create('Ext.window.Window', {
		hidden: self.PALLET_WINDOW_HIDDEN,
		constrainHeader: true,
		id: 'pallet-window',
		title: 'Pallet',
		border: false,
		closable: false,
		maximizable: true,
		stateId: 'pallet-window',
		stateEvents: ['resize','move'],
		stateful: true,
		layout: 'fit',
		width: 250,
		height: 250,
		minWidth: 250,
		minWeight: 250,
		items: pallet_grid,
		listeners: {
			afterrender: function(comp){
				pallet_grid.setBorder(0);
				pallet_grid.getHeader().hide();
			},
			beforestatesave: function(stateful,state,eOpts){
			},
			render: function(comp){
			},
			resize: function(comp,adjWidth,adjHeight,rawWidth,rawHeight){
			}
		}
	});
*/
/*
	var bg_window = Ext.create('Ext.window.Window', {
		constrainHeader: true,
		id: 'bg-window',
		title: 'BG',
		border: false,
		closable: false,
		maximizable: true,
		maximized: false,
//		layout: {
//			type: 'hbox',
//			align: 'stretch'
//		},
		layout: 'border',
		width: 500,
		height: 500,
		minWidth: 250,
		minWeight: 250,
		items: [render_panel,east_tab_panel,pallet_grid],
		listeners: {
			afterrender: function(comp){
				console.log('afterrender', comp.id);

				var b = Ext.getCmp('mapping-mng-btn');
				var panel = Ext.getCmp('window-panel');
				if(b.pressed){
					bg_window.setSize(panel.body.getWidth()/3*2,panel.body.getHeight());
					bg_window.showAt(Math.floor(panel.body.getWidth()/3),0);
				}else{
					bg_window.setSize(panel.body.getWidth(),panel.body.getHeight());
					bg_window.showAt(0,0);
				}




			},
			beforestatesave: function(stateful,state,eOpts){
			},
			render: function(comp){
			},
			resize: function(comp,adjWidth,adjHeight,rawWidth,rawHeight){
//				console.log('resize',comp.id,adjWidth,adjHeight);
			},
			show: function(comp){
//				comp.maximize(false);
			}
		}
	});
*/

	var mapping_mng_win = 	self.openMappingMngWin({
		id: self.MAPPING_MNG_ID,
		iconCls: 'gear-btn',
		title: AgLang.mapping_mng
	});

	var bg_panel = Ext.create('Ext.panel.Panel', {
		id: 'bg-window',
		title: 'BackStageEditor',
		iconCls: 'pallet_edit',
		border: false,
		closable: false,
		maximizable: true,
		maximized: false,
//		layout: {
//			type: 'hbox',
//			align: 'stretch'
//		},

		header: false,
		dockedItems: [{
			xtype: 'toolbar',
			dock: 'top',
			items: [{
				xtype: 'tbtext',
				text : '<b>'+'BackStageEditor'+'</b>'
			},'->','-',{
				xtype: 'button',
				iconCls: 'package-btn',
//				text: AgLang.freeze_mapping,
				tooltip: AgLang.freeze_mapping,
				handler: function(b,e){
					self.openFreezeMappingMngWin({
						id: 'freeze-'+self.MAPPING_MNG_ID,
						iconCls: b.iconCls,
						title: b.text || b.tooltip,
						animateTarget: b.el,
						changeTargets: [mapping_mng_win]
					});
				}
			}]
		}],

		layout: 'border',
		region: 'center',
		flex: 2,
		minWidth: 250,
		minWeight: 250,
		items: [render_panel,east_tab_panel,pallet_grid],
		listeners: {
			afterrender: function(comp){
			},
			beforestatesave: function(stateful,state,eOpts){
			},
			render: function(comp){
			},
			resize: function(comp,adjWidth,adjHeight,rawWidth,rawHeight){
			},
			show: function(comp){
			}
		}
	});

	//layout:window
	var viewport_items = [{
		id: 'window-panel',
		bodyStyle: 'background:#aaa;',
		dockedItems: north_panel_dockedItems,
//		items: [render_window,pallet_window,upload_window],
//		items: bg_window,

		layout: 'border',
		items: [
			mapping_mng_win,
			bg_panel
		],
		listeners: {
			afterrender: function(comp){
//				console.log('afterrender', comp.id);

//				render_window.show();
//				if(!self.PALLET_WINDOW_HIDDEN) pallet_window.show();
//				upload_window.show();

//				bg_window.show();

			},
			render: function(comp){
			},
			resize: function(comp,adjWidth,adjHeight,rawWidth,rawHeight){
//				arrange_windows();
//				console.log('resize',comp.id,adjWidth,adjHeight);
//				bg_window.show();
			},
			show: function(comp){
				console.log('show',comp.id);
			}
		}
	}];


	var viewport = Ext.create('Ext.container.Viewport', {
		id: 'main-viewport',
		layout: 'fit',
		items: viewport_items,
		listeners: {
			afterrender: function(viewport){
			},
			beforedestroy: function(viewport){
			},
			destroy: function(viewport){
			},
			render: function(viewport){
			},
			resize: function(viewport,adjWidth,adjHeight,rawWidth,rawHeight){
			},
			show: function(viewport){
			}
		}
	});
};

window.AgApp.prototype.export = function(config){
	var self = this;
	config = config || {};
	config.title = config.title || 'Export';
	config.iconCls = config.iconCls || 'pallet_download';
	config.msg = config.msg || 'Please enter download file name:';
	config.filename = config.filename || 'export_'+Ext.util.Format.date(new Date(),'YmdHis');
	config.format = config.format || 'txt';

	Ext.FilenamePrompt.show({
		title: config.title,
		msg: config.msg,
		iconCls: config.iconCls,
		buttons: Ext.Msg.OKCANCEL,
		prompt: true,
		value: config.filename,
		animateTarget: config.animateTarget,
		closable: false,
		icon: Ext.MessageBox.QUESTION,
		defaultFocus: 'cancel',
		modal: true,
		width: 400,
		fn: function(btn, filename){
			if(btn != 'ok') return;

			var p = self.getExtraParams({current_datas:0});
			p.cmd = config.cmd;
			p.format = config.format;
//			p.title = config.title;
			p.filename = config.filename;
			window.location.href = 'get-info.cgi?'+ Ext.Object.toQueryString(p);
		}
	});
};

window.AgApp.prototype.downloadObjects = function(config){
	var self = this;
	config = config || {};
	config.title = config.title || 'Download';
	config.iconCls = config.iconCls || 'pallet_download';
	config.msg = config.msg || 'Please enter download file name:';
	config.filename = config.filename || 'objects_'+Ext.util.Format.date(new Date(),'YmdHis');
	config.records = config.records || [];

	var records = [];
	Ext.each(config.records,function(r,i,a){
		if(Ext.isEmpty(r.get('art_id')) && Ext.isEmpty(r.get('artf_id'))) return true;
		records.push({
			art_id: r.get('art_id'),
			artf_id: r.get('artf_id')
		});
	});
	if(Ext.isEmpty(records)){
		if(config.callback) (config.callback)(config.records)
		return;
	}

	Ext.FilenamePrompt.show({
		title: config.title,
		msg: config.msg,
		iconCls: config.iconCls,
		buttons: Ext.Msg.OKCANCEL,
		prompt: true,
		value: config.filename,
		animateTarget: config.animateTarget,
		closable: false,
		icon: Ext.MessageBox.QUESTION,
		defaultFocus: 'cancel',
		modal: true,
		width: 300,
		fn: function(btn, filename){
			if(btn == 'ok'){
				var form_name = 'form_download';
				if(!document.forms[form_name]){
					var form = $('<form>').attr({
						action: 'download.cgi',
						method: 'POST',
						name:   form_name,
						id:     form_name,
						style:  "display:none;"
					}).appendTo($(document.body));
					var input = $('<input type="hidden" name="type">').appendTo(form);
					var input = $('<input type="hidden" name="records">').appendTo(form);
					var input = $('<input type="hidden" name="filename">').appendTo(form);
				}
				document.forms[form_name].type.value = config.type;
				document.forms[form_name].records.value = Ext.encode(records);
				document.forms[form_name].filename.value = filename;
				document.forms[form_name].submit();
			}
			if(config.callback) (config.callback)(config.records)
		}
	});
};

window.AgApp.prototype.initContextmenu = function(){
	var self = this;

	self.contextMenu = self.contextMenu || {};

	self.contextMenu.bp3d = Ext.create('Ext.menu.Menu', {
		items: [{
			iconCls:'pallet_copy',
			text: AgLang.copy,
			itemId: 'pallet_copy'
		},'-',{
			iconCls:'pallet_find',
			text: AgLang.parts_find,
			itemId: 'pallet_find'
//		},'-',{
//			iconCls:'pallet_folder_find',
//			text: AgLang.tree_find,
//			itemId: 'pallet_folder_find'
//		},'-',{
//			iconCls:'color_pallet',
//			text: AgLang.properties,
//			itemId: 'properties'
//		},'-',{
//			iconCls:'thumbnail_background_part',
//			text: AgLang.thumbnail_background_part,
//			itemId: 'thumbnail_background_part'
		}]
	});

	self.bp3dItemContextmenuFunc = {
		click_parts_find: function(item,e,eOpts){
			var panel = this;

			var selModel = panel.getSelectionModel();
			var record = selModel.getSelection()[0];
			if(Ext.isEmpty(record)) return;

			self.getUploadObjInfo({cdi_names:Ext.encode([{cdi_name:record.get('cdi_name')}])},{
				store: Ext.data.StoreManager.lookup('palletPartsStore'),
				success: function(records){
					Ext.getCmp('pallet-grid').getSelectionModel().select(records);
					self.update_other_palletPartsStore();
				}
			});
		},
		show: function(menu,eOpts){
			var panel = this;

			var selModel = panel.getSelectionModel();
			var record = selModel.getSelection()[0];

			var disabled_select = false;
			var cdi_name = undefined;
			if(Ext.isEmpty(record) || record.data.art_num==0){
				disabled_select = true;
			}else{
				cdi_name = record.data.cdi_name;
			}

			var disabled_pallet_folder_find = false;
			var cdi_name = undefined;
			if(Ext.isEmpty(record) || Ext.isEmpty(record.data.cdi_name)){
				disabled_pallet_folder_find = true;
			}else{
				cdi_name = record.data.cdi_name;
			}
			if(panel instanceof Ext.tree.Panel) disabled_pallet_folder_find = true;


			var pallet_find = menu.getComponent('pallet_find');
			if(pallet_find){
				if(disabled_select){
					pallet_find.setText(AgLang.parts_find);
					pallet_find.setDisabled(true);
				}else{
					pallet_find.setText(AgLang.parts_find+':['+cdi_name+']');
					pallet_find.setDisabled(false);
//					pallet_find.on('click',self.bp3dItemContextmenuFunc.click_parts_find,panel,{delay:100});
					pallet_find.on('click',self.bp3dItemContextmenuFunc.click_parts_find,panel);
				}
			}
/*
			var pallet_folder_find = menu.getComponent('pallet_folder_find');
			if(pallet_folder_find){
				if(disabled_pallet_folder_find){
					pallet_folder_find.setText(AgLang.tree_find);
					pallet_folder_find.setDisabled(true);
				}else{
					pallet_folder_find.setText(AgLang.tree_find+':['+cdi_name+']');
					pallet_folder_find.setDisabled(false);
					pallet_folder_find.on('click',self.palletItemContextmenuFunc.click_folder_find,panel);
				}
			}
*/
			var mv_publish = false;

			var reload = menu.getComponent('reload');
			if(reload){
				reload.on('click',self.palletItemContextmenuFunc.click_reload,panel);
			}

			var pallet_copy = menu.getComponent('pallet_copy');
			if(pallet_copy){
//				pallet_copy.on('click',self.bp3dItemContextmenuFunc.click_copy,panel,{delay:100});
				pallet_copy.on('click',self.palletItemContextmenuFunc.click_copy,panel);
			}

//			var properties = menu.getComponent('properties');
//			if(properties){
//				properties.on('click',self.palletItemContextmenuFunc.click_properties,panel);
//			}

//			var thumbnail_background_part = menu.getComponent('thumbnail_background_part');
//			if(thumbnail_background_part){
//				thumbnail_background_part.on('click',self.palletItemContextmenuFunc.click_thumbnail_background_part,panel);
//			}
		},
		hide: function(menu,eOpts){
			var panel = this;

//			self.contextMenu.bp3d.un('show',self.bp3dItemContextmenuFunc.show,panel);
			self.contextMenu.bp3d.un('beforeshow',self.bp3dItemContextmenuFunc.show,panel);
			self.contextMenu.bp3d.un('hide',self.bp3dItemContextmenuFunc.hide,panel);

			var selModel = panel.getSelectionModel();
			var record = selModel.getSelection()[0];
			var disabled_select = false;
			if(Ext.isEmpty(record) || record.data.art_num==0) disabled_select = true;

			var disabled_pallet_folder_find = false;
			var cdi_name = undefined;
			if(Ext.isEmpty(record) || Ext.isEmpty(record.data.cdi_name)) disabled_pallet_folder_find = true;
			if(panel instanceof Ext.tree.Panel) disabled_pallet_folder_find = true;

			var pallet_find = menu.getComponent('pallet_find');
			if(pallet_find){
				if(disabled_select){
					pallet_find.setDisabled(true);
				}else{
					pallet_find.setDisabled(false);
					pallet_find.un('click',self.bp3dItemContextmenuFunc.click_parts_find,panel);
				}
			}
/*
			var pallet_folder_find = menu.getComponent('pallet_folder_find');
			if(pallet_folder_find){
				if(disabled_pallet_folder_find){
					pallet_folder_find.setDisabled(true);
				}else{
					pallet_folder_find.setDisabled(false);
					pallet_folder_find.un('click',self.palletItemContextmenuFunc.click_folder_find,panel);
				}
			}
*/
			var mv_frozen = false;

			var reload = menu.getComponent('reload');
			if(reload){
				if(!reload.isDisabled()) reload.un('click',self.palletItemContextmenuFunc.click_reload,panel);
			}

			var pallet_copy = menu.getComponent('pallet_copy');
			if(pallet_copy){
				pallet_copy.un('click',self.palletItemContextmenuFunc.click_copy,panel);
			}

//			var properties = menu.getComponent('properties');
//			if(properties){
//				properties.un('click',self.palletItemContextmenuFunc.click_properties,panel);
//			}

//			var thumbnail_background_part = menu.getComponent('thumbnail_background_part');
//			if(thumbnail_background_part){
//				thumbnail_background_part.un('click',self.palletItemContextmenuFunc.click_thumbnail_background_part,panel);
//			}
		}
	};

	self.contextMenu.pallet = Ext.create('Ext.menu.Menu', {
		items: [{
			iconCls:'pallet_copy',
			text: AgLang.copy,
			itemId: 'pallet_copy'
		},'-',{
			iconCls:'pallet_find',
			text: AgLang.parts_mirroring_find,
			itemId: 'parts_mirroring_find'
		},{
			iconCls:'pallet_find',
			text: AgLang.parts_org_find,
			itemId: 'parts_org_find'
//		},'-',{
//			iconCls:'pallet_folder_find',
//			text: AgLang.tree_find,
//			itemId: 'pallet_folder_find'
		}]
	});

	self.palletItemContextmenuFunc = {
		click_parts_mirroring_find: function(item,e,eOpts){
			var grid = this;
			var selModel = grid.getSelectionModel();
			var record = selModel.getSelection()[0];
			if(Ext.isEmpty(record) || Ext.isEmpty(record.get('art_id'))) return;

			var art_mirroring_id = record.get('art_id');
			if(art_mirroring_id.match(/^(.+)M$/)){
				art_mirroring_id = RegExp.$1;
			}else{
				art_mirroring_id += 'M';
			}
			Ext.defer(function(){
				var data = {};
				for(var key in record.data){
					if(Ext.isEmpty(record.data[key])) continue;
					if(Ext.isDate(record.data[key])){
						data[key] = record.data[key].getTime()/1000;
					}else{
						data[key] = record.data[key];
					}
				}
				data.art_id=art_mirroring_id;
				var art_ids = [data];

				self.getUploadObjInfo({art_ids : Ext.encode(art_ids)},{
					emptyMsg: {
						title: 'Failure',
						msg: AgLang.art_id+' : [ '+art_mirroring_id+' ] は、存在しません',
						buttons: Ext.Msg.OK,
						icon: Ext.Msg.ERROR
					},
					success: function(records){
						selModel.select(records);
						var idxs = [];
						var store = grid.getStore();
						records.forEach(function(record){
							var idx = store.indexOf(record);
							if(idx>=0) idxs.push(idx);
						});
						var idx = idxs.sort().shift();
						if(Ext.isEmpty(grid.getView().getNode(idx))){
							var plugin = grid.getPlugin('bufferedrenderer');
							if(plugin) plugin.scrollTo(idx,true);
						}
						self.update_other_palletPartsStore();
					}
				});
			},0);
		},

		click_parts_org_find: function(item,e,eOpts){
			var grid = this;
			var selModel = grid.getSelectionModel();
			var record = selModel.getSelection()[0];
			if(Ext.isEmpty(record) || Ext.isEmpty(record.data) || Ext.isEmpty(record.data.arto_id)) return;

			var arto_ids = (record.data.arto_id+"").split(/[^A-Za-z0-9]+/);
			var art_ids = [];
			Ext.each(arto_ids,function(arto_id){
				art_ids.push({art_id:arto_id});
			});
			var params = {art_ids:Ext.encode(art_ids)};
			self.getUploadObjInfo(params,{
				emptyMsg: {
					title: 'Failure',
					msg: '対応するデータは、存在しません',
					buttons: Ext.Msg.OK,
					icon: Ext.Msg.ERROR
				},
				success: function(records){
					selModel.select(records);
					var idxs = [];
					var store = grid.getStore();
					records.forEach(function(record){
						var idx = store.indexOf(record);
						if(idx>=0) idxs.push(idx);
					});
					var idx = idxs.sort().shift();
					if(Ext.isEmpty(grid.getView().getNode(idx))){
						var plugin = grid.getPlugin('bufferedrenderer');
						if(plugin) plugin.scrollTo(idx,true);
					}
					self.update_other_palletPartsStore();
				}
			});
		},
/*
		click_folder_find: function(item,e,eOpts){
			var grid = this;
		},
*/
		click_reload: function(item,e,eOpts){
			//動作が不明
			var panel = this;
			if(panel.getXType()=='treepanel'){
				var selModel = panel.getSelectionModel();
				var record = selModel.getSelection()[0];
				if(Ext.isEmpty(record)) return;
				panel.store.lastOptions.node = record.parentNode;
				record.store.reload();
				return;
				Ext.each(records,function(r){
					var options = {
						params : Ext.apply({},{cdi_name : r.data.cdi_name},r.store.proxy.extraParams)
					};
					r.store.reload(options);
				});
			}else if(panel.store){
				panel.store.reload();
			}

		},
		click_copy: function(item,e,eOpts){
			var panel = this;
			var selModel = panel.getSelectionModel();
			var records = [];
			if(panel.getXType()=='treepanel'){
				records = selModel.getSelection();
			}else{
				panel.getStore().each(function(r,i,a){
					if(selModel.isSelected(r)) records.push(r);
				});
			}
			if(records.length>0){
				AgUtils.copyListCB(panel,records);
			}
		},
/*
		click_properties: function(item,e,eOpts){
			var panel = this;
			var selModel = panel.getSelectionModel();
			var records = [];
			if(panel.getXType()=='treepanel'){
				records = selModel.getSelection();
			}else{
				panel.getStore().each(function(r,i,a){
					if(selModel.isSelected(r)) records.push(r);
				});
			}
			if(records.length>0){
				self.openConceptColorSettingWindow({
					panel: panel,
					title: item.text,
					iconCls: item.iconCls,
					records: records
				});
			}
		},
*/
/*
		click_thumbnail_background_part: function(item,e,eOpts){
			var panel = this;
			var selModel = panel.getSelectionModel();
			var records = [];
			if(panel.getXType()=='treepanel'){
				records = selModel.getSelection();
			}else{
				panel.getStore().each(function(r,i,a){
					if(selModel.isSelected(r)) records.push(r);
				});
			}
			if(records.length>0){
				var extraParams = self.getExtraParams();
				var new_records = [];
				Ext.each(records,function(record,i,a){
					new_records.push(Ext.create(record.modelName,Ext.apply({},extraParams,record.getData())));
				});
				self.openThumbnailBackgroundPartSettingWindow({
					record: new_records[0],
					records: new_records
				});
			}
		},
*/
		show: function(menu,eOpts){
			var grid = this;

			var selModel = grid.getSelectionModel();
			var record = selModel.getSelection()[0];


			var disabled_parts_mirroring_find = false;
			var art_mirroring_id = undefined;
			if(Ext.isEmpty(record) || Ext.isEmpty(record.get('art_id'))){
				disabled_parts_mirroring_find = true;
			}else{
				art_mirroring_id = record.get('art_id');
				if(art_mirroring_id.match(/^(.+)M$/)){
					art_mirroring_id = RegExp.$1;
				}else{
					art_mirroring_id += 'M';
				}
			}

			var parts_mirroring_find = menu.getComponent('parts_mirroring_find');
			if(parts_mirroring_find){
				if(disabled_parts_mirroring_find){
					parts_mirroring_find.setText(AgLang.parts_mirroring_find);
					parts_mirroring_find.setDisabled(true);
				}else{
					parts_mirroring_find.setText(AgLang.parts_mirroring_find+':['+art_mirroring_id+']');
					parts_mirroring_find.setDisabled(false);
					parts_mirroring_find.on('click',self.palletItemContextmenuFunc.click_parts_mirroring_find,grid);
				}
			}


			var disabled_parts_org_find = false;
			var arto_id = undefined;
			if(Ext.isEmpty(record) || Ext.isEmpty(record.data.arto_id)){
				disabled_parts_org_find = true;
			}else{
				arto_id = record.data.arto_id;
			}

			var parts_org_find = menu.getComponent('parts_org_find');
			if(parts_org_find){
				if(disabled_parts_org_find){
					parts_org_find.setText(AgLang.parts_org_find);
					parts_org_find.setDisabled(true);
				}else{
					parts_org_find.setText(AgLang.parts_org_find+':['+arto_id+']');
					parts_org_find.setDisabled(false);
					parts_org_find.on('click',self.palletItemContextmenuFunc.click_parts_org_find,grid);
				}
			}


			var disabled_pallet_folder_find = false;
			var cdi_name = undefined;
			if(Ext.isEmpty(record) || Ext.isEmpty(record.data.cdi_name)){
				disabled_pallet_folder_find = true;
			}else{
				cdi_name = record.data.cdi_name;
			}
			var mv_publish = false;

			var pallet_copy = menu.getComponent('pallet_copy');
			if(pallet_copy){
				pallet_copy.on('click',self.palletItemContextmenuFunc.click_copy,grid);
			}
		},
		hide: function(menu,eOpts){
			var grid = this;
			var selModel = grid.getSelectionModel();
			var record = selModel.getSelection()[0];

			var disabled_parts_org_find = false;
			var arto_id = undefined;
			if(Ext.isEmpty(record) || Ext.isEmpty(record.data.arto_id)){
				disabled_parts_org_find = true;
			}else{
				arto_id = record.data.arto_id;
			}

			var parts_org_find = menu.getComponent('parts_org_find');
			if(parts_org_find){
				parts_org_find.setText(AgLang.parts_org_find);
				parts_org_find.setDisabled(disabled_parts_org_find);
				parts_org_find.un('click',self.palletItemContextmenuFunc.click_parts_org_find,grid);
			}


			var disabled_pallet_folder_find = false;
			var cdi_name = undefined;
			if(Ext.isEmpty(record) || Ext.isEmpty(record.data.cdi_name)){
				disabled_pallet_folder_find = true;
			}else{
				cdi_name = record.data.cdi_name;
			}

			self.contextMenu.pallet.un('beforeshow',self.palletItemContextmenuFunc.show,grid);
			self.contextMenu.pallet.un('hide',self.palletItemContextmenuFunc.hide,grid);
/*
			var pallet_folder_find = menu.getComponent('pallet_folder_find');
			if(pallet_folder_find){
				pallet_folder_find.setDisabled(disabled_pallet_folder_find);
				pallet_folder_find.un('click',self.palletItemContextmenuFunc.click_folder_find,grid);
			}
*/
			var mv_frozen = false;

			var pallet_copy = menu.getComponent('pallet_copy');
			if(pallet_copy){
				pallet_copy.un('click',self.palletItemContextmenuFunc.click_copy,grid);
			}
		}
	};

	self.contextMenu.upload_folder = Ext.create('Ext.menu.Menu', {
		items: [{
			itemId: 'upload'
		},'-',{
			itemId: 'add'
		},'-',{
			itemId: 'rename'
		},'-',{
			itemId: 'delete'
		},'-',{
			text: 'Reload',
			itemId: 'reload'
		}],
		listeners: {
			afterrender: function( menu, eOpts ){
//				console.log('afterrender()');
			},
			beforehide: function( menu, eOpts ){
//				console.log('beforehide()');
			},
			beforerender: function( menu, eOpts ){
//				console.log('beforerender()');
			},
			beforeshow: function( menu, eOpts ){
//				console.log('beforeshow()');
			},
			hide: function( menu, eOpts ){
//				console.log('hide()');
			},
			render: function( menu, eOpts ){
//				console.log('render()');
			},
			show: function( menu, eOpts ){
//				console.log('show()');
				var treepanel = Ext.getCmp('upload-folder-tree');
				var toolbar = treepanel.getDockedItems('toolbar[dock="top"]')[0];
				menu.items.each(function(item){
					var button = toolbar.getComponent(item.itemId);
					if(Ext.isEmpty(button)) return true;
					item.setDisabled(button.disabled);
					var text = button.getText() || button.tooltip;
					if(text) item.setText(text);
					item.setIconCls(button.iconCls);
				});
			},
			click: function( menu, item, e, eOpts ){
//				console.log('click()');
//				console.log(item);
				if(Ext.isEmpty(item) || item.disabled) return;
				var treepanel = Ext.getCmp('upload-folder-tree');
				var toolbar = treepanel.getDockedItems('toolbar[dock="top"]')[0];
				var button = toolbar.getComponent(item.itemId);
				if(Ext.isEmpty(button) || button.disabled) return;
				button.fireEvent('click',button);
			}
		}
	});

};

window.AgApp.prototype.showBp3dItemContextmenu = function(view,record,item,index,e,eOpts){
	var self = this;
	e.stopEvent();

	var panel = view.up('gridpanel');
	if(!panel) panel = view.up('treepanel');
	if(!panel) return;
	var selModel = panel.getSelectionModel();
	selModel.deselect([record],true);
	selModel.select([record],true,true);

	self.contextMenu.bp3d.on('beforeshow',self.bp3dItemContextmenuFunc.show,panel);
	self.contextMenu.bp3d.on('hide',self.bp3dItemContextmenuFunc.hide,panel,{buffer:100});
	var xy = e.getXY();
	xy[0] += 2;
	xy[1] += 2;
	self.contextMenu.bp3d.showAt(xy);
};

window.AgApp.prototype.showPalletItemContextmenu = function(view,record,item,index,e,eOpts){
	var self = this;
	e.stopEvent();

	var grid = view.up('gridpanel');
	var selModel = grid.getSelectionModel();
	selModel.deselect([record],true);
	selModel.select([record],true,true);

	self.contextMenu.pallet.on('beforeshow',self.palletItemContextmenuFunc.show,grid);
	self.contextMenu.pallet.on('hide',self.palletItemContextmenuFunc.hide,grid,{buffer:100});
	var xy = e.getXY();
	xy[0] += 2;
	xy[1] += 2;
	self.contextMenu.pallet.showAt(xy);
};

window.AgApp.prototype.openImportWindow = function(config){
	var self = this;

	config = config || {};
	config.title = config.title || AgLang['import'];
	config.iconCls = config.iconCls || 'pallet_upload';
	config.height = config.height || 184;
	config.width = config.width || 400;
	config.minHeight = config.minHeight || 184;
	config.minWidth = config.minWidth || 400;
	config.closable = Ext.isEmpty(config.closable) ? true : config.closable;
	config.maximizable = Ext.isEmpty(config.maximizable) ? true : config.maximizable;
	config.modal = Ext.isEmpty(config.modal) ? true : config.modal;
	config.resizable = Ext.isEmpty(config.resizable) ? false : config.resizable;
	config.id = config.id || 'import-window';

	var win = Ext.create('Ext.window.Window', {
		title: config.title,
		iconCls: config.iconCls,
		closable: config.closable,
		closeAction: 'destroy',
		modal: config.modal,
		resizable: config.resizable,
		width: config.width,
		minWidth: config.minWidth,
		height: config.height,
		minHeight: config.minHeight,
		layout: 'fit',
		border: false,
		items:[{
			xtype:'form',
			bodyPadding: 5,
			defaults: {
				hideLabel: false,
				labelAlign: 'right',
				labelStyle: 'font-weight:bold;',
				labelWidth: 70
			},
			items: [{
				xtype: 'filefield',
				name: 'file',
				itemId: 'file',
				hideLabel:true,
//									msgTarget: 'side',
//									allowBlank: false,
//									anchor: '100%',
				buttonOnly: true,
				buttonText: 'Select File...',
				listeners: {
					change: function(field,value,eOpts){
						var formPanel = field.up('form');
						var submit_btn = formPanel.getDockedItems('toolbar[dock="bottom"]')[0].getComponent('submit');
						if(field.fileInputEl.dom.files && field.fileInputEl.dom.files.length){
							var file = field.fileInputEl.dom.files[0];
							formPanel.getComponent('file_name').setValue(file.name);
							formPanel.getComponent('file_size').setValue(Ext.util.Format.fileSize(file.size));
							formPanel.getComponent('file_last').setValue(Ext.util.Format.date(file.lastModifiedDate,self.FORMAT_DATE_TIME));

							var error = false;
							var error_msg = '';
							if(file.size>DEF_UPLOAD_FILE_MAX_SIZE){
								error = true;
								formPanel.getComponent('file_error').setValue(Ext.String.format(AgLang.error_file_size,Ext.util.Format.fileSize(DEF_UPLOAD_FILE_MAX_SIZE)));
							}
							if(error){
								formPanel.getComponent('file_error').show();
							}else{
								formPanel.getComponent('file_error').hide();
							}
							submit_btn.setDisabled(error);
						}else{
							formPanel.getComponent('file_name').setValue('');
							formPanel.getComponent('file_size').setValue('');
							formPanel.getComponent('file_last').setValue('');
							formPanel.getComponent('file_error').hide();
							submit_btn.setDisabled(true);
						}
					}
				}
			},{
				xtype: 'displayfield',
				fieldLabel: AgLang.file_name,
				itemId: 'file_name'
			},{
				xtype: 'displayfield',
				fieldLabel: AgLang.file_size,
				itemId: 'file_size'
			},{
				hidden: true,
				xtype: 'displayfield',
				fieldLabel: 'ERROR',
				itemId: 'file_error',
				labelStyle: 'font-weight:bold;color:red;',
				fieldStyle: 'color:red;'
			},{
				xtype: 'displayfield',
				fieldLabel: AgLang.timestamp,
				itemId: 'file_last'
			}],
			buttons: [{
				disabled: true,
				iconCls: config.iconCls,
				text: AgLang['import'],
				itemId: 'submit',
				listeners: {
					click: function(b) {
						var formPanel = b.up('form');
						var form = formPanel.getForm();
						if(form.isValid()){
//							console.log(b);
							Ext.Msg.show({
								title: config.title,
								msg: AgLang.import_confirm,
								buttons: Ext.Msg.OKCANCEL,
								icon: Ext.MessageBox.WARNING,
								iconCls: config.iconCls,
								modal: true,
								animateTarget: b.el,
								fn: function(buttonId){
									if(buttonId != 'ok') return;
									b.setDisabled(true);

									var file_field = form.findField('file');
									if(file_field && file_field.fileInputEl && file_field.fileInputEl.dom.files && file_field.fileInputEl.dom.files.length){
										var file = file_field.fileInputEl.dom.files[0];
										var fd = new FormData();
										fd.append('file',file);
										fd.append('name',file.name);
										fd.append('size',file.size);
										fd.append('last',file.lastModifiedDate.getTime());
										if(Ext.isObject(config.params)){
											Ext.Object.each(config.params,function(key,value){
												fd.append(key,value);
											});
										}
										file_field.setDisabled(true);

										var _upload_progress_msg = 'Upload... ['+file.name+']';
										var _upload_progress = Ext.Msg.show({
											closable : false,
											modal    : true,
											msg      : _upload_progress_msg,
											progress : true,
											title    : 'Import...'
										});

										$.ajax({
											url: 'import.cgi',
											type: 'POST',
											timeout: 300000,
											data: fd,
											processData: false,
											contentType: false,
											dataType: 'json',
											xhr : function(){
												var XHR = $.ajaxSettings.xhr();
												if(XHR.upload){
													XHR.upload.addEventListener('progress',function(e){
														var value = e.loaded/e.total;
														_upload_progress.updateProgress(value,Math.floor(value*100)+'%',_upload_progress_msg);
														if(value>=1){
															_upload_progress.wait(_upload_progress_msg);
														}
													});
												}
												return XHR;
											}
										})
										.done(function( data, textStatus, jqXHR ){
											file_field.setDisabled(false);
											b.setDisabled(false);
											_upload_progress.close();
											if(!data.success){
												Ext.Msg.show({
													title: 'Failure',
													msg: data.msg,
													buttons: Ext.Msg.OK,
													icon: Ext.Msg.ERROR
												});
												return;
											}

											var _progress = Ext.Msg.show({
												closable : false,
												modal    : true,
												msg      : 'Uncompress...',
												progress : true,
												title    : 'Import...',
												autoShow : true
											});
											_progress.center();
											var url = 'import.cgi?'+Ext.Object.toQueryString({sessionID: data.sessionID});
											var cb = function(json,callback){
												if(Ext.isEmpty(json)) return;
												if(Ext.isObject(json) && Ext.isObject(json.progress) && Ext.isNumber(json.progress.value)){
													var value = json.progress.value;
													if(Ext.isString(value)) value = parseFloat(value);
													_progress.updateProgress(value,Math.floor(value*100)+'%',json.progress.msg);
												}
												var close_progress_title = null;
												var close_progress_icon = null;
												var close_progress_msg = null;
												if(json.progress && Ext.isString(json.progress.msg) && json.progress.msg.toLowerCase()=='end'){
													close_progress_title = 'Success';
													close_progress_icon = Ext.Msg.INFO;
													close_progress_msg = json.file ? 'Your data "' + json.file + '" has been uploaded.' : 'Your data uploaded.';
												}else if(json.progress && Ext.isString(json.progress.msg) && json.progress.msg.toLowerCase().indexOf('error')==0){
													close_progress_title = 'Error';
													close_progress_icon = Ext.Msg.ERROR;
													close_progress_msg = Ext.isString(json.msg) && json.msg.length ? json.msg : json.progress.msg;
												}else if(Ext.isBoolean(json.success) && !json.success && Ext.isString(json.msg) && json.msg.length){
													close_progress_title = 'Error';
													close_progress_icon = Ext.Msg.ERROR;
													close_progress_msg = json.msg;
												}
												if(callback) (callback)(close_progress_msg?true:false);
												if(close_progress_msg){
													_progress.close();
													Ext.Msg.show({
														title: close_progress_title,
														msg: close_progress_msg,
														buttons: Ext.Msg.OK,
														icon: close_progress_icon
													});

													if(json.exec_folder_file_ins){
														var uploadFolderTreePanelStore = Ext.data.StoreManager.lookup('uploadFolderTreePanelStore');
														uploadFolderTreePanelStore.load();
													}else{
														var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
														uploadObjectStore.loadPage(1);
													}
													var fmaAllStore = Ext.data.StoreManager.lookup('fmaAllStore');
													var proxy = fmaAllStore.getProxy();
													proxy.extraParams = proxy.extraParams || {};
													delete proxy.extraParams.ci_id;
													fmaAllStore.loadPage(1);
												}
											};

											if(Ext.isEmpty(self._TaskRunner)) self._TaskRunner = new Ext.util.TaskRunner();
											var task = self._TaskRunner.newTask({
												run: function () {
													task.stop();
													Ext.Ajax.abort();
													Ext.Ajax.request({
														url: url,
														method: 'GET',
														callback: function(options,success,response){
															task.stop();
															try{json = Ext.decode(response.responseText)}catch(e){};
															if(json){
																cb(json,function(isEndOrError){if(!isEndOrError) task.start();});
															}
														}
													});
												},
												interval: 1000
											});
											task.start();

											var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
											uploadObjectStore.loadPage(1);
										})
										.fail(function( jqXHR, textStatus, errorThrown ){
											console.log(jqXHR);
											console.log(textStatus);
											console.log(errorThrown);

											file_field.setDisabled(false);
											b.setDisabled(false);
											_upload_progress.close();
											Ext.Msg.show({
												title: textStatus,
												msg: errorThrown,
												buttons: Ext.Msg.OK,
												icon: Ext.Msg.ERROR
											});

										});

									}
									else{
										form.clearListeners();
										form.on({
											actioncomplete : function(form,action,eOpts){
											},
											actionfailed : function(form,action,eOpts){
											},
											beforeaction : function(form,action,eOpts){
											},
											dirtychange : function(form,dirty,eOpts){
											},
											validitychange : function(form,valid,eOpts){
											},
										});
										form.submit({
											url: 'import.cgi',
											params: config.params,
											waitMsg: AgLang['import']+' your data...',
											success: function(fp, o) {
												win.hide();
												self.updateArtInfo(function(){
													var viewDom = Ext.getCmp('upload-object-grid').getView().el.dom;
													var scX = viewDom.scrollLeft;
													var scY = viewDom.scrollTop;
													var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
													uploadObjectStore.on({
														load: {
															fn: function(store,records,successful,eOpts){
																b.setDisabled(false);
																b.up('window').setLoading(false);
																b.up('window').close();
																Ext.getCmp('upload-object-grid').getView().scrollBy(scX,scY,false);
															},
															single: true,
															scope: self
														}
													});
													var selected_art_ids = self.getSelectedArtIds();
													var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
													uploadObjectStore.setLoadUploadObjectAllStoreFlag();
													uploadObjectStore.loadPage(1,{
														params: { selected_art_ids: Ext.encode(selected_art_ids) },
														sorters: uploadObjectStore.getUploadObjectLastSorters()
													});
												});
											},
											failure: function(form, action) {
												win.hide();
												switch (action.failureType) {
													case Ext.form.action.Action.CLIENT_INVALID:
														Ext.Msg.show({
															title: 'Failure',
															msg: 'Form fields may not be submitted with invalid values',
															buttons: Ext.Msg.OK,
															icon: Ext.Msg.ERROR
														});
														break;
													case Ext.form.action.Action.CONNECT_FAILURE:
														Ext.Msg.show({
															title: 'Failure',
															msg: 'Ajax communication failed',
															buttons: Ext.Msg.OK,
															icon: Ext.Msg.ERROR
														});
														break;
													case Ext.form.action.Action.SERVER_INVALID:
														Ext.Msg.show({
															title: 'Failure',
															msg: action.result.msg,
															buttons: Ext.Msg.OK,
															icon: Ext.Msg.ERROR
														});
												}
											}
										});
									}
								}
							});
						}
					}
				}
			}],
			listeners: {
				show: function(comp){
				}
			}
		}],
		listeners: {
			hide: function(comp){
				var formPanel = comp.down('form');
				formPanel.getForm().reset();
				formPanel.getComponent('file_error').hide();
				formPanel.getDockedItems('toolbar[dock="bottom"]')[0].getComponent('submit').setDisabled(true);
			}
		}
	});
	win.show();
};

window.AgApp.prototype.openFMASearch = function(config){
	var self = this;
	config = config || {};
	config.title = config.title || 'FMA Search';
	config.iconCls = config.iconCls || 'pallet_find';
	config.modal = config.modal || true;
	config.height = config.height || 300;
	config.width = config.width || 400;
	var fma_search_window = Ext.create('Ext.window.Window', {
		title: config.title,
		iconCls: config.iconCls,
		modal: config.modal,
		height: config.height,
		width: config.width,
		animateTarget: config.animateTarget,
		autoShow: true,
		layout: 'fit',
		items: [{
			xtype: 'gridpanel',
			border: false,
			columnLines: true,
			store: 'fmaSearchStore',
			columns: [
				{xtype: 'rownumberer'},
				{text: AgLang.cdi_name,   dataIndex: 'cdi_name',   width:80, minWidth:80, hidden:false, hideable:false, draggable: false},
				{text: AgLang.cdi_name_e, dataIndex: 'cdi_name_e', flex:1,   minWidth:80, hidden:false, hideable:false, draggable: false}
			],
			selType: 'rowmodel',
			selModel: {
				mode:'SINGLE',
				listeners: {
					selectionchange: function(selModel,selected,eOpts){
					}
				}
			},
			dockedItems: [{
				dock: 'top',
				xtype: 'toolbar',
				items: {
					width: 100,
					fieldLabel: 'Keyword',
					labelWidth: 50,
					xtype: 'searchfield',
					selectOnFocus: true,
					store: 'fmaSearchStore',
					value: Ext.isString(config.query) ? config.query : (Ext.isFunction(config.query) ? (config.query)() : ''),
					listeners: {
						beforerender: function(searchfield, eOpt){
						},
						afterrender: function(searchfield, eOpt){
							searchfield.inputEl.set({autocomplete:'on'});
						},
						specialkey: function(field, e, eOpts){
							e.stopPropagation();
						}
					}
				},
				listeners: {
					resize: function(toolbar,width,height,oldWidth,oldHeight,eOpts){
						try{
							var searchfield = toolbar.down('searchfield');
							searchfield.setWidth(toolbar.getWidth()-6);
						}catch(e){
							console.error(e);
						}
					}
				}
			},{
				id: 'fma-search-grid-agpagingtoolbar',
				stateId: 'fma-search-grid-agpagingtoolbar',
				xtype: 'agpagingtoolbar',
				store: 'fmaSearchStore',
				dock: 'bottom'
			}],
			listeners: {
				render: function(comp, eOpt){
					comp.getSelectionModel().deselectAll();
					comp.getStore().removeAll();
				},
				selectionchange: function(selModel,selected,eOpts){
					var button = selModel.view.up('window').getDockedItems('toolbar[dock="bottom"]')[0].down('button');
					button.setDisabled(Ext.isEmpty(selected[0]));
				}
			}
		}],
		buttons: [{
			disabled: true,
			text: 'Set This ID',
			listeners: {
				click: function(b,e,eOpts){
					var win = b.up('window');
					if(config.callback) (config.callback)(win.down('gridpanel').getSelectionModel().getSelection()[0]);
					win.close();
				}
			}
		},{
			text: 'Cancel',
			listeners: {
				click: function(b,e,eOpts){
					b.up('window').close();
				}
			}
		}],
		listeners: {
			afterrender: function(comp){
//				console.log('afterrender()');
			},
			show: function(comp){
//				console.log('show()');
				var searchfield = comp.down('gridpanel').getDockedItems('toolbar[dock="top"]')[0].down('searchfield');
				if(searchfield) searchfield.focus(true);
			}
		}
	});

};

window.AgApp.prototype.initEventSource = function(){
	var self = this;
	if(useEventSource && EventSource){
		self.__EventSource = new EventSource('eventsource.cgi',{withCredentials:true});
		self.__EventSource.onopen = function(e) {
			console.log('onopen');
			console.log(this);
			console.log(e);
		};
		self.__EventSource.onerror = function(e) {
			console.log('onerror');
			console.log(this);
			console.error(e);
		};
		self.__EventSource.addEventListener('model_version',function(e) {
			var datasetMngStore = Ext.data.StoreManager.lookup('datasetMngStore');
			if(datasetMngStore){
				datasetMngStore.loadPage(1,{
					callback: function(records, operation, success) {
						if(!success) return;
						var fmaAllStore = Ext.data.StoreManager.lookup('fmaAllStore');
						if(fmaAllStore){
							if(fmaAllStore.isLoading()){
								fmaAllStore.on({
									load: function(store, records, successful, eOpts){
										if(successful) store.loadPage(1);
									},
									single: true
								});
							}else{
								fmaAllStore.loadPage(1);
							}
						}
					}
				});
			}
		});
		$(window).unload(function(e){
			try{
				if(self.__EventSource){
					self.__EventSource.close();
					delete self.__EventSource;
				}
			}catch(e){
				console.error(e);
			}
		});
	}
};

window.AgApp.prototype.init = function(){
	var self = this;

	self.initBind();
	self.initExtJS();
	self.initStore();
	self.initDelayedTask();
	self.initComponent();
	self.initContextmenu();
	self.initFileDrop();
	self.initEventSource();

/*
	Ext.FilenamePrompt.show({
		title: 'TEST',
		msg: 'Please enter new folder name:',
		iconCls: 'tfolder_rename',
		buttons: Ext.Msg.OKCANCEL,
		prompt: true,
		value: 'TEST',
		fn: function(btn, text){
			console.log(btn,text);
		}
	});
*/

	//self.openMappingMngWin();

	return;
	//DEBUG(START)
	var btn = Ext.getCmp('error-twitter-button');
	if(btn.isDisabled()){
		btn.on({
			enable: {
				fn: function(btn){
					btn.fireEvent('click',btn);
				},
				buffer: 250,
				single: true
			}
		});
	}else{
		btn.fireEvent('click',btn);
	}
	//DEBUG(END)
};
